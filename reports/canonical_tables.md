### corpus

|   instances |   classes: identical matrix |   redundant: identical matrix |   classes: isomorphic matrix |   redundant: isomorphic matrix |   classes: isomorphic MOSP graph |   redundant: isomorphic MOSP graph |   classes: WL hash (not complete) |   redundant: WL hash (not complete) |
|------------:|----------------------------:|------------------------------:|-----------------------------:|-------------------------------:|---------------------------------:|-----------------------------------:|----------------------------------:|------------------------------------:|
|        6376 |                        6332 |                            44 |                         6313 |                             63 |                             3667 |                               2709 |                              3653 |                                2723 |

### per collection

| collection                          |   instances |   classes: identical matrix |   classes: isomorphic matrix |   classes: isomorphic MOSP graph |   classes: WL hash (not complete) |
|:------------------------------------|------------:|----------------------------:|-----------------------------:|---------------------------------:|----------------------------------:|
| ChallengeInstances2005/Harvey       |        2130 |                        2130 |                         2111 |                             1398 |                              1384 |
| ChallengeInstances2005/Miller       |           1 |                           1 |                            1 |                                1 |                                 1 |
| ChallengeInstances2005/Shaw         |          25 |                          25 |                           25 |                               25 |                                25 |
| ChallengeInstances2005/Simonis      |        3630 |                        3630 |                         3630 |                             1784 |                              1784 |
| ChallengeInstances2005/Wilson       |          20 |                          20 |                           20 |                               20 |                                20 |
| MOSP_Instances/Challenge            |          46 |                          46 |                           46 |                               46 |                                46 |
| MOSP_Instances/Chu_Stuckey          |         200 |                         200 |                          200 |                              200 |                               200 |
| MOSP_Instances/Faggioli_Bentivoglio |         300 |                         300 |                          300 |                              287 |                               287 |
| MOSP_Instances/SCOOP                |          24 |                          24 |                           24 |                               24 |                                24 |

### per (n_customers, n_patterns) (sizes with >= 20 instances)

|   n_customers |   n_patterns |   instances |   classes: identical matrix |   classes: isomorphic matrix |   classes: isomorphic MOSP graph |   classes: WL hash (not complete) |
|--------------:|-------------:|------------:|----------------------------:|-----------------------------:|---------------------------------:|----------------------------------:|
|            10 |           10 |         670 |                         670 |                          664 |                              317 |                               315 |
|            10 |           20 |         714 |                         712 |                          712 |                              225 |                               225 |
|            10 |           30 |         190 |                         190 |                          190 |                               68 |                                68 |
|            15 |           15 |         730 |                         730 |                          724 |                              377 |                               375 |
|            15 |           30 |         460 |                         460 |                          460 |                              169 |                               169 |
|            20 |           10 |         710 |                         710 |                          710 |                              516 |                               516 |
|            20 |           20 |         540 |                         515 |                          511 |                              307 |                               302 |
|            30 |           10 |         740 |                         740 |                          740 |                              589 |                               589 |
|            30 |           15 |         470 |                         470 |                          470 |                              366 |                               366 |
|            30 |           30 |         555 |                         555 |                          552 |                              335 |                               330 |
|            40 |           20 |         120 |                         120 |                          120 |                               73 |                                73 |
|            40 |           40 |          25 |                          25 |                           25 |                               25 |                                25 |
|            50 |           50 |          35 |                          30 |                           30 |                               30 |                                30 |
|            50 |          100 |          25 |                          25 |                           25 |                               25 |                                25 |
|            75 |           75 |          27 |                          26 |                           26 |                               26 |                                26 |
|           100 |           50 |          25 |                          25 |                           25 |                               25 |                                25 |
|           100 |          100 |          35 |                          30 |                           30 |                               30 |                                30 |
|           125 |          125 |          25 |                          25 |                           25 |                               25 |                                25 |

### per size band

| size_band   |   instances |   classes: identical matrix |   classes: isomorphic matrix |   classes: isomorphic MOSP graph |   classes: WL hash (not complete) |
|:------------|------------:|----------------------------:|-----------------------------:|---------------------------------:|----------------------------------:|
| n <= 30     |        5938 |                        5905 |                         5886 |                             3287 |                              3273 |
| n > 30      |         438 |                         427 |                          427 |                              380 |                               380 |

### trivial instances

|   complete MOSP graph | share of corpus   |   optimum == n_customers |   in Harvey |   in Simonis |   elsewhere |
|----------------------:|:------------------|-------------------------:|------------:|-------------:|------------:|
|                  1669 | 26.2%             |                     1669 |         457 |         1212 |           0 |

### largest MOSP-graph classes

|   instances |   n_customers | n_patterns   |   g_edges |   optimum |   files | collections      |
|------------:|--------------:|:-------------|----------:|----------:|--------:|:-----------------|
|         643 |            10 | 10/20/30     |        45 |        10 |      11 | Harvey + Simonis |
|         447 |            15 | 15/30        |       105 |        15 |       7 | Harvey + Simonis |
|         287 |            30 | 10/15/30     |       435 |        30 |      10 | Harvey + Simonis |
|         250 |            20 | 10/20        |       190 |        20 |       7 | Harvey + Simonis |
|         108 |            10 | 10/20/30     |        44 |         9 |      10 | Harvey + Simonis |
|          86 |            30 | 10/15/30     |       434 |        29 |      10 | Harvey + Simonis |
|          76 |            20 | 10/20        |       189 |        19 |       7 | Harvey + Simonis |
|          72 |            15 | 15/30        |       104 |        14 |       8 | Harvey + Simonis |
|          45 |            10 | 10/20/30     |        43 |         9 |       8 | Harvey + Simonis |
|          42 |            40 | 20           |       780 |        40 |       1 | Simonis          |

### class sizes

|   classes |   singletons |   classes of size >= 10 |   instances in them |   classes spanning > 1 file |
|----------:|-------------:|------------------------:|--------------------:|----------------------------:|
|      3667 |         3464 |                      26 |                2364 |                         157 |

### classes shared across collections

| collections                                              |   classes |   instances |
|:---------------------------------------------------------|----------:|------------:|
| ChallengeInstances2005/Miller + MOSP_Instances/Challenge |         1 |           2 |
| ChallengeInstances2005/Shaw + MOSP_Instances/Challenge   |        25 |          50 |
| ChallengeInstances2005/Wilson + MOSP_Instances/Challenge |        18 |          36 |

### graph classes with several matrix classes

|   graph classes |   with >1 matrix class |   matrix classes inside them |
|----------------:|-----------------------:|-----------------------------:|
|            3667 |                    150 |                         2796 |

### WL against nauty

|   WL classes |   nauty classes |   WL classes merging >1 nauty class |   nauty classes hidden by WL |
|-------------:|----------------:|------------------------------------:|-----------------------------:|
|         3653 |            3667 |                                   5 |                           14 |

### audit

All classes by `graph_cert` carry one optimum: zero disagreements over 6376 instances.
