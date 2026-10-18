/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The hypercube on finite sets of naturals: order, neighbourhoods, sections

The vertices of the cube `Q_U` are the subsets of a finite set `U ⊆ ℕ`; two are
adjacent when they differ in one element. Everything here is stated on
`Finset ℕ`, so that the cube on `U.erase i` (a *section* of `Q_U`) needs no
relabelling.

* `key` — the **simplicial order** (Harper 1966): by size, then, within a size,
  by reversed colex (`x` precedes `y` when the largest element of `x ∆ y` is in
  `x`). It is the order whose initial segments minimise the vertex boundary.
* `IsInit U C` — `C` is an initial segment of the simplicial order on `Q_U`.
* `nbhd U S` — the closed neighbourhood of `S` in `Q_U`.
* `lowerSec i S`, `upperSec i S` — the two `i`-sections of `S`, as families on
  `U.erase i`; `card_nbhd_sec` splits `|N(S)|` across them.
* `isInit_nbhd` — the closed neighbourhood of an initial segment is an initial
  segment.
-/

import Mathlib.Combinatorics.Colex
import Mathlib.Data.Prod.Lex
import Mathlib.Data.Finset.Powerset
import Mathlib.Algebra.Order.BigOperators.Group.Finset

set_option linter.unusedSectionVars false

namespace MOSPFormalization.Hypercube

open Finset Finset.Colex
open scoped symmDiff

/-! ### The simplicial order -/

/-- The simplicial key: size first, then reversed colex. -/
def key (x : Finset ℕ) : ℕ ×ₗ (Colex (Finset ℕ))ᵒᵈ :=
  toLex (x.card, OrderDual.toDual (toColex x))

theorem key_injective : Function.Injective key := by
  intro x y h
  simpa [key] using congrArg (fun p => OrderDual.ofDual (ofLex p).2) h

theorem key_inj {x y : Finset ℕ} : key x = key y ↔ x = y := key_injective.eq_iff

theorem key_lt_iff {x y : Finset ℕ} :
    key x < key y ↔ x.card < y.card ∨ (x.card = y.card ∧ toColex y < toColex x) := by
  unfold key
  rw [Prod.Lex.toLex_lt_toLex]
  simp

theorem key_le_iff {x y : Finset ℕ} :
    key x ≤ key y ↔ x.card < y.card ∨ (x.card = y.card ∧ toColex y ≤ toColex x) := by
  unfold key
  rw [Prod.Lex.toLex_le_toLex]
  simp

theorem key_lt_of_card_lt {x y : Finset ℕ} (h : x.card < y.card) : key x < key y :=
  key_lt_iff.mpr (Or.inl h)

theorem card_le_of_key_le {x y : Finset ℕ} (h : key x ≤ key y) : x.card ≤ y.card := by
  rcases key_le_iff.mp h with h | ⟨h, -⟩ <;> omega

theorem card_le_of_key_lt {x y : Finset ℕ} (h : key x < key y) : x.card ≤ y.card :=
  card_le_of_key_le h.le

theorem key_empty_le (y : Finset ℕ) : key ∅ ≤ key y := by
  rw [key_le_iff]
  rcases Nat.eq_zero_or_pos y.card with h | h
  · right; rw [card_eq_zero.mp h]; simp
  · left; simpa using h

/-- Within one size, `x` precedes `y` iff the largest element of `x ∆ y` is in `x`. -/
theorem key_lt_iff_of_card_eq {x y : Finset ℕ} (h : x.card = y.card) :
    key x < key y ↔ ∃ a ∈ x, a ∉ y ∧ ∀ b ∈ y, b ∉ x → b < a := by
  rw [key_lt_iff, ← toColex_lt_toColex_iff_exists_forall_lt]
  constructor
  · rintro (h' | ⟨-, h'⟩)
    · omega
    · exact h'
  · intro h'; exact Or.inr ⟨h, h'⟩

/-- Adding the same new element to both sets preserves the order. -/
theorem key_insert_lt_insert {i : ℕ} {x y : Finset ℕ} (hx : i ∉ x) (hy : i ∉ y) :
    key (insert i x) < key (insert i y) ↔ key x < key y := by
  have hc : toColex (insert i y) < toColex (insert i x) ↔ toColex y < toColex x := by
    have := toColex_sdiff_lt_toColex_sdiff (u := {i}) (s := insert i y) (t := insert i x)
      (by simp) (by simp)
    rw [← this]
    rw [insert_sdiff_of_mem _ (mem_singleton_self i), insert_sdiff_of_mem _ (mem_singleton_self i),
      sdiff_singleton_eq_erase, sdiff_singleton_eq_erase, erase_eq_of_notMem hx,
      erase_eq_of_notMem hy]
  rw [key_lt_iff, key_lt_iff, card_insert_of_notMem hx, card_insert_of_notMem hy, hc]
  simp only [Nat.add_lt_add_iff_right, Nat.add_right_cancel_iff]

