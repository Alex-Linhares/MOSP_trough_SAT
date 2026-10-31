# The first-moment lower bound on the pathwidth of random graphs: the asymptotic half, on paper

*2026-10-31. ANALYST, with the CHECKER attacking every inequality (`reports/scratch/first_moment/gossip.md`).
Scripts: `reports/scratch/first_moment/beta_star.py`, `finite_bound.py`; logs beside them.*

This document takes the finite, deterministic inequality proved in Lean
(`lean/MOSPFormalization/FirstMoment.lean`, `weightedSum_graphsOfPathwidthLe_le`) and
does the analysis the survey (`reports/random_graph_pathwidth_survey.md` §1.4, §3) left
on paper: the exponential decay below `β*(c)·n` in the sparse case, the threshold
`c > 4 ln 2`, the asymptotics of `β*(c)`, the `n − (4 + ε) log_b n` bound in the dense
case, the numerical values, and the finite inequality against the pilot data.
Everything starts from one inequality and uses nothing probabilistic beyond it.

**The starting point** (Lean, `weightedSum_graphsOfPathwidthLe_le`; `k < n`, `0 ≤ p ≤ 1`):

```
P(pw(G(n, p)) ≤ k) ≤ C(n, t) · C(n − t, t − 1) · (1 − p)^(t(t − 1)),     t = (n − k + 1) div 2 = ⌈(n − k)/2⌉.   (0)
```

The factor `C(n, t)·C(n − t, t − 1)` is the trinomial coefficient
`n! / (t! (t − 1)! (n − 2t + 1)!)`: the number of ordered pairs `(A, R)` of disjoint
vertex sets with `|A| = t`, `|R| = t − 1`, which is what the Lean proof counts
(`card_emptyPairIndices`) before the union bound. **The entropy term below comes from
bounding this trinomial by one application of the multinomial entropy bound, not from
two binomial bounds** (the two routes give the same number, see Remark 2.1).

Notation: `ln` is the natural logarithm; `φ(x) = −x ln x` with `φ(0) = 0`;
`H(x, y, z) = φ(x) + φ(y) + φ(z)` for `x + y + z = 1` (the trinomial entropy in nats);
`a = (1 − β)/2`; and

```
δ(β, c) = c a² − H(a, a, 1 − 2a) = c a² + 2a ln a + (1 − 2a) ln(1 − 2a).
```

---

## 1. Statements

**Theorem A (sparse case, finite form).** Let `c > 0` and `0 < β < 1`, `a = (1 − β)/2`.
For every integer `n ≥ max(3, c)`,

```
P( pw(G(n, c/n)) ≤ βn ) ≤ exp( −δ(β, c)·n + 3 ln n + c·a ) ≤ e^(c/2) · n³ · e^(−δ(β, c)·n).      (A)
```

In particular, if `δ(β, c) > 0` the probability is exponentially small in `n`.

**Theorem A′ (the admissible region).** For `c ≤ 4 ln 2` there is no `β ∈ (0, 1)` with
`δ(β, c) > 0`. For `c > 4 ln 2` the function `a ↦ H(a, a, 1 − 2a) − c a²` has exactly one
zero `a*(c)` in `(0, 1/2)`, and `δ(β, c) > 0` holds exactly for `0 < β < β*(c) := 1 − 2a*(c)`.
Hence, writing `β*(c) = 0` for `c ≤ 4 ln 2`: **`pw(G(n, c/n)) ≥ βn` with probability
`1 − O(n³ e^(−δn))` for every `β < β*(c)`, and `β*(c) > 0` if and only if `c > 4 ln 2 ≈ 2.7726`.**
`β*(c)` is the root in `(0, 1)` of

```
−(1 − β) ln((1 − β)/2) − β ln β = c (1 − β)² / 4.
```

*The threshold `4 ln 2` is a property of the method, not of pathwidth* (CHECKER, gossip
05:20): it is the first-moment threshold for an edge-free balanced bipartition
(`C(n, n/2) ≈ 2^n` partitions, each empty with probability `e^(−cn/4)`), and the pathwidth
of `G(n, c/n)` is linear for every `c > 1` (Lee–Lee–Oum 2012 via treewidth), with the pilot's
slope `0.040` already at `c = 2`. Below `4 ln 2` the first moment says nothing; it is not
that nothing is true.

**Theorem A″ (asymptotics of the threshold).** For every `c ≥ 14`,

```
(4 ln c − 4 ln ln c − 4 ln 2) / c  <  1 − β*(c)  <  (4 ln c − 4 ln ln c + 4 ln 2 + 4) / c,
```

so `1 − β*(c) ~ 4 ln c / c` as `c → ∞`; more precisely
`1 − β*(c) = (4 ln c − 4 ln ln c + 4 − 4 ln 2 + o(1)) / c`, the `o(1)` being `O(ln ln c / ln c)`.
The survey's leading term `4 ln c / c` is correct; the second-order term `−4 ln ln c / c`
is new here and matters numerically up to very large `c` (§3).

**Theorem B (dense case).** Fix `0 < p < 1`, `b = 1/(1 − p)`, `ε > 0`. For every `n ≥ b^(4/ε)`
with `(4 + ε) log_b n ≤ n`,

```
P( pw(G(n, p)) ≤ n − (4 + ε) log_b n ) ≤ n^(−1) · exp( −(ε / (2 ln b)) · ln² n ) = n^(−1 − (ε/2) log_b n).
```

In particular `n − pw(G(n, p)) ≤ (4 + o(1)) log_b n` with probability `1 − n^(−ω(1))`.

