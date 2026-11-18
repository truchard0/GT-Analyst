# prints_nvda_avgo.csv and consensus_nvda_avgo.csv: collection notes

Gathered 18 Nov 2026 UTC under `data/ai_prints_backtest/PREREG_5Y.md`. Data only; nothing here is scored or analysed.

## What is in the files

**prints_nvda_avgo.csv**: 36 rows, one per quarterly report published from 18 Nov 2020 up to (not including) the first
report already in `prints_history_a.csv` (NVDA 2025-05-28, AVGO 2025-06-05).

| Ticker | Rows | First report | Last report | Quality |
|---|---|---|---|---|
| NVDA | 18 | 2020-11-18 (Q3 FY2021) | 2025-02-26 (Q4 FY2025) | 18 primary |
| AVGO | 18 | 2020-12-10 (Q4 FY2020) | 2025-03-06 (Q1 FY2025) | 18 primary |

36 primary, 0 secondary. Rows dated 18 Nov 2020 to 17 Nov 2021 are the warm-up years under the pre-registration
(NVDA 5 rows, the last being 2021-11-17; AVGO 4 rows); the rest fall in the scored window.

**consensus_nvda_avgo.csv**: 34 rows (NVDA 18, AVGO 16), all `secondary` (press coverage). 28 of them also carry a
next-quarter consensus.

## How it was sourced

- **Report list**: from each company's EDGAR submissions JSON (data.sec.gov), every Form 8-K with Item 2.02 in the
  window. Report dates are 8-K filing dates. NVDA has one extra Item 2.02 8-K (2022-08-08, a pre-announcement, not a
  quarterly report, so not a row).
- **Guides and actuals**: read on Exhibit 99.1 of each Item 2.02 8-K, downloaded from SEC EDGAR. `source_guide` is
  the previous quarter's release (where the guide was given); `source_actual` is the quarter's own release, which
  also carries the next-quarter guide. The two releases that only supply the first guide (NVDA 2020-08-19, AVGO
  2020-09-03) are outside the window and are not rows.
- **Actuals** are the income-statement revenue to the precision printed (USD millions, so three decimals in
  billions).
- **Conversions**: Nvidia "$X billion, plus or minus 2%" (2020-2021 releases write "2 percent") converted
  arithmetically to low and high. Broadcom "approximately $X billion" used for low, high and mid, except the guide for
  Q4 FY2020 (given 2020-09-03), which was "$6.4 billion plus or minus $150 million" (6.25 to 6.55).
- **Timing**: EDGAR acceptance time converted to US Eastern. 35 of 36 were accepted between 16:16 and 17:18 ET (AMC).
  One is BMO: AVGO 2022-05-26, accepted 07:28 ET, released before the open with the VMware acquisition announcement.

## Cross-checks done

- Every actual was checked against SEC XBRL (data.sec.gov companyfacts). The 10-Q quarters match a stand-alone
  quarterly XBRL value exactly. Fourth quarters have no stand-alone XBRL quarter in most years, so each was checked as
  the 10-K full-year value less the nine-month value. All matched, with no discrepancy:
  NVDA 5,003 / 7,643 / 6,051 / 22,103 / 39,331; AVGO 7,407 / 8,930 / 9,295 / 14,054 (AVGO Q4 FY2020 6,467 has a
  quarterly XBRL value in the 10-K).
- Each actual was also visible in the next release's prior-quarter or prior-year column where read (for example AVGO
  Q2 FY2022 8,103 in the 2022-09-01 release).

## Gaps (blank cells), all deliberate

Prints file, no figure is missing that a release states. Blanks are where Broadcom gave no quarterly guide:

1. **AVGO 2023-12-07 (Q4 FY2023)**: `next_guide` blank. The release gave only a fiscal 2024 annual revenue guide of
   about $50.0 billion including VMware.
2. **AVGO 2024-03-07 (Q1 FY2024)**: `guide` and `next_guide` blank. Annual guide only (about $50.0 billion, unchanged).
3. **AVGO 2024-06-12 (Q2 FY2024)**: `guide` and `next_guide` blank. Annual guide raised to about $51.0 billion, no
   quarterly guide.
4. **AVGO 2024-09-05 (Q3 FY2024)**: `guide` blank. Quarterly guidance resumes in this release (Q4 FY2024 about $14.0
   billion).

Consensus file:

1. **AVGO Q4 FY2020 (2020-12-10): not sourced, no row.** The CNBC after-hours roundup says revenue "came in ahead of
   estimates" without a figure. A search summary attributed 6.43 (quarter) and 6.52 (next quarter, "IBES data from
   Refinitiv") to a Reuters story, but its only copy found (metro.us) would not open.
2. **AVGO Q1 FY2021 (2021-03-04): not sourced, no row.** Only Benzinga figures (6.61 and 6.33, provider not named)
   appeared, in search summaries.
