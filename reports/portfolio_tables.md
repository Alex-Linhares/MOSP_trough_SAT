# Relabelling portfolio tables (`python -m learning.relabel_portfolio --stage tables`)


Rows: 26,724 calls on 1,572 instances, 17 labellings each, configuration `csearch`.


## Audit: status at optimum − 1 by source

| source   |   unknown |   unsat |
|:---------|----------:|--------:|
| campaign |        19 |   23237 |
| corpus   |         8 |    3460 |

## Audit: status at the optimum by source

| source   |   sat |
|:---------|------:|
| campaign | 23256 |
| corpus   |  3468 |

Witnesses simulating above the optimum: 0.

## Refutation (optimum − 1): speed-up of min-of-k, every instance

| band          |   instances |   identity nodes median |   censored |   max/min median |   max/min p90 |   MAD log10 |   min-of-2 vs identity median |   min-of-2 vs identity p90 |   min-of-4 vs identity median |   min-of-4 vs identity p90 |   min-of-8 vs identity median |   min-of-8 vs identity p90 |   min-of-16 vs identity median |   min-of-16 vs identity p90 |   min-of-8 vs median labelling median | min-of-8 saves >= 1.5x   |   core efficiency k=16 median |
|:--------------|------------:|------------------------:|-----------:|-----------------:|--------------:|------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|-------------------------------:|----------------------------:|--------------------------------------:|:-------------------------|------------------------------:|
| campaign n=40 |         288 |               72        |          0 |             1    |          1.14 |     0.00389 |                             1 |                       1.03 |                          1    |                       1.05 |                          1    |                       1.06 |                           1    |                        1.07 |                                  1    | 0 (0.0%)                 |                        0.0625 |
| campaign n=50 |         360 |              891        |          0 |             1.02 |          1.16 |     0.00558 |                             1 |                       1.05 |                          1    |                       1.06 |                          1    |                       1.08 |                           1.01 |                        1.1  |                                  1.01 | 0 (0.0%)                 |                        0.063  |
| campaign n=60 |         360 |                3.48e+03 |          0 |             1.02 |          1.14 |     0.00485 |                             1 |                       1.03 |                          1    |                       1.04 |                          1    |                       1.06 |                           1    |                        1.07 |                                  1.01 | 1 (0.3%)                 |                        0.0628 |
| campaign n=75 |         360 |                2.79e+04 |          2 |             1.01 |          1.15 |     0.00512 |                             1 |                       1.03 |                          1    |                       1.04 |                          1    |                       1.06 |                           1    |                        1.08 |                                  1    | 0 (0.0%)                 |                        0.0627 |
| corpus 50     |         120 |              620        |          0 |             1.05 |          1.13 |     0.00518 |                             1 |                       1.05 |                          1.01 |                       1.06 |                          1.01 |                       1.08 |                           1.02 |                        1.09 |                                  1.02 | 0 (0.0%)                 |                        0.0636 |
| corpus 60–82  |          33 |                3.7e+04  |          0 |             1.02 |          1.11 |     0.00394 |                             1 |                       1.05 |                          1    |                       1.06 |                          1    |                       1.07 |                           1.01 |                        1.08 |                                  1.01 | 0 (0.0%)                 |                        0.0628 |
| corpus 99–100 |          51 |                4.4e+05  |          1 |             1.01 |          1.26 |     0.00661 |                             1 |                       1.02 |                          1    |                       1.04 |                          1    |                       1.06 |                           1    |                        1.08 |                                  1    | 0 (0.0%)                 |                        0.0626 |

## Refutation: instances whose identity refutation costs ≥ 10,000 nodes

