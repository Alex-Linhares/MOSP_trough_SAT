6376 instances, 617 files, 47 features of which 13 invariants; n_customers 9-134, 5938 at n <= 30, 241 at n >= 50; splits: grouped by file, grouped by file ∪ class, random (leaks!)

## Invariants as point estimates of the optimum

| estimate                   |   mae |   rmse |   exact |   over |   below |   above |   max_below |   max_above |
|:---------------------------|------:|-------:|--------:|-------:|--------:|--------:|------------:|------------:|
| lb_best                    | 0.431 |  1.732 |   0.770 |  0.000 |    1467 |       0 |          30 |           0 |
| ub_best                    | 0.239 |  0.733 |   0.846 |  0.154 |       0 |     979 |           0 |          10 |
| ub_cs_dfs                  | 0.241 |  0.736 |   0.845 |  0.155 |       0 |     988 |           0 |          10 |
| tw_min_fill + 1            | 0.188 |  0.606 |   0.857 |  0.067 |     481 |     428 |           3 |           7 |
| tw_min_degree + 1          | 0.292 |  0.885 |   0.811 |  0.126 |     401 |     805 |           3 |          11 |
| bw_rcm + 1                 | 1.935 |  4.422 |   0.514 |  0.486 |       0 |    3097 |           0 |          49 |
| round(spectral_radius) + 1 | 1.235 |  3.232 |   0.379 |  0.529 |     585 |    3372 |          43 |          26 |
| g_degeneracy + 1           | 1.782 |  4.965 |   0.516 |  0.000 |    3083 |       0 |          61 |           0 |
| sep_size + 1               | 8.663 | 10.803 |   0.010 |  0.001 |    6308 |       7 |          63 |           3 |

## The leading estimates by size band

| band   |   instances |   exact lb_best |   mae lb_best |   exact ub_best |   mae ub_best |   exact ub_cs_dfs |   mae ub_cs_dfs |   exact tw_min_fill+1 |   mae tw_min_fill+1 |
|:-------|------------:|----------------:|--------------:|----------------:|--------------:|------------------:|----------------:|----------------------:|--------------------:|
| 1-30   |        5938 |           0.800 |         0.226 |           0.880 |         0.155 |             0.879 |           0.157 |                 0.887 |               0.121 |
| 31-60  |         318 |           0.453 |         1.132 |           0.503 |         0.783 |             0.503 |           0.783 |                 0.582 |               0.525 |
| 61-200 |         120 |           0.117 |         8.708 |           0.092 |         2.958 |             0.092 |           2.958 |                 0.133 |               2.633 |

## How unbalanced the groupings are

| split                   |   groups |   largest |   largest_frac |   top5_frac |
|:------------------------|---------:|----------:|---------------:|------------:|
| grouped by file         |      617 |       550 |          0.086 |       0.431 |
| grouped by file ∪ class |      512 |      1620 |          0.254 |       0.880 |

## Ablation: the same model with and without the invariants

