/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The customer search in pathwidth language

Section 4.7 of `paper1/revised_algorithm.md` (loop0008 item 03). The search of
`Basic.lean` is stated in MOSP words: closed customers, opened stacks. This file proves
the dictionary to the words of the exact pathwidth literature, so that each rule can be
read as a statement about vertex layouts, and identifies the repaired definite move with
a known theorem.

## The dictionary

For a set `T` of vertices, `boundary G T` is `N(T)`, the vertices outside `T` with a
neighbour in `T`: the *border* of Coudert, Mazauric & Nisse (SEA 2014, p. 48) and the
`N(X)` of Kobayashi, Komuro & Tamaki (SEA 2014, p. 390), whose `d(X) = |N(X)|`.

* `opened_sdiff_eq_boundary`, `openStacks_eq_card_boundary`: `O(T) ∖ T = N(T)`, so the
  open stacks after `T` are `b(T) = d(T)`.
* `opened_eq_union_boundary`: `O(T) = N[T] = T ∪ N(T)`.
* `stepCost_eq_card_boundary_add_one`: closing `c ∉ T` costs `d(T ∪ {c}) + 1`. A closing
  order is a vertex sequence, read forwards, and its cost is `1 +` the largest `d` of a
  prefix: the vertex sequences of Kobayashi et al. and Kitsunai et al., where `σ` is
  `k`-feasible when every prefix has `d ≤ k`. So `P_k(T)` says that `T` extends to a
  `(k − 1)`-feasible permutation, counting only the prefixes that contain `T`.
* `mem_cl_iff`: `cl(T)` is the *full set* of `T` (Suchan & Villanger, IWPEC 2009, p. 328:
  `U* = N[U] ∖ N(Ũ)`, the vertices of `N[U]` with no neighbour outside `N[U]`;
  Kitsunai et al., Algorithmica 2016, p. 143, `fullset(U)`).

## The commitment lemma

`IsCommittable G S T` is Tamaki's condition (WG 2011, as restated with proof by Kitsunai,
Kobayashi, Komuro, Tamaki & Tano, Algorithmica 75 (2016), §3, p. 142): `S ⊆ T`, and every
`X` with `S ⊆ X ⊆ T` has `d(X) ≥ d(T)`.

* `solvable_of_committable` — **the commitment lemma** (their Lemma 1): if `T` is
  committable from `S`, then `P_k(S) → P_k(T)`. The proof is theirs, by submodularity of
  `d` (`openStacks_submodular`, their Proposition 1), and needs no feasibility of the
  extension itself, because `P_k` counts only the steps after its argument.
* `isHereditarilyDefinite_iff_isCommittable` — **the repaired definite move is a
  commitment**: `q` is hereditarily definite at `S` iff the child `cl(S ∪ {q})` is
  committable from `S`. The sets `X ∋ q` that the repair leaves out satisfy the condition
  automatically. So `solvable_cl_insert_of_hereditarilyDefinite` (Theorem 4.7) is the
  commitment lemma at `T = cl(S ∪ {q})` (`solvable_cl_insert_of_hereditarilyDefinite'`).
* `isDefinite_iff_endpoint` — **the published definite move checks the commitment
  condition at `X = S` only**, and `cex_isDefinite_not_isCommittable` is a state where the
  endpoint test passes and the commitment fails (Counterexample 4.5).
* `exists_isCommittable_of_isDefinite` — **the published premise does guarantee a
  commitment, to another set**: if `d(cl(S ∪ {q})) ≤ d(S)`, a set of least border strictly
  between `S` and the child (or the child) is committable (Kitsunai et al. 2016, Lemma 10 and
  Corollary 2, pp. 148–149). In Counterexample 4.5 it is `{2, 3, 4}`
  (`cex_isCommittable_234`). The published rule's error is the target, not the premise.
* `isCommittable_insert_iff` — the **depth-1 commitments** of Kobayashi et al. (SEA 2014,
  §4.2, p. 392), `T = S ∪ {q}`, are exactly the moves with `open(q, S) ≤ 1`, the case the
  published rule gets right (`isHereditarilyDefinite_of_openCount_le_one`).
