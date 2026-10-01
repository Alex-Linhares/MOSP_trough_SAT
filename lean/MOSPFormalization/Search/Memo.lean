/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The memo and the old move (Chu & Stuckey 2009, Theorem 3), together

Loop0006 item 11, `paper2/search_soundness.md` §2.6, §2.7 and §4.5. Source: Chu & Stuckey,
*Minimizing the maximum number of open stacks by customer search*, CP 2009, §3.3
(preprint p. 7):

> **Theorem 3.** Suppose that `S′ = [s₁, …, s_m, q, s_{m+1}, …, s_n]` is playable, then if
> `U′ = S ++ [q] ++ R` is a solution then `U = S′ ++ R` is a solution.

and "if … at some ancestor node, the `q` branch has been searched and `U` is playable, then
`q` can immediately be pruned". The code keeps the set `Q` (`seen`) of such `q`: a child `c`
of a node `(S, Q)` inherits `q ∈ seen` iff `|(O(S) ∪ N[q] ∪ N[c]) ∖ (S ∪ {q})| ≤ k`, which is
`stepCost G (insert q S) c ≤ k` (`customer_search.py:350–363`, `customer_search.c:401–412`),
and a child whose subtree completed with `false` joins `seen` for its later siblings. The memo
records the free-closed set of every node whose loop completed with `false`
(`customer_search.py:375–379`, `customer_search.c:491`) and answers `false` at any later node
with that closed set.

## What is proved

* **The old move, one step.** `searchSol_reinsert`: if `stepCost G (insert q S) c ≤ k` (the
  inheritance test), then `Sol_k(cl(q · cl(c · S))) → Sol_k(cl(q · S))`, for every set `S`,
  with no invariant. Reinserting `q` before `c` keeps the path playable; both routes end at
  `cl(S ∪ {q, c})` (`cl_insert_cl_insert_comm`), and if `q` already made `c` free the step
  vanishes. `searchSol_reinsert_path` iterates it along any path whose every step passes the
  test (`Inherits`), and `not_searchSol_of_oldMove` is the rule: if the `q` branch at the
  ancestor `A` has no solution, neither has `q` at the end of the path. This is Theorem 3 in
  the form the search uses it; the free moves of the intervening nodes are absorbed by `cl`.
  The test is needed: `reinsert_needs_test` is a 5-vertex path on which the lemma fails
  without it.
* **The memo key.** `solvable_iff_of_cl_eq`: two sets of closed customers with the same free
  closure are equally solvable (under the node invariant at each), so a state refuted once is
  refuted whatever path reached it. `SearchSol` is a predicate on sets.
* **Old move and the memo together are sound** (`Exec.sound`). `Exec G k F M S Q o M′` is a
  big-step semantics of the search's `false` answers, with the filter `F` abstract: a memo hit
  (step 2); a node (steps 3–8) that intersects `Q` with the remaining customers, enumerates
  the filter's output in any order, runs each child with *any* subset of the inherited old
  moves (so old move off is the empty subset), adds each refuted child to `seen`, and records
  its state in the memo or not (memo off, or full). If `F` is node-sound and returns playable
  customers, then from a genuine memo and genuine old moves every run leaves a genuine memo,
  and every `false` answer is a genuine `¬ Sol_k(S)`. The proof is by induction on the run,
  which is the order in which subtrees complete: each `seen` entry is a completed refutation,
  so each inherited old move is genuinely refuted by `searchSol_reinsert`, so each recorded
  state is genuinely refuted. `exec_root_sound`: a run from the root refutes `Solvable G k ∅`.
  `exec_repairedFullFilter_sound` instantiates `F` with `repairedFullFilter`
  (`BetterMove.lean`): the search with free moves, memo, old move and the repaired
  `definite → subset → better` filter, in the code's order, answers `false` only if
  `¬ Solvable G k ∅`.
