# Machine learning and the nature of MOSP — the synthesis

*2026-09-26, loop0003 item 13 (plan 2 §2.11). One paragraph per claim the two
plans produced: `reports/ml_nature_plan.md` asked ten questions, answered in
`reports/ml_nature.md` §1–§14 (loop0001, loop0002); `reports/ml_nature_plan_2.md`
asked eleven, answered in §15–§26 (loop0003). Every number below is copied
from the section cited and regenerates by the command that section names;
this file computes nothing and is not a bound. Where a later section corrected
an earlier one, the paragraph gives the corrected value and cites both.*

**How to read a paragraph.** Each ends with three lines: the **size range**
the claim covers, the **regenerate** command (the section holds the full form
with flags and timings), and a **status** from the plan's four words —
*finding* (a measured statement about the instances or the solver),
*conjecture* (checked on every certified instance, proved nowhere), *proposed
solver change* (measured behind a flag or in a report, never enabled here) and
*closed question* (measured, answered, not to be rebuilt) — plus *theorem* for
what `lake build` accepts without `sorry` (§26).

**The rules the work ran under.** A prediction is never a bound: nothing
learned reaches `satisfiability/mosp_solver.py::_lower_bound` or any path that
decides `k`. No solver default changed in three loops; the one change to
solver code, the C `better_move` fix, landed through the owner
(`reports/better_move_bug.md` §7). Every split groups by file ∪ MOSP-graph
isomorphism class. Hardness is counted in nodes, never seconds. A censored
call is a lower bound, never a missing value. Every conclusion states its size
range: the corpus is 6,376 instances at 9–134 customers, the campaign 37,800
generated instances at 10–40 plus 6,785 at 50–100 and 2,750 at 50–75, and
nothing below 100 is evidence about 125 × 125 except through a stated
extrapolation.

---

## 0. In one page

- **The corpus is 3,667 distinct MOSP graphs, not 6,376 instances**, a quarter
  of them complete graphs; the generators are fingerprintable at 94.4% from
  structure alone; instance space is a lattice of 74 size cells (§1, §2).
- **The optimum is sandwiched**, `degeneracy + 1 ≤ optimum ≤ bw_rcm + 1`, on
  every certified instance; both ends are now **theorems in Lean** for every
  finite graph, with Yanasse's equality the one trusted step between them and
  the optimum (§5, §26). Min-fill treewidth + 1 is the best point estimate to
  about 50 customers and 4 stacks high at 125 (§4, §14).
- **The proved bound fails structurally**: three of its four components bound
  treewidth, and pathwidth strictly exceeds treewidth on 48.5–76.3% of the
  338 instances it misses by two or more; the smallest graph with
  `pw − tw = 2` has 10 vertices (§6, §21). Exact treewidth + 1 beats the
  solver's bound on 933 corpus instances; no mined formula beats
  `max(lb_best, tw + 1)` anywhere treewidth is exact (§24).
- **Hardness has a ridge** at cover excess `(n_ones − m) / n ≈ 2–2.4`, one
  independent cycle of the incidence graph per customer; on it the refutation
  doubles every 2.9–3.5 customers, at a rate that itself falls by 0.002 per
  ten customers; the 125 × 125 ridge counts on record are predicted to 0.04
  decades (§11, §16, §25). Hardness is a property of the labelled graph and of
  nothing else in the matrix (§13).
- **Every refutation at n ≤ 40 is sound on twenty independent searches, and
  92.0% of them now carry a DRAT proof a third party has checked**; the
  harness found a false `unsat` at the *optimum* in the C `better_move`,
  fixed by the owner (§15, §17).
- **Three search rules measured, none worth enabling for refutations**: fan
  order changes 0.0% of nodes; a relabelling portfolio wins 1.00–1.01×;
  Theorem 2 always-on saves 6.6% of nodes and loses 5% of seconds. The
  satisfiable side is where labels and fan order pay (§18, §20, §22).
- **Imitation is closed**: the optimum is never unique (10⁵ optimal orders at
  n = 10, 10¹⁰ at 15), a one-sentence rule beats the ranker, and with the
  exact set of optimal moves as label the best policy beats the rule by 0.008
  MAE against a kill of 0.02 (§7, §8, §23).
