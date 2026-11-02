# TASK: The duality gap of each lower-bound obstruction family, found by search, across the certified corpus

## Philosophy
- **Read first, in full**:
  - `reports/obstruction_search_plan.md`, the plan this loop executes. Its
    §0.2 is the correction everything rests on: the empty-pair and Harper
    bounds are *universal* statements (`n − 2s* − 2 ≤ pw` with `s*` the
    maximum over **all** sets; `pw ≥ min_{|A|=t} |N[A]| − t` for every `t`),
    so a set found by search certifies only a **ceiling** on what the
    expansion family can ever prove, and the valid **floor** needs the inner
    minimum proved (branch and bound to cap 12, or SAT with a DRAT proof);
    cliques, contraction minors and separator branches are genuine
    maximisations whose search gives a **floor** with a certificate. §0.3
    lists what is on record (nothing is solved twice), §0.4 nine
    corrections to the brief, §0.5 the design decisions (modules, the
    C-program call on minors with its own minor step disabled, the SAT
    encoding, the certificate formats, the checker that shares no code, the
    frozen targets, the units), §0.9 the kill criteria per family. Do not
    re-decide what §0.5 decides; if an item finds §0.5 wrong, say so in
    PROGRESS.md and the report and do the smallest sound thing.
  - `CLAUDE.md`: the owner's rules on compute (only unsolved problems — here
    every target is solved, so every run is a *scoring* run on minors,
    branches and subset searches, never a refutation of a certified value
    or of an open class's recorded width; never the Python pathwidth
    solver; never `solutions_dir=None`; nothing written under `solutions/`),
    the bounds section (what `_lower_bound` computes; the expansion bound a
    net loss *inside the search*, which is about the solver's clock and not
    about the bound's strength; the bound-defeating family of trees of
    cliques; `optimum > tw_min_fill + 1` on 131 of the 338), the minor
    certificates (`reports/minor_bound_verification.md`; `2-3_0` has a
    rule-free one, `2-2_0` has none at any size tried), and "Lessons that
    cost sessions".
  - The code the loop reuses: `satisfiability/expansion_bound.py` (Harper by
    exact branch and bound under a cap; its docstring on why a heuristic
    inner minimum is a *wrong answer*, not a slow bound),
    `satisfiability/relaxation.py` (`minor_sequence`, `minor_groups`,
    `MinorConfig`), `satisfiability/mosp_solver.py::_lower_bound`,
    `pathwidth_solver/cli/README.md` and `pathwidth_solver/pathwidth/minor.py`'s
    docstring (the contraction rules and `replay`; read, never run the
    Python solver), `learning/bound_harness.py` (every floor goes through
    it; `family_separators`, `linked_third`, `--extra`), `learning/proofs.py`
    (CaDiCaL with proof, `drat-trim`), `reports/scratch/minor_certificates/`
    (`mc_graph.py`'s independent replay, `vsmemo.c`, `checkF.c`;
    `vsanneal.c` anneals layouts, not contractions), `learning/first_moment.py::vertex_separation_brute`,
    `learning/extremal.py::local_search`.
  - The Lean tools: `lean/MOSPFormalization/EmptyPair.lean`
    (`exists_closedNbhd_card_le`, `emptyPairIndex`,
    `card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth`), `Minor.lean`
    (`IsContractionSeq`, `minorOf`, `pathwidth_minorOf_le`,
    `pathwidth_gt_of_minorOf`, `lt_mospValue_of_minorOf`), `Sandwich.lean`
    (`branch_lemma`, `branch_lemma_separator`, `minDegreeIn_le_degeneracy`,
    `degeneracy_le_pathwidth`, `treewidth_le_pathwidth`), `MOSPGraph.lean`
    (`card_le_pathwidth_add_one_of_isClique`, `mospValue_eq_pathwidth_add_one`),
    `PendantCliques.lean`; `Search/BetterMove.lean` for the `decide +kernel`
    pattern; `paper1/axiom_check.lean`; `learning/sandwich.py`.
