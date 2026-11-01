# The excess phase diagram of MOSP

*Ralph loop0010, executing `reports/excess_phase_plan.md`. One section per
item; each states its size range, its regenerate command, its kill verdict
and what it does not claim. The parameter throughout is the excess
`e = (n_ones − m) / n`, the mean number of patterns per customer minus one,
always realised from the matrix and never the generator's nominal value.*

## 1. The map: every instance on record placed by its excess (item 01, 2026-10-31)

**Question.** Where does every instance we hold sit in the excess, how far is
each from an incidence forest, and do the three lines on record — the giant
component of the incidence graph at `e_g(r) = (√(r² + 4r) − r) / 2`, the
first-moment threshold `e = 1`, and the hardness ridge at `e ≈ 2–2.4` —
separate the collections?

**What was done.** `learning/excess.py` computes, for every instance from
its matrix, `n`, `m`, `n_ones`, `e`, `r = m / n`, `c = n_ones / m`, the
customer–pattern incidence graph `B`'s component count `κ`, its cyclomatic
number `γ = n_ones − n − m + κ` and `γ / n`, its largest component as a
fraction of its `n + m` vertices and of its `n` customers, the forest flag
`γ = 0`, and the (2, 2)-core of `B` (`learning.cover_excess.peel`) as a
fraction of the customers, the patterns and the vertices; and joins the
certified optimum where there is one. Three sources, 64,291 rows:

| source | rows | size range | how the matrix was obtained |
|---|---|---|---|
| corpus | 6,376 | 9–134 customers, 10–125 patterns | read from `benchmarks/instances/`, joined to `learning/data/instances.csv` for the certified optimum (all 6,376 certified) |
| ensembles | 50,715 | 10–100 customers, `m / n` from ⅛ to 8 | regenerated from the seed with `learning.ensemble.generate(Cell.parse(...), index)` for every row of `results.csv` (37,800), `results_upward.csv` (6,785, finish file applied), `results_ratio.csv` (2,750), `results_height.csv` (3,380); the regenerated `n_ones` is asserted equal to the recorded one on every row, and was |
| simulations | 7,200 | 30 and 40 customers, `m = n`, `d ∈ {2, 4, 6, 8, 10}` | regenerated from the seed with the scratch generator `bern_padC1_padP2_conn` of `reports/scratch/clique_cover_moment/gen_candidates.py`; the recorded `ones` asserted equal, and was |

Nothing was solved; no file under `solutions/` was read or written. Two
identities are checked on all 64,291 rows: `e = r (c − 1)` to 7 × 10⁻¹⁵ and
`γ / n = e − 1 + κ / n` to 1.4 × 10⁻¹⁴; and on every row the (2, 2)-core is
empty exactly when `γ = 0` (asserted inside `incidence_stats`, two
independent computations of the same fact).

**Regenerate.** `python -m learning.excess` (build, tables and figure; 4 s
wall on 8 workers at nice 19, 23 CPU-seconds) writes
`learning/data/excess.csv` (64,291 rows, 15.1 MB, git-ignored under
`learning/data/*`), prints every table below, and draws
`reports/figures/excess_giant_component.png`. Stages: `--stage build`,
`--stage tables`, `--stage figure`. Tests: `python -m pytest
tests/test_excess.py -q` (8 tests: `e`, `γ`, `κ` by hand on a path, a
4-cycle with a pendant and a two-component graph; `e = r (c − 1)` and
`γ / n = e − 1 + κ / n` on random matrices; the thresholds; the crossing
interpolation on a synthetic series).

### 1.1 Findings

1. **The corpus holds no forest regime.** Of 6,376 corpus instances, 0 sit
   below `e_g(r)`, 12 sit in `[e_g(r), 1)` (9 Faggioli–Bentivoglio, 1 SCOOP,
   2 Simonis), and exactly 2 are incidence forests (`HS problem 5 size 10 10
   density 0.20`, Simonis, and `p1050n3_0`, Faggioli–Bentivoglio). Every
   other instance has `γ ≥ 1`; `e ≥ 1` forces `γ = n (e − 1) + κ ≥ 1`
   outright, which is where 99.8% of the corpus sits. A forest theorem
   (items 03, 06) would describe none of the benchmark instances directly;
   its use is as the base of the sparse flank, not as a description of
   anything we hold.

2. **Industry sits between the threshold and the ridge; the benchmark
   generators mostly do not.** SCOOP: 24 instances, `e` from 0.97 to 2.50,
   median 1.35, 19 of 24 in `[1, 2)`, 3 in `[2, 2.4]`, 1 above; 10 of the 24
   decompose (`κ > 1`), none is a forest, and their median `γ / n` is 0.37.
   Faggioli–Bentivoglio: median 1.98, quartiles 1.38–3.12, 48% in `[1, 2)`
   and 40% above 2.4. Harvey (median 4.5), Simonis (5.15), Shaw (5 exactly),
   Wilson and Challenge (5–6.6 medians, up to 84.7) sit far above the
   ridge: 80% of Harvey, 88% of Simonis and 95–100% of Shaw, Wilson, Miller and Challenge are above 2.4. The corpus as a whole: median 4.87,
   only 9.4% in `[1, 2)` and 7.8% in `[2, 2.4]`.

3. **Chu & Stuckey by class, realised.** With `m = n`: `d = 2` has `e` in
   1.48–2.02 (median 1.76), `d = 4` in 2.83–3.73 (median 3.24), `d = 6` in
   4.33–5.68, `d = 8` in 6.32–8.16, `d = 10` in 7.97–10.2. The ridge at
   2–2.4 falls between the `d = 2` and `d = 4` classes, as §0 of the plan
   says and as the paper's Appendix E does not yet; the 125 × 125 `d = 2`
   class is at 1.66–1.78 and `d = 4` at 2.94–3.38 (full table below). The
   half-ratio classes `Random-n-n/2-d` sit lower in `e` (`Random-100-50-2`: 1.15–1.39, `Random-100-50-4`: 1.73–1.96) and the double-ratio ones higher (`Random-50-100-2`: 3.02–3.44), because
   `e = r (c − 1)` scales with `r`. No Chu & Stuckey instance decomposes
   (their generator discards those), none is a forest, and their 2-core
   holds 93% of the customers on average.

4. **The ensembles cover the sparse flank that the corpus lacks**, but
   thinly at `n ≥ 50`: 3,127 ensemble instances sit below `e_g(r)` (all
   Bernoulli, 2,504 of them at `n ≤ 25`, 6 at `n ≥ 50`), 2,095 in
   `[e_g(r), 1)`, and 3,446 are forests (1,093 at `n = 10` falling to 66 at
   `n = 75`, none at 100). The fixed-size generator never goes below
   `e_g(r)`: its padding of empty customers lifts the realised `e` to at
   least 0.85 even at `d = 2`, `m = n / 2`.

5. **Is `e < e_g(r)` the forest regime?** Across the line the forest share
   falls from 0.92 (`n` 10–25), 0.74 (30–40) and 0.67 (50–75, six
   instances) below `e_g(r)` to 0.23–0.40 in `[e_g(r), 1)`, with median `γ`
   going from 0 to 1–2; at `e ≥ 1` there are no forests at all, as the
   identity forces. So `e_g(r)` separates "mostly forests" from "a few
   cycles", and `e = 1` separates "a few cycles" from "none". At finite `n`
   a random graph below its giant threshold still carries O(1) cycles, so
   a forest share below one there is what the theory expects, not a
   failure of the line. The 355 non-forests below `e_g(r)` are all
   Bernoulli at `r = n` and `2n`, where the plan's fixed-size form of
   `e_g` is not the Bernoulli threshold (Poisson sizes give `√r − r`, zero
   at `r = 1`).

6. **The stated check is not met.** The largest component of `B` reaches
   one half of the vertices on five observable series at `n ≥ 50`, at
   `e` = 0.83–0.93, which is 0.21–0.43 above `e_g(r)` on every one (tolerance
   ±0.15); the other 30 series have every cell above one half and cannot
   test it. The reason is in the criterion, not the line: at the
   branching-factor-one point the giant component is a vanishing fraction
   by definition and grows continuously from there (in `G(n, c/n)` the half
   point is at `c = 1.386`, 39% above the threshold), so a half-crossing
   can never sit *at* `e_g(r)`; and the ensemble grid is coarse there (the
   straddling cells are 0.4–0.9 apart in `e`), so the interpolated
   crossing is itself uncertain by a few tenths. The generators' padded
   degree distributions move the configuration-model threshold down, not
   up (`e_g repaired` in the table: 0.48 at `r = n / 2`, 0.49 at `r = n`,
   against 0.50 and 0.62; values of 0 are the bisection's floor at
   `col_mean = 1`). **Consequence for the loop, as the item prescribes:
   `e_g(r)` is not to be used later as the point where the largest
   component is one half.** What the data do support about it is finding
   5: it is where forests stop being the majority. Items 06 and 11 should
   state the random corollary for `e` below `e_g(r)` with that meaning and
   with the finite-`n` caveat, or avoid the line.

7. **The 338 bound-gap instances of §6 are the sparse ones at their size.**
   Among the 229 with at least five corpus peers at equal `(n, m)`, the
   median gap instance's `e` sits at the 7th percentile of its cell
   (quartiles 1st–17th) and 97.4% are below their cell's median `e`; the
   same for `γ / n`. Their `e` runs 1.44–4.06 (deciles), median 2.05, with
   41% in `[1, 2)` against 7.6% of the rest of the corpus, 18% in `[2, 2.4]`
   and 41% above; none is a forest, none is below 1. In the cells that mix
   collections the contrast is large: `(30, 10)` 2.17 against 4.07, `(30,
   30)` 2.0 against 8.0, `(40, 20)` 1.45 against 8.62, `(100, 100)` 3.85
   against 53.3. Where the gap instances are the whole cell (the
   Faggioli–Bentivoglio `(40–50, 25–40)` cells, three SCOOP instances) the
   comparison is empty. This is consistent with §6's reading, "connected
   and sparse", in one parameter.

8. **The simulations reproduce the corpus classes they imitate.** The
   7,200 `bern_padC1_padP2_conn` instances at `m = n` have `e` medians 1.6
   (`d = 2`), 3.1, 5.0, 7.0, 9.0 against the Chu & Stuckey `m = n` medians
   1.76, 3.24, 5.11, 7.15, 9.04: within 0.1–0.16 at every `d`, all
   connected, none a forest.

### 1.2 Kill verdict

None (descriptive). The one stated check — the largest-component fraction
of `B` crosses one half within ±0.15 in `e` of `e_g(r)` on every ensemble
series at `n ≥ 50` — is **not met** on all five series where it is
observable (deltas +0.21 to +0.43) and unobservable on the other 30.
Finding 6 says why the criterion could not have been met and what `e_g(r)`
does separate.

### 1.3 What this does not claim

Nothing about the optimum, nor about hardness: the map is a description of
the instances we happen to hold and of where they sit against three lines
whose meaning is established elsewhere. The crossing check uses cell means
on a coarse grid at `n = 50–100`, interpolated linearly, and the repaired
thresholds come from a configuration model of the generators, not from the
generators. The percentile statement about the bound-gap instances is a
within-cell comparison with no claim of cause. 24 SCOOP instances are 24
instances.

### 1.4 Figure

![largest component of B against e, per product ratio](figures/excess_giant_component.png)

*The mean largest-component fraction of `B` per ensemble cell against the
cell's median `e`, one line per `(generator, n)` at `n ≥ 50` (paler =
smaller `n`), one panel per product ratio `r`; dashed vertical `e_g(r)`,
grey vertical `e = 1`, dotted horizontal one half. `python -m
learning.excess --stage figure`.*

### 1.5 Tables, in full

`python -m learning.excess --stage tables`. The per-series table (526
series) is folded; open it to read.

Rows: 64291 (corpus 6376, ensemble 50715, simulation 7200); max |e − r(c − 1)| = 7.1e-15; max |γ/n − (e − 1 + κ/n)| = 1.4e-14.

#### The three lines, by source

| source     |   count |   forest |   e < e_g(r) |   e_g(r) <= e < 1 |   1 <= e < 2 |   2 <= e <= 2.4 |   e > 2.4 |   forests with e >= e_g(r) |   non-forests with e < e_g(r) |
|:-----------|--------:|---------:|-------------:|------------------:|-------------:|----------------:|----------:|---------------------------:|------------------------------:|
| corpus     |    6376 |        2 |            0 |                12 |          599 |             500 |      5265 |                          2 |                             0 |
| ensemble   |   50715 |     3446 |         3127 |              2095 |         6882 |            4634 |     33977 |                        674 |                           355 |
| simulation |    7200 |        0 |            0 |                 0 |         1982 |              33 |      5185 |                          0 |                             0 |

#### Is e < e_g(r) the forest regime? The ensembles by generator and size band

| generator   | n     |   count e < e_g |   forest share e < e_g |   median gamma e < e_g |   count e_g <= e < 1 |   forest share e_g <= e < 1 |   median gamma e_g <= e < 1 |   count e >= 1 |   forest share e >= 1 |
|:------------|:------|----------------:|-----------------------:|-----------------------:|---------------------:|----------------------------:|----------------------------:|---------------:|----------------------:|
| bernoulli   | 10-25 |            2504 |                  0.924 |                      0 |                  973 |                       0.314 |                           1 |           7323 |                     0 |
| bernoulli   | 30-40 |             617 |                  0.736 |                      0 |                  440 |                       0.232 |                           2 |           7393 |                     0 |
| bernoulli   | 50-75 |               6 |                  0.667 |                      0 |                  358 |                       0.38  |                           1 |           5636 |                     0 |
| bernoulli   | 100   |               0 |                nan     |                    nan |                    0 |                     nan     |                         nan |            270 |                     0 |
| fixed       | 10-25 |               0 |                nan     |                    nan |                    0 |                     nan     |                         nan |          10800 |                     0 |
| fixed       | 30-40 |               0 |                nan     |                    nan |                    0 |                     nan     |                         nan |           8100 |                     0 |
| fixed       | 50-75 |               0 |                nan     |                    nan |                  324 |                       0.401 |                           1 |           5576 |                     0 |
| fixed       | 100   |               0 |                nan     |                    nan |                    0 |                     nan     |                         nan |            395 |                     0 |

#### Per collection

| collection           |   count | n range   | m range   |   e min |   e q10 |   e q25 |   e median |   e q75 |   e q90 |   e max |   gamma/n q10 |   gamma/n median |   gamma/n q90 |   forest share |   2-core cust share |   lcc frac |   below e_g |   below 1 |   in [1, 2) |   in [2, 2.4] |   above 2.4 |
|:---------------------|--------:|:----------|:----------|--------:|--------:|--------:|-----------:|--------:|--------:|--------:|--------------:|-----------------:|--------------:|---------------:|--------------------:|-----------:|------------:|----------:|------------:|--------------:|------------:|
| SCOOP                |      24 | 13-134    | 10-49     |   0.968 |    1.13 |    1.21 |       1.35 |    1.83 |    2.05 |    2.5  |         0.164 |            0.373 |         1.11  |       0        |               0.536 |      0.92  |           0 |  0.0417   |      0.792  |        0.125  |      0.0417 |
| Faggioli-Bentivoglio |     300 | 9-50      | 10-40     |   0.94  |    1.1  |    1.38 |       1.98 |    3.12 |    4.9  |    8.7  |         0.133 |            1     |         4     |       0.00333  |               0.68  |      0.982 |           0 |  0.03     |      0.477  |        0.09   |      0.403  |
| Chu & Stuckey        |     200 | 30-125    | 30-125    |   1.15  |    1.75 |    3.04 |       5.02 |    7.28 |    9.24 |   18.6  |         0.766 |            4.04  |         8.24  |       0        |               0.929 |      1     |           0 |  0        |      0.19   |        0.01   |      0.8    |
| Random-30-30-2       |       5 | 30-30     | 30-30     |   1.63  |    1.66 |    1.7  |       1.7  |    1.73 |    1.77 |    1.8  |         0.693 |            0.733 |         0.807 |       0        |               0.753 |      1     |           0 |  0        |      1      |        0      |      0      |
| Random-30-30-4       |       5 | 30-30     | 30-30     |   2.83  |    2.95 |    3.13 |       3.2  |    3.37 |    3.59 |    3.73 |         1.99  |            2.23  |         2.62  |       0        |               0.927 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-30-30-6       |       5 | 30-30     | 30-30     |   4.33  |    4.37 |    4.43 |       4.97 |    5.07 |    5.39 |    5.6  |         3.41  |            4     |         4.42  |       0        |               0.967 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-30-30-8       |       5 | 30-30     | 30-30     |   6.37  |    6.47 |    6.63 |       6.83 |    7.07 |    7.17 |    7.23 |         5.51  |            5.87  |         6.2   |       0        |               0.987 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-30-30-10      |       5 | 30-30     | 30-30     |   7.97  |    8.33 |    8.87 |       8.93 |    8.93 |    9.31 |    9.57 |         7.36  |            7.97  |         8.35  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-40-40-2       |       5 | 40-40     | 40-40     |   1.48  |    1.56 |    1.7  |       1.8  |    1.93 |    1.97 |    2    |         0.59  |            0.825 |         0.995 |       0        |               0.76  |      1     |           0 |  0        |      0.8    |        0.2    |      0      |
| Random-40-40-4       |       5 | 40-40     | 40-40     |   3.1   |    3.11 |    3.12 |       3.25 |    3.27 |    3.32 |    3.35 |         2.13  |            2.27  |         2.34  |       0        |               0.935 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-40-40-6       |       5 | 40-40     | 40-40     |   4.72  |    4.76 |    4.83 |       4.92 |    5.15 |    5.17 |    5.17 |         3.79  |            3.95  |         4.19  |       0        |               0.995 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-40-40-8       |       5 | 40-40     | 40-40     |   6.53  |    6.63 |    6.8  |       6.97 |    7.2  |    7.21 |    7.22 |         5.66  |            6     |         6.24  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-40-40-10      |       5 | 40-40     | 40-40     |   8.32  |    8.55 |    8.9  |       8.9  |    8.97 |    8.99 |    9    |         7.58  |            7.92  |         8.02  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-50-2       |       5 | 50-50     | 50-50     |   1.66  |    1.71 |    1.78 |       1.78 |    1.98 |    2    |    2.02 |         0.728 |            0.8   |         1.02  |       0        |               0.82  |      1     |           0 |  0        |      0.8    |        0.2    |      0      |
| Random-50-50-4       |       5 | 50-50     | 50-50     |   3.14  |    3.16 |    3.18 |       3.28 |    3.62 |    3.63 |    3.64 |         2.18  |            2.3   |         2.65  |       0        |               0.952 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-50-6       |       5 | 50-50     | 50-50     |   4.9   |    4.94 |    5    |       5.34 |    5.38 |    5.56 |    5.68 |         3.96  |            4.36  |         4.58  |       0        |               0.984 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-50-8       |       5 | 50-50     | 50-50     |   6.8   |    6.82 |    6.86 |       7.2  |    7.36 |    7.84 |    8.16 |         5.84  |            6.22  |         6.86  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-50-10      |       5 | 50-50     | 50-50     |   8.66  |    8.81 |    9.04 |       9.08 |    9.18 |    9.79 |   10.2  |         7.83  |            8.1   |         8.81  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-100-2      |       5 | 50-50     | 100-100   |   3.02  |    3.02 |    3.02 |       3.14 |    3.34 |    3.4  |    3.44 |         2.04  |            2.16  |         2.42  |       0        |               0.964 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-100-4      |       5 | 50-50     | 100-100   |   6     |    6.06 |    6.16 |       6.36 |    6.52 |    6.59 |    6.64 |         5.08  |            5.38  |         5.61  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-100-6      |       5 | 50-50     | 100-100   |   9.18  |    9.61 |   10.3  |      10.3  |   10.3  |   10.5  |   10.6  |         8.63  |            9.34  |         9.53  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-100-8      |       5 | 50-50     | 100-100   |  13.4   |   13.6  |   13.8  |      13.8  |   14.2  |   14.5  |   14.7  |        12.6   |           12.9   |        13.5   |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-50-100-10     |       5 | 50-50     | 100-100   |  17.5   |   17.5  |   17.6  |      18    |   18.3  |   18.5  |   18.6  |        16.6   |           17     |        17.5   |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-75-75-2       |       5 | 75-75     | 75-75     |   1.56  |    1.63 |    1.75 |       1.87 |    1.88 |    1.9  |    1.92 |         0.648 |            0.88  |         0.917 |       0        |               0.803 |      1     |           0 |  0        |      1      |        0      |      0      |
| Random-75-75-4       |       5 | 75-75     | 75-75     |   3.03  |    3.03 |    3.04 |       3.24 |    3.43 |    3.48 |    3.52 |         2.05  |            2.25  |         2.5   |       0        |               0.933 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-75-75-6       |       5 | 75-75     | 75-75     |   5.04  |    5.05 |    5.07 |       5.12 |    5.19 |    5.37 |    5.49 |         4.06  |            4.13  |         4.38  |       0        |               0.995 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-75-75-8       |       5 | 75-75     | 75-75     |   7.03  |    7.1  |    7.2  |       7.24 |    7.25 |    7.44 |    7.56 |         6.11  |            6.25  |         6.45  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-75-75-10      |       5 | 75-75     | 75-75     |   8.67  |    8.82 |    9.04 |       9.08 |    9.2  |    9.31 |    9.39 |         7.83  |            8.09  |         8.33  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-50-2      |       5 | 100-100   | 50-50     |   1.15  |    1.17 |    1.2  |       1.22 |    1.26 |    1.34 |    1.39 |         0.18  |            0.23  |         0.348 |       0        |               0.444 |      1     |           0 |  0        |      1      |        0      |      0      |
| Random-100-50-4      |       5 | 100-100   | 50-50     |   1.73  |    1.75 |    1.79 |       1.85 |    1.93 |    1.95 |    1.96 |         0.764 |            0.86  |         0.958 |       0        |               0.728 |      1     |           0 |  0        |      1      |        0      |      0      |
| Random-100-50-6      |       5 | 100-100   | 50-50     |   2.44  |    2.52 |    2.64 |       2.82 |    2.88 |    2.92 |    2.95 |         1.53  |            1.83  |         1.93  |       0        |               0.888 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-50-8      |       5 | 100-100   | 50-50     |   3.38  |    3.41 |    3.45 |       3.67 |    3.72 |    3.82 |    3.88 |         2.42  |            2.68  |         2.83  |       0        |               0.944 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-50-10     |       5 | 100-100   | 50-50     |   4.2   |    4.34 |    4.56 |       4.68 |    4.7  |    4.73 |    4.75 |         3.35  |            3.69  |         3.74  |       0        |               0.98  |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-100-2     |       5 | 100-100   | 100-100   |   1.57  |    1.61 |    1.67 |       1.75 |    1.82 |    1.87 |    1.91 |         0.62  |            0.76  |         0.884 |       0        |               0.762 |      1     |           0 |  0        |      1      |        0      |      0      |
| Random-100-100-4     |       5 | 100-100   | 100-100   |   3.09  |    3.11 |    3.13 |       3.18 |    3.29 |    3.48 |    3.6  |         2.12  |            2.19  |         2.49  |       0        |               0.936 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-100-6     |       5 | 100-100   | 100-100   |   4.9   |    4.98 |    5.09 |       5.17 |    5.19 |    5.36 |    5.47 |         3.99  |            4.18  |         4.37  |       0        |               0.988 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-100-8     |       5 | 100-100   | 100-100   |   6.88  |    6.92 |    6.97 |       7.13 |    7.17 |    7.29 |    7.37 |         5.93  |            6.14  |         6.3   |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-100-100-10    |       5 | 100-100   | 100-100   |   8.54  |    8.72 |    8.99 |       9.18 |    9.35 |    9.41 |    9.45 |         7.73  |            8.19  |         8.42  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-125-125-2     |       5 | 125-125   | 125-125   |   1.66  |    1.66 |    1.66 |       1.73 |    1.77 |    1.78 |    1.78 |         0.664 |            0.736 |         0.786 |       0        |               0.774 |      1     |           0 |  0        |      1      |        0      |      0      |
| Random-125-125-4     |       5 | 125-125   | 125-125   |   2.94  |    3    |    3.09 |       3.29 |    3.32 |    3.36 |    3.38 |         2.01  |            2.3   |         2.37  |       0        |               0.946 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-125-125-6     |       5 | 125-125   | 125-125   |   4.7   |    4.85 |    5.09 |       5.13 |    5.24 |    5.25 |    5.26 |         3.86  |            4.14  |         4.26  |       0        |               0.992 |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-125-125-8     |       5 | 125-125   | 125-125   |   6.32  |    6.6  |    7.01 |       7.18 |    7.22 |    7.3  |    7.34 |         5.6   |            6.19  |         6.3   |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Random-125-125-10    |       5 | 125-125   | 125-125   |   8.22  |    8.54 |    9.03 |       9.18 |    9.22 |    9.32 |    9.38 |         7.55  |            8.18  |         8.32  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Harvey               |    2130 | 10-30     | 10-30     |   1     |    2    |    3    |       4.5  |    7    |   10    |   14    |         1.03  |            3.53  |         9.1   |       0        |               0.956 |      0.991 |           0 |  0        |      0.0986 |        0.103  |      0.798  |
| Simonis              |    3630 | 10-40     | 10-30     |   0.7   |    2.3  |    3.4  |       5.15 |    7.63 |   10.8  |   20.8  |         1.4   |            4.2   |         9.8   |       0.000275 |               0.961 |      0.999 |           0 |  0.000551 |      0.0515 |        0.0683 |      0.88   |
| Shaw                 |      25 | 20-20     | 20-20     |   5     |    5    |    5    |       5    |    5    |    5    |    5    |         4.05  |            4.05  |         4.05  |       0        |               0.978 |      1     |           0 |  0        |      0      |        0      |      1      |
| Wilson               |      20 | 10-100    | 20-100    |   1.6   |    2.49 |    3.71 |       6.61 |   33.6  |   66.2  |   84.7  |         1.58  |            5.67  |        65.2   |       0        |               0.968 |      0.999 |           0 |  0        |      0.05   |        0      |      0.95   |
| Miller               |       1 | 20-20     | 40-40     |   6     |    6    |    6    |       6    |    6    |    6    |    6    |         5.05  |            5.05  |         5.05  |       0        |               1     |      1     |           0 |  0        |      0      |        0      |      1      |
| Challenge            |      46 | 10-100    | 20-100    |   1.6   |    3.58 |    5    |       5    |    6.11 |   35.5  |   84.7  |         2.63  |            4.05  |        34.6   |       0        |               0.974 |      1     |           0 |  0        |      0.0217 |        0      |      0.978  |
| corpus, all          |    6376 | 9-134     | 10-125    |   0.7   |    2    |    3    |       4.87 |    7.17 |   10.4  |   84.7  |         1.03  |            3.9   |         9.5   |       0.000314 |               0.944 |      0.995 |           0 |  0.00188  |      0.0939 |        0.0784 |      0.826  |

