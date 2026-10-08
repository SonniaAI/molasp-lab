### tick 47 collection — dG-2 window + L3-at-vacancy (n=500/arm)

| arm | fill | D2T:L2 census | first-stable persist | L3 census | L3 episodes (n, terminal) |
|---|---|---|---|---|---|
| s2_dg0.5_l3probe | 0.412 (ref 0.412) | — | 0.872 | 0.100 (ref 0.100) | 53, 0.9433962264150944 |
| s2_dg0.5_win4 | 0.432 | — | 0.826 | 0.096 | 60, 0.8 |
| s2_dg2_win4 | 0.734 (ref 0.464, gain +0.270) | 367 : 131 (share 0.737) | 0.402 | 0.002 | 61, 0.01639344262295082 |
| fam_dg2_win4 | 0.984 | — | 0.036 | 0.000 | 3, 0.0 |

Machine verdicts (script == independent re-computation, this harness):

| gate | verdict | decisive number |
|---|---|---|
| DW8 dG-2 window gain | CONFIRMED | fill gain +0.270 (confirm >= +0.10, falsify <= +0.03) |
| DW9 coin survival | FALSIFIED | D2T share 0.737 over 498 events (confirm [0.40, 0.60]) |
| DW10 family window-neutrality | CONFIRMED | fam fill 0.984 (floor 0.70) |
| DW11 frozen-regime immunity | CONFIRMED | persist 0.826 (confirm >= 0.80, falsify < 0.65) |
| LV1 L3 frozen-contender class | CONFIRMED | pooled episode persistence 0.867 over 113 episodes (census max 0.100) |
| LV2 L3 window stability | CONFIRMED | census diff 0.004 (confirm <= 0.05, falsify > 0.10) |

