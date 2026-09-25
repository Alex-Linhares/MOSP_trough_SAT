6376 instances, 617 files; n_customers 9-134, 5938 at n <= 30; pools: structure (38), structure + treewidth heuristics (40); splits: grouped by file, grouped by file ∪ class, random (leaks!); boosting: LightGBM

## The searches: best monomial, best pair, boosting on the same pool

`mae`/`exact` are pooled held-out errors of the two-parameter fit `y ≈ a·t + b` under the split, constants by least absolute deviation; the term itself was selected by that error, so these are optimistic (see the nested table).

| target            | pool                             | split                   |   terms | best monomial                     |   mae |   exact |   best pair mae |   pair exact |   boosting mae |   boosting exact |   seconds |
|:------------------|:---------------------------------|:------------------------|--------:|:----------------------------------|------:|--------:|----------------:|-------------:|---------------:|-----------------:|----------:|
| optimum           | structure                        | grouped by file         |   58221 | sqrt(g_degeneracy) · sqrt(bw_rcm) | 0.672 |   0.671 |           0.576 |        0.667 |          0.390 |            0.738 |    16.657 |
| optimum           | structure                        | grouped by file ∪ class |   58221 | sqrt(g_degeneracy) · sqrt(bw_rcm) | 0.672 |   0.671 |           0.599 |        0.659 |          1.588 |            0.355 |    10.243 |
| optimum           | structure                        | random (leaks!)         |   58221 | sqrt(g_degeneracy) · sqrt(bw_rcm) | 0.672 |   0.671 |           0.574 |        0.667 |          0.317 |            0.793 |    12.368 |
| optimum           | structure + treewidth heuristics | grouped by file         |   68690 | tw_min_fill                       | 0.188 |   0.857 |           0.187 |        0.860 |          0.221 |            0.872 |    16.942 |
| optimum           | structure + treewidth heuristics | grouped by file ∪ class |   68690 | tw_min_fill                       | 0.189 |   0.857 |           0.209 |        0.857 |          1.022 |            0.760 |    16.902 |
| optimum           | structure + treewidth heuristics | random (leaks!)         |   68690 | tw_min_fill                       | 0.188 |   0.857 |           0.186 |        0.860 |          0.200 |            0.877 |    15.539 |
| optimum − lb_best | structure                        | grouped by file         |   58221 | g_deg_std · sep_size / g_density  | 0.303 |   0.802 |           0.295 |        0.804 |          0.260 |            0.814 |     9.147 |
| optimum − lb_best | structure                        | grouped by file ∪ class |   58221 | g_deg_std · sep_size / g_density  | 0.302 |   0.803 |           0.307 |        0.801 |          0.428 |            0.795 |     9.279 |
| optimum − lb_best | structure                        | random (leaks!)         |   58221 | g_deg_std · sep_size / g_density  | 0.302 |   0.803 |           0.296 |        0.804 |          0.242 |            0.823 |    11.231 |

## Leading monomials — target `optimum`, pool `structure`, grouped by file

`mae`/`exact`: LAD constants; `mae_ols`/`exact_ols`: the least-squares first pass.

| formula                                    |   degree |    mae |   exact |   mae_ols |   exact_ols | fit on all rows (LAD)   |
|:-------------------------------------------|---------:|-------:|--------:|----------:|------------:|:------------------------|
| sqrt(g_degeneracy) · sqrt(bw_rcm)          |        2 | 0.6721 |  0.6711 |    1.0313 |      0.4258 | +1 · t +1               |
| sqrt(g_density) · bw_rcm                   |        2 | 0.7116 |  0.6300 |    0.9332 |      0.4580 | +0.9957 · t +1.12       |
| bw_rcm · sqrt(rig_edge_prob)               |        2 | 0.7184 |  0.6267 |    0.9150 |      0.4613 | +0.9952 · t +1.16       |
| bw_rcm · spectral_radius / g_deg_max       |        3 | 0.8139 |  0.6012 |    1.0059 |      0.4082 | +0.9957 · t +1.17       |
| sqrt(g_deg_mean) · sqrt(bw_rcm)            |        2 | 0.8176 |  0.6015 |    0.9449 |      0.3215 | +0.9952 · t +0.645      |
| sqrt(g_degeneracy) · sqrt(sep_size)        |        2 | 0.8395 |  0.5049 |    0.9613 |      0.4023 | +1.796 · t -0.774       |
| sqrt(bw_rcm) · sqrt(rig_deg_expected)      |        2 | 0.9480 |  0.4514 |    1.0283 |      0.3105 | +1.003 · t +0.506       |
| g_deg_mean · bw_rcm / g_deg_max            |        3 | 0.9684 |  0.5941 |    1.2293 |      0.3145 | +0.9847 · t +1.49       |
| sqrt(bw_rcm) · sqrt(spectral_radius)       |        2 | 0.9732 |  0.3656 |    1.0608 |      0.2836 | +0.9951 · t +0.519      |
| bw_rcm² / n_customers                      |        2 | 0.9832 |  0.4933 |    1.0172 |      0.3747 | +0.9825 · t +2.43       |
| sqrt(g_clustering) · bw_rcm                |        2 | 0.9894 |  0.6087 |    1.1878 |      0.2462 | +0.9999 · t +1          |
| g_deg_max · bw_rcm / n_customers           |        3 | 1.0524 |  0.5527 |    1.1110 |      0.5394 | +0.9979 · t +1.89       |
| sqrt(g_degeneracy) · sqrt(g_deg_max)       |        2 | 1.0648 |  0.5881 |    1.3005 |      0.3446 | +1.013 · t +0.492       |
| sqrt(n_customers) · sqrt(g_degeneracy)     |        2 | 1.0899 |  0.4335 |    1.2780 |      0.2914 | +1.028 · t -0.499       |
| g_degeneracy · g_deg_max / spectral_radius |        3 | 1.0919 |  0.5596 |    1.3651 |      0.3082 | +1.003 · t +0.914       |

### Leading pairs — target `optimum`, pool `structure`

| formula                                                                                                        |    mae |   exact |   mae_ols |
|:---------------------------------------------------------------------------------------------------------------|-------:|--------:|----------:|
| +0.5317 · [bw_rcm² / n_customers] +0.4696 · [sqrt(g_deg_mean) · sqrt(spectral_radius)] +1.479                  | 0.5758 |  0.6666 |    0.6564 |
| +0.5349 · [bw_rcm² / n_customers] +0.4668 · [sqrt(distinct_row_frac) · spectral_radius] +1.475                 | 0.5777 |  0.6586 |    0.6537 |
| +0.5416 · [bw_rcm² / n_customers] +0.4596 · [sqrt(g_components) · g_deg_mean] +1.489                           | 0.5795 |  0.6647 |    0.6583 |
| +0.5416 · [bw_rcm² / n_customers] +0.9193 · [g_edges / (n_customers · g_largest_comp_frac)] +1.49              | 0.5821 |  0.6611 |    0.6596 |
| +0.5416 · [bw_rcm² / n_customers] +0.4596 · [rig_deg_expected · rig_density_ratio / g_largest_comp_frac] +1.49 | 0.5821 |  0.6611 |    0.6596 |
| +0.5416 · [bw_rcm² / n_customers] +0.4596 · [g_deg_mean / g_largest_comp_frac] +1.49                           | 0.5821 |  0.6611 |    0.6596 |
| +0.5411 · [bw_rcm² / n_customers] +0.4601 · [g_deg_mean / sqrt(g_largest_comp_frac)] +1.49                     | 0.5831 |  0.6592 |    0.6622 |
| +0.549 · [bw_rcm² / n_customers] +0.4523 · [sqrt(spectral_radius) · sqrt(rig_deg_expected)] +1.503             | 0.5839 |  0.6664 |    0.6609 |

## Leading monomials — target `optimum`, pool `structure + treewidth heuristics`, grouped by file

`mae`/`exact`: LAD constants; `mae_ols`/`exact_ols`: the least-squares first pass.

