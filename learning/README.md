# Learning from the solved instances — in plain English

*Rewritten 2026-09-26 after three unattended loops (26 report sections). The
full account with every number is `reports/ml_nature.md`; the one-page version
is `reports/ml_nature_summary.md` §0; this file is for someone who has never
opened either.*

## The situation

This project has solved 6,376 scheduling puzzles and *proved* that each answer
is the best possible. Each comes with the schedule that achieves it. That is a
large pile of worked examples with the answers in the back of the book, and
this folder started by asking whether a machine learning model could look at
the pile and learn anything we did not already know.

The puzzle, briefly. A factory has a list of products to make and a list of
customers, each waiting on some subset of those products. A customer's "stack"
opens when the first product they want gets made and closes when the last one
does. Make the products in a bad order and dozens of stacks sit open at once,
each taking floor space. The question is what order to make things in so that
the worst moment is as good as it can be. It is NP-hard: nobody knows a
shortcut. Mathematically, the answer is a property of a graph — join two
customers whenever they share a product, and the best possible number of open
stacks is that graph's *pathwidth* plus one. Most of what follows is about that
graph.

## The one safety rule

There are two ways a model could feed into the solver, and only one is safe.

**Unsafe: letting a model guess how good the answer will be.** The solver
starts its search from a "lower bound" — a proved statement that the answer is
at least such-and-such. If that number is ever too high by even one, the solver
starts above the true answer, finds something that works there, and reports it
as optimal. The schedule it hands back genuinely achieves the number it claims,
so checking the schedule does *not* catch the error. A guess dressed up as a
bound would break the solver silently. Nothing in this folder does it, and
nothing here touches the code that decides what value to try.

**Safe: letting a model propose a schedule.** A schedule can be simulated
directly — run the products in that order, count the stacks, done. A bad
proposal costs a little quality and nothing else.

Two further rules grew out of the work and are now fixed: **count nodes, not
seconds** (at small sizes the clock does not see hardness at all, and on a
busy machine it invents speed-ups that are not there), and **say what sizes a
conclusion covers** (almost everything solved cheaply has 40 or fewer
customers; the instances that cost a day have 125, and a result at 40 is
evidence about 125 only through an extrapolation that says so).

## What this folder is for

**It is a measuring instrument, not a part of the solver.** The original idea
was that learning from the solved puzzles would make the solver faster. It does
not — three separate attempts, three measured negatives, all in
`reports/learned_search.md`. The expensive part of proving an answer optimal is
showing that one-better is impossible, and better guesses do not help with
that.

But every time the folder has been pointed at the solver or at the problem, it
has found something true that nobody knew. The list below is what three loops
of that produced.

## What we found

Numbers are rounded here; the section of `reports/ml_nature.md` in brackets has
the exact ones and the command that regenerates them.

### About the pile itself

- **It is smaller than it looks.** The 6,376 instances are only 3,667 distinct
  graphs; two in five are copies of another under renamed customers, and a
  quarter are "complete" graphs where every customer meets every other and the
  answer is trivially the number of customers (§1). Any honest test has to
  keep copies together on one side of the split.
- **You can tell which generator made an instance from its shape alone**, 94%
  of the time (§2). So a result on one benchmark family says little about
  another. The instances that are actually hard — Chu & Stuckey's sparse
  random ones — and the only real industrial instances both sit in the same
  sparse corner.
- **Small instances are free.** We can generate and solve a random instance
  with 40 customers in a fraction of a second, so the questions about what
  happens "on average" were answered on 37,800 generated instances, later
  extended to 75 customers with 6,750 more and to a handful at 100 (§9, §10,
  §16). Everything about them regenerates from a manifest of seeds.

### About the answer

- **The answer is squeezed between two simple graph numbers.** Two textbook
  quantities, the graph's *degeneracy* and a *bandwidth* estimate, satisfy
  `degeneracy + 1 ≤ answer ≤ bandwidth + 1` on every instance we have (§5,
  §12). Both inequalities are now **proved theorems** in the project's Lean
  development, for every finite graph (§26). The one step still taken on trust
  is the classical result that the answer equals pathwidth plus one.
