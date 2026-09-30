/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The definite move (Chu & Stuckey 2009, Theorem 1): false as stated, and its repair

Loop0006 item 08, `paper2/search_soundness.md` §2.2 and §4.2. Source: Chu & Stuckey,
*Minimizing the maximum number of open stacks by customer search*, CP 2009, §3.1
(preprint p. 6):

> **Theorem 1.** Suppose `S ++ [q]` is playable and `close(q, S) ≥ open(q, S)`, then if
> `U′ = S ++ R` is a solution, there exists a solution `U = S ++ [q] ++ R′`.

with `open(q, S) = |o(q, S)|`, `o(q, S) = N[q] ∖ O(S)` and `close(q, S) = |{d : o(d, S) ⊆
o(q, S)}|`. The code (`satisfiability/customer_search.py:404–412`, `customer_search.c:313–330`)
checks exactly this, with `d` ranging over the customers not yet closed at the free-closed
state `S`, and keeps only the first such `q` in index order.

## What is proved

* `openStacks_submodular` — the number of open stacks `b(T) = |O(T) ∖ T|` is
  **submodular**: `b(A ∪ B) + b(A ∩ B) ≤ b(A) + b(B)`. This is the whole engine.
* `isDefinite_iff` — the code's premise `open(q, S) ≤ close(q, S)` says exactly that the
  child has no more open stacks than the parent: `b(cl(S ∪ {q})) ≤ b(S)`.
* **The theorem is false.** `definiteMove_counterexample`: on a 14-customer graph
  (`cexGraph`), at the free-closed state `S = {2}` with `k = 6`, the move `q = 0` is
  playable, `close(0, S) = open(0, S) = 3`, `0` is the first customer in index order, the
  node invariant holds, a solution from `S` exists (`Solvable`, hence `SearchSol`), and
  **no solution exists from the child `cl(S ∪ {0}) = {0, 2, 3, 4}`**. So the rule, as the
  paper states it and as the C and Python implement it, can discard the last solution at a
  node. The paper's proof fails at its last sentence: customers `d` with `o(d, S) ⊆ o(q, S)`
  that `U′` had already closed before `q` are not "extra stacks closed" — here `3` and `4`
  share the single new stack `0`, so closing them first gains two stacks for one, which
  moving `q` forward throws away.
