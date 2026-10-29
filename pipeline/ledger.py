#!/usr/bin/env python3
"""Prediction ledger: log, resolve, Brier-score. SQLite at ledger/ledger.db

  add      log a prediction (argparse flags, see --help)
  resolve  <id> <1|0>  score a matured prediction
  due      list open predictions whose horizon has passed
  report   calibration report: prob buckets, conviction bands, sectors, sources
"""
import argparse
import pathlib
import re
import sqlite3
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import utc_iso, utc_now

DB = pathlib.Path(__file__).resolve().parent.parent / "ledger" / "ledger.db"

DIRECTIONS = ("up", "down", "vol", "neutral")

# formal §8.1 falsifier-symmetry rule (10-25 sweep: #11/#23/#68/#14). Escape clauses
# hide the real bet; a falsifier must be NOT(prediction). Warn, don't block.
ESCAPE_CLAUSE = re.compile(r"\b(absent|unless|barring|with no new|excluding|if no)\b", re.I)


def falsifier_lint(prediction, falsifier):
    hits = sorted({m.group(0).lower() for t in (prediction, falsifier)
                   for m in ESCAPE_CLAUSE.finditer(t or "")})
    if hits:
        print(f"WARN formal §8.1: escape-clause wording {hits} - if conditional, pre-register a "
              "VOID rule and ledger P(condition) as its own row; falsifier must be NOT(prediction).")


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


# contrarian-red-team Part C abstention zone (2026-10-29): a probability within 0.10 of a coin
# is "no view". Mechanical/auto calls there are refused; manual ones are warned. The report
# tracks whether resolution (Murphy RES) rises for calls logged after the rule.
ABSTAIN_RULE_DATE = "2026-10-29"
HEDGE_ZONE = (0.40, 0.60)
MECHANICAL_SOURCES = {"auto", "mechanical"}


def in_hedge_zone(p):
    return HEDGE_ZONE[0] < p < HEDGE_ZONE[1]


def add(args):
    if args.direction and args.direction not in DIRECTIONS:
        sys.exit(f"direction must be one of {DIRECTIONS}")
    if not (0.0 <= args.prob <= 1.0):
        sys.exit("prob must be in [0,1]")
    if args.conviction is not None and not (0.0 <= args.conviction <= 1.0):
        sys.exit("conviction must be in [0,1]")
    if in_hedge_zone(args.prob):
        if args.source in MECHANICAL_SOURCES:
            sys.exit(f"ABSTAIN (contrarian Part C): P={args.prob} is inside the no-view zone "
                     f"{HEDGE_ZONE[0]}-{HEDGE_ZONE[1]}; a {args.source} call there is not a prediction. "
                     "Not logged.")
        print(f"WARN contrarian Part C: P={args.prob} is in the hedge zone {HEDGE_ZONE[0]}-"
              f"{HEDGE_ZONE[1]} - abstain unless an independent lens moves it out.")
    falsifier_lint(args.prediction, args.falsifier)
    c = db()
    c.execute("""INSERT INTO predictions
        (ts,event,prediction,prob,horizon,falsifier,sensitivity,
         conviction,sectors,tickers,direction,source,cluster)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (args.ts or utc_iso(), args.event, args.prediction, args.prob,
         args.horizon, args.falsifier, args.sensitivity,
         args.conviction, args.sectors, args.tickers, args.direction, args.source, args.cluster))
    c.commit()
    print(f"logged #{c.execute('SELECT MAX(id) FROM predictions').fetchone()[0]}")


def resolve(pid, outcome):
    c = db()
    p = c.execute("SELECT prob FROM predictions WHERE id=?", (pid,)).fetchone()
    if not p:
        sys.exit("no such id")
    brier = (p[0] - (1.0 if int(outcome) else 0.0)) ** 2
    c.execute("""UPDATE predictions SET status='resolved',outcome=?,resolved_ts=?,brier=?
                 WHERE id=?""", (int(outcome), utc_iso(), brier, pid))
    c.commit()
    print(f"#{pid} resolved outcome={outcome} brier={brier:.4f}")


LESSON_VERDICTS = ("hit-clean", "hit-wrong-reason", "partial", "miss")
DORMANCY_DAYS = 7   # sweep fails when the ledger has seen no add/resolve/lesson for longer


def lesson(args):
    c = db()
    row = c.execute("SELECT status FROM predictions WHERE id=?", (args.id,)).fetchone()
    if not row:
        sys.exit("no such id")
    if row[0] != "resolved":
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
                              WHERE p.status='resolved' AND l.pred_id IS NULL
                              ORDER BY p.id""").fetchall()
    if unlessoned:
        bad = True
        print(f"RESOLVED WITHOUT LESSON ({len(unlessoned)}) - diagnose + patch (or 'none - variance'):")
        for i, out, br, pred in unlessoned:
            print(f"  #{i} outcome={'HIT' if out else 'MISS'} brier={br:.3f} :: {pred}")
    # dormancy alarm (10-25 lesson: 35 calls went 14-79 days unscored while nothing ran)
    last = max(x for x in c.execute(
        "SELECT MAX(ts) FROM predictions UNION ALL SELECT MAX(resolved_ts) FROM predictions "
        "UNION ALL SELECT MAX(ts) FROM lessons").fetchall() if x[0])[0]
    idle = (today - date.fromisoformat(last[:10])).days
    if idle > DORMANCY_DAYS:
        bad = True
        print(f"DORMANT: no ledger activity for {idle} days (last {last[:10]}). Run a cycle: "
              "ingest, analyze, log, resolve.")
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


