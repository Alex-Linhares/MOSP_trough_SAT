/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The subset rule (Chu & Stuckey 2009, §2), with its index tie-break

Loop0006 item 09, `paper2/search_soundness.md` §2.3 and §4.3. Source: Chu & Stuckey,
*Minimizing the maximum number of open stacks by customer search*, CP 2009, §2 (preprint p. 5):

> if `o(cᵢ, S) ⊆ o(cⱼ, S)` and `i < j`, then clearly, we can always play `i` before `j` rather
> than playing `j` immediately, since closing `j` will close `i` in any case. Hence move `j`
> can be removed.

The code (`satisfiability/customer_search.py:417–428`, `customer_search.c:151–164`,
`subset_pass`) drops a playable candidate `r` when some `d` among **all** customers not yet
closed (candidates, old moves `Q`, anything but `r`) has `o(d, S) ⊆ o(r, S)` with the
inclusion strict or `d < r`; if every candidate would go, it keeps them all. It runs only
when the definite move did not fire, before the better move.

## Definitions

* `Dominates G S d r` — `d ≠ r`, `o(d, S) ⊆ o(r, S)`, and `o(d, S) ≠ o(r, S) ∨ d < r`;
* `IsSubsetDominated G S r` — some `d ∉ S` dominates `r`;
* `playable G k S K` — the members of `K` with step cost `≤ k` (the cost cut);
* `subsetKept G S P`, `subsetFilter G S P` — the undominated members of `P`, or `P` itself
  when there are none (the fallback);
* `WeakDominates`, `weakSubsetFilter` — the same without the tie-break (for the
  counterexample);
* `definiteThenSubset G D S P` — the filter in the code's order: the least member of `P`
  meeting the definite-move premise `D`, alone, if there is one; else the subset filter.
  `codeFilter` takes `D` to be the code's premise `IsDefinite`, `repairedFilter` the repair
  `IsHereditarilyDefinite` of `DefiniteMove.lean`; the candidates are `(V ∖ S) ∖ Q`.

## What is proved

* `searchSol_cl_insert_of_newlyOpened_subset` — **the rule's covering**: if
  `o(d, S) ⊆ o(r, S)` and `r` is playable at `S`, then `Sol_k(S·r) → Sol_k(S·d)`. No
  hypothesis on `S` (free-closed or not, invariant or not), no `d ∉ S`, and no tie-break:
  closing `r` finishes `d` (`mem_cl_insert_of_newlyOpened_subset`), `S·d ⊆ S·r`
  (`cl_insert_subset_of_newlyOpened_subset`), and closing `r` from `S·d` costs no more than
  from `S` and lands on `S·r` (`cl_insert_cl_insert_of_newlyOpened_subset`). `d` is itself
  playable (`stepCost_le_of_newlyOpened_subset`). Unlike the definite move (item 08), the
  paper's argument is correct as it stands.
