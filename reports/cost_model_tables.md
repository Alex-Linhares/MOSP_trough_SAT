# Cost model tables (§19)

*Generated 2026-09-26 15:25 by `python -m learning.cost_model`. Every log is log10(1 + nodes); a censored count is a lower bound.*

## Rows on record by source and band

| source   | band   |   rows |   default |   csearch |
|:---------|:-------|-------:|----------:|----------:|
| campaign | 10-20  |  16200 |     16200 |     16200 |
| campaign | 21-40  |  21600 |     21600 |     21600 |
| corpus   | 10-20  |   4122 |      4122 |      4122 |
| corpus   | 100    |     62 |        50 |        50 |
| corpus   | 125    |     26 |        15 |        20 |
| corpus   | 21-40  |   2013 |      2013 |      2013 |
| corpus   | 50-60  |    121 |        50 |        50 |
| corpus   | 75     |     32 |        25 |        25 |
| upward   | 100    |     35 |        33 |        33 |
| upward   | 50-60  |   4500 |      4500 |      4500 |
| upward   | 75     |   2250 |      2247 |      2247 |

## Noise floor: sd of log10(1 + nodes) over relabellings of one instance (refutation, settled)

| study              | config   | band   |   instances |   labellings |   sd_median |   sd_p90 |   sd_median_hard(≥1e4 nodes) |
|:-------------------|:---------|:-------|------------:|-------------:|------------:|---------:|-----------------------------:|
| differential (§15) | csearch  | 10-20  |       20316 |           10 |       0.000 |    0.035 |                      nan     |
| differential (§15) | csearch  | 21-40  |       23613 |           10 |       0.000 |    0.035 |                        0.016 |
| portfolio (§18)    | csearch  | 21-40  |         288 |           17 |       0.000 |    0.017 |                        0.017 |
| portfolio (§18)    | csearch  | 50-60  |         841 |           17 |       0.003 |    0.017 |                        0.006 |
| portfolio (§18)    | csearch  | 75     |         391 |           17 |       0.001 |    0.017 |                        0.004 |
| portfolio (§18)    | csearch  | 100    |          51 |           17 |       0.002 |    0.024 |                        0.003 |
| differential (§15) | default  | 10-20  |       20316 |           10 |       0.000 |    0.006 |                      nan     |
| differential (§15) | default  | 21-40  |       23613 |           10 |       0.000 |    0.013 |                        0.009 |

## Dating the upward run's csearch counts (post-fix identity counts of §18 against the run)

| verdict              |   cells |
|:---------------------|--------:|
| differs: pre-fix     |      70 |
| rule off: pre = post |      65 |


# Configuration `default`

## Model selection: fit n ≤ 60, score at 75 (test sizes untouched)

| variant                            | fit_n   |   test_n |   counts |   censored |   MAE |    bias |   RMSE |   within_decade |   seconds |
|:-----------------------------------|:--------|---------:|---------:|-----------:|------:|--------:|-------:|----------------:|----------:|
| linear + drift + gbm [row]         | ≤60     |       75 |     2272 |          8 | 0.189 |  0.0543 |  0.271 |           0.991 |       0.6 |
| linear + drift + gbm [per_n, n≥20] | ≤60     |       75 |     2272 |          8 | 0.231 |  0.108  |  0.313 |           0.986 |       0.2 |
| linear + drift [per_n]             | ≤60     |       75 |     2272 |          8 | 0.271 | -0.085  |  0.406 |           0.951 |       0   |
| linear + drift [row]               | ≤60     |       75 |     2272 |          8 | 0.272 |  0.0531 |  0.408 |           0.944 |       0   |
| linear + drift [row, n≥20]         | ≤60     |       75 |     2272 |          8 | 0.274 |  0.0907 |  0.397 |           0.955 |       0   |
| linear, no drift [row]             | ≤60     |       75 |     2272 |          8 | 0.288 | -0.142  |  0.426 |           0.946 |       0   |
| linear + drift [per_n, n≥20]       | ≤60     |       75 |     2272 |          8 | 0.302 |  0.107  |  0.437 |           0.944 |       0   |

## Error at the test sizes (fit n ≤ 75)

