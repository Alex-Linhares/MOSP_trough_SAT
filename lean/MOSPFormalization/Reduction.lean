/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

# MOSP ≤ Pathwidth + 1 Reduction

The main theorem: for a reduced MOSP instance M,
  mospValue(M) ≤ pathwidth(agreementGraph(M)) + 1

## Proof strategy

The proof goes through path decomposition bags:

1. Given any path decomposition `D` of width k of the agreement graph:
2. Construct a monotone layout σ from `D` (sorting by lastBag).
3. At each position i, active customers inject into `D.bag(D.lastBag(σ⁻¹(i)))`.
4. This bag has size ≤ k + 1, so openStacksAt ≤ k + 1.
5. Taking max and inf: mospValue ≤ pathwidth + 1.

Step 3 requires Hall's marriage theorem under `IsReduced` and remains as sorry.
-/

import MOSPFormalization.VSEquivPW
import MOSPFormalization.OpenStacks

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]

namespace MOSPInstance

variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- A customer with a pattern at or before `i` and one strictly after `i` has a
    pattern in the active suffix of the agreement graph.

    The strict hypothesis is stated explicitly rather than taken from
    `isActive`, which no longer implies it. `isActive` is inclusive at both
    ends, so a customer requiring a single pattern is active at that pattern's
    own position while having nothing strictly beyond it — and the argument
    below needs two distinct patterns, one on each side. Such a customer opens
    and closes in one step and never contributes to a separator, so nothing is
    lost; it simply is not this lemma's business. -/
theorem active_customer_has_activeSuffix_pattern (σ : LinearLayout Pt) (c : C) (i : ℕ)
    (hpre : ((M.patterns c).filter (fun p => (σ p).val ≤ i)).Nonempty)
    (hsuf : ((M.patterns c).filter (fun p => (σ p).val > i)).Nonempty) :
    ∃ p, M.requires c p ∧ p ∈ activeSuffix M.agreementGraph σ i := by
  obtain ⟨p, hp⟩ := hsuf
  obtain ⟨q, hq⟩ := hpre
  have hp_mem := Finset.mem_filter.mp hp
  have hq_mem := Finset.mem_filter.mp hq
  have hp_req : M.requires c p := (Finset.mem_filter.mp hp_mem.1).2
  have hq_req : M.requires c q := (Finset.mem_filter.mp hq_mem.1).2
  refine ⟨p, hp_req, ?_⟩
  rw [mem_activeSuffix_iff]
  exact ⟨hp_mem.2, q, by rw [mem_prefixSet_iff]; exact hq_mem.2,
    ⟨fun heq => by subst heq; omega, c, hq_req, hp_req⟩⟩

/-- Under `IsReduced`, active customers inject into decomposition bag vertices.
This is the core step requiring Hall's marriage theorem. -/
theorem openStacksAt_le_bag_card (hred : M.IsReduced)
    (D : PathDecomposition M.agreementGraph)
    (σ : LinearLayout Pt) (hmono : IsMonotoneLayout M.agreementGraph D σ)
    (i : Fin (Fintype.card Pt)) :
    M.openStacksAt σ i.val ≤ (D.bag (D.lastBag (σ.symm i))).card := by
  sorry

/-- For a monotone layout from decomposition D, maxOpenStacks ≤ D.width + 1. -/
theorem maxOpenStacks_le_width_add_one (hred : M.IsReduced)
    (D : PathDecomposition M.agreementGraph)
    (σ : LinearLayout Pt) (hmono : IsMonotoneLayout M.agreementGraph D σ) :
    M.maxOpenStacks σ ≤ D.width + 1 := by
  unfold maxOpenStacks
  by_cases hn : Fintype.card Pt = 0
  · simp [hn]
  · simp only [dite_eq_right hn]
    apply Finset.sup'_le
    intro i _
    calc M.openStacksAt σ i.val
        ≤ (D.bag (D.lastBag (σ.symm ⟨i.val, by omega⟩))).card :=
          openStacksAt_le_bag_card M hred D σ hmono ⟨i.val, by omega⟩
      _ ≤ D.width + 1 := D.bag_card_le_width_add_one _

/-- For any decomposition D, mospValue ≤ D.width + 1. -/
theorem mospValue_le_width_add_one (hred : M.IsReduced)
    (D : PathDecomposition M.agreementGraph) :
    M.mospValue ≤ D.width + 1 := by
  obtain ⟨σ, hmono⟩ := exists_monotone_layout M.agreementGraph D
  calc M.mospValue ≤ M.maxOpenStacks σ := by
        apply Nat.sInf_le; exact ⟨σ, rfl⟩
    _ ≤ D.width + 1 := maxOpenStacks_le_width_add_one M hred D σ hmono

/-- **Main Theorem**: For a reduced MOSP instance, the MOSP value is at most
    pathwidth of the agreement graph plus 1. -/
theorem mosp_le_pathwidth_add_one (hred : M.IsReduced) :
    M.mospValue ≤ pathwidth M.agreementGraph + 1 := by
  -- pathwidth is achieved by some decomposition D₀ (ℕ is well-ordered)
  have hne : (Set.range (fun D : PathDecomposition M.agreementGraph => D.width)).Nonempty :=
    ⟨_, ⟨PathDecomposition.trivial _, rfl⟩⟩
  obtain ⟨D₀, hD₀⟩ := Nat.sInf_mem hne
  have h1 := mospValue_le_width_add_one M hred D₀
  -- hD₀ : D₀.width = sInf {D.width | D} = pathwidth
  rw [show pathwidth M.agreementGraph =
    sInf (Set.range (fun D : PathDecomposition M.agreementGraph => D.width)) from rfl,
    ← hD₀]
  exact h1

/-- **Tightness** (stated): For any graph G, there exists a reduced instance whose
    agreement graph is isomorphic to G and whose MOSP value equals PW(G) + 1. -/
theorem exists_instance_achieving_equality
    {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∃ (C' P' : Type*) (_ : Fintype C') (_ : DecidableEq C') (_ : Fintype P')
      (_ : DecidableEq P') (M' : MOSPInstance C' P') (_ : DecidableRel M'.requires),
      M'.IsReduced ∧ Nonempty (M'.agreementGraph.Iso G) ∧
      M'.mospValue = pathwidth G + 1 := by
  sorry

end MOSPInstance

end MOSPFormalization
