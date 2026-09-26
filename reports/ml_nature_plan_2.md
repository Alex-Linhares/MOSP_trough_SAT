# Using machine learning to understand the nature of MOSP — second plan

*2026-09-26. The sequel to `reports/ml_nature_plan.md`, whose ten questions
two Ralph loops answered in fourteen sections of `reports/ml_nature.md`
(loop0001 §1–§8, loop0002 §9–§14; `CLAUDE.md` carries the digest). This plan
asks what those answers make possible. It is more ambitious than the first
by design: the first plan asked whether learning could say anything about the
problem, and it could; this one asks for objects — certificates a third party
can check, a conjectured bound with a counterexample engine behind it, a
speed-up for the day-long instances, a search rule the literature would
recognise, and a synthesis that reads as a paper. Nothing here changes a
solver default; every proposed change is measured in nodes and left for the
owner to enable.*

## 0. What the first two loops established

Fourteen findings, in the order the questions below build on them.

1. **Hardness is a property of the labelled graph and of nothing else** (§13):
   re-covering the same edge set with different cliques leaves the node count
   *exactly* unchanged; relabelling the customers changes it by up to 2.3×
   (default) and 8× (`csearch`) and never changes the answer.
2. **Hardness has a ridge** (§11, §14): nodes to refute grow exponentially in
   `n` at fixed density, doubling every 3–3.5 customers on the ridge at about
   three customers per product (`m = n`), and the ridge law pre-registered at
   `n ≤ 40` predicted the 125×125 counts within a factor of 3 over eight
   decades. Chu & Stuckey's density-2 classes are the ridge.
3. **The cost of a refutation at `n ≤ 75` is seconds; at 100 on the ridge it
   is 17 minutes; at 125 it is a day** (§9, §14). So 75 is free, 100 is a
   budgeted campaign, and 125 is out of reach for anything but single runs.
4. **The proved bound fails structurally** (§6): three of its four components
   are treewidth bounds, and pathwidth provably exceeds treewidth on 131 of
   the 338 instances with gap ≥ 2. The family is trees of cliques with
   branching. Only the expansion bound is a pathwidth argument.
5. **Two invariants sandwich the optimum on every instance we have** (§5,
   §12): `degeneracy + 1 ≤ optimum ≤ bw_rcm + 1`, forced on a third of the
   corpus and on a third of the campaign. Where they differ the position runs
   from 0 at very sparse to ⅔ at dense.
6. **A one-sentence rule beats the imitation ranker** (§7): *close the
   customer that opens the fewest new stacks; on ties, the one with the most
   unclosed neighbours.* It is the DFS's own fan order followed greedily, with
   MCN's tie-break reversed, and it is the better DFS seed.
7. **The optimum is never unique and imitation targets are ~90% arbitrary**
   (§8): 10⁵ optimal closing orders at `n = 10`, 10¹⁰ at 15; step agreement
   above 0.3 measures the solver's tie-breaks.
8. **Theorem 2 never costs and saves more with size** (§13, §14): `csearch /
   default` nodes 0.87 at `n ≤ 40`, 0.63 at 100, 0.17 on `Random-100-50-4`;
   the switch that turns it on is a hand threshold on a matrix statistic.
9. **Nothing checks that a refutation is sound above 40 customers** (§3, §8):
   the lattice oracle agrees with the search to 15, two configurations agree
   to 40, and the two known false refutations were above that.
10. **The corpus is 3,667 graphs, the generators are fingerprintable, and
    every grouped split must group by isomorphism class** (§1, §2).
11. **Min-fill treewidth is the best point estimate to 50 customers and
    wrong by 4 stacks at 125** (§4, §14); the `E[opt]` formula is within ±2 at
    densities 4–10 to 125 and off by 8 at density 2.
12. **Seconds do not measure hardness at `n ≤ 40`** (§9); nodes do.
13. **Fourteen of fourteen items produced a finding about the solver rather
    than a component of it** — a rule, a ridge, a ceiling, a leak, a bug.
14. **Cost**: loop0001 $57 and 3.1 session-hours; loop0002 $40 and 2.1.

