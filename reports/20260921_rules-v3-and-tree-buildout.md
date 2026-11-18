# Rules v3, a trading ruleset, and +200 nodes on the master tree
**2026-09-21** · schema v2 → **v3** · tree 66 → **266 nodes / 19 lanes** · RULES R01–R27 → **R01–R36** · new **T01–T14**

---

## 1. What the misses actually taught

STATE.md already names the patch for each loss. Read across all twelve at once and a
tighter thing shows up: **the engine is a good physicist and a bad psychologist.**

Every one of the twelve misses is one of four shapes, and all four are the same underlying
error — pricing something as a *mechanism* when it was really a **choice**, a **conjunction**,
a **stale state**, or a **levered proxy**.

| shape | rows | what actually went wrong |
|---|---|---|
| **Choice ≠ mechanism** | #26 #63 #59 #29 #72 | every miss that turned on a named human or committee deciding — the Fed, Trump, OPEC+, the IRGC. Meanwhile physical/institutional invariants went **8-for-8 at Brier 0.10**. The edge is exactly where agency has been removed. |
| **Conjunction priced like a narrative** | #63 #39 #69 (#74) | #63 needed two independent discretionary actions and was priced **0.75 — above either leg alone**. #39 needed an oil leg *and* a food-emergency leg. #69 needed three bands to hold at once. A conjunction was never priced below its weakest leg. |
| **Premise already dead on the tape** | #19 #28 #29 | #19 was logged ~24h *after* the ceasefire broke. #28 was logged with the Hormuz re-closure already visible. This is not forecasting error, it is a data-freshness bug. |
| **The proxy carried more risk than the thesis** | #74 #70/#27 | #74 expressed a refining-margin view through a 3.8%/day instrument against a 1.25%/day one. #70 and #27 were one semis bet logged twice, and they tracked MISS together. The mechanism can be right and the expression still loses. |

Two more that the doctrine names in prose but nothing enforced:

**5. The book had no immune response to self-contradiction.** #32 (August CPI hot) and #76
(gasoline falls, CPI thesis weakens) were live simultaneously. #26 (no oil-driven hike)
contradicted #32 too — and #32's hot print is *what caused the hike that killed #26*. The
book was hedging against itself and booking it as two insights. STATE.md lesson 7 says this;
nothing checked it.

**6. The measurement lesson, which is the most important one.** 47 resolved rows in 14
correlated clusters puts the 95% interval on Brier at **0.16–0.26** and resolution at ~0.00.
So any lesson of the form *"P≥0.80 hit only 3/5, therefore lower high probabilities"* is
fitting noise — 3/5 at a true 0.8 happens about a quarter of the time. Only lessons with an
**outside-evidence mechanism** survive at this sample size. That is why leg-extrapolation
stands (ViEWS, Fortna, Min back it) and "inverted calibration" does not.

Everything below follows from that last point: **the fixes are mechanism-based, not
bucket-based.** Not one new rule is of the form "this bucket underperformed".

---

## 2. Rules v3 — nine new rules, each bought with a specific loss

R01–R27 police the *inside* of one row: its wording, its base rate, its leg-neutrality.
The gap was everything *between* rows, and everything about *who settles* a row.

| id | rule | the loss that bought it |
|---|---|---|
| **R28** | the book may not contradict itself silently: a row opposing an OPEN row on the same asset, or another row in the same batch, must declare it in `contradicts[]` with a `hedge_reason` | **#26 vs #32** — and lesson 7, which had never been machine-checked |
| **R29** | a two-ticker row declares both legs' realized vol; ratio > 1.5× means it is a **levered direction bet on the high-vol leg**, not a spread — P ≤ 0.55 and `row_class` must be `direction` | **#74** — XLE 1.25%/day vs USO 3.8%/day, second-worst score in the book |
| **R30** | every row names its resolution source: publisher, series, and the **reading convention**, fixed before the horizon | **#59** scored against the engine purely on scope; **#30** reached its horizon still "AMBIGUOUS, leaning HIT" |
| **R31** | a row reversing one of the engine's own open rows carries the mechanism's **lag length** and the days of contrary data actually in hand; `data_days < lag_length_days` is refused | **#76** — talked itself out of the correct #32 on two sessions against a 2–3 week pass-through lag (13g made enforceable) |
| **R32** | a row resting on a reported **plan** ("preparing to", drafted, leaked, *tabled*) caps at 0.35 until an **execution signal** exists | **#72** — a fully-coordinated leaked strike plan read as an action forecast (16.14 made enforceable) |
| **R33** | a row priced within 0.05 of the book's own base rate with no `divergence_reason` carries no information *(warning)* | the 9/20 research: a flat forecast at 0.745 would have scored **0.190 vs the book's 0.221** |
| **R34** | two rows sharing a ticker **and** a direction over overlapping horizons are ONE bet; the second needs an independence argument | **#70 and #27** — one SMH bet, logged twice, missed together |
| **R35** | a claim about ONE dated meeting must be priced **strictly below** the same claim over the window containing it | **#26** — a six-month window reasoned about as if it were a single meeting |
| **R36** | a conjunctive row declares its legs and their probabilities, and P may not exceed the **weakest leg**; a wording fix for a compound AND does not fix its price | **#63** at 0.75, **#39**, **#69** |

