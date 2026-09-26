# Hardness map tables (config `default`, raw instances)

37800 rows in 252 cells; 30699 connected. Regenerate: `python -m learning.hardness_map --config default`.

### median nodes: fixed, m = 1n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   12 |   34 |   58 |  109 |  244 |  473 |
|   3 |          3 |    5 |   16 |   53 |  155 |  460 | 1402 | 3953 |
|   4 |          4 |    2 |    9 |   30 |   89 |  288 |  830 | 2477 |
|   5 |          5 |    1 |    4 |   14 |   43 |  126 |  338 |  890 |
|   6 |          6 |    0 |    2 |    8 |   18 |   50 |  120 |  314 |
|   7 |          7 |    0 |    1 |    3 |   10 |   23 |   53 |  112 |
|   8 |          8 |    0 |    0 |    1 |    5 |   12 |   25 |   51 |
|   9 |          9 |    0 |    0 |    0 |    2 |    6 |   12 |   25 |
|  10 |         10 |    0 |    0 |    0 |    1 |    3 |    7 |   13 |

### median nodes: fixed, m = 2n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   23 |   82 |  262 |  940 | 3080 | 9968 |
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
|   0 |          1 |    5 |    8 |   11 |   14 |   19 |   27 |   48 |
|   0 |          2 |    5 |    8 |   12 |   26 |   82 |  269 |  960 |
|   0 |          2 |    5 |    9 |   23 |   74 |  250 |  796 | 2222 |
|   0 |          3 |    5 |   12 |   40 |  112 |  340 |  718 | 1313 |
|   0 |          4 |    5 |   16 |   38 |   80 |  110 |  164 |  199 |
|   0 |          5 |    6 |   13 |   20 |   32 |   38 |   34 |   37 |
|   0 |          8 |    4 |    5 |    5 |    5 |    4 |    4 |    3 |
|   0 |         10 |    1 |    1 |    1 |    1 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### median nodes: bernoulli, m = 2n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    6 |    9 |   13 |   19 |   30 |   72 |  166 |
|   0 |          2 |    6 |    9 |   26 |   71 |  325 | 1339 | 4270 |
|   0 |          2 |    5 |   12 |   52 |  148 |  394 |  876 | 1411 |
|   0 |          3 |    5 |   17 |   52 |  114 |  172 |  224 |  316 |
|   0 |          4 |    6 |   14 |   21 |   25 |   30 |   28 |   28 |
|   0 |          5 |    4 |    6 |    7 |    7 |    6 |    5 |    5 |
|   0 |          8 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |
|   0 |         10 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### p90 nodes: fixed, m = 1n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |   12 |   27 |   70 |  125 |  302 |  657 | 1052 |
|   3 |          3 |    8 |   26 |   93 |  261 |  874 | 2777 | 8071 |
|   4 |          4 |    4 |   14 |   50 |  152 |  464 | 1441 | 4859 |
|   5 |          5 |    2 |    7 |   22 |   66 |  195 |  507 | 1305 |
|   6 |          6 |    1 |    4 |   11 |   28 |   71 |  185 |  447 |
|   7 |          7 |    0 |    2 |    6 |   14 |   34 |   73 |  174 |
|   8 |          8 |    0 |    1 |    3 |    8 |   16 |   36 |   68 |
|   9 |          9 |    0 |    0 |    1 |    4 |   10 |   18 |   39 |
|  10 |         10 |    0 |    0 |    1 |    2 |    5 |   11 |   18 |

### p90 nodes: fixed, m = 2n

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |    40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|------:|
|   2 |          2 |   11 |   40 |  174 |  607 | 2131 | 6580 | 22004 |
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
|   0 |          1 |    6 |   10 |   14 |   22 |   33 |   79 |  168 |
|   0 |          2 |    6 |   11 |   27 |   81 |  258 |  908 | 2946 |
|   0 |          2 |    7 |   18 |   54 |  196 |  744 | 2042 | 4635 |
|   0 |          3 |    7 |   24 |   91 |  245 |  672 | 1402 | 2564 |
|   0 |          4 |   10 |   29 |   78 |  139 |  208 |  301 |  346 |
|   0 |          5 |   11 |   24 |   43 |   59 |   69 |   63 |   60 |
|   0 |          8 |    7 |   10 |   10 |    8 |    8 |    6 |    5 |
|   0 |         10 |    3 |    3 |    3 |    2 |    1 |    1 |    0 |
|   0 |         12 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |

### p90 nodes: bernoulli, m = 2n

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          1 |    8 |   12 |   17 |   44 |   78 |  183 |  677 |
|   0 |          2 |    7 |   17 |   59 |  207 |  812 | 3037 | 9915 |
|   0 |          2 |    8 |   28 |   94 |  330 |  856 | 1974 | 3016 |
|   0 |          3 |    9 |   35 |   99 |  218 |  310 |  519 |  526 |
|   0 |          4 |   10 |   29 |   38 |   46 |   50 |   50 |   44 |
|   0 |          5 |    7 |   13 |   13 |   12 |   10 |   11 |    9 |
|   0 |          8 |    3 |    3 |    2 |    1 |    1 |    1 |    0 |
|   0 |         10 |    1 |    0 |    0 |    0 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