| formula                                            |   degree |    mae |   exact |   mae_ols |   exact_ols | fit on all rows (LAD)   |
|:---------------------------------------------------|---------:|-------:|--------:|----------:|------------:|:------------------------|
| tw_min_fill                                        |        1 | 0.1885 |  0.8574 |    0.3267 |      0.8428 | +1 · t +1               |
| tw_min_fill / sqrt(g_largest_comp_frac)            |        2 | 0.1955 |  0.8537 |    0.3275 |      0.8331 | +1 · t +1               |
| sqrt(g_largest_comp_frac) · tw_min_fill            |        2 | 0.1973 |  0.8538 |    0.3330 |      0.8411 | +1 · t +1               |
| g_largest_comp_frac · tw_min_fill                  |        2 | 0.2046 |  0.8483 |    0.3428 |      0.8392 | +1 · t +1               |
| tw_min_fill / g_largest_comp_frac                  |        2 | 0.2070 |  0.8474 |    0.3360 |      0.8294 | +1 · t +1               |
| g_largest_comp_frac² · tw_min_fill                 |        2 | 0.2160 |  0.8422 |    0.3608 |      0.8336 | +1 · t +1               |
| tw_min_fill / sqrt(distinct_col_frac)              |        2 | 0.2171 |  0.8469 |    0.3425 |      0.8116 | +1 · t +1               |
| sqrt(distinct_col_frac) · tw_min_fill              |        2 | 0.2173 |  0.8488 |    0.3303 |      0.8419 | +1 · t +1               |
| tw_min_fill / sqrt(g_components)                   |        2 | 0.2190 |  0.8391 |    0.3649 |      0.8347 | +1 · t +1               |
| sqrt(g_components) · tw_min_fill                   |        2 | 0.2262 |  0.8405 |    0.3482 |      0.8254 | +1 · t +1               |
| tw_min_fill / (g_components · g_largest_comp_frac) |        3 | 0.2291 |  0.8400 |    0.3827 |      0.8311 | +1 · t +1               |
| sqrt(tw_min_fill) · sqrt(tw_min_degree)            |        2 | 0.2375 |  0.8505 |    0.3760 |      0.7376 | +1 · t +1               |
| tw_min_fill / g_components                         |        2 | 0.2384 |  0.8391 |    0.3989 |      0.8071 | +1 · t +1               |
| distinct_col_frac · tw_min_fill                    |        2 | 0.2445 |  0.8199 |    0.3569 |      0.8247 | +1 · t +1               |
| g_largest_comp_frac · tw_min_fill / g_components   |        3 | 0.2447 |  0.8389 |    0.4103 |      0.8041 | +1 · t +1               |

### Leading pairs — target `optimum`, pool `structure + treewidth heuristics`

| formula                                                                                                        |    mae |   exact |   mae_ols |
|:---------------------------------------------------------------------------------------------------------------|-------:|--------:|----------:|
| +0.9069 · [tw_min_fill] +0.09116 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.016                               | 0.1865 |  0.8596 |    0.2195 |
| +0.905 · [tw_min_fill] +0.09297 · [sqrt(g_deg_mean) · sqrt(tw_min_degree)] +1.014                              | 0.1872 |  0.8596 |    0.2176 |
| +0.9157 · [tw_min_fill] +0.0832 · [sqrt(spectral_radius) · sqrt(tw_min_fill)] +0.9907                          | 0.1889 |  0.8581 |    0.2109 |
| +0.9326 · [tw_min_fill] +0.06656 · [sqrt(spectral_radius) · sqrt(tw_min_degree)] +0.9918                       | 0.1902 |  0.8573 |    0.2104 |
| +0.9834 · [tw_min_fill] +0.01632 · [sqrt(rig_deg_expected) · sqrt(tw_min_degree)] +1.002                       | 0.1902 |  0.8566 |    0.2199 |
| +0.977 · [tw_min_fill] +0.02268 · [sqrt(rig_deg_expected) · sqrt(tw_min_fill)] +1.002                          | 0.1904 |  0.8568 |    0.2221 |
| +0.9026 · [tw_min_fill / sqrt(g_largest_comp_frac)] +0.09555 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.01    | 0.1926 |  0.8563 |    0.2179 |
| +0.8992 · [tw_min_fill / sqrt(g_largest_comp_frac)] +0.09892 · [sqrt(g_deg_mean) · sqrt(tw_min_degree)] +1.009 | 0.1932 |  0.8562 |    0.2164 |

## Leading monomials — target `optimum − lb_best`, pool `structure`, grouped by file

`mae`/`exact`: LAD constants; `mae_ols`/`exact_ols`: the least-squares first pass.

| formula                                 |   degree |    mae |   exact |   mae_ols |   exact_ols | fit on all rows (LAD)   |
|:----------------------------------------|---------:|-------:|--------:|----------:|------------:|:------------------------|
| g_deg_std · sep_size / g_density        |        3 | 0.3034 |  0.8022 |    0.3368 |      0.8018 | +0.01015 · t -0.0174    |
| g_deg_std · sep_size / rig_edge_prob    |        3 | 0.3035 |  0.8005 |    0.3353 |      0.7999 | +0.01075 · t -0.0188    |
| sep_size / (density · row_min)          |        3 | 0.3084 |  0.7997 |    0.3399 |      0.8049 | +0.02282 · t -0.0608    |
| g_deg_std · bw_rcm / rig_edge_prob      |        3 | 0.3123 |  0.8005 |    0.3506 |      0.7999 | +0.003774 · t -0.0151   |
| g_deg_std · bw_rcm / g_density          |        3 | 0.3135 |  0.7999 |    0.3538 |      0.8005 | +0.00368 · t -0.0155    |
| bw_rcm / (density · row_min)            |        3 | 0.3137 |  0.7999 |    0.3492 |      0.8022 | +0.008173 · t -0.0529   |
| g_deg_std / (density · row_min)         |        3 | 0.3167 |  0.7952 |    0.3820 |      0.7712 | +0.05422 · t -0.00882   |
| g_deg_std² / g_density                  |        2 | 0.3179 |  0.8038 |    0.3290 |      0.7961 | +0.02372 · t -0.00318   |
| sep_size / (row_min · col_max_frac)     |        3 | 0.3218 |  0.8019 |    0.3419 |      0.7887 | +0.03608 · t -0.0722    |
| g_deg_std² / rig_edge_prob              |        2 | 0.3223 |  0.7988 |    0.3311 |      0.7942 | +0.02434 · t -0.00326   |
| bw_rcm / (row_min · col_max_frac)       |        3 | 0.3257 |  0.7977 |    0.3463 |      0.7842 | +0.01288 · t -0.062     |
| g_deg_std / (density · col_max_frac)    |        3 | 0.3265 |  0.7820 |    0.3881 |      0.7800 | +0.006373 · t -0.00572  |
| g_edges / (density · row_min)           |        3 | 0.3293 |  0.7851 |    0.3768 |      0.7905 | +0.000654 · t -0.0305   |
| n_customers · g_deg_std / col_max_frac  |        3 | 0.3309 |  0.7911 |    0.3980 |      0.7922 | +0.001419 · t -0.0102   |
| n_customers · g_deg_std / rig_edge_prob |        3 | 0.3319 |  0.7947 |    0.3860 |      0.7988 | +0.002305 · t -0.0114   |

### Leading pairs — target `optimum − lb_best`, pool `structure`

