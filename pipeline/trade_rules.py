#!/usr/bin/env python3
"""Enforced TRADING ruleset (T01..T14) - the sibling of schema.py's prediction ruleset R01..R27.
Stdlib only, `mypy --strict` clean, and it imports NOTHING from the rest of the repo.

The prediction side of this engine has had machine-checked rules since 2026-09-20. The TRADE
book has had none: trade discipline lived as prose in STATE.md section 8, and prose is exactly
what let trade #2's pre-registered 800 target be touched on 7/28 and sit unbooked for seven
weeks - while the 1035 invalidation was pierced at 1042.40 on 9/9 and the row still read "open"
(STATE.md section 2; reports/20260919_scoring-cycle-reality-check.md section 5).

Every rule below is the machine form of a loss or a near-loss already in this book. Each rule
has an id (T01..T14) so a violation names the rule it broke, and the rule's source is in its
one-line description.

Like schema.check(), nothing here touches the disk or the network: everything the rules need
about the repo - ledger rows, other open trades, prior stored values, price bars, realized vol,
branch weights - arrives in a `TradeContext`, so the rules stay pure and testable.

    python pipeline/trade_rules.py            # print the rule list
"""
from __future__ import annotations

import datetime
import math
import re
import sys
from dataclasses import dataclass, field
from typing import Literal, Optional

TRADE_SCHEMA_VERSION = 1     # 1 = the first enforced trading ruleset, 2026-09-21

# ── closed vocabularies ──────────────────────────────────────────────────────
#: severities mirror schema.py: "error" is a refusal, "warning" is for the human to overrule.
Severity = Literal["error", "warning"]

#: `direction` and `status` arrive from SQLite as plain strings, so they are typed `str` on the
#: dataclass and checked by the rules (T01, and the open/closed split below) rather than by the
#: parser - a bad value must produce a named rule violation, not a crash.
DIRECTIONS: frozenset[str] = frozenset({"long", "short"})
STATUSES: frozenset[str] = frozenset({"open", "closed"})

#: T11's closed vocabulary. `target` = the pre-registered level printed; `invalidation` = the
#: falsifier printed; `horizon` = the parent prediction's clock ran out with neither touched;
#: `thesis-void` = the premise stopped existing (the ledger's `void` case, applied to a trade).
EXIT_REASONS: frozenset[str] = frozenset({"target", "invalidation", "horizon", "thesis-void"})

#: a trade's direction must agree with its parent prediction's stated direction (T01).
DIRECTION_AGREES: dict[str, str] = {"long": "up", "short": "down"}

# ── numeric thresholds (each one is a number the book already paid for) ──────
CONCENTRATION_CAP: float = 0.35      # hygiene rule 1 / R15 - iran-war has been over it all summer
MIN_REWARD_RISK: float = 1.5         # T04 floor
MAX_REWARD_RISK: float = 8.0         # T04 fantasy-target warning
RV_VOL_RATIO_CAP: float = 1.5        # doctrine 13h - #74 XLE (1.25%/day) vs USO (3.8%/day)
DIRECTION_PROB_CAP: float = 0.55     # doctrine 16.15 / R12 - direction rows cap at 0.55
TAIL_BRANCH_P: float = 0.35          # T12 - below this the parent lives on a tail branch
PNL_TOLERANCE: float = 0.01          # T11 - re-derived pct must match the stored pct
PRICE_EPS: float = 0.005             # half a cent: two prices are "the same level"


