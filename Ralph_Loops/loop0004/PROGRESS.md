# Progress Log

## Ralph Loop 0004 Status
- **Started**: 2026-09-27
- **Target**: 13 items
- **Current**: 11/13 SOLVED

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

## Iteration 6 — 2026-09-27 20:55

### Completed
- **Item 06 · Q1c, the differential harness above 40 under a budget — SOLVED.**
  `reports/ml_nature.md` §33; tables in `reports/differential_scale_tables.md`;
  data `learning/data/ensemble/differential_scale.csv` (12,960 rows, one per
  instance × labelling × configuration, both calls), `differential_scale_price.csv`,
  `differential_scale_variants.csv` (12,220 rows).
- `learning/differential_scale.py`: targets (first 8 certified by index of
  each of the 135 campaign cells at 50–75 = 1,080; all 214 certified corpus
  instances at 50–100), a `price` stage (every call priced from a recorded
  identity run of the same instance and configuration — `results_upward`,
  `scale_nodes`, §31's `fix_cost_scale`, §18's portfolio, plus a 10 s probe
  for the 96 unrecorded corpus pairs — ×1.3, capped at the deadline, censored
  records at the full 300 s; witnesses always scheduled, refutations cheapest
  instance first to the budget), a resumable `run` (one job per instance ×
  labelling × configuration, side-aware resume, dearest first, wall cutoff), a
  `variants` stage (item 04's `old-order`, `prefix`, `bm-first` beside `fixed`
  on the refutation side where Theorem 2 is on and the identity settled ≤ 2 s
  in §31), and tables.
- Result over 1,294 instances × 5 labellings × 2 configurations at 300 s:
  **25,800 decision calls, 12,860 of 12,860 refutations `unsat` (none censored,
  max 193 s), 12,938 of 12,940 witnesses simulate to the optimum, 0
  disagreements, 0 contradictions, 0 witness failures**; the 2 censored calls
  are the witness search on one relabelling of `Random-100-100-2-5_0` (≥ 6.8 ×
  10⁸ nodes), where the other labellings find it in 3.6 × 10⁶–1.8 × 10⁸. Both
  configurations agree on all 6,430 settled pairs; `csearch/default` median
  1.000, never above 1 at p90. Baseline added: `verdict` over §18's 21,828
  portfolio rows at 50–100 also gives 0 flagged.
- Affordability: priced 6.74 → 7.41 → 8.23 core-hours over three passes
  (reserve released, then budget 8.9 for one instance), actual 5.96 + 0.45
  (price/actual 1.38). Priced out: all five `Random-100-100-2` and three of
  five `Random-100-100-4` (6.67 core-hours of calls certain to censor). **The
  harness is affordable at 300 s everywhere at ≤ 75 (ridge cell included:
  8/8 refuted on every labelling, ≤ 193 s) and at 100 on every class but the
  ridge and its dense shoulder** — the first size at which it stops being
  affordable is 100 customers on `Random-100-100-2/4`, the classes that take a
  day at 125.
- Spread: refutation max/min median 1.004–1.025 by band, p90 1.06–1.17, max
  1.58, MAD 0.002–0.006 log10; on the ridge and its sparse side at 75–100,
  1.07–1.31 (max 1.54). Witness max/min median 1.3–2.0, p90 14–1,600, max 4 ×
  10⁴; witness cheaper than refutation on 12,395 of 12,840.
- Variants on 611 cheap sparse instances (12,220 calls, 0.45 core-h): 0 false
  answers from the unsound reverts (not evidence of soundness; §31 stands);
  the pre-fix rule is 2.5–3× more label-sensitive (MAD 0.019–0.024 vs
  0.007–0.008, max/min up to 7.1× vs 1.4×), most of it from the rule order.
- Tests: `tests/test_differential_scale.py` (9) — per-cell sample, pricing
  arithmetic incl. censored records, schedule (witnesses always, cheapest
  first, reserve), job order and side-aware resume, `run_sides` on the spider
  under both configurations with a skipped side, censored/skipped never a
  disagreement, spread arithmetic by hand with a censored base, band/class
  names. Full suite 1,162 passed, 2 skipped, 1 xfailed in 95 s, re-run after
  the last code edit. `solutions/` untouched; recertify (9 workers) untouched.

