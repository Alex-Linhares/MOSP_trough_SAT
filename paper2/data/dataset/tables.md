# Section 4's dataset: counts, deduplication, provenance

Regenerate: `python -m paper2.dataset tables` (after `index`, `values`, `run`, `write`).

## Instances per collection, before and after deduplication

*files*: instances read; *distinct*: isomorphism classes within the collection; *new*: classes whose first member, in the order of this table, is in this collection (so the column sums to the dataset's class count); *n*: vertices of the graph (customers or nets for the matrix collections); *header only*: graphs above 5,000 vertices, deduplicated by exact file content, not by isomorphism.

| collection | problem | files | distinct | new | n | header only | unreadable |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOSP: Challenge 2005 | MOSP | 5,806 | 3,169 | 3,169 | 10–100 |  |  |
| MOSP: Challenge 2005 (second copy) | MOSP | 46 | 46 | 0 | 10–100 |  |  |
| MOSP: Faggioli & Bentivoglio | MOSP | 300 | 287 | 274 | 9–50 |  |  |
| MOSP: SCOOP | MOSP | 24 | 24 | 24 | 13–134 |  |  |
| MOSP: Chu & Stuckey | MOSP | 200 | 200 | 200 | 30–125 |  |  |
| MOSP: Carvalho & Soma 2015 | MOSP | 150 | 150 | 150 | 150–200 |  |  |
| MOSP: Frinhani et al. 2018, large | MOSP | 610 | 610 | 610 | 400–1000 |  |  |
| VLSI gate matrix circuits | gate matrix layout / one-dimensional logic | 11 | 11 | 11 | 10–202 |  |  |
| VSPLIB trees | vertex separation | 50 | 28 | 28 | 22–202 |  |  |
| VSPLIB grids | vertex separation | 50 | 50 | 50 | 25–2916 |  |  |
| VSPLIB Harwell-Boeing | vertex separation | 73 | 72 | 72 | 24–960 |  |  |
| Small (Marti et al. 2008) | vertex separation | 84 | 84 | 84 | 16–24 |  |  |
| Rome graphs | pathwidth | 11,534 | 11,199 | 11,199 | 10–110 |  |  |
| TreewidthLIB colouring | pathwidth (treewidth collection) | 58 | 58 | 58 | 5–864 |  |  |
| freetdi named graphs | pathwidth (treewidth collection) | 150 | 146 | 143 | 4–3282 |  |  |
| freetdi control-flow graphs | pathwidth (treewidth collection) | 1,817 | 1,070 | 1,064 | 1–1452 |  |  |
| PACE 2016 | pathwidth (treewidth collection) | 291 | 288 | 112 | 0–24643531 | 5 |  |
| PACE 2017 exact | pathwidth (treewidth collection) | 200 | 199 | 193 | 48–3706 |  |  |
| PACE 2017 heuristic | pathwidth (treewidth collection) | 200 | 197 | 173 | 7–15531867 | 73 |  |
| PACE 2017 bonus | pathwidth (treewidth collection) | 100 | 100 | 100 | 92–420 |  |  |
| **all** |  | 21,754 |  | 17,714 |  | 78 | 0 |

## Classes shared between collections

| collections | classes |
|---|---:|
| freetdi control-flow graphs + PACE 2016 | 99 |
| freetdi named graphs + PACE 2016 | 60 |
| MOSP: Challenge 2005 + MOSP: Challenge 2005 (second copy) | 46 |
| MOSP: Challenge 2005 + MOSP: Faggioli & Bentivoglio | 13 |
| freetdi named graphs + PACE 2016 + PACE 2017 heuristic | 12 |
| Rome graphs + freetdi control-flow graphs | 6 |
| PACE 2016 + PACE 2017 heuristic | 6 |
| freetdi named graphs + PACE 2016 + PACE 2017 exact + PACE 2017 heuristic | 4 |
| PACE 2016 + PACE 2017 exact | 2 |
| MOSP: Challenge 2005 + freetdi named graphs | 1 |
| VSPLIB grids + freetdi named graphs | 1 |
| TreewidthLIB colouring + freetdi named graphs + PACE 2016 | 1 |
| TreewidthLIB colouring + PACE 2017 heuristic | 1 |
| freetdi named graphs + PACE 2017 heuristic | 1 |

## Provenance of each class, by the collection that owns it

Classes, not files. A class's value is its best-established member's.

| collection | certified:refutation | certified:bound | solution | certified:refutation (no witness yet) | certified:bound (no witness yet) | solution (no witness yet) | no value |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOSP: Challenge 2005 | 3,168 | 1 | 0 | 0 | 0 | 0 | 0 |
| MOSP: Challenge 2005 (second copy) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MOSP: Faggioli & Bentivoglio | 274 | 0 | 0 | 0 | 0 | 0 | 0 |
| MOSP: SCOOP | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| MOSP: Chu & Stuckey | 198 | 0 | 2 | 0 | 0 | 0 | 0 |
| MOSP: Carvalho & Soma 2015 | 11 | 0 | 139 | 0 | 0 | 0 | 0 |
| MOSP: Frinhani et al. 2018, large | 0 | 0 | 0 | 0 | 0 | 0 | 610 |
| VLSI gate matrix circuits | 5 | 5 | 1 | 0 | 0 | 0 | 0 |
| VSPLIB trees | 28 | 0 | 0 | 0 | 0 | 0 | 0 |
| VSPLIB grids | 9 | 0 | 19 | 0 | 0 | 22 | 0 |
| VSPLIB Harwell-Boeing | 32 | 7 | 33 | 0 | 0 | 0 | 0 |
| Small (Marti et al. 2008) | 32 | 52 | 0 | 0 | 0 | 0 | 0 |
| Rome graphs | 8,126 | 2,746 | 326 | 1 | 0 | 0 | 0 |
| TreewidthLIB colouring | 18 | 13 | 27 | 0 | 0 | 0 | 0 |
| freetdi named graphs | 97 | 22 | 23 | 0 | 0 | 0 | 1 |
| freetdi control-flow graphs | 398 | 661 | 4 | 0 | 0 | 0 | 1 |
| PACE 2016 | 37 | 18 | 51 | 0 | 0 | 0 | 6 |
| PACE 2017 exact | 61 | 7 | 115 | 0 | 0 | 0 | 10 |
| PACE 2017 heuristic | 11 | 3 | 45 | 0 | 0 | 0 | 114 |
| PACE 2017 bonus | 23 | 0 | 77 | 0 | 0 | 0 | 0 |
| **all** | 12,552 | 3,535 | 862 | 1 | 0 | 22 | 742 |

## Against published values

VLSI circuits, tracks (= pathwidth + 1 of the net graph). Best known from Oliveira & Lorena (2002) Table I as recorded in `benchmarks/hunt_matrix.md`.

| circuit | nets | best known | here | provenance |
|---|---:|---:|---:|---:|
| V4470 | 37 | 9 | 9 | certified:refutation |
| W1 | 18 | 4 | 4 | certified:bound |
| W2 | 48 | 14 | 14 | certified:bound |
| W3 | 84 | 18 | 18 | certified:refutation |
| W4 | 202 | 27 | 28 | solution |
| Wli | 11 | 4 | 4 | certified:bound |
| Wsn | 17 | 8 | 8 | certified:refutation |
| X0 | 40 | 11 | 11 | certified:refutation |
| v4000 | 10 | 5 | 5 | certified:bound |
| v4050 | 13 | 5 | 5 | certified:bound |
| v4090 | 23 | 10 | 10 | certified:refutation |

Small (Martí et al. 2008): 84 values read from Mallach (2018) Tables 4-5 (pp. 165-166); compared 84, agree 84, differ 0; certified here 84.

Carvalho & Soma (2015), open stacks against the PT-MOSP spreadsheet (`raw/carvalho_soma2015/PT-MOSP_reference_values_LARGER_AND_HARDER_RANDOM.xlsx`, sheet `best solutions larger random`, which is at or below the sheet `optimal solutions known` on all 150 and below it on 15; the latter's legend marks some values as not proved optimal). Read with rows as customers (see `paper2/dataset.md` on orientation): certified =: 11, upper bound <: 1, upper bound =: 38, upper bound >: 100. Disagreements: Random-200-200-6-7: 119 (solution) vs 120

