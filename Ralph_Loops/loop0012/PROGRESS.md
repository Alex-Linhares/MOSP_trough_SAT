# loop0012 progress

Plan: `reports/edwards_mcdermid_plan.md` — the Edwards–McDermid (2015)
degree-sequence upper bound on pathwidth, verified on every graph with a
proved pathwidth and formalised in Lean conditional on the cubic base case
(Fomin & Høie 2006) and the reduction lemma (Kneis et al. 2009), both as
named `Prop`s; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0012/gate.py`.

Current: 8/11 SOLVED

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

---

## Iteration 4 — 2026-11-02 02:26–02:45 UTC — item 04: Lean (v), the cut lemma and its iterated form

### Completed
- **`lean/MOSPFormalization/DegreeBound/CutLemma.lean`** (namespace
  `MOSPFormalization`; independent of (H1), (H3)): `boundaryTo G A B`,
  `boundary G A`; **20 theorems, no `sorry`, no `axiom`**, every one
  `[propext, Classical.choice, Quot.sound]`: `pathwidth_induce_mono`,
  `pathwidth_induce_univ`, `pathwidth_induce_le_induce_add_card_sdiff`
  (`pw G[U] ≤ pw G[T] + |U ∖ T|`, any `T, U`),
  `pathwidth_induce_union_le_max_add_boundaryTo`,
  `pathwidth_induce_union_le_max_add_min` (**C1s, relative**),
  `pathwidth_le_max_add_min_boundary` (**C1s**), `pathwidth_le_cut` (**C1**,
  the item's three-term form, `− 1` in `ℕ`), `BisectionTree` /
  `BisectionTreeMax` (`Prop` by recursion on the budget list, the item's
  "C1 applied `h` times" form), `pathwidth_induce_le_of_bisectionTree`,
  `pathwidth_le_of_bisectionTree` (**C2s**, `≤ k + Σ b`),
  `bisectionTree_of_bisectionTreeMax`, `pathwidth_le_of_bisectionTreeMax`
  (`≤ k + Σ b` with the larger boundary budgeted),
  `pathwidth_le_of_bisectionTreeMax_two_mul` (**C2**, the item's `k + 2 Σ b`;
  the factor 2 is slack), and the membership lemmas. Imported by
  `lean/MOSPFormalization.lean`; builds in 0.9 s; `lake build` passes
  (`reports/scratch/edwards_mcdermid/04_cut/lake_build.log`).
- **Checked before stated** (`04_cut/check.py`, `check.log`, `summary.json`;
  33 s on 8 workers at load < 2): every graph on 1–8 vertices (13,598; the
  item asked for 7) — monotonicity and C1r1/C1r (relative C1s) on all
  83,408,340 ordered disjoint pairs, the deletion lemma on all 826,889,252
  ordered pairs `(T, U)`, C1s and C1 on all 1,652,749 partitions — and the
  three bisection forms on 10,000 random balanced trees (depth 2 and 3) over
  2,000 random graphs at 10–12 vertices. **Kill checks: none fired**, 0
  violations. C1s tight on 13.5% of partitions, slack ≤ 4 at `n ≤ 8`.
- **Three choices beyond §2.6** (report §4.2): C1s proved in the relative
  form so the iteration recurses on `Finset V` with no nested `induce`; the
  deletion lemma's inclusion `T ⊆ U` dropped after Lean's linter found it
  unused (the check was extended to every pair and rerun before the
  statement was kept); `BisectionTreeMax` gives `k + Σ b`, the item's factor
  2 is slack.
- **Axiom check**: 20 new `#print axioms` lines in `paper1/axiom_check.lean`
  (`04_cut/axiom_check.log`; `make -C paper1/latex axioms`: 371 theorems
  checked, 0 failures). `CUT_LEMMA_PROVED` (20 names) folded into
  `learning.sandwich.ALL_PROVED`.
- **Code**: `parse_g6`, `boundary_to`, `separator_cut_bound`,
  `bisection_bound` in `learning/edwards_mcdermid.py`; 3 new tests in
  `tests/test_edwards_mcdermid.py` (36 in all: the helpers, the relative
  forms and the bisection bound on random graphs to 9, the Lean names
  declared / imported / audited, no `sorry`, no `axiom`).
- **Report**: `reports/edwards_mcdermid.md` §4 (the check's counts, the 20
  statements with their proofs, the Fomin–Høie paragraph with Lemma 4 quoted
  and the transfer lemma stated and **not** proved — a candidate for item
  11 — kill verdict, regenerate commands, what it does not claim).
