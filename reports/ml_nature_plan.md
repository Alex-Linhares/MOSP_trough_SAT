# Using machine learning to understand the nature of MOSP

*2026-09-25. A companion to `reports/learning_plan.md`, not a replacement. That
plan asks what learning can do for the solver and answers "measurement, not
machinery". This one asks what learning can tell us about the problem — which
quantities determine the optimum, where the proved bounds fail and why, whether
hardness has a phase transition, what optimal orderings have in common, and how
representative the benchmarks are. Nothing here goes into the solver's critical
path; the deliverables are findings, conjectures and extremal instances.*

## 0. What we are standing on

**The object of study is a graph, not a matrix.** By Yanasse (1997c),
`MOSP = pathwidth(MOSP graph) + 1`, where the MOSP graph has customers as nodes
and a clique per product. So every question about the optimum is a question
about the pathwidth of a *union of cliques*, and for the random benchmarks that
graph is a **random intersection graph** `G(n, m, p)`: `n` customers, `m`
products, each customer in each product with probability `p`. That family has a
literature of its own (degree distribution, clustering, giant-component
threshold), which gives the studies below something to compare against. The
matrix carries information the graph does not — which cliques cover which
edges — and one question (§2.9) is whether that residue matters for anything.

**The assets.**

| asset | size | notes |
|---|---|---|
| certified optima with witness orderings | 6,376 | 6,370 by refutation; `Random-100-100-2-2_0` was once certified wrong, see `reports/learning_plan.md` §6 |
| feature table (`learning.dataset`) | 6,376 × 36 | matrix, MOSP-graph and bound features; regenerate in ~20 s |
| closing-order decisions from witnesses | 2.27 M | already used for imitation in `learning/policy.py` |
| timings | ledger 280 rows + sweep CSVs | sparse and censored by timeouts; node counts are printed, not stored |
| exact solver at small `n` | unlimited | `n ≤ 30` certifies in milliseconds, so labelled data is free below that size |

**The lopsidedness.** 5,938 of the 6,376 instances have 30 or fewer customers,
and the 125×125 class that holds all the compute is 25 rows. A model that says
something about "MOSP" is mostly saying something about small instances, and
every study below has to say which size range its conclusion covers.

**The rules, unchanged.** A prediction is never a bound. Every split groups by
source file, and where the question is about scale it groups by size. Labels are
proofs from our own search, which has been wrong once, so any finding that rests
on a handful of instances is re-certified for those instances before it is
written up.

## 1. Methods on the table

Each question below picks from this list; listing them once keeps the question
sections about the question.

| method | what it is for | status |
|---|---|---|
| gradient boosting (LightGBM) with permutation and SHAP importance | which features carry the signal | built |
| interpretable models: shallow trees, explainable boosting machines, monotone GAMs | rules a human can read and try to prove | new |
| symbolic regression (PySR or a small hand-rolled search over formulae) | a closed-form estimator of the optimum or of the residual over a bound | new |
| conformal prediction / quantile regression | calibrated intervals where a point estimate would mislead | new |
| survival models (Cox, random survival forest) | runtimes with timeouts, which are censored observations and must not be fed to ordinary regression | new |
| graph neural network on the MOSP graph, or on the bipartite matrix graph | a check on whether the hand-built features miss structure: if it beats them under grouped splits, they do | new |
| Weisfeiler–Lehman hashing and canonical forms (nauty) | isomorphism classes, near-duplicates, generator fingerprints | new |
| embeddings and clustering (UMAP over features or WL kernels) | the shape of instance space and where the benchmarks sit in it | new |
| evolutionary / local search over bit flips with the exact solver as oracle | extremal instances: maximal bound gap, maximal nodes per size, maximal heuristic error | new |
| finite-size scaling on generated ensembles | phase transitions and scaling exponents | new |
| differential testing across configurations | soundness of refutations; the only tool that has caught a false one | planned in `learning_plan.md` §3.3 |

## 2. The questions

Ordered roughly by cost. Each has the method, the baseline that makes an answer
mean something, the deliverable, and a kill criterion.

### 2.1 How redundant is the corpus, and what does it actually cover?

Data hygiene, and a finding in its own right. Two instances with isomorphic MOSP
graphs have the same optimum, and a generator that emits near-duplicates
inflates every downstream sample size.

- **Method:** WL hash and canonical form of every MOSP graph; count isomorphism
  classes per collection and per size; embed the feature table with UMAP and
  colour by collection.
- **Deliverable:** a table of distinct classes per collection, and a map of
  instance space showing which regions the benchmarks occupy and which are
  empty. A generator-classifier (predict `collection` from structure) whose
  accuracy measures how distinguishable the benchmark families are: near 100%
  means results on one family do not transfer to another.