* `isGreedyStep_iff` — the **greedy step** of Coudert, Mazauric & Nisse (SEA 2014,
  Lemma 3, p. 49; JEA 2016, Lemma 6), undirected: `N(v) ⊆ S ∪ N(S)`, or `v ∈ N(S)` and
  `N(v) ∖ (S ∪ N(S))` is one vertex. For `v ∉ S` it is again `open(v, S) ≤ 1`.
-/

import MOSPFormalization.Search.DefiniteMove

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### The dictionary -/

/-- `N(T)`: the vertices outside `T` with a neighbour in `T` (the border of a prefix). -/
def boundary (T : Finset V) : Finset V :=
  univ.filter (fun v => v ∉ T ∧ ∃ u ∈ T, G.Adj u v)

/-- Tamaki's commitment condition: `S ⊆ T`, and no set between `S` and `T` has a smaller
border than `T`. -/
def IsCommittable (S T : Finset V) : Prop :=
  S ⊆ T ∧ ∀ X : Finset V, S ⊆ X → X ⊆ T → openStacks G T ≤ openStacks G X

/-- The greedy step of Coudert, Mazauric & Nisse, for a symmetric digraph: every
neighbour of `v` is in `S ∪ N(S)`, or `v ∈ N(S)` and exactly one neighbour of `v` is outside
`S ∪ N(S)`. -/
def IsGreedyStep (S : Finset V) (v : V) : Prop :=
  (∀ w, G.Adj v w → w ∈ opened G S) ∨
    (v ∈ boundary G S ∧ ∃ w, univ.filter (fun x => G.Adj v x ∧ x ∉ opened G S) = {w})

variable {G}

theorem mem_boundary {T : Finset V} {v : V} :
    v ∈ boundary G T ↔ v ∉ T ∧ ∃ u ∈ T, G.Adj u v := by
  simp [boundary]

/-- `O(T) ∖ T = N(T)`. -/
theorem opened_sdiff_eq_boundary (T : Finset V) : opened G T \ T = boundary G T := by
  ext v
  rw [Finset.mem_sdiff, mem_boundary, mem_opened]
  constructor
  · rintro ⟨⟨c, hc, hv⟩, hvT⟩
    rcases mem_nbhd.1 hv with rfl | hadj
    · exact absurd hc hvT
    · exact ⟨hvT, c, hc, hadj⟩
  · rintro ⟨hvT, u, hu, hadj⟩
    exact ⟨⟨u, hu, mem_nbhd.2 (Or.inr hadj)⟩, hvT⟩

/-- The open stacks after `T` are its border: `b(T) = d(T) = |N(T)|`. -/
theorem openStacks_eq_card_boundary (T : Finset V) :
    openStacks G T = (boundary G T).card := by
  unfold openStacks
  rw [opened_sdiff_eq_boundary]

/-- `O(T) = N[T] = T ∪ N(T)`. -/
theorem opened_eq_union_boundary (T : Finset V) : opened G T = T ∪ boundary G T := by
  rw [← opened_sdiff_eq_boundary, Finset.union_sdiff_of_subset (subset_opened T)]

/-- Closing `c ∉ T` costs the border of the new prefix, plus one. -/
theorem stepCost_eq_card_boundary_add_one {T : Finset V} {c : V} (hc : c ∉ T) :
    stepCost G T c = (boundary G (insert c T)).card + 1 := by
  rw [stepCost_eq_openStacks_insert_add_one hc, openStacks_eq_card_boundary]

/-- `cl(T)` is the full set of `T`: the vertices of `N[T]` with no neighbour outside
`N[T]`. -/
theorem mem_cl_iff {T : Finset V} {v : V} :
    v ∈ cl G T ↔ v ∈ T ∪ boundary G T ∧ ∀ w, G.Adj v w → w ∈ T ∪ boundary G T := by
  rw [← opened_eq_union_boundary, cl, mem_finished]
  constructor
  · intro h
    exact ⟨h (self_mem_nbhd v), fun w hw => h (mem_nbhd.2 (Or.inr hw))⟩
  · rintro ⟨hv, hw⟩ x hx
    rcases mem_nbhd.1 hx with rfl | hadj
    · exact hv
    · exact hw x hadj

