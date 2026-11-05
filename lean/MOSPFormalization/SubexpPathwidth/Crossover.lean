/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The crossover: counting beats the width dynamic programs at linear pathwidth

Item 06 of loop0014 (`reports/subexp_pathwidth.md` §6). Two things, both over the frame of
`Frame.lean`:

1. **The independent-set algorithm, as a consequence of the counting hypothesis.** `indepCNF G`
   is the formula of the ETH paper's Corollary 1.3: one Boolean variable per vertex and the clause
   `¬x_u ∨ ¬x_w` per edge. `indepCNF_width` (width `≤ 2`), `indepCNF_eval_iff` (its models are
   the independent sets) and `count_indepCNF` (`SAT.count (indepCNF G) = indepCount G`, the number
   of independent sets) are the encoding's correctness; `indepCount_subexp` is the algorithm:
   under `SubexpCount 2`, one primitive machine writes the number of independent sets of every
   graph `G` on `n` vertices on its count tape, on the input `encodeCNF (indepCNF G)`, within
   `C (L + 1)^d · 2^(A · ρ(n))` steps, `L` the formula's bit length — and the exponent
   `A · ρ(n)` is `o(n)` in the number of vertices (`isSubexpExponent_runtimeScale`). Nothing is
   asserted: the theorem is `SubexpCount 2 → …`.

2. **The `q`-colouring algorithm, likewise.** `coloringCNF G q` is Corollary 1.3's second
   formula on the variables `Fin (n * q)` (`colVar v c = finProdFinEquiv (v, c)`): one clause
   `⋁_c x_{v,c}` per vertex, `¬x_{v,c} ∨ ¬x_{v,c'}` for `c ≠ c'`, and `¬x_{u,c} ∨ ¬x_{w,c}` per
   edge and colour; `coloringCNF_width` (width `≤ max q 2`), `coloringCNF_eval_iff` (a model is
   exactly one colour per vertex with no equal colours across an edge), `count_coloringCNF`
   (`SAT.count (coloringCNF G q) = coloringCount G q`, the number of proper colourings
   `Fin n → Fin q`), and `coloringCount_subexp`: under `SubexpCount (max q 2)` one primitive
   machine counts the proper `q`-colourings and decides `q`-colourability (the answer bit) within
   `C (L + 1)^d · 2^(A · ρ(n q))` steps, with `A · ρ(n q) = o(n)` at fixed `q`
   (`runtimeScale_mul_isLittleO`).

3. **The crossover inequality.** `crossoverThreshold A c n = A ρ(n) / log₂ c` is the pathwidth at
   which the decomposition dynamic program's `c^pw` equals the counting bound's `2^(A ρ(n))`:
   `rpow_le_of_crossover` (`pw ≥` threshold `→ 2^(A ρ(n)) ≤ c^pw`), `crossoverThreshold_eventually_lt`
   (for every `β > 0` the threshold is below `β n` for all large `n`, from `ρ = o(n)`), and
   `counting_beats_dp_eventually`: on every class of linear pathwidth (`pw G ≥ β n`) the counting
   bound's exponential factor is at most `c^{pw G}` for all large `n`, for every base `c > 1` and
   every constant `A`. The polynomial factors and the constants are outside the statement, as
   they are in the paper.

Every statement here was brute-force checked before it was stated: the formula's count against
subset enumeration on every graph of the atlas to 7 vertices
(`learning/subexp_crossover.py`, `reports/scratch/subexp_pathwidth/06_crossover/`).

