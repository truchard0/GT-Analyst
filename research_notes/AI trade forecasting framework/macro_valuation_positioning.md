# Macro, valuation, positioning and price state of the AI equity trade (as of 18 Nov 2026)

Method note for the report writer. Price levels marked **[RH]** come from a brokerage market-data feed (Robinhood quote / fundamentals / historical-bar / indicator endpoints, official SIP closes), pulled at 02:33 UTC on 18 Nov 2026 (9:33 pm ET, 17 Nov). They are exact to the cent and dated. Everything else comes from web reporting, read through automated page summaries; several load-bearing pages (Forbes, Benzinga, TheStreet, Kiplinger) returned HTTP 403 or truncated text, so those figures come from search-result summaries and are flagged where it matters. Percent changes that I computed from [RH] levels are marked "(calc)". All dates are 2026 unless stated. 17 Nov 2026 was a Tuesday; 12 Nov was a Thursday.

Three premises in the brief need correcting before use:
1. The November 2026 BofA survey's most crowded trade is **semiconductors (39%)**, not "long Magnificent 7". The "long Mag 7 54% / AI bubble 45%" figures are the **November 2025** survey.
2. The semiconductor complex peaked on **22 June 2026** (SMH, SOXX, SOX; Micron 25 June; Broadcom 3 June). 6 October was a *lower high* for SMH/SOX but the *record* for Nvidia, AMD, QQQ and SPY.
3. The 17 Nov software selloff was attributed mainly to AI seat-pricing fears and the Anthropic IPO supply; outages were cited as a secondary factor. I found no reporting tying it to "AI misuse".

A fourth item the brief did not mention but which dominates the Nvidia tape: **Jensen Huang resigned as Nvidia CEO on Thursday 12 Nov 2026**; CFO Colette Kress is interim CEO.

---

## 1. Price state: levels, highs/lows, size and dating of the selloff, moving averages, volatility, Nvidia earnings reaction

### Takeaway
Nvidia closed at **$155.46 on 17 Nov**, 35% below its 6 Oct record close ($239.24) and about **$2.06 trillion** of market value lighter; SMH closed at **$460.10**, 31.5% below its 22 June record and 12% below its 200-day average. The S&P 500 (**7,340.53**) closed exactly on its 200-day average with VIX at **25.46**; Nvidia beat and guided above consensus after the close, but the after-hours gain (reported +1% to +5%, +0.9% by 9:33 pm ET) is far inside the ~8% implied move.

### Cited Findings

**Closing levels 17 Nov 2026, 2026 highs/lows, drawdown, moving averages (all [RH]; highs/lows are intraday; drawdown and MA gaps are calc)**

| Ticker | Close 17 Nov | 2026 high (date) | 2026 low (date) | vs 2026 high | 50-DMA | 200-DMA | vs 50 / vs 200 |
|---|---|---|---|---|---|---|---|
| NVDA | 155.46 | 243.37 (6 Oct) | 148.80 (12 Nov) | -36.1% | 211.76 | 203.87 | -26.6% / -23.7% |
| SMH | 460.10 | 671.83 (22 Jun) | 359.86 (week of 30 Mar) | -31.5% | 555.47 | 524.45 | -17.2% / -12.3% |
| SOXX | 141.46 | 218.65 (22 Jun) | 102.42 (date not pulled) | -35.3% | 170.56 | 160.63 | -17.1% / -11.9% |
| QQQ | 656.95 | 762.86 (6 Oct) | 555.60 (30 Mar) | -13.9% | 715.59 | 682.62 | -8.2% / -3.8% |
| SPY | 732.44 | 781.62 (6 Oct) | 629.28 (30 Mar) | -6.3% | 763.30 | 732.38 | -4.0% / +0.0% |
| AMD | 503.41 | 658.52 (6 Oct) | 188.22 (3 Mar) | -23.6% | 555.06 | 425.75 | -9.3% / +18.2% |
| AVGO | 341.60 | 495.00 (3 Jun) | 289.77 (6 Nov) | -31.0% | 344.19 | 367.45 | -0.8% / -7.0% |
| TSM (ADR) | 359.69 | 487.47 (5 Oct) | 311.70 (date not pulled) | -26.2% | 427.69 | 403.43 | -15.9% / -10.8% |
| MU | 712.42 | 1,255.00 (25 Jun) | 294.86 (early Jan) | -43.2% | 932.20 | 768.53 | -23.6% / -7.3% |
| CRWV | 49.89 | 138.25 (6 May) | 40.58 (5 Nov) | -63.9% | n/a | n/a | n/a |
| ORCL | 115.00 | 250.25 (1 Jun) | 109.21 (6 Nov) | -54.0% | n/a | n/a | n/a |
| MSFT | 506.24 | 559.15 (4 Nov) | 349.20 (25 Jun) | -9.5% | n/a | n/a | n/a |
| GOOGL | 280.20 | 408.61 (18 May) | 272.11 (30 Mar) | -31.4% | n/a | n/a | n/a |
| AMZN | 257.89 | 287.20 (3 Aug) | 196.00 (17 Feb) | -10.2% | n/a | n/a | n/a |
| META | 618.87 | 779.82 (24 Sep) | 520.26 (27 Mar) | -20.6% | n/a | n/a | n/a |
| IGV | 95.74 | 113.70 (12 Oct) | 73.93 (10 Apr) | -15.8% | 105.93 | 94.27 | -9.6% / +1.6% |

