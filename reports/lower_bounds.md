# Lower Bounds for MOSP: Clique and Contraction Degeneracy

**Status:** measured. Every figure below is reproducible from this repository;
§9 gives the commands. Sample sizes and dates are stated throughout.

---

## 1. Summary

The lower bound used by a branch-and-bound or binary-search MOSP solver is not a
tuning parameter. It decides which decision problems the solver poses, and the
expensive ones — refutations at values far below the optimum — are precisely
those a weak bound fails to rule out. In this solver the refutation at `k-1`
dominates runtime, so the bound determines how much of the budget is spent on
questions whose answers are already known.

This report evaluates three bounds on the MOSP graph:

| bound | mean gap to optimum | tight | max gap |
|---|---|---|---|
| trivial (max item types per pattern) | 5.58 | 1.2% | 19 |
| maximum clique | 2.02 | 36.9% | 13 |
| **contraction degeneracy (MMD+)** | **0.54** | **63.4%** | **5** |

*(900 benchmark instances with known optima, sampled uniformly at random from
the 6,226-instance solved corpus.)*

Contraction degeneracy is tight on nearly two thirds of instances and never more
than 5 below the optimum, against a trivial bound that is tight on one instance
in eighty. It costs a median of 1.1 ms.

---

## 2. The graph

All bounds here are computed on the **MOSP graph** of Yanasse (1997c), as
defined in Yanasse & Senne (2010): nodes are item types (customers), with an arc
between two nodes iff some pattern contains both. A pattern with k item types is
therefore a clique of size k, and the graph is a union of cliques.

This is `M @ M^T`, implemented as `customer_inter/customer_graph.py`. It is *not*
the pattern connection graph (`M^T @ M`, patterns as nodes), which this
repository calls the agreement graph and which the literature uses only for
decomposing an instance into independent clusters. Computing these bounds on the
wrong graph yields wrong numbers; see `CLAUDE.md` for that correction.

The union-of-cliques property was verified empirically as a check on the
implementation: across 445 patterns drawn from 12 benchmark files, every pattern
induced a clique in the constructed graph, with no exceptions.

---

## 3. Prior art

Yanasse & Senne (2010) review the bounds in the literature:

- **Yuen & Richardson (1995)**: the maximum number of different item types in any
  pattern. Described there as *the trivial lower bound*. This is what this solver
  used until now.
- **Yanasse (1997c)**: the size of the maximal clique of the MOSP graph, and the
  smallest degree of any node.
- **Yanasse, Becceneri & Soma (1999)**: an arc contraction bound, reported to
  *"dominate all previous lower bounds proposed in the literature"*.

The last is the natural comparison for this work and we have not obtained it.
It is in *Pesquisa Operacional* 19, 249–277 (1999). That journal is on SciELO,
but **only from 2001 onward**, so the 1999 paper is not available there despite
the journal being open access — nor is Yanasse (1997a), for the same reason.
Yanasse & Senne (2010), which we do hold, cites the arc contraction bound and
states that it dominates all earlier bounds, but does not give the algorithm, so
the comparison cannot be made from our holdings.

The bound developed below is arrived at from the treewidth literature rather than
from that paper. Given that "arc contraction" and "contraction degeneracy" both
contract edges of the same graph, **the two may well be the same bound, and no
novelty should be claimed for §5 until this is settled.** Acquisition routes
worth trying: the INPE digital library (Yanasse is at INPE/LAC, and institutional
repositories commonly hold pre-digitisation work), Becceneri's 1999 thesis which
presents the same operation, Becceneri et al. (2004) in *Computers & Operations
Research* which reports an implementation of it, or writing to the authors.

---

## 4. The clique bound

**Claim.** `MOSP(I) >= omega(G)`, where `G` is the MOSP graph of `I`.

