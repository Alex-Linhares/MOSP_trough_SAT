/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The first-moment count on random clique covers: the Chu & Stuckey model

`FirstMoment.lean` counts the labelled graphs of pathwidth at most `k` on `n`
vertices. The benchmark generators do not draw graphs: they draw *patterns*,
each an independent uniformly random set of customers of a given size, and the
MOSP graph is the union of those cliques (`reports/scratch/clique_cover_moment/`).
This file redoes the count in that model, in the repository's own MOSP
vocabulary: a *cover* is a function `S : Fin m → Finset C` with `|S j| = s j`
for a size vector `s`; its instance is the `MOSPInstance` with
`requires c j ↔ c ∈ S j`, and its graph is the `mospGraph` of that instance.

Checked by brute force first (`reports/scratch/clique_cover_moment/lean_check.py`,
2026-10-31): every cover for `n ≤ 6` customers, `m ≤ 3` patterns and sizes
`≤ 3`, pathwidth by the subset DP and the MOSP value by brute force over pattern
orders, every `k < n`: zero violations in 1,604 cases of the count, the
probability form and the MOSP form; `avoidCount` exact against enumeration for
every disjoint `(A, R)` and every `s` at `n ≤ 6` (7,107 cases).

## The argument

Write `n = |C|`, `t = (n − k + 1) / 2 = ⌈(n − k)/2⌉`. By `exists_empty_pair`
(`EmptyPair.lean`) a cover whose graph has pathwidth `≤ k < n` has an empty
pair `(A, R)`, `|A| = t`, `|R| = t − 1`, and a pair is empty iff **no pattern
meets both sides** (a pattern meeting both contains an edge between them). The
patterns are chosen independently, so the covers with a given empty pair form a
product set whose factor for a pattern of size `s` has

  `N(s) = C(n − t, s) + C(n − t + 1, s) − C(n − 2t + 1, s)`

elements, by inclusion–exclusion over "avoids `A`", "avoids `R`", "avoids both".
The union bound over the `n.choose t · (n − t).choose (t − 1)` pairs gives

  `#{S : pathwidth (mospGraph S) ≤ k} ≤ n.choose t · (n − t).choose (t − 1) · ∏_j N(s_j)`,

and dividing by the number of covers `∏_j n.choose (s_j)` gives the probability
form of `finite_bound_cs.py`, `P(pw ≤ k) ≤ C(n,t)·C(n−t,t−1)·∏_j q(s_j)` with
`q(s) = N(s) / C(n, s)`.

A note on the formula in `ℕ`: `n − 2t + 1` read with truncated subtraction is
wrong at `2t = n + 1` (which is `k = 0` with `n` odd), so `avoidCount` is stated for
sides of sizes `a` and `r` as `C(n − a, s) + C(n − r, s) − C(n − (a + r), s)`,
and `avoidCount_eq` restates it in the form above as `C(n + 1 − 2t, s)`.

## Main results

* `covers s` — the covers with size vector `s`, as `Fintype.piFinset`;
  `card_covers`: there are `∏_j n.choose (s j)` of them.
* `coverInstance S`, `coverGraph S` — the instance and MOSP graph of a cover;
  `coverGraph_adj`: adjacent iff distinct and in a common pattern.
* `isEmptyPair_coverGraph_iff` — for disjoint `A`, `R`: `(A, R)` is an empty
  pair of the cover's graph iff every pattern is disjoint from `A` or from `R`.
* `avoidCount n a r s`; `card_filter_avoid` — **the `s`-subsets of `C` disjoint
  from `A` or from `R` number `avoidCount n |A| |R| s`**; `avoidCount_eq` — the
  README's form at `a = t`, `r = t − 1`.
* `emptyPairCovers s A R`, `card_emptyPairCovers` — the covers in which no
  pattern meets both sides, `∏_j avoidCount n |A| |R| (s j)` of them.
* `card_coversOfPathwidthLe_le` — **the first-moment count**: for `k < n`,
  `#{S ∈ covers s : pathwidth (coverGraph S) ≤ k} ≤ n.choose t · (n − t).choose (t − 1) · ∏_j avoidCount n t (t − 1) (s j)`.
