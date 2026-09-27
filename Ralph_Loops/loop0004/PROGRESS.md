# Progress Log

## Ralph Loop 0004 Status
- **Started**: 2026-09-27
- **Target**: 13 items
- **Current**: 5/13 SOLVED

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

## Iteration 3 — 2026-09-27 18:40

### Completed
- **Item 03 · Q5, does the graph story hold for the SAT path? — SOLVED.**
  `reports/ml_nature.md` §30; tables in `reports/sat_story_tables.md`; data
  `learning/data/ensemble/sat_story.csv.gz` (one row per SAT call, 147 KB).
- `learning/sat_story.py`: §13's pairs regenerated from the manifest (40 bases
  per size from its 200, one re-covering per method, four relabellings), each
  run through `decide_mosp`'s exact reduction (components, dominance,
  `encode_mosp_decision`) at `optimum − 1` and `optimum`, 120 s deadline.
  Conflicts on `cadical195` with conflict-budget chunks against the wall;
  `kissat404` (the default backend) exposes no statistics, ignores
  `interrupt()` and aborts the interpreter on `conf_budget`, so it is timed in
  seconds in a forked, hard-killed child on the calls CaDiCaL settled within
  30 s. Resumable CSV, wall cutoff (`--wall`), one job per call.
- Run: 3,258 calls, 65 min on 16 workers beside 6 recertify workers; complete
  at 10–30 customers, a 10-base sample at 35 when the wall fell. **All 5,657
  settled decisions on both backends agree with the certified value.**
- Result: the cover moves SAT cost. Refutation paired ratios greedy 0.77 /
  merge 0.87 / split 1.15 at the median (each p < 1e−8), p10–p90 0.26–1.67,
  MAD 0.13 log10; the search's node ratio is 1 on the same 464 pairs. The
  channel is the reduced formula (Spearman 0.6–0.7 between Δconflicts and
  Δclauses / Δproducts; identical formula ⇒ identical conflicts on all 29
  such pairs). SAT's label floor is 1.6–1.9× (refute) and 7–13× (witness)
  against the search's 1.00–1.05×. Within-graph share of SAT variance 4–21%;
  at fixed n, nodes and conflicts anticorrelate (−0.04 to −0.34) because SAT
  tracks clause count (0.93–0.98). Kill test inverted from §13: graph-only
  MAE 0.533 vs full 0.245 vs six formula quantities 0.264.
- **Kill verdict: met on its letter, failed in its spirit** — pooled median
  1.00 on both sides because 17% of pairs are equal and the methods pull
  opposite ways; the per-method medians are all outside ±5%.
- Proposed, not applied: race a pre-encoding merge re-cover on the SAT path.
- Tests: `tests/test_sat_story.py` (10) — hand instance optimum 3 by brute
  force, unsat/sat on both backends, dominance makes the reduced formula and
  the conflicts equal, deadline censoring on both mechanisms, ratio-table
  arithmetic incl. censored pairs, kill verdict, job construction. Full suite:
  1,130 passed, 2 skipped, 1 xfailed in 118 s (loaded machine). `solutions/`
  untouched; recertify untouched.

### Blockers
- None. Censoring at 120 s: 22% of refutations at 25, 62% at 30, 71% at 35 —
  the paired tables at those sizes are on the easier pairs, said in §30. The
  wall cutoff dropped the in-flight calls (≤ 16) rather than recording them.

### Next
- Item 04 · Q1a: which of the `better_move` fix's two changes carries its cost,
  behind flags, through the differential harness at n ≤ 40 and paired in
  nodes at 50–100.

## Iteration 4 — 2026-09-27 19:35

### Completed
- **Item 04 · Q1a, which change of the `better_move` fix carries its cost — SOLVED.**
  `reports/ml_nature.md` §31; tables in `reports/fix_cost_tables.md`; data
  `learning/data/ensemble/fix_cost_harness.csv.gz` (876,350 rows) and
  `fix_cost_scale.csv` (34,485 rows).
- Flags: C `cs_decide_variant` (new entry point; `cs_decide` and `cs_decide_fan`
  keep their signatures and pass variant 0), bits `BM_OLD_CLOSE_COUNT`,
  `BM_OLD_RULE_ORDER`, `BM_SUBSET_RESTRICTED`; Python `old_close_count`,
  `old_rule_order`, `subset_after_better_move` on `decide_native` and through
  `decide`'s kwargs. All default off; the default path is byte-for-byte the old
  library (10,248 calls against the pre-change `.so`, same status/nodes/witness).
  The filter is refactored into `subset_pass` / `better_move_pass` helpers with
  the bodies verbatim.
