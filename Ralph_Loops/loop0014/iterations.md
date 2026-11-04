# loop0014 — pathwidth after ETH: items

OpenAI's family 378 (*The Exponential Time Hypothesis is False*, 2026-10-25,
Lean-verified against a comparator statement) gives a deterministic
`#k`-SAT algorithm subexponential in the **number of variables**. Pathwidth
is a permutation problem whose natural CNF encodings use `Θ(n²)` variables,
so the theorem says nothing about it directly, and every "no `2^{o(n)}`
unless ETH fails" statement about width parameters is void if the theorem
stands. The plan, `reports/subexp_pathwidth_plan.md`, fixes the premise as a
named `Prop` never asserted (§0.4.1), linearity in vertices as the only
transfer (§0.4.2), classes before the general case (§0.4.3), no compute on
instances (§0.4.4), four subagents per session at most (§0.4.5), and brute
force to 7 vertices before any statement (§0.4.6). Kill criteria are in
§0.6; item 01 can kill the loop.

The report is `reports/subexp_pathwidth.md`; scratch under
`reports/scratch/subexp_pathwidth/<item>/`; Lean under
`lean/MOSPFormalization/SubexpPathwidth/` (imported by
`lean/MOSPFormalization.lean`).

- [x] **01 The audit and the kill check: exact bases, ETH-conditional lower bounds, and what the counting method needs from a problem.**
  `pdftotext` the ETH paper once; read Sections 1, 2 (technique overview),
  6 (the reduction of `#k`-SAT to counting common zeros) and Appendix D
  (tensor contraction), and skim 3–5 for the objects (shared linear
  summaries, low-degree replacement forms, sparse polynomial systems).
  Write `reports/subexp_pathwidth.md` §1 with: (a) the best published exact
  algorithms for pathwidth / vertex separation, treewidth, bandwidth and
  cutwidth with their bases and citations (held papers under `literature/`
  first; Suchan & Villanger, Kitsunai et al., Bodlaender–Fomin–Koster–
  Kratsch–Thilikos, Fomin & Villanger, Cygan & Pilipczuk for bandwidth);
  (b) every ETH- or SETH-conditional lower bound on those parameters we can
  find in held papers or in the citation graph, each with the reduction it
  rests on and the reduction's vertex blow-up; (c) **the two-page account
  of what the counting method needs from a problem, in our words**: the
  input form (variables per object, clause width, sparsity), where the
  `2^{n/√log n}` comes from, what breaks if the constraint width is
  unbounded, and whether the method is a counting method only or decides
  structured existence too. Then the kill check of plan §0.6: stop the
  loop (mark 02–09 `[!]`, leave 10–11) if a `2^{o(n)}` exact pathwidth
  algorithm is on record or the method demonstrably cannot apply to any
  NP-hard width problem. One subagent at most. Ends with "what this does
  not claim".