**The rules, unchanged.** A prediction is never a bound. Nothing learned
touches `_lower_bound` or any path that decides `k`. Splits group by file ∪
isomorphism class. Every conclusion states its size range. Findings resting
on a handful of instances are re-certified first. Nodes, not seconds.

## 1. Methods on the table

| method | what it is for | status |
|---|---|---|
| differential testing over relabellings and re-coverings | soundness: two runs that must agree on the answer and need not agree on the cost | new; §13 supplies the invariants |
| DRAT proof logging (pysat `with_proof=True` on CaDiCaL) with an external checker (drat-trim, to be built) | third-party-checkable refutations | new |
| the subset-lattice oracle (`learning.degeneracy`) | an exact optimum that shares no code with the search, `n ≤ 15` (20 vectorised) | built |
| survival / censored regression on node counts | runtime prediction where the tail is timeouts | new |
| order statistics of a portfolio over relabellings | turning label noise into a speed-up | new |
| conjecture mining with a validity oracle: enumerate bound formulas, keep those never above the optimum on 44,000 certified instances, rank by tightness | a candidate lower bound | new; `learning.formula_search` is the enumerator |
| adversarial extremal search with the exact solver as oracle (`n ≤ 15`) and an exact treewidth DP | counterexamples to a conjecture; the instances the theory is missing | new |
| set-valued imitation (`learning.degeneracy.optimal_choices`) | the first imitation objective that is not the solver's tie-breaks | new |
| the generated-ensemble campaign (`learning.ensemble`) | data at any `(n, m, p)` we can afford | built; extend upward |
| Lean 4 (`lean/MOSPFormalization`) | the sandwich inequalities as theorems | existing development |

## 2. The questions

### 2.1 Can every certified optimum at n ≤ 40 carry a proof a third party can check?

The main project's open item 7 is the end-to-end certificate chain, and the
first plan's §2.10 is the differential harness. Both are about the same
blind spot (finding 9), and the corpus is meant to be published.

- **Method.** (a) A differential harness: for every instance, `k` random
  relabellings and one re-covering, `decide(optimum − 1)` and
  `decide(optimum)` under both configurations; any disagreement in *status*
  is an unsound rule; node counts are recorded because their spread is the
  §2.4 measurement. Run over the campaign (37,800), the corpus at `n ≤ 40`,
  and the lattice oracle where it reaches. (b) DRAT: re-refute `optimum − 1`
  through the SAT encoding with proof logging for every certified instance
  at `n ≤ 40`, check each proof with drat-trim, and record proof size, check
  time and the checker's verdict. Proofs are stored compressed outside git
  with their hashes and verdicts in a committed table.
- **Baseline.** Today: zero third-party-checkable refutations.
- **Deliverable.** The harness and its run (expected: zero disagreements,
  stated as such), and the fraction of the corpus carrying a checked proof
  by size band. The first `n` at which SAT-with-proof stops being affordable.
- **Kill.** None for (a). For (b): if drat-trim cannot be built or pysat's
  proof output is not checkable, the item records that and the SAT proof
  path is closed for this stack.

### 2.2 How far up does the ridge law hold, and what is the true rate?

§14 found the campaign's `n ≤ 40` rates overstate the corpus's by
0.005–0.018 per customer, from five instances per class. Finding 3 says the
campaign can go to 75 for free and to 100 on the ridge for a budgeted run.

- **Method.** Extend `learning.ensemble` with `n ∈ {50, 60, 75}` across the
  density sweep at `m ∈ {n/2, n, 2n}` (the half ratio was never generated
  and is where Theorem 2 saves most), 50 per cell, and `n = 100` on the
  ridge and its two neighbours only, 25 per cell, priced by the ridge law
  before it is run. Re-fit the rates per density with the local rate between
  consecutive sizes; fit whether the rate itself drifts with `n`.
- **Baseline.** §11's rates and §14's corpus rates.
- **Deliverable.** The rate per density with its drift, the size at which
  the drift is resolved, and a revised prediction for the 125×125 classes
  with its error band from the 100-customer cells.