### Peaks of the median, with bootstrap intervals on the ratio to each neighbour

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_median |   tied | interior   |   ratio_left | ci_left        | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|--------------:|-------:|:-----------|-------------:|:---------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.2   |            2.2  |      6        |      1 | True       |         1.17 | [0.92, 1.20]   | False              |          1.4  | [1.20, 1.75] | True                |
| bernoulli   |       1 |  15 |        0.15  |            2.4  |     16        |      1 | True       |         1.36 | [1.11, 1.55]   | True               |          1.21 | [1.00, 1.32] | False               |
| bernoulli   |       1 |  20 |        0.1   |            2.25 |     40.5      |      1 | True       |         1.73 | [1.41, 1.96]   | True               |          1.05 | [0.87, 1.19] | False               |
| bernoulli   |       1 |  25 |        0.1   |            2.56 |    112        |      1 | True       |         1.5  | [1.34, 1.81]   | True               |          1.39 | [1.24, 1.59] | True                |
| bernoulli   |       1 |  30 |        0.1   |            3.07 |    340        |      1 | True       |         1.36 | [1.12, 1.70]   | True               |          3.07 | [2.56, 3.50] | True                |
| bernoulli   |       1 |  35 |        0.075 |            2.77 |    796        |      1 | True       |         2.95 | [2.45, 3.79]   | True               |          1.11 | [0.96, 1.36] | False               |
| bernoulli   |       1 |  40 |        0.075 |            3.1  |      2.22e+03 |      1 | True       |         2.31 | [1.95, 2.92]   | True               |          1.69 | [1.48, 2.02] | True                |
| bernoulli   |       2 |  10 |        0.025 |            1.1  |      6        |      2 | False      |       nan    | edge           | False              |          1    | [1.00, 1.17] | False               |
| bernoulli   |       2 |  15 |        0.1   |            1.73 |     17        |      1 | True       |         1.38 | [1.21, 1.67]   | True               |          1.2  | [1.03, 1.46] | True                |
| bernoulli   |       2 |  20 |        0.1   |            2.12 |     52.5      |      1 | True       |         1.02 | [0.93, 1.27]   | False              |          2.43 | [2.22, 2.90] | True                |
| bernoulli   |       2 |  25 |        0.075 |            2.04 |    148        |      1 | True       |         2.06 | [1.68, 2.45]   | True               |          1.3  | [1.13, 1.55] | True                |
| bernoulli   |       2 |  30 |        0.075 |            2.35 |    394        |      1 | True       |         1.21 | [0.98, 1.56]   | False              |          2.29 | [2.05, 2.66] | True                |
| bernoulli   |       2 |  35 |        0.05  |            1.91 |      1.34e+03 |      1 | True       |        18.4  | [15.33, 25.26] | True               |          1.53 | [1.27, 1.90] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.12 |      4.27e+03 |      1 | True       |        25.6  | [19.50, 32.71] | True               |          3.02 | [2.50, 3.59] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |      5        |      2 | False      |       nan    | edge           | False              |          1    | [0.83, 1.20] | False               |
| fixed       |       1 |  15 |        3     |            3    |     16.5      |      1 | True       |         1.35 | [1.13, 1.73]   | True               |          1.75 | [1.55, 1.90] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |     53        |      1 | True       |         1.54 | [1.36, 1.93]   | True               |          1.74 | [1.59, 1.93] | True                |
| fixed       |       1 |  25 |        3     |            3.04 |    155        |      1 | True       |         2.67 | [2.25, 3.00]   | True               |          1.73 | [1.50, 1.92] | True                |
| fixed       |       1 |  30 |        3     |            3.03 |    460        |      1 | True       |         4.19 | [3.44, 4.80]   | True               |          1.59 | [1.40, 1.76] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |      1.4e+03  |      1 | True       |         5.71 | [4.34, 7.04]   | True               |          1.69 | [1.50, 1.89] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |      3.95e+03 |      1 | True       |         8.34 | [6.73, 11.15]  | True               |          1.6  | [1.39, 1.86] | True                |
| fixed       |       2 |  10 |        2     |            2    |      5        |      1 | False      |       nan    | edge           | False              |          2    | [1.50, 2.33] | True                |
| fixed       |       2 |  15 |        2     |            2    |     23        |      1 | False      |       nan    | edge           | False              |          2    | [1.83, 2.32] | True                |
| fixed       |       2 |  20 |        2     |            2    |     82.5      |      1 | False      |       nan    | edge           | False              |          2.09 | [1.83, 2.41] | True                |
| fixed       |       2 |  25 |        2     |            2    |    262        |      1 | False      |       nan    | edge           | False              |          2.16 | [1.93, 2.52] | True                |
| fixed       |       2 |  30 |        2     |            2    |    940        |      1 | False      |       nan    | edge           | False              |          2.51 | [2.18, 2.77] | True                |
| fixed       |       2 |  35 |        2     |            2    |      3.08e+03 |      1 | False      |       nan    | edge           | False              |          2.46 | [2.19, 2.80] | True                |
| fixed       |       2 |  40 |        2     |            2    |      9.97e+03 |      1 | False      |       nan    | edge           | False              |          2.64 | [2.17, 3.09] | True                |

