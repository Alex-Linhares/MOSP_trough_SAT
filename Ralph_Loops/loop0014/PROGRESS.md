# loop0014 progress

Plan: `reports/subexp_pathwidth_plan.md` — pathwidth after ETH: a
subexponential exact algorithm for pathwidth conditional on the formally
verified subexponential `#k`-SAT theorem (restated as a `Prop`, never
asserted), or a formalised linear reduction naming what such an algorithm
would refute, and a map of the post-ETH hypothesis landscape for width
parameters; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0014/gate.py`.

Current: 5/12 SOLVED

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

---

## Iteration 4 — 2026-11-04 21:24

Item 04, classes with `O(n)`-bit layouts. Report:
`reports/subexp_pathwidth.md` §4 (what "fits" means §4.0; cobipartite
§4.1; split §4.2; maximum degree 3 §4.3; cocomparability and AT-free
§4.4; chordal, starlike and the clique-tree covers §4.5; the gap lemma
§4.6; the verdict §4.7; checks §4.8). Code: `learning/subexp_classes.py`,
`tests/test_subexp_classes.py` (9 tests). Scratch:
`reports/scratch/subexp_pathwidth/04_classes/` (README with regenerate
commands, `check_atlas7.log`, `check.json`, `gate.log`).

### Completed

- **Cobipartite** (§4.1): Theorem 4.1, some optimal layout places one
  clique entirely first, and with `X` first the value is
  `max(|X| − 1, max_t (t + |N_X(Y_{>t})|))`; Corollary 4.2, the decision
  is a one-sided cut condition — a chain through
  `{S ⊆ Y : |N_X(S)| − |S| ≤ k − |Y|}`. On the doubles of §3.4.1 that
  lattice is `F_k` of `reports/checkpoint_relaxation.md` §10 verbatim, so
  the cobipartite decision *is* item 05's lattice problem with no
  translation. Does not fit. Side remark: exact `vs` on cobipartite
  graphs in `O*(2^{max(a, b)})` (base `1.415` balanced, against `1.89`
  in general); nothing gained on the doubles, as it must be.
- **Split** (§4.2): polynomial, so moot — Gustedt (1993, **held**)
  Lemma 2.8 gives `pw ∈ {ω − 1, ω}` and paper 2 (`polynomial_cases.md`
  §2.2) already has the deciding criterion; here the layout-side proof
  (Theorem 4.3: `vs = κ − 1` iff some clique vertex's independent
  neighbours have a common clique non-neighbour) and the exhaustive
  check. Fits vacuously; contributes no class.
- **Maximum degree 3** (§4.3): the one `O(n)`-bit object, the acyclic
  orientation a layout induces, does not determine the value: on the
  252 subcubic atlas graphs, 11,486 of 20,820 orientations have
  disagreeing linear extensions and 6,791 of 10,607 optimal ones are not
  forced; its residual is a down-set chain, `F_k` again. Does not fit.
- **Cocomparability, AT-free** (§4.4): contain the doubles at blow-up 2,
  so they fit iff all graphs fit. Does not fit, by §4.1.
- **Chordal, starlike, clique-tree covers** (§4.5): Theorem 4.4, the
  twin lemma (true or false twins consecutive in some optimal layout),
  hence `vs` in `O*(2^u)` over twin classes — on MOSP the
  equivalent-customers reduction with a proof. Gustedt's hardness
  instances have `u = O(√n)`, and his Theorem 6.4 (`O(4^{α₀} r + n)`,
  `α₀` the centre) gives **Corollary 4.5: starlike chordal graphs with
  centre `≤ √n` are an NP-hard class on which pathwidth is `2^{O(√n)}`
  unconditionally** — plan §0.2's positive answer in letter and not in
  spirit (the quadratic blow-up of §3.3 seen from the algorithm's side;
  no certificate; nothing of the counting theorem); recorded for items
  07 (no `2^{Ω(n)}` for chordal pathwidth can come from Gustedt's
  construction) and 10. Does not fit: the hard object is a chain over
  the centre or the tree nodes.
- **The gap lemma** (§4.6): a certificate determining the layout's
  prefix sets at every multiple of `g` has `N ≥ n log₂(n/(eg))` bits
  (Lemma 4.6); with the segment encodings on record no `g` fits the
  verified route at any `n`, and on the paper route (R6) the family is
  excluded asymptotically only — the segment width passes `s^{9/10}`
  near `n = 10⁹`, with Theorem D.1's constants unknown. Said as such.
- **Verdict** (§4.7): **item 04's kill is met** — no NP-hard class among
  the five has `O(n)`-bit layouts under bounded-width constraints, and
  each presents the lattice chain in a class-specific form; **item 09 is
  the chain-count attempt only** (plan §0.6), and item 05 may work on
  `F_k` for general graphs without loss.
- **Checks** (§4.8, `python -m learning.subexp_classes`, 36.5 s): the
  normal form on every cobipartition of every atlas graph (149 graphs,
  496 pairs, formula and layouts) and on all 108,622 `A × B` edge sets
  with `a + b ≤ 8`; the split dichotomy and criterion on every split
  partition (257 graphs, 670 pairs) and 300 random split graphs on 11
  vertices; the twin lemma (layouts) and the unit DP on all 1,252 atlas
  graphs: **zero failures everywhere**. Every statement was checked
  before it was written.
- One refuter subagent (the only one used, 1 of 4) read the four proofs
  and Corollary 4.5's arithmetic blind to the rest of §4 with its own
  brute force to 6 vertices. It found **two wrong sentences and two
  gaps, no wrong verdict**: Corollary 4.2's index range (`s < |Y|` for
  `1 ≤ s ≤ |Y|`; 42 brute-force failures as first written — the
  corrected statement is now checked on all 3,653 `(partition, k)`
  decisions to 7 vertices, zero failures, `cobipartite_decision`); the
  twin-class induction order (reverse layout order, else a member is
  stranded); Lemma 4.6's unstated uniformity hypothesis (added, with the
  path-graph argument and a `− 1`); the verified route's constant (now
  `1`, from the `g²` nested-chain variables); and the paper-route table
  mixing the two budgets — recomputed per route, the crossover moves
  from "near `10⁹`" to **beyond `10²⁴`**, so the paper route excludes
  the family asymptotically only, said as such. All folded in; the
  lesson of loop0004 again: a statement checked only in its formula
  form can be wrong in its stated form.
- Gate: `python3 Ralph_Loops/loop0014/gate.py` **PASS** — `lake build` ok
  (no Lean file changed), 0 `sorry`, no `axiom`, tests 1,948 passed /
  2 skipped / 1 xfailed (278 s), `pathwidth_solver` 123 passed (496 s),
  paper check clean; log `04_classes/gate.log`.

### Blockers

None. Not committed (the driver commits). `solutions/` untouched; no
run on any instance; nothing downloaded; no Lean file changed.

### Next

Items 05 and 06 in either order. Item 05 starts from §4.1's identity
(the cobipartite one-sided chain is `F_k` verbatim) and §4.6's last
paragraph: the object it needs must witness reachability in `F_k`
without naming a chain, since every chain-carrying certificate is
excluded. Item 07 should take Corollary 4.5 as a constraint on where a
`2^{Ω(n)}` statement for chordal pathwidth could come from, and Theorem
4.4 is available if a construction needs twins. Item 10 should record
Corollary 4.5 beside Bonnet's `√n` remark.

---

## Iteration 5 — 2026-11-04 22:05

Item 05, the chain count as an algebraic object. Report:
`reports/subexp_pathwidth.md` §5 (conventions and the object §5.0; the
`#SAT` theorem §5.1; the threshold as a polynomial §5.2; ranks and the
interval form §5.3; the exact-count bound §5.4; the sieve over supports
§5.5; one cut in the tensor form §5.6; the obstacle named and the verdict
§5.7; checks §5.8). Code: `learning/subexp_chain.py`,
`tests/test_subexp_chain.py` (9 tests). Scratch:
`reports/scratch/subexp_pathwidth/05_chain/` (README with regenerate
commands, `check_atlas7.log`, `check.json`, `membership_polynomial.csv`,
`split_rank.csv`, `gate.log`).

