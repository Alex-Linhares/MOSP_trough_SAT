# loop0011 progress

Plan: `reports/separator_moment_plan.md` — counting events (balanced
separators, closed pairs, the weighted count) instead of witnesses (empty
pairs) in the first-moment lower bound on pathwidth; items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0011/gate.py`.

Current: 0/13 SOLVED

## Setup — 2026-11-01

- **Baseline.** Lean: zero `sorry`, zero `axiom` in code (loop0010 left it
  so; the gate's baseline is 0). Tests: 100 test modules (`tests/`), 1,656
  passed at the last gate of loop0010, pathwidth_solver 123. Paper:
  `paper1/latex/main.pdf` builds, 71 pages, Appendix E holds the first
  moment, the generator and the excess subsection; its paragraph "Why the
  first moment is loose" and the section's closing sentence are what item
  12 replaces.
- **Data on record** (nothing to re-solve): the pilot's 6,542 proved
  `G(n, c/n)` graphs with layouts (`reports/scratch/gnp_pilot/results.csv`,
  `n = 20–120`; at `n = 120` only `c ≤ 2` fully proved); 50,716 certified
  random covers in the four ensemble frames; 6,376 corpus instances;
  Harper values on 650 certified `(6, 1)` instances
  (`reports/scratch/structured_count/slack_6_1.csv`); the second-moment
  tables at `(6, 1)` (`second_moment_rate.csv`, `second_moment_125.csv`).
- **Six corrections to the brief, carried into the plan** (§0 of
  `reports/separator_moment_plan.md`): the measured clumping is across
  separators, not within one (§8.5 (a)'s extremal table exchanges `0.057 n`
  vertices with `S`), so the separator count merges only the component
  flips, estimated at `+0.004–0.010` in `β` at `c = 6–10`; the count on
  record has no sub-pairs (exact sizes); "no component larger than `N/2`"
  is a strict relaxation with a cheaper competing route (global thinning)
  at `c′ ≲ 5`, so the bipartition event is what is counted; the kill at
  `c = 6, 10` would miss the near-threshold gains and the threshold
  (`4 ln 2 → 2 ln 2`, conditional on the giant's lower tail), which are
  pre-registered separately; Kloks 1994 is held as a 2-page preview and
  Lee–Lee–Oum is not a first moment; the pilot's exact values at `n = 120`
  exist only for `c ≤ 2`.
- **Planner's estimates** (plan §0; predictions, never results): closed
  pairs `β = 0.1803 / 0.3453` at `c = 6 / 10` against `β* = 0.1706 / 0.3371`;
  the bracket on the inner rate at `c = 3` puts `β_sep(3)` in
  `[0.009, 0.056]` against a fitted slope of `0.099`.
- **Driver.** `loop.py` and `gate.py` are loop0010's with the loop number
  changed (the item regex passes whole items — 2-space continuation lines,
  no blank line inside an item); `knobs.json` unchanged (cap 4 h, fix cap
  45 min, 3 fix attempts, 16 iterations); `allowed_sorries.txt` empty.
- **Before launch.** The driver refuses to start while `git status` shows
  changes under `learning reports tests benchmarks satisfiability mosp
  customer_inter`; commit or stash first (on 2026-11-01 the only changes
  were loop0010's `loop.log` and `status.json`). Check that the owner's
  `run_unlimited.py` is not running (by PID), or leave it its cores.
  Launch as `Ralph_Loops/Ralph_Loop_Guide.md` "As practised here" says,
  with the API key from `~/.config/anthropic/api_key`; never a second
  driver on this folder.

---
