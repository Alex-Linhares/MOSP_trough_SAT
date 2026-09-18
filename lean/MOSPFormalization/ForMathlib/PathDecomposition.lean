/-
Copyright (c) 2024 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.
Authors: Alexandre Linhares
-/
import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Data.Finset.Max
import Mathlib.Data.Fintype.Card
import Mathlib.Order.Lattice.Nat

/-!
# Path decompositions and pathwidth

This file defines path decompositions of simple graphs and the pathwidth invariant.

A *path decomposition* of a graph `G` is a sequence of sets of vertices (called *bags*)
such that:
1. every vertex appears in some bag,
2. for every edge, both endpoints appear together in some bag, and
3. the bags containing any given vertex form a contiguous interval.

The *width* of a path decomposition is the maximum bag size minus one.
The *pathwidth* of a graph is the minimum width over all path decompositions.

## Main definitions

* `SimpleGraph.PathDecomposition`: A path decomposition of a simple graph.
* `SimpleGraph.PathDecomposition.width`: The width of a path decomposition.
* `SimpleGraph.pathwidth`: The pathwidth of a graph.

## Main results

* `SimpleGraph.PathDecomposition.mem_bag_iff_between`: A vertex appears in bag `i`
  iff `firstBag v ≤ i ≤ lastBag v`.
* `SimpleGraph.pathwidth_le_card_sub_one`: The pathwidth is at most `|V| - 1`.

## References

* [R. Kinnersley, *The vertex separation number of a graph equals its path-width*][kinnersley1992]
-/

namespace SimpleGraph

variable {V : Type*}

/-- A path decomposition of a simple graph `G` on vertex type `V`. -/
structure PathDecomposition (G : SimpleGraph V) where
  /-- The number of bags minus one. -/
  length : ℕ
  /-- The bag function. -/
  bag : Fin (length + 1) → Finset V
  /-- Every vertex appears in at least one bag. -/
  vertex_coverage : ∀ v : V, ∃ i, v ∈ bag i
  /-- Both endpoints of every edge appear together in some bag. -/
  edge_coverage : ∀ u v : V, G.Adj u v → ∃ i, u ∈ bag i ∧ v ∈ bag i
  /-- The bags containing any given vertex form a contiguous interval. -/
  interval : ∀ (v : V) (i j k : Fin (length + 1)),
    i ≤ j → j ≤ k → v ∈ bag i → v ∈ bag k → v ∈ bag j

namespace PathDecomposition

variable {G : SimpleGraph V}

/-- The width of a path decomposition: `(max bag size) - 1`. -/
noncomputable def width (P : PathDecomposition G) : ℕ :=
  Finset.sup' Finset.univ
    (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
    (fun i => (P.bag i).card) - 1

theorem bag_card_le_width_add_one (P : PathDecomposition G)
    (i : Fin (P.length + 1)) : (P.bag i).card ≤ P.width + 1 := by
  unfold width
  have h := Finset.le_sup' (fun i => (P.bag i).card) (Finset.mem_univ i)
  omega

variable [Fintype V] [DecidableEq V]

/-- The trivial path decomposition with a single bag containing all vertices. -/
def trivial (G : SimpleGraph V) : PathDecomposition G where
  length := 0
  bag := fun _ => Finset.univ
  vertex_coverage v := ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.mem_univ v⟩
  edge_coverage u v _ := ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.mem_univ u, Finset.mem_univ v⟩
  interval _ _ _ _ _ _ _ _ := Finset.mem_univ _

omit [DecidableEq V] in
@[simp]
theorem trivial_width (G : SimpleGraph V) :
    (trivial G).width = Fintype.card V - 1 := by
  simp [width, trivial, Finset.sup'_const]

/-- The set of bag indices containing a given vertex. -/
def bagsOf (P : PathDecomposition G) (v : V) : Finset (Fin (P.length + 1)) :=
  Finset.univ.filter (fun i => v ∈ P.bag i)

omit [Fintype V] in
theorem bagsOf_nonempty (P : PathDecomposition G) (v : V) : (P.bagsOf v).Nonempty := by
  obtain ⟨i, hi⟩ := P.vertex_coverage v
  exact ⟨i, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hi⟩⟩

/-- The first bag index containing vertex `v`. -/
noncomputable def firstBag (P : PathDecomposition G) (v : V) : Fin (P.length + 1) :=
  (P.bagsOf v).min' (P.bagsOf_nonempty v)

/-- The last bag index containing vertex `v`. -/
noncomputable def lastBag (P : PathDecomposition G) (v : V) : Fin (P.length + 1) :=
  (P.bagsOf v).max' (P.bagsOf_nonempty v)

omit [Fintype V] in
theorem mem_bag_firstBag (P : PathDecomposition G) (v : V) :
    v ∈ P.bag (P.firstBag v) :=
  (Finset.mem_filter.mp (Finset.min'_mem _ (P.bagsOf_nonempty v))).2

omit [Fintype V] in
theorem mem_bag_lastBag (P : PathDecomposition G) (v : V) :
    v ∈ P.bag (P.lastBag v) :=
  (Finset.mem_filter.mp (Finset.max'_mem _ (P.bagsOf_nonempty v))).2

omit [Fintype V] in
theorem firstBag_le_lastBag (P : PathDecomposition G) (v : V) :
    P.firstBag v ≤ P.lastBag v := by
  apply Finset.min'_le
  exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, P.mem_bag_lastBag v⟩

omit [Fintype V] in
/-- A vertex appears in bag `i` iff `firstBag v ≤ i ≤ lastBag v`. -/
theorem mem_bag_iff_between (P : PathDecomposition G) (v : V)
    (i : Fin (P.length + 1)) :
    v ∈ P.bag i ↔ P.firstBag v ≤ i ∧ i ≤ P.lastBag v := by
  constructor
  · intro hvi
    constructor
    · apply Finset.min'_le
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hvi⟩
    · apply Finset.le_max'
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hvi⟩
  · exact fun ⟨hfi, hil⟩ =>
      P.interval v _ i _ hfi hil (P.mem_bag_firstBag v) (P.mem_bag_lastBag v)

end PathDecomposition

section Pathwidth

variable [Fintype V] [DecidableEq V]

/-- The pathwidth of a graph: minimum width over all path decompositions. -/
noncomputable def pathwidth (G : SimpleGraph V) : ℕ :=
  sInf (Set.range (fun P : PathDecomposition G => P.width))

omit [Fintype V] [DecidableEq V] in
theorem pathwidth_le_width (G : SimpleGraph V) (P : PathDecomposition G) :
    G.pathwidth ≤ P.width :=
  Nat.sInf_le ⟨P, rfl⟩

omit [DecidableEq V] in
theorem pathwidth_le_card_sub_one (G : SimpleGraph V) :
    G.pathwidth ≤ Fintype.card V - 1 :=
  calc G.pathwidth ≤ (PathDecomposition.trivial G).width := pathwidth_le_width G _
    _ = Fintype.card V - 1 := PathDecomposition.trivial_width G

end Pathwidth

end SimpleGraph
