# Hyperscaler capex, 5-year extension: collection notes (capex_hyperscalers.csv)

Gathered 18 Nov 2026 UTC for `PREREG_5Y.md` (V2 N3, quarterly capex: MSFT, GOOGL, AMZN, META).
Collection only; nothing here is scored or analysed.

## Window and row counts

Every quarterly earnings report published from 18 Nov 2020 up to, not including, the first report already in
`capex_history.csv`. Report dates are the filing dates of the Item 2.02 8-Ks in SEC EDGAR (submissions API).

| Ticker | Rows | First report | Last report | Next report (already in capex_history.csv) |
|---|---|---|---|---|
| MSFT | 16 | 2021-01-26 (FY21 Q2) | 2024-10-30 (FY25 Q1) | 2025-01-29 |
| GOOGL | 16 | 2021-02-02 (Q4 2020) | 2024-10-29 (Q3 2024) | 2025-02-04 |
| AMZN | 16 | 2021-02-02 (Q4 2020) | 2024-10-31 (Q3 2024) | 2025-02-06 |
| META | 16 | 2021-01-27 (Q4 2020) | 2024-10-30 (Q3 2024) | 2025-01-29 |

64 rows, no quarter missing. Rows are sorted by ticker, then report date. Columns and header are identical to
`capex_history.csv`. Units are USD billions.

Rows dated 18 Nov 2020 to 17 Nov 2021 are the warm-up years under the pre-registration (4 per company); the rest are in
the scored window.

## Quality counts

- primary: 58 (MSFT 16, GOOGL 16, META 16, AMZN 10)
- secondary: 6 (all AMZN: 2022-10-27, 2023-02-02, 2023-08-03, 2023-10-26, 2024-02-01, 2024-10-31)

Rule used: a row is primary when every NUMBER in it (reported_quarter_capex and any guide cell) was read on a primary
source (the company's release, 10-Q/10-K, SEC XBRL companyfacts, or the company's own transcript). The six AMZN rows
are secondary because their annual guide numbers come only from Motley Fool transcripts (Amazon publishes no
transcript and puts no capex outlook in its releases). Where a row's TEXT columns quote a third-party transcript but
all its numbers are primary, the row stays primary and the note says so (all 16 AMZN rows and the five GOOGL rows
from 2021-02-02 to 2022-02-01). Under a stricter rule (any third-party text makes a row secondary) the count would be
43 primary / 21 secondary.

## How each company was sourced