- **Gate**: **PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,785
  passed, 2 skipped, 1 xfailed in 273 s, the 3 new tests included;
  pathwidth_solver pytest 123 passed in 383 s; `make -C paper1/latex check` ok,
  74 pages, the paper untouched). Log: `04_cut/gate.log`.

### Blockers
None. Notes for later items: `congrArg Subtype.val hxy` must be elaborated
without an expected type (a `have := …` then `Subtype.ext`), or Lean unifies
the expected `x.val.val = y.val.val` against the wrong level and reports
"expected `↑x = ↑y`"; the lattice lemma is `disjoint_compl_right`, not
`Finset.disjoint_compl_right`; `omega` handles `min`/`max` on `ℕ`
directly, which closes C1, C1s and the C2 step from the one-sided bounds.
For item 09, the relative C1s and `pathwidth_induce_univ` are the forms to
use (`G[S₁ ∪ S₂]`, `boundaryTo`), and `pathwidth_induce_le_induce_add_card_sdiff`
is the per-component deletion lemma it will need for `G − X`.

### Next
Item 05: `DegreeBound/Potential.lean` — `f`, `minDeg`, `fminus`, `F`;
`degree_isolate`, `f_isolate` (P1), `f_isolate_le_sub_one` (P2),
`f_isolate_regular` (P2r), `fminus_le_F`, `fminus_eq_F_of_connected`,
`fminus_eq_sum_components`, `fminus_component_nonneg`, `fminus_cubic`
(checked in item 02: P1 on 2,579,255 (graph, `w`), P2 on 163,265, P2r on
501, B1 on 290,103 components).

---

## Iteration 5 — 2026-11-02 02:57–03:24 UTC — item 05: Lean (ii), the potential and the one-deletion degree accounting

### Completed
- **`lean/MOSPFormalization/DegreeBound/Potential.lean`** (namespace
  `MOSPFormalization.DegreeBound`, imports `Weights` and `Minor`): `supp`,
  `potential` (`f`), `compFinset`, `minDeg`, `potentialMinus` (`f⁻`, the plan's
  definition literally), `compPotential`, `vertexTerm`, `globalMinDeg`, `F`;
  **54 theorems, no `sorry`, no `axiom`**, every one
  `[propext, Classical.choice, Quot.sound]`: `degree_isolate` (and its three
  cases), **P1** `potential_isolate`, **P2** `potential_isolate_le_sub_one`,
  **P2r** `potential_isolate_regular` (an equality, constraining only the
  neighbours of `w`) with `potential_isolate_le_regular`,
  `potentialMinus_le_potential`, `potentialMinus_eq_sum_compPotential`,
  `compPotential_nonneg`, `potentialMinus_nonneg`,
  `potentialMinus_eq_sum_vertexTerm`, `potentialMinus_le_F`,
  `potentialMinus_eq_F_of_connected`, **additivity** `potentialMinus_add`
  (`Disjoint (supp G₁) (supp G₂) → f⁻ (G₁ ⊔ G₂) = f⁻ G₁ + f⁻ G₂`) through
  `reachable_sup_iff` and `vertexTerm_sup`, **B1** `potentialMinus_cubic`
  (`f⁻ = N/6 − 1/6`) and the optional floor `potentialMinus_ge_five_sixths`.
  Imported by `lean/MOSPFormalization.lean`; builds in 1.4 s; `lake build`
  passes (`reports/scratch/edwards_mcdermid/05_potential/lake_build.log`).
- **Checked before stated** (`05_potential/check.py`, `check.log`,
  `summary.json`; 2.5 s): every statement in the form Lean proves it, in exact
  rationals, on 20,000 random graphs at `n ≤ 12` with isolated vertices,
  10,000 random disjoint unions, 1,996 embedded connected cubic graphs —
  1,076,930 (graph, `w`, `v`) for `degree_isolate`, 129,602 for P1, 13,723 for
  P2, 4,806 for the neighbours-only P2r (the one statement beyond item 02's
  checks), 10,000 unions for additivity, 70,283 for the reachability
  characterisation, 52,969 components for non-negativity. **Zero violations.**
- **Three choices beyond §2.6** (report §5.4): additivity goes through the
  per-vertex form `vertexTerm` (a pointwise identity on `V`), not through a
  bijection of component types; `compPotential G C` replaces
  `fminus (G.restrict C)` — no `restrict` is defined here, and if item 08's
  disconnected case wants `G = restrict C ⊔ restrict Cᶜ` it defines it and uses
  `potentialMinus_add`; `vertexTerm_congr` handles the decidability instance
  that `sup_comm` changes.