| band          |   instances |   identity nodes median |   censored |   max/min median |   max/min p90 |   MAD log10 |   min-of-2 vs identity median |   min-of-2 vs identity p90 |   min-of-4 vs identity median |   min-of-4 vs identity p90 |   min-of-8 vs identity median |   min-of-8 vs identity p90 |   min-of-16 vs identity median |   min-of-16 vs identity p90 |   min-of-8 vs median labelling median | min-of-8 saves >= 1.5x   |   core efficiency k=16 median |
|:--------------|------------:|------------------------:|-----------:|-----------------:|--------------:|------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|-------------------------------:|----------------------------:|--------------------------------------:|:-------------------------|------------------------------:|
| campaign n=40 |           3 |                1.35e+04 |          0 |             1.19 |          1.29 |     0.0195  |                          1.04 |                       1.11 |                          1.07 |                       1.15 |                          1.09 |                       1.17 |                           1.12 |                        1.2  |                                  1.09 | 0 (0.0%)                 |                        0.0697 |
| campaign n=50 |          49 |                2.57e+04 |          0 |             1.07 |          1.13 |     0.00659 |                          1.01 |                       1.07 |                          1.02 |                       1.09 |                          1.02 |                       1.1  |                           1.02 |                        1.11 |                                  1.03 | 0 (0.0%)                 |                        0.064  |
| campaign n=60 |         131 |                4e+04    |          0 |             1.04 |          1.14 |     0.00578 |                          1    |                       1.03 |                          1.01 |                       1.04 |                          1.01 |                       1.05 |                           1.02 |                        1.07 |                                  1.02 | 0 (0.0%)                 |                        0.0636 |
| campaign n=75 |         201 |                2.12e+05 |          2 |             1.03 |          1.19 |     0.00703 |                          1    |                       1.04 |                          1    |                       1.05 |                          1.01 |                       1.09 |                           1.01 |                        1.1  |                                  1.01 | 0 (0.0%)                 |                        0.0633 |
| corpus 50     |          23 |                2.91e+04 |          0 |             1.09 |          1.11 |     0.00686 |                          1.02 |                       1.05 |                          1.03 |                       1.07 |                          1.04 |                       1.08 |                           1.05 |                        1.09 |                                  1.03 | 0 (0.0%)                 |                        0.0656 |
| corpus 60–82  |          18 |                6.85e+05 |          0 |             1.02 |          1.11 |     0.00476 |                          1    |                       1.05 |                          1.01 |                       1.06 |                          1.01 |                       1.07 |                           1.01 |                        1.07 |                                  1.01 | 0 (0.0%)                 |                        0.0633 |
| corpus 99–100 |          39 |                1.97e+06 |          1 |             1.02 |          1.3  |     0.00864 |                          1    |                       1.03 |                          1    |                       1.07 |                          1.01 |                       1.08 |                           1.01 |                        1.09 |                                  1.01 | 0 (0.0%)                 |                        0.0631 |

## Witness search (optimum): speed-up of min-of-k, every instance

| band          |   instances |   identity nodes median |   censored |   max/min median |   max/min p90 |   MAD log10 |   min-of-2 vs identity median |   min-of-2 vs identity p90 |   min-of-4 vs identity median |   min-of-4 vs identity p90 |   min-of-8 vs identity median |   min-of-8 vs identity p90 |   min-of-16 vs identity median |   min-of-16 vs identity p90 |   min-of-8 vs median labelling median | min-of-8 saves >= 1.5x   |   core efficiency k=16 median |
|:--------------|------------:|------------------------:|-----------:|-----------------:|--------------:|------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|-------------------------------:|----------------------------:|--------------------------------------:|:-------------------------|------------------------------:|
| campaign n=40 |         288 |               12        |          0 |             1.2  |          7.04 |      0.0735 |                          1    |                       1.59 |                          1    |                       2.08 |                          1.01 |                       2.59 |                           1.04 |                        2.8  |                                  1.05 | 54 (18.8%)               |                        0.0652 |
| campaign n=50 |         360 |               27        |          0 |             1.66 |         20.8  |      0.134  |                          1.02 |                       2.26 |                          1.08 |                       3.58 |                          1.14 |                       4.85 |                           1.16 |                        5.8  |                                  1.17 | 111 (30.8%)              |                        0.0726 |
| campaign n=60 |         360 |               44.5      |          0 |             1.75 |         81.7  |      0.175  |                          1.03 |                       3.2  |                          1.09 |                       7.21 |                          1.13 |                      11    |                           1.17 |                       14    |                                  1.17 | 117 (32.5%)              |                        0.0729 |
| campaign n=75 |         360 |              183        |          0 |             2.64 |        542    |      0.25   |                          1.01 |                       2.71 |                          1.06 |                       6.34 |                          1.12 |                      14.8  |                           1.17 |                       35.9  |                                  1.26 | 136 (37.8%)              |                        0.0729 |
| corpus 50     |         120 |               33.5      |          0 |             2.1  |         19.3  |      0.13   |                          1    |                       1.9  |                          1.09 |                       2.61 |                          1.14 |                       4.18 |                           1.17 |                        5.34 |                                  1.27 | 43 (35.8%)               |                        0.0729 |
| corpus 60–82  |          33 |              160        |          0 |             2.02 |        312    |      0.197  |                          1.03 |                       1.83 |                          1.07 |                       3.62 |                          1.1  |                       5.12 |                           1.14 |                        6.13 |                                  1.3  | 10 (30.3%)               |                        0.0714 |
| corpus 99–100 |          51 |                6.81e+03 |          0 |             1.69 |         96.8  |      0.17   |                          1    |                       2.22 |                          1.03 |                       5.5  |                          1.07 |                      12.3  |                           1.08 |                       21    |                                  1.14 | 11 (21.6%)               |                        0.0673 |