- **The object.** For a graph `G` on `n` vertices (the MOSP graph of an
  instance: customers as vertices, a clique per pattern; or a dataset
  class's edge list), `f(t) = min_{|C| = t} |N[C]|`, `s* = max_t min(t − 1, n − f(t))`;
  family **E**'s floor is `max_t (f(t) − t) + 1` over proved levels, its
  ceiling `max_t (f̂(t) − t) + 1` over incumbents; family **M**'s floor is the
  proved pathwidth (+1) of a contraction minor; family **B**'s the
  third-largest certified branch width + 1 at a separator. Every value in
  optimum units (`pathwidth + 1`); "gap" is `optimum − value`; a value that
  is not a valid bound is called a ceiling or an estimate in every table.
- **Nothing is solved twice.** Every optimum is on record (`solutions/`,
  `learning/data/instances.csv`, the dataset). The C program runs on minors
  and on branches only, each under a cap, with `-m min_vertices=1000000`
  so the certificate is ours; never on a whole certified graph; on the 24
  open classes never on a minor above 90% of the vertices. New exact
  solves are allowed only where an item says so: subset enumeration at
  `n ≤ 22`, `vertex_separation_brute` at `n ≤ 16` for validation, the
  C program on minors and branches, SAT decisions on `(t, b)`.
- **Every certificate is checked by code that shares nothing with the
  search**: `paper1/obstruction_check.py`, with its own readers, its own
  contraction replay, its own CNF generator, its own BFS. A claim in the
  report cites the checker's verdict, the certificate's path and the Lean
  theorem the certificate rests on. A certificate the checker rejects is a
  finding, not a nuisance.
- **State before you prove, and check before you state.** Every Lean
  statement is first checked by brute force on every graph to 8 vertices
  and the check's log is kept under `reports/scratch/obstruction_search/09_lean/`.
  This loop adds no `sorry` and no `axiom`.
- **A measurement is not a theorem; a search's failure is not a proof of
  absence.** Every number carries its size range, its budget and its
  regenerate command. "No certificate found under this budget", never "no
  certificate exists". Every item ends with "what this does not claim". Say
  "we found no prior report", never "first". Ellis, Sudborough & Turner
  (1994) and Harper (1966) are cited where the loop meets them.
- **The planner's numbers in the plan** (the ten-second check of §0.2, the
  figures read from the record in §0.3) are to be replaced by the items'
  own, never quoted as results.

## Compute, and the machine
- 32 cores, shared with the owner's other projects; the load is often above
  24 from work that is not ours. Every process under `nice -n 19`; at most
  8 workers, 4 if the one-minute load in `uptime` is above 24. Check
  `uptime` before anything parallel. Find processes by PID, never by
  command-line text; never a bare `pkill -f <word>`.
- The owner's `reports/scratch/dataset_open/run_unlimited.py` (24 workers at
  nice 19) may be running or may be restarted at any time; it must not be
  disturbed, and its idle cores are the owner's, not ours.
- Budgets per item are in `iterations.md`; the loop's total is about 56
  core-hours (E 9, M 28, B 4, open classes 10, the rest under 5). Every
  item with a core-hour figure has a hard stop in its driver; long jobs run
  in the foreground with bounded polls; never end a turn on a background
  wait.
- Only one `lake build` at a time (the loop is sequential; do not start a
  second build in the background).
- Nothing is downloaded. The C program is `pathwidth_solver/cli/pathwidth`
  (`make -C pathwidth_solver/cli` if the binary is stale; record its
  SHA-256 in every certificate).

## Current Focus
Item 01 measures the record and freezes the targets. Items 02–03 are family
E (the ceiling by search, the exact floor by branch and bound and by SAT
with DRAT). Items 04–05 are family M (the contraction-sequence search, its
certificate and checker, the 338 and the 200 Chu & Stuckey, the two ridge
instances). Item 06 is family B with certified branches. Item 07 is the 24
open classes, after the searches are validated on known optima (the tree
first, on paper). Item 08 draws the duality-gap map and states the kill
verdicts. Item 09 is Lean. Item 10 writes; 11 is the reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration; the
item's full text is in the prompt and in the file. An item that depends on a
blocked (`- [!]`) item uses what the record has (item 01's `floor0`, the
ladder as the M floor) and says so.

## Acceptance Criteria (per item)
- [ ] The deliverable exists where the item says, states its size range,
      gives its regenerate command, has a kill verdict (met / not met /
      none), and says what it does not claim.
