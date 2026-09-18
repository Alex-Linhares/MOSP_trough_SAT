/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Path Decompositions

A path decomposition of a graph G is a sequence of "bags" (finite sets of vertices)
satisfying:
1. Every vertex appears in some bag (vertex coverage)
2. For every edge, both endpoints appear in some common bag (edge coverage)
3. The bags containing any given vertex form a contiguous interval (interval property)

The width of a path decomposition is (max bag size) - 1.
-/

import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Data.Finset.Max
import Mathlib.Data.Fintype.Basic

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- A path decomposition of a simple graph `G`. -/
structure PathDecomposition (G : SimpleGraph V) where
  /-- Number of bags minus 1 (so there are `length + 1` bags). -/
  length : ℕ
  /-- The bag function mapping indices to sets of vertices. -/
  bag : Fin (length + 1) → Finset V
  /-- Every vertex appears in at least one bag. -/
  vertex_coverage : ∀ v : V, ∃ i, v ∈ bag i
  /-- Both endpoints of every edge appear together in some bag. -/
  edge_coverage : ∀ u v : V, G.Adj u v → ∃ i, u ∈ bag i ∧ v ∈ bag i
  /-- The bags containing any vertex form a contiguous interval. -/
  interval : ∀ (v : V) (i j k : Fin (length + 1)),
    i ≤ j → j ≤ k → v ∈ bag i → v ∈ bag k → v ∈ bag j

namespace PathDecomposition

variable {G : SimpleGraph V}

/-- The width of a path decomposition: (max bag size) - 1. -/
noncomputable def width (P : PathDecomposition G) : ℕ :=
  Finset.sup' (Finset.univ (α := Fin (P.length + 1)))
    (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
    (fun i => (P.bag i).card) - 1

/-- Every bag has size at most width + 1. -/
theorem bag_card_le_width_add_one (P : PathDecomposition G) (i : Fin (P.length + 1)) :
    (P.bag i).card ≤ P.width + 1 := by
  unfold width
  have h := Finset.le_sup' (fun i => (P.bag i).card) (Finset.mem_univ i)
  omega

/-- The trivial path decomposition with one bag containing all vertices. -/
def trivial (G : SimpleGraph V) : PathDecomposition G where
  length := 0
  bag := fun _ => Finset.univ
  vertex_coverage := fun v => ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.mem_univ v⟩
  edge_coverage := fun u v _ =>
    ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.mem_univ u, Finset.mem_univ v⟩
  interval := fun _ _ _ _ _ _ _ _ => Finset.mem_univ _

theorem trivial_width (G : SimpleGraph V) :
    (trivial G).width = Fintype.card V - 1 := by
  simp [width, trivial, Finset.sup'_const]

/-- The set of bag indices containing vertex `v`. -/
def bagsOf (P : PathDecomposition G) (v : V) : Finset (Fin (P.length + 1)) :=
  Finset.univ.filter (fun i => v ∈ P.bag i)

theorem bagsOf_nonempty (P : PathDecomposition G) (v : V) :
    (P.bagsOf v).Nonempty := by
  obtain ⟨i, hi⟩ := P.vertex_coverage v
  exact ⟨i, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hi⟩⟩

/-- The first bag index in which vertex `v` appears. -/
noncomputable def firstBag (P : PathDecomposition G) (v : V) : Fin (P.length + 1) :=
  (P.bagsOf v).min' (P.bagsOf_nonempty v)

/-- The last bag index in which vertex `v` appears. -/
noncomputable def lastBag (P : PathDecomposition G) (v : V) : Fin (P.length + 1) :=
  (P.bagsOf v).max' (P.bagsOf_nonempty v)

theorem mem_bag_firstBag (P : PathDecomposition G) (v : V) :
    v ∈ P.bag (P.firstBag v) := by
  have := Finset.min'_mem _ (P.bagsOf_nonempty v)
  exact (Finset.mem_filter.mp this).2

theorem mem_bag_lastBag (P : PathDecomposition G) (v : V) :
    v ∈ P.bag (P.lastBag v) := by
  have := Finset.max'_mem _ (P.bagsOf_nonempty v)
  exact (Finset.mem_filter.mp this).2

theorem firstBag_le_lastBag (P : PathDecomposition G) (v : V) :
    P.firstBag v ≤ P.lastBag v := by
  apply Finset.min'_le
  exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, P.mem_bag_lastBag v⟩

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
  · intro ⟨hfi, hil⟩
    exact P.interval v (P.firstBag v) i (P.lastBag v)
      hfi hil (P.mem_bag_firstBag v) (P.mem_bag_lastBag v)

end PathDecomposition

end MOSPFormalization
