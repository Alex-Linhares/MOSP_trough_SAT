# loop0013 progress

Plan: `reports/obstruction_search_plan.md` — the duality gap of each
lower-bound obstruction family (E expansion, M contraction minors, B
separator branches; C and P on record), found by search across the certified
corpus, the 338 bound-gap instances, the 200 Chu & Stuckey instances and the
24 open dataset classes; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0013/gate.py`.

Current: 7/11 SOLVED

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

---
## Iteration 3 — 2026-11-03 01:56

### Completed

- **Item 03 — family E exact at full depth: the inner minimum by SAT with
  DRAT; the bracket closed where it settles.** `exact_sat`, `expansion_cnf`
  (own full totalizer, the contract `ENCODING_SPEC`), `mark_levels`,
  `profile_floor`, stages `sat` and `sat-tables` in
  `learning/obstruction_expansion.py`; `paper1/obstruction_check.py`
  (`check-expansion`: own reader, own graph, own CNF from the contract,
  hash comparison, drat-trim on the regenerated CNF, the bound and its
  theorems; imports nothing from the four project packages);
  `tests/test_obstruction_expansion.py` +6 (24 total, all pass);
  `reports/scratch/obstruction_search/03_sat/{levels.csv, instances.csv,
  boundary.csv, tables.md, joined.csv, checker_verdicts.csv, harness_values.csv,
  harness_table.md, run_harness.py, recheck_certificates.py, certificates/,
  run.log}` and `03_sat_run.out`; `reports/obstruction_search.md` §3.
- **Numbers.** 148 targets had a bracket after item 02 (145 of the 338);
  144 reached in the 6-core-hour cap; the bracket **closed on 72** (the
  family's duality gap now exact on 264 of 338, 193 before), the floor rose
  on 85 (by 1–4), the ceiling fell on 3. Every bracket at 30–60 customers
  closed (68 of 68, in seconds), 2 of 13 at 75, 1 of 41 at 76–100, 0 of 22
  at 101–134. On the 338 the exact floor closes 12 (7 before) and beats
  `max(lb_best, tw + 1)` on 98 (87); 6 stay open with a bracket, all dense
  100–125-customer instances. `scoop-A_FA+AA-_6_0` (79): the SAT answers
  lowered the ceiling to 7 = floor against an optimum of 13 — the family's
  gap on that industrial instance is exactly 6. 344 calls: 155 UNSAT (all
  drat-trim verified), 18 SAT, 79 budget, 92 timeout. **Boundary**:
  `n ≈ 60–75` on the Chu & Stuckey graphs at the argmax levels
  (`t* ≈ 0.2–0.35 n`); all calls at `n ≤ 50` finish, 28 of 52 at 75, 22 of
  108 at 100 (none at the `Random` instances' argmax), 3 of 62 at 125;
  sparse SCOOP instances settle to `t = 52` at `n = 79`.
- **Certificates**: 158 on disk, **158 of 158 verified** by the independent
  checker (`checker_verdicts.csv`), the largest proof 38.7 MB gzipped. The
  proofs total 1.3 GB and are **git-ignored** (`.gitignore`, one rule added:
  `reports/scratch/obstruction_search/**/*.drat.gz`), kept on disk and
  regenerable; the certificate JSONs with the proof hashes are committed.
  **Harness** validity on all 6,376: above optimum **0**, beats the
  reference on 74 of the 338 (the 144 reached instances only).
- **Kill verdict: met** (argmax settled by SAT on 70 of the 145 with a
  bracket, 48.3% < 50%; 20.7% of the 338): "Harper exact is out of reach by
  SAT above cap 12 at 75 customers and beyond; fully in reach to 60". The
  bug condition (UNSAT where the enumeration has a set) occurred on 0 calls.
  Floors downstream: the exact floor where a verified certificate proves it,
  the cap-12 floor elsewhere.
- **One deviation from the item's text**, recorded in §3.1: levels with
  `f̂(t) − t + 1 = floor` are not asked (they can move neither half); the
  item's `≥ floor − 1` includes them.
- **Compute ≈ 6.2 core-hours** (instance time 5.76, checker sweep 0.31,
  harness < 0.01, smoke and probes ≈ 0.1) against the item's 6; load 2–8.
- **Gate: PASS** (`reports/scratch/obstruction_search/03_sat/gate_run.out`):
  lake build ok, 0 sorry, 0 axiom; `tests/` 1,831 passed, 2 skipped, 1 xfailed
  (4:27); `pathwidth_solver/` 123 passed (6:22); paper 77 pages, no undefined
  references. No Lean touched by this item.

### Blockers

None. Three instances not reached at the cap (`Random-125-125-8-5_0` of the
338, `Random-100-50-2-2_0` and `-2-4_0` of `cs200`); their partial
certificates are on disk and verified but outside the tables.

### Next

Item 04 (family M: the contraction-sequence search, its certificate and
checker, the 338 at `n ≤ 60` against the greedy ladder). Family E's floors
for the map (item 08) are `03_sat/instances.csv::floor_after` on the 144
reached instances and `02_expansion` / item 01's `harper12` elsewhere; the
six 338-instances still open with an E bracket are the dense 100–125 ones,
where M and B are the remaining families.

---
## Iteration 4 — 2026-11-03 03:26

### Completed

- **Item 04 — family M by search: the contraction-sequence search, its
  certificate and checker; the 338 at `n ≤ 60` against the greedy ladder.**
  `learning/obstruction_minor.py` (replay on masks mirroring
  `relaxation.minor_groups`'s checks, `repair`, the two greedy rules, the
  lifted-witness and greedy upper bounds, the C-program evaluator with the
  C's minor step off, the tabu search, the ladder, the certificate format
  `obstruction-minor-1`, stages `validate`, `run`, `check`, `tables`);
  `paper1/obstruction_check.py check-minor` (own readers, own replay, the
  quotient from branch sets, own graph6 encoder, the C re-proof at cap ×5,
  `vsmemo` + `checkF` compiled into a temp dir for the rule-free check);
  `tests/test_obstruction_minor.py` (11 passed);
  `reports/scratch/obstruction_search/04_minor/{search.csv, ladder.csv,
  certificates/<instance>/, checker_verdicts.csv, validation.log,
  validation_small.csv, validation_recorded.csv, harness_values.csv,
  harness_table.md, tables.md, joined.csv, run.log, run_harness.py}` and
  `../04_minor_{validate,run,check}.out`; `reports/obstruction_search.md` §4.
- **Validation**: 1,485 minors on 50 corpus instances at `n ≤ 16`, the C's
  proved width against `vertex_separation_brute`: **0 disagreements**; the
  six recorded certificates of `reports/minor_bound_verification.md`
  replay, hash-match and are re-proved by the C at exactly the recorded
  widths (6 of 6; 0.03–28 s).
- **Numbers** (251 instances of `gap338` at `n ≤ 60`, in fact 20–50): the
  family's duality gap is **zero — the search's floor equals the optimum on
  251 of 251**; the ladder's on 222 (88.4%), one short on 29. The record
  (`floor0`) was tight on 70, family E on 8. The search beats the ladder on
  **29 of 251 (11.6%)**, always by one and always to the optimum, by a
  different contraction at a size the ladder already visits (never by a
  larger minor than +9 vertices); never below it. Minimal certifying minor:
  `m / n` median 0.66 (ladder 0.80), falling with `n` (0.75 → 0.51 across
  the bands) and rising with the excess (0.55 → 0.80 across terciles);
  all 251 floors are C refutations on 12–40-vertex minors. **Checker: 251
  of 251 verified on all three checks** (replay + hash, C re-proof,
  rule-free `vsmemo` + `checkF` at ≤ 0.15 s each). **Harness**: above
  optimum **0** on all 6,376; beats the reference on 184 of the 251.
- **Two bugs found in the checker, none in a certificate** (§4.1): its
  partition check first ignored isolated deletions (crash), then missed
  that a deleted "isolated" vertex may carry a whole contracted component
  (5 certificates wrongly rejected), then a sort slip; the regression test
  is `test_checker_accepts_deletion_of_a_contracted_component`. The three
  attempts' outputs are kept (`check_attempt{1,2,3}.out`).
- **Kill verdict: not met** (11.6% ≥ 10%), by a small margin; the honest
  reading in §4.3 (the ladder is never more than one short at these sizes
  and costs a hundredth of the time). Stop conditions did not fire.
- **Compute ≈ 5.6 core-hours** against the item's 8 (search 5.08, of which
  1.02 in the C; ladder 0.007; validation 0.3; checker and harness < 0.05;
  about 0.2 redone after two restarts). The run was stopped and resumed
  twice: at 4 workers when the one-minute load rose to 48–59 from the
  owner's chrome/puppeteer processes after 74 instances, at 8 again when it
  fell to 4 after 114 (`run.log`); the search's wall-clock budgets mean
  the instances under load got fewer moves, nothing else.
- **Gate**: **PASS** (`reports/scratch/obstruction_search/04_minor/gate_run.out`):
  lake build ok, 0 sorry, 0 axiom; `tests/` 1,842 passed, 2 skipped, 1 xfailed
  (4:27); `pathwidth_solver/` 123 passed (6:23); paper 77 pages, no undefined
  references. No Lean and no paper file touched by this item.

### Blockers

None. The 251 are 20–50 customers (the 338 has nothing at 51–60); one
correction to the item's text: the ladder cannot use "the same total
seconds" because it has only 20 points and reaches the optimum in 0.1 s —
the budgets are equal caps, the spent time is not.

### Next

Item 05 (family M at scale: the 87 instances of the 338 above 60 and the
200 Chu & Stuckey, the two ridge instances). Inputs from this item: the
module's `search`, `ladder`, `certificate` and the `check` stage; caps per
plan §0.5 (e) (5 s at 61–100, 10 s at 101–134, 20 s on the ridge pair);
the checker's rule-free half will stop fitting above about 90 vertices
(the record's 87-vertex minor took 255 s and 19.7 GB), so the verdict
there will be replay + C, said so. The C-call overhead (≈ 45 ms per call,
a process start) is the search's bottleneck at small sizes; at 100+
customers the 5–10 s caps dominate instead, so expect a few hundred calls
per instance, not thousands.

---
## Iteration 5 — 2026-11-03 04:50

### Completed

- **Item 05 — family M at scale: the 87 gap instances above 60 customers
  and the 200 Chu & Stuckey; the two ridge instances.** Additions to
  `learning/obstruction_minor.py`: `set_out` (paths under
  `05_minor_scale/`), `cap_for` / `budget_for` (C cap 2 / 5 / 10 s and
  budgets 60 / 120 / 180 / 300 s by band, plan §0.5 (e)), a scheduler in
  `run` that stops starting instances at `--core-hours` (`not_reached.txt`),
  `search(starts=…)`, the `ridge` stage (greedy rules at 100–110 under 120 s,
  then the search at 60 s per call; for `2-3_0` from the recorded 70-vertex
  certificate downward), the C's `nodes=` parsed into every certificate,
  `check` also on `ladder.json` where the ladder is the better certificate
  and on the ridge certificates, the item's tables (`write_tables_scale`),
  carried rows (`carried_item04.csv`) for the 22 Chu & Stuckey gap
  instances at 30–50 that item 04 ran; `tests/test_obstruction_minor.py`
  +6 (17 pass); `reports/scratch/obstruction_search/05_minor_scale/{search.csv,
  ladder.csv, ridge.csv, ridge_summary.csv, certificates/, ridge/,
  carried_item04*, checker_verdicts.csv, harness_values.csv,
  harness_table.md, tables.md, joined.csv, run.log, run_harness.py,
  gate_run.out}` and `../05_minor_scale_{run,small_run,ridge,check}.out`;
  `reports/obstruction_search.md` §5.
- **Numbers.** Family M's floor (ladder or search) is tight on **73 of the
  87** gap instances above 60 (17/17 at 61–75, 43/45 at 76–100, 13/25 at
  101–134; `floor0` was tight on 11, family E on 4) and on **186 of the 200**
  Chu & Stuckey (all 125 at 30–75, 48/50 at 100, 13/25 at 125); with the
  record, **327 of the 338 are closed (324 by family M, 3 by the record) and 11 open**, all `Random-100-100-4`
  and `Random-125-125-4/6` — the dense shoulder, where item 03's six E
  brackets are. M is at least as tight as E on every one of the 200 (tighter
  on 142, tied on 58): the record's expectation "expansion on the dense
  classes" holds only at density 10, where the two tie. The search beats
  the ladder on 60 of the 185 run (by 1 / 2 / 3 on 44 / 14 / 2), on 41 of
  them with a minor above 95% of the vertices (the ladder's grid stops at
  95%: a grid artefact, a 97–99% rung proposed, not applied), and finishes
  below it on 3 (the budget binds at 5–10 s per call; the ladder's
  certificate is the family's there, checked). The record's seven:
  `8-2_0` **93 = optimum** at 118 (survey 92); `SP4` 53 at 90 (record 96);
  `2-3_0` 21 at 53 and **51** (record 70); `2-2_0` 24 at 70; `2-1_0`,
  `4-1_0`, `6-1_0` one below the record's 87–120-vertex minors, whose
  refutations took 28–80 s against this item's 10 s cap. Ridge: `2-2_0`
  — five distinct greedy minors at 100–110 all `upper` after 120 s (width
  23 found at 100: that minor cannot certify 25), 50 search calls at
  97–107 all `upper` (22 proved useless, 28 undecided), **no certificate
  for 25 within one core-hour**, a recorded negative; `2-3_0` — the greedy
  minors at 100–110 do not refute 20 in 120 s while the recorded 70-vertex
  one does in 757,009 nodes (the record's count exactly), and the search
  shrank it to a **51-vertex minor refuting 19 in 145,355 nodes, 0.12 s**,
  rule-free verified (367 candidates at 50 all have pathwidth 19).
- **Checker: 190 of 190 verified** (185 search, 3 ladder, 2 ridge; C
  re-proof on all; rule-free on the 137 with m ≤ 80). **Harness**: above
  optimum **0** on all 6,376; beats the reference on 87 of the 338.
- **Kill verdict (the 338 as a whole): not met** — the search beats the
  ladder on 45 of 338 (29 + 16), 13.3% ≥ 10%; the honest reading as in §4.3.
  No stop condition fired. The 18-core-hour driver stop was not reached.
- **Compute ≈ 10.6 core-hours** of the item's 22: main run 6.56 (107 at
  61–134, 3,111 s wall at 8 workers, load 8–10) + 1.88 (78 at 30–50) —
  ladder 0.31, search 8.13 of which 3.35 in the C (278,571 calls); ridge
  2.0; checker 0.15; harness 0.01.
- **One slip, repaired**: the module's `log` bound its default path at
  import time, so the main run's progress lines went to
  `04_minor/run.log`; the default is now resolved at call time, 05's
  `run.log` was rebuilt from the stdout captures (130 lines) and 04's
  restored from git.
- **Gate: PASS** (`reports/scratch/obstruction_search/05_minor_scale/gate_run.out`):
  lake build ok, 0 sorry, 0 axiom; `tests/` 1,848 passed, 2 skipped, 1 xfailed
  (4:30); `pathwidth_solver/` 123 passed (6:22); paper 77 pages, no undefined
  references. No Lean and no paper file touched by this item.

### Blockers

None. The item's count of "262 distinct" is the planner's: the union is
207 (87 + 200 − 80 shared above 60). The rule-free check was capped at
120 s (item 04: 300 s) and skipped above 80 vertices, as the item says.

### Next

Item 06 (family B: separators with certified branches on the residual gap
instances). The residual after items 03–05 is 11 instances of the 338
(`Random-100-100-4-1_0`, `-4-3_0`, `Random-125-125-4-{1..4}_0`,
`Random-125-125-6-{2..5}_0`; `tables.md` of this item and `joined.csv`'s
`gb` column), plus the family-E and family-M floors for the map: M's are
`05_minor_scale/joined.csv::best` (ladder or search, in optimum units) on
the 207 and `04_minor/search.csv::search_floor` on the 251.

---
## Iteration 6 — 2026-11-03 07:15

### Completed

- **Item 06 — family B: separators with certified branches on the residual
  gap instances; the trees-of-cliques family.**
  `learning/obstruction_branch.py` (components, connectivity and the link
  condition on bit masks; a leaf oracle with the C program at cap 5 s, the
  clique and trivial nodes, family M's ladder on a branch as the `minor`
  leaf; the branch rule at depth 2 memoised by vertex set; the separator
  family plus a tabu local search over `S`, `|S| ≤ 6`, tenure 5; a **lazy
  evaluation with upper bounds** so a branch goes to the C program only
  while it could raise the value, which also yields `b_potential`, a
  ceiling at the separators tried; the certificate format
  `obstruction-branch-1`; stages `hand`, `run`, `check`, `connectivity`,
  `tables`); `paper1/obstruction_check.py check-branch` (own BFS, own
  relabelling and graph6, the C re-run per `c` leaf, `check-minor` per
  `minor` leaf, recursion over nested nodes); `tests/test_obstruction_branch.py`
  (16 passed); `reports/scratch/obstruction_search/06_branch/{search.csv,
  joined.csv, certificates/ (156), checker_verdicts.csv, connectivity.csv,
  hand.csv, harness_values.csv, harness_table.md, tables.md, run.log,
  run_harness.py, pass1/, gate_run.out}` and `../06_branch_{run,check,
  harness,connectivity}.out`; `reports/obstruction_search.md` §6.
- **Numbers.** Residual (11, all dense 100–125 Chu & Stuckey): **unchanged,
  11 of 11** — no linked triple on 8, values 2–3 on 3 against optima
  25–80 (the separators found isolate one to three fringe customers:
  branch sizes `[94, 1, 1]`, `[118, 1, 1]`, `[112, 3, 2]`); vertex
  connectivity 1–3 on seven, 6 on one, 7–12 on three. All 338: a linked
  triple on 156, **B closes 0, exceeds the record on 0, exceeds the
  reference on 1** (`p2050n1_0`: three branches of pathwidth 4 at a
  4-separator, value 6 against optimum 7); the value is below ω on 147 of
  156; mean gap 11.7 where a triple exists, and the potential's mean gap
  is 11.6, so the leaves are essentially exact and the shortfall is the
  third-largest branch. §38's seeded `sep_branch` was above its seed on 0
  of 338; exact widths beat it on 1. Depth 2 used on 0 certificates; the
  `minor` leaf fired on 8 instances and improved none; `|S| = 6` on 72 of
  156. Hand instances 7 of 7 agree with the seeded form. Checker **156 of
  156 verified** (624 nodes, 187 C re-runs). Harness on all 6,376: above
  optimum **0**, beats the reference on 1 of the 338.
- **Kill verdict: met — "branching is closed"**; exact branch widths
  changed exactly one value, by one, on an instance family M had closed.
  No stop condition fired.
- **Two deviations recorded in §6.1**: the item's "M certificate from item
  04/05" cannot restrict to an induced subgraph, so the `minor` leaf runs
  the ladder on the branch; the mask-level link condition replaces the
  harness's `linked_third` inside the search and is pinned equal to it by
  a test. The item's "spider of spiders 3" is 4 in optimum units.
- **Compute ≈ 1.0 core-hour** of the item's 4 (final pass 0.47, of which
  168 s in 347 C calls; a first pass 0.48 whose values agree on 338 of
  338; connectivity, checker 0.07, harness < 0.01). Load 0.2–4 throughout.
- **Gate: PASS** (`reports/scratch/obstruction_search/06_branch/gate_run.out`,
  07:05–07:15): lake build ok, 0 sorry, 0 axiom; `tests/` 1,864 passed, 2
  skipped, 1 xfailed (4:31); `pathwidth_solver/` 123 passed (6:21); paper 77
  pages, no undefined references. No Lean and no paper file touched by this
  item.

### Blockers

None.

### Next

Item 07 (the 24 open classes: family E's ceiling, M and B as lower-bound
searches only; `BalancedTree_3_5` by the branch lemma as a nested B
certificate). Inputs from this item: `branch_search(adj, …)` takes any
graph as masks (a dataset class's edge list through `minor_masks`);
`certificate_dict` with `matrix=None` for an edge-list instance; the
checker accepts an edge-list instance (`.txt`) and nested `branch` nodes of
any depth, with `trivial` leaves of claim 0 (the tree's height-1 stars give
`k = 0` at the leaves); `check-branch` re-runs the C only on `c` nodes, so
a certificate built from `branch` and `trivial` nodes alone is checked
without the C program. Family B's floors for the map (item 08) are
`06_branch/joined.csv::b_value` (NaN where no triple) with `b_floor =
max(b_value, ω)` beside it.

---
## Iteration 7 — 2026-11-03 07:27

### Completed

- **Item 07 — the 24 open classes: family E's ceiling, M and B as
  lower-bound searches only; `BalancedTree_3_5` by the branch lemma; the
  evidence rows.** `learning/obstruction_ledger.py::open_class_graphs` (the
  24 as graphs with the stored layout in its prefix orientation — vertex
  separation = recorded width on all 24 — and the representative computed
  as `fold` does, matching the record edge for edge on all 24);
  `learning/obstruction_branch.py` (`ternary_tree_certificate`, stages
  `open-tree` and `open`; the leaf oracle takes a recorded layout as its
  upper bound and a size cap above which no C call is made);
  `learning/obstruction_minor.py` (stage `open` with the 30–85% window
  enforced in the evaluator before any C call, `open-check`, `open-tables`,
  the evidence rows); `learning/obstruction_expansion.py` (`--targets
  open24`; the C helper's cap raised from 256 to 768 vertices, `MAXW 12`);
  `tests/test_obstruction_open.py` (11 passed);
  `reports/scratch/obstruction_search/07_open/{tree_certificate.json,
  tree_instance.txt, ceiling.csv, sets/, minor.csv, branch.csv, certificates/
  (23), checker_verdicts.csv (47), joined.csv, tables.md,
  results_obstruction.csv, lower_bounds.csv, open_runs_proposal.diff,
  run.log, gate_run.out}` and `../07_open_*.out`; `reports/obstruction_search.md` §7.
- **Two classes closed.** `pwc-15933` (`BalancedTree_3_5`, 364 vertices):
  the branch lemma down the tree as a nested B certificate (121 `branch`
  nodes, 243 `trivial` leaves), `pw ≥ 5` = the stored layout's width,
  verified by the checker with 0 C re-runs (the C program had spent 236.7
  core-hours on it); the value is Ellis, Sudborough & Turner (1994)'s, the
  certificate is new to the record. **`pwc-17632` (`NY_13`, PACE 2017
  bonus, 283 vertices, recorded width 10, floor 9): family M's search found
  an 85-vertex contraction minor of pathwidth 10** (refutes 9 in 67,455
  nodes, 0.07 s; 236.7 core-hours on the whole graph had found nothing),
  verified on all three checks including the rule-free one (1.17 M refuted
  prefixes, 1.9 s) — `pw(NY_13) = 10`. The one class where the search beat
  the greedy ladder.
- **The other 22**: family M's floor is `width − 1` on 21 (and `width − 2` on
  `494_bus`), each a C refutation on a minor at the 30% rung (37–39% on 3)
  whose pathwidth the C re-proves exactly, so on 21 classes the truth is
  `width − 1` or `width`; five floors rise above the record (2 → 7, 3 → 9,
  2 → 8, 3 → 9, 9 → 10). **Harper's ceiling is below the recorded width on
  all 24** (by 1–5; on the tree 4 against the proved 5): the expansion
  family cannot close any of them under any computation. Family B: values
  2–5, above the record on 2, never above M (fringes only). Checker: 47 of
  47 verified, no contradiction.
- **Evidence rows**: `results_obstruction.csv` (2 rows in
  `run_unlimited.py`'s `FIELDS`, representative's labels, `order` checked
  with `layout_width`; `NY_13` as `proof=minor` with the certificate,
  replayed by `dataset_check.py`'s own code; the tree as `proof=theorem`,
  which `fold` does not read) and `lower_bounds.csv` (4). The `OPEN_RUNS`
  line is **proposed, not applied** (`open_runs_proposal.diff`): with the
  `NY_13` row, `fold` would emit a new `certified:minor` record, i.e. a
  dataset rebuild, which the item forbids; `paper1/dataset.py` untouched.
- **Kill verdict: not met** (one new floor meets its width); no stop
  condition fired (no floor above a width, no rejected certificate).
  Harness validity stage not applicable (no certified optimum on an open
  class): the stored layouts and the checker stand in.
- **Deviations from the item's text**, recorded in §7.1: the ladder and
  the search share one 900 s budget per class (the ladder alone costs up to
  24 × 20 s); B ran 240 s per class with no minor leaves; the E, M and B
  runs ran beside each other (4 + 2 + 2 processes, load 4–7).
- **Compute ≈ 7.1 core-hours** of the item's 10 (M 5.75, E 0.50, B 0.39,
  checks 0.42, smoke 0.06). The first E launch failed on the 256-vertex cap
  and appended its lines to `02_expansion/run.log`, restored from git.
- **Gate: PASS** (`reports/scratch/obstruction_search/07_open/gate_run.out`,
  09:08–09:20): lake build ok, 0 sorry, 0 axiom; `tests/` 1,875 passed, 2
  skipped, 1 xfailed (4:34); `pathwidth_solver/` 123 passed (6:23); paper 77
  pages, no undefined references. No Lean and no paper file touched by this
  item.

### Blockers

None.

### Next

Item 08 (the duality-gap map). Family floors for the map: E
`03_sat/instances.csv::floor_after` on the 144 reached, `harper12` elsewhere,
ceilings in `02_expansion/ceiling.csv`; M `05_minor_scale/joined.csv::best`
and `04_minor/search.csv::search_floor`; B `06_branch/joined.csv::b_value`;
the open classes in `07_open/joined.csv` (pathwidth units). Two findings
for item 10's summary: on the 24 open classes Harper's ceiling is below the
width everywhere, and a searched 85-vertex minor closed `NY_13` where
236.7 core-hours of whole-graph search had not.
