/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The pathwidth of the hypercube

**Theorem** (Chandran & Kavitha 2006, Theorem 2, after Harper 1966). For every
`d`, the `d`-dimensional hypercube `Q_d` has pathwidth
`Σ_{i < d} C(i, ⌊i/2⌋)` (OEIS A036256: `0, 1, 2, 4, 7, 13, 23, 43, …`).

This file formalises the published theorem; no novelty is claimed. Chandran &
Kavitha argue `pw ≥ b_v(s)` through interval supergraphs and get the upper
bound from Harper's bandwidth; we argue both directions on vertex separation,
which `VSEquivPW.lean` equates with pathwidth (Kinnersley 1992).

## Definitions

* `hypercube d` — the graph on `Finset (Fin d)` in which two sets are adjacent
  when their symmetric difference is a single element.
* `cubeGraph d` — the same graph on the subsets of `range d ⊆ ℕ`, where the
  combinatorics of `Hypercube/` lives; `hypercubeIsoCubeGraph` relates them.

## Proof

The vertex separation of a layout at position `i` is the outer vertex boundary
`|N[P] \ P|` of its prefix `P` (`vertexSepAt_cubeGraph`).

* **Lower bound.** Some initial segment `T` of the simplicial order has
  `|N[T]| - |T| ≥ harperSum d` (`exists_init_profile`, Harper's induction), and by
  Harper's vertex-isoperimetric theorem (`harper`, proved in
  `Hypercube/Harper.lean` by compression) every set of `|T|` vertices has a
  closed neighbourhood at least as large. Every layout has a prefix of size `|T|`.
* **Upper bound.** The layout along the simplicial order
  (`simplicialLayout`) has initial segments for prefixes, each with at most
  `harperSum d` boundary vertices (`card_nbhd_init_le`).

## Main results

* `pathwidth_cubeGraph` — `pathwidth (cubeGraph d) = harperSum d`.
* `pathwidth_hypercube` — `pathwidth (hypercube d) = Σ i ∈ range d, i.choose (i / 2)`.

## References

* L. S. Chandran, T. Kavitha, *The treewidth and pathwidth of hypercubes*,
  Discrete Math. 306 (2006) 359–365 (`literature/chandran_kavitha_2006_…pdf`).
* L. H. Harper, *Optimal numberings and isoperimetric problems on graphs*,
  J. Combin. Theory 1 (1966) 385–393.
-/

import MOSPFormalization.Hypercube.Profile
import MOSPFormalization.Sandwich
import MOSPFormalization.Minor

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open Finset Hypercube
open scoped symmDiff

/-! ### The graph -/

/-- The vertices of `Q_d`: the subsets of `range d`. -/
abbrev CubeV (d : ℕ) := ↥((range d).powerset)

/-- `Q_d` on the subsets of `range d`. -/
def cubeGraph (d : ℕ) : SimpleGraph (CubeV d) where
  Adj x y := Hypercube.Adj x.1 y.1
  symm := ⟨fun _ _ h => Hypercube.Adj.symm h⟩
  loopless := ⟨fun _ h => Hypercube.Adj.ne h rfl⟩

noncomputable instance (d : ℕ) : DecidableRel (cubeGraph d).Adj := Classical.decRel _

theorem cubeGraph_adj {d : ℕ} {x y : CubeV d} : (cubeGraph d).Adj x y ↔ Hypercube.Adj x.1 y.1 :=
  Iff.rfl

/-! ### Layouts: prefixes and their boundaries -/

theorem card_prefixSet {V : Type*} [Fintype V] [DecidableEq V] (σ : LinearLayout V) {i : ℕ}
    (hi : i < Fintype.card V) : (prefixSet σ i).card = i + 1 := by
  have : (prefixSet σ i).map σ.toEmbedding = Finset.Iic ⟨i, hi⟩ := by
    ext j
    simp only [mem_map, mem_prefixSet_iff, Equiv.coe_toEmbedding, mem_Iic, Fin.le_def]
    constructor
    · rintro ⟨v, hv, rfl⟩; exact hv
    · intro hj; exact ⟨σ.symm j, by simpa using hj, by simp⟩
  rw [← card_map σ.toEmbedding, this, Fin.card_Iic]

/-- The prefix of a layout, as a family of subsets of `range d`. -/
def prefixFam {d : ℕ} (σ : LinearLayout (CubeV d)) (i : ℕ) : Finset (Finset ℕ) :=
  (prefixSet σ i).map (Function.Embedding.subtype _)

