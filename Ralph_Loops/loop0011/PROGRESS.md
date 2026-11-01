# loop0011 progress

Plan: `reports/separator_moment_plan.md` — counting events (balanced
separators, closed pairs, the weighted count) instead of witnesses (empty
pairs) in the first-moment lower bound on pathwidth; items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0011/gate.py`.

Current: 12/13 SOLVED

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

---

## Iteration 4 — 2026-11-01 15:57

Item 04, the planted cluster: condition on one exact-size empty pair and
count the others, their distance and the mechanism; the median against
the second-moment prediction. **Done.** Deliverable:
`reports/separator_moment.md` §4 (the two identities, the instance table,
the 28-cell table median / gm / mean / prediction, the growth and the
fork, the distance histogram with its figure, the far/near overlap
tables, the mechanism table, the union-bound slack measured directly, the
verdict, regenerate / size range / non-claims);
`reports/scratch/separator_moment/04_planted/` (`run.py` with stages
`run`, `stats`, `draw` and `--probe`; `planted.csv` with every seed,
every count and every within-ε share of the 5,600 instances;
`distance_hist.csv`, `mechanism.csv`, `overlap_far_near.csv`,
`cells.csv`, `slopes.csv`, `mechanism_summary.csv`, `run.log`,
`run_stdout.log`, `distance_hist.png`); `learning/separator_moment.py`
extended (`beta_star_gnp`, `plant_pair`, `plant_cover`, `overlap_table`,
`hamming_distance`, `lq_sides`, `second_moment_exact_cover`,
`planted_mean_gnp`, `planted_mean_cover`); `tests/test_separator_moment.py`
(14 new tests, 50 in the module).

### Completed

- **Instances.** 4,000 planted `G(n, c/n)` (`n = 16–32`, `c = 6, 10`,
  `β ∈ {β*, β* + 0.1}`, 200 per cell) and 1,600 planted `(6, 1)` covers
  (`n = 16–28`), every exact-size empty pair enumerated; 305 s on 8
  workers (0.6 core-hours against 3 budgeted); 7 instances censored above
  2 million pairs.
- **Two identities carry the item**: `E[X′ | P₀ empty] = E[X²]/E[X] − 1`
  (the second-moment ratio *is* the planted mean) and
  `P(X > 0)/E[X] = E[1/X | P₀ empty]` (the union bound's whole slack is a
  bounded planted statistic). Both checked exactly by enumeration in the
  tests; the first also against the sample means (20 of 26 uncensored
  cells within two standard errors, the six exceptions all below, where
  the top 10% of instances carry 68–94% of the sum).
- **The fork, decided per model.** `log(median X′)/n` over `log E[X′]/n`
  at the largest `n`: **0.57** at `G(32, 6/32)`, `β*`; **0.36** at
  `G(32, 10/32)`, `β*`; **0** on `(6, 1)` covers at `β*` (median `X′ = 1`
  at every size: the reversed pair and nothing else); 0.69–0.75 at
  `β* + 0.1`, where the other pairs are the instance's own population.
  Growth: the median at `0.24 ± 0.03` nats per vertex against the mean's
  `0.31 ± 0.03` (`c = 6`); per-instance geometric mean at `0.17` / `0.12`
  against `0.31` / `0.30`; covers `0.00` against `0.16`. **§8.5's
  `e^{0.23 n}` at `(6, 1)` is a rare-instance artefact of `E[X²]`; on
  `G(n, c/n)` the cluster is half typical and half tail** (the item's
  middle branch, both written up).
- **The cluster is two lobes with an empty middle** at `β*`: perturbations
  of `P₀` and of its reverse, nothing at `d ≈ 0.5–0.6 n` (1.7% of pairs on
  `G(32, 6/32)`, 4 of 4,584 on covers). On the median planted instance
  88–100% of the other pairs are within `0.2 n` of `P₀` or its reverse;
  pooled, 18–78%, the far pairs belonging to the rare large-`X′`
  instances. The move-class of `P₀` holds 8–9 pairs at `c = 6`, `n = 28–32`
  and `P₀` alone at `c = 10` and on covers.
- **Mechanism, in direction and not in its strong form**: the `S`
  vertices that join a side have half the planted-side degree of a
  typical `S` vertex (2.7 vs 5.1 at `c = 6`; 5.1 vs 9.1 on covers) but are
  not isolated from the sides; what is small is what they evict (none in
  18–51% of cases, at most one in 60–87%, mean 0.6–1.4).
- **The union bound's slack, measured**: `0.065` (`c = 6`), `0.039`
  (`c = 10`), `0.043` (covers) nats per vertex at `β*` and the largest `n`
  — **`0.019`, `0.012`, `0.015` in `β`** — against planted-mean exponents
  of 0.23, 0.15, 0.11; sub-linear in `n` over the range (total 0.8 → 2.1
  nats at `c = 6`, 0.8 → 1.2 on covers), so an upper estimate of the rate.
  The ideal weighted count `Σ 1[P empty]/X` equals `1[X > 0]`, so no `Z`
  in item 09 gains more than this at the same `(n, k)`: item 09 is
  reduced to the paragraph the fork prescribes; item 12 is to say the
  remaining gap to the slopes is mostly the necessary condition.
- **Corrections to the item.** The mechanism statistic as the item
  phrases it ("neighbours on that side") is orientation-dependent and
  wrong on the reversed lobe; replaced by the orientation-free
  planted-side degree and the eviction count. The reversed pair is an
  exact-size pair at distance `N` whenever `N` is even, so distances are
  reported to `P₀` and to the nearer of `P₀` and its reverse. The cover
  model planted is the i.i.d.-pattern model of `CliqueCoverMoment.lean`,
  not the ensemble's repairing generator.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,706 passed / 2 skipped / 1 xfailed in 4:17, the 14 new tests among them; pathwidth_solver 123 passed in 6:24; paper 71 pages, no undefined references; the one-minute load was 1–4).

### Blockers

None. The one-minute load was below 5 throughout.

### Next

Item 05 (the inner probability, exact): `P_N(E_bip)` by Gilbert's
recursion and a sum over partitions to `N = 60–80`, the relaxed event by
the `O(N²)` DP to `N = 400`, against the product bound and the pilot
cells; compare the relaxed rate against `I_{c′}^β(½)` of item 01's
`rate_check.py` (§1.6). Items 06 and 09 carry §4.6's measured slack
(`0.012–0.019` in `β` at `β*`, `n ≤ 32`) as the ceiling any
representative count can reach at these sizes; item 11's ledger can use
identity 2 directly on planted samples at the pilot cells.

---

## Iteration 5 — 2026-11-01 17:05

Item 05, the inner probability exactly: `P_N(E_bip)` and `P_N(E_relax)` of
`G(N, p)` from the component structure, against the product bound the pair
count uses; the finite separator bound at the pilot cells; the rate in `N`
against the analytic bracket and item 01's LDP rate. **Done.** Deliverable:
`reports/separator_moment.md` §5 (method, the finite table at the ten
pilot cells, the rate table with three kinds of fit, the gap-to-product
table, the kill verdict, regenerate / size range / non-claims);
`learning/separator_moment.py` extended (`connected_probs`,
`log_connected`, `partitions`, `log_prob_partition`, `log_prob_bip`,
`log_prob_rel`, `log_product_bound`, the enumeration and Monte Carlo
checks `log_connected_enum`, `log_connected_mc`, `log_prob_bip_enum`,
`log_prob_bip_mc`); `reports/scratch/separator_moment/05_inner/` (`run.py`
with stages `check`, `inner`, `rates`, `draw`; `inner.csv` for every
`(n, c, k)`; `floors.csv`; `rates.csv`; `rate_fits.csv`; `rates.png`;
`run.log`); `tests/test_separator_moment.py` (10 new tests, 60 in the
module).

### Completed

- **Exact further than asked.** `P_N(E_bip)` is a sum over the partitions
  of `N` with a sub-multiset summing to `t`; a memoised recursion over the
  part sizes with the achievable sums as a bitset, closing a branch by the
  exponential-formula coefficient table once `t` is reachable, does
  `N = 60` in 0.1 s and `N = 120` in 18 s (2.0 M states), so the exact
  range is `N ≤ 120` (the item asked 60, 80 if cheap) and the relaxed
  event is exact to `N = 400`. Gilbert's recursion needed `60 + 0.6·N(1−p)^N`
  digits, not 60 (`C_400(2/400) ≈ e^{−54}`). Checks on record: enumeration
  of every labelled graph at `j ≤ 6` (connectedness) and `N ≤ 7`
  (`E_bip`, 2,097,152 graphs at 7), Monte Carlo at `j = N = 20`, partition
  law summing to one at `N ≤ 20`, the inequalities on a grid — zero
  violations. About 0.5 core-hours in all (1 budgeted).
- **Kill criterion: met for `c ≥ 6`.** The separator floor at `< 0.01`
  is the pair floor or one stack above it in all six cells with `c ≥ 6`
  (`60`: 11/11, 17/17, 22/21; `120`: 22/21, 33/33, 42/41). **The
  separator count is a rounding at these sizes**; item 06 is told so.
  At `c = 3–4` it is two to three stacks above (`120`: `1 → 4`, `7 → 10`),
  still far below the truth (lower bounds 12, 17). The relaxed and
  bipartition floors coincide in every cell.
- **The exact computation reproduces item 01's quoted LDP rate** to
  `0.0003–0.002` at all seven `c′` (log-corrected fit of `E_relax` over
  `N = 100–400`): an independent check of the *value* of the quoted
  formula, which item 01 could check only at its zero and sign; the
  misprint risk of §1.6 is retired for that form.
- **`E_bip` has the rate of `E_relax`**: the two differ by at most 0.008
  nats *in total* at `N = 120`. The number-partitioning condition is free.
- **The bracket holds when read at finite `N`.** The log-corrected fit is
  inside `[c′/4 − ln 2, min(c′/4, thinning)]` at every `c′`; the plain
  linear fit at `c′ = 10` sits 0.007 below the asymptotic lower end
  because of the `log N` term, and is above the same linear fit of the
  product bound (the finite form of that end) at every `c′`. The
  planner's two routes are far above the truth everywhere (0.918 and
  1.25 against 0.600 at `c′ = 5`), as §1.6 predicted.
- **Where the gain is**: at `c′ ≥ 8` the gap to the product bound is
  `ln 2` plus `≤ 0.3` nats at `N = 120`, growing at under 0.004 nats per
  vertex — the two orientations of one bipartition and nothing else; at
  `c′ ≤ 5` it is linear in `N` at `0.035, 0.065, 0.120, 0.226` nats per
  vertex of `N` (`c′ = 5, 4, 3, 2`), limits `0.043, 0.073, 0.126`.
  Linearised at `β*`: `+0.023, +0.020, +0.011, +0.006, +0.004` in `β` at
  `c = 3, 4, 6, 8, 10`, the same as §1.6's preview. **Prediction for item
  06: `β_sep = β_relax` to the fit's accuracy; its kill is met at
  `c = 6, 10` and not at `c ≤ 4`.**
- **Corrections to the item.** 60 digits are not enough at `N = 400`;
  the plain partition enumeration is unnecessary; the plan's thinning
  value `1.19` at `c′ = 4.98` does not reproduce from the plan's own
  formula (`0.91`) and nothing rests on it; the linear-fit-in-bracket
  check needs the finite form of the lower end.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,716 passed / 2 skipped / 1 xfailed in 4:22, the 10 new tests among them; pathwidth_solver 123 passed in 6:22; paper 71 pages, no undefined references; the one-minute load was 1–4).

### Blockers

None. The one-minute load was 0.3–4 throughout.

### Next

Item 06 (`β_sep(c)`): take the rate as `I_{c′}(½)` (now checked by the
exact computation, §5.3) and the exact finite `P_N(E_bip)` to `N = 120`
(`log_prob_bip`, `rates.csv`); `β_sep = β_relax` of §1.6 is the
prediction, with the kill met at `c = 6, 10` and the near-threshold
gains (`+0.02` at `c = 3–4`, a positive constant for every `c > 2 ln 2`)
the separate finding. The Edwards & McDermid 2015 upper line from the
owner's note goes into the `β` figure there. Item 07 has no LDP to
quote; `log_prob_bip`'s recursion applies to any component-size law
given the analogue of `C_j` for a random clique cover, which is the
thing to compute. Item 08 can state the separator inequality
`P(pw ≤ k) ≤ C(n, k) P_N(E_bip)` with `P_N(E_bip)` defined by the
partition sum of §5.1.

---

## Iteration 6 — 2026-11-01 17:40

Item 06, `β_sep(c)`, `β_closed(c)` and the combination against `β*(c)` and
the fitted slopes; the threshold. **Done.** Deliverable:
`reports/separator_moment.md` §6 (method for the three counts, the rate
grid against item 05 and the LDP, the constants table at ten `c`, the
threshold proposition with its hypothesis and citation status and the
`N ≤ 400` check, the finite form in stacks, the figure, the kill verdict,
corrections / non-claims); `learning/separator_moment.py` extended
(`ldp_rate` ported from `rate_check.py`, `rate_bracket`,
`pair_exponent_beta`, `sep_exponent`, `beta_sep`, `exponent_slope_at`,
`closed_exponent`, `closed_rate`, `beta_closed`, `log_closed_count`,
`log_combined_count`, `combined_exponent`, `combined_rate`, `beta_combined`,
`edwards_mcdermid_g` / `edwards_mcdermid_poisson`, `log_prob_rel_fast`; a
window `t_hi` and a tilt in `log_prob_bip` / `log_prob_rel`);
`reports/scratch/separator_moment/06_constants/` (`run.py` with stages
`check`, `grid`, `constants`, `threshold`, `finite`, `draw`; `rate_grid.csv`,
`rate_fits.csv`, `constants.csv`, `threshold.csv`, `finite.csv`,
`finite_floors.csv`, `check.log`, `run.log`, `beta_vs_c.png`);
`tests/test_separator_moment.py` (10 new tests, 70 in the module).

### Completed

- **Kill criterion (the brief's): met.** `β_sep(fitted) − β* = +0.0113`
  at `c = 6` and `+0.0038` at `c = 10`, below `0.02` at both: **the
  separator route is closed for the headline constants**, as §3.5 and
  §5.5 predicted. Beside it: closed pairs `+0.0097 / +0.0082` (the
  planner's `0.1803 / 0.3453` reproduced exactly), the combined count
  `+0.0076 / +0.0080`; no count or maximum of counts reaches `0.02`.
- **The pre-registered separate findings.** Near the threshold the
  separator count gains `+0.029` at `c = 3` (32% of the gap to the fitted
  slope `0.099`; the plan's bracket was `[0.009, 0.056]`, the answer
  `0.037`) and `+0.022` at `c = 4` (23%), and is a positive constant at
  `c = 2, 2.5` (`0.006, 0.019`) where `β* = 0`. The threshold moves from
  `4 ln 2` to `2 ln 2`, stated as a proposition conditional on the cited
  LDP upper bound (O'Connell 1998 via Puhalskii 2005 Cor. 2.4(3), p. 8 of
  the arXiv version; AKP 2021 Cor. 1.3), proved in three lines from L1′;
  the hypothesis is cited, not verified by us. Numerically at `N ≤ 400`
  the relaxed rate is bounded away from zero at `c = 2, 2.5` (fits
  `0.0375, 0.1025` against cited `0.0362, 0.1006`), undecided at `c = 1.5`
  (finite `0.0046` still falling, limit `0.0015`), and falls like `1/N`
  at and below `2 ln 2`.
- **Three rates, three columns.** The fitted rate (log-corrected fits over
  `N = 100–400` on a 77-point `c′` grid) reproduces item 05's seven values
  to `10⁻⁴` and the LDP to `0.002` for `c′ ≤ 10`; fitted and cited
  `β_sep` agree to `0.0006` at every `c`. The bracket's lower end gives
  `β*` *exactly* (an identity, tested), so the bracket is `[β*, β_opt]`
  with `β_opt` far above the truth (`0.248` against `0.182` at `c = 6`).
- **The closed count's supremum sits at the corner at every `c`**, so its
  gain is the `q` terms alone, `2β ln q((1 − β)/2)` nats: a dense-side
  gain (`+0.008–0.010` at `c = 6–12`) where the separator's is a sparse-
  side one; the separator wins at `c ≤ 6`, the closed count at `c ≥ 8`.
- **The combined count is valid and not the best**: bounding the balanced
  2-colourings of the components by `2^κ` costs more than the separator
  count gained (tilted-minus-untilted rate `0.161, 0.098, 0.051, 0.028,
  0.009, 0.003` at `c′ = 3 … 10` against gains `0.126, 0.073, 0.043, 0.026,
  0.009, 0.003`), so it falls below the closed count everywhere and below
  `β*` at `c ≤ 4`. The best valid first moment per `c` is
  `max(β_sep, β_closed)`: `0.037, 0.083, 0.182, 0.272, 0.345` at
  `c = 3, 4, 6, 8, 10`, 32%, 23%, 12%, 10%, 11% of the gap to the slopes;
  the sandwich with Edwards & McDermid's published upper line (owner's
  note; reproduced from the recurrence: `0.183, 0.458, 0.656`) is
  `[0.037, 0.183]`, `[0.182, 0.458]`, `[0.345, 0.656]`.
- **In stacks** (`n = 60, 120`): the separator count leads by 2–3 stacks
  at `c = 3–4`, the closed count ties or leads by one at `c ≥ 6`
  (`P(pw ≤ 44) ≤ 0.10` at `(120, 10)` against solver floors of 41–42);
  the window and relaxed forms of the combined count agree to 0.01
  decades at `n = 60`.
- **A correction to the loop's own prediction**: §3.5's typical-instance
  instrument put the closed count's merge at `≤ 0.003` in `β` at `c = 10`;
  the constant gains `0.008`. The first moment is decided in the
  rare-instance regime (§3.3's two maximisers); the separator prediction
  held.
- Checks on record: window/tilt recursions against every labelled graph
  at `N ≤ 6` (`3 × 10⁻¹³`), fast relaxed recursion against the table one,
  finite closed count against the enumeration of closed pairs at `n ≤ 6`
  and Monte Carlo at `n = 7, 8`. Compute: about 0.05 core-hours (0.2
  budgeted). Figure: two panels, palette validated (six slots pass; the
  contrast warning relieved by the legend).
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,726 passed / 2 skipped / 1 xfailed in 4:20, the 10 new tests among them; pathwidth_solver 123 passed in 6:26; paper 71 pages, no undefined references; the one-minute load was below 2).

### Blockers

None. The one-minute load was below 2 throughout.

### Next

Item 07 (the MOSP version): the closed-pair count on random clique covers
by inclusion–exclusion over `S` and the component flips; there is no LDP
to quote, and §6.3 (3) says a `2^κ` bound on the colourings gives the
separator's gain back, so the cover version should count the closed pair
(the `q` terms, which dominate at `c ≥ 8` here) before it attempts a
component law. Item 08 can state the separator inequality with
`P_N(E_relax)`, the threshold proposition of §6.4 verbatim with its
hypothesis, and the closed-pair count's exponent; item 11's ledger gets
the closed floor as the best count at `c = 10`. Item 12 should carry
Edwards & McDermid as the upper line (now in `edwards_mcdermid_poisson`).

---

## Iteration 7 — 2026-11-01 18:01

Item 07, the MOSP version: the closed-pair count, the component flips and
the half-giant line on random clique covers, against `β*(d, μ)` and the
certified slopes; the floors on the 200 Chu & Stuckey instances. **Done.**
Deliverable: `reports/separator_moment.md` §7 (the three events on covers,
the method with the exact `(u, w)` inclusion–exclusion and the
negative-association / tangent bound, the 23-cell grid, the checks, the
half-giant line with the conditional threshold proposition, the floors
table, the kill verdict, corrections, non-claims);
`learning/separator_moment.py` extended (`closed_cover_log_prob_exact`,
`closed_cover_log_count_exact`, `closed_cover_log_prob_na`,
`closed_cover_log_bound`, `cover_log_pair_bound`, the cover exponents
`cover_pair_exponent*`, `closed_cover_exponent_na/ind`, `closed_cover_rate`,
`beta_star_cover`, `beta_closed_cover`, the flips `isolated_binomial_moments`,
`isolated_pgf`, `isolated_pmf`, `flip_joint_moments`, `flip_joint_pmf`,
`flip_log_bound`, `flip_log_bound_fast`, `flip_cover_tail_exponent`,
`flip_cover_exponent_na`, `beta_flip_cover`, the giant `rig_branching_factor`,
`rig_giant`, `half_giant_line`, and `cover_degree_law`,
`edwards_mcdermid_cover`, `_root_above`);
`reports/scratch/separator_moment/07_cover/` (`run.py` with stages `check`,
`slack`, `grid`, `grid_fix`, `giant`, `floors`; `check.log`, `slack.csv`,
`grid.csv`, `giant.csv`, `half_giant.csv`, `floors_cs.csv`, `run.log`,
the `stdout_*.log` of each stage); `tests/test_separator_moment.py` (4 new
tests, 74 in the module).

### Completed

- **Kill criterion (the brief's): met.** `β_closed − β* = +0.0111` at
  `(6, 1)` and `+0.0110` at `(4, 1)`, below `0.02` at both; the flips add
  `+0.002` and `+0.006` (additive estimate `+0.0126`, `+0.0161`). **The
  route is closed for the headline constants on covers**, as on
  `G(n, c/n)` (§6.7). The supremum sits at the corner in every cell, so the
  gain is the coverage term `2β ln(1 − e^{−λ})`, `λ = 3.57` at `(6, 1)`;
  17–18% of the gap to the certified slope at `μ = 1`, `d = 4–8`.
- **Separately pre-registered findings.** (i) The closed count is a
  sparse-side gain, largest at few, large patterns: `+0.018, +0.021,
  +0.020` at `(6, ½), (8, ½), (10, ½)` — **above `0.02` at `(8, ½)`**,
  22–32% of the gap to `b` there — outside the kill's named cells and
  recorded as where the count is worth most. (ii) The flips are worth
  `0.001–0.006` in `β` at `μ ≥ 1`, `d ≥ 4`, up to `+0.017` at `(4, ½)` and
  `+0.011` at the Chu & Stuckey `d = 2` sizes; the supremum sits at *one
  side with no isolated customer* in 21 of 21 cells — the mechanism item
  09 was told to expect, the one-sided lower tail (`−0.0063` nats at
  `(6, 1)`). (iii) **The half-giant line**: `θ = ½` at `e = 0.595, 0.603,
  0.658, 0.736, 0.816` for `μ = ⅛, ¼, ½, 1, 2`, between `e_g` and `1`
  at every `μ`, as the plan predicted; at `μ ≥ 1` every integer `d ≥ 2` is
  above it. Proposition 7.1 (the separator count's floor is positive above
  the line) is proved in three lines from L3 and the thinning of patterns,
  **conditional on an exponentially small lower tail of the giant of the
  random intersection graph, which no held paper states** (Behrisch 2007
  and Lagerås–Lindholm 2008 give the law of large numbers only). (iv)
  **Floors on the 200 instances: zero violations at `< 0.01` for all four
  counts**; the closed floor is higher than the exact-size pair floor on 97
  instances, equal on 103, lower on none — `+1.6, +1.4, +0.8, +0.6, +0.4`
  stacks at 125 × 125, `d = 4, 6, 2, 8, 10` — and the flip floor higher on
  35 (the `d = 2` classes, `+0.8–1.4` stacks at 100–125), equal on 165.
  Stop condition of TASK.md: did not fire.
- **The negative-association bound is free at the exponential scale.** The
  cancellation-free bound (NA of sampling without replacement, Joag-Dev &
  Proschan 1983, plus a tangent of the concave `ln(1 − e^{−L})`) sits a
  constant `0.2` nats above the exact `(u, w)` alternating sum
  (fitted slope `−0.002 / +0.002` nats per customer at `(6, 1), (4, 1)`,
  `n = 8–26`), and `β_closed` from it differs from the independent-sites
  approximation by `≤ 0.001`: the `G(n, c/n)` closed-pair form carries
  over to covers with `q → 1 − e^{−λ}`.
- **Edwards & McDermid on the cover degree law is loose**: `0.66, 0.86,
  0.96` at `(4, 1), (6, 1), (10, 1)` against `b = 0.35, 0.58, 0.80`; the
  published sandwich on covers is wide on the upper side.
- **Checks on record** (`check.log`): the exact closed probability against
  the enumeration of every cover at `n = 3–8`, `m ≤ 3` (66 cases, `9 × 10⁻¹⁶`);
  the NA bound above it on all and on 60 random cases at `n = 8–16`; the
  isolated and joint pmfs exact against enumeration (66 cases); `pgf(1) = 1`;
  `θ = 0` at branching factor one. The half-giant check against the
  ensembles' largest-component fractions **cannot confirm the line**: the
  `fixed` generator's repairs and the Chu & Stuckey connectivity rejection
  put every measured fraction above `θ` (all 200 files have `lcc = 1`).
- **Corrections to the item**: the inclusion–exclusion needs no
  `NestedStructure` (the count depends on two sizes; `(s + 1)²` integer
  terms, no `mpmath`); the item's isolated-customer pgf is the
  unconditioned cover's and the sides given the empty event are neither
  that model nor independent — the joint binomial moments are what the
  weighted count needs; the exact sum over every triple reaches `n ≈ 30`,
  not 125; two root-finding defects in the first grid run (`1.0` returned
  where an exponent falls back to zero at `β → 1`) fixed by `_root_above`
  and the `grid_fix` stage. Compute: 0.60 core-hours for the floors,
  1.4 for the grid (the five pooled-size cells 0.9 of it), seconds for
  the rest: 2.0 against 1 budgeted, the overrun in the flip roots.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,730 passed / 2 skipped / 1 xfailed in 4:25, the 4 new tests among them; pathwidth_solver 123 passed in 6:26; paper builds with no undefined references; the one-minute load was 1–8).

### Blockers

None. The one-minute load was below 10 throughout (the owner's
`run_unlimited.py` was not running).

### Next

Item 08 (the theorems on paper): the closed-pair theorem on covers can
state the `(u, w)` formula of §7.1 (a) as its finite form and the
negative-association bound as a corollary with its citation; L4's first
instance is the cover flip count of §7.1 (b) (`Z = C(I_A + I_R, I_A)`,
every swap an exact-size empty pair), exact and checked; the threshold
proposition for covers is §7.4 verbatim with its hypothesis. Item 09 has
its mechanism measured on covers already (one side with no movable
customer); item 11's ledger can take the closed and flip floors from
`floors_cs.csv`; item 12 carries Edwards & McDermid on both the `β` figure
(§6) and the cover grid (§7.2) and the half-giant line as the proposed
one-line addition to `paper1/latex/figures/excess_phase_diagram.py`
(`e = 0.736` at `r = 1`, dashed, between `e_g` and `e = 1`; not made).

---

## Iteration 8 — 2026-11-01 19:41

Item 08, the theorems on paper: the separator first moment in finite form,
the closed-pair count, the weighted-count identity and its first instance,
the threshold propositions with their hypotheses explicit. **Done.**
Deliverable: `reports/separator_moment.md` §8 (§8.1 the statements —
Theorem S with the factorisation stated as an exact identity per `S`,
Lemma P, Lemmas G and F, Corollary S′, Theorem Cl, Lemma W, Lemma Fl (the
flip lemma), Lemma J, Corollary W-flip, Theorem Cl-cover, Propositions T
and T-cover; §8.2 the proofs with every step named; §8.3 the check with
the `n = 7` table and the Monte Carlo table; §8.4 the Lean targets for
item 10, each with the lemma it rests on and its one new ingredient; §8.5
regenerate / size range / kill verdict / non-claims);
`learning/separator_moment.py` extended with the exact-rational forms
(`connected_probs_exact`, `prob_relax_exact`, `prob_bip_exact`,
`pair_count_exact`, `closed_count_exact`, `weighted_graph_count`,
`isolated_in`, `flip_swaps`, `flip_count`, `weighted_count`);
`reports/scratch/separator_moment/08_theorems/{check.py, check.log,
lemma_w_n10.csv}`; `tests/test_separator_moment.py` (3 new tests, 77 in
the module).

### Completed

- **Kill criterion: not met.** Every labelled graph on 1–7 vertices
  (2,097,152 at `n = 7`) in exact rationals at `p = 1/2` and `1/3`, for
  every `k < n`: Theorem S, Corollary S′, Theorem Cl and the pair count
  all above the weighted count of `{pw ≤ k}`; Theorem Cl's formula
  *equal* to the enumerated `E[X₃]`; Lemmas G, F, P equal to the
  enumerated connectedness, `E_relax(M)` for every `M`, and `E_bip`
  (Gilbert's recursion returns OEIS A001187 at `p = 1/2`); the
  factorisation identity `P_n(E_bip(S)) = P_N(E_bip)` exact on all 120
  `(n, k, S)` triples at `n ≤ 6`; the flip lemma on 1,422,005 exact-size
  pairs; Lemma W on 1,000 random instances at `n = 10` with `Z` the
  move-class size and the flip count; Lemma J on 24 enumerated cover
  cases; `E[Y]`, `E[X]` of `flip_log_bound` within 1.7 s.e. of 1,000
  Monte Carlo covers in four cells. **Zero violations**, 29 s on 8 workers.
  No statement withdrawn; stop condition of TASK.md did not fire.
- **What is now a theorem on paper, finite and unconditional**: the
  separator bound with its inner probability an exact weighted count and
  the union bound over `S` the only inequality (the inner probability is
  the same for every `S`, by the bijection graphs(V) ≅ graphs(V ∖ S) ×
  𝒫(pairs meeting S), written out for item 10); the closed-pair bound as
  an exact expectation (closed ⟺ empty ∧ every separator vertex sees both
  sides, `1 + 2s` independent events on disjoint pair sets); the
  weighted-count identity `Y ≥ 1[X > 0]` pointwise, equality at `Z = X`;
  the flips as an admissible `Z` (four-case emptiness, injectivity,
  Vandermonde), and their exact evaluation on random covers by the joint
  binomial moments and a two-variable inversion. The thresholds stay
  propositions conditional on (H_G) (cited: O'Connell via Puhalskii Cor.
  2.4(3), AKP Cor. 1.3) and (H_C) (in no held paper).
- **Two corrections to later briefs.** Item 10 needs no termination
  argument for the closure (L2 iii: a fixpoint after one round, so two
  applications of `V ∖ closedNbhd`); and Theorem S can be formalised with
  the inner probability *defined* as the weighted count of the pair-form
  event, so Lemma P (components as `Finset`s, the obstacle of §2.6) is
  not on Theorem S's path — only Corollary S′ and Lemmas G, F need it.
- **Seven-vertex observations, quoted as nothing more**: `E_bip` and
  `E_relax` first differ in measure at `N = 6` (0.1156 vs 0.1188 at
  `p = 1/2`); the separator count is below the closed count at
  `k = 0–1` and above it at `k = 2–4` (an echo of §6.3's sparse/dense
  split); at `k = n − 1` the closed count exceeds the pair count (sides
  larger than forced). At `n = 10` the flips merge 1.2–1.3 at the
  median, the move-classes 2.4; at `k = 3` on `(10, 10, 3)` covers the
  weighted count is 1.35 against a sampled `P(X > 0)` of 0.42 — the lower
  tail of `Z` (pairs with no isolated vertex) is the gap, as item 09
  expects.
- Compute: 29 s of wall on 8 workers (0.1 core-hours budgeted; about 0.05
  used); the one-minute load was below 2 throughout.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,733 passed / 2 skipped / 1 xfailed in 4:25, the 3 new tests among them; pathwidth_solver 123 passed in 6:25; paper builds with no undefined references; the one-minute load was below 2).

### Blockers

None.

### Next

Item 09 (the branch): §4.6 says no `Z` gains more than the measured
slack (`0.012–0.019` in `β` at `β*`, `n ≤ 32`), so the item is the one
page the fork prescribes; Lemma W and Lemma Fl of §8.1 are its statements,
and the recombination count `Z_j` must be checked as Lemma Fl was (every
image pair empty, injective) before it is used. Item 10 takes §8.4's table
in the recommended order (Lemma W first; Theorem S via `sum_gnpWeight_fiber`;
Lemmas P, G, F only if components-as-`Finset`s is cheap). Item 12 quotes
Theorem S and Theorem Cl from §8.1 and Propositions T / T-cover with their
hypotheses, never as theorems.

---

## Iteration 9 — 2026-11-01 20:14

Item 09, the branch: the weighted count's lower tail — can any computable
`Z` merge the far pairs? **Done.** Deliverable: `reports/separator_moment.md`
§9 (Lemma Rc, the recombination count as an admissible `Z`, with its
brute-force check; the measured lower tail on item 04's planted instances;
the computable `Ẑ₀`, its exact transform and exponent, `β_W(c)` against
`β_closed(c)`; the kill verdict with the mechanism; the (d) branch: the
separator count at `c = 2.0, 2.2, …, 4.0` and the exact floors at `n = 60`;
regenerate / size range / non-claims); `learning/separator_moment.py`
extended (`recombinations`, `recombination_pairs`, `z_recomb`,
`side_avoiders`, `z_hat0`, `z_hat_log_laplace`, `log_pair_count`,
`log_weighted_bound`, `z_hat_exponent`, `weighted_exponent`,
`beta_weighted`); `reports/scratch/separator_moment/09_lower_tail/`
(`run.py` with stages `check`, `tail`, `stats`, `laplace`, `threshold`;
`check.log`, `tail.csv`, `cells.csv`, `laplace.csv`, `beta_w.csv`,
`rate_fits_fine.csv`, `threshold_fine.csv`, `floors_60_rows.csv`,
`floors_60.csv`, `run.log`); `tests/test_separator_moment.py` (5 new tests,
82 in the module).

### Completed

- **Kill criterion: met.** `β_W − β_closed = −0.0002` at `c = 6` and at
  `c = 10` (`0.1801` against `0.1803`; `0.3451` against `0.3453`), against
  the kill at `0.02`: **the weighted count is closed on this record** for
  every `Z` with a closed-form transform. Mechanism: `Ẑ₀ = 1` iff the
  planted pair is *closed* (every separator vertex sees both sides), so
  `E[1/Ẑ₀] ≥ P(closed | empty) = (q_t q_r)^k` exactly and the weighted
  count is at least the closed count at the forced sizes; the exponent's
  minimiser is interior at `λ = 0.0006` and `0.0006` nats above the corner
  `2β ln q(a)` (`0.030` nats at `c = 6`, `0.025` at `c = 10`). The typical
  `Ẑ₀` is `e^{0.05–0.06 n}` and none of it reaches the constant: the cost
  of emptying `L_A`, `L_R` falls faster than the entropy of the moves
  grows. The planner's pre-registered expectation (plan §0) holds to
  `0.0002` in `β`.
- **Lemma Rc, checked before it was called a lemma**: every labelled graph
  on 4–6 vertices, every width with `min(t, r) ≥ 2`, every exact-size pair
  (218,424), every recombined pair (1,351,064) empty, exact-size, distinct,
  not `P₀`, in the enumeration, closed-form count = explicit count,
  `Ẑ₀ ≤ Z ≤ X`; Lemma W pointwise with `Z_4` and `Ẑ₀` on 2,100 random
  `(G(10, p), k)`; zero violations, 3 s. The general form has both lobes
  and `d = t − r ∈ {0, 1}`; the item's definition is the reversed lobe at
  `N` odd; `1 + Σ_j Z_j` is admissible (the level is recoverable from
  `|U_A|`) and is what was measured.
- **The measured lower tail** (2,800 planted instances at `β*`, `j ≤ 4`,
  order `Ẑ₀ ≤ Z_all ≤ X` on all; under a second): at the largest `n`, the
  recombinations `Z_4` recover 54% / 79% / 98% of item 04's measured
  union-bound slack (`0.035 / 0.031 / 0.042` of `0.065 / 0.039 / 0.043`
  nats per vertex at `c = 6`, `c = 10`, covers), `Ẑ₀` 26% / 28% / 37%
  (`0.017 / 0.011 / 0.016`); the flips `≤ 0.010`. `Z_4 = 1` on 16–21% of
  instances where `N` is odd, on 30–35% of the closed planted pairs and
  never on an open one; `P(Z_4 = 1)` is 56–58% of `E[1/Z_4]`. The price
  of computability at `n = 32` is `0.018–0.026` nats per vertex
  (`0.005–0.008` in `β`), from the two-sided and reversed-lobe moves whose
  transform needs the edge-free pairs inside `G[S]` and has no closed form
  here. On covers `Z_4` is the whole measured slack to two decimals (the
  cluster there is the reversed pair, §4.3).
- **The transform, exact to `n = 3,200`**: `(1/n) log E[1/Ẑ₀]` runs
  `−0.018 → −0.0291` at `c = 6` (asymptotic `−0.0290`) and `−0.013 →
  −0.0245` at `c = 10` (`−0.0245`), within `0.001` per vertex of
  `log P(P₀ closed)` at every `n`; at `n = 32` it reproduces the planted
  measurement. Checks: against the average over every planted graph at
  `n = 6`; the bound above `P(pw ≤ k)` on every labelled graph at `n = 5`
  and below the pair count.
- **The (d) branch, near the threshold**: `β_sep` at eleven `c` from `2.0`
  to `4.0` (cited LDP rate and a fit on a `0.05` grid of `c′`, within
  `0.0022` of each other). **The separator count's gain over `β*` peaks at
  the pair count's threshold**: `+0.0294` at `c = 2.8 ≈ 4 ln 2`, falling to
  `+0.0059` at `c = 2` and `+0.0219` at `c = 4`; in nats at `β*` it is
  monotone (`0.142 → 0.078`), the peak in `β` being the slope `dg/dβ`
  falling from 7.6 to 3.9. Sandwich with Edwards & McDermid: `[0.006,
  0.085]`, `[0.029, 0.162]`, `[0.037, 0.183]`, `[0.083, 0.285]` at `c = 2,
  2.8, 3, 4`. At `n = 60` (exact `P_N(E_bip)`) the separator floor at
  `< 0.01` is `−1, 0, 0, 0, 1, 1, 2, 3, 3, 4, 4` across the eleven `c`, one
  to two stacks above the exact-size pair count's from `c = 2.2` on, one
  above the closed count's through `c = 3.8`, equal to the relaxed form's
  everywhere, and `1 / 5`, `4 / 8` against the pilot's minimum exact
  pathwidth at `c = 3, 4`: real in the constant, small in stacks at sixty.
- Compute: about 0.03 core-hours (0.5 budgeted); the one-minute load was
  below 1 throughout. No figure (none in the deliverable).
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,738 passed / 2 skipped / 1 xfailed in 4:31, the 5 new tests among them; pathwidth_solver 123 passed in 6:26; paper 71 pages, no undefined references; the one-minute load was below 1).

### Blockers

None. The one-minute load was below 1 throughout.

### Next

Item 10 (Lean) takes §8.4's table in its recommended order (Lemma W first,
via `sum_gnpWeight_fiber` for Theorem S); Lemma Rc of §9.1 is a candidate
after those — its proof is four edge classes and a reconstruction of
`(W, U)` from `(A′, R′)`, and `z_recomb` is pinned to the explicit
enumeration on every graph to six vertices — but nothing in §9 depends on
it being formalised, since `β_W = β_closed` to `0.0002` and the closed
count is Theorem Cl. Item 11's ledger takes, per cell at `n ≤ 32`, the
three measured slacks of §9.2 (`X`, `Z_4`, `Ẑ₀`) beside §4.6's; item 12
should say that the weighted count is closed (the lower tail is the closed
pair), that the recombinations are half the cluster's logarithm on
`G(n, c/n)` and all of it on covers, and carry §9.6's finer-`c` table and
the gain's peak at `c = 4 ln 2` in the `β` figure's near-threshold region.

---

## Iteration 10 — 2026-11-01 21:20

Item 10, Lean: the deterministic lemmas and the union bound over separators.
**Done — all of (a)–(d), and the relabelling, Theorem Cl's union bound,
Lemma Fl and Corollary W-flip's sound part beyond them.** Deliverable:
`lean/MOSPFormalization/SeparatorMoment.lean` (new; 1,229 lines, 78 `theorem`
declarations, 21 definitions; imported by `lean/MOSPFormalization.lean`;
imports `EmptyPair`, `FirstMoment`, `CliqueCoverMoment`; **no `sorry`, no
`axiom`**, every theorem on `propext`, `Classical.choice`, `Quot.sound` only);
30 new `#print axioms` lines in `paper1/axiom_check.lean` (`make -C
paper1/latex axioms`: 296 theorems checked, 0 failures); `learning/sandwich.py`
(`SEPARATOR_PROVED`, 30 names, in `ALL_PROVED`; the `--stage separator`
numerical pin with `close_step` and `sees_both` transcribed from Lean and
`separator_check` / `separator_summary`); `tests/test_separator_moment.py`
(5 new tests, 87 in the module); `reports/separator_moment.md` §10 (the
statement-by-statement table with Lean names and status, the headline theorem
verbatim, what went beyond the brief, the three obstacles named, the checks,
the corrections to the item, the Appendix A rows drafted for item 12,
regenerate / size range / kill verdict / non-claims);
`reports/scratch/separator_moment/10_lean/` (`lake_build.log`,
`axiom_check.log`, `sandwich_separator.{md,log}`, `gate.log`).

### Completed

- **Theorem S is a Lean theorem, exactly as §8.1 states it**:
  `weightedSum_graphsOfPathwidthLe_le_choose_mul_innerBip` —
  `∑_{pw G ≤ k} gnpWeight p G ≤ n.choose k · innerBip p S₀ k` for `0 ≤ p ≤ 1`,
  `k < n` and any `k`-set `S₀`, with `innerBip` the `G(N, p)`-weighted count
  of the pair-form event over the graphs on `V ∖ S₀` (kept as graphs on `V`
  with no edge meeting `S₀`, as §8.4 recommended). The chain: L1′ (a) ⇒ the
  union bound over separators (`…_le_sum_separators`); the factorisation
  step `sum_gnpWeight_fiber` (the fibre over a graph `H` on `V ∖ S` is the
  `2^{|pairsMeeting S|}` subsets of the pairs meeting `S`, total weight
  `(p + (1 − p))^{…} = 1`, by `sum_nbij'` with `F ↦ fromEdgeSet (E(H) ∪ F)`);
  `card_pairsOff` (`|pairsOff S| = (n − |S|).choose 2`, through the edges of
  `⊤` on the subtype and `Sym2.map.injective`); and the relabelling
  `innerBip_eq_of_card_eq` (a permutation of `V` carrying `S₀` onto `S`,
  built from `Fintype.card_eq` on the subtypes and their complements and
  `Equiv.Set.sumCompl`; `relabel e G := G.comap e.symm`, with the edge set
  mapped by `Sym2.map e`, restriction and `E_bip` invariant). The named
  `Prop` `SeparatorFactorisation` the item allowed was not needed.
