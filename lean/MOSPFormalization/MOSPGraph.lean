/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# MOSP = Pathwidth + 1, over the MOSP graph

The **MOSP graph** of an instance has the *customers* as vertices, two of them
adjacent iff some pattern requires both (Yanasse 1997c; Yanasse & Senne 2010).
Each pattern's customer set is a clique, so the graph is a union of cliques.
This is the graph for which the pathwidth equivalence holds:

  `mospValue M = pathwidth (mospGraph M) + 1`

whenever some customer requires some pattern (`mospValue_eq_pathwidth_add_one`).
Without that hypothesis the left side is `0` and the right side is `1`
(`mospValue_eq_zero_of_forall_not`, `pathwidth_mospGraph_eq_zero_of_forall_not`),
so the hypothesis is exactly what the statement needs; the two one-sided
inequalities are stated without it where they hold:

* `mospValue_le_pathwidth_add_one` — no hypothesis at all;
* `pathwidth_le_mospValue_sub_one` — no hypothesis at all, with truncated
  subtraction, which is `pathwidth_add_one_le_mospValue` once `1 ≤ mospValue`.

The *agreement graph* of `MOSPInstance.lean`, with patterns as vertices, is a
different graph, and the corresponding statement over it is false: see the
module comment of `Reduction.lean` and the star instance in `MOSPGraphExamples.lean`.

## The two directions

**Layout to decomposition** (`stackDecomposition`). A pattern order `σ` gives
the decomposition whose bag at step `i < |Pt|` is the set of customers whose
stack is open at `i`. A customer's stack is open exactly between the first and
the last of its patterns, inclusive (`isActive`), so the bags containing it
form an interval; two customers sharing pattern `p` are both open at `σ p`.
A customer with no pattern is never open and gets a singleton bag of its own,
appended after the `|Pt|` stack bags, so the construction needs no hypothesis.
The width is `maxOpenStacks σ - 1`, up to the singleton bags of size `1`.

**Decomposition to layout** (`exists_maxOpenStacks_le_width_add_one`). In a
path decomposition every clique lies inside a single bag
(`PathDecomposition.exists_bag_of_isClique`, the Helly property of intervals:
take the clique vertex whose first bag is latest). Choose for each pattern a
bag holding its customers (`bagOf`), and order the patterns by that bag
(`exists_layout_sorted`). A customer open at step `i` has a pattern at or
before `i` and one at or after `i`; their bags bracket the bag of the pattern
at `i`, so the customer is in that bag by the interval property. Hence at most
`width + 1` stacks are open at any step.

The literature chain is Linhares & Yanasse (2002) Prop. 2, Fellows & Langston
(1989) Thm. 7 with Fellows & Langston (1987) Lemma 4.1, and Kinnersley (1992)
Thm. 3.1; the proofs here are direct and go through bags rather than vertex
separation.
-/

import MOSPFormalization.Pathwidth
import MOSPFormalization.OpenStacks
import MOSPFormalization.DecompositionToLayout
import Mathlib.Combinatorics.SimpleGraph.Clique

set_option linter.unusedSectionVars false

namespace MOSPFormalization

/-! ### Graph-level lemmas -/

section Graph

variable {V : Type*} [Fintype V] [DecidableEq V]

namespace PathDecomposition

variable {G : SimpleGraph V}

