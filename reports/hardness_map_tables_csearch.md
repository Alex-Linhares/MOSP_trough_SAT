# Hardness map tables (config `csearch`, raw instances)

37800 rows in 252 cells; 30699 connected. Regenerate: `python -m learning.hardness_map --config csearch`.

### median nodes: fixed, m = 1n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    4 |   10 |   27 |   45 |   88 |  183 |  319 |
|   3 |          3 |    4 |   14 |   44 |  128 |  376 | 1151 | 3255 |
|   4 |          4 |    2 |    9 |   28 |   78 |  252 |  723 | 2146 |
|   5 |          5 |    1 |    4 |   13 |   40 |  116 |  316 |  818 |
|   6 |          6 |    0 |    2 |    8 |   18 |   50 |  120 |  314 |
|   7 |          7 |    0 |    1 |    3 |   10 |   23 |   53 |  112 |
|   8 |          8 |    0 |    0 |    1 |    5 |   12 |   25 |   51 |
|   9 |          9 |    0 |    0 |    0 |    2 |    6 |   12 |   25 |
|  10 |         10 |    0 |    0 |    0 |    1 |    3 |    7 |   13 |

### median nodes: fixed, m = 2n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   18 |   63 |  214 |  733 | 2537 | 8021 |
|   3 |          3 |    2 |   11 |   39 |  120 |  374 | 1249 | 3774 |
|   4 |          4 |    0 |    3 |   12 |   34 |   94 |  232 |  625 |
|   5 |          5 |    0 |    1 |    4 |   12 |   26 |   58 |  138 |
|   6 |          6 |    0 |    0 |    1 |    4 |   10 |   21 |   42 |
|   7 |          7 |    0 |    0 |    0 |    1 |    4 |    9 |   17 |
|   8 |          8 |    0 |    0 |    0 |    0 |    1 |    4 |    7 |
|   9 |          9 |    0 |    0 |    0 |    0 |    0 |    1 |    3 |
|  10 |         10 |    0 |    0 |    0 |    0 |    0 |    0 |    1 |

### median nodes: bernoulli, m = 1n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    5 |    8 |   11 |   14 |   17 |   23 |   38 |
|   0 |          2 |    5 |    8 |   11 |   21 |   57 |  181 |  626 |
|   0 |          2 |    5 |    8 |   20 |   52 |  174 |  590 | 1772 |
|   0 |          3 |    4 |   10 |   30 |   88 |  254 |  578 | 1124 |
|   0 |          4 |    4 |   12 |   31 |   70 |  102 |  161 |  199 |
|   0 |          5 |    5 |   11 |   19 |   30 |   38 |   34 |   37 |
|   0 |          8 |    3 |    4 |    5 |    5 |    4 |    4 |    3 |
|   0 |         10 |    1 |    1 |    1 |    1 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### median nodes: bernoulli, m = 2n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    6 |    9 |   12 |   18 |   25 |   54 |  121 |
|   0 |          2 |    6 |    9 |   20 |   54 |  226 | 1072 | 3342 |
|   0 |          2 |    5 |   10 |   37 |  120 |  350 |  868 | 1411 |
|   0 |          3 |    5 |   14 |   44 |  104 |  170 |  224 |  316 |
|   0 |          4 |    5 |   12 |   21 |   25 |   30 |   28 |   28 |
|   0 |          5 |    3 |    6 |    7 |    7 |    6 |    5 |    5 |
|   0 |          8 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |
|   0 |         10 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### p90 nodes: fixed, m = 1n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    9 |   22 |   56 |   97 |  204 |  449 |  802 |
|   3 |          3 |    7 |   23 |   74 |  208 |  704 | 2291 | 6635 |
|   4 |          4 |    3 |   13 |   45 |  133 |  392 | 1182 | 4244 |
|   5 |          5 |    2 |    7 |   21 |   58 |  175 |  482 | 1235 |
|   6 |          6 |    1 |    4 |   11 |   28 |   71 |  185 |  447 |
|   7 |          7 |    0 |    2 |    6 |   14 |   34 |   73 |  174 |
|   8 |          8 |    0 |    1 |    3 |    8 |   16 |   36 |   68 |
|   9 |          9 |    0 |    0 |    1 |    4 |   10 |   18 |   39 |
|  10 |         10 |    0 |    0 |    1 |    2 |    5 |   11 |   18 |

### p90 nodes: fixed, m = 2n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |    40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|------:|
|   2 |          2 |    8 |   32 |  135 |  483 | 1666 | 5452 | 17508 |
|   3 |          3 |    4 |   17 |   57 |  189 |  673 | 2128 |  6331 |
|   4 |          4 |    1 |    6 |   19 |   47 |  142 |  372 |   929 |
|   5 |          5 |    0 |    2 |    7 |   17 |   38 |   86 |   208 |
|   6 |          6 |    0 |    1 |    3 |    7 |   15 |   30 |    61 |
|   7 |          7 |    0 |    0 |    1 |    3 |    7 |   13 |    23 |
|   8 |          8 |    0 |    0 |    0 |    1 |    3 |    6 |    11 |
|   9 |          9 |    0 |    0 |    0 |    0 |    1 |    3 |     4 |
|  10 |         10 |    0 |    0 |    0 |    0 |    0 |    1 |     2 |

### p90 nodes: bernoulli, m = 1n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    6 |    9 |   13 |   18 |   25 |   48 |  125 |
|   0 |          2 |    6 |   10 |   20 |   52 |  161 |  595 | 2157 |
|   0 |          2 |    6 |   15 |   40 |  125 |  551 | 1631 | 3655 |
|   0 |          3 |    6 |   21 |   68 |  181 |  526 | 1143 | 2182 |
|   0 |          4 |    8 |   22 |   62 |  121 |  186 |  287 |  346 |
|   0 |          5 |    9 |   20 |   37 |   52 |   69 |   63 |   60 |
|   0 |          8 |    7 |    8 |   10 |    8 |    8 |    6 |    5 |
|   0 |         10 |    3 |    3 |    3 |    2 |    1 |    1 |    0 |
|   0 |         12 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |

