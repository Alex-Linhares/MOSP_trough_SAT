# Extremal search and exact treewidth — tables (loop0003 item 08)

*Regenerate: `python -m learning.extremal --stage tables`. 1431 search jobs, 727,816 oracle evaluations, 30,151,809 canonical duplicates skipped, 2.73 core-hours.*

## Kill test: the search's best against the corpus's worst at the same n

| objective   |   n |   search best | corpus worst   | beats corpus       |   corpus instances |   evaluations |
|:------------|----:|--------------:|:---------------|:-------------------|-------------------:|--------------:|
| disagree    |   8 |             0 | —              | no corpus instance |                  0 |          1367 |
| disagree    |   9 |             0 | 0              | no                 |                 10 |          1827 |
| disagree    |  10 |             0 | 0              | no                 |               1604 |          2216 |
| disagree    |  11 |             0 | —              | no corpus instance |                  0 |          2725 |
| disagree    |  12 |             0 | —              | no corpus instance |                  0 |          3308 |
| disagree    |  13 |             0 | 0              | no                 |                  1 |          3919 |
| disagree    |  14 |             0 | 0              | no                 |                  3 |          4599 |
| disagree    |  15 |             0 | 0              | no                 |               1194 |          5622 |
| gap         |   8 |             1 | —              | no corpus instance |                  0 |          1703 |
| gap         |   9 |             1 | 1              | no                 |                 10 |          2173 |
| gap         |  10 |             1 | 1              | no                 |               1604 |          2859 |
| gap         |  11 |             1 | —              | no corpus instance |                  0 |          3506 |
| gap         |  12 |             2 | —              | no corpus instance |                  0 |          4997 |
| gap         |  13 |             1 | 0              | yes                |                  1 |          6375 |
| gap         |  14 |             2 | 1              | yes                |                  3 |          7449 |
| gap         |  15 |             2 | 1              | yes                |               1194 |          7858 |
| nodes       |   8 |            14 | —              | no corpus instance |                  0 |          4076 |
| nodes       |   9 |            21 | 6              | yes                |                 10 |          5620 |
| nodes       |  10 |            37 | 15             | yes                |               1604 |          7068 |
| nodes       |  11 |            53 | —              | no corpus instance |                  0 |          8993 |
| nodes       |  12 |            63 | —              | no corpus instance |                  0 |         10621 |
| nodes       |  13 |           114 | 1              | yes                |                  1 |         12612 |
| nodes       |  14 |           132 | 11             | yes                |                  3 |         12357 |
| nodes       |  15 |           209 | 57             | yes                |               1194 |         14520 |
| overshoot   |   8 |             2 | —              | no corpus instance |                  0 |          2339 |
| overshoot   |   9 |             2 | 0              | yes                |                 10 |          3453 |
| overshoot   |  10 |             2 | 1              | yes                |               1604 |          4170 |
| overshoot   |  11 |             3 | —              | no corpus instance |                  0 |          5201 |
| overshoot   |  12 |             3 | —              | no corpus instance |                  0 |          6461 |
| overshoot   |  13 |             3 | 0              | yes                |                  1 |          7271 |
| overshoot   |  14 |             3 | 2              | yes                |                  3 |          8453 |
| overshoot   |  15 |             4 | 2              | yes                |               1194 |          9506 |
| pwtw        |   7 |             1 | —              | no corpus instance |                  0 |         12464 |
| pwtw        |   8 |             1 | —              | no corpus instance |                  0 |         79424 |
| pwtw        |   9 |             1 | 1              | no                 |                 10 |        128127 |
| pwtw        |  10 |             2 | 1              | yes                |               1604 |        129153 |
| pwtw        |  11 |             2 | —              | no corpus instance |                  0 |         82136 |
| pwtw        |  12 |             1 | —              | no corpus instance |                  0 |         34932 |
| pwtw        |  13 |             2 | 0              | yes                |                  1 |          6775 |
| pwtw        |  14 |             2 | 1              | yes                |                  3 |          7566 |
| pwtw        |  15 |             2 | 1              | yes                |               1194 |          8716 |
| pwtw        |  16 |             2 | —              | no corpus instance |                  0 |          9036 |
| pwtw        |  17 |             2 | 1              | yes                |                  3 |         10522 |
| pwtw        |  18 |             2 | 1              | yes                |                  4 |         10928 |
| pwtw        |  19 |             2 | 2              | no                 |                  5 |         11256 |
| pwtw        |  20 |             2 | 2              | no                 |               1298 |         11557 |

## Per objective and n: the best instance drawn

| objective   |   n |   n_active |   value | kind   |   m |   ones |   edges |   optimum |   lb_best |   tw |   nodes_default |   ub_cs_dfs |   disagree |   evaluations |   skipped |
|:------------|----:|-----------:|--------:|:-------|----:|-------:|--------:|----------:|----------:|-----:|----------------:|------------:|-----------:|--------------:|----------:|
| disagree    |   8 |          3 |       0 | toc    |   4 |      3 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          1367 |     21712 |
| disagree    |   9 |          6 |       0 | bern   |   9 |      8 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          1827 |     21259 |
| disagree    |  10 |          4 |       0 | toc    |   7 |      5 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          2216 |     20864 |
| disagree    |  11 |          4 |       0 | toc    |   6 |      5 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          2725 |     20345 |
| disagree    |  12 |          5 |       0 | toc    |   7 |      5 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          3308 |     19751 |
| disagree    |  13 |          6 |       0 | toc    |   7 |      7 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          3919 |     19126 |
| disagree    |  14 |         10 |       0 | bern   |  14 |     14 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          4599 |     18447 |
| disagree    |  15 |          7 |       0 | toc    |   8 |      8 |       0 |         1 |         1 |    0 |               0 |           1 |          0 |          5622 |     17396 |
| gap         |   8 |          7 |       1 | bern   |   8 |     17 |       9 |         4 |         3 |    2 |               4 |           4 |          0 |          1703 |     21395 |
| gap         |   9 |          8 |       1 | bern   |  13 |     19 |       6 |         3 |         2 |    1 |               7 |           3 |          0 |          2173 |     20926 |
| gap         |  10 |          6 |       1 | toc    |   6 |     10 |       9 |         4 |         3 |    2 |               3 |           4 |          0 |          2859 |     20221 |
| gap         |  11 |          7 |       1 | toc    |   6 |     10 |       9 |         4 |         3 |    2 |               4 |           4 |          0 |          3506 |     19576 |
| gap         |  12 |         11 |       2 | toc    |   6 |     19 |      28 |         7 |         5 |    5 |              10 |           7 |          0 |          4997 |     18062 |
| gap         |  13 |          8 |       1 | corpus |   9 |     16 |       9 |         4 |         3 |    2 |               5 |           4 |          0 |          6375 |     16659 |
| gap         |  14 |         11 |       2 | toc    |   6 |     18 |      28 |         7 |         5 |    5 |               7 |           7 |          0 |          7449 |     15598 |
| gap         |  15 |         11 |       2 | toc    |   8 |     20 |      28 |         7 |         5 |    5 |               7 |           7 |          0 |          7858 |     15156 |
| nodes       |   8 |          8 |      14 | bern   |  12 |     26 |      12 |         4 |         4 |    3 |              14 |           4 |          0 |          4076 |     19030 |
| nodes       |   9 |          9 |      21 | bern   |   9 |     19 |      12 |         4 |         4 |    3 |              21 |           4 |          0 |          5620 |     17450 |
| nodes       |  10 |         10 |      37 | bern   |  10 |     23 |      15 |         4 |         4 |    3 |              37 |           4 |          0 |          7068 |     15971 |
| nodes       |  11 |         11 |      53 | corpus |   9 |     24 |      21 |         5 |         5 |    4 |              53 |           5 |          0 |          8993 |     14020 |
| nodes       |  12 |         12 |      63 | bern   |  12 |     29 |      22 |         6 |         6 |    5 |              63 |           6 |          0 |         10621 |     12375 |
| nodes       |  13 |         13 |     114 | corpus |  10 |     28 |      28 |         6 |         6 |    5 |             114 |           6 |          0 |         12612 |     10359 |
| nodes       |  14 |         14 |     132 | corpus |  10 |     26 |      26 |         6 |         5 |    4 |             132 |           6 |          0 |         12357 |     10619 |
| nodes       |  15 |         15 |     209 | corpus |  10 |     29 |      33 |         7 |         7 |    6 |             209 |           7 |          0 |         14520 |      8408 |
| overshoot   |   8 |          8 |       2 | corpus |   9 |     16 |       6 |         2 |         2 |    1 |               1 |           4 |          0 |          2339 |     20767 |
| overshoot   |   9 |          7 |       2 | toc    |   8 |     13 |       6 |         2 |         2 |    1 |               0 |           4 |          0 |          3453 |     19638 |
| overshoot   |  10 |          8 |       2 | bern   |  10 |     16 |       6 |         2 |         2 |    1 |               1 |           4 |          0 |          4170 |     18926 |
| overshoot   |  11 |         11 |       3 | corpus |  10 |     20 |      13 |         3 |         3 |    2 |               3 |           6 |          0 |          5201 |     17871 |
| overshoot   |  12 |         11 |       3 | corpus |  10 |     18 |       8 |         2 |         2 |    1 |               1 |           5 |          0 |          6461 |     16583 |
| overshoot   |  13 |         11 |       3 | corpus |   9 |     19 |      13 |         3 |         3 |    2 |               4 |           6 |          0 |          7271 |     15792 |
| overshoot   |  14 |         11 |       3 | corpus |  10 |     24 |      14 |         3 |         3 |    2 |               2 |           6 |          0 |          8453 |     14569 |
| overshoot   |  15 |         15 |       4 | bern   |  22 |     53 |      35 |         6 |         6 |    5 |              31 |          10 |          0 |          9506 |     13507 |
| pwtw        |   7 |          7 |       1 | bern   |   7 |     13 |       6 |         3 |         3 |    1 |               6 |           3 |          0 |         12464 |   1683091 |
| pwtw        |   8 |          7 |       1 | bern   |  12 |     18 |       6 |         3 |         2 |    1 |               6 |           3 |          0 |         79424 |   7121868 |
| pwtw        |   9 |          8 |       1 | corpus |   9 |     15 |       6 |         3 |         2 |    1 |               7 |           3 |          0 |        128127 |   8480117 |
| pwtw        |  10 |         10 |       2 | corpus |   9 |     23 |      21 |         6 |         5 |    3 |              10 |           6 |          0 |        129153 |   7430092 |
| pwtw        |  11 |         11 |       2 | corpus |  10 |     24 |      21 |         6 |         5 |    3 |              15 |           6 |          0 |         82136 |   3174840 |
| pwtw        |  12 |          8 |       1 | corpus |  10 |     16 |       6 |         3 |         2 |    1 |               7 |           3 |          0 |         34932 |   1601814 |
| pwtw        |  13 |         11 |       2 | corpus |  10 |     24 |      21 |         6 |         4 |    3 |              15 |           6 |          0 |          6775 |     16261 |
| pwtw        |  14 |         11 |       2 | corpus |  10 |     24 |      21 |         6 |         4 |    3 |              11 |           6 |          0 |          7566 |     15466 |
| pwtw        |  15 |         14 |       2 | toc    |   8 |     23 |      33 |         7 |         5 |    4 |              18 |           7 |          0 |          8716 |     14301 |
| pwtw        |  16 |         13 |       2 | corpus |  10 |     27 |      29 |         7 |         5 |    4 |              31 |           7 |          0 |          9036 |     13967 |
| pwtw        |  17 |         14 |       2 | toc    |  12 |     25 |      22 |         6 |         4 |    3 |              13 |           6 |          0 |         10522 |     12456 |
| pwtw        |  18 |         14 |       2 | corpus |  10 |     28 |      27 |         6 |         4 |    3 |              20 |           6 |          0 |         10928 |     12048 |
| pwtw        |  19 |         12 |       2 | corpus |  10 |     24 |      21 |         6 |         4 |    3 |              16 |           6 |          0 |         11256 |     11702 |
| pwtw        |  20 |         14 |       2 | toc    |  12 |     25 |      24 |         6 |         4 |    3 |              14 |           6 |          0 |         11557 |     11408 |

