### 10.1 The generator, with its randomness made explicit

The fitted generator (`REPORT_generator.md` §1.3, `gen_candidates.py`
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
not known; neither is the density constant (§1.4 of the generator report:
`p = (1.05–1.10) d / n` at `d ≤ 4`).

**The auxiliary randomness.** Let `ω = (U, σ)` be independent of `B`: `U_j`
a uniform pattern index for every customer `j`, `σ_i` a uniform permutation
of the customers for every pattern `i`. Define `Φ(B, ω)` as: step 2 adds
`(U_j, j)` for every empty column `j`; step 3 adds, for every row `i` with
fewer than two ones, the first ones it lacks in the order `σ_i`. Since a
uniform choice among the candidates is the first candidate of a uniform
permutation restricted to them, `Φ(B, ω)` has exactly the generator's law
(`pad_with_aux`; the `law` stage of the check compares five statistics on
4,000 draws per class, all within 2.1 standard errors). Write `M = Φ(B, ω)`,
`M⁺ = B ∨ C(ω)` with `C(ω) = {(U_j, j) : all j} ∪ {(i, σ_i(1)), (i, σ_i(2)) :
all i}` (every pad applied whether needed or not; `unconditional_pad`), and
`E = {every column of B nonempty, every row of B has ≥ 2 ones}` (no repair
fires). `G_X` is the MOSP graph of a matrix `X` (customers adjacent iff they
share a pattern), `acc = {G_M connected}`, `acc⁺ = {G_{M⁺} connected}`, and
`UB_B(k) = C(n, t) C(n − t, t − 1) q_p(t)^m` with `t = ⌈(n − k)/2⌉` and
`q_p(t) = (1 − p)^t + (1 − p)^{t−1} − (1 − p)^{2t−1}`.

### 10.2 Statements

**Lemma V1 (the pre-repair bound, exact).** For disjoint customer sets
`A`, `R` with `|A| = a`, `|R| = r`,

    P((A, R) is an empty pair of G_B) = [(1 − p)^a + (1 − p)^r − (1 − p)^{a+r}]^m,

a product of independent patterns; and this is the Binomial(`n`, `p`)
average of the uniform model's factor, `Σ_s Bin(n, p)(s) · q(n, t, s) =
q_p(t)` with `q(n, t, s)` the fraction of `s`-sets missing `A` or missing
`R` (§8, `CliqueCoverMoment.lean`). Hence `P(pw(G_B) ≤ k) ≤ UB_B(k)` for
every `k < n`.

**Lemma V2 (the monotone coupling).** For every `(B, ω)`: (i) `B ≤ Φ(B, ω)
≤ M⁺` entrywise, in both pad orders; (ii) `G_B ⊆ G_M`, so every empty pair
of `G_M` is an empty pair of `G_B`, and `pw(G_B) ≤ pw(G_M)`; (iii) on `E`,
`Φ(B, ω) = B`.

**Theorem V3 (the first moment survives the pads).** Without the rejection,
for every `n`, `m`, `p` and `k < n`, in both pad orders,

    P(pw(G_M) ≤ k) ≤ P(pw(G_B) ≤ k) ≤ UB_B(k),

and since every customer of `M` has a pattern, `P(MOSP(M) ≤ k + 1) ≤ UB_B(k)`.
In the patterns-first order the stronger form holds with the truncated
sizes: `P(pw(G_M) ≤ k) ≤ C(n, t) C(n − t, t − 1) q̃_p(t)^m` with
`q̃_p(t) = Σ_s Bin(n, p)(s) · q(n, t, max(s, 2)) ≤ q_p(t)`.

**Lemma V4 (the repair map is not monotone).** There are `B ≤ B'` and `ω`
with `Φ(B, ω) ⊄ Φ(B', ω)`, `G_{Φ(B,ω)}` connected and `G_{Φ(B',ω)}`
disconnected, and `pw(G_{Φ(B',ω)}) < pw(G_{Φ(B,ω)})`. So neither "accepted"
nor "`pw(G_M) ≤ k`" is a monotone event of the base entries at fixed `ω`,
and Harris's inequality does not apply to the pair directly. `M⁺` is
monotone in `B` at fixed `ω`, and so is `acc⁺`.

**Theorem V5 (the rejection).** For every `n`, `m`, `p`, `k < n` with
`P(acc) > 0`, in the fitted order:

- (i) trivial: `P(pw(G_M) ≤ k | acc) ≤ UB_B(k) / P(acc)`; in the
  patterns-first order the same with the truncated bound and that order's
  `P(acc)`;
- (ii) Harris on the unconditional pad: `P(pw(G_M) ≤ k | acc) ≤ UB_B(k) ·
  P(acc⁺) / P(acc)`, with `P(acc) ≤ P(acc⁺) ≤ 1`;
- (iii) Harris on the no-repair event: `P(pw(G_M) ≤ k | acc) ≤ UB_B(k) +
  P(E^c | acc) ≤ UB_B(k) + P(E^c) / P(acc)`, with the closed form
  `P(E^c) ≤ n (1 − p)^m + m [(1 − p)^n + n p (1 − p)^{n−1}]`;
- (iv) closed form for the acceptance: `P(acc) ≥ P(G_B connected) ≥ 1 −
  Σ_{s=1}^{⌊n/2⌋} C(n, s) [(1 − p)^s + (1 − p)^{n−s} − (1 − p)^n]^m`, so (i)
  holds with that in place of the measured acceptance wherever the sum is
  below 1;
- (v) the generator as the paper states it (Bernoulli entries, rejection,
  no pads): `P(pw(G_B) ≤ k | G_B connected) ≤ P(pw(G_B) ≤ k) ≤ UB_B(k)`, with
  no loss at all.

**Proposition V6 (monotone in the density).** `UB_B(k)` and the truncated
bound are decreasing in `p`, and `P(pw(G_{M_p}) ≤ k) ≤ P(pw(G_{B_{p'}}) ≤ k)`
for `p ≥ p'` under the standard coupling of Bernoulli entries; so the
floors of Theorem V3 computed at `p = d / n` are valid for every density at
or above `d / n`, and not for a density below it.

### 10.3 Proofs

*V1.* Pattern `i` meets both sides iff it contains a customer of `A` and a
customer of `R`; with independent entries, `P(misses A) = (1 − p)^a`,
`P(misses R) = (1 − p)^r`, `P(misses both) = (1 − p)^{a+r}`, and
inclusion–exclusion gives the avoid probability. The patterns are
independent, so the pair is empty with the product probability. A
Bernoulli(`p`) row conditioned on its size `s` is a uniform `s`-set, so the
avoid probability is also `Σ_s Bin(n, p)(s) q(n, t, s)`; the identity is
checked exactly in rationals (205 cases, `n ≤ 12`) and the product against
full enumeration of every base matrix at `2 × 6` and `3 × 4`. The bound on
`P(pw(G_B) ≤ k)` is the union bound over the `C(n, t) C(n − t, t − 1)` pairs
of the sizes `exists_empty_pair` forces (`EmptyPair.lean`); it is the
`CliqueCoverMoment.lean` argument with the factor averaged over sizes.

*V2.* (i) Both pads only set entries to 1; the customer pad sets `(U_j, j)
∈ C(ω)`; the pattern pad on a row with at most one 1 sets the first one or
two customers of `σ_i` not already in the row, which lie in
`{σ_i(1), σ_i(2)} ⊆ C(ω)`. (ii) An edge of `G_B` is a pattern containing
both ends, which `M ⊇ B` still contains; a pattern of `M` meeting both sides
of a pair meets both in… no: a pattern of `B` meeting both sides is a pattern
of `M` meeting both sides, so a pair with no such pattern in `M` has none in
`B`; pathwidth is monotone under subgraphs on the same vertex set (a path
decomposition of `G_M` is one of `G_B`). (iii) By definition of `E`.

*V3.* By V2 (ii), `{pw(G_M) ≤ k} ⊆ {pw(G_B) ≤ k}`; by V1 the latter has
probability at most `UB_B(k)`; `MOSP = pw + 1` for an instance with a
requirement (`mospValue_eq_pathwidth_add_one`). For the truncated form:
after the pattern pad applied to `B` alone, row `i` depends on `(B_i, σ_i)`
only, so the rows are independent; given `|B_i| = s ≥ 2` the row is `B_i`,
uniform of size `s`; given `s = 1` it is `{x, y}` with `x` uniform and `y`
the first of `σ_i` other than `x`, a uniform 2-set; given `s = 0` it is
`{σ_i(1), σ_i(2)}`, a uniform 2-set. So the pattern-padded matrix is the
uniform model with independent sizes `max(s_i, 2)`, `s_i ~ Bin(n, p)`, its
empty-pair probability is `q̃_p(t)^m`, and the customer pad then only adds
ones (V2 (i) again). `q̃_p ≤ q_p` because `q(n, t, s)` is non-increasing in
`s`. (The lemma on the row law is checked by a chi-square on 20,000 draws in
`tests/test_first_moment.py`.) In the fitted order the customer pad comes
first and the pattern pad acts on rows that may already contain a padded
customer, so the rows are neither independent nor uniform of a known size,
and only the Bernoulli form is proved there.

*V4.* `n = 5`, `m = 3`: `B` has patterns `{3, 4}`, `∅`, `{3, 4}`, so
customers 1 and 2 are empty; with `U ≡ 0` and `σ_i = (3, 4, 0, 1, 2)` the
customer pad gives pattern 0 = `{1, 2, 3, 4}`, the pattern pad gives pattern
1 = `{3, 4}`, and `G_M` is connected (customer 0 joins pattern 0 through
`U_0 = 0`). `B' = B + (1, 1) + (1, 2)` has pattern 1 = `{1, 2}`, every
customer and every row satisfied, so no pad fires and `G_{B'}` has the two
components `{1, 2}` and `{0, 3, 4}` — wait, customer 0 is empty in `B'`: it
joins pattern 0 = `{0, 3, 4}`; the components are `{1, 2}` and `{0, 3, 4}`,
disconnected, and `pw` falls from 3 to 1. `M⁺ = B ∨ C(ω)` is monotone
because `C(ω)` does not depend on `B`; connectivity is increasing in the
edge set. (`tests/test_first_moment.py::test_the_repair_map_is_not_monotone_in_the_base`;
the `coupling` stage counts how often a single added entry makes a pad
vanish, loses acceptance or lowers `pw(G_M)`.)

*V5.* (i) `P(X ≤ k | acc) = P(X ≤ k, acc) / P(acc) ≤ P(X ≤ k) / P(acc)` with
V3. (ii) Fix `ω`. On the product space of the base entries, `D = {pw(G_B) ≤
k}` is decreasing (V2 (ii) applied to `B ≤ B'`) and `acc⁺(·, ω)` is
increasing (V4); Harris's inequality for product measures gives
`P(D ∩ acc⁺ | ω) ≤ P(D) P(acc⁺ | ω)` (`D` does not depend on `ω`).
Integrating over `ω`, `P(D ∩ acc⁺) ≤ P(D) P(acc⁺)`. Since `{pw(G_M) ≤ k} ∩
acc ⊆ D ∩ acc⁺` (V2 (i), (ii)), `P(pw(G_M) ≤ k, acc) ≤ UB_B(k) P(acc⁺)`;
divide by `P(acc)`. (iii) `{pw(G_M) ≤ k} ∩ acc ⊆ (D ∩ {G_B connected} ∩ E)
∪ (E^c ∩ acc)`, because on `E` the matrix is `B` (V2 (iii)). `E` and
`{G_B connected}` are increasing in `B`, `D` decreasing, so Harris gives
`P(D ∩ conn ∩ E) ≤ P(D) P(conn ∩ E) ≤ P(D) P(acc)`, the last since `conn ∩
E ⊆ acc`. Hence `P(pw(G_M) ≤ k, acc) ≤ UB_B(k) P(acc) + P(E^c ∩ acc)`, and
`P(E^c) ≤` the union bound over the `n` customers and `m` patterns. (iv)
`acc ⊇ {G_B connected}` by V2 (ii); a disconnected graph has a component
`S` with `1 ≤ |S| ≤ n/2`, across which no pattern reaches, and V1's formula
with `(A, R) = (S, S^c)` gives each term. (v) With no pads, `acc = {G_B
connected}` is increasing and `D` decreasing on the product space: Harris.

*V6.* `q_p(t)` and `q(n, t, s)` are non-increasing in `p` and `s`; couple
`B_{p'} ≤ B_p` entrywise and apply V2 (ii) to the pair `B_{p'} ⊆ B_p ⊆ M_p`.
