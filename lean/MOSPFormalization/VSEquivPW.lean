/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Kinnersley's Theorem: Vertex Separation = Pathwidth

Combines the two directions:
- PW ≤ VS (from LayoutToDecomposition: any layout gives a decomposition of that width)
- VS ≤ PW (from DecompositionToLayout: any decomposition gives a layout of that width)

to establish VS(G) = PW(G) for all finite simple graphs G.

Reference: Kinnersley (1992), "The vertex separation number of a graph
equals its path-width".
-/

import MOSPFormalization.LayoutToDecomposition
import MOSPFormalization.DecompositionToLayout

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- PW ≤ VS: pathwidth is at most vertex separation.
    Follows from: for any layout σ, PW ≤ width(decomp from σ) ≤ vsOfLayout(σ),
    then take inf over σ. -/
theorem pathwidth_le_vertexSeparation :
    pathwidth G ≤ vertexSeparation G := by
  -- vertexSeparation = sInf { vertexSepOfLayout σ | σ }
  -- For each σ, pathwidth ≤ vertexSepOfLayout σ
  -- Therefore pathwidth ≤ sInf { vertexSepOfLayout σ } = vertexSeparation
  unfold vertexSeparation
  apply le_csInf
  · exact ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  · intro b ⟨σ, hσ⟩
    rw [← hσ]
    exact pathwidth_le_vertexSepOfLayout G σ

/-- VS ≤ PW: vertex separation is at most pathwidth. -/
theorem vertexSeparation_le_pathwidth' :
    vertexSeparation G ≤ pathwidth G :=
  vertexSeparation_le_pathwidth G

/-- **Kinnersley's Theorem**: The vertex separation number of a finite simple graph
    equals its pathwidth. -/
theorem vertexSeparation_eq_pathwidth :
    vertexSeparation G = pathwidth G :=
  le_antisymm (vertexSeparation_le_pathwidth G) (pathwidth_le_vertexSeparation G)

end MOSPFormalization