| formula                                                                                                      |    mae |   exact |   mae_ols |
|:-------------------------------------------------------------------------------------------------------------|-------:|--------:|----------:|
| +0.01408 · [sep_size / (density · row_min)] +0.01135 · [g_deg_std² / rig_edge_prob] -0.04237                 | 0.2945 |  0.8040 |    0.2984 |
| +0.01346 · [sep_size / (density · row_min)] +0.01116 · [g_deg_std² / g_density] -0.04048                     | 0.2963 |  0.8033 |    0.2998 |
| +0.007018 · [g_deg_std · sep_size / rig_edge_prob] +0.02079 · [g_deg_std / (density · row_min)] -0.01806     | 0.2965 |  0.8049 |    0.3079 |
| +0.007916 · [g_deg_std · sep_size / rig_edge_prob] +0.004038 · [bw_rcm / (row_min · col_max_frac)] -0.03525  | 0.2974 |  0.8029 |    0.3025 |
| +0.007949 · [g_deg_std · sep_size / rig_edge_prob] +0.01052 · [sep_size / (row_min · col_max_frac)] -0.03601 | 0.2978 |  0.8035 |    0.3044 |
| +0.01713 · [sep_size / (density · row_min)] +0.004146 · [g_deg_std · bw_rcm / row_min] -0.05073              | 0.2988 |  0.8000 |    0.3070 |
| +0.006969 · [g_deg_std · sep_size / g_density] +0.01878 · [g_deg_std / (density · row_min)] -0.01732         | 0.2991 |  0.8061 |    0.3120 |
| +0.004539 · [bw_rcm / (density · row_min)] +0.01242 · [g_deg_std² / rig_edge_prob] -0.03461                  | 0.2993 |  0.8019 |    0.3052 |

## Point estimates of the optimum: baselines and the chosen formulas

Formulas here are cross-validated predictions grouped by file (constants refitted per fold); the residual formula is added to `lb_best`. `below`/`above` count rounded estimates under/over the optimum; a valid lower bound would have `above = 0`.

| estimate                               |   mae |   rmse |   exact |   over |   mae_rounded |   below |   above |   max_below |   max_above |
|:---------------------------------------|------:|-------:|--------:|-------:|--------------:|--------:|--------:|------------:|------------:|
| lb_best                                | 0.431 |  1.732 |   0.770 |  0.000 |         0.431 |    1467 |       0 |      30.000 |       0.000 |
| ub_best                                | 0.239 |  0.733 |   0.846 |  0.154 |         0.239 |       0 |     979 |       0.000 |      10.000 |
| tw_min_fill + 1                        | 0.188 |  0.606 |   0.857 |  0.067 |         0.188 |     481 |     428 |       3.000 |       7.000 |
| lb_best + 0 (no residual)              | 0.431 |  1.732 |   0.770 |  0.000 |         0.431 |    1467 |       0 |      30.000 |       0.000 |
| formula[optimum; structure]            | 0.672 |  2.330 |   0.671 |  0.094 |         0.669 |    1495 |     602 |      34.000 |       9.000 |
| pair[optimum; structure]               | 0.576 |  1.368 |   0.667 |  0.190 |         0.534 |     914 |    1212 |      19.000 |       9.000 |
| boosting[optimum; structure]           | 0.390 |  0.776 |   0.738 |  0.141 |         0.325 |     771 |     897 |       7.000 |      20.000 |
| formula[optimum; structure+tw]         | 0.188 |  0.606 |   0.857 |  0.067 |         0.188 |     481 |     428 |       3.000 |       7.000 |
| pair[optimum; structure+tw]            | 0.187 |  0.467 |   0.860 |  0.064 |         0.165 |     490 |     405 |       3.000 |       4.000 |
| boosting[optimum; structure+tw]        | 0.221 |  0.525 |   0.872 |  0.061 |         0.158 |     426 |     388 |       8.000 |      12.000 |
| formula[optimum − lb_best; structure]  | 0.303 |  0.768 |   0.802 |  0.037 |         0.266 |    1024 |     237 |      11.000 |      10.000 |
| pair[optimum − lb_best; structure]     | 0.295 |  0.728 |   0.804 |  0.053 |         0.253 |     909 |     341 |      13.000 |      11.000 |
| boosting[optimum − lb_best; structure] | 0.260 |  0.498 |   0.814 |  0.080 |         0.206 |     677 |     507 |       9.000 |       8.000 |

### By size band (grouped by file, target optimum)

| band   |   instances | estimate                               |    mae |   rmse |   exact |   over |
|:-------|------------:|:---------------------------------------|-------:|-------:|--------:|-------:|
| 1-30   |        5938 | lb_best                                |  0.226 |  0.527 |   0.800 |  0.000 |
| 1-30   |        5938 | ub_best                                |  0.155 |  0.494 |   0.880 |  0.120 |
| 1-30   |        5938 | tw_min_fill + 1                        |  0.121 |  0.372 |   0.887 |  0.048 |
| 1-30   |        5938 | lb_best + 0 (no residual)              |  0.226 |  0.527 |   0.800 |  0.000 |
| 1-30   |        5938 | formula[optimum; structure]            |  0.360 |  0.660 |   0.706 |  0.082 |
| 1-30   |        5938 | pair[optimum; structure]               |  0.424 |  0.721 |   0.696 |  0.185 |
| 1-30   |        5938 | boosting[optimum; structure]           |  0.313 |  0.489 |   0.771 |  0.128 |
| 1-30   |        5938 | formula[optimum; structure+tw]         |  0.121 |  0.372 |   0.887 |  0.048 |
| 1-30   |        5938 | pair[optimum; structure+tw]            |  0.140 |  0.350 |   0.887 |  0.048 |
| 1-30   |        5938 | boosting[optimum; structure+tw]        |  0.165 |  0.299 |   0.900 |  0.048 |
| 1-30   |        5938 | formula[optimum − lb_best; structure]  |  0.214 |  0.393 |   0.832 |  0.017 |
| 1-30   |        5938 | pair[optimum − lb_best; structure]     |  0.215 |  0.388 |   0.834 |  0.033 |
| 1-30   |        5938 | boosting[optimum − lb_best; structure] |  0.220 |  0.368 |   0.834 |  0.068 |
| 31-60  |         318 | lb_best                                |  1.132 |  1.764 |   0.453 |  0.000 |
| 31-60  |         318 | ub_best                                |  0.783 |  1.235 |   0.503 |  0.497 |
| 31-60  |         318 | tw_min_fill + 1                        |  0.525 |  0.871 |   0.582 |  0.160 |
| 31-60  |         318 | lb_best + 0 (no residual)              |  1.132 |  1.764 |   0.453 |  0.000 |
| 31-60  |         318 | formula[optimum; structure]            |  1.830 |  2.470 |   0.261 |  0.286 |
| 31-60  |         318 | pair[optimum; structure]               |  1.124 |  1.620 |   0.365 |  0.296 |
| 31-60  |         318 | boosting[optimum; structure]           |  1.003 |  1.314 |   0.352 |  0.267 |
| 31-60  |         318 | formula[optimum; structure+tw]         |  0.525 |  0.870 |   0.582 |  0.160 |
| 31-60  |         318 | pair[optimum; structure+tw]            |  0.563 |  0.839 |   0.591 |  0.145 |
| 31-60  |         318 | boosting[optimum; structure+tw]        |  0.658 |  0.914 |   0.563 |  0.186 |
| 31-60  |         318 | formula[optimum − lb_best; structure]  |  0.627 |  0.863 |   0.519 |  0.198 |
| 31-60  |         318 | pair[optimum − lb_best; structure]     |  0.568 |  0.782 |   0.528 |  0.245 |
| 31-60  |         318 | boosting[optimum − lb_best; structure] |  0.483 |  0.626 |   0.657 |  0.170 |
| 61-200 |         120 | lb_best                                |  8.708 | 11.719 |   0.117 |  0.000 |
| 61-200 |         120 | ub_best                                |  2.958 |  3.518 |   0.092 |  0.908 |
| 61-200 |         120 | tw_min_fill + 1                        |  2.633 |  3.271 |   0.133 |  0.767 |
| 61-200 |         120 | lb_best + 0 (no residual)              |  8.708 | 11.719 |   0.117 |  0.000 |
| 61-200 |         120 | formula[optimum; structure]            | 13.059 | 15.832 |   0.050 |  0.192 |
| 61-200 |         120 | pair[optimum; structure]               |  6.632 |  8.167 |   0.025 |  0.167 |
| 61-200 |         120 | boosting[optimum; structure]           |  2.589 |  3.953 |   0.125 |  0.442 |
| 61-200 |         120 | formula[optimum; structure+tw]         |  2.633 |  3.270 |   0.133 |  0.767 |
| 61-200 |         120 | pair[optimum; structure+tw]            |  1.505 |  1.912 |   0.225 |  0.617 |
| 61-200 |         120 | boosting[optimum; structure+tw]        |  1.822 |  2.825 |   0.308 |  0.383 |
| 61-200 |         120 | formula[optimum − lb_best; structure]  |  3.883 |  4.663 |   0.067 |  0.617 |
| 61-200 |         120 | pair[optimum − lb_best; structure]     |  3.485 |  4.369 |   0.042 |  0.575 |
| 61-200 |         120 | boosting[optimum − lb_best; structure] |  1.642 |  2.338 |   0.242 |  0.433 |

