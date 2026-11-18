# Buyers dataset notes (capex.csv, prints_buyers.csv)

Gathered 18 Nov 2026. Window: reports published 18 May 2026 to 17 Nov 2026 inclusive.
Collection only; nothing here is scored.

## Coverage

| Ticker | Reports in window | Third report? |
|---|---|---|
| MSFT | 2026-07-29 (FY26 Q4), 2026-10-28 (FY27 Q1) | No |
| GOOGL | 2026-07-22 (Q2), 2026-10-28 (Q3) | No |
| AMZN | 2026-07-30 (Q2), 2026-10-29 (Q3) | No |
| META | 2026-07-29 (Q2), 2026-10-21 (Q3) | No |
| ORCL | 2026-06-10 (FY26 Q4), 2026-09-10 (FY27 Q1) | No |

Report dates come from the SEC filing index (Item 2.02 8-Ks). Each company's previous report
(29 Apr 2026 for the first four, 10 Mar 2026 for Oracle) is before the window, and Oracle's next one
(FY27 Q2) had not been filed by 17 Nov 2026. So: 10 capex rows, 6 revenue rows.

All ten reports were after the close. Timing is taken from the SEC acceptance time of each 8-K
(16:01 to 16:16 Eastern), not from a company statement of the release time.

## How each source was read

- **Microsoft, Alphabet:** the full call transcripts on the companies' own sites were downloaded and
  read as text. Quotes in the CSV are copied from them.
- **Amazon, Meta, Oracle press releases (SEC Exhibit 99.1):** the SEC site refused direct download, so
  these were read through a fetch tool that returns extracted passages, not the raw page. Every reported
  number taken from them (revenue, capex, finance leases) was then checked against the SEC XBRL data and
  matched. Guidance ranges cannot be checked that way; each was checked against at least one news report
  and matched. They are tagged primary on that basis. Quotes from these releases are as returned by the
  fetch tool and may differ from the original in punctuation.
- **Amazon and Oracle call statements:** neither company publishes a transcript. These come from
  third-party transcripts and recaps and are tagged secondary.

## Quality tags

capex.csv: 7 primary, 3 secondary, 0 unverified.
prints_buyers.csv: 6 primary, 0 secondary, 0 unverified.

Secondary capex rows:
- AMZN 2026-07-30: the raise to about 220 is from a Motley Fool transcript of the call. The Q2 release has
  no annual capex figure. The company's own 29 Oct 2026 release later says "We continue to expect 2026
  cash capital expenditures to be approximately $220 billion", which confirms the number.
- ORCL 2026-06-10 and 2026-09-10: Oracle's releases carry revenue and EPS guidance but no fiscal 2027
  capex figure. The capex guide is from call recaps (MarketBeat, The Next Web, Outlook Business citing
  Reuters). No full transcript could be opened (two transcript sites refused access).

## Judgment calls in the `change` column

1. **MSFT 2026-07-29, tagged `hold`. This is the one row where the tag could reasonably be `cut`.**
   The calendar-2026 number went from roughly 190 to approximately 175. Microsoft said the whole
   difference is accounting: it extended datacenter useful lives from 15 to 25 years, which moves future
   datacenter leases from finance leases (counted in its capex) to operating leases (not counted), and
   "outside of this useful life impact, our calendar year 2026 CapEx investment expectations remain
   unchanged." The collection rules say both "cut = the number went down" and "hold = unchanged or
   reaffirmed"; both fit. I used `hold` because the two numbers are on different definitions and the
   company reaffirmed the like-for-like plan. Anyone scoring a no-cut rule should run this row both ways.
   At the same report Microsoft also said fiscal 2027 capex "will grow year-over-year", its first
   fiscal-year statement.
2. **MSFT 2026-10-28, tagged `cut`.** Calendar 2026 went from approximately 175 to approximately 170
   "due to the 3P capacity delays". Microsoft described it as timing (third-party capacity deliveries
   slipped into the second half of fiscal 2027, where it expects capex to accelerate), not a smaller
   plan. Tagged `cut` because the number went down and the rules count a cut blamed on capacity delays
   as a cut. The quarter's capex (45.2) was also below the "over $50 billion" guide for the quarter.
3. **MSFT guide basis.** The rules ask for Microsoft's fiscal-year guide. Microsoft's only numeric annual
   guide is for calendar 2026, so the number columns hold the calendar-2026 figure. The fiscal-year
   statement is directional only and is in the text columns.
4. **META, both rows tagged `raise`.** Meta called each change a narrowing: 125-145 to 130-145 in July
   and 130-145 to 135-145 in October. The top of the range never moved; the bottom rose each time, so
   the midpoint rose (135, 137.5, 140). Tagged `raise` under the midpoint rule.
5. **ORCL 2026-06-10, tagged `raise`.** This report rolls the fiscal year. The guide before it was for
   fiscal 2026 (50, reaffirmed 10 Mar 2026); the guide at it is the first fiscal 2027 figure. The two
   number cells are therefore different fiscal years. I found no fiscal 2027 capex number from before
   10 Jun 2026. Tagged `raise` because the new annual figure is far above both the fiscal 2026 guide and
   the fiscal 2026 actual (55.663, which itself overshot the 50 guide). A stricter reading is that there
   is no like-for-like prior and the row should be excluded.