### chosen: linear + drift + gbm [row]

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       83 |        72 |         11 | 0.535 |  0.431 |  0.674 |     1.07  |           0.855 |               0.636 |
|    125 |       15 |        15 |          0 | 0.382 |  0.377 |  0.455 |     0.593 |           1     |             nan     |

### linear: linear + drift [per_n]

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       83 |        72 |         11 | 0.884 |  0.583 |   1.15 |     2     |           0.687 |                   1 |
|    125 |       15 |        15 |          0 | 0.261 | -0.068 |   0.34 |     0.562 |           1     |                 nan |

### §11 cell law (fit 15-40, interpolated in col_mean)

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       58 |        47 |         11 | 0.858 |  0.818 |  0.942 |      1.31 |           0.655 |                   1 |
|    125 |       15 |        15 |          0 | 1.29  |  1.29  |  1.34  |      1.72 |           0.267 |                 nan |

### §14 surface (fit n ≤ 30)

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       83 |        72 |         11 | 0.829 |  0.626 |   1.07 |      1.85 |           0.663 |               0.636 |
|    125 |       15 |        15 |          0 | 1.43  |  1.32  |   1.68 |      2.42 |           0.333 |             nan     |

### The decade claim at 100–125 (kill: < 80% within one decade)

| predictor                                          |   counts |   censored |   within_decade |   within_decade_settled | kill_met   |
|:---------------------------------------------------|---------:|-----------:|----------------:|------------------------:|:-----------|
| chosen: linear + drift + gbm [row]                 |       98 |         11 |           0.878 |                   0.874 | False      |
| linear: linear + drift [per_n]                     |       98 |         11 |           0.735 |                   0.713 | True       |
| §11 cell law (fit 15-40, interpolated in col_mean) |       73 |         11 |           0.575 |                   0.532 | True       |
| §14 surface (fit n ≤ 30)                           |       98 |         11 |           0.612 |                   0.598 | True       |

### Chosen model by class at 100 and 125

| class              |   n |   counts |   censored |   median_y |   median_pred |      bias |   within_decade |
|:-------------------|----:|---------:|-----------:|-----------:|--------------:|----------:|----------------:|
| Random-100-100-10  | 100 |        5 |          0 |       3.87 |          3.78 |  -0.179   |            1    |
| Random-100-100-2   | 100 |        5 |          4 |       9.56 |          9.43 |  -0.00516 |            0.8  |
| Random-100-100-4   | 100 |        5 |          0 |       8.71 |          8.68 |  -0.0924  |            1    |
| Random-100-100-6   | 100 |        5 |          0 |       6.55 |          6.96 |   0.329   |            1    |
| Random-100-100-8   | 100 |        5 |          0 |       5.18 |          5.15 |   0.0151  |            1    |
| Random-100-50-10   | 100 |        5 |          0 |       5.35 |          5.62 |   0.262   |            1    |
| Random-100-50-2    | 100 |        5 |          0 |       5.8  |          6.22 |   0.456   |            1    |
| Random-100-50-4    | 100 |        5 |          0 |       7.82 |          7.66 |  -0.175   |            1    |
| Random-100-50-6    | 100 |        5 |          0 |       6.66 |          7.22 |   0.36    |            1    |
| Random-100-50-8    | 100 |        5 |          0 |       6.2  |          6.75 |   0.486   |            1    |
| Random-125-125-10  | 125 |        5 |          0 |       4.94 |          5.1  |   0.121   |            1    |
| Random-125-125-6   | 125 |        5 |          0 |       8.6  |          9.2  |   0.619   |            1    |
| Random-125-125-8   | 125 |        5 |          0 |       6.45 |          6.89 |   0.391   |            1    |
| ens_f_n100_m100_d2 | 100 |       25 |          0 |       5.45 |          6.47 |   0.947   |            0.56 |
| ens_f_n100_m100_d3 | 100 |        3 |          3 |       9.49 |          9.35 | nan       |            1    |
| ens_f_n100_m100_d4 | 100 |        5 |          4 |       9.35 |          9.33 |   0.0366  |            1    |

## In-range error at n ≤ 75, 5-fold grouped by file ∪ class (chosen model)