### p90 nodes: bernoulli, m = 2n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    8 |   11 |   16 |   36 |   58 |  140 |  424 |
|   0 |          2 |    7 |   14 |   41 |  147 |  534 | 2182 | 7988 |
|   0 |          2 |    7 |   20 |   71 |  261 |  671 | 1855 | 3016 |
|   0 |          3 |    8 |   29 |   82 |  182 |  310 |  519 |  526 |
|   0 |          4 |    8 |   23 |   38 |   46 |   50 |   50 |   44 |
|   0 |          5 |    7 |   13 |   13 |   12 |   10 |   11 |    9 |
|   0 |          8 |    3 |    3 |    2 |    1 |    1 |    1 |    0 |
|   0 |         10 |    1 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### Peaks of the median, with bootstrap intervals on the ratio to each neighbour

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_median |   tied | interior   |   ratio_left | ci_left        | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|--------------:|-------:|:-----------|-------------:|:---------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.025 |            1.3  |      5        |      4 | False      |       nan    | edge           | False              |          1    | [0.83, 1.20] | False               |
| bernoulli   |       1 |  15 |        0.15  |            2.4  |     12        |      1 | True       |         1.18 | [1.09, 1.40]   | True               |          1.08 | [0.89, 1.27] | False               |
| bernoulli   |       1 |  20 |        0.15  |            3.1  |     31        |      1 | True       |         1.03 | [0.91, 1.22]   | False              |          1.6  | [1.45, 1.87] | True                |
| bernoulli   |       1 |  25 |        0.1   |            2.56 |     87.5      |      1 | True       |         1.69 | [1.30, 2.00]   | True               |          1.26 | [1.06, 1.47] | True                |
| bernoulli   |       1 |  30 |        0.1   |            3.07 |    254        |      1 | True       |         1.45 | [1.24, 1.75]   | True               |          2.49 | [2.17, 2.93] | True                |
| bernoulli   |       1 |  35 |        0.075 |            2.77 |    590        |      1 | True       |         3.25 | [2.51, 4.11]   | True               |          1.02 | [0.87, 1.26] | False               |
| bernoulli   |       1 |  40 |        0.075 |            3.1  |      1.77e+03 |      1 | True       |         2.83 | [2.24, 3.46]   | True               |          1.57 | [1.35, 1.90] | True                |
| bernoulli   |       2 |  10 |        0.025 |            1.1  |      6        |      1 | False      |       nan    | edge           | False              |          1.08 | [1.00, 1.17] | False               |
| bernoulli   |       2 |  15 |        0.1   |            1.73 |     14        |      1 | True       |         1.36 | [1.17, 1.41]   | True               |          1.15 | [1.00, 1.25] | False               |
| bernoulli   |       2 |  20 |        0.1   |            2.12 |     44.5      |      1 | True       |         1.2  | [1.06, 1.47]   | True               |          2.07 | [1.87, 2.35] | True                |
| bernoulli   |       2 |  25 |        0.075 |            2.04 |    120        |      1 | True       |         2.19 | [1.69, 2.58]   | True               |          1.14 | [0.97, 1.33] | False               |
| bernoulli   |       2 |  30 |        0.075 |            2.35 |    350        |      1 | True       |         1.54 | [1.29, 1.78]   | True               |          2.06 | [1.77, 2.30] | True                |
| bernoulli   |       2 |  35 |        0.05  |            1.91 |      1.07e+03 |      1 | True       |        19.5  | [14.66, 24.83] | True               |          1.23 | [0.93, 1.50] | False               |
| bernoulli   |       2 |  40 |        0.05  |            2.12 |      3.34e+03 |      1 | True       |        27.4  | [20.92, 34.20] | True               |          2.37 | [2.03, 2.89] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |      4        |      2 | False      |       nan    | edge           | False              |          1    | [0.83, 1.20] | False               |
| fixed       |       1 |  15 |        3     |            3    |     14        |      1 | True       |         1.36 | [1.13, 1.78]   | True               |          1.5  | [1.40, 1.78] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |     43.5      |      1 | True       |         1.59 | [1.35, 1.96]   | True               |          1.53 | [1.40, 1.77] | True                |
| fixed       |       1 |  25 |        3     |            3.04 |    128        |      1 | True       |         2.79 | [2.30, 3.21]   | True               |          1.62 | [1.44, 1.83] | True                |
| fixed       |       1 |  30 |        3     |            3.03 |    376        |      1 | True       |         4.27 | [3.53, 4.93]   | True               |          1.49 | [1.25, 1.63] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |      1.15e+03 |      1 | True       |         6.26 | [5.47, 7.53]   | True               |          1.59 | [1.40, 1.77] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |      3.26e+03 |      1 | True       |        10.2  | [8.38, 12.77]  | True               |          1.52 | [1.34, 1.74] | True                |
| fixed       |       2 |  10 |        2     |            2    |      5        |      1 | False      |       nan    | edge           | False              |          2    | [1.25, 2.00] | True                |
| fixed       |       2 |  15 |        2     |            2    |     18        |      1 | False      |       nan    | edge           | False              |          1.58 | [1.46, 1.90] | True                |
| fixed       |       2 |  20 |        2     |            2    |     63        |      1 | False      |       nan    | edge           | False              |          1.6  | [1.45, 1.89] | True                |
| fixed       |       2 |  25 |        2     |            2    |    214        |      1 | False      |       nan    | edge           | False              |          1.77 | [1.46, 2.02] | True                |
| fixed       |       2 |  30 |        2     |            2    |    733        |      1 | False      |       nan    | edge           | False              |          1.96 | [1.67, 2.22] | True                |
| fixed       |       2 |  35 |        2     |            2    |      2.54e+03 |      1 | False      |       nan    | edge           | False              |          2.03 | [1.74, 2.22] | True                |
| fixed       |       2 |  40 |        2     |            2    |      8.02e+03 |      1 | False      |       nan    | edge           | False              |          2.12 | [1.79, 2.41] | True                |

### Peaks of the p90

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_p90 |   tied | interior   |   ratio_left | ci_left        | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|-----------:|-------:|:-----------|-------------:|:---------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.2   |            2.2  |   9        |      1 | True       |         1.11 | [0.89, 1.25]   | False              |          1.25 | [1.00, 1.43] | False               |
| bernoulli   |       1 |  15 |        0.15  |            2.4  |  22        |      1 | True       |         1.05 | [0.95, 1.43]   | False              |          1.09 | [0.91, 1.30] | False               |
| bernoulli   |       1 |  20 |        0.1   |            2.25 |  68        |      1 | True       |         1.68 | [1.33, 1.97]   | True               |          1.09 | [0.92, 1.27] | False               |
| bernoulli   |       1 |  25 |        0.1   |            2.56 | 181        |      1 | True       |         1.44 | [1.14, 1.93]   | True               |          1.49 | [1.24, 1.93] | True                |
| bernoulli   |       1 |  30 |        0.075 |            2.43 | 551        |      1 | True       |         3.4  | [2.51, 4.23]   | True               |          1.05 | [0.78, 1.28] | False               |
| bernoulli   |       1 |  35 |        0.075 |            2.77 |   1.63e+03 |      1 | True       |         2.74 | [1.88, 3.88]   | True               |          1.43 | [0.96, 1.85] | False               |
| bernoulli   |       1 |  40 |        0.075 |            3.1  |   3.66e+03 |      1 | True       |         1.69 | [1.34, 2.23]   | True               |          1.67 | [1.27, 2.16] | True                |
| bernoulli   |       2 |  10 |        0.025 |            1.1  |   8        |      3 | False      |       nan    | edge           | False              |          1.12 | [1.00, 1.12] | False               |
| bernoulli   |       2 |  15 |        0.1   |            1.73 |  29.1      |      1 | True       |         1.43 | [1.12, 1.73]   | True               |          1.25 | [0.96, 1.60] | False               |
| bernoulli   |       2 |  20 |        0.1   |            2.12 |  82.1      |      1 | True       |         1.15 | [0.86, 1.38]   | False              |          2.13 | [1.67, 2.48] | True                |
| bernoulli   |       2 |  25 |        0.075 |            2.04 | 261        |      1 | True       |         1.77 | [1.31, 2.15]   | True               |          1.43 | [1.05, 1.64] | True                |
| bernoulli   |       2 |  30 |        0.075 |            2.35 | 671        |      1 | True       |         1.26 | [0.90, 1.62]   | False              |          2.16 | [1.91, 2.57] | True                |
| bernoulli   |       2 |  35 |        0.05  |            1.91 |   2.18e+03 |      1 | True       |        15.5  | [12.99, 20.30] | True               |          1.18 | [1.02, 1.51] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.12 |   7.99e+03 |      1 | True       |        18.8  | [12.80, 24.12] | True               |          2.65 | [2.23, 3.21] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |   9.1      |      1 | False      |       nan    | edge           | False              |          1.26 | [1.11, 1.61] | True                |
| fixed       |       1 |  15 |        3     |            3    |  23        |      1 | True       |         1.04 | [0.88, 1.19]   | False              |          1.71 | [1.50, 1.92] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |  74.5      |      1 | True       |         1.32 | [1.13, 1.62]   | True               |          1.64 | [1.41, 1.98] | True                |
| fixed       |       1 |  25 |        3     |            3.04 | 208        |      1 | True       |         2.13 | [1.65, 2.62]   | True               |          1.56 | [1.34, 1.85] | True                |
| fixed       |       1 |  30 |        3     |            3.03 | 704        |      1 | True       |         3.44 | [2.70, 4.14]   | True               |          1.8  | [1.44, 2.13] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |   2.29e+03 |      1 | True       |         5.1  | [4.48, 6.17]   | True               |          1.94 | [1.58, 2.33] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |   6.63e+03 |      1 | True       |         8.26 | [6.58, 10.12]  | True               |          1.56 | [1.22, 2.01] | True                |
| fixed       |       2 |  10 |        2     |            2    |   8        |      1 | False      |       nan    | edge           | False              |          1.8  | [1.80, 2.00] | True                |
| fixed       |       2 |  15 |        2     |            2    |  32.1      |      1 | False      |       nan    | edge           | False              |          1.84 | [1.58, 2.16] | True                |
| fixed       |       2 |  20 |        2     |            2    | 135        |      1 | False      |       nan    | edge           | False              |          2.35 | [1.95, 2.64] | True                |
| fixed       |       2 |  25 |        2     |            2    | 483        |      1 | False      |       nan    | edge           | False              |          2.55 | [1.94, 3.09] | True                |
| fixed       |       2 |  30 |        2     |            2    |   1.67e+03 |      1 | False      |       nan    | edge           | False              |          2.47 | [2.13, 3.38] | True                |
| fixed       |       2 |  35 |        2     |            2    |   5.45e+03 |      1 | False      |       nan    | edge           | False              |          2.56 | [2.03, 3.12] | True                |
| fixed       |       2 |  40 |        2     |            2    |   1.75e+04 |      1 | False      |       nan    | edge           | False              |          2.77 | [2.27, 3.60] | True                |

