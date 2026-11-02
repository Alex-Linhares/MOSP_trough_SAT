# loop0012 progress

Plan: `reports/edwards_mcdermid_plan.md` — the Edwards–McDermid (2015)
degree-sequence upper bound on pathwidth, verified on every graph with a
proved pathwidth and formalised in Lean conditional on the cubic base case
(Fomin & Høie 2006) and the reduction lemma (Kneis et al. 2009), both as
named `Prop`s; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0012/gate.py`.

Current: 1/11 SOLVED

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
