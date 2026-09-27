# Iterations — loop0004

One item per iteration, in order. Mark `- [x]` when done, `- [!]` when blocked.
Plan sections refer to `reports/ml_nature_plan_3.md`; earlier findings to
`reports/ml_nature.md` §1–§27. Report sections continue from §28.

- [x] 01 · Q6a **The rule as the DFS seed, over the whole corpus.** Register
      `rule+cs-dfs` in `satisfiability/heuristics.py` (the two-key rule of §7,
      `learning.distil.HYPOTHESES`, followed greedily, then `restricted_dfs` at
      its default budget seeded with that order; not the default of anything).
      Run `learning.corpus_sweep` over all 6,376 with it, beside `cs-dfs` and
      `learned+cs-dfs` (the 709 better / 13 worse of `reports/learning.md`),
      grouped by file ∪ class where a model is involved. Deliverable: the
      three-way table (exact, mean overshoot, worst, better/equal/worse pairs,
      ms per instance) and a one-paragraph answer to whether the LightGBM
      dependency question still exists. Tests: the strategy on a 3-customer
      chain and the paper's example; the sweep's ledger row.
- [x] 02 · Q6b **The 2004 arc-traversal MCNh.** Implement the Minimal Cost
      Node heuristic exactly as `literature/becceneri_yanasse_soma_2004_method_mosp_cutting.pdf`
      §4 states it (Ω(k) over untraversed arcs, SETV ordered by Ω, the arc
      (n₁, n₂) with Ω(n₁) = Ω(k) and pairwise smallest Ω, then every arc among
      OPEN nodes, patterns sequenced when all their nodes are first open),
      registered as `mcnh` in `satisfiability/heuristics.py`. Verify on the
      paper's Table 1 instance: ξ′ = 4 and the printed pattern sequence
      (P11, P10, P14, P2, P4, P6, P12, P3, P9, P1, P7, P5, P8, P13) or a
      tie-equivalent one, and Fig. 2's open-stack profile. Compare with
      Frinhani et al. (2018)'s MCNh numbers on the Challenge and SCOOP
      instances, and with `mcn` and the two-key rule over the corpus. State
      whether the rule is MCNh under another name (agreement per step and per
      instance). **Kill**: the paper's example cannot be reproduced from the
      pseudocode — say what is ambiguous and stop.
- [x] 03 · Q5 **Does the graph story hold for the SAT path?** On §13's pairs
      (`learning/data/ensemble/recover*.csv*`, `relabel.csv.gz`; regenerate
      pairs with `learning.graph_story` if needed) at n ≤ 40, run
      `decide_mosp` through the SAT path (`SAT_BACKEND`, conflicts and seconds
      recorded, 120 s deadline) at `optimum − 1` and `optimum`; paired ratios
      for re-coverings and for relabellings; predict SAT conflicts from
      graph-only against graph-plus-matrix features under grouped splits.
      Deliverable: whether the clique cover moves SAT cost, by how much, and
      whether SAT and the search therefore fail on different instances for
      that reason. **Kill**: paired median re-covering ratio within ±5%.
- [x] 04 · Q1a **Which change carries the fix's cost?** Behind flags in the C
      and the Python (new entry point; defaults unchanged), toggle the
      close-count correction and the rule reordering separately, giving four
      variants including today's and the pre-fix one. Run each through
      `learning.differential` at n ≤ 40 (sound or not, with the count of false
      answers); for the sound ones, paired `csearch` nodes at 50–100 on the
      campaign and corpus, and on `Random-100-100-2-4_0` (§18: 93 M pre-fix
      vs ≥ 1.39 G post-fix). Deliverable: a cost table per variant and a
      recommendation, stated and not applied. Tests: the default path
      byte-for-byte unchanged; each flag never changes a `decide` status on
      the differential harness's drawn instances.
- [ ] 05 · Q1b **A proof object for the customer search.** Define a
      certificate: the sequence of pruning decisions of a refutation, each
      with its rule and its witness (the dominator and the subset relation for
      `subset_rule` and `definite_move`; the covering candidate and the cost
      comparison for `better_move`), plus the branching tree it leaves. Emit
      it from the Python search (`native=False`); write an independent
      checker in `learning/search_certificate.py` that verifies every premise
      from the instance and the state and replays the residual search without
      any dominance rule. Test at n ≤ 20 against the DRAT verdicts (§17) and
      the lattice oracle. Deliverable: certificate size and check time by
      size, and the statement of which rule's steps are locally checkable.
      **Kill**: if a Theorem 2 step cannot be checked from the instance and
      the state alone, say precisely why; that is the finding.
