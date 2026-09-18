/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Path Decomposition to Layout (VS ≤ PW direction)

Given a path decomposition of width k, we construct a linear layout
with vertex separation ≤ k. This proves VS(G) ≤ PW(G).

Construction: Sort vertices by their `lastBag` index (breaking ties arbitrarily).
Key invariant: every active suffix vertex at any position is contained in the
bag at `lastBag(current_vertex)`, giving |activeSuffix| ≤ |bag| - 1 ≤ width.
-/

import MOSPFormalization.VertexSeparation
import MOSPFormalization.Pathwidth
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Data.Fintype.Sort
import Mathlib.Data.List.NodupEquivFin
import Mathlib.Data.Finset.Sort
import Mathlib.Data.Prod.Lex

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- A layout is **monotone** with respect to a path decomposition P if vertices with
    smaller lastBag indices are placed earlier in the layout. -/
def IsMonotoneLayout (P : PathDecomposition G) (σ : LinearLayout V) : Prop :=
  ∀ u v : V, P.lastBag u < P.lastBag v → (σ u).val < (σ v).val

/-- Key lemma: if σ is monotone w.r.t. P, then at each position i, every active suffix
    vertex is in the bag at lastBag of the current vertex. -/
theorem activeSuffix_subset_lastBag_of_monotone (P : PathDecomposition G)
    (σ : LinearLayout V) (hmono : IsMonotoneLayout G P σ)
    (i : Fin (Fintype.card V)) :
    activeSuffix G σ i.val ⊆
      P.bag (P.lastBag (σ.symm i)) := by
  intro w hw
  rw [mem_activeSuffix_iff] at hw
  obtain ⟨hw_suffix, u, hu_prefix, hadj⟩ := hw
  rw [mem_prefixSet_iff] at hu_prefix
  -- w is in suffix: σ(w) > i, so w comes after current vertex
  -- u is in prefix: σ(u) ≤ i, so u comes before or at current vertex
  let v := σ.symm i  -- current vertex
  have hσv : σ v = i := by simp [v]
  -- By monotonicity contrapositive: σ(w) > σ(v) = i implies lastBag(w) ≥ lastBag(v)
  have hw_last_ge : P.lastBag v ≤ P.lastBag w := by
    by_contra h
    push Not at h
    have := hmono w v h
    rw [hσv] at this
    omega
  -- By monotonicity (or directly): σ(u) ≤ i = σ(v) implies lastBag(u) ≤ lastBag(v)
  have hu_last_le : P.lastBag u ≤ P.lastBag v := by
    by_contra h
    push Not at h
    have := hmono v u h
    rw [hσv] at this
    omega
  -- By edge coverage: ∃ bag l containing both u and w
  obtain ⟨l, hul, hwl⟩ := P.edge_coverage u w hadj
  -- u ∈ bag(l) implies l ≤ lastBag(u) ≤ lastBag(v)
  have hl_le : l ≤ P.lastBag v := by
    calc l ≤ P.lastBag u := (P.mem_bag_iff_between u l).mp hul |>.2
      _ ≤ P.lastBag v := hu_last_le
  -- w ∈ bag(l) implies firstBag(w) ≤ l
  have hfirst_le : P.firstBag w ≤ l := (P.mem_bag_iff_between w l).mp hwl |>.1
  -- So firstBag(w) ≤ l ≤ lastBag(v) ≤ lastBag(w)
  -- By interval property: w ∈ bag(lastBag(v))
  rw [P.mem_bag_iff_between]
  exact ⟨le_trans hfirst_le hl_le, hw_last_ge⟩

/-- If σ is monotone w.r.t. P, then vertexSepOfLayout σ ≤ P.width. -/
theorem vertexSepOfLayout_le_width_of_monotone (P : PathDecomposition G)
    (σ : LinearLayout V) (hmono : IsMonotoneLayout G P σ) :
    vertexSepOfLayout G σ ≤ P.width := by
  unfold vertexSepOfLayout
  by_cases hn : Fintype.card V = 0
  · simp [hn]
  · simp only [dite_eq_right hn]
    apply Finset.sup'_le
    intro i _
    -- vertexSepAt = |activeSuffix|
    unfold vertexSepAt
    -- activeSuffix ⊆ bag(lastBag(σ⁻¹(i)))
    have hsub := activeSuffix_subset_lastBag_of_monotone G P σ hmono
        ⟨i.val, by omega⟩
    have hcard := Finset.card_le_card hsub
    -- |bag(j)| ≤ width + 1 for any j
    have hbag := P.bag_card_le_width_add_one (P.lastBag (σ.symm ⟨i.val, by omega⟩))
    -- But we also know σ⁻¹(i) ∈ bag(lastBag(σ⁻¹(i))) and σ⁻¹(i) ∉ activeSuffix
    -- (since σ(σ⁻¹(i)) = i, so σ⁻¹(i) is NOT in the suffix at i)
    -- So |activeSuffix| ≤ |bag| - 1 ≤ width
    have hv_in_bag : σ.symm ⟨i.val, by omega⟩ ∈
        P.bag (P.lastBag (σ.symm ⟨i.val, by omega⟩)) := P.mem_bag_lastBag _
    have hv_not_in_suffix : σ.symm ⟨i.val, by omega⟩ ∉ activeSuffix G σ i.val := by
      rw [mem_activeSuffix_iff]
      push Not
      intro h
      exfalso; simp at h
    -- activeSuffix ⊆ bag \ {current vertex}
    have hsub' : activeSuffix G σ i.val ⊆
        (P.bag (P.lastBag (σ.symm ⟨i.val, by omega⟩))).erase
          (σ.symm ⟨i.val, by omega⟩) := by
      intro w hw
      rw [Finset.mem_erase]
      constructor
      · intro heq
        rw [heq] at hw
        exact hv_not_in_suffix hw
      · exact hsub hw
    calc (activeSuffix G σ i.val).card
        ≤ ((P.bag (P.lastBag (σ.symm ⟨i.val, by omega⟩))).erase
            (σ.symm ⟨i.val, by omega⟩)).card := Finset.card_le_card hsub'
      _ = (P.bag (P.lastBag (σ.symm ⟨i.val, by omega⟩))).card - 1 :=
          Finset.card_erase_of_mem hv_in_bag
      _ ≤ P.width := by omega

