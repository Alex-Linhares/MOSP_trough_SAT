/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# A gap in the proof of Kirousis & Papadimitriou (1986), Theorem 4.1

Kirousis & Papadimitriou, *Searching and pebbling*, Theoret. Comput. Sci. 47
(1986) 205–218, Theorem 4.1: `ns(G) = vs(G) + 1`. The lower half (p. 217):

> consider an optimal, recontamination-free node-searching strategy `S` for `G`.
> Define a layout `L` so that `L(v) < L(w)` iff `v` accepts a searcher before `w`
> does. For any `1 ≤ i < |V|`, let
> `Dᵢ = {v ∈ V | L(v) ≤ i and for some w (L(w) > i and {v, w} ∈ E)}`.
> Let `i₀` be an index such that `D_{i₀}` takes its maximum cardinality. Then
> `vs(G) ≤ |D_{i₀}|` (1). Consider that point during the execution of `S` at
> which exactly the vertices `v` for which `L(v) ≤ i₀` have accepted a searcher.
> Let `u₁, …, uₙ` be those among them that at this point carry a searcher. …
> `D_{i₀} ⊆ {u₁, …, uₙ}` (2). … `|{u₁, …, uₙ}| < ns(G)` (3) … `vs(G) < ns(G)`.

Claim (2) is false for the strategies the proof quantifies over. On `K_{1,3}`
(centre `0`, leaves `1, 2, 3`) the strategy

  place 1, remove 1, place 2, remove 2, place 3, remove 3,
  place 0, place 1, remove 1, place 2, remove 2, place 3

clears every edge, never recontaminates an edge (the first six moves clear
nothing and so have nothing to lose), and uses two searchers, which is
`ns(K_{1,3})`: it is optimal and recontamination-free. First acceptance orders
the vertices `1, 2, 3, 0`, so `D₁ = {1}`, `D₂ = {1, 2}`, `D₃ = {1, 2, 3}` and
`i₀ = 3` is forced. At the only points where exactly `1, 2, 3` have accepted a
searcher (after moves 5 and 6), the guards are `{3}` and `∅`. Worse, claim (2)
with (3) or (4) would give `3 = |D_{i₀}| < ns = 2`.

The theorem is not affected (`vs(K_{1,3}) + 1 = 2 = ns`), and the proof is
repaired by restricting `S` to strategies in which no vertex is visited twice —
which the paper's Corollary 2.4 (p. 210) provides, and which the sentence "In
the sequel we shall consider only strategies of the above type" (p. 208, after
Corollary 2.2, stated for edge searching) may be read as imposing. The proof of
Theorem 4.1 cites neither; "optimal, recontamination-free" alone does not
exclude this strategy (`kpStrategy_not_visitsOnce`). `NodeSearch.lean`'s
`vertexSeparation_add_one_le_of_monotone` avoids the issue by ordering by
clearing time.

## Main results

* `kpStrategy_isMonotoneNodeSearch`, `searchCost_kpStrategy` — (a).
* `nodeSearch_star3`, `monotoneNodeSearch_star3` — (b): both are `2`.
* `card_kpD_three`, `kpD_card_le_three`, `kpD_max_iff` — (c): `|D₃| = 3`, the
  unique maximum; `kp_claim2_fails_star3` — the inclusion (2) fails at every
  point where exactly the first three vertices have accepted a searcher.
* `kirousisPapadimitriou_claim2_false` — (d), the headline.
* `kpStrategy_not_visitsOnce` — the strategy is excluded only by Corollary 2.4's
  normal form (no vertex visited twice).
* `kpClearTime_eq`, `dBy_clearTime_card_le`, `dBy_clearTime_eq` — the repair on
  this example: with the clearing times computed from the game, ordering by
  decreasing clearing time gives `Dᵢ = {0}` for every `i`, one vertex, which is
  `ns − 1` and guarded throughout the second half of the run.
-/

import MOSPFormalization.Complex.NodeSearch
import Mathlib.Tactic.IntervalCases

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

open Finset

