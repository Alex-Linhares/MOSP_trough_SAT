# loop0012 progress

Plan: `reports/edwards_mcdermid_plan.md` — the Edwards–McDermid (2015)
degree-sequence upper bound on pathwidth, verified on every graph with a
proved pathwidth and formalised in Lean conditional on the cubic base case
(Fomin & Høie 2006) and the reduction lemma (Kneis et al. 2009), both as
named `Prop`s; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0012/gate.py`.

Current: 3/11 SOLVED

## Setup — 2026-11-01

- **Baseline.** To be recorded by the first session before it starts its
  item: the Lean `sorry` and `axiom` count in code (expected 0 after
  loop0011; the gate's baseline is 0), the test counts of the two pytest
  suites, the paper's page count (`paper1/latex/main.pdf`). loop0011 was
  still running when this loop was written; its last commits add
  `lean/MOSPFormalization/SeparatorMoment.lean` and `reports/separator_moment.md`.
- **Data on record** (nothing to re-solve): the pilot's 6,542 proved
  `G(n, c/n)` graphs (`reports/scratch/gnp_pilot/results.csv`,
  `status ∈ {refutation, bound, minor}`, `n = 20–120`; 173 `upper` rows are
  unproved); 16,636 certified classes in
  `paper1/data/dataset/pathwidth_dataset.jsonl.gz` (`n` to 2,916; Rome
  11,199, MOSP 3,705, freetdi 1,187, PACE 296, VSPLIB 122, TreewidthLIB 33,
  Martí 84, VLSI 10; 42 of them cubic, `N = 4–120`); 50,716 certified
  random covers in the ensemble frames; the corpus's 6,376 instances
  (inside the dataset as 3,705 distinct graphs).
- **Ten corrections to the brief, carried into the plan** (§0.4): the
  paper gives no constants for its base case (`τ(n) = o(n)` and an
  unspecified `O(log n)`; Fomin–Høie's explicit `n_ε` makes the budget
  vacuous below `n ≈ 10⁴`), so the hypothesis is parameterised by a budget
  and the record *measures* what it needs; the "simple kind" has pathwidth
  `Θ(log n)`, not a constant; Fomin–Høie's transfer is one bisection plus
  their Lemma 4 and a boundary sweep, not a recursion (a recursion summed
  down the levels gives `n/3`); no finite graph can violate Corollary 5.2
  as stated, so the kill criterion lives on the deterministic lemmas;
  Kneis et al. 2009 is not held and not obtainable, so the reduction
  lemma is the second named hypothesis and Lemma 3.1's confluence appeal
  is replaced by a local commutation lemma; Corollary 5.2's displayed `=`
  is `≤`; Theorem 5.3 rests on an Edwards–Farr averaging lemma not proved
  in the paper; Mathlib has no series-parallel graphs or minors; the
  repository already has the deletion, concatenation and
  max-over-components lemmas; the data are richer than the brief lists.
- **Planner's ten-second checks** (plan §0, never quoted as results): the
  `g` table to `d = 9`, properties 3–6 and the closed form to `n = 15`,
  the Poisson values `0.1826, 0.4575, 0.6558`, Fomin–Høie's `n_ε`
  (55, 389, 1,674, 18,605 at `ε = 0.5, 0.3, 0.2, 0.1`), the second-kind
  floor `f⁻ ≥ 5/6`.
- **Driver.** `loop.py` and `gate.py` are loop0011's with the loop number
  changed (the item regex passes whole items — 2-space continuation lines,
  no blank line inside an item); `knobs.json` unchanged (cap 4 h, fix cap
  45 min, 3 fix attempts, 16 iterations); `allowed_sorries.txt` empty (the
  cited results are named `Prop`s, never `sorry`).
- **Before launch.** Wait for loop0011 to finish (`status.json` phase
  `idle`, or the completion marker in its PROGRESS.md) and for its last commit.
  The driver refuses to start while `git status` shows changes under
  `learning reports tests benchmarks satisfiability mosp customer_inter`;
  commit or stash first. Check that the owner's `run_unlimited.py` is not
  running (by PID), or leave it its cores. Launch as
  `Ralph_Loops/Ralph_Loop_Guide.md` "As practised here" says, with the API
  key from `~/.config/anthropic/api_key`; never a second driver on this
  folder.

---

## Iteration 1 — 2026-11-02 00:26–00:50 UTC — item 01: fetch the manuscript; Corollary 5.2 and Theorem 5.3 on every graph with a proved pathwidth

### Completed
- **Baseline** (recorded before the item): Lean `sorry` in code 0, `axiom` 0
  (gate); paper `paper1/latex/main.pdf` 74 pages; test counts from the gate
  run are in the gate line below.
- **Fetched** the accepted manuscript into
  `reports/scratch/edwards_mcdermid/em2015.pdf` (31 pages: two portal cover
  sheets plus the 29-page manuscript of April 29, 2014), text `em2015.txt` by
  `pdftotext -layout`, `SHA256` beside them (`f94e8c08…8665`, 2026-11-02
  00:26 UTC). Sections 1, 3, 5 and the Appendix read against plan §0.2:
  **every quotation agrees word for word**; Corollary 5.2 and Theorem 5.3 are
  on p. 20 (the section starts on p. 19). No discrepancy of substance.
- **Code**: `learning/edwards_mcdermid.py` (`g` in `Fraction`, `g_real`,
  `g_prime`, the closed form, `reduce` on bit masks with a low-degree stack
  so it is linear in the steps, `main_term`, `histogram_term`,
  `average_degree_term`, `fminus` per component, `poisson_value`,
  `fomin_hoie_budget`, `evaluate`); 21 tests in
  `tests/test_edwards_mcdermid.py` (the paper's table to `d = 8` exactly,
  properties 3–6 and Lemma 8.1 to `n = 30`, the four named reductions, no
  degree rises and `main ≤ histogram` on 200 random graphs, idempotence and
  relabelling invariance of `reduce`).
- **Run**: `reports/scratch/edwards_mcdermid/01_verify/run.py` (75 s on 8
  workers at load 0.1): pilot 6,542 proved (+173 unproved carried apart),
  dataset 16,635 certified non-empty classes (+336 `solution`), ensembles
  50,701 certified rows of which 40,153 distinct within their cell by the
  stored nauty certificate; 4,681 connected cubic graphs to 16 vertices by
  the subset DP (the only new solves, allowed by the item).
- **Kill checks: none fired.** 0 of 63,330 proved graphs with
  `pw > main term + τ_FH(n)`; 0 with `main term > histogram term`; `reduce`
  never raised a degree.
- **Numbers** (`reports/edwards_mcdermid.md` §1): the main term alone bounds
  61.8% of the record, the histogram term 72.0%; max deficit **5** (the
  202-vertex VSPLIB trees at pw 5, main term 0: the paper's `O(log n)` term),
  **4.333** over graphs whose reduction is non-empty (the Coxeter graph);
  `B(n)` = 3.333, 4, 4.333, 4.333, 4.333, 4.333, 5, 5, 5 at
  `n = 10, 20, 40, 60, 100, 200, 500, 1000, 2916` against `τ_FH(n)` = 7.5 …
  498 (2.2× to 100× above, vacuous as the plan said). Cubic base case:
  smallest `c` with `pw ≤ N/6 − 1/6 + c` is **3.833** exhaustively to 16
  (Heawood) and **4.5** on the 42 certified connected cubic graphs to 120
  (Coxeter); the record-holders are the small cages. The 13 dataset cubic
  graphs at `N ≤ 16` matched the sweep by isomorphism and all 13 pathwidths
  agree (a free audit; nothing re-solved). Poisson: histogram/n within 0.012
  of `poisson_value(c)` at every cell `n = 60–120`; the reduction's gain is
  0.021–0.025 per vertex at `c = 3`, 0.009 at 4, 0.001 at 6, 0 from 8; the
  bound is 1.1–1.2× the proved `pw` at `c = 3`, 1.4–1.5× at `c = 6–10`.
  Theorem 5.3: the Edwards–Farr averaging lemma holds on all 52,747 graphs
  where it applies (0 with `main > g(d̄)n`) and fails on 1,431 of the 5,487
  disconnected graphs with `d̄ < 5` — its hypothesis is needed.
- Figure `01_verify/poisson_n120.png` (dataviz skill read first); the report
  created with its header (statement, the two hypotheses, notation) and §1.
- **Gate: PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,770
  passed, 2 skipped, 1 xfailed in 274 s, the 21 new tests included;
  pathwidth_solver pytest 123 passed in 386 s; `make -C paper1/latex check`
  ok, the paper untouched).

### Blockers
None. Observations for later items: the dataset's certified classes are
16,635 non-empty (the plan's 16,636 counts the empty graph); the ensembles'
certified rows are 50,701 (not 50,716); `Cell.parse` takes `f:10:10:2`, not
the frame's `cell` string — build `Cell(generator, n, m, param)` from the
columns.

### Next
Item 02: the exact statement to formalise, every intermediate lemma checked
on every graph to 9 vertices (`reduce` and `fminus` from
`learning.edwards_mcdermid` are ready for it; the (H3) gap `pw(H) − pw(r(H))`
is measured only in shape here: `pw ≤ log₃ n + 0.904` on the 6,785 graphs
that reduce to empty).

---

## Iteration 2 — 2026-11-02 00:58–01:24 UTC — item 02: the exact statements, every intermediate lemma checked on every graph to 9 vertices

### Completed
- **Script** `reports/scratch/edwards_mcdermid/02_lemmas/check.py` (every graph
  on 1–9 vertices from `nauty-geng`, 288,266 graphs, pathwidth by the subset
  DP; `check.log`, `violations.txt`, `summary.json`); 335 s on 8 workers.
  Nothing sampled: the 9950X computes `pw(G[S])` for every `S` of a 9-vertex
  graph in 20 ms, so the cut lemma was checked on **every partition of every
  graph** (71,967,757), R3 on every (graph, step, `w`) (3,115,987), the
  reduct's uniqueness on 200 random orders per graph (39,657,000), S1′ on
  every maximum-degree vertex to 9.
- **Kill checks: none fired.** 0 violations of W1–W5 (to `n = 40`, exact),
  C1, C2, P1, P2, R1, R2, R3, R5, R6, S0, S1, SJ, T1, B1.
- **Two measurements, both findings** (as the item provided for): **S1′ is
  false** — 663 of 157,324 (graph, max-degree `w`, reduct) triples fail, on
  350 graphs from 7 vertices, every one with all neighbours of `w` at the
  maximum degree in a non-regular graph, by exactly `g'(Δ−1) − g'(Δ)`;
  the paper's two-key rule (max degree, then smallest lowest-neighbour
  degree) never fails (137,573 triples), so **item 07 keeps the tie-break**
  (pinned by `test_paper_choice_tie_break_is_needed`, graph `F]~vo`).
  **The reduct is unique** on every graph to 9 (and `r(G − X)` equals
  Algorithm X's final graph on all 89,972 T1 instances); the design does not
  use it.
- **Six corrections to the design and the item's wording** (report §2.1):
  the step relation is defined at degrees 1–2 only (operation 1 is the
  identity on `SimpleGraph V`, so R1 would be false with it); the cut lemma
  has the stronger **separator form C1s** `pw ≤ max(pw(G[V₁]), pw(G[V₂])) + min(|∂₁|, |∂₂|)`,
  which rests on `pathwidth_le_pathwidth_induce_add_card_compl`,
  `pathwidth_induce_union_le_max` and `pathwidth_le_of_injective` and implies
  the item's three-term C1, and the iterated C2 then has factor 1 (C2s);
  B1's floor `5/6` is for *non-cubic* components (`K₄` is cubic and of the
  second kind with `f⁻ = 1/2`), and A1 needs only `f⁻(C) ≥ 0`; P2's regular
  case is an equality and needs `Δ ≥ 4` (property 6 fails at 3); S1 is
  proved in the global-minimum form `1 + F(G*) ≤ F(G)`, which implies the
  per-component form; T1 needs `G ≠ ⊥`, and **no confluence fact is needed
  anywhere** ("not basic" is `∀ v, ¬ SPReduces (G − v) ⊥`).
- **Budgets at `n ≤ 9`** (§2.5): `pw − f⁻` over reduced graphs peaks at 5/2
  (`K₄`) and 17/6 (the two cubic graphs on 8 vertices of pathwidth 4);
  `pw − main term` at 3 from `n = 6`. **(H3)'s shape**: `pw(G) − pw(r(G))`
  is 0 / 1 / 2 / 3 on 273,776 / 3,210 / 9,899 / 1,381 graphs — maximum 3,
  not the expected 2, first at 6 vertices (a triangle with each edge
  subdivided, series-parallel, pathwidth 3); never negative; one step never
  costs more than one (R6).
- **Lean-ready list** for items 03–09 in report §2.6 (names, statements,
  hypotheses, file, the existing lemma each rests on), copied below.
- **Code**: the helpers in `learning/edwards_mcdermid.py` (`support`,
  `isolate`, `isolate_set`, `restrict`, `step_vertices`, `sp_step`,
  `reduce_random`, `global_min_degree`, `F_global`, `is_basic_component`,
  `is_basic`, `paper_choice`, `algorithm_x`, `pathwidth_induced`); 9 new
  tests in `tests/test_edwards_mcdermid.py` (30 in all).
- **Gate: PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,779
  passed, 2 skipped, 1 xfailed in 304 s, the 9 new tests included;
  pathwidth_solver pytest 123 passed in 392 s; `make -C paper1/latex check`
  ok, 74 pages, the paper untouched). The refactored script's rerun gave
  per-`n` counters identical to the first run (284 s).

### The Lean-ready list (report §2.6, abridged; the full tables are there)
- **03 `Weights.lean`**: `g`, `g'`; `g_recurrence` (W1), `g_table`,
  `g_monotone` (W2, via `g(n−1) ≤ g(n) ≤ (1 + g(n−1))/2`), `g'_recurrence`
  (`n g'(n) = (n−3) g'(n−1) + g'(n−2)`, `n ≥ 5`), `g'_antitone_of_three_le`
  (W3, via `g'(n−1) ≥ g'(n) ≥ g'(n−1)/3`), `one_sub_g_eq` (W4),
  `g_nonneg`, `g_lt_one`, `g'_nonneg`, `g'_le_sixth`, `g'_le_g` (W5);
  `g_closed_form` optional.
