# Pathwidth after ETH: a subexponential exact algorithm, or what its absence would cost — plan for Ralph loop0014

*Written 2026-11-04, after the checkpoint relaxation and the two-ended
measurement (`reports/checkpoint_relaxation.md`) closed the last cheap
routes to the 125-vertex refutations. Nothing here has been run. The loop
directory would be `Ralph_Loops/loop0014/` (`TASK.md`, `iterations.md`,
`PROGRESS.md`, `loop.py`, `gate.py`, `knobs.json`, `allowed_sorries.txt`),
cloned from loop0013's. Not launched.*

## 0. The question, the hypothesis it rests on, and why now

### 0.1 The landscape changed on 2026-10-25

OpenAI's manuscript collection (`github.com/openai/math`, Apache-2.0;
cloned read-only under `~/dev/untrusted/openai-math`, never built or run
from inside the repository) contains family 378, *The Exponential Time
Hypothesis is False*: a deterministic algorithm that counts the satisfying
assignments of any `k`-CNF on `n` variables in time
`(n + m)^{O_k(1)} · 2^{O_k(n (log log n)² / √log n)}` and polynomial space.
The Lean library behind it is 3,977 files, no `sorry`, the three standard
axioms, and the comparator statement
(`lean/ComparatorChallenges/SubexponentialSAT.lean`,
`exact_count_and_sat`) is a concrete multi-tape machine with an explicit
runtime bound in the *number of variables*. We take no position on whether
the community will accept it; everything this loop proves is stated
**conditionally on a named `Prop` that restates that theorem and is never
asserted**, exactly as loop0012 handled Fomin–Høie's `CubicPathwidthBound`.
If the result stands, SETH falls with it (SETH ⇒ ETH), and every
"no `2^{o(n)}` algorithm unless ETH fails" statement in the width
literature is void.

### 0.2 The question

Vertex separation — hence pathwidth, hence MOSP — is a *permutation*
problem: its witness is an ordering of `n` vertices, its natural exact
algorithm the `O*(2^n)` subset DP, and the best published base is below 2
but not `2^{o(n)}`. The ETH paper's Corollary 1.3 gives `2^{o(v)}` for
problems with **one Boolean variable per vertex and bounded-width
constraints** (independent sets, `q`-colourings for fixed `q`); it says
nothing about permutation problems, and the natural CNF encodings of
"`pw ≤ k`" use `Θ(n²)` variables, on which the theorem is worse than the
DP. So, after ETH:

> **Q.** Does pathwidth admit a `2^{o(n)}` exact algorithm on `n`-vertex
> graphs, unconditionally or conditionally on the subexponential counting
> theorem? And if not: which surviving hypothesis would a `2^{o(n)}`
> algorithm for pathwidth refute, through a reduction that is **linear** in
> the number of vertices?

Either answer is a clean statement. A positive answer on any class where
pathwidth is NP-hard is a headline; a negative answer that names the
hypothesis and formalises the reduction is a note that the literature
needs the morning ETH falls. **What this loop does not promise** is a
practical solver: `2^{n/√log n}` at `n = 125` with unknown constants is not
a run, and no item spends compute on an open instance.

### 0.3 What is on record (nothing to solve twice)

- `reports/checkpoint_relaxation.md` §10: the decision "`MOSP ≤ k`" is
  reachability inside `F_k = {S : |N(S) ∖ S| ≤ k − 1}`; the forward
  reachable lattice is within 2.3× of the search's node count at 30–50;
  `R_b(n − j) = C(n, j)` for `j ≤ k − 1`. The subset DP *is* the lattice,
  and the search is near its floor. A `2^{o(n)}` algorithm must not
  enumerate it.
- `learning/two_ended.py` enumerates `R_f(i)` exactly to a cap: the
  instrument for item 06 (how `|F_k|` and `|R_f|` grow with `n` on
  bounded-degree graphs at `k = pw`).
- `lean/MOSPFormalization/`: vertex separation, pathwidth, their equality,
  `MOSP = pw + 1`, treewidth, the sandwich, all `sorry`-free: the
  definitions any reduction theorem is stated against.
- `paper1/`, `paper2/`, `reports/`: **no reliance on ETH or SETH**
  (checked 2026-11-04, zero files). Nothing of ours needs revision.
