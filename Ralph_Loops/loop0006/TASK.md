# TASK: Pebbling, and the soundness of the customer search, in Lean

## Philosophy
- Read `paper2/plan.md` (section 4 is what phase B serves),
  `paper2/equivalences.md` (the loop0005 census and its conventions),
  `paper2/problem_transformations.md` (how problems and proofs are written
  for the paper), `Ralph_Loops/loop0005/PROGRESS.md` (what the last loop
  did and how), and the `CLAUDE.md` blocks on the `better_move` bugs
  ("A dominance rule implemented only in the C had no test and was wrong",
  and "It happened again on 2026-09-26").
- **Two parts.** Phase A adds progressive black-white pebbling to the
  complex (Lengauer 1981 Thms 2-3; Kirousis & Papadimitriou 1986 §3,
  Thm 3.1). Phase B proves that the pruning rules of Chu & Stuckey's
  customer search never discard the last solution: the definite move
  (their Thm 1), the subset rule, the better move (their Thm 2, in its
  **corrected** form), the old move (their Thm 3), and the memo.
- **State before you prove, and check before you state.** Every Lean
  statement is first checked by brute force on small instances. The
  `better_move` rule has been wrong twice in code (`reports/better_move_bug.md`,
  especially §7: a wrong close count, a cross-rule cycle, and an early exit).
  **The rules are only sound in the order and form the fixed code uses**:
  `definite_move → subset_rule → better_move`, each citing only candidates
  still standing. A statement that ignores the order can be false. Find the
  exact form in `satisfiability/customer_search.py` (the Python reference)
  and in `satisfiability/customer_search.c` (`dominance_filter`), and in the
  certificate checker `learning/search_certificate.py`, whose premises are
  what the search must satisfy at each node.
- **No `sorry`, no `axiom`.** An item ends sorry-free or is marked blocked
  with the precise obstacle. Only items 11-12 may leave a stated gap, and
  only as a named `Prop` used as an explicit hypothesis (as loop0005 did
  with `EdgeSearchMonotonicity`), or as a line in
  `Ralph_Loops/loop0006/allowed_sorries.txt`.
- **Faithful definitions.** Pebbling is defined as in its sources (Cook &
  Sethi's black-white game as Lengauer states it, p. 466; the progressive
  restriction). The search is modelled at the level of its specification:
  states are closed sets, a move closes one customer, the cost of a state is
  the number of open customers. Do not define a rule's soundness as its own
  conclusion.
- Reuse the existing development: `lean/MOSPFormalization/` (MOSPGraph,
  VSEquivPW, Complex/ from loop0005, especially `Narrowness.lean` whose shack
  is the customer-search state and `EdgeSeparation.lean` which has
  Lengauer's VSG).

## Current Focus
Phase A (items 01-04): pebbling. Phase B (05-11): the search. Then 12
(assemble) and 13 (reserve).

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration.

## Acceptance Criteria (per item)
- [ ] Lean in `lean/MOSPFormalization/Complex/Pebbling*.lean` (phase A) or
      `lean/MOSPFormalization/Search/<Name>.lean` (phase B), imported from
      `lean/MOSPFormalization.lean`, each with a module docstring naming the
      source and the exact statement proved.
- [ ] Python checks in `paper2/complex_check.py` (pebbling) or a new
      `paper2/search_check.py` (phase B), with tests in `tests/`.
- [ ] Phase A updates `paper2/equivalences.md` and
      `paper2/problem_transformations.md` (a new problem §1.x and its
      transformations and proofs, in the existing style: formal proof, then
      *In plain English*). Phase B writes `paper2/search_soundness.md`: each
      rule stated precisely, its proof sketch, its Lean name, and what the
      certificate checker checks for it.
- [ ] `python3 Ralph_Loops/loop0006/gate.py` passes (lake build, imports of
      Complex/ and Search/, sorry/axiom count, pytest).
- [ ] The item is marked `- [x]` or `- [!]` (with a reason in PROGRESS.md).

## Completion Conditions
An item is DONE when solved, or blocked with the specific obstacle
documented. **If a rule turns out unsound as stated** (in its source or in
our code), that is a finding: state the correct form, prove a Lean
counterexample to the wrong one, check whether the C implements the right
one, and say so prominently in PROGRESS.md and in `paper2/search_soundness.md`.
Do not change the solver; the owner decides.

## Context
- **Sources**: `literature/lengauer_1981_black_white_pebbles_graph_separation.pdf`
  (§1-2, Thms 2-4; Def. 1: G_u and G_d), `paper2/literature/10_kirousis_papadimitriou_1986.pdf`
  (§3, Thm 3.1: mpb, mpbw), Chu & Stuckey 2009 (find it in `literature/` or
  `paper2/`; the rules and Thms 1-3 are described in `reports/customer_search.md`
  and `reports/chu_stuckey_plan.md`), `reports/better_move_bug.md` §7, and
  `reports/ml_nature.md` §15, §31, §32 (the harness, the fix variants, the
  certificate).
- **Code**: `satisfiability/customer_search.py` (`decide`, the rules),
  `satisfiability/customer_search.c` (`dominance_filter`),
  `learning/search_certificate.py` (the checker), `learning/differential.py`
  (the soundness harness), `pathwidth_solver/pathwidth/search.py` (the same
  search on graphs).
- **Lean**: `lean/` (Lake project, Mathlib master). `cd lean && lake build`.
- **Testing**: `python3 Ralph_Loops/loop0006/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md`, the solver (`satisfiability/`), `pathwidth_solver/`,
  or existing proved Lean files except to add an import to the root.
- Do NOT create a GitHub repository or push anything.
- Do NOT touch `solutions/`. Commit nothing yourself; the driver commits.
- Print mode: **ending your turn ends the session.** Never end on a
  background wait. Match processes by PID, never a bare `pkill -f <word>`.
- If a proof is not converging, stop at a clean state: keep proved lemmas,
  delete broken ones, write the obstacle down.
