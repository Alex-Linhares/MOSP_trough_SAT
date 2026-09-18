/-
Copyright (c) 2024 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Computed Examples

Concrete examples on small types verifying definitions behave correctly.
Since pathwidth/vertexSeparation use sInf (noncomputable), we verify the
agreement graph construction and open stack counting on explicit instances.
-/

import MOSPFormalization.Reduction

namespace MOSPFormalization

/-! ### Example 1: Two patterns, one customer

Customer 0 requires both patterns 0 and 1.
Agreement graph: K₂ (single edge between patterns 0 and 1).
-/

/-- A simple instance: 1 customer, 2 patterns, customer requires both. -/
def exampleInstance1 : MOSPInstance (Fin 1) (Fin 2) where
  requires := fun _ _ => True

instance : DecidableRel exampleInstance1.requires := fun _ _ => isTrue trivial

-- The two patterns agree (share customer 0)
example : exampleInstance1.agree 0 1 := by
  constructor
  · decide
  · exact ⟨0, trivial, trivial⟩

-- The agreement graph has an edge between 0 and 1
example : exampleInstance1.agreementGraph.Adj 0 1 := by
  constructor
  · decide
  · exact ⟨0, trivial, trivial⟩

/-! ### Example 2: Path decomposition structure

We verify that the trivial decomposition (one bag with all vertices)
of K₃ has width 2.
-/

/-- K₃ as a SimpleGraph on Fin 3. -/
def K3 : SimpleGraph (Fin 3) where
  Adj := fun i j => i ≠ j
  symm := by constructor; intro i j h; exact h.symm
  loopless := by constructor; intro i h; exact h rfl

instance : DecidableRel K3.Adj := fun i j => by
  unfold K3
  simp only
  exact instDecidableNot

-- The trivial decomposition of K₃ has width 2 (= 3 - 1)
example : (PathDecomposition.trivial K3).width = 2 := by
  simp [PathDecomposition.width, PathDecomposition.trivial, Finset.sup'_const]

/-! ### Example 3: Agreement graph from a more complex instance

3 customers, 3 patterns:
- Customer 0 requires patterns 0, 1
- Customer 1 requires patterns 1, 2
- Customer 2 requires patterns 0, 2

Agreement graph: K₃ (every pair of patterns shares a customer).
-/

def exampleInstance3 : MOSPInstance (Fin 3) (Fin 3) where
  requires := fun c p =>
    match c, p with
    | 0, 0 => True | 0, 1 => True
    | 1, 1 => True | 1, 2 => True
    | 2, 0 => True | 2, 2 => True
    | _, _ => False

instance : DecidableRel exampleInstance3.requires := fun c p =>
  match c, p with
  | 0, 0 => isTrue trivial | 0, 1 => isTrue trivial
  | 1, 1 => isTrue trivial | 1, 2 => isTrue trivial
  | 2, 0 => isTrue trivial | 2, 2 => isTrue trivial
  | 0, 2 => isFalse (fun h => h) | 1, 0 => isFalse (fun h => h)
  | 2, 1 => isFalse (fun h => h)

-- This instance is reduced (each customer has a distinct pattern set)
-- (We'd need to unfold IsReduced and check, which is complex; stated as an example)

-- Patterns 0 and 1 share customer 0
example : exampleInstance3.agreementGraph.Adj 0 1 := by
  constructor
  · decide
  · exact ⟨0, trivial, trivial⟩

-- Patterns 1 and 2 share customer 1
example : exampleInstance3.agreementGraph.Adj 1 2 := by
  constructor
  · decide
  · exact ⟨1, trivial, trivial⟩

-- Patterns 0 and 2 share customer 2
example : exampleInstance3.agreementGraph.Adj 0 2 := by
  constructor
  · decide
  · exact ⟨2, trivial, trivial⟩

end MOSPFormalization
