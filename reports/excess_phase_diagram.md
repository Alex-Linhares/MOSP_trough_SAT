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