* `prob_coversOfPathwidthLe_le` — **the probability form**, over `ℝ`:
  `#{…} / ∏_j n.choose (s j) ≤ n.choose t · (n − t).choose (t − 1) · ∏_j (avoidCount n t (t − 1) (s j) / n.choose (s j))`.
* `coversOfMospValueLe_eq_coversOfPathwidthLe` — with `m ≥ 1` and every
  `s j ≥ 1` (so some customer requires some pattern), `mospValue ≤ k + 1` and
  `pathwidth ≤ k` cut out the same covers (`mospValue_eq_pathwidth_add_one`);
  `card_coversOfMospValueLe_le`, `prob_coversOfMospValueLe_le` — **the MOSP
  reading** of both bounds.

No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only.
-/

import MOSPFormalization.FirstMoment
import MOSPFormalization.MOSPGraph
import Mathlib.Data.Fintype.BigOperators

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open Finset

variable {C : Type*} [Fintype C] [DecidableEq C] {m : ℕ}

/-! ### Covers and their instances -/

/-- The clique covers with size vector `s`: one `s j`-subset of the customers per
pattern `j`. -/
def covers (s : Fin m → ℕ) : Finset (Fin m → Finset C) :=
  Fintype.piFinset (fun j => (univ : Finset C).powersetCard (s j))

theorem mem_covers {s : Fin m → ℕ} {S : Fin m → Finset C} :
    S ∈ covers s ↔ ∀ j, (S j).card = s j := by
  simp [covers, Fintype.mem_piFinset, mem_powersetCard]

/-- **The number of covers** with size vector `s` is `∏_j n.choose (s j)`. -/
theorem card_covers (s : Fin m → ℕ) :
    (covers (C := C) s).card = ∏ j, (Fintype.card C).choose (s j) := by
  simp [covers, Fintype.card_piFinset, card_powersetCard, card_univ]

/-- The MOSP instance of a cover: customer `c` requires pattern `j` iff `c ∈ S j`. -/
def coverInstance (S : Fin m → Finset C) : MOSPInstance C (Fin m) :=
  ⟨fun c j => c ∈ S j⟩

instance (S : Fin m → Finset C) : DecidableRel (coverInstance S).requires :=
  fun c j => inferInstanceAs (Decidable (c ∈ S j))

theorem coverInstance_requires {S : Fin m → Finset C} {c : C} {j : Fin m} :
    (coverInstance S).requires c j ↔ c ∈ S j := Iff.rfl

/-- The graph of a cover: the MOSP graph of its instance, customers adjacent iff
some pattern contains both. -/
abbrev coverGraph (S : Fin m → Finset C) : SimpleGraph C :=
  (coverInstance S).mospGraph

theorem coverGraph_adj {S : Fin m → Finset C} {u v : C} :
    (coverGraph S).Adj u v ↔ u ≠ v ∧ ∃ j, u ∈ S j ∧ v ∈ S j := Iff.rfl

/-! ### Empty pairs of a cover -/

/-- For disjoint `A`, `R`: `(A, R)` is an empty pair of the cover's graph iff no
pattern meets both sides. -/
theorem isEmptyPair_coverGraph_iff {S : Fin m → Finset C} {A R : Finset C}
    (hAR : Disjoint A R) :
    IsEmptyPair (coverGraph S) A R ↔ ∀ j, Disjoint (S j) A ∨ Disjoint (S j) R := by
  constructor
  · intro h j
    by_contra hc
    rw [not_or, Finset.not_disjoint_iff, Finset.not_disjoint_iff] at hc
    obtain ⟨⟨a, haS, haA⟩, ⟨r, hrS, hrR⟩⟩ := hc
    exact h a haA r hrR
      ⟨fun hne => Finset.disjoint_left.1 hAR haA (hne ▸ hrR), j, haS, hrS⟩
  · intro h a ha r hr hadj
    obtain ⟨_, j, haS, hrS⟩ := hadj
    rcases h j with hj | hj
    · exact Finset.disjoint_left.1 hj haS ha
    · exact Finset.disjoint_left.1 hj hrS hr

/-! ### Counting the patterns that avoid a side -/