| target            | split                   | features                |   mae |   rmse |   exact |   over |   mae_gap_rows |   exact_gap_rows |   delta_mae |
|:------------------|:------------------------|:------------------------|------:|-------:|--------:|-------:|---------------:|-----------------:|------------:|
| optimum           | grouped by file         | structure (28)          | 0.436 |  0.857 |   0.712 |  0.175 |          0.778 |            0.484 |     nan     |
| optimum           | grouped by file         | structure + invariants  | 0.220 |  0.487 |   0.871 |  0.062 |          0.480 |            0.669 |      -0.216 |
| optimum           | grouped by file         | structure + bounds (36) | 0.191 |  0.472 |   0.883 |  0.065 |          0.512 |            0.629 |     nan     |
| optimum           | grouped by file         | all (36 + invariants)   | 0.179 |  0.454 |   0.892 |  0.054 |          0.467 |            0.667 |      -0.012 |
| optimum           | grouped by file ∪ class | structure (28)          | 1.667 |  5.430 |   0.356 |  0.129 |          2.796 |            0.388 |     nan     |
| optimum           | grouped by file ∪ class | structure + invariants  | 1.030 |  4.977 |   0.775 |  0.069 |          2.191 |            0.580 |      -0.637 |
| optimum           | grouped by file ∪ class | structure + bounds (36) | 0.967 |  4.970 |   0.771 |  0.059 |          2.253 |            0.557 |     nan     |
| optimum           | grouped by file ∪ class | all (36 + invariants)   | 0.923 |  4.932 |   0.832 |  0.050 |          2.173 |            0.607 |      -0.044 |
| optimum           | random (leaks!)         | structure (28)          | 0.343 |  0.807 |   0.777 |  0.109 |          0.706 |            0.548 |     nan     |
| optimum           | random (leaks!)         | structure + invariants  | 0.199 |  0.535 |   0.878 |  0.058 |          0.487 |            0.660 |      -0.144 |
| optimum           | random (leaks!)         | structure + bounds (36) | 0.176 |  0.505 |   0.889 |  0.063 |          0.511 |            0.638 |     nan     |
| optimum           | random (leaks!)         | all (36 + invariants)   | 0.165 |  0.494 |   0.900 |  0.054 |          0.465 |            0.680 |      -0.012 |
| optimum - lb_best | grouped by file         | structure (28)          | 0.273 |  0.500 |   0.810 |  0.078 |          0.617 |            0.467 |     nan     |
| optimum - lb_best | grouped by file         | structure + invariants  | 0.269 |  0.526 |   0.813 |  0.077 |          0.613 |            0.512 |      -0.004 |
| optimum - lb_best | grouped by file         | structure + bounds (36) | 0.155 |  0.378 |   0.892 |  0.062 |          0.479 |            0.635 |     nan     |
| optimum - lb_best | grouped by file         | all (36 + invariants)   | 0.155 |  0.378 |   0.889 |  0.063 |          0.475 |            0.626 |      -0.000 |
| optimum - lb_best | grouped by file ∪ class | structure (28)          | 0.453 |  1.599 |   0.781 |  0.090 |          1.077 |            0.439 |     nan     |
| optimum - lb_best | grouped by file ∪ class | structure + invariants  | 0.449 |  1.559 |   0.789 |  0.093 |          1.056 |            0.462 |      -0.004 |
| optimum - lb_best | grouped by file ∪ class | structure + bounds (36) | 0.306 |  1.510 |   0.878 |  0.065 |          0.940 |            0.590 |     nan     |
| optimum - lb_best | grouped by file ∪ class | all (36 + invariants)   | 0.298 |  1.496 |   0.883 |  0.063 |          0.927 |            0.606 |      -0.009 |
| optimum - lb_best | random (leaks!)         | structure (28)          | 0.245 |  0.478 |   0.822 |  0.072 |          0.601 |            0.499 |     nan     |
| optimum - lb_best | random (leaks!)         | structure + invariants  | 0.237 |  0.463 |   0.827 |  0.071 |          0.586 |            0.512 |      -0.008 |
| optimum - lb_best | random (leaks!)         | structure + bounds (36) | 0.147 |  0.371 |   0.891 |  0.063 |          0.467 |            0.633 |     nan     |
| optimum - lb_best | random (leaks!)         | all (36 + invariants)   | 0.144 |  0.357 |   0.894 |  0.062 |          0.457 |            0.643 |      -0.003 |

kill criterion 0.02 MAE: largest grouped gain 0.637 (structure + invariants, grouped by file ∪ class, target optimum)

## By size band (grouped by file ∪ class, target optimum)

