# loop0005 progress

Plan: `paper2/plan.md` section 3; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0005/gate.py`.

Current: 11/14 SOLVED

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

## Iteration 5 — 2026-09-30 12:47

### Completed
- **05 Interval thickness** — `lean/MOSPFormalization/Complex/IntervalThickness.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** from [9] p. 182 and Möhring pp. 28, 31 (since [5] is not
  held): `IntervalModel α H` (closed intervals of a linear order `α`, distinct
  vertices adjacent iff the intervals intersect), `IsIntervalGraph` (a model in
  `ℕ`), `intervalThickness` = least Mathlib `cliqueNum` over interval
  supergraphs on the same vertex type. Nothing mentions bags.
- **Proved** (Möhring Prop. 3.5, by his two constructions):
  - `intervalThickness_le_pathwidth_add_one`, no hypothesis: "share a bag"
    (`bagGraph`) is an interval supergraph via `[firstBag, lastBag]`, and its
    clique number is ≤ width + 1 by the Helly lemma of `MOSPGraph.lean`.
  - `pathwidth_add_one_le_cliqueNum`: for a model in *any* linear order,
    bags at the sorted left endpoints (`pointDecomposition`) are cliques, so
    pw + 1 ≤ ω(H). So restricting models to `ℕ` changes nothing.
  - `intervalThickness_eq_pathwidth_add_one` under `[Nonempty V]`, and
    `intervalThickness_eq_vertexSeparation_add_one`.
  - Edge case `intervalThickness_of_isEmpty`: `θ = 0`, which matches
    `complex_check`.
- `paper2/equivalences.md`: row 5 updated, and a new section "Item 05".
- Gate passes (1,231 tests).

### Blockers
- None.

### Next
- Item 06 (one-dimensional logic): Ohtsuki's tracks = θ(H) for the
  connection graph. `IntervalModel`, `bagGraph` and
  `pathwidth_add_one_le_cliqueNum` apply directly. The placement gives an
  interval model of the nets, and the track count for a fixed placement is the
  left-edge argument from `GateMatrix.lean` (`tracksFor_eq_maxOpenStacks`).
- Item 10 (node search, ns = θ) can state against `intervalThickness` now.

## Iteration 6 — 2026-09-30 12:56

