/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The blow-up bound: MOSP against the pathwidth of the incidence graph

Item 06 of `reports/excess_phase_plan.md` (`reports/excess_phase_diagram.md` §6) proved on
paper, for every MOSP instance, that

  `mospValue M ≤ ω · (pathwidth (incidence M) + 1)`,

where the *incidence graph* has the customers and the patterns as vertices, a customer
adjacent to each pattern it requires, and `ω` is the largest number of customers on one
pattern. The forest hypothesis of the item's title buys only the second step: when the
incidence graph is acyclic its components are trees on at most `n + m` vertices, so
`TreeBound.lean`'s size bound gives `pathwidth (incidence M) ≤ tb (n + m)` with
`tb N = ⌊log₃((6N + 3)/5)⌋`, the least `k` with `N ≤ treeBound k`.

Checked before it was stated (item 06, `reports/scratch/forest_check/`): zero violations on
4,410 record rows with both pathwidths exact, 594 depth-one block graphs and 2,000 random
instances, 1,799 of them not forests; and again for this file on the 3,448 forest instances
on record (`learning/sandwich.py --stage forest`, `reports/scratch/forest_cover/`).

## The construction (`blowUp`)

From a path decomposition `D` of the incidence graph, the bag `i` of the MOSP graph is
*the customers in `D.bag i` together with the customers of every pattern in `D.bag i`*
(`blowBag`). A pattern's customers are a clique and all enter with the pattern, so every
edge of the MOSP graph is covered by any bag holding the pattern. The interval property is
the union-of-intervals lemma of §6.2: a customer `c` appears through `inl c` or through one
of its patterns `inr p`, every one of those vertices shares a bag with `inl c` (edge coverage
in `D`), and a union of intervals each meeting a common interval is an interval
(`PathDecomposition.mem_bag_of_meet`, the three-way case split on the meeting bags). The bag
has at most `a + b·ω ≤ (a + b)·ω ≤ (width + 1)·ω` customers, where `a` customers and `b`
patterns sit in `D.bag i`.

## Main results

* `incidence M : SimpleGraph (C ⊕ Pt)` — `Adj (inl c) (inr p) ↔ M.requires c p`, symmetric,
  nothing else (`incidence_adj_inl_inr`, `incidence_adj_inr_inl`, `incidence_not_adj_inl_inl`,
  `incidence_not_adj_inr_inr`).
* `maxPatternSize M` — `ω`; `one_le_maxPatternSize_iff`: `1 ≤ ω ↔ ∃ c p, M.requires c p`.
* `blowUp D : PathDecomposition M.mospGraph` with `blowUp_width_add_one_le`:
  `(blowUp D).width + 1 ≤ (D.width + 1) · ω` when `1 ≤ ω`.
* `pathwidth_mospGraph_add_one_le` — **(L2)** `pathwidth M.mospGraph + 1 ≤ (pathwidth (incidence M) + 1) · ω`
  when `1 ≤ ω`; `mospValue_le_maxPatternSize_mul` — **F1 in MOSP terms, no hypothesis**:
  `mospValue M ≤ ω · (pathwidth (incidence M) + 1)`.
* `treeBoundInv N = Nat.log 3 ((6N + 3) / 5)` with `le_treeBound_treeBoundInv`
  (`N ≤ treeBound (treeBoundInv N)`) and `treeBound_lt_of_lt_treeBoundInv` (it is the least
  such `k`): Lemma 5 of §6.2 as an integer identity.
* `pathwidth_le_treeBoundInv_of_isAcyclic` — **(L3)** every forest on `N` vertices has
  pathwidth at most `treeBoundInv N` (per component through
  `pathwidth_induce_le_of_forall_connected` and `tree_pathwidth_le_treeBound`).
* `mospValue_le_of_incidence_isAcyclic` — **(L4), F1′**:
  `(incidence M).IsAcyclic → mospValue M ≤ ω · (treeBoundInv (|C| + |Pt|) + 1)`.

## The layer lemma (item 07, Lemma L)

* `IsLayering G lvl` — adjacent vertices at most one level apart; `layer lvl i` the vertices at
  level `i`; `layerWidth lvl h = max_{i ≤ h} (|L_i| + |L_{i+1}|)`.
