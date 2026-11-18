#!/usr/bin/env python3
"""Range / barrier odds - the OUTSIDE VIEW for any level, range or "does NOT close above X" call.

Written after the 2026-09-19 scoring cycle. #69 (SPY 705-775 AND QQQ 640-720 AND SMH 480-605
through 9/30) was logged at P=0.60 and died in TWO sessions: QQQ sat 4.7% under its upper bound
with ~1.5%/day realized vol and 42 sessions to run. At July's realized vol a driftless random
walk gave the QQQ leg alone ~0.1 and the three-asset compound less than that - the call needed
a ~+0.5 edge over the no-view odds and no mechanism for it was named. The engine never ran the
arithmetic. This tool is the arithmetic. Stdlib only.

It answers one question: with NO view at all (driftless log-random-walk at recent realized vol),
how likely is it that daily CLOSES stay inside [lo, hi] for N sessions? That number is the
reference class (contrarian-red-team #3). The engine's P may deviate from it - but only with a
NAMED mechanism, and by more than ~0.20 only with a catalyst-dated reason.

Usage:
  python tools/range_odds.py --spot 687.99 --lo 640 --hi 720 --days 42 --vol 1.6
  python tools/range_odds.py --spot 582.7 --hi 605 --days 3 --vol 2.9         # one-sided: stays BELOW hi
  python tools/range_odds.py --spot 45.3 --hi 100 --days 28 --vol 3.5 --touch  # P(TOUCHES hi) instead
  python tools/range_odds.py --closes 745.76,744.78,751.28,... --lo 705 --hi 775 --days 42
        (--closes: vol is estimated from the series, spot = last close)
  python tools/range_odds.py --legs "SPY:747.03:705:775:0.9" "QQQ:687.99:640:720:1.6" --days 42
        (compound AND of several assets: reports each leg, the independent product and the
         perfectly-correlated ceiling - the truth lies between; if even the CEILING is below
         your stated P, the call is mis-priced. Better: split it into rows, per CLAUDE.md.)

--vol is DAILY close-to-close volatility in percent (1.6 = 1.6%/day). Rule of thumb: annualized
implied vol / 16.
"""
import argparse
import math
import random
import statistics
import sys


def realized_vol(closes):
    rets = [math.log(b / a) for a, b in zip(closes, closes[1:]) if a > 0 and b > 0]
    if len(rets) < 5:
        sys.exit("need at least 6 closes to estimate vol")
    return statistics.pstdev(rets)


def stay_inside(spot, lo, hi, days, vol, paths=40000, seed=7, sessions_outside=1):
    """P(no run of `sessions_outside` consecutive daily closes outside [lo,hi] within `days`).
    Monte Carlo on DAILY closes (the falsifiers are written on closes, so a continuous-barrier
    formula would overstate the breach odds). Driftless in log space."""
    rnd = random.Random(seed)
    llo = math.log(lo) if lo else -math.inf
    lhi = math.log(hi) if hi else math.inf
    x0 = math.log(spot)
    ok = 0
    for _ in range(paths):
        x, run, alive = x0, 0, True
        for _ in range(days):
            x += rnd.gauss(0.0, vol)
            if x < llo or x > lhi:
                run += 1
                if run >= sessions_outside:
                    alive = False
                    break
            else:
                run = 0
        ok += alive
    return ok / paths


def verdict(p_inside, stated):
    if stated is None:
        return ""
    gap = stated - p_inside
    if abs(gap) <= 0.10:
        return f"stated P={stated:.2f} is within 0.10 of the no-view odds - fine, the view is modest."
    if abs(gap) <= 0.20:
        return (f"stated P={stated:.2f} deviates {gap:+.2f} from the no-view odds - "
                "NAME the mechanism in --sensitivity.")
    return (f"stated P={stated:.2f} deviates {gap:+.2f} from the no-view odds - that is a LARGE claim. "
            "Needs a dated catalyst/mechanism, or re-price.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spot", type=float)
    ap.add_argument("--lo", type=float, default=None, help="lower bound on closes (omit for one-sided)")
    ap.add_argument("--hi", type=float, default=None, help="upper bound on closes (omit for one-sided)")
    ap.add_argument("--days", type=int, required=True, help="TRADING sessions to the horizon")
    ap.add_argument("--vol", type=float, help="daily vol in PERCENT (1.6 = 1.6%%/day)")
    ap.add_argument("--closes", help="comma-separated recent closes; estimates vol, spot = last")
    ap.add_argument("--hold", type=int, default=1,
                    help="consecutive closes outside the band needed to breach (e.g. 3 for 'holds 3+ sessions')")
    ap.add_argument("--touch", action="store_true", help="report P(breach) instead of P(stays inside)")
    ap.add_argument("--stated", type=float, default=None, help="the P you intend to ledger, for the gap check")
    ap.add_argument("--legs", nargs="*", help='compound AND: "NAME:spot:lo:hi:vol%%" ... (blank lo/hi = none)')
    a = ap.parse_args()

    if a.legs:
        ps = []
        for leg in a.legs:
            name, spot, lo, hi, vol = (leg.split(":") + [""] * 5)[:5]
            p = stay_inside(float(spot), float(lo) if lo else None, float(hi) if hi else None,
                            a.days, float(vol) / 100.0, sessions_outside=a.hold)
            ps.append(p)
            print(f"  {name:6s} spot {float(spot):.2f} band [{lo or '-'}, {hi or '-'}] vol {vol}%/d "
                  f"-> P(stays inside {a.days}d) = {p:.2f}")
        prod = math.prod(ps)
        print(f"  compound AND: independent product = {prod:.2f} | perfectly-correlated ceiling = {min(ps):.2f}")
        print("  " + verdict(min(ps), a.stated).replace("no-view odds", "no-view CEILING") if a.stated else "")
        print("  RULE: a compound of N assets is N rows (CLAUDE.md: separate assets = separate rows).")
        return

    if a.closes:
        closes = [float(x) for x in a.closes.split(",") if x.strip()]
        vol = realized_vol(closes)
        spot = a.spot or closes[-1]
        print(f"  realized vol from {len(closes)} closes = {vol * 100:.2f}%/day")
    else:
        if a.spot is None or a.vol is None:
            sys.exit("give --spot and --vol, or --closes")
        spot, vol = a.spot, a.vol / 100.0
    if a.lo is None and a.hi is None:
        sys.exit("give --lo and/or --hi")
    p = stay_inside(spot, a.lo, a.hi, a.days, vol, sessions_outside=a.hold)
    room = []
    if a.hi:
        room.append(f"{(a.hi / spot - 1) * 100:+.1f}% to hi = {(math.log(a.hi / spot)) / (vol * math.sqrt(a.days)):.2f} sigma-to-horizon")
    if a.lo:
        room.append(f"{(a.lo / spot - 1) * 100:+.1f}% to lo = {(math.log(spot / a.lo)) / (vol * math.sqrt(a.days)):.2f} sigma-to-horizon")
    print("  headroom: " + " | ".join(room))
    if a.touch:
        print(f"  NO-VIEW P(breaches within {a.days} sessions) = {1 - p:.2f}")
        print("  " + verdict(1 - p, a.stated))
    else:
        print(f"  NO-VIEW P(closes stay inside for {a.days} sessions) = {p:.2f}")
        print("  " + verdict(p, a.stated))
    print("  (driftless random walk at the given vol; vol clusters, so after a vol spike the true odds "
          "of staying inside are LOWER than this.)")


if __name__ == "__main__":
    main()
