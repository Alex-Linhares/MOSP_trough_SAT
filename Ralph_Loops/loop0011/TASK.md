# TASK: Counting events, not witnesses — the separator first moment on random graphs and random MOSP instances

## Philosophy
- **Read first, in full**:
  - `reports/separator_moment_plan.md`, the plan this loop executes: what
    the loop stands on, the planner's estimates (never to be quoted as
    results), the six places the record corrects the brief, the items.
  - `CLAUDE.md`: the owner's rules on compute (only unsolved problems;
    never the Python pathwidth solver; never `solutions_dir=None`), what is
    proved and what is measured, "Lessons that cost sessions", and the
    paragraph "The excess phase diagram".
  - `reports/excess_phase_diagram.md` §0 (the two-page summary), **§8 in
    full** (the structured count: nested pairs lower `β*`; the clumping
    `E[X²]/E[X]² = e^{0.23 n}` at `β*` for `d = 6`, `μ = 1`; the slack is the
    union bound over clustered pairs), §14 (open list, item 1), §2.5 (the
    certified slopes `b` per `(d, μ)`).
  - `reports/random_graph_first_moment.md` (Theorems A, A′, A″, B;
    `β*(c)`; the finite form against the pilot, §5) and
    `reports/scratch/clique_cover_moment/README.md` + `REPORT_generator.md`
    (the clique-cover version; `β*(d, μ)`; the threshold at excess 1; the
    fitted generator).
  - `reports/random_graph_pathwidth_survey.md` §1 and §7(d) (what is
    published; the pilot's fitted slopes).
  - The Lean headers: `lean/MOSPFormalization/EmptyPair.lean`
    (`exists_empty_pair_of_layout`, `exists_closedNbhd_card_le`,
    `exists_empty_pair`), `FirstMoment.lean` (`IsEmptyPair`, `gnpWeight`,
    `weightedSum_graphsOfPathwidthLe_le`), `FirstMomentAsymptotics.lean`,
    `CliqueCoverMoment.lean` (`coverGraph`, `avoidCount`,
    `prob_coversOfMospValueLe_le`), `ForestCover.lean` (the layer lemma;
    `isEmptyPair_coverGraph_of_subset`).
- **The object.** A layout of vertex separation `≤ k` gives, at the prefix
  of size `t = ⌈(n − k)/2⌉`, a separator `S` (the active suffix, `≤ k`
  vertices) with the prefix `A` and the inactive suffix `R` on either side
  and no `A–R` edge. Padding `S` to exactly `k` vertices from `R`:
  `|A| = t`, `|R| = N − t`, `|S| = k`, `N = n − k`, `A ∪ R ∪ S = V`. The pair
  count on record sums over `(A, R)`; this loop sums over `S` with the inner
  probability `P(G − S` has a balanced empty bipartition`)` computed from
  the component structure, and over two further representatives: the
  *closed* pair (`S = N(A) ∩ N(R)`) and the weighted count
  `Y = Σ_P 1[P empty] / Z(P)` for any `Z ≤ X`. Say exactly which event is
  counted in every statement; the three are not the same event, and the
  relaxation "no component larger than `t`" is weaker than the bipartition
  event (plan §0, correction 3).
- **Nothing is solved twice.** The pilot graphs
  (`reports/scratch/gnp_pilot/results.csv`: 6,542 proved with layouts,
  `n = 20–120`), the certified ensembles (`learning/data/ensemble/results*.csv`,
  regenerate from seed with `learning.ensemble.generate(Cell.parse(...), index)`)
  and the corpus (`solutions/`, read only) carry exact values already. New
  exact solves are allowed only where an item says so: tiny graphs that are
  not MOSP instances (`n ≤ 24`), by the subset DP
  (`learning.first_moment.vertex_separation_brute`, `n ≤ 16`) or the C
  program `pathwidth_solver/cli/pathwidth` (graph6 on stdin, `-l` for the
  layout), never the Python pathwidth solver; every layout persisted in the
  item's CSV under `reports/scratch/separator_moment/`; never
  `solutions_dir=None`; never `solutions/`.
- **State before you prove, and check before you state.** Every statement
  that will be called a lemma or theorem — on paper or in Lean — is first
  checked by brute force on small instances (every graph to 9 vertices by
  `nauty-geng`, as `reports/scratch/empty_pair/check.py` does; every
  labelled graph to 7 for weighted counts, as
  `reports/scratch/first_moment/check.py` does), and the check's script and
  log are kept. Two earlier `sorry`s in this development hid false
  statements, not hard ones.
- **A measurement is not a theorem; a first moment is not the constant; a
  fit is not a rate.** Every number carries its size range and its
  regenerate command. Where a rate is fitted from finite `N`, say "fitted".
  Every item ends with "what this does not claim". Say "we found no prior
  statement", never "first". The planner's estimates in the plan are
  predictions to be tested, never results to be cited.
- **Nats per vertex, with the conversion beside them**: the pair exponent's
  slope at `β*` is `3.3–3.4` per unit of `β` on `G(n, c/n)` at `c = 6–10`
  (compute it for each cell you quote), so a gain of `g` nats per vertex is
  `g / 3.3` in `β`. Report both.

## Compute, and the machine
- 32 cores, shared with the owner's other projects; the load is often above
  24 from work that is not ours. Every process under `nice -n 19`; at most
  8 workers, 4 if the one-minute load in `uptime` is above 24. Check
  `uptime` before anything parallel. Find processes by PID, never by
  command-line text; never a bare `pkill -f <word>`.
- The owner's `reports/scratch/dataset_open/run_unlimited.py` (24 workers at
  nice 19) may be running or may be restarted at any time; it must not be
  disturbed, and its idle cores are the owner's, not ours.
