/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Edge search, full game: `vs ≤ s ≤ vs + 2`

Loop0005 item 14, the reserve, second half. Ellis, Sudborough & Turner
(1994), Lemma 2.1 (p. 55), `vs(G) ≤ s(G)`, for the **full** edge search game
of `EdgeSearch.lean` (recontamination allowed), and hence their Theorem 2.1
`vs ≤ s ≤ vs + 2` for the game as they define it. `EdgeSearch.lean` proved
the lower half only for progressive strategies and derived the full one from
the named gap `EdgeSearchMonotonicity` (LaPaugh 1993); this file removes that
dependence for the band.

## The argument

The crusade method of `NodeMonotonicity.lean`, with width `k` instead of
`k − 1`. The clean set of any closed position has its outer boundary among the
guarded vertices, of which there are at most `k`. One move becomes a chain
(`exists_chain_edgeStep`): shrink to the intersection of the clean sets before
and after, add the one newly clean vertex that may be left unguarded (at most
one, by `clear_step_unique`: a slide clears one edge and its searcher lands on
the far end), then the newly clean guarded ones. The intersection is the only
delicate set: if an unguarded vertex became clean, the move was a slide
`a → b` along a contaminated edge, so `b` was not clean before and every
boundary vertex of the intersection was already guarded before the move.

## Main results

* `vertexSeparation_le_of_isEdgeSearch`, `vertexSeparation_le_edgeSearch` —
  EST Lemma 2.1, full game, every finite graph.
* `vertexSeparation_le_edgeSearch_le_add_two`,
  `pathwidth_le_edgeSearch_le_add_two` — EST Theorem 2.1, full game.
* `nodeSearch_sub_one_le_edgeSearch_le_add_one` — [10] p. 209,
  `ns − 1 ≤ es ≤ ns + 1`, full games, graphs with an edge.
* `edgeSearch_le_progressiveEdgeSearch_le_add_two` — recontamination saves at
  most two searchers.

## Not proved

LaPaugh's theorem itself, `s = ps` (`EdgeSearchMonotonicity`), stays a named
gap: the vertex-set crusade gives only `ps ≤ vs + 2 ≤ s + 2`. Closing it needs
Bienstock & Seymour's edge-set crusades and a monotone edge strategy built
from a progressive edge crusade (their route goes through mixed search), which
this session did not attempt.
-/

import MOSPFormalization.Complex.NodeMonotonicity
import MOSPFormalization.Complex.EdgeSearch

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-- A one-step chain. -/
theorem isChain_one {K : ℕ} {P Q : Finset V} (hstep : (Q \ P).card ≤ 1)
    (hP : (outerBd G P).card ≤ K) (hQ : (outerBd G Q).card ≤ K) :
    IsChain G K P Q 1 (fun i => if i = 0 then P else Q) where
  start := rfl
  stop := rfl
  step := by
    intro i hi
    obtain rfl : i = 0 := by omega
    simpa using hstep
  width := by
    intro i hi
    by_cases h0 : i = 0
    · simp only [h0, ↓reduceIte]
      exact hP
    · simp only [h0, ↓reduceIte]
      exact hQ

/-- An edge-search position seen as a node-search position: the guarded
vertices and the contaminated edges. -/
def EdgeState.view (s : EdgeState V) : SearchState V := ⟨s.guards, s.contaminated⟩

/-- A slide adds at most its target to the guarded vertices. -/
theorem guards_slide_subset (s : EdgeState V) (a b : V) :
    (edgeStep G s (.slide a b)).guards ⊆ insert b s.guards := by
  intro w hw
  simp only [edgeStep, EdgeState.guards, mem_supp, edgeCount] at hw
  rw [mem_insert]
  by_cases hwb : w = b
  · exact Or.inl hwb
  · right
    simp only [EdgeState.guards, mem_supp]
    by_cases hcond : G.Adj a b ∧ s.count a ≠ 0
    · simp only [hcond, ne_eq, not_false_eq_true, and_self, ↓reduceIte, hwb] at hw
      by_cases hwa : w = a
      · subst hwa
        simp only [↓reduceIte] at hw
        omega
      · simpa [hwa] using hw
    · simpa [hcond] using hw

