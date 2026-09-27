/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The MOSP graph on concrete instances

Two instances small enough for `decide` on the graph side, each with the
equality `mospValue = pathwidth (mospGraph) + 1` evaluated through
`MOSPGraph.lean`:

* `star` — the counterexample to the pattern-graph statement that
  `Reduction.lean` used to carry. One hub pattern and four customers each
  requiring the hub plus a private pattern. It is reduced, its MOSP graph is
  `K₄` (pathwidth `3`, so `mospValue = 4`), and its agreement graph on patterns
  is the star `K_{1,4}` (pathwidth `1`), so the withdrawn bound
  `mospValue ≤ pathwidth (agreementGraph) + 1` reads `4 ≤ 2`.
* `exampleInstance3` of `Examples.lean` — three customers pairwise sharing a
  pattern, MOSP graph `K₃`, `mospValue = 3`.

`mospValue` and `pathwidth` are infima and cannot be evaluated by `decide`; each
value below is pinned from both sides — the clique bound
`card_le_pathwidth_add_one_of_isClique` from below and an explicit decomposition
(or the trivial one) from above — and `decide` settles the finite facts about
adjacency, cliques, coverage and interval properties.
-/

import MOSPFormalization.MOSPGraph
import MOSPFormalization.Examples

namespace MOSPFormalization

/-! ### The star -/

/-- Customers `Fin 4`, patterns `Fin 5`: pattern `0` is the hub and pattern `j + 1`
is customer `j`'s private pattern, so customer `j` requires `{0, j + 1}`. -/
def star : MOSPInstance (Fin 4) (Fin 5) where
  requires := fun c p => p.val = 0 ∨ p.val = c.val + 1

instance : DecidableRel star.requires := fun c p =>
  inferInstanceAs (Decidable (p.val = 0 ∨ p.val = c.val + 1))

/-- The star satisfies the hypothesis of the withdrawn statement. -/
theorem star_isReduced : star.IsReduced := by
  unfold MOSPInstance.IsReduced
  decide

/-- The star satisfies the hypothesis of the true statement. -/
theorem star_nontrivial : ∃ c p, star.requires c p := ⟨0, 0, Or.inl rfl⟩

/-- Under the identity order the hub is produced first and all four stacks open;
customer `j`'s stack closes at step `j + 1`, inclusive. -/
noncomputable def starLayout : LinearLayout (Fin 5) := Equiv.refl _

example : star.openStacksAt starLayout 0 = 4 := by decide
example : star.openStacksAt starLayout 1 = 4 := by decide
example : star.openStacksAt starLayout 2 = 3 := by decide
example : star.openStacksAt starLayout 4 = 1 := by decide

/-- The MOSP graph of the star is complete: every two customers share the hub. -/
theorem star_mospGraph_adj : ∀ c d : Fin 4, star.mospGraph.Adj c d ↔ c ≠ d := by decide

theorem star_univ_isClique : star.mospGraph.IsClique (Finset.univ : Finset (Fin 4)) := by
  rw [SimpleGraph.isClique_iff]
  intro c _ d _ hne
  exact ⟨hne, 0, Or.inl rfl, Or.inl rfl⟩

theorem star_pathwidth_mospGraph : pathwidth star.mospGraph = 3 := by
  apply le_antisymm
  · simpa using pathwidth_le_card_sub_one star.mospGraph
  · have h := card_le_pathwidth_add_one_of_isClique star.mospGraph Finset.univ star_univ_isClique
    simp at h
    omega

/-- `mospValue star = 4`, through the main theorem. -/
theorem star_mospValue : star.mospValue = 4 := by
  rw [star.mospValue_eq_pathwidth_add_one star_nontrivial, star_pathwidth_mospGraph]

/-- Bag `j` of the star's pattern graph: the hub and customer `j`'s private pattern. -/
def starBag (i : Fin 4) : Finset (Fin 5) := {0, ⟨i.val + 1, Nat.succ_lt_succ i.isLt⟩}

/-- The four bags `{hub, j + 1}` of the star's pattern graph: a decomposition of width `1`. -/
def starPatternDecomposition : PathDecomposition star.agreementGraph where
  length := 3
  bag := starBag
  vertex_coverage := by decide
  edge_coverage := by decide
  interval := by decide

theorem starPatternDecomposition_width_le : starPatternDecomposition.width ≤ 1 := by
  unfold PathDecomposition.width
  have h : Finset.sup' Finset.univ
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
      (fun i : Fin (starPatternDecomposition.length + 1) =>
        (starPatternDecomposition.bag i).card) ≤ 2 := by
    apply Finset.sup'_le
    intro i _
    exact Finset.card_le_two
  omega

/-- Patterns `0` and `1` share customer `0`. -/
theorem star_pattern_clique : star.agreementGraph.IsClique (({0, 1} : Finset (Fin 5)) : Set (Fin 5)) := by
  rw [SimpleGraph.isClique_iff]
  intro u hu v hv hne
  refine ⟨hne, 0, ?_, ?_⟩
  · simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff] at hu
    rcases hu with rfl | rfl
    · exact Or.inl rfl
    · exact Or.inr rfl
  · simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff] at hv
    rcases hv with rfl | rfl
    · exact Or.inl rfl
    · exact Or.inr rfl

theorem star_pathwidth_agreementGraph : pathwidth star.agreementGraph = 1 := by
  apply le_antisymm
  · exact (pathwidth_le_width _ starPatternDecomposition).trans starPatternDecomposition_width_le
  · have h := card_le_pathwidth_add_one_of_isClique star.agreementGraph {0, 1} star_pattern_clique
    have h2 : ({0, 1} : Finset (Fin 5)).card = 2 := by decide
    omega

/-- **The withdrawn statement is false**: on the reduced star instance,
`pathwidth (agreementGraph) + 1 = 2 < 4 = mospValue`. -/
theorem star_refutes_pattern_graph_bound :
    star.IsReduced ∧ pathwidth star.agreementGraph + 1 < star.mospValue := by
  refine ⟨star_isReduced, ?_⟩
  rw [star_pathwidth_agreementGraph, star_mospValue]
  decide

/-! ### `exampleInstance3`: three customers, MOSP graph `K₃` -/

theorem exampleInstance3_mospGraph_adj :
    ∀ c d : Fin 3, exampleInstance3.mospGraph.Adj c d ↔ c ≠ d := by decide

theorem exampleInstance3_univ_isClique :
    exampleInstance3.mospGraph.IsClique (Finset.univ : Finset (Fin 3)) := by
  rw [SimpleGraph.isClique_iff]
  intro c _ d _ hne
  exact (exampleInstance3_mospGraph_adj c d).mpr hne

theorem exampleInstance3_pathwidth : pathwidth exampleInstance3.mospGraph = 2 := by
  apply le_antisymm
  · simpa using pathwidth_le_card_sub_one exampleInstance3.mospGraph
  · have h := card_le_pathwidth_add_one_of_isClique exampleInstance3.mospGraph Finset.univ
      exampleInstance3_univ_isClique
    simp at h
    omega

theorem exampleInstance3_mospValue : exampleInstance3.mospValue = 3 := by
  rw [exampleInstance3.mospValue_eq_pathwidth_add_one ⟨0, 0, trivial⟩, exampleInstance3_pathwidth]

end MOSPFormalization
