# Section 4's dataset: the price of the full certification run

Regenerate: `python -m paper2.dataset price`. Core-hours are one core's wall time; a censored call counts what it ran, so every spent figure is a lower bound on the price of what it attempted.

## Where the work stands, by collection (classes)

*open, engine*: classes without a certified value whose largest component fits the C engine (≤ 1024 vertices); *open, beyond*: larger, or read by header only. *spent 10-02*: the repaired-rules runs of 2026-10-02 (`solver_fix.md` item 08); *spent here*: this item's run (witnesses and first runs).

| collection | classes | certified | open, engine | open, beyond | spent 10-02 (core-h) | spent here (core-h) |
|---|---:|---:|---:|---:|---:|---:|
| MOSP: Challenge 2005 | 3,169 | 3,169 | 0 | 0 |  | 0.00 |
| MOSP: Faggioli & Bentivoglio | 274 | 274 | 0 | 0 |  | 0.00 |
| MOSP: SCOOP | 24 | 24 | 0 | 0 |  | 0.00 |
| MOSP: Chu & Stuckey | 200 | 198 | 2 | 0 |  | 0.00 |
| MOSP: Carvalho & Soma 2015 | 150 | 11 | 139 | 0 |  | 2.37 |
| MOSP: Frinhani et al. 2018, large | 610 | 0 | 610 | 0 |  | 0.00 |
| VLSI gate matrix circuits | 11 | 10 | 1 | 0 |  | 0.01 |
| VSPLIB trees | 28 | 28 | 0 | 0 | 0.0 | 0.00 |
| VSPLIB grids | 50 | 9 | 19 | 22 | 6.9 | 0.00 |
| VSPLIB Harwell-Boeing | 72 | 39 | 33 | 0 | 5.7 | 0.03 |
| Small (Marti et al. 2008) | 84 | 84 | 0 | 0 |  | 0.00 |
| Rome graphs | 11,199 | 10,873 | 326 | 0 | 110.9 | 0.69 |
| TreewidthLIB colouring | 58 | 31 | 27 | 0 | 4.7 | 0.05 |
| freetdi named graphs | 143 | 119 | 23 | 1 | 2.6 | 0.01 |
| freetdi control-flow graphs | 1,064 | 1,059 | 4 | 1 |  | 0.05 |
| PACE 2016 | 112 | 55 | 51 | 6 |  | 0.44 |
| PACE 2017 exact | 193 | 68 | 115 | 10 |  | 1.00 |
| PACE 2017 heuristic | 173 | 14 | 45 | 114 |  | 0.39 |
| PACE 2017 bonus | 100 | 23 | 77 | 0 |  | 0.68 |

## The next step for the graph collections, priced

Each open class within the engine, run once more at the next budget. The Rome graphs show what to expect: of the graphs still open at one budget, the next (×5–×12) closed 39–45% (table below), so a step closes a share, not the set. Each step's cost is bounded by classes × budget.

| collection | open classes (engine) | next budget | core-hours at most |
|---|---:|---:|---:|
| MOSP: Carvalho & Soma 2015 | 139 | 600 s (had 30 s) | 23 |
| VLSI gate matrix circuits | 1 | 600 s (had 30 s) | 0 |
| VSPLIB grids | 19 | 3,600 s (had 600 s) | 19 |
| VSPLIB Harwell-Boeing | 33 | 3,600 s (had 600 s) | 33 |
| Rome graphs | 326 | 3,600 s (had 600 s) | 326 |
| TreewidthLIB colouring | 27 | 3,600 s (had 600 s) | 27 |
| freetdi named graphs | 23 | 3,600 s (had 600 s) | 23 |
| freetdi control-flow graphs | 4 | 600 s (had 30 s) | 1 |
| PACE 2016 | 51 | 600 s (had 30 s) | 8 |
| PACE 2017 exact | 115 | 600 s (had 30 s) | 19 |
| PACE 2017 heuristic | 45 | 600 s (had 30 s) | 8 |
| PACE 2017 bonus | 77 | 600 s (had 30 s) | 13 |
| **all** |  |  | 500 |

## The Rome graphs: what each budget closed (repaired rules, 2026-10-02)

| file | cap per graph | attempted | proved | share | core-hours |
|---|---:|---:|---:|---:|---:|
| `rome.csv` | 10 s | 11,534 | 10,522 | 91% | 3.6 |
| `rome_120s.csv` | 120 s | 1,012 | 390 | 39% | 25.9 |
| `rome_600s.csv` | 600 s | 622 | 282 | 45% | 79.7 |
| `rome_3600s.csv` | 3,600 s | 13 | 13 | 100% | 1.6 |

## MOSP corpus: the values still open or in flight

The in-flight values are `certified:refutation` in `solutions/` (certified before the repair) and carry a note in the dataset; the two open ones are `solution`. *Item 07 price*: `solver_fix.md` item 07, which says those prices are low. The one density-2 125 × 125 re-certification completed so far, `Random-125-125-2-4_0`, took 154.1 core-hours (split run, refuted 2026-10-03 02:55) against an item 07 price of 47.5.

| instance | state | split run so far (core-h) | item 07 price (core-h) |
|---|---:|---:|---:|
| `Random-125-125-2-1_0` | re-certification in flight (`paper2.solver_fix_split`) | 26.5 | 76.1 |
| `Random-125-125-2-2_0` | optimality open (`solution`) | — | — |
| `Random-125-125-2-3_0` | optimality open (`solution`) | — | — |
| `Random-125-125-2-5_0` | re-certification in flight (`paper2.solver_fix_split`) | 23.5 | 116 |
| `Random-125-125-4-4_0` | re-certification in flight (`paper2.solver_fix_split`) | 36.2 | 153 |

## Never-certified MOSP collections: the §19 cost model, extrapolated

Predicted nodes to refute `optimum − 1` under the `default` configuration (Tobit + drift, trained at n ≤ 75, tested at 100–125: §19's model), converted at 0.55 µs per node (`learning.cost_model.SECONDS_PER_NODE_125`). The best upper bound found here stands in for the optimum. **Extrapolation**: 150–200 lies beyond every size the model was tested at, its per-instance spread is a decade at 100–125, and the post-fix rules cost more on the ridge (`solver_fix.md` item 09). Frinhani is a sample, one instance per density at 400. Instances already certified here are included, which shows how far off the low end is.

| collection | n | instances | median log10 nodes | range | median core-h | ≤ 1 core-h | ≤ 100 core-h | core-h of those ≤ 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MOSP: Carvalho & Soma 2015 | 150 | 50 | 12.2 | 6.3–15.4 | 233 | 20 | 21 | 34 |
| MOSP: Carvalho & Soma 2015 | 175 | 50 | 15.0 | 8.3–18.9 | 1.67e+05 | 10 | 16 | 340 |
| MOSP: Carvalho & Soma 2015 | 200 | 50 | 18.7 | 10.4–23.1 | 7.95e+08 | 0 | 10 | 158 |
| MOSP: Frinhani et al. 2018, large | 400 | 12 | 28.9 | 20.1–69.8 | 1.18e+19 | 0 | 0 | 0 |