- OpenAI's `Computation.PrimitiveMachine` model (220 lines, self-contained
  over Mathlib's `Turing.TM0`): a formal notion of "algorithm with a time
  bound" that makes `∃ machine, time ≤ f(n)` a `Prop`. Reusable under
  Apache-2.0 with attribution; item 02 decides whether to copy it or to
  state algorithms abstractly.

### 0.4 Design decisions (fixed)

1. **The hypothesis is a `Prop`, never an axiom.** `SubexpCount k : Prop`
   restates `exact_count_and_sat` in our own file; theorems read
   `SubexpCount k → …`. `allowed_sorries.txt` stays empty; the gate counts
   axioms.
2. **Linear means linear in vertices.** A reduction from problem `X` on
   size-`N` instances to pathwidth on `O(N)` vertices transfers
   `2^{o(n)}`; a quadratic one transfers nothing. Every reduction in the
   catalogue (item 03) carries its blow-up, and only linear ones enter a
   theorem.
3. **Classes before the general case.** The positive track (item 04) looks
   for a class where pathwidth is NP-hard *and* a layout is determined by
   `O(n)` bits under bounded-width local constraints. A positive result on
   such a class is worth more than a failed attempt on all graphs.
4. **No compute on open instances; measurement on generated graphs only**
   (item 06, random cubic and random `G(n, c/n)` at `n ≤ 60`, seconds each).
5. **Subagents: at most 4 per session**, stated in `TASK.md` (loop0013's
   item 07 fanned out per class; its cost was first recorded as $947 and
   is $38 by the corrected reading of the session logs, 2026-11-04).
6. **Every mathematical claim gets a small-instance check before it is
   stated** (the loop0004 lesson): a reduction is tested on every graph to
   7 vertices against brute-force vertex separation before Lean sees it.
7. **Reading the ETH paper is an item, not a background task.** Its
   Sections 2–6 (technique overview, shared linear summaries, replacement
   forms, common zeros of sparse systems, the reduction) are 40 pages; item
   01 reads them and writes a two-page account of *what the method needs
   from a problem* in our words, which every later item cites instead of
   the paper.

### 0.5 Items, one line each, in dependency order

