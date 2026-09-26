# Progress Log

## Ralph Loop 0003 Status
- **Started**: 2026-09-26 10:23
- **Target**: 14 items
- **Current**: 8/14 SOLVED

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

## Iteration 4 — 2026-09-26 15:15

**Item 04 · §2.4 The relabelling portfolio** — SOLVED. **Kill criterion met,
by a wide margin**: median min-of-8 refutation speed-up at n ≥ 60 is 1.003
(804 instances) and 1.009 on the 389 whose identity refutation costs ≥ 10⁴
nodes; the spread shrinks with n rather than growing. The race produced an
unplanned finding: today's `better_move` fix costs ≥ 15× nodes on the one
ridge instance at n = 100 where both sides are on record.

### Completed
- `learning/relabel_portfolio.py`: identity + 16 seeded relabellings per
  instance, `decide(optimum − 1)` and `decide(optimum)` under `csearch`,
  one pool job per (instance, labelling); exact E[min-of-k] by order
  statistics; speed-ups against the identity and the median labelling,
  core efficiency; growth fit; six cheap labelling statistics plus the
  witness count as predictors; `--stage race` (16 labellings on 16 cores,
  losers terminated at the first refutation, `--no-early-stop` to run all);
  projection from `recertify/results.json` and §16's predictions.
- The study: 1,572 instances (8 per cell from 171 campaign cells at
  n ∈ {40, 50, 60, 75}; 204 corpus instances at 50–100, the ten
  `Random-100-100-2/4` excluded as unaffordable), 53,448 decision calls,
  5.95 core-hours, 22 min on 16 workers. Audit free: 26,697 `unsat` + 27
  censored at optimum − 1, 26,724 `sat` with valid witnesses at the optimum,
  no value contradicted.
- **Refutation**: max/min over 16 labellings median 1.00–1.05, p90 1.11–1.26
  in every band; min-of-16 vs identity median 1.00–1.02; widest spread in
  the study 2.14×; core efficiency of a 16-way portfolio 0.063. Same 288
  n = 40 instances and nine labellings as item 01: p90 spread 1.21 before
  the fix, 1.12 after. Seconds spread on the loaded machine 1.49× median
  against 1.05× in nodes — the clock alone would have passed the kill.
- **Witness search**: spread grows with n (p90 max/min 7 → 542 from 40 to
  75); where it is hard (≥ 10⁴ nodes, 67 of 360 at n = 75) min-of-16 saves
  8–13× at core efficiency 0.5–0.8; but it is 183 nodes against 27,900 for
  the refutation at n = 75, so a portfolio on it removes 2–5% of a descent
  pair's cost. No cheap statistic predicts a labelling's cost (|ρ| < 0.35).
- **Race** (10.5 core-hours against 8 budgeted; the overrun is the fourth
  instance run all sixteen ways to the deadline): `Random-100-100-2-4_0`,
  §14 identity 93.1 M nodes / 37 s pre-fix — today's identity ≥ 1.39 G nodes
  at 600 s unfinished, 3 of 16 labellings finished (630 M–1.25 G), spread
  ≥ 2.9×, portfolio wall ≥ 2.1× the identity's at 16× the cores. The three
  §14-censored instances: 0 of 48 labellings finished in 600 s; counts at
  the deadline span 1.5–1.6× (rate, not size).
- **The fix's cost at scale** (§18 (e)): post/pre ratio on the identity
  where Theorem 2 is on — 1.00 (p90 1.09) at n = 40; medians 1.06–1.07
  (p90 1.37–1.55, max 34) in the m = n/2 cells at 50–75; 1.19–1.27 on
  `Random-50/75-*-2`; 2.3× and 3.5× on `Random-100-50-2/4`; ≥ 15× on
  `Random-100-100-2-4`. Dense classes and every `default` count unchanged.
  `results.csv`, `scale_nodes.csv`, the recertify counts and 71 of 135
  `results_upward.csv` cells are pre-fix `csearch` counts.
- `reports/ml_nature.md` §18 (a)–(f); `reports/portfolio_tables.md`;
  `learning/data/ensemble/portfolio.csv.gz` (1.1 MB), `portfolio_race.csv`,
  two logs; ensemble directory 69 MB apparent.