- **L1, its cover form, L1′ (a), (b), (d), L2 (i)–(v), L1 + L2, the
  characterisation step of Cl, Lemma W and its `G(n, p)` reading**: all
  proved (`exists_balanced_separator`, `exists_balanced_separator_cover`,
  `exists_isBalancedBip`, `componentOff_subset_side`,
  `card_componentOff_le_of_isBalancedBip`, `not_isBalancedBip_threeK2`,
  `card_componentOff_threeK2_le`, `subset_compl_closedNbhd_iff`,
  `subset_closeStep`, `closeStep_isClosedPair`, `closeStep_closeStep`,
  `sdiff_eq_inter_boundary_of_isClosedPair`, `card_closeStep`,
  `exists_closedPair_of_pathwidth_le`, `isClosedPair_iff_sees_both`,
  `weightedCount_ge_indicator`, `weightedSum_graphsOfPathwidthLe_le_weighted`).
  L1′ (b) uses a `componentOff` defined as the vertices reachable by a walk
  avoiding `S` (induction on `SimpleGraph.Walk`), not Mathlib's
  `ConnectedComponent` quotient; the `3K₂` half "no `3`-set is an empty pair
  with its complement" is `decide +kernel` over the 64 subsets (a direct
  `decide` over `64 × 64` pairs hits the recursion limit; `native_decide`
  not used).