theorem key_insert_le_insert {i : ℕ} {x y : Finset ℕ} (hx : i ∉ x) (hy : i ∉ y) :
    key (insert i x) ≤ key (insert i y) ↔ key x ≤ key y := by
  rw [le_iff_lt_or_eq, le_iff_lt_or_eq, key_insert_lt_insert hx hy, key_inj, key_inj]
  constructor
  · rintro (h | h)
    · exact Or.inl h
    · right
      have := congrArg (fun s => s.erase i) h
      simpa [erase_insert hx, erase_insert hy] using this
  · rintro (h | h)
    · exact Or.inl h
    · right; rw [h]

/-! ### Initial segments -/

/-- `C` is an initial segment of the simplicial order on the cube `Q_U`. -/
def IsInit (U : Finset ℕ) (C : Finset (Finset ℕ)) : Prop :=
  C ⊆ U.powerset ∧ ∀ x ∈ C, ∀ y ∈ U.powerset, key y ≤ key x → y ∈ C

theorem IsInit.subset {U : Finset ℕ} {C : Finset (Finset ℕ)} (h : IsInit U C) :
    C ⊆ U.powerset := h.1

theorem IsInit.mem_of_le {U : Finset ℕ} {C : Finset (Finset ℕ)} (h : IsInit U C)
    {x y : Finset ℕ} (hx : x ∈ C) (hy : y ⊆ U) (hle : key y ≤ key x) : y ∈ C :=
  h.2 x hx y (mem_powerset.mpr hy) hle

theorem isInit_empty (U : Finset ℕ) : IsInit U ∅ := ⟨by simp, by simp⟩

theorem isInit_powerset (U : Finset ℕ) : IsInit U U.powerset :=
  ⟨subset_rfl, fun _ _ y hy _ => hy⟩

theorem IsInit.empty_mem {U : Finset ℕ} {C : Finset (Finset ℕ)} (h : IsInit U C)
    (hne : C.Nonempty) : ∅ ∈ C := by
  obtain ⟨x, hx⟩ := hne
  exact h.mem_of_le hx (empty_subset _) (key_empty_le x)

/-- Two initial segments are nested. -/
theorem IsInit.total {U : Finset ℕ} {C D : Finset (Finset ℕ)} (hC : IsInit U C)
    (hD : IsInit U D) : C ⊆ D ∨ D ⊆ C := by
  by_contra hcon
  rw [not_or, not_subset, not_subset] at hcon
  obtain ⟨⟨c, hcC, hcD⟩, ⟨d, hdD, hdC⟩⟩ := hcon
  rcases le_total (key c) (key d) with h | h
  · exact hcD (hD.mem_of_le hdD (mem_powerset.mp (hC.subset hcC)) h)
  · exact hdC (hC.mem_of_le hcC (mem_powerset.mp (hD.subset hdD)) h)

theorem IsInit.eq_of_card_eq {U : Finset ℕ} {C D : Finset (Finset ℕ)} (hC : IsInit U C)
    (hD : IsInit U D) (hcard : C.card = D.card) : C = D := by
  rcases hC.total hD with h | h
  · exact eq_of_subset_of_card_le h hcard.ge
  · exact (eq_of_subset_of_card_le h hcard.le).symm

theorem IsInit.card_union {U : Finset ℕ} {C D : Finset (Finset ℕ)} (hC : IsInit U C)
    (hD : IsInit U D) : (C ∪ D).card = max C.card D.card := by
  rcases hC.total hD with h | h
  · rw [union_eq_right.mpr h, max_eq_right (card_le_card h)]
  · rw [union_eq_left.mpr h, max_eq_left (card_le_card h)]

/-- An initial segment of every size exists. -/
theorem exists_isInit (U : Finset ℕ) :
    ∀ k, k ≤ U.powerset.card → ∃ C, IsInit U C ∧ C.card = k := by
  intro k
  induction k with
  | zero => intro _; exact ⟨∅, isInit_empty U, rfl⟩
  | succ k ih =>
    intro hk
    obtain ⟨C, hC, hcard⟩ := ih (by omega)
    have hne : (U.powerset \ C).Nonempty := by
      rw [nonempty_iff_ne_empty]
      intro h
      rw [sdiff_eq_empty_iff_subset] at h
      have := card_le_card h
      omega
    obtain ⟨m, hm, hmin⟩ := exists_min_image _ key hne
    rw [mem_sdiff] at hm
    refine ⟨insert m C, ⟨?_, ?_⟩, by rw [card_insert_of_notMem hm.2, hcard]⟩
    · exact insert_subset hm.1 hC.subset
    · intro x hx y hy hle
      rw [mem_insert] at hx ⊢
      by_cases hyC : y ∈ C
      · exact Or.inr hyC
      left
      have h1 : key m ≤ key y := hmin y (mem_sdiff.mpr ⟨hy, hyC⟩)
      rcases hx with rfl | hx
      · exact key_injective (le_antisymm hle h1)
      · exact absurd (hC.2 x hx y hy hle) hyC