/-- **Helly property**: every clique of `G` is contained in a single bag of any
path decomposition. Take the clique vertex `v` whose first bag is latest; every
other clique vertex `u` shares a bag with `v`, so `firstBag u ≤ firstBag v ≤ lastBag u`
and `u` lies in `bag (firstBag v)` by the interval property. -/
theorem exists_bag_of_isClique (D : PathDecomposition G) (K : Finset V)
    (hK : G.IsClique (K : Set V)) : ∃ b, K ⊆ D.bag b := by
  rcases K.eq_empty_or_nonempty with rfl | hne
  · exact ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.empty_subset _⟩
  · obtain ⟨v, hv, hmax⟩ := Finset.exists_max_image K (fun u => D.firstBag u) hne
    refine ⟨D.firstBag v, fun u hu => ?_⟩
    by_cases huv : u = v
    · subst huv; exact D.mem_bag_firstBag u
    · have hadj : G.Adj u v :=
        ((SimpleGraph.isClique_iff G).mp hK) (Finset.mem_coe.mpr hu) (Finset.mem_coe.mpr hv) huv
      obtain ⟨l, hul, hvl⟩ := D.edge_coverage u v hadj
      rw [D.mem_bag_iff_between]
      exact ⟨hmax u hu,
        le_trans ((D.mem_bag_iff_between v l).mp hvl).1 ((D.mem_bag_iff_between u l).mp hul).2⟩

/-- A clique has at most `width + 1` vertices. -/
theorem card_le_width_add_one_of_isClique (D : PathDecomposition G) (K : Finset V)
    (hK : G.IsClique (K : Set V)) : K.card ≤ D.width + 1 := by
  obtain ⟨b, hb⟩ := D.exists_bag_of_isClique K hK
  exact (Finset.card_le_card hb).trans (D.bag_card_le_width_add_one b)

end PathDecomposition

/-- The pathwidth of a graph is attained by some path decomposition. -/
theorem exists_pathDecomposition_width_eq (G : SimpleGraph V) :
    ∃ D : PathDecomposition G, D.width = pathwidth G := by
  have hne : (Set.range (fun D : PathDecomposition G => D.width)).Nonempty :=
    ⟨_, ⟨PathDecomposition.trivial G, rfl⟩⟩
  obtain ⟨D, hD⟩ := Nat.sInf_mem hne
  exact ⟨D, hD⟩

/-- A clique has at most `pathwidth + 1` vertices. -/
theorem card_le_pathwidth_add_one_of_isClique (G : SimpleGraph V) (K : Finset V)
    (hK : G.IsClique (K : Set V)) : K.card ≤ pathwidth G + 1 := by
  obtain ⟨D, hD⟩ := exists_pathDecomposition_width_eq G
  rw [← hD]
  exact D.card_le_width_add_one_of_isClique K hK

/-- Any function into a linear order can be realised as a layout up to ties:
vertices with strictly smaller key come strictly earlier. This generalises
`exists_monotone_layout`, which is the case `f = lastBag`. -/
theorem exists_layout_sorted {ι : Type*} [LinearOrder ι] (f : V → ι) :
    ∃ σ : LinearLayout V, ∀ u v : V, f u < f v → (σ u).val < (σ v).val := by
  classical
  let e := Fintype.equivFin V
  let _ : LinearOrder V :=
    LinearOrder.lift' (fun v => toLex (f v, e v)) (by
      intro u v huv
      have huv' : (f u, e u) = (f v, e v) := huv
      exact e.injective (congr_arg Prod.snd huv'))
  let iso : Fin (Fintype.card V) ≃o V := monoEquivOfFin V rfl
  refine ⟨iso.symm.toEquiv, fun u v hlt => ?_⟩
  have hu_lt_v : toLex (f u, e u) < toLex (f v, e v) := by
    rw [Prod.Lex.toLex_lt_toLex]
    exact Or.inl hlt
  exact iso.symm.strictMono (show u < v from hu_lt_v)

end Graph

/-! ### The MOSP graph -/

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]

namespace MOSPInstance

variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- Two customers *share* a pattern if they are distinct and some pattern requires both. -/
def shares (c d : C) : Prop :=
  c ≠ d ∧ ∃ p, M.requires c p ∧ M.requires d p

instance decShares : DecidableRel M.shares := by
  intro c d
  unfold shares
  exact instDecidableAnd

/-- The **MOSP graph**: vertices are customers, adjacent iff they share a pattern.
This is the graph of Yanasse (1997c), not the agreement graph on patterns. -/
def mospGraph : SimpleGraph C where
  Adj := M.shares
  symm := by
    constructor
    intro x y ⟨hne, p, hx, hy⟩
    exact ⟨hne.symm, p, hy, hx⟩
  loopless := by
    constructor
    intro x ⟨hne, _⟩
    exact hne rfl

