# loop0007 item 08: pathwidth benchmarks, repaired rules against the old results

Regenerate: `python paper2/solver_fix_bench.py compare` (after `run`).

| set | graphs | proved old | proved new | both | same width | width differs | new only | old only |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| coloring | 58 | 31 | 31 | 31 | 31 | 0 | 0 | 0 |
| named | 150 | 125 | 125 | 125 | 125 | 0 | 0 | 0 |
| vsplib-grids | 50 | 9 | 9 | 9 | 9 | 0 | 0 | 0 |
| vsplib-hb | 73 | 39 | 39 | 39 | 39 | 0 | 0 | 0 |
| vsplib-tree | 50 | 50 | 50 | 50 | 50 | 0 | 0 | 0 |
| rome | 11,534 | 11,183 | 11,194 | 11,170 | 11,170 | 0 | 24 | 13 |
| **all** | **11,915** | **11,437** | **11,448** | **11,424** | **11,424** | **0** | **24** | **13** |

Findings (any row here is a changed width or a contradiction):

- none

VSPLIB trees: 50 of 50 proved, 50 at the width the name encodes.

Proved on one side only (a cap effect, not a width change):

| set | graph | n | old | old s | new | new s |
|---|---|---:|---|---:|---|---:|
| rome | grafo10154.94 | 94 | 10 ub | 600.014 | 10 refutation | 533.617 |
| rome | grafo10266.94 | 94 | 11 ub | 600.059 | 11 refutation | 588.48 |
| rome | grafo10322.97 | 97 | 10 ub | 600.02 | 10 refutation | 598.989 |
| rome | grafo10331.100 | 100 | 9 ub | 600.027 | 9 refutation | 452.656 |
| rome | grafo10332.94 | 94 | 10 ub | 600.024 | 10 refutation | 482.214 |
| rome | grafo10351.97 | 97 | 10 ub | 600.021 | 10 refutation | 394.515 |
| rome | grafo10382.94 | 94 | 11 ub | 600.023 | 11 refutation | 566.824 |
| rome | grafo10385.94 | 94 | 10 ub | 600.023 | 10 refutation | 429.93 |
| rome | grafo10445.94 | 94 | 12 ub | 600.015 | 12 refutation | 562.679 |
| rome | grafo10741.92 | 92 | 10 ub | 600.029 | 10 refutation | 449.191 |
| rome | grafo10750.100 | 100 | 10 ub | 600.011 | 10 refutation | 590.772 |
| rome | grafo10809.99 | 99 | 9 ub | 600.014 | 9 refutation | 361.171 |
| rome | grafo10810.97 | 97 | 11 ub | 600.014 | 11 refutation | 531.853 |
| rome | grafo10865.100 | 100 | 10 ub | 600.013 | 10 refutation | 573.013 |
| rome | grafo10984.98 | 98 | 9 ub | 600.026 | 9 refutation | 425.381 |
| rome | grafo11017.97 | 97 | 9 ub | 600.023 | 9 refutation | 589.3 |
| rome | grafo11109.94 | 94 | 10 ub | 600.023 | 10 refutation | 542.402 |
| rome | grafo11187.98 | 98 | 9 ub | 600.023 | 9 refutation | 550.92 |
| rome | grafo11198.98 | 98 | 10 ub | 600.027 | 10 refutation | 599.234 |
| rome | grafo11297.93 | 93 | 9 ub | 600.011 | 9 refutation | 515.06 |
| rome | grafo11380.97 | 97 | 10 ub | 600.014 | 10 refutation | 515.28 |
| rome | grafo8720.100 | 100 | 9 ub | 600.01 | 9 refutation | 437.092 |
| rome | grafo8904.92 | 92 | 9 ub | 600.012 | 9 refutation | 582.258 |
| rome | grafo8905.100 | 100 | 8 ub | 600.011 | 8 refutation | 429.939 |
| rome | grafo10104.96 | 96 | 10 refutation | 543.714 | 10 ub | 600.036 |
| rome | grafo10153.100 | 100 | 9 refutation | 560.145 | 9 ub | 600.008 |
| rome | grafo10489.95 | 95 | 10 refutation | 346.669 | 10 ub | 600.012 |
| rome | grafo10527.93 | 93 | 11 refutation | 504.0 | 11 ub | 600.011 |
| rome | grafo10600.93 | 93 | 10 refutation | 523.591 | 10 ub | 600.011 |
| rome | grafo10663.99 | 99 | 10 refutation | 424.627 | 10 ub | 600.008 |
| rome | grafo11470.91 | 91 | 11 refutation | 532.127 | 11 ub | 600.013 |
| rome | grafo11502.100 | 100 | 8 refutation | 597.261 | 8 ub | 600.013 |
| rome | grafo11647.90 | 90 | 11 refutation | 575.574 | 11 ub | 600.011 |
| rome | grafo7587.95 | 95 | 9 refutation | 554.312 | 9 ub | 600.012 |
| rome | grafo8036.94 | 94 | 10 refutation | 555.048 | 10 ub | 600.011 |
| rome | grafo8585.91 | 91 | 10 refutation | 536.958 | 10 ub | 600.01 |
| rome | grafo8647.91 | 91 | 11 refutation | 396.105 | 11 ub | 600.008 |

