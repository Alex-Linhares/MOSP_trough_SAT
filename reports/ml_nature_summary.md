# Machine learning and the nature of MOSP — the synthesis

*2026-09-26, loop0003 item 13 (plan 2 §2.11); brought up to date 2026-09-28
after loop0004 and the Lean proof of Yanasse's equality. One paragraph per
claim the three plans produced: `reports/ml_nature_plan.md` asked ten
questions, answered in `reports/ml_nature.md` §1–§14 (loop0001, loop0002);
`reports/ml_nature_plan_2.md` asked eleven, answered in §15–§27 (loop0003,
§27 its reserve item); `reports/ml_nature_plan_3.md` asked seven, answered in
§28–§40 (loop0004, thirteen items). Beside the loops, on 2026-09-27, the
MOSP–pathwidth equality was proved in Lean (§26's resolution note). Every
number below is copied from the section cited and regenerates by the command
that section names; this file computes nothing and is not a bound. Where a
later section corrected an earlier one, the paragraph gives the corrected
value and cites both.*

*Audited 2026-09-30 against the code and the corpus. Current state, where it
differs from the dated paragraphs below: `rule+cs-dfs` is the default
upper-bound strategy since 2026-09-28 (§8 #14), and on 2026-09-29 the seed
was measured not to change certification cost at 100–125 customers (§28
addendum); the corpus is 6,374 of 6,376 certified, two open
(`Random-125-125-2-2_0` at 25, `-2-3_0` at 21); the Lean development has one
`sorry` (the §24 conjecture) and, since loop0005, proves Table 1's
equivalences in `lean/MOSPFormalization/Complex/` (2.10); the expansion bound
is Harper's vertex-isoperimetric bound, no novelty; and the encoding's
faithfulness is proved in `Encoding.lean`, so §10's Lean gap is the
Python-to-clauses step, not the encoding.*

**How to read a paragraph.** Each ends with three lines: the **size range**
the claim covers, the **regenerate** command (the section holds the full form
with flags and timings), and a **status** from the plan's four words —
*finding* (a measured statement about the instances or the solver),
*conjecture* (checked on every certified instance, proved nowhere), *proposed
solver change* (measured behind a flag or in a report, never enabled here) and
*closed question* (measured, answered, not to be rebuilt) — plus *theorem* for
what `lake build` accepts without `sorry` (§26, §39, §40).

**The rules the work ran under.** A prediction is never a bound: nothing
learned reaches `satisfiability/mosp_solver.py::_lower_bound` or any path that
decides `k`. No solver default changed in four loops; the one change to
solver code that changed an answer, the C `better_move` fix, landed through
the owner (`reports/better_move_bug.md` §7), and loop0004's additions to the
solver — §31's variant flags in the C, §28's `rule+cs-dfs` and §29's `mcnh`
strategies — default to today's behaviour and are the default of nothing.
*(Superseded 2026-09-30: the owner made `rule+cs-dfs` the default on
2026-09-28, §8 #14.)* The
Lean proof of `mospValue = pathwidth (mospGraph) + 1` (`MOSPGraph.lean`,
commit `d723d173`) also landed outside a loop, on 2026-09-27. Every split
groups by file ∪ MOSP-graph isomorphism class. Hardness is counted in nodes,
never seconds. A censored call is a lower bound, never a missing value. Every
`csearch` node count is dated against the fix (§11 below). Every conclusion
states its size range: the corpus is 6,376 instances at 9–134 customers, the
campaign 37,800 generated instances at 10–40 plus 6,785 at 50–100, 2,750 at
50–75, 3,380 at 40–100 (§37) and one 25-instance ridge cell at 100 (§34), and
nothing below 100 is evidence about 125 × 125 except through a stated
extrapolation.

---

## 0. In one page

- **The corpus is 3,667 distinct MOSP graphs, not 6,376 instances**, a quarter
  of them complete graphs; the generators are fingerprintable at 94.4% from
  structure alone; instance space is a lattice of 74 size cells (§1, §2).
  *(2026-09-30: 6,374 of the 6,376 carry a certified optimum; two
  125 × 125 entries withdrawn after the `better_move` bug are still open.)*
- **`mospValue = pathwidth (mospGraph) + 1` is a `sorry`-free Lean theorem**,
  both directions, over the MOSP graph; the `Reduction.lean` statement it
  replaces was over the pattern graph and false (§26, resolution note). So
  the sandwich `degeneracy + 1 ≤ optimum ≤ bw_rcm + 1`, checked on every
  certified instance, and `treewidth + 1 ≤ optimum` are theorems about the
  optimum itself; 34 named theorems proved, one `sorry` kept on purpose
  (§5, §26, §39, §40). *(2026-09-30: loop0005 added Table 1's equivalences
  in `Complex/`, still one `sorry` in the whole development, 2.10.)* Min-fill treewidth + 1 is the best point estimate to
  about 50 customers and 4 stacks high at 125 (§4, §14).
- **The proved bound fails structurally**: three of its four components bound
  treewidth, pathwidth strictly exceeds treewidth on 48.5–76.3% of the 338
  instances it misses by two or more, and no graph on ≤ 9 vertices has
  `pw − tw ≥ 2` (§6, §21, §27). Exact treewidth + 1 beats the solver's bound
  on 933 corpus instances; no mined formula and **no branching-aware bound at
  any separator the clique structure exposes** beats `max(lb_best, tw + 1)`
  on a gap instance — three candidates, valid on 49,862 instances, through a
  harness any bound can enter (§24, §38). The branch lemma as the Lean file
  stated it was false; the corrected lemma and its separator form are proved
  (§39, §40).
- **Hardness has a ridge** at cover excess `(n_ones − m) / n ≈ 2–2.4` — a
  density condition, not a percolation threshold; the transition is in the
  reachable region of the closed-set lattice (§11, §25, §36). Its **height
  needs `m` separately**: `log10 nodes ≈ −0.10 + n (0.089 + 0.058
  log10(m_eff / n))` (§37). On the `m = n` ridge the rate **stopped falling**
  between 75 and 100 (0.116 per customer against 0.092–0.095 over 60 → 75),
  the 100 cell does not certify in 28 core-hours, and read like with like a
  constant-rate law puts the 125 × 125 ridge refutation at **2.7 × 10¹¹
  nodes, 55 h on one core pre-fix, ×/÷ 10 per instance**, the record's three
  counts within 0.2 decades (§34, §35). Hardness is a property of the
  labelled graph for the search and of the formula size for SAT (§13, §30).
- **Every refutation at n ≤ 40 is sound on twenty searches and carries a
  certificate a third party checks in milliseconds**; 92.0% also carry a
  DRAT proof; at 50–100, zero disagreements on 25,800 calls, affordable
  everywhere but the eight `Random-100-100-2/4` instances (§15, §17, §32,
  §33). The harness found a false `unsat` at the *optimum* in the C
  `better_move`, fixed by the owner; both halves of the fix are necessary,
  the reordering carries 81% of its cost at n ≤ 40, and no cheaper sound
  composition exists (§31).
- **Search rules measured, none worth enabling for refutations**: fan order
  changes 0.0% of nodes; a relabelling portfolio wins 1.00–1.01×; Theorem 2
  always-on saves 6.6% of nodes and loses 5% of seconds; labels and fan order
  pay only on the satisfiable side (§18, §20, §22, §33).
- **Imitation is closed, and so is the LightGBM question**: the optimum is
  never unique, the set-valued policy beats the one-sentence rule by 0.008
  against a kill of 0.02 (§7, §8, §23), and over the whole corpus the rule
  seeds the DFS better than the learned policy on every statistic (94.2% vs
  92.1% exact, 263 / 80) with no model (§28). The rule is not the
  literature's MCNh, now reproduced and registered (§29). *(2026-09-30:
  `rule+cs-dfs` is the default since 2026-09-28; at 100–125 customers it
  changes the upper bound and not the certification cost, nodes within 0.2%
  on four instances, §28 addendum.)*
- **A cost model puts 88–89% of the 100–125 refutation counts within a
  decade**; it sized the 100 ridge cell correctly from the heuristic upper
  bound and is 1.1 decades under from the certified optimum (§19, §34).

---

## 1. The corpus and the instruments

**1.1 The corpus is 3,667 graphs (§1).** By nauty certificate of the MOSP
graph the 6,376 certified instances hold 3,667 distinct graphs: 42.5% of the
corpus is isomorphic copies, 1,669 instances (26.2%) are complete graphs with
optimum `n`, all from Harvey and Simonis, and the 46 `MOSP_Instances/Challenge`
files are the Miller, Shaw and Wilson files under a second name, certified
twice. Redundancy is 44.6% at n ≤ 30 and 13.2% above; Chu & Stuckey, SCOOP,
Shaw and Wilson contain no duplicates. 157 graph classes span more than one
source file (the largest spans eleven), so grouping by `source_file` leaks
isomorphic copies across a split; the honest grouping is file ∪ class
(`learning.fingerprint.union_groups`), which is a five-region hold-out in
practice (largest group 1,620 instances, §4). The audit came free: isomorphic
instances carry equal optima in all 203 multi-member classes. The effective
sample is 3,287 classes at n ≤ 30 and 380 above, 200 of them Chu & Stuckey.
§28 measured what the leak was worth: about a seventh of the learned seed's
2026-09-22 gain (709 / 13 over `cs-dfs` by file, 602 / 19 by file ∪ class).
*Size range:* all 6,376, 9–134. *Regenerate:* `python -m learning.canonical --workers 16`.
*Status:* finding.

**1.2 The generators are fingerprintable (§2).** A random forest on 28
structure-only features assigns 94.4% of instances to their collection with
the source file held out (93.3% with isomorphic copies held out too), 98.8% at
equal `(n, m)` where the baseline is 61.6%. The fingerprint is two lines a
person can state: every Harvey instance has constant column sums, constant row
sums or both, and no other generator's does; Faggioli–Bentivoglio caps the
largest product at half the customers; Simonis is dense with large products;
Chu & Stuckey is sparse where nothing else is, its density class is `col_mean`
to within rounding and its seed index is at chance. The UMAP map is a lattice
of 74 `(n, m)` streaks with empty regions between, and the 24 SCOOP industrial
instances fall in the sparse corner with all 200 Chu & Stuckey. A result on
one collection is a result about that generator.
*Size range:* all 6,376; same-size test 10–40. *Regenerate:* `python -m learning.fingerprint`.
*Status:* finding.

**1.3 Node counts reach the ledger (§3).** `solve_mosp_exact(..., stats=dict)`
returns `nodes`; `compute_ledger.csv` carries a `nodes` column written by
`csearch` and `recertify`. On the 6,135 certified instances at n ≤ 40, 38.5% of
refutations at `optimum − 1` visit zero nodes (the root's cost check refutes;
2,357 of those 2,360 are Challenge complete graphs), the p90 grows about 10×
per ten customers (4 → 23 → 108 → 1,764), and over the fifty `Random-30/40`
instances median nodes fall monotonically with density (1,068 → 6 from
density 2 to 10). The `csearch` configuration never cost more than 1.1× the
defaults there. The run is itself a second refutation of every optimum it
touched: 12,270 calls, all `unsat`.
*Size range:* 9–40 (96% of the corpus by count). *Regenerate:* `python -m learning.node_counts --max-customers 40`.
*Status:* finding (instrumentation).

**1.4 The generated campaign is free at n ≤ 40 (§9, §10).** 252 cells
(`n ∈ {10, …, 40}`, `m ∈ {n, 2n}`, fixed `d ∈ {2, …, 10}`, Bernoulli
`p ∈ {0.025, …, 0.5}`), 150 instances per cell, 37,800 in all, every one
certified, refuted at `optimum − 1` under both configurations, featured and
canonicalised in 2.16 core-hours and eight and a half minutes of wall clock;
every manifest row regenerates byte for byte from its seed. The refutation is
0.5–0.7% of the cost: seconds are a smooth function of `n` alone while node
counts vary by three orders of magnitude across cells at fixed n = 40, so at
these sizes seconds do not see hardness at all. 6,511 instances (17.2%) are
complete graphs, 7,101 (18.8%) decompose (kept and counted; Chu & Stuckey
discard them), 10,479 (27.7%) are isomorphic repeats within their cell, almost
all at the complete or near-empty edges; 145 cells and 20,652 distinct graphs
are the useful core. Realised density (`col_mean`) is the coordinate: the
fixed generator's empty-row repair inflates `d = 2` to 2.1, and Chu &
Stuckey's "density 2" is 2.7–2.8 realised. loop0004 added 3,380 instances in
82 cells — Bernoulli `m = 4n` at 40–75 and `8n` at 50–60, a finer `m = 2n`
grid at 50–75, and `m = n / 4` and `n / 2` at 100 for both generators — 3,378
of them certified (§37), and the 25-instance `m = n`, `d = 3` cell at 100, of
which one is certified and 24 are verified upper bounds (§34).
*Size range:* 10–40; the additions 40–100. *Regenerate:* `python -m learning.ensemble --item02 --workers 16 --verify-manifest 0`; `python -m learning.ridge_height --stage run`; `python -m learning.ridge100 --stage run`.
*Status:* finding (infrastructure; the artifact is `learning/data/ensemble/`).

**1.5 The bound harness (§38).** `learning/bound_harness.py` takes any
candidate lower bound as a function `f(graph, matrix, budget) -> int` and
returns a verdict: the "above optimum (must be 0)" column over every certified
instance (corpus 6,376, campaign 37,800, upward 5,686 of 6,773 — 49,862 rows),
an adversarial record from `learning.extremal.local_search` climbing
`f(G) − optimum` with the exact solver as oracle (60 jobs, 11,880 evaluations
per candidate at 8–15 and 18–25), and tightness on the 338 gap instances
against the honest reference `max(lb_best, tw + 1)`; a row above the optimum
is drawn and re-certified. Under a per-instance budget a candidate that runs
out returns its seed and the row is flagged censored, so every value is a
valid bound that might have been higher. Three candidates cost 7.4
core-hours. It is the place the plan's "a prediction is never a bound" rule
sends a candidate to become one or be refuted.
*Size range:* 9–134 for validity; the adversary 8–25. *Regenerate:*
`python -m learning.bound_harness --stage {validity,attack,tables}`; `--extra module:function` plugs a candidate in.
*Status:* finding (instrumentation).

---

## 2. What determines the optimum

**2.1 Min-fill treewidth + 1 is the best point estimate, and a bound on
nothing (§4).** Among thirteen pathwidth-adjacent invariants added to the
feature table, one carries almost everything: `tw_min_fill + 1` is exact on
85.7% of the corpus at MAE 0.188, against 84.6% / 0.239 for the solver's upper
bound and 77.0% / 0.431 for its lower bound, leading in every size band. It
sits below the optimum on 481 instances and above on 428. The plan's kill
(no invariant moves grouped MAE by 0.02) is cleared ten times over on
structure alone (0.436 → 0.220 by file) and narrowly or not at all once the
bounds are present (−0.012 by file, −0.044 by file ∪ class); on the residual
over the proved bound the group adds nothing (−0.004): the invariants know
what the bound knows, expressed differently. `bw_rcm + 1 ≥ optimum` held on
all 6,376, a theorem checked for free — and since §26's resolution a theorem
about the optimum outright, `MOSPInstance.mospValue_le_bandwidth_add_one`.
*Size range:* 9–134; at 31–60 every model's grouped MAE is above 4 and at
61–134 above 26. *Regenerate:* `python -m learning.dataset --workers 16 && python -m learning.invariants_study --workers 16`.
*Status:* finding; the kill verdict is met against the plan's stated baseline.

**2.2 No clean formula for the residual; a clean sandwich for the optimum
(§5).** The best closed form for `optimum − lb_best` in structure features is
`0.01 · g_deg_std · sep_size / g_density − 0.02`, i.e. `(n − 1) · sep_size ·
σ_deg / μ_deg`, grouped MAE 0.303 against 0.431 for zero and 0.260 for
boosting: degree dispersion is the variable, and no conjecture is stated. For
the optimum both the enumerated search and PySR converge on
`1 + √(g_degeneracy · bw_rcm)` with constants exactly (1, 1), MAE 0.672,
exact 67.1%: `degeneracy + 1 ≤ optimum ≤ bw_rcm + 1` holds on all 6,376, the
ends coincide and force the optimum on 2,823, and where they differ the
optimum sits at the midpoint on median (IQR ⅓–⅔) with its position λ
tracking sparsity (ρ 0.40 with the separator fraction), not size (0.05).
§12 later showed the midpoint is a pooled artifact (2.4 below). The geometric
mean is below the optimum on 1,495 instances and above on 600, and is worse
than `lb_best` at 61–134 (13.06 vs 8.71); `degeneracy + 1` is dominated by the
contraction degeneracy the solver already computes.
*Size range:* 9–134; every grouped MAE dominated by n ≤ 30. *Regenerate:*
`python -m learning.formula_search --workers 16` (PySR rows are not
deterministic). *Status:* finding; the sandwich is a theorem (2.6).

**2.3 The optimum concentrates on random instances (§12).** At every one of
the 36 cells at n = 40 the coefficient of variation of the optimum is under
0.2 (0.004–0.197, median 0.031); the only cells above 0.2 at any size are 32
Bernoulli cells at or below the giant-component threshold, where the optimum
is a small integer with a standard deviation of 0.7–0.9 that does not fall.
Above the threshold the standard deviation is one stack or less at n ≤ 40 and
grows between constant and `√n` at fixed degree, so the CV falls like
`n^{−0.1}` to `n^{−0.5}`; a cell is still two or three adjacent integers with
the mode holding 37–60% of it. `E[opt]` is a line in `n` at fixed degree
(r² ≥ 0.999 in all 17 fixed-degree series) and sublinear below the threshold
(γ ≈ ⅓): the `G(n, p)` picture.
*Size range:* 10–40, `m ∈ {n, 2n}`, 37,800 instances. *Regenerate:*
`python -m learning.concentration --workers 4`. *Status:* finding; kill
(CV above 0.2 up to n = 40) not met.

**2.4 The `E[opt]` formula, and where its constants break (§12, §14, §16).**
`E[opt](n, m, p) ≈ 2.1·(1 − q) + n·[1 − √(1 − q) · 27 / (D + 27)]`, with
`q = 1 − (1 − p²)^m` and `D = (n − 1)·q`, has held-out MAE 0.49 stacks on the
252 cell means, 0.66 when fitted at n ≤ 30 and asked about 35 and 40, and per
instance sits below the optimum on 9,445 and above on 10,641 — an estimate of
a mean, never a bound. On the Chu & Stuckey corpus at 30–125 the *line* holds
(`E[opt] = α·n + β`, r² ≥ 0.986 in every class, no class mean more than 1.2
stacks off) but the constants do not: intercept 4–5 stacks where the formula
has 2.2, slope 0.146 at `col_mean` 2.8 where the formula saturates at 0.22, so
the bias grows linearly to +8.1 at `Random-125-125-2` and stays within ±2 at
densities 4–10; `opt / n` at density 2.8 is still falling at 125 (0.182) as
`0.146 + 5 / n`. At 50–75 on the campaign the line holds again (slope 0.35 per
customer at `d = 4, m = n`; the formula gives 0.34). λ, the optimum's
position in the sandwich, is **not ½**: pooled it is ½ to the digit as in §5,
but by density it runs from 0 below 1.5 customers per product to ⅔ above 6
(ρ 0.63–0.69 with density, 0.24 with `n`).
*Size range:* fitted 10–40; tested 30–125 on 200 Chu & Stuckey instances and
50–75 on 6,750 generated. *Regenerate:* `python -m learning.concentration`,
`python -m learning.scale_test`, `python -m learning.upward`. *Status:*
finding; the formula is a description of the mean at n ≤ 40 and biased above
50 at sparse density; every interval calibrated at n ≤ 40 fails by 50–100 and
is not to be quoted at n ≥ 50 (kill met, §14).

**2.5 The size at which each small-size finding stops holding (§14).** Of the
laws fitted at n ≤ 40 the forms survive to 125 and the constants do not.
`tw_min_fill + 1`, exact on 85.7% of the corpus, is off by 4.2 stacks on
average at 125 and inside its ±1 band on 2 of 25. Conformal intervals for both
the optimum and the nodes cover 0.92–1.00 at 30–40, 0.40–0.74 at 50–75 and
0.08–0.27 at 100–125 for every absolute radius; the `n`-scaled ones hold only
by being 6–10 stacks or 1.4–4.9 decades wide. The item computed the 50–125
corpus node counts itself (`compute_ledger.csv` had the column and no values):
280 calls, 273 settled, 7 censored at 1,500 s in `Random-100-100-2`, 5.65
core-hours, committed as `scale_nodes.csv`.
*Size range:* Chu & Stuckey's 200 `Random-n-m-d` at 30–125; rates above 40
rest on class medians of five, the 125 rows on two and three counts.
*Regenerate:* `python -m learning.scale_test`. *Status:* finding; kill met
for every interval.

**2.6 Both ends of the sandwich are theorems (§26).** In
`lean/MOSPFormalization/Sandwich.lean`, over the repository's `LinearLayout`
and Mathlib's `SimpleGraph`: `degeneracy_le_pathwidth` and
`pathwidth_le_bandwidth` for every finite simple graph, proved through
`vertexSeparation` and Kinnersley's `vertexSeparation_eq_pathwidth`, with
`#print axioms` giving `[propext, Classical.choice, Quot.sound]` on every
theorem named in `learning.sandwich.PROVED` (thirteen when §26 was written,
34 after §40); the layout-level form `pathwidth_le_bandwidthOfLayout σ` is
literally the `bw_rcm` check of §5. The Lick–White and elimination-ordering
forms of degeneracy are proved equal by the greedy ordering. The definitions
are pinned to the corpus's implementations by brute force on all 1,099
labelled graphs on 1–5 vertices (zero violations against networkx's core
number and the exact pathwidth DP) and by kernel `decide` on four graphs. The
corpus recount gives 6,376 / 6,376 on both ends, 3,293 / 3,279 tight, 2,823
with both ends coinciding — §5's number regenerated. §26 as written said the
theorems reached the optimum only through the hypothesis
`mospValue = pathwidth + 1`, then held in `Reduction.lean` with a `sorry`;
2.7 records what became of that.
*Size range:* every finite graph; corpus recount 9–134. *Regenerate:*
`cd lean && lake build; python -m learning.sandwich`. *Status:* theorem
(two, plus the chain and the sandwich statement).

**2.7 Yanasse's equality is a theorem, and the statement it replaces was
false (§26, resolution note of 2026-09-27).**
`lean/MOSPFormalization/MOSPGraph.lean` proves
`mospValue = pathwidth (mospGraph) + 1` for every instance with a requirement
(`∃ c p, requires c p`), `sorry`-free in both directions, where `mospGraph`
has customers as vertices and a clique per pattern. The key graph-level by-product is the Helly lemma
`PathDecomposition.exists_bag_of_isClique`; the proof needs the interval
property and no Hall's theorem and no `IsReduced` hypothesis. The
`Reduction.lean` statements the sandwich section had inherited its trusted
step from were over the *pattern* graph and were false: one pattern shared by
four customers each with a private pattern has `mospValue = 4` and a pattern
graph that is the star `K_{1,4}` of pathwidth 1, which `MOSPGraphExamples.lean`
proves; the false statements are deleted. Consequently
`MOSPInstance.mospValue_le_bandwidth_add_one` is proved outright over
`mospGraph`, `degeneracy_add_one_le_mospValue_of_eq` is replaced by
`degeneracy_add_one_le_mospValue`, and nothing between the corpus sandwich
and the optimum is a trusted step any more — for the contraction and
expansion components of `_lower_bound` as much as for these theorems. The
commit is `d723d173`. The lesson §39 restates a day later: a
stated-not-proved theorem needs a small-instance check before it is
committed, because two `sorry`s in this development were hiding false
statements, not hard ones.
*Size range:* every MOSP instance with a requirement. *Regenerate:*
`cd lean && lake build; python -m learning.sandwich --stage lean`.
*Status:* theorem.

**2.8 `treewidth ≤ pathwidth`, and the branch lemma corrected (§39).** The
`TreeDecomposition` structure of §26 asks for `T.IsTree`, and Mathlib (the
September 2026 master pinned here) has `pathGraph_connected` and nothing on
its acyclicity; `pathGraph_isTree` is proved in 30 lines (every edge
`{i, i + 1}` is a bridge, `pathGraph_isBridge_succ`) together with
`pathGraph_induce_interval_connected`, both about Mathlib objects only.
`PathDecomposition.toTreeDecomposition` reads a path decomposition as a tree
decomposition on the path graph with the same width, so
`treewidth_le_pathwidth` follows by `le_csInf`, and over the MOSP graph
`MOSPInstance.treewidth_add_one_le_mospValue` — the reference `tw + 1` of
§21, §24 and §38, and the treewidth ceiling of §6, now on a checked proof.
**The branch lemma as `Sandwich.lean` had stated it since §24 was false**: it
asked for neither the connectivity of the three branches nor their attachment
to the vertex, and four isolated vertices with `k = 0` satisfy every
hypothesis with pathwidth 0; `old_branch_statement_false` proves the
counterexample in Lean (`pathwidth_bot_fin4`). The corrected `branch_lemma` —
`v ∉ A ∪ B ∪ D`, the three finsets pairwise disjoint, each inducing a
connected subgraph, each containing a neighbour of `v`, each of pathwidth
`≥ k` — gives `k + 1 ≤ pathwidth G`, by the interval argument of Fellows &
Langston (1987) Lemma 4.3 (each branch fills a bag, the middle bag is
`middle_bag_false`); the separation hypotheses of the old statement are
dropped, so it is slightly more general than the literature's phrasing.
`branch_lemma_treewidth` is the treewidth-seeded form §38's `cut-branch`
computes, which implemented the correct rule (components of `G − v`), so no
measurement in §38 is affected. Inventory after the item: `sorry` 3 → 1,
`PROVED` 17 → 28, `Sandwich.lean` 579 → 906 lines, 3 definitions and 14
theorems added, `lake build` 1,640 jobs.
*Size range:* every finite simple graph; kernel-checked instances on 3, 4 and
7 vertices; Python cross-checks on 4–10. *Regenerate:*
`cd lean && lake build; python -m learning.sandwich --stage lean`.
*Status:* theorem (two); the old branch statement is a closed question.

**2.9 The separator form of the branch lemma, §38's Lemma A, is a theorem
(§40).** `branch_lemma_separator` takes a finset `S` and three branches
`A, B, D`, all pairwise disjoint, each connected and of pathwidth `≥ k`, and
for each pair a *connector* — a connected `Q ⊆ S` adjacent to a vertex of
each — and concludes `k + 1 ≤ pathwidth G`; the connected-subset reading is
equivalent to §38's component reading, which `linked_third` in
`learning/bound_harness.py` checks, so the theorem covers the rule as
computed. It is proved through the more general `branch_lemma_linked`, in
which each pair's connector need only be a connected finset disjoint from the
third branch, and its middle-bag step (`middle_bag_false_linked`) is shorter
than the cut-vertex one because no case on where the cut vertex lies is
needed; the cut-vertex lemma falls out as `branch_lemma_of_separator` with
`S = {v}`, a second proof of `branch_lemma`. `branch_lemma_separator_treewidth`
is the form `sep-branch` computes. Six theorems, no definitions; `PROVED` 28
→ 34; `Sandwich.lean` 1,099 lines; the development's one `sorry` is
`conjecture_sqrt_tw_f6`, kept as a statement on purpose. Not formalised:
the component form as a corollary (needs Mathlib's `ConnectedComponent` of an
induced subgraph read back as a `Finset`), and the minor monotonicity that
`contract-branch` also rests on.
*Size range:* every finite simple graph; Python cross-checks on 8 and 11
vertices. *Regenerate:* `cd lean && lake build; python -m learning.sandwich --stage lean`.
*Status:* theorem.

**2.10 Table 1's equivalences are proved in Lean (loop0005, 2026-09-30;
outside the three plans).** `lean/MOSPFormalization/Complex/`, 13 files,
formalises the rows of Linhares & Yanasse (2002) Table 1 against pathwidth:
gate matrix layout, narrowness, interval thickness, one-dimensional logic,
split bandwidth (a sandwich), edge separation (false read as cutwidth, exact
as Lengauer's VSG), PLA folding (simple folding false, multiple folding
exact), node search (the full game, monotonicity via Bienstock–Seymour),
edge search (`band ≤ es ≤ vs + 2`, full game), interval thickness = node
search, and a counterexample to the proof of Kirousis & Papadimitriou (1986)
Theorem 4.1 as written. One named gap, `EdgeSearchMonotonicity` (LaPaugh),
is a hypothesis used by no row, not a `sorry`; the axioms are `propext`,
`Classical.choice` and `Quot.sound` only (`paper1/axiom_check.lean`). The
development's only `sorry` is still `conjecture_sqrt_tw_f6`.
*Size range:* every finite graph. *Regenerate:* `cd lean && lake build`.
*Status:* theorem.

---

## 3. Where the proved bounds fail, and why

**3.1 The bound-defeating family is trees of cliques with branching (§6).**
`lb_best` equals the optimum on 77.0% of the corpus, misses by one on 17.7%
and by two or more on 338 instances (5.3%; 51.0% of Chu & Stuckey, 27.7% of
Faggioli–Bentivoglio). Gap ≥ 2 never occurs below 20 customers. At fixed
`(n, m)` the gap instances are the sparser ones with more dispersed degrees
(`g_deg_cv` d = +1.48), exactly as dense as the random model predicts for
their matrix density. A depth-3 tree on size-free features reads "a connected
sparse MOSP graph, or a dense one with a low-degree customer" and separates
gap ≥ 2 from tight at AUC 0.931 within fixed cells against 0.849 for density
and size; the EBM reaches 0.971 with average precision 0.81 against 0.54; the
lower bounds add nothing to the classifier. The ten smallest gap instances are
all 20 × 10: one connected graph of ten small cliques glued at a few hub
customers with a fringe of single-product customers. The reason is
structural: the trivial, clique and contraction-degeneracy components are all
lower bounds on treewidth + 1, and `optimum > tw_min_fill + 1` certifies
`pathwidth > treewidth` with no heuristic in the certificate on 131 of the
338 and on 8 of the 10 smallest — a certificate that since §39 rests on the
proved `treewidth_add_one_le_mospValue`. Only the expansion bound is a
pathwidth argument; it passed the ceiling on 36 instances. §38 adds that the
family does not branch at any separator the clique structure exposes either:
only 10 of the 338 have a cut vertex with three branches and 99 any cut
vertex.
*Size range:* 9–134; gap statements cover 20–134; the drawn family is
established at n = 20. *Regenerate:* `python -m learning.bound_gap --workers 16`.
*Status:* finding; kill (structure cannot beat density and size) not met.

**3.2 The smallest graph with `pw − tw = 2` has 10 vertices, and the corpus
is not extremal (§21).** Exact treewidth was built two ways (subset DP to
n = 26; a decision search with simplicial reductions to n = 64 under a budget,
censored runs an interval). A bit-flip search with the exact solver as oracle
beats the corpus's worst instance at the same size on `gap` (2 vs 1 at
14–15), on `pw − tw` (2 vs 0–1 at 10 and 13–18), on refutation nodes (3–12× at
every size with a corpus instance) and on `cs-dfs` overshoot (4 vs 2 at 15), in
2.7 core-hours and 727,816 oracle evaluations. The object: a 10-vertex,
21-edge graph — three K₄s glued pairwise at three hub vertices plus a tenth
vertex joined to one non-hub vertex of each — with treewidth 3 and pathwidth
5, vertex- and edge-minimal for `pw − tw = 2` (all 10 vertex deletions and 21
edge deletions evaluated exactly), proved by a K₄, an elimination ordering,
two refutations, the pathwidth DP and the lattice oracle; half the size of the
corpus's smallest (19) and of the smallest tree with the property (22).
`pw − tw` grows with `n` but slowly: 1 at 7, 2 at 10, 3 not below 50 in
anything on record. §6's floor becomes an interval: `pw > tw` on 164 of the
338 gap instances (48.5%), `pw = tw` on 80 (23.7%), open on 94 (82 above 64
customers). The soundness objective `disagree` was flat at zero. §27 made
the 10-vertex record a theorem by enumeration (3.3).
*Size range:* search 7–20; exact treewidth on every corpus instance at 9–20
and every gap instance at 20–50 (22 by interval). *Regenerate:*
`python -m learning.extremal --stage corpus --workers 8; --stage search …; --stage tables`.
*Status:* finding; kill met for `disagree` only.

