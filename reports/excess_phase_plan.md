# A one-parameter theory of MOSP in the excess — plan for Ralph loop0010

*2026-10-31. The sequel to the first-moment work of this week
(`reports/random_graph_first_moment.md`, `reports/scratch/clique_cover_moment/`,
Appendix E of the paper). The loop files are `Ralph_Loops/loop0010/`; each item
there is self-contained. This document says what the loop stands on, what it
asks, in what order and at what price, and where the record corrects the brief
that produced it. Nothing here changes a solver default; nothing re-solves an
instance that is already certified.*

## 0. The parameter, and what the loop stands on

The **excess** of an instance with `n` customers, `m` patterns and `n_ones`
ones is

    e = (n_ones − m) / n = (mean patterns per customer) − 1 = r (c − 1),

with `r = m / n` and `c = n_ones / m` the mean customers per pattern. The
customer–pattern incidence graph `B` has `n + m` vertices, `n_ones` edges and
`κ` components, so its cyclomatic number per customer is `γ / n = e − 1 + κ / n`.
Three lines of constant excess are on record, and they are the reason for a
one-parameter theory:

- **`e = 1`: the first moment turns on.** For random clique covers with
  `m = μ n` patterns of mean size `d`, the exponent of the expected number
  of balanced empty pairs is `ln 2 · (1 + μ (1 − d))`, so the first-moment
  constant `β*(d, μ)` is positive iff `μ (d − 1) > 1`, i.e. `e > 1`
  (`REPORT_generator.md` §3.1, in closed form; the inequality itself is the
  Lean theorem `prob_coversOfMospValueLe_le`, `CliqueCoverMoment.lean`). The
  threshold depends on the size law only through its mean; the constant
  depends on `(d, μ)` separately (`asymptotic_cs.log`: `β*` runs 0.24–0.32
  along `e = 3`).
- **`e ≈ 2–2.4`: the hardness ridge.** The nodes to refute `optimum − 1` peak,
  at every product ratio from `m = 2n` to `m = n / 8`, at `(n_ones − m)/n ≈
  2–2.4` (`reports/ml_nature.md` §25), and no threshold of `B` coincides with
  it; what peaks there is the number of closed sets reachable through
  fitting steps (§36). Its height needs `m` separately (§37).
- **`e_g(r) = (√(r² + 4r) − r) / 2`: the giant component of `B`.** The
  branching factor `r c (c − 1) = 1` of the random bipartite incidence graph,
  in excess coordinates: 0.62 at `r = 1`, 0.74 at `r = 2`, 0.50 at `r = ½`
  (§36 (a); §25's table 1.37 / 1.62 / 2.0 in `col_mean`).

Where the instances sit (`learning/data/instances.csv`, realised `e`): the
24 SCOOP instances at median 1.35, range 0.97–2.50; Faggioli–Bentivoglio
median 1.98; the Chu & Stuckey `d = 2` classes at 1.6–2.0 (125 × 125:
1.66–1.78), `d = 4` at 3.0–3.6, `d = 6` at 4.7–5.5; the Challenge, Harvey and
Simonis sets at median 5. Industry sits between the threshold and the ridge.

What is proved: `MOSP = pathwidth + 1` (`MOSPGraph.lean`); the empty-pair
lemma, the first-moment count for `G(n, p)` and for clique covers, and
Theorem A's finite exponential bound (`EmptyPair.lean`, `FirstMoment.lean`,
`FirstMomentAsymptotics.lean`, `CliqueCoverMoment.lean`); trees on at most
`treeBound k` vertices have pathwidth at most `k`, the complete ternary tree
has pathwidth its height (`TreeBound.lean`); the branch lemma and its
separator form (`Sandwich.lean`); `pw ≤ n − α` (`IndependenceBound.lean`).
What is measured: zero of 200 certified Chu & Stuckey optima below the
0.01 floor; the certified `opt / n` at 125 × 125 sits 0.06–0.10 above
`β*`; the fitted generator (Bernoulli entries, empty customers padded to one
pattern, patterns to two customers, disconnected instances discarded) makes
empty pairs rarer than the uniform model, measured, not proved; the two-key
closing rule is exact on 94.2% of the corpus (§28).