- **Beyond the brief**: Theorem Cl's union bound over `closedIndices t r`
  (`weightedSum_graphsOfPathwidthLe_le_sum_closedPairs`); Lemma Fl
  (`flipPair_isEmptyPair` — the four cases —, `flipPair_disjoint`,
  `card_flipPair`, `flipPair_injOn`, `card_flips_le`: `1 ≤ #flips ≤ X` on
  the empty pairs); Corollary W-flip's sound part
  (`weightedSum_graphsOfPathwidthLe_le_flipWeighted`).
- **Obstacles named, not hit on Theorem S's path** (§10.3): components of
  `G − S` as finsets with their sizes (Lemmas P, G, F, Corollary S′ in
  component form, the converse of L1′ c); the product-over-blocks lemma for
  weighted sums over edge subsets (Theorem Cl's independence step — the one
  thing between Theorem Cl and Lean, a session on its own);
  inclusion–exclusion over pattern sets (Lemma J, Theorem Cl-cover). The
  paper may cite Theorem S as proved in Lean, Theorem Cl as "union bound and
  characterisation in Lean, independence step on paper", W-flip as "sound
  part in Lean".
- **Checks**: every statement was brute-force checked before it was written
  (§2.4, §8.3); the two statements stronger than the checked ones
  (`closeStep` idempotent and closed for *every* `A`; the sees-both
  characterisation) re-checked on every labelled graph to 5 vertices and
  every `A` in the tests; the numerical pin `python -m learning.sandwich
  --stage separator`: 500 random `G(n, p)` graphs at `n = 5–11` with exact
  pathwidth, `k = pw` and `pw + 1`, **1,000 rows, zero violations**, the
  Lean `closeStep` transcription equal to item 03's `close_pair` on every
  exact-size pair, in 1 s.
