# prints_mu_tsm.csv and consensus_mu_tsm.csv: collection notes

Gathered 18 Nov 2026 UTC under `data/ai_prints_backtest/PREREG_5Y.md`. Data only; nothing here is scored or analysed.

## What is in the files

`prints_mu_tsm.csv`: 36 rows, one per quarterly report published from 18 Nov 2020 up to (not including) the first
report already on file in `prints_history_a.csv` (MU 2025-06-25, TSM 2025-07-17). Header copied exactly from
`prints_history_a.csv`.

| Ticker | Rows | First report | Last report | Warm-up rows (published before 18 Nov 2021) |
|---|---|---|---|---|
| MU | 18 | 2021-01-07 (Q1 FY2021) | 2025-03-20 (Q2 FY2025) | 4 (2021-01-07, 03-31, 06-30, 09-28) |
| TSM | 18 | 2021-01-14 (4Q20) | 2025-04-17 (1Q25) | 4 (2021-01-14, 04-15, 07-15, 10-14) |

Quality: 36 primary, 0 secondary. No guide, actual or next-guide cell is blank.

`consensus_mu_tsm.csv`: 26 rows (MU 18, TSM 8), all secondary. Header copied exactly from `consensus.csv`.

## How the prints were sourced

- Report list from the EDGAR submissions index (data.sec.gov): every Micron 8-K with Item 2.02, and every TSMC 6-K
  that carries the quarterly earnings release. Report dates are EDGAR filing dates.
- Guides and actuals were read on the company's own release as furnished to the SEC: Micron Exhibit 99.1 to the
  Item 2.02 8-K; TSMC Exhibit 99.1 to the earnings 6-K. `source_guide` is the PREVIOUS report's release (where the
  guide was given); `source_actual` is that quarter's own release (which also carries the next guide). The guides for
  the first row of each company came from reports before the window: Micron 2020-09-29 (5.2 plus or minus 0.2) and
  TSMC 2020-10-15 (12.4 to 12.7).
- Timing from the EDGAR acceptance time converted to US Eastern time (quoted in each note). All 18 Micron reports were
  accepted at 16:00 or 16:01 ET (AMC). All 18 TSMC reports were accepted between 06:01 and 07:25 ET (BMO; released in
  the Taiwan afternoon).
- Micron guides are "$X billion plus or minus $Y million", converted arithmetically; GAAP and non-GAAP revenue guides
  were identical in every release. The band was plus or minus $200 million except Q4 FY2022 (plus or minus $400
  million, given 2022-06-30) and Q1 FY2023 (plus or minus $250 million, given 2022-09-29).
- TSMC guides are "between US$X billion and US$Y billion". Actual is the US dollar figure TSMC states in the release
  text ("In US dollars, ... revenue was $X billion"), not a conversion of mine. Each TSM note also gives the NT dollar
  revenue and the exchange-rate assumption behind the next guide, both from the same release.
- Fiscal-quarter end dates for Micron are from SEC XBRL period ends; TSMC quarters are calendar quarters.

## Cross-checks done

- **Micron actual vs SEC XBRL (companyfacts, RevenueFromContractWithCustomerExcludingAssessedTax):** all 18 match. The
  14 non-Q4 quarters match a stand-alone quarterly fact. The 4 fiscal Q4s have no stand-alone fact, so full year less
  nine months was used: FY2021 27,705 - 19,431 = 8,274; FY2022 30,758 - 24,115 = 6,643; FY2023 15,540 - 11,530 = 4,010;
  FY2024 25,111 - 17,361 = 7,750. All equal the release.
- **Micron actual vs next release's prior-quarter column:** the 17 rows whose next release is in this set all agree;
  the last row (Q2 FY2025, 8.053) is restated by the 2025-06-25 release already on file, not re-read here, and matches
  XBRL.
- **TSMC actual vs the quarter-on-quarter change stated in the release:** all 18 reconcile to the previous quarter's
  stated figure. Two differ by 0.1 point because of two-decimal rounding: 4Q23 (stated +13.6%, 19.62/17.28 = +13.5%)
  and 1Q25 (stated -5.1%, 25.53/26.88 = -5.0%). TSMC files no XBRL revenue in US dollars, so there is no XBRL check.
- **Guide chain:** every row's next guide equals the following row's guide. The last rows chain into the existing
  file: MU next guide 8.6 to 9.0 equals the 2025-06-25 row's guide; TSM next guide 28.4 to 29.2 equals the 2025-07-17
  row's guide.

## Mid-quarter guidance changes (Micron; read every non-2.02 8-K in the window)

Rows keep the guide given at the previous report, as instructed; the update is in the row note.