- [x] **02 The formal frame: `SubexpCount`, an algorithm-with-time-bound notion, and `PathwidthSubexp`.**
  In `lean/MOSPFormalization/SubexpPathwidth/Frame.lean`: decide, and
  record in the report, whether to copy OpenAI's `PrimitiveMachine` model
  (`lean/ComparatorChallenges/SubexponentialSAT.lean`, 220 lines over
  Mathlib's `Turing.TM0`; Apache-2.0, verbatim with attribution in the file
  header and a `literature/MISSING.md` entry) or to use an abstract notion
  (a decidable predicate with a time function, `∃ T : ℕ → ℕ, (∀ ε > 0,
  eventually T n ≤ 2^(ε n)) ∧ …`). Define `SubexpCount (k : ℕ) : Prop`
  restating `exact_count_and_sat` (never proved, never an axiom: a `def`
  of a `Prop`), `PathwidthSubexp : Prop` ("some machine decides `pw G ≤ k`
  for every `n`-vertex `G` and `k` in time `2^{o(n)} · poly`"), and the
  class-restricted `PathwidthSubexpOn (C : SimpleGraph → Prop)`. Prove the
  two trivial lemmas (monotonicity in the class; `PathwidthSubexp ↔
  PathwidthSubexpOn (fun _ => True)`). `lake build`; axiom audit; no
  `sorry`.

- [x] **03 The reduction catalogue: every reduction into pathwidth or vertex separation on record, with its blow-up; the best linear `X`.**
  From held papers and the citation graph: Lengauer 1981, Kashiwabara &
  Fujisawa 1979 (missing: say so), Arnborg–Corneil–Proskurowski 1987
  (treewidth via cobipartite graphs), Monien & Sudborough (cutwidth,
  vertex separation on planar/degree-3 graphs), Bodlaender's and
  Gustedt's hardness proofs, Linhares & Yanasse 2002 (MOSP), Kinnersley
  1992, the `Complex/` chain. For each: source problem, target problem,
  vertex blow-up as a function of the source size, and whether the
  source problem is itself believed to lack `2^{o(N)}` algorithms after
  ETH. Write §3 with the table and name the best `X` with a **linear**
  reduction, or state that none is on record. Every reduction claimed
  linear is implemented in `learning/subexp_reductions.py` and checked on
  every graph (or source instance) to 7 vertices against brute-force
  vertex separation; log under `reports/scratch/subexp_pathwidth/03_reductions/`.

- [x] **04 Classes with `O(n)`-bit layouts: cobipartite, split, bounded-degree, co-comparability, the paper-2 MOSP cover classes.**
  For each class where pathwidth (or treewidth = pathwidth) is NP-hard:
  is a layout, or the decision "`vs ≤ k`", determined by `O(n)` Boolean
  variables under constraints of bounded width in the sense of item 01's
  account? Cobipartite first (Arnborg et al.: `tw = pw` and NP-hard;
  what does a layout look like, and is the decision a cut condition on one
  side?); then split graphs, graphs of maximum degree 3 (pw NP-hard,
  Monien & Sudborough), co-comparability graphs, and the clique-tree
  covers of paper 2. Write §4 with one subsection per class ending in
  "fits / does not fit, because …" and a brute-force check to 7 vertices
  of any claimed encoding. If none fits, say so and mark the positive
  track as the chain-count attempt only (plan §0.6).

- [ ] **05 The chain count as an algebraic object.**
  The number of feasible closing orders is `Σ_σ Π_t [S_t(σ) ∈ F_k]`; the
  decision is whether it is positive. Ask whether this sum is the number
  of common zeros of a sparse polynomial system in `o(n²)` variables in
  the sense of item 01's account: write the threshold constraint
  `|N(S) ∖ S| ≤ k − 1` as a polynomial over a field, measure its degree and
  sparsity, and name the obstacle (unbounded width, or the ordering
  variables) if it does not fit. Test any claimed encoding by counting on
  every graph to 7 vertices (`learning/two_ended.py` and
  `itertools.permutations`) and log under
  `reports/scratch/subexp_pathwidth/05_chain/`. Write §5 ending in a
  verdict for plan §0.6's chain-count kill.

- [ ] **06 Measurement: the reachable lattice against `n` on random cubic graphs and `G(n, 3/n)` at `k = pw`.**
  Generate random cubic graphs (`networkx.random_regular_graph(3, n)`) and
  `G(n, 3/n)` at `n = 16, 20, …, 60`, 10 per cell with fixed seeds;
  `pw` by the C program (`pathwidth_solver/cli/pathwidth`, graph6 on
  stdin, 60 s each; these are new generated graphs, not instances on
  record); then `learning.two_ended.forward_layers` at `k = pw` (the
  refutation level `k = pw`, in MOSP units `k = pw + 1 − 1`; be explicit
  about units) with cap `3 × 10⁶`. Fit `log |R_f| = a n + b` and
  `log |F_k ∩ reachable|`; report the rates with intervals and whether
  any class's rate is consistent with `2^{o(n)}` (it will not be: say what
  the rate is). All under `nice -n 19`, ≤ 8 workers, minutes. Write §6.

- [ ] **07 The transfer theorem, on paper: `PathwidthSubexp → X ∈ 2^{o(N)}` for item 03's best linear `X`.**
  State and prove, in the report, the transfer for the best linear
  reduction of item 03 (the reduction's correctness in both directions and
  the blow-up bound). If item 03 found only superlinear reductions, this
  item tries **one** linear construction from Hamiltonian path or from
  bandwidth into vertex separation (one session, the attempt's obstacle
  named if it fails), and otherwise states the absence: "no reduction
  linear in the vertices into pathwidth is on record; the classical ones
  pass through cutwidth or interval completion with blow-up …". Checked
  on every source instance to 7 vertices before stated. Write §7.

- [ ] **08 The transfer theorem, in Lean.**
  `lean/MOSPFormalization/SubexpPathwidth/Transfer.lean`: the graph
  construction of item 07 as a definition, the width equivalence
  `vs(G'(I)) ≤ k(I) ↔ X(I)` against `VertexSeparation.lean` (through
  `VSEquivPW.lean` if stated for pathwidth), and the transfer
  `PathwidthSubexp → XSubexp` in the frame of item 02. No `sorry`, no
  `axiom`; axiom audit; a `decide`-style check on one small instance if
  feasible. If item 07 ended in the absence statement, this item
  formalises instead the one trivial transfer that is always available
  (pathwidth on a class to pathwidth on all graphs) and the equivalence
  `PathwidthSubexp ↔ VertexSeparationSubexp ↔ MOSPSubexp` through
  `MOSPGraph.lean`, and says so.

