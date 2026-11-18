# A. How the Skylit methodology reads dealer-gamma heatmaps — structured extraction

Extracted 2026-11-18 from the user's own files under `C:\Users\hudso\Downloads\Trading Bot`. Read-only; no source edited.
Reading rules only. Nothing here is trade advice; the "setups" are recorded as ways of reading a map.

## 0. Sources, citation keys, and the one caveat that governs everything

**Transcripts (7, all read in full; teacher = "Glitch", Skylit/Heatseeker founder).** The `.txt` files are one physical
line each, so line numbers were made on wrapped copies in the scratchpad (re-runnable):

| key | video id | date / topic | citation form |
|---|---|---|---|
| bgkp | bgkpUxFpOvM | ~8 Sep 2025, Owls onboarding, live SPX 0DTE read + single-name scroll | `bgkp:L<n>` = `fold -s -w 400` line (scratchpad `gamma_research\wrapped\`) |
| motn | motnKLCPElY | ~30 May–1 Jun 2026, GEX+VEX swing reading | `motn:L<n>`, same fold-400 |
| XSyb | XSybHIpQ078 | ~16 Sep 2025, "Heatseeker 102", eve of FOMC | `XSyb:L<n>` = `fold -s -w 600` line (`gamma_research\parts\folded\`) |
| fs8 | -fs8LJBPM-E | ~11–12 Oct 2025, recap of the 10 Oct sell-off; VIX map, gatekeepers | `fs8:L<n>`, same fold-600 |
| AE9 | AE9PY1a5tyc | ~27–28 Sep 2025, quarter-end, VIX map, SPX 26 Sep recap | `AE9@c<offset>` = char offset of a 1,500-char window (`gamma_research\t3fold\`) |
| 470 | 4_70qFYqENU | ~20–21 Sep 2025, how to pick swings, OPEX roll-off, four-digit rule | `470@c<offset>` |
| G5O | G5OutDv14Qo | FOMC day, probably 29 Oct 2025; Trinity mode, decoys, velocity, colour scale | `G5O@c<offset>` |

`skylit_transcripts/moc_fetch/` holds only five oEmbed title stubs for non-Skylit MOC videos (no transcript text).
Timestamped cites of the form `<id>@h:mm:ss` come from the 96-video synthesis digests (below).

**Knowledge files** (line cites `<key>:L<n>`):
HD = `knowledge/HEATMAP_DOCTRINE.md`; HR = `knowledge/HEATMAP_RULES.md` (the rules "as taught", no test results);
RB = `knowledge/SKYLIT_RULEBOOK.md`; GTS = `knowledge/GAMMA_TRADING_SHEET.md`; SDS = `knowledge/skylit_doctrine_spec.md`
(extraction of 91 vendor doc pages, 2026-07-20); GVS = `knowledge/GEX_VEX_STATES.md`; ONL = `knowledge/OVERNIGHT_LEVELS.md`;
GPR = `knowledge/GARMA_PLAYBOOK_RULES.md`; HAP = `knowledge/HERMES_AGENT_PROMPT.md`; IDX = `knowledge/INDEX.md`;
DG-nn = `knowledge/skylit_videos/synthesis/chapters/digests/nn.md` (digests of the 96-video synthesis: Glitch, Garma, Giul,
Wicksy panel, SkylitAI, skylit cat); ERR = `knowledge/skylit_videos/synthesis/ERRATA.md`;
ACAD = `brain/Memory/reference_skylit_academy.md` (Skylit Academy lessons the user pasted); MEM-* = other `brain/Memory/` notes.

**Status vocabulary** used by the repo (HD:L41-50, RB L24-30 per K1 notes): DOCTRINE = taught, never measured here;
NULL-55d = measured on 55 days of 1-second maps, no effect as large as claimed; FALSIFIED = tested and lost money;
VALIDATED = measured and survived; CONFLICT = sources disagree.

**The governing caveat.** The repo's own measurements find no measurable price effect for any core node claim
(King magnet, first-tap deflection, sign, regime, rolls, Trinity) (HD:L26-37, HD:L108-122), and Skylit's own September
2026 doc rewrite calls the playbooks "a habit, not a tested signal" (HD:L32-33, HD:L128-131). The repo therefore uses the
heatmap only as "a level-selection and context tool... never as the trigger, never as a probability" (HD:L34-36).
What follows is the method *as taught*, with the measured status attached where it exists.

---

## 1. Map anatomy

### 1.1 Axes and cells
- **Rows = strikes; columns = expirations, nearest first.** "first column is going to be the strongest and then second
  column, third column" (bgkp:L111); per-expiry columns out to monthlies/LEAPS on swing maps (motn:L11, L36, L41); a grey
  box marks spot and the view auto-centres on the King (XSyb:L33; bgkp:L182-183). Computed "on a per column basis", not
  aggregated into bars (AE9@c32952). DG-01:L3 summarises: a grid of strikes by expiries holding "net notional dealer exposure".
- **Trinity mode** = the first expiry column of SPX, SPY and QQQ side by side (G5O@c2996; HD:L96). The repo's captures
  use the per-strike *ladder* (one column, `EXPIRATIONS=Current`) rather than the full strike x expiry grid (GTS:L150; RB
  has no strike x expiry reading rule, K1 §1.1).
- **Two map modes per ticker:** GEX (gamma; "magical for zero day expiration... intraday", fs8:L42-43; 0-5 days,
  motn:L8) and VEX (vanna; "speculative swing" nodes, fs8:L17; 2-4 weeks, 470@c1496). Toggle Ctrl/Cmd+G and +V
  (XSyb:L36; 470@c44917). A one-off "DEX" mention is unresolved (XSyb:L53).
- **Values are signed and scaled.** "This is 22 million cuz it's by the thousandth" (bgkp:L60) — display in thousands
  (RB L1 shows `$14,234K`, `-$102,914K`, K1 §1.2). Teacher calls them "net notional" (bgkp:L106) / "dealer exposure"
  (XSyb:L6-7) / how dealers "are hedging and what their notional exposure is" (fs8:L73). **Units and the meaning of the
  sign are never formally defined in any transcript** (T3 notes §6.1; XSyb:L116 ambiguity).
- **Magnitude conventions in the repo:** the repo's reconstruction uses the "$ per 1% move" convention,
  `(Γc·OIc − Γp·OIp)·100·S²·0.01` (RB D1/D7, GTS:L117), so a "$50M" cell = ~$50M of underlying to trade per 1% move.
  GEX and VEX live on different scales (~1e8 vs ~1e4), so "GEX+VEX" is a sign-agreement read, never a sum
  (HD:L60-62; ACAD:L66-69).

### 1.2 How Skylit computes and normalises — known vs unknown
- **Teacher's account:** a "proprietary inference layer to predict dealer positioning" over ~300 tickers (bgkp:L34-35);
  "I don't even use the vanilla equation and formula for gamma exposure" (470@c56903); "I call it gex and vex because...
  I can't think of other words for it" (same); charm, vomma, speed are folded in "in the back end" (bgkp:L201-203);
  rule-based "with a data model", back-tested "20 to 30 years" (bgkp:L244, L264-265).
- **Rejects open interest:** OI "doesn't tell you if that position is a short position or a long position", OI tools are
  a "50/50 crapshoot" (bgkp:L47-49, L95-97).
- **Persistence:** exposure tracked "from the beginning of time", no morning reset; it "doesn't ever roll off... unless I
  have confirmation through our inference layer", so the end-of-day map "is still in play for tomorrow morning" (XSyb:L6-7).
- **Seeding:** new tickers need "a couple of weeks" (XSyb:L52) / "3 to four weeks of... seeding and reinforcement learning"
  (470@c34442).
- **Refresh:** backend ~5 s; images every ~15 s (really 15-25 s) (bgkp:L62-64; XSyb:L10); later "45 or like 50 second
  refreshes" (AE9@c5995). Vendor docs: OPRA + ThetaData, aggregates ≤1/s, 1-second history to 365 days, `maxStrikes`
  default 92 (SDS:L102, L321, L327 per K2 §1.2). API nets **5 expirations by default** (HD:L63).
- **Admitted unknowns:** "no proper way and no like explicit way" to track dealer positioning; competitors "all get it
  wrong" and his may not be "100% correct" (bgkp:L8-9). "Dealer positioning is derived, not exchange-reported" (HD:L57-59).
  Vendor weighting unknown (GTS:L444).
- **What the repo measured about the construction:** the intraday ladder is **flow-driven, not OI-driven** — best
  reconstruction `cumvol(K, t−1bar) × BS_gamma` with OI weight 0 (alignment 3.29/5 vs 2.44/5 with full OI) (RB D8,
  GTS:L305-310), so nodes can be born intraday. Skylit ≠ public GEX (top-5 overlap 1.46/5, DG-01:L41). Skylit API "SPX" is
  the MONTHLY book, not 0DTE SPXW (HD:L67-68); SPXW and SPY are different maps (King within 5 pts only 18% of the time,
  HD:L66).

### 1.3 Colour — the most contested anatomy point
- **Taught (2025 videos, Academy):** "purple just means that dealers are short gamma and yellow means that dealers are long
  gamma" (bgkp:L77-80); purple ≠ sellers, yellow ≠ buyers (bgkp:L79-80). Academy: positive gamma = YELLOW "Pika", negative
  = PURPLE "Barney" (ACAD:L56-59; SDS:L58-66; RB D12). Vendor palette: positive green→yellow, negative blue→purple (SDS:L60, L65).
- **Colour scale (G5O):** dark purple at one extreme, bright yellow at the other, "in between... the zero zone... neutral
  colors are what I consider like air pockets"; "the gradients help you understand... how weak or how strong a level is"
  (G5O@c43443-c44943). "If a node doesn't have a number... it's a air pocket" (G5O@c59914).
- **Background colour is a contrast artefact:** yellow background = "massive negative exposure somewhere"; dark purple
  background = "massive positive exposure somewhere"; "that's really all it tells you" (XSyb:L10-12; bgkp:L53-54).
- **Corrected in 2026 (product fact):** on the default viridis palette "yellow = highest value on the board, purple =
  lowest; zero has no fixed colour. A purple- or blue-looking cell without a minus sign is still a positive node" —
  "Any human or vision reader that infers sign from heatmap colour is wrong" (HD:L74-79, citing skylit docs/guides/heatseeker;
  HR:L15). Trinity has its own colour scale; Atlas orbs do colour by sign (HD:L77-78).
- **Repo rule:** read the number, not the colour (HR:L15). See §6 C1.

### 1.4 Strength
- **Absolute value is strength; sign only changes the approach.** "Absolute value does not give a crap whether a number
  is positive or negative" (bgkp:L59); "king node can be yellow or purple... I only want people to care about what the
  absolute value of that node is" (AE9@c32952-c34448); Academy "ABSOLUTE VALUE RULE: magnitude > color... bigger AND closer
  = stronger pull... Purple ≠ bearish" (ACAD:L60-62; RB D13).
- **Significance floor:** "at least four digits or larger" for a strong pull; three-digit nodes = weak, illiquid or new
  ticker (XSyb:L116-121; 470@c22458, c26953; AE9@c55404). Ambiguous because "it's in a millionth" (XSyb:L116) — four digits
  in a thousands display ≈ $1M+ (T2 notes §A1).
- **Relative size:** read as **% of King** (HD:L145; HR:L13; RB L1-L2). Repo/user: always show node size as signed % of
  that book's own King, never raw $ (MEM feedback_pct_of_king:L11-20); King is per book, never across a merged map
  (MEM feedback_king_per_book:L8-14). Composite node = sum over books of |node|/|own King|, 0-4 (MEM feedback_composite_node:L11-15).

### 1.5 Node glossary (exact definitions with sources)

| Term | Definition | Source |
|---|---|---|
| **Node** | One strike's exposure value. "Positive means dampened interactions, not bullish." | HD:L84 |
| **King (King node, "key node")** | Largest absolute value on the board for the chosen expirations, either sign; starred/auto-bordered. "There is no single King" — it depends on the Expirations setting. Contested King: leads runner-up by <10%. Stacked King: GEX King and VEX King on the same strike+expiry. | AE9@c31453; bgkp:L74, L182; HD:L64-65, L85; HR:L25 |
| **King (vendor)** | "dealers prefer to settle price at this level" EOD/EOW; primary destination | SDS:L13-15 |
| **Gatekeeper** | "a node between your current price and the king node and it's like at least a quarter of the size of your king node" | fs8:L62 |
| — variants | "a major node... in between the current node... and the next major... in the opposing direction" (AE9@c31453); either colour, "a road bump or... roadblock" (XSyb:L107); Garma ≳25-33% can gatekeep, 60% strong (HD:L87; HR:L27); repo classifier ≥25%; only tested version used ≥70% (RB T2/G27; GTS:L192, L201); "five gatekeeper definitions" in the 96-video corpus (DG-02:L71) |
| **Floor / ceiling** | Large node below / above price. Docs: either sign, the *biggest* not the nearest. Academy rolling article: largest *positive* node. CONFLICT. | HD:L86; HR:L26 |
| **Call wall / put wall** (repo) | max +GEX strike above spot / max −GEX strike below spot; a global max/min is a bug | RB D6; GTS:L215-229 |
| **Air pocket** | Run of tiny (<~10-20% of King) or missing strikes. "Air pocket is space; rate of change is fuel." A missing strike IS an air pocket. Garma: <20-30%. | G5O@c43443; HD:L88, L158; DG-01:L28 |
| **Pika / Barney** | Standout positive / negative node | HD:L84; ACAD:L56-59 |
| **Stack / cluster / Pika cloud** | Several large adjacent nodes; dense positive = "gravity well" where trends stall | HD:L89; SDS:L43 |
| **Double stack** | Nodes stacked together → strong bounce potential (vendor) | SDS:L43 |
| **Magnet / wall** | The same major node: "gravity will pull towards it" and price is unlikely "to go above and stay above"; "It's a magnet and it's a wall" | bgkp:L60-61, L98 |
| **Hedge node** | Huge (often downside) node before CPI/PPI/data; "doesn't mean that price is going to go down there"; judged by "how far out the money it is and how many days left" (QQQ 575, 3 days, 18 pts = hedge) | bgkp:L109-111; XSyb:L22-23, L28-29 |
| **Decoy** | ~100 pts OTM node popping on FOMC/OPEX/news days, "dormant" rate of change; NFLX 1290 / LLY vendor examples | G5O@c4495, c16477, c19472; SDS:L36-38; HD:L177-178 |
| **Rug** | + node stacked over − node (vendor: "a yellow node positioned directly above a purple node, with no visible floor below") — five competing definitions | HD:L90; SDS:L160-166; DG-03:L63 |
| **Reverse rug / trampoline** | − over + ("a purple node above a yellow node"); "if this claims, you're going to get a buy loop" | G5O@c25466; HD:L91 |
| **Rolling** | Floor moving up / ceiling moving down across updates; 1 move = noise, 2 = signal, 3 = confirmation | HD:L92; fs8:L30-32 |
| **Slip-in** | A node materialising at/next to spot; under price supports, over price caps | HD:L93; ACAD:L88-112 |
| **Velocity** | Rate of change of \|value\| over 1/5/10 min (badges, sparklines, top movers); halo = ≥2 timeframes agree | G5O@c37455-c38954; HD:L94 |
| **Flip / polarity level** | Where cumulative net exposure changes sign (`/v1/gex/levels summary.flip`). Never taught in the 7 transcripts; repo computes it by re-pricing total gamma | HD:L95; RB D2; GTS:L53 |
| **Rainbow Road** | Map scrambled by a macro/earnings shock (many big ± nodes) — stand aside | HD:L97; AE9@c52410; SDS:L168-171 |
| **Node lifecycle** | Fresh → tested → delivered → decaying/spent; the board does not flag which | HD:L98 |
| **Delivered-from** | The node price launched from or was rejected from is a used-up wall, not a fresh target | bgkp:L184-185, L222-223; AE9@c65877 |
| **Stubborn / suspect / lit** | node that "never lit off" (persists); dubious downside nodes; "brightly lit" = bright, large | motn:L39, L81, L84-86 |
| **Sandwich / no man's land** | price pinned between floor and ceiling → "pinball"; spot between two majors | XSyb:L68-71, L132 |
| **Stubborn King** (Garma) | large SPY King pins price in ~$1 range until killed | HR:L48 |
| **GEX VWAP** | value-weighted centre of the board; "Not a target or a signal" | HD:L99 |

---

## 2. Reading procedure as taught

### 2.1 Before reading: set the instrument (repo practice built from the teaching)
- Index day trade: GEX, Expirations = Front/0DTE; swing: To Friday or N=2 plus VEX (HD:L141-142; HR:L11-12).
- S&P = **SPXW** 0DTE column (never the monthly "SPX" book), Nasdaq = QQQ (+NDX), SPY third panel (HR:L10; RB D5).
  ES from SPXW/SPY, NQ from QQQ at the live ratio (~41 NQ pts per QQQ $) (HD:L143-144; DG-07:L31).
- Display: Read-as % King, low nodes Dim (~20% of King) but keep ≥12 rows (HD:L145-146; HR:L13).

### 2.2 The step order
Three orders are taught; they disagree on whether the chart or the map comes first.

**(a) The teacher's own live order (transcripts):**
1. Read SPX, SPY and QQQ together; if not "in alignment" expect chop and go to single names with relative strength
   (XSyb:L13, L16-17; AE9@c43422; fs8:L24-25). "the number one rule... you have to trade in the direction of the overall
   market" before single names (AE9@c10486).
2. Find the King (largest |value|) and the opposing major node; judge the range — 5-10 pts "not even worth it", 15 pts with
   clear ends tradeable, 30-50 pts best (bgkp:L121-124, L156, L195).
3. Discard decoys/hedge nodes and sub-four-digit nodes (G5O@c16477; XSyb:L22-23, L116).
4. Locate gatekeepers between spot and King and the air pockets (AE9@c31453; G5O@c43443).
5. Check skew/R:R: reject when upside to the next node is smaller than downside to the floor ("IONQ 3 up vs 7 down =
   negative", XSyb:L37-38); minimum 3:1 (XSyb:L90).
6. Check where price was delivered from (XSyb:L46; AE9@c65877).
7. Cross-check sector ETF / peers for single names (XSyb:L78-79; bgkp:L190-191).
8. Price action confirms: "charts and like price action is number one" for users (XSyb:L100-101; AE9@c32952), though he
   himself is map-first: "I don't look at charts" (bgkp:L42) / "Heatseeker becomes my primary" (470@c7481-c8976).

**(b) The vendor/docs 30-second order, adopted by the repo as R3 (≤2 minutes)** (HD:L154-162; HR:L24-32):
1. King — strike, value, sign, contested or not. 2. Floor and ceiling — the *biggest* node below/above, not the nearest.
3. Gatekeepers between spot and King; count them (dense = friction). 4. Air pockets — gaps in the strike grid and tiny rows.
5. Where spot sits — edge vs middle. 6. Building vs melting — velocity on floor/ceiling/King (Garma: 10-min).
7. Agreement across SPX/SPY/QQQ (+NDX). Write the read down with a timestamp.
Preceded by **charts first** (HD:L148-152; ACAD:L38-51: "Heatseeker is a CONFIRMATION tool, not a signal generator";
X-ray analogy; SDS step 1 per K2 §2.1).

**(c) Repo additions to the read** (HD:L164-178): R4 *name levels, never outcomes* (the map says where interaction is
likely, not what happens, because nothing in the vendor docs defines deflect vs pass-through, RB T14); R5 re-read
continuously, a frozen map is a different instrument; R6 widen everything or stand aside on FOMC, CPI, NFP, OPEX week,
earnings, first minutes after 09:30, last half hour, Rainbow Road; R7 watch for decoys.

**Garma's three pre-open passes** (GPR:L43-51): price (V-band wicks, double tops/bottoms, 1H/15M swings) → liquidity
(PDH/PDL, ON H/L, Asia, London, premarket, NQ 500s/1000s) → maps (King, floors, ceilings, gatekeepers, 2 of 3, tug of war).

### 2.3 Combining expiries
- **Nearest column dominates:** "closer date high node has more of a pull" because dealers care about the current-day
  expiration most (bgkp:L91-92); "I place a lot more emphasis on like current day columns" (AE9@c49414); "nodes that are
  closest to price are going to be the ones that matter the most" (G5O@c16477).
- **But don't ignore far nodes that are much larger:** "You don't want to ignore the nodes even if they're a week out, two
  weeks out, or 3 weeks out" (AE9@c47915; FSLR 250 example). When the next column's node is ~3x the current week's, it
  "kicks in" after Friday rolls off (AE9@c65877; DG-01:L13 MAP-F23).
- **Roll-off read:** re-read what the map becomes after today's column expires ("after 5/27 rolls to 5/28 the king node...
  is going to be at 420 and there's nothing below it", motn:L9-10); OPEX Friday nodes "wash off like really fast in the
  close" and the next column takes over (470@c31448-c32946).
- **Same strike across expiries** "getting slapped" in multiple columns = "incredibly bullish signal" (motn:L11).
- **Swing aggregation:** current + next 2-3 expiries at most (DG-06:L11); stair-step "up and to the right" across later
  columns (470@c2993-c5985; XSyb:L40-41).
- **This-week vs next-week disagreement** = divergence (bgkp:L189-190). Two far-apart big nodes → may settle near the
  midpoint (bgkp:L220-221).
- **Repo findings that constrain this:** "0DTE/front-expiry and all-expiry maps are different objects" (top-5 overlap
  0.81/5; SPXW 0.00/5) (RB D9; GTS:L524). No rule for blending expiries exists; DTE-weighted blending is a deferred item
  (RB Q12, K1 §2.2). "Never sum expiries" — the stored `value` is a 5-expiration sum and the 0DTE column gave different
  answers (GVS:L67). Gamma concentration by DTE: 1d = 5.5x peak, half-width 1.05%; "Everything outside ±3σ√T is
  decoration" (GTS:L515-526).

### 2.4 Reading the map as it changes intraday
- **Track values, not just positions.** −22M → −30M "node became stronger", likelihood of hitting rises (bgkp:L64);
  30M → 60M with flat price = magnet "has doubled" (bgkp:L105-107); new accumulation at empty strikes and its "delta rate
  of change" — 6470 doubling vs 6500 +15-20% → "dealers are positioning for a potential downside move" (bgkp:L132-137).
- **Velocity = freshness:** "the rate of change is going to be important because... that's kind of showing the freshness"
  (G5O@c16477); 30→45M in 3 min, QQQ 630 from ~0 to 14M "1400%" = "hot... in play" (G5O@c14978, c19472).
- **Bearish divergence:** price rises with no new nodes above while the node below grows in |value| → "still active... a
  very strong pole" (XSyb:L46-47; DG-04:L11 MAP-F41).
- **Breakout confirmation:** after a node is cleared you want it to WEAKEN; if it keeps growing "the pop is going to fade
  back down" (bgkp:L139-142). Hold for the far target only if the near node "starts to reduce in value and [the far] one
  continues to increase" (XSyb:L111-112).
- **Rolls:** ceiling diminishing while a lower strike grows = "lowering... the ceiling" (XSyb:L129-131); SPY below 670 →
  "670 becomes the king node... the floor has effectively rolled down", short a retest (fs8:L30-32). Academy: 1 = noise,
  2 = signal, 3 = confirmation; two strikes in one update = urgency; trail behind the rolling level (HR:L54).
- **Washed-off magnet:** a previously bright target shrinks after a near-tap → "dealers are done with it" (AE9@c37437-c38929);
  about half lost = spent (DG-04:L12 MAP-F32).
- **Killed node:** a node losing its value as price arrives = no trade there, or a knife-through; a reshuffle before price
  arrives voids the setup (HR:L44; HD:L170-171).
- **Reversal comes first:** "The reversal is going to happen first and then the true cards will start showing itself...
  buy loops" — use post-reversal accumulation to decide whether to hold (G5O@c14978-c16477, c22470).
- **Reshuffles:** 2-3 major shuffles a day for SPX/SPY/QQQ, otherwise "pretty stable" (XSyb:L107); after a King rejection
  "a high likelihood of a reshuffle" (fs8:L76); reshuffles after news are information (fs8:L73-74). Vendor T9: step back,
  re-mark King/gatekeeper, wait for stabilisation, "Never trade yesterday's map in today's market" (RB T9; SDS:L101).
- **Persistence filter (repo, VALIDATED):** a violent King down-migration reversed within 15 min; a state needs ECoM
  migration ≥0.12% of price over 3 windows on 2 of 3 maps; exclude 15:55+ windows (RB T26-T27; GTS:L341).
- **Measured status:** the roll arrives *after* price has moved 8-10 bps the same way and predicts nothing (HD:L115;
  DG-04:L32); a live map scored +367.1 vs +47.5 for a frozen 09:30 map (87% of in-sample edge), but that engine later
  failed out of sample (HD:L118; RB READ-FIRST 1).

### 2.5 Opening, midday, close, overnight
- **Opening:** "the first 30 to 45 minutes is when you see the most shuffling... that's why I say don't play the morning
  maps" (XSyb:L7-8); also stated as 15-30 min (bgkp:L88-89) and "I usually tell people to wait it out" for indices, single
  names earlier (AE9@c35940); "90% of all the institutional selling volume for options contracts happens in the first 30
  minutes" (AE9@c50913, unsourced). Exception for experienced users: price overshot the Kings at the gap with no prominent
  upside nodes on all three → fade until the reshuffle; invalidated by a fresh node accumulating above spot (XSyb:L8-9).
  Pre-market data not used, taps not counted (AE9@c49414); weekend/forward 0DTE maps not trusted (470@c8976-c11969).
  Early approach to a big node → rejection more likely (fs8:L62-65).
- **Midday:** 11:00 lunch = range, "data chop hour"; 12:30-1:00 re-solidifies (bgkp:L90-93); lunch 11:20-11:30 "you should
  not even be trading" (G5O@c22470).
- **Afternoon/close:** afternoon SPX nodes "even stronger than during the morning... that's the charm effect" (bgkp:L201);
  0DTE gamma "grows stronger and stronger as you near the close" (G5O@c38954); late approach → "the possibility of it
  pinning there is going to become higher" (fs8:L62-65); 3:30 ET "Robin Hood liquidation" reshuffle; MOC last 10 min
  "major shuffling" (bgkp:L83, L90-93; XSyb:L14-15; 470@c28450). Close forecasting is impossible: anyone who could "would
  literally become a trillionaire" (bgkp:L83-84). Garma MOC read: ceilings rolling down / upside nodes growing show MOC
  direction; MOC usually adds positive nodes (HR:L102).
- **Day of week:** Wed-Fri favourite, "the magnets just become stronger and like charm kicks in"; Monday entries need more
  room (470@c47914); Mon/Tue entries for Friday targets need 5:1-10:1 because the map may reshuffle before Wednesday (fs8:L82-83).
- **Overnight / next day:** end-of-day map carries into the morning; overnight nodes playable (XSyb:L7, L10); but "once
  Monday opens like everything is going to change" — "I open up the heat map and I let Gex tell me" (fs8:L72-73).
  Week-over-week: compare last week's King with this week's (bgkp:L236-237). Repo: single-stock maps are unchanged close →
  pre-open, SPXW/QQQ change (DG-04:L36); overnight node levels carry no reversal edge on ~370 nights (ONL:L17-26); a captured
  map needs an expiry (ONL:L98-106).

---

## 3. Named setups and playbook rules (as reading rules)

| Setup | What the map should show | Expected read | Invalidation / caveat | Source |
|---|---|---|---|---|
| **King / major-node reversal** (the core method) | Price approaching an untested King or major node, nothing major beyond | Reaction within ±5 SPX pts; "I'm a reversal trader", no breakouts | Close back beyond the node; reshuffle; R:R <3:1 | bgkp:L112-113, L74-76; AE9@c23973; fs8:L35-36 |
| ±5 padding / purple undercut | Purple node | Undercuts 3-5 pts ("hunt... five points below") then reverses; QQQ ~50c overshoot | 8-10 SPX = wrong; >20 NQ pts invalidates | bgkp:L148-150; 470@c29950; fs8:L26; DG-02:L29 |
| **Tap-count decay** | Same level retested | 1st play it; 2nd "like 66%"; 3rd "33% or less", i.e. 2/3 chance of breaking | SPX broke on 4th, TSLA 5th, 6500 on the "13th" (likely "third", ERR A5) | bgkp:L129-131; AE9@c29953; 470@c17960; HR:L40 |
| **Gatekeeper bounce/rejection** | Major node (≥¼-⅓ King) between spot and King | First test "very very high chance of a bounce"; untapped gatekeeper rejects; clean break → "accelerates into the cleared zone" | Each tap weakens it; a larger gatekeeper "could become the king" | AE9@c26962, c32952; fs8:L57-62; HR:L39 |
| **Range fade / equal pull** | Two similar magnets either side | Range/whipsaw; fade both ends, never the midpoint | Equal split with no clear ends = no setup | bgkp:L107-108, L155-161, L191-192; HR:L21 |
| **Purple-to-yellow** | Downside purple floor, upside yellow target | Purple floors "hunt liquidity" first (low limit below); "higher success rate with purple being the floors" | Yellow floors "a lot of times... just kind of falls through" | XSyb:L18-21, L35, L83-84 |
| **Floor + air pocket + target** ("buy the dip map") | Floor at/under spot, empty strikes above, bright node beyond | Fast travel through the pocket to the target | No floor = no long; floor lost = flush | DG-03:L7-10; HR:L62-63 |
| **Ceiling + air pocket short** | Mirror | — | — | DG-03:L8 |
| **Rug pull** | Floor tested repeatedly, price sitting on it, ceiling being lowered | "quick swift rug pull" | Damped if another index is sandwiched; QQQ "fat floor" can veto an SPX rug | XSyb:L128-134; AE9@c43422 |
| **Reverse rug** | Purple over yellow | If price claims the purple, "buy loop" to the next node; "never short into one" | Fails to clear the purple | G5O@c25466; HR:L51 |
| **Sandwich / pin** | Floor and ceiling tight around price | "pinball within this range"; Garma: pinned = stay out | — | XSyb:L132; GPR:L22 |
| **Ceiling roll-down / floor roll-up** | Ceiling re-forms lower / floor higher across updates | Bearish / bullish; short the retest of the new King; trail behind it | Measured to lag price | fs8:L30-32; XSyb:L129-131; HR:L54 |
| **Breakout confirmation** | Price clears a node | Continue only if the broken node weakens and upper nodes grow | Broken node keeps growing → pop fades back | bgkp:L139-142, L81-82 |
| **Purple break = brief squeeze** | Price breaks a purple ceiling/floor | "brief moments of like a gamma squeeze" then reverts to the major King ("rainbow boost") | — | fs8:L44-45, L55 |
| **Overshoot snap-back** | SPY/QQQ overshoot their King | "has to snap back... especially if there's no further downside accumulation" | Fresh accumulation | AE9@c26962 |
| **Trend day** | All nodes "pointing to the upside"; stair-step accumulation | Straight trend | — | bgkp:L174-175, L193-194; HR:L64 |
| **Stair-step VEX swing** | Current week near a GEX floor; later columns' Kings step higher; one direction only; VEX agrees; ≥3:1 exposure above vs below | Buy the floor, target a "realistic" VEX node 1-4 weeks out | Two-way stair-steps; PA disagrees; reward <10% | 470@c2993-c5985; motn:L8-16, L12-14; DG-06:L12 |
| **Far-dated magnet** | Later-dated node ≥3x current-week nodes | Current-week floor toward it | No further same-week accumulation | AE9@c65877, c71867 |
| **King stacked on GEX and VEX** | Same strike on both maps all week | "you don't ignore that" | — | 470@c23956 |
| **Hedge-node / decoy filter** | Far-OTM node before data/FOMC/OPEX; dormant velocity | Ignore; fast growth would make it "in play" | — | bgkp:L109-111; G5O@c19472 |
| **Delivered-from** | Node price just launched from / was rejected at | Used-up wall, downgrade | — | bgkp:L184-185 |
| **Nothing below spot** | After a large gap down, map all upside | Dip-buy read with flow | — | motn:L66-67 |
| **Chase filter** | Most of the move to the node done | Poor R:R, skip | — | XSyb:L89-90 |
| **Midpoint / symmetric** | Price midway between King clusters | No trade | — | 470@c32946; HR:L21 |
| **Chop map / Rainbow Road** | Two Kings in a tight range, or significant nodes "all over the map" | Chop; stand aside. "No big node does NOT imply chop" | — | AE9@c52410, c55404 |
| **Too good to be true** | Very large upside on the map | Suspect a trap | — | XSyb:L56-57; AE9@c73366 |
| **Garma stack** (map as filter) | Session-level sweep + IB 0.5/0.618/0.786 golden zone + 2-of-3 node confluence | "Maps choose the IB side": capped upside + downside nodes → IB low breaks first; "the sweep isn't the trade; the reaction after the sweep is" | Node killed on arrival; >20 NQ pts through | HD:L238-249; HR:L80; GPR:L13-14 |
| **Vendor patterns** | Whipsaw (≥2 high nodes, few between); Trend/King re-crowning (stair-step crowning beyond); topping/bottoming stair-steps on VEX; pin job (EOD) / drive-away (early) | as named | rug/reverse-rug/beach-ball/spring are not in the official docs | SDS:L168-213 (K2 §3); RB T13 |
| **GEX/VEX four states** | Sign agreement per strike/book | +/+ fade extremes; −/− momentum; +G/−V "calm fades fail"; −G/+V "panic low, violent bounce"; flip of both at one strike = "structural breakout zone" | Directional claims FAIL on 305 days | ACAD:L65-80; GVS:L9-14, L46 |

---

## 4. Regimes, flips, pins, vanna/charm, VIX, single names, OPEX/earnings

### 4.1 Positive vs negative gamma
- **Taught, node level:** yellow = "suppressive", price slows; purple = "oppressive or a lot more aggressive", "fuel on fire"
  (bgkp:L72-74); "negative GEX is going to be a lot more aggressive... overshooting and then eventually coming back down;
  positive... a little bit more like suppressive" (fs8:L43-44); purple is pro-cyclical — "if you're selling then dealers are
  going to sell into the move"; clearing it gives a dealer "buy loop" (G5O@c25466, c29964). Both signs attract: "it doesn't
  matter if the node is going to be negative or positive... they're going to have a pull on price" (fs8:L43); a negative
  node above can be resistance or support (fs8:L50). The only consensus rule in 96 videos: yellow damps, purple accelerates
  (DG-05:L7 MAP-F10).
- **Exception (Glitch):** buy a major negative node for a V-reversal if volatility is not spiking; trust floors in low vol
  (DG-05:L8; DasbJL9ZDvw@0:22:29).
- **Book level (repo/mechanism):** the regime is the sign of TOTAL dealer gamma at spot, not any node's colour; "A NODE'S
  COLOUR IS NOT THE REGIME"; SPY King −$202,794K and QQQ King +$91,806K at the same minute on 0.999-correlated tapes
  (GTS:L48-51). +GEX = fade extremes, breakouts fail; −GEX = momentum, fades get run over (GTS:L35-41). "Purple ≠ bearish"
  (GTS:L57; ACAD:L62).
- **Day types:** Range (+γ, stable floor/ceiling, fade extremes, wider stops/tighter targets); Trend (−γ, King growing,
  rolling, air pockets, follow); Whipsaw (−γ with conflicting maps; fade the outer bounds or sit out); range→trend
  transition often "the best entry of the day" (HR:L63-66). Day type comes mostly from map geometry, not sign (DG-05:L68).
- **Measured:** range ratio neg/pos ≈1 within-day (HD:L114); 0DTE SPXW negative → next-hour range 1.09 [0.90, 1.35], the
  only cell leaning the doctrine way (HD:L119, L331); final 10 min smaller when 0DTE index gamma is positive (16.9 vs 23.0
  bps SPXW, uncontrolled) (DG-05:L73).

### 4.2 Flip level
- Never taught in any of the 7 transcripts (T1 §4, T2 §A4, T3 §4). Vendor API exposes `summary.flip` (HD:L95). Repo:
  compute by re-pricing total gamma at candidate spots; above = damped, below = amplified; it moves intraday; "If you are
  reading only the terminal ladder, you do not have the flip" (RB D2; GTS:L53, L98-111). Flip-cross-and-return as a trade:
  FALSIFIED / inert (+0.3 to +0.9 pts vs +12 bar) (RB G28). Polarity flip (crossing + → −) = "rug pull", (− → +) =
  "slingshot" (HR:L56).

### 4.3 Pinning / magnet / reversal claims
- Magnet and wall at once (bgkp:L60-61, L98); King = settlement target; early drive-off, late pin (HR:L38; SDS:L15, L18);
  early approach rejects, late approach pins (fs8:L62-65; ERR A1 corrects a dossier that reversed this); stubborn SPY King
  pins ~$1 (HR:L48); low-VIX afternoons drift to the biggest strike (charm) (HR:L76). Not a close predictor (bgkp:L83-84).
- Larger node wins the "fight between the magnets"; +22M vs −17M ≈ 60/40 (470@c5985; DG-01:L29).
- Reversal odds stated: 2nd tap 66%, 3rd 33% (AE9@c29953); "A double bottom has a 67% chance of a reversal" (G5O@c28465);
  round numbers "high high chance of reversal" (G5O@c29964).
- **Measured:** King magnet NULL (price got closer only 40-48% of the time); late pin NULL; first-tap deflection at
  ≥25%-King nodes 71/73/70% vs any strike with the same geometry 72-76% (random-walk arithmetic); later taps reverse
  slightly *more* (HD:L110-112, L119). Literature cited by the repo finds anti-pinning before S&P index expiry
  (GTS:L672-673, L694). "Delta hedging... has no target" (GTS:L693).

### 4.4 Breakouts through negative gamma
- "very rare that price is going to break through purple and squeeze"; can be claimed as a floor only if an even larger
  node above keeps growing (bgkp:L81-82). Break of purple = "brief" squeeze then reversion (fs8:L44-45, L55). Clearing purple
  → buy/sell loop (G5O@c25466). Breakouts valid after a liquidity hunt below support or after repeated taps with upside
  accumulation (G5O@c34459; AE9@c41926). "stop trading breakouts" (G5O@c28465); Beach Ball "We do not trade breakouts" vs
  Academy "accelerates into the cleared zone" (HD:L298, CONFLICT). Repo: put wall is "a magnet with the hedge flow on the
  side of the break" — never lean a stop under it (GTS:L217-227); literature: unconditioned fades of level breaks fail,
  breaks continue 2+ hours (GTS:L697).

### 4.5 Vanna (VEX) and charm
- GEX for 0-5 days, VEX for 2-4-week swings (470@c1496; motn:L8, L12); "I generally always prioritize... GEX and I look for
  VEX to be a supporting factor"; "I don't have a clear explanation of like why it works... I can just tell you it works"
  (AE9@c44921). VEX nodes "seem... completely out of like right field" (fs8:L17). VIX >20 toward 25-30 hands control to VEX;
  gamma back at ~17-19; VEX irrelevant for 0DTE 80-90% of the time (DG-06:L10). TheArchitect (one clinic): negative VEX above
  + IV falling = dealers buy; positive above + IV falling = top; IV rising = sell either sign (DG-06:L14).
- Charm: folded into the backend (bgkp:L201-203); explains stronger afternoon nodes (bgkp:L201) and cleaner Wed-Fri magnets
  (470@c47914). Never a separate map. Repo: no charm is computed anywhere (GTS:L544); post-14:00 charm/vanna pin trade
  FALSIFIED (RB G32). User directive: GEX only for day trades, VEX for swing/watchlist only (RB D15).

### 4.6 VIX map
- Read like any ticker: weekly range between a VIX floor and ceiling. Late Sep 2025 range 15-17, close 15.44 at the floor →
  "the range to the upside is more probable" → play defence (AE9@c3000). A "major... put floor at 15"; far December nodes at
  55 and 100 = "people are worried... major pullback into December" (470@c58403, c61400-c64395). VIX King 32 in the Nov column
  + SPX VEX node = "the only indicators you need to be on defense" (fs8:L19); but "VIX spike doesn't mean upside or downside,
  but it means volatility" (fs8:L54), not a signal to "go full port short" (fs8:L39-40).
- Wider corpus: VIX floor with nothing below = bearish indexes; far lit VIX strike = fear/hedge; a VIX that does not spike
  on a dip confirms a long; expiring VIX column dead; Wicks prefers VIX GEX (DG-06:L15-16).
- Not in RB/GTS/SDS at all (K1 §4, K2 §4.6). The only VIX rule there is the VIX 10-minute pivot rule, whose "~88%" is the
  author's unmeasured claim (RB T68). All VIX-map rules untested; VIX map forward-only since 2026-10-02 (DG-06:L46).

### 4.7 Single names vs indices
- Indices most liquid; NDX and XSP "too illiquid" — use QQQ and SPX/SPY (bgkp:L44-49) (Garma later uses NDX as a fourth
  map, DG-07:L67). Single names: four-digit nodes, seeding history, sector ETF + peers must agree ("if they're not all in
  alignment then it's just a crapshoot", bgkp:L190-191, L205-206), broad-market map must support the name (bgkp:L219-220;
  AE9@c10486), avoid memes ("scary to trust dealer exposure for memes", AE9@c61381) and all-time highs (XSyb:L24, L100), each
  ticker has a "personality" (AE9@c76363). Single names can be traded earlier in the session than indices (AE9@c35940).
  Cross-asset: COIN/MSTR map as a Bitcoin read (fs8:L10-14; G5O@c44943).
- Repo: index 0DTE maps are dense (~5-pt spacing), the video doctrine came from sparse single-stock maps (next node 15-45
  pts away); "Rules do not transfer between the two"; the four mechanised video gates hurt on index 0DTE but that "does not
  disprove the rules for single stocks with sparse maps" (RB T38; GTS:L267-268).

### 4.8 OPEX, FOMC, earnings, quarter-end
- OPEX: quad-witching column "taken with a grain of salt... a lot of manipulation"; OPEX "always has like... very wacky
  nodes"; play third-Friday nodes "as lottos" (XSyb:L30-31, L54, L99); yet recent OPEX weeks "have been fine" if trading
  deflections, not chasing (fs8:L37-38); Friday exposure washes off and the next column kicks in (470@c31448); an OPEX target
  may not be hit "because" it is OPEX (470@c38934). Vendor: OPEX-week nodes carry less weight; clarity improves after (SDS:L223).
- FOMC/data: decoy nodes ~100 pts OTM (G5O@c4495); no pre-FOMC deflection (G5OutDv14Qo@0:27:20, DG-05:L20); Garma 7/29 FOMC "maps
  completely useless" (HD:L175); hedge nodes before CPI/PPI (bgkp:L109-111); claims maps work on FOMC/earnings (bgkp:L104-105).
- Earnings: COST "very very low liquidity in terms of the dealer exposure after earnings" (AE9@c50913); VEX used ahead of
  LULU earnings (AE9@c46418); hedge nodes appear around earnings (SDS:L31). No earnings-specific reading rule exists in
  RB/GTS/SDS.
- Quarter-end rebalancing makes exposure swing "very very violently" (AE9@c4498).

### 4.9 Cross-ticker confirmation (Trinity)
- "you have to look at SPX, you have to look at SPY, you have to look at QQQ"; QQQ "at least 50%" of S&P positioning; if
  QQQ is topping, SPX/SPY upside nodes probably won't be reached (fs8:L24-25; AE9@c43422). Divergence = "no play... chop...
  whipsaw" (G5O@c4495; bgkp:L164-166). ±5 tolerance is shifted by cross-ticker context (G5O@c47936). Rolling up across all
  three confirms a second leg (470@c17960).
- Academy/repo-taught: all three = full size, 2 of 3 = minimum, 1 of 3 = skip; SPXW disagreeing counts more than a QQQ lag
  (HR:L69-73). Two senses of "divergence" (maps pointing different ways vs prices moving unequally) are conflated (DG-07:L72).
- Measured: Trinity 2-of-3 +3.1 pp ns; 3-of-3 worse than 1-of-3 on SPY; the 66% is just the fraction 2/3 (HD:L121, L280;
  DG-07:L41, L71; ERR B).

---

## 5. Accuracy and edge claims

### 5.1 The teacher's claims (verbatim numbers)
- Inference confidence "80 to 85%... other people are flipping a coin and doing 50/50 guesses" (bgkp:L9-10, L52, L85).
- Second test "like 66%" (bgkp:L130, L150); third "33% or less" (AE9@c29953); first touch ~80% is credited to "the
  academy", never said in the videos (ERR A7; DG-02:L10).
- Double bottom "67% chance of a reversal" (G5O@c28465).
- Watch-list "hit rate would probably be like... 85%... for the week" (XSyb:L3).
- VEX: "if I treat it like the Bible, like my hit rate's probably like 50% or like 60%", hits are "massive massive runners"
  (AE9@c46418); "minimum 500 to 1,000%" (fs8:L18).
- Trinity 3-of-3 "85 to 90%" (DG-07:L13, no sample).
- Win-rate framing: "even if you have a 40% or 50% win rate, you will be a profitable trader" at 1:3; best traders "lower
  than 60%" (motn:L14-15, L94).
- P&L anecdotes (case-selected): UNH "5,000%" (really ~1,900% by his own numbers, ERR B), CRWD "3,000 to 5,000%", MSFT
  "3,000% plus", "2,000%" SPX contracts, some puts "10,000% plus", "zero draw down" repeatedly (470@c0, c22458, c29950;
  fs8:L18-20; XSyb:L84). "90% of all my profits... come from SPX" (AE9@c17979); YTD "342 or 41%" (bgkp:L44).
- Hedges: "it's not always going to be right" (bgkp:L189); "if we can know this with certainty... I would not be selling
  it" (fs8:L63-64); admits ~70% of trades expire at zero (DG-16, WSQDM-gz9Zo@0:44:26).
- Garma: "80-90%" / "70-80%" / "10 out of 10" / "60-70%" / "pretty low"; 191 recapped trades with 87% stated hit rate while
  daily scorecards show 3/6 and 4/6 (HD:L227-228, L259). IB-fib "70-80% alone" (HD:L120). Overnight range breaks ~95% (HR:L82).
- VIX 10-minute rule "~88%" (author's claim, RB T68).

### 5.2 What the repo measured (kept separate)
- First tap 69.9-72.7% at big nodes vs 72.4-76.1% at any strike; no decay (HD:L112; DG-02:L36).
- King magnet / late pin NULL; yellow vs purple lead does not replicate on 0DTE SPXW (−1.5 pp); regime → range NULL; rolls
  lag price; slip-in direction NULL (HD:L110-119).
- Trinity 3-of-3 rates 75.2% / 60.5%, below the claimed 85-90% (DG-07:L41).
- IB-fib golden zone 32.0% win at 2R vs 33.3% breakeven (NQ 332 sessions; QQQ 879) (HD:L278).
- Overnight range breaks 93.1%, but a random same-width range breaks 91.1% (geometry) (HD:L282-283).
- Engine: baseline −0.0201 R/day (283 sessions); direction right 40.9% of 1,348 plays (−6.7σ); 22 of 22 registry
  candidates dead; only holdout +0.24 R/day at t = 0.80 (GTS:L15, L66, L572-580). Mechanised 3:1, tap cap, dominance, clean
  path all lost money (RB G12-G15; HD:L117).
- GEX overnight node levels: 20-night pass (+5.5 pts) failed on ~370 holdout nights (+0.1 pts) (ONL:L17-26).
- GEX x VEX four states: next-day SPY does not separate by state; vanna adds nothing inside a gamma cell (GVS:L41-50, L68).
- Summary line: no core claim "shows up as a measurable price effect" on 55 days (HD:L29-31); "The mechanism is real and well
  documented. The edge is not demonstrated." (GTS:L15). Hermes standing prompt lists King magnet, first-tap 80%, colour,
  rolls, slip-ins, Trinity, IB-fib and the 83-rule playbook as dead (HAP:L98).

---

## 6. Contradictions and ambiguities

**C1. Colour vs sign.** 2025 videos and the Academy: purple = short gamma (negative), yellow = long gamma (bgkp:L77-80;
ACAD:L56-59). The background rule (yellow background = massive negative node) is consistent only on a diverging scale
(XSyb:L10-12; T2 notes §6). The 2026 docs: viridis colours by value rank, "yellow = highest value, purple = lowest", sign
not encoded (HD:L74-79). G5O never states the colour-sign mapping; T3 could only infer it from signed values. Resolved in the
repo as "number wins" (HD:L79; HR:L15).

**C2. Magnet vs wall.** "It's a magnet and it's a wall" wherever it is (bgkp:L98) vs delivered-from and tap-decay caveats
(bgkp:L129-131, L184-185). No source defines when a node attracts vs deflects (RB T14; GTS:L238). Glitch's only
reconciliations: pull from afar, deflect on arrival; purple reverses only when volatility compresses (DG-01:L59). Glitch moved
from "magnets" to "walls" in 2026; Garma and Giul kept magnets (DG-02:L70).

**C3. Purple behaviour.** "Very rare" to break purple (bgkp:L81) vs purple "aggressive" approach (bgkp:L73); purple below
spot = "cushions and... reversals" (G5O@c4495) vs pro-cyclical "sell into the move" (G5O@c29964); purple floors have the
"higher success rate" (XSyb:L20-21) vs "Be cautious buying into Barneys" (DG-05:L7). Negative node below: floor vs flush, and
Glitch's reconciling variable is whether vol is spiking (DG-19:L14).

**C4. Positive node behaviour.** Yellow damps and deflects (G5O@c7488) vs yellow floors "a lot of times... just kind of falls
through" (XSyb:L20-21); positive gamma = brake (Glitch) vs fuel (Garma) (DG-01:L51); Garma "negatives only amplify, play
deflections off positives" vs "a negative King can be a floor by absolute value" (HD:L257).

**C5. Chart first vs map first.** Users must put price action first (XSyb:L100-101; bgkp:L65-67; ACAD:L39-41) while he trades
map-first ("I don't look at charts", bgkp:L42; 470@c7481). Garma flipped from map-first (July) to chart-first (2 Sep 2026)
(DG-16).

**C6. Opening window.** 15-30 min (bgkp:L88) vs 30-45 min (XSyb:L7; bgkp:L247) vs "any rule that I share is just a rule"
(AE9@c50913) vs SPY 674 at 9:30 read as the day's ceiling and early-day King fades (fs8:L35-36, L62). Glitch's ban decayed
to a beginner caution; his main window became 9:30-10:50 by Jan 2026 (DG-11:L3, L52).

**C7. Tap decay.** 80/66/33 (AE9@c29953) vs breaks on the 4th, 5th and 13th tap (470@c17960; AE9@c40426; bgkp:L138) vs the
double-bottom 67% (G5O@c28465), which treats the second test as the high-probability one; tap count resets when a node is
building at its peak (RB T39).

**C8. Gatekeeper size.** ≥¼ (fs8:L62) vs ~⅓ example (fs8:L58) vs 25-33% / 60% strong (HD:L87) vs ≥70% in the only tested
version (RB G27); "five gatekeeper definitions" (DG-02:L71). Whether a growing gatekeeper overrides the King is discretionary
(AE9@c32952 vs 470@c28450).

**C9. Air-pocket threshold.** <10-20% of King (G5O@c43443) vs <20-30% (Garma) vs "I just look at the map" (G5O@c44943); the
code uses <10%; dim mode (MIN %KING 20%) makes it uncomputable (RB F46; GTS:L156-160).

**C10. Floor/ceiling definition.** Docs: either sign, the biggest node; Academy rolling article: the largest positive node
(HD:L86). Rug defined five ways (DG-03:L63).

**C11. Far nodes.** Hedges/decoys (Glitch 2025) vs targets/destinations (Giul, Garma 2026) (DG-05:L62); the same far shape is a
"hedge note" (QQQ 575) or a lotto-worthy VEX target (ORCL 230, SPX 6600) (XSyb:L22-29, L53; fs8:L17).

**C12. Expiry weighting.** Current column first (AE9@c49414) vs don't ignore nodes 1-3 weeks out (AE9@c47915); weekend 0DTE
maps untrusted (470@c8976) vs end-of-day map "still in play for tomorrow" (XSyb:L7) vs "once Monday opens like everything is
going to change" (fs8:L72-73).

**C13. OPEX.** Grain of salt / lottos only (XSyb:L30, L54) vs "fine" if trading deflections (fs8:L37-38).

**C14. Lead vs lag of map changes.** Garma/Giul act on the roll; Glitch says the reversal comes first (G5O@c14978); the
repo measured rolls trailing price by 8-10 bps (DG-04:L53; HD:L115).

**C15. Breakouts.** "We do not trade breakouts" (HR:L53) vs gatekeeper break "accelerates into the cleared zone" (HR:L39) vs
literature showing breaks continue 2+ hours (GTS:L697).

**C16. Trendlines.** "You don't need to use trend lines anymore" (bgkp:L68) vs heavy trendline/wedge use (motn:L22-27, L79-80).

**C17. Teacher's arithmetic.** "50%" growth was +36%; "x3" was ~11x; Rule of 16 at VIX 24 is 1.5%, not 1.2%; UNH 5,000% was
~1,900% (ERR B).

**C18. Repo-internal.** Ladder depth ≥40 strikes (RB I23) vs exactly 12 nodes per tape (RB A2); %King sign against a negative
King is undefined (RB F47); %King integer quantisation means "never rank two nodes that differ by a single displayed point"
(RB F48); the hand-walked corpus is unsigned and excluded the King cell, so its "King" is a substitute (RB F44); colour as
regime (SDS) vs book-total sign as regime (GTS:L48-53).

**Units ambiguity throughout:** no teacher states the unit, formula or sign derivation; "four digits", "far" and "static" are
untestable until fixed (DG-01:L56).

---

## 7. Gaps — what the sources do not supply
- No formal unit or sign definition from the teacher; the inference layer is a black box (470@c56903).
- No flip level in any transcript; Skylit's terminal does not display one (GTS:L53).
- No rule for netting or weighting 0DTE vs weekly vs monthly columns beyond "nearest column first" and "far nodes only if much
  larger" (RB Q12; GTS:L524).
- No charm map; no earnings-specific map rule; VIX map rules come from Glitch plus one clinic and are untested (DG-06:L5, L46).
- No attract-vs-deflect boundary (RB T14).
- The wider 96-video corpus (Garma 58, Glitch 16, Giul 13, Wicksy panel, SkylitAI, skylit cat) is synthesised in
  `knowledge/skylit_videos/synthesis/chapters/` (21 chapters, ~1.7 MB) with digests used here; the raw per-video extractions
  in `knowledge/skylit_videos/batch/` were not re-read, and the ERRATA say those batch files are not yet patched (ERR:L4-5).