# ── the ruleset ──────────────────────────────────────────────────────────────
TRADE_RULES: dict[str, str] = {
    "T01": "every trade cites an OPEN or resolved ledger prediction that exists, and the trade's "
           "direction agrees with that row's stated direction - no orphan trades",
    "T02": "entry, target and invalidation are pre-registered NUMBERS at open and are frozen after "
           "entry_ts; a later edit to any of them is refused (STATE.md lesson 1: pre-register the "
           "falsifier before the move - #61 was flagged at-risk in real time and resolved HIT)",
    "T03": "invalidation is a PRICE, never a narrative string, and it sits on the losing side of "
           "entry: long -> invalidation < entry < target; short -> target < entry < invalidation",
    "T04": "reward:risk = |target-entry| / |entry-invalidation| >= 1.5; > 8 warns - a fantasy target "
           "dressed as a good ratio (the 8/1 position report's 'checklist, not a level alone')",
    "T05": "refused if the parent prediction's cluster is over the 35pct concentration cap, or if "
           "ticker+direction duplicates another OPEN trade (#70 and #27 were the same SMH bet twice)",
    "T06": "a two-ticker relative-value trade must declare BOTH legs' realized vol; a ratio over 1.5x "
           "is not RV, it is a levered direction bet on the high-vol leg and it inherits the 0.55 "
           "direction cap (doctrine 13h; #74 XLE 1.25pct/day vs USO 3.8pct/day, 0.56 - second-worst "
           "score in the book)",
    "T07": "no sizing language anywhere in the note - this engine does direction and mechanism only "
           "(doctrine 14; the same regex shape schema.py's R18 uses)",
    "T08": "STALE-TARGET GATE: an OPEN trade whose session high (long) or low (short) has touched the "
           "pre-registered target is EXIT-DUE and the check FAILS until it is booked (trade #2 MU - "
           "the 800 target was touched 7/28 and sat unbooked for seven weeks)",
    "T09": "a target exit books AT the pre-registered target, never the hindsight extreme "
           "(STATE.md lesson 4: MU booked at 800, not at the 737.88 low)",
    "T10": "no averaging down: a second trade on the same ticker+direction while the first is open "
           "and underwater is refused",
    "T11": "a closed trade carries an exit_reason from {target, invalidation, horizon, thesis-void} "
           "and a note, and the re-derived pct matches the stored pct to within 0.01",
    "T12": "branch-robustness: a trade whose parent prediction hangs on a timeline branch with p < 0.35 "
           "is a tail-branch expression - warned, and the note must say what it wins on BESIDES that "
           "branch (#44 RTX was chosen because it wins on the modal branch and most alternatives)",
    "T13": "STALE-INVALIDATION GATE: an OPEN trade whose session low (long) or high (short) has touched "
           "the pre-registered invalidation is DEAD and the check FAILS until it is booked - the "
           "falsifier binds or it is not a falsifier (MU printed 1042.40 on 9/9 through the 1035 "
           "invalidation while trade #2 still read open)",
    "T14": "a booked fill has to be a fill: exit_ts is after entry_ts and names a session whose own "
           "high/low range contains exit_price (the 9/19 late booking is dated 7/28 - open 839.61, "
           "low 789.09 - because that is the session in which a cover at 800 could fill)",
}


# ── the data the rules need, passed in ───────────────────────────────────────
#: one session of tape: (YYYY-MM-DD, high, low). Supplied as data - this module never fetches.
PriceBar = tuple[str, float, float]

#: a pre-registered level as the ledger can actually hold it. SQLite columns are typed by value,
#: not by declaration, so a narrative string CAN sit in the REAL column - that is T03's whole point.
Level = Optional[float | str]


@dataclass(frozen=True)
class LedgerRow:
    """The slice of a `predictions` row a trade rule needs."""
    id: int
    direction: str                  # "up" | "down" | "vol" | "neutral" | ""
    status: str                     # "open" | "resolved" | "void"
    cluster: str
    prob: float


@dataclass(frozen=True)
class Trade:
    """One row of the `trades` table, plus the realized-vol declaration T06 asks for."""
    id: int
    pred_id: Optional[int]
    ticker: str
    direction: str
    entry_price: Level
    entry_ts: str
    target: Level
    invalidation: Level
    exit_price: Level = None
    exit_ts: Optional[str] = None
    exit_reason: Optional[str] = None
    status: str = "open"
    pct: Optional[float] = None
    note: str = ""
    #: for a relative-value pair: ticker -> realized vol in pct/day, declared AT OPEN (T06).
    leg_vol: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class TradeContext:
    """Everything the rules need from the repo - passed in, so rules stay pure and testable."""
    #: ledger rows by id, for T01/T05/T06/T12
    predictions: dict[int, LedgerRow] = field(default_factory=dict)
    #: open prediction counts by cluster + the open total, for the 35pct cap (T05)
    open_by_cluster: dict[str, int] = field(default_factory=dict)
    open_total: int = 0
    #: the OTHER open trades in the book, for T05's duplicate test and T10's averaging-down test
    open_trades: tuple[Trade, ...] = ()
    #: ticker -> session bars, for T08 / T13 / T14. Data only - this module never fetches prices.
    prices: dict[str, list[PriceBar]] = field(default_factory=dict)
    #: ticker -> last price, for T10's "underwater" test
    last_price: dict[str, float] = field(default_factory=dict)
    #: the values already stored for this trade id, for T02's freeze
    stored: dict[int, Trade] = field(default_factory=dict)
    #: pred_id -> the probability of the timeline branch the row hangs on, for T12
    branch_p: dict[int, float] = field(default_factory=dict)
    #: the date the check is being run (YYYY-MM-DD); bars after it are ignored
    asof: str = ""