### Peaks of the median, connected instances only

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_median |   tied | interior   |   ratio_left | ci_left       | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|--------------:|-------:|:-----------|-------------:|:--------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.15  |            2.1  |      5        |      2 | True       |         2    | [1.00, 3.26]  | False              |          1    | [0.75, 1.20] | False               |
| bernoulli   |       1 |  15 |        0.075 |            1.93 |     23        |      1 | False      |       nan    | edge          | False              |          1.5  | [1.14, 2.18] | True                |
| bernoulli   |       1 |  20 |        0.1   |            2.45 |     41        |      1 | True       |         1.31 | [0.52, 1.62]  | False              |          1.29 | [0.91, 1.48] | False               |
| bernoulli   |       1 |  25 |        0.1   |            2.68 |    100        |      1 | True       |         1.1  | [0.82, 1.89]  | False              |          1.43 | [1.16, 1.67] | True                |
| bernoulli   |       1 |  30 |        0.1   |            3.1  |    278        |      1 | True       |         1.08 | [0.83, 1.46]  | False              |          2.72 | [2.25, 3.23] | True                |
| bernoulli   |       1 |  35 |        0.075 |            2.86 |    750        |      1 | True       |         4.5  | [1.07, 5.43]  | True               |          1.26 | [1.08, 1.52] | True                |
| bernoulli   |       1 |  40 |        0.075 |            3.15 |      1.95e+03 |      1 | True       |         1.57 | [0.84, 3.10]  | False              |          1.72 | [1.46, 2.22] | True                |
| bernoulli   |       2 |  10 |        0.1   |            1.6  |      5        |      2 | True       |         2    | [1.25, 3.51]  | True               |          1    | [0.75, 1.33] | False               |
| bernoulli   |       2 |  15 |        0.075 |            1.63 |     21        |      1 | False      |       nan    | edge          | False              |          1.38 | [0.81, 2.06] | False               |
| bernoulli   |       2 |  20 |        0.05  |            1.57 |     64        |      1 | False      |       nan    | edge          | False              |          1.29 | [0.53, 1.72] | False               |
| bernoulli   |       2 |  25 |        0.05  |            1.74 |    157        |      1 | False      |       nan    | edge          | False              |          1.12 | [0.71, 1.56] | False               |
| bernoulli   |       2 |  30 |        0.05  |            1.85 |    395        |      1 | False      |       nan    | edge          | False              |          1.12 | [0.86, 1.92] | False               |
| bernoulli   |       2 |  35 |        0.05  |            2    |      1.38e+03 |      1 | False      |       nan    | edge          | False              |          1.59 | [1.38, 2.03] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.17 |      3.52e+03 |      1 | False      |       nan    | edge          | False              |          2.54 | [2.13, 3.22] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |      4.5      |      1 | False      |       nan    | edge          | False              |          1.1  | [0.83, 1.20] | False               |
| fixed       |       1 |  15 |        3     |            3    |     14        |      1 | True       |         1.25 | [0.96, 1.78]  | False              |          1.5  | [1.40, 1.78] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |     43.5      |      1 | True       |         1.44 | [1.13, 2.07]  | True               |          1.53 | [1.38, 1.78] | True                |
| fixed       |       1 |  25 |        3     |            3.04 |    128        |      1 | True       |         2.55 | [2.12, 3.11]  | True               |          1.62 | [1.44, 1.83] | True                |
| fixed       |       1 |  30 |        3     |            3.03 |    376        |      1 | True       |         3.93 | [3.22, 4.60]  | True               |          1.49 | [1.25, 1.62] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |      1.15e+03 |      1 | True       |         5.43 | [3.56, 7.54]  | True               |          1.59 | [1.40, 1.80] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |      3.26e+03 |      1 | True       |         8.38 | [6.82, 15.47] | True               |          1.52 | [1.34, 1.74] | True                |
| fixed       |       2 |  10 |        2     |            2    |      5        |      1 | False      |       nan    | edge          | False              |          2    | [1.38, 2.00] | True                |
| fixed       |       2 |  15 |        2     |            2    |     18        |      1 | False      |       nan    | edge          | False              |          1.58 | [1.50, 1.86] | True                |
| fixed       |       2 |  20 |        2     |            2    |     63        |      1 | False      |       nan    | edge          | False              |          1.6  | [1.48, 1.89] | True                |
| fixed       |       2 |  25 |        2     |            2    |    215        |      1 | False      |       nan    | edge          | False              |          1.78 | [1.48, 2.02] | True                |
| fixed       |       2 |  30 |        2     |            2    |    744        |      1 | False      |       nan    | edge          | False              |          1.99 | [1.71, 2.26] | True                |
| fixed       |       2 |  35 |        2     |            2    |      2.55e+03 |      1 | False      |       nan    | edge          | False              |          2.04 | [1.75, 2.23] | True                |
| fixed       |       2 |  40 |        2     |            2    |      8.08e+03 |      1 | False      |       nan    | edge          | False              |          2.14 | [1.81, 2.45] | True                |

### Kill criterion

```
{
 "bernoulli, m = 1n": {
  "sizes": 7,
  "monotone_at": [],
  "interior_peak_at": [
   15,
   20,
   25,
   30,
   35,
   40
  ],
  "interior_peak_resolved_both_sides_at": [
   25,
   30,
   40
  ],
  "kill_fires": false
 },
 "bernoulli, m = 2n": {
  "sizes": 7,
  "monotone_at": [
   10
  ],
  "interior_peak_at": [
   15,
   20,
   25,
   30,
   35,
   40
  ],
  "interior_peak_resolved_both_sides_at": [
   20,
   30,
   40
  ],
  "kill_fires": false
 },
 "fixed, m = 1n": {
  "sizes": 7,
  "monotone_at": [
   10
  ],
  "interior_peak_at": [
   15,
   20,
   25,
   30,
   35,
   40
  ],
  "interior_peak_resolved_both_sides_at": [
   15,
   20,
   25,
   30,
   35,
   40
  ],
  "kill_fires": false
 },
 "fixed, m = 2n": {
  "sizes": 7,
  "monotone_at": [
   10,
   15,
   20,
   25,
   30,
   35,
   40
  ],
  "interior_peak_at": [],
  "interior_peak_resolved_both_sides_at": [],
  "kill_fires": true
 },
 "overall": {
  "kill_fires": false
 }
}
```

### Sharpness: width of the peak in log10(col_mean) and peak-to-edge ratios