Nodes where both sides proved by refutation (sum new / sum old; median and worst pair ratio):

| set | pairs | nodes old | nodes new | ratio | median | max | min |
|---|---:|---:|---:|---:|---:|---:|---:|
| coloring | 18 | 441,082,074 | 443,248,634 | 1.0049 | 1.0000 | 1.023 | 1.000 |
| named | 102 | 342,295,019 | 343,456,465 | 1.0034 | 1.0000 | 1.016 | 1.000 |
| vsplib-grids | 9 | 42,139,983 | 42,842,268 | 1.0167 | 1.0002 | 1.018 | 1.000 |
| vsplib-hb | 32 | 18,565,257 | 18,788,663 | 1.0120 | 1.0000 | 1.027 | 0.999 |
| vsplib-tree | 26 | 27,438,779 | 27,523,233 | 1.0031 | 1.0000 | 1.009 | 1.000 |
| rome | 8,269 | 174,571,249,023 | 177,219,273,870 | 1.0152 | 1.0000 | 1.644 | 0.918 |

The graphs proved by the old run only, rerun under the repaired rules at 3,600 s (`rome_3600s.csv`; a longer cap than the like-for-like table above):

| graph | n | old width | old nodes | old s | new width | proof | new nodes | new s | nodes new/old |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| grafo10104.96 | 96 | 10 | 1225361336 | 543.714 | 10 | refutation | 1231336156 | 475.355 | 1.005 |
| grafo10153.100 | 100 | 9 | 1537829139 | 560.145 | 9 | refutation | 1577045938 | 556.275 | 1.026 |
| grafo10489.95 | 95 | 10 | 1193567600 | 346.669 | 10 | refutation | 1262846560 | 385.979 | 1.058 |
| grafo10527.93 | 93 | 11 | 953819434 | 504.0 | 11 | refutation | 1020380560 | 398.219 | 1.070 |
| grafo10600.93 | 93 | 10 | 1139651896 | 523.591 | 10 | refutation | 1168769251 | 387.573 | 1.026 |
| grafo10663.99 | 99 | 10 | 1135109030 | 424.627 | 10 | refutation | 1168449766 | 423.692 | 1.029 |
| grafo11470.91 | 91 | 11 | 1150778069 | 532.127 | 11 | refutation | 1171540004 | 442.952 | 1.018 |
| grafo11502.100 | 100 | 8 | 1264291316 | 597.261 | 8 | refutation | 1261082635 | 430.677 | 0.997 |
| grafo11647.90 | 90 | 11 | 1125370753 | 575.574 | 11 | refutation | 1148748651 | 420.714 | 1.021 |
| grafo7587.95 | 95 | 9 | 1304823262 | 554.312 | 9 | refutation | 1515568902 | 442.473 | 1.162 |
| grafo8036.94 | 94 | 10 | 1637853596 | 555.048 | 10 | refutation | 1720331443 | 564.975 | 1.050 |
| grafo8585.91 | 91 | 10 | 1213342458 | 536.958 | 10 | refutation | 1220965815 | 410.926 | 1.006 |
| grafo8647.91 | 91 | 11 | 1150778069 | 396.105 | 11 | refutation | 1171540004 | 445.429 | 1.018 |

Errors or kills in the new run: 1
- named `named/gr/DorogovtsevGoltsevMendesGraph.gr`: killed after 1020 s

Old graphs with no new row: 0
