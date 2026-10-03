# Section 4's dataset: defined, checked and priced

*loop0008 item 04, 2026-10-03. Builder `paper2/dataset.py`, independent
checker `paper2/dataset_check.py`, price `paper2/dataset_price.py`, tests
`tests/test_dataset.py` and `tests/test_dataset_check.py`. Data in
`paper2/data/dataset/`.*

```bash
python -m paper2.dataset index  --workers 4    # every source read, nauty certificates (about 4 min)
python -m paper2.dataset values                # values on record: solutions/, pathwidth_solver repaired runs
python -m paper2.dataset run    --workers 4 --until <ISO time>   # witnesses, first runs (2.5 core-h here)
python -m paper2.dataset write                 # pathwidth_dataset.jsonl.gz, classes.csv.gz (1 min)
python paper2/dataset_check.py --sources       # the independent check (2 min)
python -m paper2.dataset tables                # tables.md: counts, deduplication, provenance, published values
python -m paper2.dataset price                 # price.md: the full certification run, by collection
python -m pytest tests/test_dataset.py tests/test_dataset_check.py -q
```

Every stage resumes where its file stops. Nothing here writes to `solutions/`.
The instance files are read from `paper2/benchmarks/raw/`,
`pathwidth_solver/bench/instances/` (both git-ignored; the second is a
sha256-verified copy of the first, `pathwidth_solver/TRANSFER.md`) and
`benchmarks/instances/`.

**Size range.** 21,754 instance files in 20 collections, graphs of 0 to
24,643,531 vertices. The dataset's records cover graphs of 0 to 1,024
vertices with a witnessed value; everything above the C engine's 1,024
vertices per component is listed and priced, not run.

## 1. What the dataset is

The paper promises (`plan.md` §4) a dataset of instances with certified
pathwidth, one value answering every problem in Table 1 that is *exactly*
equivalent to pathwidth. This file fixes what that means.

- **Problems.** Pathwidth, vertex separation and Lengauer's vertex separator
  game (value `w`); MOSP, gate matrix layout including multiple PLA folding,
  one-dimensional logic, interval thickness, narrowness and node search
  number (value `w + 1`). The equalities are section 3's
  (`equivalences.md`, Lean in `lean/MOSPFormalization/Complex/`). Split
  bandwidth and edge search (bands), simple PLA folding and cutwidth (false
  as Table 1 states them) are out, as decided on 2026-09-30.
- **Instances.** Every instance of those problems in the collections of
  `benchmarks/README.md` §1, and the MOSP corpus. Twenty collections:
  - MOSP: the 2005 Constraint Modelling Challenge (and its second copy in
    `MOSP_Instances/Challenge`), Faggioli & Bentivoglio, SCOOP, Chu &
    Stuckey (the corpus); Carvalho & Soma 2015; Frinhani et al. 2018, large;
  - gate matrix layout / one-dimensional logic: the 11 VLSI circuits of
    Lorena's page;
  - vertex separation: VSPLIB trees, grids and Harwell-Boeing; the Small set
    of Martí et al. (2008);
  - pathwidth: the Rome graphs; and graphs from treewidth collections used as
    pathwidth benchmarks: TreewidthLIB's colouring subset, freetdi's named
    graphs and control-flow graphs, PACE 2016, PACE 2017 exact, heuristic
    and bonus.

  The four collections that must be requested (`benchmarks/README.md` §2) and
  those that need converters (§3) are not in it yet.
- **The graph.** For a matrix instance (MOSP, gate matrix), the MOSP graph:
  one vertex per customer (net), a clique per pattern (gate). Its pathwidth
  plus one is the instance's optimum (`MOSPGraph.lean`). For a graph
  collection, the graph as given, self-loops and repeated edges dropped.
- **The unit is the isomorphism class.** Two instances with isomorphic graphs
  have the same value under every problem above, so the dataset holds one
  record per class, listing every member. Classes are nauty canonical
  certificates (`pynauty`, as `learning/canonical.py` uses), across
  collections and across problems. Graphs above 5,000 vertices are read by
  their header only and are deduplicated by the sha256 of their file content,
  not up to isomorphism (78 files, all PACE).