| generator   |   ratio |   n |   peak_median |   width_half_log10 |   width_half_factor | half_note   |   width_tenth_log10 |   width_tenth_factor | tenth_note            |   peak_over_sparsest |   peak_over_densest |
|:------------|--------:|----:|--------------:|-------------------:|--------------------:|:------------|--------------------:|---------------------:|:----------------------|---------------------:|--------------------:|
| bernoulli   |       1 |  10 |      5        |              0.415 |                2.6  | left open   |               0.585 |                 3.85 | left open; right open |                 1    |            6        |
| bernoulli   |       1 |  15 |     12        |              0.455 |                2.85 | left open   |               0.689 |                 4.89 | left open             |                 1.44 |           13        |
| bernoulli   |       1 |  20 |     31        |              0.403 |                2.53 |             |               0.703 |                 5.05 | left open             |                 2.67 |           32        |
| bernoulli   |       1 |  25 |     87.5      |              0.337 |                2.17 |             |               0.663 |                 4.6  | left open             |                 5.9  |           88.5      |
| bernoulli   |       1 |  30 |    254        |              0.264 |                1.84 |             |               0.609 |                 4.07 |                       |                14.2  |          255        |
| bernoulli   |       1 |  35 |    590        |              0.27  |                1.86 |             |               0.559 |                 3.63 |                       |                24.6  |          591        |
| bernoulli   |       1 |  40 |      1.77e+03 |              0.229 |                1.7  |             |               0.494 |                 3.12 |                       |                45.4  |            1.77e+03 |
| bernoulli   |       2 |  10 |      6        |              0.311 |                2.04 | left open   |               0.658 |                 4.55 | left open; right open |                 1    |            7        |
| bernoulli   |       2 |  15 |     14        |              0.415 |                2.6  | left open   |               0.647 |                 4.44 | left open             |                 1.5  |           15        |
| bernoulli   |       2 |  20 |     44.5      |              0.316 |                2.07 |             |               0.599 |                 3.98 | left open             |                 3.5  |           45.5      |
| bernoulli   |       2 |  25 |    119        |              0.272 |                1.87 |             |               0.57  |                 3.72 | left open             |                 6.51 |          120        |
| bernoulli   |       2 |  30 |    349        |              0.258 |                1.81 |             |               0.52  |                 3.31 |                       |                13.5  |          350        |
| bernoulli   |       2 |  35 |      1.07e+03 |              0.223 |                1.67 |             |               0.447 |                 2.8  |                       |                19.5  |            1.07e+03 |
| bernoulli   |       2 |  40 |      3.34e+03 |              0.161 |                1.45 |             |               0.398 |                 2.5  |                       |                27.4  |            3.34e+03 |
| fixed       |       1 |  10 |      4        |              0.323 |                2.11 | left open   |               0.678 |                 4.76 | left open; right open |                 1    |            5        |
| fixed       |       1 |  15 |     14        |              0.313 |                2.06 | left open   |               0.54  |                 3.47 | left open             |                 1.36 |           15        |
| fixed       |       1 |  20 |     43.5      |              0.315 |                2.07 | left open   |               0.514 |                 3.27 | left open             |                 1.59 |           44.5      |
| fixed       |       1 |  25 |    128        |              0.256 |                1.8  |             |               0.496 |                 3.13 | left open             |                 2.79 |           64.2      |
| fixed       |       1 |  30 |    377        |              0.23  |                1.7  |             |               0.476 |                 2.99 | left open             |                 4.27 |           94.4      |
| fixed       |       1 |  35 |      1.15e+03 |              0.202 |                1.59 |             |               0.451 |                 2.83 | left open             |                 6.26 |          144        |
| fixed       |       1 |  40 |      3.26e+03 |              0.193 |                1.56 |             |               0.447 |                 2.8  |                       |                10.2  |          233        |
| fixed       |       2 |  10 |      5        |              0.176 |                1.5  | left open   |               0.699 |                 5    | left open; right open |                 1    |            6        |
| fixed       |       2 |  15 |     18        |              0.203 |                1.59 | left open   |               0.404 |                 2.53 | left open             |                 1    |           19        |
| fixed       |       2 |  20 |     63        |              0.202 |                1.59 | left open   |               0.374 |                 2.37 | left open             |                 1    |           64        |
| fixed       |       2 |  25 |    214        |              0.188 |                1.54 | left open   |               0.349 |                 2.23 | left open             |                 1    |          215        |
| fixed       |       2 |  30 |    733        |              0.178 |                1.51 | left open   |               0.321 |                 2.1  | left open             |                 1    |          734        |
| fixed       |       2 |  35 |      2.54e+03 |              0.172 |                1.49 | left open   |               0.295 |                 1.97 | left open             |                 1    |            2.54e+03 |
| fixed       |       2 |  40 |      8.02e+03 |              0.162 |                1.45 | left open   |               0.284 |                 1.92 | left open             |                 1    |            4.01e+03 |

### Scaling of the median with n (n >= 15, cells with median >= 2)

| generator   |   ratio | where                       |   param |   points |      rate |   doubling_n |   rms_exp |   alpha |   rms_pow | better      |
|:------------|--------:|:----------------------------|--------:|---------:|----------:|-------------:|----------:|--------:|----------:|:------------|
| bernoulli   |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0866  |         3.48 |   0.0208  |   5.05  |   0.107   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.025 |        6 |   0.0253  |        11.9  |   0.0334  |   1.46  |   0.0561  | exponential |
| bernoulli   |       1 | fixed parameter             |   0.05  |        6 |   0.0774  |         3.89 |   0.131   |   4.39  |   0.223   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.075 |        6 |   0.0952  |         3.16 |   0.0463  |   5.52  |   0.158   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.1   |        6 |   0.0833  |         3.62 |   0.0641  |   4.92  |   0.0527  | power       |
| bernoulli   |       1 | fixed parameter             |   0.15  |        6 |   0.0481  |         6.26 |   0.101   |   2.9   |   0.044   | power       |
| bernoulli   |       1 | fixed parameter             |   0.2   |        6 |   0.02    |        15    |   0.0913  |   1.25  |   0.0676  | power       |
| bernoulli   |       1 | fixed parameter             |   0.3   |        6 |  -0.00578 |       inf    |   0.0562  |  -0.287 |   0.0622  | exponential |
| bernoulli   |       1 | fixed parameter             |   0.4   |        0 | nan       |       nan    | nan       | nan     | nan       |             |
| bernoulli   |       1 | fixed parameter             |   0.5   |        0 | nan       |       nan    | nan       | nan     | nan       |             |
| bernoulli   |       2 | ridge (peak cell at each n) | nan     |        6 |   0.0943  |         3.19 |   0.017   |   5.5   |   0.121   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.025 |        6 |   0.0443  |         6.79 |   0.0836  |   2.51  |   0.134   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.05  |        6 |   0.107   |         2.82 |   0.0977  |   6.15  |   0.218   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.075 |        6 |   0.0876  |         3.44 |   0.103   |   5.2   |   0.0404  | power       |
| bernoulli   |       2 | fixed parameter             |   0.1   |        6 |   0.0519  |         5.8  |   0.127   |   3.15  |   0.0646  | power       |
| bernoulli   |       2 | fixed parameter             |   0.15  |        6 |   0.0131  |        23    |   0.0769  |   0.839 |   0.0607  | power       |
| bernoulli   |       2 | fixed parameter             |   0.2   |        6 |  -0.00515 |       inf    |   0.0404  |  -0.268 |   0.0454  | exponential |
| bernoulli   |       2 | fixed parameter             |   0.3   |        0 | nan       |       nan    | nan       | nan     | nan       |             |
| bernoulli   |       2 | fixed parameter             |   0.4   |        0 | nan       |       nan    | nan       | nan     | nan       |             |
| bernoulli   |       2 | fixed parameter             |   0.5   |        0 | nan       |       nan    | nan       | nan     | nan       |             |
| fixed       |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0947  |         3.18 |   0.00844 |   5.53  |   0.109   | exponential |
| fixed       |       1 | fixed parameter             |   2     |        6 |   0.0589  |         5.11 |   0.0426  |   3.46  |   0.0542  | exponential |
| fixed       |       1 | fixed parameter             |   3     |        6 |   0.0947  |         3.18 |   0.00844 |   5.53  |   0.109   | exponential |
| fixed       |       1 | fixed parameter             |   4     |        6 |   0.095   |         3.17 |   0.0107  |   5.55  |   0.113   | exponential |
| fixed       |       1 | fixed parameter             |   5     |        6 |   0.0924  |         3.26 |   0.0317  |   5.43  |   0.0812  | exponential |
| fixed       |       1 | fixed parameter             |   6     |        6 |   0.0854  |         3.52 |   0.0538  |   5.03  |   0.0719  | exponential |
| fixed       |       1 | fixed parameter             |   7     |        5 |   0.0779  |         3.86 |   0.0459  |   5.19  |   0.0139  | power       |
| fixed       |       1 | fixed parameter             |   8     |        4 |   0.0669  |         4.5  |   0.0186  |   4.92  |   0.00934 | power       |
| fixed       |       1 | fixed parameter             |   9     |        4 |   0.0718  |         4.19 |   0.0451  |   5.3   |   0.0229  | power       |
| fixed       |       1 | fixed parameter             |  10     |        3 |   0.0637  |         4.73 |   0.0234  |   5.11  |   0.0126  | power       |
| fixed       |       2 | ridge (peak cell at each n) | nan     |        6 |   0.106   |         2.83 |   0.0104  |   6.21  |   0.121   | exponential |
| fixed       |       2 | fixed parameter             |   2     |        6 |   0.106   |         2.83 |   0.0104  |   6.21  |   0.121   | exponential |
| fixed       |       2 | fixed parameter             |   3     |        6 |   0.101   |         2.98 |   0.0153  |   5.91  |   0.113   | exponential |
| fixed       |       2 | fixed parameter             |   4     |        6 |   0.0905  |         3.33 |   0.0592  |   5.34  |   0.0606  | exponential |
| fixed       |       2 | fixed parameter             |   5     |        5 |   0.0751  |         4.01 |   0.034   |   4.99  |   0.0374  | exponential |
| fixed       |       2 | fixed parameter             |   6     |        4 |   0.0677  |         4.45 |   0.025   |   4.98  |   0.00479 | power       |
| fixed       |       2 | fixed parameter             |   7     |        3 |   0.0628  |         4.79 |   0.0179  |   5.04  |   0.00729 | power       |
| fixed       |       2 | fixed parameter             |   8     |        2 | nan       |       nan    | nan       | nan     | nan       |             |
| fixed       |       2 | fixed parameter             |   9     |        1 | nan       |       nan    | nan       | nan     | nan       |             |
| fixed       |       2 | fixed parameter             |  10     |        0 | nan       |       nan    | nan       | nan     | nan       |             |

