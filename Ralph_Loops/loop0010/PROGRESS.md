# loop0010 progress

Plan: `reports/excess_phase_plan.md` — a one-parameter theory of MOSP in the
excess `e = (n_ones − m) / n`; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0010/gate.py`.

Current: 5/13 SOLVED

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
