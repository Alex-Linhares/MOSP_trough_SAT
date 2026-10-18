/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The boundary profile of the simplicial order on `Q_d`

On the ground set `range d = {0, …, d - 1}`, the simplicial order of `Q_{d+1}` is
the order of `Q_d` played layer by layer twice: the sets containing the new
element `d` come first within each size. So an initial segment `S` of `Q_{d+1}`
has `d`-sections of one of two shapes (`ball d r` is the family of subsets of
size `< r`):

* `S₊ = ball d t` and `ball d t ⊆ S₋ ⊆ ball d (t + 1)`, or
* `S₋ = ball d (t + 1)` and `ball d t ⊆ S₊ ⊆ ball d (t + 1)`.

Splitting `|N(S)|` across the sections (`card_nbhd_sec`) then gives, by
induction on `d`, with `harperSum d = Σ_{i < d} C(i, ⌊i/2⌋)`:

* `card_nbhd_init_le` — every initial segment `S` of `Q_d` has
  `|N(S)| ≤ |S| + harperSum d` (the step adds at most `C(d, t) ≤ C(d, ⌊d/2⌋)`);
* `exists_init_profile` — some initial segment, sandwiched between the balls of
  radius `⌊d/2⌋`, attains `|N(S)| ≥ |S| + harperSum d` (the step adds exactly
  the middle binomial coefficient).

This is the induction "mentioned on the last page of Harper's article", as
Chandran & Kavitha (2006, after Lemma 3) put it.
-/

import MOSPFormalization.Hypercube.Harper

set_option linter.unusedSectionVars false

namespace MOSPFormalization.Hypercube

open Finset

/-- `Σ_{i < d} C(i, ⌊i/2⌋)`, OEIS A036256: the vertex separation of `Q_d`. -/
def harperSum (d : ℕ) : ℕ := ∑ i ∈ range d, i.choose (i / 2)

theorem harperSum_succ (d : ℕ) : harperSum (d + 1) = harperSum d + d.choose (d / 2) := by
  unfold harperSum; rw [sum_range_succ]

theorem harperSum_zero : harperSum 0 = 0 := rfl

/-- The subsets of `range d` with fewer than `r` elements. -/
def ball (d r : ℕ) : Finset (Finset ℕ) := (range d).powerset.filter (fun z => z.card < r)

theorem mem_ball {d r : ℕ} {z : Finset ℕ} : z ∈ ball d r ↔ z ⊆ range d ∧ z.card < r := by
  unfold ball; rw [mem_filter, mem_powerset]

theorem ball_subset_powerset (d r : ℕ) : ball d r ⊆ (range d).powerset := filter_subset _ _

theorem ball_mono {d r s : ℕ} (h : r ≤ s) : ball d r ⊆ ball d s := by
  intro z hz; rw [mem_ball] at hz ⊢; exact ⟨hz.1, by omega⟩

theorem card_ball_succ (d r : ℕ) : (ball d (r + 1)).card = (ball d r).card + d.choose r := by
  have : ball d (r + 1) = ball d r ∪ powersetCard r (range d) := by
    ext z; rw [mem_union, mem_ball, mem_ball, mem_powersetCard]
    constructor
    · rintro ⟨h1, h2⟩
      rcases Nat.lt_or_ge z.card r with h | h
      · exact Or.inl ⟨h1, h⟩
      · exact Or.inr ⟨h1, by omega⟩
    · rintro (⟨h1, h2⟩ | ⟨h1, h2⟩)
      · exact ⟨h1, by omega⟩
      · exact ⟨h1, by omega⟩
  rw [this, card_union_of_disjoint, card_powersetCard, card_range]
  rw [disjoint_left]
  intro z h1 h2
  rw [mem_ball] at h1; rw [mem_powersetCard] at h2; omega

theorem isInit_ball (d r : ℕ) : IsInit (range d) (ball d r) := by
  refine ⟨ball_subset_powerset d r, fun x hx y hy hle => ?_⟩
  rw [mem_ball] at hx ⊢
  exact ⟨mem_powerset.mp hy, (card_le_of_key_le hle).trans_lt hx.2⟩