#### The stated check: where the largest component of B crosses one half, against e_g(r)

| generator   | r   |   n |   cells | e range    | lcc range   |   e_g(r) |   e_g repaired |   crossing |   delta | verdict                              |
|:------------|:----|----:|--------:|:-----------|:------------|---------:|---------------:|-----------:|--------:|:-------------------------------------|
| bernoulli   | n/4 |  50 |       6 | 0.90-2.18  | 0.50-1.00   |    0.384 |          0.241 |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n/4 |  60 |       6 | 0.93-2.77  | 0.67-1.00   |    0.39  |          0.241 |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n/4 |  75 |       6 | 1.04-3.34  | 0.89-1.00   |    0.384 |          0.241 |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n/4 | 100 |       5 | 1.67-2.80  | 1.00-1.00   |    0.39  |          0.241 |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n/2 |  50 |       6 | 0.68-4.56  | 0.25-1.00   |    0.5   |          0.183 |      0.842 |   0.342 | outside tolerance                    |
| bernoulli   | n/2 |  60 |       6 | 0.74-5.51  | 0.33-1.00   |    0.5   |          0.183 |      0.885 |   0.385 | outside tolerance                    |
| bernoulli   | n/2 |  75 |       6 | 0.85-6.91  | 0.51-1.00   |    0.498 |          0.183 |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n/2 | 100 |       4 | 1.65-3.00  | 0.99-1.00   |    0.5   |          0.183 |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n   |  50 |       6 | 0.74-9.06  | 0.45-1.00   |    0.618 |          0     |      0.829 |   0.211 | outside tolerance                    |
| bernoulli   | n   |  60 |       6 | 0.87-10.98 | 0.68-1.00   |    0.618 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | n   |  75 |       6 | 1.17-14.16 | 0.86-1.00   |    0.618 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 2n  |  50 |      10 | 1.10-17.98 | 0.83-1.00   |    0.732 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 2n  |  60 |       9 | 1.51-21.84 | 0.94-1.00   |    0.732 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 2n  |  75 |      10 | 1.42-27.92 | 0.93-1.00   |    0.732 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 4n  |  50 |       7 | 2.03-8.09  | 0.98-1.00   |    0.828 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 4n  |  60 |       7 | 1.98-8.19  | 0.98-1.00   |    0.828 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 4n  |  75 |       6 | 2.01-6.03  | 0.98-1.00   |    0.828 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 8n  |  50 |      11 | 1.51-10.40 | 0.93-1.00   |    0.899 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| bernoulli   | 8n  |  60 |      11 | 1.56-10.34 | 0.94-1.00   |    0.899 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n/8 |  75 |      10 | 0.97-2.79  | 0.62-1.00   |    0.292 |          0.118 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n/4 |  50 |       9 | 0.96-2.68  | 0.66-1.00   |    0.384 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n/4 |  60 |       9 | 0.97-2.78  | 0.67-1.00   |    0.39  |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n/4 |  75 |       9 | 0.96-2.69  | 0.64-1.00   |    0.384 |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n/4 | 100 |       7 | 1.46-3.27  | 1.00-1.00   |    0.39  |          0     |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n/2 |  50 |       9 | 0.88-4.50  | 0.46-1.00   |    0.5   |          0.475 |      0.908 |   0.408 | outside tolerance                    |
| fixed       | n/2 |  60 |       9 | 0.86-4.50  | 0.40-1.00   |    0.5   |          0.475 |      0.919 |   0.419 | outside tolerance                    |
| fixed       | n/2 |  75 |       9 | 0.85-4.44  | 0.36-1.00   |    0.498 |          0.475 |      0.932 |   0.434 | outside tolerance                    |
| fixed       | n/2 | 100 |       5 | 1.63-3.51  | 1.00-1.00   |    0.5   |          0.475 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n   |  50 |       9 | 1.13-9.00  | 0.94-1.00   |    0.618 |          0.489 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n   |  60 |       9 | 1.12-9.00  | 0.92-1.00   |    0.618 |          0.489 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n   |  75 |       9 | 1.13-9.00  | 0.94-1.00   |    0.618 |          0.489 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | n   | 100 |       3 | 1.13-3.02  | 0.95-1.00   |    0.618 |          0.489 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | 2n  |  50 |       9 | 2.02-18.00 | 1.00-1.00   |    0.732 |          0.496 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | 2n  |  60 |       9 | 2.02-18.00 | 1.00-1.00   |    0.732 |          0.496 |    nan     | nan     | not observable (all cells above 1/2) |
| fixed       | 2n  |  75 |       9 | 2.01-18.00 | 1.00-1.00   |    0.732 |          0.496 |    nan     | nan     | not observable (all cells above 1/2) |

#### Per ensemble series (generator, r, param, n)

<details><summary>526 series: generator, r, param, n (click to open)</summary>

