# loop0014 progress

Plan: `reports/subexp_pathwidth_plan.md` — pathwidth after ETH: a
subexponential exact algorithm for pathwidth conditional on the formally
verified subexponential `#k`-SAT theorem (restated as a `Prop`, never
asserted), or a formalised linear reduction naming what such an algorithm
would refute, and a map of the post-ETH hypothesis landscape for width
parameters; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0014/gate.py`.

Current: 3/12 SOLVED

## Setup — 2026-11-04

- Driver, gate and knobs cloned from loop0013 (`sed s/loop0013/loop0014/`);
  `allowed_sorries.txt` empty; `max_iterations` 16, item cap 4 h, fix cap
  0.75 h, 3 fix attempts, one retry after a network error.
- The OpenAI collection is cloned read-only under `~/dev/untrusted/`
  (never built, never run from inside); nothing of it is imported into
  `lean/`.
- Tree clean at launch; the last commits are the checkpoint relaxation
  (`3161ff6b2`, `484ca6ff3`), the two-ended measurement (`6869dfba0`) and
  the plan (`bc5ca4cfd`).

---

## Iteration 1 — 2026-11-04 18:35

Item 01, the audit and the kill check. Report: `reports/subexp_pathwidth.md`
§1 (4,300 words; §0 is left for item 11). Scratch:
`reports/scratch/subexp_pathwidth/01_audit/` (README with regenerate
commands; the `pdftotext` extracts git-ignored; the subagent's second
reading committed).

### Completed

- The ETH paper read as the item specifies (Sections 1, 2, 3.5, Lemma 4.8,
  5, 6, Appendices C and D through D.4.2), extracted once to
  `01_audit/eth.txt`; nothing in the untrusted clone built or run. The
  formally verified comparator statement read with `cat`: **it carries the
  weaker exponent** `n (log log n)² / √log n` (Proposition 6.4's route); the
  sharper `n log log n / √log n` and the fixed-density `n / √log n` of
  Theorem 1.1 are paper-only (Appendix D, `lean/docs/378.md` says so).
  Item 02 must restate the verified form, not Theorem 1.1.
- §1.1 (a): the bases. Pathwidth `O(1.89ⁿ)` (Kitsunai et al. 2016, held)
  and `O*(1.9657ⁿ)` (Suchan & Villanger 2009, held); treewidth `1.7549`
  (Fomin & Villanger 2012, not held) and `1.7347` (as recalled, not held);
  cutwidth, OLA, FAS stuck at `O*(2ⁿ)` with no `c < 2` on record (Bentert
  et al. ITCS 2025, held, says so explicitly); bandwidth below 5 (Cygan &
  Pilipczuk 2010, not held, base from memory). **No `2^{o(n)}` exact
  algorithm for any of them is on record.**
- §1.2 (b): ETH/SETH-conditional bounds on *computing* the widths. One
  found, and it matters: **Bonnet (JACM 2025, arXiv 2406.11628; abstract on
  disk in `paper1/data/openalex_candidates.json`, paper not held) proves
  `2^{Ω(n)}` for exact treewidth under ETH by "a simple, self-contained
  reduction from 3-SAT"**, and says the earlier chains through cutwidth /
  pathwidth on bounded-degree graphs gave only `2^{Ω(√n)}`. No sentence of
  the form "no `2^{o(n)}` for pathwidth unless ETH fails" was found in any
  held paper or on-disk title; no SETH bound on computing any width. The
  Lampis primal-pathwidth SETH (SODA 2025) is on disk as a title, for item
  10.
- §1.3 (c): the two-page account. The method computes
  `Σ_x Π_f Φ_f(x|I_f)` over a Boolean cube; the exponent is in the cube's
  dimension (CNF form) or in the number of **wires = total
  variable–constraint incidence** (tensor form, Theorem D.1). Requirements
  R1–R6: bounded-degree factors, **linear total degree (so `O(n)`
  constraints)**, polylog incidence per variable after branching on
  `n/√log n` frequent ones, the separating design (supplied by the paper,
  not the problem), integer counts modulo `2^{n+1}`, and — tensor form —
  vertices of degree up to `s^{9/10}` with `2^{O(s^{9/10})}`-time entries, so
  **a wide threshold constraint costs its width in wires and nothing more**;
  what fixed `k` buys is sparsification (`B = (log n)^{Θ(k)}`) and the
  replacement-row degree. It counts, hence decides, finds witnesses by
  self-reduction, samples uniformly, and takes weights in any commutative
  `Q`-algebra or `(Z/2^P)[V]/(V^ℓ)`. **The budget for pathwidth** (§1.3.8):
  an encoding of "`vs ≤ k`" needs `N = o(n √log n / (log log n)²)` CNF
  variables (verified route) or `s = o(n √log n)` wires (paper route);
  the position and nested-chain encodings are `Θ(n²)`; a layout is
  `n log₂ n` bits, so a witness that determines the layout already exceeds
  the verified budget — the certificate must be another object. Cross-checked
  by one subagent's blind second reading: no disagreement.
- §1.4, the kill check: **not killed** on either criterion (no `2^{o(n)}`
  pathwidth algorithm on record; the method's failure on every NP-hard
  width problem is not demonstrated — nothing is demonstrated either way).
- §1.5 what this does not claim; §1.6 regenerate. `.gitignore` entry for
  the extracts.

### Blockers

None. Subagents used: 1 of 4.

### Next

Item 02 (the formal frame), restating the **verified** statement: for each
`k ≥ 2`, a machine and constants with time
`≤ C (L + 1)^d · 2^{A · n (log log(n+16))² / √log(n+16)}` on every
width-`≤ k` CNF on `n` variables; not Theorem 1.1's sharper exponents. Two
findings for the later items: item 03 should start from Bonnet's reduction
and ask whether its graphs have `pw = tw` (if so, the linear ETH bound
transfers to pathwidth at blow-up 1, and the only hypothesis a `2^{o(n)}`
pathwidth algorithm is known to refute is ETH itself, already refuted);
items 04/05 should look for a certificate of "`vs ≤ k`" with total
incidence `o(n √log n)` and constraints of any width, not for
bounded-width clauses. Missing papers for item 11's `MISSING.md`: listed at
the end of §1.2.

---

## Iteration 2 — 2026-11-04 18:52

Item 02, the formal frame. Report: `reports/subexp_pathwidth.md` §2.
Lean: `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean`
(verbatim copy) and `SubexpPathwidth/Frame.lean` (ours), both imported by
`lean/MOSPFormalization.lean`. Scratch:
`reports/scratch/subexp_pathwidth/02_frame/` (README with regenerate
commands, axiom audit, the textual diff of the hypothesis against the
comparator).

### Completed

- **Decision (§2.1): OpenAI's `PrimitiveMachine` model is copied
  verbatim**, lines 1–190 and 220 of the comparator file (definitions
  only; the theorem and its `sorry` are not copied), under an Apache-2.0
  header naming the origin and commit, byte-for-byte checked, compiling
  unchanged on our Mathlib; origin recorded in `literature/MISSING.md`.
  Reasons: `SubexpCount k` is then the comparator's body character for
  character (`02_frame/body_diff.log`, 23 lines identical); an abstract
  "function with a time function" is provable outright without a cost
  model, so the hypothesis would be vacuous; no proof is copied. The
  price: any transfer theorem will need a machine-composition fact as a
  further named `Prop` (the comparator does not state one).
- `SubexpCount (k : ℕ) : Prop` and `ExactCountAndSat : Prop`
  (`∀ k ≥ 2, SubexpCount k`): `def`s, never proved, never axioms; the
  **verified** exponent `n (log log(n + 16))² / √log(n + 16)`, not Theorem
  1.1's. `SubexpCount.anti` (`k' ≤ k`) proved.
