# loop0010 progress

Plan: `reports/excess_phase_plan.md` — a one-parameter theory of MOSP in the
excess `e = (n_ones − m) / n`; items in `iterations.md`; rules in `TASK.md`.
Gate: `python3 Ralph_Loops/loop0010/gate.py`.

Current: 0/13 SOLVED

## Setup — 2026-10-31

- **Baseline.** Lean: zero `sorry`, zero `axiom` in code (the §24 conjecture
  was proved before Appendix E; the gate's baseline is 0). Tests: 89 test
  modules. Paper: `paper1/latex/main.pdf` builds, 66 pages, Appendix E
  (`sec9e_appendix_random.tex`) holds the first moment and the generator.
- **Data on record** (nothing to re-solve): 6,376 certified corpus
  instances; 50,716 certified random covers in the four ensemble frames
  (`n = 10–100`, `m / n` ⅛–8, both generators); 7,200 generator simulations
  under `reports/scratch/clique_cover_moment/sim_solutions/`.
- **Three corrections to the brief, carried into the plan** (§0 of
  `reports/excess_phase_plan.md`): the hardest Chu & Stuckey classes
  (`d = 2`) sit at `e = 1.6–2.0`, below the generated-ensemble ridge at
  2–2.4; the incidence graph's giant component appears at `e_g(r) ≈ 0.62`
  (`r = 1`), so `e < 1` is not a forest regime; a second moment of empty
  pairs cannot lift `β*` (it bounds `P(X > 0)` from below), so item 08 is a
  structured count with the second moment as diagnostic.
- **Driver.** `loop.py` is loop0009's with the item regex widened so the
  whole item text (2-space continuation) reaches the session; loop0009's
  passed only the first line. `gate.py` points at `paper1/latex` (the
  paper directory was renamed from `paper2/`) and checks that every Lean
  file, top level included, is imported.
- **Before launch.** The driver refuses to start while `git status` shows
  changes under `learning reports tests benchmarks satisfiability mosp
  customer_inter`; on 2026-10-31 there are 55 untracked scratch files
  under `reports/scratch/`. Commit them or ignore them first. Check that
  the owner's `run_unlimited.py` is not running (by PID), or leave it its
  cores.

---