/-! ### The commitment lemma -/

theorem solvable_union_of_isCommittable {k : ℕ} {S T : Finset V} (h : IsCommittable G S T) :
    ∀ (l : List V) (U : Finset V), S ⊆ U → IsClosingOrder U l → orderCost G U l ≤ k →
      Solvable G k (U ∪ T) := by
  intro l
  induction l with
  | nil =>
    intro U _ hl _
    rw [isClosingOrder_nil_iff.1 hl, Finset.union_eq_left.2 (Finset.subset_univ _)]
    exact ⟨[], isClosingOrder_nil_iff.2 rfl, Nat.zero_le _⟩
  | cons c l ih =>
    intro U hSU hl hcost
    obtain ⟨hcU, hl'⟩ := IsClosingOrder.cons_iff.1 hl
    rw [orderCost_cons] at hcost
    have hc1 : stepCost G U c ≤ k := le_trans (le_max_left _ _) hcost
    have hc2 : orderCost G (insert c U) l ≤ k := le_trans (le_max_right _ _) hcost
    have hrest := ih (insert c U) (hSU.trans (Finset.subset_insert _ _)) hl' hc2
    by_cases hcT : c ∈ T
    · rwa [Finset.insert_union, Finset.insert_eq_of_mem (Finset.mem_union_right _ hcT)]
        at hrest
    · rw [Finset.insert_union] at hrest
      have hc' : c ∉ U ∪ T := by simp [hcU, hcT]
      refine solvable_of_solvable_insert hc' (le_trans ?_ hc1) hrest
      rw [stepCost_eq_openStacks_insert_add_one hcU, stepCost_eq_openStacks_insert_add_one hc']
      have hsub := openStacks_submodular (G := G) (insert c U) T
      have hX : openStacks G T ≤ openStacks G (insert c U ∩ T) :=
        h.2 _ (Finset.subset_inter (hSU.trans (Finset.subset_insert _ _)) h.1)
          Finset.inter_subset_right
      rw [← Finset.insert_union]
      omega

/-- **The commitment lemma** (Tamaki 2011; Kitsunai et al. 2016, Lemma 1): a committable
extension of a solvable set is solvable. -/
theorem solvable_of_isCommittable {k : ℕ} {S T : Finset V} (h : IsCommittable G S T)
    (hs : Solvable G k S) : Solvable G k T := by
  obtain ⟨l, hl, hc⟩ := hs
  have := solvable_union_of_isCommittable h l S le_rfl hl hc
  rwa [Finset.union_eq_right.2 h.1] at this

/-- **The repaired definite move is a commitment**: `q` is hereditarily definite at `S` iff
the child `cl(S ∪ {q})` is a committable extension of `S`. -/
theorem isHereditarilyDefinite_iff_isCommittable (S : Finset V) (q : V) :
    IsHereditarilyDefinite G S q ↔ IsCommittable G S (cl G (insert q S)) := by
  constructor
  · intro h
    refine ⟨subset_cl_insert S q, fun X hSX hXT => ?_⟩
    by_cases hqX : q ∈ X
    · have h1 : opened G X ⊆ opened G (cl G (insert q S)) := opened_mono hXT
      have h2 : opened G (cl G (insert q S)) ⊆ opened G X := by
        rw [opened_cl]
        exact opened_mono (Finset.insert_subset hqX hSX)
      have heq := Finset.Subset.antisymm h1 h2
      have a1 := openStacks_add_card (G := G) (cl G (insert q S))
      have a2 := openStacks_add_card (G := G) X
      have a3 := Finset.card_le_card hXT
      rw [← heq] at a1
      omega
    · exact h X hSX hXT hqX
  · rintro ⟨_, h⟩ X hSX hXT _
    exact h X hSX hXT

/-- Theorem 4.7 again, as the commitment lemma at `T = cl(S ∪ {q})`. -/
theorem solvable_cl_insert_of_hereditarilyDefinite' {k : ℕ} {S : Finset V} {q : V}
    (h : IsHereditarilyDefinite G S q) (hs : Solvable G k S) :
    Solvable G k (cl G (insert q S)) :=
  solvable_of_isCommittable ((isHereditarilyDefinite_iff_isCommittable S q).1 h) hs

/-- **The published definite move checks the commitment condition at the endpoint
`X = S` only.** (A restatement of `isDefinite_iff` in border terms.) -/
theorem isDefinite_iff_endpoint (S : Finset V) (q : V) :
    IsDefinite G S q ↔
      (boundary G (cl G (insert q S))).card ≤ (boundary G S).card := by
  rw [isDefinite_iff, openStacks_eq_card_boundary, openStacks_eq_card_boundary]

/-- **Depth-1 commitments are the moves that open at most one new stack.** -/
theorem isCommittable_insert_iff {S : Finset V} {q : V} (hq : q ∉ S) :
    IsCommittable G S (insert q S) ↔ openCount G S q ≤ 1 := by
  have e1 := openStacks_add_card (G := G) (insert q S)
  have e2 := openStacks_add_card (G := G) S
  have e3 := card_opened_insert (G := G) S q
  have e4 := Finset.card_insert_of_notMem hq
  constructor
  · rintro ⟨_, h⟩
    have := h S le_rfl (Finset.subset_insert _ _)
    omega
  · intro h
    refine ⟨Finset.subset_insert _ _, fun X hSX hXT => ?_⟩
    by_cases hqX : q ∈ X
    · have : X = insert q S := Finset.Subset.antisymm hXT (Finset.insert_subset hqX hSX)
      subst this
      exact le_rfl
    · have : X = S := by
        refine Finset.Subset.antisymm (fun x hx => ?_) hSX
        rcases Finset.mem_insert.1 (hXT hx) with rfl | hxS
        · exact absurd hx hqX
        · exact hxS
      subst this
      omega

/-- **The greedy step of Coudert, Mazauric & Nisse is `open(v, S) ≤ 1`.** -/
theorem isGreedyStep_iff {S : Finset V} {v : V} (hv : v ∉ S) :
    IsGreedyStep G S v ↔ openCount G S v ≤ 1 := by
  unfold IsGreedyStep openCount newlyOpened
  rw [Finset.card_le_one]
  constructor
  · rintro (hall | ⟨hvb, w, hw⟩) a ha b hb
    · -- every new stack is `v` itself
      have key : ∀ x ∈ nbhd G v \ opened G S, x = v := by
        intro x hx
        obtain ⟨hxn, hxo⟩ := Finset.mem_sdiff.1 hx
        rcases mem_nbhd.1 hxn with rfl | hadj
        · rfl
        · exact absurd (hall x hadj) hxo
      rw [key a ha, key b hb]
    · -- every new stack is `w`
      have hvo : v ∈ opened G S := by
        rw [opened_eq_union_boundary]
        exact Finset.mem_union_right _ hvb
      have key : ∀ x ∈ nbhd G v \ opened G S, x = w := by
        intro x hx
        obtain ⟨hxn, hxo⟩ := Finset.mem_sdiff.1 hx
        rcases mem_nbhd.1 hxn with rfl | hadj
        · exact absurd hvo hxo
        · have : x ∈ univ.filter (fun x => G.Adj v x ∧ x ∉ opened G S) := by
            simp [hadj, hxo]
          rw [hw] at this
          exact Finset.mem_singleton.1 this
      rw [key a ha, key b hb]
  · intro h
    by_cases hvo : v ∈ opened G S
    · by_cases hall : ∀ w, G.Adj v w → w ∈ opened G S
      · exact Or.inl hall
      · simp only [not_forall] at hall
        obtain ⟨w, hadj, hwo⟩ := hall
        refine Or.inr ⟨?_, w, ?_⟩
        · rw [← opened_sdiff_eq_boundary]
          exact Finset.mem_sdiff.2 ⟨hvo, hv⟩
        · ext x
          simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_singleton]
          constructor
          · rintro ⟨hx, hxo⟩
            exact h x (Finset.mem_sdiff.2 ⟨mem_nbhd.2 (Or.inr hx), hxo⟩)
              w (Finset.mem_sdiff.2 ⟨mem_nbhd.2 (Or.inr hadj), hwo⟩)
          · rintro rfl
            exact ⟨hadj, hwo⟩
    · left
      intro w hadj
      by_contra hwo
      have := h v (Finset.mem_sdiff.2 ⟨self_mem_nbhd v, hvo⟩)
        w (Finset.mem_sdiff.2 ⟨mem_nbhd.2 (Or.inr hadj), hwo⟩)
      exact G.irrefl (this ▸ hadj)

