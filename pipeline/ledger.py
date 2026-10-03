#!/usr/bin/env python3
"""Prediction ledger: log, resolve, Brier-score. SQLite at ledger/ledger.db

  add      log a prediction (argparse flags, see --help)
  resolve  <id> <1|0>  score a matured prediction
  void     <id> --reason  close a CONDITIONAL call whose trigger never fired (or whose
           wording proved unscoreable) - excluded from Brier, still needs a lesson
  due      list open predictions whose horizon has passed
  report   calibration report: prob buckets, conviction bands, sectors, sources
  ref      <id> record/refresh the REFERENCE forecast for a row (base rate + class, market price)
  revise   <id> --prob --reason   change a live probability (small, dated steps - kept as history)
  confirm  <id> --reason          looked again, fresh datapoint, probability stands
  stale    open rows nobody has looked at in N days

Two ideas from the 2026-09-20 research review run through this file:
  * a Brier number means nothing alone. Every row carries a REFERENCE recorded when it was logged -
    the market price where a liquid market exists, else a base rate with its named reference class -
    and the scoreboard is the EDGE over that reference, with an interval that respects clusters.
  * a forecast is a path, not a point. `prob` is the CURRENT probability; every change is a row in
    `revisions`, and a resolved row scores the time-weighted mean of its daily Brier (how GJ Open
    and Metaculus score), so looking again and moving in small steps is what gets rewarded.
"""
import argparse
import csv
import math
import pathlib
import random
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import trade_rules  # noqa: E402  - the enforced trading ruleset, T01..T14

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import utc_iso, utc_now

DB = pathlib.Path(__file__).resolve().parent.parent / "ledger" / "ledger.db"

DIRECTIONS = ("up", "down", "vol", "neutral")
# Portfolio-hygiene rule 2 (CLAUDE.md): the lean is TAGGED at logging time, never
# inferred later from keywords (the 8/1 audit's regex mislabelled negation-form calls).
LEANS = ("escalation", "de-escalation", "neutral")
DIVERGE = 0.10        # |P - reference| beyond this needs a written reason (no source gives a number; ours)
LATE_REF_HOURS = 48   # a reference written later than this after logging is hindsight-exposed
STALE_DAYS = 7        # an open row nobody has revised or confirmed for this long is stale
BIG_STEP = 0.15       # Atanasov et al. 2020: small frequent updates beat large infrequent ones
NEW_COLS = (("base_rate", "REAL"), ("base_class", "TEXT DEFAULT ''"), ("market_prob", "REAL"),
            ("market_src", "TEXT DEFAULT ''"), ("ref_ts", "TEXT DEFAULT ''"),
            ("diverge_reason", "TEXT DEFAULT ''"), ("prob0", "REAL"), ("asof", "TEXT DEFAULT ''"))


def _load_bars(path):
    """ticker,date,high,low -> {ticker: [(date, high, low)]}. Data only; nothing is fetched."""
    if not path:
        return {}
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["ticker"].upper(), []).append(
                (row["date"][:10], float(row["high"]), float(row["low"])))
    return out


def _trade_of(r, leg_vol=None):
    """A `trades` row -> trade_rules.Trade."""
    return trade_rules.Trade(
        id=r["id"], pred_id=r["pred_id"], ticker=r["ticker"], direction=r["direction"],
        entry_price=r["entry_price"], entry_ts=r["entry_ts"] or "", target=r["target"],
        invalidation=r["invalidation"], exit_price=r["exit_price"], exit_ts=r["exit_ts"],
        exit_reason=r["exit_reason"], status=r["status"], pct=r["pct"], note=r["note"] or "",
        leg_vol=leg_vol or {})


def _trade_ctx(c, bars_path="", exclude_id=None):
    """Everything T01..T14 needs, read out of the ledger. Pure data in, no fetching."""
    c.row_factory = sqlite3.Row
    preds = {r["id"]: trade_rules.LedgerRow(
                 id=r["id"], direction=r["direction"] or "", status=r["status"],
                 cluster=r["cluster"] or "", prob=r["prob"])
             for r in c.execute("SELECT id,direction,status,cluster,prob FROM predictions")}
    by_cluster = {}
    for r in c.execute("SELECT cluster,COUNT(*) n FROM predictions WHERE status='open' GROUP BY cluster"):
        by_cluster[r["cluster"] or ""] = r["n"]
    open_total = c.execute("SELECT COUNT(*) FROM predictions WHERE status='open'").fetchone()[0]
    rows = c.execute("SELECT * FROM trades WHERE status='open'").fetchall()
    open_trades = tuple(_trade_of(r) for r in rows if r["id"] != exclude_id)
    stored = {r["id"]: _trade_of(r) for r in c.execute("SELECT * FROM trades")}
    return trade_rules.TradeContext(
        predictions=preds, open_by_cluster=by_cluster, open_total=open_total,
        open_trades=open_trades, prices=_load_bars(bars_path), stored=stored,
        asof=utc_iso()[:10])


def _report(findings, where):
    """Print every finding. Errors are refusals; the caller decides what to do about it."""
    errs = trade_rules.errors(findings)
    for f in findings:
        print(f"  {'REFUSED' if f.severity == 'error' else 'warning'} {f}")
    if not findings:
        print(f"  {where}: T01-T14 clean")
    return errs


def _price_gap_note(ctx):
    if not ctx.prices:
        print("  NOT CHECKED: T08 (stale target) and T13 (stale invalidation) need session "
              "bars - pass --bars ticker,date,high,low. They are the two rules that caught "
              "the MU blind spot, so a run without them is not a full check.")


