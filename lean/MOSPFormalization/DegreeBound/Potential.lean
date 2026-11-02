/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The potential `f`, the component potential `f⁻`, and one-deletion degree accounting

Item 05 of loop0012 (`reports/edwards_mcdermid_plan.md` §0.5; `reports/edwards_mcdermid.md`
§2.6 and §5): the potential of Edwards & McDermid (2015, p. 7), `f G = Σ_v g (deg v)`, and
its per-component form `f⁻ G = f G − Σ_C g' (δ(C))` (the sum over the connected components
`C` of `G`, `δ(C)` the minimum degree on `C`), on `SimpleGraph V` with removed vertices
isolated (plan §0.5). Isolated vertices are singleton components of minimum degree 0 and
contribute `g 0 = g' 0 = 0`.

* `supp G` — the vertices of positive degree; `isolate G w` (`Minor.lean`) deletes the
  edges at `w`; `degree_isolate` — the degree after one deletion.
* **P1** `potential_isolate`: `f (G − w) = f G − g (deg w) − Σ_{v ∈ N(w)} g' (deg v)`.
* **P2** `potential_isolate_le_sub_one`: every degree `0` or `≥ 3`, `w` of maximum degree
  `Δ ≥ 4` with a neighbour of degree `≤ Δ − 1` ⇒ `f (G − w) ≤ f G − 1` (W3, W4).
* **P2r** `potential_isolate_regular`: `deg w = Δ ≥ 4` and every neighbour of `w` of
  degree `Δ` ⇒ `f (G − w) = f G − 1 + g' (Δ − 1) − g' Δ` (an equality; needs only the
  neighbours, not regularity); `potential_isolate_le_regular` is its `≤` form.
* `compFinset G C`, `minDeg G C`, `potentialMinus G` (`f⁻`), `compPotential G C`
  (the summand of one component), `vertexTerm G v` (the same quantity spread over the
  vertices of the component): `potentialMinus_eq_sum_compPotential`,
  `potentialMinus_eq_sum_vertexTerm`, `compPotential_nonneg`,
  `potentialMinus_le_potential`.
* `globalMinDeg G` (the minimum degree over the support, `0` if empty) and
  `F G = f G − g' (globalMinDeg G)`: `potentialMinus_le_F`, and
  `potentialMinus_eq_F_of_connected` when the support is connected.
* **Additivity** `potentialMinus_add`: `Disjoint (supp G₁) (supp G₂)` ⇒
  `f⁻ (G₁ ⊔ G₂) = f⁻ G₁ + f⁻ G₂`, through `reachable_sup_iff` (a walk in the union of two
  graphs with disjoint supports stays in one of them) and `vertexTerm_sup`.
* **B1** `potentialMinus_cubic`: support connected and cubic on `N` vertices ⇒
  `f⁻ = N/6 − 1/6`; `potentialMinus_ge_five_sixths`: support connected, degrees `0` or
  `≥ 3`, some degree `≥ 4` ⇒ `5/6 ≤ f⁻`.

Every statement was checked in exact rationals before it was stated
(`reports/scratch/edwards_mcdermid/05_potential/check.py`: 20,000 random graphs with
isolated vertices at `n ≤ 12`, 10,000 random disjoint unions, 1,996 embedded cubic graphs;
item 02 had P1, P2 and P2r on every graph to 9 vertices). Nothing here is about reductions
(item 06) or pathwidth (item 09).
-/
import MOSPFormalization.DegreeBound.Weights
import MOSPFormalization.Minor
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite

set_option linter.unusedSectionVars false

namespace MOSPFormalization.DegreeBound

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### The support, and degrees after one deletion -/

/-- The vertices of positive degree (the "non-removed" vertices of the design). -/
def supp (G : SimpleGraph V) [DecidableRel G.Adj] : Finset V :=
  univ.filter (fun v => 0 < G.degree v)

theorem mem_supp {G : SimpleGraph V} [DecidableRel G.Adj] {v : V} :
    v ∈ supp G ↔ 0 < G.degree v := by
  simp [supp]

theorem mem_supp_iff_exists_adj {G : SimpleGraph V} [DecidableRel G.Adj] {v : V} :
    v ∈ supp G ↔ ∃ w, G.Adj v w := by
  rw [mem_supp, G.degree_pos_iff_exists_adj]

instance instDecidableRelIsolateAdj (G : SimpleGraph V) [DecidableRel G.Adj] (w : V) :
    DecidableRel (isolate G w).Adj :=
  fun x y => inferInstanceAs (Decidable (G.Adj x y ∧ x ≠ w ∧ y ≠ w))

