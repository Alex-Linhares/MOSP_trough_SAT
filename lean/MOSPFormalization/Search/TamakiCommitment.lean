/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Tamaki's commitment lemma, in Tamaki's own terms, and its relation to the corrected
# definite move

Source: Kitsunai, Kobayashi, Komuro, Tamaki & Tano, *Computing directed pathwidth in
O(1.89ⁿ) time*, Algorithmica 75 (2016) 138–157, §2 (pp. 141–142) and §3 (p. 142), which
restates with proof the notion Tamaki introduced for his XP algorithm (WG 2011, [25]
there). The undirected form, without proof, is Kobayashi, Komuro & Tamaki, SEA 2014,
LNCS 8504, §2–§3 (pp. 390–391).

The question this file answers: is the corrected definite move,
`solvable_cl_insert_of_hereditarilyDefinite` (`DefiniteMove.lean`), *the same theorem* as
their Lemma 1, or does it differ? `Layout.lean` already identified the two through a
set-form `IsCommittable` written in our vocabulary. Here the lemma is transcribed in
**their** vocabulary — digraphs, in-neighbours, vertex sequences, prefixes, `k`-feasible
and strongly `k`-feasible sequences, `k`-committable extensions — proved as printed, and
then related to our theorem formally.

## Their definitions (p. 141–142), transcribed

* `N⁻(v) = {u ∈ V(G) ∖ {v} | (u, v) ∈ E(G)}`; `N⁻(U) = ⋃_{v ∈ U} N⁻(v) ∖ U`;
  `d⁻(U) = |N⁻(U)|` — `inNbrs`, `inNbrsSet`, `inDeg`.
* A sequence `σ` of vertices has no repetition (their standing convention); `V(σ)` is its
  set of vertices; `σ` is a *prefix* of `τ` and `τ` an *extension* of `σ` if `τ = σ τ'`,
  *proper* if `τ'` is nonempty — `List V`, `List.toFinset`, `<+:`, `σ ≠ τ`.
* `σ` is *`k`-feasible* if `d⁻(σ') ≤ k` for every prefix `σ'` of `σ` — `KFeasible`.
* `σ` is *strongly `k`-feasible* if it is a prefix of a `k`-feasible permutation —
  `StronglyKFeasible`.
* Let `σ` be `k`-feasible and `τ` a `k`-feasible proper extension of `σ`; `τ` is a
  *`k`-committable extension* of `σ` if `d⁻(X) ≥ d⁻(τ)` for every `X` with
  `V(σ) ⊆ X ⊆ V(τ)` — `IsCommittableExt`.

## Their Lemma 1 (Commitment Lemma [25]), as printed on p. 142

> Let `G` be a digraph and `k` a positive integer. Let `σ` be a `k`-feasible sequence and
> let `τ` be a `k`-committable extension of `σ`. If `σ` is strongly `k`-feasible then so
> is `τ`.

`lemma1` is this statement for an arbitrary digraph (Mathlib's `Digraph`, loops allowed
and ignored, as `N⁻(v)` excludes `v`), proved by their argument: submodularity of `d⁻`
(their Proposition 1, `inDeg_submodular`) applied prefix by prefix (`inDeg_union_le_of_prefix`).
The hypothesis `k > 0` plays no part and is dropped.

## The relation to the corrected definite move

For an undirected `G` read as the symmetric digraph `symm G` (their `Ĝ`, p. 139):

* `inDeg_symm`: `d⁻(U) = b(U)`, the open stacks; `stronglyKFeasible_symm_iff`: `τ` is
  strongly `w`-feasible iff `τ` is `w`-feasible and `P_{w+1}(V(τ))` — the suffix part of
  their notion is our `Solvable`, with the shift `k = w + 1` (a step cost counts the
  customer being closed).
* `isCommittableExt_symm_iff_hereditarilyDefinite`: for `V(σ) = S` and `V(τ) = cl(S ∪ {q})`
  with `τ` a `w`-feasible extension of `σ`, **`τ` is a `w`-committable extension of `σ` iff
  `q` is hereditarily definite at `S`**. Our premise is theirs.
* `stronglyKFeasible_child_of_hereditarilyDefinite`: their Lemma 1 at `V(τ) = cl(S ∪ {q})`
  on `symm G`, derived from our theorem alone. `lemma1_symm_of_isCommittable`: their
  Lemma 1 on `symm G` for *every* extension, derived from `Layout.lean`'s set-form
  commitment lemma.
* `solvable_cl_insert_of_lemma1`: our theorem derived from their Lemma 1 used as a black
  box — **under two extra hypotheses**: `S` is `w`-feasible as a set (some `w`-feasible
  `σ` has `V(σ) = S`) and `q` is playable (`cost(S, q) ≤ w + 1`, which makes the path
  `σ, q, free moves` a `w`-feasible `τ`). Both hold at every node below the root of the
  search (the node was reached by playable moves and `q` is only ever tried when playable).