### By collection (grouped by file, target optimum)

| collection                          |   instances | estimate                               |   mae |   exact |
|:------------------------------------|------------:|:---------------------------------------|------:|--------:|
| ChallengeInstances2005/Harvey       |        2130 | lb_best                                | 0.281 |   0.754 |
| ChallengeInstances2005/Harvey       |        2130 | ub_best                                | 0.196 |   0.847 |
| ChallengeInstances2005/Harvey       |        2130 | tw_min_fill + 1                        | 0.160 |   0.857 |
| ChallengeInstances2005/Harvey       |        2130 | lb_best + 0 (no residual)              | 0.281 |   0.754 |
| ChallengeInstances2005/Harvey       |        2130 | formula[optimum; structure]            | 0.453 |   0.643 |
| ChallengeInstances2005/Harvey       |        2130 | pair[optimum; structure]               | 0.511 |   0.631 |
| ChallengeInstances2005/Harvey       |        2130 | boosting[optimum; structure]           | 0.335 |   0.751 |
| ChallengeInstances2005/Harvey       |        2130 | formula[optimum; structure+tw]         | 0.160 |   0.857 |
| ChallengeInstances2005/Harvey       |        2130 | pair[optimum; structure+tw]            | 0.173 |   0.857 |
| ChallengeInstances2005/Harvey       |        2130 | boosting[optimum; structure+tw]        | 0.192 |   0.872 |
| ChallengeInstances2005/Harvey       |        2130 | formula[optimum − lb_best; structure]  | 0.266 |   0.786 |
| ChallengeInstances2005/Harvey       |        2130 | pair[optimum − lb_best; structure]     | 0.264 |   0.782 |
| ChallengeInstances2005/Harvey       |        2130 | boosting[optimum − lb_best; structure] | 0.274 |   0.785 |
| ChallengeInstances2005/Miller       |           1 | lb_best                                | 0.000 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | ub_best                                | 0.000 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | tw_min_fill + 1                        | 0.000 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | lb_best + 0 (no residual)              | 0.000 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | formula[optimum; structure]            | 0.598 |   0.000 |
| ChallengeInstances2005/Miller       |           1 | pair[optimum; structure]               | 2.340 |   0.000 |
| ChallengeInstances2005/Miller       |           1 | boosting[optimum; structure]           | 0.222 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | formula[optimum; structure+tw]         | 0.000 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | pair[optimum; structure+tw]            | 0.103 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | boosting[optimum; structure+tw]        | 0.154 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | formula[optimum − lb_best; structure]  | 0.016 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | pair[optimum − lb_best; structure]     | 0.025 |   1.000 |
| ChallengeInstances2005/Miller       |           1 | boosting[optimum − lb_best; structure] | 0.082 |   1.000 |
| ChallengeInstances2005/Shaw         |          25 | lb_best                                | 0.440 |   0.560 |
| ChallengeInstances2005/Shaw         |          25 | ub_best                                | 0.160 |   0.880 |
| ChallengeInstances2005/Shaw         |          25 | tw_min_fill + 1                        | 0.240 |   0.760 |
| ChallengeInstances2005/Shaw         |          25 | lb_best + 0 (no residual)              | 0.440 |   0.560 |
| ChallengeInstances2005/Shaw         |          25 | formula[optimum; structure]            | 0.854 |   0.320 |
| ChallengeInstances2005/Shaw         |          25 | pair[optimum; structure]               | 0.629 |   0.560 |
| ChallengeInstances2005/Shaw         |          25 | boosting[optimum; structure]           | 0.296 |   0.800 |
| ChallengeInstances2005/Shaw         |          25 | formula[optimum; structure+tw]         | 0.240 |   0.760 |
| ChallengeInstances2005/Shaw         |          25 | pair[optimum; structure+tw]            | 0.250 |   0.760 |
| ChallengeInstances2005/Shaw         |          25 | boosting[optimum; structure+tw]        | 0.202 |   0.880 |
| ChallengeInstances2005/Shaw         |          25 | formula[optimum − lb_best; structure]  | 0.461 |   0.560 |
| ChallengeInstances2005/Shaw         |          25 | pair[optimum − lb_best; structure]     | 0.457 |   0.560 |
| ChallengeInstances2005/Shaw         |          25 | boosting[optimum − lb_best; structure] | 0.318 |   0.800 |
| ChallengeInstances2005/Simonis      |        3630 | lb_best                                | 0.178 |   0.842 |
| ChallengeInstances2005/Simonis      |        3630 | ub_best                                | 0.106 |   0.915 |
| ChallengeInstances2005/Simonis      |        3630 | tw_min_fill + 1                        | 0.085 |   0.917 |
| ChallengeInstances2005/Simonis      |        3630 | lb_best + 0 (no residual)              | 0.178 |   0.842 |
| ChallengeInstances2005/Simonis      |        3630 | formula[optimum; structure]            | 0.282 |   0.760 |
| ChallengeInstances2005/Simonis      |        3630 | pair[optimum; structure]               | 0.351 |   0.749 |
| ChallengeInstances2005/Simonis      |        3630 | boosting[optimum; structure]           | 0.330 |   0.771 |
| ChallengeInstances2005/Simonis      |        3630 | formula[optimum; structure+tw]         | 0.085 |   0.917 |
| ChallengeInstances2005/Simonis      |        3630 | pair[optimum; structure+tw]            | 0.107 |   0.917 |
| ChallengeInstances2005/Simonis      |        3630 | boosting[optimum; structure+tw]        | 0.161 |   0.914 |
| ChallengeInstances2005/Simonis      |        3630 | formula[optimum − lb_best; structure]  | 0.172 |   0.870 |
| ChallengeInstances2005/Simonis      |        3630 | pair[optimum − lb_best; structure]     | 0.174 |   0.876 |
| ChallengeInstances2005/Simonis      |        3630 | boosting[optimum − lb_best; structure] | 0.184 |   0.871 |
| ChallengeInstances2005/Wilson       |          20 | lb_best                                | 1.550 |   0.800 |
| ChallengeInstances2005/Wilson       |          20 | ub_best                                | 0.550 |   0.700 |
| ChallengeInstances2005/Wilson       |          20 | tw_min_fill + 1                        | 0.450 |   0.800 |
| ChallengeInstances2005/Wilson       |          20 | lb_best + 0 (no residual)              | 1.550 |   0.800 |
| ChallengeInstances2005/Wilson       |          20 | formula[optimum; structure]            | 2.635 |   0.300 |
| ChallengeInstances2005/Wilson       |          20 | pair[optimum; structure]               | 2.553 |   0.250 |
| ChallengeInstances2005/Wilson       |          20 | boosting[optimum; structure]           | 2.044 |   0.400 |
| ChallengeInstances2005/Wilson       |          20 | formula[optimum; structure+tw]         | 0.450 |   0.800 |
| ChallengeInstances2005/Wilson       |          20 | pair[optimum; structure+tw]            | 0.471 |   0.650 |
| ChallengeInstances2005/Wilson       |          20 | boosting[optimum; structure+tw]        | 1.250 |   0.750 |
| ChallengeInstances2005/Wilson       |          20 | formula[optimum − lb_best; structure]  | 1.329 |   0.500 |
| ChallengeInstances2005/Wilson       |          20 | pair[optimum − lb_best; structure]     | 0.771 |   0.550 |
| ChallengeInstances2005/Wilson       |          20 | boosting[optimum − lb_best; structure] | 0.286 |   0.900 |
| MOSP_Instances/Challenge            |          46 | lb_best                                | 0.913 |   0.674 |
| MOSP_Instances/Challenge            |          46 | ub_best                                | 0.326 |   0.804 |
| MOSP_Instances/Challenge            |          46 | tw_min_fill + 1                        | 0.326 |   0.783 |
| MOSP_Instances/Challenge            |          46 | lb_best + 0 (no residual)              | 0.913 |   0.674 |
| MOSP_Instances/Challenge            |          46 | formula[optimum; structure]            | 1.622 |   0.304 |
| MOSP_Instances/Challenge            |          46 | pair[optimum; structure]               | 1.476 |   0.370 |
| MOSP_Instances/Challenge            |          46 | boosting[optimum; structure]           | 0.984 |   0.652 |
| MOSP_Instances/Challenge            |          46 | formula[optimum; structure+tw]         | 0.326 |   0.783 |
| MOSP_Instances/Challenge            |          46 | pair[optimum; structure+tw]            | 0.343 |   0.717 |
| MOSP_Instances/Challenge            |          46 | boosting[optimum; structure+tw]        | 0.533 |   0.870 |
| MOSP_Instances/Challenge            |          46 | formula[optimum − lb_best; structure]  | 0.813 |   0.565 |
| MOSP_Instances/Challenge            |          46 | pair[optimum − lb_best; structure]     | 0.589 |   0.565 |
| MOSP_Instances/Challenge            |          46 | boosting[optimum − lb_best; structure] | 0.289 |   0.870 |
| MOSP_Instances/Chu_Stuckey          |         200 | lb_best                                | 5.425 |   0.265 |
| MOSP_Instances/Chu_Stuckey          |         200 | ub_best                                | 2.075 |   0.255 |
| MOSP_Instances/Chu_Stuckey          |         200 | tw_min_fill + 1                        | 1.715 |   0.335 |
| MOSP_Instances/Chu_Stuckey          |         200 | lb_best + 0 (no residual)              | 5.425 |   0.265 |
| MOSP_Instances/Chu_Stuckey          |         200 | formula[optimum; structure]            | 8.462 |   0.085 |
| MOSP_Instances/Chu_Stuckey          |         200 | pair[optimum; structure]               | 4.262 |   0.125 |
| MOSP_Instances/Chu_Stuckey          |         200 | boosting[optimum; structure]           | 1.564 |   0.275 |
| MOSP_Instances/Chu_Stuckey          |         200 | formula[optimum; structure+tw]         | 1.715 |   0.335 |
| MOSP_Instances/Chu_Stuckey          |         200 | pair[optimum; structure+tw]            | 1.043 |   0.435 |
| MOSP_Instances/Chu_Stuckey          |         200 | boosting[optimum; structure+tw]        | 1.165 |   0.390 |
| MOSP_Instances/Chu_Stuckey          |         200 | formula[optimum − lb_best; structure]  | 2.430 |   0.240 |
| MOSP_Instances/Chu_Stuckey          |         200 | pair[optimum − lb_best; structure]     | 2.230 |   0.255 |
| MOSP_Instances/Chu_Stuckey          |         200 | boosting[optimum − lb_best; structure] | 1.191 |   0.385 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | lb_best                                | 1.023 |   0.417 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | ub_best                                | 0.850 |   0.447 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | tw_min_fill + 1                        | 0.530 |   0.557 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | lb_best + 0 (no residual)              | 1.023 |   0.417 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | formula[optimum; structure]            | 1.254 |   0.330 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | pair[optimum; structure]               | 0.920 |   0.403 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | boosting[optimum; structure]           | 0.462 |   0.610 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | formula[optimum; structure+tw]         | 0.530 |   0.557 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | pair[optimum; structure+tw]            | 0.572 |   0.557 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | boosting[optimum; structure+tw]        | 0.382 |   0.707 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | formula[optimum − lb_best; structure]  | 0.505 |   0.590 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | pair[optimum − lb_best; structure]     | 0.512 |   0.573 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | boosting[optimum − lb_best; structure] | 0.426 |   0.637 |
| MOSP_Instances/SCOOP                |          24 | lb_best                                | 1.042 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | ub_best                                | 0.958 |   0.500 |
| MOSP_Instances/SCOOP                |          24 | tw_min_fill + 1                        | 0.833 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | lb_best + 0 (no residual)              | 1.042 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | formula[optimum; structure]            | 3.190 |   0.208 |
| MOSP_Instances/SCOOP                |          24 | pair[optimum; structure]               | 1.870 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | boosting[optimum; structure]           | 1.429 |   0.542 |
| MOSP_Instances/SCOOP                |          24 | formula[optimum; structure+tw]         | 0.833 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | pair[optimum; structure+tw]            | 0.871 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | boosting[optimum; structure+tw]        | 0.429 |   0.750 |
| MOSP_Instances/SCOOP                |          24 | formula[optimum − lb_best; structure]  | 1.245 |   0.333 |
| MOSP_Instances/SCOOP                |          24 | pair[optimum − lb_best; structure]     | 1.298 |   0.250 |
| MOSP_Instances/SCOOP                |          24 | boosting[optimum − lb_best; structure] | 0.519 |   0.458 |