- Reproduction: `prefix` gives §15's 56 instances / 88 false answers exactly,
  the bug report's 6,101,183 → 6,544,638 totals, §14's 93.1 M nodes / 37 s on
  `Random-100-100-2-4_0` (93,127,027 in 38.8 s), and the pre-fix `nodes_csearch`
  of `results.csv` (60/60 sampled) and `results_upward.csv` (3,334 of 3,348).
- Soundness at n ≤ 40 (17,527 instances × 10 labellings × 2 calls per variant):
  `fixed` 0, `old-close` 1 instance / 3 false `unsat` at the optimum, `old-order`
  36 / 61, `prefix` 56 / 88. **Both changes are necessary**; no revert is a
  candidate. Correction to `better_move_bug.md` §7: the 10 × 13 minimal instance
  needs both bugs (the campaign instance it came from falls to Bug B alone).
- Cost at n ≤ 40 (17,521 identity refutations): fix 1.073 total nodes; close
  count 1.011, reordering 1.064; log-cost shares 23% / 81% / −4% interaction;
  seconds 1.10. At 41–100 (3,452 refutations all variants settled, Theorem 2 on):
  fix 1.54 (median 1.08, p90 1.59), close 1.06, order 1.48; seconds 1.30 (the
  fixed order is faster per node, 1.73 vs 1.45 M/s); per-instance log shares
  54% / 59% / −14% — the close count grows with size (changes 89% of counts vs
  13% below 40) and dominates on half-ratio and SCOOP instances. The fix censors
  10 more at 75 (60 s) and 1 more at 100. §18's ×2–3.5 reproduced on
  `Random-100-50-*` (3.46 = 1.67 close × 2.73 order); the ridge instance is
  2.26× close, ≥ 8.7× order, ≥ 19.6× in all.
- A fifth, non-revert variant `bm-first` (better move first, subset rule citing
  nothing better move discarded): sound on all 350,540 harness calls and every
  settled scale call; +2% nodes at n ≤ 40, **0.854× nodes at 41–100** (0.79 at
  d = 2, 0.84 at n = 75, 0.87 corpus), 1.16 on the 100-customer ridge cell,
  even in seconds (0.98; slower per node, 1.50 M/s). Censored 31 vs 38.
- **Recommendation, stated, not applied**: keep today's rule; the reordering is
  the cost and it is the price of acyclic coverings; `bm-first` is a candidate
  to tune (move the citation check out of the subset loop) and re-measure in
  seconds on the 125 × 125 density-2/4 classes, not to adopt.
- Tests: `tests/test_fix_cost.py` (8) — default byte-for-byte incl. old entry
  points, recorded `nodes_default` and pre-fix `nodes_csearch` reproduced, flags
  no-ops without `better_move`, documented statuses on both minimal instances
  for all five variants, `bm-first` never changes a status vs the Python
  reference, harness rows / soundness table on the 10 × 13, ratio arithmetic.
  Full suite 1,138 passed, 2 skipped, 1 xfailed in 86 s, re-run after the last
  code edit.
  `solutions/` untouched; recertify (13 workers) untouched.

### Blockers
- None. The acceptance criterion "each flag never changes a `decide` status on
  the drawn instances" cannot hold literally for flags whose purpose is to
  revert a soundness fix; the test asserts the documented statuses instead
  (`prefix` refutes both minimal instances, `old-close` the 17 × 9, `old-order`
  neither) and the never-changes invariant for the one sound flag, `bm-first`.
- Censoring: 60 s at 75 leaves 27 (fixed) / 17 (prefix) refutations as lower
  bounds; 120 s at 100 leaves 9–10; the paired tables are on the settled pairs
  and say so. Random-100-100-2-4_0 is censored at 600 s under `fixed`,
  `old-close` and `bm-first`.
- Compute: harness 53 s + 35 s, scale 27 + 10 min, all on 14 workers beside 13
  recertify workers; seconds are from a loaded machine, ratios are the claim.

### Next
- Item 05 · Q1b: a proof object for the customer search — certificate format,
  emitter on the Python search, independent checker, tested at n ≤ 20 against
  the DRAT and lattice verdicts.

## Iteration 5 — 2026-09-27 20:05

### Completed
- **Item 05 · Q1b, a proof object for the customer search — SOLVED.**
  `reports/ml_nature.md` §32; tables in `reports/search_certificate_tables.md`;
  data `learning/data/ensemble/search_certificate.csv` (18,707 rows, one per
  instance × configuration, 9–75 customers; certificates not stored, they
  regenerate in milliseconds).
- `learning/search_certificate.py`: the format (one record per node: move,
  free moves, kind, steps `["definite", q]` / `["subset", r, d]` /
  `["better", r, q]`, children; state, cost cut and Theorem 3 recomputed by
  the checker from the path), the emitter (`decide(native=False)` with
  witnesses, plus a Python port of the C's fixed `better_move` so Theorem 2
  steps can be certified at all; reverts `old_close_count` / `old_rule_order`
  for the tests), the independent checker (`check`: neighbourhoods from the
  matrix, premises recomputed, exhaustiveness with covering chains that must
  end at a child or in Q(S), no cycles, memo only without old move), and the
  corpus study (stages `run` / `tables` / `one`).
