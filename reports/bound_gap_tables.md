6376 instances, n_customers 9-134, 5938 at n <= 30; gap = optimum - lb_best: 4909 tight, 1129 at gap 1, 338 at gap >= 2; smallest gap >= 2 instance has 20 customers

## Where the gap is: by size band

| band   |   instances |   tight |   gap 1 |   gap >= 2 |   frac gap >= 2 |   mean gap |   max gap |
|:-------|------------:|--------:|--------:|-----------:|----------------:|-----------:|----------:|
| 1-10   |        1614 |    1566 |      48 |          0 |           0.000 |      0.030 |         1 |
| 11-20  |        2508 |    2051 |     440 |         17 |           0.007 |      0.189 |         2 |
| 21-30  |        1816 |    1134 |     549 |        133 |           0.073 |      0.450 |         3 |
| 31-60  |         318 |     144 |      73 |        101 |           0.318 |      1.132 |         5 |
| 61-200 |         120 |      14 |      19 |         87 |           0.725 |      8.708 |        30 |

## Where the gap is: by collection

| collection                          |   instances | n range   |   tight |   gap 1 |   gap >= 2 |   frac gap >= 2 |   mean gap |   max gap |
|:------------------------------------|------------:|:----------|--------:|--------:|-----------:|----------------:|-----------:|----------:|
| MOSP_Instances/Chu_Stuckey          |         200 | 30-125    |      53 |      45 |        102 |           0.510 |      5.425 |        30 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 | 9-50      |     125 |      92 |         83 |           0.277 |      1.023 |         5 |
| ChallengeInstances2005/Wilson       |          20 | 10-100    |      16 |       1 |          3 |           0.150 |      1.550 |        16 |
| MOSP_Instances/SCOOP                |          24 | 13-134    |       6 |      15 |          3 |           0.125 |      1.042 |         6 |
| MOSP_Instances/Challenge            |          46 | 10-100    |      31 |      12 |          3 |           0.065 |      0.913 |        16 |
| ChallengeInstances2005/Harvey       |        2130 | 10-30     |    1605 |     454 |         71 |           0.033 |      0.281 |         3 |
| ChallengeInstances2005/Simonis      |        3630 | 10-40     |    3058 |     499 |         73 |           0.020 |      0.178 |         3 |
| ChallengeInstances2005/Miller       |           1 | 20-20     |       1 |       0 |          0 |           0.000 |      0.000 |         0 |
| ChallengeInstances2005/Shaw         |          25 | 20-20     |      14 |      11 |          0 |           0.000 |      0.440 |         1 |

## How far each component bound falls short

| rows     |   instances | bound          |   mean shortfall |   median shortfall |   max shortfall |   tight frac |
|:---------|------------:|:---------------|-----------------:|-------------------:|----------------:|-------------:|
| tight    |        4909 | lb_best        |            0.000 |              0.000 |               0 |        1.000 |
| tight    |        4909 | lb_contraction |            0.303 |              0.000 |              26 |        0.848 |
| tight    |        4909 | lb_trivial     |            5.207 |              4.000 |              66 |        0.048 |
| gap 1    |        1129 | lb_best        |            1.000 |              1.000 |               1 |        0.000 |
| gap 1    |        1129 | lb_contraction |            2.004 |              1.000 |              39 |        0.000 |
| gap 1    |        1129 | lb_trivial     |            7.744 |              6.000 |              86 |        0.000 |
| gap >= 2 |         338 | lb_best        |            4.781 |              2.000 |              30 |        0.000 |
| gap >= 2 |         338 | lb_contraction |            7.370 |              3.000 |              44 |        0.000 |
| gap >= 2 |         338 | lb_trivial     |           14.432 |              7.000 |              85 |        0.000 |

## The classifier: gap >= 2 against tight, grouped, all sizes

5247 rows (338 positives); gap-1 rows left out.