@dataclass
class Finding:
    rule: str
    where: str
    message: str
    severity: Severity = "error"

    def __str__(self) -> str:
        return f"[{self.rule}] {self.where}: {self.message}"


# ── helpers ──────────────────────────────────────────────────────────────────
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

#: copied (deliberately NOT imported) from schema.py's R18 - doctrine 14.
_SIZING = re.compile(r"\b(position siz|% of (the )?(portfolio|book|account)|allocate \d|"
                     r"buy \d+ (shares|contracts)|leverage of|risk \d+(\.\d+)?%)", re.I)

#: T12's "what does it win on besides that branch" - the #44 RTX note is the positive template.
_BRANCH_ROBUST = re.compile(r"branch[- ]robust|regardless of|besides that branch|even if the branch|"
                            r"also wins|independent of the branch|modal branch", re.I)

#: how a two-ticker relative-value expression is written in this book: "XLE/USO", "XLE vs USO".
_RV_SPLIT = re.compile(r"\s*(?:/|,|\||\bvs\.?\b)\s*", re.I)


def _level(v: Level) -> Optional[float]:
    """A pre-registered level is a finite NUMBER. Anything else (a narrative string, None, nan)
    is not a level - the caller decides which rule that breaks."""
    if isinstance(v, str) or v is None:
        return None
    f = float(v)
    return f if math.isfinite(f) else None


def _date(ts: Optional[str]) -> str:
    """The YYYY-MM-DD prefix of an ISO timestamp, or '' if there isn't one."""
    s = (ts or "").strip()
    return s[:10] if _ISO_DATE.match(s[:10]) else ""


