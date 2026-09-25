# Progress Log

## Ralph Loop 0001 Status
- **Started**: 2026-09-25
- **Target**: 8 items
- **Current**: 1/8 SOLVED

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