| band   |   counts |   settled |   censored |    MAE |     bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|:-------|---------:|----------:|-----------:|-------:|---------:|-------:|----------:|----------------:|--------------------:|
| 10-20  |    20312 |     20312 |          0 | 0.0859 |  0.0174  |  0.116 |     0.187 |           1     |                 nan |
| 21-40  |    23613 |     23613 |          0 | 0.0864 | -0.0056  |  0.119 |     0.192 |           1     |                 nan |
| 50-60  |     4550 |      4550 |          0 | 0.137  |  0.00789 |  0.204 |     0.282 |           0.995 |                 nan |
| 75     |     2272 |      2264 |          8 | 0.205  |  0.00416 |  0.333 |     0.46  |           0.965 |                   1 |

## Linear Tobit coefficients (linear + drift [per_n]; σ = 0.164, 8 censored training rows)

| term         |      coef |
|:-------------|----------:|
| 1            |  0.3746   |
| n            |  0.06245  |
| x            |  3.336    |
| x2           | -2.182    |
| n·x          | -0.09909  |
| n·x2         |  0.05411  |
| opt_frac     | -0.5537   |
| opt_frac2    |  3.237    |
| n·opt_frac   |  0.4724   |
| n·opt_frac2  | -0.295    |
| log_deg      | -1.643    |
| n·log_deg    | -0.09358  |
| deg_cv       |  2.225    |
| n·deg_cv     | -0.002312 |
| lcc          | -1.201    |
| n·lcc        |  0.04015  |
| log_comp     | -1.241    |
| log_ratio    | -0.1323   |
| log_ratio2   | -0.05079  |
| n·log_ratio  |  0.001852 |
| tw_frac      |  0.8763   |
| n·tw_frac    | -0.1      |
| degen_frac   | -3.299    |
| n·degen_frac |  0.05761  |
| clust        | -0.4106   |
| n·clust      |  0.01519  |
| n2           |  0.03022  |
| n2·x         | -0.009238 |


# Configuration `csearch` (pre-fix counts only)

## Model selection: fit n ≤ 60, score at 75 (test sizes untouched)

| variant                            | fit_n   |   test_n |   counts |   censored |   MAE |    bias |   RMSE |   within_decade |   seconds |
|:-----------------------------------|:--------|---------:|---------:|-----------:|------:|--------:|-------:|----------------:|----------:|
| linear + drift + gbm [row]         | ≤60     |       75 |     2272 |          7 | 0.182 |  0.0681 |  0.258 |           0.995 |       0.2 |
| linear + drift + gbm [per_n, n≥20] | ≤60     |       75 |     2272 |          7 | 0.243 |  0.145  |  0.322 |           0.991 |       0.2 |
| linear + drift [row]               | ≤60     |       75 |     2272 |          7 | 0.267 |  0.0684 |  0.387 |           0.961 |       0   |
| linear + drift [per_n]             | ≤60     |       75 |     2272 |          7 | 0.267 | -0.0751 |  0.382 |           0.966 |       0   |
| linear + drift [row, n≥20]         | ≤60     |       75 |     2272 |          7 | 0.272 |  0.115  |  0.386 |           0.962 |       0   |
| linear, no drift [row]             | ≤60     |       75 |     2272 |          7 | 0.28  | -0.118  |  0.402 |           0.956 |       0   |
| linear + drift [per_n, n≥20]       | ≤60     |       75 |     2272 |          7 | 0.312 |  0.142  |  0.438 |           0.948 |       0   |

## Error at the test sizes (fit n ≤ 75)

### chosen: linear + drift + gbm [row]

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       83 |        73 |         10 | 0.532 |  0.482 |  0.675 |     1.12  |           0.867 |                 0.7 |
|    125 |       20 |        20 |          0 | 0.375 |  0.371 |  0.441 |     0.601 |           1     |               nan   |

### linear: linear + drift [row]

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       83 |        73 |         10 | 0.918 |  0.831 |  1.22  |     2.21  |           0.687 |                 0.9 |
|    125 |       20 |        20 |          0 | 0.423 |  0.358 |  0.511 |     0.714 |           0.95  |               nan   |

### §11 cell law (fit 15-40, interpolated in col_mean)

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       58 |        48 |         10 | 0.794 |  0.763 |  0.884 |      1.2  |           0.724 |                 0.8 |
|    125 |       20 |        20 |          0 | 1.1   |  0.944 |  1.2   |      1.72 |           0.45  |               nan   |

### §14 surface (fit n ≤ 30)

