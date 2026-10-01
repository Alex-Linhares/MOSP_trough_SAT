# loop0007 — fix both solvers to match the theorems: items

- [x] **01 The repaired rules in the Python reference.** In
  `satisfiability/customer_search.py`, behind `repaired_rules: bool`
  (default `False` for now): the hereditary definite test by matching, run
  only for candidates that pass `close ≥ open`, and the repaired better move.
  Tests: on every graph in `paper2/search_check.py`'s small sets, the
  repaired filter is node-sound against the oracle; on `DEFINITE_CEX` the
  repaired filter no longer keeps 0 alone; with `repaired_rules=False`
  nothing changes, node for node, against today's behaviour.

- [x] **02 The repaired rules in the C.** In `customer_search.c` and
  `native.py`, the same flag. The matching is small: write it directly, for
  example by augmenting paths over at most 128 customers. Tests: C equals
  Python node for node under both settings, on the inputs
  `tests/test_native.py` uses and on `DEFINITE_CEX` and the Bug B instances.

- [x] **03 The pathwidth solver.** The same change in
  `pathwidth_solver/pathwidth/` (`search.py`, `closing_search.c`,
  `closing_search_w.c` for every WORDS, `native.py`). Tests: its identity
  tests against MOSP still pass under both settings, and multiword equals
  legacy equals Python node for node. **Then make `repaired_rules=True` the
  default in both solvers** (the owner's decision), and record it at the top
  of `paper2/solver_fix.md`.

- [x] **04 What the repair costs.** Paired runs, old against repaired, in
  nodes and seconds:
  - the corpus at n ≤ 40, refuting optimum − 1;
  - the Chu & Stuckey classes at 50-100;
  - a sample of the 125 × 125 instances under a budget;
  - the pathwidth benchmarks: VSPLIB, coloring, named, and a Rome sample.
  How often does the old test pass but the matching fail, so the rule no
  longer fires? Report the overhead.

- [ ] **05 Soundness of the fixed solver.** Run `paper2/search_check.py`'s
  whole-search checks against the production code with the repaired rules
  (the port must still equal the C node for node). Run
  `learning.differential` on a sample at n ≤ 40 and 50-75, and the gadget
  family from `paper2/definite_hunt_gen.py`, at 12-17. Expect zero
  node-level losses and zero disagreements. Re-run
  `python -m benchmarks.corpus` and confirm no certified value changed.

- [ ] **06 Which certified values rested only on the customer search.**
  From the records (compute ledger, sweep CSVs, recertify results, DRAT
  coverage in `learning/data/proofs/`, the lattice oracle at n ≤ 15), list
  every corpus instance whose optimality certificate is a customer-search
  refutation and has no independent proof (SAT, DRAT, lattice). Write the
  list as a CSV with the instance, the value, the configuration that
  certified it, and its size.

- [ ] **07 Re-check them, cheapest first.** For each instance on item 06's
  list, run the old-code refutation of `value − 1` with the certificate
  emitter, and check `CodeNodeRepaired` at every node
  (`Search/Decide.lean`: the definite pick is hereditarily definite, and
  every better-move drop has a repaired citation). A pass makes the old
  refutation sound by `codeExec_mospValue_of_repaired`. For a fail, or where
  emitting is too big, re-refute `value − 1` with the repaired solver. Price
  first with the cost model; budget per instance; the 125 × 125 ridge
  instances may not fit, so mark them censored. Write the results as a CSV
  and a table. Never touch `solutions/`.

- [ ] **08 The pathwidth benchmarks under the repaired rules.** Rerun
  `pathwidth_solver/bench/run.py` on VSPLIB, coloring, named and Rome, at the
  same caps as before, with the repaired default. Compare every proved width
  with the old results; any change is a finding. Fix the two result-file
  issues in `pathwidth_solver/TRANSFER.md` on the way: proof `budget` means
  unproved, and the name must be the path.

- [ ] **09 Documents.** Update `paper2/revised_algorithm.md` §4.4.4 and §4.6
  ("what holds for the code": it now matches the theorem), and the summary
  and "Known Limitations" paragraphs that a later owner edit to `CLAUDE.md`
  will need: put the proposed text in `paper2/solver_fix.md` §"For CLAUDE.md".
  Do not edit `CLAUDE.md` yourself.

- [ ] **10 Reserve.** The best remaining gap from items 04-08, one session.
