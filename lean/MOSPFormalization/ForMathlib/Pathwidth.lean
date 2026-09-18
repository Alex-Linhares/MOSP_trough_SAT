/-
Copyright (c) 2024 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.
Authors: Alexandre Linhares
-/
import MOSPFormalization.ForMathlib.PathDecomposition
import MOSPFormalization.ForMathlib.VertexSeparation
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Data.Fintype.Sort
import Mathlib.Data.Prod.Lex

/-!
# Pathwidth equals vertex separation (Kinnersley's theorem)

This file proves that the pathwidth of a finite simple graph equals its vertex separation
number, following Kinnersley (1992).

The proof proceeds in two directions:

* **PW ≤ VS** (`pathwidth_le_vertexSeparation`): Given any linear layout `σ`, we construct
  a path decomposition whose bags are `{σ⁻¹(i)} ∪ activeSuffix(G, σ, i)`. The width of this
  decomposition is at most the vertex separation of `σ`.

* **VS ≤ PW** (`vertexSeparation_le_pathwidth`): Given any path decomposition `P`, we construct
  a layout by sorting vertices according to their `lastBag` index. The key invariant is that
  every active suffix vertex at any position must lie in the bag corresponding to the current
  vertex's `lastBag`, giving `|activeSuffix| ≤ |bag| - 1 ≤ width`.

## Main results

* `SimpleGraph.vertexSeparation_eq_pathwidth`: The vertex separation number of a finite
  simple graph equals its pathwidth. This is Kinnersley's theorem.

## References

* [R. Kinnersley, *The vertex separation number of a graph equals its path-width*][kinnersley1992]
-/

namespace SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Direction 1: PW ≤ VS (Layout → Decomposition) -/

section LayoutToDecomposition

/-- The bag at position `i` in the decomposition derived from layout `σ`:
the vertex at position `i` together with all active suffix vertices. -/
def layoutBag (σ : LinearLayout V) (i : Fin (Fintype.card V)) : Finset V :=
  {σ.symm i} ∪ activeSuffix G σ i.val

theorem mem_layoutBag_iff (σ : LinearLayout V) (i : Fin (Fintype.card V)) (v : V) :
    v ∈ layoutBag G σ i ↔ v = σ.symm i ∨ v ∈ activeSuffix G σ i.val := by
  simp [layoutBag]