instance : DecidableRel M.mospGraph.Adj := M.decShares

theorem mospGraph_adj_iff (c d : C) :
    M.mospGraph.Adj c d ↔ c ≠ d ∧ ∃ p, M.requires c p ∧ M.requires d p := Iff.rfl

theorem mem_customers_iff (p : Pt) (c : C) : c ∈ M.customers p ↔ M.requires c p := by
  simp [customers]

theorem mem_patterns_iff (c : C) (p : Pt) : p ∈ M.patterns c ↔ M.requires c p := by
  simp [patterns]

/-- Each pattern's customer set is a clique of the MOSP graph. -/
theorem customers_isClique (p : Pt) : M.mospGraph.IsClique (M.customers p : Set C) := by
  rw [SimpleGraph.isClique_iff]
  intro c hc d hd hne
  exact ⟨hne, p, (M.mem_customers_iff p c).mp (Finset.mem_coe.mp hc),
    (M.mem_customers_iff p d).mp (Finset.mem_coe.mp hd)⟩

/-! ### Open stacks as bags -/

theorem isActive_iff (σ : LinearLayout Pt) (c : C) (i : ℕ) :
    M.isActive σ c i ↔
      (∃ p, M.requires c p ∧ (σ p).val ≤ i) ∧ (∃ p, M.requires c p ∧ i ≤ (σ p).val) := by
  simp only [isActive, Finset.Nonempty, Finset.mem_filter, mem_patterns_iff, ge_iff_le]

/-- A customer's stack is open at the step of each of its patterns. -/
theorem isActive_of_requires (σ : LinearLayout Pt) {c : C} {p : Pt} (h : M.requires c p) :
    M.isActive σ c (σ p).val :=
  (M.isActive_iff σ c _).mpr ⟨⟨p, h, le_rfl⟩, ⟨p, h, le_rfl⟩⟩

/-- The steps at which a customer's stack is open form an interval. -/
theorem isActive_of_between (σ : LinearLayout Pt) {c : C} {i j k : ℕ}
    (hij : i ≤ j) (hjk : j ≤ k) (hi : M.isActive σ c i) (hk : M.isActive σ c k) :
    M.isActive σ c j := by
  rw [isActive_iff] at hi hk ⊢
  obtain ⟨⟨p, hp, hpi⟩, _⟩ := hi
  obtain ⟨_, ⟨q, hq, hqk⟩⟩ := hk
  exact ⟨⟨p, hp, by omega⟩, ⟨q, hq, by omega⟩⟩

/-- An open stack belongs to a customer with at least one pattern. -/
theorem exists_requires_of_isActive (σ : LinearLayout Pt) {c : C} {i : ℕ}
    (h : M.isActive σ c i) : ∃ p, M.requires c p := by
  obtain ⟨⟨p, hp, _⟩, _⟩ := (M.isActive_iff σ c i).mp h
  exact ⟨p, hp⟩

/-- A stack can only be open at a step that exists. -/
theorem lt_card_of_isActive (σ : LinearLayout Pt) {c : C} {i : ℕ}
    (h : M.isActive σ c i) : i < Fintype.card Pt := by
  obtain ⟨_, ⟨p, _, hpi⟩⟩ := (M.isActive_iff σ c i).mp h
  exact lt_of_le_of_lt hpi (σ p).isLt

/-- The customers whose stack is open at step `i`. -/
def activeSet (σ : LinearLayout Pt) (i : ℕ) : Finset C :=
  Finset.univ.filter (fun c => M.isActive σ c i)

theorem mem_activeSet_iff (σ : LinearLayout Pt) (i : ℕ) (c : C) :
    c ∈ M.activeSet σ i ↔ M.isActive σ c i := by
  simp [activeSet]

theorem card_activeSet (σ : LinearLayout Pt) (i : ℕ) :
    (M.activeSet σ i).card = M.openStacksAt σ i := rfl