* `not_dominates_self`, `Dominates.trans` — the tie-break makes dominance a strict order, so
  no cycle is possible (`reports/better_move_bug.md` §7's Bug B needs a second rule).
  `exists_undominated`: every `r ∉ S` has an undominated `m ∉ S` with `o(m, S) ⊆ o(r, S)`,
  the least by `(|o(m, S)|, m)`.
* `subsetFilter_sound` — **node soundness of the rule on its own**: at any `S ≠ V`, if every
  old move `q ∈ Q` is refuted (`¬ Sol_k(S·q)`) and `Sol_k(S)`, then the subset filter of the
  playable candidates `(V ∖ S) ∖ Q` keeps some `c` with `Sol_k(S·c)`. `Q = ∅` is the rule
  without old move. On the way, `subsetKept_nonempty`: when a solution exists the fallback
  never fires.
* `definiteThenSubset_sound` — **after the definite move**: for any premise `D` that is
  sound at `S` (`D q`, `q` playable, `Sol_k(S)` give `Sol_k(S·q)`), the composition
  `definite → subset` is node-sound. `repairedFilter_sound`: with the repaired premise, at a
  node with the invariant `|O(S) ∖ S| ≤ k`, it is.
* `codeFilter_counterexample` — with the code's premise it is not: on `cexGraph` at
  `S = {2}`, `k = 6`, `Q = ∅`, the composition keeps `{0}` alone and `Sol_k(S)` holds while
  `Sol_k(S·0)` fails. The subset rule never runs there; the loss is the definite move's
  (item 08), which the composition inherits.
* `noTieBreak_counterexample` — **the tie-break is needed for soundness**, not only for
  acyclicity: without it (`WeakDominates`, `weakSubsetFilter`), on a 7-customer graph
  (`tieGraph`) at `S = {2}`, `k = 3`, the twins `0` and `3` (equal new stacks) dominate each
  other and both go, the filter keeps `{5}` alone, and `Sol_k(S)` holds while `Sol_k(S·5)`
  fails. The fallback does not save it because `5` survives. The paper's own form (`d < r`
  required even for a strict inclusion) is sound by the same covering; it is checked, not
  stated here.

## Checks

`python -m paper2.search_check --subset` (`paper2/search_check.py`) transcribes these
definitions and checks every statement by brute force; see `paper2/search_soundness.md` §4.3.
-/

import MOSPFormalization.Search.DefiniteMove

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

section

variable {V : Type*} [Fintype V] [LinearOrder V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Definitions -/

/-- `d` dominates `r` at `S` in the subset rule's sense, with the code's index tie-break. -/
def Dominates (S : Finset V) (d r : V) : Prop :=
  d ≠ r ∧ newlyOpened G S d ⊆ newlyOpened G S r ∧
    (newlyOpened G S d ≠ newlyOpened G S r ∨ d < r)

instance (S : Finset V) (d r : V) : Decidable (Dominates G S d r) := by
  unfold Dominates; infer_instance

/-- Some customer not yet closed dominates `r` (the code ranges `d` over `R(S)`, which at a
free-closed state is `V ∖ S`). -/
def IsSubsetDominated (S : Finset V) (r : V) : Prop := ∃ d ∈ univ \ S, Dominates G S d r

instance (S : Finset V) (r : V) : Decidable (IsSubsetDominated G S r) := by
  unfold IsSubsetDominated; infer_instance

/-- The cost cut: the members of `K` playable at `S`. -/
def playable (k : ℕ) (S K : Finset V) : Finset V := K.filter (fun c => stepCost G S c ≤ k)

/-- The playable candidates the subset rule keeps. -/
def subsetKept (S P : Finset V) : Finset V := P.filter (fun r => ¬ IsSubsetDominated G S r)

/-- The subset rule with its fallback: if every candidate would go, all are kept. -/
def subsetFilter (S P : Finset V) : Finset V :=
  if subsetKept G S P = ∅ then P else subsetKept G S P

/-- The filter in the code's order, `definite_move → subset_rule`: the least candidate meeting
the definite-move premise `D`, alone, if there is one; otherwise the subset filter. -/
def definiteThenSubset (D : V → Prop) [DecidablePred D] (S P : Finset V) : Finset V :=
  if h : (P.filter D).Nonempty then {(P.filter D).min' h} else subsetFilter G S P

/-- The code's filter (definite move with `open ≤ close`, then the subset rule) at the node
`(S, Q)`: candidates `(V ∖ S) ∖ Q`, cost cut, filter. -/
def codeFilter (k : ℕ) (S Q : Finset V) : Finset V :=
  definiteThenSubset G (IsDefinite G S) S (playable G k S ((univ \ S) \ Q))

/-- The same filter with the repaired definite move of `DefiniteMove.lean`. -/
noncomputable def repairedFilter (k : ℕ) (S Q : Finset V) : Finset V :=
  @definiteThenSubset V _ _ G _ (IsHereditarilyDefinite G S) (Classical.decPred _) S
    (playable G k S ((univ \ S) \ Q))

/-- Domination **without** the index tie-break: `o(d, S) ⊆ o(r, S)` and `d ≠ r` only, so two
customers with equal new stacks dominate each other. -/
def WeakDominates (S : Finset V) (d r : V) : Prop :=
  d ≠ r ∧ newlyOpened G S d ⊆ newlyOpened G S r

instance (S : Finset V) (d r : V) : Decidable (WeakDominates G S d r) := by
  unfold WeakDominates; infer_instance

/-- The subset filter without the tie-break, with the same fallback. -/
def weakSubsetFilter (S P : Finset V) : Finset V :=
  let kept := P.filter (fun r => ¬ ∃ d ∈ univ \ S, WeakDominates G S d r)
  if kept = ∅ then P else kept

variable {G}

/-! ### The covering -/

/-- Closing `r` opens everything `d` needs. -/
theorem nbhd_subset_opened_insert_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) : nbhd G d ⊆ opened G (insert r S) := by
  intro x hx
  rw [opened_insert]
  by_cases hxS : x ∈ opened G S
  · exact mem_union_right _ hxS
  · exact mem_union_left _ (mem_sdiff.1 (h (mem_sdiff.2 ⟨hx, hxS⟩))).1

/-- Closing `r` finishes `d`. -/
theorem mem_cl_insert_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) : d ∈ cl G (insert r S) :=
  mem_finished.2 (nbhd_subset_opened_insert_of_newlyOpened_subset h)