— [Robinhood NVDA](https://robinhood.com/stocks/NVDA), [SMH](https://robinhood.com/stocks/SMH), [SOXX](https://robinhood.com/stocks/SOXX), [QQQ](https://robinhood.com/stocks/QQQ), [SPY](https://robinhood.com/stocks/SPY), [AMD](https://robinhood.com/stocks/AMD), [AVGO](https://robinhood.com/stocks/AVGO), [TSM](https://robinhood.com/stocks/TSM), [MU](https://robinhood.com/stocks/MU), [CRWV](https://robinhood.com/stocks/CRWV), [ORCL](https://robinhood.com/stocks/ORCL), [MSFT](https://robinhood.com/stocks/MSFT), [GOOGL](https://robinhood.com/stocks/GOOGL), [AMZN](https://robinhood.com/stocks/AMZN), [META](https://robinhood.com/stocks/META), [IGV](https://robinhood.com/stocks/IGV)

- Other 17 Nov closes [RH]: AAPL 351.91, TSLA 380.11, XLU 43.42, XLP 91.46. — [Robinhood AAPL](https://robinhood.com/stocks/AAPL)
- Market caps at the 17 Nov close [RH]: NVDA $3.82tn, MSFT $3.76tn, GOOGL $3.43tn, AMZN $2.79tn, TSM $1.87tn, AVGO $1.63tn, META $1.58tn, AMD $826bn, MU $807bn, ORCL $348bn, CRWV $27.4bn. ETF assets: SMH $60.9bn, SOXX $36.0bn. — [Robinhood NVDA](https://robinhood.com/stocks/NVDA)
- Index closes 17 Nov: S&P 500 **7,340.53** (-76.06, -1.03%; lowest close since late July; intraday -1.73%); Dow **50,759.42** (-848.75, -1.64%); Nasdaq Composite **24,328.38** (-181.37, -0.74%; intraday about -2.1%, lowest level since April); Russell 2000 **2,701.87** (-1.50%). — [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html); [TechFlow recap](https://www.techflowpost.com/en-US/article/35453)
- Nasdaq-100 on 17 Nov: **27,001.78** (index feed, timestamp 17:15 ET) [RH]. — [Robinhood QQQ](https://robinhood.com/stocks/QQQ)
- Earlier S&P 500 closes: 10 Nov 7,520.93; 11 Nov 7,619.38 (+1.3%, CoreWeave relief); 12 Nov 7,592.40 (-0.35%); Nasdaq Composite 11 Nov 25,466.19, 12 Nov 25,366.09; Dow 12 Nov 52,297.09. — [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields); [Zacks](https://www.zacks.com/stock/news/3027683/stock-market-news-for-nov-11-2026)
- Philadelphia Semiconductor Index (SOX): all-time high **14,655 on 22 June 2026**; closed **10,268.65 on 4 Nov** and **9,011.14 on 5 Nov** (-1,257.52 points, -12.25%, second-largest one-day fall on record, largest since March 2020). — [24/7 Wall St. (search summary)](https://247wallst.com/investing/2026/11/06/chip-stocks-just-had-their-second-worst-day-on-record/); [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1)
- SOX finished 38% below its 22 June record (Forbes, published 12 Nov; the arithmetic matches the 5 Nov close). 28 of 30 SOXX holdings were at least 20% below record closes on 5 Nov. — [Forbes (search summary, page 403)](https://www.forbes.com/sites/danirvine/2026/11/12/the-calmest-market-in-years-was-hiding-a-bear-market/); [Benzinga (search summary, page 403)](https://www.benzinga.com/markets/equities/26/11/62961405/chip-stocks-worst-day-since-2020-soxx-bear-market)
- SOX rose about 6.9% on 9 Nov and reclaimed 10,000; an undated TheStreet item has it +5.66% to 10,564 (consistent with 11 Nov). — [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262296975-philadelphia-semiconductor-index-reclaims-10000-morgan-stanley-ai-stock-opportunities-nvidia-broadcom-tradingkey); [TheStreet Pro (search summary)](https://pro.thestreet.com/market-commentary/wednesdays-charts-best-four-day-gain-for-semis-since-march-2020)

**Nvidia daily path through the selloff [RH closes]**
- 6 Oct 239.24 (record close; intraday record 243.37); 16 Oct 214.13; 29 Oct 213.66; 30 Oct 204.64 (-4.2%); 4 Nov 200.13; **5 Nov 181.60 (-9.26%)**; 6 Nov 186.64; 9 Nov 178.67 (-4.3%, 463m shares); 10 Nov 168.89 (-5.5%); 11 Nov 173.73; **12 Nov 166.19 (-4.3%; intraday low 148.80, -14.3%; 748m shares)**; 13 Nov 162.85; 16 Nov 156.14 (-4.1%); **17 Nov 155.46 (-0.44%; intraday low 150.33)**. — [Robinhood NVDA](https://robinhood.com/stocks/NVDA)
- Nvidia's 16 Nov close was its lowest settlement since June 2025, and it was on track for a seventh straight weekly loss. — [TheStreet Pro (search summary)](https://pro.thestreet.com/stock-market-today/2026-11-17#update-wp:31548)
- Huang resigned as CEO (reported 12 Nov session), linked in the report to an alleged affair with a Chinese businesswoman suspected by US authorities of spying; CFO Colette Kress is interim CEO. AMD rose 5.9% and Broadcom 5.5% that day. — [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields)
- The board chairman said there are no plans to reinstate Huang; Huang said on 17 Nov he would be open to returning, which briefly lifted the stock. — [NBC News live blog](https://www.nbcnews.com/business/business-news/live-blog/nvidia-stock-earnings-report-jensen-huang-rcna609804); [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html)
- "Nvidia has lost nearly $1.4 trillion since its October record" (early November) and "$2 trillion market cap loss" (17 Nov options coverage) are both in print; they are the same drawdown measured two weeks apart. — [IBTimes UK](https://www.ibtimes.co.uk/nvidia-loses-market-value-ai-stock-selloff-1830575); [TokenPost](https://www.tokenpost.com/news/investing/59327)
- Nvidia was down 26% over the month into 17 Nov and 14% over the past year. — [24/7 Wall St.](https://247wallst.com/investing/2026/11/17/stock-market-today-nvidias-26-plunge-puts-wall-street-on-edge-ahead-of-earnings-tonight/); [RiskReversal](https://riskreversal.substack.com/p/s-and-p-testing-200-day-nvidia-higher)

**SMH / SOXX / QQQ / SPY / IGV path [RH closes]**
- SMH: 5 Oct 633.90 (autumn closing high); 16 Oct 539.79 (eight straight down sessions 7–16 Oct, -14.7% calc); 28 Oct 567.67; 30 Oct 522.49 (-6.98%); 4 Nov 504.27; **5 Nov 447.73 (-11.2%; low 445.59)**; 9 Nov 487.41; 11 Nov 506.96; 13 Nov 486.75; 16 Nov 461.90; **17 Nov 460.10 (intraday low 445.32, a marginal new low for the move, then recovered)**. — [Robinhood SMH](https://robinhood.com/stocks/SMH)
- SOXX: 29 Oct 171.29; 30 Oct 157.17 (-8.24%); 4 Nov 150.14; **5 Nov 131.90 (-12.2%; low 130.75)**; 9 Nov 146.76 (+7.5%); 11 Nov 155.40 (+6.0%); 13 Nov 149.30; 16 Nov 141.22 (-5.4%); 17 Nov 141.46 (low 136.17). — [Robinhood SOXX](https://robinhood.com/stocks/SOXX)
- QQQ: 6 Oct 759.66 (record close); 4 Nov 691.95; **5 Nov 647.05 (-6.5%)**; 11 Nov 690.38; 16 Nov 661.75; 17 Nov 656.95 (low 646.65, marginally under the 5 Nov low). SPY: 6 Oct 779.09 (record close); 4 Nov 766.81; **5 Nov 733.00 (-4.4%)**; 11 Nov 759.81; 16 Nov 739.95; 17 Nov 732.44 (low 727.00). — [Robinhood QQQ](https://robinhood.com/stocks/QQQ); [Robinhood SPY](https://robinhood.com/stocks/SPY)
- IGV: 12 Oct 111.28 (high 113.70); 28 Oct 111.91; 5 Nov 99.01; 16 Nov 99.00; 17 Nov 95.74 (-3.3%). — [Robinhood IGV](https://robinhood.com/stocks/IGV)
- SOX had eight straight down sessions in October, a 15.7% slide and the longest losing streak since October 2008. — [SimianX (low-quality source, but matches SMH tape)](https://www.simianx.ai/stories/semiconductor-bear-markets-every-sox-crash-1995-2026)
- 5 Nov: Nasdaq-100 fell 6.36% (largest since March 2020); about $2.3tn of Nasdaq-100 market cap was lost, the largest single-day loss in the index's history (Bloomberg Intelligence); Dow fell about 1,800 points; Nasdaq entered correction; Qualcomm -12% on guidance. Reuters put the Nasdaq value loss at about $2.5tn. — [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1); [Yahoo Finance live](https://finance.yahoo.com/markets/live/stock-market-today-thursday-november-5-dow-sp-500-nasdaq-plunge-chip-stocks-melt-down-193726491.html); [YourStory](https://yourstory.com/ai-story/ai-stocks-crash-wall-street-trillion-rout)
- Stated causes of the 5 Nov break: Democrats sweeping House and Senate in the midterms (AI/data-centre regulation fears), doubts about AI capex sustainability and hyperscaler borrowing. Goldman traders: "building will become more expensive, complicated and slower." — [CNBC](https://www.cnbc.com/2026/11/05/the-rotation-out-of-tech-is-becoming-a-risk-for-the-broader-market.html)
- SOXX was down more than 23% in the month to 5 Nov and had closed below its 200-day average four sessions running (BTIG); the Dow was +4.1% and equal-weight S&P +5% over the same month. — [CNBC](https://www.cnbc.com/2026/11/05/the-rotation-out-of-tech-is-becoming-a-risk-for-the-broader-market.html)

**Volatility and options**
- VIX closed **25.45–25.46 on 17 Nov** (+11.1%), intraday high 27.73 (highest since 6 Nov), fourth straight daily gain; it was about 19 at the 13 Nov close. — [TechFlow recap](https://www.techflowpost.com/en-US/article/35453); [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html); [24/7 Wall St.](https://247wallst.com/investing/2026/11/17/stock-market-today-nvidias-26-plunge-puts-wall-street-on-edge-ahead-of-earnings-tonight/)
- SPX one-day expected move for 18 Nov: 1.2%; 85% of names closed lower on 17 Nov; equal-weight RSP -1.4%. — [RiskReversal](https://riskreversal.substack.com/p/s-and-p-testing-200-day-nvidia-higher)
- Nvidia implied post-earnings move: about 8% (Cboe; versus a 4.8% average realised move after the prior four reports); 8.5% (Susquehanna via Reuters, a ~$335bn swing); 7.64% from the at-the-money straddle; 10.3% from the 20 Nov straddle on 13 Nov (SpotGamma, weekly range about $140–172). — [Invezz](https://invezz.com/news/2026/11/17/nvidia-stock-faces-a-300-billion-earnings-gamble-as-options-signal-8-swing/); [Reuters via Investing.com](https://investing.com/news/stock-market-news/nvidia-shares-set-for-335-billion-swing-after-earnings-options-show-5032318); [Seeking Alpha](https://seekingalpha.com/news/4673750-nvidia-shares-brace-for-7-post-earnings-swing-options-market-show); [SpotGamma](https://spotgamma.com/nvidia-earnings-preview-leadership-shock/)

**Nvidia fiscal Q3 results (17 Nov, after the close) and reaction**
- Revenue $115.84bn (+103% y/y) vs $109.1bn consensus; adjusted EPS $2.68 vs $2.48; data-centre revenue $107.6bn vs $101.87bn; non-GAAP gross margin 74.9% vs 74% expected. — [TechFlow recap](https://www.techflowpost.com/en-US/article/35453); [Motley Fool via Yahoo](https://finance.yahoo.com/markets/stocks/articles/stock-market-today-nov-17-222310679.html)
- Q4 revenue guide about $130bn ±3% (excluding China data-centre compute) vs about $125bn consensus; Q4 gross-margin guide 71–72% (down from 74.9%); FY2028 growth outlook raised to 75% from 70%; buyback authorisation raised by $150bn ($227.3bn remaining); $28.1bn repurchased in Q3. — [RiskReversal](https://riskreversal.substack.com/p/s-and-p-testing-200-day-nvidia-higher); [TechFlow recap](https://www.techflowpost.com/en-US/article/35453)
- After-hours reaction, by source and time: about +1.3% early (Motley Fool), about +2% (search summary of CNBC/Yahoo), about +3% (RiskReversal), nearly +4% (TechFlow), nearly +5% (The Fly). Last extended-hours trade at 9:33 pm ET: **$156.88 (+0.9%)** [RH]. — [Motley Fool via Yahoo](https://finance.yahoo.com/markets/stocks/articles/stock-market-today-nov-17-222310679.html); [TipRanks / The Fly](https://www.tipranks.com/news/the-fly/closing-bell-movers-nvidia-up-nearly-5-after-strong-q3-results-guidance-raise-thefly-news); [Robinhood NVDA](https://robinhood.com/stocks/NVDA)
- Other extended-hours prints at about 9:33 pm ET 17 Nov [RH]: SMH 467.01 (+1.5%), SOXX 143.38 (+1.4%), TSM 369.27 (+2.7%), AMD 510.99 (+1.5%), MU 722.00 (+1.3%), AVGO 345.80 (+1.2%), CRWV 51.75 (+3.7%), ORCL 117.85 (+2.5%), QQQ 660.18 (+0.5%), SPY 734.24 (+0.25%), MSFT 508.89 (+0.5%), META 618.70 (flat). — [Robinhood SMH](https://robinhood.com/stocks/SMH)
- Futures on the evening of 17 Nov: Nasdaq-100 +1.4%, S&P 500 +0.8%, Dow +0.3%; CoreWeave, Nebius and Iren were up 8–10% after hours at the peak. — [Stocktwits](https://stocktwits.com/news-articles/markets/equity/s-and-p-500-dow-nasdaq-futures-power-ahead-on-nvidia-outlook-beat-nvda-tsla-ant-in-focus/cNbXjOsR9hh); [TechFlow recap](https://www.techflowpost.com/en-US/article/35453)

### Inferences
- Nvidia market value lost from the 6 Oct record close to the 17 Nov close: (239.24 − 155.46) × 24.598bn shares ≈ **$2.06tn** (from $5.89tn to $3.82tn). The "$2 trillion" headline is accurate as of 16–17 Nov.
- Estimated SOX close on 17 Nov ≈ **9,620–9,670** (SOXX 141.46 × the SOX/SOXX ratio of 68.0–68.4 observed on 4, 5 and 11 Nov), roughly **34% below** the 14,655 record. This is an estimate, not a reported close.
- Estimated record closes for the indices (6 Oct), scaled from SPY and QQQ: S&P 500 ≈ 7,810; Nasdaq-100 ≈ 31,200. Drawdowns from record close: S&P 500 -6.0%, QQQ -13.5%, NVDA -35.0%.
- Quarter-to-date (from 30 Sep closes) [RH calc]: NVDA -31.9% (228.38 → 155.46), SMH -24.5% (609.00 → 460.10), QQQ -11.2% (739.77 → 656.95), IGV -10.1% (106.48 → 95.74), SPY -4.0% (762.63 → 732.44).
- Trend state for thresholds: NVDA, SMH, SOXX, TSM, MU and QQQ are below both the 50- and 200-day averages; AVGO is below its 200-day but back at its 50-day; AMD is the only large semi still well above its 200-day (+18%); IGV is 1.6% above its 200-day; SPY is sitting on it (the gap is within rounding). In every case pulled the 50-day is still above the 200-day (no "death cross" yet in NVDA: 211.76 vs 203.87).
- 17 Nov was a successful intraday retest for SMH and QQQ (marginal undercut of the 5 Nov lows, close well off the low). SOXX and NVDA held above their 5 Nov and 12 Nov lows respectively. Natural reference levels: NVDA 148.80 (12 Nov low) and 181.60 (5 Nov close); SMH 445.3–445.6 (double low) and 524.45 (200-day); QQQ 646.65–647.05 and 682.62; SPY 727.00 and 732.4 (200-day).
- The earnings reaction so far (+0.9% to +5%) is less than the 8% implied move and less than the stock's 16 Nov decline alone, despite a 6% revenue beat and a guide 4% above consensus. The gross-margin guide-down (74.9% → 71–72%) and the unresolved CEO vacancy are the visible offsets.

### Gaps
- No reported SOX closing level for 16 or 17 Nov was found; only the 4/5 Nov closes and the 22 June record are sourced. Whether 14,655 is a closing or intraday record is not stated.
- Dates of the 2026 lows for SOXX (102.42) and TSM (311.70), and the exact day of MU's 294.86 low (inferred 2 Jan) and SMH's 359.86 low (inferred 30–31 Mar), were not pulled.
- 50- and 200-day averages were not pulled for CRWV, ORCL, MSFT, GOOGL, AMZN, META.
- The daily bar for 17 Nov was not yet finalised in the history feed for ETFs, so their moving averages may carry a placeholder for that day; the effect is under 0.05% but SPY's "on the 200-day" reading is within that tolerance.
- No independent breadth series (percent of S&P 500 or Nasdaq members above 50/200-day) was found.
- The reported cause of Huang's resignation rests on one wire report as summarised; I did not verify it against a primary Nvidia filing.

---

## 2. Valuation: forward P/E and price/sales, equity risk premium with the 10-year above 5%, concentration, comparisons to 2000

### Takeaway
The selloff has been a de-rating as much as a price decline: Nvidia trades at roughly **12x forward earnings** (lowest since 2011–12, below the S&P 500's ~17.5–18x), semis at ~14.7x versus 33x a year ago, and the S&P tech sector at ~17x versus 32x at the October 2025 peak. With the 10-year at 5.10%, however, the S&P 500 earnings yield exceeds the Treasury yield by only about half a point.

### Cited Findings
- Nvidia forward P/E: about 12x, lowest since 2012 (Reuters, 12 Nov); 11.7x, lowest since October 2011 (FactSet via TradingKey); 12.9x on 2 Nov versus S&P 500 18.7x, PEG 0.27 (Yahoo); 14x on 12 Nov (Josh Brown); 9.93x on 17 Nov (GuruFocus). — [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields); [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262300737-nvidia-stock-nvda-forward-pe-drops-11-7x-hitting-15-year-low-tradingkey); [Yahoo Finance](https://finance.yahoo.com/markets/stocks/article/nvidia-stock-valuation-gets-torched-by-tech-stock-rout-110145628.html); [Yahoo / Josh Brown](https://finance.yahoo.com/markets/stocks/articles/josh-brown-nvidia-no-jensen-173128136.html); [GuruFocus](https://www.gurufocus.com/term/forward-pe-ratio/NVDA)
- S&P 500 forward P/E: 18.7x on 30 Oct; 17.7x on 5 Nov (lowest in more than three years); about 18x on 10 Nov. Goldman notes it fell from 22x to 19x during 2026. — [AI Bubble Monitor](https://aibubblemonitor.com/analysis/dot-com-bubble-vs-ai-bubble-data-comparison); [Yahoo / Josh Brown](https://finance.yahoo.com/markets/stocks/articles/josh-brown-nvidia-no-jensen-173128136.html); [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1)
- S&P 500 technology sector forward P/E about 17x, down from 32x at the October 2025 peak, and below the index (18x) for the first time since 2017. — [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1)
- Semiconductor forward P/E 14.7x, down from 33x a year earlier (early November). SOX had traded near 28x forward versus a five-year average under 22x earlier in the cycle. — [Benzinga (search summary, page 403)](https://www.benzinga.com/etfs/sector-etfs/26/11/62779160/semiconductor-stocks-are-cheaper-than-the-sp-500-is-it-time-to-buy-soxx-and-smh-etfs); [SimianX](https://www.simianx.ai/stories/every-fed-rate-hike-cycle-since-1983)
- Trailing P/E from the data feed on 17 Nov [RH]: NVDA 19.7, AMD 109.6, AVGO 42.6, TSM 24.0, MU 9.7, MSFT 27.1, GOOGL 14.8, AMZN 20.8, META 21.4, ORCL 18.7; ETFs: SMH 31.2, SOXX 30.6, QQQ 29.9, SPY 25.4, IGV 45.8. Price/book: NVDA 16.5, SMH 9.8, QQQ 8.1, SPY 5.4. — [Robinhood NVDA](https://robinhood.com/stocks/NVDA); [Robinhood SMH](https://robinhood.com/stocks/SMH)
- SOXX trailing P/E was 43 at the start of October. — [Motley Fool](https://www.fool.com/investing/2026/10/02/why-the-ishares-semiconductor-etf-gained-11-in-september/)
- Tech is 37% of S&P 500 market cap (5 Nov), above the 2000 peak share. — [CNBC](https://www.cnbc.com/2026/11/05/the-rotation-out-of-tech-is-becoming-a-risk-for-the-broader-market.html); [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1)
- Top-10 share of the S&P 500: about 36% in mid-2026 after a 41% peak in 2025; Goldman-attributed range 38–41%, versus about 27% at the 2000 peak; Magnificent 7 about 31%; top 10 are 38% of cap but 28% of earnings. — [Walnut](https://walnutinvest.com/stats/market-concentration-statistics); [Mavros Group](https://www.mavrosgroup.com/insights/how-concentrated-the-sp-has-become)
- 2000 comparison: S&P 500 forward P/E 24.4 on 24 Mar 2000 versus 18.7 on 30 Oct 2026; largest company Cisco $579bn then versus Nvidia about $4.99tn on 3 Nov 2026. — [AI Bubble Monitor](https://aibubblemonitor.com/analysis/dot-com-bubble-vs-ai-bubble-data-comparison)
- Goldman (Snider): AI has lifted S&P 500 earnings 25% above trend and drives about half of 2026 index earnings growth; the bear case (5,600) assumes earnings revert to the 30-year trend and the P/E to its 30-year average of 17x. — [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/); [MLQ](https://mlq.ai/news/goldman-sachs-sees-the-sp-500-at-8700-by-the-end-of-2027-as-earnings-growth-slows/)

### Inferences
- Simple equity risk premium (forward earnings yield minus 10-year yield): at 17.7x the earnings yield is 5.65%; against a 5.10% 10-year that leaves **about +0.55pp**. Using Morgan Stanley's $420 2027 EPS on 7,340.53 gives 17.5x, a 5.72% yield and about +0.62pp. At the 6 Oct peak (S&P ≈ 7,810, 10-year 5.31% the day before, forward P/E ≈ 19x) the same measure was roughly zero or slightly negative. The de-rating has restored a small positive premium; it has not restored a normal one.
- Nvidia price/sales: about 8.3x on annualised Q3 revenue ($3.82tn / $463bn) and about 7.4x on the annualised Q4 guide ($520bn). A trailing-four-quarter figure is roughly 10–11x, but two of the four quarterly revenues are from secondary reports ($96.2bn and $81.6bn) and one from memory, so treat it as approximate.
- The valuation picture and the 2000 analogy pull apart: concentration and sector weight exceed 2000, but multiples are far below 2000 (index 17.5–18x versus 24.4x; the leader at 12x forward). The bear case in print (Goldman 5,600) is an *earnings* reversion story, not a multiple story.
- Nvidia's gross-margin guide (71–72%) is the first hard datapoint for the "earnings above trend" risk that the valuation debate now turns on.

### Gaps
- No sourced forward P/E for the Magnificent 7 as a group, and no sourced price/sales for SMH/SOX or the S&P 500.
- No strategist-published equity risk premium figure was found; the numbers above are my arithmetic.
- Forward P/E readings for Nvidia range from 9.9x to 14x across providers and dates; none post-dates the 17 Nov guidance, which will lower them further once estimates rise.
- Concentration figures come from low-authority aggregators and are not dated to November; no S&P Dow Jones or Goldman primary figure for mid-November was retrieved.
- No FactSet Earnings Insight page for mid-November was retrieved.

---

## 3. Positioning and flows: 13F, prime-broker data, retail, ETF flows, options, margin debt, surveys

### Takeaway
Fast money has already cut hard: the November BofA survey shows the largest one-month fall in tech allocation since 2006 (net overweight 37% → 12%) and Goldman's prime book saw near-record tech selling into 6 Nov, with gross leverage falling more than net. But cash is only 3.6%, semis are still named the most crowded trade, margin debt is 3% off its record, and the Q3 13Fs show marquee funds *adding* Nvidia at about $228 a share just before a 32% fall.

### Cited Findings

**BofA Global Fund Manager Survey, November 2026 (survey 6–12 Nov, published 17 Nov)**
- Net tech overweight fell to 12% from 37% in October, the largest one-month drop since June 2006. — [Startup Fortune (citing Fortune/Bloomberg)](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/); [KuCoin news](https://www.kucoin.com/news/flash/bank-of-america-survey-shows-fund-managers-cut-tech-exposure-at-fastest-pace-since-2006)
- Average cash 3.6% ("uber-low"). — [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/); contradicted by a Yahoo piece on Hartnett citing cash above 4.2%, up from 3.9% — [Yahoo Finance](https://finance.yahoo.com/markets/articles/bofa-hartnett-says-stay-risk-111032299.html)
- Most crowded trade: semiconductors, 39% of respondents (October: 45%). — [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/); [FI Desk (October survey)](https://www.fi-desk.com/?p=26786)
- Biggest tail risk: "AI bubble" 34%; "AI hyperscaler credit event" 31%. 38% name hyperscaler bonds as the most likely source of a credit event. — [Seeking Alpha](https://seekingalpha.com/news/4673758-ai-bubble-emerges-as-top-market-tail-risk-in-bofa-survey); [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/)
- 52% expect at least one hyperscaler to announce a capex cut within six months; a record 38% say companies are overinvesting; 16% want more capex (lowest since May 2020); 3% predict recession. — [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/)
- Hartnett called the mood "euphoria on boom & AI over", said the survey did not show enough fear to buy, and would stay risk-off until the 10-year is below 4.5% and oil below $70. — [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/); [Yahoo Finance](https://finance.yahoo.com/markets/articles/bofa-hartnett-says-stay-risk-111032299.html)
- October 2026 survey: 45% expected an AI bubble to form in 2027, 42% did not. July 2026: long semis most crowded for a third month. — [FI Desk](https://www.fi-desk.com/?p=26786)
- For reference, "long Magnificent 7" (54%) as most crowded and "AI bubble" (45%) as top tail risk are the **November 2025** survey. — [InvestingLive](https://investinglive.com/news/bofa-fms-ai-bubble-biggest-tail-risk-for-45-of-respondents-20251118/amp); [ROIC.ai](https://www.roic.ai/news/long-magnificent-seven-is-most-crowded-trade-bofa-survey-says-11-18-2025)

**13F filings for Q3 2026 (positions as of 30 Sep; filed by 16 Nov)**
- Appaloosa (Tepper): Nvidia +31% to 2.0m shares (from 1.53m); Micron +28% to 1.25m shares, now the largest holding; trimmed Alphabet and Amazon. — [MLQ 13F roundup](https://mlq.ai/news/13f-roundup-tepper-adds-micron-and-nvidia-loeb-buys-meta-viking-halves-meta-and-lone-pine-buys-amazon-and-intel/)
- Third Point (Loeb): new Nvidia stake of 1.5m shares ($342.6m at quarter-end); re-added Meta (655k shares, about 10.5% of a $4.59bn book, now the top holding) and Microsoft; exited Amazon and most of Alphabet; about $1.05bn of new Meta/Nvidia/Microsoft in total. — [Benzinga](https://www.benzinga.com/markets/large-cap/26/11/63365903/billionaire-daniel-loeb-swaps-amazon-for-meta-nvidia-and-microsoft-in-q3-meta-now-third-points-top-holding); [FourWeekMBA](https://fourweekmba.com/ai-third-point-opened-1-05b-of-meta-nvidia-microsoft-stakes/)
- Viking halved Meta; Lone Pine bought Amazon and Intel; Tiger Global added Nvidia. — [MLQ 13F roundup](https://mlq.ai/news/13f-roundup-tepper-adds-micron-and-nvidia-loeb-buys-meta-viking-halves-meta-and-lone-pine-buys-amazon-and-intel/); [KuCoin news](https://www.kucoin.com/news/flash/2026-q3-13f-filings-reveal-major-institutional-divergence-on-nvidia-and-tech-stocks)
- Bridgewater cut Nvidia to 2.69m shares from 3.87m; Soros and Druckenmiller reduced Nvidia and semis; one aggregator has Renaissance cutting Nvidia 99.7%. — [KuCoin news](https://www.kucoin.com/news/flash/2026-q3-13f-filings-reveal-major-institutional-divergence-on-nvidia-and-tech-stocks)
- Morgan Stanley's Erik Woodring: Nvidia was the most under-owned large-cap tech stock at the end of Q3. — [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html)

**Prime-broker and futures flow**
- Week to 15 Oct (Goldman prime book): hedge funds sold tech at the fastest pace in a decade; semis saw the heaviest dollar selling; net leverage fell to 48.6%, a one-year low; tech was still 23.5% of net exposure, in the 90th percentile of five years. — [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/hedge-funds-dumped-tech-stocks-133527326.html)
- Week to 6 Nov: tech selling near the highest pace since 2016; gross leverage fell far more than net; funds ended the week net buyers on Friday short covering in index and ETF macro products. — [24/7 Wall St.](https://247wallst.com/investing/2026/11/10/hedge-funds-dumped-tech-at-a-near-record-pace-right-before-chip-stocks-jumped-7/); [Quartz](https://qz.com/hedge-funds-tech-stocks-near-record-pace-midterms-110926)
- 5 Nov: about $11bn of S&P 500 futures sold net in the first 90 minutes (JPMorgan derivatives); more than $60bn of late-session leveraged-ETF selling, about 90% in tech products. — [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1)

**ETF flows**
- Flows reported 10 Nov: SOXX about -$4.1bn, SMH about -$1.0bn, SPY -$4.2bn, QQQ +$2.4bn. — [Yahoo Finance ETF flows](https://finance.yahoo.com/markets/options/articles/etf-fund-flows-nov-10-235434793.html)
- A 16 Nov roundup shows SOXX -$3.16bn and SMH +$1.73bn one-day, with assets of $38.06bn and $64.44bn (attribution from a search summary, not page-verified). — [Investing.com](https://www.investing.com/news/stock-market-news/best-semiconductor-etfs-smh-leads-on-cost-liquidity-and-momentum-93CH-5030811)
- SOXX had a $1.4bn week-over-week outflow in early October. — [ETF Channel](https://www.etfchannel.com/article/202610/soxx-sees-1-4-billion-etf-outflow-as-semiconductor-holdings-weaken-SOXX10062026outflow.htm/)

**Options, retail, leverage**
- Nvidia put skew: the $120 put for 20 Nov traded near 111% implied volatility versus a 90th-percentile reference near 98% (13 Nov). Put/call open interest 0.87, down from a one-year high of 1.02 two weeks earlier; another source has 0.66. — [SpotGamma](https://spotgamma.com/nvidia-earnings-preview-leadership-shock/); [Reuters via Investing.com](https://investing.com/news/stock-market-news/nvidia-shares-set-for-335-billion-swing-after-earnings-options-show-5032318)
- Retail: bearish put purchases were 32% of retail opening trades on Cboe exchanges on 12 Nov versus a 21% year-to-date average. — [Invezz](https://invezz.com/news/2026/11/17/nvidia-stock-faces-a-300-billion-earnings-gamble-as-options-signal-8-swing/)
- FINRA margin debt about $1.45tn in October (-2% m/m, +22% y/y); record about $1.50tn in June; July saw the largest one-month dollar fall on record; September $1.48tn. Margin debt about 4.4% of GDP versus a 4.6% record. — [TheTrading.tools](https://www.thetrading.tools/margin-debt); [CMG Private Wealth](https://www.cmgprivatewealth.com/omr/oct232026); [GuruFocus](https://www.gurufocus.com/economic_indicators/4266/finra-investor-margin-debt-relative-to-gdp)
- Nvidia volume on 17 Nov was 345m shares, 127% above its three-month average; 748m shares traded on 12 Nov. — [Motley Fool via Yahoo](https://finance.yahoo.com/markets/stocks/articles/stock-market-today-nov-17-222310679.html); [Robinhood NVDA](https://robinhood.com/stocks/NVDA)

### Inferences
- The 13F data is six to seven weeks stale and pre-dates the entire break. Loeb's reported $342.6m for 1.5m shares implies $228.4 a share, which is Nvidia's 30 Sep close; those positions were 32% under water at the 17 Nov close if held. The filings are evidence of where long-only style hedge funds were positioned at the top, not of current buying.
- Positioning has shifted from a tail-wind to a mixed signal. Evidence of capitulation: tech overweight at 12%, record-pace prime-book selling, gross de-leveraging, retail put buying, SOXX redemptions. Evidence against a washout: cash at 3.6% (below BofA's 4% contrarian sell threshold), semis still the most crowded trade at 39%, tech still at the 90th percentile of prime-book exposure in mid-October, margin debt only 3% below record, SMH still taking inflows while SOXX bleeds.
- The survey's centre of worry has moved from equity valuation to credit: "hyperscaler credit event" (31%) is nearly level with "AI bubble" (34%), and a majority expects a capex cut within six months. A capex-cut announcement is therefore partly expected, which matters for how much it would move prices.
- The SMH/SOXX flow split (SMH in, SOXX out) is consistent with SMH's heavier Nvidia/TSMC weight attracting dip buyers while the broader equal-ish SOXX basket is sold; this is a hypothesis, not a sourced finding.

### Gaps
- No November short-interest data for Nvidia, SMH or semis was found.
- No Vanda or other retail net-purchase series for November was found; the only retail datapoint is the Cboe put share.
- The cash-level conflict (3.6% versus above 4.2%) is unresolved; three outlets carry 3.6%.
- No Goldman prime-book reading after 6 Nov, and nothing covering the 12–17 Nov leg.
- No November FINRA release exists yet (October is the latest); figures are from aggregators, not FINRA's file.
- 13F share counts are from press roundups, not EDGAR.
- Survey participant count and AUM for November were not found.

---

## 4. Strategist 2027 outlooks published in November 2026

### Takeaway
Goldman Sachs, Morgan Stanley and Barclays all sit at **8,700** for end-2027 (about 18.5% above the 17 Nov close), with Wells Fargo the low at 8,200; the bullish cases rest on earnings growth of 14–18% in 2027 with AI capex still rising but decelerating, and both Goldman and Morgan Stanley published into the selloff rather than before it.

### Cited Findings
- Morgan Stanley (Mike Wilson), 16 Nov: end-2027 S&P 500 target 8,700; S&P 500 EPS $420 in 2027 versus an estimated $369 in 2026; global equities moved to "maximum overweight"; gold target $5,250. — [Yahoo / TheStreet](https://finance.yahoo.com/markets/stocks/articles/morgan-stanley-resets-p-500-220300784.html); [InvestingLive](https://investinglive.com/stock-market-update/more-from-morgan-stanley-8-700-s-p-target-and-5-250-gold-lead-its-2027-outlook/); [BigGo Finance](https://finance.biggo.com/news/109742f4-038e-48b0-8149-f862ae796d77)
- Earlier in the selloff (about 10 Nov) Wilson gave a downside range of 7,100–7,300 with his 8,000 year-end 2026 target unchanged; Morgan Stanley separately projected another 10–15% fall for semis with the correction ending mid-November. — [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1); [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262240448-philadelphia-semiconductor-index-sox-forecast-morgan-stanley-expects-decline-tradingkey)
- Goldman Sachs (Ben Snider), published 13 Nov and reported 17 Nov: 8,700 for end-2027 (a 17% gain from about 7,315); S&P 500 earnings growth 18% in 2027 after 30% in 2026, slowing further in 2028; bull case 9,400, bear case 5,600; biggest risk is earnings "in both directions"; favours hyperscalers, "buyback aristocrats", energy infrastructure, with health care and staples for diversification. — [MLQ (citing CNBC/Bloomberg)](https://mlq.ai/news/goldman-sachs-sees-the-sp-500-at-8700-by-the-end-of-2027-as-earnings-growth-slows/)
- A second report gives Goldman's earnings growth path as 11% in 2027 from 36%, and "AI capex peaks". — [BigGo Finance](https://finance.biggo.com/news/fede9441-d851-4b6c-b8d5-102788f13770)
- Goldman on AI capex: hyperscaler capex about $1.4tn in 2027, up 58%; its contribution to earnings growth turns negative by 2028. — [Startup Fortune](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/)
- Wells Fargo: 8,200 for end-2027, the lowest on the Street; Barclays (Venu Krishna): 8,700, trimmed from 8,800. — [Seoul Economic Daily](https://en.sedaily.com/world/2026/11/18/wall-street-splits-on-2027-outlook-wells-fargo-sees-8200)
- Sell-side stance during the rout: Morgan Stanley, UBS and HSBC said buy the dip; Citi downgraded global and US tech to neutral. Jefferies: after S&P 500 drops of more than 4% in a day, the average gain over the next six months is 11.9%. UBS (Hoffmann-Burchardi, 17 Nov): the selloff does not yet signal lasting AI-cycle deterioration. — [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1); [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html)

### Inferences
- From the 17 Nov close of 7,340.53: 8,700 is +18.5%, 8,200 is +11.7%, Goldman's bull 9,400 is +28.1% and bear 5,600 is -23.7%.
- Morgan Stanley's numbers imply 2027 EPS growth of 13.8% ($369 → $420) and a target multiple of 20.7x 2027 EPS, about three turns above today's ~17.5x. The target therefore needs re-rating as well as earnings, with the 10-year at 5.1% and the Fed hiking. That is the assumption most exposed to the rates path.
- Goldman's own framing makes the distribution wide and earnings-driven: its bear case is larger in absolute terms (-24%) than its base-case upside (+17–18%), and it expects the AI-capex earnings contribution to turn negative in 2028. The base case is an explicit bet that capex decelerates (58% growth) rather than contracts.
- The published targets do not conflict with the BofA survey's 52% expecting a hyperscaler capex cut within six months, but they do not incorporate one.

### Gaps
- Morgan Stanley's bull/bear cases, multiple assumption, rates assumption and sector calls were not retrievable (TheStreet 403); the "maximum overweight" detail comes from headlines and summaries.
- Goldman's absolute EPS figures were not found, and its 2027 growth number conflicts across reports (18% versus 11%).
- No November 2027-outlook figures were found for JPMorgan, BofA, Citi, UBS or Deutsche Bank.
- No strategist note was found that explicitly models the equity risk premium with a 5% 10-year.

---

## 5. Rates: Fed path, Treasury yields, dollar, inflation, and how semis and long-duration tech behave in such regimes

### Takeaway
The Fed is in a hiking cycle (3.75–4.00% after 16 Sep; a 10–2 hold on 28 Oct with both dissents for a hike) and a 25bp December hike is about 95% priced, with officials talking of several more by spring 2027; the 10-year is 5.10%, the 2-year 4.81%, the 30-year 5.46%. In 2026 itself, semis *rallied* through the September hike and the first break above 5%, and peaked within a day of the 10-year's 5.31% cycle-high close; the autumn selloff was triggered by AI-specific and political news while yields were slightly *below* their highs.

### Cited Findings

**Policy**
- 16 Sep: FOMC raised the funds rate 25bp to 3.75–4.00%, unanimously (12–0), the first hike since 2023; interest on reserves 3.90%. The median projection had 4.1% at end-2026 and no change in 2027; 16 of 18 participants expected one more hike this year. CPI was 3.4% y/y in July. — [Federal Reserve minutes](https://www.federalreserve.gov/monetarypolicy/fomcminutes20260916.htm); [Raisin](https://www.raisin.com/en-us/news/fed-rate-decision-policy-breakdown-september-2026/)
- 28 Oct: held at 3.75–4.00% by 10–2; Lisa Cook and Beth Hammack dissented in favour of a 25bp hike. Chair Kevin Warsh gave no guidance for December. — [Federal Reserve statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm); [456x Research](https://456xresearch.substack.com/p/fed-holds-rates-steady-as-two-dissent)
- December (8–9 Dec) pricing: about 77% after the jobs report (7 Nov); 88.8% for 25bp plus 11.2% for 50bp after CPI (10 Nov, from about 72% a week earlier); 29bp priced on 12 Nov; **95% for 25bp on 17 Nov** (95.7% / 4.3% for 50bp). — [24/7 Wall St.](https://247wallst.com/investing/2026/11/07/odds-of-a-december-rate-hike-jump-to-77-after-a-blowout-jobs-report/); [Investing.com](https://www.investing.com/news/economy-news/fed-rate-hike-odds-in-december-at-88-after-hot-cpi-cme-fedwatch-5017585); [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields); [CNBC](https://cnbc.com/2026/11/17/treasury-yields-bonds-inflation.html); [FXStreet](https://www.fxstreet.com/news/indonesian-rupiah-gains-as-us-dollar-weakens-amid-treasury-sell-off-202611170544)
- Fed speakers: Musalem (17 Nov) said the economy "will likely require several interest rate increases before the spring of 2027", possibly as many as four; Waller said the Fed "ought to hike rates in December"; Paulson backed "further gradual tightening"; Williams (7 Oct) saw "no need for urgency". FOMC minutes are due 18 Nov at 2 pm ET. — [CNBC](https://cnbc.com/2026/11/17/treasury-yields-bonds-inflation.html); [Investing.com](https://www.investing.com/news/economy-news/fed-rate-hike-odds-in-december-at-88-after-hot-cpi-cme-fedwatch-5017585); [Yahoo Finance](https://finance.yahoo.com/economy/policy/article/the-fed-was-unanimous-about-raising-rates-in-september-economic-signals-have-since-changed-184839972.html)

**Yields and dollar**
- 17 Nov: 2-year 4.806% (-2bp); 10-year 5.10–5.11% (-1 to -2bp); 30-year 5.46–5.47%. — [CNBC](https://cnbc.com/2026/11/17/treasury-yields-bonds-inflation.html); [TechFlow recap](https://www.techflowpost.com/en-US/article/35453)
- 12 Nov: 2-year 4.867% (+14bp, highest since 14 Oct); 10-year 5.105% (+11.6bp, highest since 21 Oct). 13 Nov: 10-year closed 5.15%, the highest in a month. — [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields); [Admiral Markets](https://admiralmarkets.com/analytics/traders-blog/fed-december-rate-hike-treasury-yields-retail-sales)
- 10-year history: touched 5.012% intraday on 14 Sep (first time since 2023, from a 4.938% close); closed 5.01% on 21 Sep; hit 5.1% on 23 Sep (first in 19 years); 5.23% in late September; **5.31% close on 5 Oct** (cycle high cited); 5.13% on 21 Oct; back to a 5.05% close on 28 Oct after the hawkish hold. — [24/7 Wall St. (14 Sep)](https://247wallst.com/investing/2026/09/14/10-year-treasury-yield-just-passed-5-heres-what-happened-to-the-market-when-the-same-thing-happened-in-2007/); [CNN](https://www.cnn.com/2026/09/23/investing/us-bond-market-fed); [24/7 Wall St. (29 Oct)](https://247wallst.com/investing/2026/10/29/the-10-year-treasury-yield-just-jumped-back-above-5/)
- Dollar index 103.18 on 12 Nov, a 19-month high; euro $1.1053; dollar/yen 159.85. — [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields)

**Inflation and activity**
- October CPI (released 10 Nov): +0.4% m/m versus about 0.3% expected; core +0.3% for a third straight month. BLS published **no official year-on-year rate** because October 2025 prices were not collected during the shutdown. Estimates: BofA 3.8% headline / 2.7% core; EY 4.1% / 2.8%; KPMG 4.2% (after 3.7% in September); Cleveland Fed nowcast 3.7% / 2.5%. — [CNBC](https://www.cnbc.com/2026/11/10/cpi-inflation-report-october-2026.html); [KPMG](https://kpmg.com/us/en/articles/2026/october-2026-cpi.html); [EY](https://www.ey.com/en_us/insights/strategy/macroeconomics/cpi-report); [Kitco](https://kitco.com/opinion/2026-11-17/silver-paying-rate-rise-has-not-happened-yet)
- October retail sales +0.2% m/m (in line), ex-autos and gasoline +0.6% versus 0.4%; import prices +1.1% versus 0.7%; NAHB index 25 from 29. — [CNBC](https://cnbc.com/2026/11/17/treasury-yields-bonds-inflation.html); [TechFlow recap](https://www.techflowpost.com/en-US/article/35453)
- Context only: Brent settled $93.14 and WTI $86.01 on 17 Nov; gold $3,877 on 12 Nov; the US-Israeli war with Iran began in February. — [TechFlow recap](https://www.techflowpost.com/en-US/article/35453); [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields)

**How semis behaved around the 2026 rate events [RH closes for SMH]**
- 14 Sep (10-year first touches 5%): SMH 541.50, -4.75% from 568.53 on 11 Sep; leveraged SOXL fell about 17% as stocks fell on rate-hike fears. — [Robinhood SMH](https://robinhood.com/stocks/SMH); [FN News](https://en.fnnews.com/news/202609150523068826)
- 16 Sep (hike day): SMH 545.56 (+0.6%); 17 Sep 560.61; 18 Sep 573.00; 22 Sep 607.46; 5 Oct 633.90. — [Robinhood SMH](https://robinhood.com/stocks/SMH)
- SOXX gained 11% in September despite the hike (Intel +34%, AMD +30%, Micron +11%, Nvidia +3%, Broadcom -5%), driven by Meta's "Muse" AI agent reviews and Micron's 1 Oct report; a cooler jobs report on 2 Oct lowered October hike odds. — [Motley Fool](https://www.fool.com/investing/2026/10/02/why-the-ishares-semiconductor-etf-gained-11-in-september/)
- 28 Oct (hawkish hold, two dissents): SMH 567.67 (+1.7%); 29 Oct 561.67; 30 Oct 522.49 (-7.0%). — [Robinhood SMH](https://robinhood.com/stocks/SMH)
- Rate-sensitive defensives fell with the yield surge: XLU made its 52-week low (39.03) on 29 Sep [RH]. — [Robinhood XLU](https://robinhood.com/stocks/XLU)

**Historical reference classes (low-authority sources; use as orientation only)**
- SOX fell about 46% from December 2021 to October 2022 during the last hiking cycle (S&P 500 about -25%); in 2018 SOX fell about 26% versus 19.8% for the S&P 500. — [SimianX](https://www.simianx.ai/stories/every-fed-rate-hike-cycle-since-1983)
- The same source says SOX beat the S&P 500 during the 1994, 1999 and 2015 hiking cycles, lagged in 2004–06, and that the median SOX bear market since 1995 is about -38%. — [SimianX](https://www.simianx.ai/stories/semiconductor-bear-markets-every-sox-crash-1995-2026)

### Inferences
- From the hike-day close to the 5 Oct close SMH gained 16.2% (545.56 → 633.90) while the 10-year rose from about 5.0% to 5.31%. In 2026 the direct rates-to-semis link was weak-to-wrong-signed for three weeks; the one clean rate shock (14 Sep) cost 4.75% in a day and was fully recovered in three sessions.
- The top coincided with the yield high (10-year 5.31% close on 5 Oct; NVDA/QQQ/SPY records on 6 Oct), and the first leg down (7–16 Oct) came with yields *falling* as money moved into Treasuries. Rates look like a ceiling on multiples and a reason dips are not being bought aggressively, not the trigger.
- The current SOX drawdown (-38.5% at the 5 Nov close; about -34% now, from 22 June) is already at the cited median semi bear market. The 2022 hiking-cycle analogue (-46%) would be roughly SOX 7,900, or SMH about 363 measured from the 671.83 high (calc), which is close to the March 2026 low of 359.86.
- The curve is 2s10s about +30bp and 10s30s about +36bp. A December hike is fully priced; the live rates risk for equities is the *count* of further hikes (Musalem's "several", the two October dissents) and any 50bp talk, which rose to 11% on 10 Nov and has faded to about 4%.
- Because there is no official October CPI year-on-year figure, any framework threshold tied to "headline CPI y/y" needs to specify whose estimate (range 3.7–4.2%).
- The dollar at a 19-month high and the yen near 160 are additional tightening of global financial conditions that non-US holders of the AI trade face.

### Gaps
- No single authoritative close series for 2-, 10- and 30-year yields on each day was retrieved; levels are from wire reports and may be intraday snapshots. The 13 Nov 10-year (5.15%) and 12 Nov (5.105%) come from different sources.
- A dollar-index sidebar reading of 103.54 (undated, around 10 Nov) conflicts with "103.18, a 19-month high" on 12 Nov; no 17 Nov DXY level was found.
- No pricing for meetings beyond December (January, March 2027) was found; "several more hikes" is Fed-speak, not a market-implied path.
- The historical reference-class numbers come from an AI-generated explainer site; no primary index study was retrieved. No reliable 1999–2000 SOX figures were found.
- I did not find a published regression or strategist study of semis versus real yields for 2026.

---

## 6. The rotation narrative: tech to defensives, software, hardware versus power/utilities

### Takeaway
The rotation is real and large: Morgan Stanley's derivatives desk calls the quarter-to-date move into defensives the biggest in 25 years (staples, health care, utilities up an average 13% while the Nasdaq-100 fell 13%). It is strongest in staples and health care; utilities have only recovered their September rate-driven losses, and software, which had been a relative refuge versus hardware until late October, broke down on 17 Nov.

### Cited Findings
- "A generational flight from tech to defensive stocks is underway" (CNBC Investing Club, 17 Nov). Morgan Stanley's derivatives group: Q4 to date is the largest rotation into defensives in 25 years; staples, health care and utilities up an average 13% while the Nasdaq-100 fell 13%. — [CNBC Investing Club](https://www.cnbc.com/investingclub/2026/11/17/a-generational-flight-from-tech-to-defensive-stocks-is-underway-how-were-capitalizing.html)
- Over the month to about 11 Nov, health care (+7%) and staples (+6%) were the two best S&P sectors versus nearly -3% for the index; Johnson & Johnson is the emblem; Citi called it a "violent rotation" but still sees defensives beating cyclicals next year; defensive valuations are now described as stretched. — [CNBC](https://www.cnbc.com/2026/11/11/tech-selloff-defensive-pivot.html); [CNBC Investing Club (Cramer)](https://www.cnbc.com/investingclub/2026/11/16/jim-cramer-says-jj-is-a-metaphor-for-whats-working-in-the-stock-market.html)
- ByteTree: "a once-in-a-generation rotation in stockmarkets." — [ByteTree](https://www.bytetree.com/research/2026/11/a-once-in-a-generation-rotation-in-stockmarkets/)
- Index-level risk: with tech at 37% of the S&P 500, rotation is a net drag on the index even when the average stock rises. — [CNBC](https://www.cnbc.com/2026/11/05/the-rotation-out-of-tech-is-becoming-a-risk-for-the-broader-market.html)
- XLP [RH]: 80.53 on 2 Oct → 91.46 on 17 Nov (+13.6%); 52-week high 93.48 on 16 Nov. XLU [RH]: 52-week high 47.80 on 27 Feb, 52-week low 39.03 on 29 Sep, 43.42 on 17 Nov (+11.2% off the low, still 9% below the February high). — [Robinhood XLP](https://robinhood.com/stocks/XLP); [Robinhood XLU](https://robinhood.com/stocks/XLU)
- Second-half reference closes [RH, weekly bars]: on 26 June SMH 611.61, MU 1,132.33, XLU 46.20, XLP 84.71. To 17 Nov: SMH -24.8%, MU -37.1%, XLU -6.0%, XLP +8.0% (calc). — [Robinhood SMH](https://robinhood.com/stocks/SMH); [Robinhood MU](https://robinhood.com/stocks/MU)
- Software on 17 Nov: IGV -3.2% to -3.3%; Salesforce -9.45% to $194.52 (worst in the S&P 500); Intuit -7.2%; ServiceNow -6.5%; Microsoft about -2%; IBM -4.7%. — [TechFlow recap](https://www.techflowpost.com/en-US/article/35453); [Benzinga](https://www.benzinga.com/markets/equities/26/11/63359152/stock-market-today-salesforce-software-selloff-anthropic-ipo-nvidia-november-17)
- Reasons given: fear that AI agents shrink paid seat counts; funds raising cash ahead of the Anthropic IPO, expected to price on the night of 18 Nov and raise up to $64bn; a new OpenAI model; inflation. Art Hogan attributed the day's broader drawdown to a pile-up of headlines including an NSA outage, an FAA ground stop and a Microsoft Outlook outage. — [MLQ](https://mlq.ai/news/salesforce-and-servicenow-fall-as-software-stocks-slide-again-a-day-before-anthropic-prices-its-ipo/); [Benzinga](https://www.benzinga.com/markets/equities/26/11/63359152/stock-market-today-salesforce-software-selloff-anthropic-ipo-nvidia-november-17); [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html)
- Hardware winners year-to-date before the break (as of 10 Nov): SanDisk about +250%, Dell about +160%, Micron about +140%. — [BigGo Finance](https://finance.biggo.com/news/88a8f70b-deee-4a5c-9594-d86d0a1f14b1)
- AI-financing names: CoreWeave -63.9% and Oracle -54.0% from their May/June highs, both making 2026 lows on 5–6 Nov [RH]; CoreWeave's 10 Nov results eased AI-trade worries for a day. — [Robinhood CRWV](https://robinhood.com/stocks/CRWV); [Robinhood ORCL](https://robinhood.com/stocks/ORCL); [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields)
- Microsoft made its 52-week high on 4 Nov (559.15) and its 52-week low on 25 June (349.20), the mirror image of the semis, which peaked 22–25 June [RH]. — [Robinhood MSFT](https://robinhood.com/stocks/MSFT)
- China tech: KWEB at its lowest since November 2022, down more than 33% year-to-date; Alibaba -7.1% on 12 Nov. — [CNBC](https://www.cnbc.com/2026/11/16/stock-market-today-live-updates.html); [Reuters via NST](https://www.nst.com.my/amp/business/corporate/2026/11/1576568/wall-street-ends-lower-nvidia-ceo-resigns-us-yields)

### Inferences
- There have been two rotations in 2026, not one. From late June, money left semis/memory for software and megacap platforms (MSFT low 25 June → high 4 Nov; IGV high 12 Oct). From October, money left the whole AI complex for staples and health care. Software's 17 Nov break (IGV from 111.91 on 28 Oct to 95.74, -14.4% calc) suggests the first refuge has now failed too.
- The within-AI ranking by drawdown from 2026 highs is a financing-risk ordering: neocloud and levered builders worst (CRWV -64%, ORCL -54%), then memory (MU -43%), then Nvidia and the semi indices (-31% to -36%), then foundry and AMD (-24% to -26%), then software (-16%), then cash-rich platforms (MSFT -9.5%, AMZN -10%). That matches the BofA survey's shift toward "hyperscaler credit event" as a tail risk.
- "Power/utilities as an AI beneficiary" is not visible in XLU: it is down 6% in the second half and 9% below its February high, having behaved as a rate-sensitive bond proxy in September. The defensive bid since October is in staples and health care first. I did not pull independent power producers or electrical-equipment names, which may differ.
- The rotation is price-insensitive on both sides according to the coverage (defensives "quite high", tech multiples at multi-year lows), which is the usual condition late in a rotation; but with the 10-year at 5.1% and a hike priced, the catalyst for reversal would have to come from AI-specific news (Nvidia's print, capex guidance, the Anthropic IPO reception) rather than from rates relief.

### Gaps
- No sector-ETF levels were pulled for health care (XLV), independent power producers, or electrical equipment, and no second-half total-return table by sector from a single source was found.
- No reporting was found linking the software selloff to "AI misuse"; outages appear only as one strategist's colour.
- The "largest rotation in 25 years" claim is Morgan Stanley's as relayed by CNBC; the underlying measure was not available.
- The Anthropic IPO size and timing are from market-wrap coverage, not a filing.
- Whether the post-earnings bounce in semis holds through the 18 Nov cash session is unknown at the time of writing.