- Budgets per item are in `iterations.md`; the loop's total is about 12
  core-hours. Long jobs run in the foreground with bounded polls; never end
  a turn on a background wait.
- Downloaded papers (item 01, arXiv) go into `literature/` as PDFs with the
  repository's naming (`YEAR-Author-Title-Venue.pdf`); nothing is executed
  from a download, and text is extracted with `pdftotext` into
  `reports/scratch/separator_moment/lit/`.

## Current Focus
Item 01 reads. Items 02–04 de-risk (the deterministic lemmas; the clumping
decomposed on instances with exact pathwidth; the planted cluster). Items
05–07 compute (the inner probability exactly; `β_sep(c)`; the MOSP version).
Item 08 proves on paper, 09 is the branch (the weighted count's lower tail),
10 is Lean, 11 the slack ledger, 12 the write-up, 13 the reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration; the
item's full text is in the prompt and in the file.

## Acceptance Criteria (per item)
- [ ] The deliverable exists where the item says, states its size range,
      gives its regenerate command, has a kill verdict (met / not met /
      none), and says what it does not claim.
- [ ] New code has tests under `tests/`; new Lean has no `sorry` and no
      `axiom` and is imported by `lean/MOSPFormalization.lean`.
- [ ] `python3 Ralph_Loops/loop0011/gate.py` passes (lake build, imports,
      sorry and axiom count at zero, MOSP pytest about 3 min,
      pathwidth_solver pytest about 6 min, `make -C paper1/latex check`).
      Run `make -C paper1/latex` before the gate if the PDF is stale.
- [ ] A section appended to `reports/separator_moment.md` (create it in
      item 01), and an entry in PROGRESS.md: what was done, the numbers,
      the kill verdict, what is left.
- [ ] The item is marked `- [x]`, or `- [!]` with the reason in PROGRESS.md.

## Completion Conditions
An item is DONE when solved, or blocked with the obstacle documented. A
killed hypothesis is a solved item. If an item finds that a certified value
is wrong, a theorem is false, a floor on record exceeds a certified optimum,
or a published claim of ours drifts, stop the item there, record it at the
top of PROGRESS.md and of the report, and end the session: that is the most
important possible finding.

## Context
- **Data**: `reports/scratch/gnp_pilot/results.csv` (pilot graphs: `n, c,
  seed, width, status, layout`); `learning/data/ensemble/results*.csv`
  (certified covers; `Cell.parse`, `generate`); `learning/data/excess*.csv`
  (regenerate with `python -m learning.excess`, 10 s);
  `reports/scratch/structured_count/` (`slack_6_1.csv`: Harper values on
  650 certified `(6, 1)` instances; `second_moment_rate.csv`,
  `second_moment_125.csv`); `benchmarks/instances/MOSP_Instances/Chu_Stuckey/`
  (the 200 files); `solutions/` (read only).
- **Code to reuse**: `learning/first_moment.py` (`rate`, `beta_star`,
  `log_bound`, `floors`, `nested_*`, `NestedStructure`, `_mobius_coefficients`,
  `second_moment_exact`, `second_moment_rate`, `empty_pair_count_brute`,
  `vertex_separation_brute`, `customer_masks`, `lq`, `lchoose`),
  `satisfiability/expansion_bound.py` (`_f_exact`: the pruned enumeration
  of `t`-sets with small closed neighbourhood), `learning/ensemble.py`,
  `benchmarks/generator.py`, `fixed_parameter_algorithm/pathwidth.py`
  (`compute_pathwidth`, `n ≤ 18`), `reports/scratch/empty_pair/check.py`
  (geng enumeration), `reports/scratch/first_moment/check.py` (labelled
  graphs, weighted counts), `reports/scratch/structured_count/run.py`,
  `learning/sandwich.py` (pins Lean definitions to implementations; sorry
  inventory), `learning/bound_harness.py`.
- **Lean**: `lean/MOSPFormalization/` as listed above; `paper1/axiom_check.lean`;
  `lake build` in `lean/`.
- **Paper**: `paper1/latex/` (`main.tex`, `sec9e_appendix_random.tex` — the
  paragraph "Why the first moment is loose" and the closing sentence of the
  section are what item 12 edits; `sec9a_appendix_lean.tex`; `Makefile`
  with `check`, `axioms`, `tables`, `refs`; `check_refs.py`),
  `tests/test_paper1_latex.py`.
- **Testing**: `python3 Ralph_Loops/loop0011/gate.py`.

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
