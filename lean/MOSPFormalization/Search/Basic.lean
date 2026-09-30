/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The customer search as a mathematical object

Section 1 of `paper2/search_soundness.md` (loop0006 item 07), the model on
which the soundness proofs of the pruning rules of Chu & Stuckey's (2009)
customer search are built (items 08–11). Source of the model: Chu & Stuckey,
*Minimizing the maximum number of open stacks by customer search*, CP 2009,
§2 (preprint p. 4): states are sets of closed customers, a move closes one
customer, and the stacks open at that moment are `|O(S) − S ∪ o(c, S)|`.
The search itself is `satisfiability/customer_search.py` (`decide`).

## Definitions

A finite graph `G` on the customers (the MOSP graph). For `T : Finset V`:

* `nbhd G c` — `N[c]`, the closed neighbourhood;
* `opened G T` — `O(T) = ⋃_{c ∈ T} N[c]`, the stacks opened so far;
* `finished G X` — `fin(X) = {c : N[c] ⊆ X}`;
* `cl G T` — `fin(O(T))`, the free-closed state the search stops at;
* `stepCost G T c` — `|O(T ∪ {c}) ∖ T|`, the stacks open when `c` closes,
  counting `c`;
* `orderCost G T l` — the cost of the closing order `l` from `T`, the maximum
  step cost along it (`0` for the empty list);
* `IsClosingOrder T l` — `l` lists `V ∖ T` without repetition;
* `Solvable G k T` — the plain predicate `P_k(T)`: some closing order of
  `V ∖ T` after `T` has cost `≤ k`;
* `SearchSol G k S` — the search's predicate `Sol_k(S)`: `S = V`, or some
  `c ∉ S` has step cost `≤ k` and `Sol_k(cl(S ∪ {c}))`.

## What is proved

* `solvable_mono` — **more closed, nothing more opened, never hurts**:
  `T ⊆ T'` and `O(T') ⊆ O(T)` give `P_k(T) → P_k(T')`. Its special case
  `solvable_insert_of_free` is the soundness of the **free move**: closing a
  customer with `N[c] ⊆ O(S)` never hurts. Its converse holds under the node
  invariant `|O(S) ∖ S| ≤ k` (`solvable_insert_iff_of_free`), and
  `solvable_cl_iff` closes all free customers at once.
* `solvable_iff_searchSol_cl` — **Lemma F**: if `|O(T) ∖ T| ≤ k` then
  `P_k(T) ↔ Sol_k(cl T)`. The direction `P_k(T) → Sol_k(cl T)` needs no
  hypothesis (`searchSol_cl_of_solvable`). At the root, `solvable_empty_iff`.
* `orderCost_ofFn_eq_outNarrowness` — the cost of the full closing order that
  closes `τ⁻¹ 0, τ⁻¹ 1, …` is `outNarrowness G τ`, the narrowness of the
  out-sequence `τ` in Kornai & Tuza's dual shack process
  (`Complex/Narrowness.lean`); `orderCost_ofFn_eq_vertexSepOfLayout_add_one`
  gives `vs(τ) + 1` for the same layout.
* `solvable_empty_iff_narrowness_le`, `searchSol_empty_iff_pathwidth_add_one_le`,
  `searchSol_empty_iff_vertexSeparation_add_one_le` — `Sol_k(∅) ↔ ν(G) ≤ k ↔
  pw(G) + 1 ≤ k` (the last two for nonempty `V`), and
  `searchSol_mospGraph_iff_mospValue_le` — for a MOSP instance with a
  requirement, `Sol_k(∅)` on its MOSP graph iff `mospValue ≤ k`. So the only
  thing a refutation `¬ Sol_k(∅)` may mean is `mospValue > k`.

## Conventions

The graph here has every customer as a vertex. The search itself drops the
customers with no product (`Py:193–194`); in `mospGraph` they are isolated
vertices, each costing one stack when closed, which never exceeds
`pw + 1 ≥ 1`, so they change neither side of the statements above.
-/

import MOSPFormalization.Complex.Narrowness
import MOSPFormalization.MOSPGraph

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Definitions -/

/-- `N[c]`: the customer and its neighbours. -/
def nbhd (c : V) : Finset V := univ.filter (fun d => d = c ∨ G.Adj c d)

/-- `O(T)`: the stacks opened once the customers of `T` are closed. -/
def opened (T : Finset V) : Finset V := T.biUnion (nbhd G)