* `layerDecomposition` — bags `L_i ∪ L_{i+1}`; `pathwidth_le_layerWidth` — **(b)**
  `pathwidth G ≤ layerWidth lvl h − 1` for any layering with levels `≤ h`;
  `vertexSeparation_le_layerWidth` the same through `vertexSeparation_eq_pathwidth`;
  `isLayering_dist` — BFS distance from a root of a connected graph is a layering;
  `pathwidth_le_layerWidth_dist` — the BFS form of §7.1. The statement is about the graph's
  pathwidth, not about the vertex separation of the layer-by-layer layout itself (which
  `DecompositionToLayout.lean` would realise from the decomposition).

## The coupling inclusion (item 10, Lemma V2)

* `isEmptyPair_anti` — an empty pair of a graph is an empty pair of every subgraph on the
  same vertices; `coverGraph_mono` — a pointwise larger cover has a larger graph;
  `isEmptyPair_coverGraph_of_subset` — **(c)**: an empty pair of `coverGraph S'` is one of
  `coverGraph S` whenever `S j ⊆ S' j` for every `j`; `pathwidth_coverGraph_mono` — and the
  pathwidth is monotone the other way (`pathwidth_mono` of `Minor.lean`).
* `mospGraph_mono`, `mospValue_mono` — Yanasse (1997a) Proposition 2, subinstance
  monotonicity: `(∀ c p, M.requires c p → M'.requires c p) → mospValue M ≤ mospValue M'`,
  with no hypothesis (through `mospValue_le_pathwidth_add_one` and
  `pathwidth_add_one_le_mospValue`, and `mospValue_eq_zero_of_forall_not` when `M` is empty).

No `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` only
(`paper1/axiom_check.lean`).
-/

import MOSPFormalization.TreeBound
import MOSPFormalization.CliqueCoverMoment
import Mathlib.Data.Fintype.Sum

set_option linter.unusedSectionVars false

namespace MOSPFormalization

/-! ### A graph-level lemma: a union of intervals meeting a common interval is an interval -/

section Graph

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V}

namespace PathDecomposition