| generator   | r   |   param |   n |   m |   count |   certified |   e median |   e min |   e max |   gamma/n median |   forest share |   2-core cust share |   lcc frac |   lcc cust frac |   e_g(r) |
|:------------|:----|--------:|----:|----:|--------:|------------:|-----------:|--------:|--------:|-----------------:|---------------:|--------------------:|-----------:|----------------:|---------:|
| bernoulli   | n/4 |  0.05   |  50 |  12 |      50 |          50 |      0.9   |  0.78   |   1.02  |           0.01   |        0.5     |            0.0384   |      0.503 |           0.507 |    0.384 |
| bernoulli   | n/4 |  0.075  |  50 |  12 |      50 |          50 |      1.06  |  0.86   |   1.26  |           0.1    |        0.02    |            0.195    |      0.873 |           0.876 |    0.384 |
| bernoulli   | n/4 |  0.1    |  50 |  12 |      50 |          50 |      1.22  |  1      |   1.42  |           0.25   |        0       |            0.326    |      0.975 |           0.977 |    0.384 |
| bernoulli   | n/4 |  0.125  |  50 |  12 |      50 |          50 |      1.42  |  1.16   |   1.84  |           0.44   |        0       |            0.428    |      0.994 |           0.995 |    0.384 |
| bernoulli   | n/4 |  0.15   |  50 |  12 |      50 |          50 |      1.68  |  1.4    |   2     |           0.7    |        0       |            0.554    |      1     |           1     |    0.384 |
| bernoulli   | n/4 |  0.2    |  50 |  12 |      50 |          50 |      2.18  |  1.78   |   2.6   |           1.2    |        0       |            0.723    |      1     |           1     |    0.384 |
| bernoulli   | n/4 |  0.05   |  60 |  15 |      50 |          50 |      0.933 |  0.833  |   1.17  |           0.0333 |        0.18    |            0.0923   |      0.67  |           0.677 |    0.39  |
| bernoulli   | n/4 |  0.075  |  60 |  15 |      50 |          50 |      1.18  |  1      |   1.4   |           0.217  |        0       |            0.297    |      0.961 |           0.962 |    0.39  |
| bernoulli   | n/4 |  0.1    |  60 |  15 |      50 |          50 |      1.42  |  1.2    |   1.85  |           0.433  |        0       |            0.432    |      0.994 |           0.995 |    0.39  |
| bernoulli   | n/4 |  0.125  |  60 |  15 |      50 |          50 |      1.77  |  1.47   |   2.03  |           0.783  |        0       |            0.58     |      0.999 |           0.999 |    0.39  |
| bernoulli   | n/4 |  0.15   |  60 |  15 |      50 |          50 |      2.08  |  1.6    |   2.37  |           1.1    |        0       |            0.672    |      1     |           1     |    0.39  |
| bernoulli   | n/4 |  0.2    |  60 |  15 |      50 |          50 |      2.77  |  2.52   |   3.28  |           1.78   |        0       |            0.835    |      1     |           1     |    0.39  |
| bernoulli   | n/4 |  0.05   |  75 |  18 |      50 |          50 |      1.04  |  0.92   |   1.29  |           0.08   |        0.02    |            0.181    |      0.886 |           0.889 |    0.384 |
| bernoulli   | n/4 |  0.075  |  75 |  18 |      50 |          50 |      1.36  |  1.17   |   1.6   |           0.373  |        0       |            0.387    |      0.989 |           0.991 |    0.384 |
| bernoulli   | n/4 |  0.1    |  75 |  18 |      50 |          50 |      1.71  |  1.43   |   1.96  |           0.72   |        0       |            0.549    |      1     |           1     |    0.384 |
| bernoulli   | n/4 |  0.125  |  75 |  18 |      50 |          50 |      2.11  |  1.73   |   2.48  |           1.12   |        0       |            0.673    |      1     |           1     |    0.384 |
| bernoulli   | n/4 |  0.15   |  75 |  18 |      50 |          50 |      2.53  |  2.24   |   2.81  |           1.54   |        0       |            0.778    |      1     |           1     |    0.384 |
| bernoulli   | n/4 |  0.2    |  75 |  18 |      50 |          50 |      3.34  |  2.93   |   3.68  |           2.35   |        0       |            0.899    |      1     |           1     |    0.384 |
| bernoulli   | n/4 |  0.07   | 100 |  25 |      30 |          30 |      1.67  |  1.5    |   1.86  |           0.69   |        0       |            0.534    |      0.999 |           0.999 |    0.39  |
| bernoulli   | n/4 |  0.08   | 100 |  25 |      30 |          30 |      1.9   |  1.7    |   2.26  |           0.915  |        0       |            0.615    |      0.999 |           1     |    0.39  |
| bernoulli   | n/4 |  0.09   | 100 |  25 |      30 |          30 |      2.06  |  1.86   |   2.37  |           1.08   |        0       |            0.675    |      1     |           1     |    0.39  |
| bernoulli   | n/4 |  0.1    | 100 |  25 |      30 |          30 |      2.33  |  2.07   |   2.47  |           1.33   |        0       |            0.73     |      1     |           1     |    0.39  |
| bernoulli   | n/4 |  0.12   | 100 |  25 |      30 |          30 |      2.8   |  2.47   |   3.22  |           1.81   |        0       |            0.814    |      1     |           1     |    0.39  |
| bernoulli   | n/2 |  0.025  |  50 |  25 |      50 |          50 |      0.68  |  0.6    |   0.8   |           0      |        0.82    |            0.0116   |      0.251 |           0.264 |    0.5   |
| bernoulli   | n/2 |  0.05   |  50 |  25 |      50 |          50 |      1.06  |  0.84   |   1.38  |           0.12   |        0       |            0.262    |      0.835 |           0.843 |    0.5   |
| bernoulli   | n/2 |  0.075  |  50 |  25 |      50 |          50 |      1.54  |  1.2    |   2.02  |           0.56   |        0       |            0.561    |      0.977 |           0.978 |    0.5   |
| bernoulli   | n/2 |  0.1    |  50 |  25 |      50 |          50 |      2.04  |  1.7    |   2.7   |           1.06   |        0       |            0.731    |      0.999 |           1     |    0.5   |
| bernoulli   | n/2 |  0.15   |  50 |  25 |      50 |          50 |      3.26  |  2.94   |   3.76  |           2.28   |        0       |            0.908    |      1     |           1     |    0.5   |
| bernoulli   | n/2 |  0.2    |  50 |  25 |      50 |          50 |      4.56  |  3.92   |   5.16  |           3.58   |        0       |            0.972    |      1     |           1     |    0.5   |
| bernoulli   | n/2 |  0.025  |  60 |  30 |      50 |          50 |      0.742 |  0.583  |   0.9   |           0      |        0.68    |            0.0227   |      0.326 |           0.338 |    0.5   |
| bernoulli   | n/2 |  0.05   |  60 |  30 |      50 |          50 |      1.25  |  0.967  |   1.48  |           0.308  |        0       |            0.405    |      0.941 |           0.945 |    0.5   |
| bernoulli   | n/2 |  0.075  |  60 |  30 |      50 |          50 |      1.79  |  1.57   |   2.23  |           0.817  |        0       |            0.646    |      0.99  |           0.991 |    0.5   |
| bernoulli   | n/2 |  0.1    |  60 |  30 |      50 |          50 |      2.48  |  1.98   |   3.03  |           1.5    |        0       |            0.809    |      1     |           1     |    0.5   |
| bernoulli   | n/2 |  0.15   |  60 |  30 |      50 |          50 |      4.04  |  3.38   |   4.82  |           3.06   |        0       |            0.953    |      1     |           1     |    0.5   |
| bernoulli   | n/2 |  0.2    |  60 |  30 |      50 |          50 |      5.51  |  4.88   |   6.13  |           4.53   |        0       |            0.99     |      1     |           1     |    0.5   |
| bernoulli   | n/2 |  0.025  |  75 |  37 |      50 |          50 |      0.847 |  0.68   |   1.03  |           0.0267 |        0.18    |            0.0837   |      0.514 |           0.523 |    0.498 |
| bernoulli   | n/2 |  0.05   |  75 |  37 |      50 |          50 |      1.51  |  1.27   |   1.88  |           0.54   |        0       |            0.533    |      0.978 |           0.98  |    0.498 |
| bernoulli   | n/2 |  0.075  |  75 |  37 |      50 |          50 |      2.33  |  2.01   |   2.72  |           1.34   |        0       |            0.774    |      0.999 |           0.999 |    0.498 |
| bernoulli   | n/2 |  0.1    |  75 |  37 |      50 |          50 |      3.25  |  2.77   |   3.68  |           2.26   |        0       |            0.896    |      1     |           1     |    0.498 |
| bernoulli   | n/2 |  0.15   |  75 |  37 |      50 |          50 |      4.97  |  4.48   |   5.48  |           3.99   |        0       |            0.981    |      1     |           1     |    0.498 |
| bernoulli   | n/2 |  0.2    |  75 |  37 |      50 |          50 |      6.91  |  6.17   |   7.57  |           5.92   |        0       |            0.997    |      1     |           1     |    0.498 |
| bernoulli   | n/2 |  0.04   | 100 |  50 |      30 |          28 |      1.65  |  1.34   |   1.86  |           0.66   |        0       |            0.577    |      0.988 |           0.989 |    0.5   |
| bernoulli   | n/2 |  0.05   | 100 |  50 |      30 |          30 |      2.06  |  1.73   |   2.36  |           1.08   |        0       |            0.731    |      0.997 |           0.998 |    0.5   |
| bernoulli   | n/2 |  0.06   | 100 |  50 |      30 |          30 |      2.54  |  2.19   |   2.88  |           1.56   |        0       |            0.802    |      0.999 |           0.999 |    0.5   |
| bernoulli   | n/2 |  0.07   | 100 |  50 |      30 |          30 |      3     |  2.69   |   3.27  |           2.01   |        0       |            0.878    |      1     |           1     |    0.5   |
| bernoulli   | n   |  0.025  |  10 |  10 |     150 |         150 |      0.3   |  0.1    |   0.7   |           0      |        1       |            0        |      0.259 |           0.262 |    0.618 |
| bernoulli   | n   |  0.05   |  10 |  10 |     150 |         150 |      0.4   |  0.1    |   0.7   |           0      |        0.98    |            0.004    |      0.328 |           0.335 |    0.618 |
| bernoulli   | n   |  0.075  |  10 |  10 |     150 |         150 |      0.5   |  0.1    |   0.8   |           0      |        0.947   |            0.0127   |      0.371 |           0.371 |    0.618 |
| bernoulli   | n   |  0.1    |  10 |  10 |     150 |         150 |      0.6   |  0.2    |   1.2   |           0      |        0.813   |            0.0573   |      0.497 |           0.497 |    0.618 |
| bernoulli   | n   |  0.15   |  10 |  10 |     150 |         150 |      0.8   |  0.3    |   1.4   |           0.1    |        0.42    |            0.207    |      0.7   |           0.705 |    0.618 |
| bernoulli   | n   |  0.2    |  10 |  10 |     150 |         150 |      1.2   |  0.4    |   2     |           0.3    |        0.1     |            0.463    |      0.903 |           0.901 |    0.618 |
| bernoulli   | n   |  0.3    |  10 |  10 |     150 |         150 |      2     |  1.2    |   3.2   |           1.1    |        0       |            0.81     |      0.995 |           0.995 |    0.618 |
| bernoulli   | n   |  0.4    |  10 |  10 |     150 |         150 |      3     |  2      |   4.1   |           2.1    |        0       |            0.947    |      0.999 |           0.999 |    0.618 |
| bernoulli   | n   |  0.5    |  10 |  10 |     150 |         150 |      4     |  2.8    |   5.3   |           3.1    |        0       |            0.988    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  15 |  15 |     150 |         150 |      0.4   |  0.2    |   0.667 |           0      |        0.993   |            0.000889 |      0.207 |           0.213 |    0.618 |
| bernoulli   | n   |  0.05   |  15 |  15 |     150 |         150 |      0.467 |  0.2    |   0.8   |           0      |        0.94    |            0.00889  |      0.3   |           0.307 |    0.618 |
| bernoulli   | n   |  0.075  |  15 |  15 |     150 |         150 |      0.667 |  0.333  |   1.07  |           0      |        0.707   |            0.0609   |      0.479 |           0.478 |    0.618 |
| bernoulli   | n   |  0.1    |  15 |  15 |     150 |         150 |      0.867 |  0.333  |   1.6   |           0.0667 |        0.273   |            0.211    |      0.706 |           0.708 |    0.618 |
| bernoulli   | n   |  0.15   |  15 |  15 |     150 |         150 |      1.4   |  0.733  |   2.4   |           0.533  |        0.02    |            0.589    |      0.938 |           0.936 |    0.618 |
| bernoulli   | n   |  0.2    |  15 |  15 |     150 |         150 |      2.07  |  1.13   |   3.2   |           1.13   |        0       |            0.792    |      0.99  |           0.99  |    0.618 |
| bernoulli   | n   |  0.3    |  15 |  15 |     150 |         150 |      3.47  |  2.6    |   5.13  |           2.53   |        0       |            0.964    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.4    |  15 |  15 |     150 |         150 |      4.93  |  3.6    |   6.07  |           4      |        0       |            0.995    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.5    |  15 |  15 |     150 |         150 |      6.47  |  5.27   |   7.8   |           5.53   |        0       |            0.999    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  20 |  20 |     150 |         150 |      0.4   |  0.2    |   0.7   |           0      |        0.987   |            0.00133  |      0.204 |           0.208 |    0.618 |
| bernoulli   | n   |  0.05   |  20 |  20 |     150 |         150 |      0.6   |  0.35   |   1.05  |           0      |        0.653   |            0.0517   |      0.383 |           0.389 |    0.618 |
| bernoulli   | n   |  0.075  |  20 |  20 |     150 |         150 |      0.85  |  0.35   |   1.65  |           0.1    |        0.24    |            0.203    |      0.682 |           0.68  |    0.618 |
| bernoulli   | n   |  0.1    |  20 |  20 |     150 |         150 |      1.25  |  0.6    |   2.1   |           0.35   |        0.0267  |            0.476    |      0.888 |           0.888 |    0.618 |
| bernoulli   | n   |  0.15   |  20 |  20 |     150 |         150 |      2.1   |  1.05   |   3.15  |           1.15   |        0       |            0.794    |      0.99  |           0.99  |    0.618 |
| bernoulli   | n   |  0.2    |  20 |  20 |     150 |         150 |      3.05  |  2      |   4.55  |           2.1    |        0       |            0.928    |      0.999 |           0.999 |    0.618 |
| bernoulli   | n   |  0.3    |  20 |  20 |     150 |         150 |      5.05  |  3.75   |   6.05  |           4.1    |        0       |            0.993    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.4    |  20 |  20 |     150 |         150 |      6.95  |  5.45   |   8.4   |           6      |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.5    |  20 |  20 |     150 |         150 |      9     |  7.75   |  10.2   |           8.05   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  25 |  25 |     150 |         150 |      0.48  |  0.24   |   0.72  |           0      |        0.973   |            0.00267  |      0.187 |           0.186 |    0.618 |
| bernoulli   | n   |  0.05   |  25 |  25 |     150 |         150 |      0.68  |  0.4    |   1.04  |           0      |        0.527   |            0.0763   |      0.464 |           0.466 |    0.618 |
| bernoulli   | n   |  0.075  |  25 |  25 |     150 |         150 |      1.12  |  0.72   |   1.8   |           0.24   |        0.0333  |            0.418    |      0.855 |           0.855 |    0.618 |
| bernoulli   | n   |  0.1    |  25 |  25 |     150 |         150 |      1.56  |  0.96   |   2.48  |           0.64   |        0       |            0.648    |      0.96  |           0.96  |    0.618 |
| bernoulli   | n   |  0.15   |  25 |  25 |     150 |         150 |      2.78  |  1.88   |   3.6   |           1.84   |        0       |            0.904    |      0.998 |           0.998 |    0.618 |
| bernoulli   | n   |  0.2    |  25 |  25 |     150 |         150 |      3.96  |  3.04   |   5.52  |           3      |        0       |            0.968    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.3    |  25 |  25 |     150 |         150 |      6.52  |  5.36   |   7.44  |           5.56   |        0       |            0.999    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.4    |  25 |  25 |     150 |         150 |      9.04  |  7.88   |  10.1   |           8.08   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.5    |  25 |  25 |     150 |         150 |     11.5   | 10.3    |  13.2   |          10.5    |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  30 |  30 |     150 |         150 |      0.5   |  0.333  |   0.767 |           0      |        0.94    |            0.00533  |      0.219 |           0.219 |    0.618 |
| bernoulli   | n   |  0.05   |  30 |  30 |     150 |         150 |      0.883 |  0.533  |   1.27  |           0.0833 |        0.12    |            0.213    |      0.682 |           0.68  |    0.618 |
| bernoulli   | n   |  0.075  |  30 |  30 |     150 |         150 |      1.43  |  0.833  |   2     |           0.5    |        0       |            0.587    |      0.944 |           0.944 |    0.618 |
| bernoulli   | n   |  0.1    |  30 |  30 |     150 |         150 |      2.07  |  1.43   |   2.7   |           1.1    |        0       |            0.782    |      0.985 |           0.986 |    0.618 |
| bernoulli   | n   |  0.15   |  30 |  30 |     150 |         150 |      3.57  |  2.73   |   4.7   |           2.6    |        0       |            0.954    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.2    |  30 |  30 |     150 |         150 |      5     |  3.7    |   6.13  |           4.03   |        0       |            0.988    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.3    |  30 |  30 |     150 |         150 |      8     |  6.87   |   9.23  |           7.03   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.4    |  30 |  30 |     150 |         150 |     11     |  9.8    |  12.5   |          10      |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.5    |  30 |  30 |     150 |         150 |     14     | 12.8    |  15.3   |          13.1    |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  35 |  35 |     150 |         150 |      0.543 |  0.4    |   0.829 |           0      |        0.833   |            0.0133   |      0.24  |           0.241 |    0.618 |
| bernoulli   | n   |  0.05   |  35 |  35 |     150 |         150 |      1.07  |  0.629  |   1.43  |           0.2    |        0.0467  |            0.35     |      0.815 |           0.817 |    0.618 |
| bernoulli   | n   |  0.075  |  35 |  35 |     150 |         150 |      1.77  |  1.14   |   2.43  |           0.829  |        0       |            0.704    |      0.974 |           0.974 |    0.618 |
| bernoulli   | n   |  0.1    |  35 |  35 |     150 |         150 |      2.54  |  1.6    |   3.43  |           1.57   |        0       |            0.859    |      0.995 |           0.994 |    0.618 |
| bernoulli   | n   |  0.15   |  35 |  35 |     150 |         150 |      4.23  |  3.49   |   5.74  |           3.26   |        0       |            0.975    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.2    |  35 |  35 |     150 |         150 |      6.07  |  4.86   |   7.11  |           5.1    |        0       |            0.996    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.3    |  35 |  35 |     150 |         150 |      9.49  |  8.31   |  10.4   |           8.51   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.4    |  35 |  35 |     150 |         150 |     13     | 11.5    |  14.2   |          12      |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.5    |  35 |  35 |     150 |         150 |     16.6   | 14.9    |  18     |          15.6    |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  40 |  40 |     150 |         150 |      0.625 |  0.425  |   0.875 |           0      |        0.707   |            0.0257   |      0.291 |           0.289 |    0.618 |
| bernoulli   | n   |  0.05   |  40 |  40 |     150 |         150 |      1.25  |  0.775  |   1.68  |           0.325  |        0.00667 |            0.489    |      0.906 |           0.906 |    0.618 |
| bernoulli   | n   |  0.075  |  40 |  40 |     150 |         150 |      2.1   |  1.5    |   2.8   |           1.12   |        0       |            0.796    |      0.988 |           0.989 |    0.618 |
| bernoulli   | n   |  0.1    |  40 |  40 |     150 |         150 |      3.02  |  2.3    |   3.85  |           2.05   |        0       |            0.92     |      0.999 |           0.999 |    0.618 |
| bernoulli   | n   |  0.15   |  40 |  40 |     150 |         150 |      4.92  |  4.05   |   5.9   |           3.95   |        0       |            0.986    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.2    |  40 |  40 |     150 |         150 |      7     |  6.15   |   7.92  |           6.03   |        0       |            0.999    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.3    |  40 |  40 |     150 |         150 |     10.9   |  9.82   |  12.3   |           9.95   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.4    |  40 |  40 |     150 |         150 |     15     | 13.8    |  16.4   |          14      |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.5    |  40 |  40 |     150 |         150 |     19     | 17.6    |  20.4   |          18      |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  50 |  50 |      50 |          50 |      0.74  |  0.44   |   0.9   |           0.02   |        0.34    |            0.0784   |      0.448 |           0.451 |    0.618 |
| bernoulli   | n   |  0.05   |  50 |  50 |      50 |          50 |      1.64  |  1.32   |   2.28  |           0.68   |        0       |            0.66     |      0.972 |           0.971 |    0.618 |
| bernoulli   | n   |  0.075  |  50 |  50 |      50 |          50 |      2.78  |  2.28   |   3.54  |           1.8    |        0       |            0.888    |      0.998 |           0.998 |    0.618 |
| bernoulli   | n   |  0.1    |  50 |  50 |      50 |          50 |      4.1   |  3.58   |   4.64  |           3.12   |        0       |            0.971    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.15   |  50 |  50 |      50 |          50 |      6.41  |  5.82   |   7.7   |           5.43   |        0       |            0.996    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.2    |  50 |  50 |      50 |          50 |      9.06  |  8.06   |   9.84  |           8.08   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  60 |  60 |      50 |          50 |      0.867 |  0.7    |   1.25  |           0.0667 |        0.06    |            0.193    |      0.684 |           0.681 |    0.618 |
| bernoulli   | n   |  0.05   |  60 |  60 |      50 |          50 |      2.13  |  1.57   |   2.55  |           1.17   |        0       |            0.794    |      0.988 |           0.988 |    0.618 |
| bernoulli   | n   |  0.075  |  60 |  60 |      50 |          50 |      3.48  |  3.05   |   4.07  |           2.5    |        0       |            0.942    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.1    |  60 |  60 |      50 |          50 |      4.89  |  4.27   |   5.45  |           3.91   |        0       |            0.983    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.15   |  60 |  60 |      50 |          50 |      7.92  |  7.12   |   9.02  |           6.93   |        0       |            0.999    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.2    |  60 |  60 |      50 |          50 |     11     |  9.93   |  11.7   |           9.99   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.025  |  75 |  75 |      50 |          50 |      1.17  |  0.813  |   1.45  |           0.273  |        0       |            0.413    |      0.859 |           0.861 |    0.618 |
| bernoulli   | n   |  0.05   |  75 |  75 |      50 |          50 |      2.79  |  2.44   |   3.35  |           1.81   |        0       |            0.886    |      0.997 |           0.996 |    0.618 |
| bernoulli   | n   |  0.075  |  75 |  75 |      50 |          50 |      4.53  |  4.01   |   5.12  |           3.55   |        0       |            0.979    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.1    |  75 |  75 |      50 |          50 |      6.52  |  6      |   7.13  |           5.53   |        0       |            0.997    |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.15   |  75 |  75 |      50 |          50 |     10.2   |  9.41   |  11     |           9.25   |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | n   |  0.2    |  75 |  75 |      50 |          50 |     14.2   | 13.1    |  14.8   |          13.2    |        0       |            1        |      1     |           1     |    0.618 |
| bernoulli   | 2n  |  0.025  |  10 |  20 |     150 |         150 |      0.2   |  0      |   0.6   |           0      |        1       |            0        |      0.255 |           0.229 |    0.732 |
| bernoulli   | 2n  |  0.05   |  10 |  20 |     150 |         150 |      0.3   |  0      |   0.8   |           0      |        0.907   |            0.0233   |      0.336 |           0.314 |    0.732 |
| bernoulli   | 2n  |  0.075  |  10 |  20 |     150 |         150 |      0.55  |  0.2    |   1.3   |           0      |        0.707   |            0.082    |      0.518 |           0.507 |    0.732 |
| bernoulli   | 2n  |  0.1    |  10 |  20 |     150 |         150 |      0.8   |  0.1    |   1.5   |           0.1    |        0.4     |            0.257    |      0.692 |           0.683 |    0.732 |
| bernoulli   | 2n  |  0.15   |  10 |  20 |     150 |         150 |      1.4   |  0.4    |   2.5   |           0.6    |        0.0133  |            0.648    |      0.938 |           0.927 |    0.732 |
| bernoulli   | 2n  |  0.2    |  10 |  20 |     150 |         150 |      2.2   |  1.1    |   4.3   |           1.3    |        0       |            0.879    |      0.987 |           0.985 |    0.732 |
| bernoulli   | 2n  |  0.3    |  10 |  20 |     150 |         150 |      4     |  2.5    |   6.1   |           3.1    |        0       |            0.989    |      0.999 |           0.999 |    0.732 |
| bernoulli   | 2n  |  0.4    |  10 |  20 |     150 |         150 |      6.1   |  4.3    |   7.8   |           5.2    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  10 |  20 |     150 |         150 |      8     |  6.2    |  10     |           7.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  15 |  30 |     150 |         150 |      0.267 |  0.0667 |   0.667 |           0      |        0.993   |            0.000889 |      0.22  |           0.208 |    0.732 |
| bernoulli   | 2n  |  0.05   |  15 |  30 |     150 |         150 |      0.533 |  0.0667 |   1.13  |           0      |        0.66    |            0.076    |      0.412 |           0.393 |    0.732 |
| bernoulli   | 2n  |  0.075  |  15 |  30 |     150 |         150 |      0.867 |  0.333  |   1.8   |           0.133  |        0.173   |            0.312    |      0.72  |           0.706 |    0.732 |
| bernoulli   | 2n  |  0.1    |  15 |  30 |     150 |         150 |      1.47  |  0.733  |   2.4   |           0.533  |        0       |            0.646    |      0.919 |           0.912 |    0.732 |
| bernoulli   | 2n  |  0.15   |  15 |  30 |     150 |         150 |      2.67  |  1.73   |   3.93  |           1.73   |        0       |            0.933    |      0.997 |           0.996 |    0.732 |
| bernoulli   | 2n  |  0.2    |  15 |  30 |     150 |         150 |      4.07  |  2.33   |   5.47  |           3.13   |        0       |            0.987    |      0.999 |           0.999 |    0.732 |
| bernoulli   | 2n  |  0.3    |  15 |  30 |     150 |         150 |      6.87  |  5.27   |   8.53  |           5.93   |        0       |            0.999    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.4    |  15 |  30 |     150 |         150 |     10     |  8.27   |  12     |           9.07   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  15 |  30 |     150 |         150 |     12.9   | 10.8    |  14.8   |          12      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  20 |  40 |     150 |         150 |      0.375 |  0.15   |   0.7   |           0      |        0.953   |            0.00533  |      0.226 |           0.212 |    0.732 |
| bernoulli   | 2n  |  0.05   |  20 |  40 |     150 |         150 |      0.8   |  0.35   |   1.45  |           0.1    |        0.18    |            0.25     |      0.664 |           0.654 |    0.732 |
| bernoulli   | 2n  |  0.075  |  20 |  40 |     150 |         150 |      1.45  |  0.65   |   2.05  |           0.55   |        0.00667 |            0.636    |      0.919 |           0.912 |    0.732 |
| bernoulli   | 2n  |  0.1    |  20 |  40 |     150 |         150 |      2.25  |  1.05   |   3.15  |           1.3    |        0       |            0.867    |      0.988 |           0.986 |    0.732 |
| bernoulli   | 2n  |  0.15   |  20 |  40 |     150 |         150 |      4.1   |  2.95   |   5.45  |           3.15   |        0       |            0.985    |      0.999 |           0.999 |    0.732 |
| bernoulli   | 2n  |  0.2    |  20 |  40 |     150 |         150 |      6     |  4.45   |   7.35  |           5.05   |        0       |            0.999    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.3    |  20 |  40 |     150 |         150 |     10     |  7.9    |  12.2   |           9.07   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.4    |  20 |  40 |     150 |         150 |     14     | 12.2    |  16.2   |          13      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  20 |  40 |     150 |         150 |     18.1   | 15.9    |  20.3   |          17.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  25 |  50 |     150 |         150 |      0.44  |  0.16   |   0.76  |           0      |        0.827   |            0.0192   |      0.26  |           0.25  |    0.732 |
| bernoulli   | 2n  |  0.05   |  25 |  50 |     150 |         150 |      1.08  |  0.56   |   2.08  |           0.24   |        0.0133  |            0.453    |      0.835 |           0.822 |    0.732 |
| bernoulli   | 2n  |  0.075  |  25 |  50 |     150 |         150 |      2.08  |  1.16   |   3.2   |           1.12   |        0       |            0.829    |      0.98  |           0.977 |    0.732 |
| bernoulli   | 2n  |  0.1    |  25 |  50 |     150 |         150 |      3.08  |  2.24   |   4.6   |           2.12   |        0       |            0.947    |      0.998 |           0.997 |    0.732 |
| bernoulli   | 2n  |  0.15   |  25 |  50 |     150 |         150 |      5.56  |  4.4    |   6.76  |           4.6    |        0       |            0.997    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  25 |  50 |     150 |         150 |      8     |  6.6    |   9.32  |           7.04   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.3    |  25 |  50 |     150 |         150 |     13     | 11.2    |  14.9   |          12.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.4    |  25 |  50 |     150 |         150 |     18     | 16      |  20     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  25 |  50 |     150 |         150 |     22.9   | 21      |  25.3   |          22      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  30 |  60 |     150 |         150 |      0.533 |  0.167  |   0.967 |           0      |        0.607   |            0.0513   |      0.342 |           0.333 |    0.732 |
| bernoulli   | 2n  |  0.05   |  30 |  60 |     150 |         150 |      1.43  |  0.733  |   2.1   |           0.533  |        0       |            0.642    |      0.925 |           0.918 |    0.732 |
| bernoulli   | 2n  |  0.075  |  30 |  60 |     150 |         150 |      2.7   |  1.77   |   3.4   |           1.73   |        0       |            0.914    |      0.994 |           0.992 |    0.732 |
| bernoulli   | 2n  |  0.1    |  30 |  60 |     150 |         150 |      4.05  |  2.93   |   5.27  |           3.08   |        0       |            0.984    |      1     |           0.999 |    0.732 |
| bernoulli   | 2n  |  0.15   |  30 |  60 |     150 |         150 |      7     |  5.4    |   8.43  |           6.03   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  30 |  60 |     150 |         150 |     10     |  8.7    |  11.3   |           9.07   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.3    |  30 |  60 |     150 |         150 |     16     | 14.4    |  17.9   |          15      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.4    |  30 |  60 |     150 |         150 |     22.1   | 20.2    |  24.1   |          21.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  30 |  60 |     150 |         150 |     28     | 26.3    |  29.7   |          27.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  35 |  70 |     150 |         150 |      0.686 |  0.371  |   1.09  |           0.0286 |        0.347   |            0.106    |      0.479 |           0.47  |    0.732 |
| bernoulli   | 2n  |  0.05   |  35 |  70 |     150 |         150 |      1.83  |  1.06   |   2.49  |           0.886  |        0       |            0.774    |      0.965 |           0.962 |    0.732 |
| bernoulli   | 2n  |  0.075  |  35 |  70 |     150 |         150 |      3.31  |  2.57   |   4.37  |           2.34   |        0       |            0.962    |      0.998 |           0.997 |    0.732 |
| bernoulli   | 2n  |  0.1    |  35 |  70 |     150 |         150 |      5.09  |  4      |   6.31  |           4.11   |        0       |            0.994    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.15   |  35 |  70 |     150 |         150 |      8.43  |  7.11   |   9.94  |           7.46   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  35 |  70 |     150 |         150 |     12.1   | 10.5    |  13.6   |          11.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.3    |  35 |  70 |     150 |         150 |     19     | 17.3    |  20.9   |          18      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.4    |  35 |  70 |     150 |         150 |     26.1   | 24.2    |  27.6   |          25.2    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  35 |  70 |     150 |         150 |     32.9   | 31.7    |  34.7   |          32      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  40 |  80 |     150 |         150 |      0.8   |  0.375  |   1.23  |           0.075  |        0.1     |            0.225    |      0.632 |           0.623 |    0.732 |
| bernoulli   | 2n  |  0.05   |  40 |  80 |     150 |         150 |      2.25  |  1.7    |   3     |           1.27   |        0       |            0.863    |      0.986 |           0.983 |    0.732 |
| bernoulli   | 2n  |  0.075  |  40 |  80 |     150 |         150 |      4.05  |  3.2    |   5.08  |           3.08   |        0       |            0.981    |      0.999 |           0.999 |    0.732 |
| bernoulli   | 2n  |  0.1    |  40 |  80 |     150 |         150 |      6.03  |  5.05   |   7.62  |           5.05   |        0       |            0.998    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.15   |  40 |  80 |     150 |         150 |     10     |  8.8    |  11.2   |           9.03   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  40 |  80 |     150 |         150 |     13.9   | 11.2    |  15.9   |          12.9    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.3    |  40 |  80 |     150 |         150 |     22     | 20.7    |  23.6   |          21.1    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.4    |  40 |  80 |     150 |         150 |     30     | 28.4    |  31.6   |          29      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.5    |  40 |  80 |     150 |         150 |     38     | 36      |  40     |          37      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  50 | 100 |      50 |          50 |      1.1   |  0.68   |   1.44  |           0.24   |        0       |            0.463    |      0.835 |           0.823 |    0.732 |
| bernoulli   | 2n  |  0.035  |  50 | 100 |      50 |          50 |      1.86  |  1.44   |   2.52  |           0.9    |        0       |            0.765    |      0.966 |           0.963 |    0.732 |
| bernoulli   | 2n  |  0.04   |  50 | 100 |      50 |          50 |      2.24  |  1.88   |   2.98  |           1.28   |        0       |            0.868    |      0.987 |           0.984 |    0.732 |
| bernoulli   | 2n  |  0.045  |  50 | 100 |      50 |          50 |      2.7   |  2.2    |   3.18  |           1.72   |        0       |            0.907    |      0.994 |           0.992 |    0.732 |
| bernoulli   | 2n  |  0.05   |  50 | 100 |      50 |          50 |      3.14  |  2.3    |   3.8   |           2.16   |        0       |            0.944    |      0.997 |           0.996 |    0.732 |
| bernoulli   | 2n  |  0.06   |  50 | 100 |      50 |          50 |      4.1   |  3.48   |   4.9   |           3.12   |        0       |            0.984    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.075  |  50 | 100 |      50 |          50 |      5.53  |  4.72   |   6.54  |           4.55   |        0       |            0.994    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.1    |  50 | 100 |      50 |          50 |      7.93  |  7.2    |   8.76  |           6.95   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.15   |  50 | 100 |      50 |          50 |     13     | 12.3    |  14     |          12      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  50 | 100 |      50 |          50 |     18     | 16.6    |  19.2   |          17      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.025  |  60 | 120 |      50 |          50 |      1.51  |  1.1    |   1.87  |           0.575  |        0       |            0.653    |      0.938 |           0.93  |    0.732 |
| bernoulli   | 2n  |  0.0292 |  60 | 120 |      50 |          50 |      1.83  |  1.48   |   2.25  |           0.883  |        0       |            0.768    |      0.966 |           0.96  |    0.732 |
| bernoulli   | 2n  |  0.0333 |  60 | 120 |      50 |          50 |      2.26  |  1.65   |   2.85  |           1.3    |        0       |            0.86     |      0.984 |           0.981 |    0.732 |
| bernoulli   | 2n  |  0.0375 |  60 | 120 |      50 |          50 |      2.68  |  2.23   |   3.28  |           1.72   |        0       |            0.903    |      0.993 |           0.99  |    0.732 |
| bernoulli   | 2n  |  0.05   |  60 | 120 |     100 |         100 |      4.07  |  3.45   |   4.98  |           3.08   |        0       |            0.976    |      0.999 |           0.999 |    0.732 |
| bernoulli   | 2n  |  0.075  |  60 | 120 |      50 |          50 |      6.98  |  6.1    |   7.92  |           6      |        0       |            0.999    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.1    |  60 | 120 |      50 |          50 |     10.2   |  9.1    |  10.8   |           9.2    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.15   |  60 | 120 |      50 |          50 |     15.9   | 14.9    |  17     |          14.9    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  60 | 120 |      50 |          50 |     21.8   | 20.5    |  23.1   |          20.9    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.02   |  75 | 150 |      20 |          20 |      1.42  |  1.28   |   1.71  |           0.507  |        0       |            0.645    |      0.935 |           0.927 |    0.732 |
| bernoulli   | 2n  |  0.0233 |  75 | 150 |      20 |          20 |      1.89  |  1.61   |   2.28  |           0.92   |        0       |            0.775    |      0.974 |           0.967 |    0.732 |
| bernoulli   | 2n  |  0.025  |  75 | 150 |      50 |          48 |      2.12  |  1.63   |   2.51  |           1.13   |        0       |            0.83     |      0.981 |           0.978 |    0.732 |
| bernoulli   | 2n  |  0.03   |  75 | 150 |      20 |          20 |      2.72  |  2.39   |   3.12  |           1.73   |        0       |            0.911    |      0.993 |           0.991 |    0.732 |
| bernoulli   | 2n  |  0.0333 |  75 | 150 |      20 |          20 |      3.23  |  2.76   |   3.56  |           2.26   |        0       |            0.945    |      0.996 |           0.995 |    0.732 |
| bernoulli   | 2n  |  0.05   |  75 | 150 |      50 |          50 |      5.54  |  4.93   |   6.28  |           4.55   |        0       |            0.996    |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.075  |  75 | 150 |      50 |          50 |      9.25  |  8.39   |  10.3   |           8.27   |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.1    |  75 | 150 |      50 |          50 |     13     | 11.9    |  14     |          12      |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.15   |  75 | 150 |      50 |          50 |     20.6   | 19.3    |  21.5   |          19.6    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 2n  |  0.2    |  75 | 150 |      50 |          50 |     27.9   | 26.7    |  29.6   |          26.9    |        0       |            1        |      1     |           1     |    0.732 |
| bernoulli   | 4n  |  0.03   |  40 | 160 |      50 |          50 |      2     |  1.5    |   2.5   |           1.06   |        0       |            0.823    |      0.971 |           0.961 |    0.828 |
| bernoulli   | 4n  |  0.035  |  40 | 160 |      50 |          50 |      2.64  |  1.85   |   3.2   |           1.66   |        0       |            0.936    |      0.991 |           0.989 |    0.828 |
| bernoulli   | 4n  |  0.04   |  40 | 160 |      50 |          50 |      3.21  |  2.6    |   3.8   |           2.25   |        0       |            0.971    |      0.999 |           0.998 |    0.828 |
| bernoulli   | 4n  |  0.045  |  40 | 160 |      50 |          50 |      3.83  |  2.92   |   4.72  |           2.85   |        0       |            0.984    |      0.999 |           0.998 |    0.828 |
| bernoulli   | 4n  |  0.05   |  40 | 160 |      50 |          50 |      4.7   |  3.85   |   5.83  |           3.73   |        0       |            0.993    |      1     |           0.999 |    0.828 |
| bernoulli   | 4n  |  0.06   |  40 | 160 |      50 |          50 |      6.05  |  4.97   |   7.3   |           5.08   |        0       |            0.999    |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.075  |  40 | 160 |      50 |          50 |      8.07  |  6.95   |   9.5   |           7.1    |        0       |            1        |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.024  |  50 | 200 |      50 |          50 |      2.03  |  1.38   |   2.46  |           1.07   |        0       |            0.854    |      0.978 |           0.973 |    0.828 |
| bernoulli   | 4n  |  0.028  |  50 | 200 |      50 |          50 |      2.52  |  1.98   |   3.3   |           1.57   |        0       |            0.921    |      0.992 |           0.989 |    0.828 |
| bernoulli   | 4n  |  0.032  |  50 | 200 |      50 |          50 |      3.17  |  2.44   |   3.62  |           2.19   |        0       |            0.96     |      0.997 |           0.997 |    0.828 |
| bernoulli   | 4n  |  0.036  |  50 | 200 |      50 |          50 |      3.84  |  3.36   |   4.46  |           2.86   |        0       |            0.982    |      0.999 |           0.998 |    0.828 |
| bernoulli   | 4n  |  0.04   |  50 | 200 |      50 |          50 |      4.48  |  3.72   |   5.3   |           3.5    |        0       |            0.992    |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.048  |  50 | 200 |      50 |          50 |      6.11  |  5.14   |   6.9   |           5.13   |        0       |            0.999    |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.06   |  50 | 200 |      50 |          50 |      8.09  |  7.3    |   8.94  |           7.11   |        0       |            1        |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.02   |  60 | 240 |      50 |          50 |      1.98  |  1.43   |   2.43  |           1.02   |        0       |            0.84     |      0.977 |           0.972 |    0.828 |
| bernoulli   | 4n  |  0.0233 |  60 | 240 |      50 |          50 |      2.52  |  2.12   |   3.15  |           1.55   |        0       |            0.919    |      0.989 |           0.986 |    0.828 |
| bernoulli   | 4n  |  0.0267 |  60 | 240 |      50 |          50 |      3.15  |  2.65   |   3.92  |           2.17   |        0       |            0.965    |      0.997 |           0.996 |    0.828 |
| bernoulli   | 4n  |  0.03   |  60 | 240 |      50 |          50 |      3.96  |  3.43   |   4.48  |           2.98   |        0       |            0.987    |      1     |           0.999 |    0.828 |
| bernoulli   | 4n  |  0.0333 |  60 | 240 |      50 |          50 |      4.54  |  3.63   |   5.12  |           3.56   |        0       |            0.993    |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.04   |  60 | 240 |      50 |          50 |      5.77  |  5      |   7.13  |           4.78   |        0       |            0.998    |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.05   |  60 | 240 |      50 |          50 |      8.19  |  7.3    |   9.17  |           7.21   |        0       |            1        |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.016  |  75 | 300 |      20 |          20 |      2.01  |  1.56   |   2.32  |           1.05   |        0       |            0.831    |      0.976 |           0.971 |    0.828 |
| bernoulli   | 4n  |  0.0187 |  75 | 300 |      20 |          20 |      2.55  |  2.17   |   3.08  |           1.59   |        0       |            0.925    |      0.994 |           0.992 |    0.828 |
| bernoulli   | 4n  |  0.0213 |  75 | 300 |      20 |          20 |      3.18  |  2.64   |   3.69  |           2.19   |        0       |            0.963    |      0.996 |           0.995 |    0.828 |
| bernoulli   | 4n  |  0.024  |  75 | 300 |      20 |          20 |      3.85  |  3.43   |   4.16  |           2.86   |        0       |            0.987    |      1     |           1     |    0.828 |
| bernoulli   | 4n  |  0.0267 |  75 | 300 |      20 |          20 |      4.55  |  3.99   |   5.13  |           3.57   |        0       |            0.993    |      1     |           0.999 |    0.828 |
| bernoulli   | 4n  |  0.032  |  75 | 300 |      20 |          20 |      6.03  |  5.23   |   6.79  |           5.05   |        0       |            0.998    |      1     |           1     |    0.828 |
| bernoulli   | 8n  |  0.014  |  50 | 400 |      50 |          50 |      1.51  |  1.14   |   2.26  |           0.6    |        0       |            0.74     |      0.929 |           0.922 |    0.899 |
| bernoulli   | 8n  |  0.016  |  50 | 400 |      50 |          50 |      2     |  1.66   |   2.6   |           1.04   |        0       |            0.859    |      0.978 |           0.974 |    0.899 |
| bernoulli   | 8n  |  0.018  |  50 | 400 |      50 |          50 |      2.42  |  2.06   |   2.88  |           1.46   |        0       |            0.934    |      0.988 |           0.985 |    0.899 |
| bernoulli   | 8n  |  0.02   |  50 | 400 |      50 |          50 |      2.9   |  2.34   |   3.48  |           1.92   |        0       |            0.957    |      0.992 |           0.99  |    0.899 |
| bernoulli   | 8n  |  0.022  |  50 | 400 |      50 |          50 |      3.51  |  2.68   |   4.14  |           2.53   |        0       |            0.983    |      0.999 |           0.998 |    0.899 |
| bernoulli   | 8n  |  0.024  |  50 | 400 |      50 |          50 |      4.06  |  3.5    |   4.94  |           3.08   |        0       |            0.992    |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.026  |  50 | 400 |      50 |          50 |      4.48  |  3.88   |   5.3   |           3.5    |        0       |            0.994    |      1     |           0.999 |    0.899 |
| bernoulli   | 8n  |  0.029  |  50 | 400 |      50 |          50 |      5.42  |  4.68   |   6.34  |           4.45   |        0       |            1        |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.032  |  50 | 400 |      50 |          50 |      6.41  |  5.4    |   7.48  |           5.43   |        0       |            1        |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.036  |  50 | 400 |      50 |          50 |      7.48  |  6.6    |   8.6   |           6.5    |        0       |            1        |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.044  |  50 | 400 |      50 |          50 |     10.4   |  9.52   |  11.5   |           9.42   |        0       |            1        |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.0117 |  60 | 480 |      50 |          50 |      1.56  |  1.05   |   1.98  |           0.625  |        0       |            0.73     |      0.936 |           0.927 |    0.899 |
| bernoulli   | 8n  |  0.0133 |  60 | 480 |      50 |          50 |      1.88  |  1.55   |   2.4   |           0.942  |        0       |            0.85     |      0.971 |           0.965 |    0.899 |
| bernoulli   | 8n  |  0.015  |  60 | 480 |      50 |          50 |      2.46  |  1.88   |   3.12  |           1.5    |        0       |            0.921    |      0.986 |           0.984 |    0.899 |
| bernoulli   | 8n  |  0.0167 |  60 | 480 |      50 |          50 |      2.83  |  2.2    |   3.3   |           1.86   |        0       |            0.958    |      0.996 |           0.995 |    0.899 |
| bernoulli   | 8n  |  0.0183 |  60 | 480 |      50 |          50 |      3.41  |  2.78   |   4     |           2.42   |        0       |            0.983    |      0.999 |           0.998 |    0.899 |
| bernoulli   | 8n  |  0.02   |  60 | 480 |      50 |          50 |      4.03  |  3.5    |   4.52  |           3.05   |        0       |            0.992    |      0.999 |           0.999 |    0.899 |
| bernoulli   | 8n  |  0.0217 |  60 | 480 |      50 |          50 |      4.6   |  4.1    |   5.22  |           3.62   |        0       |            0.995    |      0.999 |           0.999 |    0.899 |
| bernoulli   | 8n  |  0.0242 |  60 | 480 |      50 |          50 |      5.48  |  4.93   |   6.23  |           4.5    |        0       |            0.999    |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.0267 |  60 | 480 |      50 |          50 |      6.39  |  5.25   |   7.38  |           5.41   |        0       |            1        |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.03   |  60 | 480 |      50 |          50 |      7.62  |  6.53   |   8.7   |           6.64   |        0       |            1        |      1     |           1     |    0.899 |
| bernoulli   | 8n  |  0.0367 |  60 | 480 |      50 |          50 |     10.3   |  9.53   |  11.6   |           9.36   |        0       |            1        |      1     |           1     |    0.899 |
| fixed       | n/8 |  4      |  75 |   9 |      50 |          50 |      0.973 |  0.92   |   1.03  |           0.0133 |        0.38    |            0.0304   |      0.617 |           0.615 |    0.292 |
| fixed       | n/8 |  6      |  75 |   9 |      50 |          50 |      1.08  |  1.01   |   1.15  |           0.0933 |        0       |            0.154    |      0.981 |           0.981 |    0.292 |
| fixed       | n/8 |  8      |  75 |   9 |      50 |          50 |      1.2   |  1.13   |   1.27  |           0.213  |        0       |            0.246    |      0.997 |           0.997 |    0.292 |
| fixed       | n/8 | 10      |  75 |   9 |      50 |          50 |      1.35  |  1.29   |   1.41  |           0.36   |        0       |            0.34     |      1     |           1     |    0.292 |
| fixed       | n/8 | 12      |  75 |   9 |      50 |          50 |      1.53  |  1.47   |   1.6   |           0.54   |        0       |            0.432    |      1     |           1     |    0.292 |
| fixed       | n/8 | 14      |  75 |   9 |      50 |          50 |      1.71  |  1.67   |   1.79  |           0.727  |        0       |            0.523    |      1     |           1     |    0.292 |
| fixed       | n/8 | 16      |  75 |   9 |      50 |          50 |      1.93  |  1.85   |   1.99  |           0.94   |        0       |            0.605    |      1     |           1     |    0.292 |
| fixed       | n/8 | 18      |  75 |   9 |      50 |          50 |      2.13  |  2.08   |   2.17  |           1.14   |        0       |            0.678    |      1     |           1     |    0.292 |
| fixed       | n/8 | 20      |  75 |   9 |      50 |          50 |      2.35  |  2.29   |   2.4   |           1.36   |        0       |            0.738    |      1     |           1     |    0.292 |
| fixed       | n/8 | 24      |  75 |   9 |      50 |          50 |      2.79  |  2.76   |   2.85  |           1.8    |        0       |            0.845    |      1     |           1     |    0.292 |
| fixed       | n/4 |  3      |  50 |  12 |      50 |          50 |      0.96  |  0.88   |   1.04  |           0.02   |        0.18    |            0.0612   |      0.663 |           0.657 |    0.384 |
| fixed       | n/4 |  4      |  50 |  12 |      50 |          50 |      1.1   |  0.94   |   1.2   |           0.12   |        0.02    |            0.223    |      0.936 |           0.935 |    0.384 |
| fixed       | n/4 |  5      |  50 |  12 |      50 |          50 |      1.24  |  1.18   |   1.32  |           0.26   |        0       |            0.338    |      0.998 |           0.998 |    0.384 |
| fixed       | n/4 |  6      |  50 |  12 |      50 |          50 |      1.42  |  1.34   |   1.5   |           0.44   |        0       |            0.425    |      1     |           1     |    0.384 |
| fixed       | n/4 |  7      |  50 |  12 |      50 |          50 |      1.6   |  1.52   |   1.7   |           0.62   |        0       |            0.515    |      1     |           1     |    0.384 |
| fixed       | n/4 |  8      |  50 |  12 |      50 |          50 |      1.8   |  1.7    |   1.9   |           0.82   |        0       |            0.582    |      1     |           1     |    0.384 |
| fixed       | n/4 |  9      |  50 |  12 |      50 |          50 |      2.02  |  1.94   |   2.08  |           1.04   |        0       |            0.654    |      1     |           1     |    0.384 |
| fixed       | n/4 | 10      |  50 |  12 |      50 |          50 |      2.24  |  2.18   |   2.32  |           1.26   |        0       |            0.733    |      1     |           1     |    0.384 |
| fixed       | n/4 | 12      |  50 |  12 |      50 |          50 |      2.68  |  2.64   |   2.74  |           1.7    |        0       |            0.813    |      1     |           1     |    0.384 |
| fixed       | n/4 |  3      |  60 |  15 |      50 |          50 |      0.967 |  0.9    |   1.03  |           0.0167 |        0.22    |            0.0687   |      0.673 |           0.668 |    0.39  |
| fixed       | n/4 |  4      |  60 |  15 |      50 |          50 |      1.1   |  1.02   |   1.18  |           0.133  |        0       |            0.231    |      0.955 |           0.953 |    0.39  |
| fixed       | n/4 |  5      |  60 |  15 |      50 |          50 |      1.25  |  1.17   |   1.35  |           0.275  |        0       |            0.357    |      0.996 |           0.996 |    0.39  |
| fixed       | n/4 |  6      |  60 |  15 |      50 |          50 |      1.47  |  1.4    |   1.55  |           0.483  |        0       |            0.449    |      1     |           1     |    0.39  |
| fixed       | n/4 |  7      |  60 |  15 |      50 |          50 |      1.63  |  1.58   |   1.72  |           0.65   |        0       |            0.535    |      1     |           1     |    0.39  |
| fixed       | n/4 |  8      |  60 |  15 |      50 |          50 |      1.88  |  1.8    |   1.95  |           0.892  |        0       |            0.612    |      1     |           1     |    0.39  |
| fixed       | n/4 |  9      |  60 |  15 |      50 |          50 |      2.1   |  2.02   |   2.17  |           1.12   |        0       |            0.688    |      1     |           1     |    0.39  |
| fixed       | n/4 | 10      |  60 |  15 |      50 |          50 |      2.32  |  2.27   |   2.4   |           1.33   |        0       |            0.73     |      1     |           1     |    0.39  |
| fixed       | n/4 | 12      |  60 |  15 |      50 |          50 |      2.78  |  2.75   |   2.83  |           1.8    |        0       |            0.831    |      1     |           1     |    0.39  |
| fixed       | n/4 |  3      |  75 |  18 |      50 |          50 |      0.96  |  0.893  |   1.04  |           0.0133 |        0.22    |            0.0595   |      0.64  |           0.635 |    0.384 |
| fixed       | n/4 |  4      |  75 |  18 |      50 |          50 |      1.09  |  1.01   |   1.16  |           0.12   |        0       |            0.223    |      0.965 |           0.963 |    0.384 |
| fixed       | n/4 |  5      |  75 |  18 |      50 |          50 |      1.26  |  1.16   |   1.32  |           0.273  |        0       |            0.338    |      0.997 |           0.997 |    0.384 |
| fixed       | n/4 |  6      |  75 |  18 |      50 |          50 |      1.43  |  1.35   |   1.53  |           0.44   |        0       |            0.419    |      1     |           1     |    0.384 |
| fixed       | n/4 |  7      |  75 |  18 |      50 |          50 |      1.61  |  1.52   |   1.68  |           0.62   |        0       |            0.507    |      1     |           1     |    0.384 |
| fixed       | n/4 |  8      |  75 |  18 |      50 |          50 |      1.8   |  1.76   |   1.88  |           0.813  |        0       |            0.584    |      1     |           1     |    0.384 |
| fixed       | n/4 |  9      |  75 |  18 |      50 |          50 |      2.03  |  1.97   |   2.08  |           1.04   |        0       |            0.649    |      1     |           1     |    0.384 |
| fixed       | n/4 | 10      |  75 |  18 |      50 |          50 |      2.24  |  2.19   |   2.28  |           1.25   |        0       |            0.711    |      1     |           1     |    0.384 |
| fixed       | n/4 | 12      |  75 |  18 |      50 |          50 |      2.69  |  2.64   |   2.72  |           1.71   |        0       |            0.81     |      1     |           1     |    0.384 |
| fixed       | n/4 |  6      | 100 |  25 |      30 |          30 |      1.46  |  1.4    |   1.51  |           0.465  |        0       |            0.453    |      1     |           1     |    0.39  |
| fixed       | n/4 |  8      | 100 |  25 |      30 |          30 |      1.88  |  1.82   |   1.94  |           0.885  |        0       |            0.611    |      1     |           1     |    0.39  |
| fixed       | n/4 |  9      | 100 |  25 |      30 |          30 |      2.08  |  2.05   |   2.14  |           1.1    |        0       |            0.67     |      1     |           1     |    0.39  |
| fixed       | n/4 | 10      | 100 |  25 |      30 |          30 |      2.32  |  2.29   |   2.37  |           1.33   |        0       |            0.716    |      1     |           1     |    0.39  |
| fixed       | n/4 | 11      | 100 |  25 |      30 |          30 |      2.55  |  2.53   |   2.61  |           1.56   |        0       |            0.776    |      1     |           1     |    0.39  |
| fixed       | n/4 | 12      | 100 |  25 |      30 |          30 |      2.79  |  2.76   |   2.83  |           1.8    |        0       |            0.81     |      1     |           1     |    0.39  |
| fixed       | n/4 | 14      | 100 |  25 |      30 |          30 |      3.27  |  3.25   |   3.31  |           2.28   |        0       |            0.89     |      1     |           1     |    0.39  |
| fixed       | n/2 |  2      |  50 |  25 |      50 |          50 |      0.88  |  0.8    |   1     |           0.02   |        0.48    |            0.0448   |      0.456 |           0.44  |    0.5   |
| fixed       | n/2 |  3      |  50 |  25 |      50 |          50 |      1.22  |  1.1    |   1.28  |           0.24   |        0       |            0.417    |      0.986 |           0.984 |    0.5   |
| fixed       | n/2 |  4      |  50 |  25 |      50 |          50 |      1.63  |  1.52   |   1.74  |           0.65   |        0       |            0.601    |      0.999 |           0.998 |    0.5   |
| fixed       | n/2 |  5      |  50 |  25 |      50 |          50 |      2.08  |  2      |   2.14  |           1.1    |        0       |            0.726    |      1     |           1     |    0.5   |
| fixed       | n/2 |  6      |  50 |  25 |      50 |          50 |      2.54  |  2.5    |   2.68  |           1.56   |        0       |            0.821    |      1     |           1     |    0.5   |
| fixed       | n/2 |  7      |  50 |  25 |      50 |          50 |      3.02  |  3      |   3.08  |           2.04   |        0       |            0.877    |      1     |           1     |    0.5   |
| fixed       | n/2 |  8      |  50 |  25 |      50 |          50 |      3.5   |  3.5    |   3.56  |           2.52   |        0       |            0.924    |      1     |           1     |    0.5   |
| fixed       | n/2 |  9      |  50 |  25 |      50 |          50 |      4     |  4      |   4.04  |           3.02   |        0       |            0.954    |      1     |           1     |    0.5   |
| fixed       | n/2 | 10      |  50 |  25 |      50 |          50 |      4.5   |  4.5    |   4.54  |           3.52   |        0       |            0.974    |      1     |           1     |    0.5   |
| fixed       | n/2 |  2      |  60 |  30 |      50 |          50 |      0.858 |  0.817  |   0.95  |           0      |        0.58    |            0.029    |      0.402 |           0.386 |    0.5   |
| fixed       | n/2 |  3      |  60 |  30 |      50 |          50 |      1.22  |  1.12   |   1.32  |           0.242  |        0       |            0.421    |      0.976 |           0.973 |    0.5   |
| fixed       | n/2 |  4      |  60 |  30 |      50 |          50 |      1.63  |  1.57   |   1.72  |           0.65   |        0       |            0.592    |      1     |           1     |    0.5   |
| fixed       | n/2 |  5      |  60 |  30 |      50 |          50 |      2.07  |  2      |   2.15  |           1.08   |        0       |            0.735    |      1     |           1     |    0.5   |
| fixed       | n/2 |  6      |  60 |  30 |      50 |          50 |      2.54  |  2.5    |   2.58  |           1.56   |        0       |            0.811    |      1     |           1     |    0.5   |
| fixed       | n/2 |  7      |  60 |  30 |      50 |          50 |      3.02  |  3      |   3.05  |           2.03   |        0       |            0.885    |      1     |           1     |    0.5   |
| fixed       | n/2 |  8      |  60 |  30 |      50 |          50 |      3.52  |  3.5    |   3.57  |           2.53   |        0       |            0.924    |      1     |           1     |    0.5   |
| fixed       | n/2 |  9      |  60 |  30 |      50 |          50 |      4     |  4      |   4.05  |           3.02   |        0       |            0.951    |      1     |           1     |    0.5   |
| fixed       | n/2 | 10      |  60 |  30 |      50 |          50 |      4.5   |  4.5    |   4.53  |           3.52   |        0       |            0.972    |      1     |           1     |    0.5   |
| fixed       | n/2 |  2      |  75 |  37 |      50 |          50 |      0.853 |  0.787  |   0.92  |           0      |        0.52    |            0.024    |      0.359 |           0.342 |    0.498 |
| fixed       | n/2 |  3      |  75 |  37 |      50 |          50 |      1.2   |  1.15   |   1.28  |           0.227  |        0       |            0.407    |      0.986 |           0.983 |    0.498 |
| fixed       | n/2 |  4      |  75 |  37 |      50 |          50 |      1.61  |  1.55   |   1.69  |           0.633  |        0       |            0.586    |      0.999 |           0.999 |    0.498 |
| fixed       | n/2 |  5      |  75 |  37 |      50 |          50 |      2.04  |  1.99   |   2.11  |           1.05   |        0       |            0.715    |      1     |           1     |    0.498 |
| fixed       | n/2 |  6      |  75 |  37 |      50 |          50 |      2.51  |  2.47   |   2.55  |           1.52   |        0       |            0.812    |      1     |           1     |    0.498 |
| fixed       | n/2 |  7      |  75 |  37 |      50 |          50 |      2.99  |  2.96   |   3.04  |           2      |        0       |            0.862    |      1     |           1     |    0.498 |
| fixed       | n/2 |  8      |  75 |  37 |      50 |          50 |      3.47  |  3.45   |   3.49  |           2.48   |        0       |            0.91     |      1     |           1     |    0.498 |
| fixed       | n/2 |  9      |  75 |  37 |      50 |          50 |      3.96  |  3.95   |   3.99  |           2.97   |        0       |            0.94     |      1     |           1     |    0.498 |
| fixed       | n/2 | 10      |  75 |  37 |      50 |          50 |      4.44  |  4.44   |   4.47  |           3.45   |        0       |            0.971    |      1     |           1     |    0.498 |
| fixed       | n/2 |  4      | 100 |  50 |      30 |          30 |      1.63  |  1.59   |   1.7   |           0.645  |        0       |            0.593    |      0.998 |           0.997 |    0.5   |
| fixed       | n/2 |  5      | 100 |  50 |      30 |          30 |      2.07  |  2.04   |   2.13  |           1.08   |        0       |            0.717    |      1     |           1     |    0.5   |
| fixed       | n/2 |  6      | 100 |  50 |      30 |          30 |      2.54  |  2.5    |   2.58  |           1.55   |        0       |            0.8      |      1     |           1     |    0.5   |
| fixed       | n/2 |  7      | 100 |  50 |      30 |          30 |      3.03  |  3.01   |   3.06  |           2.04   |        0       |            0.872    |      1     |           1     |    0.5   |
| fixed       | n/2 |  8      | 100 |  50 |      30 |          30 |      3.51  |  3.5    |   3.56  |           2.52   |        0       |            0.913    |      1     |           1     |    0.5   |
| fixed       | n   |  2      |  10 |  10 |     150 |         150 |      1.1   |  1      |   1.3   |           0.2    |        0       |            0.499    |      0.943 |           0.934 |    0.618 |
| fixed       | n   |  3      |  10 |  10 |     150 |         150 |      2     |  2      |   2.2   |           1.1    |        0       |            0.848    |      1     |           1     |    0.618 |
| fixed       | n   |  4      |  10 |  10 |     150 |         150 |      3     |  3      |   3.1   |           2.1    |        0       |            0.949    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  10 |  10 |     150 |         150 |      4     |  4      |   4     |           3.1    |        0       |            0.991    |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  10 |  10 |     150 |         150 |      5     |  5      |   5.1   |           4.1    |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  10 |  10 |     150 |         150 |      6     |  6      |   6     |           5.1    |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  10 |  10 |     150 |         150 |      7     |  7      |   7     |           6.1    |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  10 |  10 |     150 |         150 |      8     |  8      |   8     |           7.1    |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  10 |  10 |     150 |         150 |      9     |  9      |   9     |           8.1    |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  15 |  15 |     150 |         150 |      1.13  |  1      |   1.33  |           0.2    |        0       |            0.482    |      0.916 |           0.901 |    0.618 |
| fixed       | n   |  3      |  15 |  15 |     150 |         150 |      2     |  2      |   2.2   |           1.07   |        0       |            0.83     |      1     |           1     |    0.618 |
| fixed       | n   |  4      |  15 |  15 |     150 |         150 |      3     |  3      |   3.07  |           2.07   |        0       |            0.942    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  15 |  15 |     150 |         150 |      4     |  4      |   4.07  |           3.07   |        0       |            0.98     |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  15 |  15 |     150 |         150 |      5     |  5      |   5.07  |           4.07   |        0       |            0.993    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  15 |  15 |     150 |         150 |      6     |  6      |   6     |           5.07   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  15 |  15 |     150 |         150 |      7     |  7      |   7     |           6.07   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  15 |  15 |     150 |         150 |      8     |  8      |   8     |           7.07   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  15 |  15 |     150 |         150 |      9     |  9      |   9     |           8.07   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  20 |  20 |     150 |         150 |      1.1   |  1      |   1.3   |           0.2    |        0       |            0.487    |      0.931 |           0.916 |    0.618 |
| fixed       | n   |  3      |  20 |  20 |     150 |         150 |      2.05  |  2      |   2.15  |           1.1    |        0       |            0.819    |      1     |           1     |    0.618 |
| fixed       | n   |  4      |  20 |  20 |     150 |         150 |      3     |  3      |   3.1   |           2.05   |        0       |            0.936    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  20 |  20 |     150 |         150 |      4     |  4      |   4.05  |           3.05   |        0       |            0.978    |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  20 |  20 |     150 |         150 |      5     |  5      |   5.05  |           4.05   |        0       |            0.993    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  20 |  20 |     150 |         150 |      6     |  6      |   6     |           5.05   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  20 |  20 |     150 |         150 |      7     |  7      |   7     |           6.05   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  20 |  20 |     150 |         150 |      8     |  8      |   8     |           7.05   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  20 |  20 |     150 |         150 |      9     |  9      |   9     |           8.05   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  25 |  25 |     150 |         150 |      1.12  |  1      |   1.32  |           0.2    |        0       |            0.496    |      0.93  |           0.915 |    0.618 |
| fixed       | n   |  3      |  25 |  25 |     150 |         150 |      2.04  |  2      |   2.16  |           1.08   |        0       |            0.818    |      0.999 |           0.999 |    0.618 |
| fixed       | n   |  4      |  25 |  25 |     150 |         150 |      3     |  3      |   3.08  |           2.04   |        0       |            0.931    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  25 |  25 |     150 |         150 |      4     |  4      |   4.08  |           3.04   |        0       |            0.968    |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  25 |  25 |     150 |         150 |      5     |  5      |   5.04  |           4.04   |        0       |            0.994    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  25 |  25 |     150 |         150 |      6     |  6      |   6.04  |           5.04   |        0       |            0.996    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  25 |  25 |     150 |         150 |      7     |  7      |   7.04  |           6.04   |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  25 |  25 |     150 |         150 |      8     |  8      |   8     |           7.04   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  25 |  25 |     150 |         150 |      9     |  9      |   9     |           8.04   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  30 |  30 |     150 |         150 |      1.13  |  1      |   1.27  |           0.2    |        0       |            0.491    |      0.934 |           0.921 |    0.618 |
| fixed       | n   |  3      |  30 |  30 |     150 |         150 |      2.03  |  2      |   2.13  |           1.07   |        0       |            0.821    |      1     |           0.999 |    0.618 |
| fixed       | n   |  4      |  30 |  30 |     150 |         150 |      3     |  3      |   3.1   |           2.03   |        0       |            0.923    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  30 |  30 |     150 |         150 |      4     |  4      |   4.03  |           3.03   |        0       |            0.97     |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  30 |  30 |     150 |         150 |      5     |  5      |   5.07  |           4.03   |        0       |            0.989    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  30 |  30 |     150 |         150 |      6     |  6      |   6.03  |           5.03   |        0       |            0.994    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  30 |  30 |     150 |         150 |      7     |  7      |   7.03  |           6.03   |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  30 |  30 |     150 |         150 |      8     |  8      |   8     |           7.03   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  30 |  30 |     150 |         150 |      9     |  9      |   9     |           8.03   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  35 |  35 |     150 |         150 |      1.14  |  1.03   |   1.26  |           0.2    |        0       |            0.487    |      0.934 |           0.918 |    0.618 |
| fixed       | n   |  3      |  35 |  35 |     150 |         150 |      2.06  |  2      |   2.14  |           1.09   |        0       |            0.804    |      1     |           1     |    0.618 |
| fixed       | n   |  4      |  35 |  35 |     150 |         150 |      3     |  3      |   3.06  |           2.03   |        0       |            0.918    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  35 |  35 |     150 |         150 |      4     |  4      |   4.03  |           3.03   |        0       |            0.97     |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  35 |  35 |     150 |         150 |      5     |  5      |   5.03  |           4.03   |        0       |            0.991    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  35 |  35 |     150 |         150 |      6     |  6      |   6     |           5.03   |        0       |            0.997    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  35 |  35 |     150 |         150 |      7     |  7      |   7     |           6.03   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  35 |  35 |     150 |         150 |      8     |  8      |   8.03  |           7.03   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  35 |  35 |     150 |         150 |      9     |  9      |   9     |           8.03   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  40 |  40 |     150 |         150 |      1.12  |  1.02   |   1.23  |           0.175  |        0       |            0.477    |      0.943 |           0.928 |    0.618 |
| fixed       | n   |  3      |  40 |  40 |     150 |         150 |      2.05  |  2      |   2.15  |           1.07   |        0       |            0.813    |      1     |           1     |    0.618 |
| fixed       | n   |  4      |  40 |  40 |     150 |         150 |      3     |  3      |   3.05  |           2.02   |        0       |            0.919    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  40 |  40 |     150 |         150 |      4     |  4      |   4.05  |           3.02   |        0       |            0.97     |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  40 |  40 |     150 |         150 |      5     |  5      |   5.03  |           4.03   |        0       |            0.987    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  40 |  40 |     150 |         150 |      6     |  6      |   6.03  |           5.03   |        0       |            0.996    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  40 |  40 |     150 |         150 |      7     |  7      |   7.03  |           6.03   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  40 |  40 |     150 |         150 |      8     |  8      |   8     |           7.03   |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  40 |  40 |     150 |         150 |      9     |  9      |   9     |           8.03   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  50 |  50 |      50 |          50 |      1.13  |  1.06   |   1.22  |           0.18   |        0       |            0.478    |      0.944 |           0.928 |    0.618 |
| fixed       | n   |  3      |  50 |  50 |      50 |          50 |      2.04  |  2      |   2.12  |           1.06   |        0       |            0.809    |      1     |           1     |    0.618 |
| fixed       | n   |  4      |  50 |  50 |      50 |          50 |      3.02  |  3      |   3.08  |           2.04   |        0       |            0.908    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  50 |  50 |      50 |          50 |      4     |  4      |   4.04  |           3.02   |        0       |            0.961    |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  50 |  50 |      50 |          50 |      5     |  5      |   5.02  |           4.02   |        0       |            0.986    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  50 |  50 |      50 |          50 |      6     |  6      |   6     |           5.02   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  50 |  50 |      50 |          50 |      7     |  7      |   7.02  |           6.02   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  50 |  50 |      50 |          50 |      8     |  8      |   8.02  |           7.02   |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  50 |  50 |      50 |          50 |      9     |  9      |   9     |           8.02   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  60 |  60 |      50 |          50 |      1.12  |  1.03   |   1.18  |           0.183  |        0       |            0.467    |      0.921 |           0.902 |    0.618 |
| fixed       | n   |  3      |  60 |  60 |      50 |          50 |      2.05  |  2      |   2.12  |           1.07   |        0       |            0.802    |      0.999 |           0.999 |    0.618 |
| fixed       | n   |  4      |  60 |  60 |      50 |          50 |      3.02  |  3      |   3.07  |           2.03   |        0       |            0.908    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  60 |  60 |      50 |          50 |      4     |  4      |   4.03  |           3.02   |        0       |            0.963    |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  60 |  60 |      50 |          50 |      5     |  5      |   5.02  |           4.02   |        0       |            0.987    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  60 |  60 |      50 |          50 |      6     |  6      |   6.02  |           5.02   |        0       |            0.993    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  60 |  60 |      50 |          50 |      7     |  7      |   7     |           6.02   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  60 |  60 |      50 |          50 |      8     |  8      |   8     |           7.02   |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  60 |  60 |      50 |          50 |      9     |  9      |   9     |           8.02   |        0       |            1        |      1     |           1     |    0.618 |
| fixed       | n   |  2      |  75 |  75 |      50 |          50 |      1.13  |  1.05   |   1.2   |           0.16   |        0       |            0.469    |      0.941 |           0.926 |    0.618 |
| fixed       | n   |  3      |  75 |  75 |      50 |          50 |      2.04  |  2.01   |   2.11  |           1.05   |        0       |            0.812    |      0.999 |           0.999 |    0.618 |
| fixed       | n   |  4      |  75 |  75 |      50 |          50 |      3.01  |  3      |   3.05  |           2.03   |        0       |            0.917    |      1     |           1     |    0.618 |
| fixed       | n   |  5      |  75 |  75 |      50 |          50 |      4     |  4      |   4.03  |           3.01   |        0       |            0.962    |      1     |           1     |    0.618 |
| fixed       | n   |  6      |  75 |  75 |      50 |          50 |      5     |  5      |   5.01  |           4.01   |        0       |            0.987    |      1     |           1     |    0.618 |
| fixed       | n   |  7      |  75 |  75 |      50 |          50 |      6     |  6      |   6.01  |           5.01   |        0       |            0.995    |      1     |           1     |    0.618 |
| fixed       | n   |  8      |  75 |  75 |      50 |          50 |      7     |  7      |   7.01  |           6.01   |        0       |            0.997    |      1     |           1     |    0.618 |
| fixed       | n   |  9      |  75 |  75 |      50 |          50 |      8     |  8      |   8     |           7.01   |        0       |            0.998    |      1     |           1     |    0.618 |
| fixed       | n   | 10      |  75 |  75 |      50 |          50 |      9     |  9      |   9     |           8.01   |        0       |            0.999    |      1     |           1     |    0.618 |
| fixed       | n   |  2      | 100 | 100 |      25 |          25 |      1.13  |  1.08   |   1.19  |           0.17   |        0       |            0.486    |      0.946 |           0.931 |    0.618 |
| fixed       | n   |  3      | 100 | 100 |       5 |           0 |      2.05  |  2.04   |   2.08  |           1.07   |        0       |            0.792    |      0.996 |           0.994 |    0.618 |
| fixed       | n   |  4      | 100 | 100 |       5 |           1 |      3.02  |  3      |   3.03  |           2.03   |        0       |            0.908    |      1     |           1     |    0.618 |
| fixed       | 2n  |  2      |  10 |  20 |     150 |         150 |      2     |  2      |   2.2   |           1.1    |        0       |            0.924    |      1     |           1     |    0.732 |
| fixed       | 2n  |  3      |  10 |  20 |     150 |         150 |      4     |  4      |   4.1   |           3.1    |        0       |            0.993    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  10 |  20 |     150 |         150 |      6     |  6      |   6     |           5.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  10 |  20 |     150 |         150 |      8     |  8      |   8     |           7.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  10 |  20 |     150 |         150 |     10     | 10      |  10     |           9.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  10 |  20 |     150 |         150 |     12     | 12      |  12     |          11.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  10 |  20 |     150 |         150 |     14     | 14      |  14     |          13.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  10 |  20 |     150 |         150 |     16     | 16      |  16     |          15.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  10 |  20 |     150 |         150 |     18     | 18      |  18     |          17.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  15 |  30 |     150 |         150 |      2     |  2      |   2.13  |           1.07   |        0       |            0.925    |      0.999 |           0.998 |    0.732 |
| fixed       | 2n  |  3      |  15 |  30 |     150 |         150 |      4     |  4      |   4.07  |           3.07   |        0       |            0.986    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  15 |  30 |     150 |         150 |      6     |  6      |   6     |           5.07   |        0       |            0.999    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  15 |  30 |     150 |         150 |      8     |  8      |   8     |           7.07   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  15 |  30 |     150 |         150 |     10     | 10      |  10     |           9.07   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  15 |  30 |     150 |         150 |     12     | 12      |  12     |          11.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  15 |  30 |     150 |         150 |     14     | 14      |  14     |          13.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  15 |  30 |     150 |         150 |     16     | 16      |  16     |          15.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  15 |  30 |     150 |         150 |     18     | 18      |  18     |          17.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  20 |  40 |     150 |         150 |      2     |  2      |   2.15  |           1.05   |        0       |            0.915    |      1     |           1     |    0.732 |
| fixed       | 2n  |  3      |  20 |  40 |     150 |         150 |      4     |  4      |   4.05  |           3.05   |        0       |            0.987    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  20 |  40 |     150 |         150 |      6     |  6      |   6.05  |           5.05   |        0       |            0.998    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  20 |  40 |     150 |         150 |      8     |  8      |   8     |           7.05   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  20 |  40 |     150 |         150 |     10     | 10      |  10     |           9.05   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  20 |  40 |     150 |         150 |     12     | 12      |  12     |          11.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  20 |  40 |     150 |         150 |     14     | 14      |  14     |          13.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  20 |  40 |     150 |         150 |     16     | 16      |  16     |          15.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  20 |  40 |     150 |         150 |     18     | 18      |  18     |          17.1    |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  25 |  50 |     150 |         150 |      2     |  2      |   2.08  |           1.04   |        0       |            0.906    |      0.999 |           0.999 |    0.732 |
| fixed       | 2n  |  3      |  25 |  50 |     150 |         150 |      4     |  4      |   4.04  |           3.04   |        0       |            0.988    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  25 |  50 |     150 |         150 |      6     |  6      |   6     |           5.04   |        0       |            0.999    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  25 |  50 |     150 |         150 |      8     |  8      |   8     |           7.04   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  25 |  50 |     150 |         150 |     10     | 10      |  10     |           9.04   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  25 |  50 |     150 |         150 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  25 |  50 |     150 |         150 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  25 |  50 |     150 |         150 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  25 |  50 |     150 |         150 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  30 |  60 |     150 |         150 |      2     |  2      |   2.07  |           1.03   |        0       |            0.914    |      1     |           0.999 |    0.732 |
| fixed       | 2n  |  3      |  30 |  60 |     150 |         150 |      4     |  4      |   4.03  |           3.03   |        0       |            0.985    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  30 |  60 |     150 |         150 |      6     |  6      |   6     |           5.03   |        0       |            0.999    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  30 |  60 |     150 |         150 |      8     |  8      |   8     |           7.03   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  30 |  60 |     150 |         150 |     10     | 10      |  10     |           9.03   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  30 |  60 |     150 |         150 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  30 |  60 |     150 |         150 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  30 |  60 |     150 |         150 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  30 |  60 |     150 |         150 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  35 |  70 |     150 |         150 |      2     |  2      |   2.11  |           1.03   |        0       |            0.905    |      1     |           0.999 |    0.732 |
| fixed       | 2n  |  3      |  35 |  70 |     150 |         150 |      4     |  4      |   4.03  |           3.03   |        0       |            0.987    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  35 |  70 |     150 |         150 |      6     |  6      |   6     |           5.03   |        0       |            0.998    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  35 |  70 |     150 |         150 |      8     |  8      |   8     |           7.03   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  35 |  70 |     150 |         150 |     10     | 10      |  10     |           9.03   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  35 |  70 |     150 |         150 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  35 |  70 |     150 |         150 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  35 |  70 |     150 |         150 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  35 |  70 |     150 |         150 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  40 |  80 |     150 |         150 |      2     |  2      |   2.08  |           1.04   |        0       |            0.911    |      0.999 |           0.998 |    0.732 |
| fixed       | 2n  |  3      |  40 |  80 |     150 |         150 |      4     |  4      |   4.03  |           3.02   |        0       |            0.987    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  40 |  80 |     150 |         150 |      6     |  6      |   6.03  |           5.03   |        0       |            0.999    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  40 |  80 |     150 |         150 |      8     |  8      |   8     |           7.03   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  40 |  80 |     150 |         150 |     10     | 10      |  10     |           9.03   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  40 |  80 |     150 |         150 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  40 |  80 |     150 |         150 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  40 |  80 |     150 |         150 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  40 |  80 |     150 |         150 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  50 | 100 |      50 |          50 |      2.02  |  2      |   2.04  |           1.04   |        0       |            0.906    |      1     |           1     |    0.732 |
| fixed       | 2n  |  3      |  50 | 100 |      50 |          50 |      4     |  4      |   4.02  |           3.02   |        0       |            0.984    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  50 | 100 |      50 |          50 |      6     |  6      |   6     |           5.02   |        0       |            0.998    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  50 | 100 |      50 |          50 |      8     |  8      |   8     |           7.02   |        0       |            0.999    |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  50 | 100 |      50 |          50 |     10     | 10      |  10     |           9.02   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  50 | 100 |      50 |          50 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  50 | 100 |      50 |          50 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  50 | 100 |      50 |          50 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  50 | 100 |      50 |          50 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  60 | 120 |      50 |          50 |      2.02  |  2      |   2.07  |           1.03   |        0       |            0.907    |      0.999 |           0.999 |    0.732 |
| fixed       | 2n  |  3      |  60 | 120 |      50 |          50 |      4     |  4      |   4.03  |           3.02   |        0       |            0.982    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  60 | 120 |      50 |          50 |      6     |  6      |   6.02  |           5.02   |        0       |            0.998    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  60 | 120 |      50 |          50 |      8     |  8      |   8     |           7.02   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  60 | 120 |      50 |          50 |     10     | 10      |  10     |           9.02   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  60 | 120 |      50 |          50 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  60 | 120 |      50 |          50 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  60 | 120 |      50 |          50 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  60 | 120 |      50 |          50 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  2      |  75 | 150 |      50 |          49 |      2.01  |  2      |   2.05  |           1.03   |        0       |            0.906    |      0.999 |           0.998 |    0.732 |
| fixed       | 2n  |  3      |  75 | 150 |      50 |          50 |      4     |  4      |   4.01  |           3.01   |        0       |            0.984    |      1     |           1     |    0.732 |
| fixed       | 2n  |  4      |  75 | 150 |      50 |          50 |      6     |  6      |   6     |           5.01   |        0       |            0.997    |      1     |           1     |    0.732 |
| fixed       | 2n  |  5      |  75 | 150 |      50 |          50 |      8     |  8      |   8     |           7.01   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  6      |  75 | 150 |      50 |          50 |     10     | 10      |  10     |           9.01   |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  7      |  75 | 150 |      50 |          50 |     12     | 12      |  12     |          11      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  8      |  75 | 150 |      50 |          50 |     14     | 14      |  14     |          13      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  |  9      |  75 | 150 |      50 |          50 |     16     | 16      |  16     |          15      |        0       |            1        |      1     |           1     |    0.732 |
| fixed       | 2n  | 10      |  75 | 150 |      50 |          50 |     18     | 18      |  18     |          17      |        0       |            1        |      1     |           1     |    0.732 |


