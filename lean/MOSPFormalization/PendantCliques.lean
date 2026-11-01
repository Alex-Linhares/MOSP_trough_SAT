/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The two-sided pendant bound (Lemma P)

Item 06 of `reports/excess_phase_plan.md` (`reports/excess_phase_diagram.md` §6, Lemma P)
proved on paper, for every graph `G` with a clique `R` and cliques `Q_1, …, Q_q` of size at
least `t` that meet `R` in exactly one vertex each, at distinct vertices `v_1, …, v_q`, that

  `pathwidth G ≥ t + ⌈q/2⌉ − 2`.

It is a pathwidth argument that is not degree-based: the clique floor `ω − 1` sees only one
clique, the pendant bound sees how `q` cliques hang off one. On random small graphs it is
above the clique floor on a few per cent (`reports/scratch/pendant_cliques/check.log`), and
on item 03's block-graph families it is exact at depth one (Theorem F2 of §6, whose lower
half it is). This file is item 13 of loop0010 (the reserve), the next Lean target §6.5 named
(L5).

Checked before it was stated: 1,905 random graphs on 2–8 vertices with exact pathwidth, every
clique as `R`, every choice of pendant cliques dominated — zero violations, tight on 1,474
(`reports/scratch/pendant_cliques/check.py`); and item 06's 594 depth-one graphs and 2,000
random instances before that.

## The proof

Let `X_0, …, X_L` be a path decomposition. By the Helly property
(`PathDecomposition.exists_bag_of_isClique`) `R` lies in some bag `X_a` and each `Q_i` in some
bag `X_{b i}`.

* If some `b i = a`, the bag `X_a` holds `R ∪ Q_i`, which has `|R| + |Q_i| − 1 ≥ q + t − 1`
  vertices (`v` is injective into `R`).
* Otherwise every `b i` is strictly left or strictly right of `a`, and one side holds at least
  `⌈q/2⌉` of them. On the left, let `j` have the largest `b j`: for every other `i` on that
  side, `v_i` lies in `X_{b i}` and in `X_a` with `b i ≤ b j ≤ a`, so in `X_{b j}` by the
  interval property; and `v_i ∉ Q_j` because `Q_j ∩ R = {v_j}` and `v_i ≠ v_j`. So `X_{b j}`
  holds `Q_j` and `⌈q/2⌉ − 1` further vertices: at least `t + ⌈q/2⌉ − 1`. The right side is
  the mirror image (`j` with the smallest `b j`).

Either way some bag has at least `t + ⌈q/2⌉ − 1` vertices, so the width is at least
`t + ⌈q/2⌉ − 2`. In `ℕ`, `⌈q/2⌉ = (q + 1) / 2` and the statement is
`t + (q + 1) / 2 ≤ pathwidth G + 2`.

## Main results

* `PathDecomposition.pendant_bound` — the bound for one decomposition,
  `t + (q + 1) / 2 ≤ D.width + 2`.
* `pathwidth_ge_of_pendant_cliques` — **(L5), Lemma P**: `t + (q + 1) / 2 ≤ pathwidth G + 2`.
* `MOSPInstance.mospValue_ge_of_pendant_patterns` — in MOSP terms: a pattern `p₀` and `q`
  patterns `p i` with at least `t` customers each, meeting `p₀` in exactly one customer `v i`,
  the `v i` distinct, force `t + (q + 1) / 2 ≤ mospValue M + 1`.
* `pathwidth_ge_of_clique_pendant_cliques` — the depth-one case `t = q = s` behind
  `CT(s, 1, b) = ⌈3s/2⌉ − 2`: a clique of size `s` with a clique of size `≥ s` pendant at each
  vertex forces `s + (s + 1) / 2 ≤ pathwidth G + 2`.
-/

import MOSPFormalization.MOSPGraph

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V}

/-! ### Three facts about `Q ∩ R = {x}` -/

theorem mem_left_of_inter_eq_singleton {Q R : Finset V} {x : V} (h : Q ∩ R = {x}) : x ∈ Q := by
  have : x ∈ Q ∩ R := by rw [h]; exact Finset.mem_singleton_self x
  exact (Finset.mem_inter.mp this).1

