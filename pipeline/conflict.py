#!/usr/bin/env python3
"""conflict.py - the coherence check R28 could not make: two rows about HOW HARD a conflict gets.

THE GAP. R28 compares rows that take OPPOSITE directions (up vs down) on a shared ticker. Every Iran row is tagged
direction 'vol', so 'no return to war-scale conflict' (#19) and 'a further attack despite the ceasefire' (#15) looked
identical to it. A war has one latent variable - how hard the fighting gets inside a window - and every such row is a
probabilistic claim about it. This module makes the claim explicit and asks the only question a pair of claims can be
asked: can ONE probability distribution over that variable give both rows the probabilities they state?

THE VARIABLE. L = the highest level reached inside the row's window [now, horizon].  Per cluster (SCALES):
    iran-war:  0 settled   1 pause (no strikes, incidents rare)   2 incidents (shipping / proxy attacks)
               3 strikes (at least one acknowledged strike on Iranian territory)   4 war-scale (a sustained campaign)
A row declares the interval its event IMPLIES: 'if this row's event happens, L lands in [lo, hi]', so the row says
P(L in [lo, hi]) >= p (a row can be narrower than its level - 'a vengeance plot' implies L>=2 but is not all of it).
#19 'no war-scale return' is [0,3]; #15 'a further attack despite the ceasefire' is [2,4]; #38 'ground invasion' is [4,4].

TWO CHECKS (both pure; both explain themselves):
  1. FEASIBILITY. For every pair of rows in a cluster: can one distribution give P(L in I_a) >= p_a and P(L in I_b) >= p_b?
     Same window = one variable; nested windows = the longer one is at least as high (l_late >= l_early). If any outcome
     satisfies both intervals the pair always fits; if none does, the claims need different outcomes and p_a + p_b must
     fit under 1 (0.03 slack). Disjoint claims that sum past 1, and a nested pair that cannot coexist, fail here.
  2. ESCALATION. If one row says P(L>=3) = p (an acknowledged strike on Iranian soil) and another says L cannot reach
     war-scale with probability q, then P(war-scale) <= 1-q must still be able to hold P(war-scale | strike) * p. This war's
     own record sets that conditional (ESCALATION: k of n strike episodes became sustained campaigns). ERROR if the
     conflict survives the Wilson lower bound of the conditional, WARN if only the point estimate breaks it. A longer-
     window row is scaled to the shorter window at a constant hazard first - the one approximation, stated.

WHAT IT DOES NOT DO. It does not know whether a row's premise is alive (16.16), does not price anything, and only sees rows
that declare a level. A pair it passes can still be wrong together; it refuses only the ones that cannot both be right.

    python pipeline/conflict.py --demo        # replay the 2026-07-08 batch
"""
from __future__ import annotations

import datetime as dt
import itertools
import math
from dataclasses import dataclass
from typing import Optional

SCALES = {"iran-war": ("settled", "pause", "incidents", "strikes", "war-scale")}
# P(sustained campaign | an acknowledged strike episode on Iranian territory): data/war_timeline.json has 7 strike episodes
# (strike days separated by <= 7 quiet days): the opening war, round 2, round 3 (each a run of 11+ consecutive days) and four
# one-off retaliations (5/7, 5/25-27, 6/7-10, 6/26-27). 3 of 7. AUDIT 2026-10-23: this was (3, 3) until a re-count found the four
# one-offs had been left out; the (3, 3) figure made the escalation check refuse rows (#59, #64) it should not have. 7 episodes
# is still little data, which is why the ERROR test uses the Wilson lower bound and the point estimate only warns.
ESCALATION = {"iran-war": (3, 7)}
SLACK = 0.03          # each stated probability may be off by this much before a pair is called infeasible
TOL = 0.02


@dataclass(frozen=True)
class Claim:
    id: str
    prob: float
    lo: int
    hi: int
    horizon: str          # ISO date
    cluster: str


@dataclass(frozen=True)
class Finding:
    severity: str         # error | warn
    ids: tuple[str, ...]
    text: str


