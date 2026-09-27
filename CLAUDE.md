# MOSP via Pathwidth Reduction — Status and Next Steps

## What This Project Is

This project tackles the **Minimization of Open Stacks Problem (MOSP)** by reducing it to **pathwidth computation** on graphs, with a formal proof of the reduction in Lean 4. MOSP is NP-hard (Linhares & Yanasse 2002).

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence for the products that minimizes the maximum number of simultaneously "open" customer stacks. A stack opens when the first product a customer needs is produced and closes when the last one is done.

## Terminology Correction: We Had the Two Graphs Swapped

Yanasse & Senne (2010, `literature/yanasse_senne_2010_properties_preprocessing.pdf`)
defines both graphs this literature uses, and says they are "completely different":

- **MOSP graph** — nodes are *item types* (customers), with an arc between two
  nodes iff some pattern contains both. `M @ M^T`. A pattern with k items becomes
  a clique of size k, so the graph is a union of cliques. **This is the graph the
  pathwidth equivalence is about**, due to Yanasse (1997c). In this repository it
  is `customer_inter/customer_graph.py`.
- **Pattern connection graph** — nodes are *patterns*, with an arc between two
  iff they share an item type. `M^T @ M`. The literature uses this for exactly
  one purpose: decomposing an instance into independent clusters (pre-processing
  1). In this repository it is `mosp/agreement_graph.py`, and the name
  "agreement graph" is ours, not the literature's.

So the claim recorded below — that `pathwidth(agreement graph) + 1` should equal
the optimum — attached the theorem to the graph the literature uses only for
decomposition. The undercounting we measured is not a counterexample to
Yanasse's result; it is a consequence of testing the wrong graph. Note also that
the graph result is **Yanasse (1997c)**, a different paper from the EJOR
"On a pattern sequencing problem..." (1997b) cited elsewhere in this repository;
there are at least three distinct Yanasse 1997 papers.

## Earlier Finding: Neither Graph Formulation Gave Exact MOSP Values

Recorded as measured. Read it in light of the correction above: the agreement
graph column was never expected to be exact, and the customer graph column is
confounded by a heuristic ordering derivation.

Validation against published optimal values (from Frinhani et al. 2018, computed using Chu & Stuckey 2009):

| Instance | Published OPT | Agreement graph (pw+1) | Customer graph (pw+1) |
|---|---|---|---|
| GP1 (50×50) | 45 | — | 45 |
| GP2 (50×50) | 40 | — | 40 |
| GP3 (50×50) | 40 | — | 40 |
| GP4 (50×50) | 30 | — | 30 |
| GP5 (100×100) | 95 | — | **96 (+1)** |
| GP6 (100×100) | 75 | — | 75 |
| GP7 (100×100) | 75 | — | 75 |
| GP8 (100×100) | 60 | — | 60 |
| SP2 (50×50) | 19 | — | **21 (+2)** |
| SP3 (75×75) | 34 | — | **35 (+1)** |
| SP4 (100×100) | 53 | — | **55 (+2)** |

The pathwidth computation itself is provably correct (SAT certifies optimality via UNSAT at k-1 / SAT at k). The problem is that:
- `pathwidth(G_a) + 1` (agreement graph) **undercounts** — gives a lower bound
- `pathwidth(G_c) + 1` (customer graph) **overcounts on sparse instances** — gives an upper bound
- Neither is tight for all instances

The overcounting on the customer graph arises because the customer-to-pattern ordering derivation is heuristic (sort by earliest/latest customer position), not optimal. A customer ordering that achieves optimal pathwidth does not necessarily produce a pattern ordering that achieves optimal MOSP.

**The correct approach is to encode MOSP directly as SAT**, bypassing the pathwidth reduction entirely. The SAT infrastructure (encoding, solver wrapper, CaDiCaL backend) built for pathwidth can be reused for a direct MOSP encoding.

## Bounds: No Longer the Weakest, and Still Weak Where It Matters

*(Rewritten 2026-09-18. This section used to say `_lower_bound` returned the
trivial bound of Yuen & Richardson (1995) — the maximum customers on any one
pattern — and that SP4's bound was 13. Both stopped being true when the clique
and contraction degeneracy bounds landed; see `reports/lower_bounds.md`.)*

`satisfiability/mosp_solver.py::_lower_bound` now returns the best of three:
the trivial bound, the largest clique found in the MOSP graph under a 5-second
budget, and contraction degeneracy (MMD+) plus one. On SP4 that is 27, not 13.

Validated over all 6,340 certified optima, 2026-09-18: **zero violations**,
tight on 65.7%, mean gap 0.86. This is a correctness dependency, not an
optimisation — a bound above a true optimum would make the search start above it
and return a wrong answer that still passes witness verification — so it is
re-checked whenever the corpus grows.

**Where it is still weak is exactly where the instances are hard.** The maximum
gap over the corpus is 42, and the eight worst are the dense 125-125 Chu &
Stuckey instances; across the 166 certified `Random` instances the mean gap is
11.05 against 0.86 corpuswide. A binary search over a 40-wide interval spends
its budget on refutations far below the optimum, which is why the SAT path never
closed them and why `satisfiability/customer_search.py` — which descends from
the *upper* bound instead — does.

**A fourth bound, better on paper and a net loss in practice** *(2026-09-22)*.
Head to head over the 25 hardest instances it makes the solver **slower on every
one** and is therefore **off by default** in `_lower_bound`. A floor only
shortens a descent when it *equals* the optimum -- otherwise the same `k` are
visited either way -- and where it is exactly tight the refutation it saves costs
**0.2s** while computing it costs **28s**. The ledger baseline that motivated the
chase was largely timeouts from an older configuration. `reports/expansion_bound.md`
§6. What follows is what it is worth as a bound, which is not in dispute:
`satisfiability/expansion_bound.py`: at any prefix `V_i` of a customer ordering
the finished customers `C_i` satisfy `N[C_i] ⊆ V_i`, so with
`f(t) = min_{|C|=t} |N[C]|` we get `vs(G) ≥ max_i (i − max{t : f(t) ≤ i})`.
Validated over all 6,376 certified optima at cap 8: **zero violations**, mean
gap **0.98 → 0.44**, tight **65.3% → 77.0%**, max gap 44 → 30, better on 1,329
instances, 196 s for the whole corpus. On the 125×125 instances the cap is a
dial — `Random-125-125-10-5_0` goes 59 → 98 against an optimum of 99 — and GP5
comes out exactly at its published 95. It rests on `MOSP = pathwidth + 1`, like
contraction degeneracy and unlike the clique bound; `BOUND_SOURCES` records
`expansion`. Prior art unsettled, no novelty claimed. `reports/expansion_bound.md`.

Why the older family could not be pushed further: they are all degree-based and
saturate at the average degree (bound 47, average degree 43.2, optimum 91 on
`Random-125-125-8-5_0`). LBN scores 12 points *worse* than contraction
degeneracy and LBN+ gains exactly zero.

**Why, structurally** *(2026-09-25, `reports/ml_nature.md` §6)*: the trivial,
clique and contraction-degeneracy components of `_lower_bound` are all lower
bounds on **treewidth + 1**, and `tw_min_fill + 1` is an upper bound on it, so
`optimum > tw_min_fill + 1` certifies pathwidth > treewidth with no heuristic
in the certificate. That holds on 131 of the 338 instances where the bound
misses by two or more (and on 8 of the 10 smallest, all 20×10), so three of
the four components could never be tight there under any budget or tie-break.
Only the expansion bound, the one pathwidth argument, passes that ceiling (36
instances). The bound-defeating family is *trees of cliques with branching*:
sparse, connected, degree-dispersed graphs of small product-cliques glued at
hub customers with a fringe of single-product customers. If the bound work is
resumed, that is the family to strengthen; degree and clique bounds are
provably the wrong place.

**Exact treewidth, and what is a theorem** *(2026-09-26, `reports/ml_nature.md`
§21, §24, §26, §27)*. `optimum ≥ treewidth + 1` is a theorem (via Yanasse's
equality and `tw ≤ pw`), tight on 77.9% of 50,949 certified instances and
above `lb_best` on 933 corpus instances (67 gap instances would become
bound-certified). `learning/treewidth.py` computes it exactly to 26 customers
by subset DP and to 64 by a decision search in 0.2–1 s per instance. Adding it
to `_lower_bound` is **proposed, not applied**: it is a better floor of the
same kind, blocked by the ceiling above on the 68% of exact gap instances
where `pw > tw`. Conjecture mining over thirty branching-aware invariants
found nothing that beats `max(lb_best, tw + 1)` where treewidth is exact; the
bound work needs a new idea, not a new formula. The smallest graph with
`pw − tw = 2` has 10 vertices (three K4s glued at three hubs plus a pendant
each), and a census of every graph on ≤ 11 vertices shows `pw ≤ tw + 1` on
all 287,884 graphs to 9 vertices, 4 exceptions at 10, 1,034 at 11 and none
with `pw − tw = 3`. Both ends of the sandwich, `degeneracy ≤ pathwidth ≤
bandwidth`, are proved in `lean/MOSPFormalization/Sandwich.lean` with no
`sorry`; `tw ≤ pw` and the branch lemma are stated there with `sorry` behind a
gap list (Mathlib lacks `pathGraph.IsTree`).

