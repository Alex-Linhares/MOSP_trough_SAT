# Progress Log

## Ralph Loop 0002 Status
- **Started**: 2026-09-26 06:18
- **Target**: 6 items
- **Current**: 6/6 SOLVED

---

## Iteration 1 — 2026-09-26 06:33

Item 01 · Campaign infrastructure and pilot. Report: `reports/ml_nature.md` §9.

### Completed
- `learning/ensemble.py`: cells `(generator, n, m, param)` under both generators
  (Bernoulli `p`, Chu & Stuckey fixed `d`); seed = CRC of cell id and index, so
  every instance regenerates byte for byte from `manifest.csv` (all 8,000
  verified, 0 mismatches). Per instance: optimum and proof kind, witness
  re-simulation, nodes/seconds/status to refute `optimum − 1` under both
  `node_counts` configurations, all 49 features, `learning.canonical`
  certificates, `complete_graph`, `g_components` kept (not discarded). One CSV
  row per instance, resumable, appends as it goes. `.gitignore` now un-ignores
  `learning/data/ensemble/` (8.2 MB: results.csv, manifest.csv, 8,000 witnesses).
- Pilot as specified (36 cells × 10) took 12 s, so it was extended to m = 2n,
  p = 0.025 and 100 per cell: 80 cells, 8,000 instances, 126 s on 16 workers,
  1,669 core-s. Audit clean: every witness re-simulates, every `optimum − 1`
  refutes under both configurations, 536 complete graphs all with optimum n.
- Cost finding: refutation is 0.7% of the time; seconds are a function of n
  (0.006 s at n=10 → 0.5 s at n=40, bounds + features), nodes of density.
  Item 02's named grid costs 31.6 core-s per instance-in-every-cell → 3,188
  per cell affordable; storage (~1 KB per instance) binds instead.
- Chosen grid for item 02: n ∈ {10,15,20,25,30,35,40}, m ∈ {n,2n}, d 2–10,
  p ∈ {0.025,…,0.5}, 252 cells × 150 = 37,800 instances (8,000 reused), ~6 min
  wall, ~40 MB; run with the default manifest store, not `--write-instances`.
- Tests: `tests/test_ensemble.py` (6): byte-for-byte regeneration through the
  `.mosp` round trip, fixed-d column sums, hand-checked 4×4 instance (optimum 2,
  positive node count both configs, 3 components), resumability + duplicate
  cell handling, manifest verification. Full suite: 782 passed, 2 skipped,
  1 xfailed, 75 s.

### Blockers
- None. `benchmarks.recertify` was running with 9 workers throughout; this
  iteration used 16.

### Next
- Item 02: run the chosen grid with `python -m learning.ensemble --cells …`
  (or add an `--item02` flag building `item02_cells()` with n = 35 and
  150 per cell), then the descriptive tables §10 asks for. Previews the
  pilot gives items 03/04 (node-count peak at d=3 / p=0.1 for m=n, moving
  lower for m=2n; CV ≤ 0.19 everywhere) are in §9 labelled as previews.
- Note for item 03: use `col_mean`, not nominal `d`, as density — the fixed-d
  generator's empty-row repair adds 0.12 to `col_mean` at d=2, m=n.

## Iteration 2 — 2026-09-26 06:55

Item 02 · The campaign. Report: `reports/ml_nature.md` §10.

### Completed
- Ran the grid §9 chose in full, no shortfall: `n ∈ {10,15,20,25,30,35,40}`,
  `m ∈ {n, 2n}`, `d ∈ {2..10}` (d ≤ n), `p ∈ {0.025,…,0.5}`; 252 cells × 150
  = 37,800 instances, 8,000 pilot rows reused (same cells, same seeds),
  29,800 new in 382 s wall on 16 workers (`recertify` held 9 cores). Total
  2.16 core-hours, 508 s wall including the pilot.
- Audit clean: 37,800 witnesses re-simulate; `optimum − 1` refutes under both
  configurations on 37,794 (+6 with optimum 1); 0 `sat`, 0 deadlines; all
  37,800 manifest digests regenerate; node counts reproduced exactly on a
  fresh re-refutation of 400 sampled instances, both configurations.
