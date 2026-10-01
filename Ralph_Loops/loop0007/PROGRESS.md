# loop0007 progress

Plan: fix both solvers to match `lean/MOSPFormalization/Search/` (owner's
decision 2026-10-01); items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0007/gate.py`.

Current: 5/10 SOLVED

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

## Iteration 4 — 2026-10-01 17:55

### Completed
- **Item 04.** Paired runs, `repaired_rules=False` against `True`, both named,
  in one worker per pair with the order alternating. `paper2/solver_fix_cost.py`
  (stages mosp40, cs, cs125, pw, overhead) and `paper2/solver_fix_cost_tables.py`.
  Section "Item 04" in `paper2/solver_fix.md`; tables in
  `paper2/data/solver_fix_cost_tables.md`.
- **The answers never differed, and no certified value moved.** Every finished
  refutation of `optimum − 1` was `unsat` under both settings. All 731 pathwidth
  graphs proved under both settings got the same width, and every proved width
  equals the recorded bench result.
- **Cost, nodes on finished pairs:**
  - corpus n ≤ 40 (6,135): +0.004%;
  - Chu & Stuckey 50–100 (118 of 125 finished, 600 s per call): +0.30%; worst
    class `100-50-4` at +1.0%; worst pair 1.013;
  - 125 × 125 (11 of 23 finished under 2 × 10⁸ nodes): −0.01%;
  - pathwidth `solve` (880 graphs, 731 proved): +2.0%, mostly Rome; the median
    pair is 1.000 and the worst 1.13.
- **Cost per node, measured quietly:** +2% in the MOSP C (−0.1% to +5.8% over
  six hard instances). About +6% in the pathwidth descents, measured under load.
- **How often the old test passes and the matching fails:** 0.07–0.13% of
  definite candidates at 9–100 customers, 0.27% at 125 (to the cap), and 0.02% in
  the pathwidth counter pass. Better-move pairs fail at 0.02–0.06%. The definite
  move stops firing at 0.007–0.08% of filter calls. Usually a later candidate
  fires instead.
- **Instrumentation, no change to the search:** per-thread rule counters in
  `customer_search.c` (`cs_last_rule_counts`), copied byte for byte to
  `closing_search.c`; `native.last_rule_counts()`. They do not slow the
  published rules against the pre-counter C (0.95–0.99× per node). New test
  `test_the_rule_counters_count_the_repair_and_change_nothing`.
- Gate: PASS (1,344 MOSP tests, 110 pathwidth_solver tests).

### Blockers
- None. Not measured: the tree size of the day-long refutations
  (`Random-100-100-2`, `125-125-2/4`), which were censored on both sides. For
  them the item reports per-node cost and counter rates only. Excluded:
  `DorogovtsevGoltsevMendesGraph` (named, 3,282 vertices), which ignores the time
  budget on the Python path; its pool was stopped by PID. `closing_search_w.c`
  has no counters, so the pathwidth counter rates come from the MOSP C on
  components of at most 128 vertices.

### Next
- Item 05: soundness of the fixed solver against `paper2/search_check.py`.
  `native.last_rule_counts()` is available if a check wants to know where the
  repaired rules changed a run.

## Iteration 5 — 2026-10-01 19:30

### Completed
- **Item 05.** `paper2/solver_fix_soundness.py` (stages port, gadget, diff40,
  diff75, tables). Section "Item 05" in `paper2/solver_fix.md`. Tables in
  `paper2/data/solver_fix_soundness_tables.md`.
- **The whole search, repaired, from the theorems.** `repaired_decide` is
  `search_check.search_decide` with the definite move gated by `d_hereditary`
  (enumeration, not matching) and the better move by `IsRepairedBetter`. It
  uses only `search_check` predicates. Under all 64 configurations at every `k`,
  it was compared with the oracle (`Sol_k`), with node soundness at every
  expanded node, with the C (`repaired_rules=True`, answer and nodes) and with
  the production Python. **17,431,232 runs over 52,592 graphs at 1–17
  vertices** (every labelled graph to 6, atlas 7 × 5 labellings, random 8–13,
  pinned counterexamples, 12,000 family-4 gadgets at 12–17 at opt−1/opt/opt+1).
  **Zero** answer failures, node losses (51.5 M nodes checked), C mismatches,
  Python mismatches and witness failures. 4,203 runs differ from the published
  port, so the comparison does tell the two rule sets apart.
- **Differential harness with the repaired defaults**, over every certified
  instance: 43,935 at 9–40 (1,757,280 calls) and 1,231 at 50–75 (29,544 calls).
  **Zero** disagreements, contradictions, witness failures and censored calls.
  The lattice oracle agrees on all 13,612 instances it can check.
- **No certified value changed.** `benchmarks.corpus` still reads 6,374 / 6,376.
  `solutions/` is clean against HEAD; digest `229207b225a666a5`.
- New test `test_the_c_runs_the_repaired_search_as_the_theorems_state_it`.
- Gate: PASS (1,345 MOSP tests, 110 pathwidth_solver tests).

### Blockers
- None. Not covered: 76–125 customers. Item 04's paired refutations are the
  record there. Differential outputs go to `paper2/data/solver_fix_diff*`, not
  over the committed `learning/data/ensemble/differential*`. Side note: the
  committed `differential.csv.gz` gives +2.5% refutation nodes at n ≤ 40
  against today's run, where item 04's paired measurement gives +0.004%. So that
  file comes from an older code state and must not be read as the repair's cost.

### Next
- Item 06: which certified values rested only on the customer search. Note
  that `learning/search_certificate.py` still models only the published rules.
