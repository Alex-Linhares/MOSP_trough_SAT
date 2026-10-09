/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Interval thickness = pathwidth + 1

Table 1 of Linhares & Yanasse (2002), row "interval thickness", source [5]
Kashiwabara & Fujisawa (1979), which is **not held**. The definition and the
relation are taken from two held sources instead.

## The source's definition

Kirousis & Papadimitriou (1985) [9], p. 182: "The interval thickness of a
graph G, denoted by θ(G), is the smallest max-clique over all interval
supergraphs of G." Möhring (1990) [6], p. 31: "The smallest clique size ω(H)
of an interval graph augmentation of G is also called the interval thickness
of G", with an interval graph being the intersection graph of a family of
intervals of a linear order (p. 28, eq. 3.2). A supergraph (augmentation) has
the same vertex set and more edges.

Formalised here:

* `IntervalModel α H` — closed intervals `[left v, right v]` of a linear order
  `α`, one per vertex, such that two distinct vertices are adjacent in `H`
  exactly when their intervals intersect;
* `IsIntervalGraph H` — `H` has an interval model in `ℕ`;
* `intervalThickness G` — the least `H.cliqueNum` (Mathlib's clique number)
  over interval graphs `H` with `G ≤ H` on the same vertex type.

Nothing in these definitions mentions bags or separation. The choice of `ℕ`
as the linear order does not matter: `pathwidth_add_one_le_cliqueNum` holds
for a model in *any* linear order, and a model in `ℕ` attains the bound, so
the least clique number over interval supergraphs with models in any linear
order is the same number.

## What is proved

Möhring Prop. 3.5 (p. 32), `pw(G) = θ(G) − 1`, by his two constructions:

* `bagGraph`, `bagModel`, `cliqueNum_bagGraph_le` — a path decomposition `D`
  gives the interval supergraph "share a bag", with each vertex's interval its
  range of bags; its cliques lie in single bags (the Helly lemma
  `PathDecomposition.exists_bag_of_isClique` of `MOSPGraph.lean`), so its
  clique number is at most `width D + 1`. Hence
  `intervalThickness_le_pathwidth_add_one`, with no hypothesis.
* `pointDecomposition`, `pathwidth_add_one_le_cliqueNum` — an interval model
  in any linear order gives a path decomposition whose bags are the sets of
  intervals through each left endpoint, in order; every bag is a clique of
  the interval graph. Hence `pathwidth G + 1 ≤ H.cliqueNum` for every interval
  supergraph `H` of `G`, when `V` is nonempty.
* `intervalThickness_eq_pathwidth_add_one` — `θ(G) = pw(G) + 1` under
  `[Nonempty V]`, and `intervalThickness_eq_vertexSeparation_add_one`.

## Edge cases

* No vertices: `intervalThickness_of_isEmpty`, `θ = 0` while `pw + 1 = 1`.
  This is the only exception, and the same convention as
  `paper1/complex_check.py` (`interval_thickness` returns 0 on the empty
  graph).
* Isolated vertices and disconnected graphs need nothing: an edgeless nonempty
  graph is its own interval supergraph (disjoint intervals), clique number 1.
-/

import MOSPFormalization.MOSPGraph
import MOSPFormalization.VSEquivPW

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### Interval graphs (Möhring p. 28) -/

/-- An interval model of `H` in the linear order `α`: a closed interval
`[left v, right v]` per vertex, with distinct vertices adjacent exactly when
their intervals intersect. -/
structure IntervalModel (α : Type*) [LinearOrder α] (H : SimpleGraph V) where
  /-- Left endpoint of each vertex's interval. -/
  left : V → α
  /-- Right endpoint of each vertex's interval. -/
  right : V → α
  /-- Intervals are nonempty. -/
  left_le_right : ∀ v, left v ≤ right v
  /-- Adjacency is intersection of the closed intervals. -/
  adj_iff : ∀ u v, u ≠ v → (H.Adj u v ↔ left u ≤ right v ∧ left v ≤ right u)

namespace IntervalModel

variable {α β : Type*} [LinearOrder α] [LinearOrder β] {H : SimpleGraph V}

/-- Transport an interval model along an order embedding. -/
def map (m : IntervalModel α H) (f : α ↪o β) : IntervalModel β H where
  left v := f (m.left v)
  right v := f (m.right v)
  left_le_right v := f.le_iff_le.mpr (m.left_le_right v)
  adj_iff u v huv := by simp only [f.le_iff_le]; exact m.adj_iff u v huv

end IntervalModel

/-- `H` is an interval graph: it has an interval model (in `ℕ`). -/
def IsIntervalGraph (H : SimpleGraph V) : Prop :=
  Nonempty (IntervalModel ℕ H)

/-- The **interval thickness** `θ(G)`: the smallest clique number of an
interval supergraph of `G` on the same vertices (Kirousis & Papadimitriou
1985, p. 182; Möhring 1990, p. 31). -/
noncomputable def intervalThickness (G : SimpleGraph V) : ℕ :=
  sInf {k | ∃ H : SimpleGraph V, G ≤ H ∧ IsIntervalGraph H ∧ H.cliqueNum = k}

/-! ### Decomposition → interval supergraph -/

section BagGraph

variable {G : SimpleGraph V}

/-- The graph "share a bag" of a path decomposition. -/
def bagGraph (D : PathDecomposition G) : SimpleGraph V where
  Adj u v := u ≠ v ∧ ∃ i, u ∈ D.bag i ∧ v ∈ D.bag i
  symm := ⟨fun _ _ ⟨h, i, hu, hv⟩ => ⟨h.symm, i, hv, hu⟩⟩
  loopless := ⟨fun _ h => h.1 rfl⟩

theorem le_bagGraph (D : PathDecomposition G) : G ≤ bagGraph D :=
  fun u v h => ⟨G.ne_of_adj h, D.edge_coverage u v h⟩

/-- The same bags, as a path decomposition of `bagGraph D`. -/
def bagDecomposition (D : PathDecomposition G) : PathDecomposition (bagGraph D) where
  length := D.length
  bag := D.bag
  vertex_coverage := D.vertex_coverage
  edge_coverage := fun _ _ h => h.2
  interval := D.interval

/-- Each vertex's interval is its range of bags. -/
noncomputable def bagModel (D : PathDecomposition G) :
    IntervalModel (Fin (D.length + 1)) (bagGraph D) where
  left := D.firstBag
  right := D.lastBag
  left_le_right := D.firstBag_le_lastBag
  adj_iff u v huv := by
    constructor
    · rintro ⟨-, i, hu, hv⟩
      rw [D.mem_bag_iff_between] at hu hv
      exact ⟨hu.1.trans hv.2, hv.1.trans hu.2⟩
    · rintro ⟨h1, h2⟩
      refine ⟨huv, max (D.firstBag u) (D.firstBag v), ?_, ?_⟩
      · rw [D.mem_bag_iff_between]
        exact ⟨le_max_left _ _, max_le (D.firstBag_le_lastBag u) h2⟩
      · rw [D.mem_bag_iff_between]
        exact ⟨le_max_right _ _, max_le h1 (D.firstBag_le_lastBag v)⟩

theorem isIntervalGraph_bagGraph (D : PathDecomposition G) :
    IsIntervalGraph (bagGraph D) :=
  ⟨(bagModel D).map (Fin.valOrderEmb _)⟩

/-- The clique number of the "share a bag" graph is at most `width + 1`. -/
theorem cliqueNum_bagGraph_le (D : PathDecomposition G) :
    (bagGraph D).cliqueNum ≤ D.width + 1 := by
  obtain ⟨s, hs⟩ := (bagGraph D).exists_isNClique_cliqueNum
  rw [← hs.card_eq]
  exact (bagDecomposition D).card_le_width_add_one_of_isClique s hs.isClique

end BagGraph

/-- `θ(G) ≤ pw(G) + 1`, with no hypothesis. -/
theorem intervalThickness_le_pathwidth_add_one (G : SimpleGraph V) :
    intervalThickness G ≤ pathwidth G + 1 := by
  obtain ⟨D, hD⟩ := exists_pathDecomposition_width_eq G
  calc intervalThickness G ≤ (bagGraph D).cliqueNum :=
        Nat.sInf_le ⟨bagGraph D, le_bagGraph D, isIntervalGraph_bagGraph D, rfl⟩
    _ ≤ D.width + 1 := cliqueNum_bagGraph_le D
    _ = pathwidth G + 1 := by rw [hD]

/-! ### Interval model → decomposition -/

section Points

variable {α : Type*} [LinearOrder α] {G H : SimpleGraph V}

/-- The left endpoints of a model: the points at which bags are taken. -/
def IntervalModel.points (m : IntervalModel α H) : Finset α :=
  Finset.univ.image m.left

theorem IntervalModel.points_card (m : IntervalModel α H) [Nonempty V] :
    m.points.card = m.points.card - 1 + 1 := by
  have : 0 < m.points.card :=
    Finset.card_pos.mpr (Finset.univ_nonempty.image _)
  omega

/-- The `i`-th left endpoint in increasing order. -/
def IntervalModel.point (m : IntervalModel α H) [Nonempty V] :
    Fin (m.points.card - 1 + 1) ↪o α :=
  m.points.orderEmbOfFin m.points_card

theorem IntervalModel.exists_point_eq (m : IntervalModel α H) [Nonempty V] (v : V) :
    ∃ i, m.point i = m.left v := by
  have : m.left v ∈ Set.range m.point := by
    rw [IntervalModel.point, Finset.range_orderEmbOfFin]
    exact Finset.mem_coe.mpr (Finset.mem_image_of_mem _ (Finset.mem_univ v))
  exact this

/-- The path decomposition of a model: bag `i` is the set of intervals
through the `i`-th left endpoint. -/
def pointDecomposition (m : IntervalModel α H) (hGH : G ≤ H) [Nonempty V] :
    PathDecomposition G where
  length := m.points.card - 1
  bag i := Finset.univ.filter (fun v => m.left v ≤ m.point i ∧ m.point i ≤ m.right v)
  vertex_coverage v := by
    obtain ⟨i, hi⟩ := m.exists_point_eq v
    exact ⟨i, by simp [hi, m.left_le_right v]⟩
  edge_coverage u v h := by
    have ⟨h1, h2⟩ := (m.adj_iff u v (G.ne_of_adj h)).mp (hGH h)
    rcases le_total (m.left u) (m.left v) with huv | huv
    · obtain ⟨i, hi⟩ := m.exists_point_eq v
      exact ⟨i, by simp [hi, huv, h2], by simp [hi, m.left_le_right v]⟩
    · obtain ⟨i, hi⟩ := m.exists_point_eq u
      exact ⟨i, by simp [hi, m.left_le_right u], by simp [hi, huv, h1]⟩
  interval v i j k hij hjk hi hk := by
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi hk ⊢
    exact ⟨hi.1.trans (m.point.monotone hij), (m.point.monotone hjk).trans hk.2⟩

/-- Every bag of `pointDecomposition` is a clique of the interval graph. -/
theorem pointDecomposition_bag_isClique (m : IntervalModel α H) (hGH : G ≤ H) [Nonempty V]
    (i : Fin ((pointDecomposition m hGH).length + 1)) :
    H.IsClique ((pointDecomposition m hGH).bag i : Set V) := by
  intro u hu v hv huv
  simp only [pointDecomposition, Finset.coe_filter, Finset.mem_univ, true_and] at hu hv
  exact (m.adj_iff u v huv).mpr ⟨hu.1.trans hv.2, hv.1.trans hu.2⟩

/-- **Model → decomposition**: for an interval model in any linear order of a
supergraph `H` of `G`, `pw(G) + 1 ≤ ω(H)`. -/
theorem pathwidth_add_one_le_cliqueNum [Nonempty V] (m : IntervalModel α H) (hGH : G ≤ H) :
    pathwidth G + 1 ≤ H.cliqueNum := by
  set D := pointDecomposition m hGH
  have hbag : ∀ i, (D.bag i).card ≤ H.cliqueNum := fun i =>
    (pointDecomposition_bag_isClique m hGH i).card_le_cliqueNum
  have hw : D.width + 1 ≤ H.cliqueNum := by
    have hpos : 0 < H.cliqueNum := Nat.pos_of_ne_zero (H.cliqueNum_ne_zero_of_finite)
    have : Finset.sup' Finset.univ
        (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
        (fun i => (D.bag i).card) ≤ H.cliqueNum :=
      Finset.sup'_le _ _ (fun i _ => hbag i)
    unfold PathDecomposition.width
    omega
  exact (Nat.add_le_add_right (pathwidth_le_width G D) 1).trans hw

end Points

/-! ### The theorem -/

/-- **Möhring Prop. 3.5**: `θ(G) = pw(G) + 1` for every graph with at least
one vertex. -/
theorem intervalThickness_eq_pathwidth_add_one [Nonempty V] (G : SimpleGraph V) :
    intervalThickness G = pathwidth G + 1 := by
  refine le_antisymm (intervalThickness_le_pathwidth_add_one G) ?_
  obtain ⟨D, -⟩ := exists_pathDecomposition_width_eq G
  have hne : {k | ∃ H : SimpleGraph V, G ≤ H ∧ IsIntervalGraph H ∧ H.cliqueNum = k}.Nonempty :=
    ⟨_, bagGraph D, le_bagGraph D, isIntervalGraph_bagGraph D, rfl⟩
  obtain ⟨H, hGH, ⟨m⟩, hk⟩ := Nat.sInf_mem hne
  unfold intervalThickness
  rw [← hk]
  exact pathwidth_add_one_le_cliqueNum m hGH

/-- `θ(G) = vs(G) + 1`, through Kinnersley (1992). -/
theorem intervalThickness_eq_vertexSeparation_add_one [Nonempty V] (G : SimpleGraph V)
    [DecidableRel G.Adj] :
    intervalThickness G = vertexSeparation G + 1 := by
  rw [intervalThickness_eq_pathwidth_add_one, vertexSeparation_eq_pathwidth]

/-- **Edge case**: with no vertices, `θ = 0` (while `pw + 1 = 1`). -/
theorem intervalThickness_of_isEmpty [IsEmpty V] (G : SimpleGraph V) :
    intervalThickness G = 0 := by
  obtain ⟨D, -⟩ := exists_pathDecomposition_width_eq G
  exact Nat.eq_zero_of_le_zero <|
    Nat.sInf_le ⟨bagGraph D, le_bagGraph D, isIntervalGraph_bagGraph D,
      (bagGraph D).cliqueNum_of_isEmpty⟩

end Complex

end MOSPFormalization