/-- Construct a path decomposition from a linear layout (when `V` is nonempty). -/
noncomputable def layoutToDecomposition (σ : LinearLayout V)
    (hn : Fintype.card V ≠ 0) : PathDecomposition G where
  length := Fintype.card V - 1
  bag := fun i => layoutBag G σ ⟨i.val, by omega⟩
  vertex_coverage := by
    intro v
    have hlt : (σ v).val < Fintype.card V := (σ v).isLt
    use ⟨(σ v).val, by omega⟩
    rw [mem_layoutBag_iff]
    left
    simp
  edge_coverage := by
    intro u v huv
    have hlu : (σ u).val < Fintype.card V := (σ u).isLt
    have hlv : (σ v).val < Fintype.card V := (σ v).isLt
    by_cases hlt : (σ u).val < (σ v).val
    · -- u comes first: at position σ(u), both are in the bag
      refine ⟨⟨(σ u).val, by omega⟩, ?_, ?_⟩
      · rw [mem_layoutBag_iff]; left; simp
      · rw [mem_layoutBag_iff]; right
        rw [mem_activeSuffix_iff]
        constructor
        · show (σ v).val > (σ u).val; omega
        · exact ⟨u, by rw [mem_prefixSet_iff], huv⟩
    · -- v comes first
      have hneq : (σ u).val ≠ (σ v).val := by
        intro heq
        exact G.ne_of_adj huv (σ.injective (Fin.ext heq))
      have hlt' : (σ v).val < (σ u).val := by omega
      refine ⟨⟨(σ v).val, by omega⟩, ?_, ?_⟩
      · rw [mem_layoutBag_iff]; right
        rw [mem_activeSuffix_iff]
        constructor
        · show (σ u).val > (σ v).val; omega
        · exact ⟨v, by rw [mem_prefixSet_iff], huv.symm⟩
      · rw [mem_layoutBag_iff]; left; simp
  interval := by
    intro v i j k hij hjk hvi hvk
    have hival : i.val < Fintype.card V := by omega
    have hjval : j.val < Fintype.card V := by omega
    have hkval : k.val < Fintype.card V := by omega
    rw [mem_layoutBag_iff] at hvi hvk ⊢
    by_cases hvj : (σ v).val > (⟨j.val, hjval⟩ : Fin (Fintype.card V)).val
    · -- v is in the suffix at position j
      right
      rw [mem_activeSuffix_iff]
      constructor
      · exact hvj
      · -- v has a prefix neighbor at ≤ i ≤ j
        rcases hvi with rfl | hvi_active
        · -- v = σ⁻¹(i), so σ(v) = i.val, but σ(v) > j.val ≥ i.val
          exfalso
          simp at hvj
          have : (σ (σ.symm ⟨i.val, hival⟩)).val = i.val := by simp
          omega
        · rw [mem_activeSuffix_iff] at hvi_active
          obtain ⟨_, u, hu_prefix, hadj⟩ := hvi_active
          rw [mem_prefixSet_iff] at hu_prefix
          exact ⟨u, by rw [mem_prefixSet_iff]; simp at hu_prefix ⊢; omega, hadj⟩
    · -- σ(v) ≤ j
      simp at hvj
      by_cases hvj_eq : (σ v).val = (⟨j.val, hjval⟩ : Fin (Fintype.card V)).val
      · -- v = σ⁻¹(j)
        left
        have : σ v = ⟨j.val, hjval⟩ := Fin.ext (by simp at hvj_eq ⊢; exact hvj_eq)
        rw [← this]; simp
      · -- σ(v) < j
        exfalso
        have hvlt : (σ v).val < j.val := by simp at hvj_eq; omega
        rcases hvk with rfl | hvk_active
        · -- v = σ⁻¹(k), so σ(v) = k.val ≥ j.val, contradiction
          simp at hvlt
          omega
        · -- v ∈ activeSuffix at k, so σ(v) > k.val ≥ j.val, contradiction
          rw [mem_activeSuffix_iff] at hvk_active
          simp at hvk_active
          omega

/-- Each bag in the layout decomposition has at most `vertexSepAt + 1` elements. -/
theorem layoutBag_card_le (σ : LinearLayout V) (i : Fin (Fintype.card V)) :
    (layoutBag G σ i).card ≤ vertexSepAt G σ i.val + 1 := by
  unfold layoutBag
  calc (({σ.symm i} ∪ activeSuffix G σ i.val) : Finset V).card
      ≤ ({σ.symm i} : Finset V).card + (activeSuffix G σ i.val).card :=
        Finset.card_union_le _ _
    _ = 1 + (activeSuffix G σ i.val).card := by simp
    _ = vertexSepAt G σ i.val + 1 := by unfold vertexSepAt; omega

/-- The width of the layout decomposition is at most the vertex separation of the layout. -/
theorem layoutDecomposition_width_le (σ : LinearLayout V) (hn : Fintype.card V ≠ 0) :
    (layoutToDecomposition G σ hn).width ≤ vertexSepOfLayout G σ := by
  set P := layoutToDecomposition G σ hn
  have hlen : P.length = Fintype.card V - 1 := rfl
  have hcard : Fintype.card V - 1 + 1 = Fintype.card V :=
    Nat.sub_one_add_one_eq_of_pos (Nat.pos_of_ne_zero hn)
  unfold vertexSepOfLayout
  simp only [dite_eq_right hn]
  unfold PathDecomposition.width
  have hsup_le : Finset.sup' Finset.univ
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
      (fun i : Fin (P.length + 1) => (P.bag i).card)
      ≤ Finset.sup' Finset.univ
        (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero hn⟩⟩)
        (fun i : Fin (Fintype.card V) => vertexSepAt G σ i.val) + 1 := by
    apply Finset.sup'_le
    intro i _
    have hival : i.val < Fintype.card V := by omega
    have hbag : (P.bag i).card ≤ vertexSepAt G σ i.val + 1 := by
      show (layoutBag G σ ⟨i.val, by omega⟩).card ≤ vertexSepAt G σ i.val + 1
      exact layoutBag_card_le G σ ⟨i.val, by omega⟩
    have hmem : (⟨i.val, hival⟩ : Fin (Fintype.card V)) ∈
        (Finset.univ : Finset (Fin (Fintype.card V))) := Finset.mem_univ _
    have hle : vertexSepAt G σ i.val ≤ Finset.sup' Finset.univ
        (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero hn⟩⟩)
        (fun j : Fin (Fintype.card V) => vertexSepAt G σ j.val) := by
      exact Finset.le_sup' (fun j : Fin (Fintype.card V) => vertexSepAt G σ j.val) hmem
    omega
  omega

