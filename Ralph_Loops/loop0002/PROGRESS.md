# Progress Log

## Ralph Loop 0002 Status
- **Started**: 2026-09-26 06:18
- **Target**: 6 items
- **Current**: 2/6 SOLVED

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
