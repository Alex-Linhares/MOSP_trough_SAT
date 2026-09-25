6376 instances, 617 files, 9 collections, 28 structure features, 19 size-free features; canonical forms joined

## Instances per collection

| collection                          |   instances |   files |   n_min |   n_max |
|:------------------------------------|------------:|--------:|--------:|--------:|
| ChallengeInstances2005/Harvey       |        2130 |      30 |      10 |      30 |
| ChallengeInstances2005/Miller       |           1 |       1 |      20 |      20 |
| ChallengeInstances2005/Shaw         |          25 |       1 |      20 |      20 |
| ChallengeInstances2005/Simonis      |        3630 |      10 |      10 |      40 |
| ChallengeInstances2005/Wilson       |          20 |       5 |      10 |     100 |
| MOSP_Instances/Challenge            |          46 |      46 |      10 |     100 |
| MOSP_Instances/Chu_Stuckey          |         200 |     200 |      30 |     125 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 |     300 |       9 |      50 |
| MOSP_Instances/SCOOP                |          24 |      24 |      13 |     134 |

## Study 1: the collection from structure

| features             | split                         |   accuracy |   balanced_accuracy |   macro_f1 |
|:---------------------|:------------------------------|-----------:|--------------------:|-----------:|
| majority class       | none (baseline)               |      0.569 |               0.111 |    nan     |
| size only (n, m)     | grouped by file               |      0.261 |               0.324 |      0.307 |
| size only (n, m)     | grouped by file + graph class |      0.134 |               0.290 |      0.171 |
| size only (n, m)     | random (leaks!)               |      0.728 |               0.420 |      0.455 |
| structure (all)      | grouped by file               |      0.944 |               0.507 |      0.491 |
| structure (all)      | grouped by file + graph class |      0.933 |               0.509 |      0.475 |
| structure (all)      | random (leaks!)               |      0.981 |               0.537 |      0.554 |
| structure, size-free | grouped by file               |      0.951 |               0.506 |      0.495 |
| structure, size-free | grouped by file + graph class |      0.957 |               0.511 |      0.513 |
| structure, size-free | random (leaks!)               |      0.980 |               0.526 |      0.546 |

groups per split: {'grouped by file': 617, 'grouped by file + graph class': 512, 'random (leaks!)': None}
ceiling from bipartite_cert classes: 0.9931
ceiling from graph_cert classes: 0.8785

### Per-class recall, structure (all), grouped by file

| collection                          |   instances |   files |   recall |
|:------------------------------------|------------:|--------:|---------:|
| ChallengeInstances2005/Harvey       |        2130 |      30 |    1.000 |
| ChallengeInstances2005/Miller       |           1 |       1 |    0.000 |
| ChallengeInstances2005/Shaw         |          25 |       1 |    0.000 |
| ChallengeInstances2005/Simonis      |        3630 |      10 |    0.934 |
| ChallengeInstances2005/Wilson       |          20 |       5 |    0.000 |
| MOSP_Instances/Challenge            |          46 |      46 |    0.130 |
| MOSP_Instances/Chu_Stuckey          |         200 |     200 |    0.935 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 |     300 |    0.983 |
| MOSP_Instances/SCOOP                |          24 |      24 |    0.583 |

with the file + graph-class split: Harvey 1.000, Miller 0.000, Shaw 0.000, Simonis 0.913, Wilson 0.050, Challenge 0.065, Chu_Stuckey 0.955, Faggioli_Bentivoglio 0.970, SCOOP 0.625

### Confusion matrix (rows true, columns predicted), structure (all), grouped by file

