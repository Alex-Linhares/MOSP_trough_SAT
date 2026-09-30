# loop0005 progress

Plan: `paper2/plan.md` section 3; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0005/gate.py`.

Current: 0/14 SOLVED

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
