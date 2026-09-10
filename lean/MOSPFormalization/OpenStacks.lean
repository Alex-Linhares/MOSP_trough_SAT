/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

# Open Stacks

Defines the open stack count for a MOSP instance given a production ordering.
A customer's stack is "open" at position i if the customer has at least one
pattern produced at or before i and at least one pattern not yet produced.
-/

import MOSPFormalization.MOSPInstance
import MOSPFormalization.LinearLayout
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Order.Lattice.Nat

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {C P : Type*} [Fintype C] [DecidableEq C] [Fintype P] [DecidableEq P]

namespace MOSPInstance

variable (M : MOSPInstance C P) [DecidableRel M.requires]

/-- Customer `c` is active at position `i` under ordering `σ` if `c` has at least
    one required pattern in the prefix (at or before i) and at least one in the
    suffix (after i). -/
def isActive (σ : LinearLayout P) (c : C) (i : ℕ) : Prop :=
  ((M.patterns c).filter (fun p => (σ p).val ≤ i)).Nonempty ∧
  ((M.patterns c).filter (fun p => (σ p).val > i)).Nonempty

instance decIsActive (σ : LinearLayout P) (c : C) (i : ℕ) :
    Decidable (M.isActive σ c i) := by
  unfold isActive
  exact instDecidableAnd

/-- The number of open stacks at position `i`. -/
def openStacksAt (σ : LinearLayout P) (i : ℕ) : ℕ :=
  (Finset.univ.filter (fun c => M.isActive σ c i)).card

/-- The maximum number of open stacks over all positions. -/
noncomputable def maxOpenStacks (σ : LinearLayout P) : ℕ :=
  if h : Fintype.card P = 0 then 0
  else
    Finset.sup' (Finset.univ (α := Fin (Fintype.card P)))
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero h⟩⟩)
      (fun i => M.openStacksAt σ i.val)

/-- The MOSP value: minimum over all orderings of the maximum open stacks. -/
noncomputable def mospValue : ℕ :=
  sInf (Set.range (fun σ : LinearLayout P => M.maxOpenStacks σ))

/-- Any ordering provides an upper bound for the MOSP value. -/
theorem mospValue_le_maxOpenStacks (σ : LinearLayout P) :
    M.mospValue ≤ M.maxOpenStacks σ := by
  apply Nat.sInf_le
  exact ⟨σ, rfl⟩

end MOSPInstance

end MOSPFormalization
