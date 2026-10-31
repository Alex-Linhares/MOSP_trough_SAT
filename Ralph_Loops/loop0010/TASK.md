# TASK: A one-parameter theory of MOSP in the excess, on random and industrial instances

## Philosophy
- **Read first, in full**:
  - `reports/excess_phase_plan.md`, the plan this loop executes: the
    parameter, what stands, the questions, and the three places the record
    corrects the brief that produced it.
  - `CLAUDE.md`: the owner's rules on compute (only unsolved problems; never
    the Python pathwidth solver; never `solutions_dir=None`), what is proved
    and what is measured, and "Lessons that cost sessions".
  - `reports/random_graph_first_moment.md` (Theorems A, A′, A″, B on
    `G(n, c/n)`), `reports/scratch/clique_cover_moment/README.md` and
    `REPORT_generator.md` (the clique-cover first moment, the fitted
    generator, the threshold `e > 1`), `paper1/latex/sec9e_appendix_random.tex`
    (how the paper states it now), and `reports/ml_nature.md` §25, §36, §37
    (the ridge as excess; what it is a transition of).
  - The Lean headers: `lean/MOSPFormalization/EmptyPair.lean`,
    `FirstMoment.lean`, `FirstMomentAsymptotics.lean`,
    `CliqueCoverMoment.lean`, `TreeBound.lean`, `Sandwich.lean`
    (`branch_lemma`), `IndependenceBound.lean`.
- **The parameter.** `e = (n_ones − m) / n`: mean patterns per customer
  minus one; `r (c − 1)` for `r = m / n`, `c` customers per pattern; and
  `e − 1 + κ / n` is the cyclomatic number per customer of the incidence
  graph (`κ` its components). Use realised `e` from the matrix, never the
  nominal `r (d − 1)`: the generators' repairs inflate it.
- **Nothing is solved twice.** About 50,700 certified random clique covers
  (`learning/data/ensemble/results*.csv`, `n = 10–100`, `m / n` from ⅛ to
  8, both generators), 7,200 generator simulations
  (`reports/scratch/clique_cover_moment/floor_violation.csv`) and the 6,376
  corpus instances carry exact optima already. Scoring runs on them (the
  two-key rule, bounds, features) are free; re-solving them is forbidden
  without the owner's word. New exact solves are allowed only where an item
  says so, priced first with `learning.cost_model`, and witnesses are
  always persisted (`learning/data/ensemble/solutions/` for ensemble cells,
  a named scratch `solutions_dir` otherwise; never `solutions_dir=None`;
  never `solutions/`). Pathwidth of graphs that are not MOSP instances goes
  through the C program `pathwidth_solver/cli/pathwidth`, never the Python
  solver.
- **State before you prove, and check before you state.** Every statement
  that will be called a theorem — on paper or in Lean — is first checked
  by brute force on small instances, and the check's script and log are
  kept. Two earlier `sorry`s in this development hid false statements, not
  hard ones.
- **A measurement is not a theorem; a first moment is not the constant;
  24 industrial instances are 24 instances.** Every number carries its
  size range and its regenerate command. Every item ends with "what this
  does not claim". Say "we found no prior statement", never "first".
- **Nodes, not seconds**, with seconds beside them; a censored run is a
  lower bound, never a value.

## Compute, and the machine
- 32 cores, shared with the owner's other projects; the load is often above
  24 from work that is not ours. Every process under `nice -n 19`; at most
  8 workers, 4 if the one-minute load in `uptime` is above 24. Check
  `uptime` before anything parallel. Find processes by PID, never by
  command-line text; never a bare `pkill -f <word>`.
- The owner's `reports/scratch/dataset_open/run_unlimited.py` (24 workers at
  nice 19) may be running or may be restarted at any time; it must not be
  disturbed, and its idle cores are the owner's, not ours.
- Budgets per item are in `iterations.md`; the loop's total is about 25
  core-hours. Long jobs run in the foreground with bounded polls; never end
  a turn on a background wait.

