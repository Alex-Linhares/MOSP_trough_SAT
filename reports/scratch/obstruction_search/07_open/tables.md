## Item 07 tables (pathwidth units: a dataset class's width is a pathwidth)

### (a) The 24 open classes: record, E ceiling, M floor, B floor, theorem, best new floor

| id        | names                                                      |   n |    m |   width |   lower |   e_ceiling_pw | m_floor_pw   | m_ladder_pw   | m_minor_vertices   | b_floor_pw   | b_potential   | theorem_pw   |   best_new_floor_pw | best_family   | above_record   | closed   |
|:----------|:-----------------------------------------------------------|----:|-----:|--------:|--------:|---------------:|:-------------|:--------------|:-------------------|:-------------|:--------------|:-------------|--------------------:|:--------------|:---------------|:---------|
| pwc-15933 | BalancedTree_3_5                                           | 364 |  363 |       5 |       4 |              4 |              |               |                    |              |               | 5            |                   5 | theorem       | True           | True     |
| pwc-16471 | contiki_shell-netperf_process_thread_shell_netperf_process | 666 |  739 |       7 |       6 |              5 | 6            | 6             | 200                | 3            | 3             |              |                   6 | M             | False          | False    |
| pwc-17043 | fuzix_vfscanf_vfscanf                                      | 587 |  668 |       8 |       2 |              6 | 7            | 7             | 176                | 3            | 3             |              |                   7 | M             | True           | False    |
| pwc-17257 | ex009.gr.xz                                                | 466 |  662 |       9 |       8 |              7 | 8            | 8             | 140                | 3            | 3             |              |                   8 | M             | False          | False    |
| pwc-17617 | FLA_14.gr.xz                                               | 266 |  423 |      10 |       9 |              5 | 9            | 9             | 101                | 5            | 6             |              |                   9 | M             | False          | False    |
| pwc-17632 | NY_13.gr.xz                                                | 283 |  448 |      10 |       9 |              8 | 10           | 9             | 85                 | 2            | 3             |              |                  10 | M             | True           | True     |
| pwc-17286 | ex040.gr.xz                                                | 285 |  526 |      10 |       9 |              8 | 9            | 9             | 86                 | 2            | 3             |              |                   9 | M             | False          | False    |
| pwc-17381 | ex139.gr.xz                                                | 334 |  568 |      10 |       9 |              7 | 9            | 9             | 100                | 4            | 4             |              |                   9 | M             | False          | False    |
| pwc-17342 | ex098.gr.xz                                                | 342 |  588 |      10 |       9 |              7 | 9            | 9             | 103                | 3            | 4             |              |                   9 | M             | False          | False    |
| pwc-04526 | bcspwr05                                                   | 443 |  590 |      10 |       3 |              8 | 9            | 9             | 133                | 3            | 4             |              |                   9 | M             | True           | False    |
| pwc-17359 | ex116.gr.xz                                                | 453 |  742 |      10 |       9 |              8 | 9            | 9             | 136                | 2            | 3             |              |                   9 | M             | False          | False    |
| pwc-17337 | ex093.gr.xz                                                | 454 |  664 |      10 |       9 |              7 | 9            | 9             | 168                | 3            | 3             |              |                   9 | M             | False          | False    |
| pwc-04517 | 494_bus                                                    | 494 |  586 |      10 |       2 |              7 | 8            | 8             | 148                | 3            | 5             |              |                   8 | M             | True           | False    |
| pwc-17343 | ex099.gr.xz                                                | 616 |  923 |      10 |       9 |              7 | 9            | 9             | 240                | 3            | 4             |              |                   9 | M             | False          | False    |
| pwc-17317 | ex073.gr.xz                                                | 712 | 1085 |      10 |       3 |              8 | 9            | 9             | 214                | 3            | 4             |              |                   9 | M             | True           | False    |
| pwc-17436 | ex195.gr.xz                                                | 216 |  382 |      11 |      10 |              9 | 10           | 10            | 65                 | 3            | 3             |              |                  10 | M             | False          | False    |
| pwc-17321 | ex077.gr.xz                                                | 237 |  423 |      11 |      10 |              8 | 10           | 10            | 71                 | 3            | 3             |              |                  10 | M             | False          | False    |
| pwc-17300 | ex054.gr.xz                                                | 243 |  428 |      11 |      10 |              9 | 10           | 10            | 73                 | 3            | 4             |              |                  10 | M             | False          | False    |
| pwc-17306 | ex060.gr.xz                                                | 249 |  434 |      11 |      10 |              8 | 10           | 10            | 75                 | 3            | 3             |              |                  10 | M             | False          | False    |
| pwc-17398 | ex157.gr.xz                                                | 260 |  467 |      11 |      10 |              7 | 10           | 10            | 78                 | 3            | 3             |              |                  10 | M             | False          | False    |
| pwc-17357 | ex114.gr.xz                                                | 268 |  456 |      11 |      10 |              9 | 10           | 10            | 80                 | 3            | 3             |              |                  10 | M             | False          | False    |
| pwc-17288 | ex042.gr.xz                                                | 278 |  522 |      11 |      10 |              8 | 10           | 10            | 83                 | 3            | 3             |              |                  10 | M             | False          | False    |
| pwc-17427 | ex186.gr.xz                                                | 316 |  563 |      11 |      10 |              9 | 10           | 10            | 95                 | 4            | 4             |              |                  10 | M             | False          | False    |
| pwc-17264 | ex017.gr.xz                                                | 330 |  571 |      11 |      10 |              9 | 10           | 10            | 99                 | 3            | 4             |              |                  10 | M             | False          | False    |