- **Axiom check**: 54 new `#print axioms` lines in `paper1/axiom_check.lean`
  (`05_potential/axiom_check.log`; `make -C paper1/latex axioms`: 425 theorems
  checked, 0 failures). `POTENTIAL_PROVED` (54 names) folded into
  `learning.sandwich.ALL_PROVED`.
- **Sandwich stage** `python -m learning.sandwich --stage degree_bound`:
  `potential_minus_lean` (the Lean definition transcribed) against
  `learning.edwards_mcdermid.fminus` on 500 random graphs, the per-vertex form
  on the same 500, additivity on 500 disjoint unions: 19 rows, **4,293 checks,
  0 violations** (`05_potential/sandwich.log`).
- **Tests**: 2 new in `tests/test_edwards_mcdermid.py` (38 in all; the stage's
  row count updated to 19).
- **Report**: `reports/edwards_mcdermid.md` §5 (the check's counts, the
  definitions, the 54 statements with their proofs, the choices beyond §2.6,
  the axiom and sandwich records, kill verdict none, regenerate commands, what
  it does not claim).
- **Gate**: **PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,787
  passed, 2 skipped, 1 xfailed in 273 s, the 2 new tests included;
  pathwidth_solver pytest 123 passed in 385 s; `make -C paper1/latex check` ok,
  74 pages, the paper untouched). Log: `05_potential/gate.log`.

### Blockers
None. Notes for later items: `G.degree` cannot be passed as a bare function to
`Finset.inf'` / `exists_mem_eq_inf'` (its `Fintype (neighborSet v)` instance
argument sits between the explicit ones) — write `(fun v => G.degree v)`;
`rw [← sum_compFinset]` needs `G` given explicitly (it is not in the right-hand
side); in current Mathlib `if_pos` / `if_neg` / `dif_pos` / `dif_neg` are
deprecated for `ite_eq_left` / `ite_eq_right` / `dite_eq_left` / `dite_eq_right`;
`SimpleGraph.ConnectedComponent` has `Fintype` under `DecidableRel G.Adj` but
no `DecidableEq`, so `compFinset` is a classical filter and `sum_compFinset` is
`sum_fiberwise` under `classical`; `isolate` is `MOSPFormalization.isolate G w`
(no dot notation), and its `DecidableRel` instance is declared in this file.
For item 07, the `j`-identity is `potential_isolate` with `one_sub_g_eq`; for
item 08, the disconnected case is `potentialMinus_add` plus a `restrict`
whose two halves have disjoint supports; for item 09, the per-component bound
adds `compPotential` over `potentialMinus_eq_sum_compPotential`.

### Next
Item 06: `DegreeBound/SPReduction.lean` — `SPStep G v H` (degrees 1 and 2
only), `SPReduces`, `IsSPReduced`, `IsBasic`; R1 (`edgeFinset_card_lt`),
`exists_reduced_reduct`, R2 (`degree_le`, `f_le`, `f_sub_ge_of_isolated`), R3
(`isolate_comm`), R4 (`isolate_comm` for sequences and finsets), R5
(`sup_of_disjoint`; `reachable_sup_iff` here is the reachability half of it),
R6 optional; all checked in item 02 on every graph to 9 (R3 on every (graph,
step, `w`), 3,115,987).

---

## Iteration 6 — 2026-11-02 03:35–03:58 UTC — item 06: Lean (iii), the series-parallel reduction system, basic graphs, degree monotonicity, and the commutation of deletion with reduction

