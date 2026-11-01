
## 10. Validity under the real generator, on paper (item 10, 2026-11-01)

**Question (E of the plan).** The first-moment inequality assumes the
patterns are uniform given their sizes. The fitted Chu & Stuckey generator
pads short patterns and empty customers and rejects disconnected instances
(`reports/scratch/clique_cover_moment/REPORT_generator.md` §1.3); measured,
the repairs make empty pairs rarer (§2.1 there) and 7,200 exact solves show
zero floor violations (§2.2). What is *proved*? **Answer.** The inequality
with the sizes of the table *before* the repairs is a theorem for the padded
instance, in both pad orders, by a monotone coupling (Theorem V3); in the
patterns-first order it holds with the truncated sizes `max(s, 2)` (the rows
after that pad are exactly uniform of those sizes); a Chernoff typical-set
argument on the i.i.d. sizes gives a quenched form of the same theorem
(V3′). The rejection is **not** an increasing event of the base entries — a
single added entry can make a pad vanish, disconnect the instance and lower
its pathwidth, measured at 0.7% of entry additions at `d = 2` — so Harris's
inequality does not apply to it directly; three rigorous forms survive
(Theorem V5): the trivial `1 / P(accepted)` with the acceptance measured,
Harris on the unconditional pad (which in practice coincides with the
trivial form, since the unconditional pads connect every instance), and
Harris on the no-repair event (useful only at `d = 10`, `n ≤ 40`); and for
the generator as the paper states it (no pads) the rejection costs nothing
at all. Numerically the proved floors are below the measured-model floors
of `finite_bound_cs.log` by more than one stack on 34–35 of the 40 classes:
trivial at `d = 2` in the Bernoulli form (40% of Bernoulli patterns have at
most one customer, and the pads that make them count are what the proof
cannot see), 3–13 in the truncated form there, and 2–13 stacks short at
`d = 4–6`, where the gap is almost entirely the difference between a bound
on the *average* over size vectors and the typical size vector. Every
lemma was checked by brute force before it was stated; no certified
optimum lies below any rigorous floor. The kill criterion's fallback (end
with the `1 / P(accepted)` form) is what the rejection comes to, and the
item says so.

**Size range.** The theorems are for every `n`, `m`, `p`. The checks: exact
identities in rationals at `n ≤ 12`; full enumeration of every base matrix
at `2 × 6` and `3 × 4` (`p = 1/3`) and at `3 × 5` for the pathwidth
probability; the coupling on 10,000 draws at `n = m = 8` for `d ∈ {2, 4}`
and both pad orders (40,000 draws); the acceptance and event rates on the 40
Chu & Stuckey classes at `p = d / n`, 2,000–60,000 draws per class and
order; the floors on the 200 Chu & Stuckey instances (their certified
optima read from `solutions/`, read only).

**Regenerate.** Library: `learning/first_moment.py`, the section "validity
under the real generator" (`lq_bernoulli`, `lq_truncated`,
`log_bound_bernoulli`, `log_bound_truncated`, `log_bound_quenched`,
`log_bound_best`, `floors_*`, `rejection_floors`, `log_disconnected_bound`,
`log_repair_bound`, `draw_aux`, `pad_customers_with_aux`,
`pad_patterns_with_aux`, `pad_with_aux`, `unconditional_pad`,
`mosp_connected`, `no_repair_needed`, `generator_draw`,
`generator_event_rates`, `wilson`, `customer_masks`,
`vertex_separation_brute`); tests `python -m pytest tests/test_first_moment.py
-q` (44, of which 13 new). Scratch: `nice -n 19 python3
reports/scratch/validity/check.py {exact, law, coupling, classes, table,
all}` — `check.log` (every stage appends; the table stage was run three
times while its columns were added, and the last block is the current one),
`classes.csv`, `floors.csv`, `tables.md`, `run_stdout.log`,
`table_stdout.log`. Wall: exact 10 s, law 20 s, coupling 70 s, classes 14 s
on 8 workers, table 4 min; about 0.1 core-hours in all at nice 19, load
0.2–1. Nothing solved, `solutions/` read only, the ledger untouched.

### 10.1 The generator, with its randomness made explicit

