# GT-Analyst
Game-theory news analysis agent for Claude Code. Four-skill brain — **jiang-doctrine** (geopolitical salience),
**formal-game-theory** (rigor/validity + modern-GT module: global games, Bayesian persuasion, cheap-talk coarseness),
**market-transmission** (turns a headline into a dated cross-asset call via the supply-vs-demand shock fork),
and **contrarian-red-team** (10 frameworks for contrarian calls + adversarial self-testing: ACH, premortem,
reference-class forecasting, cascades, reflexivity/Minsky, neglected risk; mandatory red-team gate at conviction >= 0.65) —
plus continuous news ingestion, conviction-scored sector/ticker mapping, a Brier-scored prediction ledger
(`redteam` self-audit command, Murphy decomposition, correlation clusters), and a themed watchlist that
auto-triggers headless analysis when your tickers hit the tape.

## Setup (Windows)
1. Open this folder in Claude Code. Skills auto-load from `.claude/skills/`.
2. Copy `.env.example` to `.env` and fill in what you have:
   - `NEWSAPI_KEY` (newsapi.org, free tier) and `FINNHUB_KEY` (finnhub.io, free tier) — optional; RSS-only works with none. APIs are polled every 3rd run to respect free tiers.
   - `CLAUDE_BIN` — path to the claude CLI, needed for auto-trigger. Install with `npm install -g @anthropic-ai/claude-code`, then `where.exe claude` and paste the path.
3. Seed the calibration ledger once: `python tools/seed_ledger.py` (8 Jiang §12.9 predictions).
4. Start continuous ingest (every 5 min, silent, per-user, no admin):
   `powershell -ExecutionPolicy Bypass -File tools/register_task.ps1`
   Teardown: `tools/unregister_task.ps1`. Health check: `logs/ingest.log` (one line per run).
5. Edit `watchlist.json` — your tickers, company-name aliases, optional theme keywords.

## Dashboard
See everything in one place — ingest health, the prediction ledger, calibration, watchlist/auto-trigger activity, and rendered reports:
```
powershell -ExecutionPolicy Bypass -File tools/start_dashboard.ps1
```
(or double-click `tools/start_dashboard.ps1`, or run `python pipeline/dashboard.py`). It opens `http://127.0.0.1:8787`. Stdlib-only, read-only, localhost-only — no dependencies, never writes or trades. Tabs: **Overview** (ingest stats + activity), **Predictions** (ledger + conviction-band calibration), **Watchlist & Triggers** (config + auto-run decision log), **Reports** (click any analysis to read it), **Tape** (feed health + latest headlines). Auto-refreshes every 30s.

## Daily loop
- **Analyze:** tell Claude **"analyze inbox/latest.md"**. It triages, runs the schema, logs conviction-scored predictions, and archives the inbox.
- **Score:** `python pipeline/ledger.py due` → `resolve <id> <1|0>` → `report` (calibration by probability bucket, conviction band, sector); `void <id> --reason` closes a conditional whose trigger never fired; `report` also prints skill vs coin/base-rate and per-cluster/horizon Brier).
- **Before logging:** `ledger.py add --dry-run ...` (wording lint) and, for any level/range call, `python tools/range_odds.py` (no-view odds).
- **Outside view and live probabilities (2026-09-20):** every row carries a reference (`--base-rate` + `--base-class`, `--market` + `--market-src` where a liquid market exists; `ledger.py ref <id>` for open rows) and `report` scores the engine's EDGE over it with cluster-resampled intervals. Probabilities are live: `ledger.py stale` -> `revise` / `confirm`, scored time-weighted; `resolve --asof` stops the clock the day the outcome was known. Iran-cluster rows are durations, markers, levels or invariants (doctrine 16.18); `python tools/cycle_odds.py` prices durations. Background: `reports/20260920_research-improving-the-engine.md`.
- **One-shot cycle without the scheduler:** `python pipeline/run.py` (add `--headless` to also run the analysis via `claude -p`).