All four are proved in §2. Nothing in them uses anything beyond (0) and elementary
inequalities, each of which is either standard with a reference or proved below.

---

## 2. Proofs

### 2.1 Four lemmas

**Lemma 1 (multinomial entropy bound).** For nonnegative integers `i + j + l = n`,

```
n! / (i! j! l!) ≤ exp( n · H(i/n, j/n, l/n) ).
```

*Reference.* This is the "method of types" bound `|T(P)| ≤ 2^(n H(P))`, Cover & Thomas,
*Elements of Information Theory*, 2nd ed., Theorem 11.1.3, for a type on three symbols;
its binomial case `C(n, k) ≤ (n/k)^k (n/(n − k))^(n − k) = exp(n h(k/n))` is the standard
entropy bound on binomials (same theorem, two symbols).

*Proof.* By the multinomial theorem, for `x, y, z ≥ 0` with `x + y + z = 1`,
`1 = (x + y + z)^n ≥ (n! / (i! j! l!)) x^i y^j z^l`, every other term being nonnegative.
Put `x = i/n`, `y = j/n`, `z = l/n`; then `x^i = exp(i ln(i/n)) = exp(−n φ(i/n))` (with `0^0 = 1`
matching `φ(0) = 0`), and likewise for `y, z`, so
`n!/(i! j! l!) ≤ x^(−i) y^(−j) z^(−l) = exp(n(φ(i/n) + φ(j/n) + φ(l/n)))`. ∎

**Remark 2.1 (which form).** I apply Lemma 1 once, to the trinomial with
`(i, j, l) = (t, t − 1, n − 2t + 1)`. Bounding the two binomials separately,
`C(n, t) ≤ e^(n h(t/n))` and `C(n − t, t − 1) ≤ e^((n − t) h((t − 1)/(n − t)))`, gives
*exactly the same* right-hand side, by the chain rule of entropy
`n h(u) + (n − t) h((t − 1)/(n − t)) = n H(u, v, w)` for `u = t/n`, `v = (t − 1)/n`, `w = 1 − u − v`
(a two-line computation: `(n − t) h(v/(1 − u)) = n[φ(v) + φ(w) − φ(1 − u)]` and
`n h(u) = n[φ(u) + φ(1 − u)]`). So whichever route a formalisation takes, the exponent is
`n H(t/n, (t − 1)/n, (n − 2t + 1)/n)`.

**Lemma 2.** For `0 ≤ p ≤ 1` and every integer `m ≥ 0`, `(1 − p)^m ≤ exp(−p m)`.

*Proof.* `1 − p ≤ e^(−p)` (the tangent line of `e^(−p)` at `0`, convexity), both sides in
`[0, 1]`, raise to the `m`-th power. ∎

**Lemma 3 (shift lemma for `φ`).** For `0 ≤ x, y ≤ 1` with `d = |x − y| ≤ 1/e`,

```
|φ(x) − φ(y)| ≤ φ(d) = d ln(1/d).
```

*Proof.* Take `x ≤ y = x + d`, `0 < d ≤ 1/e` (`d = 0` is trivial).
*Upper.* `φ(x + d) = −x ln(x + d) − d ln(x + d) ≤ −x ln x − d ln d = φ(x) + φ(d)`, because
`ln(x + d) ≥ ln x` (for `x > 0`; for `x = 0` the first term is `0` on both sides) and
`ln(x + d) ≥ ln d`. So `φ(y) − φ(x) ≤ φ(d)`.
*Lower.* `φ` is concave on `[0, 1]` (`φ'' = −1/x < 0`), so `x ↦ φ(x + d) − φ(x)` is
nonincreasing on `[0, 1 − d]`, and its minimum is at `x = 1 − d`:
`φ(1) − φ(1 − d) = (1 − d) ln(1 − d) ≥ −d`, because `ψ(d) = (1 − d) ln(1 − d) + d` has
`ψ(0) = 0` and `ψ'(d) = −ln(1 − d) ≥ 0`. So `φ(y) − φ(x) ≥ −d ≥ −φ(d)`, the last step
because `φ(d) = d ln(1/d) ≥ d` iff `d ≤ 1/e`. ∎

The restriction `d ≤ 1/e` is needed: at `x = 0.1`, `y = 1` the difference is `0.230` and
`φ(0.9) = 0.095`. `beta_star.py` tests the lemma on a `2001 × 2001` grid (zero violations);
the CHECKER's independent attack is in the gossip file. Note also that `φ` is increasing on `[0, 1/e]` (`φ'(x) = −ln x − 1 ≥ 0`),
so `d ≤ 1/n ≤ 1/e` gives `φ(d) ≤ φ(1/n) = (ln n)/n`.

**Lemma 4 (the rounding of `t`).** Let `0 < β < 1`, `a = (1 − β)/2`, `k = ⌊βn⌋` and
`t = ⌈(n − k)/2⌉`. Then `t ≥ 1`, `a n ≤ t < a n + 1`, and `t(t − 1) ≥ a n (a n − 1)`.

*Proof.* `k ≤ βn < n` gives `n − k ≥ 1`, so `t ≥ 1`, and `t ≥ (n − k)/2 ≥ (n − βn)/2 = an`.
`k > βn − 1` gives `n − k < 2an + 1`, so `t ≤ (n − k + 1)/2 < an + 1`.
For the product: if `an ≥ 1/2`, `x ↦ x(x − 1)` is nondecreasing on `[1/2, ∞)` and
`t ≥ an ≥ 1/2`; if `an < 1/2`, then `an(an − 1) < 0 ≤ t(t − 1)` since `t ≥ 1`. ∎

### 2.2 Proof of Theorem A

Let `n ≥ max(3, c)`, so that `p = c/n ∈ (0, 1]`, and `k = ⌊βn⌋`; the event `{pw ≤ βn}` is
`{pw ≤ k}`, and `k < n` so (0) applies. Write `θ = t − an ∈ [0, 1)` (Lemma 4) and

```
u = t/n = a + θ/n,     v = (t − 1)/n = a + (θ − 1)/n,     w = (n − 2t + 1)/n = (1 − 2a) + (1 − 2θ)/n,
```

three numbers in `[0, 1]` summing to `1`, each within `1/n` of `a`, `a`, `1 − 2a`
respectively (`|θ| < 1`, `|θ − 1| ≤ 1`, `|1 − 2θ| ≤ 1`). Since `n ≥ 3 > e`, Lemma 3 applies to
each coordinate with `d ≤ 1/n ≤ 1/e`, and `φ(d) ≤ φ(1/n) = (ln n)/n` because `φ` is increasing on
`[0, 1/e]` (`φ'(x) = −ln x − 1 ≥ 0` there; the CHECKER asked for this step to be stated):