## The sandwich: degeneracy + 1 ≤ optimum ≤ bandwidth + 1, constants fixed by hand

Both searches keep returning `g_degeneracy` and `bw_rcm`. Degeneracy ≤ treewidth ≤ pathwidth and bandwidth ≥ pathwidth, so `g_degeneracy + 1` is a proved lower bound on the optimum and `bw_rcm + 1` a proved upper bound (both checked on every row). The optimum is `g_degeneracy + 1 + λ · (bw_rcm − g_degeneracy)` for some λ in [0, 1]; nothing below is fitted, so there is nothing to hold out.

| estimate                        |   mae |   rmse |   exact |   over |   below |   above |   max_below |   max_above |   mae 1-30 |   exact 1-30 |   mae 31-60 |   exact 31-60 |   mae 61-200 |   exact 61-200 |
|:--------------------------------|------:|-------:|--------:|-------:|--------:|--------:|------------:|------------:|-----------:|-------------:|------------:|--------------:|-------------:|---------------:|
| g_degeneracy + 1                | 1.782 |  4.965 |   0.516 |  0.000 |    3083 |       0 |      61.000 |       0.000 |      1.132 |        0.539 |       4.459 |         0.258 |       26.817 |          0.067 |
| bw_rcm + 1                      | 1.935 |  4.422 |   0.514 |  0.486 |       0 |    3097 |       0.000 |      49.000 |      1.302 |        0.542 |       6.566 |         0.179 |       20.983 |          0.017 |
| 1 + sqrt(g_degeneracy · bw_rcm) | 0.672 |  2.330 |   0.671 |  0.094 |    1495 |     600 |      34.000 |       9.000 |      0.360 |        0.706 |       1.830 |         0.261 |       13.060 |          0.067 |
| 1 + (g_degeneracy + bw_rcm) / 2 | 0.631 |  1.773 |   0.788 |  0.130 |     930 |    1146 |      22.000 |      21.000 |      0.374 |        0.827 |       2.239 |         0.330 |        9.125 |          0.075 |
| tw_min_fill + 1                 | 0.188 |  0.606 |   0.857 |  0.067 |     481 |     428 |       3.000 |       7.000 |      0.121 |        0.887 |       0.525 |         0.582 |        2.633 |          0.133 |
| lb_best                         | 0.431 |  1.732 |   0.770 |  0.000 |    1467 |       0 |      30.000 |       0.000 |      0.226 |        0.800 |       1.132 |         0.453 |        8.708 |          0.117 |