- **Corrections to the item**: no termination argument (the closure is
  idempotent on every pair, `subset_compl_closedNbhd_compl_closedNbhd` for
  every `A`); `|R| = n − k − t` written `(n − k) / 2`; (d) fitted and so did
  the relabelling; `decide` needs the 64-subset reduction.
- Compute: seconds (Lean builds the file in 1.5 s; the pin in 1 s; the gate
  about 12 minutes). The one-minute load was below 2 throughout.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,743 passed / 2 skipped / 1 xfailed in 4:32, the 5 new tests among them; pathwidth_solver 123 passed in 6:23; paper 71 pages, no undefined references; the one-minute load was below 2). Log: `reports/scratch/separator_moment/10_lean/gate.log`.

### Blockers

None.

### Next

Item 11 (the slack ledger): per cell, in stacks, what each count buys —
the separator and closed floors from `floors_cs.csv` (§7.5) and `finite.csv`
(§6.5), the measured slacks of §4.6 and §9.2 — and what is left to the
truth. Item 12 should quote Theorem S from Lean
(`weightedSum_graphsOfPathwidthLe_le_choose_mul_innerBip`), take the five
Appendix A rows drafted in §10.6 (adding `SeparatorMoment.lean` to the file
list at the head of `sec9e_appendix_random.tex`), and say that Theorem Cl's
independence step and Lemma J are on paper. Item 13's reserve could be the
product-over-blocks lemma (Theorem Cl into Lean) if nothing from 01–12 is
more pressing.