```
H(u, v, w) ≤ H(a, a, 1 − 2a) + 3 (ln n)/n.                                                         (1)
```

By Lemma 1 on the trinomial, `C(n, t)·C(n − t, t − 1) ≤ exp(n H(u, v, w))`, hence by (1)

```
C(n, t)·C(n − t, t − 1) ≤ exp( n H(a, a, 1 − 2a) + 3 ln n ).                                       (2)
```

By Lemma 2 with `p = c/n`, `m = t(t − 1)`, then Lemma 4,

```
(1 − c/n)^(t(t − 1)) ≤ exp( −c t(t − 1)/n ) ≤ exp( −c (a²n² − an)/n ) = exp( −c a² n + c a ).       (3)
```

Multiplying (2) and (3) into (0):

```
P(pw ≤ βn) ≤ exp( n H(a, a, 1 − 2a) − c a² n + 3 ln n + c a ) = exp( −δ(β, c) n + 3 ln n + c a ),
```

and `a ≤ 1/2` gives the second form of (A). ∎

**Where the error terms come from, for a later formalisation.** `3 ln n` is three
applications of Lemma 3 with shifts `≤ 1/n` (one per coordinate of the type); `c·a` is
the `−an` in `t(t − 1) ≥ a²n² − an` (Lemma 4). Lemma 1 and Lemma 2 contribute no error at
all: they are exact bounds on the two factors of (0). Nothing is hidden in an `o(n)`.

### 2.3 Proof of Theorem A′

Put `g(a) = H(a, a, 1 − 2a) − c a² = −2a ln a − (1 − 2a) ln(1 − 2a) − c a²` on `(0, 1/2]`,
so `δ(β, c) = −g((1 − β)/2)`; `β ∈ (0, 1)` corresponds to `a ∈ (0, 1/2)`, decreasingly.

*Shape of `g`.* `g` extends continuously by `g(0) = 0` (`φ(a) → 0`). It is `C²` on
`(0, 1/2)` with

```
g'(a) = 2 ln((1 − 2a)/a) − 2 c a,        g''(a) = −4/(1 − 2a) − 2/a − 2c < 0,
```

so `g` is strictly concave on `(0, 1/2]` (and continuous on `[0, 1/2]`). Also
`g'(a) → +∞` as `a → 0⁺`, so `g > 0` on some `(0, η)`. Finally
`g(1/2) = −ln(1/2) − 0 − c/4 = ln 2 − c/4`.

*Case `c ≤ 4 ln 2`.* Then `g(1/2) ≥ 0 = g(0)`. A concave function lies above its chords,
so on `[0, 1/2]`, `g(a) ≥ (1 − 2a) g(0) + 2a g(1/2) ≥ 0`; thus `δ(β, c) ≤ 0` for every
`β ∈ (0, 1)`. At the boundary `c = 4 ln 2` exactly, `g(1/2) = 0` and *strict* concavity gives
`g > 0` on `(0, 1/2)`, so no `β ∈ (0, 1)` is admissible there either: `β*(4 ln 2) = 0`, and the
condition in the theorem is `c > 4 ln 2`, strictly.

*Case `c > 4 ln 2`.* Then `g(1/2) < 0 < g(η/2)`, so `g` has a zero `a*` in `(η/2, 1/2)` by
continuity. It is unique: a strictly concave function that is positive somewhere to the
left of a zero is negative everywhere to the right of it (if `g(a₁) = 0 < g(a₀)` with
`a₀ < a₁ < a₂` then `g(a₁) > ` the chord value between `a₀` and `a₂`, which forces
`g(a₂) < 0`). So `g > 0` on `(0, a*)`, `g(a*) = 0`, `g < 0` on `(a*, 1/2]`, i.e.
`δ(β, c) > 0 ⟺ a > a* ⟺ β < 1 − 2a* = β*(c)`. ∎

Unwinding `g(a*) = 0` with `a = (1 − β)/2` gives the displayed equation for `β*`.
(At `β = β*` itself the bound (A) is `e^(c/2) n³`, which says nothing — the theorem is
for `β < β*`.)

### 2.4 Proof of Theorem A″

Two elementary facts. (i) For `0 < x < 1`: `0 < −(1 − x) ln(1 − x) ≤ x`. The left is
`ln(1/(1 − x)) > 0`; the right is `ln y ≤ y − 1` at `y = 1/(1 − x)`, i.e.
`−ln(1 − x) ≤ x/(1 − x)`. (ii) Hence for `0 < a < 1/2`, dividing `g(a)` by `a` and using (i)
with `x = 2a`:

```
2 ln(1/a) − c a  <  g(a)/a  ≤  2 ln(1/a) + 2 − c a.                                              (4)
```

Let `c ≥ 14` and set

```
a₋ = (2/c) ln( c / (2 ln c) ),          a₊ = (2/c) ( ln( 2c / ln c ) + 1 ).
```

*Both lie in `(0, 1/2)`.* `a₋ > 0` because `c > 2 ln c` for all `c > 0` (the minimum of
`c − 2 ln c` is `2 − 2 ln 2 > 0`); `a₋ ≤ (2/c) ln c ≤ (2 ln 14)/14 < 0.38` because `ln c / c`
decreases for `c ≥ e`. `a₊ > 0` is clear; `a₊ ≤ 1/2 ⟺ 4 ln(2c/ln c) + 4 ≤ c`, which holds at
`c = 14` (`13.45 ≤ 14`) and for all larger `c` since the left side has derivative
`4(1/c − 1/(c ln c)) < 1`. (It fails at `c = 13`, which is why the statement says `c ≥ 14`.)

*`g(a₋) > 0`.* By the left inequality of (4),
`g(a₋)/a₋ > 2 ln(1/a₋) − c a₋ = 2 ln( c / (2 ln(c/(2 ln c))) ) − 2 ln( c/(2 ln c) ) = 2 ln( ln c / ln(c/(2 ln c)) ) > 0`,
since `ln c > ln(c/(2 ln c))` as soon as `2 ln c > 1`.

*`g(a₊) < 0`.* By the right inequality of (4), with `c a₊ = 2 ln(2c/ln c) + 2`,
`g(a₊)/a₊ ≤ 2 ln(1/a₊) + 2 − 2 ln(2c/ln c) − 2 = 2 ln( ln c / (2c a₊) ) = 2 ln( ln c / (4 ln(2c/ln c) + 4) )`,
and this is negative iff `ln c < 4 ln(2c/ln c) + 4`; with `x = ln c` that reads
`4 ln x − 3x < 4 ln 2 + 4`, true for every `x > 0` since `4 ln x − 3x ≤ 4 ln(4/3) − 4 < 0`.

*Conclusion.* By §2.3, `g > 0` exactly on `(0, a*)` and `g < 0` exactly on `(a*, 1/2]`, so
`a₋ < a*(c) < a₊`, which is the displayed two-sided bound after multiplying by `2`
(`2a₋ = (4 ln c − 4 ln ln c − 4 ln 2)/c`, `2a₊ = (4 ln c − 4 ln ln c + 4 ln 2 + 4)/c`).
Both ends are `(4 ln c / c)(1 + o(1))`, so `1 − β*(c) ~ 4 ln c / c`.

*The constant.* The bracket gives `c a* = 2 ln c − 2 ln ln c + O(1)`, so
`ln(1/a*) = ln c − ln(c a*) = ln c − ln ln c − ln 2 + o(1)`. The exact equation
`g(a*) = 0` reads `c a* = 2 ln(1/a*) + ψ(2a*)/a*` with `ψ(x) = −(1 − x) ln(1 − x) = x − x²/2 − …`,
and `ψ(2a)/a = 2 − 2a + O(a²) → 2`. Hence
`c a* = 2 ln c − 2 ln ln c − 2 ln 2 + 2 + o(1)` and `1 − β* = 2a* = (4 ln c − 4 ln ln c + 4 − 4 ln 2 + o(1))/c`.
The `o(1)` is dominated by `2 ln(1 + (ln ln c + O(1))/ln c) = O(ln ln c / ln c)`, which is
why the numerics in §3 approach `4 − 4 ln 2 ≈ 1.227` only slowly: the measured
`c(1 − β*) − (4 ln c − 4 ln ln c)` is `1.95` at `c = 10²`, `2.10` at `10³` and `1.90` at `10⁶`
(`beta_star.log`), still `0.7` above the limit at `c = 10⁶`, where `ln ln c / ln c = 0.19`. ∎

### 2.5 Proof of Theorem B

Fix `p ∈ (0, 1)`, `b = 1/(1 − p) > 1`, `ε > 0`; let `s = (4 + ε) log_b n`, assume `s ≤ n`, and
let `k = ⌊n − s⌋`, so `0 ≤ k < n` and `{pw ≤ n − s} = {pw ≤ k}`. Then `n − k ≥ s` and
`t = ⌈(n − k)/2⌉ ≥ s/2 = (2 + ε/2) log_b n ≥ 2 ln n / ln b`.

Apply (0) with the crude bounds `C(n, t) ≤ n^t`, `C(n − t, t − 1) ≤ n^(t − 1)` and
`(1 − p)^(t(t − 1)) = b^(−t(t − 1))`:

```
ln P(pw ≤ k) ≤ (2t − 1) ln n − t(t − 1) ln b = −t · [ (t − 1) ln b − 2 ln n ] − ln n.
```

Now `(t − 1) ln b ≥ (2 + ε/2) ln n − ln b ≥ (2 + ε/4) ln n` when `ln b ≤ (ε/4) ln n`, i.e. for
`n ≥ b^(4/ε)`. Then the bracket is `≥ (ε/4) ln n > 0`, and with `t ≥ 2 ln n / ln b`,

```
ln P(pw ≤ k) ≤ −(2 ln n / ln b)(ε/4) ln n − ln n = −(ε / (2 ln b)) ln² n − ln n,
```