/-- **One move as a chain, edge search.** From a closed position, with at most
`k` guarded vertices before and after the move, there is a chain of width
`≤ k` from the clean set before to the clean set after: shrink to the
intersection, add the (at most one) newly clean vertex left unguarded, then
the newly clean guarded ones. -/
theorem exists_chain_edgeStep {s : EdgeState V} (hs : IsClosed (G := G) s.view)
    (m : EdgeMove V) {k : ℕ} (hS : s.guards.card ≤ k)
    (hS' : (edgeStep G s m).guards.card ≤ k) :
    ∃ n X, IsChain G k (cleanSet s.view) (cleanSet (edgeStep G s m).view) n X := by
  set s' := edgeStep G s m with hs'
  set A := cleanSet s.view
  set A' := cleanSet s'.view
  have hbd : outerBd G A ⊆ s.guards := outerBd_cleanSet_subset hs
  have hbd' : outerBd G A' ⊆ s'.guards := outerBd_cleanSet_subset (isClosed_edgeStep s m)
  have hnew : ∀ v, v ∈ A' → v ∉ A →
      ∃ e ∈ s.contaminated, v ∈ e ∧ e ∉ s'.contaminated := by
    intro v hv' hv
    rw [mem_cleanSet] at hv hv'
    push Not at hv
    obtain ⟨e, he, hve⟩ := hv
    exact ⟨e, he, hve, fun h => hv' e h hve⟩
  set U := (A' \ A).filter (· ∉ s'.guards) with hU
  have hUcard : U.card ≤ 1 := by
    rw [card_le_one]
    intro x hx y hy
    by_contra hxy
    simp only [hU, mem_filter, mem_sdiff] at hx hy
    obtain ⟨e, he, hxe, he'⟩ := hnew x hx.1.1 hx.1.2
    obtain ⟨f, hf, hyf, hf'⟩ := hnew y hy.1.1 hy.1.2
    exact clear_step_unique hxy he hxe he' hf hyf hf' hx.2 hy.2
  have hUA' : U ⊆ A' := fun x hx => (mem_sdiff.mp (mem_filter.mp hx).1).1
  have hgood : ∀ C, (A ∩ A') ∪ U ⊆ C → C ⊆ A' → (outerBd G C).card ≤ k := by
    intro C h1 h2
    refine (card_le_card ?_).trans hS'
    intro w hw
    obtain ⟨hwC, v, hvC, hvw⟩ := (mem_outerBd G).mp hw
    by_cases hwA' : w ∈ A'
    · have hwA : w ∉ A := fun hwA => hwC (h1 (mem_union_left _ (mem_inter.mpr ⟨hwA, hwA'⟩)))
      by_contra hwS
      exact hwC (h1 (mem_union_right _ (mem_filter.mpr ⟨mem_sdiff.mpr ⟨hwA', hwA⟩, hwS⟩)))
    · exact hbd' ((mem_outerBd G).mpr ⟨hwA', v, h2 hvC, hvw⟩)
  have hA : (outerBd G A).card ≤ k := (card_le_card hbd).trans hS
  have hmid : (outerBd G (A ∩ A')).card ≤ k := by
    rcases U.eq_empty_or_nonempty with hUe | ⟨x, hx⟩
    · exact hgood _ (by rw [hUe, union_empty]) inter_subset_right
    · simp only [hU, mem_filter, mem_sdiff] at hx
      obtain ⟨e, he, hxe, he'⟩ := hnew x hx.1.1 hx.1.2
      have hce : e ∈ clearedBy G m s.count := by
        by_contra h
        exact he' (sdiff_subset_step s m ⟨he, h⟩)
      obtain ⟨a, b, rfl, -, -, rfl⟩ := mem_clearedBy hce
      have hbA : b ∉ A := fun hb => mem_cleanSet.mp hb _ he (Sym2.mem_mk_right _ _)
      refine (card_le_card ?_).trans hS
      intro w hw
      obtain ⟨hwC, v, hvC, hvw⟩ := (mem_outerBd G).mp hw
      rw [mem_inter] at hvC
      by_cases hwA : w ∈ A
      · have hwA' : w ∉ A' := fun h => hwC (mem_inter.mpr ⟨hwA, h⟩)
        have := guards_slide_subset s a b (hbd' ((mem_outerBd G).mpr ⟨hwA', v, hvC.2, hvw⟩))
        rw [mem_insert] at this
        exact this.resolve_left fun h => hbA (h ▸ hwA)
      · exact hbd ((mem_outerBd G).mpr ⟨hwA, v, hvC.1, hvw⟩)
  have c1 := isChain_one (G := G) (K := k) (P := A) (Q := A ∩ A')
    (by rw [sdiff_eq_empty_iff_subset.mpr inter_subset_left, card_empty]; exact Nat.zero_le _)
    hA hmid
  have c2 := isChain_one (G := G) (K := k) (P := A ∩ A') (Q := (A ∩ A') ∪ U)
    ((card_le_card (by
      intro x hx
      rw [mem_sdiff, mem_union] at hx
      exact hx.1.resolve_left hx.2)).trans hUcard)
    hmid (hgood _ subset_rfl (union_subset inter_subset_right hUA'))
  obtain ⟨n, X, c3⟩ := exists_chain_of_interval (union_subset inter_subset_right hUA') hgood
  exact ⟨_, _, (c1.trans c2).trans c3⟩

variable (G)

/-- **EST Lemma 2.1 for the full game**: any search strategy — recontamination
allowed — with at most `k` searchers gives `vs(G) ≤ k`. -/
theorem vertexSeparation_le_of_isEdgeSearch {k : ℕ} {ms : List (EdgeMove V)}
    (h : IsEdgeSearch G k ms) : vertexSeparation G ≤ k := by
  obtain ⟨hclr, hcost⟩ := h
  let st : ℕ → EdgeState V := fun t => edgeRun G (edgeInit G) (ms.take t)
  have hcard : ∀ t, (st t).guards.card ≤ k :=
    fun t => (card_supp_le_sum _).trans ((sum_le_edgeCost_take _ _ t).trans hcost)
  have hstep : ∀ t (ht : t < ms.length), st (t + 1) = edgeStep G (st t) (ms[t]'ht) :=
    fun t ht => edgeRun_take_succ (G := G) (edgeInit G) ms ht
  have h0 : st 0 = edgeInit G := by simp [st, edgeRun]
  have hclosed : ∀ t, t ≤ ms.length → IsClosed (G := G) (st t).view := by
    intro t ht
    rcases Nat.eq_zero_or_pos t with rfl | hpos
    · rw [h0]
      exact fun e he _ _ _ _ _ _ _ _ => he
    · obtain ⟨t', rfl⟩ : ∃ t', t = t' + 1 := ⟨t - 1, by omega⟩
      rw [hstep t' (by omega)]
      exact isClosed_edgeStep _ _
  have key : ∀ t ≤ ms.length, ∃ n X, IsChain G k ∅ (cleanSet (st t).view) n X := by
    intro t ht
    induction t with
    | zero =>
      rw [h0]
      refine exists_chain_of_interval (empty_subset _) fun C _ hC => ?_
      rw [card_eq_zero.mpr]
      · exact Nat.zero_le _
      · apply eq_empty_of_forall_notMem
        intro w hw
        obtain ⟨-, v, hvC, hvw⟩ := (mem_outerBd G).mp hw
        exact mem_cleanSet.mp (hC hvC) s(v, w) (G.mem_edgeSet.mpr hvw) (Sym2.mem_mk_left _ _)
    | succ t ih =>
      obtain ⟨n, X, hX⟩ := ih (by omega)
      obtain ⟨n', Y, hY⟩ := exists_chain_edgeStep (hclosed t (by omega)) (ms[t]'(by omega))
        (hcard t) (hstep t (by omega) ▸ hcard (t + 1))
      rw [hstep t (by omega)]
      exact ⟨_, _, hX.trans hY⟩
  obtain ⟨n, X, hX⟩ := key ms.length le_rfl
  have hfin : cleanSet (st ms.length).view = univ := by
    apply eq_univ_of_forall
    intro v
    rw [mem_cleanSet]
    intro e he
    have : st ms.length = edgeRun G (edgeInit G) ms := by simp [st]
    change e ∈ (st ms.length).contaminated at he
    rw [this, hclr] at he
    exact absurd he (Set.notMem_empty e)
  rw [hfin] at hX
  obtain ⟨Y, hY, hYmono⟩ := exists_monotone_chain hX
  exact vertexSeparation_le_of_monotone_chain G hY hYmono

/-- **EST Lemma 2.1**: `vs(G) ≤ s(G)`, full game, every finite graph. -/
theorem vertexSeparation_le_edgeSearch : vertexSeparation G ≤ edgeSearch G := by
  rcases isEmpty_or_nonempty V with hV | hV
  · have : vertexSeparation G = 0 := by
      apply Nat.eq_zero_of_le_zero
      refine (vertexSeparation_le_vertexSepOfLayout G (Fintype.equivFin V)).trans ?_
      simp [vertexSepOfLayout]
    omega
  · obtain ⟨ms, hms⟩ := Nat.sInf_mem (s := {k | ∃ ms, IsEdgeSearch G k ms})
      ⟨_, _, (edgeStrategy_isProgressive G (Fintype.equivFin V)).1⟩
    exact vertexSeparation_le_of_isEdgeSearch G hms

/-- **Ellis, Sudborough & Turner (1994), Theorem 2.1, full game**:
`vs(G) ≤ s(G) ≤ vs(G) + 2` on every finite graph. -/
theorem vertexSeparation_le_edgeSearch_le_add_two :
    vertexSeparation G ≤ edgeSearch G ∧ edgeSearch G ≤ vertexSeparation G + 2 :=
  ⟨vertexSeparation_le_edgeSearch G, edgeSearch_le_vertexSeparation_add_two G⟩

/-- With Kinnersley's theorem: `pw(G) ≤ s(G) ≤ pw(G) + 2`, full game. -/
theorem pathwidth_le_edgeSearch_le_add_two :
    pathwidth G ≤ edgeSearch G ∧ edgeSearch G ≤ pathwidth G + 2 := by
  rw [← vertexSeparation_eq_pathwidth]
  exact vertexSeparation_le_edgeSearch_le_add_two G

/-- **[10] p. 209, full games**: `ns − 1 ≤ es ≤ ns + 1` on a graph with an edge. -/
theorem nodeSearch_sub_one_le_edgeSearch_le_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G - 1 ≤ edgeSearch G ∧ edgeSearch G ≤ nodeSearch G + 1 := by
  rw [nodeSearch_eq_vertexSeparation_add_one G h₀, Nat.add_sub_cancel]
  exact ⟨vertexSeparation_le_edgeSearch G, edgeSearch_le_vertexSeparation_add_two G⟩

/-- Recontamination saves at most two searchers in the edge game:
`s(G) ≤ ps(G) ≤ s(G) + 2`. What LaPaugh (1993) proves, `s = ps`, is not
reached by this argument and stays the named gap `EdgeSearchMonotonicity`. -/
theorem edgeSearch_le_progressiveEdgeSearch_le_add_two :
    edgeSearch G ≤ progressiveEdgeSearch G ∧
      progressiveEdgeSearch G ≤ edgeSearch G + 2 :=
  ⟨edgeSearch_le_progressiveEdgeSearch G,
    (progressiveEdgeSearch_le_vertexSeparation_add_two G).trans
      (Nat.add_le_add_right (vertexSeparation_le_edgeSearch G) 2)⟩

end Complex

end MOSPFormalization