### Completed

- **The object** (§5.0): `C_k(G) = Σ_σ Π_t [S_t(σ) ∈ L_k]`,
  `L_k = {S : |N(S) ∖ S| ≤ k}` (= `F_{k+1}` of the checkpoint report).
  Lemma 5.1: it equals the number of layouts of `vs ≤ k` (reversal maps
  prefix chains to suffix chains, `∂_in S = ∂(V ∖ S)`), so
  `vs ≤ k ⟺ C_k > 0`. Checked three ways on every atlas graph to 7.
- **The literal answer, yes — in `Θ(n²)` variables** (§5.1, Theorem
  5.2): the nested-chain / position CNF with every auxiliary defined by an
  equivalence (bidirectional OR, bidirectional sequential counter) has
  **exactly `C_k(G)` models**, verified by CaDiCaL enumeration with a
  blocking clause over all variables on every atlas graph to 6 and a
  sample at 7 (1,391 counts, zero failures), sizes against closed forms.
  As equations over a field it is a degree-`≤ 3`, `≤ 8`-monomial system:
  R1, R2, R5 hold; only the budget fails — `n(n − 1) = 15,500` `y`
  variables at `n = 125` against a nominal `B_v = 111`; under
  `SubexpCount 3` it gives `2^{Õ(n² k / √log n)}`, worse than the DP.
- **The threshold as a polynomial** (§5.2): Lemma 5.3 (boundary bit:
  degree `deg + 1`, `2^{deg+1} − 2` monomials), Lemma 5.4 (bare
  threshold: top coefficient `(−1)^{n−k} C(n−1, k)`, so degree `n`; but
  communication rank `≤ min(|A|, |B|, k) + 1` across any split — the
  width compiles away, §1.3.5). The composite `[S ∈ L_k]` measured on
  all 8,475 (graph, `k`) pairs: at `k = vs − 1` degree `= n` on 81.8%,
  median 0.625 of all `2ⁿ` monomials, and **every set variable
  essential on every connected graph (995 of 995)**; `|L_k| / 2ⁿ` 0.28
  at `n = 5–7`. R1 fails for the raw constraint; the dependence on every
  vertex is what does not compile away.