|   band |   counts |   settled |   censored |   MAE |   bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|-------:|---------:|----------:|-----------:|------:|-------:|-------:|----------:|----------------:|--------------------:|
|    100 |       83 |        73 |         10 | 0.817 |  0.544 |   1.04 |      1.77 |           0.663 |                 0.6 |
|    125 |       20 |        20 |          0 | 1.42  |  0.961 |   1.62 |      2.28 |           0.3   |               nan   |

### The decade claim at 100–125 (kill: < 80% within one decade)

| predictor                                          |   counts |   censored |   within_decade |   within_decade_settled | kill_met   |
|:---------------------------------------------------|---------:|-----------:|----------------:|------------------------:|:-----------|
| chosen: linear + drift + gbm [row]                 |      103 |         10 |           0.893 |                   0.882 | False      |
| linear: linear + drift [row]                       |      103 |         10 |           0.738 |                   0.71  | True       |
| §11 cell law (fit 15-40, interpolated in col_mean) |       78 |         10 |           0.654 |                   0.618 | True       |
| §14 surface (fit n ≤ 30)                           |      103 |         10 |           0.592 |                   0.581 | True       |

### Chosen model by class at 100 and 125

| class              |   n |   counts |   censored |   median_y |   median_pred |      bias |   within_decade |
|:-------------------|----:|---------:|-----------:|-----------:|--------------:|----------:|----------------:|
| Random-100-100-10  | 100 |        5 |          0 |       3.87 |          3.77 |  -0.179   |            1    |
| Random-100-100-2   | 100 |        5 |          3 |       9.31 |          8.98 |   0.284   |            1    |
| Random-100-100-4   | 100 |        5 |          0 |       8.55 |          8.63 |   0.0583  |            1    |
| Random-100-100-6   | 100 |        5 |          0 |       6.55 |          6.95 |   0.322   |            1    |
| Random-100-100-8   | 100 |        5 |          0 |       5.18 |          5.13 |   0.00529 |            1    |
| Random-100-50-10   | 100 |        5 |          0 |       5.35 |          5.6  |   0.263   |            1    |
| Random-100-50-2    | 100 |        5 |          0 |       5.42 |          5.77 |   0.423   |            1    |
| Random-100-50-4    | 100 |        5 |          0 |       7.05 |          7.4  |   0.273   |            1    |
| Random-100-50-6    | 100 |        5 |          0 |       6.62 |          7.17 |   0.48    |            1    |
| Random-100-50-8    | 100 |        5 |          0 |       6.16 |          6.68 |   0.475   |            1    |
| Random-125-125-10  | 125 |        5 |          0 |       4.94 |          5.1  |   0.12    |            1    |
| Random-125-125-2   | 125 |        2 |          0 |      11.2  |         11.4  |   0.159   |            1    |
| Random-125-125-4   | 125 |        3 |          0 |      10.8  |         11.4  |   0.527   |            1    |
| Random-125-125-6   | 125 |        5 |          0 |       8.6  |          9.17 |   0.573   |            1    |
| Random-125-125-8   | 125 |        5 |          0 |       6.45 |          6.92 |   0.41    |            1    |
| ens_f_n100_m100_d2 | 100 |       25 |          0 |       5.28 |          6.23 |   0.959   |            0.56 |
| ens_f_n100_m100_d3 | 100 |        3 |          3 |       9.19 |          9.08 | nan       |            1    |
| ens_f_n100_m100_d4 | 100 |        5 |          4 |       9.13 |          9.22 |   0.0538  |            1    |

## In-range error at n ≤ 75, 5-fold grouped by file ∪ class (chosen model)

| band   |   counts |   settled |   censored |    MAE |     bias |   RMSE |   p90_abs |   within_decade |   under_lower_bound |
|:-------|---------:|----------:|-----------:|-------:|---------:|-------:|----------:|----------------:|--------------------:|
| 10-20  |    20312 |     20312 |          0 | 0.0838 |  0.011   |  0.114 |     0.187 |           1     |                 nan |
| 21-40  |    23613 |     23613 |          0 | 0.0864 | -0.00429 |  0.12  |     0.193 |           1     |                 nan |
| 50-60  |     4550 |      4550 |          0 | 0.137  |  0.00215 |  0.2   |     0.281 |           0.995 |                 nan |
| 75     |     2272 |      2265 |          7 | 0.191  |  0.00386 |  0.299 |     0.416 |           0.977 |                   1 |