/-! ### Simulating a recontamination-free run with finite sets -/

section Sim

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

instance (S : Finset V) (e : Sym2 V) : Decidable (Guarded S e) := by
  unfold Guarded; infer_instance

/-- The guards after a sequence of moves: the contaminated edges play no role. -/
def guardsAfter (S : Finset V) (ms : List (SearchMove V)) : Finset V :=
  ms.foldl (fun S m => m.applyTo S) S

/-- The cost of a run computed from the guards alone. -/
def guardsCost : Finset V → List (SearchMove V) → ℕ
  | S, [] => S.card
  | S, m :: ms => max S.card (guardsCost (m.applyTo S) ms)

theorem runSearch_guards (s : SearchState V) (ms : List (SearchMove V)) :
    (runSearch G s ms).guards = guardsAfter s.guards ms := by
  induction ms generalizing s with
  | nil => rfl
  | cons m ms ih => exact ih (searchStep G s m)

theorem searchCost_eq_guardsCost (s : SearchState V) (ms : List (SearchMove V)) :
    searchCost G s ms = guardsCost s.guards ms := by
  induction ms generalizing s with
  | nil => rfl
  | cons m ms ih =>
    simp only [searchCost, guardsCost]
    rw [ih]
    rfl

/-- A move that provably recontaminates nothing: a placement, or a deletion
from a node touching no contaminated edge, or any move while every edge is
contaminated. -/
def SafeMove (C : Finset (Sym2 V)) : SearchMove V → Prop
  | .place _ => True
  | .remove v => (∀ e ∈ C, v ∉ e) ∨ C = G.edgeFinset

instance (C : Finset (Sym2 V)) (m : SearchMove V) : Decidable (SafeMove G C m) := by
  cases m <;> unfold SafeMove <;> infer_instance

/-- The contaminated edges after a safe move: those not guarded afterwards. -/
def simStep (S : Finset V) (C : Finset (Sym2 V)) (m : SearchMove V) : Finset (Sym2 V) :=
  C.filter fun e => ¬ Guarded (m.applyTo S) e

/-- Every move of the run is safe, tracking the contaminated edges. -/
def SimOK : Finset V → Finset (Sym2 V) → List (SearchMove V) → Prop
  | _, _, [] => True
  | S, C, m :: ms => SafeMove G C m ∧ SimOK (m.applyTo S) (simStep S C m) ms

instance simOKDec : (S : Finset V) → (C : Finset (Sym2 V)) → (ms : List (SearchMove V)) →
    Decidable (SimOK G S C ms)
  | _, _, [] => isTrue trivial
  | S, C, m :: ms =>
    haveI := simOKDec (m.applyTo S) (simStep S C m) ms
    inferInstanceAs (Decidable (_ ∧ _))

/-- The contaminated edges at the end of a safe run. -/
def simFinal : Finset V → Finset (Sym2 V) → List (SearchMove V) → Finset (Sym2 V)
  | _, C, [] => C
  | S, C, m :: ms => simFinal (m.applyTo S) (simStep S C m) ms

theorem step_of_safe {s : SearchState V} {C : Finset (Sym2 V)} (hC : s.contaminated = ↑C)
    (hs : IsClosed (G := G) s) {m : SearchMove V} (hm : SafeMove G C m) :
    (searchStep G s m).contaminated ⊆ s.contaminated ∧
      (searchStep G s m).contaminated = ↑(simStep s.guards C m) := by
  have hsub : (searchStep G s m).contaminated ⊆ s.contaminated := by
    cases m with
    | place v => exact step_place_subset hs v
    | remove v =>
      rcases hm with hv | hE
      · exact step_remove_subset hs v fun e he => hv e (by rw [hC] at he; exact_mod_cast he)
      · have hsE : s.contaminated = G.edgeSet := by rw [hC, hE, SimpleGraph.coe_edgeFinset]
        rw [hsE]
        exact contaminated_step_subset_edgeSet hsE.le _
  refine ⟨hsub, ?_⟩
  ext e
  simp only [simStep, coe_filter, Set.mem_ofPred_eq]
  constructor
  · intro he
    refine ⟨?_, not_guarded_of_mem_step he⟩
    have := hsub he
    rw [hC] at this
    exact_mod_cast this
  · rintro ⟨he, hg⟩
    exact mem_step_of_mem (by rw [hC]; exact_mod_cast he) hg