| check                                       | value                                 |
|:--------------------------------------------|:--------------------------------------|
| instances                                   | 6376                                  |
| g_degeneracy + 1 > optimum (must be 0)      | 0                                     |
| bw_rcm + 1 < optimum (must be 0)            | 0                                     |
| bw_rcm == g_degeneracy (optimum forced)     | 2823                                  |
| of those with optimum == g_degeneracy + 1   | 2823                                  |
| bw_rcm > g_degeneracy                       | 3553                                  |
| λ quantiles 10/25/50/75/90                  | 0.000 / 0.333 / 0.500 / 0.667 / 1.000 |
| λ mean                                      | 0.486                                 |
| degree-regular graphs (g_deg_std == 0)      | 1705                                  |
| of those complete (g_density == 1)          | 1669                                  |
| max gap optimum − lb_best on regular graphs | 0.0                                   |
| mean gap on the rest                        | 0.588                                 |

λ where `bw_rcm > g_degeneracy`, by size band:

| band   |   instances |   λ median |   λ mean |
|:-------|------------:|-----------:|---------:|
| 1-30   |        3169 |      0.500 |    0.491 |
| 31-60  |         266 |      0.409 |    0.411 |
| 61-200 |         118 |      0.550 |    0.509 |

## Nested protocol: the formula selected on the training files only

Outer GroupKFold by file; the whole search runs inside each training fold and its winner is scored on the held-out files. These are the honest grouped errors; the winners per fold show whether one formula keeps being chosen.

| target            | pool                             | estimate      |   mae |   rmse |   exact |   over |   seconds |
|:------------------|:---------------------------------|:--------------|------:|-------:|--------:|-------:|----------:|
| optimum           | structure                        | best monomial | 0.672 |  2.330 |   0.671 |  0.094 |    35.055 |
| optimum           | structure                        | best pair     | 0.608 |  1.379 |   0.661 |  0.183 |   nan     |
| optimum           | structure                        | boosting      | 0.390 |  0.776 |   0.738 |  0.141 |   nan     |
| optimum           | structure + treewidth heuristics | best monomial | 0.188 |  0.606 |   0.857 |  0.067 |    43.631 |
| optimum           | structure + treewidth heuristics | best pair     | 0.187 |  0.467 |   0.860 |  0.064 |   nan     |
| optimum           | structure + treewidth heuristics | boosting      | 0.221 |  0.525 |   0.872 |  0.061 |   nan     |
| optimum − lb_best | structure                        | best monomial | 0.304 |  0.756 |   0.800 |  0.039 |    36.985 |
| optimum − lb_best | structure                        | best pair     | 0.300 |  0.720 |   0.803 |  0.045 |   nan     |
| optimum − lb_best | structure                        | boosting      | 0.260 |  0.498 |   0.814 |  0.080 |   nan     |

### Winners per outer fold

| target            | pool                             |   fold | monomial                             |   inner_mae | pair                                                                                                        |   pair_inner_mae |
|:------------------|:---------------------------------|-------:|:-------------------------------------|------------:|:------------------------------------------------------------------------------------------------------------|-----------------:|
| optimum           | structure                        |      0 | sqrt(g_degeneracy) · sqrt(bw_rcm)    |      0.6313 | +0.5426 · [bw_rcm² / n_customers] +0.4593 · [spectral_radius / sqrt(g_largest_comp_frac)] +1.479            |           0.5031 |
| optimum           | structure                        |      1 | sqrt(g_degeneracy) · sqrt(bw_rcm)    |      0.6705 | +0.5425 · [bw_rcm² / n_customers] +0.4587 · [sqrt(g_deg_mean) · sqrt(spectral_radius)] +1.488               |           0.5724 |
| optimum           | structure                        |      2 | sqrt(g_degeneracy) · sqrt(bw_rcm)    |      0.6928 | +0.733 · [sqrt(g_degeneracy) · sqrt(bw_rcm)] +0.8671 · [bw_rcm · sep_frac / g_largest_comp_frac] +0.361     |           0.5703 |
| optimum           | structure                        |      3 | sqrt(g_degeneracy) · sqrt(bw_rcm)    |      0.6648 | +0.5175 · [bw_rcm² / n_customers] +0.4836 · [sqrt(g_deg_mean) · sqrt(spectral_radius)] +1.467               |           0.5823 |
| optimum           | structure                        |      4 | sqrt(g_degeneracy) · sqrt(bw_rcm)    |      0.7011 | +0.5254 · [bw_rcm² / n_customers] +0.4758 · [sqrt(g_deg_mean) · sqrt(spectral_radius)] +1.474               |           0.6006 |
| optimum           | structure + treewidth heuristics |      0 | tw_min_fill                          |      0.1699 | +0.907 · [tw_min_fill] +0.09159 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.009                             |           0.1686 |
| optimum           | structure + treewidth heuristics |      1 | tw_min_fill                          |      0.1865 | +0.9068 · [tw_min_fill] +0.09121 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.017                            |           0.1841 |
| optimum           | structure + treewidth heuristics |      2 | tw_min_fill                          |      0.2034 | +0.8957 · [tw_min_fill] +0.102 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.019                              |           0.1997 |
| optimum           | structure + treewidth heuristics |      3 | tw_min_fill                          |      0.1846 | +0.9066 · [tw_min_fill] +0.09152 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.011                            |           0.1832 |
| optimum           | structure + treewidth heuristics |      4 | tw_min_fill                          |      0.1979 | +0.912 · [tw_min_fill] +0.08595 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.017                             |           0.1969 |
| optimum − lb_best | structure                        |      0 | g_deg_std · sep_size / g_density     |      0.2706 | +0.007095 · [g_deg_std · sep_size / rig_edge_prob] +0.004435 · [bw_rcm / (row_min · col_max_frac)] -0.03275 |           0.2656 |
| optimum − lb_best | structure                        |      1 | g_deg_std · sep_size / rig_edge_prob |      0.2984 | +0.007912 · [g_deg_std · sep_size / rig_edge_prob] +0.004188 · [bw_rcm / (row_min · col_max_frac)] -0.03398 |           0.2917 |
| optimum − lb_best | structure                        |      2 | g_deg_std · sep_size / rig_edge_prob |      0.3160 | +0.008834 · [g_deg_std · sep_size / rig_edge_prob] +0.003411 · [bw_rcm / (row_min · col_max_frac)] -0.03579 |           0.3121 |
| optimum − lb_best | structure                        |      3 | g_deg_std · sep_size / rig_edge_prob |      0.3023 | +0.007434 · [g_deg_std · sep_size / rig_edge_prob] +0.004723 · [bw_rcm / (row_min · col_max_frac)] -0.04206 |           0.2964 |
| optimum − lb_best | structure                        |      4 | g_deg_std · sep_size / rig_edge_prob |      0.3269 | +0.006859 · [g_deg_std · sep_size / rig_edge_prob] +0.02248 · [g_deg_std / (density · row_min)] -0.01753    |           0.3169 |

## PySR on a held-out fifth of the files

Train 5657 instances / test 719 instances (124 files held out). 2000 iterations of search per row on 4 Julia threads, `L1DistLoss`, operators `+ - * /`, `sqrt`, `square`, `log`, maxsize 20. The enumerated monomial and pair are selected by grouped CV on the training rows only; boosting is fitted on the same rows.

