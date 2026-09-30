# loop0005 progress

Plan: `paper2/plan.md` section 3; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0005/gate.py`.

Current: 1/14 SOLVED

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