### Peaks of the p90

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_p90 |   tied | interior   |   ratio_left | ci_left        | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|-----------:|-------:|:-----------|-------------:|:---------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.2   |            2.2  |  11        |      1 | True       |         1.09 | [0.91, 1.34]   | False              |          1.5  | [1.09, 1.62] | True                |
| bernoulli   |       1 |  15 |        0.15  |            2.4  |  29.1      |      1 | True       |         1.2  | [0.84, 1.52]   | False              |          1.2  | [0.96, 1.55] | False               |
| bernoulli   |       1 |  20 |        0.1   |            2.25 |  91.1      |      1 | True       |         1.67 | [1.29, 1.92]   | True               |          1.17 | [0.93, 1.40] | False               |
| bernoulli   |       1 |  25 |        0.1   |            2.56 | 245        |      1 | True       |         1.25 | [0.99, 1.67]   | False              |          1.76 | [1.42, 2.19] | True                |
| bernoulli   |       1 |  30 |        0.075 |            2.43 | 744        |      1 | True       |         2.87 | [2.13, 3.75]   | True               |          1.11 | [0.87, 1.42] | False               |
| bernoulli   |       1 |  35 |        0.075 |            2.77 |   2.04e+03 |      1 | True       |         2.25 | [1.64, 3.11]   | True               |          1.46 | [1.05, 1.85] | True                |
| bernoulli   |       1 |  40 |        0.075 |            3.1  |   4.64e+03 |      1 | True       |         1.57 | [1.24, 1.91]   | True               |          1.81 | [1.40, 2.29] | True                |
| bernoulli   |       2 |  10 |        0.15  |            1.7  |  10        |      1 | True       |         1.1  | [1.00, 1.33]   | False              |          1.38 | [1.22, 1.50] | True                |
| bernoulli   |       2 |  15 |        0.1   |            1.73 |  35.1      |      1 | True       |         1.24 | [1.04, 1.63]   | True               |          1.2  | [1.00, 1.63] | False               |
| bernoulli   |       2 |  20 |        0.1   |            2.12 |  99.4      |      1 | True       |         1.06 | [0.84, 1.27]   | False              |          2.57 | [2.13, 2.97] | True                |
| bernoulli   |       2 |  25 |        0.075 |            2.04 | 330        |      1 | True       |         1.59 | [1.20, 2.01]   | True               |          1.51 | [1.24, 1.97] | True                |
| bernoulli   |       2 |  30 |        0.075 |            2.35 | 856        |      1 | True       |         1.05 | [0.88, 1.43]   | False              |          2.76 | [2.30, 3.21] | True                |
| bernoulli   |       2 |  35 |        0.05  |            1.91 |   3.04e+03 |      1 | True       |        16.5  | [11.24, 23.18] | True               |          1.54 | [1.25, 1.93] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.12 |   9.91e+03 |      1 | True       |        14.6  | [11.08, 21.71] | True               |          3.29 | [2.72, 4.15] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |  12        |      1 | False      |       nan    | edge           | False              |          1.44 | [1.22, 1.75] | True                |
| fixed       |       1 |  15 |        2     |            2.13 |  27.2      |      1 | False      |       nan    | edge           | False              |          1.04 | [0.90, 1.26] | False               |
| fixed       |       1 |  20 |        3     |            3.05 |  93.1      |      1 | True       |         1.32 | [1.14, 1.57]   | True               |          1.84 | [1.62, 2.12] | True                |
| fixed       |       1 |  25 |        3     |            3.04 | 261        |      1 | True       |         2.08 | [1.65, 2.45]   | True               |          1.72 | [1.43, 1.96] | True                |
| fixed       |       1 |  30 |        3     |            3.03 | 874        |      1 | True       |         2.89 | [2.38, 3.48]   | True               |          1.88 | [1.57, 2.27] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |   2.78e+03 |      1 | True       |         4.22 | [3.69, 5.08]   | True               |          1.93 | [1.68, 2.43] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |   8.07e+03 |      1 | True       |         7.67 | [5.57, 8.94]   | True               |          1.66 | [1.38, 2.26] | True                |
| fixed       |       2 |  10 |        2     |            2    |  11        |      1 | False      |       nan    | edge           | False              |          2.4  | [2.20, 2.62] | True                |
| fixed       |       2 |  15 |        2     |            2    |  40        |      1 | False      |       nan    | edge           | False              |          2.28 | [2.05, 2.71] | True                |
| fixed       |       2 |  20 |        2     |            2    | 174        |      1 | False      |       nan    | edge           | False              |          3.02 | [2.59, 3.43] | True                |
| fixed       |       2 |  25 |        2     |            2    | 607        |      1 | False      |       nan    | edge           | False              |          3.2  | [2.60, 3.93] | True                |
| fixed       |       2 |  30 |        2     |            2    |   2.13e+03 |      1 | False      |       nan    | edge           | False              |          3.16 | [2.77, 4.28] | True                |
| fixed       |       2 |  35 |        2     |            2    |   6.58e+03 |      1 | False      |       nan    | edge           | False              |          3.09 | [2.57, 3.86] | True                |
| fixed       |       2 |  40 |        2     |            2    |   2.2e+04  |      1 | False      |       nan    | edge           | False              |          3.48 | [2.77, 4.56] | True                |