### Three places the record corrects the brief

1. **The hardest benchmark classes are not on the ridge.** The brief and the
   paper's Appendix E say the classes that took thousands of core-hours have
   excess 2–2.5. The files say the `d = 2` classes have `e = 1.6–2.0` and the
   `d = 4` classes `3.0–3.6`; the generated-ensemble ridge at `col_mean ≈ 3.3–3.5`
   (`m = n`, i.e. `e ≈ 2.3–2.5`) lies *between* them. §11 called `d = 2`
   "exactly on the ridge" in `col_mean` 2.7 against a ridge at 3; in excess
   the `d = 2` class is on the sparse flank, 0.6 below the peak, where SCOOP
   also lives. Item 12 corrects the sentence in `sec9e_appendix_random.tex`.
2. **`e < 1` is not a forest regime.** Below `e = 1` the incidence graph has
   fewer edges than vertices, but its giant component — with `Θ(n)`
   independent cycles — appears at `e_g(r) ≈ 0.62` for `r = 1`. The forest
   regime is `e < e_g(r)`, and "forest" is taken as a deterministic
   hypothesis on the instance (`γ = 0`), measured on every instance in item
   01, with the random-model corollary stated for `e < e_g(r)` only.
3. **A second moment cannot lift `β*`.** The first moment bounds
   `P(pw ≤ k) ≤ E[X]` for the empty-pair count `X`; a second moment bounds
   `P(X > 0)` from *below*, the wrong direction for a pathwidth lower bound.
   What can lift the constant is a first moment over a richer necessary
   structure — `ℓ` nested empty pairs, one per position of the layout — and
   that is item 08, with the second moment kept as the diagnostic of where
   the slack is. The brief's kill criterion (0.03 at `d = 6`, `μ = 1`) is
   kept for the structured count.

And one thing the brief's wording of B(i) would have had the loop do twice:
about 50,700 certified random clique covers already exist across `(d, μ, n)`
(`learning/data/ensemble/results*.csv`: `n = 10–100`, `m / n ∈ {⅛, ¼, ½, 1, 2,
4, 8}`, both generators), with `e`-matched series at `n = 50–75` for every
integer excess to 9. B(i) is therefore a scoring run (the two-key rule, 1 ms
per instance) and an analysis, not a certification campaign; the owner's
rule of 2026-10-12 forbids the latter without his word.

## 1. The questions and their items

Order: measurements that de-risk the theory (01–04), then analysis (05–10),
then Lean (11), then writing (12), then the reserve (13). Dependencies:
01 → 03, 04; 02 → 05, 08, 09; 03 → 06 → 11; 05 → 07 → 09; 10 is independent;
12 needs all.

**The map (01).** Every instance on record placed by `e`, `γ / n`, forest or
not, 2-core size, largest incidence component, against `e_g(r)`, `1` and the
ridge; per collection and per ensemble series; the 338 bound-gap instances
of §6 ("trees of cliques with branching") beside them. Descriptive; one
stated check (the largest component of `B` crosses one half within ±0.15 of
`e_g(r)`).

**Is `lim opt / n` a function of `e` alone? (02)** — B(i), B(iii). Per
series slopes `b` of `opt ≈ a + b n` at `n = 30–100`; `e`-matched pairs with
different `(d, μ)` (`e = 2`: `(3, 1)`, `(5, ½)`, `(2, 2)`, `(9, ¼)`; `e = 3`:
`(4, 1)`, `(7, ½)`, `(12, ¼)` at 2.75; all certified); `β*(d, μ)` beside them; the
two-key rule scored on every instance. *Kill for the one-parameter
hypothesis:* slopes at equal `e` differ by more than twice their error on
half the pairs. Either answer is the finding.

**The forest regime, brute force (03)** — A, first half. Exact pathwidth of
clique trees `CT(s, h, b)` and random block trees by the C program, against
the candidates `ω − 1 + pw(B)`, `ω − 1 + h`, `ω (pw(B) + 1) − 1` and the
TreeBound form; the caterpillar of cliques as the discriminating case; a
literature check on block graphs. *Kill:* no small-constant additive
formula fits `CT(s, h, b)` exactly → item 06 proves the blow-up bound only.

