# Exact pathwidth of random intersection graphs

*2026-10-17. Script: `learning/rig_pathwidth.py`. Figures: `reports/figures/rig_*.png`.
Background: `reports/random_graph_pathwidth_survey.md` §4 and §7(c).*

Every certified MOSP optimum of a generated instance is `pw + 1` of its MOSP
graph: customers are the vertices and each product is a clique
(`lean/MOSPFormalization/MOSPGraph.lean`). A random MOSP matrix therefore gives
a random intersection graph (RIG) whose pathwidth is known exactly. Throughout
this report **`pw = optimum − 1`**. The survey (§7(c)) found no published exact
pathwidth measurement of RIGs, so as far as we know these are the first.

**Data.** No instance was solved or certified again.
- `learning/data/ensemble/results.csv`: 37,800 instances, `n = 10…40`,
  `m ∈ {n, 2n}`, 150 per cell. The Bernoulli generator (`p`) is the
  Karoński–Scheinerman–Singer-Cohen model up to a patch (see below). The fixed
  generator places each product on exactly `d` customers, Chu & Stuckey style.
- `learning/data/ensemble/results_upward.csv` (§16 of `reports/ml_nature.md`):
  the cells whose model matches (`m ∈ {n, 2n}`, `n = 50, 60, 75`, 50 per cell,
  4,523 instances). Three uncertified instances at `n = 75, m = 2n` are
  dropped (one in `d = 2`, two in `p = 0.025`). That trims the sparse tail of
  those two cells slightly. The 100-customer cell is excluded because 9 of its
  75 instances are uncertified.

**New compute**, every process under `nice -n 19` and never more than 8 workers:
- (a) exact treewidth for the 37,800 instances and the 1,500 at `n = 50`,
  exact on 38,548 of the 39,300 (§4);
- (b) exact pathwidth of 9,848 *unpatched* Bernoulli matrices (the true
  `R(n, m, p)`), regenerated from the same seeds. These are new graphs, never
  solved before (§1).

Results are in `learning/data/ensemble/treewidth_exact.csv` and
`kss_raw_pathwidth.csv`. Both are resumable, and the second keeps its layouts
as witnesses.

**What this report does not repeat.** These results are already in
`reports/ml_nature.md` and are cited here, not derived again:
- `E[opt]` is linear in `n` at fixed degree (§12);
- the CV of the optimum is below 0.2 at `n = 40` (§12);
- the `E[opt]` formula of §12;
- the hardness ridge (§11, §16, §25);
- the min-fill bracket on `pw − tw` (§12).

Regenerate everything, after the two data files exist:

```bash
nice -n 19 python -m learning.rig_pathwidth kss-raw --workers 4   # §1: exact pw of the 9,848 unpatched matrices, ~1 min
python -m learning.rig_pathwidth analyse      # all tables to stdout, the four figures, ~40 s
# §4's treewidth: the commands at the end of §4 (13.2 core-hours as run)
```

**At a glance** (each item has its size range in the section):

1. **The Karoński–Szymkowiak thresholds** (`n = 10–75`).
   - On the unpatched `R(n, m, p)`, `P(pw ≤ 2)` against `x = p/p₃*` is nearly
     the same curve for every `n`. It sits to the right of the derived limit
     `e^{−x⁴/24}` (`x₅₀` ≈ 2.1–2.9 against 2.02).
   - The offset is a finite-size correction of order `m^{−1/4}`, too slow to
     vanish at any feasible `n`.
   - At `m = n` almost every failure is a product with ≥ 4 customers. Among
     instances with no such product, 94–100% have `pw ≤ 2` (for `x₃ ≤ 2.5`).
   - The patched generator, not the theorem, caused the apparent drift with
     `n`.
   - The `k = 4, 5` conjecture is consistent with the data but untestable
     here: non-clique obstructions dominate at these sizes.
2. **The sd of `pw` at fixed density grows** (`n = 15–75`). A constant is
   rejected. The growth is like `n^{0.2–0.5}`, and √n and log n cannot be
   distinguished.