theorem mem_right_of_inter_eq_singleton {Q R : Finset V} {x : V} (h : Q ∩ R = {x}) : x ∈ R := by
  have : x ∈ Q ∩ R := by rw [h]; exact Finset.mem_singleton_self x
  exact (Finset.mem_inter.mp this).2

theorem not_mem_left_of_inter_eq_singleton {Q R : Finset V} {x y : V} (h : Q ∩ R = {y})
    (hx : x ∈ R) (hxy : x ≠ y) : x ∉ Q := by
  intro hxQ
  have : x ∈ Q ∩ R := Finset.mem_inter.mpr ⟨hxQ, hx⟩
  rw [h, Finset.mem_singleton] at this
  exact hxy this

namespace PathDecomposition

/-- A pendant clique's private vertices and the other attachment vertices are disjoint. -/
theorem disjoint_pendant_image {ι : Type*} [DecidableEq ι] {R : Finset V} {Q : ι → Finset V}
    {v : ι → V} (hv : Function.Injective v) (hQR : ∀ i, Q i ∩ R = {v i}) (S : Finset ι) (j : ι) :
    Disjoint (Q j) ((S.erase j).image v) := by
  rw [Finset.disjoint_left]
  intro x hxQ hxI
  obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hxI
  exact not_mem_left_of_inter_eq_singleton (hQR j) (mem_right_of_inter_eq_singleton (hQR i))
    (fun h => Finset.ne_of_mem_erase hi (hv h)) hxQ

/-- **Left side.** If the bags `b i` of the pendant cliques `i ∈ S` all lie strictly before
the bag `a` holding `R`, the one with the largest `b j` holds `Q j` together with the other
attachment vertices of `S`: `|Q j| + |S| − 1` vertices. -/
theorem exists_bag_of_pendant_left (D : PathDecomposition G) {ι : Type*} [DecidableEq ι]
    {R : Finset V} {Q : ι → Finset V} {v : ι → V} (hv : Function.Injective v)
    (hQR : ∀ i, Q i ∩ R = {v i}) {a : Fin (D.length + 1)} (haR : R ⊆ D.bag a)
    {b : ι → Fin (D.length + 1)} (hb : ∀ i, Q i ⊆ D.bag (b i))
    (S : Finset ι) (hS : S.Nonempty) (hside : ∀ i ∈ S, b i < a) :
    ∃ j ∈ S, (Q j).card + S.card ≤ (D.bag (b j)).card + 1 := by
  obtain ⟨j, hj, hmax⟩ := S.exists_max_image b hS
  refine ⟨j, hj, ?_⟩
  have hsub : Q j ∪ (S.erase j).image v ⊆ D.bag (b j) := by
    intro x hx
    rcases Finset.mem_union.mp hx with hx | hx
    · exact hb j hx
    · obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
      exact D.interval (v i) (b i) (b j) a (hmax i (Finset.mem_of_mem_erase hi))
        (le_of_lt (hside j hj)) (hb i (mem_left_of_inter_eq_singleton (hQR i)))
        (haR (mem_right_of_inter_eq_singleton (hQR i)))
  have hcard := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint (disjoint_pendant_image hv hQR S j),
    Finset.card_image_of_injective _ hv, Finset.card_erase_of_mem hj] at hcard
  have := Finset.card_pos.mpr ⟨j, hj⟩
  omega

/-- **Right side**, the mirror image: the one with the smallest `b j`. -/
theorem exists_bag_of_pendant_right (D : PathDecomposition G) {ι : Type*} [DecidableEq ι]
    {R : Finset V} {Q : ι → Finset V} {v : ι → V} (hv : Function.Injective v)
    (hQR : ∀ i, Q i ∩ R = {v i}) {a : Fin (D.length + 1)} (haR : R ⊆ D.bag a)
    {b : ι → Fin (D.length + 1)} (hb : ∀ i, Q i ⊆ D.bag (b i))
    (S : Finset ι) (hS : S.Nonempty) (hside : ∀ i ∈ S, a < b i) :
    ∃ j ∈ S, (Q j).card + S.card ≤ (D.bag (b j)).card + 1 := by
  obtain ⟨j, hj, hmin⟩ := S.exists_min_image b hS
  refine ⟨j, hj, ?_⟩
  have hsub : Q j ∪ (S.erase j).image v ⊆ D.bag (b j) := by
    intro x hx
    rcases Finset.mem_union.mp hx with hx | hx
    · exact hb j hx
    · obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
      exact D.interval (v i) a (b j) (b i) (le_of_lt (hside j hj))
        (hmin i (Finset.mem_of_mem_erase hi))
        (haR (mem_right_of_inter_eq_singleton (hQR i)))
        (hb i (mem_left_of_inter_eq_singleton (hQR i)))
  have hcard := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint (disjoint_pendant_image hv hQR S j),
    Finset.card_image_of_injective _ hv, Finset.card_erase_of_mem hj] at hcard
  have := Finset.card_pos.mpr ⟨j, hj⟩
  omega

