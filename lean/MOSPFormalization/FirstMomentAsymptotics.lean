/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The first moment at `p = c/n`: Theorem A, the finite exponential bound

Theorem A of `reports/random_graph_first_moment.md` (2026-10-31): the finite-`n` form of
the first-moment lower bound on the pathwidth of `G(n, c/n)`. Its probabilistic input is
`weightedSum_graphsOfPathwidthLe_le` (`FirstMoment.lean`, inequality (0) of the report);
everything here is real analysis on top of it, following §2.1–§2.2 of the report one
lemma per step.

Checked numerically first (`reports/scratch/first_moment/lean_target_check.py`, log beside
it, 2026-10-31): the exact statement of `firstMoment_pathwidth_le_fin` and each lemma
(I1)–(I4) in the exact form used below, on `n = 3..300`, `c ∈ {0.5, 1, 2, 4, 6, 10, 20, 50}`
with `c ≤ n` (so `n = c`, `p = 1`, included), `β` on 400 points of `(0, 1)` plus every `j/n`
and `β = 1 − 10⁻⁹`, `10⁻⁹`: 1,285,619 grid points, **zero violations**; the smallest slack is
`2.197` nats (`n = 3`, `β → 1`); the 30 tightest points re-evaluated in mpmath at 50 digits.

## The statement

For `c > 0`, `0 < β < 1`, `a = (1 − β)/2`, `n ≥ max(3, c)`, `k = ⌊βn⌋₊`, `t = (n − k + 1)/2`:

  `P(pw(G(n, c/n)) ≤ k) ≤ exp(−δ(β, c)·n + 3 log n + c·a) ≤ e^(c/2) · n³ · e^(−δ(β, c)·n)`,

  `δ(β, c) = c a² − H(a, a, 1 − 2a)`,  `H(x, y, z) = φ(x) + φ(y) + φ(z)`,  `φ = Real.negMulLog`.

`δ(β, c)` is `firstMomentRate c β`. The probability is written, as in `FirstMoment.lean`, as
the sum of `gnpWeight (c/n)` over `graphsOfPathwidthLe k` on `Fin n` (or any `V` with
`|V| = n`). If `δ(β, c) > 0` the probability tends to `0`
(`tendsto_firstMoment_pathwidth`); that `δ > 0` holds exactly for `β < β*(c)`, `c > 4 log 2`,
is Theorem A′ of the report and is **not** formalised here.

## The four lemmas and what Mathlib had

* **(I1)** `choose_mul_choose_le_exp_entropy` — the method-of-types bound in trinomial form,
  `C(n,i)·C(n−i,j) ≤ exp(n·H(i/n, j/n, (n−i−j)/n))`. Mathlib has no entropy bound on
  binomials or multinomials (`Nat.choose_le_pow_div` is `n^r/r!`; `BinaryEntropy.lean` has
  no `choose` lemma). Proved from `add_pow` and `Finset.single_le_sum`: one term of the
  binomial expansion is at most the sum (`choose_mul_pow_mul_pow_le_add_pow`), applied
  twice (`choose_mul_choose_mul_pow_le`: the trinomial term is at most `(x + y + z)^n`),
  at the weights `(i/n, j/n, (n−i−j)/n)` summing to `1`, with
  `exp_mul_negMulLog_div_mul_pow`: `exp(n·φ(j/n))·(j/n)^j = 1` (`0^0 = 1` matching
  `φ(0) = 0`). This is Remark 2.1 of the report: the two-binomial route yields the trinomial
  exponent with no chain rule, because `(1 − u)·(j/(n−i)) = j/n` is absorbed by the weights.
* **(I2)** `one_sub_pow_le_exp_neg_mul` — `(1 − p)^m ≤ exp(−p·m)`, from `Real.add_one_le_exp`
  and `pow_le_pow_left₀`.
* **(I3)** the shift lemma `negMulLog_le_add_of_abs_sub_le`: `φ(y) ≤ φ(x) + φ(d)` for
  `x ∈ [0, 1]`, `y ≥ 0`, `|y − x| ≤ d ≤ 1/e`. Mathlib has `Real.negMulLog` with
  `concaveOn_negMulLog`, `negMulLog_nonneg`, `negMulLog_mul` and its derivatives, but no
  shift or monotonicity lemma. The report proves the lower half by concavity; here both
  halves come from `Real.log_le_sub_one_of_pos` alone: `negMulLog_add_le`
  (`φ(x + d) ≤ φ(x) + φ(d)`, from `log` monotone), `negMulLog_le_negMulLog_add_sub`
  (`φ(x) ≤ φ(y) + (y − x)` for `x ≤ y ≤ 1`), `negMulLog_le_negMulLog_of_le` (`φ` monotone
  on `[0, 1/e]`), `le_negMulLog` (`d ≤ φ(d)` on `[0, 1/e]`). With `negMulLog_one_div_natCast`
  (`φ(1/n) = log n / n`) and `one_div_le_exp_neg_one` (`1/n ≤ 1/e` for `n ≥ 3`, from
  `Real.exp_one_lt_d9`).