| target            | pool                             | method                     | formula                                                                                                                             |   mae |   rmse |   exact |   over |
|:------------------|:---------------------------------|:---------------------------|:------------------------------------------------------------------------------------------------------------------------------------|------:|-------:|--------:|-------:|
| optimum           | structure                        | best monomial (enumerated) | sqrt(g_degeneracy) · sqrt(bw_rcm)                                                                                                   | 0.820 |  2.944 |   0.680 |  0.095 |
| optimum           | structure                        | best pair (enumerated)     | +0.5206 · [bw_rcm² / n_customers] +0.4806 · [sqrt(g_deg_mean) · sqrt(spectral_radius)] +1.468                                       | 0.618 |  1.681 |   0.677 |  0.167 |
| optimum           | structure                        | boosting                   |                                                                                                                                     | 0.358 |  0.663 |   0.783 |  0.114 |
| optimum           | structure                        | PySR (its own pick)        | distinct_row_frac + sqrt(g_degeneracy * bw_rcm)                                                                                     | 0.814 |  2.935 |   0.677 |  0.095 |
| optimum           | structure                        | PySR (best on held-out)    | square(g_degeneracy / bw_rcm) + sqrt(bw_rcm * (spectral_radius - (g_clustering * sqrt((g_deg_std * 1.7341464) * shape_ratio))))     | 0.525 |  1.695 |   0.745 |  0.128 |
| optimum           | structure + treewidth heuristics | best monomial (enumerated) | tw_min_fill                                                                                                                         | 0.224 |  0.699 |   0.841 |  0.070 |
| optimum           | structure + treewidth heuristics | best pair (enumerated)     | +0.912 · [tw_min_fill] +0.086 · [sqrt(g_deg_mean) · sqrt(tw_min_fill)] +1.016                                                       | 0.208 |  0.519 |   0.844 |  0.064 |
| optimum           | structure + treewidth heuristics | boosting                   |                                                                                                                                     | 0.229 |  0.553 |   0.869 |  0.058 |
| optimum           | structure + treewidth heuristics | PySR (its own pick)        | tw_min_fill + 0.99999994                                                                                                            | 0.224 |  0.699 |   0.841 |  0.070 |
| optimum           | structure + treewidth heuristics | PySR (best on held-out)    | (tw_min_fill + 1.0009065) - square((g_deg_mean - (tw_min_fill * 1.0435883)) / (((row_std + rig_edge_prob) * 7.078448) + 3.1676776)) | 0.173 |  0.448 |   0.847 |  0.058 |
| optimum − lb_best | structure                        | best monomial (enumerated) | g_deg_std · sep_size / rig_edge_prob                                                                                                | 0.345 |  0.885 |   0.772 |  0.047 |
| optimum − lb_best | structure                        | best pair (enumerated)     | +0.007944 · [g_deg_std · sep_size / rig_edge_prob] +0.004124 · [bw_rcm / (row_min · col_max_frac)] -0.03748                         | 0.341 |  0.866 |   0.775 |  0.051 |
| optimum − lb_best | structure                        | boosting                   |                                                                                                                                     | 0.276 |  0.567 |   0.815 |  0.092 |
| optimum − lb_best | structure                        | PySR (its own pick)        | square((g_deg_mean - bw_rcm) * 0.070278354)                                                                                         | 0.321 |  0.929 |   0.787 |  0.024 |
| optimum − lb_best | structure                        | PySR (best on held-out)    | square(square((g_components * (rig_edge_prob * distinct_row_frac)) + -0.8898241) * (distinct_row_frac * g_deg_std))                 | 0.235 |  0.610 |   0.801 |  0.039 |

### PySR Pareto fronts, scored on the held-out files