| split        | model              | features                              |   positives |   rows |   auc |   avg precision |   balanced acc |   auc 11-20 |   auc 21-30 |   auc 31-60 |   auc 61-200 |
|:-------------|:-------------------|:--------------------------------------|------------:|-------:|------:|----------------:|---------------:|------------:|------------:|------------:|-------------:|
| file ∪ class | tree (depth 3)     | density + size                        |         338 |   5247 | 0.884 |           0.263 |          0.851 |       0.746 |       0.804 |       0.730 |        0.786 |
| file ∪ class | tree (depth 3)     | structure (28)                        |         338 |   5247 | 0.946 |           0.523 |          0.928 |       0.688 |       0.898 |       0.905 |        0.906 |
| file ∪ class | tree (depth 3)     | structure + invariants (41)           |         338 |   5247 | 0.937 |           0.486 |          0.934 |       0.717 |       0.904 |       0.928 |        0.906 |
| file ∪ class | tree (depth 3)     | size-free (32)                        |         338 |   5247 | 0.942 |           0.524 |          0.936 |       0.908 |       0.892 |       0.904 |        0.900 |
| file ∪ class | tree (depth 3)     | structure + invariants + lower bounds |         338 |   5247 | 0.937 |           0.486 |          0.934 |       0.717 |       0.904 |       0.928 |        0.906 |
| file ∪ class | EBM                | density + size                        |         338 |   5247 | 0.920 |           0.349 |          0.632 |       0.950 |       0.918 |       0.724 |        0.611 |
| file ∪ class | EBM                | structure (28)                        |         338 |   5247 | 0.978 |           0.689 |          0.708 |       0.956 |       0.953 |       0.923 |        0.973 |
| file ∪ class | EBM                | structure + invariants (41)           |         338 |   5247 | 0.983 |           0.768 |          0.756 |       0.958 |       0.960 |       0.974 |        0.979 |
| file ∪ class | EBM                | size-free (32)                        |         338 |   5247 | 0.984 |           0.772 |          0.691 |       0.958 |       0.965 |       0.981 |        0.975 |
| file ∪ class | EBM                | structure + invariants + lower bounds |         338 |   5247 | 0.980 |           0.782 |          0.770 |       0.953 |       0.961 |       0.971 |        0.929 |
| file ∪ class | boosting (ceiling) | density + size                        |         338 |   5247 | 0.963 |           0.566 |          0.870 |       0.893 |       0.913 |       0.849 |        0.951 |
| file ∪ class | boosting (ceiling) | structure (28)                        |         338 |   5247 | 0.953 |           0.685 |          0.775 |       0.864 |       0.947 |       0.917 |        0.741 |
| file ∪ class | boosting (ceiling) | structure + invariants (41)           |         338 |   5247 | 0.967 |           0.699 |          0.778 |       0.872 |       0.942 |       0.939 |        0.941 |
| file ∪ class | boosting (ceiling) | size-free (32)                        |         338 |   5247 | 0.968 |           0.681 |          0.713 |       0.905 |       0.943 |       0.967 |        0.980 |
| file ∪ class | boosting (ceiling) | structure + invariants + lower bounds |         338 |   5247 | 0.977 |           0.794 |          0.801 |       0.933 |       0.954 |       0.971 |        0.926 |
| file         | tree (depth 3)     | density + size                        |         338 |   5247 | 0.958 |           0.578 |          0.900 |       0.893 |       0.804 |       0.928 |        0.876 |
| file         | tree (depth 3)     | structure (28)                        |         338 |   5247 | 0.956 |           0.628 |          0.932 |       0.626 |       0.902 |       0.915 |        0.885 |
| file         | tree (depth 3)     | structure + invariants (41)           |         338 |   5247 | 0.966 |           0.643 |          0.933 |       0.758 |       0.921 |       0.918 |        0.878 |
| file         | tree (depth 3)     | size-free (32)                        |         338 |   5247 | 0.966 |           0.613 |          0.932 |       0.915 |       0.914 |       0.927 |        0.905 |
| file         | tree (depth 3)     | structure + invariants + lower bounds |         338 |   5247 | 0.966 |           0.643 |          0.933 |       0.758 |       0.921 |       0.918 |        0.878 |
| file         | EBM                | density + size                        |         338 |   5247 | 0.988 |           0.882 |          0.869 |       0.943 |       0.953 |       0.973 |        0.997 |
| file         | EBM                | structure (28)                        |         338 |   5247 | 0.991 |           0.913 |          0.906 |       0.945 |       0.967 |       0.987 |        1.000 |
| file         | EBM                | structure + invariants (41)           |         338 |   5247 | 0.992 |           0.925 |          0.905 |       0.952 |       0.969 |       0.994 |        0.999 |
| file         | EBM                | size-free (32)                        |         338 |   5247 | 0.992 |           0.916 |          0.891 |       0.956 |       0.968 |       0.992 |        1.000 |
| file         | EBM                | structure + invariants + lower bounds |         338 |   5247 | 0.993 |           0.930 |          0.915 |       0.949 |       0.973 |       0.993 |        0.997 |
| file         | boosting (ceiling) | density + size                        |         338 |   5247 | 0.984 |           0.871 |          0.914 |       0.896 |       0.949 |       0.975 |        0.998 |
| file         | boosting (ceiling) | structure (28)                        |         338 |   5247 | 0.986 |           0.896 |          0.917 |       0.906 |       0.950 |       0.989 |        0.999 |
| file         | boosting (ceiling) | structure + invariants (41)           |         338 |   5247 | 0.990 |           0.918 |          0.908 |       0.941 |       0.958 |       0.996 |        0.995 |
| file         | boosting (ceiling) | size-free (32)                        |         338 |   5247 | 0.989 |           0.907 |          0.912 |       0.935 |       0.957 |       0.992 |        1.000 |
| file         | boosting (ceiling) | structure + invariants + lower bounds |         338 |   5247 | 0.992 |           0.943 |          0.924 |       0.931 |       0.978 |       0.995 |        0.997 |

## The classifier within the (n, m) cells holding both classes

2407 rows in 11 cells, 218 positives; cells: 20×10 (515/13), 20×20 (433/4), 30×10 (478/86), 30×15 (328/35), 30×30 (444/8), 40×20 (91/11), 40×40 (18/6), 50×50 (28/12), 50×100 (20/5), 75×75 (22/17), 100×100 (30/21).