The fitted generator (`REPORT_generator.md` §1.3; `gen_candidates.py`,
`bern_padC1_padP2_conn`) draws an instance in four steps. Write the matrix
as `patterns × customers`, `B[i, j] = 1` iff pattern `i` contains customer
`j`, with `m` patterns, `n` customers and `p = d / n`.

1. **Base.** `B` has independent Bernoulli(`p`) entries.
2. **Customer pad.** Every customer with no pattern joins one uniformly
   random pattern.
3. **Pattern pad.** Every pattern with fewer than two customers gains
   uniformly random customers it lacks until it has two.
4. **Rejection.** The instance is kept iff its MOSP graph is connected.

The variant `bern_padP2_padC1_conn` applies 3 before 2 (fit `z²` 2.29
against 2.00; both reach all 40 classes). Which order the real code uses is
not known; neither is the density constant (`REPORT_generator.md` §1.4:
`p = (1.05–1.10) d / n` at `d ≤ 4`, `d / n` within noise at `d ≥ 6`).

**The auxiliary randomness.** Let `ω = (U, σ)` be independent of `B`: `U_j`
a uniform pattern index for every customer `j`, `σ_i` a uniform permutation
of the customers for every pattern `i`. Define `Φ(B, ω)`: step 2 adds
`(U_j, j)` for every empty column `j`; step 3 adds, for every row `i` with
fewer than two ones, the first customers it lacks in the order `σ_i`. A
uniform choice among candidates is the first candidate of a uniform
permutation restricted to them, so `Φ(B, ω)` has exactly the generator's
law (`pad_with_aux`; the `law` stage compares five statistics with the
scratch generator on 4,000 draws for four classes, all within 2.1 standard
errors). Write `M = Φ(B, ω)`; `M⁺ = B ∨ C(ω)` with `C(ω) = {(U_j, j) : all j}
∪ {(i, σ_i(1)), (i, σ_i(2)) : all i}`, every pad applied whether needed or
not (`unconditional_pad`); `E = {every column of B nonempty and every row of
B has ≥ 2 ones}`, the event that no repair fires. `G_X` is the MOSP graph of
a matrix `X` (customers adjacent iff they share a pattern), `acc = {G_M
connected}`, `acc⁺ = {G_{M⁺} connected}`, `t = ⌈(n − k)/2⌉`, `C = C(n, t)
C(n − t, t − 1)`, and

    q_p(t) = (1 − p)^t + (1 − p)^{t−1} − (1 − p)^{2t−1},    UB_B(k) = C · q_p(t)^m.

### 10.2 Statements

**Lemma V1 (the pre-repair bound, exact).** For disjoint customer sets
`A`, `R` with `|A| = a`, `|R| = r`,

    P((A, R) is an empty pair of G_B) = [(1 − p)^a + (1 − p)^r − (1 − p)^{a+r}]^m,

a product over independent patterns; and the factor is the Binomial(`n`,
`p`) average of the uniform model's, `Σ_s Bin(n, p)(s) · q(n, t, s) = q_p(t)`
with `q(n, t, s)` the fraction of `s`-sets missing `A` or missing `R` (§8;
`CliqueCoverMoment.lean`). Hence `P(pw(G_B) ≤ k) ≤ UB_B(k)` for every `k < n`.

**Lemma V2 (the monotone coupling).** For every `(B, ω)`, in both pad
orders: (i) `B ≤ Φ(B, ω) ≤ M⁺` entrywise; (ii) `G_B ⊆ G_M`, so every empty
pair of `G_M` is an empty pair of `G_B`, and `pw(G_B) ≤ pw(G_M)`; (iii) on
`E`, `Φ(B, ω) = B`.

**Theorem V3 (the first moment survives the pads).** Without the rejection,
for every `n`, `m`, `p`, `k < n` and both pad orders,

    P(pw(G_M) ≤ k) ≤ P(pw(G_B) ≤ k) ≤ UB_B(k),

and, every customer of `M` having a pattern, `P(MOSP(M) ≤ k + 1) ≤ UB_B(k)`.
In the patterns-first order the stronger form holds with the truncated
sizes, `P(pw(G_M) ≤ k) ≤ C · q̃_p(t)^m` with `q̃_p(t) = Σ_s Bin(n, p)(s) ·
q(n, t, max(s, 2)) ≤ q_p(t)`.