- **Kill:** none; this is cheap and every other study needs its answer.

### 2.2 Which structural quantities determine the optimum?

`reports/learning.md` §1 already shows structure alone predicts the optimum
exactly on 71.2% of held-out instances against the proved bound's 65.3%, and
that MOSP-graph edges and mean degree carry the signal, not matrix shape. The
open question is *what function* of the graph it is.

- **Method:** extend the feature set with graph invariants that pathwidth is
  known to relate to — treewidth upper bounds (min-fill, min-degree), bandwidth
  heuristics (Cuthill–McKee), spectral radius and Fiedler value, balanced
  separator size from a cheap partitioner, clique cover number, and the random
  intersection graph parameters `(n, m, p)` themselves. Then symbolic regression
  and monotone GAMs on the optimum and, separately, on the **residual over the
  best proved bound**. A GNN on the MOSP graph as the "is anything missing"
  check.
- **Baseline:** the current 36-feature LightGBM, grouped by file.
- **Deliverable:** a ranked list of invariants, and if one simple formula fits
  the residual, a written conjecture of the form "for these graphs,
  `pw ≥ f(...)`" handed to the bound work. That is the route by which the
  expansion bound was found, formalised.
- **Kill:** if no invariant beyond the current set moves grouped MAE by more
  than 0.02, the current features already capture what is capturable at this
  scale, and the section closes with that statement.

### 2.3 Where do the proved bounds fail, and what do those instances look like?

The contraction bound has mean gap 0.86 corpus-wide and 11.05 on the `Random`
class. The learning report found that degree-based bounds saturate at the
average degree. The question is whether the bound-defeating instances share a
recognisable structure.

- **Method:** a classifier for `bound tight` vs `gap ≥ 2` with an interpretable
  model (depth-3 tree, EBM); cluster the gap instances; inspect the smallest
  ones by hand. Compare the gap against each candidate invariant from §2.2 to
  see which one the bound is blind to.
- **Baseline:** density and size alone.
- **Deliverable:** a description of the bound-defeating family in graph terms,
  and the ten smallest instances exhibiting it, drawn. Small enough to reason
  about is the point.
- **Kill:** if the classifier cannot beat density-and-size, the gap is not
  structural at this scale and the section says so.

### 2.4 Is there a phase transition in hardness?

Random SAT has its ratio 4.26; random graph colouring has its threshold. Does
MOSP hardness peak at a density, and does the peak sharpen with size?

- **Method:** generate ensembles at fixed `(n, m)` across a density sweep, at
  sizes where certification is cheap (`n ≤ 40`), 100+ instances per cell.
  Record nodes visited by the refutation at `optimum − 1` — nodes, not seconds,
  so the measurement survives hardware changes. Plot median and tail of nodes
  against density; fit a scaling exponent across sizes. Test candidate order
  parameters: density, mean degree, `optimum / n`, `(ub − lb)`.
- **Prerequisite:** `benchmarks.csearch` and the C search print node counts but
  do not store them. Add a `nodes` column to the ledger first.
- **Baseline:** hardness monotone in density (no peak).
- **Deliverable:** a hardness map over `(n, density)`, an order parameter if one
  exists, and a statement of where Chu & Stuckey's `Random` classes sit on it —
  which would explain in one picture why densities 2 and 4 at 125×125 are the
  ones that take 28 hours.
- **Kill:** if node counts at fixed `n` are monotone in density with no peak
  across three sizes, there is no transition to find at these sizes.

### 2.5 Does the optimum concentrate on random instances?

If, at fixed `(n, m, p)`, the optimum's variance is small relative to its mean,
then for random instances the optimum is essentially a function of the
parameters, and a formula for `E[opt](n, m, p)` is a description of the problem
rather than a model of the corpus.

- **Method:** the same generated ensembles as §2.4; measure mean and variance of
  the optimum per cell; fit `E[opt]` as a function of `(n, m, p)` by symbolic
  regression; compare with what is known about pathwidth of random intersection
  graphs and of `G(n, p)` (linear in `n` above the giant-component threshold).
- **Deliverable:** a formula with its residual distribution, and the size range
  it is validated on. Nothing here is a bound.
- **Kill:** if the coefficient of variation stays above 0.2 up to `n = 40`,
  the optimum does not concentrate at reachable sizes and the formula is not
  worth stating.

### 2.6 What do optimal orderings have in common?

The 6,376 witnesses induce closing orders. `learning/policy.py` imitates them
with a LightGBM ranker and wins, but the ranker is opaque. The question is
what rule it learned.

- **Method:** distil the ranker into a depth-3 tree or a linear scorer over the
  eight local features and measure how much of its accuracy survives; test
  simple hypotheses directly — does the witness close customers in Fiedler-vector
  order, in BFS layers, by minimum remaining degree with a specific tie-break?
  For `n ≤ 12`, enumerate *all* optimal closing orders exactly and measure how
  degenerate the optimum is: one ordering up to symmetry, or thousands.