theorem openStacksAt_le_maxOpenStacks (σ : LinearLayout Pt) {i : ℕ}
    (hi : i < Fintype.card Pt) : M.openStacksAt σ i ≤ M.maxOpenStacks σ := by
  unfold maxOpenStacks
  have hn : Fintype.card Pt ≠ 0 := by omega
  simp only [dite_eq_right hn]
  exact Finset.le_sup' (fun j : Fin (Fintype.card Pt) => M.openStacksAt σ j.val)
    (Finset.mem_univ (⟨i, hi⟩ : Fin (Fintype.card Pt)))

/-! ### Layout to decomposition -/

/-- The bag at step `i` of the decomposition read off a pattern order `σ`: for
`i < |Pt|` the customers open at step `i`; for `i = |Pt| + e c` the singleton of a
customer `c` with no pattern, so that such customers are covered too. The two
cases are exclusive because an open stack forces `i < |Pt|`. -/
def stackBag (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C)) (i : ℕ) : Finset C :=
  Finset.univ.filter (fun c =>
    M.isActive σ c i ∨ (M.patterns c = ∅ ∧ (e c).val + Fintype.card Pt = i))

theorem mem_stackBag_iff (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C)) (i : ℕ)
    (c : C) : c ∈ M.stackBag σ e i ↔
      M.isActive σ c i ∨ (M.patterns c = ∅ ∧ (e c).val + Fintype.card Pt = i) := by
  simp [stackBag]

theorem patterns_eq_empty_iff (c : C) : M.patterns c = ∅ ↔ ∀ p, ¬ M.requires c p := by
  simp [patterns, Finset.filter_eq_empty_iff]

/-- A stack bag below `|Pt|` is exactly the set of open stacks. -/
theorem stackBag_subset_activeSet (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C))
    {i : ℕ} (hi : i < Fintype.card Pt) : M.stackBag σ e i ⊆ M.activeSet σ i := by
  intro c hc
  rw [mem_stackBag_iff] at hc
  rw [mem_activeSet_iff]
  rcases hc with h | ⟨_, h⟩
  · exact h
  · omega

/-- A stack bag at or beyond `|Pt|` has at most one customer. -/
theorem card_stackBag_le_one (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C))
    {i : ℕ} (hi : Fintype.card Pt ≤ i) : (M.stackBag σ e i).card ≤ 1 := by
  rw [Finset.card_le_one]
  intro a ha b hb
  rw [mem_stackBag_iff] at ha hb
  rcases ha with ha | ⟨_, ha⟩
  · have := M.lt_card_of_isActive σ ha; omega
  rcases hb with hb | ⟨_, hb⟩
  · have := M.lt_card_of_isActive σ hb; omega
  exact e.injective (Fin.ext (by omega))

theorem card_stackBag_le (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C)) (i : ℕ) :
    (M.stackBag σ e i).card ≤ max (M.maxOpenStacks σ) 1 := by
  by_cases hi : i < Fintype.card Pt
  · calc (M.stackBag σ e i).card ≤ (M.activeSet σ i).card :=
          Finset.card_le_card (M.stackBag_subset_activeSet σ e hi)
      _ = M.openStacksAt σ i := M.card_activeSet σ i
      _ ≤ M.maxOpenStacks σ := M.openStacksAt_le_maxOpenStacks σ hi
      _ ≤ max (M.maxOpenStacks σ) 1 := le_max_left _ _
  · exact (M.card_stackBag_le_one σ e (by omega)).trans (le_max_right _ _)