| split        | model              | features                              |   positives |   rows |   auc |   avg precision |   balanced acc |   auc 11-20 |   auc 21-30 |   auc 31-60 |   auc 61-200 |
|:-------------|:-------------------|:--------------------------------------|------------:|-------:|------:|----------------:|---------------:|------------:|------------:|------------:|-------------:|
| file ∪ class | tree (depth 3)     | density + size                        |         218 |   2407 | 0.849 |           0.256 |          0.835 |       0.865 |       0.858 |       0.805 |        0.746 |
| file ∪ class | tree (depth 3)     | structure (28)                        |         218 |   2407 | 0.905 |           0.426 |          0.881 |       0.778 |       0.888 |       0.928 |        0.832 |
| file ∪ class | tree (depth 3)     | structure + invariants (41)           |         218 |   2407 | 0.895 |           0.380 |          0.869 |       0.803 |       0.897 |       0.935 |        0.832 |
| file ∪ class | tree (depth 3)     | size-free (32)                        |         218 |   2407 | 0.931 |           0.517 |          0.823 |       0.894 |       0.902 |       0.956 |        0.964 |
| file ∪ class | tree (depth 3)     | structure + invariants + lower bounds |         218 |   2407 | 0.896 |           0.380 |          0.876 |       0.807 |       0.897 |       0.935 |        0.832 |
| file ∪ class | EBM                | density + size                        |         218 |   2407 | 0.947 |           0.538 |          0.802 |       0.878 |       0.918 |       0.982 |        0.989 |
| file ∪ class | EBM                | structure (28)                        |         218 |   2407 | 0.965 |           0.772 |          0.841 |       0.906 |       0.948 |       0.988 |        0.994 |
| file ∪ class | EBM                | structure + invariants (41)           |         218 |   2407 | 0.969 |           0.802 |          0.847 |       0.919 |       0.956 |       0.990 |        0.998 |
| file ∪ class | EBM                | size-free (32)                        |         218 |   2407 | 0.971 |           0.813 |          0.839 |       0.924 |       0.957 |       0.992 |        1.000 |
| file ∪ class | EBM                | structure + invariants + lower bounds |         218 |   2407 | 0.970 |           0.817 |          0.827 |       0.910 |       0.958 |       0.989 |        0.996 |
| file ∪ class | boosting (ceiling) | density + size                        |         218 |   2407 | 0.935 |           0.636 |          0.819 |       0.777 |       0.906 |       0.989 |        0.994 |
| file ∪ class | boosting (ceiling) | structure (28)                        |         218 |   2407 | 0.947 |           0.714 |          0.834 |       0.812 |       0.921 |       0.989 |        0.998 |
| file ∪ class | boosting (ceiling) | structure + invariants (41)           |         218 |   2407 | 0.956 |           0.771 |          0.845 |       0.858 |       0.936 |       0.992 |        0.998 |
| file ∪ class | boosting (ceiling) | size-free (32)                        |         218 |   2407 | 0.957 |           0.770 |          0.795 |       0.888 |       0.943 |       0.997 |        1.000 |
| file ∪ class | boosting (ceiling) | structure + invariants + lower bounds |         218 |   2407 | 0.962 |           0.802 |          0.840 |       0.891 |       0.945 |       0.987 |        0.996 |
| file         | tree (depth 3)     | density + size                        |         218 |   2407 | 0.891 |           0.393 |          0.840 |       0.698 |       0.857 |       0.845 |        0.799 |
| file         | tree (depth 3)     | structure (28)                        |         218 |   2407 | 0.921 |           0.423 |          0.885 |       0.790 |       0.887 |       0.933 |        0.941 |
| file         | tree (depth 3)     | structure + invariants (41)           |         218 |   2407 | 0.915 |           0.420 |          0.883 |       0.797 |       0.888 |       0.942 |        0.878 |
| file         | tree (depth 3)     | size-free (32)                        |         218 |   2407 | 0.938 |           0.568 |          0.891 |       0.865 |       0.921 |       0.956 |        0.929 |
| file         | tree (depth 3)     | structure + invariants + lower bounds |         218 |   2407 | 0.915 |           0.420 |          0.883 |       0.797 |       0.888 |       0.942 |        0.878 |
| file         | EBM                | density + size                        |         218 |   2407 | 0.968 |           0.792 |          0.812 |       0.884 |       0.957 |       0.981 |        0.987 |
| file         | EBM                | structure (28)                        |         218 |   2407 | 0.973 |           0.829 |          0.839 |       0.914 |       0.963 |       0.990 |        0.994 |
| file         | EBM                | structure + invariants (41)           |         218 |   2407 | 0.976 |           0.845 |          0.859 |       0.918 |       0.969 |       0.991 |        0.994 |
| file         | EBM                | size-free (32)                        |         218 |   2407 | 0.975 |           0.815 |          0.819 |       0.935 |       0.965 |       0.993 |        1.000 |
| file         | EBM                | structure + invariants + lower bounds |         218 |   2407 | 0.978 |           0.847 |          0.861 |       0.925 |       0.970 |       0.991 |        0.992 |
| file         | boosting (ceiling) | density + size                        |         218 |   2407 | 0.950 |           0.769 |          0.875 |       0.769 |       0.946 |       0.982 |        1.000 |
| file         | boosting (ceiling) | structure (28)                        |         218 |   2407 | 0.957 |           0.760 |          0.829 |       0.857 |       0.939 |       0.993 |        0.998 |
| file         | boosting (ceiling) | structure + invariants (41)           |         218 |   2407 | 0.964 |           0.815 |          0.848 |       0.859 |       0.953 |       0.994 |        1.000 |
| file         | boosting (ceiling) | size-free (32)                        |         218 |   2407 | 0.961 |           0.760 |          0.819 |       0.889 |       0.941 |       0.996 |        1.000 |
| file         | boosting (ceiling) | structure + invariants + lower bounds |         218 |   2407 | 0.975 |           0.869 |          0.880 |       0.867 |       0.973 |       0.992 |        0.998 |

## The depth-3 tree (all rows, structure + invariants)

```
|--- rig_edge_prob <= 0.654
|   |--- bw_rcm <= 11.500
|   |   |--- col_mean <= 3.950
|   |   |   |--- class: tight
|   |   |--- col_mean >  3.950
|   |   |   |--- class: gap>=2
|   |--- bw_rcm >  11.500
|   |   |--- n_customers <= 29.500
|   |   |   |--- class: gap>=2
|   |   |--- n_customers >  29.500
|   |   |   |--- class: gap>=2
|--- rig_edge_prob >  0.654
|   |--- g_deg_std <= 3.482
|   |   |--- row_max <= 4.500
|   |   |   |--- class: tight
|   |   |--- row_max >  4.500
|   |   |   |--- class: tight
|   |--- g_deg_std >  3.482
|   |   |--- col_mean <= 7.987
|   |   |   |--- class: tight
|   |   |--- col_mean >  7.987
|   |   |   |--- class: gap>=2
```

## The depth-3 tree within the mixed cells (structure + invariants)

```
|--- rig_edge_prob <= 0.685
|   |--- spectral_radius <= 5.845
|   |   |--- class: tight
|   |--- spectral_radius >  5.845
|   |   |--- g_nodes <= 25.000
|   |   |   |--- class: gap>=2
|   |   |--- g_nodes >  25.000
|   |   |   |--- class: gap>=2
|--- rig_edge_prob >  0.685
|   |--- g_deg_std <= 4.524
|   |   |--- row_mean <= 4.017
|   |   |   |--- class: tight
|   |   |--- row_mean >  4.017
|   |   |   |--- class: tight
|   |--- g_deg_std >  4.524
|   |   |--- row_max <= 10.500
|   |   |   |--- class: gap>=2
|   |   |--- row_max >  10.500
|   |   |   |--- class: tight
```