/-- **Lemma P for one decomposition.** A clique `R` and `q ≥ 1` cliques `Q i` of size at
least `t`, each meeting `R` exactly in `v i`, the `v i` distinct: some bag has at least
`t + ⌈q/2⌉ − 1` vertices, i.e. `t + (q + 1) / 2 ≤ D.width + 2`. -/
theorem pendant_bound (D : PathDecomposition G) {q : ℕ} (hq : 1 ≤ q)
    (R : Finset V) (hR : G.IsClique (R : Set V))
    (Q : Fin q → Finset V) (hQ : ∀ i, G.IsClique (Q i : Set V))
    (t : ℕ) (ht : ∀ i, t ≤ (Q i).card)
    (v : Fin q → V) (hv : Function.Injective v) (hQR : ∀ i, Q i ∩ R = {v i}) :
    t + (q + 1) / 2 ≤ D.width + 2 := by
  obtain ⟨a, haR⟩ := D.exists_bag_of_isClique R hR
  choose b hb using fun i => D.exists_bag_of_isClique (Q i) (hQ i)
  by_cases hex : ∃ i, b i = a
  · -- the bag of `R` holds a whole pendant clique as well
    obtain ⟨i, hi⟩ := hex
    have hsub : R ∪ Q i ⊆ D.bag a := Finset.union_subset haR (hi ▸ hb i)
    have hcard := Finset.card_le_card hsub
    have hunion := Finset.card_union_add_card_inter R (Q i)
    have hint : (R ∩ Q i).card = 1 := by
      rw [Finset.inter_comm, hQR i, Finset.card_singleton]
    have hRq : q ≤ R.card := by
      have himg : Finset.univ.image v ⊆ R := by
        intro x hx
        obtain ⟨k, _, rfl⟩ := Finset.mem_image.mp hx
        exact mem_right_of_inter_eq_singleton (hQR k)
      have := Finset.card_le_card himg
      rwa [Finset.card_image_of_injective _ hv, Finset.card_univ, Fintype.card_fin] at this
    have hw := D.bag_card_le_width_add_one a
    have := ht i
    omega
  · -- every pendant bag is strictly left or strictly right of `a`
    replace hex : ∀ i, b i ≠ a := fun i h => hex ⟨i, h⟩
    have hsplit := Finset.card_filter_add_card_filter_not (s := (Finset.univ : Finset (Fin q)))
      (fun i => b i < a)
    rw [Finset.card_univ, Fintype.card_fin] at hsplit
    rcases le_or_gt ((q + 1) / 2) (Finset.univ.filter (fun i => b i < a)).card with hL | hL
    · have hne : (Finset.univ.filter (fun i => b i < a)).Nonempty :=
        Finset.card_pos.mp (by omega)
      obtain ⟨j, hj, hcard⟩ := D.exists_bag_of_pendant_left hv hQR haR hb _ hne
        (fun i hi => (Finset.mem_filter.mp hi).2)
      have hw := D.bag_card_le_width_add_one (b j)
      have := ht j
      omega
    · have hne : (Finset.univ.filter (fun i => ¬ b i < a)).Nonempty :=
        Finset.card_pos.mp (by omega)
      obtain ⟨j, hj, hcard⟩ := D.exists_bag_of_pendant_right hv hQR haR hb _ hne
        (fun i hi => lt_of_le_of_ne (not_lt.mp (Finset.mem_filter.mp hi).2) (Ne.symm (hex i)))
      have hw := D.bag_card_le_width_add_one (b j)
      have := ht j
      have hc : (q + 1) / 2 ≤ (Finset.univ.filter (fun i => ¬ b i < a)).card := by omega
      omega

