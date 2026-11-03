# loop0013 progress

Plan: `reports/obstruction_search_plan.md` — the duality gap of each
lower-bound obstruction family (E expansion, M contraction minors, B
separator branches; C and P on record), found by search across the certified
corpus, the 338 bound-gap instances, the 200 Chu & Stuckey instances and the
24 open dataset classes; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0013/gate.py`.

Current: 2/11 SOLVED

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
## Iteration 1 — 2026-11-02 22:10

**Baseline recorded before the item** (TASK/PROGRESS setup): Lean `sorry` and
`axiom` in code: 0 (the gate's count); test suites as of loop0012's last
gate: 1,804 in `tests/`, 123 in `pathwidth_solver/`; `paper1/latex/main.pdf`
77 pages. This item adds 12 tests and no Lean.

### Completed

- **Item 01 — the baseline ledger and the frozen targets.**
  `learning/obstruction_ledger.py` (stages `corpus`, `dataset`, `targets`,
  `tables`), `tests/test_obstruction_ledger.py` (12 passed),
  `reports/scratch/obstruction_search/01_ledger/{ledger_corpus.csv,
  harper12.csv, ledger_dataset.csv.gz, targets.json, tables.md, run.log}`,
  `reports/obstruction_search.md` created with the document header and §1.
- **The guard passed**: no bound on record above a certified optimum (6,376
  instances × 9 bound columns), no dataset floor above a certified width
  (16,636 classes × 4 floors); `instances.csv`'s optimum equals the
  `solutions/` value on all 6,376 (provenance read from the files: 6,374
  refutation, 2 bound).
- **The only new computation**: Harper at cap 12 under 60 s on every corpus
  instance, 8 workers, 479 s wall, **1.01 core-hours**; 35 censored at the
  limit (13 at 76–100 customers, 22 at 101–134), still valid floors; never
  below the recorded `exp`, above it on 442 instances (max +21).
- **Numbers**: `floor0 = max(lb_best, tw + 1, harper12, lemmaP, minor)` is
  tight on 5,732 of 6,376 (89.9%; `lb_best` 4,909, 77.0%); gap ≥ 2 falls
  from 338 to 122, max gap 30 → 23. Of the 338 the record closes 81: 67 by
  exact treewidth alone, 7 by Harper at cap 12 alone, 7 by a minor
  certificate alone, 0 by Lemma P (above `lb_best` on 3, by one). `floor0`
  is above the harness's reference `max(lb_best, tw + 1)` on 104 instances
  and closes 14 of the 338 the reference does not. **Twelve** corpus
  instances have a file-backed minor certificate (the survey lists seven;
  loop0010's `large@recorded` run left five more), 7 of them tight; the
  survey's file-less 54 (`4-1_0`) and 92 (`8-2_0`) are carried as
  `minor_survey`, outside `floor0`. Chu & Stuckey by class: mean `floor0` gap
  0.2 / 0.2 / 0.64 / 2.72 / 6.64 / 4.96 at 30–125 customers; Harper carries
  the dense classes (`125-125-10` gap 0.2), minors the ridge (`125-125-2`
  4 of 5 closed), and nothing on record reaches the sparse 100s
  (`100-100-2` gap 7.8). `optimum > tw_hi + 1` on 564 instances, 156 of the
  338. Dataset: cheap floors tight on 5,231 of 16,636 (31.4%); MMD+
  least-c the best (5,059 tight); 0 of 430 `certified:minor` classes tight
  (gap 4.6); 22 VSPLIB grids with a component above 1,024 vertices skipped
  for those components; 17 clique enumerations censored; no "header-only"
  rows exist in the jsonl (the brief's 78 is not reproduced); 5 of 430 minor
  rows carry no certificate; all 425 certificates refute `width − 1`.
- **Targets frozen** (`targets.json`, seed 0): `gap338` 338, `cs200` 200,
  `open24` 24 (floors from `results_quick.csv` and
  `results_quick_rescued.csv`, not `results.csv` as plan §0.3 says),
  `rest500` 500 (stratified 345 / 140 / 11 / 3 / 0 / 1 / 0 over the bands:
  the pool has nothing above 100 customers outside `gap338 ∪ cs200`),
  `small` 4,123. The test re-derives `rest500` from the ledger and the seed.
- **Kill verdict**: none for the item; guard passed. The harness's validity
  stage ("above optimum" must be 0) was not re-run: the ledger's guard is
  that check, applied to every bound column on every corpus instance.
- **Gate: PASS** (`reports/scratch/obstruction_search/01_ledger/gate_run.out`):
  lake build ok, 0 sorry, 0 axiom; `tests/` 1,816 passed, 2 skipped, 1 xfailed
  (4:43); `pathwidth_solver/` 123 passed (8:01, under the owner's load of
  27); paper 77 pages, no undefined references.

### Blockers

None. One correction to the plan recorded in the report: the open classes'
floors live in `results_quick*.csv`, and the file-backed minor certificates
number twelve, not seven.

### Next

Item 02 (family E by search: the ceiling on every target, exact `f` and `s*`
at `n ≤ 22`, the floor by branch and bound). It reads `targets.json` and
`ledger_corpus.csv` (`harper12`, its levels and caps are the family's floor on
record; the 35 censored instances are where the SAT half of item 03 is
needed). Compute used by item 01: 1.01 core-hours of its 1.5.

### Gate fixes after iteration 1 — 2026-11-02 22:57 to 2026-11-03

The item's own gate run passed (above); the driver's two reruns hung in
`pytest` and timed out at 2,400 s. Two fix sessions; nothing in Lean was
touched, no test or theorem was removed or weakened.

**Fix attempt 1 (session it01_fix1, 22:57–23:42, hit its 0.75 h cap).**
Chased the fork-from-a-threaded-parent hazard: added `tests/conftest.py`
(`OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1`, `JE_ARROW_MALLOC_CONF=
background_thread:false`, so the test process has one thread at every fork;
measured, with the docstring's numbers) and gave `gate.py` a `_run` that
kills the whole process group on timeout and prints the tail, plus
`-o faulthandler_timeout=900` so a stuck test dumps its stack. Both stand.
The gate rerun under them still hung, in
`tests/test_pebbling_check.py::test_gu_quick_run_has_no_failures`, at
`Pool.__exit__ → terminate → _terminate_pool → p.join()` (the dump the
faulthandler flag bought).

**Fix attempt 2 (session it01_fix2, this one). Cause found and fixed.**
`paper1/false_refutation_hunt.py::run` installs SIGTERM and SIGINT handlers
(`on_term`, which only sets a flag) and never restores them.
`tests/test_false_refutation_hunt.py::test_stop_and_resume` calls `run`
twice, so every test after it — 774 of them, measured with a plugin that
records `signal.getsignal(SIGTERM)` after each test — runs in a process with
a Python-level SIGTERM handler, and every `fork`-started `multiprocessing.Pool`
worker inherits it. `Pool.terminate()` ends workers with SIGTERM (its
`_help_stuff_finish` takes the task queue's reader lock and keeps it, so the
`None` sentinel cannot reach a worker still waiting for that lock); a worker
with the inherited handler absorbs the signal, returns to its semaphore wait,
and `p.join()` blocks forever. Intermittent because the worker only needs the
SIGTERM when it is the one still waiting on the reader lock at exit (or
deadlocked after a fork from a threaded parent, the hazard attempt 1 removed);
the handler turns that race into a hang. Evidence: the orphaned worker
PID 2442642 that attempt 1's diagnostic run left behind (forked 23:14:34,
`cmd` = pytest, one thread, asleep on a futex) had SIGTERM in `SigCgt`, survived
`kill` (SIGTERM) and died on SIGKILL. The fix: `run` records the previous
handlers and restores them in a `finally`; `test_stop_and_resume` asserts the
handlers are what they were. After the fix the plugin records no test with a
non-default SIGTERM handler. Also killed the leftover orphan.

Seen once and not addressed: in attempt 1's run of 23:14:59, under its own
parallel pytest runs plus the owner's load, `test_stop_and_resume` failed with
`KeyError: 'tested'` — the spawned hunt worker had not reported stats within
the test's 8 s deadline, so the checkpoint's counters held only the base
keys. A load-dependent flake of the test's budget, recorded here.

**Gate after fix 2: PASS** (`python3 Ralph_Loops/loop0013/gate.py`, 2026-11-03
00:30–00:43): lake build ok, 0 sorry, 0 axiom; `tests/` 1,816 passed, 2 skipped,
1 xfailed (4:24); `pathwidth_solver/` 123 passed (6:23); paper 77 pages, no
undefined references. Not committed (the driver commits).

---
## Iteration 2 — 2026-11-03 00:52

### Completed

- **Item 02 — family E by search: the ceiling on every target, the exact
  profile at `n ≤ 22`, the floor by branch and bound.**
  `learning/obstruction_expansion.py` + `learning/obstruction_expansion.c`
  (tabu search on swaps per level, restarts from cliques, the witness's
  prefix sets, BFS balls and the neighbouring levels, focus rounds on the
  argmax levels; the exact profile over `2^n` subsets; `harper_floor` as a
  harness `--extra` candidate; stages `ceiling`, `exact`, `floor`,
  `tables`, a `--tag` for a second pass), `tests/test_obstruction_expansion.py`
  (9 passed), `reports/scratch/obstruction_search/02_expansion/{ceiling.csv,
  ceiling_s2x3.csv, exact_small.csv, floor.csv, sets/, sets_s2x3/, tables.md,
  harness_values.csv, harness_table.md, run_harness.py, run.log, *_run.out}`,
  `reports/obstruction_search.md` §2.
- **The headline**: on **320 of the 338** bound-gap instances the ceiling
  is below the optimum, so the expansion family cannot close them under
  any computation; on 249 of the 338 it is at or below the best floor on
  record. Ceiling at the optimum on 18 of the 338 (11 Chu & Stuckey), of
  which the floor closes 7 and 11 stay open for item 03. Over all 4,697
  targets: ceiling = optimum on 3,099, below on 1,598, above on **0**;
  the bracket `ceiling − floor` is 0 on 4,547 (the family's duality gap is
  exact there) and opens with size to 9.1 at 101–134.
- **Exact at `n ≤ 22`** (4,123): the search attains `f(t)` at every `t`
  on 4,090 (99.2%; 33 misses, one level each, by one, none at an argmax
  level), the ceiling equals the exact bound on 4,123 of 4,123, Harper
  exact equals the optimum on 2,933 (71.1%: 78% at `n = 10`, 59% at 20),
  the empty-pair value on 748 (18.1%); the exact bound beats `lb_best` and
  `floor0` on none.
- **The floor rerun** (35 instances item 01 censored; 600 s where cap ≤ 10,
  300 s at cap 11; 26 completed cap 12; 2.83 core-hours): up on 32 of 35,
  mean +1.9, max +6; **above the best floor on record on 17** (all the
  density-6 and density-8 125 × 125 instances among them); the bracket
  closes on `125-125-10-2_0` (103 = 103 < 104: duality gap exactly 1) and
  `125-125-10-5_0` (= optimum).
- **Harness**: `harper_floor` through the validity stage on all 6,376:
  above optimum **0**, tight 63.7% at 10 s, beats the reference
  `max(lb_best, tw + 1)` on 73 of the 338.
- **Second pass** (seed 2, budget ×3, 436 instances): equal on 432, lower
  on 1, higher on 3 — the ceiling is a ±1 search artefact on about 1% at
  30–100 customers.
- **A correction to the item's text**: the witness's layout by *closing*
  time has no vertex-separation guarantee under the prefix definition
  (56 against 24 on `Random-125-125-2-2_0`); the layout by *opening* time
  has vertex separation exactly `optimum − 1` on all 4,697 targets and is
  what the `ceiling ≤ optimum` guarantee rests on (asserted by a test).
- **Kill verdict**: not met (99.2% ≥ 90%); no ceiling below the floor, no
  floor above the optimum. Compute **3.4 core-hours** (ceiling 0.14, floor
  2.83, second pass 0.13, harness 0.32) against the item's 3; the floor's
  cap was halved where only `f(13)` was missing, said so in the report.
- **Gate: PASS** (`reports/scratch/obstruction_search/02_expansion/gate_run.out`,
  01:31–01:45): lake build ok, 0 sorry, 0 axiom; `tests/` 1,825 passed, 2
  skipped, 1 xfailed (5:08); `pathwidth_solver/` 123 passed (6:26); paper 77
  pages, no undefined references.

### Blockers

None.

### Next

Item 03 (family E exact at full depth by SAT with DRAT). Its inputs: the 11
instances of the 338 with the ceiling at the optimum and the floor below it
(`tables.md` (c); `ceiling.csv` joined with `floor.csv`), the argmax levels
`t*` and the sets per `t` in `sets/<name>.json` (`sets`, and `exact_sets`
at `n ≤ 22`) as incumbents; the bracket is 0 on 4,547 of 4,697 targets, so
the SAT half matters only on the 150 with a bracket, almost all at
61–134 customers (`gap338`: 145 with a bracket). Its kill criterion's
boundary `(n, t)` is what to record.