theorem mem_prefixFam {d : ℕ} {σ : LinearLayout (CubeV d)} {i : ℕ} {y : Finset ℕ} :
    y ∈ prefixFam σ i ↔ ∃ h : y ∈ (range d).powerset, (σ ⟨y, h⟩).val ≤ i := by
  unfold prefixFam
  rw [mem_map]
  constructor
  · rintro ⟨v, hv, rfl⟩
    exact ⟨v.2, by simpa [mem_prefixSet_iff] using hv⟩
  · rintro ⟨h, hle⟩
    exact ⟨⟨y, h⟩, by rw [mem_prefixSet_iff]; exact hle, rfl⟩

theorem prefixFam_subset {d : ℕ} (σ : LinearLayout (CubeV d)) (i : ℕ) :
    prefixFam σ i ⊆ (range d).powerset := by
  intro y hy
  obtain ⟨h, -⟩ := mem_prefixFam.mp hy
  exact h

theorem card_prefixFam {d : ℕ} (σ : LinearLayout (CubeV d)) (i : ℕ) :
    (prefixFam σ i).card = (prefixSet σ i).card := card_map _

/-- The vertex separation at a position is the outer boundary of the prefix. -/
theorem vertexSepAt_cubeGraph {d : ℕ} (σ : LinearLayout (CubeV d)) (i : ℕ) :
    vertexSepAt (cubeGraph d) σ i =
      (nbhd (range d) (prefixFam σ i)).card - (prefixFam σ i).card := by
  have hmap : (activeSuffix (cubeGraph d) σ i).map (Function.Embedding.subtype _) =
      nbhd (range d) (prefixFam σ i) \ prefixFam σ i := by
    ext y
    rw [mem_map, mem_sdiff, mem_nbhd]
    constructor
    · rintro ⟨v, hv, rfl⟩
      rw [mem_activeSuffix_iff] at hv
      obtain ⟨hvi, u, hu, hadj⟩ := hv
      refine ⟨⟨mem_powerset.mp v.2, u.1, ?_, Or.inr hadj⟩, ?_⟩
      · exact mem_prefixFam.mpr ⟨u.2, by rwa [mem_prefixSet_iff] at hu⟩
      · rintro hy
        obtain ⟨h', hle⟩ := mem_prefixFam.mp hy
        have : (σ v).val ≤ i := by simpa using hle
        omega
    · rintro ⟨⟨hyU, x, hx, hxy⟩, hyP⟩
      have hyV : y ∈ (range d).powerset := mem_powerset.mpr hyU
      refine ⟨⟨y, hyV⟩, ?_, rfl⟩
      rw [mem_activeSuffix_iff]
      obtain ⟨hxV, hxle⟩ := mem_prefixFam.mp hx
      refine ⟨?_, ⟨x, hxV⟩, by rw [mem_prefixSet_iff]; exact hxle, ?_⟩
      · by_contra hle
        exact hyP (mem_prefixFam.mpr ⟨hyV, by omega⟩)
      · rcases hxy with rfl | hxy
        · exact absurd hx hyP
        · exact hxy
  unfold vertexSepAt
  rw [← card_map (Function.Embedding.subtype _), hmap,
    card_sdiff_of_subset (subset_nbhd (prefixFam_subset σ i))]

/-! ### Lower bound -/

/-- **Every layout of `Q_d` has vertex separation at least `harperSum d`.** -/
theorem harperSum_le_vertexSepOfLayout {d : ℕ} (σ : LinearLayout (CubeV d)) :
    harperSum d ≤ vertexSepOfLayout (cubeGraph d) σ := by
  obtain ⟨T, hT, hT0, -, -, hbd⟩ := exists_init_profile d
  have hk1 : 1 ≤ T.card := card_pos.mpr ⟨_, hT0⟩
  have hkN : T.card ≤ Fintype.card (CubeV d) := by
    rw [Fintype.card_coe]; exact card_le_card hT.subset
  have hi : T.card - 1 < Fintype.card (CubeV d) := by omega
  have hcardP : (prefixFam σ (T.card - 1)).card = T.card := by
    rw [card_prefixFam, card_prefixSet σ hi]; omega
  have hH := harper (prefixFam_subset σ (T.card - 1)) hT hcardP.symm
  calc harperSum d ≤ vertexSepAt (cubeGraph d) σ (T.card - 1) := by
        rw [vertexSepAt_cubeGraph, hcardP]; omega
    _ = vertexSepAt (cubeGraph d) σ (⟨T.card - 1, hi⟩ : Fin _).val := rfl
    _ ≤ vertexSepOfLayout (cubeGraph d) σ := vertexSepAt_le_vertexSepOfLayout _ σ _

