# Bound harness tables (§38)

*Regenerate: `python -m learning.bound_harness --stage tables`. Every candidate in optimum units (pathwidth + 1). Reference = `max(lb_best, tw_lo + 1)`. Gap instances = the 338 corpus instances with `optimum − lb_best ≥ 2`.*

## Coverage

| source   |   rows |   n_min |   n_max |
|:---------|-------:|--------:|--------:|
| campaign |  37800 |  10.000 |  40.000 |
| corpus   |   6376 |   9.000 | 134.000 |
| upward   |   5686 |  50.000 | 100.000 |

## (a) validity and (c) tightness

| bound                                        |   rows |   above optimum (must be 0) |   tight, all |   > lb_best, all |   > reference, all |   tight, gap |   > lb_best, gap |   > reference, gap |   beats reference, gap (count) |   mean shortfall, gap |
|:---------------------------------------------|-------:|----------------------------:|-------------:|-----------------:|-------------------:|-------------:|-----------------:|-------------------:|-------------------------------:|----------------------:|
| tw + 1 (tw_lo)                               |  49862 |                           0 |        0.789 |            0.147 |              0.000 |        0.198 |            0.589 |              0.000 |                              0 |                 8.882 |
| lb_best                                      |  49862 |                           0 |        0.698 |            0.000 |              0.000 |        0.000 |            0.000 |              0.000 |                              0 |                 4.781 |
| reference max(lb_best, tw + 1)               |  49862 |                           0 |        0.819 |            0.147 |              0.000 |        0.198 |            0.589 |              0.000 |                              0 |                 3.920 |
| branch lemma + 1 (§24, one level, tw-seeded) |  49862 |                           0 |        0.008 |            0.001 |              0.001 |        0.000 |            0.000 |              0.000 |                              0 |                22.299 |
| cut-branch                                   |  49862 |                           0 |        0.362 |            0.001 |              0.001 |        0.000 |            0.000 |              0.000 |                              0 |                14.151 |
| sep-branch                                   |  49862 |                           0 |        0.506 |            0.025 |              0.001 |        0.015 |            0.044 |              0.000 |                              0 |                13.988 |
| contract-branch                              |  49862 |                           0 |        0.553 |            0.051 |              0.004 |        0.024 |            0.249 |              0.024 |                              8 |                 7.896 |

## (c) by size band, gap instances

| band    |   gap instances |   tw exact |   cut-branch > lb_best |   cut-branch > ref |   cut-branch tight |   cut-branch shortfall |   sep-branch > lb_best |   sep-branch > ref |   sep-branch tight |   sep-branch shortfall |   contract-branch > lb_best |   contract-branch > ref |   contract-branch tight |   contract-branch shortfall |
|:--------|----------------:|-----------:|-----------------------:|-------------------:|-------------------:|-----------------------:|-----------------------:|-------------------:|-------------------:|-----------------------:|----------------------------:|------------------------:|------------------------:|----------------------------:|
| 9–20    |              17 |         17 |                      0 |                  0 |                  0 |                  4.059 |                     15 |                  0 |                  5 |                  0.824 |                          15 |                       0 |                       5 |                       0.824 |
| 21–30   |             133 |        130 |                      0 |                  0 |                  0 |                  6.008 |                      0 |                  0 |                  0 |                  6.008 |                          30 |                       0 |                       1 |                       2.098 |
| 31–40   |              47 |         38 |                      0 |                  0 |                  0 |                  5.957 |                      0 |                  0 |                  0 |                  5.957 |                          20 |                       0 |                       2 |                       2.298 |
| 41–60   |              54 |         23 |                      0 |                  0 |                  0 |                  7.759 |                      0 |                  0 |                  0 |                  7.759 |                          16 |                       5 |                       0 |                       4.259 |
| 61–75   |              17 |          0 |                      0 |                  0 |                  0 |                 24.235 |                      0 |                  0 |                  0 |                 24.235 |                           1 |                       1 |                       0 |                      14.353 |
| 76–100  |              45 |          1 |                      0 |                  0 |                  0 |                 33.956 |                      0 |                  0 |                  0 |                 33.956 |                           1 |                       1 |                       0 |                      21.911 |
| 101–134 |              25 |          0 |                      0 |                  0 |                  0 |                 51.040 |                      0 |                  0 |                  0 |                 51.040 |                           1 |                       1 |                       0 |                      32.320 |

## Gain over the seed, censoring and cost