**Proof.** Let `C` be a clique of `G` and fix any pattern sequence. Let `c` be
the customer of `C` whose stack closes earliest. Take any other `c'` in `C`.
Since `c` and `c'` are adjacent, some pattern `p` contains both. All of `c`'s
patterns, `p` among them, are produced no later than the step at which `c`
closes; so `c'` has opened by that step. And `c'` closes after `c`, because `c`
closes earliest. Hence every member of `C` is open at the step where `c` closes,
and `MOSP(I) >= |C|`. ∎

Two things are worth noting. First, the argument is **direct**: it does not
appeal to `MOSP = pathwidth + 1`, which matters because that equality is one this
project has reason to treat carefully. Second, it **subsumes the trivial bound**:
each pattern is a clique of size equal to its number of item types, so the
maximum over patterns is the special case of this bound over single-pattern
cliques.

Maximum clique is NP-hard, but any clique gives a valid bound, so enumeration can
be stopped at any point. The implementation time-boxes `networkx.find_cliques`
and keeps the largest found.

---

## 5. The contraction degeneracy bound

**Definition.** Contraction degeneracy, computed by MMD+ with the least-c
selection rule: repeatedly record the minimum degree of the current graph, then
contract the minimum-degree vertex into the neighbour with which it shares fewest
neighbours. The largest minimum degree observed over the sequence is the bound.

**Justification.** Contraction degeneracy lower-bounds treewidth, treewidth
lower-bounds pathwidth, and — by Yanasse's equivalence on the MOSP graph —
`MOSP = pathwidth + 1`. Hence `MOSP >= delta_C(G) + 1`.

A shorter route may exist. Chu & Stuckey (2009) state as their Lemma 1 that any
*contraction* of the customer graph is a **relaxation** of the instance, which
would bound the original directly with no appeal to the pathwidth equality —
moving this bound from validated to proved. They attribute it to Becceneri,
Yanasse & Soma (2004), noting that only informal arguments are given there, and
that paper is still unobtained. See `reports/chu_stuckey_transferable.md` §4.

**This chain is weaker than the clique argument and the difference matters.**
Unlike §4, it depends on the `MOSP = pathwidth + 1` equality. A lower bound that
is too high does not merely slow a solver down: it makes the search start above
the true optimum and return a value that is wrong. Worse, the usual safety net
does not catch it — verifying the witness ordering by simulation confirms that
the ordering achieves the reported value, not that no better ordering exists. A
wrong lower bound therefore produces a wrong optimum that passes verification.

This is why §8 validates the bound against every known optimum in the corpus
rather than relying on the derivation.

**Domination.** Contraction degeneracy subsumes the clique bound. A clique
`K_k` is a subgraph of minimum degree `k-1`, so degeneracy `>= k-1`, hence
`degeneracy + 1 >= omega`; and contraction degeneracy is at least degeneracy.

The practical consequence is worth stating plainly, because the implementation
time-boxes its clique enumeration and that invites the reasonable question of
whether a longer search would find a better bound. **It would not.** MMD+ already
dominates the *true maximum clique*, not merely the largest one found within the
budget, so an exact maximum-clique solver given unlimited time could not
contribute a single unit. Nothing is being traded away for speed.

*(measured)* Across all 900 sampled instances:

| | count |
|---|---|
| clique strictly better than MMD+ | **0** |
| equal | 359 |
| MMD+ strictly better | 541 |

The time-box is not what limits it either: clique enumeration takes a median of
0.1 ms and a maximum of 4 ms against a 5 s budget, so the cutoff has never fired
on a benchmark instance.

The clique bound is nevertheless retained, and not as a contributor — it has
never supplied a value MMD+ did not. It is kept because it is the only one of the
two provable directly, without the `MOSP = pathwidth + 1` equality this project
has reason to treat carefully (§5, §8). If that equality were ever found wanting,
the clique bound still stands and the solver remains sound. It costs 0.1 ms.

---

## 6. Results

900 instances sampled uniformly from the solved corpus, gap measured as
`optimum − bound` (so 0 is tight, larger is worse):