/-! ### Upper bound: the simplicial layout -/

/-- The position of a vertex in the simplicial order. -/
noncomputable def simplicialPos {d : ℕ} (v : CubeV d) : ℕ :=
  (univ.filter (fun u : CubeV d => key u.1 < key v.1)).card

theorem simplicialPos_le {d : ℕ} {u v : CubeV d} (h : key u.1 ≤ key v.1) :
    simplicialPos u ≤ simplicialPos v := by
  apply card_le_card
  intro w hw
  simp only [mem_filter, mem_univ, true_and] at hw ⊢
  exact hw.trans_le h

theorem simplicialPos_lt {d : ℕ} {u v : CubeV d} (h : key u.1 < key v.1) :
    simplicialPos u < simplicialPos v := by
  apply card_lt_card
  rw [ssubset_iff_of_subset]
  · exact ⟨u, by simp [h], by simp⟩
  · intro w hw
    simp only [mem_filter, mem_univ, true_and] at hw ⊢
    exact hw.trans h

theorem simplicialPos_lt_card {d : ℕ} (v : CubeV d) :
    simplicialPos v < Fintype.card (CubeV d) := by
  unfold simplicialPos
  rw [← card_univ]
  apply card_lt_card
  rw [ssubset_iff_of_subset (filter_subset _ _)]
  exact ⟨v, mem_univ _, by simp⟩

theorem simplicialPos_injective {d : ℕ} :
    Function.Injective (fun v : CubeV d => (⟨simplicialPos v, simplicialPos_lt_card v⟩ :
      Fin (Fintype.card (CubeV d)))) := by
  intro u v h
  simp only [Fin.mk.injEq] at h
  rcases lt_trichotomy (key u.1) (key v.1) with hlt | heq | hgt
  · exact absurd h (simplicialPos_lt hlt).ne
  · exact Subtype.ext (key_injective heq)
  · exact absurd h (simplicialPos_lt hgt).ne'

/-- The layout of `Q_d` along the simplicial order. -/
noncomputable def simplicialLayout (d : ℕ) : LinearLayout (CubeV d) :=
  Equiv.ofBijective _ ((Fintype.bijective_iff_injective_and_card _).mpr
    ⟨simplicialPos_injective, by simp⟩)

theorem simplicialLayout_val {d : ℕ} (v : CubeV d) :
    (simplicialLayout d v).val = simplicialPos v := rfl

theorem isInit_prefixFam_simplicial (d i : ℕ) :
    IsInit (range d) (prefixFam (simplicialLayout d) i) := by
  refine ⟨prefixFam_subset _ i, fun x hx y hy hle => ?_⟩
  obtain ⟨hxV, hxi⟩ := mem_prefixFam.mp hx
  refine mem_prefixFam.mpr ⟨hy, ?_⟩
  rw [simplicialLayout_val] at hxi ⊢
  exact (simplicialPos_le (u := ⟨y, hy⟩) (v := ⟨x, hxV⟩) hle).trans hxi

/-- **The simplicial layout has vertex separation at most `harperSum d`.** -/
theorem vertexSepOfLayout_simplicial_le (d : ℕ) :
    vertexSepOfLayout (cubeGraph d) (simplicialLayout d) ≤ harperSum d := by
  unfold vertexSepOfLayout
  split_ifs with h
  · exact Nat.zero_le _
  · apply Finset.sup'_le
    intro j _
    rw [vertexSepAt_cubeGraph]
    have := card_nbhd_init_le d _ (isInit_prefixFam_simplicial d j.val)
    omega

/-! ### The theorem -/

/-- **The pathwidth of `Q_d` is `Σ_{i < d} C(i, ⌊i/2⌋)`**, on the subsets of `range d`. -/
theorem pathwidth_cubeGraph (d : ℕ) : pathwidth (cubeGraph d) = harperSum d := by
  rw [← vertexSeparation_eq_pathwidth]
  apply le_antisymm
  · exact (vertexSeparation_le_vertexSepOfLayout _ (simplicialLayout d)).trans
      (vertexSepOfLayout_simplicial_le d)
  · unfold vertexSeparation
    apply le_csInf
    · exact ⟨_, ⟨Fintype.equivFin _, rfl⟩⟩
    · rintro b ⟨σ, rfl⟩
      exact harperSum_le_vertexSepOfLayout σ