theorem opened_insert_subset_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) :
    opened G (insert d S) ⊆ opened G (insert r S) := by
  rw [opened_insert d]
  exact union_subset (nbhd_subset_opened_insert_of_newlyOpened_subset h)
    (opened_mono (subset_insert _ _))

/-- `S·d ⊆ S·r`. -/
theorem cl_insert_subset_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) : cl G (insert d S) ⊆ cl G (insert r S) :=
  fun _ hc => mem_finished.2 ((mem_finished.1 hc).trans
    (opened_insert_subset_of_newlyOpened_subset h))

/-- The dominator is no dearer than the dominated move, so it is playable too. -/
theorem stepCost_le_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) : stepCost G S d ≤ stepCost G S r :=
  card_le_card (sdiff_subset_sdiff (opened_insert_subset_of_newlyOpened_subset h) le_rfl)

/-- Closing `r` after `S·d` opens exactly what closing `r` after `S` does. -/
theorem opened_insert_cl_insert_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) :
    opened G (insert r (cl G (insert d S))) = opened G (insert r S) := by
  apply le_antisymm
  · rw [opened_insert r (cl G _), opened_cl]
    refine union_subset ?_ (opened_insert_subset_of_newlyOpened_subset h)
    rw [opened_insert]
    exact subset_union_left
  · exact opened_mono (insert_subset_insert _ (subset_cl_insert S d))

/-- `(S·d)·r = S·r`. -/
theorem cl_insert_cl_insert_of_newlyOpened_subset {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) :
    cl G (insert r (cl G (insert d S))) = cl G (insert r S) := by
  show finished G (opened G _) = finished G (opened G _)
  rw [opened_insert_cl_insert_of_newlyOpened_subset h]

/-- **The subset rule's covering**: if `o(d, S) ⊆ o(r, S)` and `r` is playable, a solution
through `r` gives one through `d`. -/
theorem searchSol_cl_insert_of_newlyOpened_subset {k : ℕ} {S : Finset V} {d r : V}
    (h : newlyOpened G S d ⊆ newlyOpened G S r) (hr : stepCost G S r ≤ k)
    (hs : SearchSol G k (cl G (insert r S))) : SearchSol G k (cl G (insert d S)) := by
  have hX := cl_insert_cl_insert_of_newlyOpened_subset h
  by_cases hrX : r ∈ cl G (insert d S)
  · rw [insert_eq_of_mem hrX, cl_cl] at hX
    rwa [hX]
  · refine SearchSol.step r hrX ?_ (by rw [hX]; exact hs)
    refine le_trans (card_le_card ?_) hr
    exact sdiff_subset_sdiff (le_of_eq (opened_insert_cl_insert_of_newlyOpened_subset h))
      (subset_cl_insert S d)

