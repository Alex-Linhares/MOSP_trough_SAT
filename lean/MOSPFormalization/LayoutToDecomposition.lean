/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Layout to Path Decomposition (VS ≥ PW direction)

Given a linear layout σ with vertex separation k, we construct a path
decomposition of width ≤ k. This proves PW(G) ≤ VS(G) for the layout.

Construction: For each position i, bag(i) := {σ⁻¹(i)} ∪ activeSuffix(G, σ, i).
-/

import MOSPFormalization.VertexSeparation
import MOSPFormalization.Pathwidth

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The bag at position i in the decomposition derived from layout σ:
    the vertex at position i plus all active suffix vertices. -/
def layoutBag (σ : LinearLayout V) (i : Fin (Fintype.card V)) : Finset V :=
  {σ.symm i} ∪ activeSuffix G σ i.val

theorem mem_layoutBag_iff (σ : LinearLayout V) (i : Fin (Fintype.card V)) (v : V) :
    v ∈ layoutBag G σ i ↔ v = σ.symm i ∨ v ∈ activeSuffix G σ i.val := by
  simp [layoutBag]

/-- Construct a path decomposition from a linear layout (when V is nonempty). -/
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

/-- Each bag in the layout decomposition has size at most vertexSepAt + 1. -/
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
  -- width = sup(bag card) - 1 ≤ sup(vertexSepAt) = vertexSepOfLayout
  -- Because each bag card ≤ vertexSepAt + 1
  set P := layoutToDecomposition G σ hn
  have hlen : P.length = Fintype.card V - 1 := rfl
  have hcard : Fintype.card V - 1 + 1 = Fintype.card V :=
    Nat.sub_one_add_one_eq_of_pos (Nat.pos_of_ne_zero hn)
  -- Unfold vertexSepOfLayout with hn
  unfold vertexSepOfLayout
  simp only [dite_eq_right hn]
  -- Goal: P.width ≤ sup'(vertexSepAt)
  -- P.width = sup'(bag card) - 1
  -- Strategy: show sup'(bag card) ≤ sup'(vertexSepAt) + 1, hence - 1 ≤ sup'(vertexSepAt)
  unfold PathDecomposition.width
  -- Goal: sup'(bag card) - 1 ≤ sup'(vertexSepAt)
  -- It suffices to show sup'(bag card) ≤ sup'(vertexSepAt) + 1
  have hsup_le : Finset.sup' Finset.univ
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
      (fun i : Fin (P.length + 1) => (P.bag i).card)
      ≤ Finset.sup' Finset.univ
        (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero hn⟩⟩)
        (fun i : Fin (Fintype.card V) => vertexSepAt G σ i.val) + 1 := by
    apply Finset.sup'_le
    intro i _
    -- Need: (P.bag i).card ≤ sup'(vertexSepAt) + 1
    -- Step 1: (P.bag i).card ≤ vertexSepAt G σ i.val + 1
    have hival : i.val < Fintype.card V := by omega
    have hbag : (P.bag i).card ≤ vertexSepAt G σ i.val + 1 := by
      show (layoutBag G σ ⟨i.val, by omega⟩).card ≤ vertexSepAt G σ i.val + 1
      exact layoutBag_card_le G σ ⟨i.val, by omega⟩
    -- Step 2: vertexSepAt G σ i.val ≤ sup'(vertexSepAt)
    have hmem : (⟨i.val, hival⟩ : Fin (Fintype.card V)) ∈
        (Finset.univ : Finset (Fin (Fintype.card V))) := Finset.mem_univ _
    have hle : vertexSepAt G σ i.val ≤ Finset.sup' Finset.univ
        (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero hn⟩⟩)
        (fun j : Fin (Fintype.card V) => vertexSepAt G σ j.val) := by
      exact Finset.le_sup' (fun j : Fin (Fintype.card V) => vertexSepAt G σ j.val) hmem
    omega
  omega

/-- The vertex separation of a layout bounds the pathwidth from above.
    This is the PW ≤ VS direction (for a specific layout). -/
theorem pathwidth_le_vertexSepOfLayout (σ : LinearLayout V) :
    pathwidth G ≤ vertexSepOfLayout G σ := by
  by_cases hn : Fintype.card V = 0
  · -- If V is empty, pathwidth = 0 since trivial decomposition has width |V| - 1 = 0
    have : pathwidth G = 0 := by
      apply Nat.le_antisymm
      · calc pathwidth G ≤ Fintype.card V - 1 := pathwidth_le_card_sub_one G
          _ = 0 := by omega
      · exact Nat.zero_le _
    rw [this]
    exact Nat.zero_le _
  · calc pathwidth G ≤ (layoutToDecomposition G σ hn).width := pathwidth_le_width G _
      _ ≤ vertexSepOfLayout G σ := layoutDecomposition_width_le G σ hn

end MOSPFormalization