- [ ] **09 The positive attempt.**
  If item 04 found a class that fits: write the `O(n)`-variable
  bounded-width encoding, prove its correctness on paper and in Lean
  (`SubexpPathwidth/Encoding.lean`: the encoding's satisfying assignments
  are exactly the layouts of width `≤ k`, checked to 7 vertices first),
  and state `SubexpCount k → PathwidthSubexpOn C` in the frame of item 02
  with the step from the counting theorem to the decision spelled out
  (the "self-reduction" paragraph of the ETH paper, Section 1). If no
  class fits: the chain-count route of item 05, one session, with the
  obstacle stated precisely as a theorem if it can be (e.g. "any CNF with
  one variable per vertex whose models are the width-`k` prefixes has a
  clause of width ≥ f(n)"), checked to 7 vertices, and the kill of plan
  §0.6 recorded. Write §9.

- [ ] **10 The consequences of ETH falling, for pathwidth: four maps.**
  (a) **Computing the widths**: every published statement that computing
  pathwidth, treewidth, vertex separation, bandwidth, cutwidth, MOSP or a
  `Complex/` problem needs `2^{Ω(n)}` or `2^{Ω(√n)}` time under ETH or
  SETH (held papers first; the citation graph of `paper1/citation_graph.py`
  for the rest): the exact sentence, the reduction it rests on, and its
  status now (void; the question reopened). (b) **Algorithms parameterised
  by pathwidth and treewidth**: the SETH-tight lower bounds
  (Lokshtanov, Marx & Saurabh 2011 on `c^{tw}` for independent set,
  dominating set, `q`-colouring and the rest; Cygan et al.'s Cut & Count
  tightness; Lampis 2025 on SAT by primal pathwidth; others found on
  disk), each void, with the surviving unconditional facts beside them.
  (c) **Where the counting theorem beats the width DPs outright**: for a
  problem solvable in `c^{pw} · poly` given a decomposition, the counting
  theorem's `2^{O(n/√log n)}` (paper form) or the verified form wins once
  `pw` exceeds `n / (log₂ c · √log n)` up to the constants; state the
  crossover as a proposition with the constants left symbolic, tabulate
  it for `c = 2, 3, 4` at `n = 10²…10⁶`, and say which graph classes
  (linear pathwidth: expanders, random graphs by our own first-moment
  floor `β*`, the Chu & Stuckey ridge) are on the far side. (d) **What
  survives**: `P ≠ NP`; `NP ⊄ DTIME(2^{o(N)})` in input length; the Set
  Cover Conjecture, Orthogonal Vectors, 3-SUM, APSP — which are implied
  by SETH alone and so lose their support, which stand on their own —
  one sentence each on whether a `2^{o(n)}` pathwidth algorithm at
  `k = Θ(n)` would touch them; FPT settles `k = o(n^{1/2})` (TASK.md).
  Cross-check that nothing in `paper1/`, `paper2/` or `reports/` rests on
  ETH (the planner found none; confirm). Write §10 in the stance of
  TASK.md: consequences, not hedges, with every item formally
  `SubexpCount k → …`. One subagent at most, for a blind second reading
  of (b)'s list.

- [ ] **11 The write-up: `reports/subexp_pathwidth.md` §0, the note, the CLAUDE.md paragraph (drafted, not applied).**
  §0 in two pages: the question, the premise as a hypothesis, the answer
  as far as it got (the transfer theorem with its Lean name; the class
  result or the obstacle; the measurement; the hypothesis map), and what
  is not claimed. A note *Pathwidth after ETH* as `paper3/pathwidth_after_eth.md`
  (prose only; the LaTeX is the owner's call) with the theorems, the
  table of item 10 and the reductions of item 03. `literature/MISSING.md`
  entries for every paper cited but not held. The CLAUDE.md paragraph in
  the report's last section, in the house style of the loop0013 paragraph,
  **not applied**. Run the full gate.

- [ ] **12 Reserve.** Whichever of 07–09 ended short, one session; or
  the algebraic question item 05 raised most sharply — whether a sum of
  products over a cube can count width-`k` layouts of a *class* (the
  cobipartite cut condition of item 04, the twin-class structure of
  chordal graphs) in the paper's framework, one session with its own
  kill; or an independent re-check of item 08's statement by a refuter
  agent against brute force to 8 vertices with the log kept.