| bound | mean gap | median gap | tight | max gap |
|---|---|---|---|---|
| trivial | 5.58 | 4.0 | 11/900 (1.2%) | 19 |
| clique | 2.02 | 1.0 | 332/900 (36.9%) | 13 |
| MMD+ | **0.54** | **0.0** | **571/900 (63.4%)** | **5** |

On the published-optima instances specifically:

| instance | size | trivial | clique | MMD+ | optimum |
|---|---|---|---|---|---|
| SP2 | 50×50 | 9 | 9 | **14** | 19 |
| SP3 | 75×75 | 9 | 9 | **21** | 34 |
| SP4 | 100×100 | 13 | 13 | **27** | 53 |
| GP5 | 100×100 | 92 | 95 | 95 | **95** |
| GP6 | 100×100 | 73 | 75 | 75 | **75** |
| GP7 | 100×100 | 74 | 75 | 75 | **75** |
| GP8 | 100×100 | 59 | 60 | 60 | **60** |

Both bounds are exactly tight on GP5–GP8. That is a strong result for the
solver: with the lower bound equal to the optimum, certifying optimality needs
no refutation at all — a satisfiable call at that value suffices, and the
expensive direction disappears.

### 6.1 Where each bound helps

Splitting the sample into density quartiles, where density is the fraction of
1-entries in `M`:

| density range | MMD+ advantage over clique | instances where MMD+ wins |
|---|---|---|
| 0.07–0.28 | +2.86 | 190/225 |
| 0.28–0.41 | +2.11 | 212/225 |
| 0.41–0.55 | +0.85 | 123/225 |
| 0.55–0.74 | +0.08 | 16/225 |

The two bounds are complementary in a way that explains the earlier difficulty.
On dense instances the clique bound is already near-optimal, because cliques are
large and a single pattern nearly suffices. On sparse instances it collapses to
the trivial bound, and contraction degeneracy supplies almost all of the value.
The instances this solver could not close — SP3, SP4, and the Chu & Stuckey
random set — are sparse, which is exactly why their bounds were so weak.

### 6.2 Cost

| | median | maximum |
|---|---|---|
| clique enumeration | 0.1 ms | (time-boxed) |
| MMD+ | 1.1 ms | 0.09 s |

Negligible against solve times measured in minutes to hours. MMD+ is
`O(n)` contractions of `O(n^2)` cost each, so the implementation skips graphs
above 400 nodes rather than stall a solve; no benchmark instance here reaches
that.

---

## 7. Effect on the solver

The bound narrows the interval the binary search must resolve. For SP4 the
search range halves, from `[13, 63]` to `[27, 63]`. This matters more than the
range arithmetic suggests: the calls it eliminates are refutations at values far
below the optimum, and those are empirically the ones that never return. In an
earlier parallel-k experiment on SP3, a satisfiable call at `k=37` returned
quickly while every probe in `k = 10..36` ran for an hour without answering. A
bound that rules those out a priori removes work that no amount of solver
improvement would have made cheap.

### 7.1 The ablation: no instances converted *(measured)*

The bound landed together with a switch of SAT backend to Kissat404, so the
corpus gains could not initially be apportioned between them. They now can, and
the result does not favour the bound.

Round 1 of an overnight run used Kissat404 with the clique bound only, at 3600 s
per instance, and solved 346 instances. Rerunning its 150 survivors at the
**same** budget and the **same** backend, with contraction degeneracy added,
converted **0 of the 60** reached before the run was stopped. Not one instance
that had resisted the clique bound fell to the stronger one.

So the corpus gains attributed to "the bound and the backend" belong to the
backend. The measurement is clean precisely because nothing else changed: same
instances, same budget, same solver, one variable.

### 7.2 Where the bound does pay

This is not the same as the bound being worthless, and the distinction matters
for how it should be described.

