/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Counting events, not witnesses: the deterministic lemmas and the union bound over separators

`FirstMoment.lean` bounds the `G(n, p)` probability of `{pathwidth ≤ k}` by the
expected number of *empty pairs* `(A, R)` of the forced sizes. The witnesses of
one graph are many; `reports/separator_moment.md` (Ralph loop0011, 2026-11-01)
asks what the count buys when it runs over the *event* instead — the separator
`S = V ∖ (A ∪ R)`, the closed pair `S = N(A) ∩ N(R)`, or a weighted count
`Σ_P 1[P empty] / Z(P)`. This file proves the deterministic lemmas of that
report's §2 and the finite, exact counting statements of its §8, in the order
its §8.4 recommends. Every statement was checked by brute force before it was
written down (§2.4: every graph on 1–9 vertices, zero violations; §8.3: every
labelled graph on 1–7 vertices in exact rationals, zero violations).

## Notation

`n = |V|`, `k < n`, `N = n − k`, `t = ⌈N/2⌉ = (n − k + 1) / 2`,
`r = ⌊N/2⌋ = (n − k) / 2`, so `t + r = N`. `IsEmptyPair G A R` (`FirstMoment.lean`)
is "no edge joins `A` to `R`"; `closedNbhd G A = N[A]` (`EmptyPair.lean`).

## Main results

* `exists_balanced_separator` — **L1**: `pathwidth G ≤ k < n` gives pairwise
  disjoint `A, R, S` covering `V` with `|A| = t`, `|R| = r`, `|S| = k` and no
  `A`–`R` edge. From `exists_empty_pair_of_layout` at position `t − 1`, shrinking
  the inactive suffix to exactly `r` vertices. `exists_balanced_separator_cover`
  is the MOSP form on a random clique cover: `mospValue ≤ k + 1` gives the same
  with "no pattern meets both `A` and `R`".
* `IsBalancedBip G S k` — the pair form of the event `E_bip(S)`: an exact-size
  empty pair partitioning `V ∖ S`; `exists_isBalancedBip` (**L1′ a**).
  `componentOff_subset_side` (**the connectivity step of L1′**): the vertices
  reachable from `a ∈ A` by a walk avoiding `S` all lie in `A`;
  `card_componentOff_le_of_isBalancedBip` (**L1′ b**): every such component of
  `G − S` has at most `t` vertices (the relaxed event `E_relax`);
  `not_isBalancedBip_threeK2`, `card_componentOff_threeK2_le` (**L1′ d**): `3K₂`
  at `k = 0` is in `E_relax` and not in `E_bip`.
* `subset_compl_closedNbhd_iff` (the Galois step), `closedNbhd_mono`,
  `IsClosedPair G A R` (`A = V ∖ N[R]` and `R = V ∖ N[A]`), `closeStep` (one
  round of the alternating closure, `A` first), `closeStep_closeStep`
  (**L2 iii**: the closure is a fixpoint after one round — no iteration and no
  termination argument), `subset_closeStep` (**L2 i**), `closeStep_isClosedPair`
  (**L2 ii–iii**, for *every* pair), `sdiff_eq_inter_boundary_of_isClosedPair`
  (**L2 iv**: `S* = N(A*) ∩ N(R*)`), `card_closeStep` (**L2 v**),
  `exists_closedPair_of_pathwidth_le` (**L1 + L2**), and
  `isClosedPair_iff_sees_both` (the characterisation step of Theorem Cl: a pair
  is closed iff it is empty and every vertex outside it sees both sides).
* `weightedCount_ge_indicator` — **Lemma W**: for a finite family of pairs, an
  emptiness predicate and any `Z` with `1 ≤ Z(P) ≤ #{empty pairs}` on the empty
  pairs, `Σ_P 1[P empty] / Z(P) ≥ 1[some pair is empty]`;
  `weightedSum_graphsOfPathwidthLe_le_weighted` — its `G(n, p)` reading over the
  exact-size pairs `pairIndices t r`: `P(pathwidth ≤ k) ≤ E[Y]`.
* `weightedSum_graphsOfPathwidthLe_le_sum_separators` — **the union bound over
  separators**: `Σ_{pw G ≤ k} gnpWeight p G ≤ Σ_{|S| = k} Σ_{G ∈ E_bip(S)} gnpWeight p G`.
* `restrictOff G S` (the edges of `G` with both ends off `S`), `pairsOff S`,
  `pairsMeeting S`; `isBalancedBip_restrictOff` (`E_bip(S)` depends on `G` only
  through its edges off `S`); `sum_gnpWeight_fiber` — **the factorisation step**:
  for `H` with no edge meeting `S`, the graphs `G` with `restrictOff G S = H` have
  total weight `p^|E(H)| (1 − p)^(|pairsOff S| − |E(H)|)` (the fibre is a product
  with the `2^|pairsMeeting S|` subsets of the pairs meeting `S`, whose weights
  sum to `(p + (1 − p))^|pairsMeeting S| = 1`); `card_pairsOff` —
  `|pairsOff S| = (n − |S|).choose 2`; `sum_gnpWeight_bipGraphs` — the inner
  probability of `E_bip(S)` **is** the `G(N, p)` weighted count of the pair-form
  event over the graphs on `V ∖ S`, exactly (`innerBip p S k`);
  `weightedSum_graphsOfPathwidthLe_le_separator` — Theorem S in its
  separator-summed form.
* `exists_equiv_mem_iff`, `relabel`, `innerBip_eq_of_card_eq` — **the
  relabelling**: a permutation of `V` carrying `S₀` onto `S` exists whenever
  `|S₀| = |S|`, and the inner count is the same for every `S` of a given size; so
  `weightedSum_graphsOfPathwidthLe_le_choose_mul_innerBip` — **Theorem S**
  (`reports/separator_moment.md` §8.1), finite and exact: for `0 ≤ p ≤ 1`, `k < n`
  and any `k`-set `S₀`, `P(pathwidth ≤ k) ≤ n.choose k · innerBip p S₀ k`.
* `weightedSum_graphsOfPathwidthLe_le_sum_closedPairs` — **the union bound of
  Theorem Cl** over the disjoint ordered pairs with `|A| ≥ t`, `|R| ≥ r`.
* `sum_subsetWeight_split`, `sum_subsetWeight_blocks` — **the product over blocks**
  (loop0011 item 13): the `p`-weight of `{F ⊆ T : ∀ i, P i (F ∩ B i)}` over pairwise
  disjoint blocks `B i ⊆ T` is the product of the per-block weights; `starPairs`,
  `ClosedEdgeSet`, `isClosedPair_iff_closedEdgeSet`, `image_edges_closedPairGraphs`;
  `sum_gnpWeight_closedPairGraphs` — **the independence step of Theorem Cl**: the
  `G(n, p)` probability that `(A, R)` is closed is
  `(1 − p)^(|A||R|) ((1 − (1 − p)^|A|)(1 − (1 − p)^|R|))^|S|`, exactly;
  `weightedSum_graphsOfPathwidthLe_le_closedPairCount` (pair-summed) and, through
  `closedIndices_eq_biUnion` and `sum_closedIndices_eq`,
  `weightedSum_graphsOfPathwidthLe_le_closedPairFormula` (summed over the size pairs
  `(a, r')` with `n.choose a · (n − a).choose r'`) — **Theorem Cl** in full
  (`reports/separator_moment.md` §8.1, §13).
* `isolatedIn`, `flipPair`, `flipPair_isEmptyPair`, `flipPair_disjoint`,
  `card_flipPair`, `flipPair_injOn`, `flips`, `one_le_card_flips`, `card_flips_le`
  — **Lemma Fl**: exchanging equally many vertices isolated in `G[A]` and `G[R]`
  gives distinct empty pairs of the same sizes, so `1 ≤ #flips ≤ X` on the empty
  pairs; `weightedSum_graphsOfPathwidthLe_le_flipWeighted` — **Corollary W-flip,
  the sound part**: `P(pathwidth ≤ k) ≤ E[Σ_P 1[P empty] / #flips(P)]`.

What is on paper and not here (`reports/separator_moment.md` §10.3, §13): the
partition formula for `P_N(E_bip)` (Lemma P), Gilbert's recursion (Lemma G) and
the first-vertex-component recursion (Lemma F), which need the components of
`G − S` as finsets with their sizes; Lemma J and Theorem Cl-cover
(inclusion–exclusion over pattern sets); the evaluation of the flip-weighted
count; and every rate and constant (§5–§7). Theorem Cl's independence step was
on that list until loop0011 item 13 (2026-11-01).

No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only.
-/

import MOSPFormalization.EmptyPair
import MOSPFormalization.FirstMoment
import MOSPFormalization.CliqueCoverMoment

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### A layout attaining the pathwidth -/

/-- The infimum defining the vertex separation is attained, and equals the pathwidth. -/
theorem exists_layout_vertexSep_eq_pathwidth :
    ∃ σ : LinearLayout V, vertexSepOfLayout G σ = pathwidth G := by
  have hne : (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ)).Nonempty :=
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  obtain ⟨σ, hσ⟩ := Nat.sInf_mem hne
  refine ⟨σ, ?_⟩
  rw [← vertexSeparation_eq_pathwidth]
  exact hσ

/-! ### L1: the balanced separator at exact sizes -/

/-- **L1.** `pathwidth G ≤ k < n` gives pairwise disjoint `A, R, S` with
`A ∪ R ∪ S = V`, `|A| = ⌈(n − k)/2⌉`, `|R| = ⌊(n − k)/2⌋`, `|S| = k` and no `A`–`R`
edge: the prefix of size `t`, the inactive suffix shrunk to `r` vertices, and the
rest (the active suffix padded to `k`). -/
theorem exists_balanced_separator (k : ℕ) (hpw : pathwidth G ≤ k) (hk : k < Fintype.card V) :
    ∃ A R S : Finset V, Disjoint A R ∧ Disjoint A S ∧ Disjoint R S ∧ A ∪ R ∪ S = univ ∧
      A.card = (Fintype.card V - k + 1) / 2 ∧ R.card = (Fintype.card V - k) / 2 ∧
      S.card = k ∧ IsEmptyPair G A R := by
  obtain ⟨σ, hσk⟩ := exists_layout_vertexSep_eq_pathwidth G
  obtain ⟨A, R₀, hAR₀, hA, hsum, hedge⟩ :=
    exists_empty_pair_of_layout G σ ((Fintype.card V - k + 1) / 2 - 1) (by omega)
  obtain ⟨R, hRR₀, hR⟩ := Finset.exists_subset_card_eq
    (s := R₀) (n := (Fintype.card V - k) / 2) (by omega)
  have hAR : Disjoint A R := Finset.disjoint_of_subset_right hRR₀ hAR₀
  have hcardU : (A ∪ R).card = (Fintype.card V - k + 1) / 2 + (Fintype.card V - k) / 2 := by
    rw [card_union_of_disjoint hAR, hR]; omega
  refine ⟨A, R, univ \ (A ∪ R), hAR,
    Finset.disjoint_sdiff.mono_left subset_union_left,
    Finset.disjoint_sdiff.mono_left subset_union_right,
    union_sdiff_of_subset (subset_univ _), by omega, hR, ?_,
    fun a ha r hr => hedge a ha r (hRR₀ hr)⟩
  rw [card_sdiff_of_subset (subset_univ _), card_univ, hcardU]
  omega

/-- The MOSP form of L1 on a random clique cover (`CliqueCoverMoment.lean`): an
instance with `mospValue ≤ k + 1`, `k < n`, has a balanced separator whose two
sides are met by no common pattern (`isEmptyPair_coverGraph_iff`). -/
theorem exists_balanced_separator_cover {C : Type*} [Fintype C] [DecidableEq C] {m : ℕ}
    (S : Fin m → Finset C) (hreq : ∃ c p, (coverInstance S).requires c p) (k : ℕ)
    (hval : (coverInstance S).mospValue ≤ k + 1) (hk : k < Fintype.card C) :
    ∃ A R T : Finset C, Disjoint A R ∧ Disjoint A T ∧ Disjoint R T ∧ A ∪ R ∪ T = univ ∧
      A.card = (Fintype.card C - k + 1) / 2 ∧ R.card = (Fintype.card C - k) / 2 ∧
      T.card = k ∧ ∀ j, Disjoint (S j) A ∨ Disjoint (S j) R := by
  have hpw : pathwidth (coverInstance S).mospGraph ≤ k := by
    rw [(coverInstance S).mospValue_eq_pathwidth_add_one hreq] at hval
    omega
  obtain ⟨A, R, T, hAR, hAT, hRT, hU, hA, hR, hT, hE⟩ :=
    exists_balanced_separator (coverGraph S) k hpw hk
  exact ⟨A, R, T, hAR, hAT, hRT, hU, hA, hR, hT, (isEmptyPair_coverGraph_iff hAR).1 hE⟩

/-! ### The Galois step and the closure -/

/-- **The Galois step.** `R ⊆ V ∖ N[A]` iff `R` is disjoint from `A` and no edge joins
them. -/
theorem subset_compl_closedNbhd_iff (A R : Finset V) :
    R ⊆ univ \ closedNbhd G A ↔ Disjoint A R ∧ IsEmptyPair G A R := by
  constructor
  · intro h
    refine ⟨?_, ?_⟩
    · rw [Finset.disjoint_left]
      intro a ha haR
      have := h haR
      rw [mem_sdiff, mem_closedNbhd_iff] at this
      exact this.2 (Or.inl ha)
    · intro a ha r hr hadj
      have := h hr
      rw [mem_sdiff, mem_closedNbhd_iff] at this
      exact this.2 (Or.inr ⟨a, ha, hadj⟩)
  · rintro ⟨hd, he⟩ r hr
    rw [mem_sdiff, mem_closedNbhd_iff]
    refine ⟨mem_univ _, ?_⟩
    rintro (hrA | ⟨a, ha, hadj⟩)
    · exact Finset.disjoint_left.1 hd hrA hr
    · exact he a ha r hr hadj

variable {G} in
theorem IsEmptyPair.symm {A R : Finset V} (h : IsEmptyPair G A R) : IsEmptyPair G R A :=
  fun r hr a ha hadj => h a ha r hr (G.adj_symm hadj)

