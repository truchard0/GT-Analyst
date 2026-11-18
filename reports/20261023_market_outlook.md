# Market outlook, 23 Oct 2026 to end-January 2027

General research view built from this repo's own data and tools. Not personalised financial advice: no positions, sizes or entries.
Every probability below is an estimate with its basis stated; the frozen list of scoreable claims is at the bottom (section 8).
Built under the engine's own rules: price ranges, dates and conditional scenarios, never a confident call on the next leg (doctrine 16.15, 16.18, 16.20).

## 1. Bottom line

1. **The index is quiet and the tape under it is not.** SPY is 2.5% off its 10/6 high with 9.8% realised vol, while the VIX sits at 19.5, QQQ is 7.3% off its high and SMH 21%. The S&P is being held up by energy and defensives; the AI-semis leg is in a drawdown.
2. **The next two weeks are a calendar, not a trend.** Israeli vote 10/27, FOMC 10/28, OPEC+ 11/1, US midterms 11/3. The US has pledged no strike on Iran before 11/3 (book: 0.84 it holds); that restraint is political and lapses at the vote.
3. **The central path is flat-to-modestly-higher with a fat left tail.** Scenario-weighted, SPY's year-end median is about where it is today (760) with a 5-95% span of roughly 680-825, against a no-view span of about 690-840: the scenario weights fatten the left side and trim the right. The left tail is the post-vote Iran branch, not the Fed.
4. **Rates are the second risk.** The 10-year is 4.99% (5.31% high on 10/5), the Fed hiked on 9/16 and the book has a second hike by 12/9 at 0.68. A retest of 5.31% by year-end is about 0.40.
5. **Skylit adds structure for the next days, nothing for the next months.** The tests below found no multi-month predictive power in its daily gamma summaries.

## 2. Where we are (closes 23 Oct)

| | last | vs 52w high | 1m | realised vol (20d, ann.) |
|---|---|---|---|---|
| SPY | 759.97 | -2.5% (779.09, 10/6) | -0.9% | 9.8% |
| QQQ | 704.40 | -7.3% (759.66, 10/6) | -5.0% | 18.5% |
| SMH | 527.20 | -21.2% (668.91, 6/22) | -12.2% | 34.3% |
| IWM | 275.75 | -9.4% (304.30, 8/14) | -2.1% | 14.7% |
| XLE | 69.33 | at its high | +10.8% | 20.3% |
| Brent | 111.66 | -5.7% (118.35, 3/31) | +4.7% | 28.9% (60d: 40%) |
| 10y yield | 4.99% | 5.31% on 10/5 | -3.4% | n/a |
| VIX | 19.45 | 31.05 on 3/27 | +24.1% | n/a |
| Gold (GLD) | 366.61 | -26.1% (495.90, 1/29) | -6.4% | 22.1% |
| HYG | 77.05 | -2.6% | -0.6% | 3.6% |

Fed funds 3.75-4.00% (hiked 25bp 9/16, 12-0). The gap between SPY's realised 9.8% and the VIX's 19.5 is the market paying for event risk.

## 3. What the Skylit data says

