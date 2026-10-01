/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The better move (Chu & Stuckey 2009, Theorem 2): the corrected form is still unsound

Loop0006 item 10, `paper2/search_soundness.md` §2.4 and §4.4. Source: Chu & Stuckey,
*Minimizing the maximum number of open stacks by customer search*, CP 2009, §3.2
(preprint p. 6):

> **Theorem 2.** Suppose `S ++ [q]` and `S ++ [r, q]` are playable and
> `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})` then if `U′ = S ++ [r] ++ R` is a solution there
> exists a solution `U = S ++ [q] ++ R′`.

The code (`customer_search.c:169–266`, `better_move_pass`; the Python has no such rule) runs
it over the survivors `W` of the subset rule, in index order, after the definite move and the
subset rule, and drops `r ∈ W` when an earlier `q ∈ W` (among the first `L`, or any if
`L = 0`) meets premise 3, `|(O(S) ∪ N[r] ∪ N[q]) ∖ (S ∪ {r})| ≤ k`, and the **corrected**
premise 4, `open′ ≤ close′`, where `close′` counts the customers `d ∉ S ∪ {r}` with
`∅ ≠ N[d] ∖ X_r ⊆ N[q] ∖ X_r`, `X_r = O(S) ∪ N[r]` (the fix of 2026-09-26 leaves out the
customers `r` finishes).

## What is proved

* `isBetter_iff` — premise 4 is exactly the code's definite-move premise for `q` at the child
  `cl(S ∪ {r})`, and premise 3 is `q`'s step cost there before free moves. So the better move
  is Theorem 1 at the child followed by a swap, and **it inherits Theorem 1's falsity**
  (`DefiniteMove.lean`).