Still on record and still unobtained:

- ~~**arc contraction bound** (Yanasse et al. 1999)~~ — **settled 2026-09-22,
  the paper is now in `literature/`.** Its LB5 repeatedly contracts an arc at a
  minimum-degree node and keeps the largest (min degree + 1) seen, which *is*
  contraction degeneracy + 1 — the bound we already compute. **No novelty is
  claimed.** The only difference is the tie-break: they contract the arc whose
  endpoint degrees sum to the least, we contract into the neighbour sharing
  fewest neighbours. Comparing the two is an open measurement.
- any subgraph of the MOSP graph yields a valid bound, so bounds can be had by
  solving smaller subinstances — which is what `satisfiability/relaxation.py`
  now does by contraction, lifting SP4 from 27 to 45.

## Preprocessing: Two of the Six Implemented

*(Rewritten 2026-09-18; this section used to say we implemented none.)*

`mosp/preprocess.py` implements two of the six operations Yanasse & Senne (2010)
review, and `satisfiability.mosp_solver.decide_mosp` applies both on every SAT
decision call:

- **component decomposition** — the components of the MOSP graph share no
  customer and no product, so each is encoded separately;
- **pattern dominance** — a product whose customers sit inside another's is
  dropped and reinserted beside its dominator afterwards, at no cost.

Both preserve the optimum, so a refutation on the reduced instance refutes the
original. Firing rates over the 6,376-instance tree: dominance on 3,409,
removing 17,699 columns; decomposition on 154. On the instances that are
actually hard, 93 and **zero** — Chu & Stuckey discard decomposable instances
from their generator's output by design.

Still unimplemented: item reduction from pattern simplicity, and the reductions
from equivalent nodes and adjacent degree-2 nodes. Measurements in
`reports/preprocessing_measurements.md`.

A third operation, **contraction**, does not preserve the optimum and is kept
separate in the same module: it is a relaxation, and the basis of
`satisfiability/relaxation.py`.

**The MOSP–pathwidth chain, closed on held papers (2026-09-27).** MOSP = gate
matrix layout cost (Linhares & Yanasse 2002, Proposition 2, by definition);
gate matrix layout cost = pathwidth + 1 (Fellows & Langston 1989, Theorem 7:
one direction sketched there, the converse elementary); pathwidth = vertex
separation (Kinnersley 1992, Theorem 3.1, both directions); and the graph in
question is the clique-per-pattern graph of Yanasse (1997a), Proposition 5,
which is Lemma 4.1 of Fellows & Langston (1987) in matrix vocabulary — the
column-expansion lemma, proved there in both directions, that Theorem 7's
sketch relies on. Every paper in the chain is in `literature/`. What remains
is formal, not bibliographic: `Reduction.lean` has `mosp ≤ pathwidth + 1`
with one `sorry` and lacks the elementary converse (loop0004 item 12);
details in `literature/MISSING.md`.

### Key References

- **Kinnersley (1992)** — Established vertex separation = pathwidth. *Information Processing Letters*, 42(6), 345-350. In `literature/` since 2026-09-27. Its Theorem 3.1 is proved by the two constructions `LayoutToDecomposition.lean` and `DecompositionToLayout.lean` formalise; its Corollary 3.2 (gate matrix layout cost = node search number = vs + 1) with Linhares & Yanasse (2002) Proposition 2 is the published chain behind `MOSP = pathwidth + 1`; and its Corollary 4.2 with Fellows & Langston (1987) Lemma 4.3 is the **pathwidth branch rule** — three branches of cost k at one vertex force k + 1 — that loop0004 item 11 tests as a bound candidate: known, to be cited.
- **Yanasse (1997b)** — Mathematical formulation, branch and bound, greedy heuristic. *European Journal of Operational Research*, 100(3), 454-463. Note: this is *not* the paper that introduces the MOSP graph.
- **Yanasse (1997a) = "Yanasse (1997c)"** — A transformation for solving a pattern sequencing problem in the wood cut industry. *Pesquisa Operacional*, 17(1), 57-70. In `literature/` since 2026-09-27 (from the author); the venue question is settled. Proposition 5 is the MOSP graph (each pattern becomes a clique on its panel types; any MOSP reduces to the two-panel case with optima corresponding both ways), Proposition 3 the minimum-degree bound, Corollary 2 the clique bound, Proposition 1 the reversal symmetry, Proposition 2 the subinstance monotonicity behind `relaxation.py`.
- **Becceneri, Yanasse & Soma (2004)** — A method for solving the minimization of the maximum number of open stacks problem within a cutting process. *Computers & Operations Research*, 31(14), 2315-2332. In `literature/` since 2026-09-27. States the Minimal Cost Node heuristic in full — it is an **arc-traversal** heuristic (smallest remaining-degree node, then the cheapest incident arc, then every arc between open nodes), which is why the node-closing `mcn` in `satisfiability/heuristics.py` does not reproduce MCNh — the global dominance and equivalency propositions with proofs, the arc contraction bound as an O(n³) procedure, pattern dominance, and their branch-and-bound. Their verdict on their own bound: "quite poor" where C is small. See `literature/MISSING.md`.
- **Yanasse, Becceneri & Soma (1999)** — Arc contraction lower bound, which dominates all earlier bounds and is contraction degeneracy + 1. *Pesquisa Operacional*, 19(2), 249-277. In `literature/`.
- **Yanasse, Becceneri & Soma (1997)** — Lower bounds for the problem of sequencing cutting patterns, APORS'97. The 1999 bounds in earlier form; a candidate for the elusive "Yanasse (1997c)", though it carries no clique bound. In `literature/`.
- **Yanasse & Senne (2010)** — Review of MOSP properties and six pre-processing operations. *European Journal of Operational Research*, 203(3), 559-567.
- **Linhares & Yanasse (2002)** — Proved MOSP is NP-hard. *Computers & Operations Research*, 29, 1759-1772.
- **Chu & Stuckey (2009)** — Benchmark instances and exact solver via customer search with nogood recording. *CP 2009*, LNCS 5732, 242-257.
- **Frinhani et al. (2018)** — PageRank heuristic; published optimal values for Challenge/SCOOP instances using Chu & Stuckey's algorithm. *PLOS ONE*, 13(8), e0203076.
- **Martin, Yanasse & Pinto (2022)** — ILP/CP formulations; comparative benchmarks. *International Transactions in Operational Research*.
- **Faggioli & Bentivoglio (1998)** — Heuristic approaches and instance generation. *European Journal of Operational Research*, 110(3), 564-575.
- **Kirousis & Papadimitriou (1986)** — Graph searching and pathwidth connections. *Theoretical Computer Science*, 47, 205-218.
- **Fellows & Langston (1987)** — Nonconstructive advances in polynomial-time complexity. *Information Processing Letters*, 26, 157-162. In `literature/` since 2026-09-27. Lemma 4.1 is the column-expansion lemma (= Yanasse 1997a Proposition 5), Lemma 4.2 minor-closure of bounded layout cost, Lemma 4.3 the pathwidth branch construction with its proof.
- **Fellows & Langston (1989)** — FPT algorithms for pathwidth. *Proc. 21st ACM STOC*, 501-512. In `literature/` since 2026-09-27. **Theorem 7**: graphs of gate matrix layout cost k are exactly the graphs of pathwidth k − 1, proved in one direction (decomposition → layout, via column expansion and their 1987 Lemma 4.1); the converse is elementary from the consecutive-ones property. This is the link between open stacks and pathwidth that Linhares & Yanasse (2002) Table 1 rests on.

## Certified Optima vs Best Known Solutions

`solutions/` now holds two different kinds of result and **the files do not say
which**. A solution file carries `instance_name`, `n_customers`, `n_patterns`,
`mosp_value` and `ordering` — nothing about how the value was established. Since
both kinds are present, adding them into one total overstates what has been
proved.

- **Certified optimum**: satisfiable at `k` with a witness *and* unsatisfiable at
  `k-1`; or satisfiable at `k` where the lower bound already equals `k`, which
  needs no refutation.
- **Best known solution**: a witness of value `k` and nothing more. Produced by
  `benchmarks/ratchet.py`, which only ever asks satisfiable questions.

