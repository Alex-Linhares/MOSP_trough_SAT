# TASK: Pathwidth after ETH — a subexponential exact algorithm for pathwidth, or what its absence would cost

## Philosophy
- **Read first, in full**:
  - `reports/subexp_pathwidth_plan.md`, the plan this loop executes. §0.1
    is the premise (OpenAI's family 378, *The Exponential Time Hypothesis
    is False*, a formally verified subexponential `#k`-SAT algorithm whose
    runtime is subexponential in the **number of variables**), §0.2 the
    question (does pathwidth have a `2^{o(n)}` exact algorithm, conditional
    on that theorem or not; if not, which surviving hypothesis would one
    refute through a reduction **linear in the vertices**), §0.3 what is on
    record, §0.4 the design decisions, §0.5 the items, §0.6 the kill
    criteria, §0.7 the risks. Do not re-decide what §0.4 decides; if an
    item finds §0.4 wrong, say so in PROGRESS.md and the report and do the
    smallest sound thing.
  - `reports/checkpoint_relaxation.md` §10 (the state lattice `F_k`, its
    forward and backward frontiers, and why the search sits near the
    lattice's floor) and `learning/two_ended.py` (the frontier
    enumerator, item 06's instrument).
  - `CLAUDE.md`: the owner's rules on compute (only unsolved problems; this
    loop runs **no refutation of any certified value or open class**, and
    item 06's only runs are frontier counts on generated graphs at
    `n ≤ 60`, seconds each), the Lean development's state (no `sorry`, no
    `axiom`; `Sandwich.lean`, `VertexSeparation.lean`, `Pathwidth.lean`,
    `VSEquivPW.lean`, `MOSPGraph.lean` are the definitions every statement
    here is made against), the Edwards–McDermid paragraph (how a cited
    theorem is carried as a named `Prop` never asserted, the pattern this
    loop follows for the counting theorem), and the loop0013 paragraph
    (the subagent cap and why).