## The depth-3 tree within the mixed cells (size-free features)

```
|--- rig_edge_prob <= 0.685
|   |--- g_components_frac <= 0.042
|   |   |--- g_deg_cv <= 0.205
|   |   |   |--- class: gap>=2
|   |   |--- g_deg_cv >  0.205
|   |   |   |--- class: gap>=2
|   |--- g_components_frac >  0.042
|   |   |--- g_deg_max_frac <= 0.500
|   |   |   |--- class: tight
|   |   |--- g_deg_max_frac >  0.500
|   |   |   |--- class: gap>=2
|--- rig_edge_prob >  0.685
|   |--- g_deg_min_frac <= 0.397
|   |   |--- g_components_frac <= 0.042
|   |   |   |--- class: gap>=2
|   |   |--- g_components_frac >  0.042
|   |   |   |--- class: tight
|   |--- g_deg_min_frac >  0.397
|   |   |--- rig_edge_prob <= 0.827
|   |   |   |--- class: tight
|   |   |--- rig_edge_prob >  0.827
|   |   |   |--- class: tight
```

## EBM term importances within the mixed cells (structure + invariants)

| term          |   importance |
|:--------------|-------------:|
| g_deg_std     |        0.891 |
| g_clustering  |        0.712 |
| row_mean      |        0.568 |
| density       |        0.523 |
| col_max_frac  |        0.323 |
| col_max       |        0.309 |
| g_density     |        0.299 |
| fiedler_lcc   |        0.278 |
| fiedler       |        0.272 |
| n_customers   |        0.255 |
| rig_edge_prob |        0.245 |
| g_nodes       |        0.230 |

## Each size-free feature alone, z-scored within its (n, m) cell

| feature              |   auc |      d |   cells |   rows |   positives |
|:---------------------|------:|-------:|--------:|-------:|------------:|
| g_clustering         | 0.097 | -1.472 |      11 |   2407 |         218 |
| g_density            | 0.105 | -1.517 |      11 |   2407 |         218 |
| rig_edge_prob        | 0.105 | -1.539 |      11 |   2407 |         218 |
| spectral_radius_frac | 0.105 | -1.495 |      11 |   2407 |         218 |
| g_degeneracy_frac    | 0.114 | -1.500 |      11 |   2407 |         218 |
| g_deg_cv             | 0.879 |  1.476 |      11 |   2407 |         218 |
| density              | 0.122 | -1.334 |      11 |   2407 |         218 |
| row_mean_frac        | 0.122 | -1.334 |      11 |   2407 |         218 |
| col_mean_frac        | 0.122 | -1.334 |      11 |   2407 |         218 |
| fiedler_lcc          | 0.131 | -1.403 |      11 |   2407 |         218 |
| fiedler              | 0.131 | -1.403 |      11 |   2407 |         218 |
| tw_min_fill_frac     | 0.133 | -1.422 |      11 |   2407 |         218 |
| g_deg_min_frac       | 0.134 | -1.393 |      11 |   2407 |         218 |
| tw_min_degree_frac   | 0.136 | -1.411 |      11 |   2407 |         218 |
| g_deg_max_frac       | 0.139 | -1.202 |      11 |   2407 |         218 |
| col_max_frac         | 0.140 | -1.250 |      11 |   2407 |         218 |
| col_min_frac         | 0.157 | -1.195 |      11 |   2407 |         218 |
| bw_rcm_frac          | 0.158 | -1.201 |      11 |   2407 |         218 |
| row_max_frac         | 0.159 | -1.199 |      11 |   2407 |         218 |
| sep_frac             | 0.204 | -1.079 |      11 |   2407 |         218 |
| row_min_frac         | 0.237 | -0.909 |      11 |   2407 |         218 |
| row_cv               | 0.705 |  0.729 |      11 |   2407 |         218 |
| distinct_row_frac    | 0.302 | -0.784 |      11 |   2407 |         218 |
| col_cv               | 0.696 |  0.728 |      11 |   2407 |         218 |
| cc_greedy_frac       | 0.675 |  0.664 |      11 |   2407 |         218 |
| cc_products_frac     | 0.345 | -0.509 |      11 |   2407 |         218 |
| dominated_col_frac   | 0.650 |  0.413 |      11 |   2407 |         218 |
| g_largest_comp_frac  | 0.387 |  0.032 |      11 |   2407 |         218 |
| distinct_col_frac    | 0.399 | -0.064 |      11 |   2407 |         218 |
| g_components_frac    | 0.533 | -0.028 |      11 |   2407 |         218 |
| rig_density_ratio    | 0.505 | -0.091 |      11 |   2407 |         218 |

## The treewidth ceiling: where pathwidth provably exceeds treewidth

| rows     |   instances |   pw > tw certified |   frac |   mean optimum − (tw_min_fill + 1) |   lb_best above ceiling |   lb_trivial above ceiling (must be 0) |   lb_contraction above ceiling (must be 0) |
|:---------|------------:|--------------------:|-------:|-----------------------------------:|------------------------:|---------------------------------------:|-------------------------------------------:|
| tight    |        4909 |                  35 |  0.007 |                             -0.038 |                      35 |                                      0 |                                          0 |
| gap 1    |        1129 |                 315 |  0.279 |                              0.147 |                       1 |                                      0 |                                          0 |
| gap >= 2 |         338 |                 131 |  0.388 |                             -0.450 |                       0 |                                      0 |                                          0 |

## Clusters of the 338 gap >= 2 instances (k = 2 by silhouette)

Silhouette by k: 2 → 0.370, 3 → 0.335, 4 → 0.344, 5 → 0.339, 6 → 0.282.