* **(I4)** `rounding_t` — `k < n`, `1 ≤ t`, `2t ≤ n + 1`, `a n ≤ t < a n + 1`, from
  `Nat.floor_le`, `Nat.lt_floor_add_one` and `omega`; the product bound
  `t(t − 1) ≥ a²n² − an` is a `nlinarith` step inside the main proof
  (`(t − an)(t + an − 1) ≥ 0`).

## Main results

* `firstMoment_pathwidth_le` — **Theorem A on any finite `V`** with `|V| ≥ max(3, c)`.
* `firstMoment_pathwidth_le_fin` — the same on `Fin n`;
  `firstMoment_pathwidth_le_fin'` — the second form `e^(c/2) · n³ · e^(−δn)`
  (`exp_bound_eq`, and `c·a ≤ c/2`).
* `tendsto_firstMoment_bound`, `tendsto_firstMoment_pathwidth` — for `δ(β, c) > 0` the bound,
  and hence `P(pw(G(n, c/n)) ≤ ⌊βn⌋)`, tends to `0` as `n → ∞`
  (`tendsto_pow_mul_exp_neg_atTop_nhds_zero` and a squeeze).

Where the error terms come from, as the report says for a formalisation: `3 log n` is three
applications of (I3) with shifts `≤ 1/n`, one per coordinate of the type `(t/n, (t−1)/n,
(n−2t+1)/n)` against `(a, a, 1 − 2a)`; `c·a` is the `−an` of (I4). (I1) and (I2) contribute
no error.

No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only
(`reports/scratch/first_moment/lean_target_check.lean`, log `lean_target_check.axioms.log`).
-/

import MOSPFormalization.FirstMoment
import Mathlib.Analysis.SpecialFunctions.Log.NegMulLog
import Mathlib.Analysis.Complex.ExponentialBounds

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open Finset Real

/-! ### (I2) `(1 − p)^m ≤ exp(−p m)` -/

/-- **Lemma 2 of the report**: `(1 − p)^m ≤ exp(−p·m)` for `p ≤ 1`, from the tangent line
`1 − p ≤ exp(−p)` (`Real.add_one_le_exp`). -/
theorem one_sub_pow_le_exp_neg_mul (p : ℝ) (hp : p ≤ 1) (m : ℕ) :
    (1 - p) ^ m ≤ Real.exp (-(p * m)) := by
  have h1 : 1 - p ≤ Real.exp (-p) := by
    have := Real.add_one_le_exp (-p)
    linarith
  calc (1 - p) ^ m ≤ Real.exp (-p) ^ m := pow_le_pow_left₀ (by linarith) h1 m
    _ = Real.exp (-(p * m)) := by rw [← Real.exp_nat_mul]; ring_nf

/-! ### (I1) The entropy bound on the trinomial coefficient -/

/-- One term of the binomial expansion is at most the whole sum, for nonnegative `x, y`. -/
theorem choose_mul_pow_mul_pow_le_add_pow (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) {n i : ℕ}
    (hi : i ≤ n) : (n.choose i : ℝ) * x ^ i * y ^ (n - i) ≤ (x + y) ^ n := by
  rw [add_pow]
  have := Finset.single_le_sum (f := fun m => x ^ m * y ^ (n - m) * (n.choose m : ℝ))
    (fun m _ => by positivity) (Finset.mem_range.2 (Nat.lt_succ_of_le hi))
  linarith

/-- The trinomial term `C(n,i) C(n−i,j) x^i y^j z^(n−i−j)` is at most `(x + y + z)^n`. -/
theorem choose_mul_choose_mul_pow_le (x y z : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) (hz : 0 ≤ z)
    {n i j : ℕ} (hij : i + j ≤ n) :
    (n.choose i : ℝ) * (n - i).choose j * x ^ i * y ^ j * z ^ (n - i - j) ≤ (x + y + z) ^ n := by
  have h1 := choose_mul_pow_mul_pow_le_add_pow y z hy hz (n := n - i) (i := j) (by omega)
  have h2 := choose_mul_pow_mul_pow_le_add_pow x (y + z) hx (by linarith) (n := n) (i := i)
    (by omega)
  have h3 : (n.choose i : ℝ) * (n - i).choose j * x ^ i * y ^ j * z ^ (n - i - j) =
      (n.choose i : ℝ) * x ^ i * ((n - i).choose j * y ^ j * z ^ (n - i - j)) := by ring
  rw [h3]
  calc (n.choose i : ℝ) * x ^ i * ((n - i).choose j * y ^ j * z ^ (n - i - j))
      ≤ (n.choose i : ℝ) * x ^ i * (y + z) ^ (n - i) :=
        mul_le_mul_of_nonneg_left h1 (by positivity)
    _ ≤ (x + (y + z)) ^ n := h2
    _ = (x + y + z) ^ n := by ring