theorem isolate_adj (G : SimpleGraph V) (w x y : V) :
    (isolate G w).Adj x y ↔ G.Adj x y ∧ x ≠ w ∧ y ≠ w := Iff.rfl

section Isolate

variable (G : SimpleGraph V) [DecidableRel G.Adj]

theorem neighborFinset_isolate (w v : V) :
    (isolate G w).neighborFinset v = if v = w then ∅ else (G.neighborFinset v).erase w := by
  ext x
  simp only [SimpleGraph.mem_neighborFinset, isolate_adj]
  split_ifs with h
  · subst h; simp
  · simp only [Finset.mem_erase, SimpleGraph.mem_neighborFinset]
    constructor
    · rintro ⟨hx, -, hxw⟩; exact ⟨hxw, hx⟩
    · rintro ⟨hxw, hx⟩; exact ⟨hx, h, hxw⟩

theorem degree_isolate_self (w : V) : (isolate G w).degree w = 0 := by
  rw [← SimpleGraph.card_neighborFinset_eq_degree, neighborFinset_isolate, ite_eq_left rfl, card_empty]

theorem degree_isolate_of_adj {w v : V} (h : G.Adj w v) :
    (isolate G w).degree v = G.degree v - 1 := by
  rw [← SimpleGraph.card_neighborFinset_eq_degree, ← SimpleGraph.card_neighborFinset_eq_degree,
    neighborFinset_isolate, ite_eq_right (G.ne_of_adj h).symm, card_erase_of_mem]
  rw [SimpleGraph.mem_neighborFinset]; exact h.symm

theorem degree_isolate_of_not_adj {w v : V} (hv : v ≠ w) (h : ¬ G.Adj w v) :
    (isolate G w).degree v = G.degree v := by
  rw [← SimpleGraph.card_neighborFinset_eq_degree, ← SimpleGraph.card_neighborFinset_eq_degree,
    neighborFinset_isolate, ite_eq_right hv, erase_eq_of_notMem]
  rw [SimpleGraph.mem_neighborFinset]; exact fun h' => h h'.symm

/-- The degree after one deletion: `0` at `w`, one less at the neighbours of `w`, unchanged
elsewhere. -/
theorem degree_isolate (w v : V) :
    (isolate G w).degree v =
      if v = w then 0 else if G.Adj w v then G.degree v - 1 else G.degree v := by
  split_ifs with h1 h2
  · subst h1; exact degree_isolate_self G v
  · exact degree_isolate_of_adj G h2
  · exact degree_isolate_of_not_adj G h1 h2

/-- `supp (G − w) ⊆ supp G`. -/
theorem supp_isolate_subset (w : V) : supp (isolate G w) ⊆ supp G := by
  intro v hv
  rw [mem_supp] at hv ⊢
  rw [degree_isolate] at hv
  split_ifs at hv with h1 h2 <;> omega

/-! ### The potential `f` and one deletion (P1, P2, P2r) -/

/-- The potential `f G = Σ_v g (deg v)` (Edwards & McDermid p. 7, `α = 1/6`). -/
def potential : ℚ := ∑ v, g (G.degree v)

theorem potential_nonneg : 0 ≤ potential G :=
  sum_nonneg (fun v _ => g_nonneg (G.degree v))