/-- An initial segment of the same size as a given family. -/
theorem exists_isInit_card {U : Finset ℕ} {S : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) :
    ∃ C, IsInit U C ∧ C.card = S.card :=
  exists_isInit U S.card (card_le_card hS)

/-! ### Adjacency and closed neighbourhoods -/

/-- Two sets are adjacent in the cube when they differ in exactly one element. -/
def Adj (x y : Finset ℕ) : Prop := ∃ j, y = x ∆ {j}

theorem Adj.symm {x y : Finset ℕ} (h : Adj x y) : Adj y x := by
  obtain ⟨j, rfl⟩ := h
  exact ⟨j, by rw [symmDiff_symmDiff_cancel_right]⟩

theorem mem_symmDiff_singleton {x : Finset ℕ} {j a : ℕ} :
    a ∈ x ∆ {j} ↔ (a ∈ x ∧ a ≠ j) ∨ (a ∉ x ∧ a = j) := by
  rw [mem_symmDiff, mem_singleton]; tauto

theorem symmDiff_singleton_of_mem {x : Finset ℕ} {j : ℕ} (h : j ∈ x) : x ∆ {j} = x.erase j := by
  ext a; rw [mem_symmDiff_singleton, mem_erase]
  constructor
  · rintro (⟨h1, h2⟩ | ⟨h1, rfl⟩)
    · exact ⟨h2, h1⟩
    · exact absurd h h1
  · rintro ⟨h1, h2⟩; exact Or.inl ⟨h2, h1⟩

theorem symmDiff_singleton_of_notMem {x : Finset ℕ} {j : ℕ} (h : j ∉ x) :
    x ∆ {j} = insert j x := by
  ext a; rw [mem_symmDiff_singleton, mem_insert]
  constructor
  · rintro (⟨h1, -⟩ | ⟨-, rfl⟩)
    · exact Or.inr h1
    · exact Or.inl rfl
  · rintro (rfl | h1)
    · exact Or.inr ⟨h, rfl⟩
    · exact Or.inl ⟨h1, fun h' => h (h' ▸ h1)⟩

theorem adj_erase {x : Finset ℕ} {j : ℕ} (h : j ∈ x) : Adj x (x.erase j) :=
  ⟨j, (symmDiff_singleton_of_mem h).symm⟩

theorem adj_insert {x : Finset ℕ} {j : ℕ} (h : j ∉ x) : Adj x (insert j x) :=
  ⟨j, (symmDiff_singleton_of_notMem h).symm⟩