- **Baseline:** MCN, which is the literature's greedy and what Yanasse & Senne
  call among the best.
- **Deliverable:** a stated rule that recovers most of the learned policy's
  advantage over MCN, which would be a heuristic in the literature's sense,
  and a measurement of optimal-ordering degeneracy versus size.
- **Kill:** if no readable rule keeps more than half of the ranker's gain over
  MCN, the policy is genuinely a function of interactions and the section
  reports that as the finding.

### 2.7 Can we construct the instances the theory is missing?

Extremal instances are how conjectures get made. `reports/constructed_instances.md`
already builds instances with *known* optima; this is the complement —
instances that are maximally bad for something.

- **Method:** local search or a genetic algorithm over the matrix at small
  sizes (`n ≤ 15`, so the exact solver is the oracle at every step), with
  fitness = bound gap, or nodes per size, or `cs-dfs` overshoot, or
  disagreement between two configurations. Deduplicate by canonical form.
- **Deliverable:** for each objective, a family of small instances with the
  objective's value, drawn. A 12-customer instance where the contraction bound
  is off by 4 is something one can reason about; a 125×125 instance where it is
  off by 42 is not.
- **Kill:** if the search cannot beat the worst instance already in the corpus
  at the same size for any objective after a fixed budget, the corpus is already
  extremal and the section says so.

### 2.8 Does what we learn at small sizes hold at large ones?

Every conclusion above is drawn where certification is cheap. The corpus has
enough 50–125 instances to test whether it survives the trip.

- **Method:** train on `n ≤ 30`, test on `n ≥ 50`, for the optimum predictor
  and for any formula from §2.2 and §2.5. Report error by size band. Conformal
  intervals fitted on small sizes, coverage checked on large.
- **Deliverable:** the size at which each finding stops holding, if it does.
  This is also the study that licenses, or refuses, the calibrated predictions
  `learning_plan.md` §3.4 wants for the uncertifiable regime.
- **Kill:** if coverage collapses across the size boundary, the intervals say
  nothing at large sizes and must not be quoted there.

### 2.9 Is the graph the whole story?

The value is a function of the graph. Is the *hardness*? Two matrices with the
same MOSP graph and different clique covers may cost the search differently, and
if so the matrix carries information the pathwidth reduction discards.

- **Method:** generate pairs of instances with identical MOSP graphs and
  different products (re-cover the same edge set with different cliques); compare
  nodes to refute at `optimum − 1`. Predict nodes from graph-only features versus
  graph-plus-matrix features under grouped splits.
- **Deliverable:** a yes or no, with the size of the effect.
- **Kill:** if graph-only features predict nodes as well as the full set, the
  matrix is irrelevant to hardness too and the graph is the whole story.

### 2.10 Which instances will expose an unsound refutation?

Carried over from `learning_plan.md` §3.3 because it belongs here as much as
there: it is a question about where the problem is subtle enough to fool a
dominance rule. Build the differential harness first, without learning; then ask
whether the features of the instances that produced disagreements predict new
ones. The kill criterion there stands.

## 3. Sequence

1. **Hygiene and instrumentation** — §2.1 in full; add node counts to the ledger
   (§2.4 prerequisite); add the extra invariants to `learning/features.py`.
   A few days, no compute.
2. **The existing table** — §2.2 and §2.3. Runs on what is already computed;
   the GNN check is the only expensive piece.
3. **Generated ensembles** — §2.4, §2.5 and §2.9 share one generation-and-solve
   campaign at `n ≤ 40`; design it once. Cheap per instance, large in count.
4. **Witnesses** — §2.6. Independent of the above; can run in parallel.
5. **Extremal search** — §2.7, once §2.1's canonical forms exist to deduplicate.
6. **Scale** — §2.8 last, because it tests everything before it.

Each item is one Ralph-loop task: an immutable question, a progress file, and a
report section as the deliverable. The guide in `Ralph_Loops/` fits this shape.

## 4. What would count as understanding

Not model accuracy. The outputs that would change what this project knows:

- a graph invariant, or a formula in `(n, m, p)`, that tracks the optimum better
  than the proved bounds, stated as a conjecture with the instances it was tested
  on — a target for a proof, or for the Lean development;
- a description of the bound-defeating family in words, with small drawn
  examples;
- a hardness map with an order parameter, locating the benchmark classes on it;
- a readable closing rule that recovers most of what imitation learned;
- the size at which each of the above stops holding.

A model that predicts well and explains nothing is a tool, and
`learning_plan.md` already decides what tools are worth. This plan is for the
other thing.
