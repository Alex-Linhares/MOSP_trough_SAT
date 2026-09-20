# MOSP Solver — Two Exact Engines, Checkable Answers

Exact solver for the **Minimization of Open Stacks Problem (MOSP)**, combining a
direct [SAT encoding](reports/encoding.md) run on [Kissat](https://github.com/arminbiere/kissat)
with a [complete search over customer closing orders](reports/customer_search.md),
plus graph-theoretic lower bounds and several upper-bound heuristics. Includes a
Lean 4 formalization: the SAT encoding is [proved faithful](lean/MOSPFormalization/Encoding.lean),
and the pathwidth theory the project started from is partly formalized.

**6,349 of 6,376 cached solutions are certified optimal —
99.58% of the corpus**, each with a witness ordering in `solutions/`
that can be checked without trusting this code, for **about a day of solving on 25
cores** (588 core-hours). What remains open is 26
instances (0.42%), all sparse Chu & Stuckey `Random` instances.
Every file records how its value was established, so proofs and good guesses are
never added together.

*(Regenerate with `python -m benchmarks.corpus` and `python -m
benchmarks.compute`; both move whenever a run closes something.)*

MOSP arises in manufacturing: given a set of customer orders (each requiring some
subset of products), find a production sequence that minimizes the maximum number
of simultaneously open customer stacks. The problem is NP-hard (Linhares &
Yanasse 2002).

## The same problem is a VLSI layout problem

Linhares & Yanasse (2002) show MOSP *is* the **gate matrix layout problem** from
VLSI design. A gate matrix circuit is a set of gates — vertical wires — carrying
transistors, with horizontal *nets* joining the gates that share a transistor.
Permuting the gates does not change the logic, but it changes how many physical
rows, or **tracks**, the nets need, and tracks are what determine circuit area.
Their Proposition 2: **the number of open stacks equals the number of tracks.**

So every solution here can be drawn as a packed circuit. Customers become nets,
patterns become gates in production order, and nets whose stacks never overlap
share a track:

![SP1 as a packed gate matrix layout](figures/SP1_gatematrix.png)

Nine tracks, so nine open stacks — the answer is the height of the picture. Dots
are transistors, marking the gates a net actually connects to; a net spanning a
single gate is a customer needing one pattern, whose stack opens and closes at
the same step.

### Why some instances are hard and others are not

The same drawing explains why instance density dominates everything about this
problem. These three are all 50x50, so only density varies:

![Sparse to dense: SP2, GP4, GP1](figures/density_contrast.png)

Same track scale in all three, so the height each fills is its optimum. Sparse
instances leave slack a sequence can exploit: SP2's nets are short, several share
a track, and 50 customers pack into 19. Dense ones do not — in GP1 almost every
net spans the whole circuit, so no two can share a track and 50 customers need
45. No permutation can help, which is why its optimum is 45 rather than anything
a better search might find.

That split runs through the whole project. It is why the maximum-clique lower
bound is exactly tight on the dense instances and useless on the sparse ones, why
contraction degeneracy is needed for the latter (see [Lower bounds](#lower-bounds)),
and why the instances whose optimality is still open are overwhelmingly sparse.

(Two quantities get called "density" in this literature: the fill rate of `M`,
and the edge density of the MOSP graph. The figures report both; Frinhani et
al.'s tabulated `D` is the second.)

## Two engines, and why both are needed

The project has two exact methods, and they are not symmetric. Stated as
measured rather than as it would be nicer to state:

| | **direct SAT** | **customer search** |
|---|---|---|
| searches | positions of products, `O(m²)` variables | orders in which customer stacks close |
| the bulk of the corpus | closed 6,226 instances | not run on them; would likely also close them |
| hard Random instances, dense (d ≥ 6) | refutations do not return | seconds to minutes |
| hard Random instances, sparse (d = 2) | refutations do not return | branching factor explodes |
| proof artifact | a CNF anyone can re-refute | none yet (see [limitations](#known-limitations)) |
| entry point | `satisfiability.mosp_solver.solve_mosp_sat` | `satisfiability.customer_search.solve` |

An earlier version of this section claimed the two "fail on disjoint sets". That
was an inference from their profiles and it is not what the corpus shows. On the
hard instances the customer search's failures are a **subset** of SAT's: it
closed 111 that SAT could not, and **no instance is known that SAT closes and it
cannot**. So racing them would be a bet, not a demonstrated win, and the
complementarity that would justify a portfolio has not been measured. What *is*
measured is that the customer search dominates at the hard end while SAT is the
only one of the two that emits a checkable proof.

### The SAT engine

The solver encodes the MOSP decision problem ("can patterns be sequenced with at
most k open stacks?") directly as a SAT formula, then **binary searches** over k.

Given a MOSP instance with binary matrix M (rows = customers, columns = patterns):

1. Compute **bounds**. Lower: the largest clique found in the MOSP graph and its
   contraction degeneracy (see [Lower bounds](#lower-bounds)). Upper: one of the
   heuristics in `satisfiability/heuristics.py`.
2. **Binary search** over k in [lower, upper]: encode "MOSP ≤ k?" as CNF and
   solve with **Kissat404** (see [SAT backend](#sat-backend)). Each instance is
   [reduced first](reports/preprocessing_measurements.md) — split into the
   components of its MOSP graph, with dominated products dropped.
3. The smallest satisfiable k is the exact optimum. If the bounds already meet,
   the heuristic ordering is optimal and no SAT call is made.
4. **Verify** by simulating the production sequence on the witness ordering.

### SAT Encoding

Position-based formulation with three variable families:

| Variable | Meaning |
|---|---|
| `x[p,t]` | Pattern p is placed at position t |
| `y[p,t]` | Pattern p is placed by step t (prefix) |
| `o[c,t]` | Customer c's stack is open at step t |
| `any[c,t]`, `all[c,t]` | Auxiliaries for the open-stack condition |

Full formulation with the constraints in LaTeX, the reasoning behind the
auxiliary variables, and measured formula sizes:
[`reports/encoding.md`](reports/encoding.md).

**Constraints:**
- **Permutation**: each pattern exactly one position, each position exactly one pattern (at-least-one + ladder at-most-one)
- **Prefix linking**: `x[p,t] -> y[p,t]`, monotonicity, converse (including t=0 base case)
- **Open stack forcing**: (a) `x[p,t] -> o[c,t]` for each pattern p of customer c; (b) `y[p,t] -> any[c,t]`, `all[c,t] -> y[p,t]`, and `any[c,t] AND NOT all[c,t] -> o[c,t]`
- **Width bound**: at most k open stacks per step (totalizer cardinality constraint)
- **Symmetry breaking**: pattern with most customers in first half of positions

Constraint (b) costs `2|P_c| + 1` clauses per (customer, step). Writing it
directly over pairs of c's patterns instead -- `y[p,t] AND NOT y[q,t] -> o[c,t]`
-- costs `|P_c|(|P_c| - 1)`, which on dense instances dominates the entire
formula: GP5 (100x100, customers needing nearly every pattern) encoded to 76.7M
clauses and cost 10.3 GB and 60s to build, against 3.25M clauses, 461 MB and
2.3s now. Only the polarities above are needed; neither auxiliary is pinned to
its full definition, but `any` occurs negatively in the forcing clause so it
stays false unless some `y[p,t]` forces it true, and `all` occurs positively so
it goes true whenever every `y[p,t]` allows. So `o[c,t]` is forced exactly when
the customer is genuinely open, never spuriously -- which would over-tighten the
width bound. The pairwise form is retained behind `pairwise_open_stacks=True`
and both are tested against exhaustive search.

### The customer search

Chu & Stuckey (2009) search the space of orders in which customer stacks *close*,
rather than the space of product sequences. Their Table 1 is why it is here:
their complete search closes the 125-customer instances at density 6, 8 and 10 in
**9 s, 0.19 s and 0.02 s** — the densities holding most of our open gap, and
exactly where SAT refutations never return.

A state is the set `S` of closed customers; `O(S)` is what has been opened.
Closing `c` costs `|O(S ∪ {c}) − S|`. The search is pruned by three dominance
relations, none of which can be written as clauses, because every one conditions
on the partial sequence already committed:

- **subset** — if `o(cᵢ,S) ⊆ o(cⱼ,S)`, closing `cᵢ` first is never worse, so `cⱼ`
  leaves the candidate set;
- **definite move** (their Theorem 1) — if `close(q,S) ≥ open(q,S)`, playing `q`
  now is always at least as good, so *every* sibling branch goes;
- **old move** (their Theorem 3) — a move already searched at an ancestor, whose
  reinsertion there stays playable, has been seen;
- **better move** (their Theorem 2) — if `S ++ [q]` and `S ++ [r, q]` are
  playable and `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})`, then `r` goes. This one
  is `O(|R|³)` per node against Theorem 1's `O(|R|²)` and is switched on **only
  for sparse instances**, where it is worth up to 300×; see below.

Running it over the instances whose optimality was open — 900 s each, 20 workers
— **closed 111 of 147 in 45 minutes**:

| | proved | stacks saved |
|---|---|---|
| density 10 | **30 / 30** | 22 |
| density 8 | **29 / 31** | 31 |
| density 6 | 24 / 32 | 35 |
| density 4 | 15 / 29 | 38 |
| density 2 | 11 / 21 | 28 |
| SP and other | 2 / 4 | 10 |
| **total** | **111 / 147** | **164** |

That gradient is their Table 1 reproduced on this corpus. 87 instances also had
their upper bound improved on the way, since a descent that fails to close still
ratchets. SP3 closed at its published optimum of 34 in 71 seconds, a refutation
an eight-backend SAT portfolio had been running for hours without an answer.

The rules are worth less here than their paper suggests, and the reason is worth
recording: on SP3's refutation the **memo** is what makes the call land at all,
while the subset and definite-move rules cut nodes 2.3× and time only 1.2×,
because they cost about twice per node what they save in nodes. Their Table 4(a)
measures a C++ search where per-node arithmetic is nearly free. Full ablation in
[`reports/customer_search.md`](reports/customer_search.md).

#### The C port, and why Theorem 2 is conditional

`satisfiability/customer_search.c` is the same search in C, called through
`ctypes`, about **120× faster** — two million branch decisions a second against
nineteen thousand. It visits *the same nodes in the same order*: the counts match
the Python instance by instance, which is the sharpest available evidence that it
is the same search and not merely a similar one. The Python stays the reference,
`native=False` forces it, and the C declines rather than guessing when it is out
of range (more than 128 customers, or a rule it does not implement).

Theorem 2 exists only in the C, and whether it pays **inverts with density**:

| products per customer | nodes without | with Theorem 2 | verdict |
|---|---|---|---|
| 2.6 (an open instance) | 263,000,000+, unresolved | **885,759** | closed it, in 3 s |
| 2.3 | 7,327,112 | **55,424** | 15× faster |
| 6.2 | 11,800,509 | 7,211,993 | 0.44×, a clear loss |
| 8.3 | 4,407,437 | 3,437,570 | 0.47×, a clear loss |

It ranges over *pairs* of candidates, so it repays its cubic cost only where many
candidates stay playable at each step — which is exactly what sparsity means
here. `sparse_enough_for_better_move()` picks it per instance at a measured
threshold of 5.0 products per customer, and the open instances separate cleanly:
none sits between 4.85 and 5.70.

The first row is the result that mattered. That instance had consumed 263 million
branch decisions in 180 seconds without resolving; with Theorem 2 it closed in
three. Eight more fell in the first 28 seconds of the sweep that followed.

## Lower bounds

The lower bound decides which decision problems the solver poses, and the
expensive ones are refutations at values *below* the optimum — exactly what a
weak bound fails to rule out. Three are available, two cheap and one not.

Computed on the MOSP graph (nodes are customers, an arc iff some pattern is
required by both):

- **Maximum clique.** Any clique forces that many simultaneously open stacks:
  take the member that closes earliest; every other member shares a pattern with
  it, that pattern is produced by the time it closes, so all of them are open at
  that step. Proved directly, with no appeal to pathwidth. Subsumes the "maximum
  customers per pattern" bound, since each pattern is itself a clique.
- **Contraction degeneracy** (MMD+, least-c). Stronger, but rests on
  `MOSP = pathwidth + 1` rather than a direct argument, so it is validated
  against every known optimum rather than assumed.

Measured over 900 solved instances:

| bound | mean gap to optimum | tight | max gap |
|---|---|---|---|
| max customers per pattern (Yuen & Richardson 1995) | 5.58 | 1.2% | 19 |
| maximum clique | 2.02 | 36.9% | 13 |
| **contraction degeneracy** | **0.54** | **63.4%** | **5** |

The two are complementary by density: clique carries the dense instances,
contraction the sparse ones. On GP5–GP8 both are exactly tight, so no refutation
is needed at all. Full analysis in [`reports/lower_bounds.md`](reports/lower_bounds.md).

### Bounds by contraction (expensive, and much stronger)

Contracting an edge of the MOSP graph — OR-ing two rows that share a product —
*relaxes* the instance, so the optimum of a contraction is a certified lower
bound on the original's (Chu & Stuckey's Lemma 1). Solving a contraction outright
therefore buys a bound for the price of a smaller search:

| instance | ub | clique + degeneracy | by contraction | at | time |
|---|---|---|---|---|---|
| SP4 | 57 | 27 | **45** | 78 of 100 customers | 94 s |
| Random-125-125-4-1_0 | 63 | 27 | **39** | 78 of 125 | 59 s |
| Random-125-125-2-1_0 | 28 | 13 | **16** | 76 of 125 | 79 s |

The method has a knee rather than a dial. Contracting all the way down to `ub` is
worse than useless — it returns 9 against an existing bound of 13 on the
density-2 instance — and the level above the useful band times out. Details and
the driver that tries to close instances with it (which does not work, for a
reason worth reading) in [`reports/relaxation.md`](reports/relaxation.md).

## Preprocessing

Two of the six operations catalogued by Yanasse & Senne (2010) are implemented in
`mosp/preprocess.py` and applied on every SAT decision call:

- **component decomposition** — the components of the MOSP graph share no
  customer and no product, so `MOSP(I) ≤ k` exactly when every component
  satisfies it, and each is encoded separately;
- **pattern dominance** — a product whose customers are a subset of another's is
  dropped and reinserted next to its dominator afterwards, at no cost.

Both preserve the optimum, so a refutation on the reduced instance refutes the
original. Firing rates over the 6,376-instance tree: dominance on 3,409 of them
(17,699 columns removed), decomposition on 154. On the instances that are
actually hard the rates are 93 and **zero** — Chu & Stuckey deliberately discard
decomposable instances from their generator's output.

A third operation, **contraction**, does *not* preserve the optimum and is kept
separate; it is the relaxation above. Measurements of what contraction plus
column dedupe does to formula size are in
[`reports/preprocessing_measurements.md`](reports/preprocessing_measurements.md).

## Upper bounds

`satisfiability/heuristics.py` registers six strategies behind one signature, so
they can be compared on the same instances:

| strategy | what it is |
|---|---|
| `tabu` | swap-move tabu search over raw product permutations |
| `mcn` | least cost node (Becceneri 1999): minimum-degree elimination on the MOSP graph |
| `mcn+tabu` | MCN to construct, tabu to improve — the default |
| `customer-tabu` | tabu search over *customer closing orders* rather than product orders |
| `cs-dfs` | Chu & Stuckey's `ub_MOSP`: DFS over closing orders, branching only on customers already open |
| `customer-tabu+cs-dfs` | tabu first, then the DFS pruning against its result |

`cs-dfs` is the one to reach for. Run once over the 148 instances whose
optimality was then open, it improved 25 of them **in 3 seconds** — on top of
what two hours of seeded `customer-tabu` sweeps had already taken.
[`reports/ub_mosp_search.md`](reports/ub_mosp_search.md) has the comparison; it
does not dominate `customer-tabu`, so both are kept and saves are monotone.

## SAT backend

`benchmarks/solver_portfolio.py` times all 19 working pysat backends on hard
instances, in both directions separately, with known optima as ground truth.
On the refutation at k-1, which is what decides an instance's runtime:

| backend | refutations closed |
|---|---|
| **Kissat404** (in use) | **6/6** |
| Cadical300 | 4/6 |
| Cadical153 | 3/6 |
| cd195 (previously in use) | 2/6 |
| Glucose / Minisat family | mostly 1/6 |

No backend gave a wrong answer in 228 trials. The choice is a named constant,
`satisfiability.mosp_solver.SAT_BACKEND`; re-run the portfolio before changing it.

## Visualising a solution

`mosp/visualize.py` draws a solution two ways.

**`plot_gate_matrix`** is the packed gate matrix layout of Linhares & Yanasse
(2002), Fig. 2(c). Gates are vertical wires, one per pattern in production order;
nets are horizontal wires, one per customer, running from the first gate it needs
to the last, with a dot at each gate it actually connects to. Nets are **packed
into tracks**, so customers whose stacks never overlap share a physical row.
Their Proposition 2 is that open stacks equal tracks, which makes the count
immediate: the number of rows *is* the answer. Per-gate open-stack counts run
along the bottom, pattern indices along the top.

**`plot_solution`** is the unpacked fill-in matrix — one row per customer, each
row's zeros filled between its first and last 1 — which shows the staircase
structure rather than the compressed circuit.

```bash
python -m mosp.visualize SP2 --out sp2.png      # any cached solution
python -m mosp.visualize GP5 --colors 5         # 5 or 10 cycling colours
```

`figures/*_gatematrix.png` holds the packed layouts for the published instances.

Rows cycle through a small palette and are drawn with a gap between them, so
open stacks in a column can be counted by eye. Rows are sorted by opening step
into the staircase form the gate-matrix literature draws; that is cosmetic, since
reordering rows cannot change a column sum. Steps attaining the peak are shaded.

`plot_comparison` draws several solutions side by side on a shared vertical
scale, so the fraction of customers open at once is comparable between panels.
`figures/density_contrast.png` uses it on SP2, GP4 and GP1 — all 50x50, so only
density varies — and the progression from a sparse staircase to a near-solid
block is the visual reason dense instances have so little to optimise, their
optima running 19, 30, 45 of 50 customers.

Note that two different densities get called "density" in this literature. The
figures report both: the fill rate of M, and the edge density of the MOSP graph.
Frinhani et al. (2018) tabulate the latter — their D of 0.21 for SP2 is the graph,
whose matrix is only 7% full.

## Validation Against Published Optima

**Why only these instances.** Per-instance optimal values are barely published in
this literature. Frinhani et al. (2018) tabulate 21 of them; Chu & Stuckey (2009)
confirm SP2, SP3 and SP4. For their 200 random instances, Chu & Stuckey state
that their method "finds and proves the optimal in all cases" but report node
counts, times and average deviations rather than the values themselves. So for
the other ~6,200 instances solved here, **there is nothing published to compare
against** — not because nobody solved them, but because nobody tabulated them.
That is the gap the witness orderings in `solutions/` are meant to fill.

| Instance | Size | Published | Ours | Status |
|---|---|---|---|---|
| GP1 | 50×50 | 45 | 45 | certified |
| GP2 | 50×50 | 40 | 40 | certified |
| GP3 | 50×50 | 40 | 40 | certified |
| GP4 | 50×50 | 30 | 30 | certified |
| GP5 | 100×100 | 95 | 95 | certified |
| GP6 | 100×100 | 75 | 75 | certified |
| GP7 | 100×100 | 75 | 75 | certified |
| GP8 | 100×100 | 60 | 60 | certified (by a tight bound) |
| Miller | 20×40 | 13 | 13 | certified |
| NWRS1–8 | 10×20 … 25×59 | 3, 4, 7, 7, 12, 12, 10, 16 | all match | certified |
| SP1 | 25×25 | — | 9 | certified (no published value) |
| SP2 | 50×50 | 19 | 19 | certified |
| SP3 | 75×75 | 34 | **34** | **certified** |
| SP4 | 100×100 | 53 | **53** | solution; optimality unproven |

**All twenty published values are matched, and none disagrees.** SP3 and SP4 were
the two long-standing exceptions and both are now resolved in value; SP3 is also
proved.

SP3 is worth recording as a before-and-after. Under the SAT engine a single
satisfiable call at `k=34` ran for **45,071 seconds — 12.5 hours — without
returning**, after a descent that had reached 35 through calls of 42 s, 404 s and
3,084 s; a later eight-backend portfolio spent hours on the same question. The
customer search settles it, refutation included, in **71 seconds**.

A caution on what this establishes: the published values are themselves
uncertified, so agreement is mutual corroboration rather than proof that either
side is right — which is the argument for shipping checkable witnesses. The
literature records a case in point: Yanasse & Senne (2010) note that later
authors found *better* solutions than Faggioli & Bentivoglio's (1998) **exact**
method reported, and conclude its implementation was faulty.

"Certified" means optimality was established: satisfiable at k with a witness
ordering and unsatisfiable at k−1 — or, where the lower bound already equals the
optimum, a satisfiable call alone, which is how GP8 was settled. Witness
orderings are cached in `solutions/` and can be re-checked independently of any
solver by simulating them with `mosp.verify.max_open_stacks`.

### Corpus

The full benchmark tree has been swept. Of 6,376 cached solutions — one per
instance, with no file matching none:

| provenance | count | share | meaning |
|---|---|---|---|
| `certified:refutation` | 6,347 | 99.55% | satisfiable at `k` with a witness, unsatisfiable at `k−1` |
| `certified:bound` | 2 | 0.03% | satisfiable at `k`, and the lower bound already equals `k` |
| **certified, either way** | **6,349** | **99.58%** | **an optimality claim** |
| `solution` | 27 | 0.42% | a witness of value `k` and nothing more; optimality open |

Every file records which it is, because a corpus that cannot distinguish a proof
from a good guess is a liability. Both kinds are equally checkable as *upper*
bounds — the witness verifies either way — but only the first is an optimality
claim, and they must not be added together.

The 27 uncertified files cover **26 distinct
instances**, all sparse — the densest left open is 8.2 products per customer,
and density 10 has none. SP4 is still among them: its value of 53 matches the
published optimum and its certified lower bound is 46, so the gap is 7, but the
refutation that would close it has not landed.

Four further files used to sit here: `GP1.json`–`GP4.json`, written by
`validate_published_optima.py` under a name `from_benchmark_file` never
produces. Matching no enumerated instance, they were invisible to every sweep,
so no later run could upgrade their provenance, and they read as four open
problems that were in fact certified twice over under their real names. They are
deleted and the script no longer creates them.

All 6,376 witnesses re-simulate to their recorded value, with zero disagreements
across every instance and every pass.

### What it cost

**About a day on 25 cores** — 588 core-hours, 24.5 core-days of recorded solver
time, totalled from the result CSVs and the ledger the parallel drivers append
to:

```bash
python -m benchmarks.compute          # the breakdown
python -m benchmarks.compute --quote  # the line quoted here
```

Quote it in that order and never the days alone: "about a day" is what a reader
wants, and is meaningless without the core count beside it, since the same work
is a day on 25 cores and 24.5 days on one. The core-hours are the invariant, and
the figure to compare between runs.

It counts only instances a run wrote a row for, so it is a lower bound on
compute spent — the right direction for a cost figure to err in.

Where it went is the more interesting part. The largest single line is 223
core-hours on one overnight SAT round; the customer search closed 111 instances
for 11 core-hours. The cheap wins came from matching the algorithm to the
instance shape, not from spending more.

## Checking the claims without trusting this code

An optimality claim here is two statements, and they are not equally easy for
someone else to check.

**`MOSP(I) ≤ k`** is witnessed by an ordering. Checking it means simulating that
ordering against the instance file and counting open stacks — no SAT solver, no
encoding, none of this code. `mosp/certify.py` does it with an implementation
deliberately sharing nothing with the solver, because a checker built on the same
code checks less than it appears to:

```bash
python -m mosp.certify check SP2     # one instance
python -m mosp.certify check         # every cached solution
```

All **6,376** cached witnesses pass. Re-implementing this checker in another
language is an afternoon's work, and doing so would remove this project from the
trust chain entirely for this half of the claim.

**`MOSP(I) > k−1`** is harder, and the two engines are in different positions:

- A **SAT refutation** rests on a solver reporting the CNF unsatisfiable, so
  re-running our code reproduces our result *including any bug in our encoding* —
  that is reproducibility, not verification. What can be done today is to export
  the formula and have it refuted by somebody else's solver:

  ```bash
  python -m mosp.certify export SP2 --k 18 --out sp2_k18.cnf
  ```

  UNSAT at `k−1` from an independent solver, plus a witness at `k`, is the
  optimality claim. That narrows what must be trusted to one question: whether
  the encoding faithfully expresses MOSP — which the Lean development answers.

- A **customer-search refutation** has no such artifact. It is a claim that a
  pruned search space was exhausted, and its soundness rests on the dominance
  relations above. There is no CNF to hand to another solver and no proof log.
  This is the newest and least-certified part of the project, and it now accounts
  for a large share of the corpus, so what stands behind it is stated plainly:

  - the unsat/sat flip point equals the brute-force optimum on hundreds of small
    instances, under **every combination of the pruning rules, varied one at a
    time**;
  - **700 instances beyond brute-force reach agree exactly with the SAT engine**,
    which shares no code with it;
  - all twenty published optima reproduce;
  - a budget abort returns "unknown", never "unsat", and is kept out of the memo,
    where it would turn one timeout into a permanent false refutation;
  - every one of the 111 optima it certified in the corpus sweep was re-verified
    afterwards by asking the refutation again from scratch — 111 checked, 0
    failed.

  That is evidence, not proof. Giving this engine a checkable proof object is
  open work.

### A third solver, as an outside check

Both engines above were written for this project, so their agreement is weaker
evidence than it looks, and the customer search's refutations carry no proof
object at all. `benchmarks/oracle_sweep.py` runs a third solver against the
corpus: Martin, Yanasse & Pinto's (2022) CP model under CP-SAT, in its own
interpreter (`.venv-cpsat`), importing nothing from this project.

Over **every certified optimum**, 300 seconds each, 25 workers, 4.5 hours:

| | count | share |
|---|---|---|
| CP-SAT proved the same optimum | **5,266** | 82.9% |
| CP-SAT disagreed | **0** | — |
| CP-SAT could not settle in 300 s | 1,083 | 17.1% |

So five sixths of the corpus is confirmed by three independent solvers — this
project's SAT encoding, its customer search, and an outside solver running a
different formulation in a different process. A transcription error, an encoding
bug or an unsound dominance rule would have to survive all three.

The 1,083 are the large instances, and they are where the confirmation is
thinnest precisely because they are where our own search is least checkable.
Its authors predicted this: they report the model as weakest on instances with
many patterns and strongest on dense MOSP graphs.

This is corroboration, not proof. Three solvers agreeing is not a certificate a
stranger can check without running anything, which is what the two routes below
would give.

Two routes would close the remaining gap for the SAT half, and neither is done:

- **proof logging** — emit a DRAT refutation checkable by a verified checker such
  as `cake_lpr`. Measured at roughly 10 MB of proof per second of solving, which
  puts the easy 94% of the corpus at about 7.5 GB and the whole of it past a
  terabyte. Shelved on those grounds — though contraction (above) makes the
  refuted instances much smaller, which changes that arithmetic.
- **the Lean formalization** — prove the CNF satisfiable iff `MOSP(I) ≤ k`.
  **Done**, in `lean/MOSPFormalization/Encoding.lean`, with no `sorry` and no
  axioms beyond `propext`, `Classical.choice` and `Quot.sound`. What remains is
  narrower than it was: that `mosp_encoding.py` emits the clauses the Lean
  development describes, and that the ladder and totalizer cardinality encodings
  it states by meaning are faithfully implemented.

So the honest summary: the upper bounds are checkable by anyone today; the SAT
lower bounds are reproducible, independently re-refutable, and rest on an
encoding proved faithful; and the customer-search lower bounds are heavily
cross-validated but carry no artifact a third party can check.

## Project Structure

```
satisfiability/                 -> the two exact engines, and the bounds
    mosp_encoding.py                Direct MOSP-to-SAT CNF encoding
    mosp_solver.py                  SAT engine: binary search, bounds, caching
    customer_search.py              Complete search over customer closing orders
    customer_search.c               The same search in C, about 120x faster
    native.py                       Loads the C port, and decides when to trust it
    cpsat.py                        Bridge to the CP-SAT oracle, in its own interpreter
    cpsat_oracle.py                 The Martin/Yanasse/Pinto CP model (runs in .venv-cpsat)
    relaxation.py                   Contraction relaxation: certified lower bounds
    heuristics.py                   Upper bound strategies behind one signature
    encoding.py                     Pathwidth CNF encoding (legacy)
    solver.py                       Pathwidth solver (legacy)

mosp/                           -> instances, checking, drawing
    instance.py                     Parse/represent MOSP instances (binary matrix)
    verify.py                       Simulate a production sequence, count open stacks
    certify.py                      Independent witness checking, CNF export
    preprocess.py                   Pattern dominance, decomposition, contraction
    visualize.py                    Packed gate matrix layout drawing
    agreement_graph.py              Pattern connection graph via M^T @ M (legacy)
    reduction.py                    Formal reduction: MOSP <-> pathwidth (legacy)
    solver.py                       End-to-end pathwidth pipeline (legacy)

customer_inter/                 -> Customer intersection graph approach (legacy)
    customer_graph.py               Build the MOSP graph via M @ M^T overlap
    reduction.py                    MOSP <-> customer-graph pathwidth reduction
    solver.py                       End-to-end pipeline using the MOSP graph
    compare.py                      Side-by-side comparison of graph formulations

fixed_parameter_algorithm/      -> Pathwidth solvers (used as subroutines)
    pathwidth.py                    Exact DP over vertex subsets (n <= 18)
    pathwidth_fpt.py                Branch-and-bound with iterative deepening
    path_decomposition.py           Extract path decomposition from ordering

benchmarks/
    csearch.py                      Parallel descent with the customer search
    marathon.py                     Deadline-sized budgets for long unattended runs
    corpus.py                       What the corpus claims, counted from the files
    oracle_sweep.py                 Checks the corpus against CP-SAT, an outside solver
    compute.py                      Totals the corpus's compute cost in core-hours
    compute.py                      Totals the corpus's compute cost in core-hours
    ratchet.py                      Descending satisfiable-call search
    reheuristic.py                  Re-run an upper bound strategy over the corpus
    solve_parallel.py               Parallel solving: across instances, and across k
    overnight.py                    Escalating-budget driver for unattended runs
    portfolio.py                    Races several SAT backends on one decision call
    solver_portfolio.py             Times every pysat backend on the hard calls
    dedupe.py                       Shares solutions between identical instances
    solve_all.py / solve_all_sat.py Batch solvers for the published files
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output
    instances/                      Published MOSP benchmark collections
        ChallengeInstances2005/         2005 Constraint Modelling Challenge
            Harvey/ Miller/ Shaw/ Simonis/ Wilson/
        MOSP_Instances/                 SCOOP dataset collection
            Challenge/ Chu_Stuckey/ Faggioli_Bentivoglio/ SCOOP/
    results/                        Benchmark result CSVs (tracked for regression)

solutions/                      Cached solutions with provenance (JSON)

lean/
    MOSPFormalization/              Lean 4 proofs: encoding faithfulness, VS = PW

reports/
    encoding.md                     The CNF formulation, and what is proved of it
    customer_search.md              The complete search, its rules, and the sweep
    relaxation.md                   Contraction: what it closes and what it gives
    preprocessing_measurements.md   What decomposition, dominance, contraction buy
    ub_mosp_search.md               The restricted DFS upper bound
    lower_bounds.md                 The clique and contraction degeneracy bounds
    chu_stuckey_plan.md             The plan the recent work follows
    fpt_theory_practice_gap.md      Why FPT tractability failed in practice

tests/                          471 tests across 26 test modules
figures/                        Gate matrix layouts for the published instances
literature/                     Reference papers
validate_published_optima.py    Batch validation against published optima
```

## Usage

### Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ with `networkx`, `numpy`, `python-sat`, `matplotlib`, and
`pytest`.

### Solve one instance

```python
from mosp.instance import MOSPInstance

instance = MOSPInstance.from_benchmark_file("path/to/instance.txt")[0]

# SAT engine: binary search over k, witness ordering over products.
from satisfiability.mosp_solver import solve_mosp_sat
value, ordering = solve_mosp_sat(instance)

# Customer search: descends k until it refutes. Try this first on dense
# instances -- it is the engine that closes them.
from satisfiability.customer_search import solve
from satisfiability.heuristics import product_order_from_customers
result = solve(instance, time_budget=600)
print(result.value, result.proof)          # 'refutation', 'bound', or '' (open)
ordering = product_order_from_customers(instance, result.order)
```

`result.proof` is empty when the budget ran out: the value is then an upper bound
worth keeping, not an optimality claim. The distinction is carried all the way
into `solutions/`.

### Solve many

```bash
# Customer search over everything still unproven
python -m benchmarks.csearch --unproven --timeout 900 --workers 20

# SAT engine, fanned out across instances
python -m benchmarks.solve_parallel sweep --workers 30 --timeout 300 \
    --output benchmarks/results/sweep.csv

# SAT engine, parallelising the binary search over k for one hard instance
python -m benchmarks.solve_parallel one GP5 --workers 28

# Improve upper bounds without re-solving anything
python -m benchmarks.reheuristic --unproven --strategy cs-dfs --workers 16

# Escalating budgets against whatever is still open (SAT path)
python -m benchmarks.overnight --rounds 3600,12000 --workers 30

# The customer search under a wall-clock deadline: one round, sized so that
# ceil(instances / workers) waves fill exactly the time given
python -m benchmarks.marathon --days 5 --workers 25
```

The solution cache is the state, so these need no bookkeeping between runs:
anything already solved is verified from disk in milliseconds and skipped, and
each run spends its budget only on what is still open. Saves are monotone in the
value and never demote a certified value to a bare solution — which matters,
because these drivers re-derive values earlier runs had proved.

`solve_parallel one` attacks a single instance. The sequential binary search
issues `log2(gap)` calls strictly in order, and its hardest call is almost always
the UNSAT proof at the optimum minus one — which it reaches *last*. Probing many
k at once starts that proof immediately; since SAT at k implies SAT at k+1, each
round cuts the live interval by a factor of `workers + 1` rather than 2.

### Certified lower bounds by contraction

```python
from satisfiability.relaxation import lower_bound
bound, groups = lower_bound(instance, target=78, time_budget=300)
```

### Validate and test

```bash
python validate_published_optima.py    # all published instances, stops on mismatch
python -m pytest tests/ -q
```

### Instance file formats

`MOSPInstance.from_file` reads this project's own single-instance `.mosp` format:

```
instance_name
n_customers n_patterns
<n_customers rows of n_patterns space-separated 0/1 values>
```

`MOSPInstance.from_benchmark_file` reads the published collections in
`benchmarks/instances/` and returns a **list** of instances, since many of those
files concatenate several instances (`Harvey/wbp_10_10.txt` holds 40). It handles
both layouts found there:

- **Format A** (`MOSP_Instances/`) -- one instance per file, leading `m n` line,
  matrix transposed to customers x patterns.
- **Format B** (`ChallengeInstances2005/`) -- multiple instances per file, optional
  description lines before each `m n` line, matrix already customers x patterns.

The format is auto-detected from the path; pass `transpose=` to override.

## Theoretical Foundation

The MOSP-pathwidth connection (Kinnersley 1992, Yanasse 1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

This equivalence is why the project started with pathwidth; both engines have
since moved off it, and it survives here as the justification for one lower
bound and as the subject of the Lean development. Two graph formulations appear
in this repository, and it is worth being precise about which one the
literature's equivalence concerns. Yanasse & Senne (2010)
defines both and calls them "completely different":

- **MOSP graph** -- nodes are *item types* (customers), an arc between two iff
  some pattern contains both (`M @ M^T`). A pattern with k items is a clique of
  size k. **This is the graph of the pathwidth equivalence**, due to Yanasse
  (1997c). Here: `customer_inter/customer_graph.py`.
- **Pattern connection graph** -- nodes are *patterns*, an arc between two iff
  they share an item type (`M^T @ M`). The literature uses it only to decompose
  an instance into independent clusters. Here: `mosp/agreement_graph.py`; the
  name "agreement graph" is this project's, not the literature's.

Earlier versions of this README attached the `pathwidth + 1` equality to the
agreement graph, which is the wrong object -- the undercounting measured there
is not a counterexample to Yanasse's result. Whether the equality is tight on the
MOSP graph is a question this project has not yet answered properly.

Neither engine depends on the resolution. The SAT encoding bypasses both
reductions, treating MOSP as a self-contained decision problem. The customer
search works on the MOSP graph — closing orders are orders on its nodes — but
uses it directly, not through pathwidth: its bound is the count of simultaneously
open stacks, which needs no equivalence to be argued.

### Formal Verification in Lean 4

The `lean/` directory contains a Lean 4 formalization covering two things: the
pathwidth theory this project started from, and — since the solver no longer
relies on that reduction — the SAT encoding it actually uses. It is a work in
progress; what is complete and what is not is set out below.

**Complete (no `sorry`):**

- **The SAT encoding is faithful** (`Encoding.lean`, stated in full in
  [`reports/encoding.md`](reports/encoding.md)):
  `(∃ a, Encodes M k a) ↔ M.mospValue ≤ k`. Left to right is what licenses
  reporting a refutation as a proof of optimality — if the formula is
  unsatisfiable then no production sequence achieves `k`. Right to left says the
  encoding never excludes a sequence that exists. Depends on no axioms beyond
  `propext`, `Classical.choice` and `Quot.sound`.

  Two constraint families are stated by their meaning rather than their clause
  form: at-most-one for positions, and at-most-`k` for open stacks. Both are
  standard cardinality encodings whose correctness is independent of MOSP. What
  *is* modelled in full is the open-stack forcing, which is the MOSP-specific
  part and the part our implementation has actually got wrong before.


- **Vertex separation = pathwidth** (Kinnersley 1992), in `VSEquivPW.lean`: proven in both directions via explicit constructions (`LayoutToDecomposition.lean` and `DecompositionToLayout.lean`).
- Supporting definitions and lemmas: linear layouts, vertex separation, path decompositions, pathwidth, MOSP instances, open-stack counting.
- `Examples.lean`: small concrete instances checking that the agreement-graph and open-stack *definitions* behave as intended. No instance is solved inside the proof assistant -- pathwidth is defined via `sInf` and is noncomputable.

`MOSPFormalization/Check.lean` cross-checks the open-stack definition against
what `mosp/verify.py` reports on small instances, by `decide`. That check earned
its place immediately: `isActive` required a pattern *strictly* after position
`i`, so a stack closed one step before its last pattern was produced, and on one
customer needing one pattern Lean gave 0 where the implementation, the
independent checker and the literature all give 1. The definition is now
inclusive at both ends, matching Yanasse & Senne's fill-in matrix.

**Incomplete (2 `sorry`s, both in `Reduction.lean`):**

- `openStacksAt_le_bag_card` -- the core injection step, which needs Hall's marriage theorem under the `IsReduced` hypothesis.
- `exists_instance_achieving_equality` -- the tightness direction.

What is stated in Lean is the one-sided bound `mospValue <= pathwidth + 1` (`mosp_le_pathwidth_add_one`, for `IsReduced` instances), and it currently rests on the first `sorry`. **Equality is not proven, and is not expected to hold in general** -- measurements on real instances (recorded in `CLAUDE.md`) show `pathwidth` of the pattern connection graph, plus one, undercounting the optimum, and the same quantity on the MOSP graph overcounting it. Closing the tightness `sorry` would require the reduced-instance hypothesis to do real work.

The formalization includes candidates for contribution to Mathlib (`ForMathlib/`).

Building requires `elan`/`lake` with the toolchain pinned in `lean/lean-toolchain`:

```bash
cd lean && lake build
```

## Known Limitations

- **35 instances remain open** — 34 sparse Chu & Stuckey `Random` instances and
  SP4. They have witnesses, and in SP4's case a witness at the published optimum
  of 53; what is missing is the refutation. Densities 2 and 4 account for 24 of
  the 34, the regime where both engines are weakest and the bounds loosest.
- **The customer search produces no checkable proof object.** Its refutations are
  claims that a pruned space was exhausted, backed by extensive cross-validation
  against the SAT engine, brute force and the published optima — but there is no
  CNF to re-refute and no proof log. It now accounts for a large share of the
  certified corpus, which makes this the project's biggest open verification gap.
  See [Checking the claims](#checking-the-claims-without-trusting-this-code).
- **Nothing races the two engines.** They fail on disjoint sets, and a portfolio
  over one decision call would be a small change with a large expected gain. Not
  built.
- **The relaxation driver cannot close instances**, only tighten bounds. It tries
  to refute `ub − 1` on a contraction, which can only succeed when `ub` is
  already the true optimum — and on the sparse instances it was being asked about,
  it was not. Partial relaxation (the bounds table above) is the part that works.
- **Theorem 2 is off on dense instances, by measurement**, where it costs about
  2.2×. It is on for everything below 5.0 products per customer, where it is
  worth up to 300×. The threshold was calibrated on completed refutations;
  comparing configurations on instances that never finish cannot settle it,
  since node counts mislead when better pruning visits fewer nodes by design.
- **Four of the six Yanasse & Senne preprocessing operations are still
  unimplemented**, and decomposition never fires on the instances that are hard.
- **The contraction degeneracy bound is validated, not proved.** It rests on
  `MOSP = pathwidth + 1`, so a bound that were too high would make the search
  start above the true optimum and return a wrong answer that still passes
  witness verification. Checked against every known optimum with zero violations,
  and re-checked by `tests/test_lower_bounds.py` — evidence, not proof.
- **Lemma 1 (contraction relaxes) is measured, not proved here.** 3,167
  contractions with no violation, and the reverse operation — merging two
  customers that share no product — really does break it, at 17 violations in
  1,044. The proof is attributed to Becceneri, Yanasse & Soma (2004), which this
  project does not have.
- **The arc contraction bound of Yanasse, Becceneri & Soma (1999) is
  unobtained**, and may be the same bound as contraction degeneracy. *Pesquisa
  Operacional* is digitised only from 2001. No novelty should be claimed until
  this is settled.
- **The Lean formalization is incomplete** for the pathwidth reduction (2
  `sorry`s), though the part the SAT solver actually relies on — encoding
  faithfulness — is complete. Nothing in Lean covers the customer search.
- **The pathwidth code paths are legacy.** `mosp/solver.py`, `customer_inter/`,
  `fixed_parameter_algorithm/` and `satisfiability/solver.py` are retained for
  comparison and for the analysis in `reports/`. Their measured disagreement with
  published optima should be read against the graph correction in
  [Theoretical Foundation](#theoretical-foundation).
- **The binary search discards learning between k values**, re-encoding and
  re-solving from scratch at each step. Incremental SAT with assumptions would
  carry learned clauses across the search.

## References

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463.
- **Linhares, A. & Yanasse, H.H.** (2002). Connections between cutting-pattern sequencing, VLSI design, and flexible machines. *Computers & Operations Research*, 29, 1759-1772.
- **Chu, G. & Stuckey, P.J.** (2009). Minimizing the maximum number of open stacks by customer search. *CP 2009*, LNCS 5732, 242-257.
- **Frinhani, R.M.D. et al.** (2018). A PageRank-based heuristic for the minimization of open stacks problem. *PLOS ONE*, 13(8), e0203076.
- **Yanasse, H.H. & Senne, E.L.F.** (2010). The minimization of open stacks problem: A review of some properties and their use in pre-processing operations. *European Journal of Operational Research*, 203(3), 559-567. (*)
- **Martin, M., Yanasse, H.H. & Pinto, M.J.** (2022). Mathematical models for the minimization of open stacks problem. *International Transactions in Operational Research*.

## License

MIT, for everything here including the Lean development — see
[`LICENSE`](LICENSE), and 2026 throughout. Note that Mathlib requires Apache 2.0 on contributions, so
the three files under `lean/MOSPFormalization/ForMathlib/` would need that header
restored before being offered upstream.