* **Why the Python refuses the combination, and why that reason is not a soundness one.**
  The Python drops the memo under old move (`customer_search.py:48–55, 217–222`): "a failure
  reached with old-move pruning depends on which branches an ancestor had searched … and
  recording it against `S` alone could refute a state that some other path would not".
  `exec_fake_oldMove` shows the part that is true: a run of a node, taken *on its own*, with an
  old move that is not refuted, refutes a solvable state and records it. What makes the code
  sound is the hypothesis of `Exec.sound` — every old move is a refutation completed earlier
  in the same run — which is a property of the run, not of the node. So the combination is
  sound; what is lost is local checkability of a memo entry (the certificate checker's reason,
  `learning/search_certificate.py:526–528`), not soundness.

## Checks

`python -m paper2.search_check --memo` (`paper2/search_check.py`) checks every statement here
by brute force, and runs the search with old move and the memo instrumented with `Exec.sound`'s
invariant; see `paper2/search_soundness.md` §4.5.
-/

import MOSPFormalization.Search.BetterMove

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

section Reinsert

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-! ### Closures commute -/

theorem opened_insert_cl (T : Finset V) (c : V) :
    opened G (insert c (cl G T)) = opened G (insert c T) := by
  rw [opened_insert, opened_insert, opened_cl]

/-- Closing `c` after the free closure of `T` is closing it after `T`. -/
theorem cl_insert_cl (T : Finset V) (c : V) : cl G (insert c (cl G T)) = cl G (insert c T) := by
  show finished G (opened G (insert c (cl G T))) = finished G (opened G (insert c T))
  rw [opened_insert_cl]

/-- The two routes to `cl(S ∪ {q, c})`. -/
theorem cl_insert_cl_insert_comm (S : Finset V) (q c : V) :
    cl G (insert q (cl G (insert c S))) = cl G (insert c (cl G (insert q S))) := by
  rw [cl_insert_cl, cl_insert_cl, Finset.insert_comm]

/-- A customer already finished at `X` adds nothing to its closure. -/
theorem cl_insert_eq_of_mem_cl {X : Finset V} {c : V} (hc : c ∈ cl G X) :
    cl G (insert c X) = cl G X := by
  show finished G (opened G (insert c X)) = finished G (opened G X)
  rw [opened_insert, Finset.union_eq_right.2 (mem_finished.1 hc)]

/-- Free-closing first never makes a step dearer. -/
theorem stepCost_cl_le (T : Finset V) (c : V) : stepCost G (cl G T) c ≤ stepCost G T c := by
  unfold stepCost
  rw [opened_insert_cl]
  exact card_le_card (sdiff_subset_sdiff le_rfl (subset_cl T))

/-- The node invariant holds at the child of a playable move (as `BetterMove.lean`'s
`card_opened_cl_insert_sdiff_le`, without the order on customers). -/
theorem card_opened_cl_insert_sdiff_le_of_playable {k : ℕ} {S : Finset V} {r : V} (hrS : r ∉ S)
    (hr : stepCost G S r ≤ k) :
    (opened G (cl G (insert r S)) \ cl G (insert r S)).card ≤ k := by
  rw [opened_cl]
  exact le_trans (Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl (subset_cl _)))
    (le_trans (card_opened_insert_sdiff_lt hrS).le hr)

/-! ### The old move -/

/-- **The old move, one step** (Chu & Stuckey Theorem 3, as the code's inheritance test uses
it). If reinserting `q` before `c` keeps `c` playable, a solution from `q` after the child
`cl(c · S)` gives a solution from `q` at `S`. -/
theorem searchSol_reinsert {k : ℕ} {S : Finset V} {q c : V}
    (htest : stepCost G (insert q S) c ≤ k)
    (h : SearchSol G k (cl G (insert q (cl G (insert c S))))) :
    SearchSol G k (cl G (insert q S)) := by
  rw [cl_insert_cl_insert_comm] at h
  by_cases hc : c ∈ cl G (insert q S)
  · rwa [cl_insert_eq_of_mem_cl (by rwa [cl_cl]), cl_cl] at h
  · exact SearchSol.step c hc ((stepCost_cl_le _ _).trans htest) h