**Industrial instances (04)** — F, measurement half. The 24 SCOOP instances
(and the 300 Faggioli–Bentivoglio as the structured comparison): `e`, `γ`,
optimum, bounds, the rule, the 0.01 floor from their own sizes, recorded
certification cost, the cost model's prediction; the one-page planner's
statement, drafted. No re-run.

**`β⁺` by simulation (05)** — B(ii), first half. The rule, the BFS-layer
layout, `n − α_greedy` and the edge-count bound at `n = 100–5000` on fresh
random covers (no exact solve), `width / n = β⁺ + a / n` per cell, beside
`b` and `β*`. *Kill:* a cell's extrapolation is not quoted if the rule at
the largest `n` and the certified slope at `n ≤ 100` differ by more than
0.03.

**The forest regime, on paper (06)** — A, second half. Theorem F1: a forest
incidence graph gives `pw(G_M) ≤ ω (pw(B) + 1) − 1 ≤ ω (tb(n + m) + 1) − 1`,
so `MOSP ≤ ω (⌊log₃((6(n + m) + 3)/5)⌋ + 1)`; Theorem F2 the sharper form if
03 found one, else the branch-lemma lower bound and the gap; the random
corollary below `e_g(r)` with its citation status. Every statement
brute-force checked before it is called a theorem. *Kill:* a counterexample
to F1 stops the item.

**`β⁺` on paper (07)** — B(ii), second half. The BFS layer lemma (deterministic)
plus the two-type exploration recursion for the layer fractions; the greedy
independent set's differential-equation limit; `β⁺(d, μ)` the smaller,
tabulated against `β*`, `b` and the rule. The rule itself is not analysed,
and the paragraph says why. *Kill:* `β⁺ − β* > 0.5` everywhere → the constant
is recorded as uninformative and the gap attributed to the constructions.

**The structured count (08)** — C. `ℓ` nested empty pairs, exact per-pattern
factor by inclusion–exclusion, `β*_ℓ` for `ℓ ≤ 4`; the finite `ℓ = 2` floor on
the 200 instances (zero violations required); the second moment at `(6, 1)`
as the diagnostic. *Kill:* `β*_ℓ(6, 1) − β*(6, 1) < 0.03` for all `ℓ ≤ 4`.

**The ridge mechanism (09)** — D. H1: the ridge is where the gap between the
exact optimum and the first-moment floor is largest, tested on §25's 25
series at `n = 50–75` with the finite floor per instance and the asymptotic
constant per cell; the optimal-order count at `n = 20` as a secondary.
*Kill:* the gap's peak outside the node peak's bootstrap interval on more
than half the series, or mean score above 0.15 decades.

**Validity under the real generator (10)** — E. The exact pre-repair
Bernoulli bound; the monotone coupling (pads only add ones; an empty pair of
the padded matrix is one of the unpadded); the rejection, with the honest
observation that connectivity of the padded matrix need not be increasing
in the base entries, and the two rigorous forms (`1 / P(accepted)`, and
Harris–FKG where monotone); the numerical consequence per class. Lemmas
checked on 10,000 draws at `n = 8` first.

**Lean (11)** — G. In order of reach: the coupling inclusion (two lines over
`CliqueCoverMoment.lean`), F1's blow-up lemma (`ForestCover.lean`: the
incidence graph as a `SimpleGraph (C ⊕ P)`, a path decomposition of it
blown up to one of `mospGraph`, then TreeBound per component), the BFS layer
lemma. No `sorry`; blocked with a named `Prop` and the obstacle is a
deliverable.

**The write-up (12)** — H. `reports/excess_phase_diagram.md` assembled with
every claim's status (theorem / proved on paper / measured / conjectured);
a two-page subsection of Appendix E with the figure, Appendix A rows and
axiom lines, checked DOIs; the correction of point 1 above; the `CLAUDE.md`
paragraph drafted, not applied. "We found no prior statement", never
"first".