- **Kill.** If the 100-customer ridge cells cost more than 8 core-hours in
  total, stop at 75 and say so.

### 2.3 Can we predict how long an instance will take?

`reports/learning_plan.md` question 2, now with the data to answer it:
nodes under both configurations on 37,800 + the corpus to 125, and finding
1's statement that only graph features and a label-noise term can matter.

- **Method.** Predict `log10 nodes` from label-free graph features (the
  ridge coordinate `col_mean`, `n`, `optimum / n` or its `E[opt]` proxy,
  degree statistics, `tw_min_fill`), with the relabelling spread from §2.1(a)
  as an irreducible-noise floor; censored observations (timeouts) handled by
  a survival model, never dropped. Train at `n ≤ 75`, test at 100 and 125.
- **Baseline.** §11's cell law interpolated in `col_mean`; §14's surface.
- **Deliverable.** A predictor with its error by size band, a decade-accuracy
  claim at 100–125, the predicted cost of the remaining recertify instances
  against what recertify actually spent, and the answer to "which of the
  withdrawn 13 would have been cheapest to re-certify first".
- **Kill.** If fewer than 80% of the 100–125 counts fall within one decade of
  the prediction, the predictor is not to be used for budgeting and the
  section says so.

### 2.4 Is label noise a free speed-up?

Finding 1: relabelling changes the node count by up to 8× under `csearch`
and never the answer. The minimum over `k` independent relabellings is a
portfolio with no coordination cost.

- **Method.** On the campaign at `n ∈ {40, 50, 60, 75}` and the corpus at
  50–100, refute `optimum − 1` under 16 random relabellings per instance;
  record the distribution; compute the expected speed-up of min-of-`k` for
  `k ∈ {2, 4, 8, 16}` against the identity labelling and against the median.
  Then, on the four 100-customer density-2 instances that are censored at
  1,500 s in §14, run the 16-way portfolio for real. Check whether the
  spread grows with `n` (it must, for this to matter at 125) and whether a
  cheap statistic of a labelling predicts its cost (if it does, choose; if
  not, race).
- **Baseline.** The identity labelling, which is what every run so far used.
- **Deliverable.** The speed-up curve against `k` and `n`, the projected wall
  clock for the 125×125 ridge classes on 16 cores, and a recommendation.
  Nothing enabled: the driver that would use it is `benchmarks.recertify`,
  and that is the owner's change.
- **Kill.** If the median min-of-8 speed-up at `n ≥ 60` is under 1.5×, the
  spread is too small to spend cores on.

### 2.5 Which fan order should the search use, and when should Theorem 2 be on?

Two solver-facing conjectures the loops produced (findings 6 and 8), both
measurable in nodes without touching a default.

- **Method.** (a) Fan order: behind a flag, order the cheapest candidates in
  `decide` and `restricted_dfs` by highest remaining degree instead of
  customer index; measure nodes on the campaign and the corpus to 100 under
  both configurations, paired per instance. (b) Theorem 2: with nodes under
  both configurations on every instance we have, fit the decision boundary
  where `csearch` beats `default` and compare with the hand threshold
  `sparse_enough_for_better_move` (≤ 5 products per customer); test the
  hypothesis §13–§14 suggest, that it should simply always be on.
- **Baseline.** Current fan order; the current threshold.
- **Deliverable.** Two paired measurements with their sign, size and
  dependence on `n` and density; a proposed default for each, stated and
  *not* applied.
- **Kill.** (a) If the paired median node change is within ±5% at every size,
  the fan order does not matter and the conjecture is closed. (b) If the
  learned boundary agrees with the hand threshold on more than 95% of
  instances, the threshold stands.

### 2.6 Is there a lower bound in the tree-of-cliques family, and can it survive an adversary?

The first plan's route to a conjecture (§2.2) found none in degree
statistics, and §6 explained why: the family the bound misses is trees of
cliques with branching, where pathwidth exceeds treewidth. A bound that sees
branching has to be a pathwidth argument, like the expansion bound.

