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

## 2026-11-06 (missed)

The scheduled session for the 11/06 close failed at start-up (usage limit reached), so no cohort was registered. It
cannot be registered now without look-ahead, because markets traded on 11/09–11/13. The week counts as missing,
not as an abstention.

## 2026-11-13 (as-of close 2026-11-13, resolves 2026-11-20)

**Registration:** `python tools/gt_stock_backtest.py forward 2026-11-13 --hormuz-impaired 1`
→ `0 v2 calls (P >= 0.6) as of 2026-11-13 close, resolving 2026-11-20 -> forward_v2_2026-11-13.csv sha256
5fe62aa66c1bb957384e32603982d053e420f34c2dfab319d6adfad38607b294`

The tool abstained on every name.

**Provenance:** the scheduled session registered this cohort at about 22:20 UTC on 11/13, but its push was refused
(git proxy 403), so the file was lost with its container. It was re-registered on 11/14, a Saturday, before the next
session opened, from inputs truncated to the 11/13 close. The sha256 is **byte-identical** to the one that session
reported.

**Hormuz flag 1 (impaired):**
- IMF PortWatch counted 2–8 transits a day from 11/01 to 11/08, against a pre-war average of 81.
- Iran reported five tankers hitting mines on 11/13–11/14 (gCaptain, The National).

**score-forward:** two cohorts, both 0 calls. The 10/30 cohort resolved on 11/06 with nothing to score.

## Final (test closed 2026-11-18)

The forward test is closed early, with no scored calls.

| Week (as-of close) | Outcome |
|---|---|
| 2026-10-30 | Registered, 0 calls (abstained on all 125 names) |
| 2026-11-06 | Missing: the scheduled run failed on the account usage limit |
| 2026-11-13 | Registered, 0 calls (abstained on all 125 names) |
| 2026-11-20 | Cancelled: war-driven sector calls were banned on 11/18, and the v2 rules mostly make them |

- **Scored calls: 0.** There is no hit rate, Brier score or interval to report.
- **Verdict:** no out-of-sample evidence either way. The corrections were neither confirmed nor refuted. The 64.6%
  in-sample figure still counts for nothing.
- **Doctrine status:** market-transmission §4.1 stays provisional. Nothing is promoted.
- **The v2 candidate is retired.** It is not a failed test; its calls are of a type the desk no longer makes.