## Re-certification of every drawn instance

| objective   |   n |   optimum | lo_default   | hi_default   | lo_csearch   | hi_csearch   | lattice   | pathwidth_dp   |   tw |   tw_order_width | agree   |
|:------------|----:|----------:|:-------------|:-------------|:-------------|:-------------|:----------|:---------------|-----:|-----------------:|:--------|
| disagree    |   8 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |   9 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |  10 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |  11 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |  12 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |  13 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |  14 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| disagree    |  15 |         1 | unsat        | sat          | unsat        | sat          | 1         | 0              |    0 |                0 | True    |
| gap         |   8 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    2 |                2 | True    |
| gap         |   9 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    1 |                1 | True    |
| gap         |  10 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    2 |                2 | True    |
| gap         |  11 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    2 |                2 | True    |
| gap         |  12 |         7 | unsat        | sat          | unsat        | sat          | 7         | 6              |    5 |                5 | True    |
| gap         |  13 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    2 |                2 | True    |
| gap         |  14 |         7 | unsat        | sat          | unsat        | sat          | 7         | 6              |    5 |                5 | True    |
| gap         |  15 |         7 | unsat        | sat          | unsat        | sat          | 7         | 6              |    5 |                5 | True    |
| nodes       |   8 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    3 |                3 | True    |
| nodes       |   9 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    3 |                3 | True    |
| nodes       |  10 |         4 | unsat        | sat          | unsat        | sat          | 4         | 3              |    3 |                3 | True    |
| nodes       |  11 |         5 | unsat        | sat          | unsat        | sat          | 5         | 4              |    4 |                4 | True    |
| nodes       |  12 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    5 |                5 | True    |
| nodes       |  13 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    5 |                5 | True    |
| nodes       |  14 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    4 |                4 | True    |
| nodes       |  15 |         7 | unsat        | sat          | unsat        | sat          | 7         | 6              |    6 |                6 | True    |
| overshoot   |   8 |         2 | unsat        | sat          | unsat        | sat          | 2         | 1              |    1 |                1 | True    |
| overshoot   |   9 |         2 | unsat        | sat          | unsat        | sat          | 2         | 1              |    1 |                1 | True    |
| overshoot   |  10 |         2 | unsat        | sat          | unsat        | sat          | 2         | 1              |    1 |                1 | True    |
| overshoot   |  11 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    2 |                2 | True    |
| overshoot   |  12 |         2 | unsat        | sat          | unsat        | sat          | 2         | 1              |    1 |                1 | True    |
| overshoot   |  13 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    2 |                2 | True    |
| overshoot   |  14 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    2 |                2 | True    |
| overshoot   |  15 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    5 |                5 | True    |
| pwtw        |   7 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    1 |                1 | True    |
| pwtw        |   8 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    1 |                1 | True    |
| pwtw        |   9 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    1 |                1 | True    |
| pwtw        |  10 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    3 |                3 | True    |
| pwtw        |  11 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    3 |                3 | True    |
| pwtw        |  12 |         3 | unsat        | sat          | unsat        | sat          | 3         | 2              |    1 |                1 | True    |
| pwtw        |  13 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    3 |                3 | True    |
| pwtw        |  14 |         6 | unsat        | sat          | unsat        | sat          | 6         | 5              |    3 |                3 | True    |
| pwtw        |  15 |         7 | unsat        | sat          | unsat        | sat          | 7         | 6              |    4 |                4 | True    |
| pwtw        |  16 |         7 | unsat        | sat          | unsat        | sat          | —         | 6              |    4 |                4 | True    |
| pwtw        |  17 |         6 | unsat        | sat          | unsat        | sat          | —         | 5              |    3 |                3 | True    |
| pwtw        |  18 |         6 | unsat        | sat          | unsat        | sat          | —         | 5              |    3 |                3 | True    |
| pwtw        |  19 |         6 | unsat        | sat          | unsat        | sat          | —         | —              |    3 |                3 | True    |
| pwtw        |  20 |         6 | unsat        | sat          | unsat        | sat          | —         | —              |    3 |                3 | True    |

## pw − tw by n: search against corpus (exact treewidth)