**3.3 No graph on ≤ 9 vertices has `pw − tw ≥ 2`; exactly four on 10 do;
none on ≤ 11 has a gap of 3 (§27).** A 300-line C program over nauty's
`geng` computed exact pathwidth (the vertex-separation subset DP) and exact
treewidth for every graph on 1–11 vertices up to isomorphism, every count
matching OEIS A000088 and the `tw ≤ 1` column matching the number of forests
(A005195) at every `n`. Over all 287,884 graphs on ≤ 9 vertices
`pw − tw ∈ {0, 1}`, so §21's graph is a smallest with `pw − tw = 2` by
exhaustion; on 10 vertices exactly four graphs have it, one family — §21's
graph with the tenth vertex additionally joined to any set of the three hubs,
a chain of 21 ⊂ 22 ⊂ 23 ⊂ 24 edges — and on 11 there are 1,034, none with
`pw − tw = 3`, so a gap of 3 needs at least 12 vertices (the smallest on
record is §21's 50-vertex corpus instance). 516 of the 1,034 are
vertex-minimal, and twelve have treewidth 2 and pathwidth 4 with no K₄ at
all: the sparsest, 15 edges and maximum degree 3, is three triangles strung
between two poles, biconnected — not a tree of cliques, a second shape the
pathwidth bounds must see. Every one of the 1,038 graphs found was
re-established by routes sharing no code with the C, including the exact MOSP
solver with a persisted witness. The share of graphs with `pw > tw` rises
0.6% → 9.9% from 6 to 11 vertices. The census to 10 took 20 s of wall clock
where §21 had priced the 9-vertex question at an hour; n = 11 took 13.2
core-hours (49 minutes on 16 workers); n = 12 is priced at 4,300–4,700
core-hours for the joint census and about 240 at level 0 for the `pw − tw ≥ 2`
question alone.
*Size range:* every graph on 1–11 vertices, exactly; nothing about 12 or more
except the price. *Regenerate:*
`python -m learning.pwtw_exhaust --stage {check,run,verify,tables}`.
*Status:* theorem by enumeration (the ≤ 9 and ≤ 11 statements); finding
(the families).

**3.4 Exact treewidth is the theorem the solver does not compute; the
mined-formula family is closed (§24).** Over 30 branching-aware invariants on
50,949 certified instances, 11,589 two-invariant candidates, 47 survivors
exceeding `lb_best` on more than 5% of the gap instances: 36 are `tw + 1`
restated, two are fitted lower envelopes of `tw + 1` and `lb_best` that never
beat their pair, and nine are "novel" only on 60–125-customer graphs where
treewidth is an unresolved interval. 77% of fitted candidates leak on grouped
hold-out (a constant fitted on 51,000 instances is the maximum of a sample);
no candidate beats `max(lb_best, tw + 1)` on more than 0.1% of the 44,578
instances with exact treewidth. The adversary (288,000 exact-solver
evaluations at 8–15, 9,000 at 20–30) broke nothing, and that record is
vacuous, not clean: the novel candidates are slack by construction below 30.
What the mining put on the table is `optimum ≥ tw + 1`: it beats the solver's
certified lower bound on 199 of the 338 gap instances (58.9%) and on 933 of
6,376 corpus instances (14.6%), and is tight on 67 gap instances. The
"trees of cliques with branching" of §6 branch at *separators*, not cut
vertices: only 10 of the 338 gap instances have a cut vertex with three
branches, so the branch lemma is a statement, not a bound. A bug the "must be
0" column caught: the first branch-lemma implementation stood above the
optimum on 347 rows; fixed and recomputed.
*Size range:* 9–134 for validity; exact treewidth to 26 by DP and to 64 under
a one-second search; the adversary 8–30. *Regenerate:*
`python -m learning.conjecture --stage {invariants,repair,mine,attack,attack-large,tables}`.
*Status:* closed question (the two-invariant family over these invariants);
one conjecture stated and labelled worthless — `optimum ≥ ⌊0.9428 · √(tw · f(6))⌋`,
valid on 50,948, undefeated at 8–30, pointwise ≤ the proved pair everywhere;
one proposed solver change (§8 below).

**3.5 The branching family is closed by the harness (§38).** Three
branching-aware candidates, all resting on Lemma A — three components of
`H − S` of pathwidth `≥ k`, pairwise linked through components of `H[S]`,
force `pw(H) ≥ k + 1`, stated and proved on paper in §38 and in Lean in §40 —
went through the harness of 1.5: `cut-branch` (the plan's: the branch rule
recursively over cut vertices, clique-seeded), `sep-branch` (the same with
`S` ranging over cut vertices, clique glue sets, clique-tree adhesions and,
on small subgraphs, every edge; seeded by `max(ω − 1, tw)`), and
`contract-branch` (`sep-branch` on every minor of the contraction-degeneracy
sequence). All three are valid on all 49,862 rows and the adversary reached
their tightness frontier in every one of 60 jobs without crossing it — a
clean record, not a vacuous one. On the 338 gap instances `cut-branch` beats
`lb_best` on none; `sep-branch` on 15 (4.4%), all its exact-treewidth seed
restated, and the reference on none; `contract-branch` beats `lb_best` on 84
(24.9%) and the reference on 8 (2.4%), every one of the 8 a 50–125-customer
instance whose treewidth is a 1-second interval and where a minor's *seed* is
`lb_best + 1` with `value == seed` — §24(c)'s finding again, and retired by
exact treewidth if it were computed. What the branch rule itself adds is
exactly one, on 68 / 158 / 64 of 49,862 rows, never on a gap instance, and
tight when it fires (43 of 43, 62 of 63, 62 of 62); among the 5,003 rows
with exact treewidth and `pw > tw` the candidates are tight on 1.2%. A
tempting strengthening — `pw ≥ k + |S|` when `S` has a matching into each
branch — is false (two adjacent hubs with three spider branches: optimum 4,
not 5). The kill (none beats the reference on more than 5% of the gap
instances while surviving) is met: 0.0 / 0.0 / 2.4%.
*Size range:* validity 9–134 on 49,862 instances (upward complete at 60, 75
and 100, 52% at 50); the adversary 8–15 and 18–25; 665 and 1,501 rows
censored at 31–75 carry their seed. *Regenerate:*
`python -m learning.bound_harness --stage {validity,attack,tables}`.
*Status:* closed question (branching at any separator the clique structure
exposes); the next bound idea has to be a different pathwidth argument.

---

## 4. Hardness

**4.1 There is a phase transition, and Chu & Stuckey's density 2 sits on it
(§11).** At every `n` from 15 to 40, in both generators and at both `m / n`,
the median nodes to refute `optimum − 1` rise and fall with density by two
orders of magnitude each side at n = 40, the peak above at least one
neighbour by bootstrap in 26 of 28 series-size rows; the peak sharpens
(half-height width 0.30 → 0.14–0.19 in `log10 col_mean` from 20 to 40). On the
ridge the median grows exponentially at 0.086–0.105 log10 per customer —
doubling every 2.9–3.5 customers — with a power law ruled out at 5–10× the
residual; off the ridge at fixed density it grows exponentially too but
slower (doubling every 4.5–4.9). The ridge sits at about three customers per
product when `m = n` and two when `m = 2n` (§25 gives the general
coordinate); mean degree predicts the *height* of the surface best (r² 0.93 of
0.95 attainable) but its peak location drifts. Chu & Stuckey's "density 2"
(realised 2.7–2.8) is the peak cell at both 30 and 40; their density 4 is its
dense shoulder. Pre-registered here: the ridge law says 5 × 10¹¹ nodes at 125;
§35's like-for-like refit says 2.7 × 10¹¹.
*Size range:* 10–40; peaks on n ≥ 15, order parameters on n ≥ 20; Chu &
Stuckey placement at 30 and 40. *Regenerate:* `python -m learning.hardness_map`.
*Status:* finding; kill (monotone, no peak) not met.

**4.2 Hardness is a property of the labelled graph and of nothing else in the
matrix — for the search (§13; §30 for SAT).** Re-covering the same edge set
with different cliques — 15,900 re-coverings of 1,400 instances, products
removed or added by up to 30 — leaves the default node count *exactly*
unchanged in every pair (the search reads neighbour masks and nothing else,
and the C and Python agree on all 15,900), and graph-only features predict
nodes as well as graph plus matrix (MAE 0.0948 vs 0.0968), matrix-only 25–30%
worse. Two things move the count and neither is the cover: **relabelling**
the customers (2–6% at the median, up to 2.26× default and 8.1× `csearch`;
the search's tie-breaks, the floor for any label-free predictor) and the
`csearch` rule that switches Theorem 2 on by a matrix statistic (10–13% at the
median, up to 25%, pre-fix, always in its favour; a design choice of
`sparse_enough_for_better_move`). The matrix does carry the number of optimal
closing orders under the construction value — by up to three orders of
magnitude at n = 15 — while the count under the search measure is identical
in all 4,516 pairs. 15,900 free audits of Yanasse's equality passed.
*Size range:* 10–40. *Regenerate:* `python -m learning.graph_story --workers 16 --per-n 200 --per-method 4 --relabellings 20`.
*Status:* finding; kill met (the matrix adds nothing to hardness prediction
for the search).

**4.3 The graph story does not hold for the SAT path, and the way it fails
is the reduced formula (§30).** §13's pairs regenerated — 205 bases, 40 per
size at 10–30 and 10 at 35 when the wall cutoff fell, about 600 re-coverings and 830 relabellings, 3,258 SAT calls in
65 minutes on 16 workers, conflicts counted on CaDiCaL 1.9.5 and seconds on
the default `kissat404` in a forked child, since pysat's Kissat exposes no
statistics, ignores `interrupt()` and aborts on `conf_budget`. Every one of
5,657 settled decisions on either backend agrees with the certified value.
With labels fixed, re-covering the same edge set moves the refutation's
conflicts by 0.26–1.67× between p10 and p90 (MAD 0.132 log10, a typical pair
off by a third), in the direction of the formula: the greedy cover and a
merge cut conflicts to 0.771 and 0.869 of the base's at the median, a split
raises them to 1.15, each with Wilcoxon `p < 10⁻⁸`, the same on the witness
(0.602 / 1.00 / 1.03) and in Kissat's seconds (0.65 / 0.86 / 1.21). The
channel is visible pair by pair: rank correlation 0.6–0.7 between the change
in conflicts and the change in clauses; where a split's product is dominated
away the formula is identical and the conflicts equal on all 29 such pairs;
across bases at fixed `n` Spearman between log clauses and log conflicts is
0.93–0.98. Two proportions. SAT has a label floor the search barely has —
renaming the customers moves the refutation 1.6–1.9× at the median (search
1.00–1.05×) and the witness 7–13× — so the cover's 1.36× median effect is of
the order of relabelling noise (1.26×), twice it at p90 (4.26 vs 2.00), and
below it on the witness. And the cover is not why the two procedures rank
instances differently (Spearman −0.04 to −0.34 between nodes and conflicts
at fixed `n`): the within-graph share of SAT's variance is 4–21%, the rest
is between graphs, set by the product count after dominance and `k`. The kill
test inverts §13's: graph-only features predict SAT refutation conflicts at
MAE 0.533 log10 against 0.245 for the full set, 0.286 matrix-only and 0.264
for six formula quantities. The plan's kill (paired median within ±5%) is met
on its letter — the pooled median is 1.00 — and fails in its spirit, because
17% of pairs are exactly equal and the methods pull opposite ways.
*Size range:* 10–30 at 40 bases per size, 4–61 products; 35 is a 10-base
sample with 71% censored and carries no conclusion; refutation censoring at
120 s is 22% at 25 and 62% at 30. *Regenerate:*
`python -m learning.sat_story --stage run --workers 16 --per-n 40 --per-method 1 --relabellings 4 --deadline 120 --wall 3900`; `--stage tables`.
*Status:* finding; proposed solver change (a pre-encoding re-cover for the
SAT path, to be raced, not switched on); the SAT-cost predictor needs formula
features and a label-noise term (±0.07 log10 on refutations, ±0.25 on
witnesses).

**4.4 The refutation grows exponentially to 125, at a rate the n ≤ 40 cells
overstate (§14).** On the Chu & Stuckey corpus at 30–125 the exponential beats
the power law in every density class by 3–5× in RMS residual on five or six
points spanning a factor of 2.5–4 in `n`. Every campaign rate is above the
corpus's by 0.005–0.018 log10 per customer, a factor of 6–34 at 125 for
densities 6–10; the two exceptions are the two day-long classes: the `d = 4`
law holds to 125 (11.5 predicted against 10.7–11.4), and §11's pre-registered
ridge law lands within a factor of 3 of the two density-2 counts on record
(5 × 10¹¹ against 1.6–1.7 × 10¹¹) after eight decades of extrapolation. The
`d = 2` class stays 2–6× harder than `d = 4` at every size to 125 while its
`optimum / n` falls from 0.29 to 0.18, so the ridge's size-stable coordinate
is customers per product, not `optimum / n`. Theorem 2 (pre-fix) saved more
at scale: `csearch / default` 0.80 at 50, 0.83 at 75, 0.63 at 100, 0.17 on
`Random-100-50-4`.
*Size range:* 30–125, five instances per class, the 125 rows on two and three
counts. *Regenerate:* `python -m learning.scale_test`. *Status:* finding.

**4.5 The rate drifts down with `n` to 75 — and §35 shows the drift does
not survive to 100 on the ridge (§16).** The campaign extended to
`n ∈ {50, 60, 75}` at `m ∈ {n/2, n, 2n}` (6,750 instances, 6,747 certified,
11.1 core-hours) and a priced sample at n = 100. The exponential form holds
to 75 in every series (4–11× better than a power law) and to 100 where there
is data. The local rate falls with `n` in 18 of 18 fixed-`d` series, pooled
at **−0.000217 ± 0.000045 log10 per customer per customer** (t = −4.8): about
0.002 per ten customers, or 0.011 between the midpoints of §11's and §14's
windows, which is the 0.005–0.018 §14 measured; fitted at 50–100 the campaign
reproduces the corpus's rates to 0.005. Drift-corrected from the 75-customer
cells, §16 predicted the two `Random-125-125-2` counts on record to 0.04
decades (11.18 against 11.21, 11.22) with a band of ±0.8 decades — **1.5 ×
10¹¹ nodes for density 2 and 4 × 10¹⁰ for density 4**, 30 and 8 hours per
refutation on one core. **§35 supersedes that headline**: the 0.04-decade
match compared a `default` law with pre-fix `csearch` counts; on the
`csearch` row of §16's own table the drifting law sat 0.22 below the record,
and read like with like the figure is 2.7 × 10¹¹ nodes and 55 h.
The ridge stays at `d = 3` (`m = n`) and `d = 2` (`m = 2n`) through 75 and
sits at 5–6 for `m = n/2`. The n = 100 ridge cells were priced at 40
core-hours against the plan's cap of 8, so the grid stopped at 75; the
5-per-cell sample confirmed the price (nine of ten descents ran out at 900 s,
two of the values reached were not optimal); §34 later spent 26.4 of 28
core-hours on the whole cell and certified one instance of 25.
*Size range:* 10–75 fully certified; 100 for `d = 2` (25 certified) and a
sample at `d = 3, 4`; every 125 figure is a 50-customer extrapolation from 75.
*Regenerate:* `python -m learning.ensemble --upward …; python -m learning.upward`.
*Status:* finding; kill (100-customer ridge cells over 8 core-hours) met;
the 125 prediction is superseded by 4.7.

**4.6 The `m = n` ridge at 100 does not certify in 28 core-hours (§34).**
The cell §16 stopped at, `f_n100_m100_d3` (100 customers, 100 products,
three per product), all 25 instances descended with the complete customer
search under `csearch` from the best of four heuristic upper bounds, 2,400 s
per call, 6,300 s of wall on 16 workers: 129 decision calls, 26.4
core-hours, 17.1 in the descents and 9.3 in `default` refutations queued
behind them. The satisfiable side is cheap — the upper bounds stood 1–6
stacks high (median 3), and the 80 `sat` calls that closed the gap cost
0.78 core-hours, a median of 2 s per instance — and the last step is not:
**24 of 25 descents censored at 2,400 s on the step below their value**,
having visited 3.4–4.8 × 10⁹ nodes (log10 9.54–9.68) under `csearch`, and
the `default` refutations ≥ 9.50 at the censored median. One instance
certified, `i012` at optimum 21, the lowest in the cell (the others stand at
22–26, mean 23.6): refuted at k = 20 under `csearch` in 2.13 × 10⁹ nodes
(1,233 s) and under `default` in 2.94 × 10⁹ (1,424 s), the two agreeing. §19's
cost model priced the cell at 45.3 core-hours under `default` and 21.3 under
`csearch` from the heuristic upper bounds, said correctly that it would not
fit, and is consistent with every count; fed `i012`'s certified 21 instead of
its UB of 26 it gives 8.36 against 9.47 observed, 1.1 decades under, because
`opt_frac` is its strongest term. §16(e)'s drift-corrected law is the one
contradicted: its median at 100 (8.92 `csearch`, 9.09 `default`) sits 0.5–0.7
decades below lower bounds that hold on every instance, so the ridge's rate
over 75 → 100 is at least 0.115 per customer. Chu & Stuckey's
`Random-100-100-2` reproduce the picture instance for instance (four of five
`default` refutations censored at 1,500 s with 3.2–5.4 × 10⁹ nodes). The fix
cost on the satisfiable side, on the two instances §16(d) had pre-fix: 2.5×
and 3.3×. `default` is faster per node than `csearch` here (2.07 against
1.82 × 10⁶ /s), so Theorem 2's per-node price at 100 on the ridge is 1.1–1.5×,
above §22's 1.17×.
*Size range:* one generated cell at 100; comparisons to §16's 75 cell and
the corpus's five `Random-100-100-2`. *Regenerate:*
`python -m learning.ridge100 --stage {price,run,tables}`.
*Status:* finding; the plan's budget (40 core-hours) was itself below the
price, so the kill (certify the cell) was not met.

**4.7 The rate did not keep falling; read like with like, the 125 × 125
ridge refutation is 2.7 × 10¹¹ nodes and 55 hours pre-fix (§35).** The six
125 × 125 recertify counts on record were made by workers forked from a
library built before the `better_move` fix, so they are **pre-fix `csearch`**,
as is every `csearch` count of the 10–75 campaign (§31 reproduces them to the
node with the `prefix` variant); `default` is untouched by the fix; §34's
`csearch` counts are post-fix. A pre-fix `csearch` run on §34's cell (25
calls, 15.2 core-hours) settled five refutations (log10 9.00–9.29), found one
value not optimal (`i005`, 26 → 25, so its censored counts bounded a witness
search and it leaves the series) and censored 19 at ≥ 9.25–9.35. Fitted as a
censored cell — a Tobit, since a median of lower bounds has no likelihood —
its location implies a rate of **0.116 [0.110, 0.121]** log10 per customer
over 75 → 100 under pre-fix `csearch` and 0.140 [0.128, 0.156] under
`default`, against 0.092–0.095 over 60 → 75 and 0.085–0.089 had §16's drift
continued; the quadratic's curvature on 10–100 is +1.8 to +3.0 × 10⁻⁵ and on
40–100 +2.9 to +4.7 × 10⁻⁴, so the drift §16 pooled from 18 series **reverses
on the ridge** while on the `d = 4` neighbour the negative curvature survives
on 10–100; the power law loses to the exponential by 1,000–1,200 AIC in every
series. Compared like with like — pre-fix `csearch` law against pre-fix
`csearch` record, which §16(e)'s headline did not do (its 11.18 was a
`default` figure) — the constant-rate exponential refitted on 10–100 puts the
median `Random-125-125-2` refutation at **11.43 log10 nodes [11.36, 11.51]**,
and the record's three counts (11.21, 11.22, 11.66) fall 0.2 below and 0.2
above it, inside one instance's spread; the readings that carry the 75 → 100
rise to 125 give 12.4–12.6, which the record contradicts by 0.8–1.4 decades,
so the rise is confined to 75–100 as far as the corpus class can tell (its
own 100 → 125 rate is 0.07–0.09). On `d = 4` the record's median (10.78) sits
on §16(e)'s drifting 10.61 and 0.65 below the exponential refit. **The
revised law, stated once:** on the ridge, pre-fix `csearch`,
`log10 nodes = −0.24 + 0.0934 n` from 10 to 100 with no resolvable drift and
σ growing to 0.5 at 100; at 125 a median of **2.7 × 10¹¹ nodes (2.3 to 3.2 ×
10¹¹ on the median; ×/÷ 10 for one instance)**, **55 hours** per refutation
on one core at 1.4 × 10⁶ nodes/s, against 25–72 hours spent on the record.
**Post-fix** the same refutations cost the fix ratio more: **≥ 2.34× on the
100 cell** (one exact pair at 2.15, four lower bounds to 3.15), ≥ 19.6× on
`Random-100-100-2-4_0` (§31); there is no post-fix series to fit. `default`
at 125 is 11.7–11.8 by the same refit and has no count on record.
*Size range:* generated `m = n` fixed-d at 10–100 (d = 3 fully certified to
75; at 100 the 24 instances that survive the pre-fix check, 1 certified);
`d = 4` at 100 on five instances; Chu & Stuckey's classes enter only as the
record. **Every 125 figure is an extrapolation of 25 customers** from a cell
that is mostly lower bounds, resting on the reading that a value reached in
2,400 s is optimal — one of 25 was not. *Regenerate:*
`python -m learning.rate_drift --stage {prefix-run,tables}`.
*Status:* finding; closed question for "is the curve sub-exponential" (no)
and "does the drift saturate" (on the ridge it reverses).