/-- The monotone step: `A ⊆ A'` gives `N[A] ⊆ N[A']`. -/
theorem closedNbhd_mono {A A' : Finset V} (h : A ⊆ A') : closedNbhd G A ⊆ closedNbhd G A' := by
  intro v hv
  rw [mem_closedNbhd_iff] at hv ⊢
  rcases hv with hvA | ⟨a, ha, hadj⟩
  · exact Or.inl (h hvA)
  · exact Or.inr ⟨a, h ha, hadj⟩

/-- `(A, R)` is a **closed pair**: `A = V ∖ N[R]` and `R = V ∖ N[A]`, the minimal-separator
form `S = N(A) ∩ N(R)` (`sdiff_eq_inter_boundary_of_isClosedPair`). -/
def IsClosedPair (A R : Finset V) : Prop :=
  A = univ \ closedNbhd G R ∧ R = univ \ closedNbhd G A

/-- One round of the alternating closure, `A` first:
`R* = V ∖ N[A]`, `A* = V ∖ N[R*]`. -/
def closeStep (P : Finset V × Finset V) : Finset V × Finset V :=
  (univ \ closedNbhd G (univ \ closedNbhd G P.1), univ \ closedNbhd G P.1)

/-- Every set is inside the complement of the closed neighbourhood of the complement of
its own closed neighbourhood: `A ⊆ V ∖ N[V ∖ N[A]]`. -/
theorem subset_compl_closedNbhd_compl_closedNbhd (A : Finset V) :
    A ⊆ univ \ closedNbhd G (univ \ closedNbhd G A) := by
  obtain ⟨hd, he⟩ := (subset_compl_closedNbhd_iff G A (univ \ closedNbhd G A)).1 subset_rfl
  exact (subset_compl_closedNbhd_iff G _ _).2 ⟨hd.symm, he.symm⟩

/-- **L2 i**: the closure is monotone on empty pairs. -/
theorem subset_closeStep {A R : Finset V} (hAR : Disjoint A R) (he : IsEmptyPair G A R) :
    A ⊆ (closeStep G (A, R)).1 ∧ R ⊆ (closeStep G (A, R)).2 :=
  ⟨subset_compl_closedNbhd_compl_closedNbhd G A,
    (subset_compl_closedNbhd_iff G A R).2 ⟨hAR, he⟩⟩

/-- **L2 ii–iii**: one round of the closure lands on a closed pair, from *any* `A`. -/
theorem closeStep_isClosedPair (P : Finset V × Finset V) :
    IsClosedPair G (closeStep G P).1 (closeStep G P).2 := by
  refine ⟨rfl, ?_⟩
  apply Finset.Subset.antisymm
  · obtain ⟨hd, he⟩ :=
      (subset_compl_closedNbhd_iff G (univ \ closedNbhd G P.1) _).1 (subset_rfl)
    exact (subset_compl_closedNbhd_iff G _ _).2 ⟨hd.symm, he.symm⟩
  · exact sdiff_subset_sdiff subset_rfl
      (closedNbhd_mono G (subset_compl_closedNbhd_compl_closedNbhd G P.1))

/-- A closed pair is disjoint and empty. -/
theorem IsClosedPair.disjoint_and_isEmptyPair {A R : Finset V} (h : IsClosedPair G A R) :
    Disjoint A R ∧ IsEmptyPair G A R :=
  (subset_compl_closedNbhd_iff G A R).1 (h.2 ▸ subset_rfl)

/-- **L2 iii**: the closure stops after one round — `closeStep` is idempotent, so the
alternating sequence `R₁ = V ∖ N[A]`, `A₁ = V ∖ N[R₁]`, `R₂ = V ∖ N[A₁]`, … is constant
from its first term on. No iteration and no termination argument are needed. -/
theorem closeStep_closeStep (P : Finset V × Finset V) :
    closeStep G (closeStep G P) = closeStep G P := by
  have h2 := (closeStep_isClosedPair G P).2
  show (univ \ closedNbhd G (univ \ closedNbhd G (closeStep G P).1),
    univ \ closedNbhd G (closeStep G P).1) = closeStep G P
  rw [← h2]
  rfl

/-- **L2 iv**: the separator of a closed pair is `N(A) ∩ N(R)`, the common outer
boundary. -/
theorem sdiff_eq_inter_boundary_of_isClosedPair {A R : Finset V} (h : IsClosedPair G A R) :
    univ \ (A ∪ R) = (closedNbhd G A \ A) ∩ (closedNbhd G R \ R) := by
  obtain ⟨hA, hR⟩ := h
  ext v
  simp only [mem_sdiff, mem_union, mem_inter, mem_univ, true_and, not_or]
  constructor
  · rintro ⟨hvA, hvR⟩
    refine ⟨⟨?_, hvA⟩, ⟨?_, hvR⟩⟩
    · by_contra hN
      exact hvR (hR ▸ mem_sdiff.2 ⟨mem_univ v, hN⟩)
    · by_contra hN
      exact hvA (hA ▸ mem_sdiff.2 ⟨mem_univ v, hN⟩)
  · rintro ⟨⟨_, hvA⟩, ⟨_, hvR⟩⟩
    exact ⟨hvA, hvR⟩

/-- **L2 v**: the closure keeps the sides at least as large and the separator at most as
large. -/
theorem card_closeStep {A R : Finset V} (hAR : Disjoint A R) (he : IsEmptyPair G A R)
    {t r k : ℕ} (hA : t ≤ A.card) (hR : r ≤ R.card) (hS : (univ \ (A ∪ R)).card ≤ k) :
    t ≤ (closeStep G (A, R)).1.card ∧ r ≤ (closeStep G (A, R)).2.card ∧
      (univ \ ((closeStep G (A, R)).1 ∪ (closeStep G (A, R)).2)).card ≤ k := by
  obtain ⟨h1, h2⟩ := subset_closeStep G hAR he
  refine ⟨hA.trans (card_le_card h1), hR.trans (card_le_card h2), ?_⟩
  exact (card_le_card (sdiff_subset_sdiff subset_rfl (union_subset_union h1 h2))).trans hS

/-- **L1 + L2.** `pathwidth G ≤ k < n` gives a closed empty pair with `|A| ≥ t`, `|R| ≥ r`
and separator of at most `k` vertices. -/
theorem exists_closedPair_of_pathwidth_le (k : ℕ) (hpw : pathwidth G ≤ k)
    (hk : k < Fintype.card V) :
    ∃ A R : Finset V, IsClosedPair G A R ∧ IsEmptyPair G A R ∧
      (Fintype.card V - k + 1) / 2 ≤ A.card ∧ (Fintype.card V - k) / 2 ≤ R.card ∧
      (univ \ (A ∪ R)).card ≤ k := by
  obtain ⟨A, R, S, hAR, hAS, hRS, hU, hA, hR, hS, hE⟩ :=
    exists_balanced_separator G k hpw hk
  have hSeq : univ \ (A ∪ R) = S := by
    rw [← hU, union_sdiff_cancel_left (Finset.disjoint_union_left.2 ⟨hAS, hRS⟩)]
  obtain ⟨h1, h2, h3⟩ := card_closeStep G hAR hE (t := (Fintype.card V - k + 1) / 2)
    (r := (Fintype.card V - k) / 2) (k := k) hA.ge hR.ge (by rw [hSeq, hS])
  exact ⟨_, _, closeStep_isClosedPair G (A, R),
    (closeStep_isClosedPair G (A, R)).disjoint_and_isEmptyPair.2, h1, h2, h3⟩

/-- **The characterisation step of Theorem Cl**: a pair is closed iff it is disjoint,
empty, and every vertex outside both sides has a neighbour in each. -/
theorem isClosedPair_iff_sees_both (A R : Finset V) :
    IsClosedPair G A R ↔ Disjoint A R ∧ IsEmptyPair G A R ∧
      ∀ v, v ∉ A → v ∉ R → (∃ a ∈ A, G.Adj a v) ∧ (∃ r ∈ R, G.Adj r v) := by
  constructor
  · intro h
    obtain ⟨hd, he⟩ := h.disjoint_and_isEmptyPair
    obtain ⟨hA, hR⟩ := h
    refine ⟨hd, he, fun v hvA hvR => ⟨?_, ?_⟩⟩
    · have : v ∈ closedNbhd G A := by
        by_contra hN
        exact hvR (hR ▸ mem_sdiff.2 ⟨mem_univ v, hN⟩)
      rw [mem_closedNbhd_iff] at this
      exact this.resolve_left hvA
    · have : v ∈ closedNbhd G R := by
        by_contra hN
        exact hvA (hA ▸ mem_sdiff.2 ⟨mem_univ v, hN⟩)
      rw [mem_closedNbhd_iff] at this
      exact this.resolve_left hvR
  · rintro ⟨hd, he, hsee⟩
    constructor
    · ext v
      rw [mem_sdiff, mem_closedNbhd_iff]
      constructor
      · intro hvA
        refine ⟨mem_univ v, ?_⟩
        rintro (hvR | ⟨r, hr, hadj⟩)
        · exact Finset.disjoint_left.1 hd hvA hvR
        · exact he.symm r hr v hvA hadj
      · rintro ⟨_, hN⟩
        by_contra hvA
        have hvR : v ∉ R := fun hvR => hN (Or.inl hvR)
        exact hN (Or.inr (hsee v hvA hvR).2)
    · ext v
      rw [mem_sdiff, mem_closedNbhd_iff]
      constructor
      · intro hvR
        refine ⟨mem_univ v, ?_⟩
        rintro (hvA | ⟨a, ha, hadj⟩)
        · exact Finset.disjoint_left.1 hd hvA hvR
        · exact he a ha v hvR hadj
      · rintro ⟨_, hN⟩
        by_contra hvR
        have hvA : v ∉ A := fun hvA => hN (Or.inl hvA)
        exact hN (Or.inr (hsee v hvA hvR).1)

/-! ### L1′: the pair form of `E_bip(S)`, and the components of `G − S` -/

/-- The pair form of the event `E_bip(S)`: an exact-size empty pair partitioning `V ∖ S`. -/
def IsBalancedBip (S : Finset V) (k : ℕ) : Prop :=
  ∃ A R : Finset V, Disjoint A R ∧ A ∪ R = univ \ S ∧
    A.card = (Fintype.card V - k + 1) / 2 ∧ R.card = (Fintype.card V - k) / 2 ∧
    IsEmptyPair G A R

/-- **L1′ a.** `pathwidth G ≤ k < n` gives a `k`-set `S` in `E_bip(S)`. -/
theorem exists_isBalancedBip (k : ℕ) (hpw : pathwidth G ≤ k) (hk : k < Fintype.card V) :
    ∃ S : Finset V, S.card = k ∧ IsBalancedBip G S k := by
  obtain ⟨A, R, S, hAR, hAS, hRS, hU, hA, hR, hS, hE⟩ :=
    exists_balanced_separator G k hpw hk
  refine ⟨S, hS, A, R, hAR, ?_, hA, hR, hE⟩
  rw [← hU, union_sdiff_cancel_right (Finset.disjoint_union_left.2 ⟨hAS, hRS⟩)]

/-- Reachability in `G − S`: a walk of `G` all of whose vertices avoid `S`. -/
def ReachableOff (S : Finset V) (u v : V) : Prop :=
  ∃ p : G.Walk u v, ∀ w ∈ p.support, w ∉ S

open scoped Classical in
/-- The component of `v` in `G − S`, as a finset. -/
noncomputable def componentOff (S : Finset V) (v : V) : Finset V :=
  univ.filter (fun w => ReachableOff G S v w)

/-- **The connectivity step of L1′.** With `(A, R)` an empty pair whose union is `V ∖ S`,
a walk avoiding `S` that starts in `A` stays in `A`: a component of `G − S` lies inside one
side. -/
theorem mem_side_of_walk {A R S : Finset V} (hU : A ∪ R = univ \ S) (he : IsEmptyPair G A R)
    {u v : V} (p : G.Walk u v) (hp : ∀ w ∈ p.support, w ∉ S) (hu : u ∈ A) : v ∈ A := by
  induction p with
  | nil => exact hu
  | @cons x y z hxy q ih =>
    have hq : ∀ w ∈ q.support, w ∉ S := fun w hw =>
      hp w (by rw [SimpleGraph.Walk.support_cons]; exact List.mem_cons_of_mem x hw)
    have hyS : y ∉ S := hq y q.start_mem_support
    have hy : y ∈ A ∪ R := by rw [hU, mem_sdiff]; exact ⟨mem_univ y, hyS⟩
    rcases mem_union.1 hy with hyA | hyR
    · exact ih hq hyA
    · exact absurd hxy (he x hu y hyR)

theorem componentOff_subset_side {A R S : Finset V} (hU : A ∪ R = univ \ S)
    (he : IsEmptyPair G A R) {v : V} (hv : v ∈ A) : componentOff G S v ⊆ A := by
  intro w hw
  classical
  obtain ⟨p, hp⟩ := (mem_filter.1 hw).2
  exact mem_side_of_walk G hU he p hp hv

