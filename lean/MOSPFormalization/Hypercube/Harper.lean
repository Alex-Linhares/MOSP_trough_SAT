/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Harper's vertex-isoperimetric theorem

**Theorem (Harper 1966).** Among all `k`-subsets of the cube `Q_U`, an initial
segment of the simplicial order has the smallest closed neighbourhood.

The proof is the compression proof (Harper; Bollobás, *Combinatorics*, §16;
Leader's lecture notes), by induction on `|U|`:

1. *Compression* (`exists_compress`). Replace both `i`-sections of `S` by the
   initial segments of `Q_{U - i}` of the same sizes. By induction and because
   neighbourhoods of initial segments are nested initial segments
   (`isInit_nbhd`, `IsInit.total`), `|N(S)|` does not increase; and the sum of
   the positions of the members strictly decreases unless `S` was already
   `i`-compressed (`sum_le_of_downClosed`).
2. *Extremal choice* (`harper_aux`). Among the `k`-sets with neighbourhood at
   most `|N(S₀)|` take one of least position sum: it is `i`-compressed for every
   `i`.
3. *Compressed sets* (`card_nbhd_le_of_compressed`). A set compressed in every
   direction is an initial segment, or is `D ∪ {y}` with `D` the elements below
   `x`, `y = U \ x` the immediate successor of `x`; then either the least
   element of `U` lies in `x` and the neighbourhood of `D ∪ {x}` is that of `D`,
   or `|U| ≤ 2` and `N(S)` is the whole cube.
-/

import MOSPFormalization.Hypercube.Order

set_option linter.unusedSectionVars false

namespace MOSPFormalization.Hypercube

open Finset

/-- The position of `z` in the simplicial order of `Q_U`. -/
noncomputable def rank (U : Finset ℕ) (z : Finset ℕ) : ℕ :=
  (U.powerset.filter (fun w => key w < key z)).card

theorem rank_lt_rank {U z z' : Finset ℕ} (hz : z ⊆ U) (h : key z < key z') :
    rank U z < rank U z' := by
  unfold rank
  apply card_lt_card
  rw [ssubset_iff_of_subset]
  · exact ⟨z, by simp [hz, h], by simp⟩
  · intro w hw
    simp only [mem_filter] at hw ⊢
    exact ⟨hw.1, hw.2.trans h⟩

/-- `S` is `i`-compressed: both its `i`-sections are initial segments. -/
def Compressed (U : Finset ℕ) (i : ℕ) (S : Finset (Finset ℕ)) : Prop :=
  IsInit (U.erase i) (lowerSec i S) ∧ IsInit (U.erase i) (upperSec i S)

/-- **The compression step.** -/
theorem exists_compress {U : Finset ℕ} {i : ℕ} (hi : i ∈ U)
    (IH : ∀ S' : Finset (Finset ℕ), S' ⊆ (U.erase i).powerset → ∀ C', IsInit (U.erase i) C' →
      C'.card = S'.card → (nbhd (U.erase i) C').card ≤ (nbhd (U.erase i) S').card)
    {S : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) (hnot : ¬ Compressed U i S) :
    ∃ T, T ⊆ U.powerset ∧ T.card = S.card ∧ (nbhd U T).card ≤ (nbhd U S).card ∧
      ∑ x ∈ T, rank U x < ∑ x ∈ S, rank U x := by
  set U' := U.erase i
  set A := lowerSec i S
  set B := upperSec i S
  have hA : A ⊆ U'.powerset := lowerSec_subset hS
  have hB : B ⊆ U'.powerset := upperSec_subset hS
  obtain ⟨Ca, hCa, hCac⟩ := exists_isInit_card hA
  obtain ⟨Cb, hCb, hCbc⟩ := exists_isInit_card hB
  have avA : ∀ x ∈ A, i ∉ x := fun x hx => notMem_of_mem_erase_powerset (hA hx)
  have avB : ∀ x ∈ B, i ∉ x := fun x hx => notMem_of_mem_erase_powerset (hB hx)
  have avCa : ∀ x ∈ Ca, i ∉ x := fun x hx => notMem_of_mem_erase_powerset (hCa.subset hx)
  have avCb : ∀ x ∈ Cb, i ∉ x := fun x hx => notMem_of_mem_erase_powerset (hCb.subset hx)
  have hTsub : glue i Ca Cb ⊆ U.powerset := glue_subset hi hCa.subset hCb.subset
  refine ⟨glue i Ca Cb, hTsub, ?_, ?_, ?_⟩
  · rw [card_glue avCa avCb, hCac, hCbc, ← card_sec]
  · have hS2 : (nbhd U S).card = (nbhd U' A ∪ B).card + (nbhd U' B ∪ A).card :=
      card_nbhd_sec hi hS
    rw [hS2, card_nbhd_sec hi hTsub, lowerSec_glue avCa, upperSec_glue avCa avCb,
      (isInit_nbhd hCa).card_union hCb, (isInit_nbhd hCb).card_union hCa]
    have h1 := IH A hA Ca hCa hCac
    have h2 := IH B hB Cb hCb hCbc
    have e1 : max (nbhd U' Ca).card Cb.card ≤ (nbhd U' A ∪ B).card :=
      max_le (h1.trans (card_le_card subset_union_left))
        (hCbc ▸ card_le_card subset_union_right)
    have e2 : max (nbhd U' Cb).card Ca.card ≤ (nbhd U' B ∪ A).card :=
      max_le (h2.trans (card_le_card subset_union_left))
        (hCac ▸ card_le_card subset_union_right)
    omega
  · have hSeq : S = glue i A B := (glue_sec i S).symm
    rw [sum_glue avCa avCb]
    conv_rhs => rw [hSeq, sum_glue avA avB]
    have hmono1 : ∀ a ∈ U'.powerset, ∀ b ∈ U'.powerset, key a < key b → rank U a < rank U b :=
      fun a ha b _ hab => rank_lt_rank ((mem_powerset.mp ha).trans (erase_subset _ _)) hab
    have hmono2 : ∀ a ∈ U'.powerset, ∀ b ∈ U'.powerset, key a < key b →
        rank U (insert i a) < rank U (insert i b) := by
      intro a ha b hb hab
      apply rank_lt_rank (insert_subset hi ((mem_powerset.mp ha).trans (erase_subset _ _)))
      exact (key_insert_lt_insert (notMem_of_mem_erase_powerset ha)
        (notMem_of_mem_erase_powerset hb)).mpr hab
    obtain ⟨g1, g1'⟩ := sum_le_of_downClosed (rank U) U'.powerset hmono1 Ca hCa.subset hCa.2 _ A hA
      hCac.symm rfl
    obtain ⟨g2, g2'⟩ := sum_le_of_downClosed (fun x => rank U (insert i x)) U'.powerset hmono2 Cb
      hCb.subset hCb.2 _ B hB hCbc.symm rfl
    by_contra hcon
    apply hnot
    have e1 : A = Ca := g1' (by omega)
    have e2 : B = Cb := g2' (by omega)
    constructor
    · have : lowerSec i S = Ca := e1
      rw [this]; exact hCa
    · have : upperSec i S = Cb := e2
      rw [this]; exact hCb

/-- In `Q_U` with `|U| ≤ 1`... the small cases: if every subset of `U` is in `S` or
adjacent to a member of `S`, then `N(S)` is the whole cube. -/
theorem card_nbhd_le_of_cover {U : Finset ℕ} {S C : Finset (Finset ℕ)}
    (hcov : ∀ w ⊆ U, ∃ x ∈ S, x = w ∨ Adj x w) : (nbhd U C).card ≤ (nbhd U S).card := by
  have : nbhd U S = U.powerset := by
    apply Subset.antisymm (nbhd_subset_powerset U S)
    intro w hw
    exact mem_nbhd.mpr ⟨mem_powerset.mp hw, hcov w (mem_powerset.mp hw)⟩
  rw [this]
  exact card_le_card (nbhd_subset_powerset U C)

/-- **A set compressed in every direction is optimal.** -/
theorem card_nbhd_le_of_compressed {U : Finset ℕ} {S : Finset (Finset ℕ)} (hSsub : S ⊆ U.powerset)
    (hcomp : ∀ i ∈ U, Compressed U i S) {C : Finset (Finset ℕ)} (hC : IsInit U C)
    (hcard : C.card = S.card) : (nbhd U C).card ≤ (nbhd U S).card := by
  by_cases hS : IsInit U S
  · rw [hC.eq_of_card_eq hS hcard]
  -- a misplaced pair is a pair of complements
  have pair : ∀ x y, x ⊆ U → x ∉ S → y ∈ S → key x < key y → x = U \ y := by
    intro x y hxU hxS hyS hlt
    have hiff : ∀ i ∈ U, (i ∈ x ↔ i ∉ y) := by
      intro i hi
      obtain ⟨hlo, hup⟩ := hcomp i hi
      constructor
      · intro hix hiy
        have h1 : y.erase i ∈ upperSec i S :=
          mem_upperSec.mpr ⟨notMem_erase _ _, by rw [insert_erase hiy]; exact hyS⟩
        have h2 : key (x.erase i) ≤ key (y.erase i) := by
          rw [← key_insert_le_insert (notMem_erase i x) (notMem_erase i y), insert_erase hix,
            insert_erase hiy]
          exact hlt.le
        have h3 := hup.mem_of_le h1
          (subset_erase.mpr ⟨(erase_subset _ _).trans hxU, notMem_erase _ _⟩) h2
        rw [mem_upperSec, insert_erase hix] at h3
        exact hxS h3.2
      · intro hiy
        by_contra hix
        have h1 : y ∈ lowerSec i S := mem_lowerSec.mpr ⟨hyS, hiy⟩
        have h3 := hlo.mem_of_le h1 (subset_erase.mpr ⟨hxU, hix⟩) hlt.le
        exact hxS (mem_lowerSec.mp h3).1
    ext a
    rw [mem_sdiff]
    constructor
    · intro ha; exact ⟨hxU ha, (hiff a (hxU ha)).mp ha⟩
    · rintro ⟨haU, hay⟩; exact (hiff a haU).mpr hay
  -- the first missing element `x0` and the last present element `y0`
  have hS' : ∃ y ∈ S, ∃ x ∈ U.powerset, key x ≤ key y ∧ x ∉ S := by
    by_contra hcon
    push Not at hcon
    exact hS ⟨hSsub, hcon⟩
  obtain ⟨y1, hy1S, x1, hx1U, hle1, hx1S⟩ := hS'
  obtain ⟨x0, hx0, hx0min⟩ := exists_min_image (U.powerset \ S) key
    ⟨x1, mem_sdiff.mpr ⟨hx1U, hx1S⟩⟩
  obtain ⟨y0, hy0S, hy0max⟩ := exists_max_image S key ⟨y1, hy1S⟩
  rw [mem_sdiff] at hx0
  have hx0U : x0 ⊆ U := mem_powerset.mp hx0.1
  have hy0U : y0 ⊆ U := mem_powerset.mp (hSsub hy0S)
  have hlt1 : key x1 < key y1 :=
    lt_of_le_of_ne hle1 (fun h => hx1S (key_injective h ▸ hy1S))
  have hx0y0 : key x0 < key y0 :=
    ((hx0min x1 (mem_sdiff.mpr ⟨hx1U, hx1S⟩)).trans_lt hlt1).trans_le (hy0max y1 hy1S)
  have hxy : x0 = U \ y0 := pair x0 y0 hx0U hx0.2 hy0S hx0y0
  have hyx : y0 = U \ x0 := by rw [hxy, Finset.sdiff_sdiff_eq_self hy0U]
  -- the elements before `x0`
  set D := U.powerset.filter (fun z => key z < key x0) with hDdef
  have hmemD : ∀ {z}, z ∈ D ↔ z ⊆ U ∧ key z < key x0 := by
    intro z; rw [hDdef, mem_filter, mem_powerset]
  have hDS : D ⊆ S := by
    intro z hz
    rw [hmemD] at hz
    by_contra hzS
    exact absurd (hx0min z (mem_sdiff.mpr ⟨mem_powerset.mpr hz.1, hzS⟩)) (not_le.mpr hz.2)
  have hgt : ∀ z ∈ S, key x0 < key z → z = y0 := by
    intro z hz hlt
    have := pair x0 z hx0U hx0.2 hz hlt
    rw [hyx, this, Finset.sdiff_sdiff_eq_self (mem_powerset.mp (hSsub hz))]
  have hSeq : S = insert y0 D := by
    ext z
    rw [mem_insert]
    constructor
    · intro hz
      by_cases hlt : key z < key x0
      · exact Or.inr (hmemD.mpr ⟨mem_powerset.mp (hSsub hz), hlt⟩)
      · left
        apply hgt z hz
        exact lt_of_le_of_ne (not_lt.mp hlt) (fun h => hx0.2 (key_injective h ▸ hz))
    · rintro (rfl | hz)
      · exact hy0S
      · exact hDS hz
  have hbetween : ∀ z ⊆ U, key x0 < key z → key z < key y0 → False := by
    intro z hzU h1 h2
    by_cases hzS : z ∈ S
    · rw [hgt z hzS h1] at h2; exact lt_irrefl _ h2
    · have := pair z y0 hzU hzS hy0S h2
      rw [← hxy] at this
      rw [this] at h1; exact lt_irrefl _ h1
  -- `D` and `D ∪ {x0}` are initial segments; the latter is `C`
  have hDinit : IsInit U D := by
    refine ⟨filter_subset _ _, fun x hx y hy hle => ?_⟩
    rw [hmemD] at hx ⊢
    exact ⟨mem_powerset.mp hy, hle.trans_lt hx.2⟩
  have hy0D : y0 ∉ D := fun h => absurd (hmemD.mp h).2 (not_lt.mpr hx0y0.le)
  have hx0D : x0 ∉ D := fun h => lt_irrefl _ (hmemD.mp h).2
  have hC'init : IsInit U (insert x0 D) := by
    refine ⟨insert_subset hx0.1 hDinit.subset, fun x hx y hy hle => ?_⟩
    rw [mem_insert] at hx ⊢
    rcases lt_or_eq_of_le hle with hlt | heq
    · right
      refine hmemD.mpr ⟨mem_powerset.mp hy, ?_⟩
      rcases hx with rfl | hx
      · exact hlt
      · exact hlt.trans (hmemD.mp hx).2
    · rcases hx with rfl | hx
      · exact Or.inl (key_injective heq)
      · exact Or.inr (key_injective heq ▸ hx)
  have hCeq : C = insert x0 D := by
    apply hC.eq_of_card_eq hC'init
    rw [hcard, hSeq, card_insert_of_notMem hy0D, card_insert_of_notMem hx0D]
  rw [hCeq]
  have hUne : U.Nonempty := by
    rw [nonempty_iff_ne_empty]
    rintro rfl
    have h1 : x0 = ∅ := subset_empty.mp hx0U
    have h2 : y0 = ∅ := subset_empty.mp hy0U
    rw [h1, h2] at hx0y0; exact lt_irrefl _ hx0y0
  set u0 := U.min' hUne
  have hu0U : u0 ∈ U := min'_mem _ _
  by_cases hu : u0 ∈ x0
  · -- Case A: the least element of `U` is in `x0`; nothing new is reached through `x0`
    apply card_le_card
    refine Subset.trans ?_ (nbhd_mono hDS)
    intro w hw
    have hwU := (mem_nbhd.mp hw).1
    rw [mem_nbhd_iff_low_mem hC'init hwU, mem_insert] at hw
    rw [mem_nbhd_iff_low_mem hDinit hwU]
    rcases hw with hw | hw
    · exfalso
      by_cases hwne : w.Nonempty
      · have hl : low w = w.erase (w.min' hwne) := by simp [low, hwne]
        rw [hl] at hw
        have hu' : u0 ∈ w.erase (w.min' hwne) := hw ▸ hu
        have hm : w.min' hwne ≤ u0 := min'_le _ _ (mem_of_mem_erase hu')
        have hm' : u0 ≤ w.min' hwne := min'_le _ _ (hwU (min'_mem _ _))
        exact (mem_erase.mp hu').1 (le_antisymm hm' hm)
      · have hl : low w = ∅ := by simp [low, hwne]
        rw [hl] at hw
        rw [← hw] at hu; simp at hu
    · exact hw
  · -- Case B: the least element of `U` is in `y0`; then `|U| ≤ 2`
    have hu0y : u0 ∈ y0 := by rw [hyx, mem_sdiff]; exact ⟨hu0U, hu⟩
    have hcardxy : x0.card ≤ y0.card := card_le_of_key_lt hx0y0
    by_cases hx0e : x0 = ∅
    · -- `x0 = ∅`, `y0 = U`, and `U` is a single point
      have hy0eq : y0 = U := by rw [hyx, hx0e, sdiff_empty]
      have hU1 : U.card = 1 := by
        by_contra hne
        have h2 : 1 < U.card := by have := card_pos.mpr hUne; omega
        apply hbetween {u0} (singleton_subset_iff.mpr hu0U)
        · rw [hx0e]; exact key_lt_of_card_lt (by simp)
        · rw [hy0eq]; exact key_lt_of_card_lt (by simpa using h2)
      obtain ⟨a, ha⟩ := card_eq_one.mp hU1
      apply card_nbhd_le_of_cover
      intro w hw
      rw [ha] at hw
      refine ⟨y0, hy0S, ?_⟩
      rw [hy0eq, ha]
      rcases subset_singleton_iff.mp hw with rfl | rfl
      · right
        have := adj_erase (mem_singleton_self a)
        rwa [erase_singleton] at this
      · left; rfl
    · have hx0ne : x0.Nonempty := nonempty_iff_ne_empty.mpr hx0e
      set M := U.max' hUne
      have hMU : M ∈ U := max'_mem _ _
      -- the candidate between `x0` and `y0`
      have mk : ∀ a ∈ x0, (x0.card < y0.card ∨ a ≠ M) → False := by
        intro a ha hor
        have hau0 : a ≠ u0 := fun h => hu (h ▸ ha)
        have hu0a : u0 < a := lt_of_le_of_ne (min'_le _ _ (hx0U ha)) hau0.symm
        set z := insert u0 (x0.erase a)
        have hu0z : u0 ∉ x0.erase a := fun h => hu (mem_of_mem_erase h)
        have hzc : z.card = x0.card := by
          rw [card_insert_of_notMem hu0z, card_erase_of_mem ha]
          have := card_pos.mpr hx0ne; omega
        have hzU : z ⊆ U := insert_subset hu0U ((erase_subset _ _).trans hx0U)
        apply hbetween z hzU
        · rw [key_lt_iff_of_card_eq hzc.symm]
          refine ⟨a, ha, ?_, ?_⟩
          · rw [mem_insert, mem_erase]; push Not; exact ⟨hau0, fun h => absurd rfl h⟩
          · intro b hb hbx
            rw [mem_insert, mem_erase] at hb
            rcases hb with rfl | ⟨-, hb⟩
            · exact hu0a
            · exact absurd hb hbx
        · by_cases hlt : x0.card < y0.card
          · exact key_lt_of_card_lt (hzc ▸ hlt)
          · have hceq : x0.card = y0.card := le_antisymm hcardxy (not_lt.mp hlt)
            have haM : a ≠ M := hor.resolve_left hlt
            have hMx : M ∈ x0 := by
              by_contra hMx
              obtain ⟨c, hc, -, hcmax⟩ := (key_lt_iff_of_card_eq hceq).mp hx0y0
              have hMy : M ∈ y0 := by rw [hyx, mem_sdiff]; exact ⟨hMU, hMx⟩
              have := hcmax M hMy hMx
              exact absurd (le_max' _ _ (hx0U hc)) (not_le.mpr this)
            rw [key_lt_iff_of_card_eq (hzc.trans hceq)]
            refine ⟨M, ?_, ?_, ?_⟩
            · rw [mem_insert, mem_erase]; exact Or.inr ⟨fun h => haM h.symm, hMx⟩
            · rw [hyx, mem_sdiff]; push Not; exact fun _ => hMx
            · intro b hb _
              have hbM : b ≠ M := by
                rintro rfl
                rw [hyx, mem_sdiff] at hb; exact hb.2 hMx
              exact lt_of_le_of_ne (le_max' _ _ (hy0U hb)) hbM
      -- so `x0 = {M}`, `y0 = {u0}`, `U = {u0, M}`
      have hcardeq : x0.card = y0.card := by
        by_contra hne
        obtain ⟨a, ha⟩ := hx0ne
        exact mk a ha (Or.inl (lt_of_le_of_ne hcardxy hne))
      have hx0M : x0 = {M} := by
        obtain ⟨a, ha⟩ := hx0ne
        rw [eq_singleton_iff_unique_mem]
        refine ⟨?_, fun b hb => ?_⟩
        · by_contra hMx
          exact mk a ha (Or.inr (fun h => hMx (h ▸ ha)))
        · by_contra hbM
          exact mk b hb (Or.inr hbM)
      have hy0c : y0.card = 1 := by rw [← hcardeq, hx0M, card_singleton]
      have hy0u : y0 = {u0} := by
        obtain ⟨b, hb⟩ := card_eq_one.mp hy0c
        rw [hb] at hu0y ⊢
        rw [mem_singleton.mp hu0y]
      have hemD : ∅ ∈ D := hmemD.mpr ⟨empty_subset _, key_lt_of_card_lt (by rw [hx0M]; simp)⟩
      have hsmall : ∀ v ⊆ U \ {M}, v ∈ S := by
        intro v hv
        rw [← hx0M, ← hyx, hy0u] at hv
        rcases subset_singleton_iff.mp hv with rfl | rfl
        · exact hDS hemD
        · rw [← hy0u]; exact hy0S
      apply card_nbhd_le_of_cover
      intro w hw
      by_cases hMw : M ∈ w
      · refine ⟨w.erase M, hsmall _ ?_, Or.inr ?_⟩
        · intro b hb
          rw [mem_erase] at hb
          rw [mem_sdiff, mem_singleton]; exact ⟨hw hb.2, hb.1⟩
        · have := adj_insert (notMem_erase M w)
          rwa [insert_erase hMw] at this
      · refine ⟨w, hsmall _ ?_, Or.inl rfl⟩
        intro b hb
        rw [mem_sdiff, mem_singleton]; exact ⟨hw hb, fun h => hMw (h ▸ hb)⟩

/-- Harper's theorem, by induction on the size of the ground set. -/
theorem harper_aux : ∀ n, ∀ U : Finset ℕ, U.card = n → ∀ S, S ⊆ U.powerset → ∀ C, IsInit U C →
    C.card = S.card → (nbhd U C).card ≤ (nbhd U S).card := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro U hU S0 hS0 C hC hcard
    set F := U.powerset.powerset.filter
      (fun S => S.card = S0.card ∧ (nbhd U S).card ≤ (nbhd U S0).card) with hF
    have hS0F : S0 ∈ F := by rw [hF, mem_filter, mem_powerset]; exact ⟨hS0, rfl, le_rfl⟩
    obtain ⟨S, hSF, hmin⟩ := exists_min_image F (fun S => ∑ x ∈ S, rank U x) ⟨S0, hS0F⟩
    rw [hF, mem_filter, mem_powerset] at hSF
    obtain ⟨hSsub, hScard, hSnb⟩ := hSF
    have hcomp : ∀ i ∈ U, Compressed U i S := by
      intro i hi
      by_contra hnot
      have IH : ∀ S' : Finset (Finset ℕ), S' ⊆ (U.erase i).powerset → ∀ C',
          IsInit (U.erase i) C' → C'.card = S'.card →
          (nbhd (U.erase i) C').card ≤ (nbhd (U.erase i) S').card := by
        intro S' hS' C' hC' hc'
        refine ih (U.erase i).card ?_ (U.erase i) rfl S' hS' C' hC' hc'
        rw [card_erase_of_mem hi, hU]
        have := card_pos.mpr ⟨i, hi⟩; omega
      obtain ⟨T, hTsub, hTcard, hTnb, hTsum⟩ := exists_compress hi IH hSsub hnot
      have hTF : T ∈ F := by
        rw [hF, mem_filter, mem_powerset]
        exact ⟨hTsub, hTcard.trans hScard, hTnb.trans hSnb⟩
      exact absurd (hmin T hTF) (not_le.mpr hTsum)
    exact (card_nbhd_le_of_compressed hSsub hcomp hC (hcard.trans hScard.symm)).trans hSnb

/-- **Harper's vertex-isoperimetric theorem** (Harper 1966). In the cube `Q_U`, an
initial segment of the simplicial order has a closed neighbourhood no larger than
that of any family of the same size. -/
theorem harper {U : Finset ℕ} {S C : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) (hC : IsInit U C)
    (hcard : C.card = S.card) : (nbhd U C).card ≤ (nbhd U S).card :=
  harper_aux _ U rfl S hS C hC hcard

end MOSPFormalization.Hypercube