- `PathwidthSubexpOn (C : GraphClass)` and `PathwidthSubexp`: a primitive
  machine decides `pathwidth G ≤ k` on the canonical input `encodeGraph G k`
  (`n`, `k` in the collection's unary code, then the `n²` adjacency bits;
  `encodeGraph_length` proved) within `c (L + 1)^d 2^(f n)`,
  `IsSubexpExponent f := f =o[atTop] n` — the parameter is the vertex
  count, the polynomial factor is in the input length. `GraphClass :=
  ∀ n, SimpleGraph (Fin n) → Prop` (the item's `SimpleGraph → Prop` is not
  a type). The two asked-for lemmas proved: `PathwidthSubexpOn.mono`,
  `pathwidthSubexp_iff`; plus `pathwidthSubexpOn_iff_vertexSeparation`
  (Kinnersley) for item 08.
- Glue (§2.4): `Trace.config_of_locatedStep` (a located trace projects to
  a plain-step trace, so the comparator's time is a bound on
  `machine.step`) and `runtimeScale_isLittleO` /
  `isSubexpExponent_runtimeScale` (the verified exponent is `o(n)`, via
  `(log y)² / √y → 0`), so the hypothesis already has the target's shape
  with the CNF variable count in place of `n` — which is the loop's
  question, §1.3.8 unchanged.