**Theorem V3′ (the quenched form).** Let `X_j = log q(n, t, s_j)` with
`s_j` i.i.d. `Bin(n, p)` (or `max(Bin(n, p), 2)` in the patterns-first
order), and `a_0 < a_1 < … < a_K` any grid with `a_0 ≤ min X`. Then

    P(pw(G_M) ≤ k) ≤ C e^{m a_0} + Σ_{i ≥ 1} min(1, C e^{m a_i}) · min(1, inf_{λ > 0} e^{−λ m a_{i−1}} (E e^{λ X})^m).

Both V3 and V3′ are valid, so the smaller is (`log_bound_best`).

**Lemma V4 (the repair map is not monotone).** There are `B ≤ B'` and `ω`
with `Φ(B, ω) ⊄ Φ(B', ω)`, `G_{Φ(B,ω)}` connected, `G_{Φ(B',ω)}`
disconnected and `pw(G_{Φ(B',ω)}) < pw(G_{Φ(B,ω)})`. So neither "accepted"
nor "`pw(G_M) ≤ k`" is a monotone event of the base entries at fixed `ω`,
and Harris's inequality does not apply to the pair. `M⁺` is monotone in `B`
at fixed `ω`, and so is `acc⁺`.

**Theorem V5 (the rejection).** For every `n`, `m`, `p`, `k < n` with
`P(acc) > 0`, in the fitted order:

- (i) trivial: `P(pw(G_M) ≤ k | acc) ≤ UB(k) / P(acc)`, `UB` any of V3, V3′;
  in the patterns-first order the same with that order's bounds and
  acceptance;
- (ii) Harris on the unconditional pad: `P(pw(G_M) ≤ k | acc) ≤ UB_B(k) ·
  P(acc⁺) / P(acc)`, with `P(acc) ≤ P(acc⁺) ≤ 1`;
- (iii) Harris on the no-repair event: `P(pw(G_M) ≤ k | acc) ≤ UB_B(k) +
  P(E^c | acc) ≤ UB_B(k) + P(E^c) / P(acc)`, with the closed form
  `P(E^c) ≤ n (1 − p)^m + m [(1 − p)^n + n p (1 − p)^{n−1}]`;
- (iv) closed form for the acceptance: `P(acc) ≥ P(G_B connected) ≥ 1 −
  Σ_{s=1}^{⌊n/2⌋} C(n, s) [(1 − p)^s + (1 − p)^{n−s} − (1 − p)^n]^m`, so (i)
  holds with this in place of the measured acceptance wherever the sum is
  below 1;
- (v) the generator as the paper states it (Bernoulli entries, rejection,
  no pads): `P(pw(G_B) ≤ k | G_B connected) ≤ P(pw(G_B) ≤ k) ≤ UB_B(k)`, no
  loss at all.

**Proposition V6 (monotone in the density).** `UB_B(k)` and the truncated
bound are non-increasing in `p`, and `P(pw(G_{M_p}) ≤ k) ≤ P(pw(G_{B_{p'}})
≤ k)` for `p ≥ p'` under the standard coupling of Bernoulli entries; so the
floors of V3 computed at `p = d / n` are valid for every density at or
above `d / n`, and not for a density below it.

### 10.3 Proofs

*V1.* Pattern `i` meets both sides iff it contains a customer of `A` and
one of `R`; with independent entries `P(misses A) = (1 − p)^a`, `P(misses
R) = (1 − p)^r`, `P(misses both) = (1 − p)^{a+r}`, and inclusion–exclusion
gives the avoid probability; the patterns are independent, so the pair is
empty with the product probability. A Bernoulli(`p`) row conditioned on its
size `s` is a uniform `s`-set, so the avoid probability is also
`Σ_s Bin(n, p)(s) q(n, t, s)`. The bound on `P(pw(G_B) ≤ k)` is the union
bound over the `C` pairs of the sizes `exists_empty_pair` forces
(`EmptyPair.lean`); it is the `CliqueCoverMoment.lean` argument with the
factor averaged over sizes.

