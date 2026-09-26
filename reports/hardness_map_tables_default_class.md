# Hardness map tables (config `default`, one row per isomorphism class per cell)

27321 rows in 252 cells; 21253 connected. Regenerate: `python -m learning.hardness_map --config default --per-class`.

### median nodes: fixed, m = 1n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   12 |   34 |   58 |  109 |  244 |  473 |
|   3 |          3 |    5 |   16 |   53 |  155 |  460 | 1402 | 3953 |
|   4 |          4 |    2 |    9 |   30 |   89 |  288 |  830 | 2477 |
|   5 |          5 |    1 |    4 |   14 |   43 |  126 |  338 |  890 |
|   6 |          6 |    0 |    2 |    8 |   18 |   50 |  120 |  314 |
|   7 |          7 |    0 |    1 |    3 |   10 |   23 |   53 |  112 |
|   8 |          8 |    0 |    1 |    2 |    5 |   12 |   25 |   51 |
|   9 |          9 |    0 |    0 |    1 |    2 |    6 |   12 |   25 |
|  10 |         10 |    0 |    0 |    1 |    1 |    3 |    7 |   13 |

### median nodes: fixed, m = 2n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   23 |   82 |  262 |  940 | 3080 | 9968 |
|   3 |          3 |    2 |   11 |   39 |  120 |  374 | 1249 | 3774 |
|   4 |          4 |    1 |    3 |   12 |   34 |   94 |  232 |  625 |
|   5 |          5 |    0 |    1 |    4 |   12 |   26 |   58 |  138 |
|   6 |          6 |    0 |    0 |    1 |    4 |   10 |   21 |   42 |
|   7 |          7 |    0 |    0 |    1 |    1 |    4 |    9 |   17 |
|   8 |          8 |    0 |    0 |    0 |    1 |    1 |    4 |    7 |
|   9 |          9 |    0 |    0 |    0 |    0 |    1 |    2 |    3 |
|  10 |         10 |    0 |    0 |    0 |    0 |    0 |    1 |    1 |

### median nodes: bernoulli, m = 1n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |    4 |    8 |   11 |   15 |   19 |   27 |   48 |
|   0 |          2 |    4 |    8 |   12 |   26 |   82 |  269 |  960 |
|   0 |          2 |    5 |    9 |   23 |   74 |  250 |  796 | 2222 |
|   0 |          3 |    5 |   12 |   40 |  112 |  340 |  718 | 1313 |
|   0 |          4 |    5 |   16 |   38 |   80 |  110 |  164 |  199 |
|   0 |          5 |    6 |   13 |   20 |   32 |   38 |   34 |   37 |
|   0 |          8 |    4 |    5 |    5 |    5 |    4 |    4 |    3 |
|   0 |         10 |    2 |    2 |    1 |    1 |    1 |    1 |    0 |
|   0 |         12 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |

### median nodes: bernoulli, m = 2n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    5 |    9 |   13 |   19 |   30 |   72 |  166 |
|   0 |          2 |    5 |    9 |   25 |   71 |  325 | 1339 | 4270 |
|   0 |          2 |    5 |   12 |   52 |  148 |  394 |  876 | 1411 |
|   0 |          3 |    6 |   17 |   52 |  114 |  172 |  224 |  316 |
|   0 |          4 |    6 |   14 |   21 |   25 |   30 |   28 |   28 |
|   0 |          5 |    4 |    6 |    7 |    7 |    6 |    5 |    5 |
|   0 |          7 |    1 |    1 |    1 |    1 |    1 |    0 |    0 |
|   0 |         10 |    1 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### p90 nodes: fixed, m = 1n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |   12 |   27 |   70 |  125 |  302 |  657 | 1052 |
|   3 |          3 |    8 |   26 |   93 |  261 |  874 | 2777 | 8071 |
|   4 |          4 |    4 |   14 |   50 |  152 |  464 | 1441 | 4859 |
|   5 |          5 |    2 |    7 |   22 |   66 |  195 |  507 | 1305 |
|   6 |          6 |    1 |    4 |   11 |   28 |   71 |  185 |  447 |
|   7 |          7 |    1 |    2 |    6 |   14 |   34 |   73 |  174 |
|   8 |          8 |    0 |    1 |    3 |    8 |   16 |   36 |   68 |
|   9 |          9 |    0 |    1 |    2 |    4 |   10 |   18 |   39 |
|  10 |         10 |    0 |    0 |    1 |    2 |    5 |   11 |   18 |

### p90 nodes: fixed, m = 2n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |    40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|------:|
|   2 |          2 |   11 |   40 |  174 |  607 | 2131 | 6580 | 22004 |
|   3 |          3 |    4 |   17 |   57 |  189 |  673 | 2128 |  6331 |
|   4 |          4 |    2 |    6 |   19 |   47 |  142 |  372 |   929 |
|   5 |          5 |    1 |    2 |    7 |   17 |   38 |   86 |   208 |
|   6 |          6 |    0 |    1 |    3 |    7 |   15 |   30 |    61 |
|   7 |          7 |    0 |    1 |    2 |    3 |    7 |   13 |    23 |
|   8 |          8 |    0 |    0 |    1 |    2 |    3 |    6 |    11 |
|   9 |          9 |    0 |    0 |    1 |    1 |    2 |    3 |     4 |
|  10 |         10 |    0 |    0 |    0 |    1 |    2 |    2 |     3 |

### p90 nodes: bernoulli, m = 1n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |    7 |   10 |   15 |   22 |   33 |   79 |  168 |
|   0 |          2 |    7 |   12 |   27 |   81 |  258 |  908 | 2946 |
|   0 |          2 |    8 |   18 |   54 |  196 |  744 | 2042 | 4635 |
|   0 |          3 |    8 |   24 |   91 |  245 |  672 | 1402 | 2564 |
|   0 |          4 |   10 |   29 |   78 |  139 |  208 |  301 |  346 |
|   0 |          5 |   11 |   24 |   43 |   59 |   69 |   63 |   60 |
|   0 |          8 |    7 |   10 |   10 |    8 |    8 |    6 |    5 |
|   0 |         10 |    4 |    3 |    3 |    3 |    2 |    2 |    1 |
|   0 |         12 |    2 |    2 |    1 |    1 |    0 |    1 |    0 |

### p90 nodes: bernoulli, m = 2n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    8 |   12 |   19 |   44 |   78 |  183 |  677 |
|   0 |          2 |    7 |   17 |   59 |  207 |  812 | 3037 | 9915 |
|   0 |          2 |    9 |   28 |   94 |  330 |  856 | 1974 | 3016 |
|   0 |          3 |    9 |   35 |   99 |  218 |  310 |  519 |  526 |
|   0 |          4 |   10 |   29 |   38 |   46 |   50 |   50 |   44 |
|   0 |          5 |    7 |   13 |   13 |   12 |   10 |   11 |    9 |
|   0 |          7 |    3 |    3 |    3 |    2 |    1 |    1 |    1 |
|   0 |         10 |    3 |    1 |    2 |    1 |    0 |    0 |    0 |
|   0 |         12 |    1 |    0 |    0 |    0 |    0 |    0 |    0 |

