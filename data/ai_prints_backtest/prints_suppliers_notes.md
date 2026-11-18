# prints_suppliers.csv: collection notes

Gathered 18 Nov 2026. Data only; nothing here is scored or analysed.

## What is in the file

23 rows, one per quarterly report published 18 May 2026 to 17 Nov 2026 inclusive.

| Ticker | Reports in window | Dates |
|---|---|---|
| NVDA | 3 | 2026-05-20, 2026-08-26, 2026-11-17 |
| AVGO | 2 | 2026-06-03, 2026-09-02 |
| MU | 2 | 2026-06-24, 2026-09-30 |
| TSM | 2 | 2026-07-16, 2026-10-15 |
| AMD | 2 | 2026-08-04, 2026-11-03 |
| MRVL | 2 | 2026-05-27, 2026-08-27 |
| ASML | 2 | 2026-07-15, 2026-10-14 |
| AMAT | 2 | 2026-08-13, 2026-11-12 |
| LRCX | 2 | 2026-07-29, 2026-10-21 |
| KLAC | 2 | 2026-07-28, 2026-10-28 |
| DELL | 2 | 2026-05-28, 2026-09-01 |

## How it was sourced

- Every guide and every actual was read on the company's own earnings release as furnished to the SEC (EDGAR):
  Exhibit 99.1 of the Item 2.02 Form 8-K for the nine US filers, and the Form 6-K earnings release for TSMC and ASML.
  All 23 rows are tagged `primary`.
- The list of reports came from each company's EDGAR filing index (every 8-K with Item 2.02, and the quarterly 6-Ks),
  so the report dates are filing dates, not dates taken from a calendar site.
- `source_guide` is the PREVIOUS quarter's release (where the guide was given); `source_actual` is that quarter's own
  release (which also carries the next-quarter guide).
- Timing comes from the EDGAR acceptance time, converted to US Eastern time and quoted in each row's note. All nine US
  filers were accepted between 16:02 and 16:26 ET (AMC). TSMC and ASML were accepted between 06:01 and 07:45 ET (BMO).
- Actuals are taken from the income statement in the release, to the precision the company prints (for example
  81.615, not the headline 81.6). TSMC is the US dollar figure TSMC states in the release text.
- Conversions: "X plus or minus Y%" and "X +/- $Y" guides were converted to low and high arithmetically. Broadcom gives
  a single "approximately X" figure, used for low, high and mid.

## Cross-checks done

- Each actual was checked against the next report's prior-quarter column where a next report exists, and against the
  10-Q or 10-K XBRL revenue value where one is filed. All agreed, with no discrepancy.
- Latest quarters with no later report yet: NVDA Q3 FY2027, AMAT Q4 FY2026, TSM 3Q26, ASML Q3 2026. These were
  checked inside their own filing instead (NVDA: nine-month total less six-month total = 115,844; AMAT: fiscal-year
  total less nine-month total = 10,409; TSM: release text and management deck both show 46.72; ASML: release table and
  US GAAP statements both show 11,662).
- MU FQ4 2026 has no stand-alone quarter in the 10-K XBRL; the 10-K full-year 133,188 less the nine-month 78,959 gives
  54,229, matching the release.

## Reports not found or not verified

None. All 23 reports and all guides were found on primary documents.

## Conflicts and judgment calls

1. **Dell Q3 FY2027 guide (the `next_guide` cells of the 2026-09-01 row).** Dell's release gives one figure, 49.0, with
   no range (earlier releases gave a low and a high). Dell's own blog post calls it "$49.0 billion at the midpoint". A
   web search summary said the range was 49.0 plus or minus 0.5 (48.5 to 49.5), presumably from the call, but I could
   not open a page that says so, so that range is unverified. Used 49.0 for low, high and mid. The midpoint is not in
   doubt. Sources: https://www.sec.gov/Archives/edgar/data/1571996/000157199626000039/exhibit991earnings8kq2fy27.htm
   and https://www.dell.com/en-us/blog/record-results-reflect-compounding-advantages/
2. **Headline rounding vs statement figures.** Headlines round (Nvidia "81.6", ASML "9.3", KLA "3.66"); the CSV uses
   the statement figures (81.615, 9.3265, 3.657556). ASML's release table prints 9,326 while its US GAAP statements
   print 9,326.5; used 9.3265.
3. **TSMC 2Q26 landed exactly on the top of its range.** Guide 39.0 to 40.2, actual 40.20 as TSMC states it to two
   decimals. It is above the midpoint (39.6); whether it is "above the range" cannot be told at this precision.
4. **Nvidia Q4 FY2027 guide is on a different basis.** 130.0 plus or minus 3% (earlier guides were plus or minus 2%)
   and the quarter includes an additional week.
5. **AMD Q4 2026 guide switched to a percentage band.** "Approximately $17 billion, plus or minus 3%" (earlier guides
   were plus or minus $300 million); converted to 16.49 to 17.51.

## Mid-quarter guidance checks

I read every other 8-K each US company filed between its reports, looking for guidance changes.

- **Marvell, 2026-06-11:** reaffirmed the Q2 FY2027 outlook unchanged (with a CFO transition). No effect on the row.
- **Marvell, 2026-11-02 (formal pre-announcement, NOT a row):** an Item 2.02 8-K filed with the Lumentum merger
  announcement said preliminary Q3 FY2027 revenue is consistent with prior guidance, keeping the midpoint (3.150) and
  narrowing the range from plus or minus 5% to plus or minus 2%. No revenue figure was given and it is not a quarterly
  report; the full Q3 FY2027 report falls after the window. If that report is added later, the guide to use is the
  original 3.150 plus or minus 5% from 2026-08-27, with this pre-announcement noted.
  Source: https://www.sec.gov/Archives/edgar/data/1835632/000119312526442714/d81187dex991.htm
- **Micron FQ3 2026 (actual 41.456 vs guide midpoint 33.5) and Dell Q1 FY2027 (actual 43.842 vs guide midpoint 35.2):**
  both beats are very large, so I checked specifically for a mid-quarter update. None was filed; the other 8-Ks in
  those quarters were debt, tender-offer and officer items. The guides in the CSV are the ones standing before the
  report. This check covers SEC filings only; remarks at investor conferences that were not filed would not show up.
- No other company filed a guidance change between reports.

## Dates close to the window edges

- **Inside, near the start:** NVDA 2026-05-20 (2 days in), MRVL 2026-05-27, DELL 2026-05-28.
- **Inside, at the end:** NVDA 2026-11-17 (the last day of the window), AMAT 2026-11-12, AMD 2026-11-03.
- **Outside, just before the start (excluded):** AMAT Q2 FY2026 on 2026-05-14 (4 days before the window; used only as
  the source of the Q3 FY2026 guide), AMD Q1 2026 on 2026-05-05.
- **Outside, after the end (not yet published as of 18 Nov 2026):** DELL Q3 FY2027, MRVL Q3 FY2027, AVGO Q4 FY2026
  and MU FQ1 2027.

## Other things a user of the file should know

- TSMC publishes monthly revenue in NT dollars, so its quarterly NT dollar revenue is public about a week before the
  report. The US dollar figure and the guide comparison are still first stated in the report.
- ASML's guide and actual are "total net sales" in euros; TSMC guides and is recorded in US dollars.
- KLA did a ten-for-one stock split between its April and July reports. Revenue is unaffected.