*V2.* (i) Both pads only set entries to 1. The customer pad sets `(U_j, j)
∈ C(ω)`; the pattern pad on a row with at most one 1 sets the first one or
two customers of `σ_i` not already in the row, which lie in `{σ_i(1),
σ_i(2)} ⊆ C(ω)` (if the row's one customer is `σ_i(1)` the pad takes
`σ_i(2)`, otherwise `σ_i(1)`; an empty row takes both). (ii) An edge of
`G_B` is a pattern containing both ends, and `M ⊇ B` still contains it; a
pattern of `B` meeting both sides of a pair meets both sides in `M`, so a
pair no pattern of `M` crosses is crossed by no pattern of `B`; a path
decomposition of `G_M` is one of `G_B`. (iii) By the definition of `E`.

*V3.* By V2 (ii), `{pw(G_M) ≤ k} ⊆ {pw(G_B) ≤ k}`; by V1 the latter has
probability at most `UB_B(k)`; `MOSP = pw + 1` for an instance with a
requirement (`mospValue_eq_pathwidth_add_one`). Truncated form: after the
pattern pad applied to `B` alone, row `i` depends on `(B_i, σ_i)` only, so
the rows are independent; given `|B_i| = s ≥ 2` the row is `B_i`, uniform of
size `s`; given `s = 1` it is `{x, y}` with `x` uniform and `y` the first
element of `σ_i` other than `x`, a uniform 2-set; given `s = 0` it is
`{σ_i(1), σ_i(2)}`, a uniform 2-set. So the pattern-padded matrix *is* the
uniform model with independent sizes `max(s_i, 2)`, `s_i ~ Bin(n, p)`, its
empty-pair probability is `q̃_p(t)^m` exactly, and the customer pad then only
adds ones (V2 (i)). `q̃_p ≤ q_p` since `q(n, t, s)` is non-increasing in
`s`. (The row law is checked by a chi-square on 20,000 draws,
`test_pattern_pad_rows_are_uniform_sets_of_the_truncated_size`.) In the
fitted order the customer pad comes first and the pattern pad then acts on
rows that may already hold a padded customer, so the rows are neither
independent nor uniform of a known size, and only the Bernoulli form is
proved there.

*V3′.* Given the size vector, the patterns are independent uniform sets of
those sizes (the Bernoulli row given its size; the padded row by V3), so
the uniform-model union bound (`prob_coversOfPathwidthLe_le`) gives
`P(pw ≤ k | s) ≤ min(1, C e^{Σ_j X_j})`. Partition by the bin of
`(1/m) Σ_j X_j`: on `(a_{i−1}, a_i]` the conditional bound is at most
`min(1, C e^{m a_i})`, and the bin has probability at most `P(Σ_j X_j >
m a_{i−1}) ≤ inf_λ e^{−λ m a_{i−1}} E[e^{λ Σ X_j}] = inf_λ e^{−λ m
a_{i−1}} (E e^{λ X})^m` (Chernoff, the `X_j` i.i.d.); below `a_0` the
bound is `C e^{m a_0}` with probability at most 1. Sizes with `q = 0` (a
pattern too large to miss either side) have `X = −∞`; the implementation
drops them from the moment generating function, which can only enlarge
`E e^{λ X}` and the bound. Checked against the exact tail by enumeration of
size vectors (`test_quenched_tail_is_a_chernoff_bound_on_the_size_sum`) and
against the exact `P(pw(G_B) ≤ k)` over all `2^{15}` base matrices at
`3 × 5` (`test_quenched_bound_is_above_the_exact_probability_by_enumeration`).

*V4.* `n = 5`, `m = 3`: `B` has patterns `{3, 4}`, `∅`, `{3, 4}`, so
customers 0, 1, 2 are empty. With `U ≡ 0` and `σ_i = (3, 4, 0, 1, 2)` the
customer pad makes pattern 0 `= {0, 1, 2, 3, 4}` and the pattern pad makes
pattern 1 `= {3, 4}`; `G_M = K_5`, connected, pathwidth 4. `B' = B + (1, 1)
+ (1, 2)` has pattern 1 `= {1, 2}`; only customer 0 is empty and joins
pattern 0 `= {0, 3, 4}`; no pattern pad fires; `G_{M'}` has the components
`{0, 3, 4}` and `{1, 2}`, disconnected, pathwidth 2, and `M' ⊉ M` (the
entries `(0, 1)`, `(0, 2)` are gone). `M⁺ = B ∨ C(ω)` is monotone because
`C(ω)` does not depend on `B`, and connectivity is increasing in the edge
set. (`test_the_repair_map_is_not_monotone_in_the_base`; the `coupling`
stage counts how often one added entry makes a pad vanish, loses the
acceptance or lowers `pw(G_M)`.)