| true \ predicted     |   Harvey |   Miller |   Shaw |   Simonis |   Wilson |   Challenge |   Chu_Stuckey |   Faggioli_Bentivoglio |   SCOOP |
|:---------------------|---------:|---------:|-------:|----------:|---------:|------------:|--------------:|-----------------------:|--------:|
| Harvey               |     2130 |        0 |      0 |         0 |        0 |           0 |             0 |                      0 |       0 |
| Miller               |        0 |        0 |      0 |         0 |        0 |           1 |             0 |                      0 |       0 |
| Shaw                 |        0 |        0 |      0 |         0 |        0 |          25 |             0 |                      0 |       0 |
| Simonis              |       17 |        0 |      0 |      3390 |        2 |           2 |            74 |                    145 |       0 |
| Wilson               |        0 |        0 |      0 |         1 |        0 |          18 |             1 |                      0 |       0 |
| Challenge            |        0 |        1 |     23 |         1 |       14 |           6 |             1 |                      0 |       0 |
| Chu_Stuckey          |        0 |        0 |      0 |        13 |        0 |           0 |           187 |                      0 |       0 |
| Faggioli_Bentivoglio |        0 |        0 |      0 |         5 |        0 |           0 |             0 |                    295 |       0 |
| SCOOP                |        0 |        0 |      0 |         4 |        0 |           0 |             1 |                      5 |      14 |

### Permutation importance (accuracy points, held-out files)

| feature      |   accuracy_cost |
|:-------------|----------------:|
| col_std      |           0.196 |
| row_std      |           0.147 |
| density      |           0.114 |
| col_max_frac |           0.113 |
| row_min      |           0.019 |
| row_max      |           0.011 |
| g_deg_std    |           0.009 |
| col_max      |           0.008 |
| col_min      |           0.006 |
| g_density    |           0.006 |
| col_mean     |           0.004 |
| n_ones       |           0.003 |

### Depth-3 tree on size-free features: grouped-by-file accuracy 0.940

```
|--- col_cv <= 0.017
|   |--- row_max_frac <= 0.217
|   |   |--- g_clustering <= 0.595
|   |   |   |--- class: Harvey
|   |   |--- g_clustering >  0.595
|   |   |   |--- class: Harvey
|   |--- row_max_frac >  0.217
|   |   |--- class: Harvey
|--- col_cv >  0.017
|   |--- row_cv <= 0.035
|   |   |--- distinct_row_frac <= 0.942
|   |   |   |--- class: Harvey
|   |   |--- distinct_row_frac >  0.942
|   |   |   |--- class: Harvey
|   |--- row_cv >  0.035
|   |   |--- col_max_frac <= 0.290
|   |   |   |--- class: Faggioli_Bentivoglio
|   |   |--- col_max_frac >  0.290
|   |   |   |--- class: Simonis
```

## Study 2: collections at the same (n, m)

| cell (n x m)     |   instances | collections                             |   majority |   structure (all) |   structure, size-free |
|:-----------------|------------:|:----------------------------------------|-----------:|------------------:|-----------------------:|
| 10x10            |         670 | Harvey + Simonis                        |      0.821 |             0.991 |                  1.000 |
| 10x20            |         710 | Faggioli_Bentivoglio + Harvey + Simonis |      0.775 |             0.939 |                  0.994 |
| 10x30            |         190 | Faggioli_Bentivoglio + Harvey           |      0.947 |             1.000 |                  1.000 |
| 15x15            |         730 | Harvey + Simonis                        |      0.753 |             1.000 |                  1.000 |
| 15x30            |         460 | Harvey + Simonis                        |      0.522 |             1.000 |                  1.000 |
| 20x10            |         710 | Faggioli_Bentivoglio + Harvey + Simonis |      0.775 |             0.996 |                  0.996 |
| 20x20            |         540 | Challenge + Harvey + Shaw + Simonis     |      0.500 |             0.917 |                  0.917 |
| 30x10            |         740 | Faggioli_Bentivoglio + Harvey + Simonis |      0.743 |             0.999 |                  0.999 |
| 30x15            |         470 | Faggioli_Bentivoglio + Harvey + Simonis |      0.511 |             1.000 |                  1.000 |
| 30x30            |         555 | Chu_Stuckey + Harvey + Simonis          |      0.757 |             0.908 |                  0.964 |
| 40x20            |         120 | Faggioli_Bentivoglio + Simonis          |      0.917 |             1.000 |                  1.000 |
| all shared cells |        5895 |                                         |      0.616 |             0.975 |                  0.988 |

## Study 3: within Chu & Stuckey, Random-n-m-d-k