- **The best single guess is a treewidth heuristic.** Add one to the min-fill
  treewidth estimate and you hit the exact answer on 86% of the corpus — better
  than either of the solver's own proved bounds — up to about 50 customers. At
  125 it is four stacks high (§4, §14). It is a guess, not a bound: it sits
  below the answer on 481 instances and above on 428.
- **On random instances the answer barely varies.** Fix the size and density
  and the optimum is two or three adjacent integers; its mean is a straight
  line in the number of customers (§12). A formula for that mean fits to half a
  stack at 40 customers and drifts off at 125 on the sparsest class (§14).

### About why the solver's bound fails

- **The bound fails for a structural reason.** Three of its four ingredients
  are really bounds on *treewidth*, and on about half of the 338 instances
  where the bound is two or more too low, pathwidth is provably larger than
  treewidth — so no amount of tuning those ingredients could ever close the
  gap (§6, §21). The instances look like small cliques glued at a few hub
  customers into a branching tree, with a fringe of customers who want only
  one product.
- **The smallest such graph has 10 vertices.** A search with the exact solver
  as oracle found a 10-vertex graph whose pathwidth exceeds its treewidth by
  two, proved it minimal, and showed the corpus's small instances are not the
  worst possible on any measure but soundness (§21).
- **Computing treewidth exactly would help; no new formula does.** Exact
  treewidth plus one beats the solver's certified bound on 933 corpus
  instances. A search over 11,589 candidate formulas found nothing that beats
  the better of the two proved bounds anywhere treewidth is known exactly — a
  formula fitted to look valid on 51,000 instances leaks 77% of the time when
  its constant is refit on a subset (§24). The bound work needs a new idea,
  not a new formula.

### About what makes an instance hard

- **Hardness has a ridge.** At fixed size, the work to prove an answer optimal
  rises and falls with density by a factor of a hundred each side of a peak,
  and on the peak it doubles every three customers (§11). Chu & Stuckey's
  "density 2" classes — the ones that take a day at 125 × 125 — sit exactly on
  it.
- **The ridge is at a simple place.** It sits where the products, counted as
  cliques, carry about twice the mass of a spanning tree — one independent
  cycle of the customer–product incidence graph per customer — at every ratio
  of products to customers tried, from eight times fewer products than
  customers to twice as many (§25). Mean degree, the obvious candidate, is not
  it.
- **The growth rate slows a little with size.** Fitted at 15–40 customers the
  ridge law overshoots at 125; the rate falls by about 0.002 (in log10 nodes
  per customer) for every ten customers, and corrected for that the law
  predicts the two day-long 125 × 125 counts on record to within a factor of
  1.1 (§14, §16). The revised central estimate is 1.5 × 10¹¹ nodes per
  density-2 refutation, with a factor of six either way.
- **Only the graph matters — and how you label it.** Two matrices with the
  same customer graph but different products cost the search *exactly* the
  same number of nodes (15,900 pairs, zero exceptions). Renaming the customers,
  on the other hand, moves the count by a few percent typically and up to
  eightfold (§13).
- **We can predict the cost within a factor of ten.** A censored regression on
  graph features, trained at up to 75 customers, puts 88% of the counts at
  100–125 within one decade of the truth and orders the remaining
  re-certification queue cheapest first (§19). A prediction, for planning
  only; never a bound.

### About whether the proofs are right

- **Every proof at 40 customers or fewer was checked twenty ways and held.**
  The same question asked under nine relabellings and one re-covering, under
  two search configurations, on 43,935 instances: 878,580 refutations, zero
  disagreements (§15).
- **The check found a bug anyway — on the other side.** Asked the *satisfiable*
  question at the optimum, one configuration of the C search said "impossible"
  on 56 instances. The stored answers were right; the pruning rule was wrong,
  in a way no earlier audit could see, because a proof that is one step too
  strong leaves the witness intact. The owner fixed it
  (`reports/better_move_bug.md` §7). Lesson: a refutation record should carry
  its satisfiable side too.