|   n | search max pw − tw   |   corpus instances (exact tw) | corpus max pw − tw   |   corpus with pw − tw ≥ 1 |   corpus with pw − tw ≥ 2 |
|----:|:---------------------|------------------------------:|:---------------------|--------------------------:|--------------------------:|
|   7 | 1                    |                             0 | —                    |                         0 |                         0 |
|   8 | 1                    |                             0 | —                    |                         0 |                         0 |
|   9 | 1                    |                            10 | 1                    |                         1 |                         0 |
|  10 | 2                    |                          1604 | 1                    |                        34 |                         0 |
|  11 | 2                    |                             0 | —                    |                         0 |                         0 |
|  12 | 1                    |                             0 | —                    |                         0 |                         0 |
|  13 | 2                    |                             1 | 0                    |                         0 |                         0 |
|  14 | 2                    |                             3 | 1                    |                         1 |                         0 |
|  15 | 2                    |                          1194 | 1                    |                        40 |                         0 |
|  16 | 2                    |                             0 | —                    |                         0 |                         0 |
|  17 | 2                    |                             3 | 1                    |                         1 |                         0 |
|  18 | 2                    |                             4 | 1                    |                         1 |                         0 |
|  19 | 2                    |                             5 | 2                    |                         2 |                         1 |
|  20 | 2                    |                          1298 | 2                    |                       157 |                         2 |
|  30 | —                    |                           133 | 2                    |                        76 |                        10 |
|  37 | —                    |                             1 | 0                    |                         0 |                         0 |
|  38 | —                    |                             2 | 1                    |                         1 |                         0 |
|  39 | —                    |                             2 | 0                    |                         0 |                         0 |
|  40 | —                    |                            42 | 2                    |                        33 |                         8 |
|  50 | —                    |                            32 | 3                    |                        27 |                        13 |
|  75 | —                    |                             0 | —                    |                         0 |                         0 |
|  79 | —                    |                             1 | 2                    |                         1 |                         1 |
| 100 | —                    |                             0 | —                    |                         0 |                         0 |
| 105 | —                    |                             0 | —                    |                         0 |                         0 |
| 125 | —                    |                             0 | —                    |                         0 |                         0 |
| 134 | —                    |                             0 | —                    |                         0 |                         0 |

## §6's floor as a number: the gap ≥ 2 corpus instances

| customers   |   gap ≥ 2 instances |   tw exact |   pw > tw |   pw = tw |   open |   pw − tw ≥ 2 |   max pw − tw (exact) |   mean seconds |
|:------------|--------------------:|-----------:|----------:|----------:|-------:|--------------:|----------------------:|---------------:|
| 20–20       |                  17 |         17 |        12 |         5 |      0 |             2 |                     2 |          0.040 |
| 21–30       |                 133 |        133 |        76 |        57 |      0 |            10 |                     2 |          0.300 |
| 31–60       |                 101 |         79 |        71 |        18 |     12 |            21 |                     3 |         10.950 |
| 61–200      |                  87 |          1 |         5 |         0 |     82 |             4 |                     2 |          0.760 |
| all         |                 338 |        230 |       164 |        80 |     94 |            37 |                     3 |          3.590 |

## Every gap ≥ 2 corpus instance with pw − tw ≥ 2 (exact or proved by interval)

| instance_name                                       | source_file                                                           |   n_customers |   optimum |   pw |   tw_lo |   tw_hi | method    |   seconds |
|:----------------------------------------------------|:----------------------------------------------------------------------|--------------:|----------:|-----:|--------:|--------:|:----------|----------:|
| HS problem 551 size 20 10 density  0.20             | benchmarks/instances/ChallengeInstances2005/Simonis/problem_20_10.dat |            20 |         9 |    8 |       6 |       6 | dp        |     0.050 |
| Warwick 871: balanced orders, 4 orders per product  | benchmarks/instances/ChallengeInstances2005/Harvey/wbo_20_10.txt      |            20 |         6 |    5 |       3 |       3 | dp        |     0.044 |
| HS problem 1108 size 30 10 density  0.20            | benchmarks/instances/ChallengeInstances2005/Simonis/problem_30_10.dat |            30 |        15 |   14 |      12 |      12 | bb        |     0.009 |
| HS problem 1121 size 30 10 density  0.20            | benchmarks/instances/ChallengeInstances2005/Simonis/problem_30_10.dat |            30 |        13 |   12 |      10 |      10 | bb        |     0.006 |
| HS problem 1130 size 30 10 density  0.20            | benchmarks/instances/ChallengeInstances2005/Simonis/problem_30_10.dat |            30 |        15 |   14 |      12 |      12 | bb        |     0.008 |
| HS problem 1131 size 30 10 density  0.20            | benchmarks/instances/ChallengeInstances2005/Simonis/problem_30_10.dat |            30 |         9 |    8 |       6 |       6 | bb        |     0.003 |
| HS problem 1135 size 30 10 density  0.20            | benchmarks/instances/ChallengeInstances2005/Simonis/problem_30_10.dat |            30 |        17 |   16 |      14 |      14 | bb        |     0.009 |
| HS problem 1140 size 30 10 density  0.20            | benchmarks/instances/ChallengeInstances2005/Simonis/problem_30_10.dat |            30 |        13 |   12 |      10 |      10 | bb        |     0.007 |
| Random-30-30-2-3_0                                  | benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-30-30-2-3.txt  |            30 |         9 |    8 |       6 |       6 | bb        |     0.003 |
| Warwick 1295: balanced orders, 6 orders per product | benchmarks/instances/ChallengeInstances2005/Harvey/wbo_30_10.txt      |            30 |        12 |   11 |       9 |       9 | bb        |     0.006 |
| Warwick 1296: balanced orders, 6 orders per product | benchmarks/instances/ChallengeInstances2005/Harvey/wbo_30_10.txt      |            30 |        12 |   11 |       9 |       9 | bb        |     0.007 |
| p1530n4_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1530n4.txt  |            30 |         8 |    7 |       5 |       5 | bb        |     0.003 |
| p1540n10_0                                          | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1540n10.txt |            40 |         8 |    7 |       5 |       5 | bb        |     0.005 |
| p1540n1_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1540n1.txt  |            40 |         8 |    7 |       5 |       5 | bb        |     0.006 |
| p1540n3_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1540n3.txt  |            40 |         7 |    6 |       4 |       4 | bb        |     0.005 |
| p1540n5_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1540n5.txt  |            40 |         8 |    7 |       5 |       5 | bb        |     0.005 |
| p1540n9_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1540n9.txt  |            40 |         7 |    6 |       4 |       4 | bb        |     0.005 |
| p2040n2_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2040n2.txt  |            40 |         8 |    7 |       5 |       5 | bb        |     0.006 |
| p2540n2_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2540n2.txt  |            40 |        11 |   10 |       8 |       8 | bb        |     0.035 |
| p2540n5_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2540n5.txt  |            40 |        10 |    9 |       7 |       7 | bb        |     0.009 |
| p1550n10_0                                          | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1550n10.txt |            50 |         8 |    7 |       5 |       5 | bb        |     0.008 |
| p1550n8_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p1550n8.txt  |            50 |         8 |    7 |       5 |       5 | bb        |     0.007 |
| p2050n1_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2050n1.txt  |            50 |         7 |    6 |       4 |       4 | bb        |     0.008 |
| p2050n3_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2050n3.txt  |            50 |         8 |    7 |       5 |       5 | bb        |     0.008 |
| p2050n4_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2050n4.txt  |            50 |         8 |    7 |       5 |       5 | bb        |     0.008 |
| p2050n7_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2050n7.txt  |            50 |         8 |    7 |       5 |       5 | bb        |     0.009 |
| p2050n9_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2050n9.txt  |            50 |        10 |    9 |       6 |       6 | bb        |     0.010 |
| p2550n10_0                                          | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2550n10.txt |            50 |        11 |   10 |       8 |       8 | bb        |     0.074 |
| p2550n1_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2550n1.txt  |            50 |         9 |    8 |       6 |       6 | bb        |     0.011 |
| p2550n2_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2550n2.txt  |            50 |        11 |   10 |       8 |       8 | bb        |     0.020 |
| p2550n7_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2550n7.txt  |            50 |        10 |    9 |       7 |       7 | bb        |     0.012 |
| p2550n8_0                                           | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p2550n8.txt  |            50 |        11 |   10 |       8 |       8 | bb        |     0.017 |
| p3050n10_0                                          | benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/p3050n10.txt |            50 |        12 |   11 |       9 |       9 | bb        |     0.877 |
| scoop-A_FA+AA-_6_0                                  | benchmarks/instances/MOSP_Instances/SCOOP/scoop-A_FA+AA-_6.txt        |            79 |        13 |   12 |      10 |      10 | heuristic |     0.040 |
| Random-100-50-2-1_0                                 | benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-100-50-2-1.txt |           100 |        12 |   11 |       6 |       9 | heuristic |     0.025 |
| Random-100-50-2-5_0                                 | benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-100-50-2-5.txt |           100 |        12 |   11 |       6 |       9 | heuristic |     0.029 |
| scoop-A_FA+AA-_1_0                                  | benchmarks/instances/MOSP_Instances/SCOOP/scoop-A_FA+AA-_1.txt        |           105 |        12 |   11 |       8 |       9 | heuristic |     0.058 |