theorem Adj.ne {x y : Finset ℕ} (h : Adj x y) : x ≠ y := by
  obtain ⟨j, rfl⟩ := h
  intro h'
  by_cases hj : j ∈ x
  · have : j ∈ x ∆ {j} := h' ▸ hj
    rw [mem_symmDiff_singleton] at this; tauto
  · have : j ∈ x ∆ {j} := by rw [mem_symmDiff_singleton]; tauto
    exact hj (h' ▸ this)

theorem Adj.card {x y : Finset ℕ} (h : Adj x y) :
    y.card + 1 = x.card ∨ x.card + 1 = y.card := by
  obtain ⟨j, rfl⟩ := h
  by_cases hj : j ∈ x
  · rw [symmDiff_singleton_of_mem hj]; left; exact card_erase_add_one hj
  · rw [symmDiff_singleton_of_notMem hj]; right; exact (card_insert_of_notMem hj).symm

theorem Adj.subset {U x y : Finset ℕ} (h : Adj x y) (hx : x ⊆ U) (hy : ∀ j, y = x ∆ {j} → j ∈ U) :
    y ⊆ U := by
  obtain ⟨j, rfl⟩ := id h
  intro a ha
  rw [mem_symmDiff_singleton] at ha
  rcases ha with ⟨ha, -⟩ | ⟨-, rfl⟩
  · exact hx ha
  · exact hy _ rfl

/-- The closed neighbourhood of `S` in the cube `Q_U`. -/
noncomputable def nbhd (U : Finset ℕ) (S : Finset (Finset ℕ)) : Finset (Finset ℕ) :=
  @Finset.filter _ (fun y => ∃ x ∈ S, x = y ∨ Adj x y) (Classical.decPred _) U.powerset

theorem mem_nbhd {U : Finset ℕ} {S : Finset (Finset ℕ)} {y : Finset ℕ} :
    y ∈ nbhd U S ↔ y ⊆ U ∧ ∃ x ∈ S, x = y ∨ Adj x y := by
  classical
  simp only [nbhd, Finset.mem_filter, mem_powerset]

theorem nbhd_subset_powerset (U : Finset ℕ) (S : Finset (Finset ℕ)) : nbhd U S ⊆ U.powerset :=
  fun y hy => mem_powerset.mpr (mem_nbhd.mp hy).1

theorem subset_nbhd {U : Finset ℕ} {S : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) :
    S ⊆ nbhd U S :=
  fun x hx => mem_nbhd.mpr ⟨mem_powerset.mp (hS hx), x, hx, Or.inl rfl⟩

theorem nbhd_mono {U : Finset ℕ} {S T : Finset (Finset ℕ)} (h : S ⊆ T) : nbhd U S ⊆ nbhd U T := by
  intro y hy
  obtain ⟨hyU, x, hx, hxy⟩ := mem_nbhd.mp hy
  exact mem_nbhd.mpr ⟨hyU, x, h hx, hxy⟩

theorem nbhd_empty (U : Finset ℕ) : nbhd U ∅ = ∅ := by
  ext y; simp [mem_nbhd]

/-! ### The lowest neighbour -/

/-- The first vertex of the closed neighbourhood of `z` in the simplicial order:
`z` without its least element (`∅` for `∅`). -/
noncomputable def low (z : Finset ℕ) : Finset ℕ :=
  if h : z.Nonempty then z.erase (z.min' h) else ∅

theorem low_subset (z : Finset ℕ) : low z ⊆ z := by
  unfold low; split_ifs
  · exact erase_subset _ _
  · exact empty_subset _

theorem low_eq_or_adj (z : Finset ℕ) : low z = z ∨ Adj z (low z) := by
  unfold low; split_ifs with h
  · exact Or.inr (adj_erase (min'_mem _ _))
  · left; exact (not_nonempty_iff_eq_empty.mp h).symm

/-- `low z` precedes everything in the closed neighbourhood of `z`. -/
theorem key_low_le {z w : Finset ℕ} (hw : w = z ∨ Adj z w) : key (low z) ≤ key w := by
  by_cases hz : z.Nonempty
  · have hl : low z = z.erase (z.min' hz) := by simp [low, hz]
    have hcl : (low z).card + 1 = z.card := by rw [hl]; exact card_erase_add_one (min'_mem _ _)
    rcases hw with rfl | ⟨j, rfl⟩
    · exact (key_lt_of_card_lt (by omega)).le
    · by_cases hj : j ∈ z
      · rw [symmDiff_singleton_of_mem hj, hl, key_le_iff]
        right
        refine ⟨by rw [card_erase_of_mem (min'_mem _ _), card_erase_of_mem hj], ?_⟩
        exact (erase_le_erase hj (min'_mem _ _)).mpr (min'_le _ _ hj)
      · rw [symmDiff_singleton_of_notMem hj]
        apply (key_lt_of_card_lt _).le
        rw [card_insert_of_notMem hj]; omega
  · have : low z = ∅ := by simp [low, hz]
    rw [this]; exact key_empty_le w

/-- `low` is monotone for the simplicial order. -/
theorem key_low_mono {z y : Finset ℕ} (h : key z ≤ key y) : key (low z) ≤ key (low y) := by
  by_cases hz : z.Nonempty
  · have hy : y.Nonempty := by
      rw [← card_pos] at hz ⊢; exact hz.trans_le (card_le_of_key_le h)
    have hlz : low z = z.erase (z.min' hz) := by simp [low, hz]
    have hly : low y = y.erase (y.min' hy) := by simp [low, hy]
    rw [hlz, hly]
    rcases key_le_iff.mp h with hc | ⟨hc, hcol⟩
    · apply (key_lt_of_card_lt _).le
      rw [card_erase_of_mem (min'_mem _ _), card_erase_of_mem (min'_mem _ _)]
      have := card_pos.mpr hz; omega
    · rw [key_le_iff]
      right
      refine ⟨by rw [card_erase_of_mem (min'_mem _ _), card_erase_of_mem (min'_mem _ _), hc], ?_⟩
      exact erase_le_erase_min' hcol hc.ge (min'_mem _ _)
  · have : low z = ∅ := by simp [low, hz]
    rw [this]; exact key_empty_le _

/-- For an initial segment `C`, `z ∈ N(C)` iff `low z ∈ C`. -/
theorem mem_nbhd_iff_low_mem {U : Finset ℕ} {C : Finset (Finset ℕ)} (hC : IsInit U C)
    {z : Finset ℕ} (hz : z ⊆ U) : z ∈ nbhd U C ↔ low z ∈ C := by
  constructor
  · intro h
    obtain ⟨-, x, hx, hxz⟩ := mem_nbhd.mp h
    have : key (low z) ≤ key x := by
      apply key_low_le
      rcases hxz with rfl | hxz
      · exact Or.inl rfl
      · exact Or.inr hxz.symm
    exact hC.mem_of_le hx ((low_subset z).trans hz) this
  · intro h
    refine mem_nbhd.mpr ⟨hz, low z, h, ?_⟩
    rcases low_eq_or_adj z with h' | h'
    · exact Or.inl h'
    · exact Or.inr h'.symm

/-- **The closed neighbourhood of an initial segment is an initial segment.** -/
theorem isInit_nbhd {U : Finset ℕ} {C : Finset (Finset ℕ)} (hC : IsInit U C) :
    IsInit U (nbhd U C) := by
  refine ⟨nbhd_subset_powerset U C, fun y hy z hz hle => ?_⟩
  have hyU := (mem_nbhd.mp hy).1
  have hzU := mem_powerset.mp hz
  rw [mem_nbhd_iff_low_mem hC hzU]
  rw [mem_nbhd_iff_low_mem hC hyU] at hy
  exact hC.mem_of_le hy ((low_subset z).trans hzU) (key_low_mono hle)


/-! ### Adjacency across a coordinate -/

theorem adj_insert_insert_iff {i : ℕ} {x y : Finset ℕ} (hx : i ∉ x) (hy : i ∉ y) :
    Adj (insert i x) (insert i y) ↔ Adj x y := by
  constructor
  · rintro ⟨j, hj⟩
    have hji : j ≠ i := by
      rintro rfl
      have : j ∈ insert j y := mem_insert_self _ _
      rw [hj, mem_symmDiff_singleton] at this
      simp at this
    refine ⟨j, ?_⟩
    ext a
    have := congrArg (a ∈ ·) hj
    simp only [mem_insert, mem_symmDiff_singleton, eq_iff_iff] at this
    rw [mem_symmDiff_singleton]
    by_cases hai : a = i
    · subst hai; simp [hx, hy, hji.symm]
    · simpa [hai] using this
  · rintro ⟨j, rfl⟩
    have hji : j ≠ i := by
      rintro rfl
      apply hy
      rw [mem_symmDiff_singleton]; exact Or.inr ⟨hx, rfl⟩
    refine ⟨j, ?_⟩
    ext a
    simp only [mem_insert, mem_symmDiff_singleton]
    by_cases hai : a = i
    · subst hai; simp [hji.symm]
    · simp [hai]

theorem eq_erase_of_adj {i : ℕ} {x y : Finset ℕ} (hx : i ∈ x) (hy : i ∉ y) (h : Adj x y) :
    y = x.erase i := by
  obtain ⟨j, rfl⟩ := h
  have hji : j = i := by
    by_contra hne
    apply hy
    rw [mem_symmDiff_singleton]; exact Or.inl ⟨hx, fun h => hne h.symm⟩
  subst hji
  exact symmDiff_singleton_of_mem hx

/-! ### Sections -/

/-- The lower `i`-section: the members of `S` avoiding `i`. -/
def lowerSec (i : ℕ) (S : Finset (Finset ℕ)) : Finset (Finset ℕ) := S.filter (fun x => i ∉ x)

/-- The upper `i`-section: the members of `S` containing `i`, with `i` removed. -/
def upperSec (i : ℕ) (S : Finset (Finset ℕ)) : Finset (Finset ℕ) :=
  (S.filter (fun x => i ∈ x)).image (fun x => x.erase i)

theorem mem_lowerSec {i : ℕ} {S : Finset (Finset ℕ)} {x : Finset ℕ} :
    x ∈ lowerSec i S ↔ x ∈ S ∧ i ∉ x := by
  unfold lowerSec; rw [mem_filter]

theorem mem_upperSec {i : ℕ} {S : Finset (Finset ℕ)} {x : Finset ℕ} :
    x ∈ upperSec i S ↔ i ∉ x ∧ insert i x ∈ S := by
  unfold upperSec
  rw [mem_image]
  constructor
  · rintro ⟨y, hy, rfl⟩
    rw [mem_filter] at hy
    exact ⟨notMem_erase _ _, by rw [insert_erase hy.2]; exact hy.1⟩
  · rintro ⟨hix, hins⟩
    exact ⟨insert i x, mem_filter.mpr ⟨hins, mem_insert_self _ _⟩, erase_insert hix⟩

theorem lowerSec_subset {U : Finset ℕ} {i : ℕ} {S : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) :
    lowerSec i S ⊆ (U.erase i).powerset := by
  intro x hx
  rw [mem_lowerSec] at hx
  rw [mem_powerset, subset_erase]
  exact ⟨mem_powerset.mp (hS hx.1), hx.2⟩

theorem upperSec_subset {U : Finset ℕ} {i : ℕ} {S : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) :
    upperSec i S ⊆ (U.erase i).powerset := by
  intro x hx
  rw [mem_upperSec] at hx
  rw [mem_powerset, subset_erase]
  exact ⟨(subset_insert i x).trans (mem_powerset.mp (hS hx.2)), hx.1⟩

theorem card_sec (i : ℕ) (S : Finset (Finset ℕ)) :
    S.card = (lowerSec i S).card + (upperSec i S).card := by
  have himg : (upperSec i S).card = (S.filter (fun x => i ∈ x)).card := by
    unfold upperSec
    apply card_image_of_injOn
    intro x hx y hy hxy
    simp only [coe_filter] at hx hy
    have := congrArg (insert i) hxy
    simp only at this
    rwa [insert_erase hx.2, insert_erase hy.2] at this
  rw [himg, lowerSec, add_comm]
  exact (card_filter_add_card_filter_not (s := S) (fun x => i ∈ x)).symm

/-- Gluing two families on `U.erase i` into one on `U`. -/
def glue (i : ℕ) (A B : Finset (Finset ℕ)) : Finset (Finset ℕ) := A ∪ B.image (insert i)

theorem mem_glue {i : ℕ} {A B : Finset (Finset ℕ)} {x : Finset ℕ} :
    x ∈ glue i A B ↔ x ∈ A ∨ ∃ y ∈ B, insert i y = x := by
  unfold glue; rw [mem_union, mem_image]

theorem lowerSec_glue {i : ℕ} {A B : Finset (Finset ℕ)} (hA : ∀ x ∈ A, i ∉ x) :
    lowerSec i (glue i A B) = A := by
  ext x
  rw [mem_lowerSec, mem_glue]
  constructor
  · rintro ⟨hx | ⟨y, -, rfl⟩, hi⟩
    · exact hx
    · exact absurd (mem_insert_self i y) hi
  · intro hx; exact ⟨Or.inl hx, hA x hx⟩

theorem upperSec_glue {i : ℕ} {A B : Finset (Finset ℕ)} (hA : ∀ x ∈ A, i ∉ x)
    (hB : ∀ x ∈ B, i ∉ x) : upperSec i (glue i A B) = B := by
  ext x
  rw [mem_upperSec, mem_glue]
  constructor
  · rintro ⟨hix, hx | ⟨y, hy, hyx⟩⟩
    · exact absurd (mem_insert_self i x) (hA _ hx)
    · have := congrArg (fun s => s.erase i) hyx
      simp only [erase_insert (hB y hy), erase_insert hix] at this
      rwa [← this]
  · intro hx; exact ⟨hB x hx, Or.inr ⟨x, hx, rfl⟩⟩

theorem glue_sec (i : ℕ) (S : Finset (Finset ℕ)) : glue i (lowerSec i S) (upperSec i S) = S := by
  ext x
  rw [mem_glue, mem_lowerSec]
  constructor
  · rintro (⟨hx, -⟩ | ⟨y, hy, rfl⟩)
    · exact hx
    · exact (mem_upperSec.mp hy).2
  · intro hx
    by_cases hix : i ∈ x
    · right
      exact ⟨x.erase i, mem_upperSec.mpr ⟨notMem_erase _ _, by rw [insert_erase hix]; exact hx⟩,
        insert_erase hix⟩
    · exact Or.inl ⟨hx, hix⟩

theorem glue_subset {U : Finset ℕ} {i : ℕ} (hi : i ∈ U) {A B : Finset (Finset ℕ)}
    (hA : A ⊆ (U.erase i).powerset) (hB : B ⊆ (U.erase i).powerset) :
    glue i A B ⊆ U.powerset := by
  intro x hx
  rw [mem_glue] at hx
  rw [mem_powerset]
  rcases hx with hx | ⟨y, hy, rfl⟩
  · exact (mem_powerset.mp (hA hx)).trans (erase_subset _ _)
  · exact insert_subset hi ((mem_powerset.mp (hB hy)).trans (erase_subset _ _))

theorem notMem_of_mem_erase_powerset {U : Finset ℕ} {i : ℕ} {x : Finset ℕ}
    (hx : x ∈ (U.erase i).powerset) : i ∉ x :=
  (subset_erase.mp (mem_powerset.mp hx)).2

/-- The closed neighbourhood, lower section. -/
theorem lowerSec_nbhd {U : Finset ℕ} {i : ℕ} {S : Finset (Finset ℕ)} (hS : S ⊆ U.powerset) :
    lowerSec i (nbhd U S) = nbhd (U.erase i) (lowerSec i S) ∪ upperSec i S := by
  ext y
  rw [mem_lowerSec, mem_union, mem_nbhd, mem_nbhd, mem_upperSec, subset_erase]
  constructor
  · rintro ⟨⟨hyU, x, hxS, hxy⟩, hiy⟩
    by_cases hix : i ∈ x
    · right
      refine ⟨hiy, ?_⟩
      rcases hxy with rfl | hxy
      · exact absurd hix hiy
      · rw [eq_erase_of_adj hix hiy hxy, insert_erase hix]; exact hxS
    · left
      exact ⟨⟨hyU, hiy⟩, x, mem_lowerSec.mpr ⟨hxS, hix⟩, hxy⟩
  · rintro (⟨⟨hyU, hiy⟩, x, hx, hxy⟩ | ⟨hiy, hins⟩)
    · exact ⟨⟨hyU, x, (mem_lowerSec.mp hx).1, hxy⟩, hiy⟩
    · refine ⟨⟨(subset_insert i y).trans (mem_powerset.mp (hS hins)), insert i y, hins,
        Or.inr ?_⟩, hiy⟩
      have := adj_erase (mem_insert_self i y)
      rwa [erase_insert hiy] at this

/-- The closed neighbourhood, upper section. -/
theorem upperSec_nbhd {U : Finset ℕ} {i : ℕ} (hi : i ∈ U) {S : Finset (Finset ℕ)}
    (hS : S ⊆ U.powerset) :
    upperSec i (nbhd U S) = nbhd (U.erase i) (upperSec i S) ∪ lowerSec i S := by
  ext y
  rw [mem_upperSec, mem_union, mem_nbhd, mem_nbhd, mem_lowerSec, subset_erase]
  constructor
  · rintro ⟨hiy, hyU, x, hxS, hxy⟩
    by_cases hix : i ∈ x
    · left
      refine ⟨⟨(subset_insert i y).trans hyU, hiy⟩, x.erase i,
        mem_upperSec.mpr ⟨notMem_erase _ _, by rw [insert_erase hix]; exact hxS⟩, ?_⟩
      rcases hxy with hxy | hxy
      · left; rw [hxy, erase_insert hiy]
      · right
        rw [← adj_insert_insert_iff (notMem_erase i x) hiy, insert_erase hix]
        exact hxy
    · right
      rcases hxy with hxy | hxy
      · exact absurd (hxy ▸ mem_insert_self i y) hix
      · have := eq_erase_of_adj (mem_insert_self i y) hix hxy.symm
        rw [erase_insert hiy] at this
        rw [← this]; exact ⟨hxS, hix⟩
  · rintro (⟨⟨hyU, hiy⟩, x, hx, hxy⟩ | ⟨hyS, hiy⟩)
    · rw [mem_upperSec] at hx
      refine ⟨hiy, insert_subset hi hyU, insert i x, hx.2, ?_⟩
      rcases hxy with rfl | hxy
      · exact Or.inl rfl
      · exact Or.inr ((adj_insert_insert_iff hx.1 hiy).mpr hxy)
    · exact ⟨hiy, insert_subset hi (mem_powerset.mp (hS hyS)), y, hyS, Or.inr (adj_insert hiy)⟩

/-- **The neighbourhood splits across a coordinate.** -/
theorem card_nbhd_sec {U : Finset ℕ} {i : ℕ} (hi : i ∈ U) {S : Finset (Finset ℕ)}
    (hS : S ⊆ U.powerset) :
    (nbhd U S).card = (nbhd (U.erase i) (lowerSec i S) ∪ upperSec i S).card +
      (nbhd (U.erase i) (upperSec i S) ∪ lowerSec i S).card := by
  rw [card_sec i (nbhd U S), lowerSec_nbhd hS, upperSec_nbhd hi hS]

/-- Sections of an initial segment are initial segments. -/
theorem IsInit.lowerSec {U : Finset ℕ} {i : ℕ} {S : Finset (Finset ℕ)} (h : IsInit U S) :
    IsInit (U.erase i) (lowerSec i S) := by
  refine ⟨lowerSec_subset h.subset, fun x hx y hy hle => ?_⟩
  rw [mem_lowerSec] at hx ⊢
  have hyU := subset_erase.mp (mem_powerset.mp hy)
  exact ⟨h.mem_of_le hx.1 hyU.1 hle, hyU.2⟩

theorem IsInit.upperSec {U : Finset ℕ} {i : ℕ} (hi : i ∈ U) {S : Finset (Finset ℕ)}
    (h : IsInit U S) : IsInit (U.erase i) (upperSec i S) := by
  refine ⟨upperSec_subset h.subset, fun x hx y hy hle => ?_⟩
  rw [mem_upperSec] at hx ⊢
  have hyU := subset_erase.mp (mem_powerset.mp hy)
  refine ⟨hyU.2, h.mem_of_le hx.2 (insert_subset hi hyU.1) ?_⟩
  exact (key_insert_le_insert hyU.2 hx.1).mpr hle

/-! ### Sums over a glued family -/

theorem sum_glue {i : ℕ} {A B : Finset (Finset ℕ)} (hA : ∀ x ∈ A, i ∉ x) (hB : ∀ x ∈ B, i ∉ x)
    (f : Finset ℕ → ℕ) :
    ∑ x ∈ glue i A B, f x = ∑ x ∈ A, f x + ∑ x ∈ B, f (insert i x) := by
  unfold glue
  rw [sum_union, sum_image]
  · intro x hx y hy hxy
    have := congrArg (fun s => s.erase i) hxy
    simpa [erase_insert (hB x hx), erase_insert (hB y hy)] using this
  · rw [disjoint_left]
    intro x hxA hxB
    rw [mem_image] at hxB
    obtain ⟨y, -, rfl⟩ := hxB
    exact hA _ hxA (mem_insert_self i y)

theorem card_glue {i : ℕ} {A B : Finset (Finset ℕ)} (hA : ∀ x ∈ A, i ∉ x)
    (hB : ∀ x ∈ B, i ∉ x) : (glue i A B).card = A.card + B.card := by
  have := sum_glue hA hB (fun _ => 1)
  simpa using this

/-! ### An exchange lemma: initial segments minimise a monotone sum -/

/-- If `f` is strictly increasing along the simplicial order on `M`, the down-closed
`D ⊆ M` has the least `f`-sum among subsets of `M` of its size, and only it. -/
theorem sum_le_of_downClosed (f : Finset ℕ → ℕ) (M : Finset (Finset ℕ))
    (hf : ∀ a ∈ M, ∀ b ∈ M, key a < key b → f a < f b) (D : Finset (Finset ℕ)) (hDM : D ⊆ M)
    (hD : ∀ x ∈ D, ∀ y ∈ M, key y ≤ key x → y ∈ D) :
    ∀ n, ∀ A : Finset (Finset ℕ), A ⊆ M → A.card = D.card → (A \ D).card = n →
      ∑ x ∈ D, f x ≤ ∑ x ∈ A, f x ∧ (∑ x ∈ A, f x ≤ ∑ x ∈ D, f x → A = D) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro A hAM hcard hn
    by_cases hAD : A = D
    · subst hAD; exact ⟨le_rfl, fun _ => rfl⟩
    have h1 : (A \ D).Nonempty := by
      rw [nonempty_iff_ne_empty, Ne, sdiff_eq_empty_iff_subset]
      intro h; exact hAD (eq_of_subset_of_card_le h hcard.ge)
    have h2 : (D \ A).Nonempty := by
      rw [nonempty_iff_ne_empty, Ne, sdiff_eq_empty_iff_subset]
      intro h; exact hAD (eq_of_subset_of_card_le h hcard.le).symm
    obtain ⟨a, ha⟩ := h1
    obtain ⟨b, hb⟩ := h2
    rw [mem_sdiff] at ha hb
    have hba : key b < key a := by
      by_contra hcon
      exact ha.2 (hD b hb.1 a (hAM ha.1) (not_lt.mp hcon))
    have hfab : f b < f a := hf b (hDM hb.1) a (hAM ha.1) hba
    set A' := insert b (A.erase a) with hA'
    have hbA' : b ∉ A.erase a := fun h => hb.2 (mem_of_mem_erase h)
    have hA'M : A' ⊆ M := insert_subset (hDM hb.1) ((erase_subset _ _).trans hAM)
    have hA'card : A'.card = D.card := by
      rw [hA', card_insert_of_notMem hbA', card_erase_of_mem ha.1, ← hcard]
      have := card_pos.mpr ⟨a, ha.1⟩; omega
    have hA'D : A' \ D = (A \ D).erase a := by
      ext z
      simp only [hA', mem_sdiff, mem_insert, mem_erase]
      constructor
      · rintro ⟨rfl | ⟨hza, hzA⟩, hzD⟩
        · exact absurd hb.1 hzD
        · exact ⟨hza, hzA, hzD⟩
      · rintro ⟨hza, hzA, hzD⟩; exact ⟨Or.inr ⟨hza, hzA⟩, hzD⟩
    have hlt : (A' \ D).card < n := by
      rw [hA'D, card_erase_of_mem (mem_sdiff.mpr ha), hn]
      have := card_pos.mpr ⟨a, mem_sdiff.mpr ha⟩; omega
    obtain ⟨ih1, -⟩ := ih _ hlt A' hA'M hA'card rfl
    have hsum : ∑ x ∈ A', f x + f a = ∑ x ∈ A, f x + f b := by
      have := sum_erase_add A f ha.1
      rw [hA', sum_insert hbA']; omega
    refine ⟨by omega, fun h => absurd h (by omega)⟩

end MOSPFormalization.Hypercube