- **A cost model puts 88–89% of the 100–125 refutation counts within a
  decade** and orders the recertify queue (§19).

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
Stuckey's "density 2" is 2.7–2.8 realised.
*Size range:* 10–40. *Regenerate:* `python -m learning.ensemble --item02 --workers 16 --verify-manifest 0`.
*Status:* finding (infrastructure; the artifact is `learning/data/ensemble/`).

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
all 6,376, a theorem checked for free.
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
`#print axioms` giving `[propext, Classical.choice, Quot.sound]` on every one
of the thirteen theorems named in `learning.sandwich.PROVED`; the layout-level
form `pathwidth_le_bandwidthOfLayout σ` is literally the `bw_rcm` check of §5.
The Lick–White and elimination-ordering forms of degeneracy are proved equal
by the greedy ordering. The definitions are pinned to the corpus's
implementations by brute force on all 1,099 labelled graphs on 1–5 vertices
(zero violations against networkx's core number and the exact pathwidth DP)
and by kernel `decide` on four graphs. The corpus recount gives 6,376 / 6,376
on both ends, 3,293 / 3,279 tight, 2,823 with both ends coinciding — §5's
number regenerated. Yanasse's equality is still a hypothesis in the
development (`Reduction.lean` has `≤` under `IsReduced` with a `sorry`, no
`≥`), so `degeneracy + 1 ≤ mospValue` is proved *given* `mospValue = pathwidth + 1`.
*Size range:* every finite graph; corpus recount 9–134. *Regenerate:*
`cd lean && lake build; python -m learning.sandwich`. *Status:* theorem
(two, plus the chain and the sandwich statement).

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
338 and on 8 of the 10 smallest. Only the expansion bound is a pathwidth
argument; it passed the ceiling on 36 instances.
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
customers). The soundness objective `disagree` was flat at zero.
*Size range:* search 7–20; exact treewidth on every corpus instance at 9–20
and every gap instance at 20–50 (22 by interval). *Regenerate:*
`python -m learning.extremal --stage corpus --workers 8; --stage search …; --stage tables`.
*Status:* finding; kill met for `disagree` only.

**3.3 Exact treewidth is the theorem the solver does not compute; the
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
dense shoulder. Pre-registered here: the ridge law says 5 × 10¹¹ nodes at 125.
*Size range:* 10–40; peaks on n ≥ 15, order parameters on n ≥ 20; Chu &
Stuckey placement at 30 and 40. *Regenerate:* `python -m learning.hardness_map`.
*Status:* finding; kill (monotone, no peak) not met.

**4.2 Hardness is a property of the labelled graph and of nothing else in the
matrix (§13).** Re-covering the same edge set with different cliques — 15,900
re-coverings of 1,400 instances, products removed or added by up to 30 —
leaves the default node count *exactly* unchanged in every pair (the search
reads neighbour masks and nothing else, and the C and Python agree on all
15,900), and graph-only features predict nodes as well as graph plus matrix
(MAE 0.0948 vs 0.0968), matrix-only 25–30% worse. Two things move the count
and neither is the cover: **relabelling** the customers (2–6% at the median,
up to 2.26× default and 8.1× `csearch`; the search's tie-breaks, the floor for
any label-free predictor) and the `csearch` rule that switches Theorem 2 on by
a matrix statistic (10–13% at the median, up to 25%, pre-fix, always in its
favour; a design choice of `sparse_enough_for_better_move`). The matrix does
carry the number of optimal closing orders under the construction value — by
up to three orders of magnitude at n = 15 — while the count under the search
measure is identical in all 4,516 pairs. 15,900 free audits of Yanasse's
equality passed.
*Size range:* 10–40. *Regenerate:* `python -m learning.graph_story --workers 16 --per-n 200 --per-method 4 --relabellings 20`.
*Status:* finding; kill met (the matrix adds nothing to hardness prediction).

**4.3 The refutation grows exponentially to 125, at a rate the n ≤ 40 cells
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

