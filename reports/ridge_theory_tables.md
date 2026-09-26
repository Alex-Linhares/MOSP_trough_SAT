# Ridge theory tables (§25)

*Regenerate: `python -m learning.ridge_theory --stage tables`. Rows: {'campaign': 37800, 'ratio': 2750, 'upward': 6773}. 2 s. Figure: `reports/figures/ridge_theory.png`.*

## Interpolated peaks per series (n >= 30)

| generator   | ratio_label   |   n |   r_exact |   cells |   peak_param |   peak_cell_col_mean |   peak_col_mean |   ci_lo |   ci_hi | interior   | peak_is_lower_bound   |   peak_median_log_nodes |   col_mean |   row_mean |   excess |   branch |   g_deg_mean |   g_density |   clique_excess |   opt_frac |   tw_min_fill_n |   g_degeneracy_n |   bw_rcm_n |   lb_best_n |   g_clustering |   g_edges_n |   bip_cyc |
|:------------|:--------------|----:|----------:|--------:|-------------:|---------------------:|----------------:|--------:|--------:|:-----------|:----------------------|------------------------:|-----------:|-----------:|---------:|---------:|-------------:|------------:|----------------:|-----------:|----------------:|-----------------:|-----------:|------------:|---------------:|------------:|----------:|
| bernoulli   | 2n            |  30 |     2     |       9 |        0.075 |                 2.35 |            2.1  |    2    |    2.18 | True       | False                 |                    2.6  |       2.12 |       4.25 |     2.25 |     9.21 |         6.71 |      0.231  |          nan    |      0.362 |           0.317 |           0.176  |      0.55  |       0.329 |         0.463  |        3.36 |     1.3   |
| bernoulli   | 2n            |  35 |     2     |       9 |        0.05  |                 1.91 |            2.15 |    2.12 |    2.2  | True       | False                 |                    3.13 |       2.18 |       4.36 |     2.36 |     9.76 |         7.42 |      0.218  |          nan    |      0.357 |           0.329 |           0.174  |      0.557 |       0.31  |         0.453  |        3.71 |     1.41  |
| bernoulli   | 2n            |  40 |     2     |       9 |        0.05  |                 2.12 |            2.27 |    2.24 |    2.3  | True       | False                 |                    3.63 |       2.29 |       4.59 |     2.59 |    10.8  |         8.26 |      0.212  |            4.68 |      0.367 |           0.342 |           0.148  |      0.583 |       0.322 |         0.446  |        4.13 |     1.61  |
| bernoulli   | 2n            |  50 |     2     |       6 |        0.05  |                 2.57 |            2.43 |    2.37 |    2.46 | True       | False                 |                    4.42 |       2.46 |       4.91 |     2.91 |    12.3  |         9.99 |      0.204  |            6.16 |      0.407 |           0.402 |           0.151  |      0.618 |       0.324 |         0.418  |        4.99 |     1.95  |
| bernoulli   | 2n            |  60 |     2     |       6 |        0.05  |                 3.03 |            2.4  |    2.31 |    2.52 | True       | False                 |                    5.09 |       2.49 |       4.97 |     2.97 |    13.2  |        10.4  |      0.177  |            8.4  |      0.374 |           0.373 |           0.124  |      0.598 |       0.305 |         0.408  |        5.21 |     2.01  |
| bernoulli   | 2n            |  75 |     2     |       6 |        0.025 |                 2.06 |            2.06 |  nan    |  nan    | False      | False                 |                    7    |       2.06 |       4.12 |     2.12 |     8.49 |         6.96 |      0.0941 |            2.86 |      0.267 |           0.267 |           0.0667 |      0.547 |       0.173 |         0.388  |        3.48 |     1.13  |
| bernoulli   | n             |  30 |     1     |       9 |        0.1   |                 3.07 |            3.02 |    2.88 |    3.14 | True       | False                 |                    2.53 |       3.03 |       3.03 |     2.03 |     9.18 |         7.62 |      0.263  |          nan    |      0.36  |           0.325 |           0.198  |      0.589 |       0.327 |         0.584  |        3.81 |     1.06  |
| bernoulli   | n             |  35 |     1     |       9 |        0.075 |                 2.77 |            3.05 |    2.95 |    3.16 | True       | False                 |                    2.9  |       3.07 |       3.07 |     2.07 |     9.57 |         7.95 |      0.234  |          nan    |      0.341 |           0.313 |           0.194  |      0.57  |       0.302 |         0.568  |        3.97 |     1.12  |
| bernoulli   | n             |  40 |     1     |       9 |        0.075 |                 3.1  |            3.11 |    3.04 |    3.18 | True       | False                 |                    3.35 |       3.11 |       3.11 |     2.11 |     9.71 |         8.35 |      0.214  |            3.82 |      0.328 |           0.303 |           0.151  |      0.602 |       0.278 |         0.547  |        4.17 |     1.14  |
| bernoulli   | n             |  50 |     1     |       6 |        0.05  |                 2.64 |            3.11 |    3.01 |    3.36 | True       | False                 |                    4.15 |       3.16 |       3.16 |     2.16 |    10.3  |         8.67 |      0.177  |            4.87 |      0.322 |           0.295 |           0.147  |      0.58  |       0.253 |         0.533  |        4.34 |     1.19  |
| bernoulli   | n             |  60 |     1     |       6 |        0.05  |                 3.13 |            3.48 |    3.35 |    3.57 | True       | False                 |                    4.95 |       3.53 |       3.53 |     2.53 |    12.8  |        11    |      0.187  |            7.84 |      0.375 |           0.374 |           0.141  |      0.644 |       0.28  |         0.509  |        5.52 |     1.56  |
| bernoulli   | n             |  75 |     1     |       6 |        0.05  |                 3.79 |            3.63 |    3.51 |    3.74 | True       | False                 |                    6.2  |       3.66 |       3.66 |     2.66 |    13.6  |        12    |      0.163  |            7.3  |      0.379 |           0.389 |           0.116  |      0.647 |       0.229 |         0.48   |        6.02 |     1.69  |
| bernoulli   | n/2           |  50 |     0.5   |       6 |        0.1   |                 5.08 |            5.11 |    4.64 |    5.25 | True       | False                 |                    3.63 |       5.11 |       2.56 |     2.06 |    13.1  |        11.6  |      0.236  |          nan    |      0.353 |           0.343 |           0.192  |      0.662 |       0.283 |         0.656  |        5.78 |     1.08  |
| bernoulli   | n/2           |  60 |     0.5   |       6 |        0.075 |                 4.58 |            4.87 |    4.76 |    5.02 | True       | False                 |                    4.28 |       4.9  |       2.45 |     1.95 |    12.2  |        11.1  |      0.189  |            5.36 |      0.331 |           0.307 |           0.158  |      0.631 |       0.236 |         0.636  |        5.56 |     0.975 |
| bernoulli   | n/2           |  75 |     0.493 |       6 |        0.075 |                 5.72 |            5.44 |    5.07 |    5.67 | True       | False                 |                    5.35 |       5.48 |       2.7  |     2.21 |    15    |        13.4  |      0.181  |            7.27 |      0.355 |           0.358 |           0.141  |      0.663 |       0.227 |         0.61   |        6.69 |     1.23  |
| bernoulli   | n/4           |  50 |     0.24  |       6 |        0.15  |                 8    |            8.43 |    6.99 |    9.7  | True       | False                 |                    2.53 |       8.48 |       2.03 |     1.79 |    17.4  |        15.1  |      0.309  |            5.42 |      0.367 |           0.332 |           0.234  |      0.734 |       0.303 |         0.754  |        7.57 |     0.814 |
| bernoulli   | n/4           |  60 |     0.25  |       6 |        0.125 |                 8.07 |            8.19 |    7.9  |    9.33 | True       | False                 |                    3.12 |       8.2  |       2.05 |     1.8  |    16.8  |        15.1  |      0.256  |            6.11 |      0.342 |           0.31  |           0.203  |      0.709 |       0.257 |         0.737  |        7.55 |     0.816 |
| bernoulli   | n/4           |  75 |     0.24  |       6 |        0.1   |                 8.11 |            8.4  |    7.74 |    9.78 | True       | False                 |                    3.72 |       8.42 |       2.02 |     1.78 |    17.1  |        15.3  |      0.207  |            6.85 |      0.313 |           0.305 |           0.167  |      0.708 |       0.228 |         0.731  |        7.64 |     0.794 |
| fixed       | 2n            |  30 |     2     |       9 |        2     |                 2    |            2    |  nan    |  nan    | False      | False                 |                    2.97 |       2    |       4    |     2    |     4    |         3.8  |      0.131  |          nan    |      0.267 |           0.233 |           0.1    |      0.433 |       0.233 |         0.139  |        1.9  |     1.03  |
| fixed       | 2n            |  35 |     2     |       9 |        2     |                 2    |            2    |  nan    |  nan    | False      | False                 |                    3.49 |       2    |       4    |     2    |     4    |         3.83 |      0.113  |          nan    |      0.257 |           0.229 |           0.0857 |      0.457 |       0.2   |         0.114  |        1.91 |     1.03  |
| fixed       | 2n            |  40 |     2     |       9 |        2     |                 2    |            2    |  nan    |  nan    | False      | False                 |                    4    |       2    |       4    |     2    |     4    |         3.85 |      0.0987 |            1.79 |      0.25  |           0.213 |           0.075  |      0.425 |       0.2   |         0.105  |        1.93 |     1.04  |
| fixed       | 2n            |  50 |     2     |       9 |        2     |                 2.01 |            2.01 |  nan    |  nan    | False      | False                 |                    5.08 |       2.01 |       4.02 |     2.02 |     4.06 |         3.92 |      0.08   |            1.84 |      0.22  |           0.2   |           0.06   |      0.42  |       0.16  |         0.0838 |        1.96 |     1.04  |
| fixed       | 2n            |  60 |     2     |       9 |        2     |                 2.01 |            2.01 |  nan    |  nan    | False      | False                 |                    6.07 |       2.01 |       4.02 |     2.02 |     4.05 |         3.97 |      0.0672 |            1.86 |      0.217 |           0.2   |           0.05   |      0.417 |       0.15  |         0.0825 |        1.98 |     1.03  |
| fixed       | 2n            |  75 |     2     |       9 |        2     |                 2.01 |            2.01 |  nan    |  nan    | False      | True                  |                    8.12 |       2.01 |       4.01 |     2.01 |     4.04 |         3.97 |      0.0537 |            1.88 |      0.2   |           0.2   |           0.04   |      0.427 |       0.133 |         0.0708 |        1.99 |     1.03  |
| fixed       | n             |  30 |     1     |       9 |        3     |                 3.03 |            3.18 |    3.14 |    3.22 | True       | False                 |                    2.66 |       3.2  |       3.2  |     2.2  |     7.14 |         6.4  |      0.221  |          nan    |      0.361 |           0.3   |           0.15   |      0.556 |       0.328 |         0.501  |        3.2  |     1.23  |
| fixed       | n             |  35 |     1     |       9 |        3     |                 3.06 |            3.2  |    3.15 |    3.25 | True       | False                 |                    3.15 |       3.22 |       3.22 |     2.22 |     7.26 |         6.54 |      0.192  |          nan    |      0.315 |           0.291 |           0.129  |      0.543 |       0.286 |         0.497  |        3.27 |     1.25  |
| fixed       | n             |  40 |     1     |       9 |        3     |                 3.05 |            3.25 |    3.2  |    3.3  | True       | False                 |                    3.6  |       3.27 |       3.27 |     2.27 |     7.6  |         6.94 |      0.178  |            3.97 |      0.335 |           0.316 |           0.118  |      0.56  |       0.272 |         0.47   |        3.47 |     1.3   |
| fixed       | n             |  50 |     1     |       9 |        3     |                 3.04 |            3.31 |    3.23 |    3.44 | True       | False                 |                    4.6  |       3.33 |       3.33 |     2.33 |     7.99 |         7.4  |      0.151  |            4.25 |      0.325 |           0.308 |           0.104  |      0.561 |       0.242 |         0.443  |        3.7  |     1.35  |
| fixed       | n             |  60 |     1     |       9 |        3     |                 3.05 |            3.47 |    3.37 |    3.55 | True       | False                 |                    5.35 |       3.51 |       3.51 |     2.51 |     9.03 |         8.36 |      0.142  |            4.86 |      0.338 |           0.337 |           0.0982 |      0.596 |       0.238 |         0.437  |        4.18 |     1.52  |
| fixed       | n             |  75 |     1     |       9 |        3     |                 3.04 |            3.41 |    3.32 |    3.52 | True       | False                 |                    6.78 |       3.44 |       3.44 |     2.44 |     8.64 |         8.17 |      0.11   |            4.41 |      0.306 |           0.325 |           0.0754 |      0.583 |       0.196 |         0.408  |        4.08 |     1.46  |
| fixed       | n/2           |  50 |     0.5   |       9 |        5     |                 5.16 |            5.5  |    5    |    6.08 | True       | False                 |                    3.59 |       5.52 |       2.76 |     2.26 |    12.6  |        11.3  |      0.23   |            6.92 |      0.379 |           0.359 |           0.163  |      0.671 |       0.291 |         0.603  |        5.64 |     1.28  |
| fixed       | n/2           |  60 |     0.5   |       9 |        6     |                 6.08 |            5.64 |    5.13 |    6.08 | True       | False                 |                    4.32 |       5.66 |       2.83 |     2.33 |    13.3  |        12    |      0.203  |            7.32 |      0.375 |           0.375 |           0.144  |      0.679 |       0.263 |         0.577  |        5.98 |     1.35  |
| fixed       | n/2           |  75 |     0.493 |       9 |        5     |                 5.14 |            5.24 |    5.1  |    5.62 | True       | False                 |                    5.46 |       5.25 |       2.59 |     2.1  |    11    |        10.5  |      0.141  |            4.7  |      0.316 |           0.319 |           0.0981 |      0.624 |       0.195 |         0.572  |        5.23 |     1.11  |
| fixed       | n/4           |  50 |     0.24  |       9 |        9     |                 9.42 |            9.17 |    8.5  |    9.65 | True       | False                 |                    2.44 |       9.18 |       2.2  |     1.96 |    18.1  |        15.8  |      0.323  |            9.49 |      0.405 |           0.365 |           0.23   |      0.74  |       0.307 |         0.729  |        7.92 |     0.984 |
| fixed       | n/4           |  60 |     0.25  |       9 |       10     |                10.3  |           10.6  |    9.4  |   11    | True       | False                 |                    3.02 |      10.7  |       2.66 |     2.41 |    25.9  |        21.4  |      0.363  |          nan    |      0.487 |           0.474 |           0.251  |      0.774 |       0.378 |         0.697  |       10.7  |     1.43  |
| fixed       | n/4           |  75 |     0.24  |       9 |        9     |                 9.44 |            9.59 |    9.4  |   10.3  | True       | False                 |                    3.73 |       9.59 |       2.3  |     2.06 |    19.8  |        17.9  |      0.242  |           11.8  |      0.382 |           0.383 |           0.164  |      0.751 |       0.26  |         0.681  |        8.94 |     1.08  |
| fixed       | n/8           |  75 |     0.12  |      10 |       20     |                20.6  |           20.7  |   18.7  |   21.7  | True       | False                 |                    2.14 |      20.7  |       2.48 |     2.36 |    48.8  |        37.6  |      0.508  |          nan    |      0.55  |           0.544 |           0.376  |      0.827 |       0.444 |         0.773  |       18.8  |     1.37  |

