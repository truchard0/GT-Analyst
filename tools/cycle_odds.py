#!/usr/bin/env python3
"""cycle_odds.py - how long does THIS phase of a fight-talk-fight cycle last?

The no-view number for DURATION rows, the way range_odds.py is the no-view number for price rows.

Why it exists (research review 2026-09-20, section 5; doctrine 16.18): the engine went 0-for-8
forecasting the DIRECTION of the next leg. What the conflict literature finds forecastable is the
level and the recent distribution of violence, which contains both legs (ViEWS competitions: no-change
and the last-12-months distribution beat the models), and since 1945 a talks round is only weak
evidence that a war is ending (Min 2020). So a call like "strikes resume by D" is priced as a
duration question - "does the current pause, already A days old, end within N more days?" - from the
cycle's own completed phases, pulled toward an outside reference class because two or three phases
are almost no data.

Model: phase endings arrive at a constant daily hazard h (memoryless). Prior h ~ Gamma(a, b) with
a = --prior-weight (pseudo-phases) and b chosen so the prior predictive median duration is --prior-median days.
Data: each completed phase adds one ending and its days; the current phase adds its days and no ending.
Posterior predictive:  P(phase survives N more days) = (b' / (b' + N)) ** a'.

  python tools/cycle_odds.py --completed 22,28 --current 10 --days 22 --stated 0.45
  python tools/cycle_odds.py --completed 109,21,9 --current 0 --days 30 --prior-median 60   # fighting rounds

Honest limits, printed with every answer: the memoryless assumption ignores deadlines that make an
ending more likely on a known date (an MOU expiry, a UN vote), and the prior's reference class is never
exact - so the tool prints a BAND across prior weights, and that band, not the point, is the no-view odds.
"""
import argparse
import sys

# Reference classes for the prior median (days a pause lasts). Documented so the choice is visible.
#   65  - ETH/PRIO ceasefire dataset (Clayton et al. 2022): median time to failure of failed ceasefires at a
#         25-fatality threshold. Civil conflicts; most are bare cessations with no monitoring.
#   193 - same dataset at a 100-fatality threshold (failure = a return to real fighting).
# Fortna (2003): 21 of 48 interstate ceasefires eventually failed; stalemate endings ~27x the hazard of a
# decisive outcome; DMZs, monitors and third-party guarantees cut it sharply. Use a SHORTER median when the
# pause has none of those markers and a LONGER one when it acquires them.
DEFAULT_PRIOR_MEDIAN = 65.0


def survive(completed, current, days, prior_median, prior_weight):
    """P(the current phase, already `current` days old, lasts `days` more)."""
    a = prior_weight + len(completed)
    # Gamma(a, b) hazard -> Lomax durations with median b * (2**(1/a) - 1); solve for b so the PRIOR median is honoured
    b = (prior_median / (2 ** (1 / prior_weight) - 1) if prior_weight > 0 else 0.0) + sum(completed) + current
    if a <= 0 or b <= 0:
        raise ValueError("need at least one completed phase or a prior")
    return (b / (b + days)) ** a


def band(completed, current, days, prior_median):
    """Odds across prior weights 0 (the cycle's own history only) .. 2 (lean on the reference class)."""
    out = {}
    for w in (0.0, 0.5, 1.0, 2.0):
        if w == 0.0 and not completed:
            continue
        out[w] = survive(completed, current, days, prior_median, w)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--completed", default="", help="durations in days of COMPLETED phases of the same kind, e.g. 22,28")
    ap.add_argument("--current", type=float, required=True, help="age in days of the phase running now")
    ap.add_argument("--days", type=float, required=True, help="days from today to the row's horizon")
    ap.add_argument("--prior-median", type=float, default=DEFAULT_PRIOR_MEDIAN, dest="prior_median",
                    help=f"median phase length in the outside reference class (default {DEFAULT_PRIOR_MEDIAN:g}; see the header)")
    ap.add_argument("--prior-weight", type=float, default=1.0, dest="prior_weight",
                    help="how many pseudo-phases the reference class is worth (default 1)")
    ap.add_argument("--stated", type=float, default=None, help="the P you intend to log for 'the phase ENDS by the horizon'")
    args = ap.parse_args(argv)
    try:
        completed = [float(x) for x in args.completed.split(",") if x.strip()]
    except ValueError:
        sys.exit("--completed takes comma-separated day counts")
    if args.days <= 0 or args.current < 0 or any(d <= 0 for d in completed):
        sys.exit("durations must be positive")

    s = survive(completed, args.current, args.days, args.prior_median, args.prior_weight)
    b = band(completed, args.current, args.days, args.prior_median)
    ends = {w: 1 - v for w, v in b.items()}
    lo, hi = min(ends.values()), max(ends.values())
    print(f"phase history: {len(completed)} completed ({', '.join(f'{d:g}d' for d in completed) or 'none'}), "
          f"current {args.current:g}d old; horizon {args.days:g}d out; prior median {args.prior_median:g}d")
    print(f"P(phase ENDS within {args.days:g}d)   = {1 - s:.2f}     P(it LASTS beyond) = {s:.2f}   [prior weight {args.prior_weight:g}]")
    print("band across prior weights: " + "  ".join(f"w={w:g}: {e:.2f}" for w, e in ends.items())
          + f"   -> no-view odds of an ending: {lo:.2f} .. {hi:.2f}")
    print("limits: constant hazard (no deadline effects); reference class is approximate; "
          f"{len(completed)} completed phases is almost no data - quote the band, not the point.")
    if args.stated is not None:
        if lo - 0.10 <= args.stated <= hi + 0.10:
            print(f"VERDICT: stated {args.stated:.2f} is inside the band (+/-0.10). Fine as a no-view price.")
        else:
            side = "above" if args.stated > hi else "below"
            print(f"VERDICT: stated {args.stated:.2f} is {side} the band by more than 0.10. That is a VIEW: it needs a dated, "
                  "capital-committed catalyst (a deployment order, a deadline, a monitoring mechanism) - not the tone of "
                  "the latest headlines - or a re-price.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