/-- `exp(n·φ(j/n)) · (j/n)^j = 1` for `j ≤ n` (with `0^0 = 1` matching `φ(0) = 0`):
`x^(−j) = exp(−j log x) = exp(n φ(x))` at `x = j/n`. -/
theorem exp_mul_negMulLog_div_mul_pow (n j : ℕ) (hj : j ≤ n) :
    Real.exp (n * negMulLog ((j : ℝ) / n)) * ((j : ℝ) / n) ^ j = 1 := by
  rcases Nat.eq_zero_or_pos j with rfl | hj0
  · simp
  have hn : (0 : ℝ) < n := by exact_mod_cast (lt_of_lt_of_le hj0 hj)
  have hx : (0 : ℝ) < (j : ℝ) / n := div_pos (by exact_mod_cast hj0) hn
  have h1 : (n : ℝ) * negMulLog ((j : ℝ) / n) = -((j : ℝ) * Real.log ((j : ℝ) / n)) := by
    rw [negMulLog]
    field_simp
  rw [h1, Real.exp_neg, Real.exp_nat_mul, Real.exp_log hx]
  exact inv_mul_cancel₀ (pow_ne_zero _ hx.ne')

/-- **Lemma 1 of the report (the method-of-types bound), trinomial form**:
`C(n,i)·C(n−i,j) ≤ exp(n·H(i/n, j/n, (n−i−j)/n))` with `H` the entropy in nats. -/
theorem choose_mul_choose_le_exp_entropy (n i j : ℕ) (hij : i + j ≤ n) :
    ((n.choose i * (n - i).choose j : ℕ) : ℝ) ≤
      Real.exp (n * (negMulLog ((i : ℝ) / n) + negMulLog ((j : ℝ) / n) +
        negMulLog (((n - i - j : ℕ) : ℝ) / n))) := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · have hi : i = 0 := by omega
    have hj : j = 0 := by omega
    subst hi; subst hj
    simp
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn
  set x : ℝ := (i : ℝ) / n with hx
  set y : ℝ := (j : ℝ) / n with hy
  set z : ℝ := ((n - i - j : ℕ) : ℝ) / n with hz
  have hx0 : 0 ≤ x := by positivity
  have hy0 : 0 ≤ y := by positivity
  have hz0 : 0 ≤ z := by positivity
  have hsum : x + y + z = 1 := by
    rw [hx, hy, hz, Nat.cast_sub (by omega), Nat.cast_sub (by omega)]
    field_simp
    ring
  have hterm := choose_mul_choose_mul_pow_le x y z hx0 hy0 hz0 hij
  rw [hsum, one_pow] at hterm
  have ex := exp_mul_negMulLog_div_mul_pow n i (by omega)
  have ey := exp_mul_negMulLog_div_mul_pow n j (by omega)
  have ez := exp_mul_negMulLog_div_mul_pow n (n - i - j) (by omega)
  rw [← hx] at ex; rw [← hy] at ey; rw [← hz] at ez
  set E := Real.exp (n * negMulLog x) * Real.exp (n * negMulLog y) * Real.exp (n * negMulLog z)
    with hE
  have hE' : E = Real.exp (n * (negMulLog x + negMulLog y + negMulLog z)) := by
    rw [hE, ← Real.exp_add, ← Real.exp_add]; ring_nf
  have hE1 : E * (x ^ i * y ^ j * z ^ (n - i - j)) = 1 := by
    calc E * (x ^ i * y ^ j * z ^ (n - i - j))
        = (Real.exp (n * negMulLog x) * x ^ i) * (Real.exp (n * negMulLog y) * y ^ j) *
            (Real.exp (n * negMulLog z) * z ^ (n - i - j)) := by rw [hE]; ring
      _ = 1 := by rw [ex, ey, ez]; ring
  rw [← hE']
  calc ((n.choose i * (n - i).choose j : ℕ) : ℝ)
      = ((n.choose i * (n - i).choose j : ℕ) : ℝ) * (E * (x ^ i * y ^ j * z ^ (n - i - j))) := by
        rw [hE1, mul_one]
    _ = E * ((n.choose i : ℝ) * (n - i).choose j * x ^ i * y ^ j * z ^ (n - i - j)) := by
        push_cast; ring
    _ ≤ E * 1 := mul_le_mul_of_nonneg_left hterm (by positivity)
    _ = E := mul_one E

/-! ### (I3) The shift lemma for `φ = negMulLog` -/

/-- `φ(x + d) ≤ φ(x) + φ(d)` for `x, d ≥ 0`: `log(x + d) ≥ log x` and `log(x + d) ≥ log d`.
(The upper half of Lemma 3 of the report; no concavity needed.) -/
theorem negMulLog_add_le (x d : ℝ) (hx : 0 ≤ x) (hd : 0 ≤ d) :
    negMulLog (x + d) ≤ negMulLog x + negMulLog d := by
  simp only [negMulLog]
  have hxl : x * Real.log x ≤ x * Real.log (x + d) := by
    rcases hx.eq_or_lt with rfl | hx'
    · simp
    · exact mul_le_mul_of_nonneg_left (Real.log_le_log hx' (by linarith)) hx
  have hdl : d * Real.log d ≤ d * Real.log (x + d) := by
    rcases hd.eq_or_lt with rfl | hd'
    · simp
    · exact mul_le_mul_of_nonneg_left (Real.log_le_log hd' (by linarith)) hd
  nlinarith

/-- `φ(x) ≤ φ(y) + (y − x)` for `0 ≤ x ≤ y ≤ 1`: the lower half of Lemma 3, from
`log(y/x) ≤ y/x − 1` and `log y ≤ 0` (the report uses concavity; this is more direct). -/
theorem negMulLog_le_negMulLog_add_sub (x y : ℝ) (hx : 0 ≤ x) (hxy : x ≤ y) (hy1 : y ≤ 1) :
    negMulLog x ≤ negMulLog y + (y - x) := by
  rcases hx.eq_or_lt with rfl | hx'
  · have := negMulLog_nonneg hxy hy1
    simp only [negMulLog_zero]
    linarith
  · have hy' : 0 < y := by linarith
    have hlog : Real.log (y / x) ≤ y / x - 1 := Real.log_le_sub_one_of_pos (div_pos hy' hx')
    rw [Real.log_div hy'.ne' hx'.ne'] at hlog
    have hly : Real.log y ≤ 0 := Real.log_nonpos hy'.le hy1
    have h2 : x * (Real.log y - Real.log x) ≤ y - x := by
      have h := mul_le_mul_of_nonneg_left hlog hx'.le
      have e : x * (y / x - 1) = y - x := by field_simp
      linarith
    simp only [negMulLog]
    nlinarith [mul_nonpos_of_nonneg_of_nonpos (sub_nonneg.2 hxy) hly]

/-- `φ` is monotone on `[0, 1/e]`: `φ(s) ≤ φ(d)` for `0 ≤ s ≤ d ≤ exp(−1)`. -/
theorem negMulLog_le_negMulLog_of_le (s d : ℝ) (hs : 0 ≤ s) (hsd : s ≤ d)
    (hd : d ≤ Real.exp (-1)) : negMulLog s ≤ negMulLog d := by
  have hd1 : d ≤ 1 := hd.trans (Real.exp_le_one_iff.2 (by norm_num))
  rcases hs.eq_or_lt with rfl | hs'
  · simpa using negMulLog_nonneg hsd hd1
  · have hd' : 0 < d := by linarith
    have hld : Real.log d ≤ -1 := by
      have := Real.log_le_log hd' hd
      rwa [Real.log_exp] at this
    have hlog : Real.log (d / s) ≤ d / s - 1 := Real.log_le_sub_one_of_pos (div_pos hd' hs')
    rw [Real.log_div hd'.ne' hs'.ne'] at hlog
    have h2 : s * (Real.log d - Real.log s) ≤ d - s := by
      have h := mul_le_mul_of_nonneg_left hlog hs'.le
      have e : s * (d / s - 1) = d - s := by field_simp
      linarith
    simp only [negMulLog]
    nlinarith [mul_nonpos_of_nonneg_of_nonpos (sub_nonneg.2 hsd) (by linarith : 1 + Real.log d ≤ 0)]

/-- `d ≤ φ(d)` for `0 ≤ d ≤ exp(−1)`: `−log d ≥ 1`. -/
theorem le_negMulLog (d : ℝ) (hd0 : 0 ≤ d) (hd : d ≤ Real.exp (-1)) : d ≤ negMulLog d := by
  rcases hd0.eq_or_lt with rfl | hd'
  · simp
  · have hld : Real.log d ≤ -1 := by
      have := Real.log_le_log hd' hd
      rwa [Real.log_exp] at this
    simp only [negMulLog]
    nlinarith [mul_nonneg hd'.le (by linarith : 0 ≤ -Real.log d - 1)]

/-- **Lemma 3 of the report (the shift lemma), in the form the assembly uses**: for
`x ∈ [0, 1]`, `y ≥ 0` with `|y − x| ≤ d ≤ 1/e`, `φ(y) ≤ φ(x) + φ(d)`. -/
theorem negMulLog_le_add_of_abs_sub_le {x y d : ℝ} (hx0 : 0 ≤ x) (hx1 : x ≤ 1) (hy0 : 0 ≤ y)
    (hxy : |y - x| ≤ d) (hd : d ≤ Real.exp (-1)) :
    negMulLog y ≤ negMulLog x + negMulLog d := by
  have hd0 : 0 ≤ d := (abs_nonneg _).trans hxy
  rcases le_or_gt x y with h | h
  · have h1 : negMulLog y ≤ negMulLog x + negMulLog (y - x) := by
      simpa using negMulLog_add_le x (y - x) hx0 (by linarith)
    have h2 : negMulLog (y - x) ≤ negMulLog d :=
      negMulLog_le_negMulLog_of_le _ _ (by linarith)
        (by rw [abs_of_nonneg (by linarith)] at hxy; exact hxy) hd
    linarith
  · have h1 := negMulLog_le_negMulLog_add_sub y x hy0 h.le hx1
    have h2 : x - y ≤ d := by rw [abs_of_neg (by linarith)] at hxy; linarith
    have h3 := le_negMulLog d hd0 hd
    linarith

/-- `φ(1/n) = (log n)/n`. -/
theorem negMulLog_one_div_natCast (n : ℕ) : negMulLog (1 / (n : ℝ)) = Real.log n / n := by
  simp only [negMulLog]
  rw [one_div, Real.log_inv]
  ring

/-- `1/n ≤ 1/e` for `n ≥ 3`, from `e < 2.7182818286` (`Real.exp_one_lt_d9`). -/
theorem one_div_le_exp_neg_one (n : ℕ) (hn : 3 ≤ n) : (1 : ℝ) / n ≤ Real.exp (-1) := by
  have h3 : (3 : ℝ) ≤ n := by exact_mod_cast hn
  have he : Real.exp 1 < 3 := lt_trans Real.exp_one_lt_d9 (by norm_num)
  rw [Real.exp_neg, one_div]
  exact inv_anti₀ (Real.exp_pos 1) (he.le.trans h3)

/-- `|x/n − y| ≤ 1/n` when `x − y n` and `y n − x` are both at most `1`. -/
theorem abs_div_sub_le_one_div {x y n : ℝ} (hn : 0 < n) (h1 : x - y * n ≤ 1)
    (h2 : y * n - x ≤ 1) : |x / n - y| ≤ 1 / n := by
  have e1 : x / n - y = (x - y * n) / n := by field_simp
  have e2 : y - x / n = (y * n - x) / n := by field_simp
  rw [abs_sub_le_iff, e1, e2]
  exact ⟨div_le_div_of_nonneg_right h1 hn.le, div_le_div_of_nonneg_right h2 hn.le⟩

/-! ### (I4) The rounding of `t` -/

/-- **Lemma 4 of the report**: with `k = ⌊βn⌋₊` and `t = (n − k + 1)/2`, for `0 ≤ β < 1` and
`n ≥ 1`: `k < n`, `1 ≤ t`, `2t ≤ n + 1`, and `a n ≤ t < a n + 1` where `a = (1 − β)/2`. -/
theorem rounding_t (β : ℝ) (hβ0 : 0 ≤ β) (hβ1 : β < 1) (n k t : ℕ) (hn : 0 < n)
    (hk : k = ⌊β * n⌋₊) (ht : t = (n - k + 1) / 2) :
    k < n ∧ 1 ≤ t ∧ 2 * t ≤ n + 1 ∧ (1 - β) / 2 * n ≤ (t : ℝ) ∧
      (t : ℝ) < (1 - β) / 2 * n + 1 := by
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn
  have hk1 : (k : ℝ) ≤ β * n := by rw [hk]; exact Nat.floor_le (by positivity)
  have hk2 : β * n < k + 1 := by rw [hk]; exact Nat.lt_floor_add_one _
  have hkn : k < n := by
    have : (k : ℝ) < n := by nlinarith
    exact_mod_cast this
  have ht1 : 1 ≤ t := by omega
  have ht2 : 2 * t ≤ n + 1 := by omega
  have ht3 : n - k ≤ 2 * t := by omega
  have ht4 : 2 * t ≤ n - k + 1 := by omega
  refine ⟨hkn, ht1, ht2, ?_, ?_⟩
  · have h : ((n - k : ℕ) : ℝ) ≤ ((2 * t : ℕ) : ℝ) := by exact_mod_cast ht3
    rw [Nat.cast_sub hkn.le] at h
    push_cast at h
    linarith
  · have h : ((2 * t : ℕ) : ℝ) ≤ ((n - k + 1 : ℕ) : ℝ) := by exact_mod_cast ht4
    rw [Nat.cast_add, Nat.cast_sub hkn.le] at h
    push_cast at h
    linarith

/-! ### Theorem A -/

/-- **The exponential rate of Theorem A**: `δ(β, c) = c a² − H(a, a, 1 − 2a)` with `a = (1 − β)/2`
and `H(x, y, z) = φ(x) + φ(y) + φ(z)` the trinomial entropy in nats, `φ = negMulLog`. -/
noncomputable def firstMomentRate (c β : ℝ) : ℝ :=
  c * ((1 - β) / 2) ^ 2 -
    (2 * negMulLog ((1 - β) / 2) + negMulLog (1 - 2 * ((1 - β) / 2)))

theorem firstMomentRate_def (c β : ℝ) :
    firstMomentRate c β = c * ((1 - β) / 2) ^ 2 -
      (2 * negMulLog ((1 - β) / 2) + negMulLog (1 - 2 * ((1 - β) / 2))) := rfl

open scoped Classical in
/-- **Theorem A (finite form)**, on any finite vertex type with `n = |V| ≥ max(3, c)`: for
`c > 0`, `0 < β < 1`, `a = (1 − β)/2`,
`P(pathwidth(G(n, c/n)) ≤ ⌊βn⌋) ≤ exp(−δ(β, c)·n + 3 log n + c·a)`,
the probability written as the `gnpWeight`-sum over `graphsOfPathwidthLe ⌊βn⌋₊`. -/
theorem firstMoment_pathwidth_le {V : Type*} [Fintype V] [DecidableEq V] (c β : ℝ) (hc : 0 < c)
    (hβ0 : 0 < β) (hβ1 : β < 1) (hn3 : 3 ≤ Fintype.card V) (hnc : c ≤ Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) ⌊β * Fintype.card V⌋₊,
        gnpWeight (c / Fintype.card V) G ≤
      Real.exp (-firstMomentRate c β * Fintype.card V + 3 * Real.log (Fintype.card V) +
        c * ((1 - β) / 2)) := by
  set n := Fintype.card V with hn
  set k := ⌊β * n⌋₊ with hk
  set t := (n - k + 1) / 2 with ht
  set a : ℝ := (1 - β) / 2 with ha
  have hn0 : 0 < n := by omega
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn0
  obtain ⟨hkn, ht1, ht2, htlo, hthi⟩ := rounding_t β hβ0.le hβ1 n k t hn0 hk ht
  rw [← ha] at htlo hthi
  set p : ℝ := c / n with hp
  have hp0 : 0 ≤ p := by positivity
  have hp1 : p ≤ 1 := by rw [hp, div_le_one hnR]; exact hnc
  -- (0): the proved first-moment inequality
  have h0 := weightedSum_graphsOfPathwidthLe_le (V := V) p hp0 hp1 k hkn
  rw [← hn, ← ht] at h0
  -- (I1): the entropy bound on the trinomial
  have hI1 := choose_mul_choose_le_exp_entropy n t (t - 1) (by omega)
  -- the three types are within `1/n` of `(a, a, 1 − 2a)`
  have ha0 : 0 ≤ a := by rw [ha]; linarith
  have ha1 : a ≤ 1 := by rw [ha]; linarith
  have hb0 : 0 ≤ 1 - 2 * a := by rw [ha]; linarith
  have hb1 : 1 - 2 * a ≤ 1 := by rw [ha]; linarith
  have hd : (1 : ℝ) / n ≤ Real.exp (-1) := one_div_le_exp_neg_one n hn3
  have htR : (1 : ℝ) ≤ t := by exact_mod_cast ht1
  have ht2R : 2 * (t : ℝ) ≤ n + 1 := by exact_mod_cast ht2
  have hcast1 : ((t - 1 : ℕ) : ℝ) = (t : ℝ) - 1 := by rw [Nat.cast_sub ht1, Nat.cast_one]
  have hcast2 : ((n - t - (t - 1) : ℕ) : ℝ) = (n : ℝ) - t - ((t : ℝ) - 1) := by
    rw [Nat.cast_sub (by omega), Nat.cast_sub (by omega), hcast1]
  have hu := negMulLog_le_add_of_abs_sub_le ha0 ha1 (y := (t : ℝ) / n) (by positivity)
    (abs_div_sub_le_one_div hnR (by linarith) (by linarith)) hd
  have hv := negMulLog_le_add_of_abs_sub_le ha0 ha1 (y := ((t - 1 : ℕ) : ℝ) / n)
    (by positivity) (by rw [hcast1]; exact abs_div_sub_le_one_div hnR (by linarith) (by linarith))
    hd
  have hw := negMulLog_le_add_of_abs_sub_le hb0 hb1 (y := ((n - t - (t - 1) : ℕ) : ℝ) / n)
    (by positivity)
    (by rw [hcast2]; exact abs_div_sub_le_one_div hnR (by linarith) (by linarith)) hd
  rw [negMulLog_one_div_natCast] at hu hv hw
  -- (2): the trinomial is at most `exp(n H(a, a, 1 − 2a) + 3 log n)`
  have h2 : ((n.choose t * (n - t).choose (t - 1) : ℕ) : ℝ) ≤
      Real.exp (n * (2 * negMulLog a + negMulLog (1 - 2 * a)) + 3 * Real.log n) := by
    refine hI1.trans (Real.exp_le_exp.2 ?_)
    have hsum : negMulLog ((t : ℝ) / n) + negMulLog (((t - 1 : ℕ) : ℝ) / n) +
        negMulLog (((n - t - (t - 1) : ℕ) : ℝ) / n) ≤
        2 * negMulLog a + negMulLog (1 - 2 * a) + 3 * (Real.log n / n) := by linarith
    have := mul_le_mul_of_nonneg_left hsum hnR.le
    have e : (n : ℝ) * (2 * negMulLog a + negMulLog (1 - 2 * a) + 3 * (Real.log n / n)) =
        n * (2 * negMulLog a + negMulLog (1 - 2 * a)) + 3 * Real.log n := by
      field_simp
    linarith
  -- (3): `(1 − p)^(t(t−1)) ≤ exp(−c a² n + c a)`, by (I2) and (I4)
  have h3 : (1 - p) ^ (t * (t - 1)) ≤ Real.exp (-(c * a ^ 2 * n - c * a)) := by
    refine (one_sub_pow_le_exp_neg_mul p hp1 _).trans (Real.exp_le_exp.2 ?_)
    have hm : ((t * (t - 1) : ℕ) : ℝ) = (t : ℝ) * ((t : ℝ) - 1) := by
      rw [Nat.cast_mul, hcast1]
    rw [hm, hp]
    have hprod : a ^ 2 * n ^ 2 - a * n ≤ (t : ℝ) * ((t : ℝ) - 1) := by
      nlinarith [mul_nonneg (sub_nonneg.2 htlo) (by linarith : (0 : ℝ) ≤ (t : ℝ) + a * n - 1)]
    have e : c / n * (a ^ 2 * n ^ 2 - a * n) = c * a ^ 2 * n - c * a := by
      field_simp
    have := mul_le_mul_of_nonneg_left hprod (by positivity : (0 : ℝ) ≤ c / n)
    linarith
  -- assembly: (0) × (2) × (3)
  calc ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G
      ≤ ((n.choose t * (n - t).choose (t - 1) : ℕ) : ℝ) * (1 - p) ^ (t * (t - 1)) := h0
    _ ≤ Real.exp (n * (2 * negMulLog a + negMulLog (1 - 2 * a)) + 3 * Real.log n) *
          Real.exp (-(c * a ^ 2 * n - c * a)) :=
        mul_le_mul h2 h3 (by positivity) (Real.exp_pos _).le
    _ = Real.exp (-firstMomentRate c β * n + 3 * Real.log n + c * a) := by
        rw [← Real.exp_add, firstMomentRate_def, ← ha]
        ring_nf

open scoped Classical in
/-- **Theorem A (finite form) on `Fin n`**: for `c > 0`, `0 < β < 1`, `n ≥ 3`, `c ≤ n`,
`P(pathwidth(G(n, c/n)) ≤ ⌊βn⌋) ≤ exp(−δ(β, c)·n + 3 log n + c·(1 − β)/2)`. -/
theorem firstMoment_pathwidth_le_fin (c β : ℝ) (hc : 0 < c) (hβ0 : 0 < β) (hβ1 : β < 1)
    (n : ℕ) (hn3 : 3 ≤ n) (hnc : c ≤ n) :
    ∑ G ∈ graphsOfPathwidthLe (V := Fin n) ⌊β * n⌋₊, gnpWeight (c / n) G ≤
      Real.exp (-firstMomentRate c β * n + 3 * Real.log n + c * ((1 - β) / 2)) := by
  have h := firstMoment_pathwidth_le (V := Fin n) c β hc hβ0 hβ1 (by simpa using hn3)
    (by simpa using hnc)
  simpa using h

/-- `exp(−δ n + 3 log n + c a) = exp(c a) · n³ · exp(−δ n)` for `n > 0`. -/
theorem exp_bound_eq (δ c a : ℝ) (n : ℕ) (hn : 0 < n) :
    Real.exp (-δ * n + 3 * Real.log n + c * a) =
      Real.exp (c * a) * (n : ℝ) ^ 3 * Real.exp (-δ * n) := by
  have hnR : (0 : ℝ) < n := by exact_mod_cast hn
  have h3 : Real.exp (3 * Real.log n) = (n : ℝ) ^ 3 := by
    rw [show (3 : ℝ) * Real.log n = Real.log ((n : ℝ) ^ 3) by rw [Real.log_pow]; norm_num]
    exact Real.exp_log (by positivity)
  rw [show -δ * n + 3 * Real.log n + c * a = c * a + 3 * Real.log n + -δ * n by ring,
    Real.exp_add, Real.exp_add, h3]

open scoped Classical in
/-- **Theorem A, second form**: `P(pathwidth(G(n, c/n)) ≤ ⌊βn⌋) ≤ e^(c/2) · n³ · e^(−δ(β, c)·n)`. -/
theorem firstMoment_pathwidth_le_fin' (c β : ℝ) (hc : 0 < c) (hβ0 : 0 < β) (hβ1 : β < 1)
    (n : ℕ) (hn3 : 3 ≤ n) (hnc : c ≤ n) :
    ∑ G ∈ graphsOfPathwidthLe (V := Fin n) ⌊β * n⌋₊, gnpWeight (c / n) G ≤
      Real.exp (c / 2) * (n : ℝ) ^ 3 * Real.exp (-firstMomentRate c β * n) := by
  refine (firstMoment_pathwidth_le_fin c β hc hβ0 hβ1 n hn3 hnc).trans ?_
  rw [exp_bound_eq _ _ _ n (by omega)]
  have ha : c * ((1 - β) / 2) ≤ c / 2 := by nlinarith [mul_pos hc hβ0]
  have hn0 : (0 : ℝ) ≤ (n : ℝ) ^ 3 := by positivity
  exact mul_le_mul_of_nonneg_right
    (mul_le_mul_of_nonneg_right (Real.exp_le_exp.2 ha) hn0) (Real.exp_pos _).le

/-- The bound of Theorem A tends to `0` when `δ(β, c) > 0`: `n³ e^(−δn) → 0`. -/
theorem tendsto_firstMoment_bound (c β : ℝ) (hδ : 0 < firstMomentRate c β) :
    Filter.Tendsto (fun n : ℕ =>
      Real.exp (c / 2) * (n : ℝ) ^ 3 * Real.exp (-firstMomentRate c β * n))
      Filter.atTop (nhds 0) := by
  set δ := firstMomentRate c β with hδdef
  have h1 : Filter.Tendsto (fun n : ℕ => δ * (n : ℝ)) Filter.atTop Filter.atTop :=
    Filter.Tendsto.const_mul_atTop hδ tendsto_natCast_atTop_atTop
  have h2 := (tendsto_pow_mul_exp_neg_atTop_nhds_zero 3).comp h1
  have h3 := h2.const_mul (Real.exp (c / 2) * δ⁻¹ ^ 3)
  rw [mul_zero] at h3
  refine h3.congr (fun n => ?_)
  simp only [Function.comp]
  have hδ0 : δ ≠ 0 := hδ.ne'
  field_simp

open scoped Classical in
/-- **Theorem A′'s consequence**: for `c > 0`, `0 < β < 1` with `δ(β, c) > 0`,
`P(pathwidth(G(n, c/n)) ≤ ⌊βn⌋) → 0` as `n → ∞`, i.e. `pathwidth(G(n, c/n)) > βn` with
probability `1 − o(1)`. (That `δ(β, c) > 0` holds exactly for `β < β*(c)`, `c > 4 log 2`, is
Theorem A′ itself and is not formalised here.) -/
theorem tendsto_firstMoment_pathwidth (c β : ℝ) (hc : 0 < c) (hβ0 : 0 < β) (hβ1 : β < 1)
    (hδ : 0 < firstMomentRate c β) :
    Filter.Tendsto (fun n : ℕ =>
      ∑ G ∈ graphsOfPathwidthLe (V := Fin n) ⌊β * n⌋₊, gnpWeight (c / n) G)
      Filter.atTop (nhds 0) := by
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' tendsto_const_nhds
    (tendsto_firstMoment_bound c β hδ) ?_ ?_
  · filter_upwards [Filter.eventually_ge_atTop ⌈c⌉₊] with n hn
    have hcn : c ≤ n := (Nat.le_ceil c).trans (by exact_mod_cast hn)
    have hnR : (0 : ℝ) < n := lt_of_lt_of_le hc hcn
    exact Finset.sum_nonneg (fun G _ =>
      gnpWeight_nonneg (by positivity) ((div_le_one hnR).2 hcn) G)
  · filter_upwards [Filter.eventually_ge_atTop ⌈c⌉₊, Filter.eventually_ge_atTop 3] with n hn hn3
    have hcn : c ≤ n := (Nat.le_ceil c).trans (by exact_mod_cast hn)
    exact firstMoment_pathwidth_le_fin' c β hc hβ0 hβ1 n hn3 hcn

end MOSPFormalization