### Completed
- **`lean/MOSPFormalization/DegreeBound/SPReduction.lean`** (namespace
  `MOSPFormalization.DegreeBound`, imports `Potential`): `ndeg` (the degree as
  `Set.ncard`, instance-free; `ndeg_eq_degree` pins it), `degSum`, `isolateSet`
  (`G − X`), `restrict` (`G|S`), `inductive SPStep G v H` with the three
  constructors `pendant` / `suppress` / `triangle` (operations 2–4; operation 1
  is the identity, report §2.1 (1)), `SPReduces` (`ReflTransGen`),
  `IsSPReduced`, `IsBasic`; **69 theorems, no `sorry`, no `axiom`**, every one
  `[propext, Classical.choice, Quot.sound]`. **R1** `SPStep.degSum_lt` and
  `exists_reduced_reduct` (strong induction on the degree sum),
  `IsSPReduced.eq_of_spReduces`; **R2** `SPStep.ndeg_le`, `SPReduces.ndeg_le`,
  `SPReduces.degree_le`, `SPReduces.potential_le`,
  `SPReduces.potential_sub_ge_of_isolated`, `SPReduces.supp_subset`; **R3**
  `SPStep.isolate_comm` (zero steps iff `v` pendant at `w`; else one step, pendant
  when `w ∈ N(v)`, the same kind otherwise), `SPStep.isolateSet_comm` (finset
  form, `v ∉ X`); **R4** `SPReduces.isolateSet_comm` (`X ⊆ supp H` ⇒
  `SPReduces (G − X) (H − X)`, by head induction: an acted vertex ends isolated),
  `SPReduces.isolate_comm`, `isolate_comm_of_isolated`; **R5**
  `SPStep.sup_of_disjoint`, `SPReduces.sup_of_disjoint` (+ the `supp` form);
  the `restrict` lemmas item 08's disconnected case needs
  (`restrict_sup_restrict_compl`, `isolate_restrict`, `restrict_eq_self`). R6
  (optional) not proved. Imported by `lean/MOSPFormalization.lean`; the file
  compiled clean on its first full attempt; `lake build` passes
  (`reports/scratch/edwards_mcdermid/06_reduction/lake_build.log`).
- **Checked before stated** (`06_reduction/check_r3.py`, `check_r3.log`,
  `summary.json`; 3 s on 8 workers at load 0.3): every graph on 1–9 vertices
  (288,266). R3 re-run **in the form the proof produces** (which case, which
  constructor): 3,115,987 (graph, step, `w`) triples — 95,300 zero-step, all
  pendant-at-`w`; 3,020,687 one-step, all of the predicted kind — item 02's
  totals to the triple; R3X on 1,179,468 random finsets; R4 replayed along
  288,266 random maximal reductions with 864,798 random `X ⊆ supp H`; R5 on
  25,566 steps with a random `K` off the support; R1/R2 on all 393,156 steps;
  step existence on 2,579,255 (graph, vertex). **Zero violations; kill checks:
  none fired.**
- **Eight choices beyond §2.6** (report §6.4): the step carries its vertex and
  states the neighbourhood by adjacency facts, not degrees (no decidability
  instance in the relation); `ndeg` makes `IsSPReduced`, `IsBasic`, R1, R2
  instance-free (no `Subsingleton.elim` anywhere); R1 on the degree sum, not
  the edge count; `isolateSet` defined directly, the fold recovered as
  `isolateSet_insert`; R4's hypothesis is `X ⊆ supp H` with the induction on
  the *sequence* (a `Finset`-first induction does not go through as §2.6 wrote
  it); R5's disjointness instance-free; `restrict` lives here; R6 skipped.
- **Axiom check**: 69 new `#print axioms` lines in `paper1/axiom_check.lean`
  (`06_reduction/axiom_check.log`; `make -C paper1/latex axioms`: **494
  theorems checked, 0 failures**). `SP_REDUCTION_PROVED` (69 names) folded into
  `learning.sandwich.ALL_PROVED`. No new sandwich stage (nothing numerical).
- **Tests**: 3 new in `tests/test_edwards_mcdermid.py` (41 in all): R3 in the
  Lean form, R3X, R4, R5, EX on 300 random graphs at 2–11 vertices; the
  brute-force summary's counts and zero violations; the 69 names declared
  (namespaces resolved) / imported / audited, no `sorry`, no `axiom`.
- **Report**: `reports/edwards_mcdermid.md` §6 (the check's table, the
  definitions, the 69 statements with their proofs, the choices beyond §2.6,
  the axiom record, kill verdict none, regenerate commands, what it does not
  claim).
- **Gate: PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,790
  passed, 2 skipped, 1 xfailed in 273 s, the 3 new tests included;
  pathwidth_solver pytest 123 passed in 385 s; `make -C paper1/latex check` ok,
  74 pages, the paper untouched). Log: `06_reduction/gate.log`.