/-! ### Dominance is a strict order -/

theorem not_dominates_self {S : Finset V} (d : V) : ¬ Dominates G S d d := fun h => h.1 rfl

theorem Dominates.trans {S : Finset V} {a b c : V} (h1 : Dominates G S a b)
    (h2 : Dominates G S b c) : Dominates G S a c := by
  obtain ⟨-, s1, t1⟩ := h1
  obtain ⟨-, s2, t2⟩ := h2
  by_cases he : newlyOpened G S a = newlyOpened G S c
  · have e1 : newlyOpened G S a = newlyOpened G S b :=
      subset_antisymm s1 (by rw [he]; exact s2)
    have e2 : newlyOpened G S b = newlyOpened G S c := by rw [← e1]; exact he
    have lab : a < b := t1.resolve_left (not_not.2 e1)
    have lbc : b < c := t2.resolve_left (not_not.2 e2)
    exact ⟨(lab.trans lbc).ne, s1.trans s2, Or.inr (lab.trans lbc)⟩
  · exact ⟨fun hac => he (by rw [hac]), s1.trans s2, Or.inl he⟩

/-- Every customer not yet closed has an undominated one below it: the least by
`(|o(m, S)|, m)` among those with `o(m, S) ⊆ o(r, S)`. -/
theorem exists_undominated (S : Finset V) {r : V} (hr : r ∉ S) :
    ∃ m, m ∉ S ∧ newlyOpened G S m ⊆ newlyOpened G S r ∧ ¬ IsSubsetDominated G S m := by
  set A := (univ \ S).filter (fun d => newlyOpened G S d ⊆ newlyOpened G S r) with hAdef
  have hA : A.Nonempty := ⟨r, mem_filter.2 ⟨by simp [hr], le_rfl⟩⟩
  obtain ⟨m0, hm0A, hmin⟩ := A.exists_min_image (openCount G S) hA
  set B := A.filter (fun d => openCount G S d = openCount G S m0) with hBdef
  have hB : B.Nonempty := ⟨m0, mem_filter.2 ⟨hm0A, rfl⟩⟩
  have hmB : B.min' hB ∈ B := B.min'_mem hB
  obtain ⟨hmA, hmc⟩ := mem_filter.1 hmB
  obtain ⟨hmS, hmr⟩ := mem_filter.1 hmA
  refine ⟨B.min' hB, (mem_sdiff.1 hmS).2, hmr, ?_⟩
  rintro ⟨d, hdS, hdm, hsub, hor⟩
  have hdA : d ∈ A := mem_filter.2 ⟨hdS, hsub.trans hmr⟩
  have hle := hmin d hdA
  have heq : newlyOpened G S d = newlyOpened G S (B.min' hB) := by
    refine eq_of_subset_of_card_le hsub ?_
    unfold openCount at hle hmc
    omega
  have hdB : d ∈ B := mem_filter.2 ⟨hdA, by unfold openCount at hmc ⊢; rw [heq]; exact hmc⟩
  rcases hor with h | h
  · exact h heq
  · exact absurd h (not_lt.2 (B.min'_le d hdB))

/-! ### Node soundness -/

/-- A solution from a state other than `V` starts with a playable move. -/
theorem SearchSol.exists_move {k : ℕ} {S : Finset V} (hs : SearchSol G k S) (hS : S ≠ univ) :
    ∃ c, c ∉ S ∧ stepCost G S c ≤ k ∧ SearchSol G k (cl G (insert c S)) := by
  cases hs with
  | done h => exact absurd h hS
  | step c hc hk hs => exact ⟨c, hc, hk, hs⟩

/-- Some undominated playable candidate carries a solution. -/
theorem exists_mem_subsetKept {k : ℕ} {S Q : Finset V}
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) :
    ∃ m ∈ subsetKept G S (playable G k S ((univ \ S) \ Q)),
      SearchSol G k (cl G (insert m S)) := by
  obtain ⟨c, hcS, hck, hcs⟩ := hs.exists_move hS
  obtain ⟨m, hmS, hmc, hmnd⟩ := exists_undominated (G := G) S hcS
  have hms := searchSol_cl_insert_of_newlyOpened_subset hmc hck hcs
  have hmQ : m ∉ Q := fun h => hQ m h hms
  refine ⟨m, mem_filter.2 ⟨mem_filter.2 ⟨?_, (stepCost_le_of_newlyOpened_subset hmc).trans hck⟩,
    hmnd⟩, hms⟩
  simp [hmS, hmQ]

/-- When a solution exists the fallback never fires. -/
theorem subsetKept_nonempty {k : ℕ} {S Q : Finset V}
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) : (subsetKept G S (playable G k S ((univ \ S) \ Q))).Nonempty :=
  let ⟨m, hm, _⟩ := exists_mem_subsetKept hQ hs hS
  ⟨m, hm⟩

theorem subsetFilter_subset (S P : Finset V) : subsetFilter G S P ⊆ P := by
  unfold subsetFilter
  split_ifs
  · exact le_rfl
  · exact filter_subset _ _

/-- **The subset rule is node-sound on its own**: with every old move refuted, a solution from
`S` survives the rule. -/
theorem subsetFilter_sound {k : ℕ} {S Q : Finset V}
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) :
    ∃ c ∈ subsetFilter G S (playable G k S ((univ \ S) \ Q)),
      SearchSol G k (cl G (insert c S)) := by
  obtain ⟨m, hm, hms⟩ := exists_mem_subsetKept hQ hs hS
  refine ⟨m, ?_, hms⟩
  unfold subsetFilter
  split_ifs with h0
  · exact absurd h0 (ne_empty_of_mem hm)
  · exact hm

