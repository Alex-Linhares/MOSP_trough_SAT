# Progress Log

## Ralph Loop 0004 Status
- **Started**: 2026-09-27
- **Target**: 13 items
- **Current**: 2/13 SOLVED

---

## Owner note — 2026-09-27 17:10 (read before items 09–12)
- `literature/kinnersley_1992_vertex_separation_equals_pathwidth.pdf` arrived
  today. Its Corollary 4.2 and Fellows & Langston (1987) Lemma 4.3 (quoted in
  it) *are* the pathwidth branch rule of item 11's first candidate: a vertex
  whose removal leaves three components of cost ≥ k forces cost ≥ k + 1. Treat
  it as a known lemma — cite it, measure it, do not claim it. `MISSING.md`
  has the details. Its Theorem 3.1 proof is the pair of constructions in
  `LayoutToDecomposition.lean` / `DecompositionToLayout.lean`; item 12 may
  cite it for the vs = pw half.
- `literature/yanasse_1997a_transformation_pattern_sequencing_wood.pdf` and
  `literature/becceneri_yanasse_soma_2004_method_mosp_cutting.pdf` also
  arrived today (item 02 already depends on the second).
- (17:25) `literature/fellows_langston_1989_search_decision_efficiency_stoc.pdf`
  arrived too. For item 12: its Theorem 7 proves `pathwidth k − 1 ⟹ layout
  cost ≤ k` by building the matrix whose columns are the bags and expanding
  each bag into pairwise two-ones columns — the direction `Reduction.lean`
  holds with a `sorry`; the converse (a pattern order gives a decomposition:
  bags = customers open at each step, intervals by construction, every edge
  in the bag of the pattern that creates it, bag size ≤ peak) is elementary
  and is the one `Reduction.lean` lacks. `MISSING.md` has the statement.
- (17:40) `literature/fellows_langston_1987_nonconstructive_advances_ipl.pdf`
  arrived as well. Item 11: its Lemma 4.3 is the branch rule *with proof*
  (three copies joined at a new vertex adjacent to one vertex in each force
  cost k + 1). Item 12: its Lemma 4.1 proves, both ways, that expanding each
  pattern into its pairwise two-customer columns preserves the optimum — the
  matrix form of Yanasse (1997a) Proposition 5 — which is the lemma the
  `IsReduced` hypothesis in `Reduction.lean` stands in for.
