/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The pathwidth of the grid

An `(h, w)`-grid has pathwidth `min h w` (Ellis & Warren 2008, Theorem 4.1),
except the `1 × 1` grid, a single vertex, whose pathwidth is `0`.

## Definition

`grid h w` is Mathlib's box product `pathGraph h □ pathGraph w` on
`Fin h × Fin w`; `grid_adj` unfolds it to "equal in one coordinate, adjacent
integers in the other", and `grid_adj_iff_manhattan` to `|Δx| + |Δy| = 1`.

## Upper bound (Ellis & Warren, Lemma 4.1)

The row-major layout `(i, j) ↦ w·i + j` (Mathlib's `finProdFinEquiv`) has
bandwidth at most `w`: a horizontal edge stretches `1`, a vertical one `w`.
`pathwidth ≤ bandwidth` (`Sandwich.lean`) gives `pathwidth ≤ w`, and the
transpose isomorphism `boxProdComm` gives `pathwidth ≤ h`.

## Lower bound

Ellis & Warren argue through node search. We argue directly on vertex
separation, which `VSEquivPW.lean` equates with pathwidth, because it needs no
search game and no monotonicity: the whole argument is one counting step.

Fix a layout and let `t` be the first position whose prefix contains a whole
row or a whole column (it exists: the full prefix contains everything), and
let `S` be the prefix one step earlier, so `S` contains no whole row and no
whole column, and `S ∪ {v}` does, `v` the vertex at position `t`. Say it is a
row `r` (columns are symmetric). For every column `c`:

* if `c` is not `v`'s column, `(r, c) ∈ S` and column `c` has a vertex outside
  `S`, so walking along column `c` from one to the other crosses an edge from
  `S` to outside `S`: column `c` has a vertex outside `S` with a neighbour in `S`;
* in `v`'s column, `v` itself is such a vertex, found the same way by walking
  along row `r` from another column (here `w ≥ 2` is used).

So the boundary of `S` meets all `w` columns and has at least `w ≥ min h w`
vertices; the boundary of a prefix is exactly the active suffix of the layout
at that position. When `h = 1` or `w = 1` the grid is a path and one edge
suffices (`one_le_pathwidth_of_adj`).

## Main results

* `pathwidth_grid_le` — `pathwidth (grid h w) ≤ min h w`.
* `min_le_pathwidth_grid` — `min h w ≤ pathwidth (grid h w)` for `2 ≤ h, w`.
* `pathwidth_grid` — `pathwidth (grid h w) = min h w` unless `h = w = 1`.
* `pathwidth_grid_one_one` — the exception: `pathwidth (grid 1 1) = 0`.
* `pathwidth_grid_square` — `pathwidth (grid n n) = n` for `n ≠ 1`.
-/

import MOSPFormalization.Sandwich
import MOSPFormalization.Minor

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open SimpleGraph

/-! ### The grid -/

/-- The `(h, w)`-grid: `h` rows and `w` columns, the box product of two paths. -/
def grid (h w : ℕ) : SimpleGraph (Fin h × Fin w) := pathGraph h □ pathGraph w

theorem grid_adj {h w : ℕ} (x y : Fin h × Fin w) :
    (grid h w).Adj x y ↔
      ((x.1.val + 1 = y.1.val ∨ y.1.val + 1 = x.1.val) ∧ x.2 = y.2) ∨
      ((x.2.val + 1 = y.2.val ∨ y.2.val + 1 = x.2.val) ∧ x.1 = y.1) := by
  simp [grid, boxProd_adj, pathGraph_adj]

instance (h w : ℕ) : DecidableRel (grid h w).Adj :=
  fun x y => decidable_of_iff _ (grid_adj x y).symm

/-- The grid is the graph of Manhattan distance one. -/
theorem grid_adj_iff_manhattan {h w : ℕ} (x y : Fin h × Fin w) :
    (grid h w).Adj x y ↔
      |(x.1.val : ℤ) - y.1.val| + |(x.2.val : ℤ) - y.2.val| = 1 := by
  rw [grid_adj]
  constructor
  · rintro (⟨h1, h2⟩ | ⟨h1, h2⟩)
    · rw [h2]; rcases h1 with h1 | h1 <;> simp [abs_eq_max_neg] <;> omega
    · rw [h2]; rcases h1 with h1 | h1 <;> simp [abs_eq_max_neg] <;> omega
  · intro hd
    simp only [abs_eq_max_neg] at hd
    have e1 : ∀ a b : Fin h, a.val = b.val → a = b := fun a b => Fin.ext
    have e2 : ∀ a b : Fin w, a.val = b.val → a = b := fun a b => Fin.ext
    by_cases hx : x.1.val = y.1.val
    · right
      refine ⟨by omega, e1 _ _ hx⟩
    · left
      refine ⟨by omega, e2 _ _ (by omega)⟩

/-- The transpose. -/
def gridTranspose (h w : ℕ) : grid h w ≃g grid w h := boxProdComm _ _

theorem pathwidth_grid_comm (h w : ℕ) : pathwidth (grid h w) = pathwidth (grid w h) :=
  pathwidth_eq_of_iso (gridTranspose h w)

/-! ### Upper bound: the row-major layout -/

/-- The row-major layout `(i, j) ↦ w·i + j`. -/
def rowMajor (h w : ℕ) : LinearLayout (Fin h × Fin w) :=
  finProdFinEquiv.trans (finCongr (by simp))

theorem rowMajor_val {h w : ℕ} (x : Fin h × Fin w) :
    (rowMajor h w x).val = x.2.val + w * x.1.val := by
  simp [rowMajor]

theorem bandwidthOfLayout_rowMajor_le (h w : ℕ) :
    bandwidthOfLayout (grid h w) (rowMajor h w) ≤ w := by
  apply Finset.sup_le
  rintro ⟨x, y⟩ hxy
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hxy
  simp only [rowMajor_val]
  rw [grid_adj] at hxy
  rcases hxy with ⟨h1 | h1, h2⟩ | ⟨h1, h2⟩
  · rw [h2, ← h1, Nat.mul_succ]; omega
  · rw [h2, ← h1, Nat.mul_succ]; omega
  · rw [h2]; omega

/-- **Upper bound in one coordinate** (Ellis & Warren, Lemma 4.1). -/
theorem pathwidth_grid_le_right (h w : ℕ) : pathwidth (grid h w) ≤ w :=
  (pathwidth_le_bandwidthOfLayout _ (rowMajor h w)).trans
    (bandwidthOfLayout_rowMajor_le h w)

/-- **Upper bound**: `pathwidth (grid h w) ≤ min h w`. -/
theorem pathwidth_grid_le (h w : ℕ) : pathwidth (grid h w) ≤ min h w := by
  apply le_min _ (pathwidth_grid_le_right h w)
  rw [pathwidth_grid_comm]
  exact pathwidth_grid_le_right w h

/-! ### Lower bound: the first full row or column -/

/-- A discrete intermediate value step: if `P a` and not `P (a + d)`, some
`k ∈ [a, a + d)` has `P k` and not `P (k + 1)`. -/
theorem exists_step_of_not (P : ℕ → Prop) (a : ℕ) :
    ∀ d, P a → ¬ P (a + d) → ∃ k, a ≤ k ∧ k < a + d ∧ P k ∧ ¬ P (k + 1) := by
  intro d
  induction d with
  | zero => intro ha hd; exact absurd ha hd
  | succ d ih =>
    intro ha hd
    by_cases hm : P (a + d)
    · exact ⟨a + d, by omega, by omega, hm, by simpa [Nat.add_assoc] using hd⟩
    · obtain ⟨k, h1, h2, h3, h4⟩ := ih ha hm
      exact ⟨k, h1, by omega, h3, h4⟩

/-- `f` holds at `m`, read as true beyond the end of `Fin n`. -/
def FinPred {n : ℕ} (f : Fin n → Prop) (m : ℕ) : Prop := ∀ hm : m < n, f ⟨m, hm⟩

/-- Along a path `Fin n`, a predicate true at `a` and false at `b` changes
across some edge. -/
theorem exists_adj_step {n : ℕ} (f : Fin n → Prop) {a b : Fin n} (ha : f a) (hb : ¬ f b) :
    ∃ k k' : Fin n, (k.val + 1 = k'.val ∨ k'.val + 1 = k.val) ∧ f k ∧ ¬ f k' := by
  have hPa : FinPred f a := fun _ => ha
  have hPb : ¬ FinPred f b := fun h => hb (h b.isLt)
  rcases le_or_gt a.val b.val with hab | hab
  · obtain ⟨k, -, hk2, hk3, hk4⟩ :=
      exists_step_of_not (FinPred f) a (b - a) hPa (by rwa [Nat.add_sub_cancel' hab])
    have hk1n : k + 1 < n := by have := b.isLt; omega
    have hkn : k < n := by omega
    exact ⟨⟨k, hkn⟩, ⟨k + 1, hk1n⟩, Or.inl rfl, hk3 hkn, fun hf => hk4 fun _ => hf⟩
  · obtain ⟨k, -, hk2, hk3, hk4⟩ :=
      exists_step_of_not (fun m => ¬ FinPred f m) b (a - b) hPb
        (by rw [Nat.add_sub_cancel' hab.le]; exact not_not.mpr hPa)
    have hk1n : k + 1 < n := by have := a.isLt; omega
    have hk4 : FinPred f (k + 1) := not_not.mp hk4
    have hkn : k < n := by omega
    exact ⟨⟨k + 1, hk1n⟩, ⟨k, hkn⟩, Or.inr rfl, hk4 hk1n, fun hf => hk3 fun _ => hf⟩

/-- The vertex boundary of `S`: vertices outside `S` with a neighbour in `S`. -/
def gridBoundary {h w : ℕ} (S : Finset (Fin h × Fin w)) : Finset (Fin h × Fin w) :=
  Finset.univ.filter (fun u => u ∉ S ∧ ∃ s ∈ S, (grid h w).Adj s u)

theorem mem_gridBoundary {h w : ℕ} {S : Finset (Fin h × Fin w)} {u : Fin h × Fin w} :
    u ∈ gridBoundary S ↔ u ∉ S ∧ ∃ s ∈ S, (grid h w).Adj s u := by
  simp [gridBoundary]

/-- An element of `Fin w` other than `c`, when `2 ≤ w`. -/
theorem exists_ne_fin {w : ℕ} (hw : 2 ≤ w) (c : Fin w) : ∃ c' : Fin w, c' ≠ c := by
  by_cases h0 : c.val = 0
  · exact ⟨⟨1, by omega⟩, fun h => by rw [← h] at h0; simp at h0⟩
  · exact ⟨⟨0, by omega⟩, fun h => h0 (by rw [← h])⟩

/-- **Row case.** `S` has no full row and no full column, and `S ∪ {v}` has the
full row `r`. Then the boundary of `S` meets every column. -/
theorem card_gridBoundary_of_row {h w : ℕ} (hw : 2 ≤ w) (S : Finset (Fin h × Fin w))
    (v : Fin h × Fin w) (r : Fin h) (hrow : ∀ c, (r, c) ∈ insert v S)
    (hnrow : ∃ c, (r, c) ∉ S) (hncol : ∀ c, ∃ i, (i, c) ∉ S) :
    w ≤ (gridBoundary S).card := by
  obtain ⟨c0, hc0⟩ := hnrow
  have hv : v = (r, c0) := by
    have := hrow c0
    rcases Finset.mem_insert.mp this with h | h
    · exact h.symm
    · exact absurd h hc0
  have hin : ∀ c, c ≠ c0 → (r, c) ∈ S := by
    intro c hc
    rcases Finset.mem_insert.mp (hrow c) with h | h
    · rw [hv] at h; exact absurd (Prod.ext_iff.mp h).2 hc
    · exact h
  have himg : (gridBoundary S).image Prod.snd = Finset.univ := by
    apply Finset.eq_univ_of_forall
    intro c
    rw [Finset.mem_image]
    by_cases hc : c = c0
    · -- walk along row `r` from another column to `c0`
      obtain ⟨c', hc'⟩ := exists_ne_fin hw c0
      obtain ⟨k, k', hkk, hk, hk'⟩ :=
        exists_adj_step (fun j : Fin w => (r, j) ∈ S) (hin c' hc') hc0
      refine ⟨(r, k'), mem_gridBoundary.mpr ⟨hk', (r, k), hk, ?_⟩, ?_⟩
      · rw [grid_adj]; right; exact ⟨hkk, rfl⟩
      · rw [hc]; by_contra hne; exact hk' (hin k' hne)
    · obtain ⟨i, hi⟩ := hncol c
      obtain ⟨k, k', hkk, hk, hk'⟩ :=
        exists_adj_step (fun j : Fin h => (j, c) ∈ S) (hin c hc) hi
      refine ⟨(k', c), mem_gridBoundary.mpr ⟨hk', (k, c), hk, ?_⟩, rfl⟩
      rw [grid_adj]; left; exact ⟨hkk, rfl⟩
  calc w = (Finset.univ : Finset (Fin w)).card := by simp
    _ = ((gridBoundary S).image Prod.snd).card := by rw [himg]
    _ ≤ (gridBoundary S).card := Finset.card_image_le

/-- **Column case**, the transpose of the row case. -/
theorem card_gridBoundary_of_col {h w : ℕ} (hh : 2 ≤ h) (S : Finset (Fin h × Fin w))
    (v : Fin h × Fin w) (c : Fin w) (hcol : ∀ r, (r, c) ∈ insert v S)
    (hncol : ∃ r, (r, c) ∉ S) (hnrow : ∀ r, ∃ j, (r, j) ∉ S) :
    h ≤ (gridBoundary S).card := by
  obtain ⟨r0, hr0⟩ := hncol
  have hv : v = (r0, c) := by
    have := hcol r0
    rcases Finset.mem_insert.mp this with h | h
    · exact h.symm
    · exact absurd h hr0
  have hin : ∀ r, r ≠ r0 → (r, c) ∈ S := by
    intro r hr
    rcases Finset.mem_insert.mp (hcol r) with h | h
    · rw [hv] at h; exact absurd (Prod.ext_iff.mp h).1 hr
    · exact h
  have himg : (gridBoundary S).image Prod.fst = Finset.univ := by
    apply Finset.eq_univ_of_forall
    intro r
    rw [Finset.mem_image]
    by_cases hr : r = r0
    · obtain ⟨r', hr'⟩ := exists_ne_fin hh r0
      obtain ⟨k, k', hkk, hk, hk'⟩ :=
        exists_adj_step (fun i : Fin h => (i, c) ∈ S) (hin r' hr') hr0
      refine ⟨(k', c), mem_gridBoundary.mpr ⟨hk', (k, c), hk, ?_⟩, ?_⟩
      · rw [grid_adj]; left; exact ⟨hkk, rfl⟩
      · rw [hr]; by_contra hne; exact hk' (hin k' hne)
    · obtain ⟨j, hj⟩ := hnrow r
      obtain ⟨k, k', hkk, hk, hk'⟩ :=
        exists_adj_step (fun i : Fin w => (r, i) ∈ S) (hin r hr) hj
      refine ⟨(r, k'), mem_gridBoundary.mpr ⟨hk', (r, k), hk, ?_⟩, rfl⟩
      rw [grid_adj]; right; exact ⟨hkk, rfl⟩
  calc h = (Finset.univ : Finset (Fin h)).card := by simp
    _ = ((gridBoundary S).image Prod.fst).card := by rw [himg]
    _ ≤ (gridBoundary S).card := Finset.card_image_le

/-- The boundary of a prefix is contained in the active suffix there. -/
theorem gridBoundary_prefixSet_subset {h w : ℕ} (σ : LinearLayout (Fin h × Fin w)) (i : ℕ) :
    gridBoundary (prefixSet σ i) ⊆ activeSuffix (grid h w) σ i := by
  intro u hu
  rw [mem_gridBoundary] at hu
  obtain ⟨hu1, s, hs, hadj⟩ := hu
  rw [mem_activeSuffix_iff]
  rw [mem_prefixSet_iff] at hu1
  exact ⟨by omega, s, hs, hadj⟩

/-- A prefix of the layout contains a full row or a full column. -/
def HasFullLine {h w : ℕ} (σ : LinearLayout (Fin h × Fin w)) (t : ℕ) : Prop :=
  (∃ r, ∀ c, (r, c) ∈ prefixSet σ t) ∨ (∃ c, ∀ r, (r, c) ∈ prefixSet σ t)

/-- **Every layout of the grid has vertex separation at least `min h w`**
when both sides are at least `2`. -/
theorem min_le_vertexSepOfLayout_grid {h w : ℕ} (hh : 2 ≤ h) (hw : 2 ≤ w)
    (σ : LinearLayout (Fin h × Fin w)) :
    min h w ≤ vertexSepOfLayout (grid h w) σ := by
  classical
  set N := Fintype.card (Fin h × Fin w) with hN
  have hNpos : 0 < N := by
    rw [hN, Fintype.card_prod, Fintype.card_fin, Fintype.card_fin]; positivity
  have hex : ∃ t, HasFullLine σ t := by
    refine ⟨N - 1, Or.inl ⟨⟨0, by omega⟩, fun c => ?_⟩⟩
    rw [mem_prefixSet_iff]; have := (σ (⟨0, by omega⟩, c)).isLt; omega
  let t := Nat.find hex
  have ht : HasFullLine σ t := Nat.find_spec hex
  have htN : t ≤ N - 1 := Nat.find_min' hex (Or.inl ⟨⟨0, by omega⟩, fun c => by
    rw [mem_prefixSet_iff]; have := (σ (⟨0, by omega⟩, c)).isLt; omega⟩)
  -- `t ≠ 0`: a single vertex is neither a row nor a column
  have ht0 : t ≠ 0 := by
    intro h0
    rw [h0] at ht
    have two : ∀ a b : Fin h × Fin w, a ∈ prefixSet σ 0 → b ∈ prefixSet σ 0 → a = b := by
      intro a b ha hb
      rw [mem_prefixSet_iff] at ha hb
      exact σ.injective (Fin.ext (by omega))
    rcases ht with ⟨r, hr⟩ | ⟨c, hc⟩
    · have := two _ _ (hr ⟨0, by omega⟩) (hr ⟨1, by omega⟩)
      simp [Prod.ext_iff, Fin.ext_iff] at this
    · have := two _ _ (hc ⟨0, by omega⟩) (hc ⟨1, by omega⟩)
      simp [Prod.ext_iff, Fin.ext_iff] at this
  obtain ⟨s, hs⟩ : ∃ s, t = s + 1 := ⟨t - 1, by omega⟩
  have hns : ¬ HasFullLine σ s := Nat.find_min hex (by omega)
  have hsN : s < N := by omega
  set S := prefixSet σ s
  let v := σ.symm ⟨s + 1, by omega⟩
  have hsub : prefixSet σ t ⊆ insert v S := by
    intro u hu
    rw [mem_prefixSet_iff] at hu
    rw [Finset.mem_insert, mem_prefixSet_iff]
    by_cases h : (σ u).val ≤ s
    · exact Or.inr h
    · left
      apply σ.injective
      simp only [v, Equiv.apply_symm_apply]
      exact Fin.ext (show (σ u).val = s + 1 by omega)
  unfold HasFullLine at hns
  push Not at hns
  obtain ⟨hnrow, hncol⟩ := hns
  have hbd : min h w ≤ (gridBoundary S).card := by
    rcases ht with ⟨r, hr⟩ | ⟨c, hc⟩
    · exact (min_le_right _ _).trans
        (card_gridBoundary_of_row hw S v r (fun c => hsub (hr c)) (hnrow r) hncol)
    · exact (min_le_left _ _).trans
        (card_gridBoundary_of_col hh S v c (fun r => hsub (hc r)) (hncol c) hnrow)
  calc min h w ≤ (gridBoundary S).card := hbd
    _ ≤ (activeSuffix (grid h w) σ s).card :=
        Finset.card_le_card (gridBoundary_prefixSet_subset σ s)
    _ = vertexSepAt (grid h w) σ (⟨s, hsN⟩ : Fin N).val := rfl
    _ ≤ vertexSepOfLayout (grid h w) σ := vertexSepAt_le_vertexSepOfLayout _ σ ⟨s, hsN⟩

/-- **Lower bound**: `min h w ≤ pathwidth (grid h w)` when `2 ≤ h` and `2 ≤ w`. -/
theorem min_le_pathwidth_grid {h w : ℕ} (hh : 2 ≤ h) (hw : 2 ≤ w) :
    min h w ≤ pathwidth (grid h w) := by
  rw [← vertexSeparation_eq_pathwidth]
  unfold vertexSeparation
  apply le_csInf
  · exact ⟨_, ⟨Fintype.equivFin _, rfl⟩⟩
  · rintro b ⟨σ, rfl⟩
    exact min_le_vertexSepOfLayout_grid hh hw σ

/-- A graph with an edge has pathwidth at least `1`. -/
theorem one_le_pathwidth_of_adj {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (huv : G.Adj u v) :
    1 ≤ pathwidth G := by
  rw [← vertexSeparation_eq_pathwidth]
  unfold vertexSeparation
  apply le_csInf
  · exact ⟨_, ⟨Fintype.equivFin _, rfl⟩⟩
  · rintro b ⟨σ, rfl⟩
    have hne : σ u ≠ σ v := fun h => G.ne_of_adj huv (σ.injective h)
    rcases lt_or_gt_of_ne (Fin.val_ne_of_ne hne) with hlt | hlt
    · have hmem : v ∈ laterNeighbors G σ u := (mem_laterNeighbors_iff G σ u v).mpr ⟨huv, hlt⟩
      exact (Finset.card_pos.mpr ⟨v, hmem⟩).trans_le
        (card_laterNeighbors_le_vertexSepOfLayout G σ u)
    · have hmem : u ∈ laterNeighbors G σ v :=
        (mem_laterNeighbors_iff G σ v u).mpr ⟨huv.symm, hlt⟩
      exact (Finset.card_pos.mpr ⟨u, hmem⟩).trans_le
        (card_laterNeighbors_le_vertexSepOfLayout G σ v)

/-! ### The theorem -/

/-- **Ellis & Warren (2008), Theorem 4.1**: the `(h, w)`-grid has pathwidth
`min h w`, for every `h` and `w` except `h = w = 1` (a single vertex, of
pathwidth `0`, `pathwidth_grid_one_one`). Empty grids (`h = 0` or `w = 0`) are
included, with pathwidth `0`. -/
theorem pathwidth_grid (h w : ℕ) (hhw : ¬ (h = 1 ∧ w = 1)) :
    pathwidth (grid h w) = min h w := by
  apply le_antisymm (pathwidth_grid_le h w)
  rcases Nat.lt_or_ge h 2 with hh | hh
  · rcases Nat.lt_or_ge w 2 with hw | hw
    · -- `h, w ≤ 1`, not both `1`: one of them is `0`
      have : h = 0 ∨ w = 0 := by omega
      rcases this with h0 | w0 <;> simp [*]
    · obtain rfl | rfl : h = 0 ∨ h = 1 := by omega
      · simp
      · rw [min_eq_left (by omega)]
        exact one_le_pathwidth_of_adj (grid 1 w) (u := (0, ⟨0, by omega⟩))
          (v := (0, ⟨1, by omega⟩)) (by rw [grid_adj]; right; exact ⟨Or.inl rfl, rfl⟩)
  · rcases Nat.lt_or_ge w 2 with hw | hw
    · obtain rfl | rfl : w = 0 ∨ w = 1 := by omega
      · simp
      · rw [min_eq_right (by omega)]
        exact one_le_pathwidth_of_adj (grid h 1) (u := (⟨0, by omega⟩, 0))
          (v := (⟨1, by omega⟩, 0)) (by rw [grid_adj]; left; exact ⟨Or.inl rfl, rfl⟩)
    · exact min_le_pathwidth_grid hh hw

/-- The exception: the `1 × 1` grid is a single vertex, of pathwidth `0`. -/
theorem pathwidth_grid_one_one : pathwidth (grid 1 1) = 0 := by
  have := pathwidth_le_card_sub_one (grid 1 1)
  simp at this
  omega

/-- The square grid: `pathwidth (grid n n) = n` for `n ≠ 1`. -/
theorem pathwidth_grid_square (n : ℕ) (hn : n ≠ 1) : pathwidth (grid n n) = n := by
  rw [pathwidth_grid n n (fun h => hn h.1), min_self]

end MOSPFormalization
