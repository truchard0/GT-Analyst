# Data request: ETH/PRIO Civil Conflict Ceasefire (CF) dataset

**To:** Dr Govinda Clayton, Center for Security Studies, ETH Zurich (named as the dataset contact on
<https://css.ethz.ch/en/research/datasets/civil-conflict-ceasefire.html>; look up the current
address there before sending)
**From:** [your name, affiliation, email]
**Status:** draft, not sent. Claude cannot send email from this session.

---

Subject: Request for access to the ETH/PRIO Civil Conflict Ceasefire dataset

Dear Dr Clayton,

I am writing to ask whether the ETH/PRIO Civil Conflict Ceasefire dataset (Clayton et al., *Journal of
Conflict Resolution* 67(7–8), 2023) could be shared for non-commercial research use.

I am building and evaluating a model of ceasefire durability. It is a survival model that predicts when
a ceasefire breaks down, scored walk-forward with no look-ahead, and it currently uses ceasefire-stage
agreements from PA-X v10 linked to UCDP GED. PA-X misses most unilateral and short-lived verbal
ceasefires. Those are exactly the cases where the timing question is hardest and where your data are
unique.

The fields I would use are:

- the ceasefire identifier, the UCDP conflict and dyad identifiers, and the actors;
- start and end dates, at the finest precision available, and how each ceasefire ended;
- class (unilateral, bilateral, multilateral), purpose and coverage, and whether it was written.

I would cite the 2023 article in any output and acknowledge the CSS, PRIO and Uppsala team. I would not
redistribute the data, and would keep them out of any public repository. If there is a data-use
agreement or a newer version beyond 2020, I would be glad to follow it.

Thank you for considering this.

Kind regards,
[your name]

---

## When the data arrive
1. Save the file as `data/ceasefire/raw/ethprio_cf.csv` (that folder is gitignored, so the data never
   reach the repository). Convert it to CSV first if it is a Stata or Excel file.
2. Fill `data/ceasefire/ethprio_columns.json` with the codebook's column names: id, conflict id, and
   either an ISO date column or year/month/day columns, plus the unilateral flag.
3. Rebuild and rerun the backtests:
   ```
   python tools/build_ceasefire_data.py
   python pipeline/ceasefire_engine.py backtest --target r25
   python pipeline/ceasefire_engine.py backtest-daily --tau 0.3
   ```
   Ceasefires on the same conflict within 3 days of a PA-X agreement merge with it automatically.

## Public alternative checked (2026-11-02)
- **What exists:** the authors' replication archive for Clayton & Sticher, "The Logic of Ceasefires in Civil War" (ISQ
  2021), is public under CC0 on Harvard Dataverse (doi:10.7910/DVN/YMCDBG). It holds a CF-based survival file
  (`ISQ_Replication_Data_CF.tab`, Stata 118).
- **Coverage:** 280 ceasefires in 68 conflicts. It has the type (preliminary, definitive, COH, unilateral, local),
  durations in days, and termination flags at several GED thresholds.
- **Limits:**
  - There are **no calendar dates**, so it cannot be joined to the day-level GED hazard.
  - It has only 13 unilateral and 28 local ceasefires, so the gap PA-X leaves stays open.
- **Use:** a duration reference class. Kaplan–Meier breakdown by 30/90/180 days:
  - all: 14% / 41% / 54%
  - COH: 16% / 49% / 65%
  - definitive: 3% / 14% / 19%
- **Where it is:** downloaded to `data/ceasefire/raw/ethprio_isq/` (gitignored).
- **Other public sources:** no copy of the full 2,202-ceasefire dataset was found on the ETH CSS page (it links only to
  the article), in PRIO's data catalogue, or in Harvard Dataverse searches. The email request above is still the way
  to get it.