What this file does **not** claim: that `SubexpCount k` holds for any `k`; that maximum
independent set (the threshold `|S| ≥ t`, which needs the adder-tree circuit of §6.2) is
formalised — only the counts are; that the dynamic program is modelled (the crossover compares
exponents, not machines); that any polynomial factor is bounded; that the crossover says anything at a specific `n`
(the constants `A`, and the paper's, are unknown).
-/
import MOSPFormalization.SubexpPathwidth.Frame
import Mathlib.Combinatorics.SimpleGraph.Clique

set_option linter.unusedSectionVars false

namespace MOSPFormalization.SubexpPathwidth

open OAI.Algorithms.SubexponentialSAT
open OAI.Algorithms.SubexponentialSAT.Computation
open OAI.Algorithms.SubexponentialSAT.SqrtLogSpace
open OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement
open Asymptotics Filter

/-! ### The independent-set formula -/

/-- The clause `¬x_u ∨ ¬x_w`. -/
def edgeClause {n : ℕ} (u w : Fin n) : SAT.Clause (Fin n) :=
  {⟨u, false⟩, ⟨w, false⟩}

/-- Corollary 1.3's formula: one variable per vertex, `¬x_u ∨ ¬x_w` for every edge. -/
noncomputable def indepCNF {n : ℕ} (G : SimpleGraph (Fin n)) : SAT.CNF (Fin n) :=
  open Classical in
  (Finset.univ.filter (fun p : Fin n × Fin n => G.Adj p.1 p.2)).image
    (fun p => edgeClause p.1 p.2)

/-- The number of independent sets of `G`. -/
noncomputable def indepCount {n : ℕ} (G : SimpleGraph (Fin n)) : ℕ :=
  open Classical in
  (Finset.univ.filter (fun S : Finset (Fin n) => G.IsIndepSet (↑S : Set (Fin n)))).card

theorem edgeClause_card_le {n : ℕ} (u w : Fin n) : (edgeClause u w).card ≤ 2 :=
  Finset.card_le_two

/-- The formula has width `≤ 2`. -/
theorem indepCNF_width {n : ℕ} (G : SimpleGraph (Fin n)) : SAT.WidthAtMost 2 (indepCNF G) := by
  intro C hC
  classical
  simp only [indepCNF, Finset.mem_image, Finset.mem_filter, Finset.mem_univ, true_and] at hC
  obtain ⟨p, -, rfl⟩ := hC
  exact edgeClause_card_le _ _

theorem edgeClause_eval {n : ℕ} (a : SAT.Assignment (Fin n)) (u w : Fin n) :
    (edgeClause u w).eval a = true ↔ (a u = false ∨ a w = false) := by
  simp [edgeClause, SAT.Clause.eval, SAT.Literal.eval]

/-- A model of `indepCNF G` is an independent set: the vertices set to `true`. -/
theorem indepCNF_eval_iff {n : ℕ} (G : SimpleGraph (Fin n)) (a : SAT.Assignment (Fin n)) :
    (indepCNF G).eval a = true ↔ G.IsIndepSet {v | a v = true} := by
  classical
  simp only [SAT.CNF.eval, decide_eq_true_eq, indepCNF, Finset.mem_image, Finset.mem_filter,
    Finset.mem_univ, true_and, forall_exists_index, and_imp]
  constructor
  · intro h v hv w hw hvw hadj
    have := h _ (v, w) hadj rfl
    rw [edgeClause_eval] at this
    simp only [Set.mem_ofPred_eq] at hv hw
    rcases this with h1 | h1 <;> simp_all
  · intro hI C p hadj rfl
    rw [edgeClause_eval]
    by_cases hu : a p.1 = false
    · exact Or.inl hu
    · right
      by_contra hw
      have hu' : a p.1 = true := by simpa using hu
      have hw' : a p.2 = true := by simpa using hw
      exact hI (by simpa using hu') (by simpa using hw') (G.ne_of_adj hadj) hadj

/-- The model count is the number of independent sets. -/
theorem count_indepCNF {n : ℕ} (G : SimpleGraph (Fin n)) :
    SAT.count (indepCNF G) = indepCount G := by
  classical
  unfold SAT.count SAT.satisfyingAssignments indepCount
  refine Finset.card_nbij' (fun a => Finset.univ.filter (fun v => a v = true))
    (fun S => fun v => decide (v ∈ S)) ?_ ?_ ?_ ?_
  · intro a ha
    simp only [Finset.mem_coe, Finset.mem_filter, Finset.mem_univ, true_and] at ha ⊢
    rw [indepCNF_eval_iff] at ha
    convert ha using 1
    ext v
    simp
  · intro S hS
    simp only [Finset.mem_coe, Finset.mem_filter, Finset.mem_univ, true_and] at hS ⊢
    rw [indepCNF_eval_iff]
    convert hS using 1
    ext v
    simp
  · intro a _
    funext v
    by_cases h : a v = true <;> simp [h]
  · intro S _
    ext v
    simp

/-! ### The algorithm: counting independent sets under the hypothesis -/

/-- **Independent sets are counted in `2^{o(n)} · poly` under the counting hypothesis.** Under
`SubexpCount 2`, one primitive machine, on the canonical encoding of `indepCNF G`, halts with the
number of independent sets of `G` on its count tape and `decide (0 < indepCount G)` as its
answer, within `C (L + 1)^d · 2^(A · ρ(n))` steps, where `L` is the formula's bit length and `n`
the number of vertices; `A · ρ(n)` is a subexponential exponent. This is Corollary 1.3's first
sentence as a consequence of the comparator statement. -/
theorem indepCount_subexp (h : SubexpCount 2) :
    ∃ (machine : PrimitiveMachine) (countTape : Fin machine.tapeCount) (C A : ℝ) (d : ℕ),
      0 < C ∧ 0 < A ∧ 0 < d ∧ IsSubexpExponent (fun n : ℕ => A * runtimeScale n) ∧
      ∀ (n : ℕ) (G : SimpleGraph (Fin n)),
        ∃ (time : ℕ) (final : machine.Cfg),
          Trace machine.step time (machine.init (Encoding.encodeCNF (indepCNF G))) final ∧
          final.tapes countTape = Turing.Tape.mk₁ ((countWord (indepCount G)).map some) ∧
          final.state = Sum.inl (decide (0 < indepCount G)) ∧
          (time : ℝ) ≤ C * ((Encoding.formulaBitLength (indepCNF G) : ℝ) + 1) ^ d *
            (2 : ℝ) ^ (A * runtimeScale n) := by
  obtain ⟨machine, countTape, answerTape, C, A, S, d, e, hC, hA, hS, hd, he, hmain⟩ := h
  refine ⟨machine, countTape, C, A, d, hC, hA, hd, isSubexpExponent_runtimeScale A, ?_⟩
  intro n G
  obtain ⟨time, final, htrace, hcount, -, hstate, -, -, htime, -⟩ :=
    hmain n (indepCNF G) (indepCNF_width G)
  refine ⟨time, final.config, ?_, ?_, ?_, ?_⟩
  · have := Trace.config_of_locatedStep htrace
    simpa [locatedInit] using this
  · rw [hcount, count_indepCNF]
  · rw [hstate, count_indepCNF]
  · simpa [runtimeBound_eq] using htime

/-! ### The crossover inequality -/

/-- The pathwidth at which `c^pw = 2^(A ρ(n))`: above it the counting bound's exponential factor
is below the decomposition dynamic program's. -/
noncomputable def crossoverThreshold (A c : ℝ) (n : ℕ) : ℝ :=
  A * runtimeScale n / Real.logb 2 c

/-- Above the threshold, `2^(A ρ(n)) ≤ c^pw`. -/
theorem rpow_le_of_crossover {A c : ℝ} (hc : 1 < c) {n : ℕ} {pw : ℝ}
    (h : crossoverThreshold A c n ≤ pw) :
    (2 : ℝ) ^ (A * runtimeScale n) ≤ c ^ pw := by
  have hlog : 0 < Real.logb 2 c := Real.logb_pos (by norm_num) hc
  have hle : A * runtimeScale n ≤ Real.logb 2 c * pw := by
    rw [crossoverThreshold, div_le_iff₀ hlog] at h
    linarith
  calc (2 : ℝ) ^ (A * runtimeScale n)
      ≤ (2 : ℝ) ^ (Real.logb 2 c * pw) :=
        Real.rpow_le_rpow_of_exponent_le (by norm_num) hle
    _ = ((2 : ℝ) ^ Real.logb 2 c) ^ pw := Real.rpow_mul (by norm_num) _ _
    _ = c ^ pw := by
        rw [Real.rpow_logb (by norm_num) (by norm_num) (by linarith)]

/-- The threshold is `o(n)`: for every `β > 0` it is below `β n` for all large `n`. -/
theorem crossoverThreshold_eventually_lt {A c β : ℝ} (hc : 1 < c) (hβ : 0 < β) :
    ∀ᶠ n : ℕ in atTop, crossoverThreshold A c n < β * n := by
  have hlog : 0 < Real.logb 2 c := Real.logb_pos (by norm_num) hc
  have hlit : (fun n : ℕ => A / Real.logb 2 c * runtimeScale n) =o[atTop]
      (fun n : ℕ => (n : ℝ)) :=
    runtimeScale_isLittleO.const_mul_left (A / Real.logb 2 c)
  have hev := hlit.def (half_pos hβ)
  filter_upwards [hev, eventually_ge_atTop 1] with n hn hn1
  have hn' : (1 : ℝ) ≤ n := by exact_mod_cast hn1
  have hβn : 0 < β * n := by positivity
  calc crossoverThreshold A c n = A / Real.logb 2 c * runtimeScale n := by
        unfold crossoverThreshold; ring
    _ ≤ ‖A / Real.logb 2 c * runtimeScale n‖ := Real.le_norm_self _
    _ ≤ β / 2 * ‖(n : ℝ)‖ := hn
    _ = β / 2 * n := by rw [Real.norm_eq_abs, abs_of_nonneg (by positivity)]
    _ < β * n := by linarith

/-- **The crossover.** On graphs of linear pathwidth (`pw G ≥ β n`), for every base `c > 1` and
every constant `A`, the counting bound's exponential factor `2^(A ρ(n))` is at most the
decomposition dynamic program's `c^{pw G}` for all large `n`. -/
theorem counting_beats_dp_eventually {A c β : ℝ} (hc : 1 < c) (hβ : 0 < β) :
    ∀ᶠ n : ℕ in atTop, ∀ G : SimpleGraph (Fin n),
      β * n ≤ (pathwidth G : ℝ) → (2 : ℝ) ^ (A * runtimeScale n) ≤ c ^ (pathwidth G : ℝ) := by
  filter_upwards [crossoverThreshold_eventually_lt (A := A) hc hβ] with n hn G hG
  exact rpow_le_of_crossover hc (le_trans hn.le hG)

/-! ### The `q`-colouring formula -/

/-- The variable `x_{v,c}` as an element of `Fin (n * q)`. -/
def colVar {n q : ℕ} (v : Fin n) (c : Fin q) : Fin (n * q) := finProdFinEquiv (v, c)

theorem colVar_injective {n q : ℕ} : Function.Injective
    (fun p : Fin n × Fin q => colVar p.1 p.2) := by
  intro p p' h
  exact finProdFinEquiv.injective h

/-- "`v` has at least one colour": `⋁_c x_{v,c}`. -/
def aloClause {n q : ℕ} (v : Fin n) : SAT.Clause (Fin (n * q)) :=
  Finset.univ.image (fun c : Fin q => (⟨colVar v c, true⟩ : SAT.Literal (Fin (n * q))))

/-- "`v` has at most one colour": `¬x_{v,c} ∨ ¬x_{v,c'}` for `c ≠ c'`; and "no equal colours
across an edge": `¬x_{u,c} ∨ ¬x_{w,c}`. -/
noncomputable def coloringCNF {n : ℕ} (G : SimpleGraph (Fin n)) (q : ℕ) :
    SAT.CNF (Fin (n * q)) :=
  open Classical in
  (Finset.univ.image (fun v : Fin n => aloClause (q := q) v)) ∪
  ((Finset.univ.filter (fun p : Fin n × Fin q × Fin q => p.2.1 ≠ p.2.2)).image
    (fun p => edgeClause (colVar p.1 p.2.1) (colVar p.1 p.2.2))) ∪
  ((Finset.univ.filter (fun p : Fin n × Fin n × Fin q => G.Adj p.1 p.2.1)).image
    (fun p => edgeClause (colVar p.1 p.2.2) (colVar p.2.1 p.2.2)))

theorem aloClause_card {n q : ℕ} (v : Fin n) : (aloClause (q := q) v).card ≤ q := by
  calc (aloClause (q := q) v).card ≤ (Finset.univ : Finset (Fin q)).card := Finset.card_image_le
    _ = q := by simp

theorem coloringCNF_width {n : ℕ} (G : SimpleGraph (Fin n)) (q : ℕ) :
    SAT.WidthAtMost (max q 2) (coloringCNF G q) := by
  intro C hC
  classical
  simp only [coloringCNF, Finset.mem_union, Finset.mem_image, Finset.mem_filter, Finset.mem_univ,
    true_and] at hC
  rcases hC with (⟨v, rfl⟩ | ⟨p, -, rfl⟩) | ⟨p, -, rfl⟩
  · exact le_trans (aloClause_card v) (le_max_left _ _)
  · exact le_trans (edgeClause_card_le _ _) (le_max_right _ _)
  · exact le_trans (edgeClause_card_le _ _) (le_max_right _ _)

theorem aloClause_eval {n q : ℕ} (a : SAT.Assignment (Fin (n * q))) (v : Fin n) :
    (aloClause (q := q) v).eval a = true ↔ ∃ c : Fin q, a (colVar v c) = true := by
  simp [aloClause, SAT.Clause.eval, SAT.Literal.eval]

/-- A model of `coloringCNF G q` is a proper colouring: `v ↦` the unique colour set at `v`. -/
theorem coloringCNF_eval_iff {n : ℕ} (G : SimpleGraph (Fin n)) (q : ℕ)
    (a : SAT.Assignment (Fin (n * q))) :
    (coloringCNF G q).eval a = true ↔
      (∀ v, ∃! c : Fin q, a (colVar v c) = true) ∧
      (∀ u w c, G.Adj u w → ¬ (a (colVar u c) = true ∧ a (colVar w c) = true)) := by
  classical
  simp only [SAT.CNF.eval, decide_eq_true_eq, coloringCNF, Finset.mem_union, Finset.mem_image,
    Finset.mem_filter, Finset.mem_univ, true_and]
  constructor
  · intro h
    refine ⟨fun v => ?_, fun u w c hadj => ?_⟩
    · obtain ⟨c, hc⟩ := (aloClause_eval a v).mp (h _ (Or.inl (Or.inl ⟨v, rfl⟩)))
      refine ⟨c, hc, fun c' hc' => ?_⟩
      by_contra hne
      have := h _ (Or.inl (Or.inr ⟨(v, c', c), hne, rfl⟩))
      rw [edgeClause_eval] at this
      simp_all
    · intro ⟨hu, hw⟩
      have := h _ (Or.inr ⟨(u, w, c), hadj, rfl⟩)
      rw [edgeClause_eval] at this
      simp_all
  · rintro ⟨h1, h2⟩ C ((⟨v, rfl⟩ | ⟨p, hne, rfl⟩) | ⟨p, hadj, rfl⟩)
    · rw [aloClause_eval]
      obtain ⟨c, hc, -⟩ := h1 v
      exact ⟨c, hc⟩
    · rw [edgeClause_eval]
      by_contra hcon
      simp only [not_or] at hcon
      obtain ⟨c, -, huniq⟩ := h1 p.1
      have e1 := huniq _ (by simpa using hcon.1)
      have e2 := huniq _ (by simpa using hcon.2)
      exact hne (e1.trans e2.symm)
    · rw [edgeClause_eval]
      by_contra hcon
      simp only [not_or] at hcon
      exact h2 _ _ _ hadj ⟨by simpa using hcon.1, by simpa using hcon.2⟩

/-- The colouring a model determines. -/
noncomputable def modelColoring {n q : ℕ} (a : SAT.Assignment (Fin (n * q)))
    (h : ∀ v, ∃! c : Fin q, a (colVar v c) = true) : Fin n → Fin q :=
  fun v => Classical.choose (h v).exists

theorem modelColoring_spec {n q : ℕ} (a : SAT.Assignment (Fin (n * q)))
    (h : ∀ v, ∃! c : Fin q, a (colVar v c) = true) (v : Fin n) :
    a (colVar v (modelColoring a h v)) = true :=
  Classical.choose_spec (h v).exists

theorem modelColoring_eq_iff {n q : ℕ} (a : SAT.Assignment (Fin (n * q)))
    (h : ∀ v, ∃! c : Fin q, a (colVar v c) = true) (v : Fin n) (c : Fin q) :
    modelColoring a h v = c ↔ a (colVar v c) = true := by
  constructor
  · rintro rfl; exact modelColoring_spec a h v
  · intro hc
    exact ((h v).unique (modelColoring_spec a h v) hc)

/-- The number of proper `q`-colourings of `G`, as functions `Fin n → Fin q`. -/
noncomputable def coloringCount {n : ℕ} (G : SimpleGraph (Fin n)) (q : ℕ) : ℕ :=
  open Classical in
  (Finset.univ.filter (fun f : Fin n → Fin q => ∀ u w, G.Adj u w → f u ≠ f w)).card

/-- The model count is the number of proper `q`-colourings. -/
theorem count_coloringCNF {n : ℕ} (G : SimpleGraph (Fin n)) (q : ℕ) :
    SAT.count (coloringCNF G q) = coloringCount G q := by
  classical
  unfold SAT.count SAT.satisfyingAssignments coloringCount
  -- the bijection: a model ↦ its colouring; a colouring ↦ the indicator assignment
  refine Finset.card_bij (fun a ha => modelColoring a ((coloringCNF_eval_iff G q a).mp
      (by simpa using ha)).1) ?_ ?_ ?_
  · intro a ha
    have h := (coloringCNF_eval_iff G q a).mp (by simpa using ha)
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    intro u w hadj heq
    apply h.2 u w (modelColoring a h.1 w) hadj
    refine ⟨?_, modelColoring_spec a h.1 w⟩
    rw [← heq]
    exact modelColoring_spec a h.1 u
  · intro a ha a' ha' heq
    have h := (coloringCNF_eval_iff G q a).mp (by simpa using ha)
    have h' := (coloringCNF_eval_iff G q a').mp (by simpa using ha')
    funext x
    obtain ⟨⟨v, c⟩, rfl⟩ := finProdFinEquiv.surjective x
    change a (colVar v c) = a' (colVar v c)
    have e1 := modelColoring_eq_iff a h.1 v c
    have e2 := modelColoring_eq_iff a' h'.1 v c
    have hfun : modelColoring a h.1 v = modelColoring a' h'.1 v := congrFun heq v
    rw [hfun] at e1
    cases hc : a' (colVar v c)
    · have hne : ¬ (modelColoring a' h'.1 v = c) := fun hm => by
        have := e2.mp hm
        simp [hc] at this
      have : ¬ (a (colVar v c) = true) := fun ht => hne (e1.mpr ht)
      simpa using this
    · exact e1.mp (e2.mpr hc)
  · intro f hf
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hf
    refine ⟨fun x => decide (f (finProdFinEquiv.symm x).1 = (finProdFinEquiv.symm x).2), ?_, ?_⟩
    · simp only [Finset.mem_filter, Finset.mem_univ, true_and]
      rw [coloringCNF_eval_iff]
      refine ⟨fun v => ⟨f v, by simp [colVar], fun c hc => ?_⟩, fun u w c hadj ⟨hu, hw⟩ => ?_⟩
      · have hc' : f v = c := by simpa [colVar] using hc
        exact hc'.symm
      · simp [colVar] at hu hw
        exact hf u w hadj (hu.trans hw.symm)
    · funext v
      rw [modelColoring_eq_iff]
      simp [colVar]

/-! ### The algorithm: counting `q`-colourings under the hypothesis -/

open Asymptotics Filter in
/-- `ρ(n q) = o(n)` at fixed `q`: a `q n`-variable encoding keeps the exponent subexponential
in the number of vertices. -/
theorem runtimeScale_mul_isLittleO (q : ℕ) :
    (fun n : ℕ => runtimeScale (n * q)) =o[atTop] (fun n : ℕ => (n : ℝ)) := by
  rcases Nat.eq_zero_or_pos q with rfl | hq
  · have h0 : (fun n : ℕ => runtimeScale (n * 0)) = fun _ => (0 : ℝ) := by
      funext n; simp [runtimeScale]
    rw [h0]
    exact isLittleO_zero _ _
  · have ht : Tendsto (fun n : ℕ => n * q) atTop atTop :=
      tendsto_atTop_mono (fun n => Nat.le_mul_of_pos_right n hq) tendsto_id
    have hcomp := runtimeScale_isLittleO.comp_tendsto ht
    have hbig : (fun n : ℕ => (((n * q : ℕ)) : ℝ)) =O[atTop] (fun n : ℕ => (n : ℝ)) := by
      refine IsBigO.of_bound q ?_
      filter_upwards with n
      rw [Real.norm_eq_abs, Real.norm_eq_abs, Nat.cast_mul, abs_mul, Nat.abs_cast, Nat.abs_cast,
        mul_comm]
    exact hcomp.trans_isBigO hbig

theorem isSubexpExponent_runtimeScale_mul (A : ℝ) (q : ℕ) :
    IsSubexpExponent (fun n : ℕ => A * runtimeScale (n * q)) :=
  (runtimeScale_mul_isLittleO q).const_mul_left A

/-- **Proper `q`-colourings are counted in `2^{o(n)} · poly` under the counting hypothesis**, and
`q`-colourability is decided (the answer bit): Corollary 1.3's second sentence as a consequence
of the comparator statement at width `max q 2`. -/
theorem coloringCount_subexp {q : ℕ} (h : SubexpCount (max q 2)) :
    ∃ (machine : PrimitiveMachine) (countTape : Fin machine.tapeCount) (C A : ℝ) (d : ℕ),
      0 < C ∧ 0 < A ∧ 0 < d ∧ IsSubexpExponent (fun n : ℕ => A * runtimeScale (n * q)) ∧
      ∀ (n : ℕ) (G : SimpleGraph (Fin n)),
        ∃ (time : ℕ) (final : machine.Cfg),
          Trace machine.step time (machine.init (Encoding.encodeCNF (coloringCNF G q))) final ∧
          final.tapes countTape = Turing.Tape.mk₁ ((countWord (coloringCount G q)).map some) ∧
          final.state = Sum.inl (decide (0 < coloringCount G q)) ∧
          (time : ℝ) ≤ C * ((Encoding.formulaBitLength (coloringCNF G q) : ℝ) + 1) ^ d *
            (2 : ℝ) ^ (A * runtimeScale (n * q)) := by
  obtain ⟨machine, countTape, answerTape, C, A, S, d, e, hC, hA, hS, hd, he, hmain⟩ := h
  refine ⟨machine, countTape, C, A, d, hC, hA, hd, isSubexpExponent_runtimeScale_mul A q, ?_⟩
  intro n G
  obtain ⟨time, final, htrace, hcount, -, hstate, -, -, htime, -⟩ :=
    hmain (n * q) (coloringCNF G q) (coloringCNF_width G q)
  refine ⟨time, final.config, ?_, ?_, ?_, ?_⟩
  · have := Trace.config_of_locatedStep htrace
    simpa [locatedInit] using this
  · rw [hcount, count_coloringCNF]
  · rw [hstate, count_coloringCNF]
  · simpa [runtimeBound_eq] using htime

end MOSPFormalization.SubexpPathwidth