* `premise_gap`: the extra hypotheses are not redundant. On the five-vertex graph
  `0–1, 0–2, 0–3, 1–4` with `S = {0}`, `q = 2`, `k = 3` (so `w = 2`): `q` is hereditarily
  definite, playable, `P_3(S)` holds, and our theorem gives `P_3({0, 2, 3})`; but
  `d⁻({0}) = 3 > 2`, so no sequence with `V(σ) = {0}` is `2`-feasible and their Lemma 1 has
  no instance there. (The search never visits such a state: below the root `b(S) ≤ k − 1`.)

## Verdict

The corrected definite move is Tamaki's commitment lemma specialised three ways and
relaxed one way: the digraph is symmetric (undirected pathwidth, their special case,
p. 139); the extension is fixed to the child `cl(S ∪ {q})`; the commitment condition is
checked only on sets avoiding `q` (equivalent for that child,
`isHereditarilyDefinite_iff_isCommittable`); and the side conditions that `σ` and `τ` be
`w`-feasible are dropped, the conclusion then being `P_k`, the suffix half of
"strongly feasible". On the search's own states the two statements coincide.

Axioms: `propext`, `Classical.choice`, `Quot.sound` only (`paper1/axiom_check.lean`).
Sanity: every statement below was checked by brute force on random digraphs and graphs
with up to six vertices before it was proved (`lemma1` on 12,596 committable pairs, the
translation on 3,855 sequences, the child-case equivalence on 2,600 states).
-/

import Mathlib.Combinatorics.Digraph.Basic
import MOSPFormalization.Search.Layout

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

namespace Tamaki

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (D : Digraph V) [DecidableRel D.Adj]

/-! ### Their definitions -/

/-- `N⁻(v) = {u ∈ V(G) ∖ {v} | (u, v) ∈ E(G)}`, the in-neighbours of `v` (p. 141). -/
def inNbrs (v : V) : Finset V := univ.filter (fun u => u ≠ v ∧ D.Adj u v)

/-- `N⁻(U) = ⋃_{v ∈ U} N⁻(v) ∖ U` (p. 141). -/
def inNbrsSet (U : Finset V) : Finset V := U.biUnion (inNbrs D) \ U

/-- `d⁻(U) = |N⁻(U)|` (p. 141). -/
def inDeg (U : Finset V) : ℕ := (inNbrsSet D U).card

/-- A sequence `σ` of vertices, without repetition, is *`k`-feasible* if `d⁻(σ') ≤ k` for
every prefix `σ'` of `σ` (p. 141). `V(σ)` is `σ.toFinset`. -/
def KFeasible (k : ℕ) (σ : List V) : Prop :=
  σ.Nodup ∧ ∀ σ' : List V, σ' <+: σ → inDeg D σ'.toFinset ≤ k

/-- A sequence is a *permutation* if `V(σ) = V(G)` (p. 141). -/
def IsPermutation (η : List V) : Prop := η.Nodup ∧ ∀ v, v ∈ η

/-- `σ` is *strongly `k`-feasible* if it is a prefix of a `k`-feasible permutation
(p. 141). -/
def StronglyKFeasible (k : ℕ) (σ : List V) : Prop :=
  ∃ η : List V, IsPermutation η ∧ KFeasible D k η ∧ σ <+: η

/-- `τ` is a *`k`-committable extension* of `σ` (p. 142): `τ` is a `k`-feasible proper
extension of `σ`, and `d⁻(X) ≥ d⁻(τ)` for every `X` with `V(σ) ⊆ X ⊆ V(τ)`. (That `σ` is
`k`-feasible is the standing hypothesis of the paragraph and of Lemma 1, kept separate.) -/
def IsCommittableExt (k : ℕ) (σ τ : List V) : Prop :=
  KFeasible D k τ ∧ σ <+: τ ∧ σ ≠ τ ∧
    ∀ X : Finset V, σ.toFinset ⊆ X → X ⊆ τ.toFinset → inDeg D τ.toFinset ≤ inDeg D X

variable {D}

/-! ### Proposition 1: `d⁻` is submodular -/

/-- `U ∪ N⁻(U)`, written as one `biUnion` so that it is a union homomorphism. -/
def inClosure (U : Finset V) : Finset V := U.biUnion (fun v => insert v (inNbrs D v))

theorem inClosure_eq (U : Finset V) : inClosure (D := D) U = U ∪ U.biUnion (inNbrs D) := by
  ext x
  simp only [inClosure, Finset.mem_biUnion, Finset.mem_insert, Finset.mem_union]
  constructor
  · rintro ⟨v, hv, rfl | hx⟩
    · exact Or.inl hv
    · exact Or.inr ⟨v, hv, hx⟩
  · rintro (hx | ⟨v, hv, hx⟩)
    · exact ⟨x, hx, Or.inl rfl⟩
    · exact ⟨v, hv, Or.inr hx⟩

theorem subset_inClosure (U : Finset V) : U ⊆ inClosure (D := D) U := by
  rw [inClosure_eq]; exact Finset.subset_union_left

theorem inNbrsSet_eq_inClosure_sdiff (U : Finset V) :
    inNbrsSet D U = inClosure (D := D) U \ U := by
  rw [inClosure_eq, Finset.union_sdiff_left]; rfl