theorem nbhd_ball_subset (d r : ℕ) : nbhd (range d) (ball d r) ⊆ ball d (r + 1) := by
  intro y hy
  obtain ⟨hyU, x, hx, hxy⟩ := mem_nbhd.mp hy
  rw [mem_ball] at hx ⊢
  refine ⟨hyU, ?_⟩
  rcases hxy with rfl | hxy
  · omega
  · rcases hxy.card with h | h <;> omega

theorem ball_succ_subset_nbhd {d r : ℕ} {T : Finset (Finset ℕ)} (hT : ball d r ⊆ T)
    (h0 : r = 0 → ∅ ∈ T) : ball d (r + 1) ⊆ nbhd (range d) T := by
  intro z hz
  rw [mem_ball] at hz
  rw [mem_nbhd]
  refine ⟨hz.1, ?_⟩
  rcases Nat.lt_or_ge z.card r with hlt | hge
  · exact ⟨z, hT (mem_ball.mpr ⟨hz.1, hlt⟩), Or.inl rfl⟩
  · have hzr : z.card = r := by omega
    rcases Nat.eq_zero_or_pos r with hr | hr
    · refine ⟨z, ?_, Or.inl rfl⟩
      rw [hr, card_eq_zero] at hzr
      rw [hzr]; exact h0 hr
    · obtain ⟨e, he⟩ : z.Nonempty := card_pos.mp (by omega)
      refine ⟨z.erase e, hT (mem_ball.mpr ⟨(erase_subset _ _).trans hz.1, ?_⟩), Or.inr ?_⟩
      · rw [card_erase_of_mem he]; omega
      · have := adj_insert (notMem_erase e z)
        rwa [insert_erase he] at this

theorem range_succ_erase (d : ℕ) : (range (d + 1)).erase d = range d := by
  rw [range_add_one, erase_insert notMem_range_self]

theorem notMem_of_mem_range_powerset {d : ℕ} {x : Finset ℕ} (hx : x ∈ (range d).powerset) :
    d ∉ x := fun h => by simpa using mem_powerset.mp hx h

/-- A set containing the new element `d` precedes a set of the same size avoiding it. -/
theorem key_insert_lt_of_notMem {d : ℕ} {w y : Finset ℕ} (hy : y ⊆ range d)
    (hc : (insert d w).card = y.card) : key (insert d w) < key y := by
  have hdy : d ∉ y := fun h => by simpa using hy h
  rw [key_lt_iff_of_card_eq hc]
  refine ⟨d, mem_insert_self _ _, hdy, fun b hb _ => ?_⟩
  simpa using hy hb

/-! ### Upper bound: every initial segment -/