/-- **After the definite move**: for any definite-move premise `D` sound at `S`, the filter
`definite → subset` is node-sound. -/
theorem definiteThenSubset_sound (D : V → Prop) [DecidablePred D] {k : ℕ} {S Q : Finset V}
    (hD : ∀ q, q ∉ S → stepCost G S q ≤ k → D q → SearchSol G k S →
      SearchSol G k (cl G (insert q S)))
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) :
    ∃ c ∈ definiteThenSubset G D S (playable G k S ((univ \ S) \ Q)),
      SearchSol G k (cl G (insert c S)) := by
  unfold definiteThenSubset
  split_ifs with h
  · refine ⟨_, mem_singleton_self _, ?_⟩
    obtain ⟨hmP, hmD⟩ := mem_filter.1 (min'_mem _ h)
    obtain ⟨hmK, hmk⟩ := mem_filter.1 hmP
    exact hD _ (mem_sdiff.1 (mem_sdiff.1 hmK).1).2 hmk hmD hs
  · exact subsetFilter_sound hQ hs hS

/-- With the repaired definite move the composition is node-sound at every node the search
visits (the invariant `|O(S) ∖ S| ≤ k`). -/
theorem repairedFilter_sound {k : ℕ} {S Q : Finset V} (hk : (opened G S \ S).card ≤ k)
    (hQ : ∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) (hs : SearchSol G k S)
    (hS : S ≠ univ) :
    ∃ c ∈ repairedFilter G k S Q, SearchSol G k (cl G (insert c S)) :=
  @definiteThenSubset_sound V _ _ G _ (IsHereditarilyDefinite G S) (Classical.decPred _) k S Q
    (fun _ hq _ hD hs => searchSol_cl_insert_of_hereditarilyDefinite hD hq hk hs) hQ hs hS

end

/-! ### With the code's definite move the composition is not sound -/

/-- **The code's composition `definite → subset` loses the last solution** on the definite
move's counterexample: at the free-closed state `{2}` with `k = 6`, the invariant, and no old
moves, the filter keeps `{0}` alone, a solution exists from `{2}`, and none from its child. -/
theorem codeFilter_counterexample :
    let S : Finset (Fin 14) := {2}
    cl cexGraph S = S ∧ (opened cexGraph S \ S).card ≤ 6 ∧
      codeFilter cexGraph 6 S ∅ = {0} ∧ SearchSol cexGraph 6 S ∧
      ¬ SearchSol cexGraph 6 (cl cexGraph (insert 0 S)) := by
  intro S
  obtain ⟨hcl, hinv, -, -, -, -, -, hs, -, hns⟩ := definiteMove_counterexample
  exact ⟨hcl, hinv, by decide +kernel, hs, hns⟩

/-! ### Without the tie-break the rule is not sound -/

/-- The edges of the tie-break counterexample, found by random search with the tie-break
removed (`paper2/search_check.py`, `SUBSET_TIE_CEX`). -/
def tieEdges : List (ℕ × ℕ) :=
  [(0, 2), (0, 3), (0, 6), (1, 4), (1, 6), (3, 6), (4, 5), (4, 6)]

/-- A 7-customer graph on which the subset rule without its tie-break loses the last
solution: at `{2}`, customers `0` and `3` have the same new stacks `{3, 6}`. -/
def tieGraph : SimpleGraph (Fin 7) := SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ tieEdges

instance : DecidableRel tieGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ tieEdges ∨ (b.val, a.val) ∈ tieEdges)))