theorem inDeg_add_card (U : Finset V) : inDeg D U + U.card = (inClosure (D := D) U).card := by
  unfold inDeg
  rw [inNbrsSet_eq_inClosure_sdiff]
  exact Finset.card_sdiff_add_card_eq_card (subset_inClosure U)

theorem mem_inNbrs {u v : V} : u ∈ inNbrs D v ↔ u ≠ v ∧ D.Adj u v := by
  simp [inNbrs]

theorem inClosure_union (A B : Finset V) :
    inClosure (D := D) (A ∪ B) = inClosure (D := D) A ∪ inClosure (D := D) B := by
  ext x
  simp only [inClosure, Finset.mem_biUnion, Finset.mem_union]
  constructor
  · rintro ⟨v, hv | hv, hx⟩
    · exact Or.inl ⟨v, hv, hx⟩
    · exact Or.inr ⟨v, hv, hx⟩
  · rintro (⟨v, hv, hx⟩ | ⟨v, hv, hx⟩)
    · exact ⟨v, Or.inl hv, hx⟩
    · exact ⟨v, Or.inr hv, hx⟩

theorem inClosure_mono {A B : Finset V} (h : A ⊆ B) :
    inClosure (D := D) A ⊆ inClosure (D := D) B :=
  Finset.biUnion_subset_biUnion_of_subset_left _ h

theorem inClosure_inter_subset (A B : Finset V) :
    inClosure (D := D) (A ∩ B) ⊆ inClosure (D := D) A ∩ inClosure (D := D) B :=
  Finset.subset_inter (inClosure_mono Finset.inter_subset_left)
    (inClosure_mono Finset.inter_subset_right)

/-- **Proposition 1** (p. 141): `d⁻(X) + d⁻(Y) ≥ d⁻(X ∪ Y) + d⁻(X ∩ Y)`. -/
theorem inDeg_submodular (X Y : Finset V) :
    inDeg D (X ∪ Y) + inDeg D (X ∩ Y) ≤ inDeg D X + inDeg D Y := by
  have h1 := inDeg_add_card (D := D) (X ∪ Y)
  have h2 := inDeg_add_card (D := D) (X ∩ Y)
  have h3 := inDeg_add_card (D := D) X
  have h4 := inDeg_add_card (D := D) Y
  have h5 := Finset.card_union_add_card_inter X Y
  have h6 := Finset.card_union_add_card_inter (inClosure (D := D) X) (inClosure (D := D) Y)
  have h7 := Finset.card_le_card (inClosure_inter_subset (D := D) X Y)
  rw [inClosure_union] at h1
  omega

/-! ### Lemma 1, the Commitment Lemma -/

/-- The inductive core of their proof. `U` is the set of a prefix `η_i` of the given
permutation that extends `σ`; `l` is what follows; `T = V(τ)`. If every prefix of `l`
after `U` has `d⁻ ≤ k`, then so does every prefix of `l` with the vertices of `T` removed,
taken after `U ∪ T`. The step `c ∉ T` is submodularity at `(U ∪ {c}, T)` together with the
commitment condition at `(U ∪ {c}) ∩ T`. -/
theorem inDeg_union_le_of_prefix {k : ℕ} {S T : Finset V} (hST : S ⊆ T)
    (hcomm : ∀ X : Finset V, S ⊆ X → X ⊆ T → inDeg D T ≤ inDeg D X) :
    ∀ (l : List V) (U : Finset V), S ⊆ U → inDeg D (U ∪ T) ≤ k →
      (∀ p : List V, p <+: l → inDeg D (U ∪ p.toFinset) ≤ k) →
      ∀ p : List V, p <+: l.filter (fun c => c ∉ T) → inDeg D (U ∪ T ∪ p.toFinset) ≤ k := by
  intro l
  induction l with
  | nil =>
    intro U _ hUT _ p hp
    rw [List.filter_nil] at hp
    rw [List.prefix_nil.1 hp]
    simpa using hUT
  | cons c l ih =>
    intro U hSU hUT hpre p hp
    by_cases hcT : c ∈ T
    · rw [List.filter_cons_of_neg (by simpa using hcT)] at hp
      have h := ih (insert c U) (hSU.trans (Finset.subset_insert _ _))
        (by rw [Finset.insert_union, Finset.insert_eq_of_mem (Finset.mem_union_right _ hcT)]
            exact hUT)
        (fun q hq => by
          have := hpre (c :: q) (List.cons_prefix_cons.2 ⟨rfl, hq⟩)
          simpa [Finset.insert_union] using this) p hp
      rwa [Finset.insert_union, Finset.insert_eq_of_mem (Finset.mem_union_right _ hcT)] at h
    · rw [List.filter_cons_of_pos (by simpa using hcT)] at hp
      -- `d⁻(U ∪ {c} ∪ T) ≤ d⁻(U ∪ {c}) ≤ k`
      have hstep : inDeg D (insert c U ∪ T) ≤ k := by
        have hsub := inDeg_submodular (D := D) (insert c U) T
        have hX : inDeg D T ≤ inDeg D (insert c U ∩ T) :=
          hcomm _ (Finset.subset_inter (hSU.trans (Finset.subset_insert _ _)) hST)
            Finset.inter_subset_right
        have hc := hpre [c] (List.cons_prefix_cons.2 ⟨rfl, List.nil_prefix⟩)
        simp only [List.toFinset_cons, List.toFinset_nil, Finset.union_insert,
          Finset.union_empty] at hc
        omega
      rcases List.prefix_cons_iff.1 hp with rfl | ⟨t, rfl, ht⟩
      · simpa using hUT
      · have h := ih (insert c U) (hSU.trans (Finset.subset_insert _ _)) hstep
          (fun q hq => by
            have := hpre (c :: q) (List.cons_prefix_cons.2 ⟨rfl, hq⟩)
            simpa [Finset.insert_union] using this) t ht
        simpa [Finset.insert_union, Finset.union_insert] using h

