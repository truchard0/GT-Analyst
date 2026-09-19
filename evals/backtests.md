# Judgment Evals — Frozen-Input Backtest Cases

Protocol: the analyst gets ONLY the frozen inputs (pretend today is the as-of date; no later knowledge). Produce the full CLAUDE.md output schema including conviction breakdown. Then self-grade against ground truth: direction correct? mechanism named? falsifier discriminating? **conviction appropriate** (would the rubric have scored a hit high and a miss low)? Log a meta-note on which formal §10 item would have caught any miss.

---

## Case 1 — Russia buildup (as-of 2022-02-10)
**Frozen inputs:** ~130k Russian troops on Ukraine border with field hospitals and blood supplies forward-deployed; Belarus joint exercises extended; US/UK embassies evacuating; Lavrov says "diplomacy continues"; Putin denies invasion plans.
**Tests:** §12.1 capital-committed (blood supplies/hospitals) vs rhetoric (denials); Fearon commitment problem (NATO trajectory); formal §10.5.
**Ground truth:** invasion 2022-02-24. Capital-committed signals were decisive; denials were noise.
**Grading:** high conviction warranted (primary-observable posture + costly signals + converging lenses). A "diplomacy will hold" read = failure of checklist item 5.

## Case 2 — Red Sea attacks (as-of 2023-12-18)
**Frozen inputs:** Houthi attacks on commercial shipping expanding; Maersk/Hapag-Lloyd suspend Red Sea transits; US announces Operation Prosperity Guardian; war-risk insurance premiums up 5x.
**Tests:** chokepoint priority (§11.4); corridor-specific shipping mapping (containers rerouted → rate spike); adaptive-vs-rigid read on the Houthis (§10.1 selective enforcement).
**Ground truth:** container rates ~tripled within weeks (ZIM rallied hugely in 2024); attacks persisted for a year+ despite coalition patrols — compellence failed (formal §11 base rate).
**Grading:** correct call = long disruption + container-rate upside; "coalition restores traffic quickly" = compellence base-rate failure (item 10).

## Case 3 — Evergrande (as-of 2021-09-20)
**Frozen inputs:** Evergrande missing offshore bond payments; "China's Lehman moment" commentary everywhere; PBOC injecting liquidity; global risk assets wobbling.
**Tests:** RESTRAINT. Over-prediction trap — contagion narrative vs actual transmission channels (closed capital account, state-controlled banks).
**Ground truth:** contained; no global credit event. Chinese property deflated slowly for years; US markets recovered within days.
**Grading:** the correct output was LOW conviction on contagion (transmission channels not demonstrable → checklist items 3 and 11). Ledgering a high-conviction Lehman call = rubric failure.

## Case 4 — OPEC+ surprise cut (as-of 2023-04-03)
**Frozen inputs:** OPEC+ announces surprise ~1.16 Mbpd voluntary cut; WTI gaps up ~6%; White House criticizes; "Saudi-US rift" commentary.
**Tests:** cartel discipline as capital-committed supply action (§13 scarcity architecture); horizon matching — announcement vs sustained physical tightness.
**Ground truth:** crude popped then faded — by June WTI was BELOW pre-cut levels (demand softness dominated).
**Grading:** correct = medium conviction on the supply mechanism with an explicit demand-side sensitivity tag; wrong = high-conviction multi-month bull call without the demand flip-test (item 2).

## Case 5 — Iran–Israel direct exchange (as-of 2024-04-14)
**Frozen inputs:** Iran launches ~300 drones/missiles at Israel (first direct state attack), heavily telegraphed, ~99% intercepted; regional airspace closed; oil and gold pre-spiked.
**Tests:** ladder calibration — was this escalation or choreography? Telegraphing = calibration signal (§2); priced-in assessment; §11.5 truce-rally fade rule.
**Ground truth:** Israel's response (Isfahan) was symbolic; oil FELL after each strike (risk premium already priced); no regional war in 2024.
**Grading:** correct = "calibrated exchange, fade the war premium" with medium conviction; wrong = rung-skipping to regional war (item 8).