## Constancy of each candidate across m / n at fixed (generator, n), n >= 50

| candidate      | text                                               |   cv_across_ratios_mean |   cv_across_ratios_max |   max_over_min_across_ratios |   cv_all_peaks |   peak_value_min |   peak_value_max |   series_n |
|:---------------|:---------------------------------------------------|------------------------:|-----------------------:|-----------------------------:|---------------:|-----------------:|-----------------:|-----------:|
| excess         | excess (n_ones − m) / n = r (col_mean − 1)         |                   0.127 |                  0.202 |                         1.65 |          0.14  |           1.78   |            2.97  |          6 |
| bw_rcm_n       | RCM bandwidth / n                                  |                   0.146 |                  0.216 |                         1.94 |          0.163 |           0.417  |            0.827 |          6 |
| opt_frac       | optimum / n                                        |                   0.181 |                  0.329 |                         2.75 |          0.216 |           0.2    |            0.55  |          6 |
| tw_min_fill_n  | min-fill treewidth / n                             |                   0.194 |                  0.316 |                         2.72 |          0.224 |           0.2    |            0.544 |          6 |
| lb_best_n      | certified lower bound / n                          |                   0.213 |                  0.435 |                         3.33 |          0.27  |           0.133  |            0.444 |          6 |
| bip_cyc        | incidence-graph cyclomatic number / n              |                   0.228 |                  0.355 |                         2.46 |          0.253 |           0.794  |            2.01  |          6 |
| row_mean       | products per customer (row_mean = r · col_mean)    |                   0.26  |                  0.348 |                         2.43 |          0.27  |           2.02   |            4.97  |          6 |
| clique_excess  | graph excess: Σ over maximal cliques (|K| − 1) / n |                   0.331 |                  0.509 |                         5.15 |        nan     |           1.84   |           11.8   |          3 |
| g_clustering   | clustering coefficient                             |                   0.366 |                  0.521 |                        10.9  |          0.387 |           0.0708 |            0.773 |          6 |
| g_edges_n      | edges / n                                          |                   0.402 |                  0.761 |                         9.46 |          0.551 |           1.96   |           18.8   |          6 |
| g_deg_mean     | MOSP-graph mean degree                             |                   0.402 |                  0.761 |                         9.46 |          0.551 |           3.92   |           37.6   |          6 |
| g_density      | MOSP-graph edge probability                        |                   0.402 |                  0.761 |                         9.46 |          0.491 |           0.0537 |            0.508 |          6 |
| g_degeneracy_n | degeneracy / n                                     |                   0.414 |                  0.794 |                         9.4  |          0.492 |           0.04   |            0.376 |          6 |
| branch         | branching factor (giant component at 1)            |                   0.423 |                  0.867 |                        12.1  |          0.621 |           4.04   |           48.8   |          6 |
| col_mean       | customers per product (col_mean)                   |                   0.564 |                  0.823 |                        10.3  |          0.714 |           2.01   |           20.7   |          6 |

## Calibrated on the m = n ridge, predicted elsewhere: summary

| candidate      | text                                               |   series |   mean_abs_log10_error |   max_abs_log10_error |   within_ci |   deciding_series |   deciding_mean_abs_log10_error |   deciding_within_ci |
|:---------------|:---------------------------------------------------|---------:|-----------------------:|----------------------:|------------:|------------------:|--------------------------------:|---------------------:|
| tw_min_fill_n  | min-fill treewidth / n                             |       19 |                 0.0438 |                0.137  |           9 |                13 |                          0.0376 |                    8 |
| clique_excess  | graph excess: Σ over maximal cliques (|K| − 1) / n |       19 |                 0.0447 |                0.0447 |           1 |                13 |                          0.0447 |                    1 |
| opt_frac       | optimum / n                                        |       19 |                 0.048  |                0.175  |           7 |                13 |                          0.0438 |                    6 |
| bip_cyc        | incidence-graph cyclomatic number / n              |       19 |                 0.0511 |                0.127  |           8 |                13 |                          0.0567 |                    4 |
| excess         | excess (n_ones − m) / n = r (col_mean − 1)         |       19 |                 0.0551 |                0.125  |           8 |                13 |                          0.0626 |                    4 |
| lb_best_n      | certified lower bound / n                          |       19 |                 0.0556 |                0.167  |           6 |                13 |                          0.054  |                    5 |
| g_edges_n      | edges / n                                          |       19 |                 0.0868 |                0.239  |           2 |                13 |                          0.0983 |                    1 |
| bw_rcm_n       | RCM bandwidth / n                                  |       19 |                 0.0904 |                0.287  |           5 |                13 |                          0.0998 |                    3 |
| g_degeneracy_n | degeneracy / n                                     |       19 |                 0.0945 |                0.231  |           2 |                13 |                          0.101  |                    2 |
| branch         | branching factor (giant component at 1)            |       19 |                 0.0961 |                0.363  |           4 |                13 |                          0.106  |                    3 |
| g_deg_mean     | MOSP-graph mean degree                             |       19 |                 0.0972 |                0.367  |           4 |                13 |                          0.109  |                    3 |
| g_density      | MOSP-graph edge probability                        |       19 |                 0.0994 |                0.319  |           5 |                13 |                          0.106  |                    4 |
| row_mean       | products per customer (row_mean = r · col_mean)    |       19 |                 0.136  |                0.233  |           0 |                13 |                          0.154  |                    0 |
| g_clustering   | clustering coefficient                             |       19 |                 0.261  |                0.348  |           0 |                13 |                        nan      |                    0 |
| col_mean       | customers per product (col_mean)                   |       19 |                 0.297  |                0.78   |           0 |                13 |                          0.34   |                    0 |

## Calibrated predictions, every series