6. **ORCL fiscal 2027 figure, 90-95.** At the June call the CFO gave about 70 of net cash capex, with
   reported capex higher by 20-25 of customer prepayments and timing. 90-95 is that sum, not a quoted
   range from June. Reuters-based coverage wrote "up to $95 billion". The September call wording ("we
   continue to anticipate $90 billion to $95 billion in CapEx for the full year with not more than
   $70 billion in net cash CapEx") supports reading June as 90-95, and makes September a `hold`.

## Conflicts between sources and the figure used

- **Alphabet October:** one aggregator said Alphabet raised 2026 capex to 195-205 in October. The official
  transcripts show the raise was on 22 Jul 2026 and the range was "unchanged" on 28 Oct 2026. Used the
  transcripts.
- **Microsoft October:** news reports variously called the 170 figure a fiscal-2027 or a calendar-year
  number. The transcript says "for the calendar year". Used calendar 2026.
- **Amazon quarterly capex:** recaps cite either gross purchases of property and equipment (54.2 in Q2,
  77.3 in Q3) or the company's "cash capex" (53.1, 75.9). The annual guide is on the cash capex basis
  (purchases less proceeds from sales and incentives), so the CSV uses that, computed from the release:
  54.208 - 1.132 = 53.076 and 77.259 - 1.381 = 75.878. Gross figures are in the note.
- **Amazon Q1 capex** (context only, not a row): recaps give 43.2 (cash capex) and 44.2 (gross
  purchases). Same definitional difference.
- **Oracle fiscal 2027 capex:** one article described the guide as 70, another as "up to 95". Both
  describe the same statement (70 net, 90-95 reported). The CSV uses the reported basis, 90-95, because
  the quarterly capex figures are on that basis.
- **Oracle fiscal 2026 capex:** recaps give 48 (net cash outlay) and 55.7 (reported). XBRL confirms
  55.663 reported.

## What the capex figure includes

| Ticker | Basis of reported_quarter_capex | Finance leases |
|---|---|---|
| MSFT | Capital expenditures as stated on the call | Included (5.6 in FY26 Q4, 7.4 in FY27 Q1) |
| GOOGL | Purchases of property and equipment | Excluded |
| AMZN | Purchases of property and equipment less proceeds from sales and incentives | Excluded |
| META | Purchases of property and equipment plus principal payments on finance leases | Included (principal payments only) |
| ORCL | Capital expenditures from the cash flow statement | Excluded; gross of customer prepayments |

Microsoft's two quarterly figures (41 and 45.2) are as spoken on the call and are not given to more
decimals anywhere I could find. The other eight are exact to the million from filings.

## Oracle revenue-guide conversion

Oracle guides total revenue growth; the range was converted using the year-ago quarter's reported revenue.
The USD growth range was used, since the actual is reported in USD.

| Quarter guided | Growth range (USD) | Year-ago revenue | Low | High | Midpoint |
|---|---|---|---|---|---|
| FY26 Q4 (guide of 10 Mar 2026) | 19% to 21% | 15.903 | 18.925 | 19.243 | 19.084 |
| FY27 Q1 (guide of 10 Jun 2026) | 27% to 29% | 14.926 | 18.956 | 19.255 | 19.105 |
| FY27 Q2 (guide of 10 Sep 2026) | 30% to 34% | 16.058 | 20.875 | 21.518 | 21.197 |

For FY26 Q4 the constant-currency range was 18% to 20%, which would give 18.766 to 19.084. For the other
two quarters Oracle gave the same range in USD and constant currency. Converted values are rounded to
three decimals. Year-ago revenues are from SEC XBRL (FY26 Q4's 15.903 is fiscal 2025 revenue 57.399 less
nine months 41.496).

## Not found or not verified

- **Statements between reports.** I did not find any capex-guide change made between quarterly reports
  (conferences, investor days) for any of the five, but I did not search for them exhaustively. In every
  row the company's own wording at the new report ("up from our previous estimate of", "narrowed from our
  prior outlook of", "continue to expect") matches the prior figure in the CSV, which is good evidence
  that nothing changed in between. The exception is Oracle in June, where there was no prior fiscal 2027
  figure to restate.
- **Amazon, 29 Apr 2026.** The Q1 release and the transcript I read contain no restatement of the
  roughly 200 full-year figure. The prior guide for the July row rests on the CEO's own July recap
  ("Earlier this year, we said we plan to invest approximately $200 billion") and on news reports that
  the company was "on track" for it in April.
- **Amazon 2027.** "Spending is expected to rise meaningfully in 2027" is from recaps; exact wording was
  not verified against a transcript.
- **Oracle call transcripts.** No complete transcript of the 10 Jun or 10 Sep 2026 calls was read. The
  CFO's exact June wording on fiscal 2027 capex is not verified.
- **Oracle 10-K and 10-Q text.** Not checked for a written fiscal 2027 capex expectation.
- **Meta calls.** Only the releases were read. Any 2027 capex commentary on the calls beyond the release
  text was not collected.
- **Microsoft fiscal-year number.** No numeric fiscal 2027 capex guide exists in either call; the cell
  holds the calendar-2026 number instead (see judgment call 3).
- No cell was estimated. The only derived values are the Oracle revenue conversions, the Oracle 90-95
  sum, and the Amazon and Meta quarterly capex sums, each with its arithmetic in the note column.