- Descriptive tables in §10 and in full in `reports/ensemble_tables.md`:
  by size (cells, instances, classes, complete, decomposable, core-s), dedupe
  per n, and per cell as density × n matrices of classes/instances, complete
  share, decomposable share. 6,511 complete graphs (17.2%, all optimum n),
  7,101 decomposable (18.8%), 10,479 isomorphic repeats within cells (27.7%,
  86.5% in cells containing a complete graph). 145 of 252 cells have < 10%
  complete and < 50% decomposable: 21,750 instances, 20,652 classes.
- Code: `--item02` flag (150 per cell unless `--per-cell`), `campaign_summary`,
  `density_matrix`, `campaign_tables` in `learning/ensemble.py`; two new tests
  in `tests/test_ensemble.py` (grid is the §9 grid and a superset of the pilot;
  tables on a tiny frame where d = 5 of n = 6 is one complete class with
  optimum 6). Full suite: 784 passed, 2 skipped, 1 xfailed, 76 s.
- Artifact `learning/data/ensemble/`: results.csv 17.5 MB, 37,800 witnesses
  19.4 MB, manifest 3.6 MB = 40.6 MB, under the ~50 MB ceiling; no `.mosp`
  files. Nothing written to `solutions/`.

### Blockers
- None.

### Next
- Item 03 (§2.4 phase transition): use `nodes_default`/`nodes_csearch` from
  `learning/data/ensemble/results.csv`, `col_mean` as density (not nominal d,
  §9), dedupe with `learning.ensemble.dedupe`; the 145 "useful" cells are
  where a peak can be resolved without edge effects, but keep the edges in
  the plot. Place Chu & Stuckey's `Random-n-m-d` classes using the corpus
  node counts from `learning/data/node_counts.csv`.
- Method note for anyone timing anything: seconds at n = 40 doubled between
  the pilot and the campaign on identical instances (0.50 → 1.18 s median)
  while node counts were reproduced exactly; use nodes.

## Iteration 3 — 2026-09-26 07:15

Item 03 · §2.4 Is there a phase transition in hardness? Report:
`reports/ml_nature.md` §11; figure `reports/figures/hardness_map.png`; all
tables in `reports/hardness_map_tables.md` (+ `_csearch`, `_default_class`).

### Completed
- `learning/hardness_map.py` (3 s on the 37,800-row campaign): per-cell node
  statistics with `col_mean` as density; peak per `(generator, m/n, n)` with
  bootstrap CIs on the ratio to each neighbour; monotonicity test (the kill's
  literal premise); peak width at half and tenth height; exponential vs
  power-law scaling along the ridge and at fixed parameter; order-parameter
  tests (collapse at fixed n, constancy of the peak location by cell and
  grid-free); Chu & Stuckey's Random-30/40 classes placed on the map
  (connected-only cells too); the five 125×125 recertify counts listed for
  item 06. `--config csearch` and `--per-class` variants written and compared.
- **Kill not met.** Interior peak at every n ≥ 15 in fixed m=n (d=3) and both
  Bernoulli series; only fixed m=2n is monotone, because its grid stops at
  d=2 where Bernoulli m=2n puts the peak (col_mean 1.9–2.1) with an 18–26×
  fall below it. Peak sharpens (half-width 0.30 → 0.14–0.19 log10 col_mean,
  n 20 → 40). Ridge: exponential, doubling every 2.9–3.5 customers,
  power law 5–10× worse; off-ridge at fixed density still exponential,
  doubling every 4.5–4.9. Order parameter: `optimum/n ≈ 0.3` is the most
  constant peak location (CV 0.12–0.14) across generators and m/n;
  `g_deg_mean` collapses the height best (r² 0.926 of 0.949) but its peak
  drifts; `col_mean` is 3.0 at m=n and 2.0 at m=2n. Chu & Stuckey's
  "density 2" has col_mean 2.7–2.8 and sits in the peak cell (d=3) at n=30
  and 40 (46th/71st percentile of the cell); density 4 is the dense shoulder.
  Per-class and csearch results identical in peak location at n ≥ 25.
- Pre-registered for item 06: ridge extrapolation ≈ 5 × 10¹¹ nodes at
  n = 125 against recorded 4.9 × 10¹⁰ – 2.6 × 10¹¹; and if `optimum/n` is the
  order parameter the 125×125 peak is on the density-4 side of density 2.
- Tests: `tests/test_hardness_map.py` (7) on a synthetic campaign with a
  known peak, width, rate and order parameter. Full suite: 791 passed,
  2 skipped, 1 xfailed, 79 s. Nothing written to `solutions/`; no solver
  default changed.