| candidate      | generator   | ratio_label   |   n |   calibration |   predicted_col_mean |   measured_col_mean |   ci_lo |   ci_hi | interior   |   log10_error | within_ci   | is_calibration   |
|:---------------|:------------|:--------------|----:|--------------:|---------------------:|--------------------:|--------:|--------:|:-----------|--------------:|:------------|:-----------------|
| bip_cyc        | bernoulli   | 2n            |  50 |        1.48   |                 2.15 |                2.43 |    2.37 |    2.46 | True       |     -0.0535   | False       | False            |
| bip_cyc        | bernoulli   | n             |  50 |        1.48   |                 3.41 |                3.11 |    3.01 |    3.36 | True       |      0.0405   | False       | True             |
| bip_cyc        | bernoulli   | n/2           |  50 |        1.48   |                 5.81 |                5.11 |    4.64 |    5.25 | True       |      0.0562   | False       | False            |
| bip_cyc        | bernoulli   | n/4           |  50 |        1.48   |               nan    |                8.43 |    6.99 |    9.7  | True       |    nan        | False       | False            |
| bip_cyc        | bernoulli   | 2n            |  60 |        1.48   |                 2.14 |                2.4  |    2.31 |    2.52 | True       |     -0.0502   | False       | False            |
| bip_cyc        | bernoulli   | n             |  60 |        1.48   |                 3.4  |                3.48 |    3.35 |    3.57 | True       |     -0.00949  | True        | True             |
| bip_cyc        | bernoulli   | n/2           |  60 |        1.48   |                 5.92 |                4.87 |    4.76 |    5.02 | True       |      0.0846   | False       | False            |
| bip_cyc        | bernoulli   | n/4           |  60 |        1.48   |                10.8  |                8.19 |    7.9  |    9.33 | True       |      0.119    | False       | False            |
| bip_cyc        | bernoulli   | 2n            |  75 |        1.48   |                 2.19 |                2.06 |  nan    |  nan    | False      |      0.0265   | True        | False            |
| bip_cyc        | bernoulli   | n             |  75 |        1.48   |                 3.36 |                3.63 |    3.51 |    3.74 | True       |     -0.0332   | False       | True             |
| bip_cyc        | bernoulli   | n/2           |  75 |        1.48   |                 5.97 |                5.44 |    5.07 |    5.67 | True       |      0.0399   | False       | False            |
| bip_cyc        | bernoulli   | n/4           |  75 |        1.48   |                11.3  |                8.4  |    7.74 |    9.78 | True       |      0.127    | False       | False            |
| bip_cyc        | fixed       | 2n            |  50 |        1.45   |                 2.18 |                2.01 |  nan    |  nan    | False      |      0.0356   | True        | False            |
| bip_cyc        | fixed       | n             |  50 |        1.45   |                 3.39 |                3.31 |    3.23 |    3.44 | True       |      0.0112   | True        | True             |
| bip_cyc        | fixed       | n/2           |  50 |        1.45   |                 5.84 |                5.5  |    5    |    6.08 | True       |      0.0259   | True        | False            |
| bip_cyc        | fixed       | n/4           |  50 |        1.45   |                11.1  |                9.17 |    8.5  |    9.65 | True       |      0.0816   | False       | False            |
| bip_cyc        | fixed       | 2n            |  60 |        1.45   |                 2.18 |                2.01 |  nan    |  nan    | False      |      0.0362   | True        | False            |
| bip_cyc        | fixed       | n             |  60 |        1.45   |                 3.4  |                3.47 |    3.37 |    3.55 | True       |     -0.00977  | True        | True             |
| bip_cyc        | fixed       | n/2           |  60 |        1.45   |                 5.84 |                5.64 |    5.13 |    6.08 | True       |      0.0156   | True        | False            |
| bip_cyc        | fixed       | n/4           |  60 |        1.45   |                10.7  |               10.6  |    9.4  |   11    | True       |      0.00236  | True        | False            |
| bip_cyc        | fixed       | 2n            |  75 |        1.45   |                 2.18 |                2.01 |  nan    |  nan    | False      |      0.0368   | True        | False            |
| bip_cyc        | fixed       | n             |  75 |        1.45   |                 3.4  |                3.41 |    3.32 |    3.52 | True       |     -0.00139  | True        | True             |
| bip_cyc        | fixed       | n/2           |  75 |        1.45   |                 5.92 |                5.24 |    5.1  |    5.62 | True       |      0.0529   | False       | False            |
| bip_cyc        | fixed       | n/4           |  75 |        1.45   |                11.1  |                9.59 |    9.4  |   10.3  | True       |      0.0634   | False       | False            |
| bip_cyc        | fixed       | n/8           |  75 |        1.45   |                21.2  |               20.7  |   18.7  |   21.7  | True       |      0.0117   | True        | False            |
| branch         | bernoulli   | 2n            |  50 |       12.2    |                 2.47 |                2.43 |    2.37 |    2.46 | True       |      0.00767  | False       | False            |
| branch         | bernoulli   | n             |  50 |       12.2    |                 3.5  |                3.11 |    3.01 |    3.36 | True       |      0.0514   | False       | True             |
| branch         | bernoulli   | n/2           |  50 |       12.2    |                 4.95 |                5.11 |    4.64 |    5.25 | True       |     -0.0139   | True        | False            |
| branch         | bernoulli   | n/4           |  50 |       12.2    |                 7.14 |                8.43 |    6.99 |    9.7  | True       |     -0.0724   | True        | False            |
| branch         | bernoulli   | 2n            |  60 |       12.2    |                 2.47 |                2.4  |    2.31 |    2.52 | True       |      0.0132   | True        | False            |
| branch         | bernoulli   | n             |  60 |       12.2    |                 3.5  |                3.48 |    3.35 |    3.57 | True       |      0.00254  | True        | True             |
| branch         | bernoulli   | n/2           |  60 |       12.2    |                 4.95 |                4.87 |    4.76 |    5.02 | True       |      0.0066   | True        | False            |
| branch         | bernoulli   | n/4           |  60 |       12.2    |                 6.99 |                8.19 |    7.9  |    9.33 | True       |     -0.0685   | False       | False            |
| branch         | bernoulli   | 2n            |  75 |       12.2    |                 2.47 |                2.06 |  nan    |  nan    | False      |      0.0794   | False       | False            |
| branch         | bernoulli   | n             |  75 |       12.2    |                 3.5  |                3.63 |    3.51 |    3.74 | True       |     -0.0159   | False       | True             |
| branch         | bernoulli   | n/2           |  75 |       12.2    |                 4.98 |                5.44 |    5.07 |    5.67 | True       |     -0.0386   | False       | False            |
| branch         | bernoulli   | n/4           |  75 |       12.2    |                 7.14 |                8.4  |    7.74 |    9.78 | True       |     -0.0704   | False       | False            |
| branch         | fixed       | 2n            |  50 |        8.55   |                 2.63 |                2.01 |  nan    |  nan    | False      |      0.116    | False       | False            |
| branch         | fixed       | n             |  50 |        8.55   |                 3.47 |                3.31 |    3.23 |    3.44 | True       |      0.0205   | False       | True             |
| branch         | fixed       | n/2           |  50 |        8.55   |                 4.67 |                5.5  |    5    |    6.08 | True       |     -0.0712   | False       | False            |
| branch         | fixed       | n/4           |  50 |        8.55   |                 6.49 |                9.17 |    8.5  |    9.65 | True       |     -0.15     | False       | False            |
| branch         | fixed       | 2n            |  60 |        8.55   |                 2.63 |                2.01 |  nan    |  nan    | False      |      0.117    | False       | False            |
| branch         | fixed       | n             |  60 |        8.55   |                 3.47 |                3.47 |    3.37 |    3.55 | True       |     -0.000941 | True        | True             |
| branch         | fixed       | n/2           |  60 |        8.55   |                 4.67 |                5.64 |    5.13 |    6.08 | True       |     -0.0821   | False       | False            |
| branch         | fixed       | n/4           |  60 |        8.55   |                 6.37 |               10.6  |    9.4  |   11    | True       |     -0.222    | False       | False            |
| branch         | fixed       | 2n            |  75 |        8.55   |                 2.63 |                2.01 |  nan    |  nan    | False      |      0.117    | False       | False            |
| branch         | fixed       | n             |  75 |        8.55   |                 3.47 |                3.41 |    3.32 |    3.52 | True       |      0.00712  | True        | True             |
| branch         | fixed       | n/2           |  75 |        8.55   |                 4.69 |                5.24 |    5.1  |    5.62 | True       |     -0.0478   | False       | False            |
| branch         | fixed       | n/4           |  75 |        8.55   |                 6.49 |                9.59 |    9.4  |   10.3  | True       |     -0.169    | False       | False            |
| branch         | fixed       | n/8           |  75 |        8.55   |                 8.96 |               20.7  |   18.7  |   21.7  | True       |     -0.363    | False       | False            |
| bw_rcm_n       | bernoulli   | 2n            |  50 |        0.624  |                 2.45 |                2.43 |    2.37 |    2.46 | True       |      0.00331  | True        | False            |
| bw_rcm_n       | bernoulli   | n             |  50 |        0.624  |                 3.34 |                3.11 |    3.01 |    3.36 | True       |      0.031    | True        | True             |
| bw_rcm_n       | bernoulli   | n/2           |  50 |        0.624  |                 4.75 |                5.11 |    4.64 |    5.25 | True       |     -0.0312   | True        | False            |
| bw_rcm_n       | bernoulli   | n/4           |  50 |        0.624  |                 7.12 |                8.43 |    6.99 |    9.7  | True       |     -0.0737   | True        | False            |
| bw_rcm_n       | bernoulli   | 2n            |  60 |        0.624  |                 2.51 |                2.4  |    2.31 |    2.52 | True       |      0.0194   | True        | False            |
| bw_rcm_n       | bernoulli   | n             |  60 |        0.624  |                 3.31 |                3.48 |    3.35 |    3.57 | True       |     -0.0208   | False       | True             |
| bw_rcm_n       | bernoulli   | n/2           |  60 |        0.624  |                 4.8  |                4.87 |    4.76 |    5.02 | True       |     -0.00624  | True        | False            |
| bw_rcm_n       | bernoulli   | n/4           |  60 |        0.624  |                 6.88 |                8.19 |    7.9  |    9.33 | True       |     -0.0756   | False       | False            |
| bw_rcm_n       | bernoulli   | 2n            |  75 |        0.624  |                 2.47 |                2.06 |  nan    |  nan    | False      |      0.0797   | False       | False            |
| bw_rcm_n       | bernoulli   | n             |  75 |        0.624  |                 3.49 |                3.63 |    3.51 |    3.74 | True       |     -0.0169   | False       | True             |
| bw_rcm_n       | bernoulli   | n/2           |  75 |        0.624  |                 5.02 |                5.44 |    5.07 |    5.67 | True       |     -0.0351   | False       | False            |
| bw_rcm_n       | bernoulli   | n/4           |  75 |        0.624  |                 7.13 |                8.4  |    7.74 |    9.78 | True       |     -0.0707   | False       | False            |
| bw_rcm_n       | fixed       | 2n            |  50 |        0.58   |                 2.57 |                2.01 |  nan    |  nan    | False      |      0.107    | False       | False            |
| bw_rcm_n       | fixed       | n             |  50 |        0.58   |                 3.41 |                3.31 |    3.23 |    3.44 | True       |      0.0137   | True        | True             |
| bw_rcm_n       | fixed       | n/2           |  50 |        0.58   |                 4.65 |                5.5  |    5    |    6.08 | True       |     -0.0727   | False       | False            |
| bw_rcm_n       | fixed       | n/4           |  50 |        0.58   |                 6.46 |                9.17 |    8.5  |    9.65 | True       |     -0.152    | False       | False            |
| bw_rcm_n       | fixed       | 2n            |  60 |        0.58   |                 2.57 |                2.01 |  nan    |  nan    | False      |      0.107    | False       | False            |
| bw_rcm_n       | fixed       | n             |  60 |        0.58   |                 3.36 |                3.47 |    3.37 |    3.55 | True       |     -0.0144   | False       | True             |
| bw_rcm_n       | fixed       | n/2           |  60 |        0.58   |                 4.69 |                5.64 |    5.13 |    6.08 | True       |     -0.0799   | False       | False            |
| bw_rcm_n       | fixed       | n/4           |  60 |        0.58   |                 6.43 |               10.6  |    9.4  |   11    | True       |     -0.218    | False       | False            |
| bw_rcm_n       | fixed       | 2n            |  75 |        0.58   |                 2.55 |                2.01 |  nan    |  nan    | False      |      0.103    | False       | False            |
| bw_rcm_n       | fixed       | n             |  75 |        0.58   |                 3.39 |                3.41 |    3.32 |    3.52 | True       |     -0.00246  | True        | True             |
| bw_rcm_n       | fixed       | n/2           |  75 |        0.58   |                 4.73 |                5.24 |    5.1  |    5.62 | True       |     -0.0447   | False       | False            |
| bw_rcm_n       | fixed       | n/4           |  75 |        0.58   |                 6.79 |                9.59 |    9.4  |   10.3  | True       |     -0.15     | False       | False            |
| bw_rcm_n       | fixed       | n/8           |  75 |        0.58   |                10.7  |               20.7  |   18.7  |   21.7  | True       |     -0.287    | False       | False            |
| clique_excess  | bernoulli   | 2n            |  50 |        6.67   |               nan    |                2.43 |    2.37 |    2.46 | True       |    nan        | False       | False            |
| clique_excess  | bernoulli   | n             |  50 |        6.67   |               nan    |                3.11 |    3.01 |    3.36 | True       |    nan        | False       | True             |
| clique_excess  | bernoulli   | n/2           |  50 |        6.67   |               nan    |                5.11 |    4.64 |    5.25 | True       |    nan        | False       | False            |
| clique_excess  | bernoulli   | n/4           |  50 |        6.67   |                 9.35 |                8.43 |    6.99 |    9.7  | True       |      0.0447   | True        | False            |
| clique_excess  | bernoulli   | 2n            |  60 |        6.67   |               nan    |                2.4  |    2.31 |    2.52 | True       |    nan        | False       | False            |
| clique_excess  | bernoulli   | n             |  60 |        6.67   |               nan    |                3.48 |    3.35 |    3.57 | True       |    nan        | False       | True             |
| clique_excess  | bernoulli   | n/2           |  60 |        6.67   |               nan    |                4.87 |    4.76 |    5.02 | True       |    nan        | False       | False            |
| clique_excess  | bernoulli   | n/4           |  60 |        6.67   |               nan    |                8.19 |    7.9  |    9.33 | True       |    nan        | False       | False            |
| clique_excess  | bernoulli   | 2n            |  75 |        6.67   |               nan    |                2.06 |  nan    |  nan    | False      |    nan        | False       | False            |
| clique_excess  | bernoulli   | n             |  75 |        6.67   |               nan    |                3.63 |    3.51 |    3.74 | True       |    nan        | False       | True             |
| clique_excess  | bernoulli   | n/2           |  75 |        6.67   |               nan    |                5.44 |    5.07 |    5.67 | True       |    nan        | False       | False            |
| clique_excess  | bernoulli   | n/4           |  75 |        6.67   |               nan    |                8.4  |    7.74 |    9.78 | True       |    nan        | False       | False            |
| clique_excess  | fixed       | 2n            |  50 |        4.51   |               nan    |                2.01 |  nan    |  nan    | False      |    nan        | False       | False            |
| clique_excess  | fixed       | n             |  50 |        4.51   |               nan    |                3.31 |    3.23 |    3.44 | True       |    nan        | False       | True             |
| clique_excess  | fixed       | n/2           |  50 |        4.51   |               nan    |                5.5  |    5    |    6.08 | True       |    nan        | False       | False            |
| clique_excess  | fixed       | n/4           |  50 |        4.51   |               nan    |                9.17 |    8.5  |    9.65 | True       |    nan        | False       | False            |
| clique_excess  | fixed       | 2n            |  60 |        4.51   |               nan    |                2.01 |  nan    |  nan    | False      |    nan        | False       | False            |
| clique_excess  | fixed       | n             |  60 |        4.51   |               nan    |                3.47 |    3.37 |    3.55 | True       |    nan        | False       | True             |
| clique_excess  | fixed       | n/2           |  60 |        4.51   |               nan    |                5.64 |    5.13 |    6.08 | True       |    nan        | False       | False            |
| clique_excess  | fixed       | n/4           |  60 |        4.51   |               nan    |               10.6  |    9.4  |   11    | True       |    nan        | False       | False            |
| clique_excess  | fixed       | 2n            |  75 |        4.51   |               nan    |                2.01 |  nan    |  nan    | False      |    nan        | False       | False            |
| clique_excess  | fixed       | n             |  75 |        4.51   |               nan    |                3.41 |    3.32 |    3.52 | True       |    nan        | False       | True             |
| clique_excess  | fixed       | n/2           |  75 |        4.51   |               nan    |                5.24 |    5.1  |    5.62 | True       |    nan        | False       | False            |
| clique_excess  | fixed       | n/4           |  75 |        4.51   |               nan    |                9.59 |    9.4  |   10.3  | True       |    nan        | False       | False            |
| clique_excess  | fixed       | n/8           |  75 |        4.51   |               nan    |               20.7  |   18.7  |   21.7  | True       |    nan        | False       | False            |
| col_mean       | bernoulli   | 2n            |  50 |        3.45   |                 3.45 |                2.43 |    2.37 |    2.46 | True       |      0.152    | False       | False            |
| col_mean       | bernoulli   | n             |  50 |        3.45   |                 3.45 |                3.11 |    3.01 |    3.36 | True       |      0.0453   | False       | True             |
| col_mean       | bernoulli   | n/2           |  50 |        3.45   |                 3.45 |                5.11 |    4.64 |    5.25 | True       |     -0.171    | False       | False            |
| col_mean       | bernoulli   | n/4           |  50 |        3.45   |                 3.45 |                8.43 |    6.99 |    9.7  | True       |     -0.388    | False       | False            |
| col_mean       | bernoulli   | 2n            |  60 |        3.45   |                 3.45 |                2.4  |    2.31 |    2.52 | True       |      0.158    | False       | False            |
| col_mean       | bernoulli   | n             |  60 |        3.45   |                 3.45 |                3.48 |    3.35 |    3.57 | True       |     -0.00358  | True        | True             |
| col_mean       | bernoulli   | n/2           |  60 |        3.45   |                 3.45 |                4.87 |    4.76 |    5.02 | True       |     -0.15     | False       | False            |
| col_mean       | bernoulli   | n/4           |  60 |        3.45   |                 3.45 |                8.19 |    7.9  |    9.33 | True       |     -0.376    | False       | False            |
| col_mean       | bernoulli   | 2n            |  75 |        3.45   |                 3.45 |                2.06 |  nan    |  nan    | False      |      0.224    | False       | False            |
| col_mean       | bernoulli   | n             |  75 |        3.45   |                 3.45 |                3.63 |    3.51 |    3.74 | True       |     -0.022    | False       | True             |
| col_mean       | bernoulli   | n/2           |  75 |        3.45   |                 3.45 |                5.44 |    5.07 |    5.67 | True       |     -0.198    | False       | False            |
| col_mean       | bernoulli   | n/4           |  75 |        3.45   |                 3.45 |                8.4  |    7.74 |    9.78 | True       |     -0.386    | False       | False            |
| col_mean       | fixed       | 2n            |  50 |        3.43   |                 3.43 |                2.01 |  nan    |  nan    | False      |      0.232    | False       | False            |
| col_mean       | fixed       | n             |  50 |        3.43   |                 3.43 |                3.31 |    3.23 |    3.44 | True       |      0.0157   | True        | True             |
| col_mean       | fixed       | n/2           |  50 |        3.43   |                 3.43 |                5.5  |    5    |    6.08 | True       |     -0.205    | False       | False            |
| col_mean       | fixed       | n/4           |  50 |        3.43   |                 3.43 |                9.17 |    8.5  |    9.65 | True       |     -0.427    | False       | False            |
| col_mean       | fixed       | 2n            |  60 |        3.43   |                 3.43 |                2.01 |  nan    |  nan    | False      |      0.232    | False       | False            |
| col_mean       | fixed       | n             |  60 |        3.43   |                 3.43 |                3.47 |    3.37 |    3.55 | True       |     -0.00578  | True        | True             |
| col_mean       | fixed       | n/2           |  60 |        3.43   |                 3.43 |                5.64 |    5.13 |    6.08 | True       |     -0.216    | False       | False            |
| col_mean       | fixed       | n/4           |  60 |        3.43   |                 3.43 |               10.6  |    9.4  |   11    | True       |     -0.491    | False       | False            |
| col_mean       | fixed       | 2n            |  75 |        3.43   |                 3.43 |                2.01 |  nan    |  nan    | False      |      0.233    | False       | False            |
| col_mean       | fixed       | n             |  75 |        3.43   |                 3.43 |                3.41 |    3.32 |    3.52 | True       |      0.00228  | True        | True             |
| col_mean       | fixed       | n/2           |  75 |        3.43   |                 3.43 |                5.24 |    5.1  |    5.62 | True       |     -0.184    | False       | False            |
| col_mean       | fixed       | n/4           |  75 |        3.43   |                 3.43 |                9.59 |    9.4  |   10.3  | True       |     -0.447    | False       | False            |
| col_mean       | fixed       | n/8           |  75 |        3.43   |                 3.43 |               20.7  |   18.7  |   21.7  | True       |     -0.78     | False       | False            |
| excess         | bernoulli   | 2n            |  50 |        2.45   |                 2.22 |                2.43 |    2.37 |    2.46 | True       |     -0.0384   | False       | False            |
| excess         | bernoulli   | n             |  50 |        2.45   |                 3.45 |                3.11 |    3.01 |    3.36 | True       |      0.0453   | False       | True             |
| excess         | bernoulli   | n/2           |  50 |        2.45   |                 5.9  |                5.11 |    4.64 |    5.25 | True       |      0.0624   | False       | False            |
| excess         | bernoulli   | n/4           |  50 |        2.45   |                11.2  |                8.43 |    6.99 |    9.7  | True       |      0.123    | False       | False            |
| excess         | bernoulli   | 2n            |  60 |        2.45   |                 2.22 |                2.4  |    2.31 |    2.52 | True       |     -0.0329   | False       | False            |
| excess         | bernoulli   | n             |  60 |        2.45   |                 3.45 |                3.48 |    3.35 |    3.57 | True       |     -0.00358  | True        | True             |
| excess         | bernoulli   | n/2           |  60 |        2.45   |                 5.9  |                4.87 |    4.76 |    5.02 | True       |      0.083    | False       | False            |
| excess         | bernoulli   | n/4           |  60 |        2.45   |                10.8  |                8.19 |    7.9  |    9.33 | True       |      0.12     | False       | False            |
| excess         | bernoulli   | 2n            |  75 |        2.45   |                 2.22 |                2.06 |  nan    |  nan    | False      |      0.0333   | True        | False            |
| excess         | bernoulli   | n             |  75 |        2.45   |                 3.45 |                3.63 |    3.51 |    3.74 | True       |     -0.022    | False       | True             |
| excess         | bernoulli   | n/2           |  75 |        2.45   |                 5.96 |                5.44 |    5.07 |    5.67 | True       |      0.0397   | False       | False            |
| excess         | bernoulli   | n/4           |  75 |        2.45   |                11.2  |                8.4  |    7.74 |    9.78 | True       |      0.125    | False       | False            |
| excess         | fixed       | 2n            |  50 |        2.43   |                 2.21 |                2.01 |  nan    |  nan    | False      |      0.042    | True        | False            |
| excess         | fixed       | n             |  50 |        2.43   |                 3.43 |                3.31 |    3.23 |    3.44 | True       |      0.0157   | True        | True             |
| excess         | fixed       | n/2           |  50 |        2.43   |                 5.86 |                5.5  |    5    |    6.08 | True       |      0.0275   | True        | False            |
| excess         | fixed       | n/4           |  50 |        2.43   |                11.1  |                9.17 |    8.5  |    9.65 | True       |      0.0836   | False       | False            |
| excess         | fixed       | 2n            |  60 |        2.43   |                 2.21 |                2.01 |  nan    |  nan    | False      |      0.0424   | True        | False            |
| excess         | fixed       | n             |  60 |        2.43   |                 3.43 |                3.47 |    3.37 |    3.55 | True       |     -0.00578  | True        | True             |
| excess         | fixed       | n/2           |  60 |        2.43   |                 5.86 |                5.64 |    5.13 |    6.08 | True       |      0.0167   | True        | False            |
| excess         | fixed       | n/4           |  60 |        2.43   |                10.7  |               10.6  |    9.4  |   11    | True       |      0.0035   | True        | False            |
| excess         | fixed       | 2n            |  75 |        2.43   |                 2.21 |                2.01 |  nan    |  nan    | False      |      0.0428   | True        | False            |
| excess         | fixed       | n             |  75 |        2.43   |                 3.43 |                3.41 |    3.32 |    3.52 | True       |      0.00228  | True        | True             |
| excess         | fixed       | n/2           |  75 |        2.43   |                 5.92 |                5.24 |    5.1  |    5.62 | True       |      0.0532   | False       | False            |
| excess         | fixed       | n/4           |  75 |        2.43   |                11.1  |                9.59 |    9.4  |   10.3  | True       |      0.0644   | False       | False            |
| excess         | fixed       | n/8           |  75 |        2.43   |                21.2  |               20.7  |   18.7  |   21.7  | True       |      0.0121   | True        | False            |
| g_clustering   | bernoulli   | 2n            |  50 |        0.507  |                 3.28 |                2.43 |    2.37 |    2.46 | True       |      0.13     | False       | False            |
| g_clustering   | bernoulli   | n             |  50 |        0.507  |                 2.44 |                3.11 |    3.01 |    3.36 | True       |     -0.106    | False       | True             |
| g_clustering   | bernoulli   | n/2           |  50 |        0.507  |               nan    |                5.11 |    4.64 |    5.25 | True       |    nan        | False       | False            |
| g_clustering   | bernoulli   | n/4           |  50 |        0.507  |               nan    |                8.43 |    6.99 |    9.7  | True       |    nan        | False       | False            |
| g_clustering   | bernoulli   | 2n            |  60 |        0.507  |                 3.77 |                2.4  |    2.31 |    2.52 | True       |      0.196    | False       | False            |
| g_clustering   | bernoulli   | n             |  60 |        0.507  |                 3.41 |                3.48 |    3.35 |    3.57 | True       |     -0.00907  | True        | True             |
| g_clustering   | bernoulli   | n/2           |  60 |        0.507  |               nan    |                4.87 |    4.76 |    5.02 | True       |    nan        | False       | False            |
| g_clustering   | bernoulli   | n/4           |  60 |        0.507  |               nan    |                8.19 |    7.9  |    9.33 | True       |    nan        | False       | False            |
| g_clustering   | bernoulli   | 2n            |  75 |        0.507  |                 4.36 |                2.06 |  nan    |  nan    | False      |      0.325    | False       | False            |
| g_clustering   | bernoulli   | n             |  75 |        0.507  |                 5.16 |                3.63 |    3.51 |    3.74 | True       |      0.153    | False       | True             |
| g_clustering   | bernoulli   | n/2           |  75 |        0.507  |               nan    |                5.44 |    5.07 |    5.67 | True       |    nan        | False       | False            |
| g_clustering   | bernoulli   | n/4           |  75 |        0.507  |               nan    |                8.4  |    7.74 |    9.78 | True       |    nan        | False       | False            |
| g_clustering   | fixed       | 2n            |  50 |        0.429  |                 3.68 |                2.01 |  nan    |  nan    | False      |      0.263    | False       | False            |
| g_clustering   | fixed       | n             |  50 |        0.429  |                 3.01 |                3.31 |    3.23 |    3.44 | True       |     -0.041    | False       | True             |
| g_clustering   | fixed       | n/2           |  50 |        0.429  |               nan    |                5.5  |    5    |    6.08 | True       |    nan        | False       | False            |
| g_clustering   | fixed       | n/4           |  50 |        0.429  |               nan    |                9.17 |    8.5  |    9.65 | True       |    nan        | False       | False            |
| g_clustering   | fixed       | 2n            |  60 |        0.429  |                 4.06 |                2.01 |  nan    |  nan    | False      |      0.306    | False       | False            |
| g_clustering   | fixed       | n             |  60 |        0.429  |                 3    |                3.47 |    3.37 |    3.55 | True       |     -0.0638   | False       | True             |
| g_clustering   | fixed       | n/2           |  60 |        0.429  |               nan    |                5.64 |    5.13 |    6.08 | True       |    nan        | False       | False            |
| g_clustering   | fixed       | n/4           |  60 |        0.429  |               nan    |               10.6  |    9.4  |   11    | True       |    nan        | False       | False            |
| g_clustering   | fixed       | 2n            |  75 |        0.429  |                 4.48 |                2.01 |  nan    |  nan    | False      |      0.348    | False       | False            |
| g_clustering   | fixed       | n             |  75 |        0.429  |                 5.13 |                3.41 |    3.32 |    3.52 | True       |      0.177    | False       | True             |
| g_clustering   | fixed       | n/2           |  75 |        0.429  |               nan    |                5.24 |    5.1  |    5.62 | True       |    nan        | False       | False            |
| g_clustering   | fixed       | n/4           |  75 |        0.429  |               nan    |                9.59 |    9.4  |   10.3  | True       |    nan        | False       | False            |
| g_clustering   | fixed       | n/8           |  75 |        0.429  |               nan    |               20.7  |   18.7  |   21.7  | True       |    nan        | False       | False            |
| g_deg_mean     | bernoulli   | 2n            |  50 |       10.6    |                 2.47 |                2.43 |    2.37 |    2.46 | True       |      0.00628  | False       | False            |
| g_deg_mean     | bernoulli   | n             |  50 |       10.6    |                 3.48 |                3.11 |    3.01 |    3.36 | True       |      0.0497   | False       | True             |
| g_deg_mean     | bernoulli   | n/2           |  50 |       10.6    |                 4.92 |                5.11 |    4.64 |    5.25 | True       |     -0.0161   | True        | False            |
| g_deg_mean     | bernoulli   | n/4           |  50 |       10.6    |                 7.08 |                8.43 |    6.99 |    9.7  | True       |     -0.0757   | True        | False            |
| g_deg_mean     | bernoulli   | 2n            |  60 |       10.6    |                 2.43 |                2.4  |    2.31 |    2.52 | True       |      0.00638  | True        | False            |
| g_deg_mean     | bernoulli   | n             |  60 |       10.6    |                 3.44 |                3.48 |    3.35 |    3.57 | True       |     -0.00446  | True        | True             |
| g_deg_mean     | bernoulli   | n/2           |  60 |       10.6    |                 4.86 |                4.87 |    4.76 |    5.02 | True       |     -0.000753 | True        | False            |
| g_deg_mean     | bernoulli   | n/4           |  60 |       10.6    |                 6.87 |                8.19 |    7.9  |    9.33 | True       |     -0.0766   | False       | False            |
| g_deg_mean     | bernoulli   | 2n            |  75 |       10.6    |                 2.41 |                2.06 |  nan    |  nan    | False      |      0.0673   | False       | False            |
| g_deg_mean     | bernoulli   | n             |  75 |       10.6    |                 3.4  |                3.63 |    3.51 |    3.74 | True       |     -0.0281   | False       | True             |
| g_deg_mean     | bernoulli   | n/2           |  75 |       10.6    |                 4.84 |                5.44 |    5.07 |    5.67 | True       |     -0.051    | False       | False            |
| g_deg_mean     | bernoulli   | n/4           |  75 |       10.6    |                 6.93 |                8.4  |    7.74 |    9.78 | True       |     -0.0833   | False       | False            |
| g_deg_mean     | fixed       | 2n            |  50 |        7.98   |                 2.64 |                2.01 |  nan    |  nan    | False      |      0.119    | False       | False            |
| g_deg_mean     | fixed       | n             |  50 |        7.98   |                 3.49 |                3.31 |    3.23 |    3.44 | True       |      0.0234   | False       | True             |
| g_deg_mean     | fixed       | n/2           |  50 |        7.98   |                 4.69 |                5.5  |    5    |    6.08 | True       |     -0.0686   | False       | False            |
| g_deg_mean     | fixed       | n/4           |  50 |        7.98   |                 6.52 |                9.17 |    8.5  |    9.65 | True       |     -0.148    | False       | False            |
| g_deg_mean     | fixed       | 2n            |  60 |        7.98   |                 2.63 |                2.01 |  nan    |  nan    | False      |      0.117    | False       | False            |
| g_deg_mean     | fixed       | n             |  60 |        7.98   |                 3.47 |                3.47 |    3.37 |    3.55 | True       |     -0.000835 | True        | True             |
| g_deg_mean     | fixed       | n/2           |  60 |        7.98   |                 4.66 |                5.64 |    5.13 |    6.08 | True       |     -0.0822   | False       | False            |
| g_deg_mean     | fixed       | n/4           |  60 |        7.98   |                 6.36 |               10.6  |    9.4  |   11    | True       |     -0.223    | False       | False            |
| g_deg_mean     | fixed       | 2n            |  75 |        7.98   |                 2.61 |                2.01 |  nan    |  nan    | False      |      0.115    | False       | False            |
| g_deg_mean     | fixed       | n             |  75 |        7.98   |                 3.45 |                3.41 |    3.32 |    3.52 | True       |      0.00456  | True        | True             |
| g_deg_mean     | fixed       | n/2           |  75 |        7.98   |                 4.66 |                5.24 |    5.1  |    5.62 | True       |     -0.0506   | False       | False            |
| g_deg_mean     | fixed       | n/4           |  75 |        7.98   |                 6.44 |                9.59 |    9.4  |   10.3  | True       |     -0.173    | False       | False            |
| g_deg_mean     | fixed       | n/8           |  75 |        7.98   |                 8.87 |               20.7  |   18.7  |   21.7  | True       |     -0.367    | False       | False            |
| g_degeneracy_n | bernoulli   | 2n            |  50 |        0.135  |                 2.19 |                2.43 |    2.37 |    2.46 | True       |     -0.0451   | False       | False            |
| g_degeneracy_n | bernoulli   | n             |  50 |        0.135  |                 2.88 |                3.11 |    3.01 |    3.36 | True       |     -0.0326   | False       | True             |
| g_degeneracy_n | bernoulli   | n/2           |  50 |        0.135  |                 3.94 |                5.11 |    4.64 |    5.25 | True       |     -0.113    | False       | False            |
| g_degeneracy_n | bernoulli   | n/4           |  50 |        0.135  |               nan    |                8.43 |    6.99 |    9.7  | True       |    nan        | False       | False            |
| g_degeneracy_n | bernoulli   | 2n            |  60 |        0.135  |                 2.55 |                2.4  |    2.31 |    2.52 | True       |      0.0258   | False       | False            |
| g_degeneracy_n | bernoulli   | n             |  60 |        0.135  |                 3.39 |                3.48 |    3.35 |    3.57 | True       |     -0.0116   | True        | True             |
| g_degeneracy_n | bernoulli   | n/2           |  60 |        0.135  |                 4.22 |                4.87 |    4.76 |    5.02 | True       |     -0.0624   | False       | False            |
| g_degeneracy_n | bernoulli   | n/4           |  60 |        0.135  |                 4.81 |                8.19 |    7.9  |    9.33 | True       |     -0.231    | False       | False            |
| g_degeneracy_n | bernoulli   | 2n            |  75 |        0.135  |                 2.73 |                2.06 |  nan    |  nan    | False      |      0.122    | False       | False            |
| g_degeneracy_n | bernoulli   | n             |  75 |        0.135  |                 3.97 |                3.63 |    3.51 |    3.74 | True       |      0.0387   | False       | True             |
| g_degeneracy_n | bernoulli   | n/2           |  75 |        0.135  |                 5.16 |                5.44 |    5.07 |    5.67 | True       |     -0.0234   | True        | False            |
| g_degeneracy_n | bernoulli   | n/4           |  75 |        0.135  |                 6.28 |                8.4  |    7.74 |    9.78 | True       |     -0.126    | False       | False            |
| g_degeneracy_n | fixed       | 2n            |  50 |        0.0926 |                 2.37 |                2.01 |  nan    |  nan    | False      |      0.0708   | False       | False            |
| g_degeneracy_n | fixed       | n             |  50 |        0.0926 |                 3.18 |                3.31 |    3.23 |    3.44 | True       |     -0.0175   | False       | True             |
| g_degeneracy_n | fixed       | n/2           |  50 |        0.0926 |                 3.93 |                5.5  |    5    |    6.08 | True       |     -0.145    | False       | False            |
| g_degeneracy_n | fixed       | n/4           |  50 |        0.0926 |               nan    |                9.17 |    8.5  |    9.65 | True       |    nan        | False       | False            |
| g_degeneracy_n | fixed       | 2n            |  60 |        0.0926 |                 2.59 |                2.01 |  nan    |  nan    | False      |      0.111    | False       | False            |
| g_degeneracy_n | fixed       | n             |  60 |        0.0926 |                 3.39 |                3.47 |    3.37 |    3.55 | True       |     -0.0101   | True        | True             |
| g_degeneracy_n | fixed       | n/2           |  60 |        0.0926 |                 4.49 |                5.64 |    5.13 |    6.08 | True       |     -0.0987   | False       | False            |
| g_degeneracy_n | fixed       | n/4           |  60 |        0.0926 |               nan    |               10.6  |    9.4  |   11    | True       |    nan        | False       | False            |
| g_degeneracy_n | fixed       | 2n            |  75 |        0.0926 |                 2.76 |                2.01 |  nan    |  nan    | False      |      0.138    | False       | False            |
| g_degeneracy_n | fixed       | n             |  75 |        0.0926 |                 3.73 |                3.41 |    3.32 |    3.52 | True       |      0.0388   | False       | True             |
| g_degeneracy_n | fixed       | n/2           |  75 |        0.0926 |                 5.11 |                5.24 |    5.1  |    5.62 | True       |     -0.011    | True        | False            |
| g_degeneracy_n | fixed       | n/4           |  75 |        0.0926 |               nan    |                9.59 |    9.4  |   10.3  | True       |    nan        | False       | False            |
| g_degeneracy_n | fixed       | n/8           |  75 |        0.0926 |               nan    |               20.7  |   18.7  |   21.7  | True       |    nan        | False       | False            |
| g_density      | bernoulli   | 2n            |  50 |        0.176  |                 2.2  |                2.43 |    2.37 |    2.46 | True       |     -0.0439   | False       | False            |
| g_density      | bernoulli   | n             |  50 |        0.176  |                 3.1  |                3.11 |    3.01 |    3.36 | True       |     -0.000399 | True        | True             |
| g_density      | bernoulli   | n/2           |  50 |        0.176  |                 4.39 |                5.11 |    4.64 |    5.25 | True       |     -0.0661   | False       | False            |
| g_density      | bernoulli   | n/4           |  50 |        0.176  |                 6.32 |                8.43 |    6.99 |    9.7  | True       |     -0.125    | False       | False            |
| g_density      | bernoulli   | 2n            |  60 |        0.176  |                 2.41 |                2.4  |    2.31 |    2.52 | True       |      0.00126  | True        | False            |
| g_density      | bernoulli   | n             |  60 |        0.176  |                 3.4  |                3.48 |    3.35 |    3.57 | True       |     -0.00957  | True        | True             |
| g_density      | bernoulli   | n/2           |  60 |        0.176  |                 4.81 |                4.87 |    4.76 |    5.02 | True       |     -0.00586  | True        | False            |
| g_density      | bernoulli   | n/4           |  60 |        0.176  |                 6.79 |                8.19 |    7.9  |    9.33 | True       |     -0.0817   | False       | False            |
| g_density      | bernoulli   | 2n            |  75 |        0.176  |                 2.69 |                2.06 |  nan    |  nan    | False      |      0.116    | False       | False            |
| g_density      | bernoulli   | n             |  75 |        0.176  |                 3.8  |                3.63 |    3.51 |    3.74 | True       |      0.0205   | False       | True             |
| g_density      | bernoulli   | n/2           |  75 |        0.176  |                 5.41 |                5.44 |    5.07 |    5.67 | True       |     -0.00246  | True        | False            |
| g_density      | bernoulli   | n/4           |  75 |        0.176  |                 7.75 |                8.4  |    7.74 |    9.78 | True       |     -0.0349   | True        | False            |
| g_density      | fixed       | 2n            |  50 |        0.134  |                 2.44 |                2.01 |  nan    |  nan    | False      |      0.085    | False       | False            |
| g_density      | fixed       | n             |  50 |        0.134  |                 3.2  |                3.31 |    3.23 |    3.44 | True       |     -0.0138   | False       | True             |
| g_density      | fixed       | n/2           |  50 |        0.134  |                 4.29 |                5.5  |    5    |    6.08 | True       |     -0.108    | False       | False            |
| g_density      | fixed       | n/4           |  50 |        0.134  |                 5.93 |                9.17 |    8.5  |    9.65 | True       |     -0.189    | False       | False            |
| g_density      | fixed       | 2n            |  60 |        0.134  |                 2.62 |                2.01 |  nan    |  nan    | False      |      0.116    | False       | False            |
| g_density      | fixed       | n             |  60 |        0.134  |                 3.46 |                3.47 |    3.37 |    3.55 | True       |     -0.00202  | True        | True             |
| g_density      | fixed       | n/2           |  60 |        0.134  |                 4.65 |                5.64 |    5.13 |    6.08 | True       |     -0.0835   | False       | False            |
| g_density      | fixed       | n/4           |  60 |        0.134  |                 6.34 |               10.6  |    9.4  |   11    | True       |     -0.224    | False       | False            |
| g_density      | fixed       | 2n            |  75 |        0.134  |                 2.86 |                2.01 |  nan    |  nan    | False      |      0.154    | False       | False            |
| g_density      | fixed       | n             |  75 |        0.134  |                 3.8  |                3.41 |    3.32 |    3.52 | True       |      0.0474   | False       | True             |
| g_density      | fixed       | n/2           |  75 |        0.134  |                 5.17 |                5.24 |    5.1  |    5.62 | True       |     -0.00544  | True        | False            |
| g_density      | fixed       | n/4           |  75 |        0.134  |                 7.18 |                9.59 |    9.4  |   10.3  | True       |     -0.126    | False       | False            |
| g_density      | fixed       | n/8           |  75 |        0.134  |                 9.91 |               20.7  |   18.7  |   21.7  | True       |     -0.319    | False       | False            |
| g_edges_n      | bernoulli   | 2n            |  50 |        5.29   |                 2.53 |                2.43 |    2.37 |    2.46 | True       |      0.0171   | False       | False            |
| g_edges_n      | bernoulli   | n             |  50 |        5.29   |                 3.5  |                3.11 |    3.01 |    3.36 | True       |      0.0514   | False       | True             |
| g_edges_n      | bernoulli   | n/2           |  50 |        5.29   |                 4.84 |                5.11 |    4.64 |    5.25 | True       |     -0.0233   | True        | False            |
| g_edges_n      | bernoulli   | n/4           |  50 |        5.29   |                 6.88 |                8.43 |    6.99 |    9.7  | True       |     -0.0885   | False       | False            |
| g_edges_n      | bernoulli   | 2n            |  60 |        5.29   |                 2.42 |                2.4  |    2.31 |    2.52 | True       |      0.00357  | True        | False            |
| g_edges_n      | bernoulli   | n             |  60 |        5.29   |                 3.41 |                3.48 |    3.35 |    3.57 | True       |     -0.00867  | True        | True             |
| g_edges_n      | bernoulli   | n/2           |  60 |        5.29   |                 4.75 |                4.87 |    4.76 |    5.02 | True       |     -0.0108   | False       | False            |
| g_edges_n      | bernoulli   | n/4           |  60 |        5.29   |                 6.74 |                8.19 |    7.9  |    9.33 | True       |     -0.0849   | False       | False            |
| g_edges_n      | bernoulli   | 2n            |  75 |        5.29   |                 2.36 |                2.06 |  nan    |  nan    | False      |      0.0589   | False       | False            |
| g_edges_n      | bernoulli   | n             |  75 |        5.29   |                 3.3  |                3.63 |    3.51 |    3.74 | True       |     -0.0411   | False       | True             |
| g_edges_n      | bernoulli   | n/2           |  75 |        5.29   |                 4.72 |                5.44 |    5.07 |    5.67 | True       |     -0.0617   | False       | False            |
| g_edges_n      | bernoulli   | n/4           |  75 |        5.29   |                 6.77 |                8.4  |    7.74 |    9.78 | True       |     -0.0936   | False       | False            |
| g_edges_n      | fixed       | 2n            |  50 |        3.99   |                 2.56 |                2.01 |  nan    |  nan    | False      |      0.105    | False       | False            |
| g_edges_n      | fixed       | n             |  50 |        3.99   |                 3.42 |                3.31 |    3.23 |    3.44 | True       |      0.014    | True        | True             |
| g_edges_n      | fixed       | n/2           |  50 |        3.99   |                 4.6  |                5.5  |    5    |    6.08 | True       |     -0.0773   | False       | False            |
| g_edges_n      | fixed       | n/4           |  50 |        3.99   |                 6.26 |                9.17 |    8.5  |    9.65 | True       |     -0.166    | False       | False            |
| g_edges_n      | fixed       | 2n            |  60 |        3.99   |                 2.53 |                2.01 |  nan    |  nan    | False      |      0.101    | False       | False            |
| g_edges_n      | fixed       | n             |  60 |        3.99   |                 3.4  |                3.47 |    3.37 |    3.55 | True       |     -0.00912  | True        | True             |
| g_edges_n      | fixed       | n/2           |  60 |        3.99   |                 4.59 |                5.64 |    5.13 |    6.08 | True       |     -0.0893   | False       | False            |
| g_edges_n      | fixed       | n/4           |  60 |        3.99   |                 6.13 |               10.6  |    9.4  |   11    | True       |     -0.239    | False       | False            |
| g_edges_n      | fixed       | 2n            |  75 |        3.99   |                 2.51 |                2.01 |  nan    |  nan    | False      |      0.098    | False       | False            |
| g_edges_n      | fixed       | n             |  75 |        3.99   |                 3.38 |                3.41 |    3.32 |    3.52 | True       |     -0.00452  | True        | True             |
| g_edges_n      | fixed       | n/2           |  75 |        3.99   |                 4.56 |                5.24 |    5.1  |    5.62 | True       |     -0.0602   | False       | False            |
| g_edges_n      | fixed       | n/4           |  75 |        3.99   |                 6.26 |                9.59 |    9.4  |   10.3  | True       |     -0.185    | False       | False            |
| g_edges_n      | fixed       | n/8           |  75 |        3.99   |               nan    |               20.7  |   18.7  |   21.7  | True       |    nan        | False       | False            |
| lb_best_n      | bernoulli   | 2n            |  50 |        0.254  |                 2.08 |                2.43 |    2.37 |    2.46 | True       |     -0.0676   | False       | False            |
| lb_best_n      | bernoulli   | n             |  50 |        0.254  |                 3.11 |                3.11 |    3.01 |    3.36 | True       |      0.001    | True        | True             |
| lb_best_n      | bernoulli   | n/2           |  50 |        0.254  |                 4.73 |                5.11 |    4.64 |    5.25 | True       |     -0.0337   | True        | False            |
| lb_best_n      | bernoulli   | n/4           |  50 |        0.254  |                 7.51 |                8.43 |    6.99 |    9.7  | True       |     -0.0507   | True        | False            |
| lb_best_n      | bernoulli   | 2n            |  60 |        0.254  |                 2.19 |                2.4  |    2.31 |    2.52 | True       |     -0.0406   | False       | False            |
| lb_best_n      | bernoulli   | n             |  60 |        0.254  |                 3.33 |                3.48 |    3.35 |    3.57 | True       |     -0.0186   | False       | True             |
| lb_best_n      | bernoulli   | n/2           |  60 |        0.254  |                 5.15 |                4.87 |    4.76 |    5.02 | True       |      0.0244   | False       | False            |
| lb_best_n      | bernoulli   | n/4           |  60 |        0.254  |                 8.13 |                8.19 |    7.9  |    9.33 | True       |     -0.00311  | True        | False            |
| lb_best_n      | bernoulli   | 2n            |  75 |        0.254  |                 2.35 |                2.06 |  nan    |  nan    | False      |      0.0565   | False       | False            |
| lb_best_n      | bernoulli   | n             |  75 |        0.254  |                 3.86 |                3.63 |    3.51 |    3.74 | True       |      0.0268   | False       | True             |
| lb_best_n      | bernoulli   | n/2           |  75 |        0.254  |                 5.86 |                5.44 |    5.07 |    5.67 | True       |      0.0318   | False       | False            |
| lb_best_n      | bernoulli   | n/4           |  75 |        0.254  |                 8.91 |                8.4  |    7.74 |    9.78 | True       |      0.0259   | True        | False            |
| lb_best_n      | fixed       | 2n            |  50 |        0.225  |                 2.22 |                2.01 |  nan    |  nan    | False      |      0.0437   | True        | False            |
| lb_best_n      | fixed       | n             |  50 |        0.225  |                 3.2  |                3.31 |    3.23 |    3.44 | True       |     -0.0145   | False       | True             |
| lb_best_n      | fixed       | n/2           |  50 |        0.225  |                 4.75 |                5.5  |    5    |    6.08 | True       |     -0.0635   | False       | False            |
| lb_best_n      | fixed       | n/4           |  50 |        0.225  |                 7.75 |                9.17 |    8.5  |    9.65 | True       |     -0.0731   | False       | False            |
| lb_best_n      | fixed       | 2n            |  60 |        0.225  |                 2.31 |                2.01 |  nan    |  nan    | False      |      0.0606   | False       | False            |
| lb_best_n      | fixed       | n             |  60 |        0.225  |                 3.4  |                3.47 |    3.37 |    3.55 | True       |     -0.00979  | True        | True             |
| lb_best_n      | fixed       | n/2           |  60 |        0.225  |                 5.23 |                5.64 |    5.13 |    6.08 | True       |     -0.0329   | True        | False            |
| lb_best_n      | fixed       | n/4           |  60 |        0.225  |                 8.01 |               10.6  |    9.4  |   11    | True       |     -0.123    | False       | False            |
| lb_best_n      | fixed       | 2n            |  75 |        0.225  |                 2.45 |                2.01 |  nan    |  nan    | False      |      0.0861   | False       | False            |
| lb_best_n      | fixed       | n             |  75 |        0.225  |                 3.65 |                3.41 |    3.32 |    3.52 | True       |      0.0292   | False       | True             |
| lb_best_n      | fixed       | n/2           |  75 |        0.225  |                 5.66 |                5.24 |    5.1  |    5.62 | True       |      0.0339   | False       | False            |
| lb_best_n      | fixed       | n/4           |  75 |        0.225  |                 8.77 |                9.59 |    9.4  |   10.3  | True       |     -0.0385   | False       | False            |
| lb_best_n      | fixed       | n/8           |  75 |        0.225  |                14.1  |               20.7  |   18.7  |   21.7  | True       |     -0.167    | False       | False            |
| opt_frac       | bernoulli   | 2n            |  50 |        0.358  |                 2.24 |                2.43 |    2.37 |    2.46 | True       |     -0.0354   | False       | False            |
| opt_frac       | bernoulli   | n             |  50 |        0.358  |                 3.34 |                3.11 |    3.01 |    3.36 | True       |      0.0317   | True        | True             |
| opt_frac       | bernoulli   | n/2           |  50 |        0.358  |                 5.15 |                5.11 |    4.64 |    5.25 | True       |      0.00383  | True        | False            |
| opt_frac       | bernoulli   | n/4           |  50 |        0.358  |                 8.29 |                8.43 |    6.99 |    9.7  | True       |     -0.00757  | True        | False            |
| opt_frac       | bernoulli   | 2n            |  60 |        0.358  |                 2.34 |                2.4  |    2.31 |    2.52 | True       |     -0.0111   | True        | False            |
| opt_frac       | bernoulli   | n             |  60 |        0.358  |                 3.38 |                3.48 |    3.35 |    3.57 | True       |     -0.0128   | True        | True             |
| opt_frac       | bernoulli   | n/2           |  60 |        0.358  |                 5.14 |                4.87 |    4.76 |    5.02 | True       |      0.0236   | False       | False            |
| opt_frac       | bernoulli   | n/4           |  60 |        0.358  |                 8.43 |                8.19 |    7.9  |    9.33 | True       |      0.0124   | True        | False            |
| opt_frac       | bernoulli   | 2n            |  75 |        0.358  |                 2.41 |                2.06 |  nan    |  nan    | False      |      0.0681   | False       | False            |
| opt_frac       | bernoulli   | n             |  75 |        0.358  |                 3.48 |                3.63 |    3.51 |    3.74 | True       |     -0.0175   | False       | True             |
| opt_frac       | bernoulli   | n/2           |  75 |        0.358  |                 5.48 |                5.44 |    5.07 |    5.67 | True       |      0.00269  | True        | False            |
| opt_frac       | bernoulli   | n/4           |  75 |        0.358  |                 9.09 |                8.4  |    7.74 |    9.78 | True       |      0.0345   | True        | False            |
| opt_frac       | fixed       | 2n            |  50 |        0.323  |                 2.36 |                2.01 |  nan    |  nan    | False      |      0.0689   | False       | False            |
| opt_frac       | fixed       | n             |  50 |        0.323  |                 3.29 |                3.31 |    3.23 |    3.44 | True       |     -0.00172  | True        | True             |
| opt_frac       | fixed       | n/2           |  50 |        0.323  |                 4.99 |                5.5  |    5    |    6.08 | True       |     -0.0417   | False       | False            |
| opt_frac       | fixed       | n/4           |  50 |        0.323  |                 7.98 |                9.17 |    8.5  |    9.65 | True       |     -0.0607   | False       | False            |
| opt_frac       | fixed       | 2n            |  60 |        0.323  |                 2.38 |                2.01 |  nan    |  nan    | False      |      0.0741   | False       | False            |
| opt_frac       | fixed       | n             |  60 |        0.323  |                 3.38 |                3.47 |    3.37 |    3.55 | True       |     -0.0117   | True        | True             |
| opt_frac       | fixed       | n/2           |  60 |        0.323  |                 5.12 |                5.64 |    5.13 |    6.08 | True       |     -0.0421   | False       | False            |
| opt_frac       | fixed       | n/4           |  60 |        0.323  |                 8.09 |               10.6  |    9.4  |   11    | True       |     -0.118    | False       | False            |
| opt_frac       | fixed       | 2n            |  75 |        0.323  |                 2.44 |                2.01 |  nan    |  nan    | False      |      0.0848   | False       | False            |
| opt_frac       | fixed       | n             |  75 |        0.323  |                 3.51 |                3.41 |    3.32 |    3.52 | True       |      0.0126   | True        | True             |
| opt_frac       | fixed       | n/2           |  75 |        0.323  |                 5.32 |                5.24 |    5.1  |    5.62 | True       |      0.00628  | True        | False            |
| opt_frac       | fixed       | n/4           |  75 |        0.323  |                 8.72 |                9.59 |    9.4  |   10.3  | True       |     -0.041    | False       | False            |
| opt_frac       | fixed       | n/8           |  75 |        0.323  |                13.8  |               20.7  |   18.7  |   21.7  | True       |     -0.175    | False       | False            |
| row_mean       | bernoulli   | 2n            |  50 |        3.45   |                 1.72 |                2.43 |    2.37 |    2.46 | True       |     -0.149    | False       | False            |
| row_mean       | bernoulli   | n             |  50 |        3.45   |                 3.45 |                3.11 |    3.01 |    3.36 | True       |      0.0453   | False       | True             |
| row_mean       | bernoulli   | n/2           |  50 |        3.45   |                 6.9  |                5.11 |    4.64 |    5.25 | True       |      0.13     | False       | False            |
| row_mean       | bernoulli   | n/4           |  50 |        3.45   |                14.4  |                8.43 |    6.99 |    9.7  | True       |      0.231    | False       | False            |
| row_mean       | bernoulli   | 2n            |  60 |        3.45   |                 1.72 |                2.4  |    2.31 |    2.52 | True       |     -0.143    | False       | False            |
| row_mean       | bernoulli   | n             |  60 |        3.45   |                 3.45 |                3.48 |    3.35 |    3.57 | True       |     -0.00358  | True        | True             |
| row_mean       | bernoulli   | n/2           |  60 |        3.45   |                 6.9  |                4.87 |    4.76 |    5.02 | True       |      0.151    | False       | False            |
| row_mean       | bernoulli   | n/4           |  60 |        3.45   |                13.8  |                8.19 |    7.9  |    9.33 | True       |      0.226    | False       | False            |
| row_mean       | bernoulli   | 2n            |  75 |        3.45   |                 1.72 |                2.06 |  nan    |  nan    | False      |     -0.0773   | False       | False            |
| row_mean       | bernoulli   | n             |  75 |        3.45   |                 3.45 |                3.63 |    3.51 |    3.74 | True       |     -0.022    | False       | True             |
| row_mean       | bernoulli   | n/2           |  75 |        3.45   |                 6.99 |                5.44 |    5.07 |    5.67 | True       |      0.109    | False       | False            |
| row_mean       | bernoulli   | n/4           |  75 |        3.45   |                14.4  |                8.4  |    7.74 |    9.78 | True       |      0.233    | False       | False            |
| row_mean       | fixed       | 2n            |  50 |        3.43   |                 1.71 |                2.01 |  nan    |  nan    | False      |     -0.0691   | False       | False            |
| row_mean       | fixed       | n             |  50 |        3.43   |                 3.43 |                3.31 |    3.23 |    3.44 | True       |      0.0157   | True        | True             |
| row_mean       | fixed       | n/2           |  50 |        3.43   |                 6.86 |                5.5  |    5    |    6.08 | True       |      0.096    | False       | False            |
| row_mean       | fixed       | n/4           |  50 |        3.43   |                14.3  |                9.17 |    8.5  |    9.65 | True       |      0.192    | False       | False            |
| row_mean       | fixed       | 2n            |  60 |        3.43   |                 1.71 |                2.01 |  nan    |  nan    | False      |     -0.0688   | False       | False            |
| row_mean       | fixed       | n             |  60 |        3.43   |                 3.43 |                3.47 |    3.37 |    3.55 | True       |     -0.00578  | True        | True             |
| row_mean       | fixed       | n/2           |  60 |        3.43   |                 6.86 |                5.64 |    5.13 |    6.08 | True       |      0.0851   | False       | False            |
| row_mean       | fixed       | n/4           |  60 |        3.43   |                13.7  |               10.6  |    9.4  |   11    | True       |      0.111    | False       | False            |
| row_mean       | fixed       | 2n            |  75 |        3.43   |                 1.71 |                2.01 |  nan    |  nan    | False      |     -0.0684   | False       | False            |
| row_mean       | fixed       | n             |  75 |        3.43   |                 3.43 |                3.41 |    3.32 |    3.52 | True       |      0.00228  | True        | True             |
| row_mean       | fixed       | n/2           |  75 |        3.43   |                 6.95 |                5.24 |    5.1  |    5.62 | True       |      0.123    | False       | False            |
| row_mean       | fixed       | n/4           |  75 |        3.43   |                14.3  |                9.59 |    9.4  |   10.3  | True       |      0.173    | False       | False            |
| row_mean       | fixed       | n/8           |  75 |        3.43   |                28.6  |               20.7  |   18.7  |   21.7  | True       |      0.141    | False       | False            |
| tw_min_fill_n  | bernoulli   | 2n            |  50 |        0.353  |                 2.26 |                2.43 |    2.37 |    2.46 | True       |     -0.0321   | False       | False            |
| tw_min_fill_n  | bernoulli   | n             |  50 |        0.353  |                 3.43 |                3.11 |    3.01 |    3.36 | True       |      0.0425   | False       | True             |
| tw_min_fill_n  | bernoulli   | n/2           |  50 |        0.353  |                 5.2  |                5.11 |    4.64 |    5.25 | True       |      0.00742  | True        | False            |
| tw_min_fill_n  | bernoulli   | n/4           |  50 |        0.353  |                 8.73 |                8.43 |    6.99 |    9.7  | True       |      0.0148   | True        | False            |
| tw_min_fill_n  | bernoulli   | 2n            |  60 |        0.353  |                 2.33 |                2.4  |    2.31 |    2.52 | True       |     -0.0127   | True        | False            |
| tw_min_fill_n  | bernoulli   | n             |  60 |        0.353  |                 3.36 |                3.48 |    3.35 |    3.57 | True       |     -0.0146   | True        | True             |
| tw_min_fill_n  | bernoulli   | n/2           |  60 |        0.353  |                 5.22 |                4.87 |    4.76 |    5.02 | True       |      0.0298   | False       | False            |
| tw_min_fill_n  | bernoulli   | n/4           |  60 |        0.353  |                 8.71 |                8.19 |    7.9  |    9.33 | True       |      0.0267   | True        | False            |
| tw_min_fill_n  | bernoulli   | 2n            |  75 |        0.353  |                 2.37 |                2.06 |  nan    |  nan    | False      |      0.0604   | False       | False            |
| tw_min_fill_n  | bernoulli   | n             |  75 |        0.353  |                 3.41 |                3.63 |    3.51 |    3.74 | True       |     -0.0274   | False       | True             |
| tw_min_fill_n  | bernoulli   | n/2           |  75 |        0.353  |                 5.39 |                5.44 |    5.07 |    5.67 | True       |     -0.00407  | True        | False            |
| tw_min_fill_n  | bernoulli   | n/4           |  75 |        0.353  |                 8.98 |                8.4  |    7.74 |    9.78 | True       |      0.0292   | True        | False            |
| tw_min_fill_n  | fixed       | 2n            |  50 |        0.323  |                 2.4  |                2.01 |  nan    |  nan    | False      |      0.0766   | False       | False            |
| tw_min_fill_n  | fixed       | n             |  50 |        0.323  |                 3.4  |                3.31 |    3.23 |    3.44 | True       |      0.0115   | True        | True             |
| tw_min_fill_n  | fixed       | n/2           |  50 |        0.323  |                 5.19 |                5.5  |    5    |    6.08 | True       |     -0.0251   | True        | False            |
| tw_min_fill_n  | fixed       | n/4           |  50 |        0.323  |                 8.55 |                9.17 |    8.5  |    9.65 | True       |     -0.0306   | True        | False            |
| tw_min_fill_n  | fixed       | 2n            |  60 |        0.323  |                 2.42 |                2.01 |  nan    |  nan    | False      |      0.0806   | False       | False            |
| tw_min_fill_n  | fixed       | n             |  60 |        0.323  |                 3.41 |                3.47 |    3.37 |    3.55 | True       |     -0.00876  | True        | True             |
| tw_min_fill_n  | fixed       | n/2           |  60 |        0.323  |                 5.12 |                5.64 |    5.13 |    6.08 | True       |     -0.0417   | False       | False            |
| tw_min_fill_n  | fixed       | n/4           |  60 |        0.323  |                 8.36 |               10.6  |    9.4  |   11    | True       |     -0.104    | False       | False            |
| tw_min_fill_n  | fixed       | 2n            |  75 |        0.323  |                 2.42 |                2.01 |  nan    |  nan    | False      |      0.0808   | False       | False            |
| tw_min_fill_n  | fixed       | n             |  75 |        0.323  |                 3.4  |                3.41 |    3.32 |    3.52 | True       |     -0.00123  | True        | True             |
| tw_min_fill_n  | fixed       | n/2           |  75 |        0.323  |                 5.28 |                5.24 |    5.1  |    5.62 | True       |      0.00351  | True        | False            |
| tw_min_fill_n  | fixed       | n/4           |  75 |        0.323  |                 8.84 |                9.59 |    9.4  |   10.3  | True       |     -0.0351   | False       | False            |
| tw_min_fill_n  | fixed       | n/8           |  75 |        0.323  |                15.1  |               20.7  |   18.7  |   21.7  | True       |     -0.137    | False       | False            |