def report():
    c = db()
    n, avg = c.execute(
        "SELECT COUNT(*),AVG(brier) FROM predictions WHERE status='resolved'").fetchone()
    o = c.execute("SELECT COUNT(*) FROM predictions WHERE status='open'").fetchone()[0]
    print(f"resolved={n} open={o} mean Brier={avg:.4f}" if n else f"resolved=0 open={o}")

    print("\n-- probability calibration --")
    for lo, hi in [(0, .4), (.4, .6), (.6, .8), (.8, 1.01)]:
        r = c.execute("""SELECT COUNT(*),AVG(outcome) FROM predictions
                         WHERE status='resolved' AND prob>=? AND prob<?""", (lo, hi)).fetchone()
        if r[0]:
            print(f"  bucket {lo:.0%}-{hi:.0%}: n={r[0]} predicted~{(lo+hi)/2:.0%} actual={r[1]:.0%}")

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
    for src, cnt in c.execute(
            "SELECT source, COUNT(*) FROM predictions GROUP BY source"):
        print(f"  {src}: n={cnt}")

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
    ro = c.execute("SELECT prob, outcome FROM predictions "
                   "WHERE status='resolved' AND outcome IS NOT NULL").fetchall()
    if len(ro) >= 5:
        rel, res, unc, obar = murphy(ro)
        print("\n-- Brier decomposition (Murphy): REL - RES + UNC --")
        print(f"  reliability (calibration, lower better) = {rel:.4f}")
        print(f"  resolution  (discrimination, higher better) = {res:.4f}")
        print(f"  uncertainty (base rate {obar:.0%}) = {unc:.4f}")
        print(f"  -> check: {rel - res + unc:.4f} vs mean Brier above")
        if rel > 0.05:
            print("  DIAGNOSIS: miscalibrated — stated probabilities drift from observed frequencies")
        if res < 0.02:
            print("  DIAGNOSIS: low resolution — forecasts barely beat always-guessing the base rate")
    else:
        print("\n-- Brier decomposition: needs >=5 resolved (have "
              f"{len(ro)}) --")

    # ── abstention-rule tracking: does resolution rise after the rule? ────────
    print(f"\n-- Abstention rule ({ABSTAIN_RULE_DATE}): is resolution rising? --")
    for label, cond in (("before", "ts < ?"), ("after ", "ts >= ?")):
        logged = c.execute(f"SELECT prob FROM predictions WHERE {cond}", (ABSTAIN_RULE_DATE,)).fetchall()
        hedge = sum(1 for (p,) in logged if in_hedge_zone(p))
        rr = c.execute(f"SELECT prob, outcome FROM predictions WHERE status='resolved' "
                       f"AND outcome IS NOT NULL AND {cond}", (ABSTAIN_RULE_DATE,)).fetchall()
        line = (f"  {label}: {len(logged)} logged, {hedge} in the hedge zone "
                f"({hedge / len(logged):.0%})" if logged else f"  {label}: none logged")
        if len(rr) >= 5:
            rel, res, _, _ = murphy(rr)
            line += f"; {len(rr)} resolved, RES={res:.4f}, REL={rel:.4f}"
        else:
            line += f"; {len(rr)} resolved (RES needs >=5)"
        print(line)