theorem g_degree_isolate (w v : V) :
    g ((isolate G w).degree v) =
      g (G.degree v) - (if v = w then g (G.degree w)
        else if G.Adj w v then g' (G.degree v) else 0) := by
  rw [degree_isolate]
  split_ifs with h1 h2
  · subst h1; simp
  · rw [g']; ring
  · simp

/-- **P1**: `f (G − w) = f G − g (deg w) − Σ_{v ∈ N(w)} g' (deg v)`. -/
theorem potential_isolate (w : V) :
    potential (isolate G w) =
      potential G - g (G.degree w) - ∑ v ∈ G.neighborFinset w, g' (G.degree v) := by
  unfold potential
  simp_rw [g_degree_isolate G w]
  rw [sum_sub_distrib]
  have hsplit : ∀ v, (if v = w then g (G.degree w) else if G.Adj w v then g' (G.degree v) else 0)
      = (if v = w then g (G.degree w) else 0) + (if G.Adj w v then g' (G.degree v) else 0) := by
    intro v
    by_cases hv : v = w
    · subst hv; simp
    · simp [hv]
  simp_rw [hsplit]
  rw [sum_add_distrib, sum_ite_eq', ite_eq_left (mem_univ _), SimpleGraph.neighborFinset_eq_filter,
    sum_filter]
  ring

/-- Every neighbour of a vertex has degree at least 3 when every degree is `0` or `≥ 3`. -/
theorem three_le_degree_of_adj (hdeg : ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v) {w v : V}
    (h : G.Adj w v) : 3 ≤ G.degree v := by
  rcases hdeg v with h0 | h3
  · exfalso
    have := (G.degree_pos_iff_exists_adj v).2 ⟨w, h.symm⟩
    omega
  · exact h3

/-- **P2** (p. 10): every degree `0` or `≥ 3`, `w` of maximum degree `Δ ≥ 4` with a
neighbour of degree at most `Δ − 1` ⇒ `f (G − w) ≤ f G − 1`. -/
theorem potential_isolate_le_sub_one {Δ : ℕ} {w : V}
    (hdeg : ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v) (hmax : ∀ v, G.degree v ≤ Δ)
    (hw : G.degree w = Δ) (h4 : 4 ≤ Δ) (hlow : ∃ v, G.Adj w v ∧ G.degree v ≤ Δ - 1) :
    potential (isolate G w) ≤ potential G - 1 := by
  obtain ⟨v₀, hv₀, hd₀⟩ := hlow
  rw [potential_isolate, hw]
  have hW4 := one_sub_g_eq h4
  have hnb : ∀ v ∈ G.neighborFinset w, g' Δ ≤ g' (G.degree v) := by
    intro v hv
    rw [SimpleGraph.mem_neighborFinset] at hv
    exact g'_antitone_of_three_le (three_le_degree_of_adj G hdeg hv) (hmax v)
  have hv₀mem : v₀ ∈ G.neighborFinset w := (SimpleGraph.mem_neighborFinset _ _ _).2 hv₀
  have h0 : g' (Δ - 1) ≤ g' (G.degree v₀) :=
    g'_antitone_of_three_le (three_le_degree_of_adj G hdeg hv₀) hd₀
  have hsum : ∑ v ∈ G.neighborFinset w, g' (G.degree v)
      = g' (G.degree v₀) + ∑ v ∈ (G.neighborFinset w).erase v₀, g' (G.degree v) :=
    (add_sum_erase _ _ hv₀mem).symm
  have hcard : ((G.neighborFinset w).erase v₀).card = Δ - 1 := by
    rw [card_erase_of_mem hv₀mem, SimpleGraph.card_neighborFinset_eq_degree, hw]
  have hrest : ((Δ - 1 : ℕ) : ℚ) * g' Δ
      ≤ ∑ v ∈ (G.neighborFinset w).erase v₀, g' (G.degree v) := by
    have := card_nsmul_le_sum ((G.neighborFinset w).erase v₀) (fun v => g' (G.degree v)) (g' Δ)
      (fun v hv => hnb v (mem_of_mem_erase hv))
    rwa [hcard, nsmul_eq_mul] at this
  have hcast : ((Δ - 1 : ℕ) : ℚ) = (Δ : ℚ) - 1 := by
    rw [Nat.cast_sub (by omega), Nat.cast_one]
  rw [hcast] at hrest
  rw [hsum]
  linarith

/-- **P2r** (p. 11): `deg w = Δ ≥ 4` and every neighbour of `w` of degree `Δ` ⇒
`f (G − w) = f G − 1 + g' (Δ − 1) − g' Δ`. Only the neighbours of `w` are constrained,
so the `Δ`-regular case is a special case. -/
theorem potential_isolate_regular {Δ : ℕ} {w : V} (hw : G.degree w = Δ) (h4 : 4 ≤ Δ)
    (hnb : ∀ v, G.Adj w v → G.degree v = Δ) :
    potential (isolate G w) = potential G - 1 + g' (Δ - 1) - g' Δ := by
  rw [potential_isolate, hw]
  have hsum : ∑ v ∈ G.neighborFinset w, g' (G.degree v) = (Δ : ℚ) * g' Δ := by
    rw [sum_congr rfl (fun v hv => by rw [hnb v ((SimpleGraph.mem_neighborFinset _ _ _).1 hv)]),
      sum_const, SimpleGraph.card_neighborFinset_eq_degree, hw, nsmul_eq_mul]
  rw [hsum]
  have hW4 := one_sub_g_eq h4
  linear_combination hW4

/-- P2r as an inequality (the item's statement). -/
theorem potential_isolate_le_regular {Δ : ℕ} {w : V} (hw : G.degree w = Δ) (h4 : 4 ≤ Δ)
    (hnb : ∀ v, G.Adj w v → G.degree v = Δ) :
    potential (isolate G w) ≤ potential G - 1 + g' (Δ - 1) - g' Δ :=
  (potential_isolate_regular G hw h4 hnb).le

end Isolate

/-! ### Components, their minimum degree, and the component potential `f⁻` -/

section Components

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The vertex set of a connected component, as a finset. -/
noncomputable def compFinset (C : G.ConnectedComponent) : Finset V := by
  classical exact univ.filter (fun v => G.connectedComponentMk v = C)

theorem mem_compFinset {C : G.ConnectedComponent} {v : V} :
    v ∈ compFinset G C ↔ G.connectedComponentMk v = C := by
  unfold compFinset; simp

theorem mem_compFinset_mk {v w : V} :
    w ∈ compFinset G (G.connectedComponentMk v) ↔ G.Reachable w v := by
  rw [mem_compFinset, SimpleGraph.ConnectedComponent.eq]

theorem self_mem_compFinset (v : V) : v ∈ compFinset G (G.connectedComponentMk v) :=
  (mem_compFinset G).2 rfl

theorem compFinset_nonempty (C : G.ConnectedComponent) : (compFinset G C).Nonempty := by
  induction C using SimpleGraph.ConnectedComponent.ind with
  | h v => exact ⟨v, self_mem_compFinset G v⟩

/-- `∑_C ∑_{v ∈ C} f v = ∑_v f v`: the components partition the vertices. -/
theorem sum_compFinset (f : V → ℚ) :
    ∑ C : G.ConnectedComponent, ∑ v ∈ compFinset G C, f v = ∑ v, f v := by
  classical
  unfold compFinset
  exact sum_fiberwise univ G.connectedComponentMk f

/-- The minimum degree on a component, `δ(C)`. -/
noncomputable def minDeg (C : G.ConnectedComponent) : ℕ :=
  (compFinset G C).inf' (compFinset_nonempty G C) (fun v => G.degree v)

theorem minDeg_le {C : G.ConnectedComponent} {v : V} (hv : v ∈ compFinset G C) :
    minDeg G C ≤ G.degree v :=
  inf'_le (fun v => G.degree v) hv

theorem exists_degree_eq_minDeg (C : G.ConnectedComponent) :
    ∃ v ∈ compFinset G C, G.degree v = minDeg G C := by
  obtain ⟨v, hv, h⟩ := exists_mem_eq_inf' (compFinset_nonempty G C) (fun v => G.degree v)
  exact ⟨v, hv, h.symm⟩

theorem le_minDeg_iff {C : G.ConnectedComponent} {a : ℕ} :
    a ≤ minDeg G C ↔ ∀ v ∈ compFinset G C, a ≤ G.degree v :=
  le_inf'_iff _ (fun v => G.degree v)

/-- The component potential `f⁻ G = f G − Σ_C g' (δ(C))` (p. 7, per component; plan §0.5). -/
noncomputable def potentialMinus : ℚ :=
  potential G - ∑ C : G.ConnectedComponent, g' (minDeg G C)

theorem potentialMinus_le_potential : potentialMinus G ≤ potential G := by
  unfold potentialMinus
  have := sum_nonneg (fun C (_ : C ∈ (univ : Finset G.ConnectedComponent)) =>
    g'_nonneg (minDeg G C))
  linarith

/-- The summand of one component: `Σ_{v ∈ C} g (deg v) − g' (δ(C))`. -/
noncomputable def compPotential (C : G.ConnectedComponent) : ℚ :=
  ∑ v ∈ compFinset G C, g (G.degree v) - g' (minDeg G C)

/-- `f⁻` is additive over the components. -/
theorem potentialMinus_eq_sum_compPotential :
    potentialMinus G = ∑ C : G.ConnectedComponent, compPotential G C := by
  unfold potentialMinus compPotential potential
  rw [sum_sub_distrib, sum_compFinset]

/-- Every component contributes a non-negative amount (`g' ≤ g` at the minimum-degree
vertex, every other term `≥ 0`). -/
theorem compPotential_nonneg (C : G.ConnectedComponent) : 0 ≤ compPotential G C := by
  obtain ⟨v, hv, hd⟩ := exists_degree_eq_minDeg G C
  unfold compPotential
  have h1 : g (G.degree v) ≤ ∑ u ∈ compFinset G C, g (G.degree u) :=
    single_le_sum (fun u _ => g_nonneg (G.degree u)) hv
  have h2 : g' (minDeg G C) ≤ g (G.degree v) := by rw [hd]; exact g'_le_g _
  linarith

theorem potentialMinus_nonneg : 0 ≤ potentialMinus G := by
  rw [potentialMinus_eq_sum_compPotential]
  exact sum_nonneg (fun C _ => compPotential_nonneg G C)

/-- The same quantity spread over the vertices of each component: `vertexTerm G v =
g (deg v) − g' (δ(C_v)) / |C_v|`. -/
noncomputable def vertexTerm (v : V) : ℚ :=
  g (G.degree v) - g' (minDeg G (G.connectedComponentMk v))
    / ((compFinset G (G.connectedComponentMk v)).card : ℚ)

theorem potentialMinus_eq_sum_vertexTerm : potentialMinus G = ∑ v, vertexTerm G v := by
  unfold vertexTerm
  rw [sum_sub_distrib]
  unfold potentialMinus potential
  congr 1
  rw [← sum_compFinset G]
  refine sum_congr rfl (fun C _ => ?_)
  rw [sum_congr rfl (fun v hv => by rw [(mem_compFinset G).1 hv]), sum_const, nsmul_eq_mul]
  have hpos : (0 : ℚ) < (compFinset G C).card := by
    exact_mod_cast card_pos.2 (compFinset_nonempty G C)
  field_simp

/-! #### Isolated vertices -/

theorem pos_degree_of_reachable_of_ne {u v : V} (h : G.Reachable u v) (hne : u ≠ v) :
    0 < G.degree u := by
  obtain ⟨p⟩ := h
  cases p with
  | nil => exact absurd rfl hne
  | cons hadj _ => exact (G.degree_pos_iff_exists_adj u).2 ⟨_, hadj⟩

theorem eq_of_reachable_of_degree_eq_zero {u v : V} (h : G.Reachable u v) (h0 : G.degree u = 0) :
    u = v := by
  by_contra hne
  have := pos_degree_of_reachable_of_ne G h hne
  omega

theorem compFinset_eq_singleton_of_degree_eq_zero {v : V} (h : G.degree v = 0) :
    compFinset G (G.connectedComponentMk v) = {v} := by
  ext w
  rw [mem_compFinset_mk, mem_singleton]
  constructor
  · intro hr; exact (eq_of_reachable_of_degree_eq_zero G hr.symm h).symm
  · rintro rfl; exact SimpleGraph.Reachable.refl _

theorem minDeg_eq_zero_of_degree_eq_zero {v : V} (h : G.degree v = 0) :
    minDeg G (G.connectedComponentMk v) = 0 := by
  have := minDeg_le G (self_mem_compFinset G v)
  omega

theorem vertexTerm_eq_zero_of_degree_eq_zero {v : V} (h : G.degree v = 0) :
    vertexTerm G v = 0 := by
  unfold vertexTerm
  rw [h, minDeg_eq_zero_of_degree_eq_zero G h, g_zero, g'_eq_zero_of_le_two (by norm_num)]
  simp

/-- A component of a vertex of positive degree lies in the support. -/
theorem compFinset_subset_supp {v : V} (hv : 0 < G.degree v) :
    compFinset G (G.connectedComponentMk v) ⊆ supp G := by
  intro w hw
  rw [mem_compFinset_mk] at hw
  rw [mem_supp]
  by_cases hwv : w = v
  · subst hwv; exact hv
  · exact pos_degree_of_reachable_of_ne G hw hwv

/-! #### The global minimum degree and `F` -/

/-- The minimum degree over the support (`0` if the support is empty). -/
noncomputable def globalMinDeg : ℕ :=
  if h : (supp G).Nonempty then (supp G).inf' h (fun v => G.degree v) else 0

/-- `F G = f G − g' (δ G)`, the global-minimum variant (rejected for Theorem 3.2 by the
design, plan §0.5; kept because `f⁻ ≤ F`, with equality on a connected support). -/
noncomputable def F : ℚ := potential G - g' (globalMinDeg G)

theorem globalMinDeg_le {v : V} (hv : v ∈ supp G) : globalMinDeg G ≤ G.degree v := by
  unfold globalMinDeg
  rw [dite_eq_left ⟨v, hv⟩]
  exact inf'_le (fun v => G.degree v) hv

theorem exists_degree_eq_globalMinDeg (hne : (supp G).Nonempty) :
    ∃ v ∈ supp G, G.degree v = globalMinDeg G := by
  unfold globalMinDeg
  rw [dite_eq_left hne]
  obtain ⟨v, hv, h⟩ := exists_mem_eq_inf' hne (fun v => G.degree v)
  exact ⟨v, hv, h.symm⟩

/-- A support vertex of minimum degree has the global minimum as its component's minimum. -/
theorem minDeg_eq_globalMinDeg {v : V} (hv : v ∈ supp G) (hd : G.degree v = globalMinDeg G) :
    minDeg G (G.connectedComponentMk v) = globalMinDeg G := by
  apply le_antisymm
  · rw [← hd]; exact minDeg_le G (self_mem_compFinset G v)
  · rw [le_minDeg_iff]
    intro w hw
    exact globalMinDeg_le G (compFinset_subset_supp G (mem_supp.1 hv) hw)

theorem potentialMinus_le_F : potentialMinus G ≤ F G := by
  unfold potentialMinus F
  suffices h : g' (globalMinDeg G) ≤ ∑ C : G.ConnectedComponent, g' (minDeg G C) by linarith
  by_cases hne : (supp G).Nonempty
  · obtain ⟨v, hv, hd⟩ := exists_degree_eq_globalMinDeg G hne
    rw [← minDeg_eq_globalMinDeg G hv hd]
    exact single_le_sum (fun C _ => g'_nonneg (minDeg G C)) (mem_univ _)
  · have h0 : globalMinDeg G = 0 := by unfold globalMinDeg; rw [dite_eq_right hne]
    rw [h0, g'_eq_zero_of_le_two (by norm_num)]
    exact sum_nonneg (fun C _ => g'_nonneg (minDeg G C))

/-- On a connected support only one component carries a non-zero `g' (δ(C))`. -/
theorem sum_g'_minDeg_of_connected (hne : (supp G).Nonempty)
    (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v) :
    ∑ C : G.ConnectedComponent, g' (minDeg G C) = g' (globalMinDeg G) := by
  obtain ⟨v₀, hv₀, hd₀⟩ := exists_degree_eq_globalMinDeg G hne
  rw [← minDeg_eq_globalMinDeg G hv₀ hd₀]
  apply sum_eq_single
  · intro C _ hC
    obtain ⟨w, hw, hdw⟩ := exists_degree_eq_minDeg G C
    have hw0 : G.degree w = 0 := by
      by_contra hpos
      have hws : w ∈ supp G := mem_supp.2 (Nat.pos_of_ne_zero hpos)
      have := (mem_compFinset G).1 hw
      exact hC (this ▸ SimpleGraph.ConnectedComponent.sound (hconn w hws v₀ hv₀))
    rw [← hdw, hw0]
    exact g'_eq_zero_of_le_two (by norm_num)
  · intro h; exact absurd (mem_univ _) h

theorem potentialMinus_eq_F_of_connected (hne : (supp G).Nonempty)
    (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v) :
    potentialMinus G = F G := by
  unfold potentialMinus F
  rw [sum_g'_minDeg_of_connected G hne hconn]

/-- The potential is a sum over the support. -/
theorem potential_eq_sum_supp : potential G = ∑ v ∈ supp G, g (G.degree v) := by
  unfold potential
  symm
  apply sum_subset (subset_univ _)
  intro v _ hv
  have : G.degree v = 0 := by rw [mem_supp] at hv; omega
  rw [this, g_zero]

/-- **B1**: a connected cubic support on `N` vertices has `f⁻ = N/6 − 1/6`. -/
theorem potentialMinus_cubic (hne : (supp G).Nonempty)
    (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v)
    (hcubic : ∀ v ∈ supp G, G.degree v = 3) :
    potentialMinus G = ((supp G).card : ℚ) / 6 - 1 / 6 := by
  rw [potentialMinus_eq_F_of_connected G hne hconn]
  unfold F
  have hg : globalMinDeg G = 3 := by
    obtain ⟨v, hv, hd⟩ := exists_degree_eq_globalMinDeg G hne
    rw [← hd, hcubic v hv]
  rw [hg, g'_three, potential_eq_sum_supp,
    sum_congr rfl (fun v hv => by rw [hcubic v hv, g_three]), sum_const, nsmul_eq_mul]
  ring

/-- **B1 floor**: a connected support with every degree `0` or `≥ 3` and some degree `≥ 4`
has `f⁻ ≥ 5/6` (`g 4 + 4 g 3 − 1/6`). -/
theorem potentialMinus_ge_five_sixths
    (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v)
    (hdeg : ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v) (h4 : ∃ v, 4 ≤ G.degree v) :
    5 / 6 ≤ potentialMinus G := by
  obtain ⟨v₁, hv₁⟩ := h4
  have hne : (supp G).Nonempty := ⟨v₁, mem_supp.2 (by omega)⟩
  rw [potentialMinus_eq_F_of_connected G hne hconn]
  unfold F
  have hg' := g'_le_sixth (globalMinDeg G)
  have hpot : 1 ≤ potential G := by
    unfold potential
    have h1 : ∑ v ∈ insert v₁ (G.neighborFinset v₁), g (G.degree v) ≤ ∑ v, g (G.degree v) :=
      sum_le_sum_of_subset_of_nonneg (subset_univ _) (fun v _ _ => g_nonneg _)
    have hnot : v₁ ∉ G.neighborFinset v₁ := by
      rw [SimpleGraph.mem_neighborFinset]; exact G.loopless.irrefl v₁
    rw [sum_insert hnot] at h1
    have h2 : g 4 ≤ g (G.degree v₁) := g_monotone hv₁
    have h3 : ((G.neighborFinset v₁).card : ℚ) * (1 / 6)
        ≤ ∑ v ∈ G.neighborFinset v₁, g (G.degree v) := by
      have := card_nsmul_le_sum (G.neighborFinset v₁) (fun v => g (G.degree v)) (1 / 6)
        (fun v hv => by
          rw [SimpleGraph.mem_neighborFinset] at hv
          rw [← g_three]; exact g_monotone (three_le_degree_of_adj G hdeg hv))
      rwa [nsmul_eq_mul] at this
    rw [SimpleGraph.card_neighborFinset_eq_degree] at h3
    have h4' : (4 : ℚ) ≤ (G.degree v₁ : ℚ) := by exact_mod_cast hv₁
    rw [g_four] at h2
    linarith
  linarith

end Components

/-! ### Disjoint unions: `f⁻` is additive -/

section Sup

variable {G₁ G₂ : SimpleGraph V} [DecidableRel G₁.Adj] [DecidableRel G₂.Adj]

/-- A walk in `G₁ ⊔ G₂` with disjoint supports stays inside `G₁` or inside `G₂`. -/
theorem reachable_sup_iff (hdisj : Disjoint (supp G₁) (supp G₂)) {u v : V} :
    (G₁ ⊔ G₂).Reachable u v ↔ G₁.Reachable u v ∨ G₂.Reachable u v := by
  constructor
  · rintro ⟨p⟩
    induction p with
    | nil => exact Or.inl (SimpleGraph.Reachable.refl _)
    | @cons a b c h p ih =>
      rcases (SimpleGraph.sup_adj _ _ _ _).1 h with h | h
      · rcases ih with ih | ih
        · exact Or.inl (h.reachable.trans ih)
        · by_cases hbc : b = c
          · subst hbc; exact Or.inl h.reachable
          · exfalso
            have hb1 : b ∈ supp G₁ :=
              mem_supp.2 ((G₁.degree_pos_iff_exists_adj b).2 ⟨a, h.symm⟩)
            have hb2 : b ∈ supp G₂ := mem_supp.2 (pos_degree_of_reachable_of_ne G₂ ih hbc)
            exact disjoint_left.1 hdisj hb1 hb2
      · rcases ih with ih | ih
        · by_cases hbc : b = c
          · subst hbc; exact Or.inr h.reachable
          · exfalso
            have hb2 : b ∈ supp G₂ :=
              mem_supp.2 ((G₂.degree_pos_iff_exists_adj b).2 ⟨a, h.symm⟩)
            have hb1 : b ∈ supp G₁ := mem_supp.2 (pos_degree_of_reachable_of_ne G₁ ih hbc)
            exact disjoint_left.1 hdisj hb1 hb2
        · exact Or.inr (h.reachable.trans ih)
  · rintro (h | h)
    · exact h.mono le_sup_left
    · exact h.mono le_sup_right

theorem degree_sup_of_degree_eq_zero_right {v : V} (h : G₂.degree v = 0) :
    (G₁ ⊔ G₂).degree v = G₁.degree v := by
  rw [← SimpleGraph.card_neighborFinset_eq_degree, ← SimpleGraph.card_neighborFinset_eq_degree,
    SimpleGraph.neighborFinset_sup]
  have : G₂.neighborFinset v = ∅ := by
    rw [← card_eq_zero, SimpleGraph.card_neighborFinset_eq_degree]; exact h
  rw [this, union_empty]

theorem degree_eq_zero_of_disjoint_supp (hdisj : Disjoint (supp G₁) (supp G₂)) {v : V}
    (hv : 0 < G₁.degree v) : G₂.degree v = 0 := by
  by_contra hne
  exact disjoint_left.1 hdisj (mem_supp.2 hv) (mem_supp.2 (Nat.pos_of_ne_zero hne))

/-- The component of a `G₁`-support vertex in `G₁ ⊔ G₂` is its component in `G₁`. -/
theorem compFinset_sup_eq (hdisj : Disjoint (supp G₁) (supp G₂)) {v : V}
    (hv : 0 < G₁.degree v) :
    compFinset (G₁ ⊔ G₂) ((G₁ ⊔ G₂).connectedComponentMk v)
      = compFinset G₁ (G₁.connectedComponentMk v) := by
  ext w
  rw [mem_compFinset_mk, mem_compFinset_mk, reachable_sup_iff hdisj]
  constructor
  · rintro (h | h)
    · exact h
    · have hv2 := degree_eq_zero_of_disjoint_supp hdisj hv
      obtain rfl := eq_of_reachable_of_degree_eq_zero G₂ h.symm hv2
      exact SimpleGraph.Reachable.refl _
  · exact Or.inl

theorem degree_sup_eq_of_mem_comp (hdisj : Disjoint (supp G₁) (supp G₂)) {v w : V}
    (hv : 0 < G₁.degree v) (hw : w ∈ compFinset G₁ (G₁.connectedComponentMk v)) :
    (G₁ ⊔ G₂).degree w = G₁.degree w := by
  apply degree_sup_of_degree_eq_zero_right
  exact degree_eq_zero_of_disjoint_supp hdisj (mem_supp.1 (compFinset_subset_supp G₁ hv hw))

theorem vertexTerm_sup_left (hdisj : Disjoint (supp G₁) (supp G₂)) {v : V}
    (hv : 0 < G₁.degree v) : vertexTerm (G₁ ⊔ G₂) v = vertexTerm G₁ v := by
  have hC := compFinset_sup_eq (G₂ := G₂) hdisj hv
  have hd : (G₁ ⊔ G₂).degree v = G₁.degree v :=
    degree_sup_eq_of_mem_comp hdisj hv (self_mem_compFinset G₁ v)
  have hm : minDeg (G₁ ⊔ G₂) ((G₁ ⊔ G₂).connectedComponentMk v)
      = minDeg G₁ (G₁.connectedComponentMk v) := by
    unfold minDeg
    exact inf'_congr _ hC (fun w hw => degree_sup_eq_of_mem_comp hdisj hv (hC ▸ hw))
  unfold vertexTerm
  rw [hd, hm, hC]

/-- `vertexTerm` does not depend on the decidability instance. -/
theorem vertexTerm_congr {G G' : SimpleGraph V} (i : DecidableRel G.Adj)
    (i' : DecidableRel G'.Adj) (h : G = G') (v : V) :
    @vertexTerm V _ _ G i v = @vertexTerm V _ _ G' i' v := by
  subst h
  have : i = i' := Subsingleton.elim _ _
  subst this
  rfl

theorem vertexTerm_sup_comm (v : V) : vertexTerm (G₁ ⊔ G₂) v = vertexTerm (G₂ ⊔ G₁) v :=
  vertexTerm_congr _ _ (sup_comm _ _) v

theorem vertexTerm_sup (hdisj : Disjoint (supp G₁) (supp G₂)) (v : V) :
    vertexTerm (G₁ ⊔ G₂) v = vertexTerm G₁ v + vertexTerm G₂ v := by
  by_cases h1 : 0 < G₁.degree v
  · have h2 := degree_eq_zero_of_disjoint_supp hdisj h1
    rw [vertexTerm_sup_left hdisj h1, vertexTerm_eq_zero_of_degree_eq_zero G₂ h2, add_zero]
  · have h1' : G₁.degree v = 0 := Nat.eq_zero_of_not_pos h1
    by_cases h2 : 0 < G₂.degree v
    · rw [vertexTerm_eq_zero_of_degree_eq_zero G₁ h1', zero_add, vertexTerm_sup_comm]
      exact vertexTerm_sup_left hdisj.symm h2
    · have h2' : G₂.degree v = 0 := Nat.eq_zero_of_not_pos h2
      have hs : (G₁ ⊔ G₂).degree v = 0 := by
        rw [degree_sup_of_degree_eq_zero_right h2']; exact h1'
      rw [vertexTerm_eq_zero_of_degree_eq_zero _ hs, vertexTerm_eq_zero_of_degree_eq_zero _ h1',
        vertexTerm_eq_zero_of_degree_eq_zero _ h2', add_zero]

/-- **Additivity**: `f⁻ (G₁ ⊔ G₂) = f⁻ G₁ + f⁻ G₂` when the supports are disjoint. -/
theorem potentialMinus_add (hdisj : Disjoint (supp G₁) (supp G₂)) :
    potentialMinus (G₁ ⊔ G₂) = potentialMinus G₁ + potentialMinus G₂ := by
  rw [potentialMinus_eq_sum_vertexTerm (G₁ ⊔ G₂), potentialMinus_eq_sum_vertexTerm G₁,
    potentialMinus_eq_sum_vertexTerm G₂, ← sum_add_distrib]
  exact sum_congr rfl (fun v _ => vertexTerm_sup hdisj v)

end Sup

end MOSPFormalization.DegreeBound
