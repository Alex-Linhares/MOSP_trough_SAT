# Iterations — loop0003

One item per iteration, in order. Mark `- [x]` when done, `- [!]` when blocked.
Plan sections refer to `reports/ml_nature_plan_2.md`; earlier findings to
`reports/ml_nature.md` §1–§14. Report sections continue from §15.

- [x] 01 · §2.1a **The differential harness.** `learning/differential.py`: for
      every instance, `k = 8` random relabellings and one re-covering
      (`learning.graph_story` primitives), `decide(optimum − 1)` and
      `decide(optimum)` under both configurations (`learning.node_counts.refute`
      and its `sat` counterpart); any disagreement in *status* across the runs
      of one instance is an unsound rule and is reported with the instance
      drawn. Record every node count (item 04 needs the spread). Run over the
      campaign (37,800), the corpus at n ≤ 40, and the lattice oracle
      (`learning.degeneracy`) wherever n ≤ 15. Deliverable: the harness, the
      run, the count of disagreements (state zero as zero), and the
      relabelling spread by size. Tests: a planted unsound rule (a `decide`
      wrapper that lies on one labelling) is caught.
- [x] 02 · §2.2 **The campaign upward.** Extend `learning.ensemble` with
      n ∈ {50, 60, 75} over the density sweep at m ∈ {n/2, n, 2n}, 50 per
      cell, and n = 100 at the ridge cell and its two neighbours (m = n), 25
      per cell, priced by the ridge law before running (§14: ~17 min per
      ridge instance at 100; stop at 75 if the 100s exceed 8 core-hours).
      Both refutation configurations, features, certificates, as before.
      Deliverable: the grid as run, the rate per density with its drift in n
      measured between consecutive sizes, and the revised 125×125 prediction
      with an error band from the 100-customer cells. Commit results and
      manifest; witnesses only if the total stays under ~120 MB apparent.
- [x] 03 · §2.1b **DRAT proofs at n ≤ 40.** Build drat-trim under `tools/`
      (record the blocker if it cannot be built). `learning/proofs.py`:
      re-refute `optimum − 1` through the SAT path with
      `Solver(name='cadical195', with_proof=True)` for every certified corpus
      instance at n ≤ 40, applying the same preprocessing `decide_mosp` does
      and recording it in the certificate; check each proof with drat-trim;
      store proofs compressed under `learning/data/proofs/` (git-ignored) and
      commit a table of instance, k, proof hash, size, solve and check time,
      verdict. Run as a resumable batch on 16 workers with a per-instance
      deadline; report the fraction certified by size band and the first n at
      which it stops being affordable. Deliverable: §17 and the table.
      Tests: a 4-customer instance's proof checks; a corrupted proof fails.
- [x] 04 · §2.4 **The relabelling portfolio.** From item 01's spreads and new
      runs at n ∈ {40, 50, 60, 75} (campaign) and 50–100 (corpus), 16 random
      relabellings per instance under `csearch`: the distribution of nodes,
      the expected speed-up of min-of-k for k ∈ {2, 4, 8, 16} against the
      identity labelling and the median, its growth with n, and whether any
      cheap statistic of a labelling predicts its cost. Then run the 16-way
      portfolio for real on the four `Random-100-100-2` instances censored at
      1,500 s in §14 (budget 8 core-hours). Deliverable: the speed-up curve,
      the projected wall clock for the 125×125 ridge on 16 cores, a
      recommendation for `benchmarks.recertify` stated and not applied.
      **Kill**: median min-of-8 speed-up under 1.5× at n ≥ 60.
- [x] 05 · §2.3 **Predicting cost.** `learning/cost_model.py`: predict
      `log10 nodes` from label-free graph features with item 04's relabelling
      spread as the noise floor; censored counts through a survival model
      (lifelines or scikit-survival behind a soft import; else a Tobit-style
      likelihood by hand); train at n ≤ 75, test at 100 and 125 (corpus +
      `scale_nodes.csv` + `recertify/results.json`). Baselines: §11's cell law,
      §14's surface. Deliverable: error by size band, the decade-accuracy claim
      at 100–125, the predicted versus actual cost of the recertify instances,
      and the cheapest-first order for whatever remains withdrawn.
      **Kill**: fewer than 80% of the 100–125 counts within one decade.