- `tests/test_relabel_portfolio.py`: 8 tests (order statistics against
  brute force, statistics on the spider, seeded labellings, status
  invariance under relabelling, both-sides job row, per-instance speed-ups
  with a censored maximum kept as a lower bound, table and kill verdict on
  a toy, a two-way race with append-not-rewrite). Full suite: 908 passed,
  2 skipped, 1 xfailed in 86 s. No solver default, flag or C changed;
  nothing written to `solutions/`.

### Blockers
- None for the item. Deliverables as asked: speed-up curve (§18 (a), flat),
  projection for the 125 × 125 ridge (§18 (f): the identity's own wall
  clock; pre-fix 25–28 h per `-2` instance), recommendation stated and not
  applied (no relabelling portfolio in `recertify`; the satisfiable side is
  where labels pay).
- **Alerts for the owner, outside this item** (restating iteration 1's with
  new evidence): the `benchmarks.recertify` run started 2026-09-24 still has
  three 125 × 125 entries open on the pre-fix C, and its five completed
  re-certifications rest on the rule `reports/better_move_bug.md` §7 shows
  unsound (bug A within the rule). Under the fixed C the same refutations
  need more nodes by a factor that is ≥ 15 on the one n = 100 ridge instance
  measured both ways, so re-running them will take longer than 25–53 h each
  by an amount nobody has measured. The §14/§16 `csearch` rate constants are
  pre-fix.
- Process notes for the driver: one job per (instance, labelling) kept
  stragglers short; the first progress flush at 500 calls was 17 min of
  silence on the heaviest cells — flush earlier; the study's 120 s deadline
  censored only 27 calls on 3 instances.

### Next
- Item 05 · §2.3 predicting cost: the noise floor is MAD log10 0.004–0.007
  on refutations (§18 (a)); **every `csearch` count must be dated** — train
  on one version's counts only (post-fix: `portfolio.csv.gz` identity rows,
  1,572 instances at 40–100; the `default` counts are unaffected everywhere
  and are the safer target).
- Item 07 · §2.5b Theorem 2's switch: the fixed rule's saving is smaller
  than §13–§16 measured (pre-fix); re-measure `csearch` vs `default` on the
  fixed C before fitting the boundary.
- A satisfiable-side portfolio (ratchet, `restricted_dfs` seeds, `k ≥ optimum`
  descent calls) is the one place labels pay; not in this loop's items.

## Iteration 5 — 2026-09-26 15:30

**Item 05 · §2.3 Predicting cost** — SOLVED. **Kill criterion not met** for the
chosen model: 87.8% of the 98 `default` counts and 89.3% of the 103 pre-fix
`csearch` counts at 100–125 fall within one decade (settled counts alone 87.4%
/ 88.2%); the linear Tobit alone fails at 73.5% / 73.8%, §11's cell law at
57.5% / 65.4%, §14's surface at 61.2% / 59.2%.