## Linear Tobit coefficients (linear + drift [row]; σ = 0.179, 7 censored training rows)

| term         |       coef |
|:-------------|-----------:|
| 1            |  0.2526    |
| n            |  0.0557    |
| x            |  0.8977    |
| x2           | -0.3401    |
| n·x          | -0.07641   |
| n·x2         |  0.02252   |
| opt_frac     |  1.138     |
| opt_frac2    |  1.76      |
| n·opt_frac   |  0.3831    |
| n·opt_frac2  | -0.2585    |
| log_deg      | -1.259     |
| n·log_deg    | -0.0732    |
| deg_cv       |  1.53      |
| n·deg_cv     |  0.0004099 |
| lcc          | -0.7507    |
| n·lcc        |  0.03969   |
| log_comp     | -1.053     |
| log_ratio    | -0.003458  |
| log_ratio2   | -0.1673    |
| n·log_ratio  | -0.005983  |
| tw_frac      |  0.07371   |
| n·tw_frac    | -0.06087   |
| degen_frac   | -2.963     |
| n·degen_frac |  0.05531   |
| clust        |  0.01251   |
| n·clust      |  0.001075  |
| n2           |  0.02547   |
| n2·x         | -0.0008437 |

## The recertify entries: predicted against spent (the csearch counts are pre-fix; hours at 0.55 µs/node; `default` columns are the other configuration's model, an upper reference)

| instance             |   value |   col_mean |   pred_csearch |   pred_hours_csearch |   pred_csearch_linear |   pred_hours_csearch_linear |   pred_default |   pred_hours_default |   pred_default_linear |   pred_hours_default_linear |   pred_§11 cell law (fit 15-40, interpolated in col_mean) |   pred_§14 surface (fit n ≤ 30) |   actual_log10_nodes |   actual_hours | status   |   running_hours |   log10_nodes_at_least |   cheapest_first_rank |
|:---------------------|--------:|-----------:|---------------:|---------------------:|----------------------:|----------------------------:|---------------:|---------------------:|----------------------:|----------------------------:|----------------------------------------------------------:|--------------------------------:|---------------------:|---------------:|:---------|----------------:|-----------------------:|----------------------:|
| Random-125-125-2-5_0 |      20 |       2.66 |           11.1 |                 21.5 |                  10.9 |                        11.4 |           11.7 |                 72.3 |                  11   |                        14.2 |                                                      10.1 |                            8.83 |                nan   |          nan   | open     |            63.3 |                   11.5 |                     1 |
| Random-125-125-2-4_0 |      24 |       2.78 |           11.3 |                 28.8 |                  10.8 |                        10.1 |           11.7 |                 81.6 |                  10.9 |                        10.9 |                                                      10.6 |                            9.14 |                 11.2 |           28.3 | unsat    |           nan   |                  nan   |                     2 |
| Random-125-125-4-5_0 |      46 |       3.94 |           11.3 |                 30.5 |                  11   |                        14.4 |           11.5 |                 45.2 |                  10.8 |                         9.6 |                                                      11.4 |                           11.7  |                 10.7 |           10.2 | unsat    |           nan   |                  nan   |                     3 |
| Random-125-125-2-3_0 |      21 |       2.66 |           11.3 |                 33.4 |                  11   |                        14.9 |           11.8 |                103   |                  11.1 |                        17.9 |                                                      10.1 |                            8.96 |                nan   |          nan   | open     |            63.3 |                   11.5 |                     4 |
| Random-125-125-4-2_0 |      57 |       4.29 |           11.4 |                 37   |                  11.1 |                        19   |           11.5 |                 46.7 |                  10.8 |                         9.3 |                                                      11.2 |                           12.4  |                 10.8 |           13.3 | unsat    |           nan   |                  nan   |                     5 |
| Random-125-125-2-1_0 |      24 |       2.73 |           11.5 |                 46.1 |                  11   |                        16.8 |           11.9 |                134   |                  11.1 |                        18.4 |                                                      10.4 |                            9.43 |                 11.2 |           25   | unsat    |           nan   |                  nan   |                     6 |
| Random-125-125-4-4_0 |      51 |       4.09 |           11.8 |                 92.8 |                  11.5 |                        44.4 |           11.9 |                128   |                  11.4 |                        34.7 |                                                      11.4 |                           12.4  |                 11.4 |           53.5 | unsat    |           nan   |                  nan   |                     7 |
| Random-125-125-2-2_0 |      25 |       2.77 |           11.8 |                107   |                  11.4 |                        35   |           12.4 |                374   |                  11.5 |                        50.3 |                                                      10.5 |                            9.88 |                nan   |          nan   | open     |            63.3 |                   11.5 |                     8 |