### Peaks of the median, connected instances only

| generator   |   ratio |   n |   peak_param |   peak_col_mean |   peak_median |   tied | interior   |   ratio_left | ci_left       | significant_left   |   ratio_right | ci_right     | significant_right   |
|:------------|--------:|----:|-------------:|----------------:|--------------:|-------:|:-----------|-------------:|:--------------|:-------------------|--------------:|:-------------|:--------------------|
| bernoulli   |       1 |  10 |        0.15  |            2.1  |      6        |      2 | True       |         2.33 | [1.17, 3.50]  | True               |          1    | [0.86, 1.29] | False               |
| bernoulli   |       1 |  15 |        0.075 |            1.93 |     40        |      1 | False      |       nan    | edge          | False              |          2.28 | [1.52, 3.73] | True                |
| bernoulli   |       1 |  20 |        0.1   |            2.45 |     51        |      1 | True       |         1.44 | [0.48, 2.00]  | False              |          1.3  | [1.08, 1.65] | True                |
| bernoulli   |       1 |  25 |        0.1   |            2.68 |    121        |      1 | True       |         1.03 | [0.58, 1.61]  | False              |          1.51 | [1.31, 1.85] | True                |
| bernoulli   |       1 |  30 |        0.1   |            3.1  |    366        |      1 | True       |         1.07 | [0.82, 1.32]  | False              |          3.3  | [2.73, 3.64] | True                |
| bernoulli   |       1 |  35 |        0.075 |            2.86 |      1.05e+03 |      1 | True       |         2.85 | [0.94, 4.88]  | False              |          1.43 | [1.13, 1.70] | True                |
| bernoulli   |       1 |  40 |        0.075 |            3.15 |      2.45e+03 |      1 | True       |         1.22 | [0.83, 2.71]  | False              |          1.85 | [1.60, 2.38] | True                |
| bernoulli   |       2 |  10 |        0.15  |            1.8  |      6        |      1 | True       |         1.17 | [0.75, 1.40]  | False              |          1.75 | [1.20, 2.00] | True                |
| bernoulli   |       2 |  15 |        0.075 |            1.63 |     29        |      1 | False      |       nan    | edge          | False              |          1.58 | [0.84, 2.19] | False               |
| bernoulli   |       2 |  20 |        0.05  |            1.57 |     74        |      1 | False      |       nan    | edge          | False              |          1.08 | [0.62, 1.47] | False               |
| bernoulli   |       2 |  25 |        0.05  |            1.74 |    222        |      1 | False      |       nan    | edge          | False              |          1.3  | [0.78, 2.41] | False               |
| bernoulli   |       2 |  30 |        0.05  |            1.85 |    491        |      1 | False      |       nan    | edge          | False              |          1.21 | [0.94, 2.17] | False               |
| bernoulli   |       2 |  35 |        0.05  |            2    |      1.87e+03 |      1 | False      |       nan    | edge          | False              |          2.14 | [1.83, 2.55] | True                |
| bernoulli   |       2 |  40 |        0.05  |            2.17 |      4.58e+03 |      1 | False      |       nan    | edge          | False              |          3.31 | [2.70, 4.44] | True                |
| fixed       |       1 |  10 |        2     |            2.1  |      5        |      2 | False      |       nan    | edge          | False              |          1    | [0.83, 1.30] | False               |
| fixed       |       1 |  15 |        3     |            3    |     16.5      |      1 | True       |         1.25 | [0.94, 1.70]  | False              |          1.75 | [1.55, 1.90] | True                |
| fixed       |       1 |  20 |        3     |            3.05 |     53        |      1 | True       |         1.38 | [1.12, 2.12]  | True               |          1.74 | [1.58, 1.97] | True                |
| fixed       |       1 |  25 |        3     |            3.04 |    155        |      1 | True       |         2.42 | [2.01, 2.96]  | True               |          1.73 | [1.49, 1.92] | True                |
| fixed       |       1 |  30 |        3     |            3.03 |    455        |      1 | True       |         3.74 | [3.11, 4.56]  | True               |          1.58 | [1.40, 1.76] | True                |
| fixed       |       1 |  35 |        3     |            3.06 |      1.4e+03  |      1 | True       |         4.26 | [3.04, 6.71]  | True               |          1.69 | [1.49, 1.92] | True                |
| fixed       |       1 |  40 |        3     |            3.05 |      3.95e+03 |      1 | True       |         6.52 | [4.93, 11.55] | True               |          1.6  | [1.38, 1.86] | True                |
| fixed       |       2 |  10 |        2     |            2    |      5        |      1 | False      |       nan    | edge          | False              |          2    | [1.50, 2.33] | True                |
| fixed       |       2 |  15 |        2     |            2    |     23        |      1 | False      |       nan    | edge          | False              |          2    | [1.77, 2.27] | True                |
| fixed       |       2 |  20 |        2     |            2    |     82.5      |      1 | False      |       nan    | edge          | False              |          2.09 | [1.83, 2.40] | True                |
| fixed       |       2 |  25 |        2     |            2    |    267        |      1 | False      |       nan    | edge          | False              |          2.21 | [1.97, 2.57] | True                |
| fixed       |       2 |  30 |        2     |            2    |    949        |      1 | False      |       nan    | edge          | False              |          2.54 | [2.22, 2.76] | True                |
| fixed       |       2 |  35 |        2     |            2    |      3.11e+03 |      1 | False      |       nan    | edge          | False              |          2.49 | [2.19, 2.87] | True                |
| fixed       |       2 |  40 |        2     |            2    |      9.99e+03 |      1 | False      |       nan    | edge          | False              |          2.65 | [2.21, 3.09] | True                |

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
| bernoulli   |       1 |  10 |      6        |              0.412 |                2.58 | left open   |               0.585 |                 3.85 | left open; right open |                 1.17 |            7        |
| bernoulli   |       1 |  15 |     16        |              0.437 |                2.73 | left open   |               0.651 |                 4.47 | left open             |                 1.89 |           17        |
| bernoulli   |       1 |  20 |     40.5      |              0.36  |                2.29 |             |               0.675 |                 4.74 | left open             |                 3.46 |           41.5      |
| bernoulli   |       1 |  25 |    112        |              0.328 |                2.13 |             |               0.639 |                 4.35 | left open             |                 7.53 |          113        |
| bernoulli   |       1 |  30 |    339        |              0.247 |                1.76 |             |               0.577 |                 3.77 |                       |                17    |          340        |
| bernoulli   |       1 |  35 |    796        |              0.255 |                1.8  |             |               0.532 |                 3.41 |                       |                28.5  |          797        |
| bernoulli   |       1 |  40 |      2.22e+03 |              0.243 |                1.75 |             |               0.481 |                 3.03 |                       |                44.9  |            2.22e+03 |
| bernoulli   |       2 |  10 |      6        |              0.341 |                2.19 | left open   |               0.658 |                 4.55 | left open; right open |                 1    |            7        |
| bernoulli   |       2 |  15 |     17        |              0.39  |                2.45 | left open   |               0.612 |                 4.1  | left open             |                 1.8  |           18        |
| bernoulli   |       2 |  20 |     52.5      |              0.302 |                2.01 |             |               0.579 |                 3.79 | left open             |                 3.82 |           53.5      |
| bernoulli   |       2 |  25 |    147        |              0.263 |                1.83 |             |               0.549 |                 3.54 | left open             |                 7.42 |          148        |
| bernoulli   |       2 |  30 |    394        |              0.256 |                1.8  |             |               0.512 |                 3.25 |                       |                12.8  |          395        |
| bernoulli   |       2 |  35 |      1.34e+03 |              0.204 |                1.6  |             |               0.432 |                 2.7  |                       |                18.4  |            1.34e+03 |
| bernoulli   |       2 |  40 |      4.27e+03 |              0.135 |                1.36 |             |               0.38  |                 2.4  |                       |                25.6  |            4.27e+03 |
| fixed       |       1 |  10 |      5        |              0.28  |                1.9  | left open   |               0.678 |                 4.76 | left open; right open |                 1    |            6        |
| fixed       |       1 |  15 |     16.5      |              0.292 |                1.96 | left open   |               0.527 |                 3.37 | left open             |                 1.35 |           17.5      |
| fixed       |       1 |  20 |     53        |              0.298 |                1.99 | left open   |               0.498 |                 3.15 | left open             |                 1.54 |           54        |
| fixed       |       1 |  25 |    155        |              0.249 |                1.77 |             |               0.474 |                 2.98 | left open             |                 2.67 |           78        |
| fixed       |       1 |  30 |    460        |              0.221 |                1.66 |             |               0.458 |                 2.87 | left open             |                 4.19 |          115        |
| fixed       |       1 |  35 |      1.4e+03  |              0.196 |                1.57 |             |               0.436 |                 2.73 | left open             |                 5.71 |          175        |
| fixed       |       1 |  40 |      3.95e+03 |              0.19  |                1.55 |             |               0.433 |                 2.71 | left open             |                 8.34 |          282        |
| fixed       |       2 |  10 |      5        |              0.176 |                1.5  | left open   |               0.699 |                 5    | left open; right open |                 1    |            6        |
| fixed       |       2 |  15 |     23        |              0.176 |                1.5  | left open   |               0.372 |                 2.36 | left open             |                 1    |           24        |
| fixed       |       2 |  20 |     82.5      |              0.166 |                1.47 | left open   |               0.348 |                 2.23 | left open             |                 1    |           83.5      |
| fixed       |       2 |  25 |    262        |              0.158 |                1.44 | left open   |               0.329 |                 2.13 | left open             |                 1    |          263        |
| fixed       |       2 |  30 |    941        |              0.132 |                1.36 | left open   |               0.302 |                 2.01 | left open             |                 1    |          942        |
| fixed       |       2 |  35 |      3.08e+03 |              0.135 |                1.37 | left open   |               0.28  |                 1.91 | left open             |                 1    |            3.08e+03 |
| fixed       |       2 |  40 |      9.97e+03 |              0.126 |                1.34 | left open   |               0.269 |                 1.86 | left open             |                 1    |            4.98e+03 |

