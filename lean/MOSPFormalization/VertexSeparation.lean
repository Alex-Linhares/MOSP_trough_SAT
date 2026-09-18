/-
Copyright (c) 2024 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Vertex Separation

Vertex separation measures how well a linear layout separates a graph.
At each position i, the "active suffix" consists of suffix vertices that
have at least one neighbor in the prefix. The vertex separation of a layout
is the maximum size of the active suffix over all positions.
The vertex separation of a graph is the minimum over all layouts.
-/

import MOSPFormalization.LinearLayout
import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Combinatorics.SimpleGraph.Finite
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Order.Lattice.Nat

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The active suffix at position `i`: suffix vertices that have a neighbor in the prefix. -/
def activeSuffix (σ : LinearLayout V) (i : ℕ) : Finset V :=
  (suffixSet σ i).filter (fun v =>
    ((prefixSet σ i).filter (fun u => G.Adj u v)).Nonempty)

/-- Vertex separation at position `i`: the number of active suffix vertices. -/
def vertexSepAt (σ : LinearLayout V) (i : ℕ) : ℕ :=
  (activeSuffix G σ i).card

/-- The vertex separation of a layout: the maximum of `vertexSepAt` over all positions.
    We take the max over `Fin n` where `n = Fintype.card V`. If `V` is empty, returns 0. -/
noncomputable def vertexSepOfLayout (σ : LinearLayout V) : ℕ :=
  if h : Fintype.card V = 0 then 0
  else
    Finset.sup' (Finset.univ (α := Fin (Fintype.card V)))
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero h⟩⟩)
      (fun i => vertexSepAt G σ i.val)

/-- The vertex separation of a graph: minimum over all layouts. -/
noncomputable def vertexSeparation : ℕ :=
  sInf (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ))

theorem mem_activeSuffix_iff (σ : LinearLayout V) (i : ℕ) (v : V) :
    v ∈ activeSuffix G σ i ↔
      (σ v).val > i ∧ ∃ u ∈ prefixSet σ i, G.Adj u v := by
  simp only [activeSuffix, Finset.mem_filter, Finset.Nonempty, mem_suffixSet_iff,
    mem_prefixSet_iff]

theorem activeSuffix_subset_suffixSet (σ : LinearLayout V) (i : ℕ) :
    activeSuffix G σ i ⊆ suffixSet σ i :=
  Finset.filter_subset _ _

theorem vertexSepAt_le_card_suffixSet (σ : LinearLayout V) (i : ℕ) :
    vertexSepAt G σ i ≤ (suffixSet σ i).card :=
  Finset.card_le_card (activeSuffix_subset_suffixSet G σ i)

/-- Any layout provides an upper bound for vertex separation. -/
theorem vertexSeparation_le_vertexSepOfLayout (σ : LinearLayout V) :
    vertexSeparation G ≤ vertexSepOfLayout G σ := by
  apply Nat.sInf_le
  exact ⟨σ, rfl⟩

end MOSPFormalization