- [ ] New code has tests under `tests/`; new Lean has no `sorry` and no
      `axiom`, is imported by `lean/MOSPFormalization.lean`, and every new
      theorem has a `#print axioms` line in `paper1/axiom_check.lean`.
- [ ] Every certificate the report cites has been run through
      `paper1/obstruction_check.py` and the verdict is in the item's CSV.
- [ ] Every floor the item produces has been through
      `learning/bound_harness.py`'s validity stage on its instances
      ("above optimum" must be 0) or the item says why not.
- [ ] `python3 Ralph_Loops/loop0013/gate.py` passes (lake build, imports,
      sorry and axiom count at zero, MOSP pytest about 5 min,
      pathwidth_solver pytest about 7 min, `make -C paper1/latex check`).
      Run `make -C paper1/latex` before the gate if the PDF is stale.
- [ ] A section appended to `reports/obstruction_search.md` (create it in
      item 01), and an entry in PROGRESS.md: what was done, the numbers,
      the kill verdict, what is left.
- [ ] The item is marked `- [x]`, or `- [!]` with the reason in PROGRESS.md.

## Completion Conditions
An item is DONE when solved, or blocked with the obstacle documented. A
killed family is a solved item. If an item finds a bound on record above a
certified optimum, a certificate the checker rejects that the record relies
on, a floor above an open class's recorded width, a statement of ours false
on a small graph, or a published claim of ours that drifts, stop the item
there, record it at the top of PROGRESS.md and of the report, and end the
session: that is the most important possible finding.

## Context
- **Data**: `solutions/` (read only); `learning/data/instances.csv`
  (git-ignored; `python -m learning.dataset --workers 8`);
  `learning/data/ensemble/conjecture_invariants.csv.gz`;
  `paper1/data/dataset/pathwidth_dataset.jsonl.gz` (`id, n, m, edges, width,
  provenance, layout, minor_certificate`); `reports/scratch/dataset_open/{unsolved_unlimited.csv, results.csv}`
  (the 24 open classes and their recorded floors); the minor certificates
  in `reports/scratch/minor_certificates/` and `reports/scratch/minor_bound/`;
  loop0010 item 13's Lemma P scores under `reports/scratch/excess_phase_diagram/`.
- **Targets**: frozen by item 01 in
  `reports/scratch/obstruction_search/01_ledger/targets.json` (`gap338`,
  `cs200`, `open24`, `rest500`, `small`); nothing else decides membership.
- **Code to write**: `learning/obstruction_ledger.py`, `_expansion.py`,
  `_minor.py`, `_branch.py`, `_map.py`; `paper1/obstruction_check.py` (no
  import from `learning/`, `satisfiability/`, `pathwidth_solver/`, `mosp/`);
  `tests/test_obstruction_*.py`; `lean/MOSPFormalization/ObstructionCertificate.lean`.
- **Reports**: `reports/obstruction_search.md` (one section per item, §0
  written last); scratch under `reports/scratch/obstruction_search/<item>/`;
  anything over 50 MB is not kept and its SHA-256 is logged.
- **Paper**: `paper1/latex/sec5_results.tex` ("A checkable proof of a
  refutation") or `sec9b_appendix_machinery.tex`; `\leanentry` rows in
  `sec9a_appendix_lean.tex`; `Makefile` with `check`, `axioms`;
  `tests/test_paper1_latex.py`.
- **Testing**: `python3 Ralph_Loops/loop0013/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md`, any existing Lean proof, or anything under
  `solutions/` or `literature/`. Do NOT push. Commit nothing yourself; the
  driver commits with `git add -A`, so leave no stray files outside the
  item's paths.
- Do NOT run `benchmarks.csearch`, `benchmarks.recertify`,
  `benchmarks.overnight`, `benchmarks.solve_parallel`, `paper1.dataset run`
  or `write`, or `pathwidth_solver/cli/pathwidth` on any whole graph that
  is already proved or whose width is open. Never `from pathwidth import solve`.
- Figures: read the dataviz skill before drawing one; PNG for the report,
  no title inside the figure.
- Print mode: **ending your turn ends the session.** Never end on a
  background wait.