- **92% of the corpus at 40 or fewer now carries a proof a stranger can
  check.** The SAT encoding's refutation is logged as a DRAT proof and verified
  by an independent checker, drat-trim, from the formula alone; 5,646 of 6,135
  instances (§17). It costs thousands of times what the search costs, so it is
  an archive, not a decision procedure, and the encoding itself cannot reach
  125 × 125 at any width.
- **Above 40 customers, nothing outside the search checks a refutation.** That
  is the most important open item this folder has.

### About search rules, measured and not enabled

Each of these was measured behind a flag that defaults to today's behaviour.
None was switched on; that is the owner's call.

- **Trying equal-cost candidates in a different order** changes a refutation's
  node count by 0.0% at every size (§20). It does help the cheap satisfiable
  side (35% fewer nodes at 75 customers, with a tail that gets slower).
- **Racing sixteen relabellings on sixteen cores** wins nothing on refutations
  — the best of sixteen is 1% faster than the one you had — and the spread
  shrinks with size (§18). Again the satisfiable side is where it pays.
- **Chu & Stuckey's "Theorem 2" pruning rule**, currently on only for sparse
  instances, saves 7% of nodes if always on and costs 17% per node, so in
  seconds the current threshold is already in the right place (§22).

### About good schedules

- **A one-sentence rule beats the learned schedule-builder** (§7): *close the
  customer that opens the fewest new stacks; on ties, the one with the most
  unclosed neighbours.* Held out, it lands on the optimum 81% of the time
  against the learned model's 75% and the textbook rule's 50%, and it is the
  better starting point for the project's search.
- **The optimum is never unique**: typically 10⁵ optimal schedules at 10
  customers and 10¹⁰ at 15, never one (§8). So imitating "the" stored
  schedule step by step was imitating the solver's coin flips.
- **Imitation is closed.** Given the exact set of correct moves at every step
  as the target, the best model beats the rule by less than a hundredth of a
  stack; the rule is already right at 99.7% of decisions (§23).

## What is closed and should not be rebuilt

Learned upper bounds, learned lower bounds and learned branching inside the
search (`reports/learning_plan.md` §4); imitation of any kind (§7, §8, §23);
fan order and relabelling portfolios for refutations (§18, §20); a learned
switch for Theorem 2 (§22); formulas over degree statistics or over the thirty
branching invariants of §24 as new lower bounds; mean degree as the ridge's
location (§25); and any confidence interval calibrated at 40 customers quoted
at 50 or more (§14). Each has a section saying why, not only that.

## What is proposed and waiting on the owner

`reports/ml_nature_summary.md` §8 is the full table. The three with the most
in them: exact treewidth as one more ingredient of the solver's lower bound
(§24); the one-sentence rule registered as a heuristic and as the search's
seed, which would also settle whether the LightGBM dependency is needed at all
(§7); and the cost model to order the re-certification queue (§19).

## How you actually use it

The solver runs without any of this installed. Everything here is loaded only
when asked for by name, so a clone that never runs
`pip install -r learning/requirements.txt` sees no difference.

Two heuristics are registered by name in `satisfiability/heuristics.py` and
are not defaults: `learned+cs-dfs` (the LightGBM seed; needs a trained model,
and errors rather than silently falling back if it is missing) and
`cs-dfs+degree` (the degree tie-break of §20). One flag exists on the complete
search, `fan_order`, defaulting to today's order.

```bash
pip install -r learning/requirements.txt      # pandas, scikit-learn, lightgbm; optional extras listed inside

python -m learning.dataset --workers 16       # the feature table, learning/data/instances.csv (~90 s)
python -m learning.canonical --workers 16     # isomorphism classes, learning/data/canonical.csv (~1 s)
python -m learning.ensemble --tables-only     # the generated campaign's tables from the committed CSV
python -m learning.hardness_map               # the ridge, reports/figures/hardness_map.png (~3 s)
python -m learning.differential --stage tables
python -m learning.sandwich                   # brute-force check of the Lean definitions + lake build (~5 s)
python -m pytest tests/ -q                    # the whole suite, ~80 s
```