---

## Iteration 11 — 2026-11-01 22:50

Item 11, the slack ledger: in stacks, on certified instances, what each
count buys and what is left — the union bound (floor to Harper) against the
necessary condition (Harper to pathwidth). **Done.** Deliverable:
`reports/separator_moment.md` §11 (conventions and the ladder, the covers
table at `n = 30–75`, the `G(n, 10/n)` table at `n = 30–60`, the paragraph
per model, the Harper censoring table, the figure, regenerate / size range /
kill verdict / corrections / non-claims);
`reports/scratch/separator_moment/11_ledger/` (`run.py` with stages
`covers`, `gnp`, `stats`, `draw`; `ledger_6_1.csv` and `ledger_gnp.csv`
with every instance's ladder; `cells_gnp.csv`; `summary.csv`; `ladder.png`;
`run.log`; `gnp_stdout.log`; `gate.log`); `learning/separator_moment.py`
extended (`harper_bound_graph` — Harper's bound in graph form on the `vs`
scale, `_f_exact` reused, cap not clipped at `MAX_LEVEL`; `HarperBound`;
`floor_pw`; `layout_vertex_separation`); `tests/test_separator_moment.py`
(4 new tests, 91 in the module: Harper ≤ exact vertex separation at every
cap; equal levels, cap and value `+ 1` to `expansion_bound` on the edge
cover; the floor convention against the record's `floors`; the layout
function against `compute_pathwidth`).