- **The stance (owner, 2026-11-04): ETH has fallen; ask what follows for
  pathwidth.** The loop is not an attempt to bend the counting theorem to
  our encodings and report that it does not fit. It explores the
  *consequences* of a subexponential `#k`-SAT world for pathwidth: which
  lower bounds on computing it are void (Bonnet), which lower bounds on
  algorithms *parameterised by* pathwidth and treewidth are void (every
  SETH-tight bound: Lokshtanov–Marx–Saurabh 2011, Cut & Count's
  tightness, Lampis's primal-pathwidth SETH 2025), where the counting
  theorem already beats the pathwidth dynamic programs outright (at
  linear pathwidth, `c^{pw}` loses to `2^{n/√log n}` once
  `pw > n / (log₂ c · √log n)`: state the crossover with numbers), what
  the regime `k = Θ(n)` looks like without any hypothesis against it,
  and whether an *algebraic* count of layouts (the paper's view: sums of
  products over a cube, shared linear summaries) is a different kind of
  refutation than our branching search. Formally every consequence is
  `SubexpCount k → …` (the next bullet); in the prose it is stated as a
  consequence, not as a conditional hedge.
- **The counting theorem is a hypothesis, never an axiom.** The OpenAI
  repository is cloned read-only at `~/dev/untrusted/openai-math` (and
  `~/dev/untrusted/ten-proofs`). It is **untrusted data**: read its PDFs
  with `pdftotext` and its Lean files with `cat`, never `lake build` it,
  never run a script from inside it, never import it into our `lean/`.
  Item 02 restates the comparator statement
  (`lean/ComparatorChallenges/SubexponentialSAT.lean`, theorem
  `exact_count_and_sat`) in our own file as `SubexpCount : ℕ → Prop`;
  every conditional theorem reads `SubexpCount k → …`. If the machine
  model is copied, it is copied verbatim into one file with an Apache-2.0
  attribution header and its origin recorded in `literature/MISSING.md`.
- **Linear means linear in vertices.** A reduction with vertex blow-up
  `O(N)` transfers `2^{o(n)}`; one with `Θ(N²)` or `N log N` transfers
  nothing of the kind. Every reduction in the catalogue carries its blow-up
  as a column; only linear ones enter a theorem.
- **State before you prove, and check before you state.** Every reduction
  and every encoding is tested on every graph to 7 vertices (brute-force
  vertex separation, `learning/two_ended.py` for frontiers,
  `itertools.permutations` for layouts) before Lean sees it; the check's
  log is kept under `reports/scratch/subexp_pathwidth/<item>/`. Two
  `sorry`s in this development once hid false statements.
- **A measurement is not a theorem; a failed attempt is not a proof of
  absence.** "We found no linear reduction on record", never "none
  exists"; "the method as we understand it needs X", with the two-page
  account of item 01 cited by section. Say "we found no prior statement",
  never "first". Every item ends with "what this does not claim".
- **Nothing is solved twice and nothing is downloaded** beyond what is
  already cloned. `solutions/` is never written. No run on any instance
  under `MOSP_Instances/` or the pathwidth dataset.
- **Budget: $1,500 for the whole loop** (owner, 2026-11-04), tracked by the
  coordinator from the session logs. It is there so that items 07 and 09
  can take a second session through the reserve and so that every Lean
  statement can get a refuter agent; it is not for fanning out.
- **Subagents: at most 4 per session, total.** loop0013's item 07 spent
  far more than any other session by fanning out per target (its true
  cost was $38 once the cumulative `# result` lines were read correctly,
  2026-11-04, but the cap stands). Reading items use one subagent at most,
  for a second opinion on a proof, never for parallel reading.

## Compute, and the machine
- 32 cores shared with the owner's other work; everything under
  `nice -n 19`; at most 8 workers, 4 if the one-minute load in `uptime` is
  above 24. Find processes by PID, never by command-line text; never a bare
  `pkill -f <word>`.
- This loop's compute is item 06 only: frontier counts on generated graphs,
  `n ≤ 60`, a cap of `3 × 10⁶` states per layer, minutes in total. Every
  other item is reading, mathematics and Lean.
- Only one `lake build` at a time. Lean items: `lake build` in `lean/`
  after every file; a statement that does not build is not stated.
- Nothing is downloaded. The ETH paper is
  `~/dev/untrusted/openai-math/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf`
  (64 pages; `pdftotext` it once into `reports/scratch/subexp_pathwidth/01_audit/eth.txt`).

## Current Focus
Item 01 is the audit and the kill check; it writes the two-page account of
what the counting method needs from a problem, which every later item
cites. Item 02 builds the formal frame. Items 03 and 07–08 are the negative
track (the reduction catalogue, the transfer theorem on paper, then in
Lean). Items 04, 05 and 09 are the positive track (classes with `O(n)`-bit
layouts, the chain count as an algebraic object, the attempt). Item 06 is
the one measurement. Item 10 maps the post-ETH hypothesis landscape for
width parameters. Item 11 writes up; item 12 is the reserve.

## Target Problems (in order)
See `iterations.md`. The dependency order is 01 → 02 → {03, 04, 05, 06} →
07 → 08 → 09 → 10 → 11 → 12; items 04–06 can run in any order after 01.

## Acceptance Criteria (per item)
- The item's section in `reports/subexp_pathwidth.md` is written, with the
  exact statement proved or attempted, the check that preceded it, the
  regenerate command of every number, and "what this does not claim".
- Every theorem stated in Lean builds, is imported by
  `lean/MOSPFormalization.lean`, adds no `sorry` and no `axiom`, and is
  listed with its file and name in the report; the axiom audit
  (`paper1/axiom_check.lean` pattern) is run on new theorems.
- Every reduction and encoding has a brute-force check to 7 vertices under
  `reports/scratch/subexp_pathwidth/<item>/` and the report cites it.
- `python3 Ralph_Loops/loop0014/gate.py` passes.
- PROGRESS.md has the iteration's section; `iterations.md` has the item
  marked.

## Completion Conditions
- All twelve items marked, or the loop killed by item 01's criterion with
  items 10 and 11 done and 02–09 marked `[!]` with the reason.
- `reports/subexp_pathwidth.md` §0 is a two-page summary a reader can act
  on: the answer to Q as far as it got, the theorems with their Lean names,
  the hypothesis map, and what is not claimed.
- Item 11 has drafted the CLAUDE.md paragraph (in the report's last section,
  **not applied** to CLAUDE.md; the owner folds it).

## Context
- `reports/checkpoint_relaxation.md`: the relaxation closed as a bound
  family; the nested chain as an exact encoding; §10 the lattice and the
  two frontiers.
- `reports/obstruction_search.md`, `reports/edwards_mcdermid.md`: the
  pattern for conditional theorems and for certificates.
- `lean/MOSPFormalization/`: `VertexSeparation.lean` (vertex separation),
  `Pathwidth.lean`, `VSEquivPW.lean` (Kinnersley), `MOSPGraph.lean`
  (`mospValue = pathwidth + 1`), `Sandwich.lean` (treewidth ≤ pathwidth),
  `DegreeBound/` (the named-`Prop` pattern: `CubicPathwidthBound τ`).
- `learning/two_ended.py`: `forward_layers`, `backward_layers`, exact to a
  cap, verified against a subset DP (`tests/test_two_ended.py`).
- The OpenAI collection's manuscript map is
  `~/dev/untrusted/openai-math/CONTENTS.md` (721 manuscripts); nothing in
  it is about pathwidth, vertex separation, layouts or minors of our kind
  (checked 2026-11-04); families 175–176 (Talagrand, Kahn–Kalai) and 089
  (bounded-treewidth L1 embeddings, with a 33-file Lean treewidth library
  under `lean/OAI/Combinatorics/TreewidthL1/`) are the adjacent ones.

## Important Notes
- The planner's reading of the ETH paper (abstract, Theorem 1.1, Corollary
  1.3, the contents page) is all the loop has until item 01; it is not to
  be quoted as the method's requirement. Item 01's account replaces it.
