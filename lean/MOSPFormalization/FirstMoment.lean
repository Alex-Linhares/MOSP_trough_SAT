/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The first-moment count: labelled graphs of small pathwidth

The counting inequality behind the first-moment lower bound on the pathwidth of
random graphs (`reports/random_graph_pathwidth_survey.md` §1.4). This is step (1)
of the plan: the finite, deterministic count. The probabilistic asymptotics —
that the right-hand side is `o(2^C(n,2))` below `β*(c)·n` — are step (2) and are
not here; Mathlib has no `G(n, p)`.

Checked by brute force first (`reports/scratch/first_moment/check.py`,
2026-10-31): every labelled graph on `1`–`6` vertices (`2^15 = 32,768` at six),
pathwidth by the subset DP, every `k < n`, zero violations of the main
inequality and of both corollaries; `card_emptyPairGraphs` exact for every
disjoint `(A, R)` at `n ≤ 5` (363 pairs).

## The argument

Write `n = |V|`, `C = n.choose 2`, `t = (n − k + 1) / 2 = ⌈(n − k)/2⌉`. By
`exists_empty_pair` (`EmptyPair.lean`) every graph of pathwidth `≤ k < n` has an
*empty pair* `(A, R)` — disjoint, no `A`–`R` edge — with `|A| ≥ t` and
`|R| ≥ t − 1`, hence one with `|A| = t`, `|R| = t − 1` exactly. The graphs with a
given empty pair `(A, R)` are the edge sets inside the `C − |A|·|R|` off-diagonal
pairs not joining `A` to `R`, so there are `2^(C − |A||R|)` of them; there are
`n.choose t · (n − t).choose (t − 1)` pairs `(A, R)`; the union bound gives

  `#{G : pathwidth G ≤ k} ≤ n.choose t · (n − t).choose (t − 1) · 2^(C − t(t − 1))`.

## Main results

* `edges G` — the edge finset of `G`, with decidability fixed classically so that
  `G ↦ edges G` is one injective function (`edges_injective`); `card_edges_top`
  is Mathlib's `card_edgeFinset_top_eq_card_choose_two`.
* `forbidden A R` — the `|A|·|R|` pairs `s(a, r)` (`card_forbidden`, for disjoint
  `A`, `R`); `IsEmptyPair G A R` — no edge between `A` and `R`.
* `image_edges_emptyPairGraphs` — `edges` maps the graphs with empty pair `(A, R)`
  onto the subsets of `edges ⊤ \ forbidden A R`, via `SimpleGraph.fromEdgeSet`.
* `card_emptyPairGraphs` — **`#{G : IsEmptyPair G A R} = 2^(C − |A|·|R|)`**;
  `card_simpleGraph` — **`Fintype.card (SimpleGraph V) = 2^C`**, the case
  `A = R = ∅` (Mathlib has the `Fintype` instance but not this count).
* `card_graphsOfPathwidthLe_le` — **the inequality above**, for any finite `V`
  and `k < |V|`; `card_pathwidth_le_le` is the same on `Fin n`.
* `card_pathwidth_le_mul_pow_le` — the `p = 1/2` reading, multiplied through:
  `#{pw ≤ k} · 2^(t(t−1)) ≤ n.choose t · (n − t).choose (t − 1) · 2^C`, using
  `mul_pred_le_choose_two`, `t(t − 1) ≤ C` for `k < n`.
* `gnpWeight p G = p^|E(G)| (1 − p)^(C − |E(G)|)`, the `G(n, p)` probability of a
  labelled graph; `sum_gnpWeight_emptyPairGraphs` — **the `G(n, p)` probability
  of a given empty pair `(A, R)` is `(1 − p)^(|A|·|R|)`**, by the same
  reindexing with the binomial theorem (`Finset.sum_pow_mul_eq_add_pow`) in
  place of `card_powerset`; `sum_biUnion_le_sum_of_nonneg` is the union bound
  for sums of nonnegative reals, which Mathlib has only for cardinalities.
