# GT-Analyst — WHERE WE ARE / WHERE WE'RE GOING
**Sat 2026-08-01.** Post-backtest position report: the honest scoreboard, the misses and what
they actually teach, the live book, and the two weeks that decide it.

---

# PART I — WHERE WE ARE

## 1. The scoreboard, stated honestly
| | |
|---|---|
| Logged | **72 predictions** |
| Resolved | **12 · all HIT · mean Brier 0.124** |
| **Honest projected** | **12/15 = 80% · Brier ~0.192** |
| Realized P&L | **+7.46%, ONE closed round-trip** (RTX) |

The 12/12 is a **maturity artifact** — nothing that could fail had matured. Three escalation
calls are now failing or at risk. The projected number is the real one.

## 2. The misses — and the single pattern behind them
All three are the same error, at high conviction:

| # | Call | P | What actually happened |
|---|---|---|---|
| **#63** | US strikes Yemen + escort framework by 8/4 | 0.75 | **No Yemen strikes. No escort framework.** Trump's response to Houthi tanker attacks was to say he'd *"hold Iran responsible"* — the pressure channel, not the kinetic one |
| **#72** | US/Israel strike Iranian energy pre-Monday | 0.55 | **Trump stood down 8/1**, citing "perimeters of a deal," at Iran's *and the Gulf states'* request |
| **#59** | Ceasefire fails (no 10 strike-free days) | 0.72 | Pause holding since ~7/25; needs to break by ~8/4 |

### The deeper lesson (beyond §16.14)
The first read was "Trump reverses." The **sharper** read, now with three data points: in this
phase of the war **the US is systematically choosing the pressure/diplomatic channel over the
kinetic one** —
- Houthis strike Saudi tankers → US declares *Iran responsible* rather than striking Yemen
- Energy-strike campaign fully planned and coordinated → **stood down** for talks
- 13-night campaign → **paused at Iran's request**

Each time the engine read a *capability + intent* signal as an *action* forecast. The
correction (§16.14) caps strike-planning reports at **0.35 absent execution signals** — and
counterfactually would have saved **~0.62 of cumulative Brier** on #63 and #72 alone.

## 3. The portfolio problem
**iran-war = 31 of 55 open predictions (56%)** — one correlated bet dressed as thirty-one, in
the exact cluster carrying the bias. Now capped at ~35% per cluster, with per-cluster
calibration required.

## 4. What's genuinely working (don't over-correct)
- **#67 — the FOMC fade.** Engine 0.75 hold vs market ~0.65 (CME ~35% hike). Fed held, three
  dissents, majority waited for July/Aug CPI — the mechanism called exactly. **Beat a live
  market price.** Brier 0.06.
- **#50/#52 — capex cohort** all raised (GOOGL $205B, META $130–145B, AMZN $220B, MSFT Azure +43%)
- **#61/#47 — the semis correction**, including being flagged at-risk mid-week and still resolving HIT
- **#44 — RTX** +12.8%, the only closed trade

**The boundary:** strong where the mechanism is *structural and datable* (Fed reaction
functions, capex cycles, positioning unwinds, calendar arithmetic); weak where the outcome is
**one person's discretionary choice**. That is where conviction should and shouldn't be spent.

## 5. Market position (7/31 close)
**SPY 746.81** (on its 50-day 744.7) · **QQQ 687.92** · **SMH 540.16** (8.5% *below* its 50-day
596, RSI 42 — the weak leg) · oil elevated, gasoline **$4.11** · yields rising on a Fed
"credibility gap."

Regime = **capped grind**: no crash (#65 tracking HIT), no durable new ATH (#66 tracking HIT).

## 6. War position
**Stand-down, not a deal.** Trump held off the energy campaign 8/1; Iran simultaneously
**denies** movement toward a longer-term agreement. Hormuz traffic still **−90%**. Oil +20–22%
in July. The **Islamabad 60-day window expires ~8/16** — that is the master clock; everything
before it is oscillation (§16.12). Map re-weighted: **off-ramp 0.45 now leads**, escalation 0.35.

---

# PART II — WHERE WE'RE GOING

## The calendar that decides everything
| Date | Event | What it resolves |
|---|---|---|
| **Mon 8/3** | Market open | #72 resolves (**likely MISS**). Gap risk now low; oil should fade |
| **Tue 8/4** | — | **#63 resolves (likely MISS)**; #59's pause-break deadline |
| **Fri 8/7** | **July jobs report** | Into a bond market flashing a credibility gap. First real macro test |
| **Wed 8/12** | **July CPI** | **THE referee.** #71 says benign (+0.1% headline) on calendar mechanics |
| **Thu 8/13** | July PPI | Tariff pass-through check |
| **~Sun 8/16** | **Islamabad window expires** | #68 (off-ramp) + #49 (election instrument) both resolve |
| **late Aug** | **NVDA earnings** | Where raised capex meets actual revenue — the margin question |
| **Aug 21** | — | #65 (no crash) + #66 (war caps melt-up) resolve |
| **Sept** | **FOMC** | The deferred hike. Decided by the Aug CPI, not the July one |
| **Sept 30** | — | #69 (range) + #70 (SMH underperforms) resolve |

## The three things that actually matter next
**1. The Aug-12 CPI is the market's referee.** My call (#71, P=0.60, conviction cut to 0.50
after you caught the gas-average error): **headline +0.1–0.2%, benign** — because the July oil
spike hit only the last ~10 days, so July's *average* pump price lands near June's. **The hot
print is the August CPI in September** — August opens at $4.11, already above July's entire
average. Soft July print → the semis bounce gets room; hot → the rate-derate re-fires.

**2. The Aug-16 window is the war's real fork.** Deal → oil fades hard, risk-on, #68 HITs.
Collapse → round-3 and the energy campaign comes back off the shelf. Trade the *convexity*
into it, not a direction.

**3. NVDA in late August is the AI referee.** Capex is confirmed ($725B cohort); the open
question is whether it converts to revenue or just compresses margins (META's EPS miss is the
warning). This decides whether SMH's 605 line gets reclaimed or 480 gets tested.

## What would change my mind
- **CPI ≥ +0.4%** → my calendar-mechanics read was wrong; rate-derate re-fires; SMH toward 480
- **A signed Iran deal** → the off-ramp confirms, oil craters, semis rip, and my escalation
  correction was right *twice over*
- **Strikes resume before 8/4** → #59 HITs and the stand-down was tactical; my de-escalation
  read would then be the over-correction (§16.14's corollary exists for exactly this)
- **A hyperscaler walking back capex** → the whole AI-floor thesis breaks

## The structural trajectory
The engine is converging on what it's actually good at. Twelve resolutions in, the evidence
says: **fade the market on datable, mechanism-driven macro** (the FOMC fade is the template —
and the prediction-market feed now lets that be benchmarked rather than self-graded), and
**stop making discretionary-actor forecasts at high conviction** (three misses paid for that
lesson). The machinery to enforce it now exists — three gates, a lessons table that blocks the
cycle until every resolution is diagnosed, a hard numeric cap replacing a judgment call, and
portfolio limits on correlated clusters.

The next two weeks will roughly double the resolved sample (12 → ~20). That is the first point
at which calibration means anything at all. Until then: **the honest number is 80% / 0.192,
one closed trade at +7.46%, and a documented bias that has now been patched three times.**