* **The corrected rule is false.** `betterMove_counterexample`: on `cexGraph` (the definite
  move's 14-customer counterexample) at the root `S = ∅` with `k = 6`, the definite move does
  not fire, `0` and `2` both survive the subset rule, `0 < 2`, `0` is playable, and the
  corrected premise holds for `r = 2`, `q = 0`; so the code drops `2` citing `0`. A solution
  exists from `S·2 = {2}` and none from `S·0 = {0}`: **the rule's own conclusion fails.** At
  this node the filter still keeps a customer with a solution (`betterMove_counterexample_node`),
  so this is a false link, not yet a lost node.
* **The repair**, `IsRepairedBetter`: premise 3 and `q` hereditarily definite at `cl(S ∪ {r})`
  (item 08's repair, at the child). `searchSol_cl_insert_of_repairedBetter`: with `r`
  playable at `S` (`q`'s playability is not needed), `Sol_k(S·r) → Sol_k(S·q)`. The proof is the paper's: the repaired Theorem 1
  at `S·r`, then the swap — `q` first costs at most `k` by playability, `r` second costs at
  most premise 3, and both orders reach `cl(S ∪ {q, r})`. `IsRepairedBetter.isBetter`: the
  repair implies the code's premise, and `isRepairedBetter_of_openCount_le_one` covers every
  `q` opening at most one stack at the child.
* **The composition.** `betterFilterBy_sound`: any pairwise-sound "cite an earlier survivor"
  rule is node-sound, because the least survivor with a solution is never dropped.
  `fullFilter_sound`: `definite → subset → better` is node-sound whenever the definite premise
  and the better premise are each sound; `repairedFullFilter_sound` instantiates it with both
  repairs, under the node invariant, with any `L` and any family `Q` of refuted old moves.
* **Bug A** (`IsBetterOld`, the close count that also counts the customers `r` finishes),
  `bugA_counterexample`: on a 12-customer graph at `S = ∅`, `k = 4`, the old premise holds for
  `r = 6`, `q = 4`, the corrected one does not, and `S·6` has a solution while `S·4` has none.
* **Bug B** (the better move first, then the subset rule citing every remaining customer),
  `bugB_counterexample`: on an 8-customer graph at `S = {2}`, `k = 4`, the old order keeps
  `{6}` (the better move drops `3` citing `0`, the subset rule drops `0` citing `3`), and
  `S·6` has no solution while `S` has one; the fixed order keeps `{3, 6}` and `S·3` has one.
  Every premise used is the corrected one: the fault is the cycle.

## Checks

`python -m paper2.search_check --better` (`paper2/search_check.py`) transcribes these
definitions and checks them by brute force, and `paper2/better_hunt.c` hunts for lost nodes;
see `paper2/search_soundness.md` §4.4.
-/

import MOSPFormalization.Search.SubsetRule

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

section

variable {V : Type*} [Fintype V] [LinearOrder V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Definitions -/

/-- `open′ = |N[q] ∖ X_r|`, `X_r = O(S ∪ {r})` (`C:219–220`). -/
def betterOpen (S : Finset V) (r q : V) : ℕ := (nbhd G q \ opened G (insert r S)).card

/-- The corrected `close′`: the customers `d ∉ S ∪ {r}` with `∅ ≠ N[d] ∖ X_r ⊆ N[q] ∖ X_r`
(`C:221–225` with `count_finished = 0`). -/
def betterClose (S : Finset V) (r q : V) : ℕ :=
  ((univ \ insert r S).filter (fun d => (nbhd G d \ opened G (insert r S)).Nonempty ∧
    nbhd G d \ opened G (insert r S) ⊆ nbhd G q \ opened G (insert r S))).card

/-- Bug A's `close′`: the same count without `N[d] ∖ X_r ≠ ∅`, so the customers `r` finishes
count too (`count_finished = 1`, `BM_OLD_CLOSE_COUNT`). -/
def betterCloseOld (S : Finset V) (r q : V) : ℕ :=
  ((univ \ insert r S).filter (fun d =>
    nbhd G d \ opened G (insert r S) ⊆ nbhd G q \ opened G (insert r S))).card

/-- The code's premise for dropping `r` citing `q` (premises 3 and 4 of §2.4). -/
def IsBetter (k : ℕ) (S : Finset V) (r q : V) : Prop :=
  stepCost G (insert r S) q ≤ k ∧ betterOpen G S r q ≤ betterClose G S r q

/-- Bug A's premise. -/
def IsBetterOld (k : ℕ) (S : Finset V) (r q : V) : Prop :=
  stepCost G (insert r S) q ≤ k ∧ betterOpen G S r q ≤ betterCloseOld G S r q

/-- The repaired premise: premise 3, and `q` hereditarily definite at the child `cl(S ∪ {r})`. -/
def IsRepairedBetter (k : ℕ) (S : Finset V) (r q : V) : Prop :=
  stepCost G (insert r S) q ≤ k ∧ IsHereditarilyDefinite G (cl G (insert r S)) q

instance (k : ℕ) (S : Finset V) (r q : V) : Decidable (IsBetter G k S r q) := by
  unfold IsBetter; infer_instance

instance (k : ℕ) (S : Finset V) (r q : V) : Decidable (IsBetterOld G k S r q) := by
  unfold IsBetterOld; infer_instance

/-- Premise 1: `q` is among the first `L` members of `W` (every earlier one if `L = 0`). -/
def withinLimit (L : ℕ) (W : Finset V) (q : V) : Prop := L = 0 ∨ (W.filter (· < q)).card < L

instance (L : ℕ) (W : Finset V) (q : V) : Decidable (withinLimit L W q) := by
  unfold withinLimit; infer_instance

/-- The code's citation relation over the list `W`: `q` within the limit and the premise. -/
def betterCite (k L : ℕ) (S W : Finset V) (r q : V) : Prop :=
  withinLimit L W q ∧ IsBetter G k S r q

instance (k L : ℕ) (S W : Finset V) : DecidableRel (betterCite G k L S W) := fun r q => by
  unfold betterCite; infer_instance

/-- A better-move pass over `W`: `r` goes if an earlier `q ∈ W` is cited by `B`. Since the
dominator loop does not consult whether `q` itself survives, this is exactly the C's pass. -/
def betterFilterBy (B : V → V → Prop) [DecidableRel B] (W : Finset V) : Finset V :=
  W.filter (fun r => ¬ ∃ q ∈ W, q < r ∧ B r q)

/-- The filter in the fixed order `definite → subset → better` over the playable candidates
`P`: the least `q` meeting `D`, alone, if any; else the better pass over the subset survivors,
the citation relation `B W` depending on the list `W` it runs over. -/
def fullFilter (D : V → Prop) [DecidablePred D] (B : Finset V → V → V → Prop)
    [∀ W, DecidableRel (B W)] (S P : Finset V) : Finset V :=
  if h : (P.filter D).Nonempty then {(P.filter D).min' h}
  else betterFilterBy (B (subsetFilter G S P)) (subsetFilter G S P)

/-- The code's filter at the node `(S, Q)`, better move with limit `L`. -/
def codeFullFilter (k L : ℕ) (S Q : Finset V) : Finset V :=
  fullFilter G (IsDefinite G S) (betterCite G k L S) S (playable G k S ((univ \ S) \ Q))

/-- Both repairs. -/
noncomputable def repairedFullFilter (k L : ℕ) (S Q : Finset V) : Finset V :=
  @fullFilter V _ _ G _ (IsHereditarilyDefinite G S) (Classical.decPred _)
    (fun W r q => withinLimit L W q ∧ IsRepairedBetter G k S r q) (fun _ => Classical.decRel _) S
    (playable G k S ((univ \ S) \ Q))

/-- Bug B, the order before 2026-09-26: the better move over the playable candidates first,
then the subset rule over its survivors, citing every customer of `V ∖ S` (discarded ones
included). -/
def oldOrderFilter (k L : ℕ) (S Q : Finset V) : Finset V :=
  let P := playable G k S ((univ \ S) \ Q)
  if h : (P.filter (IsDefinite G S)).Nonempty then {(P.filter (IsDefinite G S)).min' h}
  else subsetFilter G S (betterFilterBy (betterCite G k L S P) P)

variable {G}

/-! ### The premise is Theorem 1 at the child -/

theorem betterOpen_eq (S : Finset V) (r q : V) :
    betterOpen G S r q = openCount G (cl G (insert r S)) q := by
  unfold betterOpen openCount newlyOpened
  rw [opened_cl]

theorem betterClose_eq (S : Finset V) (r q : V) :
    betterClose G S r q = closeCount G (cl G (insert r S)) q := by
  unfold betterClose closeCount newlyOpened
  rw [opened_cl]
  congr 1
  ext d
  simp only [mem_filter, mem_sdiff, mem_univ, true_and, cl, mem_finished]
  constructor
  · rintro ⟨-, hne, hsub⟩
    exact ⟨Finset.sdiff_nonempty.1 hne, hsub⟩
  · rintro ⟨hnot, hsub⟩
    exact ⟨fun hd => hnot fun x hx => mem_opened.2 ⟨d, hd, hx⟩, Finset.sdiff_nonempty.2 hnot,
      hsub⟩

/-- **Premise 4 is the definite-move premise for `q` at the child `cl(S ∪ {r})`**, and
premise 3 is `q`'s step cost after `S ∪ {r}`. -/
theorem isBetter_iff (k : ℕ) (S : Finset V) (r q : V) :
    IsBetter G k S r q ↔
      stepCost G (insert r S) q ≤ k ∧ IsDefinite G (cl G (insert r S)) q := by
  unfold IsBetter IsDefinite
  rw [betterOpen_eq, betterClose_eq]

/-- The repair implies the code's premise. -/
theorem IsRepairedBetter.isBetter {k : ℕ} {S : Finset V} {r q : V}
    (h : IsRepairedBetter G k S r q) : IsBetter G k S r q := by
  refine (isBetter_iff k S r q).2 ⟨h.1, ?_⟩
  by_cases hq : q ∈ cl G (insert r S)
  · unfold IsDefinite openCount newlyOpened
    rw [opened_cl, Finset.sdiff_eq_empty_iff_subset.2 (mem_finished.1 hq)]
    simp
  · exact h.2.isDefinite hq

/-- The repair covers every `q` opening at most one new stack at the child. -/
theorem isRepairedBetter_of_openCount_le_one {k : ℕ} {S : Finset V} {r q : V}
    (h3 : stepCost G (insert r S) q ≤ k) (h : betterOpen G S r q ≤ 1) :
    IsRepairedBetter G k S r q :=
  ⟨h3, isHereditarilyDefinite_of_openCount_le_one (by rwa [← betterOpen_eq])⟩

/-! ### The repaired rule is sound -/

theorem card_sdiff_insert_eq {U S : Finset V} {q r : V} (hq : q ∈ U) (hr : r ∈ U) (hqS : q ∉ S)
    (hrS : r ∉ S) : (U \ insert q S).card = (U \ insert r S).card := by
  rw [Finset.sdiff_insert, Finset.sdiff_insert, Finset.card_erase_of_mem (by simp [hq, hqS]),
    Finset.card_erase_of_mem (by simp [hr, hrS])]

/-- **The repaired better move is sound**: with the repaired premise (no playability hypothesis),
a solution from `cl(S ∪ {r})` gives one from `cl(S ∪ {q})`. -/
theorem solvable_cl_insert_of_repairedBetter {k : ℕ} {S : Finset V} {r q : V}
    (hrS : r ∉ S) (hqS : q ∉ S) (hb : IsRepairedBetter G k S r q)
    (hs : Solvable G k (cl G (insert r S))) : Solvable G k (cl G (insert q S)) := by
  set T := cl G (insert r S) with hT
  set Z := cl G (insert q S) with hZ
  -- The repaired Theorem 1 at the child `T`.
  have h1 : Solvable G k (cl G (insert q T)) := by
    by_cases hqT : q ∈ T
    · rw [Finset.insert_eq_of_mem hqT, hT, cl_cl]; exact hs
    · exact solvable_cl_insert_of_hereditarilyDefinite hb.2 hqT hs
  -- Both orders open the same stacks.
  have hO : opened G (insert r Z) = opened G (insert q (insert r S)) := by
    rw [opened_insert, hZ, opened_cl, opened_insert, opened_insert, opened_insert]
    exact Finset.union_left_comm _ _ _
  have hO' : opened G (insert q T) = opened G (insert q (insert r S)) := by
    simp only [hT, opened_insert, opened_cl]
  have hcl : cl G (insert r Z) = cl G (insert q T) := by
    unfold cl; rw [hO, hO']
  -- `r` second costs at most premise 3.
  have hcost : stepCost G Z r ≤ k := by
    refine le_trans ?_ hb.1
    unfold stepCost
    rw [hO]
    have hU := fun c (hc : c ∈ insert q (insert r S)) => subset_opened (G := G) _ hc
    calc (opened G (insert q (insert r S)) \ Z).card
        ≤ (opened G (insert q (insert r S)) \ insert q S).card :=
          Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl (subset_cl _))
      _ = (opened G (insert q (insert r S)) \ insert r S).card :=
          card_sdiff_insert_eq (hU q (by simp)) (hU r (by simp)) hqS hrS
  have hinv : (opened G (insert r Z) \ insert r Z).card ≤ k :=
    le_trans (Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl (Finset.subset_insert _ _)))
      hcost
  have h2 : Solvable G k (insert r Z) := (solvable_cl_iff hinv).1 (hcl ▸ h1)
  by_cases hrZ : r ∈ Z
  · rwa [Finset.insert_eq_of_mem hrZ] at h2
  · exact solvable_of_solvable_insert hrZ hcost h2

/-- The node invariant holds at the child of a playable move. -/
theorem card_opened_cl_insert_sdiff_le {k : ℕ} {S : Finset V} {r : V} (hrS : r ∉ S)
    (hr : stepCost G S r ≤ k) :
    (opened G (cl G (insert r S)) \ cl G (insert r S)).card ≤ k := by
  rw [opened_cl]
  exact le_trans (Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl (subset_cl _)))
    (le_trans (card_opened_insert_sdiff_lt hrS).le hr)

/-- The search's form: with `r` playable at `S`, `Sol_k(S·r) → Sol_k(S·q)`. -/
theorem searchSol_cl_insert_of_repairedBetter {k : ℕ} {S : Finset V} {r q : V}
    (hrS : r ∉ S) (hqS : q ∉ S) (hr : stepCost G S r ≤ k) (hb : IsRepairedBetter G k S r q)
    (hs : SearchSol G k (cl G (insert r S))) : SearchSol G k (cl G (insert q S)) := by
  have := searchSol_cl_of_solvable (G := G) _ _ le_rfl
    (solvable_cl_insert_of_repairedBetter hrS hqS hb
      (solvable_of_searchSol hs (card_opened_cl_insert_sdiff_le hrS hr)))
  rwa [cl_cl] at this

/-! ### Node soundness of the composition -/

/-- **A better pass is node-sound whenever each citation is**: the least member of `W` with a
solution is never dropped, since the customer it would cite is earlier and has one too. -/
theorem betterFilterBy_sound (B : V → V → Prop) [DecidableRel B] {k : ℕ} {S W : Finset V}
    (hB : ∀ r ∈ W, ∀ q ∈ W, B r q → SearchSol G k (cl G (insert r S)) →
      SearchSol G k (cl G (insert q S)))
    (h : ∃ c ∈ W, SearchSol G k (cl G (insert c S))) :
    ∃ c ∈ betterFilterBy B W, SearchSol G k (cl G (insert c S)) := by
  classical
  set A := W.filter (fun c => SearchSol G k (cl G (insert c S)))
  have hA : A.Nonempty := let ⟨c, hc, hs⟩ := h; ⟨c, mem_filter.2 ⟨hc, hs⟩⟩
  obtain ⟨hmW, hms⟩ := mem_filter.1 (A.min'_mem hA)
  refine ⟨A.min' hA, mem_filter.2 ⟨hmW, ?_⟩, hms⟩
  rintro ⟨q, hqW, hlt, hBq⟩
  have hqA : q ∈ A := mem_filter.2 ⟨hqW, hB _ hmW q hqW hBq hms⟩
  exact absurd (A.min'_le q hqA) (not_le.2 hlt)

/-- **The fixed order is node-sound** when the definite premise `D` and the citation relation
`B` are each sound at `S` on playable candidates. -/
theorem fullFilter_sound (D : V → Prop) [DecidablePred D] (B : Finset V → V → V → Prop)
    [∀ W, DecidableRel (B W)] {k : ℕ} {S Q : Finset V}
    (hD : ∀ q, q ∉ S → stepCost G S q ≤ k → D q → SearchSol G k S →
      SearchSol G k (cl G (insert q S)))
    (hB : ∀ W r q, r ∉ S → q ∉ S → stepCost G S r ≤ k → stepCost G S q ≤ k → B W r q →
      SearchSol G k (cl G (insert r S)) → SearchSol G k (cl G (insert q S)))
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) :
    ∃ c ∈ fullFilter G D B S (playable G k S ((univ \ S) \ Q)),
      SearchSol G k (cl G (insert c S)) := by
  unfold fullFilter
  split_ifs with h
  · refine ⟨_, mem_singleton_self _, ?_⟩
    obtain ⟨hmP, hmD⟩ := mem_filter.1 (min'_mem _ h)
    obtain ⟨hmK, hmk⟩ := mem_filter.1 hmP
    exact hD _ (mem_sdiff.1 (mem_sdiff.1 hmK).1).2 hmk hmD hs
  · have hP : ∀ c ∈ subsetFilter G S (playable G k S ((univ \ S) \ Q)),
        c ∉ S ∧ stepCost G S c ≤ k := fun c hc => by
      obtain ⟨hcK, hck⟩ := mem_filter.1 (subsetFilter_subset _ _ hc)
      exact ⟨(mem_sdiff.1 (mem_sdiff.1 hcK).1).2, hck⟩
    refine betterFilterBy_sound _ (fun r hr q hq hBrq hrs => ?_) (subsetFilter_sound hQ hs hS)
    exact hB _ r q (hP r hr).1 (hP q hq).1 (hP r hr).2 (hP q hq).2 hBrq hrs

/-- **With both repairs the composition `definite → subset → better` is node-sound** at every
node the search visits, for any limit `L` and any family `Q` of refuted old moves. -/
theorem repairedFullFilter_sound {k L : ℕ} {S Q : Finset V} (hk : (opened G S \ S).card ≤ k)
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) :
    ∃ c ∈ repairedFullFilter G k L S Q, SearchSol G k (cl G (insert c S)) :=
  @fullFilter_sound V _ _ G _ (IsHereditarilyDefinite G S) (Classical.decPred _)
    (fun W r q => withinLimit L W q ∧ IsRepairedBetter G k S r q) (fun _ => Classical.decRel _)
    k S Q (fun _ hq _ hD hs => searchSol_cl_insert_of_hereditarilyDefinite hD hq hk hs)
    (fun _ _ _ hr hq hrk _ hB hs => searchSol_cl_insert_of_repairedBetter hr hq hrk hB.2 hs)
    hQ hs hS

end

/-! ### The corrected rule is still unsound -/

/-- The states reachable from `{0}` in `cexGraph` within `6` stacks. -/
def bmFamily : Finset (Finset (Fin 14)) :=
  {{0}, {0, 2}, {0, 3}, {0, 4}, {0, 2, 3}, {0, 2, 4}, {0, 3, 4}, {0, 1, 2, 3}, {0, 1, 2, 4},
   {0, 1, 3, 4}, {0, 2, 3, 4}, {0, 3, 4, 7}, {0, 1, 2, 3, 4}, {0, 2, 3, 4, 5}, {0, 2, 3, 4, 6},
   {0, 2, 3, 4, 7}, {0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 6}}

set_option maxRecDepth 100000 in
theorem bmFamily_closed : ∀ A ∈ bmFamily, ∀ c, c ∉ A → stepCost cexGraph A c ≤ 6 →
    insert c A ∈ bmFamily := by
  decide +kernel

theorem bm_cl_zero : cl cexGraph (insert 0 (∅ : Finset (Fin 14))) = {0} := by decide

theorem bm_cl_two : cl cexGraph (insert 2 (∅ : Finset (Fin 14))) = {2} := by decide

theorem bm_not_searchSol_zero : ¬ SearchSol cexGraph 6 (cl cexGraph (insert 0 ∅)) := by
  intro h
  have hk : (opened cexGraph (cl cexGraph (insert 0 ∅)) \ cl cexGraph (insert 0 ∅)).card ≤ 6 := by
    rw [bm_cl_zero]; decide
  refine not_solvable_of_invariant bmFamily (by decide) bmFamily_closed ?_
    (solvable_of_searchSol h hk)
  rw [bm_cl_zero]; decide

theorem bm_searchSol_two : SearchSol cexGraph 6 (cl cexGraph (insert 2 ∅)) := by
  have := searchSol_cl_of_solvable (G := cexGraph) _ _ le_rfl cex_solvable
  rwa [← bm_cl_two, cl_cl] at this

/-- **Chu & Stuckey's Theorem 2 is false in its corrected form, the form the C runs.** At the
root of `cexGraph` with `k = 6` the definite move does not fire, `0` and `2` survive the subset
rule, `0 < 2`, and the corrected premise holds for `r = 2`, `q = 0`, so the code drops `2`
citing `0`; the repaired premise fails. A solution exists after `2` and none after `0`. -/
theorem betterMove_counterexample :
    let S : Finset (Fin 14) := ∅
    let P := playable cexGraph 6 S (univ \ S)
    ¬ (P.filter (IsDefinite cexGraph S)).Nonempty ∧
      (0 : Fin 14) ∈ subsetFilter cexGraph S P ∧ (2 : Fin 14) ∈ subsetFilter cexGraph S P ∧
      (0 : Fin 14) < 2 ∧ IsBetter cexGraph 6 S 2 0 ∧ ¬ IsRepairedBetter cexGraph 6 S 2 0 ∧
      (2 : Fin 14) ∉ codeFullFilter cexGraph 6 0 S ∅ ∧
      SearchSol cexGraph 6 (cl cexGraph (insert 2 S)) ∧
      ¬ SearchSol cexGraph 6 (cl cexGraph (insert 0 S)) := by
  intro S P
  refine ⟨by decide +kernel, by decide +kernel, by decide +kernel, by decide, by decide +kernel,
    ?_, by decide +kernel, bm_searchSol_two, bm_not_searchSol_zero⟩
  rintro ⟨-, h⟩
  have := h {2, 3, 4} (by rw [bm_cl_two]; decide) (by rw [bm_cl_two, cex_cl_insert]; decide)
    (by decide)
  rw [bm_cl_two, cex_cl_insert] at this
  revert this
  decide

/-- At the same node the filter still keeps a customer with a solution (`1`): the false link
does not by itself lose the node. -/
theorem betterMove_counterexample_node :
    (1 : Fin 14) ∈ codeFullFilter cexGraph 6 0 ∅ ∅ ∧
      SearchSol cexGraph 6 (cl cexGraph (insert 1 ∅)) := by
  refine ⟨by decide +kernel, ?_⟩
  have hsol : Solvable cexGraph 6 (insert 1 (∅ : Finset (Fin 14))) :=
    ⟨[2, 3, 4, 6, 12, 13, 0, 5, 7, 8, 9, 10, 11], by unfold IsClosingOrder; decide, by decide⟩
  exact searchSol_cl_of_solvable _ _ le_rfl hsol

/-! ### Bug A: the uncorrected close count -/

/-- The edges of the Bug A counterexample, found by `paper2/better_hunt.c` (`MODE=1`) on
random sparse graphs at 11–13 customers. -/
def bugAEdges : List (ℕ × ℕ) :=
  [(0, 1), (0, 2), (0, 3), (0, 5), (0, 8), (0, 10), (0, 11), (1, 3), (1, 4), (1, 10), (2, 3),
   (2, 7), (2, 10), (5, 8), (6, 7), (6, 9), (7, 9), (7, 10), (8, 10), (8, 11), (10, 11)]

def bugAGraph : SimpleGraph (Fin 12) := SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ bugAEdges

instance : DecidableRel bugAGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ bugAEdges ∨ (b.val, a.val) ∈ bugAEdges)))

/-- The states reachable from `{4}` within `4` stacks. -/
def bugAFamily : Finset (Finset (Fin 12)) :=
  {{4}, {1, 4}, {3, 4}, {4, 5}, {4, 6}, {4, 9}, {1, 3, 4}, {4, 6, 9}, {1, 2, 3, 4}, {4, 6, 7, 9}}

set_option maxRecDepth 100000 in
theorem bugAFamily_closed : ∀ A ∈ bugAFamily, ∀ c, c ∉ A → stepCost bugAGraph A c ≤ 4 →
    insert c A ∈ bugAFamily := by
  decide +kernel

theorem bugA_cl_four : cl bugAGraph (insert 4 (∅ : Finset (Fin 12))) = {4} := by decide

theorem bugA_cl_six : cl bugAGraph (insert 6 (∅ : Finset (Fin 12))) = {6, 9} := by decide

/-- **Bug A is unsound on its own**: at the root of `bugAGraph` with `k = 4`, `4 < 6`, both are
playable, the old premise holds for `r = 6`, `q = 4` and the corrected one does not; a
solution exists after `6` and none after `4`. -/
theorem bugA_counterexample :
    let S : Finset (Fin 12) := ∅
    (4 : Fin 12) < 6 ∧ stepCost bugAGraph S 4 ≤ 4 ∧ stepCost bugAGraph S 6 ≤ 4 ∧
      IsBetterOld bugAGraph 4 S 6 4 ∧ ¬ IsBetter bugAGraph 4 S 6 4 ∧
      SearchSol bugAGraph 4 (cl bugAGraph (insert 6 S)) ∧
      ¬ SearchSol bugAGraph 4 (cl bugAGraph (insert 4 S)) := by
  intro S
  refine ⟨by decide, by decide, by decide, by decide +kernel, by decide +kernel, ?_, ?_⟩
  · have hsol : Solvable bugAGraph 4 (cl bugAGraph (insert 6 S)) := by
      rw [bugA_cl_six]
      exact ⟨[7, 2, 3, 1, 4, 5, 0, 8, 10, 11], by unfold IsClosingOrder; decide, by decide⟩
    have := searchSol_cl_of_solvable _ _ le_rfl hsol
    rwa [cl_cl] at this
  · intro h
    have hk : (opened bugAGraph (cl bugAGraph (insert 4 S)) \
        cl bugAGraph (insert 4 S)).card ≤ 4 := by
      rw [bugA_cl_four]; decide
    refine not_solvable_of_invariant bugAFamily (by decide) bugAFamily_closed ?_
      (solvable_of_searchSol h hk)
    rw [bugA_cl_four]; decide

/-! ### Bug B: the cross-rule cycle -/

/-- The edges of the Bug B counterexample, the 8-customer node found by item 06
(`paper2/search_check.py`). -/
def bugBEdges : List (ℕ × ℕ) :=
  [(0, 1), (0, 3), (0, 7), (1, 3), (1, 4), (1, 5), (2, 3), (4, 5), (4, 7), (5, 6), (5, 7), (6, 7)]

def bugBGraph : SimpleGraph (Fin 8) := SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ bugBEdges

instance : DecidableRel bugBGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ bugBEdges ∨ (b.val, a.val) ∈ bugBEdges)))