- It does **not** make hard refutations tractable. §7.1 is the evidence, and the
  mechanism is visible in the numbers: SP4's bound rose from 13 to 27 while its
  optimum is 53, so the refutations that remain are still far below the answer
  and still do not return.
- It **does** make refutations unnecessary where it is tight. GP7 and GP8 were
  both settled by a single satisfiable call, because ω equalled the optimum and
  nothing had to be refuted at all. Both had resisted hours of binary search, and
  no additional budget would have closed either.

The bound's contribution is therefore in its *quality* — tight on 63.4% of
instances, mean gap 0.54 — realised through the descending ratchet
(`benchmarks/ratchet.py`), which closes an instance outright whenever the value
it reaches meets the bound. It is not measurable as instances-solved-per-CPU-hour
by a binary search, which is where §7 originally implied it would show up.

---

## 8. Soundness validation

Because §5 makes the bound a correctness dependency, it was checked rather than
assumed.

- **Full corpus.** The bound was computed for all **6,226** benchmark instances
  with a known optimum and compared against it. **Zero violations** — the bound
  never exceeded an optimum.

  (`solutions/` holds 6,230 files, four of which — `GP1.json` through
  `GP4.json` — are duplicates written by `validate_published_optima.py` under a
  bare naming convention that `from_benchmark_file` does not produce. 6,226 is
  the number of distinct benchmark instances with a solution, and the figure to
  quote.)
- **Exhaustive small instances.** `tests/test_lower_bounds.py` compares the
  bound against optima obtained by brute-force enumeration over all orderings,
  on random instances across a range of sizes and densities.
- **Continuous.** The same test file re-checks a sample of the corpus on every
  test run, so a regression in the bound fails the suite rather than silently
  corrupting results.

A caveat on what this establishes: agreement with 6,226 known optima is strong
evidence, but those optima were produced by this same solver. The check rules
out the bound exceeding values the solver found, and it would catch a bound that
is outright wrong; it does not independently confirm the underlying equality
chain. The 11 published-optima instances in §6 are the only fully independent
comparisons, and the bound is consistent with all of them.

---

## 9. Reproduction

```bash
# bound values, cost, and comparison across the corpus
python -c "
from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph
from satisfiability.mosp_solver import _lower_bound, _contraction_degeneracy
inst = MOSPInstance.from_benchmark_file('benchmarks/instances/ChallengeInstances2005/Wilson/sp4.txt')[3]
G = build_customer_graph(inst)
print('MMD+ bound:', _contraction_degeneracy(G) + 1)
print('combined  :', _lower_bound(inst))
"

# soundness against known optima
python -m pytest tests/test_lower_bounds.py -v
```

Implementation: `satisfiability/mosp_solver.py::_lower_bound` and
`::_contraction_degeneracy`.

---

## 10. Open items

1. **Obtain Yanasse, Becceneri & Soma (1999)** and determine whether its arc
   contraction bound is this bound, a weaker one, or a stronger one. No novelty
   should be claimed for §5 until this is settled — the names are suggestively
   similar and both contract edges of the MOSP graph. Note that *Pesquisa
   Operacional* is digitised on SciELO only from 2001, so this is not the easy
   download it first appeared to be; see §3 for routes.
2. ~~Ablate the bound against the Kissat404 switch~~ — done, §7.1. The gains
   belong to the backend; the bound pays through §7.2 instead.
3. ~~Re-run the unsolved instances with the strengthened bound~~ — done, twice.
   By binary search it converted nothing (§7.1). By the descending ratchet all
   147 gained a solution and **6 closed outright** on reaching their bound, which
   is §7.2's mechanism at scale: the bound closes instances that no refutation
   budget would have.
4. **Consider an exact maximum clique** on the instances where enumeration is
   time-boxed out, though §5's domination result suggests little is available
   there.
5. **Close the gap on the remaining 0.54.** The bound is tight on 63% of
   instances; the residual is concentrated where neither bound is strong, and
   characterising those instances would say where to look next.