### Blockers
None. Notes for later items: `SPStep` is stated with adjacency facts
(`G.Adj v x`, `∀ z, G.Adj v z → z = x`), so a degree-1/2 hypothesis is
converted by `ndeg_eq_one_iff` / `ndeg_eq_two_iff` (`exists_spStep_of_ndeg`
does it); every intermediate graph of a `ReflTransGen` induction is
instance-free, so state along-the-sequence facts with `ndeg` and convert with
`ndeg_eq_degree` at the ends (`SPReduces.degree_le` is the pattern); in this
Mathlib `symm` fields of a `SimpleGraph` structure literal are `Std.Symm` and
need `⟨fun _ _ h => …⟩`; `Set.mem_diff` and `Set.ncard_diff_singleton_add_one`
are deprecated for `Set.mem_sdiff` / `Set.ncard_sdiff_singleton_add_one`;
`induction h using Relation.ReflTransGen.head_induction_on with | refl | @head a c h' h ih`
needs `unfold SPReduces at h` first; the `rw [isolate_comm]` inside
`SPStep.isolate_comm` must name `MOSPFormalization.DegreeBound.isolate_comm`
(the namespace `SPStep` shadows it). For item 07: `nonbasic_reduct_ne_bot`
is `IsBasic`'s second clause with `restrict_eq_self` (one component on the
support); the hinge `j₄ ≥ g'(d)` is `SPReduces.ndeg_le` (survivor: W3) or
`SPReduces.potential_sub_ge_of_isolated` with `g'_le_g` (reduced away). For
item 08: `SPReduces.isolateSet_comm` with `X* ⊆ supp G*`,
`SPReduces.sup_of_disjoint` with `restrict_sup_restrict_compl` and
`potentialMinus_add`; `exists_reduced_reduct` for `G*`.

### Next
Item 07: `DegreeBound/Step.lean` — `minNbrDeg`, the paper's two-key choice
of `w`, `j_identity` (SJ: P1 with W4), `j4_ge` (S0), `step_inequality` (S1,
`1 + F G* ≤ F G` in its four cases; **not S1′**, which is false, §2.4),
`step_inequality_fminus`, `nonbasic_reduct_ne_bot`; all checked in item 02
(S0 on 1,093,524, SJ on 157,324, S1 on 137,573 pairs).

---

## Iteration 7 — 2026-11-02 04:10–04:35 UTC — item 07: Lean (iv-a), the step inequality `1 + f⁻(G*) ≤ f⁻(G)` for a connected non-basic graph