### Scaling of the p90 with n

| generator   |   ratio | where                       |   param |   points |      rate |   doubling_n |   rms_exp |   alpha |    rms_pow | better      |
|:------------|--------:|:----------------------------|--------:|---------:|----------:|-------------:|----------:|--------:|-----------:|:------------|
| bernoulli   |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0899  |         3.35 |   0.0328  |   5.26  |   0.092    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.025 |        6 |   0.0433  |         6.96 |   0.0895  |   2.45  |   0.136    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.05  |        6 |   0.0947  |         3.18 |   0.0866  |   5.44  |   0.2      | exponential |
| bernoulli   |       1 | fixed parameter             |   0.075 |        6 |   0.0995  |         3.03 |   0.0647  |   5.82  |   0.126    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.1   |        6 |   0.0813  |         3.7  |   0.0692  |   4.81  |   0.0429   | power       |
| bernoulli   |       1 | fixed parameter             |   0.15  |        6 |   0.0466  |         6.45 |   0.103   |   2.82  |   0.0466   | power       |
| bernoulli   |       1 | fixed parameter             |   0.2   |        6 |   0.0182  |        16.5  |   0.0988  |   1.16  |   0.0763   | power       |
| bernoulli   |       1 | fixed parameter             |   0.3   |        6 |  -0.00982 |       inf    |   0.0522  |  -0.528 |   0.0626   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.4   |        3 |  -0.0176  |       inf    |   0.0415  |  -0.756 |   0.0466   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.5   |        0 | nan       |       nan    | nan       | nan     | nan        |             |
| bernoulli   |       2 | ridge (peak cell at each n) | nan     |        6 |   0.0964  |         3.12 |   0.0363  |   5.6   |   0.143    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.025 |        6 |   0.0626  |         4.81 |   0.0855  |   3.58  |   0.155    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.05  |        6 |   0.112   |         2.7  |   0.0359  |   6.47  |   0.169    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.075 |        6 |   0.0888  |         3.39 |   0.102   |   5.27  |   0.0452   | power       |
| bernoulli   |       2 | fixed parameter             |   0.1   |        6 |   0.051   |         5.91 |   0.122   |   3.09  |   0.0637   | power       |
| bernoulli   |       2 | fixed parameter             |   0.15  |        6 |   0.0103  |        29.3  |   0.0769  |   0.676 |   0.0637   | power       |
| bernoulli   |       2 | fixed parameter             |   0.2   |        6 |  -0.00623 |       inf    |   0.0236  |  -0.357 |   0.0268   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.3   |        2 | nan       |       nan    | nan       | nan     | nan        |             |
| bernoulli   |       2 | fixed parameter             |   0.4   |        0 | nan       |       nan    | nan       | nan     | nan        |             |
| bernoulli   |       2 | fixed parameter             |   0.5   |        0 | nan       |       nan    | nan       | nan     | nan        |             |
| fixed       |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0988  |         3.05 |   0.0176  |   5.77  |   0.123    | exponential |
| fixed       |       1 | fixed parameter             |   2     |        6 |   0.0619  |         4.86 |   0.0328  |   3.63  |   0.0648   | exponential |
| fixed       |       1 | fixed parameter             |   3     |        6 |   0.0988  |         3.05 |   0.0176  |   5.77  |   0.123    | exponential |
| fixed       |       1 | fixed parameter             |   4     |        6 |   0.0988  |         3.05 |   0.024   |   5.77  |   0.123    | exponential |
| fixed       |       1 | fixed parameter             |   5     |        6 |   0.0903  |         3.34 |   0.0187  |   5.28  |   0.0955   | exponential |
| fixed       |       1 | fixed parameter             |   6     |        6 |   0.0819  |         3.68 |   0.0124  |   4.79  |   0.0883   | exponential |
| fixed       |       1 | fixed parameter             |   7     |        6 |   0.0762  |         3.95 |   0.0351  |   4.48  |   0.0627   | exponential |
| fixed       |       1 | fixed parameter             |   8     |        5 |   0.0673  |         4.47 |   0.0347  |   4.48  |   0.0235   | power       |
| fixed       |       1 | fixed parameter             |   9     |        4 |   0.0645  |         4.67 |   0.029   |   4.74  |   0.0241   | power       |
| fixed       |       1 | fixed parameter             |  10     |        4 |   0.0641  |         4.7  |   0.0467  |   4.74  |   0.0232   | power       |
| fixed       |       2 | ridge (peak cell at each n) | nan     |        6 |   0.109   |         2.77 |   0.0344  |   6.38  |   0.0981   | exponential |
| fixed       |       2 | fixed parameter             |   2     |        6 |   0.109   |         2.77 |   0.0344  |   6.38  |   0.0981   | exponential |
| fixed       |       2 | fixed parameter             |   3     |        6 |   0.104   |         2.91 |   0.0196  |   6.06  |   0.113    | exponential |
| fixed       |       2 | fixed parameter             |   4     |        6 |   0.0875  |         3.44 |   0.0261  |   5.12  |   0.089    | exponential |
| fixed       |       2 | fixed parameter             |   5     |        6 |   0.0783  |         3.84 |   0.0534  |   4.62  |   0.0551   | exponential |
| fixed       |       2 | fixed parameter             |   6     |        5 |   0.065   |         4.63 |   0.019   |   4.32  |   0.0286   | exponential |
| fixed       |       2 | fixed parameter             |   7     |        4 |   0.0586  |         5.14 |   0.0309  |   4.32  |   0.00997  | power       |
| fixed       |       2 | fixed parameter             |   8     |        3 |   0.0564  |         5.33 |   0.00891 |   4.52  |   0.000625 | power       |
| fixed       |       2 | fixed parameter             |   9     |        2 | nan       |       nan    | nan       | nan     | nan        |             |
| fixed       |       2 | fixed parameter             |  10     |        1 | nan       |       nan    | nan       | nan     | nan        |             |

