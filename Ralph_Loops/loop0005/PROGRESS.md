# loop0005 progress

Plan: `paper2/plan.md` section 3; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0005/gate.py`.

Current: 4/14 SOLVED

## Setup — 2026-09-30

- Baseline: `lake build` passes; one `sorry` in code (`Sandwich.lean`, the §24
  conjecture, kept on purpose); 1,217 tests pass.
- New Lean goes in `lean/MOSPFormalization/Complex/` (empty), imported from the
  root; it moves to the paper's own repository later.
- Known before the loop starts (from reading the sources, 2026-09-29):
  Kornai & Tuza (1992) Prop. 3.1 is `ν(G) = π(G) + 1` exactly; Fomin (1998)
  Thm 8 is the sandwich `pw ≤ sb ≤ pw + 1`; Lengauer (1981) concerns a vertex
  separator game and says the edge version is min-cut linear arrangement;
  Ellis, Sudborough & Turner (1994) Thm 2.1 is `vs ≤ s ≤ vs + 2`.

## Iteration 1 — 2026-09-30

### Completed
- **01 Statement census** — `paper2/equivalences.md` rewritten: master table
  (12 rows) plus one section per problem, each quoting the source definition
  with page and number, the input, the graph, the exact relation with its
  theorem number, and a status. No code; gate passes (1,217 tests).
- Verdicts: **confirmed** — MOSP (relation not in the cited [1], [4]; it is
  Yanasse 1997a / F&L 1989 Thm 7 / L&Y Prop. 2, already in Lean), gate matrix
  layout (identity map on the matrix, rows = nets = piece types; Möhring
  Thm 3.2, p. 31, Prop. 3.5), one-dimensional logic (Ohtsuki §II–III, Thm 3;
  the boundary-gate variant of §IV is not ±1), narrowness (K&T Prop. 3.1),
  node search (K&P 1985 Thm: ns = θ; K&P 1986 Thm 4.1: ns = vs + 1; both
  false on edgeless graphs, where ns = 0), vertex separation (Kinnersley Thm
  3.1). **Unsourced** — interval thickness at [5]; the relation is proved in
  Möhring Prop. 3.5. **Weaker than stated** — edge search, a band `vs ≤ es ≤
  vs + 2` (K&P 1986 p. 209; EST 1994 Thm 2.1), all three values occur;
  split bandwidth, `pw ≤ sb ≤ pw + 1` (Fomin Thm 8), both values occur (K_2,
  K_{1,3}). Both still satisfy the literal "±1 of open stacks" wording.
  **False** — PLA folding in Möhring's own sense (≤ 2 nets per track, Prop.
  3.15; 5 × 5 identity: tracks 3 vs pw + 1 = 1), though multiple folding is
  exact (Thm 3.14); edge separation, misattributed: Lengauer's edge game is
  cutwidth and his Def. 6 is modified cutwidth, both unbounded against pw on
  stars (K_{1,7}: cw 4; K_{1,9}: mcw 4, checked by a throwaway script); his
  vertex game VSG is vs exactly, and Thms 2–4 are exact transformations.
- Side corrections: Table 1 is on p. 1764 of L&Y 2002, not p. 1762 as
  `paper2/literature/MANIFEST.md` says (not edited — outside this item);
  Fink & Voss transpose the MOSP matrix (rows = patterns); Wing et al.'s full
  problem adds a realizability constraint Table 1's problem drops.
- An eleven-point list of statements for item 02 to brute-force closes the
  file.

### Blockers
- None. Everything is from the held papers; [5] is still not held and the
  interval-thickness row is sourced from [6] and [9] instead.

### Next
- Item 02: the brute-force checker. Open design point recorded in the
  checklist: split bandwidth needs a bound on the number of splittings (or
  compute `ib` over numberings of bounded length, via Fomin Thm 6).
- Items 06, 08, 09 now have settled targets: 06 core problem only (plus the
  boundary counterexample if cheap); 08 VSG = vs, Thm 4, and a star
  counterexample for cutwidth; 09 multiple folding = θ and the identity-matrix
  counterexample for simple folding.

## Iteration 2 — 2026-09-30 12:40

### Completed
- **02 Brute-force checker** — `paper2/complex_check.py` (`python -m
  paper2.complex_check`, ~2.5 min on 32 cores, JSON report in
  `paper2/data/complex_check.json`), 14 tests in `tests/test_complex_check.py`
  (P4, K1,3, C5, K4, K3,3, edgeless, stars, identity matrix, Ohtsuki
  instances; the prefix-set DPs against literal permutation minima). Every
  quantity from its own definition: pw by bag-sequence search, vs / VSG /
  ν / cw / mcw over permutations, θ by interval models (two independent
  searches), node and edge search by game-state search with recontamination
  and in the monotone version, ib by Fomin's numberings via a finite
  automaton (no length bound), sb by explicit splittings (upper bound, six
  graphs), Z / t / PLA / one-dim logic by column order plus explicit track
  assignment.
- Inputs: all 1,252 atlas graphs on 1–7 vertices, 400 random on 7–8, 2,130
  matrices (every class to 4 × 4, 1,500 random 5 × 5), 1,027 random Ohtsuki
  boundary instances. **Zero failures** on every exact statement of item 01
  (MOSP = t = pw + 1, one-dim logic, θ, ν, ns = θ = vs + 1 for ≥ 1 edge, ns = 0
  edgeless, vs = pw, VSG = vs, Lengauer Thms 4 and 7, EST Thm 2.2, the es band
  and the ib sandwich); monotone games equal the full games everywhere. The
  bands are attained: es − vs ∈ {0, 1, 2}, ib − pw ∈ {0, 1}. Counterexamples
  confirmed: cw / mcw off ±1 on 341 / 738 of 1,644 graphs, PLA `I_5` 3 vs 1.
- **One item-01 verdict corrected**: the Ohtsuki boundary-gate family `kK_2`
  was a misreading — eq. (6) builds `H` over all gates, boundary included, and
  there tracks = pw(H) + 1. The boundary variant is a band {pw + 1, pw + 2}
  on everything checked (gap 1 on 47 of 1,027; explicit 5-net path instance
  `boundary_path_instance`). `equivalences.md` §3, row 3 and statement 2
  updated; new section "Item 02: the brute-force check" at the end.
- Gate passes (1,231 tests).

### Blockers
- None. Limits recorded in equivalences.md: sb from its own definition only
  on six graphs (the scale check goes through ib and Fomin Thm 6); Lengauer
  Thm 7 only to N = 4; edge search to 20 edges; whether the boundary gap can
  reach 2 is open.

### Next
- Item 03 (gate matrix layout in Lean): the checker confirms `t = Z` with an
  explicit track assignment, identity map on the matrix. The Lean definition
  should be the track-assignment one (Möhring p. 18), which makes the
  left-edge argument (max column sum = min tracks for intervals) the real
  content of the proof.
- The Lean items can take small counterexamples straight from the checker:
  `I_5` (PLA), `K_{1,7}` / `K_{1,9}` (cw / mcw), K_2 (mcw 0 vs Z 2), the
  boundary path instance (item 06, if the variant is formalised).

## Iteration 3 — 2026-09-30

### Completed
- **03 Gate matrix layout** — `lean/MOSPFormalization/Complex/GateMatrix.lean`,
  imported from the root. Sorry-free; `#print axioms` shows only `propext`,
  `Classical.choice`, `Quot.sound`.