/-- `fin(X)`: the customers all of whose neighbourhood is open in `X`. -/
def finished (X : Finset V) : Finset V := univ.filter (fun c => nbhd G c ⊆ X)

/-- `cl(T) = fin(O(T))`: `T` with every free move made. -/
def cl (T : Finset V) : Finset V := finished G (opened G T)

/-- The stacks open at the moment `c` is closed after `T`, counting `c`. -/
def stepCost (T : Finset V) (c : V) : ℕ := (opened G (insert c T) \ T).card

/-- The cost of closing the customers of `l` in order, after `T`. -/
def orderCost : Finset V → List V → ℕ
  | _, [] => 0
  | T, c :: l => max (stepCost G T c) (orderCost (insert c T) l)

/-- `l` is an ordering of the customers not in `T`. -/
def IsClosingOrder (T : Finset V) (l : List V) : Prop :=
  l.Nodup ∧ ∀ c, c ∈ l ↔ c ∉ T

/-- `P_k(T)`: some ordering of `V ∖ T` after `T` has cost at most `k`. -/
def Solvable (k : ℕ) (T : Finset V) : Prop :=
  ∃ l, IsClosingOrder T l ∧ orderCost G T l ≤ k

/-- `Sol_k(S)`, the predicate the search decides: all customers are closed, or
some playable move leads to a free-closed state satisfying it. -/
inductive SearchSol (k : ℕ) : Finset V → Prop
  | done {S : Finset V} : S = univ → SearchSol k S
  | step {S : Finset V} (c : V) : c ∉ S → stepCost G S c ≤ k →
      SearchSol k (cl G (insert c S)) → SearchSol k S

/-! ### Opened and finished sets -/

variable {G}

theorem mem_nbhd {c d : V} : d ∈ nbhd G c ↔ d = c ∨ G.Adj c d := by
  simp [nbhd]

theorem self_mem_nbhd (c : V) : c ∈ nbhd G c := mem_nbhd.2 (Or.inl rfl)

theorem mem_nbhd_comm {c d : V} : d ∈ nbhd G c ↔ c ∈ nbhd G d := by
  simp only [mem_nbhd]
  constructor
  · rintro (rfl | h)
    · exact Or.inl rfl
    · exact Or.inr h.symm
  · rintro (rfl | h)
    · exact Or.inl rfl
    · exact Or.inr h.symm

theorem mem_opened {T : Finset V} {v : V} : v ∈ opened G T ↔ ∃ c ∈ T, v ∈ nbhd G c := by
  simp [opened]

theorem opened_empty : opened G (∅ : Finset V) = ∅ := by simp [opened]

theorem opened_insert (c : V) (T : Finset V) :
    opened G (insert c T) = nbhd G c ∪ opened G T := by
  simp [opened, Finset.biUnion_insert]

theorem opened_mono {T T' : Finset V} (h : T ⊆ T') : opened G T ⊆ opened G T' :=
  Finset.biUnion_subset_biUnion_of_subset_left _ h

theorem subset_opened (T : Finset V) : T ⊆ opened G T := fun c hc =>
  mem_opened.2 ⟨c, hc, self_mem_nbhd c⟩

theorem mem_finished {X : Finset V} {c : V} : c ∈ finished G X ↔ nbhd G c ⊆ X := by
  simp [finished]

theorem subset_cl (T : Finset V) : T ⊆ cl G T := fun c hc =>
  mem_finished.2 fun _ hd => mem_opened.2 ⟨c, hc, hd⟩

/-- A set of finished customers opens nothing new. -/
theorem opened_subset_of_subset_cl {T T' : Finset V} (h : T' ⊆ cl G T) :
    opened G T' ⊆ opened G T := by
  intro v hv
  obtain ⟨c, hc, hvc⟩ := mem_opened.1 hv
  exact mem_finished.1 (h hc) hvc

/-- `O(cl T) = O(T)`: the memo may key on the closed set alone. -/
theorem opened_cl (T : Finset V) : opened G (cl G T) = opened G T :=
  le_antisymm (opened_subset_of_subset_cl le_rfl) (opened_mono (subset_cl T))

theorem cl_empty : cl G (∅ : Finset V) = ∅ := by
  ext c
  simp only [cl, mem_finished, opened_empty, Finset.subset_empty, Finset.notMem_empty,
    iff_false]
  exact Finset.ne_empty_of_mem (self_mem_nbhd c)