### Order parameters: collapse at fixed n (n >= 20) and constancy of the peak location

| candidate    | meaning                          |   dispersion_mean |   r2_mean |   r2_ceiling_mean |   peak_value_mean |   peak_value_cv |   peak_value_min |   peak_value_max |   series_with_interior_peak |
|:-------------|:---------------------------------|------------------:|----------:|------------------:|------------------:|----------------:|-----------------:|-----------------:|----------------------------:|
| g_deg_mean   | mean degree of the MOSP graph    |             0.3   |    0.923  |             0.949 |            6.42   |           0.16  |           5.28   |            8.28  |                          15 |
| opt_frac     | optimum / n                      |             0.317 |    0.909  |             0.949 |            0.34   |           0.158 |           0.28   |            0.45  |                          15 |
| density      | matrix density                   |             0.626 |    0.822  |             0.949 |            0.0953 |           0.316 |           0.0531 |            0.155 |                          15 |
| col_mean     | customers per product (realised) |             0.626 |    0.822  |             0.949 |            2.69   |           0.169 |           1.91   |            3.1   |                          15 |
| bound_gap    | ub_best - lb_best                |             0.721 |    0.312  |             0.949 |            2.27   |           0.513 |           1      |            4     |                          15 |
| g_components | components of the MOSP graph     |             0.781 |    0.0194 |             0.949 |            1.27   |           0.361 |           1      |            2     |                          15 |

### Candidate values at the peak cell

| generator   |   ratio |   n |   peak_param | interior   |   col_mean |   density |   g_deg_mean |   opt_frac |   bound_gap |   g_components |
|:------------|--------:|----:|-------------:|:-----------|-----------:|----------:|-------------:|-----------:|------------:|---------------:|
| bernoulli   |       1 |  20 |        0.15  | True       |       3.1  |    0.155  |         7.15 |      0.45  |           1 |              1 |
| bernoulli   |       1 |  25 |        0.1   | True       |       2.56 |    0.102  |         5.28 |      0.28  |           1 |              2 |
| bernoulli   |       1 |  30 |        0.1   | True       |       3.07 |    0.102  |         7.8  |      0.367 |           2 |              1 |
| bernoulli   |       1 |  35 |        0.075 | True       |       2.77 |    0.0792 |         6.57 |      0.286 |           3 |              2 |
| bernoulli   |       1 |  40 |        0.075 | True       |       3.1  |    0.0775 |         8.28 |      0.325 |           4 |              1 |
| bernoulli   |       2 |  20 |        0.1   | True       |       2.12 |    0.106  |         6.4  |      0.4   |           1 |              1 |
| bernoulli   |       2 |  25 |        0.075 | True       |       2.04 |    0.0816 |         5.92 |      0.36  |           2 |              1 |
| bernoulli   |       2 |  30 |        0.075 | True       |       2.35 |    0.0783 |         8.2  |      0.433 |           2 |              1 |
| bernoulli   |       2 |  35 |        0.05  | True       |       1.91 |    0.0547 |         5.49 |      0.286 |           3 |              2 |
| bernoulli   |       2 |  40 |        0.05  | True       |       2.12 |    0.0531 |         6.95 |      0.325 |           4 |              2 |
| fixed       |       1 |  20 |        3     | True       |       3.05 |    0.152  |         5.4  |      0.35  |           1 |              1 |
| fixed       |       1 |  25 |        3     | True       |       3.04 |    0.122  |         5.6  |      0.32  |           1 |              1 |
| fixed       |       1 |  30 |        3     | True       |       3.03 |    0.101  |         5.67 |      0.333 |           2 |              1 |
| fixed       |       1 |  35 |        3     | True       |       3.06 |    0.0873 |         5.77 |      0.286 |           3 |              1 |
| fixed       |       1 |  40 |        3     | True       |       3.05 |    0.0762 |         5.85 |      0.3   |           4 |              1 |
| fixed       |       2 |  20 |        2     | False      |       2    |    0.1    |         3.7  |      0.3   |           1 |              1 |
| fixed       |       2 |  25 |        2     | False      |       2    |    0.08   |         3.76 |      0.28  |           2 |              1 |
| fixed       |       2 |  30 |        2     | False      |       2    |    0.0667 |         3.8  |      0.267 |           2 |              1 |
| fixed       |       2 |  35 |        2     | False      |       2    |    0.0571 |         3.83 |      0.257 |           3 |              1 |
| fixed       |       2 |  40 |        2     | False      |       2    |    0.05   |         3.85 |      0.25  |           4 |              1 |

### Grid-free peak location per candidate (instances pooled over the four series at each n, 12 quantile bins)

| candidate    |   sizes | peak_values_by_n                                      | interior_at_every_n   |   mean |    cv |
|:-------------|--------:|:------------------------------------------------------|:----------------------|-------:|------:|
| g_components |       2 | 20: 4, 25: 4                                          | True                  | 4      | 0     |
| opt_frac     |       5 | 20: 0.3, 25: 0.32, 30: 0.333, 35: 0.343, 40: 0.25     | True                  | 0.309  | 0.119 |
| col_mean     |       5 | 20: 2.05, 25: 3, 30: 2.73, 35: 2.87, 40: 3            | True                  | 2.73   | 0.145 |
| bound_gap    |       4 | 25: 3, 30: 3, 35: 4, 40: 4                            | False                 | 3.5    | 0.165 |
| density      |       5 | 20: 0.102, 25: 0.12, 30: 0.0911, 35: 0.082, 40: 0.075 | True                  | 0.0941 | 0.189 |
| g_deg_mean   |       5 | 20: 3.8, 25: 5.12, 30: 9.8, 35: 6.91, 40: 8.9         | True                  | 6.91   | 0.363 |

### Monotonicity along density per series and n

| generator   |   ratio |   n | monotone   | rises_then_falls   |
|:------------|--------:|----:|:-----------|:-------------------|
| bernoulli   |       1 |  10 | False      | False              |
| bernoulli   |       1 |  15 | False      | True               |
| bernoulli   |       1 |  20 | False      | True               |
| bernoulli   |       1 |  25 | False      | True               |
| bernoulli   |       1 |  30 | False      | True               |
| bernoulli   |       1 |  35 | False      | True               |
| bernoulli   |       1 |  40 | False      | True               |
| bernoulli   |       2 |  10 | True       | False              |
| bernoulli   |       2 |  15 | False      | True               |
| bernoulli   |       2 |  20 | False      | True               |
| bernoulli   |       2 |  25 | False      | True               |
| bernoulli   |       2 |  30 | False      | True               |
| bernoulli   |       2 |  35 | False      | True               |
| bernoulli   |       2 |  40 | False      | True               |
| fixed       |       1 |  10 | True       | False              |
| fixed       |       1 |  15 | False      | True               |
| fixed       |       1 |  20 | False      | True               |
| fixed       |       1 |  25 | False      | True               |
| fixed       |       1 |  30 | False      | True               |
| fixed       |       1 |  35 | False      | True               |
| fixed       |       1 |  40 | False      | True               |
| fixed       |       2 |  10 | True       | False              |
| fixed       |       2 |  15 | True       | False              |
| fixed       |       2 |  20 | True       | False              |
| fixed       |       2 |  25 | True       | False              |
| fixed       |       2 |  30 | True       | False              |
| fixed       |       2 |  35 | True       | False              |
| fixed       |       2 |  40 | True       | False              |

### Collapse by n: col_mean

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| col_mean    |  10 |     10 |        0.143 | 0.768 |
| col_mean    |  15 |     10 |        0.224 | 0.819 |
| col_mean    |  20 |     10 |        0.321 | 0.82  |
| col_mean    |  25 |     10 |        0.518 | 0.831 |
| col_mean    |  30 |     10 |        0.584 | 0.831 |
| col_mean    |  35 |     10 |        0.799 | 0.817 |
| col_mean    |  40 |     10 |        0.907 | 0.812 |