- **Definitions** follow Möhring p. 18: a net–gate relation, the augmented
  matrix `M^π`, "share a gate", track assignments `h : N → Fin k`,
  `tracksFor π`, `tracks = t(M)`, and the net adjacency graph (p. 29).
  Nothing in them mentions stacks or pathwidth.
- **Proved**, all under the hypothesis "M has a 1":
  - `tracksFor_eq_maxOpenStacks`: the left-edge theorem, min tracks for a
    fixed order = max column sum of `M^π`. The lower bound is a pigeonhole;
    the upper bound is greedy colouring by leftmost gate, by
    `Finset.induction_on_max_value`.
  - `tracks_eq_mospValue`: L&Y Prop. 2, identity map on the matrix, no
    transposition.
  - `tracks_eq_pathwidth_add_one`: via `netGraph_eq_mospGraph` and
    `mospValue_eq_pathwidth_add_one`.
- **Degenerate cases**, stated explicitly: `t = 1` on an all-zero matrix with
  at least one net, and `t = 0` with no nets.
- `paper2/equivalences.md`: row 2 updated, and a new section "Item 03".

### Blockers
- None. One convention difference is recorded: on an all-zero matrix,
  `complex_check.gate_matrix_tracks` gives 0 (it drops empty rows) and Lean
  gives 1 (every net gets a track). The two agree whenever M has a 1.

### Next
- Item 04 (narrowness, Kornai & Tuza Prop. 3.1).
- `GateMatrix.lean` gives the pattern for item 09: PLA multiple folding is
  `tracks` with a path-partition constraint. The simple-folding
  counterexample `I_5` needs a cap of two nets per track on top of
  `IsTrackAssignment`.
- Item 06 (one-dimensional logic) can reuse the same track-assignment
  definitions, with gates restricted per Ohtsuki eqs. (3)–(4).

## Iteration 4 — 2026-09-30 12:39

### Completed
- **04 Narrowness** — `lean/MOSPFormalization/Complex/Narrowness.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** are the shack process of Kornai & Tuza §2 (p. 2):
  `MovedAt`, `shackAfterPut`, `shackAfterMove`, `inNarrowness` (the
  maximum over both states of every step), `narrowness`. The out-sequence
  dual is its own process (`EnteredBy`, `outShackBeforeMove`,
  `outShackAfterMove`, `outNarrowness`, `outNarrownessGraph`), not a
  reversal, so Prop. 2.1 says something.
- **Proved**:
  - per sequence, `inNarrowness_eq_vertexSepOfLayout_reverse`:
    `ν(σ) = vs(reverse σ) + 1` when `V` is nonempty. The shack just after
    `vᵢ` enters is `vᵢ` plus the active suffix of the reversed layout at
    `n − 1 − i`. The reversal is there because the development's
    `activeSuffix` counts suffix vertices and the shack counts prefix vertices.
  - Prop. 2.1, as stated (`exists_inNarrowness_iff_exists_outNarrowness`),
    by their proof (`outNarrowness_reverse`), and
    `outNarrownessGraph_eq_narrowness`.
  - Prop. 3.1, `narrowness_eq_pathwidth_add_one` under `[Nonempty V]`,
    through `vertexSeparation_eq_pathwidth`.
  - Edge case: `narrowness_of_isEmpty` (`ν = 0`, the same convention as
    `complex_check`).
- `paper2/equivalences.md`: row 8 updated, and a new section "Item 04".
- Gate passes (1,231 tests).

### Blockers
- None.

### Next
- Item 05 (interval thickness). `reverseLayout` and `sup_comp_rev` in
  `Narrowness.lean` are reusable. `mem_shackAfterPut_iff` already has the
  interval form: `v` is in the shack at `i` iff
  `σ v ≤ i ≤ max_{u ∈ N[v]} σ u`. That is the interval model a layout
  gives, so the layout → interval-supergraph direction of item 05 can
  probably go through the same identity.