### Peaks of the median, with bootstrap intervals on the ratio to each neighbour

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_median |   tied | interior   |   ratio_left | ci_left        | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|--------------:|-------:|:-----------|-------------:|:---------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.2   |            2.2  |      6        |      1 | True       |         1.17 | [0.86, 1.40]   | False              |          1.4  | [1.20, 1.75] | True                |
| bernoulli   |       1 |  15 |        0.15  |            2.4  |     16        |      1 | True       |         1.31 | [1.07, 1.55]   | True               |          1.21 | [1.00, 1.32] | False               |
| bernoulli   |       1 |  20 |        0.1   |            2.25 |     40.5      |      1 | True       |         1.73 | [1.41, 1.96]   | True               |          1.05 | [0.87, 1.19] | False               |
| bernoulli   |       1 |  25 |        0.1   |            2.56 |    112        |      1 | True       |         1.5  | [1.34, 1.79]   | True               |          1.39 | [1.24, 1.57] | True                |
| bernoulli   |       1 |  30 |        0.1   |            3.07 |    340        |      1 | True       |         1.36 | [1.12, 1.71]   | True               |          3.07 | [2.55, 3.48] | True                |
| bernoulli   |       1 |  35 |        0.075 |            2.77 |    796        |      1 | True       |         2.95 | [2.46, 3.80]   | True               |          1.11 | [0.96, 1.34] | False               |
| bernoulli   |       1 |  40 |        0.075 |            3.1  |      2.22e+03 |      1 | True       |         2.31 | [1.96, 2.90]   | True               |          1.69 | [1.47, 2.02] | True                |
| bernoulli   |       2 |  10 |        0.1   |            1.4  |      6        |      1 | True       |         1.17 | [0.86, 1.17]   | False              |          1.08 | [0.86, 1.17] | False               |
| bernoulli   |       2 |  15 |        0.1   |            1.73 |     17        |      1 | True       |         1.38 | [1.21, 1.65]   | True               |          1.2  | [1.03, 1.46] | True                |
| bernoulli   |       2 |  20 |        0.1   |            2.12 |     52.5      |      1 | True       |         1.02 | [0.91, 1.26]   | False              |          2.43 | [2.23, 2.85] | True                |
| bernoulli   |       2 |  25 |        0.075 |            2.04 |    148        |      1 | True       |         2.06 | [1.66, 2.43]   | True               |          1.3  | [1.13, 1.56] | True                |
| bernoulli   |       2 |  30 |        0.075 |            2.35 |    394        |      1 | True       |         1.21 | [0.98, 1.52]   | False              |          2.29 | [2.03, 2.66] | True                |
| bernoulli   |       2 |  35 |        0.05  |            1.91 |      1.34e+03 |      1 | True       |        18.4  | [15.42, 25.61] | True               |          1.53 | [1.22, 1.91] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.12 |      4.27e+03 |      1 | True       |        25.6  | [19.05, 32.58] | True               |          3.02 | [2.55, 3.60] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |      5        |      2 | False      |       nan    | edge           | False              |          1    | [0.83, 1.20] | False               |
| fixed       |       1 |  15 |        3     |            3    |     16.5      |      1 | True       |         1.35 | [1.13, 1.71]   | True               |          1.75 | [1.55, 1.90] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |     53        |      1 | True       |         1.54 | [1.35, 1.93]   | True               |          1.74 | [1.58, 1.97] | True                |
| fixed       |       1 |  25 |        3     |            3.04 |    155        |      1 | True       |         2.67 | [2.25, 3.02]   | True               |          1.73 | [1.48, 1.92] | True                |
| fixed       |       1 |  30 |        3     |            3.03 |    460        |      1 | True       |         4.19 | [3.46, 4.81]   | True               |          1.59 | [1.40, 1.75] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |      1.4e+03  |      1 | True       |         5.71 | [4.35, 6.94]   | True               |          1.69 | [1.48, 1.92] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |      3.95e+03 |      1 | True       |         8.34 | [6.68, 11.19]  | True               |          1.6  | [1.37, 1.85] | True                |
| fixed       |       2 |  10 |        2     |            2    |      5        |      1 | False      |       nan    | edge           | False              |          2    | [1.50, 2.33] | True                |
| fixed       |       2 |  15 |        2     |            2    |     23        |      1 | False      |       nan    | edge           | False              |          2    | [1.77, 2.35] | True                |
| fixed       |       2 |  20 |        2     |            2    |     82.5      |      1 | False      |       nan    | edge           | False              |          2.09 | [1.84, 2.38] | True                |
| fixed       |       2 |  25 |        2     |            2    |    262        |      1 | False      |       nan    | edge           | False              |          2.16 | [1.96, 2.54] | True                |
| fixed       |       2 |  30 |        2     |            2    |    940        |      1 | False      |       nan    | edge           | False              |          2.51 | [2.17, 2.75] | True                |
| fixed       |       2 |  35 |        2     |            2    |      3.08e+03 |      1 | False      |       nan    | edge           | False              |          2.46 | [2.17, 2.83] | True                |
| fixed       |       2 |  40 |        2     |            2    |      9.97e+03 |      1 | False      |       nan    | edge           | False              |          2.64 | [2.15, 3.09] | True                |