/-- A safe run is recontamination-free and ends at `simFinal`. -/
theorem sim_correct {s : SearchState V} {C : Finset (Sym2 V)} (hC : s.contaminated = ↑C)
    (hs : IsClosed (G := G) s) {ms : List (SearchMove V)} (h : SimOK G s.guards C ms) :
    NoRecontamination G s ms ∧
      (runSearch G s ms).contaminated = ↑(simFinal s.guards C ms) := by
  induction ms generalizing s C with
  | nil => exact ⟨trivial, hC⟩
  | cons m ms ih =>
    obtain ⟨hm, hrest⟩ := h
    obtain ⟨h1, h2⟩ := step_of_safe G hC hs hm
    obtain ⟨h3, h4⟩ := ih h2 (isClosed_step s m) hrest
    exact ⟨⟨h1, h3⟩, h4⟩

/-- With at most one searcher at any time no edge is ever cleared. -/
theorem contaminated_eq_of_searchCost_le_one {s : SearchState V}
    (hs : s.contaminated = G.edgeSet) {ms : List (SearchMove V)}
    (hc : searchCost G s ms ≤ 1) : (runSearch G s ms).contaminated = G.edgeSet := by
  induction ms generalizing s with
  | nil => exact hs
  | cons m ms ih =>
    apply ih _ ((le_max_right _ _).trans hc)
    apply le_antisymm (contaminated_step_subset_edgeSet hs.le m)
    intro e he
    have hcard : (searchStep G s m).guards.card ≤ 1 :=
      (card_le_searchCost _ ms).trans ((le_max_right _ _).trans hc)
    refine mem_step_of_mem (by rw [hs]; exact he) ?_
    intro hg
    induction e using Sym2.ind with
    | h a b =>
      have hab : a ≠ b := G.ne_of_adj he
      have : ({a, b} : Finset V) ⊆ (searchStep G s m).guards := by
        intro x hx
        rcases Finset.mem_insert.mp hx with rfl | hx
        · exact hg _ (Sym2.mem_mk_left _ _)
        · rw [Finset.mem_singleton.mp hx]; exact hg _ (Sym2.mem_mk_right _ _)
      have := (Finset.card_le_card this).trans hcard
      rw [Finset.card_pair hab] at this
      omega

/-- Clearing an edge needs two searchers at once. -/
theorem two_le_of_isNodeSearch {u v : V} (huv : G.Adj u v) {k : ℕ}
    {ms : List (SearchMove V)} (h : IsNodeSearch G k ms) : 2 ≤ k := by
  by_contra hk
  have := contaminated_eq_of_searchCost_le_one G (s := searchInit G) rfl
    (ms := ms) (by have := h.2; omega)
  rw [h.1] at this
  have hmem : s(u, v) ∈ G.edgeSet := huv
  rw [← this] at hmem
  exact hmem

/-! ### The paper's first-acceptance layout -/

/-- `v` accepts a searcher at this move. -/
def SearchMove.placesOn (v : V) : SearchMove V → Bool
  | .place w => decide (w = v)
  | .remove _ => false

/-- The index of the move at which `v` first accepts a searcher (the length of
the strategy if it never does). -/
def firstAccept (ms : List (SearchMove V)) (v : V) : ℕ := ms.findIdx (SearchMove.placesOn v)

/-- The paper's layout `L` (1-based): `L(v) < L(w)` iff `v` accepts a searcher
before `w` does. -/
def kpLayout (ms : List (SearchMove V)) (v : V) : ℕ :=
  (univ.filter fun w => firstAccept ms w < firstAccept ms v).card + 1