- [ ] 06 · Q1c **The differential harness above 40.** Four relabellings, both
      configurations, both `k`, on the campaign at 50–75 (sample 8 per cell)
      and the corpus at 50–100 (all), 300 s per call, priced first, ≤ 8
      core-hours; censored calls are lower bounds and never disagreements.
      Deliverable: disagreements (state zero as zero), the relabelling spread
      by size for item 04's variants where it is cheap to add, and the first
      size at which the harness stops being affordable.
- [ ] 07 · Q4a **One certified ridge cell at 100.** `learning.upward` (or a
      new stage) at n = 100, m = n, the realised-density cell nearest three
      customers per product, 25 instances, `default` configuration, resumable,
      priced by `learning.cost_model` before starting; as many as 2.5 hours on
      16 workers certify, the rest recorded as censored lower bounds with
      their counts. Both refutation configurations where affordable.
      Deliverable: the cell's optima and nodes, the audit, and the price paid
      against the prediction.
- [ ] 08 · Q4b **Does the rate keep falling?** Refit §16's drift with the 100
      cell (settled and censored); predict 125 with a band; compare with the
      six recertify counts on record (pre-fix, `csearch`; compare like with
      like); state whether the curve is sub-exponential, whether the drift
      saturates, and what the day-long classes cost under each reading.
      Deliverable: the revised law and its band, and a sentence on what it
      means for re-certifying the withdrawn instances.
- [ ] 09 · Q3a **Why cover excess two.** Analysis: the cover excess
      `(n_ones − m) / n` as a quantity of the random bipartite incidence graph
      (cyclomatic number `n_ones − n − m + c`, so excess 2 is one independent
      cycle per customer); the 2-core and k-core thresholds of random
      bipartite graphs and the random-intersection-graph literature; a
      derivation of where the ridge should sit for each `m / n` under the
      best candidate mechanism, tested against §25's measured peaks at
      m/n ∈ {2, 1, 1/2, 1/4, 1/8}. Deliverable: the mechanism, or the
      statement that none of the candidate thresholds coincides with the
      ridge, with the numbers.
- [ ] 10 · Q3b **Is the ridge's height a function of the same quantity?**
      Fit peak median nodes against `(n, excess, m / n)` across all series
      (§11, §16, item 07); test whether height at fixed `n` is a function of
      `m` alone (§25 said 1–1.5 decades per doubling), of excess, or of both.
      Deliverable: a formula with held-out error, or the statement that
      height needs `m` separately from the ridge coordinate.
- [ ] 11 · Q2 **The bound harness and three candidates.**
      `learning/bound_harness.py`: takes any candidate bound as a Python
      function over an instance or its MOSP graph; (a) validity on every
      certified instance (corpus + campaign; a single "above optimum" is a
      counterexample, drawn); (b) attack with `learning.extremal` at n ≤ 15
      (10⁴ evaluations); (c) tightness on the 338 gap instances against
      `max(lb_best, tw + 1)`. Then three candidates: the pathwidth branch rule
      applied recursively over cut vertices (if `G − v` has three components
      of bound ≥ k then bound ≥ k + 1, seeded by clique size, on the
      block-cut tree), and two of the session's own that see separators of
      trees of cliques. Deliverable: the harness and a verdict per candidate.
      **Kill**: none beats the reference on more than 5% of the gap instances
      while surviving.
- [ ] 12 · Q7 **The remaining Lean gaps.** The MOSP–pathwidth equality is
      already proved (`lean/MOSPFormalization/MOSPGraph.lean`, 2026-09-27,
      `sorry`-free; read its header and PROGRESS.md's owner notes first). What
      is left is the tree-decomposition section of `Sandwich.lean`: prove
      `treewidth_le_pathwidth` (every path decomposition is a tree
      decomposition — build the `TreeDecomposition` from a `PathDecomposition`
      directly rather than through `pathGraph.IsTree` if Mathlib lacks it),
      and the branch lemma (three branches of treewidth ≥ k at a cut vertex
      force pathwidth ≥ k + 1; Fellows & Langston 1987 Lemma 4.3 and Kinnersley
      1992 Theorem 4.3 are the references, in `literature/`). Leave
      `conjecture_sqrt_tw_f6` as a statement. `lake build` must pass;
      `python -m learning.sandwich --stage lean` must list the inventory and
      `tests/test_sandwich.py` must pass (move any newly proved name from
      `STATED` to `PROVED` in `learning/sandwich.py`). Blocked with a precise
      gap list is an acceptable deliverable.
- [ ] 13 · **Reserve.** If any item above is marked `- [!]`, re-open the most
      valuable one with what its blocker taught. If none is blocked, take the
      first "for the next loop" note left by items 01–12 in PROGRESS.md.