theorem cl_univ : cl G (univ : Finset V) = univ :=
  Finset.eq_univ_of_forall fun c => subset_cl _ (Finset.mem_univ c)

/-- Closing `c` after `T`: the step cost in the code's second form,
`|O(T) ∖ T| + open(c, T)`, as an inequality in the direction the proofs use. -/
theorem card_opened_sdiff_le_stepCost (T : Finset V) (c : V) :
    (opened G T \ T).card ≤ stepCost G T c := by
  unfold stepCost
  exact Finset.card_le_card (Finset.sdiff_subset_sdiff (opened_mono (Finset.subset_insert _ _))
    le_rfl)

/-- After closing `c ∉ T` the node invariant drops by one from the step cost. -/
theorem card_opened_insert_sdiff_lt {T : Finset V} {c : V} (hc : c ∉ T) :
    (opened G (insert c T) \ insert c T).card < stepCost G T c := by
  unfold stepCost
  apply Finset.card_lt_card
  refine ⟨Finset.sdiff_subset_sdiff le_rfl (Finset.subset_insert _ _), fun h => ?_⟩
  have hmem : c ∈ opened G (insert c T) \ T :=
    Finset.mem_sdiff.2 ⟨subset_opened _ (Finset.mem_insert_self _ _), hc⟩
  exact (Finset.mem_sdiff.1 (h hmem)).2 (Finset.mem_insert_self _ _)

/-- A free move costs exactly the node invariant `|O(T) ∖ T|`. -/
theorem stepCost_of_free {T : Finset V} {c : V} (h : nbhd G c ⊆ opened G T) :
    stepCost G T c = (opened G T \ T).card := by
  unfold stepCost
  rw [opened_insert, Finset.union_eq_right.2 h]

/-! ### Closing orders -/

theorem isClosingOrder_nil_iff {T : Finset V} : IsClosingOrder T [] ↔ T = univ := by
  simp only [IsClosingOrder, List.nodup_nil, List.not_mem_nil, false_iff, not_not, true_and]
  exact ⟨fun h => Finset.eq_univ_of_forall h, fun h c => h ▸ Finset.mem_univ c⟩

theorem IsClosingOrder.cons_iff {T : Finset V} {c : V} {l : List V} :
    IsClosingOrder T (c :: l) ↔ c ∉ T ∧ IsClosingOrder (insert c T) l := by
  unfold IsClosingOrder
  constructor
  · rintro ⟨hnd, hmem⟩
    have hc : c ∉ T := (hmem c).1 (List.mem_cons_self)
    have hcl : c ∉ l := (List.nodup_cons.1 hnd).1
    refine ⟨hc, (List.nodup_cons.1 hnd).2, fun x => ?_⟩
    rw [Finset.mem_insert, not_or]
    constructor
    · intro hx
      exact ⟨fun h => hcl (h ▸ hx), (hmem x).1 (List.mem_cons_of_mem _ hx)⟩
    · rintro ⟨hxc, hxT⟩
      rcases List.mem_cons.1 ((hmem x).2 hxT) with h | h
      · exact absurd h hxc
      · exact h
  · rintro ⟨hc, hnd, hmem⟩
    have hcl : c ∉ l := fun h => (hmem c).1 h (Finset.mem_insert_self _ _)
    refine ⟨List.nodup_cons.2 ⟨hcl, hnd⟩, fun x => ?_⟩
    rw [List.mem_cons, hmem, Finset.mem_insert, not_or]
    constructor
    · rintro (rfl | ⟨_, h⟩)
      · exact hc
      · exact h
    · intro hx
      by_cases hxc : x = c
      · exact Or.inl hxc
      · exact Or.inr ⟨hxc, hx⟩

variable (G)

theorem orderCost_cons (T : Finset V) (c : V) (l : List V) :
    orderCost G T (c :: l) = max (stepCost G T c) (orderCost G (insert c T) l) := rfl

