/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under the MIT license as described in the file LICENSE.
Authors: MOSP Formalization Project
-/
import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Combinatorics.SimpleGraph.Finite
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Order.Lattice.Nat
import Mathlib.Logic.Equiv.Defs

/-!
# Vertex separation

This file defines vertex separation for simple graphs and proves basic properties.

Given a *linear layout* `σ : V ≃ Fin n` of the vertices of a graph `G`, the
*active suffix* at position `i` consists of vertices placed after position `i`
that have at least one neighbor at or before position `i`. The *vertex separation*
of the layout is the maximum size of the active suffix over all positions.
The *vertex separation* of the graph is the minimum over all layouts.

## Main definitions

* `SimpleGraph.LinearLayout`: A bijection `V ≃ Fin (Fintype.card V)` giving each
  vertex a position.
* `SimpleGraph.prefixSet`: Vertices at or before a given position.
* `SimpleGraph.suffixSet`: Vertices after a given position.
* `SimpleGraph.activeSuffix`: Suffix vertices with a neighbor in the prefix.
* `SimpleGraph.vertexSepAt`: Size of the active suffix at a position.
* `SimpleGraph.vertexSepOfLayout`: Maximum vertex separation over all positions.
* `SimpleGraph.vertexSeparation`: Minimum vertex separation over all layouts.

## Main results

* `SimpleGraph.vertexSeparation_le_vertexSepOfLayout`: The vertex separation is
  at most that of any specific layout.

## References

* [R. Kinnersley, *The vertex separation number of a graph equals its path-width*][kinnersley1992]
-/

namespace SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- A linear layout of a finite type `V` is a bijection `V ≃ Fin (Fintype.card V)`,
giving each vertex a unique position in a linear ordering. -/
abbrev LinearLayout (V : Type*) [Fintype V] := V ≃ Fin (Fintype.card V)

section Layout

variable {n : ℕ}

/-- The prefix set at position `i`: all vertices placed at or before position `i`. -/
def prefixSet (σ : V ≃ Fin n) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => (σ v).val ≤ i)

/-- The suffix set at position `i`: all vertices placed after position `i`. -/
def suffixSet (σ : V ≃ Fin n) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => (σ v).val > i)

omit [DecidableEq V] in
@[simp]
theorem mem_prefixSet_iff (σ : V ≃ Fin n) (v : V) (i : ℕ) :
    v ∈ prefixSet σ i ↔ (σ v).val ≤ i := by
  simp [prefixSet]

omit [DecidableEq V] in
@[simp]
theorem mem_suffixSet_iff (σ : V ≃ Fin n) (v : V) (i : ℕ) :
    v ∈ suffixSet σ i ↔ (σ v).val > i := by
  simp [suffixSet]

theorem prefixSet_union_suffixSet (σ : V ≃ Fin n) (i : ℕ) :
    prefixSet σ i ∪ suffixSet σ i = Finset.univ := by
  ext v; simp [prefixSet, suffixSet]; omega

omit [DecidableEq V] in
theorem disjoint_prefixSet_suffixSet (σ : V ≃ Fin n) (i : ℕ) :
    Disjoint (prefixSet σ i) (suffixSet σ i) := by
  rw [Finset.disjoint_left]
  intro v hv hsv; simp at hv hsv; omega

omit [DecidableEq V] in
theorem prefixSet_mono (σ : V ≃ Fin n) {i j : ℕ} (hij : i ≤ j) :
    prefixSet σ i ⊆ prefixSet σ j := by
  intro v hv; simp at hv ⊢; omega

omit [DecidableEq V] in
theorem suffixSet_anti (σ : V ≃ Fin n) {i j : ℕ} (hij : i ≤ j) :
    suffixSet σ j ⊆ suffixSet σ i := by
  intro v hv; simp at hv ⊢; omega

end Layout

section VertexSeparation

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The active suffix at position `i`: suffix vertices that have at least one
neighbor in the prefix. -/
def activeSuffix (σ : LinearLayout V) (i : ℕ) : Finset V :=
  (suffixSet σ i).filter (fun v =>
    ((prefixSet σ i).filter (fun u => G.Adj u v)).Nonempty)

omit [DecidableEq V] in
@[simp]
theorem mem_activeSuffix_iff (σ : LinearLayout V) (i : ℕ) (v : V) :
    v ∈ activeSuffix G σ i ↔
      (σ v).val > i ∧ ∃ u ∈ prefixSet σ i, G.Adj u v := by
  simp only [activeSuffix, Finset.mem_filter, Finset.Nonempty, mem_suffixSet_iff,
    mem_prefixSet_iff]

omit [DecidableEq V] in
theorem activeSuffix_subset_suffixSet (σ : LinearLayout V) (i : ℕ) :
    activeSuffix G σ i ⊆ suffixSet σ i :=
  Finset.filter_subset _ _

/-- Vertex separation at position `i`: the cardinality of the active suffix. -/
def vertexSepAt (σ : LinearLayout V) (i : ℕ) : ℕ :=
  (activeSuffix G σ i).card

omit [DecidableEq V] in
theorem vertexSepAt_le_card_suffixSet (σ : LinearLayout V) (i : ℕ) :
    vertexSepAt G σ i ≤ (suffixSet σ i).card :=
  Finset.card_le_card (activeSuffix_subset_suffixSet G σ i)

/-- The vertex separation of a layout: the maximum of `vertexSepAt` over all positions.
Returns `0` when `V` is empty. -/
noncomputable def vertexSepOfLayout (σ : LinearLayout V) : ℕ :=
  if h : Fintype.card V = 0 then 0
  else
    Finset.sup' (Finset.univ (α := Fin (Fintype.card V)))
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero h⟩⟩)
      (fun i => vertexSepAt G σ i.val)

/-- The vertex separation of a graph: the minimum of `vertexSepOfLayout` over all layouts. -/
noncomputable def vertexSeparation : ℕ :=
  sInf (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ))

omit [DecidableEq V] in
theorem vertexSeparation_le_vertexSepOfLayout (σ : LinearLayout V) :
    vertexSeparation G ≤ vertexSepOfLayout G σ := by
  apply Nat.sInf_le
  exact ⟨σ, rfl⟩

end VertexSeparation

end SimpleGraph