/-- The paper's `Dᵢ = {v | L(v) ≤ i and some neighbour w has L(w) > i}`. -/
def kpD (ms : List (SearchMove V)) (i : ℕ) : Finset V :=
  univ.filter fun v => kpLayout ms v ≤ i ∧ ∃ w, G.Adj v w ∧ i < kpLayout ms w

/-- The vertices that have accepted a searcher after the first `t` moves. -/
def acceptedBy (ms : List (SearchMove V)) (t : ℕ) : Finset V :=
  univ.filter fun v => firstAccept ms v < t

/-- No vertex accepts a searcher twice (condition (i) of the paper's
Corollaries 2.2 and 2.4). -/
def VisitsOnce (ms : List (SearchMove V)) : Prop :=
  ∀ v, ms.countP (SearchMove.placesOn v) ≤ 1

instance (ms : List (SearchMove V)) : Decidable (VisitsOnce ms) := by
  unfold VisitsOnce; infer_instance

end Sim

/-! ### The counterexample on `K_{1,3}` -/

section Star

/-- `K_{1,3}`: centre `0`, leaves `1, 2, 3`. -/
abbrev star3 : SimpleGraph (Fin 4) := starGraph 3

/-- Guard and release each leaf, then search from the centre. -/
def kpStrategy : List (SearchMove (Fin 4)) :=
  [.place 1, .remove 1, .place 2, .remove 2, .place 3, .remove 3,
   .place 0, .place 1, .remove 1, .place 2, .remove 2, .place 3]

theorem kpStrategy_simOK : SimOK star3 ∅ star3.edgeFinset kpStrategy := by decide

theorem kpStrategy_simFinal : simFinal ∅ star3.edgeFinset kpStrategy = ∅ := by decide

/-- (a) The strategy is recontamination-free and clears `K_{1,3}`. -/
theorem kpStrategy_noRecontamination_and_clears :
    NoRecontamination star3 (searchInit star3) kpStrategy ∧
      (runSearch star3 (searchInit star3) kpStrategy).contaminated = ∅ := by
  obtain ⟨h1, h2⟩ := sim_correct star3 (s := searchInit star3) (C := star3.edgeFinset)
    (by simp [searchInit]) isClosed_init kpStrategy_simOK
  refine ⟨h1, ?_⟩
  rw [h2]
  exact_mod_cast kpStrategy_simFinal

/-- (a) It uses two searchers. -/
theorem searchCost_kpStrategy : searchCost star3 (searchInit star3) kpStrategy = 2 := by
  rw [searchCost_eq_guardsCost]
  decide

theorem kpStrategy_isMonotoneNodeSearch : IsMonotoneNodeSearch star3 2 kpStrategy :=
  ⟨⟨kpStrategy_noRecontamination_and_clears.2, searchCost_kpStrategy.le⟩,
    kpStrategy_noRecontamination_and_clears.1⟩

theorem star3_adj_01 : star3.Adj 0 1 := by decide

/-- (b) `ns(K_{1,3}) = 2`, so the strategy is optimal. -/
theorem nodeSearch_star3 : nodeSearch star3 = 2 := by
  unfold nodeSearch
  refine le_antisymm (Nat.sInf_le ⟨kpStrategy, kpStrategy_isMonotoneNodeSearch.1⟩) ?_
  refine le_csInf ⟨2, kpStrategy, kpStrategy_isMonotoneNodeSearch.1⟩ ?_
  rintro k ⟨ms, hms⟩
  exact two_le_of_isNodeSearch star3 star3_adj_01 hms

theorem monotoneNodeSearch_star3 : monotoneNodeSearch star3 = 2 := by
  unfold monotoneNodeSearch
  refine le_antisymm (Nat.sInf_le ⟨kpStrategy, kpStrategy_isMonotoneNodeSearch⟩) ?_
  refine le_csInf ⟨2, kpStrategy, kpStrategy_isMonotoneNodeSearch⟩ ?_
  rintro k ⟨ms, hms⟩
  exact two_le_of_isNodeSearch star3 star3_adj_01 hms.1