def murphy(ro):
    """Murphy (1973) partition of the Brier score over 0.1-wide probability bins.
    ro = [(prob, outcome)]. Returns (reliability, resolution, uncertainty, base rate)."""
    n = len(ro)
    obar = sum(o for _, o in ro) / n
    bins = {}
    for p, o in ro:
        bins.setdefault(round(p, 1), []).append((p, o))
    rel = res = 0.0
    for v in bins.values():
        nk = len(v)
        pbar = sum(p for p, _ in v) / nk
        ok = sum(o for _, o in v) / nk
        rel += nk * (pbar - ok) ** 2
        res += nk * (ok - obar) ** 2
    return rel / n, res / n, obar * (1 - obar), obar


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
    a.add_argument("--ts", default=None, help="override timestamp (seeding)")

    r = sub.add_parser("resolve", help="score a matured prediction")
    r.add_argument("id")
    r.add_argument("outcome", choices=["0", "1"])

    sub.add_parser("due", help="open predictions past horizon")
    sub.add_parser("report", help="calibration report")
    sub.add_parser("redteam", help="adversarial self-audit worksheet of open predictions")
    to = sub.add_parser("trade-open", help="record a real entry (a position actually taken)")
    to.add_argument("ticker"); to.add_argument("--pred", type=int, required=True)
    to.add_argument("--direction", required=True, help="long|short")
    to.add_argument("--entry", type=float, required=True)
    to.add_argument("--target", type=float); to.add_argument("--invalidation", type=float)
    to.add_argument("--ts", default=""); to.add_argument("--note", default="")
    tc = sub.add_parser("trade-close", help="close a round-trip at a REAL exit price")
    tc.add_argument("id", type=int); tc.add_argument("--exit", type=float, required=True)
    tc.add_argument("--reason", required=True, help="target|invalidation|manual")
    tc.add_argument("--ts", default="")
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
        resolve(args.id, args.outcome)
    elif args.cmd == "due":
        due()
    elif args.cmd == "redteam":
        redteam()
    elif args.cmd == "trade-open":
        c = db()
        c.execute("INSERT INTO trades(pred_id,ticker,direction,entry_price,entry_ts,target,invalidation,status,note)"
                  " VALUES(?,?,?,?,?,?,?, 'open', ?)",
                  (args.pred, args.ticker.upper(), args.direction, args.entry,
                   args.ts or utc_iso(), args.target, args.invalidation, args.note))
        c.commit()
        print(f"trade #{c.execute('SELECT MAX(id) FROM trades').fetchone()[0]} OPEN "
              f"{args.direction} {args.ticker.upper()} @ {args.entry}")
    elif args.cmd == "trade-close":
        c = db()
        r = c.execute("SELECT ticker,direction,entry_price,status FROM trades WHERE id=?", (args.id,)).fetchone()
        if not r:
            sys.exit("no such trade")
        if r[3] != "open":
            sys.exit(f"trade #{args.id} already closed")
        pct = ((args.exit - r[2]) / r[2] * 100.0) if r[1] == "long" else ((r[2] - args.exit) / r[2] * 100.0)
        c.execute("UPDATE trades SET exit_price=?,exit_ts=?,exit_reason=?,status='closed',pct=? WHERE id=?",
                  (args.exit, args.ts or utc_iso(), args.reason, pct, args.id))
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