/-- **Lemma 1 (Commitment Lemma [25])**, Kitsunai et al. 2016, p. 142: *Let `G` be a
digraph and `k` a positive integer. Let `σ` be a `k`-feasible sequence and let `τ` be a
`k`-committable extension of `σ`. If `σ` is strongly `k`-feasible then so is `τ`.*

Their proof: with `η` a `k`-feasible permutation extending `σ` and `α` the subsequence of
`η` on `V(G) ∖ V(τ)`, the permutation `τ α` is `k`-feasible, because each prefix `τ αᵢ`
has `V(τ αᵢ) = V(τ) ∪ V(ηᵢ)` and submodularity with the commitment condition at
`V(τ) ∩ V(ηᵢ) ⊇ V(σ)` gives `d⁻(τ αᵢ) ≤ d⁻(ηᵢ) ≤ k`. -/
theorem lemma1 {k : ℕ} {σ τ : List V} (_hσ : KFeasible D k σ)
    (hτ : IsCommittableExt D k σ τ) (h : StronglyKFeasible D k σ) :
    StronglyKFeasible D k τ := by
  obtain ⟨⟨hτnd, hτfeas⟩, hστ, -, hcomm⟩ := hτ
  obtain ⟨η, ⟨hηnd, hηall⟩, ⟨-, hηfeas⟩, hση⟩ := h
  -- `η = σ ++ l`; `α = l` with the vertices of `τ` removed.
  obtain ⟨l, rfl⟩ := hση
  set T := τ.toFinset with hT
  set α := l.filter (fun c => c ∉ T) with hα
  have hσT : σ.toFinset ⊆ T := fun x hx =>
    List.mem_toFinset.2 (hστ.subset (List.mem_toFinset.1 hx))
  have hlnd : l.Nodup := (List.nodup_append.1 hηnd).2.1
  have hnd : (τ ++ α).Nodup := by
    refine List.nodup_append.2 ⟨hτnd, hlnd.filter _, fun x hxτ y hyα e => ?_⟩
    subst e
    exact (by simpa [hα, hT] using (List.mem_filter.1 hyα).2 : x ∉ τ) hxτ
  refine ⟨τ ++ α, ⟨hnd, ?_⟩, ⟨hnd, ?_⟩, List.prefix_append τ α⟩
  · -- every vertex occurs
    intro v
    by_cases hv : v ∈ τ
    · exact List.mem_append_left _ hv
    · refine List.mem_append_right _ (List.mem_filter.2 ⟨?_, by simpa [hT] using hv⟩)
      rcases List.mem_append.1 (hηall v) with hvσ | hvl
      · exact absurd (hστ.subset hvσ) hv
      · exact hvl
  · -- every prefix of `τ α` has `d⁻ ≤ k`
    intro p hp
    rcases List.prefix_or_prefix_of_prefix hp (List.prefix_append τ α) with hpτ | hτp
    · exact hτfeas p hpτ
    · obtain ⟨β, rfl⟩ := hτp
      have hβ : β <+: α := (List.prefix_append_right_inj τ).1 hp
      have key := inDeg_union_le_of_prefix (D := D) (k := k) hσT hcomm l σ.toFinset le_rfl
        (by rw [Finset.union_eq_right.2 hσT]; exact hτfeas τ List.prefix_rfl)
        (fun q hq => by
          rw [← List.toFinset_append]
          exact hηfeas (σ ++ q) ((List.prefix_append_right_inj σ).2 hq)) β hβ
      rw [Finset.union_eq_right.2 hσT] at key
      rwa [List.toFinset_append]