which is the claim, since `exp(−(ε/(2 ln b)) ln² n) = n^(−(ε/2) ln n / ln b) = n^(−(ε/2) log_b n)`. ∎

**Theorem B is Turner's Theorem 2.1 for bandwidth, re-proved for pathwidth with the same count** (the direction matters: `pw ≤ bw`, so a bandwidth lower bound says nothing about pathwidth; what carries over is the pair count, and the pathwidth empty-pair lemma does the rest). Turner (1986),
*SIAM J. Comput.* 15(2):561–580, §2 (read in full by the CHECKER, `lit/turner1986.pdf`):
Lemma 2.1 is the empty-pair lemma for bandwidth (`bw ≤ n − 2k` gives an empty pair of sizes
`k, k`, the first and last `k` positions), Lemma 2.2 the first moment
`P(bw ≤ n − 2k) ≤ [(en/k)(1 − p)^(k/2)]^(2k)`, and Theorem 2.1 states `bw > n − 4 log_b n`
almost surely for fixed `p`. Since `pw ≤ bw`, our Theorem B *implies* his Theorem 2.1 and
not conversely; the proof is the same count with the pathwidth empty pair in place of the
bandwidth one. Cite him for the dense constant `4`.

(The entropy bound of Lemma 1 would sharpen the constant in front of `ln² n` but not the
`4` in `(4 + ε) log_b n`, which comes from `n^(2t)` against `b^(t²)`: the pair `(A, R)` has
about `2t log n` bits of choice and `t²` forbidden edges. Together with `pw ≤ n − α(G)` and
`α(G(n, p)) = (2 + o(1)) log_b n`, this is the sandwich `(2 − o(1)) log_b n ≤ n − pw ≤ (4 + o(1)) log_b n`
of the survey §3; the lower half is proved here, the upper half is the independence bound
`pathwidth_le_card_sub_indepNum` plus the classical independence number, which is not
re-proved here.)

---

## 3. `β*(c)` numerically

`beta_star.py`: Brent's method on `g(a) = −2a ln a − (1 − 2a) ln(1 − 2a) − c a²` over
`(10⁻¹², 1/2)`, `xtol = 10⁻¹⁴`; `β* = 1 − 2a*`. The equation solved is the one in
Theorem A′. Comparison with the survey's table (§7(a), three decimals, computed there by a
`10⁻⁴` scan) and with the two asymptotic formulas of Theorem A″:

| `c` | `a*(c)` | **`β*(c)`** | survey | difference | `1 − 4 ln c/c` | `1 − (4 ln c − 4 ln ln c + 4 − 4 ln 2)/c` |
|---|---|---|---|---|---|---|
| 3 | 0.495654 | **0.0087** | 0.009 | −0.0003 | −0.465 | −0.749 |
| 4 | 0.469354 | **0.0613** | 0.061 | +0.0003 | −0.386 | −0.367 |
| 5 | 0.441265 | **0.1175** | 0.118 | −0.0005 | −0.288 | −0.152 |
| 6 | 0.414682 | **0.1706** | 0.171 | −0.0004 | −0.195 | −0.010 |
| 8 | 0.368604 | **0.2628** | 0.263 | −0.0002 | −0.040 | 0.173 |
| 10 | 0.331448 | **0.3371** | 0.337 | +0.0001 | 0.079 | 0.290 |
| 12 | 0.301338 | **0.3973** | 0.397 | +0.0003 | 0.172 | 0.373 |
| 16 | 0.255880 | **0.4882** | 0.488 | +0.0002 | 0.307 | 0.485 |
| 20 | 0.223263 | **0.5535** | 0.554 | −0.0005 | 0.401 | 0.559 |
| 50 | 0.119691 | **0.7606** | 0.761 | −0.0004 | 0.687 | 0.772 |
| 100 | 0.071314 | **0.8574** | 0.857 | +0.0004 | 0.816 | 0.865 |

