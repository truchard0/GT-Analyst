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