| band   |   instances | features                |    mae |   rmse |   exact |   over |
|:-------|------------:|:------------------------|-------:|-------:|--------:|-------:|
| 1-30   |        5938 | structure (28)          |  0.875 |  1.090 |   0.377 |  0.121 |
| 1-30   |        5938 | structure + invariants  |  0.330 |  0.433 |   0.819 |  0.067 |
| 1-30   |        5938 | structure + bounds (36) |  0.246 |  0.381 |   0.813 |  0.060 |
| 1-30   |        5938 | all (36 + invariants)   |  0.216 |  0.320 |   0.877 |  0.050 |
| 31-60  |         318 | structure (28)          |  5.744 |  7.560 |   0.091 |  0.296 |
| 31-60  |         318 | structure + invariants  |  4.507 |  6.637 |   0.223 |  0.110 |
| 31-60  |         318 | structure + bounds (36) |  4.492 |  6.566 |   0.261 |  0.057 |
| 31-60  |         318 | all (36 + invariants)   |  4.401 |  6.509 |   0.277 |  0.060 |
| 61-200 |         120 | structure (28)          | 30.051 | 36.830 |   0.025 |  0.108 |
| 61-200 |         120 | structure + invariants  | 26.443 | 34.501 |   0.092 |  0.058 |
| 61-200 |         120 | structure + bounds (36) | 27.286 | 34.511 |   0.033 |  0.033 |
| 61-200 |         120 | all (36 + invariants)   | 26.726 | 34.282 |   0.067 |  0.008 |

## Permutation importance, all features, target optimum (MAE points, held-out groups)

|   rank | feature         | group      |   mae_cost |
|-------:|:----------------|:-----------|-----------:|
|      1 | tw_min_fill     | invariants |      2.011 |
|      2 | ub_cs_dfs       | bounds     |      1.207 |
|      3 | lb_best         | bounds     |      0.431 |
|      4 | ub_best         | bounds     |      0.146 |
|      5 | lb_contraction  | bounds     |      0.076 |
|      6 | tw_min_degree   | invariants |      0.064 |
|      7 | ub_mcn          | bounds     |      0.037 |
|      8 | g_deg_max       | graph      |      0.036 |
|      9 | g_edges         | graph      |      0.034 |
|     10 | spectral_radius | invariants |      0.025 |
|     11 | bw_rcm          | invariants |      0.024 |
|     12 | g_deg_mean      | graph      |      0.023 |
|     13 | n_patterns      | matrix     |      0.017 |
|     14 | g_degeneracy    | graph      |      0.010 |
|     15 | g_density       | graph      |      0.008 |
|     16 | n_customers     | matrix     |      0.007 |
|     17 | g_deg_std       | graph      |      0.005 |
|     18 | n_ones          | matrix     |      0.005 |
|     19 | cc_greedy       | invariants |      0.005 |
|     20 | g_deg_min       | graph      |      0.005 |

invariants' ranks: tw_min_fill #1 (2.011), tw_min_degree #6 (0.064), spectral_radius #10 (0.025), bw_rcm #11 (0.024), cc_greedy #19 (0.005), sep_frac #21 (0.005), rig_deg_expected #24 (0.002), rig_density_ratio #30 (0.001), cc_products #31 (0.000), rig_edge_prob #34 (0.000), fiedler #41 (-0.000), sep_size #47 (-0.002), fiedler_lcc #48 (-0.003)

## Permutation importance, target optimum - lb_best

|   rank | feature        | group      |   mae_cost |
|-------:|:---------------|:-----------|-----------:|
|      1 | bound_gap      | bounds     |      0.283 |
|      2 | bound_gap_frac | bounds     |      0.229 |
|      3 | ub_cs_dfs      | bounds     |      0.020 |
|      4 | bw_rcm         | invariants |      0.017 |
|      5 | density        | matrix     |      0.016 |
|      6 | lb_best        | bounds     |      0.012 |
|      7 | n_customers    | matrix     |      0.011 |
|      8 | sep_size       | invariants |      0.010 |
|      9 | ub_mcn         | bounds     |      0.009 |
|     10 | g_deg_std      | graph      |      0.008 |
|     11 | tw_min_fill    | invariants |      0.007 |
|     12 | fiedler        | invariants |      0.007 |
|     13 | g_clustering   | graph      |      0.007 |
|     14 | g_deg_max      | graph      |      0.007 |
|     15 | col_max_frac   | matrix     |      0.005 |