**MSFT.** `reported_quarter_capex` = "capital expenditures including finance leases" as spoken by the CFO, read in
Microsoft's own Word transcripts (cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/TranscriptFY21Q2 and so on,
the targets of the aka.ms/transcriptfy..q.. links). All 16 calls state the figure in the old wording ("Capital
expenditures including finance leases were $X billion"), so the definition is the same as the existing MSFT rows and
no row is left blank. Cash paid for PP&E (10-Q three-month column via SEC XBRL; Q4 figures as fiscal year less nine
months) is in the note for reference only. Several figures are spoken only to the nearest billion (6, 14, 19, 20).
Microsoft gave no numeric annual capex figure in this period; all guide cells are blank and the statements are in
the text columns. guide_year is the fiscal year of the reported quarter.

**GOOGL.** Purchases of property and equipment, three months, from the cash flow statement in the release
(SEC 8-K Exhibit 99.1), each checked against XBRL year-to-date arithmetic (all 16 match). Text: Alphabet's own
transcript PDFs (s206.q4cdn.com) for the 11 calls from Q1 2022 on; Motley Fool transcripts for the Q3 2020 to Q3 2021
calls, because Alphabet's older PDFs (abc.xyz) are behind a bot challenge. Alphabet gave no numeric annual capex figure
in this period (only words such as "sizable increase", "generally in line with 2022", "notably larger"); all guide
cells are blank.

**AMZN.** Purchases of property and equipment, GROSS, three months, from the release cash flow statement, with the
year-to-date subtraction shown in each note (prior year-to-date from the same filing) and checked against SEC XBRL
`PaymentsToAcquireProductiveAssets` (all match; Q4 2020 has a 1 million rounding difference: 40,140 less 25,317 =
14,823 against the release's 14,824, release figure used). Text and the guide numbers: Motley Fool transcripts.

**META.** Capital expenditures including principal payments on finance leases, as stated in each release, with a
cash-flow check in the note (purchases of property and equipment, net, plus principal payments on finance leases from
the release's three-month columns; all 16 agree to within rounding). Guides are the release outlook sentences.
Meta gives no next-quarter figure, so that column is blank for all META rows.

## Definitional breaks and judgment calls

1. **AMZN guide basis differs from the capex column (same issue as in capex_history.csv).** Through Q3 2024 Amazon
   talked and guided on "capital investments" = capex plus equipment finance leases (31 Oct 2024: "cash capex plus
   equipment finance leases"), not gross purchases of property and equipment. The guide numbers (60 for 2022, 50 for
   2023, 75 for 2024) are on that basis. Stated year-end actuals on that basis: 2022 "$59 billion" (vs gross 63.645),
   2023 "$48.4 billion" (vs gross 52.729).
2. **AMZN "slightly more than $50 billion" (3 Aug 2023)** is entered as a floor: new_guide_low 50, high and mid blank;
   it is the prior guide of the next row the same way (prior_guide_low only), following the Oracle "over $25 billion"
   treatment in capex_history.csv.
3. **Directional statements are not entered as numbers.** E.g. AMZN 27 Apr 2023 "lower than our $59 billion investment
   level in 2022", AMZN 28 Jul 2022 "slightly more ... than last year", GOOGL 2 Feb 2023 "generally in line with 2022",
   GOOGL 25 Apr 2024 "quarterly CapEx ... roughly at or above the Q1 level" (implied 48+ is arithmetic only).
4. **Q4 rows follow capex_history.csv:** guide_year is the year just completed, prior guide = last guide for that
   year, new guide blank; the first next-year guide is quoted in new_text and carried as the prior guide of the next
   row. Where the next-year guide CHANGED at the Q4 report, the change is only in the text, so a scorer that reads only
   the number columns will not see it:
   - META 2023-02-01: CY2023 cut from 34-37 to 30-33.
   - META 2024-02-01: CY2024 raised from 30-35 to 30-37.
   - META 2021-01-27 and 2022-02-02: next-year guide reaffirmed (21-23; 29-34).
5. **META between-report change.** On 9 Nov 2022 (8-K Exhibit 99.1, layoff announcement) Meta narrowed CY2023 from
   34-39 to 34-37. Recorded in the note of the 2023-02-01 row; no row exists for it because it was not an earnings
   report. Meta's 14 Mar 2023 8-K (Year of Efficiency) was checked and has no capex figure.
6. **META capex basis.** From 2022 Meta's cash flow shows gross purchases and proceeds separately; the release
   capex figure uses purchases net of proceeds plus finance lease principal. Earlier-year figures were also net (the
   2021 numbers were later restated as gross plus separate proceeds). Release figures used throughout.
7. **MSFT accounting change.** From FY2023 server and network useful lives went from four to six years (noted in the
   FY2022 Q4 row). This changes depreciation, not capex.
8. **GOOGL release column order.** Alphabet's release lists the prior-year quarter first; the current quarter is the
   second column (e.g. Q4 2020 = 5,479, not 6,052). Every GOOGL figure was checked against XBRL year-to-date
   differences.

## Gaps

- **GOOGL 1 Feb 2022 call (Q4 2021 row, new_text; and Q1 2022 row, prior_text):** not read. Alphabet's PDF was
  blocked, the Motley Fool page was not found under any address tried, and other hosts were paywalled. The next call
  refers back to "a meaningful increase in Capex in 2022"; the February wording is unverified. No numeric 2022 guide is
  known to exist.
- **Quotes from PDF text extraction (GOOGL 2022-2024):** letter-spacing artefacts ("W e", "a bove") and page numbers
  inside sentences were removed by hand; otherwise verbatim.
- **AMZN 2 Feb 2023 call:** the transcript contains no capex outlook (searched for capex, capital investments,
  infrastructure); recorded as such, not as a gap.
- **Statements between reports** (conferences, investor days) were not searched systematically, except Meta's 8-Ks.
- No cell was estimated. Derived values are only the year-to-date subtractions (AMZN, GOOGL, MSFT cash PP&E) and the
  META cash-flow checks, each with its arithmetic in the note.
