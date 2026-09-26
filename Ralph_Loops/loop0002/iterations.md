# Iterations — loop0002

One item per iteration, in order. Mark `- [x]` when done, `- [!]` when blocked.
Plan sections refer to `reports/ml_nature_plan.md`; earlier findings to
`reports/ml_nature.md` §1–§8.

- [x] 01 · §3 phase 3 **Campaign infrastructure and pilot.** `learning/ensemble.py`:
      generate `G(n, m, p)` ensembles under both generators (Bernoulli `p`, and
      Chu & Stuckey's fixed customers-per-product `d`), dedupe by
      `learning.canonical` MOSP-graph certificate, record `g_components` rather
      than discarding decomposable instances, solve each with `solve_mosp_exact`
      into `learning/data/ensemble/solutions/`, and for each record: optimum,
      nodes and seconds to refute `optimum − 1` under both configurations
      (`learning.node_counts.refute`), `lb_best`, `ub_cs_dfs`, `tw_min_fill`,
      `bw_rcm`, `g_degeneracy`, the 49 features, and the generator parameters.
      One CSV row per instance, resumable (skip rows already present). Un-ignore
      `learning/data/ensemble/` in `.gitignore`. Then a **pilot**: 10 instances
      per cell over n ∈ {10, 20, 30, 40}, m = n, d ∈ {2, 3, 4, 6, 8} and
      p ∈ {0.05, 0.1, 0.2, 0.3}; report the cost per cell (median and max
      seconds, nodes) and from it the grid item 02 can afford in 2.5 hours on
      16 workers. Deliverable: the cost table and the chosen grid, written into
      the report as §9. Tests: a tiny cell regenerates byte for byte from its
      seeds; the results row for a hand-checkable instance carries the right
      optimum and a positive node count.
- [x] 02 · §3 phase 3 **The campaign.** Run the grid item 01 chose: at least
      n ∈ {10, 15, 20, 25, 30, 40}, m ∈ {n, 2n}, a density sweep fine enough to
      resolve a peak (d from 2 to 10, and p from 0.05 to 0.5, extending *below*
      Chu & Stuckey's density 2 since §3 found nodes still rising there), 100+
      instances per cell where the pilot says it fits, fewer where it does not,
      with the shortfall stated. Report §10: the grid as run, instances per cell
      before and after deduplication, the share of complete graphs and of
      decomposable instances per cell (§8 found p = 0.5 gives complete graphs on
      56–81% of instances at n ≥ 10, so the useful range is narrower than the
      grid), total core-hours, and the audit (every witness re-simulates, every
      `optimum − 1` refutes). No analysis yet beyond the descriptive tables.
- [ ] 03 · §2.4 **Is there a phase transition in hardness?** From the campaign
      table: median and p90 nodes against density per size; is there a peak,
      where is it, does it sharpen with n; fit a scaling exponent of nodes
      against n at the peak and away from it. Candidate order parameters:
      density, `d`, mean degree, `optimum / n`, `ub − lb`, `g_components`.
      Locate Chu & Stuckey's `Random-n-m-d` classes on the map using their
      corpus node counts from §3. Baseline: hardness monotone in density.
      **Kill**: node counts at fixed n monotone in density with no peak across
      three sizes. Deliverable: the hardness map figure
      (`reports/figures/hardness_map.png`), the order parameter if one exists,
      and one sentence on why densities 2 and 4 at 125×125 are the ones that
      take 28 hours — or why the map does not say.
- [ ] 04 · §2.5 **Does the optimum concentrate?** Per cell: mean, variance and
      coefficient of variation of the optimum; CV against n at fixed `(m/n, p)`.
      Fit `E[opt](n, m, p)` with `learning.formula_search`'s enumerated search
      over the generator parameters alone (no graph features), and compare with
      `G(n, p)` pathwidth (linear in n above the giant-component threshold).
      Beside it, the §5 sandwich on the ensemble: `g_degeneracy + 1`,
      `bw_rcm + 1`, and whether λ concentrates at ½; and `optimum − (tw_min_fill + 1)`
      against sparsity, to see how `pw − tw` scales. **Kill**: CV above 0.2 up
      to n = 40. Deliverable: the formula with its residual distribution and
      validated range, labelled *not a bound* in every table.
- [ ] 05 · §2.9 **Is the graph the whole story?** Two sources of pairs with
      identical MOSP graphs and different products: the 150 corpus graph
      classes holding several matrix classes (§1), and generated re-coverings —
      for a campaign instance, re-cover its edge set with different cliques
      (split a product in two along a cut, merge two overlapping products,
      greedy edge-clique-cover under a shuffled edge order) and solve each.
      Compare nodes to refute `optimum − 1` within a pair (paired test, and the
      ratio's distribution); predict nodes from graph-only against
      graph-plus-matrix features under grouped splits; and check §8's
      quantity: `count_search` should be equal within a pair and
      `count_closing` need not be. **Kill**: graph-only features predict nodes
      as well as the full set. Deliverable: a yes or no with the effect size.
- [ ] 06 · §2.8 (scaling only) **Does it hold at 125×125?** Take item 03's
      scaling law and item 04's formula, fitted at n ≤ 40, and predict (a) the
      optimum and (b) the nodes to refute for the 200 Chu & Stuckey corpus
      instances at 30–125, whose optima are certified and whose node counts at
      50–125 are in `benchmarks/results/compute_ledger.csv` and
      `recertify/results.json` (`Random-125-125-2-4_0`: 167.8 billion nodes).
      Report error by size band and the size at which each prediction leaves
      its conformal interval fitted on n ≤ 40. **Kill**: coverage collapses
      across the size boundary, in which case the intervals are not to be
      quoted at large sizes and the section says so. Deliverable: the size at
      which each finding stops holding, if it does.