/-- The path decomposition of the MOSP graph read off a pattern order `σ`:
`|Pt|` stack bags followed by `|C|` bags, of which the ones for customers with no
pattern are singletons and the rest are empty. There is always at least one bag
(`length + 1 ≥ 1`), so no hypothesis is needed. -/
def stackDecomposition (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C)) :
    PathDecomposition M.mospGraph where
  length := Fintype.card Pt + Fintype.card C - 1
  bag := fun i => M.stackBag σ e i.val
  vertex_coverage := by
    intro c
    by_cases hc : ∃ p, M.requires c p
    · obtain ⟨p, hp⟩ := hc
      refine ⟨⟨(σ p).val, by have := (σ p).isLt; omega⟩, ?_⟩
      rw [mem_stackBag_iff]
      exact Or.inl (M.isActive_of_requires σ hp)
    · refine ⟨⟨(e c).val + Fintype.card Pt, by have := (e c).isLt; omega⟩, ?_⟩
      rw [mem_stackBag_iff]
      right
      refine ⟨(M.patterns_eq_empty_iff c).mpr ?_, rfl⟩
      intro p hp
      exact hc ⟨p, hp⟩
  edge_coverage := by
    intro c d hcd
    obtain ⟨_, p, hc, hd⟩ := hcd
    refine ⟨⟨(σ p).val, by have := (σ p).isLt; omega⟩, ?_, ?_⟩
    · rw [mem_stackBag_iff]; exact Or.inl (M.isActive_of_requires σ hc)
    · rw [mem_stackBag_iff]; exact Or.inl (M.isActive_of_requires σ hd)
  interval := by
    intro c i j k hij hjk hi hk
    simp only [mem_stackBag_iff] at hi hk ⊢
    have hij' : i.val ≤ j.val := hij
    have hjk' : j.val ≤ k.val := hjk
    rcases hi with hi | ⟨hempty, hi⟩
    · rcases hk with hk | ⟨hempty, hk⟩
      · exact Or.inl (M.isActive_of_between σ hij' hjk' hi hk)
      · exfalso
        obtain ⟨p, hp⟩ := M.exists_requires_of_isActive σ hi
        exact ((M.patterns_eq_empty_iff c).mp hempty) p hp
    · rcases hk with hk | ⟨_, hk⟩
      · exfalso
        obtain ⟨p, hp⟩ := M.exists_requires_of_isActive σ hk
        exact ((M.patterns_eq_empty_iff c).mp hempty) p hp
      · exact Or.inr ⟨hempty, by omega⟩

/-- The decomposition read off `σ` has width at most `maxOpenStacks σ - 1`. -/
theorem stackDecomposition_width_le (σ : LinearLayout Pt) (e : C ≃ Fin (Fintype.card C)) :
    (M.stackDecomposition σ e).width ≤ M.maxOpenStacks σ - 1 := by
  unfold PathDecomposition.width
  have hsup : Finset.sup' Finset.univ
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
      (fun i : Fin ((M.stackDecomposition σ e).length + 1) =>
        ((M.stackDecomposition σ e).bag i).card) ≤ max (M.maxOpenStacks σ) 1 := by
    apply Finset.sup'_le
    intro i _
    exact M.card_stackBag_le σ e i.val
  omega

/-- **Easy direction, per layout**: the pathwidth of the MOSP graph is below
`maxOpenStacks σ - 1` for every pattern order `σ`. -/
theorem pathwidth_le_maxOpenStacks_sub_one (σ : LinearLayout Pt) :
    pathwidth M.mospGraph ≤ M.maxOpenStacks σ - 1 :=
  calc pathwidth M.mospGraph
      ≤ (M.stackDecomposition σ (Fintype.equivFin C)).width := pathwidth_le_width _ _
    _ ≤ M.maxOpenStacks σ - 1 := M.stackDecomposition_width_le σ _

/-- The MOSP value is attained by some pattern order. -/
theorem exists_maxOpenStacks_eq_mospValue :
    ∃ σ : LinearLayout Pt, M.maxOpenStacks σ = M.mospValue := by
  have hne : (Set.range (fun σ : LinearLayout Pt => M.maxOpenStacks σ)).Nonempty :=
    ⟨_, ⟨Fintype.equivFin Pt, rfl⟩⟩
  obtain ⟨σ, hσ⟩ := Nat.sInf_mem hne
  exact ⟨σ, hσ⟩