Both are equally checkable as *upper* bounds — the witness verifies either way
via `mosp/certify.py`. Only the first is an optimality claim.

### Recovering the split

Until a provenance field exists, the split is recoverable from other records:

1. Any instance appearing as `status=solved` in `benchmarks/results/sweep_*.csv`
   or `overnight_*round*.csv` was solved by the binary search, which certifies
   optimality by construction.
2. Any cached value equal to its `_lower_bound` is certified by the bound,
   whatever produced it.
3. Everything else is a best known solution with optimality unproven.

Measured on 2026-09-22 with 6,376 cached solutions (regenerate with `python -m benchmarks.corpus`), now read from the files
themselves rather than reconstructed:

**The corpus was re-opened on 2026-09-23 by a bug, not by a new instance.**
`better_move` could return a **false refutation** — it let the domination
relation cycle, so two candidates covered each other and were discarded
together with the solution they carried (`reports/better_move_bug.md`). Every
entry `benchmarks.csearch` certified with that rule was suspect: 55 of them.

| provenance | count |
|---|---|
| `certified:refutation` | 6,361 |
| `certified:bound` | 2 |
| `solution` (optimality open) | 13 |

**6,363 of 6,376 certified optimal; 13 open.** Re-verified with the fixed code
at `value - 1`: 41 of the 55 re-certify, 13 need hours per refutation and have
had their optimality claim **withdrawn** until they do, and **one was simply
wrong** — `Random-100-100-2-2_0`, certified at 21 when the true optimum is
**20**, now corrected and re-certified (`k = 19` refuted, `k = 20` satisfiable
with a witness that simulates to 20).

The 13 keep their values, which are still verified upper bounds; what is
withdrawn is the claim that they are optimal. They have no independent
certification: the direct SAT path and `csearch` have zero overlap in the
records, so nothing else ever proved them.

The last 27 — all 125×125 at density 2 or 4, the classes Chu & Stuckey (2009)
call hardest — fell in one 19.2-hour round on 25 cores under the configuration
their paper states ("better move", "old move" and nogood recording, no
relaxation). That is the configuration carrying the bug, which is why most of
the withdrawn 13 are from that round.

Re-verified after closing: all 6,376 witnesses re-simulate to their recorded
value, none sits below its independently recomputed lower bound, every file
matches an enumerated instance and every instance has a file. See the README's
*What Chu & Stuckey's paper does not settle* for what remains uncheckable
against the literature.

**Compute cost: about a day on 25 cores (667 core-hours)**, from `python -m
benchmarks.compute`, which totals the result CSVs and the ledger `csearch` and
`reheuristic` append to.

Quote it in that order -- rough days with the core count beside them, then
core-hours. The days are what a reader wants and are meaningless without the
cores, since the same work is a day on 25 cores and 27.8 days on one; the
core-hours are the invariant that compares between runs. Never maintain the
number by hand: it is regenerated, because several hand-carried figures in these
documents drifted before this existed. It counts only runs that wrote a row, so
it is a lower bound.

*(Updated 2026-09-18 after the customer-search sweep closed 111 of the 147 then
open: `reports/customer_search.md`. Every one of the 111 was re-verified by an
independent refutation, and all 6,376 witnesses re-simulate to their recorded
value.)*

There is one file per enumerated instance and no file that matches none, and as
of 2026-09-22 none of them is open.

The count of 6,376 is instances, not problems: the 46 `MOSP_Instances/Challenge`
files are the Miller, Shaw and Wilson files under a second name (certified twice),
and the corpus holds **3,667 distinct MOSP graphs**, 1,669 of them complete
(`reports/ml_nature.md` §1). Isomorphic instances carry equal optima everywhere.

That last property had to be restored. Four orphans — `GP1.json` through
`GP4.json` — were written by `validate_published_optima.py`, which overwrote
`inst.name` with the short key before saving, producing a filename
`from_benchmark_file` never generates. Matching no enumerated instance, they
were invisible to every sweep, so nothing could ever upgrade their provenance
and they sat permanently as uncertified duplicates of instances that were in
fact certified twice over under their real names. The files are deleted and the
script now carries the short key alongside the instance instead of over it.

### The provenance field — done

`_save_solution` records a `provenance` field: `certified:refutation`,
`certified:bound`, or `solution`. Existing files were backfilled using the two
recovery rules above. Saves are monotone in the value and never demote a
certified value to a bare solution, which matters because the ratchet re-derives
values earlier runs had proved — without that guard a night of re-solving would
quietly downgrade proofs to guesses.

This matters beyond bookkeeping: the corpus is intended as a published artifact,
and an artifact that cannot distinguish a proof from a good guess is a liability.

## Architecture

```
satisfiability/                 → SAT-based solvers (pathwidth + direct MOSP)
    encoding.py                     Position-based CNF encoding for pathwidth
    solver.py                       Pathwidth solver: preprocessing, iterative deepening, CaDiCaL
    mosp_encoding.py                Direct MOSP-to-SAT CNF encoding (no pathwidth reduction)
    mosp_solver.py                  Direct MOSP solver: bounds, iterative deepening, solution caching
                                    `solve_mosp_exact` is the entry point; default procedure is csearch
    heuristics.py                   Upper bound strategies behind one signature
    customer_search.py              Complete search over customer closing orders
    relaxation.py                   Contraction relaxation: certified lower bounds
    expansion_bound.py              Neighbourhood-expansion lower bound (not degree-based)
    race.py                         Portfolio: SAT and customer search on one decision call

customer_inter/                 → Customer intersection graph approach (customers as vertices)
    customer_graph.py               Build customer graph via M @ M^T overlap
    reduction.py                    MOSP ↔ customer-graph pathwidth reduction
    solver.py                       End-to-end pipeline using customer graph
    compare.py                      Side-by-side comparison of both approaches

mosp/                           → Agreement graph approach (patterns as vertices)
    instance.py                     Parse/represent MOSP instances (binary matrix)
    agreement_graph.py              Build MOSP graph via M^T @ M overlap
    reduction.py                    Formal reduction: MOSP ↔ pathwidth
    solver.py                       End-to-end pipeline: parse → graph → pathwidth → ordering
    verify.py                       Simulate production sequence to count open stacks
    certify.py                      Independent verification of a witness ordering
    preprocess.py                   Pattern dominance, decomposition, edge contraction

fixed_parameter_algorithm/      → Pathwidth solvers (exact DP and branch-and-bound)
    pathwidth.py                    Exact DP over vertex subsets (n ≤ 18)
    pathwidth_fpt.py                Branch-and-bound with iterative deepening (n ≤ 100+)
    path_decomposition.py           Extract path decomposition from ordering

benchmarks/
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output
    solve_all.py                    Batch solver for published benchmark files
    solve_all_sat.py                Batch SAT solver for large benchmark instances
    solve_parallel.py               Parallel solving: across instances, and across k
    ratchet.py                      Descending satisfiable-call search
    overnight.py                    Escalating-budget driver for unattended runs
    solver_portfolio.py             Times every pysat backend on the hard calls
    portfolio.py                    Races several backends on one decision call
    reheuristic.py                  Re-runs an upper bound strategy over solved instances
    csearch.py                      Parallel descent with the complete customer search
    dedupe.py                       Shares solutions between identical instances

lean/
    MOSPFormalization/              Lean 4 proofs of the MOSP-pathwidth reduction
        LinearLayout.lean               Linear vertex orderings
        VertexSeparation.lean           Vertex separation number
        PathDecomposition.lean          Path decomposition structure
        Pathwidth.lean                  Pathwidth definitions
        LayoutToDecomposition.lean      Layout → decomposition construction
        DecompositionToLayout.lean      Decomposition → layout construction
        VSEquivPW.lean                  VS = PW proof (Kinnersley 1992)
        MOSPInstance.lean               MOSP instance formalization
        OpenStacks.lean                 Open stacks counting
        Reduction.lean                  MOSP ↔ pathwidth reduction proof
        Examples.lean                   Verified example instances
        Sandwich.lean                   degeneracy ≤ pathwidth ≤ bandwidth, proved (2026-09-26)
        ForMathlib/                     Candidates for Mathlib contribution

learning/                       → ML over the certified corpus (instance → optimum)
    features.py                     Instance features: matrix, MOSP graph, bounds
    dataset.py                      Joins instances with solutions into one table
    study_optimum.py                Can the optimum be predicted, and better than the bounds?
    policy.py                       Closing-order policy imitating the certified witnesses
    corpus_sweep.py                 Scores a strategy against all 6,376 known optima
    guided_search.py                Learned branching inside the complete search
    descent_bench.py                Does a better starting bound certify faster?
    canonical.py                    Isomorphism classes: nauty certificates, WL hashes, |Aut(G)|
    fingerprint.py                  Generator classifier, size-free features, instance-space map
    node_counts.py                  Refutes optimum − 1 at n ≤ 40 under both configs, records nodes
    invariants_study.py             Pathwidth-adjacent invariants as features, ablation
    formula_search.py               Enumerated + PySR symbolic regression for optimum and residual
    bound_gap.py                    Where the proved bounds fail; the treewidth ceiling
    distil.py                       Distils the closing policy into readable rules
    degeneracy.py                   Exact counts of optimal orderings by lattice path counting (n ≤ 15)
    ensemble.py                     Generated G(n, m, p) campaign: solve, refute, feature, certify (n ≤ 40)
    hardness_map.py                 Nodes against density per size: the phase transition
    concentration.py                Variance of the optimum per cell; E[opt](n, m, p)
    graph_story.py                  Same graph, different clique covers: is hardness a graph property?
    scale_test.py                   The n ≤ 40 laws against the Chu & Stuckey corpus at 30–125
    upward.py                       The campaign at 50–75 across the sweep, 100 on the ridge
    differential.py                 Soundness harness: relabellings and re-coverings must agree on the answer
    proofs.py                       DRAT refutations of optimum − 1 through the SAT path, checked by drat-trim
    relabel_portfolio.py            Min-of-k relabellings as a speed-up (it is not, for refutations)
    cost_model.py                   Censored regression: log nodes from label-free graph features
    fan_order.py                    Cheapest-first fan by remaining degree vs index, paired in nodes
    theorem2.py                     Where Theorem 2 should be on: nodes vs seconds
    extremal.py                     Bit-flip search for extremal small instances, exact solver as oracle
    treewidth.py                    Exact treewidth: subset DP to 26, decision search to 64
    conjecture.py                   Conjecture mining with a validity oracle over every certified instance
    set_imitation.py                Imitation with the optimal-move set as label
    ridge_theory.py                 The ridge as one parameter across m / n
    sandwich.py                     Pins the Lean definitions to the corpus implementations; sorry inventory
    pwtw_exhaust.py                 Census of every graph on ≤ 11 vertices: pathwidth against treewidth

solutions/                      → Cached SAT solver solutions (JSON)

reports/                        → Analysis documents
tools/drat-trim/                → DRAT proof checker, built from source (loop0003 item 03)
tests/                          → 1,051 tests across 55 test modules
literature/                     → Reference papers (PDFs)
Ralph_Loops/                    → Unattended one-item-per-session drivers (loop0001–loop0003 done)
```