3. **Next-quarter consensus blank**: NVDA Q1 FY2022 and Q3 FY2024 (articles give none); AVGO Q2 FY2022 (CNBC says
   only "just over $8 billion" per Refinitiv); AVGO Q4 FY2023, Q1 FY2024, Q2 FY2024 (no quarterly guide, no
   quarterly next-q consensus).

## Pre-announcements and mid-quarter updates

I read every Item 2.02 and Item 7.01 8-K both companies filed in the window. Item 8.01 8-Ks (debt offerings, deal
items) were listed but not read for guidance.

- **NVDA 2022-08-08 (Item 2.02, formal pre-announcement)**: preliminary Q2 FY2023 revenue of about $6.70 billion
  against the $8.10 billion outlook (Gaming shortfall, about $1.32 billion of charges). The 2022-08-24 row keeps the
  $8.10 billion guide given at the previous report, as instructed, and says so in its note. Actual 6.704.
- **NVDA 2021-04-12 (Item 7.01, Investor Day)**: Q1 FY2022 revenue "tracking above" the $5.30 billion outlook, no new
  figure; CMP estimate raised to $150 million from $50 million. Noted on the 2021-05-26 row; guide unchanged.
- **NVDA 2021-06-28 (Item 7.01)**: tax-rate outlook change only, no revenue effect.
- **AVGO 2022-05-26 and 2023-05-23 (Item 7.01)**: the VMware deal announcement and an Apple supply agreement; no
  guidance change.
- This covers SEC filings only; remarks at conferences that were not filed would not show up.

## Breaks in the series a user should know

1. **AVGO from Q1 FY2024 includes VMware** (the 2024-03-07 release: revenue up 34% including VMware, 11% excluding).
2. **14-week quarters**, from XBRL period dates (neither release mentions it): NVDA Q4 FY2021 (2020-10-26 to
   2021-01-31; fiscal 2021 ran 370 days) and AVGO Q1 FY2024 (2023-10-30 to 2024-02-04; fiscal 2024 ran 53 weeks).
3. **NVDA Q2 FY2023 next guide** and **Q1 FY2023 next guide** carry qualifiers in the release (channel inventory
   reduction; an estimated $500 million reduction for Russia and China lockdowns). Both are noted on the rows.

## Consensus: sources, conflicts and judgment calls

- Results-day CNBC articles (provider named in the article's comparison block) for all 18 NVDA rows and five AVGO
  rows; Reuters copies syndicated by Euronews, Yahoo Finance, The Star, ThePrint and US radio-station sites for most
  AVGO rows. Some CNBC articles were read as republished by NBC station sites (Money Report) when the cnbc.com URL
  could not be found: NVDA Q1 FY2025, AVGO Q2 FY2024, Q4 FY2024, Q1 FY2025.
- Provider labels: Refinitiv until mid-2023, then LSEG (the same estimates product, renamed).
- **Provider not named on the exact line** (named elsewhere in the same article or comparison block): NVDA next-q for
  Q4 FY2021, Q3 FY2022, Q4 FY2022, Q1 FY2023, Q4 FY2023, Q1 FY2024; AVGO quarter figures for Q3 FY2021, Q4 FY2021,
  Q1 FY2022, Q4 FY2022, Q2 FY2023, Q4 FY2024. Each is flagged in the row's note.
- **Different provider for the next quarter**: NVDA Q2 FY2025 next-q is StreetAccount (31.7), quarter LSEG; AVGO Q2
  FY2021 next-q is Bloomberg (6.59), quarter Refinitiv. Flagged in `consensus_source_name`.
- **Stale consensus**: NVDA Q2 FY2023 quarter consensus 8.10 equals the original guide. CNBC says Refinitiv estimates
  did not change after the 2022-08-08 pre-announcement, so it predates the warning.
- **Conflicts**: NVDA Q1 FY2025 next-q 26.61 (CNBC, LSEG) vs 26.66 (Reuters, LSEG), CNBC used. AVGO Q4 FY2023 quarter
  9.41 (CNBC Investing Club, LSEG) vs 9.28 attributed to FactSet and Investing.com in search summaries only; under
  9.41 the quarter is a miss, under 9.28 a beat. AVGO Q1 FY2024: the Reuters copy calls 11.96 "below" the 11.72 LSEG
  estimate (wording error); the CNBC roundup says "higher than".
- **Next-quarter estimate below the quarter's own estimate, as printed**: NVDA Q4 FY2021 (4.51 vs 4.82), NVDA Q4
  FY2022 (7.29 vs 7.42), AVGO Q1 FY2022 (7.43 vs 7.60). Recorded as printed; possibly different bases or vintages.
- **Rounded figures**: AVGO Q2 FY2022 quarter 7.9 and NVDA Q2 FY2022 next-q 6.5, as printed.
- **Not same-day**: AVGO Q1 FY2023 quarter figure is from CNBC's premarket roundup the next morning (2023-03-03); the
  next-q figure is the results-day Reuters copy. The AVGO Q3 FY2021 Euronews copy of the Reuters story was posted the
  next morning (Europe time).
