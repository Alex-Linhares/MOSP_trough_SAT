# loop0006 progress

Plan: `paper2/plan.md` section 4 (phase B) and the complex (phase A); items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0006/gate.py`.

Current: 0/13 SOLVED

## Setup — 2026-09-30

- Baseline: loop0005 complete (Table 1 in `lean/MOSPFormalization/Complex/`);
  one `sorry` in code (`Sandwich.lean`, the §24 conjecture); 1,234 tests.
- New Lean for phase B goes in `lean/MOSPFormalization/Search/` (empty).
- Why these two: they are the two open items from `~/dev/pathwidth`'s to-do
  list (`pathwidth_solver/TODO.md`) that loop0005 did not cover. Pebbling is a
  candidate thirteenth member of the complex. The soundness of the pruning rules
  is what every certified refutation rests on; two `better_move` bugs broke it
  and were caught only by testing.