**4.8 The ridge is a condition on the excess of the product cover (§25).**
The plan's hypothesis — the ridge is one MOSP-graph mean degree, 8–9 — fails:
the mean degree at the peak runs 3.9 / 7.4–8.4 / 10.5–12.0 / 15.8–21.4 / 37.6
for `m = 2n / n / n/2 / n/4 / n/8` (×9.5), and calibrated at `m = n` it
predicts the `m = n/2` ridge at 4.7 customers per product against a measured
5.2–5.6 with every fixed-generator interval excluding it, 6.4 against 9.2–10.6
at `n/4`, 8.9 against 20.7 at `n/8`. The parameter that is the same across
`m / n` is the **excess** `(n_ones − m) / n = Σ_j (|C_j| − 1) / n`: 2.0–2.5 at
every fixed-generator peak and 1.8–3.0 at every Bernoulli peak (CV 0.13, the
only candidate within a factor of 1.65 across ratios); calibrated at `m = n` it
predicts the other ridges to 0.055 decades on average and the `n/8` ridge to
0.012. In `col_mean` coordinates the ridge is at about `1 + 2.4 n / m`:
2 / 3 / 5–6 / 9–11 / 21 customers per product. At excess 1 the
customer–product incidence graph has as many edges as vertices; the ridge is
one independent cycle per customer. It is an incidence-graph parameter, not a
MOSP-graph invariant (the maximal-clique version runs 1.8–11.8; no graph
invariant tested is constant within a factor of 1.9). The literature's
transition (branching factor 1: giant component, linear width) lies 1.5–6×
below the ridge and is where the optimum becomes linear, not where the search
is hardest. The ridge's height scales as `m^2.9` (n = 50) to `m^4.9` (n = 75),
so nothing collapses the surface: the excess locates the ridge, `m` sets its
height (§37 gives the law, 4.10). Placed by the excess, the 125 × 125 ridge
is at `col_mean ≈ 3`, between Chu & Stuckey's densities 2 (excess 1.76) and 4
(3.2), nearer 2 — a prediction, not a measurement. The deciding cells
(`m = n/4` at 50–75, `m = n/8` at 75; 2,750 instances) were generated for
this item. §37's finer `m = 2n` Bernoulli grid later raised that series'
peaks by up to half a decade (the 75 peak from 7.00 at the grid edge to 7.15
interior).
*Size range:* 50–75, `m / n ∈ {⅛ (75 only), ¼, ½, 1, 2}`, 9,497 instances in 190
cells; 30–40 confirms excess 2.0–2.6. *Regenerate:*
`python -m learning.ridge_theory --stage {run,cliques,tables}`.
*Status:* finding (no kill stated).

