# Progress Log

## Ralph Loop 0001 Status
- **Started**: 2026-09-25
- **Target**: 8 items
- **Current**: 2/8 SOLVED

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