## Corpus baselines per n

|       n |   instances |    gap |   overshoot |   disagree |     nodes |    pwtw |   pwtw_instances |
|--------:|------------:|-------:|------------:|-----------:|----------:|--------:|-----------------:|
|   9.000 |      10.000 |  1.000 |       0.000 |      0.000 |     6.000 |   1.000 |           10.000 |
|  10.000 |    1604.000 |  1.000 |       1.000 |      0.000 |    15.000 |   1.000 |         1604.000 |
|  13.000 |       1.000 |  0.000 |       0.000 |      0.000 |     1.000 |   0.000 |            1.000 |
|  14.000 |       3.000 |  1.000 |       2.000 |      0.000 |    11.000 |   1.000 |            3.000 |
|  15.000 |    1194.000 |  1.000 |       2.000 |      0.000 |    57.000 |   1.000 |         1194.000 |
|  17.000 |       3.000 |  1.000 |       1.000 |      0.000 |    32.000 |   1.000 |            3.000 |
|  18.000 |       4.000 |  1.000 |       2.000 |      0.000 |    55.000 |   1.000 |            4.000 |
|  19.000 |       5.000 |  1.000 |       0.000 |      0.000 |    48.000 |   2.000 |            5.000 |
|  20.000 |    1298.000 |  2.000 |       3.000 |      0.000 |    90.000 |   2.000 |         1298.000 |
|  21.000 |       1.000 |  1.000 |       0.000 |      0.000 |    65.000 | -99.000 |            0.000 |
|  24.000 |       1.000 |  1.000 |       0.000 |      0.000 |    47.000 | -99.000 |            0.000 |
|  25.000 |       6.000 |  1.000 |       0.000 |      0.000 |   370.000 | -99.000 |            0.000 |
|  26.000 |       1.000 |  1.000 |       0.000 |      0.000 |   257.000 | -99.000 |            0.000 |
|  27.000 |       2.000 |  1.000 |       0.000 |      0.000 |   144.000 | -99.000 |            0.000 |
|  28.000 |       4.000 |  1.000 |       3.000 |      0.000 |   498.000 | -99.000 |            0.000 |
|  29.000 |       6.000 |  1.000 |       1.000 |      0.000 |   654.000 | -99.000 |            0.000 |
|  30.000 |    1795.000 |  3.000 |       6.000 |      0.000 |  1149.000 |   2.000 |          133.000 |
|  31.000 |       2.000 |  1.000 |       3.000 |      0.000 |   160.000 | -99.000 |            0.000 |
|  37.000 |       2.000 |  2.000 |       2.000 |      0.000 |  5380.000 |   0.000 |            1.000 |
|  38.000 |       6.000 |  3.000 |       2.000 |      0.000 |  4964.000 |   1.000 |            2.000 |
|  39.000 |       2.000 |  3.000 |       2.000 |      0.000 |  5276.000 |   0.000 |            2.000 |
|  40.000 |     185.000 |  4.000 |       3.000 |      0.000 | 29138.000 |   2.000 |           42.000 |
|  50.000 |     120.000 |  5.000 |       6.000 |      0.000 |    -1.000 |   3.000 |           32.000 |
|  60.000 |       1.000 |  0.000 |       1.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
|  68.000 |       1.000 |  1.000 |       1.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
|  75.000 |      29.000 | 16.000 |       5.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
|  79.000 |       1.000 |  2.000 |       0.000 |      0.000 |    -1.000 |   2.000 |            1.000 |
|  82.000 |       1.000 |  1.000 |       2.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
|  99.000 |       1.000 |  1.000 |       1.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
| 100.000 |      60.000 | 23.000 |      10.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
| 105.000 |       1.000 |  2.000 |       2.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
| 125.000 |      25.000 | 30.000 |       7.000 |      0.000 |    -1.000 | -99.000 |            0.000 |
| 134.000 |       1.000 |  6.000 |       4.000 |      0.000 |    -1.000 | -99.000 |            0.000 |

## The smallest instances found with pw − tw ≥ 2 (isolated customers dropped)

50 distinct instances with pw − tw ≥ 2 over every job; by active vertex count: 10 vertices × 1, 11 vertices × 6, 12 vertices × 10, 13 vertices × 13, 14 vertices × 9, 15 vertices × 6, 16 vertices × 1, 17 vertices × 2, 18 vertices × 2.

**10 vertices, pw − tw = 2 (drawn at n = 10, seed kind corpus)** — 10 customers × 9 products, 23 ones; MOSP graph 21 edges, degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3.

```
0 0 1 0 0 0 1 1 0
0 0 0 0 0 0 1 0 0
1 0 1 0 0 0 0 0 0
0 0 1 0 1 1 0 0 0
0 0 0 0 1 1 0 0 1
0 0 0 0 0 1 0 0 0
1 0 0 1 0 0 0 0 1
0 0 1 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0
0 1 0 0 1 1 1 0 0
```

- treewidth **3**: ≥ 3 because the MOSP graph contains K4 (so the lower half is a clique anyone can check); ≤ 3 by the elimination ordering `7 5 4 2 3 6 9 8 1 0` (width recomputed by `elimination_width`).
- pathwidth **5**: the certified optimum 6 minus one (`decide(5)` unsat / unsat and `decide(6)` sat / sat under `default` / `csearch`); the exact pathwidth DP says 5; the lattice oracle says optimum 6.
- so **pw − tw = 2** on 10 vertices, 21 edges, 1 component(s), degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3.

**11 vertices, pw − tw = 2 (drawn at n = 11, seed kind corpus)** — 11 customers × 10 products, 24 ones; MOSP graph 21 edges, degrees 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2.

```
0 0 0 0 0 1 0 0 1 0
0 0 1 0 0 0 0 0 1 0
0 0 1 1 0 0 0 0 0 1
0 0 0 0 0 0 0 1 1 0
1 0 0 1 0 0 1 0 0 0
1 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 1 0
0 0 1 0 0 1 0 0 0 1
0 1 0 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
```

- treewidth **3**: ≥ 3 because the MOSP graph contains K4 (so the lower half is a clique anyone can check); ≤ 3 by the elimination ordering `10 9 8 5 2 7 4 6 3 1 0` (width recomputed by `elimination_width`).
- pathwidth **5**: the certified optimum 6 minus one (`decide(5)` unsat / unsat and `decide(6)` sat / sat under `default` / `csearch`); the exact pathwidth DP says 5; the lattice oracle says optimum 6.
- so **pw − tw = 2** on 11 vertices, 21 edges, 1 component(s), degrees 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2.

**12 vertices, pw − tw = 2 (drawn at n = 17, seed kind toc)** — 12 customers × 9 products, 23 ones; MOSP graph 22 edges, degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3, 1, 1.

```
0 0 1 0 0 0 1 0 0
1 1 0 1 0 0 0 0 0
0 0 1 0 0 0 0 0 0
0 0 1 0 1 1 0 0 0
1 0 1 0 0 0 0 0 1
0 1 0 0 1 0 0 0 0
0 0 0 0 1 0 1 0 0
0 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 1 0
0 0 0 0 1 1 0 0 0
0 0 0 0 0 0 1 0 0
0 0 0 1 0 0 1 0 0
```

- treewidth **3**: ≥ 3 because the MOSP graph contains K4 (so the lower half is a clique anyone can check); ≤ 3 by the elimination ordering `10 11 9 8 7 5 6 2 4 3 1 0` (width recomputed by `elimination_width`).
- pathwidth **5**: the certified optimum 6 minus one (`decide(5)` unsat / unsat and `decide(6)` sat / sat under `default` / `csearch`); the exact pathwidth DP says 5; the lattice oracle says optimum 6.
- so **pw − tw = 2** on 12 vertices, 22 edges, 2 component(s), degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3, 1, 1.

## Drawings

**disagree at n = 8: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 8 customers × 4 products, 3 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0.

```
0 1 0 0
0 0 0 0
0 0 0 1
0 0 0 0
1 0 0 0
0 0 0 0
0 0 0 0
0 0 0 0
```
Witness closing order `1 3 0 2`; elimination ordering of width 0: `7 6 5 4 3 2 1 0`.