## Each invariant alone, with the two sizes (grouped by file ∪ class)

| feature           |   rho_optimum |   rho_residual |   mae_optimum |   exact_optimum |   mae_residual |
|:------------------|--------------:|---------------:|--------------:|----------------:|---------------:|
| tw_min_fill       |         0.998 |          0.070 |         0.997 |           0.737 |          0.550 |
| lb_best           |         0.993 |          0.002 |         1.081 |           0.686 |          0.445 |
| tw_min_degree     |         0.997 |          0.080 |         1.106 |           0.659 |          0.552 |
| g_deg_mean        |         0.972 |         -0.028 |         1.468 |           0.385 |          0.472 |
| spectral_radius   |         0.980 |          0.027 |         1.637 |           0.345 |          0.490 |
| g_degeneracy      |         0.949 |         -0.109 |         1.898 |           0.248 |          0.481 |
| g_edges           |         0.963 |          0.206 |         2.113 |           0.217 |          0.588 |
| rig_deg_expected  |         0.970 |         -0.011 |         2.129 |           0.197 |          0.473 |
| bw_rcm            |         0.937 |          0.265 |         2.794 |           0.120 |          0.605 |
| fiedler           |         0.788 |         -0.320 |         2.987 |           0.139 |          0.486 |
| fiedler_lcc       |         0.787 |         -0.322 |         3.011 |           0.143 |          0.482 |
| rig_edge_prob     |         0.355 |         -0.524 |         3.200 |           0.140 |          0.443 |
| sep_frac          |         0.026 |         -0.418 |         3.715 |           0.112 |          0.506 |
| sep_size          |         0.930 |          0.259 |         3.784 |           0.093 |          0.532 |
| rig_density_ratio |         0.252 |         -0.081 |         3.883 |           0.074 |          0.509 |
| cc_greedy         |         0.186 |          0.381 |         6.030 |           0.115 |          0.518 |
| cc_products       |         0.198 |          0.002 |         6.851 |           0.035 |          0.619 |
| (sizes only)      |       nan     |        nan     |         7.053 |           0.044 |          0.625 |

## Order-dependence: shuffle customers and products, re-feature

| feature           |   instances |   changed |   changed_frac |   max_abs_change |   changed_n_ge_50 |
|:------------------|------------:|----------:|---------------:|-----------------:|------------------:|
| tw_min_fill       |         623 |         0 |          0.000 |            0.000 |                 0 |
| tw_min_degree     |         623 |         0 |          0.000 |            0.000 |                 0 |
| bw_rcm            |         623 |         1 |          0.002 |            1.000 |                 0 |
| spectral_radius   |         623 |         0 |          0.000 |            0.000 |                 0 |
| fiedler           |         623 |         0 |          0.000 |            0.000 |                 0 |
| fiedler_lcc       |         623 |         0 |          0.000 |            0.000 |                 0 |
| cc_products       |         623 |         0 |          0.000 |            0.000 |                 0 |
| cc_greedy         |         623 |        26 |          0.042 |            2.000 |                 4 |
| sep_size          |         623 |         0 |          0.000 |            0.000 |                 0 |
| sep_frac          |         623 |         0 |          0.000 |            0.000 |                 0 |
| rig_edge_prob     |         623 |         0 |          0.000 |            0.000 |                 0 |
| rig_deg_expected  |         623 |         0 |          0.000 |            0.000 |                 0 |
| rig_density_ratio |         623 |         0 |          0.000 |            0.000 |                 0 |

130 s