### Peaks of the p90

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_p90 |   tied | interior   |   ratio_left | ci_left        | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|-----------:|-------:|:-----------|-------------:|:---------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.2   |            2.2  |  11        |      1 | True       |         1.09 | [0.86, 1.33]   | False              |          1.5  | [1.06, 1.62] | True                |
| bernoulli   |       1 |  15 |        0.15  |            2.4  |  29.1      |      1 | True       |         1.19 | [0.84, 1.50]   | False              |          1.2  | [0.93, 1.53] | False               |
| bernoulli   |       1 |  20 |        0.1   |            2.25 |  91.1      |      1 | True       |         1.67 | [1.30, 1.92]   | True               |          1.17 | [0.94, 1.39] | False               |
| bernoulli   |       1 |  25 |        0.1   |            2.56 | 245        |      1 | True       |         1.25 | [0.98, 1.67]   | False              |          1.76 | [1.44, 2.17] | True                |
| bernoulli   |       1 |  30 |        0.075 |            2.43 | 744        |      1 | True       |         2.87 | [2.17, 3.71]   | True               |          1.11 | [0.88, 1.39] | False               |
| bernoulli   |       1 |  35 |        0.075 |            2.77 |   2.04e+03 |      1 | True       |         2.25 | [1.62, 3.08]   | True               |          1.46 | [1.04, 1.83] | True                |
| bernoulli   |       1 |  40 |        0.075 |            3.1  |   4.64e+03 |      1 | True       |         1.57 | [1.24, 1.90]   | True               |          1.81 | [1.41, 2.24] | True                |
| bernoulli   |       2 |  10 |        0.15  |            1.7  |  10        |      1 | True       |         1.1  | [1.00, 1.33]   | False              |          1.38 | [1.22, 1.50] | True                |
| bernoulli   |       2 |  15 |        0.1   |            1.73 |  35.1      |      1 | True       |         1.24 | [1.03, 1.66]   | True               |          1.2  | [1.00, 1.62] | True                |
| bernoulli   |       2 |  20 |        0.1   |            2.12 |  99.4      |      1 | True       |         1.06 | [0.85, 1.30]   | False              |          2.57 | [2.10, 2.97] | True                |
| bernoulli   |       2 |  25 |        0.075 |            2.04 | 330        |      1 | True       |         1.59 | [1.22, 2.00]   | True               |          1.51 | [1.26, 1.97] | True                |
| bernoulli   |       2 |  30 |        0.075 |            2.35 | 856        |      1 | True       |         1.05 | [0.86, 1.44]   | False              |          2.76 | [2.30, 3.21] | True                |
| bernoulli   |       2 |  35 |        0.05  |            1.91 |   3.04e+03 |      1 | True       |        16.5  | [11.75, 22.12] | True               |          1.54 | [1.26, 1.93] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.12 |   9.91e+03 |      1 | True       |        14.6  | [11.27, 21.53] | True               |          3.29 | [2.73, 4.15] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |  12        |      1 | False      |       nan    | edge           | False              |          1.44 | [1.22, 1.73] | True                |
| fixed       |       1 |  15 |        2     |            2.13 |  27.2      |      1 | False      |       nan    | edge           | False              |          1.04 | [0.90, 1.27] | False               |
| fixed       |       1 |  20 |        3     |            3.05 |  93.1      |      1 | True       |         1.32 | [1.14, 1.59]   | True               |          1.84 | [1.64, 2.16] | True                |
| fixed       |       1 |  25 |        3     |            3.04 | 261        |      1 | True       |         2.08 | [1.63, 2.46]   | True               |          1.72 | [1.44, 1.96] | True                |
| fixed       |       1 |  30 |        3     |            3.03 | 874        |      1 | True       |         2.89 | [2.37, 3.50]   | True               |          1.88 | [1.55, 2.27] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |   2.78e+03 |      1 | True       |         4.22 | [3.72, 5.07]   | True               |          1.93 | [1.68, 2.43] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |   8.07e+03 |      1 | True       |         7.67 | [5.61, 8.95]   | True               |          1.66 | [1.41, 2.23] | True                |
| fixed       |       2 |  10 |        2     |            2    |  11        |      1 | False      |       nan    | edge           | False              |          2.4  | [2.02, 2.62] | True                |
| fixed       |       2 |  15 |        2     |            2    |  40        |      1 | False      |       nan    | edge           | False              |          2.28 | [2.05, 2.71] | True                |
| fixed       |       2 |  20 |        2     |            2    | 174        |      1 | False      |       nan    | edge           | False              |          3.02 | [2.60, 3.43] | True                |
| fixed       |       2 |  25 |        2     |            2    | 607        |      1 | False      |       nan    | edge           | False              |          3.2  | [2.60, 3.93] | True                |
| fixed       |       2 |  30 |        2     |            2    |   2.13e+03 |      1 | False      |       nan    | edge           | False              |          3.16 | [2.78, 4.28] | True                |
| fixed       |       2 |  35 |        2     |            2    |   6.58e+03 |      1 | False      |       nan    | edge           | False              |          3.09 | [2.59, 3.86] | True                |
| fixed       |       2 |  40 |        2     |            2    |   2.2e+04  |      1 | False      |       nan    | edge           | False              |          3.48 | [2.80, 4.56] | True                |

### Peaks of the median, connected instances only

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_median |   tied | interior   |   ratio_left | ci_left       | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|--------------:|-------:|:-----------|-------------:|:--------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.15  |            2.1  |      6        |      2 | True       |         2.33 | [1.17, 3.50]  | True               |          1    | [0.86, 1.29] | False               |
| bernoulli   |       1 |  15 |        0.075 |            1.93 |     40        |      1 | False      |       nan    | edge          | False              |          2.28 | [1.52, 3.73] | True                |
| bernoulli   |       1 |  20 |        0.1   |            2.45 |     51        |      1 | True       |         1.44 | [0.48, 2.00]  | False              |          1.3  | [1.08, 1.65] | True                |
| bernoulli   |       1 |  25 |        0.1   |            2.68 |    121        |      1 | True       |         1.03 | [0.58, 1.64]  | False              |          1.51 | [1.30, 1.84] | True                |
| bernoulli   |       1 |  30 |        0.1   |            3.1  |    366        |      1 | True       |         1.07 | [0.82, 1.31]  | False              |          3.3  | [2.65, 3.65] | True                |
| bernoulli   |       1 |  35 |        0.075 |            2.86 |      1.05e+03 |      1 | True       |         2.85 | [0.94, 4.90]  | False              |          1.43 | [1.13, 1.70] | True                |
| bernoulli   |       1 |  40 |        0.075 |            3.15 |      2.45e+03 |      1 | True       |         1.22 | [0.82, 2.69]  | False              |          1.85 | [1.61, 2.37] | True                |
| bernoulli   |       2 |  10 |        0.15  |            1.8  |      6        |      1 | True       |         1.17 | [0.75, 1.40]  | False              |          1.75 | [1.20, 2.00] | True                |
| bernoulli   |       2 |  15 |        0.075 |            1.63 |     29        |      1 | False      |       nan    | edge          | False              |          1.58 | [0.83, 2.21] | False               |
| bernoulli   |       2 |  20 |        0.05  |            1.57 |     74        |      1 | False      |       nan    | edge          | False              |          1.08 | [0.61, 1.44] | False               |
| bernoulli   |       2 |  25 |        0.05  |            1.74 |    222        |      1 | False      |       nan    | edge          | False              |          1.3  | [0.77, 2.32] | False               |
| bernoulli   |       2 |  30 |        0.05  |            1.85 |    491        |      1 | False      |       nan    | edge          | False              |          1.21 | [0.91, 2.15] | False               |
| bernoulli   |       2 |  35 |        0.05  |            2    |      1.87e+03 |      1 | False      |       nan    | edge          | False              |          2.14 | [1.83, 2.54] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.17 |      4.58e+03 |      1 | False      |       nan    | edge          | False              |          3.31 | [2.70, 4.28] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |      5        |      2 | False      |       nan    | edge          | False              |          1    | [0.83, 1.40] | False               |
| fixed       |       1 |  15 |        3     |            3    |     16.5      |      1 | True       |         1.25 | [0.94, 1.64]  | False              |          1.75 | [1.55, 1.90] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |     53        |      1 | True       |         1.38 | [1.11, 2.15]  | True               |          1.74 | [1.59, 1.97] | True                |
| fixed       |       1 |  25 |        3     |            3.04 |    155        |      1 | True       |         2.42 | [2.03, 2.95]  | True               |          1.73 | [1.50, 1.93] | True                |
| fixed       |       1 |  30 |        3     |            3.03 |    455        |      1 | True       |         3.74 | [3.19, 4.60]  | True               |          1.58 | [1.40, 1.76] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |      1.4e+03  |      1 | True       |         4.26 | [3.05, 6.73]  | True               |          1.69 | [1.49, 1.92] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |      3.95e+03 |      1 | True       |         6.52 | [4.92, 11.99] | True               |          1.6  | [1.38, 1.86] | True                |
| fixed       |       2 |  10 |        2     |            2    |      5        |      1 | False      |       nan    | edge          | False              |          2    | [1.50, 2.33] | True                |
| fixed       |       2 |  15 |        2     |            2    |     23        |      1 | False      |       nan    | edge          | False              |          2    | [1.79, 2.30] | True                |
| fixed       |       2 |  20 |        2     |            2    |     82.5      |      1 | False      |       nan    | edge          | False              |          2.09 | [1.82, 2.41] | True                |
| fixed       |       2 |  25 |        2     |            2    |    267        |      1 | False      |       nan    | edge          | False              |          2.21 | [1.97, 2.56] | True                |
| fixed       |       2 |  30 |        2     |            2    |    949        |      1 | False      |       nan    | edge          | False              |          2.54 | [2.20, 2.76] | True                |
| fixed       |       2 |  35 |        2     |            2    |      3.11e+03 |      1 | False      |       nan    | edge          | False              |          2.49 | [2.20, 2.84] | True                |
| fixed       |       2 |  40 |        2     |            2    |      9.99e+03 |      1 | False      |       nan    | edge          | False              |          2.65 | [2.19, 3.13] | True                |