**disagree at n = 9: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 9 customers × 9 products, 8 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 0
0 0 0 0 0 1 0 1 0
0 0 0 0 1 0 0 0 0
0 0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 1 0 1 0 0 0 0 0
```
Witness closing order `6 4 2 0 5 7 1 3 8`; elimination ordering of width 0: `8 7 6 5 4 3 2 1 0`.

**disagree at n = 10: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 10 customers × 7 products, 5 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 1 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 1 0 0
0 0 0 0 0 0 0
0 1 0 1 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
1 0 0 0 0 0 0
```
Witness closing order `2 4 0 1 3 5 6`; elimination ordering of width 0: `9 8 7 6 5 4 3 2 1 0`.

**disagree at n = 11: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 11 customers × 6 products, 5 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0
1 0 0 0 0 0
0 0 0 0 0 0
0 0 0 1 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 1
0 0 0 0 0 0
0 0 0 0 0 0
0 1 1 0 0 0
0 0 0 0 0 0
```
Witness closing order `0 3 5 1 2 4`; elimination ordering of width 0: `10 9 8 7 6 5 4 3 2 1 0`.

**disagree at n = 12: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 12 customers × 7 products, 5 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0 0
0 0 0 0 0 0 0
1 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 1 0 0
0 0 0 0 0 0 0
0 0 0 1 0 0 0
0 0 1 0 0 0 0
0 0 0 0 0 0 0
0 1 0 0 0 0 0
0 0 0 0 0 0 0
```
Witness closing order `0 4 3 2 1 5 6`; elimination ordering of width 0: `11 10 9 8 7 6 5 4 3 2 1 0`.

**disagree at n = 13: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 13 customers × 7 products, 7 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0 0
0 0 0 0 0 0 0
1 0 0 0 1 0 0
0 0 1 0 0 0 0
0 0 0 1 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 1 0 0 0 0 0
0 0 0 0 0 1 0
0 0 0 0 0 0 1
0 0 0 0 0 0 0
```
Witness closing order `2 3 1 5 6 0 4`; elimination ordering of width 0: `12 11 10 9 8 7 6 5 4 3 2 1 0`.

**disagree at n = 14: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 14 customers × 14 products, 14 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
1 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 1 1 0 0 0 0 1 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 1 0 0 0 0 1 0
0 0 0 0 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 1 0 0
0 1 0 0 0 0 0 0 0 0 0 0 0 0
```
Witness closing order `0 4 10 13 6 11 1 5 9 7 12 2 3 8`; elimination ordering of width 0: `13 12 11 10 9 8 7 6 5 4 3 2 1 0`.