/-- The `s`-subsets of the customers disjoint from `A`: `(n − |A|).choose s` of them. -/
theorem card_powersetCard_filter_disjoint (A : Finset C) (s : ℕ) :
    (((univ : Finset C).powersetCard s).filter (fun T => Disjoint T A)).card =
      (Fintype.card C - A.card).choose s := by
  have h : ((univ : Finset C).powersetCard s).filter (fun T => Disjoint T A) =
      (univ \ A).powersetCard s := by
    ext T
    rw [mem_filter, mem_powersetCard, mem_powersetCard, subset_sdiff]
    constructor
    · rintro ⟨⟨_, hc⟩, hd⟩
      exact ⟨⟨subset_univ T, hd⟩, hc⟩
    · rintro ⟨⟨_, hd⟩, hc⟩
      exact ⟨⟨subset_univ T, hc⟩, hd⟩
  rw [h, card_powersetCard, card_univ_sdiff]

/-- `N(s)` for sides of sizes `a` and `r`: the number of `s`-subsets of an `n`-set
that avoid a given `a`-set or a given disjoint `r`-set,
`C(n − a, s) + C(n − r, s) − C(n − (a + r), s)`. -/
def avoidCount (n a r s : ℕ) : ℕ :=
  (n - a).choose s + (n - r).choose s - (n - (a + r)).choose s

/-- The README's form at `a = t`, `r = t − 1`:
`N(s) = C(n − t, s) + C(n − t + 1, s) − C(n − 2t + 1, s)`, the last two written
`n + 1 − t` and `n + 1 − 2t` so that they are right in `ℕ`. -/
theorem avoidCount_eq {n t s : ℕ} (ht : 1 ≤ t) :
    avoidCount n t (t - 1) s =
      (n - t).choose s + (n + 1 - t).choose s - (n + 1 - 2 * t).choose s := by
  unfold avoidCount
  have h1 : n - (t - 1) = n + 1 - t := by omega
  have h2 : n - (t + (t - 1)) = n + 1 - 2 * t := by omega
  rw [h1, h2]

/-- **Inclusion–exclusion**: the `s`-subsets disjoint from `A` or from `R` number
`avoidCount n |A| |R| s`, for disjoint `A`, `R`. -/
theorem card_filter_avoid {A R : Finset C} (hAR : Disjoint A R) (s : ℕ) :
    (((univ : Finset C).powersetCard s).filter
        (fun T => Disjoint T A ∨ Disjoint T R)).card =
      avoidCount (Fintype.card C) A.card R.card s := by
  set X := ((univ : Finset C).powersetCard s).filter (fun T => Disjoint T A) with hX
  set Y := ((univ : Finset C).powersetCard s).filter (fun T => Disjoint T R) with hY
  have hunion : ((univ : Finset C).powersetCard s).filter
      (fun T => Disjoint T A ∨ Disjoint T R) = X ∪ Y := by
    ext T
    simp only [hX, hY, mem_union, mem_filter]
    tauto
  have hinter : X ∩ Y =
      ((univ : Finset C).powersetCard s).filter (fun T => Disjoint T (A ∪ R)) := by
    ext T
    simp only [hX, hY, mem_inter, mem_filter, disjoint_union_right]
    tauto
  have h := card_union_add_card_inter X Y
  have hXc : X.card = (Fintype.card C - A.card).choose s :=
    card_powersetCard_filter_disjoint A s
  have hYc : Y.card = (Fintype.card C - R.card).choose s :=
    card_powersetCard_filter_disjoint R s
  have hIc : (X ∩ Y).card = (Fintype.card C - (A.card + R.card)).choose s := by
    rw [hinter, card_powersetCard_filter_disjoint, card_union_of_disjoint hAR]
  rw [hunion]
  unfold avoidCount
  omega

/-! ### The covers with a given empty pair -/

/-- The covers with size vector `s` in which no pattern meets both `A` and `R`. -/
def emptyPairCovers (s : Fin m → ℕ) (A R : Finset C) : Finset (Fin m → Finset C) :=
  Fintype.piFinset (fun j => ((univ : Finset C).powersetCard (s j)).filter
    (fun T => Disjoint T A ∨ Disjoint T R))

theorem mem_emptyPairCovers {s : Fin m → ℕ} {A R : Finset C} {S : Fin m → Finset C} :
    S ∈ emptyPairCovers s A R ↔
      (∀ j, (S j).card = s j) ∧ ∀ j, Disjoint (S j) A ∨ Disjoint (S j) R := by
  simp only [emptyPairCovers, Fintype.mem_piFinset, mem_filter, mem_powersetCard,
    subset_univ, true_and]
  exact forall_and