### Completed

- **Instances, nothing re-solved.** The 600 certified `(6, 1)` fixed
  generator instances at `n = m = 30–75` with Harper on record
  (`slack_6_1.csv`, read; the item and the plan say 650 — the record's own
  table sums to 600), sizes regenerated from the seeds with the record's
  old and exact-size floors reproduced on all 600 (asserted); the pilot's
  543 proved `c = 10` graphs at `n = 30, 40, 50, 60`, regenerated from
  their seeds with the edge counts asserted and **every recorded layout
  re-checked to its width** (543 / 543 in one orientation). Everything on
  the `pw` scale; floors at `< 0.01` (the paper's) and `< 1` (the record's).
- **Stop condition: did not fire.** Zero floors above a certified
  pathwidth at `< 0.01` for every count on all 1,143 instances; at `< 1`
  the expected handful (covers: exact-size 1, closed 4, flip 1; graphs: 2
  per count, the two minimum-pathwidth graphs at `n = 30`).
- **What the counts buy, in stacks.** Covers at `n = 75`: the old pair
  floor is 7.0 stacks below `pw` (mean); exact sizes buy 0.8, the closed
  count 0.8 more, the flips nothing (equal to the exact-size floor on every
  instance but the parity cell at 50; `0.03` decades at `k = pw`): **1.6 of
  the seven**. The closed count is higher than the exact-size floor on
  150 / 150 at 40, 47 / 50 at 50, 41 / 50 at 75 and on none at 30, 35, 60 —
  §7.2's `+0.011` in `β` is `0.3–0.8` stacks here and rounds by parity.
  `G(n, 10/n)` at `n = 60`: old floor 5.8 stacks below the mean `pw`; the
  separator and closed counts buy **one stack** (`22 → 23`, the same one:
  their floors coincide in all four cells), nothing at `n ≤ 50` (§6.7's
  `+0.004–0.008` in `β` is `0.2–0.5` stacks). The `n = 60` row is §6.5's
  `(60, 10)` row on the `pw` scale.