### Blockers
- None. `benchmarks.recertify` was running with 9 workers; this iteration
  used one core.

### Next
- Item 04 (§2.5 concentration): `learning.hardness_map.cell_table` and
  `load` give the per-cell frame; CV of the optimum per cell, formula for
  `E[opt](n, m, p)`. Note from §11 that `optimum/n ≈ 0.3` marks the hardness
  peak, so the concentration study should report CV on and off the ridge.
- Item 06 will want the ridge fit (`scaling`, `fit_scaling`) and the
  `large_counts` table; the recertify counts are under `better_move=True`, a
  third configuration — say so when comparing.

## Iteration 4 — 2026-09-26 08:05

Item 04 · §2.5 Does the optimum concentrate? Report: `reports/ml_nature.md`
§12; figure `reports/figures/concentration.png`; all tables in
`reports/concentration_tables.md` (+ `_class`).

### Completed
- `learning/concentration.py` (6 s; ~30 s with the nested search): per-cell
  mean/variance/std/CV and modal share of the optimum, raw and per class;
  kill verdict; CV and std against n as power laws at fixed parameter, with
  the regime (sub / critical / super / complete) read from the *realised*
  largest-component fraction; E[opt] against n as line and power law; slope
  against nominal degree; `formula_search`'s enumerated search over the
  generator parameters alone (n, m, p, d, k, q, D) on the 252 cell means
  with leave-one-size-out folds, nested, and a `n ≤ 30 → 35, 40`
  extrapolation; five hand-written structural forms fitted by LAD; §5's
  sandwich on the ensemble with λ by n, density and series; the bracket
  `optimum − tw_min_fill − 1 ≤ pw − tw ≤ optimum − g_degeneracy − 1`.
- **Kill not met.** Max CV at n = 40 is 0.197 (median 0.031); the 32 cells
  above 0.2 are all Bernoulli at or below the giant-component threshold
  (31 of 32 with largest component < 0.95 n), mean optimum 2.3–7.6 and a
  flat std of 0.7–0.9. Above the threshold std is ≤ 1 stack at n ≤ 40 and
  grows between constant and √n at fixed degree; a cell is still 2–3
  adjacent integers (mode share 37–60%).
- E[opt] linear in n above the threshold (r² ≥ 0.999 in all 17 fixed-degree
  series), γ ≈ ⅓ below it; slope a function of nominal degree D alone across
  both m/n. Formula: `E[opt] ≈ 2.1(1 − q) + n[1 − √(1 − q)·27/(D + 27)]`,
  q = 1 − (1 − p²)^m, D = (n − 1)q: held-out-n MAE 0.49 on cell means (0.46
  with the exponent fitted, 0.56 per class), 0.66 extrapolated from n ≤ 30,
  per-instance MAE 0.80 (below on 9,445, above on 10,641, max 6 each way;
  cell-mean ceiling 0.60). The enumerated monomials cannot express the
  saturating shape and lose to a linear-in-(n, D) baseline (1.20 vs 0.89).
  Forms in D alone fail (2.1–2.7) because they cannot reach the complete
  graph; the (1 − q) factor is the fix.
- Sandwich holds on all 37,800; forced on 34.2%; **λ is not ½**: pooled ½ as
  in §5, but 0 → ⅔ monotone in density (ρ 0.63–0.69), 0.24 with n. §5's
  midpoint was a corpus average over sparsities; old section left in place,
  contradiction stated in §12.
- pw > tw certified on ~10% of instances at n ≥ 25, by at most 2, a third of
  instances at col_mean 2–2.5 (the §11 ridge / §6 family); the scaling of
  pw − tw is hidden by min-fill's own growing slack (overshoot share 5% →
  22% from n = 25 to 40). Needs exact treewidth; not computed here.
- Tests: `tests/test_concentration.py` (7). Full suite: 798 passed,
  2 skipped, 1 xfailed, 76 s. Nothing written to `solutions/`; no solver
  default changed; `_lower_bound` untouched.

### Blockers
- None. `benchmarks.recertify` was running with 9 workers; this iteration
  used at most 4 cores.

### Next
- Item 05 (§2.9): `learning.ensemble` rows carry `graph_cert` and
  `bipartite_cert`, so same-graph/different-matrix pairs within the campaign
  are `groupby(graph_cert)` with > 1 `bipartite_cert`; `learning.degeneracy`
  has `count_search` / `count_closing`. Node counts are `nodes_default` /
  `nodes_csearch` per row.