def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY, ts TEXT, event TEXT, prediction TEXT,
        prob REAL, horizon TEXT, falsifier TEXT, sensitivity TEXT,
        conviction REAL, sectors TEXT, tickers TEXT, direction TEXT,
        source TEXT DEFAULT 'manual', cluster TEXT DEFAULT '',
        status TEXT DEFAULT 'open', outcome INTEGER, resolved_ts TEXT, brier REAL)""")
    # migration: add cluster to pre-existing DBs (correlated calls share a slug;
    # blank = an independent bet). Idempotent.
    have = {r[1] for r in c.execute("PRAGMA table_info(predictions)")}
    if "cluster" not in have:
        c.execute("ALTER TABLE predictions ADD COLUMN cluster TEXT DEFAULT ''")
    if "lean" not in have:          # escalation | de-escalation | neutral ('' = untagged legacy row)
        c.execute("ALTER TABLE predictions ADD COLUMN lean TEXT DEFAULT ''")
    if "void_reason" not in have:   # why a row was closed unscored (status='void')
        c.execute("ALTER TABLE predictions ADD COLUMN void_reason TEXT DEFAULT ''")
    # reference forecast (base rate / market price), first-stated probability, date the outcome was known
    for col, typ in NEW_COLS:
        if col not in have:
            c.execute(f"ALTER TABLE predictions ADD COLUMN {col} {typ}")
    # every change to a live probability. kind: initial | revise | confirm
    c.execute("""CREATE TABLE IF NOT EXISTS revisions(
        id INTEGER PRIMARY KEY, pred_id INTEGER, ts TEXT, prob REAL, reason TEXT,
        kind TEXT DEFAULT 'revise')""")
    # backfill: a row with no history gets its stated probability as the initial revision. Idempotent.
    orphans = c.execute("""SELECT p.id,p.ts,p.prob FROM predictions p
                           WHERE NOT EXISTS (SELECT 1 FROM revisions r WHERE r.pred_id=p.id)""").fetchall()
    for pid, ts, prob in orphans:
        c.execute("INSERT INTO revisions(pred_id,ts,prob,reason,kind) VALUES(?,?,?,?,'initial')",
                  (pid, ts, prob, "as logged"))
    if orphans or c.execute("SELECT 1 FROM predictions WHERE prob0 IS NULL LIMIT 1").fetchone():
        c.execute("""UPDATE predictions SET prob0=(SELECT prob FROM revisions r WHERE r.pred_id=predictions.id
                     ORDER BY r.ts, r.id LIMIT 1) WHERE prob0 IS NULL""")
        c.commit()
    # learning loop: every resolution must produce a lesson (diagnosis + patch).
    # REALIZED P&L: only CLOSED round-trips count. A trade needs a real entry AND a
    # real exit (pre-registered target or invalidation). Open positions are tracked
    # but excluded from the profit number - paper gains are not profit.
    c.execute("""CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY, pred_id INTEGER, ticker TEXT, direction TEXT,
        entry_price REAL, entry_ts TEXT, target REAL, invalidation REAL,
        exit_price REAL, exit_ts TEXT, exit_reason TEXT,
        status TEXT DEFAULT 'open', pct REAL, note TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS lessons(
        pred_id INTEGER PRIMARY KEY, ts TEXT,
        verdict TEXT,      -- hit-clean | hit-wrong-reason | partial | miss
        diagnosis TEXT,    -- WHICH premise held/failed and why
        patch TEXT)""")    # patch = doctrine/skill section updated, or 'none - variance'
    return c


def lint(prediction, falsifier, prob):
    """Wording defects that made rows unscoreable or mis-priced in the 2026-09-19 cycle. Warnings
    only - the analyst may overrule, but each of these cost a clean score at least once."""
    import re
    w = []
    text = f" {prediction} "
    multi_asset = len(re.findall(r"\b[A-Z]{2,5} (?:holds?|stays?|closes?) ", prediction)) >= 2
    if re.search(r"\bAND\b", prediction) or multi_asset \
            or re.search(r"[a-z\)] and (at least|a |an |the )", prediction):
        w.append("COMPOUND 'AND': every leg must hit. P(A and B) <= min(P(A),P(B)) - price the weakest "
                 "leg, or split into rows (#63 0.75 on two discretionary acts; #39 oil leg hit, food leg missed; "
                 "#69 three ranges, dead in 2 sessions).")
    if re.search(r"\bOR\b| or an? ", prediction):
        w.append("DISJUNCTION 'OR': the EASIEST leg sets the floor. If one leg is near-certain the row "
                 "measures nothing (#21: 'Iran OR an Iran-linked proxy' - Israel strikes Hezbollah weekly; "
                 "logged 0.58, base rate ~0.95). Price off the easy leg or drop it.")
    if re.search(r"\b(if|IF|CONDITIONAL|absent|unless)\b", text) and not re.search(r"N/?A|void|VOID", falsifier + prediction):
        w.append("CONDITIONAL without a void clause: say in the falsifier what happens if the trigger "
                 "never fires ('resolve N/A if ...') and define the trigger NUMERICALLY (#23, #32 needed "
                 "judgment calls on 'sustains'/'absent a re-closure').")
    if re.search(r"\b(sustain|durabl|normaliz|significant|major|credibl|materially|functionally)", text + falsifier, re.I) \
            and not re.search(r"\d", falsifier):
        w.append("VAGUE THRESHOLD: 'sustained/durable/significant/normalized' with no number in the "
                 "falsifier. Give N sessions, a level, a count, a named data source.")
    if re.search(r"\bstrike", text, re.I) and not re.search(r"\b(on|against|inside|territory|shipping|vessels?|bases?)\b", falsifier, re.I):
        w.append("SCOPE: 'strike' by whom, on what? #59 turned on whether IRGC missile hits on tankers "
                 "counted as 'Iranian strikes' - the falsifier did not say.")
    if re.search(r"\b(ceasefire|truce|pause\b|MOU\b|memorandum|deal\b|talks\b|normaliz|re-?clos|re-?open|"
                 r"stays? (on|open|closed)|return to|resum)", text, re.I):
        w.append("STATE-PREMISE: this row leans on a state (ceasefire/deal/strait/pause). Doctrine 16.16 - "
                 "cite a primary datapoint for that state dated within 24h of logging in --event, else cap "
                 "P at 0.55. (The 7/8 batch was logged on 'ceasefire holds' a day after it broke.)")
    if not re.search(r"20\d\d|\d{1,2}/\d{1,2}|horizon", falsifier):
        w.append("falsifier carries no date - restate the horizon inside it.")
    if re.search(r"\b(close[sd]? (above|below)|RANGE CALL|holds? \d|stays? (below|above)|does NOT close|trades? below|touch)", text, re.I):
        w.append("LEVEL/RANGE call: run `python tools/range_odds.py` for the no-view odds first and put "
                 "the number in --sensitivity. A stated P more than 0.20 off it needs a dated mechanism.")
    return w


def _ts(s):
    """ISO string -> aware UTC datetime (date-only strings mean 00:00Z). None if unparseable."""
    try:
        d = datetime.fromisoformat((s or "").strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def reference(base_rate, market_prob):
    """The row's reference forecast: the market price when one was recorded, else the base rate."""
    if market_prob is not None:
        return market_prob, "market"
    if base_rate is not None:
        return base_rate, "base-rate"
    return None, ""


def ref_lint(prob, base_rate, base_class, market_prob, market_src, diverge_reason):
    """Outside view first (research review 2026-09-20, sections 3-4). Warnings, like lint()."""
    w = []
    for name, v in (("--base-rate", base_rate), ("--market", market_prob)):
        if v is not None and not (0.0 < v < 1.0):
            w.append(f"{name} must be strictly between 0 and 1 (got {v}).")
    if base_rate is None:
        w.append("NO BASE RATE: start from the outside view. Give --base-rate and --base-class (the named "
                 "comparison class and its count, e.g. 'interstate ceasefires after a stalemate, 21/48 resumed, "
                 "Fortna 2003'). Without a reference the row can never earn an edge score.")
    elif len((base_class or "").strip()) < 12:
        w.append("BASE RATE WITHOUT A CLASS: name the comparison class and where the number comes from "
                 "(two classes if they disagree - the spread is the uncertainty).")
    if market_prob is not None and len((market_src or "").strip()) < 8:
        w.append("MARKET PRICE WITHOUT A SOURCE: --market-src needs venue, contract, and spread/volume. A thin "
                 "market's midpoint is not a price (a 0.01/0.99 quote has a midpoint of 0.50).")
    ref, kind = reference(base_rate, market_prob)
    if ref is not None and abs(prob - ref) > DIVERGE + 1e-9 and len((diverge_reason or "").strip()) < 20:
        w.append(f"DIVERGENCE: P {prob:.2f} is {prob - ref:+.2f} off the {kind} reference {ref:.2f}. Say in "
                 "--diverge what you know that the reference does not (a dated datapoint, not a mood), or re-price.")
    return w


