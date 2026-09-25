# Progress Log

## Ralph Loop 0001 Status
- **Started**: 2026-09-25
- **Target**: 8 items
- **Current**: 5/8 SOLVED

---

## Iteration 1 — 2026-09-25 19:15

Item 01 · §2.1a Isomorphism classes. **SOLVED.**

### Completed
- `learning/canonical.py`: three canonical forms per instance (matrix digest,
  nauty certificate of the two-coloured bipartite graph, nauty certificate of
  the MOSP graph) plus the networkx WL hash and |Aut(G)|; pynauty behind a soft
  import, WL-only fallback. Class tables per collection, per (n, m), per size
  band, cross-collection duplicates, largest classes, WL-vs-nauty, and the
  equal-optima audit with an optional `--recertify` follow-up. Runs in under a
  second on 16 cores. Writes `learning/data/canonical.csv` (git-ignored, regenerable).
- `tests/test_canonical.py`: 7 tests on hand-checkable 3-customer instances
  (permutation invariance, matrix-vs-graph separation, the coloured bipartite
  certificate not mapping customers to products, the audit firing on a
  planted wrong optimum, class counts). Full suite: 703 passed, 2 skipped,
  1 xfailed, 66 s.
- `reports/ml_nature.md` created, §1 written; `reports/canonical_tables.md`
  is the raw regenerated output. `pynauty` added to `learning/requirements.txt`
  as optional.
- Findings: 6,376 instances are 3,667 distinct MOSP graphs (42.5% redundant);
  1,669 (26.2%) are complete graphs with optimum n, all from Harvey and
  Simonis; `MOSP_Instances/Challenge` is a byte-for-byte (44) or
  zero-column-removed (2) copy of the Miller/Shaw/Wilson files, so all 46 are
  certified twice under two names; 157 graph classes span more than one file,
  so grouping by `source_file` leaks isomorphic copies across the split; WL
  loses 14 of 3,667 classes, all sparse optimum-3 Harvey instances; the audit
  found zero optimum disagreements, so nothing was re-certified and nothing
  was written to `solutions/`.

### Blockers
None.

### Next
- Item 02 (§2.1b generator fingerprint and instance-space map). It should
  group by `graph_cert` from `learning/data/canonical.csv`, or take one
  representative per class, rather than by `source_file` alone; §1 shows the
  file grouping leaks. The same applies to any study re-quoting the grouped
  numbers in `reports/learning.md`.
- The 150 graph classes with several matrix classes are ready-made pairs for
  §2.9 (same graph, different clique cover).

## Iteration 2 — 2026-09-25 20:05

Item 02 · §2.1b Generator fingerprint and instance-space map. **SOLVED.**

### Completed
- `learning/fingerprint.py`: random-forest classifier of the sub-collection
  from the 28 structure-only features and from a 19-column size-free set,
  under three splits (grouped by file, grouped by file ∪ MOSP-graph class via
  `learning/data/canonical.csv`, random for contrast), with the majority and
  size-only baselines and the accuracy ceiling set by cross-labelled
  isomorphism classes; a same-(n, m) test over the eleven shared size cells;
  the Chu & Stuckey density class and a seed-index control; permutation
  importance and a depth-3 readable tree; UMAP (soft import, PCA fallback) map
  saved as `reports/figures/instance_space.png` with 10-NN purity and k-means
  region composition. ~50 s on 16 cores. Writes `learning/data/instance_space.csv`
  (git-ignored) and `reports/fingerprint_tables.md`.
- `tests/test_fingerprint.py`: 7 tests on hand-checkable frames (size-free
  transform, union grouping, ceiling arithmetic, grouped classifier on a
  separable toy plus refusal of an ungrouped call, PCA fallback and purity).
  Full suite: 710 passed, 2 skipped, 1 xfailed, 72 s.
- `reports/ml_nature.md` §2 written; `umap-learn` added to
  `learning/requirements.txt` as optional.
- Findings: 94.4% of instances are assigned to their collection from structure
  alone with the file held out (93.3% with isomorphic copies held out; 98.8%
  at equal size against a 61.6% baseline); size alone is below the majority
  class under a grouped split, and the size-free features do as well as the
  full set, so the fingerprint is not size. It is readable: every Harvey
  instance has constant column sums (`wbo`), constant row sums (`wbp`) or
  both (`wbop`) and no other generator has either; Faggioli–Bentivoglio's
  largest product covers ≤ half the customers; Simonis is dense with large
  products; Chu & Stuckey is sparse where nothing else is, and within it
  `col_mean` alone recovers the density class at 98% while the seed index
  sits at chance. Shaw, Miller, Wilson and the Challenge copies cannot be
  fingerprinted because they are one file or one size each; their copies set
  a ceiling of 0.993 the model hits exactly. The map is a lattice of 74 (n, m)
  cells, not a continuum; the 24 SCOOP industrial instances have almost no
  SCOOP neighbours and fall in the sparse region shared with all 200 Chu &
  Stuckey instances.
