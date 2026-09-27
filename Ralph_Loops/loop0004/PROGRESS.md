# Progress Log

## Ralph Loop 0004 Status
- **Started**: 2026-09-27
- **Target**: 13 items
- **Current**: 1/13 SOLVED

---

## Iteration 1 — 2026-09-27 16:58

### Completed
- **Item 01 · Q6a, the rule as the DFS seed over the whole corpus — SOLVED.**
  `reports/ml_nature.md` §28; tables in `reports/rule_seed_tables.md`.
- Registered `rule` and `rule+cs-dfs` in `satisfiability/heuristics.py`
  (`two_key_closing_order`, popcount form of `learning.distil.HYPOTHESES`'s
  two-key rule; agrees with it on 400 random instances). Default of nothing:
  `DEFAULT_STRATEGY` is still `mcn+tabu`, `customer_search.solve` still `cs-dfs`.
- `learning/rule_seed.py`: trains five fold models grouped by file ∪ isomorphism
  class (`learning/models/union/`), sweeps five strategies with
  `learning.corpus_sweep` (new `--model-dir`), times every strategy in-process,
  writes the tables. Whole run ~12 min on 16 workers beside 9 recertify workers.
- Result over 6,376 (9–134 customers): `rule+cs-dfs` exact 94.2% / mean 0.092 /
  worst +8 / 16.7 ms; `learned+cs-dfs` (union folds) 92.1% / 0.128 / +8 / 20.6 ms;
  `cs-dfs` 84.5% / 0.241 / +10 / 29.5 ms. Head to head: rule seed 780 better /
  12 worse than `cs-dfs` (learned: 709/13 with file folds, 602/19 with the honest
  folds); rule seed 263 better / 80 worse than the learned seed. Leads in every
  size band and every collection. **The LightGBM dependency question no longer
  exists**: the learned seed is dominated by a model-free strategy of the same
  cost class. Proposed, not applied: `rule+cs-dfs` wherever `cs-dfs` is used.
- Side finding: file-grouped folds leaked; the union grouping puts all Chu &
  Stuckey, Faggioli–Bentivoglio, SCOOP, Challenge, Wilson and Shaw files in one
  fold trained on Harvey/Simonis only, and about a seventh of the 2026-09-22
  learned gain disappears under it.
- Tests: `tests/test_rule_seed.py` (11) — chain, 4-cycle tie-break direction,
  distil equivalence, Becceneri–Yanasse–Soma 2004 Table 1 (printed sequence = 4
  = optimum, all strategies reach 4), sweep ledger row into a temp ledger and
  temp solutions dir, union fold assignment, table arithmetic. Full suite:
  1,083 passed, 2 skipped, 1 xfailed in 83 s. `solutions/` untouched.

### Blockers
- None. Milliseconds were measured on a loaded machine (9 recertify + 16 sweep
  workers): absolute values ~1.5× `reports/learning.md`'s, ratios are the claim.

### Next
- Item 02 · Q6b: the 2004 arc-traversal Minimal Cost Node heuristic from its
  pseudocode; the Table 1 instance is already transcribed in
  `tests/test_rule_seed.py` (`BYS2004`, printed sequence, ξ′ = 4 = optimum).