/-- **L1′ b.** Under `E_bip(S)` every component of `G − S` has at most
`t = ⌈(n − k)/2⌉` vertices: the relaxed event `E_relax(S)`. -/
theorem card_componentOff_le_of_isBalancedBip {S : Finset V} {k : ℕ}
    (h : IsBalancedBip G S k) {v : V} (hv : v ∉ S) :
    (componentOff G S v).card ≤ (Fintype.card V - k + 1) / 2 := by
  obtain ⟨A, R, hAR, hU, hA, hR, he⟩ := h
  have hv' : v ∈ A ∪ R := by rw [hU, mem_sdiff]; exact ⟨mem_univ v, hv⟩
  rcases mem_union.1 hv' with hvA | hvR
  · exact (card_le_card (componentOff_subset_side G hU he hvA)).trans hA.le
  · have hU' : R ∪ A = univ \ S := by rw [union_comm]; exact hU
    have := card_le_card (componentOff_subset_side G hU' he.symm hvR)
    omega

/-! ### Lemma W: the weighted-count identity -/

/-- **Lemma W.** For a finite family `𝓟` of pairs, an emptiness predicate and a weight
`Z : 𝓟 → ℕ` with `1 ≤ Z(P) ≤ #{empty pairs}` on every empty pair, the weighted count
`Σ_P 1[P empty] / Z(P)` is at least the indicator of "some pair is empty". -/
theorem weightedCount_ge_indicator {ι : Type*} (𝓟 : Finset ι) (empty : ι → Prop)
    [DecidablePred empty] (Z : ι → ℕ)
    (hZ : ∀ P ∈ 𝓟, empty P → 1 ≤ Z P ∧ Z P ≤ (𝓟.filter empty).card) :
    (if ∃ P ∈ 𝓟, empty P then (1 : ℝ) else 0) ≤
      ∑ P ∈ 𝓟, if empty P then (1 : ℝ) / Z P else 0 := by
  split_ifs with h
  · obtain ⟨P₀, hP₀, hE₀⟩ := h
    have hXpos : 0 < (𝓟.filter empty).card := card_pos.2 ⟨P₀, mem_filter.2 ⟨hP₀, hE₀⟩⟩
    calc (1 : ℝ) = ∑ P ∈ 𝓟.filter empty, (1 : ℝ) / (𝓟.filter empty).card := by
          rw [sum_const, nsmul_eq_mul, mul_one_div_cancel]
          exact_mod_cast hXpos.ne'
      _ ≤ ∑ P ∈ 𝓟.filter empty, (1 : ℝ) / Z P := by
          refine sum_le_sum (fun P hP => ?_)
          obtain ⟨hP, hE⟩ := mem_filter.1 hP
          obtain ⟨h1, h2⟩ := hZ P hP hE
          exact one_div_le_one_div_of_le (by exact_mod_cast h1) (by exact_mod_cast h2)
      _ = ∑ P ∈ 𝓟, if empty P then (1 : ℝ) / Z P else 0 := by rw [sum_filter]
  · exact sum_nonneg (fun P _ => by split_ifs <;> positivity)

/-- Lemma W when some pair is empty: the weighted count is at least one. -/
theorem one_le_weightedCount {ι : Type*} (𝓟 : Finset ι) (empty : ι → Prop)
    [DecidablePred empty] (Z : ι → ℕ)
    (hZ : ∀ P ∈ 𝓟, empty P → 1 ≤ Z P ∧ Z P ≤ (𝓟.filter empty).card)
    (h : ∃ P ∈ 𝓟, empty P) :
    (1 : ℝ) ≤ ∑ P ∈ 𝓟, if empty P then (1 : ℝ) / Z P else 0 := by
  have := weightedCount_ge_indicator 𝓟 empty Z hZ
  simpa [h] using this

/-- The ordered pairs `(A, R)` with `|A| = t`, `|R| = r`, `R ⊆ V ∖ A`. -/
def pairIndices (t r : ℕ) : Finset (Σ _ : Finset V, Finset V) :=
  (univ.powersetCard t).sigma (fun A => (univ \ A).powersetCard r)

theorem mem_pairIndices {t r : ℕ} {q : Σ _ : Finset V, Finset V} :
    q ∈ pairIndices t r ↔ q.1.card = t ∧ q.2 ⊆ univ \ q.1 ∧ q.2.card = r := by
  simp only [pairIndices, mem_sigma, mem_powersetCard, subset_univ, true_and]

theorem card_pairIndices (t r : ℕ) :
    (pairIndices (V := V) t r).card = (Fintype.card V).choose t * (Fintype.card V - t).choose r := by
  unfold pairIndices
  rw [card_sigma]
  rw [Finset.sum_congr rfl (g := fun _ => (Fintype.card V - t).choose r)
    (fun A hA => by rw [card_powersetCard, card_univ_sdiff, (mem_powersetCard.1 hA).2])]
  rw [sum_const, card_powersetCard, card_univ, smul_eq_mul]

/-- Every graph of pathwidth `≤ k < n` has an exact-size empty pair in `pairIndices t r`. -/
theorem exists_mem_pairIndices_isEmptyPair (k : ℕ) (hpw : pathwidth G ≤ k)
    (hk : k < Fintype.card V) :
    ∃ q ∈ pairIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2),
      IsEmptyPair G q.1 q.2 := by
  obtain ⟨A, R, S, hAR, _, _, _, hA, hR, _, hE⟩ := exists_balanced_separator G k hpw hk
  refine ⟨⟨A, R⟩, mem_pairIndices.2 ⟨hA, ?_, hR⟩, hE⟩
  intro r hr
  rw [mem_sdiff]
  exact ⟨mem_univ r, fun hrA => Finset.disjoint_left.1 hAR hrA hr⟩

open scoped Classical in
/-- **Lemma W, the `G(n, p)` reading.** For any weight `Z(G, P)` with
`1 ≤ Z ≤ #{empty exact-size pairs of G}` on the empty pairs of every graph,
`P(pathwidth ≤ k) ≤ E[Σ_P 1[P empty] / Z(G, P)]`. -/
theorem weightedSum_graphsOfPathwidthLe_le_weighted (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : ℕ) (hk : k < Fintype.card V)
    (Z : SimpleGraph V → (Σ _ : Finset V, Finset V) → ℕ)
    (hZ : ∀ (G : SimpleGraph V) q,
      q ∈ pairIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2) →
      IsEmptyPair G q.1 q.2 → 1 ≤ Z G q ∧ Z G q ≤
        ((pairIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2)).filter
          (fun q => IsEmptyPair G q.1 q.2)).card) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ G : SimpleGraph V, gnpWeight p G *
        ∑ q ∈ pairIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2),
          if IsEmptyPair G q.1 q.2 then (1 : ℝ) / Z G q else 0 := by
  set 𝓟 := pairIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2)
  have hY : ∀ G : SimpleGraph V, 0 ≤ ∑ q ∈ 𝓟, if IsEmptyPair G q.1 q.2 then (1 : ℝ) / Z G q else 0 :=
    fun G => sum_nonneg (fun q _ => by split_ifs <;> positivity)
  calc ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G
      ≤ ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G *
          ∑ q ∈ 𝓟, if IsEmptyPair G q.1 q.2 then (1 : ℝ) / Z G q else 0 := by
        refine sum_le_sum (fun G hG => ?_)
        have hpw := mem_graphsOfPathwidthLe.1 hG
        have hind := one_le_weightedCount 𝓟 (fun q => IsEmptyPair G q.1 q.2) (Z G)
          (fun q hq hE => hZ G q hq hE) (exists_mem_pairIndices_isEmptyPair G k hpw hk)
        calc gnpWeight p G = gnpWeight p G * 1 := (mul_one _).symm
          _ ≤ _ := mul_le_mul_of_nonneg_left hind (gnpWeight_nonneg hp0 hp1 G)
    _ ≤ _ := sum_le_sum_of_subset_of_nonneg (subset_univ _)
          (fun G _ _ => mul_nonneg (gnpWeight_nonneg hp0 hp1 G) (hY G))

/-! ### The union bound over separators -/

/-- The graphs on `V` in the event `E_bip(S)` (pair form), at width `k`. -/
noncomputable def bipGraphs (S : Finset V) (k : ℕ) : Finset (SimpleGraph V) := by
  classical exact univ.filter (fun G => IsBalancedBip G S k)

theorem mem_bipGraphs {S : Finset V} {k : ℕ} {G : SimpleGraph V} :
    G ∈ bipGraphs S k ↔ IsBalancedBip G S k := by
  simp [bipGraphs]