**4.4 The rate drifts down with `n`, and that is the whole discrepancy (§16).**
The campaign extended to `n ∈ {50, 60, 75}` at `m ∈ {n/2, n, 2n}` (6,750
instances, 6,747 certified, 11.1 core-hours) and a priced sample at n = 100.
The exponential form holds to 75 in every series (4–11× better than a power
law) and to 100 where there is data. The local rate falls with `n` in 18 of
18 fixed-`d` series, pooled at **−0.000217 ± 0.000045 log10 per customer per
customer** (t = −4.8): about 0.002 per ten customers, or 0.011 between the
midpoints of §11's and §14's windows, which is the 0.005–0.018 §14 measured;
fitted at 50–100 the campaign reproduces the corpus's rates to 0.005. Drift-
corrected from the 75-customer cells, the ridge law predicts the two
`Random-125-125-2` counts on record to 0.04 decades (11.18 against 11.21,
11.22) with a band of ±0.8 decades: **1.5 × 10¹¹ nodes (2.5 × 10¹⁰ to
9 × 10¹¹) for density 2 and 4 × 10¹⁰ (1.8 × 10¹⁰ to 1.1 × 10¹¹) for density
4**, 30 hours (5 to 180) and 8 hours (3.5 to 22) per refutation on one core.
The ridge stays at `d = 3` (`m = n`) and `d = 2` (`m = 2n`) through 75 and
sits at 5–6 for `m = n/2`. The n = 100 ridge cells were priced at 40
core-hours against the plan's cap of 8, so the grid stopped at 75; the
5-per-cell sample confirmed the price (nine of ten descents ran out at 900 s,
two of the values reached were not optimal).
*Size range:* 10–75 fully certified; 100 for `d = 2` (25 certified) and a
sample at `d = 3, 4`; every 125 figure is a 50-customer extrapolation from 75.
*Regenerate:* `python -m learning.ensemble --upward …; python -m learning.upward`.
*Status:* finding; kill (100-customer ridge cells over 8 core-hours) met.

**4.5 The ridge is a condition on the excess of the product cover (§25).**
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
height. Placed by the excess, the 125 × 125 ridge is at `col_mean ≈ 3`,
between Chu & Stuckey's densities 2 (excess 1.76) and 4 (3.2), nearer 2 — a
prediction, not a measurement. The deciding cells (`m = n/4` at 50–75,
`m = n/8` at 75; 2,750 instances) were generated for this item.
*Size range:* 50–75, `m / n ∈ {⅛ (75 only), ¼, ½, 1, 2}`, 9,497 instances in 190
cells; 30–40 confirms excess 2.0–2.6. *Regenerate:*
`python -m learning.ridge_theory --stage {run,cliques,tables}`.
*Status:* finding (no kill stated).

**4.6 A cost model predicts a refutation to within a decade at 100–125
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
§11 law −0.3). Cheapest-first for the three still withdrawn:
`Random-125-125-2-5_0`, `2-3_0`, `2-2_0` (11.15 / 11.34 / 11.85 log10 nodes;
22 / 33 / 107 h at 0.55 µs per node). Every prediction is for the pre-fix
`csearch`; post-fix ridge counts at 100 are ≥ 15× larger (§18) and the model
has never seen one at 125.
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
when the stored value is right.
*Size range:* 9–40; every statement about 125 × 125 is about which code runs
there. *Regenerate:* `python -m learning.differential --workers 16` (`--stage drawn`, `--stage shrink`).
*Status:* finding; the proposed fix was **applied by the owner**;
`tests/test_differential.py` pins the two minimal counterexamples (10 × 13,
17 × 9).

**5.2 92.0% of the corpus at n ≤ 40 carries a DRAT proof a third party has
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

**5.3 Independent audits that came free.** The lattice oracle
(`learning.degeneracy`, sharing no code with the search) equals the certified
optimum on all 2,812 corpus instances at n ≤ 15 and on 256 generated ones
(§8), on 4,916 re-covered instances (§13), on 13,612 in the differential run
(§15) and on 4,122 at n ≤ 20 through the vectorised lattice (§23);
`optimum − 1` re-refutes on all 6,135 at n ≤ 40 under two configurations
(§3); isomorphic instances carry equal optima in every class (§1); the
sandwich holds on all 6,376 + 37,800 (§5, §12); 15,900 re-coverings solve to
their base's optimum (§13); 27,000 relabelled refutations at 40–100 contradict
nothing (§18); 50,861 paired refutations and 50,909 witness searches agree
across Theorem 2 arms (§22); 407,168 calls agree across fan orders (§20).
Nothing was re-certified because nothing disagreed, except the 56 instances of
5.1, whose values were right. **Nothing above 40 customers is checked by
anything outside the search** except the relabelling agreement of §18 and the
two-arm agreement of §22 at 41–125.
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
and 3.5× on `Random-100-50-2/4`, ≥ 15× on `Random-100-100-2-4`; every
`csearch` count in `results.csv`, `scale_nodes.csv` and the recertify record
is pre-fix, and the post-fix cost at 125 is not known.
*Size range:* campaign 40–75, corpus 50–100; the race at 100 on four
instances; the 125 projection is an extrapolation of a flat curve.
*Regenerate:* `python -m learning.relabel_portfolio --workers 16 --deadline 120`; `--stage race …`.
*Status:* closed question for refutations (kill met: median min-of-8 at
n ≥ 60 is 1.003); proposed solver change for satisfiable-side drivers only
(`ratchet`, `restricted_dfs` seeds, the `k ≥ optimum` calls of a descent).
Recommendation for `recertify`: do not add a portfolio.

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
the *seed*, not the fan order.
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
0.826 but 1,253 costs, max 184×.
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
against `cs-dfs+lgbm` 0.157 / 91.0%. Fiedler order keeps 66% of the gain with
no state at all; BFS from a min-degree root does not. The ranker imitates the
witness at 45.3% of steps, below MCN's 52.5% and the rule's 62.3%: imitation
rate ranks constructions almost inversely to their value.
*Size range:* 9–134 on 1,920 held-out instances, 1,768 at ≤ 30; above 60
customers it rests on 56 instances with the rule 3.7 stacks off.
*Regenerate:* `python -m learning.distil --workers 16`. *Status:* finding;
kill (no readable rule keeps half the gain) exceeded at 115%; proposed solver
change (register the rule as a heuristic and as the `cs-dfs` seed), not
applied.