### The one that matters most

**R36 closes a dodge that has been open since R09 was written.** R09 bans the *wording*
"A AND B". An author who hits R09 can rewrite the sentence and log the same conjunction at
the same price. R36 forces the declaration, then checks the arithmetic. #63 would now be
refused at 0.75 against legs of 0.55 and 0.40 — and it would have had to be logged at
**≤ 0.40**, turning a Brier of 0.5625 into roughly 0.16.

### Two rules that will bind on rows the book currently calls good

This is the point, not a side effect:

- The repo's own canonical "known-good" test document is an FOMC row at P=0.72. Under v3
  it needed a resolution source (R30) and had to prove it sits below its window (R35) — and
  it now **fires R33 as a warning**, because 0.72 is inside 0.05 of the book's own 0.745 hit
  rate. By the book's own measurement, its model row carries no information.
- STATE.md's two live Fed rows — the `fomc-oct` second hike at 0.60 and the December SEP
  expression of the same view — are **one view, not two**. R28/R34 make that say so out loud.

### Verification

46 tests in `tests/test_schema.py` (was 35), two-sided: each new rule has a mutation that
must fire it *and* a repair that must clear it. Mutation-checked — disabling R29/R30/R31/
R32/R33/R35/R36 each turns the suite red, so nothing here is vacuous.

---

## 3. The trading ruleset — T01–T14 (`pipeline/trade_rules.py`)

There were **zero** enforced trading rules. Trade discipline lived only as prose in STATE.md
section 8 — which is exactly how a booked target went unnoticed for seven weeks.

Fourteen rules, same architecture as the prediction ruleset (pure, injected context, no repo
imports), 64 tests. The ones that would have caught real events:

- **T08 STALE-TARGET GATE** — an open trade whose tape has touched its target is `EXIT-DUE`
  and **fails the check**. This is trade #2 (MU): the pre-registered 800 target was touched
  on 7/28 and sat unbooked until 9/19.
- **T13 STALE-INVALIDATION GATE** — the same blind spot on the *losing* side. MU printed
  1042.40 on 9/9, through its own 1035 invalidation, while the trade still read "open". Only
  the retroactive 7/28 booking saved the book. *A falsifier that doesn't bind isn't one.*
- **T09 / T14** — a target exit books **at** the target, and the exit must name a session whose
  actual range contains the exit price. Together these make the 737.88 hindsight-low booking
  impossible to write down.
- **T06** — the #74 rule at the trade layer: a two-leg trade with a vol ratio > 1.5× is a
  levered direction bet, and inherits the cap.

**A real contradiction, reported rather than smoothed over:** the book's biggest win,
MU short 937→800, has R:R = 137/98 = **1.40**, below T04's 1.5 floor. That is either a floor
that wants to be 1.35, or mispriced risk that happened to pay. It is logged as an explicit
test rather than fitted away — a threshold tuned to make your best trade legal is not a rule.

**Not yet wired:** `ledger.py trade-open` does not require `--target`/`--invalidation` and
does no freeze or parent check. T01–T03 exist but the CLI does not call them yet.

---

## 4. The buildout — +200 nodes, 19 lanes

`tools/buildout_2026_09_21.py`, reproducible, self-policing, merged after a clean dry run.

**The mix is the argument.** Weighted to what the book actually scores on and starved of what
it loses on:

```
invariant  89   scheduled 33   level 23   marker 20   duration 16   direction 14   branch 5
p spread:  min 0.15 · p25 0.68 · median 0.78 · p75 0.88 · max 1.0
p ≤ 0.45:  10 rows        p ≥ 0.88:  50 rows
```

- **61% invariant-or-scheduled** — the 8-for-8 and 12-for-14 classes.
- **7% direction**, all capped at 0.55 — the class that went 0-for-8.
- **Only 2 new iran-energy nodes**, both durations, because that cluster is at 44% of open
  rows and over the 35% cap. Neither is a call on the next leg (16.18 / R27).
- **10 rows at ≤0.45 and 50 at ≥0.88.** This is the direct answer to resolution ≈ 0.00: a
  book whose every row sits between 0.40 and 0.88 cannot earn resolution no matter how often
  it is right. You fix that by being willing to say *probably not*, and *almost certainly*.

**Thirteen new lanes** fill genuine coverage holes — healthcare is ~18% of the economy and had
zero nodes; Europe had zero despite being the marginal buyer of the energy this book trades;
mining, where geology *is* the invariant, had none at all.

**The best single node** is `npt-notice-arithmetic`: NPT Article X requires three months'
notice before withdrawal takes effect, so "no withdrawal before 2027-01-01" is a notice-period
calculation, not a geopolitical forecast — and it turns on a distinction the engine has already
paid for: a bill **tabled** is not a notice **filed** (#72).

### The buildout polices itself

The script refuses to merge a batch that would not survive the book's own rules. On the first
run it **refused its own author, 32 times** — thin rationales, confident rows whose basis
named no structural constraint, two direction rows over the 0.55 cap, three markers above the
0.85 invariant threshold. All 32 were fixed by moving the *number* or improving the *argument*,
never by moving the rule.

### Honesty constraint

**Not one dated news fact is invented.** `evidence` carries only structural/calendrical facts
that are true by construction (a treaty's notice period, an auction calendar, a maturity
schedule, a protocol rule) — 6 nodes. Every other node states an outside-view prior in `basis`
and carries `evidence: []`. Fabricating a plausible headline would poison the evidence base of
a machine whose three worst misses were all *"the premise was already dead on the tape"*.

### Gates

`web_coverage` OK (77/77 wired, 0 dead-end catalysts) · `debug_all` **0 FAIL** · all 10 branch
forks sum to 1.00 · no dangling parents · no shift edges to missing nodes.

Lesson 5 says verify the map *visually*, not just in the DOM. Measured on the live render:
**293 positioned boxes, 0 overlapping pairs**, canvas 2860×4464, 59 nodes rendering in the
Oct–Dec band. (The browser pane stopped painting partway through, so this is DOM-geometry
rather than an eyeball — stated rather than glossed.)

---

## 5. Also fixed

The `ecb` feed had failed on **every** run for hours — `CERTIFICATE_VERIFY_FAILED`. Root cause
was neither a global trust-store problem nor the usual missing-intermediate: Python's anchor
set holds Sectigo root **R46** (RSA) but not **E46** (ECC), and Windows fetches missing roots
on demand while OpenSSL does not. Fixed by *adding* that one root via `load_verify_locations`
— no `CERT_NONE`, no `check_hostname = False`, no relaxing fallback, with `badssl.com` negative
controls proving verification is still enforced. Feeds went **37/38 → 40/40**.

---

## 6. What this does NOT fix

- **None of it is outcome-tested.** Zero resolved rows carry a resolution source, an
  independence argument or a conjunction block. R28–R36 and T01–T14 are *hypotheses about
  what would have helped*, grounded in specific losses — not measured improvements. The first
  honest read is when rows logged under v3 mature.
- **The sample problem is untouched.** 47 resolved rows in 14 correlated clusters. Nine new
  rules do not add statistical power; they add structure that makes future rows *countable*
  and *independent*. That is the only lever available at this n.
- **R33 is a warning, not an error, and should stay that way** until there is evidence that
  base-rate-adjacent rows actually cost something. Turning it into an error would push the
  book toward false precision — the #24 failure mode.
- **200 nodes is 200 places to be wrong.** Most carry a prior and no fresh evidence, which is
  honest but thin. They earn their place by being *checkable*, not by being confident — and
  every one of them says which it is.
- **T01–T03 are not wired into `ledger.py`.** The rules exist; the CLI does not call them.