/-- The step costs a closing order is made of can only fall when more customers
are closed and nothing more is opened. -/
theorem orderCost_filter_le (l : List V) (hl : l.Nodup) :
    ∀ (T T' : Finset V), T ⊆ T' → opened G T' ⊆ opened G T →
      orderCost G T' (l.filter (fun c => c ∉ T')) ≤ orderCost G T l := by
  induction l with
  | nil => intro T T' _ _; simp [orderCost]
  | cons c l ih =>
    intro T T' hTT' hO
    have hcl : c ∉ l := (List.nodup_cons.1 hl).1
    have hnd : l.Nodup := (List.nodup_cons.1 hl).2
    rw [orderCost_cons]
    by_cases hc : c ∈ T'
    · rw [List.filter_cons_of_neg (by simpa using hc)]
      refine le_trans ?_ (le_max_right _ _)
      exact ih hnd (insert c T) T' (Finset.insert_subset hc hTT')
        (le_trans hO (opened_mono (Finset.subset_insert _ _)))
    · rw [List.filter_cons_of_pos (by simpa using hc), orderCost_cons]
      have hfilt : l.filter (fun x => x ∉ T') = l.filter (fun x => x ∉ insert c T') := by
        apply List.filter_congr
        intro x hx
        have : x ≠ c := fun h => hcl (h ▸ hx)
        simp [Finset.mem_insert, this]
      rw [hfilt]
      apply max_le_max
      · unfold stepCost
        apply Finset.card_le_card
        rw [opened_insert, opened_insert]
        exact Finset.sdiff_subset_sdiff (Finset.union_subset_union le_rfl hO) hTT'
      · refine ih hnd (insert c T) (insert c T') (Finset.insert_subset_insert _ hTT') ?_
        rw [opened_insert, opened_insert]
        exact Finset.union_subset_union le_rfl hO

