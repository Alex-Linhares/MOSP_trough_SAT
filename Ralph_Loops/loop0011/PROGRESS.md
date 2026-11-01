# loop0011 progress

Plan: `reports/separator_moment_plan.md` — counting events (balanced
separators, closed pairs, the weighted count) instead of witnesses (empty
pairs) in the first-moment lower bound on pathwidth; items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0011/gate.py`.

Current: 3/13 SOLVED

## Setup — 2026-11-01

- **Baseline.** Lean: zero `sorry`, zero `axiom` in code (loop0010 left it
  so; the gate's baseline is 0). Tests: 100 test modules (`tests/`), 1,656
  passed at the last gate of loop0010, pathwidth_solver 123. Paper:
  `paper1/latex/main.pdf` builds, 71 pages, Appendix E holds the first
  moment, the generator and the excess subsection; its paragraph "Why the
  first moment is loose" and the section's closing sentence are what item
  12 replaces.
- **Data on record** (nothing to re-solve): the pilot's 6,542 proved
  `G(n, c/n)` graphs with layouts (`reports/scratch/gnp_pilot/results.csv`,
  `n = 20–120`; at `n = 120` only `c ≤ 2` fully proved); 50,716 certified
  random covers in the four ensemble frames; 6,376 corpus instances;
  Harper values on 650 certified `(6, 1)` instances
  (`reports/scratch/structured_count/slack_6_1.csv`); the second-moment
  tables at `(6, 1)` (`second_moment_rate.csv`, `second_moment_125.csv`).
- **Six corrections to the brief, carried into the plan** (§0 of
  `reports/separator_moment_plan.md`): the measured clumping is across
  separators, not within one (§8.5 (a)'s extremal table exchanges `0.057 n`
  vertices with `S`), so the separator count merges only the component
  flips, estimated at `+0.004–0.010` in `β` at `c = 6–10`; the count on
  record has no sub-pairs (exact sizes); "no component larger than `N/2`"
  is a strict relaxation with a cheaper competing route (global thinning)
  at `c′ ≲ 5`, so the bipartition event is what is counted; the kill at
  `c = 6, 10` would miss the near-threshold gains and the threshold
  (`4 ln 2 → 2 ln 2`, conditional on the giant's lower tail), which are
  pre-registered separately; Kloks 1994 is held as a 2-page preview and
  Lee–Lee–Oum is not a first moment; the pilot's exact values at `n = 120`
  exist only for `c ≤ 2`.
- **Planner's estimates** (plan §0; predictions, never results): closed
  pairs `β = 0.1803 / 0.3453` at `c = 6 / 10` against `β* = 0.1706 / 0.3371`;
  the bracket on the inner rate at `c = 3` puts `β_sep(3)` in
  `[0.009, 0.056]` against a fitted slope of `0.099`.
- **Driver.** `loop.py` and `gate.py` are loop0010's with the loop number
  changed (the item regex passes whole items — 2-space continuation lines,
  no blank line inside an item); `knobs.json` unchanged (cap 4 h, fix cap
  45 min, 3 fix attempts, 16 iterations); `allowed_sorries.txt` empty.
- **Before launch.** The driver refuses to start while `git status` shows
  changes under `learning reports tests benchmarks satisfiability mosp
  customer_inter`; commit or stash first (on 2026-11-01 the only changes
  were loop0010's `loop.log` and `status.json`). Check that the owner's
  `run_unlimited.py` is not running (by PID), or leave it its cores.
  Launch as `Ralph_Loops/Ralph_Loop_Guide.md` "As practised here" says,
  with the API key from `~/.config/anthropic/api_key`; never a second
  driver on this folder.

---

## Iteration 1 — 2026-11-01 12:55

Item 01, the literature: who counts separators, and what the inner
probability is known to be. **Done.** Deliverable: `reports/separator_moment.md`
created (header with the three events and the notation; §1 with Table A
"who counts what", Table B "the rates", Table C "representative counts and
what they bought", the brief's paragraph, what items 05–08 take from it, the
corrections to the item, the verdict and the non-claims); five PDFs added to
`literature/` (Dembo–Montanari–Sen 2017, Andreis–König–Patterson 2021,
Puhalskii 2005, Díaz–Serna–Wormald 2003 TR, Lampis 2012); text extracts of
twenty papers in `reports/scratch/separator_moment/lit/`; a new section in
`literature/MISSING.md` for the five not obtained (O'Connell 1998,
Luczak–McDiarmid 2001, Bollobás 1988, the journal Díaz–Serna–Wormald 2007,
Kloks 1994's random-graph chapter); DOIs resolved through Crossref for every
paper cited.

### Completed

- **Stop rule: did not fire.** No held or fetched paper states a separator
  first moment for pathwidth or vertex separation of `G(n, c/n)` with an
  exact inner probability and a constant. Nearest: Do–Erde–Kang 2024 count
  separators `S` of a spanning tree's vertex set with the bipartitions per
  `S` bounded by `2^{Δ(T)|S|}` (a deterministic inner bound, used to reach
  the threshold `c = 1` with constant `Ω(ε³/log(1/ε))`); Kolesnik–Wormald
  2014 have the configuration-model-exact inner count for a single vertex
  cut with its vertex and edge boundaries ("best possible for a direct
  application of the first moment method"), no bipartition of the rest, no
  `G(n, c/n)`; the inner probability of the *relaxed* event is a corollary
  of the LDP for the largest component (O'Connell 1998 via Puhalskii 2005
  Cor. 2.4(3); Andreis–König–Patterson 2021 Cor. 1.3), used in no width
  first moment we found.
- **The rate the loop needs is cited, with the statement quoted**: the
  largest component of `G(N, c′/N)` satisfies an LDP at scale `N` with
  O'Connell's rate `I_{c′}^β`; `[0, ½]` is closed, so
  `P(no component > N/2) ≤ e^{−(I_{c′}^β(½) − o(1)) N}`, and (checked
  numerically on the quoted formula, `rate_check.log`) `I` vanishes at the
  typical giant and `I(½) > 0` iff `c′ > 2 ln 2`. The relaxed separator
  count's threshold is therefore `2 ln 2`, conditional only on the LDP as
  quoted. Values: `I(½) = 0.183, 0.595, 1.810` at `c′ = 3, 4.98, 10`.
- **Both routes the planner wrote down for the relaxed rate are the wrong
  route**: at `c = 6` the plan's bracket was `[0.552, 1.245]` with thinning
  at `1.19`; the LDP gives `0.595`.
- **Preview for item 06, from the quotation alone** (`rate_preview.log`,
  labelled, superseded by item 06): the relaxed separator count's constant
  `β_relax` exceeds `β*` by `+0.028, +0.021, +0.011, +0.004, +0.0007` at
  `c = 3, 4, 6, 10, 20`, and is positive at `c = 2, 2.5, 2.77` where `β* = 0`.
  Below the brief's kill at `c = 6, 10`, above it at `c ≤ 4`; inside the
  planner's bracket at `c = 3` and at the top of the planner's estimate at
  `c = 6–10`. The slope of the pair exponent at `β*` is `5.5, 3.9, 3.4, 3.3`
  per unit of `β` at `c = 3, 4, 6, 10`.
- **Representative counts in print bought 1.7% (Gao 2012's rigid
  partitions, treewidth threshold), 2–10% (Lampis 2012's locally optimal
  sets, edge expansion at Δ = 4–7) and 6–25% (Lichev–Mitsche 2023's
  structural count with an overcount division, cubic bisection) of the gap
  to the truth or to the best upper bound.** The brief's kill of 0.02 at
  `c = 6, 10` is 21–26% of the gap to the fitted slope, at the top of that
  record.
- **Corrections to the item**: Kolesnik–Wormald is arXiv 1311.6555 (the
  item's 1109.0689 is a paper on payment systems); Puhalskii is *Ann.
  Probab.*, not *SPA*; "Díaz–Serna–Wormald's locally optimal bisections"
  are a misattribution (DSW is a greedy upper bound; the locally optimal
  count is Lampis 2012, fetched); the held Kloks preview is chapter 12 on
  cocomparability graphs, with no random-graph content; Díaz–Diner–Serna–
  Serra is published (JCSS 2024).
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, tests 1,656 passed / 2 skipped / 1 xfailed in 4:07, pathwidth_solver 123 passed in 6:29, paper 71 pages with no undefined references).

### Blockers

None. Five papers not obtainable without a login (recorded in
`literature/MISSING.md`, each with the restatement it is cited through).

### Next

Item 02 (the deterministic lemmas): the three forms from
`exists_empty_pair_of_layout`, checked on every graph to 9 vertices before
any is called a lemma. Items 05–06 should compare their relaxed-event rate
against `I_{c′}^β(½)` of `rate_check.py` and not fit it to the planner's two
routes (`reports/separator_moment.md` §1.6); item 07 has no LDP to quote for
covers and must compute the giant's lower tail itself.

---

## Iteration 2 — 2026-11-01 13:10

Item 02, the deterministic lemmas: the balanced separator at exact sizes
(L1), the separator events `E_bip` ⊆ `E_relax` (L1′), the closed pair by
the alternating closure (L2), the MOSP forms (L3). **Done.** Deliverable:
`reports/separator_moment.md` §2 (statements, proofs with every step
named, the check's table, the Lean-ready list for item 10, regenerate /
size range / kill verdict / non-claims); `learning/separator_moment.py`
(forced sizes, the subset DP, exact-size pairs, components, `E_bip` /
`E_relax`, the closure, closed-pair enumeration, the cover forms);
`reports/scratch/separator_moment/02_lemmas/{check.py, check.log,
summary.csv, x3_vs_x3prime.py, x3_vs_x3prime.log}`;
`tests/test_separator_moment.py` (21 tests: every labelled graph to 6
vertices, the DP pinned to `vertex_separation_brute` and
`compute_pathwidth`, the `3K₂` example, the two closure orders, covers).

### Completed

- **Kill criterion: not met.** Every graph on 1–9 vertices (288,266),
  20,000 random `G(n, p)` at 10–12 and 2,000 random covers at 4–10
  customers: **310,266 graphs, 4,027,298 closures, zero violations** of
  L1, L1′, L2 or L3 at `k = pw` (113 s on 4 workers at nice 19; the load
  was above 24). The loop's premise stands.
- **The closure stops after one round, not after an iteration.** The
  item expected `A ⊆ A₁ ⊆ A₂ ⊆ …`; the Galois step gives
  `R₁ = V ∖ N[A]`, `A₁ = V ∖ N[R₁]` and then `R₂ = R₁`, `A₂ = A₁` (L2 iii,
  proved from `A ⊆ A₁ ⟹ N[A] ⊆ N[A₁]`). Monotonicity holds as asserted,
  with equality from the second step; checked at every step on every
  closure. A correction to the item's expectation, not a counterexample.
- **The fixpoint is a representative, not canonical**: the `A`-first and
  `R`-first closures differ on 7–10% of exact-size pairs at 7–9 vertices,
  10–14% on the random graphs, 3% on covers. The union bound needs only a
  map, and L2 gives one.
- **`E_bip` and "an exact-size pair exists" are the same event** (L1′ c);
  `X₁` and `X₂` count it differently (`X₁ ≥ X₂` always). `E_relax` is
  strictly weaker — `3K₂` with `k = 0` is the first 6-vertex example in
  geng order — but adds separators at `k = pw` on only 0.3–8% of graphs
  at these sizes (growing with `n` and density).
- **The closure's image `X₃′` is a proper subset of all closed pairs
  `X₃`** on 2.8% of graphs at 7, 1.8% at 8, 0.9% of random graphs at
  10–12 (§2.3 remark iv); both are valid first moments, item 03 measures
  both.
- **The necessary condition's slack is visible at nine vertices**: at
  `k = pw − 1` the structures still exist on 39–46% of graphs at 7–9
  vertices and 27% of the covers (`E_relax` within 0.6 points of L1).
- Seventeen Lean-ready statements listed for item 10 with hypotheses,
  conclusions and the existing lemma each rests on; the one obstacle
  named (components of an induced subgraph as `Finset`s, for the
  component form of `E_bip`; the pair form is cheap and is what item 08
  needs).
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,677 passed / 2 skipped / 1 xfailed in 15:01 under a load of 20–60, the 21 new tests among them; pathwidth_solver 123 passed in 7:05; paper builds with no undefined references).

### Blockers

None.

### Next

Item 03 (the clumping decomposed): `X₁`, `X₂`, `X₃`, `X₄` on graphs with
exact pathwidth at 14–24 and certified covers at `n ≤ 22`, using
`learning.separator_moment` (`exact_pairs`, `count_separators`,
`closed_pairs`, `close_pair`) — note that `closed_pairs` enumerates all
`2^n` subsets and `count_separators` all `C(n, k)` sets, fine to 24 and
not beyond, and that `X₃` and `X₃′` differ (§2.3 remark iv): report
both. Item 10 takes §2.6's list.

Note for items 05–07 and 12: the owner appended a note to `TASK.md` during
this session (Edwards & McDermid 2015 as the published upper line in the `β`
figure and the cover grid; Cheung & Girardet 2020's prefix-at-`(1 − ε)n`
variant; the disputed random-cubic bisection constant, not to be quoted
without the source). It does not touch item 02.

---

## Iteration 3 — 2026-11-01 13:53

Item 03, the clumping decomposed: exact-size empty pairs `X₁`, distinct
separators `X₂`, closed pairs `X₃` (and the closure image `X₃′`) and
move-classes `X₄` on instances with exact pathwidth. **Done.** Deliverable:
`reports/separator_moment.md` §3 (the events counted, the instance table,
the counts at `k = pw`, the rate table with standard errors, the Bernoulli
second moment beside them, the overlap distribution with its figure, the
kill verdict, regenerate / size range / non-claims);
`learning/separator_moment.py` extended (`small_nbhd_sets`,
`enumerate_empty_pairs`, `separators_of`, `closed_pairs_pruned`,
`closure_image`, `move_classes`, `overlap_tables`, `second_moment_rate_gnp`,
`second_moment_exact_gnp`, `second_moment_enum_gnp`, `gnp_masks`);
`reports/scratch/separator_moment/03_clumping/` (`run.py` with stages
`solve`, `count`, `rates`, `overlap`; `instances.csv` with every seed and
every layout of the 4,800 fresh graphs; `counts.csv` at
`k = pw − 1 … pw + 2`; `cells.csv`, `slopes.csv`, `second_moment_gnp.csv`,
`rates.log`; `overlap_*.csv`, `overlap.log`, `overlap_hist.png`;
`checks.py` / `checks.log`); `tests/test_separator_moment.py` (16 new
tests, 37 in the module).

### Completed

- **Instances.** 4,800 fresh `G(n, c/n)` at `n = 14–24`, `c = 4, 6, 8, 10`
  (200 per cell), every one proved by the C program in 7 s of wall time
  with the layout kept, the subset DP agreeing on all 1,600 at `n ≤ 16`;
  the pilot's 548 `n = 20` graphs and 1,200 certified covers
  (`n = 10–25`, `d = 4, 6`, `m = n`) read from the record. The counts took
  66 s on 8 workers (516 s of enumeration; about 0.15 core-hours against
  3 budgeted); no cap was hit.
- **Kill criterion 1: met.** At `c = 10`, `k = pw`, the slope of
  `log(X₁/X₂)` is `0.000 ± 0.003` and of `log(X₁/X₃)` is `−0.003 ± 0.003`
  nats per vertex against the `0.066` a `0.02` gain in `β` needs —
  twenty standard errors below. **Prediction recorded: the separator and
  closed-pair counts fail item 06's kill**; by this instrument each merges
  at most `0.01` nats per vertex, `0.003` in `β`. Items 05–06 are kept
  (the prediction is at `k = pw` on typical instances, not at `β*`), item
  09 is the route the item points to.
- **Kill criterion 2: not met.** `X₁/X₄` does not grow (`−0.003 ± 0.004`
  at `c = 10`); the move-classes merge a factor 1.4–2.5, flat in `n`.
  The `e^{0.23 n}` of §8.5 is not the typical cluster; item 04's planted
  model is where the rare-instance cluster must be measured.
- **What a typical instance looks like at its own pathwidth** (`n ≤ 24`):
  8–62 exact-size pairs (geometric mean), growing at `0.09–0.13` nats per
  vertex (fitted); one separator carries one pair and its reverse — with
  `N` odd `X₁/X₂ = 1.08, 1.14, 1.23, 1.57` at `c = 10, 8, 6, 4` and
  `1.03–1.09` on covers, with `N` even `2.0–2.4`; the closure merges
  1.3–1.6 (graphs) and 1.7–3.3 (covers); **`X₃′ = X₃` on every fresh and
  pilot graph at `k = pw`** (99.8% of covers), separating only at `pw + 2`
  (27–40% of instances). At `k = pw − 1`, 43–74% of graphs have no
  exact-size pair at all.
- **The Bernoulli second moment** (`second_moment_rate_gnp`, exact finite
  form checked against the enumeration of pairs of pairs at `n = 8, 10`,
  the sup against a `61⁴` grid): at `β*` it reproduces §8.5 (a) on
  `G(n, c/n)` — ratio exponent `0.39, 0.37, 0.34, 0.30` at `c = 4, 6, 8,
  10`, maximiser the same or the reversed pair — while at the typical `β`
  of the cells the maximiser is the symmetric table and the exponent is
  `0.02–0.16`. The two regimes have different maximisers, which is why
  this item cannot stand in for item 04.
- **The overlap at `n = 20`, `c = 10`** (20 graphs, 23,412 ordered pairs
  of distinct pairs): two pairs share `0.45 n` of their separators (80%
  of `S`) against `0.35 n` for the extremal table at this `a` and `0.32 n`
  for the product; `A′` meets `A` and `R` equally (medians one vertex
  each); `A ∩ S′` below both reference tables. Pairs on an instance are
  small perturbations of each other through `S`, not the reversed pair.
- **Corrections to the item.** "One vertex changed class" cannot happen at
  exact sizes, so the move-class adjacency is one swap between two classes
  (stated as "labellings differing on at most two vertices"); the direct
  closed-pair enumeration at `n ≤ 16` and the pruned one agree on all 2,200
  rows, and the pruned one is what runs at `n > 16`; `X₃` and `X₃′` turned
  out to coincide at `k = pw` on every graph, so the "report both" of item
  02 is one number there.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,693 passed / 2 skipped / 1 xfailed in 4:17, the 16 new tests among them; pathwidth_solver 123 passed in 6:23; paper 71 pages, no undefined references). A first gate run, started while the one-minute load was 60, hung in the pathwidth_solver suite (65 min at full CPU after the load had fallen to 1, no child process); a verbose copy of that suite run beside it passed in 6:28, the hung run was stopped by PID and the gate rerun from the start under load 1 — the PASS above is that rerun.

### Blockers

None. The one-minute load rose from 1 to 60 during the session (the
owner's other work); the counts had finished by then and only the gate
ran under it.

### Next

Item 04 (the planted cluster): condition on an empty pair and count the
other exact-size pairs — this item says the typical regime has small
clusters and the large-deviation regime has a different maximising
overlap, so the planted measurement is the one that decides whether the
`e^{0.23 n}` is a cluster or a rare-instance artefact. Reuse
`enumerate_empty_pairs`, `move_classes`, `overlap_tables` and
`second_moment_rate_gnp` (whose extremal table at `β*` is the reversed
pair on `G(n, c/n)`, `checks.log`). Items 05–06 carry the prediction of
§3.5 and decide it.