theorem bugB_cl_six : cl bugBGraph (insert 6 ({2} : Finset (Fin 8))) = {2, 6} := by decide

theorem bugB_cl_three : cl bugBGraph (insert 3 ({2} : Finset (Fin 8))) = {2, 3} := by decide

/-- **Bug B loses the last solution at a node, with every premise the corrected one.** At the
free-closed state `{2}` of `bugBGraph` with `k = 4`, the invariant, and no old moves, the old
order keeps `{6}` alone: the better move drops `3` citing `0`, then the subset rule drops `0`
citing `3`. A solution exists from `{2}` and none from `{2}·6`. The fixed order keeps
`{3, 6}`, and `{2}·3` has a solution. -/
theorem bugB_counterexample :
    let S : Finset (Fin 8) := {2}
    cl bugBGraph S = S ∧ (opened bugBGraph S \ S).card ≤ 4 ∧
      playable bugBGraph 4 S ((univ \ S) \ (∅ : Finset (Fin 8))) = {0, 3, 6} ∧
      IsBetter bugBGraph 4 S 3 0 ∧ Dominates bugBGraph S 3 0 ∧
      oldOrderFilter bugBGraph 4 0 S ∅ = {6} ∧ codeFullFilter bugBGraph 4 0 S ∅ = {3, 6} ∧
      SearchSol bugBGraph 4 S ∧ SearchSol bugBGraph 4 (cl bugBGraph (insert 3 S)) ∧
      ¬ SearchSol bugBGraph 4 (cl bugBGraph (insert 6 S)) := by
  intro S
  have hcl : cl bugBGraph S = S := by decide
  refine ⟨hcl, by decide, by decide +kernel, by decide +kernel, by decide +kernel,
    by decide +kernel, by decide +kernel, ?_, ?_, ?_⟩
  · have hsol : Solvable bugBGraph 4 S :=
      ⟨[0, 3, 1, 4, 5, 6, 7], by unfold IsClosingOrder; decide, by decide⟩
    have := searchSol_cl_of_solvable _ _ le_rfl hsol
    rwa [hcl] at this
  · have hsol : Solvable bugBGraph 4 (cl bugBGraph (insert 3 S)) := by
      rw [bugB_cl_three]
      exact ⟨[0, 1, 4, 5, 6, 7], by unfold IsClosingOrder; decide, by decide⟩
    have := searchSol_cl_of_solvable _ _ le_rfl hsol
    rwa [cl_cl] at this
  · intro h
    have hk : (opened bugBGraph (cl bugBGraph (insert 6 S)) \
        cl bugBGraph (insert 6 S)).card ≤ 4 := by
      rw [bugB_cl_six]; decide
    refine not_solvable_of_invariant {{2, 6}} (by decide) (by decide +kernel) ?_
      (solvable_of_searchSol h hk)
    rw [bugB_cl_six]; exact mem_singleton_self _

end Search

end MOSPFormalization