/-- For any layout `σ`, the pathwidth is at most the vertex separation of `σ`. -/
theorem pathwidth_le_vertexSepOfLayout (σ : LinearLayout V) :
    G.pathwidth ≤ vertexSepOfLayout G σ := by
  by_cases hn : Fintype.card V = 0
  · have : G.pathwidth = 0 := by
      apply Nat.le_antisymm
      · calc G.pathwidth ≤ Fintype.card V - 1 := pathwidth_le_card_sub_one G
          _ = 0 := by omega
      · exact Nat.zero_le _
    rw [this]
    exact Nat.zero_le _
  · calc G.pathwidth ≤ (layoutToDecomposition G σ hn).width := pathwidth_le_width G _
      _ ≤ vertexSepOfLayout G σ := layoutDecomposition_width_le G σ hn

theorem pathwidth_le_vertexSeparation : G.pathwidth ≤ G.vertexSeparation := by
  unfold vertexSeparation
  have hne : (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ)).Nonempty :=
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  rw [le_csInf_iff_of_wellFoundedLT hne]
  intro b ⟨σ, hσ⟩; rw [← hσ]
  exact pathwidth_le_vertexSepOfLayout G σ

end LayoutToDecomposition

/-! ### Direction 2: VS ≤ PW (Decomposition → Layout) -/

section DecompositionToLayout

/-- A layout is *monotone* with respect to a path decomposition `P` if vertices
with smaller `lastBag` indices are placed earlier. -/
def IsMonotoneLayout (P : PathDecomposition G) (σ : LinearLayout V) : Prop :=
  ∀ u v : V, P.lastBag u < P.lastBag v → (σ u).val < (σ v).val

/-- If `σ` is monotone w.r.t. `P`, then at each position, every active suffix
vertex lies in the bag at `lastBag` of the current vertex. -/
theorem activeSuffix_subset_lastBag (P : PathDecomposition G)
    (σ : LinearLayout V) (hmono : IsMonotoneLayout G P σ)
    (i : Fin (Fintype.card V)) :
    activeSuffix G σ i.val ⊆ P.bag (P.lastBag (σ.symm i)) := by
  intro w hw
  rw [mem_activeSuffix_iff] at hw
  obtain ⟨hw_suffix, u, hu_prefix, hadj⟩ := hw
  rw [mem_prefixSet_iff] at hu_prefix
  let v := σ.symm i
  have hσv : σ v = i := by simp [v]
  have hw_last_ge : P.lastBag v ≤ P.lastBag w := by
    by_contra h
    push Not at h
    have := hmono w v h
    rw [hσv] at this
    omega
  have hu_last_le : P.lastBag u ≤ P.lastBag v := by
    by_contra h
    push Not at h
    have := hmono v u h
    rw [hσv] at this
    omega
  obtain ⟨l, hul, hwl⟩ := P.edge_coverage u w hadj
  rw [P.mem_bag_iff_between]
  exact ⟨le_trans ((P.mem_bag_iff_between w l).mp hwl).1
           (le_trans ((P.mem_bag_iff_between u l).mp hul).2 hu_last_le),
         hw_last_ge⟩