| Quarter | Date | What was filed |
|---|---|---|
| Q1 FY2021 | 2020-12-01 | Raised to 5.70 to 5.75 (from 5.0 to 5.4). Actual 5.773. |
| Q2 FY2021 | 2021-03-03 | Raised to 6.20 to 6.25 (from 5.6 to 6.0). Actual 6.236. |
| Q2 FY2022 | 2022-01-10 | Reaffirmed unchanged (Xi'an lockdown note). |
| Q4 FY2022 | 2022-08-09 | Qualitative: revenue "may come in at or below the low end" of the range. No new range. Actual 6.643, below the 6.8 low. |
| Q1 FY2024 | 2023-11-28 | Revenue "will approach $4.7 billion" (no range; from 4.2 to 4.6). Actual 4.726. |

Other Item 7.01 8-Ks (CAC decision 2023-05-22 and 2023-06-16, Taiwan earthquake 2024-04-11, CHIPS applications,
buyback, 3D XPoint exit) contained no revenue range change; the CAC and earthquake ones are noted on their rows.
TSMC gave no mid-quarter guide changes; it publishes monthly NT dollar revenue (about the 10th of each month), so the
quarter's NT dollar total is public about a week before each report. This check covers SEC filings only; remarks at
conferences that were not filed would not show up.

## How the consensus was sourced

- Candidate articles found by scanning CNBC's daily site maps for the report day and the day after, plus web searches
  for the Reuters results story; each figure below was read on a page I opened (Reuters copies were read on
  syndication sites: KFGO, WDEZ, WHTC, WSAU, Jack 106.5, The Star, ThePrint, Fiji Times, Yahoo, DataFloq, Euronews,
  MarketScreener). Figures seen only in search summaries are in the notes and are not used as values.
- **Micron (18 rows):** provider Refinitiv (2021 to mid-2023) or LSEG (late 2023 on). Next-quarter value present on
  all 18.
  - Quarter value blank (not found with a named provider) on 3 rows: Q4 FY2021 (2021-09-28), Q2 FY2022 (2022-03-29),
    Q3 FY2022 (2022-06-30). These rows carry the next-quarter value only.
  - 2 rows use a Bloomberg News figure for the quarter, where Bloomberg names no provider and no LSEG figure was found:
    Q1 FY2024 (2023-12-20, 4.54) and Q4 FY2024 (2024-09-25, 7.66). Their next-quarter values are LSEG. Marked "MIXED
    PROVIDERS" in the note; drop them if only LSEG/Refinitiv quarter values are wanted.
  - On several rows the provider is named on one figure and the other figure sits in the same article without its own
    attribution (2022-09-29 quarter, 2022-12-21 next-q, 2023-09-27 quarter, 2024-06-26 next-q); each is flagged.
  - 2021-06-30 figures are from a CNBC article published the day after the report.
  - Rounded values as printed: 2024-06-26 next-q 7.6 and 2025-03-20 next-q 8.5.
- **TSMC (8 rows):** CNBC states TSMC's revenue consensus only in NT DOLLARS (Refinitiv/LSEG), so these 8 rows are in
  `TWD bn`, not US dollars; the TSMC NT dollar actual is given in each note for a like-for-like comparison. No US
  dollar revenue consensus and no next-quarter consensus was found for any TSMC report in 2021-2025.
  - Rows: 2Q22, 2Q23, 3Q23, 4Q23, 1Q24, 2Q24, 4Q24, 1Q25.
  - Left out (no revenue estimate with a named provider found; coverage gives only net-profit consensus or nothing):
    4Q20, 1Q21, 2Q21, 3Q21, 4Q21, 1Q22, 3Q22, 4Q22, 1Q23, 3Q24 (10 reports).
  - Because the NT dollar quarter is public from the monthly revenue reports before the results, these consensus
    figures are close to known numbers and are not a clean pre-report expectation.

## Conflicts and judgment calls

1. **TSMC 4Q24 dollar figure:** CNBC converted NT$868.46 billion to $26.36 billion; TSMC states $26.88 billion. The
   CSV uses TSMC's 26.88.
2. **TSMC 4Q23 exhibit file name:** the 2024-01-18 exhibit is named `a4q24e_withguidancexfinal.htm` but its text is
   the fourth-quarter 2023 release (19.62 actual, 1Q24 guide 18.0 to 18.8). Used as is.
3. **Micron Q3 FY2022 next-q consensus:** Reuters/Refinitiv 9.05 used; Bloomberg 9.14 seen in a search summary only.
4. **Micron Q1 FY2021 next-q consensus:** Reuters/Refinitiv IBES 5.50 used; other outlets' 5.66 and 5.52 (provider not
   named, search summaries only) not used.
5. **Micron Q2 FY2022 Reuters copy (DataFloq) is undated on the page;** it is placed on 2022-03-29 because its 8.7
   guide and "on Tuesday" match only that report.

## Gaps

- Prints: none. All 36 reports and all guides, actuals and next guides were read on primary documents.
- Consensus: 10 TSMC reports have no row; 3 Micron rows lack the quarter value; 8 TSMC rows are NT dollar only with no
  next-quarter value.