**disagree at n = 15: value 0 (optimum 1, lb_best 1, tw 0, nodes 0, cs-dfs 1)** — 15 customers × 8 products, 8 ones; MOSP graph 0 edges, degrees 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0
1 0 1 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0
0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0
```
Witness closing order `7 3 1 5 6 4 0 2`; elimination ordering of width 0: `14 13 12 11 10 9 8 7 6 5 4 3 2 1 0`.

**gap at n = 8: value 1 (optimum 4, lb_best 3, tw 2, nodes 4, cs-dfs 4)** — 8 customers × 8 products, 17 ones; MOSP graph 9 edges, degrees 4, 4, 4, 2, 2, 2, 0, 0.

```
0 0 0 1 1 1 1 1
0 0 0 1 0 0 1 0
1 0 1 0 1 0 0 0
0 0 1 0 0 0 0 0
0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 1 1 0 0 1 0
1 0 0 0 0 0 0 1
```
Witness closing order `1 2 3 6 0 7 4 5`; elimination ordering of width 2: `7 3 2 6 5 4 1 0`.

**gap at n = 9: value 1 (optimum 3, lb_best 2, tw 1, nodes 7, cs-dfs 3)** — 9 customers × 13 products, 19 ones; MOSP graph 6 edges, degrees 3, 2, 2, 2, 1, 1, 1, 0, 0.

```
1 0 0 1 0 1 0 0 0 0 0 1 0
0 0 1 0 0 0 0 0 0 0 1 0 0
0 1 0 0 0 0 0 1 1 0 0 0 1
0 0 0 0 0 0 0 0 0 0 1 0 1
0 0 0 0 1 0 0 1 0 1 0 0 0
0 0 0 0 0 0 1 0 0 0 0 0 0
0 0 0 0 1 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0
```
Witness closing order `6 4 2 10 12 7 9 0 3 5 11 8 1`; elimination ordering of width 1: `8 6 4 1 3 2 7 5 0`.

**gap at n = 10: value 1 (optimum 4, lb_best 3, tw 2, nodes 3, cs-dfs 4)** — 10 customers × 6 products, 10 ones; MOSP graph 9 edges, degrees 4, 4, 4, 2, 2, 2, 0, 0, 0, 0.

```
0 1 1 1 0 0
1 0 1 0 0 0
0 0 0 0 0 0
1 0 0 1 0 0
0 0 0 0 0 0
1 0 0 0 0 0
0 0 1 0 0 0
0 0 0 0 0 0
0 0 0 1 0 0
0 0 0 0 0 0
```
Witness closing order `0 2 3 1 4 5`; elimination ordering of width 2: `9 8 7 6 5 4 3 2 1 0`.

**gap at n = 11: value 1 (optimum 4, lb_best 3, tw 2, nodes 4, cs-dfs 4)** — 11 customers × 6 products, 10 ones; MOSP graph 9 edges, degrees 4, 4, 4, 2, 2, 2, 0, 0, 0, 0, 0.

```
0 1 0 0 0 0
0 0 0 1 0 0
0 1 0 1 0 0
0 0 1 0 0 0
1 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 1 1 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 1 1 0 0 0
```
Witness closing order `0 1 3 2 4 5`; elimination ordering of width 2: `3 1 7 10 9 8 6 5 4 2 0`.

**gap at n = 12: value 2 (optimum 7, lb_best 5, tw 5, nodes 10, cs-dfs 7)** — 12 customers × 6 products, 19 ones; MOSP graph 28 edges, degrees 7, 7, 6, 6, 6, 6, 4, 4, 4, 4, 2, 0.

```
1 1 0 0 0 0
0 0 0 1 0 0
0 1 0 0 0 0
0 1 0 0 0 1
0 0 0 0 0 0
0 1 1 0 0 0
1 1 0 0 0 0
1 0 1 0 0 0
1 0 0 0 0 0
0 0 0 1 0 1
0 0 1 1 0 0
1 0 0 0 0 1
```
Witness closing order `3 5 2 1 0 4`; elimination ordering of width 5: `8 11 10 2 6 9 7 5 4 3 1 0`.

**gap at n = 13: value 1 (optimum 4, lb_best 3, tw 2, nodes 5, cs-dfs 4)** — 13 customers × 9 products, 16 ones; MOSP graph 9 edges, degrees 4, 4, 4, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0.

```
1 0 0 0 1 1 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 1 1 0 0 0
0 0 0 1 0 0 0 0 1
0 1 1 0 0 0 0 1 0
0 0 0 0 1 0 0 0 1
1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 1
0 0 0 0 0 0 1 0 0
```
Witness closing order `6 1 2 7 0 4 5 3 8`; elimination ordering of width 2: `12 6 3 11 10 9 8 7 5 4 2 1 0`.

**gap at n = 14: value 2 (optimum 7, lb_best 5, tw 5, nodes 7, cs-dfs 7)** — 14 customers × 6 products, 18 ones; MOSP graph 28 edges, degrees 7, 7, 7, 7, 6, 6, 5, 4, 4, 3, 0, 0, 0, 0.

```
1 0 0 1 0 0
1 0 0 0 0 0
1 1 0 0 0 0
0 0 0 0 0 0
0 1 0 1 0 0
0 0 0 0 1 0
0 0 1 0 0 0
0 1 1 0 0 0
0 0 0 0 0 0
0 1 0 0 0 0
0 0 0 0 0 0
1 0 1 0 0 0
0 0 1 1 0 0
1 1 0 0 0 0
```
Witness closing order `4 2 3 0 1 5`; elimination ordering of width 5: `6 12 9 7 13 11 10 8 5 4 3 2 1 0`.

**gap at n = 15: value 2 (optimum 7, lb_best 5, tw 5, nodes 7, cs-dfs 7)** — 15 customers × 8 products, 20 ones; MOSP graph 28 edges, degrees 7, 7, 7, 7, 6, 6, 5, 4, 4, 3, 0, 0, 0, 0, 0.

```
0 1 0 0 0 0 0 0
1 1 0 0 0 0 0 0
1 0 1 0 0 0 0 0
1 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0
1 1 0 0 0 0 0 0
0 0 1 0 0 1 0 1
0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0
0 1 0 0 1 1 0 0
0 0 0 0 0 0 0 0
0 1 1 0 0 0 0 0
0 0 0 1 0 0 0 0
1 0 0 0 0 0 0 0
```
Witness closing order `3 5 2 7 0 1 4 6`; elimination ordering of width 5: `14 13 8 6 3 12 11 10 9 7 5 4 2 1 0`.

**nodes at n = 8: value 14 (optimum 4, lb_best 4, tw 3, nodes 14, cs-dfs 4)** — 8 customers × 12 products, 26 ones; MOSP graph 12 edges, degrees 6, 6, 3, 3, 2, 2, 1, 1.

```
0 0 1 0 1 0 0 1 1 1 1 1
0 0 0 1 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 1 0 1 0 0
0 0 0 0 1 0 0 0 0 0 0 0
1 1 1 1 0 0 0 1 1 0 0 1
0 0 1 0 0 1 0 0 0 0 0 1
1 0 0 0 0 0 1 0 0 0 0 0
0 0 0 1 0 0 0 0 0 0 1 0
```
Witness closing order `4 0 6 7 9 2 5 11 3 8 10 1`; elimination ordering of width 3: `7 6 5 4 3 2 1 0`.

**nodes at n = 9: value 21 (optimum 4, lb_best 4, tw 3, nodes 21, cs-dfs 4)** — 9 customers × 9 products, 19 ones; MOSP graph 12 edges, degrees 6, 5, 3, 3, 2, 2, 1, 1, 1.

```
1 0 0 0 1 1 0 1 0
0 1 1 0 1 0 0 0 0
0 0 0 1 0 0 1 0 0
0 0 0 0 0 0 0 1 0
0 0 0 0 1 0 0 0 0
0 0 0 1 0 1 0 0 0
0 1 0 0 1 0 1 0 1
0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0
```
Witness closing order `7 8 0 3 6 5 4 1 2`; elimination ordering of width 3: `8 7 4 6 5 3 2 1 0`.

**nodes at n = 10: value 37 (optimum 4, lb_best 4, tw 3, nodes 37, cs-dfs 4)** — 10 customers × 10 products, 23 ones; MOSP graph 15 edges, degrees 8, 7, 3, 3, 2, 2, 2, 1, 1, 1.

```
1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 1
0 1 0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 1 0 0
0 0 0 0 0 0 0 0 1 0
0 0 0 0 0 1 0 0 0 0
0 1 0 0 1 1 1 0 1 1
1 1 1 0 0 1 0 1 0 1
0 0 0 1 1 0 0 1 0 0
```
Witness closing order `0 6 8 9 1 5 4 7 3 2`; elimination ordering of width 3: `9 6 4 3 8 5 7 2 1 0`.

**nodes at n = 11: value 53 (optimum 5, lb_best 5, tw 4, nodes 53, cs-dfs 5)** — 11 customers × 9 products, 24 ones; MOSP graph 21 edges, degrees 8, 8, 7, 4, 4, 3, 3, 2, 1, 1, 1.

```
0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 1 0
0 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1
1 1 1 0 0 0 1 1 0
1 0 1 0 1 0 0 1 0
0 0 0 0 0 0 0 1 0
1 0 0 1 0 0 0 0 0
0 0 0 0 0 1 1 0 0
0 0 1 1 0 0 1 1 1
0 0 1 0 0 0 0 0 0
```
Witness closing order `4 1 8 5 6 2 0 3 7`; elimination ordering of width 4: `10 8 7 6 9 5 4 3 2 1 0`.

**nodes at n = 12: value 63 (optimum 6, lb_best 6, tw 5, nodes 63, cs-dfs 6)** — 12 customers × 12 products, 29 ones; MOSP graph 22 edges, degrees 7, 6, 5, 5, 5, 5, 4, 3, 1, 1, 1, 1.

```
0 1 0 0 0 0 0 0 0 0 0 0
0 0 0 1 1 1 0 0 0 1 0 0
0 0 0 0 0 0 0 1 0 0 1 1
0 0 0 1 0 0 0 0 0 0 0 1
1 0 1 0 0 0 0 0 1 0 0 0
0 1 1 0 0 0 0 0 0 1 0 1
1 0 0 1 0 0 1 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0 1 0
0 0 0 0 0 0 1 0 0 0 0 0
0 0 0 1 0 0 0 0 0 0 0 1
0 0 0 0 1 0 0 0 0 0 0 0
0 0 1 0 0 1 0 1 0 0 0 0
```
Witness closing order `1 10 6 4 0 2 8 5 7 11 9 3`; elimination ordering of width 5: `11 10 9 8 7 6 5 4 3 2 1 0`.

**nodes at n = 13: value 114 (optimum 6, lb_best 6, tw 5, nodes 114, cs-dfs 6)** — 13 customers × 10 products, 28 ones; MOSP graph 28 edges, degrees 9, 8, 8, 8, 5, 5, 3, 3, 3, 1, 1, 1, 1.

```
0 0 0 0 0 0 1 0 0 0
1 1 0 0 1 0 0 0 0 1
1 0 0 1 1 0 1 0 0 1
0 0 1 0 0 0 0 0 0 0
1 0 0 0 0 1 0 1 1 0
1 0 0 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0 0
1 0 1 1 1 0 0 0 0 0
0 0 0 0 1 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 1
0 0 0 1 0 0 0 1 0 0
0 0 0 0 0 0 0 0 1 0
```
Witness closing order `6 2 1 8 4 5 9 3 7 0`; elimination ordering of width 5: `12 11 10 9 8 7 6 5 4 3 2 1 0`.

**nodes at n = 14: value 132 (optimum 6, lb_best 5, tw 4, nodes 132, cs-dfs 6)** — 14 customers × 10 products, 26 ones; MOSP graph 26 edges, degrees 7, 7, 7, 7, 6, 4, 3, 2, 2, 2, 2, 1, 1, 1.

```
0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 1 1 0 0
0 0 0 1 0 0 0 0 0 0
0 1 0 0 0 0 0 0 1 0
0 0 0 1 0 0 0 1 0 0
1 0 0 1 0 0 0 0 1 0
0 0 1 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0
0 0 0 0 1 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
0 0 0 1 0 1 0 0 0 1
0 0 0 0 0 0 0 1 0 0
0 0 0 0 1 0 1 0 1 1
1 0 0 0 0 0 0 0 0 0
```
Witness closing order `7 6 3 0 8 1 2 4 9 5`; elimination ordering of width 4: `13 8 6 2 9 7 10 5 12 11 4 3 1 0`.

**nodes at n = 15: value 209 (optimum 7, lb_best 7, tw 6, nodes 209, cs-dfs 7)** — 15 customers × 10 products, 29 ones; MOSP graph 33 edges, degrees 10, 8, 8, 8, 7, 7, 6, 2, 2, 2, 2, 1, 1, 1, 1.

```
0 0 0 0 0 0 1 0 0 1
0 0 1 1 0 1 0 1 0 1
1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0
0 0 0 1 1 0 0 0 0 0
0 0 1 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0 0 0
0 1 0 1 0 0 0 1 0 0
1 0 0 1 0 0 1 0 0 1
0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0
0 0 0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1 0
0 0 1 1 0 0 0 0 0 0
0 0 0 1 0 1 0 0 1 0
```
Witness closing order `0 4 1 8 5 2 7 6 9 3`; elimination ordering of width 6: `12 11 14 13 10 9 7 8 6 5 4 3 2 1 0`.

**overshoot at n = 8: value 2 (optimum 2, lb_best 2, tw 1, nodes 1, cs-dfs 4)** — 8 customers × 9 products, 16 ones; MOSP graph 6 edges, degrees 4, 2, 2, 1, 1, 1, 1, 0.

```
0 0 0 0 0 1 0 0 0
1 0 0 0 1 0 0 0 0
0 1 1 1 0 0 0 1 1
1 0 0 0 1 0 0 0 1
0 1 0 0 0 1 0 0 0
0 0 0 1 0 0 0 0 0
0 0 1 0 0 0 0 0 0
0 0 0 0 0 0 1 0 0
```
Witness closing order `6 5 1 3 2 7 8 0 4`; elimination ordering of width 1: `7 6 5 1 3 2 4 0`.

**overshoot at n = 9: value 2 (optimum 2, lb_best 2, tw 1, nodes 0, cs-dfs 4)** — 9 customers × 8 products, 13 ones; MOSP graph 6 edges, degrees 4, 2, 2, 1, 1, 1, 1, 0, 0.

```
1 1 1 1 0 0 0 0
0 0 0 0 1 1 0 0
0 0 0 0 0 0 0 0
1 0 0 0 1 0 0 0
0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0
0 0 1 0 0 0 0 1
0 0 0 1 0 0 0 0
```
Witness closing order `4 5 0 1 3 2 7 6`; elimination ordering of width 1: `8 5 7 6 4 1 3 2 0`.

**overshoot at n = 10: value 2 (optimum 2, lb_best 2, tw 1, nodes 1, cs-dfs 4)** — 10 customers × 10 products, 16 ones; MOSP graph 6 edges, degrees 4, 2, 2, 1, 1, 1, 1, 0, 0, 0.

```
0 0 0 0 0 0 0 1 1 0
1 0 0 0 0 0 0 0 0 0
0 1 1 1 0 0 0 0 0 0
0 0 0 1 1 1 1 0 1 0
0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 0 1
```
Witness closing order `0 9 6 7 8 5 3 4 1 2`; elimination ordering of width 1: `4 9 8 7 6 5 2 3 1 0`.

**overshoot at n = 11: value 3 (optimum 3, lb_best 3, tw 2, nodes 3, cs-dfs 6)** — 11 customers × 10 products, 20 ones; MOSP graph 13 edges, degrees 7, 3, 3, 3, 2, 2, 2, 2, 1, 1, 0.

```
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 1
0 0 0 0 1 1 1 1 0 0
0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 1 0 0 0 0
0 0 1 0 0 0 0 0 1 0
0 0 0 1 0 0 1 0 0 0
0 1 0 0 0 0 0 0 0 0
0 1 0 0 0 1 0 0 0 0
1 0 0 0 1 0 0 0 0 1
0 0 0 0 1 0 0 0 0 1
```
Witness closing order `2 8 7 6 3 5 1 4 9 0`; elimination ordering of width 2: `1 10 9 7 8 6 5 4 3 2 0`.

**overshoot at n = 12: value 3 (optimum 2, lb_best 2, tw 1, nodes 1, cs-dfs 5)** — 12 customers × 10 products, 18 ones; MOSP graph 8 edges, degrees 5, 2, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0.

```
0 0 1 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 1 0 0 0 0
0 0 0 0 1 0 1 0 0 0
0 0 0 0 0 0 1 0 0 0
1 0 0 0 1 1 0 1 0 1
0 1 0 0 0 0 0 0 1 0
0 0 0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 1 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1 0
```
Witness closing order `1 8 3 6 4 9 5 0 7 2`; elimination ordering of width 1: `11 10 9 8 7 6 4 3 2 1 5 0`.

**overshoot at n = 13: value 3 (optimum 3, lb_best 3, tw 2, nodes 4, cs-dfs 6)** — 13 customers × 9 products, 19 ones; MOSP graph 13 edges, degrees 7, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1, 0, 0.

```
0 0 0 0 0 0 0 0 1
0 0 1 0 0 0 0 0 0
1 0 0 0 0 0 0 1 1
0 1 0 1 1 0 0 0 0
1 1 1 0 0 1 0 0 0
0 1 0 0 0 0 1 0 0
0 0 0 1 0 0 0 0 0
0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 1 0 0
1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 1 0 0 0 0 0 0
```
Witness closing order `8 0 7 2 5 1 3 4 6`; elimination ordering of width 2: `12 11 10 9 8 7 6 5 3 4 2 1 0`.

**overshoot at n = 14: value 3 (optimum 3, lb_best 3, tw 2, nodes 2, cs-dfs 6)** — 14 customers × 10 products, 24 ones; MOSP graph 14 edges, degrees 7, 3, 3, 3, 3, 2, 2, 2, 2, 1, 0, 0, 0, 0.

```
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1 0
1 0 0 0 0 0 0 0 0 0
0 1 1 1 1 0 1 0 0 0
0 0 0 1 0 0 0 0 0 0
0 0 0 0 0 1 1 0 0 0
0 0 0 0 0 1 0 0 0 0
0 0 1 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0 1 1
0 0 0 0 1 0 0 0 1 1
0 1 0 0 0 1 1 0 0 0
0 0 1 0 0 0 0 1 0 0
```
Witness closing order `0 8 4 9 3 2 7 1 6 5`; elimination ordering of width 2: `13 6 12 7 5 4 3 11 10 9 8 2 1 0`.

**overshoot at n = 15: value 4 (optimum 6, lb_best 6, tw 5, nodes 31, cs-dfs 10)** — 15 customers × 22 products, 53 ones; MOSP graph 35 edges, degrees 10, 7, 6, 6, 6, 5, 5, 5, 5, 4, 3, 3, 3, 1, 1.

```
0 0 1 0 0 1 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 1 0 1
1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0
0 0 0 1 0 0 0 1 0 0 0 1 0 1 0 1 1 0 0 0 1 0
0 0 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 1 0 1
0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0
1 0 0 0 0 1 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 1 0
0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0
1 0 0 0 0 0 0 1 0 0 0 1 0 1 0 1 0 0 0 0 1 0
0 1 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1
```
Witness closing order `6 14 4 18 7 11 20 3 13 15 16 0 12 17 5 2 21 8 10 19 1 9`; elimination ordering of width 5: `11 4 13 12 8 10 5 9 14 7 6 3 2 1 0`.

**pwtw at n = 7: value 1 (optimum 3, lb_best 3, tw 1, nodes 6, cs-dfs 3)** — 7 customers × 7 products, 13 ones; MOSP graph 6 edges, degrees 3, 2, 2, 2, 1, 1, 1.

```
0 0 0 0 1 0 1
0 1 0 0 0 1 0
0 0 0 1 0 0 0
0 0 0 0 0 1 0
1 1 1 0 0 0 1
1 0 0 1 0 0 0
0 0 0 0 1 0 0
```
Witness closing order `3 0 1 2 6 4 5`; elimination ordering of width 1: `6 2 5 3 1 4 0`.

**pwtw at n = 8: value 1 (optimum 3, lb_best 2, tw 1, nodes 6, cs-dfs 3)** — 8 customers × 12 products, 18 ones; MOSP graph 6 edges, degrees 3, 2, 2, 2, 1, 1, 1, 0.

```
0 0 0 0 1 1 0 0 0 1 0 0
0 0 1 0 0 0 0 1 1 1 0 0
1 0 0 1 0 0 0 0 0 0 1 0
0 0 0 1 0 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 1 1 0 0 0 0 0
0 1 1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
```
Witness closing order `1 11 5 6 2 4 9 0 3 10 7 8`; elimination ordering of width 1: `7 4 6 5 2 3 1 0`.

**pwtw at n = 9: value 1 (optimum 3, lb_best 2, tw 1, nodes 7, cs-dfs 3)** — 9 customers × 9 products, 15 ones; MOSP graph 6 edges, degrees 3, 2, 2, 2, 1, 1, 1, 0, 0.

```
0 0 1 0 0 0 0 1 0
0 0 0 0 0 0 1 0 0
1 0 1 0 0 0 0 0 0
0 0 0 0 1 1 0 0 1
0 0 0 0 0 1 0 0 0
1 0 0 1 0 0 0 0 1
0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0
0 1 0 0 0 0 0 0 0
```
Witness closing order `1 2 7 0 3 8 4 5 6`; elimination ordering of width 1: `8 1 7 6 4 3 5 2 0`.

**pwtw at n = 10: value 2 (optimum 6, lb_best 5, tw 3, nodes 10, cs-dfs 6)** — 10 customers × 9 products, 23 ones; MOSP graph 21 edges, degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3.

```
0 0 1 0 0 0 1 1 0
0 0 0 0 0 0 1 0 0
1 0 1 0 0 0 0 0 0
0 0 1 0 1 1 0 0 0
0 0 0 0 1 1 0 0 1
0 0 0 0 0 1 0 0 0
1 0 0 1 0 0 0 0 1
0 0 1 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0
0 1 0 0 1 1 1 0 0
```
Witness closing order `6 3 0 8 2 7 4 5 1`; elimination ordering of width 3: `7 5 4 2 3 6 9 8 1 0`.

**pwtw at n = 11: value 2 (optimum 6, lb_best 5, tw 3, nodes 15, cs-dfs 6)** — 11 customers × 10 products, 24 ones; MOSP graph 21 edges, degrees 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2.

```
0 0 0 0 0 1 0 0 1 0
0 0 1 0 0 0 0 0 1 0
0 0 1 1 0 0 0 0 0 1
0 0 0 0 0 0 0 1 1 0
1 0 0 1 0 0 1 0 0 0
1 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 1 0
0 0 1 0 0 1 0 0 0 1
0 1 0 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
```
Witness closing order `1 0 5 3 6 8 7 2 4 9`; elimination ordering of width 3: `10 9 8 5 2 7 4 6 3 1 0`.

**pwtw at n = 12: value 1 (optimum 3, lb_best 2, tw 1, nodes 7, cs-dfs 3)** — 12 customers × 10 products, 16 ones; MOSP graph 6 edges, degrees 3, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0.

```
1 0 0 0 1 0 0 0 0 0
0 0 0 0 1 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
1 0 1 0 0 1 0 0 1 0
0 0 0 1 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 1 0 0 0
0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 1 0 0 0 0 1 0 0
```
Witness closing order `1 4 9 0 2 5 8 6 7 3`; elimination ordering of width 1: `6 11 10 9 8 7 5 4 3 2 1 0`.

**pwtw at n = 13: value 2 (optimum 6, lb_best 4, tw 3, nodes 15, cs-dfs 6)** — 13 customers × 10 products, 24 ones; MOSP graph 21 edges, degrees 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 0, 0.

```
0 0 0 0 0 1 0 0 1 0
0 0 0 0 0 0 0 0 0 0
0 0 1 0 0 0 0 0 1 0
0 0 1 1 0 0 0 0 0 1
0 0 0 0 0 0 0 1 1 0
1 0 0 1 0 0 1 0 0 0
1 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 1 0
0 0 1 0 0 1 0 0 0 1
0 1 0 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
```
Witness closing order `1 0 5 3 6 8 7 2 4 9`; elimination ordering of width 3: `12 11 10 6 3 9 5 8 7 4 2 1 0`.

**pwtw at n = 14: value 2 (optimum 6, lb_best 4, tw 3, nodes 11, cs-dfs 6)** — 14 customers × 10 products, 24 ones; MOSP graph 21 edges, degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3, 0, 0, 0, 0.

```
0 0 1 0 0 0 1 0 1 0
0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0
1 0 1 0 0 0 0 0 0 0
0 0 1 0 1 1 0 0 0 0
0 0 0 0 1 1 0 0 0 1
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0
1 0 0 1 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0
0 0 1 0 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0 0
0 1 0 0 1 1 1 0 0 0
```
Witness closing order `7 6 3 0 9 2 8 4 5 1`; elimination ordering of width 3: `11 7 5 3 4 9 13 12 10 8 6 2 1 0`.

**pwtw at n = 15: value 2 (optimum 7, lb_best 5, tw 4, nodes 18, cs-dfs 7)** — 15 customers × 8 products, 23 ones; MOSP graph 33 edges, degrees 8, 6, 6, 6, 6, 5, 4, 4, 4, 4, 4, 3, 3, 3, 0.

```
1 0 0 1 0 0 0 0
0 0 0 0 0 1 0 0
0 1 0 1 0 0 0 0
0 0 0 1 0 0 0 0
1 0 0 0 1 0 0 0
1 1 0 0 0 0 0 0
0 0 0 0 1 1 0 0
0 1 1 0 0 0 0 0
0 0 0 1 0 0 0 1
1 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0
1 0 0 0 0 0 0 0
0 0 0 1 1 0 0 0
0 0 0 0 0 0 0 0
0 0 1 0 0 1 0 0
```
Witness closing order `5 2 4 1 3 7 0 6`; elimination ordering of width 4: `14 13 8 3 12 11 10 9 7 4 6 5 2 1 0`.

**pwtw at n = 16: value 2 (optimum 7, lb_best 5, tw 4, nodes 31, cs-dfs 7)** — 16 customers × 10 products, 27 ones; MOSP graph 29 edges, degrees 8, 7, 6, 6, 5, 5, 4, 4, 4, 3, 3, 2, 1, 0, 0, 0.

```
1 1 0 0 0 0 0 0 0 0
0 1 1 0 0 0 0 0 0 0
1 0 0 0 1 1 0 0 0 0
0 0 1 0 0 0 0 0 1 0
0 0 0 0 0 0 0 1 0 0
0 1 0 1 0 0 1 0 1 1
0 1 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 0 1 0
0 1 0 1 0 0 0 0 0 0
0 0 0 0 1 0 0 0 1 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 1 0 1 0 0
0 0 1 0 0 0 0 1 0 0
```
Witness closing order `9 7 5 2 0 4 8 1 3 6`; elimination ordering of width 4: `15 14 13 12 11 10 7 9 8 4 3 6 5 2 1 0`.

**pwtw at n = 17: value 2 (optimum 6, lb_best 4, tw 3, nodes 13, cs-dfs 6)** — 17 customers × 12 products, 25 ones; MOSP graph 22 edges, degrees 6, 6, 6, 4, 4, 4, 3, 3, 3, 3, 1, 1, 0, 0, 0, 0, 0.

```
0 0 0 1 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 1 1 0 1 0 0 0 0 0 0 0
0 0 0 1 0 0 0 0 0 0 0 0
0 0 0 1 0 1 0 1 0 0 0 0
0 1 0 1 0 0 0 0 0 0 1 0
0 0 1 0 0 1 0 0 0 0 0 0
0 0 0 0 0 0 1 0 0 0 0 0
0 0 0 0 0 1 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 1 0 0
1 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 1 0 1 0 0 0 0
0 0 0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0 1 0 0 0
```
Witness closing order `6 0 9 1 2 4 3 10 8 5 7 11`; elimination ordering of width 3: `13 16 15 14 12 11 10 9 6 8 7 3 5 4 2 1 0`.

**pwtw at n = 18: value 2 (optimum 6, lb_best 4, tw 3, nodes 20, cs-dfs 6)** — 18 customers × 10 products, 28 ones; MOSP graph 27 edges, degrees 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0.

```
0 0 0 0 0 1 0 0 0 0
1 0 1 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
0 0 0 1 0 0 0 0 0 1
0 0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 1 0 0 0 0 1 0 0 0
0 0 0 0 0 1 0 1 1 0
0 0 0 0 0 0 0 0 0 0
1 1 0 0 0 0 0 0 1 0
0 0 0 1 0 0 1 1 0 0
0 1 0 0 0 0 0 0 1 0
0 0 0 1 0 0 0 0 0 1
0 0 1 0 0 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 1 1 0 0 0 0 0
```
Witness closing order `5 2 0 4 7 8 1 6 3 9`; elimination ordering of width 3: `12 17 16 15 14 11 3 10 9 6 4 2 13 8 7 5 1 0`.

**pwtw at n = 19: value 2 (optimum 6, lb_best 4, tw 3, nodes 16, cs-dfs 6)** — 19 customers × 10 products, 24 ones; MOSP graph 21 edges, degrees 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 1 0 1 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 1 0 0 1 0 0 0 0
0 0 0 0 0 1 1 0 0 0
0 1 0 0 0 0 0 0 1 1
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 1 0 0 0
0 0 0 0 1 0 0 0 0 0
0 0 0 0 1 0 0 0 1 0
1 0 0 0 0 0 0 0 0 0
0 1 0 1 0 1 0 0 0 0
```
Witness closing order `7 0 9 6 1 8 4 2 5 3`; elimination ordering of width 3: `6 18 17 15 16 14 13 12 11 10 9 8 7 5 4 3 2 1 0`.

**pwtw at n = 20: value 2 (optimum 6, lb_best 4, tw 3, nodes 14, cs-dfs 6)** — 20 customers × 12 products, 25 ones; MOSP graph 24 edges, degrees 5, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0.

```
0 0 0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 1 0 1 0 0 0
0 0 1 1 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 0 1 0 0 0 0
0 0 1 0 0 0 1 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0 0 0 0 0
0 1 0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 0 0 0 0 0 0
0 0 1 0 0 1 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0 0 0
0 1 0 0 0 1 0 0 0 0 0 0
0 1 0 0 0 0 0 0 1 0 0 0
```
Witness closing order `0 4 8 6 2 1 3 7 5 9 10 11`; elimination ordering of width 3: `12 7 18 15 4 11 16 2 19 17 14 13 10 9 8 6 5 3 1 0`.
