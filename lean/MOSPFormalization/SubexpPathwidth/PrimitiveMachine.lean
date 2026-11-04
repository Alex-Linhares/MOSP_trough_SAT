/-
# OpenAI's machine model and canonical CNF encoding, copied verbatim

This file is a **verbatim copy of lines 1–190 and 220** of
`lean/ComparatorChallenges/SubexponentialSAT.lean` in the OpenAI mathematics
collection (`github.com/openai/math`, commit `4eaee87548250b2682affda7d05d947c05554bae`,
2026-10-29; the file's SHA-256 is
`4183b2057cff350d66848215ff7167196dfc20e1891b598fdddea59077a76685`), the comparator
statement of family 378, *The Exponential Time Hypothesis is False* (October 25, 2026).
Lines 191–219, the theorem `exact_count_and_sat` with its `sorry`, are **not** copied: its
statement is restated as the named `Prop` `SubexpCount` in `Frame.lean`, and it is never
asserted in this development (loop0014, plan `reports/subexp_pathwidth_plan.md` §0.4.1;
`reports/subexp_pathwidth.md` §2).

Copyright 2026 OpenAI. Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
agreed to in writing, software distributed under the License is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under the License.
The copy is recorded in `literature/MISSING.md` (the OpenAI collection entry) and the rest of
this development is MIT-licensed as described in the file LICENSE.

Nothing below is proved: the file contains definitions only (the canonical encoding of a CNF
over `Fin n`, the `PrimitiveMachine` multi-tape model over Mathlib's `Turing.TM0.Stmt` and
`Turing.Tape`, its `Trace`, the located configuration that monitors the visited cells, and the
runtime bound `C (L + 1)^d 2^(A · n (log log(n + 16))² / √log(n + 16))`). The namespaces are
kept as in the source so that `SubexpCount` reads character for character as the comparator.
Everything after this comment block is the copy.
-/
import Mathlib

namespace OAI.Algorithms.SubexponentialSAT.BinaryArithmetic

def bitVal (b : Bool) : ℕ := if b then 1 else 0

def toNat : List Bool → ℕ
  | [] => 0
  | b :: bs => bitVal b + 2 * toNat bs

end OAI.Algorithms.SubexponentialSAT.BinaryArithmetic

namespace OAI.Algorithms.SubexponentialSAT.SAT

universe u

abbrev Assignment (V : Type u) := V → Bool

structure Literal (V : Type u) where
  «variable» : V
  positive : Bool
  deriving DecidableEq

abbrev Clause (V : Type u) := Finset (Literal V)
abbrev CNF (V : Type u) := Finset (Clause V)

variable {V : Type u} [DecidableEq V]

def Literal.eval (a : Assignment V) (l : Literal V) : Bool :=
  a l.variable == l.positive

def Clause.eval (a : Assignment V) (C : Clause V) : Bool :=
  decide (∃ l ∈ C, l.eval a = true)

def CNF.eval (a : Assignment V) (F : CNF V) : Bool :=
  decide (∀ C ∈ F, C.eval a = true)

def WidthAtMost (k : ℕ) (F : CNF V) : Prop := ∀ C ∈ F, C.card ≤ k

section Finite

variable [Fintype V]

def satisfyingAssignments (F : CNF V) : Finset (Assignment V) :=
  Finset.univ.filter fun a => F.eval a = true

def count (F : CNF V) : ℕ := (satisfyingAssignments F).card

end Finite

end OAI.Algorithms.SubexponentialSAT.SAT

namespace OAI.Algorithms.SubexponentialSAT.Encoding

def encodeNat (n : ℕ) : List Bool := List.replicate n true ++ [false]

def frame (bits : List Bool) : List Bool :=
  bits.foldr (fun b rest => true :: b :: rest) [false]

def encodeList {α : Type*} (enc : α → List Bool) : List α → List Bool
  | [] => [false]
  | a :: as => true :: (frame (enc a) ++ encodeList enc as)

def literalCode {n : ℕ} (l : SAT.Literal (Fin n)) : ℕ :=
  2 * l.variable.val + if l.positive then 1 else 0

def clauseNumbers {n : ℕ} (C : SAT.Clause (Fin n)) : List ℕ :=
  (C.image literalCode).sort (· ≤ ·)

def cnfNumbers {n : ℕ} (F : SAT.CNF (Fin n)) : List (List ℕ) :=
  (F.image clauseNumbers).sort (· ≤ ·)

def encodeCNFBody {n : ℕ} (F : SAT.CNF (Fin n)) : List Bool :=
  encodeList (encodeList encodeNat) (cnfNumbers F)

def encodeCNF {n : ℕ} (F : SAT.CNF (Fin n)) : List Bool :=
  encodeNat n ++ encodeCNFBody F