</details>

#### Per simulation cell

| generator             | r   |   param |   n |   m |   count |   certified |   e median |   e min |   e max |   gamma/n median |   forest share |   2-core cust share |   lcc frac |   lcc cust frac |   e_g(r) |
|:----------------------|:----|--------:|----:|----:|--------:|------------:|-----------:|--------:|--------:|-----------------:|---------------:|--------------------:|-----------:|----------------:|---------:|
| bern_padC1_padP2_conn | n   |       2 |  30 |  30 |    1000 |        1000 |       1.6  |    1.2  |    2.13 |            0.633 |              0 |               0.741 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       4 |  30 |  30 |    1000 |        1000 |       3.1  |    2.2  |    4.17 |            2.13  |              0 |               0.931 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       6 |  30 |  30 |    1000 |        1000 |       5    |    3.9  |    6.17 |            4.03  |              0 |               0.989 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       8 |  30 |  30 |     300 |         300 |       7    |    5.7  |    8.03 |            6.03  |              0 |               0.998 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |      10 |  30 |  30 |     300 |         300 |       8.97 |    7.8  |   10.1  |            8     |              0 |               1     |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       2 |  40 |  40 |    1000 |        1000 |       1.6  |    1.27 |    2.17 |            0.625 |              0 |               0.736 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       4 |  40 |  40 |    1000 |        1000 |       3.1  |    2.38 |    4.03 |            2.12  |              0 |               0.926 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       6 |  40 |  40 |    1000 |        1000 |       5    |    4.03 |    6.38 |            4.03  |              0 |               0.987 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |       8 |  40 |  40 |     300 |         300 |       7    |    5.9  |    8.05 |            6.03  |              0 |               0.999 |          1 |               1 |    0.618 |
| bern_padC1_padP2_conn | n   |      10 |  40 |  40 |     300 |         300 |       9    |    7.95 |   10.3  |            8.03  |              0 |               1     |          1 |               1 |    0.618 |