/-- Strong feasibility is a property of the vertex set: a `k`-feasible sequence on the
same set as a strongly `k`-feasible one is strongly `k`-feasible (the same completion
works). -/
theorem stronglyKFeasible_of_toFinset_eq {k : ℕ} {σ σ' : List V} (hσ : KFeasible D k σ)
    (h : StronglyKFeasible D k σ') (he : σ.toFinset = σ'.toFinset) :
    StronglyKFeasible D k σ := by
  obtain ⟨η, ⟨hηnd, hηall⟩, ⟨-, hηfeas⟩, hσ'η⟩ := h
  obtain ⟨l, rfl⟩ := hσ'η
  have hlnd : l.Nodup := (List.nodup_append.1 hηnd).2.1
  have hmemσ : ∀ x, x ∈ σ ↔ x ∈ σ' := fun x => by
    rw [← List.mem_toFinset, he, List.mem_toFinset]
  have hnd : (σ ++ l).Nodup := List.nodup_append.2 ⟨hσ.1, hlnd, fun x hxσ y hyl e =>
    (List.nodup_append.1 hηnd).2.2 x ((hmemσ x).1 hxσ) y hyl e⟩
  refine ⟨σ ++ l, ⟨hnd, fun v => ?_⟩, ⟨hnd, fun p hp => ?_⟩, List.prefix_append σ l⟩
  · rcases List.mem_append.1 (hηall v) with h | h
    · exact List.mem_append_left _ ((hmemσ v).2 h)
    · exact List.mem_append_right _ h
  · rcases List.prefix_or_prefix_of_prefix hp (List.prefix_append σ l) with hpσ | hσp
    · exact hσ.2 p hpσ
    · obtain ⟨β, rfl⟩ := hσp
      rw [List.toFinset_append, he, ← List.toFinset_append]
      exact hηfeas (σ' ++ β) ((List.prefix_append_right_inj σ').2
        ((List.prefix_append_right_inj σ).1 hp))

/-- **Corollary 1** (p. 143), the set form: *Let `U` be a `k`-feasible subset of `V(G)` and
let `W` be a `k`-committable extension of `U`. If `U` is strongly `k`-feasible then so is
`W`.* A set is (strongly) `k`-feasible if some (strongly) `k`-feasible sequence has it as
its vertex set; `W` is a `k`-committable extension of `U` if some `k`-feasible `σ` with
`V(σ) = U` has a `k`-committable extension `τ` with `V(τ) = W` (p. 142). -/
theorem corollary1 {k : ℕ} {U W : Finset V}
    (hUW : ∃ σ τ : List V, σ.toFinset = U ∧ τ.toFinset = W ∧ KFeasible D k σ ∧
      IsCommittableExt D k σ τ)
    (hU : ∃ σ : List V, StronglyKFeasible D k σ ∧ σ.toFinset = U) :
    ∃ τ : List V, StronglyKFeasible D k τ ∧ τ.toFinset = W := by
  obtain ⟨σ, τ, hσU, hτW, hσf, hcomm⟩ := hUW
  obtain ⟨σ', hσ', hσ'U⟩ := hU
  exact ⟨τ, lemma1 hσf hcomm (stronglyKFeasible_of_toFinset_eq hσf hσ' (hσU.trans hσ'U.symm)),
    hτW⟩

/-! ### The symmetric digraph of an undirected graph -/

section Symm

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- `Ĝ` (p. 139): each edge `{u, v}` replaced by the pair `(u, v)`, `(v, u)`. -/
def symm : Digraph V := ⟨G.Adj⟩

instance : DecidableRel (symm G).Adj := fun u v => inferInstanceAs (Decidable (G.Adj u v))

variable {G}

theorem symm_adj {u v : V} : (symm G).Adj u v ↔ G.Adj u v := Iff.rfl

theorem insert_inNbrs_symm (v : V) : insert v (inNbrs (symm G) v) = nbhd G v := by
  ext u
  rw [Finset.mem_insert, mem_inNbrs, symm_adj, mem_nbhd]
  constructor
  · rintro (rfl | ⟨_, h⟩)
    · exact Or.inl rfl
    · exact Or.inr h.symm
  · rintro (rfl | h)
    · exact Or.inl rfl
    · exact Or.inr ⟨fun e => G.irrefl (e ▸ h), h.symm⟩

theorem inClosure_symm (U : Finset V) : inClosure (D := symm G) U = opened G U := by
  unfold inClosure opened
  simp_rw [insert_inNbrs_symm]

/-- **The dictionary**: on `Ĝ`, `d⁻(U)` is the border of `U`, i.e. the open stacks `b(U)`. -/
theorem inDeg_symm (U : Finset V) : inDeg (symm G) U = openStacks G U := by
  unfold inDeg openStacks
  rw [inNbrsSet_eq_inClosure_sdiff, inClosure_symm]