- Two method notes worth keeping: `HistGradientBoostingClassifier` scored
  0.81 on a random split where a forest and LightGBM score 0.98 (thrown by
  the one- and twenty-instance classes); and unshuffled `GroupKFold` on the
  Chu & Stuckey files put each seed index in its own fold, making the control
  score exactly 0. Both are documented in the module.

### Blockers
None.

### Next
- Item 03 (node counts into the ledger), the §2.4 prerequisite.
- For §2.2 onwards: any grouped split should use the file ∪ graph-class
  grouping now implemented as `learning.fingerprint.union_groups` (512 groups),
  and any transfer claim should be stated per collection, since §2 shows the
  collections are separable regions; SCOOP is the only collection whose
  neighbours are other collections, so it is the natural held-out test for
  "does this transfer to real instances".

## Iteration 3 — 2026-09-25 19:40

Item 03 · §2.4 prerequisite Node counts into the ledger. **SOLVED.**

### Completed
- The search was already returning its count (`Decision.nodes`,
  `Solution.nodes`, from both the Python and the C path); every seam above it
  dropped it. Now: `solve_mosp_exact(..., stats=dict)` fills `nodes`,
  `seconds`, `proof`, `procedure` with the return value unchanged (`nodes` is
  `None`, not 0, for cached and SAT answers); `benchmarks.compute.record`
  writes a fifth column `nodes` and accepts 2- or 3-tuples, with
  `ensure_fields` migrating an older ledger in place once (`--migrate-ledger`);
  `benchmarks.csearch` posts and records `result.nodes` as a sixth row field
  (first five unchanged, which is what `marathon` indexes); `benchmarks.recertify`
  appends a ledger row per finished entry as it lands (`--ledger`).
- `benchmarks/results/compute_ledger.csv` migrated: header gains `nodes`, all
  279 existing rows have an empty value, compute total unchanged (667 core-hours).
- `learning/node_counts.py`: summarises the ledger's `nodes` column per driver
  and refutes `optimum - 1` for every certified instance with n ≤ 40 under the
  two configurations whose counts reach the ledger. Writes
  `learning/data/node_counts.csv` (git-ignored) and `reports/node_count_tables.md`.
  About 1 s on 16 workers.
- `tests/test_node_counts.py`: 7 tests. A hand-checkable 7-customer spider tree
  (optimum 3, trivial bound 2) refutes k = 2 with a positive count, equal on the
  Python and C paths; `solve_mosp_exact` stats on the 9×10 Faggioli–Bentivoglio
  instance `p1010n10_0` (bound 5, optimum 6); ledger write/migration; csearch
  sweep row and ledger; recertify worker and row; the study module's audit and
  summary. Full suite: 717 passed, 2 skipped, 1 xfailed, 74 s.
- `reports/ml_nature.md` §3 written.
- Findings: all 12,270 calls (6,135 instances × 2 configurations) return
  `unsat` at `optimum - 1`, a second independent refutation of 96% of the
  corpus; 38.5% of them refute at the root with zero nodes (53.7% at n ≤ 10),
  almost all Challenge instances; the tail grows roughly 10× per ten customers
  (p90 4 → 23 → 108 → 1,764); the worst call is 29,138 nodes on
  `Random-40-40-2-2_0`, and over the fifty Random-30/40 instances median nodes
  fall monotonically with density (1,068 → 6 from density 2 to 10). The
  csearch configuration is never more than 1.1× the defaults.

### Blockers
None. Note: the running `benchmarks.recertify` (started before this iteration)
was not restarted, so its rows will not reach the ledger; its counts are in
`recertify/results.json`.

### Next
- Item 04 (§2.2a pathwidth-adjacent invariants). Use
  `learning.fingerprint.union_groups` for the grouped split.
- For §2.4 proper (next loop): `learning.node_counts.refute` is the per-call
  primitive to reuse; record `config` per row as it does; dedupe by
  `graph_cert` from `learning/data/canonical.csv`; the small-corpus signal
  says the density peak, if any, is at or below Chu & Stuckey density 2 at
  n = 30–40, so the sweep should extend below it.

## Iteration 4 — 2026-09-25 20:05

Item 04 · §2.2a Pathwidth-adjacent invariants as features. **SOLVED.**

