# News-informed forecast of AI prints: first run (18 Nov 2026 UTC, 17 Nov PT)

Rules fixed before any forecast: `data/news_forecast/PREREG.md` (commit `b4fe670`). Packets
`data/news_forecast/packets/`, forecasts `data/news_forecast/forecasts.json`, scores `data/news_forecast/results.json`
(`python tools/news_forecast.py score`). Not wired into the ledger, the timeline or any call.

## Result: on next-quarter guides it beat the mechanical model and matched consensus on the median
17 reports, 1 Aug to 17 Nov 2026. Median absolute miss on the next-quarter guide midpoint (mean in brackets):

| Set | Reports | Guide unchanged | Mechanical | Mechanical + news | Consensus |
|---|---|---|---|---|---|
| Test (surprises) | 8 | 17.1% | 11.5% (11.3) | **4.3% (7.1)** | 5.8% (5.9) |
| - A: analysts missed by 5%+ | 4 | 13.9% | 7.6% | **3.6%** | 7.6% |
| - B: mechanical missed by 10%+ | 5 | 18.7% | 14.9% | 9.5% | **3.4%** |
| Control | 9 | 14.3% | 4.2% (4.1) | **2.3% (3.9)** | 3.5% (2.5) |
| All | 17 | 15.2% | 7.5% (7.5) | 3.9% (5.4) | **3.7% (4.1)** |

| Pre-registered line | Result |
|---|---|
| 1. News helps: test median below mechanical and closer on 5+ of 8 | **PASS** (4.3% vs 11.5%; closer on 7 of 8) |
| 2. No harm: control median no more than 0.5 points worse | **PASS** (2.3% vs 4.2%) |
| 3. Near consensus: all-17 median within 1.0 point of consensus | **PASS** (3.9% vs 3.7%) |
| Secondary, revenue (not a pass line) | News 1.10% vs mechanical 1.12% vs consensus 1.91%: no gain on revenue; line 1 would fail (closer on 3 of 8) |

- **Ranges:** the news forecasts' 80% ranges held 12 of 17 (71%), and 2 of 5 on set B: somewhat too narrow.
- **Where it helped most:** Amazon (miss 14.9% → 2.3%) and Meta (10.6% → 4.7%), by reading the Q4 seasonal step-up in
  the company's own history, which the mechanical average blurs with the Q1 drop; TSMC (7.7% → 3.4%) from monthly
  revenue; Applied (7.5% → 3.9%) from peers' guide step-ups.
- **Where consensus stayed far better:** Micron (17.1% vs 7.3%), AMD November (12.6% vs 4.7%), ASML (9.5% vs 3.4%).
  Analysts still carry order-book information the packets do not.

## Read it with these caveats
1. **Part of the gain is a bias fix learned on the same reports.** The packet told the forecaster that the mechanical
   guide forecast "usually runs too low", a fact measured on the backtest that includes these 17 reports. A pure bias
   fix (mechanical × 1.048, run after the fact, not pre-registered) gets a 5.3% median: so roughly half the gain from
   7.5% to 3.9% is the bias fix, and half is the packet's other content.
2. **Little of it is headlines.** The forecasters' own notes credit the company's history, peers' prints, buyers'
   capex guides and TSMC monthly revenue far more often than headlines; most headlines were judged sentiment. "News"
   here mostly means structured, dated facts about the season.
3. **No-tool rule not auditable.** Each forecaster was told to read its one packet and use no other tool; each
   reported two tool uses (the read and its hand-back), and all 17 said they did not recognise the outcome. The
   forecaster model's training data ends before these reports.
4. **Small and one regime.** 17 reports, all in an up-cycle; set A has 4 and set B has 5.

## Verdict
On this sample, a forecaster that reads a dated packet of the season's facts names next-quarter guides about as well
as consensus on the median, and much better than our mechanical model, but not on the mean, and not on the quarters
where the order book moved. It adds nothing on reported revenue. The clean test is forward: run the same packet rules
before the December and January reports and score them against consensus. Nothing is wired in until that is done.