- **(18:05) Item 12 — read this before touching `Reduction.lean`.** The main
  theorem `mosp_le_pathwidth_add_one` is stated over `agreementGraph`, whose
  vertices are *patterns* (two adjacent iff they share a customer). **Over
  that graph the statement is false**, so its `sorry` (`openStacksAt_le_bag_card`,
  "active customers inject into the bag") can never be filled: take one
  pattern `p` and customers `c₁..c₄` with `c_j` requiring `{p, q_j}` — the
  instance is `IsReduced`, `mospValue = 4` (every order has all four stacks
  open at `p`), the agreement graph is the star `K_{1,4}` with pathwidth 1,
  so `pathwidth + 1 = 2 < 4`. Checked with `solve_mosp_exact` and
  `fixed_parameter_algorithm.pathwidth` on 2026-09-27. `Sandwich.lean`'s
  `mospValue_le_bandwidth_add_one` inherits the falsehood (bandwidth of
  `K_{1,4}` is 2). The theorem that is true is over the **MOSP graph**:
  vertices are *customers*, adjacent iff they share a pattern (each pattern
  is a clique); `customer_inter/customer_graph.py` builds it, and the chain
  Linhares & Yanasse 2002 Prop. 2 → Fellows & Langston 1989 Thm 7 (with the
  1987 Lemma 4.1) → Kinnersley 1992 Thm 3.1 proves `mospValue = pathwidth + 1`
  for it. What item 12 should do: define `mospGraph : SimpleGraph C`
  (`Adj c d := c ≠ d ∧ ∃ p, requires c p ∧ requires d p`), then prove both
  directions over it. Easy direction, `pathwidth + 1 ≤ mospValue`: from a
  pattern order build bags `X_i = {c | isActive σ c i}`; each customer's
  bags form an interval by construction, every edge (two customers sharing
  the pattern at step `i`) lies in `X_i`, `|X_i| = openStacksAt σ i`. Hard
  direction, `mospValue ≤ pathwidth + 1`: from a path decomposition, every
  clique (each pattern's customer set) lies in some bag — the Helly lemma:
  take `v ∈ K` with the largest first bag; every `u ∈ K` is adjacent to `v`,
  so shares a bag with it, so `u`'s interval covers `firstBag v` — assign
  each pattern the index of a bag containing its clique, order patterns by
  that index, and a customer open at step `i` has patterns at bags `≤` and
  `≥` the current one, hence lies in the current bag by the interval
  property; so `openStacksAt ≤ width + 1`. No Hall's theorem and no
  `IsReduced` are needed; the existing `LayoutToDecomposition` /
  `DecompositionToLayout` files are the templates. Keep the old
  `Reduction.lean` statements only with a comment recording the
  counterexample, or replace them; do not leave a false statement standing
  as if it were an open gap.
- **(18:20) Item 12 is now mostly done outside the loop**: `MOSPGraph.lean`
  proves `mospValue = pathwidth (mospGraph) + 1` sorry-free (merged on main);
  `learning.sandwich --stage lean` and `tests/test_sandwich.py` are updated.
  What is left for item 12 is the tree-decomposition section of
  `Sandwich.lean`: `treewidth_le_pathwidth` (needs the path graph to be a tree
  or a direct argument that a path decomposition is a tree decomposition),
  the branch lemma, and the conjecture. Kinnersley 1992 and Fellows &
  Langston 1987 Lemma 4.3 are the references for the branch lemma.

---

## Iteration 1 — 2026-09-27 16:58

### Completed
- **Item 01 · Q6a, the rule as the DFS seed over the whole corpus — SOLVED.**
  `reports/ml_nature.md` §28; tables in `reports/rule_seed_tables.md`.
- Registered `rule` and `rule+cs-dfs` in `satisfiability/heuristics.py`
  (`two_key_closing_order`, popcount form of `learning.distil.HYPOTHESES`'s
  two-key rule; agrees with it on 400 random instances). Default of nothing:
  `DEFAULT_STRATEGY` is still `mcn+tabu`, `customer_search.solve` still `cs-dfs`.
- `learning/rule_seed.py`: trains five fold models grouped by file ∪ isomorphism
  class (`learning/models/union/`), sweeps five strategies with
  `learning.corpus_sweep` (new `--model-dir`), times every strategy in-process,
  writes the tables. Whole run ~12 min on 16 workers beside 9 recertify workers.
- Result over 6,376 (9–134 customers): `rule+cs-dfs` exact 94.2% / mean 0.092 /
  worst +8 / 16.7 ms; `learned+cs-dfs` (union folds) 92.1% / 0.128 / +8 / 20.6 ms;
  `cs-dfs` 84.5% / 0.241 / +10 / 29.5 ms. Head to head: rule seed 780 better /
  12 worse than `cs-dfs` (learned: 709/13 with file folds, 602/19 with the honest
  folds); rule seed 263 better / 80 worse than the learned seed. Leads in every
  size band and every collection. **The LightGBM dependency question no longer
  exists**: the learned seed is dominated by a model-free strategy of the same
  cost class. Proposed, not applied: `rule+cs-dfs` wherever `cs-dfs` is used.
- Side finding: file-grouped folds leaked; the union grouping puts all Chu &
  Stuckey, Faggioli–Bentivoglio, SCOOP, Challenge, Wilson and Shaw files in one
  fold trained on Harvey/Simonis only, and about a seventh of the 2026-09-22
  learned gain disappears under it.
- Tests: `tests/test_rule_seed.py` (11) — chain, 4-cycle tie-break direction,
  distil equivalence, Becceneri–Yanasse–Soma 2004 Table 1 (printed sequence = 4
  = optimum, all strategies reach 4), sweep ledger row into a temp ledger and
  temp solutions dir, union fold assignment, table arithmetic. Full suite:
  1,083 passed, 2 skipped, 1 xfailed in 83 s. `solutions/` untouched.

### Blockers
- None. Milliseconds were measured on a loaded machine (9 recertify + 16 sweep
  workers): absolute values ~1.5× `reports/learning.md`'s, ratios are the claim.

### Next
- Item 02 · Q6b: the 2004 arc-traversal Minimal Cost Node heuristic from its
  pseudocode; the Table 1 instance is already transcribed in
  `tests/test_rule_seed.py` (`BYS2004`, printed sequence, ξ′ = 4 = optimum).

## Iteration 2 — 2026-09-27 17:15

### Completed
- **Item 02 · Q6b, the 2004 arc-traversal MCNh — SOLVED.** `reports/ml_nature.md`
  §29; tables in `reports/mcnh_tables.md`. Kill criterion **not met**: the
  pseudocode reproduces the paper's Table 1 example to the arc.
- `satisfiability/heuristics.py`: `mcnh_trace` (Becceneri, Yanasse & Soma 2004
  §4 as written: Ω over untraversed arcs, SETV by non-decreasing Ω then index,
  the arc (n₁, n₂) with Ω(n₁) = Ω(k) and pair-wise smallest Ω over *every*
  minimum-degree node, then every arc among OPEN nodes lexicographically),
  `patterns_from_arcs` (pattern sequenced when all its pieces have been opened;
  same-arc ties: the arc's own pattern first, then index — the one tie-break the
  example does not print, needed for P12 before P3), `mcnh`. Registered `mcnh`
  and `mcnh-arcs` (pattern sequenced at its last own arc). Default of nothing.
- Reproduction: seven loops with the paper's (n₁, n₂) per loop, states after
  loops 1–3 element for element, the sixteen arcs of ARC in printed order, ξ = 4,
  the printed sequence P11, P10, P14, P2, P4, P6, P12, P3, P9, P1, P7, P5, P8, P13
  under both pattern rules, and Fig. 2's profile 2,3,3,4,3,3,3,2,3,4,3,4,3,2.
- Frinhani et al. (2018) Table 2: `mcnh` equals their MCNh on 21 of 21 named
  Challenge rows (671 = 671; SP2–4 exactly 23/37/57, where `mcn` gives 26/49/74),
  Shaw mean 14.04 vs 14.00; SCOOP (Fig. 6, aggregates only) total 233 = 233,
  gap 25.27% = 25.27%, buckets 7/0/8/9 vs 8/0/7/9. `mcnh` is the published MCNh
  to within tie-breaks; `mcn` never was (2,528 worse / 61 better, MAE 1.343 vs 0.361).
- Is the rule MCNh under another name? **No.** Over 6,376 (9–134): same value
  86.9%, same closing order 0.6%, same pattern sequence 0.8%; rule better on 592,
  worse on 242, MAE 0.279 vs 0.361, leading in every size band. Per step along
  MCNh's order: its pick attains the rule's first key on 98.8% (structural: arcs
  among open nodes are swept first), both keys 79.2%, MCN's min-degree key
  73.4% — falling to 49% / 40% at 61–134. Same first key, opposite second key.
- `mcnh` vs `mcnh-arcs`: different sequences on 5,748 instances, same value on
  all 6,376. In-process ms: mcnh 0.94, mcn 0.38, rule 0.27 (loaded machine).
- `learning/mcnh.py` (stages paper / corpus / report, ~10 s on 16 workers);
  `tests/test_mcnh.py` (13). Full suite: 1,120 passed, 2 skipped, 1 xfailed in
  83 s. `solutions/` untouched; recertify (6 workers) untouched.

### Blockers
- None. SCOOP is compared on aggregates only: Frinhani publish a figure, not a
  table, for it. Frinhani's own arcs-to-patterns derivation (via Yanasse's
  reversed piece sequence) is a third reading, not implemented.

### Next
- Item 03 · Q5: `decide_mosp` through the SAT path on §13's re-covering and
  relabelling pairs, conflicts and seconds, paired ratios.