- Fidelity: the emitter equals `decide(native=False)` in status and branches
  at every k on four configurations (1,060 refutations) and equals the C under
  `csearch` (1,000 refutations, 170 Theorem 2 steps). On the corpus at n ≤ 40
  the branch counts equal the C's recorded counts on 5,221 / 5,205 of 6,135
  (`default` / `csearch`) and **every remaining difference (914 / 930) equals
  the C run with `memo=False`**: the certificate tree is the C's tree without
  the memo, which saves the C 40% of nodes there and is exactly the part that
  is not locally checkable under old move.
- Result at 9–40: **all 6,135 certified corpus instances refuted and every
  certificate verified under all three configurations** (`default`, `csearch`,
  `memo`), 0 rejections, 0 unknown; agrees with §17's 5,646 DRAT verdicts and
  covers the 489 DRAT censored; lattice oracle 2,812 / 2,812. 25,567 Theorem 2
  steps certified under `csearch`. Size ~60 bytes per branch uncompressed,
  325–750 B gzipped at the median per band, 388 KB max; check 14.8 µs per
  node, 0.62× emit time; whole corpus at n ≤ 40 is 5.0 MB gzipped and checks
  in 4.5 s. Against DRAT on the 5,646 with both: 13–13,700× smaller gzipped,
  800–10,000× faster to check (3.2 MB / 2.1 s vs 11.7 GB / 5,190 s) — with
  the stated difference in trust base (three dominance theorems in the
  free-move cost model vs resolution + the encoding).
- At 41–75 (151 instances, Python emitter, 60 s): 141 refuted and verified
  under both configurations, 10 censored, all at 75 customers (SP3 twice,
  eight Random-75-75); max verified certificate 977,956 nodes / 10.1 MB gz,
  check 24 s; 211,737 Theorem 2 steps.
- Both shipped bugs reproduced and rejected for the right reason: the 17 × 9
  under the old close count fails a `better` premise at the root; the
  campaign instance `ens_f_n10_m20_d2_i070` under the old rule order (Bug B
  alone, from item 04's harness) is rejected as *covering cycle through
  [6, 9]* with every premise true. Corruptions (dropped child, forged
  dominator, swapped Theorem 2 roles, raised k, sat leaf, wrong instance,
  redirected memo) all rejected.
- **Kill verdict: not met at the step; the finding is where the locality
  ends.** A Theorem 2 step's premise is a function of (N, S, O(S), k, r, q)
  and is checked from the instance and the state alone; what is not
  step-local is termination of the covering chain, a property of the node's
  whole step set (the 2026-09-26 cycle is exactly that). Theorem 3 is
  path-local; the memo is state-local only without Theorem 3 — with both, as
  the C runs them, a cited refutation belongs to its path and checking it is
  a replay, not a lookup. Table of rules × what each needs in §32.
- Proposed, not applied: a C emitter behind a flag; Lean statements of the
  three theorems in the free-move cost model (the one trusted step left);
  `recertify` emitting and checking certificates.
- Tests: `tests/test_search_certificate.py` (15) — hand 4-cycle, 17 × 9
  shape, emitter = reference on 4 configurations, emitter = C with Theorem 2,
  memo references emitted/checked/redirect rejected, memo+old move refused,
  Bug A rejected at a `better` premise, Bug B rejected as a cycle, both bugs
  on the 10 × 13, corruptions, brute-force agreement, row/table plumbing.
  Full suite 1,153 passed, 2 skipped, 1 xfailed in 100 s, re-run after the
  last code edit. `solutions/` untouched.

### Blockers
- None. The first 41–75 run stalled on two 75-customer emits because the
  deadline was checked every 4,096 branches and Theorem 2 nodes there cost
  ~0.1 s each; stopped by PID, the emitter now checks every 256 branches and
  the pool dispatches one job at a time; the run resumed from its CSV.
  Killing pool workers before their parent made the Pool respawn
  replacements that were orphaned to systemd — kill the parent first.
- `pgrep -f benchmarks.recertify` matches this session's own prompt text; no
  recertify Python process was actually running during this iteration.
- Nothing at or above 100 customers was emitted; the certificate at 125 × 125
  would be the 10¹¹-node tree itself (§32 says so).

### Next
- Item 06 · Q1c: the differential harness at 50–100 under a budget — four
  relabellings, both configurations, both k, campaign 50–75 and corpus
  50–100, 300 s per call, ≤ 8 core-hours; censored calls are lower bounds.