Every module runs as `python -m learning.<name>`, has a docstring saying what
question it answers and how to run it, and names its report section. Long
runs are resumable and write to `learning/data/ensemble/`; nothing writes to
the corpus's `solutions/` directory.

## The map of the folder

Grouped by the question each module answers; the section is in
`reports/ml_nature.md`.

**Instruments**
```
features.py          an instance as 49 numbers (matrix, graph, bounds, invariants)   §4
dataset.py           joins every instance with its proved answer -> data/instances.csv
canonical.py         isomorphism classes, nauty certificates, WL hashes            §1
fingerprint.py       generator classifier, size-free features, the instance map;
                     union_groups is the split every study uses                  §2
node_counts.py       refute(optimum - 1) under the two search configurations      §3
ensemble.py          the generated campaign: generate, solve, refute, feature   §9, §10, §16
degeneracy.py        the exact lattice oracle: optimal orders, optimal choices     §8
treewidth.py / .c    exact treewidth (subset DP to 26; decision search to 64)     §21
```

**The answer**
```
study_optimum.py     can structure predict the optimum?           reports/learning.md
invariants_study.py  pathwidth-adjacent invariants as features                   §4
formula_search.py    enumerated + PySR symbolic regression                       §5
concentration.py     variance of the optimum per cell; E[opt](n, m, p)          §12
scale_test.py        the n <= 40 laws against the corpus at 30-125              §14
sandwich.py          the Lean theorems checked against brute force and the corpus §26
```

**The bounds**
```
bound_gap.py         where the proved bound fails; the treewidth ceiling           §6
extremal.py          adversarial search for the worst small instances             §21
conjecture.py        mining and attacking candidate lower bounds                  §24
```

**Hardness**
```
hardness_map.py      nodes against density per size: the ridge                   §11
graph_story.py       same graph, different products: re-covering and relabelling §13
upward.py            rates and drift at 50-100; the revised 125 x 125 prediction §16
ridge_theory.py      why the ridge is where it is: the excess                    §25
cost_model.py        censored regression: nodes before the run                   §19
```

**Soundness**
```
differential.py      the same question under ten labellings and two configurations §15
proofs.py            DRAT proofs through the SAT encoding, checked by drat-trim   §17
```

**Search rules**
```
relabel_portfolio.py min-of-k over relabellings                                   §18
fan_order.py         degree against index as the tie-break                        §20
theorem2.py          Chu & Stuckey's Theorem 2 on against off, everywhere         §22
```

**Schedules**
```
policy.py            the LightGBM closing-order ranker (learned+cs-dfs)   reports/learning.md
distil.py            what the ranker learned: the two-key rule                     §7
set_imitation.py     imitation with the set of optimal moves as the label         §23
corpus_sweep.py      scores a heuristic against all 6,376 known answers
guided_search.py, descent_bench.py   learned branching and starting bounds (closed) reports/learned_search.md
```

**Data** — `learning/data/ensemble/` is committed (82 MB apparent): the
campaign's manifests, results and witnesses, and one CSV per study. The rest
of `learning/data/` is rebuilt by the commands above; the 11.7 GB of DRAT
proofs live git-ignored under `learning/data/proofs/` with only their hashes
and verdicts committed in `proofs.csv`.

## Two ways this could have fooled us, and the third that nearly did

**Nearly-identical puzzles.** Instances from one benchmark file, and instances
that are the same graph under renamed customers, are near-copies. Split them
randomly and a model is tested on what it studied. Every number in these
reports groups by file *and* by isomorphism class; where a random-split number
is shown it is shown to display the leak.

**The pile is not the problem.** Of 6,376 instances, 5,938 have 30 or fewer
customers. The instances that cost a day of compute are 25 rows. A result on
the corpus is a result about small instances unless it says otherwise, which
is why every finding states its size range and why the generated campaign
exists.

**A count is dated by the code that made it.** Node counts from the C search
exist from three versions of one pruning rule, and only counts from the same
version are comparable. The reports say which version made each file; a model
predicts for the version that made its training data.