end PathDecomposition

/-- **Lemma P, the two-sided pendant bound (L5).** For any graph `G`, a clique `R` and
`q ≥ 1` cliques `Q i` with `t ≤ |Q i|` and `Q i ∩ R = {v i}`, the `v i` distinct, force
`pathwidth G ≥ t + ⌈q/2⌉ − 2`, stated as `t + (q + 1) / 2 ≤ pathwidth G + 2`. -/
theorem pathwidth_ge_of_pendant_cliques (G : SimpleGraph V) {q : ℕ} (hq : 1 ≤ q)
    (R : Finset V) (hR : G.IsClique (R : Set V))
    (Q : Fin q → Finset V) (hQ : ∀ i, G.IsClique (Q i : Set V))
    (t : ℕ) (ht : ∀ i, t ≤ (Q i).card)
    (v : Fin q → V) (hv : Function.Injective v) (hQR : ∀ i, Q i ∩ R = {v i}) :
    t + (q + 1) / 2 ≤ pathwidth G + 2 := by
  obtain ⟨D, hD⟩ := exists_pathDecomposition_width_eq G
  rw [← hD]
  exact D.pendant_bound hq R hR Q hQ t ht v hv hQR

/-- The depth-one case behind `CT(s, 1, b) = ⌈3s/2⌉ − 2`: a clique `R` of size `s` with a
clique of size at least `s` pendant at each of its vertices forces
`pathwidth G ≥ s + ⌈s/2⌉ − 2`. -/
theorem pathwidth_ge_of_clique_pendant_cliques (G : SimpleGraph V) (R : Finset V)
    (hR : G.IsClique (R : Set V)) (hs : 1 ≤ R.card)
    (Q : R → Finset V) (hQ : ∀ x, G.IsClique (Q x : Set V)) (ht : ∀ x, R.card ≤ (Q x).card)
    (hQR : ∀ x : R, Q x ∩ R = {(x : V)}) :
    R.card + (R.card + 1) / 2 ≤ pathwidth G + 2 := by
  let e : Fin R.card ≃ R := (Finset.equivFin R).symm
  have := pathwidth_ge_of_pendant_cliques G hs R hR (fun i => Q (e i)) (fun i => hQ (e i))
    R.card (fun i => ht (e i)) (fun i => (e i : V))
    (fun i j h => e.injective (Subtype.ext h)) (fun i => hQR (e i))
  exact this

namespace MOSPInstance

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]
variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- **Lemma P in MOSP terms.** A pattern `p₀` and `q ≥ 1` patterns `p i` with at least `t`
customers each, meeting `p₀` in exactly one customer `v i`, the `v i` distinct, force
`mospValue M ≥ t + ⌈q/2⌉ − 1`, stated as `t + (q + 1) / 2 ≤ mospValue M + 1`. -/
theorem mospValue_ge_of_pendant_patterns {q : ℕ} (hq : 1 ≤ q) (p₀ : Pt) (p : Fin q → Pt)
    (t : ℕ) (ht : ∀ i, t ≤ (M.customers (p i)).card)
    (v : Fin q → C) (hv : Function.Injective v)
    (hpv : ∀ i, M.customers (p i) ∩ M.customers p₀ = {v i}) :
    t + (q + 1) / 2 ≤ M.mospValue + 1 := by
  have hreq : ∃ c p, M.requires c p := by
    refine ⟨v ⟨0, hq⟩, p₀, ?_⟩
    exact (M.mem_customers_iff p₀ _).mp (mem_right_of_inter_eq_singleton (hpv ⟨0, hq⟩))
  have h := pathwidth_ge_of_pendant_cliques M.mospGraph hq (M.customers p₀)
    (M.customers_isClique p₀) (fun i => M.customers (p i)) (fun i => M.customers_isClique (p i))
    t ht v hv hpv
  have := M.pathwidth_add_one_le_mospValue hreq
  omega

end MOSPInstance

end MOSPFormalization
