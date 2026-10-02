# loop0008 progress

Plan: strengthen paper 2, "The pathwidth complex", toward a first full draft.
Items are in `iterations.md`, rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0008/gate.py`.

Current: 0/9 SOLVED

## Setup — 2026-10-03

- **Baseline.** loop0007 is complete:
  - both solvers apply the repaired rules by default;
  - 111 of the 115 values that rested only on the customer search are
    re-refuted, all unsat, so no certified value changed;
  - `Search/Split.lean` proves the root split sound.

  The one `sorry` in code is the §24 conjecture (`Sandwich.lean`).
- **In flight.** `paper2.solver_fix_split` has a five-day budget to
  2026-10-08, 20 workers, `--parallel`, on the four open 125 × 125 instances:
  `Random-125-125-2-4_0`, `-4-4_0`, `-2-1_0` and `-2-5_0`. Its PID is in
  `paper2/data/solver_fix_split.pid`. Do not touch it.
- **Novelty check so far.** `paper2/prior_art_counterexample.md`: no correction
  found. Chu's 2011 thesis restates Theorem 1 unchanged and states the better
  move with a different premise, and both are false on `cexGraph` by brute
  force. Item 01 widens this, and item 02 puts it in Lean.
- **Driver.** This loop's driver retries a session once, after 300 s, when it
  ends on an error without marking its item. loop0007's last session was lost
  to a network error.

---