*V5.* (i) `P(X ≤ k | acc) = P(X ≤ k, acc) / P(acc) ≤ P(X ≤ k) / P(acc)` with
V3 or V3′. (ii) Fix `ω`. On the product space of the base entries,
`D = {pw(G_B) ≤ k}` is decreasing (V2 (ii) applied to `B ≤ B'`) and `acc⁺(·,
ω)` is increasing (V4); Harris's inequality for product measures gives
`P(D ∩ acc⁺ | ω) ≤ P(D) P(acc⁺ | ω)`, `D` not depending on `ω`; integrate
over `ω`: `P(D ∩ acc⁺) ≤ P(D) P(acc⁺)`. Since `{pw(G_M) ≤ k} ∩ acc ⊆ D ∩
acc⁺` (V2 (i), (ii)), `P(pw(G_M) ≤ k, acc) ≤ UB_B(k) P(acc⁺)`; divide by
`P(acc)`. (iii) `{pw(G_M) ≤ k} ∩ acc ⊆ (D ∩ {G_B connected} ∩ E) ∪ (E^c ∩
acc)`, because on `E` the matrix is `B` (V2 (iii)). `E` and `{G_B
connected}` are increasing in `B` and `D` decreasing, so Harris gives `P(D ∩
conn ∩ E) ≤ P(D) P(conn ∩ E) ≤ P(D) P(acc)`, the last since `conn ∩ E ⊆
acc`. Hence `P(pw(G_M) ≤ k, acc) ≤ UB_B(k) P(acc) + P(E^c ∩ acc)`, and
`P(E^c)` is at most the union bound over the `n` customers and `m`
patterns. (iv) `acc ⊇ {G_B connected}` by V2 (ii); a disconnected graph has
a component `S` with `1 ≤ |S| ≤ n/2`, which no pattern crosses, and V1 with
`(A, R) = (S, S^c)` gives each term. (v) With no pads `acc = {G_B
connected}` is increasing and `D` decreasing on the product space: Harris.
*Why (ii) does not help in practice:* the unconditional pads give every
customer a pattern and every pattern two customers, and `P(acc⁺)` is 1.000
in every class and at `n = 8`, so (ii) is (i).

*V6.* `q_p(t)` and `q(n, t, s)` are non-increasing in `p` and `s`; couple
`B_{p'} ≤ B_p` entrywise and apply V2 (ii) to `B_{p'} ⊆ B_p ⊆ M_p`.

### 10.4 The checks (`check.log`)

- **exact.** The identity `Σ_s Bin(n, p)(s) q(n, t, s) = q_p(t)` holds
  exactly in rationals on 205 cases (`n ≤ 12`, five values of `p`, every
  `t`), as does the truncated average against `lq_truncated` and
  `q̃_p ≤ q_p`. Full enumeration of every base matrix at `2 × 6` and
  `3 × 4` with `p = 1/3`: the pair probability equals the product formula
  on all 126 + 16 pairs `(A, R)` of the forced sizes; `P(G_B disconnected)`
  (0.978, 0.859) is below the cut bound; `P(a repair fires)` (0.973, 0.952)
  is below the repair bound (both bounds are vacuous at these sizes, which
  is what a union bound does at `p = 1/3`).
- **law.** Five statistics (ones, row variance, share of size-2 patterns,
  share of one-pattern customers, acceptance) on 4,000 draws per class and
  implementation, four classes: all within 2.1 standard errors.