3. **`pw/n` at fixed mean degree falls with `n`** through 75: no collapse.
   - Extrapolated `pw/n` limits sit *below* the Erdős–Rényi lower bound at
     the same mean degree for `c ≥ 8–12`.
   - At equal finite `n` and `c ≥ 4`, ER treewidth already exceeds RIG
     pathwidth.
   - Mean degree is the wrong size-free coordinate for a clustered model.
4. **`pw − tw` is 0, 1 or 2 on all 38,548 exactly measured instances**
   (`n = 10–50`), never 3. `P(pw > tw)` grows with `n` at fixed sparse
   density: 0.07 → 0.70 from `n = 10` to 50 at `d = 2`, `m = n`. It
   concentrates at 2–2.5 customers per product. The min-fill heuristic of
   §12 had hidden a third of the gaps.

---

## Findings

### 1. The Karoński–Szymkowiak thresholds (`pw ≤ 2, 3, 4`)

**The statement, checked in the PDF**
(`literature/2001-Karonski-Szymkowiak-Randomized-Three-Tracks-Gate-Matrix-Layout-DM.pdf`):
- **Model.** `R(n, m, p)` is an `n × m` matrix with i.i.d. Bernoulli(`p`)
  entries and `m = n^α`. Rows are nets (customers) and columns are gates
  (products).
- **3-GML.** A "yes" instance of 3-GML has a column order with at most 3
  tracks, which is `pw ≤ 2` (the 1-GML obstruction is `K₂`).
- **Thm 1.** Set `p₃* = m^{−1/4} n^{−1}` for `α ≤ 40/21`. Then
  `Pr(yes) → 1` if `p ≪ p₃*` and `→ 0` if `p ≫ p₃*`.
- **§5 conjecture.** For every `k`, `p_k* = m^{−1/(k+1)} n^{−1}` when
  `α ≤ (t_k − 2)(k + 1) / ((t_k − 1)(k − 1))`, and
  `m^{−1/2} n^{−t_k / (2(t_k − 1))}` above, where `t_k = (5·3^{k−1} − 1)/2`.
  The extracted text of that condition is garbled. The reading given here is
  the only one that reproduces Thm 1's 40/21 at `k = 3`: it is where the
  `K_{k+1}`-star and tree densities cross. That is precise enough to test.
- **Applicability.** The caps are 1.905, 1.641 and 1.493 for `k = 3, 4, 5`.
  Our largest `α` is 1.30 (`n = 10`, `m = 20`), so the first branch applies
  everywhere.

**A limit curve [derived, not in the paper].** Thm 1 is a coarse threshold.
The dominating obstruction is the one-column generator of `K_{k+1}`: one
product with `k + 1` customers. At `p = x·p_k*` the number of such products is
asymptotically Poisson with mean `m·C(n, k+1)·p^{k+1} → x^{k+1}/(k+1)!`. If
every other obstruction generator has strictly larger α-density, so that
their counts vanish, then

`P(pw ≤ k − 1) → exp(−x^{k+1}/(k+1)!)`,

and the curve crosses 1/2 at `x = 2.02` (`k = 3`), 2.42 (`k = 4`) and 2.82
(`k = 5`). Lemma 5's proof suggests that uniqueness for `k = 3` but does not
state it. For `k ≥ 4` the curve is conditional on the conjecture too.

**A confound in our generator, and what was done.**
- `generate_random_instance` gives every empty row one random 1. A column
  patch adds no edges. So the certified instances are `R(n, m, p)` plus
  patches.
- At the threshold `p` the patch is large: 30–60% of rows are patched at
  `x₃ ≈ 1–2.5` (column `patched_row_frac` in the per-cell table).
- The patches join isolated customers to cliques and push `pw` up. This
  produces most of the lack of collapse seen in a first look. The certified
  instances give `P(pw ≤ 2) = 0.69 / 0.38 / 0.19` at `n = 10 / 20 / 35`
  (`m = n`, `x₃ = 1.78 / 2.12 / 2.13`). The unpatched matrices of the same
  cells give 0.91 / 0.69 / 0.69.