theorem IsClosingOrder.filter {T T' : Finset V} {l : List V} (h : IsClosingOrder T l)
    (hTT' : T ⊆ T') : IsClosingOrder T' (l.filter (fun c => c ∉ T')) := by
  refine ⟨h.1.filter _, fun c => ?_⟩
  simp only [List.mem_filter, decide_eq_true_eq, h.2 c]
  exact ⟨fun h => h.2, fun h => ⟨fun hc => h (hTT' hc), h⟩⟩

/-! ### Monotonicity and the free move -/

variable {G}

/-- **More closed, nothing more opened, never hurts.** -/
theorem solvable_mono {k : ℕ} {T T' : Finset V} (hs : Solvable G k T) (hTT' : T ⊆ T')
    (hO : opened G T' ⊆ opened G T) : Solvable G k T' := by
  obtain ⟨l, hl, hc⟩ := hs
  exact ⟨_, hl.filter hTT', le_trans (orderCost_filter_le G l hl.1 T T' hTT' hO) hc⟩

/-- **The free move is sound**: closing a customer whose neighbourhood is
already open never hurts. -/
theorem solvable_insert_of_free {k : ℕ} {S : Finset V} {c : V}
    (hfree : nbhd G c ⊆ opened G S) (hs : Solvable G k S) : Solvable G k (insert c S) := by
  refine solvable_mono hs (Finset.subset_insert _ _) ?_
  rw [opened_insert]
  exact Finset.union_subset hfree le_rfl

theorem solvable_cl {k : ℕ} {T : Finset V} (hs : Solvable G k T) : Solvable G k (cl G T) :=
  solvable_mono hs (subset_cl T) (opened_subset_of_subset_cl le_rfl)

/-- Prepending a playable move. -/
theorem solvable_of_solvable_insert {k : ℕ} {S : Finset V} {c : V} (hc : c ∉ S)
    (hcost : stepCost G S c ≤ k) (hs : Solvable G k (insert c S)) : Solvable G k S := by
  obtain ⟨l, hl, hlc⟩ := hs
  exact ⟨c :: l, IsClosingOrder.cons_iff.2 ⟨hc, hl⟩, max_le hcost hlc⟩

/-- A playable first move out of a solvable state, and its solvable child. -/
theorem exists_first_move {k : ℕ} {S : Finset V} (hs : Solvable G k S) (hS : S ≠ univ) :
    ∃ c, c ∉ S ∧ stepCost G S c ≤ k ∧ Solvable G k (insert c S) := by
  obtain ⟨l, hl, hlc⟩ := hs
  cases l with
  | nil => exact absurd (isClosingOrder_nil_iff.1 hl) hS
  | cons c l =>
    obtain ⟨hc, hl'⟩ := IsClosingOrder.cons_iff.1 hl
    rw [orderCost_cons] at hlc
    exact ⟨c, hc, le_trans (le_max_left _ _) hlc, l, hl', le_trans (le_max_right _ _) hlc⟩

/-- The converse of the free move: closing finished customers first costs
the node invariant each time. -/
theorem solvable_of_solvable_of_subset_cl {k : ℕ} {T' : Finset V} (hT' : Solvable G k T') :
    ∀ (n : ℕ) (T : Finset V), (T' \ T).card = n → T ⊆ T' → T' ⊆ cl G T →
      (opened G T \ T).card ≤ k → Solvable G k T := by
  intro n
  induction n with
  | zero =>
    intro T hn hTT' _ _
    have : T' ⊆ T := Finset.sdiff_eq_empty_iff_subset.1 (Finset.card_eq_zero.1 hn)
    exact (le_antisymm hTT' this) ▸ hT'
  | succ n ih =>
    intro T hn hTT' hT'cl hk
    obtain ⟨c, hc⟩ := Finset.card_pos.1 (by omega : 0 < (T' \ T).card)
    obtain ⟨hcT', hcT⟩ := Finset.mem_sdiff.1 hc
    have hfree : nbhd G c ⊆ opened G T := mem_finished.1 (hT'cl hcT')
    have hO : opened G (insert c T) = opened G T := by
      rw [opened_insert, Finset.union_eq_right.2 hfree]
    refine solvable_of_solvable_insert hcT (by rw [stepCost_of_free hfree]; exact hk) ?_
    refine ih (insert c T) ?_ (Finset.insert_subset hcT' hTT') ?_ ?_
    · have : T' \ insert c T = (T' \ T).erase c := by
        ext x
        simp only [Finset.mem_sdiff, Finset.mem_insert, not_or, Finset.mem_erase]
        tauto
      rw [this, Finset.card_erase_of_mem hc, hn]; rfl
    · unfold cl; rw [hO]; exact hT'cl
    · rw [hO]
      exact le_trans (Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl
        (Finset.subset_insert _ _))) hk

/-- Under the node invariant, a state and its free closure are equally
solvable. -/
theorem solvable_cl_iff {k : ℕ} {T : Finset V} (hk : (opened G T \ T).card ≤ k) :
    Solvable G k (cl G T) ↔ Solvable G k T :=
  ⟨fun h => solvable_of_solvable_of_subset_cl h _ T rfl (subset_cl T) le_rfl hk, solvable_cl⟩

/-- Under the node invariant, a free move neither helps nor hurts. -/
theorem solvable_insert_iff_of_free {k : ℕ} {S : Finset V} {c : V}
    (hfree : nbhd G c ⊆ opened G S) (hk : (opened G S \ S).card ≤ k) :
    Solvable G k (insert c S) ↔ Solvable G k S := by
  refine ⟨fun h => ?_, solvable_insert_of_free hfree⟩
  by_cases hc : c ∈ S
  · rwa [Finset.insert_eq_of_mem hc] at h
  · exact solvable_of_solvable_insert hc (by rw [stepCost_of_free hfree]; exact hk) h

/-! ### Lemma F: the search's predicate is the plain one -/

/-- The direction of Lemma F that needs no hypothesis. -/
theorem searchSol_cl_of_solvable {k : ℕ} :
    ∀ (n : ℕ) (T : Finset V), (univ \ T).card ≤ n → Solvable G k T →
      SearchSol G k (cl G T) := by
  intro n
  induction n with
  | zero =>
    intro T hn _
    have : T = univ := by
      have := Finset.card_eq_zero.1 (Nat.le_zero.1 hn)
      exact Finset.eq_univ_of_forall fun c => by
        by_contra h
        exact Finset.notMem_empty c (this ▸ Finset.mem_sdiff.2 ⟨Finset.mem_univ c, h⟩)
    subst this
    exact SearchSol.done cl_univ
  | succ n ih =>
    intro T hn hs
    have hS := solvable_cl hs
    by_cases hU : cl G T = univ
    · exact SearchSol.done hU
    obtain ⟨c, hc, hcost, hchild⟩ := exists_first_move hS hU
    refine SearchSol.step c hc hcost (ih _ ?_ hchild)
    have hsub : univ \ insert c (cl G T) ⊆ (univ \ T).erase c := by
      intro x hx
      simp only [Finset.mem_sdiff, Finset.mem_univ, true_and, Finset.mem_insert, not_or,
        Finset.mem_erase] at hx ⊢
      exact ⟨hx.1, fun h => hx.2 (subset_cl T h)⟩
    have hcm : c ∈ univ \ T :=
      Finset.mem_sdiff.2 ⟨Finset.mem_univ c, fun h => hc (subset_cl T h)⟩
    have := Finset.card_le_card hsub
    rw [Finset.card_erase_of_mem hcm] at this
    omega

theorem solvable_of_searchSol {k : ℕ} {S : Finset V} (h : SearchSol G k S) :
    (opened G S \ S).card ≤ k → Solvable G k S := by
  induction h with
  | done hS =>
    intro _
    exact ⟨[], isClosingOrder_nil_iff.2 hS, Nat.zero_le _⟩
  | @step S c hc hcost _ ih =>
    intro _
    have hlt := card_opened_insert_sdiff_lt (G := G) hc
    have hchild : Solvable G k (cl G (insert c S)) := by
      apply ih
      rw [opened_cl]
      refine le_trans (Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl
        (subset_cl _))) ?_
      omega
    exact solvable_of_solvable_insert hc hcost ((solvable_cl_iff (by omega)).1 hchild)

/-- **Lemma F** (`search_soundness.md` §1.4). Under the node invariant
`|O(T) ∖ T| ≤ k`, which holds at every node the search visits, some closing
order from `T` has cost `≤ k` iff the search's predicate holds at `cl T`. -/
theorem solvable_iff_searchSol_cl {k : ℕ} {T : Finset V} (hk : (opened G T \ T).card ≤ k) :
    Solvable G k T ↔ SearchSol G k (cl G T) := by
  refine ⟨searchSol_cl_of_solvable _ T le_rfl, fun h => ?_⟩
  refine (solvable_cl_iff hk).1 (solvable_of_searchSol h ?_)
  rw [opened_cl]
  exact le_trans (Finset.card_le_card (Finset.sdiff_subset_sdiff le_rfl (subset_cl T))) hk

/-- At the root. -/
theorem solvable_empty_iff {k : ℕ} : Solvable G k ∅ ↔ SearchSol G k (∅ : Finset V) := by
  have := solvable_iff_searchSol_cl (G := G) (k := k) (T := ∅) (by simp [opened_empty])
  rwa [cl_empty] at this

/-! ### A full closing order is an out-sequence -/

/-- The closing order that closes `τ⁻¹ 0, τ⁻¹ 1, …`. -/
def orderOfLayout (τ : LinearLayout V) : List V :=
  List.ofFn (fun i : Fin (Fintype.card V) => τ.symm i)

theorem mem_take_orderOfLayout (τ : LinearLayout V) (i : ℕ) (u : V) :
    u ∈ (orderOfLayout τ).take i ↔ (τ u).val < i := by
  rw [List.mem_take_iff_getElem]
  simp only [orderOfLayout, List.length_ofFn, List.getElem_ofFn]
  constructor
  · rintro ⟨j, hj, rfl⟩
    simp only [Equiv.apply_symm_apply]
    omega
  · intro h
    refine ⟨(τ u).val, lt_min h (τ u).isLt, ?_⟩
    simp

theorem isClosingOrder_orderOfLayout (τ : LinearLayout V) :
    IsClosingOrder (∅ : Finset V) (orderOfLayout τ) := by
  refine ⟨List.nodup_ofFn.2 τ.symm.injective, fun c => ?_⟩
  simp only [Finset.notMem_empty, not_false_eq_true, iff_true, orderOfLayout, List.mem_ofFn]
  exact ⟨τ c, by simp⟩

/-- Every full closing order is `orderOfLayout τ` for some layout `τ`. -/
theorem exists_orderOfLayout {l : List V} (hl : IsClosingOrder (∅ : Finset V) l) :
    ∃ τ : LinearLayout V, orderOfLayout τ = l := by
  have hall : ∀ x, x ∈ l := fun x => (hl.2 x).2 (Finset.notMem_empty x)
  have hlen : l.length = Fintype.card V := by
    rw [← List.toFinset_card_of_nodup hl.1]
    congr 1
    exact Finset.eq_univ_of_forall fun x => List.mem_toFinset.2 (hall x)
  let e := List.Nodup.getEquivOfForallMemList l hl.1 hall
  refine ⟨e.symm.trans (finCongr hlen), ?_⟩
  apply List.ext_getElem
  · simp [orderOfLayout, hlen]
  · intro i h₁ h₂
    simp [orderOfLayout, e]

/-- The `i`-th step of `orderOfLayout τ` opens exactly the shack of the
out-sequence `τ` just before `wᵢ` leaves it. -/
theorem stepCost_orderOfLayout (τ : LinearLayout V) (i : Fin (Fintype.card V)) :
    stepCost G ((orderOfLayout τ).take i).toFinset (τ.symm i) =
      (Complex.outShackBeforeMove G τ i).card := by
  unfold stepCost
  congr 1
  ext v
  rw [Complex.outShackBeforeMove, Finset.mem_filter]
  simp only [Finset.mem_sdiff, mem_opened, Finset.mem_insert, List.mem_toFinset,
    mem_take_orderOfLayout, Complex.EnteredBy, Finset.mem_univ, true_and, not_lt]
  have key : ∀ u : V, (u = τ.symm i ∨ (τ u).val < i) ↔ (τ u).val ≤ i := by
    intro u
    constructor
    · rintro (rfl | h)
      · simp
      · exact h.le
    · intro h
      rcases Nat.eq_or_lt_of_le h with h | h
      · left
        rw [Equiv.eq_symm_apply]
        exact Fin.ext h
      · exact Or.inr h
  constructor
  · rintro ⟨⟨u, hu, hv⟩, hle⟩
    refine ⟨⟨u, ?_, (key u).1 hu⟩, hle⟩
    rcases mem_nbhd.1 hv with h | h
    · exact Or.inl h.symm
    · exact Or.inr h.symm
  · rintro ⟨⟨u, hu, hle⟩, hge⟩
    refine ⟨⟨u, (key u).2 hle, ?_⟩, hge⟩
    rcases hu with h | h
    · exact mem_nbhd.2 (Or.inl h.symm)
    · exact mem_nbhd.2 (Or.inr h.symm)

variable (G)

/-- A closing order's cost is at most `k` iff every step's is. -/
theorem orderCost_le_iff (k : ℕ) :
    ∀ (l : List V) (T : Finset V), orderCost G T l ≤ k ↔
      ∀ (i : ℕ) (hi : i < l.length), stepCost G (T ∪ (l.take i).toFinset) l[i] ≤ k := by
  intro l
  induction l with
  | nil => intro T; simp [orderCost]
  | cons c l ih =>
    intro T
    rw [orderCost_cons, max_le_iff, ih]
    constructor
    · rintro ⟨h0, hs⟩ i hi
      cases i with
      | zero => simpa using h0
      | succ j =>
        have := hs j (by simpa using hi)
        simpa [List.take_succ_cons, List.toFinset_cons, Finset.union_insert,
          Finset.insert_union] using this
    · intro h
      have h0 := h 0 (by simp)
      simp only [List.getElem_cons_zero, List.take_zero, List.toFinset_nil,
        Finset.union_empty] at h0
      refine ⟨h0, fun j hj => ?_⟩
      have := h (j + 1) (by simpa using hj)
      simpa [List.take_succ_cons, List.toFinset_cons, Finset.union_insert,
        Finset.insert_union] using this

theorem orderCost_orderOfLayout_le_iff (τ : LinearLayout V) (k : ℕ) :
    orderCost G ∅ (orderOfLayout τ) ≤ k ↔ Complex.outNarrowness G τ ≤ k := by
  rw [orderCost_le_iff, Complex.outNarrowness_eq_sup, Finset.sup_le_iff]
  constructor
  · intro h i _
    have := h i.val (by simp [orderOfLayout])
    simp only [Finset.empty_union, orderOfLayout, List.getElem_ofFn] at this
    rw [← stepCost_orderOfLayout]
    exact this
  · intro h i hi
    have hi' : i < Fintype.card V := by simpa [orderOfLayout] using hi
    have := h ⟨i, hi'⟩ (Finset.mem_univ _)
    rw [← stepCost_orderOfLayout] at this
    simpa [orderOfLayout] using this

/-- **A full closing order's cost is the narrowness of the out-sequence**
(Kornai & Tuza's dual shack process, `Complex/Narrowness.lean`). -/
theorem orderCost_ofFn_eq_outNarrowness (τ : LinearLayout V) :
    orderCost G ∅ (orderOfLayout τ) = Complex.outNarrowness G τ :=
  le_antisymm ((orderCost_orderOfLayout_le_iff G τ _).2 le_rfl)
    ((orderCost_orderOfLayout_le_iff G τ _).1 le_rfl)

/-- The same cost as the vertex separation of the layout, plus one. -/
theorem orderCost_ofFn_eq_vertexSepOfLayout_add_one [Nonempty V] (τ : LinearLayout V) :
    orderCost G ∅ (orderOfLayout τ) = vertexSepOfLayout G τ + 1 := by
  rw [orderCost_ofFn_eq_outNarrowness]
  have := Complex.outNarrowness_reverse G (Complex.reverseLayout τ)
  rw [Complex.reverseLayout_reverseLayout] at this
  rw [this, Complex.inNarrowness_eq_vertexSepOfLayout_reverse,
    Complex.reverseLayout_reverseLayout]

theorem solvable_empty_iff_exists_outNarrowness_le (k : ℕ) :
    Solvable G k ∅ ↔ ∃ τ : LinearLayout V, Complex.outNarrowness G τ ≤ k := by
  constructor
  · rintro ⟨l, hl, hc⟩
    obtain ⟨τ, rfl⟩ := exists_orderOfLayout hl
    exact ⟨τ, (orderCost_orderOfLayout_le_iff G τ k).1 hc⟩
  · rintro ⟨τ, hτ⟩
    exact ⟨_, isClosingOrder_orderOfLayout τ, (orderCost_orderOfLayout_le_iff G τ k).2 hτ⟩

/-- `P_k(∅) ↔ ν(G) ≤ k`. -/
theorem solvable_empty_iff_narrowness_le (k : ℕ) :
    Solvable G k ∅ ↔ Complex.narrowness G ≤ k := by
  rw [solvable_empty_iff_exists_outNarrowness_le, ← Complex.outNarrownessGraph_eq_narrowness]
  unfold Complex.outNarrownessGraph
  constructor
  · rintro ⟨τ, hτ⟩
    exact le_trans (Nat.sInf_le ⟨τ, rfl⟩) hτ
  · intro h
    obtain ⟨τ, hτ⟩ := Nat.sInf_mem (s := Set.range (fun τ : LinearLayout V =>
      Complex.outNarrowness G τ)) ⟨_, Fintype.equivFin V, rfl⟩
    exact ⟨τ, hτ.trans_le h⟩

theorem searchSol_empty_iff_narrowness_le (k : ℕ) :
    SearchSol G k (∅ : Finset V) ↔ Complex.narrowness G ≤ k := by
  rw [← solvable_empty_iff, solvable_empty_iff_narrowness_le]

theorem searchSol_empty_iff_vertexSeparation_add_one_le [Nonempty V] (k : ℕ) :
    SearchSol G k (∅ : Finset V) ↔ vertexSeparation G + 1 ≤ k := by
  rw [searchSol_empty_iff_narrowness_le, Complex.narrowness_eq_vertexSeparation_add_one]

/-- **The search decides pathwidth**: `Sol_k(∅) ↔ pw(G) + 1 ≤ k`. -/
theorem searchSol_empty_iff_pathwidth_add_one_le [Nonempty V] (k : ℕ) :
    SearchSol G k (∅ : Finset V) ↔ pathwidth G + 1 ≤ k := by
  rw [searchSol_empty_iff_narrowness_le, Complex.narrowness_eq_pathwidth_add_one]

/-- **The search decides MOSP**: on the MOSP graph of an instance with a
requirement, `Sol_k(∅)` holds iff the instance can be sequenced with at most
`k` open stacks. A refutation `¬ Sol_k(∅)` therefore means `mospValue > k`. -/
theorem searchSol_mospGraph_iff_mospValue_le {C Pt : Type*} [Fintype C] [DecidableEq C]
    [Fintype Pt] [DecidableEq Pt] (M : MOSPInstance C Pt) [DecidableRel M.requires]
    (h : ∃ c p, M.requires c p) (k : ℕ) :
    SearchSol M.mospGraph k (∅ : Finset C) ↔ M.mospValue ≤ k := by
  have : Nonempty C := let ⟨c, _⟩ := h; ⟨c⟩
  rw [searchSol_empty_iff_pathwidth_add_one_le, M.mospValue_eq_pathwidth_add_one h]

end Search

end MOSPFormalization