### Rank agreement on the finished entries

| predictor                                          |   finished |   spearman |   MAE |    bias |   within_decade |
|:---------------------------------------------------|-----------:|-----------:|------:|--------:|----------------:|
| csearch                                            |          5 |        0.4 | 0.38  |  0.38   |             1   |
| csearch_linear                                     |          5 |        0.3 | 0.244 |  0.0142 |             1   |
| default                                            |          5 |        0.7 | 0.645 |  0.645  |             1   |
| default_linear                                     |          5 |        0.8 | 0.134 | -0.0898 |             1   |
| §11 cell law (fit 15-40, interpolated in col_mean) |          5 |       -0.3 | 0.547 | -0.0775 |             1   |
| §14 surface (fit n ≤ 30)                           |          5 |       -0.2 | 1.51  | -0.0362 |             0.2 |

## Post-fix csearch counts at 99–100 against the pre-fix model (labelled; not the test set)

| study              | class                                                  |   instances |   censored |   median_pred |   median_postfix |   median_prefix |   within_decade |
|:-------------------|:-------------------------------------------------------|------------:|-----------:|--------------:|-----------------:|----------------:|----------------:|
| portfolio identity | GP5:  100 customers,  100 products,  high path width   |           1 |          0 |         0.824 |            0.301 |          nan    |               1 |
| portfolio identity | GP5_0                                                  |           1 |          0 |         0.824 |            0.301 |          nan    |               1 |
| portfolio identity | GP6:  100 customers,  100 products,  medium path width |           1 |          0 |         2.44  |            0     |          nan    |               0 |
| portfolio identity | GP6_0                                                  |           1 |          0 |         2.44  |            0     |          nan    |               0 |
| portfolio identity | GP7:  100 customers,  100 products,  medium path width |           1 |          0 |         2.45  |            0.301 |          nan    |               0 |
| portfolio identity | GP7_0                                                  |           1 |          0 |         2.45  |            0.301 |          nan    |               0 |
| portfolio identity | GP8:  100 customers,  100 products,  low path width    |           1 |          0 |         2.46  |            0.602 |          nan    |               0 |
| portfolio identity | GP8_0                                                  |           1 |          0 |         2.46  |            0.602 |          nan    |               0 |
| portfolio identity | Random-100-100-10                                      |           5 |          0 |         3.77  |            3.87  |            3.87 |               1 |
| portfolio identity | Random-100-100-6                                       |           5 |          0 |         6.95  |            6.55  |            6.55 |               1 |
| portfolio identity | Random-100-100-8                                       |           5 |          0 |         5.13  |            5.18  |            5.18 |               1 |
| portfolio identity | Random-100-50-10                                       |           5 |          0 |         5.6   |            5.35  |            5.35 |               1 |
| portfolio identity | Random-100-50-2                                        |           5 |          0 |         5.77  |            5.78  |            5.42 |               1 |
| portfolio identity | Random-100-50-4                                        |           5 |          0 |         7.4   |            7.59  |            7.05 |               1 |
| portfolio identity | Random-100-50-6                                        |           5 |          0 |         7.17  |            6.64  |            6.62 |               1 |
| portfolio identity | Random-100-50-8                                        |           5 |          0 |         6.68  |            6.18  |            6.16 |               1 |
| portfolio identity | SP4                                                    |           1 |          0 |         7.96  |            7.7   |          nan    |               1 |
| portfolio identity | SP4_0                                                  |           1 |          0 |         7.96  |            7.7   |          nan    |               1 |
| portfolio identity | scoop-A_FA+AA                                          |           1 |          0 |         4.15  |            4.1   |          nan    |               1 |
| race identity      | Random-100-100-2                                       |           4 |          4 |         9.07  |            9.05  |            9.37 |               1 |


*11 s.*