### Completed
- **06 One-dimensional logic** — `lean/MOSPFormalization/Complex/OneDimLogic.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** from Ohtsuki et al. §II (pp. 676–677): `LogicArray`
  (`v ∈ V(t)`), `IsOhtsuki` (eqs. (3)–(4)), `connectionGraph` (eq. (6)),
  `OnInterval`, `placementGraph π` (interval graph of a gate sequence),
  `tracksFor π` = its chromatic number (least `k` with Mathlib
  `Colorable k`), `tracks` = least over gate sequences, and `tracksPinned`
  for §IV. Nothing mentions stacks, bags or pathwidth.
- **Proved, Ohtsuki's route through interval graphs**:
  - `connectionGraph_le_placementGraph`, `placementModel` (placement graph is
    an interval graph when every net has a gate);
  - `tracksFor_eq_cliqueNum`: χ = ω for placement graphs (the left-edge
    argument of item 03);
  - `exists_placementGraph_le`: Thm 3's inclusion `E* ⊆ Ê` — from any
    interval supergraph `Ĥ`, sorting gates by `d(t) = max_{v∈V(t)} left(v)`
    gives a placement whose graph lies inside `Ĥ` (minimality of the
    augmentation is not needed for the count);
  - `tracks_eq_intervalThickness`: **min tracks = θ(H)** when every net has a
    gate; `tracks_eq_pathwidth_add_one_of_forall_exists` and the
    `IsOhtsuki.*` corollaries via item 05.
- **Also**: `tracks_eq_gateMatrix_tracks` (same value as `t(M)`, no
  hypothesis), `tracks_eq_pathwidth_add_one` (one connection suffices,
  gateless nets allowed), edge cases `tracks_of_isEmpty`,
  `tracks_eq_one_of_forall_not`, and for §IV only the trivial
  `pathwidth_add_one_le_tracksPinned`.
- `paper2/equivalences.md`: row 3 updated, new section "Item 06".

### Blockers
- None for the core problem. The §IV boundary variant is left at its lower
  bound: the observed band `{pw + 1, pw + 2}` has no proof in hand (the
  expected upper bound needs Ohtsuki's B-augmentation argument), and the
  fixed-offset counterexample `boundary_path_instance` would need a case
  analysis over 120 inner-gate orders; it stays with the checker.

### Next
- Item 07 (split bandwidth, Fomin Thm 8). `Sandwich.lean` has
  `pw ≤ bandwidth` for the lower half.
- Item 09 (PLA folding) can reuse `placementGraph`/`colorable_iff_isTrackAssignment`
  style: simple folding is a colouring with colour classes of size ≤ 2.
- Item 10 (node search, ns = θ) can state against `intervalThickness`.

## Iteration 7 — 2026-09-30 13:24

### Completed
- **07 Split bandwidth** — `lean/MOSPFormalization/Complex/SplitBandwidth.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** from Fomin §3.2 (p. 7): `IsNodeSplitting` (one vertex
  becomes an adjacent pair `u, w`, its neighbourhood partitioned into `M`,
  `N`, either empty; vertices named up to a bijection), `IsSplit` (a copy of
  `G` followed by finitely many splittings, an inductive predicate over the
  vertex type), `splitBandwidth` = least `bandwidth` (Sandwich.lean's) over
  finite splits.
- **Proved, Theorem 8 in full, no hypothesis** (Fomin assumes connected,
  ≥ 2 vertices; both halves hold for every finite graph, the empty one
  included): `pathwidth_le_splitBandwidth_le_pathwidth_add_one`.
  - Lower half: `pathwidth_le_of_isNodeSplitting` — the special case of
    minor-monotonicity Fomin's proof uses (merge `u, w` back in every bag; the
    two bag intervals meet at the edge `uw`). General minor-monotonicity was
    not needed and is not formalised. Then `pathwidth_le_bandwidth`.
  - Upper half: not Fomin's route (equal-size bags + `sb = ib`, Thm 6), which
    would need interval bandwidth. Instead an explicit split from an
    in-sequence `σ` of item 04: `v` becomes a path of copies, one per step
    at which `v` is in Kornai & Tuza's shack; edge `uv` attaches at step
    `max(σ u, σ v)`; sorted by `(step, σ v)` its bandwidth is ≤ `ν(σ)`
    (`bandwidth_stage_le`), and it is reached one node splitting per copy
    (`isSplit_stage`). With `ν = pw + 1` (item 04) this is the bound.
- `paper2/equivalences.md`: row 9 (marked **sandwich**, proved), §9 status,
  and a new section "Item 07".

### Blockers
- None. Not formalised, by choice: that both ends are attained
  (`sb(K_{1,3}) = 2 = pw + 1` needs a lower bound over every split of
  `K_{1,3}`; it stays with the checker), and Fomin's Thms 3 and 6
  (`sb = ib = 1/μ_m`).

### Next
- Item 08 (edge separation: Lengauer's VSG = vs, and the star
  counterexample for cutwidth / modified cutwidth).
- `bandwidth_le_of_key` (layout from an injective sorting key) and
  `pathwidth_le_of_map` (pathwidth under a vertex map whose fibres keep the
  interval property) in `SplitBandwidth.lean` are reusable; the
  search games (10–11) may want the latter for 2-expansions (EST Thm 2.2).

## Iteration 8 — 2026-09-30 13:43