### Blockers
- None. Three passes were needed because the first resume keyed on the
  triple and skipped instances whose witness side was already recorded; fixed
  (`recorded_sides`, side-aware `build_jobs`) with a test. Seconds are from a
  loaded machine (16 + 9 workers on 32 cores, 0.49 M nodes/s median); nodes
  are the claim. The campaign at 50–75 is a per-cell sample of 8, not the
  cells; the eight priced-out instances at 100 have witness-side checks only.

### Next
- Item 07 · Q4a: one certified ridge cell at n = 100, m = n, realised three
  customers per product, priced by `learning.cost_model` first; as many of 25
  as 2.5 h on 16 workers certify under `default`, the rest censored lower
  bounds.

## Iteration 7 — 2026-09-27 22:50

### Completed
- **Item 07 · Q4a, one certified ridge cell at 100 — SOLVED (as a sampled
  run, as the item allows).** `reports/ml_nature.md` §34; tables
  `reports/ridge100_tables.md`; data `learning/data/ensemble/manifest_ridge100.csv`
  (25 instances, `i000`–`i004` byte for byte §16's sample, digests checked),
  `ridge100_price.csv`, `ridge100_calls.csv` (one row per decision call, 129),
  `ridge100_run.log`, `ridge100_refute_censored*.log`; witnesses under
  `learning/data/ensemble/solutions/` (monotone via `_save_solution`).
- `learning/ridge100.py`: `price` (features, four heuristic UBs, §19's Tobit +
  drift cost model per instance and configuration, §16(e)'s law figures),
  `run` (priority scheduler, one decision call per job on 16 workers: descent
  under `csearch` from the heuristic UB, cheapest predicted first; the final
  `unsat` is the `csearch` refutation; the `default` refutation of a certified
  instance queued behind every descent step; 2,400 s per call, 6,300 s wall,
  resumable from the calls CSV), `refute-censored` (a `default` call at
  `value − 1` for every censored instance, on idle workers, `--exclude` for
  calls in flight elsewhere), `tables`.
- **Price first**: cost model with the UB as optimum proxy: 45.3 core-hours for
  the 25 `default` refutations, 21.3 for `csearch`; available 28 (16 × 6,300 s).
  §16(e) law at 100: 9.09 / 8.92 (default / csearch, drifting). So a sample by
  construction; the plan's own 40 core-hours would not have fit either.
- **Result**: 129 calls, 26.4 core-hours (17.1 descents, 9.3 `default`). **1 of
  25 certified**: `i012`, optimum 21, `unsat` at 20 under `csearch` (2.13 × 10⁹
  nodes, 1,233 s) and `default` (2.94 × 10⁹, 1,424 s), both agree. The other
  24: verified upper bounds 22–26 (mean 23.6, heuristic UB 1–6 above), the step
  below censored at 2,400 s with 3.4–4.8 × 10⁹ nodes under `csearch` (log ≥
  9.54–9.68) and 1.5–5.2 × 10⁹ under `default` (960–1,800 s; all 24, the last
  two landing after the wall). Censored cell medians: `csearch` ≥ 9.64,
  `default` ≥ 9.50. The satisfiable side cost 0.78 core-hours in all (80 `sat`
  calls, median 10⁴·¹ nodes, two at 1.4–2.0 × 10⁹): the whole cost is the last
  step.
- **Price against paid**: the cost model said the cell would not fit and it did
  not, and its `csearch` 9.63 is consistent with every count — but re-priced on
  `i012`'s certified 21 it gives 8.36 against 9.47 observed (1.1 decades under;
  `opt_frac` is its strongest term). **§16(e)'s law is contradicted**: its
  median at 100 (8.92 csearch [8.56, 9.08]) is below all 25 lower bounds; the
  ridge's rate over 75 → 100 is at least 0.115 per customer, above §11's 0.095
  — it did not keep falling on this interval, or the 75-cell is low. For item
  08: these are post-fix counts, the six 125 × 125 recertify counts are pre-fix
  `csearch` (§31: 1/2–1/3.5 of post-fix at 100, ≥ 1/15 on the ridge instance),
  so §16(e)'s 0.04-decade match at 125 was post-fix law against pre-fix data;
  24 of 25 counts here are censored, so the refit is a Tobit.
- Audit: 25 distinct graphs, 2 decomposable, 25/25 witnesses re-simulate, 0
  disagreements, 0 below `lb_best` (12–13, 8–13 short), 1 certified provenance.
  Pre-fix vs post-fix `csearch` on the same `sat` calls (`i001` k = 23, `i002`
  k = 24): 2.5× and 3.3× more nodes post-fix, §31's fix cost on the sat side.
- Tests: `tests/test_ridge100.py` (8) — manifest shares §16's five and digests
  agree, state machine (descent, certification, censoring, disagreement over
  every k), scheduler priority and in-flight exclusion, heuristic UBs on a
  chain, law figures, censored median by hand, per-instance/audit with a real
  witness and monotone save, `refute-censored` a no-op when nothing is
  censored. Full suite 1,170 passed, 2 skipped, 1 xfailed in 91 s, re-run
  after the last code edit. `solutions/` untouched.

### Blockers
- None; the item is sampled as its text allows. What could not be done in 3
  hours: certify more than one instance (every other final step exceeds
  10⁹·⁵ nodes); run the descent twice for `default`-side witness counts.
  Seconds are from a loaded machine (16 + 9 + 8 recertify workers on 32
  cores; 1.4–2.9 × 10⁶ nodes/s); nodes are the claim.
- Two things cost minutes: `instance_features` returns its own `ub_best` and
  silently overwrote the four-strategy minimum in the first price (fixed,
  re-priced); a second `refute-censored` launch re-dispatched five calls still
  in flight in the first and was stopped by anchored `pkill` (fixed with
  `--exclude`).
- `pgrep -f benchmarks.recertify` shows 9 processes (`--days 5`); their 8
  workers were left alone.
- The witness files of §16's `i000`–`i004` under `learning/data/ensemble/solutions/`
  were lowered by the monotone save (`i001` 24 → 23, `i002` 25 → 24);
  `results_upward.csv` still records the 900 s descents' upper bounds. Not
  rewritten, said in §34(d).
- Unrelated working-tree changes present at the end (owner's, not this
  item's): `literature/MISSING.md`, the Möhring 1990 PDF rename, `paper2/`.

### Next
- Item 08 · Q4b: refit §16's drift with the 100 cell — Tobit over 1 exact + 24
  censored `csearch` counts (and the `default` ones) — predict 125 with a band,
  and compare with the recertify counts **like with like** (pre-fix vs
  pre-fix, or re-scale by §31's fix cost). The cell's counts: `ridge100_calls.csv`
  rows with `purpose == descent`, `status != sat` (csearch) and
  `config == default` at `k == value − 1`.

## Iteration 8 — 2026-09-28 00:35

### Completed
- **Item 08 · Q4b, does the rate keep falling? — SOLVED.** `reports/ml_nature.md`
  §35; tables `reports/rate_drift_tables.md`; data
  `learning/data/ensemble/ridge100_prefix_calls.csv` (25 pre-fix `csearch`
  calls at `value − 1` on §34's cell), `ridge100_prefix_run.log`; one witness
  lowered under `learning/data/ensemble/solutions/` (`i005`, 26 → 25).
- `learning/rate_drift.py`: `prefix-run` (item 04's `prefix` variant —
  `old_close_count` + `old_rule_order`, Theorem 2 on — one call per instance,
  deadline capped by the wall, resumable, `sat` witnesses saved monotonically);
  series assembly (10–75 campaign + 100 cell per configuration; an instance
  the pre-fix run shows non-optimal leaves every series at 100); censored
  maximum likelihood (Tobit) for exponential / quadratic / power / saturating
  laws with `σ(n)`, windows 10–100 and 40–100, stratified bootstrap bands
  (parallel, spawned pool); the 100 cell's censored-normal location with a
  profile interval; readings of 125 incl. §16(e)'s and two pointwise ones;
  fix-cost pairing post-fix vs pre-fix; the class cost table.
- **Like with like**: the six recertify counts and every campaign `csearch`
  count below 100 are pre-fix (workers forked 2026-09-24; files written before
  the fix); `default` is fix-invariant; §34's `csearch` is post-fix. §16(e)'s
  0.04-decade "match" compared the `default` law with the pre-fix `csearch`
  record; on its own `csearch` row it sat 0.22 below.
- **Pre-fix run** (15.2 core-hours, 75 min, 16 workers beside 36 foreign):
  5 `unsat` (9.00–9.29), 1 `sat` (`i005` at k = 25 — the value was not
  optimal; its §34 censored counts were witness-search bounds), 19 censored
  at ≥ 9.25–9.35 (2,086–2,400 s at 0.8–0.9 M nodes/s).
- **Result**: over 75 → 100 the ridge's rate is 0.116 [0.110, 0.121] (pre-fix
  `csearch`) / 0.140 [0.128, 0.156] (`default`) by the cell's location, against
  0.092–0.095 over 60 → 75; the quadratic's curvature on 10–100 turns from
  −4.4/−6.9 × 10⁻⁵ (10–75) to +3.0/+1.8 × 10⁻⁵ with the cell, positive on
  40–100. **Not sub-exponential** (power law loses by 1,000–1,200 AIC
  everywhere); **the drift reverses on the ridge** over 75 → 100 and survives
  on the d = 4 neighbour (5-instance cell). At 125, pre-fix `csearch`, the
  exponential refit on 10–100 gives **11.43 [11.36, 11.51]** with the record
  (11.21, 11.22, 11.66) 0.2 either side, §16(e)'s drifting 11.00 0.22 below;
  the readings carrying the 75 → 100 rise forward (12.4–12.6) are 0.8–1.4
  above the record — **the rise is not sustained to 125 in the corpus class**.
  d = 4: record median 10.78 sits on §16's drifting law (10.61), 0.65 below the
  exponential refit.
- **Revised law**: `log10 nodes = −0.24 + 0.0934 n` (ridge, pre-fix `csearch`),
  no resolvable drift, σ → 0.5 at 100; at 125 median 2.7 × 10¹¹ nodes (2.3–3.2
  on the median, ×/÷ 10 per instance), 55 h per refutation on one core at
  1.4 M nodes/s (record 25–72 h). Fix ratio on the 100 cell **≥ 2.34×**
  (exact 2.15 on `i012`; four lower bounds to 3.15). Withdrawn instances: the
  two still open have the median (55 h) inside their 5-day budget but not the
  tail; re-refuting all eight 125 × 125 on the fixed code ≥ 130 h (5.3 days)
  per instance median, ~6 core-weeks, d = 2 tail a week or more each.
- Tests: `tests/test_rate_drift.py` (8) — rate = d mean/dn for all four laws,
  Tobit recovers an exact exponential under 90% censoring (and the as-exact
  reading is biased low, the quadratic finds no curvature, the power law
  loses), cell location by hand (exact → 1.0; one exact + two bounds → above
  the censored median; all censored → no upper end), bootstrap band covers the
  fit, fix-cost pairing on temp CSVs incl. the `sat` exclusion, record
  comparison and hours arithmetic, on-disk records, fix-ratio summary and
  class cost table. Full suite: 1,178 passed, 2 skipped, 1 xfailed in 440 s (loaded machine), re-run after the last code edit.
  `solutions/` untouched; recertify (8 workers) untouched.

### Blockers
- None. 19 of 24 pre-fix calls censored at 2,400 s on a machine at load 37–42
  (28 foreign `bench/run.py` workers appeared at 23:00), so the pre-fix cell
  is itself mostly lower bounds; its location rests on the 75 cell's spread.
  Both `sat` and `unsat` answers of the pre-fix rule are labelled as what they
  are (a `sat` verifies; an `unsat` is a refutation under the over-pruning
  rule, not a certificate).
- A bootstrap pool launched from a `python -` stdin script cannot be
  re-imported by `spawn` and respawned failing workers into a 40 MB log until
  killed by PID; the module's pool is launched from a file and is fine.
- The d = 4 series at 100 is §16(d)'s five instances with four censored
  values from 900 s descents, weighed accordingly.

### Next
- Item 09 · Q3: the cover excess as a quantity of the random bipartite
  incidence graph (cyclomatic number `n_ones − n − m + c`), against the 2-core
  / k-core thresholds and the random-intersection-graph literature; a
  derivation of where the ridge should sit per `m / n`, tested against §25's
  measured peaks.

## Iteration 9 — 2026-09-28 02:05

### Completed
- **Item 09 · Q3a, why cover excess two — SOLVED (as the statement the item
  allows: none of the candidate thresholds coincides with the ridge, with the
  numbers, plus the mechanism the ridge is a transition of).**
  `reports/ml_nature.md` §36; tables `reports/cover_excess_tables.md`; data
  `learning/data/ensemble/cover_excess_measures.csv` (9,497 rows: peeled
  2-/(3,2)-/(2,3)-/(3,3)-cores and the dominance-reduced instance for every
  certified instance at n ∈ {50, 60, 75}), `cover_excess_states.csv` (6,840
  rows at n = 20, 25: exact boundary-feasible, fitting and reachable closed-set
  counts at optimum − 1), three run logs. `literature/MISSING.md` gained the
  list of random-graph / core / random-intersection-graph papers cited from
  memory in §36, none held.
- `learning/cover_excess.py`: the incidence graph as a two-type configuration
  model with the generators' degree distributions and the empty-row repair;
  the (k_C, k_P)-core peeling fixed point, core sizes and cyclomatic numbers,
  emergence thresholds by bisection, scan-then-bisect inversion; peeling and
  dominance reduction on instances; §25's peaks with the new candidates
  (natural-value scoring, constancy, calibrated predictions); exact subset-DP
  counts of feasible / fitting / reachable closed sets (n ≤ 25) with the
  random-model prediction of the feasible count. Analytic cores check against
  peeled cores to 0.002 (2-core share) at m ≥ n; 0.03–0.15 high at m ≤ n/4.
- Result over the 25 measured peaks (n = 50–75, m/n ∈ {2, 1, ½, ¼, ⅛}, both
  generators): giant / 2-core emergence 0.34–0.78 decades below the ridge,
  further below the fewer the products; (3,2)- and (2,3)-core emergence
  0.11–0.45 below with the same drift; (3,3)-core crosses the ridge (+0.08 at
  2n, −0.25 at n/8); XORSAT-style "2-core cyclomatic = core customers"
  0.06–0.37 below; connectivity moves with n. Excess 2 at its natural value:
  mean 0.039, max 0.084, flat residual −0.07…+0.01 across ratios; its
  tree-free form "2-core cyclomatic number = n" 0.047. Calibrated at m = n,
  the excess (2.40), the 2-core's cyclomatic number per core customer (1.68 /
  1.73, i.e. core excess ≈ 2.7) and the dominance-reduced excess (2.66) all
  score 0.035–0.052 — one condition read on three subsets of the cover, not
  separable at the grid's 0.05-decade resolution. Constancy: 2-core excess CV
  0.101 (range 2.11–3.14) vs excess 0.127.
- Mechanism (n = 20, 25; 6,840 instances): the number of closed sets whose
  boundary fits optimum − 1 is monotone in density (saturates at 2^n),
  predicted by the random model to 0.0002 decades, and anticorrelated with the
  nodes (Spearman −0.87); the number of sets *reachable* from ∅ through fitting
  steps equals the default node count to 0.03 (fixed) / 0.06 (Bernoulli)
  decades at the median on connected instances (nodes ≤ reachable on 99.1%;
  Spearman 0.99 / 0.97) and peaks where the nodes peak in all 8
  connected-instance series. The ridge is a percolation statement about the
  subset lattice under the boundary cost, not about the incidence graph, which
  is why no incidence-graph threshold locates it.
- Tests: `tests/test_cover_excess.py` (12) — degree pmfs and repair, size
  biasing, 2-core at the giant threshold, core order (2,2) < (3,2) < (3,3),
  regular bipartite fixed point, peeling and cyclomatic numbers by hand,
  components, dominance reduction, four-cycle measures, inversion and
  connectivity, planted excess-2 ridge scored exactly, reachable/fitting
  counts against brute force on the 4-cycle. Full suite, re-run after the
  last code edit: 1,190 passed, 2 skipped, 1 xfailed in 343 s (loaded
  machine). `solutions/` untouched (git status clean there); recertify
  (9 workers) untouched.

### Blockers
- None. The item's alternative deliverable was taken: no threshold coincides.
  Two compute notes: the exact reachable-set DP at n = 25 costs 13 s per
  instance at load 35, so n = 25 is 40 per cell; the `tables` stage is 4.5
  min because the core inversions scan 100 points before bisecting. One lost
  run: a section appended after the `if __name__ == "__main__"` block left
  `STATES_CSV` undefined when the module ran as a script.
- Literature: none of the random-graph papers cited in §36 is held; the
  fixed-point method is standard and is checked against peeled cores here,
  but every citation should be verified before quoting (listed in
  `literature/MISSING.md`).

### Next
- Item 10 · Q3b: is the ridge's *height* a function of the same quantity —
  fit peak median nodes against (n, excess, m/n) across all series; §36's
  `cover_excess_measures.csv` has the 2-core and reduced-instance sizes per
  instance if the height wants the core's size rather than n.

## Iteration 10 — 2026-09-28 03:41

### Completed
- **Item 10 · Q3b, is the ridge's height a function of the same quantity? —
  SOLVED (a formula with held-out error; the height needs `m` separately, as
  `n · log(m_eff / n)`, and the excess at the peak adds nothing).**
  `reports/ml_nature.md` §37; tables `reports/ridge_height_tables.md`; data
  `learning/data/ensemble/results_height.csv` (3,380 rows, one per new
  instance, both configurations; manifest `manifest_height.csv`),
  `height_effective_m.csv` (products with ≥ 2 customers per Bernoulli
  instance at n ≥ 15, by regeneration), three run logs; witnesses under
  `learning/data/ensemble/solutions/`.
- `learning/ridge_height.py`: peaks for every (generator, m/n, n) series
  through §25's `peak_table` (heights flagged censored / grid-edge), §35's
  100-cell location as a held-out point, the new cells (Bernoulli m = 4n at
  40–75, 8n at 50–60, a finer 2n grid at 50–75, and — because they are cheap —
  m = n/4 and n/2 at n = 100, both generators, 30 per cell), eighteen
  candidate laws fitted per generator and pooled with leave-series-out,
  leave-n-out, ≤ 60 → 75 and ≤ 75 → 100 errors (100 never fitted), the excess
  partial, the surface-collapse statistic (raw / minus own peak / minus fitted
  H) and the width table.
- New cells: 3,380 instances in 82 cells, all certified under both
  configurations; 10 refutations censored at 120 s (n = 75, m = 300), none at
  100. ~50 min of 16 workers in three launches.
- Result (`default`, 15–75 fitted, 54 exact peaks pooled): the height at the
  ridge is `log10 nodes ≈ −0.10 + n (0.089 + 0.058 log10(m_eff / n))`,
  `m_eff` the products with two or more customers — 0.0175 decades per
  customer per doubling of effective products — leave-series-out 0.20,
  leave-n-out 0.21, ≤ 60 → 75 MAE 0.33, and it predicts the two certified
  n/4 ridges at 100 to +0.16 / +0.21. Fixed generator alone: the log-clique
  form `−0.16 + n (0.1325 − 0.0767 log10(1 + 2.4 n/m))`, leave-series-out
  0.136, n/4 at 100 to +0.10. `n`-only law: 1.15; `a + b n + c m`: 1.10;
  excess-only laws: ~1.0. Same ranking under `csearch`.
- The Bernoulli climb per doubling of m saturates (1.0–1.6 decades at
  n/4 → n/2, 0.1–0.25 at 4n → 8n) because the effective products saturate at
  the excess-2.4 ridge (m_eff/n 0.24 → 2.1 from m = n/4 to 8n); per doubling
  of m_eff the increments are flat at ≈ 0.017 n, which is what the fixed
  generator (m_eff = m) shows as §25 (g)'s "1–1.5 decades per doubling".
- The excess at the peak: slope of the residual +0.15 per unit (fixed) and
  −0.18 (Bernoulli), opposite signs; held-out gain −0.01 to +0.07 decades.
- Collapse at 50–75: with each series' own height removed, the shape is one
  function of the excess (r² 0.86 / 0.89 / 0.94, dispersion 0.8–0.9 decades,
  not growing with n); in `col_mean` r² ≤ 0.2; degree / branching 0.81–0.85.
  Widths: 0.25–0.51 decades of excess at half a decade below the peak,
  asymmetric (sparse side short for m ≥ n), narrowing slowly with n.
- At 100 the laws reach the low-ratio ridges (+0.1–0.2) and miss the m = n
  location by 1.3–1.9 decades (§35's rise, restated): the 75 → 100 rise is a
  not an artifact of the linear-in-n form — and it grows with m/n: the two
  certified n/2 ridges at 100 (fixed 8.10, Bernoulli 7.80; the ridge cells
  13 and 8 of 30 censored at 120 s above the median) sit 0.6–1.1 decades
  above the law. Rates per customer 60→75 vs 75→100: n/4 0.04 → 0.055, n/2
  0.07 → 0.10, m = n 0.095 → 0.14.
- The finer Bernoulli 2n grid lifted §25's peaks by up to 0.5 decades
  (n = 60: 5.09 → 5.59; n = 75 now interior at 7.15).
- Tests: `tests/test_ridge_height.py` (10) — extended ratio labels, the cell
  design and its order, design-matrix shapes, exact recovery of planted
  `n·g(r)` and log-clique laws with zero held-out error under all four
  schemes (100 never fitted), excess partial zero when not planted, model
  table plumbing incl. the 100-cell check, increments per doubling by hand,
  collapse statistic on a perfect and a broken collapse, width crossings on a
  triangle, the 100-cell location against §35. Full suite: 1,200 passed, 2 skipped, 1 xfailed in 342 s (loaded machine), re-run after the last code edit.
  `solutions/` untouched; recertify (8 workers) untouched.

### Blockers
- None. Three compute notes: the first launch put the n = 75, m = 300 cells
  first (about three worker-minutes each against two seconds at n ≤ 60) and
  was stopped and reordered; the first m = 8n grid (nominal 1.1–2.2
  customers per product) lay entirely on the dense side of the ridge because
  the generator's empty-column repair adds about e^{−c} to the realised
  density, and was extended down to 0.7; the low-ratio 100 cells were added
  mid-session because the law prices them at minutes (they took 55 min of 16
  workers, the n/2 ridge cells at 100 running into the 120 s deadline on
  their upper half). Two n = 100, m = 50 Bernoulli instances left the 600 s
  solve budget uncertified (verified upper bounds 24 and 22); excluded from
  the peaks, not re-solved.
- Seconds are from a machine at load 40–45 (24 foreign `bench/run.py`
  workers and 8 recertify workers beside these 16); nodes are the claim.

### Next
- Item 11 · Q2: the bound harness (validity over every certified instance,
  `learning.extremal` as adversary, tightness on the 338 gap instances against
  `max(lb_best, tw + 1)`) and three candidates, the first the pathwidth branch
  rule over cut vertices (Fellows & Langston 1987 Lemma 4.3 / Kinnersley 1992
  Corollary 4.2 — known, to be cited, not claimed).

## Iteration 11 — 2026-09-28 05:40

### Completed
- **Item 11 · Q2, the bound harness and three candidates — SOLVED (the
  harness works; each candidate has a verdict; the kill is met).**
  `reports/ml_nature.md` §38; tables `reports/bound_harness_tables.md`; data
  `learning/data/ensemble/bound_harness_values.csv.gz` (one row per
  certified instance evaluated: three values, their seeds, seconds,
  subproblems, censored flags), `bound_harness_attack.csv` (144 adversary
  jobs at 8–15) and `bound_harness_attack_large.csv` (36 at 18–25), five
  run logs. Scratch witnesses under `learning/data/bound_harness/`
  (git-ignored).
- `learning/bound_harness.py`: a candidate is any callable
  `f(graph, matrix, budget) -> int | (int, dict)` returning a lower bound in
  optimum units (`--extra module:function` plugs one in); stage `validity`
  runs every candidate on every certified instance under a per-instance
  budget (deadline + subproblem cap; on exhaustion the recursion returns its
  seed, still valid, and flags `censored`), resumable, largest first; stage
  `attack` is `learning.extremal.local_search` climbing `f − optimum` with
  the exact solver as oracle (8 sizes × 3 seed families × 2 restarts × 210 =
  10,080 evaluations per candidate; `--sizes` for more); stage `tables`
  writes the "above optimum (must be 0)" column beside tightness and the
  shares above `lb_best` and above the reference `max(lb_best, tw_lo + 1)`
  on all rows and on the 338 gap instances, per band, the gain over each
  candidate's own seed, the counterexample list (drawn and re-certified when
  non-empty) and the kill verdict.
- Three candidates, all proved valid: `cut-branch` (the plan's: the
  Fellows–Langston / Kinnersley branch rule recursively over cut vertices,
  clique-seeded), `sep-branch` (the rule with the cut vertex replaced by a
  separator — Lemma A in §38, proved there: three components of `H − S`
  pairwise linked through components of `H[S]` with pw ≥ k force pw ≥ k + 1 —
  over cut vertices, maximal-clique intersections, clique-tree adhesions of
  the MCS-M completion and edges on small subgraphs; seeded by `max(ω − 1,
  tw)` with exact treewidth on subgraphs ≤ 16 / ≤ 22 at the top), and
  `contract-branch` (`sep-branch` on every minor of the contraction-degeneracy
  sequence, by minor monotonicity; minors seeded also by minimum degree).
- Result: over 49,862 certified instances (corpus 6,376 at 9–134, all;
  campaign 37,800 at 10–40, all; upward 5,686 of 6,773 at 50–100 — complete
  at 60/75/100, 52% at 50, the rest not reached under the wall) **no candidate
  is ever above the optimum**, and all three survive 11,880 adversarial
  evaluations each (10,080 at 8–15 + 1,800 at 18–25), reaching the optimum in
  all 60 jobs. On the 338 gap instances: `cut-branch` beats `lb_best` on 0,
  `sep-branch` on 15 (its exact-tw seed; 0 above the reference),
  `contract-branch` on 84 and above the reference on **8 (2.4%)** — all 8 a
  minor's seed (clique / min degree / tw of a ≤ 16-vertex minor) at `lb_best + 1`
  where `tw_lo` is a 1-second interval, `value == seed`, no branching. The
  branch rule itself adds **at most one**, on 0.1–0.3% of rows and on zero gap
  instances; where it lifts a candidate above the reference (43 / 63 / 62
  rows) the candidate is tight and `pw = tw + 1`: forests (12; the five
  Warwick "2 orders per product" instances the reference misses are all
  recovered), sparse campaign trees of cliques at 10–40, two upward at 60/75,
  `Warwick 1857` at 30. Among the 5,003 exact-tw rows with `pw > tw` the
  candidates are tight on 1.2%; on all 142 gap instances with `pw > tw` exact,
  on none. Cost 7.4 core-hours; censored 665 / 1,501 rows (31–75 customers),
  which carry their seed.
- Kill verdict: **met** — `cut-branch` 0.0%, `sep-branch` 0.0%,
  `contract-branch` 2.4% of the gap instances above the reference, the last
  entirely the minors' treewidth seeds where `tw_lo` is a 1-second interval.
- Tests: `tests/test_bound_harness.py` (14) — hand instances (stars, spiders,
  three K4 at a hub, the theta graph with its edge separator) against the
  exact optimum, the spider-of-spiders recursion, Lemma A's pairwise-link
  condition, the separator family, seeds, budget exhaustion returning the
  seed, the contraction sequence against `_contraction_degeneracy`, a
  user candidate that overclaims caught by the "must be 0" column, the
  evaluate protocol. Full suite: 1,214 passed, 2 skipped, 1 xfailed in 107 s, on the final code. `solutions/` untouched;
  recertify (9 workers) untouched.

### Blockers
- None. Upward is a 5,686-of-6,773 sample (wall), said in §38. Three things
  cost minutes: materialising every maximal clique of a dense 125-vertex
  graph (hang; `islice` cap), recomputing the separator family per
  subproblem (budget spent on chordal completions; computed once and
  restricted), and a seed diagnostic undefined on disconnected graphs (7,253
  rows rerun; values unchanged). The upward run was moved to its own file
  and merged because two processes appending to one `.csv.gz` corrupt it.
  The `Random-*` gap "beats" are read against `tw_lo`, a 1-second interval;
  exact treewidth would retire them. Recertify (9 workers) untouched.

### Next
- Item 12 · Q7: the three tree-decomposition `sorry`s of `Sandwich.lean`
  (`treewidth_le_pathwidth`, the branch lemma — Lemma A of §38 is the
  separator form, with its layout proof written out — and the conjecture
  statement); `lake build` must pass; a gap list is an acceptable deliverable.
