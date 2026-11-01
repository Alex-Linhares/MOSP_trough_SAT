# loop0010 progress

Plan: `reports/excess_phase_plan.md` — a one-parameter theory of MOSP in the
excess `e = (n_ones − m) / n`; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0010/gate.py`.

Current: 3/13 SOLVED

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