### Completed
- `learning/cost_model.py`: assembles every refutation count on record
  (campaign 37,800 at 10–40, upward 6,785 at 50–100 with the finish stage
  merged, corpus 6,135 at ≤ 40 + `scale_nodes.csv` at 50–125 + the five
  recertify counts) with label-free graph features and file ∪ isomorphism-class
  groups; a hand-written **Tobit** (censored Gaussian regression in log space,
  analytic gradient, L-BFGS; neither `lifelines` nor `scikit-survival` is
  installed) on a linear, extrapolable design in `n × {density, m/n, opt/n,
  degree, dispersion, treewidth, degeneracy, components, clustering}` plus
  §16's drift (`n²`, `n²·x`); an optional LightGBM correction of the residual
  on scale-free features only; model selection by fit ≤ 60 → score 75 (test
  sizes untouched); baselines §11 cell law and §14 surface as published; error
  by band; the decade claim with censored counts as lower bounds; the noise
  floor from `portfolio.csv.gz` and `differential.csv.gz`; the recertify table
  with a censored lower bound for the three entries still running (63.3 h at
  the finished entries' 0.74 µs/node → ≥ 10^11.49 nodes); a post-fix check
  labelled as such. Runs in 11 s.
- **Dating the upward run** (`date_upward_csearch`): in all 70 upward cells
  where Theorem 2 is on, §18's post-fix identity counts differ from the run's
  on at least one of the eight shared instances (0 of 70 match), so the whole
  §16 run is pre-fix and its `csearch` counts train the `csearch` model. §18
  (e)'s "71 of 135 cells" is the number of cells where the distinction
  matters, not of post-fix cells.
- **Findings** (`reports/ml_nature.md` §19, tables `reports/cost_model_tables.md`):
  in-range MAE 0.09 / 0.09 / 0.14 / 0.20 decades at 10–20 / 21–40 / 50–60 /
  75 (five-fold grouped CV); at 100 MAE 0.54, bias +0.43, p90 1.07; at 125
  MAE 0.38, bias +0.38, p90 0.59, 15 of 15 within a decade (`default`), 20 of
  20 (`csearch`, incl. the five recertify counts). The drift term and the
  residual GBM are each worth ~0.1 MAE at the first size beyond the fit; the
  noise floor over relabellings (sd 0.003–0.017) is 30–100× below the error.
  **The one class missed** is the generated 100-customer `d = 2` cell (96%
  decomposable): over-predicted by a decade, 14 of 25; without it the
  100-band is 57 of 58 / 58 of 58. Every corpus class at 100 and 125 is
  within a decade. **Recertify**: the five finished entries predicted to MAE
  0.38 / bias +0.38 (over: 29–93 h predicted at 0.55 µs vs 10–53 spent),
  Spearman 0.4 on the order (the `default` linear model 0.8, MAE 0.13; the
  §11 law −0.3, ranking the `-2` class below the `-4`). **Cheapest-first for
  what remains: `Random-125-125-2-5_0`, `2-3_0`, `2-2_0`** (11.15 / 11.34 /
  11.85 log10 nodes; 22 / 33 / 107 h at 0.55 µs); the first two have already
  run past their predictions (≥ 11.49 after 63.3 h) and remain within a
  decade; `2-2_0` is predicted the most expensive of the eight by every model.
- `learning/data/ensemble/cost_model_predictions.csv` (201 test rows, 26 KB),
  `cost_model_recertify.csv`; ensemble directory 69 MB apparent.
- `tests/test_cost_model.py`: 9 tests — Tobit recovers a slope least squares
  gets wrong under 30%+ censoring and equals OLS without censoring; the
  decade rule on censored lower bounds; per-band evaluation; the model
  extrapolates an exact exponential 40 customers beyond its fit; the noise
  floor on a toy; the recertify table's ranking, hours and open-entry bound;
  the dating verdicts on toy cells. Full suite: 917 passed, 2 skipped,
  1 xfailed in 79 s.

### Blockers
- None. Deliverables as asked: error by size band, the decade claim at
  100–125 (kill not met), predicted vs actual on the recertify entries, the
  cheapest-first order for the withdrawn three. Not built: a per-component
  model (the fix for the decomposable-cell miss).
- Caveats carried into §19: the 125 claim rests on 15–20 counts (5 on the
  ridge); 21 of 201 test counts are censored lower bounds and the `default`
  model sits below 7 of its 11; **every prediction is for the pre-fix
  `csearch`** — post-fix ridge counts at 100 are ≥ 15× larger (§18) and the
  model has never seen one at 125.
- Process note: `pgrep -f benchmarks.recertify` matched this session's own
  `claude -p` process (the item text is in its command line); anchor on
  `^python -m benchmarks.recertify`.

### Next
- Item 06 · §2.5(a) fan order. Paired node counts behind a flag; the noise
  floor for such pairs is sd 0.003–0.017 decades (§19), so a 5% effect is
  resolvable per instance.
- Item 07 · §2.5(b) Theorem 2's switch: re-measure on the fixed C first (§18
  (e)); §19's dating method (compare with a run of known version) tells
  pre-fix from post-fix counts wherever both exist.
- For the owner: the cost model orders the recertify queue `2-5_0, 2-3_0,
  2-2_0` and prices `2-2_0` at 4–6 more days on the pre-fix rule; a
  per-component predictor would fix the one class it misses.