## Case 6 — Ever Given / Suez (as-of 2021-03-25)
**Frozen inputs:** container ship grounded blocking Suez; 300+ vessels queued; salvage timeline "days to weeks"; 12% of global trade transits Suez.
**Tests:** chokepoint event but SHORT-duration mechanics — horizon matching; over-extrapolation trap (§11.4 priority ≠ automatic long thesis).
**Ground truth:** refloated in 6 days; rate effects transient.
**Grading:** correct = high conviction on direction, SHORT horizon, falsifier = refloat date; wrong = structural repricing thesis on an engineering problem (item 11 — falsifier had to be the salvage itself).

## Case 7 — SVB (as-of 2023-03-10 morning)
**Frozen inputs:** SVB fails after deposit run; FDIC receivership; First Republic wobbling; uninsured-deposit panic spreading among regional banks; Treasury/Fed "monitoring."
**Tests:** regime-break vs contained (§5 snap-not-glide); predicting the POLICY REACTION as part of the game (two-level, §5 formal); KRE/TLT direction.
**Ground truth:** BTFP announced 2023-03-12 — backstop contained systemic spread but KRE kept bleeding for weeks (First Republic failed in May); rates rallied hard (yields collapsed).
**Grading:** correct = split prediction: systemic contagion contained (policy best-response, item 9) BUT regional-bank equity impaired + duration rally; single-direction "everything crashes" or "nothing happens" both fail.

## Case 8 — CHIPS Act + export controls (as-of 2022-10-10)
**Frozen inputs:** CHIPS Act signed (Aug) with $52B; sweeping October 7 export controls on advanced chips/tools to China; ASML/AMAT guidance cuts on China exposure; semis in a brutal cyclical downturn.
**Tests:** capital-committed structural thesis (§12.1 strongest tier) arriving DURING a cyclical bear — separating horizons; dependency-cascade mapping (§10.8 tech chain).
**Ground truth:** SOX bottomed within weeks; 2023–24 was a historic semi bull (AI capex); export controls entrenched the western-equipment premium.
**Grading:** correct = high conviction on the multi-year structural leg with explicit "cyclical bottom timing unknown" sensitivity; wrong = letting the cyclical bear override the capital-committed signal (item 2 flip-test).

## Case 9 — Tariff escalation rounds (as-of 2019-08-05)
**Frozen inputs:** new 10% tariffs announced on remaining $300B China imports; CNY fixes through 7.0; US designates China "currency manipulator"; farm-purchase promises suspended; markets down ~3%.
**Tests:** announced vs implemented (§12.1 — tariff *announcements* were often negotiating rhetoric); repeated-game structure of the trade war (§4 formal); which sectors actually transmit.
**Ground truth:** repeated announce-escalate-negotiate-partial-rollback cycle; Phase One deal Jan 2020; broad equities made new highs within months while soybeans/semis carried the real impact.
**Grading:** correct = treat each announcement as a rung in a repeated bargaining game (medium conviction, sector-specific), not a regime break; wrong = extrapolating each announcement linearly (items 4, 10).

## Case 10 — Assad collapse (as-of 2024-12-01)
**Frozen inputs:** HTS takes Aleppo in days with minimal resistance; Syrian army units dissolving; Russia distracted in Ukraine, Hezbollah degraded by Israel; Iran's land bridge under pressure.
**Tests:** precondition tracking (§12.3 — patron capacity as the load-bearing precondition); cascade speed once preconditions flip; allies-as-separate-players (§4 — would Russia/Iran actually spend to save him?).
**Ground truth:** Damascus fell 2024-12-08 — a week. Patron withdrawal was the whole game.
**Grading:** correct = once both patrons' capacity preconditions failed, high conviction on rapid collapse (the base rate for patron-abandoned clients is brutal); wrong = anchoring on 13 years of stalemate (item 10 — the base rate changed class when the preconditions flipped).

---

## Grading ledger
Track eval scores over time in this table as the agent (or new model versions) re-run the cases:

| Date | Case | Direction | Mechanism | Falsifier | Conviction-appropriate | Notes |
|------|------|-----------|-----------|-----------|------------------------|-------|
