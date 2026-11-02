/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The Edwards–McDermid weights `g = g_{1/6}` and `g'`

Edwards & McDermid, *A general reduction theorem with applications to pathwidth and the
complexity of MAX 2-CSP*, Algorithmica 72 (2015), Section 3.1 (p. 6–7) and Appendix
(Lemmas 8.1, 8.3, 8.4, 8.5). This is item 03 of loop0012 (`reports/edwards_mcdermid_plan.md`
§0.5; `reports/edwards_mcdermid.md` §3): the weight function the degree-sequence bound on
pathwidth is built from, with every property the reduction theorem (items 05–08) uses.

* `g 0 = g 1 = g 2 = 0`, `g 3 = 1/6`, and `n g n = (n − 2) g (n − 1) + g (n − 2) + 1` for
  `n ≥ 4` (`g_recurrence`); the table `1/6, 1/3, 13/30, 23/45, 359/630, 1553/2520,
  14827/22680` at `n = 3..9` (`g_four` … `g_nine`, the paper's table p. 7 to `d = 8`).
* `g' n = g n − g (n − 1)` (natural subtraction, so `g' 0 = 0`); `g' d = 0` for `d ≤ 2`.
* Lemma 8.3 (`g_monotone`): `g` is non-decreasing, by the coupled invariant
  `0 ≤ g n ≤ g (n + 1) ≤ (1 + g n) / 2`, `g n < 1` (`g_aux`); hence `g_nonneg`, `g_lt_one`.
* Lemma 8.4 (`g'_antitone_of_three_le`): `g'` is non-increasing from 3, by the recurrence
  `n g' n = (n − 3) g' (n − 1) + g' (n − 2)` for `n ≥ 5` (`g'_recurrence`) and the sandwich
  `g' n / 3 ≤ g' (n + 1) ≤ g' n` (`g'_aux`); hence `g'_le_sixth`.
* Property 6 (`one_sub_g_eq`): `1 − g n = (n − 1) g' n + g' (n − 1)` for `n ≥ 4`.
* `g'_nonneg`, `g'_le_g`; Lemma 8.1 (`g_closed_form`): `g n = (7/2) A n / n! + (3/2) (−1)^n / n! − 5/2`
  for `n ≥ 2`, `A` the alternating factorial; Lemma 8.5 (`g_div_lt_g_div`): `g n / n` is
  strictly decreasing from `n = 5`.

Only `α = 1/6` is formalised (plan §0.5). Every statement was checked in exact rationals to
`n = 200` before it was stated (`reports/scratch/edwards_mcdermid/03_weights/check.py`).
-/
import Mathlib.Tactic

namespace MOSPFormalization.DegreeBound

/-- The Edwards–McDermid weight `g_{1/6}`: `g 0 = g 1 = g 2 = 0`, `g 3 = 1/6`, and
`n g n = (n − 2) g (n − 1) + g (n − 2) + 1` for `n ≥ 4` (p. 6). -/
def g : ℕ → ℚ
  | 0 => 0
  | 1 => 0
  | 2 => 0
  | 3 => 1 / 6
  | n + 4 => (((n : ℚ) + 2) * g (n + 3) + g (n + 2) + 1) / ((n : ℚ) + 4)

/-- `g' n = g n − g (n − 1)`, the marginal weight of one more edge at a vertex (p. 7). -/
def g' (n : ℕ) : ℚ := g n - g (n - 1)

@[simp] theorem g_zero : g 0 = 0 := rfl
@[simp] theorem g_one : g 1 = 0 := rfl
@[simp] theorem g_two : g 2 = 0 := rfl
@[simp] theorem g_three : g 3 = 1 / 6 := rfl

/-- The defining recurrence in shifted form. -/
theorem g_add_four (n : ℕ) :
    g (n + 4) = (((n : ℚ) + 2) * g (n + 3) + g (n + 2) + 1) / ((n : ℚ) + 4) := by
  rw [g]

/-- The defining recurrence, multiplied out. -/
theorem g_add_four_mul (n : ℕ) :
    ((n : ℚ) + 4) * g (n + 4) = ((n : ℚ) + 2) * g (n + 3) + g (n + 2) + 1 := by
  rw [g_add_four, mul_div_cancel₀]
  positivity

/-- W1: `n g n = (n − 2) g (n − 1) + g (n − 2) + 1` for `n ≥ 4` (p. 6). -/
theorem g_recurrence {n : ℕ} (hn : 4 ≤ n) :
    (n : ℚ) * g n = ((n : ℚ) - 2) * g (n - 1) + g (n - 2) + 1 := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 4 := ⟨n - 4, by omega⟩
  have h1 : m + 4 - 1 = m + 3 := by omega
  have h2 : m + 4 - 2 = m + 2 := by omega
  rw [h1, h2]
  push_cast
  have := g_add_four_mul m
  linear_combination this

theorem g_four : g 4 = 1 / 3 := by norm_num [g_add_four]
theorem g_five : g 5 = 13 / 30 := by norm_num [g_add_four]
theorem g_six : g 6 = 23 / 45 := by norm_num [g_add_four]
theorem g_seven : g 7 = 359 / 630 := by norm_num [g_add_four]
theorem g_eight : g 8 = 1553 / 2520 := by norm_num [g_add_four]
theorem g_nine : g 9 = 14827 / 22680 := by norm_num [g_add_four]

/-- The table of `g` to `d = 9` in one statement (the paper's table p. 7 runs to 8). -/
theorem g_table :
    g 3 = 1 / 6 ∧ g 4 = 1 / 3 ∧ g 5 = 13 / 30 ∧ g 6 = 23 / 45 ∧ g 7 = 359 / 630 ∧
      g 8 = 1553 / 2520 ∧ g 9 = 14827 / 22680 :=
  ⟨g_three, g_four, g_five, g_six, g_seven, g_eight, g_nine⟩

/-- The coupled invariant of Lemma 8.3, with the bound `g n < 1` it needs:
`0 ≤ g n ≤ g (n + 1) ≤ (1 + g n) / 2` and `g n < 1`. -/
theorem g_aux (n : ℕ) :
    0 ≤ g n ∧ g n ≤ g (n + 1) ∧ g (n + 1) ≤ (1 + g n) / 2 ∧ g n < 1 := by
  induction n with
  | zero => norm_num
  | succ n ih =>
    obtain ⟨h0, h1, h2, h3⟩ := ih
    have h4 : g (n + 1) < 1 := by linarith
    refine ⟨le_trans h0 h1, ?_, ?_, h4⟩
    · -- `g (n + 1) ≤ g (n + 2)`
      rcases n with _ | _ | m
      · norm_num [g_four]
      · norm_num [g_four, g_five]
      · have hrec := g_add_four_mul m
        have hpos : (0 : ℚ) < (m : ℚ) + 4 := by positivity
        -- `(m + 4) (g (m + 4) − g (m + 3)) = 1 + g (m + 2) − 2 g (m + 3) ≥ 0`
        have : ((m : ℚ) + 4) * (g (m + 2 + 1 + 1) - g (m + 2 + 1)) ≥ 0 := by
          have e : ((m : ℚ) + 4) * (g (m + 2 + 1 + 1) - g (m + 2 + 1)) =
              1 + g (m + 2) - 2 * g (m + 3) := by
            show ((m : ℚ) + 4) * (g (m + 4) - g (m + 3)) = 1 + g (m + 2) - 2 * g (m + 3)
            linear_combination hrec
          rw [e]; linarith
        exact sub_nonneg.mp ((mul_nonneg_iff_of_pos_left hpos).mp this)
    · -- `g (n + 2) ≤ (1 + g (n + 1)) / 2`
      rcases n with _ | _ | m
      · norm_num [g_four]
      · norm_num [g_four, g_five]
      · have hrec := g_add_four_mul m
        have hpos : (0 : ℚ) < (m : ℚ) + 4 := by positivity
        have hm : (0 : ℚ) ≤ m := Nat.cast_nonneg m
        -- `(m + 4) ((1 + g (m + 3)) / 2 − g (m + 4)) = (m + 2 − m g (m + 3) − 2 g (m + 2)) / 2 ≥ 0`
        have : ((m : ℚ) + 4) * ((1 + g (m + 2 + 1)) / 2 - g (m + 2 + 1 + 1)) ≥ 0 := by
          have e : ((m : ℚ) + 4) * ((1 + g (m + 2 + 1)) / 2 - g (m + 2 + 1 + 1)) =
              ((m : ℚ) + 2 - (m : ℚ) * g (m + 3) - 2 * g (m + 2)) / 2 := by
            show ((m : ℚ) + 4) * ((1 + g (m + 3)) / 2 - g (m + 4)) =
              ((m : ℚ) + 2 - (m : ℚ) * g (m + 3) - 2 * g (m + 2)) / 2
            linear_combination (-1 : ℚ) * hrec
          rw [e]
          have : (m : ℚ) * g (m + 3) ≤ m := by
            have := mul_le_mul_of_nonneg_left h4.le hm
            simpa using this
          linarith
        exact sub_nonneg.mp ((mul_nonneg_iff_of_pos_left hpos).mp this)

/-- W5a: `0 ≤ g n`. -/
theorem g_nonneg (n : ℕ) : 0 ≤ g n := (g_aux n).1

/-- W5a: `g n < 1`. -/
theorem g_lt_one (n : ℕ) : g n < 1 := (g_aux n).2.2.2

theorem g_le_succ (n : ℕ) : g n ≤ g (n + 1) := (g_aux n).2.1

/-- W2, Lemma 8.3: `g` is non-decreasing. -/
theorem g_monotone : Monotone g := monotone_nat_of_le_succ g_le_succ

theorem g'_succ (n : ℕ) : g' (n + 1) = g (n + 1) - g n := by simp [g']

@[simp] theorem g'_zero : g' 0 = 0 := by simp [g']
@[simp] theorem g'_one : g' 1 = 0 := by simp [g']
@[simp] theorem g'_two : g' 2 = 0 := by simp [g']
theorem g'_three : g' 3 = 1 / 6 := by simp [g']
theorem g'_four : g' 4 = 1 / 6 := by rw [g'_succ, g_four, g_three]; norm_num
theorem g'_five : g' 5 = 1 / 10 := by rw [g'_succ, g_five, g_four]; norm_num
theorem g'_six : g' 6 = 7 / 90 := by rw [g'_succ, g_six, g_five]; norm_num
theorem g'_seven : g' 7 = 37 / 630 := by rw [g'_succ, g_seven, g_six]; norm_num
theorem g'_eight : g' 8 = 13 / 280 := by rw [g'_succ, g_eight, g_seven]; norm_num

/-- `g' d = 0` for `d ≤ 2`: the removed (isolated) vertices and the degrees the reduction
never leaves standing carry no marginal weight. -/
theorem g'_eq_zero_of_le_two {n : ℕ} (hn : n ≤ 2) : g' n = 0 := by
  interval_cases n <;> simp

/-- W5b: `0 ≤ g' n`. -/
theorem g'_nonneg (n : ℕ) : 0 ≤ g' n := by
  unfold g'
  exact sub_nonneg.mpr (g_monotone (Nat.sub_le n 1))

/-- `g' n ≤ g n` (used by the `j₄` lemma, item 07). -/
theorem g'_le_g (n : ℕ) : g' n ≤ g n := by
  unfold g'
  linarith [g_nonneg (n - 1)]

/-- The recurrence for `g'` in shifted form: `(m + 5) g' (m + 5) = (m + 2) g' (m + 4) + g' (m + 3)`. -/
theorem g'_add_five_mul (m : ℕ) :
    ((m : ℚ) + 5) * g' (m + 5) = ((m : ℚ) + 2) * g' (m + 4) + g' (m + 3) := by
  have h5 : g' (m + 5) = g (m + 5) - g (m + 4) := g'_succ (m + 4)
  have h4 : g' (m + 4) = g (m + 4) - g (m + 3) := g'_succ (m + 3)
  have h3 : g' (m + 3) = g (m + 3) - g (m + 2) := g'_succ (m + 2)
  rw [h5, h4, h3]
  have r1 := g_add_four_mul (m + 1)
  have r0 := g_add_four_mul m
  push_cast at r1
  have e1 : (m + 1 + 4 : ℕ) = m + 5 := by omega
  have e2 : (m + 1 + 3 : ℕ) = m + 4 := by omega
  have e3 : (m + 1 + 2 : ℕ) = m + 3 := by omega
  rw [e1, e2, e3] at r1
  linear_combination r1 - r0

/-- `n g' n = (n − 3) g' (n − 1) + g' (n − 2)` for `n ≥ 5` (the step of Lemma 8.4). -/
theorem g'_recurrence {n : ℕ} (hn : 5 ≤ n) :
    (n : ℚ) * g' n = ((n : ℚ) - 3) * g' (n - 1) + g' (n - 2) := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 5 := ⟨n - 5, by omega⟩
  have h1 : m + 5 - 1 = m + 4 := by omega
  have h2 : m + 5 - 2 = m + 3 := by omega
  rw [h1, h2]
  push_cast
  have := g'_add_five_mul m
  linear_combination this

/-- The sandwich of Lemma 8.4: for `n ≥ 3`, `g' n / 3 ≤ g' (n + 1) ≤ g' n`. -/
theorem g'_aux {n : ℕ} (hn : 3 ≤ n) : g' (n + 1) ≤ g' n ∧ g' n / 3 ≤ g' (n + 1) := by
  induction n, hn using Nat.le_induction with
  | base => rw [g'_four, g'_three]; norm_num
  | succ n hn ih =>
    obtain ⟨h1, h2⟩ := ih
    obtain ⟨m, rfl⟩ : ∃ m, n = m + 3 := ⟨n - 3, by omega⟩
    have hrec := g'_add_five_mul m
    have hb := g'_nonneg (m + 4)
    have ha := g'_nonneg (m + 3)
    have hpos : (0 : ℚ) < (m : ℚ) + 5 := by positivity
    have hm : (0 : ℚ) ≤ m := Nat.cast_nonneg m
    constructor
    · -- `(m + 5) (g' (m + 4) − g' (m + 5)) = 3 g' (m + 4) − g' (m + 3) ≥ 0`
      have : ((m : ℚ) + 5) * (g' (m + 3 + 1) - g' (m + 3 + 1 + 1)) ≥ 0 := by
        have e : ((m : ℚ) + 5) * (g' (m + 3 + 1) - g' (m + 3 + 1 + 1)) =
            3 * g' (m + 4) - g' (m + 3) := by
          show ((m : ℚ) + 5) * (g' (m + 4) - g' (m + 5)) = 3 * g' (m + 4) - g' (m + 3)
          linear_combination -hrec
        rw [e]; linarith
      exact sub_nonneg.mp ((mul_nonneg_iff_of_pos_left hpos).mp this)
    · -- `(m + 5) (g' (m + 5) − g' (m + 4) / 3) = (2m + 1) g' (m + 4) / 3 + g' (m + 3) ≥ 0`
      have : ((m : ℚ) + 5) * (g' (m + 3 + 1 + 1) - g' (m + 3 + 1) / 3) ≥ 0 := by
        have e : ((m : ℚ) + 5) * (g' (m + 3 + 1 + 1) - g' (m + 3 + 1) / 3) =
            (2 * (m : ℚ) + 1) * g' (m + 4) / 3 + g' (m + 3) := by
          show ((m : ℚ) + 5) * (g' (m + 5) - g' (m + 4) / 3) =
            (2 * (m : ℚ) + 1) * g' (m + 4) / 3 + g' (m + 3)
          linear_combination hrec
        rw [e]
        have : 0 ≤ (2 * (m : ℚ) + 1) * g' (m + 4) := by positivity
        linarith
      exact sub_nonneg.mp ((mul_nonneg_iff_of_pos_left hpos).mp this)

theorem g'_succ_le {n : ℕ} (hn : 3 ≤ n) : g' (n + 1) ≤ g' n := (g'_aux hn).1

/-- W3, Lemma 8.4: `g'` is non-increasing from 3: `3 ≤ m ≤ n → g' n ≤ g' m`. -/
theorem g'_antitone_of_three_le {m n : ℕ} (hm : 3 ≤ m) (hmn : m ≤ n) : g' n ≤ g' m := by
  induction n, hmn using Nat.le_induction with
  | base => exact le_rfl
  | succ n hn ih => exact le_trans (g'_succ_le (le_trans hm hn)) ih

/-- W5b: `g' n ≤ 1/6` for every `n` (the maximum is at 3 and 4). -/
theorem g'_le_sixth (n : ℕ) : g' n ≤ 1 / 6 := by
  rcases Nat.lt_or_ge n 3 with h | h
  · rw [g'_eq_zero_of_le_two (Nat.lt_succ_iff.mp h)]; norm_num
  · calc g' n ≤ g' 3 := g'_antitone_of_three_le le_rfl h
      _ = 1 / 6 := g'_three

/-- W4, property 6 (p. 7): `1 − g n = (n − 1) g' n + g' (n − 1)` for `n ≥ 4`. -/
theorem one_sub_g_eq {n : ℕ} (hn : 4 ≤ n) :
    1 - g n = ((n : ℚ) - 1) * g' n + g' (n - 1) := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 4 := ⟨n - 4, by omega⟩
  have h1 : m + 4 - 1 = m + 3 := by omega
  rw [h1]
  have h4 : g' (m + 4) = g (m + 4) - g (m + 3) := g'_succ (m + 3)
  have h3 : g' (m + 3) = g (m + 3) - g (m + 2) := g'_succ (m + 2)
  rw [h4, h3]
  push_cast
  have := g_add_four_mul m
  linear_combination -this

/-! ### Lemma 8.1, the closed form, and Lemma 8.5 -/

/-- The alternating factorial `A n = n! − (n − 1)! + … ± 1!`, as `A 0 = 0`,
`A (n + 1) = (n + 1)! − A n` (so `A 1 = 1`, `A 2 = 1`, `A 3 = 5`). -/
def altFactorial : ℕ → ℚ
  | 0 => 0
  | n + 1 => ((n + 1).factorial : ℚ) - altFactorial n

@[simp] theorem altFactorial_zero : altFactorial 0 = 0 := rfl
theorem altFactorial_succ (n : ℕ) :
    altFactorial (n + 1) = ((n + 1).factorial : ℚ) - altFactorial n := rfl

/-- Lemma 8.1 at `α = 1/6`: `g n = (7/2) A n / n! + (3/2) (−1)^n / n! − 5/2` for `n ≥ 2`. -/
theorem g_closed_form {n : ℕ} (hn : 2 ≤ n) :
    g n = (7 / 2) * altFactorial n / (n.factorial : ℚ) +
      (3 / 2) * (-1) ^ n / (n.factorial : ℚ) - 5 / 2 := by
  -- two-step induction: the form holds at 2 and 3 and satisfies the recurrence
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    rcases n with _ | _ | _ | _ | m
    · omega
    · omega
    · norm_num [altFactorial_succ]
    · norm_num [altFactorial_succ, Nat.factorial]
    · have ih3 := ih (m + 3) (by omega) (by omega)
      have ih2 := ih (m + 2) (by omega) (by omega)
      rw [g_add_four, ih3, ih2]
      have f2 : (0 : ℚ) < ((m + 2).factorial : ℚ) := by positivity
      have f3 : ((m + 3).factorial : ℚ) = ((m : ℚ) + 3) * ((m + 2).factorial : ℚ) := by
        rw [Nat.factorial_succ]; push_cast; ring
      have f4 : ((m + 4).factorial : ℚ) = ((m : ℚ) + 4) * ((m : ℚ) + 3) * ((m + 2).factorial : ℚ) := by
        rw [Nat.factorial_succ]; push_cast; rw [f3]; ring
      have a3 : altFactorial (m + 3) = ((m : ℚ) + 3) * ((m + 2).factorial : ℚ) - altFactorial (m + 2) := by
        rw [altFactorial_succ, f3]
      have a4 : altFactorial (m + 4) =
          ((m : ℚ) + 4) * ((m : ℚ) + 3) * ((m + 2).factorial : ℚ) - altFactorial (m + 3) := by
        rw [altFactorial_succ, f4]
      rw [a4, a3, f4, f3]
      have s3 : ((-1 : ℚ)) ^ (m + 3) = -((-1) ^ (m + 2)) := by rw [pow_succ]; ring
      have s4 : ((-1 : ℚ)) ^ (m + 4) = (-1) ^ (m + 2) := by rw [pow_succ, pow_succ]; ring
      rw [s3, s4]
      have hm4 : ((m : ℚ) + 4) ≠ 0 := by positivity
      have hm3 : ((m : ℚ) + 3) ≠ 0 := by positivity
      have f2' : ((m + 2).factorial : ℚ) ≠ 0 := f2.ne'
      field_simp
      ring

/-- `g n ≥ 1/2` for `n ≥ 6` (from the table and monotonicity). -/
theorem half_le_g {n : ℕ} (hn : 6 ≤ n) : 1 / 2 ≤ g n :=
  le_trans (by rw [g_six]; norm_num) (g_monotone hn)

/-- Lemma 8.5 at `α = 1/6`: `g n / n` is strictly decreasing from `n = 5`:
`g (n + 1) / (n + 1) < g n / n` for `n ≥ 5`. (False at `n = 4`: `g 4 / 4 = 1/12 < 13/150 = g 5 / 5`.) -/
theorem g_div_lt_g_div {n : ℕ} (hn : 5 ≤ n) : g (n + 1) / ((n : ℚ) + 1) < g n / n := by
  rcases Nat.lt_or_ge n 6 with h | h
  · obtain rfl : n = 5 := by omega
    rw [g_six, g_five]; norm_num
  · obtain ⟨m, rfl⟩ : ∃ m, n = m + 6 := ⟨n - 6, by omega⟩
    have hpos : (0 : ℚ) < (m : ℚ) + 6 := by positivity
    have hpos' : (0 : ℚ) < (m : ℚ) + 6 + 1 := by positivity
    push_cast
    rw [div_lt_div_iff₀ hpos' hpos]
    -- `(m + 7) g (m + 7) = (m + 5) g (m + 6) + g (m + 5) + 1`
    have hrec := g_add_four_mul (m + 3)
    have e7 : (m + 3 + 4 : ℕ) = m + 7 := by omega
    have e6 : (m + 3 + 3 : ℕ) = m + 6 := by omega
    have e5 : (m + 3 + 2 : ℕ) = m + 5 := by omega
    rw [e7, e6, e5] at hrec
    push_cast at hrec
    have hmono : g (m + 5) ≤ g (m + 6) := g_le_succ (m + 5)
    have hhalf : 1 / 2 ≤ g (m + 6) := half_le_g (by omega)
    have hm : (0 : ℚ) ≤ m := Nat.cast_nonneg m
    -- want `(m + 6) g (m + 7) < (m + 7) g (m + 6)`; multiply by `m + 7 > 0`:
    -- `(m + 6) ((m + 5) g6 + g5 + 1) < (m + 7)² g6`, i.e. `(m + 6)(g5 + 1) < (2m + 13) g6`,
    -- and `g5 ≤ g6`, `g6 ≥ 1/2` give `(m + 6)(g6 + 1) ≤ (m + 6) g6 + (2m + 12) g6 < (2m + 13) g6`
    have h7 : (0 : ℚ) < (m : ℚ) + 7 := by positivity
    have key : ((m : ℚ) + 7) * (g (m + 6 + 1) * ((m : ℚ) + 6)) <
        ((m : ℚ) + 7) * (g (m + 6) * ((m : ℚ) + 6 + 1)) := by
      have : ((m : ℚ) + 7) * (g (m + 6 + 1) * ((m : ℚ) + 6)) =
          ((m : ℚ) + 6) * (((m : ℚ) + 5) * g (m + 6) + g (m + 5) + 1) := by
        show ((m : ℚ) + 7) * (g (m + 7) * ((m : ℚ) + 6)) =
          ((m : ℚ) + 6) * (((m : ℚ) + 5) * g (m + 6) + g (m + 5) + 1)
        linear_combination ((m : ℚ) + 6) * hrec
      rw [this]
      nlinarith [mul_le_mul_of_nonneg_left hmono (by positivity : (0 : ℚ) ≤ (m : ℚ) + 6),
        mul_le_mul_of_nonneg_left hhalf (by positivity : (0 : ℚ) ≤ 2 * (m : ℚ) + 12)]
    exact lt_of_mul_lt_mul_left key h7.le

end MOSPFormalization.DegreeBound