def parse_level(s: str, cluster: str) -> tuple[int, int]:
    """'3' -> (3,3);  '0-3' -> (0,3).  Validated against the cluster's scale."""
    top = len(SCALES[cluster]) - 1
    try:
        parts = [int(x) for x in str(s).strip().split("-")]
    except ValueError:
        raise ValueError(f"level {s!r}: write a level or a range of levels, e.g. 3 or 0-3")
    lo, hi = (parts[0], parts[0]) if len(parts) == 1 else (parts[0], parts[1])
    if len(parts) > 2 or not 0 <= lo <= hi <= top:
        raise ValueError(f"level {s!r}: must satisfy 0 <= lo <= hi <= {top} on {cluster}'s scale {SCALES[cluster]}")
    return lo, hi


def _days(horizon: str, today: dt.date) -> int:
    return max(1, (dt.date.fromisoformat(horizon[:10]) - today).days)


def _wilson_lower(k: int, n: int, z: float = 1.645) -> float:
    if n == 0:
        return 0.0
    ph = k / n
    d = 1 + z * z / n
    centre = ph + z * z / (2 * n)
    return max(0.0, (centre - z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))) / d)


def _feasible(pa: float, ia: tuple[int, int], pb: float, ib: tuple[int, int], same: bool, top: int) -> bool:
    """Can ONE distribution over the level give P(la in ia) >= pa and P(lb in ib) >= pb?
    Same window: both claims are about one variable (la == lb). Nested windows: the longer one is at least as high.
    If any allowed outcome satisfies both claims, put all the mass there and both hold. If none does, the two claims
    must live on different outcomes and their probabilities have to fit under 1 together."""
    both = any(ia[0] <= la <= ia[1] and ib[0] <= lb <= ib[1]
               for la in range(top + 1) for lb in range(top + 1)
               if ((la == lb) if same else (la <= lb)))
    return both or pa + pb <= 1.0 + SLACK


def _scale_window(p: float, d_from: int, d_to: int) -> float:
    """P(event inside d_from days) restated for a SHORTER window d_to at a constant hazard."""
    if d_to >= d_from:
        return p
    return 1.0 - (1.0 - p) ** (d_to / d_from)


def check(claims: list[Claim], today: Optional[dt.date] = None) -> list[Finding]:
    today = today or dt.date.today()
    out: list[Finding] = []
    for cluster, scale in SCALES.items():
        cs = [c for c in claims if c.cluster == cluster]
        top = len(scale) - 1
        for a, b in itertools.combinations(cs, 2):
            da, db = _days(a.horizon, today), _days(b.horizon, today)
            same = abs(da - db) <= 7
            first, second = (a, b) if da <= db else (b, a)
            if not _feasible(first.prob, (first.lo, first.hi), second.prob, (second.lo, second.hi),
                             same=same, top=top):
                out.append(Finding("error", (a.id, b.id),
                                   f"#{a.id} (P {a.prob:.2f}, L in {a.lo}-{a.hi} by {a.horizon}) and #{b.id} "
                                   f"(P {b.prob:.2f}, L in {b.lo}-{b.hi} by {b.horizon}) cannot both be right: no single "
                                   f"distribution over how hard the fighting gets gives them both those probabilities"))
        k, n = ESCALATION.get(cluster, (0, 0))
        if not n:
            continue
        c_pt, c_lo = (k + 1) / (n + 2), _wilson_lower(k, n)
        for x, y in itertools.permutations(cs, 2):
            if not (x.lo >= 3 and y.hi == top - 1 and y.hi >= 3):       # x: a strike happens; y: war-scale does not
                continue
            dx, dy = _days(x.horizon, today), _days(y.horizon, today)
            px = _scale_window(x.prob, dx, dy)
            room = (1.0 - y.prob) + TOL
            if c_lo * px > room:
                out.append(Finding("error", (x.id, y.id),
                                   f"#{x.id} says a strike on Iranian territory (P {x.prob:.2f}, scaled to #{y.id}'s "
                                   f"window {px:.2f}) while #{y.id} says war-scale does NOT happen (P {y.prob:.2f}): "
                                   f"that leaves {1 - y.prob:.2f} for war-scale, but in this war {k} of {n} strike "
                                   f"episodes became sustained campaigns (lower bound {c_lo:.2f}), which needs at least "
                                   f"{c_lo * px:.2f}"))
            elif c_pt * px > room:
                out.append(Finding("warn", (x.id, y.id),
                                   f"#{x.id} (strike, scaled {px:.2f}) and #{y.id} (no war-scale, P {y.prob:.2f}) fit only "
                                   f"if a strike has under a {room / px:.0%} chance of becoming a campaign; this war's "
                                   f"record ({k}/{n}) puts it near {c_pt:.0%}"))
    return out