#### The 338 bound-gap instances against the rest of the corpus at equal (n, m)

| quantity   |   gap instances with >= 5 peers |   percentile q25 |   percentile median |   percentile q75 |   share below cell median |
|:-----------|--------------------------------:|-----------------:|--------------------:|-----------------:|--------------------------:|
| e          |                             229 |          0.00805 |              0.0742 |            0.172 |                     0.974 |
| gamma/n    |                             229 |          0.00805 |              0.0742 |            0.175 |                     0.974 |

|   n |   m |   gap |   rest |   e gap median |   e rest median |   gamma/n gap median |   gamma/n rest median |   forest share gap |   forest share rest | collections                           |
|----:|----:|------:|-------:|---------------:|----------------:|---------------------:|----------------------:|-------------------:|--------------------:|:--------------------------------------|
|  20 |  10 |    13 |    697 |           1.95 |            3.7  |                1     |                 2.75  |                  0 |                   0 | Harvey, Simonis                       |
|  20 |  20 |     4 |    536 |           2.67 |            6    |                1.73  |                 5.05  |                  0 |                   0 | Harvey, Simonis                       |
|  30 |  10 |    86 |    654 |           2.17 |            4.07 |                1.2   |                 3.1   |                  0 |                   0 | Harvey, Simonis                       |
|  30 |  15 |    35 |    435 |           2.13 |            5.27 |                1.17  |                 4.3   |                  0 |                   0 | Faggioli-Bentivoglio, Harvey, Simonis |
|  30 |  20 |     1 |      9 |           1.7  |            1.77 |                0.733 |                 0.8   |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  30 |  25 |     3 |      7 |           2.1  |            2.13 |                1.13  |                 1.17  |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  30 |  30 |     8 |    547 |           2    |            8    |                1.03  |                 7.03  |                  0 |                   0 | Chu & Stuckey, Harvey                 |
|  37 |  40 |     1 |      1 |           2.59 |            2.62 |                1.62  |                 1.65  |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  38 |  40 |     2 |      4 |           2.57 |            2.58 |                1.59  |                 1.61  |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  39 |  40 |     2 |      0 |           2.55 |          nan    |                1.58  |               nan     |                  0 |                 nan | Faggioli-Bentivoglio                  |
|  40 |  15 |     5 |      5 |           1.2  |            1.15 |                0.225 |                 0.2   |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  40 |  20 |    11 |    109 |           1.45 |            8.62 |                0.475 |                 7.65  |                  0 |                   0 | Faggioli-Bentivoglio, Simonis         |
|  40 |  25 |    10 |      0 |           1.66 |          nan    |                0.688 |               nan     |                  0 |                 nan | Faggioli-Bentivoglio                  |
|  40 |  30 |    10 |      0 |           1.9  |          nan    |                0.925 |               nan     |                  0 |                 nan | Faggioli-Bentivoglio                  |
|  40 |  40 |     6 |     19 |           1.96 |            6.53 |                0.987 |                 5.55  |                  0 |                   0 | Chu & Stuckey                         |
|  50 |  15 |     2 |      8 |           1.1  |            1.08 |                0.14  |                 0.12  |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  50 |  20 |     6 |      4 |           1.23 |            1.19 |                0.25  |                 0.23  |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  50 |  25 |    10 |      0 |           1.43 |          nan    |                0.45  |               nan     |                  0 |                 nan | Faggioli-Bentivoglio                  |
|  50 |  30 |     9 |      1 |           1.62 |            1.44 |                0.64  |                 0.46  |                  0 |                   0 | Faggioli-Bentivoglio                  |
|  50 |  40 |    10 |      0 |           2.03 |          nan    |                1.05  |               nan     |                  0 |                 nan | Faggioli-Bentivoglio                  |
|  50 |  50 |    12 |     23 |           2.42 |            9.04 |                1.44  |                 8.06  |                  0 |                   0 | Challenge, Chu & Stuckey, Wilson      |
|  50 | 100 |     5 |     20 |           3.14 |           12    |                2.16  |                11     |                  0 |                   0 | Chu & Stuckey                         |
|  75 |  75 |    17 |     10 |           3.19 |            8.11 |                2.2   |                 7.13  |                  0 |                   0 | Challenge, Chu & Stuckey, Wilson      |
|  79 |  21 |     1 |      0 |           1.34 |          nan    |                0.354 |               nan     |                  0 |                 nan | SCOOP                                 |
| 100 |  50 |    23 |      2 |           2.88 |            1.17 |                1.89  |                 0.185 |                  0 |                   0 | Chu & Stuckey                         |
| 100 | 100 |    21 |     14 |           3.85 |           53.3  |                2.86  |                52.3   |                  0 |                   0 | Challenge, Chu & Stuckey, Wilson      |
| 105 |  37 |     1 |      0 |           1.37 |          nan    |                0.39  |               nan     |                  0 |                 nan | SCOOP                                 |
| 125 | 125 |    23 |      2 |           5.09 |            9.3  |                4.1   |                 8.31  |                  0 |                   0 | Chu & Stuckey                         |
| 134 |  37 |     1 |      0 |           1.34 |          nan    |                0.343 |               nan     |                  0 |                 nan | SCOOP                                 |