### Completed
- **`lean/MOSPFormalization/DegreeBound/Step.lean`** (namespace
  `MOSPFormalization.DegreeBound`, imports `SPReduction`): **21 theorems, no
  `sorry`, no `axiom`**, every one `[propext, Classical.choice, Quot.sound]`.
  **All four cases of the paper (pp. 11–12) are proved; the item's fallback
  (the regular case as a named gap, S1 as a hypothesis `hstep` of item 08) is
  not needed.** `minNbrDeg` and the two-key rule as hypotheses `hmax` / `htie`,
  `exists_paper_choice` (the `w` item 08 constructs); `supp_nonempty_of_not_isBasic`,
  `three_le_globalMinDeg`, `four_le_degree_of_not_isBasic` (derived, not
  assumed), `isBasic_of_spReduces_bot` and `nonbasic_reduct_ne_bot` (`G* ≠ ⊥`
  for *every* reduct, from the definition of `IsBasic` alone — no confluence),
  `exists_pos_degree_of_ne_bot`; **SJ** `one_add_potential_isolate` (unsorted)
  and `j_identity` (the paper's `j₁, j₂, j₃` for *any* two distinct
  neighbours — sorting is presentational); **S0** `j4_ge` (without the paper's
  `d ≥ 3`, which Lean's linter found unused) and `j4_nonneg`;
  `sum_g'_neighbors_ge`, `sum_g'_neighbors_eq`; `degree_eq_of_reachable` (the
  regular case: the tie-break's only use, exactly where item 02 found S1′
  failing); **S1** `one_add_F_le` (`1 + F G* ≤ F G`, one theorem with the four
  branches R / A / B1 / B2 of report §7.3's case table) and
  `one_add_potentialMinus_le` (`1 + f⁻(G*) ≤ f⁻(G)`); `structure StepData`
  with instance fields and `StepData.one_add_F_le`,
  `StepData.one_add_potentialMinus_le`. Imported by `lean/MOSPFormalization.lean`;
  compiled on the first full attempt up to two elaboration slips (an anonymous
  `Finset.Nonempty` constructor; explicit instance arguments in the structure),
  no statement changed; `lake build` passes (`07_step/lake_build.log`).
- **Checked before stated** (`07_step/check.py`, `check.log`, `summary.json`;
  2 s on 8 workers at load 0): every connected graph of minimum degree 3 on
  4–9 vertices (`nauty-geng -c -d3`, 87,004 graphs, 82,419 not basic), every
  two-key `w` (133,055 pairs — item 02's S1 count to the pair), canonical
  reduct + 3 random ones (never different). Re-run **in the form the proof
  produces**: which branch fires (R 315 / A 125,252 / B1 7,478 / B2 10) and
  that branch's inequalities; the new statements (unsorted SJ, `j_identity`
  for a random pair, `j₄ ≥ g'(d)` on 910,385 (triple, `v`), the neighbour-sum
  bound on 822,729 (pair, `v₀`), regular-case propagation, `Δ ≥ 4`,
  `G* ≠ ⊥`); S1 in both forms. **Zero violations; kill checks: none fired.**
- **Axiom check**: 21 new `#print axioms` lines in `paper1/axiom_check.lean`
  (`07_step/axiom_check.log`; `make -C paper1/latex axioms`: **515 theorems
  checked, 0 failures**). `STEP_PROVED` (21 names) folded into
  `learning.sandwich.ALL_PROVED`; `--stage lean` audits them (then
  `--stage degree_bound` re-run so `reports/sandwich_tables.md` is byte-identical
  to HEAD — the file holds the last stage run, a trap noted below).
- **Tests**: 3 new in `tests/test_edwards_mcdermid.py` (44 in all): S1 in the
  Lean form on 150 random connected min-degree-3 graphs at 5–10 vertices; the
  brute-force summary's counts and zero violations; the 21 names declared /
  imported / audited, no `sorry`, no `axiom`, the structure, `minNbrDeg` and the
  tie-break hypothesis present.
- **Report**: `reports/edwards_mcdermid.md` §7 (the check's table, definitions,
  the statements with their proofs, **the case table mapping each paragraph of
  pp. 11–12 to its branch and the lemmas it uses**, seven choices beyond §2.6,
  the axiom record, kill verdict none, regenerate commands, what it does not
  claim).
- **Gate: PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,793
  passed, 2 skipped, 1 xfailed in 275 s, the 3 new tests included;
  pathwidth_solver pytest 123 passed in 422 s; `make -C paper1/latex check` ok,
  74 pages, the paper untouched). Log: `07_step/gate.log`.

### Blockers
None. Notes for later items: an anonymous constructor `⟨v, hv⟩` for
`(s : Finset _).Nonempty` elaborates as `Exists.intro` inside `dite_eq_left`
and then `inf'`'s proof argument mismatches — name it with
`have hne : s.Nonempty := ⟨v, hv⟩` first; `supp` takes only `[Fintype V]`
before `G` (the `DecidableEq` variable is not included), so never spell
`@supp V _ _ G inst` — in a structure, `[instG : DecidableRel G.Adj]` as a
field makes `supp G` / `G.degree` elaborate in later fields with no explicit
instances; `push_neg` is deprecated for `push Not at h`; `j4_ge` needs the
vertex named (`(v := v) rfl`) when the degree is given by `rfl`;
`python -m learning.sandwich --stage X` overwrites `reports/sandwich_tables.md`
with stage `X`'s tables only, so finish with `--stage degree_bound` (what
HEAD holds). For item 08: `exists_paper_choice` gives `w` from
`(supp G).Nonempty`; `exists_reduced_reduct (isolate G w)` gives `G*` with no
instance (use `classical`); `one_add_potentialMinus_le` is S1 in the
per-component form; `nonbasic_reduct_ne_bot` for `G* ≠ ⊥`; connectivity of
the support must be supplied by item 08's component split (`restrict` and
`potentialMinus_add`); the regular branch's `linarith` and B2's `nlinarith`
need the product `(Δ − 2)(g'(3) − g'(Δ)) ≥ 0` given explicitly.

### Next
Item 08: `DegreeBound/ReductionTheorem.lean` — `exists_reduction_set` (T1,
Theorem 3.2) by strong induction on `|supp G|`: basic → `X = ∅`;
disconnected → one component and the rest (`restrict_sup_restrict_compl`,
R5 `SPReduces.sup_of_disjoint`, `potentialMinus_add`); connected non-basic →
`exists_paper_choice`, `exists_reduced_reduct`, S1
(`one_add_potentialMinus_le`), the induction hypothesis on `G*`, R4
`SPReduces.isolateSet_comm` with `X* ⊆ supp G*`, transitivity,
`X = insert w X*`. Checked in item 02 on all 89,972 reduced non-empty graphs
to 9 (T1), with `r(G − X) = B` on all.