|   cluster |   instances | n range   | collections                                                                                   |   mean gap |   max gap |   mean optimum/n |   mean density |   mean g_density | extreme features (z)                                                                                       |
|----------:|------------:|:----------|:----------------------------------------------------------------------------------------------|-----------:|----------:|-----------------:|---------------:|-----------------:|:-----------------------------------------------------------------------------------------------------------|
|         0 |         201 | 20-134    | Chu_Stuckey 85, Faggioli_Bentivoglio 83, Harvey 23, Challenge 3, Wilson 3, SCOOP 3, Simonis 1 |      6.259 |        30 |            0.336 |          0.079 |            0.181 | g_deg_max_frac -0.7, spectral_radius_frac -0.7, g_density -0.7, rig_edge_prob -0.7, g_degeneracy_frac -0.7 |
|         1 |         137 | 20-125    | Simonis 72, Harvey 48, Chu_Stuckey 17                                                         |      2.613 |        16 |            0.614 |          0.238 |            0.536 | g_deg_max_frac +1.0, spectral_radius_frac +1.0, g_density +1.0, rig_edge_prob +1.0, g_degeneracy_frac +1.0 |

## The 10 smallest gap >= 2 instances, one per isomorphism class

| instance                                 |   n |   m |   ones | products/customer        | customers/product                 |   simplicial | deg min-max   |   trivial |   clique |   contraction |   expansion |   tw_min_fill+1 |   tw_ub+1 |   bw_rcm+1 |   sep |   components |   optimum | pw > tw   |
|:-----------------------------------------|----:|----:|-------:|:-------------------------|:----------------------------------|-------------:|:--------------|----------:|---------:|--------------:|------------:|----------------:|----------:|-----------:|------:|-------------:|----------:|:----------|
| Warwick 871: balanced orders, 4 orders p |  20 |  10 |     40 | 5×1, 4×3, 3×2, 2×3, 1×11 | 4×10                              |           11 | 3-10          |         4 |        4 |             4 |           4 |               4 |         4 |         10 |     2 |            1 |         6 | True      |
| Warwick 877: balanced orders, 4 orders p |  20 |  10 |     40 | 4×2, 3×4, 2×6, 1×8       | 4×10                              |            8 | 3-12          |         4 |        4 |             6 |           6 |               7 |         7 |         10 |     3 |            1 |         8 | True      |
| Warwick 879: balanced orders, 4 orders p |  20 |  10 |     40 | 4×1, 3×3, 2×11, 1×5      | 4×10                              |            5 | 3-10          |         4 |        4 |             6 |           6 |               7 |         7 |         12 |     4 |            1 |         8 | True      |
| HS problem 590 size 20 10 density  0.20  |  20 |  10 |     43 | 4×1, 3×3, 2×14, 1×2      | 8×1, 7×1, 5×2, 4×2, 3×3, 1×1      |            2 | 4-14          |         8 |        8 |             8 |           8 |              10 |        10 |         14 |     5 |            1 |        10 | False     |
| HS problem 551 size 20 10 density  0.20  |  20 |  10 |     45 | 6×1, 4×2, 3×4, 2×6, 1×7  | 7×1, 6×1, 5×4, 4×2, 3×1, 1×1      |            7 | 3-15          |         7 |        7 |             7 |           7 |               7 |         7 |         14 |     5 |            1 |         9 | True      |
| HS problem 575 size 20 10 density  0.20  |  20 |  10 |     47 | 4×3, 3×5, 2×8, 1×4       | 8×1, 7×1, 6×2, 4×2, 3×4           |            4 | 4-15          |         8 |        8 |             8 |           8 |              10 |         9 |         13 |     5 |            1 |        10 | True      |
| HS problem 640 size 20 10 density  0.25  |  20 |  10 |     49 | 5×1, 4×2, 3×6, 2×7, 1×4  | 8×1, 7×1, 6×1, 5×3, 4×2, 3×1, 2×1 |            4 | 1-17          |         8 |        8 |             9 |           9 |              10 |        10 |         15 |     6 |            1 |        11 | True      |
| HS problem 620 size 20 10 density  0.25  |  20 |  10 |     54 | 5×1, 3×13, 2×4, 1×2      | 9×1, 8×1, 6×1, 5×5, 4×1, 2×1      |            2 | 4-16          |         9 |        9 |            11 |          10 |              12 |        12 |         16 |     6 |            1 |        13 | True      |
| HS problem 678 size 20 10 density  0.30  |  20 |  10 |     54 | 5×1, 4×3, 3×7, 2×7, 1×2  | 7×3, 6×2, 5×2, 4×2, 3×1           |            2 | 3-16          |         7 |        7 |            10 |          10 |              11 |        11 |         15 |     6 |            1 |        12 | True      |
| Warwick 955: balanced products, 3 produc |  20 |  10 |     60 | 3×20                     | 10×1, 7×4, 6×1, 5×2, 4×1, 2×1     |            0 | 10-16         |        10 |       10 |            13 |          13 |              15 |        15 |         18 |     7 |            1 |        15 | False     |

### Re-certification

| instance                                 |   cached |   resolved | refute status   |   refute nodes | agree   |
|:-----------------------------------------|---------:|-----------:|:----------------|---------------:|:--------|
| Warwick 871: balanced orders, 4 orders p |        6 |          6 | unsat           |             41 | True    |
| Warwick 877: balanced orders, 4 orders p |        8 |          8 | unsat           |             59 | True    |
| Warwick 879: balanced orders, 4 orders p |        8 |          8 | unsat           |             48 | True    |
| HS problem 590 size 20 10 density  0.20  |       10 |         10 | unsat           |             33 | True    |
| HS problem 551 size 20 10 density  0.20  |        9 |          9 | unsat           |             35 | True    |
| HS problem 575 size 20 10 density  0.20  |       10 |         10 | unsat           |             23 | True    |
| HS problem 640 size 20 10 density  0.25  |       11 |         11 | unsat           |             43 | True    |
| HS problem 620 size 20 10 density  0.25  |       13 |         13 | unsat           |             25 | True    |
| HS problem 678 size 20 10 density  0.30  |       12 |         12 | unsat           |             27 | True    |
| Warwick 955: balanced products, 3 produc |       15 |         15 | unsat           |             20 | True    |