## 2. `opt / n` against the excess: one parameter, or two? (item 02, 2026-11-01)

**Question.** B(i) and B(iii) of the plan. On random clique covers, is
`lim opt / n` a function of the excess `e` alone, or of `(d, μ)` separately?
And how far is the two-key closing rule from the exact optimum as a function
of `e`?

**What was done.** No instance was solved. Two computations on what is on
record:

1. **The two-key rule on every instance** (`satisfiability.heuristics.two_key_rule`,
   registered 2026-09-27, after the ensemble campaign ran, so the four frames
   lacked it): the 50,715 ensemble instances regenerated from their seeds and
   the 6,376 corpus instances, one call each, 30 s of rule time in all and 7 s
   wall on 8 workers, written with the certified optimum and the pattern-size
   histogram to `learning/data/excess_rule.csv` (57,091 rows; git-ignored
   under `learning/data/*`; never the compute ledger).
2. **Per series `(generator, r, d or p)` with three or more sizes at `n ≥ 30`**,
   the fit `opt = a + b n` by least squares over the certified instances (one
   point per instance, so the standard error of `b` carries the within-cell
   spread), the same fit for the rule's value, the realised `e` (mean over the
   fitted instances), `β*(d, μ)` of `learning/first_moment.py` at the series'
   pooled size histogram and `μ = m / n`, and the rule's exactness and gap.
   72 series: 36 fixed-`d`, 31 Bernoulli, and the 5 Chu & Stuckey `m = n`
   classes across `n = 30, 40, 50, 75, 100, 125`.

`learning/first_moment.py` is the asymptotic constant of
`reports/scratch/clique_cover_moment/asymptotic_cs.py` and the finite floor of
`bound_lib.py` / `finite_bound_cs.py`, moved with the same formulas;
`tests/test_first_moment.py` reproduces `asymptotic_cs.log` (the `β*(d, μ)`
table at every entry, the threshold `d > 2.0031`, five classes at empirical
sizes) and `finite_bound_cs.log` (five classes' mean floors) to the printed
digits, and checks that the histogram interface agrees with the list one to
10⁻¹².

**Size range.** `n = 10–100` for the rule (30–125 with the Chu & Stuckey
classes); slopes fitted on `n ≥ 30` (30–100 ensemble, 30–125 Chu & Stuckey).

**Regenerate.**

```
python -m learning.excess --stage rule          # -> learning/data/excess_rule.csv, 7 s on 8 workers
python -m learning.excess --stage slopes        # the tables below
python -m learning.excess --stage figure-opt    # reports/figures/excess_opt.png
python -m learning.first_moment                 # the two scratch tables from the benchmark files
python -m pytest tests/test_first_moment.py tests/test_excess.py -q
```

### 2.1 Findings

1. **Which series test the hypothesis.** A fixed-`d` series has `e = r (d − 1)`
   up to the generator's padding and is constant in `n` (range over `n` at most
   0.01 of its mean); the Chu & Stuckey classes vary by 5–8% of their mean
   across `n` (the `n = 100` cell sits 0.3–1.7 below the others at every `d`).
   A **Bernoulli series at fixed `p` is not a constant-excess series**: `e = r (n p − 1)`
   grows with `n`, by 0.16 to 17.9 across the fitted sizes, its intercepts
   `a` run to −26 and its "slopes" exceed 1 (the optimum cannot exceed `n`), so
   those fits are the local slope along a path of rising density and say
   nothing about `opt / n` at fixed `e`. The kill count is therefore taken on
   the pairs of two constant-`e` series (fixed `d` or Chu & Stuckey, `e`
   constant to within 10% of its mean), with the all-pairs count beside it.

2. **The one-parameter hypothesis is dead.** Of the 16 constant-`e` pairs
   with realised `e` within ±0.05 and different `(generator, d, μ)`, **13 differ
   by more than twice the larger standard error** (26 of all 30 pairs). The
   item's own groups, all on record at `n = 50–100`:

   | nominal `e` | `(d, μ)` | realised `e` | `b` | `β*` | `b − β*` |
   |---|---|---|---|---|---|
   | 2 | (9, ¼) | 2.05 | 0.282 ± 0.006 | 0.180 | 0.10 |
   | 2 | (5, ½) | 2.06 | 0.232 ± 0.005 | 0.169 | 0.06 |
   | 2 | (3, 1) | 2.04 | 0.200 ± 0.003 | 0.147 | 0.05 |
   | 2 | (2, 2) | 2.02 | 0.167 ± 0.002 | 0.123 | 0.04 |
   | 3 | (7, ½) | 3.01 | 0.400 ± 0.005 | 0.327 | 0.07 |
   | 3 | (4, 1) | 3.02 | 0.348 ± 0.003 | 0.288 | 0.06 |
   | 3 | (12, ¼) | 2.73 (outside ±0.05) | 0.405 ± 0.006 | 0.306 | 0.10 |
   | 4 | (9, ½) | 3.99 | 0.517 ± 0.011 | 0.463 | 0.05 |
   | 4 | (5, 1) | 4.00 | 0.479 ± 0.003 | 0.411 | 0.07 |
   | 4 | (3, 2) | 4.00 | 0.409 ± 0.003 | 0.356 | 0.05 |
   | 6 | (7, 1) | 6.00 | 0.651 ± 0.003 | 0.595 | 0.06 |
   | 6 | (4, 2) | 6.00 | 0.568 ± 0.003 | 0.525 | 0.04 |
   | 8 | (9, 1) | 8.00 | 0.752 ± 0.002 | 0.714 | 0.04 |
   | 8 | (5, 2) | 8.00 | 0.685 ± 0.002 | 0.642 | 0.04 |

   (`±` is one standard error.) At every excess, **the slope falls with `μ`
   at fixed `e`**: at `e = 2` from 0.282 (few, large patterns, `μ = ¼`) to
   0.167 (many small ones, `μ = 2`), a spread of 0.115 against a standard
   error of 0.006 — twenty times the noise. The three pairs that do not
   differ are `(4, ¼)` against `(2, 1)` at `e ≈ 1.1` (both near the
   threshold, slopes 0.03–0.04), `(7, ¼)` against `(4, ½)` at `e ≈ 1.62`, and
   the fixed `(10, 1)` series against the Chu & Stuckey `d = 10` class, which
   is the same model with padding. `e` sets the scale of `opt / n`
   (correlation of `b` with `log e` 0.988 over the 41 constant-`e` series) and
   `μ` moves it by up to 0.1 at fixed `e`; so **`lim opt / n`, if it exists,
   is a function of `(d, μ)` and not of `e` alone.**

3. **The first moment has the two-parameter dependence in the right
   direction.** `β*(d, μ)` falls with `μ` at fixed `e` exactly as `b` does
   (at `e = 2`: 0.180, 0.169, 0.147, 0.123 against 0.282, 0.232, 0.200,
   0.167), and over the 41 constant-`e` series `b = 0.057 + 0.984 β*` with
   residual standard deviation **0.024** (0.015 with a quadratic), against
   0.042 for the best line in `log e` (0.033 for a cubic). The slack
   `b − β*` is 0.005–0.108, median 0.053, and **peaks on the ridge**: mean
   0.026 at `e ≤ 1.5`, 0.069–0.071 at `e = 1.5–4`, 0.036 at `e > 6`, largest
   on the `μ = ¼` series at `e = 1.8–2.7` (0.09–0.11). `β*` is not the
   constant either: of 30 pairs matched in `β*` to ±0.02, 14 differ in `b`.
   But the first moment is a far better one-parameter coordinate for
   `opt / n` than the excess is, which is what item 08's structured count has
   to improve on and item 09's ridge hypothesis stands on.

4. **The rule.** Over all 57,077 certified instances the bare two-key rule
   (no DFS behind it) is exact on 83.3% of the corpus and 62.2% of the
   ensembles; on the 200 Chu & Stuckey instances it is exact on 27%, mean
   gap 2.35, worst 10 (the `125 × 125` `d = 2` and `d = 4` classes, mean
   gaps 6.8). **Its gap peaks on the ridge** in every source: on the
   ensembles the exact share falls from 98% at `e < 0.62` to 22% at
   `e ∈ [1.5, 2)` and 27% at `[2.4, 3)`, then climbs to 91% at `e ≥ 10`; the
   mean gap per customer is 0.03–0.04 at `e = 1.5–3` and below 0.002 at the
   ends. The worst gap is 14 (`n = 100`, `m = 50`, `e = 2.5`, optimum 37,
   rule 51), and every one of the ten worst cases is at `n = 100` with
   `m ≤ n / 2`. Per constant-`e` series, the rule's `width / n` at the largest
   `n` sits 0.04–0.15 above `b` (median 0.08), by more at small `μ`; and on
   the ridge the rule's excess per customer grows with `n` (0.03 at `n = 30`,
   0.046 at 75, 0.058 at 100), so the rule's `width / n` is not an estimate
   of the slope at the largest sizes, and item 05 should expect it to drift
   upward at `n = 1,000–5,000`.

5. **A stale table, corrected in passing.** `learning/data/instances.csv`
   (2026-09-25) carries `provenance = solution` for four `125 × 125`
   instances certified in October 2026 (`Random-125-125-2-2_0`, `2-3_0`,
   `2-5_0`, `4-4_0`); item 01's build took its corpus optima from it, so
   `learning/data/excess.csv` had 6,372 certified corpus rows. `corpus_rows`
   now reads the value and provenance from the solution file (read only), the
   map is rebuilt with 6,376 of 6,376 certified, and no number in §1 changes
   (none of its tables uses the optimum). The four values are right in
   `solutions/`; nothing was re-solved.

### 2.2 Kill verdict

**Met: the hypothesis "a function of `e` alone" is dead.** 13 of the 16
constant-`e` matched pairs (26 of all 30) have slopes that differ by more
than twice the larger standard error; the dependence on `μ` at fixed `e` is
monotone, twenty standard errors wide at `e = 2`, and the first moment has
it in the same direction. The finding recorded for items 05, 07, 08 and 09:
**the parameter of the constant is `(d, μ)`, or, to a residual of 0.024,
`β*(d, μ)`; the excess sets the threshold, the ridge and the scale, not the
value.**

### 2.3 What this does not claim

- **A limit.** `b` is a finite-range slope on `n = 30–100` (30–125 for the
  Chu & Stuckey classes). `opt / n` at the largest `n` is above `b` on every
  series (the intercepts `a` are 3–9), `pw / n` falls with `n` at every fixed
  density to 75, and §14 showed that constants fitted at `n ≤ 40` fail at
  125. Whether the two slopes of a differing pair converge as `n → ∞` is not
  tested here; what is shown is that at `n = 30–100` they differ by twenty
  standard errors, and that the first-moment constants, which are limits,
  differ in the same direction.
- **That `β*` is the constant.** `b = 0.057 + 0.984 β*` is a description of
  41 series, not a theorem; 14 of 30 `β*`-matched pairs still differ, and the
  slack peaks on the ridge where the solver also struggles.
- **Anything about the Bernoulli generator at fixed `p`.** Its series are not
  constant-excess series and were excluded from the kill count; its 31 fits
  are tabulated for completeness only.
- **That the rule is a bound.** It is a heuristic, exact on 83% of the corpus
  and worst on the ridge; `rule / n` is an upper envelope that drifts up with
  `n` there.

### 2.4 Figure

`reports/figures/excess_opt.png`: one panel per product ratio `r = m / n`,
the 41 constant-`e` series only (circles the fixed generator at `n = 30–100`,
squares the Chu & Stuckey classes at `n = 30–125`); against the realised `e`,
the certified slope `b` with its ±2 se bar (the bars are smaller than the
markers), the rule's `width / n` at the largest `n`, and `β*` at the realised
sizes. The grey line is `e = 1`, the band `e = 2–2.4`. Three quantities on
three categorical slots; the Bernoulli series are left out for the reason in
finding 1.

