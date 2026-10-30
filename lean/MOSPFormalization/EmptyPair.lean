/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The empty-pair lemma: the deterministic core of the first-moment pathwidth bound

`reports/random_graph_pathwidth_survey.md` §1.4 derives a lower bound on the
pathwidth of `G(n, c/n)` by a first moment over *empty pairs*: two disjoint
vertex sets with no edge between them. The deterministic half of that argument
is proved here, in the sharp form checked by brute force on every graph on at
most 9 vertices (`reports/scratch/empty_pair/check.py`, 2026-10-30, zero
violations, tight on 22.5% at 9 vertices).

The argument is one line in the repository's convention for vertex separation
(`VertexSeparation.lean`: at position `i` the *active suffix* is the set of
suffix vertices with a neighbour in the prefix). At any position `i` of a layout
`σ`, the prefix `P` and the *inactive* suffix `R` — the suffix vertices with no
prefix neighbour — are an empty pair, `|P| = i + 1`, and `|R| ≥ n − i − 1 − k`
where `k` is the layout's vertex separation. Since `R` avoids the closed
neighbourhood `N[P]`, this says `|N[P]| ≤ |P| + k`.

## Main results

* `exists_prefix_closedNbhd_card_le` — for every `j ≤ n` there is a `j`-set `A`
  with `|N[A]| ≤ j + pathwidth G`. This is Harper's vertex-isoperimetric lower
  bound on pathwidth in its layout form (CLAUDE.md, *the expansion bound*;
  Chandran & Kavitha 2006 on hypercubes): `pathwidth G ≥ min_{|A| = j} |N[A]| − j`
  for every `j`.
* `emptyPairIndex G` — `s*(G) = max_A min(|A| − 1, n − |N[A]|)`, the largest `s`
  such that some set of at least `s + 1` vertices has at least `s` vertices
  outside its closed neighbourhood.
* `card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth` — **the sharp
  empty-pair bound**: `n − 2·s*(G) − 2 ≤ pathwidth G`. Taking
  `j = ⌈(n − k)/2⌉` in the first result gives a `j`-set with at least
  `⌊(n − k)/2⌋ ≥ j − 1` vertices outside its closed neighbourhood, so
  `s* ≥ j − 1`, i.e. `n − 2s* − 2 ≤ n − 2j ≤ k`.
* `exists_empty_pair` — the survey's own phrasing: disjoint `A`, `R` with no
  `A`–`R` edge, `|A| = ⌈(n − k)/2⌉` and `|R| ≥ ⌈(n − k)/2⌉ − 1`.

The probabilistic half (the expected number of empty pairs of these sizes in
`G(n, c/n)` vanishes below `β*(c)·n`) is not formalised: Mathlib has no `G(n, p)`.
-/

import MOSPFormalization.Sandwich

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Suffix cardinality (`card_prefixSet` is in `LinearLayout.lean`) -/

theorem card_suffixSet (σ : LinearLayout V) (i : ℕ) (hi : i < Fintype.card V) :
    (suffixSet σ i).card = Fintype.card V - (i + 1) := by
  have := card_prefixSet_add_card_suffixSet σ i rfl
  rw [card_prefixSet σ hi] at this
  omega

/-! ### The inactive suffix -/

/-- The suffix vertices at position `i` with no neighbour in the prefix. -/
def inactiveSuffix (σ : LinearLayout V) (i : ℕ) : Finset V :=
  suffixSet σ i \ activeSuffix G σ i

theorem card_inactiveSuffix (σ : LinearLayout V) (i : ℕ) :
    (inactiveSuffix G σ i).card = (suffixSet σ i).card - vertexSepAt G σ i := by
  unfold inactiveSuffix vertexSepAt
  exact Finset.card_sdiff_of_subset (activeSuffix_subset_suffixSet G σ i)