| # | item | depends on | kind | cap |
|---|---|---|---|---|
| 01 | The audit: best exact bases for pw/tw/vs/bandwidth/cutwidth; every ETH/SETH-conditional lower bound on them, with its reduction and blow-up; what the counting theorem's method needs from a problem (two pages, our words); the kill check | — | reading, writing | 4 h |
| 02 | The formal frame: `SubexpCount k` restated; an algorithm-with-time-bound notion (copy of the `PrimitiveMachine` model with attribution, or an abstract one, decided here); `PathwidthSubexp : Prop`; `lake build` | 01 | Lean | 3 h |
| 03 | The reduction catalogue: every linear-in-vertices reduction *into* pathwidth / vertex separation on record, and the best `X` such that `PathwidthSubexp → X ∈ 2^{o(N)}`; each candidate checked on all graphs to 7 vertices | 01 | reading, code | 4 h |
| 04 | Classes with `O(n)`-bit layouts: cobipartite (tw = pw, NP-hard), split, bounded-degree, co-comparability, the MOSP cover classes of paper 2; for each, whether "`vs ≤ k`" is a bounded-width constraint system in `O(n)` Boolean variables | 01 | mathematics | 4 h |
| 05 | The chain count as an algebraic object: `#` feasible chains as a sum over orderings; whether it is the number of common zeros of a sparse polynomial system in `o(n²)` variables; the obstacle named if not | 01, 04 | mathematics | 4 h |
| 06 | Measurement: `|F_k|` and `|R_f|` at `k = pw` against `n` on random cubic graphs and `G(n, 3/n)` to `n = 60` (`learning/two_ended.py`); the exponential rate; is the reachable lattice ever `2^{o(n)}` on a class where pw is NP-hard? | — | compute (minutes) | 2 h |
| 07 | The reduction theorem, on paper: `PathwidthSubexp → X ∈ 2^{o(N)}` for item 03's `X`, with the reduction's correctness proved; if item 03 finds only quadratic reductions, the theorem is "no linear reduction into pathwidth is on record" and item 07 tries to build one from Hamiltonian path or bandwidth | 03 | mathematics | 4 h |
| 08 | The reduction theorem, in Lean: the graph construction and the width equivalence (`vs(G') ≤ k ↔ X(I)`), stated against `VertexSeparation.lean`, `sorry`-free | 07 | Lean | 4 h |
| 09 | The positive attempt: if item 04 found a class with `O(n)`-bit layouts and bounded-width constraints, write the encoding and prove `SubexpCount k → pathwidth on the class ∈ 2^{o(n)}`; else the attempt on the chain count (item 05's route) with a stated kill | 04, 05 | mathematics, Lean | 4 h |
| 10 | The hypothesis map: which published lower bounds on width parameters rested on ETH or SETH (with citations and the exact statement voided), and which hypotheses survive (`P ≠ NP`, `NP ⊄ SUBEXP` in input length, the Set Cover and Orthogonal Vectors conjectures' status); a table for the note | 01 | reading, writing | 3 h |
| 11 | The write-up: `reports/subexp_pathwidth.md` (§0 two pages), the note *Pathwidth after ETH* in `paper1/latex/` or a new `paper3/` stub, the CLAUDE.md paragraph, `literature/MISSING.md` entries | all | writing | 3 h |
| 12 | Reserve: whichever of 07–09 ended short, or an independent re-check of item 08's statement by a refuter agent against brute force | 11 | — | 4 h |

Twelve items; Lean items at loop0012's rate (6–20 min each) and reading
items at the cap; **estimate 12–20 hours wall, $300–450** at loop0012–13's
cost per item with the subagent cap honoured. **The owner's budget is
$1,500 (set 2026-11-04 after launch)**: the difference over the estimate is
for the two hard-mathematics items (07, the linear construction; 09, the
positive attempt) to take a second session each through the reserve, and
for a refuter agent on every Lean statement, not for more fan-out.

### 0.6 Kill criteria, stated up front

- **Item 01 kills the loop** if a `2^{o(n)}` exact algorithm for
  pathwidth is already on record, or if the counting theorem's method
  demonstrably needs `O(n)` variables in a way no width problem can
  supply and no NP-hard class supplies either. Then items 10 and 11 run
  (the note is still worth having) and 02–09 are marked `[skipped]`.
- **Item 04 kills the positive track** (09 becomes the chain-count attempt
  only) if no NP-hard class has `O(n)`-bit layouts under bounded-width
  constraints.
- **Item 05 kills the chain-count route** if the obstacle is structural
  (threshold constraints of unbounded width are inherent), stated in a
  paragraph with the smallest example.
- **Item 03 lowers item 07's ambition** if every known reduction into
  pathwidth is superlinear: the theorem becomes the absence statement plus
  one attempted construction, not a transfer theorem.
- **Budget**: **$1,500 total** (owner, 2026-11-04). The coordinator sums the
  `# result` lines of the session logs after each iteration and sets
  `knobs.json` `stop` when the sum passes $1,500 or any session exceeds
  its cap; the driver re-reads the knobs before each session.

### 0.7 The three biggest risks

1. **The ETH paper is wrong, or its method is narrower than its abstract.**
   Mitigated by decision 1: nothing here asserts it, and item 01's two-page
   account is what the rest of the loop uses. If the method needs more
   than "one variable per vertex, bounded-width clauses", item 04's class
   search uses the true requirement.
2. **The positive track produces nothing** (the likely outcome). Then the
   loop's product is the reduction theorem of 07–08 and the hypothesis map
   of item 10 — a publishable note either way, and the first formal
   statement of what a subexponential pathwidth algorithm would refute.
3. **Reductions into pathwidth are all quadratic** (the classical ones go
   through cutwidth or interval completion with size blow-up). Then the
   negative side has no transfer theorem and item 07's attempt at a linear
   construction is the hard mathematics of the loop; its kill is one
   session.

### 0.8 Gate

`gate.py` from loop0013 with: `lake build` of `lean/`, `sorry` count against
an empty `allowed_sorries.txt`, axiom audit of every new theorem
(`paper1/axiom_check.lean` pattern, extended to the new files), pytest on
`tests/test_two_ended.py`, `tests/test_checkpoint_bound.py` and any new
test module with a 900 s timeout, and a check that no file under
`solutions/` or `reports/scratch/obstruction_search/` changed.

## 1. What this plan does not claim

It does not claim a solver, a bound, or a refutation of anything on the
record. It does not assert the ETH result. It does not re-run any proved
instance. It claims, at the end, one of: a conditional `2^{o(n)}` algorithm
for pathwidth on a named NP-hard class, formalised; or a formalised
reduction theorem naming what a `2^{o(n)}` pathwidth algorithm would refute
and a note placing pathwidth in the post-ETH landscape.