| candidate            | over                         |   gain > 0, all |   gain > 0, gap |   max gain |   mean gain, gap |   censored |   median s |   max s |   total core-h |
|:---------------------|:-----------------------------|----------------:|----------------:|-----------:|-----------------:|-----------:|-----------:|--------:|---------------:|
| cut-branch           | ω (its seed)                 |           0.001 |           0.000 |          1 |            0.000 |         34 |      0.001 |  23.459 |          0.353 |
| sep-branch           | max(ω, tw_DP) + 1 (its seed) |           0.003 |           0.000 |          1 |            0.000 |        665 |      0.030 |  23.800 |          2.675 |
| contract-branch      | best seed over the minors    |           0.001 |           0.000 |          1 |            0.000 |       1501 |      0.155 |  23.607 |          4.405 |
| contract-branch      | sep-branch                   |           0.428 |           0.743 |         48 |            6.092 |       1501 |      0.155 |  23.607 |          4.405 |
| contract-branch seed | reference (seed only)        |           0.003 |           0.024 |          3 |           -3.976 |       1501 |      0.155 |  23.607 |          4.405 |

## Counterexamples from (a)

none — no candidate exceeds the optimum on any certified instance.

## (b) the adversary (plan's run at 8–15 and the supplementary run together)

| candidate       |   jobs |   evaluations |   skipped |   max_viol |   reached_optimum |   n_min |   n_max |   counter_n | counter_key   | verdict   |
|:----------------|-------:|--------------:|----------:|-----------:|------------------:|--------:|--------:|------------:|:--------------|:----------|
| contract-branch |     60 |         11880 |    615340 |          0 |                60 |       8 |      25 |          -1 |               | survived  |
| cut-branch      |     60 |         11880 |    629207 |          0 |                60 |       8 |      25 |          -1 |               | survived  |
| sep-branch      |     60 |         11880 |    598199 |          0 |                60 |       8 |      25 |          -1 |               | survived  |

### by size

| candidate       |   n |   jobs |   evaluations |   max_viol |
|:----------------|----:|-------:|--------------:|-----------:|
| contract-branch |   8 |      6 |          1260 |          0 |
| contract-branch |   9 |      6 |          1260 |          0 |
| contract-branch |  10 |      6 |          1260 |          0 |
| contract-branch |  11 |      6 |          1260 |          0 |
| contract-branch |  12 |      6 |          1260 |          0 |
| contract-branch |  13 |      6 |          1260 |          0 |
| contract-branch |  14 |      6 |          1260 |          0 |
| contract-branch |  15 |      6 |          1260 |          0 |
| contract-branch |  18 |      3 |           450 |          0 |
| contract-branch |  20 |      3 |           450 |          0 |
| contract-branch |  22 |      3 |           450 |          0 |
| contract-branch |  25 |      3 |           450 |          0 |
| cut-branch      |   8 |      6 |          1260 |          0 |
| cut-branch      |   9 |      6 |          1260 |          0 |
| cut-branch      |  10 |      6 |          1260 |          0 |
| cut-branch      |  11 |      6 |          1260 |          0 |
| cut-branch      |  12 |      6 |          1260 |          0 |
| cut-branch      |  13 |      6 |          1260 |          0 |
| cut-branch      |  14 |      6 |          1260 |          0 |
| cut-branch      |  15 |      6 |          1260 |          0 |
| cut-branch      |  18 |      3 |           450 |          0 |
| cut-branch      |  20 |      3 |           450 |          0 |
| cut-branch      |  22 |      3 |           450 |          0 |
| cut-branch      |  25 |      3 |           450 |          0 |
| sep-branch      |   8 |      6 |          1260 |          0 |
| sep-branch      |   9 |      6 |          1260 |          0 |
| sep-branch      |  10 |      6 |          1260 |          0 |
| sep-branch      |  11 |      6 |          1260 |          0 |
| sep-branch      |  12 |      6 |          1260 |          0 |
| sep-branch      |  13 |      6 |          1260 |          0 |
| sep-branch      |  14 |      6 |          1260 |          0 |
| sep-branch      |  15 |      6 |          1260 |          0 |
| sep-branch      |  18 |      3 |           450 |          0 |
| sep-branch      |  20 |      3 |           450 |          0 |
| sep-branch      |  22 |      3 |           450 |          0 |
| sep-branch      |  25 |      3 |           450 |          0 |

## Kill verdict

| candidate       | valid on every certified instance   | survived the adversary   | beats reference on gap   | beats > 5% while surviving   |
|:----------------|:------------------------------------|:-------------------------|:-------------------------|:-----------------------------|
| cut-branch      | True                                | True                     | 0.0%                     | False                        |
| sep-branch      | True                                | True                     | 0.0%                     | False                        |
| contract-branch | True                                | True                     | 2.4%                     | False                        |
