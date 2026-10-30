/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The independence bound: `pathwidth G ≤ n − α(G)`

The deterministic core of §3 of `reports/random_graph_pathwidth_survey.md`
(the dense case of `G(n, p)`), checked by brute force on every graph on at most
9 vertices on 2026-10-30 (`reports/scratch/empty_pair/check23.py`, zero
violations, tight on 6.5% at 9 vertices). The decomposition is the standard one:
for an independent set `I`, the bags `(V ∖ I) ∪ {v}`, one per `v ∈ I`, in any
order. Every vertex outside `I` is in every bag, every vertex of `I` is in exactly
one, and an edge has at most one end in `I`, so the three axioms hold and every
bag has at most `n − |I| + 1` vertices.

## Main results

* `indepDecomposition G I hI` — the decomposition above, with one extra bag
  `V ∖ I` at the end so that the index type is `Fin (|I| + 1)` even for `I = ∅`.
* `pathwidth_le_card_sub_card_indep` — `pathwidth G ≤ n − |I|` for every
  independent set `I`.
* `pathwidth_le_card_sub_indepNum` — `pathwidth G ≤ n − α(G)`, with Mathlib's
  `SimpleGraph.indepNum`.
-/

import MOSPFormalization.Pathwidth
import Mathlib.Combinatorics.SimpleGraph.Clique

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V)

/-- An enumeration of a finite set of vertices. -/
noncomputable def indepEnum (I : Finset V) : ↥I ≃ Fin I.card :=
  (Fintype.equivFin ↥I).trans (finCongr (Fintype.card_coe I))

/-- The position of `v` in the enumeration of `I` (`0` for vertices outside `I`). -/
noncomputable def indepPos (I : Finset V) (v : V) : ℕ :=
  if hv : v ∈ I then (indepEnum I ⟨v, hv⟩).val else 0

theorem indepPos_of_mem (I : Finset V) {v : V} (hv : v ∈ I) :
    indepPos I v = (indepEnum I ⟨v, hv⟩).val := by
  unfold indepPos; simp [hv]

theorem indepPos_lt (I : Finset V) {v : V} (hv : v ∈ I) : indepPos I v < I.card := by
  rw [indepPos_of_mem I hv]
  exact (indepEnum I ⟨v, hv⟩).isLt

theorem indepPos_injOn (I : Finset V) {u v : V} (hu : u ∈ I) (hv : v ∈ I)
    (h : indepPos I u = indepPos I v) : u = v := by
  rw [indepPos_of_mem I hu, indepPos_of_mem I hv] at h
  have := (indepEnum I).injective (Fin.ext h)
  exact congrArg Subtype.val this

/-- Bag `j`: the vertices outside `I`, plus the vertex of `I` at position `j`, if any. -/
noncomputable def indepBag (I : Finset V) (j : ℕ) : Finset V :=
  (Finset.univ \ I) ∪ I.filter (fun v => indepPos I v = j)

theorem mem_indepBag_iff (I : Finset V) (j : ℕ) (v : V) :
    v ∈ indepBag I j ↔ v ∉ I ∨ (v ∈ I ∧ indepPos I v = j) := by
  simp [indepBag]

theorem card_indepBag_le (I : Finset V) (j : ℕ) :
    (indepBag I j).card ≤ Fintype.card V - I.card + 1 := by
  unfold indepBag
  calc ((Finset.univ \ I) ∪ I.filter (fun v => indepPos I v = j)).card
      ≤ (Finset.univ \ I).card + (I.filter (fun v => indepPos I v = j)).card :=
        Finset.card_union_le _ _
    _ ≤ (Fintype.card V - I.card) + 1 := by
        apply Nat.add_le_add
        · rw [Finset.card_univ_sdiff]
        · apply Finset.card_le_one.mpr
          intro a ha b hb
          rw [Finset.mem_filter] at ha hb
          exact indepPos_injOn I ha.1 hb.1 (ha.2.trans hb.2.symm)

/-- The path decomposition `(V ∖ I) ∪ {v}`, `v ∈ I`, followed by one bag `V ∖ I`. -/
noncomputable def indepDecomposition (I : Finset V) (hI : G.IsIndepSet (I : Set V)) :
    PathDecomposition G where
  length := I.card
  bag := fun j => indepBag I j.val
  vertex_coverage := by
    intro v
    by_cases hv : v ∈ I
    · refine ⟨⟨indepPos I v, by have := indepPos_lt I hv; omega⟩, ?_⟩
      rw [mem_indepBag_iff]; exact Or.inr ⟨hv, rfl⟩
    · exact ⟨⟨0, Nat.zero_lt_succ _⟩, (mem_indepBag_iff I 0 v).mpr (Or.inl hv)⟩
  edge_coverage := by
    intro u v huv
    by_cases hu : u ∈ I <;> by_cases hv : v ∈ I
    · exact absurd huv (hI hu hv (G.ne_of_adj huv))
    · refine ⟨⟨indepPos I u, by have := indepPos_lt I hu; omega⟩, ?_, ?_⟩
      · rw [mem_indepBag_iff]; exact Or.inr ⟨hu, rfl⟩
      · rw [mem_indepBag_iff]; exact Or.inl hv
    · refine ⟨⟨indepPos I v, by have := indepPos_lt I hv; omega⟩, ?_, ?_⟩
      · rw [mem_indepBag_iff]; exact Or.inl hu
      · rw [mem_indepBag_iff]; exact Or.inr ⟨hv, rfl⟩
    · exact ⟨⟨0, Nat.zero_lt_succ _⟩, (mem_indepBag_iff I 0 u).mpr (Or.inl hu),
        (mem_indepBag_iff I 0 v).mpr (Or.inl hv)⟩
  interval := by
    intro v i j k hij hjk hi hk
    rw [mem_indepBag_iff] at hi hk ⊢
    rcases hi with hi | ⟨hv, hi⟩
    · exact Or.inl hi
    · rcases hk with hk | ⟨_, hk⟩
      · exact absurd hv hk
      · refine Or.inr ⟨hv, ?_⟩
        have h1 : i.val ≤ j.val := hij
        have h2 : j.val ≤ k.val := hjk
        omega

theorem indepDecomposition_width_le (I : Finset V) (hI : G.IsIndepSet (I : Set V)) :
    (indepDecomposition G I hI).width ≤ Fintype.card V - I.card := by
  unfold PathDecomposition.width
  apply Nat.sub_le_of_le_add
  apply Finset.sup'_le
  intro j _
  exact card_indepBag_le I j.val

/-- **The independence bound**, set form: `pathwidth G ≤ n − |I|` for every
independent set `I`. -/
theorem pathwidth_le_card_sub_card_indep (I : Finset V) (hI : G.IsIndepSet (I : Set V)) :
    pathwidth G ≤ Fintype.card V - I.card :=
  (pathwidth_le_width G (indepDecomposition G I hI)).trans (indepDecomposition_width_le G I hI)

/-- **The independence bound**: `pathwidth G ≤ n − α(G)`. -/
theorem pathwidth_le_card_sub_indepNum :
    pathwidth G ≤ Fintype.card V - G.indepNum := by
  obtain ⟨I, hI⟩ := G.exists_isNIndepSet_indepNum
  rw [← hI.card_eq]
  exact pathwidth_le_card_sub_card_indep G I hI.isIndepSet

end MOSPFormalization