- **04 `CutLemma.lean`**: `boundary G S`; `pathwidth_le_max_add_min_boundary`
  (C1s); `pathwidth_le_cut` (C1, corollary); `BisectionTree G S bs k` (a
  `Prop` by recursion on the budget list) with `pathwidth_le_of_bisectionTree`
  (C2s, `≤ k + bs.sum`) and the factor-2 corollary (C2); the Fomin–Høie note.
- **05 `Potential.lean`**: `f`, `minDeg`, `fminus`, `F`; `degree_isolate`,
  `f_isolate` (P1), `f_isolate_le_sub_one` (P2), `f_isolate_regular` (P2r),
  `fminus_le_F`, `fminus_eq_F_of_connected`, `fminus_eq_sum_components`,
  `fminus_component_nonneg`, `fminus_cubic`; `fminus_ge_five_sixths_of_not_cubic` optional.
- **06 `SPReduction.lean`**: `SPStep G v H` (degrees 1 and 2 only),
  `SPReduces`, `IsSPReduced`, `IsBasic` (second kind = `∃ v, SPReduces ((G.restrict C).isolate v) ⊥`);
  `SPStep.edgeFinset_card_lt` (R1), `exists_reduced_reduct`,
  `SPStep.degree_le` / `SPReduces.degree_le` / `SPReduces.f_le` /
  `SPReduces.f_sub_ge_of_isolated` (R2), `SPStep.isolate_comm` (R3),
  `SPReduces.isolate_comm` and `SPReduces.isolateSet_comm` (R4, `X` disjoint
  from the acted vertices), `SPStep.sup_of_disjoint` (R5, the lift to a
  disjoint union); `pathwidth_le_SPStep_add_one` (R6) optional.