**7.2 The optimum is never unique (§8).** Exact path counting over the subset
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

**7.3 Imitation is closed for good (§23).** With the construction-measure
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

Every entry is behind a flag that defaults to today's behaviour or lives in a
report; enabling any of them is the owner's change. "Decides" names the
measurement that would settle whether to enable it, or that already has.

| # | change | proposed in | measured effect | what decides it | state |
|---|---|---|---|---|---|
| 1 | Fix the C `better_move` (cross-rule composition; wrong close count; early exit) | §15 | false `unsat` at the optimum on 0.32% of sparse instances at 10–40; fix costs `csearch` refutations +7.3% nodes at n ≤ 40, ≥ 15× on `Random-100-100-2-4_0` (§18) | the differential harness at 0 disagreements — done | **applied by the owner** (`0eb33915`; `better_move_bug.md` §7) |
| 2 | Exact / interval treewidth as a `_lower_bound` component | §24 | floor rises on 933 corpus instances, 67 gap instances become bound-certified; 0.2–1 s per instance (39 s worst); valid on all 50,949 ("above optimum" = 0) | a descent timing over the 25 hardest instances, as `reports/expansion_bound.md` §6 did — a floor shortens a descent only where it equals the optimum, and it never does where `pw > tw` (68% of exact gap instances). Rests on Yanasse's equality like the contraction component | proposed |
| 3 | Register the two-key rule as a heuristic and as the `restricted_dfs` seed | §7 | `cs-dfs+rule` 0.127 / 92.7% vs `cs-dfs+lgbm` 0.157 / 91.0% vs `cs-dfs` 0.311 held out (1,920) | `learning.corpus_sweep` over all 6,376 with the rule seeding `restricted_dfs`, against `learned+cs-dfs`'s 709 better / 13 worse (`reports/learning.md`); would settle the LightGBM dependency question | proposed |
| 4 | `fan_order="degree"` on `decide` | §20 | refutation 0.0% at every size (kill met) | decided: keep `index` | closed |
| 5 | `fan_order="degree"` for satisfiable-side drivers (`ratchet`, the `k ≥ optimum` calls of a descent) | §20 | −35% witness nodes at 75, −13% at 100 in total; p90 cost 1.1–1.3× | a paired run of `benchmarks.ratchet` under both orders in nodes | proposed |
| 6 | `cs-dfs+degree` as the `cs-dfs` default | §20 | +0.1 pt exact, −1.3% total overshoot, corpus 99–100 MAE 3.21 → 2.95; 50% slower in Python | replace the sort-key lambda by a tuple, then re-time; still second to #3 | registered, not default |
| 7 | Theorem 2 always on (`sparse_enough_for_better_move` → true) | §22 | nodes −6.6% where the hand rule is off (one cost of 1.2%); seconds +5% on heavy hand-off refutations at 1.167× per node | the C `better_move`'s per-node overhead: below 1.03 always-on wins the clock from 50 up | proposed and **recommended against** (keep 5) |
| 8 | A relabelling portfolio in `benchmarks.recertify` | §18 | min-of-16 refutation speed-up 1.00–1.01, core efficiency 0.063 | decided at 40–100 | recommended against |
| 9 | A relabelling portfolio on satisfiable calls | §18 | 8–13× where the witness search is hard, core efficiency 0.5–0.8; 2–5% of a descent pair | same as #5 | proposed |
| 10 | The cost model to order and size the recertify queue | §19 | 88–89% of 100–125 counts within a decade; order `2-5_0, 2-3_0, 2-2_0` | the three entries finishing (predicted 22 / 33 / 107 h at 0.55 µs, pre-fix) | proposed, for ordering only, never for `k` |
| 11 | `learned+cs-dfs` as the default upper bound | `reports/learning.md` | 709 better / 13 worse than `cs-dfs` over 6,376; needs LightGBM on the critical path | superseded by #3: the rule seeds better with no model | registered, not default |
| 12 | Group `learning/study_optimum.py`'s split by `graph_cert` | §1 | file grouping leaks 157 classes across files | a study change, not a solver change | proposed |
| 13 | Draw `test_better_move_never_changes_a_decision`'s instances at 1–3 products per customer and add the two minimal counterexamples | §15 | the dense family it drew never ties enough candidates to expose the cycle | done if the strict `xfail` in `tests/test_differential.py` has been promoted | proposed |