/-- **Easy direction**: `pathwidth (mospGraph M) ≤ mospValue M - 1`, with truncated
subtraction and no hypothesis. -/
theorem pathwidth_le_mospValue_sub_one :
    pathwidth M.mospGraph ≤ M.mospValue - 1 := by
  obtain ⟨σ, hσ⟩ := M.exists_maxOpenStacks_eq_mospValue
  rw [← hσ]
  exact M.pathwidth_le_maxOpenStacks_sub_one σ

/-! ### Decomposition to layout -/

/-- A bag containing all the customers of pattern `p`, which exist by the Helly
property since they form a clique. -/
noncomputable def bagOf (D : PathDecomposition M.mospGraph) (p : Pt) : Fin (D.length + 1) :=
  Classical.choose (D.exists_bag_of_isClique (M.customers p) (M.customers_isClique p))

theorem customers_subset_bag_bagOf (D : PathDecomposition M.mospGraph) (p : Pt) :
    M.customers p ⊆ D.bag (M.bagOf D p) :=
  Classical.choose_spec (D.exists_bag_of_isClique (M.customers p) (M.customers_isClique p))

/-- Under a pattern order sorted by `bagOf`, every stack open at step `i` lies in
the bag chosen for the pattern produced at step `i`. -/
theorem activeSet_subset_bag_of_sorted (D : PathDecomposition M.mospGraph)
    (σ : LinearLayout Pt)
    (hσ : ∀ p q : Pt, M.bagOf D p < M.bagOf D q → (σ p).val < (σ q).val)
    (i : Fin (Fintype.card Pt)) :
    M.activeSet σ i.val ⊆ D.bag (M.bagOf D (σ.symm i)) := by
  intro c hc
  rw [mem_activeSet_iff, isActive_iff] at hc
  obtain ⟨⟨p₁, hp₁, hle₁⟩, ⟨p₂, hp₂, hle₂⟩⟩ := hc
  have hσ₀ : (σ (σ.symm i)).val = i.val := by simp
  -- sortedness, contrapositive: earlier patterns have no later bag
  have hb₁ : M.bagOf D p₁ ≤ M.bagOf D (σ.symm i) := by
    by_contra hlt
    push Not at hlt
    have := hσ _ _ hlt
    omega
  have hb₂ : M.bagOf D (σ.symm i) ≤ M.bagOf D p₂ := by
    by_contra hlt
    push Not at hlt
    have := hσ _ _ hlt
    omega
  exact D.interval c _ _ _ hb₁ hb₂
    (M.customers_subset_bag_bagOf D p₁ ((M.mem_customers_iff p₁ c).mpr hp₁))
    (M.customers_subset_bag_bagOf D p₂ ((M.mem_customers_iff p₂ c).mpr hp₂))

/-- Every path decomposition of the MOSP graph yields a pattern order with at
most `width + 1` open stacks at every step. -/
theorem exists_maxOpenStacks_le_width_add_one (D : PathDecomposition M.mospGraph) :
    ∃ σ : LinearLayout Pt, M.maxOpenStacks σ ≤ D.width + 1 := by
  obtain ⟨σ, hσ⟩ := exists_layout_sorted (M.bagOf D)
  refine ⟨σ, ?_⟩
  unfold maxOpenStacks
  by_cases hn : Fintype.card Pt = 0
  · simp [hn]
  · simp only [dite_eq_right hn]
    apply Finset.sup'_le
    intro i _
    calc M.openStacksAt σ i.val = (M.activeSet σ i.val).card := (M.card_activeSet σ i.val).symm
      _ ≤ (D.bag (M.bagOf D (σ.symm i))).card :=
          Finset.card_le_card (M.activeSet_subset_bag_of_sorted D σ hσ i)
      _ ≤ D.width + 1 := D.bag_card_le_width_add_one _

/-- For every path decomposition `D` of the MOSP graph, `mospValue ≤ D.width + 1`. -/
theorem mospValue_le_width_add_one (D : PathDecomposition M.mospGraph) :
    M.mospValue ≤ D.width + 1 := by
  obtain ⟨σ, hσ⟩ := M.exists_maxOpenStacks_le_width_add_one D
  exact (M.mospValue_le_maxOpenStacks σ).trans hσ

