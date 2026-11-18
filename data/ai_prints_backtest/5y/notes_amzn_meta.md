# AMZN and META, 5-year extension: collection notes (prints_amzn_meta.csv, consensus_amzn_meta.csv)

Gathered 18 Nov 2026 UTC under `PREREG_5Y.md`. Collection only; nothing here is scored or analysed.

## Window and coverage

Reports published from 18 Nov 2020 up to, not including, the first report already in `prints_history_b.csv`
(AMZN 31 Jul 2025, META 30 Jul 2025).

| Ticker | First row | Last row | Rows |
|---|---|---|---|
| AMZN | Q4 2020 (2 Feb 2021) | Q1 2025 (1 May 2025) | 18 |
| META | Q4 2020 (27 Jan 2021) | Q1 2025 (30 Apr 2025) | 18 |

18 per company, not 19: Q4 2020 to Q1 2025 is 18 quarterly reports. The Q3 2020 reports (29 Oct 2020) are before
the window and were used only as the source of the Q4 2020 guide. No report in the window is missing; every Item 2.02
8-K for both companies between those dates is a row.

## How the prints were sourced

- **Report list:** SEC EDGAR submissions JSON (data.sec.gov) for CIK 1018724 (Amazon) and 1326801 (Meta), filtered to
  8-Ks carrying Item 2.02. `report_date` is the 8-K filing date. Timing is from the SEC acceptance time: every 8-K was
  accepted 20:06-21:47 UTC, which is 16:06-16:47 New York time in both summer and winter, so all 36 rows are AMC.
- **Guides and actuals:** each Exhibit 99.1 press release was downloaded directly from the SEC Archives (raw HTML, not
  a summarising fetch tool) and parsed locally. Guides were taken from the release text (Amazon "Net sales are
  expected to be between $X billion and $Y billion"; Meta CFO Outlook "total revenue to be in the range of $X-Y
  billion"). Actuals were taken from the income-statement table to the million (Amazon "Total net sales", Meta
  "Revenue"), not from the rounded headline.
- **XBRL check:** every actual was checked against SEC companyfacts (`RevenueFromContractWithCustomerExcludingAssessedTax`).
  Q1-Q3 match quarterly frames exactly. Q4 values have no quarterly frame and were checked as full year less nine
  months: all four Amazon Q4s match exactly; Meta Q4 2020, Q4 2023 and Q4 2024 differ by 1m (28071 vs 28072, 40112 vs
  40111, 48386 vs 48385), the same rounding seen in the existing Meta rows. The release figure is used.
- **Links to the existing file:** the Q1 2025 rows' next guides (AMZN 159-164, META 42.5-45.5) equal the guides already
  in the Q2 2025 rows of `prints_history_b.csv`, and AMZN Q1 2025 actual 155667m equals the restated figure noted there.
- **Prior-year columns:** the prior-year quarter printed in each release equals the figure first reported a year
  earlier in every case checked, so no restatement affects these rows.

## Quality counts

prints_amzn_meta.csv: 36 primary, 0 secondary. Every figure was read on the company's own 8-K Exhibit 99.1.

consensus_amzn_meta.csv: 36 rows, all secondary (press coverage, as the rules require). 36 have a quarter consensus;
28 have a next-quarter consensus (AMZN 15, META 13).

## Gaps (cells left blank on purpose)

**Meta revenue guides, 4 quarters.** Meta gave no numeric revenue guide from the Q3 2020 release through the Q2 2021
release; it gave only qualitative growth outlooks ("stable or modestly accelerate", "decelerate significantly"). So:
- META Q4 2020, Q1 2021, Q2 2021: guide and next guide blank.
- META Q3 2021: guide blank; next guide present (31.5-34, the first numeric range in the window).
Scored models that need a guide have 14 META rows with a guide (Q4 2021 onward), and 15 with a next guide.