---

## 9. Closed questions

Measured, answered, and not to be rebuilt without a new idea. Each has a
section explaining the mechanism, not only the outcome.

- **Fan order for refutations** (§20): 0.0% at every size; the visited state
  set is order-independent.
- **A learned boundary for Theorem 2** (§22): "always on" in nodes, the hand
  threshold in seconds; no learned rule beats 5 on the clock.
- **A relabelling portfolio for refutations** (§18): the spread shrinks with `n`.
- **Imitation, single-witness and set-valued** (§7, §8, §23): the target is
  90% arbitrary; the rule is already optimal at 99.7% of states; the ceiling
  is 0.10 at 125.
- **A branching-aware lower bound as a two-invariant formula over the thirty
  invariants of §24**: theorems in disguise or sample maxima; the new idea has
  to see separators of trees of cliques.
- **Degree statistics as the residual's formula** (§4, §5): they saturate at
  the average degree and know what the bound knows.
- **Mean degree as the ridge's coordinate** (§25) and **`optimum / n` as its
  size-stable coordinate** (§14): the excess is; `col_mean` at fixed `m / n` is.
- **Intervals calibrated at n ≤ 40 quoted at n ≥ 50** (§14): every one fails
  at the first band beyond calibration.
- **The clique cover as a hardness factor** (§13): exactly nothing, with
  labels fixed.
- **DRAT proofs for 125 × 125 through the direct encoding** (§17): the
  boundary `m² · k ≈ 10⁴` is crossed at k = 1.
- **`disagree` as an extremal objective on the fixed C** (§21): flat at zero.
- **Learned upper bounds, learned lower bounds, learned branching** as routes
  to faster solving (`reports/learning_plan.md` §4, inherited): closed before
  these plans and confirmed by them.

---

## 10. Open questions, by cost

Priced from the sections' own timings where one exists; "unpriced" where none
does. Nothing here is started.

**Minutes to an hour.**
- Exhaust the 274,668 graphs on 9 vertices for `pw − tw ≥ 2` with the DP and
  the lattice oracle, making the 10-vertex record a theorem (~1 core-hour, §21).
- `learning.corpus_sweep` with the two-key rule seeding `restricted_dfs`
  against `learned+cs-dfs`'s 709 / 13 (~8 min, §7; decides #3 and #11 above).
- Replace `cs-dfs+degree`'s Python sort-key lambda by a tuple and re-time (§20).
- Run `learning.sandwich --stage lean` as a CI check on the Lean `sorry`
  inventory, extending `PROVED` with `Reduction.lean`'s names (§26).
- Whether the first plan's GNN "is anything missing" check is worth running:
  §1 bounds in advance what 1-WL can lose on this corpus at nothing that shows
  in the optimum; it was never run (plan 1 §2.2).

**Hours.**
- Exact treewidth with 128-bit masks for the 82 gap ≥ 2 instances above 64
  customers, where §6's certificate rate collapsed to 5.7% (§21; the search is
  under a second to 64, unpriced above).
- Lean gap 1, `treewidth_le_pathwidth`: needs `(pathGraph n).IsTree`, which
  Mathlib lacks, and the connectivity of an interval of the path graph;
  estimated 2–3 hours (§26). Gap 2, the branch lemma, depends on it.
- A per-component cost model, the fix for the one class §19 misses (the 96%
  decomposable 100-customer `d = 2` cell); unpriced, the current model fits in
  0.2 s.
- Halving the ±0.8-decade band on the 125 × 125 prediction: 200 instances per
  cell at 75, or one certified ridge cell at 100 at about an hour per
  instance (§16).