open scoped Classical in
/-- **The union bound over separators.** For `0 ≤ p ≤ 1` and `k < n`,
`Σ_{pathwidth G ≤ k} gnpWeight p G ≤ Σ_{|S| = k} Σ_{G ∈ E_bip(S)} gnpWeight p G`. -/
theorem weightedSum_graphsOfPathwidthLe_le_sum_separators (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : ℕ) (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ S ∈ (univ : Finset V).powersetCard k, ∑ G ∈ bipGraphs S k, gnpWeight p G := by
  calc ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G
      ≤ ∑ G ∈ ((univ : Finset V).powersetCard k).biUnion (fun S => bipGraphs S k),
          gnpWeight p G := by
        refine sum_le_sum_of_subset_of_nonneg (fun G hG => ?_)
          (fun G _ _ => gnpWeight_nonneg hp0 hp1 G)
        obtain ⟨S, hS, hbip⟩ := exists_isBalancedBip G k (mem_graphsOfPathwidthLe.1 hG) hk
        exact mem_biUnion.2 ⟨S, mem_powersetCard.2 ⟨subset_univ _, hS⟩, mem_bipGraphs.2 hbip⟩
    _ ≤ _ := sum_biUnion_le_sum_of_nonneg _ _ _ (gnpWeight_nonneg hp0 hp1)

/-! ### The factorisation step: graphs on `V` against graphs on `V ∖ S` -/

section Factorisation

variable (G : SimpleGraph V)

/-- `G − S` kept on the vertex set `V`: the edges of `G` with both ends off `S`. -/
def restrictOff (S : Finset V) : SimpleGraph V where
  Adj u v := G.Adj u v ∧ u ∉ S ∧ v ∉ S
  symm := by
    constructor
    intro u v ⟨h, hu, hv⟩
    exact ⟨G.adj_symm h, hv, hu⟩
  loopless := by
    constructor
    intro v ⟨h, _, _⟩
    exact G.irrefl h

theorem restrictOff_adj {S : Finset V} {u v : V} :
    (restrictOff G S).Adj u v ↔ G.Adj u v ∧ u ∉ S ∧ v ∉ S := Iff.rfl

theorem restrictOff_restrictOff (S : Finset V) :
    restrictOff (restrictOff G S) S = restrictOff G S := by
  ext u v
  simp only [restrictOff_adj]
  tauto

/-- A pair avoids `S`: both its ends are off `S`. -/
def AvoidsSet (S : Finset V) (e : Sym2 V) : Prop := ∀ v ∈ e, v ∉ S

theorem avoidsSet_mk {S : Finset V} {u v : V} : AvoidsSet S s(u, v) ↔ u ∉ S ∧ v ∉ S := by
  simp [AvoidsSet, Sym2.mem_iff, or_imp, forall_and]

open scoped Classical in
/-- The non-diagonal pairs with both ends off `S`: the pairs of `V ∖ S`. -/
noncomputable def pairsOff (S : Finset V) : Finset (Sym2 V) :=
  (edges (⊤ : SimpleGraph V)).filter (AvoidsSet S)

open scoped Classical in
/-- The non-diagonal pairs meeting `S`. -/
noncomputable def pairsMeeting (S : Finset V) : Finset (Sym2 V) :=
  (edges (⊤ : SimpleGraph V)).filter (fun e => ¬ AvoidsSet S e)

open scoped Classical in
theorem card_pairsOff_add_card_pairsMeeting (S : Finset V) :
    (pairsOff S).card + (pairsMeeting S).card = (Fintype.card V).choose 2 := by
  rw [← card_edges_top (V := V)]
  exact card_filter_add_card_filter_not _

open scoped Classical in
theorem disjoint_pairsOff_pairsMeeting (S : Finset V) : Disjoint (pairsOff S) (pairsMeeting S) :=
  disjoint_filter_filter_not _ _ _

open scoped Classical in
theorem pairsMeeting_subset_top (S : Finset V) : pairsMeeting S ⊆ edges (⊤ : SimpleGraph V) :=
  filter_subset _ _

open scoped Classical in
theorem mem_pairsMeeting {S : Finset V} {e : Sym2 V} :
    e ∈ pairsMeeting S ↔ e ∈ edges (⊤ : SimpleGraph V) ∧ ¬ AvoidsSet S e := by
  simp [pairsMeeting]

open scoped Classical in
theorem mem_pairsOff {S : Finset V} {e : Sym2 V} :
    e ∈ pairsOff S ↔ e ∈ edges (⊤ : SimpleGraph V) ∧ AvoidsSet S e := by
  simp [pairsOff]

open scoped Classical in
/-- The edge set of `G − S` is the edge set of `G` filtered to the pairs off `S`. -/
theorem edges_restrictOff (S : Finset V) :
    edges (restrictOff G S) = (edges G).filter (AvoidsSet S) := by
  ext e
  induction e using Sym2.ind with
  | _ u v =>
    rw [mem_filter, mem_edges, mem_edges, SimpleGraph.mem_edgeSet, SimpleGraph.mem_edgeSet,
      restrictOff_adj, avoidsSet_mk]

open scoped Classical in
theorem edges_subset_pairsOff_of_restrictOff_eq {S : Finset V} {H : SimpleGraph V}
    (hH : restrictOff H S = H) : edges H ⊆ pairsOff S := by
  intro e he
  rw [← hH, edges_restrictOff] at he
  rw [mem_pairsOff]
  exact ⟨edges_subset_top _ (filter_subset _ _ he), (mem_filter.1 he).2⟩

/-- `E_bip(S)` depends on `G` only through its edges off `S`. -/
theorem isBalancedBip_restrictOff (S : Finset V) (k : ℕ) :
    IsBalancedBip (restrictOff G S) S k ↔ IsBalancedBip G S k := by
  have key : ∀ A R : Finset V, A ∪ R = univ \ S →
      (IsEmptyPair (restrictOff G S) A R ↔ IsEmptyPair G A R) := by
    intro A R hU
    have hA : ∀ a ∈ A, a ∉ S := fun a ha =>
      (mem_sdiff.1 (hU ▸ mem_union_left R ha)).2
    have hR : ∀ r ∈ R, r ∉ S := fun r hr =>
      (mem_sdiff.1 (hU ▸ mem_union_right A hr)).2
    constructor
    · intro h a ha r hr hadj
      exact h a ha r hr ⟨hadj, hA a ha, hR r hr⟩
    · intro h a ha r hr hadj
      exact h a ha r hr hadj.1
  constructor
  · rintro ⟨A, R, hAR, hU, hA, hR, hE⟩
    exact ⟨A, R, hAR, hU, hA, hR, (key A R hU).1 hE⟩
  · rintro ⟨A, R, hAR, hU, hA, hR, hE⟩
    exact ⟨A, R, hAR, hU, hA, hR, (key A R hU).2 hE⟩

theorem edges_coe (H : SimpleGraph V) : ((edges H : Finset (Sym2 V)) : Set (Sym2 V)) = H.edgeSet := by
  ext e
  simp [mem_edges]

open scoped Classical in
/-- **The factorisation step.** For a graph `H` with no edge meeting `S`, the graphs `G`
on `V` with `restrictOff G S = H` are the unions of `H` with a subset of the pairs meeting
`S`; their total `G(n, p)` weight is `p^|E(H)| (1 − p)^(|pairsOff S| − |E(H)|)` — the
`G(N, p)` weight of `H` as a graph on `V ∖ S` — because the subsets of the pairs meeting
`S` carry total weight `(p + (1 − p))^|pairsMeeting S| = 1`. -/
theorem sum_gnpWeight_fiber (S : Finset V) {H : SimpleGraph V} (hH : restrictOff H S = H)
    (p : ℝ) :
    ∑ G ∈ (univ : Finset (SimpleGraph V)).filter (fun G => restrictOff G S = H), gnpWeight p G =
      p ^ (edges H).card * (1 - p) ^ ((pairsOff S).card - (edges H).card) := by
  have hEH : edges H ⊆ pairsOff S := edges_subset_pairsOff_of_restrictOff_eq hH
  have hHtop : edges H ⊆ edges (⊤ : SimpleGraph V) := edges_subset_top H
  have hcardH : (edges H).card ≤ (pairsOff S).card := card_le_card hEH
  have hsum := card_pairsOff_add_card_pairsMeeting (V := V) S
  have hHS : ∀ u v, H.Adj u v → u ∉ S ∧ v ∉ S := fun u v h => by
    rw [← hH] at h; exact h.2
  -- the bijection `F ↦ H ∪ F` from the subsets of the pairs meeting `S` onto the fibre
  have hbij : ∑ F ∈ (pairsMeeting S).powerset,
      p ^ ((edges H).card + F.card) *
        (1 - p) ^ ((Fintype.card V).choose 2 - ((edges H).card + F.card)) =
      ∑ G ∈ (univ : Finset (SimpleGraph V)).filter (fun G => restrictOff G S = H),
        gnpWeight p G := by
    refine sum_nbij' (fun F => SimpleGraph.fromEdgeSet ((edges H ∪ F : Finset (Sym2 V)) : Set (Sym2 V)))
      (fun G => (edges G).filter (fun e => ¬ AvoidsSet S e)) ?_ ?_ ?_ ?_ ?_
    · -- `H ∪ F` restricts back to `H`
      intro F hF
      have hFm : F ⊆ pairsMeeting S := mem_powerset.1 hF
      rw [mem_filter]
      refine ⟨mem_univ _, ?_⟩
      ext u v
      rw [restrictOff_adj, SimpleGraph.fromEdgeSet_adj, mem_coe, mem_union]
      constructor
      · rintro ⟨⟨hmem | hmem, hne⟩, hu, hv⟩
        · exact (SimpleGraph.mem_edgeSet H).1 (mem_edges.1 hmem)
        · exact absurd (avoidsSet_mk.2 ⟨hu, hv⟩) (mem_pairsMeeting.1 (hFm hmem)).2
      · intro h
        obtain ⟨hu, hv⟩ := hHS u v h
        exact ⟨⟨Or.inl (mem_edges.2 ((SimpleGraph.mem_edgeSet H).2 h)), H.ne_of_adj h⟩, hu, hv⟩
    · -- the pairs of `G` meeting `S` form a subset of `pairsMeeting S`
      intro G _
      rw [mem_powerset]
      intro e he
      rw [mem_filter] at he
      exact mem_pairsMeeting.2 ⟨edges_subset_top G he.1, he.2⟩
    · -- left inverse
      intro F hF
      have hFm : F ⊆ pairsMeeting S := mem_powerset.1 hF
      rw [edges_fromEdgeSet _ (union_subset hHtop (hFm.trans (pairsMeeting_subset_top S))),
        filter_union]
      have h1 : (edges H).filter (fun e => ¬ AvoidsSet S e) = ∅ :=
        filter_eq_empty_iff.2 (fun e he hne => hne (mem_pairsOff.1 (hEH he)).2)
      have h2 : F.filter (fun e => ¬ AvoidsSet S e) = F :=
        filter_true_of_mem (fun e he => (mem_pairsMeeting.1 (hFm he)).2)
      rw [h1, h2, empty_union]
    · -- right inverse
      intro G hG
      have hG' : restrictOff G S = H := (mem_filter.1 hG).2
      have : edges H ∪ (edges G).filter (fun e => ¬ AvoidsSet S e) = edges G := by
        rw [← hG', edges_restrictOff]
        exact filter_union_filter_not_eq _ _
      rw [this, edges_coe, SimpleGraph.fromEdgeSet_edgeSet]
    · -- the weights agree
      intro F hF
      have hFm : F ⊆ pairsMeeting S := mem_powerset.1 hF
      have hdisj : Disjoint (edges H) F :=
        Finset.disjoint_of_subset_left hEH
          (Finset.disjoint_of_subset_right hFm (disjoint_pairsOff_pairsMeeting S))
      unfold gnpWeight
      rw [edges_fromEdgeSet _ (union_subset hHtop (hFm.trans (pairsMeeting_subset_top S))),
        card_union_of_disjoint hdisj]
  rw [← hbij]
  calc ∑ F ∈ (pairsMeeting S).powerset,
        p ^ ((edges H).card + F.card) *
          (1 - p) ^ ((Fintype.card V).choose 2 - ((edges H).card + F.card))
      = ∑ F ∈ (pairsMeeting S).powerset,
          (p ^ (edges H).card * (1 - p) ^ ((pairsOff S).card - (edges H).card)) *
            (p ^ F.card * (1 - p) ^ ((pairsMeeting S).card - F.card)) := by
        refine sum_congr rfl (fun F hF => ?_)
        have hF' : F.card ≤ (pairsMeeting S).card := card_le_card (mem_powerset.1 hF)
        have : (Fintype.card V).choose 2 - ((edges H).card + F.card) =
            ((pairsOff S).card - (edges H).card) + ((pairsMeeting S).card - F.card) := by
          omega
        rw [this, pow_add, pow_add]
        ring
    _ = (p ^ (edges H).card * (1 - p) ^ ((pairsOff S).card - (edges H).card)) *
          (p + (1 - p)) ^ (pairsMeeting S).card := by
        rw [← mul_sum, sum_pow_mul_eq_add_pow]
    _ = _ := by simp

/-- The graphs on `V` with no edge meeting `S`: the graphs on `V ∖ S`. -/
noncomputable def offGraphs (S : Finset V) : Finset (SimpleGraph V) := by
  classical exact univ.filter (fun H => restrictOff H S = H)

theorem mem_offGraphs {S : Finset V} {H : SimpleGraph V} :
    H ∈ offGraphs S ↔ restrictOff H S = H := by
  simp [offGraphs]

open scoped Classical in
/-- **The inner probability of `E_bip(S)` is a weighted count over the graphs on `V ∖ S`**,
exactly: `Σ_{G ∈ E_bip(S)} gnpWeight p G = Σ_{H on V ∖ S, H ∈ E_bip(S)} p^|E(H)| (1 − p)^(|pairsOff S| − |E(H)|)`. -/
theorem sum_gnpWeight_bipGraphs (S : Finset V) (k : ℕ) (p : ℝ) :
    ∑ G ∈ bipGraphs S k, gnpWeight p G =
      ∑ H ∈ (offGraphs S).filter (fun H => IsBalancedBip H S k),
        p ^ (edges H).card * (1 - p) ^ ((pairsOff S).card - (edges H).card) := by
  have hmaps : ∀ G ∈ bipGraphs S k,
      restrictOff G S ∈ (offGraphs S).filter (fun H => IsBalancedBip H S k) := by
    intro G hG
    rw [mem_filter, mem_offGraphs, restrictOff_restrictOff, isBalancedBip_restrictOff]
    exact ⟨rfl, mem_bipGraphs.1 hG⟩
  rw [← sum_fiberwise_of_maps_to hmaps]
  refine sum_congr rfl (fun H hH => ?_)
  obtain ⟨hHoff, hHbip⟩ := mem_filter.1 hH
  rw [mem_offGraphs] at hHoff
  rw [← sum_gnpWeight_fiber S hHoff p]
  refine sum_congr ?_ (fun _ _ => rfl)
  ext G
  simp only [mem_filter, mem_bipGraphs, mem_univ, true_and]
  constructor
  · exact fun h => h.2
  · intro h
    refine ⟨?_, h⟩
    rw [← isBalancedBip_restrictOff, h]
    exact hHbip

/-! ### `|pairsOff S| = (n − |S|).choose 2` -/

open scoped Classical in
/-- The pairs off `S` are the image of the edges of the complete graph on `V ∖ S`. -/
theorem pairsOff_eq_image (S : Finset V) :
    pairsOff S = (edges (⊤ : SimpleGraph ↥(univ \ S))).image (Sym2.map Subtype.val) := by
  ext e
  induction e using Sym2.ind with
  | _ u v =>
    rw [mem_pairsOff, mem_edges_top, Sym2.mk_isDiag_iff, avoidsSet_mk, mem_image]
    constructor
    · rintro ⟨hne, hu, hv⟩
      refine ⟨s(⟨u, mem_sdiff.2 ⟨mem_univ u, hu⟩⟩, ⟨v, mem_sdiff.2 ⟨mem_univ v, hv⟩⟩), ?_, ?_⟩
      · rw [mem_edges_top, Sym2.mk_isDiag_iff]
        intro h
        exact hne (congrArg Subtype.val h)
      · rw [Sym2.map_mk]
    · rintro ⟨e', he', hmap⟩
      induction e' using Sym2.ind with
      | _ a b =>
        rw [mem_edges_top, Sym2.mk_isDiag_iff] at he'
        rw [Sym2.map_mk, Sym2.eq_iff] at hmap
        have ha : (a : V) ∉ S := (mem_sdiff.1 a.2).2
        have hb : (b : V) ∉ S := (mem_sdiff.1 b.2).2
        have hab : (a : V) ≠ b := fun h => he' (Subtype.ext h)
        rcases hmap with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
        · exact ⟨hab, ha, hb⟩
        · exact ⟨hab.symm, hb, ha⟩

open scoped Classical in
/-- **`|pairsOff S| = (n − |S|).choose 2`**: the pairs off `S` are the pairs of `V ∖ S`. -/
theorem card_pairsOff (S : Finset V) :
    (pairsOff S).card = (Fintype.card V - S.card).choose 2 := by
  rw [pairsOff_eq_image, card_image_of_injective _ (Sym2.map.injective Subtype.val_injective),
    card_edges_top, Fintype.card_coe, card_univ_sdiff]

/-! ### Theorem S, separator-summed form -/

open scoped Classical in
/-- The inner weighted count of `E_bip(S)` on the graphs on `V ∖ S`, with the weight written
with `(n − |S|).choose 2` — the `G(N, p)` probability of `E_bip` when `|S| = k`, up to the
relabelling of `V ∖ S` that is on paper. -/
noncomputable def innerBip (p : ℝ) (S : Finset V) (k : ℕ) : ℝ :=
  ∑ H ∈ (offGraphs S).filter (fun H => IsBalancedBip H S k),
    p ^ (edges H).card * (1 - p) ^ ((Fintype.card V - S.card).choose 2 - (edges H).card)

open scoped Classical in
theorem sum_gnpWeight_bipGraphs_eq_innerBip (S : Finset V) (k : ℕ) (p : ℝ) :
    ∑ G ∈ bipGraphs S k, gnpWeight p G = innerBip p S k := by
  rw [sum_gnpWeight_bipGraphs, innerBip, card_pairsOff]

open scoped Classical in
/-- **Theorem S, separator-summed form.** For `0 ≤ p ≤ 1` and `k < n`,
`P(pathwidth ≤ k) ≤ Σ_{|S| = k} innerBip p S k`, where `innerBip p S k` is the exact
`G(n, p)` probability of `E_bip(S)`, written as a weighted count over the graphs on
`V ∖ S`. The union bound over `S` is the only inequality. -/
theorem weightedSum_graphsOfPathwidthLe_le_separator (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : ℕ) (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ S ∈ (univ : Finset V).powersetCard k, innerBip p S k := by
  refine (weightedSum_graphsOfPathwidthLe_le_sum_separators p hp0 hp1 k hk).trans_eq ?_
  exact sum_congr rfl (fun S _ => sum_gnpWeight_bipGraphs_eq_innerBip S k p)

end Factorisation

/-! ### The relabelling: the inner count does not depend on `S` -/

section Relabelling

/-- A permutation of `V` with `S₀` mapped onto `S`, whenever `|S₀| = |S|`. -/
theorem exists_equiv_mem_iff {S₀ S : Finset V} (h : S₀.card = S.card) :
    ∃ e : V ≃ V, ∀ x, e x ∈ S ↔ x ∈ S₀ := by
  classical
  have h1 : Fintype.card (↥(S₀ : Set V)) = Fintype.card (↥(S : Set V)) := by
    simp [h]
  have h2 : Fintype.card (↥((S₀ : Set V)ᶜ)) = Fintype.card (↥((S : Set V)ᶜ)) := by
    rw [Fintype.card_compl_set, Fintype.card_compl_set, h1]
  obtain ⟨e₁⟩ := Fintype.card_eq.1 h1
  obtain ⟨e₂⟩ := Fintype.card_eq.1 h2
  refine ⟨(Equiv.Set.sumCompl (S₀ : Set V)).symm.trans
    ((Equiv.sumCongr e₁ e₂).trans (Equiv.Set.sumCompl (S : Set V))), fun x => ?_⟩
  by_cases hx : x ∈ S₀
  · have hx' : x ∈ (S₀ : Set V) := mem_coe.2 hx
    simp only [Equiv.trans_apply, Equiv.Set.sumCompl_symm_apply_of_mem hx',
      Equiv.sumCongr_apply, Sum.map_inl, Equiv.Set.sumCompl_apply_inl]
    exact ⟨fun _ => hx, fun _ => mem_coe.1 (e₁ ⟨x, hx'⟩).2⟩
  · have hx' : x ∉ (S₀ : Set V) := fun h => hx (mem_coe.1 h)
    simp only [Equiv.trans_apply, Equiv.Set.sumCompl_symm_apply_of_notMem hx',
      Equiv.sumCongr_apply, Sum.map_inr, Equiv.Set.sumCompl_apply_inr]
    refine ⟨fun h => absurd (mem_coe.2 h) (e₂ ⟨x, hx'⟩).2, fun h => absurd h hx⟩

/-- The graph `G` relabelled by `e`: `u ~ v` iff `e⁻¹ u ~ e⁻¹ v` in `G`, so that the edge
`{x, y}` of `G` becomes `{e x, e y}`. -/
def relabel (e : V ≃ V) (G : SimpleGraph V) : SimpleGraph V :=
  G.comap e.symm

theorem relabel_adj {e : V ≃ V} {G : SimpleGraph V} {u v : V} :
    (relabel e G).Adj u v ↔ G.Adj (e.symm u) (e.symm v) := Iff.rfl

theorem relabel_symm_relabel (e : V ≃ V) (G : SimpleGraph V) :
    relabel e.symm (relabel e G) = G := by
  ext u v
  simp [relabel_adj]

theorem relabel_relabel_symm (e : V ≃ V) (G : SimpleGraph V) :
    relabel e (relabel e.symm G) = G := by
  ext u v
  simp [relabel_adj]

open scoped Classical in
theorem edges_relabel (e : V ≃ V) (G : SimpleGraph V) :
    edges (relabel e G) = (edges G).image (Sym2.map e) := by
  ext x
  induction x using Sym2.ind with
  | _ u v =>
    rw [mem_edges, SimpleGraph.mem_edgeSet, relabel_adj, mem_image]
    constructor
    · intro h
      refine ⟨s(e.symm u, e.symm v), mem_edges.2 ((SimpleGraph.mem_edgeSet G).2 h), ?_⟩
      rw [Sym2.map_mk, Equiv.apply_symm_apply, Equiv.apply_symm_apply]
    · rintro ⟨x, hx, hmap⟩
      induction x using Sym2.ind with
      | _ a b =>
        rw [Sym2.map_mk, Sym2.eq_iff] at hmap
        have hab : G.Adj a b := (SimpleGraph.mem_edgeSet G).1 (mem_edges.1 hx)
        rcases hmap with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
        · simpa using hab
        · simpa using hab.symm

theorem card_edges_relabel (e : V ≃ V) (G : SimpleGraph V) :
    (edges (relabel e G)).card = (edges G).card := by
  classical
  rw [edges_relabel, card_image_of_injective _ (Sym2.map.injective e.injective)]

theorem gnpWeight_relabel (p : ℝ) (e : V ≃ V) (G : SimpleGraph V) :
    gnpWeight p (relabel e G) = gnpWeight p G := by
  unfold gnpWeight
  rw [card_edges_relabel]

/-- Relabelling commutes with restriction when `e` carries `S₀` onto `S`. -/
theorem restrictOff_relabel {e : V ≃ V} {S₀ S : Finset V} (hS : ∀ x, e x ∈ S ↔ x ∈ S₀)
    (G : SimpleGraph V) : restrictOff (relabel e G) S = relabel e (restrictOff G S₀) := by
  ext u v
  rw [restrictOff_adj, relabel_adj, relabel_adj, restrictOff_adj]
  have hu : u ∈ S ↔ e.symm u ∈ S₀ := by rw [← hS, Equiv.apply_symm_apply]
  have hv : v ∈ S ↔ e.symm v ∈ S₀ := by rw [← hS, Equiv.apply_symm_apply]
  rw [hu, hv]

theorem isEmptyPair_relabel (e : V ≃ V) (G : SimpleGraph V) (A R : Finset V) :
    IsEmptyPair (relabel e G) (A.map e.toEmbedding) (R.map e.toEmbedding) ↔
      IsEmptyPair G A R := by
  constructor
  · intro h a ha r hr hadj
    refine h (e a) (mem_map_of_mem _ ha) (e r) (mem_map_of_mem _ hr) ?_
    rw [relabel_adj, Equiv.symm_apply_apply, Equiv.symm_apply_apply]
    exact hadj
  · intro h a' ha' r' hr' hadj
    rw [mem_map_equiv] at ha' hr'
    exact h _ ha' _ hr' hadj

theorem map_univ_sdiff {e : V ≃ V} {S₀ S : Finset V} (hS : ∀ x, e x ∈ S ↔ x ∈ S₀) :
    (univ \ S₀).map e.toEmbedding = univ \ S := by
  ext y
  rw [mem_map_equiv, mem_sdiff, mem_sdiff, ← hS, Equiv.apply_symm_apply]
  simp

/-- `E_bip` is invariant under relabelling (one direction; the other is the inverse). -/
theorem isBalancedBip_relabel_of {e : V ≃ V} {S₀ S : Finset V} (hS : ∀ x, e x ∈ S ↔ x ∈ S₀)
    {G : SimpleGraph V} {k : ℕ} (h : IsBalancedBip G S₀ k) : IsBalancedBip (relabel e G) S k := by
  obtain ⟨A, R, hAR, hU, hA, hR, hE⟩ := h
  refine ⟨A.map e.toEmbedding, R.map e.toEmbedding, (disjoint_map _).2 hAR, ?_,
    by rw [card_map, hA], by rw [card_map, hR], (isEmptyPair_relabel e G A R).2 hE⟩
  rw [← map_union, hU, map_univ_sdiff hS]

theorem isBalancedBip_relabel_iff {e : V ≃ V} {S₀ S : Finset V} (hS : ∀ x, e x ∈ S ↔ x ∈ S₀)
    (G : SimpleGraph V) (k : ℕ) : IsBalancedBip (relabel e G) S k ↔ IsBalancedBip G S₀ k := by
  refine ⟨fun h => ?_, isBalancedBip_relabel_of hS⟩
  have hS' : ∀ x, e.symm x ∈ S₀ ↔ x ∈ S := fun x => by
    rw [← hS, Equiv.apply_symm_apply]
  have := isBalancedBip_relabel_of hS' h
  rwa [relabel_symm_relabel] at this

open scoped Classical in
/-- **The inner count is the same for every `S` of a given size**: relabel `V` by a
permutation carrying `S₀` onto `S`. -/
theorem innerBip_eq_of_card_eq (p : ℝ) {S₀ S : Finset V} (h : S₀.card = S.card) (k : ℕ) :
    innerBip p S₀ k = innerBip p S k := by
  obtain ⟨e, hS⟩ := exists_equiv_mem_iff h
  have hS' : ∀ x, e.symm x ∈ S₀ ↔ x ∈ S := fun x => by rw [← hS, Equiv.apply_symm_apply]
  unfold innerBip
  rw [h]
  refine sum_nbij' (relabel e) (relabel e.symm) ?_ ?_ ?_ ?_ ?_
  · intro H hH
    rw [mem_filter, mem_offGraphs] at hH ⊢
    rw [restrictOff_relabel hS, hH.1]
    exact ⟨rfl, isBalancedBip_relabel_of hS hH.2⟩
  · intro H hH
    rw [mem_filter, mem_offGraphs] at hH ⊢
    rw [restrictOff_relabel hS', hH.1]
    exact ⟨rfl, isBalancedBip_relabel_of hS' hH.2⟩
  · intro H _
    exact relabel_symm_relabel e H
  · intro H _
    exact relabel_relabel_symm e H
  · intro H _
    rw [card_edges_relabel]

open scoped Classical in
/-- **Theorem S** (`reports/separator_moment.md` §8.1), finite and exact: for `0 ≤ p ≤ 1`,
`k < n` and any `k`-set `S₀`,
`P(pathwidth ≤ k) ≤ n.choose k · innerBip p S₀ k`, where `innerBip p S₀ k` is the
`G(n, p)` probability of `E_bip(S₀)` — a weighted count over the graphs on `V ∖ S₀` with the
`G(N, p)` weights, `N = n − k`. The union bound over the `n.choose k` separators is the only
inequality; the inner probability is the same for every `S`. -/
theorem weightedSum_graphsOfPathwidthLe_le_choose_mul_innerBip (p : ℝ) (hp0 : 0 ≤ p)
    (hp1 : p ≤ 1) (k : ℕ) (hk : k < Fintype.card V) (S₀ : Finset V) (hS₀ : S₀.card = k) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ((Fintype.card V).choose k : ℝ) * innerBip p S₀ k := by
  refine (weightedSum_graphsOfPathwidthLe_le_separator p hp0 hp1 k hk).trans_eq ?_
  rw [sum_congr rfl (g := fun _ => innerBip p S₀ k) (fun S hS =>
    (innerBip_eq_of_card_eq p (by rw [hS₀, (mem_powersetCard.1 hS).2]) k).symm)]
  rw [sum_const, card_powersetCard, card_univ, nsmul_eq_mul]

end Relabelling

/-! ### Theorem Cl: the union bound over closed pairs -/

section ClosedUnion

/-- The ordered disjoint pairs `(A, R)` with `|A| ≥ t` and `|R| ≥ r`: the index set of the
closed-pair count (the separator `V ∖ (A ∪ R)` then has at most `n − t − r` vertices). -/
def closedIndices (t r : ℕ) : Finset (Σ _ : Finset V, Finset V) :=
  ((univ : Finset (Finset V)).filter (fun A => t ≤ A.card)).sigma
    (fun A => (univ \ A).powerset.filter (fun R => r ≤ R.card))

theorem mem_closedIndices {t r : ℕ} {q : Σ _ : Finset V, Finset V} :
    q ∈ closedIndices t r ↔ t ≤ q.1.card ∧ q.2 ⊆ univ \ q.1 ∧ r ≤ q.2.card := by
  simp only [closedIndices, mem_sigma, mem_filter, mem_univ, true_and, mem_powerset]

/-- The graphs on `V` for which `(A, R)` is a closed pair. -/
noncomputable def closedPairGraphs (A R : Finset V) : Finset (SimpleGraph V) := by
  classical exact univ.filter (fun G => IsClosedPair G A R)

open scoped Classical in
theorem mem_closedPairGraphs {A R : Finset V} {G : SimpleGraph V} :
    G ∈ closedPairGraphs A R ↔ IsClosedPair G A R := by
  simp [closedPairGraphs]

open scoped Classical in
/-- **The union bound of Theorem Cl.** `P(pathwidth ≤ k) ≤ Σ_{(A, R) : |A| ≥ t, |R| ≥ r} P((A, R) is closed)`,
the sum over the ordered disjoint pairs of at least the forced sizes. The independence step —
that the inner sum is `(1 − p)^(|A||R|) ((1 − (1 − p)^|A|)(1 − (1 − p)^|R|))^|S|` — is on paper
(`reports/separator_moment.md` §8.2). -/
theorem weightedSum_graphsOfPathwidthLe_le_sum_closedPairs (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : ℕ) (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ q ∈ closedIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2),
        ∑ G ∈ closedPairGraphs q.1 q.2, gnpWeight p G := by
  set t := (Fintype.card V - k + 1) / 2
  set r := (Fintype.card V - k) / 2
  calc ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G
      ≤ ∑ G ∈ (closedIndices (V := V) t r).biUnion (fun q => closedPairGraphs q.1 q.2),
          gnpWeight p G := by
        refine sum_le_sum_of_subset_of_nonneg (fun G hG => ?_)
          (fun G _ _ => gnpWeight_nonneg hp0 hp1 G)
        obtain ⟨A, R, hcl, _, hA, hR, _⟩ :=
          exists_closedPair_of_pathwidth_le G k (mem_graphsOfPathwidthLe.1 hG) hk
        refine mem_biUnion.2 ⟨⟨A, R⟩, mem_closedIndices.2 ⟨hA, ?_, hR⟩, mem_closedPairGraphs.2 hcl⟩
        intro x hx
        rw [mem_sdiff]
        exact ⟨mem_univ x, fun hxA =>
          Finset.disjoint_left.1 hcl.disjoint_and_isEmptyPair.1 hxA hx⟩
    _ ≤ _ := sum_biUnion_le_sum_of_nonneg _ _ _ (gnpWeight_nonneg hp0 hp1)

end ClosedUnion

/-! ### Lemma Fl: the flips of an empty pair -/

section Flips

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The vertices of `A` with no neighbour in `A`: isolated in `G[A]`. -/
def isolatedIn (A : Finset V) : Finset V := A.filter (fun v => ∀ a ∈ A, ¬ G.Adj v a)

theorem isolatedIn_subset (A : Finset V) : isolatedIn G A ⊆ A := filter_subset _ _

theorem not_adj_of_mem_isolatedIn {A : Finset V} {v a : V} (hv : v ∈ isolatedIn G A)
    (ha : a ∈ A) : ¬ G.Adj v a :=
  (mem_filter.1 hv).2 a ha

/-- The flip of `(A, R)` along `J ⊆ I_A`, `J' ⊆ I_R`: `((A ∖ J) ∪ J', (R ∖ J') ∪ J)`. -/
def flipPair (A R J J' : Finset V) : Σ _ : Finset V, Finset V :=
  ⟨(A \ J) ∪ J', (R \ J') ∪ J⟩

/-- **Lemma Fl, emptiness**: the flipped pair is empty (four cases). -/
theorem flipPair_isEmptyPair {A R J J' : Finset V} (he : IsEmptyPair G A R)
    (hJ : J ⊆ isolatedIn G A) (hJ' : J' ⊆ isolatedIn G R) :
    IsEmptyPair G ((A \ J) ∪ J') ((R \ J') ∪ J) := by
  intro x hx y hy hadj
  rcases mem_union.1 hx with hx | hx <;> rcases mem_union.1 hy with hy | hy
  · exact he x (mem_sdiff.1 hx).1 y (mem_sdiff.1 hy).1 hadj
  · exact not_adj_of_mem_isolatedIn G (hJ hy) (mem_sdiff.1 hx).1 (G.adj_symm hadj)
  · exact not_adj_of_mem_isolatedIn G (hJ' hx) (mem_sdiff.1 hy).1 hadj
  · exact he y (isolatedIn_subset G A (hJ hy)) x (isolatedIn_subset G R (hJ' hx)) (G.adj_symm hadj)

/-- **Lemma Fl, disjointness**: the flipped sides are disjoint. -/
theorem flipPair_disjoint {A R J J' : Finset V} (hAR : Disjoint A R)
    (hJ : J ⊆ isolatedIn G A) (hJ' : J' ⊆ isolatedIn G R) :
    Disjoint ((A \ J) ∪ J') ((R \ J') ∪ J) := by
  have hJA : J ⊆ A := hJ.trans (isolatedIn_subset G A)
  have hJ'R : J' ⊆ R := hJ'.trans (isolatedIn_subset G R)
  rw [Finset.disjoint_left]
  intro x hx hy
  rcases mem_union.1 hx with hx | hx <;> rcases mem_union.1 hy with hy | hy
  · exact Finset.disjoint_left.1 hAR (mem_sdiff.1 hx).1 (mem_sdiff.1 hy).1
  · exact (mem_sdiff.1 hx).2 hy
  · exact (mem_sdiff.1 hy).2 hx
  · exact Finset.disjoint_left.1 hAR (hJA hy) (hJ'R hx)

/-- **Lemma Fl, sizes**: the flipped sides have the sizes of the original ones. -/
theorem card_flipPair {A R J J' : Finset V} (hAR : Disjoint A R)
    (hJ : J ⊆ isolatedIn G A) (hJ' : J' ⊆ isolatedIn G R) (hcard : J.card = J'.card) :
    ((A \ J) ∪ J').card = A.card ∧ ((R \ J') ∪ J).card = R.card := by
  have hJA : J ⊆ A := hJ.trans (isolatedIn_subset G A)
  have hJ'R : J' ⊆ R := hJ'.trans (isolatedIn_subset G R)
  have h1 : Disjoint (A \ J) J' :=
    Finset.disjoint_of_subset_left sdiff_subset (Finset.disjoint_of_subset_right hJ'R hAR)
  have h2 : Disjoint (R \ J') J :=
    Finset.disjoint_of_subset_left sdiff_subset (Finset.disjoint_of_subset_right hJA hAR.symm)
  rw [card_union_of_disjoint h1, card_union_of_disjoint h2, card_sdiff_of_subset hJA,
    card_sdiff_of_subset hJ'R]
  have := card_le_card hJA
  have := card_le_card hJ'R
  omega

/-- **Lemma Fl, injectivity**: `(J, J')` is recovered from the flipped pair as
`(R* ∩ A, A* ∩ R)`. -/
theorem flipPair_injOn {A R : Finset V} (hAR : Disjoint A R) :
    Set.InjOn (fun JJ : Finset V × Finset V => flipPair A R JJ.1 JJ.2)
      ((isolatedIn G A).powerset ×ˢ (isolatedIn G R).powerset : Finset (Finset V × Finset V)) := by
  have key : ∀ J J' : Finset V, J ⊆ isolatedIn G A → J' ⊆ isolatedIn G R →
      ((R \ J') ∪ J) ∩ A = J ∧ ((A \ J) ∪ J') ∩ R = J' := by
    intro J J' hJ hJ'
    have hJA : J ⊆ A := hJ.trans (isolatedIn_subset G A)
    have hJ'R : J' ⊆ R := hJ'.trans (isolatedIn_subset G R)
    constructor
    · rw [union_inter_distrib_right, inter_eq_left.2 hJA]
      have : (R \ J') ∩ A = ∅ := by
        rw [← Finset.disjoint_iff_inter_eq_empty]
        exact Finset.disjoint_of_subset_left sdiff_subset hAR.symm
      rw [this, empty_union]
    · rw [union_inter_distrib_right, inter_eq_left.2 hJ'R]
      have : (A \ J) ∩ R = ∅ := by
        rw [← Finset.disjoint_iff_inter_eq_empty]
        exact Finset.disjoint_of_subset_left sdiff_subset hAR
      rw [this, empty_union]
  rintro ⟨J₁, J₁'⟩ h₁ ⟨J₂, J₂'⟩ h₂ heq
  simp only [coe_product, Set.mem_prod, mem_coe, mem_powerset] at h₁ h₂
  simp only [flipPair, Sigma.mk.injEq, heq_eq_eq] at heq
  obtain ⟨hA₁, hR₁⟩ := key J₁ J₁' h₁.1 h₁.2
  obtain ⟨hA₂, hR₂⟩ := key J₂ J₂' h₂.1 h₂.2
  rw [Prod.mk.injEq]
  constructor
  · rw [← hA₁, ← hA₂, heq.2]
  · rw [← hR₁, ← hR₂, heq.1]

/-- The flips of `(A, R)`: the pairs reached by exchanging equally many isolated vertices. -/
def flips (A R : Finset V) : Finset (Σ _ : Finset V, Finset V) :=
  (((isolatedIn G A).powerset ×ˢ (isolatedIn G R).powerset).filter
    (fun JJ => JJ.1.card = JJ.2.card)).image (fun JJ => flipPair A R JJ.1 JJ.2)

/-- `(A, R)` is its own flip along `(∅, ∅)`. -/
theorem one_le_card_flips (A R : Finset V) : 1 ≤ (flips G A R).card := by
  refine card_pos.2 ⟨⟨A, R⟩, mem_image.2 ⟨(∅, ∅), ?_, ?_⟩⟩
  · simp
  · simp [flipPair]

open scoped Classical in
/-- **Lemma Fl, admissibility**: every flip of an empty pair of `pairIndices t r` is an
empty pair of `pairIndices t r`, and the flips are distinct, so their number is at most the
number of empty pairs. -/
theorem card_flips_le {t r : ℕ} {A R : Finset V} (hq : (⟨A, R⟩ : Σ _ : Finset V, Finset V) ∈ pairIndices t r)
    (he : IsEmptyPair G A R) :
    (flips G A R).card ≤
      ((pairIndices (V := V) t r).filter
        (fun q : Σ _ : Finset V, Finset V => IsEmptyPair G q.1 q.2)).card := by
  obtain ⟨hA, hRA, hR⟩ := mem_pairIndices.1 hq
  have hAR : Disjoint A R := by
    rw [Finset.disjoint_left]
    exact fun x hx hxR => (mem_sdiff.1 (hRA hxR)).2 hx
  unfold flips
  rw [card_image_of_injOn ((flipPair_injOn G hAR).mono (coe_subset.2 (filter_subset _ _)))]
  refine card_le_card_of_injOn (fun JJ : Finset V × Finset V => flipPair A R JJ.1 JJ.2) ?_
    ((flipPair_injOn G hAR).mono (coe_subset.2 (filter_subset _ _)))
  intro JJ hJJ
  have hJJ' := Finset.mem_coe.1 hJJ
  rw [mem_filter, mem_product, mem_powerset, mem_powerset] at hJJ'
  obtain ⟨⟨hJ, hJ'⟩, hcard⟩ := hJJ'
  obtain ⟨h1, h2⟩ := card_flipPair G hAR hJ hJ' hcard
  rw [mem_coe, mem_filter, mem_pairIndices]
  simp only [flipPair]
  refine ⟨⟨h1.trans hA, ?_, h2.trans hR⟩, flipPair_isEmptyPair G he hJ hJ'⟩
  intro x hx
  rw [mem_sdiff]
  exact ⟨mem_univ x, fun hxA => Finset.disjoint_left.1 (flipPair_disjoint G hAR hJ hJ') hxA hx⟩

end Flips

/-! ### L1′ d: `3K₂` is in `E_relax` and not in `E_bip` at `k = 0` -/

section ThreeK2

/-- Three disjoint edges on six vertices: `03`, `14`, `25`. -/
def threeK2 : SimpleGraph (Fin 6) :=
  SimpleGraph.fromEdgeSet {s(0, 3), s(1, 4), s(2, 5)}

instance : DecidableRel threeK2.Adj := by
  unfold threeK2; infer_instance

/-- The partner of a vertex of `3K₂`. -/
def threeK2Partner (i : Fin 6) : Fin 6 := if i.val < 3 then i + 3 else i - 3

theorem threeK2_adj_iff : ∀ u v : Fin 6, threeK2.Adj u v ↔ v = threeK2Partner u := by
  decide

theorem threeK2Partner_partner : ∀ x : Fin 6, threeK2Partner (threeK2Partner x) = x := by
  decide

instance (A R : Finset (Fin 6)) : Decidable (IsEmptyPair threeK2 A R) := by
  unfold IsEmptyPair; infer_instance

/-- No `3`-set of `3K₂` is an empty pair with its complement: a `3`-set must split one of
the three edges. Decided in the kernel over the `64` subsets. -/
theorem threeK2_no_balanced :
    ∀ A : Finset (Fin 6), A.card = 3 → ¬ IsEmptyPair threeK2 A (univ \ A) := by
  decide +kernel

/-- **L1′ d, the bipartition half**: with `k = 0` and `S = ∅`, `3K₂` has no empty pair with
sides of sizes `3` and `3` (no sub-family of the component sizes `2, 2, 2` sums to `3`). -/
theorem not_isBalancedBip_threeK2 : ¬ IsBalancedBip threeK2 ∅ 0 := by
  rintro ⟨A, R, hAR, hU, hA, _, hE⟩
  have hRu : R = univ \ A := by
    rw [sdiff_empty] at hU
    rw [← hU, union_sdiff_cancel_left hAR]
  exact threeK2_no_balanced A (by simpa using hA) (hRu ▸ hE)

/-- A walk of `3K₂` from `u` stays in `{u, partner u}`. -/
theorem threeK2_walk_support {u v : Fin 6} (p : threeK2.Walk u v) :
    v = u ∨ v = threeK2Partner u := by
  induction p with
  | nil => exact Or.inl rfl
  | @cons x y z hxy q ih =>
    rw [threeK2_adj_iff] at hxy
    rcases ih with rfl | rfl
    · exact Or.inr hxy
    · rw [hxy, threeK2Partner_partner]; exact Or.inl rfl

/-- **L1′ d, the relaxed half**: every component of `3K₂ − ∅` has at most `2 ≤ 3 = t`
vertices. -/
theorem card_componentOff_threeK2_le (v : Fin 6) :
    (componentOff threeK2 ∅ v).card ≤ (Fintype.card (Fin 6) - 0 + 1) / 2 := by
  have hsub : componentOff threeK2 ∅ v ⊆ {v, threeK2Partner v} := by
    intro w hw
    classical
    obtain ⟨p, _⟩ := (mem_filter.1 hw).2
    rcases threeK2_walk_support p with rfl | rfl
    · exact mem_insert_self _ _
    · exact mem_insert_of_mem (mem_singleton_self _)
  calc (componentOff threeK2 ∅ v).card ≤ ({v, threeK2Partner v} : Finset (Fin 6)).card :=
        card_le_card hsub
    _ ≤ 2 := card_le_two
    _ ≤ (Fintype.card (Fin 6) - 0 + 1) / 2 := by simp

end ThreeK2

/-! ### Corollary W-flip, the sound part -/

open scoped Classical in
/-- **Corollary W-flip, the sound part**: with `Z(G, (A, R)) = #flips G A R`, which Lemma Fl
makes admissible, `P(pathwidth ≤ k) ≤ E[Σ_{(A, R)} 1[(A, R) empty] / #flips G A R]` over the
exact-size pairs. The evaluation of the right-hand side on random covers by the joint
binomial moments (Lemma J) is on paper. -/
theorem weightedSum_graphsOfPathwidthLe_le_flipWeighted (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : ℕ) (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ G : SimpleGraph V, gnpWeight p G *
        ∑ q ∈ pairIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2),
          if IsEmptyPair G q.1 q.2 then (1 : ℝ) / (flips G q.1 q.2).card else 0 := by
  refine weightedSum_graphsOfPathwidthLe_le_weighted p hp0 hp1 k hk
    (fun G q => (flips G q.1 q.2).card) (fun G q hq hE => ⟨one_le_card_flips G q.1 q.2, ?_⟩)
  have := card_flips_le G (t := (Fintype.card V - k + 1) / 2) (r := (Fintype.card V - k) / 2)
    (A := q.1) (R := q.2) hq hE
  convert this using 3

/-! ### The independence step of Theorem Cl: a product over blocks of pairs

The closed-pair event is a conjunction of `1 + 2|S|` events on pairwise disjoint blocks of
pairs — no `A`–`R` edge; for each `v ∈ S`, some `A`–`v` edge and some `R`–`v` edge — and the
`G(n, p)` weight of a conjunction over disjoint blocks is the product of the per-block weights
(`sum_subsetWeight_split`, `sum_subsetWeight_blocks`: the fibre argument of
`sum_gnpWeight_fiber`, iterated). `sum_gnpWeight_closedPairGraphs` is the evaluation
`(1 − p)^(|A||R|) ((1 − (1 − p)^|A|)(1 − (1 − p)^|R|))^|S|`, and
`weightedSum_graphsOfPathwidthLe_le_closedPairCount` is **Theorem Cl** of
`reports/separator_moment.md` §8.1 in its pair-summed form,
`weightedSum_graphsOfPathwidthLe_le_closedPairFormula` in its size-summed form. Checked
before it was stated: every disjoint pair of every labelled graph on `n ≤ 5` and 80 random
pairs at `n = 6`, in exact rationals (`reports/scratch/separator_moment/13_reserve/check.log`). -/

section ProductOverBlocks

variable {α : Type*} [DecidableEq α]

/-- The `p`-weight of a subset `F` of a finite set `T` of pairs: `p^|F| (1 − p)^(|T| − |F|)`. -/
def subsetWeight (p : ℝ) (T F : Finset α) : ℝ := p ^ F.card * (1 - p) ^ (T.card - F.card)

theorem sum_subsetWeight_powerset (p : ℝ) (T : Finset α) :
    ∑ F ∈ T.powerset, subsetWeight p T F = 1 := by
  unfold subsetWeight
  rw [sum_pow_mul_eq_add_pow]
  simp

theorem subsetWeight_union {p : ℝ} {B T' F₁ F₂ : Finset α} (hd : Disjoint B T')
    (h₁ : F₁ ⊆ B) (h₂ : F₂ ⊆ T') :
    subsetWeight p (B ∪ T') (F₁ ∪ F₂) = subsetWeight p B F₁ * subsetWeight p T' F₂ := by
  unfold subsetWeight
  have hF : Disjoint F₁ F₂ := disjoint_of_subset_left h₁ (disjoint_of_subset_right h₂ hd)
  rw [card_union_of_disjoint hd, card_union_of_disjoint hF]
  have h1 := card_le_card h₁
  have h2 := card_le_card h₂
  have : B.card + T'.card - (F₁.card + F₂.card) =
      (B.card - F₁.card) + (T'.card - F₂.card) := by omega
  rw [this, pow_add, pow_add]
  ring

/-- **The split lemma.** For disjoint `B`, `T'` and predicates `P` on the subsets of `B`
and `Q` on the subsets of `T'`, the weight of `{F ⊆ B ∪ T' : P (F ∩ B) ∧ Q (F ∩ T')}` is the
product of the weights of `{F ⊆ B : P F}` and `{F ⊆ T' : Q F}`. -/
theorem sum_subsetWeight_split (p : ℝ) {B T' : Finset α} (hd : Disjoint B T')
    (P Q : Finset α → Prop) [DecidablePred P] [DecidablePred Q] :
    ∑ F ∈ (B ∪ T').powerset.filter (fun F => P (F ∩ B) ∧ Q (F ∩ T')),
        subsetWeight p (B ∪ T') F =
      (∑ F ∈ B.powerset.filter P, subsetWeight p B F) *
        (∑ F ∈ T'.powerset.filter Q, subsetWeight p T' F) := by
  rw [sum_mul_sum, ← sum_product']
  symm
  have key : ∀ F₁ F₂ : Finset α, F₁ ⊆ B → F₂ ⊆ T' →
      (F₁ ∪ F₂) ∩ B = F₁ ∧ (F₁ ∪ F₂) ∩ T' = F₂ := by
    intro F₁ F₂ h₁ h₂
    have e₂ : F₂ ∩ B = ∅ := disjoint_iff_inter_eq_empty.1 (disjoint_of_subset_left h₂ hd.symm)
    have e₁ : F₁ ∩ T' = ∅ := disjoint_iff_inter_eq_empty.1 (disjoint_of_subset_left h₁ hd)
    constructor
    · rw [union_inter_distrib_right, inter_eq_left.2 h₁, e₂, union_empty]
    · rw [union_inter_distrib_right, inter_eq_left.2 h₂, e₁, empty_union]
  refine sum_nbij' (fun q => q.1 ∪ q.2) (fun F => (F ∩ B, F ∩ T')) ?_ ?_ ?_ ?_ ?_
  · rintro ⟨F₁, F₂⟩ hq
    simp only [mem_product, mem_filter, mem_powerset] at hq
    obtain ⟨⟨h₁, hP⟩, ⟨h₂, hQ⟩⟩ := hq
    obtain ⟨e1, e2⟩ := key F₁ F₂ h₁ h₂
    simp only [mem_filter, mem_powerset]
    exact ⟨union_subset_union h₁ h₂, by rw [e1, e2]; exact ⟨hP, hQ⟩⟩
  · intro F hF
    simp only [mem_filter, mem_powerset] at hF
    simp only [mem_product, mem_filter, mem_powerset]
    exact ⟨⟨inter_subset_right, hF.2.1⟩, ⟨inter_subset_right, hF.2.2⟩⟩
  · rintro ⟨F₁, F₂⟩ hq
    simp only [mem_product, mem_filter, mem_powerset] at hq
    obtain ⟨e1, e2⟩ := key F₁ F₂ hq.1.1 hq.2.1
    simp only [e1, e2]
  · intro F hF
    simp only [mem_filter, mem_powerset] at hF
    simp only
    rw [← inter_union_distrib_left, inter_eq_left.2 hF.1]
  · rintro ⟨F₁, F₂⟩ hq
    simp only [mem_product, mem_filter, mem_powerset] at hq
    exact (subsetWeight_union hd hq.1.1 hq.2.1).symm

/-- **The product over blocks.** For pairwise disjoint blocks `B i ⊆ T`, `i ∈ s`, and
predicates `P i` on the subsets of `B i`, the weight of `{F ⊆ T : ∀ i ∈ s, P i (F ∩ B i)}` is
the product over `i ∈ s` of the weights of `{F ⊆ B i : P i F}`; the pairs of `T` in no block
are free and contribute the factor `(p + (1 − p))^… = 1`. -/
theorem sum_subsetWeight_blocks (p : ℝ) {ι : Type*} [DecidableEq ι] (s : Finset ι)
    (B : ι → Finset α) (P : ι → Finset α → Prop) [∀ i, DecidablePred (P i)] :
    ∀ T : Finset α, (∀ i ∈ s, B i ⊆ T) →
      (∀ i ∈ s, ∀ j ∈ s, i ≠ j → Disjoint (B i) (B j)) →
      ∑ F ∈ T.powerset.filter (fun F => ∀ i ∈ s, P i (F ∩ B i)), subsetWeight p T F =
        ∏ i ∈ s, ∑ F ∈ (B i).powerset.filter (P i), subsetWeight p (B i) F := by
  induction s using Finset.induction_on with
  | empty =>
    intro T _ _
    simp [sum_subsetWeight_powerset]
  | insert i s hi ih =>
    intro T hBT hdisj
    have hiT : B i ⊆ T := hBT i (mem_insert_self i s)
    have hT : B i ∪ (T \ B i) = T := union_sdiff_of_subset hiT
    have hd : Disjoint (B i) (T \ B i) := disjoint_sdiff
    have hsub : ∀ j ∈ s, B j ⊆ T \ B i := by
      intro j hj
      have hij : i ≠ j := fun h => hi (h ▸ hj)
      exact subset_sdiff.2 ⟨hBT j (mem_insert_of_mem hj),
        (hdisj i (mem_insert_self i s) j (mem_insert_of_mem hj) hij).symm⟩
    rw [prod_insert hi, ← ih (T \ B i) hsub
      (fun j hj j' hj' hne => hdisj j (mem_insert_of_mem hj) j' (mem_insert_of_mem hj') hne)]
    have hsplit := sum_subsetWeight_split p hd (P i) (fun F => ∀ j ∈ s, P j (F ∩ B j))
    rw [hT] at hsplit
    rw [← hsplit]
    refine sum_congr (filter_congr ?_) (fun _ _ => rfl)
    intro F _
    simp only [mem_insert, forall_eq_or_imp]
    refine and_congr_right (fun _ => forall₂_congr (fun j hj => ?_))
    rw [inter_assoc, inter_eq_right.2 (hsub j hj)]

/-- The block weight of "no pair chosen": `(1 − p)^|B|`. -/
theorem sum_subsetWeight_eq_empty (p : ℝ) (B : Finset α) :
    ∑ F ∈ B.powerset.filter (fun F => F = ∅), subsetWeight p B F = (1 - p) ^ B.card := by
  have : B.powerset.filter (fun F => F = ∅) = {∅} := by
    ext F
    simp only [mem_filter, mem_powerset, mem_singleton]
    exact ⟨fun h => h.2, fun h => ⟨h ▸ empty_subset _, h⟩⟩
  rw [this, sum_singleton]
  simp [subsetWeight]

/-- The block weight of "some pair chosen": `1 − (1 − p)^|B|`. -/
theorem sum_subsetWeight_nonempty (p : ℝ) (B : Finset α) :
    ∑ F ∈ B.powerset.filter (fun F => F.Nonempty), subsetWeight p B F =
      1 - (1 - p) ^ B.card := by
  have h := sum_filter_add_sum_filter_not B.powerset (fun F => F.Nonempty) (subsetWeight p B)
  rw [sum_subsetWeight_powerset] at h
  have : B.powerset.filter (fun F => ¬ F.Nonempty) = B.powerset.filter (fun F => F = ∅) :=
    filter_congr (fun F _ => not_nonempty_iff_eq_empty)
  rw [this, sum_subsetWeight_eq_empty] at h
  linarith

end ProductOverBlocks

section ClosedProduct

/-- The pairs `s(a, v)`, `a ∈ A`: the `A`–`v` edges a separator vertex `v` may carry. -/
def starPairs (A : Finset V) (v : V) : Finset (Sym2 V) := A.image (fun a => s(a, v))

theorem mem_starPairs {A : Finset V} {v : V} {e : Sym2 V} :
    e ∈ starPairs A v ↔ ∃ a ∈ A, e = s(a, v) := by
  simp only [starPairs, mem_image, eq_comm]

theorem card_starPairs (A : Finset V) (v : V) : (starPairs A v).card = A.card := by
  rw [starPairs, card_image_of_injOn]
  intro a _ a' _ h
  exact Sym2.congr_left.1 h

theorem starPairs_subset_top {A : Finset V} {v : V} (hv : v ∉ A) :
    starPairs A v ⊆ edges (⊤ : SimpleGraph V) := by
  intro e he
  obtain ⟨a, ha, rfl⟩ := mem_starPairs.1 he
  rw [mem_edges_top, Sym2.mk_isDiag_iff]
  exact fun h => hv (h ▸ ha)

theorem disjoint_starPairs_forbidden (X : Finset V) {A R : Finset V} {v : V}
    (hvA : v ∉ A) (hvR : v ∉ R) : Disjoint (starPairs X v) (forbidden A R) := by
  rw [Finset.disjoint_left]
  intro e he hf
  obtain ⟨x, hx, rfl⟩ := mem_starPairs.1 he
  obtain ⟨a', ha', r', hr', h⟩ := mem_forbidden.1 hf
  rw [Sym2.eq_iff] at h
  rcases h with ⟨_, rfl⟩ | ⟨rfl, rfl⟩
  · exact hvR hr'
  · exact hvA ha'

theorem disjoint_starPairs_starPairs {A R : Finset V} {v : V} (hAR : Disjoint A R)
    (hvA : v ∉ A) : Disjoint (starPairs A v) (starPairs R v) := by
  rw [Finset.disjoint_left]
  intro e he he'
  obtain ⟨a, ha, rfl⟩ := mem_starPairs.1 he
  obtain ⟨r, hr, h⟩ := mem_starPairs.1 he'
  rw [Sym2.eq_iff] at h
  rcases h with ⟨rfl, _⟩ | ⟨rfl, rfl⟩
  · exact Finset.disjoint_left.1 hAR ha hr
  · exact hvA ha

theorem disjoint_starPairs_of_ne {A A' : Finset V} {v w : V} (hwA : w ∉ A)
    (hvw : v ≠ w) : Disjoint (starPairs A v) (starPairs A' w) := by
  rw [Finset.disjoint_left]
  intro e he he'
  obtain ⟨a, ha, rfl⟩ := mem_starPairs.1 he
  obtain ⟨a', ha', h⟩ := mem_starPairs.1 he'
  rw [Sym2.eq_iff] at h
  rcases h with ⟨_, h⟩ | ⟨rfl, rfl⟩
  · exact hvw h
  · exact hwA ha

/-- The two star blocks of a separator vertex `v`. -/
def starBlock (A R : Finset V) (v : V) : Finset (Sym2 V) := starPairs A v ∪ starPairs R v

/-- The closed-pair predicate on an edge set: no forbidden pair, and for every vertex off
`A ∪ R` some `A`-pair and some `R`-pair. -/
def ClosedEdgeSet (A R : Finset V) (F : Finset (Sym2 V)) : Prop :=
  F ∩ forbidden A R = ∅ ∧
    ∀ v ∈ univ \ (A ∪ R), (F ∩ starPairs A v).Nonempty ∧ (F ∩ starPairs R v).Nonempty

theorem isEmptyPair_iff_inter_forbidden (A R : Finset V) :
    IsEmptyPair G A R ↔ edges G ∩ forbidden A R = ∅ := by
  constructor
  · intro h
    rw [eq_empty_iff_forall_notMem]
    intro e he
    rw [mem_inter] at he
    obtain ⟨a, ha, r, hr, rfl⟩ := mem_forbidden.1 he.2
    exact h a ha r hr ((SimpleGraph.mem_edgeSet G).1 (mem_edges.1 he.1))
  · intro h a ha r hr hadj
    have : s(a, r) ∈ edges G ∩ forbidden A R :=
      mem_inter.2 ⟨mem_edges.2 ((SimpleGraph.mem_edgeSet G).2 hadj),
        mem_forbidden.2 ⟨a, ha, r, hr, rfl⟩⟩
    rw [h] at this
    exact notMem_empty _ this

theorem exists_adj_iff_inter_starPairs_nonempty (A : Finset V) (v : V) :
    (∃ a ∈ A, G.Adj a v) ↔ (edges G ∩ starPairs A v).Nonempty := by
  constructor
  · rintro ⟨a, ha, hadj⟩
    exact ⟨s(a, v), mem_inter.2 ⟨mem_edges.2 ((SimpleGraph.mem_edgeSet G).2 hadj),
      mem_starPairs.2 ⟨a, ha, rfl⟩⟩⟩
  · rintro ⟨e, he⟩
    rw [mem_inter] at he
    obtain ⟨a, ha, rfl⟩ := mem_starPairs.1 he.2
    exact ⟨a, ha, (SimpleGraph.mem_edgeSet G).1 (mem_edges.1 he.1)⟩

/-- A pair is closed iff its sides are disjoint and the edge set satisfies `ClosedEdgeSet`. -/
theorem isClosedPair_iff_closedEdgeSet (A R : Finset V) :
    IsClosedPair G A R ↔ Disjoint A R ∧ ClosedEdgeSet A R (edges G) := by
  rw [isClosedPair_iff_sees_both, ClosedEdgeSet, isEmptyPair_iff_inter_forbidden]
  refine and_congr_right (fun _ => and_congr_right (fun _ => ?_))
  constructor
  · intro h v hv
    rw [mem_sdiff, mem_union, not_or] at hv
    obtain ⟨hA, hR⟩ := h v hv.2.1 hv.2.2
    exact ⟨(exists_adj_iff_inter_starPairs_nonempty G A v).1 hA,
      (exists_adj_iff_inter_starPairs_nonempty G R v).1 hR⟩
  · intro h v hvA hvR
    obtain ⟨hA, hR⟩ := h v (by rw [mem_sdiff, mem_union, not_or]; exact ⟨mem_univ v, hvA, hvR⟩)
    exact ⟨(exists_adj_iff_inter_starPairs_nonempty G A v).2 hA,
      (exists_adj_iff_inter_starPairs_nonempty G R v).2 hR⟩

open scoped Classical in
/-- `edges` maps the graphs in which `(A, R)` is closed onto the closed edge sets. -/
theorem image_edges_closedPairGraphs {A R : Finset V} (hAR : Disjoint A R) :
    (closedPairGraphs A R).image edges =
      (edges (⊤ : SimpleGraph V)).powerset.filter (ClosedEdgeSet A R) := by
  ext F
  rw [mem_image, mem_filter, mem_powerset]
  constructor
  · rintro ⟨G, hG, rfl⟩
    exact ⟨edges_subset_top G, ((isClosedPair_iff_closedEdgeSet G A R).1
      (mem_closedPairGraphs.1 hG)).2⟩
  · rintro ⟨hF, hcl⟩
    refine ⟨SimpleGraph.fromEdgeSet (F : Set (Sym2 V)), ?_, edges_fromEdgeSet F hF⟩
    rw [mem_closedPairGraphs, isClosedPair_iff_closedEdgeSet, edges_fromEdgeSet F hF]
    exact ⟨hAR, hcl⟩

/-- The weight of one star block: a separator vertex sees both sides with probability
`(1 − (1 − p)^|A|)(1 − (1 − p)^|R|)`. -/
theorem sum_subsetWeight_starBlock {A R : Finset V} (hAR : Disjoint A R) {v : V} (hvA : v ∉ A)
    (p : ℝ) :
    ∑ F ∈ (starBlock A R v).powerset.filter
        (fun F => (F ∩ starPairs A v).Nonempty ∧ (F ∩ starPairs R v).Nonempty),
        subsetWeight p (starBlock A R v) F =
      (1 - (1 - p) ^ A.card) * (1 - (1 - p) ^ R.card) := by
  unfold starBlock
  rw [sum_subsetWeight_split p (disjoint_starPairs_starPairs hAR hvA)
    (fun F => F.Nonempty) (fun F => F.Nonempty), sum_subsetWeight_nonempty,
    sum_subsetWeight_nonempty, card_starPairs, card_starPairs]

open scoped Classical in
/-- **The independence step of Theorem Cl.** The `G(n, p)` probability that `(A, R)` is a
closed pair is `(1 − p)^(|A||R|) ((1 − (1 − p)^|A|)(1 − (1 − p)^|R|))^|S|`, `S = V ∖ (A ∪ R)`:
the forbidden pairs, and the two star blocks of each `v ∈ S`, are pairwise disjoint blocks. -/
theorem sum_gnpWeight_closedPairGraphs {A R : Finset V} (hAR : Disjoint A R) (p : ℝ) :
    ∑ G ∈ closedPairGraphs A R, gnpWeight p G =
      (1 - p) ^ (A.card * R.card) *
        ((1 - (1 - p) ^ A.card) * (1 - (1 - p) ^ R.card)) ^ (univ \ (A ∪ R)).card := by
  set S := univ \ (A ∪ R) with hS
  have hSA : ∀ v ∈ S, v ∉ A := fun v hv => by
    rw [hS, mem_sdiff, mem_union, not_or] at hv; exact hv.2.1
  have hSR : ∀ v ∈ S, v ∉ R := fun v hv => by
    rw [hS, mem_sdiff, mem_union, not_or] at hv; exact hv.2.2
  have hforb := forbidden_subset_top (V := V) hAR
  set T' := edges (⊤ : SimpleGraph V) \ forbidden A R with hT'
  have hT : forbidden A R ∪ T' = edges (⊤ : SimpleGraph V) := union_sdiff_of_subset hforb
  have hd : Disjoint (forbidden A R) T' := disjoint_sdiff
  have hblock : ∀ v ∈ S, starBlock A R v ⊆ T' := by
    intro v hv
    rw [hT']
    refine subset_sdiff.2 ⟨union_subset (starPairs_subset_top (hSA v hv))
      (starPairs_subset_top (hSR v hv)), ?_⟩
    exact Finset.disjoint_union_left.2 ⟨disjoint_starPairs_forbidden A (hSA v hv) (hSR v hv),
      disjoint_starPairs_forbidden R (hSA v hv) (hSR v hv)⟩
  have hbd : ∀ v ∈ S, ∀ w ∈ S, v ≠ w → Disjoint (starBlock A R v) (starBlock A R w) := by
    intro v hv w hw hvw
    unfold starBlock
    rw [Finset.disjoint_union_left, Finset.disjoint_union_right, Finset.disjoint_union_right]
    exact ⟨⟨disjoint_starPairs_of_ne (hSA w hw) hvw,
      disjoint_starPairs_of_ne (hSA w hw) hvw⟩,
      ⟨disjoint_starPairs_of_ne (hSR w hw) hvw,
      disjoint_starPairs_of_ne (hSR w hw) hvw⟩⟩
  calc ∑ G ∈ closedPairGraphs A R, gnpWeight p G
      = ∑ F ∈ (closedPairGraphs A R).image edges,
          subsetWeight p (edges (⊤ : SimpleGraph V)) F := by
        rw [sum_image edges_injective.injOn]
        refine sum_congr rfl (fun G _ => ?_)
        unfold gnpWeight subsetWeight
        rw [card_edges_top]
    _ = ∑ F ∈ (forbidden A R ∪ T').powerset.filter
          (fun F => (F ∩ forbidden A R = ∅) ∧
            ∀ v ∈ S, ((F ∩ T') ∩ starPairs A v).Nonempty ∧ ((F ∩ T') ∩ starPairs R v).Nonempty),
          subsetWeight p (forbidden A R ∪ T') F := by
        rw [image_edges_closedPairGraphs hAR, hT]
        refine sum_congr ?_ (fun _ _ => rfl)
        ext F
        simp only [mem_filter, mem_powerset, ClosedEdgeSet]
        refine and_congr_right (fun _ => and_congr_right (fun _ => forall₂_congr (fun v hv => ?_)))
        have h1 : starPairs A v ⊆ T' := (subset_union_left).trans (hblock v hv)
        have h2 : starPairs R v ⊆ T' := (subset_union_right).trans (hblock v hv)
        rw [inter_assoc, inter_eq_right.2 h1, inter_assoc, inter_eq_right.2 h2]
    _ = (∑ F ∈ (forbidden A R).powerset.filter (fun F => F = ∅),
            subsetWeight p (forbidden A R) F) *
          ∑ F ∈ T'.powerset.filter
            (fun F => ∀ v ∈ S, (F ∩ starPairs A v).Nonempty ∧ (F ∩ starPairs R v).Nonempty),
            subsetWeight p T' F :=
        sum_subsetWeight_split p hd (fun F => F = ∅)
          (fun F => ∀ v ∈ S, (F ∩ starPairs A v).Nonempty ∧ (F ∩ starPairs R v).Nonempty)
    _ = (1 - p) ^ (A.card * R.card) *
          ∏ v ∈ S, ∑ F ∈ (starBlock A R v).powerset.filter
            (fun F => (F ∩ starPairs A v).Nonempty ∧ (F ∩ starPairs R v).Nonempty),
            subsetWeight p (starBlock A R v) F := by
        rw [sum_subsetWeight_eq_empty, card_forbidden hAR]
        congr 1
        have hb := sum_subsetWeight_blocks p S (starBlock A R)
          (fun v F => (F ∩ starPairs A v).Nonempty ∧ (F ∩ starPairs R v).Nonempty) T' hblock hbd
        refine Eq.trans ?_ hb
        refine sum_congr ?_ (fun _ _ => rfl)
        ext F
        simp only [mem_filter, mem_powerset]
        refine and_congr_right (fun _ => forall₂_congr (fun v hv => ?_))
        have h1 : starPairs A v ⊆ starBlock A R v := subset_union_left
        have h2 : starPairs R v ⊆ starBlock A R v := subset_union_right
        rw [inter_assoc, inter_eq_right.2 h1, inter_assoc, inter_eq_right.2 h2]
    _ = _ := by
        rw [prod_congr rfl (fun v hv => sum_subsetWeight_starBlock hAR (hSA v hv) p), prod_const]

open scoped Classical in
/-- **Theorem Cl** (`reports/separator_moment.md` §8.1), pair-summed form: for `0 ≤ p ≤ 1` and
`k < n`, `P(pathwidth ≤ k)` is at most the expected number of closed pairs with `|A| ≥ t`,
`|R| ≥ r`, each term evaluated exactly. -/
theorem weightedSum_graphsOfPathwidthLe_le_closedPairCount (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (k : ℕ) (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ q ∈ closedIndices (V := V) ((Fintype.card V - k + 1) / 2) ((Fintype.card V - k) / 2),
        (1 - p) ^ (q.1.card * q.2.card) *
          ((1 - (1 - p) ^ q.1.card) * (1 - (1 - p) ^ q.2.card)) ^ (univ \ (q.1 ∪ q.2)).card := by
  refine (weightedSum_graphsOfPathwidthLe_le_sum_closedPairs p hp0 hp1 k hk).trans
    (le_of_eq (sum_congr rfl (fun q hq => ?_)))
  have hAR : Disjoint q.1 q.2 := by
    rw [Finset.disjoint_left]
    intro a ha ha'
    exact (mem_sdiff.1 ((mem_closedIndices.1 hq).2.1 ha')).2 ha
  exact sum_gnpWeight_closedPairGraphs hAR p

open scoped Classical in
/-- The closed indices split by sizes: the disjoint union over `(a, r')` with `t ≤ a`, `r ≤ r'`
of the exact-size index sets `pairIndices a r'`. -/
theorem closedIndices_eq_biUnion (t r : ℕ) :
    closedIndices (V := V) t r =
      ((range (Fintype.card V + 1) ×ˢ range (Fintype.card V + 1)).filter
        (fun x => t ≤ x.1 ∧ r ≤ x.2)).biUnion (fun x => pairIndices x.1 x.2) := by
  ext q
  simp only [mem_closedIndices, mem_biUnion, mem_filter, mem_product, mem_range, mem_pairIndices]
  constructor
  · rintro ⟨hA, hR, hr⟩
    exact ⟨(q.1.card, q.2.card), ⟨⟨Nat.lt_succ_of_le (card_le_univ _),
      Nat.lt_succ_of_le (card_le_univ _)⟩, hA, hr⟩, rfl, hR, rfl⟩
  · rintro ⟨x, ⟨_, hA, hr⟩, h1, hR, h2⟩
    exact ⟨h1 ▸ hA, hR, h2 ▸ hr⟩

open scoped Classical in
/-- A sum over the closed indices of a function of the two sizes, regrouped by sizes: the
pairs with `|A| = a`, `|R| = r'` number `n.choose a · (n − a).choose r' = n! / (a! r'! (n − a − r')!)`. -/
theorem sum_closedIndices_eq (t r : ℕ) (f : ℕ → ℕ → ℝ) :
    ∑ q ∈ closedIndices (V := V) t r, f q.1.card q.2.card =
      ∑ x ∈ (range (Fintype.card V + 1) ×ˢ range (Fintype.card V + 1)).filter
          (fun x => t ≤ x.1 ∧ r ≤ x.2),
        ((Fintype.card V).choose x.1 * (Fintype.card V - x.1).choose x.2 : ℝ) * f x.1 x.2 := by
  rw [closedIndices_eq_biUnion, sum_biUnion]
  · refine sum_congr rfl (fun x _ => ?_)
    rw [sum_congr rfl (g := fun _ => f x.1 x.2) (fun q hq => by
      rw [(mem_pairIndices.1 hq).1, (mem_pairIndices.1 hq).2.2]), sum_const, card_pairIndices,
      nsmul_eq_mul]
    push_cast
    ring
  · intro x _ y _ hxy
    rw [Function.onFun, Finset.disjoint_left]
    intro q hq hq'
    apply hxy
    rw [mem_pairIndices] at hq hq'
    exact Prod.ext (hq.1.symm.trans hq'.1) (hq.2.2.symm.trans hq'.2.2)

open scoped Classical in
/-- **Theorem Cl** (`reports/separator_moment.md` §8.1), size-summed form: for `0 ≤ p ≤ 1` and
`k < n`, with `t = ⌈(n − k)/2⌉`, `r = ⌊(n − k)/2⌋`,
`P(pathwidth ≤ k) ≤ Σ_{a ≥ t, r' ≥ r, a + r' ≤ n} n.choose a · (n − a).choose r' ·
  (1 − p)^(a r') ((1 − (1 − p)^a)(1 − (1 − p)^r'))^(n − a − r')`,
the sum over the size pairs `(a, r')` (the binomial product is `n!/(a! r'! s!)`, `s = n − a − r'`;
the terms with `a + r' > n` have an empty index set and are zero through `(n − a).choose r' = 0`
when `r' > n − a`). The right-hand side is exactly the expected number of closed pairs with
`|A| ≥ t`, `|R| ≥ r`. -/
theorem weightedSum_graphsOfPathwidthLe_le_closedPairFormula (p : ℝ) (hp0 : 0 ≤ p)
    (hp1 : p ≤ 1) (k : ℕ) (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      ∑ x ∈ (range (Fintype.card V + 1) ×ˢ range (Fintype.card V + 1)).filter
          (fun x => (Fintype.card V - k + 1) / 2 ≤ x.1 ∧ (Fintype.card V - k) / 2 ≤ x.2),
        ((Fintype.card V).choose x.1 * (Fintype.card V - x.1).choose x.2 : ℝ) *
          ((1 - p) ^ (x.1 * x.2) *
            ((1 - (1 - p) ^ x.1) * (1 - (1 - p) ^ x.2)) ^ (Fintype.card V - x.1 - x.2)) := by
  refine (weightedSum_graphsOfPathwidthLe_le_closedPairCount p hp0 hp1 k hk).trans (le_of_eq ?_)
  rw [← sum_closedIndices_eq _ _ (fun a r' => (1 - p) ^ (a * r') *
    ((1 - (1 - p) ^ a) * (1 - (1 - p) ^ r')) ^ (Fintype.card V - a - r'))]
  refine sum_congr rfl (fun q hq => ?_)
  have hAR : Disjoint q.1 q.2 := by
    rw [Finset.disjoint_left]
    intro a ha ha'
    exact (mem_sdiff.1 ((mem_closedIndices.1 hq).2.1 ha')).2 ha
  rw [card_univ_sdiff, card_union_of_disjoint hAR, Nat.sub_sub]

end ClosedProduct

end MOSPFormalization