![opt / n against the excess](figures/excess_opt.png)

### 2.5 Tables, in full

Scored: 57077 certified instances (corpus 6376, ensemble 50701), rule time 30.1 s in all; series with >= 3 sizes at n >= 30: 72 (41 with e constant in n to within 10% of its mean; the Bernoulli series at fixed p have e growing with n and are not constant-e series). e-matched pairs (|Δe| <= 0.05, different (generator, d or p, mu)): 30, of which 26 differ by more than twice the larger standard error; among the 16 pairs of two constant-e series, 13 differ. Verdict: the one-parameter hypothesis is DEAD (slopes differ on at least half of the constant-e matched pairs).


#### Per series: opt = a + b n on n >= 30, the rule, beta*

| generator   | r   |   param |      e |   e range over n |    mu |   mean size | n sizes                     |   instances |        a |       b |     se b |   b rule |   opt/n at max n |   rule/n at max n |   beta* (sizes) |   beta* (fixed d) |   rule exact |   rule gap mean |   rule gap max |
|:------------|:----|--------:|-------:|-----------------:|------:|------------:|:----------------------------|------------:|---------:|--------:|---------:|---------:|-----------------:|------------------:|----------------:|------------------:|-------------:|----------------:|---------------:|
| fixed       | n/4 |   3     |  0.96  |         0.00433  | 0.243 |        4.95 | 50, 60, 75                  |         150 |   6.62   | 0.0166  | 0.00685  |   0.0501 |           0.106  |            0.128  |          0      |            0      |      0.313   |          1.2    |              5 |
| fixed       | n/4 |   4     |  1.09  |         0.0044   | 0.243 |        5.5  | 50, 60, 75                  |         150 |   6.97   | 0.0282  | 0.00634  |   0.072  |           0.122  |            0.164  |          0.0106 |            0      |      0.06    |          2.53   |              7 |
| fixed       | n/4 |   5     |  1.25  |         0.0172   | 0.243 |        6.16 | 50, 60, 75                  |         150 |   6.1    | 0.0787  | 0.00774  |   0.122  |           0.16   |            0.206  |          0.0344 |            0      |      0.02    |          2.93   |              7 |
| fixed       | n/4 |   6     |  1.44  |         0.0453   | 0.244 |        6.89 | 50, 60, 75, 100             |         180 |   6.6    | 0.12    | 0.00463  |   0.171  |           0.186  |            0.233  |          0.0658 |            0.0292 |      0.0222  |          3.32   |              8 |
| fixed       | n/4 |   7     |  1.62  |         0.0349   | 0.243 |        7.65 | 50, 60, 75                  |         150 |   7.53   | 0.156   | 0.00972  |   0.197  |           0.255  |            0.305  |          0.0986 |            0.0694 |      0.02    |          3.17   |              8 |
| fixed       | n/4 |   8     |  1.84  |         0.0702   | 0.244 |        8.51 | 50, 60, 75, 100             |         180 |   6.41   | 0.232   | 0.00549  |   0.282  |           0.301  |            0.351  |          0.139  |            0.116  |      0.0278  |          3.33   |              9 |
| fixed       | n/4 |   9     |  2.05  |         0.0803   | 0.244 |        9.38 | 50, 60, 75, 100             |         180 |   6.86   | 0.282   | 0.00577  |   0.334  |           0.352  |            0.404  |          0.18   |            0.162  |      0.0667  |          3.42   |             10 |
| fixed       | n/4 |  10     |  2.27  |         0.0954   | 0.244 |       10.3  | 50, 60, 75, 100             |         180 |   7.1    | 0.332   | 0.00597  |   0.398  |           0.406  |            0.457  |          0.223  |            0.209  |      0.0778  |          3.14   |              8 |
| fixed       | n/4 |  12     |  2.73  |         0.111    | 0.244 |       12.2  | 50, 60, 75, 100             |         180 |   8.72   | 0.405   | 0.00632  |   0.465  |           0.492  |            0.54   |          0.306  |            0.299  |      0.0944  |          2.69   |             11 |
| fixed       | n/2 |   2     |  0.864 |         0.0119   | 0.498 |        2.74 | 50, 60, 75                  |         150 |   4.72   | 0.00516 | 0.00586  |   0.0364 |           0.0677 |            0.0875 |          0      |            0      |      0.393   |          1.02   |              4 |
| fixed       | n/2 |   3     |  1.21  |         0.0082   | 0.498 |        3.44 | 50, 60, 75                  |         150 |   4.74   | 0.0483  | 0.00624  |   0.0966 |           0.112  |            0.158  |          0.0262 |            0      |      0.00667 |          2.8    |              7 |
| fixed       | n/2 |   4     |  1.63  |         0.0123   | 0.498 |        4.27 | 50, 60, 75, 100             |         180 |   4.19   | 0.151   | 0.00431  |   0.2    |           0.193  |            0.242  |          0.0932 |            0.0706 |      0.0222  |          3.14   |              8 |
| fixed       | n/2 |   5     |  2.06  |         0.0333   | 0.498 |        5.14 | 50, 60, 75, 100             |         180 |   5.3    | 0.232   | 0.00531  |   0.291  |           0.285  |            0.334  |          0.169  |            0.157  |      0.0389  |          3.16   |              8 |
| fixed       | n/2 |   6     |  2.53  |         0.0412   | 0.498 |        6.09 | 50, 60, 75, 100             |         180 |   5.48   | 0.323   | 0.00525  |   0.391  |           0.379  |            0.432  |          0.249  |            0.242  |      0.05    |          2.84   |              9 |
| fixed       | n/2 |   7     |  3.01  |         0.0451   | 0.498 |        7.05 | 50, 60, 75, 100             |         180 |   6.01   | 0.4     | 0.00509  |   0.452  |           0.459  |            0.501  |          0.327  |            0.323  |      0.0667  |          2.58   |              7 |
| fixed       | n/2 |   8     |  3.5   |         0.0497   | 0.498 |        8.03 | 50, 60, 75, 100             |         180 |   6.7    | 0.463   | 0.00586  |   0.524  |           0.532  |            0.581  |          0.398  |            0.396  |      0.0833  |          2.54   |              8 |
| fixed       | n/2 |   9     |  3.99  |         0.0514   | 0.498 |        9.02 | 50, 60, 75                  |         150 |   7.29   | 0.517   | 0.0108   |   0.56   |           0.613  |            0.647  |          0.463  |            0.462  |      0.147   |          1.85   |              5 |
| fixed       | n/2 |  10     |  4.48  |         0.0611   | 0.498 |       10    | 50, 60, 75                  |         150 |   6.55   | 0.585   | 0.00965  |   0.622  |           0.673  |            0.701  |          0.521  |            0.521  |      0.133   |          1.61   |              5 |
| fixed       | n   |   2     |  1.13  |         0.0131   | 1     |        2.13 | 30, 35, 40, 50, 60, 75, 100 |         625 |   3.11   | 0.0378  | 0.00141  |   0.0637 |           0.0692 |            0.0904 |          0.0134 |            0      |      0.362   |          0.885  |              4 |
| fixed       | n   |   3     |  2.04  |         0.009    | 1     |        3.04 | 30, 35, 40, 50, 60, 75      |         600 |   3.54   | 0.2     | 0.00267  |   0.245  |           0.245  |            0.284  |          0.147  |            0.14   |      0.203   |          1.43   |              6 |
| fixed       | n   |   4     |  3.02  |         0.00547  | 1     |        4.02 | 30, 35, 40, 50, 60, 75, 100 |         601 |   4.17   | 0.348   | 0.00288  |   0.399  |           0.38   |            0.45   |          0.288  |            0.286  |      0.253   |          1.37   |              9 |
| fixed       | n   |   5     |  4     |         0.00378  | 1     |        5    | 30, 35, 40, 50, 60, 75      |         600 |   4.11   | 0.479   | 0.00324  |   0.525  |           0.534  |            0.569  |          0.411  |            0.411  |      0.332   |          1.08   |              6 |
| fixed       | n   |   6     |  5     |         0.00183  | 1     |        6    | 30, 35, 40, 50, 60, 75      |         600 |   4.11   | 0.577   | 0.00299  |   0.615  |           0.632  |            0.658  |          0.513  |            0.513  |      0.437   |          0.857  |              5 |
| fixed       | n   |   7     |  6     |         0.00107  | 1     |        7    | 30, 35, 40, 50, 60, 75      |         600 |   4.12   | 0.651   | 0.00289  |   0.686  |           0.706  |            0.731  |          0.595  |            0.595  |      0.48    |          0.733  |              5 |
| fixed       | n   |   8     |  7     |         0.0004   | 1     |        8    | 30, 35, 40, 50, 60, 75      |         600 |   4.19   | 0.706   | 0.00246  |   0.737  |           0.762  |            0.783  |          0.661  |            0.661  |      0.638   |          0.487  |              4 |
| fixed       | n   |   9     |  8     |         0.0004   | 1     |        9    | 30, 35, 40, 50, 60, 75      |         600 |   4.12   | 0.752   | 0.00231  |   0.777  |           0.805  |            0.821  |          0.714  |            0.714  |      0.71    |          0.365  |              3 |
| fixed       | n   |  10     |  9     |         0        | 1     |       10    | 30, 35, 40, 50, 60, 75      |         600 |   3.71   | 0.795   | 0.00218  |   0.817  |           0.843  |            0.858  |          0.757  |            0.757  |      0.75    |          0.298  |              3 |
| fixed       | 2n  |   2     |  2.02  |         0.00473  | 2     |        2.01 | 30, 35, 40, 50, 60, 75      |         599 |   2.88   | 0.167   | 0.00231  |   0.2    |           0.204  |            0.236  |          0.123  |            0.121  |      0.282   |          1.12   |              5 |
| fixed       | 2n  |   3     |  4     |         0.00137  | 2     |        3    | 30, 35, 40, 50, 60, 75      |         600 |   3.35   | 0.409   | 0.00275  |   0.447  |           0.454  |            0.484  |          0.356  |            0.355  |      0.272   |          1.23   |              5 |
| fixed       | 2n  |   4     |  6     |         0.000333 | 2     |        4    | 30, 35, 40, 50, 60, 75      |         600 |   3.66   | 0.568   | 0.00274  |   0.601  |           0.617  |            0.643  |          0.525  |            0.525  |      0.4     |          0.88   |              5 |
| fixed       | 2n  |   5     |  8     |         0        | 2     |        5    | 30, 35, 40, 50, 60, 75      |         600 |   3.25   | 0.685   | 0.00243  |   0.712  |           0.728  |            0.75   |          0.642  |            0.642  |      0.485   |          0.667  |              3 |
| fixed       | 2n  |   6     | 10     |         0        | 2     |        6    | 30, 35, 40, 50, 60, 75      |         600 |   3.24   | 0.755   | 0.00219  |   0.776  |           0.799  |            0.814  |          0.724  |            0.724  |      0.635   |          0.433  |              3 |
| fixed       | 2n  |   7     | 12     |         0        | 2     |        7    | 30, 35, 40, 50, 60, 75      |         600 |   2.96   | 0.811   | 0.0019   |   0.832  |           0.851  |            0.864  |          0.782  |            0.782  |      0.712   |          0.318  |              3 |
| fixed       | 2n  |   8     | 14     |         0        | 2     |        8    | 30, 35, 40, 50, 60, 75      |         600 |   2.92   | 0.847   | 0.00179  |   0.861  |           0.885  |            0.894  |          0.825  |            0.825  |      0.818   |          0.19   |              2 |
| fixed       | 2n  |   9     | 16     |         0        | 2     |        9    | 30, 35, 40, 50, 60, 75      |         600 |   2.82   | 0.873   | 0.00153  |   0.886  |           0.91   |            0.919  |          0.856  |            0.856  |      0.867   |          0.143  |              2 |
| fixed       | 2n  |  10     | 18     |         0        | 2     |       10    | 30, 35, 40, 50, 60, 75      |         600 |   2.72   | 0.894   | 0.00159  |   0.905  |           0.93   |            0.937  |          0.88   |            0.88   |      0.92    |          0.085  |              2 |
| bernoulli   | n/4 |   0.05  |  0.976 |         0.165    | 0.243 |        5.06 | 50, 60, 75                  |         150 |   3.97   | 0.0848  | 0.01     |   0.18   |           0.138  |            0.177  |          0      |          nan      |      0.32    |          1.61   |              7 |
| bernoulli   | n/4 |   0.075 |  1.21  |         0.306    | 0.243 |        6.06 | 50, 60, 75                  |         150 |  -2.21   | 0.234   | 0.0128   |   0.376  |           0.206  |            0.274  |          0.0306 |          nan      |      0.0733  |          3.33   |              9 |
| bernoulli   | n/4 |   0.1   |  1.6   |         1.08     | 0.244 |        7.91 | 50, 60, 75, 100             |         180 | -19.4    | 0.584   | 0.0122   |   0.668  |           0.411  |            0.477  |          0.112  |          nan      |      0.0333  |          4.29   |             12 |
| bernoulli   | n/4 |   0.125 |  1.77  |         0.686    | 0.243 |        8.45 | 50, 60, 75                  |         150 | -18      | 0.636   | 0.0191   |   0.743  |           0.397  |            0.463  |          0.135  |          nan      |      0.06    |          3.72   |              9 |
| bernoulli   | n/4 |   0.15  |  2.11  |         0.823    | 0.243 |        9.89 | 50, 60, 75                  |         150 | -21.1    | 0.77    | 0.0192   |   0.829  |           0.491  |            0.548  |          0.202  |          nan      |      0.0467  |          3.66   |              8 |
| bernoulli   | n/4 |   0.2   |  2.78  |         1.15     | 0.243 |       12.7  | 50, 60, 75                  |         150 | -23.9    | 0.962   | 0.021    |   0.974  |           0.641  |            0.679  |          0.329  |          nan      |      0.0867  |          2.75   |              7 |
| bernoulli   | n/2 |   0.025 |  0.765 |         0.164    | 0.498 |        2.56 | 50, 60, 75                  |         150 |   3.63   | 0.0414  | 0.00803  |   0.11   |           0.0896 |            0.116  |          0      |          nan      |      0.487   |          0.967  |              7 |
| bernoulli   | n/2 |   0.05  |  1.41  |         1.03     | 0.498 |        4.01 | 50, 60, 75, 100             |         180 | -17      | 0.462   | 0.0114   |   0.552  |           0.31   |            0.377  |          0.0728 |          nan      |      0.0333  |          3.93   |             11 |
| bernoulli   | n/2 |   0.075 |  1.9   |         0.801    | 0.498 |        4.94 | 50, 60, 75                  |         150 | -20.3    | 0.644   | 0.0186   |   0.69   |           0.378  |            0.433  |          0.153  |          nan      |      0       |          3.46   |              9 |
| bernoulli   | n/2 |   0.1   |  2.61  |         1.14     | 0.498 |        6.41 | 50, 60, 75                  |         150 | -25.7    | 0.87    | 0.0217   |   0.887  |           0.532  |            0.575  |          0.277  |          nan      |      0.0467  |          3.11   |              7 |
| bernoulli   | n/2 |   0.15  |  4.11  |         1.71     | 0.498 |        9.49 | 50, 60, 75                  |         150 | -23.4    | 1.04    | 0.0166   |   1.05   |           0.73   |            0.758  |          0.494  |          nan      |      0.113   |          1.97   |              5 |
| bernoulli   | n/2 |   0.2   |  5.66  |         2.34     | 0.498 |       12.7  | 50, 60, 75                  |         150 | -19.2    | 1.11    | 0.0136   |   1.09   |           0.849  |            0.86   |          0.65   |          nan      |      0.307   |          1.07   |              3 |
| bernoulli   | n   |   0.025 |  0.651 |         0.649    | 1     |        1.71 | 30, 35, 40, 50, 60, 75      |         600 |   0.506  | 0.101   | 0.00331  |   0.178  |           0.121  |            0.169  |          0      |          nan      |      0.685   |          0.667  |              7 |
| bernoulli   | n   |   0.05  |  1.36  |         1.91     | 1     |        2.53 | 30, 35, 40, 50, 60, 75      |         600 | -12.7    | 0.539   | 0.00658  |   0.604  |           0.402  |            0.446  |          0.074  |          nan      |      0.238   |          1.57   |              7 |
| bernoulli   | n   |   0.075 |  2.23  |         3.09     | 1     |        3.52 | 30, 35, 40, 50, 60, 75      |         600 | -18.7    | 0.835   | 0.00692  |   0.867  |           0.611  |            0.646  |          0.23   |          nan      |      0.16    |          1.61   |              7 |
| bernoulli   | n   |   0.1   |  3.2   |         4.48     | 1     |        4.61 | 30, 35, 40, 50, 60, 75      |         600 | -19.7    | 0.998   | 0.00602  |   1.01   |           0.752  |            0.775  |          0.38   |          nan      |      0.223   |          1.35   |              6 |
| bernoulli   | n   |   0.15  |  5.26  |         6.69     | 1     |        6.88 | 30, 35, 40, 50, 60, 75      |         600 | -15.1    | 1.08    | 0.00485  |   1.08   |           0.886  |            0.895  |          0.6    |          nan      |      0.397   |          0.812  |              4 |
| bernoulli   | n   |   0.2   |  7.36  |         9.12     | 1     |        9.19 | 30, 35, 40, 50, 60, 75      |         600 | -10.4    | 1.08    | 0.00362  |   1.08   |           0.944  |            0.947  |          0.734  |          nan      |      0.675   |          0.362  |              2 |
| bernoulli   | n   |   0.3   |  9.48  |         2.96     | 1     |       10.6  | 30, 35, 40                  |         450 |  -5.41   | 1.08    | 0.00843  |   1.07   |           0.941  |            0.942  |          0.783  |          nan      |      0.924   |          0.0778 |              2 |
| bernoulli   | n   |   0.4   | 13     |         3.97     | 1     |       14.2  | 30, 35, 40                  |         450 |  -2.49   | 1.05    | 0.00664  |   1.05   |           0.989  |            0.989  |          0.867  |          nan      |      1       |          0      |              0 |
| bernoulli   | n   |   0.5   | 16.5   |         4.94     | 1     |       17.8  | 30, 35, 40                  |         450 |  -0.18   | 1       | 0.00226  |   1      |           1      |            1      |          0.911  |          nan      |      1       |          0      |              0 |
| bernoulli   | 2n  |   0.025 |  0.899 |         1.55     | 2     |        1.52 | 30, 35, 40, 50, 60, 75      |         598 |  -7.71   | 0.334   | 0.00575  |   0.412  |           0.267  |            0.314  |          0.003  |          nan      |      0.503   |          0.962  |              8 |
| bernoulli   | 2n  |   0.05  |  2.57  |         4.07     | 2     |        2.47 | 30, 35, 40, 50, 60, 75      |         650 | -20.1    | 0.86    | 0.00598  |   0.892  |           0.621  |            0.651  |          0.27   |          nan      |      0.2     |          1.51   |              6 |
| bernoulli   | 2n  |   0.075 |  4.34  |         6.53     | 2     |        3.47 | 30, 35, 40, 50, 60, 75      |         600 | -19      | 1.04    | 0.00536  |   1.05   |           0.791  |            0.812  |          0.478  |          nan      |      0.26    |          1.16   |              4 |
| bernoulli   | 2n  |   0.1   |  6.38  |         8.91     | 2     |        4.6  | 30, 35, 40, 50, 60, 75      |         600 | -15      | 1.08    | 0.00432  |   1.08   |           0.877  |            0.887  |          0.629  |          nan      |      0.425   |          0.752  |              4 |
| bernoulli   | 2n  |   0.15  | 10.5   |        13.6      | 2     |        6.87 | 30, 35, 40, 50, 60, 75      |         600 |  -8.97   | 1.08    | 0.00289  |   1.07   |           0.954  |            0.957  |          0.793  |          nan      |      0.692   |          0.332  |              2 |
| bernoulli   | 2n  |   0.2   | 14.7   |        17.9      | 2     |        9.15 | 30, 35, 40, 50, 60, 75      |         600 |  -4.96   | 1.05    | 0.00204  |   1.05   |           0.982  |            0.982  |          0.871  |          nan      |      0.873   |          0.127  |              1 |
| bernoulli   | 2n  |   0.3   | 19     |         6.08     | 2     |       10.7  | 30, 35, 40                  |         450 |  -2.1    | 1.04    | 0.00623  |   1.04   |           0.991  |            0.991  |          0.896  |          nan      |      1       |          0      |              0 |
| bernoulli   | 2n  |   0.4   | 26.1   |         7.93     | 2     |       14.2  | 30, 35, 40                  |         450 |  -0.0767 | 1       | 0.000937 |   1      |           1      |            1      |          0.937  |          nan      |      1       |          0      |              0 |
| bernoulli   | 2n  |   0.5   | 33     |         9.94     | 2     |       17.7  | 30, 35, 40                  |         450 |   0      | 1       | 0        |   1      |           1      |            1      |          0.958  |          nan      |      1       |          0      |              0 |
| bernoulli   | 4n  |   0.04  |  4.53  |         2.61     | 4     |        2.17 | 40, 50, 60                  |         150 | -22.2    | 0.972   | 0.0168   |   1      |           0.603  |            0.635  |          0.419  |          nan      |      0.167   |          1.55   |              5 |
| chu_stuckey | n   |   2     |  1.77  |         0.131    | 1     |        2.76 | 30, 40, 50, 75, 100, 125    |          30 |   5.04   | 0.146   | 0.0117   |   0.206  |           0.182  |            0.237  |          0.105  |            0      |      0.1     |          3.57   |             10 |
| chu_stuckey | n   |   4     |  3.26  |         0.167    | 1     |        4.25 | 30, 40, 50, 75, 100, 125    |          30 |   4.3    | 0.396   | 0.0142   |   0.453  |           0.424  |            0.478  |          0.327  |            0.286  |      0.0667  |          3.17   |             10 |
| chu_stuckey | n   |   6     |  5.09  |         0.38     | 1     |        6.11 | 30, 40, 50, 75, 100, 125    |          30 |   4.35   | 0.599   | 0.0112   |   0.626  |           0.627  |            0.653  |          0.532  |            0.513  |      0.2     |          1.57   |              7 |
| chu_stuckey | n   |   8     |  7.07  |         0.449    | 1     |        8.09 | 30, 40, 50, 75, 100, 125    |          30 |   4.06   | 0.722   | 0.00785  |   0.76   |           0.749  |            0.778  |          0.673  |            0.661  |      0.367   |          1.43   |              5 |
| chu_stuckey | n   |  10     |  9.01  |         0.412    | 1     |       10    | 30, 40, 50, 75, 100, 125    |          30 |   3.61   | 0.804   | 0.00818  |   0.824  |           0.826  |            0.843  |          0.763  |            0.757  |      0.567   |          0.7    |              4 |

