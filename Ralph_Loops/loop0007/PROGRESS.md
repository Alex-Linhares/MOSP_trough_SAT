# loop0007 progress

Plan: fix both solvers to match `lean/MOSPFormalization/Search/` (owner's
decision 2026-10-01); items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0007/gate.py`.

Current: 3/10 SOLVED

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

## Iteration 2 — 2026-10-01 15:20

### Completed
- **Item 02.** `customer_search.c`: new entry point `cs_decide_rules`
  (`cs_decide_variant` + `repaired_rules`). `cs_decide_variant` is now a wrapper
  with the flag off, and `cs_decide_fan`/`cs_decide` are unchanged.
  `has_definite_matching` is Kuhn over at most 128 stacks. The definite move
  skips a q that fails the matching. The better move collects the freed sets at
  the child (`d ≠ q`, `∅ ≠ left ⊆ own`), and a q that fails the matching does
  not cite. `native.decide_native(repaired_rules=)` calls the new entry point.
  `decide` no longer forces the Python when the flag is set.
- The C lines quoted in `paper2/search_soundness.md` are kept word for word,
  so `tests/test_search_soundness_doc.py` passes.
- `paper2/solver_fix_c_check.py` compares the C and the Python on 1,529
  instances: the test_native generator, the pinned counterexamples (both
  DEFINITE_CEX, Bug A, Bug B at 8 and 10 vertices, RUN_LOST, 10×13, 17×9,
  10×20), gadgets at 14–17, random graphs at 10–24, and 420 certified corpus
  instances at 10–125 under node caps. **1,557,980 calls, zero
  disagreements** in status, nodes or witness under either setting. Old and
  repaired never gave different answers. Node counts differed on 6,575 pairs,
  +0.03% nodes in total (capped runs, not a cost measurement).
- `tests/test_repaired_rules.py`: 16 tests (6 new for the C, and the
  "forces the Python" test removed). `paper2/solver_fix.md`: item 02 section,
  and the status-of-default paragraph updated.
- Gate: PASS (1,343 MOSP tests, 95 pathwidth_solver tests).

### Blockers
- None. Known by design and documented: with old move and memo both on, the C
  runs both and the Python drops the memo, so node-for-node comparisons use the
  other three settings. Customers with no products appear as root free moves
  in the C's order and not in the Python's, so witnesses are compared over
  active customers.

### Next
- Item 03: the pathwidth solver. `closing_search.c` was a verbatim copy of
  `customer_search.c`, so apply the same diff, and the analogous diff to
  `closing_search_w.c` for every WORDS (the matching's `owner` array needs 64·WORDS
  entries). Then `native.py` and `search.py` (which needs the Python port of
  `_better_move_pass` and `_has_definite_matching`). Then make
  `repaired_rules=True` the default in both solvers and record it at the top
  of `paper2/solver_fix.md`. Note: `pathwidth_solver/tests/test_identity_mosp.py`
  compares MOSP's C with the pathwidth C, so the two defaults must change
  together.

## Iteration 3 — 2026-10-01 16:05

### Completed
- **Item 03.** The pathwidth solver now carries `repaired_rules`.
  `closing_search.c` is again a byte copy of MOSP's `customer_search.c`, and the
  legacy wrapper calls `cs_decide_rules`. `closing_search_w.c` has the same diff
  for every WORDS: Kuhn's matching with `owner[64·WORDS]`, a per-frame `freed`
  scratch array, and `csw_decide` gained the parameter. `search.py` gained the
  flag and **a Python better move** (before, it was ignored on the Python path).
  It uses MOSP's `_apply_dominance` / `_subset_survivors` / `_better_move_pass` /
  `_has_definite_matching`. `native.py` passes the flag through.
  `src/customer_search.py` (the pristine copy) is untouched.
- **`repaired_rules=True` is now the default in both solvers**, in `decide` and
  `decide_native`, MOSP and pathwidth alike. This is recorded at the top of
  `paper2/solver_fix.md`. Four tools that model the published rules now name
  `repaired_rules=False`, with their pinned counts unchanged:
  `learning/fix_cost.py`, `paper2/search_check.native_decide`,
  `tests/test_fix_cost.py`, and the reference calls in
  `tests/test_search_certificate.py`. The pre-flag digest test in
  `tests/test_repaired_rules.py` names it too. On the 10×13 instance, the
  `prefix` revert's false refutation at the optimum disappears under the
  repaired premises.
- `paper2/solver_fix_pw_check.py` runs up to 8 implementations per call: the
  pathwidth Python, the multiword C at w2/w4/w8/w16, the legacy C, and MOSP's
  Python and C. It covered 1,319 instances at 4–992 vertices.
  **12,582,320 implementation-calls, zero disagreements** under either setting.
  The two settings never gave a different answer, and the repaired rules took
  0.02% more nodes over these capped runs, which is not a cost measurement.
  Data: `paper2/data/solver_fix_pw_check.json`.
- Tests: `pathwidth_solver/tests/test_repaired_rules.py` (8 new tests), and
  `test_identity_mosp.py` now runs under both settings (7 → 14 Python cases,
  and the C test covers better move × both settings).
- Gate: PASS (1,343 MOSP tests, 110 pathwidth_solver tests).

### Blockers
- None. No certified value changed in anything run here, and no false refutation
  was found. Note: the certificate emitter (`learning/search_certificate.py`)
  models only the published rules, so it certifies `repaired_rules=False`
  searches. Items 06–08 should either extend it or call the solver with the
  flag off when they compare against it.

### Next
- Item 04: what the repair costs, in paired runs (old against repaired), in nodes
  and seconds. Name `repaired_rules` explicitly on both sides, because the
  default is now `True`. The pathwidth benchmarks go through
  `pathwidth_solver/bench/run.py`, which uses the default and therefore
  repaired.