## Collapse at n in {50, 60, 75} (series = generator x ratio)

| candidate     |   dispersion |    r2 | text                                            |
|:--------------|-------------:|------:|:------------------------------------------------|
| row_mean      |         1.99 | 0.559 | products per customer (row_mean = r · col_mean) |
| excess        |         2.2  | 0.479 | excess (n_ones − m) / n = r (col_mean − 1)      |
| bw_rcm_n      |         2.23 | 0.435 | RCM bandwidth / n                               |
| tw_min_fill_n |         2.23 | 0.45  | min-fill treewidth / n                          |
| opt_frac      |         2.24 | 0.418 | optimum / n                                     |
| g_deg_mean    |         2.25 | 0.382 | MOSP-graph mean degree                          |
| branch        |         2.32 | 0.375 | branching factor (giant component at 1)         |
| col_mean      |         2.37 | 0.415 | customers per product (col_mean)                |

| candidate     |   n |   series |   dispersion |    r2 |   cell_r2 |
|:--------------|----:|---------:|-------------:|------:|----------:|
| excess        |  50 |        8 |         1.52 | 0.519 |     0.939 |
| excess        |  60 |        8 |         1.77 | 0.555 |     0.953 |
| excess        |  75 |        9 |         3.32 | 0.362 |     0.972 |
| g_deg_mean    |  50 |        8 |         1.62 | 0.423 |     0.939 |
| g_deg_mean    |  60 |        8 |         1.79 | 0.469 |     0.953 |
| g_deg_mean    |  75 |        9 |         3.36 | 0.254 |     0.972 |
| col_mean      |  50 |        8 |         1.89 | 0.362 |     0.939 |
| col_mean      |  60 |        8 |         2.37 | 0.375 |     0.953 |
| col_mean      |  75 |        9 |         2.84 | 0.507 |     0.972 |
| row_mean      |  50 |        8 |         1.38 | 0.584 |     0.939 |
| row_mean      |  60 |        8 |         1.75 | 0.572 |     0.953 |
| row_mean      |  75 |        9 |         2.84 | 0.522 |     0.972 |
| opt_frac      |  50 |        8 |         1.5  | 0.493 |     0.939 |
| opt_frac      |  60 |        8 |         1.68 | 0.506 |     0.953 |
| opt_frac      |  75 |        9 |         3.54 | 0.255 |     0.972 |
| tw_min_fill_n |  50 |        8 |         1.46 | 0.518 |     0.939 |
| tw_min_fill_n |  60 |        8 |         1.62 | 0.547 |     0.953 |
| tw_min_fill_n |  75 |        9 |         3.61 | 0.283 |     0.972 |
| bw_rcm_n      |  50 |        8 |         1.49 | 0.487 |     0.939 |
| bw_rcm_n      |  60 |        8 |         1.72 | 0.521 |     0.953 |
| bw_rcm_n      |  75 |        9 |         3.47 | 0.298 |     0.972 |
| branch        |  50 |        8 |         1.61 | 0.429 |     0.939 |
| branch        |  60 |        8 |         1.82 | 0.474 |     0.953 |
| branch        |  75 |        9 |         3.54 | 0.224 |     0.972 |

