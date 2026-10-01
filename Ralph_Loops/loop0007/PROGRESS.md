# loop0007 progress

Plan: fix both solvers to match `lean/MOSPFormalization/Search/` (owner's
decision 2026-10-01); items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0007/gate.py`.

Current: 1/10 SOLVED

## Setup — 2026-10-01

- Baseline: loop0006 complete. The repaired search is proved sound
  (`exec_repairedFullFilter_mospValue`). Chu & Stuckey's Theorems 1 and 2 are
  proved false as stated (`Search/PublishedTheorems.lean`). One `sorry` in code
  (`Sandwich.lean`, the §24 conjecture). 1,327 MOSP tests and 95
  pathwidth_solver tests pass.
- The production code still applies the published rules. No whole-instance
  false refutation is known. The code's runs reach nodes where its filter loses
  the last solution in 58 of 570,206 runs, all on gadget graphs, all at
  satisfiable `k`, and all answered correctly.
- No recertify or csearch process is running. `recertify` ended 2026-09-29
  with two entries open: `Random-125-125-2-2_0` (25) and `Random-125-125-2-3_0`
  (21).

## Iteration 1 — 2026-10-01 14:50

### Completed
- **Item 01.** `satisfiability/customer_search.py`: `decide(..., repaired_rules=False)`.
  The definite move fires on the first playable q passing `close ≥ open` and
  the matching test (`_has_definite_matching`, Kuhn, = `HasDefiniteMatching`).
  A q failing the matching is skipped, so the pick is `repairedFullFilter`'s.
  The better move cites only under premises 3, 4 and the matching at
  `cl(S ∪ {r})` (`IsRepairedBetter`). The flag forces the Python until item 02.
- **The Python now has Theorem 2** (`_better_move_pass`, ported from the C's
  `better_move_pass`). Before, `better_move=True` was inert under
  `native=False`. `better_move` and `better_move_dominators` are explicit
  parameters of `decide`. Python = C node for node, old rules, 117,828 runs.
- Flag off: identical to pre-change code on 35,264 decisions (status, nodes,
  witness). Pinned in a test by a digest computed before the change.
- `paper2/solver_fix_check.py`: the production filter equals the Lean
  `repairedFullFilter` transcription (and, flag off, `codeFullFilter`) at all
  16,244,090 node checks. It is node-sound at all 11,109,357 nodes with a
  solution. The matching equals the hereditary premise on 36,939,226
  candidates. 4,016,096 whole searches per setting are right. Graphs: 1–17
  vertices, exhaustive to 6. **Zero failures.** The old filter lost the node 302
  times (gadgets and pinned graphs) and never the answer.
- `tests/test_repaired_rules.py` (11 tests, 2 s); `paper2/solver_fix.md`
  created with the item 01 section; the stale "inert" comment in
  `tests/test_differential.py` corrected.
- Gate: PASS (1,338 MOSP tests, 95 pathwidth_solver tests).

### Blockers
- None. Note for later items: `paper2/search_soundness.md` quotes Python lines
  verbatim (`tests/test_search_soundness_doc.py`). The definite-move lines and
  `return kept or playable` were kept textually for that reason. Item 02/03
  edits to the C or the pathwidth solver may trip the same test.

### Next
- Item 02: the same flag in `customer_search.c` / `native.py`. The C has no
  better-move path that excludes q from the freed set; mirror
  `_better_move_pass` (`freed` excludes q, `need = opened_by − 1`). Compare
  against `decide(native=False, repaired_rules=True, better_move=...)` node for
  node. Then remove the "forces the Python" gate in `decide`.
