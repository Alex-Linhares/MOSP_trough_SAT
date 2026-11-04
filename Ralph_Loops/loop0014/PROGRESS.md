# loop0014 progress

Plan: `reports/subexp_pathwidth_plan.md` — pathwidth after ETH: a
subexponential exact algorithm for pathwidth conditional on the formally
verified subexponential `#k`-SAT theorem (restated as a `Prop`, never
asserted), or a formalised linear reduction naming what such an algorithm
would refute, and a map of the post-ETH hypothesis landscape for width
parameters; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0014/gate.py`.

Current: 0/12 SOLVED

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