| target                 | features             |   accuracy |   balanced_accuracy |
|:-----------------------|:---------------------|-----------:|--------------------:|
| density class d        | majority class       |      0.200 |               0.200 |
| density class d        | size only (n, m)     |      0.035 |               0.035 |
| density class d        | structure (all)      |      0.980 |               0.980 |
| density class d        | structure, size-free |      0.875 |               0.875 |
| density class d        | col_mean alone       |      0.980 |               0.980 |
| seed index k (control) | majority class       |      0.200 |               0.200 |
| seed index k (control) | size only (n, m)     |      0.040 |               0.040 |
| seed index k (control) | structure (all)      |      0.045 |               0.045 |
| seed index k (control) | structure, size-free |      0.050 |               0.050 |
| seed index k (control) | col_mean alone       |      0.200 |               0.200 |

## The map

embedding: UMAP
figure: reports/figures/instance_space.png; coordinates: learning/data/instance_space.csv

### 10-nearest-neighbour purity (share of neighbours from the same collection)

| collection                          |   instances |   features |   map |   size-free map |
|:------------------------------------|------------:|-----------:|------:|----------------:|
| ChallengeInstances2005/Harvey       |        2130 |      0.960 | 0.952 |           0.991 |
| ChallengeInstances2005/Miller       |           1 |      0.000 | 0.000 |           0.000 |
| ChallengeInstances2005/Shaw         |          25 |      0.480 | 0.436 |           0.468 |
| ChallengeInstances2005/Simonis      |        3630 |      0.987 | 0.971 |           0.984 |
| ChallengeInstances2005/Wilson       |          20 |      0.225 | 0.210 |           0.235 |
| MOSP_Instances/Challenge            |          46 |      0.393 | 0.339 |           0.352 |
| MOSP_Instances/Chu_Stuckey          |         200 |      0.861 | 0.872 |           0.854 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 |      0.877 | 0.820 |           0.862 |
| MOSP_Instances/SCOOP                |          24 |      0.146 | 0.058 |           0.083 |
| all                                 |        6376 |      0.957 | 0.942 |           0.964 |

### Regions of the map (k-means, 12)

|   region |   instances | n range   |   density |   optimum/n | composition                                                                                        |
|---------:|------------:|:----------|----------:|------------:|:---------------------------------------------------------------------------------------------------|
|        7 |         998 | 9-30      |      0.30 |        0.72 | Harvey 638, Simonis 262, Faggioli_Bentivoglio 87, Challenge 4, Wilson 3, SCOOP 3, Miller 1         |
|        0 |         920 | 20-134    |      0.24 |        0.60 | Harvey 431, Chu_Stuckey 200, Faggioli_Bentivoglio 161, Simonis 113, SCOOP 9, Wilson 3, Challenge 3 |
|        3 |         809 | 10-25     |      0.45 |        0.89 | Simonis 748, Harvey 51, Wilson 4, Challenge 4, SCOOP 2                                             |
|        5 |         747 | 10-99     |      0.39 |        0.69 | Simonis 574, Harvey 134, Faggioli_Bentivoglio 30, SCOOP 9                                          |
|        9 |         630 | 9-20      |      0.45 |        0.81 | Simonis 497, Harvey 118, Faggioli_Bentivoglio 14, SCOOP 1                                          |
|        4 |         588 | 30-30     |      0.45 |        0.80 | Simonis 548, Harvey 40                                                                             |
|        1 |         508 | 10-20     |      0.40 |        0.90 | Harvey 238, Simonis 216, Challenge 27, Shaw 25, Wilson 2                                           |
|       11 |         395 | 30-100    |      0.45 |        0.88 | Simonis 329, Harvey 50, Challenge 8, Wilson 8                                                      |
|        6 |         371 | 10-20     |      0.49 |        0.94 | Simonis 343, Harvey 20, Faggioli_Bentivoglio 8                                                     |
|        8 |         160 | 20-30     |      0.31 |        0.86 | Harvey 160                                                                                         |
|        2 |         140 | 15-30     |      0.34 |        0.93 | Harvey 140                                                                                         |
|       10 |         110 | 30-30     |      0.33 |        0.88 | Harvey 110                                                                                         |