/-- **Every initial segment of `Q_d` has at most `harperSum d` boundary vertices.** -/
theorem card_nbhd_init_le : ∀ d, ∀ S, IsInit (range d) S →
    (nbhd (range d) S).card ≤ S.card + harperSum d := by
  intro d
  induction d with
  | zero =>
    intro S hS
    rw [harperSum_zero, add_zero]
    rcases S.eq_empty_or_nonempty with rfl | hne
    · rw [nbhd_empty]
    · have h1 : (nbhd (range 0) S).card ≤ 1 := by
        have := card_le_card (nbhd_subset_powerset (range 0) S)
        simpa using this
      have := card_pos.mpr hne; omega
  | succ d ih =>
    intro S hS
    rcases S.eq_empty_or_nonempty with rfl | hne
    · rw [nbhd_empty]; simp
    have hdU : d ∈ range (d + 1) := self_mem_range_succ d
    have hsplit := card_nbhd_sec hdU hS.subset
    have hcard := card_sec d S
    rw [range_succ_erase] at hsplit
    set A := lowerSec d S
    set B := upperSec d S
    have hA : IsInit (range d) A := by have := hS.lowerSec (i := d); rwa [range_succ_erase] at this
    have hB : IsInit (range d) B := by have := hS.upperSec hdU; rwa [range_succ_erase] at this
    have hAav : ∀ x ∈ A, d ∉ x := fun x hx => notMem_of_mem_range_powerset (hA.subset hx)
    have hBav : ∀ x ∈ B, d ∉ x := fun x hx => notMem_of_mem_range_powerset (hB.subset hx)
    obtain ⟨s, hsS, hsmax⟩ := exists_max_image S key hne
    set t := s.card
    -- `S` sits between the balls of radius `t`
    have hSup : ∀ z ∈ S, z.card ≤ t := fun z hz => card_le_of_key_le (hsmax z hz)
    have hSlow : ∀ z ⊆ range (d + 1), z.card < t → z ∈ S :=
      fun z hz hlt => hS.mem_of_le hsS hz (key_lt_of_card_lt hlt).le
    have hAlow : ball d t ⊆ A := by
      intro z hz
      rw [mem_ball] at hz
      exact mem_lowerSec.mpr ⟨hSlow z (hz.1.trans (range_subset_range.mpr (by omega))) hz.2,
        fun h => by simpa using hz.1 h⟩
    have hAup : A ⊆ ball d (t + 1) := by
      intro z hz
      rw [mem_ball]
      refine ⟨mem_powerset.mp (hA.subset hz), ?_⟩
      have := hSup z (mem_lowerSec.mp hz).1; omega
    have hBup : B ⊆ ball d t := by
      intro z hz
      rw [mem_ball]
      refine ⟨mem_powerset.mp (hB.subset hz), ?_⟩
      have h1 := hSup _ (mem_upperSec.mp hz).2
      rw [card_insert_of_notMem (mem_upperSec.mp hz).1] at h1; omega
    have hBlow : ball d (t - 1) ⊆ B := by
      intro z hz
      rw [mem_ball] at hz
      have hdz : d ∉ z := fun h => by simpa using hz.1 h
      refine mem_upperSec.mpr ⟨hdz, hSlow _ ?_ ?_⟩
      · exact insert_subset hdU (hz.1.trans (range_subset_range.mpr (by omega)))
      · rw [card_insert_of_notMem hdz]; omega
    by_cases hcase : ∃ a ∈ A, a.card = t
    · -- first shape: `B = ball d t`
      obtain ⟨a, haA, hat⟩ := hcase
      have hBeq : B = ball d t := by
        apply Subset.antisymm hBup
        intro z hz
        rw [mem_ball] at hz
        have hdz : d ∉ z := fun h => by simpa using hz.1 h
        refine mem_upperSec.mpr ⟨hdz, ?_⟩
        have hzU : insert d z ⊆ range (d + 1) :=
          insert_subset hdU (hz.1.trans (range_subset_range.mpr (by omega)))
        rcases Nat.lt_or_ge (insert d z).card t with hlt | hge
        · exact hSlow _ hzU hlt
        · have hc : (insert d z).card = a.card := by
            rw [card_insert_of_notMem hdz] at hge ⊢; omega
          exact hS.mem_of_le (mem_lowerSec.mp haA).1 hzU
            (key_insert_lt_of_notMem (mem_powerset.mp (hA.subset haA)) hc).le
      have e1 : nbhd (range d) A ∪ B = nbhd (range d) A :=
        union_eq_left.mpr (hBeq ▸ hAlow |>.trans (subset_nbhd hA.subset))
      have e2 : (nbhd (range d) B ∪ A).card ≤ (ball d (t + 1)).card := by
        apply card_le_card
        rw [hBeq]
        exact union_subset (nbhd_ball_subset d t) hAup
      have hmid : d.choose t ≤ d.choose (d / 2) := Nat.choose_le_middle t d
      have hih := ih A hA
      rw [card_ball_succ, ← hBeq] at e2
      rw [hsplit, e1, harperSum_succ]
      omega
    · -- second shape: `A = ball d t`
      push Not at hcase
      have hAeq : A = ball d t := by
        apply Subset.antisymm _ hAlow
        intro z hz
        have := hAup hz
        rw [mem_ball] at this ⊢
        exact ⟨this.1, lt_of_le_of_ne (by omega) (hcase z hz)⟩
      have hds : d ∈ s := by
        by_contra hds
        exact hcase s (mem_lowerSec.mpr ⟨hsS, hds⟩) rfl
      have ht : 1 ≤ t := card_pos.mpr ⟨d, hds⟩
      have hBne : B.Nonempty :=
        ⟨s.erase d, mem_upperSec.mpr ⟨notMem_erase _ _, by rw [insert_erase hds]; exact hsS⟩⟩
      set t' := t - 1 with ht'
      have htt : t = t' + 1 := by omega
      rw [htt] at hAeq hBup
      have hBlow' : ball d t' ⊆ B := hBlow
      have e2 : nbhd (range d) B ∪ A = nbhd (range d) B := by
        apply union_eq_left.mpr
        rw [hAeq]
        exact ball_succ_subset_nbhd hBlow' (fun _ => hB.empty_mem hBne)
      have e1 : (nbhd (range d) A ∪ B).card ≤ (ball d (t' + 1 + 1)).card := by
        apply card_le_card
        rw [hAeq]
        exact union_subset (nbhd_ball_subset d _) (hBup.trans (ball_mono (by omega)))
      have hmid : d.choose (t' + 1) ≤ d.choose (d / 2) := Nat.choose_le_middle _ d
      have hih := ih B hB
      rw [card_ball_succ, ← hAeq] at e1
      rw [hsplit, e2, harperSum_succ]
      omega

/-! ### Lower bound: the profile attains `harperSum d` -/

/-- The first shape is an initial segment. -/
theorem isInit_glue_first {d r : ℕ} {T : Finset (Finset ℕ)} (hT : IsInit (range d) T)
    (hlo : ball d r ⊆ T) (hhi : T ⊆ ball d (r + 1)) :
    IsInit (range (d + 1)) (glue d T (ball d r)) := by
  have hdU : d ∈ range (d + 1) := self_mem_range_succ d
  refine ⟨?_, fun x hx y hy hle => ?_⟩
  · have := glue_subset hdU (i := d) (A := T) (B := ball d r)
    rw [range_succ_erase] at this
    exact this hT.subset (ball_subset_powerset d r)
  have hyU := mem_powerset.mp hy
  have hxr : x.card ≤ r := by
    rcases mem_glue.mp hx with hx | ⟨w, hw, rfl⟩
    · have := mem_ball.mp (hhi hx); omega
    · rw [mem_ball] at hw
      have := card_insert_le d w; omega
  have hyr : y.card ≤ r := (card_le_of_key_le hle).trans hxr
  rw [mem_glue]
  by_cases hdy : d ∈ y
  · right
    refine ⟨y.erase d, mem_ball.mpr ⟨?_, ?_⟩, insert_erase hdy⟩
    · intro b hb
      rw [mem_erase] at hb
      have := hyU hb.2; rw [mem_range] at this ⊢; omega
    · have := card_erase_add_one hdy; omega
  · left
    have hyd : y ⊆ range d := by
      intro b hb
      have := hyU hb; rw [mem_range] at this ⊢
      exact lt_of_le_of_ne (by omega) (fun h => hdy (h ▸ hb))
    rcases Nat.lt_or_ge y.card r with hlt | hge
    · exact hlo (mem_ball.mpr ⟨hyd, hlt⟩)
    rcases mem_glue.mp hx with hx | ⟨w, hw, rfl⟩
    · exact hT.mem_of_le hx hyd hle
    · exfalso
      have := card_le_of_key_le hle
      have hc : (insert d w).card = y.card := by omega
      exact absurd hle (not_le.mpr (key_insert_lt_of_notMem hyd hc))

/-- The second shape is an initial segment. -/
theorem isInit_glue_second {d r : ℕ} {T : Finset (Finset ℕ)} (hT : IsInit (range d) T)
    (hlo : ball d r ⊆ T) (hhi : T ⊆ ball d (r + 1)) :
    IsInit (range (d + 1)) (glue d (ball d (r + 1)) T) := by
  have hdU : d ∈ range (d + 1) := self_mem_range_succ d
  refine ⟨?_, fun x hx y hy hle => ?_⟩
  · have := glue_subset hdU (i := d) (A := ball d (r + 1)) (B := T)
    rw [range_succ_erase] at this
    exact this (ball_subset_powerset d _) hT.subset
  have hyU := mem_powerset.mp hy
  have hxr : x.card ≤ r + 1 := by
    rcases mem_glue.mp hx with hx | ⟨w, hw, rfl⟩
    · have := mem_ball.mp hx; omega
    · have := mem_ball.mp (hhi hw)
      have := card_insert_le d w; omega
  have hyr : y.card ≤ r + 1 := (card_le_of_key_le hle).trans hxr
  rw [mem_glue]
  have hyed : y.erase d ⊆ range d := by
    intro b hb
    rw [mem_erase] at hb
    have := hyU hb.2; rw [mem_range] at this ⊢; omega
  by_cases hdy : d ∈ y
  · right
    refine ⟨y.erase d, ?_, insert_erase hdy⟩
    have hce := card_erase_add_one hdy
    rcases Nat.lt_or_ge (y.erase d).card r with hlt | hge
    · exact hlo (mem_ball.mpr ⟨hyed, hlt⟩)
    -- `y` has size `r + 1`, so `x` does too, and `x` contains `d`
    rcases mem_glue.mp hx with hx | ⟨w, hw, rfl⟩
    · have := mem_ball.mp hx
      have := card_le_of_key_le hle; omega
    · have hdw : d ∉ w := notMem_of_mem_range_powerset (hT.subset hw)
      have hle' : key (insert d (y.erase d)) ≤ key (insert d w) := by rwa [insert_erase hdy]
      rw [key_insert_le_insert (notMem_erase d y) hdw] at hle'
      exact hT.mem_of_le hw hyed hle'
  · left
    have hyd : y ⊆ range d := by
      intro b hb
      have := hyU hb; rw [mem_range] at this ⊢
      exact lt_of_le_of_ne (by omega) (fun h => hdy (h ▸ hb))
    refine mem_ball.mpr ⟨hyd, ?_⟩
    rcases Nat.lt_or_ge y.card (r + 1) with hlt | hge
    · exact hlt
    exfalso
    rcases mem_glue.mp hx with hx | ⟨w, hw, rfl⟩
    · have := mem_ball.mp hx; have := card_le_of_key_le hle; omega
    · have := card_le_of_key_le hle
      have hc : (insert d w).card = y.card := by omega
      exact absurd hle (not_le.mpr (key_insert_lt_of_notMem hyd hc))

theorem ball_succ_subset_glue {d r : ℕ} {A B : Finset (Finset ℕ)} (hA : ball d r ⊆ A)
    (hB : ball d (r - 1) ⊆ B) : ball (d + 1) r ⊆ glue d A B := by
  intro z hz
  rw [mem_ball] at hz
  rw [mem_glue]
  by_cases hdz : d ∈ z
  · right
    refine ⟨z.erase d, hB (mem_ball.mpr ⟨?_, ?_⟩), insert_erase hdz⟩
    · intro b hb
      rw [mem_erase] at hb
      have := hz.1 hb.2; rw [mem_range] at this ⊢; omega
    · have := card_erase_add_one hdz; omega
  · left
    refine hA (mem_ball.mpr ⟨?_, hz.2⟩)
    intro b hb
    have := hz.1 hb; rw [mem_range] at this ⊢
    exact lt_of_le_of_ne (by omega) (fun h => hdz (h ▸ hb))

theorem glue_subset_ball {d r : ℕ} {A B : Finset (Finset ℕ)} (hA : A ⊆ ball d (r + 1))
    (hB : B ⊆ ball d r) : glue d A B ⊆ ball (d + 1) (r + 1) := by
  intro z hz
  rw [mem_ball]
  rcases mem_glue.mp hz with hz | ⟨w, hw, rfl⟩
  · have := mem_ball.mp (hA hz)
    exact ⟨this.1.trans (range_subset_range.mpr (by omega)), this.2⟩
  · have := mem_ball.mp (hB hw)
    refine ⟨insert_subset (self_mem_range_succ d)
      (this.1.trans (range_subset_range.mpr (by omega))), ?_⟩
    have := card_insert_le d w; omega

/-- **Some initial segment of `Q_d` has at least `harperSum d` boundary vertices**,
sandwiched between the balls of radius `⌊d/2⌋`. -/
theorem exists_init_profile : ∀ d, ∃ T, IsInit (range d) T ∧ ∅ ∈ T ∧ ball d (d / 2) ⊆ T ∧
    T ⊆ ball d (d / 2 + 1) ∧ T.card + harperSum d ≤ (nbhd (range d) T).card := by
  intro d
  induction d with
  | zero =>
    refine ⟨(range 0).powerset, isInit_powerset _, by simp, ?_, ?_, ?_⟩
    · intro z hz; exact (mem_ball.mp hz).1 |> mem_powerset.mpr
    · intro z hz
      rw [mem_ball]
      refine ⟨mem_powerset.mp hz, ?_⟩
      have := mem_powerset.mp hz; simp at this; simp [this]
    · rw [harperSum_zero, add_zero]
      exact card_le_card (subset_nbhd subset_rfl)
  | succ d ih =>
    obtain ⟨T, hT, hT0, hlo, hhi, hbd⟩ := ih
    have hdU : d ∈ range (d + 1) := self_mem_range_succ d
    have hTav : ∀ x ∈ T, d ∉ x := fun x hx => notMem_of_mem_range_powerset (hT.subset hx)
    have hballav : ∀ r, ∀ x ∈ ball d r, d ∉ x :=
      fun r x hx => notMem_of_mem_range_powerset (ball_subset_powerset d r hx)
    rcases Nat.even_or_odd d with ⟨h, hh⟩ | ⟨h, hh⟩
    · -- `d = 2h`: the first shape, at radius `h`
      have hd2 : d / 2 = h := by omega
      have hd2' : (d + 1) / 2 = h := by omega
      rw [hd2] at hlo hhi
      have hSinit : IsInit (range (d + 1)) (glue d T (ball d h)) := isInit_glue_first hT hlo hhi
      have hSsub := hSinit.subset
      refine ⟨glue d T (ball d h), hSinit, mem_glue.mpr (Or.inl hT0), ?_, ?_, ?_⟩
      · rw [hd2']; exact ball_succ_subset_glue hlo (ball_mono (by omega))
      · rw [hd2']; exact glue_subset_ball hhi subset_rfl
      · have hsplit := card_nbhd_sec hdU hSsub
        rw [range_succ_erase, lowerSec_glue hTav, upperSec_glue hTav (hballav h)] at hsplit
        rw [hsplit, card_glue hTav (hballav h), harperSum_succ, hd2]
        have e1 : (nbhd (range d) T).card ≤ (nbhd (range d) T ∪ ball d h).card :=
          card_le_card subset_union_left
        have e2 : (ball d (h + 1)).card ≤ (nbhd (range d) (ball d h) ∪ T).card := by
          apply card_le_card
          rcases Nat.eq_zero_or_pos h with h0 | h0
          · intro z hz
            rw [h0, mem_ball] at hz
            rw [mem_union]; right
            rw [card_eq_zero.mp (by omega : z.card = 0)]; exact hT0
          · exact (ball_succ_subset_nbhd subset_rfl (fun h' => absurd h' (by omega))).trans
              subset_union_left
        rw [card_ball_succ] at e2
        omega
    · -- `d = 2h + 1`: the second shape, at radius `h`
      have hd2 : d / 2 = h := by omega
      have hd2' : (d + 1) / 2 = h + 1 := by omega
      rw [hd2] at hlo hhi
      have hSinit : IsInit (range (d + 1)) (glue d (ball d (h + 1)) T) :=
        isInit_glue_second hT hlo hhi
      have hSsub := hSinit.subset
      have hball0 : ∅ ∈ ball d (h + 1) := mem_ball.mpr ⟨empty_subset _, by simp⟩
      refine ⟨glue d (ball d (h + 1)) T, hSinit, mem_glue.mpr (Or.inl hball0), ?_, ?_, ?_⟩
      · rw [hd2']; exact ball_succ_subset_glue subset_rfl (by simpa using hlo)
      · rw [hd2']; exact glue_subset_ball (ball_mono (by omega)) hhi
      · have hsplit := card_nbhd_sec hdU hSsub
        rw [range_succ_erase, lowerSec_glue (hballav _), upperSec_glue (hballav _) hTav] at hsplit
        rw [hsplit, card_glue (hballav _) hTav, harperSum_succ, hd2]
        have e1 : (ball d (h + 1 + 1)).card ≤ (nbhd (range d) (ball d (h + 1)) ∪ T).card :=
          card_le_card ((ball_succ_subset_nbhd subset_rfl (fun h' => absurd h' (by omega))).trans
            subset_union_left)
        have e2 : (nbhd (range d) T).card ≤ (nbhd (range d) T ∪ ball d (h + 1)).card :=
          card_le_card subset_union_left
        have hsym : d.choose (h + 1) = d.choose h := by rw [hh]; exact Nat.choose_symm_half h
        rw [card_ball_succ] at e1
        omega

end MOSPFormalization.Hypercube