### Completed
- `learning/features.py`: fourth group `invariants`, 13 columns — min-fill
  and min-degree elimination widths (`tw_min_fill`, `tw_min_degree`), reverse
  Cuthill–McKee bandwidth (`bw_rcm`), spectral radius, Fiedler value (whole
  graph and largest component), two edge clique cover counts (`cc_products`,
  the distinct products containing an edge, and `cc_greedy` after dropping
  products every edge of which another covers), a balanced separator from
  Fiedler and RCM sweeps (`sep_size`, `sep_frac`), and the random
  intersection quantities (`rig_edge_prob = 1 − (1 − p̂²)^m`,
  `rig_deg_expected`, `rig_density_ratio`); `p̂`, `n`, `m` are the existing
  `density`, `n_customers`, `n_patterns` and were not duplicated. The greedy
  invariants run on a copy relabelled by a label-free key so tie-breaks do
  not depend on the file's row order. `DEFAULT_GROUPS` and `invariant_names`
  exported; `learning.dataset` builds 49 features by default (54 columns,
  ~90 s on 16 cores); `learning.study_optimum` and `learning.fingerprint`
  leave the group out by default so `reports/learning.md` §1 and
  `reports/ml_nature.md` §2 regenerate from the columns they report.
- `learning/invariants_study.py`: point estimates (each invariant + 1 against
  the optimum, with below/above counts, per size band), the four-set ablation
  under three splits on the optimum and on the residual, by-band ablation,
  permutation importance of all 49 on held-out file ∪ class groups (both
  targets), each invariant alone with the sizes, and a shuffle check of
  order-dependence on 623 instances. ~140 s on 16 workers. Writes
  `reports/invariants_tables.md`.
- `tests/test_invariants.py`: 11 tests on P4, K4 and an over-covered
  triangle (hand-checked widths, bandwidth, golden-ratio spectral radius,
  `2 − √2` Fiedler value, clique cover counts, separator sizes, RIG
  arithmetic), permutation invariance of the exact invariants, the
  bound-violation counter, and the shuffle check. Full suite: 728 passed,
  2 skipped, 1 xfailed, 79 s.
- `reports/ml_nature.md` §4 written. No new dependencies (networkx's
  treewidth heuristics, numpy eigensolvers).
- Findings: `tw_min_fill + 1` is a closer point estimate of the optimum than
  either solver bound — exact on 85.7% vs 84.6% (`ub_best`) and 77.0%
  (`lb_best`), MAE 0.188 vs 0.239/0.431, leading in every size band including
  61–134 customers — and a bound on nothing (481 below by ≤ 3, 428 above by
  ≤ 7). It is the top feature of all 49 (2.01 MAE points, above `ub_cs_dfs`
  1.21). Structure + invariants with no solver bound predicts the optimum as
  well as structure + bounds did (grouped-by-file MAE 0.436 → 0.220, exact
  71.2% → 87.1%; kill criterion 0.02 cleared 10×). On the residual
  `optimum − lb_best` the group adds nothing (−0.004 / −0.000 / −0.009 MAE):
  the invariants know what the bound knows, not what it misses. The residual
  correlates with random-model sparsity (`rig_edge_prob` ρ = −0.52,
  `sep_frac` −0.42, `fiedler` −0.32). `bw_rcm + 1 ≥ optimum` on all 6,376,
  as bandwidth ≥ pathwidth requires. The label-free relabelling leaves the
  treewidth heuristics and separator unchanged on all 623 shuffles; `bw_rcm`
  changed once, `cc_greedy` on 26 (by ≤ 2), and it carries no importance.
- Two notes on record: the rebuilt table's `lb_best` includes the expansion
  bound (higher on 1,329 rows than the September 22 table) and carries the
  corrected optimum for `Random-100-100-2-2_0`, so the `lb_best` baseline is
  now MAE 0.431 rather than the 0.979 in `reports/learning.md` §1 — the old
  CSV was stale, not the code. And the file ∪ class grouping is a five-region
  hold-out in practice (largest group 1,620 instances, top five 88%), which
  is why its absolute errors are several times the file-grouped ones.

### Blockers
None.

### Next
- Item 05 (§2.2b, a formula for the residual). Aim at `optimum − lb_best`;
  leave `tw_min_fill`, `tw_min_degree` and `lb_*` out of the formula search
  since §4 shows they track the bound, not the gap. Candidates with signal on
  the gap: `rig_edge_prob`, `sep_frac`, `fiedler`, `cc_greedy`, `bw_rcm`,
  `density`. A formula for the *optimum* should be compared against
  `tw_min_fill + 1` as the point-estimate baseline, not only against LightGBM.
- For §2.3: the residual's correlates all point at sparse, weakly connected
  graphs; start the gap-vs-tight classifier from `rig_edge_prob` and
  `sep_frac`.
- `pysr` is not installed; the enumerated fallback is the path unless it is
  added to `learning/requirements.txt` as optional.

## Iteration 5 — 2026-09-25 20:09:14
### Completed
- (driver) session ended with outcome `error` without marking the item
### Blockers
- see session_it05.log
### Next
- revisit or re-open this item

---