**No disagreement with the survey**: every difference is within the rounding of its three
decimals (the largest, `0.0005`, is `β*(5) = 0.11747` and `β*(20) = 0.55347`, both rounding
to the survey's values). Near the threshold: `β*(2.78) = 0.00018`, `β*(2.8) = 0.00077`,
`β*(2.9) = 0.0044`, `β*(3) = 0.0087`. The threshold itself is `4 ln 2 = 2.77259`.

The leading asymptotic `1 − 4 ln c / c` is useless below `c ≈ 10` and still `0.04` low at
`c = 100`; the second-order form is within `0.01` from `c = 16` on and `0.008` high at
`c = 100`, the residual being the `O(ln ln c / ln c)` of §2.4. The two-sided bound of
Theorem A″ was verified for every integer `c` from `14` to `199` and at `c = 500, 10³, 10⁴, 10⁵, 10⁶`
(`beta_star.log`: "bracketing holds on all tested c").

The exponential rate itself, at a point halfway to the threshold: `δ(β*/2, c) = 0.025, 0.13,
0.23, 0.33, 0.52, 0.70, 0.87, 1.21, 1.52, 3.71, 7.08` at the eleven `c` above. At `c = 3` the
rate is tiny even at `β = β*/2 = 0.0043`: the bound at `c = 3` is a statement about
`n ≳ 10³` (`3 ln n / n < 0.025` needs `n > 1000`), see §5.

---

## 4. Comparison with the literature

*The CHECKER's findings, gossip file entry of 2026-10-31 04:58, with the exact statements
located; the sources it read in full are in `reports/scratch/first_moment/lit/`.*

**Verdict (final, gossip entries 04:58 and 05:20).** The *method* is published twice, both
times with a crude count and neither time with a sparse constant.

*Turner (1986)*, *SIAM J. Comput.* 15(2):561–580, §2, for **bandwidth**: Lemma 2.1 (`bw ≤ n − 2k`
forces an empty pair of sizes `k, k`), Lemma 2.2 (`P(bw ≤ n − 2k) ≤ [(en/k)(1 − p)^(k/2)]^(2k)`,
by `C(n, k) ≤ (en/k)^k`), Theorem 2.1 (`bw > n − 4 log_b n` a.s. for fixed `p` — our Theorem B's
constant, for the larger parameter) and Theorem 2.2 (`bw ≥ (1 − ε) n` for `p = c ln n / n`). He
states nothing at `p = c/n`, and then leaves `G(n, p)` for a planted model. His Lemma 2.2 at
`p = c/n`, `k = εn` would give `bw ≥ (1 − 2ε) n` whenever `cε > 2 + 2 ln(1/ε)`, a bandwidth
constant he never wrote down: vacuous for `c ≤ 4 + 4 ln 2 = 6.77`, then `0.100, 0.222, 0.311,
0.434, 0.516, 0.753, 0.855` at `c = 8, 10, 12, 16, 20, 50, 100` (CHECKER, `checker_turner.py`),
against `β* = 0.263, 0.337, 0.397, 0.488, 0.554, 0.761, 0.857`: the `(en/k)^k` count loses
almost nothing at large `c` and everything near the threshold. Those numbers are for `bw`; as
`pw ≤ bw` they say nothing about pathwidth without the pathwidth empty-pair lemma
(`EmptyPair.lean`), which is the step he does not have.

*Díaz, Petit, Serna & Trevisan (2001)*, *Discrete
Math.* 235:245–253, Lemma 2 (pp. 249–250) and Lemma 3 (g5) (p. 252), for **vertex separation**. Lemma 2 shows
`G(n, c_n/n)` is `(ε, γ, c_n)`-mixing with probability `1 − 2^(−Ω(n))` for
`c_n ≥ 3(1 + ln 3)(εγ)^(−2)`, `ε ∈ (0, 1/6)`, by a union bound over the `3^n` pairs `(A, B)`
and a Chernoff bound on the `A–B` edges; Lemma 3 (g5) then observes, for any layout, that
"there cannot be `εn` vertices on the left of `i` and `εn` vertices on the right of `i`
without any connection", so the cut at `i` has `≥ i − εn` active vertices and
`MINVS(G) ≥ (1/2 − ε) n − 1`. **That is the empty-pair first moment**: the deterministic
observation is the one `EmptyPair.lean` makes exact (`pw ≤ k` forces an empty pair of sizes
`⌈(n − k)/2⌉`, `⌈(n − k)/2⌉ − 1`), and the count is theirs with `3^n` in place of the
trinomial and a two-sided Chernoff slack in place of the exact `(1 − p)^(|A||B|)`.

**What is not published**, as far as the checker found (Turner 1986 and DPST 2001 read in
full; Díaz–Petit–Serna 2002 *ACM Comput. Surv.* §8.1 Theorem 8.1, which restates DPST
verbatim and cites Turner and Bollobás 1985 p. 374 for bandwidth; Petit's 2011 addenda;
Perarnau–Serra 2014; Lee–Lee–Oum 2012; Kloks 1994; Gao 2006, 2012; Luczak–McDiarmid 2001,
whose `ln 4` bisection threshold is a giant-component argument, not a first moment;
Karoński–Scheinerman–Singer-Cohen 1999, subgraph thresholds only; web search on
pathwidth / vertex separation / node search of random graphs): the trinomial entropy form
`H(a, a, 1 − 2a) − c a²`, any `β(c)` for pathwidth or bandwidth at `p = c/n`, the threshold
`4 ln 2`, and the asymptotics of §2.4. **The claim this document supports: the empty-pair
first moment is Turner's (1986, bandwidth) and Díaz–Petit–Serna–Trevisan's (2001, vertex
separation); what is new is (i) the exact empty-pair lemma for pathwidth (`EmptyPair.lean`),
(ii) the entropy count in place of `(en/k)^(2k)` or `3^n`, (iii) the resulting `β*(c)`, its
threshold and its asymptotics, and (iv) the finite, Lean-proved inequality (0). It is a
sharpening of a published argument, not a new method; cite Turner beside DPST.** One source
is **UNVERIFIED**: Bollobás (1985) p. 374, cited by DPS 2002 for bandwidth, could not be
obtained (not held, not on archive.org, Google Books quota exhausted); by its citation
context it is Turner's statement for `p ≫ 1/n`, and an entropy-form sparse constant there is
not expected but was not excluded by reading.

A remark the checker makes that belongs in the paper: the pathwidth pair (sizes `t, t − 1`)
and the bandwidth pair (sizes `k, k`) differ by one vertex, so **`β*(c)` is simultaneously
the first-moment lower bound for `bw`, `pw`, `vs`, node search and gate-matrix layout `− 1`
on `G(n, c/n)`, and it can be sharp for at most one of them**; `pw ≤ n − α(G) ≤ (1 − ln(1 + c)/c) n`
keeps `pw/n` strictly below `1`, and where `bw/n` sits is not checked.

**The numbers.** Lower bounds on `pw(G(n, c/n))/n` at the same `c` (a treewidth bound is a
pathwidth bound since `tw ≤ pw`; the converse fails):

| `c` | **`β*(c)` (here, pw)** | DPST Lemma 3 as stated, `1/2 − √(3(1 + ln 3)/c)` | DPST with the prefix at `(1 − ε)n`, `1 − 2√(3(1 + ln 3)/c)` | DPST's `3^n` count with the exact pair probability, `1 − 2√(ln 3/c)` | Perarnau–Serra 2014 (tw), `1 − √(9 ln 3/(2c))` |
|---|---|---|---|---|---|
| 3 | 0.0087 | — | — | — | — |
| 4 | 0.0613 | — | — | — | — |
| 5 | 0.1175 | — | — | 0.063 | 0.006 |
| 6 | 0.1706 | — | — | 0.144 | 0.092 |
| 8 | 0.2628 | — | — | 0.259 | 0.214 |
| 10 | 0.3371 | — | — | **0.337** | 0.297 |
| 12 | 0.3973 | — | — | 0.395 | 0.358 |
| 16 | 0.4882 | — | — | 0.476 | 0.444 |
| 20 | 0.5535 | — | — | 0.531 | 0.503 |
| 50 | 0.7606 | 0.145 | 0.290 | 0.704 | 0.686 |
| 100 | 0.8574 | 0.249 | 0.498 | 0.790 | 0.778 |

"—" means vacuous (nonpositive, or outside the lemma's hypotheses: DPST need `ε < 1/6`,
i.e. `c ≥ 226.6`, formally; the column is evaluated at `γ → 1` and ignores that restriction,
so it is generous to them). Reading the columns:

- **DPST as published** is vacuous for every `c` in the table and gives `0.333` at `c = 227`,
  `0.421` at `c = 1000`, against `β* = 0.925`, `0.978`: the Chernoff slack `3(1 + ln 3)` and the
  single position `n/2` cost most of the bound.
- **Their argument with the exact pair probability and the `3^n` count** gives
  `1 − 2√(ln 3 / c)`, which **equals `β*` at `c = 10`** — not a coincidence of the table but of
  the numbers: `a*(10) = 0.3314 ≈ 1/3`, and `H(1/3, 1/3, 1/3) = ln 3`, so the trinomial entropy
  and the `3^n` count agree exactly where the empty pair is one third of the vertices. Within
  `0.004` of `β*` for `8 ≤ c ≤ 12`; below it everywhere else, by `0.05` at `c = 5` and `0.07` at
  `c = 100`. The entropy count is what separates `β*` from this column at large `c`
  (`1 − 2√(ln 3/c)` has `1 − β = Θ(c^(−1/2))` against the true `Θ(ln c / c)`).
- **Perarnau–Serra's treewidth bound** is below `β*` at every `c`, by `0.05`–`0.11` for `c ≥ 6`
  and vacuous below `c = 4.94`; the `9 ln 3 / 2` carries their `1/3`–`2/3` balancing slack,
  which layouts do not need. It is also the only one of the four that is a treewidth
  statement, so it says more than `β*` does about a different parameter.
- **Lee–Lee–Oum (2012), Gao (2006, 2012), Kloks (1994)**: linear treewidth above
  `c = 1`, `2.146`/`2.162`, `2.36` respectively, with implicit constants and nothing for
  pathwidth; they are the only results that say anything for `c ≤ 4 ln 2`, where the first
  moment says nothing (§6, item 3).

## 5. The finite inequality against the pilot data

`finite_bound.py` evaluates the right-hand side of (0) **exactly** (log-gamma, no
relaxation), `B(n, k, p) = C(n, t)·C(n − t, t − 1)·(1 − p)^(t(t − 1))`, at `p = c/n`, and the
relaxed form (A) beside it, for the pilot cells of `reports/scratch/gnp_pilot/results.csv`
(survey §7(d)). "min pw" is the smallest pathwidth among the cell's exactly solved graphs
(status `bound`, `minor` or `refutation`); at `n = 120` the graphs are unproved
(status `upper`) and only the solver's lower bounds are known.

| `n` | `c` | largest `k` with `B < 1` | largest `k` with `B < 0.01` | largest `k` with (A) `< 1` | `β*(c)·n` | graphs | exact | observed min pw | min lower bound (unproved) |
|---|---|---|---|---|---|---|---|---|---|
| 60 | 3 | 1 | — | — | 0.5 | 136 | 136 | 5 | — |
| 60 | 4 | 5 | 3 | 0 | 3.7 | 136 | 136 | 8 | — |
| 60 | 6 | 11 | 11 | 6 | 10.2 | 134 | 134 | 16 | — |
| 60 | 8 | 17 | 17 | 11 | 15.8 | 132 | 132 | 20 | — |
| **60** | **10** | **23** | **21** | **15** | **20.2** | **133** | **133** | **25** | — |
| 120 | 3 | 1 | 1 | — | 1.0 | 13 | 3 | 11 | 12 |
| 120 | 4 | 9 | 7 | 3 | 7.4 | 13 | 0 | — | 17 |
| 120 | 6 | 21 | 21 | 15 | 20.5 | 13 | 0 | — | 25 |
| 120 | 8 | 33 | 33 | 26 | 31.5 | 13 | 0 | — | 34 |
| **120** | **10** | **43** | **41** | **35** | **40.5** | **13** | **0** | — | **41** |

**At `n = 60`, `c = 10`** (`p = 1/6`), the proved finite bound gives

| `k` | 0–1 | 2–3 | … | 14–15 | 16–17 | 18–19 | 20–21 | 22–23 | 24–25 | 26–27 |
|---|---|---|---|---|---|---|---|---|---|---|
| `t` | 30 | 29 | | 23 | 22 | 21 | 20 | 19 | 18 | 17 |
| `B(60, k, 1/6)` | 4.6e−51 | 2.6e−44 | | 1.9e−14 | 1.1e−10 | 3.1e−7 | 4.5e−4 | **0.34** | 139 | 3.0e4 |

(the value depends on `k` only through `t = ⌈(60 − k)/2⌉`, so it is constant on pairs).
So **the finite inequality says `P(pw ≤ 23) ≤ 0.34` and `P(pw ≤ 21) ≤ 4.5 × 10⁻⁴`**, and the
pilot's 133 graphs have pathwidths `25 (5 graphs), 26 (10), 27 (39), 28 (40), 29 (32), 30 (6), 32 (1)`:
the observed minimum `25 = 0.417 n` sits **two above** the last `k` the bound excludes with
any confidence, and the whole sample sits above it. The asymptotic threshold `β*(10)·60 = 20.2`
is *below* the finite bound's reach (`23`), because the finite inequality keeps the
trinomial's polynomial factor (about `1/n` relative to `e^(nH)`) and the exact
`(1 − p)^m`, both of which the relaxation (A) gives away: (A) is below `1` only for
`k ≤ 15`, eight stacks lower. The cost of (A)'s error terms at this size is
`3 ln n + c a ≈ 12.3 + 3.3` nats, plus the Stirling factor of Lemma 1 (about `2` decades)
and Lemma 2's `p² t²/2 ≈ c² a²/2 ≈ 5` nats — some ten decades in all, matching
`log₁₀ A − log₁₀ B ≈ 9.6` at `k = 22`.

**At `n = 120`, `c = 10`** (`p = 1/12`): `B < 1` for `k ≤ 43` (`B(43) = 0.10`), `B < 0.01` for
`k ≤ 41` (`B(41) = 1.3 × 10⁻⁴`), `B(45) = 58`. The 13 pilot graphs there are unproved, with
solver lower bounds `41 (6 graphs)` and `42 (7)` and upper bounds up to `14` higher; so the
finite inequality (`pw ≥ 42` with probability `≥ 0.9998`, `pw ≥ 44` with probability `≥ 0.89`)
is *at least as informative as the solver's lower bounds* at this size, and says what the
pilot could not: the true values are almost surely `≥ 44`. `β*(10)·120 = 40.5`.

**Reading.** The exact finite bound (0) is within 2–5 stacks of the observed minimum at
`n = 60` for `c ≥ 6`, and its finite-`n` threshold exceeds `β*(c)·n` at every cell; the
relaxed exponential form (A) is what is proved to decay but is loose by `~8` stacks at
`n = 60` and only reaches `k = βn` for `β = 0.30`, `c = 10` from `n ≈ 141` (and for
`β = 0.25` from `n ≈ 45`; these are with `k = ⌊βn⌋` and the criterion "below `1` for the
next sixty `n`" — evaluated at exactly `βn` the first `n` are `143` and `48`, CHECKER; the
exact `B(n, ⌊βn⌋, c/n)` is already below `1` at `n = 12` for every `β ≤ 0.33` at `c = 10`). For the paper: quote the exact finite bound (0) against the
data and Theorem A for the limit; do not quote (A) at `n = 60`.

At `c = 3`, `n = 60` the bound excludes only `pw ≤ 1` and the observed minimum is `5`: the
rate `δ` is at most `0.025` there (§3), so (A) needs `n` in the thousands, and the finite
bound needs `n ≈ 10³` to reach `β*(3) n ≈ 9`. This is the regime where the first moment is
weakest and the data (fitted slope `0.099` against `β*(3) = 0.009`, survey §7(d)) are far
above it.

---

## 6. What remains

1. **Lean.** Theorem A is written so that each step is one lemma: (I1) the multinomial
   entropy bound (Mathlib has `Nat.multinomial` and the multinomial theorem; the entropy
   form is a short lemma), (I2) `1 − p ≤ e^(−p)` (`Real.add_one_le_exp`), (I3) the shift
   lemma for `−x log x` (Mathlib's `Real.negMulLog` with its concavity), (I4) the
   rounding of `t` (integer arithmetic). The assembly is (0) × (2) × (3). Theorem A′
   needs strict concavity of `g` and the intermediate value theorem; Theorem A″ is
   elementary real inequalities; Theorem B is (0) with `C(n, j) ≤ n^j`. The statements
   are in the survey's `paper1/todo.md` queue as step (2) of the first-moment plan.
2. **The constant in Theorem A″.** `1 − β* = (4 ln c − 4 ln ln c + K + o(1))/c` with
   `K = 4 − 4 ln 2` is proved; the rate of the `o(1)` is `O(ln ln c / ln c)` and is not
   made explicit.
3. **The literature check is closed except for one page**: Bollobás (1985) p. 374, which
   the checker could not obtain (§4). Turner (1986) was read in full and is cited for the
   method and the dense constant.
4. **Below `4 ln 2`.** The method gives nothing for `c ≤ 2.7726`; a linear lower bound there
   (Lee–Lee–Oum, Gao) needs a different argument, and the data (slope `0.040` at `c = 2`)
   say the pathwidth is linear well below the threshold.
5. **The gap to the data** is `0.08`–`0.10` in `β` at `c = 3`–`10` (survey §7(d)). The finite
   inequality is tight to within a few stacks at `n = 60` for `c ≥ 6`, so the gap is
   asymptotic, not a finite-size artefact of the bound: the union bound over `(A, R)`
   overcounts by the number of empty pairs a graph of pathwidth `k` has, which is
   exponential in `n`. A second-moment or a structured count is the next step if the
   constant is to move.