**Warwick 871: balanced orders, 4 orders per product** — `wbo_20_10.txt`, 20 customers × 10 products, 40 ones; optimum **6**, `lb_best` 4, gap **2**.
Bounds recomputed: trivial 4, clique 4, contraction 4, expansion 4; `tw_min_fill + 1` 4, `bw_rcm + 1` 10, separator 2, Fiedler 0.882.
MOSP graph: 50 edges, 1 component(s), clustering 0.778; degree sequence 10×4, 6×2, 5×3, 3×11. Products per customer 5×1, 4×3, 3×2, 2×3, 1×11; customers per product 4×10; 11 of 20 customers in exactly one product (simplicial). pathwidth 5 > treewidth (≤ 3), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 6 (cached 6), `optimum − 1` unsat in 41 nodes.

```
0 1 0 1 0 1 1 0 1 0
0 0 0 0 0 0 1 0 0 0
0 1 1 1 0 0 0 1 0 0
1 0 0 0 0 0 0 0 0 1
0 0 0 0 0 1 1 0 0 0
0 0 0 0 1 0 0 0 0 0
0 0 1 0 0 0 0 0 0 0
0 0 0 0 0 1 0 1 1 1
1 0 0 0 1 0 0 0 0 0
0 1 0 1 0 0 0 0 1 0
1 0 0 0 1 0 0 0 0 1
0 1 0 0 0 0 0 0 0 0
0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 1 0 0
0 0 0 1 0 0 0 0 0 0
0 0 1 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0
0 0 1 0 1 1 0 0 0 1
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 1 0
```

**Warwick 877: balanced orders, 4 orders per product** — `wbo_20_10.txt`, 20 customers × 10 products, 40 ones; optimum **8**, `lb_best` 6, gap **2**.
Bounds recomputed: trivial 4, clique 4, contraction 6, expansion 6; `tw_min_fill + 1` 7, `bw_rcm + 1` 10, separator 3, Fiedler 0.837.
MOSP graph: 56 edges, 1 component(s), clustering 0.724; degree sequence 12×1, 10×1, 9×2, 8×1, 7×1, 6×4, 5×1, 4×1, 3×8. Products per customer 4×2, 3×4, 2×6, 1×8; customers per product 4×10; 8 of 20 customers in exactly one product (simplicial). pathwidth 7 > treewidth (≤ 6), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 8 (cached 8), `optimum − 1` unsat in 59 nodes.

```
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 1 0 0 0
0 1 1 0 0 0 0 0 1 0
0 0 1 0 0 1 0 0 0 1
0 1 0 0 1 0 1 1 0 0
0 0 0 0 0 0 1 0 0 0
0 0 0 0 0 1 0 0 0 0
0 0 1 0 0 0 0 0 1 0
0 0 0 0 0 0 0 1 0 0
0 0 0 1 0 0 0 0 1 0
0 1 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 1
1 0 0 0 1 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0
1 1 0 1 0 0 0 0 0 0
0 0 0 1 0 1 1 0 0 1
0 0 0 0 0 0 0 1 0 0
0 0 0 0 1 0 0 0 0 1
1 0 0 0 0 0 0 0 1 0
```

**Warwick 879: balanced orders, 4 orders per product** — `wbo_20_10.txt`, 20 customers × 10 products, 40 ones; optimum **8**, `lb_best` 6, gap **2**.
Bounds recomputed: trivial 4, clique 4, contraction 6, expansion 6; `tw_min_fill + 1` 7, `bw_rcm + 1` 12, separator 4, Fiedler 1.274.
MOSP graph: 56 edges, 1 component(s), clustering 0.613; degree sequence 10×1, 9×2, 8×1, 6×6, 5×5, 3×5. Products per customer 4×1, 3×3, 2×11, 1×5; customers per product 4×10; 5 of 20 customers in exactly one product (simplicial). pathwidth 7 > treewidth (≤ 6), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 8 (cached 8), `optimum − 1` unsat in 48 nodes.

```
0 0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 1 1 1
1 0 1 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
0 0 0 1 0 0 0 0 0 1
0 0 0 0 0 1 0 1 0 0
0 0 0 0 1 0 0 0 0 0
0 1 0 0 0 0 1 0 0 0
0 0 0 0 0 0 0 1 1 0
0 0 1 0 0 0 0 0 0 0
1 0 0 1 0 0 1 0 0 0
1 1 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 1 0 1 0
0 0 0 1 0 0 0 0 0 1
1 0 1 0 1 1 0 0 0 0
0 1 0 0 0 1 0 0 0 0
0 0 0 0 0 0 1 0 0 0
0 1 0 0 0 0 0 0 0 1
0 0 0 1 1 0 0 0 0 0
```

**HS problem 590 size 20 10 density  0.20** — `problem_20_10.dat`, 20 customers × 10 products, 43 ones; optimum **10**, `lb_best` 8, gap **2**.
Bounds recomputed: trivial 8, clique 8, contraction 8, expansion 8; `tw_min_fill + 1` 10, `bw_rcm + 1` 14, separator 5, Fiedler 2.372.
MOSP graph: 82 edges, 1 component(s), clustering 0.683; degree sequence 14×1, 12×2, 11×2, 9×3, 8×4, 7×3, 6×2, 4×3. Products per customer 4×1, 3×3, 2×14, 1×2; customers per product 8×1, 7×1, 5×2, 4×2, 3×3, 1×1; 2 of 20 customers in exactly one product (simplicial). pathwidth 9, treewidth ≤ 9: not separated by the heuristic.
Re-certified: `solve_mosp_exact` 10 (cached 10), `optimum − 1` unsat in 33 nodes.