/-- **The published premise does guarantee a commitment, but not to the child.** If
`d(cl(S ∪ {q})) ≤ d(S)`, a set `W` of least border between `S` and the child, other than `S`,
is a committable extension of `S` (Kitsunai et al. 2016, Lemma 10 and Corollary 2,
pp. 148–149, which also find `W` by a minimum `s`–`t` separator). Chu & Stuckey's
Theorem 1 commits to the child instead. -/
theorem exists_isCommittable_of_isDefinite {S : Finset V} {q : V} (hq : q ∉ S)
    (h : IsDefinite G S q) :
    ∃ W, S ⊂ W ∧ W ⊆ cl G (insert q S) ∧ IsCommittable G S W := by
  have hd := (isDefinite_iff S q).1 h
  have hXS : cl G (insert q S) ≠ S := fun e => hq (e ▸ mem_cl_insert_self S q)
  set X := cl G (insert q S) with hXdef
  set F := X.powerset.filter (fun B => S ⊆ B ∧ B ≠ S) with hF
  have hXF : X ∈ F := by
    rw [hF, Finset.mem_filter, Finset.mem_powerset]
    exact ⟨le_rfl, subset_cl_insert S q, hXS⟩
  obtain ⟨W, hWF, hmin⟩ := Finset.exists_min_image F (openStacks G) ⟨X, hXF⟩
  rw [hF, Finset.mem_filter, Finset.mem_powerset] at hWF
  obtain ⟨hWX, hSW, hWS⟩ := hWF
  refine ⟨W, Finset.ssubset_iff_subset_ne.2 ⟨hSW, Ne.symm hWS⟩, hWX, hSW, fun B hSB hBW => ?_⟩
  by_cases hBS : B = S
  · subst hBS
    exact le_trans (hmin X hXF) hd
  · refine hmin B ?_
    rw [hF, Finset.mem_filter, Finset.mem_powerset]
    exact ⟨hBW.trans hWX, hSB, hBS⟩