- **coupling** (`n = m = 8`, 10,000 draws per configuration, `d ∈ {2, 4}`,
  both orders): `M ≥ B` in 10,000 of 10,000, `M ≤ M⁺` in 10,000, every one
  of the 6,050 ordered disjoint nonempty pairs that is empty in `G_M` is
  empty in `G_B` in 10,000, `pw(G_B) ≤ pw(G_M)` in 10,000 — in all four
  configurations. Over every single-entry increase of the base on the first
  2,000 draws: at `d = 2`, fitted order, 95,855 increases, a pad vanished in
  38,834 (40.5%), the acceptance was lost in 688 (0.72%), `pw(G_M)` fell in
  3,342 (3.5%); patterns-first 95,837 / 38,575 / 717 / 2,837; at `d = 4`
  64,043 / 3,785 / 0 / 121 and 64,362 / 3,980 / 1 / 121. `M⁺` was
  non-monotone in 0, lost its connectivity in 0; `G_B` lost its
  connectivity in 0 and `pw(G_B)` fell in 0 (the base's pathwidth on the
  first 300 draws). Monte Carlo of `P(pw(G_M) ≤ k | acc)` against the three
  rigorous forms: 0 violations at 3 standard errors over 8 values of `k` in
  each configuration (the bounds are above 1 at `n = 8`, so this checks
  only that nothing is inverted). Measured direction: `P(pw(G_M) ≤ k | acc)
  ≤ P(pw(G_B) ≤ k)` at 8 of 8 `k` in each configuration — the pads and the
  rejection lower the probability, as §2.1 of the generator report found at
  30–50; a measurement.
- **classes.** The event rates below, 2,000 draws per class and order,
  continued to 300 acceptances up to 60,000 draws for the sparse ones
  (`(100, 50, 2)`: 291 accepted of 60,000 in the fitted order, 300 of
  15,725 patterns-first).

### 10.5 The numerical consequence

The columns of the main table (`tables.md`, in full in §10.9): the
measured-model floors are `finite_bound_cs.log`'s (per file from the
realised sizes, averaged over the five files); "B" is the Bernoulli
form at `p = d / n` (fitted order), "T" the truncated form (patterns-first
order); "base" is V3 without the rejection, "triv" V5 (i) at the measured
acceptance (in brackets: at the Wilson 95% lower acceptance), "Harris+" V5
(ii), "Harris_E" V5 (iii), "closed" V5 (iv) where the cut bound is below 1,
"best" the smaller of V3 and V3′ (with and without the rejection).

1. **The acceptance.** Fitted order, measured: 0.87, 0.83, 0.80, 0.70,
   0.65, 0.56 on the square `d = 2` classes from 30 to 125 customers;
   0.998 at `(50, 100, 2)`; **0.0049** at `(100, 50, 2)` (the fit log's
   0.0046); 0.77 at `(100, 50, 4)`; 0.99–1.00 on the square `d = 4`
   classes; ≥ 0.99 at `d ≥ 6`. Patterns-first: within 0.04 of these, except
   `(100, 50, 2)` at 0.019. `P(acc⁺) = 1.000` in every class, so V5 (ii)
   coincides with V5 (i). `P(no repair)` is 0.000 at `d = 2–4` in every
   class, 0.12–0.71 at `d = 6`, 0.19–0.96 at `d = 8`, 0.40–1.00 at `d = 10`,
   so V5 (iii)'s additive term `P(E^c)/P(acc)` exceeds 0.01 everywhere
   except `(30, 30, 10)` and `(40, 40, 10)`: that form keeps a 0.01 floor
   on two classes of 40. The closed-form acceptance V5 (iv) is non-vacuous
   at `d ≥ 4` for `n ≤ 40`, at `d ≥ 6` on the square classes to 125 and at
   `d = 10` on `100 × 50`; where it is, it gives the same floor as the
   measured acceptance except at `(100, 50, 10)` (47 against 49).
2. **The cost of the rejection is at most one stack at `d ≥ 4` and zero
   on most classes**: the trivial and base columns agree on every class
   with `P(acc) ≥ 0.99`, and at `d = 2` the factor `1/P(acc) ≤ 1.9` moves
   no 0.01 floor (the floors there are already trivial or small). Even
   `(100, 50, 2)`'s factor of 204 costs nothing, because the floor is
   trivial before it: at the nominal sizes that class has excess `r (c − 1)
   = 0.5` (truncated: 0.65), *below the threshold* `e = 1` of §2, so no
   first-moment floor exists for it at all; the measured floor of 4.6 is
   entirely the pads' doing (the files have 1.74 × `d m` ones).