* `weightedSum_graphsOfPathwidthLe_le` — **the `G(n, p)` reading**, `0 ≤ p ≤ 1`,
  over `ℝ`: `∑_{pw G ≤ k} gnpWeight p G ≤ n.choose t · (n − t).choose (t − 1) · (1 − p)^(t(t−1))`,
  i.e. `P(pathwidth ≤ k) ≤ n.choose t · (n − t).choose (t − 1) · (1 − p)^(t(t−1))`;
  `weightedSum_pathwidth_le_le` is the same on `Fin n` with the weight written out.
  Step (2) is to show this is `o(1)` at `p = c/n`, `k = βn`, `β < β*(c)`.

No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only.
-/

import MOSPFormalization.EmptyPair
import Mathlib.Combinatorics.SimpleGraph.Finite
import Mathlib.Data.Sym.Card
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### Graphs as edge finsets -/

/-- The edge set of `G` as a finset, with decidability chosen classically so that
`G ↦ edges G` is a single function on `SimpleGraph V`. -/
noncomputable def edges (G : SimpleGraph V) : Finset (Sym2 V) := by
  classical exact G.edgeFinset

theorem mem_edges {G : SimpleGraph V} {e : Sym2 V} : e ∈ edges G ↔ e ∈ G.edgeSet := by
  simp [edges]

theorem edges_injective : Function.Injective (edges (V := V)) := by
  intro G H h
  simpa [edges] using h

theorem card_edges_top : (edges (⊤ : SimpleGraph V)).card = (Fintype.card V).choose 2 := by
  unfold edges
  convert SimpleGraph.card_edgeFinset_top_eq_card_choose_two (V := V)

theorem mem_edges_top {e : Sym2 V} : e ∈ edges (⊤ : SimpleGraph V) ↔ ¬ e.IsDiag := by
  rw [mem_edges, SimpleGraph.edgeSet_top]
  rfl

theorem edges_subset_top (G : SimpleGraph V) : edges G ⊆ edges (⊤ : SimpleGraph V) := by
  intro e he
  rw [mem_edges_top]
  exact SimpleGraph.not_isDiag_of_mem_edgeSet G (mem_edges.1 he)

/-! ### Forbidden pairs and empty pairs -/

/-- The pairs `s(a, r)` with `a ∈ A`, `r ∈ R`: the edges an empty pair `(A, R)` forbids. -/
def forbidden (A R : Finset V) : Finset (Sym2 V) :=
  (A ×ˢ R).image (fun p => s(p.1, p.2))

theorem mem_forbidden {A R : Finset V} {e : Sym2 V} :
    e ∈ forbidden A R ↔ ∃ a ∈ A, ∃ r ∈ R, e = s(a, r) := by
  simp only [forbidden, mem_image, mem_product, Prod.exists]
  constructor
  · rintro ⟨a, r, ⟨ha, hr⟩, rfl⟩
    exact ⟨a, ha, r, hr, rfl⟩
  · rintro ⟨a, ha, r, hr, rfl⟩
    exact ⟨a, r, ⟨ha, hr⟩, rfl⟩