- The per-node overhead of the C `better_move` (1.17×): whoever touches the C
  decides #7 (§22).
- A satisfiable-side portfolio or fan order in `ratchet`, paired in nodes
  (#5, #9).

**Days.**
- The 489 corpus instances at n ≤ 40 without a DRAT proof: another factor of
  five in conflicts would buy perhaps 150 for ~40 core-hours; the 295
  Harvey/Simonis 30 × 30 at `k` 21–30 are the bulk (§17).
- Re-certifying the three withdrawn 125 × 125 ridge entries on the fixed C:
  25–53 h each pre-fix, larger post-fix by a factor measured as ≥ 15 at 100
  and not measured at 125 (§18, §19). Cheapest first: `2-5_0`, `2-3_0`, `2-2_0`.
- `pw − tw = 3` below 50 customers: nothing above 20 was searched (§21).
- Post-fix `csearch` rate constants for §14 and §16, which are pre-fix (§18).

**Unpriced, and the ones that matter most.**
- **A sound refutation check above 40 customers.** The lattice oracle reaches
  15 (20 vectorised), the differential harness 40, the DRAT path `m² · k ≈ 10⁴`;
  above that the two-arm agreement of §22 and the relabelling agreement of
  §18 are all there is, and the two known false refutations were above 40
  (§15, §17).
- **Yanasse's equality in Lean**: `Reduction.lean` has `mospValue ≤ pathwidth + 1`
  under `IsReduced` with a Hall-theorem `sorry` and no `≥`; every bound that
  is not a clique bound, and every theorem of §26 in MOSP terms, trusts it
  (§26).
- **The encoding's correctness in Lean** (`encode_mosp_decision` satisfiable
  iff MOSP ≤ k): with it, §17's 5,646 proofs become end-to-end certificates.
- **A pathwidth lower bound that sees separators of trees of cliques**: the
  family §6 drew and §21 minimised, on which every degree, clique and
  treewidth bound is provably blocked on about half the gap instances; §24
  says the bound work needs a new idea, not a new formula.

---

## 11. Costs, provenance and where the numbers live

**Compute.** Plan 2 §0 records loop0001 at 3.1 session-hours and loop0002 at
2.1; the campaign of §10 cost 2.16 core-hours, §14's corpus counts 5.65.
loop0003's items, from their sections and PROGRESS entries: §15 199 s on 16
workers; §16 11.1 + 9.6 core-hours; §17 13.0; §18 5.95 + 10.5; §19 11 s; §20
9.25; §22 5.3; §21 2.73 plus the corpus pass; §24 6.6 plus about 10 minutes
on 16 workers; §23 226 s on 8 workers plus 1.8; §25 0.36; §26 a 2-second
`lake build` from the cache. Summed from those lines, about 80 core-hours for
the third loop. None of it is corpus compute: nothing was written to
`solutions/` in any of the three loops.

**Dated counts.** `csearch` node counts exist from three versions of the C
search (before 2026-09-23, between the two fixes, after `0eb33915`).
`results.csv`, `results_upward.csv`, `scale_nodes.csv` and the recertify counts
are pre-fix; `portfolio.csv.gz`, `fan_order.csv.gz` and `theorem2.csv.gz` are
post-fix; `default` counts are unaffected everywhere (§18 (e), §19). A rate or
a model is for the version that made its training counts.

**Artifacts.** `learning/data/ensemble/` (82 MB apparent, committed):
manifests and results for the campaign (§10), the upward run (§16) and the
ratio cells (§25), with witnesses; `scale_nodes.csv` (§14); `recover*.csv`,
`relabel.csv.gz` (§13); `differential*.csv` (§15); `portfolio*.csv` (§18);
`cost_model_*.csv` (§19); `fan_order.csv.gz` (§20); `extremal_*.csv` (§21);
`theorem2.csv.gz` (§22); `set_imitation_*.csv` (§23); `conjecture_*.csv` (§24).
`learning/data/canonical.csv` (§1), `proofs.csv` and `proofs_200k.csv` (§17;
the 11.7 GB of proofs are git-ignored under `learning/data/proofs/`). Every
table quoted in `reports/ml_nature.md` is in full in its `reports/*_tables.md`
companion.

**What no section says.** No section changes a solver default, touches
`_lower_bound`, or writes to `solutions/`. No prediction in this file is a
bound. No number below 100 customers is evidence about 125 × 125 except the
extrapolations of §14, §16 and §25, each labelled as one.