- [ ] 06 · §2.5a **Fan order.** Behind a flag defaulting to today's behaviour,
      order the cheapest candidates in `decide` (Python and C) and
      `restricted_dfs` by highest remaining degree instead of customer index;
      test that the default path is byte-for-byte unchanged and that the flag
      never changes a `decide` status (item 01's harness, reused). Paired node
      counts on the campaign to 75 and the corpus to 100, both configurations.
      Deliverable: the paired distribution by size and density, a proposed
      default stated and not applied. **Kill**: paired median within ±5% at
      every size.
- [ ] 07 · §2.5b **Theorem 2's switch.** With nodes under both configurations
      on every instance we have (campaign to 100, corpus to 125), fit the
      decision boundary where `csearch` beats `default` (depth-3 tree on
      size-free features, grouped) and compare with
      `sparse_enough_for_better_move` (≤ 5 products per customer); test the
      hypothesis that it should always be on (§13–§14: it never cost, saved
      0.63 at n = 100 and 0.17 at m = n/2). Deliverable: the boundary, its
      agreement with the hand threshold, the nodes saved or lost under each
      rule, a proposed rule stated and not applied. **Kill**: the learned
      boundary agrees with the hand threshold on more than 95% of instances.
- [ ] 08 · §2.7 **Extremal search and exact treewidth.** `learning/extremal.py`:
      an exact treewidth DP (O(2ⁿ·n), to n = 20) with a test against min-fill
      on small graphs and against known values (paths, cycles, grids); local
      search over bit flips at n ≤ 15 with `solve_mosp_exact` as oracle,
      objectives `optimum − lb_best`, `optimum − (tw + 1)`, nodes per size,
      `cs-dfs` overshoot, and configuration disagreement; seeded from §6's ten
      smallest gap instances and random trees of cliques; deduped by canonical
      form. Exact treewidth for every uncertified gap ≥ 2 corpus instance at
      n ≤ 20 and a branch-and-bound attempt at 21–30 with a deadline.
      Deliverable: per objective the best instances drawn, the largest
      `pw − tw` per n and whether it grows, the smallest instance with
      `pw − tw ≥ 2` with its proof, and §6's floor turned into a number.
      **Kill**: nothing beats the corpus's worst at the same size.
- [ ] 09 · §2.6 **Conjecture mining for a branching-aware lower bound.**
      `learning/conjecture.py`: candidate invariants that can see branching —
      the expansion profile `f(t)`, separator sizes at several balance ratios,
      simplicial and hub counts, the clique tree's pathwidth where the graph is
      chordal, block and bridge counts — enumerated as formulas with
      `learning.formula_search`'s machinery; keep every candidate never above
      the optimum on all certified instances (corpus + campaign), rank by how
      often it exceeds `lb_best` and by tightness on the 338 gap instances;
      attack each survivor with item 08's search (10⁴ adversarial instances at
      n ≤ 15); draw the smallest counterexample of each broken candidate.
      Deliverable: zero or more conjectures `pathwidth ≥ f(G)` with their
      tightness, size range and adversarial record, handed to item 12.
      **Kill**: no survivor exceeds `lb_best` on more than 5% of the gap
      instances.
- [ ] 10 · §2.8 **Set-valued imitation.** Vectorise
      `learning.degeneracy`'s search-measure lattice to reach n = 20 (1,298
      corpus instances); train a ranker whose loss counts a step right when it
      lands in `optimal_choices`, with the two-key rule's keys as features so
      the model can only add to the rule; evaluate by construction value,
      grouped by file ∪ class, against the rule (§7: 0.348 / 80.7%) and the old
      ranker. Along every witness at 50–125, bounded backward search on the
      witness's own prefixes for the optimal choices per step. Deliverable:
      whether any learned policy beats the rule under the correct objective,
      and the imitation ceiling at 50–125. **Kill**: not better than the rule
      by 0.02 MAE grouped — then imitation is closed for good.
- [ ] 11 · §2.9 **Why the ridge is where it is.** Analysis: expected degree,
      edge probability and giant-component threshold of G(n, m, p) in
      `col_mean` coordinates for each m/n, overlaid on the hardness map; the
      ridge's `col_mean` at m = n/2 (item 02) against what a mean-degree
      hypothesis predicts (§11: ~8–9 at both m = n and m = 2n); comparison
      with the literature's transitions for pathwidth and treewidth of sparse
      random graphs. Deliverable: the ridge as a condition on one graph
      parameter across m/n, or the statement that none does it, decided by the
      m = n/2 cells. No kill.
- [ ] 12 · §2.10 **The sandwich in Lean.** In `lean/MOSPFormalization/`, define
      degeneracy and bandwidth over the existing graph definitions and prove
      `degeneracy ≤ vertex separation` and `vertex separation ≤ bandwidth`,
      connecting through `VSEquivPW`; `lake build` must pass. Blocked is
      acceptable: then commit the statements with `sorry` and a gap list in
      the report section. If item 09 produced a conjecture, state it too, with
      `sorry`. Deliverable: two theorems or two statements and the gaps.
- [ ] 13 · §2.11 **The synthesis.** `reports/ml_nature_summary.md`: every claim
      the two plans produced, one paragraph each, with size range, regenerate
      command and status (finding / conjecture / proposed solver change with
      measured effect / closed question); the solver changes proposed and never
      enabled with the measurement that decides each; open questions by cost.
      Bring `learning/README.md` up to date in plain English. No new
      computation; every number copied from a section and cited by number.
- [ ] 14 · **Reserve.** If any item above is marked `- [!]`, re-open the most
      valuable one with what its blocker taught, and finish it or say exactly
      why it cannot be. If none is blocked, spend this session on the first
      "for the next loop" note left by items 01–13 in PROGRESS.md.