## Daily analyst (typed, propose-only)
`tools\start_analyst.cmd` runs it once and schedules it twice a day (`tools\register_analyst_task.ps1 -Times "07:00"` for once). Each run takes everything ingest collected, triages **every** item, runs the full four-skill analysis headless via the Claude Code CLI, and writes:
- `reports/daily/<stamp>.md` - the human report;
- `proposals/<stamp>/analysis.json` - the **typed** analysis (`pipeline/schema.py`: strict dataclasses + rules R01-R27 = the output schema, conviction rubric and pre-ledger gates as code; `python -m unittest tests.test_schema` covers every rule);
- `proposals/<stamp>/REVIEW.md` - what it proposes and which rows the rules BLOCKED.

**Per-article stage - Jev.** With `TYPESAFE_API_KEY` in `.env`, TypeSafe AI's Jev model gives every article a typed verdict (triage, capital tier, shock type, lane, lean, salience, state-change, injection flag) before Claude sees anything - about a cent per 1,000 articles. It never discards alone (watchlist, primary-source, low-confidence and state-change items always pass through), and it falls back to a keyword pre-cut without a key. `python pipeline/jev.py questions` prints the question set; `python pipeline/jev.py try "<headline>"` makes one live call. Optional: `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai` gives Claude Code TypeSafe's own reference skill for editing those questions.

**In Claude Code:** `/jev-triage`, `/analyze-news`, `/review-proposals`.

Nothing reaches the ledger until you approve: `tools\review_proposals.cmd`, or `python pipeline/analyst.py approve <stamp> --ids p1,p3` / `reject <stamp> --all`. The run cannot write the ledger itself - protected files are hashed before and restored after. Settings: `config.json -> "analyst": {"max_runs_per_day": 2, "model": "", "max_items": 120, "web": true}`. Health: `logs/analyst.log`, `python pipeline/analyst.py status`.

## Watchlist (themed, with a main index per sector)
`watchlist.json` is organized into themes (robotics, space, memory, photonics, chips, ai_datacenters, hyperscalers, defense, macro), each with a **main index** (BOTZ, ARKX, SMH, EUV, SOXX, DTCR, MAGS, ITA, SPY). ~274 tickers. Company-name aliases boost recall; word-like tickers (ARM, NET, FLY, PATH…) only match with `$SYM` or `(NYSE: SYM)` context. The dashboard's **Watchlist** tab shows every theme, its index, and each ticker colored by tier.

## Auto-trigger (tiered watchlist → tokens)
When ingest finds fresh news matching a watchlisted ticker it writes `inbox/triggered/<ts>_<TICKER>.md`. **Tiering:** only tickers in `config.json → auto_trigger.auto_tickers` (the ~85 "bigger names") dispatch a token-burning headless analysis; every other match is **watch-only** — recorded and shown in the dashboard, but no spend. Set `tier_enabled: false` to let all names trigger.

**Ships in dry-run**: decisions log to `logs/autoruns.jsonl`, nothing runs until you set `dry_run: false`. Guardrails: per-ticker cooldown (90 min) · max 2/hour · 8/day · single-flight lockfile · `model: sonnet` + `max_turns: 25`. Kill switches: `enabled: false` or unregister the task. Dropped batches stay in `inbox/triggered/` — nothing is lost.

## Phone notifications (Telegram)
When an auto-tier analysis actually **runs**, GT-Analyst sends you a Telegram message. Setup (once):
1. In Telegram, message **@BotFather** → `/newbot` → copy the token.
2. Put `TELEGRAM_BOT_TOKEN=<token>` in `.env`.
3. Open your new bot, send it "hi", then run `python tools/telegram_setup.py` → copy the printed `TELEGRAM_CHAT_ID=<id>` into `.env`.
4. Test: `python pipeline/notify.py "hello"`.
Stdlib-only (`pipeline/notify.py`), works from the headless pipeline, no-ops safely if unconfigured. Not SMS — alerts arrive in your Telegram app.

## Quality control
- Logic evals: solved exercises in `references/GT_book.pdf` — ask Claude to solve, compare to book.
- Judgment evals: `evals/backtests.md` — 10 frozen-input historical cases with grading protocol.
- Calibration: the ledger's conviction-band report is the payoff loop — if high-conviction predictions don't out-score low-conviction ones, the rubric weights are wrong.

## Not investment advice
This produces analysis with explicit uncertainty, not trade instructions. Doctrine §14: this layer
does direction/mechanism, not magnitude/sizing. Everything derives from public information, timestamped.
