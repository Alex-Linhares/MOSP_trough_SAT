# Using machine learning to understand the nature of MOSP — third plan

*2026-09-27. The sequel to `reports/ml_nature_plan_2.md`. Twenty-seven sections
of `reports/ml_nature.md` and the synthesis `reports/ml_nature_summary.md`
leave seven questions, ranked by what depends on them. This plan turns the
ones that are loop-shaped into items, cuts the ones that can be cut, and is
honest about the two that a loop can only equip: a branching-aware bound and
the Lean equality are proof problems, and the loop supplies their harnesses
and their statements, not their proofs. Nothing here changes a solver default;
every proposed change is measured in nodes behind a flag and left for the
owner.*

## 0. What the third loop stands on

- Every refutation at n ≤ 40 is sound on twenty independent searches and
  92% carry a checked DRAT proof; above 40 the only checks are agreement
  between two configurations and among a few relabellings (§15, §17).
- The C `better_move` was fixed on 2026-09-26 (`0eb33915`); the fixed rule
  costs +7% nodes at n ≤ 40, ×2–3.5 at the 100-customer half-ratio classes
  and ≥ 15× on the one ridge instance at 100 with both sides on record (§18).
  Which of the fix's two changes carries that cost is unmeasured.
- Hardness is a property of the labelled customer graph and of nothing else
  in the matrix, for the customer search; the SAT encoding, with a variable
  per product position, was never tested (§13).
- The ridge sits at cover excess `(n_ones − m) / n ≈ 2–2.4` across every
  product ratio, one independent cycle of the incidence graph per customer;
  its rate falls by 0.002 per customer per ten customers from 10 to 75 (§16,
  §25). Nothing at 100 on the ridge is certified beyond a 5-instance sample.
- The bound's blocked family is trees of cliques with branching; `tw + 1` is
  a theorem and beats the bound on 933 instances; no formula over thirty
  invariants beats `max(lb_best, tw + 1)` (§6, §21, §24).
- The two-key closing rule beats every learned policy; whether it is the
  literature's MCNh under another name is open, now that Becceneri, Yanasse &
  Soma (2004) — obtained 2026-09-27 — states MCNh as an arc-traversal
  heuristic (§7, `literature/MISSING.md`).
- `Sandwich.lean` proves both sandwich inequalities; `Reduction.lean` had
  `mosp ≤ pathwidth + 1` with a Hall's-theorem `sorry` and no `≥` (§26) —
  **superseded 2026-09-27 before item 12 ran**: that statement was over the
  pattern graph and false; `MOSPGraph.lean` now proves the equality over the
  MOSP graph, `sorry`-free, both directions. Item 12 is reduced to the three
  tree-decomposition `sorry`s of `Sandwich.lean`.

## 1. The questions and their items

**Q6 — two cheap closures.** (01) `learning.corpus_sweep` with the two-key
rule seeding `restricted_dfs`, against `learned+cs-dfs`'s 709 better / 13
worse over `cs-dfs`; decides whether the LightGBM dependency question exists.
(02) Implement the 2004 arc-traversal Minimal Cost Node heuristic from its
pseudocode, verify on the paper's worked example (Table 1, ξ′ = 4, the printed
sequence), compare with Frinhani et al. (2018)'s MCNh column on the Challenge
and SCOOP instances and with our `mcn` and the rule. *Kill for 02:* if the
paper's example cannot be reproduced from the pseudocode, say what is
ambiguous and stop.

**Q5 — does the graph story hold for SAT?** (03) On §13's re-covering and
relabelling pairs, `decide_mosp` through the SAT path at `optimum − 1` and
`optimum`, conflicts and seconds recorded; paired ratios; predict SAT
conflicts from graph-only against graph-plus-matrix features. *Kill:* SAT
cost as cover-independent as the search's (paired median within ±5%); then
the two procedures cannot fail on disjoint sets for that reason.

**Q1 — soundness at scale, in three pieces.** (04) Which change carries the
fix's cost: behind flags, the close-count correction and the rule reordering
toggled separately, each variant run through the differential harness at
n ≤ 40 and, where sound, paired in nodes at 50–100; a cheaper sound variant
recommended if one exists, not applied. (05) A proof object for the customer
search: a certificate format that records every pruning decision with its
rule and its witness (the dominator, the subset relation), an emitter on the
Python search, and an independent checker that verifies each premise from
the instance and replays the residual search; tested at n ≤ 20 against the
DRAT and lattice verdicts. *Kill:* if a Theorem 2 step cannot be checked
locally from the instance and the state, say so precisely; that is the
finding. (06) The differential harness at 50–100 under a budget: four
relabellings, both configurations, both `k`, on the campaign at 50–75 and the
corpus at 50–100, 300 s per call, ≤ 8 core-hours; censored calls are lower
bounds.

**Q4 — does the rate keep falling?** (07) One certified ridge cell at
n = 100, m = n, realised three customers per product: as many of 25
instances as 2.5 hours on 16 workers certify under `default`, resumable,
priced by `learning.cost_model` before starting; the rest recorded as
censored lower bounds. (08) Refit §16's rate drift with the 100 cell,
predict 125 with a band, compare with the six recertify counts on record,
and state whether the curve is sub-exponential or the drift saturates.

**Q3 — why cover excess two?** (09) Analysis: the cover excess as a quantity
of the random bipartite incidence graph — its cyclomatic number is
`n_ones − n − m + c`, so excess 2 is one independent cycle per customer —
against the 2-core and k-core thresholds of random bipartite graphs and the
random-intersection-graph literature; a derivation of where the ridge should
sit for each `m / n`, tested against §25's measured peaks. (10) Is the
ridge's *height* a function of the same quantity: fit peak median nodes
against `(n, excess, m / n)` across all series; deliverable a formula or the
statement that height needs `m` separately.

**Q2 — a bound that sees branching.** (11) The harness, not the discovery: a
module that takes any candidate bound as a Python function and (a) checks
validity on every certified instance, (b) attacks it with `learning.extremal`,
(c) reports tightness on the 338 gap instances against `max(lb_best, tw + 1)`;
then three stated candidates run through it, the first being the
pathwidth branch rule applied recursively over cut vertices (if `G − v` has
three components of bound ≥ k then bound ≥ k + 1, seeded by clique size), the
others the session's. *Kill:* none beats the reference on more than 5% of the
gap instances while surviving.

**Q7 — the Lean equality.** *(Closed outside the loop on 2026-09-27: see §0.)*
(12) What remains in `Sandwich.lean`: `treewidth_le_pathwidth` (a path
decomposition is a tree decomposition; needs either `pathGraph.IsTree` or a
direct construction), the branch lemma (Fellows & Langston 1987 Lemma 4.3,
Kinnersley 1992 Theorem 4.3), and the `conjecture_sqrt_tw_f6` statement, which
stays a statement. `lake build` must pass. Blocked with a gap list is an
acceptable deliverable.

(13) Reserve.

## 2. What would count as success

Questions 4, 5 and 6 settled outright; question 1 narrowed to a cost table per
fix variant, a checked certificate format at small sizes, and a budgeted
harness run above 40; question 3 with a derivation tested against the
measured peaks; questions 2 and 7 with a working harness and precise
statements. The plan does not promise the bound or the proof.