- **07 `Step.lean`**: `minNbrDeg`; `j_identity` (SJ), `j4_ge` (S0),
  `step_inequality` (S1: `1 + f G* − g' (δ G*) ≤ f G − g' (δ G)` for the
  two-key `w`), `step_inequality_fminus`, `nonbasic_reduct_ne_bot` (from the
  definition of `IsBasic`, no confluence). **Not S1′.**
- **08 `ReductionTheorem.lean`**: `exists_reduction_set` (T1) by strong
  induction on `|supp G|`: basic → `X = ∅`; disconnected → one component and
  the rest, R5 to lift, additivity; connected non-basic → the two-key `w`,
  `exists_reduced_reduct`, S1, the induction hypothesis on `G*`, R4,
  transitivity, `X = insert w X*`.
- **09 `Pathwidth.lean`**: `CubicPathwidthBound τ`, `ReductionPathwidthBound ρ`
  (named `Prop`s); `pathwidth_le_pathwidth_isolateSet_add_card`,
  `pathwidth_eq_pathwidth_induce_supp`, `pathwidth_le_max_components`,
  `pathwidth_basic_le` (`≤ fminus B + τ n + ρ n + 1`),
  `pathwidth_le_potential_of_hypotheses` (A1, `+ τ n + 2ρ n + 1`),
  `pathwidth_le_degreeSum_of_hypotheses` (A2, `+ τ n + 3ρ n + 1`);
  `#print axioms` rows; `learning/sandwich.py --stage degree_bound`.