- **Ranks** (§5.3, Lemma 5.5, the interval form of the cut, checked by
  counting on 1,538 (graph, `k`) pairs): `n ⌈log₂ n⌉` variables, `n − 1`
  constraints of width `n ⌈log₂ n⌉`; incidence `Θ(n² log n)`. The item's
  dichotomy is a trade-off and the incidence is `≥ n(n − 1)` either way.
- **The exact count needs `n log₂ n` bits** (§5.4, Lemma 5.6):
  `N ≥ log₂ C_k(G)`, `C_{n−1}(K_n) = n!`; above `B_v` (constant 1) from
  `n = 11`, the ranks within `1 + o(1)` of it. The only escapes are
  weighted factors and decision-only systems — item 09's starting point.
- **The sieve over supports returns the lattice** (§5.5, Lemma 5.7,
  checked on 1,405 identities): `C_k = Σ_S (−1)^{n−|S|} W_k(S)` holds, but
  `W_k(S) = Σ_j c_j(S) h_{n−j}(1..j)` is a lattice sum (state: the
  support, `3ⁿ` in all) and Möbius inversion returns `C_k = C_k`; the
  Hamiltonian sieve runs because its condition is on consecutive pairs.
- **One cut in the tensor form** (§5.6, measured): the composite's
  crossing rank at the best balanced split exceeds the bare threshold's
  bound on 90% of connected 7-vertex graphs at `k = vs − 1`; `C₇` has
  full rank across every split at `k = vs`. No asymptotic claim.
- **Verdict** (§5.7): **plan §0.6's chain-count kill is met, with the
  parenthetical corrected** — the obstacle is structural and it is the
  ordering through its `n − 1` cuts (each reads every vertex; `n − 1`
  distinct sets; incidence `≥ n(n − 1)` in every system on record), not
  the threshold's width, which compiles away at `O(n + Σ deg)` per cut.
  Smallest examples: `K₃` at `k = 1` (full-degree, all-monomial test;
  every chain dies at its first set); the paw at `k = 1` (the first
  refutation needing a second cut); `K_{1,6}` + one leaf edge at `k = 1`
  (frontier `1, 4, 6, 4, 1, 0`: 24 beginnings survive four cuts and die
  at the fifth — §10's binomial frontier from the front). Item 09's
  attempt, if made: a weighted or decision-only system not organised by
  cuts, with the kill stated in §5.7.
- **Checks** (§5.8, `python -m learning.subexp_chain`, 265.6 s after the split fix): 8,475
  chain counts three ways, 1,391 model counts, 1,538 rank counts, 1,405
  sieve identities, 8,475 boundary-bit polynomials, 28 threshold
  coefficients, `K_n` to 7: **zero failures everywhere**. Every
  statement was checked before it was written.
- One refuter subagent (the only one used, 1 of 4) checked every lemma with
  its own code to 5 vertices and the table arithmetic exactly: no lemma
  wrong; it found the `Θ(n²)` headline (counted `Θ(n² k)`), an odd-`n`
  bug in `balanced_splits` that skipped 15 of the 35 splits at `n = 7`
  (fixed, check rerun, §5.6 regenerated, one "full rank" graph withdrawn),
  two over-stated sentences in §5.7 and the `k ≥ n` case of Theorem 5.2.
  All folded in; §5.9 lists them.
- Gate: `python3 Ralph_Loops/loop0014/gate.py` **PASS** twice — once started before
  the split fix (`gate_run1_prefix.log`: 1,958 passed, 123 solver tests) and once on
  the final module (`gate.log`): `lake build` ok (no Lean file changed), 0 `sorry`,
  no `axiom`, tests 1958 passed / 2 skipped / 1 xfailed (277 s),
  `pathwidth_solver` 123 passed (395 s), paper check clean.

### Blockers

None. Not committed (the driver commits). `solutions/` untouched; no
run on any instance; nothing downloaded; no Lean file changed.

### Next

Item 06 (the measurement: `|F_k|` and `|R_f|` on random cubic graphs and
`G(n, 3/n)` to `n = 60`) is the only unmarked item among 03–06; §5.2's
`|L_k| / 2ⁿ ≈ 0.28` at `n ≤ 7` and the binomial frontier of §5.7's
seven-vertex example are the small-`n` end of what it measures. Item 09
now has both kills (04: no class fits; 05: the chain count is organised
by cuts) and §5.7 states what its one-session attempt would be: a
weighted or decision-only system that witnesses `C_k > 0` without
testing cuts — the coordinator may prefer to mark it `[!]` on the two
kills and give the session to item 07's linear construction instead.
Item 07 may use Lemma 5.5 (the interval form) and Lemma 5.1 as stated;
item 10 should record beside Bonnet's `√n` remark that permutation
problems in general (Hamiltonicity, bandwidth, cutwidth, OLA, pathwidth)
are outside the counting theorem's corollaries for the reason §5.4
gives: a permutation witness is `n log₂ n` bits.