### Completed
- **08 Edge separation** — `lean/MOSPFormalization/Complex/EdgeSeparation.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** from Lengauer (1981): the vertex separator game VSG (p. 467:
  `VSGStrategy`, `pebbledAfter`, `vertexCut`, `vsgOfStrategy`,
  `IsPositiveVSG` with `K > 0`, `vsg`); `G_du` (p. 472, `triangleGraph` on
  `V ⊕ G.edgeSet`); min-cut linear arrangement (p. 468, `cutAt`, `cutwidth`);
  MMCLA (Def. 6, p. 473, `modCutAt`, `modCutwidth`); `starGraph n` = `K_{1,n}`.
- **Proved**:
  - `vsg_eq_max`: VSG = max(1, vs); `vsg_eq_pathwidth` for graphs with an
    edge, `vsg_eq_one_of_edgeless` otherwise. The cut after move `i + 1` is
    literally `activeSuffix` at `i` (`vertexCut_succ`), no reversal needed.
  - **Theorem 4**: `vertexSeparation_triangleGraph` / `pathwidth_triangleGraph`
    (`+1` exactly, G with an edge) and Lengauer's form
    `isPositiveVSG_iff_triangleGraph` (G has an edge or K > 0). **Found**: the
    theorem as stated fails at K = 0 on edgeless graphs,
    `isPositiveVSG_triangleGraph_counterexample`. Upper half by Lengauer's
    construction (each e' just before its first endpoint, via a sorting key);
    lower half by a direct induction along the induced layout instead of his
    normal-form Lemma 5.
  - Cutwidth readings false: `pathwidth_le_cutwidth` (one-sided),
    `n ≤ 2 cw(K_{1,n})`, `n ≤ 2 mcw(K_{1,n}) + 2`, `pw(K_{1,n}) ≤ 1`; hence
    `pathwidth_add_two_lt_cutwidth_star7`, `pathwidth_add_two_lt_modCutwidth_star9`,
    and `cutwidth_unbounded` / `modCutwidth_unbounded` (no additive constant).
- `paper2/equivalences.md`: rows 11 and 12 updated; new section "Item 08".
- Gate passes (1,231 tests).

### Blockers
- None. Not formalised, by choice: Thms 2–3 (black–white pebbling, not a
  Table 1 problem), Thm 7 (the MMCLA → VSG NP-hardness blow-up), and exact
  cw / mcw values on stars (only the lower bounds are needed).

### Next
- Item 09 (PLA folding): Möhring Thm 3.14 (multiple folding = θ) and the
  `I_5` counterexample for simple folding. `GateMatrix.lean`'s track
  assignments and `OneDimLogic.lean`'s colouring view apply.
- Reusable here: `exists_layout_vertexSeparation`, `vertexSepOfLayout_le_iff`,
  `exists_vertexSepAt_eq`, `one_le_vertexSeparation`,
  `vertexSeparation_eq_zero_of_edgeless` (`EdgeSeparation.lean`, Helpers);
  item 10 (node search, ns = vs + 1 except on edgeless graphs) needs exactly
  the same edgeless split as `vsg_eq_max`.

## Iteration 9 — 2026-09-30 13:51

### Completed
- **09 PLA folding** — `lean/MOSPFormalization/Complex/PLAFolding.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** from Möhring p. 25 (PLAMPP), on item 03's MPP:
  `IsFolding c π h` (a track assignment of `M^π` with ≤ `c` nets per
  track), `foldTracks c`, `plaTracks = foldTracks 2`. Multiple folding is
  the uncapped case.
- **Proved**:
  - `pathwidth_add_one_le_plaTracks` and `card_le_two_mul_plaTracks`:
    `max(pw + 1, ⌈|N|/2⌉) ≤ pla`, the correct general relation;
    `plaTracks_le_card`.
  - `foldTracks_eq_tracks` / `foldTracks_eq_pathwidth_add_one`: multiple
    folding (`c ≥ |N|`) is exactly `t = pw + 1`.
  - Counterexamples to Table 1's ±1: `plaTracks_idMatrix` (`= ⌈n/2⌉`
    exactly), `plaTracks_idMatrix_five` (3 vs `pw + 1 = 1`),
    `plaTracks_idMatrix_unbounded`; and on a **connected** net graph, the
    path incidence matrix: `netGraph_pathMatrix_connected`,
    `tracks_pathMatrix_le_two`, `plaTracks_pathMatrix_six` (gap ≥ 2 on
    `P_7`), `plaTracks_pathMatrix_unbounded`.