**4.9 Excess two is a density condition, not a percolation threshold; the
transition is in the reachable region of the closed-set lattice (§36).**
Excess 2 in incidence-graph terms is `β ≈ n`, one independent Berge cycle per
customer, or products per customer `2 + m / n`, or `n_ones = 2n + m` — each a
statement about a mean, none about a structure appearing. The incidence
graph of both generators is a random bipartite configuration model whose
cores come from a two-type peeling recursion (checked against the peeled
cores of the 9,497 instances at 50–75: 2-core share within 0.002 at
`m ≥ n`), and no known threshold sits where the ridge sits for every
`m / n`: the giant component (also where the 2-core appears) is 0.34–0.78
decades below it and further below the fewer the products, the `(3,2)`- and
`(2,3)`-cores 0.11–0.45 below with the same drift, the `(3,3)`-core *crosses*
it (+0.08 at `m = 2n`, −0.25 at `n / 8`), the XORSAT-style "core cyclomatic
number = core customers" 0.06–0.37 below, and connectivity moves with `n`
where the ridge does not. Excess 2 is the only line within 0.09 decades of
every one of the 25 measured peaks with a flat residual across ratios (mean
|log10 error| 0.039, −0.07 to +0.01 by ratio); its tree-free form "2-core
cyclomatic number = `n`" scores 0.047, and calibrated at `m = n` the excess,
the 2-core excess and the dominance-reduced excess all land at 0.035–0.052 —
one condition on the cycle mass of the cover read on three subsets, not
separable at the grid's 0.05-decade resolution. At the ridge the 2-core holds
64–92% of the customers and 96–100% of the products, so no core is emerging
there. What the ridge is a transition *of*: at `n = 20` and `25` on 6,840
certified instances, the count of closed sets whose boundary fits
`optimum − 1` is monotone in density, saturates at `2^n`, is reproduced by
the random model to 0.0002 decades and is *anticorrelated* with the node
count (Spearman −0.87), while the count of sets *reachable* from the empty
set through fitting steps equals the node count to 0.03–0.06 decades at the
median on connected instances (Spearman 0.88; 0.99 / 0.97 on connected
instances with ≥ 10 reachable sets) and peaks where the nodes peak in all
eight series. Sparse instances have many feasible sets and few chains; dense
ones have every set feasible and a first step that already costs more than
`k`. Deriving the reachable count in the random model is a first-passage
problem over `2^n` states, not attempted.
*Size range:* thresholds scored on 25 peaks at 50–75, `m / n ∈ {2, 1, ½, ¼,
⅛}`; the mechanism test at 20–25, `m ∈ {n, 2n}`. Nothing here is evidence
about 125 × 125 except through §25's extrapolation, left as it was.
*Regenerate:* `python -m learning.cover_excess --stage {measure,tables}`;
`measure_states(workers=12)`. *Status:* closed question (the incidence-graph
thresholds); finding (the reachability mechanism).

**4.10 The ridge's height needs `m` separately, as `n · log(m_eff / n)`
(§37).** With 3,380 new instances (1.4) filling the ratios the surface
lacked — Bernoulli `m = 4n` and `8n`, a finer `2n` grid, and the cheap
`n / 4` and `n / 2` ridges at 100 — there are 57 series peaks under each
configuration. At fixed `n` the Bernoulli climb per doubling of `m` falls
from 1.0–1.6 decades (`n / 4 → n / 2`) to 0.1–0.25 (`4n → 8n`): it
saturates because at the excess-2.4 ridge the products that carry an edge
saturate near `2n` (a product with one customer or none adds nothing and is
dominated away; `m_eff / n` at the Bernoulli peaks is 0.24 / 0.48 / 0.74–0.89
/ 1.32–1.34 / 1.4–1.9 / 2.1 for `m / n = ¼ … 8`). Per doubling of the
*effective* products the increments are flat at about `0.017 n` decades,
which the fixed generator (`m_eff = m`) shows directly at 1.02–1.66 per
doubling. Of thirteen candidate laws the three-parameter one that survives is
`log10 nodes at the ridge ≈ −0.10 + n · (0.089 + 0.058 · log10(m_eff / n))`
— 0.0175 decades per customer per doubling of the effective products, and
at `m_eff = n` 0.089 per customer (§35's `0.0934 n − 0.24` refitted with
every ratio): in-sample RMSE 0.18, leave-series-out 0.21, leave-`n`-out 0.22,
75 from ≤ 60 at 0.33, and the two certified `n / 4` ridges at 100 (heights
5.13 fixed, 5.07 Bernoulli) predicted from `n ≤ 75` to +0.16 and +0.21. The
`n`-only law is wrong by a decade and more in every test and a law linear in
`m` by as much. The excess at the peak carries nothing about the height
(slope +0.15 in one generator and −0.18 in the other against the residual;
held-out change −0.03 to +0.07 decades). Once each series' height is taken
out, the whole surface at 50–75 is one shape in the excess (r² 0.86–0.94,
0.8-decade residual from widths that differ) and no shape in `col_mean`
(r² ≤ 0.2); the ridge is about a factor 2.2 wide in excess at half a decade
below its peak and a factor 3 at one, the sparse side the short one for
`m ≥ n`. At 100 the law holds where the ridge is cheap and not where it is
not: the `n / 2` ridges (8.10 fixed, 7.80 Bernoulli) sit 0.6–1.1 decades
above it and §35's `m = n` location (10.27 [9.97, 10.68]) 1.3–1.9 above, with
the 75 → 100 rate rising with the ratio — 0.054–0.056 at `n / 4`, 0.098–0.106
at `n / 2`, 0.140 at `m = n` — so the rise §35 found is real, not an artifact
of the form, and grows with `m / n`. The law's value at `n = 125`,
`m_eff = n` is 11.0, to be read against §35 and not asserted.
*Size range:* peaks at 15–40 (`m ∈ {n, 2n}`), 50–75 (`m / n` from ⅛ to 8)
and 100 (`n / 4`, `n / 2` certified; `m = n` as a location only); fits on
15–75, 54 exact peaks pooled; 3,378 of the 3,380 new instances certified.
*Regenerate:* `python -m learning.ridge_height --stage {run,tables}`.
*Status:* finding; closed question (the height as a function of the ridge
coordinate: it is not).