### Scaling of the median with n (n >= 15, cells with median >= 2)

| generator   |   ratio | where                       |   param |   points |      rate |   doubling_n |   rms_exp |   alpha |   rms_pow | better      |
|:------------|--------:|:----------------------------|--------:|---------:|----------:|-------------:|----------:|--------:|----------:|:------------|
| bernoulli   |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0861  |         3.49 |    0.021  |   5.03  |   0.105   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.025 |        6 |   0.0298  |        10.1  |    0.04   |   1.71  |   0.0712  | exponential |
| bernoulli   |       1 | fixed parameter             |   0.05  |        6 |   0.0854  |         3.53 |    0.118  |   4.87  |   0.22    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.075 |        6 |   0.0977  |         3.08 |    0.029  |   5.69  |   0.133   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.1   |        6 |   0.0829  |         3.63 |    0.0865 |   4.92  |   0.0361  | power       |
| bernoulli   |       1 | fixed parameter             |   0.15  |        6 |   0.0428  |         7.03 |    0.0954 |   2.59  |   0.0447  | power       |
| bernoulli   |       1 | fixed parameter             |   0.2   |        6 |   0.0172  |        17.5  |    0.0839 |   1.08  |   0.0638  | power       |
| bernoulli   |       1 | fixed parameter             |   0.3   |        6 |  -0.00855 |       inf    |    0.0346 |  -0.472 |   0.043   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.4   |        0 | nan       |       nan    |  nan      | nan     | nan       |             |
| bernoulli   |       1 | fixed parameter             |   0.5   |        0 | nan       |       nan    |  nan      | nan     | nan       |             |
| bernoulli   |       2 | ridge (peak cell at each n) | nan     |        6 |   0.0951  |         3.16 |    0.0268 |   5.54  |   0.132   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.025 |        6 |   0.05    |         6.02 |    0.0866 |   2.84  |   0.144   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.05  |        6 |   0.11    |         2.74 |    0.0642 |   6.36  |   0.185   | exponential |
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
| fixed       |       1 | fixed parameter             |   8     |        4 |   0.0669  |         4.5  |    0.0186 |   4.92  |   0.00934 | power       |
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
| fixed       |       2 | fixed parameter             |   9     |        1 | nan       |       nan    |  nan      | nan     | nan       |             |
| fixed       |       2 | fixed parameter             |  10     |        0 | nan       |       nan    |  nan      | nan     | nan       |             |