theorem card_forbidden {A R : Finset V} (hAR : Disjoint A R) :
    (forbidden A R).card = A.card * R.card := by
  rw [forbidden, card_image_of_injOn, card_product]
  rintro ⟨a, r⟩ h ⟨a', r'⟩ h' heq
  simp only [coe_product, Set.mem_prod, mem_coe] at h h'
  simp only [Sym2.eq_iff] at heq
  rcases heq with ⟨rfl, rfl⟩ | ⟨h1, h2⟩
  · rfl
  · exact absurd h.1 (Finset.disjoint_right.1 hAR (h1 ▸ h'.2))

theorem forbidden_subset_top {A R : Finset V} (hAR : Disjoint A R) :
    forbidden A R ⊆ edges (⊤ : SimpleGraph V) := by
  intro e he
  obtain ⟨a, ha, r, hr, rfl⟩ := mem_forbidden.1 he
  rw [mem_edges_top, Sym2.mk_isDiag_iff]
  intro h
  exact Finset.disjoint_left.1 hAR ha (h ▸ hr)

/-- `(A, R)` is an empty pair of `G`: no edge joins `A` to `R`. -/
def IsEmptyPair (G : SimpleGraph V) (A R : Finset V) : Prop :=
  ∀ a ∈ A, ∀ r ∈ R, ¬ G.Adj a r

/-- The graphs on `V` with empty pair `(A, R)`. -/
noncomputable def emptyPairGraphs (A R : Finset V) : Finset (SimpleGraph V) := by
  classical exact univ.filter (fun G => IsEmptyPair G A R)

theorem mem_emptyPairGraphs {A R : Finset V} {G : SimpleGraph V} :
    G ∈ emptyPairGraphs A R ↔ IsEmptyPair G A R := by
  simp [emptyPairGraphs]

theorem edges_subset_of_isEmptyPair {G : SimpleGraph V} {A R : Finset V}
    (h : IsEmptyPair G A R) : edges G ⊆ edges (⊤ : SimpleGraph V) \ forbidden A R := by
  intro e he
  rw [mem_sdiff]
  refine ⟨edges_subset_top G he, fun hf => ?_⟩
  obtain ⟨a, ha, r, hr, rfl⟩ := mem_forbidden.1 hf
  exact h a ha r hr ((SimpleGraph.mem_edgeSet G).1 (mem_edges.1 he))

theorem edges_fromEdgeSet (S : Finset (Sym2 V)) (hS : S ⊆ edges (⊤ : SimpleGraph V)) :
    edges (SimpleGraph.fromEdgeSet (S : Set (Sym2 V))) = S := by
  ext e
  rw [mem_edges, SimpleGraph.edgeSet_fromEdgeSet, Set.mem_sdiff, mem_coe]
  exact ⟨fun h => h.1, fun h => ⟨h, mem_edges_top.1 (hS h)⟩⟩

theorem isEmptyPair_fromEdgeSet {A R : Finset V} {S : Finset (Sym2 V)}
    (hS : S ⊆ edges (⊤ : SimpleGraph V) \ forbidden A R) :
    IsEmptyPair (SimpleGraph.fromEdgeSet (S : Set (Sym2 V))) A R := by
  intro a ha r hr hadj
  rw [SimpleGraph.fromEdgeSet_adj, mem_coe] at hadj
  exact (mem_sdiff.1 (hS hadj.1)).2 (mem_forbidden.2 ⟨a, ha, r, hr, rfl⟩)

/-- `edges` maps the graphs with empty pair `(A, R)` onto the subsets of the allowed pairs. -/
theorem image_edges_emptyPairGraphs (A R : Finset V) :
    (emptyPairGraphs A R).image edges = (edges (⊤ : SimpleGraph V) \ forbidden A R).powerset := by
  ext S
  rw [mem_image, mem_powerset]
  constructor
  · rintro ⟨G, hG, rfl⟩
    exact edges_subset_of_isEmptyPair (mem_emptyPairGraphs.1 hG)
  · intro hS
    exact ⟨SimpleGraph.fromEdgeSet (S : Set (Sym2 V)),
      mem_emptyPairGraphs.2 (isEmptyPair_fromEdgeSet hS),
      edges_fromEdgeSet S (hS.trans sdiff_subset)⟩

/-- **The graphs with a given empty pair**: `2^(C(n,2) − |A|·|R|)` of them. -/
theorem card_emptyPairGraphs {A R : Finset V} (hAR : Disjoint A R) :
    (emptyPairGraphs A R).card = 2 ^ ((Fintype.card V).choose 2 - A.card * R.card) := by
  rw [← card_image_of_injOn edges_injective.injOn, image_edges_emptyPairGraphs, card_powerset,
    card_sdiff_of_subset (forbidden_subset_top hAR), card_edges_top, card_forbidden hAR]

/-- **The number of labelled simple graphs** on `V` is `2^(C(n,2))`. -/
theorem card_simpleGraph : Fintype.card (SimpleGraph V) = 2 ^ (Fintype.card V).choose 2 := by
  have h := card_emptyPairGraphs (V := V) (A := ∅) (R := ∅) (Finset.disjoint_empty_left _)
  rw [card_empty, zero_mul, Nat.sub_zero] at h
  have huniv : emptyPairGraphs (∅ : Finset V) ∅ = univ := by
    ext G
    simp [mem_emptyPairGraphs, IsEmptyPair]
  rw [← card_univ, ← huniv, h]

/-! ### The union bound -/

/-- The pairs `(A, R)` with `|A| = t`, `|R| = t − 1`, `R ⊆ V ∖ A`. -/
def emptyPairIndices (t : ℕ) : Finset (Σ _ : Finset V, Finset V) :=
  (univ.powersetCard t).sigma (fun A => (univ \ A).powersetCard (t - 1))

theorem mem_emptyPairIndices {t : ℕ} {p : Σ _ : Finset V, Finset V} :
    p ∈ emptyPairIndices t ↔ p.1.card = t ∧ p.2 ⊆ univ \ p.1 ∧ p.2.card = t - 1 := by
  simp only [emptyPairIndices, mem_sigma, mem_powersetCard, subset_univ, true_and]

theorem disjoint_of_mem_emptyPairIndices {t : ℕ} {p : Σ _ : Finset V, Finset V}
    (hp : p ∈ emptyPairIndices t) : Disjoint p.1 p.2 := by
  obtain ⟨_, hR, _⟩ := mem_emptyPairIndices.1 hp
  rw [Finset.disjoint_left]
  intro x hx1 hx2
  exact (mem_sdiff.1 (hR hx2)).2 hx1

theorem card_emptyPairIndices (t : ℕ) :
    (emptyPairIndices (V := V) t).card =
      (Fintype.card V).choose t * (Fintype.card V - t).choose (t - 1) := by
  unfold emptyPairIndices
  rw [card_sigma]
  rw [Finset.sum_congr rfl (g := fun _ => (Fintype.card V - t).choose (t - 1))
    (fun A hA => by rw [card_powersetCard, card_univ_sdiff, (mem_powersetCard.1 hA).2])]
  rw [sum_const, card_powersetCard, card_univ, smul_eq_mul]

/-- The graphs of pathwidth at most `k`. -/
noncomputable def graphsOfPathwidthLe (k : ℕ) : Finset (SimpleGraph V) := by
  classical exact univ.filter (fun G => pathwidth G ≤ k)

theorem mem_graphsOfPathwidthLe {k : ℕ} {G : SimpleGraph V} :
    G ∈ graphsOfPathwidthLe k ↔ pathwidth G ≤ k := by
  simp [graphsOfPathwidthLe]

open scoped Classical in
/-- Every graph of pathwidth `≤ k < n` has an empty pair `(A, R)` with `|A| = t`,
`|R| = t − 1`, `t = (n − k + 1) / 2`: by `exists_empty_pair`, shrinking the pair. -/
theorem mem_biUnion_emptyPairIndices {k : ℕ} (hk : k < Fintype.card V) {G : SimpleGraph V}
    (hG : pathwidth G ≤ k) :
    G ∈ (emptyPairIndices ((Fintype.card V - k + 1) / 2)).biUnion
      (fun p => emptyPairGraphs p.1 p.2) := by
  classical
  obtain ⟨A, R, hAR, hedge, hA, hR⟩ := exists_empty_pair G (by omega)
  obtain ⟨A', hA'A, hA'⟩ := Finset.exists_subset_card_eq
    (s := A) (n := (Fintype.card V - k + 1) / 2) (by omega)
  obtain ⟨R', hR'R, hR'⟩ := Finset.exists_subset_card_eq
    (s := R) (n := (Fintype.card V - k + 1) / 2 - 1) (by omega)
  rw [mem_biUnion]
  refine ⟨⟨A', R'⟩, mem_emptyPairIndices.2 ⟨hA', ?_, hR'⟩,
    mem_emptyPairGraphs.2 (fun a ha r hr => hedge a (hA'A ha) r (hR'R hr))⟩
  intro r hr
  rw [mem_sdiff]
  exact ⟨mem_univ r, fun hrA => Finset.disjoint_left.1 hAR (hA'A hrA) (hR'R hr)⟩

/-- **The first-moment count.** For `k < n = |V|` and `t = (n − k + 1) / 2`,
`#{G : pathwidth G ≤ k} ≤ n.choose t · (n − t).choose (t − 1) · 2^(C(n,2) − t(t − 1))`. -/
theorem card_graphsOfPathwidthLe_le (k : ℕ) (hk : k < Fintype.card V) :
    (graphsOfPathwidthLe (V := V) k).card ≤
      (Fintype.card V).choose ((Fintype.card V - k + 1) / 2) *
        (Fintype.card V - (Fintype.card V - k + 1) / 2).choose ((Fintype.card V - k + 1) / 2 - 1) *
        2 ^ ((Fintype.card V).choose 2 -
          (Fintype.card V - k + 1) / 2 * ((Fintype.card V - k + 1) / 2 - 1)) := by
  classical
  set t := (Fintype.card V - k + 1) / 2 with ht
  calc (graphsOfPathwidthLe (V := V) k).card
      ≤ ((emptyPairIndices t).biUnion (fun p => emptyPairGraphs p.1 p.2)).card :=
        card_le_card (fun G hG =>
          mem_biUnion_emptyPairIndices hk (mem_graphsOfPathwidthLe.1 hG))
    _ ≤ (emptyPairIndices (V := V) t).card * 2 ^ ((Fintype.card V).choose 2 - t * (t - 1)) := by
        refine card_biUnion_le_card_mul _ _ _ (fun p hp => ?_)
        obtain ⟨hA, _, hR⟩ := mem_emptyPairIndices.1 hp
        rw [card_emptyPairGraphs (disjoint_of_mem_emptyPairIndices hp), hA, hR]
    _ = _ := by rw [card_emptyPairIndices]

open scoped Classical in
/-- The same on `Fin n`, with the filter written out. -/
theorem card_pathwidth_le_le (n k : ℕ) (hk : k < n) :
    (univ.filter (fun G : SimpleGraph (Fin n) => pathwidth G ≤ k)).card ≤
      n.choose ((n - k + 1) / 2) * (n - (n - k + 1) / 2).choose ((n - k + 1) / 2 - 1) *
        2 ^ (n.choose 2 - (n - k + 1) / 2 * ((n - k + 1) / 2 - 1)) := by
  have h := card_graphsOfPathwidthLe_le (V := Fin n) k (by simpa using hk)
  simp only [Fintype.card_fin] at h
  convert h using 2
  simp [graphsOfPathwidthLe]

/-! ### The probability reading at `p = 1/2` -/

/-- `t(t − 1) ≤ C(n, 2)` for `t = (n − k + 1) / 2`, `k < n`. -/
theorem mul_pred_le_choose_two {n k : ℕ} (hk : k < n) :
    (n - k + 1) / 2 * ((n - k + 1) / 2 - 1) ≤ n.choose 2 := by
  rw [Nat.choose_two_right, Nat.le_div_iff_mul_le two_pos]
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  obtain ⟨u, hu⟩ : ∃ u, (m + 1 - k + 1) / 2 = u + 1 := ⟨(m + 1 - k + 1) / 2 - 1, by omega⟩
  rw [hu]
  have h2u : 2 * u ≤ m := by omega
  simp only [Nat.add_sub_cancel]
  nlinarith [Nat.mul_le_mul h2u h2u]

open scoped Classical in
/-- **The `p = 1/2` reading, multiplied through**:
`#{pw ≤ k} · 2^(t(t−1)) ≤ n.choose t · (n − t).choose (t − 1) · 2^C(n,2)`, i.e.
`P(pathwidth ≤ k) ≤ n.choose t · (n − t).choose (t − 1) / 2^(t(t−1))` in `G(n, 1/2)`. -/
theorem card_pathwidth_le_mul_pow_le (n k : ℕ) (hk : k < n) :
    (univ.filter (fun G : SimpleGraph (Fin n) => pathwidth G ≤ k)).card *
        2 ^ ((n - k + 1) / 2 * ((n - k + 1) / 2 - 1)) ≤
      n.choose ((n - k + 1) / 2) * (n - (n - k + 1) / 2).choose ((n - k + 1) / 2 - 1) *
        2 ^ n.choose 2 := by
  calc (univ.filter (fun G : SimpleGraph (Fin n) => pathwidth G ≤ k)).card *
        2 ^ ((n - k + 1) / 2 * ((n - k + 1) / 2 - 1))
      ≤ n.choose ((n - k + 1) / 2) * (n - (n - k + 1) / 2).choose ((n - k + 1) / 2 - 1) *
          2 ^ (n.choose 2 - (n - k + 1) / 2 * ((n - k + 1) / 2 - 1)) *
          2 ^ ((n - k + 1) / 2 * ((n - k + 1) / 2 - 1)) :=
        Nat.mul_le_mul_right _ (card_pathwidth_le_le n k hk)
    _ = _ := by
        rw [mul_assoc, ← pow_add, Nat.sub_add_cancel (mul_pred_le_choose_two hk)]

/-! ### The `G(n, p)` reading -/

/-- The `G(n, p)` probability of a labelled graph: `p^|E| (1 − p)^(C(n,2) − |E|)`. -/
noncomputable def gnpWeight (p : ℝ) (G : SimpleGraph V) : ℝ :=
  p ^ (edges G).card * (1 - p) ^ ((Fintype.card V).choose 2 - (edges G).card)

theorem gnpWeight_nonneg {p : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (G : SimpleGraph V) :
    0 ≤ gnpWeight p G :=
  mul_nonneg (pow_nonneg hp0 _) (pow_nonneg (sub_nonneg.2 hp1) _)

/-- A sum over a `biUnion` of nonnegative terms is at most the sum of the sums. -/
theorem sum_biUnion_le_sum_of_nonneg {ι α : Type*} [DecidableEq α] (s : Finset ι)
    (t : ι → Finset α) (f : α → ℝ) (hf : ∀ x, 0 ≤ f x) :
    ∑ x ∈ s.biUnion t, f x ≤ ∑ i ∈ s, ∑ x ∈ t i, f x := by
  classical
  refine Finset.induction_on s (by simp) (fun a s has ih => ?_)
  rw [biUnion_insert, sum_insert has]
  have h1 := Finset.sum_union_inter (s₁ := t a) (s₂ := s.biUnion t) (f := f)
  have h0 : 0 ≤ ∑ x ∈ t a ∩ s.biUnion t, f x := sum_nonneg (fun x _ => hf x)
  linarith

/-- **The `G(n, p)` probability of a given empty pair** is `(1 − p)^(|A|·|R|)`: reindex the
graphs by their edge sets and apply the binomial theorem on the allowed pairs. -/
theorem sum_gnpWeight_emptyPairGraphs {A R : Finset V} (hAR : Disjoint A R) (p : ℝ) :
    ∑ G ∈ emptyPairGraphs A R, gnpWeight p G = (1 - p) ^ (A.card * R.card) := by
  have hsub := forbidden_subset_top (V := V) hAR
  set T := edges (⊤ : SimpleGraph V) \ forbidden A R with hT
  have hcard : T.card + A.card * R.card = (Fintype.card V).choose 2 := by
    have hle : (forbidden A R).card ≤ (edges (⊤ : SimpleGraph V)).card := card_le_card hsub
    rw [hT, card_sdiff_of_subset hsub, card_edges_top, card_forbidden hAR] at *
    omega
  calc ∑ G ∈ emptyPairGraphs A R, gnpWeight p G
      = ∑ S ∈ (emptyPairGraphs A R).image edges,
          p ^ S.card * (1 - p) ^ ((Fintype.card V).choose 2 - S.card) := by
        rw [sum_image edges_injective.injOn]
        rfl
    _ = ∑ S ∈ T.powerset,
          (1 - p) ^ (A.card * R.card) * (p ^ S.card * (1 - p) ^ (T.card - S.card)) := by
        rw [image_edges_emptyPairGraphs]
        refine sum_congr rfl (fun S hS => ?_)
        have hS' : S.card ≤ T.card := card_le_card (mem_powerset.1 hS)
        have : (Fintype.card V).choose 2 - S.card = (T.card - S.card) + A.card * R.card := by
          omega
        rw [this, pow_add]
        ring
    _ = (1 - p) ^ (A.card * R.card) * (p + (1 - p)) ^ T.card := by
        rw [← mul_sum, sum_pow_mul_eq_add_pow]
    _ = (1 - p) ^ (A.card * R.card) := by simp

open scoped Classical in
/-- **The first-moment bound in `G(n, p)`**, `0 ≤ p ≤ 1`, `k < n = |V|`, `t = (n − k + 1) / 2`:
`∑_{pathwidth G ≤ k} p^|E(G)| (1 − p)^(C(n,2) − |E(G)|) ≤
  n.choose t · (n − t).choose (t − 1) · (1 − p)^(t(t − 1))`,
i.e. `P(pathwidth ≤ k) ≤ n.choose t · (n − t).choose (t − 1) · (1 − p)^(t(t−1))`. -/
theorem weightedSum_graphsOfPathwidthLe_le (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (k : ℕ)
    (hk : k < Fintype.card V) :
    ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G ≤
      (((Fintype.card V).choose ((Fintype.card V - k + 1) / 2) *
        (Fintype.card V - (Fintype.card V - k + 1) / 2).choose
          ((Fintype.card V - k + 1) / 2 - 1) : ℕ) : ℝ) *
        (1 - p) ^ ((Fintype.card V - k + 1) / 2 * ((Fintype.card V - k + 1) / 2 - 1)) := by
  set t := (Fintype.card V - k + 1) / 2 with ht
  calc ∑ G ∈ graphsOfPathwidthLe (V := V) k, gnpWeight p G
      ≤ ∑ G ∈ (emptyPairIndices t).biUnion (fun q => emptyPairGraphs q.1 q.2), gnpWeight p G :=
        sum_le_sum_of_subset_of_nonneg
          (fun G hG => mem_biUnion_emptyPairIndices hk (mem_graphsOfPathwidthLe.1 hG))
          (fun G _ _ => gnpWeight_nonneg hp0 hp1 G)
    _ ≤ ∑ q ∈ emptyPairIndices t, ∑ G ∈ emptyPairGraphs q.1 q.2, gnpWeight p G :=
        sum_biUnion_le_sum_of_nonneg _ _ _ (gnpWeight_nonneg hp0 hp1)
    _ = ∑ q ∈ emptyPairIndices (V := V) t, (1 - p) ^ (t * (t - 1)) := by
        refine sum_congr rfl (fun q hq => ?_)
        obtain ⟨hA, _, hR⟩ := mem_emptyPairIndices.1 hq
        rw [sum_gnpWeight_emptyPairGraphs (disjoint_of_mem_emptyPairIndices hq), hA, hR]
    _ = _ := by rw [sum_const, card_emptyPairIndices, nsmul_eq_mul]

open scoped Classical in
/-- The same on `Fin n`, with the filter and the weight written out. -/
theorem weightedSum_pathwidth_le_le (n : ℕ) (p : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (k : ℕ)
    (hk : k < n) :
    ∑ G ∈ univ.filter (fun G : SimpleGraph (Fin n) => pathwidth G ≤ k),
        p ^ (edges G).card * (1 - p) ^ (n.choose 2 - (edges G).card) ≤
      ((n.choose ((n - k + 1) / 2) * (n - (n - k + 1) / 2).choose ((n - k + 1) / 2 - 1) : ℕ) : ℝ) *
        (1 - p) ^ ((n - k + 1) / 2 * ((n - k + 1) / 2 - 1)) := by
  have h := weightedSum_graphsOfPathwidthLe_le (V := Fin n) p hp0 hp1 k (by simpa using hk)
  simp only [Fintype.card_fin, gnpWeight] at h
  convert h using 2
  simp [graphsOfPathwidthLe]

end MOSPFormalization