## Current Focus
Items 01–04 measure (the map, `opt / n` against `e`, the forest regime by
brute force, the SCOOP instances). Items 05–10 analyse (`β⁺` by simulation,
the forest theorem, `β⁺` on paper, the structured count, the ridge
hypothesis, validity under the real generator). Item 11 is Lean, 12 the
write-up, 13 the reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration; the
item's full text is in the prompt and in the file.

## Acceptance Criteria (per item)
- [ ] The deliverable exists where the item says, states its size range,
      gives its regenerate command, has a kill verdict (met / not met /
      none), and says what it does not claim.
- [ ] New code has tests under `tests/`; new Lean has no `sorry` and no
      `axiom` and is imported by `lean/MOSPFormalization.lean`.
- [ ] `python3 Ralph_Loops/loop0010/gate.py` passes (lake build, imports,
      sorry and axiom count at zero, MOSP pytest about 3 min,
      pathwidth_solver pytest about 6 min, `make -C paper1/latex check`).
      Run `make -C paper1/latex` before the gate if the PDF is stale.
- [ ] A section appended to `reports/excess_phase_diagram.md` (create it in
      item 01), and an entry in PROGRESS.md: what was done, the numbers,
      the kill verdict, what is left.
- [ ] The item is marked `- [x]`, or `- [!]` with the reason in PROGRESS.md.

## Completion Conditions
An item is DONE when solved, or blocked with the obstacle documented. A
killed hypothesis is a solved item. If an item finds that a certified value
is wrong, a theorem is false, or a published claim of ours drifts, stop the
item there, record it at the top of PROGRESS.md and of the report, and end
the session: that is the most important possible finding.

## Context
- **Data**: `learning/data/instances.csv` (corpus features, `n_ones`),
  `learning/data/ensemble/results*.csv` (regenerate any instance from its
  seed with `learning.ensemble.generate`), `benchmarks/results/compute_ledger.csv`,
  `solutions/` (read only), `reports/scratch/clique_cover_moment/`.
- **Code to reuse**: `learning/ensemble.py`, `learning/ridge_theory.py`
  (`load_frames`, the peak interpolation), `learning/cover_excess.py`
  (`peel`, `bipartite_components`), `learning/degeneracy.py`
  (`lattice_counts`), `learning/cost_model.py`, `learning/treewidth.py`,
  `learning/bound_harness.py`, `satisfiability/heuristics.py`
  (`two_key_rule`, `restricted_dfs`), `satisfiability/customer_search.py`
  (`decide`, `.nodes`), `mosp/preprocess.py`, `benchmarks/generator.py`,
  `reports/scratch/clique_cover_moment/{bound_lib,asymptotic_cs,finite_bound_cs,gen_candidates}.py`,
  `reports/scratch/tree_bound/compare_bound.py`.
- **Lean**: `lean/MOSPFormalization/` as listed above; `learning/sandwich.py`
  pins Lean definitions to the corpus implementations; `paper1/axiom_check.lean`.
- **Paper**: `paper1/latex/` (`main.tex`, `sec9e_appendix_random.tex`,
  `sec9a_appendix_lean.tex`, `Makefile` with `check`, `axioms`, `tables`,
  `refs`), `tests/test_paper1_latex.py`.
- **Testing**: `python3 Ralph_Loops/loop0010/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md`, any existing Lean proof, or anything under
  `solutions/`. Do NOT push. Commit nothing yourself; the driver commits
  with `git add -A`, so leave no stray files outside the item's paths.
- Do NOT run `benchmarks.csearch`, `benchmarks.recertify`,
  `benchmarks.overnight` or `benchmarks.solve_parallel`.
- Figures: read the dataviz skill before drawing one; print vectors for
  the paper, PNG for the report, no title inside the figure.
- Print mode: **ending your turn ends the session.** Never end on a
  background wait.