variable (G)

/-- The state reached from `A` by the moves `l`, each followed by its free moves. -/
def pathEnd : Finset V → List V → Finset V
  | A, [] => A
  | A, a :: l => pathEnd (cl G (insert a A)) l

/-- Every move of `l` from `A` passes the inheritance test for `q`. -/
def Inherits (k : ℕ) (q : V) : Finset V → List V → Prop
  | _, [] => True
  | A, a :: l => stepCost G (insert q A) a ≤ k ∧ Inherits k q (cl G (insert a A)) l

variable {G}

/-- The old move along a path: `q` reinserted at the ancestor `A`. -/
theorem searchSol_reinsert_path {k : ℕ} {q : V} :
    ∀ (l : List V) (A : Finset V), Inherits G k q A l →
      SearchSol G k (cl G (insert q (pathEnd G A l))) → SearchSol G k (cl G (insert q A))
  | [], _, _, h => h
  | _ :: l, _, ⟨ha, hl⟩, h => searchSol_reinsert ha (searchSol_reinsert_path l _ hl h)

/-- **The old-move rule**: if the `q` branch at the ancestor `A` has no solution and every move
since passed the inheritance test, `q` has no solution at the current node. -/
theorem not_searchSol_of_oldMove {k : ℕ} {q : V} {A : Finset V} {l : List V}
    (hA : ¬ SearchSol G k (cl G (insert q A))) (hl : Inherits G k q A l) :
    ¬ SearchSol G k (cl G (insert q (pathEnd G A l))) :=
  fun h => hA (searchSol_reinsert_path l A hl h)

/-! ### The memo key -/