### (b) Counts

- classes: 24; closed by this item: 2 (pwc-15933, pwc-17632)
- new floor above the recorded floor: 6; above the recorded width: 0 (must be 0)
- E ceiling below the recorded width (Harper cannot close the class under any computation): 24 of 24 with a ceiling
- M floor = width − 1: 21; M floor above the recorded floor: 5; search above the ladder: 1
- B with a linked triple: 23; B above the recorded floor: 2
- evidence rows written: 2 (results_obstruction.csv); non-closing floors: 4 (lower_bounds.csv)

### (c) Checker

| id        | kind   | verdict   |   pathwidth_proved | c_status   | rulefree                                   |   nodes_checked |   c_reruns |   seconds |
|:----------|:-------|:----------|-------------------:|:-----------|:-------------------------------------------|----------------:|-----------:|----------:|
| pwc-04517 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100.1  |
| pwc-04517 | minor  | verified  |                  8 | refutation | skipped                                    |             nan |        nan |      1    |
| pwc-04526 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100.1  |
| pwc-04526 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0.3  |
| pwc-15933 | branch | verified  |                  5 | nan        | not needed (branch and trivial nodes only) |             364 |          0 |      0.03 |
| pwc-16471 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100.1  |
| pwc-16471 | minor  | verified  |                  6 | refutation | skipped                                    |             nan |        nan |      0.1  |
| pwc-17043 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |      0    |
| pwc-17043 | minor  | verified  |                  7 | refutation | skipped                                    |             nan |        nan |      0.6  |
| pwc-17257 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100.1  |
| pwc-17257 | minor  | verified  |                  8 | refutation | skipped                                    |             nan |        nan |      0    |
| pwc-17264 | branch | verified  |                  3 | nan        | nan                                        |               7 |          4 |    100    |
| pwc-17264 | minor  | verified  |                 10 | refutation | skipped                                    |             nan |        nan |      0.1  |
| pwc-17286 | branch | verified  |                  2 | nan        | nan                                        |               7 |          0 |      0    |
| pwc-17286 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0    |
| pwc-17288 | branch | verified  |                  3 | nan        | nan                                        |               7 |          3 |    100    |
| pwc-17288 | minor  | verified  |                 10 | refutation | skipped                                    |             nan |        nan |      0    |
| pwc-17300 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17300 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.2  |
| pwc-17306 | branch | verified  |                  3 | nan        | nan                                        |               7 |          1 |      0    |
| pwc-17306 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.4  |
| pwc-17317 | branch | verified  |                  3 | nan        | nan                                        |               4 |          1 |      0    |
| pwc-17317 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0.5  |
| pwc-17321 | branch | verified  |                  3 | nan        | nan                                        |               7 |          4 |    100    |
| pwc-17321 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.2  |
| pwc-17337 | branch | verified  |                  3 | nan        | nan                                        |               4 |          2 |    100.1  |
| pwc-17337 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      1.2  |
| pwc-17342 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17342 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0    |
| pwc-17343 | branch | verified  |                  3 | nan        | nan                                        |               4 |          1 |      0    |
| pwc-17343 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0.8  |
| pwc-17357 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17357 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.4  |
| pwc-17359 | branch | verified  |                  2 | nan        | nan                                        |               4 |          0 |      0    |
| pwc-17359 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0.2  |
| pwc-17381 | branch | verified  |                  4 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17381 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0    |
| pwc-17398 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17398 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.3  |
| pwc-17427 | branch | verified  |                  4 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17427 | minor  | verified  |                 10 | refutation | skipped                                    |             nan |        nan |      0    |
| pwc-17436 | branch | verified  |                  3 | nan        | nan                                        |               4 |          3 |    100    |
| pwc-17436 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.2  |
| pwc-17617 | branch | verified  |                  5 | nan        | nan                                        |               4 |          3 |      4.8  |
| pwc-17617 | minor  | verified  |                  9 | refutation | skipped                                    |             nan |        nan |      0.2  |
| pwc-17632 | branch | verified  |                  2 | nan        | nan                                        |               4 |          0 |      0    |
| pwc-17632 | minor  | verified  |                 10 | refutation | verified                                   |             nan |        nan |      0.1  |