- `paper2/equivalences.md`: row 4 updated, §4 status, new section "Item 09".
- Gate passes (1,231 tests).

### Blockers
- None. Not formalised, by choice: Prop. 3.15 (`|V| − s` over folding
  sets), Thm 3.14 in path-partition vocabulary, Prop. 3.16, block and
  constrained folding. The verdict does not need them.

### Next
- Item 10 (node search, monotone): `ns = vs + 1` with the same edgeless
  split as `vsg_eq_max` (EdgeSeparation.lean helpers).
- `finLayout n` (identity layout on `Fin n`, `finLayout_val`) in
  PLAFolding.lean is reusable for concrete examples.

## Iteration 10 — 2026-09-30 14:07

### Completed
- **10 Node search, monotone** — `lean/MOSPFormalization/Complex/NodeSearch.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** are the game of [9] p. 181 / [10] §2: `SearchState` (guards,
  contaminated edges), `SearchMove` (`place` / `remove`), `searchStep`
  (change guards, clear doubly-guarded edges, recontaminate through
  searcher-free paths, `FreeReach`), `searchCost`, `NoRecontamination`,
  `nodeSearch`, `monotoneNodeSearch`. Same semantics as the checker's
  `node_search`. Nothing mentions layouts.
- **Proved**:
  - `monotoneNodeSearch_eq_vertexSeparation_add_one` ([10] Thm 4.1, monotone
    game, ≥ 1 edge) and `monotoneNodeSearch_eq_pathwidth_add_one`.
    Upper half: `shackStrategy_isMonotone`, Kornai & Tuza's shack process as
    moves, costs exactly `ν(σ)`; with item 04's `ν(σ) = vs(rev σ) + 1`.
    Lower half: `vertexSeparation_add_one_le_of_monotone`, order by the time a
    vertex stops touching contaminated edges.
  - `nodeSearch_le_vertexSeparation_add_one` (full game, no monotonicity
    needed); edge cases `monotoneNodeSearch_of_edgeless`,
    `nodeSearch_of_edgeless` (`= 0`), and the exception is real
    (`monotoneNodeSearch_ne_vertexSeparation_add_one_of_edgeless`).
- **Gap, stated as a Prop, not asserted**: `NodeSearchMonotonicity` (`ns = mns`,
  [10] Thm 2.3 via LaPaugh); `nodeSearch_eq_vertexSeparation_add_one_of_monotonicity`
  derives the full theorem from it. No `sorry`, so `allowed_sorries.txt` is
  unchanged.
- **Found**: [10]'s proof of `vs ≤ ns − 1` (p. 217, claim (2)) orders by first
  acceptance of a searcher, and the claim fails for monotone strategies with
  useless placements: `K_{1,3}`, place/delete each leaf, then search from the
  centre — cost 2, but `|D_{i₀}| = 3`. The theorem survives; ordering by
  clearing time avoids the repair. Checked by hand, not in Lean.
- `paper2/equivalences.md`: row 6, §6 status, new section "Item 10".
- Gate passes (1,231 tests).

### Blockers
- None for the item. The full game (`ns ≥ vs + 1`) needs LaPaugh's
  monotonicity theorem; that is item 14's reserve, not attempted here.

### Next
- Item 11 (edge search, progressive): the game machinery here (`searchStep`
  style, `FreeReach`, `step_remove_subset`, the run lemmas
  `searchCost_append`, `noRecontamination_append`, `runSearch_take_succ`)
  should adapt to the slide move; the `τ`-ordering argument of
  `vertexSeparation_add_one_le_of_monotone` is the likely template for EST
  Lemma 2.1.
- Item 12 (interval thickness = node search): now a two-line corollary of
  `monotoneNodeSearch_eq_pathwidth_add_one` and
  `intervalThickness_eq_pathwidth_add_one` (≥ 1 edge).

## Iteration 11 — 2026-09-30 14:26

### Completed
- **11 Edge search, progressive** — `lean/MOSPFormalization/Complex/EdgeSearch.lean`,
  imported from the root. Sorry-free; axioms `propext`, `Classical.choice`,
  `Quot.sound` only.
- **Definitions** are the game of EST 1994 p. 53 / [10] §2 p. 208:
  `EdgeState` (searcher count per vertex, since `search1` stacks searchers;
  contaminated edges), `EdgeMove` (`place` / `remove` / `slide`), `edgeStep`
  (a slide from a guarded vertex along an edge clears it, then the gas spreads
  through searcher-free paths, reusing item 10's `recontaminate`),
  `edgeCost` (total searchers), `Progressive`, `edgeSearch`,
  `progressiveEdgeSearch`. The source's two clearing cases are one rule,
  "clear, then recontaminate". Same semantics as the checker's `edge_search`.
- **Proved, EST Theorem 2.1 for the progressive game, no hypothesis** (edgeless
  and empty graphs included): `vertexSeparation_le_progressiveEdgeSearch_le_add_two`,
  `pathwidth_le_progressiveEdgeSearch_le_add_two`.
  - Upper half (Lemma 2.2): `edgeStrategy_isProgressive`, EST's `search1` on a
    Kornai–Tuza in-sequence, cost `ν(σ) + 1`; progressive because the cleared
    set stays *safe* (`SafeClear`, `not_mem_of_mem_recontaminate`,
    `edgeStep_of_safe`); the phase induction EST leave as "it can be shown" is
    `edgePhase_spec`.
  - Lower half (Lemma 2.1): `vertexSeparation_le_of_progressive`, not EST's
    argument (first occupation after an irredundancy normal form) but the
    clearing-time order of item 10, with ties broken unguarded-first and
    `clear_step_unique` (one step makes at most one unguarded vertex clear).
- Also: `edgeSearch_le_vertexSeparation_add_two` / `_pathwidth_add_two` (full
  game), [10] p. 209's `mns − 1 ≤ pes ≤ mns + 1` on graphs with an edge,
  `edgeSearch_of_edgeless`, `progressiveEdgeSearch_of_edgeless`.
- **Gap, stated as a Prop, not asserted**: `EdgeSearchMonotonicity` (LaPaugh
  1993); `vertexSeparation_le_edgeSearch_of_monotonicity` derives the missing
  full-game half. No `sorry`; `allowed_sorries.txt` unchanged.
- `paper2/equivalences.md`: row 7, §7 status, new section "Item 11".
- Gate passes (1,231 tests).

### Blockers
- None for the item. Not formalised, by choice: that both band ends are
  attained (needs lower bounds over all strategies on `K₃,₃`), EST Thm 2.2
  (`s = vs` of the 2-expansion), multigraphs/loops. All stay with the checker.

### Next
- Item 12 (interval thickness = node search): a two-line corollary of
  `monotoneNodeSearch_eq_pathwidth_add_one` and
  `intervalThickness_eq_pathwidth_add_one` (≥ 1 edge), plus any Table 1
  counterexample not yet in Lean (check items 01–02's list; cw/mcw and PLA
  are done).
- Item 14's reserve: LaPaugh's theorem would discharge both
  `EdgeSearchMonotonicity` and (via [10] Thm 2.3) `NodeSearchMonotonicity`.
  The `SafeClear` machinery here is the natural starting point for a
  Bienstock–Seymour style proof.