/-- The strategy is optimal among all strategies and among recontamination-free
ones. -/
theorem kpStrategy_optimal :
    IsMonotoneNodeSearch star3 (nodeSearch star3) kpStrategy ∧
      searchCost star3 (searchInit star3) kpStrategy = nodeSearch star3 ∧
      searchCost star3 (searchInit star3) kpStrategy = monotoneNodeSearch star3 := by
  rw [nodeSearch_star3, monotoneNodeSearch_star3, searchCost_kpStrategy]
  exact ⟨kpStrategy_isMonotoneNodeSearch, rfl, rfl⟩

/-- It is excluded only by the paper's Corollary 2.4 normal form: leaf `1`
accepts a searcher twice. -/
theorem kpStrategy_not_visitsOnce : ¬ VisitsOnce kpStrategy := by decide

/-- (c) First acceptance lays out `1, 2, 3, 0`. -/
theorem kpLayout_kpStrategy :
    kpLayout kpStrategy 1 = 1 ∧ kpLayout kpStrategy 2 = 2 ∧ kpLayout kpStrategy 3 = 3 ∧
      kpLayout kpStrategy 0 = 4 := by decide

theorem kpD_one : kpD star3 kpStrategy 1 = {1} := by decide
theorem kpD_two : kpD star3 kpStrategy 2 = {1, 2} := by decide
theorem kpD_three : kpD star3 kpStrategy 3 = {1, 2, 3} := by decide

/-- (c) `|D₃| = 3`. -/
theorem card_kpD_three : (kpD star3 kpStrategy 3).card = 3 := by decide

/-- (c) `D₃` has the largest cardinality over `1 ≤ i < |V|`. -/
theorem kpD_card_le_three : ∀ i, 1 ≤ i → i < 4 →
    (kpD star3 kpStrategy i).card ≤ (kpD star3 kpStrategy 3).card := by decide

/-- (c) and it is the only index of largest cardinality: `i₀ = 3` is forced. -/
theorem kpD_max_iff (i₀ : ℕ) (h1 : 1 ≤ i₀) (h4 : i₀ < 4) :
    (∀ i, 1 ≤ i → i < 4 → (kpD star3 kpStrategy i).card ≤ (kpD star3 kpStrategy i₀).card) ↔
      i₀ = 3 := by
  constructor
  · intro h
    have := h 3 (by omega) (by omega)
    interval_cases i₀ <;> simp_all [kpD_one, kpD_two, kpD_three]
  · rintro rfl; exact kpD_card_le_three

/-- The guards after the first `t` moves. -/
theorem guards_take (t : ℕ) :
    (runSearch star3 (searchInit star3) (kpStrategy.take t)).guards =
      guardsAfter ∅ (kpStrategy.take t) :=
  runSearch_guards star3 _ _

/-- The points at which exactly the vertices with `L(v) ≤ 3` have accepted a
searcher are after moves 5 and 6. -/
theorem acceptedBy_eq_iff (t : ℕ) :
    acceptedBy kpStrategy t = univ.filter (fun v => kpLayout kpStrategy v ≤ 3) ↔
      t = 5 ∨ t = 6 := by
  rcases Nat.lt_or_ge t 13 with ht | ht
  · interval_cases t <;> decide
  · have h0 : (0 : Fin 4) ∈ acceptedBy kpStrategy t := by
      simp only [acceptedBy, mem_filter, mem_univ, true_and]
      have : firstAccept kpStrategy (0 : Fin 4) = 6 := by decide
      omega
    constructor
    · intro h
      rw [h] at h0
      exact absurd (mem_filter.mp h0).2 (by decide)
    · omega

/-- (c) **Claim (2) fails.** At every point where exactly the vertices with
`L(v) ≤ i₀ = 3` have accepted a searcher, `D_{i₀}` is not contained in the set
of guarded vertices. -/
theorem kp_claim2_fails_star3 (t : ℕ)
    (ht : acceptedBy kpStrategy t = univ.filter (fun v => kpLayout kpStrategy v ≤ 3)) :
    ¬ kpD star3 kpStrategy 3 ⊆ (runSearch star3 (searchInit star3) (kpStrategy.take t)).guards := by
  rw [guards_take]
  rcases (acceptedBy_eq_iff t).mp ht with rfl | rfl <;> decide