def formulaBitLength {n : ℕ} (F : SAT.CNF (Fin n)) : ℕ := (encodeCNF F).length

end OAI.Algorithms.SubexponentialSAT.Encoding

namespace OAI.Algorithms.SubexponentialSAT.Computation

universe u

inductive Trace {α : Type u} (step : α → Option α) : ℕ → α → α → Prop
  | refl (a : α) : Trace step 0 a a
  | cons {n : ℕ} {a b c : α} :
      step a = some b → Trace step n b c → Trace step (n + 1) a c

structure PrimitiveMachine where
  tapeCount : ℕ
  stateCount : ℕ
  inputTape : Fin tapeCount
  start : Fin stateCount
  scan : Fin stateCount → Fin tapeCount
  transition : Fin stateCount → Option Bool →
    Bool ⊕ (Fin stateCount × Turing.TM0.Stmt (Option Bool))

namespace PrimitiveMachine

structure Cfg (machine : PrimitiveMachine) where
  state : Bool ⊕ Fin machine.stateCount
  tapes : Fin machine.tapeCount → Turing.Tape (Option Bool)

def step (machine : PrimitiveMachine) (c : machine.Cfg) : Option machine.Cfg :=
  match c.state with
  | .inl _ => none
  | .inr q =>
    let tapeIndex := machine.scan q
    match machine.transition q (c.tapes tapeIndex).head with
    | .inl answer => some ⟨.inl answer, c.tapes⟩
    | .inr (q', action) =>
      let nextTape :=
        match action with
        | .move direction => (c.tapes tapeIndex).move direction
        | .write symbol => (c.tapes tapeIndex).write symbol
      some ⟨.inr q', Function.update c.tapes tapeIndex nextTape⟩

def init (machine : PrimitiveMachine) (input : List Bool) : machine.Cfg :=
  ⟨.inr machine.start, fun k =>
    if k = machine.inputTape then Turing.Tape.mk₁ (input.map some)
    else Turing.Tape.mk₁ []⟩

end PrimitiveMachine

end OAI.Algorithms.SubexponentialSAT.Computation

namespace OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement

noncomputable def runtimeScale (n : ℕ) : ℝ :=
  (n : ℝ) * (Real.log (Real.log ((n : ℝ) + 16))) ^ 2 /
    Real.sqrt (Real.log ((n : ℝ) + 16))

noncomputable def runtimeBound (constant exponentConstant : ℝ)
    (degree inputBits numVars : ℕ) : ℝ :=
  constant * ((inputBits : ℝ) + 1) ^ degree *
    (2 : ℝ) ^ (exponentConstant * runtimeScale numVars)

end OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement

namespace OAI.Algorithms.SubexponentialSAT.SqrtLogSpace

open OAI.Algorithms.SubexponentialSAT.Computation

def countWord (a : ℕ) : List Bool := if a = 0 then [false] else a.bits

structure LocatedCfg (machine : PrimitiveMachine) where
  config : machine.Cfg
  position : Fin machine.tapeCount → ℤ
  lower : Fin machine.tapeCount → ℤ
  upper : Fin machine.tapeCount → ℤ

def locatedInit (machine : PrimitiveMachine) (input : List Bool) : LocatedCfg machine where
  config := machine.init input
  position _ := 0
  lower _ := 0
  upper i := if i = machine.inputTape then Int.ofNat (input.length - 1) else 0

def headDisplacement : Turing.TM0.Stmt (Option Bool) → ℤ
  | .move .left => -1
  | .move .right => 1
  | .write _ => 0

def LocatedCfg.monitor {machine : PrimitiveMachine} (c : LocatedCfg machine)
    (config : machine.Cfg) : LocatedCfg machine :=
  Sum.elim
    (fun _ => { c with config })
    (fun q =>
      Sum.elim
        (fun _ => { c with config })
        (fun targetAction =>
          let action := targetAction.2
          let i := machine.scan q
          let position := c.position i + headDisplacement action
          { config
            position := Function.update c.position i position
            lower := Function.update c.lower i (min (c.lower i) position)
            upper := Function.update c.upper i (max (c.upper i) position) })
        (machine.transition q (c.config.tapes (machine.scan q)).head))
    c.config.state

def locatedStep (machine : PrimitiveMachine) (c : LocatedCfg machine) :
    Option (LocatedCfg machine) :=
  (machine.step c.config).map c.monitor

def visitedSpace {machine : PrimitiveMachine} (c : LocatedCfg machine) : ℕ :=
  ∑ i, (c.upper i - c.lower i + 1).toNat

end OAI.Algorithms.SubexponentialSAT.SqrtLogSpace