## Witness search: identity ≥ 10,000 nodes

| band          |   instances |   identity nodes median |   censored |   max/min median |   max/min p90 |   MAD log10 |   min-of-2 vs identity median |   min-of-2 vs identity p90 |   min-of-4 vs identity median |   min-of-4 vs identity p90 |   min-of-8 vs identity median |   min-of-8 vs identity p90 |   min-of-16 vs identity median |   min-of-16 vs identity p90 |   min-of-8 vs median labelling median | min-of-8 saves >= 1.5x   |   core efficiency k=16 median |
|:--------------|------------:|------------------------:|-----------:|-----------------:|--------------:|------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|------------------------------:|---------------------------:|-------------------------------:|----------------------------:|--------------------------------------:|:-------------------------|------------------------------:|
| campaign n=50 |           2 |                2.09e+04 |          0 |           324    |    581        |       0.278 |                          1.93 |                       2.49 |                          3.56 |                       5.17 |                          8.66 |                       14.2 |                         174    |                         312 |                                  5.36 | 2 (100.0%)               |                       10.9    |
| campaign n=60 |          25 |                1.8e+04  |          0 |             8.06 |      1.46e+03 |       0.356 |                          3.2  |                       5.36 |                          6.01 |                      21.5  |                          7.39 |                      225   |                           8.01 |                         592 |                                  2.44 | 18 (72.0%)               |                        0.501  |
| campaign n=75 |          67 |                5.11e+04 |          0 |            34.8  |      4.48e+03 |       0.425 |                          1.58 |                       6.43 |                          2.91 |                      32.4  |                          6.01 |                      177   |                          13.1  |                         695 |                                  4.32 | 51 (76.1%)               |                        0.82   |
| corpus 60–82  |           8 |                9.03e+04 |          0 |             5.61 |      4.12e+03 |       0.331 |                          1.51 |                       2.29 |                          2.61 |                       4.83 |                          3.97 |                       31.6 |                           4.25 |                         456 |                                  2.57 | 6 (75.0%)                |                        0.266  |
| corpus 99–100 |          23 |                4.8e+04  |          0 |             6.16 |    505        |       0.271 |                          1    |                       3.52 |                          1.03 |                       7.92 |                          1.2  |                       27   |                           1.28 |                         274 |                                  1.98 | 7 (30.4%)                |                        0.0802 |

## Growth of the median min-of-16 refutation speed-up with n (campaign)

- every instance: {40: 1.0, 50: 1.007746625319483, 60: 1.0049522926340912, 75: 1.00310812543129}, slope 0.0000 log10 per customer, at 100: 1.01×, at 125: 1.01×
- identity ≥ 10,000 nodes: {40: 1.115381443298969, 50: 1.0246618933969769, 60: 1.017751479289941, 75: 1.0120336943441637}, slope -0.0011, at 100: 0.94×, at 125: 0.88×

## Kill criterion (median min-of-8 refutation speed-up at n ≥ 60 under 1.5×)