/-! ### The repair on this example: order by clearing time -/

/-- The contaminated edges after each prefix of the strategy, from the game. -/
theorem contaminated_take (t : ℕ) :
    (runSearch star3 (searchInit star3) (kpStrategy.take t)).contaminated =
      ↑(simFinal ∅ star3.edgeFinset (kpStrategy.take t)) := by
  have hok : SimOK star3 ∅ star3.edgeFinset (kpStrategy.take t) := by
    rcases Nat.lt_or_ge t 13 with ht | ht
    · interval_cases t <;> decide
    · rw [List.take_of_length_le (by simp [kpStrategy]; omega)]
      exact kpStrategy_simOK
  exact (sim_correct star3 (s := searchInit star3) (C := star3.edgeFinset)
    (by simp [searchInit]) isClosed_init hok).2

/-- The time from which no contaminated edge touches `v` (the order used by
`vertexSeparation_add_one_le_of_monotone`). -/
noncomputable def kpClearTime (v : Fin 4) : ℕ :=
  sInf {t | ∀ e ∈ (runSearch star3 (searchInit star3) (kpStrategy.take t)).contaminated, v ∉ e}

/-- Its computable form on this strategy. -/
def kpClearKey : Fin 4 → ℕ := ![12, 8, 10, 12]

theorem kpClearTime_eq (v : Fin 4) : kpClearTime v = kpClearKey v := by
  have hyes : ∀ e ∈ simFinal ∅ star3.edgeFinset (kpStrategy.take (kpClearKey v)), v ∉ e := by
    revert v; decide
  have hno : ∀ t < kpClearKey v, ¬ ∀ e ∈ simFinal ∅ star3.edgeFinset (kpStrategy.take t), v ∉ e := by
    revert v; decide
  have hclear : ∀ t, (∀ e ∈ (runSearch star3 (searchInit star3) (kpStrategy.take t)).contaminated,
      v ∉ e) ↔ ∀ e ∈ simFinal ∅ star3.edgeFinset (kpStrategy.take t), v ∉ e := by
    intro t; rw [contaminated_take]; simp
  unfold kpClearTime
  apply le_antisymm (Nat.sInf_le (show kpClearKey v ∈ {t | ∀ e ∈ (runSearch star3
    (searchInit star3) (kpStrategy.take t)).contaminated, v ∉ e} from (hclear _).mpr hyes))
  refine le_csInf ⟨_, (hclear _).mpr hyes⟩ fun t ht => ?_
  by_contra hlt
  exact hno t (by omega) ((hclear t).mp ht)

/-- The paper's layout, for an arbitrary key: `L(v) < L(w)` iff `key v < key w`. -/
def layoutBy (key : Fin 4 → ℕ) (v : Fin 4) : ℕ := (univ.filter fun w => key w < key v).card + 1

/-- The paper's `Dᵢ` for that layout. -/
def dBy (key : Fin 4 → ℕ) (i : ℕ) : Finset (Fin 4) :=
  univ.filter fun v => layoutBy key v ≤ i ∧ ∃ w, star3.Adj v w ∧ i < layoutBy key w