/-- No edge joins the prefix to the inactive suffix. -/
theorem not_adj_prefix_inactiveSuffix (σ : LinearLayout V) (i : ℕ) {u v : V}
    (hu : u ∈ prefixSet σ i) (hv : v ∈ inactiveSuffix G σ i) : ¬ G.Adj u v := by
  intro huv
  unfold inactiveSuffix at hv
  rw [Finset.mem_sdiff] at hv
  apply hv.2
  rw [mem_activeSuffix_iff]
  exact ⟨(mem_suffixSet_iff σ v i).mp hv.1, u, hu, huv⟩

theorem disjoint_prefix_inactiveSuffix (σ : LinearLayout V) (i : ℕ) :
    Disjoint (prefixSet σ i) (inactiveSuffix G σ i) :=
  Finset.disjoint_of_subset_right Finset.sdiff_subset (disjoint_prefix_suffix σ i)

/-! ### Closed neighbourhoods -/

/-- The closed neighbourhood of a vertex set: the set and all neighbours of its members. -/
def closedNbhd (A : Finset V) : Finset V :=
  A ∪ A.biUnion (fun a => G.neighborFinset a)

theorem mem_closedNbhd_iff (A : Finset V) (v : V) :
    v ∈ closedNbhd G A ↔ v ∈ A ∨ ∃ a ∈ A, G.Adj a v := by
  simp [closedNbhd, SimpleGraph.mem_neighborFinset]

theorem subset_closedNbhd (A : Finset V) : A ⊆ closedNbhd G A :=
  Finset.subset_union_left

/-- A set disjoint from `A` with no edge to `A` lies outside `N[A]`. -/
theorem disjoint_closedNbhd_of_no_edge (A R : Finset V) (hAR : Disjoint A R)
    (h : ∀ u ∈ A, ∀ v ∈ R, ¬ G.Adj u v) : Disjoint (closedNbhd G A) R := by
  rw [Finset.disjoint_left]
  intro v hv hvR
  rw [mem_closedNbhd_iff] at hv
  rcases hv with hvA | ⟨a, ha, hav⟩
  · exact Finset.disjoint_left.mp hAR hvA hvR
  · exact h a ha v hvR hav

/-- `|N[A]| + |R| ≤ n` for an empty pair `A`, `R`. -/
theorem card_closedNbhd_add_card_le (A R : Finset V) (hAR : Disjoint A R)
    (h : ∀ u ∈ A, ∀ v ∈ R, ¬ G.Adj u v) :
    (closedNbhd G A).card + R.card ≤ Fintype.card V := by
  rw [← Finset.card_union_of_disjoint (disjoint_closedNbhd_of_no_edge G A R hAR h)]
  exact Finset.card_le_univ _

/-! ### The layout form: Harper's vertex-isoperimetric bound -/

/-- At any position of any layout, the prefix and the inactive suffix are an empty
pair whose sizes add up to at least `n − k`. -/
theorem exists_empty_pair_of_layout (σ : LinearLayout V) (i : ℕ) (hi : i < Fintype.card V) :
    ∃ A R : Finset V, Disjoint A R ∧ A.card = i + 1 ∧
      Fintype.card V ≤ A.card + R.card + vertexSepOfLayout G σ ∧
      ∀ u ∈ A, ∀ v ∈ R, ¬ G.Adj u v := by
  refine ⟨prefixSet σ i, inactiveSuffix G σ i, disjoint_prefix_inactiveSuffix G σ i,
    card_prefixSet σ hi, ?_, fun u hu v hv => not_adj_prefix_inactiveSuffix G σ i hu hv⟩
  have h1 := card_inactiveSuffix G σ i
  have h2 := card_suffixSet σ i hi
  have h3 := vertexSepAt_le_vertexSepOfLayout G σ ⟨i, hi⟩
  have h4 := card_prefixSet σ hi
  simp only at h3
  omega

/-- **Harper's bound, layout form**: for every `j ≤ n` some `j`-set `A` has
`|N[A]| ≤ j + vs(σ)` under any layout `σ`. -/
theorem exists_closedNbhd_card_le_of_layout (σ : LinearLayout V) (j : ℕ)
    (hj : j ≤ Fintype.card V) :
    ∃ A : Finset V, A.card = j ∧ (closedNbhd G A).card ≤ j + vertexSepOfLayout G σ := by
  rcases Nat.eq_zero_or_pos j with rfl | hpos
  · exact ⟨∅, Finset.card_empty, by simp [closedNbhd]⟩
  · obtain ⟨A, R, hAR, hA, hsum, hedge⟩ :=
      exists_empty_pair_of_layout G σ (j - 1) (by omega)
    refine ⟨A, by omega, ?_⟩
    have := card_closedNbhd_add_card_le G A R hAR hedge
    omega

