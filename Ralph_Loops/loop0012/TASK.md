# TASK: The Edwards–McDermid degree-sequence bound on pathwidth — verified on the record, formalised in Lean conditional on the cubic base case

## Philosophy
- **Read first, in full**:
  - `reports/edwards_mcdermid_plan.md`, the plan this loop executes. Its §0.2
    quotes every statement of Edwards & McDermid (2015) and of Fomin & Høie
    (2006) the loop needs, verbatim, so that no session depends on the
    manuscript's temporary copy; §0.3 names the two hypotheses the
    formalisation is conditional on; §0.4 lists ten places where the paper
    or the repository corrects the brief; §0.5 fixes the Lean design
    (graphs on one vertex type, removed vertices isolated, no `r(·)` as a
    function, the per-component potential, `ℚ` arithmetic, file names).
    Do not re-decide what §0.5 decides; if an item finds §0.5 wrong, say so
    in PROGRESS.md and the report and do the smallest sound thing.
  - `CLAUDE.md`: the owner's rules on compute (only unsolved problems;
    never the Python pathwidth solver; never `solutions_dir=None`), what is
    proved and what is measured, "Lessons that cost sessions".
  - The Lean tools: `lean/MOSPFormalization/TreeBound.lean` (its header
    lists `pathwidth_le_pathwidth_erase_add_one`,
    `pathwidth_le_pathwidth_induce_add_card_compl`,
    `pathwidth_induce_union_le_max`, `pathwidth_induce_le_of_forall_connected`,
    `PathDecomposition.extend`, `cat`, `glue`, `reachSet`,
    `tree_pathwidth_le_log`), `Minor.lean` (`isolate`, `pathwidth_mono`,
    `pathwidth_eq_of_iso`), `Pathwidth.lean`, `PathDecomposition.lean`,
    `EmptyPair.lean`, `ForestCover.lean`; the named-Prop pattern in
    `lean/MOSPFormalization/Complex/EdgeSearch.lean` (`EdgeSearchMonotonicity`,
    a `def … : Prop`, never asserted, with the theorems that need it taking
    it as a hypothesis `(h : EdgeSearchMonotonicity G)`); `paper1/axiom_check.lean`.
  - The source, once item 01 has fetched it:
    `reports/scratch/edwards_mcdermid/em2015.pdf` and `em2015.txt`
    (Sections 1, 3, 5 and the Appendix); the held
    `literature/2006-Fomin-Hoie-Pathwidth-Cubic-Graphs-Exact-Algorithms-IPL.pdf`.
- **The object.** `g : ℕ → ℚ` with `g 0 = g 1 = g 2 = 0`, `g 3 = 1/6`,
  `n g n = (n − 2) g (n − 1) + g (n − 2) + 1` for `n ≥ 4`; `g' n = g n − g (n − 1)`
  (so `g' d = 0` for `d ≤ 2`); `f G = Σ_v g (G.degree v)`;
  `fminus G = f G − Σ_{components C} g' (minDeg C)`. The series-parallel
  operations act on `SimpleGraph V` with removed vertices isolated;
  `SPReduces` is their reflexive–transitive closure; a graph is *reduced*
  when every degree is 0 or ≥ 3, *basic* when every component of its
  support is cubic or becomes `⊥` by reduction after one vertex is removed.
  The two named hypotheses are `CubicPathwidthBound τ` (every connected
  cubic graph on `N` vertices has `pw ≤ N/6 − 1/6 + τ N`) and
  `ReductionPathwidthBound ρ` (`SPReduces G H → pw G ≤ pw H + ρ |V|`);
  the theorem is `pw G ≤ fminus G + τ n + 2 ρ n + 1` for graphs with every
  degree 0 or ≥ 3, and `pw G ≤ Σ_v g (degree_{r G} v) + τ n + 3 ρ n + 1`
  for every `G`. Say in every statement which budget it uses; the paper's
  `τ(n) + O(log n)` is this with `ρ = O(log n)`, and the paper gives no
  constants (plan §0.3).