## The derivation against the measured mean degree (cells at n >= 40)

| generator   | ratio_label   |   cells |   median_rel_err |   max_abs_rel_err |   sparsest_cell_rel_err |
|:------------|:--------------|--------:|-----------------:|------------------:|------------------------:|
| bernoulli   | 2n            |      27 |         0.000134 |            0.656  |                  0.656  |
| bernoulli   | n             |      27 |         0.000607 |            0.385  |                  0.385  |
| bernoulli   | n/2           |      18 |         0.00223  |            0.0462 |                  0.0462 |
| bernoulli   | n/4           |      18 |        -0.031    |            0.0554 |                 -0.044  |
| fixed       | 2n            |      36 |        -0.000662 |            0.0129 |                 -0.0119 |
| fixed       | n             |      38 |        -0.00245  |            0.0528 |                 -0.0528 |
| fixed       | n/2           |      27 |        -0.0117   |            0.153  |                 -0.153  |
| fixed       | n/4           |      27 |        -0.0438   |            0.117  |                 -0.108  |
| fixed       | n/8           |      10 |        -0.0549   |            0.105  |                 -0.105  |

## Thresholds beside the ridge (n >= 50)

| generator   | ratio_label   |   n |   r_exact |   giant_col_mean |   tree_col_mean |   peak_col_mean |   ci_lo |   ci_hi | interior   | peak_is_lower_bound   |   branch_analytic |   excess_analytic |   g_deg_mean |   opt_frac |   ridge_over_giant |
|:------------|:--------------|----:|----------:|-----------------:|----------------:|----------------:|--------:|--------:|:-----------|:----------------------|------------------:|------------------:|-------------:|-----------:|-------------------:|
| bernoulli   | n/4           |  50 |     0.24  |            2.04  |            5.17 |            8.43 |    6.99 |    9.7  | True       | False                 |             17.1  |              1.78 |        15.1  |      0.367 |               4.13 |
| bernoulli   | n/4           |  75 |     0.24  |            2.04  |            5.17 |            8.4  |    7.74 |    9.78 | True       | False                 |             16.9  |              1.78 |        15.3  |      0.313 |               4.11 |
| bernoulli   | n/4           |  60 |     0.25  |            2     |            5    |            8.19 |    7.9  |    9.33 | True       | False                 |             16.8  |              1.8  |        15.1  |      0.342 |               4.1  |
| bernoulli   | n/2           |  75 |     0.493 |            1.42  |            3.03 |            5.44 |    5.07 |    5.67 | True       | False                 |             14.6  |              2.19 |        13.4  |      0.355 |               3.82 |
| bernoulli   | n/2           |  50 |     0.5   |            1.41  |            3    |            5.11 |    4.64 |    5.25 | True       | False                 |             13    |              2.05 |        11.6  |      0.353 |               3.61 |
| bernoulli   | n/2           |  60 |     0.5   |            1.41  |            3    |            4.87 |    4.76 |    5.02 | True       | False                 |             11.9  |              1.94 |        11.1  |      0.331 |               3.44 |
| bernoulli   | n             |  50 |     1     |            1     |            2    |            3.11 |    3.01 |    3.36 | True       | False                 |              9.66 |              2.11 |         8.67 |      0.322 |               3.11 |
| bernoulli   | n             |  60 |     1     |            1     |            2    |            3.48 |    3.35 |    3.57 | True       | False                 |             12.1  |              2.48 |        11    |      0.375 |               3.48 |
| bernoulli   | n             |  75 |     1     |            1     |            2    |            3.63 |    3.51 |    3.74 | True       | False                 |             13.2  |              2.63 |        12    |      0.379 |               3.63 |
| bernoulli   | 2n            |  50 |     2     |            0.707 |            1.5  |            2.43 |    2.37 |    2.46 | True       | False                 |             11.8  |              2.86 |         9.99 |      0.407 |               3.44 |
| bernoulli   | 2n            |  60 |     2     |            0.707 |            1.5  |            2.4  |    2.31 |    2.52 | True       | False                 |             11.5  |              2.8  |        10.4  |      0.374 |               3.39 |
| bernoulli   | 2n            |  75 |     2     |            0.707 |            1.5  |            2.06 |  nan    |  nan    | False      | False                 |              8.49 |              2.12 |         6.96 |      0.267 |               2.91 |
| fixed       | n/8           |  75 |     0.12  |            3.43  |            9.33 |           20.7  |   18.7  |   21.7  | True       | False                 |             48.7  |              2.36 |        37.6  |      0.55  |               6.02 |
| fixed       | n/4           |  50 |     0.24  |            2.6   |            5.17 |            9.17 |    8.5  |    9.65 | True       | False                 |             18    |              1.96 |        15.8  |      0.405 |               3.53 |
| fixed       | n/4           |  75 |     0.24  |            2.6   |            5.17 |            9.59 |    9.4  |   10.3  | True       | False                 |             19.8  |              2.06 |        17.9  |      0.382 |               3.69 |
| fixed       | n/4           |  60 |     0.25  |            2.56  |            5    |           10.6  |    9.4  |   11    | True       | False                 |             25.6  |              2.41 |        21.4  |      0.487 |               4.15 |
| fixed       | n/2           |  75 |     0.493 |            2.01  |            3.03 |            5.24 |    5.1  |    5.62 | True       | False                 |             11    |              2.09 |        10.5  |      0.316 |               2.61 |
| fixed       | n/2           |  50 |     0.5   |            2     |            3    |            5.5  |    5    |    6.08 | True       | False                 |             12.4  |              2.25 |        11.3  |      0.379 |               2.75 |
| fixed       | n/2           |  60 |     0.5   |            2     |            3    |            5.64 |    5.13 |    6.08 | True       | False                 |             13.1  |              2.32 |        12    |      0.375 |               2.82 |
| fixed       | n             |  50 |     1     |            1.62  |            2    |            3.31 |    3.23 |    3.44 | True       | False                 |              7.63 |              2.31 |         7.4  |      0.325 |               2.04 |
| fixed       | n             |  60 |     1     |            1.62  |            2    |            3.47 |    3.37 |    3.55 | True       | False                 |              8.6  |              2.47 |         8.36 |      0.338 |               2.15 |
| fixed       | n             |  75 |     1     |            1.62  |            2    |            3.41 |    3.32 |    3.52 | True       | False                 |              8.22 |              2.41 |         8.17 |      0.306 |               2.11 |
| fixed       | 2n            |  50 |     2     |            1.37  |            1.5  |            2.01 |  nan    |  nan    | False      | False                 |              4.06 |              2.02 |         3.92 |      0.22  |               1.47 |
| fixed       | 2n            |  60 |     2     |            1.37  |            1.5  |            2.01 |  nan    |  nan    | False      | False                 |              4.05 |              2.02 |         3.97 |      0.217 |               1.47 |
| fixed       | 2n            |  75 |     2     |            1.37  |            1.5  |            2.01 |  nan    |  nan    | False      | True                  |              4.04 |              2.01 |         3.97 |      0.2   |               1.47 |

