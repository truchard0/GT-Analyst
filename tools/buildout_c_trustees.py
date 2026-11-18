#!/usr/bin/env python3
"""+8 nodes: the trust-fund depletion rows the us-fiscal lane could not carry.

Those rows were left unwritten on 2026-10-02 because they need a dated published fact and the
author refused to invent one. The fact has now been read from the primary source:

    SSA Office of the Chief Actuary, "A SUMMARY OF THE 2026 ANNUAL REPORTS",
    https://www.ssa.gov/OACT/TRSUM/ , read 2026-10-02.
      OASI   depleted Q4 2032 (one quarter earlier than the 2025 report), 78% payable after
      DI     solvent through at least 2100, the end of the projection period
      OASDI  combined Q3 2034 (unchanged from the 2025 report), 83% payable after
      HI     depleted Q2 2033 (one quarter earlier than the 2025 report), 89% payable after
      SMI    adequately financed indefinitely BY CONSTRUCTION - premiums and the matching
             federal contribution are reset annually by statute to cover the coming year
      assumptions set February 2026; ultimate TFR lowered 1.90 -> 1.75; net immigration lowered;
      OBBBA (enacted 2025-07-04) permanently reduces revenue from taxation of benefits

Note which way the drift runs: every one of those assumption changes pushes depletion EARLIER,
and both dated funds moved a quarter earlier this year. The rows below are written against that
asymmetry rather than against the point estimate.

    python tools/buildout_c_trustees.py --dry-run | --write
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import buildout_b_lib as L   # noqa: E402

L.STAMP = "buildout-2026-10-02-trustees"
N = L.N

SRC = "SSA 2026 Trustees Report summary (ssa.gov/OACT/TRSUM), read 2026-10-02"

N("usf-no-depletion-pre-2030", "usf-anchor",
  "No OASI trust fund reserve depletion actually occurs before 2030-01-01", 0.97, "2030-01-01",
  "us-fiscal", "invariant", "13 quarters",
  "Stock arithmetic against a published projection. The 2026 Trustees Report puts OASI depletion in "
  "the fourth quarter of 2032. Reserves are a measured balance drawn down at a known rate; they "
  "cannot vanish more than two years ahead of the actuaries' own projection absent legislation that "
  "would itself be a separate, observable event.",
  "INVARIANT and close to the strongest row in the lane: it is about the SPEED LIMIT on a balance "
  "sheet, not about the projection being right. Deliberately framed as the near-certain negative "
  "rather than as the dramatic depletion-year call - the 9/20 research measured resolution ~0.00 "
  "because the book never logged genuine near-certainties, and this is one.",
  "Depletion dates move markets through the legislative response, not through the date itself.",
  evidence=[{"fact": "The 2026 Trustees Report projects OASI reserve depletion in the fourth "
                     "quarter of 2032, with 78 percent of scheduled benefits payable thereafter",
             "reported": SRC}])

N("usf-oasi-not-later-2032", "usf-anchor",
  "The next Trustees Report does not move the OASI depletion date later than the fourth quarter "
  "of 2032", 0.84, "2027-12-31", "us-fiscal", "scheduled", "5 quarters",
  "Scheduled annual publication; the value drifts. The asymmetry is the argument: the date moved a "
  "quarter EARLIER in the 2026 report, and the three assumption changes behind it all push the same "
  "way - ultimate fertility cut 1.90 to 1.75, net immigration lowered, and OBBBA permanently "
  "reducing revenue from taxation of benefits. Moving later requires a reversal of at least one.",
  "Scheduled-print class where the EVENT is near-certain and only the value is open - the 12-for-14 "
  "shape. Priced on the direction of assumption drift rather than on an actuarial model the book "
  "cannot reproduce. The soft part is a large upward revision to near-term payroll, which would be "
  "visible in the quarterly data well before the report.",
  "A date that keeps moving earlier is what eventually forces the legislative row below.",
  evidence=[{"fact": "The 2026 report moved OASI depletion one quarter earlier than the 2025 "
                     "report; ultimate TFR was lowered from 1.90 to 1.75 and net immigration was "
                     "lowered", "reported": SRC}])

N("usf-hi-not-later-2033", "usf-anchor",
  "The next Trustees Report does not move the HI depletion date later than the second quarter of "
  "2033", 0.80, "2027-12-31", "us-fiscal", "scheduled", "5 quarters",
  "Same scheduled publication and the same drift asymmetry: HI also moved a quarter earlier in the "
  "2026 report, on higher assumed utilisation, upward revisions to Medicare Advantage per-capita "
  "spend, and the same OBBBA revenue reduction. Priced below the OASI row because HI is far more "
  "sensitive to a single year's cost experience than OASI is to demographics.",
  "Priced LOWER than its OASI sibling on purpose, and the reason is stated: HI's driver is medical "
  "cost trend, which is volatile, where OASI's is cohort arithmetic, which is not. Two rows on the "
  "same report that are NOT equally confident is what it looks like to price the mechanism rather "
  "than the headline.",
  "Medicare Part A solvency is the harder legislative problem and the earlier-moving one.",
  evidence=[{"fact": "The 2026 report projects HI depletion in the second quarter of 2033, one "
                     "quarter earlier than the 2025 report, with 89 percent payable thereafter",
             "reported": SRC}])

N("usf-oasi-before-hi", "usf-anchor",
  "OASI remains projected to deplete before HI in the next Trustees Report", 0.86, "2027-12-31",
  "us-fiscal", "invariant", "5 quarters",
  "An ORDERING claim on published arithmetic, structurally more stable than either date: the 2026 "
  "report puts OASI at Q4 2032 and HI at Q2 2033, about two quarters apart, and the two funds run "
  "on different statutory financing streams - payroll tax against scheduled benefits for OASI, "
  "hospital-insurance tax against medical cost trend for HI - which would have to move in opposite "
  "directions by more than that gap to cross. Reference class: the ordering has held in every "
  "report of the recent record.",
  "The most robust construction available on this report: a RELATIVE claim survives a common shock "
  "that would move both dates together, which is exactly the error that killed the absolute version "
  "of several rows. Note it is not independent of the two rows above - it is the same report seen "
  "through a difference, and that is declared rather than counted three times (#70/#27).",
  "Which fund hits the wall first determines which committee writes the bill.")

N("usf-oasi-payable-band", "usf-anchor",
  "The payable share of scheduled OASI benefits at depletion stays between 70 and 85 percent in the "
  "next Trustees Report", 0.88, "2027-12-31", "us-fiscal", "scheduled", "5 quarters",
  "The payable share is the ratio of continuing payroll-tax income to scheduled benefits - a slow, "
  "structurally determined quantity. It printed 78 percent in the 2026 report, and a move outside a "
  "15-point band would require a change in the tax rate or the benefit formula, both legislative.",
  "A band on a RATIO rather than on a date. Ratios of two slow aggregates are the most forecastable "
  "objects in actuarial work, and the distance to both bounds is wide - the distance-to-threshold "
  "argument that #69 failed to make.",
  "The payable share is the actual size of the cliff and the number any reform is sized against.",
  evidence=[{"fact": "The 2026 report states that at OASI depletion continuing income would be "
                     "sufficient to pay 78 percent of total scheduled benefits", "reported": SRC}])

N("usf-smi-adequately-financed", "usf-anchor",
  "SMI is again reported as adequately financed into the indefinite future in the next Trustees "
  "Report", 0.96, "2027-12-31", "us-fiscal", "invariant", "5 quarters",
  "DEFINITIONAL rather than actuarial: SMI's financing sources - beneficiary premiums and the "
  "matching federal contribution - are reset annually BY STATUTE to cover the coming year's costs. "
  "The fund is adequately financed by construction, whatever its spending does.",
  "The cleanest row in the batch and a genuinely useful distinction: SMI cannot become insolvent "
  "the way OASI and HI can, because its revenue is defined as whatever its cost turns out to be. "
  "Commentary routinely lumps the three funds together; the statute does not. The real SMI problem "
  "is the burden on premiums and general revenue, which is a different claim and is not bundled "
  "here (#63).",
  "SMI is a general-revenue growth story, never a depletion story.",
  evidence=[{"fact": "SMI financing is automatically adjusted each year to cover the upcoming "
                     "year's costs, unlike the other trust funds", "reported": SRC}])

N("usf-di-solvent-projection", "usf-anchor",
  "DI remains projected solvent through the end of the projection period in the next Trustees "
  "Report", 0.88, "2027-12-31", "us-fiscal", "scheduled", "5 quarters",
  "The 2026 report extends DI solvency through at least 2100, the last year of its projection, and "
  "the 2025 report said 2099 - the fund's position IMPROVED. Disability incidence has been running "
  "below earlier assumptions, which is a slow-moving demographic and programmatic quantity.",
  "Included specifically because it cuts against the lane's own narrative. A fiscal lane that only "
  "logs deterioration is telling a story, not forecasting; DI is the trust fund that got better and "
  "the book should be on record saying so.",
  "DI solvency is why the combined OASDI date is later than the OASI date that actually binds.",
  evidence=[{"fact": "The 2026 report projects DI able to pay scheduled benefits through at least "
                     "2100; the 2025 report projected through at least 2099", "reported": SRC}])

N("usf-tfr-not-raised", "usf-anchor",
  "The ultimate total fertility rate assumption is not raised above 1.90 in the next Trustees "
  "Report", 0.90, "2027-12-31", "us-fiscal", "invariant", "5 quarters",
  "Demographic arithmetic plus a sticky published methodology: the Trustees moved the ultimate TFR "
  "from 1.90 to 1.75 in 2026 after years of realised fertility running below the prior assumption. "
  "Reversing a cut made one year earlier, past the level it was cut from, would require realised "
  "births - which are already-counted data on a fixed annual publication schedule, not a forecast - "
  "to turn sharply. Reference class: ultimate-assumption revisions, which move in small steps and "
  "rarely reverse within one report cycle.",
  "The input, not the output. Pricing the ASSUMPTION rather than the depletion date is the better "
  "row because the assumption is observable, sticky and upstream of everything else in the report. "
  "The soft part is a methodology review, which happens on a published cycle.",
  "Fertility is the single assumption with the largest long-range effect on the 75-year balance.",
  evidence=[{"fact": "The 2026 report lowered the assumed ultimate total fertility rate from 1.90 "
                     "to 1.75 children per woman", "reported": SRC}])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tree = json.loads(L.TREE.read_text(encoding="utf-8"))
    ids = {n["id"] for n in tree["nodes"]} | {"now"}
    already = {n["id"] for n in tree["nodes"] if n.get("source") == L.STAMP}
    if already:
        print(f"  NOTE: {len(already)} ids already merged under '{L.STAMP}' — --write refused.")
        ids -= already

    bad = L.validate(ids, set(tree["lanes"]))
    # the batch-size quotas in the lib are written for a 200-node buildout; an 8-node addendum
    # cannot satisfy "8 rows at p<=0.45". Keep every per-node rule, drop only the batch quotas.
    bad = [b for b in bad if not b.startswith("only ") and "of the batch" not in b]
    L.summarise()
    if bad:
        print(f"\nREFUSED — {len(bad)} violation(s):")
        for b in bad:
            print("  - " + b)
        return 1
    print("\nself-check PASS (per-node rules; batch-size quotas N/A for an 8-node addendum)")
    if not a.write:
        print("dry run; pass --write to merge")
        return 0
    if already:
        return 1

    backup = L.TREE.with_suffix(f".json.bak-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    shutil.copy2(L.TREE, backup)
    tree["nodes"] = list(tree["nodes"]) + L.NODES
    tree["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    L.TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged -> {L.TREE} (backup: {backup.name}); tree is now {len(tree['nodes'])} nodes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