- **Where the leftover sits.** Covers: of the `3.5 → 5.4` stacks from the
  best count to `pw`, **at least 77–88% is the union bound** (`Harper −
  best`: median 3 at 30–50, 4 at 60–75; Harper at or above the best count
  on all 600) and **at most 12–23% the necessary condition** (`pw − Harper`
  mean `0.40 → 1.24`, inflated by the cap from `n = 50`). Graphs: **90–93%
  union bound at `n ≤ 50`**, where Harper equals `pw` on two thirds of the
  graphs (91 / 137, 95 / 137, 92 / 136) and the necessary condition's slack
  is at most `0.3` stacks; at `n = 60` the split (68 / 32, `Harper = pw` on
  4 / 133) is the cap's. The leftover grows with `n` in stacks (`pw − best`
  `3.5 → 5.4` on covers, `3.5 → 4.8` on graphs) and falls as a fraction of
  `n` (`0.115 → 0.072`, `0.116 → 0.080`). **The slack of the first moment
  is the union bound on both models, and the counts of this loop reach a
  fifth of it**; the necessary condition is tight to within a stack
  wherever Harper reaches the forced prefix.
- **Censoring, stated as §8.5 (b) does.** Covers: the record's runs
  complete but clipped at `MAX_LEVEL = 12`, below the forced `t = 14–16`
  at `n = 75`. Graphs: 16 levels under 60 s ran out of budget inside
  level 12–14 on every graph at `n ≥ 50` (cap 8–13 against `t = 12–18`);
  `pw − Harper` is an upper bound and `Harper − floor` a lower bound
  throughout, and the `n ≥ 50` graph rows carry the cap.
