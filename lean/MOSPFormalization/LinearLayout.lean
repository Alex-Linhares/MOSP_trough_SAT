/-
Copyright (c) 2024 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Linear Layouts

A linear layout of a finite type `V` is a bijection `V ≃ Fin n` where `n = |V|`.
This gives each vertex a unique position in a linear ordering.

We define prefix sets (vertices at or before position i) and suffix sets
(vertices after position i), and prove basic properties.
-/

import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Basic
import Mathlib.Logic.Equiv.Defs

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- A linear layout of `V` is a bijection from `V` to `Fin (Fintype.card V)`,
    giving each vertex a unique position. -/
abbrev LinearLayout (V : Type*) [Fintype V] := V ≃ Fin (Fintype.card V)

variable {n : ℕ}

/-- The prefix set at position `i`: all vertices placed at or before position `i`. -/
def prefixSet (σ : V ≃ Fin n) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => (σ v).val ≤ i)

/-- The suffix set at position `i`: all vertices placed after position `i`. -/
def suffixSet (σ : V ≃ Fin n) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => (σ v).val > i)

/-- The vertex at position `i` in layout `σ`. -/
def vertexAt (σ : V ≃ Fin n) (i : Fin n) : V :=
  σ.symm i

theorem mem_prefixSet_iff (σ : V ≃ Fin n) (v : V) (i : ℕ) :
    v ∈ prefixSet σ i ↔ (σ v).val ≤ i := by
  simp [prefixSet]

theorem mem_suffixSet_iff (σ : V ≃ Fin n) (v : V) (i : ℕ) :
    v ∈ suffixSet σ i ↔ (σ v).val > i := by
  simp [suffixSet]

theorem prefixSet_union_suffixSet (σ : V ≃ Fin n) (i : ℕ) :
    prefixSet σ i ∪ suffixSet σ i = Finset.univ := by
  ext v
  simp [prefixSet, suffixSet]
  omega

theorem disjoint_prefix_suffix (σ : V ≃ Fin n) (i : ℕ) :
    Disjoint (prefixSet σ i) (suffixSet σ i) := by
  rw [Finset.disjoint_left]
  intro v hv hsv
  rw [mem_prefixSet_iff] at hv
  rw [mem_suffixSet_iff] at hsv
  omega

theorem prefixSet_mono (σ : V ≃ Fin n) {i j : ℕ} (hij : i ≤ j) :
    prefixSet σ i ⊆ prefixSet σ j := by
  intro v hv
  rw [mem_prefixSet_iff] at hv ⊢
  omega

theorem suffixSet_anti (σ : V ≃ Fin n) {i j : ℕ} (hij : i ≤ j) :
    suffixSet σ j ⊆ suffixSet σ i := by
  intro v hv
  rw [mem_suffixSet_iff] at hv ⊢
  omega

theorem vertexAt_mem_prefixSet (σ : V ≃ Fin n) (i : Fin n) :
    vertexAt σ i ∈ prefixSet σ i.val := by
  rw [mem_prefixSet_iff]
  simp [vertexAt]

theorem vertexAt_not_mem_suffixSet (σ : V ≃ Fin n) (i : Fin n) :
    vertexAt σ i ∉ suffixSet σ i.val := by
  rw [mem_suffixSet_iff]
  simp [vertexAt]

theorem card_prefixSet_add_card_suffixSet (σ : V ≃ Fin n) (i : ℕ)
    (hn : Fintype.card V = n) :
    (prefixSet σ i).card + (suffixSet σ i).card = n := by
  rw [← Finset.card_union_of_disjoint (disjoint_prefix_suffix σ i)]
  rw [prefixSet_union_suffixSet]
  rw [Finset.card_univ, hn]

end MOSPFormalization