## Iteration 6 — 2026-09-26 16:23

**Item 06 · §2.5a Fan order** — SOLVED. **Kill criterion met, for both
configurations**: the paired median node change of the refutation is 0.0% at
every size from 10 to 100 customers (p10–p90 within [0.992, 1.008]); the fan
order does not matter for refutations. The witness search and `cs-dfs` are
where it shows, in aggregate and two-sided; proposed for satisfiable-side
drivers only, not applied.

### Completed
- **The flag.** `fan_order="index" | "degree"` on `customer_search.decide`
  (Python and C) and `heuristics.restricted_dfs` (registered as
  `cs-dfs+degree`); `heuristics.fan_sort_key` is the one definition both use
  (cost, then most neighbours not yet closed, then index — §7's two-key rule
  as a fan order). Defaults unchanged. The C adds `cs_decide_fan` and keeps
  `cs_decide` with its old signature, because the running
  `benchmarks.recertify` forks workers late and its in-memory `argtypes` are
  the old ones; `native._build` now compiles to a scratch name and renames
  into place so a mapped library keeps its inode. Recertify's nine processes
  were the same before and after the rebuild.
- **`learning/fan_order.py`**: item 01's protocol on every certified
  campaign instance at 10–75 (44,547) and corpus instance at 9–100 (6,349):
  `decide(optimum − 1)` and `decide(optimum)` × both configurations × both
  fan orders, witnesses simulated, plus `restricted_dfs` under both orders;
  default arm compared node for node with every recorded count. 407,168
  decision calls, 101,792 DFS runs, 9.25 core-hours, 35 min on 16 workers.
- **Audit**: zero status disagreements between fan orders (50,845 / 50,849
  refutation pairs, 50,894 / 50,894 witness pairs), zero contradictions, all
  203,576 witnesses within the optimum; the default arm equals the recorded
  `nodes_default` on 50,756 of 50,756 (30 of them at the six significant
  digits `results_upward.csv` stored), §15's identity counts on 43,935 of
  43,935, §18's post-fix `csearch` identities on 1,572 of 1,572, and
  `ub_cs_dfs` on 44,547 of 44,547. The default path is byte-for-byte
  unchanged over the whole study.
- **Findings** (`reports/ml_nature.md` §20, tables `reports/fan_order_tables.md`):
  refutation median ratio 1.000 in every band, geometric mean 1.000, widest
  ratios 0.66–1.12 at n ≥ 50, class-deduplicated medians 1.000 at every n,
  no per-node cost in seconds; the *fraction of refutations whose count
  changes at all* rises from 0.1% at n = 10 to 74% at 75 and cancels. Witness
  search: median 1.000 but geometric mean 0.81 at 75 and total nodes 0.65 at
  75 / 0.87 at 99–100; on hard searches (≥ 10⁴ nodes) 301 fewer / 162 more at
  75, total 0.64, p10 0.055, p90 1.06; gain on the ridge cells (total
  0.43–0.62), neutral-to-worse on dense `m = n/2`. Worth 1.7% of a descent's
  nodes at 75 (§18 (b) bound). `cs-dfs`: exact 70.0% → 70.1%, total
  overshoot −1.3%, corpus 99–100 MAE 3.21 → 2.95 and worst 10 → 8, 50% slower
  in the Python (the sort-key lambda); §7's `cs-dfs+rule` gain came from the
  seed, not the fan order.
- `learning/data/ensemble/fan_order.csv.gz` (2.0 MB, one wide row per
  instance), `fan_order_run.log`; ensemble directory 71 MB apparent.
- `tests/test_fan_order.py`: 10 tests — the sort key on a hand-built star,
  the flag reaching the Python fan through the `branch` hook, rejection of an
  unknown order, no-flag ≡ `"index"` in status/nodes/witness (Python and C),
  status invariance at every k under both configurations, C ≡ Python under
  the flag node for node (and not a no-op), the default reproducing eight
  recorded campaign counts and `ub_cs_dfs` values byte for byte, the DFS
  still a bound and registered, `measure`/tables/kill verdict on a toy. Full
  suite: 939 passed, 2 skipped, 1 xfailed in 80 s.