/-! ### The counterexample in these terms -/

/-- At the state of Counterexample 4.5 the endpoint test passes and the child is not
committable: the published rule commits where Tamaki's condition forbids it. -/
theorem cex_isDefinite_not_isCommittable :
    IsDefinite cexGraph {2} 0 ∧ ¬ IsCommittable cexGraph {2} (cl cexGraph (insert 0 {2})) :=
  ⟨definiteMove_counterexample.2.2.2.2.1,
    fun h => not_isHereditarilyDefinite_cex
      ((isHereditarilyDefinite_iff_isCommittable _ _).2 h)⟩

/-- In Counterexample 4.5 the set `W` of `exists_isCommittable_of_isDefinite` is `{2, 3, 4}`:
it is committable from `{2}`, with border `2` against the child's `3`. -/
theorem cex_isCommittable_234 :
    IsCommittable cexGraph {2} {2, 3, 4} ∧ openStacks cexGraph {2, 3, 4} = 2 ∧
      openStacks cexGraph (cl cexGraph (insert 0 {2})) = 3 := by
  refine ⟨⟨by decide, fun X hSX hXW => ?_⟩, by decide, by rw [cex_cl_insert]; decide⟩
  have hX : X ∈ ({2, 3, 4} : Finset (Fin 14)).powerset := Finset.mem_powerset.2 hXW
  revert hSX
  revert X
  decide

end Search

end MOSPFormalization
