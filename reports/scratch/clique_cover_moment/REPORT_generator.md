# The Chu & Stuckey generator, the first-moment bound under it, and the threshold against the ridge

*2026-10-31, agent report. Everything here lives in `reports/scratch/clique_cover_moment/`; nothing
outside it was touched, nothing committed. All runs under `nice -n 19`, at most 8 processes.*

Scripts: `stats_cs.py` (the 200 files), `gen_candidates.py` + `fit_generators.py` + `fit_variants.py`
+ `diag_hist.py` (Q1), `bound_lib.py` + `mc_empty_pairs.py` + `floor_violation.py` (Q2),
`q3_thresholds.py` (Q3). Logs beside each. Extracted paper texts in `lit/`.

## 0. Orientation and a correction to the README

The files are `m n` then an `m × n` matrix, **rows = patterns, columns = pieces = customers**
(Frinhani's `Dataset_Description`; the repository's solver reads them that way, and the certified
optima agree with Frinhani's S1 table, e.g. Random-100-50-2 mean 11.6). `Random-n1-n2-d`: n1 =
customers, n2 = products (Chu & Stuckey list "number of customers, number of products"; the
file for `Random-100-50` has 50 rows of 100 columns).

**The README's "every customer has at least two patterns" is the wrong way round.** Over the 200
files the *pattern* (row) minimum is 2 in every class and the *customer* (column) minimum is 1 in
most classes (5 of 5 files at every d = 2 class, 4–5 of 5 at d = 4, 1–5 at d = 6; none at d ≥ 8 for
the square classes). So: every pattern has at least two customers; customers with a single pattern
are common (17–23 % of customers at d = 2, 48 % in Random-100-50-2).

## 1. What the generator is

### 1.1 What the papers say

Chu & Stuckey (2009), §4.2, p. 253 of LNCS 5732 (`lit/chu_stuckey_2009.txt` lines 534–549), verbatim:

> First we specify the number of customers, number of products and the average number of
> customers per product. We then calculate a density that will achieve the specified average
> number of customers per product. The customer vs product table is then randomly generated
> using the calculated density to determine when to put 1's and 0's. As a post condition, we
> throw away any instance where the customer graph can be decomposed into separate components.

Chu's PhD thesis (2011), §6.4.2, pp. 151–152, repeats this word for word. Neither mentions a
minimum pattern size or any repair of empty customers. Frinhani et al. (2018)'s dataset
description only says "sets of five instances with 2, 4, 6, 8 and 10 pieces per pattern were
created by a pseudorandom instance generator" and that no instance is a complete graph, tree or
1-tree. No held paper gives the code.

### 1.2 The joint statistics (`stats_cs.log`)

Per class, all five files pooled (n customers, m patterns, nominal d; "binom var" is the
Bernoulli(d/n) prediction d(1 − d/n) for a pattern and (md/n)(1 − d/n) for a customer):

| class (n, m, d) | ones (d·m) | pattern size min / mean / var / max | binom var | patterns per customer min / mean / var / max | binom var | files with a 1-pattern customer |
|---|---|---|---|---|---|---|
| (30,30,2) | 81.4 (60) | 2 / 2.71 / 1.02 / 6 | 1.87 | 1 / 2.71 / 2.08 / 8 | 1.87 | 5 |
| (30,30,4) | 127.6 (120) | 2 / 4.25 / 2.98 / 10 | 3.47 | 1 / 4.25 / 3.99 / 10 | 3.47 | 5 |
| (30,30,6) | 176.4 (180) | 2 / 5.88 / 4.84 / 14 | 4.80 | 1 / 5.88 / 5.64 / 12 | 4.80 | 5 |
| (30,30,8) | 234.8 (240) | 3 / 7.83 / 5.01 / 15 | 5.87 | 1 / 7.83 / 6.69 / 14 | 5.87 | 2 |
| (30,30,10) | 295.6 (300) | 5 / 9.85 / 5.37 / 17 | 6.67 | 2 / 9.85 / 7.95 / 17 | 6.67 | 0 |
| (50,100,2) | 259.6 (200) | 2 / 2.60 / 1.02 / 8 | 1.92 | 1 / 5.19 / 4.35 / 10 | 3.84 | 5 |
| (100,50,2) | 174.4 (100) | 2 / 3.49 / 2.25 / 10 | 1.96 | 1 / 1.74 / 0.77 / 5 | 0.98 | 5 |
| (125,125,2) | 339.8 (250) | 2 / 2.72 / 1.16 / 8 | 1.97 | 1 / 2.72 / 1.94 / 9 | 1.97 | 5 |
| (125,125,4) | 525.6 (500) | 2 / 4.20 / 3.33 / 12 | 3.87 | 1 / 4.20 / 3.80 / 13 | 3.87 | 5 |
| (125,125,6) | 760.2 (750) | 2 / 6.08 / 5.78 / 15 | 5.71 | 1 / 6.08 / 5.64 / 15 | 5.71 | 3 |
| (125,125,8) | 1002.0 (1000) | 2 / 8.02 / 7.76 / 17 | 7.49 | 2 / 8.02 / 7.78 / 18 | 7.49 | 0 |
| (125,125,10) | 1250.6 (1250) | 2 / 10.00 / 9.86 / 19 | 9.20 | 3 / 10.00 / 9.94 / 21 | 9.20 | 0 |

(all 40 classes in `stats_cs.log`). Three facts that any generator must reproduce:

1. **The ones overshoot d·m at low density and match it at high density**: ×1.36 at d = 2 in every
   square class (30 to 125), ×1.30 at (50,100,2), ×1.74 at (100,50,2); ×1.05 at d = 4; ×1.00 ± 0.02 at
   d ≥ 6. Bernoulli(d/n) with nothing else cannot do this; a fixed size d cannot either.
2. **Pattern sizes have a binomial-like variance at d ≥ 6 (var ≈ d(1 − d/n)), below it at d = 2
   (1.0–1.5 against 1.9) and no mass at 0 or 1**: a Binomial(n, d/n) with its 0 and 1 moved up to 2.
3. **Patterns per customer: a Binomial-like spread with no zeros and plenty of ones.**
   The correlation between a pattern's size and its customers' counts (over incidences) is
   −0.09 … +0.04, i.e. no size–degree assortativity beyond what padding induces.

Every file's MOSP graph is connected (`all connected = True` in every class).

### 1.3 Candidates fitted by simulation (`fit_generators.log`, `fit_generators.csv`)

Per class and candidate, 200 accepted instances; for each of 11 statistics (ones, row variance,
row max, column variance, min, max, share of size-2 and size-3 patterns, share of 1- and
2-pattern customers, size correlation) the observed 5-file mean is scored as a z against the
simulated distribution of a 5-file mean. The summary (mean z² over the 40 classes × 11 statistics;
share of |z| > 3; worst acceptance rate of the connectivity rejection, cap 2,000 tries):

| candidate | classes reachable | mean z² | share \|z\| > 3 | min acceptance |
|---|---|---|---|---|
| (i) exactly d per pattern, customers padded to ≥ 2 | 40 | 3,659 | 0.63 | 1 |
| (ii) Bernoulli(d/n), customers padded to ≥ 2 | 40 | 1,065 | 0.25 | 1 |
| (iii) = (i) + discard decomposable | 40 | 3,621 | 0.64 | 0.99 |
| exactly d, customers padded to ≥ 1, discard decomposable | 39 | 3,223 | 0.54 | 0.02 |
| the paper as written: Bernoulli(d/n), discard decomposable | 33 | 3.4 | 0.05 | 0.005 |
| Bernoulli, patterns padded to ≥ 2, discard decomposable | 36 | 1.3 | 0.02 | 0.001 |
| Bernoulli, patterns *redrawn* until ≥ 2, discard decomposable | 38 | 242 | 0.08 | 0.0003 |
| Bernoulli, customers padded to ≥ 1 only, discard decomposable | 39 | 31 | 0.09 | 0.0006 |
| **Bernoulli(d/n), customers padded to ≥ 1, patterns padded to ≥ 2, discard decomposable** | **40** | **2.0** | **0.05** | **0.005** |
| same, patterns first then customers | 40 | 2.3 | 0.06 | 0.02 |
| same without the discard | 40 | 2.4 | 0.06 | 1 |

"Padded" means: a short pattern gains uniformly random customers it lacks until it has 2; an
empty customer joins one uniformly random pattern. "Discard decomposable" is rejection until the
MOSP graph is connected.

**Verdict.** The three candidates the question named — (i), (ii), (iii), all with *customers*
padded to ≥ 2 — are refuted outright (mean z² in the thousands; the files have customers with one
pattern in 5 of 5 files at every d = 2 class, and fixed-size patterns have zero variance where the
files have d(1 − d/n)). The generator is the paper's description plus two repairs the paper does
not mention: **Bernoulli entries at density ≈ d/n; every empty customer given one random pattern;
every pattern with fewer than two customers padded to two; instances with a disconnected MOSP
graph discarded.** This family reproduces every class, including the two the pure-rejection
versions cannot reach at all (`Random-100-50-2` needs each of 100 customers covered by 50 products
of mean size 2: with rejection alone that is e^{−20} per draw; with the repairs it is accepted
once in 220 draws), with mean z² = 2.0 over 440 (class, statistic) cells and 5 % of cells beyond
3σ (3 % is expected by chance at 11 correlated statistics).

The pure rejection version "patterns padded to ≥ 2, discard decomposable" scores marginally
better on the 36 classes it can reach (mean z² 1.3) — the two are the same model wherever
acceptance is not tiny, since an accepted instance rarely has an empty customer — but it cannot
have produced `Random-100-50-2`, `Random-100-50-4`, `Random-100-100-2` or `Random-125-125-2`
(acceptance < 1/2,000 at (75,75,2) already). So the customer repair is needed, and it is the only
cheap mechanism that explains the ×1.74 ones at (100,50,2).

**What does not fit, honestly.** The best family *undershoots the ones count at low density by a
consistent 3–8 %* (z = +2.4 … +5.9 at the six d = 2 classes and at (100,50,2–6)), and the observed
pattern-size distribution has fewer size-2 patterns than it (0.55–0.60 against 0.64 at d = 2)
and a slightly heavier tail (row variance z = +1.3 … +3.9 at d = 2, with single 10-customer
patterns at p = 0.02–0.05 that are ~10⁻⁵ events). Redrawing short rows instead of padding them
*overshoots* by 5–10 % (z = −2 … −6). The truth lies between the two repairs, or the density is
2–8 % above d/n at d ≤ 4; with five files per class the residual is 2–4σ and cannot be resolved
further. Variants tried in `fit_variants.log`: see §1.4.

### 1.4 Variants on the d ≤ 4 classes (`fit_variants.log`; 16 classes × 5 statistics, 200 instances each)

| variant | mean z² | share \|z\| > 3 | ones z at the six square d = 2 classes (30 … 125) | at (100,50,2) |
|---|---|---|---|---|
| best family, p = d/n | 4.0 | 0.16 | +1.6, +2.3, +3.9, +3.3, +2.6, +2.6 | +5.6 |
| best family, p = 1.05 d/n | 2.6 | 0.05 | +0.4, +1.7, +3.2, +2.3, +1.4, +0.8 | +5.2 |
| best family, p = 1.10 d/n | 2.6 | 0.08 | −0.1, +0.7, +1.6, +1.1, −0.1, −0.4 | +3.4 |
| empty patterns redrawn, size-1 patterns padded, empty customers padded | 3.5 | 0.10 | +0.5, +1.5, +2.2, +2.0, +0.8, +0.4 | +4.3 |

A density 5–10 % above d/n removes the ones residual on the square classes (and (50,100,2),
z = −1.3 at 1.10) but not at (100,50,2), which stays 3.4σ denser than any variant; the row-variance
excess at (40,40,2) (one 10-customer pattern among 200 at p = 0.05) stays at +2σ under every
variant and is a single outlier. So the family is settled and its density constant is not:
**p = (1.05–1.10) · d/n at d ≤ 4, p = d/n within noise at d ≥ 6**, with the 100 × 50 classes
denser still. Chu & Stuckey's phrase "calculate a density that will achieve the specified
average" admits a calibration we cannot reconstruct from five files per class.

## 2. Does the first-moment bound hold under the real generator?

The bound of `finite_bound_cs.py` needs, for every pair (A, R) with |A| = t, |R| = t − 1,

    P(no pattern meets both A and R | realised sizes s_1..s_m) ≤ ∏_j q(s_j),   q(s) = [C(n−t,s) + C(n−t+1,s) − C(n−2t+1,s)] / C(n,s),

which is an equality when the patterns are independent uniform subsets of their sizes. The real
generator pads short patterns and empty customers and rejects disconnected instances, so the sets
are neither uniform given their sizes nor independent. Two measurements (`mc_empty_pairs.py`,
`floor_violation.py`).

### 2.1 A fixed pair, directly (`mc_empty_pairs.log`, `mc_empty_pairs.csv`)

Cells n = m ∈ {30, 50}, d ∈ {2, 4, 6}; 2,000 instances per cell and generator; in each instance
4,000 uniformly random disjoint pairs (A, R) of sizes (t, t − 1) — by the generator's symmetry
under customer relabelling a random pair and a fixed pair have the same empty probability — for
every t at which ∏q ≥ 10⁻⁶ for patterns of size d. Reported: the ratio of the mean empty fraction
to the mean of ∏_j q(s_j) over the sampled instances, with a 95 % bootstrap interval over
instances (pairs within an instance are correlated; the bootstrap resamples instances). A ratio
≤ 1 means the bound is conservative *on average over instances*; the "low / high ones" split
in the log (instances below / above the median total ones) checks that the direction does not
reverse between sparse and dense draws — it does not, in any cell.

| cell | generator | ratio P(empty) / E[∏q] at t = 2, 3, 4, … (95% CI half-width; hits) |
|---|---|---|
| (30,30,2) | best fit (Bernoulli, pad C≥1, pad P≥2, connected) | t=2: **0.991** ±0.001; t=3: **0.962** ±0.002; t=4: **0.912** ±0.004; t=5: **0.845** ±0.007; t=6: **0.766** ±0.010; t=7: **0.689** ±0.016; t=8: **0.624** ±0.032; t=9: **0.579** ±0.079; t=10: (12 hits); t=11: (0 hits); t=12: (0 hits); t=13: (0 hits) |
| (30,30,2) | paper as written (Bernoulli, connected) | t=2: **0.984** ±0.001; t=3: **0.936** ±0.002; t=4: **0.858** ±0.004; t=5: **0.760** ±0.006; t=6: **0.653** ±0.010; t=7: **0.551** ±0.013; t=8: **0.491** ±0.029; t=9: **0.428** ±0.070; t=10: (18 hits); t=11: (2 hits); t=12: (0 hits); t=13: (0 hits) |
| (30,30,2) | (i) fixed d, customers padded to ≥2 | t=2: **0.982** ±0.001; t=3: **0.916** ±0.001; t=4: **0.798** ±0.003; t=5: **0.650** ±0.004; t=6: **0.498** ±0.005; t=7: **0.365** ±0.008; t=8: **0.261** ±0.016; t=9: **0.190** ±0.036; t=10: (4 hits); t=11: (1 hits); t=12: (0 hits); t=13: (0 hits) |
| (30,30,2) | (ii) Bernoulli, customers padded to ≥2 | t=2: **0.973** ±0.001; t=3: **0.887** ±0.002; t=4: **0.751** ±0.004; t=5: **0.594** ±0.005; t=6: **0.444** ±0.008; t=7: **0.335** ±0.013; t=8: **0.254** ±0.028; t=9: **0.210** ±0.080; t=10: (4 hits); t=11: (0 hits); t=12: (0 hits); t=13: (0 hits) |
| (30,30,2) | control: best-fit sizes, uniform sets | t=2: **1.000** ±0.001; t=3: **1.000** ±0.002; t=4: **1.001** ±0.004; t=5: **0.998** ±0.008; t=6: **1.003** ±0.014; t=7: **0.990** ±0.024; t=8: **0.993** ±0.048; t=9: **0.955** ±0.104; t=10: **1.033** ±0.300; t=11: (5 hits); t=12: (0 hits); t=13: (0 hits) |
| (30,30,4) | best fit (Bernoulli, pad C≥1, pad P≥2, connected) | t=2: **0.993** ±0.003; t=3: **0.970** ±0.008; t=4: **0.934** ±0.018; t=5: **0.874** ±0.042; t=6: **0.903** ±0.174 |
| (30,30,4) | paper as written (Bernoulli, connected) | t=2: **0.984** ±0.003; t=3: **0.944** ±0.007; t=4: **0.877** ±0.016; t=5: **0.809** ±0.043; t=6: **0.757** ±0.147 |
| (30,30,4) | (i) fixed d, customers padded to ≥2 | t=2: **0.971** ±0.002; t=3: **0.886** ±0.005; t=4: **0.755** ±0.010; t=5: **0.615** ±0.027; t=6: **0.478** ±0.106 |
| (30,30,4) | (ii) Bernoulli, customers padded to ≥2 | t=2: **0.965** ±0.002; t=3: **0.871** ±0.006; t=4: **0.737** ±0.014; t=5: **0.572** ±0.034; t=6: **0.567** ±0.143 |
| (30,30,4) | control: best-fit sizes, uniform sets | t=2: **1.001** ±0.003; t=3: **1.005** ±0.008; t=4: **1.016** ±0.020; t=5: **1.036** ±0.048; t=6: **1.113** ±0.199 |
| (30,30,6) | best fit (Bernoulli, pad C≥1, pad P≥2, connected) | t=2: **0.996** ±0.007; t=3: **0.978** ±0.027; t=4: **1.082** ±0.132 |
| (30,30,6) | paper as written (Bernoulli, connected) | t=2: **0.990** ±0.007; t=3: **0.961** ±0.028; t=4: **0.959** ±0.145 |
| (30,30,6) | (i) fixed d, customers padded to ≥2 | t=2: **0.976** ±0.006; t=3: **0.910** ±0.017; t=4: **0.784** ±0.094 |
| (30,30,6) | (ii) Bernoulli, customers padded to ≥2 | t=2: **0.976** ±0.007; t=3: **0.903** ±0.022; t=4: **0.704** ±0.109 |
| (30,30,6) | control: best-fit sizes, uniform sets | t=2: **1.002** ±0.007; t=3: **1.000** ±0.026; t=4: **0.998** ±0.129 |
| (50,50,2) | best fit (Bernoulli, pad C≥1, pad P≥2, connected) | t=2: **0.997** ±0.001; t=3: **0.984** ±0.001; t=4: **0.962** ±0.002; t=5: **0.930** ±0.003; t=6: **0.884** ±0.004; t=7: **0.827** ±0.007; t=8: **0.766** ±0.010; t=9: **0.712** ±0.016; t=10: **0.632** ±0.026; t=11: **0.605** ±0.059; t=12: **0.624** ±0.146; t=13: (11 hits); t=14: (2 hits); t=15: (0 hits); t=16: (0 hits); t=17: (0 hits) |
| (50,50,2) | paper as written (Bernoulli, connected) | t=2: **0.995** ±0.001; t=3: **0.975** ±0.002; t=4: **0.935** ±0.004; t=5: **0.886** ±0.006; t=6: **0.807** ±0.009; t=7: **0.730** ±0.014; t=8: **0.653** ±0.020; t=9: **0.572** ±0.031; t=10: **0.499** ±0.055; t=11: **0.433** ±0.123; t=12: (5 hits); t=13: (2 hits); t=14: (0 hits); t=15: (0 hits); t=16: (0 hits); t=17: (0 hits) |
| (50,50,2) | (i) fixed d, customers padded to ≥2 | t=2: **0.993** ±0.000; t=3: **0.967** ±0.001; t=4: **0.915** ±0.002; t=5: **0.833** ±0.002; t=6: **0.731** ±0.003; t=7: **0.616** ±0.004; t=8: **0.494** ±0.006; t=9: **0.389** ±0.008; t=10: **0.300** ±0.015; t=11: **0.203** ±0.025; t=12: **0.163** ±0.050; t=13: (3 hits); t=14: (0 hits); t=15: (0 hits); t=16: (0 hits); t=17: (0 hits) |
| (50,50,2) | (ii) Bernoulli, customers padded to ≥2 | t=2: **0.989** ±0.001; t=3: **0.952** ±0.001; t=4: **0.881** ±0.002; t=5: **0.783** ±0.003; t=6: **0.667** ±0.004; t=7: **0.550** ±0.006; t=8: **0.433** ±0.009; t=9: **0.345** ±0.014; t=10: **0.260** ±0.027; t=11: **0.186** ±0.057; t=12: (7 hits); t=13: (1 hits); t=14: (0 hits); t=15: (0 hits); t=16: (0 hits); t=17: (0 hits) |
| (50,50,2) | control: best-fit sizes, uniform sets | t=2: **1.000** ±0.000; t=3: **0.999** ±0.001; t=4: **1.000** ±0.002; t=5: **1.000** ±0.003; t=6: **0.999** ±0.005; t=7: **0.997** ±0.009; t=8: **0.992** ±0.014; t=9: **1.008** ±0.023; t=10: **1.014** ±0.038; t=11: **1.016** ±0.081; t=12: **0.867** ±0.167; t=13: **1.391** ±0.540; t=14: (4 hits); t=15: (0 hits); t=16: (0 hits); t=17: (0 hits) |
| (50,50,4) | best fit (Bernoulli, pad C≥1, pad P≥2, connected) | t=2: **0.997** ±0.001; t=3: **0.988** ±0.003; t=4: **0.973** ±0.007; t=5: **0.945** ±0.013; t=6: **0.918** ±0.030; t=7: **0.878** ±0.094; t=8: **0.858** ±0.307 |
| (50,50,4) | paper as written (Bernoulli, connected) | t=2: **0.994** ±0.001; t=3: **0.974** ±0.003; t=4: **0.940** ±0.006; t=5: **0.892** ±0.014; t=6: **0.821** ±0.031; t=7: **0.690** ±0.085; t=8: **0.830** ±0.353 |
| (50,50,4) | (i) fixed d, customers padded to ≥2 | t=2: **0.989** ±0.001; t=3: **0.954** ±0.002; t=4: **0.887** ±0.005; t=5: **0.797** ±0.009; t=6: **0.683** ±0.018; t=7: **0.571** ±0.051; t=8: **0.677** ±0.230 |
| (50,50,4) | (ii) Bernoulli, customers padded to ≥2 | t=2: **0.988** ±0.001; t=3: **0.947** ±0.003; t=4: **0.877** ±0.006; t=5: **0.786** ±0.013; t=6: **0.691** ±0.029; t=7: **0.608** ±0.086; t=8: (2 hits) |
| (50,50,4) | control: best-fit sizes, uniform sets | t=2: **1.000** ±0.001; t=3: **1.000** ±0.003; t=4: **1.000** ±0.007; t=5: **0.997** ±0.015; t=6: **1.023** ±0.034; t=7: **1.014** ±0.105; t=8: **1.175** ±0.385 |
| (50,50,6) | best fit (Bernoulli, pad C≥1, pad P≥2, connected) | t=2: **1.000** ±0.002; t=3: **0.997** ±0.009; t=4: **1.020** ±0.028; t=5: **1.111** ±0.148 |
| (50,50,6) | paper as written (Bernoulli, connected) | t=2: **0.998** ±0.003; t=3: **0.987** ±0.009; t=4: **0.963** ±0.027; t=5: **0.969** ±0.136 |
| (50,50,6) | (i) fixed d, customers padded to ≥2 | t=2: **0.992** ±0.002; t=3: **0.962** ±0.006; t=4: **0.906** ±0.019; t=5: **0.861** ±0.093 |
| (50,50,6) | (ii) Bernoulli, customers padded to ≥2 | t=2: **0.992** ±0.003; t=3: **0.966** ±0.009; t=4: **0.929** ±0.026; t=5: **0.792** ±0.119 |
| (50,50,6) | control: best-fit sizes, uniform sets | t=2: **1.001** ±0.003; t=3: **1.003** ±0.008; t=4: **1.012** ±0.029; t=5: **1.015** ±0.135 |

**Direction: padding and rejection make empty pairs *less* likely, so the bound stays valid.**
For the generators that repair, the ratio is below 1 at d = 2 and d = 4 at every t with enough
hits, falling with t; at d = 6 the best-fit generator is at 1 within error (0.997–1.02 ± 0.03 at
n = 50), because at p = 0.12 the repairs almost never fire and the rejection almost never rejects,
so the model is exact there — the departures are confined to the sparse classes, which is where
the bound is loose anyway. The customer-padded candidates (i) and (ii) sit below 1 at every d. The
control (the best-fit generator's instances with every pattern redrawn as a uniform subset of
its own size) sits at 1 within its interval, so the estimator is unbiased. The ratio falls
monotonically with t: for the best-fit generator at (30,30,2) from 0.99 at t = 2 to 0.58 ± 0.08
at t = 9; the paper's pure rejection version is 0.98 → 0.76 at (30,30,4), t = 2…6; the
customer-padded candidates (i) and (ii) fall faster (0.98 → 0.19 and 0.97 → 0.21 at t = 9),
because padding every customer to two patterns adds ones where a pair is most likely to be
empty. Why the direction is this one: every repair only *adds* ones (so by monotone coupling an
empty pair in the repaired matrix was empty before), and the added ones go to the shortest rows
and columns, which is where the uniform-given-sizes model puts its empty pairs; rejection of
disconnected instances is conditioning on an increasing event, which by Harris–FKG lowers every
decreasing event's probability. The product form over patterns is what the measurement cannot
check at the operating point: the floors in `finite_bound_cs.log` are set where
C(n,t)C(n−t,t−1)·∏q ≈ 10⁻² … 1, i.e. ∏q ≈ 10⁻¹⁰ … 10⁻¹³ at n = 30, three to seven decades below
what direct sampling reaches (10⁻⁵ … 10⁻⁶). What the measurement shows is the trend in t up to
there, which is monotone and in the safe direction, and §2.2 tests the operating point itself.

### 2.2 The floor against the exact optimum (`floor_violation*.log`, `floor_violation.csv`)

Instances from the best-fit generator at n = m ∈ {30, 40}, d ∈ {2, 4, 6} (1,000 per class) and
d ∈ {8, 10} (300 per class), each solved exactly by `satisfiability.solve_mosp_exact` (witnesses
persisted under `sim_solutions/`), and the floor computed from each instance's realised sizes as
in `finite_bound_cs.py`. If the model were exact, P(optimum < floor at 0.01) ≤ 0.01 and
P(optimum < floor at 1) ≤ 1 (the latter is no guarantee at all; it is listed to show how tight
the bound runs).

| class | N | mean optimum | mean floor (bound < 1) | mean floor (bound < 0.01) | P(opt < floor at 1) | P(opt < floor at 0.01) | min(opt − floor at 0.01) | solve time |
|---|---|---|---|---|---|---|---|---|
| (30,30,2) | 1000 | 7.78 | 4.95 | 3.64 | 0.0000 | **0.0000** | 1 | 142 s |
| (30,30,4) | 1000 | 15.81 | 12.86 | 11.24 | 0.0000 | **0.0000** | 2 | 194 s |
| (30,30,6) | 1000 | 22.08 | 19.78 | 18.07 | 0.0010 | **0.0000** | 1 | 185 s |
| (30,30,8) | 300 | 25.73 | 24.15 | 22.47 | 0.0100 | **0.0000** | 1 | 45 s |
| (30,30,10) | 300 | 27.71 | 26.72 | 25.01 | 0.0200 | **0.0000** | 1 | 60 s |
| (40,40,2) | 1000 | 9.14 | 5.81 | 4.59 | 0.0000 | **0.0000** | 2 | 783 s |
| (40,40,4) | 1000 | 19.68 | 16.04 | 14.41 | 0.0000 | **0.0000** | 1 | 474 s |
| (40,40,6) | 1000 | 27.98 | 25.12 | 23.42 | 0.0040 | **0.0000** | 1 | 272 s |
| (40,40,8) | 300 | 33.12 | 30.98 | 29.31 | 0.0000 | **0.0000** | 1 | 103 s |
| (40,40,10) | 300 | 35.85 | 34.43 | 32.84 | 0.0133 | **0.0000** | 0 | 100 s |

7200 instances, 0 violations of the 0.01-floor; one instance ((40,40,10)) sits exactly on it. Total solver time 0.66 core-hours.

So the generator's departures from the model do not break the bound: the empirical violation rate
of the 0.01-floor is 0 in every class, against an allowance of 0.01, and the mean gap between the
optimum and the 0.01-floor is 2.7–3.0 stacks at d = 10, 3.3–3.8 at d = 8, 4.0–4.6 at d = 6 and
4.1–5.3 at d = 2–4 (at these sizes; on the 200 real instances it narrows to 3.5 % of the optimum
at 125 × 125, d = 10). The bound-at-1 floor — the README's "floor (< 1)" — is exceeded by the
true optimum in 98–100 % of instances; the 0.1–2 % below it at d ≥ 6 are what "bound < 1"
permits, and they show that floor is not a safe one to quote as a lower bound on its own.

**Conclusion for rigour.** As a statement about a *random* instance of the generator the bound
is supported in the only direction that matters: every departure from the uniform-independent
model that the fit found (padding of short patterns and empty customers, rejection of
disconnected instances) lowers the probability of an empty pair relative to ∏q(s_j), measured at
every reachable t, and the floor is never violated in 6,000 exactly solved instances. What is
not proved is the inequality itself under the real generator; a proof would go through the
monotone coupling (repairs add ones) plus FKG for the rejection, and would need the realised
sizes replaced by the pre-repair Bernoulli sizes — which is a weaker but clean bound: with
Bernoulli(p) entries, P(pair empty) = [(1−p)^t + (1−p)^{t−1} − (1−p)^{2t−1}]^m exactly, and
the repairs and rejection can only lower it.


## 3. The threshold against the ridge and against Gao (`q3_thresholds.log`)

### 3.1 The threshold is excess 1, in closed form

For patterns of fixed size d, m = μn, the rate at the balanced point is exact:
g(1/2) = ln 2 + μ ln(2·2^{−d} − 0) = ln 2 · (1 + μ(1 − d)). So g(1/2) < 0 iff

    d > d₀(μ) = 1 + 1/μ,   equivalently   μ(d − 1) = (n_ones − m)/n = excess > 1.

The bisection in `asymptotic_cs.py` reproduces this to its step (2.0031 at μ = 1 is 2 + the
10⁻⁴ grid). Just below d₀ the rate is positive on the whole interval (g(0.49) = +0.12 at d = d₀,
so β* = 0 exactly at the threshold and grows continuously above it). The threshold does not
depend on the size distribution's shape, only on its mean, because at a = 1/2 the per-pattern
term ln(2(1−a)^s − (1−2a)^s) = ln 2 − s ln 2 is linear in s; it does depend on quenched (sizes
given, E_s ln) against annealed (Bernoulli sizes averaged inside the log, ln E_s) — the annealed
Bernoulli threshold solves 2e^{−d/2} − e^{−d} = 2^{−1/μ} and is 2.456 at μ = 1.

| μ = m/n | d₀ = 1 + 1/μ (first moment, fixed sizes) | annealed Bernoulli d₀ | Gao Thm 2 (c = μd > 2 ⇒ d > 2/μ) | ridge, measured (fixed generator, §25) | ridge formula 1 + 2.4/μ | giant component (fixed) | excess at d₀ / at ridge |
|---|---|---|---|---|---|---|---|
| 0.125 | 9.00 | 12.47 | 16.0 | 20.7 [18.7, 21.6] | 20.2 | 3.37 | 1 / 2.4 |
| 0.25 | 5.00 | 6.90 | 8.0 | 9.17–10.63 | 10.6 | 2.56 | 1 / 2.4 |
| 0.5 | 3.00 | 4.02 | 4.0 | 5.24–5.64 | 5.8 | 2.00 | 1 / 2.4 |
| 1 | 2.00 | 2.46 | 2.0 | 3.31–3.47 | 3.4 | 1.62 | 1 / 2.4 |
| 2 | 1.50 | 1.56 | 1.0 | 2.01 (grid edge) | 2.2 | 1.37 | 1 / 2.4 |
| 4 | 1.25 | 1.02 | 0.5 | — | 1.6 | 1.21 | 1 / 2.4 |
| 8 | 1.125 | 0.68 | 0.25 | — | 1.3 | 1.11 | 1 / 2.4 |

β* at the measured ridge (fixed sizes): 0.12, 0.20, 0.19, 0.21, 0.27 for μ = 2, 1, ½, ¼, ⅛ — the
ridge is where the first moment already certifies a fifth of n.

### 3.2 Same curve, related, or unrelated?

- **First-moment threshold and ridge: the same one-parameter family, at different values of the
  parameter.** Both are lines of constant excess μ(d − 1) in the (μ, d) plane: the first moment
  becomes non-vacuous at excess 1, the ridge sits at excess 2.0–2.5 (§25's `1 + 2.4/μ`, measured
  2.0 / 3.3–3.5 / 5.2–5.6 / 9.2–10.6 / 20.7 against the threshold's 1.5 / 2 / 3 / 5 / 9). The ridge
  is the threshold's curve shifted by one unit of excess — one independent cycle of the
  customer–product incidence graph per customer — at every μ from ⅛ to 2. §25 (e) found the
  excess empirically and could not say why 2; this says the first-moment lower bound turns on
  at excess 1, so the ridge lies one unit inside the region where pathwidth is provably linear,
  with β* ≈ 0.12–0.27 there. It is not the giant-component threshold of §25 (f) (that is
  branching factor μd(d − 1) = 1, a different curve: 1.37 / 1.62 / 2.0 / 2.56 / 3.37).
- **Gao's threshold is a different curve that crosses ours at μ = 1.** His Theorem 2 is stated
  for the Bernoulli model G_I(n, m, p) with m = n^α and p ≥ 2/m, i.e. c = mp = expected items
  per vertex > 2 — in our coordinates μd > 2, d > 2/μ. That coincides with d₀ = 1 + 1/μ only at
  μ = 1 (both 2); at μ = ½ it is 4 against 3, at μ = 2 it is 1 against 1.5. The two are not the
  same quantity: his is "patterns per customer", ours is "excess", and only at m = n do they
  agree.
- **Gao's proof is a first moment over empty pairs — the same count — but, as printed, it drops
  a factor.** §4 (arXiv v1, pp. 16–17): a balanced partition (S, A, B) with |S| = βn is counted,
  P{no edge between A∖S and B∖S} = [(1−p)^{|A|} + (1−p)^{|B|} − (1−p)^{|A|+|B|}]^m by the
  independence of the items (his (4.22)), exactly our ∏_j q(s_j) with Bernoulli sizes. He then
  writes this as (1−p)^{|A|m}·[1 + (1−p)^{|B|−|A|} − (1−p)^{(1−β)n−|A|−|B|}]^m and keeps only
  (1−p)^{|A|m} = e^{−c|A|} (p = c/m) in the next line, dropping the bracket, which is ≥ 1 and
  ≤ 2^m — for m = Θ(n) it is e^{Θ(n)} and changes the constant; for α > 1 it is what makes the
  bound vacuous (with p = c/m and m ≫ n the graph has o(n) edges, so linear treewidth is false
  there, which the printed theorem's "any α > 0" would contradict). With the bracket kept, at
  m = μn and Bernoulli patterns the condition at the balanced point is the annealed one above,
  2e^{−d/2} − e^{−d} < 2^{−1/μ}, i.e. c = μd > 2.456 at μ = 1, not 2. So **c > 2 is an artefact of
  the dropped factor, and it is slightly too strong**, not too weak, as the survey (§4) guessed.
  The surviving content of Theorem 2 is the method, which is ours. His threshold is not the
  ridge either (2/μ against 1 + 2.4/μ: 2 vs 3.4 at μ = 1, 4 vs 5.4 at μ = ½).

## 4. Unresolved

1. **The generator's density constant.** The family is settled (Bernoulli entries, empty
   customers given one pattern, patterns padded to two customers, disconnected instances
   discarded) but the realised density is 5–10 % above d/n at d ≤ 4 and the 100 × 50 classes are
   denser still (+3σ after a 10 % lift); whether the padding redraws or pads a short row is also
   between two variants. Five files per class cannot separate these; the generator's source
   (gchu@csse.unimelb.edu.au, per the dataset description) would.
2. **The inequality P(pair empty | sizes) ≤ ∏q(s_j) is measured, not proved, under the real
   generator**, and only to ∏q ≈ 10⁻⁶ (t ≤ 10 at n = 30, t ≤ 11 at n = 50); the floors are set
   at ∏q ≈ 10⁻¹⁰ … 10⁻¹³. The trend is monotone in the safe direction and the floor is never
   violated in 7,200 exact solves, but a proof needs the monotone coupling (repairs only add ones)
   with the bound restated on the *pre-repair* Bernoulli sizes, where it is exact, plus FKG for
   the rejection. That version is weaker numerically (sizes before padding are smaller).
3. **The quenched / annealed distinction** matters for the asymptotic constant with random
   sizes: `asymptotic_cs.py` averages the log over the empirical sizes (sizes given), which is the
   right statement for a sequence of instances whose size histogram converges; the unconditional
   constant for the generator would average inside the log and is smaller (threshold 2.46
   rather than 2.00 at μ = 1 for Bernoulli sizes). The README should say which it quotes.
4. **Gao (2012) Theorem 2.** The printed proof drops a factor in [1, 2^m]; the exact first
   moment at m = μn needs c = μd > 2.57 at μ = 1 (treewidth-type partitions, a ∈ [⅓, ½]) and
   more at larger μ, less at smaller μ (1.96 at μ = ¼, 1.91 at μ = ⅛), so "c > 2 for any α" is
   proved by his argument only where μ → 0 (α < 1), is not established by it at α = 1, and is
   false for α > 2 (o(n) edges). We did not check the published DAM version against the arXiv
   text; if it differs the page references here (arXiv v1, pp. 16–17) need updating.
5. **Why excess 2 and not excess 1 at the ridge.** The threshold-at-excess-1 result gives the
   ridge a natural origin (the hardness ridge is one unit of excess inside the region where the
   pathwidth is provably linear) but no mechanism for the factor 2–2.4; the §25 (e) reading —
   one independent cycle per customer — is a description, not a derivation.
6. **Not run**: nothing at n > 50 for the pair test, nothing above n = 40 for the exact-solve
   test, and nothing on the 200 real instances beyond reading their sizes, as the compute rule
   requires. Total compute: about 2.5 core-hours for the pair test, 0.65 for the exact solves,
   0.3 for the generator fits.