### Blockers
- None. Deliverables as asked: the paired distribution by size and density
  (§20 (a), (b), tables), a proposed default stated and not applied (keep
  `index` for `decide`; `degree` for satisfiable-side drivers only;
  `cs-dfs+degree` registered, not default), the harness check that the flag
  never changes a status.
- Process notes: a C-vs-Python *order* comparison must be made on the active
  customers — the C lists product-less customers as free moves, the Python
  omits them (pre-existing, not a bug); a recorded count is only as exact as
  its CSV (`results_upward.csv` has six significant digits); running the
  heaviest instances first meant no progress line for 11 minutes.

### Next
- Item 07 · §2.5b Theorem 2's switch. This run's `nodes_lo_default_*` and
  `nodes_lo_csearch_*` columns are 50,896 paired post-fix counts under both
  configurations on the identity labelling — the boundary can be fitted from
  `fan_order.csv.gz` alone before any new run; §18 (e) says the pre-fix
  `results*.csv` `csearch` counts must not be mixed in.
- For the owner: if a satisfiable-side driver is ever tuned, `fan_order=
  "degree"` is a measured 35% at 75 with a 1.1–1.3× p90 tail; the `cs-dfs`
  route to a stronger bound is the rule as seed (§7), not the fan order.

## Iteration 7 — 2026-09-26 17:06:34
### Completed
- (driver) session ended with outcome `ok` without marking the item
- (owner, 17:15) The session finished the study and the tests (946 passed) and
  committed `learning/theorem2.py`, `tests/test_theorem2.py` and a 40-instance
  smoke-test `reports/theorem2_tables.md` (c98f0477), then ended its turn
  waiting on one 125 × 125 straggler — the failure mode TASK.md warns about.
  **No §21 was written.** Its full run (50,911 instances, 203,644 decision
  calls, 4.4 core-hours) was still alive as `python -m learning.theorem2
  --workers 16` (PID 661367) at 17:15, appending to
  `learning/data/theorem2_partial.csv`; if it has finished, its output is the
  data for the section; if the straggler is a ridge 125 × 125 refutation it
  may never finish and should be censored. Item 07 has been re-opened
  (`- [ ]`) so it is redone after item 08: read `session_it07.log`, reuse the
  committed code and the partial/full CSV, regenerate the tables with
  `--stage tables`, and write §21. Do not re-run the whole study.
### Blockers
- see session_it07.log
### Next
- re-opened; see above

---

## Iteration 8 — 2026-09-26 17:57

**Item 08 · §2.7 Extremal search and exact treewidth** — SOLVED. **Kill
criterion not met** for four of the five objectives: a bit-flip search with
the exact solver as oracle beats the corpus's worst instance at the same size
on `gap` (2 vs 1 at 14–15), `pw − tw` (2 vs 0–1 at 10 and 13–18), refutation
nodes (3–12× at every n with a corpus instance) and `cs-dfs` overshoot (4 vs 2
at 15); met for `disagree` (zero in 25,583 adversarial evaluations and in all
727,816 evaluations that computed it).

### Completed
- `learning/treewidth.c` + `learning/treewidth.py`: exact treewidth two ways
  — the O(2ⁿ · n · poly) subset DP (Bodlaender et al.) to n = 26 (5 × 5 grid
  in 2.2 s), and a decision search "tw ≤ k?" over elimination prefixes with
  simplicial / almost-simplicial reductions, an MMD cut and a failure memo, to
  n = 64 under a node budget and deadline (a censored run is an interval).
  Every answer carries an elimination ordering re-checked by
  `elimination_width`; a Python reference of the recurrence is in the tests.
