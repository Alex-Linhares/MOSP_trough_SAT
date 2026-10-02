/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The root split: a refutation spread over independent processes

Loop0007 item 10, `paper2/solver_fix.md` ("Item 10"), `paper2/solver_fix_split.py`. The
driver opens the top of the search tree itself, exactly as the search opens a node (free moves,
the filter, the children in loop order, the old moves each child inherits), and hands each
child to its own process, which runs the unchanged search from that state with **an empty
memo**. The processes share nothing, so the memo the sequential run would have carried from
one subtree into the next is lost; nothing else changes.

`ExecSplit` is that run: the constructors of `Exec` (`Memo.lean`) for the driver's part of
the tree, plus `task`, a call answered `false` by a complete `Exec` run from `∅` whose memo is
then discarded (the driver's memo is unchanged). The driver itself never records or hits.

## What is proved

* `Exec.union_memo`: a run from memo `M` is a run from `M ∪ N`, ending in `M′ ∪ N`. A larger
  memo is only more look-ups that the run is free not to take (`Exec` lets a node be expanded
  whatever the memo holds), and every entry the run records is recorded on top of `N`.
* `ExecSplit.exec`: every split run lifts to an `Exec` run, from any memo containing the
  driver's: each task's run from `∅` is replayed from the memo accumulated so far.
* `execSplit_repairedFullFilter_sound` and `execSplit_repairedFullFilter_mospValue`: a split run
  of the repaired filter from the root answering `false` means `¬ Solvable G k ∅`, and on the
  MOSP graph `k < mospValue`. These are `exec_repairedFullFilter_sound` and
  `exec_repairedFullFilter_mospValue` through the lift.

The old moves a task inherits are refutations made by *other* tasks (its earlier siblings, or
an ancestor's); `Exec.sound` discharges them in run order, which is why the conclusion needs
every task to have answered `false`, and why the driver claims nothing before then.
-/

import MOSPFormalization.Search.Decide

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

section General

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ)
variable (F : Finset V → Finset V → Finset V)

/-- A split run: `Exec`'s driver constructors, with `task` leaves that run from an empty memo
and leave the driver's memo as it was. -/
inductive ExecSplit :
    Set (Finset V) → Finset V → Finset V → Option (List V) → Set (Finset V) → Prop
  /-- A child handed to its own process: a complete run from `∅` answering `false`. -/
  | task {M M₁ : Set (Finset V)} {S Q : Finset V} :
      Exec G k F ∅ S Q none M₁ → ExecSplit M S Q none M
  | hit {M : Set (Finset V)} {S Q : Finset V} : S ∈ M → ExecSplit M S Q none M
  | node {M M' : Set (Finset V)} {S Q : Finset V} (l : List V) (record : Bool) : S ≠ univ →
      (∀ c, c ∈ l ↔ c ∈ F S (Q \ S)) → ExecSplit M S (Q \ S) (some l) M' →
      ExecSplit M S Q none (if record then insert S M' else M')
  | nil {M : Set (Finset V)} {S seen : Finset V} : ExecSplit M S seen (some []) M
  | cons {M M₁ M₂ : Set (Finset V)} {S seen Q' : Finset V} (c : V) (l : List V) :
      Q' ⊆ seen.filter (fun q => stepCost G (insert q S) c ≤ k) →
      ExecSplit M (cl G (insert c S)) Q' none M₁ → ExecSplit M₁ S (insert c seen) (some l) M₂ →
      ExecSplit M S seen (some (c :: l)) M₂

variable {G k F}

/-- **A larger memo changes nothing a run needs.** -/
theorem Exec.union_memo {M M' : Set (Finset V)} {S Q : Finset V} {o : Option (List V)}
    (h : Exec G k F M S Q o M') (N : Set (Finset V)) : Exec G k F (M ∪ N) S Q o (M' ∪ N) := by
  induction h with
  | hit hS => exact Exec.hit (Or.inl hS)
  | node l record hS hl _ ih =>
    have h' := Exec.node l record hS hl ih
    cases record
    · simpa using h'
    · simpa [Set.insert_union] using h'
  | nil => exact Exec.nil
  | cons c l hQ' _ _ ihc ihl => exact Exec.cons c l hQ' ihc ihl

/-- **A split run is a run.** From any memo containing the driver's, the split run lifts to an
`Exec` run ending in a memo containing the driver's final one. -/
theorem ExecSplit.exec {M M' : Set (Finset V)} {S Q : Finset V} {o : Option (List V)}
    (h : ExecSplit G k F M S Q o M') :
    ∀ N : Set (Finset V), M ⊆ N → ∃ N', M' ⊆ N' ∧ Exec G k F N S Q o N' := by
  induction h with
  | @task M₀ M₁ S₀ Q₀ hrun =>
    intro N hN
    refine ⟨M₁ ∪ N, hN.trans Set.subset_union_right, ?_⟩
    simpa using hrun.union_memo N
  | hit hS =>
    intro N hN
    exact ⟨N, hN, Exec.hit (hN hS)⟩
  | node l record hS hl _ ih =>
    intro N hN
    obtain ⟨N', hMN', h'⟩ := ih N hN
    refine ⟨_, ?_, Exec.node l record hS hl h'⟩
    cases record
    · exact hMN'
    · exact Set.insert_subset_insert hMN'
  | nil =>
    intro N hN
    exact ⟨N, hN, Exec.nil⟩
  | cons c l hQ' _ _ ihc ihl =>
    intro N hN
    obtain ⟨N₁, hN₁, h₁⟩ := ihc N hN
    obtain ⟨N₂, hN₂, h₂⟩ := ihl N₁ hN₁
    exact ⟨N₂, hN₂, Exec.cons c l hQ' h₁ h₂⟩

/-- A split run from the root, lifted. -/
theorem ExecSplit.exec_root {M' : Set (Finset V)} (h : ExecSplit G k F ∅ ∅ ∅ none M') :
    ∃ N', Exec G k F ∅ ∅ ∅ none N' := by
  obtain ⟨N', -, h'⟩ := h.exec ∅ subset_rfl
  exact ⟨N', h'⟩

end General

section Repaired

variable {V : Type*} [Fintype V] [LinearOrder V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-- **The split refutation is genuine**: a split run of the repaired search from the root
answering `false` means no closing order costs at most `k`. -/
theorem execSplit_repairedFullFilter_sound {k L : ℕ} {M' : Set (Finset V)}
    (h : ExecSplit G k (repairedFullFilter G k L) ∅ ∅ ∅ none M') : ¬ Solvable G k ∅ := by
  obtain ⟨N', h'⟩ := h.exec_root
  exact exec_repairedFullFilter_sound h'

end Repaired

section RepairedMOSP

variable {C Pt : Type*} [Fintype C] [LinearOrder C] [Fintype Pt] [DecidableEq Pt]

/-- **A split refutation by the repaired search on the MOSP graph means MOSP > k.** -/
theorem execSplit_repairedFullFilter_mospValue (M : MOSPInstance C Pt)
    [DecidableRel M.requires] (hreq : ∃ c p, M.requires c p) {k L : ℕ} {M' : Set (Finset C)}
    (h : ExecSplit M.mospGraph k (repairedFullFilter M.mospGraph k L) ∅ ∅ ∅ none M') :
    k < M.mospValue := by
  obtain ⟨N', h'⟩ := h.exec_root
  exact exec_repairedFullFilter_mospValue M hreq h'

end RepairedMOSP

end Search

end MOSPFormalization