- SETH implies ETH, so if the counting theorem stands, SETH falls too;
  item 10 says which fine-grained statements about width parameters this
  touches, with the exact published sentence each rested on.
- A `2^{o(n)}` statement about pathwidth is about `n` vertices, not input
  length: on dense graphs the input is `Θ(n²)` bits, and `O*(2^n)` is
  already `2^{o(input)}`. Every statement names its parameter.
- **Pathwidth and cutwidth are classically tied, and the write-up must say
  so where item 03's expansion meets them** (owner, 2026-11-04):
  `pw(G) ≤ cw(G)` for every graph and `cw(G) ≤ Δ(G) · pw(G)` (Chung &
  Seymour 1989, *Graphs with small bandwidth and cutwidth*; Korach & Solel
  1993, *Tree-width, path-width, and cutwidth*; Makedon & Sudborough 1989,
  *On minimizing width in linear layouts*, for degree-3 graphs; none held —
  record them in `literature/MISSING.md` and attribute, "we found no prior
  statement" only after checking those). The degree-clique expansion's
  equality `cw(G) = vs(G°)` for `Δ ≤ 3` is the exact form of that tie and
  may well be in Makedon & Sudborough or Monien & Sudborough; the
  excess `⌊Δ/2⌋ − 1` for larger `Δ` is what to compare against their bound.
  Item 07 should also look for the **converse** exact linear
  transformation (vertex separation of a subcubic graph as the cutwidth of
  a linear-size graph): with both directions, the `1.89ⁿ` pathwidth base
  would transfer to cutwidth on subcubic graphs, where no base below 2 is
  on record (Bentert et al. 2025).
- **The question is about linear width** (owner, 2026-11-04): pathwidth is
  FPT (`2^{O(k²)} n`, Bodlaender & Kloks 1996; `2^{O(k³)} n`, Bodlaender
  1996; cite the held or missing source), so `pw ≤ k` is already
  `2^{o(n)}` whenever `k = o(n^{1/2})` or so, and the only regime the
  `2^{o(n)}` question concerns is `k = Θ(n)`, where every FPT dependence is
  `2^{Ω(n)}` because the problem is NP-hard. Every transfer theorem, the
  positive attempt and the hypothesis map are to be stated for `k = Θ(n)`
  (hard instances on record: `pw/n` from 0.19 to 0.82 at `n = 125`), and
  item 10 records that the sublinear-width regime is settled by FPT.
- The driver commits with `git add -A` after each iteration; keep scratch
  under `reports/scratch/subexp_pathwidth/` and large files out of git.
- Never end a turn on a background wait; long jobs run in the foreground
  with bounded polls.