* **The repair** — `IsHereditarilyDefinite G S q`: `b(cl(S ∪ {q})) ≤ b(B)` for every `B`
  with `S ⊆ B ⊆ cl(S ∪ {q})` and `q ∉ B` (the code's premise is the case `B = S`).
  `solvable_cl_insert_of_hereditarilyDefinite`: under it, **`P_k(S) → P_k(cl(S ∪ {q}))`**,
  with no other hypothesis, by the uncrossing argument: along any solution from `S` replace
  each prefix `T` by `T ∪ cl(S ∪ {q})`; submodularity at `T ∩ cl(S ∪ {q})` makes each step
  no dearer. `searchSol_cl_insert_of_hereditarilyDefinite` is the search's form: at a node
  with the invariant `|O(S) ∖ S| ≤ k`, `Sol_k(S) → Sol_k(S·q)`, so keeping only `q` is
  sound when `q` is playable.
* `isHereditarilyDefinite_of_openCount_le_one` — the repair covers every `q` opening at most
  one new stack (the `open ≤ 1` cases of the code's rule, which are therefore sound).
  `isHereditarilyDefinite_of_matching` — the form that is cheap to compute: `q` is
  hereditarily definite if `open(q, S) − 1` distinct customers `d ≠ q` with
  `o(d, S) ⊆ o(q, S)` can be matched to distinct stacks `y ∈ o(d, S)` (an injection). The
  converse holds by Hall's theorem with deficiency (checked, not proved here).
* `not_isHereditarilyDefinite_cex` — the counterexample violates the repair at
  `B = {2, 3, 4}`.

## Checks

`python -m paper2.search_check --definite` (`paper2/search_check.py`) transcribes these
definitions and checks them by brute force; see `paper2/search_soundness.md` §4.2.
-/

import MOSPFormalization.Search.Basic

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Definitions -/

/-- `b(T) = |O(T) ∖ T|`: the stacks open once the customers of `T` are closed. -/
def openStacks (T : Finset V) : ℕ := (opened G T \ T).card

/-- `o(c, S) = N[c] ∖ O(S)`: the stacks closing `c` next would newly open. -/
def newlyOpened (S : Finset V) (c : V) : Finset V := nbhd G c \ opened G S

/-- `open(c, S) = |o(c, S)|`. -/
def openCount (S : Finset V) (c : V) : ℕ := (newlyOpened G S c).card

/-- `close(q, S)`: the customers not in `S` whose new stacks all open with `q`'s, as the code
counts them (`Py:408`, `C:320–323`; at a free-closed `S` the unclosed customers are `V ∖ S`). -/
def closeCount (S : Finset V) (q : V) : ℕ :=
  ((univ \ S).filter (fun d => newlyOpened G S d ⊆ newlyOpened G S q)).card

/-- The code's premise of the definite move, besides playability: `open(q, S) ≤ close(q, S)`. -/
def IsDefinite (S : Finset V) (q : V) : Prop := openCount G S q ≤ closeCount G S q

/-- The repaired premise: no state between `S` and the child `cl(S ∪ {q})` that avoids `q`
has fewer open stacks than the child. -/
def IsHereditarilyDefinite (S : Finset V) (q : V) : Prop :=
  ∀ B : Finset V, S ⊆ B → B ⊆ cl G (insert q S) → q ∉ B →
    openStacks G (cl G (insert q S)) ≤ openStacks G B

instance (S : Finset V) (q : V) : Decidable (IsDefinite G S q) :=
  inferInstanceAs (Decidable (_ ≤ _))

/-! ### Open stacks -/

variable {G}

theorem openStacks_add_card (T : Finset V) : openStacks G T + T.card = (opened G T).card :=
  Finset.card_sdiff_add_card_eq_card (subset_opened T)

theorem opened_union (A B : Finset V) : opened G (A ∪ B) = opened G A ∪ opened G B := by
  ext v
  simp only [mem_opened, Finset.mem_union]
  constructor
  · rintro ⟨c, hc | hc, hv⟩
    · exact Or.inl ⟨c, hc, hv⟩
    · exact Or.inr ⟨c, hc, hv⟩
  · rintro (⟨c, hc, hv⟩ | ⟨c, hc, hv⟩)
    · exact ⟨c, Or.inl hc, hv⟩
    · exact ⟨c, Or.inr hc, hv⟩

theorem opened_inter_subset (A B : Finset V) :
    opened G (A ∩ B) ⊆ opened G A ∩ opened G B :=
  Finset.subset_inter (opened_mono Finset.inter_subset_left)
    (opened_mono Finset.inter_subset_right)

/-- **The number of open stacks is submodular.** -/
theorem openStacks_submodular (A B : Finset V) :
    openStacks G (A ∪ B) + openStacks G (A ∩ B) ≤ openStacks G A + openStacks G B := by
  have h1 := openStacks_add_card (G := G) (A ∪ B)
  have h2 := openStacks_add_card (G := G) (A ∩ B)
  have h3 := openStacks_add_card (G := G) A
  have h4 := openStacks_add_card (G := G) B
  have h5 := Finset.card_union_add_card_inter A B
  have h6 := Finset.card_union_add_card_inter (opened G A) (opened G B)
  have h7 := Finset.card_le_card (opened_inter_subset (G := G) A B)
  rw [opened_union] at h1
  omega

/-- Closing `c ∉ T` costs the open stacks after it, plus `c` itself. -/
theorem stepCost_eq_openStacks_insert_add_one {T : Finset V} {c : V} (hc : c ∉ T) :
    stepCost G T c = openStacks G (insert c T) + 1 := by
  unfold stepCost openStacks
  have hcm : c ∈ opened G (insert c T) := subset_opened _ (Finset.mem_insert_self _ _)
  have : opened G (insert c T) \ T = insert c (opened G (insert c T) \ insert c T) := by
    ext x
    simp only [Finset.mem_sdiff, Finset.mem_insert]
    constructor
    · rintro ⟨hx, hxT⟩
      by_cases hxc : x = c
      · exact Or.inl hxc
      · exact Or.inr ⟨hx, fun h => h.elim hxc hxT⟩
    · rintro (rfl | ⟨hx, hxT⟩)
      · exact ⟨hcm, hc⟩
      · exact ⟨hx, fun h => hxT (Or.inr h)⟩
  rw [this, Finset.card_insert_of_notMem (by simp)]

theorem cl_cl (T : Finset V) : cl G (cl G T) = cl G T := by
  show finished G (opened G (cl G T)) = cl G T
  rw [opened_cl]
  rfl

theorem subset_cl_insert (S : Finset V) (q : V) : S ⊆ cl G (insert q S) :=
  (Finset.subset_insert _ _).trans (subset_cl _)

theorem mem_cl_insert_self (S : Finset V) (q : V) : q ∈ cl G (insert q S) :=
  subset_cl _ (Finset.mem_insert_self _ _)

/-- `close(q, S)` counts exactly the customers the child closes beyond `S`. -/
theorem closeCount_eq (S : Finset V) (q : V) :
    closeCount G S q = (cl G (insert q S) \ S).card := by
  have : (univ \ S).filter (fun d => newlyOpened G S d ⊆ newlyOpened G S q) =
      cl G (insert q S) \ S := by
    refine Finset.ext fun d => ?_
    rw [Finset.mem_filter, Finset.mem_sdiff, Finset.mem_sdiff, cl, mem_finished]
    simp only [Finset.mem_univ, true_and, newlyOpened, opened_insert]
    constructor
    · rintro ⟨hd, h⟩
      refine ⟨fun x hx => ?_, hd⟩
      by_cases hxo : x ∈ opened G S
      · exact Finset.mem_union_right _ hxo
      · exact Finset.mem_union_left _ (Finset.mem_sdiff.1 (h (Finset.mem_sdiff.2 ⟨hx, hxo⟩))).1
    · rintro ⟨h, hd⟩
      refine ⟨hd, fun x hx => ?_⟩
      obtain ⟨hxd, hxo⟩ := Finset.mem_sdiff.1 hx
      rcases Finset.mem_union.1 (h hxd) with h' | h'
      · exact Finset.mem_sdiff.2 ⟨h', hxo⟩
      · exact absurd h' hxo
  unfold closeCount
  rw [this]

theorem card_opened_insert (S : Finset V) (q : V) :
    (opened G (insert q S)).card = (opened G S).card + openCount G S q := by
  unfold openCount newlyOpened
  rw [opened_insert, Finset.union_comm, ← Finset.card_union_of_disjoint Finset.disjoint_sdiff,
    Finset.union_sdiff_self_eq_union]

/-- **The code's premise, restated**: `open(q, S) ≤ close(q, S)` iff the child
`cl(S ∪ {q})` has no more open stacks than `S`. -/
theorem isDefinite_iff (S : Finset V) (q : V) :
    IsDefinite G S q ↔ openStacks G (cl G (insert q S)) ≤ openStacks G S := by
  unfold IsDefinite
  rw [closeCount_eq]
  have h1 := openStacks_add_card (G := G) (cl G (insert q S))
  have h2 := openStacks_add_card (G := G) S
  have h3 := card_opened_insert (G := G) S q
  have h4 := Finset.card_sdiff_add_card_eq_card (subset_cl_insert (G := G) S q)
  rw [opened_cl] at h1
  omega

theorem IsHereditarilyDefinite.isDefinite {S : Finset V} {q : V} (h : IsHereditarilyDefinite G S q)
    (hq : q ∉ S) : IsDefinite G S q :=
  (isDefinite_iff S q).2 (h S le_rfl (subset_cl_insert S q) hq)

/-! ### The repaired rule is sound -/

/-- The uncrossing step: after `T ⊇ S` (not containing `q`), closing `c` outside the child
costs no more once the child's customers are added to `T`. -/
theorem stepCost_union_cl_le {S T : Finset V} {q c : V} (h : IsHereditarilyDefinite G S q)
    (hST : S ⊆ T) (hqT : q ∉ T) (hcT : c ∉ T) (hcX : c ∉ cl G (insert q S)) :
    stepCost G (T ∪ cl G (insert q S)) c ≤ stepCost G T c := by
  set X := cl G (insert q S)
  have hc' : c ∉ T ∪ X := by simp [hcT, hcX]
  rw [stepCost_eq_openStacks_insert_add_one hcT, stepCost_eq_openStacks_insert_add_one hc']
  have hsub := openStacks_submodular (G := G) (insert c T) X
  have hB : openStacks G X ≤ openStacks G (insert c T ∩ X) := by
    refine h _ (Finset.subset_inter (hST.trans (Finset.subset_insert _ _)) (subset_cl_insert S q))
      Finset.inter_subset_right ?_
    intro hq
    rcases Finset.mem_insert.1 (Finset.mem_inter.1 hq).1 with h' | h'
    · exact hcX (h' ▸ mem_cl_insert_self S q)
    · exact hqT h'
  rw [← Finset.insert_union]
  omega

theorem solvable_union_cl_of_hereditarilyDefinite {k : ℕ} {S : Finset V} {q : V}
    (h : IsHereditarilyDefinite G S q) :
    ∀ (l : List V) (T : Finset V), S ⊆ T → q ∉ T → IsClosingOrder T l → orderCost G T l ≤ k →
      Solvable G k (T ∪ cl G (insert q S)) := by
  intro l
  induction l with
  | nil =>
    intro T _ hqT hl _
    exact absurd (isClosingOrder_nil_iff.1 hl ▸ Finset.mem_univ q) hqT
  | cons c l ih =>
    intro T hST hqT hl hcost
    obtain ⟨hcT, hl'⟩ := IsClosingOrder.cons_iff.1 hl
    rw [orderCost_cons] at hcost
    have hc1 : stepCost G T c ≤ k := le_trans (le_max_left _ _) hcost
    have hc2 : orderCost G (insert c T) l ≤ k := le_trans (le_max_right _ _) hcost
    by_cases hcq : c = q
    · subst hcq
      refine solvable_mono ⟨l, hl', hc2⟩ ?_ ?_
      · exact Finset.insert_subset (Finset.mem_union_right _ (mem_cl_insert_self S c))
          Finset.subset_union_left
      · rw [opened_union, opened_cl, opened_insert, opened_insert]
        exact Finset.union_subset Finset.subset_union_right
          (Finset.union_subset Finset.subset_union_left
            ((opened_mono hST).trans Finset.subset_union_right))
    have hqT' : q ∉ insert c T := by simp [Ne.symm hcq, hqT]
    have hrest := ih (insert c T) (hST.trans (Finset.subset_insert _ _)) hqT' hl' hc2
    by_cases hcX : c ∈ cl G (insert q S)
    · have : insert c T ∪ cl G (insert q S) = T ∪ cl G (insert q S) := by
        rw [Finset.insert_union, Finset.insert_eq_of_mem (Finset.mem_union_right _ hcX)]
      rwa [this] at hrest
    · rw [Finset.insert_union] at hrest
      exact solvable_of_solvable_insert (by simp [hcT, hcX])
        ((stepCost_union_cl_le h hST hqT hcT hcX).trans hc1) hrest

/-- **The repaired definite move is sound**: under `IsHereditarilyDefinite`, a solution from
`S` gives a solution from the child `cl(S ∪ {q})`. -/
theorem solvable_cl_insert_of_hereditarilyDefinite {k : ℕ} {S : Finset V} {q : V}
    (h : IsHereditarilyDefinite G S q) (hq : q ∉ S) (hs : Solvable G k S) :
    Solvable G k (cl G (insert q S)) := by
  obtain ⟨l, hl, hc⟩ := hs
  have := solvable_union_cl_of_hereditarilyDefinite h l S le_rfl hq hl hc
  rwa [Finset.union_eq_right.2 (subset_cl_insert S q)] at this

/-- The search's form: at a node with the invariant `|O(S) ∖ S| ≤ k`, `Sol_k(S) → Sol_k(S·q)`.
With `q` playable, keeping `q` as the only child therefore never loses the last solution. -/
theorem searchSol_cl_insert_of_hereditarilyDefinite {k : ℕ} {S : Finset V} {q : V}
    (h : IsHereditarilyDefinite G S q) (hq : q ∉ S) (hk : (opened G S \ S).card ≤ k)
    (hs : SearchSol G k S) : SearchSol G k (cl G (insert q S)) := by
  have := searchSol_cl_of_solvable _ _ le_rfl
    (solvable_cl_insert_of_hereditarilyDefinite h hq (solvable_of_searchSol hs hk))
  rwa [cl_cl] at this

/-- The repair covers every move that opens at most one new stack. -/
theorem isHereditarilyDefinite_of_openCount_le_one {S : Finset V} {q : V}
    (h : openCount G S q ≤ 1) : IsHereditarilyDefinite G S q := by
  intro B hSB hBX hqB
  have h1 := openStacks_add_card (G := G) (cl G (insert q S))
  have h2 := openStacks_add_card (G := G) B
  have h3 := card_opened_insert (G := G) S q
  rw [opened_cl] at h1
  have h4 : (opened G S).card ≤ (opened G B).card := Finset.card_le_card (opened_mono hSB)
  have h5 : B.card < (cl G (insert q S)).card :=
    Finset.card_lt_card ⟨hBX, fun h => hqB (h (mem_cl_insert_self S q))⟩
  omega

/-- A cheap sufficient condition: `open(q, S) − 1` of the customers the child closes, other
than `q`, carry distinct new stacks. `f` matches each `d ∈ M` to a stack `f d ∈ o(d, S)`. -/
theorem isHereditarilyDefinite_of_matching {S : Finset V} {q : V}
    (M : Finset V) (f : V → V) (hM : M ⊆ cl G (insert q S) \ insert q S)
    (hf : ∀ d ∈ M, f d ∈ newlyOpened G S d) (hinj : Set.InjOn f M)
    (hcard : openCount G S q ≤ M.card + 1) : IsHereditarilyDefinite G S q := by
  intro B hSB hBX hqB
  -- `O(B) ⊇ O(S) ∪ f(M ∩ B)`, the second part disjoint from `O(S)`.
  have hfB : (M ∩ B).image f ⊆ opened G B \ opened G S := by
    intro y hy
    obtain ⟨d, hd, rfl⟩ := Finset.mem_image.1 hy
    obtain ⟨hdn, hdo⟩ := Finset.mem_sdiff.1 (hf d (Finset.mem_inter.1 hd).1)
    exact Finset.mem_sdiff.2 ⟨mem_opened.2 ⟨d, (Finset.mem_inter.1 hd).2, hdn⟩, hdo⟩
  have hcardf : ((M ∩ B).image f).card = (M ∩ B).card :=
    Finset.card_image_of_injOn (hinj.mono (Finset.coe_subset.2 Finset.inter_subset_left))
  have hOB : (opened G S).card + (M ∩ B).card ≤ (opened G B).card := by
    have := Finset.card_le_card hfB
    rw [Finset.card_sdiff_of_subset (opened_mono hSB)] at this
    have := Finset.card_le_card (opened_mono (G := G) hSB)
    omega
  -- `|X| ≥ |B| + 1 + |M ∖ B|`: `X` contains `B`, `q` and the unclosed part of `M`.
  have hX : B.card + 1 + (M \ B).card ≤ (cl G (insert q S)).card := by
    have hsub : B ∪ insert q (M \ B) ⊆ cl G (insert q S) :=
      Finset.union_subset hBX (Finset.insert_subset (mem_cl_insert_self S q)
        (fun x hx => (Finset.mem_sdiff.1 (hM (Finset.mem_sdiff.1 hx).1)).1))
    have hdisj : Disjoint B (insert q (M \ B)) := by
      rw [Finset.disjoint_insert_right]
      exact ⟨hqB, Finset.disjoint_sdiff⟩
    have hqM : q ∉ M \ B := fun h =>
      (Finset.mem_sdiff.1 (hM (Finset.mem_sdiff.1 h).1)).2 (Finset.mem_insert_self _ _)
    have := Finset.card_le_card hsub
    rw [Finset.card_union_of_disjoint hdisj, Finset.card_insert_of_notMem hqM] at this
    omega
  have h1 := openStacks_add_card (G := G) (cl G (insert q S))
  have h2 := openStacks_add_card (G := G) B
  have h3 := card_opened_insert (G := G) S q
  rw [opened_cl] at h1
  have h6 := Finset.card_sdiff_add_card_inter M B
  omega

/-! ### An invariant family refutes -/

/-- If a family of states contains `T`, not `V`, and is closed under playable moves, no
solution exists from `T`. -/
theorem not_solvable_of_invariant {k : ℕ} (F : Finset (Finset V)) (huniv : univ ∉ F)
    (hF : ∀ A ∈ F, ∀ c, c ∉ A → stepCost G A c ≤ k → insert c A ∈ F) {T : Finset V}
    (hT : T ∈ F) : ¬ Solvable G k T := by
  rintro ⟨l, hl, hc⟩
  induction l generalizing T with
  | nil => exact huniv (isClosingOrder_nil_iff.1 hl ▸ hT)
  | cons c l ih =>
    obtain ⟨hcT, hl'⟩ := IsClosingOrder.cons_iff.1 hl
    rw [orderCost_cons] at hc
    exact ih (hF T hT c hcT (le_trans (le_max_left _ _) hc)) hl' (le_trans (le_max_right _ _) hc)

/-! ### The counterexample to Theorem 1 -/

/-- The edges of the counterexample, found by exhaustive checking of the rule's conclusion
on random graphs and minimised by vertex and edge deletion (`paper2/search_check.py`). -/
def cexEdges : List (ℕ × ℕ) :=
  [(0, 3), (0, 4), (0, 7), (0, 11), (1, 2), (1, 5), (1, 6), (2, 3), (2, 4), (5, 9), (5, 11),
   (5, 12), (6, 8), (6, 13), (7, 9), (7, 10), (7, 13), (8, 9), (8, 10), (8, 11), (9, 10),
   (9, 11), (10, 11), (10, 12), (10, 13), (12, 13)]

/-- A 14-customer MOSP graph on which the definite move loses the last solution. -/
def cexGraph : SimpleGraph (Fin 14) := SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ cexEdges

instance : DecidableRel cexGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ cexEdges ∨ (b.val, a.val) ∈ cexEdges)))

/-- The states reachable from the child `{0, 2, 3, 4}` within `6` stacks. -/
def cexFamily : Finset (Finset (Fin 14)) :=
  {{0, 2, 3, 4}, {0, 1, 2, 3, 4}, {0, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}, {0, 2, 3, 4, 6},
   {0, 1, 2, 3, 4, 6}, {0, 2, 3, 4, 7}}

set_option maxRecDepth 100000 in
theorem cexFamily_closed : ∀ A ∈ cexFamily, ∀ c, c ∉ A → stepCost cexGraph A c ≤ 6 →
    insert c A ∈ cexFamily := by
  decide +kernel

theorem cex_cl_insert : cl cexGraph (insert 0 ({2} : Finset (Fin 14))) = {0, 2, 3, 4} := by
  decide

theorem cex_not_solvable_child : ¬ Solvable cexGraph 6 (cl cexGraph (insert 0 {2})) := by
  rw [cex_cl_insert]
  exact not_solvable_of_invariant cexFamily (by decide) cexFamily_closed (by decide)

theorem cex_solvable : Solvable cexGraph 6 ({2} : Finset (Fin 14)) :=
  ⟨[1, 3, 4, 6, 12, 13, 0, 5, 7, 8, 9, 10, 11], by unfold IsClosingOrder; decide, by decide⟩

/-- **Chu & Stuckey's Theorem 1 is false, in the form the code implements.** At the
free-closed state `{2}` with `k = 6` and the node invariant, customer `0` is playable,
`open(0, S) ≤ close(0, S)`, and no smaller customer is playable and definite; a solution
exists from `{2}` (in the search's sense too), and none from the child the rule keeps. -/
theorem definiteMove_counterexample :
    let S : Finset (Fin 14) := {2}
    cl cexGraph S = S ∧ (opened cexGraph S \ S).card ≤ 6 ∧ (0 : Fin 14) ∉ S ∧
      stepCost cexGraph S 0 ≤ 6 ∧ IsDefinite cexGraph S 0 ∧
      (∀ q < (0 : Fin 14), ¬ (stepCost cexGraph S q ≤ 6 ∧ IsDefinite cexGraph S q)) ∧
      Solvable cexGraph 6 S ∧ SearchSol cexGraph 6 S ∧
      ¬ Solvable cexGraph 6 (cl cexGraph (insert 0 S)) ∧
      ¬ SearchSol cexGraph 6 (cl cexGraph (insert 0 S)) := by
  intro S
  have hcl : cl cexGraph S = S := by decide
  have hinv : (opened cexGraph S \ S).card ≤ 6 := by decide
  have hsol := cex_solvable
  refine ⟨hcl, hinv, by decide, by decide, by decide, fun q hq => absurd hq (Fin.not_lt_zero q),
    hsol, ?_, cex_not_solvable_child, ?_⟩
  · have := searchSol_cl_of_solvable (G := cexGraph) _ S le_rfl hsol
    rwa [hcl] at this
  · intro h
    have hk : (opened cexGraph (cl cexGraph (insert 0 S)) \ cl cexGraph (insert 0 S)).card ≤ 6 := by
      rw [cex_cl_insert]; decide
    exact cex_not_solvable_child (solvable_of_searchSol h hk)

/-- The counterexample violates the repair, at `B = {2, 3, 4}`: closing `3` and `4`, which
share the single new stack `0`, leaves `2` open stacks, and the child leaves `3`. -/
theorem not_isHereditarilyDefinite_cex : ¬ IsHereditarilyDefinite cexGraph {2} 0 := by
  intro h
  have := h {2, 3, 4} (by decide) (by rw [cex_cl_insert]; decide) (by decide)
  rw [cex_cl_insert] at this
  revert this
  decide

end Search

end MOSPFormalization