- instances: 804
- median_all: 1.0028785847066528
- hard_instances: 389
- median_hard: 1.0093743373318032
- threshold: 1.5
- kill_met_all: True
- kill_met_hard: True

## Does a cheap statistic of a labelling predict its refutation cost? (instances with max/min ≥ 1.5)

| statistic                          |   instances |   mean Spearman with nodes | |rho| >= 0.5   |   choose smallest: median speed-up |   choose largest: median speed-up |
|:-----------------------------------|------------:|---------------------------:|:---------------|-----------------------------------:|----------------------------------:|
| rho_index_degree                   |           8 |                    -0.13   | 0%             |                              0.946 |                             1.11  |
| rho_index_rows                     |           8 |                    -0.0871 | 0%             |                              0.988 |                             1.07  |
| rho_col_index_sum                  |           8 |                    -0.0277 | 12%            |                              1.04  |                             1.02  |
| deg_first                          |           8 |                    -0.186  | 0%             |                              1     |                             1.12  |
| root_choice_nbr_deg                |           5 |                     0.331  | 20%            |                              1.15  |                             0.976 |
| root_choice_index                  |           8 |                     0.0537 | 12%            |                              0.891 |                             0.967 |
| nodes_hi                           |           8 |                     0.129  | 25%            |                              1.08  |                             1.1   |
| (reference) one random relabelling |           8 |                   nan      |                |                              1.01  |                           nan     |
| (reference) min-of-2               |           8 |                   nan      |                |                              1.09  |                           nan     |
| (reference) min-of-4               |           8 |                   nan      |                |                              1.19  |                           nan     |

## The fifteen widest spreads (refutation)

| base_name                 |   n |   m |   optimum |   identity |        min |        max |   max_over_min |   identity_over_min |   speedup_identity_8 | censored_any   |
|:--------------------------|----:|----:|----------:|-----------:|-----------:|-----------:|---------------:|--------------------:|---------------------:|:---------------|
| ens_f_n75_m75_d3_i025     |  75 |  75 |        20 |   1.86e+07 |   1.63e+07 |   3.48e+07 |           2.14 |               1.15  |                1.11  | False          |
| ens_f_n60_m30_d2_i026     |  60 |  30 |         7 |   1.1e+03  | 539        |   1.04e+03 |           1.93 |               2.04  |                1.88  | False          |
| Random-100-50-4-2_0       | 100 |  50 |        29 |   3.93e+07 |   4.14e+07 |   7.48e+07 |           1.81 |               0.95  |                0.9   | False          |
| ens_f_n75_m150_d2_i036    |  75 | 150 |        14 |   5.83e+07 |   4.59e+07 |   7.32e+07 |           1.6  |               1.27  |                1.2   | False          |
| p1050n2_0                 |  50 |  10 |         9 |  50        |  34        |  54        |           1.57 |               1.46  |                1.39  | False          |
| Random-100-50-4-4_0       | 100 |  50 |        24 |   2.41e+08 |   1.6e+08  |   2.47e+08 |           1.55 |               1.51  |                1.48  | True           |
| ens_b_n50_m50_p0.025_i001 |  50 |  50 |         8 | 400        | 270        | 416        |           1.54 |               1.48  |                1.44  | False          |
| ens_b_n60_m30_p0.025_i032 |  60 |  30 |         6 |  68        |  53        |  81        |           1.52 |               1.28  |                1.17  | False          |
| ens_f_n75_m75_d2_i006     |  75 |  75 |         6 |   1.36e+04 |   1.04e+04 |   1.56e+04 |           1.5  |               1.3   |                1.2   | False          |
| ens_f_n60_m30_d2_i004     |  60 |  30 |         5 | 595        | 427        | 633        |           1.48 |               1.39  |                1.38  | False          |
| ens_f_n75_m75_d2_i043     |  75 |  75 |         7 |   5.85e+04 |   6.27e+04 |   9.29e+04 |           1.48 |               0.932 |                0.919 | False          |
| ens_b_n60_m30_p0.05_i030  |  60 |  30 |         9 |   1.24e+04 |   1.14e+04 |   1.69e+04 |           1.47 |               1.08  |                1.07  | False          |
| ens_f_n50_m50_d2_i043     |  50 |  50 |         5 |   1.71e+03 |   1.5e+03  |   2.2e+03  |           1.47 |               1.14  |                1.07  | False          |
| ens_f_n75_m150_d2_i023    |  75 | 150 |        14 |   1.43e+07 |   1.05e+07 |   1.53e+07 |           1.46 |               1.37  |                1.34  | False          |
| ens_f_n75_m150_d2_i017    |  75 | 150 |        15 |   1.49e+08 |   1.32e+08 |   1.93e+08 |           1.46 |               1.13  |                1.09  | True           |