### Collapse by n: density

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| density     |  10 |     10 |        0.143 | 0.768 |
| density     |  15 |     10 |        0.224 | 0.819 |
| density     |  20 |     10 |        0.321 | 0.82  |
| density     |  25 |     10 |        0.518 | 0.831 |
| density     |  30 |     10 |        0.584 | 0.831 |
| density     |  35 |     10 |        0.799 | 0.817 |
| density     |  40 |     10 |        0.907 | 0.812 |

### Collapse by n: g_deg_mean

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| g_deg_mean  |  10 |      7 |       0.0436 | 0.837 |
| g_deg_mean  |  15 |      8 |       0.0649 | 0.898 |
| g_deg_mean  |  20 |      9 |       0.174  | 0.907 |
| g_deg_mean  |  25 |      9 |       0.186  | 0.924 |
| g_deg_mean  |  30 |      9 |       0.259  | 0.931 |
| g_deg_mean  |  35 |      9 |       0.338  | 0.934 |
| g_deg_mean  |  40 |      9 |       0.542  | 0.919 |

### Collapse by n: opt_frac

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| opt_frac    |  10 |      6 |        0.113 | 0.791 |
| opt_frac    |  15 |      8 |        0.119 | 0.861 |
| opt_frac    |  20 |      9 |        0.205 | 0.888 |
| opt_frac    |  25 |      9 |        0.322 | 0.892 |
| opt_frac    |  30 |      9 |        0.307 | 0.913 |
| opt_frac    |  35 |      9 |        0.388 | 0.917 |
| opt_frac    |  40 |      9 |        0.363 | 0.934 |

### Collapse by n: bound_gap

| candidate   |   n |   bins |   dispersion |      r2 |
|:------------|----:|-------:|-------------:|--------:|
| bound_gap   |  10 |      1 |        0.699 | -4e-15  |
| bound_gap   |  15 |      2 |        0.893 |  0.0106 |
| bound_gap   |  20 |      2 |        0.748 |  0.084  |
| bound_gap   |  25 |      3 |        0.656 |  0.188  |
| bound_gap   |  30 |      3 |        0.535 |  0.32   |
| bound_gap   |  35 |      4 |        0.752 |  0.437  |
| bound_gap   |  40 |      5 |        0.915 |  0.532  |

### Collapse by n: g_components

| candidate    |   n |   bins |   dispersion |      r2 |
|:-------------|----:|-------:|-------------:|--------:|
| g_components |  10 |      3 |        0.492 | 0.119   |
| g_components |  15 |      3 |        0.577 | 0.142   |
| g_components |  20 |      3 |        0.536 | 0.069   |
| g_components |  25 |      2 |        0.641 | 0.00827 |
| g_components |  30 |      2 |        0.602 | 0.00342 |
| g_components |  35 |      2 |        0.908 | 0.00971 |
| g_components |  40 |      2 |        1.22  | 0.00684 |

### Median nodes, connected instances only

**fixed, m = 1n**

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    4 |   11 |   30 |   50 |   95 |  211 |  388 |
|   3 |          3 |    4 |   14 |   44 |  128 |  376 | 1151 | 3255 |
|   4 |          4 |    2 |    9 |   28 |   78 |  252 |  723 | 2146 |
|   5 |          5 |    1 |    4 |   13 |   40 |  116 |  316 |  818 |
|   6 |          6 |    0 |    2 |    8 |   18 |   50 |  120 |  314 |
|   7 |          7 |    0 |    1 |    3 |   10 |   23 |   53 |  112 |
|   8 |          8 |    0 |    0 |    1 |    5 |   12 |   25 |   51 |
|   9 |          9 |    0 |    0 |    0 |    2 |    6 |   12 |   25 |
|  10 |         10 |    0 |    0 |    0 |    1 |    3 |    7 |   13 |

**fixed, m = 2n**

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   18 |   63 |  215 |  744 | 2549 | 8080 |
|   3 |          3 |    2 |   11 |   39 |  120 |  374 | 1249 | 3774 |
|   4 |          4 |    0 |    3 |   12 |   34 |   94 |  232 |  625 |
|   5 |          5 |    0 |    1 |    4 |   12 |   26 |   58 |  138 |
|   6 |          6 |    0 |    0 |    1 |    4 |   10 |   21 |   42 |
|   7 |          7 |    0 |    0 |    0 |    1 |    4 |    9 |   17 |
|   8 |          8 |    0 |    0 |    0 |    0 |    1 |    4 |    7 |
|   9 |          9 |    0 |    0 |    0 |    0 |    0 |    1 |    3 |
|  10 |         10 |    0 |    0 |    0 |    0 |    0 |    0 |    1 |

**bernoulli, m = 1n**

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |  nan |  nan |  nan |  nan |  141 |  166 | 1244 |
|   0 |          2 |  nan |   23 |   31 |   91 |  258 |  750 | 1954 |
|   0 |          3 |    2 |   15 |   41 |  100 |  278 |  597 | 1137 |
|   0 |          4 |    5 |   14 |   32 |   70 |  102 |  161 |  198 |
|   0 |          5 |    5 |   11 |   19 |   30 |   38 |   34 |   37 |
|   0 |          8 |    3 |    4 |    5 |    5 |    4 |    4 |    3 |
|   0 |         10 |    1 |    1 |    1 |    1 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

**bernoulli, m = 2n**

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |  nan |  nan |   64 |  157 |  395 | 1378 | 3518 |
|   0 |          2 |    2 |   21 |   50 |  140 |  351 |  868 | 1384 |
|   0 |          3 |    5 |   15 |   46 |  104 |  171 |  224 |  316 |
|   0 |          4 |    5 |   12 |   21 |   25 |   30 |   28 |   28 |
|   0 |          5 |    3 |    6 |    7 |    7 |    6 |    5 |    5 |
|   0 |          8 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |
|   0 |         10 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### Chu & Stuckey's classes against the campaign's nearest fixed m = n cell

| class           |   instances |   corpus_median_nodes |   corpus_max_nodes |   corpus_col_mean |   corpus_opt_frac |   nearest_cell_d |   cell_col_mean |   cell_median_all |   cell_median_connected |   cell_connected_share |   mean_percentile_in_connected_cell | cell_is_peak   |
|:----------------|------------:|----------------------:|-------------------:|------------------:|------------------:|-----------------:|----------------:|------------------:|------------------------:|-----------------------:|------------------------------------:|:---------------|
| Random-30-30-2  |           5 |            600        |         877        |              2.7  |             0.3   |                3 |            3.03 |        376        |              376        |                  0.993 |                              0.722  | True           |
| Random-30-30-4  |           5 |            159        |         240        |              4.2  |             0.533 |                4 |            4    |        252        |              252        |                  1     |                              0.147  | False          |
| Random-30-30-6  |           5 |             45        |          66        |              5.97 |             0.7   |                6 |            6    |         50        |               50        |                  1     |                              0.445  | False          |
| Random-30-30-8  |           5 |             12        |          15        |              7.83 |             0.833 |                8 |            8    |         12        |               12        |                  1     |                              0.401  | False          |
| Random-30-30-10 |           5 |              3        |           5        |              9.93 |             0.9   |               10 |           10    |          3        |                3        |                  1     |                              0.427  | False          |
| Random-40-40-2  |           5 |              3.45e+03 |           2.17e+04 |              2.8  |             0.275 |                3 |            3.05 |          3.26e+03 |                3.26e+03 |                  1     |                              0.456  | True           |
| Random-40-40-4  |           5 |            984        |           1.34e+03 |              4.25 |             0.525 |                4 |            4    |          2.15e+03 |                2.15e+03 |                  1     |                              0.0427 | False          |
| Random-40-40-6  |           5 |            276        |         415        |              5.92 |             0.7   |                6 |            6    |        314        |              314        |                  1     |                              0.364  | False          |
| Random-40-40-8  |           5 |             38        |          57        |              7.97 |             0.825 |                8 |            8    |         51        |               51        |                  1     |                              0.235  | False          |
| Random-40-40-10 |           5 |             15        |          24        |              9.9  |             0.9   |               10 |           10    |         13        |               13        |                  1     |                              0.527  | False          |

