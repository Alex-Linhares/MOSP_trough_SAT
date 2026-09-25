# Node counts: instrumentation check and first look

*Regenerated 2026-09-25 19:32 by `python -m learning.node_counts --max-customers 40`; 6135 instances, 1 s, 16 workers, 10 s deadline per call.*

### The compute ledger: rows per driver, and rows carrying a node count

| driver      |   rows |   with_nodes |
|:------------|-------:|-------------:|
| csearch     |    174 |            0 |
| reheuristic |    105 |            0 |
| TOTAL       |    279 |            0 |

### Status of the decision call at optimum - 1 (a `sat` would be a wrong stored optimum)

| config   | status   |   instances |
|:---------|:---------|------------:|
| csearch  | unsat    |        6135 |
| default  | unsat    |        6135 |

### Nodes to refute optimum - 1, by size band

| config   | band   |   instances |   unsat |   min |   median |    p90 |   max |   seconds_total |
|:---------|:-------|------------:|--------:|------:|---------:|-------:|------:|----------------:|
| default  | 0-10   |        1614 |    1614 |     0 |        0 |    4   |    15 |            0.19 |
| csearch  | 0-10   |        1614 |    1614 |     0 |        0 |    4   |    13 |            0.16 |
| default  | 11-20  |        2508 |    2508 |     0 |        2 |   23   |    90 |            0.29 |
| csearch  | 11-20  |        2508 |    2508 |     0 |        1 |   19   |    79 |            0.27 |
| default  | 21-30  |        1816 |    1816 |     0 |        7 |  108.5 |  1149 |            0.36 |
| csearch  | 21-30  |        1816 |    1816 |     0 |        7 |   88.5 |   945 |            0.36 |
| default  | 31-40  |         197 |     197 |     0 |       38 | 1763.8 | 29138 |            0.2  |
| csearch  | 31-40  |         197 |     197 |     0 |       34 | 1406.6 | 21745 |            0.17 |

### Nodes to refute optimum - 1, by collection

| config   | collection             |   instances |   unsat |   min |   median |    p90 |   max |   seconds_total |
|:---------|:-----------------------|------------:|--------:|------:|---------:|-------:|------:|----------------:|
| csearch  | ChallengeInstances2005 |        5795 |    5795 |     0 |      1   |   27   |   716 |            0.75 |
| csearch  | MOSP_Instances         |         340 |     340 |     0 |     34.5 |  877.1 | 21745 |            0.2  |
| default  | ChallengeInstances2005 |        5795 |    5795 |     0 |      1   |   31   |   976 |            0.8  |
| default  | MOSP_Instances         |         340 |     340 |     0 |     39.5 | 1152.2 | 29138 |            0.24 |

### csearch configuration against decide defaults, nodes per instance

|   instances |   csearch_fewer |   equal |   csearch_more |   median_ratio |   max_ratio |   min_ratio |
|------------:|----------------:|--------:|---------------:|---------------:|------------:|------------:|
|        6135 |            1302 |    4827 |              6 |          0.867 |         1.1 |           0 |