## The race: the 16-way portfolio on the censored `Random-100-100-2` instances

| instance             |   k | identity §14               |   ways | early stop   | winner   |   winner nodes |   wall (s) |   labellings finished |   finished unsat | wall speed-up vs identity   | core cost (ways × wall) / identity s   |   finished max/min nodes |
|:---------------------|----:|:---------------------------|-------:|:-------------|:---------|---------------:|-----------:|----------------------:|-----------------:|:----------------------------|:---------------------------------------|-------------------------:|
| Random-100-100-2-4_0 |  14 | 9.31e+07 nodes, 37 s       |     16 | False        | relabel6 |        6.3e+08 |        600 |                    16 |                3 | 0.06×                       | 260.34                                 |                     1.99 |
| Random-100-100-2-1_0 |  23 | ≥ 2.06e+09 nodes, ≥ 1500 s |     16 | True         | nan      |      nan       |        600 |                    16 |                0 | —                           | —                                      |                   nan    |
| Random-100-100-2-3_0 |  22 | ≥ 2.64e+09 nodes, ≥ 1500 s |     16 | True         | nan      |      nan       |        600 |                    16 |                0 | —                           | —                                      |                   nan    |
| Random-100-100-2-5_0 |  18 | ≥ 2.63e+09 nodes, ≥ 1500 s |     16 | True         | nan      |      nan       |        600 |                    16 |                0 | —                           | —                                      |                   nan    |

### Every labelling that returned

