# Progress Log

## Ralph Loop 0003 Status
- **Started**: 2026-09-26 10:23
- **Target**: 14 items
- **Current**: 3/14 SOLVED

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

## Iteration 2 — 2026-09-26 12:20

**Item 02 · §2.2 The campaign upward** — SOLVED, with the kill criterion met
for the 100-customer cells and the sample run for the price check.

### Completed
- `learning/ensemble.py`: `--upward` (n ∈ {50, 60, 75} × m ∈ {n//2, n, 2n},
  fixed d 2..10 and Bernoulli p 0.025..0.2, 50 per cell, 135 cells; plus
  n = 100 at m = n, d ∈ {2, 3, 4}), `price_ridge100` (the §11 cell laws price
  the 25-per-cell n = 100 run at **40 core-hours against the cap of 8**, so
  the kill applies and the sample flag `--ridge100-sample 5` ran instead),
  per-cell counts in `run`, separate `results_upward.csv` / `manifest_upward.csv`
  so §10–§15 regenerate unchanged.
- `learning/upward.py`: censoring-aware cell medians, local rates with
  bootstrap bands, per-series and pooled drift of the rate with n, global
  fits by window, ridge location, Theorem 2 by ratio, drift-corrected
  extrapolation to 100 and 125, the n = 100 instance table, the corpus
  classes; a finish stage that decides `value − 1` for descents that ran out,
  writing to its own CSV (merged on load, never rewriting the run's file).
- The run: 6,785 instances, 11.1 core-hours, 50 min wall on 16 workers, in
  two parts (stopped by PID at the slow n = 75, m = 2n cells and resumed
  with 240/90 s budgets for the last 665 rows); the n = 100 sample and its
  finish stage a further 9.6 core-hours. 6,773 certified, every witness
  re-simulates, no certified value contradicted by either configuration;
  manifest regenerates (400 sampled, 0 mismatches).
- **Findings** (`reports/ml_nature.md` §16): the exponential form holds to
  75 in every series and to 100 where there is data; **the rate falls with n
  by 0.000217 ± 0.000045 log10 per customer per customer** (18 of 18 series,
  pooled t = −4.8), which is exactly the 0.005–0.018 discrepancy §14 found
  between the 15–40 campaign rates and the 30–125 corpus rates — fitted at
  50–100 the campaign reproduces the corpus's rates to 0.005. Drift-corrected
  extrapolation from the 75 cells predicts the two `Random-125-125-2` counts
  on record to 0.04 decades (11.18 vs 11.21, 11.22 log10 nodes) with a band
  of ±0.8 decades; the revised 125 × 125 prediction is 1.5 × 10¹¹ nodes
  (2.5 × 10¹⁰ – 9 × 10¹¹) for density 2 and 4 × 10¹⁰ (1.8 × 10¹⁰ – 1.1 × 10¹¹)
  for density 4. The ridge stays at d = 3 (m = n) and d = 2 (m = 2n) through
  75 and sits at d = 5–6 for m = n/2, where Theorem 2's switch is on for
  87–95% of instances and saves the same 15% at the median as elsewhere.
  At n = 100 on the ridge 9 of 10 descents ran out at 900 s (10^9.1–9.3
  nodes), two of the values reached were **not optimal** (`sat` at value − 1
  under both configurations), and the rest censored at 1,500 s: the price
  was right.
- `tests/test_upward.py`: 6 tests (the grid, the price as a closed form, an
  exact exponential recovered with zero drift, censored medians flagged as
  lower bounds, per-cell counts in `run`, the finish stage certifying a row
  without rewriting the run's file). Full suite: 830 passed, 2 skipped,
  2 xfailed in 118 s.
- Data committed under `learning/data/ensemble/` (68 MB apparent in total):
  `results_upward.csv` (3.2 MB), `manifest_upward.csv`,
  `results_upward_finish.csv`, the three run logs, and 6,785 witnesses under
  `solutions/`. `reports/upward_tables.md`, `reports/upward_ensemble_tables.md`.

### Blockers
- None for the item. The deliverable's error band comes from the 75-customer
  cells rather than the 100-customer cells the item asked for, because the
  100-customer ridge cells did not certify inside any budget the session
  could afford (an hour per instance); stated in §16 (d)–(e) and under the
  kill criterion.
- Process notes for the driver: a `kill $(pgrep -f '<pattern>')` matched the
  issuing shell (exit 144); anchor patterns. Cores briefly exceeded 16
  (campaign 16 + finish stage 10) for ~11 minutes on a machine with 8 idle
  cores; recertify's 4 active workers were not displaced.

### Next
- Item 03 · §2.3 runtime prediction: the drift (rate = f(n)) is a feature the
  cell law lacked; the n = 100 censored counts are lower bounds, not missing.
- Item 04 · §2.4 relabelling portfolio: the ten n = 100 ridge instances in
  `results_upward.csv` (uncertified, values known to be within one of the
  optimum for two of them) are the natural test set beside the corpus's
  `Random-100-100-2`.
- Item 05 · §2.5 Theorem 2: §16 (b) shows the switch is on for nearly every
  m = n/2 instance and saves ~15% wherever it is on; the boundary question
  is whether it ever costs at m ≥ n.

## Iteration 3 — 2026-09-26 13:55

**Item 03 · §2.1(b) DRAT proofs at n ≤ 40** — SOLVED. Kill criterion not met:
drat-trim builds, pysat's CaDiCaL proofs check once flushed, and 92.0% of the
corpus at n ≤ 40 now carries a third-party-checkable refutation.

### Completed
- `tools/drat-trim/`: Marijn Heule's checker vendored at commit `2e3b2dc`
  (2024-11-25, `.git` removed, 7 MB of example proofs dropped; `tools/README.md`).
  Upstream's `-std=c99` fails on this glibc (`getc_unlocked`); built with
  `gcc drat-trim.c -std=gnu99 -O2`. Binary git-ignored.
- `learning/proofs.py`: for every certified corpus instance at n ≤ 40, the
  two `decide_mosp` reductions (decomposition, pattern dominance) recorded as
  index lists, `encode_mosp_decision` at `optimum − 1`, CaDiCaL 1.9.5 with
  `with_proof=True` under a **conflict budget** (the reproducible censoring)
  in a child process the worker kills at a wall deadline (the safety net),
  binary DRAT checked by drat-trim, proof gzip-compressed under
  `learning/data/proofs/` (git-ignored, 11.7 GB) with a JSON certificate; one
  row per instance in the committed `learning/data/proofs.csv` (instance, k,
  preprocessing, CNF size and SHA-256, proof SHA-256, size, lemma count,
  conflicts, solve and check seconds, verdict, budget). Stages `run`
  (resumable, largest first, `--wall`, `--retry-timeouts`), `tables`, `check`
  (rebuilds the CNF from the certificate's indices and the benchmark file
  without `mosp.preprocess`, re-runs drat-trim), `backfill`, `one`.
- **Two pysat facts, each costing part of the session** (recorded in §17 and
  the module docstring): `Solver.interrupt()` raises `NotImplementedError`
  for CaDiCaL, so a timer cannot stop a solve — the first batch's 90 s
  "deadline" let one instance run 372 s; and `Solver.get_proof()` returns a
  **truncated** proof for CaDiCaL (a C stdio buffer pysat never flushes), so
  drat-trim says "no conflict" even on PHP(5); `libc.fflush(NULL)` before
  reading the trace file gives the complete proof.
- The run: pass 1, all 6,135 at 200,000 conflicts (5,325 checked, 810
  censored; 3.0 core-hours, 15.5 min wall on 16 workers); pass 2, the 810
  again at 1,000,000 (321 more; 10.0 core-hours, 39.4 min wall). **5,646 of
  6,135 checked (92.0%)**: 99.4% / 97.1% / 80.0% / 77.7% by band ≤10 /
  11–20 / 21–30 / 31–40. Zero `not_verified`, zero `sat`, zero wall kills;
  the 489 left all exhausted a million conflicts (median 54 s).
- **Findings** (`reports/ml_nature.md` §17, tables in `reports/proof_tables.md`):
  affordability is decided by the formula, `m² · k`, not by `n` — censoring
  0 of 4,062 below 5,000, 4% / 25% / 69% in the next three decades; every
  instance with m ≤ 20 patterns certified at any k (0 of 4,775); the first
  failures at 200k are at n = 10 (`wbo_10_30`, m = 30); at 1M only one of
  the 25 `Random-40-40` instances (k = 6) certifies, the k 9–12 ones having
  needed 1.3–1.9 M lemmas in the unbudgeted first batch. The SAT proof costs
  6,000–70,000× the customer search's seconds on the same questions: an
  archive object, not a decision procedure. At m = 125 the boundary is
  crossed at k = 1.
- `tests/test_proofs.py`: 7 tests — the 4-customer (C4) proof checks and
  re-checks from the certificate alone, four corruptions fail (half the
  proof, the empty proof, a flipped literal, the proof against a satisfiable
  formula), a false claim is `sat` with no proof, a decomposed instance
  records its refuted component and rebuilds its CNF hash, the lemma counter
  on hand-built binary DRAT, `summarise` on a toy frame, `backfill`. Full
  suite: 900 passed, 2 skipped, 1 xfailed in 78 s.
- `.gitignore`: `learning/data/proofs/`, `!learning/data/proofs.csv`,
  `!learning/data/proofs_200k.csv`, the built tool binaries.

### Blockers
- None. Not attempted: the 241 corpus instances above 40 customers (out of
  the item's scope; §17 says why the encoding cannot reach 125 × 125).
- The proofs replace trust in CaDiCaL and in the search's dominance rules;
  they do not replace trust in `encode_mosp_decision` or in the two
  reductions, which stay as trusted code (§17, "What the certificate does
  and does not cover"). That gap is item 12's.
- Process notes for the driver: `pgrep -f "<pattern>"` inside a polling
  loop matches the loop's own shell when the pattern appears in its command
  line — use a bracket trick (`ru[n]`); the first batch was stopped by
  process group after its deadline proved unenforced, and its 7 rows
  discarded.

### Next
- Item 04 · §2.4 relabelling portfolio. §15's spread tables are its input;
  the `sat` side moves most with labels at n ≤ 40.
- For item 12 (Lean): the statement worth having is that `encode_mosp_decision`
  is satisfiable iff MOSP ≤ k — with it, §17's 5,646 proofs become
  end-to-end certificates.
- If the owner wants the 489 censored instances proved: another factor of
  five in conflicts would buy perhaps 150 for ~40 core-hours on the observed
  curve; the 295 Harvey/Simonis 30 × 30 at k 21–30 are the bulk and the
  least responsive.