---

## Iteration 8 — 2026-11-02 04:46–05:20 UTC — item 08: Lean (iv-b), Theorem 3.2, the reduction theorem by induction on the support

### Completed
- **`lean/MOSPFormalization/DegreeBound/ReductionTheorem.lean`** (namespace
  `MOSPFormalization.DegreeBound`, imports `Step`): **41 theorems and one
  structure, no `sorry`, no `axiom`**, every theorem
  `[propext, Classical.choice, Quot.sound]`. **T1** `exists_reduction_set`:
  `IsSPReduced G → G ≠ ⊥ → ∃ X B (_ : DecidableRel B.Adj), IsReductionSet G X B`
  (the six clauses `X ⊆ supp G`, `SPReduces (G − X) B`, `B ≠ ⊥`, `IsSPReduced B`,
  `IsBasic B`, `|X| + f⁻(B) ≤ f⁻(G)` as a `Prop` structure; the instance on `B` is
  bound in the existential because `potentialMinus B` needs one), and
  `exists_reduction_set_and` in §2.6's conjunction form. **Neither fallback of the
  item is used**: S1 is item 07's lemma, R3–R4 are item 06's theorems, and no
  confluence fact appears anywhere. The proof `exists_reduction_set_of_card` is a
  strong induction on `|supp G|` quantifying over the graph *and its instance*,
  with the paper's three cases: `isReductionSet_empty` (basic);
  `exists_reduction_set_of_split` + `isReductionSet_sup` (support disconnected:
  `C` the component of a support vertex `u` missing a support vertex `v`,
  `G = G|C ⊔ G|Cᶜ`, both halves reduced, non-empty and smaller, the hypothesis on
  each, R5 twice, `isSPReduced_sup`, `isBasic_sup`, `potentialMinus_add` on both
  sides); `isReductionSet_insert` (connected non-basic: the two-key `w`, a reduced
  reduct `G*` of `G − w` under a classical instance, `X = insert w X*`, R4 for
  `(G − w) − X* →* G* − X*`, S1 for the inequality). Supporting lemmas: the
  degrees of `G|S` for `S` closed under adjacency and `isSPReduced_restrict`;
  `isolateSet_sup`, `isolateSet_union_of_forall_not_adj`; the transfer of "basic"
  to a disjoint union through `isBasic_clause_of_agree` (for any `H ≥ G₁` agreeing
  with `G₁` at the `G₁`-vertices, the `H`-component of such a vertex is its
  `G₁`-component — `reachable_iff_of_agree`, `supp_eq_of_agree`); and the
  per-component statements for item 09: `isBasic_component`,
  `compPotential_cubic` (`= |C|/6 − 1/6`), `compPotential_ge_five_sixths` (for
  components with a vertex of degree `≥ 4` — *not* "second kind", §2.1 (3)),
  `five_le_card_compFinset`, `compPotential_cubic_or_ge_five_sixths`. Imported by
  `lean/MOSPFormalization.lean`; compiled on the first attempt (one style warning,
  `letI` → `let`); `lake build` passes (`08_reduction/lake_build.log`, 1.4 s).
- **Checked before stated** (`08_reduction/check.py`, `check.log`, `summary.json`;
  2.8 s on 8 workers at load 0.3): every graph on 1–9 vertices (288,266), the
  **Lean induction replayed** on each of the 89,972 reduced non-empty ones
  (item 02's T1 count to the graph; 214,768 recursion nodes: 89,973 basic, 1
  disconnected, 124,794 connected; R4 decided by a search over step sequences on
  all 124,794; `|X|` = 0–5 on 5,209 / 47,734 / 34,067 / 2,923 / 38 / 1), plus
  20,000 random disjoint pairs on `≤ 5` vertices (9,203 both reduced, 14,201 both
  basic; 8,212 unions through the induction, where the disconnected case fires
  3,556 times with R5 by search 7,112 times); the per-component statements on
  290,103 + 16,424 components; `restrict` degrees and the `isolateSet` identity
  on every graph. **Zero violations; kill checks: none fired.**
- **Axiom check**: 41 new `#print axioms` lines in `paper1/axiom_check.lean`
  (`08_reduction/axiom_check.log`; `make -C paper1/latex axioms`: **556 theorems
  checked, 0 failures**). `REDUCTION_THEOREM_PROVED` (41 names) folded into
  `learning.sandwich.ALL_PROVED`; `--stage lean` audits them
  (`sandwich_lean.log`), `--stage degree_bound` re-run so `reports/sandwich_tables.md`
  is byte-identical to HEAD (4,293 checks, 0 violations).
