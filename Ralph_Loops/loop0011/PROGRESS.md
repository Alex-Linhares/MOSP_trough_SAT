# loop0011 progress

Plan: `reports/separator_moment_plan.md` — counting events (balanced
separators, closed pairs, the weighted count) instead of witnesses (empty
pairs) in the first-moment lower bound on pathwidth; items in
`iterations.md`; rules in `TASK.md`. Gate: `python3 Ralph_Loops/loop0011/gate.py`.

Current: 1/13 SOLVED

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