| target            | pool                             |   complexity |   train_loss | equation                                                                                                                                                                            |    mae |   rmse |   exact |   over | chosen   |
|:------------------|:---------------------------------|-------------:|-------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------:|-------:|--------:|-------:|:---------|
| optimum           | structure                        |            1 |       1.1940 | spectral_radius                                                                                                                                                                     | 1.4455 | 4.1134 |  0.3491 | 0.0890 |          |
| optimum           | structure                        |            3 |       1.1254 | spectral_radius + density                                                                                                                                                           | 1.2916 | 4.0750 |  0.5661 | 0.1599 |          |
| optimum           | structure                        |            4 |       0.9123 | sqrt(g_deg_mean * bw_rcm)                                                                                                                                                           | 0.9910 | 1.9827 |  0.2879 | 0.1349 |          |
| optimum           | structure                        |            5 |       0.9123 | sqrt(g_deg_mean) * sqrt(bw_rcm)                                                                                                                                                     | 0.9910 | 1.9827 |  0.2879 | 0.1349 |          |
| optimum           | structure                        |            6 |       0.6487 | distinct_row_frac + sqrt(g_degeneracy * bw_rcm)                                                                                                                                     | 0.8141 | 2.9349 |  0.6773 | 0.0946 | *        |
| optimum           | structure                        |            7 |       0.6466 | square(distinct_row_frac) + sqrt(g_degeneracy * bw_rcm)                                                                                                                             | 0.8131 | 2.9308 |  0.6773 | 0.0918 |          |
| optimum           | structure                        |            8 |       0.5766 | distinct_row_frac + sqrt(g_deg_mean * (bw_rcm - g_deg_std))                                                                                                                         | 0.6930 | 2.2496 |  0.6940 | 0.1586 |          |
| optimum           | structure                        |            9 |       0.5719 | distinct_row_frac + sqrt(bw_rcm * (g_deg_mean - sqrt(g_deg_std)))                                                                                                                   | 0.6520 | 2.1130 |  0.7079 | 0.1794 |          |
| optimum           | structure                        |           10 |       0.5462 | sqrt((spectral_radius - (g_clustering * g_deg_std)) * bw_rcm) + rig_edge_prob                                                                                                       | 0.6333 | 2.0325 |  0.7107 | 0.1669 |          |
| optimum           | structure                        |           11 |       0.5139 | sqrt(bw_rcm * (g_deg_mean - sqrt(shape_ratio * g_deg_std))) - -1.0000001                                                                                                            | 0.6276 | 2.1318 |  0.7316 | 0.1460 |          |
| optimum           | structure                        |           12 |       0.5120 | sqrt(g_components) + sqrt((g_deg_mean - sqrt(g_deg_std * shape_ratio)) * bw_rcm)                                                                                                    | 0.6210 | 2.1289 |  0.7371 | 0.1474 |          |
| optimum           | structure                        |           13 |       0.4887 | sqrt((spectral_radius - (1.3490039 * sqrt(shape_ratio * g_deg_std))) * bw_rcm) + distinct_row_frac                                                                                  | 0.5690 | 1.8237 |  0.7288 | 0.1544 |          |
| optimum           | structure                        |           15 |       0.4840 | sqrt(bw_rcm * (spectral_radius - (sqrt(shape_ratio * g_deg_std) * 1.1718863))) + (g_degeneracy / bw_rcm)                                                                            | 0.5644 | 1.8489 |  0.7399 | 0.1238 |          |
| optimum           | structure                        |           17 |       0.4733 | (g_degeneracy / bw_rcm) + sqrt(bw_rcm * (spectral_radius - sqrt(g_clustering * ((g_deg_std * 1.734218) * shape_ratio))))                                                            | 0.5372 | 1.7587 |  0.7510 | 0.1349 |          |
| optimum           | structure                        |           18 |       0.4709 | square(g_degeneracy / bw_rcm) + sqrt(bw_rcm * (spectral_radius - (g_clustering * sqrt((g_deg_std * 1.7341464) * shape_ratio))))                                                     | 0.5250 | 1.6949 |  0.7455 | 0.1280 |          |
| optimum           | structure                        |           19 |       0.4605 | (g_degeneracy / g_deg_max) + sqrt((spectral_radius - (sqrt((g_deg_max * (shape_ratio * g_deg_std)) / g_degeneracy) * g_clustering)) * bw_rcm)                                       | 0.5264 | 1.7005 |  0.7330 | 0.1502 |          |
| optimum           | structure                        |           20 |       0.4572 | square(g_degeneracy / bw_rcm) + sqrt(bw_rcm * (spectral_radius - (sqrt((g_deg_max * (shape_ratio * g_deg_std)) / g_degeneracy) * g_clustering)))                                    | 0.5276 | 1.7338 |  0.7455 | 0.1224 |          |
| optimum           | structure + treewidth heuristics |            1 |       1.0343 | tw_min_degree                                                                                                                                                                       | 1.0821 | 1.3069 |  0.0793 | 0.0431 |          |
| optimum           | structure + treewidth heuristics |            3 |       0.1838 | tw_min_fill + 0.99999994                                                                                                                                                            | 0.2239 | 0.6987 |  0.8414 | 0.0695 | *        |
| optimum           | structure + treewidth heuristics |            5 |       0.1838 | (tw_min_fill + 1.6351659) - 0.6351662                                                                                                                                               | 0.2239 | 0.6987 |  0.8414 | 0.0695 |          |
| optimum           | structure + treewidth heuristics |            8 |       0.1836 | tw_min_fill + (1.0070641 - square(cc_greedy / -118.97394))                                                                                                                          | 0.2181 | 0.6311 |  0.8414 | 0.0668 |          |
| optimum           | structure + treewidth heuristics |            9 |       0.1686 | (tw_min_fill - square(square(cc_greedy) / 7068.009)) + 1.0002002                                                                                                                    | 0.2025 | 0.5697 |  0.8401 | 0.0584 |          |
| optimum           | structure + treewidth heuristics |           10 |       0.1611 | (tw_min_fill + 1.0010463) - square((tw_min_fill - g_deg_mean) / 18.886564)                                                                                                          | 0.1824 | 0.4926 |  0.8484 | 0.0584 |          |
| optimum           | structure + treewidth heuristics |           12 |       0.1549 | tw_min_fill + (1.0018277 - square((tw_min_fill - g_deg_mean) / (row_max * 1.7141763)))                                                                                              | 0.1822 | 0.4821 |  0.8484 | 0.0542 |          |
| optimum           | structure + treewidth heuristics |           13 |       0.1525 | tw_min_fill + (1.0018277 - square((tw_min_fill - g_deg_mean) / square(row_std + 2.2323313)))                                                                                        | 0.1778 | 0.4557 |  0.8498 | 0.0570 |          |
| optimum           | structure + treewidth heuristics |           14 |       0.1516 | tw_min_fill + (1.0019441 - square((g_deg_mean - tw_min_fill) / ((row_std * 5.951502) + 5.159428)))                                                                                  | 0.1774 | 0.4478 |  0.8470 | 0.0584 |          |
| optimum           | structure + treewidth heuristics |           15 |       0.1500 | (tw_min_fill + 1.0016836) - square(((tw_min_fill * 1.0270205) - g_deg_mean) / square(row_std + 2.2958949))                                                                          | 0.1757 | 0.4516 |  0.8498 | 0.0570 |          |
| optimum           | structure + treewidth heuristics |           16 |       0.1494 | 1.0012126 + (tw_min_fill - square(((tw_min_fill * 1.0253094) - g_deg_mean) / ((row_std * 6.0873632) + 5.5541368)))                                                                  | 0.1755 | 0.4469 |  0.8456 | 0.0584 |          |
| optimum           | structure + treewidth heuristics |           18 |       0.1489 | (tw_min_fill + 1.0009065) - square((g_deg_mean - (tw_min_fill * 1.0435883)) / (((row_std + rig_edge_prob) * 7.078448) + 3.1676776))                                                 | 0.1734 | 0.4482 |  0.8470 | 0.0584 |          |
| optimum           | structure + treewidth heuristics |           19 |       0.1483 | (tw_min_fill + 1.0013524) - square(((tw_min_fill * 1.0285536) - g_deg_mean) / (((row_std + rig_edge_prob) * 6.0527277) + log(n_patterns)))                                          | 0.1735 | 0.4447 |  0.8484 | 0.0570 |          |
| optimum − lb_best | structure                        |            1 |       0.4147 | 0.0                                                                                                                                                                                 | 0.5549 | 2.2633 |  0.7775 | 0.0000 |          |
| optimum − lb_best | structure                        |            3 |       0.3980 | spectral_radius - g_deg_mean                                                                                                                                                        | 0.4841 | 1.7211 |  0.7566 | 0.1182 |          |
| optimum − lb_best | structure                        |            4 |       0.3751 | square(g_deg_std * -0.18770522)                                                                                                                                                     | 0.5133 | 1.8928 |  0.7608 | 0.0320 |          |
| optimum − lb_best | structure                        |            5 |       0.3284 | (bw_rcm - g_degeneracy) * 0.09090957                                                                                                                                                | 0.4366 | 1.5202 |  0.7789 | 0.0709 |          |
| optimum − lb_best | structure                        |            6 |       0.2870 | square((g_deg_mean - bw_rcm) * 0.070278354)                                                                                                                                         | 0.3213 | 0.9294 |  0.7872 | 0.0236 | *        |
| optimum − lb_best | structure                        |            7 |       0.2602 | square(square(rig_edge_prob + -0.8867843) * g_deg_std)                                                                                                                              | 0.2698 | 0.7185 |  0.7858 | 0.0501 |          |
| optimum − lb_best | structure                        |            8 |       0.2542 | square((fiedler_lcc - bw_rcm) * (0.05583164 / row_min))                                                                                                                             | 0.3034 | 0.8651 |  0.7886 | 0.0292 |          |
| optimum − lb_best | structure                        |            9 |       0.2471 | square(g_deg_std * (square(rig_edge_prob + -0.8976283) * distinct_row_frac))                                                                                                        | 0.2410 | 0.6066 |  0.7955 | 0.0417 |          |
| optimum − lb_best | structure                        |           10 |       0.2466 | square(((bw_rcm + shape_ratio) - g_degeneracy) * (0.066291206 / row_min))                                                                                                           | 0.3006 | 0.8988 |  0.7942 | 0.0264 |          |
| optimum − lb_best | structure                        |           11 |       0.2442 | square(square((rig_edge_prob * g_components) + -0.89799356) * (g_deg_std * distinct_row_frac))                                                                                      | 0.2392 | 0.6052 |  0.7955 | 0.0403 |          |
| optimum − lb_best | structure                        |           12 |       0.2423 | square(g_deg_std * square(((rig_edge_prob * square(distinct_row_frac)) + -0.89528954) * distinct_row_frac))                                                                         | 0.2415 | 0.6215 |  0.8039 | 0.0292 |          |
| optimum − lb_best | structure                        |           13 |       0.2418 | square(square((g_components * (rig_edge_prob * distinct_row_frac)) + -0.8898241) * (distinct_row_frac * g_deg_std))                                                                 | 0.2349 | 0.6103 |  0.8011 | 0.0389 |          |
| optimum − lb_best | structure                        |           14 |       0.2402 | square(square(((square(distinct_row_frac) * (rig_edge_prob * g_components)) + -0.89578635) * distinct_row_frac) * g_deg_std)                                                        | 0.2411 | 0.6213 |  0.8011 | 0.0306 |          |
| optimum − lb_best | structure                        |           16 |       0.2378 | square(g_deg_std * square(distinct_row_frac * (-0.8262539 + ((rig_edge_prob * square(distinct_row_frac)) * g_components)))) / 0.6172685                                             | 0.2378 | 0.5783 |  0.7955 | 0.0362 |          |
| optimum − lb_best | structure                        |           18 |       0.2369 | square(g_deg_std * square(distinct_row_frac * ((distinct_col_frac * -0.8262539) + ((square(distinct_row_frac) * g_components) * rig_edge_prob)))) / 0.6172685                       | 0.2373 | 0.5773 |  0.7955 | 0.0362 |          |
| optimum − lb_best | structure                        |           20 |       0.2369 | square((distinct_col_frac * g_deg_std) * square(distinct_row_frac * ((distinct_col_frac * -0.8262539) + ((square(distinct_row_frac) * g_components) * rig_edge_prob)))) / 0.6172685 | 0.2373 | 0.5771 |  0.7955 | 0.0362 |          |

_400 s total._