- **Tests**: 3 new in `tests/test_edwards_mcdermid.py` (47 in all): the induction
  replayed on 300 random reduced graphs at 4–13 vertices, about half disjoint
  unions, every clause of T1 with `SPReduces` by search and the three union
  transfers; the brute-force summary's counts and zero violations; the 41 names
  declared / imported / audited, no `sorry`, no `axiom`, T1 stated with
  `IsSPReduced G` and `G ≠ ⊥`, no `Confluence` and no `hstep` in the code.
- **Report**: `reports/edwards_mcdermid.md` §8 (the check's table, definitions,
  the 41 statements with their proofs grouped as the Lean file is, seven choices
  beyond §2.6 and the item's wording, the axiom record, kill verdict none,
  regenerate commands, what it does not claim).
- **Gate**: **PASS** (`lake build` ok; `sorry` 0, `axiom` 0; MOSP pytest 1,796
  passed, 2 skipped, 1 xfailed in 326 s, the 3 new tests included;
  pathwidth_solver pytest 123 passed in 390 s; `make -C paper1/latex check` ok,
  74 pages, the paper untouched). Log: `08_reduction/gate.log`.

### Blockers
None. Notes for later items: a lemma named `IsSPReduced.restrict` or `IsBasic.sup`
would have its own name shadow the def `restrict` / the `⊔` lemma inside its body
(the declaration's namespace is open there), so the transfer lemmas are
`isSPReduced_restrict`, `isSPReduced_sup`, `isBasic_sup`, `isBasic_component`; a
component of `G₁ ⊔ G₂` is not a term of `(G₂ ⊔ G₁).ConnectedComponent`, so a
symmetric argument by `sup_comm` does not typecheck per component — state the
transfer for a general `H ≥ G₁` that agrees with `G₁` at the `G₁`-vertices and
apply it on either side; `set C := … with h` makes `C` a let-variable whose body
defeq is not reliably available to `exact`, so the split is a separate lemma with
`C : Set V` abstract and closure under adjacency as a hypothesis; a strong
induction over graphs must quantify over the `DecidableRel` instance too
(`∀ G [DecidableRel G.Adj], …`) and the hypothesis is applied as
`@ih m hm H instH rfl …`; `∃ (_ : DecidableRel B.Adj), …` binds a usable local
instance (Mathlib's `∃ (_ : Fintype α), …` pattern); `Finset.card_union_of_disjoint`
is a simp alias of `card_union_eq_card_add_card` and still works as a rewrite;
`rw [sup_comm a b] at h` needs the *present* order of `a ⊔ b` in `h`, not the
target order. For item 09: `exists_reduction_set G hG hne` gives
`⟨X, B, instB, h⟩` with `h.subset_supp`, `h.reduces`, `h.ne_bot`, `h.reduced`,
`h.basic`, `h.card_add_le`; the per-component bound adds `compPotential` over
`potentialMinus_eq_sum_compPotential` using `isBasic_component`,
`compPotential_cubic` and `compPotential_nonneg`; `pathwidth (G − X) + |X|` is the
`pathwidth_le_pathwidth_induce_add_card_compl` route of §2.6, and the pathwidth of
`restrict G C.supp` is the component's.

### Next
Item 09: `DegreeBound/Pathwidth.lean` — the named `Prop`s `CubicPathwidthBound τ`
and `ReductionPathwidthBound ρ`; `pathwidth_le_pathwidth_isolateSet_add_card`,
`pathwidth_eq_pathwidth_induce_supp`, `pathwidth_le_max_components`,
`pathwidth_basic_le` (`≤ f⁻(B) + τ n + ρ n + 1`, per component: cubic by (H1)
and `compPotential_cubic`; second kind by `pathwidth_le_pathwidth_erase_add_one`,
(H3) to `⊥`, `compPotential_nonneg`), A1 `pathwidth_le_potential_of_hypotheses`
(`+ τ n + 2 ρ n + 1`, from T1, the deletion lemma and (H3) for `G − X →* B`), A2
`pathwidth_le_degreeSum_of_hypotheses` (`+ τ n + 3 ρ n + 1`); `#print axioms`
rows; `learning/sandwich.py --stage degree_bound` extended. Checked in item 02 as
A1/A2 on every graph to 9 (§2.3) with the budgets of §2.5.
