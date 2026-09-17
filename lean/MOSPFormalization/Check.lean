/-
Copyright (c) 2024 MOSP Formalization Project. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

# Agreement with the implementation

Small instances where the open-stack count can be computed by `decide` and
compared against what `mosp/verify.py` reports for the same input. The
definitions in `OpenStacks.lean` and the simulation in the solver are separate
implementations of the same quantity, and nothing but tests like these keeps
them from drifting.

One did drift: `isActive` used to require a pattern strictly after position `i`,
so a stack closed one step before its last pattern was produced. The first
example below returned 0 where the implementation gives 1.
-/

import MOSPFormalization.OpenStacks

namespace MOSPFormalization

/-- One customer, one pattern. -/
def oneByOne : MOSPInstance (Fin 1) (Fin 1) where
  requires := fun _ _ => True

instance : DecidableRel oneByOne.requires := fun _ _ => isTrue trivial

noncomputable def idLayout1 : LinearLayout (Fin 1) := Equiv.refl _

/-- The stack is open at the step its only pattern is cut. Python: 1. -/
example : oneByOne.openStacksAt idLayout1 0 = 1 := by decide

/-- Two customers, two patterns, each customer needing exactly one of them. -/
def diagonal : MOSPInstance (Fin 2) (Fin 2) where
  requires := fun c p => c.val = p.val

instance : DecidableRel diagonal.requires := fun c p => Nat.decEq c.val p.val

noncomputable def idLayout2 : LinearLayout (Fin 2) := Equiv.refl _

/-- Each customer opens and closes at its own step, so one stack at a time.
    Python on [[1,0],[0,1]]: 1. -/
example : diagonal.openStacksAt idLayout2 0 = 1 := by decide
example : diagonal.openStacksAt idLayout2 1 = 1 := by decide

/-- Both customers need both patterns, so both stay open throughout.
    Python on [[1,1],[1,1]]: 2. -/
def full : MOSPInstance (Fin 2) (Fin 2) where
  requires := fun _ _ => True

instance : DecidableRel full.requires := fun _ _ => isTrue trivial

example : full.openStacksAt idLayout2 0 = 2 := by decide
example : full.openStacksAt idLayout2 1 = 2 := by decide

end MOSPFormalization