### Blockers
None. Observations: the item's "2,000 random partitions at 8–9" and "S1′ to
8 if slow" were not needed (exhaustive to 9 in 335 s); `summary.json` keeps
the per-`n` counters and maxima for later items.

### Next
Item 03: `DegreeBound/Weights.lean` — `g`, `g'` and W1–W5 as listed, with
the two induction invariants named above (both checked to `n = 40` in exact
rationals here), the sandwich pin in `learning/sandwich.py`.

---

## Iteration 3 — 2026-11-02 01:35–02:13 UTC — item 03: Lean (i), the weights `g`, `g'` and their lemmas

### Completed
- **`lean/MOSPFormalization/DegreeBound/Weights.lean`**: `g : ℕ → ℚ` (four
  cases and `g (n + 4) = ((n + 2) g (n + 3) + g (n + 2) + 1) / (n + 4)`),
  `g' n = g n − g (n − 1)` (the plan's literal form, natural subtraction),
  `altFactorial`; **44 theorems, no `sorry`, no `axiom`**, in `ℚ` throughout:
  `g_recurrence` (W1), `g_four … g_nine` and `g_table` (to `d = 9`), `g_aux`
  (the coupled invariant of Lemma 8.3 with `g n < 1`), `g_nonneg`, `g_lt_one`,
  `g_monotone` (W2), `g'_succ`, `g'_zero … g'_eight`, `g'_eq_zero_of_le_two`,
  `g'_nonneg`, `g'_le_g`, `g'_recurrence` (`n ≥ 5`), `g'_aux` (the sandwich of
  Lemma 8.4), `g'_succ_le`, `g'_antitone_of_three_le` (W3), `g'_le_sixth`,
  `one_sub_g_eq` (W4), and the two optional ones: `g_closed_form` (Lemma 8.1,
  with `altFactorial_zero/succ`) and `g_div_lt_g_div` (Lemma 8.5, strict from
  5; false at 4, as the paper says) with `half_le_g`. Imported by
  `lean/MOSPFormalization.lean`; builds in 8.1 s; `lake build` passes
  (`reports/scratch/edwards_mcdermid/03_weights/lake_build.log`).
- **Checked before stated**: `03_weights/check.py` — every statement in the
  exact form Lean proves it, in exact rationals to `n = 200`, zero failures
  (`check.log`); item 02 had W1–W5 to 40.
- **Axiom check**: 44 new `#print axioms` lines in `paper1/axiom_check.lean`;
  every one `[propext, Classical.choice, Quot.sound]` (`axiom_check.log`;
  `make -C paper1/latex axioms`: 351 theorems checked, 0 failures).
- **Sandwich stage** `python -m learning.sandwich --stage degree_bound`:
  `g_lean`, `g_prime_lean`, `alt_factorial_lean` transcribed from Lean,
  `degree_bound_check` (16 rows, **2,793 checks, 0 violations**, `sandwich.log`),
  `DEGREE_BOUND_PROVED` (44 names) folded into `ALL_PROVED` so `--stage lean`
  audits them too.
- **Tests**: 3 new in `tests/test_edwards_mcdermid.py` (33 in all): the
  transcription to 200, the stage, the names declared / imported / audited.
- **Report**: `reports/edwards_mcdermid.md` §3 (definitions, the 44 statements
  with their proofs, the axiom lines, what items 05–08 get, kill verdict none,
  regenerate commands, what it does not claim).
- **Gate**: **PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,782
  passed, 2 skipped, 1 xfailed in 896 s and pathwidth_solver pytest 123 passed
  in 796 s — both 2–3× their usual time under a machine load of 50–58 from the
  owner's other work; `make -C paper1/latex check` ok, 74 pages, the paper
  untouched). Log: `03_weights/gate.log`.

### Blockers
None. Notes for later items: `g_zero … g_three` are `rfl` but their axiom lines
still show the standard three (the compiled recursion's unfolding), so no
theorem of the file is axiom-free — nothing to do, recorded so nobody chases it;
in current Mathlib `le_or_lt` is `le_or_gt` (use `Nat.lt_or_ge`); `linear_combination`
coefficients for the `(m + 4)`-multiplied recurrence are `±1`, not `±1/2`, when
the target was already divided by 2; `field_simp; ring` closes Lemma 8.1's step
only after `(m + 3)!` is also rewritten to `(m + 3)(m + 2)!`.

### Next
Item 04: `DegreeBound/CutLemma.lean` — `boundary G S`,
`pathwidth_le_max_add_min_boundary` (C1s) from
`pathwidth_le_pathwidth_induce_add_card_compl`, `pathwidth_induce_union_le_max`
and `pathwidth_le_of_injective`; `pathwidth_le_cut` (C1); `BisectionTree` with
`pathwidth_le_of_bisectionTree` (C2s) and the factor-2 corollary (C2); checked
on every partition of every graph to 9 in item 02 (71,967,757).