/-- **The covers with a given empty pair**: `∏_j avoidCount n |A| |R| (s j)`, the
patterns being independent. -/
theorem card_emptyPairCovers (s : Fin m → ℕ) {A R : Finset C} (hAR : Disjoint A R) :
    (emptyPairCovers s A R).card =
      ∏ j, avoidCount (Fintype.card C) A.card R.card (s j) := by
  unfold emptyPairCovers
  rw [Fintype.card_piFinset]
  exact Finset.prod_congr rfl (fun j _ => card_filter_avoid hAR (s j))

/-! ### The union bound -/

/-- The covers with size vector `s` whose graph has pathwidth at most `k`. -/
noncomputable def coversOfPathwidthLe (s : Fin m → ℕ) (k : ℕ) : Finset (Fin m → Finset C) := by
  classical exact (covers s).filter (fun S => pathwidth (coverGraph S) ≤ k)

theorem mem_coversOfPathwidthLe {s : Fin m → ℕ} {k : ℕ} {S : Fin m → Finset C} :
    S ∈ coversOfPathwidthLe s k ↔ S ∈ covers s ∧ pathwidth (coverGraph S) ≤ k := by
  simp [coversOfPathwidthLe]

/-- Every cover of pathwidth `≤ k < n` lies in the set of some pair `(A, R)` with
`|A| = t`, `|R| = t − 1`, `t = (n − k + 1) / 2`: by `exists_empty_pair`, shrinking
the pair, and `isEmptyPair_coverGraph_iff`. -/
theorem mem_biUnion_emptyPairCovers {s : Fin m → ℕ} {k : ℕ} (hk : k < Fintype.card C)
    {S : Fin m → Finset C} (hS : S ∈ covers s) (hpw : pathwidth (coverGraph S) ≤ k) :
    S ∈ (emptyPairIndices ((Fintype.card C - k + 1) / 2)).biUnion
      (fun p => emptyPairCovers s p.1 p.2) := by
  obtain ⟨A, R, hAR, hedge, hA, hR⟩ := exists_empty_pair (coverGraph S) (by omega)
  obtain ⟨A', hA'A, hA'⟩ := Finset.exists_subset_card_eq
    (s := A) (n := (Fintype.card C - k + 1) / 2) (by omega)
  obtain ⟨R', hR'R, hR'⟩ := Finset.exists_subset_card_eq
    (s := R) (n := (Fintype.card C - k + 1) / 2 - 1) (by omega)
  have hAR' : Disjoint A' R' :=
    Finset.disjoint_of_subset_left hA'A (Finset.disjoint_of_subset_right hR'R hAR)
  rw [mem_biUnion]
  refine ⟨⟨A', R'⟩, mem_emptyPairIndices.2 ⟨hA', ?_, hR'⟩, ?_⟩
  · intro r hr
    rw [mem_sdiff]
    exact ⟨mem_univ r, fun hrA => Finset.disjoint_left.1 hAR' hrA hr⟩
  · rw [mem_emptyPairCovers]
    refine ⟨mem_covers.1 hS, ?_⟩
    exact (isEmptyPair_coverGraph_iff hAR').1
      (fun a ha r hr => hedge a (hA'A ha) r (hR'R hr))

/-- **The first-moment count on clique covers.** For `k < n = |C|` and
`t = (n − k + 1) / 2`,
`#{S ∈ covers s : pathwidth (coverGraph S) ≤ k} ≤
  n.choose t · (n − t).choose (t − 1) · ∏_j avoidCount n t (t − 1) (s j)`. -/
theorem card_coversOfPathwidthLe_le (s : Fin m → ℕ) (k : ℕ) (hk : k < Fintype.card C) :
    (coversOfPathwidthLe (C := C) s k).card ≤
      (Fintype.card C).choose ((Fintype.card C - k + 1) / 2) *
        (Fintype.card C - (Fintype.card C - k + 1) / 2).choose
          ((Fintype.card C - k + 1) / 2 - 1) *
        ∏ j, avoidCount (Fintype.card C) ((Fintype.card C - k + 1) / 2)
          ((Fintype.card C - k + 1) / 2 - 1) (s j) := by
  classical
  set t := (Fintype.card C - k + 1) / 2 with ht
  calc (coversOfPathwidthLe (C := C) s k).card
      ≤ ((emptyPairIndices t).biUnion (fun p => emptyPairCovers s p.1 p.2)).card :=
        card_le_card (fun S hS => by
          obtain ⟨h1, h2⟩ := mem_coversOfPathwidthLe.1 hS
          exact mem_biUnion_emptyPairCovers hk h1 h2)
    _ ≤ (emptyPairIndices (V := C) t).card *
          ∏ j, avoidCount (Fintype.card C) t (t - 1) (s j) := by
        refine card_biUnion_le_card_mul _ _ _ (fun p hp => ?_)
        obtain ⟨hA, _, hR⟩ := mem_emptyPairIndices.1 hp
        rw [card_emptyPairCovers s (disjoint_of_mem_emptyPairIndices hp), hA, hR]
    _ = _ := by rw [card_emptyPairIndices]

/-! ### The probability form -/

/-- **The first-moment bound on random clique covers**, over `ℝ`: with every
cover of size vector `s` equally likely, `k < n = |C|`, `t = (n − k + 1) / 2`,
`q(s) = avoidCount n t (t − 1) s / n.choose s`,
`P(pathwidth (coverGraph S) ≤ k) ≤ n.choose t · (n − t).choose (t − 1) · ∏_j q(s j)`,
the inequality of `reports/scratch/clique_cover_moment/finite_bound_cs.py`. -/
theorem prob_coversOfPathwidthLe_le (s : Fin m → ℕ) (k : ℕ) (hk : k < Fintype.card C) :
    ((coversOfPathwidthLe (C := C) s k).card : ℝ) /
        ∏ j, ((Fintype.card C).choose (s j) : ℝ) ≤
      (((Fintype.card C).choose ((Fintype.card C - k + 1) / 2) *
        (Fintype.card C - (Fintype.card C - k + 1) / 2).choose
          ((Fintype.card C - k + 1) / 2 - 1) : ℕ) : ℝ) *
        ∏ j, ((avoidCount (Fintype.card C) ((Fintype.card C - k + 1) / 2)
          ((Fintype.card C - k + 1) / 2 - 1) (s j) : ℝ) /
            ((Fintype.card C).choose (s j) : ℝ)) := by
  have h := card_coversOfPathwidthLe_le s k hk
  have hP : 0 ≤ ∏ j, ((Fintype.card C).choose (s j) : ℝ) :=
    prod_nonneg (fun j _ => Nat.cast_nonneg _)
  calc ((coversOfPathwidthLe (C := C) s k).card : ℝ) /
        ∏ j, ((Fintype.card C).choose (s j) : ℝ)
      ≤ (((Fintype.card C).choose ((Fintype.card C - k + 1) / 2) *
          (Fintype.card C - (Fintype.card C - k + 1) / 2).choose
            ((Fintype.card C - k + 1) / 2 - 1) *
          ∏ j, avoidCount (Fintype.card C) ((Fintype.card C - k + 1) / 2)
            ((Fintype.card C - k + 1) / 2 - 1) (s j) : ℕ) : ℝ) /
          ∏ j, ((Fintype.card C).choose (s j) : ℝ) :=
        div_le_div_of_nonneg_right (by exact_mod_cast h) hP
    _ = _ := by
        rw [prod_div_distrib]
        push_cast
        ring

/-! ### The MOSP reading -/

/-- The covers with size vector `s` whose instance has MOSP value at most `k`. -/
noncomputable def coversOfMospValueLe (s : Fin m → ℕ) (k : ℕ) : Finset (Fin m → Finset C) := by
  classical exact (covers s).filter (fun S => (coverInstance S).mospValue ≤ k)

theorem mem_coversOfMospValueLe {s : Fin m → ℕ} {k : ℕ} {S : Fin m → Finset C} :
    S ∈ coversOfMospValueLe s k ↔ S ∈ covers s ∧ (coverInstance S).mospValue ≤ k := by
  simp [coversOfMospValueLe]

/-- With at least one pattern and no empty pattern, some customer requires some
pattern in every cover, the hypothesis of `mospValue_eq_pathwidth_add_one`. -/
theorem exists_requires_of_mem_covers {s : Fin m → ℕ} (hm : 0 < m) (hs : ∀ j, 1 ≤ s j)
    {S : Fin m → Finset C} (hS : S ∈ covers s) :
    ∃ c p, (coverInstance S).requires c p := by
  have hcard : 0 < (S ⟨0, hm⟩).card := by
    rw [mem_covers.1 hS ⟨0, hm⟩]
    exact hs _
  obtain ⟨c, hc⟩ := Finset.card_pos.1 hcard
  exact ⟨c, ⟨0, hm⟩, hc⟩

/-- `mospValue ≤ k + 1` and `pathwidth ≤ k` cut out the same covers, by Yanasse's
equality, when `m ≥ 1` and every pattern is nonempty. -/
theorem coversOfMospValueLe_eq_coversOfPathwidthLe {s : Fin m → ℕ} (hm : 0 < m)
    (hs : ∀ j, 1 ≤ s j) (k : ℕ) :
    coversOfMospValueLe (C := C) s (k + 1) = coversOfPathwidthLe s k := by
  ext S
  rw [mem_coversOfMospValueLe, mem_coversOfPathwidthLe]
  constructor
  · rintro ⟨hS, h⟩
    refine ⟨hS, ?_⟩
    rw [(coverInstance S).mospValue_eq_pathwidth_add_one
      (exists_requires_of_mem_covers hm hs hS)] at h
    exact Nat.le_of_add_le_add_right h
  · rintro ⟨hS, h⟩
    refine ⟨hS, ?_⟩
    rw [(coverInstance S).mospValue_eq_pathwidth_add_one
      (exists_requires_of_mem_covers hm hs hS)]
    exact Nat.add_le_add_right h 1

/-- **The first-moment count, MOSP reading.** With `m ≥ 1`, every `s j ≥ 1` and
`k < n = |C|`, `t = (n − k + 1) / 2`,
`#{S ∈ covers s : mospValue (coverInstance S) ≤ k + 1} ≤
  n.choose t · (n − t).choose (t − 1) · ∏_j avoidCount n t (t − 1) (s j)`. -/
theorem card_coversOfMospValueLe_le (s : Fin m → ℕ) (hm : 0 < m) (hs : ∀ j, 1 ≤ s j)
    (k : ℕ) (hk : k < Fintype.card C) :
    (coversOfMospValueLe (C := C) s (k + 1)).card ≤
      (Fintype.card C).choose ((Fintype.card C - k + 1) / 2) *
        (Fintype.card C - (Fintype.card C - k + 1) / 2).choose
          ((Fintype.card C - k + 1) / 2 - 1) *
        ∏ j, avoidCount (Fintype.card C) ((Fintype.card C - k + 1) / 2)
          ((Fintype.card C - k + 1) / 2 - 1) (s j) := by
  rw [coversOfMospValueLe_eq_coversOfPathwidthLe hm hs]
  exact card_coversOfPathwidthLe_le s k hk

/-- **The first-moment bound, MOSP reading**, over `ℝ`: the probability that a
uniformly random cover of size vector `s` has MOSP value at most `k + 1`. -/
theorem prob_coversOfMospValueLe_le (s : Fin m → ℕ) (hm : 0 < m) (hs : ∀ j, 1 ≤ s j)
    (k : ℕ) (hk : k < Fintype.card C) :
    ((coversOfMospValueLe (C := C) s (k + 1)).card : ℝ) /
        ∏ j, ((Fintype.card C).choose (s j) : ℝ) ≤
      (((Fintype.card C).choose ((Fintype.card C - k + 1) / 2) *
        (Fintype.card C - (Fintype.card C - k + 1) / 2).choose
          ((Fintype.card C - k + 1) / 2 - 1) : ℕ) : ℝ) *
        ∏ j, ((avoidCount (Fintype.card C) ((Fintype.card C - k + 1) / 2)
          ((Fintype.card C - k + 1) / 2 - 1) (s j) : ℝ) /
            ((Fintype.card C).choose (s j) : ℝ)) := by
  rw [coversOfMospValueLe_eq_coversOfPathwidthLe hm hs]
  exact prob_coversOfPathwidthLe_le s k hk

end MOSPFormalization