### Scaling of the p90 with n

| generator   |   ratio | where                       |   param |   points |      rate |   doubling_n |   rms_exp |   alpha |    rms_pow | better      |
|:------------|--------:|:----------------------------|--------:|---------:|----------:|-------------:|----------:|--------:|-----------:|:------------|
| bernoulli   |       1 | ridge (peak cell at each n) | nan     |        6 |   0.0888  |         3.39 |   0.0346  |   5.21  |   0.0828   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.025 |        6 |   0.0489  |         6.15 |   0.0773  |   2.79  |   0.133    | exponential |
| bernoulli   |       1 | fixed parameter             |   0.05  |        6 |   0.0984  |         3.06 |   0.0428  |   5.7   |   0.16     | exponential |
| bernoulli   |       1 | fixed parameter             |   0.075 |        6 |   0.0992  |         3.03 |   0.064   |   5.83  |   0.0931   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.1   |        6 |   0.0808  |         3.73 |   0.0911  |   4.8   |   0.0203   | power       |
| bernoulli   |       1 | fixed parameter             |   0.15  |        6 |   0.0418  |         7.2  |   0.101   |   2.54  |   0.0498   | power       |
| bernoulli   |       1 | fixed parameter             |   0.2   |        6 |   0.0145  |        20.7  |   0.0948  |   0.941 |   0.0764   | power       |
| bernoulli   |       1 | fixed parameter             |   0.3   |        6 |  -0.0124  |       inf    |   0.0306  |  -0.703 |   0.0431   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.4   |        3 |  -0.0176  |       inf    |   0.0415  |  -0.756 |   0.0466   | exponential |
| bernoulli   |       1 | fixed parameter             |   0.5   |        0 | nan       |       nan    | nan       | nan     | nan        |             |
| bernoulli   |       2 | ridge (peak cell at each n) | nan     |        6 |   0.0979  |         3.08 |   0.0292  |   5.69  |   0.138    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.025 |        6 |   0.0692  |         4.35 |   0.0977  |   3.96  |   0.173    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.05  |        6 |   0.112   |         2.69 |   0.0174  |   6.52  |   0.138    | exponential |
| bernoulli   |       2 | fixed parameter             |   0.075 |        6 |   0.0831  |         3.62 |   0.112   |   4.95  |   0.0423   | power       |
| bernoulli   |       2 | fixed parameter             |   0.1   |        6 |   0.0468  |         6.44 |   0.124   |   2.85  |   0.0689   | power       |
| bernoulli   |       2 | fixed parameter             |   0.15  |        6 |   0.00747 |        40.3  |   0.0534  |   0.487 |   0.0441   | power       |
| bernoulli   |       2 | fixed parameter             |   0.2   |        6 |  -0.00623 |       inf    |   0.0236  |  -0.357 |   0.0268   | exponential |
| bernoulli   |       2 | fixed parameter             |   0.3   |        2 | nan       |       nan    | nan       | nan     | nan        |             |
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
| fixed       |       1 | fixed parameter             |   9     |        4 |   0.0645  |         4.67 |   0.029   |   4.74  |   0.0241   | power       |
| fixed       |       1 | fixed parameter             |  10     |        4 |   0.0641  |         4.7  |   0.0467  |   4.74  |   0.0232   | power       |
| fixed       |       2 | ridge (peak cell at each n) | nan     |        6 |   0.108   |         2.78 |   0.0388  |   6.37  |   0.0955   | exponential |
| fixed       |       2 | fixed parameter             |   2     |        6 |   0.108   |         2.78 |   0.0388  |   6.37  |   0.0955   | exponential |
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
| g_deg_mean   | mean degree of the MOSP graph    |             0.291 |     0.926 |             0.949 |            6.21   |           0.19  |           4      |            8.28  |                          15 |
| opt_frac     | optimum / n                      |             0.313 |     0.912 |             0.949 |            0.33   |           0.137 |           0.28   |            0.433 |                          15 |
| density      | matrix density                   |             0.633 |     0.827 |             0.949 |            0.0924 |           0.279 |           0.0531 |            0.152 |                          15 |
| col_mean     | customers per product (realised) |             0.633 |     0.827 |             0.949 |            2.64   |           0.173 |           1.91   |            3.1   |                          15 |
| bound_gap    | ub_best - lb_best                |             0.714 |     0.32  |             0.949 |            2.27   |           0.513 |           1      |            4     |                          15 |
| g_components | components of the MOSP graph     |             0.803 |     0.024 |             0.949 |            1.33   |           0.366 |           1      |            2     |                          15 |

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
| g_components |       2 | 20: 4, 25: 4                                          | True                  | 4      | 0     |
| opt_frac     |       5 | 20: 0.3, 25: 0.32, 30: 0.333, 35: 0.343, 40: 0.25     | True                  | 0.309  | 0.119 |
| col_mean     |       5 | 20: 2.05, 25: 3, 30: 2.73, 35: 2.87, 40: 3            | True                  | 2.73   | 0.145 |
| density      |       5 | 20: 0.102, 25: 0.12, 30: 0.0911, 35: 0.082, 40: 0.075 | True                  | 0.0941 | 0.189 |
| g_deg_mean   |       5 | 20: 3.8, 25: 5.12, 30: 5.8, 35: 6.91, 40: 4.3         | True                  | 5.19   | 0.238 |
| bound_gap    |       4 | 25: 3, 30: 3, 35: 4, 40: 5                            | False                 | 3.75   | 0.255 |

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
| bernoulli   |       2 |  10 | False      | False              |
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
| col_mean    |  10 |     10 |        0.16  | 0.763 |
| col_mean    |  15 |     10 |        0.245 | 0.817 |
| col_mean    |  20 |     10 |        0.329 | 0.822 |
| col_mean    |  25 |     10 |        0.519 | 0.834 |
| col_mean    |  30 |     10 |        0.606 | 0.834 |
| col_mean    |  35 |     10 |        0.81  | 0.824 |
| col_mean    |  40 |     10 |        0.9   | 0.823 |