/-- Prefix by prefix after `T`: `d⁻ ≤ w` along `l` iff `d⁻(T) ≤ w` and the closing order
`l` from `T` costs at most `w + 1`. -/
theorem forall_prefix_inDeg_le_iff {w : ℕ} :
    ∀ (l : List V) (T : Finset V), l.Nodup → (∀ c ∈ l, c ∉ T) →
      ((∀ p : List V, p <+: l → inDeg (symm G) (T ∪ p.toFinset) ≤ w) ↔
        (openStacks G T ≤ w ∧ orderCost G T l ≤ w + 1)) := by
  intro l
  induction l with
  | nil =>
    intro T _ _
    simp only [List.prefix_nil, forall_eq, List.toFinset_nil, Finset.union_empty, orderCost,
      inDeg_symm]
    omega
  | cons c l ih =>
    intro T hnd hdisj
    have hcT : c ∉ T := hdisj c List.mem_cons_self
    have hlnd : l.Nodup := (List.nodup_cons.1 hnd).2
    have hl : ∀ x ∈ l, x ∉ insert c T := fun x hx hxT => by
      rcases Finset.mem_insert.1 hxT with rfl | h
      · exact (List.nodup_cons.1 hnd).1 hx
      · exact hdisj x (List.mem_cons_of_mem _ hx) h
    have e : (∀ p : List V, p <+: c :: l → inDeg (symm G) (T ∪ p.toFinset) ≤ w) ↔
        (inDeg (symm G) T ≤ w ∧
          ∀ p : List V, p <+: l → inDeg (symm G) (insert c T ∪ p.toFinset) ≤ w) := by
      constructor
      · intro h
        refine ⟨by simpa using h [] List.nil_prefix, fun p hp => ?_⟩
        have := h (c :: p) (List.cons_prefix_cons.2 ⟨rfl, hp⟩)
        simpa [Finset.union_insert, Finset.insert_union] using this
      · rintro ⟨h0, h⟩ p hp
        rcases List.prefix_cons_iff.1 hp with rfl | ⟨t, rfl, ht⟩
        · simpa using h0
        · simpa [Finset.union_insert, Finset.insert_union] using h t ht
    rw [e, ih (insert c T) hlnd hl, orderCost_cons, max_le_iff,
      stepCost_eq_openStacks_insert_add_one hcT, inDeg_symm]
    omega

/-- Strongly `w`-feasible on `Ĝ` is `w`-feasible together with `P_{w+1}` of the vertex set:
the suffix half of Tamaki's notion is our `Solvable`, shifted by one because a step cost
counts the customer being closed. -/
theorem stronglyKFeasible_symm_iff {w : ℕ} {τ : List V} :
    StronglyKFeasible (symm G) w τ ↔
      KFeasible (symm G) w τ ∧ Solvable G (w + 1) τ.toFinset := by
  constructor
  · rintro ⟨η, ⟨hηnd, hηall⟩, ⟨-, hηfeas⟩, hτη⟩
    obtain ⟨l, rfl⟩ := hτη
    have hτnd : τ.Nodup := (List.nodup_append.1 hηnd).1
    have hlnd : l.Nodup := (List.nodup_append.1 hηnd).2.1
    have hdisj : ∀ x ∈ l, x ∉ τ.toFinset := fun x hxl hxτ =>
      (List.nodup_append.1 hηnd).2.2 x (List.mem_toFinset.1 hxτ) x hxl rfl
    refine ⟨⟨hτnd, fun p hp => hηfeas p (hp.trans (List.prefix_append τ l))⟩, l, ⟨hlnd, ?_⟩, ?_⟩
    · intro c
      refine ⟨hdisj c, fun hc => ?_⟩
      rcases List.mem_append.1 (hηall c) with h | h
      · exact absurd (List.mem_toFinset.2 h) hc
      · exact h
    · refine ((forall_prefix_inDeg_le_iff l τ.toFinset hlnd hdisj).1 fun p hp => ?_).2
      rw [← List.toFinset_append]
      exact hηfeas (τ ++ p) ((List.prefix_append_right_inj τ).2 hp)
  · rintro ⟨⟨hτnd, hτfeas⟩, l, ⟨hlnd, hlmem⟩, hcost⟩
    have hdisj : ∀ x ∈ l, x ∉ τ.toFinset := fun x hx => (hlmem x).1 hx
    have hnd : (τ ++ l).Nodup := List.nodup_append.2 ⟨hτnd, hlnd, fun x hxτ y hyl e => by
      subst e; exact hdisj x hyl (List.mem_toFinset.2 hxτ)⟩
    refine ⟨τ ++ l, ⟨hnd, ?_⟩, ⟨hnd, ?_⟩, List.prefix_append τ l⟩
    · intro v
      by_cases hv : v ∈ τ
      · exact List.mem_append_left _ hv
      · exact List.mem_append_right _ ((hlmem v).2 (by simpa using hv))
    · intro p hp
      rcases List.prefix_or_prefix_of_prefix hp (List.prefix_append τ l) with hpτ | hτp
      · exact hτfeas p hpτ
      · obtain ⟨β, rfl⟩ := hτp
        rw [List.toFinset_append]
        exact (forall_prefix_inDeg_le_iff l τ.toFinset hlnd hdisj).2
          ⟨by rw [← inDeg_symm]; exact hτfeas τ List.prefix_rfl, hcost⟩ β
          ((List.prefix_append_right_inj τ).1 hp)

/-! ### The relation to the corrected definite move -/

/-- **Our premise is theirs.** For `V(σ) = S`, `V(τ) = cl(S ∪ {q})`, `q ∉ S`, and `τ` a
`w`-feasible extension of `σ`: `τ` is a `w`-committable extension of `σ` iff `q` is
hereditarily definite at `S`. -/
theorem isCommittableExt_symm_iff_hereditarilyDefinite {w : ℕ} {S : Finset V} {q : V}
    {σ τ : List V} (hσS : σ.toFinset = S) (hτX : τ.toFinset = cl G (insert q S)) (hq : q ∉ S)
    (hτ : KFeasible (symm G) w τ) (hστ : σ <+: τ) :
    IsCommittableExt (symm G) w σ τ ↔ IsHereditarilyDefinite G S q := by
  rw [isHereditarilyDefinite_iff_isCommittable, IsCommittableExt, IsCommittable, hσS, hτX]
  simp_rw [inDeg_symm]
  constructor
  · rintro ⟨-, -, -, h⟩
    exact ⟨subset_cl_insert S q, h⟩
  · rintro ⟨-, h⟩
    refine ⟨hτ, hστ, fun e => hq ?_, h⟩
    have : q ∈ τ.toFinset := hτX ▸ mem_cl_insert_self S q
    rw [← e, hσS] at this
    exact this