## Two Graph Formulations

### Agreement Graph (`mosp/solver.py`)

Nodes = patterns, edges between patterns sharing a customer (`M^T @ M`). Pathwidth gives a **lower bound** on MOSP but can undercount on some instances.

### Customer Intersection Graph (`customer_inter/solver.py`)

Nodes = customers, edges between customers sharing a pattern (`M @ M^T`). Pathwidth(G_c) + 1 gives an **upper bound** on MOSP. Matches published optimal values on dense instances (GP1-4, GP6-8) but overcounts on sparse instances (SP2-4, GP5).

The overcounting arises because the customer-to-pattern ordering derivation (sort patterns by earliest/latest customer position) is not guaranteed to produce an optimal MOSP ordering, even when the customer ordering achieves optimal pathwidth.

## Pathwidth Computation

### Exact DP (n ≤ 18)

O(2^n · n²) Held-Karp style subset DP with bitmask adjacency. Guaranteed optimal. Used automatically for small graphs.

### Branch-and-Bound (n ≤ 100+)

For larger graphs with small pathwidth k. The algorithm:
1. **Preprocesses**: removes degree-1 (pendant) vertices iteratively, decomposes into connected components
2. **Bounds**: greedy heuristic upper bound, max-clique lower bound (pathwidth ≥ ω(G) - 1)
3. **Iterative deepening**: tests pathwidth ≤ k for k = lower..upper
4. **Decision procedure**: DFS backtracking building orderings left-to-right, pruning when vertex separation exceeds k
5. **Memoization**: bitmask cache for n ≤ 30; pruning-only for larger graphs
6. **Vertex selection**: prioritizes active suffix vertices (already "open") sorted by remaining neighbor count

Note: despite the filename `pathwidth_fpt.py`, this is not a true FPT algorithm. It is branch-and-bound that works well when pathwidth is small, but has no proven f(k) · poly(n) guarantee. The theoretical FPT algorithm (Bodlaender-Kloks, 2^(32k³) · n) has constants too large for practical use. See `reports/fpt_theory_practice_gap.md`.

`compute_pathwidth_fpt()` delegates to exact DP for n ≤ 18. The threshold was lowered from 25 to 18 because branch-and-bound is faster than DP for n=19-25 when pathwidth is small (test suite: 114s → 5s).

### SAT Solver (n ≤ 125)

For large instances where branch-and-bound times out, a SAT-based solver encodes the pathwidth decision problem ("is pathwidth ≤ k?") as a CNF formula and solves it with CaDiCaL. This is the most powerful pathwidth solver in the project, handling instances up to 125 vertices.

**Encoding** (position-based formulation):
- Variables: `x[v,t]` (vertex v at position t), `y[v,t]` (vertex v placed by step t), `s[v,t]` (vertex v separated at step t)
- Permutation constraints via at-least-one + ladder at-most-one
- Prefix linking: `x→y`, monotonicity, converse
- Separation: if a neighbor is placed but v is not, v is separated
- Width bound: totalizer cardinality constraint (at most k separated per step)
- Symmetry breaking: fix vertex 0 at position 0

**Performance** (with 300s timeout, customer intersection graph):
- 40×40: 100% solved, avg 5s
- 50×50: 100% solved, avg 8s
- 75×75: 100% solved, avg 37s
- 100×100: 92% solved, avg 140s (2 of 25 Chu & Stuckey timeout)
- 100×50: 100% solved, avg 84s
- 50×100: 100% solved, avg 11s
- 125×125: 28% solved (only density-2 and 2 density-4; density ≥ 4 mostly timeout)
- **Overall: 200 of 220 instances solved that were previously out of reach for the branch-and-bound solver (91%)**

**Important**: These pathwidth values are provably correct, but the derived MOSP values (pathwidth + 1) are upper bounds that may overcount on sparse instances. See "Critical Finding" above.

`compute_pathwidth_sat()` is a drop-in replacement for `compute_pathwidth_fpt()` with the same interface. It reuses the same preprocessing (pendant removal, component decomposition) and bounds (greedy upper, clique lower).

**Known bug**: The pathwidth SAT encoding (`encoding.py`) has a variable ID collision bug in `pool.occupy()` / `top_id` tracking. CardEnc auxiliary variables from different constraints share the same IDs, making the encoding unsound. The solver still returns correct results because: (1) n ≤ 18 delegates to exact DP, (2) n > 18 falls back to greedy ordering when SAT returns UNSAT. This bug is fixed in the direct MOSP encoding (`mosp_encoding.py`) which properly tracks auxiliary variable IDs.

### Direct MOSP-to-SAT Solver (`satisfiability/mosp_solver.py`)

Encodes the MOSP decision problem directly as SAT, bypassing the pathwidth reduction entirely. This produces **exact optimal MOSP values** — validated against all published optima (GP1-8, SP2-4).