- **Nothing is solved twice.** Every pathwidth the loop uses is on record:
  the pilot (`reports/scratch/gnp_pilot/results.csv`: 6,542 proved rows,
  `status ∈ {refutation, bound, minor}`; graphs regenerate as
  `networkx.gnp_random_graph(n, c/n, seed=seed)`, the `layout` column is a
  witness; the 173 `upper` rows are unproved and only their `lower` column
  may be used), the dataset (`paper1/data/dataset/pathwidth_dataset.jsonl.gz`,
  16,636 certified classes with `edges`, `width`, `provenance`), the
  ensembles (`learning/data/ensemble/results*.csv`, regenerate each instance
  from its seed with `learning.ensemble.generate(Cell.parse(...), index)`,
  MOSP graph by `customer_inter.customer_graph.build_customer_graph`,
  `pw = optimum − 1`). New exact solves are allowed only where an item says
  so: every graph to 9 vertices from `nauty-geng` and every cubic graph to
  16 vertices (`nauty-geng -d3 -D3`), by the subset DP
  (`learning.first_moment.vertex_separation_brute`, `n ≤ 16`, or
  `fixed_parameter_algorithm.pathwidth.compute_pathwidth`, `n ≤ 18`); never
  the Python pathwidth solver; never `solutions_dir=None`; never `solutions/`.
- **State before you prove, and check before you state.** Every statement
  that will be called a lemma or theorem — on paper or in Lean — is first
  checked by brute force on small instances (every graph to 9 vertices, as
  `reports/scratch/empty_pair/check.py` does), and the check's script and
  log are kept under `reports/scratch/edwards_mcdermid/<item>/`. Two earlier
  `sorry`s in this development hid false statements, not hard ones; this
  loop adds none, and a cited result is a named `Prop`, never a `sorry` or
  an `axiom`.
- **A measurement is not a theorem; a budget the record needs is not the
  paper's budget.** Every number carries its size range and its regenerate
  command. Where the lower-order term is measured (the smallest constant
  the record requires), say "measured on … to `n = …`", never "the
  constant". Every item ends with "what this does not claim". Say "we found
  no prior statement", never "first". This is a formalisation of a
  published theorem (Edwards & McDermid 2015, Lemma 5.1 and Corollary 5.2),
  conditional on two cited results (Fomin & Høie 2006 Theorem 5; Kneis et
  al. 2009): say so plainly, every time.
- **The planner's numbers in the plan** (the Poisson values, `g` table,
  Fomin–Høie's `n_ε`, the `5/6` floor) are ten-second checks to be replaced
  by item 01's, never quoted as results.

## Compute, and the machine
- 32 cores, shared with the owner's other projects; the load is often above
  24 from work that is not ours. Every process under `nice -n 19`; at most
  8 workers, 4 if the one-minute load in `uptime` is above 24. Check
  `uptime` before anything parallel. Find processes by PID, never by
  command-line text; never a bare `pkill -f <word>`.
- The owner's `reports/scratch/dataset_open/run_unlimited.py` (24 workers at
  nice 19) may be running or may be restarted at any time; it must not be
  disturbed, and its idle cores are the owner's, not ours.
- Budgets per item are in `iterations.md`; the loop's total is about 4
  core-hours. Long jobs run in the foreground with bounded polls; never end
  a turn on a background wait.
- Only one `lake build` at a time (the loop is sequential, so this holds by
  construction; do not start a second build in the background).
- The manuscript (item 01) goes to `reports/scratch/edwards_mcdermid/`, not
  `literature/`; nothing is executed from a download; text is extracted with
  `pdftotext`; Python that reads a download runs with `-I`.

## Current Focus
Item 01 fetches and verifies. Item 02 writes the exact statements and checks
every intermediate lemma on every graph to 9 vertices. Items 03–09 are Lean,
in order of reach: the weights (03), the independent cut lemma (04), the
potential's deletion accounting (05), the reduction system with the
commutation lemma (06), the step inequality (07), Theorem 3.2 (08), the
pathwidth assembly under the named hypotheses with the axiom check (09).
Item 10 writes; 11 is the reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration; the
item's full text is in the prompt and in the file. An item that depends on a
blocked (`- [!]`) item states the named `Prop` that stands in for the
missing result and proceeds with what is independent.

## Acceptance Criteria (per item)
- [ ] The deliverable exists where the item says, states its size range,
      gives its regenerate command, has a kill verdict (met / not met /
      none), and says what it does not claim.
- [ ] New code has tests under `tests/`; new Lean has no `sorry` and no
      `axiom`, is imported by `lean/MOSPFormalization.lean`, and every new
      theorem has a `#print axioms` line in `paper1/axiom_check.lean`.