- We therefore regenerated the raw matrix (the first draw of the same
  `RandomState`) for every Bernoulli instance with `x₃ ≤ 8`, 9,848 in all.
  Its exact pathwidth was computed with `pathwidth_solver/`, all proved.
- **Check:** raw `pw ≤` certified `pw` on all 9,848, as it must be (subgraph).

**Findings** (`n = 10…75`, Bernoulli, `m ∈ {n, 2n}`;
`reports/figures/rig_ks_threshold.png`; top row raw, bottom row as generated):

1. **On the raw model the `k = 3` curves nearly collapse in `x = p/p₃*`, but
   to the right of the limit curve.** The interpolated `x₅₀` (where
   `P(pw ≤ 2) = 1/2`) is:

   | m | `x₅₀` across `n = 10…35` |
   |---|---|
   | `m = n` | 2.88, 2.64, 2.49, 2.89, 2.45, 2.57 |
   | `m = 2n` | 2.51, 2.36, 2.08, 2.23, 2.39 |

   There is no monotone trend in `n`. The interpolation is coarse: our `p`
   grid steps `x` by factors of 1.3–2. At `x = 2.5` the raw `P` is 0.47–0.64
   at `m = n` against a limit of 0.20.
2. **The shift is a slow finite-size correction, and it is computable.** Take
   the exact finite-`n` probability that no product has ≥ 4 customers,
   `P(Bin(n, p) ≤ 3)^m`. It puts `x₅₀` at:

   | `n` | 10 | 40 | 75 | 1,000 | 10,000 | limit |
   |---|---|---|---|---|---|---|
   | `x₅₀` (`m = n`) | 2.93 | 2.50 | 2.40 | 2.18 | 2.11 | 2.02 |

   The relative correction is of order `np = x·m^{−1/4}`
   (`(1 − p)^{n}` and `C(n,4)/n⁴` terms), so it decays like `n^{−1/4}`.
   **No experiment at `n ≤ 10⁴` would see the limit curve.** [derived]
3. **At `k = 3` the one-product clique is almost the whole story.**
   - At `m = n`, among raw instances where every product has ≤ 3 customers,
     `P(pw ≤ 2)` is 0.94–1.00 at `x₃ ≤ 2.5` for every `n ≤ 40`. So
     `P(pw ≤ 2) ≈ P(Bin(n,p) ≤ 3)^m` (lower-right panel, `k = 3` points on
     the diagonal).
   - At `m = 2n` the conditional share drops to 0.79–0.94 at `x₃ = 2`. Larger
     `α` brings the other obstructions closer, as the paper's 40/21 crossover
     says it should.
4. **At `k = 4, 5` the other obstructions matter at these sizes.** We cannot
   test the conjecture's asymptotics. At finite size:
   - Observed `x₅₀` is 2.3–3.5 (`k = 4`) and 2.2–3.9 (`k = 5`).
   - The one-product event alone predicts 3.1–3.8 and 3.7–4.7 at the same
     cells.
   - The conditional `P(pw ≤ k−1 | no product of size ≥ k+1)` is 0.65–1.0.
   - At `k = 5`, `m = n`, `n = 40`, the observed `x₅₀ = 2.70` is even *below*
     the conjectured limit's 2.82. The transition is driven by multi-product
     structure that the conjecture says must vanish asymptotically.

   So the data are **consistent with the conjecture's scaling `p ∝ m^{−1/(k+1)} n^{−1}`**:
   transitions at `x = O(1)` across a 7-fold range of `n`, and `p` at the
   transition falling like `n^{−5/4}` (`k = 3`). They **cannot confirm or
   refute** it. The largest tree obstruction has `t_5 = 202` vertices, beyond
   every `n` here.
5. **As generated, the certified data are a different model at sparse `p`.**
   Any use of `learning/data/ensemble` Bernoulli cells as "KSS random
   intersection graphs" below `p ≈ 3/m` should say so.