/-- If `σ` is monotone w.r.t. `P`, then `vertexSepOfLayout σ ≤ P.width`. -/
theorem vertexSepOfLayout_le_width_of_monotone (P : PathDecomposition G)
    (σ : LinearLayout V) (hmono : IsMonotoneLayout G P σ) :
    vertexSepOfLayout G σ ≤ P.width := by
  unfold vertexSepOfLayout
  by_cases hn : Fintype.card V = 0
  · simp [hn]
  · simp only [dite_eq_right hn]
    apply Finset.sup'_le
    intro i _
    unfold vertexSepAt
    have hsub := activeSuffix_subset_lastBag G P σ hmono ⟨i.val, by omega⟩
    have hv_in_bag : σ.symm ⟨i.val, by omega⟩ ∈
        P.bag (P.lastBag (σ.symm ⟨i.val, by omega⟩)) := P.mem_bag_lastBag _
    have hv_not_in_suffix : σ.symm ⟨i.val, by omega⟩ ∉ activeSuffix G σ i.val := by
      rw [mem_activeSuffix_iff]
      push Not
      intro h
      exfalso; simp at h
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
      _ ≤ P.width := by
          have := P.bag_card_le_width_add_one (P.lastBag (σ.symm ⟨i.val, by omega⟩))
          omega

omit [DecidableRel G.Adj] in
/-- A monotone layout exists for any path decomposition: sort vertices by `lastBag`,
breaking ties with an arbitrary bijection. -/
theorem exists_monotone_layout (P : PathDecomposition G) :
    ∃ σ : LinearLayout V, IsMonotoneLayout G P σ := by
  classical
  let e := Fintype.equivFin V
  let _ : LinearOrder V :=
    LinearOrder.lift' (fun v => toLex (P.lastBag v, e v)) (by
      intro u v huv
      exact e.injective (congr_arg Prod.snd huv))
  let iso := monoEquivOfFin V rfl
  use iso.symm.toEquiv
  intro u v hlast
  exact iso.symm.strictMono (Prod.Lex.toLex_lt_toLex.mpr (Or.inl hlast))

/-- For any path decomposition, there exists a layout whose vertex separation is at
most the width of the decomposition. -/
theorem exists_layout_of_decomposition (P : PathDecomposition G) :
    ∃ σ : LinearLayout V, vertexSepOfLayout G σ ≤ P.width := by
  obtain ⟨σ, hmono⟩ := exists_monotone_layout G P
  exact ⟨σ, vertexSepOfLayout_le_width_of_monotone G P σ hmono⟩

theorem vertexSeparation_le_pathwidth : G.vertexSeparation ≤ G.pathwidth := by
  unfold pathwidth
  have hne : (Set.range (fun P : PathDecomposition G => P.width)).Nonempty :=
    ⟨_, ⟨PathDecomposition.trivial G, rfl⟩⟩
  rw [le_csInf_iff_of_wellFoundedLT hne]
  intro k ⟨P, hP⟩
  obtain ⟨σ, hσ⟩ := exists_layout_of_decomposition G P
  calc G.vertexSeparation ≤ vertexSepOfLayout G σ :=
        vertexSeparation_le_vertexSepOfLayout G σ
    _ ≤ P.width := hσ
    _ = k := hP

end DecompositionToLayout

/-! ### Kinnersley's theorem -/

/-- **Kinnersley's theorem**: The vertex separation number of a finite simple graph
equals its pathwidth.

This was proved by Nancy Kinnersley in 1992. The two directions are:
* `pathwidth_le_vertexSeparation`: Any layout gives a path decomposition of at most
  that width.
* `vertexSeparation_le_pathwidth`: Any path decomposition gives a layout of at most
  that vertex separation.
-/
theorem vertexSeparation_eq_pathwidth :
    G.vertexSeparation = G.pathwidth :=
  le_antisymm (vertexSeparation_le_pathwidth G) (pathwidth_le_vertexSeparation G)

end SimpleGraph