## The ridge's height against m at fixed n

| generator   |   n | ratio_label   |   m |   peak_col_mean |   peak_median_log_nodes | peak_is_lower_bound   |   excess |
|:------------|----:|:--------------|----:|----------------:|------------------------:|:----------------------|---------:|
| bernoulli   |  50 | n/4           |  12 |            8.43 |                    2.53 | False                 |     1.79 |
| bernoulli   |  50 | n/2           |  25 |            5.11 |                    3.63 | False                 |     2.06 |
| bernoulli   |  50 | n             |  50 |            3.11 |                    4.15 | False                 |     2.16 |
| bernoulli   |  50 | 2n            | 100 |            2.43 |                    4.42 | False                 |     2.91 |
| bernoulli   |  60 | n/4           |  15 |            8.19 |                    3.12 | False                 |     1.8  |
| bernoulli   |  60 | n/2           |  30 |            4.87 |                    4.28 | False                 |     1.95 |
| bernoulli   |  60 | n             |  60 |            3.48 |                    4.95 | False                 |     2.53 |
| bernoulli   |  60 | 2n            | 120 |            2.4  |                    5.09 | False                 |     2.97 |
| bernoulli   |  75 | n/4           |  18 |            8.4  |                    3.72 | False                 |     1.78 |
| bernoulli   |  75 | n/2           |  37 |            5.44 |                    5.35 | False                 |     2.21 |
| bernoulli   |  75 | n             |  75 |            3.63 |                    6.2  | False                 |     2.66 |
| bernoulli   |  75 | 2n            | 150 |            2.06 |                    7    | False                 |     2.12 |
| fixed       |  50 | n/4           |  12 |            9.17 |                    2.44 | False                 |     1.96 |
| fixed       |  50 | n/2           |  25 |            5.5  |                    3.59 | False                 |     2.26 |
| fixed       |  50 | n             |  50 |            3.31 |                    4.6  | False                 |     2.33 |
| fixed       |  50 | 2n            | 100 |            2.01 |                    5.08 | False                 |     2.02 |
| fixed       |  60 | n/4           |  15 |           10.6  |                    3.02 | False                 |     2.41 |
| fixed       |  60 | n/2           |  30 |            5.64 |                    4.32 | False                 |     2.33 |
| fixed       |  60 | n             |  60 |            3.47 |                    5.35 | False                 |     2.51 |
| fixed       |  60 | 2n            | 120 |            2.01 |                    6.07 | False                 |     2.02 |
| fixed       |  75 | n/8           |   9 |           20.7  |                    2.14 | False                 |     2.36 |
| fixed       |  75 | n/4           |  18 |            9.59 |                    3.73 | False                 |     2.06 |
| fixed       |  75 | n/2           |  37 |            5.24 |                    5.46 | False                 |     2.1  |
| fixed       |  75 | n             |  75 |            3.41 |                    6.78 | False                 |     2.44 |
| fixed       |  75 | 2n            | 150 |            2.01 |                    8.12 | True                  |     2.01 |