Size range: `n = 10–75`. Cells with transitions inside the grid exist only to
`n ≈ 40` for `k = 3` and to `n = 50` for `k = 4, 5`. Above that, our smallest
`p` (0.025) is already at `x > 3`.

### 2. Concentration: the standard deviation of `pw` grows, roughly like `n^{0.3–0.5}`

§12 established CV → 0. Here the question is the absolute spread, now through
`n = 75` (`reports/figures/rig_sd.png`). Fits are weighted by bootstrap
standard errors (400 resamples per cell) on `n ≥ 15`.

- **Bounded is rejected.** A constant `sd` fits with `χ²/dof` = 2.5–17
  (median ≈ 8) in every fixed-`d` series. Over `n = 15 → 75` the sd rises:

  | series | sd at `n = 15` | sd at `n = 75` |
  |---|---|---|
  | fixed `d = 3`, `m = n` | 0.57 | 0.96 |
  | fixed `d = 5`, `m = n` | 0.63 | 1.28 |
  | Bernoulli, peak over the grid | 1.2 | 2.4 |

- **√n and log n cannot be told apart.** Power-law exponents at fixed `d` are
  0.19–0.49 (± 0.05), median ≈ 0.33, ignoring `d ≥ 9`, whose small-`n` cells
  are near-complete graphs.
  - `a + b√n` and `a + b·log n` both fit with `χ²/dof` 0.25–3.0, below 1.5
    in 11 of the 15 series with `d ≤ 8`. Neither is consistently preferred.
  - Over 15–75, `√n` grows by 2.24× and `log n` by 1.59×. The observed growth
    (1.4–2.0×) sits between them.
- **Peak sd** (the largest cell sd at each `n`):
  - fixed generator: exponent 0.42 ± 0.04 (`m = n`), 0.37 ± 0.05 (`m = 2n`);
  - Bernoulli: 0.47 ± 0.05 and 0.49 ± 0.05, consistent with √n. `log n`
    fits as well (`χ²/dof` 0.51 / 0.28, against 0.50 / 0.72 for √n).
- **Part of the Bernoulli spread is the number of ones.** That count is itself
  `Bin(nm, p)` and has `√(nmp)` fluctuations. Within a cell, a linear
  regression on `n_ones` explains a median 37–62% of the variance of `pw`. The
  fixed generator fixes the number of ones, and its peak sd is about half the
  Bernoulli one (1.34 against 2.41 at `n = 75`).
- **Caveat.** The peak is a max over a coarse parameter grid, and the peak
  cell moves with `n`. Read it as an envelope, not a fit to one family.