**Reserve (13).**

## 2. Budget

Modelled on loop0004 (13 items, 13 sessions, $235, 13.7 h wall) and
loop0009 (11 items, 11 sessions, about a day). Compute is small because the
exact optima exist; the only solver runs are new graphs (03) and layouts
without certification (05).

| item | sessions | wall-clock | dollars | compute (core-hours, nice 19) |
|---|---|---|---|---|
| 01 the map | 1 | 1.5 h | 15 | 0.5 (features over 64,000 instances) |
| 02 `opt / n` against `e` | 1 | 2 h | 20 | 0.2 (the rule, 50,700 × 1 ms) |
| 03 forest regime, brute force | 1 | 3 h | 20 | ≤ 6 (C program, ≤ 400 vertices) |
| 04 SCOOP | 1 | 1.5 h | 15 | 0 |
| 05 `β⁺` by simulation | 1 | 3 h | 20 | ≤ 8 (the rule at `n ≤ 5000`) |
| 06 forest regime, on paper | 1 | 3 h | 25 | 0.5 (the brute-force check) |
| 07 `β⁺` on paper | 1 | 3 h | 25 | 0.2 (recursions) |
| 08 structured count | 1 | 3 h | 25 | 1 (the `ℓ = 2` floor, the second moment) |
| 09 ridge hypothesis | 1 | 2 h | 20 | 2 (lattice counts at `n = 20`) |
| 10 validity | 1 | 2.5 h | 20 | 0.1 |
| 11 Lean | 1–2 | 4 h | 30 | 0 (lake build) |
| 12 write-up | 1 | 3 h | 25 | 0 |
| 13 reserve | 1 | 3 h | 20 | ≤ 4 |
| **total** | **13–14** | **≈ 35 h** | **≈ $280** | **≤ 25** |

Per-session cap 4 h (`knobs.json`), fix cap 45 min, three fix attempts; the
gate (lake build, two pytest suites, the paper's `make check`) takes about
10 min and is run once per item.

## 3. Risks

1. **The forest theorem may be the weak one.** F1 is a factor `ω` loose on a
   chain of cliques and probably on most forests; if item 03 finds that the
   true pathwidth of clique trees is additive in `ω` and the depth, the
   proof of that form is a new argument (the path and centroid lemmas of
   `TreeBound.lean` do not lift to blocks for free), and one session may
   not hold it. The plan then ships F1 and the gap.
2. **`β⁺` from provable constructions may be uninformative.** BFS layers on
   a graph of mean degree 8 reach width about 0.9 `n`; `n − α` is better but
   still far from the truth at `e ≳ 3`. The rule is near-exact and
   unanalysable in a session. The loop may end with `β*` from below, the
   rule from above by measurement, and no provable constant within 0.3 of
   either; item 07's kill records exactly that.
3. **The ridge hypothesis is a coincidence test, not a mechanism.** Twenty-five
   series at `n = 50–75` with peaks interpolated from three-cell grids can
   agree by accident at the 0.1-decade level; and §36's real finding — the
   reachable count — is a first-passage problem over `2^n` states that no
   item here attempts. A surviving H1 is evidence, not a theory of the
   ridge.

Two smaller ones: the machine is shared and loaded (load 27–40 on 32 cores
on the day of writing), so the 4 h caps may bind on items 03 and 05 — both
are told to sample and say so; and the paper's Appendix E already states
the ridge sentence this loop corrects, so item 12 must change a published
draft, with the reason recorded.

## 4. What would count as success

A map of every held instance in one parameter with the three lines on it;
the one-parameter question answered either way with error bars; a forest
theorem proved on paper and in Lean with its tightness measured; `β⁺`
tabulated by construction with its provable part separated from its
measured part; the structured count tried against a stated threshold; one
ridge hypothesis tested to a kill; the generator's validity stated to the
exact extent it is proved; and 24 industrial instances described in the
same coordinates, with a statement a planner could read, labelled as 24
instances. The plan does not promise the constant, the ridge mechanism, or
a theorem above `e_g(r)`.