3. **The price of rigour is the pads at `d = 2` and the annealing at
   `d ≥ 4`.** The three-column decomposition (annealed rigorous → the
   per-instance floor at *simulated* binomial sizes, a typical-instance
   diagnostic and not a theorem → the realised sizes) reads, at the 0.01
   level: `(125, 125, 2)`: 1 → 3.4 → 13.6 in the Bernoulli form and 6 →
   10.4 → 13.6 truncated; `(125, 125, 4)`: 26 → 39.8 → 42.4 (T: 30 → 40.9);
   `(125, 125, 6)`: 58 → 68.2 → 69.6; `(100, 50, 6)`: 15 → 27.6 → 31.8;
   `(50, 50, 4)`: 11 → 17.1 → 19.0. So at `d ≥ 4` the typical instance of
   the *same* size law is within 1–4 stacks of the measured floor and the
   rigorous bound is 2–13 below it: the rigorous bound controls the
   expectation over size vectors, which the rare sparse draws dominate.
   At `d = 2` the typical binomial instance is itself far below the
   measured floor (3.4 against 13.6) and the truncated sizes recover most
   of the difference (10.4): there the pads are the price.
4. **The quenched form V3′ buys back part of the annealing**, at the 0.01
   level 2–4 stacks on the large dense classes — `(125, 125, 4)` 26 → 30
   (T 30 → 32), `(125, 125, 6)` 58 → 60 (62), `(100, 100, 4)` 21 → 25,
   `(100, 50, 6)` 15 → 19, `(100, 50, 4)` 1 → 3 — and nothing on the small
   or sparse ones; at the `< 1` level it is worth 4–10 stacks (`(125, 125,
   4)` 28 → 36 (38), `(100, 50, 6)` 17 → 23). The Chernoff tail on 125
   i.i.d. sizes is what it costs: the rest of the distance to the typical
   instance (10 stacks at `(125, 125, 4)`) is the tail's price at
   confidence 0.01.
5. **Where the two differ by more than one stack: 35 of 40 classes in the
   Bernoulli form, 34 in the truncated form** (best form, with the
   rejection; the table in §10.10). The five that agree are `(30, 30, 8)`,
   `(30, 30, 10)`, `(40, 40, 10)`, `(50, 100, 8)`, `(50, 100, 10)` (the
   truncated form adds `(30, 30, 6)`), where the pads rarely fire and the
   sizes concentrate. At `(30, 30, 10)` the
   rigorous floor (25) is *above* the measured one (24.6): the files are
   1.5% sparser than `d m` ones there, and V6 says the rigorous floor at
   `d / n` is a statement for densities at or above `d / n`.
6. **Sensitivity to the density constant.** At `1.10 d / n` the annealed
   floors rise by 2–6 stacks on the large classes (`(125, 125, 4)` 26 → 32,
   `(125, 125, 6)` 58 → 66, `(100, 50, 6)` 15 → 21). The unresolved constant
   therefore moves the rigorous floor by about as much as the quenched form
   does; by V6 the floors quoted are valid for the fitted generator at any
   density at or above `d / n`, which is what the fit supports at `d ≤ 4`
   and what the files do not quite support at `(30, 30, 10)`.
7. **No certified optimum lies below any rigorous floor** (0 of 200 against
   every column, best forms included); the smallest margin is one stack
   (`(30, 30, 10)`, minimum optimum 26 against the floor 25).

### 10.6 Findings

1. **The first-moment floor with pre-repair sizes is a theorem for the
   padded generator** (V3), by a coupling in which the pads only add ones,
   and with the truncated sizes `max(s, 2)` in the patterns-first order,
   where the pattern pad produces exactly the uniform model of those sizes.
2. **The rejection cannot be handled by Harris–FKG on the fitted
   generator**, because its acceptance is not an increasing event of the
   base entries (V4: 0.7% of single-entry additions at `d = 2` lose the
   acceptance, 3.5% lower the padded pathwidth), and the item ends, as its
   kill criterion allows, with the `1 / P(accepted)` form and the measured
   acceptance. The two Harris forms that are rigorous add nothing in
   practice: the unconditional pad is always connected, and the no-repair
   event is rare below `d = 10`. Harris does apply to the generator as the
   paper describes it, with no loss, and that generator cannot have
   produced the sparse classes (`REPORT_generator.md` §1.3).