def _ts(ts: Optional[str]) -> Optional[datetime.datetime]:
    try:
        dt = datetime.datetime.fromisoformat((ts or "").strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= PRICE_EPS


def _bars(ctx: TradeContext, ticker: str, start: str, end: str) -> list[PriceBar]:
    """The supplied session bars for `ticker` between two YYYY-MM-DD bounds, inclusive."""
    out: list[PriceBar] = []
    for bar in ctx.prices.get(ticker.upper(), []):
        day = bar[0][:10]
        if not _ISO_DATE.match(day):
            continue
        if start and day < start:
            continue
        if end and day > end:
            continue
        out.append(bar)
    return sorted(out)


def _legs(ticker: str) -> list[str]:
    """['XLE', 'USO'] for a relative-value expression; ['RTX'] for an outright."""
    return [p for p in (s.strip().upper() for s in _RV_SPLIT.split(ticker.strip())) if p]


def rv_verdict(trade: Trade) -> tuple[Optional[str], Optional[float]]:
    """(high-vol leg, vol ratio) for a declared two-leg trade, else (None, None). Doctrine 13h."""
    legs = _legs(trade.ticker)
    if len(legs) != 2:
        return None, None
    vols = {k.upper(): v for k, v in trade.leg_vol.items()}
    a, b = vols.get(legs[0]), vols.get(legs[1])
    if a is None or b is None or a <= 0.0 or b <= 0.0:
        return None, None
    hi = legs[0] if a >= b else legs[1]
    return hi, max(a, b) / min(a, b)


def reward_risk(entry: float, target: float, invalidation: float) -> Optional[float]:
    """|target-entry| / |entry-invalidation|, or None when the risk leg is zero-width."""
    risk = abs(entry - invalidation)
    return None if risk < PRICE_EPS else abs(target - entry) / risk


def derive_pct(direction: str, entry: float, exit_price: float) -> float:
    """The same arithmetic `ledger.py trade-close` books, re-derived independently (T11)."""
    if direction == "short":
        return (entry - exit_price) / entry * 100.0
    return (exit_price - entry) / entry * 100.0


# ── the checker ──────────────────────────────────────────────────────────────
def check_trade(trade: Trade, ctx: TradeContext) -> list[Finding]:
    """Run T01..T14 over one trade. Returns every finding; `severity == "error"` is a refusal.

    Open-only rules (T08, T13) and closed-only rules (T09, T11, T14) skip the other state.
    T05's concentration half is evaluated only for OPEN trades: today's cluster counts cannot be
    used to retroactively refuse a trade that was entered months ago.
    """
    out: list[Finding] = []
    w = f"trade #{trade.id}"

    def err(rule: str, msg: str) -> None:
        out.append(Finding(rule, w, msg))

    def warn(rule: str, msg: str) -> None:
        out.append(Finding(rule, w, msg, "warning"))

    direction = (trade.direction or "").strip().lower()
    is_open = trade.status == "open"
    entry = _level(trade.entry_price)
    target = _level(trade.target)
    inval = _level(trade.invalidation)
    exit_price = _level(trade.exit_price)
    parent = ctx.predictions.get(trade.pred_id) if trade.pred_id is not None else None

    if direction not in DIRECTIONS:
        err("T01", f"direction {trade.direction!r} is outside {sorted(DIRECTIONS)}")
    if trade.status not in STATUSES:
        err("T11", f"status {trade.status!r} is outside {sorted(STATUSES)} - a trade row is open "
                   f"or closed, and the closed rules run on anything that is not open")

    # ── T01: no orphan trades ────────────────────────────────────────────────
    if trade.pred_id is None:
        err("T01", "cites no ledger prediction - a trade is the expression of a logged call, "
                   "never a free-standing opinion")
    elif parent is None:
        err("T01", f"cites prediction #{trade.pred_id}, which is not in the ledger")
    else:
        if parent.status not in ("open", "resolved"):
            err("T01", f"parent #{parent.id} is {parent.status!r} - a trade may only express an "
                       f"OPEN or resolved row")
        want = DIRECTION_AGREES.get(direction)
        if want is not None and parent.direction and parent.direction != want:
            err("T01", f"{direction} disagrees with prediction #{parent.id}, whose stated direction "
                       f"is {parent.direction!r} (expected {want!r})")
        elif want is not None and not parent.direction:
            warn("T01", f"prediction #{parent.id} states no direction - the agreement test cannot run")

    # ── T02: pre-registered and then frozen ──────────────────────────────────
    for name, raw, lvl in (("entry", trade.entry_price, entry),
                           ("target", trade.target, target),
                           ("invalidation", trade.invalidation, inval)):
        if raw is None:
            err("T02", f"{name} is not pre-registered - entry, target and invalidation are all set "
                       f"BEFORE the move, never after it (STATE.md lesson 1)")
        elif lvl is None:
            err("T02", f"{name} {raw!r} is not a number")
    if not _date(trade.entry_ts):
        err("T02", f"entry_ts {trade.entry_ts!r} is not a dated ISO timestamp")

    prior = ctx.stored.get(trade.id)
    if prior is not None:
        frozen: tuple[tuple[str, Level, Level], ...] = (
            ("entry_price", trade.entry_price, prior.entry_price),
            ("target", trade.target, prior.target),
            ("invalidation", trade.invalidation, prior.invalidation))
        for name, now_v, was_v in frozen:
            a, b = _level(now_v), _level(was_v)
            changed = (not _same(a, b)) if (a is not None and b is not None) else (now_v != was_v)
            if changed:
                err("T02", f"{name} was stored as {was_v!r} at entry and is now {now_v!r} - a "
                           f"pre-registered level is frozen after entry_ts; book the trade, do not "
                           f"move the goalposts")
        if trade.entry_ts != prior.entry_ts:
            err("T02", f"entry_ts was stored as {prior.entry_ts!r} and is now {trade.entry_ts!r} - "
                       f"re-dating an entry re-dates every gate that hangs off it")

    # ── T03: the invalidation is a price, on the losing side ─────────────────
    if isinstance(trade.invalidation, str):
        err("T03", f"invalidation {trade.invalidation!r} is narrative, not a price - a falsifier you "
                   f"cannot test against the tape is not a falsifier")
    if entry is not None and target is not None and inval is not None:
        if direction == "long" and not (inval < entry < target):
            err("T03", f"long needs invalidation < entry < target, got {inval} / {entry} / {target}")
        if direction == "short" and not (target < entry < inval):
            err("T03", f"short needs target < entry < invalidation, got {target} / {entry} / {inval}")

    # ── T04: reward:risk ─────────────────────────────────────────────────────
    if entry is not None and target is not None and inval is not None:
        rr = reward_risk(entry, target, inval)
        if rr is None:
            err("T04", "invalidation sits on top of entry - the risk leg has no width")
        elif rr < MIN_REWARD_RISK:
            err("T04", f"reward:risk {rr:.2f} is below {MIN_REWARD_RISK} "
                       f"(|{target}-{entry}| / |{entry}-{inval}|)")
        elif rr > MAX_REWARD_RISK:
            warn("T04", f"reward:risk {rr:.2f} is above {MAX_REWARD_RISK} - check the TARGET, not the "
                        f"ratio: a fantasy level makes any stop look cheap")

    # ── T05: concentration + duplication ─────────────────────────────────────
    if parent is not None and is_open and ctx.open_total > 0:
        n = ctx.open_by_cluster.get(parent.cluster, 0)
        share = n / ctx.open_total
        if parent.cluster and share > CONCENTRATION_CAP:
            err("T05", f"parent #{parent.id} is in cluster {parent.cluster!r}, which holds {n} of "
                       f"{ctx.open_total} open rows ({share:.0%}) - over the "
                       f"{CONCENTRATION_CAP:.0%} cap; the trade is more of a bet the book already has")
    for other in ctx.open_trades:
        if other.id == trade.id or other.status != "open":
            continue
        if other.ticker.strip().upper() == trade.ticker.strip().upper() \
                and (other.direction or "").strip().lower() == direction:
            err("T05", f"duplicates OPEN trade #{other.id} ({other.direction} {other.ticker}) - one "
                       f"bet logged twice is one bet, and it prices like two (#70 / #27)")

    # ── T06: relative value, or a levered direction bet wearing its clothes ──
    legs = _legs(trade.ticker)
    if len(legs) == 2:
        missing = [lg for lg in legs if lg not in {k.upper() for k in trade.leg_vol}]
        if missing:
            err("T06", f"relative-value pair {'/'.join(legs)} does not declare realized vol for "
                       f"{', '.join(missing)} - without both legs' vol you cannot know whether this is "
                       f"RV or a levered direction bet (doctrine 13h)")
        else:
            hi, ratio = rv_verdict(trade)
            if hi is None or ratio is None:
                err("T06", "declared realized vol must be a positive pct/day for both legs")
            elif ratio > RV_VOL_RATIO_CAP:
                err("T06", f"vol ratio {ratio:.2f}x exceeds {RV_VOL_RATIO_CAP}x - this is NOT a "
                           f"relative-value trade, it is a levered direction bet on {hi}; re-express it "
                           f"as one and take the direction caps (#74)")
                if parent is not None and parent.prob > DIRECTION_PROB_CAP:
                    err("T06", f"as a direction bet it inherits the {DIRECTION_PROB_CAP} cap, but "
                               f"parent #{parent.id} is priced {parent.prob} (doctrine 16.15 / R12)")
    elif trade.leg_vol:
        warn("T06", "realized vol is declared but the trade names one ticker - no RV test to run")

    # ── T07: direction and mechanism only ────────────────────────────────────
    if _SIZING.search(trade.note or ""):
        err("T07", "sizing language in the note - this layer does direction and mechanism only "
                   "(doctrine 14)")

    # ── T08 / T13: the two stale gates, for OPEN trades ──────────────────────
    if is_open and entry is not None:
        start, end = _date(trade.entry_ts), ctx.asof or ""
        bars = _bars(ctx, legs[0] if len(legs) == 1 else trade.ticker, start, end)
        if target is not None:
            if direction == "long":
                hit = next((b for b in bars if b[1] >= target - PRICE_EPS), None)
            else:
                hit = next((b for b in bars if b[2] <= target + PRICE_EPS), None)
            if hit is not None:
                err("T08", f"EXIT-DUE: the pre-registered target {target} was touched on {hit[0]} "
                           f"(session high {hit[1]}, low {hit[2]}) and the trade is still open - book it. "
                           f"This is trade #2's seven-week defect, mechanized")
        if inval is not None:
            if direction == "long":
                dead = next((b for b in bars if b[2] <= inval + PRICE_EPS), None)
            else:
                dead = next((b for b in bars if b[1] >= inval - PRICE_EPS), None)
            if dead is not None:
                err("T13", f"DEAD: the pre-registered invalidation {inval} was touched on {dead[0]} "
                           f"(session high {dead[1]}, low {dead[2]}) and the trade is still open - the "
                           f"falsifier binds or it is not a falsifier")

    # ── T09 / T11 / T14: closed trades ───────────────────────────────────────
    if not is_open:
        reason = (trade.exit_reason or "").strip().lower()
        if reason not in EXIT_REASONS:
            err("T11", f"exit_reason {trade.exit_reason!r} is outside the closed vocabulary "
                       f"{sorted(EXIT_REASONS)}")
        if not (trade.note or "").strip():
            err("T11", "a closed trade carries a note saying what happened - a bare number teaches "
                       "nothing next cycle")
        if exit_price is None:
            err("T11", f"exit_price {trade.exit_price!r} is not a number")
        elif entry is not None:
            want = derive_pct(direction, entry, exit_price)
            if trade.pct is None:
                err("T11", f"pct is not stored; re-derived {want:+.2f}%")
            elif abs(want - trade.pct) > PNL_TOLERANCE:
                err("T11", f"stored pct {trade.pct:+.4f}% does not match the re-derived "
                           f"{want:+.4f}% (tolerance {PNL_TOLERANCE})")

        # T09
        if reason == "target" and exit_price is not None and target is not None:
            better = (exit_price > target + PRICE_EPS) if direction == "long" \
                else (exit_price < target - PRICE_EPS)
            if better:
                err("T09", f"a target exit books AT {target}, not at {exit_price} - that is the "
                           f"hindsight extreme, and the book does not get paid for prices it never "
                           f"committed to (STATE.md lesson 4)")
            elif not _same(exit_price, target):
                warn("T09", f"target exit booked at {exit_price} against a pre-registered target of "
                            f"{target} - say in the note why the fill slipped")

        # T14
        ets, xts = _ts(trade.entry_ts), _ts(trade.exit_ts)
        if xts is None:
            err("T14", f"exit_ts {trade.exit_ts!r} is not a dated ISO timestamp")
        elif ets is not None and xts <= ets:
            err("T14", f"exit_ts {trade.exit_ts} is not after entry_ts {trade.entry_ts} - a round trip "
                       f"takes time")
        day = _date(trade.exit_ts)
        series = ctx.prices.get((legs[0] if len(legs) == 1 else trade.ticker).upper(), [])
        if series and day and exit_price is not None:
            bar = next((b for b in series if b[0][:10] == day), None)
            if bar is None:
                err("T14", f"exit_ts is dated {day}, for which no session is on the tape - date the "
                           f"booking to the session the fill could actually have happened in")
            elif not (bar[2] - PRICE_EPS <= exit_price <= bar[1] + PRICE_EPS):
                err("T14", f"exit_price {exit_price} is outside the {day} range "
                           f"[{bar[2]}, {bar[1]}] - that fill never traded")

    # ── T10: no averaging down ───────────────────────────────────────────────
    if entry is not None:
        for other in ctx.open_trades:
            if other.id == trade.id or other.status != "open":
                continue
            if other.ticker.strip().upper() != trade.ticker.strip().upper():
                continue
            if (other.direction or "").strip().lower() != direction:
                continue
            first = _level(other.entry_price)
            last = ctx.last_price.get(trade.ticker.strip().upper())
            if first is None or last is None:
                continue
            underwater = last < first if direction == "long" else last > first
            if underwater:
                err("T10", f"open trade #{other.id} is the same {direction} {other.ticker} at "
                           f"{first} and is underwater at {last} - adding here is averaging down, "
                           f"which turns one falsifiable bet into an unfalsifiable one")

    # ── T12: branch robustness ───────────────────────────────────────────────
    if trade.pred_id is not None and trade.pred_id in ctx.branch_p:
        p = ctx.branch_p[trade.pred_id]
        if p < TAIL_BRANCH_P:
            warn("T12", f"prediction #{trade.pred_id} hangs on a branch weighted {p:.2f} (< "
                        f"{TAIL_BRANCH_P:.2f}) - this is a tail-branch expression, not a base case")
            if not _BRANCH_ROBUST.search(trade.note or ""):
                err("T12", "a tail-branch trade's note must say what it wins on BESIDES that branch "
                           "(#44 RTX: branch-robust, it paid whichever way Iran went)")

    return out


def errors(findings: list[Finding]) -> list[Finding]:
    """The refusals only - warnings are for the human."""
    return [f for f in findings if f.severity == "error"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ("rules", "-h", "--help"):
        sys.exit(f"usage: {sys.argv[0]} [rules]")
    for k, v in TRADE_RULES.items():
        print(f"{k}  {v}")