### Kill criterion

```
{
 "bernoulli, m = 1n": {
  "sizes": 7,
  "monotone_at": [],
  "interior_peak_at": [
   10,
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
  "monotone_at": [],
  "interior_peak_at": [
   10,
   15,
   20,
   25,
   30,
   35,
   40
  ],
  "interior_peak_resolved_both_sides_at": [
   15,
   25,
   35,
   40
  ],
  "kill_fires": false
 },
 "fixed, m = 1n": {
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
| bernoulli   |       1 |  10 |      6        |              0.36  |                2.29 | left open   |               0.477 |                 3    | left open; right open |                 1.4  |            3.5      |
| bernoulli   |       1 |  15 |     16        |              0.417 |                2.61 | left open   |               0.675 |                 4.73 | left open; right open |                 1.89 |            8.5      |
| bernoulli   |       1 |  20 |     40.5      |              0.36  |                2.29 |             |               0.656 |                 4.53 | left open             |                 3.46 |           20.8      |
| bernoulli   |       1 |  25 |    112        |              0.328 |                2.13 |             |               0.639 |                 4.35 | left open             |                 7.06 |          113        |
| bernoulli   |       1 |  30 |    339        |              0.247 |                1.76 |             |               0.577 |                 3.77 |                       |                17    |          340        |
| bernoulli   |       1 |  35 |    796        |              0.255 |                1.8  |             |               0.532 |                 3.41 |                       |                28.5  |          797        |
| bernoulli   |       1 |  40 |      2.22e+03 |              0.243 |                1.75 |             |               0.481 |                 3.03 |                       |                44.9  |            2.22e+03 |
| bernoulli   |       2 |  10 |      6        |              0.3   |                2    | left open   |               0.615 |                 4.13 | left open; right open |                 1.17 |            7        |
| bernoulli   |       2 |  15 |     17        |              0.365 |                2.32 | left open   |               0.577 |                 3.78 | left open             |                 1.8  |           18        |
| bernoulli   |       2 |  20 |     52.5      |              0.3   |                2    |             |               0.569 |                 3.71 | left open             |                 3.82 |           53.5      |
| bernoulli   |       2 |  25 |    147        |              0.263 |                1.83 |             |               0.549 |                 3.54 | left open             |                 7.42 |          148        |
| bernoulli   |       2 |  30 |    394        |              0.256 |                1.8  |             |               0.512 |                 3.25 |                       |                12.8  |          395        |
| bernoulli   |       2 |  35 |      1.34e+03 |              0.204 |                1.6  |             |               0.432 |                 2.7  |                       |                18.4  |            1.34e+03 |
| bernoulli   |       2 |  40 |      4.27e+03 |              0.135 |                1.36 |             |               0.38  |                 2.4  |                       |                25.6  |            4.27e+03 |
| fixed       |       1 |  10 |      5        |              0.28  |                1.9  | left open   |               0.678 |                 4.76 | left open; right open |                 1    |            6        |
| fixed       |       1 |  15 |     16.5      |              0.292 |                1.96 | left open   |               0.584 |                 3.84 | left open             |                 1.35 |           17.5      |
| fixed       |       1 |  20 |     53        |              0.298 |                1.99 | left open   |               0.498 |                 3.15 | left open             |                 1.54 |           27        |
| fixed       |       1 |  25 |    155        |              0.249 |                1.77 |             |               0.474 |                 2.98 | left open             |                 2.67 |           78        |
| fixed       |       1 |  30 |    460        |              0.221 |                1.66 |             |               0.458 |                 2.87 | left open             |                 4.19 |          115        |
| fixed       |       1 |  35 |      1.4e+03  |              0.196 |                1.57 |             |               0.436 |                 2.73 | left open             |                 5.71 |          175        |
| fixed       |       1 |  40 |      3.95e+03 |              0.19  |                1.55 |             |               0.433 |                 2.71 | left open             |                 8.34 |          282        |
| fixed       |       2 |  10 |      5        |              0.176 |                1.5  | left open   |               0.699 |                 5    | left open; right open |                 1    |            6        |
| fixed       |       2 |  15 |     23        |              0.176 |                1.5  | left open   |               0.372 |                 2.36 | left open             |                 1    |           24        |
| fixed       |       2 |  20 |     82.5      |              0.166 |                1.47 | left open   |               0.348 |                 2.23 | left open             |                 1    |           83.5      |
| fixed       |       2 |  25 |    262        |              0.158 |                1.44 | left open   |               0.329 |                 2.13 | left open             |                 1    |          263        |
| fixed       |       2 |  30 |    941        |              0.132 |                1.36 | left open   |               0.302 |                 2.01 | left open             |                 1    |          628        |
| fixed       |       2 |  35 |      3.08e+03 |              0.135 |                1.37 | left open   |               0.28  |                 1.91 | left open             |                 1    |            1.54e+03 |
| fixed       |       2 |  40 |      9.97e+03 |              0.126 |                1.34 | left open   |               0.269 |                 1.86 | left open             |                 1    |            4.98e+03 |

### Scaling of the median with n (n >= 15, cells with median >= 2)

| generator   |   ratio | where                       |   param |   points |      rate |   doubling_n |   rms_exp |   alpha |   rms_pow | better      |
|:------------|--------:|:----------------------------|--------:|---------:|----------:|-------------:|----------:|--------:|----------:|:------------|
| bernoulli   |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0861  |         3.49 |    0.021  |   5.03  |   0.105   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.025 |        6 |   0.0296  |        10.2  |    0.0381 |   1.71  |   0.067   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.05  |        6 |   0.0854  |         3.53 |    0.118  |   4.87  |   0.22    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.075 |        6 |   0.0977  |         3.08 |    0.029  |   5.69  |   0.133   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.1   |        6 |   0.0824  |         3.65 |    0.0828 |   4.88  |   0.0395  | power       |
| bernoulli   |       1 | fixed parameter             |   0.15  |        6 |   0.0428  |         7.03 |    0.0954 |   2.59  |   0.0447  | power       |
| bernoulli   |       1 | fixed parameter             |   0.2   |        6 |   0.0172  |        17.5  |    0.0839 |   1.08  |   0.0638  | power       |
| bernoulli   |       1 | fixed parameter             |   0.3   |        6 |  -0.00855 |       inf    |    0.0346 |  -0.472 |   0.043   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.4   |        1 | nan       |       nan    |  nan      | nan     | nan       |             |
| bernoulli   |       1 | fixed parameter             |   0.5   |        0 | nan       |       nan    |  nan      | nan     | nan       |             |
| bernoulli   |       2 | ridge (peak cell at each n) | nan     |        6 |   0.0951  |         3.16 |    0.0268 |   5.54  |   0.132   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.025 |        6 |   0.05    |         6.02 |    0.0866 |   2.84  |   0.144   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.05  |        6 |   0.11    |         2.74 |    0.0646 |   6.37  |   0.186   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.075 |        6 |   0.0827  |         3.64 |    0.116  |   4.94  |   0.0256  | power       |
| bernoulli   |       2 | fixed parameter             |   0.1   |        6 |   0.0481  |         6.26 |    0.121  |   2.92  |   0.0634  | power       |
| bernoulli   |       2 | fixed parameter             |   0.15  |        6 |   0.0112  |        26.9  |    0.0601 |   0.711 |   0.0464  | power       |
| bernoulli   |       2 | fixed parameter             |   0.2   |        6 |  -0.00515 |       inf    |    0.0404 |  -0.268 |   0.0454  | exponential |
| bernoulli   |       2 | fixed parameter             |   0.3   |        0 | nan       |       nan    |  nan      | nan     | nan       |             |
| bernoulli   |       2 | fixed parameter             |   0.4   |        0 | nan       |       nan    |  nan      | nan     | nan       |             |
| bernoulli   |       2 | fixed parameter             |   0.5   |        0 | nan       |       nan    |  nan      | nan     | nan       |             |
| fixed       |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0951  |         3.17 |    0.0119 |   5.56  |   0.106   | exponential |
| fixed       |       1 | fixed parameter             |   2     |        6 |   0.0619  |         4.87 |    0.044  |   3.63  |   0.0676  | exponential |
| fixed       |       1 | fixed parameter             |   3     |        6 |   0.0951  |         3.17 |    0.0119 |   5.56  |   0.106   | exponential |
| fixed       |       1 | fixed parameter             |   4     |        6 |   0.0973  |         3.09 |    0.0157 |   5.69  |   0.105   | exponential |
| fixed       |       1 | fixed parameter             |   5     |        6 |   0.0934  |         3.22 |    0.0389 |   5.49  |   0.0749  | exponential |
| fixed       |       1 | fixed parameter             |   6     |        6 |   0.0854  |         3.52 |    0.0538 |   5.03  |   0.0719  | exponential |
| fixed       |       1 | fixed parameter             |   7     |        5 |   0.0779  |         3.86 |    0.0459 |   5.19  |   0.0139  | power       |
| fixed       |       1 | fixed parameter             |   8     |        5 |   0.0702  |         4.29 |    0.0289 |   4.67  |   0.0231  | power       |
| fixed       |       1 | fixed parameter             |   9     |        4 |   0.0718  |         4.19 |    0.0451 |   5.3   |   0.0229  | power       |
| fixed       |       1 | fixed parameter             |  10     |        3 |   0.0637  |         4.73 |    0.0234 |   5.11  |   0.0126  | power       |
| fixed       |       2 | ridge (peak cell at each n) | nan     |        6 |   0.105   |         2.85 |    0.0126 |   6.16  |   0.121   | exponential |
| fixed       |       2 | fixed parameter             |   2     |        6 |   0.105   |         2.85 |    0.0126 |   6.16  |   0.121   | exponential |
| fixed       |       2 | fixed parameter             |   3     |        6 |   0.101   |         2.98 |    0.0153 |   5.91  |   0.113   | exponential |
| fixed       |       2 | fixed parameter             |   4     |        6 |   0.0905  |         3.33 |    0.0592 |   5.34  |   0.0606  | exponential |
| fixed       |       2 | fixed parameter             |   5     |        5 |   0.0751  |         4.01 |    0.034  |   4.99  |   0.0374  | exponential |
| fixed       |       2 | fixed parameter             |   6     |        4 |   0.0677  |         4.45 |    0.025  |   4.98  |   0.00479 | power       |
| fixed       |       2 | fixed parameter             |   7     |        3 |   0.0628  |         4.79 |    0.0179 |   5.04  |   0.00729 | power       |
| fixed       |       2 | fixed parameter             |   8     |        2 | nan       |       nan    |  nan      | nan     | nan       |             |
| fixed       |       2 | fixed parameter             |   9     |        2 | nan       |       nan    |  nan      | nan     | nan       |             |
| fixed       |       2 | fixed parameter             |  10     |        0 | nan       |       nan    |  nan      | nan     | nan       |             |

### Scaling of the p90 with n

| generator   |   ratio | where                       |   param |   points |      rate |   doubling_n |   rms_exp |   alpha |    rms_pow | better      |
|:------------|--------:|:----------------------------|--------:|---------:|----------:|-------------:|----------:|--------:|-----------:|:------------|
| bernoulli   |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0888  |         3.39 |   0.0346  |   5.21  |   0.0828   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.025 |        6 |   0.0486  |         6.19 |   0.0772  |   2.77  |   0.132    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.05  |        6 |   0.0968  |         3.11 |   0.0574  |   5.59  |   0.172    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.075 |        6 |   0.0992  |         3.03 |   0.064   |   5.83  |   0.0931   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.1   |        6 |   0.0807  |         3.73 |   0.0907  |   4.8   |   0.0205   | power       |
| bernoulli   |       1 | fixed parameter             |   0.15  |        6 |   0.0418  |         7.2  |   0.101   |   2.54  |   0.0498   | power       |
| bernoulli   |       1 | fixed parameter             |   0.2   |        6 |   0.0145  |        20.7  |   0.0948  |   0.941 |   0.0764   | power       |
| bernoulli   |       1 | fixed parameter             |   0.3   |        6 |  -0.0124  |       inf    |   0.0306  |  -0.703 |   0.0431   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.4   |        5 |  -0.0106  |       inf    |   0.0385  |  -0.551 |   0.044    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.5   |        1 | nan       |       nan    | nan       | nan     | nan        |             |
| bernoulli   |       2 | ridge (peak cell at each n) | nan     |        6 |   0.0979  |         3.08 |   0.0292  |   5.69  |   0.138    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.025 |        6 |   0.0684  |         4.4  |   0.0927  |   3.91  |   0.167    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.05  |        6 |   0.112   |         2.7  |   0.0177  |   6.52  |   0.138    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.075 |        6 |   0.0831  |         3.62 |   0.112   |   4.95  |   0.0423   | power       |
| bernoulli   |       2 | fixed parameter             |   0.1   |        6 |   0.0468  |         6.44 |   0.124   |   2.85  |   0.0689   | power       |
| bernoulli   |       2 | fixed parameter             |   0.15  |        6 |   0.00747 |        40.3  |   0.0534  |   0.487 |   0.0441   | power       |
| bernoulli   |       2 | fixed parameter             |   0.2   |        6 |  -0.00623 |       inf    |   0.0236  |  -0.357 |   0.0268   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.3   |        3 |  -0.0176  |       inf    |   0.0415  |  -0.756 |   0.0466   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.4   |        0 | nan       |       nan    | nan       | nan     | nan        |             |
| bernoulli   |       2 | fixed parameter             |   0.5   |        0 | nan       |       nan    | nan       | nan     | nan        |             |
| fixed       |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0989  |         3.04 |   0.0176  |   5.78  |   0.115    | exponential |
| fixed       |       1 | fixed parameter             |   2     |        6 |   0.0642  |         4.69 |   0.0466  |   3.77  |   0.0605   | exponential |
| fixed       |       1 | fixed parameter             |   3     |        6 |   0.0995  |         3.03 |   0.0209  |   5.82  |   0.111    | exponential |
| fixed       |       1 | fixed parameter             |   4     |        6 |   0.1     |         3    |   0.017   |   5.86  |   0.117    | exponential |
| fixed       |       1 | fixed parameter             |   5     |        6 |   0.0909  |         3.31 |   0.0314  |   5.33  |   0.0806   | exponential |
| fixed       |       1 | fixed parameter             |   6     |        6 |   0.0819  |         3.68 |   0.0124  |   4.79  |   0.0883   | exponential |
| fixed       |       1 | fixed parameter             |   7     |        6 |   0.0762  |         3.95 |   0.0351  |   4.48  |   0.0627   | exponential |
| fixed       |       1 | fixed parameter             |   8     |        5 |   0.0673  |         4.47 |   0.0347  |   4.48  |   0.0235   | power       |
| fixed       |       1 | fixed parameter             |   9     |        5 |   0.0647  |         4.65 |   0.026   |   4.29  |   0.0455   | exponential |
| fixed       |       1 | fixed parameter             |  10     |        4 |   0.0641  |         4.7  |   0.0467  |   4.74  |   0.0232   | power       |
| fixed       |       2 | ridge (peak cell at each n) | nan     |        6 |   0.108   |         2.78 |   0.0388  |   6.37  |   0.0955   | exponential |
| fixed       |       2 | fixed parameter             |   2     |        6 |   0.108   |         2.78 |   0.0388  |   6.37  |   0.0955   | exponential |
| fixed       |       2 | fixed parameter             |   3     |        6 |   0.104   |         2.91 |   0.0196  |   6.06  |   0.113    | exponential |
| fixed       |       2 | fixed parameter             |   4     |        6 |   0.0875  |         3.44 |   0.0261  |   5.12  |   0.089    | exponential |
| fixed       |       2 | fixed parameter             |   5     |        6 |   0.0783  |         3.84 |   0.0534  |   4.62  |   0.0551   | exponential |
| fixed       |       2 | fixed parameter             |   6     |        5 |   0.065   |         4.63 |   0.019   |   4.32  |   0.0286   | exponential |
| fixed       |       2 | fixed parameter             |   7     |        5 |   0.0552  |         5.45 |   0.0363  |   3.64  |   0.0603   | exponential |
| fixed       |       2 | fixed parameter             |   8     |        3 |   0.0564  |         5.33 |   0.00891 |   4.52  |   0.000625 | power       |
| fixed       |       2 | fixed parameter             |   9     |        3 |   0.0301  |        10    |   0.0121  |   2.42  |   0.00697  | power       |
| fixed       |       2 | fixed parameter             |  10     |        1 | nan       |       nan    | nan       | nan     | nan        |             |

### Order parameters: collapse at fixed n (n >= 20) and constancy of the peak location

| candidate    | meaning                          |   dispersion_mean |   r2_mean |   r2_ceiling_mean |   peak_value_mean |   peak_value_cv |   peak_value_min |   peak_value_max |   series_with_interior_peak |
|:-------------|:---------------------------------|------------------:|----------:|------------------:|------------------:|----------------:|-----------------:|-----------------:|----------------------------:|
| g_deg_mean   | mean degree of the MOSP graph    |             0.278 |   0.882   |             0.906 |            6.21   |           0.19  |           4      |            8.28  |                          15 |
| opt_frac     | optimum / n                      |             0.356 |   0.85    |             0.906 |            0.33   |           0.137 |           0.28   |            0.433 |                          15 |
| bound_gap    | ub_best - lb_best                |             0.37  |   0.312   |             0.906 |            2.27   |           0.513 |           1      |            4     |                          15 |
| g_components | components of the MOSP graph     |             0.519 |   0.00679 |             0.906 |            1.33   |           0.366 |           1      |            2     |                          15 |
| col_mean     | customers per product (realised) |             0.644 |   0.729   |             0.906 |            2.64   |           0.173 |           1.91   |            3.1   |                          15 |
| density      | matrix density                   |             0.644 |   0.729   |             0.906 |            0.0924 |           0.279 |           0.0531 |            0.152 |                          15 |

### Candidate values at the peak cell

| generator   |   ratio |   n |   peak_param | interior   |   col_mean |   density |   g_deg_mean |   opt_frac |   bound_gap |   g_components |
|:------------|--------:|----:|-------------:|:-----------|-----------:|----------:|-------------:|-----------:|------------:|---------------:|
| bernoulli   |       1 |  20 |        0.1   | True       |       2.25 |    0.113  |         4    |      0.3   |           1 |              2 |
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
| opt_frac     |       5 | 20: 0.4, 25: 0.32, 30: 0.267, 35: 0.286, 40: 0.3      | True                  | 0.314  | 0.164 |
| col_mean     |       5 | 20: 2, 25: 3, 30: 2, 35: 3, 40: 2.92                  | True                  | 2.58   | 0.207 |
| g_deg_mean   |       5 | 20: 4.1, 25: 3.76, 30: 4.8, 35: 5.71, 40: 6.47        | True                  | 4.97   | 0.227 |
| density      |       5 | 20: 0.1, 25: 0.12, 30: 0.0667, 35: 0.0857, 40: 0.0731 | True                  | 0.0891 | 0.241 |
| bound_gap    |       5 | 20: 3, 25: 3, 30: 3, 35: 4, 40: 5                     | False                 | 3.6    | 0.248 |
| g_components |       4 | 20: 3, 25: 6, 30: 4, 35: 3                            | True                  | 4      | 0.354 |

### Monotonicity along density per series and n

| generator   |   ratio |   n | monotone   | rises_then_falls   |
|:------------|--------:|----:|:-----------|:-------------------|
| bernoulli   |       1 |  10 | False      | True               |
| bernoulli   |       1 |  15 | False      | True               |
| bernoulli   |       1 |  20 | False      | True               |
| bernoulli   |       1 |  25 | False      | True               |
| bernoulli   |       1 |  30 | False      | True               |
| bernoulli   |       1 |  35 | False      | True               |
| bernoulli   |       1 |  40 | False      | True               |
| bernoulli   |       2 |  10 | False      | True               |
| bernoulli   |       2 |  15 | False      | True               |
| bernoulli   |       2 |  20 | False      | True               |
| bernoulli   |       2 |  25 | False      | True               |
| bernoulli   |       2 |  30 | False      | True               |
| bernoulli   |       2 |  35 | False      | True               |
| bernoulli   |       2 |  40 | False      | True               |
| fixed       |       1 |  10 | False      | False              |
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
| col_mean    |  10 |     10 |        0.168 | 0.327 |
| col_mean    |  15 |     10 |        0.35  | 0.561 |
| col_mean    |  20 |     10 |        0.362 | 0.688 |
| col_mean    |  25 |     10 |        0.515 | 0.725 |
| col_mean    |  30 |     10 |        0.599 | 0.748 |
| col_mean    |  35 |     10 |        0.729 | 0.754 |
| col_mean    |  40 |     10 |        1.01  | 0.731 |

### Collapse by n: density

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| density     |  10 |     10 |        0.168 | 0.327 |
| density     |  15 |     10 |        0.35  | 0.561 |
| density     |  20 |     10 |        0.362 | 0.688 |
| density     |  25 |     10 |        0.515 | 0.725 |
| density     |  30 |     10 |        0.599 | 0.748 |
| density     |  35 |     10 |        0.729 | 0.754 |
| density     |  40 |     10 |        1.01  | 0.731 |

### Collapse by n: g_deg_mean

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| g_deg_mean  |  10 |     10 |       0.0773 | 0.425 |
| g_deg_mean  |  15 |     10 |       0.0714 | 0.722 |
| g_deg_mean  |  20 |     10 |       0.132  | 0.828 |
| g_deg_mean  |  25 |     10 |       0.228  | 0.877 |
| g_deg_mean  |  30 |     10 |       0.281  | 0.889 |
| g_deg_mean  |  35 |     10 |       0.354  | 0.899 |
| g_deg_mean  |  40 |     10 |       0.395  | 0.918 |

### Collapse by n: opt_frac

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| opt_frac    |  10 |      7 |        0.208 | 0.344 |
| opt_frac    |  15 |     10 |        0.19  | 0.658 |
| opt_frac    |  20 |     10 |        0.268 | 0.765 |
| opt_frac    |  25 |     10 |        0.236 | 0.839 |
| opt_frac    |  30 |     10 |        0.408 | 0.868 |
| opt_frac    |  35 |     10 |        0.382 | 0.878 |
| opt_frac    |  40 |     10 |        0.487 | 0.902 |

### Collapse by n: bound_gap

| candidate   |   n |   bins |   dispersion |        r2 |
|:------------|----:|-------:|-------------:|----------:|
| bound_gap   |  10 |      2 |       0.0969 | -0.000489 |
| bound_gap   |  15 |      2 |       0.195  |  0.00567  |
| bound_gap   |  20 |      2 |       0.245  |  0.0714   |
| bound_gap   |  25 |      3 |       0.323  |  0.178    |
| bound_gap   |  30 |      3 |       0.365  |  0.319    |
| bound_gap   |  35 |      4 |       0.431  |  0.443    |
| bound_gap   |  40 |      5 |       0.487  |  0.546    |

### Collapse by n: g_components

| candidate    |   n |   bins |   dispersion |        r2 |
|:-------------|----:|-------:|-------------:|----------:|
| g_components |  10 |      4 |       0.0113 |  0.048    |
| g_components |  15 |      4 |       0.133  |  0.0336   |
| g_components |  20 |      3 |       0.237  |  0.00773  |
| g_components |  25 |      3 |       0.338  |  0.0285   |
| g_components |  30 |      2 |       0.608  | -0.00175  |
| g_components |  35 |      2 |       0.657  | -0.000472 |
| g_components |  40 |      2 |       0.756  | -0.000117 |

### Median nodes, connected instances only

**fixed, m = 1n**

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   13 |   38 |   64 |  121 |  328 |  605 |
|   3 |          3 |    5 |   16 |   53 |  155 |  455 | 1402 | 3953 |
|   4 |          4 |    2 |    9 |   30 |   89 |  288 |  830 | 2477 |
|   5 |          5 |    1 |    4 |   14 |   43 |  126 |  338 |  890 |
|   6 |          6 |    0 |    2 |    8 |   18 |   50 |  120 |  314 |
|   7 |          7 |    0 |    1 |    3 |   10 |   23 |   53 |  112 |
|   8 |          8 |    0 |    1 |    2 |    5 |   12 |   25 |   51 |
|   9 |          9 |    0 |    0 |    1 |    2 |    6 |   12 |   25 |
|  10 |         10 |    0 |    0 |    1 |    1 |    3 |    7 |   13 |

**fixed, m = 2n**

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   23 |   82 |  267 |  949 | 3106 | 9992 |
|   3 |          3 |    2 |   11 |   39 |  120 |  374 | 1249 | 3774 |
|   4 |          4 |    1 |    3 |   12 |   34 |   94 |  232 |  625 |
|   5 |          5 |    0 |    1 |    4 |   12 |   26 |   58 |  138 |
|   6 |          6 |    0 |    0 |    1 |    4 |   10 |   21 |   42 |
|   7 |          7 |    0 |    0 |    1 |    1 |    4 |    9 |   17 |
|   8 |          8 |    0 |    0 |    0 |    1 |    1 |    4 |    7 |
|   9 |          9 |    0 |    0 |    0 |    0 |    1 |    2 |    3 |
|  10 |         10 |    0 |    0 |    0 |    0 |    0 |    1 |    1 |

**bernoulli, m = 1n**

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |  nan |  nan |  nan |  nan |  166 |  368 | 1999 |
|   0 |          2 |  nan |   40 |   35 |  117 |  340 | 1050 | 2448 |
|   0 |          3 |    2 |   17 |   51 |  121 |  366 |  732 | 1326 |
|   0 |          4 |    6 |   18 |   39 |   80 |  110 |  164 |  198 |
|   0 |          5 |    6 |   13 |   21 |   32 |   38 |   34 |   37 |
|   0 |          8 |    4 |    5 |    5 |    5 |    4 |    4 |    3 |
|   0 |         10 |    1 |    2 |    1 |    1 |    1 |    1 |    0 |
|   0 |         12 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |

**bernoulli, m = 2n**

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |  nan |  nan |   74 |  222 |  491 | 1872 | 4578 |
|   0 |          2 |    5 |   29 |   68 |  170 |  406 |  876 | 1384 |
|   0 |          3 |    5 |   18 |   56 |  112 |  173 |  224 |  316 |
|   0 |          4 |    6 |   14 |   21 |   25 |   30 |   28 |   28 |
|   0 |          5 |    3 |    6 |    7 |    7 |    6 |    5 |    5 |
|   0 |          7 |    1 |    1 |    1 |    1 |    1 |    0 |    0 |
|   0 |         10 |    1 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### Chu & Stuckey's classes against the campaign's nearest fixed m = n cell

| class           |   instances |   corpus_median_nodes |   corpus_max_nodes |   corpus_col_mean |   corpus_opt_frac |   nearest_cell_d |   cell_col_mean |   cell_median_all |   cell_median_connected |   cell_connected_share |   mean_percentile_in_connected_cell | cell_is_peak   |
|:----------------|------------:|----------------------:|-------------------:|------------------:|------------------:|-----------------:|----------------:|------------------:|------------------------:|-----------------------:|------------------------------------:|:---------------|
| Random-30-30-2  |           5 |            691        |           1.15e+03 |              2.7  |             0.3   |                3 |            3.03 |        460        |              455        |                  0.993 |                               0.706 | True           |
| Random-30-30-4  |           5 |            168        |         271        |              4.2  |             0.533 |                4 |            4    |        288        |              288        |                  1     |                               0.159 | False          |
| Random-30-30-6  |           5 |             45        |          66        |              5.97 |             0.7   |                6 |            6    |         50        |               50        |                  1     |                               0.445 | False          |
| Random-30-30-8  |           5 |             12        |          15        |              7.83 |             0.833 |                8 |            8    |         12        |               12        |                  1     |                               0.401 | False          |
| Random-30-30-10 |           5 |              3        |           5        |              9.93 |             0.9   |               10 |           10    |          3        |                3        |                  1     |                               0.427 | False          |
| Random-40-40-2  |           5 |              4.36e+03 |           2.91e+04 |              2.8  |             0.275 |                3 |            3.05 |          3.95e+03 |                3.95e+03 |                  1     |                               0.464 | True           |
| Random-40-40-4  |           5 |              1.19e+03 |           1.48e+03 |              4.25 |             0.525 |                4 |            4    |          2.48e+03 |                2.48e+03 |                  1     |                               0.048 | False          |
| Random-40-40-6  |           5 |            276        |         415        |              5.92 |             0.7   |                6 |            6    |        314        |              314        |                  1     |                               0.364 | False          |
| Random-40-40-8  |           5 |             38        |          57        |              7.97 |             0.825 |                8 |            8    |         51        |               51        |                  1     |                               0.235 | False          |
| Random-40-40-10 |           5 |             15        |          24        |              9.9  |             0.9   |               10 |           10    |         13        |               13        |                  1     |                               0.527 | False          |

### Chu & Stuckey's instances

| instance_name       |   n |   d |   optimum |   col_mean |   g_deg_mean |   g_components |   bound_gap |   nodes |
|:--------------------|----:|----:|----------:|-----------:|-------------:|---------------:|------------:|--------:|
| Random-30-30-2-1_0  |  30 |   2 |         9 |       2.8  |         5.33 |              1 |           1 |     670 |
| Random-30-30-2-2_0  |  30 |   2 |         8 |       2.7  |         5.53 |              1 |           1 |     221 |
| Random-30-30-2-3_0  |  30 |   2 |         9 |       2.73 |         5.47 |              1 |           2 |    1149 |
| Random-30-30-2-4_0  |  30 |   2 |         9 |       2.7  |         5.2  |              1 |           2 |     845 |
| Random-30-30-2-5_0  |  30 |   2 |         8 |       2.63 |         4.67 |              1 |           3 |     691 |
| Random-30-30-4-1_0  |  30 |   4 |        17 |       4.73 |        14.2  |              1 |           1 |     145 |
| Random-30-30-4-2_0  |  30 |   4 |        15 |       4.2  |        11.8  |              1 |           4 |     217 |
| Random-30-30-4-3_0  |  30 |   4 |        16 |       4.37 |        13    |              1 |           2 |     128 |
| Random-30-30-4-4_0  |  30 |   4 |        15 |       3.83 |        11.5  |              1 |           3 |     271 |
| Random-30-30-4-5_0  |  30 |   4 |        17 |       4.13 |        12.7  |              1 |           1 |     168 |
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
| Random-40-40-2-1_0  |  40 |   2 |        11 |       2.8  |         6.05 |              1 |           4 |    4800 |
| Random-40-40-2-2_0  |  40 |   2 |        14 |       2.92 |         6.85 |              1 |           6 |   29138 |
| Random-40-40-2-3_0  |  40 |   2 |        10 |       2.7  |         5.25 |              1 |           4 |    1229 |
| Random-40-40-2-4_0  |  40 |   2 |         7 |       2.48 |         4.05 |              1 |           4 |     987 |
| Random-40-40-2-5_0  |  40 |   2 |        13 |       3    |         8.25 |              1 |           5 |    4364 |
| Random-40-40-4-1_0  |  40 |   4 |        21 |       4.25 |        13.6  |              1 |           4 |    1193 |
| Random-40-40-4-2_0  |  40 |   4 |        21 |       4.28 |        14.2  |              1 |           2 |    1308 |
| Random-40-40-4-3_0  |  40 |   4 |        19 |       4.12 |        12.8  |              1 |           4 |    1485 |
| Random-40-40-4-4_0  |  40 |   4 |        18 |       4.1  |        12.8  |              1 |           3 |     586 |
| Random-40-40-4-5_0  |  40 |   4 |        22 |       4.35 |        15.3  |              1 |           3 |     706 |
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