- `learning/extremal.py`: the oracle evaluation (optimum, four component
  bounds, exact tw, both configurations at `optimum − 1` and `optimum`,
  `cs-dfs`), hill climbing over bit flips with nauty canonical dedupe and a
  fewer-edges tie-break, three seed families (trees of cliques, Bernoulli,
  subsets of §6's ten), stages `corpus` / `search` / `tables`, re-certification
  of every draw (solver, both refutations, lattice oracle at n ≤ 15, pathwidth
  DP at n ≤ 18, clique + ordering for tw), and a proof block per `pw − tw`
  instance.
- **The corpus pass** (167 s on 8 workers): exact treewidth on 4,335 of 4,443
  instances — all 4,122 at n ≤ 20, 212 of 234 gap ≥ 2 instances at 27–50 by
  the decision search. **§6's 38.8% floor is now an interval**: `pw > tw` on
  164 of 338 gap ≥ 2 instances (48.5%), `pw = tw` on 80 (23.7%), 94 open (82
  above 64 customers, 12 censored). Corpus max `pw − tw`: 1 to n = 18, 2 at
  19–40, 3 at 50 (`p2050n9_0`).
- **The search** (1,431 jobs, 727,816 oracle evaluations, 30.2 M duplicates
  skipped, 2.73 core-hours): the object is a **10-vertex, 21-edge graph with
  pathwidth 5 and treewidth 3** — three K4s glued pairwise at three hub
  vertices plus a tenth vertex joined to one non-hub vertex of each —
  vertex- and edge-minimal for `pw − tw = 2` (all 10 vertex deletions and 21
  edge deletions evaluated exactly), proved by a K4, an elimination ordering,
  two refutations, the pathwidth DP and the lattice oracle. Half the size of
  the corpus's smallest (19) and of the smallest tree (22). `pw − tw` grows
  with n but slowly (1 at 7, 2 at 10, 3 not below 50 on record); 3 was not
  reached at n ≤ 20. Every one of the 48 drawn instances re-certifies.
- `reports/ml_nature.md` §21; `reports/extremal_tables.md` (all tables,
  drawings, proofs); `learning/data/ensemble/extremal_*.csv[.gz]` (1.4 MB;
  ensemble directory 74 MB apparent). Generated witnesses under the
  git-ignored `learning/data/extremal/solutions/`.
- `tests/test_extremal.py`: 22 tests — DP against known values and a Python
  reference, min-fill and MMD as bounds, decision search against the DP on
  random graphs, censoring is not an answer, the spider (tw 1, pw 2) through
  `evaluate` and `recertify`, certificate invariance, seeds, a planted
  objective the search must climb with no matrix evaluated twice, kill and
  growth tables, the corpus job by DP and by decision search, the n > 64
  fallback. Full suite: 968 passed, 2 skipped, 1 xfailed in 82 s.

### Blockers
- None for the item. Not done, stated in §21: exhausting the 274,668
  9-vertex graphs to make the 10-vertex record a theorem (~1 core-hour);
  128-bit masks for the 82 open gap ≥ 2 instances above 64 customers.
- Process notes: the C pendant-vertex shortcut first skipped `degree > k`
  (caught by a `decide(tw − 1)` test); duplicate proposals must not count as
  steps; a `pgrep -f` pattern naming an output file matches the shell that
  names it. `learning/data/ensemble/theorem2*` and `reports/theorem2_tables.md`
  are modified/untracked from iteration 7 and were not touched here.

### Next
- Item 09 · §2.6 conjecture mining: `learning.extremal.local_search` takes any
  callable objective and is the adversary the plan asks for; the family to
  target is cliques glued pairwise at hubs (§21 (b)), which defeats every
  degree bound and the min-fill ceiling alike. `learning.treewidth` gives
  exact tw for candidate invariants at n ≤ 26.
- Item 12 (Lean): the 10-vertex graph is a concrete instance for any
  `pathwidth > treewidth` statement.


## Iteration 9 — 2026-09-26 18:20

**Item 07 · §2.5b Theorem 2's switch** — SOLVED (re-opened from iteration 7,
whose run finished but whose section was never written). **Kill criterion
not met**: the learned boundary is "always on" and agrees with the hand
threshold on 41.2% of instances (0 hand-on/learned-off, 29,920
hand-off/learned-on). The nodes say always on; the clock says the hand
threshold at 5 is in the right place. **Recommendation: no change to
`sparse_enough_for_better_move`.**