- **Method.** Conjecture mining: enumerate candidate formulas over invariants
  that *can* see branching — the expansion bound's `f(t)` profile, separator
  sizes at several balance ratios, the number of simplicial vertices and
  hubs, the pathwidth of the clique tree where the graph is chordal, block
  and bridge counts — keep every candidate that is never above the optimum
  on all 44,000 certified instances, rank by how often it exceeds `lb_best`
  and by tightness on the 338 gap instances. Then attack each survivor with
  §2.7's extremal search at `n ≤ 15` using the exact solver as oracle: the
  smallest counterexample, if any, is drawn. A survivor is stated as a
  conjecture with the instances it was tested on, and handed to the Lean
  item.
- **Baseline.** `lb_best`; the expansion bound alone.
- **Deliverable.** Zero or more conjectures of the form `pathwidth ≥ f(G)`,
  each with tightness statistics, size range, and either a counterexample or
  the statement that 10⁴ adversarial instances at `n ≤ 15` did not find one.
- **Kill.** If no candidate exceeds `lb_best` on more than 5% of the gap
  instances while surviving the adversary, the family is closed and the
  section says the bound work needs a new idea, not a new formula.

### 2.7 What are the extremal instances, and is pathwidth minus treewidth bounded?

The first plan's §2.7, unrun, now with an objective §6 wrote down.

- **Method.** Local search over bit flips at `n ≤ 15` with `solve_mosp_exact`
  as the oracle and an exact treewidth DP (O(2ⁿ·n), fine to 20) beside it;
  objectives: `optimum − lb_best`, `optimum − (tw + 1)`, nodes per size,
  `cs-dfs` overshoot, and disagreement between two configurations (the
  soundness objective from §2.10). Dedupe by canonical form. Start from the
  ten smallest gap instances of §6 and from random trees of cliques. Also:
  exact treewidth for the 82 uncertified gap ≥ 2 corpus instances at `n ≤ 30`
  where the DP or a branch-and-bound reaches, to turn §6's 38.8% floor into
  a number.
- **Baseline.** The worst instance already in the corpus at each size, per
  objective.
- **Deliverable.** Per objective, a family of small instances with the
  objective's value, drawn; the largest `pw − tw` found at each `n` and
  whether it grows with `n`; the smallest instance with `pw − tw ≥ 2` and a
  proof of it.
- **Kill.** If the search cannot beat the corpus's worst at the same size for
  any objective after a fixed budget, the corpus is already extremal.

### 2.8 Does imitation work when the target is the set of optimal moves?

Finding 7 says the previous imitation target was 90% arbitrary. The only
honest test of "can a policy learn more than the rule" uses the
optimal-continuation set as the label.

- **Method.** Vectorise `learning.degeneracy`'s search-measure lattice to
  reach `n = 20` (1,298 corpus instances). Train a ranker whose loss counts a
  step right when it lands in `optimal_choices`; evaluate by construction
  value, grouped by file ∪ class, against the two-key rule and the old
  ranker; add the rule's two keys as features so the model can only add to
  it. Along every witness at 50–125, count the optimal choices per step by a
  bounded backward search restricted to the witness's own prefixes, to see
  whether the ~0.3 ceiling holds at the sizes that matter.
- **Baseline.** The two-key rule (§7): MAE 0.348, exact 80.7%.
- **Deliverable.** Whether any learned policy beats the rule under the
  correct objective, by how much, and the imitation ceiling at 50–125.
- **Kill.** If the set-valued policy does not beat the rule by more than
  0.02 MAE grouped, imitation is closed for good and the rule is the answer.

### 2.9 Why is the ridge where it is?

§11 located the ridge at three customers per product (`m = n`) and two
(`m = 2n`); in random-intersection-graph terms both are a MOSP-graph mean
degree near 8–9. That coincidence is a hypothesis.