**4.11 A cost model predicts a refutation to within a decade at 100–125
(§19).** A hand-written Tobit (censored Gaussian regression in log space) on a
linear, extrapolable design in `n × {density, m/n, opt/n, degree, dispersion,
treewidth, degeneracy, components, clustering}` plus §16's drift, with a
LightGBM residual correction on scale-free features, trained at 10–75 and
selected at ≤ 60 → 75, puts **87.8% of the 98 `default` counts and 89.3% of
the 103 pre-fix `csearch` counts at 100–125 within one decade**, against
57.5–65.4% for §11's cell law and 59.2–61.2% for §14's surface; in-range MAE
0.09 / 0.09 / 0.14 / 0.20 decades at 10–20 / 21–40 / 50–60 / 75; bias +0.4
decades (it over-predicts); the relabelling noise floor (sd 0.003–0.017) is
10–100× below any error. The one class missed is the generated 100-customer
`d = 2` cell, 96% decomposable (14 of 25 within a decade); without it the
100-band is 57 of 58. On the five finished recertify entries it has MAE 0.38,
bias +0.38, Spearman 0.4 on the order (the `default` linear variant 0.8; the
§11 law −0.3). Cheapest-first for the three then withdrawn:
`Random-125-125-2-5_0`, `2-3_0`, `2-2_0` (11.15 / 11.34 / 11.85 log10 nodes;
22 / 33 / 107 h at 0.55 µs per node). Every prediction is for the pre-fix
`csearch`; post-fix ridge counts at 100 are ≥ 2.34× larger on the 100 cell
and ≥ 19.6× on `Random-100-100-2-4_0` (§31, §35) and the model has never seen
one at 125. §34 tested it on the 100 ridge cell: it sized the budget
correctly from the heuristic upper bound (which overstates the optimum by
1–6 there) and under-predicts by 1.1 decades from the certified optimum;
§35's like-for-like law now prices the queue at 55 h median, ×/÷ 10.
*Size range:* trained 10–75; tested on 98 + 103 counts at 100–125, 15–20 at
125 and 5 on the ridge. *Regenerate:* `python -m learning.cost_model` (11 s).
*Status:* finding; kill (under 80% within a decade) not met for the chosen
model, met for the linear Tobit alone and both baselines. A prediction for
ordering a queue, never a bound.

---

## 5. Soundness and certificates

**5.1 Every refutation at n ≤ 40 is sound on twenty searches; the satisfiable
side found a false `unsat` (§15).** For 43,935 certified instances (campaign
37,800, corpus 6,135 at n ≤ 40), ten labellings each (identity, eight
relabellings, one re-covering), `decide(optimum − 1)` and `decide(optimum)`
under both configurations: 1,757,280 decision calls in 199 s on 16 workers.
Every call at `optimum − 1` returned `unsat` (878,580 of 878,580); the lattice
oracle agreed on all 13,612 instances it reaches; zero contradictions. At
`k = optimum` **88 runs on 56 instances said `unsat`**, all under the `csearch`
configuration with Theorem 2 on, all sparse (1–2 products per customer), 8 on
the identity labelling. The 56 stored optima are right (56 of 56 re-certified
by routes sharing nothing with the C `better_move`); the rule was wrong. The
resolution (`reports/better_move_bug.md` §7): three bugs — a wrong close count
inside the rule, the cross-rule cycle §15 diagnosed (`subset_rule` measured
survivors against candidates `better_move` had discarded), and an early exit
that hid both. Fixed by the owner in commit `0eb33915`; the harness now
reports 0 disagreements on the same 43,935 instances, and the fix costs
`csearch` refutations +7.3% nodes in total at n ≤ 40 (median 1.00, p90 1.18),
no `default` count changed. §13's two symmetries hold on all 43,935: the
re-covering's default count equals the identity's on every pair. Method
lesson: a refutation record should carry its `sat` side under the same
configuration — an unsound pruning rule cannot be caught at `k = optimum − 1`
when the stored value is right. §31 later corrected one attribution in the
bug report: the 10 × 13 minimal instance needs *both* bugs (the campaign
instance it was cut from falls to the reordering alone).
*Size range:* 9–40; every statement about 125 × 125 is about which code runs
there. *Regenerate:* `python -m learning.differential --workers 16` (`--stage drawn`, `--stage shrink`).
*Status:* finding; the proposed fix was **applied by the owner**;
`tests/test_differential.py` pins the two minimal counterexamples (10 × 13,
17 × 9).

**5.2 Both halves of the fix are necessary, the reordering carries its cost,
and no cheaper sound composition exists (§31).** Each change of `0eb33915`
sits behind its own bit of a new C argument (`cs_decide_variant`, default 0):
`old-close` (the over-counting close count alone), `old-order` (better move
before the subset rule, citing every remaining customer), `prefix` (both, the
rule as it stood) and `bm-first`, a candidate sound composition added after
the reverts were measured — better move over every candidate first, then the
subset rule over its survivors forbidden to cite anything better move
discarded. `prefix` reproduces the pre-fix search exactly: §15's 56 instances
and 88 false answers to the call, the pre-fix total of 6,101,183 nodes, and
`results_upward.csv`'s `csearch` counts on 3,334 of 3,348. Soundness at
n ≤ 40 on §15's ten labellings and both calls (350,540 calls per variant):
`fixed` 0 instances with a false answer, `old-close` **1** (3 calls),
`old-order` **36** (61), `prefix` **56** (88), `bm-first` 0; every false
answer an `unsat` at the optimum, and 1 + 36 < 56 because the two bugs
interact. So no variant that undoes either change is a candidate. Cost at
n ≤ 40 over 17,521 identity refutations: the whole fix 1.073×; in summed
log-ratios the close count is 23% of the extra search and the reordering
81% (interaction −4%); the close count changes 13.4% of counts and costs
1.1%, the reordering 35.8% and 6.4%. At 41–100 (3,566 instances with Theorem 2
on, 3,452 settled by every variant) the fix costs **1.54× the nodes** (median
1.08, p90 1.59) and 1.30× the seconds, the fixed order being faster per node
(1.73 against 1.45 M nodes/s); the reordering still carries the total (1.48
against 1.06), growing with size (1.06 / 1.07 / 1.43 at 50 / 60 / 75) and
sparsity (1.51 at d = 2), but per instance the two are now comparable (54% /
59% of the log-cost), because at 75–100 the over-count was doing real
unsound pruning. §18's ×2–3.5 on `Random-100-50` is reproduced (3.46, split
1.67 close / 2.73 order), and on `Random-100-100-2-4_0` at 600 s the close
count alone costs 2.26× and the reordering ≥ 8.7× on top, **≥ 19.6× in all**
(`prefix` 93.1 M nodes in 38.8 s; `fixed` censored at ≥ 1.82 G). `bm-first`
is sound everywhere measured, 2.0% dearer at n ≤ 40, **0.854× today's nodes
at 41–100** (1.32× pre-fix) and a wash in seconds (0.98) because it is slower
per node (1.50 against 1.73 M nodes/s: the untuned citation check); it costs
1.16 on the 100 ridge cell. The pre-fix rule's cheapness was the cycle
itself, not the order of the rules.
*Size range:* soundness and cost at 9–40 on 17,527 instances × 10
labellings; refutation cost only, identity only, at 41–100; nothing about
125 × 125 except through §16's rate law. *Regenerate:*
`python -m learning.fix_cost --stage {harness,scale,tables}`; `--variants bm-first`.
*Status:* closed question (a cheaper sound fix among the reverts: none);
proposed solver change (`bm-first`, to tune and re-measure in seconds on the
two day-long 125 × 125 classes, not to adopt); recommendation: keep today's
rule.

**5.3 92.0% of the corpus at n ≤ 40 carries a DRAT proof a third party has
checked (§17).** drat-trim (Heule, vendored at `tools/drat-trim/`, built with
`-std=gnu99`) verifies CaDiCaL 1.9.5's binary DRAT trace of
`encode_mosp_decision` at `optimum − 1`, after the same decomposition and
pattern dominance `decide_mosp` applies, recorded as index lists in a
certificate from which the CNF rebuilds without `mosp.preprocess`. **5,646 of
6,135 (92.0%)**: 99.4% / 97.1% / 80.0% / 77.7% by band ≤ 10 / 11–20 / 21–30 /
31–40, for 11.2 core-hours and 11.7 GB of compressed proofs (31.8 GB raw),
zero checker rejections, zero `sat`, zero wall-deadline kills. Affordability
is decided by the formula, `m² · k`, not by `n`: censoring 0 of 4,062 below
5,000, then 4% / 25% / 69% in the next three decades; every instance with
m ≤ 20 certified at any `k`; the boundary `m² · k ≈ 10⁴` is crossed by an
m = 125 instance at k = 1, so the direct encoding has no proof to offer at
125 × 125. The SAT proof costs 6,000–70,000× the customer search's seconds on
the same questions: an archive object, not a decision procedure. Two pysat
facts: `Solver.interrupt()` raises `NotImplementedError` for CaDiCaL, and
`get_proof()` returns a truncated proof until every C stream is flushed. The
proof replaces trust in CaDiCaL and in the search's dominance rules; it does
not replace trust in the encoding or the two reductions.
*Size range:* 9–40 (6,135 instances; the 241 above 40 not attempted).
*Regenerate:* `python -m learning.proofs run --max-customers 40 --workers 16 --conflicts 200000`, then `--conflicts 1000000 --retry-timeouts`; `tables`; `check <stem>`.
*Status:* finding; kill (checker cannot be built or proofs not checkable) not met.

**5.4 The customer search has a proof object: every refutation at n ≤ 40
carries a certificate a third party checks in milliseconds (§32).** A
refutation is a tree of search nodes; the certificate is that tree with every
pruning decision named — per node the closing customer, its free moves, its
kind (`refuted`, or `memo` citing an earlier node), its steps `["definite",
q]`, `["subset", r, d]`, `["better", r, q]`, and its children; the cost cut,
Theorem 3 and the state record nothing. The checker shares no code with the
search: it derives the state from the path, recomputes every premise from the
instance, checks that the free moves are exactly the computable set, that a
memo cites a completed refutation of the same closed set, and —
**exhaustiveness** — that every candidate with cost ≤ k is a child or is
covered by a chain ending at a child or in `Q(S)`, with no cycle. It trusts
the three theorems in the free-move cost model and the cost cut, not the
search, the emitter or the C. About 60 bytes per branch uncompressed; 325–750
bytes gzipped at the median in every band to 40, 388 KB at the largest
(38,777 nodes). On the corpus at 9–40, all 6,135 instances emitted at
`optimum − 1` under three configurations (`default`, `csearch`, `memo`):
**6,135 verified, 0 rejected, in every configuration**, agreeing with all
5,646 DRAT verdicts and the lattice oracle's 2,812, and covering the 489
instances the DRAT budget censored; under `csearch` 305,316 nodes and 159,616
steps, 25,567 of them Theorem 2. Checking is 14.8 µs per node in pure Python:
the whole corpus at n ≤ 40 is **5.0 MB gzipped and checks in 4.5 s**, against
11.7 GB and 5,190 s for the DRAT proofs on the 5,646 instances that have both
— 12.7× to 13,700× smaller and 791× to 10,200× faster to check, on a
different trust base. The emitter is the Python reference with a port of the
C's `better_move`; its tree is the C's *without the memo*, node for node (914
and 930 count differences all equal the C with `memo=False`), and the memo,
which saves the C 40% of its nodes at n ≤ 40, is exactly what the certificate
cannot carry. **Both bugs that shipped are rejected** by the checker: the
17 × 9 instance under the old close count at the root (its premise recomputed
is false), and a campaign instance under the old rule order as *covering
cycle through [6, 9]* with every premise true. The kill (a Theorem 2 step
checkable from the instance and the state alone) is not met at the step, and
the precise form is the finding: a Theorem 2 *premise* is local, but whether
it prunes soundly is a property of the node's whole step set — the very
property the cycle violated — so the checkable unit is the node; Theorem 3's
premise lives on the path; and the memo is local only without Theorem 3,
since with both on a refutation belongs to the path that found it. Above 40
the Python emitter is about 120× slower than the C: at 60 s per call, **141
of 151 corpus instances at 41–75 are refuted and verified under both
configurations** (the 10 censored all at 75, at 1.2–1.9 M branches), gzipped
median 13.5 KB and max 10.1 MB, check time median 31 ms, p90 1.3 s, max 24.4 s,
211,737 Theorem 2 steps certified. At 125 × 125 the tree is 10¹¹ nodes (§14),
some 10 TB uncompressed, and is not a shippable artifact.
*Size range:* corpus 9–40 (6,135, every certificate verified, three
configurations); 41–75 (151 instances, 141 verified); nothing at or above
100 emitted. *Regenerate:*
`python -m learning.search_certificate --stage run --max-customers 20 --workers 16`; `--min-customers 21 --max-customers 40 --deadline 60`; `--min-customers 41 --max-customers 75 --deadline 60 --configs default,csearch`; `--stage tables`.
*Status:* finding; kill not met at the step (the node is the unit); proposed
solver changes (a C emitter behind a flag; `recertify` emitting and checking
a certificate; a Lean statement of the three theorems in the free-move cost
model).

**5.5 Zero disagreements above 40, and the harness is affordable to 100 on
every class but the ridge (§33).** 1,294 certified instances at 50–100 —
eight from each of the 135 campaign cells at 50–75 and every corpus instance
at 50–100 (214) — on the identity and four relabellings, decided at
`optimum − 1` and `optimum` under both configurations at 300 s per call,
every call **priced from a recorded identity run** before scheduling
(inflated 1.3× for the spread; a censored record priced at the full 300 s)
inside an eight-core-hour budget: 25,800 calls, **12,860 of 12,860
refutations `unsat`**, 12,938 of 12,940 witnesses simulating to the optimum,
zero disagreements, zero contradictions, zero witness failures; the two
censored calls are witness searches on one relabelling of
`Random-100-100-2-5_0`. 5.96 + 0.45 core-hours against a price of 8.23
(price / actual 1.38, both conservatisms). The slowest refutation took 193 s
(`Random-100-100-4-2_0`, `relabel3`, 1.85 × 10⁸ nodes). Refutations were
priced out for **eight instances**, all five `Random-100-100-2` and three of
five `Random-100-100-4` (80 calls at 6.67 core-hours, every one expected to
censor since 300 s buys 1.5–3 × 10⁸ nodes and §14's counts for them are 1.6 ×
10⁸ to ≥ 1.8 × 10⁹): the first size at which the harness stops being
affordable is **100 customers, `m = n`, two to four customers per product** —
the eight §18 excluded by hand, and the classes that take a day at 125 × 125.
Everywhere at ≤ 75 it is affordable, including the ridge cell
`f_n75_m150_d2` (1.5 × 10⁸ nodes median, 193 s at worst). The relabelling
spread of a refutation is 1.00–1.02× at the median at every size, 1.1–1.3×
on the ridge and its sparse side at 75–100 (`Random-100-50-4` 1.27–1.31, max
1.54), MAD 0.002–0.006 log10, so no labelling of a censored instance would
have settled; the witness spread is 1.3–2.0× at the median and up to 10⁴×,
where §18's portfolio pays, confirmed at 100 under both configurations
(witnesses are cheaper than refutations on 12,395 of 12,840 pairs, median
ratio 0.059). `csearch / default` has median 1.000 at every size but 50
(0.968) and never exceeds 1 at p90: Theorem 2 saves and never costs in nodes
at 50–100, as §22 found below. §18's own 21,828 rows were re-verdicted: 0
disagreements, a check §18 did not report. §31's variants on 611 cheap
sparse instances (12,220 calls): no false answer from the unsound reverts —
not evidence of soundness, about two were expected on a sample this size —
and the pre-fix rule is 2.5–3× more label-sensitive than today's (MAD
0.019–0.024 against 0.007–0.008; max/min up to 7.1× against 1.4×).
*Size range:* campaign 50–75 (1,080 of 6,747, a sample and not the cells),
corpus 50–100 (all 214; 52 of 60 at 100 refuted, 8 witness-only); nothing at
125. *Regenerate:*
`python -m learning.differential_scale --stage {price,run,variants,tables}`.
*Status:* finding (zero stated as zero over 25,800 calls); proposed solver
changes (the price stage's admission rule for any future harness run;
`recertify` running its satisfiable calls as a labelling portfolio; §32's
certificate for the eight priced-out instances if a C emitter is built).

