/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Pathwidth

The pathwidth of a graph is the minimum width over all path decompositions.
-/

import MOSPFormalization.PathDecomposition
import Mathlib.Order.Lattice.Nat

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V)

/-- The pathwidth of a graph: minimum width over all path decompositions. -/
noncomputable def pathwidth : ℕ :=
  sInf (Set.range (fun P : PathDecomposition G => P.width))

/-- Pathwidth is at most the width of any specific decomposition. -/
theorem pathwidth_le_width (P : PathDecomposition G) :
    pathwidth G ≤ P.width := by
  apply Nat.sInf_le
  exact ⟨P, rfl⟩

/-- Pathwidth is at most `Fintype.card V - 1` (trivial decomposition). -/
theorem pathwidth_le_card_sub_one :
    pathwidth G ≤ Fintype.card V - 1 := by
  calc pathwidth G ≤ (PathDecomposition.trivial G).width := pathwidth_le_width G _
    _ = Fintype.card V - 1 := PathDecomposition.trivial_width G

end MOSPFormalization