### Collapse by n: density

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| density     |  10 |     10 |        0.16  | 0.763 |
| density     |  15 |     10 |        0.245 | 0.817 |
| density     |  20 |     10 |        0.329 | 0.822 |
| density     |  25 |     10 |        0.519 | 0.834 |
| density     |  30 |     10 |        0.606 | 0.834 |
| density     |  35 |     10 |        0.81  | 0.824 |
| density     |  40 |     10 |        0.9   | 0.823 |

### Collapse by n: g_deg_mean

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| g_deg_mean  |  10 |      7 |       0.034  | 0.833 |
| g_deg_mean  |  15 |      8 |       0.0683 | 0.897 |
| g_deg_mean  |  20 |      9 |       0.176  | 0.91  |
| g_deg_mean  |  25 |      9 |       0.18   | 0.926 |
| g_deg_mean  |  30 |      9 |       0.244  | 0.933 |
| g_deg_mean  |  35 |      9 |       0.329  | 0.937 |
| g_deg_mean  |  40 |      9 |       0.524  | 0.923 |

### Collapse by n: opt_frac

| candidate   |   n |   bins |   dispersion |    r2 |
|:------------|----:|-------:|-------------:|------:|
| opt_frac    |  10 |      6 |        0.148 | 0.787 |
| opt_frac    |  15 |      8 |        0.128 | 0.863 |
| opt_frac    |  20 |      9 |        0.209 | 0.891 |
| opt_frac    |  25 |      9 |        0.325 | 0.896 |
| opt_frac    |  30 |      9 |        0.304 | 0.917 |
| opt_frac    |  35 |      9 |        0.371 | 0.919 |
| opt_frac    |  40 |      9 |        0.355 | 0.936 |

