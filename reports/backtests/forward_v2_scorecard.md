# Forward test: v2 stock-call candidate

Pre-registered. The rules in `tools/gt_stock_backtest.py` are frozen; changing them voids the test. These calls
never enter `ledger/ledger.db`. Universe: `data/gt_backtest/universe.csv` (125 names). Calls only at P ≥ 0.60.

## 2026-10-30 (as-of close 2026-10-30, resolves 2026-11-06)

**Registration:** `python tools/gt_stock_backtest.py forward 2026-10-30 --hormuz-impaired 1`
→ `0 v2 calls (P >= 0.6) as of 2026-10-30 close, resolving 2026-11-06 -> forward_v2_2026-10-30.csv sha256
b0493a1cf58d272686a50657ad4f0b8088f0c5453ccf043e3adec8d4207ef3df`

The tool abstained on every name. The best candidates were HWM, LMT, ONDS and RTX outperform at P 0.5875, just
under the bar, and the 2-year yield's fall that week halved the rate-channel weight, as on the 10/23 dry run.

**Provenance:** the scheduled session registered this cohort at 21:26 UTC on 10/30, but it could not push (git
proxy 403: the repository was not among that session's sources), so the file was lost with its container. It was
re-registered on 11/01 at 23:55 UTC, from inputs truncated to the 10/30 close, before the next cash session (11/02)
opened.
The sha256 is **byte-identical** to the one the 10/30 session reported, so this is the same registration, not a
new one.

**Hormuz flag 1 (impaired)**, from the 10/30 session's research (recovered from its transcript):
- IMF PortWatch counted 2 transits on 10/25, against a pre-war baseline of about 85 a day.
- The hormuz.now live AIS count was 6–10 a day on 10/22, 10/28 and 10/29.
- No October Kpler daily count and no current-week UKMTO figure were found; the latest Kpler counts were single
  digits to low teens.
- Several counts come from aggregators. The flag does not depend on them: every source is far below the threshold
  (about 130 a day by Kpler, about 85 by PortWatch).

**score-forward:**
```
forward_v2_2026-10-30.csv: 0 calls, resolves - (pending)
```
