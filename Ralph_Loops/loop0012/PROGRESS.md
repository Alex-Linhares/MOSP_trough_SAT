# loop0012 progress

Plan: `reports/edwards_mcdermid_plan.md` — the Edwards–McDermid (2015)
degree-sequence upper bound on pathwidth, verified on every graph with a
proved pathwidth and formalised in Lean conditional on the cubic base case
(Fomin & Høie 2006) and the reduction lemma (Kneis et al. 2009), both as
named `Prop`s; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0012/gate.py`.

Current: 0/11 SOLVED

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
  `idle`, or `LOOP_COMPLETE` in its PROGRESS.md) and for its last commit.
  The driver refuses to start while `git status` shows changes under
  `learning reports tests benchmarks satisfiability mosp customer_inter`;
  commit or stash first. Check that the owner's `run_unlimited.py` is not
  running (by PID), or leave it its cores. Launch as
  `Ralph_Loops/Ralph_Loop_Guide.md` "As practised here" says, with the API
  key from `~/.config/anthropic/api_key`; never a second driver on this
  folder.

---