**Next-quarter consensus left blank, 8 rows**, because the only figure I could read did not name a provider:
| Row | Figure stated without provider | Other figure seen but not readable |
|---|---|---|
| AMZN Q4 2020 | 95.8 (CNBC) | Bloomberg 95.72, search summary only (BNN Bloomberg page did not resolve) |
| AMZN Q1 2021 | 108.6 (CNBC) | none |
| AMZN Q2 2021 | 119.2 (CNBC) | Reuters copy, 118.90 'IBES data from Refinitiv', search summary only (page returned 403) |
| META Q4 2020, Q1 2021 | none (no numeric guide; no next-q estimate printed) | none |
| META Q3 2021 | 34.8 (CNBC) | none |
| META Q4 2023 | 33.8 (CNBC) | TheFly 33.83, provider not named, search summary only |
| META Q1 2025 | 44.03 (CNBC) | Variety-based 43.81, provider not named, search summary only |

## Conflicts and judgment calls

- **Mixed providers in one row (2 rows).** AMZN Q3 2021 quarter consensus is Refinitiv but the only sourced next-q is
  FactSet (142.1); META Q1 2024 quarter is LSEG, next-q FactSet (38.254, CNBC Investing Club). `consensus_source_name`
  says so ("Refinitiv; next-q FactSet", "LSEG; next-q FactSet"). Anyone scoring a single-provider B1 should drop or
  split these next-q cells.
- **Refinitiv vs LSEG.** Same provider renamed in 2023 (CNBC: "LSEG, formerly known as Refinitiv"). Rows are labelled
  by the name the article used for the quarter line; AMZN Q4 2023 uses LSEG for the quarter and "Refinitiv" for next-q.
- **Next-q from a second outlet (4 rows).** Where CNBC printed a next-q number without a provider and a same-morning
  wire report named one, the wire figure was used: META Q3 2022 (RTE, 32.2 Refinitiv; same as CNBC), META Q2 2024
  (RTE, 39.1 LSEG; same as CNBC), META Q3 2024 (Reuters on ThePrint, 46.31 LSEG; CNBC 46.3), META Q4 2024 (Reuters on
  ThePrint, 41.72 LSEG; CNBC 41.73, a 0.01 conflict). The two ThePrint pages refused direct download and were read
  through a fetch tool that returns extracted passages.
- **AMZN Q3 2022 next-q 155.15 (Refinitiv).** Recorded as printed by CNBC. It is far above the 140-148 guide; it
  implies 13% growth on Q4 2021 and looks like a pre-guide consensus, which is what the column means, but it is the
  largest guide-vs-consensus gap in the file and worth a second look before scoring.
- **AMZN Q4 2021 next-q 120.** CNBC printed it rounded to the billion ("$120 billion").
- **META Q1 2023 quarter consensus.** CNBC results article 27.65; a search summary attributes 27.66 to another CNBC
  piece (not opened). Used 27.65.
- **META Q1 2024 quarter consensus.** CNBC 36.16; CNBC Investing Club 36.156 (both LSEG). Used 36.16, the results-day
  article figure.
- **META Q4 2023 CNBC URL** reads `meta-earnings-q4-2024.html` but the article is the Q4 2023 report (published 1 Feb
  2024).

## How the consensus was sourced

CNBC results-day articles (one per report, all published on the report date, located by web search and downloaded
directly). Every quarter figure is from the article's key-numbers list; where the list itself does not name the
provider, the sentence introducing it does ("relative to analyst estimates compiled by Refinitiv", "compared with
estimates from analysts polled by LSEG"), and the note quotes it. Next-quarter figures were taken only when the same
sentence named a provider. Quotes in the CSV notes are copied from the downloaded pages, except the two ThePrint
quotes, which came through a fetch tool and may differ in punctuation.

No cell in either file was estimated, filled from memory, or derived, except `guide_mid` / `next_guide_mid`, which
are the arithmetic midpoints of the stated ranges.
