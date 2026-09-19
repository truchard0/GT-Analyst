#!/usr/bin/env python3
"""Idempotently seed the 8 Jiang calibration predictions (doctrine §12.9,
on-record April 21, 2026) with source='jiang-seed'. Safe to run repeatedly."""
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
from ledger import db

TS = "2026-04-21T00:00:00Z"

SEEDS = [
    ("GT#21: US-Iran conflict trajectory",
     "US-Iran war continues for years despite ceasefires/talks; no durable peace treaty",
     0.70, "2028-04-21",
     "Ratified peace treaty followed by 12 months without kinetic exchange",
     "assumes constitutive-conflict classification (doctrine 11.5)"),
    ("GT#21: conscription following automatic registration (registration dated Dec 2026)",
     "US introduces a national draft after automatic registration begins",
     0.50, "2027-06-30",
     "No draft legislation enacted by horizon",
     "precondition-tracking call (12.3); registration itself is the leading indicator"),
    ("GT#21: Pentagon budget trajectory",
     "Pentagon budget reaches ~$1.5T next fiscal year",
     0.55, "2027-01-31",
     "Enacted FY27 topline below $1.3T",
     "war-economy conversion index (10.10/12.5)"),
    ("GT#21: hemispheric retrenchment",
     "US never durably exits Iran conflict but is eventually forced back to hemisphere",
     0.40, "2036-04-21",
     "Sustained US forward presence in the Gulf through the 2030s",
     "unfalsifiable-horizon; empire failure triad (12.8) decade leg"),
    ("GT#21: Russian naval attrition challenge",
     "Russian naval attrition challenge at chokepoints, staging via Cuba",
     0.35, "2027-12-31",
     "No Russian naval staging in Cuba or chokepoint interdiction incidents by horizon",
     "audition-model / coalition-rules read (10.4/10.5)"),
    ("GT#21: bandwagoning against the hegemon",
     "Most nations bandwagon against the US over time (alliance exits, UN-vote realignment)",
     0.45, "2028-12-31",
     "US alliance network stable or growing (no major treaty-ally exits; UN voting alignment steady)",
     "soft falsifier; coalition dynamics (10.5)"),
    ("GT#21: third-term attempt / election manipulation",
     "Third-term attempt or overt election manipulation occurs",
     0.30, "2028-11-30",
     "2028 election proceeds with incumbent transition per constitutional norms",
     "partly-unfalsifiable as stated (flagged by doctrine itself)"),
    ("GT#21: strategy continuity across parties",
     "Democrats continue the chokepoint-control strategy if they win in 2028",
     0.60, "2029-06-30",
     "Winning Democratic administration reverses NDS posture within 6 months (conditional: resolve N/A if Democrats lose)",
     "opposition-theater / hidden-consensus prior (12.6)"),
]


def main():
    c = db()
    added = 0
    for event, prediction, prob, horizon, falsifier, sensitivity in SEEDS:
        if c.execute("SELECT 1 FROM predictions WHERE event=? AND source='jiang-seed'",
                     (event,)).fetchone():
            continue
        c.execute("""INSERT INTO predictions
            (ts,event,prediction,prob,horizon,falsifier,sensitivity,source)
            VALUES(?,?,?,?,?,?,?,'jiang-seed')""",
            (TS, event, prediction, prob, horizon, falsifier, sensitivity))
        added += 1
    c.commit()
    total = c.execute("SELECT COUNT(*) FROM predictions WHERE source='jiang-seed'").fetchone()[0]
    print(f"seeded {added} new; {total} jiang-seed rows total")


if __name__ == "__main__":
    main()