- [ ] Every new Lean statement was checked by brute force first and the
      check's log is under `reports/scratch/edwards_mcdermid/`.
- [ ] `python3 Ralph_Loops/loop0012/gate.py` passes (lake build, imports,
      sorry and axiom count at zero, MOSP pytest about 3 min,
      pathwidth_solver pytest about 6 min, `make -C paper1/latex check`).
      Run `make -C paper1/latex` before the gate if the PDF is stale.
- [ ] A section appended to `reports/edwards_mcdermid.md` (create it in
      item 01), and an entry in PROGRESS.md: what was done, the numbers,
      the kill verdict, what is left.
- [ ] The item is marked `- [x]`, or `- [!]` with the reason in PROGRESS.md.

## Completion Conditions
An item is DONE when solved, or blocked with the obstacle documented. A
killed hypothesis is a solved item. If an item finds that a proved pathwidth
on record is wrong, that a deterministic statement of the chain is false on
a small graph, that a theorem of ours is false, or that a published claim of
ours drifts, stop the item there, record it at the top of PROGRESS.md and of
the report, and end the session: that is the most important possible finding.

## Context
- **Data**: `reports/scratch/gnp_pilot/results.csv`;
  `paper1/data/dataset/pathwidth_dataset.jsonl.gz` (fields `id, n, m, edges,
  width, provenance, layout, members`); `learning/data/ensemble/results*.csv`
  (`cell`, `index`, `seed`, `optimum`, `certified`); `solutions/` (read
  only, never needed here).
- **Code to reuse**: `learning/first_moment.py` (`vertex_separation_brute`,
  `n ≤ 16`), `fixed_parameter_algorithm/pathwidth.py` (`compute_pathwidth`,
  networkx graph, `n ≤ 18`), `reports/scratch/empty_pair/check.py` (the
  geng enumeration pattern: `parse_g6`, a worker pool, a log),
  `learning/ensemble.py` (`Cell.parse`, `generate`),
  `customer_inter/customer_graph.py` (`build_customer_graph`),
  `learning/sandwich.py` (pins Lean definitions to implementations; add a
  stage), `learning/separator_moment.py` (adjacency as bit masks; the style
  for a new `learning/edwards_mcdermid.py`).
- **Lean**: `lean/MOSPFormalization/` as listed above; new files under
  `lean/MOSPFormalization/DegreeBound/`; `paper1/axiom_check.lean`;
  `lake build` in `lean/`.
- **Paper**: `paper1/latex/` (`sec9e_appendix_random.tex` cites
  `EdwardsMcDermid2015` at two places — the sandwich paragraph and the
  bounds table — and item 10 edits the sentences around them;
  `sec9a_appendix_lean.tex` holds the `\leanentry{…}{…}\leannames{…}` rows;
  `Makefile` with `check`, `axioms`, `tables`, `refs`; `check_refs.py`),
  `tests/test_paper1_latex.py`. The survey is
  `reports/random_graph_pathwidth_survey.md` (§1.4 is the explicit-bounds
  section; §7(a) the bounds table, §7(e) the tree-bound-against-data
  section whose format item 01 copies).
- **Testing**: `python3 Ralph_Loops/loop0012/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md`, any existing Lean proof, or anything under
  `solutions/` or `literature/`. Do NOT push. Commit nothing yourself; the
  driver commits with `git add -A`, so leave no stray files outside the
  item's paths.
- Do NOT run `benchmarks.csearch`, `benchmarks.recertify`,
  `benchmarks.overnight`, `benchmarks.solve_parallel`, or
  `pathwidth_solver/cli/pathwidth` on anything already proved.
- Figures: read the dataviz skill before drawing one; print vectors for
  the paper, PNG for the report, no title inside the figure.
- Print mode: **ending your turn ends the session.** Never end on a
  background wait.
- The branch `appendix-picture` (worktree `/home/al/dev/MOSP-wt`) holds
  `reports/random_graph_pathwidth_literature_2.md`, the second literature
  pass whose §3.3 is the project's prior reading of this paper; read it
  with `git -C /home/al/dev/MOSP-wt show appendix-picture:reports/random_graph_pathwidth_literature_2.md`
  and do not edit that branch.