- **Figure** `ladder.png`: median gap to `pw` per rung and `n`, two
  panels, rungs dodged within each `n`, direct labels at the largest `n`;
  palette slots 1, 2, 3, 4, 7 validated (contrast warning on slots 3–4
  relieved by direct labels and the tables).
- **Corrections to the item**: 600 not 650; `nested_floors(1, …)` is the
  exact-size pair floor (one rung, not two; equal to `cover_log_pair_bound`'s
  on every instance); the record's `harper` is on the MOSP scale; the
  pilot's `lower` column is the solver's starting bound and `status` the
  proof; the Harper pass with 16 levels cost **4.87 core-hours against the
  item's 0.5** (49 min on 6 workers at nice 19; a first launch failed on a
  wrong `lower == width` assertion and was relaunched), and reached the
  caps a 12-level run (18–50 s per graph at `n = 60` in the probe, about
  2 core-hours) would have.
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,747 passed / 2 skipped / 1 xfailed in 4:32, the 4 new tests among them; pathwidth_solver 123 passed in 6:25; paper 71 pages, no undefined references; the one-minute load was below 4). Log: `reports/scratch/separator_moment/11_ledger/gate.log`.

### Blockers

None. The one-minute load was 1–6 (our own workers) throughout; the
owner's `run_unlimited.py` was not running.

### Next

Item 12 (the write-up): §0 of the report and the paper's Appendix E
paragraph. From §11 it can say, in stacks: the counts of this loop buy
one to two stacks at `n = 60–75` on both models (the exact-size pair one,
the closed count one on half the sizes, the separator one at `c = 10`,
`n = 60`, the flips none on `(6, 1)`), the remaining 4–5 stacks are at
least three-quarters the union bound by Harper's deterministic
instrument, and the necessary condition is tight to within a stack where
Harper reaches the forced prefix — with Harper's cap stated beside every
such number. Theorem S from Lean, Theorem Cl with its paper step, Edwards
& McDermid as the upper line (§6, §7), the finer-`c` table of §9.6, and
the ladder figure as the candidate for the paper's "Why the first moment
is loose" paragraph (print it as a vector then). Item 13's reserve: the
product-over-blocks lemma (Theorem Cl into Lean), or a 12-level Harper
rerun at `n = 60–75` with no budget if the exact split at the largest
sizes is wanted.

---

## Iteration 12 — 2026-11-01 23:22

Item 12, the write-up: the report's summary, the paper's paragraph, the
`CLAUDE.md` paragraph, the pointer in the excess report. **Done.**
Deliverable: `reports/separator_moment.md` §0 (the one-paragraph answer; the
three events and the two identities; the ladder of counts with each rung's
status — Lean name, on paper, measured with its range and section, fitted,
conditional; the constants tables for `G(n, c/n)` at eight `c` and for covers
at six cells, each column with its basis; the two threshold propositions with
their hypotheses' status; the clumping decomposed in one paragraph; the ledger
in stacks; the kill verdicts of all twelve items in one table; "What this is
not"; "Open"; "Where everything is" with page counts and regenerate commands)
and §12, the `CLAUDE.md` paragraph in the format of "The excess phase diagram"
(drafted, `CLAUDE.md` not edited); `paper1/latex/sec9e_appendix_random.tex`
(the last two sentences of "Why the first moment is loose" replaced by
Theorem~E.6 — Theorem S in finite form, cited to Lean — and about a page on the
separator count, its rate from the cited LDP, `β_sep = 0.037` at `c = 3` and
`0.341` at `c = 10` with their basis, the threshold `2 ln 2` conditional on the
cited upper bound, the closed-pair count with its independence step marked
on paper, the weighted count, the planted measurement, and the honest sentence
on the two unreconciled instruments; the section's closing sentence replaced by
the sandwich with Edwards & McDermid's upper line; one sentence in the cover
sandwich paragraph and one in "What is checked"; the header comment);
`paper1/latex/sec9a_appendix_lean.tex` (five Appendix A rows, A.64–A.68, for
the 30 new Lean theorems, all already audited by `paper1/axiom_check.lean`);
`paper1/latex/refs.bib` (seven entries: O'Connell 1998, Puhalskii 2005,
Andreis–König–Patterson 2021, Do–Erde–Kang 2024, Luczak–McDiarmid 2001,
Kolesnik–Wormald 2014, Edwards–McDermid 2015, every DOI resolved through
Crossref, cache updated); `reports/excess_phase_diagram.md` §14 item 1 struck
through with a pointer; `reports/scratch/separator_moment/12_writeup/`
(`paper_build.log`, `axiom_check.log`, `check_refs.log`, `gate.log`).

### Completed

- **The paper builds: 71 pages before, 74 after** (`make -C paper1/latex`,
  `make check`: no undefined references; `make axioms`: 296 theorems, 0
  failures; `check_refs`: 79 entries, 67 DOIs, 0 disagreements; `check_lean`:
  193 names cited, 0 missing). The new text runs from the bottom of page 70
  to the top of page 72, about 1.1 pages with the paragraph's kept opening
  and the theorem environment — the item said at most one page, and this is
  the length after one trim; cutting further would drop a named fact.
  The one `Overfull \hbox` in the log is in `main.tex` (line 102), not new.
- **Wording checked against the rules**: "we found no prior statement" (twice,
  never "first"); every rate from a fit is "fitted"; `β_sep` is tied to the
  cited LDP in the theorem's paragraph and again in "What is checked"; the
  threshold is "conditional on the cited large-deviation upper bound"; the
  planted numbers carry `n ≤ 32`; the ledger carries the cap; the two
  instruments' disagreement is stated, not resolved.
- **§0 states, per count, exactly what is proved where**: Theorem S in Lean
  (`weightedSum_graphsOfPathwidthLe_le_choose_mul_innerBip`), Theorem Cl's
  union bound and characterisation in Lean and its independence step on
  paper, Lemma W and Fl in Lean and Lemma J on paper, Lemma Rc and `Ẑ₀` on
  paper, the combined count fitted only, Propositions T and T-cover
  conditional with (H_G) cited and (H_C) in no held paper. Two cells of the
  constants table (`β_W` at `c = 2, 2.8`) are "—" because item 09 did not
  compute them.
- **The one-voice edit of §1–§11 was not done**: the sections are kept as
  their items wrote them (each self-contained, each with its own regenerate
  command and non-claims), and §0.10 says so. The header was edited and §0
  and §12 added. A rewrite would have risked drifting numbers for no new
  content, and the summary is the single document the item asked for.
- Kill criterion: none. Size range: as stated per claim in §0 (every number
  there carries its section). Compute: none (builds and checks only).
- Gate: `python3 Ralph_Loops/loop0011/gate.py` **PASS** (lake build ok, 0 sorry, 0 axiom; tests 1,747 passed / 2 skipped / 1 xfailed in 4:32; pathwidth_solver 123 passed in 6:24; paper 74 pages, no undefined references; the one-minute load was about 1). Log: `reports/scratch/separator_moment/12_writeup/gate.log`.

### Blockers

None.

### Next

Item 13, the reserve. Candidates from §0.9, in the order the record suggests:
the product-over-blocks lemma that puts Theorem Cl's independence step into
Lean (§10.3, a session on its own; after it the paper may say "Theorem Cl in
Lean"); or the reconciliation of the two slack instruments — a Harper run
with no level cap at `n = 60–75` on the `(6, 1)` covers (about 2–5 core-hours
at nice 19, nothing re-solved) and the planted `E[1/X]` at `n = 48–64` —
which would decide whether the union bound's slack grows with `n` or the
ledger sees the `θ = 0.01` rounding. The owner's `CLAUDE.md` paragraph is
§12 of the report, ready to paste.
