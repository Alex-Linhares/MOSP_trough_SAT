# What the certified corpus teaches a model

*2026-09-22. Code in `learning/`; regenerate every number below with*

```bash
python -m learning.dataset          # 6,376 x 36 feature table, ~20s
python -m learning.study_optimum    # the prediction tables
python -m learning.policy evaluate  # the ordering tables, ~3 min
```

The corpus is 6,376 instances with a **proved** optimum and a witness ordering
that achieves it. Supervised learning on an NP-hard problem normally trains
against whatever a solver reached inside its budget, so the model fits the
solver's failures as well as the problem; here the labels are refutations. That
is the whole reason this is worth doing, and it is worth stating before any
table: the dataset is unusual, the methods are not.

## 0. The rule

**Nothing learned becomes a bound.** `satisfiability.mosp_solver._lower_bound`
is a correctness dependency — a bound one point above the true optimum makes the
binary search start above it and return a wrong answer that still passes witness
verification, because the witness does achieve the value reported. A model's
prediction has no such guarantee and never will.

An *ordering* is different. It is checked by `max_open_stacks` on the original
instance, so a model that proposes a bad one costs solution quality and nothing
else. §2 is therefore the half of this work with a route into the solver, and §1
is analysis.

## 1. Predicting the optimum

Five-fold cross-validation, grouped by source file. `exact` is the fraction
landing on the optimum; `over` is the fraction predicting above it, which for a
*bound* would be a wrong answer and for a prediction is merely wrong.

| model | split | MAE | RMSE | exact | over |
|---|---|---|---|---|---|
| lower bound (`_lower_bound`) | none (baseline) | 0.979 | 3.314 | 65.3% | 0.0% |
| upper bound (`cs-dfs`) | none (baseline) | 0.241 | 0.735 | 84.5% | 15.5% |
| structure only | grouped by file | 0.453 | 0.855 | 71.2% | 13.6% |
| structure only | random (leaks!) | 0.343 | 0.809 | 77.5% | 11.0% |
| structure + bounds | grouped by file | **0.213** | **0.513** | **86.7%** | 7.4% |
| structure + bounds | random (leaks!) | 0.192 | 0.514 | 87.9% | 7.0% |

Three things to take from it.

**Structure alone beats the lower bound as a predictor.** No search, no
heuristic, nothing the solver computed — only shape, degree distributions and
MOSP-graph statistics — and the optimum comes out exactly on 71.2% of held-out
instances against the bound's 65.3%, at half the MAE and a quarter of the RMSE.
The bound is a proof and this is a guess, so it replaces nothing. What it says is
that the instance's structure determines more of the optimum than our best
certified bound currently extracts from it, which is an argument for looking
again at the bound, not for trusting the model.

**With the bounds as features the model beats `cs-dfs`,** and the margin is in
RMSE (0.513 against 0.735) far more than in MAE. It is not finding a better
answer on the easy instances — it is failing less badly on the ones where the
heuristic is far off.

**The leakage is real but small.** Instances in one benchmark file come from one
generator configuration and are near-duplicates; splitting at random puts
siblings on both sides, and it is worth 0.11 MAE on structure alone. Reported
here rather than buried because a study of this corpus that split at random
would have looked better and meant less.

### Where the bounds leave a gap

3,975 of the 6,376 instances have `ub_best == lb_best` — settled before any
search runs. Restricting to the other 2,401:

| population | n | model | MAE | RMSE | exact |
|---|---|---|---|---|---|
| all instances | 6,376 | learned | 0.213 | 0.513 | 86.7% |
| all instances | 6,376 | `cs-dfs` | 0.241 | 0.735 | 84.5% |
| bounds leave a gap | 2,401 | learned | **0.467** | **0.808** | **67.3%** |
| bounds leave a gap | 2,401 | `cs-dfs` | 0.639 | 1.197 | 59.0% |

The margin widens where it matters: on the instances that actually need search,
the model is exact 8 points more often and its RMSE is a third lower.

### Which features carry it

Permutation importance on a held-out fifth, in MAE points:

| feature | cost |
|---|---|
| `ub_cs_dfs` | 4.447 |
| `ub_best` | 2.622 |
| `lb_contraction` | 0.876 |
| `g_edges` | 0.413 |
| `g_deg_mean` | 0.364 |
| `ub_mcn` | 0.089 |

The bounds dominate, as they should — they are near-answers. Below them the
signal is the MOSP graph's edge count and mean degree, not the matrix shape or
density, which is consistent with the optimum being a property of that graph
rather than of the matrix that generates it.

### An incidental finding about `_lower_bound`