**Encoding** (position-based formulation):
- Variables: `x[p,t]` (pattern p at position t), `y[p,t]` (pattern p placed by step t), `o[c,t]` (customer c's stack open at step t)
- Permutation constraints via at-least-one + ladder at-most-one
- Prefix linking: `x→y`, monotonicity, converse (including t=0 base case)
- Open stack forcing: (a) placement clause `x[p,t] → o[c,t]` for each pattern p of customer c; (b) auxiliary `any[c,t]`/`all[c,t]` at `2|P_c|+1` clauses per (customer, step). The pair-wise form `y[p,t] ∧ ¬y[q,t] → o[c,t]` costs `|P_c|(|P_c|-1)` and is retained behind `pairwise_open_stacks=True` for equivalence testing only — it encoded GP5 to 76.7M clauses against 3.25M now
- Width bound: totalizer cardinality constraint (at most k open stacks per step)
- Symmetry breaking: pattern with most customers in first ⌊m/2⌋+1 positions

**Solution caching**: Results are saved as JSON files in `solutions/`. On subsequent runs, cached solutions are loaded and verified by simulation instead of re-solving. Disable with `solutions_dir=None`.

**Bounds for iterative deepening**:
- Lower bound: `_lower_bound` — trivial, clique and contraction degeneracy, best of the three (see the bounds section above)
- Upper bound: a named strategy from `satisfiability/heuristics.py`, defaulting to `mcn+tabu`; `cs-dfs` is usually stronger and far faster

## Design Decisions

**Two graph formulations.** The agreement graph (patterns as vertices) and customer intersection graph (customers as vertices) provide complementary bounds. Neither yields exact MOSP on all instances: agreement undercounts, customer overcounts. The Lean formalization proves agreement graph properties.

**Direct MOSP-to-SAT solver.** Encodes MOSP directly without the pathwidth reduction. Produces exact optimal values validated against all published benchmarks. The placement + pair-wise open-stack forcing captures the full open/close semantics correctly.

**The default decision procedure is the customer search, not SAT** *(changed
2026-09-22)*. `solve_mosp_exact` runs `satisfiability.customer_search`; the SAT
encoding is `procedure="sat"`. Raced head to head, the customer search won 63 of
63 decision calls on hard `Random` instances at densities 2 and 8 with SAT on
kissat404, and 49 of 49 on a broad corpus sample — where it certified 39 of 40
instances in 1.1 s against SAT's 36 in 30.3 s, a factor of 38 on the instances
both settle. The belief that the
two fail on disjoint instance sets was never measured: the direct SAT path has
solved rows for 6,226 instances, `csearch` for 147, and the overlap is zero.
`reports/learned_search.md` §3.

Keep reaching for SAT when a **checkable proof object** matters. A refutation
from the customer search rests on the dominance rules being sound, with no CNF
to re-refute and no proof log, which is the open item 7 in Next Steps.

**Three-tier pathwidth solver.** Exact DP for n ≤ 18 (fastest, no overhead). Branch-and-bound for n ≤ 100+ when pathwidth is small. SAT solver for large instances (n ≤ 125) where branch-and-bound times out — handles high pathwidth that defeats backtracking search.

**Verify by simulation, not formula alone.** Both solvers compute the ordering from pathwidth but determine the actual MOSP value by simulating the production sequence on the original instance.

**Customer ordering to pattern ordering.** Given a customer ordering, each pattern is assigned priority (first_customer_position, last_customer_position) and sorted. This heuristic is not guaranteed to produce an optimal MOSP ordering even from an optimal pathwidth ordering.

**Convention: rows = customers, columns = patterns.** The binary matrix M[i][j] = 1 means customer i requires pattern/product j. This matches the standard MOSP file format.

**Bitmask adjacency.** Both pathwidth solvers represent graph adjacency as Python ints with bitwise operations, making neighbor queries O(1).

## File Format

Standard MOSP instance files (`.mosp`):
```
instance_name
n_customers n_patterns
<n_customers rows of n_patterns space-separated 0/1 values>
```

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Solve via customer intersection graph + branch-and-bound (small/medium instances)
# NOTE: gives upper bound, may overcount on sparse instances
python -c "
from mosp.instance import MOSPInstance
from customer_inter.solver import solve_mosp
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
sol = solve_mosp(instance)
print(f'Upper bound: {sol.max_open_stacks}, Ordering: {sol.ordering}')
"

# Solve MOSP exactly (recommended) — the complete customer search by default
python -c "
from mosp.instance import MOSPInstance
from satisfiability import solve_mosp_exact
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
val, ordering = solve_mosp_exact(instance)
print(f'Optimal MOSP: {val}, Ordering: {ordering}')
"

# The same through the SAT encoding, which is what to use when a checkable
# proof object matters — a customer-search refutation is not a DRAT proof
python -c "
from mosp.instance import MOSPInstance
from satisfiability import solve_mosp_exact
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
print(solve_mosp_exact(instance, procedure='sat'))
"

# Solve large instances with SAT solver (upper bounds via pathwidth reduction)
python -m benchmarks.solve_all_sat --timeout 300

# Compare both approaches on SCOOP benchmarks
python -m customer_inter.compare

# Run all published benchmarks with timeout
python -m benchmarks.solve_all --timeout 120
```

## Known Limitations

- **The SAT path does not close dense 125×125 instances.** The ~50×50 ceiling recorded here previously was lifted by the linear open-stack encoding; the corpus now holds certified optima at 125×125. What remains is that SAT *refutations* on the dense Chu & Stuckey instances do not return, which is what `satisfiability/customer_search.py` exists for.
- **A dominance rule implemented only in the C had no test and was wrong.**
  `better_move` returned false refutations; `tests/test_native.py` compares the
  C against the Python and `better_move` has no Python side, so nothing checked
  it. One corpus value was certified a stack too high and 13 more had their
  optimality withdrawn (`reports/better_move_bug.md`). The general lesson: a
  rule that exists on one side only needs its own invariant, and here it is one
  line — *a dominance rule may change the cost of a search, never its answer.*
  **It happened again on 2026-09-26** (`reports/ml_nature.md` §15,
  `reports/better_move_bug.md` §7): the differential harness found the C
  `better_move` answering `unsat` at the *optimum* on 56 of 17,527 sparse
  instances at 10–40 customers — a wrong close count inside the rule, a
  cross-rule cycle with `subset_rule`, and an early exit that had hidden both
  from the "rule alone" control. Fixed in `0eb33915`: rules now run
  `definite_move → subset_rule → better_move` and cite only standing
  candidates; the harness reports zero disagreements on 878,700 runs, the
  `default` configuration's counts are unchanged to the node, and the fixed
  rule prunes less — +7.3% nodes at n ≤ 40, ×2–3.5 on the 100-customer
  half-ratio classes, **≥ 15× on `Random-100-100-2-4_0`**. Every `csearch`
  count recorded before 2026-09-26 12:19, including the five 125×125
  recertify counts, is a pre-fix number. The invariant test now draws its
  instances at 1–3 products per customer, where the failures live.
- **Nothing checks that a refutation is sound.** Witness verification, the
  corpus audit and the lower-bound guards all confirm a value is *achievable*.
  A refutation one step too strong is invisible to every one of them, which is
  how the above survived. Item 7's proof objects are the real fix. *Partly
  addressed at small sizes, 2026-09-25:* `learning.degeneracy` computes the
  optimum by path counting over the subset lattice, sharing no code with the
  search, and agrees with the certified value on all 2,812 instances at n ≤ 15;
  `learning.node_counts` re-refutes `optimum − 1` on all 6,135 at n ≤ 40 under
  two search configurations. Neither reaches the sizes where the two known
  false refutations were. *Further, 2026-09-26:* `learning.differential` runs
  every certified instance at n ≤ 40 (corpus and 37,800 generated) on ten
  labellings under both configurations at `optimum − 1` *and* `optimum` — the
  satisfiable side is where an over-strong rule shows — with zero
  disagreements after the fix; and `learning.proofs` gives 5,646 of the 6,135
  corpus instances at n ≤ 40 (92.0%) a DRAT refutation drat-trim verifies.
  Above 40 the only checks are two-configuration and relabelling agreement.
- **The customer search produces no checkable proof object**, and it is now the
  default, which makes this limitation apply by default too.   Its refutations rest on the dominance rules being sound, cross-validated heavily but with no CNF to re-refute and no proof log. It now accounts for a large share of the certified corpus.
  *Partly closed at n ≤ 40 (2026-09-26, §17)*: the SAT path with proof logging
  re-refutes 92.0% of those instances with a checked DRAT proof (11.2
  core-hours, 11.7 GB compressed under git-ignored `learning/data/proofs/`);
  the boundary is `m² · k ≈ 10⁴`, not `n`, so the direct encoding has no proof
  to offer at 125×125 at any width. The certificate replaces trust in CaDiCaL
  and in the dominance rules, not in the encoding.
- **Pathwidth reduction is not tight**: `pathwidth(G_c) + 1` overcounts MOSP on sparse instances (validated on GP5, SP2-4). Use `solve_mosp_sat()` for exact results.
- **Agreement graph undercounts**: `pathwidth(G_a) + 1` gives a lower bound that can be too low.
- **Pathwidth SAT encoding has a variable ID collision bug**: The `encoding.py` pool.occupy/top_id tracking is broken (CardEnc auxiliary variables collide across constraints). The solver works because it falls back to greedy. Fixed in `mosp_encoding.py`.
- **SAT solver ceiling around n = 125**: The pathwidth position-based encoding produces O(n²) variables and O(n² · degree) clauses. Instances with 125 vertices and density ≥ 4 (pathwidth ≥ 50) exceed 300s.
- **Exact DP ceiling at n = 18**: The subset DP uses O(2^n) space/time.
- **Branch-and-bound depends on pathwidth**: Handles n = 100+ when k ≤ 5, but slows down for moderate pathwidth (k ≥ 10) on large graphs.

## Next Steps

Sequenced by `reports/chu_stuckey_plan.md` §7, which supersedes the earlier list
here. Items 1, 3 and 6 are done (2026-09-18).

**Done, with reports:**
- **Item 2**, the dominance rules — built into a *complete* customer search
  rather than the heuristic, because their Table 1 shows the complete search
  closing the dense instances in seconds. It refutes, so it certifies optima
  with no SAT solver. `satisfiability/customer_search.py`,
  `reports/customer_search.md`.
- **Item 5**, contraction relaxation. `prove` closes nothing — it can only
  succeed when the upper bound is already optimal — but partial relaxation
  lifts SP4's certified lower bound from 27 to 45.
  `satisfiability/relaxation.py`, `reports/relaxation.md`.
- **Item 1**, `ub_MOSP` restricted DFS — `satisfiability/heuristics.py`, strategy
  `cs-dfs`. Improved 25 of the 148 unproven instances in 3 seconds, on top of
  what two hours of seeded tabu had already taken. `reports/ub_mosp_search.md`.
- **Item 3**, contract + column dedupe, with the formula shrink measured. The
  finding is that item 5 does **not** need item 4 first, and that item 4's
  remaining argument is weaker than it looked.
  `reports/preprocessing_measurements.md`.
- **Item 6**, component decomposition and pattern dominance —
  `mosp/preprocess.py`, applied on every SAT call through
  `satisfiability.mosp_solver.decide_mosp`.

**Next, in order:**
- **Item 7**: the end-to-end certificate chain — contraction sequence, DRAT
  refutation, witness ordering, each checkable by a third party without
  trusting our code. This is the publishable claim, and the customer search
  changes what it has to cover: a refutation from `customer_search` is not a
  DRAT proof, so either the refuted instances are re-refuted through SAT for
  their certificates, or the search's own proof object has to be defined.
  *Status 2026-09-26*: re-refuted through SAT with checked DRAT proofs for
  92.0% of the corpus at n ≤ 40 (`reports/ml_nature.md` §17); the gap left is
  the encoding's correctness in Lean (`Encoding.lean` exists) and everything
  above the `m² · k ≈ 10⁴` boundary.
- ~~**A portfolio decision procedure.**~~ **Built and measured 2026-09-22 —
  `satisfiability/race.py`, `reports/learned_search.md` §3. It does not pay, and
  the premise was wrong.** Over 20 hard `Random` instances at densities 2 and 8,
  with SAT on `kissat404`, the customer search won **63 of 63** decision calls
  and SAT certified none; the race costs 4% to arrive where `csearch` alone
  would. The claim that the two "fail on disjoint sets" was never measured: the
  direct SAT path has solved rows for 6,226 instances, `csearch` for 147, and
  **the overlap is zero** — `csearch` was only ever pointed at what SAT had
  already failed. The corollary is actionable: **the SAT path is the wrong
  default for hard instances**, and `benchmarks.solve_parallel` / `csearch`
  should swap roles.
- **Learning does not help certification, only bounds** —
  `reports/learned_search.md`. Learned branching inside `decide` is neutral
  except on sparse satisfiable calls (-60% nodes, but a tail that turns 65 nodes
  into a timeout, so not ported to C); a learned starting bound does not speed
  the descent, because its cost is the refutation both configurations must do.
  The gains in `reports/learning.md` are bound *quality*, which is not what the
  hard instances are short of. The `decide` `branch` hook is proved
  order-insensitive in `tests/test_learning.py`.
- **Old move on large sparse instances.** It prunes 27% more nodes than the memo
  on SP3 and still loses on the clock. Its advantage is in nodes, so it should
  win exactly where the memo degrades, which is where we are now stuck. Not yet
  measured there.
- **Item 4** (customer-order encoding) is no longer a prerequisite for anything.
  The customer search now covers the space that encoding was meant to reach,
  without a SAT solver. Keep the kill criterion if it is ever built.

**Profiling the C inner loop** (`reports/inner_loop.md`): the dominance rules
*are* the inner loop — the base search is 0.258 µs of 0.688, and `old_move`
alone is 42%. Merging three O(R) passes into one gained 1.05×. A flag sweep on
*dense* instances suggested the memo was a 15-18% net loss; calibrating on
*sparse* instances with `better_move` on showed it saving 3-7× the nodes
instead. **The default was not changed, and that near-miss is the lesson**: the
value of a rule depends on the instance shape and on which other rules run
beside it.

**The expansion argument, tried twice and rejected twice** (`reports/expansion_bound.md`):
as a root-level floor it is off by default — it changes the search by 2 seconds
out of 7,629 and doubles the wall clock (§6). As a *per-node* cut inside
`decide` (`expansion_prune=True`, also off) it cuts 0.0% of nodes on sparse
instances and 0.5% on dense, for 7-10% more time (§7). The binding constraint
there is not the bound's strength but that **Chu & Stuckey's dominance rules
have already collapsed the node** before it is consulted. Hard refutations visit
274-627M nodes at **0.65 µs each**, so what is worth attacking is the cost per
node, not the node count.

**The learning plan, revised** (`reports/learning_plan.md`, 2026-09-24).
`corpus → model → better answers → better solver` is measured false at the last
link, three ways. What the work has actually produced every time is a **finding
about the solver** rather than a component of it: the clique bound never helps,
structure predicts the optimum better than our proved bound does, the SAT
default was backwards, and a performance experiment found a false-refutation
bug the verification machinery was structurally blind to. The plan is now
measurement-shaped, and asks four questions in order:

1. **which configuration to run** — the selector deciding a 28× choice is one
   hand-picked threshold on one statistic, and a wrong answer costs time, never
   correctness;
2. **how long an instance will take** — five-day budgets are being allocated
   blind;
3. **where two sound configurations are most likely to disagree** — the only
   tool that can see an unsound refutation, and it has already found one;
4. **what the optimum is where certification is out of reach** — with
   calibrated uncertainty, labelled as prediction every time.

Closed, do not rebuild: learned upper bounds, learned lower bounds, learned
branching. Each has a report explaining the mechanism, not just the outcome.

**From the learning folder** (`reports/learning.md`, 2026-09-22):
- **`learned+cs-dfs` is registered, and better than `cs-dfs` on 709 instances
  against 13 worse.** Swept over all 6,376 fold by fold, each instance scored by
  a model blind to its own source file: mean overshoot 0.241 → 0.105, exact
  84.5% → 93.3%, total overshoot 1,538 → 670 stacks. It recovers 571 of the 988
  optima `cs-dfs` misses, and it is *faster* — 11.6 ms against 19.3 ms per
  instance, because a better incumbent prunes more than the policy costs. The
  policy imitates the 2.27M closing decisions the certified witnesses contain.
  Registered behind a soft import and **not** the default for anything: that
  would put LightGBM on the solver's critical path, a dependency decision left
  open. The 13 regressions are all off by one and are the `_cs_cost` proxy
  mismatch its own docstring predicts. **Superseded 2026-09-25** by the
  two-key rule of `reports/ml_nature.md` §7, which seeds the DFS better than the
  ranker (held out 0.127 / 92.7% vs 0.157 / 91.0%) with no model; the
  measurement that would close the dependency question is `learning.corpus_sweep`
  with the rule seeding `restricted_dfs`, against the 709 / 13 figure above.
- **`benchmarks.reheuristic` can no longer improve anything** — the corpus is
  closed, so `--all` is a scoring run rather than an improvement run, and
  `learning.corpus_sweep` wraps it with held-out models. Scoring sweeps write to
  their own ledger: they are not compute the corpus cost.
- **The clique bound never improved on contraction degeneracy + 1** anywhere in
  the corpus, under a 1-second budget. `_lower_bound` spends up to 5 seconds per
  call on it. A measurement, not a theorem — and the clique bound is the one
  provable without Yanasse's pathwidth equality — but the budget is worth
  revisiting.

**What the corpus says about the problem itself** (`reports/ml_nature.md`,
Ralph loop0001, 2026-09-25, executing `reports/ml_nature_plan.md`). Eight
studies, each with a regenerate command and a stated size range. Every number
below covers 9–134 customers with 5,938 of 6,376 instances at n ≤ 30, unless it
says otherwise; nothing in it is a bound or a solver change.

- **The corpus is 3,667 distinct MOSP graphs, not 6,376 instances** (§1).
  42.5% is isomorphic copies; 26.2% are complete graphs with optimum `n`, all
  Harvey and Simonis. **157 graph classes span more than one file, so grouping
  by `source_file` leaks isomorphic copies across the split**; the honest split
  is `learning.fingerprint.union_groups` (file ∪ class), which is a five-region
  hold-out in practice (largest group 1,620 instances). Certificates in
  `learning/data/canonical.csv`.
- **The generators are fingerprintable at 94.4% from structure alone**, 98.8%
  at equal size (§2). Harvey is a regularity constraint (constant row or
  column sums, in all 2,130 and in no other generator); Faggioli–Bentivoglio
  caps the largest product at half the customers; Chu & Stuckey is sparse
  where nothing else is, and its density class `d` is `col_mean` to within
  rounding. Instance space is a lattice of 74 `(n, m)` cells with empty
  regions between, and the 24 SCOOP industrial instances fall in the sparse
  corner with all 200 Chu & Stuckey. A result on one collection is a result
  about that generator.
- **Node counts are in the ledger** (§3): `solve_mosp_exact(..., stats=dict)`
  fills `nodes`, `benchmarks/results/compute_ledger.csv` has a `nodes` column,
  written by `csearch` and `recertify`. 38.5% of refutations at n ≤ 40 visit
  zero nodes; the p90 grows about 10× per ten customers; over the Random-30/40
  instances median nodes fall monotonically with density (1,068 → 6 from
  density 2 to 10), so any hardness peak sits at or below density 2 there.
- **Min-fill treewidth is the best point estimate of the optimum we have**
  (§4): `tw_min_fill + 1` is exact on 85.7% at MAE 0.188 against 84.6% / 0.239
  for `ub_best` and 77.0% / 0.431 for `lb_best`, leading in every size band.
  It is a bound on nothing (below on 481, above on 428). The 13 invariants
  add nothing to the *residual* over the bound (−0.004 MAE): they know what
  the bound knows, expressed differently. `bw_rcm + 1 ≥ optimum` on all 6,376.
  *It stops being the best estimate above about 50 customers*: on the Chu &
  Stuckey classes its error is 1.3 stacks at 75 and +4.2 at 125 (§14).
- **No clean formula for the residual; a clean sandwich for the optimum** (§5).
  The best residual formula is `0.01 · (σ_deg / μ_deg) · (n − 1) · sep_size`,
  MAE 0.303 against 0.431 for zero and 0.260 for boosting: degree dispersion
  is the variable, and no conjecture is stated. For the optimum both searches
  converge on `1 + √(degeneracy · bw_rcm)` with constants exactly (1, 1):
  `degeneracy + 1 ≤ optimum ≤ bw_rcm + 1` holds on all 6,376 (two theorems,
  checked), the ends coincide and force the optimum on 2,823, and elsewhere
  the optimum sits at their midpoint on median (IQR ⅓–⅔) in every size band,
  its position tracking sparsity, not size. `degeneracy + 1` is dominated by
  contraction degeneracy, so nothing goes to the bound work. *The midpoint is
  a pooled artifact*: on the generated ensembles the position runs from 0
  below 1.5 customers per product to ⅔ above 6 (§12).
- **Where the bound fails is structural, not statistical** (§6): gap ≥ 2 never
  occurs below 20 customers, is 338 instances (5.3%) and 51% of Chu & Stuckey,
  and on 131 of the 338 pathwidth provably exceeds treewidth (see the bounds
  section). A depth-3 tree at fixed `(n, m)` reads "connected and sparse, or
  dense with a low-degree customer" at AUC 0.931 against 0.849 for density and
  size; the lower bounds themselves add nothing to the classifier.
- **The imitation ranker resolves into a one-sentence rule** (§7): *close the
  customer that opens the fewest new stacks; on ties, the one with the most
  unclosed neighbours.* Held out: MAE 0.348, exact 80.7%, worst +9 against the
  LightGBM ranker's 0.519 / 75.0% / +34 and MCN's 1.616 / 50.2% / +26; better
  than the ranker on 253 instances and worse on 109, in every band and every
  collection but Shaw; on the 91 Chu & Stuckey held out, 2.42 vs 3.35 vs 9.44.
  The first key is `restricted_dfs`'s own cheapest-first fan order, so the
  greedy is that search's first leaf; the tie-break is the *reverse* of MCN's
  minimum degree. Fiedler order keeps 66% of the gain with no state at all;
  BFS from a min-degree root does not. Distilled trees and scorers keep less
  (57%, 82%) because imitation is the wrong objective. **Not registered in
  `satisfiability/heuristics.py`**: a solver change, left to the owner.
- **The optimum is never unique** (§8, n ≤ 15 only): 0 of 2,812 corpus
  instances have a unique optimal closing order even up to twins, 0 of 2,138 a
  unique product order up to reversal; medians 4 × 10⁵ optimal closing orders
  at n = 10 and 2.5 × 10¹⁰ at n = 15. The share tracks `optimum / n` (ρ 0.70)
  and not the bound gap (0.02). A policy optimal at every step but indifferent
  among optimal moves agrees with the stored witness on only ~30% of steps, and
  every policy measured sits far above that, so **step agreement above 0.3
  measures reproduction of the solver's tie-breaks, not optimality**; the
  2.27 M decisions `learning/policy.py` trains on are ~90% arbitrary choices
  among optimal ones. Any future imitation must be set-valued
  (`learning.degeneracy.optimal_choices`) or score construction value only.

Two audits came free and both passed: isomorphic instances carry equal optima
(§1); the lattice minimum equals the certified optimum on every instance at
n ≤ 15 and `optimum − 1` re-refutes on every instance at n ≤ 40 under two
configurations (§3, §8). Nothing was re-certified because nothing disagreed.

**Kill criteria.** §2.2's (no invariant moves grouped MAE by more than 0.02)
is **met against the plan's stated baseline**, the 36-feature model by file
(−0.012), and cleared ten times over against structure alone (−0.216); the
section reports both. §2.3's (structure cannot beat density and size) and
§2.6's (no readable rule keeps half the ranker's gain) are **not met**, the
latter exceeded at 115%. §2.1, §2.2b and §2.6b carry no kill criterion. §2.4,
§2.5, §2.8 and §2.9 are the campaign below.

**Method notes that each cost a session**: a label column swept into a
feature set by an every-numeric-column selector scored 1.000 everywhere (the
guard is `learning.bound_gap.feature_sets`; build feature sets from group
names, never from every numeric column); forking a worker pool after LightGBM
has run deadlocks in libgomp (`spawn` with an initializer); PySR crashes Julia
at 16 threads and 10,000 iterations, and runs at 4 and 2,000; a bare
`pkill -f <word>` killed a session's own shell; `pandas` reads 15! from CSV
one ulp short, so round before dividing by `aut_order`. The generated
witnesses of §8 live in `learning/data/degeneracy_solutions/`, which is
git-ignored: persisted on disk, not in the repository.

**The generated-ensemble campaign** (`reports/ml_nature.md` §9–§14, Ralph
loop0002, 2026-09-26, six items in 2 h 11 min). The corpus is a lattice of
size cells with generator fingerprints, so the questions about density had to
be asked on ensembles we control: 37,800 instances in 252 cells, `n` from 10
to 40, `m ∈ {n, 2n}`, both generators (Bernoulli `p` and Chu & Stuckey's fixed
customers per product `d`), 150 per cell, every one certified, refuted at
`optimum − 1` under both search configurations, featured and canonicalised,
in 2.16 core-hours. The artifact is committed under `learning/data/ensemble/`
(manifest, results, witnesses; instances regenerate byte for byte from their
seeds; 49 MB). Density means *realised* customers per product (`col_mean`)
throughout: Chu & Stuckey's "density 2" is 2.7–2.8 realised.

- **At n ≤ 40 the campaign is free and seconds do not see hardness** (§9,
  §10): the refutation is 0.7% of the cost, bounds and features are the rest;
  the hardest refutation in 37,800 took 0.04 s while node counts vary by three
  orders of magnitude across cells at fixed `n = 40`. 17% of the instances are
  complete graphs, 19% decompose (kept and recorded; Chu & Stuckey discard
  them), 28% are isomorphic repeats within their cell.
- **There is a phase transition in hardness** (§11, kill not met): at every
  `n` from 15 to 40, in both generators, median nodes to refute rise and fall
  with density by two orders of magnitude each side, the peak sharpens with
  `n`, and on the ridge the median doubles every 2.9–3.5 customers (power law
  ruled out at 5–10× the residual; off the ridge, every 4.5–4.9). The ridge
  sits at about three customers per product when `m = n`, two when `m = 2n`.
  **Chu & Stuckey's density-2 classes sit exactly on the ridge and their
  density 4 is its dense shoulder** — the one-picture reason those two classes
  take a day at 125×125. `reports/figures/hardness_map.png`.
- **The optimum concentrates** (§12, kill not met): CV under 0.2 in every cell
  at `n = 40` (median 0.031); the only cells above are Bernoulli cells at or
  below the giant-component threshold. `E[opt]` is a line in `n` at fixed
  degree (r² ≥ 0.999 in all 17 series) with slope a function of the nominal
  degree alone; the fitted formula `E[opt] ≈ 2.1(1 − q) + n[1 − √(1 − q)·27/(D + 27)]`,
  `q = 1 − (1 − p²)^m`, `D = (n − 1)q`, has held-out MAE 0.49 on cell means.
  **Not a bound** (below on 9,445 instances, above on 10,641).
- **The graph is the whole story for hardness** (§13, kill met): re-covering
  the same edge set with different cliques (15,900 re-coverings of 1,400
  instances) leaves the node count *exactly* unchanged in every pair — the
  search reads neighbour masks and nothing else, and the C and Python agree
  on all 15,900 — and graph-only features predict nodes as well as graph plus
  matrix. Two things move the count and neither is the cover: **relabelling
  the customers** (2–6% at the median, up to 2.3× default and 8× `csearch`;
  the search's tie-breaks, the floor for any label-free predictor), and the
  `csearch` rule that switches Theorem 2 on by a matrix statistic (10–13%,
  always in its favour; a design choice, not a property of the problem). The
  matrix does carry the number of optimal closing orders under the
  construction value, by up to three orders of magnitude, as §8 said.
- **At 125×125 the forms hold and the constants do not** (§14, kill met for
  every interval). Measured on the 200 Chu & Stuckey corpus instances, whose
  50–125 node counts this item computed (5.65 core-hours; `compute_ledger.csv`
  had the column and no values) and committed as `scale_nodes.csv`. The
  refutation grows exponentially in `n` at fixed density through 125 in every
  class (power law 3–5× worse), at rates the `n ≤ 40` cells overstate by
  0.005–0.018 per customer, a factor of 6–34 at 125 for densities 6–10 but
  **within a factor of 3 for the two day-long classes**: §11's pre-registered
  ridge law said 5 × 10¹¹ nodes at 125 and the recertify counts are 1.6–1.7 ×
  10¹¹, eight decades of extrapolation. The density-2 class stays 2–6× harder
  than density 4 at every size to 125 while its `optimum / n` falls from 0.29
  to 0.18, so the ridge's size-stable coordinate is customers per product, not
  `optimum / n`. `E[opt]` stays linear in `n` to 125 (r² ≥ 0.986) but with
  intercept 4–5 stacks where the formula has 2.2 and, at density 2, slope
  0.146 where it saturates at 0.22, so the formula's bias grows linearly to
  +8 at `Random-125-125-2` and stays within ±2 at densities 4–10. **Every 90%
  interval calibrated at n ≤ 40 fails by 50 or 75 and is not to be quoted at
  n ≥ 50**; the size at which each finding stops holding is tabulated in §14.
  Theorem 2 saves more at scale than at `n ≤ 40`: `csearch / default` nodes
  0.63 at `n = 100` and 0.17 on `Random-100-50-4`, never a cost.

**Kill criteria, the campaign.** §2.4 and §2.5 **not met** (a peak exists; the
optimum concentrates). §2.9 **met** (graph-only predicts nodes as well as the
full set, and the cover changes nothing). §2.8 **met** for both quantities and
every estimate: no interval from §11, §12 or §14 at `n ≥ 50`.

**Method notes from the campaign**: plot density as realised `col_mean`, not
nominal `p`, or the peak appears to drift; the recertify configuration equals
`csearch` on any instance with ≤ 5 products per customer, so its counts are
`csearch` observations and never `default` ones; a censored refutation is a
lower bound, not a missing value; a column-key collision silently overwrote
one law's column with another's in a first draft, caught by reading the table
against its summary.

**The objects loop** (`reports/ml_nature_plan_2.md`, Ralph loop0003,
2026-09-26, fourteen items in 11 h 20 min and 16 sessions; findings in
`reports/ml_nature.md` §15–§27; the synthesis, one paragraph per claim with
its status, is `reports/ml_nature_summary.md`, and `learning/README.md` is its
plain-English form). Two sessions ended their turn on a background wait and
had to be re-opened; nothing else stumbled.

- **Soundness** (§15): 1.76 M decision calls over 43,935 certified instances
  at 9–40 on ten labellings each: every refutation at `optimum − 1` held, and
  56 instances said `unsat` at the *optimum* — the `better_move` bug above,
  found only because the harness asked the satisfiable side. **Ask the
  satisfiable side**: an over-strong rule cannot be caught at `optimum − 1`
  when the stored value is right.
- **The campaign to 75** (§16): 6,747 more certified instances at 50–75 at
  all three product ratios; the exponential rate falls by 0.002 per customer
  per ten customers, which is the whole of §14's rate discrepancy; corrected,
  the ridge law from 75 predicts the two 125×125 ridge counts to 0.04
  decades. 100 on the ridge was priced at 40 core-hours and stopped at a
  5-per-cell sample.
- **DRAT proofs** (§17): 92.0% of the corpus at n ≤ 40, zero checker
  rejections, zero contradictions; the boundary is the formula size, not `n`.
- **Relabelling portfolio** (§18, kill met): min-of-16 beats the identity by
  1.00–1.02 on refutations and the spread shrinks with `n`; recommended
  against for `recertify`. It pays only on the witness side (8–13× where hard,
  under 5% of a descent). Seconds spread 1.5× where nodes spread 1.05× on a
  loaded machine — the clock would have passed the kill.
- **Cost model** (§19, kill not met): a censored linear model in `n` and
  label-free graph terms, trained at 10–75, puts 88–89% of the 100–125 counts
  within a decade (baselines 58–65%), biased upward ×2.5; usable to order a
  queue and size a budget, never for `k`. Recertify's open entries, cheapest
  first: `2-5_0`, `2-3_0`, `2-2_0`.
- **Fan order** (§20, kill met): 0.0% median node change on refutations at
  every size; keep index order in `decide`. Degree order saves 35% of witness
  nodes at 75 and is proposed for satisfiable-side drivers only.
- **Theorem 2's switch** (§22): always-on wins in nodes (−6.6%, never costs
  more than 1.2%) and loses in seconds (+5–8% on the dense half at 1.17× per
  node); **keep `sparse_enough_for_better_move` at 5**. Post-fix, where on, the
  rule saves 27% of refutation nodes in total.
- **Extremal search** (§21): the corpus's small instances are not extremal
  for any objective but soundness; the 10-vertex `pw − tw = 2` graph above;
  pathwidth exceeds treewidth on 48.5–76.3% of the gap instances.
- **Conjecture mining** (§24): closed against the honest reference
  `max(lb_best, tw + 1)`; two theorems and one worthless-but-surviving
  conjecture handed to Lean.
- **Set-valued imitation** (§23, kill met): with the exact optimal-move set
  as label and the rule's keys as features, the best policy beats the two-key
  rule by 0.008 MAE against a kill of 0.02. The rule's pick is already optimal
  at 99.7% of states. **Imitation is closed for good.**
- **The ridge** (§25): not a mean-degree condition; the parameter constant
  across every `m / n` is the cover excess `(n_ones − m) / n ≈ 2–2.4`, one
  independent cycle of the incidence graph per customer, which puts the ridge
  at about `1 + 2.4 n / m` customers per product. The giant-component
  threshold lies 1.5–6× below it.
- **Lean** (§26): both sandwich inequalities proved; `lake build` passes.
- **Census** (§27): `pw ≤ tw + 1` on every graph to 9 vertices, by
  enumeration of all 287,884.

**Kill criteria, this loop.** Met: relabelling portfolio (§18), fan order
(§20), set-valued imitation (§23), conjecture mining against the honest
reference (§24), the 100-customer ridge budget (§16). Not met: the DRAT path
is open (§17), the cost model is usable (§19). Overturned by the data: the
mean-degree ridge hypothesis (§25).

**Thirteen solver changes proposed and one applied**, each with the
measurement that decides it, in `reports/ml_nature_summary.md` §8. Applied:
the `better_move` fix. Recommended against: Theorem 2 always-on, a
refutation portfolio, degree fan order for `decide`. Still to decide: exact
treewidth in `_lower_bound`; the two-key rule as heuristic and DFS seed (one
`corpus_sweep` run settles it and the LightGBM question with it); degree fan
order and a portfolio on the satisfiable side. **Open and unpriced**: a sound
refutation check above 40 customers; Yanasse's equality and the encoding's
correctness in Lean; a pathwidth bound that sees separators of trees of
cliques.

**Unrelated to the plan:**
- Fix the pathwidth SAT encoding variable ID collision bug in `encoding.py`.
- ~~Becceneri, Yanasse & Soma (2004) is still missing~~ — **obtained 2026-09-27**,
  with Yanasse (1997a), both from the author. The MCNh our `mcn` does not
  reproduce is an arc-traversal heuristic (see Key References); reproducing it
  as a strategy in `satisfiability/heuristics.py` is a small, well-specified
  item. The global dominance proposition is proved there, and the authors
  report that using it inside their branch-and-bound made it slower — the
  same lesson as `reports/inner_loop.md`, that a rule's value depends on what
  runs beside it.