| generator   |   n |   ratios |   slope_log_height_per_log_m |   decades_per_doubling_of_m | any_lower_bound   |
|:------------|----:|---------:|-----------------------------:|----------------------------:|:------------------|
| bernoulli   |  50 |        4 |                         2.02 |                       0.609 | False             |
| bernoulli   |  60 |        4 |                         2.19 |                       0.659 | False             |
| bernoulli   |  75 |        4 |                         3.48 |                       1.05  | False             |
| fixed       |  50 |        4 |                         2.92 |                       0.878 | False             |
| fixed       |  60 |        4 |                         3.39 |                       1.02  | False             |
| fixed       |  75 |        5 |                         4.9  |                       1.48  | True              |

## Instances at 30-40 customers binned by branching factor

| branching_factor   |   instances |   median_log_nodes |   median_nodes |   opt_frac_median |   largest_component_frac |   decomposable_share |   excess_median |
|:-------------------|------------:|-------------------:|---------------:|------------------:|-------------------------:|---------------------:|----------------:|
| [1.0, 2.0)         |          24 |              1.3   |             19 |             0.1   |                    0.133 |              1       |           0.4   |
| [2.0, 4.0)         |        1409 |              1.86  |             72 |             0.125 |                    0.525 |              0.877   |           0.725 |
| [4.0, 8.0)         |        1811 |              2.95  |            898 |             0.257 |                    1     |              0.42    |           1.95  |
| [8.0, 16.0)        |        1922 |              2.98  |            961 |             0.457 |                    1     |              0.132   |           3     |
| [16.0, 32.0)       |        2278 |              2.36  |            226 |             0.65  |                    1     |              0.00439 |           4.59  |
| [32.0, inf)        |        8756 |              0.778 |              5 |             0.914 |                    1     |              0       |          10.9   |