### Collapse by n: bound_gap

| candidate   |   n |   bins |   dispersion |       r2 |
|:------------|----:|-------:|-------------:|---------:|
| bound_gap   |  10 |      1 |        0.699 | 6.11e-15 |
| bound_gap   |  15 |      2 |        0.894 | 0.0111   |
| bound_gap   |  20 |      2 |        0.748 | 0.0848   |
| bound_gap   |  25 |      3 |        0.675 | 0.194    |
| bound_gap   |  30 |      3 |        0.516 | 0.331    |
| bound_gap   |  35 |      4 |        0.736 | 0.448    |
| bound_gap   |  40 |      5 |        0.895 | 0.543    |

### Collapse by n: g_components

| candidate    |   n |   bins |   dispersion |      r2 |
|:-------------|----:|-------:|-------------:|--------:|
| g_components |  10 |      3 |        0.492 | 0.101   |
| g_components |  15 |      3 |        0.64  | 0.137   |
| g_components |  20 |      3 |        0.558 | 0.0755  |
| g_components |  25 |      2 |        0.684 | 0.0114  |
| g_components |  30 |      2 |        0.61  | 0.00703 |
| g_components |  35 |      2 |        0.914 | 0.015   |
| g_components |  40 |      2 |        1.25  | 0.0111  |

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
|   8 |          8 |    0 |    0 |    1 |    5 |   12 |   25 |   51 |
|   9 |          9 |    0 |    0 |    0 |    2 |    6 |   12 |   25 |
|  10 |         10 |    0 |    0 |    0 |    1 |    3 |    7 |   13 |

**fixed, m = 2n**

|   d |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   2 |          2 |    5 |   23 |   82 |  267 |  949 | 3106 | 9992 |
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
|   0 |          2 |  nan |  nan |  nan |  nan |  166 |  368 | 1999 |
|   0 |          2 |  nan |   40 |   35 |  117 |  340 | 1050 | 2448 |
|   0 |          3 |    2 |   17 |   51 |  121 |  366 |  732 | 1326 |
|   0 |          4 |    6 |   18 |   39 |   80 |  110 |  164 |  198 |
|   0 |          5 |    6 |   13 |   21 |   32 |   38 |   34 |   37 |
|   0 |          8 |    4 |    5 |    5 |    5 |    4 |    4 |    3 |
|   0 |         10 |    1 |    1 |    1 |    1 |    0 |    0 |    0 |
|   0 |         12 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |

**bernoulli, m = 2n**

|   p |   col_mean |   10 |   15 |   20 |   25 |   30 |   35 |   40 |
|----:|-----------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
|   0 |          2 |  nan |  nan |   74 |  222 |  491 | 1872 | 4578 |
|   0 |          2 |    5 |   29 |   68 |  170 |  406 |  876 | 1384 |
|   0 |          3 |    5 |   18 |   56 |  112 |  173 |  224 |  316 |
|   0 |          4 |    6 |   14 |   21 |   25 |   30 |   28 |   28 |
|   0 |          5 |    3 |    6 |    7 |    7 |    6 |    5 |    5 |
|   0 |          8 |    1 |    1 |    1 |    0 |    0 |    0 |    0 |
|   0 |         10 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |
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