/-- **Their Lemma 1 at the child, from our theorem.** On `Ĝ`, with `V(σ) = S` and
`V(τ) = cl(S ∪ {q})`, the conclusion of the Commitment Lemma follows from
`solvable_cl_insert_of_hereditarilyDefinite` and the dictionary alone. -/
theorem stronglyKFeasible_child_of_hereditarilyDefinite {w : ℕ} {S : Finset V} {q : V}
    {σ τ : List V} (hσS : σ.toFinset = S) (hτX : τ.toFinset = cl G (insert q S)) (hq : q ∉ S)
    (_hσ : KFeasible (symm G) w σ) (hτ : IsCommittableExt (symm G) w σ τ)
    (h : StronglyKFeasible (symm G) w σ) : StronglyKFeasible (symm G) w τ := by
  have hdef := (isCommittableExt_symm_iff_hereditarilyDefinite hσS hτX hq hτ.1 hτ.2.1).1 hτ
  rw [stronglyKFeasible_symm_iff] at h ⊢
  refine ⟨hτ.1, ?_⟩
  rw [hτX]
  exact solvable_cl_insert_of_hereditarilyDefinite hdef hq (hσS ▸ h.2)

/-- **Their Lemma 1 on `Ĝ`, for every extension, from the set-form commitment lemma of
`Layout.lean`** (`solvable_of_isCommittable`). -/
theorem lemma1_symm_of_isCommittable {w : ℕ} {σ τ : List V} (_hσ : KFeasible (symm G) w σ)
    (hτ : IsCommittableExt (symm G) w σ τ) (h : StronglyKFeasible (symm G) w σ) :
    StronglyKFeasible (symm G) w τ := by
  obtain ⟨hτf, hστ, -, hcomm⟩ := hτ
  rw [stronglyKFeasible_symm_iff] at h ⊢
  refine ⟨hτf, solvable_of_isCommittable ⟨?_, fun X hSX hXT => ?_⟩ h.2⟩
  · exact fun x hx => List.mem_toFinset.2 (hστ.subset (List.mem_toFinset.1 hx))
  · have := hcomm X hSX hXT
    rwa [inDeg_symm, inDeg_symm] at this

/-- The border never grows between a set and its free closure. -/
theorem openStacks_le_of_subset_cl {A P : Finset V} (hAP : A ⊆ P) (hP : P ⊆ cl G A) :
    openStacks G P ≤ openStacks G A := by
  have h1 := openStacks_add_card (G := G) P
  have h2 := openStacks_add_card (G := G) A
  have h3 : opened G P = opened G A :=
    le_antisymm (opened_subset_of_subset_cl hP) (opened_mono hAP)
  have h4 := Finset.card_le_card hAP
  rw [h3] at h1
  omega

/-- The path `q`, then the free moves, is `w`-feasible after a `w`-feasible `σ` whenever
`q` is playable at budget `w + 1`. -/
theorem kFeasible_child_path {w : ℕ} {S : Finset V} {q : V} {σ : List V} (hσS : σ.toFinset = S)
    (hσ : KFeasible (symm G) w σ) (hq : q ∉ S) (hplay : stepCost G S q ≤ w + 1) :
    KFeasible (symm G) w (σ ++ q :: (cl G (insert q S) \ insert q S).toList) := by
  set r := (cl G (insert q S) \ insert q S).toList with hr
  have hrmem : ∀ x ∈ r, x ∈ cl G (insert q S) \ insert q S := fun x hx =>
    Finset.mem_toList.1 hx
  have hqr : q ∉ r := fun h => (Finset.mem_sdiff.1 (hrmem q h)).2 (Finset.mem_insert_self _ _)
  refine ⟨?_, ?_⟩
  · refine List.nodup_append.2 ⟨hσ.1, List.nodup_cons.2 ⟨hqr, Finset.nodup_toList _⟩,
      fun x hxσ y hyr e => ?_⟩
    subst e
    have hxS : x ∈ S := hσS ▸ List.mem_toFinset.2 hxσ
    rcases List.mem_cons.1 hyr with rfl | hxr
    · exact hq hxS
    · exact (Finset.mem_sdiff.1 (hrmem x hxr)).2 (Finset.mem_insert_of_mem hxS)
  · intro p hp
    rcases List.prefix_or_prefix_of_prefix hp (List.prefix_append σ _) with hpσ | hσp
    · exact hσ.2 p hpσ
    · obtain ⟨β, rfl⟩ := hσp
      have hβ : β <+: q :: r := (List.prefix_append_right_inj σ).1 hp
      rw [List.toFinset_append, hσS, inDeg_symm]
      rcases List.prefix_cons_iff.1 hβ with rfl | ⟨t, rfl, ht⟩
      · simp only [List.toFinset_nil, Finset.union_empty]
        rw [← inDeg_symm, ← hσS]
        exact hσ.2 σ List.prefix_rfl
      · rw [List.toFinset_cons, Finset.union_insert]
        have hsub : insert q S ⊆ insert q (S ∪ t.toFinset) :=
          Finset.insert_subset_insert _ Finset.subset_union_left
        have hcl : insert q (S ∪ t.toFinset) ⊆ cl G (insert q S) := by
          refine Finset.insert_subset (mem_cl_insert_self S q)
            (Finset.union_subset (subset_cl_insert S q) fun x hx => ?_)
          exact (Finset.mem_sdiff.1 (hrmem x (ht.subset (List.mem_toFinset.1 hx)))).1
        have := openStacks_le_of_subset_cl hsub hcl
        have hcost := stepCost_eq_openStacks_insert_add_one (G := G) hq
        omega