3. **What is proved is far from what is measured** on 34–35 of 40 classes,
   trivial at `d = 2` in the Bernoulli form, and the gap has two causes
   that the decomposition separates: the pads at `d = 2` (40% of Bernoulli
   patterns have at most one customer and cannot cross a pair), the
   annealing at `d ≥ 4` (the rigorous bound is on the expectation over
   size vectors). The quenched form V3′ recovers 2–4 stacks of the latter
   at the 0.01 level and 4–10 at the `< 1` level.
4. **The realised-size inequality stays measured.** The sizes in the
   files are the padded ones; conditioning on them does not give uniform,
   independent patterns in either order (the customer pad concentrates its
   ones on empty customers), and no coupling here reaches it. What the
   measurement of §2.1 showed — the ratio below 1 at every reachable `t` —
   is consistent with V2's direction and is not implied by it.
5. **The `(100, 50, 2)` class has no first-moment floor at its nominal
   sizes** (excess 0.5, below the threshold); its measured floor of 4.6 is
   the pads' 74% extra ones. This is the clearest instance of the
   generator's repairs changing the regime of a class.

### 10.7 The paper's sentence

Applied to `paper1/latex/sec9e_appendix_random.tex` (the last paragraph of
"The benchmark generator"), replacing "That is a measurement, not a proof;
a proof would couple the padded instance to the unpadded one, which has
only more edges": the inequality with the pre-repair sizes is proved by
the coupling (the Bernoulli form in both pad orders, the truncated form in
the patterns-first order, a Chernoff quenched form); the rejection is not
an increasing event of the entries, so Harris does not apply and the
rejection costs at most `1 / P(accepted)`, measured per class; the proved
floors lie below the table's by the stated amounts and are trivial at
`d = 2`; the realised-size statement remains measured. The PDF rebuilds
(66 pages, no undefined references).

### 10.8 Kill verdict

**The fallback of the kill criterion is the result.** V5 (ii)–(v) make the
rejection rigorous only where monotonicity holds (the unconditional pad,
the no-repair event, the base graph's own connectivity, the paper's
generator), and none of those is the fitted generator's acceptance; for
that, the item ends with the `1 / P(accepted)` form and the measured
acceptance, as the criterion says is acceptable; that factor moves no 0.01
floor on any of the 40 classes. No certified value is
wrong, no theorem is false; one published sentence of ours is replaced by
what is proved, as item 12 planned, and that is not a drift.

### 10.9 What this does not claim

- **The inequality with the realised sizes** of the files, under either
  pad order. It is measured (§2.1–2.2 of the generator report; 0 of 200
  and 0 of 7,200 violations) and not proved.
- **Anything about Chu & Stuckey's actual code.** The theorems are about
  the fitted family at `p = d / n` (and, by V6, any density at or above
  it); the pad order and the density constant are unresolved
  (`REPORT_generator.md` §4.1).
- **That the rejection helps.** The measured direction (the conditional
  probability below the unconditional one at every `k`, at `n = 8` and at
  30–50) is a measurement; what is proved is that it costs at most
  `1 / P(accepted)`.
- **Tightness of any form.** The quenched form's Chernoff tail is paid at
  the stated confidence and leaves 10 stacks to the typical instance at
  `(125, 125, 4)`; a sharper tail (Bernstein, or the exact distribution of
  the size sum, which is computable) would recover more and was not
  attempted.
- **An asymptotic constant** for the padded generator. The threshold and
  `β*` of §2 are quenched statements at the empirical sizes; the Bernoulli
  annealed threshold is `d > 2.46` at `μ = 1` (`REPORT_generator.md` §3.1),
  and nothing here changes either.
- **That `P(accepted)` is known.** It is measured with 2,000–60,000 draws
  per class (Wilson intervals in `classes.csv`; the bracketed floors use
  the lower limit and never differ), and in closed form only where V5 (iv)
  is non-vacuous.

### 10.10 Tables, in full (`reports/scratch/validity/tables.md`)

