# Set-valued imitation — tables (loop0003 item 10)

Regenerate: `python -m learning.set_imitation --stage tables`.

## Lattice audit

- instances: 4122; audit failures (lattice optimum ≠ certified): 0; witnesses not construction-optimal: 0; labelled states: 175,687; rows: 1,501,721; good rows: 1,268,751; rule's pick good on 0.997 of labelled states; lattice seconds total 1776, max 2.7.

## Held out, n ≤ 20 (training regime)

| strategy | instances | MAE | exact | worst | total_overshoot |
|---|---|---|---|---|---|
| mcn | 4122 | 0.552 | 0.665 | 6 | 2275 |
| rule | 4122 | 0.081 | 0.929 | 3 | 332 |
| old-ranker | 4122 | 0.189 | 0.835 | 5 | 778 |
| set-binary | 4122 | 0.073 | 0.933 | 3 | 299 |
| set-rank | 4122 | 0.081 | 0.927 | 3 | 334 |

## Held out, whole corpus (models fitted at n ≤ 20)

| strategy | instances | MAE | exact | worst | total_overshoot |
|---|---|---|---|---|---|
| mcn | 6373 | 1.332 | 0.549 | 32 | 8487 |
| rule | 6373 | 0.276 | 0.834 | 10 | 1758 |
| old-ranker | 6373 | 0.443 | 0.749 | 16 | 2823 |
| set-binary | 6373 | 0.269 | 0.838 | 13 | 1717 |
| set-rank | 6373 | 0.268 | 0.836 | 10 | 1705 |

## MAE by size band, whole corpus

| customers | instances | mcn | rule | old-ranker | set-binary | set-rank |
|---|---|---|---|---|---|---|
| 9–15 | 2812 | 0.324 | 0.035 | 0.135 | 0.034 | 0.033 |
| 16–20 | 1310 | 1.040 | 0.178 | 0.303 | 0.155 | 0.184 |
| 21–40 | 2013 | 1.909 | 0.420 | 0.550 | 0.403 | 0.393 |
| 41–75 | 151 | 6.815 | 1.669 | 2.682 | 1.570 | 1.642 |
| 76–134 | 87 | 15.414 | 3.782 | 6.115 | 4.253 | 3.805 |

## Head to head (whole corpus)

| first | second | better | equal | worse |
|---|---|---|---|---|
| set-binary | rule | 251 | 5936 | 186 |
| set-rank | rule | 237 | 5926 | 210 |
| old-ranker | rule | 296 | 5125 | 952 |
| set-binary | old-ranker | 1012 | 5073 | 288 |
| rule | mcn | 2660 | 3686 | 27 |

## Head to head (n ≤ 20)

| first | second | better | equal | worse |
|---|---|---|---|---|
| set-binary | rule | 83 | 3975 | 64 |
| set-rank | rule | 74 | 3965 | 83 |
| old-ranker | rule | 84 | 3556 | 482 |

## Grouped MAE difference with a bootstrap over groups

| first | second | MAE diff | bootstrap p5 | bootstrap p95 | groups |
|---|---|---|---|---|---|
| set-binary | rule | -0.008 | -0.025 | -0.004 | 110 |
| set-rank | rule | 0.000 | -0.018 | 0.009 | 110 |
| set-binary | rule | -0.006 | -0.018 | 0.007 | 509 |
| set-rank | rule | -0.008 | -0.023 | 0.002 | 509 |
| old-ranker | rule | 0.167 | 0.120 | 0.304 | 509 |

## Step accuracy under the correct objective, n ≤ 20

| strategy | own path: good steps | witness states: good picks |
|---|---|---|
| mcn | 0.967 | 0.939 |
| rule | 0.994 | 0.996 |
| old-ranker | 0.987 | 0.989 |
| set-binary | 0.995 | 0.996 |
| set-rank | 0.994 | 0.996 |

## The imitation ceiling along the witnesses

| customers | instances | kind | mean choices per step | ceiling (median) | ceiling (mean) | forced steps |
|---|---|---|---|---|---|---|
| 9–15 | 1722 | exact | 4.700 | 0.330 | 0.341 | 0.123 |
| 16–20 | 1060 | exact | 7.600 | 0.233 | 0.245 | 0.072 |
| 50–75 | 151 | bounded (lower bound on choices) | 14.541 | 0.142 | 0.146 | 0.021 |
| 76–100 | 63 | bounded (lower bound on choices) | 24.192 | 0.109 | 0.136 | 0.040 |
| 101–134 | 24 | bounded (lower bound on choices) | 35.048 | 0.100 | 0.099 | 0.020 |

## Bounded search at ≥ 50: where the confirmations came from

- instances 238, censored 0, witnesses not construction-optimal 0; confirmations by suffix 362,700, by DFS 20,192, unknown 95,838; seconds total 6433, max 238.

| n_customers | instances | ceiling_upper_median | ceiling_upper_max | confirmed_mean_median | multi_frac_mean | censored |
|---|---|---|---|---|---|---|
| 50.000 | 120.000 | 0.143 | 0.335 | 12.643 | 0.981 | 0.000 |
| 60.000 | 1.000 | 0.182 | 0.182 | 9.068 | 1.000 | 0.000 |
| 68.000 | 1.000 | 0.144 | 0.144 | 10.597 | 0.985 | 0.000 |
| 75.000 | 29.000 | 0.132 | 0.230 | 19.973 | 0.971 | 0.000 |
| 79.000 | 1.000 | 0.112 | 0.112 | 12.167 | 1.000 | 0.000 |
| 82.000 | 1.000 | 0.156 | 0.156 | 8.728 | 1.000 | 0.000 |
| 99.000 | 1.000 | 0.079 | 0.079 | 20.102 | 1.000 | 0.000 |
| 100.000 | 60.000 | 0.109 | 0.350 | 24.783 | 0.958 | 0.000 |
| 105.000 | 1.000 | 0.084 | 0.084 | 17.000 | 1.000 | 0.000 |
| 125.000 | 22.000 | 0.102 | 0.141 | 36.040 | 0.978 | 0.000 |
| 134.000 | 1.000 | 0.082 | 0.082 | 17.579 | 0.992 | 0.000 |

## Calibration of the bounded procedure at 16–20 against the exact counts

- instances 1310; confirmed / exact choices (sum over steps): 0.999; mean ceiling upper bound 0.193 vs exact 0.192; instances where the bound equals the exact ceiling: 1218; steps where the confirmed count equals the exact count: 0.9957; seconds per instance max 0.017.