- Item 06 will want, from this item: `learning.concentration.STRUCTURAL`
  (the best form's callable, constants (2.20, 30.8, 0.549) or (2.14, 26.5)
  with e = ½) and `nominal_features`; note Chu & Stuckey's nominal d
  understates their realised col_mean at density 2 (§11), which is why the
  formula under-predicts that class by 1.6–2.8 at n = 30/40 — use col_mean
  (or (n − 1)·q from the realised matrix density) when placing them.

## Iteration 5 — 2026-09-26 08:25

Item 05 · §2.9 Is the graph the whole story? Report: `reports/ml_nature.md`
§13; all tables in `reports/graph_story_tables.md`.

### Completed
- `learning/graph_story.py` (251 s on 16 workers for everything): three
  re-covering constructions with fixed customer labels (split a product along
  a cut whose crossing edges are covered elsewhere, merge two overlapping
  products whose union is a clique, greedy edge-clique cover under a shuffled
  edge order), each seeded from `(base_name, method, k)`; relabellings; the
  §8 lattice counts on re-covered pairs; the corpus pairs from `canonical.csv`
  joined to `node_counts.csv`; the kill test (LightGBM, GroupKFold by graph
  class, feature sets from `learning.features` group names).
- 1,400 bases (200 per n ∈ {10,…,40}, one per class, half from the hardest
  decile), 15,900 applicable re-coverings in 12,031 matrix classes, all with
  the base's masks and nauty certificate, **all solved independently to the
  base's optimum** with a re-simulating witness. **Default node count equal
  in 15,900 of 15,900 pairs.** csearch differs in 394, every one among the
  622 pairs where the re-covering crossed the `better_move` density
  threshold (mean products per customer ≤ 5): Theorem 2 saves 10–13% of
  nodes at the median for n ≥ 25, up to 25%, never costs.
- Relabelling the same matrix (29,400 refutations) changes the default count
  on 588 of 800 bases at n ≥ 25 by 2–6% median, up to 2.26×; csearch up to
  8.1×. This label floor (MAD 0.005–0.008 log10) is what no graph invariant
  can see.
- §8 counts, 4,516 pairs at n = 10, 15: `count_search` equal in all;
  `count_closing` differs in nearly all greedy pairs, ×2.9–4.5 median, up to
  ×1,540.
- Corpus pairs (150 classes, 2,796 matrix classes at n ≤ 40) never differ
  but are near-complete graphs refuted in 0–13 nodes: uninformative, said so.
- **Kill met**: graph-only MAE 0.0948 vs full 0.0968 (all rows), 0.0937 vs
  0.0952 (non-complete), also on `nodes_csearch`; matrix-only 25–30% worse.
  Answer: **no**, the matrix is not part of the hardness story with labels
  fixed (effect exactly 0); labelling and the configuration rule are.
- Tests: `tests/test_graph_story.py` (7): hand-checked 4×3 instance for all
  three constructions, masks preserved on random instances, default node
  count invariant under re-covering with independent solves, relabel is the
  same matrix class, feature sets contain no matrix names, tables on tiny
  frames. Full suite: 805 passed, 2 skipped, 1 xfailed, 77 s.
