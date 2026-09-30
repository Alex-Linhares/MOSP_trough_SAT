/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Interval thickness = node search (monotone game)

Table 1 of Linhares & Yanasse (2002), rows "interval thickness" and "node search
game", source [9] Kirousis & Papadimitriou (1985), *Interval graphs and
searching*, Discrete Mathematics 55, 181–184, Theorem (p. 182): "For any graph
G, ns(G) = θ(G)." Möhring (1990) restates it for gate matrix layout as
Theorem 3.9 (p. 34): `t(M) = ns(G_M)`.

## Definitions used

Nothing new is defined here. Both sides are the definitions of earlier items,
each faithful to its source:

* `intervalThickness` (`IntervalThickness.lean`, item 05): [9] p. 182, "the
  smallest max-clique over all interval supergraphs of G";
* `monotoneNodeSearch`, `nodeSearch` (`NodeSearch.lean`, item 10): the game of
  [9] p. 181, with and without the recontamination-free restriction of [10] §2.

## What is proved

* `monotoneNodeSearch_eq_intervalThickness` — **[9]'s Theorem for the
  monotone game**, for every graph with at least one edge: `mns(G) = θ(G)`.
  It is the chain `θ = pw + 1` (Möhring Prop. 3.5, item 05) and
  `mns = vs + 1 = pw + 1` ([10] Thm 4.1, monotone, item 10), not [9]'s own
  proof (which builds a strategy from an interval model by sweeping, and an
  interval model from a strategy by the time each node holds a searcher).
  `intervalSearch_chain` states the whole chain
  `θ = mns = vs + 1 = pw + 1` at once.
* In [9]'s two directions, per object: `monotoneNodeSearch_le_cliqueNum`
  (any interval supergraph `H`, in any linear order, gives `mns ≤ ω(H)`) and
  `intervalThickness_le_of_isMonotoneNodeSearch` (any monotone strategy of
  cost `k` gives an interval supergraph with `ω ≤ k`).
* Full game: `nodeSearch_le_intervalThickness` (no monotonicity needed), and
  `nodeSearch_eq_intervalThickness_of_monotonicity` — [9]'s Theorem as
  stated, from the named gap `NodeSearchMonotonicity` of item 10 ([10] Thm 2.3).
* Gate matrix layout, Möhring Thm 3.9 for the monotone game:
  `NetGateMatrix.tracks_eq_monotoneNodeSearch` (the net graph has an edge).
* **Counterexample to [9]'s Theorem as stated** ("for any graph G"): on every
  nonempty edgeless graph `ns = mns = 0` but `θ = 1`
  (`intervalThickness_of_edgeless`, `nodeSearch_ne_intervalThickness_of_edgeless`),
  concretely on one vertex (`nodeSearch_ne_intervalThickness_K1`). The same
  instance breaks Möhring's Thm 3.9 read literally: the `1 × 1` matrix `[1]`
  has `t = 1` and an edgeless net graph (`tracks_ne_monotoneNodeSearch_one`).
  Nothing is lost for Table 1: on these inputs both values are within ±1 of
  the open-stack number.

The full game's `θ ≤ ns` is item 10's gap and is not asserted; no `sorry`.
-/

import MOSPFormalization.Complex.IntervalThickness
import MOSPFormalization.Complex.NodeSearch
import MOSPFormalization.Complex.GateMatrix

namespace MOSPFormalization