**5.6 Independent audits that came free.** The lattice oracle
(`learning.degeneracy`, sharing no code with the search) equals the certified
optimum on all 2,812 corpus instances at n ≤ 15 and on 256 generated ones
(§8), on 4,916 re-covered instances (§13), on 13,612 in the differential run
(§15) and on 4,122 at n ≤ 20 through the vectorised lattice (§23);
`optimum − 1` re-refutes on all 6,135 at n ≤ 40 under two configurations
(§3); isomorphic instances carry equal optima in every class (§1); the
sandwich holds on all 6,376 + 37,800 (§5, §12); 15,900 re-coverings solve to
their base's optimum (§13); 27,000 relabelled refutations at 40–100 contradict
nothing (§18); 50,861 paired refutations and 50,909 witness searches agree
across Theorem 2 arms (§22); 407,168 calls agree across fan orders (§20);
5,657 settled SAT decisions on two backends agree with the certified value
(§30); every settled call of every `better_move` variant at 41–100 answered
`unsat` (§31); 25,800 calls at 50–100 on five labellings agree (§33); the
1,038 census graphs re-certify as MOSP instances by every route (§27); and
the three bound candidates of §38 never stand above an optimum on 49,862
rows. Nothing was re-certified because nothing disagreed, except the 56
instances of 5.1, whose values were right. **Above 100 customers nothing is
checked by anything outside the search** except the two-arm agreement of §22
and the relabelling agreement of §18 and §33 at 101–125; at 50–100 the
five-labelling, two-configuration harness of §33 covers every corpus
instance but the eight it priced out.
*Status:* finding.

---

## 6. Search rules and portfolios (proposed, measured, not applied)

**6.1 A relabelling portfolio wins nothing on refutations (§18).** Sixteen
seeded relabellings per instance on 1,572 instances at 40–100 (53,448 decision
calls, 5.95 core-hours): the max/min refutation spread over labellings is
1.00–1.05 at the median and 1.11–1.26 at p90 in every band; min-of-16 against
the identity is 1.00–1.02 at the median, 1.01–1.05 on the 389 instances at
n ≥ 60 whose identity refutation costs ≥ 10⁴ nodes; the widest spread in the
study is 2.14×; **the spread shrinks with `n`** (1.12, 1.02, 1.02, 1.01 at 40,
50, 60, 75) and a 16-way portfolio's core efficiency is 0.063. Seconds on the
loaded machine spread 1.49× against 1.05× in nodes — the clock alone would
have passed the kill. No cheap statistic of a labelling predicts its cost
(|ρ| < 0.35). The **witness search** is the other story: its spread grows
with `n` (p90 max/min 7 → 542 from 40 to 75), and where it is hard (≥ 10⁴
nodes, 67 of 360 at 75) min-of-16 saves 8–13× at core efficiency 0.5–0.8 — but
it is 183 nodes against 27,900 for the refutation, so a portfolio on it removes
2–5% of a descent pair's cost. The race on `Random-100-100-2-4_0` found the
unplanned result: §14's pre-fix identity took 93.1 M nodes in 37 s; the
post-fix identity had visited 1.39 G nodes at 600 s unfinished, 3 of 16
labellings finished (630 M–1.25 G). **The fix costs more the larger the
instance**: post/pre 1.00 at n = 40, 1.06–1.27 at 50–75 on sparse cells, 2.3×
and 3.5× on `Random-100-50-2/4`, ≥ 15× on `Random-100-100-2-4` — refined by
§31 to 1.54× over 41–100 in total and ≥ 19.6× on that instance, and by §35
to ≥ 2.34× on the 100 ridge cell; every `csearch` count in `results.csv`,
`scale_nodes.csv` and the recertify record is pre-fix, and the post-fix cost
at 125 is not known. §33 reproduced the refutation spread with four
labellings under both configurations (1.00–1.02 at the median) and confirmed
the witness-side case at 100.
*Size range:* campaign 40–75, corpus 50–100; the race at 100 on four
instances; the 125 projection is an extrapolation of a flat curve.
*Regenerate:* `python -m learning.relabel_portfolio --workers 16 --deadline 120`; `--stage race …`.
*Status:* closed question for refutations (kill met: median min-of-8 at
n ≥ 60 is 1.003); proposed solver change for satisfiable-side drivers only
(`ratchet`, `restricted_dfs` seeds, the `k ≥ optimum` calls of a descent).
Recommendation for `recertify`: do not add a portfolio on refutations.

**6.2 Fan order does not matter for refutations (§20).** Behind
`fan_order="index" | "degree"` on `decide` (Python and C) and `restricted_dfs`
(registered as `cs-dfs+degree`), with defaults unchanged and the default path
byte-for-byte equal to every recorded count (50,756 of 50,756 campaign,
43,935 §15 identities, 1,572 §18 identities, 44,547 `ub_cs_dfs`): 407,168
decision calls on 50,896 instances at 9–100, zero status changes. The paired
refutation ratio has median 1.000 in every band under both configurations,
geometric mean 1.000, p10–p90 within [0.992, 1.008]; the fraction of
refutations whose count changes at all rises from 0.1% at n = 10 to 74.4% at
75 and cancels, because the cost cut, the memo and the dominance rules are
properties of the state, not of the order the fan is read in. The witness
search is two-sided: median 1.000 but geometric mean 0.81 at 75, total nodes
0.65 at 75 and 0.87 at 99–100, gain on the ridge cells (0.43–0.62), p90 above
1 everywhere; worth 1.7% of a descent's nodes at 75. `cs-dfs+degree`: exact
70.0% → 70.1%, total overshoot −1.3%, corpus 99–100 MAE 3.21 → 2.95, 50%
slower in the Python (the sort-key lambda). §7's `cs-dfs+rule` gain came from
the *seed*, not the fan order — confirmed over the whole corpus by §28
(`cs-dfs+degree` 128 better / 113 worse than `cs-dfs` at 1.5× the time;
`rule+cs-dfs` 780 / 12).
*Size range:* 10–75 campaign, 9–100 corpus. *Regenerate:* `python -m learning.fan_order --workers 16`.
*Status:* closed question for `decide` (kill met at every size); proposed
solver change for satisfiable-side drivers (`fan_order="degree"`: 35% of
witness nodes at 75, 13% at 100, p90 cost 1.1–1.3×). Keep `index` for
`decide`; `cs-dfs+degree` registered, not default.

**6.3 Theorem 2 should always be on in nodes and stay at 5 in seconds (§22).**
Theorem 2 on against off on every instance, paired, under the fixed C: 50,911
instances at 9–125 (the fifteen dense 125 × 125 included), 203,632 calls, 5.3
core-hours, 0 status disagreements. Where the hand rule
(`sparse_enough_for_better_move`, ≤ 5 products per customer) turns it *off*,
forced on saves on 8,810 instances, ties on 21,109 and costs on **one**
(405 → 410 nodes), 6.6% of the nodes in total, 3–7% by size from 50 up; all
fifteen 125 × 125 instances save (median 0.933 on `-6`). Where it is *on*,
post-fix, it saves 27% in total and 8% at the median, and costs on 174
instances (0.8%), never heavily (worst 1.27×). Always on is the node oracle
to four decimals; the hand threshold leaves 4%. The depth-3 tree fitted to the
sign of the difference predicts on for every instance, so it agrees with the
hand rule on 41.2% — kill (agreement above 95%) not met. **On the clock the
hand threshold is right**: Theorem 2 costs 1.167× per node (p10 1.10, p90
1.23, flat in `n`), break-even node ratio 0.857; where the hand rule is off,
on is slower on 347 of 350 heavy refutations (1.13× median); the seconds sweep
is flat at regret 1.025–1.029 for thresholds 4.5–6 and always on is *slower
than always off* in seconds (1.061 vs 1.066). The threshold should rise only
if the C's per-node overhead falls below about 1.03. The witness side: total
0.826 but 1,253 costs, max 184×. §33 adds that at 50–100 `csearch / default`
never exceeds 1 at p90 in nodes, and §34 that on the 100 ridge cell the
per-node price is 1.1–1.5× (`default` 2.07 against `csearch` 1.82 × 10⁶
nodes/s), above the 1.167× measured here.
*Size range:* 10–75 campaign, 9–100 corpus, 125 × 125 `-6/-8/-10`; the `-2`
and `-4` classes not covered. *Regenerate:* `python -m learning.theorem2 --workers 16`.
*Status:* proposed solver change, measured both ways; **recommendation: no
change to `sparse_enough_for_better_move`**; closed question for the learned
boundary.

---

## 7. Optimal orderings and imitation