/-- **Harper's bound, graph form**: for every `j ≤ n` some `j`-set `A` has
`|N[A]| ≤ j + pathwidth G`. Equivalently `pathwidth G ≥ min_{|A| = j} |N[A]| − j`
for every `j`, the expansion bound of `satisfiability/expansion_bound.py`. -/
theorem exists_closedNbhd_card_le (j : ℕ) (hj : j ≤ Fintype.card V) :
    ∃ A : Finset V, A.card = j ∧ (closedNbhd G A).card ≤ j + pathwidth G := by
  -- the infimum defining vertex separation is attained
  have hne : (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ)).Nonempty :=
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  obtain ⟨σ, hσ⟩ := Nat.sInf_mem hne
  obtain ⟨A, hA, hN⟩ := exists_closedNbhd_card_le_of_layout G σ j hj
  refine ⟨A, hA, ?_⟩
  have : vertexSepOfLayout G σ = pathwidth G := by
    rw [← vertexSeparation_eq_pathwidth]; exact hσ
  omega

/-! ### The empty-pair index and the sharp bound -/

/-- `s*(G) = max_A min(|A| − 1, n − |N[A]|)`: the largest `s` such that some set of
at least `s + 1` vertices has at least `s` vertices outside its closed neighbourhood. -/
def emptyPairIndex : ℕ :=
  (Finset.univ : Finset (Finset V)).sup
    (fun A => min (A.card - 1) (Fintype.card V - (closedNbhd G A).card))

theorem le_emptyPairIndex (A : Finset V) :
    min (A.card - 1) (Fintype.card V - (closedNbhd G A).card) ≤ emptyPairIndex G :=
  Finset.le_sup (f := fun A => min (A.card - 1) (Fintype.card V - (closedNbhd G A).card))
    (Finset.mem_univ A)

/-- **The sharp empty-pair bound**: `n − 2·s*(G) − 2 ≤ pathwidth G`. -/
theorem card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth :
    Fintype.card V - 2 * emptyPairIndex G - 2 ≤ pathwidth G := by
  set n := Fintype.card V with hn
  set k := pathwidth G with hk
  by_cases hnk : n ≤ k
  · omega
  · -- j = ⌈(n − k)/2⌉ = (n − k + 1) / 2
    obtain ⟨A, hA, hN⟩ := exists_closedNbhd_card_le G ((n - k + 1) / 2) (by omega)
    have := le_emptyPairIndex G A
    omega

/-- The survey's phrasing: an empty pair with `|A| = ⌈(n − k)/2⌉` and
`|R| ≥ ⌈(n − k)/2⌉ − 1`, `k = pathwidth G`, whenever `k < n`. -/
theorem exists_empty_pair (h : pathwidth G < Fintype.card V) :
    ∃ A R : Finset V, Disjoint A R ∧ (∀ u ∈ A, ∀ v ∈ R, ¬ G.Adj u v) ∧
      A.card = (Fintype.card V - pathwidth G + 1) / 2 ∧
      (Fintype.card V - pathwidth G + 1) / 2 - 1 ≤ R.card := by
  have hne : (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ)).Nonempty :=
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  obtain ⟨σ, hσ⟩ := Nat.sInf_mem hne
  have hσk : vertexSepOfLayout G σ = pathwidth G := by
    rw [← vertexSeparation_eq_pathwidth]; exact hσ
  obtain ⟨A, R, hAR, hA, hsum, hedge⟩ :=
    exists_empty_pair_of_layout G σ ((Fintype.card V - pathwidth G + 1) / 2 - 1) (by omega)
  exact ⟨A, R, hAR, hedge, by omega, by omega⟩

end MOSPFormalization
