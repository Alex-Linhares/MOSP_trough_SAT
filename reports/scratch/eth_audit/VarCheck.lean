import Mathlib
-- Retyped from the comparator (SubexponentialSAT.lean lines 13-51): variable [DecidableEq V] before Literal.eval
namespace Cmp
universe u
abbrev Assignment (V : Type u) := V → Bool
structure Literal (V : Type u) where
  «variable» : V
  positive : Bool
  deriving DecidableEq
abbrev Clause (V : Type u) := Finset (Literal V)
abbrev CNF (V : Type u) := Finset (Clause V)
variable {V : Type u} [DecidableEq V]
def Literal.eval (a : Assignment V) (l : Literal V) : Bool := a l.variable == l.positive
def Clause.eval (a : Assignment V) (C : Clause V) : Bool := decide (∃ l ∈ C, l.eval a = true)
def CNF.eval (a : Assignment V) (F : CNF V) : Bool := decide (∀ C ∈ F, C.eval a = true)
def WidthAtMost (k : ℕ) (F : CNF V) : Prop := ∀ C ∈ F, C.card ≤ k
section Finite
variable [Fintype V]
def satisfyingAssignments (F : CNF V) : Finset (Assignment V) := Finset.univ.filter fun a => F.eval a = true
def count (F : CNF V) : ℕ := (satisfyingAssignments F).card
end Finite
end Cmp
-- Solution variant (SAT.lean): variable [DecidableEq V] declared after Literal.eval
namespace Sol
universe u
abbrev Assignment (V : Type u) := V → Bool
structure Literal (V : Type u) where
  «variable» : V
  positive : Bool
  deriving DecidableEq
abbrev Clause (V : Type u) := Finset (Literal V)
abbrev CNF (V : Type u) := Finset (Clause V)
variable {V : Type u}
def Literal.eval (a : Assignment V) (l : Literal V) : Bool := a l.variable == l.positive
variable [DecidableEq V]
def Clause.eval (a : Assignment V) (C : Clause V) : Bool := decide (∃ l ∈ C, l.eval a = true)
end Sol
#check @Cmp.Literal.eval
#check @Sol.Literal.eval
#check @Cmp.Clause.eval
#check @Sol.Clause.eval
#check @Cmp.WidthAtMost
#check @Cmp.count
-- count really is the model count over all 2^n assignments
example : Cmp.count (V := Fin 2) ∅ = 4 := by decide
example : Cmp.count (V := Fin 1) {∅} = 0 := by decide