**Speculative.** An Azuma-type bound (vertex exposure, `pw` 1-Lipschitz in
each customer's row) gives `sd = O(√n)`. The data are consistent with growth
at or a little below that rate. Nothing published states the variance for
any random graph model (survey §7(b) item 3).

### 3. `pw/n` against size-free density: no collapse at `n ≤ 75`

`reports/figures/rig_pw_over_n.png` plots mean `pw/n` against the MOSP graph's
mean degree (`g_deg_mean`) and against realised customers per product
(`col_mean`), per `n`, for both generators.

- **No collapse.** At every fixed mean degree `c`, `pw/n` *falls* with `n` from
  10 through 75, in both generators and both ratios. For example (fixed
  generator, `m = n`):

  | `c` | `pw/n` at `n = 20` | at `n = 40` | at `n = 75` |
  |---|---|---|---|
  | 4 | 0.253 | 0.188 | 0.154 |
  | 8 | 0.453 | 0.352 | 0.303 |

  This is the intercept of §12's linear law, `pw ≈ a + b·n` with `a > 0`, read
  as `pw/n = b + a/n`. Curves against `col_mean` do not collapse either: at
  equal `col_mean`, `m = 2n` has about twice the degree.
- **Evidence for a limit at fixed degree.** It is weak, and only in the sense
  that the data are consistent with one: `pw/n = a + b/n` fits every
  fixed-degree series. The extrapolated `a(c)`:

  | `c` | 3 | 4 | 6 | 8 | 12 | 16 |
  |---|---|---|---|---|---|---|
  | fixed, `m = n`, `a(c)` | 0.071 | 0.124 | 0.194 | 0.253 | 0.336 | 0.391 |
  | Bernoulli, `m = n`, `a(c)` | 0.053 | 0.086 | 0.152 | 0.204 | 0.283 | 0.345 |

  The `m = 2n` values are 0.03–0.06 higher. Formal standard errors are
  0.001–0.02, which **understates** the uncertainty: the `1/n` form is
  assumed, not tested. §14 showed that `n ≤ 40` constants fail at 125.
  Nothing here distinguishes a limit from slow drift. [speculative]
- **Against the Erdős–Rényi bounds at equal mean degree.**
  - Every RIG extrapolation `a(c)` sits inside the ER window
    `[LB, UB]` of the survey's §7(a) at `c ≤ 4`.
  - As `c` grows, more of the RIG extrapolations fall **below the ER whp
    lower bound** (the FM first moment) for `pw/n`:

    | `c` | series below the ER LB | ER LB | RIG `a(c)` |
    |---|---|---|---|
    | 6 | 1 of 4 | 0.171 | 0.152–0.250 |
    | 8 | 3 of 4 | 0.263 | 0.204–0.313 |
    | 12 | 4 of 4 | 0.397 | 0.283–0.395 |
    | 16 | 4 of 4 | 0.488 | 0.345–0.450 |

  - Measured values at `n = 75` (no extrapolation) are already below it for
    Bernoulli `m = n` at `c = 12` and 16 (0.371 against 0.397, 0.456 against
    0.488).
  - The ER bound is asymptotic, and finite-`n` ER values sit above their
    limit. Gogate–Dechter's tw/n falls from `n = 25` to 50, so the comparison
    at equal finite `n` (next bullet) is the cleaner one.
  - This is not a contradiction. The RIG is a different, clustered model: a
    product of size `s` spends `s(s−1)/2` edges on a clique whose width cost
    is one bag. So equal mean degree buys less pathwidth than in `G(n, c/n)`.
  - It does say that **mean degree is not the right size-free coordinate for
    comparing RIGs with ER.** A clustering-corrected degree, such as the
    number of distinct products per customer times `col_mean − 1`, would be
    the natural next try.
  - **At equal `n` and equal `c`, ER treewidth exceeds RIG pathwidth** for
    every `c ≥ 4` where Gogate–Dechter have exact ER treewidths (`n = 25, 50`;
    red crosses). Since `tw ≤ pw`, ER pathwidth is larger still. Examples:
    - `c = 8`, `n = 50`: ER tw/n 0.407 against RIG pw/n 0.29–0.39;
    - `c = 12`, `n = 50`: 0.552 against 0.41–0.50;
    - `c = 4`, `n = 25`: 0.252 against 0.20–0.26.

    At `c = 2` the order reverses: ER tw/n 0.072 at `n = 50`, RIG pw/n 0.09–0.10
    at `n = 40`. RIGs at low degree have small dense cliques, so they have
    larger width per vertex.

Size range: `n = 10–75`. Mean degree 0.6–70. All conclusions are finite-size
statements.

### 4. Pathwidth − treewidth, exact

**What was computed, and what was already stored.**
- Exact treewidth existed only for corpus instances
  (`learning/data/ensemble/extremal_corpus_tw.csv`, §21) and for small
  enumerated graphs (`pwtw_census.csv`, §27). The ensemble had only the
  min-fill and min-degree heuristics, so it was computed here.
- **Method** (`learning/treewidth.py`, per connected component):
  - a component that is a clique has `tw = s − 1`;
  - components of ≤ 20 vertices use the subset DP;
  - larger ones use the decision search from the MMD lower bound to the
    min-fill upper bound. It never uses `pw`, so `tw ≤ pw` is a real check.
  - A censored search at ≤ 26 vertices falls back to the DP.
  - Every elimination ordering is re-verified in Python.
- **Cost: 13.2 core-hours**, over the ~10 asked for:
  - 4.6 core-hours for 37,800 instances at a 5 M-node budget per call;
  - 3.5 for a retry of the 429 censored ones at 50 M nodes and 300 s, which
    closed 218 and was then stopped;
  - 5.1 for the 1,500 instances at `n = 50`, against an estimate of ~2.5 from
    a 15-instance sample.
  - `n = 60` was skipped on cost (sample: 10 s per instance, a third
    censored), and the `n = 50` stragglers were not retried.
- **Coverage, exact:**

  | `n` | exact | of | cells with every instance exact |
  |---|---|---|---|
  | 10–35 | every instance | 32,400 | all |
  | 40 | 5,153 | 5,400 | 29 of 36 |
  | 50 | 995 | 1,500 | 18 of 30 |

  Censoring is **not** random. It falls on the ridge cells (fixed `d = 2–5`,
  Bernoulli `p = 0.05–0.1`). Hence two rules: per-cell statistics below use
  only fully exact cells, and pooled shares give the interval from the
  censored rows: "certain gap" when `pw > tw_hi`, "possible gap" when
  `pw > tw_lo`.
- **Sanity:** `tw ≤ pw` on all 39,300 instances, censored rows included
  (`tw_lo ≤ pw`). Every ordering re-verified. No violation.

**Findings** (`n = 10–50`; `reports/figures/rig_pw_minus_tw.png`):

1. **`pw − tw ∈ {0, 1, 2}` on every instance; never 3.** Over the 38,548
   instances with exact treewidth, the counts of `pw − tw = 2` are 0, 2, 5, 6,
   17, 25, 19 and 8 at `n = 10, 15, …, 40, 50`. No censored instance has a
   certain gap above 2. This agrees with the census of every graph to 11
   vertices (§27: no graph with `pw − tw = 3`), now on random graphs to 50
   vertices. **It is not a bound.** It says that on these models a gap of 3
   has frequency below about 1 in 13,000 (95%, rule of three).
2. **`P(pw > tw)` grows with `n`.** Pooled over the grid it is 2.2%, 6.2%,
   10.8%, 13.3%, 15.1% and 15.9% at `n = 10–35`, all exact. At `n = 40` it is
   between 16.2% and 20.5%; at `n = 50`, between 13.1% and 45.1%, because the
   censoring is too heavy to say more there. The pooled figure depends on the
   grid. The clean statement is at fixed density, the fixed generator at
   `d = 2`, `m = n` (`col_mean` ≈ 2.1). That cell is exact at every `n`:

   | `n` | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 50 |
   |---|---|---|---|---|---|---|---|---|
   | `P(pw > tw)` | 0.07 | 0.17 | 0.39 | 0.41 | 0.53 | 0.67 | 0.64 | 0.70 |

   150 instances per cell (50 at `n = 50`), standard error about 0.04 (0.07).
   The other fully exact sparse series rise the same way. Bernoulli
   `p = 0.05`, `m = n`, goes 0 → 0.72 by `n = 40`, but its density rises with
   `n`.
3. **The gap concentrates at two to three customers per product, the hardness
   ridge.** By `col_mean` band, pooled over `n`:

   | `col_mean` | ≤ 1.5 | 1.5–2 | 2–2.5 | 2.5–3 | 3–4 | 4–6 | 6–10 | > 10 |
   |---|---|---|---|---|---|---|---|---|
   | mean gap | 0.04 | 0.17 | **0.40** | 0.26 | 0.20 | 0.09 | 0.04 | 0.004 |

   In the 2–2.5 band, `P(pw > tw)` over exact rows rises with `n` from 0.07
   (`n = 10`) to 0.57 (35) and 0.59 (40). The cell with the highest `P(pw > tw)`
   sits at `col_mean` 2.1–2.6 for every `n ≥ 20`. Its `P` is 0.39, 0.47, 0.59,
   0.67, 0.72 at `n = 20, 25, 30, 35, 40`.
   - At fixed middle density (fixed `d = 4–6`) the share rises to about 0.2
     by `n = 25–30` and then stops rising through 40.
   - The dense cells (`d ≥ 8`) start at 0 and creep to 0.05–0.15.

   Whether the middle-density plateau is real or a finite-size pause cannot
   be told at `n ≤ 40`.
4. **The min-fill bracket of §12 hid a third of the gaps.** §12 could certify
   `pw > tw` only through `optimum − (tw_min_fill + 1) > 0` and found the
   share "flat at about 10% from 25 to 40". With exact treewidth:

   | `n` | min-fill certified | exact |
   |---|---|---|
   | 30 | 11.2% | 15.1% |
   | 35 | 10.1% | 15.9% |
   | 40 | 10.5% | 16.2–20.5% |

   So §12's flat share was an artefact of the heuristic's growing slack. The
   true share keeps growing, at least to 40.
5. **The largest gaps** (`pw − tw = 2`) are mostly sparse instances near the
   ridge. Examples:
   - `ens_f_n50_m50_d2_i043`: `pw = 4`, `tw = 2`, mean degree 2.2;
   - Bernoulli `p = 0.05` at `n = 50`: `pw = 12`, `tw = 10`;
   - Bernoulli `p = 0.025`, `m = 2n` at `n = 50`: `pw = 6`, `tw = 4`.

   In the Bernoulli `p = 0.05`, `m = n` cell at `n = 40`, 7.3% of instances
   have gap 2.

**Reading, marked speculative.** For sparse RIGs the gap behaves like a
"local obstruction count": it is present more and more often as `n` grows
at fixed density. That is what one expects if it comes from small tree-like
pieces (the 10-vertex `pw − tw = 2` graphs of §21/§27 are three `K₄`s on hubs
with pendants), whose number grows linearly in `n`. For `G(n, c/n)` the survey
(§2) derives an unbounded subcritical gap, and nothing is known in the linear
regime. Here, at `n ≤ 50`, the gap is unbounded in neither sense: it is 0, 1
or 2 throughout. What grows is its frequency.

Regenerate:

```bash
nice -n 19 python -m learning.rig_pathwidth treewidth --workers 8                     # n <= 40, ~35 min wall at 8 workers
nice -n 19 python -m learning.rig_pathwidth treewidth --workers 8 --retry --deadline 300 --budget 50000000
nice -n 19 python -m learning.rig_pathwidth treewidth --workers 8 --upward --nmax 50
python -m learning.rig_pathwidth analyse
```

---

## Caveats

- **Finite size.** Every number is for `n ≤ 75` (`n ≤ 50` for treewidth).
  `n ≤ 75` says nothing direct about limits. The survey §7(b) lists what such
  data can and cannot inform, and §14 of `ml_nature.md` is the project's own
  record of constants that failed out of range.
- **Two generators, neither exactly KSS.** The Bernoulli generator patches
  empty rows. §1 uses the unpatched matrices. §§2–4 use the certified
  instances as generated, so read their Bernoulli cells at small `p` as a
  patched model. The fixed generator is Chu & Stuckey's, not KSS.
- **The `p` grid is coarse** (9 values per series at `n ≤ 40`, 6 at 50–75).
  Interpolated quantities (`x₅₀`, `pw/n` at fixed `c`) carry interpolation
  error comparable to the effects at the second decimal.
- **A bug found in passing, not fixed.** `fixed_parameter_algorithm/pathwidth_fpt.compute_pathwidth_fpt`
  returns pathwidth 1 for *any* tree with more than 18 vertices. It removes
  pendant vertices, then treats an empty core as width 1. For example,
  `nx.balanced_tree(3, 3)` (40 vertices, pathwidth 3) gets 1. Pendant removal
  is not pathwidth-preserving in general (`S(K₁,₃)` has pathwidth 2). It was
  not used here. Any pathwidth value it produced above 18 vertices is suspect
  as a *lower* value. `customer_inter/` still turns its orderings into MOSP
  values by simulation, so those values are unaffected.