#### The e-matched groups named by the item (fixed generator)

| group   |   d |    mu |    e | within tolerance   |      b |    se b |   beta* |   b - beta* |   rule/n at max n |   rule/n - b |
|:--------|----:|------:|-----:|:-------------------|-------:|--------:|--------:|------------:|------------------:|-------------:|
| e = 1   |   2 | 1     | 1.13 | True               | 0.0378 | 0.00141 |  0.0134 |      0.0244 |            0.0904 |       0.0526 |
| e = 1   |   3 | 0.498 | 1.21 | False              | 0.0483 | 0.00624 |  0.0262 |      0.0221 |            0.158  |       0.11   |
| e = 1   |   4 | 0.243 | 1.09 | True               | 0.0282 | 0.00634 |  0.0106 |      0.0176 |            0.164  |       0.136  |
| e = 2   |   3 | 1     | 2.04 | True               | 0.2    | 0.00267 |  0.147  |      0.0532 |            0.284  |       0.0842 |
| e = 2   |   5 | 0.498 | 2.06 | True               | 0.232  | 0.00531 |  0.169  |      0.0629 |            0.334  |       0.102  |
| e = 2   |   2 | 2     | 2.02 | True               | 0.167  | 0.00231 |  0.123  |      0.0442 |            0.236  |       0.0692 |
| e = 2   |   9 | 0.244 | 2.05 | True               | 0.282  | 0.00577 |  0.18   |      0.101  |            0.404  |       0.122  |
| e = 3   |   4 | 1     | 3.02 | True               | 0.348  | 0.00288 |  0.288  |      0.0604 |            0.45   |       0.102  |
| e = 3   |   7 | 0.498 | 3.01 | True               | 0.4    | 0.00509 |  0.327  |      0.0733 |            0.501  |       0.101  |
| e = 3   |  12 | 0.244 | 2.73 | False              | 0.405  | 0.00632 |  0.306  |      0.0991 |            0.54   |       0.134  |
| e = 4   |   5 | 1     | 4    | True               | 0.479  | 0.00324 |  0.411  |      0.0678 |            0.569  |       0.0899 |
| e = 4   |   9 | 0.498 | 3.99 | True               | 0.517  | 0.0108  |  0.463  |      0.0546 |            0.647  |       0.129  |
| e = 4   |   3 | 2     | 4    | True               | 0.409  | 0.00275 |  0.356  |      0.0533 |            0.484  |       0.0754 |
| e = 6   |   7 | 1     | 6    | True               | 0.651  | 0.00289 |  0.595  |      0.0555 |            0.731  |       0.08   |
| e = 6   |   4 | 2     | 6    | True               | 0.568  | 0.00274 |  0.525  |      0.0433 |            0.643  |       0.0749 |
| e = 8   |   9 | 1     | 8    | True               | 0.752  | 0.00231 |  0.714  |      0.0378 |            0.821  |       0.0685 |
| e = 8   |   5 | 2     | 8    | True               | 0.685  | 0.00243 |  0.642  |      0.0424 |            0.75   |       0.0654 |

#### The e-matched pairs

| series 1              | series 2              |   e 1 |   e 2 |     b 1 |    b 2 |     diff |   2 max se |   |diff| / 2 max se | differ   | both constant e   |   beta* 1 |   beta* 2 |   rule/n 1 |   rule/n 2 |
|:----------------------|:----------------------|------:|------:|--------:|-------:|---------:|-----------:|--------------------:|:---------|:------------------|----------:|----------:|-----------:|-----------:|
| fixed r=n/2 2         | bernoulli r=2n 0.025  | 0.864 | 0.899 | 0.00516 | 0.334  | -0.328   |    0.0117  |              28     | True     | False             |    0      |    0.003  |     0.0875 |     0.314  |
| fixed r=n/4 3         | bernoulli r=n/4 0.05  | 0.96  | 0.976 | 0.0166  | 0.0848 | -0.0682  |    0.0201  |               3.39  | True     | False             |    0      |    0      |     0.128  |     0.177  |
| fixed r=n/4 4         | fixed r=n 2           | 1.09  | 1.13  | 0.0282  | 0.0378 | -0.00955 |    0.0127  |               0.753 | False    | True              |    0.0106 |    0.0134 |     0.164  |     0.0904 |
| fixed r=n/2 3         | bernoulli r=n/4 0.075 | 1.21  | 1.21  | 0.0483  | 0.234  | -0.186   |    0.0256  |               7.25  | True     | False             |    0.0262 |    0.0306 |     0.158  |     0.274  |
| fixed r=n/4 5         | fixed r=n/2 3         | 1.25  | 1.21  | 0.0787  | 0.0483 |  0.0304  |    0.0155  |               1.96  | True     | True              |    0.0344 |    0.0262 |     0.206  |     0.158  |
| fixed r=n/4 5         | bernoulli r=n/4 0.075 | 1.25  | 1.21  | 0.0787  | 0.234  | -0.155   |    0.0256  |               6.06  | True     | False             |    0.0344 |    0.0306 |     0.206  |     0.274  |
| fixed r=n/4 6         | bernoulli r=n/2 0.05  | 1.44  | 1.41  | 0.12    | 0.462  | -0.342   |    0.0229  |              14.9   | True     | False             |    0.0658 |    0.0728 |     0.233  |     0.377  |
| fixed r=n/4 7         | fixed r=n/2 4         | 1.62  | 1.63  | 0.156   | 0.151  |  0.00457 |    0.0194  |               0.235 | False    | True              |    0.0986 |    0.0932 |     0.305  |     0.242  |
| fixed r=n/4 7         | bernoulli r=n/4 0.1   | 1.62  | 1.6   | 0.156   | 0.584  | -0.429   |    0.0243  |              17.6   | True     | False             |    0.0986 |    0.112  |     0.305  |     0.477  |
| fixed r=n/2 4         | bernoulli r=n/4 0.1   | 1.63  | 1.6   | 0.151   | 0.584  | -0.433   |    0.0243  |              17.8   | True     | False             |    0.0932 |    0.112  |     0.242  |     0.477  |
| bernoulli r=n/4 0.125 | chu_stuckey r=n 2     | 1.77  | 1.77  | 0.636   | 0.146  |  0.49    |    0.0383  |              12.8   | True     | False             |    0.135  |    0.105  |     0.463  |     0.237  |
| fixed r=n 3           | fixed r=2n 2          | 2.04  | 2.02  | 0.2     | 0.167  |  0.0329  |    0.00533 |               6.16  | True     | True              |    0.147  |    0.123  |     0.284  |     0.236  |
| fixed r=n/4 9         | fixed r=n/2 5         | 2.05  | 2.06  | 0.282   | 0.232  |  0.05    |    0.0115  |               4.33  | True     | True              |    0.18   |    0.169  |     0.404  |     0.334  |
| fixed r=n/4 9         | fixed r=n 3           | 2.05  | 2.04  | 0.282   | 0.2    |  0.0818  |    0.0115  |               7.09  | True     | True              |    0.18   |    0.147  |     0.404  |     0.284  |
| fixed r=n/4 9         | fixed r=2n 2          | 2.05  | 2.02  | 0.282   | 0.167  |  0.115   |    0.0115  |               9.94  | True     | True              |    0.18   |    0.123  |     0.404  |     0.236  |
| fixed r=n/2 5         | fixed r=n 3           | 2.06  | 2.04  | 0.232   | 0.2    |  0.0318  |    0.0106  |               3     | True     | True              |    0.169  |    0.147  |     0.334  |     0.284  |
| fixed r=n/2 5         | fixed r=2n 2          | 2.06  | 2.02  | 0.232   | 0.167  |  0.0647  |    0.0106  |               6.09  | True     | True              |    0.169  |    0.123  |     0.334  |     0.236  |
| fixed r=n/2 5         | bernoulli r=n/4 0.15  | 2.06  | 2.11  | 0.232   | 0.77   | -0.539   |    0.0385  |              14     | True     | False             |    0.169  |    0.202  |     0.334  |     0.548  |
| fixed r=n/4 10        | bernoulli r=n 0.075   | 2.27  | 2.23  | 0.332   | 0.835  | -0.504   |    0.0138  |              36.4   | True     | False             |    0.223  |    0.23   |     0.457  |     0.646  |
| fixed r=n/2 6         | bernoulli r=2n 0.05   | 2.53  | 2.57  | 0.323   | 0.86   | -0.538   |    0.012   |              45     | True     | False             |    0.249  |    0.27   |     0.432  |     0.651  |
| bernoulli r=n/2 0.1   | bernoulli r=2n 0.05   | 2.61  | 2.57  | 0.87    | 0.86   |  0.00996 |    0.0434  |               0.23  | False    | False             |    0.277  |    0.27   |     0.575  |     0.651  |
| fixed r=n/4 12        | bernoulli r=n/4 0.2   | 2.73  | 2.78  | 0.405   | 0.962  | -0.557   |    0.042   |              13.2   | True     | False             |    0.306  |    0.329  |     0.54   |     0.679  |
| fixed r=n/2 7         | fixed r=n 4           | 3.01  | 3.02  | 0.4     | 0.348  |  0.0515  |    0.0102  |               5.07  | True     | True              |    0.327  |    0.288  |     0.501  |     0.45   |
| fixed r=n/2 9         | fixed r=n 5           | 3.99  | 4     | 0.517   | 0.479  |  0.0382  |    0.0217  |               1.76  | True     | True              |    0.463  |    0.411  |     0.647  |     0.569  |
| fixed r=n/2 9         | fixed r=2n 3          | 3.99  | 4     | 0.517   | 0.409  |  0.109   |    0.0217  |               5.01  | True     | True              |    0.463  |    0.356  |     0.647  |     0.484  |
| fixed r=n 5           | fixed r=2n 3          | 4     | 4     | 0.479   | 0.409  |  0.0703  |    0.00647 |              10.9   | True     | True              |    0.411  |    0.356  |     0.569  |     0.484  |
| fixed r=n/2 10        | bernoulli r=4n 0.04   | 4.48  | 4.53  | 0.585   | 0.972  | -0.387   |    0.0336  |              11.5   | True     | False             |    0.521  |    0.419  |     0.701  |     0.635  |
| fixed r=n 7           | fixed r=2n 4          | 6     | 6     | 0.651   | 0.568  |  0.0825  |    0.00577 |              14.3   | True     | True              |    0.595  |    0.525  |     0.731  |     0.643  |
| fixed r=n 9           | fixed r=2n 5          | 8     | 8     | 0.752   | 0.685  |  0.0673  |    0.00485 |              13.9   | True     | True              |    0.714  |    0.642  |     0.821  |     0.75   |
| fixed r=n 10          | chu_stuckey r=n 10    | 9     | 9.01  | 0.795   | 0.804  | -0.00946 |    0.0164  |               0.578 | False    | True              |    0.757  |    0.763  |     0.858  |     0.843  |

#### Is b a function of beta* alone? Residuals of b about beta* on the constant-e series

| series 1       | series 2           |   beta* 1 |   beta* 2 |    e 1 |    e 2 |     b 1 |     b 2 |     diff |   2 max se | differ   |
|:---------------|:-------------------|----------:|----------:|-------:|-------:|--------:|--------:|---------:|-----------:|:---------|
| fixed r=n/4 3  | fixed r=n/4 4      |    0      |    0.0106 |  0.96  |  1.09  | 0.0166  | 0.0282  | -0.0116  |    0.0137  | False    |
| fixed r=n/4 3  | fixed r=n/2 2      |    0      |    0      |  0.96  |  0.864 | 0.0166  | 0.00516 |  0.0115  |    0.0137  | False    |
| fixed r=n/4 3  | fixed r=n 2        |    0      |    0.0134 |  0.96  |  1.13  | 0.0166  | 0.0378  | -0.0211  |    0.0137  | True     |
| fixed r=n/2 2  | fixed r=n 2        |    0      |    0.0134 |  0.864 |  1.13  | 0.00516 | 0.0378  | -0.0326  |    0.0117  | True     |
| fixed r=n/4 4  | fixed r=n/2 3      |    0.0106 |    0.0262 |  1.09  |  1.21  | 0.0282  | 0.0483  | -0.0201  |    0.0127  | True     |
| fixed r=n/4 4  | fixed r=n 2        |    0.0106 |    0.0134 |  1.09  |  1.13  | 0.0282  | 0.0378  | -0.00955 |    0.0127  | False    |
| fixed r=n/4 4  | fixed r=n/2 2      |    0.0106 |    0      |  1.09  |  0.864 | 0.0282  | 0.00516 |  0.0231  |    0.0127  | True     |
| fixed r=n/2 3  | fixed r=n 2        |    0.0262 |    0.0134 |  1.21  |  1.13  | 0.0483  | 0.0378  |  0.0106  |    0.0125  | False    |
| fixed r=n/4 5  | fixed r=n/2 3      |    0.0344 |    0.0262 |  1.25  |  1.21  | 0.0787  | 0.0483  |  0.0304  |    0.0155  | True     |
| fixed r=n/2 4  | chu_stuckey r=n 2  |    0.0932 |    0.105  |  1.63  |  1.77  | 0.151   | 0.146   |  0.00488 |    0.0233  | False    |
| fixed r=n/4 7  | fixed r=n/2 4      |    0.0986 |    0.0932 |  1.62  |  1.63  | 0.156   | 0.151   |  0.00457 |    0.0194  | False    |
| fixed r=n/4 7  | chu_stuckey r=n 2  |    0.0986 |    0.105  |  1.62  |  1.77  | 0.156   | 0.146   |  0.00945 |    0.0233  | False    |
| fixed r=2n 2   | chu_stuckey r=n 2  |    0.123  |    0.105  |  2.02  |  1.77  | 0.167   | 0.146   |  0.0209  |    0.0233  | False    |
| fixed r=n/4 8  | fixed r=n 3        |    0.139  |    0.147  |  1.84  |  2.04  | 0.232   | 0.2     |  0.0325  |    0.011   | True     |
| fixed r=n/4 8  | fixed r=2n 2       |    0.139  |    0.123  |  1.84  |  2.02  | 0.232   | 0.167   |  0.0654  |    0.011   | True     |
| fixed r=n/4 9  | fixed r=n/2 5      |    0.18   |    0.169  |  2.05  |  2.06  | 0.282   | 0.232   |  0.05    |    0.0115  | True     |
| fixed r=n/4 12 | fixed r=n 4        |    0.306  |    0.288  |  2.73  |  3.02  | 0.405   | 0.348   |  0.0569  |    0.0126  | True     |
| fixed r=n/2 7  | chu_stuckey r=n 4  |    0.327  |    0.327  |  3.01  |  3.26  | 0.4     | 0.396   |  0.0037  |    0.0283  | False    |
| fixed r=n/2 8  | fixed r=n 5        |    0.398  |    0.411  |  3.5   |  4     | 0.463   | 0.479   | -0.0164  |    0.0117  | True     |
| fixed r=n 6    | chu_stuckey r=n 6  |    0.513  |    0.532  |  5     |  5.09  | 0.577   | 0.599   | -0.0216  |    0.0224  | False    |
| fixed r=n 6    | fixed r=2n 4       |    0.513  |    0.525  |  5     |  6     | 0.577   | 0.568   |  0.00894 |    0.00598 | True     |
| fixed r=n/2 10 | fixed r=2n 4       |    0.521  |    0.525  |  4.48  |  6     | 0.585   | 0.568   |  0.0164  |    0.0193  | False    |
| fixed r=n/2 10 | chu_stuckey r=n 6  |    0.521  |    0.532  |  4.48  |  5.09  | 0.585   | 0.599   | -0.0141  |    0.0224  | False    |
| fixed r=n/2 10 | fixed r=n 6        |    0.521  |    0.513  |  4.48  |  5     | 0.585   | 0.577   |  0.00746 |    0.0193  | False    |
| fixed r=2n 4   | chu_stuckey r=n 6  |    0.525  |    0.532  |  6     |  5.09  | 0.568   | 0.599   | -0.0305  |    0.0224  | True     |
| fixed r=n 8    | fixed r=2n 5       |    0.661  |    0.642  |  7     |  8     | 0.706   | 0.685   |  0.0215  |    0.00493 | True     |
| fixed r=n 8    | chu_stuckey r=n 8  |    0.661  |    0.673  |  7     |  7.07  | 0.706   | 0.722   | -0.0162  |    0.0157  | True     |
| fixed r=n 9    | fixed r=2n 6       |    0.714  |    0.724  |  8     | 10     | 0.752   | 0.755   | -0.00342 |    0.00462 | False    |
| fixed r=n 10   | chu_stuckey r=n 10 |    0.757  |    0.763  |  9     |  9.01  | 0.795   | 0.804   | -0.00946 |    0.0164  | False    |
| fixed r=2n 7   | chu_stuckey r=n 10 |    0.782  |    0.763  | 12     |  9.01  | 0.811   | 0.804   |  0.00725 |    0.0164  | False    |

#### The rule against the optimum, per excess bin

| source   | e bin     |   count | n range   |   exact |   gap mean |   gap q90 |   gap max |   gap/n mean |   opt/n mean |   rule/n mean |
|:---------|:----------|--------:|:----------|--------:|-----------:|----------:|----------:|-------------:|-------------:|--------------:|
| corpus   | [0.62, 1) |      12 | 10-50     |   0.667 |     0.333  |       1   |         1 |     0.00769  |        0.195 |         0.203 |
| corpus   | [1, 1.5)  |     273 | 10-134    |   0.568 |     0.857  |       2.8 |         8 |     0.0219   |        0.238 |         0.26  |
| corpus   | [1.5, 2)  |     326 | 10-125    |   0.414 |     1.21   |       3   |        10 |     0.0341   |        0.396 |         0.43  |
| corpus   | [2, 2.4)  |     458 | 9-50      |   0.624 |     0.546  |       2   |         4 |     0.0224   |        0.501 |         0.523 |
| corpus   | [2.4, 3)  |     434 | 9-125     |   0.682 |     0.502  |       2   |         7 |     0.0173   |        0.622 |         0.64  |
| corpus   | [3, 4)    |     877 | 10-125    |   0.774 |     0.392  |       1   |        10 |     0.011    |        0.719 |         0.73  |
| corpus   | [4, 6)    |    1627 | 10-125    |   0.897 |     0.136  |       1   |         7 |     0.00455  |        0.86  |         0.864 |
| corpus   | [6, 10)   |    1602 | 10-125    |   0.958 |     0.0655 |       0   |         5 |     0.00132  |        0.948 |         0.95  |
| corpus   | >= 10     |     767 | 10-100    |   0.993 |     0.0117 |       0   |         3 |     0.000209 |        0.989 |         0.989 |
| ensemble | [0, 0.62) |    2899 | 10-60     |   0.982 |     0.0183 |       0   |         2 |     0.000578 |        0.199 |         0.199 |
| ensemble | [0.62, 1) |    2323 | 10-75     |   0.663 |     0.483  |       2   |         7 |     0.0116   |        0.181 |         0.193 |
| ensemble | [1, 1.5)  |    4258 | 10-100    |   0.369 |     1.38   |       4   |         9 |     0.0295   |        0.212 |         0.241 |
| ensemble | [1.5, 2)  |    2621 | 10-100    |   0.225 |     2.22   |       5   |        12 |     0.0407   |        0.313 |         0.354 |
| ensemble | [2, 2.4)  |    4525 | 10-100    |   0.352 |     1.51   |       4   |        12 |     0.0317   |        0.355 |         0.386 |
| ensemble | [2.4, 3)  |    2181 | 10-100    |   0.267 |     1.93   |       4   |        14 |     0.0346   |        0.465 |         0.499 |
| ensemble | [3, 4)    |    3738 | 10-100    |   0.403 |     1.21   |       3   |        10 |     0.0256   |        0.55  |         0.576 |
| ensemble | [4, 6)    |    6854 | 10-75     |   0.53  |     0.767  |       2   |         6 |     0.0178   |        0.668 |         0.686 |
| ensemble | [6, 10)   |   10602 | 10-75     |   0.747 |     0.344  |       1   |         5 |     0.00783  |        0.847 |         0.855 |
| ensemble | >= 10     |   10700 | 10-75     |   0.913 |     0.0982 |       0   |         3 |     0.00202  |        0.955 |         0.957 |

#### The rule's worst cases

| source   | instance_name             |   n |   m |    e |   optimum |   rule |   rule_gap |
|:---------|:--------------------------|----:|----:|-----:|----------:|-------:|-----------:|
| ensemble | ens_b_n100_m50_p0.06_i018 | 100 |  50 | 2.48 |        37 |     51 |         14 |
| ensemble | ens_b_n100_m25_p0.07_i022 | 100 |  25 | 1.71 |        25 |     37 |         12 |
| ensemble | ens_b_n100_m25_p0.08_i004 | 100 |  25 | 1.92 |        32 |     44 |         12 |
| ensemble | ens_b_n100_m25_p0.1_i019  | 100 |  25 | 2.37 |        43 |     55 |         12 |
| ensemble | ens_b_n100_m50_p0.04_i011 | 100 |  50 | 1.56 |        18 |     30 |         12 |
| ensemble | ens_f_n100_m25_d12_i005   | 100 |  25 | 2.79 |        49 |     60 |         11 |
| ensemble | ens_b_n100_m25_p0.09_i012 | 100 |  25 | 2.2  |        37 |     48 |         11 |
| ensemble | ens_b_n100_m25_p0.09_i010 | 100 |  25 | 2.04 |        35 |     46 |         11 |
| ensemble | ens_b_n100_m25_p0.1_i006  | 100 |  25 | 2.43 |        42 |     53 |         11 |
| ensemble | ens_b_n100_m25_p0.12_i008 | 100 |  25 | 2.64 |        46 |     57 |         11 |

