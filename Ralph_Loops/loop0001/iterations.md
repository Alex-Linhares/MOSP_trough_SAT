# Iterations — loop0001

One item per iteration, in order. Mark `- [x]` when done, `- [!]` when blocked.
Plan sections refer to `reports/ml_nature_plan.md`.

- [x] 01 · §2.1a **Isomorphism classes.** `learning/canonical.py`: WL hash (networkx
      `weisfeiler_lehman_graph_hash`) and, behind a soft import, a pynauty
      certificate of every MOSP graph. Table: distinct classes per collection and
      per (n_customers, n_patterns); how many instances are exact duplicates of
      another. Check that isomorphic instances have equal optima (a free audit).
- [x] 02 · §2.1b **Generator fingerprint and instance-space map.** A classifier
      predicting `collection` (and, within Chu & Stuckey, the density class) from
      structure-only features, grouped by file. Its accuracy is the finding. Plus
      a 2-D embedding (UMAP behind a soft import, else PCA) of the feature table,
      saved as `reports/figures/instance_space.png`, coloured by collection.
- [x] 03 · §2.4 prerequisite **Node counts into the ledger.** Make the customer
      search's node count a returned quantity (not only printed) and record it in
      a `nodes` column wherever a decision call is logged (`benchmarks/results/compute_ledger.csv`
      writers, `csearch`, `recertify`). Existing rows get an empty value. Do not
      change the search itself. Test: a tiny instance returns a positive count.
- [x] 04 · §2.2a **Pathwidth-adjacent invariants as features.** Add to
      `learning/features.py`, as a new group `invariants`: min-fill and min-degree
      treewidth upper bounds, reverse Cuthill–McKee bandwidth, spectral radius,
      Fiedler value, clique-cover number (the number of distinct products is an
      upper bound; report that), a cheap balanced-separator size, and the
      random-intersection parameters `(n, m, p̂)`. Rebuild the table. Report
      grouped permutation importance beside the existing 36.
- [x] 05 · §2.2b **A formula for the residual.** Symbolic regression (PySR behind
      a soft import; otherwise a small enumerated search over products and ratios
      of ≤ 3 features) for `optimum − lb_best` and for `optimum` from
      structure-only features. Baseline: LightGBM on the same features, grouped.
      Deliverable: the best formula, its grouped MAE, and a stated conjecture if
      the formula is a clean one. State plainly that it is not a bound.
- [x] 06 · §2.3 **Where the bounds fail.** Classifier `gap ≥ 2` vs tight with a
      depth-3 tree and, if `interpret` is available, an EBM; baseline density and
      size. Cluster the gap instances. Write out the ten smallest instances with
      gap ≥ 2 as matrices in the report, with their MOSP graphs' degree sequences,
      and say in words what they have in common.
- [x] 07 · §2.6a **Distil the closing policy.** Fit a depth-3 tree and a linear
      scorer to the same 2.27 M decisions `learning/policy.py` trains on; measure
      how much of the ranker's gain over MCN each keeps (grouped, same protocol
      as `python -m learning.policy evaluate`, sampled if 3 minutes is exceeded).
      Test two direct hypotheses: closing in Fiedler-vector order, and BFS-layer
      order from a minimum-degree root. Deliverable: the best readable rule.
- [ ] 08 · §2.6b **Degeneracy of the optimum.** For every corpus instance with
      n_customers ≤ 12 (and a sample of generated ones), enumerate all closing
      orders achieving the optimum by exhaustive search; report the count's
      distribution against n and density, and the fraction of instances whose
      optimum is unique up to reversal. Say what this implies for imitation.