**7.1 A one-sentence rule beats the imitation ranker (§7).** Distilling the
LightGBM closing-order ranker of `learning/policy.py`: the logistic scorer is
MCN's criterion with "already open" in front (82% of the ranker's gain), the
depth-3 tree ties constantly (57% with MCN's tie-break). Of 570 lexicographic
rules over five per-candidate features, 64 beat the ranker, all 57 whose first
key is *fewest new stacks* among them. The rule — **close the customer that
opens the fewest new stacks; on ties, the one with the most unclosed
neighbours** — scores held out MAE 0.348, exact 80.7%, worst +9 against the
ranker's 0.519 / 75.0% / +34 and MCN's 1.616 / 50.2% / +26; better than the
ranker on 253 instances and worse on 109, in every size band and every
collection but Shaw; on the 91 Chu & Stuckey held out, 2.42 vs 3.35 vs 9.44.
The first key is `restricted_dfs`'s own cheapest-first fan order, so the
greedy is that search's first leaf; the tie-break is the *reverse* of MCN's.
As the DFS's incumbent it beats the learned seed: `cs-dfs+rule` 0.127 / 92.7%
against `cs-dfs+lgbm` 0.157 / 91.0% on the 1,920 held out — settled over the
whole corpus by §28 (7.2). Fiedler order keeps 66% of the gain with no state
at all; BFS from a min-degree root does not. The ranker imitates the witness
at 45.3% of steps, below MCN's 52.5% and the rule's 62.3%: imitation rate
ranks constructions almost inversely to their value.
*Size range:* 9–134 on 1,920 held-out instances, 1,768 at ≤ 30; above 60
customers it rests on 56 instances with the rule 3.7 stacks off.
*Regenerate:* `python -m learning.distil --workers 16`. *Status:* finding;
kill (no readable rule keeps half the gain) exceeded at 115%; proposed solver
change (register the rule as a heuristic and as the `cs-dfs` seed) —
registered by §28 as `rule` and `rule+cs-dfs`, the default of nothing.
*(Superseded 2026-09-30: `rule+cs-dfs` is the default since 2026-09-28.)*

**7.2 The rule seeds the DFS better than the learned policy over the whole
corpus; the LightGBM question is closed (§28).** `two_key_closing_order`
(§7's rule with popcounts, then MCN's own tie-break) is registered in
`satisfiability/heuristics.py` as `rule` and, as the incumbent of
`restricted_dfs` at its default 200,000 nodes, as `rule+cs-dfs`. Swept over
all 6,376 certified instances with `learning.corpus_sweep`, the learned
strategy scored fold by fold with models blind to their fold and the folds
grouped by file ∪ MOSP-graph class (§1's honest split): `rule+cs-dfs` **exact
94.2%, mean overshoot 0.092, worst +8, total overshoot 586 stacks, 370
misses, 16.7 ms per instance (0.29 at the median)** against `learned+cs-dfs`
92.1% / 0.128 / +8 / 819 / 506 / 20.6 ms (1.68 at the median, the ranker's
per-step predict) and `cs-dfs` 84.5% / 0.241 / +10 / 1,539 / 988 / 29.5 ms.
Head to head the rule seed is better than the learned seed on 263 instances
and worse on 80 (never by more than three; 71 of the 80 by one), and over
`cs-dfs` it is **780 better / 12 worse** where the learned seed was 709 / 13
on the leaky file split and is 602 / 19 on the honest one — about a seventh
of the 2026-09-22 gain was the split. It recovers 627 of the 988 optima
`cs-dfs` misses (the learned seed 497), leads in every size band (0.037 vs
0.056 at 9–30, 0.355 vs 0.516 at 31–60, 2.108 vs 2.667 at 61–134) and every
collection (Chu & Stuckey 1.275 at 50.5% exact against 1.670 at 38.0%; Shaw
a tie at zero). The 12 regressions are off by one on 11 and by two on one,
the `_cs_cost` proxy mismatch `reports/learning.md` diagnosed for the learned
seed's 13. The value is in the incumbent: `rule` alone (0.26 ms) is worse
than `cs-dfs` on 485 instances, and sorting the fan by the same keys without
the seed (`cs-dfs+degree`) changes almost nothing (128 / 113) at 1.5× the
time. So nothing is left for LightGBM to decide on the solver's critical
path: `learned+cs-dfs` is dominated by a strategy of the same cost class with
no model, no training, no fold protocol and no dependency.
*Size range:* 6,376 at 9–134, 5,938 of them at ≤ 30; above 60 the lead rests
on 120 instances where the rule seed is still 2.1 stacks over on average; at
125 × 125 it is exact on 2 of 25 (learned 1, `cs-dfs` 1) at mean overshoots
2.88 / 3.40 / 3.68. Milliseconds are from a loaded machine and comparable
only with each other. *Regenerate:* `python -m learning.rule_seed --workers 16`.
*Status:* closed question (the LightGBM dependency); proposed solver change
(`rule+cs-dfs` as the upper-bound strategy wherever `cs-dfs` is used today:
`customer_search.solve`'s `upper_strategy`, `csearch`, the descent drivers),
not applied. *(Superseded 2026-09-30: applied by the owner on 2026-09-28,
commit `d0b5c5ecd`; measured 2026-09-29 on four instances at 100–125, the
seed changes the starting bound and not the certification cost, nodes within
0.2%, because the refutation at `optimum − 1` is the same search under
either seed (§28 addendum). Its value at scale is a better answer when a run
is stopped early, not a faster proof.)*

**7.3 The rule is not the literature's MCNh, which is now reproduced (§29).**
Becceneri, Yanasse & Soma (2004), obtained from the author on 2026-09-27,
state the Minimal Cost Node heuristic in full: an *arc traversal* of the MOSP
graph — the arc at a minimum-degree node with the pair-wise smallest degree,
then every untraversed arc between open nodes — not the node-closing
procedure `mcn` implements from Yanasse & Senne (2010)'s one sentence. `mcnh`
(strategies `mcnh` and `mcnh-arcs`, registered, the default of nothing)
reproduces the paper's worked example to the arc — seven loops, the three
printed states, the sixteen arcs of `ARC` in order, ξ = 4, the printed pattern
sequence and Fig. 2's profile row by row — with only two tie-breaks not in
the pseudocode, both pinned by the example, so the kill (the pseudocode must
be guessed) is not met. It reproduces Frinhani et al. (2018)'s MCNh column on
**21 of 21 named rows** (sums 671 = 671 against OPT 659; SP2–SP4 at 23 / 37 /
57 where `mcn` gives 26 / 49 / 74), Shaw to one stack in total over 25 files
and SCOOP's aggregates (gap 25.27% in both). Over the corpus `mcnh` is MAE
0.361, exact 79.6%, worst +13 against `mcn`'s 1.343 / 54.9% / +32 (2,528
better, 61 worse): `mcn` never was MCNh, and the heuristics docstring's
statement to that effect is confirmed and closed. **The two-key rule is not
MCNh under another name**: the two produce the same closing order on 37
instances (0.6%) and the same pattern sequence on 51 (0.8%), agree on the
value on 86.9%, and where they differ the rule wins 592 to 242, leading in
MAE overall (0.279 against 0.361) and in every band, the gap widening with
size (3.61 against 4.44 at 61–134). What they share is the first key — on
98.8% of MCNh's closing decisions the customer it closes opens the fewest
new stacks, which the arc traversal enforces structurally — and the whole
difference is the tie-break: MCNh's minimum-`Ω` choice is a minimum-degree
rule (attains MCN's key on 73.4% of steps, the rule's second key on 79.2%,
falling to 39.8% and 49.0% at 61–134), the reverse of the rule's. `mcnh`
costs 0.94 ms per instance against 0.27 for the rule and 0.38 for `mcn`; the
two readings of the arcs-to-patterns sentence give different sequences on
5,748 instances and the same value on all 6,376.
*Size range:* 9–134, the whole certified corpus; nothing about the generated
ensembles or 125 × 125 beyond the eight Chu & Stuckey files of that size.
*Regenerate:* `python -m learning.mcnh --workers 16`; `--stage paper`.
*Status:* closed question (the rule vs MCNh; `mcn` vs MCNh); `mcnh` stays
registered as the literature's reference point, nothing proposed.

**7.4 The optimum is never unique (§8).** Exact path counting over the subset
lattice on every corpus instance at n ≤ 15: 0 of 2,812 have a unique optimal
closing order even up to twins, 0 of 2,138 a unique product order up to
reversal; the least degenerate corpus instance has 156 optimal closing orders,
the median 4 × 10⁵ at n = 10 and 2.5 × 10¹⁰ at n = 15. The share tracks
`optimum / n` (ρ +0.70) and not the bound gap (+0.02); Chu & Stuckey's search
measure over-charges up to 95% of optimal orders and still finds the minimum
every time. A policy optimal at every step but indifferent among optimal
moves agrees with the stored witness on 30–38% of steps at n = 15, and every
policy measured sits far above that, so step agreement above about 0.3
measures reproduction of the solver's tie-breaks. About 90% of the 2.27 M
decisions `learning/policy.py` trains on are arbitrary choices among optimal
ones.
*Size range:* 9–15 corpus, 8–15 generated. *Regenerate:* `python -m learning.degeneracy --workers 16`.
*Status:* finding.

**7.5 Imitation is closed for good (§23).** With the construction-measure
lattice vectorised to n = 20 (4,122 instances; 175,687 states, 1,501,721
candidate rows, 84.5% good), the exact set of optimal moves as label, and the
rule's own keys as features so that the model can only add to the rule, the
best learned policy beats the rule by **0.008 MAE grouped at n ≤ 20**
(0.0805 → 0.0725; bootstrap over union groups −0.025 to −0.004), by
0.006–0.008 over the whole corpus with intervals including zero, against the
plan's kill of 0.02. The rule's pick is already in the optimal set at 99.71%
of labelled states — 97.6% even on the 291 instances it misses, a single bad
step per instance; the old ranker is wrong under the correct objective twice
as often as the rule (1.25% vs 0.56%). **The imitation ceiling falls with
size**: exact 0.330 median at 9–15 and 0.233 at 16–20 (complete graphs
excluded); bounded above by 0.142 / 0.109 / 0.100 at 50–75 / 76–100 / 101–134
along 238 witnesses, with 14.5 / 24.2 / 35.1 optimal alternatives per step at
the median and fewer than 4% of steps forced; the bounded procedure recovers
99.92% of exact choices at 16–20.
*Size range:* labels 9–20; construction values 9–134 (above 75, 87 instances,
undetermined); ceiling 50–134 on 238 witnesses. *Regenerate:*
`python -m learning.set_imitation --stage {lattice,train,ceiling,calibration,tables}`.
*Status:* closed question (kill met).

---

## 8. Solver changes proposed and never enabled

*(2026-09-30: two of the entries below have since been enabled by the owner,
#1 and #14; the heading is kept as written.)*

Every entry is behind a flag that defaults to today's behaviour or lives in a
report; enabling any of them is the owner's change. "Decides" names the
measurement that would settle whether to enable it, or that already has.

| # | change | proposed in | measured effect | what decides it | state |
|---|---|---|---|---|---|
| 1 | Fix the C `better_move` (cross-rule composition; wrong close count; early exit) | §15 | false `unsat` at the optimum on 0.32% of sparse instances at 10–40; fix costs `csearch` refutations +7.3% nodes at n ≤ 40, 1.54× at 41–100, ≥ 19.6× on `Random-100-100-2-4_0` (§31), ≥ 2.34× on the 100 ridge cell (§35) | the differential harness at 0 disagreements — done; §31: both halves necessary (1 and 36 of the 56 false answers return if either is reverted) | **applied by the owner** (`0eb33915`; `better_move_bug.md` §7) |
| 2 | Exact / interval treewidth as a `_lower_bound` component | §24 | floor rises on 933 corpus instances, 67 gap instances become bound-certified; 0.2–1 s per instance (39 s worst); valid on all 50,949 ("above optimum" = 0); would also retire the eight seed-on-an-interval "beats" of `contract-branch` (§38) | a descent timing over the 25 hardest instances, as `reports/expansion_bound.md` §6 did — a floor shortens a descent only where it equals the optimum, and it never does where `pw > tw` (68% of exact gap instances). Since §39 it rests on the proved `treewidth_add_one_le_mospValue`, not on a cited equality | proposed |
| 3 | Register the two-key rule as a heuristic and as the `restricted_dfs` seed | §7 | `cs-dfs+rule` 0.127 / 92.7% vs `cs-dfs+lgbm` 0.157 / 91.0% held out (1,920); over all 6,376 (§28): `rule+cs-dfs` 94.2% / 0.092 / 586 stacks, 780 / 12 over `cs-dfs`, 263 / 80 over `learned+cs-dfs`, at 57% of `cs-dfs`'s time | decided by §28's corpus sweep: the rule seeds better with no model | **registered** (`rule`, `rule+cs-dfs`); `rule+cs-dfs` default since 2026-09-28, see #14 |
| 4 | `fan_order="degree"` on `decide` | §20 | refutation 0.0% at every size (kill met) | decided: keep `index` | closed |
| 5 | `fan_order="degree"` for satisfiable-side drivers (`ratchet`, the `k ≥ optimum` calls of a descent) | §20 | −35% witness nodes at 75, −13% at 100 in total; p90 cost 1.1–1.3× | a paired run of `benchmarks.ratchet` under both orders in nodes | proposed |
| 6 | `cs-dfs+degree` as the `cs-dfs` default | §20 | +0.1 pt exact, −1.3% total overshoot, corpus 99–100 MAE 3.21 → 2.95; 50% slower in Python; over the corpus 128 / 113 against `cs-dfs` at 1.5× the time (§28) | replace the sort-key lambda by a tuple, then re-time; dominated by #14 | registered, not default |
| 7 | Theorem 2 always on (`sparse_enough_for_better_move` → true) | §22 | nodes −6.6% where the hand rule is off (one cost of 1.2%); seconds +5% on heavy hand-off refutations at 1.167× per node; at 50–100 `csearch / default` never above 1 at p90 in nodes (§33); per-node price 1.1–1.5× on the 100 ridge cell (§34) | the C `better_move`'s per-node overhead: below 1.03 always-on wins the clock from 50 up | proposed and **recommended against** (keep 5) |
| 8 | A relabelling portfolio in `benchmarks.recertify` on refutations | §18 | min-of-16 refutation speed-up 1.00–1.01, core efficiency 0.063; spread 1.00–1.02 with four labellings under both configurations at 50–100 (§33) | decided at 40–100 | recommended against |
| 9 | A relabelling portfolio on satisfiable calls (`recertify`, `ratchet`) | §18 | 8–13× where the witness search is hard, core efficiency 0.5–0.8; 2–5% of a descent pair; confirmed at 100 under both configurations: witness spread up to 10⁴×, the witness 6% of a refutation's cost (§33) | same as #5 | proposed |
| 10 | The cost model to order and size the recertify queue | §19 | 88–89% of 100–125 counts within a decade; sized the 100 ridge cell correctly from the heuristic UB (45.3 / 21.3 core-hours; 28 available) and under-predicts by 1.1 decades from the certified optimum (§34) | the two entries still open (`Random-125-125-2-2_0`, `-2-3_0`, open as of 2026-09-30) finishing; §35's like-for-like law (55 h median pre-fix, ×/÷ 10) is the simpler price | proposed, for ordering only, never for `k` |
| 11 | `learned+cs-dfs` as the default upper bound | `reports/learning.md` | 709 / 13 over `cs-dfs` on the file split; 602 / 19 on the honest split; dominated by `rule+cs-dfs` 263 / 80 head to head (§28) | decided by §28 | registered, not default; nothing to be built on it |
| 12 | Group `learning/study_optimum.py`'s split by `graph_cert` | §1 | file grouping leaks 157 classes across files; worth a seventh of the learned seed's gain (§28) | a study change, not a solver change | proposed |
| 13 | Draw `test_better_move_never_changes_a_decision`'s instances at 1–3 products per customer and add the two minimal counterexamples | §15 | the dense family it drew never ties enough candidates to expose the cycle | done if the strict `xfail` in `tests/test_differential.py` has been promoted (§28's test run still reports 1 xfailed) | proposed |
| 14 | `rule+cs-dfs` as the upper-bound strategy wherever `cs-dfs` is used today (`customer_search.solve`'s `upper_strategy`, `csearch`, the descent drivers) | §28 | 780 better / 12 worse over `cs-dfs` on 6,376, 627 of its 988 misses recovered, 16.7 ms against 29.5 per instance; the 12 regressions off by one (one by two); 2026-09-29: certification cost unchanged at 100–125 (nodes within 0.2% on four instances, §28 addendum) | decided by §28; before 2026-09-28 `DEFAULT_STRATEGY` was `mcn+tabu` and `upper_strategy` `cs-dfs` | **applied by the owner 2026-09-28** (`DEFAULT_STRATEGY`, `customer_search.solve`, `solve_mosp_exact`, `race`; `d0b5c5ecd`) |
| 15 | `mcnh` / `mcnh-arcs` as strategies | §29 | the published MCNh to within tie-breaks (21 of 21 named Frinhani rows); MAE 0.361 against `rule`'s 0.279; 0.94 ms | nothing: `rule` dominates it as a construction and `rule+cs-dfs` dominates both | registered as the literature's reference point |
| 16 | `bm-first`: better move first, the subset rule over its survivors citing nothing better move discarded | §31 | sound on 350,540 calls at n ≤ 40 and every settled call at 41–100; +2.0% nodes at n ≤ 40, **0.854×** at 41–100, 1.16 on the 100 ridge cell; seconds a wash (0.98) at 1.50 against 1.73 M nodes/s | move the citation check out of the subset loop, then seconds on the two day-long 125 × 125 classes | proposed to tune and re-measure, not to adopt; the four revert flags stay measured, default off, unsound where labelled so |
| 17 | A pre-encoding re-cover for the SAT path (merge products whose union is a clique, optimum-preserving by §13's construction) | §30 | greedy re-cover 0.77× conflicts and 0.71× seconds at the median on refutations, p90 1.39× | a race, not a switch | proposed |
| 18 | A C emitter for the search certificate (a trace of `(move, free, steps)` per node) | §32 | the Python emitter verifies 141 of 151 at 41–75 at 25–30 k branches/s, about 120× slower than the C; the certificate is the C's tree *without the memo* under old move | behind a flag, never the default; the memo becomes an uncertified speed-up whose omission the checker flags | proposed |
| 19 | `benchmarks.recertify` emits and checks a certificate for every refutation it records | §32 | turns "two configurations agree" into "a third party can check"; 5.0 MB and 4.5 s for the whole corpus at n ≤ 40 | #18 for the sizes `recertify` runs at | proposed |
| 20 | A Lean statement of the three dominance theorems in the free-move cost model | §32 | the one trusted step the checker leaves; Theorem 2's hypotheses have a brute-force pedigree (124 M applications) and no proof | a Lean session | proposed |
| 21 | The price stage's admission rule for any harness run — schedule a refutation only if a recorded identity run of the same instance and configuration settled within the deadline over the inflation | §33 | price / actual 1.38 over 25,800 calls; 8.23 priced against 5.96 + 0.45 spent | already usable as written in `learning/differential_scale.py` | proposed |
| 22 | A certificate for the eight priced-out instances (`Random-100-100-2-*`, three of `-4-*`) | §33 | above the harness's boundary the soundness check is the certificate or nothing | #18 | proposed |

---

## 9. Closed questions

Measured, answered, and not to be rebuilt without a new idea. Each has a
section explaining the mechanism, not only the outcome.

- **Fan order for refutations** (§20): 0.0% at every size; the visited state
  set is order-independent.
- **A learned boundary for Theorem 2** (§22): "always on" in nodes, the hand
  threshold in seconds; no learned rule beats 5 on the clock.
- **A relabelling portfolio for refutations** (§18, §33): the spread shrinks
  with `n` and is 1.00–1.02 at the median under both configurations at 50–100.
- **Imitation, single-witness and set-valued** (§7, §8, §23): the target is
  90% arbitrary; the rule is already optimal at 99.7% of states; the ceiling
  is 0.10 at 125.
- **The LightGBM dependency** (§28): over all 6,376 the two-key rule seeds
  the DFS better than the learned policy on every statistic (94.2% vs 92.1%,
  263 / 80, faster); a seventh of the learned seed's recorded gain was the
  file split leaking isomorphic copies. Nothing is to be built on `learned`.
- **The two-key rule as MCNh under another name** (§29): no — same closing
  order on 0.6% of instances, the same first key on 98.8% of steps, opposite
  tie-breaks (most unclosed neighbours against minimum degree), the rule
  wins 592 / 242. And **`mcn` as MCNh** (§29): never was; `mcnh` is, to
  within tie-breaks, on 21 of 21 named published values.
- **A cheaper sound fix for `better_move`** (§31): none among the reverts —
  each half alone brings false refutations back (1 and 36 of the 56) — and
  the one sound alternative composition, `bm-first`, is 15% cheaper in nodes
  at 41–100 and even in seconds, so it is a tuning question, not a cheaper
  fix. Which half carries the cost: the reordering (81% of the log-cost at
  n ≤ 40, the larger share of total nodes at 41–100).
- **A branching-aware lower bound as a two-invariant formula over the thirty
  invariants of §24**: theorems in disguise or sample maxima.
- **A branching-aware lower bound at any separator the clique structure
  exposes** (§38): three candidates, valid on 49,862 instances and under
  11,880 adversarial evaluations each, beat `max(lb_best, tw + 1)` on no gap
  instance by branching; the rule is worth exactly one stack where
  `pw = tw + 1` and nothing on the gap instances. The next bound idea has to
  be a different pathwidth argument.
- **Degree statistics as the residual's formula** (§4, §5): they saturate at
  the average degree and know what the bound knows.
- **Mean degree as the ridge's coordinate** (§25) and **`optimum / n` as its
  size-stable coordinate** (§14): the excess is; `col_mean` at fixed `m / n` is.
- **The ridge as a threshold of the incidence graph** (§36): no core, giant
  component or connectivity threshold coincides with it at every `m / n`;
  excess 2 is a density condition, and the transition it marks is in the
  reachable region of the closed-set lattice.
- **The ridge's height as a function of its coordinate** (§37): it is not;
  the height is `n · log(m_eff / n)` and the excess at the peak adds nothing.
- **Is the ridge law sub-exponential, and does §16's drift saturate** (§35):
  no (the power law loses by 1,000–1,200 AIC), and on the ridge the drift
  reverses over 75 → 100 rather than saturating, while the rise is not
  sustained to 125 in the corpus class.
- **Intervals calibrated at n ≤ 40 quoted at n ≥ 50** (§14): every one fails
  at the first band beyond calibration.
- **The clique cover as a hardness factor for the search** (§13): exactly
  nothing, with labels fixed. **For SAT** (§30): what closed is the claim
  that the cover is why the two procedures fail on different instances —
  the within-graph share of SAT's variance is 4–21% and the rest is formula
  size, set by the product count after dominance and `k` — and the plan's
  kill on its letter (pooled median 1.00). What did *not* close: the cover
  does move SAT's conflicts (0.77 / 0.87 / 1.15 by method, `p < 10⁻⁸`, a
  typical pair off by a third), so SAT is not cover-independent in §13's
  sense; and nothing above 30 customers was measured.
- **DRAT proofs for 125 × 125 through the direct encoding** (§17): the
  boundary `m² · k ≈ 10⁴` is crossed at k = 1.
- **`disagree` as an extremal objective on the fixed C** (§21): flat at zero.
- **`pw − tw ≥ 2` on nine vertices** (§27): impossible, by exhaustion of all
  287,884 graphs; and `pw − tw = 3` on ≤ 11 vertices likewise.
- **Yanasse's equality as a hypothesis** (§26, resolution note): it is a
  `sorry`-free Lean theorem over the MOSP graph in both directions; the
  `Reduction.lean` statement over the pattern graph was false.
- **`treewidth ≤ pathwidth` in Lean** (§39): proved, via `pathGraph_isTree`,
  which Mathlib lacked.
- **The branch lemma in Lean** (§39, §40): the stated version was false
  (no connectivity, no attachment; a four-vertex counterexample is proved),
  the corrected cut-vertex form and the separator form (§38's Lemma A) are
  proved, the latter through a linked form that needs no common `S` at all.
- **The rule seed as a certification speed-up at scale** (§28 addendum,
  2026-09-29): no; on four instances at 100–125 the descent's nodes agree to
  within 0.2% under either seed, the refutation being the same search.
- **Novelty of the expansion bound** (2026-09-28, `reports/expansion_bound.md`
  §4, `literature/MISSING.md`): none; it is Harper's vertex-isoperimetric
  bound (Harper 1966; on pathwidth Chandran & Kavitha 2006, Lin & Lin 2025).
  The capped exact computation and the corpus measurement are ours.
- **Learned upper bounds, learned lower bounds, learned branching** as routes
  to faster solving (`reports/learning_plan.md` §4, inherited): closed before
  these plans and confirmed by them.

---

## 10. Open questions, by cost

Priced from the sections' own timings where one exists; "unpriced" where none
does. Nothing here is started.

**Minutes to an hour.**
- Replace `cs-dfs+degree`'s Python sort-key lambda by a tuple and re-time
  (§20); dominated by `rule+cs-dfs` either way (§28).
- Run `learning.sandwich --stage lean` as a CI check on the Lean `sorry`
  inventory (34 proved, one stated; §40).
- Whether §24's conjecture mining or the expansion bound sees the
  `(4, 2)` family of §27 — treewidth 2, pathwidth 4, biconnected, no K₄ — a
  one-command check on twelve graphs.
- Whether the first plan's GNN "is anything missing" check is worth running:
  §1 bounds in advance what 1-WL can lose on this corpus at nothing that shows
  in the optimum; it was never run (plan 1 §2.2).

**Hours.**
- Exact treewidth with 128-bit masks for the 82 gap ≥ 2 instances above 64
  customers, where §6's certificate rate collapsed to 5.7% (§21, §27 note
  (iii); the search is under a second to 64, unpriced above); it would also
  settle the eight seed-on-an-interval "beats" of §38.
- Move `bm-first`'s citation check out of the subset loop and re-measure in
  seconds on the two day-long 125 × 125 classes (§31; the harness stage is
  53 + 35 s on 14 workers, the scale stage 27 minutes).
- A per-component cost model, the fix for the one class §19 misses (the 96%
  decomposable 100-customer `d = 2` cell); and the model's `opt_frac`
  sensitivity, 1.1 decades between the heuristic UB and the certified
  optimum on `i012` (§34); unpriced, the current model fits in 0.2 s.
- The per-node overhead of the C `better_move` (1.17× at ≤ 100 in §22,
  1.1–1.5× on the 100 ridge cell in §34): whoever touches the C decides #7.
- A satisfiable-side portfolio or fan order in `ratchet` and `recertify`,
  paired in nodes (#5, #9; §33 confirms the case at 100).
- The component-form corollaries of the branch lemmas and moving
  `pathGraph_isTree`, `pathGraph_induce_interval_connected` and
  `induce_singleton_connected` to `ForMathlib/` (§39, §40); the minor
  monotonicity of pathwidth that `contract-branch` also rests on (§40).
- A race of the pre-encoding re-cover on the SAT path (§30, #17).
- Where the 75 → 100 rise in the ridge's rate starts for each product ratio:
  it is absent at `n / 4`, +0.03 per customer at `n / 2` and +0.045 at
  `m = n` (§37); the cheap ridges at 100 cost minutes per instance.

**Days.**
- The 489 corpus instances at n ≤ 40 without a DRAT proof: another factor of
  five in conflicts would buy perhaps 150 for ~40 core-hours; the 295
  Harvey/Simonis 30 × 30 at `k` 21–30 are the bulk (§17). Every one of the 489
  already carries a search certificate (§32).
- **Re-certifying the withdrawn 125 × 125 entries.** Two are still open
  (`Random-125-125-2-2_0`, `-2-3_0`), running since 2026-09-24 on the pre-fix
  library with five-day budgets, four days spent when §35 was written; §35's
  law prices a ridge refutation at a median of **55 h pre-fix on one core,
  ×/÷ 10 per instance** (the record's own counts took 25–72 h), so the budget
  covers the median and not the tail. Re-refuting all eight 125 × 125
  instances on the fixed code — the six on record carry the pre-fix caveat —
  costs at least the fix ratio more: **≥ 2.34× (the 100 cell) to ~20× (≥ 19.6×
  on the one measured ridge instance)**, a median of ≥ 130 h (5.3 days) per
  instance on one core, some six core-weeks in all, the `d = 2` tail at a
  week or more each. That is the price of a clean corpus at 125 × 125, and it
  is a `csearch` price; `default` at 125 has no count on record (§31, §35).
  *(2026-09-30: both still open; the corpus stands at 6,374 of 6,376
  certified.)*
- **The `m = n` ridge at 100 beyond 28 core-hours** (§34): 24 of 25
  instances stand as verified upper bounds with the step below undecided at
  3.4–4.8 × 10⁹ nodes under `csearch`; the cost model priced the 25
  `default` refutations at 45.3 core-hours and the `csearch` ones at 21.3,
  and 17.1 bought one; one value was not optimal (§35), so a descent must be
  re-asked before a refutation is trusted.
- **Post-fix 125 counts** (§35): every `csearch` count below 100 is pre-fix
  and there is no post-fix series to fit; the ≥ 2.34× multiplier is one exact
  pair and four lower bounds at 100. Post-fix rate constants for §14 and §16
  likewise (§18).
- The n = 12 census (§27): about 240 core-hours at level 0 for `pw − tw ≥ 2`,
  4,300–4,700 for the joint table; `pw − tw = 3` at 12 — the first size at
  which it is possible — is cheaper with `geng -c -d2` and a treewidth lower
  bound before the DP. Nothing between 12 and 50 was searched for a gap of 3.
- A C emitter for the search certificate (§32, #18) and, with it, certificates
  for the eight instances the differential harness priced out at 100 (§33,
  #22): above that boundary the soundness check is the certificate or nothing.

**Unpriced, and the ones that matter most.**
- **A sound refutation check above 100 customers.** The lattice oracle
  reaches 15 (20 vectorised), the differential harness 40 on ten labellings
  (§15) and 100 on five, except the eight ridge and shoulder instances (§33);
  the search certificate reaches 75 with the Python emitter (§32); the DRAT
  path `m² · k ≈ 10⁴`. Above that the two-arm agreement of §22 and the
  relabelling agreement of §18 are all there is, and at 125 × 125 the
  certificate is the 10¹¹-node tree itself.
- **The encoding's correctness in Lean** (`encode_mosp_decision` satisfiable
  iff MOSP ≤ k): with it, §17's 5,646 proofs become end-to-end certificates.
  With Yanasse's equality now proved (§26), the graph side of that chain is
  closed and this is the remaining formal gap on the SAT side; on the search
  side it is #20, the three dominance theorems. *(Corrected 2026-09-30: the
  abstract encoding is already proved faithful, `encodes_iff_mospValue_le` in
  `lean/MOSPFormalization/Encoding.lean`, `sorry`-free since 2026-09-18,
  `reports/encoding.md` §8. What is open is that `mosp_encoding.py` emits
  those clauses and that the AMO and totalizer clause forms mean what the
  Lean models them as.)*
- **A pathwidth lower bound that is a different argument**: the family §6
  drew, §21 minimised and §27 enumerated (including the biconnected `(4, 2)`
  shape), on which every degree, clique and treewidth bound is provably
  blocked on about half the gap instances; §24 says the bound work needs a
  new idea, not a new formula, and §38 that the idea is not branching at any
  separator the clique structure exposes. The harness of 1.5 is where the
  next candidate goes.
- **The reachable count in the random model** (§36): the ridge is where the
  reachable region of the closed-set lattice is largest; deriving that count
  is a first-passage problem over `2^n` states, not attempted.

---

## 11. Costs, provenance and where the numbers live

**Compute.** Plan 2 §0 records loop0001 at 3.1 session-hours and loop0002 at
2.1; the campaign of §10 cost 2.16 core-hours, §14's corpus counts 5.65.
loop0003's items, from their sections and PROGRESS entries: §15 199 s on 16
workers; §16 11.1 + 9.6 core-hours; §17 13.0; §18 5.95 + 10.5; §19 11 s; §20
9.25; §22 5.3; §21 2.73 plus the corpus pass; §24 6.6 plus about 10 minutes
on 16 workers; §23 226 s on 8 workers plus 1.8; §25 0.36; §26 a 2-second
`lake build` from the cache; §27, its reserve item, 13.2 core-hours for the
n = 11 pass plus 20 s for n ≤ 10. Summed from those lines, about 80 core-hours
for the third loop before the census and about 93 with it. loop0004's items,
from their sections: §28 about 12 minutes on 16 workers; §29 10 s; §30 65
minutes on 16 workers; §31 53 + 35 s and 27 + 10 minutes on 14 workers; §32
15 + 6 s on 16 workers and a 60-s-per-call pass at 41–75; §33 5.96 + 0.45
core-hours (priced 8.23); §34 26.4 core-hours; §35 15.2 core-hours plus 8
minutes on 8 workers; §36 5 s, 26 minutes on 12 workers and 4.5 minutes; §37
about 90 minutes on 16 workers; §38 7.4 core-hours plus 3 + 4 minutes on 4
workers per candidate; §39 and §40 a 2-second `lake build` each. Summed from
those lines, with the worker-minute entries converted at their stated worker
counts, about 115 core-hours for the fourth loop, a sum of quoted figures
and not a measurement; the loop itself ran 2026-09-27 16:29 to 2026-09-28
06:10 in thirteen sessions (CLAUDE.md). None of it is corpus compute: nothing
was written to `solutions/` in any of the four loops (§34's and §35's
witnesses live under `learning/data/ensemble/solutions/`).

**Dated counts.** `csearch` node counts exist from three versions of the C
search (before 2026-09-23, between the two fixes, after `0eb33915`).
`results.csv`, `results_upward.csv`, `scale_nodes.csv` and the six 125 × 125
recertify counts are pre-fix — §31's `prefix` variant reproduces
`results_upward.csv` on 3,334 of 3,348 settled refutations and §35 dates the
recertify workers to a library built before the fix; `portfolio.csv.gz`,
`fan_order.csv.gz`, `theorem2.csv.gz`, `fix_cost_*.csv`,
`differential_scale.csv`, `ridge100_calls.csv`, `results_height.csv` and
`bound_harness_values.csv.gz` are post-fix; `ridge100_prefix_calls.csv` is a
post-fix run of the pre-fix rule; `default` counts are unaffected everywhere
(§18 (e), §19, §31). A rate or a model is for the version that made its
training counts: §16's and §35's laws and §19's `csearch` model are pre-fix;
the post-fix reading of any 125 figure is the pre-fix figure times at least
2.34 (§35).

**Artifacts.** `learning/data/ensemble/` (committed): manifests and results
for the campaign (§10), the upward run (§16), the ratio cells (§25), the
height cells (`manifest_height.csv`, `results_height.csv`,
`height_effective_m.csv`, §37) and the 100 ridge cell
(`manifest_ridge100.csv`, `ridge100_price.csv`, `ridge100_calls.csv`,
`ridge100_prefix_calls.csv`, §34, §35), with witnesses under its `solutions/`;
`scale_nodes.csv` (§14); `recover*.csv`, `relabel.csv.gz` (§13);
`differential*.csv` (§15); `portfolio*.csv` (§18); `cost_model_*.csv` (§19);
`fan_order.csv.gz` (§20); `extremal_*.csv` (§21); `theorem2.csv.gz` (§22);
`set_imitation_*.csv` (§23); `conjecture_*.csv` (§24); `pwtw_census.csv`,
`pwtw_found.csv`, `pwtw_totals.csv` (§27); `sat_story.csv.gz` (§30);
`fix_cost_harness.csv.gz`, `fix_cost_scale.csv` (§31);
`search_certificate.csv` (§32; the certificates themselves are not stored,
every one regenerates in milliseconds); `differential_scale*.csv` (§33);
`cover_excess_measures.csv`, `cover_excess_states.csv` (§36);
`bound_harness_values.csv.gz`, `bound_harness_attack*.csv` (§38).
`learning/data/canonical.csv` (§1), `proofs.csv` and `proofs_200k.csv` (§17;
the 11.7 GB of proofs are git-ignored under `learning/data/proofs/`).
Git-ignored and regenerable in seconds to minutes: `learning/models/union/`
and `learning/data/rule_seed/` (§28), `learning/data/mcnh/` (§29),
`learning/data/pwtw/` and `learning/data/extremal/solutions/` (§27),
`learning/data/bound_harness/` (§38). Every table quoted in
`reports/ml_nature.md` is in full in its `reports/*_tables.md` companion —
for loop0004, `rule_seed_tables.md`, `mcnh_tables.md`, `sat_story_tables.md`,
`fix_cost_tables.md`, `search_certificate_tables.md`,
`differential_scale_tables.md`, `ridge100_tables.md`, `rate_drift_tables.md`,
`cover_excess_tables.md`, `ridge_height_tables.md`, `bound_harness_tables.md`
and `sandwich_tables.md` (the axiom list of every named theorem). The Lean
development: `lean/MOSPFormalization/MOSPGraph.lean` and
`MOSPGraphExamples.lean` (Yanasse's equality and the star counterexample,
2026-09-27), `Sandwich.lean` (1,099 lines: the sandwich, the
tree-decomposition section, the branch lemmas and their separator form),
`Reduction.lean` with its false statements deleted; the inventory in
`learning/sandwich.py` (`PROVED`, 34 names; `STATED`, one).

**What no section says.** No section changes a solver default, touches
`_lower_bound`, or writes to `solutions/`. No prediction in this file is a
bound. No number below 100 customers is evidence about 125 × 125 except the
extrapolations of §14, §16, §25, §35 and §37, each labelled as one.