- Artifact: `recover.csv.gz` (1.2 MB), `relabel.csv.gz` (0.3 MB),
  `recover_lattice.csv` (0.45 MB) committed; the 64 MB of re-covered
  witnesses under `recover_solutions/` are git-ignored (regenerate in 170 s
  from the CSV's `(base_name, method, k)`), keeping the ensemble artifact at
  ~43 MB. Nothing written to `solutions/`; no solver default changed;
  `_lower_bound` untouched.

### Blockers
- None. `benchmarks.recertify` was running with 9 workers; this iteration
  used 16 for 4 minutes.

### Next
- Item 06 (§2.8 scaling): hardness is a function of the *labelled* graph
  (§13), so predict nodes at 50–125 from graph features only, and carry a
  label-noise term (MAD 0.005–0.008 log10 at n ≤ 40, growing wider under
  csearch); the recertify counts are under `better_move=True`, a third
  configuration, and §13's flip table gives its expected saving (10–13%) so
  the default-configuration ridge fit of §11 can be adjusted before
  comparison. `learning.hardness_map.scaling` / `fit_scaling` and
  `large_counts`, `learning.concentration.STRUCTURAL` as §12 noted.

## Iteration 6 — 2026-09-26 08:30

Item 06 · §2.8 (scaling only) Does it hold at 125 × 125? Report:
`reports/ml_nature.md` §14; figure `reports/figures/scale_test.png`; all
tables in `reports/scale_test_tables.md`.

### Completed
- `learning/scale_test.py`: `--refute` computes the 50–125 node counts
  (`learning/data/ensemble/scale_nodes.csv`, committed, 38 KB); the analysis
  predicts the optimum (§12 formula refit on n ≤ 30 with nominal and realised
  p, §12 constants, `tw_min_fill + 1`, sandwich midpoint, `lb_best`,
  `ub_best`, LightGBM on scale-free graph features) and the nodes (§11 cell
  law per density interpolated in `col_mean`, fitted 15–30 and 15–40, ratio-
  aware for m = 2n; the pre-registered ridge law; a linear surface in n,
  log col_mean, opt/n, degree), split-conformal radii from campaign n = 35, 40
  (absolute and n-scaled, widths printed), coverage by band with censored
  calls as lower bounds, the first band where each interval fails, and the
  laws read off the corpus itself (`corpus_scaling`, `corpus_linearity`).
- **The ledger has no node counts** (the brief said it did; the column is
  empty), so this item refuted `optimum − 1` for the 140 corpus instances at
  n ≥ 50 outside the two day-long 125 classes under both configurations:
  280 calls, 273 settled, 7 censored at 1,500 s (all `Random-100-100-2`, at
  2.1–5.4 × 10⁹ nodes), 5.65 core-hours, 27 min wall on 16 workers. The five
  recertify counts are the `csearch` configuration (verified via
  `sparse_enough_for_better_move`) and are compared only with `csearch` laws.
- Findings: exponential growth in n at fixed density **holds through 125**
  in every class (power law 3–5× worse in RMS); the campaign's n ≤ 40 rates
  overstate the corpus's by 0.005–0.018 per customer, a factor 6–34 at 125
  for d = 6–10, but within ×3 for the two day-long classes: the §11
  pre-registered ridge law (5 × 10¹¹) against 1.6–1.7 × 10¹¹ on record, and
  the d = 4 law 11.5 vs 10.7–11.4. The d = 2 class stays 2–6× above d = 4 at
  every size to 125 while its opt/n falls 0.29 → 0.18, so `col_mean`, not
  `opt/n`, is the ridge's size-stable coordinate (§11's open question).
  E[opt] is linear in n at fixed density through 125 (r² ≥ 0.986) but with
  intercept 4–5 (formula: 2.2) and slope 0.146 at col_mean 2.8 (formula
  0.22), so the formula's bias reaches +8 at `Random-125-125-2` while
  staying within ±2 at d ≥ 4; `tw_min_fill + 1` is +4.2 at 125. Theorem 2
  saves more at 50–125 (median ratio 0.63 at n = 100, 0.17 at
  `Random-100-50-4`) than §13 measured at n ≤ 40.
- **Kill met, both quantities**: every 90% interval calibrated on n ≤ 40
  fails at 50 (tight radii) or 75 (loose radii) and collapses to 0.08–0.27
  coverage at 100–125; n-scaled radii hold only at ±6–10 stacks / ±1.4–4.9
  decades. §14 quotes point errors at 50–125 and no interval.
- Tests: `tests/test_scale_test.py` (8): name parsing, conformal quantile by
  hand, law interpolation, coverage with censoring and no-radius, first
  failure, formula ends (complete graph → n), planted scaling rate and
  linearity, planted cell law. Full suite: 813 passed, 2 skipped, 1 xfailed,
  76 s. Nothing written to `solutions/`; no solver default changed;
  `_lower_bound` untouched.

### Blockers
- None. `benchmarks.recertify` was running with 9 workers; this iteration
  used 16 for 27 minutes.

### Next
- Loop complete. For the owner: §14's table "where each finding stops
  holding" is the fold-in for `CLAUDE.md`; the two open measurements it
  leaves are exact treewidth on the ridge classes (§12) and whether the
  Theorem 2 saving keeps growing at 125 on `m = n / 2` instances, which the
  corpus does not have.

LOOP_COMPLETE