| base_name            | labelling   | status   |    nodes |   seconds |   wall_at_return |
|:---------------------|:------------|:---------|---------:|----------:|-----------------:|
| Random-100-100-2-4_0 | relabel6    | unsat    | 6.3e+08  |       287 |              287 |
| Random-100-100-2-4_0 | relabel12   | unsat    | 6.84e+08 |       318 |              318 |
| Random-100-100-2-4_0 | relabel7    | unsat    | 1.25e+09 |       503 |              503 |
| Random-100-100-2-4_0 | relabel5    | unknown  | 1.55e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel3    | unknown  | 1.72e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel0    | unknown  | 1.39e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel1    | unknown  | 1.64e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel11   | unknown  | 1.36e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel2    | unknown  | 1.57e+09 |       600 |              600 |
| Random-100-100-2-4_0 | identity    | unknown  | 1.39e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel10   | unknown  | 1.44e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel9    | unknown  | 1.81e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel8    | unknown  | 1.52e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel4    | unknown  | 9.93e+08 |       600 |              600 |
| Random-100-100-2-4_0 | relabel13   | unknown  | 1.61e+09 |       600 |              600 |
| Random-100-100-2-4_0 | relabel14   | unknown  | 1.58e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel8    | unknown  | 1.08e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel3    | unknown  | 7.45e+08 |       600 |              600 |
| Random-100-100-2-1_0 | identity    | unknown  | 1.15e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel5    | unknown  | 9.32e+08 |       600 |              600 |
| Random-100-100-2-1_0 | relabel13   | unknown  | 8.86e+08 |       600 |              600 |
| Random-100-100-2-1_0 | relabel14   | unknown  | 1.14e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel7    | unknown  | 1.06e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel11   | unknown  | 7.66e+08 |       600 |              600 |
| Random-100-100-2-1_0 | relabel4    | unknown  | 1.06e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel2    | unknown  | 1.14e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel1    | unknown  | 1.04e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel10   | unknown  | 1.12e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel12   | unknown  | 9.03e+08 |       600 |              600 |
| Random-100-100-2-1_0 | relabel6    | unknown  | 7.17e+08 |       600 |              600 |
| Random-100-100-2-1_0 | relabel9    | unknown  | 1.15e+09 |       600 |              600 |
| Random-100-100-2-1_0 | relabel0    | unknown  | 1.02e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel11   | unknown  | 1.23e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel6    | unknown  | 1.08e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel9    | unknown  | 1.17e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel1    | unknown  | 1.08e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel5    | unknown  | 8.02e+08 |       600 |              600 |
| Random-100-100-2-3_0 | relabel8    | unknown  | 1.09e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel0    | unknown  | 1.27e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel2    | unknown  | 8.14e+08 |       600 |              600 |
| Random-100-100-2-3_0 | relabel10   | unknown  | 1.26e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel3    | unknown  | 1.29e+09 |       600 |              600 |
| Random-100-100-2-3_0 | identity    | unknown  | 1.11e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel12   | unknown  | 8.36e+08 |       600 |              600 |
| Random-100-100-2-3_0 | relabel4    | unknown  | 8.62e+08 |       600 |              600 |
| Random-100-100-2-3_0 | relabel7    | unknown  | 1.18e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel13   | unknown  | 1.31e+09 |       600 |              600 |
| Random-100-100-2-3_0 | relabel14   | unknown  | 1.17e+09 |       600 |              600 |
| Random-100-100-2-5_0 | relabel6    | unknown  | 7.65e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel10   | unknown  | 1e+09    |       600 |              600 |
| Random-100-100-2-5_0 | relabel4    | unknown  | 9.91e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel1    | unknown  | 1.06e+09 |       600 |              600 |
| Random-100-100-2-5_0 | relabel12   | unknown  | 7.36e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel5    | unknown  | 1.02e+09 |       600 |              600 |
| Random-100-100-2-5_0 | relabel11   | unknown  | 9.72e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel3    | unknown  | 1.03e+09 |       600 |              600 |
| Random-100-100-2-5_0 | relabel9    | unknown  | 7.56e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel2    | unknown  | 1.09e+09 |       600 |              600 |
| Random-100-100-2-5_0 | identity    | unknown  | 1.03e+09 |       600 |              600 |
| Random-100-100-2-5_0 | relabel7    | unknown  | 7.41e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel8    | unknown  | 7.89e+08 |       600 |              600 |
| Random-100-100-2-5_0 | relabel0    | unknown  | 1.1e+09  |       600 |              600 |
| Random-100-100-2-5_0 | relabel13   | unknown  | 1.04e+09 |       600 |              600 |
| Random-100-100-2-5_0 | relabel14   | unknown  | 1.06e+09 |       600 |              600 |

## Projection: the 125 × 125 ridge on 16 cores

| instance / class                 |    nodes |   identity hours (1 core) |   portfolio hours, min-of-16 at n=75 (hard, measured) |   portfolio hours, min-of-16 extrapolated to 125 |   portfolio hours, race wall speed-up at n=100 (median, ≥ where censored) |
|:---------------------------------|---------:|--------------------------:|------------------------------------------------------:|-------------------------------------------------:|--------------------------------------------------------------------------:|
| Random-125-125-4-5_0 (recertify) | 4.89e+10 |                     10.2  |                                                 10    |                                            11.5  |                                                                       169 |
| Random-125-125-4-2_0 (recertify) | 6.08e+10 |                     13.3  |                                                 13.1  |                                            15.1  |                                                                       221 |
| Random-125-125-2-1_0 (recertify) | 1.62e+11 |                     25    |                                                 24.7  |                                            28.4  |                                                                       417 |
| Random-125-125-2-4_0 (recertify) | 1.68e+11 |                     28.3  |                                                 27.9  |                                            32.1  |                                                                       471 |
| Random-125-125-4-4_0 (recertify) | 2.6e+11  |                     53.5  |                                                 52.9  |                                            60.8  |                                                                       892 |
| Random-125-125-2 (§16)           | 1.5e+11  |                     22.9  |                                                 22.6  |                                            26    |                                                                       382 |
| Random-125-125-4 (§16)           | 4e+10    |                      6.11 |                                                  6.04 |                                             6.94 |                                                                       102 |