- **Method.** Analysis, not learning: derive the expected degree, edge
  probability and giant-component threshold of `G(n, m, p)` in `col_mean`
  coordinates for each `m / n`; overlay them on the hardness map; compare
  the ridge with the known transitions of pathwidth and treewidth in sparse
  random graphs (linear above a constant average degree, with the constants
  the literature gives). Test on the campaign whether the ridge's `col_mean`
  at `m = n / 2` (from §2.2) is what the degree hypothesis predicts.
- **Baseline.** "Three customers per product", the empirical statement.
- **Deliverable.** The ridge stated as a condition on a graph parameter that
  is the same across `m / n`, or the statement that no single parameter
  does it, with the `m = n / 2` cells as the deciding test.
- **Kill.** None; the deliverable is a statement either way.

### 2.10 Can the sandwich be a theorem in the repository's Lean development?

`degeneracy(G) + 1 ≤ pathwidth(G) + 1 ≤ bandwidth(G) + 1` are textbook
inequalities, checked on 44,000 instances; the treewidth ceiling of §6 is a
corollary of `treewidth ≤ pathwidth`. The Lean development already has
`Pathwidth.lean`, `VertexSeparation.lean` and `ForMathlib/`.

- **Method.** State degeneracy and bandwidth over the existing graph
  definitions, prove `degeneracy ≤ vertex separation` and `vertex separation
  ≤ bandwidth`, connect through `VSEquivPW`. Blocked is an acceptable outcome
  for this item if the definitions do not fit in a session; the deliverable
  then is the statements with `sorry` and a note of what is missing.
- **Deliverable.** Two theorems, or two statements and a gap list.
- **Kill.** None.

### 2.11 What does it all say?

Fourteen sections and however many this loop adds are not a paper. The
last item writes the synthesis.

- **Method.** `reports/ml_nature_summary.md`: every claim the two plans
  produced, one paragraph each, with its size range, its regenerate command,
  and its status (finding / conjecture / proposed solver change with measured
  effect / closed question); the list of solver changes proposed and never
  enabled, with the measurement that would decide each; the open questions
  in order of what they would cost. Then the plain-English
  `learning/README.md` brought up to date.
- **Deliverable.** The summary, and a README a newcomer can read first.
- **Kill.** None.

## 3. Sequence

One Ralph loop, `Ralph_Loops/loop0003/`, fourteen items in the order the
dependencies require:

1. §2.1(a) the differential harness — everything after it rests on the
   answer being sound, and it is the cheapest item.
2. §2.2 the campaign upward — the data three later items need.
3. §2.1(b) DRAT proofs at `n ≤ 40` — long-running, independent, can share the
   machine with the analysis items.
4. §2.4 the relabelling portfolio — the biggest practical payoff, needs §2.1(a)'s
   relabelling runs.
5. §2.3 runtime prediction — needs §2.2 and §2.4's noise floor.
6. §2.5(a) fan order.
7. §2.5(b) Theorem 2's switch.
8. §2.7 extremal search and exact treewidth — the counterexample engine.
9. §2.6 conjecture mining, attacked by item 8's engine.
10. §2.8 set-valued imitation.
11. §2.9 why the ridge is where it is — needs §2.2's `m = n / 2` cells.
12. §2.10 Lean.
13. §2.11 the synthesis.
14. Reserve: any item marked blocked, re-opened with what was learned.

Estimated from the first two loops: 14 sessions at 20–50 minutes,
$100–150, one working day of wall clock; the two long-running items (3 and
4's real runs) are budgeted at 8 core-hours each and the recertify run keeps
its cores.

## 4. What would count as success

- The corpus at `n ≤ 40` carries proofs a third party has checked, and the
  differential harness has run over 44,000 instances with zero disagreements.
- A number for the 125×125 ridge that comes from measurement at 100, not
  extrapolation from 40, and a portfolio that turns a day into hours or a
  measurement that says it cannot.
- A conjectured pathwidth lower bound that sees branching, with 10⁴
  adversarial instances behind it, or a clean statement that the family is
  closed.
- Two solver changes with paired node measurements, proposed and not
  applied.
- The ridge as a graph parameter.
- A synthesis document.

Not success: a model that predicts well and explains nothing, a bound that
is a prediction, or a default changed without the owner's hand.
