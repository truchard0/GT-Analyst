# Learning loop report

Updated 2026-11-21T13:20:36Z. Model `n58-69e83ddc`, status **shadow**.

- Trained on 58 resolved calls (39 right) in 16 clusters.
- The stated probabilities separate hits from misses with AUC 0.47 (0.50 means no separation).

## Trained priors by call type

| Type | Scored | Right | Trained prior |
|---|---|---|---|
| rates | 10 | 9 | 0.85 |
| state | 9 | 8 | 0.83 |
| markets | 16 | 12 | 0.74 |
| macro | 3 | 2 | 0.67 |
| decision | 14 | 7 | 0.53 |
| war-price | 6 | 1 | 0.34 |

## Out-of-sample test (Brier, lower is better)

| Test | Coin | Base rate | Type model | Blend | Stated | Type model beats stated |
|---|---|---|---|---|---|---|
| leave-one-out | 0.250 | 0.228 | 0.204 | 0.211 | 0.231 | 88% of cluster resamples |
| leave-one-cluster-out | 0.250 | 0.256 | 0.256 | 0.238 | 0.231 | 18% of cluster resamples |

Reading: the type model wins when it has already seen calls on the same topic and loses on a topic it has not seen. The type priors are lessons about these topics, not general laws, so the model stays in shadow until the forward scoreboard decides.

## Forward scoreboard

0 of 20 forward calls resolved so far. 0 new shadow rows logged this run.

Promotion rule: after 20 forward calls, promote if the model beats the stated probabilities by 0.01 Brier, retire if it loses by 0.01, otherwise keep shadowing.
