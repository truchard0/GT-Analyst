# Learning loop report

Updated 2026-11-18T01:32:32Z. Model `n56-b83a1a35`, status **shadow**.

- Trained on 56 resolved calls (37 right) in 14 clusters.
- The stated probabilities separate hits from misses with AUC 0.47 (0.50 means no separation).

## Trained priors by call type

| Type | Scored | Right | Trained prior |
|---|---|---|---|
| rates | 10 | 9 | 0.84 |
| state | 8 | 7 | 0.82 |
| markets | 16 | 12 | 0.74 |
| macro | 2 | 1 | 0.60 |
| decision | 14 | 7 | 0.53 |
| war-price | 6 | 1 | 0.33 |

## Out-of-sample test (Brier, lower is better)

| Test | Coin | Base rate | Type model | Blend | Stated | Type model beats stated |
|---|---|---|---|---|---|---|
| leave-one-out | 0.250 | 0.232 | 0.208 | 0.215 | 0.236 | 87% of cluster resamples |
| leave-one-cluster-out | 0.250 | 0.259 | 0.259 | 0.242 | 0.236 | 15% of cluster resamples |

Reading: the type model wins when it has already seen calls on the same topic and loses on a topic it has not seen. The type priors are lessons about these topics, not general laws, so the model stays in shadow until the forward scoreboard decides.

## Forward scoreboard

0 of 20 forward calls resolved so far. 2 new shadow rows logged this run.

Promotion rule: after 20 forward calls, promote if the model beats the stated probabilities by 0.01 Brier, retire if it loses by 0.01, otherwise keep shadowing.