/-- A monotone layout with respect to P exists. We construct it by defining a
    linear order on V via (lastBag, tiebreaker) and using the order-preserving
    bijection to Fin n. -/
theorem exists_monotone_layout (P : PathDecomposition G) :
    ∃ σ : LinearLayout V, IsMonotoneLayout G P σ := by
  -- Define a linear order on V using (lastBag v, defaultEquiv v) as the sort key
  -- where defaultEquiv : V ≃ Fin n gives a tiebreaker
  classical
  let e := Fintype.equivFin V
  -- Define the key function: V → Fin (P.length + 1) × Fin (Fintype.card V)
  let key : V → Fin (P.length + 1) × Fin (Fintype.card V) :=
    fun v => (P.lastBag v, e v)
  -- key is injective (since e is injective in the second component)
  have hkey_inj : Function.Injective key := by
    intro u v huv
    have : e u = e v := congr_arg Prod.snd huv
    exact e.injective this
  -- Lift a LinearOrder on V via the injective function v ↦ toLex (lastBag v, e v).
  -- Lexicographic order on Fin × Fin is a LinearOrder; lifting it gives a LinearOrder on V
  -- where lastBag u < lastBag v implies u < v.
  let _ : LinearOrder V :=
    LinearOrder.lift' (fun v => toLex (P.lastBag v, e v)) (by
      intro u v huv
      have huv' : (P.lastBag u, e u) = (P.lastBag v, e v) := huv
      have : e u = e v := congr_arg Prod.snd huv'
      exact e.injective this)
  -- Use the order-preserving bijection Fin n ≃o V from monoEquivOfFin
  let iso : Fin (Fintype.card V) ≃o V := monoEquivOfFin V rfl
  -- The inverse gives V ≃ Fin n, and it is strictly monotone (order-reflecting)
  let σ : LinearLayout V := iso.symm.toEquiv
  use σ
  intro u v hlast
  -- We need: (σ u).val < (σ v).val, i.e., iso.symm u < iso.symm v
  -- Since iso.symm is an OrderIso, it preserves strict order
  -- So it suffices to show u < v in our LinearOrder on V
  -- In our order: u < v iff toLex (lastBag u, e u) < toLex (lastBag v, e v)
  -- Since lastBag u < lastBag v, this holds by left lexicographic comparison
  have hu_lt_v : toLex (P.lastBag u, e u) < toLex (P.lastBag v, e v) := by
    rw [Prod.Lex.toLex_lt_toLex]
    exact Or.inl hlast
  -- Therefore u < v in our lifted LinearOrder
  have huv : u < v := hu_lt_v
  -- iso.symm is strictly monotone, so iso.symm u < iso.symm v
  have := iso.symm.strictMono huv
  exact this

/-- For any path decomposition P, there exists a layout whose vertex separation
    is at most the width of P. -/
theorem exists_layout_of_decomposition (P : PathDecomposition G) :
    ∃ σ : LinearLayout V, vertexSepOfLayout G σ ≤ P.width := by
  obtain ⟨σ, hmono⟩ := exists_monotone_layout G P
  exact ⟨σ, vertexSepOfLayout_le_width_of_monotone G P σ hmono⟩

/-- Vertex separation ≤ pathwidth. -/
theorem vertexSeparation_le_pathwidth :
    vertexSeparation G ≤ pathwidth G := by
  unfold pathwidth
  have hne : (Set.range (fun P : PathDecomposition G => P.width)).Nonempty :=
    ⟨_, ⟨PathDecomposition.trivial G, rfl⟩⟩
  rw [le_csInf_iff_of_wellFoundedLT hne]
  intro k ⟨P, hP⟩
  obtain ⟨σ, hσ⟩ := exists_layout_of_decomposition G P
  calc vertexSeparation G ≤ vertexSepOfLayout G σ :=
        vertexSeparation_le_vertexSepOfLayout G σ
    _ ≤ P.width := hσ
    _ = k := hP

end MOSPFormalization