**Structure now (saved locally, no credits spent).** Final saved snapshot, valid for the next session only:
- SPY: net dealer gamma **-702M**; gamma flip **754.1** (0.8-0.9% below; the snapshot's spot of 761.2 is a little above the 759.97 close); largest node a **negative King at 755 (-367M)**; positive wall 750 (+178M).
- SPXW: spot 7623.7; flip **7495** (1.7% below the snapshot spot); King 7750 (+10.6M); negative wall 7500.
- QQQ: net +29M; flip 689.4 (2.3% below); King 725 (+59M); negative wall 690.
- 10/22 close read: maps THIN, SPY and QQQ flagged LOW-GAMMA DAY (Kings 40-56% of their 20-session medians).
- SPY's overnight net gamma was negative on 9 of the last 10 nights.

Reading, under the engine's doctrine (maps are structure and magnets, not direction): 750-755 is the zone where hedging flips from damping to amplifying; a close below about 754 puts SPY in short-gamma territory where a given shock moves it further. That is a statement about the size of moves, not their sign.

**What it cannot do (tested today).** On Skylit's daily SPX gamma summary (734 sessions, July 2023 to July 2026, for the first test; 754 for the second):
- the size of the day's gamma peak vs the next 20 days' realised vol: Spearman -0.14, 95% block CI [-0.29, +0.00]; vs the next 60 days: -0.09 [-0.25, +0.07]. The top quartile of gamma size was followed by 11.9% vol against 13.6% overall; an effect of about two vol points, not significant.
- the negative-gamma share of the day's strike gamma: -0.07 [-0.23, +0.08] at 20 days, -0.09 [-0.29, +0.11] at 60 days.

So today's thin, negative-gamma map is a mild reason to expect bigger swings for a few weeks, and no reason at all to expect a direction or a regime for months. The saved monthly-book maps stop at 9/30 and the live recorder keeps only the five nearest expiries, so there is no local view of the December or January monthly structure. Pulling it would cost credits and I have not.

## 4. The calendar (dates from the book's tree unless marked)

| date | event and the book's probability |
|---|---|
| 10/27 | Israeli election; no bloc at 61 seats 0.84; Netanyahu still prime minister (transitional government) on 12/1: 0.90 |
| 10/28 | FOMC statement; hike at this meeting 0.15; second hike by 12/9: 0.68 |
| 10/29 | ECB; hike 0.30 |
| late Oct | Q3 mega-cap earnings and AI-capex guidance (dates not in the tree) |
| 11/1 | OPEC+ meeting (sets December output); quotas unchanged 0.55 |
| 11/3 | US midterms; Democratic House 0.80, contested result 0.08; the US no-strike pledge expires |
| 11/4 | Treasury refunding; Israeli certified results |
| 11/4-11/17 | first window after the pledge lapses (my estimate: 0.20-0.25 for a US strike, not logged) |
| 11/6, 11/12 | October payrolls; October CPI |
| 11/18-19 | APEC; US-China Busan truce rolled or replaced by 1/10: 0.66 |
| 12/9 | FOMC with projections; dots show a further 2027 hike 0.60; SCOTUS DVD argument |
| 12/11 | funding stopgap expires; a lapse of a day or more by 12/31: 0.30 |
| 12/17-19 | ECB (hold 0.55), BoJ (hike 0.45), monthly options expiry 12/18 |
| 1/3 | new Congress convenes |

## 5. Scenarios to year-end

The war has given three observations of how markets react (SPY/Brent over 10 sessions): strikes began 3/2 (SPY -2.5%, Brent +38%), 7/8 (SPY 0.0%, Brent +27%), 8/31 (SPY -1.6%, Brent +22%); stand-downs came 4/8 (SPY +7.9%, Brent -7%), 7/27 (+4.6%, -9%), 8/3 (+3.4%, +1%), 9/10 (+0.9%, +5%). Strikes move oil a lot and the index little; stand-downs lift the index 1-8%.

| scenario | weight | what happens | SPY year-end (judgement) | Brent |
|---|---|---|---|---|
| **A. restraint holds** | 0.50 | no US or Israeli campaign by 12/31; talks via Qatar drag; post-vote relief plus seasonal strength | median ~775, middle half 750-800 | drifts 95-110 |
| **B. limited strike, then pause** | 0.28 | the planned few-day strike on nuclear or energy sites after 11/3; oil spikes, equities dip 1-4%, then recover | median ~760, middle half 736-784, after an early dip to 735-750 | spike to 125-140, ends 105-120 |
| **C. sustained campaign** | 0.22 | strikes become a campaign (3 of the war's 7 strike episodes became campaigns, runs of 39, 16 and 11 days; the other four were one-off retaliations) | median ~715, middle half 688-742 | 125-150 |

The weights come from the tree: a US strike 11/4-12/31 at 0.45 and 0.16 before the vote overlap (a strike before the vote usually continues after it), so the union is about 0.50 for any strike; I split it by how strikes have unfolded: C is 0.44 of B+C, against 3 of 7 episodes so far. Seasonality is a mild tailwind for A: the S&P rose in the 12 months after 32 of 38 midterms since 1874 (average ~14%), and the 12 months before a midterm average only about 3% (Motley Fool, US Bank; sponsored sources, high valuations argue against leaning on it).

## 6. No-view ranges (driftless, vol-based)

SPY 759.97 to 12/31 (47 sessions). Vol per day: 0.62% (current realised), 0.88% (long-run, ~14% annualised), 1.23% (VIX-implied).

| | 5% | 25% | 50% | 75% | 95% |
|---|---|---|---|---|---|
| 0.62% | 708 | 738 | 759 | 781 | 814 |
| 0.88% | 687 | 728 | 759 | 790 | 838 |
| 1.23% | 659 | 715 | 757 | 802 | 870 |

| SPY, by 12/31 | 0.62% | 0.88% | 1.23% |
|---|---|---|---|
| closes above 779.09 on 12/31 | 0.27 | 0.33 | 0.37 |
| touches 780 | 0.54 | 0.67 | 0.76 |
| closes below 720 on 12/31 | 0.11 | 0.19 | 0.27 |
| touches 720 | 0.20 | 0.37 | 0.52 |
| touches 700 | 0.05 | 0.17 | 0.33 |
| closes 12/31 inside 720-800 | 0.78 | 0.62 | 0.47 |

Other no-view numbers by 12/31: QQQ touches 759.66 0.35-0.43, touches 650 0.32-0.40; SMH touches 605 0.35, touches 480 0.52; Brent closes below 100 0.20-0.29, touches 125 0.36-0.51, touches 140 0.07-0.19; the 10-year, one standard deviation about 39bp (5/50/95% = 4.35/4.99/5.63), touches 5.31 0.41, touches 5.50 0.19.

## 7. What would change the view

- **A US strike or an Iranian attack that kills US personnel before 11/3**: restraint broken; move weight from A toward B/C. Per R37, only that trigger justifies a pre-vote strike call above 0.5.
- **The pledge repeated or extended past 11/3** (book: 0.12): lowers B and C, raises A.
- **SPY closing below 754** with the 755 negative King failing: short-gamma regime, larger daily moves in both directions.
- **10-year above 5.31%**: the AI-semis leg has been the casualty of each leg up in yields.
- **A 12/9 dot plot or CPI (11/12) that revives the hike path**, and the 12/11 funding deadline with a changed House.

## 8. Frozen forward claims (scoreable; registered in prereg/REGISTRY.jsonl)

Probabilities are the engine's, not the no-view ones; a direction claim is capped at 0.55 by doctrine.

| # | claim (by 2026-12-31 unless stated) | P | no-view reference |
|---|---|---|---|
| 1 | SPY closes 12/31 above 759.97 | 0.52 | 0.49 |
| 2 | SPY makes a closing high above 779.09 | 0.55 | 0.54-0.76 (touch of 780; a closing basis is lower) |
| 3 | SPY closes at or below 720 on at least one day | 0.30 | 0.18-0.47 (closing basis) |
| 4 | SPY closes at or below 701.2 (10% under the high) on at least one day | 0.13 | 0.05-0.30 (closing basis) |
| 5 | VIX closes above 25 on at least one day | 0.30 | scenario-built |
| 6 | Brent closes above 125 on at least one day | 0.38 | 0.36-0.51 (touch) |
| 7 | Brent closes 12/31 below 100 | 0.30 | 0.20-0.29 |
| 8 | the 10-year closes at or above 5.31% on at least one day | 0.38 | 0.41 |
| 9 | SMH closes at or above 605 on at least one day | 0.33 | 0.35 |
| 10 | SMH closes at or below 480 on at least one day | 0.45 | 0.52 |
| 11 | by 11/6 SPY closes at or below 754.1 (the 10/23 gamma flip) on at least one day | 0.62 | 0.56-0.70 (closing basis) |
| 12 | the US or Israel strikes Iranian territory | 0.50 | book |
| 13 | the FOMC has raised by its 12/9 decision | 0.68 | book |
| 14 | the Democrats win the House | 0.80 | forecasters 0.78-0.92 |

## 9. Limits

- Scenario weights and the SPY ranges inside each scenario are my judgement from three war observations; the Iran branch rests on a restraint model that beat persistence only in the political stretch (doctrine 16.20).
- No-view odds assume a driftless random walk at one volatility; vol clusters, so a shock widens everything above.
- Closing-basis claims are lower than the touch probabilities they sit beside.
- This is a research view, not advice about any position.

## 10. Corrections after a check on 23 Oct (registered again as market-outlook-20261023-r2)

The first version was registered before any claim could resolve, then audited. Changes:
- **Scenario centres.** The first table put A at 785, B at 767 and C at 720, which implied a year-end median of 771 and P(SPY above today) of 0.63, contradicting both the text (median 760-765) and claim 1 (0.52). Re-centred to A 775, B 760, C 715 with within-scenario spreads of 35-40; the mixture is now median 760, P(above 759.97) 0.50, P(close 12/31 below 720) 0.19.
- **War base rate.** The text said each strike episode had become a campaign, 3 of 3. Counting the war's strike episodes properly gives 3 of 7: the four one-off retaliations had been left out. Round lengths were also misstated; the coded data say 39, 16 (22 with the 7/29 strike) and 11 days. The same 3-of-3 figure sat in pipeline/conflict.py and made its escalation check refuse #59 and #64, which it should not have; fixed there too (see STATE.md).
- **Claim 11** compared a 754.1 barrier with a no-view figure computed for 750; recomputed on a closing basis (0.56-0.70) and raised to 0.62. Claims 2, 3 and 4 now state their no-view references on the basis the claim uses.
- **Unchanged:** the market snapshot, the Skylit levels, the two vol tests, the event reactions, the calendar and every book probability, each re-checked against its source.

## 11. Corrections on 25 Oct (after the 24 Oct deep research, "Stock market geopolitical game")

Not re-registered: claims 1-14 and their probabilities stand exactly as registered in r2. These change the inputs and the book around them.
- **Brent, 23 Oct: both numbers were right, for different contracts.** The table's 111.66 is the continuous BZ=F series, which rolled to January Brent on 10/23 (BZF27 settled 111.70). Reuters' 116.72 is December Brent (BZZ26), still the ICE front month until it expires 10/30. The December-January spread was about $5 that day, a steep backwardation that says the market already prices the war premium decaying. **Claims 6 and 7 and the section-6 Brent no-view odds were computed on BZ=F and stay valid on that basis;** a December-contract basis would need only a ~7% rise to 125 instead of ~12%. Ledger #83 resolves on the FRONT month, so tools/tripwire.py now reads December's closes to 10/30 (`front_months` in data/autoresolve.json); #83 confirmed at 0.25 (no-view 0.32 at 2.5%/day from 116.72).
- **Brent's 2026 peak is unresolved:** 118.35 on 3/31 here; other sources give 120.88 (4/30 intraday), 126 and 138.21 (4/7). Some of the gap is probably the same contract-month issue.
- **The 10-year's high:** 5.31% on 10/5 is the close used here; Forbes reports 5.35-5.36% on 10/7, "highest since 2002".
- **Scenario A's Brent band stays 95-110 on the BZ=F basis** (spot 111.7). Add an upside branch A+: a Qatar-channel deal trading blockade relief for an end to tanker attacks (the June precedent took Goldman's Q4 call to $80). Weights unchanged; the research supports at most a ~0.05 tilt from A to B, not taken.
- **Calendar probabilities, repriced in the tree (tools/corrections_20261025.py):** ECB hike 10/29 0.30 -> 0.05 (ECB Watch 97% hold); ECB hold 12/17 0.55 -> 0.45 (Danske expects a final hike to 2.75%); BoJ hike in December 0.45 -> 0.50 (ledger #104 too); OPEC+ quotas unchanged 0.55 -> 0.70 (the 11/1 meeting is the seven-member core group, which pumps ~5 mb/d below quota since the UAE left on 5/1; 2027 policy is set at the 11/29 ministerial, now on the tree); the Fed has hiked by 12/9 0.68 -> 0.72 (claim 13 stays registered at 0.68).
- **US-China truce row reworded:** it already runs to 1/10/2027 (extended 9/23), so the call is "extended beyond 1/10/2027 or replaced, announced by 1/10"; 0.66 unchanged.
- **Restraint calendar re-sourced:** the 10/22 NewsNation "postpones major combat" line and a "Reuters 10/20" story could not be found; us-energy-price-oct is now `inferred` and cites the NYT 10/21-22 reporting; Iran's pre-vote pressure cites Reuters 10/14 and the Washington Post 10/18. The suppression to 11/3 rests on the 10/8 pledge alone.