namespace Complex

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- **Kirousis & Papadimitriou (1985), Theorem, for the monotone game**: on a
graph with at least one edge, `mns(G) = θ(G)`. -/
theorem monotoneNodeSearch_eq_intervalThickness {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    monotoneNodeSearch G = intervalThickness G := by
  have : Nonempty V := ⟨u₀⟩
  rw [monotoneNodeSearch_eq_pathwidth_add_one G h₀, intervalThickness_eq_pathwidth_add_one]

/-- The whole chain of Table 1's search rows, for a graph with an edge:
`θ = mns = vs + 1 = pw + 1`. -/
theorem intervalSearch_chain {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    intervalThickness G = monotoneNodeSearch G ∧
      monotoneNodeSearch G = vertexSeparation G + 1 ∧
      vertexSeparation G + 1 = pathwidth G + 1 :=
  ⟨(monotoneNodeSearch_eq_intervalThickness G h₀).symm,
    monotoneNodeSearch_eq_vertexSeparation_add_one G h₀,
    by rw [vertexSeparation_eq_pathwidth]⟩

/-- [9]'s direction `ns ≤ θ`, per model: any interval supergraph `H` of `G`,
with intervals in any linear order, bounds the monotone search number by its
clique number. -/
theorem monotoneNodeSearch_le_cliqueNum {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀)
    {α : Type*} [LinearOrder α] {H : SimpleGraph V} (m : IntervalModel α H) (hGH : G ≤ H) :
    monotoneNodeSearch G ≤ H.cliqueNum := by
  have : Nonempty V := ⟨u₀⟩
  rw [monotoneNodeSearch_eq_pathwidth_add_one G h₀]
  exact pathwidth_add_one_le_cliqueNum m hGH

/-- [9]'s direction `θ ≤ ns`, per strategy: a monotone strategy of cost `k`
yields an interval supergraph of clique number at most `k`. -/
theorem intervalThickness_le_of_isMonotoneNodeSearch {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) {k : ℕ}
    {ms : List (SearchMove V)} (h : IsMonotoneNodeSearch G k ms) :
    intervalThickness G ≤ k := by
  have : Nonempty V := ⟨u₀⟩
  rw [intervalThickness_eq_vertexSeparation_add_one]
  exact vertexSeparation_add_one_le_of_monotone G h₀ h

/-- The half of [9]'s Theorem that needs no monotonicity: `ns ≤ θ`. -/
theorem nodeSearch_le_intervalThickness {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G ≤ intervalThickness G :=
  (nodeSearch_le_monotoneNodeSearch G).trans
    (monotoneNodeSearch_eq_intervalThickness G h₀).le

/-- [9]'s Theorem for the full game, from the named gap
`NodeSearchMonotonicity` ([10] Theorem 2.3), which is not asserted. -/
theorem nodeSearch_eq_intervalThickness_of_monotonicity
    (hmono : NodeSearchMonotonicity G) {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G = intervalThickness G := by
  rw [hmono, monotoneNodeSearch_eq_intervalThickness G h₀]

/-! ### The edgeless exception -/

/-- On a nonempty edgeless graph `θ = 1` (every interval supergraph has a
vertex, so clique number at least one; the edgeless graph itself is interval). -/
theorem intervalThickness_of_edgeless [Nonempty V] (h : ∀ u v, ¬ G.Adj u v) :
    intervalThickness G = 1 := by
  rw [intervalThickness_eq_vertexSeparation_add_one, vertexSeparation_eq_zero_of_edgeless G h]

/-- **[9]'s Theorem fails as stated** ("for any graph G") on every nonempty
edgeless graph: `ns = 0`, `θ = 1`. -/
theorem nodeSearch_ne_intervalThickness_of_edgeless [Nonempty V] (h : ∀ u v, ¬ G.Adj u v) :
    nodeSearch G ≠ intervalThickness G := by
  rw [nodeSearch_of_edgeless G h, intervalThickness_of_edgeless G h]
  omega

/-- The same for the monotone game. -/
theorem monotoneNodeSearch_ne_intervalThickness_of_edgeless [Nonempty V]
    (h : ∀ u v, ¬ G.Adj u v) : monotoneNodeSearch G ≠ intervalThickness G := by
  rw [monotoneNodeSearch_of_edgeless G h, intervalThickness_of_edgeless G h]
  omega

/-- The smallest counterexample: one vertex, `ns = 0`, `θ = 1`. -/
theorem nodeSearch_ne_intervalThickness_K1 :
    nodeSearch (⊥ : SimpleGraph (Fin 1)) = 0 ∧
      intervalThickness (⊥ : SimpleGraph (Fin 1)) = 1 :=
  ⟨nodeSearch_of_edgeless _ fun _ _ h => h,
    intervalThickness_of_edgeless _ fun _ _ h => h⟩

/-! ### Gate matrix layout (Möhring 1990, Theorem 3.9) -/

namespace NetGateMatrix

variable {N Gt : Type*} [Fintype N] [DecidableEq N] [Fintype Gt] [DecidableEq Gt]
variable (M : NetGateMatrix N Gt) [DecidableRel M.conn] [DecidableRel M.netGraph.Adj]

/-- **Möhring (1990), Theorem 3.9, for the monotone game**: when two nets share
a gate, the least number of tracks equals the monotone node search number of
the net graph. -/
theorem tracks_eq_monotoneNodeSearch {n₀ n₁ : N} (h₀ : M.netGraph.Adj n₀ n₁) :
    M.tracks = monotoneNodeSearch M.netGraph := by
  obtain ⟨-, g, hg, -⟩ := id h₀
  rw [M.tracks_eq_pathwidth_add_one ⟨n₀, g, hg⟩,
    monotoneNodeSearch_eq_pathwidth_add_one _ h₀]

/-- And for the full game, from the named gap. -/
theorem tracks_eq_nodeSearch_of_monotonicity (hmono : NodeSearchMonotonicity M.netGraph)
    {n₀ n₁ : N} (h₀ : M.netGraph.Adj n₀ n₁) :
    M.tracks = nodeSearch M.netGraph := by
  rw [hmono, M.tracks_eq_monotoneNodeSearch h₀]

end NetGateMatrix

/-- The `1 × 1` matrix `[1]`. -/
def oneMatrix : NetGateMatrix (Fin 1) (Fin 1) := ⟨fun _ _ => True⟩

instance : DecidableRel oneMatrix.conn := fun _ _ => isTrue trivial

instance : DecidableRel oneMatrix.netGraph.Adj := fun n n' =>
  isFalse fun h => h.1 (Subsingleton.elim n n')

/-- **Möhring's Theorem 3.9 fails read literally** on the `1 × 1` matrix `[1]`:
one track, but the net graph has no edge, so its node search number is `0`. -/
theorem tracks_ne_monotoneNodeSearch_one :
    oneMatrix.tracks = 1 ∧ monotoneNodeSearch oneMatrix.netGraph = 0 := by
  have hedge : ∀ u v, ¬ oneMatrix.netGraph.Adj u v := fun u v h => h.1 (Subsingleton.elim u v)
  refine ⟨?_, monotoneNodeSearch_of_edgeless _ hedge⟩
  rw [oneMatrix.tracks_eq_pathwidth_add_one ⟨0, 0, trivial⟩, ← vertexSeparation_eq_pathwidth,
    vertexSeparation_eq_zero_of_edgeless _ hedge]

end Complex

end MOSPFormalization