/-- **Hard direction**: `mospValue M ≤ pathwidth (mospGraph M) + 1`, no hypothesis. -/
theorem mospValue_le_pathwidth_add_one :
    M.mospValue ≤ pathwidth M.mospGraph + 1 := by
  obtain ⟨D, hD⟩ := exists_pathDecomposition_width_eq M.mospGraph
  rw [← hD]
  exact M.mospValue_le_width_add_one D

/-! ### The equality and its degenerate case -/

/-- If some customer requires some pattern, every pattern order opens a stack. -/
theorem one_le_maxOpenStacks (σ : LinearLayout Pt) (h : ∃ c p, M.requires c p) :
    1 ≤ M.maxOpenStacks σ := by
  obtain ⟨c, p, hcp⟩ := h
  calc 1 ≤ M.openStacksAt σ (σ p).val := by
        unfold openStacksAt
        exact Finset.card_pos.mpr ⟨c, Finset.mem_filter.mpr
          ⟨Finset.mem_univ _, M.isActive_of_requires σ hcp⟩⟩
    _ ≤ M.maxOpenStacks σ := M.openStacksAt_le_maxOpenStacks σ (σ p).isLt

theorem one_le_mospValue (h : ∃ c p, M.requires c p) : 1 ≤ M.mospValue := by
  obtain ⟨σ, hσ⟩ := M.exists_maxOpenStacks_eq_mospValue
  rw [← hσ]
  exact M.one_le_maxOpenStacks σ h

/-- **Easy direction**, with the `+ 1` on the pathwidth side, under the hypothesis
that makes it true. -/
theorem pathwidth_add_one_le_mospValue (h : ∃ c p, M.requires c p) :
    pathwidth M.mospGraph + 1 ≤ M.mospValue := by
  have h1 := M.one_le_mospValue h
  have h2 := M.pathwidth_le_mospValue_sub_one
  omega

/-- **Main theorem** (Yanasse 1997c; Linhares & Yanasse 2002): the MOSP value is
the pathwidth of the MOSP graph plus one, whenever some customer requires some
pattern. The hypothesis is necessary: without it both sides degenerate, to `0`
and to `1` respectively. -/
theorem mospValue_eq_pathwidth_add_one (h : ∃ c p, M.requires c p) :
    M.mospValue = pathwidth M.mospGraph + 1 :=
  le_antisymm M.mospValue_le_pathwidth_add_one (M.pathwidth_add_one_le_mospValue h)

/-- The degenerate case: with no requirement at all, no stack ever opens. -/
theorem mospValue_eq_zero_of_forall_not (h : ∀ c p, ¬ M.requires c p) : M.mospValue = 0 := by
  apply Nat.eq_zero_of_le_zero
  calc M.mospValue ≤ M.maxOpenStacks (Fintype.equivFin Pt) := M.mospValue_le_maxOpenStacks _
    _ ≤ 0 := by
      unfold maxOpenStacks
      by_cases hn : Fintype.card Pt = 0
      · simp [hn]
      · simp only [dite_eq_right hn]
        apply Finset.sup'_le
        intro i _
        unfold openStacksAt
        rw [Nat.le_zero, Finset.card_eq_zero, Finset.filter_eq_empty_iff]
        intro c _ hc
        obtain ⟨p, hp⟩ := M.exists_requires_of_isActive _ hc
        exact h c p hp

/-- The degenerate case on the graph side: with no requirement the MOSP graph has
no edges and pathwidth `0`, so the equality fails there by exactly one. -/
theorem pathwidth_mospGraph_eq_zero_of_forall_not (h : ∀ c p, ¬ M.requires c p) :
    pathwidth M.mospGraph = 0 := by
  have := M.pathwidth_le_mospValue_sub_one
  rw [M.mospValue_eq_zero_of_forall_not h] at this
  omega

end MOSPInstance

end MOSPFormalization