### Chu & Stuckey's instances

| instance_name       |   n |   d |   optimum |   col_mean |   g_deg_mean |   g_components |   bound_gap |   nodes |
|:--------------------|----:|----:|----------:|-----------:|-------------:|---------------:|------------:|--------:|
| Random-30-30-2-1_0  |  30 |   2 |         9 |       2.8  |         5.33 |              1 |           1 |     615 |
| Random-30-30-2-2_0  |  30 |   2 |         8 |       2.7  |         5.53 |              1 |           1 |     178 |
| Random-30-30-2-3_0  |  30 |   2 |         9 |       2.73 |         5.47 |              1 |           2 |     877 |
| Random-30-30-2-4_0  |  30 |   2 |         9 |       2.7  |         5.2  |              1 |           2 |     600 |
| Random-30-30-2-5_0  |  30 |   2 |         8 |       2.63 |         4.67 |              1 |           3 |     587 |
| Random-30-30-4-1_0  |  30 |   4 |        17 |       4.73 |        14.2  |              1 |           1 |     125 |
| Random-30-30-4-2_0  |  30 |   4 |        15 |       4.2  |        11.8  |              1 |           4 |     167 |
| Random-30-30-4-3_0  |  30 |   4 |        16 |       4.37 |        13    |              1 |           2 |      89 |
| Random-30-30-4-4_0  |  30 |   4 |        15 |       3.83 |        11.5  |              1 |           3 |     240 |
| Random-30-30-4-5_0  |  30 |   4 |        17 |       4.13 |        12.7  |              1 |           1 |     159 |
| Random-30-30-6-1_0  |  30 |   6 |        23 |       6.6  |        22.5  |              1 |           1 |      21 |
| Random-30-30-6-2_0  |  30 |   6 |        20 |       5.43 |        17.7  |              1 |           1 |      64 |
| Random-30-30-6-3_0  |  30 |   6 |        22 |       6.07 |        20.7  |              1 |           1 |      45 |
| Random-30-30-6-4_0  |  30 |   6 |        21 |       5.97 |        19.5  |              1 |           2 |      43 |
| Random-30-30-6-5_0  |  30 |   6 |        20 |       5.33 |        18.1  |              1 |           1 |      66 |
| Random-30-30-8-1_0  |  30 |   8 |        25 |       8.07 |        24.8  |              1 |           1 |      15 |
| Random-30-30-8-2_0  |  30 |   8 |        25 |       7.37 |        24.9  |              1 |           0 |      13 |
| Random-30-30-8-3_0  |  30 |   8 |        26 |       8.23 |        26.3  |              1 |           0 |       8 |
| Random-30-30-8-4_0  |  30 |   8 |        25 |       7.83 |        24.5  |              1 |           1 |       8 |
| Random-30-30-8-5_0  |  30 |   8 |        25 |       7.63 |        24.9  |              1 |           0 |      12 |
| Random-30-30-10-1_0 |  30 |  10 |        27 |       9.93 |        27.9  |              1 |           0 |       3 |
| Random-30-30-10-2_0 |  30 |  10 |        26 |       8.97 |        26.9  |              1 |           0 |       5 |
| Random-30-30-10-3_0 |  30 |  10 |        27 |      10.6  |        28.2  |              1 |           0 |       1 |
| Random-30-30-10-4_0 |  30 |  10 |        27 |       9.93 |        27.6  |              1 |           1 |       3 |
| Random-30-30-10-5_0 |  30 |  10 |        28 |       9.87 |        28.3  |              1 |           0 |       3 |
| Random-40-40-2-1_0  |  40 |   2 |        11 |       2.8  |         6.05 |              1 |           4 |    3448 |
| Random-40-40-2-2_0  |  40 |   2 |        14 |       2.92 |         6.85 |              1 |           6 |   21745 |
| Random-40-40-2-3_0  |  40 |   2 |        10 |       2.7  |         5.25 |              1 |           4 |    1017 |
| Random-40-40-2-4_0  |  40 |   2 |         7 |       2.48 |         4.05 |              1 |           4 |    1049 |
| Random-40-40-2-5_0  |  40 |   2 |        13 |       3    |         8.25 |              1 |           5 |    3780 |
| Random-40-40-4-1_0  |  40 |   4 |        21 |       4.25 |        13.6  |              1 |           4 |    1096 |
| Random-40-40-4-2_0  |  40 |   4 |        21 |       4.28 |        14.2  |              1 |           2 |     984 |
| Random-40-40-4-3_0  |  40 |   4 |        19 |       4.12 |        12.8  |              1 |           4 |    1337 |
| Random-40-40-4-4_0  |  40 |   4 |        18 |       4.1  |        12.8  |              1 |           3 |     478 |
| Random-40-40-4-5_0  |  40 |   4 |        22 |       4.35 |        15.3  |              1 |           3 |     612 |
| Random-40-40-6-1_0  |  40 |   6 |        28 |       6.17 |        23.6  |              1 |           2 |     213 |
| Random-40-40-6-2_0  |  40 |   6 |        30 |       6.15 |        23.9  |              1 |           2 |     220 |
| Random-40-40-6-3_0  |  40 |   6 |        26 |       5.83 |        21.1  |              1 |           1 |     281 |
| Random-40-40-6-4_0  |  40 |   6 |        29 |       5.72 |        21.6  |              1 |           2 |     415 |
| Random-40-40-6-5_0  |  40 |   6 |        28 |       5.92 |        23.3  |              1 |           1 |     276 |
| Random-40-40-8-1_0  |  40 |   8 |        34 |       8.2  |        32.5  |              1 |           1 |      38 |
| Random-40-40-8-2_0  |  40 |   8 |        32 |       7.97 |        30.4  |              1 |           2 |      31 |
| Random-40-40-8-3_0  |  40 |   8 |        30 |       7.53 |        27.9  |              1 |           1 |      57 |
| Random-40-40-8-4_0  |  40 |   8 |        33 |       7.8  |        30.6  |              1 |           1 |      42 |
| Random-40-40-8-5_0  |  40 |   8 |        34 |       8.22 |        32.1  |              1 |           1 |      30 |
| Random-40-40-10-1_0 |  40 |  10 |        36 |       9.9  |        35.8  |              1 |           0 |      15 |
| Random-40-40-10-2_0 |  40 |  10 |        36 |       9.97 |        35.1  |              1 |           0 |      15 |
| Random-40-40-10-3_0 |  40 |  10 |        34 |       9.32 |        33.2  |              1 |           2 |      24 |
| Random-40-40-10-4_0 |  40 |  10 |        36 |       9.9  |        35.8  |              1 |           0 |      12 |
| Random-40-40-10-5_0 |  40 |  10 |        35 |      10    |        36    |              1 |           0 |       8 |

### 125 x 125 refutation counts on record (recertify/results.json) -- item 06's data, listed only

| name                 |   d |   col_mean |   optimum |   value | status   |        nodes |   hours |   lb_best |   ub_best |
|:---------------------|----:|-----------:|----------:|--------:|:---------|-------------:|--------:|----------:|----------:|
| Random-125-125-4-5_0 |   4 |       3.94 |        46 |      46 | unsat    |  48904669193 |    10.2 |        23 |        51 |
| Random-125-125-4-2_0 |   4 |       4.29 |        57 |      57 | unsat    |  60830884980 |    13.3 |        27 |        63 |
| Random-125-125-2-1_0 |   2 |       2.73 |        24 |      24 | unsat    | 162268751357 |    25   |        13 |        29 |
| Random-125-125-2-4_0 |   2 |       2.78 |        24 |      24 | unsat    | 167770785378 |    28.3 |        15 |        29 |
| Random-125-125-4-4_0 |   4 |       4.09 |        51 |      51 | unsat    | 259718252374 |    53.5 |        24 |        55 |