# ───────────────────────── cross-cluster world states ─────────────────────────
# The level check above compares rows INSIDE one conflict cluster. The #29 miss (OPEC+ 'defends price into a normalizing-
# Hormuz glut') sat in another cluster from the hits that said Hormuz would NOT normalize (#22, #73), so nothing compared
# them. A WORLD STATE is a named ordinal variable that rows from ANY cluster can make claims about; a row declares the
# interval of that variable its event requires (`--state hormuz=0-1`). Two rows whose claims about one state cannot both
# hold (disjoint intervals) must have probabilities that fit under 1 together, or one is refused.
#
# Semantics, stated plainly: a claim is 'P(state over the row's window lies in [lo,hi]) >= p'. Rows whose horizons are
# within STATE_SAME_DAYS of each other are treated as claims about ONE variable; rows further apart are not compared (a
# state can legitimately change in between). That is an approximation, not a model of dynamics.
STATES = {
    "hormuz": ("shut", "impaired", "normal"),              # transits: <25% / 25-90% / ~pre-war of the pre-war average
    "brent_peak": ("<=80", "80-90", "90-100", ">100"),    # highest Brent reached inside the window
    "cpi_jun": ("soft", "neutral", "hot"),
    "cpi_jul": ("soft", "neutral", "hot"),
    "cpi_aug": ("soft", "neutral", "hot"),
}
STATE_SAME_DAYS = 45


@dataclass(frozen=True)
class StateClaim:
    id: str
    prob: float
    state: str
    lo: int
    hi: int
    horizon: str


def parse_state(spec: str) -> tuple[str, int, int]:
    """'hormuz=0-1' -> ('hormuz', 0, 1);  'brent_peak=3' -> ('brent_peak', 3, 3)."""
    try:
        name, rng = str(spec).split("=", 1)
        name = name.strip()
        top = len(STATES[name]) - 1
        parts = [int(x) for x in rng.strip().split("-")]
    except (ValueError, KeyError):
        raise ValueError(f"state {spec!r}: write NAME=LO[-HI] with NAME in {sorted(STATES)}")
    lo, hi = (parts[0], parts[0]) if len(parts) == 1 else (parts[0], parts[1])
    if len(parts) > 2 or not 0 <= lo <= hi <= top:
        raise ValueError(f"state {spec!r}: must satisfy 0 <= lo <= hi <= {top} on {name}'s scale {STATES[name]}")
    return name, lo, hi


def check_states(claims: list[StateClaim], today: Optional[dt.date] = None) -> list[Finding]:
    today = today or dt.date.today()
    out: list[Finding] = []
    for name, scale in STATES.items():
        cs = [c for c in claims if c.state == name]
        top = len(scale) - 1
        for a, b in itertools.combinations(cs, 2):
            if abs(_days(a.horizon, today) - _days(b.horizon, today)) > STATE_SAME_DAYS:
                continue
            if not _feasible(a.prob, (a.lo, a.hi), b.prob, (b.lo, b.hi), same=True, top=top):
                out.append(Finding("error", (a.id, b.id),
                                   f"#{a.id} (P {a.prob:.2f}) needs {name} in {_names(scale, a.lo, a.hi)} and #{b.id} "
                                   f"(P {b.prob:.2f}) needs {name} in {_names(scale, b.lo, b.hi)}: those cannot both be "
                                   f"true, yet together they claim {a.prob + b.prob:.2f} of the probability"))
    return out


def _names(scale, lo, hi):
    return scale[lo] if lo == hi else f"{scale[lo]}..{scale[hi]}"


def _demo() -> None:
    """The 2026-07-08 batch, as logged."""
    today = dt.date(2026, 7, 8)
    rows = [Claim("19", .70, 0, 3, "2026-09-06", "iran-war"), Claim("15", .70, 2, 4, "2026-09-06", "iran-war"),
            Claim("20", .55, 2, 4, "2026-09-06", "iran-war"), Claim("21", .58, 2, 3, "2026-09-06", "iran-war"),
            Claim("16", .74, 3, 4, "2027-01-08", "iran-war")]
    found = check(rows, today)
    print(f"{len(rows)} rows, {len(found)} finding(s)")
    for f in found:
        print(f"  {f.severity.upper()}: {f.text}")
    if not found:
        print("(no pair in that batch is formally incoherent - #19's loss was a dead premise, 16.16, not a contradiction)")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
