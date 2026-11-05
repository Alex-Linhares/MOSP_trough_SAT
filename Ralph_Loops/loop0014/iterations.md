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

- [x] **05 The chain count as an algebraic object.**
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

- [x] **06 Algorithms from the counting theorem for problems on graphs of linear pathwidth: the crossover, as algorithms with proofs.**
  For every problem with a published `c^{pw} · poly` or `c^{tw} · poly`
  algorithm given a decomposition (independent set `2`, `q`-colouring `q`,
  dominating set `3`, Cut & Count's connectivity problems, SAT by primal
  pathwidth; take the list from Lokshtanov–Marx–Saurabh 2011, Cygan et al.
  2011/2022, Lampis 2025, each cited), ask whether the problem has a
  bounded-width CNF with `O(n)` variables in the sense of item 01's
  account (one variable per vertex; dominating set only at bounded degree;
  exact Max-Cut and Max-`k`-SAT through the weighted count if §1.3 says the
  method supports `Q[y]/(y^ℓ)` weights — check the paper's Appendix C
  first and cite it where it already says so). For each that does, state
  **the algorithm** (encode, run the counting machine, read the count) with
  **a proof of its running time** `2^{O(n/√log n)} · poly` (paper form) and
  the verified form, and **the crossover proposition**: it beats the
  decomposition DP once `pw > n / (log₂ c · √log n)` up to the constants,
  tabulated for `c = 2, 3, 4` at `n = 10²…10⁶`, with the classes on the far
  side named (linear pathwidth: expanders, `G(n, c/n)` by our `β*`, the
  Chu & Stuckey ridge). Beside each: the SETH-tight lower bound it
  previously carried, now void. Lean (`SubexpPathwidth/Crossover.lean`):
  the crossover inequality as a proposition over the frame of item 02,
  and `SubexpCount k → ` the problem's decision in the stated time for at
  least independent set, with the encoding's correctness proved. Brute
  force to 7 vertices for every encoding. Write §6.

- [ ] **07 New exact algorithms by exact linear transformation, unconditional.**
  (a) The converse of item 03's expansion: vertex separation of a graph of
  maximum degree 3 as the cutwidth of a linear-size graph (or a direct
  argument), so that the published `O(1.89ⁿ)` pathwidth algorithm
  (Kitsunai et al., held) becomes an exact cutwidth algorithm on subcubic
  graphs with base below 2 — where Bentert et al. 2025 state no base below
  2 is known; if the transformation costs a factor `α` in the vertex
  count the base is `1.89^α` and is reported honestly (and compared with
  `2`). (b) Item 04's algorithms stated as algorithms with proofs and
  implemented in `learning/subexp_algorithms.py` with tests: cobipartite
  vertex separation in `O*(2^{max(a, b)})`, vertex separation in `O*(2^u)`
  over twin classes (the equivalent-customers reduction of MOSP with a
  proof), starlike chordal pathwidth in `2^{O(√n)}` for centre `≤ √n`.
  (c) Any further exact transformation at blow-up `≤ 2` found between
  pathwidth and a `Complex/` problem that lacks a base below 2. Every
  algorithm run against brute force on all graphs to 7 vertices and on
  the 149 cobipartite and 252 subcubic atlas graphs. Write §7.

- [ ] **08 Lean for item 07: the transformations' width equivalences and the algorithms' correctness.**
  `SubexpPathwidth/Transform.lean`: the converse transformation of 07(a)
  as a definition and `cw(T(G)) = vs(G)` (or the inequality pair actually
  proved) against `VertexSeparation.lean` and a cutwidth definition stated
  here; the cobipartite normal form (Theorem 4.1) and the twin lemma
  (Theorem 4.4) as theorems, since they are what 07(b)'s algorithms rest
  on. No `sorry`, no `axiom`; axiom audit; a `decide` check on one small
  instance where feasible. Every statement brute-force checked to 7
  vertices before it is stated.

- [ ] **09 The pathwidth complex after ETH: an algorithm with a proof for every Table 1 problem.**
  For every problem of Linhares & Yanasse (2002) Table 1 proved equivalent
  in `lean/MOSPFormalization/Complex/` (gate matrix layout, interval
  thickness, node search, narrowness, one-dimensional logic, MOSP, …) and
  for the sandwiched ones (split bandwidth, edge search): the best exact
  algorithm **now**, as a theorem — `O(1.89ⁿ)` carried through each
  blow-up-1 equivalence (cite the Lean equivalence it rides on, state the
  parameter: `n` customers for MOSP, vertices for the graph problems),
  the sandwiched ones with the base the sandwich allows, cutwidth-like
  ones through item 07 — and, where a problem has a bounded-width
  `O(n)`-variable encoding (none of the ordering problems; say so per
  problem), the counting theorem's time beside it. Then every ETH/SETH
  statement about a complex member (held papers, the citation graph),
  void. The deliverable is a table `problem → algorithm → time → proof
  (Lean name or section)`, with a paragraph per row; prose that is not
  attached to an algorithm or a theorem is cut. Write §9.

- [ ] **10 What fell, and what survives: the maps.**
  (a) every published statement that computing pathwidth, treewidth,
  vertex separation, bandwidth, cutwidth, MOSP or a `Complex/` problem
  needs `2^{Ω(n)}` or `2^{Ω(√n)}` under ETH or SETH (held papers first;
  `paper1/citation_graph.py` for the rest): the sentence, the reduction,
  the status now. (b) The surviving hypotheses (`P ≠ NP`;
  `NP ⊄ DTIME(2^{o(N)})` in input length; Set Cover, Orthogonal Vectors,
  3-SUM, APSP — which stand on their own once SETH is gone) and, for each,
  whether a `2^{o(n)}` pathwidth algorithm at `k = Θ(n)` would touch it;
  FPT settles `k = o(n^{1/2})` (TASK.md). (c) Confirm nothing in
  `paper1/`, `paper2/` or `reports/` rests on ETH. Short, as a reference
  section for items 06 and 09, which carry the mathematics. Write §10.

- [ ] **11 The write-up: `reports/subexp_pathwidth.md` §0, the note, the CLAUDE.md paragraph (drafted, not applied).**
  §0 in two pages, in the stance of TASK.md: the algorithms this loop
  produced with their running times and their Lean names first; the
  crossover; what is unconditional and what is `SubexpCount →`; the
  question at `k = Θ(n)` as it now stands; what is not claimed. A note
  *Pathwidth after ETH* as `paper3/pathwidth_after_eth.md` (prose only)
  organised by algorithm, not by map. `literature/MISSING.md` entries for
  every paper cited but not held. The CLAUDE.md paragraph in the report's
  last section, **not applied**. Run the full gate.

- [ ] **12 Reserve.** The algebraic question item 05 leaves sharpest —
  whether a sum of products over a cube counts width-`k` layouts of a
  class (the cobipartite cut condition, the twin-class structure) in the
  paper's framework, as an algorithm with a proof or a stated obstacle,
  one session with its own kill; or whichever of 06–09 ended short.
