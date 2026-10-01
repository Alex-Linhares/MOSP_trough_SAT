# TASK: Fix both solvers to match the soundness theorems, then re-check what rested on them

## Philosophy
- Read first, in full: `paper2/revised_algorithm.md` (section 4 of the paper:
  the search, each rule, the repairs and the main theorem; §4.6 is the
  revised algorithm in pseudocode), and `Ralph_Loops/loop0006/PROGRESS.md`
  (how the repairs were found and proved). Then the `CLAUDE.md` block that
  begins "Chu & Stuckey's Theorem 1 (the definite move) is false as
  published".
- **The owner's decision (2026-10-01): fix the solver to match the
  theorems, in both `satisfiability/` (MOSP) and `pathwidth_solver/`
  (pathwidth).** This loop is authorised to change solver code. It is the
  first loop that is.
- **What "match the theorems" means.** The production search must apply the
  *repaired* rules proved sound in `lean/MOSPFormalization/Search/`:
  - the definite move fires only when `q` is hereditarily definite
    (`IsHereditarilyDefinite`), tested by the matching condition
    (`HasDefiniteMatching`, equivalent by
    `isHereditarilyDefinite_iff_hasDefiniteMatching`), and only after the
    old test `close ≥ open` passes, so the old test is a cheap prefilter;
  - the better move drops `r` citing `q` only under the repaired premise
    (`IsRepairedBetter`: premise 3, and `q` hereditarily definite at
    `cl(S ∪ {r})`);
  - everything else unchanged: the free move, the subset rule with its index
    tie-break, the order `definite → subset → better` citing only standing
    candidates, the old move with its reinsertion test, and the memo, all
    proved sound as coded.
  The main theorem (`exec_repairedFullFilter_mospValue`) then covers the code.
- **Change safely.**
  - Keep the old behaviour available behind a flag (e.g.
    `repaired_rules=False`) for comparison and regression. The repaired rules
    become the default, in both solvers, only once items 01-03 pass every
    check below. Record the default change prominently.
  - The C and the Python must agree node for node, under both settings, as
    `tests/test_native.py` already requires for other flags.
  - The repaired filter must never keep a candidate the theorems do not
    allow. Check it against the independent oracle in
    `paper2/search_check.py`, which shares no code with the solver.
  - Every certified value must stay the same. Re-run
    `python -m benchmarks.corpus` and compare. A changed value is a finding,
    and must never be silently overwritten.
- **Never write to `solutions/`.** Re-certification results go to a report
  and a CSV. The owner applies them.
- **Nodes, not seconds**, with seconds beside them. A censored run is a lower
  bound.
- **State the size range** every conclusion covers.

## Current Focus
Items 01-03 change the code (Python, C, pathwidth solver). Items 04-05
measure cost and soundness. Items 06-08 re-check what rested on the old
rules. Item 09 updates the documents. Item 10 is the reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration.

## Acceptance Criteria (per item)
- [ ] Code changes in `satisfiability/customer_search.py`, `customer_search.c`,
      `native.py`, and `pathwidth_solver/pathwidth/`; each with tests.
- [ ] A section appended to `paper2/solver_fix.md`: what changed, the tests,
      the measurements (table), the size range, the regenerate command.
- [ ] `python3 Ralph_Loops/loop0007/gate.py` passes (lake build, sorry
      count, MOSP pytest ~2.5 min, pathwidth_solver pytest ~6 min).
- [ ] The item is marked `- [x]`, or `- [!]` with the reason in PROGRESS.md.

## Completion Conditions
An item is DONE when solved, or blocked with the obstacle documented. **If
the repaired solver ever gives a different certified value, or a false
refutation is found under the old rules, stop the item there.** Record it at
the top of `paper2/solver_fix.md` and in PROGRESS.md, with the instance and
how to reproduce it. That is the most important possible finding.

## Context
- **The repairs, in Lean**: `Search/DefiniteMove.lean` (`IsHereditarilyDefinite`,
  the counterexample), `Search/DefiniteMatching.lean` (the matching form),
  `Search/BetterMove.lean` (`IsRepairedBetter`), `Search/Decide.lean` (the
  theorem, `CodeNodeRepaired` for checking old-code runs node by node).
- **The independent oracle and counterexamples**: `paper2/search_check.py`
  (`DEFINITE_CEX`, the 8- and 10-vertex Bug B instances, the gadget
  generator), `paper2/definite_hunt.c` and `definite_hunt_gen.py`.
- **The search**: `satisfiability/customer_search.py` (`decide`, `solve`,
  `_apply_dominance`), `customer_search.c` (`dominance_filter`,
  `subset_pass`, `better_move_pass`), `satisfiability/native.py`. The same
  search on graphs: `pathwidth_solver/pathwidth/search.py`,
  `closing_search.c`, `closing_search_w.c`, `native.py`.
- **Re-certification inputs**: `learning/search_certificate.py` (the emitter
  and checker), `benchmarks/results/compute_ledger.csv` (the `csearch` and
  `recertify` rows), `recertify/results.json`, `solutions/*.json`
  (read-only), `pathwidth_solver/bench/results/` and `bench/run.py`.
- **Testing**: `python3 Ralph_Loops/loop0007/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md` or existing Lean proofs. Do NOT push.
- Do NOT write to `solutions/`. Do NOT run `benchmarks.csearch`,
  `benchmarks.recertify` or `benchmarks.overnight` in modes that write to
  `solutions/`.
- Commit nothing yourself; the driver commits.
- Print mode: **ending your turn ends the session.** Never end on a
  background wait. Match processes by PID, never a bare `pkill -f <word>`.
- Compute: 32 cores; use up to 24. Check `uptime` first; another project's
  loop may be using some.
- C entry points: add a parameter or a new entry point; keep `native._build`
  compiling to a scratch name and renaming into place.
