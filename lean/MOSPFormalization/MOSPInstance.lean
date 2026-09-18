/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# MOSP Instances and Agreement Graphs

A MOSP instance consists of a set of customers C, a set of patterns P,
and a binary relation `requires` indicating which customers need which patterns.

The agreement graph has patterns as vertices, with an edge between two patterns
iff they share at least one common customer.
-/

import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Basic

set_option linter.unusedSectionVars false

namespace MOSPFormalization

/-- A MOSP instance with customer type `C` and pattern type `P`.
    `requires c p` means customer `c` needs pattern `p`. -/
structure MOSPInstance (C P : Type*) where
  requires : C → P → Prop

variable {C P : Type*} [Fintype C] [DecidableEq C] [Fintype P] [DecidableEq P]

namespace MOSPInstance

variable (M : MOSPInstance C P) [DecidableRel M.requires]

/-- The set of customers that require pattern `p`. -/
def customers (p : P) : Finset C :=
  Finset.univ.filter (fun c => M.requires c p)

/-- The set of patterns needed by customer `c`. -/
def patterns (c : C) : Finset P :=
  Finset.univ.filter (fun p => M.requires c p)

/-- Two patterns agree if they share at least one common customer. -/
def agree (p q : P) : Prop :=
  p ≠ q ∧ ∃ c, M.requires c p ∧ M.requires c q

instance decAgree : DecidableRel (M.agree) := by
  intro p q
  unfold agree
  exact instDecidableAnd

/-- The agreement graph: vertices are patterns, edges connect patterns
    that share a common customer. -/
def agreementGraph : SimpleGraph P where
  Adj := M.agree
  symm := by
    constructor
    intro x y ⟨hne, c, hp, hq⟩
    exact ⟨hne.symm, c, hq, hp⟩
  loopless := by
    constructor
    intro x ⟨hne, _⟩
    exact hne rfl

instance : DecidableRel (M.agreementGraph).Adj := M.decAgree

/-- An instance is reduced if no two distinct customers have identical pattern sets. -/
def IsReduced : Prop :=
  ∀ c₁ c₂ : C, M.patterns c₁ = M.patterns c₂ → c₁ = c₂

theorem agree_comm (p q : P) : M.agree p q ↔ M.agree q p := by
  constructor
  · rintro ⟨hne, c, hp, hq⟩; exact ⟨hne.symm, c, hq, hp⟩
  · rintro ⟨hne, c, hq, hp⟩; exact ⟨hne.symm, c, hp, hq⟩

theorem customers_nonempty_of_adj {p q : P} (h : M.agreementGraph.Adj p q) :
    (M.customers p ∩ M.customers q).Nonempty := by
  obtain ⟨_, c, hp, hq⟩ := h
  exact ⟨c, Finset.mem_inter.mpr ⟨Finset.mem_filter.mpr ⟨Finset.mem_univ _, hp⟩,
    Finset.mem_filter.mpr ⟨Finset.mem_univ _, hq⟩⟩⟩

end MOSPInstance

end MOSPFormalization
