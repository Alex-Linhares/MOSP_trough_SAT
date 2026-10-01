/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The repaired definite move is a matching condition (Hall's theorem with deficiency)

Loop0006 item 13 (reserve), closing the open half of item 08 (`paper2/search_soundness.md`
§4.2 and §4.6). `DefiniteMove.lean` proves the repair `IsHereditarilyDefinite G S q` sound and
proves one direction of its cheap form, `isHereditarilyDefinite_of_matching`. This file proves
the converse, so the two are **equivalent**.

Write `X = cl(S ∪ {q})` for the child, `Y = X ∖ (S ∪ {q})` for the customers it closes beyond
`q`, `o(d) = o(d, S) = N[d] ∖ O(S)` and `o(D) = ⋃_{d ∈ D} o(d)`.

## What is proved

* `card_opened_union_eq` — `|O(S ∪ D)| = |O(S)| + |o(D)|`.
* `hall_of_isHereditarilyDefinite` — the deficiency form of the repair: for `q ∉ S`, if `q` is
  hereditarily definite then every `D ⊆ Y` has `open(q, S) + |D| ≤ |o(D)| + |Y| + 1`. (This is
  the repair at `B = S ∪ D`, with the cardinalities of `O` and of the child written out.)
* `exists_matching_of_isHereditarilyDefinite` — **the converse of
  `isHereditarilyDefinite_of_matching`**: a hereditarily definite `q` has a matching of at least
  `open(q, S) − 1` customers of `Y` to distinct stacks `f d ∈ o(d, S)`. The proof is Hall's
  theorem with deficiency, by the textbook reduction: give every `d ∈ Y` the same
  `δ = |Y| + 1 − open(q, S)` dummy stacks besides `o(d)`, check Hall's condition from the
  deficiency form, apply Mathlib's `Finset.all_card_le_biUnion_card_iff_existsInjective'`, and
  keep the customers matched to real stacks; at most `δ` were matched to dummies.
* **`isHereditarilyDefinite_iff_hasDefiniteMatching`** — `IsHereditarilyDefinite G S q ↔
  HasDefiniteMatching G S q`, for every `S` and `q` (no invariant, no free-closedness).

So the test a fixed solver (and a strengthened certificate checker) would compute — one maximum
bipartite matching of `Y` against `o(q, S)`, compared with `open(q, S) − 1` — is a proved
equivalent of the premise under which the definite move is proved sound, not merely a
sufficient condition.

## Checks

`python -m paper2.search_check --hall` checks the deficiency form, the matching form and the
repair against one another by brute force; see `paper2/search_soundness.md` §4.6.
-/

import MOSPFormalization.Search.DefiniteMove
import Mathlib.Combinatorics.Hall.Finite

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The matching form of the repaired definite move: `open(q, S) − 1` customers the child
closes beyond `q` are matched to distinct stacks among their own new stacks. -/
def HasDefiniteMatching (S : Finset V) (q : V) : Prop :=
  ∃ (M : Finset V) (f : V → V), M ⊆ cl G (insert q S) \ insert q S ∧
    (∀ d ∈ M, f d ∈ newlyOpened G S d) ∧ Set.InjOn f M ∧ openCount G S q ≤ M.card + 1

variable {G}

/-- `O(S ∪ D)` is `O(S)` together with the new stacks of `D`, disjointly. -/
theorem card_opened_union_eq (S D : Finset V) :
    (opened G (S ∪ D)).card = (opened G S).card + (D.biUnion (newlyOpened G S)).card := by
  have h : D.biUnion (newlyOpened G S) = opened G D \ opened G S := by
    ext y
    simp only [mem_biUnion, newlyOpened, mem_sdiff, mem_opened]
    constructor
    · rintro ⟨d, hd, hy, hyS⟩
      exact ⟨⟨d, hd, hy⟩, hyS⟩
    · rintro ⟨⟨d, hd, hy⟩, hyS⟩
      exact ⟨d, hd, hy, hyS⟩
  rw [opened_union, h, ← Finset.card_union_of_disjoint Finset.disjoint_sdiff,
    Finset.union_sdiff_self_eq_union]

/-- `q ∈ S` opens nothing new. -/
theorem openCount_eq_zero_of_mem {S : Finset V} {q : V} (hq : q ∈ S) : openCount G S q = 0 := by
  unfold openCount newlyOpened
  rw [Finset.card_eq_zero, Finset.sdiff_eq_empty_iff_subset]
  exact fun y hy => mem_opened.2 ⟨q, hq, hy⟩

/-- The child has `|S| + 1 + |Y|` customers. -/
theorem card_cl_insert {S : Finset V} {q : V} (hq : q ∉ S) :
    (cl G (insert q S)).card = S.card + 1 + (cl G (insert q S) \ insert q S).card := by
  have := Finset.card_sdiff_add_card_eq_card (subset_cl (G := G) (insert q S))
  rw [Finset.card_insert_of_notMem hq] at this
  omega

/-- **The deficiency form of the repair.** -/
theorem hall_of_isHereditarilyDefinite {S : Finset V} {q : V} (h : IsHereditarilyDefinite G S q)
    (hq : q ∉ S) (D : Finset V) (hD : D ⊆ cl G (insert q S) \ insert q S) :
    openCount G S q + D.card ≤
      (D.biUnion (newlyOpened G S)).card + (cl G (insert q S) \ insert q S).card + 1 := by
  have hDX : D ⊆ cl G (insert q S) := hD.trans Finset.sdiff_subset
  have hDS : Disjoint S D := by
    rw [Finset.disjoint_right]
    intro d hd hdS
    exact (Finset.mem_sdiff.1 (hD hd)).2 (Finset.mem_insert_of_mem hdS)
  have hqD : q ∉ D := fun h' => (Finset.mem_sdiff.1 (hD h')).2 (Finset.mem_insert_self _ _)
  have hB := h (S ∪ D) Finset.subset_union_left
    (Finset.union_subset (subset_cl_insert S q) hDX)
    (by simp [hq, hqD])
  have h1 := openStacks_add_card (G := G) (cl G (insert q S))
  have h2 := openStacks_add_card (G := G) (S ∪ D)
  have h3 := card_opened_insert (G := G) S q
  have h4 := card_opened_union_eq (G := G) S D
  have h5 := card_cl_insert (G := G) hq
  have h6 := Finset.card_union_of_disjoint hDS
  rw [opened_cl] at h1
  omega

/-- **Hall's converse**: a hereditarily definite `q` has the matching. -/
theorem exists_matching_of_isHereditarilyDefinite {S : Finset V} {q : V}
    (h : IsHereditarilyDefinite G S q) : HasDefiniteMatching G S q := by
  by_cases hq : q ∈ S
  · exact ⟨∅, id, Finset.empty_subset _, by simp, by simp,
      by rw [openCount_eq_zero_of_mem hq]; omega⟩
  have hall := hall_of_isHereditarilyDefinite h hq
  -- `D = ∅`: the open count is at most `|Y| + 1`, so `δ` loses nothing to truncation.
  have hY := hall ∅ (Finset.empty_subset _)
  simp only [Finset.card_empty, Finset.biUnion_empty, add_zero] at hY
  set Y := cl G (insert q S) \ insert q S with hYdef
  set δ := Y.card + 1 - openCount G S q with hδ
  have hδ' : δ + openCount G S q = Y.card + 1 := by omega
  let t : Y → Finset (V ⊕ Fin δ) := fun d => (newlyOpened G S d.1).disjSum univ
  have hcond : ∀ s : Finset Y, s.card ≤ (s.biUnion t).card := by
    intro s
    rcases s.eq_empty_or_nonempty with rfl | ⟨d₀, hd₀⟩
    · simp
    set D := s.map (Function.Embedding.subtype _) with hDdef
    have hDY : D ⊆ Y := by
      intro d hd
      obtain ⟨e, _, rfl⟩ := Finset.mem_map.1 hd
      exact e.2
    have hsub : (D.biUnion (newlyOpened G S)).disjSum (univ : Finset (Fin δ)) ⊆ s.biUnion t := by
      intro x hx
      rcases x with y | i
      · obtain ⟨d, hd, hy⟩ := Finset.mem_biUnion.1 (Finset.inl_mem_disjSum.1 hx)
        obtain ⟨e, he, rfl⟩ := Finset.mem_map.1 hd
        exact Finset.mem_biUnion.2 ⟨e, he, Finset.inl_mem_disjSum.2 hy⟩
      · exact Finset.mem_biUnion.2 ⟨d₀, hd₀, Finset.inr_mem_disjSum.2 (Finset.mem_univ _)⟩
    have hc := Finset.card_le_card hsub
    rw [Finset.card_disjSum, Finset.card_univ, Fintype.card_fin] at hc
    have hD := hall D hDY
    have hDc : D.card = s.card := Finset.card_map _
    omega
  obtain ⟨F, hFinj, hFmem⟩ :=
    (Finset.all_card_le_biUnion_card_iff_existsInjective' t).1 hcond
  -- Extend `F` to all of `V`, and keep the customers matched to real stacks.
  let g : V → V ⊕ Fin δ := fun d => if hd : d ∈ Y then F ⟨d, hd⟩ else Sum.inl d
  let f : V → V := fun d => (g d).elim id (fun _ => d)
  let M := Y.filter (fun d => (g d).isLeft)
  have hgM : ∀ d ∈ M, g d = Sum.inl (f d) := by
    intro d hd
    have := (Finset.mem_filter.1 hd).2
    simp only [f]
    rcases hgd : g d with y | i
    · rfl
    · rw [hgd] at this; simp at this
  have hgY : ∀ d (hd : d ∈ Y), g d = F ⟨d, hd⟩ := fun d hd => by simp [g, hd]
  refine ⟨M, f, Finset.filter_subset _ _, ?_, ?_, ?_⟩
  · intro d hd
    have hdY := (Finset.mem_filter.1 hd).1
    have := hFmem ⟨d, hdY⟩
    rw [← hgY d hdY, hgM d hd] at this
    exact Finset.inl_mem_disjSum.1 this
  · intro d₁ hd₁ d₂ hd₂ heq
    have hY₁ := (Finset.mem_filter.1 (Finset.mem_coe.1 hd₁)).1
    have hY₂ := (Finset.mem_filter.1 (Finset.mem_coe.1 hd₂)).1
    have : g d₁ = g d₂ := by rw [hgM d₁ hd₁, hgM d₂ hd₂, heq]
    rw [hgY d₁ hY₁, hgY d₂ hY₂] at this
    exact congrArg Subtype.val (hFinj this)
  · -- At most `δ` customers of `Y` are matched to dummies.
    have hdummy : (Y.filter (fun d => ¬ (g d).isLeft)).card ≤ δ := by
      have := Finset.card_le_card_of_injOn g
        (t := (∅ : Finset V).disjSum (univ : Finset (Fin δ))) (s := Y.filter (fun d => ¬ (g d).isLeft))
        (by
          intro d hd
          have := (Finset.mem_filter.1 (Finset.mem_coe.1 hd)).2
          rcases hgd : g d with y | i
          · rw [hgd] at this; simp at this
          · exact Finset.mem_coe.2 (Finset.inr_mem_disjSum.2 (Finset.mem_univ _)))
        (by
          intro d₁ hd₁ d₂ hd₂ heq
          have hY₁ := (Finset.mem_filter.1 (Finset.mem_coe.1 hd₁)).1
          have hY₂ := (Finset.mem_filter.1 (Finset.mem_coe.1 hd₂)).1
          rw [hgY d₁ hY₁, hgY d₂ hY₂] at heq
          exact congrArg Subtype.val (hFinj heq))
      rwa [Finset.card_disjSum, Finset.card_empty, Finset.card_univ, Fintype.card_fin,
        zero_add] at this
    have hsplit := Finset.card_filter_add_card_filter_not (s := Y)
      (fun d => (g d).isLeft = true)
    have hMc : M.card = (Y.filter (fun d => (g d).isLeft = true)).card := rfl
    omega

/-- **The repaired definite move is exactly the matching condition.** -/
theorem isHereditarilyDefinite_iff_hasDefiniteMatching (S : Finset V) (q : V) :
    IsHereditarilyDefinite G S q ↔ HasDefiniteMatching G S q := by
  refine ⟨exists_matching_of_isHereditarilyDefinite, ?_⟩
  rintro ⟨M, f, hM, hf, hinj, hcard⟩
  exact isHereditarilyDefinite_of_matching M f hM hf hinj hcard

end Search

end MOSPFormalization
