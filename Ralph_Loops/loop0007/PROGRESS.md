# loop0007 progress

Plan: fix both solvers to match `lean/MOSPFormalization/Search/` (owner's
decision 2026-10-01); items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0007/gate.py`.

Current: 0/10 SOLVED

## Setup — 2026-10-01

- Baseline: loop0006 complete. The repaired search is proved sound
  (`exec_repairedFullFilter_mospValue`). Chu & Stuckey's Theorems 1 and 2 are
  proved false as stated (`Search/PublishedTheorems.lean`). One `sorry` in code
  (`Sandwich.lean`, the §24 conjecture). 1,327 MOSP tests and 95
  pathwidth_solver tests pass.
- The production code still applies the published rules. No whole-instance
  false refutation is known. The code's runs reach nodes where its filter loses
  the last solution in 58 of 570,206 runs, all on gadget graphs, all at
  satisfiable `k`, and all answered correctly.
- No recertify or csearch process is running. `recertify` ended 2026-09-29
  with two entries open: `Random-125-125-2-2_0` (25) and `Random-125-125-2-3_0`
  (21).