```
1 0 0 0 1 0 0 0 0 0
1 1 0 0 0 0 0 0 0 0
0 1 0 0 0 1 0 0 0 1
1 0 1 0 1 1 0 0 0 0
0 0 1 0 0 0 0 0 1 0
0 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 1 0 1 0
0 1 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 0 1 1
0 1 0 1 0 0 0 0 0 0
0 0 0 0 1 0 0 0 1 0
0 1 0 0 1 0 0 0 1 0
0 1 0 0 0 0 0 0 0 0
0 0 0 1 0 0 0 1 0 0
0 1 0 0 0 1 0 1 0 0
0 0 0 1 0 0 0 0 0 1
0 0 1 0 0 0 0 0 1 0
0 1 0 0 0 1 0 0 0 0
0 0 0 0 0 1 0 1 0 0
0 0 1 0 0 0 0 1 0 0
```

**HS problem 551 size 20 10 density  0.20** — `problem_20_10.dat`, 20 customers × 10 products, 45 ones; optimum **9**, `lb_best` 7, gap **2**.
Bounds recomputed: trivial 7, clique 7, contraction 7, expansion 7; `tw_min_fill + 1` 7, `bw_rcm + 1` 14, separator 5, Fiedler 1.617.
MOSP graph: 73 edges, 1 component(s), clustering 0.742; degree sequence 15×1, 12×1, 10×3, 9×3, 7×4, 6×2, 5×1, 4×2, 3×3. Products per customer 6×1, 4×2, 3×4, 2×6, 1×7; customers per product 7×1, 6×1, 5×4, 4×2, 3×1, 1×1; 7 of 20 customers in exactly one product (simplicial). pathwidth 8 > treewidth (≤ 6), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 9 (cached 9), `optimum − 1` unsat in 35 nodes.

```
0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 1 0
1 0 0 0 1 0 1 0 1 0
1 0 0 1 1 0 1 1 1 0
1 0 0 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
1 0 1 1 0 0 0 0 0 0
0 0 1 0 0 1 0 0 0 0
0 0 0 0 0 1 1 0 0 1
0 0 0 0 1 0 0 0 1 1
0 0 0 0 0 0 0 1 0 0
0 0 1 0 0 0 0 1 0 0
0 0 0 0 0 1 0 0 0 0
0 0 0 0 0 0 0 1 0 0
1 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 1 0 0 0
0 0 0 0 1 0 0 0 0 0
0 0 0 0 1 0 0 0 1 0
1 0 0 1 0 1 1 0 0 0
0 1 1 0 0 1 0 0 0 0
```

**HS problem 575 size 20 10 density  0.20** — `problem_20_10.dat`, 20 customers × 10 products, 47 ones; optimum **10**, `lb_best` 8, gap **2**.
Bounds recomputed: trivial 8, clique 8, contraction 8, expansion 8; `tw_min_fill + 1` 10, `bw_rcm + 1` 13, separator 5, Fiedler 2.497.
MOSP graph: 88 edges, 1 component(s), clustering 0.729; degree sequence 15×1, 14×1, 13×1, 12×1, 11×2, 10×1, 9×3, 8×3, 7×2, 6×1, 5×3, 4×1. Products per customer 4×3, 3×5, 2×8, 1×4; customers per product 8×1, 7×1, 6×2, 4×2, 3×4; 4 of 20 customers in exactly one product (simplicial). pathwidth 9 > treewidth (≤ 8), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 10 (cached 10), `optimum − 1` unsat in 23 nodes.

```
0 0 0 0 0 0 0 0 0 1
1 0 0 0 1 0 1 0 0 1
0 1 0 1 1 0 0 1 0 0
0 1 0 0 0 1 0 0 0 1
0 0 0 0 0 1 0 0 0 1
1 0 0 0 0 0 0 0 0 1
0 1 0 1 0 0 0 0 1 0
0 0 0 0 1 0 0 0 0 1
0 0 0 0 0 1 0 1 0 0
0 0 1 0 0 0 0 0 0 0
1 0 1 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0 0 0
0 0 1 0 0 0 1 0 1 0
1 0 1 0 0 0 0 0 0 1
0 1 0 0 0 0 0 0 0 1
0 0 1 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0
0 1 0 1 0 0 0 0 0 0
1 0 0 0 0 0 1 0 1 0
1 1 0 0 0 1 0 1 0 0
```

**HS problem 640 size 20 10 density  0.25** — `problem_20_10.dat`, 20 customers × 10 products, 49 ones; optimum **11**, `lb_best` 9, gap **2**.
Bounds recomputed: trivial 8, clique 8, contraction 9, expansion 9; `tw_min_fill + 1` 10, `bw_rcm + 1` 15, separator 6, Fiedler 0.991.
MOSP graph: 93 edges, 1 component(s), clustering 0.692; degree sequence 17×1, 13×3, 12×1, 11×1, 10×6, 9×2, 7×2, 6×1, 4×2, 1×1. Products per customer 5×1, 4×2, 3×6, 2×7, 1×4; customers per product 8×1, 7×1, 6×1, 5×3, 4×2, 3×1, 2×1; 4 of 20 customers in exactly one product (simplicial). pathwidth 10 > treewidth (≤ 9), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 11 (cached 11), `optimum − 1` unsat in 43 nodes.

```
0 0 0 0 1 0 0 1 0 1
1 0 0 0 0 0 0 0 0 0
1 0 0 1 1 0 1 0 0 0
0 0 0 1 0 0 0 0 0 0
0 0 1 1 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0 0
0 0 0 0 0 1 1 0 0 1
1 0 0 1 1 1 0 0 0 0
0 0 1 0 0 1 0 0 0 0
0 0 1 0 0 0 1 0 0 0
0 0 1 0 0 0 0 0 1 0
0 0 1 0 0 0 0 0 0 0
1 0 0 0 1 1 0 0 0 0
1 0 1 0 0 0 0 0 0 1
0 0 1 0 0 0 0 0 1 1
0 1 0 0 0 0 0 0 0 0
0 1 1 0 1 0 1 0 1 0
0 0 0 0 1 0 0 0 1 0
0 0 0 0 1 0 0 1 1 0
0 0 0 0 0 0 0 1 1 0
```

