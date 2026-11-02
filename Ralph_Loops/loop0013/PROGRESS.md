# loop0013 progress

Plan: `reports/obstruction_search_plan.md` — the duality gap of each
lower-bound obstruction family (E expansion, M contraction minors, B
separator branches; C and P on record), found by search across the certified
corpus, the 338 bound-gap instances, the 200 Chu & Stuckey instances and the
24 open dataset classes; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0013/gate.py`.

Current: 0/11 SOLVED

## Setup — 2026-11-02

- **Baseline.** To be recorded by the first session before it starts its
  item: the Lean `sorry` and `axiom` count in code (expected 0 after
  loop0012; the gate's baseline is 0), the test counts of the two pytest
  suites (loop0012's last gate: 1,804 passed in `tests/`, 123 in
  `pathwidth_solver/`), the paper's page count (`paper1/latex/main.pdf`, 77
  pages at loop0012's end).
- **Data on record** (nothing to re-solve): 6,376 certified optima
  (`solutions/`, all `certified:*`); the 338 bound-gap instances
  (`optimum − lb_best ≥ 2` in `learning/data/instances.csv`: 20–134
  customers, gap 2–30, 102 of them Chu & Stuckey); the 200 Chu & Stuckey
  instances (mean gap 0.56 at 30 customers to 14.0 at 125); the dataset's
  16,636 certified classes (430 `certified:minor` with their certificates)
  and its 24 open classes (216–712 vertices, widths 5–11, floors below; one
  is the complete ternary tree of height 5, which the branch lemma closes
  on paper, item 07); the minor certificates of seven instances
  (`reports/minor_bound_verification.md`; `2-2_0` has none at any size
  tried); the harness's verdict that no branching candidate beats
  `max(lb_best, tw + 1)` on any of the 338 (`ml_nature.md` §38) and Lemma
  P's 3 of 338 (`excess_phase_diagram.md` §16).
- **The correction the loop rests on** (plan §0.2): a set found by search
  certifies a *ceiling* for the expansion family, not a bound; the planner
  checked it on 200 random graphs on 8 vertices (the found-set value exceeds
  the pathwidth on 50 of 200; the exact bound holds on all). Nine
  corrections to the brief are in plan §0.4, including that `vsanneal.c`
  anneals layouts and that `paper1.dataset.fold` has no channel for a lower
  bound that does not close a class.
- **Planner's ten-second checks** (plan §0, never quoted as results): the
  200-graph direction check above; the loop cost figures read from the
  session logs of loops 0010–0012 (27 / 40 / 21 sessions, $356 / $389 /
  $212, 10.5 / 11.6 / ≈ 7.2 h).
- **Driver.** `loop.py` and `gate.py` are loop0012's with the loop number
  changed (the item regex passes whole items — 2-space continuation lines,
  no blank line inside an item; checked on the eleven items); `knobs.json`
  unchanged (cap 4 h, fix cap 45 min, 3 fix attempts, 16 iterations);
  `allowed_sorries.txt` empty.
- **Before launch.** Wait for loop0012 to finish (`Ralph_Loops/loop0012/status.json`
  phase `idle`, its last commit in `git log`) and for the working tree to
  be clean under `learning reports tests benchmarks satisfiability mosp
  customer_inter` (the driver refuses to start otherwise; commit or stash
  first). Check by PID whether the owner's `run_unlimited.py` is running
  and leave it its cores. Launch as `Ralph_Loops/Ralph_Loop_Guide.md` "As
  practised here" says, with the API key from
  `~/.config/anthropic/api_key`; never a second driver on this folder. The
  driver stops on the completion marker named in `loop.py`'s docstring;
  only the last session writes it, and this file must not name it before
  then.

---