/-- Ordering by *decreasing* clearing time (the paper counts earlier endpoints;
`NodeSearch.lean` counts later endpoints in increasing clearing time), every
`Dᵢ` has at most `ns − 1 = 1` vertex, as the argument needs. -/
theorem dBy_clearTime_card_le (i : ℕ) :
    (dBy (fun v => 12 - kpClearTime v) i).card ≤ nodeSearch star3 - 1 := by
  rw [nodeSearch_star3]
  have : (fun v => 12 - kpClearTime v) = fun v => 12 - kpClearKey v := by
    funext v; rw [kpClearTime_eq]
  rw [this]
  rcases Nat.lt_or_ge i 5 with hi | hi
  · interval_cases i <;> decide
  · have : dBy (fun v => 12 - kpClearKey v) i = ∅ := by
      ext v
      simp only [dBy, mem_filter, mem_univ, true_and, Finset.notMem_empty, iff_false, not_and,
        not_exists]
      intro _ w _ hw
      have hc := Finset.card_le_univ (univ.filter fun u =>
        (fun v => 12 - kpClearKey v) u < (fun v => 12 - kpClearKey v) w)
      rw [Fintype.card_fin] at hc
      unfold layoutBy at hw
      omega
    rw [this]; simp

/-- …and `D_i` is guarded at the time the `i`-th vertex in that order is cleared:
here `Dᵢ = {0}` for `1 ≤ i < 4`, and the centre is guarded from move 7 on. -/
theorem dBy_clearTime_eq (i : ℕ) (h1 : 1 ≤ i) (h4 : i < 4) :
    dBy (fun v => 12 - kpClearTime v) i = {0} := by
  have : (fun v => 12 - kpClearTime v) = fun v => 12 - kpClearKey v := by
    funext v; rw [kpClearTime_eq]
  rw [this]
  interval_cases i <;> decide

/-! ### The headline -/

/-- **Claim (2) of Kirousis & Papadimitriou (1986), p. 217, is false.** There is
a graph with an edge and an optimal, recontamination-free node-searching strategy
clearing it such that, for the first-acceptance layout `L`, every index `i₀`
maximising `|D_i|` over `1 ≤ i < |V|` has `ns(G) ≤ |D_{i₀}|` — so neither (2) with
(3), nor (4), which give `|D_{i₀}| < ns(G)`, can hold — and at every point of the
run at which exactly the vertices with `L(v) ≤ i₀` have accepted a searcher,
`D_{i₀}` is not contained in the set of guarded vertices. -/
theorem kirousisPapadimitriou_claim2_false :
    ∃ (n : ℕ) (G : SimpleGraph (Fin n)) (_ : DecidableRel G.Adj) (ms : List (SearchMove (Fin n))),
      (∃ u v, G.Adj u v) ∧
      IsMonotoneNodeSearch G (nodeSearch G) ms ∧
      searchCost G (searchInit G) ms = nodeSearch G ∧
      ∃ i₀, 1 ≤ i₀ ∧ i₀ < n ∧
        (∀ i, 1 ≤ i → i < n → (kpD G ms i).card ≤ (kpD G ms i₀).card) ∧
        ∀ j₀, 1 ≤ j₀ → j₀ < n →
          (∀ i, 1 ≤ i → i < n → (kpD G ms i).card ≤ (kpD G ms j₀).card) →
          nodeSearch G ≤ (kpD G ms j₀).card ∧
          (∃ t, acceptedBy ms t = univ.filter (fun v => kpLayout ms v ≤ j₀)) ∧
          ∀ t, acceptedBy ms t = univ.filter (fun v => kpLayout ms v ≤ j₀) →
            ¬ kpD G ms j₀ ⊆ (runSearch G (searchInit G) (ms.take t)).guards := by
  refine ⟨4, star3, inferInstance, kpStrategy, ⟨0, 1, star3_adj_01⟩,
    kpStrategy_optimal.1, kpStrategy_optimal.2.1, 3, by omega, by omega,
    kpD_card_le_three, ?_⟩
  intro j₀ h1 h4 hmax
  obtain rfl := (kpD_max_iff j₀ h1 h4).mp hmax
  refine ⟨?_, ⟨5, (acceptedBy_eq_iff 5).mpr (Or.inl rfl)⟩, kp_claim2_fails_star3⟩
  rw [nodeSearch_star3, card_kpD_three]
  omega

-- #print axioms kirousisPapadimitriou_claim2_false
-- 'kirousisPapadimitriou_claim2_false' depends on axioms: [propext, Classical.choice, Quot.sound]

end Star

end Complex

end MOSPFormalization