theorem tie_cl_insert : cl tieGraph (insert 5 ({2} : Finset (Fin 7))) = {2, 5} := by decide

theorem tie_solvable : Solvable tieGraph 3 ({2} : Finset (Fin 7)) :=
  ⟨[0, 3, 1, 4, 5, 6], by unfold IsClosingOrder; decide, by decide⟩

/-- **The index tie-break is needed for soundness, not only for acyclicity.** At the
free-closed state `{2}` with `k = 3` and the invariant, the twins `0` and `3` dominate each
other without the tie-break and both go; the rule keeps `{5}` alone, a solution exists from
`{2}` and none from `{2}·5`. With the tie-break only `3` goes and the filter keeps `{0, 5}`. -/
theorem noTieBreak_counterexample :
    let S : Finset (Fin 7) := {2}
    cl tieGraph S = S ∧ (opened tieGraph S \ S).card ≤ 3 ∧
      playable tieGraph 3 S (univ \ S) = {0, 3, 5} ∧
      weakSubsetFilter tieGraph S (playable tieGraph 3 S (univ \ S)) = {5} ∧
      subsetFilter tieGraph S (playable tieGraph 3 S (univ \ S)) = {0, 5} ∧
      SearchSol tieGraph 3 S ∧ ¬ SearchSol tieGraph 3 (cl tieGraph (insert 5 S)) := by
  intro S
  have hcl : cl tieGraph S = S := by decide
  refine ⟨hcl, by decide, by decide +kernel, by decide +kernel, by decide +kernel, ?_, ?_⟩
  · have := searchSol_cl_of_solvable (G := tieGraph) _ S le_rfl tie_solvable
    rwa [hcl] at this
  · intro h
    have hk : (opened tieGraph (cl tieGraph (insert 5 S)) \ cl tieGraph (insert 5 S)).card ≤ 3 := by
      rw [tie_cl_insert]; decide
    refine not_solvable_of_invariant {{2, 5}} (by decide) (by decide +kernel) ?_
      (solvable_of_searchSol h hk)
    rw [tie_cl_insert]; exact mem_singleton_self _

end Search

end MOSPFormalization