/-- Three vertices `x`, `y`, `z` of a path decomposition with `x ∈ bag i`, `y ∈ bag k`,
`x` and `z` together in some bag `l`, `y` and `z` together in some bag `l'`: then for
`i ≤ j ≤ k` one of the three is in `bag j`. (If `j` lies between `l` and `l'`, it is `z`;
if `j` is before both, `x`; if after both, `y`.) -/
theorem mem_bag_of_meet (D : PathDecomposition G) {x y z : V}
    {i j k l l' : Fin (D.length + 1)} (hij : i ≤ j) (hjk : j ≤ k)
    (hxi : x ∈ D.bag i) (hyk : y ∈ D.bag k) (hxl : x ∈ D.bag l) (hzl : z ∈ D.bag l)
    (hyl : y ∈ D.bag l') (hzl' : z ∈ D.bag l') :
    x ∈ D.bag j ∨ y ∈ D.bag j ∨ z ∈ D.bag j := by
  rcases le_or_gt l j with hlj | hjl
  · rcases le_or_gt j l' with hjl' | hl'j
    · exact Or.inr (Or.inr (D.interval z l j l' hlj hjl' hzl hzl'))
    · exact Or.inr (Or.inl (D.interval y l' j k hl'j.le hjk hyl hyk))
  · rcases le_or_gt l' j with hl'j | hjl'
    · exact Or.inr (Or.inr (D.interval z l' j l hl'j hjl.le hzl' hzl))
    · exact Or.inl (D.interval x i j l hij hjl.le hxi hxl)

end PathDecomposition

/-- An empty pair of `G'` is an empty pair of every `G ≤ G'` on the same vertices. -/
theorem isEmptyPair_anti {G G' : SimpleGraph V} (hG : G ≤ G') {A R : Finset V}
    (h : IsEmptyPair G' A R) : IsEmptyPair G A R :=
  fun a ha r hr hadj => h a ha r hr (hG hadj)

end Graph

/-! ### The incidence graph and the largest pattern -/

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]

namespace MOSPInstance

variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- The **incidence graph** of an instance: customers and patterns as vertices, a customer
adjacent to each pattern it requires, and no other edges. -/
def incidence : SimpleGraph (C ⊕ Pt) where
  Adj x y :=
    match x, y with
    | Sum.inl c, Sum.inr p => M.requires c p
    | Sum.inr p, Sum.inl c => M.requires c p
    | _, _ => False
  symm := ⟨fun x y h => by cases x <;> cases y <;> exact h⟩
  loopless := ⟨fun x h => by cases x <;> exact h⟩

@[simp] theorem incidence_adj_inl_inr (c : C) (p : Pt) :
    M.incidence.Adj (Sum.inl c) (Sum.inr p) ↔ M.requires c p := Iff.rfl

@[simp] theorem incidence_adj_inr_inl (p : Pt) (c : C) :
    M.incidence.Adj (Sum.inr p) (Sum.inl c) ↔ M.requires c p := Iff.rfl

@[simp] theorem incidence_not_adj_inl_inl (c d : C) :
    ¬ M.incidence.Adj (Sum.inl c) (Sum.inl d) := fun h => h

@[simp] theorem incidence_not_adj_inr_inr (p q : Pt) :
    ¬ M.incidence.Adj (Sum.inr p) (Sum.inr q) := fun h => h

/-- `ω`: the largest number of customers on one pattern (the clique size of the largest
pattern clique of the MOSP graph). -/
def maxPatternSize : ℕ := Finset.univ.sup (fun p => (M.customers p).card)

theorem card_customers_le_maxPatternSize (p : Pt) :
    (M.customers p).card ≤ M.maxPatternSize :=
  Finset.le_sup (f := fun p => (M.customers p).card) (Finset.mem_univ p)

theorem one_le_maxPatternSize_iff : 1 ≤ M.maxPatternSize ↔ ∃ c p, M.requires c p := by
  constructor
  · intro h
    by_contra hno
    push Not at hno
    have hzero : M.maxPatternSize ≤ 0 := by
      apply Finset.sup_le
      intro p _
      have : M.customers p = ∅ := by
        ext c
        simp [mem_customers_iff, hno c p]
      simp [this]
    omega
  · rintro ⟨c, p, hcp⟩
    have hc : c ∈ M.customers p := (M.mem_customers_iff p c).mpr hcp
    have : 1 ≤ (M.customers p).card := Finset.card_pos.mpr ⟨c, hc⟩
    exact this.trans (M.card_customers_le_maxPatternSize p)

theorem forall_not_requires_of_maxPatternSize_eq_zero (h : M.maxPatternSize = 0) :
    ∀ c p, ¬ M.requires c p := by
  by_contra hcon
  push Not at hcon
  have := (M.one_le_maxPatternSize_iff).mpr hcon
  omega

/-! ### The blow-up of a path decomposition of the incidence graph -/

variable (D : PathDecomposition M.incidence)

/-- The customers of `D.bag i` in the incidence graph. -/
def bagCustomers (i : Fin (D.length + 1)) : Finset C :=
  Finset.univ.filter (fun c => Sum.inl c ∈ D.bag i)

/-- The patterns of `D.bag i` in the incidence graph. -/
def bagPatterns (i : Fin (D.length + 1)) : Finset Pt :=
  Finset.univ.filter (fun p => Sum.inr p ∈ D.bag i)

/-- Bag `i` of the blow-up: the customers in `D.bag i` together with the customers of every
pattern in `D.bag i`. -/
def blowBag (i : Fin (D.length + 1)) : Finset C :=
  M.bagCustomers D i ∪ (M.bagPatterns D i).biUnion M.customers

theorem mem_blowBag_iff (i : Fin (D.length + 1)) (c : C) :
    c ∈ M.blowBag D i ↔ Sum.inl c ∈ D.bag i ∨ ∃ p, Sum.inr p ∈ D.bag i ∧ M.requires c p := by
  simp [blowBag, bagCustomers, bagPatterns, mem_customers_iff]

/-- `x` is a *reason* for `c`: `x` is `inl c` or `inr p` for a pattern `p` of `c`. -/
def IsReason (c : C) (x : C ⊕ Pt) : Prop :=
  x = Sum.inl c ∨ ∃ p, x = Sum.inr p ∧ M.requires c p

theorem isReason_inl (c : C) : M.IsReason c (Sum.inl c) := Or.inl rfl

theorem mem_blowBag_iff_exists_reason (i : Fin (D.length + 1)) (c : C) :
    c ∈ M.blowBag D i ↔ ∃ x, M.IsReason c x ∧ x ∈ D.bag i := by
  rw [mem_blowBag_iff]
  constructor
  · rintro (h | ⟨p, hp, hcp⟩)
    · exact ⟨Sum.inl c, Or.inl rfl, h⟩
    · exact ⟨Sum.inr p, Or.inr ⟨p, rfl, hcp⟩, hp⟩
  · rintro ⟨x, (rfl | ⟨p, rfl, hcp⟩), hx⟩
    · exact Or.inl hx
    · exact Or.inr ⟨p, hx, hcp⟩

/-- Every reason for `c` shares a bag of `D` with `inl c`: `inl c` itself by vertex
coverage, a pattern of `c` by edge coverage. -/
theorem exists_bag_of_isReason {c : C} {x : C ⊕ Pt} (hx : M.IsReason c x) :
    ∃ l, x ∈ D.bag l ∧ Sum.inl c ∈ D.bag l := by
  rcases hx with rfl | ⟨p, rfl, hcp⟩
  · obtain ⟨l, hl⟩ := D.vertex_coverage (Sum.inl c)
    exact ⟨l, hl, hl⟩
  · obtain ⟨l, hc, hp⟩ := D.edge_coverage (Sum.inl c) (Sum.inr p) hcp
    exact ⟨l, hp, hc⟩

/-- The blown-up decomposition of the MOSP graph. -/
def blowUp : PathDecomposition M.mospGraph where
  length := D.length
  bag i := M.blowBag D i
  vertex_coverage c := by
    obtain ⟨i, hi⟩ := D.vertex_coverage (Sum.inl c)
    exact ⟨i, (M.mem_blowBag_iff D i c).mpr (Or.inl hi)⟩
  edge_coverage c d hcd := by
    obtain ⟨_, p, hc, hd⟩ := hcd
    obtain ⟨i, hi⟩ := D.vertex_coverage (Sum.inr p)
    exact ⟨i, (M.mem_blowBag_iff D i c).mpr (Or.inr ⟨p, hi, hc⟩),
      (M.mem_blowBag_iff D i d).mpr (Or.inr ⟨p, hi, hd⟩)⟩
  interval c i j k hij hjk hi hk := by
    obtain ⟨x, hx, hxi⟩ := (M.mem_blowBag_iff_exists_reason D i c).mp hi
    obtain ⟨y, hy, hyk⟩ := (M.mem_blowBag_iff_exists_reason D k c).mp hk
    obtain ⟨l, hxl, hcl⟩ := M.exists_bag_of_isReason D hx
    obtain ⟨l', hyl', hcl'⟩ := M.exists_bag_of_isReason D hy
    rw [M.mem_blowBag_iff_exists_reason]
    rcases D.mem_bag_of_meet hij hjk hxi hyk hxl hcl hyl' hcl' with h | h | h
    · exact ⟨x, hx, h⟩
    · exact ⟨y, hy, h⟩
    · exact ⟨Sum.inl c, M.isReason_inl c, h⟩

theorem blowUp_bag (i : Fin (D.length + 1)) : (M.blowUp D).bag i = M.blowBag D i := rfl

/-- The customers and patterns of a bag, counted in it: `a + b ≤ |D.bag i|`. -/
theorem card_bagCustomers_add_card_bagPatterns_le (i : Fin (D.length + 1)) :
    (M.bagCustomers D i).card + (M.bagPatterns D i).card ≤ (D.bag i).card := by
  have hsub : (M.bagCustomers D i).image Sum.inl ∪ (M.bagPatterns D i).image Sum.inr ⊆
      D.bag i := by
    intro x hx
    rcases Finset.mem_union.mp hx with hx | hx
    · obtain ⟨c, hc, rfl⟩ := Finset.mem_image.mp hx
      exact (Finset.mem_filter.mp hc).2
    · obtain ⟨p, hp, rfl⟩ := Finset.mem_image.mp hx
      exact (Finset.mem_filter.mp hp).2
  have hdisj : Disjoint ((M.bagCustomers D i).image Sum.inl)
      ((M.bagPatterns D i).image Sum.inr) := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    obtain ⟨c, _, rfl⟩ := Finset.mem_image.mp hx
    obtain ⟨p, _, h⟩ := Finset.mem_image.mp hx'
    exact Sum.inr_ne_inl h
  calc (M.bagCustomers D i).card + (M.bagPatterns D i).card
      = ((M.bagCustomers D i).image Sum.inl).card + ((M.bagPatterns D i).image Sum.inr).card := by
        rw [Finset.card_image_of_injective _ Sum.inl_injective,
          Finset.card_image_of_injective _ Sum.inr_injective]
    _ = ((M.bagCustomers D i).image Sum.inl ∪ (M.bagPatterns D i).image Sum.inr).card :=
        (Finset.card_union_of_disjoint hdisj).symm
    _ ≤ (D.bag i).card := Finset.card_le_card hsub

/-- A bag of the blow-up has at most `a + b·ω` customers. -/
theorem card_blowBag_le (i : Fin (D.length + 1)) :
    (M.blowBag D i).card ≤
      (M.bagCustomers D i).card + (M.bagPatterns D i).card * M.maxPatternSize := by
  calc (M.blowBag D i).card
      ≤ (M.bagCustomers D i).card + ((M.bagPatterns D i).biUnion M.customers).card :=
        Finset.card_union_le _ _
    _ ≤ (M.bagCustomers D i).card + ∑ p ∈ M.bagPatterns D i, (M.customers p).card :=
        Nat.add_le_add_left Finset.card_biUnion_le _
    _ ≤ (M.bagCustomers D i).card + ∑ _p ∈ M.bagPatterns D i, M.maxPatternSize :=
        Nat.add_le_add_left
          (Finset.sum_le_sum (fun p _ => M.card_customers_le_maxPatternSize p)) _
    _ = (M.bagCustomers D i).card + (M.bagPatterns D i).card * M.maxPatternSize := by
        rw [Finset.sum_const, smul_eq_mul]

/-- **The blow-up's width**: `(blowUp D).width + 1 ≤ (D.width + 1) · ω` when `1 ≤ ω`. -/
theorem blowUp_width_add_one_le (hω : 1 ≤ M.maxPatternSize) :
    (M.blowUp D).width + 1 ≤ (D.width + 1) * M.maxPatternSize := by
  have hpos : 1 ≤ (D.width + 1) * M.maxPatternSize :=
    Nat.mul_pos (Nat.succ_pos _) hω
  have hle : (M.blowUp D).width ≤ (D.width + 1) * M.maxPatternSize - 1 := by
    apply PathDecomposition.width_le_of_forall_card_le
    intro i
    rw [Nat.sub_add_cancel hpos]
    show (M.blowBag D i).card ≤ _
    set a := (M.bagCustomers D i).card
    set b := (M.bagPatterns D i).card
    have hab : a + b ≤ D.width + 1 :=
      (M.card_bagCustomers_add_card_bagPatterns_le D i).trans (D.bag_card_le_width_add_one i)
    have ha : a ≤ a * M.maxPatternSize := Nat.le_mul_of_pos_right a hω
    calc (M.blowBag D i).card ≤ a + b * M.maxPatternSize := M.card_blowBag_le D i
      _ ≤ a * M.maxPatternSize + b * M.maxPatternSize := Nat.add_le_add_right ha _
      _ = (a + b) * M.maxPatternSize := (Nat.add_mul a b _).symm
      _ ≤ (D.width + 1) * M.maxPatternSize := Nat.mul_le_mul_right _ hab
  omega

/-- **(L2), the blow-up bound**: `pathwidth (mospGraph M) + 1 ≤ (pathwidth (incidence M) + 1) · ω`
when some pattern has a customer. -/
theorem pathwidth_mospGraph_add_one_le (hω : 1 ≤ M.maxPatternSize) :
    pathwidth M.mospGraph + 1 ≤ (pathwidth M.incidence + 1) * M.maxPatternSize := by
  obtain ⟨D, hD⟩ := exists_pathDecomposition_width_eq M.incidence
  rw [← hD]
  exact (Nat.add_le_add_right (pathwidth_le_width M.mospGraph (M.blowUp D)) 1).trans
    (M.blowUp_width_add_one_le D hω)

/-- **F1 in MOSP terms, for every instance**: `mospValue M ≤ ω · (pathwidth (incidence M) + 1)`.
The forest hypothesis of §6 is not used; when `ω = 0` no customer requires anything and the
MOSP value is `0`. -/
theorem mospValue_le_maxPatternSize_mul :
    M.mospValue ≤ M.maxPatternSize * (pathwidth M.incidence + 1) := by
  rcases Nat.eq_zero_or_pos M.maxPatternSize with h0 | hω
  · rw [M.mospValue_eq_zero_of_forall_not (M.forall_not_requires_of_maxPatternSize_eq_zero h0)]
    exact Nat.zero_le _
  · calc M.mospValue ≤ pathwidth M.mospGraph + 1 := M.mospValue_le_pathwidth_add_one
      _ ≤ (pathwidth M.incidence + 1) * M.maxPatternSize := M.pathwidth_mospGraph_add_one_le hω
      _ = M.maxPatternSize * (pathwidth M.incidence + 1) := Nat.mul_comm _ _

end MOSPInstance

/-! ### `tb N = ⌊log₃((6N + 3)/5)⌋`, the least `k` with `N ≤ treeBound k` -/

/-- `treeBoundInv N = ⌊log₃((6N + 3)/5)⌋`: Lemma 5 of §6.2, the least `k` with
`N ≤ treeBound k` (`le_treeBound_treeBoundInv`, `treeBound_lt_of_lt_treeBoundInv`). -/
def treeBoundInv (N : ℕ) : ℕ := Nat.log 3 ((6 * N + 3) / 5)

theorem three_pow_odd (k : ℕ) : 3 ^ k % 2 = 1 := by
  rw [Nat.pow_mod]; simp

/-- `N ≤ treeBound (treeBoundInv N)`: from `(6N + 3)/5 < 3^(k+1)` and the parity of
`5·3^k`, `2N + 3 ≤ 5·3^k = 2·treeBound k + 3`. -/
theorem le_treeBound_treeBoundInv (N : ℕ) : N ≤ treeBound (treeBoundInv N) := by
  have h1 : (6 * N + 3) / 5 < 3 ^ (treeBoundInv N + 1) :=
    Nat.lt_pow_succ_log_self (by norm_num) _
  have h2 := two_mul_treeBound_add_three (treeBoundInv N)
  have h3 := three_pow_odd (treeBoundInv N)
  rw [pow_succ] at h1
  omega

/-- `treeBoundInv N` is the least such `k`: below it the bound is too small. -/
theorem treeBound_lt_of_lt_treeBoundInv {N k : ℕ} (hk : k < treeBoundInv N) :
    treeBound k < N := by
  have hne : (6 * N + 3) / 5 ≠ 0 := by
    intro h0
    have h00 : treeBoundInv N = 0 := by
      unfold treeBoundInv; rw [h0, Nat.log_zero_right]
    omega
  have h1 : 3 ^ (k + 1) ≤ (6 * N + 3) / 5 := Nat.pow_le_of_le_log hne hk
  have h2 := two_mul_treeBound_add_three k
  rw [pow_succ] at h1
  omega

/-- **(L3)**: every forest on `N` vertices has pathwidth at most `treeBoundInv N`
(`tree_pathwidth_le_treeBound` on each connected piece, which is a tree on at most `N`
vertices). -/
theorem pathwidth_le_treeBoundInv_of_isAcyclic {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (hG : G.IsAcyclic) :
    pathwidth G ≤ treeBoundInv (Fintype.card V) := by
  have h := pathwidth_le_pathwidth_induce_add_card_compl G Finset.univ
  rw [Finset.compl_univ, Finset.card_empty, add_zero] at h
  refine h.trans (pathwidth_induce_le_of_forall_connected G Finset.univ _ ?_)
  intro K _ hc
  have hT : (G.induce (↑K : Set V)).IsTree := ⟨hc, hG.induce _⟩
  apply tree_pathwidth_le_treeBound _ _ hT
  have hK : Fintype.card (↑(↑K : Set V) : Type _) = K.card := by
    simp only [Finset.coe_sort_coe, Fintype.card_coe]
  rw [hK]
  exact (Finset.card_le_univ K).trans (le_treeBound_treeBoundInv _)

namespace MOSPInstance

variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- **(L4), F1′, the forest regime**: if the incidence graph is a forest,
`mospValue M ≤ ω · (⌊log₃((6(n + m) + 3)/5)⌋ + 1)`. -/
theorem mospValue_le_of_incidence_isAcyclic (h : M.incidence.IsAcyclic) :
    M.mospValue ≤ M.maxPatternSize * (treeBoundInv (Fintype.card C + Fintype.card Pt) + 1) := by
  refine M.mospValue_le_maxPatternSize_mul.trans (Nat.mul_le_mul_left _ (Nat.add_le_add_right ?_ 1))
  have := pathwidth_le_treeBoundInv_of_isAcyclic M.incidence h
  rwa [Fintype.card_sum] at this

/-! ### Subinstance monotonicity -/

/-- A larger instance has a larger MOSP graph. -/
theorem mospGraph_mono (M' : MOSPInstance C Pt) [DecidableRel M'.requires]
    (h : ∀ c p, M.requires c p → M'.requires c p) : M.mospGraph ≤ M'.mospGraph := by
  intro c d hcd
  obtain ⟨hne, p, hc, hd⟩ := hcd
  exact ⟨hne, p, h c p hc, h d p hd⟩

/-- **Subinstance monotonicity** (Yanasse 1997a, Proposition 2): adding requirements never
lowers the MOSP value. No hypothesis: if `M` has no requirement its value is `0`. -/
theorem mospValue_mono (M' : MOSPInstance C Pt) [DecidableRel M'.requires]
    (h : ∀ c p, M.requires c p → M'.requires c p) : M.mospValue ≤ M'.mospValue := by
  by_cases hM : ∃ c p, M.requires c p
  · obtain ⟨c, p, hcp⟩ := hM
    calc M.mospValue ≤ pathwidth M.mospGraph + 1 := M.mospValue_le_pathwidth_add_one
      _ ≤ pathwidth M'.mospGraph + 1 := Nat.add_le_add_right (pathwidth_mono (M.mospGraph_mono M' h)) 1
      _ ≤ M'.mospValue := M'.pathwidth_add_one_le_mospValue ⟨c, p, h c p hcp⟩
  · push Not at hM
    rw [M.mospValue_eq_zero_of_forall_not hM]
    exact Nat.zero_le _

end MOSPInstance

/-! ### The coupling inclusion on clique covers (item 10, Lemma V2) -/

section Cover

variable {m : ℕ}

/-- A pointwise larger cover has a larger graph. -/
theorem coverGraph_mono {S S' : Fin m → Finset C} (hS : ∀ j, S j ⊆ S' j) :
    coverGraph S ≤ coverGraph S' := by
  intro u v huv
  obtain ⟨hne, j, hu, hv⟩ := huv
  exact ⟨hne, j, hS j hu, hS j hv⟩

/-- **The coupling inclusion**: an empty pair of the graph of a larger cover is an empty pair
of the graph of the smaller one. With `S` the base matrix and `S'` the padded one, every
empty pair of the padded graph is an empty pair of the base graph. -/
theorem isEmptyPair_coverGraph_of_subset {S S' : Fin m → Finset C} (hS : ∀ j, S j ⊆ S' j)
    {A R : Finset C} (h : IsEmptyPair (coverGraph S') A R) : IsEmptyPair (coverGraph S) A R :=
  isEmptyPair_anti (coverGraph_mono hS) h

/-- The pathwidth of a cover's graph is monotone in the cover. -/
theorem pathwidth_coverGraph_mono {S S' : Fin m → Finset C} (hS : ∀ j, S j ⊆ S' j) :
    pathwidth (coverGraph S) ≤ pathwidth (coverGraph S') :=
  pathwidth_mono (coverGraph_mono hS)

end Cover

/-! ### The layer lemma (item 07, Lemma L): a layering bounds the pathwidth -/

section Layering

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V)

/-- The vertices at level `i` of a level function. -/
def layer (lvl : V → ℕ) (i : ℕ) : Finset V := Finset.univ.filter (fun v => lvl v = i)

theorem mem_layer_iff (lvl : V → ℕ) (i : ℕ) (v : V) : v ∈ layer lvl i ↔ lvl v = i := by
  simp [layer]

/-- A **layering**: adjacent vertices are at most one level apart (BFS distance from a
root is one, `isLayering_dist`). -/
def IsLayering (lvl : V → ℕ) : Prop := ∀ u v, G.Adj u v → lvl u ≤ lvl v + 1

/-- `|L_i| + |L_{i+1}|` maximised over `i ≤ h`. -/
def layerWidth (lvl : V → ℕ) (h : ℕ) : ℕ :=
  (Finset.range (h + 1)).sup (fun i => (layer lvl i).card + (layer lvl (i + 1)).card)

/-- The layer decomposition: bag `i` is `L_i ∪ L_{i+1}`. A vertex of level `l` is in bags
`l − 1` and `l` only, an interval; an edge joins levels at most one apart, so both ends are
in the bag of the lower level. -/
def layerDecomposition (lvl : V → ℕ) (hl : IsLayering G lvl) (h : ℕ) (hh : ∀ v, lvl v ≤ h) :
    PathDecomposition G where
  length := h
  bag i := layer lvl i.val ∪ layer lvl (i.val + 1)
  vertex_coverage v :=
    ⟨⟨lvl v, by have := hh v; omega⟩, Finset.mem_union_left _ ((mem_layer_iff lvl _ v).mpr rfl)⟩
  edge_coverage u v huv := by
    have h1 := hl u v huv
    have h2 := hl v u (huv.symm)
    rcases le_total (lvl u) (lvl v) with hle | hle
    · refine ⟨⟨lvl u, by have := hh u; omega⟩, Finset.mem_union_left _
        ((mem_layer_iff lvl _ u).mpr rfl), ?_⟩
      simp only [Finset.mem_union, mem_layer_iff]
      omega
    · refine ⟨⟨lvl v, by have := hh v; omega⟩, ?_, Finset.mem_union_left _
        ((mem_layer_iff lvl _ v).mpr rfl)⟩
      simp only [Finset.mem_union, mem_layer_iff]
      omega
  interval v i j k hij hjk hi hk := by
    simp only [Finset.mem_union, mem_layer_iff] at hi hk ⊢
    have hij' : i.val ≤ j.val := hij
    have hjk' : j.val ≤ k.val := hjk
    omega

/-- **The layer lemma** (item 07, Lemma L, in pathwidth form): for a layering with levels
`≤ h`, `pathwidth G ≤ max_{i ≤ h} (|L_i| + |L_{i+1}|) − 1`. -/
theorem pathwidth_le_layerWidth (lvl : V → ℕ) (hl : IsLayering G lvl) (h : ℕ)
    (hh : ∀ v, lvl v ≤ h) : pathwidth G ≤ layerWidth lvl h - 1 := by
  refine (pathwidth_le_width G (layerDecomposition G lvl hl h hh)).trans ?_
  apply PathDecomposition.width_le_of_forall_card_le
  intro i
  have hle : (layer lvl i.val).card + (layer lvl (i.val + 1)).card ≤ layerWidth lvl h :=
    Finset.le_sup (f := fun i => (layer lvl i).card + (layer lvl (i + 1)).card)
      (Finset.mem_range.mpr i.isLt)
  have hcard := Finset.card_union_le (layer lvl i.val) (layer lvl (i.val + 1))
  show (layer lvl i.val ∪ layer lvl (i.val + 1)).card ≤ layerWidth lvl h - 1 + 1
  omega

/-- The same in vertex-separation form (`vertexSeparation_eq_pathwidth`, Kinnersley 1992). -/
theorem vertexSeparation_le_layerWidth [DecidableRel G.Adj] (lvl : V → ℕ) (hl : IsLayering G lvl) (h : ℕ)
    (hh : ∀ v, lvl v ≤ h) : vertexSeparation G ≤ layerWidth lvl h - 1 := by
  rw [vertexSeparation_eq_pathwidth]
  exact pathwidth_le_layerWidth G lvl hl h hh

/-- BFS distance from a root of a connected graph is a layering. -/
theorem isLayering_dist (hG : G.Connected) (r : V) : IsLayering G (G.dist r) := by
  intro u v huv
  have h1 : G.dist r u ≤ G.dist r v + G.dist v u := hG.dist_triangle
  have h2 : G.dist v u = 1 := SimpleGraph.dist_eq_one_iff_adj.mpr (huv.symm)
  omega

/-- **The BFS form**: for a connected graph and any root `r`, with `L_i` the vertices at
distance `i` from `r` and `h` the eccentricity of `r`,
`pathwidth G ≤ max_{i ≤ h} (|L_i| + |L_{i+1}|) − 1`. -/
theorem pathwidth_le_layerWidth_dist (hG : G.Connected) (r : V) :
    pathwidth G ≤ layerWidth (G.dist r) (Finset.univ.sup (G.dist r)) - 1 :=
  pathwidth_le_layerWidth G (G.dist r) (isLayering_dist G hG r) _
    (fun v => Finset.le_sup (f := G.dist r) (Finset.mem_univ v))

end Layering

end MOSPFormalization