**HS problem 620 size 20 10 density  0.25** — `problem_20_10.dat`, 20 customers × 10 products, 54 ones; optimum **13**, `lb_best` 11, gap **2**.
Bounds recomputed: trivial 9, clique 9, contraction 11, expansion 10; `tw_min_fill + 1` 12, `bw_rcm + 1` 16, separator 6, Fiedler 3.647.
MOSP graph: 112 edges, 1 component(s), clustering 0.729; degree sequence 16×1, 15×1, 14×2, 13×5, 11×6, 8×2, 7×2, 4×1. Products per customer 5×1, 3×13, 2×4, 1×2; customers per product 9×1, 8×1, 6×1, 5×5, 4×1, 2×1; 2 of 20 customers in exactly one product (simplicial). pathwidth 12 > treewidth (≤ 11), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 13 (cached 13), `optimum − 1` unsat in 25 nodes.

```
0 0 0 0 1 0 0 1 0 0
0 0 0 0 0 1 0 1 0 1
0 1 0 0 0 1 0 1 0 0
1 0 0 0 0 1 1 1 1 0
0 0 1 0 0 0 0 1 0 1
0 0 0 0 0 1 1 0 0 0
0 1 1 0 0 0 0 1 0 0
0 1 0 1 0 0 1 0 0 0
1 0 0 0 1 0 0 0 1 0
0 1 0 0 0 0 0 1 0 0
0 0 1 0 1 1 0 0 0 0
0 1 0 0 0 0 0 0 0 0
0 1 0 1 0 0 0 0 1 0
0 0 0 0 0 0 1 1 1 0
0 0 0 0 0 0 0 0 0 1
0 0 0 0 1 0 1 1 0 0
0 0 1 0 1 0 1 0 0 0
0 1 0 1 0 0 0 0 0 1
0 0 1 1 0 0 0 0 0 0
0 1 0 1 0 0 0 0 0 1
```

**HS problem 678 size 20 10 density  0.30** — `problem_20_10.dat`, 20 customers × 10 products, 54 ones; optimum **12**, `lb_best` 10, gap **2**.
Bounds recomputed: trivial 7, clique 7, contraction 10, expansion 10; `tw_min_fill + 1` 11, `bw_rcm + 1` 15, separator 6, Fiedler 2.717.
MOSP graph: 104 edges, 1 component(s), clustering 0.717; degree sequence 16×2, 14×1, 13×3, 12×3, 11×2, 9×2, 8×3, 7×2, 6×1, 3×1. Products per customer 5×1, 4×3, 3×7, 2×7, 1×2; customers per product 7×3, 6×2, 5×2, 4×2, 3×1; 2 of 20 customers in exactly one product (simplicial). pathwidth 11 > treewidth (≤ 10), so no treewidth bound reaches the optimum.
Re-certified: `solve_mosp_exact` 12 (cached 12), `optimum − 1` unsat in 27 nodes.

```
1 0 0 0 1 0 0 0 1 0
1 0 0 0 0 0 0 1 0 1
0 1 1 0 0 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0
1 0 0 0 1 0 1 0 0 0
0 0 1 1 0 0 1 0 0 1
0 1 0 0 0 0 0 1 1 0
0 0 0 1 0 0 0 0 1 1
1 1 0 1 0 0 0 0 1 0
0 0 0 0 0 0 0 0 1 0
0 0 0 1 0 0 0 1 0 0
0 1 0 1 1 0 0 0 0 0
0 1 0 1 1 1 0 0 1 0
0 0 0 0 1 1 0 0 0 0
0 0 1 0 0 0 0 0 1 0
0 1 0 0 0 0 0 1 0 0
0 0 0 0 1 0 1 0 0 0
1 0 0 0 0 0 1 1 0 1
1 1 0 0 0 1 0 0 0 0
1 0 0 0 0 0 0 0 0 1
```

**Warwick 955: balanced products, 3 products per order** — `wbp_20_10.txt`, 20 customers × 10 products, 60 ones; optimum **15**, `lb_best` 13, gap **2**.
Bounds recomputed: trivial 10, clique 10, contraction 13, expansion 13; `tw_min_fill + 1` 15, `bw_rcm + 1` 18, separator 7, Fiedler 8.108.
MOSP graph: 132 edges, 1 component(s), clustering 0.720; degree sequence 16×2, 15×3, 14×5, 13×3, 12×2, 11×4, 10×1. Products per customer 3×20; customers per product 10×1, 7×4, 6×1, 5×2, 4×1, 2×1; 0 of 20 customers in exactly one product (simplicial). pathwidth 14, treewidth ≤ 14: not separated by the heuristic.
Re-certified: `solve_mosp_exact` 15 (cached 15), `optimum − 1` unsat in 20 nodes.

```
0 1 0 1 0 0 0 0 0 1
0 0 1 0 0 1 0 0 0 1
1 1 0 0 0 0 0 1 0 0
0 0 1 0 0 1 1 0 0 0
0 1 1 0 0 1 0 0 0 0
0 0 0 0 1 1 0 1 0 0
0 0 0 0 0 0 0 1 1 1
0 1 0 1 0 0 0 0 1 0
0 0 0 1 1 0 0 1 0 0
0 0 0 0 1 1 0 0 0 1
0 1 1 0 0 0 0 0 1 0
0 0 1 1 0 1 0 0 0 0
0 1 0 0 0 0 1 0 1 0
0 0 0 0 0 0 1 1 1 0
1 0 1 0 0 0 0 0 0 1
0 1 0 1 1 0 0 0 0 0
0 0 0 0 0 1 1 0 1 0
0 1 1 0 0 0 0 0 0 1
0 1 0 1 0 0 0 0 1 0
0 1 0 1 0 0 1 0 0 0
```

_122 s; learning/data/bound_gap.csv written._