## Iteration 6 — 2026-09-25 20:20:06
### Completed
- (driver) session ended with outcome `ok` without marking the item
### Blockers
- see session_it06.log
### Next
- revisit or re-open this item

---
## Iteration 7 — 2026-09-25 21:25

Item 05 · §2.2b A formula for the residual. **SOLVED.** (Iteration 5 wrote
`learning/formula_search.py` and its tests, then killed its own shell with a
bare `pkill -f`; the iteration numbered 7 before this one worked on item 07
and errored. This iteration finished item 05 on the committed code.)

### Completed
- `learning/formula_search.py`, built on iteration 5's module: enumerated
  search over 58,221 / 68,690 monomials of ≤ 3 features (LAD constants after
  an OLS first pass), pair stage, nested protocol, LightGBM baseline, PySR on
  a held-out fifth of the files, plus a new **sandwich table** with constants
  fixed by hand (`g_degeneracy + 1`, `bw_rcm + 1`, their geometric and
  arithmetic means, the distribution of the optimum's position λ between
  them, the gap on degree-regular graphs). PySR now runs in a child process
  (`--pysr-child`, internal) with one retry, bounded by iterations on
  `--pysr-threads 4` (default 2,000): PySR 2.5 / Julia on this machine
  crashed in the garbage collector on six of seven fits at 16 threads and
  10,000 iterations, in-process or in a child, on or off the wall-clock stop
  path; every fit at 4 threads / 2,000 iterations finished. The tables above
  PySR are flushed to `--out` before it starts. Full run 400 s on 16 workers;
  writes `reports/formula_tables.md`.
- `tests/test_formula_search.py`: 13 tests (iteration 5's ten, plus the
  sandwich table on a four-row hand-computed frame, a planted bound
  violation, and the PySR child's failure path, which fails before Julia
  boots). Full suite: see below.
- `reports/ml_nature.md` §5 written; `pysr` added to
  `learning/requirements.txt` as optional.
- Findings: no clean formula for the residual — the best is
  `0.01 · g_deg_std · sep_size / g_density − 0.02`, grouped MAE 0.303 (0.304
  nested) vs 0.431 for the constant zero and 0.260 for LightGBM; with
  `g_density = g_deg_mean / (n − 1)` it reads `(n − 1) · sep_size · σ_deg / μ_deg`,
  so the residual's variable is degree dispersion, and on the 1,705
  degree-regular graphs (complete graphs, Harvey's unions of cycles, one
  Miller graph) the gap is zero every time, which is a triviality, so no
  conjecture is stated. For the optimum the clean formulas exist and both
  searches agree: `tw_min_fill + 1` (MAE 0.188, constants exactly 1 and 1)
  and, from structure alone, `1 + sqrt(g_degeneracy · bw_rcm)` (0.672, exact
  67.1%, constants exactly 1 and 1, chosen in all five outer folds, and PySR's
  own pick too): the geometric mean of a proved lower bound and a proved upper
  bound. `degeneracy + 1 ≤ optimum ≤ bw_rcm + 1` holds on all 6,376 (a
  consistency check against two theorems), the two coincide and force the
  optimum on 2,823, and where they differ λ has median ½ and IQR ⅓–⅔ in
  every size band, tracking sparsity (Spearman 0.40 with `sep_frac`) and not
  size (0.05). PySR beats boosting only on the residual on the held-out files
  (0.235 vs 0.276, selected on the test rows), again with `g_deg_std` times
  a sparsity term. None of it is a bound: the geometric mean is below the
  optimum on 1,495 instances and above on 600, and worse than `lb_best` at
  61–134 customers; `g_degeneracy + 1` is dominated by the contraction
  degeneracy the solver already uses, so nothing goes to the bound work.

### Blockers
None. Nothing written to `solutions/`; no solver file touched; the running
`benchmarks.recertify` was not touched (its 12 processes were counted before
and after every process kill in this session).

### Next
- Item 06 (§2.3 where the bounds fail): iteration 6 left `learning/bound_gap.py`
  and `tests/test_bound_gap.py` committed with a `reports/bound_gap_tables.md`
  run but no report section; read PROGRESS.md's iteration 6 entry and
  `session_it06.log` first. §5 says the classifier should start from
  `g_deg_std / g_deg_mean` and `sep_size` beside `rig_edge_prob` and `sep_frac`.
- Item 07 (§2.6a): an earlier iteration 7 left `learning/distil.py`; check
  its state before rebuilding.
- For §2.5 next loop: the sandwich `g_degeneracy + 1 ≤ optimum ≤ bw_rcm + 1`
  is the frame; the question is whether λ concentrates at ½ on `G(n, m, p)`.
- PySR caveat for any later symbolic-regression item: keep 4 threads and an
  iteration bound; do not rely on `timeout_in_seconds`.

---

