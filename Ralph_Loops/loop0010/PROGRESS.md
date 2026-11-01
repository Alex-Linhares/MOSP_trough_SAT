# loop0010 progress

Plan: `reports/excess_phase_plan.md` — a one-parameter theory of MOSP in the
excess `e = (n_ones − m) / n`; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0010/gate.py`.

Current: 10/13 SOLVED

## Setup — 2026-10-31

- **Baseline.** Lean: zero `sorry`, zero `axiom` in code (the §24 conjecture
  was proved before Appendix E; the gate's baseline is 0). Tests: 89 test
  modules. Paper: `paper1/latex/main.pdf` builds, 66 pages, Appendix E
  (`sec9e_appendix_random.tex`) holds the first moment and the generator.
- **Data on record** (nothing to re-solve): 6,376 certified corpus
  instances; 50,716 certified random covers in the four ensemble frames
  (`n = 10–100`, `m / n` ⅛–8, both generators); 7,200 generator simulations
  under `reports/scratch/clique_cover_moment/sim_solutions/`.
- **Three corrections to the brief, carried into the plan** (§0 of
  `reports/excess_phase_plan.md`): the hardest Chu & Stuckey classes
  (`d = 2`) sit at `e = 1.6–2.0`, below the generated-ensemble ridge at
  2–2.4; the incidence graph's giant component appears at `e_g(r) ≈ 0.62`
  (`r = 1`), so `e < 1` is not a forest regime; a second moment of empty
  pairs cannot lift `β*` (it bounds `P(X > 0)` from below), so item 08 is a
  structured count with the second moment as diagnostic.
- **Driver.** `loop.py` is loop0009's with the item regex widened so the
  whole item text (2-space continuation) reaches the session; loop0009's
  passed only the first line. `gate.py` points at `paper1/latex` (the
  paper directory was renamed from `paper2/`) and checks that every Lean
  file, top level included, is imported.
- **Before launch.** The driver refuses to start while `git status` shows
  changes under `learning reports tests benchmarks satisfiability mosp
  customer_inter`; on 2026-10-31 there are 55 untracked scratch files
  under `reports/scratch/`. Commit them or ignore them first. Check that
  the owner's `run_unlimited.py` is not running (by PID), or leave it its
  cores.

---

## Iteration 1 — 2026-10-31 23:15

Item 01, the map: every instance on record placed by its excess.

### Completed

- **`learning/excess.py`** (`python -m learning.excess`; stages `build`,
  `tables`, `figure`): for every instance we hold — 6,376 corpus, 50,715
  ensemble (all four frames, regenerated from their seeds, the recorded
  `n_ones` asserted equal on every row) and 7,200 generator simulations
  (regenerated from their seeds, `ones` asserted equal) — `n`, `m`,
  `n_ones`, `e`, `r`, `c`, the incidence graph's `κ`, `γ`, `γ / n`, its
  largest component as a fraction of vertices and of customers, the forest
  flag, the (2, 2)-core shares, and the certified optimum. 64,291 rows in
  `learning/data/excess.csv` (15.1 MB, git-ignored under `learning/data/*`),
  4 s wall on 8 workers. Nothing solved, `solutions/` untouched. Two
  identities hold to 10⁻¹⁴ on every row and the 2-core is empty exactly
  when `γ = 0` on every row (asserted).
- **`tests/test_excess.py`**, 8 tests: `e`, `γ`, `κ` by hand on a path
  (forest), a 4-cycle with a pendant and a two-component graph;
  `e = r (c − 1)` and `γ / n = e − 1 + κ / n` on random matrices; the
  thresholds; the crossing interpolation on a synthetic series.
- **`reports/excess_phase_diagram.md` §1** (created), every table in full
  (per collection with Chu & Stuckey by class; the stated check; 526
  ensemble series, folded; 10 simulation cells; the bound-gap instances
  against their cells), the figure
  `reports/figures/excess_giant_component.png`, regenerate commands.
- **Numbers.** Corpus: 0 instances below `e_g(r)`, 12 in `[e_g, 1)`, 2
  incidence forests (one Simonis 10 × 10, one Faggioli–Bentivoglio);
  median `e` 4.87, 9.4% in `[1, 2)`, 7.8% in `[2, 2.4]`. SCOOP: `e`
  0.97–2.50, median 1.35, 19 of 24 in `[1, 2)`, 10 of 24 decompose.
  Chu & Stuckey `m = n`: `d = 2` at 1.48–2.02 (125 × 125: 1.66–1.78),
  `d = 4` at 2.83–3.73 — the ridge at 2–2.4 lies between them. Ensembles:
  3,127 below `e_g(r)` (all Bernoulli; 6 at `n ≥ 50`), 3,446 forests
  (none at `n = 100`); the fixed generator's padding keeps it at `e ≥ 0.85`.
  Forest share falls from 0.74–0.92 below `e_g(r)` to 0.23–0.40 in
  `[e_g, 1)` and to 0 at `e ≥ 1` (forced by the identity). Bound-gap
  instances: the median one sits at the 7th percentile of `e` in its
  `(n, m)` cell, 97.4% below the cell median; 41% in `[1, 2)` against 7.6%
  of the rest. Simulations reproduce the Chu & Stuckey `m = n` medians
  within 0.16 at every `d`.
- **Kill verdict: none (descriptive). The stated check is not met**: the
  largest component of `B` crosses one half at `e = 0.83–0.93` on the five
  observable series at `n ≥ 50`, +0.21 to +0.43 above `e_g(r)` (tolerance
  ±0.15); the other 30 series have every cell above one half. The
  criterion could not have been met — at the branching-factor-one point
  the giant fraction is zero by definition — so `e_g(r)` is **not to be
  used later as a half-point**; what it does separate is "mostly forests"
  from "a few cycles" (finding 5 of the report). Items 06 and 11 should
  state the random corollary with that meaning or avoid the line.
- **Gate.** First run failed on a pre-existing stale pin outside this
  item: `tests/test_sandwich.py::test_lean_theorems_are_sorry_free`
  expected `conjecture_sqrt_tw_f6` to carry `sorryAx`, but it was proved
  on 2026-10-31 (before this loop). Promoted it to `PROVED` in
  `learning/sandwich.py`, `STATED` is now empty, and the inventory test's
  two assertions updated (`STATED == ()`, zero `sorry` in the
  tree-decomposition section). Second run: lake build ok, sorry 0, MOSP
  pytest 1,529 passed, pathwidth_solver 123 passed, paper check ok, but
  the import check failed on a second pre-existing fault, also present in
  the first run's log: `Search/WrongOptimumData.lean` (committed
  2026-10-11, imported by `Search/WrongOptimum.lean` so already built) had
  no line in `lean/MOSPFormalization.lean`. Added the one import line; no
  proof touched. Third gate run: **PASS** (lake build ok, every file imported, sorry 0, MOSP pytest 1,529 passed, pathwidth_solver 123 passed, paper check ok; 23 min under load 30).

### Blockers

None.

### Next

Item 02: `opt / n` against the excess. From this map: the `e`-matched
series it needs exist (`e = 2`: `(3, 1)`, `(5, ½)`, `(2, 2)`, `(9, ¼)`),
and the realised `e` of every cell is in `learning/data/excess.csv`
(`learning.excess.load()`), so no regeneration is needed there.

---

## Iteration 2 — 2026-10-31 23:38 (ends past midnight)

Item 02, `opt / n` against the excess: one parameter, or two?

### Completed

- **`learning/first_moment.py`**: the asymptotic constant `β*(d, μ)` of
  `reports/scratch/clique_cover_moment/asymptotic_cs.py` and the finite
  floor of `bound_lib.py` / `finite_bound_cs.py`, moved as a library with the
  same formulas and a histogram interface; `tests/test_first_moment.py` (16
  tests) reproduces `asymptotic_cs.log` (the whole `β*(d, μ)` table, the
  threshold `d > 2.0031`, five classes at empirical sizes) and
  `finite_bound_cs.log` (five classes' mean floors) to the printed digits.
  Reads the benchmark files and `instances.csv`, never `solutions/`.
- **`learning/excess.py --stage rule`**: the two-key rule on every ensemble
  instance (regenerated from its seed) and every corpus instance, 57,091
  rows with the certified optimum and the pattern-size histogram, 30 s of
  rule time, 7 s wall on 8 workers, to `learning/data/excess_rule.csv`
  (git-ignored). **`--stage slopes`**: per series `opt = a + b n` on
  `n ≥ 30` with standard errors, `β*` at the realised sizes, the
  `e`-matched pairs, the named groups, a `β*`-matched control, the rule per
  excess bin and its worst cases. **`--stage figure-opt`**:
  `reports/figures/excess_opt.png`. Five new tests in `tests/test_excess.py`
  (synthetic series with known slopes and verdicts).
- **`reports/excess_phase_diagram.md` §2**, tables in full.
- **Numbers.** 72 series with ≥ 3 sizes at `n ≥ 30`; 41 are constant-`e`
  (fixed `d`, and the 5 Chu & Stuckey `m = n` classes across 30–125). The
  31 Bernoulli series at fixed `p` are **not** constant-excess series
  (`e = r (n p − 1)` grows with `n`, intercepts to −26, slopes above 1) and
  are excluded from the kill count. Of the 16 constant-`e` matched pairs
  (`|Δe| ≤ 0.05`, different `(d, μ)`), **13 differ by more than twice the
  larger standard error** (26 of all 30). At `e = 2` the slope is 0.282,
  0.232, 0.200, 0.167 for `μ = ¼, ½, 1, 2` (se 0.002–0.006): it falls with
  `μ` at fixed `e`, and `β*` falls the same way (0.180, 0.169, 0.147,
  0.123). Over the 41 series `b = 0.057 + 0.984 β*` with residual sd 0.024,
  against 0.042 for the best line in `log e`; `b − β*` is 0.005–0.108 and
  peaks on the ridge (0.07 at `e = 1.5–4`, 0.03 at the ends). The bare rule
  is exact on 83.3% of the corpus, 62.2% of the ensembles, 27% of the 200
  Chu & Stuckey (mean gap 2.35, worst 10); its gap peaks on the ridge (exact
  22% at `e ∈ [1.5, 2)`, gap/n 0.03–0.04) and its per-customer excess grows
  with `n` there (0.03 at 30, 0.058 at 100), so `rule / n` is not the slope.
- **Kill verdict: met — "a function of `e` alone" is dead.** The parameter
  of `lim opt / n` is `(d, μ)`, or to 0.024 `β*(d, μ)`; `e` sets the
  threshold, the ridge and the scale.
- **A stale table found and routed around.** `learning/data/instances.csv`
  (2026-09-25) says `solution` for four `125 × 125` instances certified in
  October (`2-2_0`, `2-3_0`, `2-5_0`, `4-4_0`); item 01's map therefore had
  6,372 certified corpus rows. `corpus_rows` now reads value and provenance
  from the solution file; the map is rebuilt (6,376 of 6,376), no §1 number
  changes (its tables do not use the optimum). Nothing re-solved; no
  certified value is wrong.
- **Gate: PASS** (one run, 2026-11-01 00:00, 11 min at load 1–10): lake build ok, every file
  imported, sorry 0, MOSP pytest 1,549 passed (2 skipped, 1 xfailed), pathwidth_solver 123
  passed, paper check ok (66 pages, no undefined references).

### Blockers

None.

### Next

Item 03, the forest regime by brute force (the C program on clique trees).
From item 02: items 05, 07, 08 and 09 should carry `(d, μ)` — or `β*` — as
the coordinate of the constant, with `e` as the coordinate of the threshold
and the ridge; the rule's `width / n` drifts upward with `n` on the ridge,
so item 05's extrapolation should be checked against the certified slope at
`n ≤ 100` as its kill says.

---

## Iteration 3 — 2026-11-01 00:12

Item 03, the forest regime by brute force.

### Completed

- **`learning/block_trees.py`**: the families (`clique_tree` `CT(s, h, b)`,
  `caterpillar_of_cliques`, `random_block_tree` with Chu & Stuckey's size
  law), the graphs (MOSP graph, incidence graph, pattern adjacency), the
  invariants (`ω`, block height `h`, `tree_bound`, `ternary_subtree_height`),
  the six candidates, the driver for the C program
  `pathwidth_solver/cli/pathwidth` (one niced process per graph, layouts
  kept and re-checked by an independent `vertex_separation`). **`learning/chou_block.py`**:
  Chou, Ko, Ho & Chen's Theorem 4 as an exact oracle (exponential as
  written, `n ≤ 30`). `tests/test_block_trees.py` (10) and
  `tests/test_chou_block.py` (4).
- **`reports/scratch/forest_regime/`**: scripts, graph6 files, logs, layouts
  (the witnesses), CSVs: 29 clique trees of the item's grid (`n ≤ 365`, all
  exact, < 1 min), 18 of an extension to `s ≤ 8`, `h ≤ 4`, `n ≤ 936` (11
  exact, 7 censored at 600 s wall under load 40–60, two of them settled by
  induced-subgraph monotonicity), 24 caterpillars of cliques, 900 random
  block trees at `n = 20–120` (898 exact, 2 censored at 600 s and still
  censored after 3600 s more each at `1.25 × 10¹⁰` nodes, intervals [6, 7]
  and [7, 8]), 3,448 forests on record scored for free from their certified
  optima; `cross_check.log`: the oracle agrees with the C program on 328 of
  328 small graphs. About 4.5 core-hours in all (the reruns included).
  Nothing through the Python solvers; `solutions/` untouched.
- **`reports/excess_phase_diagram.md` §3**, with every table of `fit.log`.
- **Literature.** Chou, Ko, Ho & Chen, DAM 156 (2008) 55–75,
  doi:10.1016/j.dam.2007.08.007: node search on block graphs is polynomial,
  `O(c² + bc + n)`, by Theorem 4 (`ns ≤ k` iff at most two branches with
  `ns ≥ k` at every vertex and, at every block, an edge whose enclosure
  subgraph has `ns < k`). Pathwidth is NP-hard on chordal graphs (Gustedt
  1993). We found no prior statement of a closed form on clique trees.
- **Numbers.** Grid: `CT(s, 1, b) = ⌈3s/2⌉ − 2` for every `b` (1, 3, 4, 6),
  the same value as the caterpillar of cliques at every length; `CT(s, 2, 1)
  = 2s − 3`, `CT(s, 2, 2) = CT(s, 2, 3) = 2s − 2`; the slope in `ω` rises
  with the depth (3/2, 2, 5/2). The additive candidates are not upper
  bounds (`ω − 1 + pw(B)` violated on the grid once and on the extension 6
  of 12; `ω − 1 + h` 7 and 12); the blow-up bound and the TreeBound form are
  never violated and never exact (mean slack 7.4 / 9.9 on the grid, 17 / 25
  on the random trees). Off the structured family `pw = ω − 1` on 99.8% of
  the 3,448 record forests and 92.8% of the random block trees (`ω` on the
  rest, never more). Two random block trees at `n = 120` needed `> 2 × 10⁹`
  nodes at `k = ω − 1`; the exact theory is quadratic.
- **A stated form refuted before it was called anything.** After the grid,
  `C1 = ⌈(h + 2)(s − 2)/2⌉ + pw(CT(2, h, b))` fitted all 29 values; the
  extension's `CT(3, 3, 3)` has a verified width-5 layout against `C1 = 6`,
  and 5 is exact since `CT(3, 3, 2)` (pathwidth 5) is an induced subgraph.
  `C2 = ⌈(h + 2)(s − 2)/2⌉ + 1 + [b ≥ 2][h ≥ 2]` fits all 33 values with
  `s ≥ 3` and is provably not the law at `s = 3` from `h = 8` (the ternary
  subtree forces `≥ h`). No closed form is conjectured.
- **Kill verdict: met.** No `α (ω − 1) + β h + γ` fits the grid (0 of 325
  forms; the best misses 14 of 29). Item 06 proves the blow-up bound only,
  cites Chou et al. for exactness, and may add the `h = 1` lower bound
  `⌈3ω/2⌉ − 2` for a clique with pendant cliques at `ω − 2` vertices.
- **Gate: PASS** (one run, 2026-11-01 00:45–01:05 at load 45–55): lake build ok, every file
  imported, sorry 0, MOSP pytest 1,563 passed (2 skipped, 1 xfailed; +14 new), pathwidth_solver 123
  passed, paper check ok. The gate ran while the reruns ran; nothing under test depends on them.

### Blockers

None.

### Next

Item 04, the SCOOP instances. For item 06: cite Chou et al. (2008) rather
than prove exactness; prove the blow-up bound; the forest regime's
practical content is `pw = ω − 1` almost surely under the random model
(finding 5), which the random corollary should state. For item 11 the
blow-up lemma is the Lean target as planned.

---

## Iteration 4 — 2026-11-01 01:55

Item 04, industrial instances: the 24 SCOOP instances in the excess.

### Completed

- **`learning/excess_scoop.py`** (`python -m learning.excess_scoop`; stages
  `build`, `tables`): for the 24 SCOOP and the 300 Faggioli–Bentivoglio
  instances, one row joining what is on record and nothing else — item 01's
  map (`e`, `γ`, `κ`, forest, 2-core, the certified optimum with its
  provenance), `instances.csv`'s bounds, item 02's two-key rule value and
  size histogram, the finite floors at bound < 1 and < 0.01 and `β*` from the
  instance's own size law, the three September SAT-path sweeps (first
  `solved` row = the certification; later rows are cache hits), the compute
  ledger (no row for any of the 324), the refutation counts of
  `node_counts.csv` (n ≤ 40) and the differential harness's identity
  labelling (50–100), the search certificates, the DRAT proofs, and the
  cost model's prediction (chosen variant refitted per configuration, with an
  `in_training` flag). `learning/data/excess_scoop.csv`, 324 rows,
  git-ignored; 5 s. Nothing solved, nothing re-run, `solutions/` untouched.
  `tests/test_excess_scoop.py`, 8 tests, including an exact-rational
  recomputation of the union bound independent of `learning.first_moment`.
- **`reports/excess_phase_diagram.md` §4**: the per-instance table in full,
  the regime table, the Faggioli–Bentivoglio cell table, the floor checks
  (two collections, and every certified corpus instance per collection), the
  cost model against every recorded count, and the planner's statement as a
  draft of the paper's paragraph. Both dataset READMEs quoted.
- **Numbers.** SCOOP: `e` 0.97–2.50, median 1.35; 19 of 24 in `[1, 2)`, 3
  on the ridge, 1 above, 1 in `[e_g, 1)`; none a forest, none below
  `e_g(r)`; 10 decompose. `lb_best` tight on 6 (worst gap 6), `ub_best` on
  12, the rule exact on 12 (mean gap 1.21, worst +7, `gap / n ≤ 0.061`) and
  exact on 47% of the `[1, 2)` instances against 13% of the 143
  Faggioli–Bentivoglio instances in the same regime. Refutations on record
  for 22 of 24: 44,379 nodes and 0.07 s in all (max 22,433), labelling
  spread ≤ 9%; the SAT path took 1,662 s on the 24, 1,459 of them on
  `A_FA+AA-_13` (134 customers). The two largest have no node count
  ("not recorded", not re-run); the cost model predicts 10^5.6 and 10^7.5
  nodes (`default`), 0.3 s and 20 s at 0.65 µs, and is within a decade on all
  22 recorded SCOOP counts (out of sample at 60–99: MAE 0.33, worst 0.47) and
  all 300 Faggioli–Bentivoglio counts. Faggioli–Bentivoglio spans `e`
  0.94–8.7 and its cost peaks in the `40 × 50` cell on the ridge (median
  24,000 nodes).
- **The stated check is not met on one of 24, and is reported:**
  `scoop-B_REVAL_145_0` (60 customers, 49 patterns, `e = 1.88`, optimum 7)
  has a 0.01 floor of 9 — a random cover of its size law has optimum ≤ 7
  with probability below 6.8 × 10⁻⁵, confirmed with exact rationals. Two
  more sit below the floor at bound < 1. Not a contradiction (the floor is
  a random-model statement); the context table shows zero violations on the
  200 Chu & Stuckey, 300 Faggioli–Bentivoglio, 3,630 Simonis and 2,130
  Harvey instances, and the designed Challenge / Wilson / Shaw instances up
  to 39 stacks below: the floor measures distance from random, and REVAL is
  the one SCOOP instance with visible structure.
- **An orientation note for item 12.** The SCOOP README's prose ("49 pieces
  and 134 patterns") has pieces and patterns the other way round from its
  own format line; the loader transposes every `MOSP_Instances/` file, so
  our customers are the file's pieces (`REVAL` = 60 × 49, `_13` = 134 × 37).
  Frinhani et al. give SCOOP results as a figure, so no per-instance
  published optimum exists to compare. All certified values are for the
  instances as loaded; the paper should state the orientation.
- **Kill verdict: none** (descriptive); the one check reported as above. No
  certified value is wrong, no theorem is false, no published claim of ours
  drifts.
- **Gate: PASS** (one run, 2026-11-01 02:00–02:14 at load 1–2): lake build
  ok, every file imported, sorry 0, MOSP pytest 1,570 passed (2 skipped,
  1 xfailed; +8 new), pathwidth_solver 123 passed, paper check ok (66 pages,
  no undefined references). Log: `Ralph_Loops/loop0010/gate_it04.log`.

### Blockers

None.

### Next

Item 05, `β⁺` by simulation. From this item: the rule's `gap / n` on the
sparse flank is 0.03–0.06 at 30–134 customers on real and generated
instances alike, so item 05's kill (0.03 between the rule at the largest `n`
and the certified slope at `n ≤ 100`) is tight on the flank and should be
checked per cell, not pooled. For item 12: the planner's paragraph is drafted
in §4.2; state the SCOOP file orientation in the paper's instance paragraph;
REVAL is the example that the floor is a random-model statement. For item 08:
REVAL (optimum 7 against a 0.01 floor of 9) is a test case a structured count
must not "fix" — a stronger random floor would move further from it, which is
correct, and the paragraph should say so.

---

## Iteration 5 — 2026-11-01 02:25

Item 05, `β⁺` by simulation: the width of explicit constructions at large `n`.

### Completed

- **`learning/excess_constructions.py`** (stages `constructions`,
  `constructions-tables`, `figure-constructions` of `learning.excess`): fresh
  random covers at `d ∈ {2, 3, 4, 6, 8, 10}`, `μ ∈ {½, 1, 2}`,
  `n ∈ {100, 200, 500, 1000, 2000, 5000}`, 10 per cell, from the fixed-size
  generator (`generate_structured_instance`, the generator of item 02's
  certified series) and the fitted Chu & Stuckey generator of
  `gen_candidates.py` (`bern_padC1_padP2_conn`, with a draw cap per `n`
  and one probe draw per cell). Per instance the two-key rule's product
  order valued by a sweep (the `O(n m)` Python simulation replaced; agrees
  with `two_key_rule` on every test), the BFS-layer layout's exact vertex
  separation and the layer bound, `n − α_greedy`, `|E| / 5.769`; per cell
  and construction the fit `width / n = β⁺ + a / n` with `β*` and item 02's
  `b` beside it, and the kill flag. 2,043 rows (2,024 accepted) in
  `learning/data/excess_constructions.csv` (git-ignored), 1.61 core-hours
  (98% the rule, `O(n²)`: 11–22 s at `n = 5000`), 751 s wall on 8 workers at
  nice 19, load 1–9. **No exact solve**; `solutions/` and the ledger
  untouched. `tests/test_excess_constructions.py`, 10 tests (the sweeps
  against `mosp.verify.max_open_stacks` and brute-force vertex separation
  on 200 random instances each, the rule's value against `two_key_rule`,
  BFS layers and the greedy set checked structurally, proved constructions
  above the certified optimum − 1 on 20 solved instances, seeds, the fit,
  the tables). Figure `reports/figures/excess_beta_plus.png` (dataviz
  reference palette, validated). `reports/excess_phase_diagram.md` §5 with
  every table; scratch log and tables under
  `reports/scratch/excess_constructions/`.
- **Numbers.** The rule's `width / n` **falls** with `n` in all 36 cells
  (item 02 expected an upward drift), the `1 / n` form fits with residuals
  within ±0.009, and `β⁺` moves by ≤ 0.01 under `1 / √n` or `log n / n`.
  `rule β⁺ − b` is 0.007–0.060: smallest at the ends of the excess (0.007 at
  `(10, 2)`, 0.017 at `(2, 1)`), 0.035–0.047 at `d = 3–4` (ridge and
  shoulder), 0.04–0.06 at every `μ = ½` cell; `rule β⁺` is below the
  certified `opt / n` at `n = 75–125` on 20 of 23 cells. The proved
  constructions: `n − α_greedy` 0.48–0.96 (flat in `n`), the edge bound
  better only at `e ≲ 2–2.5` and above 1 from `(4, 1)`; best proved minus
  `β*` 0.075 (`(10, 2)`) to 0.61, below 0.5 on 29 of 35 cells, so item 07's
  kill is not met in advance but no proved construction is within 0.07 of
  `β*` anywhere. BFS separation 0.13–0.96, 1.1–2.4× the rule — except on
  the fixed `(2, ½)` cell (`e = 0.87`, 652 components at 5000), where the
  BFS width is sublinear (0.073 → 0.005 per customer, 25 stacks at 5000)
  and **the rule's is linear** (0.044 ± 0.002, 215 stacks; certified
  `b = 0.005 ± 0.006`). The fitted generator is not accepted at large `n`
  and small `d` (`(2, ½)` from `n = 200`, `(3, ½)` from 1000, `(4, ½)` and
  `(2, 1)` from 2000, `(3, 1)` at 5000; acceptance `exp(−c n)`), and where
  accepted its realised `e` is 0.1–1.1 above nominal and its `β⁺` 0.005–0.035
  above the fixed generator's.
- **Kill verdict: met on 12 of the 23 cells with a certified `b`.** Not
  trusted (|rule/n at max `n` − `b`| > 0.03): all six `μ = ½` cells
  (0.038–0.062), fixed `(3, 1)`, `(4, 1)`, `(3, 2)`, `(4, 2)`, fitted
  `(2, 1)`, `(4, 1)`. Trusted: fixed `(2, 1)`, `(6, 1)`, `(8, 1)`, `(10, 1)`,
  `(2, 2)`, `(6, 2)`, `(8, 2)`, `(10, 2)`, fitted `(6, 1)`, `(8, 1)`,
  `(10, 1)`. 13 fitted cells have no certified series and are untested;
  neither group is to be quoted by later items. No certified value is
  wrong, no theorem is false, no published claim of ours drifts.
- **Gate: PASS** (one run, 2026-11-01 02:49–03:00 at load 1–4): lake build
  ok, every file imported, sorry 0, MOSP pytest 1,581 passed (2 skipped,
  1 xfailed; +10 new), pathwidth_solver 123 passed, paper check ok (66
  pages, no undefined references). Log: `Ralph_Loops/loop0010/gate_it05.log`.

### Blockers

None.

### Next

Item 06, the forest regime on paper. From this item, for item 07: the
limits to prove are those of `n − α_greedy` (flat in `n` to ±0.005, so the
differential-equation constant is what the table shows) and the BFS layer
fractions (the layer bound is 0.35–1.0 per customer and never binding; the
exact separation of the layer layout is what matters, and it is 1.1–2.4×
the rule's); the table says in advance that neither will be within 0.07 of
`β*`, and that the rule's measured `β⁺` is the envelope to beat. For items
08 and 09: quote `β⁺` only on the 11 trusted cells. For item 10: the fitted
generator's rejection is a finite-size object at `d ≤ 3` (finding 6), which
the validity statement should say. For item 12: the rule's linear width on
the many-component sparse cell against the BFS layout's sublinear one is a
one-sentence caveat on the rule as a bound.

---

## Iteration 6 — 2026-11-01 03:12

Item 06, the forest regime, on paper.

### Completed

- **`learning/forest_theorems.py`** (`python -m learning.excess --stage
  forest_check`): the four statements of §6 as functions (`f1_bound`,
  `f1_log_bound`, `log3_form`, `f2_value`, `clique_with_pendants`,
  `pendant_lower_bound`, `branch_lower_bound_ct`) and three brute-force
  checks — item 03's whole record (4,419 rows, read from its CSVs), 594
  fresh graphs of the depth-one family `K_s` with `b` pendant `K_t` at `q`
  vertices (`s, t ≤ 7`, `q ≤ s`, `b ≤ 3`, `n ≤ 133`) and 2,000 random small
  instances (`n = 6–12`, `m = 4–12`, two generators; 1,799 of them **not**
  forests) solved exactly by the C program, layouts re-checked. 4 s wall on
  8 workers, milliseconds per solve, no MOSP instance solved, `solutions/`
  untouched. Log and three CSVs under `reports/scratch/forest_check/`.
  `tests/test_forest_theorems.py`, 8 tests, repeat the checks on tiny graphs
  through the exact subset DP (no code shared with the C program).
- **`reports/excess_phase_diagram.md` §6**: statements, proofs in numbered
  lemmas (Helly, interval unions, the blow-up decomposition, components, the
  tree bound with the integer identity `tb(N) = ⌊log₃((6N + 3)/5)⌋`, the
  branch lemma, monotonicity), the check's tables, findings, the Lean-ready
  list for item 11, kill verdict, what it does not claim.
- **The theorems.** *F1 (blow-up)*: `pw(G_M) ≤ ω (pw(B) + 1) − 1` for **every
  instance** — the proof (replace each pattern node of a path decomposition
  of `B` by its customers; a customer's nodes in `B` form a star, so its bags
  stay an interval by the union-of-intervals lemma) never uses the forest
  hypothesis, which buys only `pw(B) ≤ tb(n + m)` and hence
  `MOSP ≤ ω (⌊log₃((6(n + m) + 3)/5)⌋ + 1)` (*F1′*). *Lemma P (two-sided
  pendant bound)*: a clique `R` with `q` cliques of size `≥ t` meeting it in
  one vertex each, at distinct vertices, forces `pw ≥ t + ⌈q/2⌉ − 2` (the
  bag argument item 03 sketched, for any graph). *F2 (depth one, exact)*:
  `K_s` with pendant `K_t` at `q` of its vertices has
  `pw = max(s − 1, t + ⌈q/2⌉ − 2)`, whatever the multiplicity; `CT(s, 1, b) =
  ⌈3s/2⌉ − 2` is the case `t = q = s`. *F3*: the branch lemma down a
  recursively defined family gives `pw(CT(s, h, 2)) ≥ s + ⌈(s − 1)/2⌉ + h − 3`
  for `h ≥ 2`, exact at `h = 1`, 1–2 below the truth at `h = 2`; the truth is
  between F3 and F1 and nearer F3. *Corollary R*: conditional on (H1) tree
  components and (H2) largest component `≤ L(n)`, `MOSP ≤ ω (tb(L(n)) + 1) =
  O(ω log log n)` at `L = O(log n)`; the hypotheses are supported by a held
  paper for `G(n, c/n)` (Perarnau & Serra 2014, Theorem 1.2 (1) p. 2, proof
  p. 6) and by Molloy & Reed (1995) Theorem 1 (b) for the configuration
  model — **not held, not verified**; the two-type bipartite form our
  generators need is in no held paper.
- **Numbers.** Zero violations in all: F1 on 4,410 record rows with both
  pathwidths exact, 594 depth-one graphs and 2,000 random instances; F1′ on
  every forest; F2 = pw on 45 record rows and 594 of 594 fresh graphs; F3 on
  14 `CT(s, h, 2)` rows; Lemma P ≤ pw everywhere, exact on 594 of 594 of its
  family and 835 of 2,000 random instances (62 where the clique floor is
  not). F1 is never exact (slack ≥ 1 on all 7,004; ratio to the truth 2–5.5
  on the block-graph families, median 3 on the record forests; F1′ 2.7–9);
  `tb = ⌊log₃((6N + 3)/5)⌋` on every row and every `N < 3000`.
- **Kill verdict: not met** — no counterexample to F1; F1 stands with no
  forest hypothesis. No certified value is wrong, no theorem is false, no
  published claim of ours drifts.
- **Lean-ready for item 11** (§6.5): `incidence M : SimpleGraph (C ⊕ P)`;
  `mospValue ≤ ω * (pathwidth (incidence M) + 1)` given `1 ≤ ω`; the forest
  form through `tree_pathwidth_le_treeBound` per component and the integer
  identity; Lemma P as `pathwidth_ge_of_pendant_cliques`; F2's explicit
  decomposition. F3 not proposed.
- **Gate: PASS** (one run, 2026-11-01 03:23–03:34 at load 1): lake build
  ok, every file imported, sorry 0, MOSP pytest 1,589 passed (2 skipped,
  1 xfailed; +8 new), pathwidth_solver 123 passed, paper check ok (66 pages,
  no undefined references). Log: `Ralph_Loops/loop0010/gate_it06.log`.

### Blockers

None.

### Next

Item 07, `β⁺` on paper. From this item: F1 needs no forest hypothesis, so
item 11's Lean statement (L2) should be stated for every instance and the
forest enter only in (L4); the integer identity `tb(N) = ⌊log₃((6N + 3)/5)⌋`
is proved in §6.2 (Lemma 5) and is the form to use in Lean and the paper.
For item 12: the random corollary is conditional, its domain on the
benchmarks is empty (item 01), and the forest regime's practical content is
item 03's `pw = ω − 1` (a measurement) — say so rather than quote F1′'s
`O(ω log log n)`. For the bound work (outside this loop): Lemma P is a
pathwidth argument that is not degree-based, exact beyond block graphs on a
few small random instances; a `learning/bound_harness.py` run on the 338
bound-gap corpus instances would say whether it is worth anything there.

---

## Iteration 7 — 2026-11-01 03:45

Item 07, `β⁺` on paper: the provable constructions analysed.

### Completed

- **`learning/beta_plus.py`**: the layer lemma (`layer_bound`,
  `bfs_components` — item 05's random choices in the same order, so the
  layout is its layout — `layer_lemma_check`); the exploration recursion for
  the uniform model (`bfs_recursion_uniform`, (R) of §7.2), its degree- and
  size-aware configuration form (`bfs_recursion`), the fixed generator's leaf
  form (`padded_layers`), the phase scan (`bfs_phase_scan`,
  `padded_phase_scan`) and the observed-state extractor (`bfs_state`); the
  greedy independent sets in the slot picture (`greedy_ode` for the
  pattern-count and random policies, (G) of §7.3; the closed form
  `random_greedy_uniform`, (C); `greedy_simulation` with witnesses). 
  `tests/test_beta_plus.py`, 14 tests (the lemma against brute-force vertex
  separation; the layers against item 05's; (R) at `d = 2` equals the
  `G(n, c/n)` recursion to `1e-12`; the general form reduces to (R) for
  Poisson degrees; the phase scan is periodic; (C) at `d = 2` is
  `ln(1 + c)/c`; (G) random reproduces (C); witnesses independent and
  maximal; (G) and (R) against simulation on the uniform model at
  `n = 8000`; the leaf form). `reports/scratch/beta_plus/recursion.py`: the
  lemma on 1,000 random graphs, all 2,024 accepted item 05 instances
  regenerated from their seeds (`n_ones` and the recorded layer bound
  asserted equal on every one), 180 fresh unpadded uniform-model instances
  (5 per cell at `n = 1000, 5000`), every comparison with relative errors;
  `instances.csv`, `pure.csv`, `beta_plus_table.csv`, `tables.md`,
  `run.log`. 49 s wall on 8 workers at nice 19, 315 s of instance time; no
  solver, `solutions/` and the ledger untouched.
- **`reports/excess_phase_diagram.md` §7**: Lemma L with proof; the
  derivation of (R) from the exact conditional law of the unrevealed
  patterns, its reduction to `G(n, c/n)` at `d = 2`, the configuration
  form, the leaf form, and the phase (the limit of the layer bound per
  customer is a band over the phase, the constant its supremum); the slot
  picture, the invariance of alive degrees, (G) with its phases, (C) with
  the `ln(1 + c)/c` check; why the min-degree greedy and the two-key rule
  are not analysed; the comparison; the `β⁺` table; findings, kill, what it
  does not claim; every table of `tables.md`.
- **Numbers.** Layer lemma: 0 violations on 1,000 graphs (tight on 104) and
  150 more against brute force. Phase-matched, (R) predicts the observed
  layer bound at `n = 5000` to median relative error 0.0029 at `d = 4`,
  0.0007 at `d = 6`, 0.0002 at `d = 8–10` (largest 0.044, 0.009, 0.009),
  0.005 at `d = 3` (0.065); the observed values lie in the phase band on
  314 of 345 instances at `d ≥ 3`, excursions ≤ 0.011, and spread across it
  (within-cell sd 0.04–0.57 of the band's width, median 0.21, against
  0.002–0.003 for the rule): **the BFS layer bound per customer does not
  concentrate; its limit depends on the phase of the exploration.** At
  `d = 2` the fixed generator's padding defeats the marginal form (growth
  factor 1.47 against 1 at `(2, ½)`, a 10% giant predicted where there is
  none) and the leaf form is right (`(2, 1)`: band `[0.335, 0.346]` against
  observed 0.334–0.355). (G) agrees with its greedy to median 0.5% (largest
  3.5%) on the uniform model, 0.8% / 4.1% on the generators at `d ≥ 4`,
  2–6% (over-estimating) on the fixed generator at `d ≤ 3`, the leaves
  again. `β⁺ = min(β⁺_BFS, 1 − α⁺_pc)` on the uniform model: the BFS wins
  at `e ≤ 1`, the greedy from `e = 1.5`; `β⁺ − β*` is 0.080 at `(10, 2)`,
  0.116 at `(8, 2)`, 0.17–0.23 at `(10, 1)`, `(6, 2)`, `(8, 1)`, 0.30–0.33
  at `(4, 2)`, `(6, 1)`, `(10, ½)`, 0.296 at `(2, 1)` and 0.40–0.49 at every
  cell with `1 ≤ e ≤ 3.5` (0.494 at `(4, ½)`), 0 at the degenerate `(2, ½)`
  (no giant component, both constants zero). The analysed greedy is within
  0.022 per customer of item 05's min-degree greedy on the same instances;
  the rule's measured `β⁺` is 0.057 (`(10, 2)`) to 0.36 (`(2, 2)`) below the
  analysed constant on the trusted cells.
- **Kill verdict: not met** — `β⁺ − β* > 0.5` on 0 of 18 cells (largest
  0.494); informative at `e ≥ 14` (gap ≤ 0.12), nearly uninformative on the
  ridge; the gap is attributed to the constructions (finding 3), and no
  further analysis item is proposed. Concentration (Wormald / the
  branching-process coupling) is cited from memory, no held copy, marked
  not verified. No certified value is wrong, no theorem is false, no
  published claim of ours drifts.
- **Literature.** We found no prior statement of (R), (G) or (C) for the
  passive random intersection graph (patterns choosing customers); the held
  Nikoletseas–Raptopoulos–Spirakis (2008) treats greedy independent sets on
  the active model `G_{n,m,p}` and was not used.
- **Gate: PASS** (one run, 2026-11-01 04:07–04:18 at load 0.4–1): lake build
  ok, every file imported, sorry 0, MOSP pytest 1,603 passed (2 skipped,
  1 xfailed; +14 new), pathwidth_solver 123 passed, paper check ok (66
  pages, no undefined references). Log: `Ralph_Loops/loop0010/gate_it07.log`.

### Blockers

None.

### Next

Item 08, the structured count. From this item: `β*` is now bracketed on the
uniform model by a provable `β⁺` that is 0.08 away at `(10, 2)` and 0.4–0.5
on the ridge, so a lift of `β*` by 0.03 at `(6, 1)` (item 08's kill) would
close a tenth of the remaining 0.32 there; the ridge is where both ends are
worst. For item 09: the BFS band is widest on the ridge (0.08–0.10), a
non-concentration that the rule does not share. For item 10: the padding is
a leaf correlation the two marginals cannot express — a uniform-model
statement transfers to the fixed generator within 1% at `d ≥ 4` and only
through the leaves at `d ≤ 3` (§7.6 (6)). For item 11: Lemma L is a small,
self-contained deterministic statement (BFS layers of a `SimpleGraph`, the
layer-by-layer layout, `vs ≤ max (|L_i| + |L_{i+1}|) − 1`) and the natural
third Lean target the plan names. For item 12: the sandwich to state is
`β* ≤ lim inf opt/n ≤ lim sup opt/n ≤ β⁺` with the concentration step
cited, and the phase band is a one-sentence caveat on any BFS-based bound.

---

## Iteration 8 — 2026-11-01 04:28

Item 08, the structured count: can a richer first moment lift `β*`?

### Completed

- **`learning/first_moment.py`, the structured count**: the `ℓ`-nested
  empty-pair structure a width-`k` layout forces at `ℓ` prefix sizes
  (`nested_cells`, `nested_sizes`, `nested_masks`; `ℓ(ℓ+1)/2 + ℓ + 1` cells,
  with the overlaps `δ_{j',i}` of each block with the earlier inactive layers
  — forced by the layout, so the honest count is a sum over `δ`, not the
  item's single multinomial), the per-pattern avoid probability by
  inclusion–exclusion as a Möbius transform over unions of cells
  (`NestedStructure`), the asymptotic exponent with its sup over `δ`
  (`nested_rate_sup`, multi-start SLSQP plus a random cloud; `ℓ = 2`
  against a 4,001-point grid), `β*_ℓ` (`beta_star_nested`; `ℓ = 1` is the
  single-pair scan on the same grid and reproduces `β*` to `1e-12` on all
  36 grid points), the finite bound summed exactly over every integer `δ`
  (`nested_log_bound`, `nested_floors`), the second moment of the
  single-pair count exact in the model (`second_moment_exact`, the `3 × 3`
  overlap table) and asymptotic (`second_moment_rate`), the brute-force
  references (`nested_count_brute`, `empty_pair_count_brute`) and the
  layout-to-structure constructor that asserts the lemma
  (`nested_structure_from_layout`). CLI `python -m learning.first_moment
  nested`. `tests/test_first_moment.py`: 15 new tests (31 in all) — the
  count equals the enumeration at `n ≤ 7` (`ℓ = 2`: 16 cases; `ℓ = 3`: 1),
  60 random layouts force the structure at every position choice (> 200)
  and are refused at `k − 1`, the Möbius transform against its definition,
  the second-moment formula against 2,000 enumerated instances at `n = 10`.
- **`reports/scratch/structured_count/`**: `run.py` (stages `table`,
  `floors`, `second`, `harper`, `slack`), logs and CSVs; `positions_6_1.log`.
  About 1.3 core-hours at nice 19, load 0.1–2; nothing solved, `solutions/`
  not read, the 650 record instances regenerated from their seeds.
- **`reports/excess_phase_diagram.md` §8**, every table in full.
- **Numbers.** `β*_ℓ` **falls** with `ℓ` on all 15 cells with `β* > 0`:
  `β*_2 − β*` from −0.012 (`(4, ½)`) to −0.055 (`(10, ½)`), −0.051 at
  `(6, 1)` (0.513 → 0.463 → 0.428 → 0.402 for `ℓ = 1..4`); the threshold
  `e = 1` is unchanged. Over a 31 × 31 grid of positions at `ℓ = 2`, no
  pair gives a negative exponent at `β* + 0.005` on any cell, and the
  minimum is always at the pair nearest the balanced single-pair position;
  the degenerate limit `p_2 − p_1 = ε n` approaches the single pair from
  above at `≈ 1.5 ε log(1/ε)` (measured to `ε = 10⁻⁴`): an extra cell of
  `ε n` vertices costs `Θ(ε log(1/ε))` of entropy and buys `Θ(ε)` of
  constraint. For `ℓ = 1` the balanced position is exactly optimal. Finite
  floors on the 200 Chu & Stuckey instances: zero violations at 0.01 for
  every variant (the record's figure reproduced); `ℓ = 2` never above
  `ℓ = 1`, below on 182 (148 with a `±3` position search), 5 stacks below
  at 125 × 125 for `d = 4–8`; the single pair at the exact size `|R| = n −
  p − k` (the Lean statement) is above the old `|R| = t − 1` floor on 105
  of 200 and below on none, half a stack on average, a rounding not a
  structure. Diagnostic: at `(6, 1)`, `n = 125`, `E[X²]/E[X]² = 7 × 10¹⁰`
  at the floor and `e^{0.23 n}` asymptotically at `β*`, the extremal overlap
  being the reversed (or identical) pair — the empty pairs cluster; the
  formula agrees with enumeration at `n = 12–14` (means within 2 se, ratio
  to 1–7% where `X > 0` is common); a fixed pair is empty with probability
  `10⁻⁵²` near the floor, so the item's simulation at 125 is impossible and
  is said so. Harper's bound on 650 certified `(6, 1)` instances at 30–75
  (all complete): `pw − Harper` 0.40–1.24 on average (median 0–1), `Harper
  − floor` 1.0–3.2 and growing with `n`: the necessary condition is tight
  to a stack and the union bound carries the slack. On the five
  `Random-125-125-6` the cap (10–11 in 120 s) stops far below the forced
  pair size (27–38): inconclusive there, reported as such.
- **Kill verdict: met.** `β*_ℓ(6, 1) − β*(6, 1) = −0.051, −0.085, −0.111`
  for `ℓ = 2, 3, 4`, all below 0.03, and no spacing does better; the slack
  is in the union bound by clustering, not in the necessary condition. No
  certified value is wrong, no theorem is false, no published claim of ours
  drifts.
- **Gate: PASS** (one run, 2026-11-01 05:00–05:10 at load 1–2): lake build
  ok, every file imported, sorry 0, MOSP pytest 1,618 passed (2 skipped,
  1 xfailed; +15 new), pathwidth_solver 123 passed, paper check ok (66
  pages, no undefined references). Log: `Ralph_Loops/loop0010/gate_it08.log`.

### Blockers

None.

### Next

Item 09, the ridge hypothesis. From this item: `β*` is the best proved
constant and will stay so under any count that *adds* specified vertices
to the single pair; the finite floor per instance should use the exact-size
single pair (`nested_floors(1, …)`, half a stack better, same zero
violations). For item 12: the sentence on the slack of `β*` is now
measured — the union bound over clustered pairs, not the empty-pair
condition, on certified instances to 75 — and the second moment is the
wrong instrument to repair it; the cluster-representative count is the
open idea, not attempted. For item 11: `nested_structure_from_layout` is
the lemma's constructive content (nesting of inactive suffixes), small and
not proposed for Lean since the count it serves is dead.

---

## Iteration 9 — 2026-11-01 05:20

Item 09, the ridge mechanism: one hypothesis, one test.

### Completed

- **`learning/excess_ridge.py`** (stages `ridge`, `ridge-lattice`,
  `ridge-tables`, `figure-ridge` of `learning.excess`): for §25's 25 series
  at `n ∈ {50, 60, 75}` (9,497 certified instances, 190 cells, through
  `ridge_theory.load_frames` so the node peaks are §25's to the digit) the
  two finite floors per instance from item 02's size histograms, `β*` per
  cell from the pooled histogram, the two gaps, their cell means with
  standard errors, each gap's peak by §25 (b)'s parabola with a bootstrap
  interval over instances, §25 (d)'s score against the node peak and its
  interval, the kill, and the profile shapes; a vectorised lattice over the
  `2^20` closed-customer sets (both edge costs of `learning.degeneracy`,
  equal to it on every edge, minimum and count in the tests) for the
  secondary. `learning/data/excess_ridge_{instances,cells,peaks,lattice}.csv`
  (git-ignored), `reports/scratch/excess_ridge/` (logs, `tables.md`),
  `reports/figures/excess_ridge.png` (reference palette, open markers for
  grid-edge maxima). `tests/test_excess_ridge.py`, 10 tests. H1: 10 s.
  Lattice: 5,400 instances at `n = 20`, 3.44 core-hours (2.3 s per
  instance), 26 min wall on 8 workers at nice 19 — above the item's 2
  core-hours because the idle-machine timing did not hold with 8 workers
  sharing memory bandwidth; all 150 per cell as the item asked, nothing
  sampled. Nothing solved, `solutions/` not read, the ledger untouched.
- **`reports/excess_phase_diagram.md` §9**: method, the per-series table in
  full, the profiles, the lattice per series and per cell, findings, kill,
  what it does not claim.
- **Numbers.** H1: the floor gap's peak lies outside the node peak's
  bootstrap interval on **22 of 25** series, the `β*` gap's on **23 of 25**
  (the kill allows 12); mean scores 0.109 and 0.135 decades (max 0.25);
  signed +0.092 and +0.135 — the gap's maximum sits on the *dense* side of
  the ridge, at excess 2.2–5.3 (floor) and 2.1–4.4 (`β*`) against the
  ridge's 1.8–3.0, and its location is less constant across ratios than the
  excess (CV 0.24 / 0.19 against 0.15), with a residual that changes sign
  between `m ≥ n / 4` (+0.07 to +0.12) and `n / 8` (−0.03). The gap is a
  broad plateau over `e ≈ 2–5`: at the node peak the floor gap is within
  0.000–0.022 per customer of its own maximum on every series (one stack at
  `n = 50`; 0–1.2 se on the Bernoulli series, 0.3–6.6 on the fixed). Its
  height orders the ratios backwards from the ridge's (0.10 at `m = 2n` to
  0.20 at `n / 8`, where the ridge is highest at `2n`). Free audits: zero
  violations of the 0.01 floor on all 9,497 (19 of the bound-below-1
  floor, one stack each but one); the lattice minimum equals the certified
  optimum under both measures on 5,400 of 5,400 at `n = 20` (§8's audit
  reached 15). Secondary: the number of optimal closing orders is
  **monotone increasing in density** on every series (connected instances;
  the sparse Bernoulli dips are disconnected instances multiplying their
  components), Spearman −0.77 to −0.98 with the nodes across cells, −0.54
  to −0.91 per instance; the share of `20!` tracks `opt / n` at 0.69 (0.70
  at `n ≤ 15`); 0 of 5,400 unique up to twins. §36's reachable count on
  the same instances is the only quantity on the table that moves with the
  nodes.
- **Kill verdict: met — H1 is dead** on both readings (interval test failed
  by both; the score test passed by the floor reading alone, 0.109 against
  0.15). A dead H1 is the result. No certified value is wrong, no theorem is
  false, no published claim of ours drifts.
- **Gate: PASS** (one run, 2026-11-01 05:58–06:10 at load 8 while the
  lattice workers were finishing): lake build ok, every file imported,
  sorry 0, MOSP pytest 1,628 passed (2 skipped, 1 xfailed; +10 new),
  pathwidth_solver 123 passed, paper check ok (66 pages, no undefined
  references). Log: `Ralph_Loops/loop0010/gate_it09.log`.

### Blockers

None.

### Next

Item 10, validity under the real generator. From this item, for item 12:
the sentence on the ridge mechanism stays §36's (reachability in the subset
lattice), and the paper should say that the first-moment gap does *not*
locate the ridge — it is a plateau on which the ridge sits, maximal on the
dense shoulder — so the two coincidences on record (gap ≥ 2 concentrated on
the ridge, §6; the ridge at excess 2) are not one fact. For the bound work
(outside this loop): the floor gap's growth as `m / n` falls is where `β*`
is loosest (few, large patterns), which §8 attributed to clustering; the
same ordering should hold for any cluster-representative count. The
vectorised lattice (`lattice_weights`, 2.3 s at `n = 20`) is the tool for
any further `n ≤ 25` lattice question; §36's reachable count could be
re-derived on it in one pass.

---

## Iteration 10 — 2026-11-01 06:19

Item 10, validity under the real generator, on paper.

### Completed

- **`learning/first_moment.py`, the section "validity under the real
  generator"**: the exact pre-repair Bernoulli bound (`lq_bernoulli`,
  `log_bound_bernoulli`), the truncated-size bound for the patterns-first
  pad order (`lq_truncated`, `log_bound_truncated`), a Chernoff quenched
  form on the i.i.d. sizes (`log_bound_quenched`, binned typical set) and
  the best of both (`log_bound_best`, `floors_best`); the generator with
  its auxiliary randomness explicit (`draw_aux`, `pad_customers_with_aux`,
  `pad_patterns_with_aux`, `pad_with_aux` in both orders, the dominating
  `unconditional_pad`, `no_repair_needed`, `generator_draw`,
  `generator_event_rates`, `wilson`); the closed-form cut and repair
  union bounds; `rejection_floors` with the five rigorous forms; a subset
  DP for exact vertex separation for the checks. `tests/test_first_moment.py`:
  13 new tests (44 in all) — the binomial-average identity exactly in
  rationals, the pair probability and both union bounds against full
  enumeration, the pads only add and are dominated, the truncated row law
  by chi-square, empty-pair inclusion and pathwidth monotonicity on 60
  draws against `compute_pathwidth`, the explicit non-monotone example,
  the quenched bound against the exact `P(pw ≤ k)` over all `2^15` base
  matrices at `3 × 5` and the Chernoff tail against the exact size-sum
  distribution, the floors' ordering.
- **`reports/scratch/validity/`**: `check.py` (stages `exact`, `law`,
  `coupling`, `classes`, `table`), `check.log`, `classes.csv`,
  `floors.csv`, `tables.md`, stdout logs. Every lemma checked before it
  was stated: 205 rational identities; two full enumerations; the coupling
  on 40,000 draws at `n = m = 8` (`M ≥ B`, `M ≤ M⁺`, every empty pair of
  `G_M` empty in `G_B`, `pw(G_B) ≤ pw(G_M)` in every draw); the
  non-monotonicity counted over 320,000 single-entry increases of the
  base; the event rates on the 40 classes in both pad orders. About 0.1
  core-hours at nice 19, load 0.2–1. Nothing solved; `solutions/` read
  only; the ledger untouched.
- **`reports/excess_phase_diagram.md` §10**: the generator with explicit
  randomness, six statements with proofs (V1 exact bound; V2 coupling; V3
  the first moment survives the pads, Bernoulli sizes in both orders and
  truncated sizes patterns-first; V3′ quenched; V4 the repair map is not
  monotone; V5 the rejection in five rigorous forms; V6 monotone in the
  density), the checks, the numerical consequence, findings, the paper's
  sentence, kill verdict, what it does not claim, every table in full.
- **The paper**: the last paragraph of Appendix E's generator subsection
  (`sec9e_appendix_random.tex`) now says what is proved (the pre-repair
  bound by coupling, the truncated and quenched forms, the rejection at
  `1 / P(accepted)` with the measured acceptances, the proved floors'
  distance from the table and why) and what stays measured; the
  "a proof would couple…" sentence is gone. PDF rebuilt.
- **Numbers.** Acceptance (fitted order, measured): 0.87 → 0.56 on the
  square `d = 2` classes from 30 to 125, 0.0049 at `(100, 50, 2)` (291 of
  60,000 draws), 0.77 at `(100, 50, 4)`, ≥ 0.99 elsewhere; `P(M⁺
  connected) = 1.000` everywhere, so the Harris form on the unconditional
  pad is the trivial form; the no-repair event keeps a 0.01 floor on 2
  classes of 40. The acceptance factor moves no 0.01 floor on any class.
  Non-monotonicity at `n = 8`, `d = 2`: a pad vanishes on 40.5% of
  single-entry additions, the acceptance is lost on 0.72%, the padded
  pathwidth falls on 3.5%; `M⁺` and `G_B` are monotone on every one. The
  proved 0.01 floors (best form, with the rejection) differ from the
  measured-model floors by more than one stack on 35 of 40 classes
  (Bernoulli sizes) and 34 (truncated): trivial at `d = 2` in the
  Bernoulli form, 3–13 truncated; 2–13 stacks short at `d = 4–6`
  (`(125, 125, 4)`: 30 / 32 against 42.4; `(125, 125, 6)`: 60 / 62 against
  69.6); 0–5 at `d ≥ 8`. The decomposition (annealed → per-instance floor
  at simulated binomial sizes → realised) puts the price at the pads at
  `d = 2` (1 → 3.4 → 13.6 at 125 × 125; truncated 6 → 10.4) and at the
  annealing at `d ≥ 4` (26 → 39.8 → 42.4); the quenched form recovers 2–4
  stacks of the latter at 0.01 and 4–10 at the `< 1` level. At nominal
  sizes `(100, 50, 2)` has excess 0.5, below the threshold: its measured
  floor is entirely the pads' 74% extra ones. At `1.10 d / n` the floors
  rise 2–6 stacks on the large classes, and V6 makes the quoted floors
  valid for any density at or above `d / n`. 0 of 200 certified optima
  below any rigorous floor (smallest margin one stack).
- **Kill verdict: the fallback is the result.** Harris–FKG applies to the
  unconditional pad, the no-repair event, the base graph and the paper's
  own generator, and not to the fitted generator's acceptance (V4); the
  item ends with the `1 / P(accepted)` form and the measured acceptance,
  as the criterion allows. No certified value is wrong, no theorem is
  false, no published claim of ours drifts (one sentence replaced by what
  is proved, as item 12 planned).
- **Gate: PASS** (one run, 2026-11-01 06:51–07:01 at load 0.5–2): lake build
  ok, every file imported, sorry 0, MOSP pytest 1,641 passed (2 skipped,
  1 xfailed; +13 new), pathwidth_solver 123 passed, paper check ok (67
  pages, up from 66 with the rewritten paragraph; no undefined references).
  Log: `Ralph_Loops/loop0010/gate_it10.log`.

### Blockers

None.

### Next

Item 11, Lean. From this item: the coupling inclusion the plan names as the
first Lean target is Lemma V2 (ii) — a pattern that meets both sides of a
pair in the base meets both in any superset matrix, so an empty pair of the
superset's graph is one of the base's; stated over `coverInstance`-style
matrices with `M ≤ M'` entrywise, it is two lines on top of
`isEmptyPair_coverGraph_iff`, and `pathwidth` monotone under `SimpleGraph`
subgraph inclusion is the other half (Mathlib may lack a direct lemma;
`PathDecomposition` restricts trivially). The Bernoulli product formula
(V1) is a probability statement and is not proposed for Lean. For item 12:
Appendix E's paragraph is already replaced (§10.7); the paper should quote
the proved floors as "pre-repair sizes, fitted generator at `p = d / n`",
never the realised-size ones as theorems; the sentence on `(100, 50, 2)`
(no first-moment floor at nominal sizes, the pads change its regime) is
worth one line. For the bound work: a sharper tail than Chernoff on the
size sum (the exact distribution is computable) would move the quenched
floor toward the typical instance, up to 10 stacks at `(125, 125, 4)`.
