# Progress Log

## Ralph Loop 0003 Status
- **Started**: 2026-09-26 10:23
- **Target**: 14 items
- **Current**: 1/14 SOLVED

---

## Iteration 1 — 2026-09-26 10:48

**Item 01 · §2.1(a) The differential harness** — SOLVED, with a finding the
plan expected not to make.

### Completed
- `learning/differential.py`: for every certified instance, the identity, 8
  seeded relabellings and one re-covering (`graph_story` primitives), each
  decided at `optimum − 1` and `optimum` under both `node_counts`
  configurations, the `sat` side's closing order simulated; disagreements,
  contradictions and lattice-oracle mismatches kept apart; every node count
  recorded. Stages: `run`, `tables`, `drawn` (re-certifies flagged instances
  by routes independent of the C `better_move` and classifies which rule
  pairing each false answer needs).
- The run: 43,935 instances (campaign 37,800 at 10–40; corpus 6,135 at 9–40),
  878,700 runs, 1,757,280 decision calls, 199 s on 16 workers. Zero
  disagreements at `optimum − 1` (878,580 of 878,580 `unsat`), zero `unknown`,
  zero witness failures, zero oracle mismatches on 13,612 instances.
- **56 disagreements at `k = optimum`** (46 campaign, 10 corpus), 88 false
  `unsat` answers, all under the `csearch` configuration (Theorem 2 on). All
  56 stored optima re-certified independently (Python reference, C default,
  cached solve, lattice oracle on 11): the values are right, the rule is
  wrong. Mechanism: the C `better_move` composed with `subset_rule` (78 of
  88) or `definite_move` (3 of 88) forms a cross-rule dominance cycle;
  `better_move` alone is sound on all 88. Traced at the root of
  `ens_f_n10_m20_d2_i070`; flag sweeps on two instances; minimal 10×13 and
  17×9 sub-instances. Fix proposed in §15, **not applied**.
- Relabelling spread by size band and configuration, refutation and witness
  sides (item 04's input): at n ≤ 40 min-of-9 beats the identity by ≥ 1.5× on
  under 0.1% of instances under `default` for refutations, 16–17% for witness
  searches at 36–40.
- Re-covering invariants of §13 confirmed on all 43,935: default node counts
  equal on every pair at both k; csearch differences only inside
  `better_move` flips.
- `reports/ml_nature.md` §15; `reports/differential_tables.md`;
  `learning/data/ensemble/differential.csv.gz` (5.5 MB), `differential_summary.csv`,
  `differential_drawn.csv`, `differential_drawn_rules.csv` (11 MB total).
- `tests/test_differential.py`: 11 tests pass, including the planted liar
  (one relabelling lies at the optimum; the harness names it) and a liar at
  `optimum − 1`; one strict `xfail` pins the C failure on the drawn instance
  and will XPASS-fail when the C is fixed. Full suite: 824 passed, 2 skipped,
  2 xfailed in 79 s.

### Blockers
- None for the item. **Alert for the owner, outside this item's scope:**
  `benchmarks.recertify --days 5` is running now (12 workers) with
  `better_move=True, better_move_dominators=0`, the configuration shown here
  to answer `unsat` to satisfiable questions on 0.3% of sparse instances at
  10–40 customers. Its 125×125 re-certifications ask only `decide(value − 1)`
  and cannot be checked by the `default` search at that size. Not stopped:
  not this item's process. The 147 corpus values `csearch` certified rest on
  the same rule. Whether any is wrong is open; the n ≤ 40 corpus and campaign
  are shown unaffected.
- No solver default or C code changed. The fix (`subset_rule` before
  `better_move`, or dominance measured only against standing candidates; same
  for `definite_move`) is proposed in §15 for the owner.

### Next
- Item 02 · §2.2 the campaign upward (n ∈ {50, 60, 75}, m ∈ {n/2, n, 2n};
  n = 100 on the ridge, priced by §14's law). Item 04 should include the
  `sat` side in its portfolio measurement: at n ≤ 40 that is where labels
  move the count. Every item that runs `csearch`-configured refutations
  should record `decide(optimum)` beside them until the C is fixed.