- **The value.** The width `w` of a record is the pathwidth when its
  provenance is `certified:*`, and an upper bound otherwise. A record exists
  only when a witness layout of width exactly `w` is stored. Classes whose
  value is on record without a witness, or which have no value, are in the
  class table and the price, not in the records.

### Orientation of the matrix files, settled from published data

A MOSP file can be read with rows as customers or as patterns, and the two
readings give different graphs. The collections disagree, and the check is
the published MOSP-graph density `D` of Frinhani, Carvalho & Soma (2018), S1
Table (`raw/frinhani2018_plos_s1/pone.0203076.s001_S1_Table.pdf`), and
published values:

- **Chu & Stuckey** (held corpus, rows are patterns, transposed on reading):
  our certified values match S1's class-mean OPT on all 40 classes S1 lists,
  and `D` matches the transposed reading (Random-50-100-4: 0.493 against
  0.293 the other way).
- **Carvalho & Soma 2015: rows are customers.** `D` matches only that reading
  (Random-150-150-2: S1 0.037, rows-as-customers 0.037, transposed 0.042),
  and so do the per-instance values: on Random-150-150-10-1, -2, -3 and -10
  the solver certifies 124, 127, 120, 124 transposed and 127, 124, 124, 123
  untransposed, and the PT-MOSP sheet publishes 127, 124, 124, 123. The
  hunt's note that their README calls the matrices "piece × pattern"
  (`benchmarks/hunt_matrix.md` §2) agrees. A first pass of this item read
  them transposed, like the Chu & Stuckey files they sit beside in PT-MOSP;
  the comparison against published values caught it.
- **Frinhani et al. 2018, large: unsettled.** Their description file says
  "a binary matrix m × n" with m patterns, i.e. rows are patterns, and that
  is how they are read. But `D` does not decide it: it favours the
  transposed reading at 400-2 and 600-2 (0.015 / 0.0103 against 0.017 /
  0.0115), the other at 800-2 and 1000-2, and matches neither at 400-4 to
  400-10. No value of theirs is certified, so nothing rests on it yet; it
  must be settled before one is.
- **VLSI circuits: rows are nets.** Read untransposed, 10 of the 11 circuits
  certify at exactly the published best-known track count (§5); transposed,
  several do not (W2: 7 against 14).

## 2. The file format

`paper2/data/dataset/pathwidth_dataset.jsonl.gz`, one JSON object per line,
one line per isomorphism class with a witnessed value:

| field | meaning |
|---|---|
| `id` | `pwc-NNNNN`, stable for a given index (the classes are numbered in collection order) |
| `n`, `m`, `edges` | the representative graph: vertices `0..n-1`, `m` edges `[u, v]` with `u < v` |
| `width` | `w`: the pathwidth if certified, an upper bound if `solution` |
| `provenance` | `certified:refutation` (a search refuted `w − 1`), `certified:bound` (`w` equals a lower bound; no refutation needed), `solution` (witness only), as in `solutions/` |
| `evidence` | where the value comes from: the `solutions/` file, or the result CSV with its rules, node count and seconds; and the witness's origin |
| `layout` | a vertex order of width exactly `w`: `max_i |N(L[:i]) \ L[:i]|`, the largest boundary of a prefix (section 4's closing-order convention, `revised_algorithm.md` §4.7) |
| `values` | `w` or `w + 1` under each of the nine problems |
| `problems` | the source problems of the members |
| `members` | every instance of the class: `collection`, `problem`, `source` (repo-relative path), `name`, `index_in_file` (MOSP files holding several instances), `to_representative` (`perm[v]` is the representative's vertex for member vertex `v`; `null` for the representative) |
| `lower_bound_certificate` | for `certified:bound` only: `ops`, a list of `["d", v]` (delete) and `["c", v, u]` (contract edge `vu` into `u`) after which every vertex has degree ≥ `w`; since `pw ≥ tw ≥` the minimum degree of any minor, it proves `pw ≥ w` |

Beside it, `classes.csv.gz` has one row per class (17,714), including the
classes without a record, with owner collection, members and provenance;
`index.csv.gz` one row per instance file with its class; `run.csv` and
`run_layouts.jsonl` the runs of this item.

**Where the witnesses come from.**
- MOSP corpus: from the stored pattern sequence in `solutions/`. Customers
  are ordered by the position of their last pattern. When the last customer
  of a prefix closes, every customer on the prefix's boundary is open, so
  the layout's width is at most the sequence's open stacks minus one. At the
  certified optimum it is exactly the pathwidth (`tests/test_dataset.py`
  checks both against brute force). No search was rerun.
- Graph collections already run (`pathwidth_solver/bench/results/repaired/`,
  2026-10-02, repaired rules, `solver_fix.md` item 08): those files keep
  width and proof but no layout. The witness is regenerated by the same
  solver told the recorded width is a lower bound. It then stops at the
  first layout of that width, which is the satisfiable side of the descent
  only, and the refutation is not repeated. The provenance stays the
  recorded one. 11,527 witness tasks. Every certified one reached exactly
  the recorded width but one, a 99-vertex Rome graph certified at 9, whose
  witness did not come back in 120 s; it has no record yet. No regenerated
  witness went below a certified width, which would have contradicted the
  refutation.
- Collections never run before (VLSI, Small, the control-flow graphs, PACE
  within the engine, Carvalho & Soma): a full descent at 30 s per graph,
  repaired rules, in this item.

## 3. The independent checker

`paper2/dataset_check.py` imports nothing from this repository, neither the
builder nor a solver nor a bound. It uses the standard library and nothing
else (a test asserts the imports). Per record it checks:

1. the graph is simple and `m` is right;
2. the layout is a permutation and its width, recomputed, **equals** `w`;
3. every problem value is `w` plus that problem's offset;
4. the provenance is one of the three;
5. for `certified:bound`, the minor certificate replays (each contraction
   along an edge of the current graph) to minimum degree ≥ `w`. Separately,
   it computes its own degeneracy and contraction degeneracy and reports how
   many bounds those alone re-establish;
6. every member's map is a permutation; with `--sources`, each member's
   source file is re-read with the checker's own readers and the map is
   checked to be an isomorphism onto the record's graph.

A `certified:refutation` cannot be checked from the record. It rests on the
repaired-rules customer search (`revised_algorithm.md`) or, for the MOSP
corpus, on the refutations `solutions/` records, all of which were
re-checked under the repaired rules (`solver_fix.md` items 06–09) except the
three in flight. The checker counts these records. A proof object for them
is item 05's subject.

**Result** (2026-10-03, `python paper2/dataset_check.py --sources`):
```
records checked```

Zero failures. All 3,535 bound certificates replay; the checker's own two bounds alone reach 3,261 of them, which is why the certificate is stored. All 20,987 member files were re-read and mapped onto their record's graph.

## 4. Collections, deduplication, provenance

Generated: `paper2/data/dataset/tables.md`.

### Instances per collection, before and after deduplication

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

### Classes shared between collections

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

### Provenance of each class, by the collection that owns it

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

Notes on the deduplication:
- **MOSP: 6,376 instances are 3,667 classes**, as `reports/ml_nature.md` §1
  found by another route. The 46 second copies of the Challenge files add
  nothing, and 13 Faggioli & Bentivoglio graphs are also Challenge graphs.
- **VSPLIB trees: 50 files, 28 classes.** The three rotation folders repeat
  trees up to relabelling.
- **Rome: 11,534 files, 11,199 classes** (150 file contents are repeated
  byte for byte, `benchmarks/hunt_graphs.md`; isomorphism merges more).
- **freetdi control-flow graphs: 1,817 files, 1,070 classes**, many of them
  tiny. 99 classes are also PACE 2016 graphs, and 6 are Rome graphs.
- **Across problems** the overlap is small: one MOSP graph is a freetdi named
  graph (a complete graph), one VSPLIB grid is a named graph, and six Rome
  graphs are control-flow graphs. PACE 2016 and 2017 share many graphs with
  freetdi.

## 5. Against published values

Generated: the end of `paper2/data/dataset/tables.md`.

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

Also from S1's class means: all ten Random-150-150-10 instances are certified here, with mean 123.9 against S1's OPT 123.90.

Two of these are worth a sentence in the paper. **Ten of the eleven VLSI
circuits are certified at their published best-known track count** (5 by
refutation, 5 by bound). Hu & Chen (1990) mark w1, w2 and wsn as minimal
(`benchmarks/hunt_matrix.md`). For the other seven we found no published
proof of optimality in the papers the hunt read, but no search for one was
made in this item. W4 (202 nets) is open at 28 against a best known of 27.
**All 84 Small graphs agree** with the pathwidth Mallach (2018) reports.

## 6. The price of the full certification run

Generated: `paper2/data/dataset/price.md`. Already spent on the MOSP corpus: about a day on 25 cores (667 core-hours, `python -m benchmarks.compute --quote`), plus its re-certification under the repaired rules (`solver_fix.md` items 06–09).

### Where the work stands, by collection (classes)

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

### The next step for the graph collections, priced

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

### The Rome graphs: what each budget closed (repaired rules, 2026-10-02)

| file | cap per graph | attempted | proved | share | core-hours |
|---|---:|---:|---:|---:|---:|
| `rome.csv` | 10 s | 11,534 | 10,522 | 91% | 3.6 |
| `rome_120s.csv` | 120 s | 1,012 | 390 | 39% | 25.9 |
| `rome_600s.csv` | 600 s | 622 | 282 | 45% | 79.7 |
| `rome_3600s.csv` | 3,600 s | 13 | 13 | 100% | 1.6 |

### MOSP corpus: the values still open or in flight

The in-flight values are `certified:refutation` in `solutions/` (certified before the repair) and carry a note in the dataset; the two open ones are `solution`. *Item 07 price*: `solver_fix.md` item 07, which says those prices are low. The one density-2 125 × 125 re-certification completed so far, `Random-125-125-2-4_0`, took 154.1 core-hours (split run, refuted 2026-10-03 02:55) against an item 07 price of 47.5.

| instance | state | split run so far (core-h) | item 07 price (core-h) |
|---|---:|---:|---:|
| `Random-125-125-2-1_0` | re-certification in flight (`paper2.solver_fix_split`) | 26.5 | 76.1 |
| `Random-125-125-2-2_0` | optimality open (`solution`) | — | — |
| `Random-125-125-2-3_0` | optimality open (`solution`) | — | — |
| `Random-125-125-2-5_0` | re-certification in flight (`paper2.solver_fix_split`) | 23.5 | 116 |
| `Random-125-125-4-4_0` | re-certification in flight (`paper2.solver_fix_split`) | 36.2 | 153 |

### Never-certified MOSP collections: the §19 cost model, extrapolated

Predicted nodes to refute `optimum − 1` under the `default` configuration (Tobit + drift, trained at n ≤ 75, tested at 100–125: §19's model), converted at 0.55 µs per node (`learning.cost_model.SECONDS_PER_NODE_125`). The best upper bound found here stands in for the optimum. **Extrapolation**: 150–200 lies beyond every size the model was tested at, its per-instance spread is a decade at 100–125, and the post-fix rules cost more on the ridge (`solver_fix.md` item 09). Frinhani is a sample, one instance per density at 400. Instances already certified here are included, which shows how far off the low end is.

| collection | n | instances | median log10 nodes | range | median core-h | ≤ 1 core-h | ≤ 100 core-h | core-h of those ≤ 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MOSP: Carvalho & Soma 2015 | 150 | 50 | 12.2 | 6.3–15.4 | 233 | 20 | 21 | 34 |
| MOSP: Carvalho & Soma 2015 | 175 | 50 | 15.0 | 8.3–18.9 | 1.67e+05 | 10 | 16 | 340 |
| MOSP: Carvalho & Soma 2015 | 200 | 50 | 18.7 | 10.4–23.1 | 7.95e+08 | 0 | 10 | 158 |
| MOSP: Frinhani et al. 2018, large | 400 | 12 | 28.9 | 20.1–69.8 | 1.18e+19 | 0 | 0 | 0 |

### What the price says

- **Done or nearly done.** The MOSP corpus (3,665 of 3,667 classes
  certified, 3 of them with their re-certification under the repaired rules
  in flight; 2 open), VSPLIB trees, Small, the control-flow
  graphs (1,059 of 1,064), VLSI (10 of 11), Rome (10,873 of 11,199, 97.1%).
- **The next graph step is affordable.** Every open graph within the engine,
  once more at the next budget (3,600 s where it had 600 s, 600 s where it
  had 30 s), costs at most 500 core-hours. The Rome data says each
  such step closes about 40% of what it attempts, not all of it, so the
  graph sets do not close by budget alone: the remaining graphs are the
  long tail, and each step up costs ×5 to ×6 for about 40%.
- **The MOSP corpus's last five are priced in the hundreds of core-hours.**
  The three in flight have item 07 prices of 76 to 153 core-hours, which item
  07 itself calls low. The one density-2 125 × 125 refutation finished so far
  took 154 core-hours against an item 07 price of 47.5. The two open
  density-2 values have never been refuted and would cost the same order.
- **Carvalho & Soma (150–200) are mostly out of reach.** 11 of 150 certified
  here in 30 s each (density 10, where the bound is tight). The cost model
  puts the median at 10¹²–10¹⁹ nodes, far beyond any budget. But it was
  never tested above 125, and it overprices the instances this run certified
  in seconds: it puts 20 of the 150-vertex instances under a core-hour, and
  10 of those are the density-10 class certified here. Read it as "a few
  dozen are within reach; the rest are not". One upper bound found here,
  Random-200-200-6-7 at 119 open stacks, is below the spreadsheet's 120. It
  is a witness, checked, and not an optimum.
- **Frinhani et al. (400–1000) and everything above 1,024 vertices** are
  out of reach of an exact search: 610 + 154 classes. The C engine stops at
  1,024 vertices per component, and the model's prediction at 400 (10²⁹
  nodes at the median) is no price at all.

### What this item ran

4 workers, 2026-10-03 03:15 to 04:22 and 04:24 to 04:46, plus one graph
at 04:55. That was 5.7 core-hours of solver time, inside the 4 cores × 2
hours, of which 1.2 went on Carvalho & Soma read the wrong way round. It
covered the 11,527 witnesses, the first full runs of 1,756 classes at 30 s
each, and the rerun of Carvalho & Soma after the orientation fix. Indexing
took 4 minutes on 4 workers. Left: the classes listed as
open in §6, all of which need budgets beyond this item's.

## 7. For the paper

- The dataset is **17,714 isomorphism classes from 21,754 instance files in
  twenty collections. 16,087 of them carry a certified pathwidth with a
  witness layout, which every problem in Table 1's exact core can read**.
  862 more carry a witnessed upper bound. Every record passes an independent
  checker that shares no code with the solvers.
- State the provenance mix. Bound-certified values carry a checkable minor
  certificate. Refutation-certified values rest on the repaired search and
  have no proof object yet (item 05).
- Report the orientation finding as a caution about MOSP benchmark files:
  the same repository ships two random sets in opposite orientations, and
  only published densities or values tell them apart.
- Do not call the graph values "new" without a search of the literature for
  each collection. Rome has no published per-graph values
  (`benchmarks/hunt_graphs.md`). For the other collections we have not
  checked.