/-- **The memo may key on the closed set.** Two sets of closed customers with the same free
closure, each under the node invariant, are equally solvable: a state refuted once is refuted
whatever path reached it. -/
theorem solvable_iff_of_cl_eq {k : ℕ} {T T' : Finset V} (hT : (opened G T \ T).card ≤ k)
    (hT' : (opened G T' \ T').card ≤ k) (h : cl G T = cl G T') :
    Solvable G k T ↔ Solvable G k T' := by
  rw [solvable_iff_searchSol_cl hT, solvable_iff_searchSol_cl hT', h]

end Reinsert

/-! ### The search with the memo and old move, as a big-step semantics -/

section Exec

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ)
variable (F : Finset V → Finset V → Finset V)

/-- `Exec G k F M S Q o M′`: a completed run answering `false`, with memo `M` before and `M′`
after. With `o = none` it is a call on the state `S` with old moves `Q`; with `o = some l` it is
the rest of the loop of the node `S`, children `l` still to run and `Q` the current `seen`.
`F S Q` is the filter's output at `(S, Q)` (`search_soundness.md` §1.5 steps 3–5). -/
inductive Exec : Set (Finset V) → Finset V → Finset V → Option (List V) → Set (Finset V) → Prop
  /-- Step 2: the state is in the memo. -/
  | hit {M : Set (Finset V)} {S Q : Finset V} : S ∈ M → Exec M S Q none M
  /-- Steps 3–8: `Q ← Q ∩ R(S)`; run the loop over an enumeration `l` of the filter's output;
  then record `S`, or not (memo off, or full). -/
  | node {M M' : Set (Finset V)} {S Q : Finset V} (l : List V) (record : Bool) : S ≠ univ →
      (∀ c, c ∈ l ↔ c ∈ F S (Q \ S)) → Exec M S (Q \ S) (some l) M' →
      Exec M S Q none (if record then insert S M' else M')
  /-- The loop is done. -/
  | nil {M : Set (Finset V)} {S seen : Finset V} : Exec M S seen (some []) M
  /-- Step 7: the child `c` is called on `cl(c · S)` with old moves `Q′`, some of the `q ∈ seen`
  passing the inheritance test, and answers `false`; `c` joins `seen`. -/
  | cons {M M₁ M₂ : Set (Finset V)} {S seen Q' : Finset V} (c : V) (l : List V) :
      Q' ⊆ seen.filter (fun q => stepCost G (insert q S) c ≤ k) →
      Exec M (cl G (insert c S)) Q' none M₁ → Exec M₁ S (insert c seen) (some l) M₂ →
      Exec M S seen (some (c :: l)) M₂

/-- The filter is node-sound (`search_soundness.md` §2.0) at every node with the invariant. -/
def FilterSound : Prop :=
  ∀ S Q : Finset V, (opened G S \ S).card ≤ k → S ≠ univ →
    (∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) → SearchSol G k S →
    ∃ c ∈ F S Q, SearchSol G k (cl G (insert c S))

/-- The filter returns playable customers only. -/
def FilterPlayable : Prop := ∀ S Q c, c ∈ F S Q → c ∉ S ∧ stepCost G S c ≤ k

variable {G k F}

/-- **Old move and the memo together are sound.** From a memo of genuine refutations and old
moves genuinely refuted, a completed run leaves a memo of genuine refutations, a call answers
`false` only at a state with no solution, and a loop's children all have none. -/
theorem Exec.sound (hF : FilterSound G k F) (hP : FilterPlayable G k F)
    {M M' : Set (Finset V)} {S Q : Finset V} {o : Option (List V)}
    (h : Exec G k F M S Q o M') :
    (opened G S \ S).card ≤ k → (∀ T ∈ M, ¬ SearchSol G k T) →
      (∀ q ∈ Q, q ∉ S → ¬ SearchSol G k (cl G (insert q S))) →
      (∀ l, o = some l → ∀ c ∈ l, c ∉ S ∧ stepCost G S c ≤ k) →
      (∀ T ∈ M', ¬ SearchSol G k T) ∧ (o = none → ¬ SearchSol G k S) ∧
        (∀ l, o = some l → ∀ c ∈ l, ¬ SearchSol G k (cl G (insert c S))) := by
  induction h with
  | hit hS =>
    intro _ hM _ _
    exact ⟨hM, (fun _ => hM _ hS), (fun _ h => by cases h)⟩
  | @node M M' S Q l record hS hl _ ih =>
    intro hk hM hQ _
    have hQ' : ∀ q ∈ Q \ S, q ∉ S → ¬ SearchSol G k (cl G (insert q S)) :=
      fun q hq hqS => hQ q (mem_sdiff.1 hq).1 hqS
    obtain ⟨hM', -, hchildren⟩ := ih hk hM hQ'
      (fun l' hl' c hc => hP S _ c ((hl c).1 (by cases hl'; exact hc)))
    have hnot : ¬ SearchSol G k S := fun hs => by
      obtain ⟨c, hc, hcs⟩ := hF S (Q \ S) hk hS (fun q hq => hQ' q hq (mem_sdiff.1 hq).2) hs
      exact hchildren l rfl c ((hl c).2 hc) hcs
    refine ⟨?_, (fun _ => hnot), (fun _ h => by cases h)⟩
    cases record
    · exact hM'
    · intro T hT
      rcases Set.mem_insert_iff.1 hT with rfl | hT
      · exact hnot
      · exact hM' T hT
  | nil =>
    intro _ hM _ _
    exact ⟨hM, (fun h => by cases h), (fun _ h => by cases h; simp)⟩
  | @cons M M₁ M₂ S seen Q' c l hQ' _ _ ihc ihl =>
    intro hk hM hseen hl
    obtain ⟨hcS, hck⟩ := hl _ rfl c (List.mem_cons_self ..)
    have hkc := card_opened_cl_insert_sdiff_le_of_playable hcS hck
    have hQc : ∀ q ∈ Q', q ∉ cl G (insert c S) →
        ¬ SearchSol G k (cl G (insert q (cl G (insert c S)))) := by
      intro q hq hqc hs
      obtain ⟨hqseen, htest⟩ := mem_filter.1 (hQ' hq)
      exact hseen q hqseen (fun h => hqc (subset_cl_insert S c h)) (searchSol_reinsert htest hs)
    obtain ⟨hM₁, hc, -⟩ := ihc hkc hM hQc (fun _ h => by cases h)
    have hc := hc rfl
    have hseen' : ∀ q ∈ insert c seen, q ∉ S → ¬ SearchSol G k (cl G (insert q S)) := by
      intro q hq hqS
      rcases mem_insert.1 hq with rfl | hq
      · exact hc
      · exact hseen q hq hqS
    obtain ⟨hM₂, -, hrest⟩ := ihl hk hM₁ hseen'
      (fun _ h c' hc' => hl _ rfl c' (List.mem_cons_of_mem _ (by cases h; exact hc')))
    refine ⟨hM₂, (fun h => by cases h), fun l' h c' hc' => ?_⟩
    cases h
    rcases List.mem_cons.1 hc' with rfl | hc'
    · exact hc
    · exact hrest l rfl c' hc'

/-- **A refutation from the root is genuine**: a completed run of the search from `∅` with an
empty memo and no old moves answering `false` means no closing order costs at most `k`. -/
theorem exec_root_sound (hF : FilterSound G k F) (hP : FilterPlayable G k F)
    {M' : Set (Finset V)} (h : Exec G k F ∅ ∅ ∅ none M') : ¬ Solvable G k ∅ := by
  rw [solvable_empty_iff]
  exact (h.sound hF hP (by simp [opened_empty]) (fun _ h => absurd h (Set.notMem_empty _))
    (fun _ h => absurd h (Finset.notMem_empty _)) (fun _ h => by cases h)).2.1 rfl

/-! ### Why a node's run is not locally checkable -/

/-- **The Python's worry, in the form in which it is true.** A node's run taken on its own,
with an old move that is *not* refuted, refutes a solvable state and records it: on one
isolated customer with `k = 1`, the root with `Q = {0}` has no candidates, answers `false` and
records `∅`, while `∅` has a solution. The filter here prunes nothing. What rules this out in
the search is `Exec.sound`'s hypothesis on `Q`, a property of the whole run. -/
theorem exec_fake_oldMove :
    let G : SimpleGraph (Fin 1) := ⊥
    let F : Finset (Fin 1) → Finset (Fin 1) → Finset (Fin 1) :=
      fun S Q => playable G 1 S ((univ \ S) \ Q)
    Exec G 1 F ∅ ∅ {0} none {∅} ∧ SearchSol G 1 ∅ := by
  intro G F
  refine ⟨?_, ?_⟩
  · have h := Exec.node (G := G) (k := 1) (F := F) (M := ∅) (S := ∅) (Q := {0}) [] true
      (by decide) (by intro c; revert c; decide) Exec.nil
    simpa using h
  · exact SearchSol.step 0 (by decide) (by decide) (SearchSol.done (by decide))

/-! ### The inheritance test is needed -/

/-- The path `4 – 0 – 2 – 1 – 3`, the smallest graph on which reinsertion without the test
fails (found by `python -m paper2.search_check --memo`'s exhaustive search). -/
def reinsertEdges : List (ℕ × ℕ) := [(0, 2), (0, 4), (1, 2), (1, 3)]

def reinsertGraph : SimpleGraph (Fin 5) :=
  SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ reinsertEdges

instance : DecidableRel reinsertGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ reinsertEdges ∨
    (b.val, a.val) ∈ reinsertEdges)))

/-- **Without the inheritance test the old move is unsound.** At the root with `k = 2`, the
move `c = 3` is playable and `q = 2` fails the test (`stepCost {2} 3 = 3`). A solution exists
from `q` after the child `cl{3}`, and none from `q` at the root: an old move `2` inherited by
the child `3` without the test would discard a solution. -/
theorem reinsert_needs_test :
    stepCost reinsertGraph (∅ : Finset (Fin 5)) 3 ≤ 2 ∧
      ¬ stepCost reinsertGraph (insert 2 (∅ : Finset (Fin 5))) 3 ≤ 2 ∧
      SearchSol reinsertGraph 2 (cl reinsertGraph (insert 2 (cl reinsertGraph (insert 3 ∅)))) ∧
      ¬ SearchSol reinsertGraph 2 (cl reinsertGraph (insert 2 (∅ : Finset (Fin 5)))) := by
  have h2 : cl reinsertGraph (insert 2 (∅ : Finset (Fin 5))) = {2} := by decide
  have h32 : cl reinsertGraph (insert 2 (cl reinsertGraph (insert 3 (∅ : Finset (Fin 5))))) =
      {1, 2, 3} := by decide
  refine ⟨by decide, by decide, ?_, ?_⟩
  · have hs : Solvable reinsertGraph 2 ({1, 2, 3} : Finset (Fin 5)) :=
      ⟨[0, 4], by unfold IsClosingOrder; decide, by decide⟩
    have := searchSol_cl_of_solvable (G := reinsertGraph) _ _ le_rfl hs
    rwa [← h32, cl_cl] at this
  · intro h
    have hk : (opened reinsertGraph (cl reinsertGraph (insert 2 ∅)) \
        cl reinsertGraph (insert 2 (∅ : Finset (Fin 5)))).card ≤ 2 := by rw [h2]; decide
    refine not_solvable_of_invariant {{2}} (by decide) (by decide) ?_
      (solvable_of_searchSol h hk)
    rw [h2]; decide

end Exec

/-! ### The search with both repairs -/

section Repaired

variable {V : Type*} [Fintype V] [LinearOrder V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

theorem fullFilter_subset (D : V → Prop) [DecidablePred D] (B : Finset V → V → V → Prop)
    [∀ W, DecidableRel (B W)] (S P : Finset V) : fullFilter G D B S P ⊆ P := by
  unfold fullFilter
  split_ifs with h
  · exact singleton_subset_iff.2 (mem_filter.1 (min'_mem _ h)).1
  · exact (filter_subset _ _).trans (subsetFilter_subset _ _)

theorem repairedFullFilter_playable (k L : ℕ) :
    FilterPlayable G k (repairedFullFilter G k L) := by
  intro S Q c hc
  obtain ⟨hcK, hck⟩ := mem_filter.1
    (@fullFilter_subset V _ _ G _ (IsHereditarilyDefinite G S) (Classical.decPred _)
      (fun W r q => withinLimit L W q ∧ IsRepairedBetter G k S r q) (fun _ => Classical.decRel _)
      S _ c hc)
  exact ⟨(mem_sdiff.1 (mem_sdiff.1 hcK).1).2, hck⟩

theorem repairedFullFilter_filterSound (k L : ℕ) :
    FilterSound G k (repairedFullFilter G k L) :=
  fun _ _ hk hS hQ hs => repairedFullFilter_sound hk hQ hs hS

/-- **The search with free moves, the memo, old move and both repairs is sound**: in the code's
order (`definite → subset → better`, any limit `L`), with any enumeration order of the
children, any memo policy and any inherited subset of old moves, a completed run from the root
answering `false` means `¬ Solvable G k ∅`. -/
theorem exec_repairedFullFilter_sound {k L : ℕ} {M' : Set (Finset V)}
    (h : Exec G k (repairedFullFilter G k L) ∅ ∅ ∅ none M') : ¬ Solvable G k ∅ :=
  exec_root_sound (repairedFullFilter_filterSound k L) (repairedFullFilter_playable k L) h

end Repaired

end Search

end MOSPFormalization