- §2.5 records the exact shape a transfer theorem takes in this frame, in
  both directions, so items 07–09 can see the frame is sufficient.
- Axiom audit: 17 declarations, all on `[propext, Classical.choice,
  Quot.sound]`. `lake build` clean; no `sorry`, no `axiom`;
  `allowed_sorries.txt` still empty.
- No reduction or encoding of pathwidth is stated, so TASK.md's
  brute-force check to 7 vertices has nothing to apply to (README says so).
- One refuter subagent (the only one used, 1 of 4) read both files blind
  to §2 looking for a vacuous or trivially refutable `PathwidthSubexp`:
  none found; its two referee points (the `k` inside `L`; the
  single-machine form against Impagliazzo–Paturi's `∀ ε ∃ machine`) are
  folded into §2.3 and §2.6.
- Gate: `python3 Ralph_Loops/loop0014/gate.py` **PASS** — `lake build` ok,
  0 `sorry`, no `axiom`, tests 1,931 passed / 2 skipped / 1 xfailed
  (535 s), `pathwidth_solver` 123 passed (725 s, under a one-minute load
  of 24), paper check clean.

### Blockers

None. Not committed (the driver commits). `solutions/` untouched; no run
on any instance; nothing downloaded.

### Next

Items 03–06 can run in any order. Item 03 (the reduction catalogue) should
start from Bonnet's 3-SAT → treewidth reduction and the `pw = tw` question
(iteration 1's finding), and define `XSubexp` for its chosen `X` in the
style of `PathwidthSubexp` (§2.5 gives the shape). Whichever of 07 and 09
first needs the machine-composition fact states it as a named `Prop`
(§2.1, item 4), never proves it from the clone.

---

## Iteration 3 — 2026-11-04 19:12

Item 03, the reduction catalogue. Report: `reports/subexp_pathwidth.md` §3
(the table §3.1, the best `X` §3.2, where the classical reductions lose
§3.3, three linear constructions with proofs §3.4, the checks §3.5).
Code: `learning/subexp_reductions.py`, `tests/test_subexp_reductions.py`
(8 tests). Scratch: `reports/scratch/subexp_pathwidth/03_reductions/`
(README with regenerate commands, `check_atlas7.log`, `check.json`,
`explore.py`; the `pdftotext` extracts git-ignored).

### Completed

- **The catalogue** (§3.1, 16 rows): every reduction into pathwidth or
  vertex separation found in the held papers, each with source problem,
  target, construction, target vertex count, exact relation, source,
  held status and the source problem's status after ETH. Read at the
  reduction: Lengauer 1981 Thm 7 (MMCLA → VSG, each vertex an
  `(N+1)`-clique, `N(N+1)` vertices, **quadratic**); Megiddo et al. 1988
  Thm 1 (bisection → edge search, `(n+1)·6n(n+2)(d+K)` vertices,
  **cubic**); Gustedt 1993 Thm 4.1 (VSP → starlike chordal, `n + nm`,
  **quadratic** on 3-regular); Mihai & Todinca 2009 Thms 3–4 (balanced
  0,1-equations → octopus/weighted trees, vertices = the sum of the
  integers, **pseudo-polynomial**); Kinnersley, Fellows & Langston,
  Linhares & Yanasse, Ohtsuki et al., Möhring 1990 (blow-up 1, the
  complex); EST 1994 Thm 2.2 from `equivalences.md` (`es = vs` of the
  2-expansion, `n + 2m`). **Every classical NP-completeness reduction into
  pathwidth is superlinear, by the same mechanism**: clique size
  simulates a weight or an offset (§3.3) — which is Bonnet's `√n` remark
  of §1.2 made concrete. Not held, recorded as unknown: Monien &
  Sudborough 1988, ACP 1987, Bonnet 2025, Kashiwabara & Fujisawa 1979
  (missing, said so). Five held PDFs are scanned with no text layer and
  are listed as such.
- **Three linear constructions, ours, proved and checked** (§3.4): the
  **closed-neighbourhood cobipartite double** `H` (`2n` vertices,
  `vs(H) = vs(G) + n`), so pathwidth on cobipartite graphs — where it
  equals treewidth — is as hard as pathwidth in general at blow-up 2;
  the **clique blow-up** `G[K_c]` (`vs + 1` multiplies by `c`; the
  pathwidth form of BGHK's treewidth amplification); the **degree-clique
  expansion** `G°` (`≤ 3n` vertices, `cw(G) ≤ vs(G°) ≤ cw(G) + ⌊Δ/2⌋ − 1`,
  **equality for maximum degree ≤ 3**, planarity and degree 3 preserved).
  Each was found by brute force on all graphs to 6 vertices (`explore.py`)
  before being stated, then proved, then checked to 7.
- **The best `X`** (§3.2): **cutwidth on graphs of maximum degree 3**
  (planar allowed), by `G ↦ G°`, linear and exact; a `2^{o(n)}` pathwidth
  algorithm would settle Bentert et al.'s explicit open problem for
  cutwidth on that class. Second: treewidth on cobipartite graphs
  (blow-up 1 by Möhring, with the double as converse). Third: MOSP and
  the complex (blow-up 1, the same problem). **No linear reduction from a
  problem with a surviving post-ETH lower bound is on record**: the two
  attributed to such sources (Bonnet from 3-SAT; ACP from bisection) are
  not held. So item 07's theorem is a transfer to cutwidth on subcubic
  graphs and to cobipartite pathwidth, not to a hypothesis (plan §0.6,
  "item 03 lowers item 07's ambition", in that form).
- **Finding for item 04**: no class containing the cobipartite graphs
  (AT-free, co-comparability, every `pw = tw` class of paper 2) can be
  an easier class for the positive track; a positive result there is a
  positive result in general.
- **Checks** (§3.5, `python -m learning.subexp_reductions`, 38.6 s): on
  every atlas graph to 7 vertices (1,252), the subset-DP evaluator agrees
  with the permutation minimum; the double, Möhring's `tw = pw` on the
  doubles and on the 149 cobipartite atlas graphs, the blow-up (`c = 2`
  on all, `c = 3` to 5 vertices), the expansion (lower bound on 696,
  equality on all 253 subcubic graphs, the excess within `⌊Δ/2⌋ − 1` on
  the 443 others and attained at every `Δ`), MOSP both ways (1,169 graphs
  by a pattern-subset DP that shares no code with the layout evaluators;
  4,095 matrices), Lengauer to `N = 4`: **zero failures everywhere**.
- One refuter subagent (the only one used, 1 of 4) read §3.4 blind to
  the rest, looking for a gap in the six proof directions: all six sound; its two editorial points (name the cut at position
  `p` in the `≥` direction of 3.4.1; place the isolated vertices in
  3.4.3) are folded in. Its own brute force (atlas to 6) agreed.
- Gate: `python3 Ralph_Loops/loop0014/gate.py` **PASS** on the second run —
  `lake build` ok (no Lean file changed), 0 `sorry`, no `axiom`, tests
  1,939 passed / 2 skipped / 1 xfailed (526 s), `pathwidth_solver` 123
  passed (730 s), paper check clean (78 pages, no undefined references).
  The first run **timed out** in the `pathwidth_solver` stage (2,400 s)
  inside `tests/test_bench_run.py::test_a_proved_row_and_an_unproved_row`,
  in a native `decide` call that did not return; it was started at a
  one-minute load of 36–51 (the owner's other work) under `nice -n 19`,
  and the same test passes in 0.5 s alone and in the second full run.
  Nothing under `pathwidth_solver/` was changed by this item; the first
  run's log is kept as `03_reductions/gate_attempt1_timeout.log` in case
  it recurs.

### Blockers

None. Not committed (the driver commits). `solutions/` untouched; no run
on any instance; nothing downloaded; no Lean file changed.

### Next

Items 04–06 in any order. Item 04 should take §3.2's finding as its
starting point (cobipartite is not an easier class; the `O(n)`-bit layout
question is the same there as in general) and look at classes that do
**not** contain the cobipartite graphs: bounded degree (where §3.4.3 says
pathwidth on subcubic graphs is at least cutwidth on subcubic graphs),
split, chordal. Item 07 has its `X` (§3.2) and its construction (§3.4.3)
and should state `CutwidthSubexpOn subcubic` in the style of
`PathwidthSubexpOn`; item 08 formalises `vs(G°) = cw(G)` for `Δ ≤ 3`
and `vs(H) = vs(G) + n` against `VertexSeparation.lean`, the two proofs
of §3.4 being written to be taken as they stand.