def add(args):
    if args.direction and args.direction not in DIRECTIONS:
        sys.exit(f"direction must be one of {DIRECTIONS}")
    if not (0.0 <= args.prob <= 1.0):
        sys.exit("prob must be in [0,1]")
    if args.conviction is not None and not (0.0 <= args.conviction <= 1.0):
        sys.exit("conviction must be in [0,1]")
    base_rate = getattr(args, "base_rate", None)
    market = getattr(args, "market", None)
    refs = ref_lint(args.prob, base_rate, getattr(args, "base_class", ""), market,
                    getattr(args, "market_src", ""), getattr(args, "diverge", ""))
    if getattr(args, "dry_run", False):   # see the lint BEFORE the row exists
        msgs = lint(args.prediction, args.falsifier, args.prob) + refs
        for msg in msgs:
            print("  LINT: " + msg)
        print(f"dry-run: {len(msgs)} lint warning(s); nothing logged")
        return
    c = db()
    c.execute("""INSERT INTO predictions
        (ts,event,prediction,prob,horizon,falsifier,sensitivity,
         conviction,sectors,tickers,direction,source,cluster,lean,
         base_rate,base_class,market_prob,market_src,ref_ts,diverge_reason,prob0)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (args.ts or utc_iso(), args.event, args.prediction, args.prob,
         args.horizon, args.falsifier, args.sensitivity,
         args.conviction, args.sectors, args.tickers, args.direction, args.source, args.cluster,
         args.lean, base_rate, getattr(args, "base_class", "") or "", market,
         getattr(args, "market_src", "") or "",
         (args.ts or utc_iso()) if (base_rate is not None or market is not None) else "",
         getattr(args, "diverge", "") or "", args.prob))
    pid = c.execute("SELECT MAX(id) FROM predictions").fetchone()[0]
    c.execute("INSERT INTO revisions(pred_id,ts,prob,reason,kind) VALUES(?,?,?,?,'initial')",
              (pid, args.ts or utc_iso(), args.prob, "as logged"))
    c.commit()
    print(f"logged #{pid}")
    for msg in lint(args.prediction, args.falsifier, args.prob) + refs:
        print("  LINT: " + msg)
    if not args.lean:
        print("  WARN: no --lean tag (escalation|de-escalation|neutral) - hygiene rule 2 says tag it now")
    if args.prob >= 0.80 or args.prob <= 0.20:
        print("  NOTE: extreme probability (>=0.80 / <=0.20). Track record at this tail is thin and "
              "includes #24 (0.80 on an anchoring prior, MISS). Confirm a reference class supports it.")


def time_weighted(revs, start, end, outcome):
    """Mean daily Brier over [start, end]: each stated probability is weighted by how long it stood.
    revs = [(ts_iso, prob)] oldest first. Revisions at or after `end` are ignored - once the outcome is
    known there is nothing left to forecast. A zero-length window scores the last probability standing."""
    pts = []
    for i, (t, p) in enumerate(revs):
        d = _ts(t) or start
        if i == 0:
            pts.append((start, p))            # the first stated probability stands from the start
        elif d < end:
            pts.append((max(d, start), p))
    if end <= start:
        return (pts[-1][1] - outcome) ** 2
    total = 0.0
    for i, (t0, p) in enumerate(pts):
        t1 = pts[i + 1][0] if i + 1 < len(pts) else end
        total += max(0.0, (min(t1, end) - t0).total_seconds()) * (p - outcome) ** 2
    return total / (end - start).total_seconds()


def score_window(ts, horizon, asof, now):
    """[start, end] a row is scored over. It ends the day the outcome became known (--asof), and never
    runs past the horizon - a row noticed seven weeks late (#33) is not scored over those weeks."""
    start = _ts(ts) or now
    hz = _ts(horizon[:10]) if horizon else None
    end = (hz + timedelta(days=1)) if hz else now
    if asof and _ts(asof[:10]):
        end = min(end, _ts(asof[:10]) + timedelta(days=1))
    return start, min(end, now) if end > start else end


def resolve(pid, outcome, asof=""):
    c = db()
    p = c.execute("SELECT prob,ts,horizon FROM predictions WHERE id=?", (pid,)).fetchone()
    if not p:
        sys.exit("no such id")
    if asof and not _ts(asof[:10]):
        sys.exit("--asof must be YYYY-MM-DD (the day the outcome became known)")
    o = 1.0 if int(outcome) else 0.0
    revs = c.execute("SELECT ts,prob FROM revisions WHERE pred_id=? ORDER BY ts,id", (pid,)).fetchall()
    start, end = score_window(p[1], p[2], asof, utc_now())
    brier = time_weighted(revs, start, end, o) if revs else (p[0] - o) ** 2
    c.execute("""UPDATE predictions SET status='resolved',outcome=?,resolved_ts=?,brier=?,asof=?
                 WHERE id=?""", (int(outcome), utc_iso(), brier, asof or "", pid))
    c.commit()
    first, last = (revs[0][1], revs[-1][1]) if revs else (p[0], p[0])
    extra = "" if len(revs) <= 1 else (f"  (time-weighted over {len(revs)} stated probabilities; "
                                       f"first {first:.2f} -> {(first - o) ** 2:.4f}, last {last:.2f} -> {(last - o) ** 2:.4f})")
    print(f"#{pid} resolved outcome={outcome} brier={brier:.4f}{extra}")


def revise(pid, prob, reason, kind="revise"):
    """Move a live probability. History is kept; the row is scored on the whole path."""
    c = db()
    row = c.execute("SELECT status,prob,horizon FROM predictions WHERE id=?", (pid,)).fetchone()
    if not row:
        sys.exit("no such id")
    if row[0] != "open":
        sys.exit(f"#{pid} is {row[0]} - only open rows can be revised")
    if len((reason or "").strip()) < 12:
        sys.exit("--reason: name the dated datapoint that moved you (or that you checked, for confirm)")
    new = row[1] if kind == "confirm" else prob
    if not (0.0 < new < 1.0):
        sys.exit("prob must be strictly between 0 and 1")
    if kind == "revise" and abs(new - row[1]) < 1e-9:
        kind = "confirm"
    c.execute("INSERT INTO revisions(pred_id,ts,prob,reason,kind) VALUES(?,?,?,?,?)",
              (pid, utc_iso(), new, reason.strip(), kind))
    c.execute("UPDATE predictions SET prob=? WHERE id=?", (new, pid))
    c.commit()
    if kind == "confirm":
        print(f"#{pid} confirmed at {new:.2f}: {reason.strip()}")
        return
    print(f"#{pid} revised {row[1]:.2f} -> {new:.2f}: {reason.strip()}")
    if abs(new - row[1]) > BIG_STEP + 1e-9:
        print(f"  NOTE: a {new - row[1]:+.2f} step. Large, rare updates were the least accurate pattern in the "
              "Good Judgment data; if the news is that big, check whether the row's premise is dead (void/resolve) "
              "rather than merely repriced.")
    ref, kind_ref = reference(*c.execute("SELECT base_rate,market_prob FROM predictions WHERE id=?", (pid,)).fetchone())
    if ref is not None and abs(new - ref) > DIVERGE + 1e-9:
        print(f"  NOTE: now {new - ref:+.2f} off the {kind_ref} reference {ref:.2f} recorded at logging - if the "
              "market has moved too, that is not edge; `ref` records a fresh price without touching the original.")
    if row[2] and row[2][:10] <= utc_now().date().isoformat():
        print("  WARN: at or past horizon - resolve it instead; late revisions are not scored.")


def stale(days=STALE_DAYS, quiet=False):
    """Open rows whose last revise/confirm is older than `days`. Returns the list."""
    c = db()
    now = utc_now()
    out = []
    for pid, prob, hz, cl, pred, last in c.execute("""
            SELECT p.id,p.prob,p.horizon,p.cluster,substr(p.prediction,1,80),
                   (SELECT MAX(ts) FROM revisions r WHERE r.pred_id=p.id)
            FROM predictions p WHERE p.status='open' ORDER BY p.horizon"""):
        age = (now - (_ts(last) or now)).days
        if age >= days:
            out.append((pid, prob, hz, cl or "(standalone)", pred, age))
    if not quiet:
        print(f"STALE ({len(out)}): open rows not revised or confirmed in {days}+ days - look again, then "
              "`revise <id> --prob P --reason ...` or `confirm <id> --reason ...`")
        for pid, prob, hz, cl, pred, age in out:
            print(f"  #{pid} P={prob:.2f} horizon={hz} {cl} last look {age}d ago :: {pred}")
        if not out:
            print("  none")
    return out


def set_ref(args):
    """Record the reference for a row that lacks one, or refresh a market price. The ORIGINAL reference is
    what the edge score uses, so an existing one is never overwritten - a later price goes in the note."""
    c = db()
    row = c.execute("SELECT ts,prob0,base_rate,base_class,market_prob,market_src,ref_ts,diverge_reason,status "
                    "FROM predictions WHERE id=?", (args.id,)).fetchone()
    if not row:
        sys.exit("no such id")
    ts, prob0, br, bc, mp, ms, ref_ts, dv, status = row
    if status != "open":
        sys.exit(f"#{args.id} is {status}: a reference written after the outcome is known is hindsight, not a baseline")
    if args.base_rate is not None and br is None:
        br, bc = args.base_rate, args.base_class or ""
    elif args.base_rate is not None:
        print(f"  kept the original base rate {br:.2f} ({bc}); the edge score uses the first one recorded")
    if args.market is not None and mp is None:
        mp, ms = args.market, args.market_src or ""
    elif args.market is not None:
        ms = f"{ms} | later: {args.market:.2f} {utc_iso()[:10]} {args.market_src or ''}".strip()
        print(f"  kept the original market price {mp:.2f}; appended the new quote to the source note")
    for msg in ref_lint(prob0, br, bc, mp, ms, args.diverge or dv):
        print("  LINT: " + msg)
    c.execute("""UPDATE predictions SET base_rate=?,base_class=?,market_prob=?,market_src=?,
                 ref_ts=CASE WHEN ref_ts='' THEN ? ELSE ref_ts END, diverge_reason=? WHERE id=?""",
              (br, bc, mp, ms, utc_iso(), args.diverge or dv, args.id))
    c.commit()
    late = (_ts(utc_iso()) - (_ts(ts) or _ts(utc_iso()))).total_seconds() / 3600 > LATE_REF_HOURS and not ref_ts
    ref, kind = reference(br, mp)
    print(f"#{args.id} reference = {ref if ref is None else round(ref, 3)} ({kind or 'none'})"
          + ("  [LATE: written >48h after logging - reported separately, hindsight-exposed]" if late else ""))


def void(pid, reason):
    """Close a row WITHOUT scoring it: a conditional whose trigger never fired, or a call whose
    own carve-out was tripped. Not a way to dodge a miss - the reason is stored and printed in
    the report, and the sweep still demands a lesson for it."""
    c = db()
    p = c.execute("SELECT status FROM predictions WHERE id=?", (pid,)).fetchone()
    if not p:
        sys.exit("no such id")
    if p[0] != "open":
        sys.exit(f"#{pid} is already {p[0]}")
    c.execute("""UPDATE predictions SET status='void',outcome=NULL,brier=NULL,resolved_ts=?,
                 void_reason=? WHERE id=?""", (utc_iso(), reason, pid))
    c.commit()
    print(f"#{pid} VOID (unscored): {reason}")


LESSON_VERDICTS = ("hit-clean", "hit-wrong-reason", "partial", "miss")


def lesson(args):
    c = db()
    row = c.execute("SELECT status FROM predictions WHERE id=?", (args.id,)).fetchone()
    if not row:
        sys.exit("no such id")
    if row[0] not in ("resolved", "void"):
        sys.exit(f"#{args.id} is not resolved yet - score it first, then extract the lesson")
    if args.verdict not in LESSON_VERDICTS:
        sys.exit(f"verdict must be one of {LESSON_VERDICTS}")
    c.execute("INSERT OR REPLACE INTO lessons(pred_id,ts,verdict,diagnosis,patch) VALUES(?,?,?,?,?)",
              (args.id, utc_iso(), args.verdict, args.diagnosis, args.patch))
    c.commit()
    print(f"lesson recorded for #{args.id} [{args.verdict}] patch: {args.patch}")


def sweep():
    """The cycle gate: overdue-unscored + resolved-unlessoned. Exit 1 if either exists."""
    c = db()
    today = utc_now().date()
    bad = False
    overdue = c.execute("""SELECT id,horizon,prob,substr(prediction,1,70) FROM predictions
                           WHERE status='open' AND horizon<? ORDER BY horizon""",
                        (today.isoformat(),)).fetchall()
    if overdue:
        bad = True
        print(f"OVERDUE UNSCORED ({len(overdue)}) - resolve, or extend horizon with justification:")
        for i, hz, prob, pred in overdue:
            try:
                days = (today - date.fromisoformat(hz[:10])).days
            except ValueError:
                days = "?"
            print(f"  #{i} horizon={hz} ({days}d overdue) P={prob:.0%} :: {pred}")
    unlessoned = c.execute("""SELECT p.id,p.outcome,p.brier,substr(p.prediction,1,70)
                              FROM predictions p LEFT JOIN lessons l ON l.pred_id=p.id
                              WHERE p.status IN ('resolved','void') AND l.pred_id IS NULL
                              ORDER BY p.id""").fetchall()
    if unlessoned:
        bad = True
        print(f"RESOLVED WITHOUT LESSON ({len(unlessoned)}) - diagnose + patch (or 'none - variance'):")
        for i, out, br, pred in unlessoned:
            tag = "VOID" if out is None else ("HIT" if out else "MISS")
            print(f"  #{i} outcome={tag} brier={br if br is None else round(br, 3)} :: {pred}")
    st = stale(quiet=True)
    if st:
        print(f"STALE ({len(st)}) - open rows nobody has looked at in {STALE_DAYS}+ days (warning, does not fail "
              f"the sweep): " + ", ".join(f"#{r[0]}" for r in st[:30]) + "  -> `ledger.py stale`")
    n_lessons = c.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    by_v = dict(c.execute("SELECT verdict,COUNT(*) FROM lessons GROUP BY verdict"))
    print(f"\nlessons on file: {n_lessons} {by_v if by_v else ''}")
    if not bad:
        print("sweep clean - every matured call scored, every resolution diagnosed")
    sys.exit(1 if bad else 0)


def due():
    c = db()
    today = utc_now().date().isoformat()
    rows = c.execute("""SELECT id,horizon,prediction,prob,conviction,tickers
                        FROM predictions WHERE status='open' AND horizon<=?
                        ORDER BY horizon""", (today,)).fetchall()
    for r in rows:
        conv = f"C={r[4]:.2f}" if r[4] is not None else "C=-"
        tick = r[5] or "-"
        print(f"#{r[0]} due {r[1]} P={r[3]:.0%} {conv} [{tick}] :: {r[2]}")
    if not rows:
        print("nothing due")


def cluster_interval(rows, B=4000, seed=20260920):
    """95% interval for the mean of `value`, resampling CLUSTERS not rows. rows = [(cluster, value)];
    a blank cluster is its own cluster. Rows that fail together are one draw, which is why this is wider
    than the naive interval - and why the naive one overstates what the book knows."""
    groups = {}
    for i, (cl, v) in enumerate(rows):
        groups.setdefault(cl or f"_solo{i}", []).append(v)
    keys = list(groups)
    if len(keys) < 3:
        return None
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        vals = []
        for k in rng.choices(keys, k=len(keys)):
            vals += groups[k]
        means.append(sum(vals) / len(vals))
    means.sort()
    return means[int(0.025 * B)], means[int(0.975 * B)], len(keys)


def report():
    c = db()
    n, avg = c.execute(
        "SELECT COUNT(*),AVG(brier) FROM predictions WHERE status='resolved'").fetchone()
    o = c.execute("SELECT COUNT(*) FROM predictions WHERE status='open'").fetchone()[0]
    print(f"resolved={n} open={o} mean Brier={avg:.4f}" if n else f"resolved=0 open={o}")
    voids = c.execute("SELECT id,void_reason FROM predictions WHERE status='void' ORDER BY id").fetchall()
    if voids:
        print(f"void (unscored) = {len(voids)}: " + "; ".join(f"#{i} {(r or '')[:60]}" for i, r in voids))

    # ── skill vs naive baselines ─────────────────────────────────────────
    # A Brier number means nothing alone. Two references: the coin (always 0.50 -> 0.25) and
    # the engine's own hit base rate (always say obar -> obar*(1-obar), i.e. Murphy's UNC).
    # Skill score = 1 - Brier/reference; <=0 means the probabilities add nothing over the baseline.
    if n:
        hits = c.execute("SELECT SUM(outcome) FROM predictions WHERE status='resolved'").fetchone()[0] or 0
        obar = hits / n
        unc = obar * (1 - obar)
        print(f"\n-- skill vs baselines --")
        print(f"  hit rate {hits}/{n} = {obar:.0%}")
        print(f"  vs coin (0.2500):        skill = {1 - avg / 0.25:+.3f}")
        if unc > 0:
            print(f"  vs own hit rate, HINDSIGHT ({unc:.4f}):   skill = {1 - avg / unc:+.3f}   "
                  f"(<=0: stated probabilities add nothing beyond 'we are usually right')")
        scored = c.execute("""SELECT cluster,brier,prob0,outcome FROM predictions
                              WHERE status='resolved' AND brier IS NOT NULL""").fetchall()
        ci = cluster_interval([(cl, b) for cl, b, _, _ in scored])
        if ci:
            lo, hi, k = ci
            verdict = ("cannot yet be told from a coin" if hi >= 0.25 else "better than a coin")
            print(f"  95% interval, resampling {k} clusters: {lo:.3f} .. {hi:.3f}  -> {verdict}")
        eps = 1e-6
        ls = [-(math.log(max(p, eps)) if oc else math.log(max(1 - p, eps))) for _, _, p, oc in scored if p is not None]
        if ls:
            print(f"  log score (first stated P) = {sum(ls) / len(ls):.4f}   (coin = {math.log(2):.4f}; "
                  "punishes confident misses harder than Brier)")

        # -- the scoreboard that matters: EDGE over the reference recorded at logging --------------
        # edge = (reference - outcome)^2 - (first stated P - outcome)^2 ; > 0 means the engine added
        # information the reference did not have. First stated P, because that is what the reference
        # was recorded against.
        print("\n-- edge over the reference (market price, else base rate) --")
        refd = []
        for pid, cl, ts, p0, oc, br, mp, rts in c.execute("""
                SELECT id,cluster,ts,prob0,outcome,base_rate,market_prob,ref_ts FROM predictions
                WHERE status='resolved' AND outcome IS NOT NULL"""):
            ref, kind = reference(br, mp)
            if ref is None or p0 is None:
                continue
            gap_h = ((_ts(rts) or _ts(ts)) - _ts(ts)).total_seconds() / 3600 if _ts(ts) else 0
            refd.append((cl, (ref - oc) ** 2 - (p0 - oc) ** 2, kind, gap_h > LATE_REF_HOURS, abs(p0 - ref) > DIVERGE))
        n_open_ref = c.execute("""SELECT COUNT(*) FROM predictions WHERE status='open'
                                  AND (base_rate IS NOT NULL OR market_prob IS NOT NULL)""").fetchone()[0]
        if not refd:
            print(f"  no resolved row carries a reference yet ({n_open_ref}/{o} open rows do). Until some do, the "
                  "engine has no outside yardstick: log new rows with --base-rate/--base-class (and --market where "
                  "a liquid market exists); backfill open rows with `ledger.py ref <id> ...`.")
        else:
            def line(label, sel):
                if not sel:
                    return
                m = sum(e for _, e, *_ in sel) / len(sel)
                ci2 = cluster_interval([(cl, e) for cl, e, *_ in sel])
                rng = f"  95% {ci2[0]:+.4f} .. {ci2[1]:+.4f}" if ci2 else "  (too few clusters for an interval)"
                print(f"  {label}: n={len(sel)} mean edge={m:+.4f}{rng}")
            late = [r for r in refd if r[3]]
            timely = [r for r in refd if not r[3]]
            line(f"all referenced rows ({len(late)} of {len(refd)} BACKFILLED late)", refd)
            if timely:
                line("  timely reference only", timely)
            else:
                # Every reference was written after the row was logged, so the reference had tape the
                # forecast did not. A late reference beating an early forecast is close to tautological
                # - printing it as "edge" without this line is how a contaminated number gets quoted.
                print("  timely reference only: n=0 -> THERE IS NO EDGE MEASUREMENT YET. Every reference "
                      "above was backfilled after its row was logged, so it carries tape the original "
                      "forecast could not have seen. Treat the number above as uninterpretable, not as "
                      "evidence the book loses to the outside view. R25 means the base rate is decided "
                      "BEFORE the probability; only rows logged that way can score an edge.")
            line("  vs market", [r for r in refd if r[2] == "market"])
            line("  vs base rate", [r for r in refd if r[2] == "base-rate"])
            line("  where the engine DIVERGED >0.10", [r for r in refd if r[4]])
            line("  where it stayed near the reference", [r for r in refd if not r[4]])
            print("  (+ = engine beat the reference. An interval that spans 0 is no evidence either way; "
                  "fewer than ~50 independent rows is noise.)")

        # -- is anyone looking? ----------------------------------------------------------------
        nrev = c.execute("SELECT COUNT(*) FROM revisions WHERE kind!='initial'").fetchone()[0]
        nrows = c.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        st = stale(quiet=True)
        print("\n-- updating --")
        print(f"  {nrev} revisions/confirmations across {nrows} rows ({nrev / max(nrows, 1):.1f} per row; Good Judgment's "
              f"best forecasters averaged ~8 per question). Open rows stale ({STALE_DAYS}+ days): {len(st)}/{o}")
        multi = c.execute("""SELECT AVG(brier), AVG((prob0-outcome)*(prob0-outcome)), COUNT(*) FROM predictions p
                             WHERE status='resolved' AND (SELECT COUNT(*) FROM revisions r
                             WHERE r.pred_id=p.id AND r.kind='revise')>0""").fetchone()
        if multi[2]:
            print(f"  revised rows (n={multi[2]}): time-weighted Brier {multi[0]:.4f} vs first-forecast {multi[1]:.4f} "
                  "(lower time-weighted = the updates helped)")

    print("\n-- probability calibration (first stated P) --")
    for lo, hi in [(0, .4), (.4, .6), (.6, .8), (.8, 1.01)]:
        r = c.execute("""SELECT COUNT(*),AVG(outcome),AVG(COALESCE(prob0,prob)) FROM predictions
                         WHERE status='resolved' AND COALESCE(prob0,prob)>=? AND COALESCE(prob0,prob)<?""", (lo, hi)).fetchone()
        if r[0]:
            gap = r[1] - r[2]   # + = under-confident (hits more than stated), - = over-confident
            print(f"  bucket {lo:.0%}-{min(hi, 1):.0%}: n={r[0]} mean stated={r[2]:.0%} actual={r[1]:.0%} "
                  f"gap={gap:+.0%}")

    print("\n-- conviction bands (does conviction predict accuracy?) --")
    for label, lo, hi in [("<0.60", 0, .6), ("0.60-0.80", .6, .8), (">0.80", .8, 1.01)]:
        r = c.execute("""SELECT COUNT(*),AVG(brier) FROM predictions
                         WHERE status='resolved' AND conviction>=? AND conviction<?""",
                      (lo, hi)).fetchone()
        if r[0]:
            print(f"  {label}: n={r[0]} mean Brier={r[1]:.4f}")
    r = c.execute("""SELECT COUNT(*) FROM predictions
                     WHERE status='resolved' AND conviction IS NULL""").fetchone()
    if r[0]:
        print(f"  (no conviction recorded: n={r[0]})")

    print("\n-- sectors --")
    for sec, cnt, brier in c.execute("""
            SELECT sectors, COUNT(*), AVG(brier) FROM predictions
            WHERE sectors IS NOT NULL AND sectors!='' GROUP BY sectors ORDER BY COUNT(*) DESC"""):
        b = f"mean Brier={brier:.4f}" if brier is not None else "unresolved"
        print(f"  {sec}: n={cnt} {b}")

    print("\n-- sources --")
    for src, cnt, nres, br in c.execute(
            "SELECT source, COUNT(*), SUM(CASE WHEN status='resolved' THEN 1 ELSE 0 END), "
            "AVG(CASE WHEN status='resolved' THEN brier END) FROM predictions GROUP BY source"):
        b = f"resolved={nres} mean Brier={br:.4f}" if br is not None else "none resolved"
        print(f"  {src}: n={cnt} {b}")

    # ── per-cluster calibration (hygiene rule 1: read calibration PER CLUSTER) ──
    print("\n-- per-cluster (resolved only) --")
    for cl, cnt, hit, br, pbar in c.execute("""
            SELECT COALESCE(NULLIF(cluster,''),'(standalone)') cl, COUNT(*), SUM(outcome),
                   AVG(brier), AVG(prob) FROM predictions WHERE status='resolved'
            GROUP BY cl ORDER BY COUNT(*) DESC"""):
        flag = "  <-- worse than a coin" if br > 0.25 else ""
        print(f"  {cl}: n={cnt} hit={hit}/{cnt} mean P={pbar:.2f} mean Brier={br:.4f}{flag}")

    # ── horizon length: are short-fuse calls or long-fuse calls better? ──
    print("\n-- by horizon length (days from log to horizon, resolved only) --")
    rows_h = c.execute("""SELECT CAST(julianday(substr(horizon,1,10)) - julianday(substr(ts,1,10)) AS INTEGER),
                          outcome, brier FROM predictions WHERE status='resolved'""").fetchall()
    for label, lo, hi in [("<=7d", -1, 7), ("8-30d", 8, 30), ("31-90d", 31, 90), (">90d", 91, 10**6)]:
        sel = [(o, b) for d, o, b in rows_h if d is not None and lo <= d <= hi]
        if sel:
            print(f"  {label}: n={len(sel)} hit={sum(o for o, _ in sel)}/{len(sel)} "
                  f"mean Brier={sum(b for _, b in sel) / len(sel):.4f}")

    # ── directional lean (tagged at logging; '' = legacy untagged) ──
    lean_rows = c.execute("""SELECT COALESCE(NULLIF(lean,''),'(untagged)') l, COUNT(*),
                             SUM(CASE WHEN status='resolved' THEN 1 ELSE 0 END),
                             AVG(CASE WHEN status='resolved' THEN brier END),
                             SUM(CASE WHEN status='open' THEN 1 ELSE 0 END)
                             FROM predictions GROUP BY l""").fetchall()
    if any(l != "(untagged)" for l, *_ in lean_rows):
        print("\n-- directional lean --")
        for l, cnt, nres, br, nopen in lean_rows:
            b = f"mean Brier={br:.4f}" if br is not None else "none resolved"
            print(f"  {l}: n={cnt} open={nopen} resolved={nres} {b}")

    # ── independence: correlated clusters count ONCE ──────────────────────
    # A cluster slug groups predictions that load on the same underlying (e.g.
    # 16 Iran calls). Raw counts/Brier over-weight big clusters; the effective
    # bet count and independence-weighted Brier give each thesis one vote.
    print("\n-- exposure concentration (each cluster = one effective bet) --")
    rows = c.execute(
        "SELECT COALESCE(NULLIF(cluster,''),'(standalone)') cl, COUNT(*), "
        "SUM(CASE WHEN status='resolved' THEN 1 ELSE 0 END) "
        "FROM predictions GROUP BY cl ORDER BY COUNT(*) DESC").fetchall()
    raw_total = c.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    named = c.execute(
        "SELECT COUNT(DISTINCT cluster) FROM predictions "
        "WHERE cluster IS NOT NULL AND cluster!=''").fetchone()[0]
    standalone_n = c.execute(
        "SELECT COUNT(*) FROM predictions WHERE cluster IS NULL OR cluster=''").fetchone()[0]
    effective = named + standalone_n
    for cl, cnt, res in rows:
        tag = "independent bets" if cl == "(standalone)" else "-> 1 effective bet"
        print(f"  {cl}: {cnt} rows ({res} resolved)  {tag}")
    print(f"  RAW rows={raw_total}  ->  EFFECTIVE independent bets={effective} "
          f"({named} clusters + {standalone_n} standalone)")

    # Independence-weighted Brier: each named cluster contributes its OWN mean
    # Brier as a single data point, alongside each standalone Brier.
    cluster_means = [avg for (_, avg) in c.execute(
        "SELECT cluster, AVG(brier) FROM predictions WHERE status='resolved' "
        "AND cluster IS NOT NULL AND cluster!='' GROUP BY cluster").fetchall()]
    standalone_briers = [b for (b,) in c.execute(
        "SELECT brier FROM predictions WHERE status='resolved' "
        "AND (cluster IS NULL OR cluster='')").fetchall()]
    vals = cluster_means + standalone_briers
    if vals:
        print(f"  independence-weighted mean Brier = {sum(vals)/len(vals):.4f} "
              f"(over {len(vals)} independent theses; vs raw over all resolved rows above)")
    else:
        print("  independence-weighted Brier: n/a (nothing resolved yet)")

    # ── Murphy (1973) decomposition: Brier = REL − RES + UNC ───────────────
    # REL (calibration, lower=better): do stated probabilities match observed
    # frequencies? RES (resolution, higher=better): do forecasts discriminate
    # outcomes from the base rate? UNC: base-rate entropy (not the forecaster's
    # doing). Tells you WHICH WAY the bot is wrong, not just how much.
    ro = c.execute("SELECT COALESCE(prob0,prob), outcome FROM predictions "
                   "WHERE status='resolved' AND outcome IS NOT NULL").fetchall()
    if len(ro) >= 5:
        n = len(ro)
        obar = sum(o for _, o in ro) / n
        bins = {}
        for p, o in ro:
            bins.setdefault(round(p, 1), []).append(o)
        rel = 0.0
        res = 0.0
        corr = 0.0            # Ferro & Fricker (2012) small-sample bias term
        for k, v in bins.items():
            nk = len(v)
            pbar = sum(p for p, o in ro if round(p, 1) == k) / nk
            ok = sum(v) / nk
            rel += nk * (pbar - ok) ** 2
            res += nk * (ok - obar) ** 2
            if nk > 1:
                corr += nk * ok * (1 - ok) / (nk - 1)
        rel /= n
        res /= n
        corr /= n
        unc = obar * (1 - obar)
        print("\n-- Brier decomposition (Murphy): REL - RES + UNC --")
        print(f"  reliability (calibration, lower better) = {rel:.4f}")
        print(f"  resolution  (discrimination, higher better) = {res:.4f}")
        print(f"  uncertainty (base rate {obar:.0%}) = {unc:.4f}")
        print(f"  -> check: {rel - res + unc:.4f} vs mean first-forecast Brier")
        rel_c, res_c = rel - corr, res - corr + unc / (n - 1)
        print(f"  small-sample corrected (Ferro & Fricker 2012): reliability = {rel_c:.4f}, resolution = {res_c:.4f}")
        small = min(len(v) for v in bins.values())
        if small < 40:
            print(f"  CAUTION: smallest bin has {small} rows. Below ~40 per bin the raw reliability term is inflated "
                  "several-fold; read the corrected line, and read neither as proof of miscalibration.")
        if rel_c > 0.05:
            print("  DIAGNOSIS: miscalibrated - stated probabilities drift from observed frequencies")
        if res_c < 0.02:
            print("  DIAGNOSIS: low resolution - forecasts barely beat always-guessing the base rate")
        lo_p, hi_p = min(p for p, _ in ro), max(p for p, _ in ro)
        if hi_p - lo_p < 0.6:
            print(f"  RANGE: every resolved row was stated between {lo_p:.2f} and {hi_p:.2f}. Resolution is capped by "
                  "that band - state unlikely events as low-P rows of the event itself, not flipped to the favoured side.")
    else:
        print("\n-- Brier decomposition: needs >=5 resolved (have "
              f"{len(ro)}) --")


def redteam():
    """Adversarial self-audit worksheet: every OPEN prediction formatted for
    attack — falsifier, sensitivity, cluster concentration, staleness. The
    contrarian-red-team skill drives this; the analyst must try to KILL each
    position, not defend it."""
    c = db()
    today = utc_now().date().isoformat()
    rows = c.execute("""SELECT id,ts,prob,conviction,horizon,cluster,prediction,
                        falsifier,sensitivity FROM predictions
                        WHERE status='open' ORDER BY horizon""").fetchall()
    if not rows:
        print("no open predictions")
        return
    from collections import Counter
    conc = Counter((r[5] or "(standalone)") for r in rows)
    print(f"RED-TEAM WORKSHEET — {len(rows)} open positions, {today}")
    print("Attack each: (a) is the falsifier still observable/dated? (b) what NEW tape "
          "since ts contradicts it? (c) is the stated sensitivity already happening? "
          "(d) cluster check — how many rows die together if the thesis is wrong?\n")
    for pid, ts, prob, conv, hz, cl, pred, fals, sens in rows:
        cl = cl or "(standalone)"
        age_flag = " [STALE: logged " + ts[:10] + "]" if ts[:10] < "2026-07-01" else ""
        due_flag = " [DUE]" if hz <= today else ""
        print(f"#{pid} P={prob:.2f} conv={conv if conv is not None else '-'} "
              f"horizon={hz}{due_flag} cluster={cl} (cluster size {conc[cl]}){age_flag}")
        print(f"   CLAIM : {pred[:160]}")
        print(f"   KILL IF: {(fals or 'NO FALSIFIER — defect!')[:160]}")
        print(f"   BREAKS ON: {(sens or '-')[:120]}\n")
    heavy = [f"{k} ({v} rows)" for k, v in conc.most_common(3) if v >= 5]
    if heavy:
        print(f"CONCENTRATION WARNING: {', '.join(heavy)} — these fail together; "
              "red-team the CLUSTER thesis, not just individual rows.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("add", help="log a prediction")
    a.add_argument("--event", required=True)
    a.add_argument("--prediction", required=True)
    a.add_argument("--prob", type=float, required=True, help="probability 0-1")
    a.add_argument("--horizon", required=True, help="YYYY-MM-DD")
    a.add_argument("--falsifier", required=True)
    a.add_argument("--sensitivity", default="")
    a.add_argument("--conviction", type=float, default=None, help="0-1 per rubric")
    a.add_argument("--sectors", default="", help="comma-separated, e.g. energy,shipping")
    a.add_argument("--tickers", default="", help="comma-separated, e.g. XLE,ZIM")
    a.add_argument("--direction", default="", choices=list(DIRECTIONS) + [""],
                   help="one direction per row; divergent directions = separate rows")
    a.add_argument("--source", default="manual", help="manual|auto|jiang-seed")
    a.add_argument("--cluster", default="", help="correlation cluster slug (e.g. iran-war); "
                   "blank = an independent bet. Correlated calls sharing a slug count as ONE "
                   "effective bet in the independence-weighted report.")
    a.add_argument("--lean", default="", choices=list(LEANS) + [""],
                   help="escalation | de-escalation | neutral - tag it NOW (hygiene rule 2)")
    def ref_args(sp):
        sp.add_argument("--base-rate", type=float, default=None, dest="base_rate",
                        help="outside-view probability from a named comparison class - decide this FIRST")
        sp.add_argument("--base-class", default="", dest="base_class",
                        help="the comparison class, its count and source, e.g. '21/48 interstate ceasefires resumed (Fortna 2003)'")
        sp.add_argument("--market", type=float, default=None, help="market-implied probability at logging, if a liquid market exists")
        sp.add_argument("--market-src", default="", dest="market_src", help="venue, contract, spread/volume, time")
        sp.add_argument("--diverge", default="", help=f"required when |P - reference| > {DIVERGE}: what you know that it does not")
    ref_args(a)
    a.add_argument("--dry-run", action="store_true", help="print the wording lint only; log nothing")
    a.add_argument("--ts", default=None, help="override timestamp (seeding)")

    r = sub.add_parser("resolve", help="score a matured prediction")
    r.add_argument("id")
    r.add_argument("outcome", choices=["0", "1"])
    r.add_argument("--asof", default="", help="YYYY-MM-DD the outcome became known (scoring stops there; "
                   "default: the horizon, or today if earlier)")

    rf = sub.add_parser("ref", help="record the reference forecast (base rate / market price) for an open row")
    rf.add_argument("id", type=int)
    ref_args(rf)
    rv = sub.add_parser("revise", help="move a live probability; history is kept and the path is scored")
    rv.add_argument("id", type=int)
    rv.add_argument("--prob", type=float, required=True)
    rv.add_argument("--reason", required=True, help="the dated datapoint that moved you")
    cf = sub.add_parser("confirm", help="looked again with fresh tape; probability stands")
    cf.add_argument("id", type=int)
    cf.add_argument("--reason", required=True, help="the dated datapoint you checked")
    sl = sub.add_parser("stale", help="open rows not revised or confirmed in N days")
    sl.add_argument("--days", type=int, default=STALE_DAYS)

    v = sub.add_parser("void", help="close a conditional whose trigger never fired - unscored, needs a lesson")
    v.add_argument("id")
    v.add_argument("--reason", required=True, help="which condition/carve-out made it unscoreable")

    sub.add_parser("due", help="open predictions past horizon")
    sub.add_parser("report", help="calibration report")
    sub.add_parser("redteam", help="adversarial self-audit worksheet of open predictions")
    to = sub.add_parser("trade-open", help="record a real entry (a position actually taken)")
    to.add_argument("ticker"); to.add_argument("--pred", type=int, required=True)
    to.add_argument("--direction", required=True, help="long|short")
    to.add_argument("--entry", type=float, required=True)
    to.add_argument("--target", type=float, required=True,
                    help="PRE-REGISTERED and frozen at entry (T02)")
    to.add_argument("--invalidation", type=float, required=True,
                    help="PRE-REGISTERED price, on the losing side of entry (T02/T03)")
    to.add_argument("--ts", default=""); to.add_argument("--note", default="")
    to.add_argument("--leg-vol", default="",
                    help="RV pairs only: realized vol pct/day per leg, e.g. 'XLE=1.25,USO=3.8' (T06)")
    to.add_argument("--bars", default="",
                    help="CSV ticker,date,high,low - lets T08/T13 run; without it they are "
                         "reported NOT CHECKED rather than silently passing")
    tc = sub.add_parser("trade-close", help="close a round-trip at a REAL exit price")
    tc.add_argument("id", type=int); tc.add_argument("--exit", type=float, required=True)
    tc.add_argument("--reason", required=True, choices=sorted(trade_rules.EXIT_REASONS),
                    help="closed vocabulary (T11)")
    tc.add_argument("--note", required=True, help="why this exit, in one line (T11)")
    tc.add_argument("--ts", default="")
    tc.add_argument("--bars", default="", help="CSV ticker,date,high,low - lets T14 check the fill")
    tk = sub.add_parser("trade-check", help="run T01-T14 over every trade in the book (gate)")
    tk.add_argument("--bars", default="",
                    help="CSV ticker,date,high,low so T08/T13 can run. Generate it with "
                         "`python pipeline/marketdata.py bars <TICKERS> --start D --out f.csv`")
    sub.add_parser("pnl", help="REALIZED p&l from closed round-trips only")
    sub.add_parser("sweep", help="cycle gate: overdue-unscored + resolved-unlessoned (exit 1 if any)")
    ls = sub.add_parser("lesson", help="record the diagnosis + doctrine patch for a resolved prediction")
    ls.add_argument("id", type=int)
    ls.add_argument("--verdict", required=True, help="hit-clean | hit-wrong-reason | partial | miss")
    ls.add_argument("--diagnosis", required=True, help="which premise held/failed and why")
    ls.add_argument("--patch", required=True, help="doctrine/skill section updated, or 'none - variance'")

    args = ap.parse_args()
    if args.cmd == "add":
        add(args)
    elif args.cmd == "resolve":
        resolve(args.id, args.outcome, args.asof)
    elif args.cmd == "ref":
        set_ref(args)
    elif args.cmd == "revise":
        revise(args.id, args.prob, args.reason)
    elif args.cmd == "confirm":
        revise(args.id, None, args.reason, kind="confirm")
    elif args.cmd == "stale":
        stale(args.days)
    elif args.cmd == "void":
        void(args.id, args.reason)
    elif args.cmd == "due":
        due()
    elif args.cmd == "redteam":
        redteam()
    elif args.cmd == "trade-open":
        c = db()
        leg_vol = {}
        for part in filter(None, (args.leg_vol or "").split(",")):
            k, _, v = part.partition("=")
            leg_vol[k.strip().upper()] = float(v)
        nxt = (c.execute("SELECT MAX(id) FROM trades").fetchone()[0] or 0) + 1
        cand = trade_rules.Trade(
            id=nxt, pred_id=args.pred, ticker=args.ticker.upper(), direction=args.direction,
            entry_price=args.entry, entry_ts=args.ts or utc_iso(), target=args.target,
            invalidation=args.invalidation, status="open", note=args.note, leg_vol=leg_vol)
        ctx = _trade_ctx(c, args.bars)
        errs = _report(trade_rules.check_trade(cand, ctx), "trade-open")
        _price_gap_note(ctx)
        if errs:
            sys.exit(f"REFUSED: {len(errs)} trading-rule violation(s) - nothing logged. "
                     f"The rules are the pre-registration; argue with them BEFORE the entry, "
                     f"not after the exit.")
        c.execute("INSERT INTO trades(pred_id,ticker,direction,entry_price,entry_ts,target,invalidation,status,note)"
                  " VALUES(?,?,?,?,?,?,?, 'open', ?)",
                  (args.pred, args.ticker.upper(), args.direction, args.entry,
                   args.ts or utc_iso(), args.target, args.invalidation, args.note))
        c.commit()
        print(f"trade #{c.execute('SELECT MAX(id) FROM trades').fetchone()[0]} OPEN "
              f"{args.direction} {args.ticker.upper()} @ {args.entry}")
    elif args.cmd == "trade-check":
        c = db()
        ctx = _trade_ctx(c, args.bars)
        c.row_factory = sqlite3.Row
        allrows = c.execute("SELECT * FROM trades ORDER BY id").fetchall()
        bad = 0
        for r in allrows:
            print(f"trade #{r['id']} {r['direction']} {r['ticker']} [{r['status']}]")
            bad += len(_report(trade_rules.check_trade(_trade_of(r), ctx), f"#{r['id']}"))
        _price_gap_note(ctx)
        print(f"\n{len(allrows)} trade(s), {bad} refusal(s)")
        sys.exit(1 if bad else 0)
    elif args.cmd == "trade-close":
        c = db()
        r = c.execute("SELECT ticker,direction,entry_price,status FROM trades WHERE id=?", (args.id,)).fetchone()
        if not r:
            sys.exit("no such trade")
        if r[3] != "open":
            sys.exit(f"trade #{args.id} already closed")
        pct = trade_rules.derive_pct(r[1], r[2], args.exit)
        c.row_factory = sqlite3.Row
        full = c.execute("SELECT * FROM trades WHERE id=?", (args.id,)).fetchone()
        cand = trade_rules.Trade(
            id=full["id"], pred_id=full["pred_id"], ticker=full["ticker"],
            direction=full["direction"], entry_price=full["entry_price"],
            entry_ts=full["entry_ts"] or "", target=full["target"],
            invalidation=full["invalidation"], exit_price=args.exit,
            exit_ts=args.ts or utc_iso(), exit_reason=args.reason, status="closed",
            pct=pct, note=(full["note"] or "") + " | " + args.note)
        ctx = _trade_ctx(c, args.bars, exclude_id=args.id)
        errs = _report(trade_rules.check_trade(cand, ctx), "trade-close")
        if errs:
            sys.exit(f"REFUSED: {len(errs)} trading-rule violation(s) - the trade is still open. "
                     f"Book at the PRE-REGISTERED level, not the hindsight one (lesson 4).")
        c.execute("UPDATE trades SET exit_price=?,exit_ts=?,exit_reason=?,status='closed',pct=?,note=? WHERE id=?",
                  (args.exit, args.ts or utc_iso(), args.reason, pct, cand.note, args.id))
        c.commit()
        print(f"trade #{args.id} CLOSED {r[0]} {r[1]} {r[2]} -> {args.exit} = {pct:+.2f}% ({args.reason})")
    elif args.cmd == "pnl":
        c = db()
        cl = c.execute("SELECT id,ticker,direction,entry_price,exit_price,pct,exit_reason,entry_ts,exit_ts,pred_id "
                       "FROM trades WHERE status='closed' ORDER BY id").fetchall()
        op = c.execute("SELECT id,ticker,direction,entry_price,target,invalidation,pred_id FROM trades "
                       "WHERE status='open' ORDER BY id").fetchall()
        print("=== REALIZED P&L (closed round-trips ONLY) ===")
        if not cl:
            print("  no closed trades yet")
        for t in cl:
            print(f"  #{t[0]} {t[1]} {t[2]} {t[3]} -> {t[4]} = {t[5]:+.2f}%  [{t[6]}] "
                  f"{str(t[7])[:10]}->{str(t[8])[:10]} (pred #{t[9]})")
        if cl:
            tot = sum(t[5] for t in cl)
            wins = sum(1 for t in cl if t[5] > 0)
            print(f"\n  closed: {len(cl)}  |  wins: {wins}/{len(cl)}  |  "
                  f"sum of returns: {tot:+.2f}%  |  avg per trade: {tot/len(cl):+.2f}%")
        print("\n=== OPEN (unrealized — NOT counted as profit) ===")
        if not op:
            print("  none")
        for t in op:
            print(f"  #{t[0]} {t[1]} {t[2]} entry {t[3]} target {t[4]} inval {t[5]} (pred #{t[6]})")
        print("\nNOTE: forecast accuracy (Brier) and trading P&L are different scoreboards.")
    elif args.cmd == "sweep":
        sweep()
    elif args.cmd == "lesson":
        lesson(args)
    else:
        report()


if __name__ == "__main__":
    main()