### Completed
- **Nothing re-run.** Iteration 7's `python -m learning.theorem2 --workers 16`
  had completed at 17:25 (the straggler `Random-125-125-6-5_0` took 3,203 s
  for its four calls): 50,911 instances (campaign 44,547 at 10–75; corpus
  6,349 at 9–100 plus the fifteen dense 125 × 125 with settled `default`
  refutations), 203,632 decision calls, 5.3 core-hours, about an hour on 16
  workers. The committed `theorem2.csv.gz` (swept into iteration 8's commit)
  is the complete run; every number in §22 regenerates from it in 6 s with
  `--stage tables`.
- `learning/theorem2.py`: a `corpus 101–125` size band (the fifteen 125 × 125
  rows were being folded into `fan_order`'s band named for 99–100),
  `hand_threshold_sweep(metric="seconds")` so the clock sweep quoted in the
  section is a regenerated table, the section number. Tables regenerated:
  `reports/theorem2_tables.md`, `learning/data/ensemble/theorem2_tree.txt`
  (the committed tables predated the clock analysis the module already
  carried).
- **Audit, all clean**: 0 status disagreements on 50,861 refutation and
  50,909 witness pairs, 0 contradictions, 0 of 101,818 witnesses above the
  optimum; off arm equals every recorded `default` count (50,772 / 50,772;
  item 06's 50,843 / 50,843), on arm equals item 06's post-fix `csearch`
  count wherever the hand rule was on (20,938 / 20,938). The new information
  is the on arm on the 29,920 instances the hand rule leaves off, where
  Theorem 2 had never run.
- **Findings** (`reports/ml_nature.md` §22): (a) in nodes, where the hand
  rule is off, forced on saves on 8,810, ties on 21,109 and costs on **one**
  (405 → 410); total saving 6.6%, 3–7% by size from 50 up, 100% of the
  125 × 125 refutations change and all fifteen save (median 0.933 on `-6`).
  Where it is on, post-fix saving 27% total / 8% median, 174 costs (0.8%),
  none heavy, worst 1.27×, 0.001% of the study's nodes; no cost above 7
  products per customer in 22,205 pairs. Always on is the node oracle to
  four decimals; the hand threshold leaves 4% (1.07 at 100–125). (b) The
  depth-3 tree is all-on: agreement 41.2%, the same with `n` and on decided
  pairs; kill not met. (c) On the 1,146 heavy refutations (≥ 10⁵ off-nodes,
  50–125 customers), Theorem 2 costs **1.167× per node** (p10 1.10, p90
  1.23, flat in `n`), break-even node ratio 0.857; where the hand rule is
  off, on is slower on 347 of 350 (1.13× median, 1.05× total); the seconds
  sweep is flat at regret 1.025–1.029 for thresholds 4.5–6 and rises to 1.06
  at 6.5 and for always on, which is *slower than always off* in seconds; a
  tree fitted to the seconds sign agrees with the hand rule on 48% and only
  ever turns it off where the hand has it on. (d) Witness search: total 0.83
  but 1,253 costs, max 184×; not where the switch matters.
- Proposed and not applied: always on if nodes are the currency; keep 5 if
  seconds are (recertify's five-day budgets); the threshold should rise only
  if the C's per-node overhead falls below ~1.03.
- `tests/test_theorem2.py`: 9 tests (two new: the 125 band, the seconds
  sweep by hand). Full suite: 970 passed, 2 skipped, 1 xfailed in 82 s.
  Nothing written to `solutions/`; no solver default, flag or C changed.

### Blockers
- None for the item. Not covered: the 125 × 125 `-2` and `-4` classes (the
  hand rule is on there; `default` censors at 1,500 s), stated in §22.
- Process notes: iteration 7 ended its turn with the run alive and its
  draft body at `/tmp/it07/body.md` carrying `xx` placeholders — the
  driver's commit after iteration 8 swept the finished data in, which is
  why this iteration had nothing to run; heaviest-first left one 125 × 125
  instance running alone for 35 of ~60 minutes.

### Next
- Item 09 · §2.6 conjecture mining (`learning.extremal.local_search` as the
  adversary, cliques glued at hubs as the target family).
- For the owner: the C `better_move` pass is the lever — its 17% per-node
  overhead is what keeps the hand threshold at 5; cheaper by a factor of six
  and always on wins the clock everywhere measured.