/-- **Our theorem from their Lemma 1, used as a black box**, under the two side conditions
their statement carries and ours does not: `S` is `w`-feasible as a set, and `q` is
playable (which makes the child path `w`-feasible, `kFeasible_child_path`). Both hold at
every node below the root of the search. -/
theorem solvable_cl_insert_of_lemma1 {w : ℕ} {S : Finset V} {q : V}
    (hfeas : ∃ σ : List V, KFeasible (symm G) w σ ∧ σ.toFinset = S)
    (hplay : stepCost G S q ≤ w + 1)
    (h : IsHereditarilyDefinite G S q) (hq : q ∉ S) (hs : Solvable G (w + 1) S) :
    Solvable G (w + 1) (cl G (insert q S)) := by
  obtain ⟨σ, hσ, hσS⟩ := hfeas
  set τ := σ ++ q :: (cl G (insert q S) \ insert q S).toList with hτdef
  have hτf : KFeasible (symm G) w τ := kFeasible_child_path hσS hσ hq hplay
  have hτX : τ.toFinset = cl G (insert q S) := by
    rw [hτdef, List.toFinset_append, List.toFinset_cons, Finset.toList_toFinset, hσS,
      Finset.union_insert, ← Finset.insert_union, Finset.union_sdiff_of_subset
        (subset_cl (insert q S))]
  have hστ : σ <+: τ := List.prefix_append σ _
  have hcomm : IsCommittableExt (symm G) w σ τ :=
    (isCommittableExt_symm_iff_hereditarilyDefinite hσS hτX hq hτf hστ).2 h
  have hstrong : StronglyKFeasible (symm G) w σ :=
    stronglyKFeasible_symm_iff.2 ⟨hσ, hσS ▸ hs⟩
  have := (stronglyKFeasible_symm_iff.1 (lemma1 hσ hcomm hstrong)).2
  rwa [hτX] at this

end Symm

/-! ### The premise gap, witnessed -/

/-- The graph `0–1, 0–2, 0–3, 1–4`. -/
def gapGraph : SimpleGraph (Fin 5) :=
  SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ [(0, 1), (0, 2), (0, 3), (1, 4)]

instance : DecidableRel gapGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ [(0, 1), (0, 2), (0, 3), (1, 4)] ∨
    (b.val, a.val) ∈ [(0, 1), (0, 2), (0, 3), (1, 4)])))

/-- **The side conditions are not redundant.** At `S = {0}`, `q = 2`, `k = 3` (`w = 2`): the
corrected definite move applies — `q` is hereditarily definite, playable, `P_3(S)` holds —
and concludes `P_3({0, 2, 3})`; but `d⁻({0}) = 3`, so no sequence with `V(σ) = {0}` is
`2`-feasible, and Lemma 1 has no instance with `V(σ) = S`. -/
theorem premise_gap :
    IsHereditarilyDefinite gapGraph {0} 2 ∧ (2 : Fin 5) ∉ ({0} : Finset (Fin 5)) ∧
      stepCost gapGraph {0} 2 ≤ 3 ∧ Solvable gapGraph 3 {0} ∧
      cl gapGraph (insert 2 {0}) = {0, 2, 3} ∧ Solvable gapGraph 3 (cl gapGraph (insert 2 {0})) ∧
      inDeg (symm gapGraph) {0} = 3 ∧
      ¬ ∃ σ : List (Fin 5), KFeasible (symm gapGraph) 2 σ ∧ σ.toFinset = {0} := by
  have hdef : IsHereditarilyDefinite gapGraph {0} 2 := by
    unfold IsHereditarilyDefinite; decide
  have hsol : Solvable gapGraph 3 {0} :=
    ⟨[2, 3, 1, 4], by unfold IsClosingOrder; decide, by decide⟩
  refine ⟨hdef, by decide, by decide, hsol, by decide,
    solvable_cl_insert_of_hereditarilyDefinite hdef (by decide) hsol, by decide, ?_⟩
  rintro ⟨σ, ⟨-, hfeas⟩, hσ⟩
  have := hfeas σ List.prefix_rfl
  rw [hσ] at this
  revert this
  decide

end Tamaki

end Search

end MOSPFormalization