/-! ### The hypercube on `Finset (Fin d)` -/

/-- The `d`-dimensional hypercube: subsets of `Fin d`, adjacent when they differ in
exactly one element. -/
def hypercube (d : ℕ) : SimpleGraph (Finset (Fin d)) where
  Adj x y := (x ∆ y).card = 1
  symm := ⟨fun x y (h : (x ∆ y).card = 1) => show (y ∆ x).card = 1 by rwa [symmDiff_comm]⟩
  loopless := ⟨fun x (h : (x ∆ x).card = 1) => by simp at h⟩

theorem Hypercube.adj_iff_card_symmDiff {a b : Finset ℕ} : Hypercube.Adj a b ↔ (a ∆ b).card = 1 := by
  constructor
  · rintro ⟨j, rfl⟩
    rw [symmDiff_symmDiff_cancel_left, card_singleton]
  · intro h
    obtain ⟨j, hj⟩ := card_eq_one.mp h
    exact ⟨j, by rw [← hj, symmDiff_symmDiff_cancel_left]⟩

/-- `Q_d` on `Finset (Fin d)` is `Q_d` on the subsets of `range d`. -/
def hypercubeIsoCubeGraph (d : ℕ) : hypercube d ≃g cubeGraph d where
  toFun x := ⟨x.map Fin.valEmbedding, mem_powerset.mpr (by
    intro a ha
    rw [mem_map] at ha
    obtain ⟨b, -, rfl⟩ := ha
    exact mem_range.mpr b.isLt)⟩
  invFun y := univ.filter (fun i : Fin d => i.val ∈ y.1)
  left_inv x := by
    ext i
    simp [Fin.val_inj]
  right_inv y := by
    apply Subtype.ext
    ext a
    simp only [mem_map, mem_filter, mem_univ, true_and, Fin.valEmbedding_apply]
    constructor
    · rintro ⟨i, hi, rfl⟩; exact hi
    · intro ha
      have := mem_range.mp (mem_powerset.mp y.2 ha)
      exact ⟨⟨a, this⟩, ha, rfl⟩
  map_rel_iff' {x y} := by
    simp only [Equiv.coe_fn_mk, cubeGraph_adj, Hypercube.adj_iff_card_symmDiff]
    change (x.map Fin.valEmbedding ∆ y.map Fin.valEmbedding).card = 1 ↔ (x ∆ y).card = 1
    have : x.map Fin.valEmbedding ∆ y.map Fin.valEmbedding = (x ∆ y).map Fin.valEmbedding := by
      ext a
      simp only [mem_symmDiff, mem_map, Fin.valEmbedding_apply]
      constructor
      · rintro (⟨⟨i, hi, rfl⟩, hn⟩ | ⟨⟨i, hi, rfl⟩, hn⟩)
        · exact ⟨i, Or.inl ⟨hi, fun h => hn ⟨i, h, rfl⟩⟩, rfl⟩
        · exact ⟨i, Or.inr ⟨hi, fun h => hn ⟨i, h, rfl⟩⟩, rfl⟩
      · rintro ⟨i, hi | hi, rfl⟩
        · refine Or.inl ⟨⟨i, hi.1, rfl⟩, ?_⟩
          rintro ⟨j, hj, hji⟩
          exact hi.2 (Fin.ext hji ▸ hj)
        · refine Or.inr ⟨⟨i, hi.1, rfl⟩, ?_⟩
          rintro ⟨j, hj, hji⟩
          exact hi.2 (Fin.ext hji ▸ hj)
    rw [this, card_map]

/-- **The pathwidth of the hypercube** (Chandran & Kavitha 2006, Theorem 2):
`pw(Q_d) = Σ_{i < d} C(i, ⌊i/2⌋)` for every `d` (OEIS A036256). -/
theorem pathwidth_hypercube (d : ℕ) :
    pathwidth (hypercube d) = ∑ i ∈ range d, i.choose (i / 2) := by
  rw [pathwidth_eq_of_iso (hypercubeIsoCubeGraph d), pathwidth_cubeGraph]
  rfl

end MOSPFormalization