Over all 6,376 instances, **the clique bound never once exceeded contraction
degeneracy + 1**: `lb_contraction == lb_best` on 100% of rows, under a 1-second
clique budget. The solver spends up to 5 seconds per call enumerating maximal
cliques for a bound that has not improved on a single instance in the corpus.
That is a measurement on this corpus and not a theorem — cliques cannot be
dropped on the strength of it, and the clique bound is the one provable *without*
Yanasse's pathwidth equality, which is an independence worth keeping. But the
budget is worth revisiting, and this is the kind of thing a feature table makes
visible for free.

### Is the heuristic upper bound already optimal?

A classifier, and the one result here with an immediate operational use: it says
whether an instance needs one refutation call or a search.

- AUC **0.965**, accuracy 0.926, against a base rate of 0.846
- on the 2,401 where the bounds leave a gap: AUC **0.868**, base rate 0.592

## 2. A closing-order policy learned from the witnesses

Every construction heuristic answers the same question repeatedly: given the
customers already closed, which closes next? Each certified witness is a product
order, which induces a closing order, which is a sequence of such decisions made
by something that provably reached the optimum. Replaying all 6,376 witnesses
yields **2.27 million labelled decisions** — at each step, the customer actually
closed against every other candidate, described by eight local features
(remaining degree, newly opened customers, open stacks after closing, progress,
and so on). A LightGBM ranker fits that in 7 seconds.

Five-fold cross-validation grouped by source file, 2,000 held-out instances:

| strategy | MAE over optimum | exact | worst |
|---|---|---|---|
| `mcn` | 1.627 | 51.0% | +27 |
| learned greedy | 0.463 | 75.0% | +34 |
| `cs-dfs` | 0.302 | 82.0% | +10 |
| **`cs-dfs` seeded with the learned order** | **0.137** | **92.0%** | **+6** |

**The learned greedy beats MCN decisively** — a third of the error, exact 24
points more often — while remaining a single pass with no search. MCN is the
literature's construction heuristic for this problem, described by Yanasse &
Senne as "the best or among the best of the literature"; our implementation of
it is admittedly not a faithful MCNh (see `satisfiability/heuristics.py`).

**It does not beat `cs-dfs`,** which is a 200,000-node DFS, and its tail is
worse: +34 on one held-out instance against the DFS's +10. A construction with
nothing behind it fails ungracefully.

**Seeding the DFS with it halves the DFS's error** and cuts the worst case from
+10 to +6. This is where the policy belongs. `restricted_dfs` already takes a
`seed_order`, its pruning is against the incumbent, and its own docstring says a
good seed is worth more to it than extra nodes. The learned order is a better
seed than MCN's, which is exactly what the table shows.

On 4 of 500 instances in an earlier single-split run the seeded DFS came out
*worse* than the unseeded one. That is not noise: the DFS prunes in `_cs_cost`
space, which over-charges, so a seed with lower `_cs_cost` can cut a branch
whose product order would have simulated lower. The proxy mismatch is documented
in `_cs_cost`; this is it showing up in practice.

## 2.1 The whole corpus, scored against truth

*Added 2026-09-22, after registering the strategies and sweeping.*

The test this was supposed to be was the one `reports/ub_mosp_search.md` ran for
`cs-dfs`: re-run the heuristic over the corpus and count the upper bounds it
improves. **That test no longer exists.** The corpus closed on 2026-09-22 — every
cached value is a certified optimum — so `benchmarks.reheuristic` can improve
nothing, and `_save_solution` is monotone, so a sweep writes nothing at all:

```
python -m benchmarks.reheuristic --all --strategy mcn
6376 instances -> 0/6376 improved, 0 stacks saved, in 36s
```

What the closed corpus gives instead is better than the original test. Every
instance's optimum is *known*, so a sweep is an exact scoring run over all 6,376
rather than a count of improvements over the then-best guess. `reheuristic`
already reports the cached value beside what the strategy achieved;
`learning.corpus_sweep` aggregates that, and sweeps fold by fold with the models
from `learning.policy train-folds` so that no instance is ever scored by a model
that trained on its own generator configuration.

| strategy | mean overshoot | exact | worst | total overshoot |
|---|---|---|---|---|
| `mcn` | — | — | — | (improves nothing; see above) |
| `cs-dfs` | 0.241 | 84.5% | +10 | 1,538 |
| `learned` | 0.383 | 77.7% | +34 | 2,439 |
| **`learned+cs-dfs`** | **0.105** | **93.3%** | **+8** | **670** |

Head to head, `learned+cs-dfs` against `cs-dfs` on the same 6,376 instances:

- **strictly better on 709 instances, 882 stacks saved**
- strictly worse on 13, 14 stacks lost
- `cs-dfs` missed the optimum on 988; the seeded version recovers **571** of them
- 417 are missed by both

This is the analogue of the 25 improvements in `reports/ub_mosp_search.md`, and
it is much larger — but the two numbers are not comparable, and it would be
wrong to read this as 28× better. That report counted improvements on 148
instances that were hard enough to still be open after everything else had run;
this counts them over the whole corpus, including thousands of small instances
`cs-dfs` was never run against before. The honest comparison is the head-to-head
column, and the honest summary is that seeding recovers 58% of the optima
`cs-dfs` misses.

The largest gains are on the Chu & Stuckey `Random` instances, which is where
the remaining difficulty is:

| instance | optimum | `cs-dfs` | `learned+cs-dfs` |
|---|---|---|---|
| `Random-100-50-6-4_0` | 48 | 58 | 51 |
| `Random-100-50-8-2_0` | 55 | 62 | 57 |
| `p4050n10_0` | 14 | 20 | 15 |
| `Random-125-125-8-1_0` | 95 | 101 | 98 |

### It is also faster

Measured in-process over 300 random instances, so that the process-spawn and
library-import cost of the sweep harness is excluded:

| strategy | per instance |
|---|---|
| `mcn` | 0.3 ms |
| `learned` | 2.1 ms |
| `cs-dfs` | 19.3 ms |
| `learned+cs-dfs` | **11.6 ms** |

Seeding the DFS with the learned order makes it **40% faster as well as more
accurate**. That is not a surprise once stated: the DFS prunes against its
incumbent, a better incumbent cuts more of the fan at once, and 2 ms of policy
buys back 10 ms of search. The 460s wall clock of the corpus sweep is almost
entirely 6,376 process spawns each importing LightGBM, not the strategy.

### The 13 regressions

All are small instances, all off by exactly one, and all have the same cause —
the one `_cs_cost`'s docstring names. The DFS prunes in `_cs_cost` space, which
over-charges relative to simulation, so a seed with lower `_cs_cost` can cut a
branch whose product order would have simulated *lower*. A better incumbent is
not monotonically a better search. 13 against 709 is a good trade, and running
both and keeping the minimum would remove even that, at the cost of the speedup.

### One more thing the sweep checked

Not one of the 6,376 orderings produced by either strategy came in *below* the
certified optimum. That is not a proof of anything — a heuristic beating a
proved optimum would mean the optimum was wrong — but it is 12,752 independent
chances for the corpus to contradict itself, taken and passed.

## 3. What this is not

**The corpus is not the problem.** 5,938 of 6,376 instances have 30 or fewer
customers, 3,975 are settled by bounds before any search, and the dense 125×125
Chu & Stuckey instances that cost 19 hours on 25 cores are **25 rows**. A model
fitted here is a model of this corpus. Everything above is reported on the
subset where the bounds leave a gap as well as overall, but no amount of
grouping fixes a population that is 93% small.

**The policy has not been run on a hard instance.** The comparison is over
held-out instances drawn uniformly, so it says nothing about 125×125 at density
4 — where `cs-dfs` is not the bottleneck anyway; the refutation is.

**Nothing here is wired into the solver.** `learning/policy.py` exposes
`learned_upper_bound`, and registering a `learned+cs-dfs` strategy in
`satisfiability.heuristics` is a few lines, but it would put LightGBM and a
checked-in model file on the solver's critical path. That is a dependency
decision, not a measurement, and it is left open.

## 4. Next, in order

1. ~~**Register the seeded strategy** and sweep the corpus with it.~~ **Done,
   2026-09-22** — §2.1. `learned` and `learned+cs-dfs` are registered behind a
   soft import in `satisfiability/heuristics.py`; the seeded strategy is better
   on 709 instances and worse on 13, and is 40% faster than `cs-dfs` besides.
   It is still not the *default* for anything: making it one would put LightGBM
   and a model file on the solver's critical path.
2. **Use the learned scorer inside the DFS,** not only as its seed: order the
   candidate fan by predicted score rather than by immediate cost. The fan is
   already sorted cheapest-first, which is a one-step-lookahead policy; this
   replaces it with a trained one, and prediction cost per node is the question.
3. **Train the tightness classifier into a scheduler.** `P(ub is optimal) =
   0.965 AUC` is enough to decide, per instance, between issuing one refutation
   call and descending — which is the shape of the portfolio decision
   `CLAUDE.md` already lists as a next step.
4. **Grow the population that matters.** Every conclusion here is bounded by a
   corpus that is 93% small instances. Generating and certifying more
   100×100-and-up instances would do more for this folder than any modelling
   choice.
