/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Pathwidth of trees: the complete ternary tree and the size bound

Statement (2) of `paper1/todo.md` ("Lean the derived random-graph bounds"): the deterministic
cores of §2 of `reports/random_graph_pathwidth_survey.md`,

* (2b) the complete ternary tree of height `h` has pathwidth exactly `h`;
* (2a) every tree on `N` vertices has pathwidth at most `⌊log₃(2N + 1)⌋`.

Brute force first (`reports/scratch/empty_pair/check23.py`, 2026-10-30): (2a) on all 32,547
trees to 16 vertices, (2b) for `h = 1, 2, 3` (4, 13, 40 vertices) by the C solver; the refuter
of `reports/scratch/tree_bound/gossip.md` extended (2a) exactly to 24 vertices and (2b) to
`h = 4`.

## General lemmas

* `pathwidth_le_pathwidth_induce_add_card_compl` — `pathwidth G ≤ pathwidth G[S] + |V ∖ S|`
  (add the deleted vertices to every bag; `PathDecomposition.extend`), and its case
  `pathwidth_le_pathwidth_erase_add_one`, `pathwidth G ≤ pathwidth (G − v) + 1`.
* `pathwidth_induce_union_le_max` — for disjoint `A`, `B` with no edge between them,
  `pathwidth G[A ∪ B] ≤ max (pathwidth G[A]) (pathwidth G[B])` (concatenation,
  `PathDecomposition.cat`).
* `pathwidth_induce_le_of_forall_connected` — `pathwidth G[S] ≤ k` as soon as every
  connected `C ⊆ S` has `pathwidth G[C] ≤ k`: pathwidth is the maximum over the components.
  Proved by induction on `|S|`, splitting off the reachability class `reachSet G S v`.

## (2b): the complete ternary tree

* `triple G r` — three copies of `G` on `Option (Fin 3 × V)`, joined to a new root `none`
  through the three copies of `r`; `copyIso` identifies each copy with `G`.
* `pathwidth_triple_le` — `pathwidth (triple G r) ≤ pathwidth G + 1` (the two lemmas above).
* `pathwidth_add_one_le_triple` — the converse for connected `G`, by `branch_lemma`
  (`Sandwich.lean`) at the root; `pathwidth_triple` is the equality.
* `TVert h`, `ternaryTree h` — `TVert 0 = Unit`, `TVert (h+1) = Option (Fin 3 × TVert h)`,
  `ternaryTree (h+1) = triple (ternaryTree h) (troot h)`; `card_TVert`:
  `2·|TVert h| + 1 = 3^(h+1)`; `ternaryTree_connected`.
* `pathwidth_ternaryTree` — **`pathwidth (ternaryTree h) = h`**.

## (2a): the size bound for trees (sorry-free)

* `treeBound k` — `1, 6, 21, 66, 201, …`: `treeBound 0 = 1`,
  `treeBound (k+1) = 3·treeBound k + 3`, so `2·treeBound k + 3 = 5·3^k`
  (`two_mul_treeBound_add_three`). This is the classical threshold: the smallest tree of
  pathwidth `k + 1` has `treeBound k + 1 = 2, 7, 22, 67, …` vertices (Ellis, Sudborough &
  Turner 1994; Scheffler 1990), which the refuter confirmed exactly to 26 vertices.
* `tree_pathwidth_le_treeBound` — **every tree on at most `treeBound k` vertices has
  pathwidth at most `k`**; by induction on `k` through the path lemma, the splitting lemma and
  `pathwidth_induce_le_of_forall_connected`; the base case is the single vertex.
* `tree_pathwidth_le_log` — **`pathwidth T ≤ Nat.log 3 (2N + 1)`** for every tree `T` on
  `N` vertices, the survey's bound, as a corollary: if `3^k ≤ 2N + 1 < 3^(k+1)` then
  `2N + 3 ≤ 3·3^k + 1 ≤ 5·3^k`. The survey's form is weaker than the size bound by about
  `log₃ (5/3) ≈ 0.46`.

The two lemmas behind the induction, both elementary and neither needing the
Ellis–Sudborough–Turner characterisation:

* **The path lemma**, `tree_pathwidth_le_pathwidth_compl_path_add_one`: for a path `P` of a
  tree `T` (an injective `p : Fin m → V` with consecutive vertices adjacent, `IsPathSeq`),
  `pathwidth T ≤ pathwidth (T − P) + 1`. Proved in two layers.
  - General graphs, `pathwidth_le_of_pathAttachment`: if the vertices off an induced path are
    partitioned into pieces `H j`, every edge leaving `H j` goes to `p j`, and each piece has
    pathwidth `≤ k`, then `pathwidth G ≤ k + 1`. The decomposition
    (`exists_decomposition_along_path`) is built by induction along the path: block `j` is a
    decomposition of `G[H j]` with `p j` added to every bag (`PathDecomposition.extendTo`), and
    consecutive blocks are joined through the bag `{p j, p (j+1)}` by the gluing lemma
    `PathDecomposition.glue` (`glue_width_le`: width `≤ max (w₁, w₂, 1)` when `x` is in the last
    bag of the first decomposition, `y` in the first bag of the second, and `xy` is the only
    edge between the two sides).
  - Trees, `tree_exists_pathAttachment`: the pieces are
    `piece T p j = reachSet T (insert (p j) Pᶜ) (p j) ∖ {p j}`; their disjointness
    (`piece_disjoint`) and the inducedness of the path (`pathSeq_induced`) come from the bridge
    characterisation of acyclicity (`isAcyclic_iff_forall_adj_isBridge`) with the path edge
    `p j p (j+1)` as the bridge and `pathSeq_reachable_deleteEdge` (the tail of the path stays
    connected without that edge); the cover (`piece_cover`) by induction on a walk to `p 0`.
* **The splitting lemma**, `tree_exists_path_split`: a tree on at most `3m` vertices has a path
  such that every connected vertex set avoiding it has fewer than `m` vertices. Brute-forced
  first on every tree to 17 vertices at the binding `m = ⌈N/3⌉` (zero violations; tight at
  every `N`, the extremal trees being spiders). Proof through *branches*: `branch G v u` is
  the vertex set reachable from `u` in `G − v` (`reachSet`); in a tree the branches at `v`
  through different neighbours are disjoint (`branch_disjoint_of_ne`), the two branches of an
  edge partition `V` (`card_branch_add_card_branch`), and a branch at `u` through `w ≠ v` sits
  strictly inside the branch at `v` through `u` (`card_branch_lt`) — all by the bridge argument.
  - `exists_centroid`: a vertex all of whose branches have at most `N/2` vertices, by
    minimising the largest branch (`maxBranch`): a branch with more than half the vertices
    contains a neighbour whose branches are all smaller.
  - `exists_heavy_path`: inside a branch with fewer than `2m` vertices there is a path from its
    attachment such that every connected set of the branch avoiding the path has fewer than
    `m` vertices — at each vertex at most one sub-branch has `≥ m` vertices, walk into it,
    induct on the size.
  - At a centroid of a tree on `≤ 3m` vertices at most two branches have `≥ m` vertices (three
    would give `3m + 1`), and each has `< 2m`; the path is the heavy path of one, reversed, then
    the centroid, then the heavy path of the other. Paths are built as `List`s (`List.IsChain`,
    `Nodup`) and converted to `Fin` sequences at the end.

## Sharpness, and that the families are trees

* `extremalTree k` on `EVert k` — `extremalTree 0` is the edge `pathGraph 2`,
  `extremalTree (k+1) = triple (extremalTree k) (eroot k)`: the classical minimal trees of
  pathwidth `k + 1` (the refuter checked them exactly to `k = 4`, 202 vertices).
  `card_EVert : |EVert k| = treeBound k + 1`, `pathwidth_extremalTree : pathwidth = k + 1`,
  `treeBound_sharp` the conjunction: **the size bound is sharp for every `k`**.
* `triple_isTree` — `triple` of a tree is a tree: acyclicity through
  `isAcyclic_iff_forall_adj_isBridge`, each edge type separately — a root–copy edge
  disconnects its copy (`triple_not_reachable_root`), a copy edge `xy` disconnects the part
  of the copy reachable from `x` without it, together with the root and the other copies when
  the copy's root is on that side (`triple_not_reachable_copy`); both by `not_reachable_of_closed`
  (a set closed under adjacency separates). Hence `ternaryTree_isTree` and
  `extremalTree_isTree`, so (2b) and the sharpness statement are about trees.

Everything in this file is `sorry`-free, with axioms `propext`, `Classical.choice`,
`Quot.sound` (checked with `#print axioms` on 2026-10-30 on every theorem named above).

## Not done

* The probabilistic half of §2 (the components of `G(n, c/n)` for `c < 1` are trees or
  unicyclic of size `O(log n)`, and a ternary tree of size `Θ(log n)` occurs): Mathlib has no
  `G(n, p)`.
* `treeBound` is the *exact* threshold only given both halves; the file proves both
  (`tree_pathwidth_le_treeBound` and `treeBound_sharp`), but does not state the
  Ellis–Sudborough–Turner min–max characterisation of tree pathwidth itself.
-/

import MOSPFormalization.Sandwich
import MOSPFormalization.Minor

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V)

/-! ### Bags of a decomposition of an induced subgraph, read in the ambient graph -/

namespace PathDecomposition

variable {G}

/-- The `i`-th bag of a decomposition of `G[S]`, as a set of vertices of `G`; empty
beyond the last index. -/
def vbag {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) (i : ℕ) : Finset V :=
  if h : i < P.length + 1 then (P.bag ⟨i, h⟩).map (Function.Embedding.subtype _) else ∅

theorem mem_vbag_iff {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) (i : ℕ)
    (v : V) : v ∈ P.vbag i ↔ ∃ (hv : v ∈ S) (hi : i < P.length + 1), ⟨v, hv⟩ ∈ P.bag ⟨i, hi⟩ := by
  unfold vbag
  split_ifs with hi
  · simp only [Finset.mem_map, Function.Embedding.coe_subtype, Subtype.exists, Finset.mem_coe,
      exists_and_right, exists_eq_right, hi, exists_true_left]
  · simp [hi]

theorem vbag_subset {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) (i : ℕ) :
    P.vbag i ⊆ S := fun v hv => ((P.mem_vbag_iff i v).mp hv).1

theorem vbag_eq_of_mem {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    (i : Fin (P.length + 1)) : P.vbag i.val = (P.bag i).map (Function.Embedding.subtype _) := by
  unfold vbag; simp [i.isLt]

theorem card_vbag_le {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) (i : ℕ) :
    (P.vbag i).card ≤ P.width + 1 := by
  unfold vbag
  split_ifs with hi
  · rw [Finset.card_map]; exact P.bag_card_le_width_add_one _
  · simp

theorem lt_of_mem_vbag {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) {i : ℕ}
    {v : V} (h : v ∈ P.vbag i) : i < P.length + 1 := by
  obtain ⟨_, hi, _⟩ := (P.mem_vbag_iff i v).mp h; exact hi

theorem vbag_interval {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    {i j k : ℕ} (hij : i ≤ j) (hjk : j ≤ k) {v : V} (hi : v ∈ P.vbag i) (hk : v ∈ P.vbag k) :
    v ∈ P.vbag j := by
  obtain ⟨hv, hi', hi⟩ := (P.mem_vbag_iff i v).mp hi
  obtain ⟨_, hk', hk⟩ := (P.mem_vbag_iff k v).mp hk
  exact (P.mem_vbag_iff j v).mpr ⟨hv, by omega,
    P.interval ⟨v, hv⟩ ⟨i, hi'⟩ ⟨j, by omega⟩ ⟨k, hk'⟩ hij hjk hi hk⟩

theorem exists_mem_vbag {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    {v : V} (hv : v ∈ S) : ∃ i, i < P.length + 1 ∧ v ∈ P.vbag i := by
  obtain ⟨i, hi⟩ := P.vertex_coverage ⟨v, hv⟩
  exact ⟨i.val, i.isLt, (P.mem_vbag_iff _ v).mpr ⟨hv, i.isLt, hi⟩⟩

theorem exists_mem_vbag_of_adj {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    {u v : V} (hu : u ∈ S) (hv : v ∈ S) (huv : G.Adj u v) :
    ∃ i, i < P.length + 1 ∧ u ∈ P.vbag i ∧ v ∈ P.vbag i := by
  obtain ⟨i, hi, hj⟩ := P.edge_coverage ⟨u, hu⟩ ⟨v, hv⟩ ((SimpleGraph.induce_adj).mpr huv)
  exact ⟨i.val, i.isLt, (P.mem_vbag_iff _ u).mpr ⟨hu, i.isLt, hi⟩,
    (P.mem_vbag_iff _ v).mpr ⟨hv, i.isLt, hj⟩⟩

/-! ### L1: adding the deleted vertices to every bag -/

/-- A decomposition of `G[S]` with the vertices outside `S` added to every bag is a
decomposition of `G`. -/
def extend {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) :
    PathDecomposition G where
  length := P.length
  bag i := P.vbag i.val ∪ Sᶜ
  vertex_coverage v := by
    by_cases hv : v ∈ S
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hv
      exact ⟨⟨i, hi⟩, Finset.mem_union_left _ h⟩
    · exact ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.mem_union_right _ (Finset.mem_compl.mpr hv)⟩
  edge_coverage u v huv := by
    by_cases hu : u ∈ S <;> by_cases hv : v ∈ S
    · obtain ⟨i, hi, h1, h2⟩ := P.exists_mem_vbag_of_adj hu hv huv
      exact ⟨⟨i, hi⟩, Finset.mem_union_left _ h1, Finset.mem_union_left _ h2⟩
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hu
      exact ⟨⟨i, hi⟩, Finset.mem_union_left _ h, Finset.mem_union_right _ (Finset.mem_compl.mpr hv)⟩
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hv
      exact ⟨⟨i, hi⟩, Finset.mem_union_right _ (Finset.mem_compl.mpr hu), Finset.mem_union_left _ h⟩
    · exact ⟨⟨0, Nat.zero_lt_succ _⟩, Finset.mem_union_right _ (Finset.mem_compl.mpr hu),
        Finset.mem_union_right _ (Finset.mem_compl.mpr hv)⟩
  interval v i j k hij hjk hi hk := by
    rcases Finset.mem_union.mp hi with hi | hi
    · rcases Finset.mem_union.mp hk with hk | hk
      · exact Finset.mem_union_left _ (P.vbag_interval hij hjk hi hk)
      · exact Finset.mem_union_right _ hk
    · exact Finset.mem_union_right _ hi

theorem extend_width_le {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) :
    P.extend.width ≤ P.width + Sᶜ.card := by
  apply width_le_of_forall_card_le
  intro i
  calc (P.vbag i.val ∪ Sᶜ).card ≤ (P.vbag i.val).card + Sᶜ.card := Finset.card_union_le _ _
    _ ≤ P.width + 1 + Sᶜ.card := Nat.add_le_add_right (P.card_vbag_le _) _
    _ = P.width + Sᶜ.card + 1 := by ring

end PathDecomposition

/-- **Deleting vertices costs at most their number**: `pathwidth G ≤ pathwidth G[S] + |V ∖ S|`. -/
theorem pathwidth_le_pathwidth_induce_add_card_compl (S : Finset V) :
    pathwidth G ≤ pathwidth (G.induce (↑S : Set V)) + Sᶜ.card := by
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq (G.induce (↑S : Set V))
  rw [← hP]
  exact (pathwidth_le_width G P.extend).trans P.extend_width_le

/-- **Deleting one vertex costs at most one**: `pathwidth G ≤ pathwidth (G − v) + 1`. -/
theorem pathwidth_le_pathwidth_erase_add_one (v : V) :
    pathwidth G ≤ pathwidth (G.induce (↑(Finset.univ.erase v) : Set V)) + 1 := by
  have h := pathwidth_le_pathwidth_induce_add_card_compl G (Finset.univ.erase v)
  rwa [Finset.compl_erase, Finset.compl_univ, Finset.insert_empty, Finset.card_singleton] at h

/-! ### L2: concatenating decompositions of two parts with no edge between them -/

namespace PathDecomposition

variable {G}

/-- The bags of the concatenation of `P` (on `A`) and `Q` (on `B`), as vertex sets of `G`:
the bags of `P`, then the bags of `Q`. -/
def catBag {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (i : ℕ) : Finset V :=
  if i < P.length + 1 then P.vbag i else Q.vbag (i - (P.length + 1))

theorem catBag_subset {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (i : ℕ) : P.catBag Q i ⊆ A ∪ B := by
  unfold catBag; split_ifs
  · exact (P.vbag_subset i).trans Finset.subset_union_left
  · exact (Q.vbag_subset _).trans Finset.subset_union_right

theorem card_catBag_le {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (i : ℕ) :
    (P.catBag Q i).card ≤ max P.width Q.width + 1 := by
  unfold catBag; split_ifs
  · exact (P.card_vbag_le i).trans (Nat.add_le_add_right (le_max_left _ _) _)
  · exact (Q.card_vbag_le _).trans (Nat.add_le_add_right (le_max_right _ _) _)

theorem mem_catBag_of_mem_A {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (hAB : Disjoint A B) {i : ℕ} {v : V}
    (hvA : v ∈ A) : v ∈ P.catBag Q i ↔ v ∈ P.vbag i := by
  unfold catBag; split_ifs with hi
  · exact Iff.rfl
  · constructor
    · intro h; exact absurd (Q.vbag_subset _ h) (Finset.disjoint_left.mp hAB hvA)
    · intro h; exact absurd (P.lt_of_mem_vbag h) hi

theorem mem_catBag_of_mem_B {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (hAB : Disjoint A B) {i : ℕ} {v : V}
    (hvB : v ∈ B) : v ∈ P.catBag Q i ↔ P.length + 1 ≤ i ∧ v ∈ Q.vbag (i - (P.length + 1)) := by
  unfold catBag; split_ifs with hi
  · constructor
    · intro h; exact absurd (P.vbag_subset _ h) (Finset.disjoint_right.mp hAB hvB)
    · intro h; omega
  · exact ⟨fun h => ⟨by omega, h⟩, fun h => h.2⟩

/-- The concatenation: a decomposition of `G[A ∪ B]` when `A`, `B` are disjoint and no edge
of `G` joins them. -/
def cat {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (hAB : Disjoint A B)
    (hno : ∀ a ∈ A, ∀ b ∈ B, ¬ G.Adj a b) :
    PathDecomposition (G.induce (↑(A ∪ B) : Set V)) where
  length := P.length + Q.length + 1
  bag i := (P.catBag Q i.val).subtype (fun x => x ∈ A ∪ B)
  vertex_coverage v := by
    have hv := Finset.mem_coe.mp v.2
    rcases Finset.mem_union.mp hv with hA | hB
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hA
      refine ⟨⟨i, by omega⟩, Finset.mem_subtype.mpr ?_⟩
      exact (P.mem_catBag_of_mem_A Q hAB hA).mpr h
    · obtain ⟨i, hi, h⟩ := Q.exists_mem_vbag hB
      refine ⟨⟨i + (P.length + 1), by omega⟩, ?_⟩
      dsimp only
      rw [Finset.mem_subtype, P.mem_catBag_of_mem_B Q hAB hB]
      exact ⟨by omega, by simpa using h⟩
  edge_coverage u v huv := by
    have huv' : G.Adj u.1 v.1 := (SimpleGraph.induce_adj).mp huv
    have hu := Finset.mem_coe.mp u.2
    have hv := Finset.mem_coe.mp v.2
    rcases Finset.mem_union.mp hu with huA | huB <;> rcases Finset.mem_union.mp hv with hvA | hvB
    · obtain ⟨i, hi, h1, h2⟩ := P.exists_mem_vbag_of_adj huA hvA huv'
      exact ⟨⟨i, by omega⟩, Finset.mem_subtype.mpr ((P.mem_catBag_of_mem_A Q hAB huA).mpr h1),
        Finset.mem_subtype.mpr ((P.mem_catBag_of_mem_A Q hAB hvA).mpr h2)⟩
    · exact absurd huv' (hno _ huA _ hvB)
    · exact absurd huv'.symm (hno _ hvA _ huB)
    · obtain ⟨i, hi, h1, h2⟩ := Q.exists_mem_vbag_of_adj huB hvB huv'
      refine ⟨⟨i + (P.length + 1), by omega⟩, ?_, ?_⟩
      · dsimp only
        rw [Finset.mem_subtype, P.mem_catBag_of_mem_B Q hAB huB]
        exact ⟨by omega, by simpa using h1⟩
      · dsimp only
        rw [Finset.mem_subtype, P.mem_catBag_of_mem_B Q hAB hvB]
        exact ⟨by omega, by simpa using h2⟩
  interval v i j k hij hjk hi hk := by
    rw [Finset.mem_subtype] at hi hk ⊢
    have hij' : i.val ≤ j.val := hij
    have hjk' : j.val ≤ k.val := hjk
    rcases Finset.mem_union.mp (Finset.mem_coe.mp v.2) with hA | hB
    · rw [P.mem_catBag_of_mem_A Q hAB hA] at hi hk ⊢
      exact P.vbag_interval hij' hjk' hi hk
    · rw [P.mem_catBag_of_mem_B Q hAB hB] at hi hk ⊢
      refine ⟨by omega, Q.vbag_interval (i := i.val - (P.length + 1))
        (k := k.val - (P.length + 1)) (by omega) (by omega) hi.2 hk.2⟩

theorem cat_width_le {A B : Finset V} (P : PathDecomposition (G.induce (↑A : Set V)))
    (Q : PathDecomposition (G.induce (↑B : Set V))) (hAB : Disjoint A B)
    (hno : ∀ a ∈ A, ∀ b ∈ B, ¬ G.Adj a b) :
    (P.cat Q hAB hno).width ≤ max P.width Q.width := by
  apply width_le_of_forall_card_le
  intro i
  show ((P.catBag Q i.val).subtype (fun x => x ∈ A ∪ B)).card ≤ _
  rw [Finset.card_subtype]
  exact (Finset.card_filter_le _ _).trans (P.card_catBag_le Q _)

end PathDecomposition

/-- **Pathwidth of a disjoint union**: if no edge joins the disjoint sets `A` and `B`, then
`pathwidth G[A ∪ B] ≤ max (pathwidth G[A]) (pathwidth G[B])`. -/
theorem pathwidth_induce_union_le_max (A B : Finset V) (hAB : Disjoint A B)
    (hno : ∀ a ∈ A, ∀ b ∈ B, ¬ G.Adj a b) :
    pathwidth (G.induce (↑(A ∪ B) : Set V)) ≤
      max (pathwidth (G.induce (↑A : Set V))) (pathwidth (G.induce (↑B : Set V))) := by
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq (G.induce (↑A : Set V))
  obtain ⟨Q, hQ⟩ := exists_pathDecomposition_width_eq (G.induce (↑B : Set V))
  rw [← hP, ← hQ]
  exact (pathwidth_le_width _ (P.cat Q hAB hno)).trans (P.cat_width_le Q hAB hno)

/-! ### Three copies joined to a root -/

section Triple

variable {G}

/-- Three copies of `G` joined to a new root `none` through the three copies of `r`. -/
def triple (G : SimpleGraph V) (r : V) : SimpleGraph (Option (Fin 3 × V)) where
  Adj a b := match a, b with
    | none, none => False
    | none, some (_, x) => x = r
    | some (_, x), none => x = r
    | some (i, x), some (j, y) => i = j ∧ G.Adj x y
  symm := ⟨by
    rintro (_ | ⟨i, x⟩) (_ | ⟨j, y⟩) h
    · exact h
    · exact h
    · exact h
    · exact ⟨h.1.symm, h.2.symm⟩⟩
  loopless := ⟨by
    rintro (_ | ⟨i, x⟩) h
    · exact h
    · exact G.loopless.irrefl x h.2⟩

variable (G) (r : V)

@[simp] theorem triple_adj_none_none : ¬ (triple G r).Adj none none := id
@[simp] theorem triple_adj_none_some (i : Fin 3) (x : V) :
    (triple G r).Adj none (some (i, x)) ↔ x = r := Iff.rfl
@[simp] theorem triple_adj_some_none (i : Fin 3) (x : V) :
    (triple G r).Adj (some (i, x)) none ↔ x = r := Iff.rfl
@[simp] theorem triple_adj_some_some (i j : Fin 3) (x y : V) :
    (triple G r).Adj (some (i, x)) (some (j, y)) ↔ i = j ∧ G.Adj x y := Iff.rfl

theorem card_triple : Fintype.card (Option (Fin 3 × V)) = 3 * Fintype.card V + 1 := by
  simp [Fintype.card_option, Fintype.card_prod]

/-- The `i`-th copy of `G` inside `triple G r`, as a homomorphism. -/
def copyHom (i : Fin 3) : G →g triple G r where
  toFun x := some (i, x)
  map_rel' h := ⟨rfl, h⟩

/-- The vertex set of the `i`-th copy. -/
def copySet (i : Fin 3) : Finset (Option (Fin 3 × V)) :=
  Finset.univ.image (fun x : V => some (i, x))

theorem mem_copySet_iff (i : Fin 3) (a : Option (Fin 3 × V)) :
    a ∈ copySet (V := V) i ↔ ∃ x, a = some (i, x) := by
  simp [copySet, eq_comm]

theorem none_not_mem_copySet (i : Fin 3) : (none : Option (Fin 3 × V)) ∉ copySet (V := V) i := by
  rw [mem_copySet_iff]; rintro ⟨x, h⟩; cases h

theorem some_mem_copySet (i : Fin 3) (x : V) : some (i, x) ∈ copySet (V := V) i :=
  (mem_copySet_iff i _).mpr ⟨x, rfl⟩

theorem copySet_disjoint {i j : Fin 3} (hij : i ≠ j) :
    Disjoint (copySet (V := V) i) (copySet (V := V) j) := by
  rw [Finset.disjoint_left]
  intro a hi hj
  obtain ⟨x, rfl⟩ := (mem_copySet_iff i a).mp hi
  obtain ⟨y, hy⟩ := (mem_copySet_iff j _).mp hj
  exact hij (Prod.mk.inj (Option.some.inj hy)).1

theorem copySet_not_adj {i j : Fin 3} (hij : i ≠ j) :
    ∀ a ∈ copySet (V := V) i, ∀ b ∈ copySet (V := V) j, ¬ (triple G r).Adj a b := by
  intro a ha b hb h
  obtain ⟨x, rfl⟩ := (mem_copySet_iff i a).mp ha
  obtain ⟨y, rfl⟩ := (mem_copySet_iff j b).mp hb
  exact hij h.1

theorem copyHom_bijective (i : Fin 3) :
    Function.Bijective (fun x : V => (⟨some (i, x), some_mem_copySet i x⟩ :
      ↥(↑(copySet (V := V) i) : Set (Option (Fin 3 × V))))) := by
  constructor
  · intro x y h
    have := congrArg Subtype.val h
    exact (Prod.mk.inj (Option.some.inj this)).2
  · rintro ⟨a, ha⟩
    obtain ⟨x, rfl⟩ := (mem_copySet_iff i a).mp (Finset.mem_coe.mp ha)
    exact ⟨x, rfl⟩

/-- The `i`-th copy is an isomorphic copy of `G`. -/
noncomputable def copyIso (i : Fin 3) :
    G ≃g (triple G r).induce (↑(copySet (V := V) i) : Set (Option (Fin 3 × V))) where
  toEquiv := Equiv.ofBijective _ (copyHom_bijective i)
  map_rel_iff' := by
    intro x y
    simp [Equiv.ofBijective_apply]

theorem pathwidth_copy (i : Fin 3) :
    pathwidth ((triple G r).induce (↑(copySet (V := V) i) : Set (Option (Fin 3 × V)))) =
      pathwidth G :=
  (pathwidth_eq_of_iso (copyIso G r i)).symm

theorem copy_connected (hG : G.Connected) (i : Fin 3) :
    ((triple G r).induce (↑(copySet (V := V) i) : Set (Option (Fin 3 × V)))).Connected :=
  (SimpleGraph.Iso.connected_iff (copyIso G r i)).mp hG

/-- The complement of the three copies is the root alone. -/
theorem compl_copySets :
    (copySet (V := V) 0 ∪ copySet 1 ∪ copySet 2)ᶜ = {(none : Option (Fin 3 × V))} := by
  ext a
  rcases a with _ | ⟨i, x⟩
  · simp [none_not_mem_copySet]
  · simp only [Finset.mem_compl, Finset.mem_union, mem_copySet_iff, Finset.mem_singleton,
      reduceCtorEq, iff_false, not_not]
    fin_cases i
    · exact Or.inl (Or.inl ⟨x, rfl⟩)
    · exact Or.inl (Or.inr ⟨x, rfl⟩)
    · exact Or.inr ⟨x, rfl⟩

/-- **Upper bound**: `pathwidth (triple G r) ≤ pathwidth G + 1` (concatenate the three
copies, add the root to every bag). -/
theorem pathwidth_triple_le : pathwidth (triple G r) ≤ pathwidth G + 1 := by
  have h1 := pathwidth_le_pathwidth_induce_add_card_compl (triple G r)
    (copySet (V := V) 0 ∪ copySet 1 ∪ copySet 2)
  rw [compl_copySets, Finset.card_singleton] at h1
  refine h1.trans (Nat.add_le_add_right ?_ 1)
  have h01 : Disjoint (copySet (V := V) 0) (copySet 1) := copySet_disjoint (by decide)
  have h012 : Disjoint (copySet (V := V) 0 ∪ copySet 1) (copySet 2) :=
    Finset.disjoint_union_left.mpr ⟨copySet_disjoint (by decide), copySet_disjoint (by decide)⟩
  have hno01 := copySet_not_adj G r (V := V) (i := 0) (j := 1) (by decide)
  have hno012 : ∀ a ∈ copySet (V := V) 0 ∪ copySet 1, ∀ b ∈ copySet (V := V) 2,
      ¬ (triple G r).Adj a b := by
    intro a ha b hb
    rcases Finset.mem_union.mp ha with ha | ha
    · exact copySet_not_adj G r (by decide) a ha b hb
    · exact copySet_not_adj G r (by decide) a ha b hb
  calc pathwidth ((triple G r).induce ↑(copySet (V := V) 0 ∪ copySet 1 ∪ copySet 2))
      ≤ max (pathwidth ((triple G r).induce ↑(copySet (V := V) 0 ∪ copySet 1)))
          (pathwidth ((triple G r).induce ↑(copySet (V := V) 2))) :=
        pathwidth_induce_union_le_max _ _ _ h012 hno012
    _ ≤ max (max (pathwidth ((triple G r).induce ↑(copySet (V := V) 0)))
          (pathwidth ((triple G r).induce ↑(copySet (V := V) 1))))
          (pathwidth ((triple G r).induce ↑(copySet (V := V) 2))) :=
        max_le_max_right _ (pathwidth_induce_union_le_max _ _ _ h01 hno01)
    _ = pathwidth G := by
        rw [pathwidth_copy, pathwidth_copy, pathwidth_copy, max_self, max_self]

/-- **Lower bound**: if `G` is connected, `pathwidth G + 1 ≤ pathwidth (triple G r)`, by the
branch lemma at the root. -/
theorem pathwidth_add_one_le_triple (hG : G.Connected) :
    pathwidth G + 1 ≤ pathwidth (triple G r) := by
  classical
  refine branch_lemma (G := triple G r) none (copySet 0) (copySet 1) (copySet 2) (pathwidth G)
    (none_not_mem_copySet 0) (none_not_mem_copySet 1) (none_not_mem_copySet 2)
    (copySet_disjoint (i := 0) (j := 1) (by decide)) (copySet_disjoint (i := 0) (j := 2) (by decide))
    (copySet_disjoint (i := 1) (j := 2) (by decide))
    (copy_connected G r hG 0) (copy_connected G r hG 1) (copy_connected G r hG 2)
    ⟨some (0, r), some_mem_copySet 0 r, rfl⟩ ⟨some (1, r), some_mem_copySet 1 r, rfl⟩
    ⟨some (2, r), some_mem_copySet 2 r, rfl⟩
    (pathwidth_copy G r 0).ge (pathwidth_copy G r 1).ge (pathwidth_copy G r 2).ge

/-- `pathwidth (triple G r) = pathwidth G + 1` for connected `G`. -/
theorem pathwidth_triple (hG : G.Connected) : pathwidth (triple G r) = pathwidth G + 1 :=
  le_antisymm (pathwidth_triple_le G r) (pathwidth_add_one_le_triple G r hG)

theorem triple_connected (hG : G.Connected) : (triple G r).Connected := by
  rw [SimpleGraph.connected_iff_exists_forall_reachable]
  refine ⟨none, ?_⟩
  rintro (_ | ⟨i, x⟩)
  · exact SimpleGraph.Reachable.refl _
  · have h1 : (triple G r).Reachable none (some (i, r)) :=
      SimpleGraph.Adj.reachable ((triple_adj_none_some G r i r).mpr rfl)
    have h2 : (triple G r).Reachable (some (i, r)) (some (i, x)) :=
      SimpleGraph.Reachable.map (copyHom G r i) (hG.preconnected r x)
    exact h1.trans h2

end Triple

/-! ### The complete ternary tree -/

/-- The vertices of the complete ternary tree of height `h`: a root, or a child index and a
vertex of a tree of height `h − 1`. -/
def TVert : ℕ → Type
  | 0 => Unit
  | h + 1 => Option (Fin 3 × TVert h)

instance instFintypeTVert : (h : ℕ) → Fintype (TVert h)
  | 0 => inferInstanceAs (Fintype Unit)
  | h + 1 => letI := instFintypeTVert h; inferInstanceAs (Fintype (Option (Fin 3 × TVert h)))

instance instDecidableEqTVert : (h : ℕ) → DecidableEq (TVert h)
  | 0 => inferInstanceAs (DecidableEq Unit)
  | h + 1 => letI := instDecidableEqTVert h; inferInstanceAs (DecidableEq (Option (Fin 3 × TVert h)))

/-- The root of the tree of height `h`. -/
def troot : (h : ℕ) → TVert h
  | 0 => ()
  | _ + 1 => none

/-- The complete ternary tree of height `h`: a single vertex at height `0`; at height `h + 1`,
three trees of height `h` joined to a new root through their roots. -/
def ternaryTree : (h : ℕ) → SimpleGraph (TVert h)
  | 0 => ⊥
  | h + 1 => triple (ternaryTree h) (troot h)

/-- The tree of height `h` has `(3^(h+1) − 1)/2` vertices. -/
theorem card_TVert : ∀ h, 2 * Fintype.card (TVert h) + 1 = 3 ^ (h + 1)
  | 0 => by
    have : Fintype.card (TVert 0) = 1 := Fintype.card_unit
    rw [this]; norm_num
  | h + 1 => by
    have ih := card_TVert h
    have : Fintype.card (TVert (h + 1)) = 3 * Fintype.card (TVert h) + 1 := card_triple
    rw [this, pow_succ, ← ih]
    ring

theorem ternaryTree_connected : ∀ h, (ternaryTree h).Connected
  | 0 => by
    rw [SimpleGraph.connected_iff_exists_forall_reachable]
    exact ⟨troot 0, fun v => by
      have : v = troot 0 := Subsingleton.elim (α := Unit) v (troot 0)
      rw [this]⟩
  | h + 1 => triple_connected _ _ (ternaryTree_connected h)

/-- **The complete ternary tree of height `h` has pathwidth `h`.** -/
theorem pathwidth_ternaryTree : ∀ h, pathwidth (ternaryTree h) = h
  | 0 => by
    apply le_antisymm _ (Nat.zero_le _)
    have := pathwidth_le_card_sub_one (ternaryTree 0)
    have hc : Fintype.card (TVert 0) = 1 := Fintype.card_unit
    omega
  | h + 1 => by
    show pathwidth (triple (ternaryTree h) (troot h)) = h + 1
    rw [pathwidth_triple _ _ (ternaryTree_connected h), pathwidth_ternaryTree h]

/-! ### Pathwidth is decided by the connected pieces -/

/-- The vertices of `S` reachable from `v` inside `G[S]`. -/
noncomputable def reachSet (S : Finset V) (v : V) : Finset V :=
  open Classical in
  S.filter (fun w => ∃ (hv : v ∈ S) (hw : w ∈ S), (G.induce (↑S : Set V)).Reachable ⟨v, hv⟩ ⟨w, hw⟩)

theorem mem_reachSet_iff (S : Finset V) (v w : V) :
    w ∈ reachSet G S v ↔ w ∈ S ∧ ∃ (hv : v ∈ S) (hw : w ∈ S),
      (G.induce (↑S : Set V)).Reachable ⟨v, hv⟩ ⟨w, hw⟩ := by
  unfold reachSet; simp only [Finset.mem_filter]

theorem reachSet_subset (S : Finset V) (v : V) : reachSet G S v ⊆ S :=
  fun _ hw => ((mem_reachSet_iff G S v _).mp hw).1

theorem self_mem_reachSet (S : Finset V) {v : V} (hv : v ∈ S) : v ∈ reachSet G S v :=
  (mem_reachSet_iff G S v v).mpr ⟨hv, hv, hv, SimpleGraph.Reachable.refl _⟩

/-- No edge leaves the reachability class. -/
theorem not_adj_reachSet_sdiff (S : Finset V) (v : V) :
    ∀ a ∈ reachSet G S v, ∀ b ∈ S \ reachSet G S v, ¬ G.Adj a b := by
  intro a ha b hb hab
  obtain ⟨haS, hv, haS', hreach⟩ := (mem_reachSet_iff G S v a).mp ha
  have hbS := (Finset.mem_sdiff.mp hb).1
  apply (Finset.mem_sdiff.mp hb).2
  refine (mem_reachSet_iff G S v b).mpr ⟨hbS, hv, hbS, hreach.trans ?_⟩
  exact SimpleGraph.Adj.reachable ((SimpleGraph.induce_adj (s := (↑S : Set V))
    (u := ⟨a, haS⟩) (v := ⟨b, hbS⟩)).mpr hab)

/-- The reachability class induces a connected subgraph. -/
theorem reachSet_connected (S : Finset V) {v : V} (hv : v ∈ S) :
    (G.induce (↑(reachSet G S v) : Set V)).Connected := by
  apply SimpleGraph.induce_connected_of_patches v (Finset.mem_coe.mpr (self_mem_reachSet G S hv))
  intro w hw
  obtain ⟨hwS, hv', hwS', hreach⟩ := (mem_reachSet_iff G S v w).mp (Finset.mem_coe.mp hw)
  obtain ⟨p⟩ := hreach
  let p' : G.Walk v w := p.map (SimpleGraph.Embedding.induce (↑S : Set V)).toHom
  refine ⟨{x | x ∈ p'.support}, ?_, p'.start_mem_support, p'.end_mem_support,
    (p'.connected_induce_support).preconnected _ _⟩
  intro x hx
  have hx' : x ∈ (p.map (SimpleGraph.Embedding.induce (↑S : Set V)).toHom).support := hx
  rw [SimpleGraph.Walk.support_map, List.mem_map] at hx'
  obtain ⟨q, hq, rfl⟩ := hx'
  refine Finset.mem_coe.mpr ((mem_reachSet_iff G S v _).mpr ⟨q.2, hv, q.2, ⟨p.takeUntil q hq⟩⟩)

/-- **Pathwidth is decided by the connected pieces**: if every connected vertex set
`C ⊆ S` has `pathwidth G[C] ≤ k`, then `pathwidth G[S] ≤ k`. (The connected pieces of
`G[S]` are its components; concatenating their decompositions, `pathwidth_induce_union_le_max`,
gives the claim by induction on `|S|`.) -/
theorem pathwidth_induce_le_of_forall_connected (S : Finset V) (k : ℕ)
    (h : ∀ C : Finset V, C ⊆ S → (G.induce (↑C : Set V)).Connected →
      pathwidth (G.induce (↑C : Set V)) ≤ k) :
    pathwidth (G.induce (↑S : Set V)) ≤ k := by
  induction S using Finset.strongInduction with
  | H S ih =>
    rcases S.eq_empty_or_nonempty with rfl | ⟨v, hv⟩
    · have := pathwidth_le_card_sub_one (G.induce (↑(∅ : Finset V) : Set V))
      simp at this
      omega
    · have hC := reachSet_subset G S v
      have hsplit : reachSet G S v ∪ (S \ reachSet G S v) = S := Finset.union_sdiff_of_subset hC
      rw [← hsplit]
      refine (pathwidth_induce_union_le_max G _ _ Finset.disjoint_sdiff
        (not_adj_reachSet_sdiff G S v)).trans (max_le ?_ ?_)
      · exact h _ hC (reachSet_connected G S hv)
      · refine ih (S \ reachSet G S v) ?_ (fun C hCS hc => h C (hCS.trans Finset.sdiff_subset) hc)
        exact Finset.sdiff_ssubset hC ⟨v, self_mem_reachSet G S hv⟩

/-! ### Trees: the size bound -/

/-- A path in `T`, given as an injective enumeration of its vertices with consecutive
vertices adjacent. -/
def IsPathSeq (T : SimpleGraph V) {m : ℕ} (p : Fin m → V) : Prop :=
  Function.Injective p ∧ ∀ i j : Fin m, i.val + 1 = j.val → T.Adj (p i) (p j)

/-! ### Gluing two decompositions through one edge -/

namespace PathDecomposition

variable {G}

/-- A decomposition of `G[R]` whose bags are given, as vertex sets of `G`, by `B`, has
`vbag i = B i` for `i ≤ length`. -/
theorem vbag_eq_of_bag_eq {R : Finset V} (D : PathDecomposition (G.induce (↑R : Set V)))
    (B : ℕ → Finset V) (hB : ∀ i, B i ⊆ R)
    (hbag : ∀ i : Fin (D.length + 1), D.bag i = (B i.val).subtype (fun x => x ∈ R))
    {i : ℕ} (hi : i < D.length + 1) : D.vbag i = B i := by
  ext v
  rw [mem_vbag_iff]
  constructor
  · rintro ⟨hv, hi', h⟩
    rw [hbag, Finset.mem_subtype] at h
    exact h
  · intro h
    refine ⟨hB i h, hi, ?_⟩
    rw [hbag, Finset.mem_subtype]
    exact h

/-- Add `R ∖ S` to every bag: a decomposition of `G[S]` becomes one of `G[R]`, `S ⊆ R`. -/
def extendTo {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V))) (R : Finset V)
    (hSR : S ⊆ R) : PathDecomposition (G.induce (↑R : Set V)) where
  length := P.length
  bag i := (P.vbag i.val ∪ (R \ S)).subtype (fun x => x ∈ R)
  vertex_coverage v := by
    have hvR := Finset.mem_coe.mp v.2
    by_cases hv : v.1 ∈ S
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hv
      exact ⟨⟨i, hi⟩, Finset.mem_subtype.mpr (Finset.mem_union_left _ h)⟩
    · exact ⟨⟨0, Nat.zero_lt_succ _⟩,
        Finset.mem_subtype.mpr (Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨hvR, hv⟩))⟩
  edge_coverage u v huv := by
    have huv' : G.Adj u.1 v.1 := (SimpleGraph.induce_adj).mp huv
    have huR := Finset.mem_coe.mp u.2
    have hvR := Finset.mem_coe.mp v.2
    by_cases hu : u.1 ∈ S <;> by_cases hv : v.1 ∈ S
    · obtain ⟨i, hi, h1, h2⟩ := P.exists_mem_vbag_of_adj hu hv huv'
      exact ⟨⟨i, hi⟩, Finset.mem_subtype.mpr (Finset.mem_union_left _ h1),
        Finset.mem_subtype.mpr (Finset.mem_union_left _ h2)⟩
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hu
      exact ⟨⟨i, hi⟩, Finset.mem_subtype.mpr (Finset.mem_union_left _ h),
        Finset.mem_subtype.mpr (Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨hvR, hv⟩))⟩
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hv
      exact ⟨⟨i, hi⟩,
        Finset.mem_subtype.mpr (Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨huR, hu⟩)),
        Finset.mem_subtype.mpr (Finset.mem_union_left _ h)⟩
    · exact ⟨⟨0, Nat.zero_lt_succ _⟩,
        Finset.mem_subtype.mpr (Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨huR, hu⟩)),
        Finset.mem_subtype.mpr (Finset.mem_union_right _ (Finset.mem_sdiff.mpr ⟨hvR, hv⟩))⟩
  interval v i j k hij hjk hi hk := by
    rw [Finset.mem_subtype] at hi hk ⊢
    rcases Finset.mem_union.mp hi with hi | hi
    · rcases Finset.mem_union.mp hk with hk | hk
      · exact Finset.mem_union_left _ (P.vbag_interval (i := i.val) (j := j.val) (k := k.val)
          hij hjk hi hk)
      · exact Finset.mem_union_right _ hk
    · exact Finset.mem_union_right _ hi

theorem extendTo_width_le {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    (R : Finset V) (hSR : S ⊆ R) : (P.extendTo R hSR).width ≤ P.width + (R \ S).card := by
  apply width_le_of_forall_card_le
  intro i
  show ((P.vbag i.val ∪ (R \ S)).subtype (fun x => x ∈ R)).card ≤ _
  rw [Finset.card_subtype]
  calc ((P.vbag i.val ∪ (R \ S)).filter (fun x => x ∈ R)).card
      ≤ (P.vbag i.val ∪ (R \ S)).card := Finset.card_filter_le _ _
    _ ≤ (P.vbag i.val).card + (R \ S).card := Finset.card_union_le _ _
    _ ≤ P.width + 1 + (R \ S).card := Nat.add_le_add_right (P.card_vbag_le _) _
    _ = P.width + (R \ S).card + 1 := by ring

theorem vbag_extendTo {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    (R : Finset V) (hSR : S ⊆ R) {i : ℕ} (hi : i < P.length + 1) :
    (P.extendTo R hSR).vbag i = P.vbag i ∪ (R \ S) :=
  vbag_eq_of_bag_eq _ (fun i => P.vbag i ∪ (R \ S))
    (fun i => Finset.union_subset ((P.vbag_subset i).trans hSR) Finset.sdiff_subset)
    (fun _ => rfl) hi

theorem extendTo_length {S : Finset V} (P : PathDecomposition (G.induce (↑S : Set V)))
    (R : Finset V) (hSR : S ⊆ R) : (P.extendTo R hSR).length = P.length := rfl

section Glue

variable {X Y : Finset V} (P : PathDecomposition (G.induce (↑X : Set V)))
  (Q : PathDecomposition (G.induce (↑Y : Set V))) (x y : V)

/-- The bags of the gluing: those of `P`, then `{x, y}`, then those of `Q`. -/
def glueBag (i : ℕ) : Finset V :=
  if i < P.length + 1 then P.vbag i
  else if i = P.length + 1 then {x, y} else Q.vbag (i - (P.length + 2))

theorem glueBag_subset (hx : x ∈ X) (hy : y ∈ Y) (i : ℕ) : glueBag P Q x y i ⊆ X ∪ Y := by
  unfold glueBag; split_ifs
  · exact (P.vbag_subset i).trans Finset.subset_union_left
  · intro v hv
    rcases Finset.mem_insert.mp hv with rfl | hv
    · exact Finset.mem_union_left _ hx
    · exact Finset.mem_union_right _ (Finset.mem_singleton.mp hv ▸ hy)
  · exact (Q.vbag_subset _).trans Finset.subset_union_right

theorem card_glueBag_le (i : ℕ) :
    (glueBag P Q x y i).card ≤ max (max P.width Q.width) 1 + 1 := by
  unfold glueBag; split_ifs
  · exact (P.card_vbag_le i).trans (Nat.add_le_add_right ((le_max_left _ _).trans (le_max_left _ _)) _)
  · exact (Finset.card_le_two).trans (by have := le_max_right (max P.width Q.width) 1; omega)
  · exact (Q.card_vbag_le _).trans (Nat.add_le_add_right ((le_max_right _ _).trans (le_max_left _ _)) _)

theorem mem_glueBag_of_mem_vbag_P {i : ℕ} {v : V} (h : v ∈ P.vbag i) : v ∈ glueBag P Q x y i := by
  unfold glueBag; rw [if_pos (P.lt_of_mem_vbag h)]; exact h

theorem mem_glueBag_of_mem_vbag_Q {i : ℕ} {v : V} (h : v ∈ Q.vbag i) :
    v ∈ glueBag P Q x y (i + (P.length + 2)) := by
  unfold glueBag
  rw [if_neg (by omega), if_neg (by omega), Nat.add_sub_cancel]
  exact h

theorem mem_glueBag_mid : x ∈ glueBag P Q x y (P.length + 1) ∧ y ∈ glueBag P Q x y (P.length + 1) := by
  unfold glueBag
  rw [if_neg (by omega), if_pos rfl]
  simp

variable (hXY : Disjoint X Y) (hx : x ∈ X) (hy : y ∈ Y)
include hXY hx hy

theorem mem_glueBag_iff_of_mem_X {v : V} (hv : v ∈ X) (hvx : v ≠ x) (i : ℕ) :
    v ∈ glueBag P Q x y i ↔ v ∈ P.vbag i := by
  unfold glueBag; split_ifs with h1 h2
  · exact Iff.rfl
  · constructor
    · intro h
      rcases Finset.mem_insert.mp h with h | h
      · exact absurd h hvx
      · exact absurd hv (Finset.disjoint_right.mp hXY (Finset.mem_singleton.mp h ▸ hy))
    · intro h; exact absurd (P.lt_of_mem_vbag h) h1
  · constructor
    · intro h; exact absurd hv (Finset.disjoint_right.mp hXY (Q.vbag_subset _ h))
    · intro h; exact absurd (P.lt_of_mem_vbag h) h1

theorem mem_glueBag_iff_of_mem_Y {v : V} (hv : v ∈ Y) (hvy : v ≠ y) (i : ℕ) :
    v ∈ glueBag P Q x y i ↔ P.length + 2 ≤ i ∧ v ∈ Q.vbag (i - (P.length + 2)) := by
  unfold glueBag; split_ifs with h1 h2
  · constructor
    · intro h; exact absurd hv (Finset.disjoint_left.mp hXY (P.vbag_subset _ h))
    · intro h; omega
  · constructor
    · intro h
      rcases Finset.mem_insert.mp h with h | h
      · exact absurd hv (Finset.disjoint_left.mp hXY (h ▸ hx))
      · exact absurd (Finset.mem_singleton.mp h) hvy
    · intro h; omega
  · exact ⟨fun h => ⟨by omega, h⟩, fun h => h.2⟩

theorem mem_glueBag_x_iff (i : ℕ) :
    x ∈ glueBag P Q x y i ↔ x ∈ P.vbag i ∨ i = P.length + 1 := by
  unfold glueBag; split_ifs with h1 h2
  · exact ⟨Or.inl, fun h => by rcases h with h | h; exact h; omega⟩
  · simp [h2]
  · constructor
    · intro h; exact absurd hx (Finset.disjoint_left.mp hXY · (Q.vbag_subset _ h))
    · intro h; rcases h with h | h; exact absurd (P.lt_of_mem_vbag h) h1; exact absurd h h2

theorem mem_glueBag_y_iff (i : ℕ) :
    y ∈ glueBag P Q x y i ↔ i = P.length + 1 ∨ (P.length + 2 ≤ i ∧ y ∈ Q.vbag (i - (P.length + 2))) := by
  unfold glueBag; split_ifs with h1 h2
  · constructor
    · intro h; exact absurd hy (Finset.disjoint_left.mp hXY (P.vbag_subset _ h))
    · intro h; omega
  · simp [h2]
  · constructor
    · intro h; exact Or.inr ⟨by omega, h⟩
    · intro h; rcases h with h | h; exact absurd h h2; exact h.2

variable (hedge : ∀ a ∈ X, ∀ b ∈ Y, G.Adj a b → a = x ∧ b = y)
  (hPx : x ∈ P.vbag P.length) (hQy : y ∈ Q.vbag 0)
include hedge hPx hQy

/-- **Gluing**: decompositions of `G[X]` and `G[Y]`, with `x` in the last bag of the first
and `y` in the first bag of the second, glue through the bag `{x, y}` into a decomposition of
`G[X ∪ Y]` when `xy` is the only edge between `X` and `Y`. -/
def glue : PathDecomposition (G.induce (↑(X ∪ Y) : Set V)) where
  length := P.length + Q.length + 2
  bag i := (glueBag P Q x y i.val).subtype (fun v => v ∈ X ∪ Y)
  vertex_coverage v := by
    rcases Finset.mem_union.mp (Finset.mem_coe.mp v.2) with hv | hv
    · obtain ⟨i, hi, h⟩ := P.exists_mem_vbag hv
      exact ⟨⟨i, by omega⟩, Finset.mem_subtype.mpr (mem_glueBag_of_mem_vbag_P P Q x y h)⟩
    · obtain ⟨i, hi, h⟩ := Q.exists_mem_vbag hv
      exact ⟨⟨i + (P.length + 2), by omega⟩,
        Finset.mem_subtype.mpr (mem_glueBag_of_mem_vbag_Q P Q x y h)⟩
  edge_coverage u v huv := by
    have huv' : G.Adj u.1 v.1 := (SimpleGraph.induce_adj).mp huv
    rcases Finset.mem_union.mp (Finset.mem_coe.mp u.2) with hu | hu <;>
      rcases Finset.mem_union.mp (Finset.mem_coe.mp v.2) with hv | hv
    · obtain ⟨i, hi, h1, h2⟩ := P.exists_mem_vbag_of_adj hu hv huv'
      exact ⟨⟨i, by omega⟩, Finset.mem_subtype.mpr (mem_glueBag_of_mem_vbag_P P Q x y h1),
        Finset.mem_subtype.mpr (mem_glueBag_of_mem_vbag_P P Q x y h2)⟩
    · obtain ⟨rfl, rfl⟩ := hedge _ hu _ hv huv'
      exact ⟨⟨P.length + 1, by omega⟩, Finset.mem_subtype.mpr (mem_glueBag_mid P Q _ _).1,
        Finset.mem_subtype.mpr (mem_glueBag_mid P Q _ _).2⟩
    · obtain ⟨rfl, rfl⟩ := hedge _ hv _ hu huv'.symm
      exact ⟨⟨P.length + 1, by omega⟩, Finset.mem_subtype.mpr (mem_glueBag_mid P Q _ _).2,
        Finset.mem_subtype.mpr (mem_glueBag_mid P Q _ _).1⟩
    · obtain ⟨i, hi, h1, h2⟩ := Q.exists_mem_vbag_of_adj hu hv huv'
      exact ⟨⟨i + (P.length + 2), by omega⟩,
        Finset.mem_subtype.mpr (mem_glueBag_of_mem_vbag_Q P Q x y h1),
        Finset.mem_subtype.mpr (mem_glueBag_of_mem_vbag_Q P Q x y h2)⟩
  interval v i j k hij hjk hi hk := by
    rw [Finset.mem_subtype] at hi hk ⊢
    have hij' : i.val ≤ j.val := hij
    have hjk' : j.val ≤ k.val := hjk
    rcases Finset.mem_union.mp (Finset.mem_coe.mp v.2) with hv | hv
    · by_cases hvx : v.1 = x
      · rw [hvx] at hi hk ⊢
        rw [mem_glueBag_x_iff P Q x y hXY hx hy] at hi hk ⊢
        by_cases hj : j.val = P.length + 1
        · exact Or.inr hj
        · rcases Nat.lt_or_gt_of_ne hj with hj | hj
          · have hi' : x ∈ P.vbag i.val := by
              rcases hi with hi | hi; exact hi; omega
            exact Or.inl (P.vbag_interval hij' (by omega) hi' hPx)
          · have hk' : x ∈ P.vbag k.val := by
              rcases hk with hk | hk; exact hk; omega
            have := P.lt_of_mem_vbag hk'
            omega
      · rw [mem_glueBag_iff_of_mem_X P Q x y hXY hx hy hv hvx] at hi hk ⊢
        exact P.vbag_interval hij' hjk' hi hk
    · by_cases hvy : v.1 = y
      · rw [hvy] at hi hk ⊢
        rw [mem_glueBag_y_iff P Q x y hXY hx hy] at hi hk ⊢
        by_cases hj : j.val = P.length + 1
        · exact Or.inl hj
        · rcases Nat.lt_or_gt_of_ne hj with hj | hj
          · rcases hi with hi | hi <;> omega
          · have hk' : y ∈ Q.vbag (k.val - (P.length + 2)) := by
              rcases hk with hk | hk; omega; exact hk.2
            exact Or.inr ⟨by omega, Q.vbag_interval (i := 0) (j := j.val - (P.length + 2))
              (k := k.val - (P.length + 2)) (Nat.zero_le _) (by omega) hQy hk'⟩
      · rw [mem_glueBag_iff_of_mem_Y P Q x y hXY hx hy hv hvy] at hi hk ⊢
        exact ⟨by omega, Q.vbag_interval (i := i.val - (P.length + 2))
          (k := k.val - (P.length + 2)) (by omega) (by omega) hi.2 hk.2⟩

theorem glue_width_le : (glue P Q x y hXY hx hy hedge hPx hQy).width ≤ max (max P.width Q.width) 1 := by
  apply width_le_of_forall_card_le
  intro i
  show ((glueBag P Q x y i.val).subtype (fun v => v ∈ X ∪ Y)).card ≤ _
  rw [Finset.card_subtype]
  exact (Finset.card_filter_le _ _).trans (card_glueBag_le P Q x y _)

theorem glue_length : (glue P Q x y hXY hx hy hedge hPx hQy).length = P.length + Q.length + 2 := rfl

theorem glue_vbag {i : ℕ} (hi : i < P.length + Q.length + 2 + 1) :
    (glue P Q x y hXY hx hy hedge hPx hQy).vbag i = glueBag P Q x y i :=
  vbag_eq_of_bag_eq _ (glueBag P Q x y) (glueBag_subset P Q x y hx hy) (fun _ => rfl) hi

theorem glue_vbag_zero : (glue P Q x y hXY hx hy hedge hPx hQy).vbag 0 = P.vbag 0 := by
  rw [glue_vbag P Q x y hXY hx hy hedge hPx hQy (by omega)]
  unfold glueBag; rw [if_pos (by omega)]

theorem glue_vbag_last :
    (glue P Q x y hXY hx hy hedge hPx hQy).vbag (P.length + Q.length + 2) = Q.vbag Q.length := by
  rw [glue_vbag P Q x y hXY hx hy hedge hPx hQy (by omega)]
  unfold glueBag; rw [if_neg (by omega), if_neg (by omega)]
  congr 1; omega

end Glue

end PathDecomposition

/-! ### Along a path: the induction -/

/-- The pieces `H j` hanging from the vertices `p j` of a path: they avoid the path, are
pairwise disjoint, every edge leaving `H j` goes to `p j`, and the path is induced. -/
structure PathAttachment {m : ℕ} (p : Fin m → V) (H : Fin m → Finset V) : Prop where
  avoid : ∀ j i, p i ∉ H j
  disjoint : ∀ j l, j ≠ l → Disjoint (H j) (H l)
  attach : ∀ j, ∀ w ∈ H j, ∀ u, G.Adj w u → u ∈ H j ∨ u = p j
  induced : ∀ i j, G.Adj (p i) (p j) → i.val + 1 = j.val ∨ j.val + 1 = i.val

/-- Along a path `p 0, …, p m` with attached pieces `H j` of pathwidth `≤ k`, the vertices
`range p ∪ ⋃ H j` have a decomposition of width `≤ k + 1` whose first bag contains `p 0` and
whose last bag contains `p m`: block `j` is a decomposition of `G[H j]` with `p j` in every
bag, and consecutive blocks glue through `{p j, p (j+1)}`. -/
theorem exists_decomposition_along_path (k : ℕ) :
    ∀ (m : ℕ) (p : Fin (m + 1) → V) (H : Fin (m + 1) → Finset V), IsPathSeq G p →
      PathAttachment G p H → (∀ j, pathwidth (G.induce (↑(H j) : Set V)) ≤ k) →
      ∀ U : Finset V, U = Finset.univ.image p ∪ Finset.univ.biUnion H →
      ∃ D : PathDecomposition (G.induce (↑U : Set V)),
        D.width ≤ k + 1 ∧ p 0 ∈ D.vbag 0 ∧ p (Fin.last m) ∈ D.vbag D.length
  | 0, p, H, hp, hH, hk, U, hU => by
    obtain ⟨D0, hD0⟩ := exists_pathDecomposition_width_eq (G.induce (↑(H 0) : Set V))
    have hsub : H 0 ⊆ U := by
      rw [hU]; exact Finset.subset_union_right.trans' (Finset.subset_biUnion_of_mem H (Finset.mem_univ 0))
    have hp0U : p 0 ∈ U := by
      rw [hU]; exact Finset.mem_union_left _ (Finset.mem_image_of_mem p (Finset.mem_univ 0))
    have hdiff : U \ H 0 ⊆ {p 0} := by
      intro v hv
      rw [Finset.mem_sdiff, hU, Finset.mem_union, Finset.mem_image, Finset.mem_biUnion] at hv
      rcases hv with ⟨⟨i, -, rfl⟩ | ⟨j, -, hj⟩, hv⟩
      · rw [Fin.fin_one_eq_zero i]; exact Finset.mem_singleton_self _
      · rw [Fin.fin_one_eq_zero j] at hj; exact absurd hj hv
    have hp0 : p 0 ∈ U \ H 0 := Finset.mem_sdiff.mpr ⟨hp0U, hH.avoid 0 0⟩
    refine ⟨D0.extendTo U hsub, ?_, ?_, ?_⟩
    · refine (D0.extendTo_width_le U hsub).trans ?_
      have := Finset.card_le_card hdiff
      rw [Finset.card_singleton] at this
      rw [hD0]
      have := hk 0
      omega
    · rw [D0.vbag_extendTo U hsub (Nat.zero_lt_succ _)]
      exact Finset.mem_union_right _ hp0
    · rw [D0.extendTo_length, D0.vbag_extendTo U hsub (Nat.lt_succ_self _)]
      exact Finset.mem_union_right _ hp0
  | m + 1, p, H, hp, hH, hk, U, hU => by
    -- the shorter path
    obtain ⟨p', hp'⟩ : ∃ p' : Fin (m + 1) → V, p' = p ∘ Fin.succ := ⟨_, rfl⟩
    obtain ⟨H', hH'⟩ : ∃ H' : Fin (m + 1) → Finset V, H' = H ∘ Fin.succ := ⟨_, rfl⟩
    have hp'app : ∀ i, p' i = p i.succ := fun i => by rw [hp']; rfl
    have hH'app : ∀ j, H' j = H j.succ := fun j => by rw [hH']; rfl
    have hp'seq : IsPathSeq G p' := by
      refine ⟨fun a b h => Fin.succ_injective _ (hp.1 (by rwa [hp'app, hp'app] at h)), ?_⟩
      intro i j hij
      rw [hp'app, hp'app]
      exact hp.2 i.succ j.succ (by simp only [Fin.val_succ]; omega)
    have hH'att : PathAttachment G p' H' := by
      refine ⟨fun j i => by rw [hp'app, hH'app]; exact hH.avoid j.succ i.succ,
        fun j l hjl => by rw [hH'app, hH'app]; exact hH.disjoint _ _ (fun h => hjl (Fin.succ_injective _ h)),
        fun j w hw u hwu => by rw [hH'app] at hw ⊢; rw [hp'app]; exact hH.attach j.succ w hw u hwu,
        fun i j hij => ?_⟩
      rw [hp'app, hp'app] at hij
      have := hH.induced i.succ j.succ hij
      simp only [Fin.val_succ] at this
      omega
    obtain ⟨U', hU'⟩ : ∃ U' : Finset V, U' = Finset.univ.image p' ∪ Finset.univ.biUnion H' := ⟨_, rfl⟩
    obtain ⟨D', hD'w, hD'0, hD'l⟩ := exists_decomposition_along_path k m p' H' hp'seq hH'att
      (fun j => by rw [hH'app]; exact hk j.succ) U' hU'
    -- the first block
    obtain ⟨X, hX⟩ : ∃ X : Finset V, X = insert (p 0) (H 0) := ⟨_, rfl⟩
    obtain ⟨D0, hD0⟩ := exists_pathDecomposition_width_eq (G.induce (↑(H 0) : Set V))
    have hsub : H 0 ⊆ X := by rw [hX]; exact Finset.subset_insert _ _
    have hp0X : p 0 ∈ X := by rw [hX]; exact Finset.mem_insert_self _ _
    have hp0 : p 0 ∈ X \ H 0 := Finset.mem_sdiff.mpr ⟨hp0X, hH.avoid 0 0⟩
    have hdiff : X \ H 0 ⊆ {p 0} := by
      intro v hv
      rw [Finset.mem_sdiff, hX, Finset.mem_insert] at hv
      rcases hv with ⟨rfl | hv, hv'⟩
      · exact Finset.mem_singleton_self _
      · exact absurd hv hv'
    have hPXw : (D0.extendTo X hsub).width ≤ k + 1 := by
      refine (D0.extendTo_width_le X hsub).trans ?_
      have := Finset.card_le_card hdiff
      rw [Finset.card_singleton] at this
      rw [hD0]
      have := hk 0
      omega
    have hPXlast : p 0 ∈ (D0.extendTo X hsub).vbag (D0.extendTo X hsub).length := by
      rw [D0.extendTo_length, D0.vbag_extendTo X hsub (Nat.lt_succ_self _)]
      exact Finset.mem_union_right _ hp0
    have hPX0 : p 0 ∈ (D0.extendTo X hsub).vbag 0 := by
      rw [D0.vbag_extendTo X hsub (Nat.zero_lt_succ _)]
      exact Finset.mem_union_right _ hp0
    -- the pieces of the second part
    have hmemU' : ∀ v, v ∈ U' ↔ (∃ i : Fin (m + 1), v = p i.succ) ∨ ∃ j : Fin (m + 1), v ∈ H j.succ := by
      intro v
      simp only [hU', Finset.mem_union, Finset.mem_image, Finset.mem_biUnion, Finset.mem_univ,
        true_and, hp'app, hH'app, eq_comm]
    have hp0U' : p 0 ∉ U' := by
      rw [hmemU']
      rintro (⟨i, hi⟩ | ⟨j, hj⟩)
      · exact Fin.succ_ne_zero i (hp.1 hi.symm)
      · exact hH.avoid _ _ hj
    have hH0U' : ∀ w ∈ H 0, w ∉ U' := by
      intro w hw hwU'
      rw [hmemU'] at hwU'
      rcases hwU' with ⟨i, rfl⟩ | ⟨j, hj⟩
      · exact hH.avoid _ _ hw
      · exact Finset.disjoint_left.mp (hH.disjoint 0 j.succ (Fin.succ_ne_zero j).symm) hw hj
    have hXY : Disjoint X U' := by
      rw [Finset.disjoint_left]
      intro v hv
      rw [hX] at hv
      rcases Finset.mem_insert.mp hv with rfl | hv
      · exact hp0U'
      · exact hH0U' v hv
    have hedge : ∀ a ∈ X, ∀ b ∈ U', G.Adj a b → a = p 0 ∧ b = p 1 := by
      intro a ha b hb hab
      have ha0 : a = p 0 := by
        rw [hX] at ha
        rcases Finset.mem_insert.mp ha with rfl | ha
        · rfl
        · rcases hH.attach 0 a ha b hab with hb0 | rfl
          · exact absurd hb (hH0U' b hb0)
          · exact absurd hb hp0U'
      subst ha0
      refine ⟨rfl, ?_⟩
      rw [hmemU'] at hb
      rcases hb with ⟨i, rfl⟩ | ⟨j, hj⟩
      · have := hH.induced 0 i.succ hab
        simp only [Fin.val_zero, Fin.val_succ] at this
        have hi : i.succ = 1 := Fin.ext (by simp only [Fin.val_succ, Fin.val_one]; omega)
        rw [hi]
      · rcases hH.attach _ b hj _ hab.symm with h | h
        · exact absurd h (hH.avoid _ _)
        · exact absurd (hp.1 h) (Fin.succ_ne_zero j).symm
    have hD'0' : p 1 ∈ D'.vbag 0 := by
      rw [hp'app, Fin.succ_zero_eq_one] at hD'0; exact hD'0
    have hD'l' : p (Fin.last (m + 1)) ∈ D'.vbag D'.length := by
      rw [hp'app, Fin.succ_last] at hD'l; exact hD'l
    have hp1U' : p 1 ∈ U' := by
      rw [hmemU']; exact Or.inl ⟨0, by rw [Fin.succ_zero_eq_one]⟩
    -- glue
    have hUeq : U = X ∪ U' := by
      rw [hU]
      ext v
      simp only [Finset.mem_union, Finset.mem_image, Finset.mem_biUnion, Finset.mem_univ,
        true_and, hX, Finset.mem_insert, hmemU', Fin.exists_fin_succ, eq_comm]
      tauto
    rw [hUeq]
    refine ⟨(D0.extendTo X hsub).glue D' (p 0) (p 1) hXY hp0X hp1U' hedge hPXlast hD'0', ?_, ?_, ?_⟩
    · refine (PathDecomposition.glue_width_le _ _ _ _ _ _ _ _ _ _).trans ?_
      exact max_le (max_le hPXw hD'w) (by omega)
    · rw [PathDecomposition.glue_vbag_zero]; exact hPX0
    · rw [PathDecomposition.glue_length, PathDecomposition.glue_vbag_last]; exact hD'l'

/-- **The path lemma, general form**: if the vertices off an induced path `p` are partitioned
into pieces `H j`, each attached to `p j` only, of pathwidth `≤ k`, then
`pathwidth G ≤ k + 1`. -/
theorem pathwidth_le_of_pathAttachment {m : ℕ} (p : Fin m → V) (H : Fin m → Finset V)
    (hp : IsPathSeq G p) (hH : PathAttachment G p H)
    (hcover : ∀ v, v ∉ Set.range p → ∃ j, v ∈ H j) (k : ℕ)
    (hk : ∀ j, pathwidth (G.induce (↑(H j) : Set V)) ≤ k) : pathwidth G ≤ k + 1 := by
  rcases m with _ | m
  · rcases isEmpty_or_nonempty V with hV | ⟨⟨v⟩⟩
    · have := pathwidth_le_card_sub_one G
      rw [Fintype.card_eq_zero] at this
      omega
    · obtain ⟨j, -⟩ := hcover v (by rw [Set.range_eq_empty p]; exact Set.notMem_empty v)
      exact j.elim0
  · have hU : Finset.univ.image p ∪ Finset.univ.biUnion H = Finset.univ := by
      apply Finset.eq_univ_of_forall
      intro v
      by_cases hv : v ∈ Set.range p
      · obtain ⟨i, rfl⟩ := hv
        exact Finset.mem_union_left _ (Finset.mem_image_of_mem p (Finset.mem_univ i))
      · obtain ⟨j, hj⟩ := hcover v hv
        exact Finset.mem_union_right _ (Finset.mem_biUnion.mpr ⟨j, Finset.mem_univ _, hj⟩)
    obtain ⟨D, hD, -, -⟩ := exists_decomposition_along_path G k m p H hp hH hk _ rfl
    have h1 : pathwidth (G.induce (↑(Finset.univ.image p ∪ Finset.univ.biUnion H) : Set V)) ≤ k + 1 :=
      (pathwidth_le_width _ D).trans hD
    rw [hU, Finset.coe_univ] at h1
    rw [← pathwidth_eq_of_iso (SimpleGraph.induceUnivIso G)]
    exact h1

/-! ### Trees: the attachment partition -/

/-! #### The pieces hanging from a path -/

section Pieces

variable {m : ℕ} (p : Fin m → V)

/-- The vertex set of the path. -/
def pathSet : Finset V := Finset.univ.image p

theorem mem_pathSet_iff (v : V) : v ∈ pathSet p ↔ ∃ i, p i = v := by
  simp [pathSet]

theorem pathVertex_mem_pathSet (i : Fin m) : p i ∈ pathSet p :=
  (mem_pathSet_iff p _).mpr ⟨i, rfl⟩

/-- The vertices off the path, together with `p j`. -/
def pieceSet (j : Fin m) : Finset V := insert (p j) (pathSet p)ᶜ

theorem mem_pieceSet_iff (j : Fin m) (v : V) : v ∈ pieceSet p j ↔ v = p j ∨ v ∉ pathSet p := by
  simp [pieceSet]

theorem pathVertex_mem_pieceSet {j : Fin m} (hp : Function.Injective p) {i : Fin m}
    (h : p i ∈ pieceSet p j) : i = j := by
  rcases (mem_pieceSet_iff p j _).mp h with h | h
  · exact hp h
  · exact absurd (pathVertex_mem_pathSet p i) h

/-- The piece hanging from `p j`: the vertices off the path reachable from `p j` without
using any other path vertex. -/
noncomputable def piece (j : Fin m) : Finset V := (reachSet G (pieceSet p j) (p j)).erase (p j)

theorem mem_piece_iff (j : Fin m) (w : V) :
    w ∈ piece G p j ↔ w ≠ p j ∧ w ∈ reachSet G (pieceSet p j) (p j) := Finset.mem_erase

theorem piece_subset_compl (j : Fin m) : piece G p j ⊆ (pathSet p)ᶜ := by
  intro w hw
  obtain ⟨hne, hw⟩ := (mem_piece_iff G p j w).mp hw
  have := reachSet_subset G _ _ hw
  rcases (mem_pieceSet_iff p j w).mp this with h | h
  · exact absurd h hne
  · exact Finset.mem_compl.mpr h

theorem pathVertex_not_mem_piece (j i : Fin m) : p i ∉ piece G p j := fun h =>
  Finset.mem_compl.mp (piece_subset_compl G p j h) (pathVertex_mem_pathSet p i)

theorem pathVertex_mem_pieceSet_self (j : Fin m) : p j ∈ pieceSet p j :=
  (mem_pieceSet_iff p j _).mpr (Or.inl rfl)

/-- A vertex off the path adjacent to `p j` is in its piece. -/
theorem mem_piece_of_adj {j : Fin m} {w : V} (hw : w ∉ pathSet p) (hadj : G.Adj (p j) w) :
    w ∈ piece G p j := by
  have hwS : w ∈ pieceSet p j := (mem_pieceSet_iff p j w).mpr (Or.inr hw)
  refine (mem_piece_iff G p j w).mpr ⟨fun h => hw (h ▸ pathVertex_mem_pathSet p j), ?_⟩
  refine (mem_reachSet_iff G _ _ w).mpr ⟨hwS, pathVertex_mem_pieceSet_self p j, hwS, ?_⟩
  exact SimpleGraph.Adj.reachable ((SimpleGraph.induce_adj).mpr hadj)

/-- A vertex off the path adjacent to a vertex of a piece is in that piece. -/
theorem mem_piece_of_adj_piece {j : Fin m} {w u : V} (hw : w ∈ piece G p j) (hu : u ∉ pathSet p)
    (hadj : G.Adj w u) : u ∈ piece G p j := by
  obtain ⟨hw0, hw⟩ := (mem_piece_iff G p j w).mp hw
  obtain ⟨hwS, hj, hwS', hreach⟩ := (mem_reachSet_iff G _ _ w).mp hw
  have huS : u ∈ pieceSet p j := (mem_pieceSet_iff p j u).mpr (Or.inr hu)
  refine (mem_piece_iff G p j u).mpr ⟨fun h => hu (h ▸ pathVertex_mem_pathSet p j), ?_⟩
  refine (mem_reachSet_iff G _ _ u).mpr ⟨huS, hj, huS, hreach.trans ?_⟩
  exact SimpleGraph.Adj.reachable ((SimpleGraph.induce_adj (u := ⟨w, hwS'⟩) (v := ⟨u, huS⟩)).mpr hadj)

/-- Adjacency survives the deletion of a different edge. -/
theorem deleteEdges_adj_of_ne {u v : V} (e : Sym2 V) (h : G.Adj u v) (hne : s(u, v) ≠ e) :
    (G.deleteEdges {e}).Adj u v := by
  rw [SimpleGraph.deleteEdges_adj]; exact ⟨h, by simpa using hne⟩

/-- Reachability inside `G[S]` survives the deletion of an edge with an end outside `S`. -/
theorem reachable_deleteEdges_of_reachable_induce (S : Finset V) (e : Sym2 V)
    (he : ∀ u ∈ S, ∀ v ∈ S, s(u, v) ≠ e) {a b : V} (ha : a ∈ S) (hb : b ∈ S)
    (h : (G.induce (↑S : Set V)).Reachable ⟨a, ha⟩ ⟨b, hb⟩) : (G.deleteEdges {e}).Reachable a b := by
  let f : G.induce (↑S : Set V) →g G.deleteEdges {e} :=
    ⟨Subtype.val, fun {x y} hxy => deleteEdges_adj_of_ne G e ((SimpleGraph.induce_adj).mp hxy)
      (he _ (Finset.mem_coe.mp x.2) _ (Finset.mem_coe.mp y.2))⟩
  exact h.map f

/-- Along a path sequence, `p (i+1), p (i+2), …` stay mutually reachable after deleting the
edge `p i p (i+1)`. -/
theorem pathSeq_reachable_deleteEdge (hp : IsPathSeq G p) (i : Fin m) (hi : i.val + 1 < m) :
    ∀ d (hd : i.val + 1 + d < m),
      (G.deleteEdges {s(p i, p ⟨i.val + 1, hi⟩)}).Reachable (p ⟨i.val + 1, hi⟩) (p ⟨i.val + 1 + d, hd⟩)
  | 0, _ => SimpleGraph.Reachable.refl _
  | d + 1, hd => by
    refine (pathSeq_reachable_deleteEdge hp i hi d (by omega)).trans (SimpleGraph.Adj.reachable ?_)
    apply deleteEdges_adj_of_ne
    · exact hp.2 _ _ (by simp only; omega)
    · intro h
      rw [Sym2.eq_iff] at h
      rcases h with ⟨h1, -⟩ | ⟨-, h2⟩
      · have := congrArg Fin.val (hp.1 h1); simp only at this; omega
      · have := congrArg Fin.val (hp.1 h2); simp only at this; omega

/-- In an acyclic graph, a path sequence is an induced path. -/
theorem pathSeq_induced_aux (hG : G.IsAcyclic) (hp : IsPathSeq G p) {i j : Fin m} (hij : i < j)
    (hadj : G.Adj (p i) (p j)) (hne : i.val + 1 ≠ j.val) : False := by
  have hi : i.val + 1 < m := by have := j.isLt; have := (Fin.lt_def).mp hij; omega
  have hbridge := (SimpleGraph.isAcyclic_iff_forall_adj_isBridge.mp hG)
    (hp.2 i ⟨i.val + 1, hi⟩ rfl)
  rw [SimpleGraph.isBridge_iff] at hbridge
  apply hbridge
  have h1 : (G.deleteEdges {s(p i, p ⟨i.val + 1, hi⟩)}).Adj (p i) (p j) := by
    apply deleteEdges_adj_of_ne G _ hadj
    intro h
    rw [Sym2.eq_iff] at h
    rcases h with ⟨-, h2⟩ | ⟨h1, -⟩
    · have := congrArg Fin.val (hp.1 h2); simp only at this; omega
    · have := congrArg Fin.val (hp.1 h1); simp only at this; omega
  have hj : j = ⟨i.val + 1 + (j.val - (i.val + 1)), by omega⟩ := by
    apply Fin.ext; simp only; have := (Fin.lt_def).mp hij; omega
  have h2 := pathSeq_reachable_deleteEdge G p hp i hi (j.val - (i.val + 1)) (by omega)
  rw [← hj] at h2
  exact h1.reachable.trans h2.symm

theorem pathSeq_induced (hG : G.IsAcyclic) (hp : IsPathSeq G p) (i j : Fin m)
    (hadj : G.Adj (p i) (p j)) : i.val + 1 = j.val ∨ j.val + 1 = i.val := by
  by_contra hcon
  have hne : i ≠ j := fun h => G.ne_of_adj hadj (by rw [h])
  rcases lt_or_gt_of_ne hne with hlt | hlt
  · exact pathSeq_induced_aux G p hG hp hlt hadj (fun h => hcon (Or.inl h))
  · exact pathSeq_induced_aux G p hG hp hlt hadj.symm (fun h => hcon (Or.inr h))

/-- No edge inside `pieceSet p j` is the path edge `p j p (j+1)`, nor is any edge inside
`pieceSet p l` for `l ≠ j`. -/
theorem pieceSet_edge_ne (hp : Function.Injective p) (j l : Fin m) (hj : j.val + 1 < m) (hlj : l ≠ j)
    : ∀ u ∈ pieceSet p l, ∀ v ∈ pieceSet p l, s(u, v) ≠ s(p j, p ⟨j.val + 1, hj⟩) := by
  intro u hu v hv h
  rw [Sym2.eq_iff] at h
  rcases h with ⟨rfl, -⟩ | ⟨-, rfl⟩
  · exact hlj (pathVertex_mem_pieceSet p hp hu).symm
  · exact hlj (pathVertex_mem_pieceSet p hp hv).symm

theorem pieceSet_edge_ne_self (hp : Function.Injective p) (j : Fin m) (hj : j.val + 1 < m) :
    ∀ u ∈ pieceSet p j, ∀ v ∈ pieceSet p j, s(u, v) ≠ s(p j, p ⟨j.val + 1, hj⟩) := by
  intro u hu v hv h
  rw [Sym2.eq_iff] at h
  rcases h with ⟨-, rfl⟩ | ⟨rfl, -⟩
  · have := congrArg Fin.val (pathVertex_mem_pieceSet p hp hv); simp only at this; omega
  · have := congrArg Fin.val (pathVertex_mem_pieceSet p hp hu); simp only at this; omega

/-- The pieces are pairwise disjoint (acyclicity). -/
theorem piece_disjoint_aux (hG : G.IsAcyclic) (hp : IsPathSeq G p) {j l : Fin m} (hjl : j < l)
    {w : V} (hwj : w ∈ piece G p j) (hwl : w ∈ piece G p l) : False := by
  have hj : j.val + 1 < m := by have := l.isLt; have := (Fin.lt_def).mp hjl; omega
  have hbridge := (SimpleGraph.isAcyclic_iff_forall_adj_isBridge.mp hG)
    (hp.2 j ⟨j.val + 1, hj⟩ rfl)
  rw [SimpleGraph.isBridge_iff] at hbridge
  apply hbridge
  obtain ⟨hwj0, hwj⟩ := (mem_piece_iff G p j w).mp hwj
  obtain ⟨hwSj, hpj, hwSj', hreachj⟩ := (mem_reachSet_iff G _ _ w).mp hwj
  obtain ⟨hwl0, hwl⟩ := (mem_piece_iff G p l w).mp hwl
  obtain ⟨hwSl, hpl, hwSl', hreachl⟩ := (mem_reachSet_iff G _ _ w).mp hwl
  have R1 := reachable_deleteEdges_of_reachable_induce G _ _ (pieceSet_edge_ne_self p hp.1 j hj)
    _ _ hreachj
  have R2 := reachable_deleteEdges_of_reachable_induce G _ _
    (pieceSet_edge_ne p hp.1 j l hj (ne_of_gt hjl)) _ _ hreachl
  have hl : l = ⟨j.val + 1 + (l.val - (j.val + 1)), by omega⟩ := by
    apply Fin.ext; simp only; have := (Fin.lt_def).mp hjl; omega
  have R3 := pathSeq_reachable_deleteEdge G p hp j hj (l.val - (j.val + 1)) (by omega)
  rw [← hl] at R3
  exact (R1.trans R2.symm).trans R3.symm

theorem piece_disjoint (hG : G.IsAcyclic) (hp : IsPathSeq G p) {j l : Fin m} (hjl : j ≠ l) :
    Disjoint (piece G p j) (piece G p l) := by
  rw [Finset.disjoint_left]
  intro w hwj hwl
  rcases lt_or_gt_of_ne hjl with h | h
  · exact piece_disjoint_aux G p hG hp h hwj hwl
  · exact piece_disjoint_aux G p hG hp h hwl hwj

/-- Every edge leaving a piece goes to its path vertex. -/
theorem piece_attach (hG : G.IsAcyclic) (hp : IsPathSeq G p) (j : Fin m) {w u : V}
    (hw : w ∈ piece G p j) (hadj : G.Adj w u) : u ∈ piece G p j ∨ u = p j := by
  by_cases hu : u ∈ pathSet p
  · obtain ⟨l, rfl⟩ := (mem_pathSet_iff p u).mp hu
    by_cases hlj : l = j
    · exact Or.inr (by rw [hlj])
    · exfalso
      have hwl : w ∈ piece G p l :=
        mem_piece_of_adj G p (Finset.mem_compl.mp (piece_subset_compl G p j hw)) hadj.symm
      exact Finset.disjoint_left.mp (piece_disjoint G p hG hp hlj) hwl hw
  · exact Or.inl (mem_piece_of_adj_piece G p hw hu hadj)

/-- Every vertex off a nonempty path of a connected graph lies in some piece. -/
theorem piece_cover (hG : G.Connected) (hm : 0 < m) {v : V} (hv : v ∉ pathSet p) :
    ∃ j, v ∈ piece G p j := by
  have key : ∀ (a b : V) (_ : G.Walk a b), a ∉ pathSet p → b ∈ pathSet p → ∃ j, a ∈ piece G p j := by
    intro a b W
    induction W with
    | nil => intro ha hb; exact absurd hb ha
    | @cons a a' b h W' ih =>
      intro ha hb
      by_cases ha' : a' ∈ pathSet p
      · obtain ⟨j, rfl⟩ := (mem_pathSet_iff p a').mp ha'
        exact ⟨j, mem_piece_of_adj G p ha h.symm⟩
      · obtain ⟨j, hj⟩ := ih ha' hb
        exact ⟨j, mem_piece_of_adj_piece G p hj ha h.symm⟩
  obtain ⟨W⟩ := hG.preconnected v (p ⟨0, hm⟩)
  exact key v _ W hv (pathVertex_mem_pathSet p _)

end Pieces

/-- **The attachment lemma for trees**: the vertices off a nonempty path `p` of a tree `T`
split into the pieces `piece T p j`, each attached to the single path vertex `p j`, and the
path is induced. -/
theorem tree_exists_pathAttachment (T : SimpleGraph V) (hT : T.IsTree) {m : ℕ} (hm : 0 < m)
    (p : Fin m → V) (hp : IsPathSeq T p) :
    ∃ H : Fin m → Finset V, PathAttachment T p H ∧ (∀ j, H j ⊆ (Finset.univ.image p)ᶜ) ∧
      ∀ v, v ∉ Set.range p → ∃ j, v ∈ H j := by
  refine ⟨piece T p, ⟨fun j i => pathVertex_not_mem_piece T p j i,
    fun j l hjl => piece_disjoint T p hT.isAcyclic hp hjl,
    fun j w hw u hwu => piece_attach T p hT.isAcyclic hp j hw hwu,
    fun i j hij => pathSeq_induced T p hT.isAcyclic hp i j hij⟩,
    fun j => piece_subset_compl T p j, fun v hv => ?_⟩
  apply piece_cover T p hT.connected hm
  rw [mem_pathSet_iff]
  rintro ⟨i, rfl⟩
  exact hv (Set.mem_range_self i)

/-- **The path lemma**: for a path `P` of a tree `T`, `pathwidth T ≤ pathwidth (T − P) + 1`.
From the attachment partition and the general form: each piece is an induced subgraph of
`T − P`, so has no larger pathwidth. -/
theorem tree_pathwidth_le_pathwidth_compl_path_add_one (T : SimpleGraph V) (hT : T.IsTree)
    {m : ℕ} (p : Fin m → V) (hp : IsPathSeq T p) :
    pathwidth T ≤ pathwidth (T.induce (↑(Finset.univ.image p)ᶜ : Set V)) + 1 := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · have h : (Finset.univ.image p)ᶜ = Finset.univ := by
      rw [Finset.univ_eq_empty, Finset.image_empty, Finset.compl_empty]
    rw [h, Finset.coe_univ, ← pathwidth_eq_of_iso (SimpleGraph.induceUnivIso T)]
    exact Nat.le_succ _
  obtain ⟨H, hH, hsub, hcover⟩ := tree_exists_pathAttachment T hT hm p hp
  refine pathwidth_le_of_pathAttachment T p H hp hH hcover _ (fun j => ?_)
  have hle : (↑(H j) : Set V) ≤ ↑(Finset.univ.image p)ᶜ := Finset.coe_subset.mpr (hsub j)
  exact pathwidth_le_of_injective (SimpleGraph.induceHomOfLE T hle) (Set.inclusion_injective hle)

/-! ### Branches at a vertex, and a centroid -/

section Branches

/-- `reachSet` is closed under edges inside `S`. -/
theorem mem_reachSet_of_adj {S : Finset V} {v x y : V} (hx : x ∈ reachSet G S v) (hy : y ∈ S)
    (hxy : G.Adj x y) : y ∈ reachSet G S v := by
  obtain ⟨hxS, hv, hxS', hreach⟩ := (mem_reachSet_iff G S v x).mp hx
  refine (mem_reachSet_iff G S v y).mpr ⟨hy, hv, hy, hreach.trans ?_⟩
  exact SimpleGraph.Adj.reachable ((SimpleGraph.induce_adj (u := ⟨x, hxS'⟩) (v := ⟨y, hy⟩)).mpr hxy)

/-- `reachSet` is closed under reachability inside a subset `C ⊆ S`. -/
theorem mem_reachSet_of_reachable_induce {S C : Finset V} (hCS : C ⊆ S) {v x y : V}
    (hx : x ∈ reachSet G S v) (hxC : x ∈ C) (hyC : y ∈ C)
    (hreach : (G.induce (↑C : Set V)).Reachable ⟨x, hxC⟩ ⟨y, hyC⟩) : y ∈ reachSet G S v := by
  obtain ⟨hxS, hv, hxS', hr⟩ := (mem_reachSet_iff G S v x).mp hx
  have hle : (↑C : Set V) ≤ ↑S := Finset.coe_subset.mpr hCS
  have h2 := hreach.map (SimpleGraph.induceHomOfLE G hle).toHom
  exact (mem_reachSet_iff G S v y).mpr ⟨hCS hyC, hv, hCS hyC, hr.trans h2⟩

/-- The branch of `G` at `v` through `u`: the vertices reachable from `u` in `G − v`. -/
noncomputable def branch (v u : V) : Finset V := reachSet G (Finset.univ.erase v) u

theorem branch_subset_erase (v u : V) : branch G v u ⊆ Finset.univ.erase v := reachSet_subset G _ _

theorem not_mem_branch_self (v u : V) : v ∉ branch G v u := fun h =>
  (Finset.mem_erase.mp (branch_subset_erase G v u h)).1 rfl

theorem ne_of_mem_branch {v u x : V} (h : x ∈ branch G v u) : x ≠ v :=
  (Finset.mem_erase.mp (branch_subset_erase G v u h)).1

theorem mem_branch_self {v u : V} (h : u ≠ v) : u ∈ branch G v u :=
  self_mem_reachSet G _ (Finset.mem_erase.mpr ⟨h, Finset.mem_univ _⟩)

theorem mem_branch_of_adj {v u x y : V} (hx : x ∈ branch G v u) (hy : y ≠ v) (hxy : G.Adj x y) :
    y ∈ branch G v u :=
  mem_reachSet_of_adj G hx (Finset.mem_erase.mpr ⟨hy, Finset.mem_univ _⟩) hxy

theorem branch_connected {v u : V} (h : u ≠ v) : (G.induce (↑(branch G v u) : Set V)).Connected :=
  reachSet_connected G _ (Finset.mem_erase.mpr ⟨h, Finset.mem_univ _⟩)

theorem branch_eq_empty (v : V) : branch G v v = ∅ := by
  ext x
  simp only [branch, mem_reachSet_iff, Finset.mem_erase, Finset.mem_univ, and_true,
    Finset.notMem_empty, iff_false, not_and, not_exists]
  intro _ h; exact absurd rfl h

/-- A vertex `x ≠ v` lies in the branch at `v` through some neighbour of `v`. -/
theorem exists_mem_branch (hG : G.Connected) {v x : V} (hx : x ≠ v) :
    ∃ u, G.Adj v u ∧ x ∈ branch G v u := by
  have key : ∀ (a b : V) (_ : G.Walk a b), a ≠ b → ∃ u, G.Adj b u ∧ a ∈ branch G b u := by
    intro a b W
    induction W with
    | nil => intro h; exact absurd rfl h
    | @cons a a' b h W' ih =>
      intro ha
      by_cases ha' : a' = b
      · subst ha'; exact ⟨a, h.symm, mem_branch_self G ha⟩
      · obtain ⟨u, hu, ha'u⟩ := ih ha'
        exact ⟨u, hu, mem_branch_of_adj G ha'u ha h.symm⟩
  obtain ⟨W⟩ := hG.preconnected x v
  exact key x v W hx

/-- A nonempty connected set avoiding `v` lies inside one branch at `v`. -/
theorem exists_branch_of_connected (hG : G.Connected) {v : V} {C : Finset V} (hvC : v ∉ C)
    (hc : (G.induce (↑C : Set V)).Connected) (hne : C.Nonempty) :
    ∃ u, G.Adj v u ∧ C ⊆ branch G v u := by
  obtain ⟨x, hx⟩ := hne
  obtain ⟨u, hu, hxu⟩ := exists_mem_branch G hG (v := v) (x := x) (fun h => hvC (h ▸ hx))
  refine ⟨u, hu, fun y hy => ?_⟩
  have hCS : C ⊆ Finset.univ.erase v := fun z hz =>
    Finset.mem_erase.mpr ⟨fun h => hvC (h ▸ hz), Finset.mem_univ _⟩
  exact mem_reachSet_of_reachable_induce G hCS hxu hx hy (hc.preconnected _ _)

/-- No edge inside `V ∖ {v}` is an edge at `v`. -/
theorem erase_edge_ne (v w : V) :
    ∀ a ∈ Finset.univ.erase v, ∀ b ∈ Finset.univ.erase v, s(a, b) ≠ s(v, w) := by
  intro a ha b hb h
  rw [Sym2.eq_iff] at h
  rcases h with ⟨rfl, -⟩ | ⟨-, rfl⟩
  · exact (Finset.mem_erase.mp ha).1 rfl
  · exact (Finset.mem_erase.mp hb).1 rfl

/-- In an acyclic graph, the branches at `v` through two different neighbours are disjoint. -/
theorem branch_disjoint_of_ne (hG : G.IsAcyclic) {v w₁ w₂ : V} (h₁ : G.Adj v w₁) (h₂ : G.Adj v w₂)
    (hne : w₁ ≠ w₂) : Disjoint (branch G v w₁) (branch G v w₂) := by
  rw [Finset.disjoint_left]
  intro x hx₁ hx₂
  have hbridge := (SimpleGraph.isAcyclic_iff_forall_adj_isBridge.mp hG) h₁
  rw [SimpleGraph.isBridge_iff] at hbridge
  apply hbridge
  obtain ⟨hxS, hw₁, hxS', hr₁⟩ := (mem_reachSet_iff G _ _ x).mp hx₁
  obtain ⟨-, hw₂, hxS'', hr₂⟩ := (mem_reachSet_iff G _ _ x).mp hx₂
  have R1 := reachable_deleteEdges_of_reachable_induce G _ _ (erase_edge_ne v w₁) _ _ hr₁
  have R2 := reachable_deleteEdges_of_reachable_induce G _ _ (erase_edge_ne v w₁) _ _ hr₂
  have hA : (G.deleteEdges {s(v, w₁)}).Adj v w₂ := by
    apply deleteEdges_adj_of_ne G _ h₂
    intro h
    rw [Sym2.eq_iff] at h
    rcases h with ⟨-, h⟩ | ⟨h, -⟩
    · exact hne h.symm
    · exact G.ne_of_adj h₁ h
  exact (hA.reachable.trans R2).trans R1.symm

/-- In an acyclic graph, the two branches of an edge are disjoint. -/
theorem branch_disjoint_swap (hG : G.IsAcyclic) {v u : V} (hvu : G.Adj v u) :
    Disjoint (branch G v u) (branch G u v) := by
  rw [Finset.disjoint_left]
  intro x hx₁ hx₂
  have hbridge := (SimpleGraph.isAcyclic_iff_forall_adj_isBridge.mp hG) hvu
  rw [SimpleGraph.isBridge_iff] at hbridge
  apply hbridge
  obtain ⟨hxS, hu, hxS', hr₁⟩ := (mem_reachSet_iff G _ _ x).mp hx₁
  obtain ⟨-, hv, hxS'', hr₂⟩ := (mem_reachSet_iff G _ _ x).mp hx₂
  have R1 := reachable_deleteEdges_of_reachable_induce G _ _ (erase_edge_ne v u) _ _ hr₁
  have R2 := reachable_deleteEdges_of_reachable_induce G (Finset.univ.erase u) s(v, u)
    (fun a ha b hb h => erase_edge_ne u v a ha b hb (h.trans Sym2.eq_swap)) _ _ hr₂
  exact R2.trans R1.symm

/-- In a connected graph, the two branches of an edge cover every vertex. -/
theorem mem_branch_or (hG : G.Connected) {v u : V} (hvu : G.Adj v u) (x : V) :
    x ∈ branch G v u ∨ x ∈ branch G u v := by
  have key : ∀ (a b : V) (_ : G.Walk a b), a ∈ branch G v u ∨ a ∈ branch G u v →
      b ∈ branch G v u ∨ b ∈ branch G u v := by
    intro a b W
    induction W with
    | nil => exact id
    | @cons a a' b h W' ih =>
      intro ha
      apply ih
      rcases ha with ha | ha
      · by_cases ha' : a' = v
        · subst ha'; exact Or.inr (mem_branch_self G (G.ne_of_adj hvu))
        · exact Or.inl (mem_branch_of_adj G ha ha' h)
      · by_cases ha' : a' = u
        · subst ha'; exact Or.inl (mem_branch_self G (G.ne_of_adj hvu).symm)
        · exact Or.inr (mem_branch_of_adj G ha ha' h)
  obtain ⟨W⟩ := hG.preconnected u x
  exact key u x W (Or.inl (mem_branch_self G (G.ne_of_adj hvu).symm))

end Branches


/-- In a tree, the two branches of an edge partition the vertices. -/
theorem card_branch_add_card_branch (hT : G.IsTree) {v u : V} (hvu : G.Adj v u) :
    (branch G v u).card + (branch G u v).card = Fintype.card V := by
  rw [← Finset.card_union_of_disjoint (branch_disjoint_swap G hT.isAcyclic hvu),
    Finset.eq_univ_iff_forall.mpr (fun x => Finset.mem_union.mpr (mem_branch_or G hT.connected hvu x)),
    Finset.card_univ]

/-- A branch at `u` through `w ≠ v` sits inside the branch at `v` through `u` (acyclic). -/
theorem branch_subset_branch (hG : G.IsAcyclic) {v u w : V} (hvu : G.Adj v u) (huw : G.Adj u w)
    (hwv : w ≠ v) : branch G u w ⊆ branch G v u := by
  have hv : v ∉ branch G u w := fun h =>
    Finset.disjoint_left.mp (branch_disjoint_of_ne G hG huw hvu.symm hwv) h
      (mem_branch_self G (G.ne_of_adj hvu))
  have hsub : branch G u w ⊆ Finset.univ.erase v := fun x hx =>
    Finset.mem_erase.mpr ⟨fun h => hv (h ▸ hx), Finset.mem_univ _⟩
  intro x hx
  have hw : w ∈ branch G v u := mem_branch_of_adj G (mem_branch_self G (G.ne_of_adj hvu).symm) hwv huw
  exact mem_reachSet_of_reachable_induce G hsub hw (mem_branch_self G (G.ne_of_adj huw).symm) hx
    ((branch_connected G (G.ne_of_adj huw).symm).preconnected _ _)

theorem card_branch_lt (hG : G.IsAcyclic) {v u w : V} (hvu : G.Adj v u) (huw : G.Adj u w)
    (hwv : w ≠ v) : (branch G u w).card < (branch G v u).card := by
  apply Finset.card_lt_card
  refine Finset.ssubset_iff_subset_ne.mpr ⟨branch_subset_branch G hG hvu huw hwv, fun h => ?_⟩
  have : u ∈ branch G u w := by rw [h]; exact mem_branch_self G (G.ne_of_adj hvu).symm
  exact not_mem_branch_self G u w this

/-- The largest branch at `v`. -/
noncomputable def maxBranch (v : V) : ℕ := Finset.univ.sup (fun u => (branch G v u).card)

theorem card_branch_le_maxBranch (v u : V) : (branch G v u).card ≤ maxBranch G v :=
  Finset.le_sup (f := fun u => (branch G v u).card) (Finset.mem_univ u)

/-- **A centroid**: a vertex all of whose branches have at most half the vertices. Take a
vertex minimising the largest branch; a branch with more than half the vertices contains a
neighbour whose branches are all smaller. -/
theorem exists_centroid (hT : G.IsTree) :
    ∃ c, ∀ u, G.Adj c u → 2 * (branch G c u).card ≤ Fintype.card V := by
  have := hT.connected.nonempty
  obtain ⟨c, -, hc⟩ := Finset.exists_min_image Finset.univ (maxBranch G) Finset.univ_nonempty
  refine ⟨c, fun u hcu => ?_⟩
  by_contra hbig
  have hbig' : Fintype.card V < 2 * (branch G c u).card := not_le.mp hbig
  have hpos : 0 < (branch G c u).card := Finset.card_pos.mpr ⟨u, mem_branch_self G (G.ne_of_adj hcu).symm⟩
  have hlt : maxBranch G u < maxBranch G c := by
    apply lt_of_lt_of_le _ (card_branch_le_maxBranch G c u)
    unfold maxBranch
    rw [Finset.sup_lt_iff hpos]
    intro x _
    by_cases hxu : x = u
    · subst hxu; rw [branch_eq_empty]; simpa using hpos
    · obtain ⟨w, huw, hsub⟩ := exists_branch_of_connected G hT.connected (not_mem_branch_self G u x)
        (branch_connected G hxu) ⟨x, mem_branch_self G hxu⟩
      refine (Finset.card_le_card hsub).trans_lt ?_
      by_cases hwc : w = c
      · subst hwc
        have := card_branch_add_card_branch G hT hcu
        omega
      · exact card_branch_lt G hT.isAcyclic hcu huw hwc
  exact absurd (hc u (Finset.mem_univ u)) (not_le.mpr hlt)

/-- **The heavy walk**: inside a branch `B(v, u)` with fewer than `2m` vertices there is a path
starting at `u` such that every connected set of the branch avoiding the path has fewer than
`m` vertices. At `u`, at most one sub-branch has `≥ m` vertices (two would need `2m + 1`);
walk into it and induct on the size. -/
theorem exists_heavy_path (hT : G.IsTree) (m : ℕ) :
    ∀ n (v u : V), G.Adj v u → (branch G v u).card = n → n < 2 * m →
      ∃ l : List V, l.head? = some u ∧ l.Nodup ∧ l.IsChain G.Adj ∧ (∀ x ∈ l, x ∈ branch G v u) ∧
        ∀ C : Finset V, C ⊆ branch G v u → (∀ x ∈ l, x ∉ C) →
          (G.induce (↑C : Set V)).Connected → C.card < m := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
  intro v u hvu hn hlt
  have hm : 0 < m := by omega
  have huv : u ≠ v := (G.ne_of_adj hvu).symm
  have hu : u ∈ branch G v u := mem_branch_self G huv
  have hsub : ∀ w, G.Adj u w → w ≠ v → branch G u w ⊆ branch G v u :=
    fun w huw hwv => branch_subset_branch G hT.isAcyclic hvu huw hwv
  have hcard : ∀ w, G.Adj u w → w ≠ v → (branch G u w).card < n :=
    fun w huw hwv => hn ▸ card_branch_lt G hT.isAcyclic hvu huw hwv
  have huniq : ∀ w₁ w₂, G.Adj u w₁ → w₁ ≠ v → m ≤ (branch G u w₁).card →
      G.Adj u w₂ → w₂ ≠ v → m ≤ (branch G u w₂).card → w₁ = w₂ := by
    intro w₁ w₂ h₁ h₁v hm₁ h₂ h₂v hm₂
    by_contra hne
    have hdisj := branch_disjoint_of_ne G hT.isAcyclic h₁ h₂ hne
    have hsub' : branch G u w₁ ∪ branch G u w₂ ⊆ (branch G v u).erase u := by
      intro x hx
      rcases Finset.mem_union.mp hx with hx | hx
      · exact Finset.mem_erase.mpr ⟨ne_of_mem_branch G hx, hsub w₁ h₁ h₁v hx⟩
      · exact Finset.mem_erase.mpr ⟨ne_of_mem_branch G hx, hsub w₂ h₂ h₂v hx⟩
    have := Finset.card_le_card hsub'
    rw [Finset.card_union_of_disjoint hdisj, Finset.card_erase_of_mem hu, hn] at this
    omega
  have hpiece : ∀ C : Finset V, C ⊆ branch G v u → u ∉ C → (G.induce (↑C : Set V)).Connected →
      C.Nonempty → ∃ w, G.Adj u w ∧ w ≠ v ∧ C ⊆ branch G u w := by
    intro C hC huC hc hne
    obtain ⟨w, huw, hCw⟩ := exists_branch_of_connected G hT.connected huC hc hne
    refine ⟨w, huw, fun hwv => ?_, hCw⟩
    subst hwv
    obtain ⟨x, hx⟩ := hne
    exact Finset.disjoint_left.mp (branch_disjoint_swap G hT.isAcyclic hvu) (hC hx) (hCw hx)
  by_cases hheavy : ∃ w, G.Adj u w ∧ w ≠ v ∧ m ≤ (branch G u w).card
  · obtain ⟨w, huw, hwv, hmw⟩ := hheavy
    obtain ⟨l', hl'h, hl'nd, hl'ch, hl'mem, hl'C⟩ :=
      ih _ (hcard w huw hwv) u w huw rfl ((hcard w huw hwv).trans hlt)
    refine ⟨u :: l', rfl, ?_, ?_, ?_, ?_⟩
    · rw [List.nodup_cons]; exact ⟨fun h => not_mem_branch_self G u w (hl'mem u h), hl'nd⟩
    · rw [List.isChain_cons]
      refine ⟨fun y hy => ?_, hl'ch⟩
      rw [Option.mem_def, hl'h] at hy
      rw [← Option.some.inj hy]; exact huw
    · intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · exact hu
      · exact hsub w huw hwv (hl'mem x hx)
    · intro C hC hlC hc
      rcases C.eq_empty_or_nonempty with rfl | hne
      · simpa using hm
      obtain ⟨w', huw', hw'v, hCw'⟩ := hpiece C hC (hlC u (List.mem_cons.mpr (Or.inl rfl))) hc hne
      by_cases hww : w' = w
      · subst hww; exact hl'C C hCw' (fun x hx => hlC x (List.mem_cons.mpr (Or.inr hx))) hc
      · have : (branch G u w').card < m := by
          by_contra h; exact hww (huniq w' w huw' hw'v (not_lt.mp h) huw hwv hmw)
        exact (Finset.card_le_card hCw').trans_lt this
  · refine ⟨[u], rfl, List.nodup_singleton u, List.isChain_singleton _, ?_, ?_⟩
    · intro x hx; rw [List.mem_singleton] at hx; subst hx; exact hu
    · intro C hC hlC hc
      rcases C.eq_empty_or_nonempty with rfl | hne
      · simpa using hm
      obtain ⟨w', huw', hw'v, hCw'⟩ := hpiece C hC (hlC u (List.mem_singleton_self u)) hc hne
      have : (branch G u w').card < m := by
        by_contra h; exact hheavy ⟨w', huw', hw'v, not_lt.mp h⟩
      exact (Finset.card_le_card hCw').trans_lt this

/-! ### Trees: the size bound -/

/-- **The splitting lemma** (stated, not proved — see the header): a tree on at most `3m`
vertices has a path whose removal leaves every connected piece with fewer than `m` vertices.
Checked by brute force on every tree to 17 vertices at the binding `m = ⌈N/3⌉`
(2026-10-30, zero violations, tight at every `N`). Proof sketch: a centroid `c` has all
components of `T − c` of size `≤ N/2 ≤ 3m/2`; at most two of them have `≥ m` vertices
(three would give `3m + 1 > N`); in each such component, rooted at its attachment, walk
to the unique child subtree with `≥ m` vertices (two would give `2m + 1 > 3m/2`) until
none has; the two walks through `c` form `P`. -/
theorem tree_exists_path_split (T : SimpleGraph V) (hT : T.IsTree) (m : ℕ) (hm : 1 ≤ m)
    (hN : Fintype.card V ≤ 3 * m) :
    ∃ (l : ℕ) (p : Fin l → V), IsPathSeq T p ∧
      ∀ C : Finset V, (∀ i, p i ∉ C) → (T.induce (↑C : Set V)).Connected → C.card < m := by
  obtain ⟨c, hc⟩ := exists_centroid T hT
  have hlt2 : ∀ u, T.Adj c u → (branch T c u).card < 2 * m := fun u hu => by
    have := hc u hu; omega
  have hthree : ∀ u₁ u₂ u₃, T.Adj c u₁ → T.Adj c u₂ → T.Adj c u₃ → u₁ ≠ u₂ → u₁ ≠ u₃ → u₂ ≠ u₃ →
      m ≤ (branch T c u₁).card → m ≤ (branch T c u₂).card → m ≤ (branch T c u₃).card → False := by
    intro u₁ u₂ u₃ h₁ h₂ h₃ h₁₂ h₁₃ h₂₃ hm₁ hm₂ hm₃
    have hd₁₂ := branch_disjoint_of_ne T hT.isAcyclic h₁ h₂ h₁₂
    have hd₁₃ := branch_disjoint_of_ne T hT.isAcyclic h₁ h₃ h₁₃
    have hd₂₃ := branch_disjoint_of_ne T hT.isAcyclic h₂ h₃ h₂₃
    have hsub : branch T c u₁ ∪ branch T c u₂ ∪ branch T c u₃ ⊆ Finset.univ.erase c :=
      Finset.union_subset (Finset.union_subset (branch_subset_erase T c u₁) (branch_subset_erase T c u₂))
        (branch_subset_erase T c u₃)
    have := Finset.card_le_card hsub
    rw [Finset.card_union_of_disjoint (Finset.disjoint_union_left.mpr ⟨hd₁₃, hd₂₃⟩),
      Finset.card_union_of_disjoint hd₁₂, Finset.card_erase_of_mem (Finset.mem_univ c),
      Finset.card_univ] at this
    omega
  suffices h : ∃ l : List V, l.Nodup ∧ l.IsChain T.Adj ∧
      ∀ C : Finset V, (∀ x ∈ l, x ∉ C) → (T.induce (↑C : Set V)).Connected → C.card < m by
    obtain ⟨l, hnd, hch, hC⟩ := h
    refine ⟨l.length, fun i => l.get i, ⟨List.nodup_iff_injective_get.mp hnd, ?_⟩, ?_⟩
    · intro i j hij
      have := List.isChain_iff_getElem.mp hch i.val (by omega)
      have hj : j = ⟨i.val + 1, by omega⟩ := Fin.ext hij.symm
      show T.Adj (l.get i) (l.get j)
      rw [hj]
      simpa only [List.get_eq_getElem] using this
    · intro C hC' hc
      exact hC C (fun x hx => by obtain ⟨n, rfl⟩ := List.mem_iff_get.mp hx; exact hC' n) hc
  have hpiece : ∀ C : Finset V, c ∉ C → (T.induce (↑C : Set V)).Connected → C.Nonempty →
      ∃ u, T.Adj c u ∧ C ⊆ branch T c u := fun C => exists_branch_of_connected T hT.connected
  by_cases h1 : ∃ u₁, T.Adj c u₁ ∧ m ≤ (branch T c u₁).card
  · obtain ⟨u₁, hcu₁, hm₁⟩ := h1
    obtain ⟨l₁, hl₁h, hl₁nd, hl₁ch, hl₁mem, hl₁C⟩ :=
      exists_heavy_path T hT m _ c u₁ hcu₁ rfl (hlt2 u₁ hcu₁)
    have hcl₁ : c ∉ l₁ := fun h => not_mem_branch_self T c u₁ (hl₁mem c h)
    by_cases h2 : ∃ u₂, T.Adj c u₂ ∧ u₂ ≠ u₁ ∧ m ≤ (branch T c u₂).card
    · obtain ⟨u₂, hcu₂, hne, hm₂⟩ := h2
      obtain ⟨l₂, hl₂h, hl₂nd, hl₂ch, hl₂mem, hl₂C⟩ :=
        exists_heavy_path T hT m _ c u₂ hcu₂ rfl (hlt2 u₂ hcu₂)
      have hcl₂ : c ∉ l₂ := fun h => not_mem_branch_self T c u₂ (hl₂mem c h)
      have hdisj := branch_disjoint_of_ne T hT.isAcyclic hcu₁ hcu₂ hne.symm
      refine ⟨l₁.reverse ++ c :: l₂, ?_, ?_, ?_⟩
      · rw [List.nodup_append]
        refine ⟨List.nodup_reverse.mpr hl₁nd, List.nodup_cons.mpr ⟨hcl₂, hl₂nd⟩, ?_⟩
        intro a ha b hb hab
        rw [List.mem_reverse] at ha
        subst hab
        rcases List.mem_cons.mp hb with rfl | hb
        · exact hcl₁ ha
        · exact Finset.disjoint_left.mp hdisj (hl₁mem a ha) (hl₂mem a hb)
      · rw [List.isChain_append]
        refine ⟨List.isChain_reverse.mpr (hl₁ch.imp fun a b h => h.symm), ?_, ?_⟩
        · rw [List.isChain_cons]
          refine ⟨fun y hy => ?_, hl₂ch⟩
          rw [Option.mem_def, hl₂h] at hy
          rw [← Option.some.inj hy]; exact hcu₂
        · intro x hx y hy
          rw [List.getLast?_reverse, Option.mem_def, hl₁h] at hx
          rw [Option.mem_def, List.head?_cons] at hy
          rw [← Option.some.inj hx, ← Option.some.inj hy]
          exact hcu₁.symm
      · intro C hC hc
        rcases C.eq_empty_or_nonempty with rfl | hne'
        · rw [Finset.card_empty]; omega
        obtain ⟨u, hcu, hCu⟩ := hpiece C (hC c (List.mem_append.mpr (Or.inr (List.mem_cons.mpr (Or.inl rfl))))) hc hne'
        by_cases hu1 : u = u₁
        · subst hu1
          exact hl₁C C hCu (fun x hx => hC x (List.mem_append.mpr (Or.inl (List.mem_reverse.mpr hx)))) hc
        by_cases hu2 : u = u₂
        · subst hu2
          exact hl₂C C hCu (fun x hx => hC x (List.mem_append.mpr (Or.inr (List.mem_cons.mpr (Or.inr hx))))) hc
        have : (branch T c u).card < m := by
          by_contra h
          exact hthree u₁ u₂ u hcu₁ hcu₂ hcu hne.symm (Ne.symm hu1) (Ne.symm hu2) hm₁ hm₂ (not_lt.mp h)
        exact (Finset.card_le_card hCu).trans_lt this
    · refine ⟨c :: l₁, List.nodup_cons.mpr ⟨hcl₁, hl₁nd⟩, ?_, ?_⟩
      · rw [List.isChain_cons]
        refine ⟨fun y hy => ?_, hl₁ch⟩
        rw [Option.mem_def, hl₁h] at hy
        rw [← Option.some.inj hy]; exact hcu₁
      · intro C hC hc
        rcases C.eq_empty_or_nonempty with rfl | hne'
        · rw [Finset.card_empty]; omega
        obtain ⟨u, hcu, hCu⟩ := hpiece C (hC c (List.mem_cons.mpr (Or.inl rfl))) hc hne'
        by_cases hu1 : u = u₁
        · subst hu1
          exact hl₁C C hCu (fun x hx => hC x (List.mem_cons.mpr (Or.inr hx))) hc
        have : (branch T c u).card < m := by
          by_contra h; exact h2 ⟨u, hcu, hu1, not_lt.mp h⟩
        exact (Finset.card_le_card hCu).trans_lt this
  · refine ⟨[c], List.nodup_singleton c, List.isChain_singleton _, ?_⟩
    intro C hC hc
    rcases C.eq_empty_or_nonempty with rfl | hne'
    · rw [Finset.card_empty]; omega
    obtain ⟨u, hcu, hCu⟩ := hpiece C (hC c (List.mem_singleton_self c)) hc hne'
    have : (branch T c u).card < m := by
      by_contra h; exact h1 ⟨u, hcu, not_lt.mp h⟩
    exact (Finset.card_le_card hCu).trans_lt this

/-- `treeBound k` is the largest `N` such that every tree on `N` vertices has pathwidth
`≤ k`: `1, 6, 21, 66, 201, …`, i.e. `(5·3^k − 3)/2`. -/
def treeBound : ℕ → ℕ
  | 0 => 1
  | k + 1 => 3 * treeBound k + 3

theorem two_mul_treeBound_add_three : ∀ k, 2 * treeBound k + 3 = 5 * 3 ^ k
  | 0 => by simp [treeBound]
  | k + 1 => by
    have ih := two_mul_treeBound_add_three k
    simp only [treeBound, pow_succ]
    omega

/-- An induced subgraph of a tree on a connected vertex set is a tree. -/
theorem isTree_induce_of_connected {T : SimpleGraph V} (hT : T.IsTree) (C : Finset V)
    (hc : (T.induce (↑C : Set V)).Connected) : (T.induce (↑C : Set V)).IsTree :=
  ⟨hc, hT.isAcyclic.induce _⟩

/-- **The size bound for trees**: every tree on at most `treeBound k` vertices has pathwidth
at most `k`. By induction on `k` through the path lemma, the splitting lemma and
`pathwidth_induce_le_of_forall_connected`; the base case is the single vertex. -/
theorem tree_pathwidth_le_treeBound : ∀ (k : ℕ) {V : Type*} [Fintype V] [DecidableEq V]
    (T : SimpleGraph V), T.IsTree → Fintype.card V ≤ treeBound k → pathwidth T ≤ k
  | 0, V, _, _, T, _, hN => by
    have := pathwidth_le_card_sub_one T
    simp only [treeBound] at hN
    omega
  | k + 1, V, _, _, T, hT, hN => by
    have hm : 1 ≤ treeBound k + 1 := Nat.succ_pos _
    have hN' : Fintype.card V ≤ 3 * (treeBound k + 1) := by simp only [treeBound] at hN; omega
    obtain ⟨l, p, hp, hsplit⟩ := tree_exists_path_split T hT (treeBound k + 1) hm hN'
    refine (tree_pathwidth_le_pathwidth_compl_path_add_one T hT p hp).trans
      (Nat.add_le_add_right ?_ 1)
    apply pathwidth_induce_le_of_forall_connected
    intro C hC hc
    have hnot : ∀ i, p i ∉ C := fun i hi =>
      (Finset.mem_compl.mp (hC hi)) (Finset.mem_image_of_mem p (Finset.mem_univ i))
    have hcard : Fintype.card (↑(↑C : Set V) : Type _) ≤ treeBound k := by
      have := hsplit C hnot hc
      simp only [Finset.coe_sort_coe, Fintype.card_coe]
      omega
    exact tree_pathwidth_le_treeBound k _ (isTree_induce_of_connected hT C hc) hcard

/-- **Every tree on `N` vertices has pathwidth at most `⌊log₃(2N + 1)⌋`** — the deterministic
core of §2 of `reports/random_graph_pathwidth_survey.md`, a corollary of the size bound:
if `3^k ≤ 2N + 1 < 3^(k+1)` then `2N + 3 ≤ 3·3^k + 1 ≤ 5·3^k = 2·treeBound k + 3`. -/
theorem tree_pathwidth_le_log (T : SimpleGraph V) (hT : T.IsTree) :
    pathwidth T ≤ Nat.log 3 (2 * Fintype.card V + 1) := by
  set k := Nat.log 3 (2 * Fintype.card V + 1) with hk
  apply tree_pathwidth_le_treeBound k T hT
  have h1 : 2 * Fintype.card V + 1 < 3 ^ (k + 1) := Nat.lt_pow_succ_log_self (by norm_num) _
  have h2 := two_mul_treeBound_add_three k
  have h3 : 1 ≤ 3 ^ k := Nat.one_le_pow _ _ (by norm_num)
  rw [pow_succ] at h1
  omega

/-! ### The extremal trees: `treeBound` is sharp -/

/-- A graph with an edge has pathwidth at least `1`: a bag must hold both ends. -/
theorem one_le_pathwidth_of_adj' {u v : V} (h : G.Adj u v) : 1 ≤ pathwidth G := by
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq G
  obtain ⟨i, hu, hv⟩ := P.edge_coverage u v h
  have h2 : 2 ≤ (P.bag i).card := by
    have : ({u, v} : Finset V) ⊆ P.bag i := by
      intro x hx
      rcases Finset.mem_insert.mp hx with rfl | hx
      · exact hu
      · exact Finset.mem_singleton.mp hx ▸ hv
    have := Finset.card_le_card this
    rwa [Finset.card_pair (G.ne_of_adj h)] at this
  have := P.bag_card_le_width_add_one i
  omega

/-- The vertices of the `k`-th extremal tree: an edge, then three copies and a root. -/
def EVert : ℕ → Type
  | 0 => Fin 2
  | k + 1 => Option (Fin 3 × EVert k)

instance instFintypeEVert : (k : ℕ) → Fintype (EVert k)
  | 0 => inferInstanceAs (Fintype (Fin 2))
  | k + 1 => letI := instFintypeEVert k; inferInstanceAs (Fintype (Option (Fin 3 × EVert k)))

instance instDecidableEqEVert : (k : ℕ) → DecidableEq (EVert k)
  | 0 => inferInstanceAs (DecidableEq (Fin 2))
  | k + 1 => letI := instDecidableEqEVert k; inferInstanceAs (DecidableEq (Option (Fin 3 × EVert k)))

/-- The root of the `k`-th extremal tree. -/
def eroot : (k : ℕ) → EVert k
  | 0 => (0 : Fin 2)
  | _ + 1 => none

/-- **The extremal trees**: `extremalTree 0` is an edge; `extremalTree (k+1)` is three copies of
`extremalTree k` joined to a new root through their roots. It has `treeBound k + 1` vertices
and pathwidth `k + 1`, so the size bound `tree_pathwidth_le_treeBound` is sharp. -/
def extremalTree : (k : ℕ) → SimpleGraph (EVert k)
  | 0 => SimpleGraph.pathGraph 2
  | k + 1 => triple (extremalTree k) (eroot k)

theorem extremalTree_connected : ∀ k, (extremalTree k).Connected
  | 0 => SimpleGraph.pathGraph_connected 1
  | k + 1 => triple_connected _ _ (extremalTree_connected k)

theorem card_EVert : ∀ k, Fintype.card (EVert k) = treeBound k + 1
  | 0 => by
    have : Fintype.card (EVert 0) = 2 := Fintype.card_fin 2
    rw [this]; rfl
  | k + 1 => by
    have ih := card_EVert k
    have : Fintype.card (EVert (k + 1)) = 3 * Fintype.card (EVert k) + 1 := card_triple
    rw [this, ih]; simp only [treeBound]; ring

/-- **The extremal tree of index `k` has pathwidth `k + 1`.** -/
theorem pathwidth_extremalTree : ∀ k, pathwidth (extremalTree k) = k + 1
  | 0 => by
    apply le_antisymm
    · have := pathwidth_le_card_sub_one (extremalTree 0)
      have hc : Fintype.card (EVert 0) = 2 := Fintype.card_fin 2
      omega
    · exact one_le_pathwidth_of_adj' (extremalTree 0)
        (u := (0 : Fin 2)) (v := (1 : Fin 2)) ((SimpleGraph.pathGraph_adj).mpr (Or.inl rfl))
  | k + 1 => by
    show pathwidth (triple (extremalTree k) (eroot k)) = k + 1 + 1
    rw [pathwidth_triple _ _ (extremalTree_connected k), pathwidth_extremalTree k]

/-- **`treeBound` is sharp**: for every `k` there is a connected graph on `treeBound k + 1`
vertices with pathwidth `k + 1` (and it is a tree: `extremalTree_isTree` below). -/
theorem treeBound_sharp (k : ℕ) :
    Fintype.card (EVert k) = treeBound k + 1 ∧ pathwidth (extremalTree k) = k + 1 :=
  ⟨card_EVert k, pathwidth_extremalTree k⟩

/-! ### `triple` of a tree is a tree -/

/-- A set closed under adjacency separates: nothing inside reaches anything outside. -/
theorem not_reachable_of_closed (S : Set V) (hS : ∀ a ∈ S, ∀ b, G.Adj a b → b ∈ S) {u v : V}
    (hu : u ∈ S) (hv : v ∉ S) : ¬ G.Reachable u v := by
  rintro ⟨W⟩
  have key : ∀ (a b : V) (_ : G.Walk a b), a ∈ S → b ∈ S := by
    intro a b W'
    induction W' with
    | nil => exact id
    | @cons a a' b h W'' ih => intro ha; exact ih (hS a ha a' h)
  exact hv (key u v W hu)

section TripleTree

variable (r : V)

theorem triple_deleteEdges_adj (e : Sym2 (Option (Fin 3 × V))) (a b : Option (Fin 3 × V)) :
    ((triple G r).deleteEdges {e}).Adj a b ↔ (triple G r).Adj a b ∧ s(a, b) ≠ e := by
  rw [SimpleGraph.deleteEdges_adj, Set.mem_singleton_iff]

/-- The root–copy edge is a bridge: the copy is closed once it is removed. -/
theorem triple_not_reachable_root (i : Fin 3) :
    ¬ ((triple G r).deleteEdges {s(none, some (i, r))}).Reachable none (some (i, r)) := by
  intro h
  apply not_reachable_of_closed _ {c | ∃ z, c = some (i, z)} _ ⟨r, rfl⟩ _ h.symm
  · rintro a ⟨z, rfl⟩ b hab
    rw [triple_deleteEdges_adj] at hab
    rcases b with _ | ⟨j, z'⟩
    · exfalso
      obtain ⟨h1, h2⟩ := hab
      have hz : z = r := (triple_adj_some_none G r i z).mp h1
      subst hz
      exact h2 Sym2.eq_swap
    · obtain ⟨h1, -⟩ := hab
      obtain ⟨rfl, -⟩ := (triple_adj_some_some G r i j z z').mp h1
      exact ⟨z', rfl⟩
  · rintro ⟨z, h⟩; cases h

/-- A copy edge is a bridge: the part of the copy reachable from one end without the edge,
together with everything outside the copy when the copy's root is in it, is closed. -/
theorem triple_not_reachable_copy (hG : G.IsAcyclic) (i : Fin 3) {x y : V} (hxy : G.Adj x y) :
    ¬ ((triple G r).deleteEdges {s(some (i, x), some (i, y))}).Reachable (some (i, x)) (some (i, y)) := by
  have hbridge := (SimpleGraph.isAcyclic_iff_forall_adj_isBridge.mp hG) hxy
  rw [SimpleGraph.isBridge_iff] at hbridge
  set R : Set V := {z | (G.deleteEdges {s(x, y)}).Reachable x z} with hR
  have hxR : x ∈ R := SimpleGraph.Reachable.refl _
  have hyR : y ∉ R := hbridge
  apply not_reachable_of_closed _
    {c | (∃ z ∈ R, c = some (i, z)) ∨ (r ∈ R ∧ (c = none ∨ ∃ j z, j ≠ i ∧ c = some (j, z)))}
    _ (Or.inl ⟨x, hxR, rfl⟩)
  · rintro (⟨z, hz, h⟩ | ⟨hr, h | ⟨j, z, hji, h⟩⟩)
    · exact hyR ((Prod.mk.inj (Option.some.inj h)).2 ▸ hz)
    · cases h
    · exact hji (Prod.mk.inj (Option.some.inj h)).1.symm
  · rintro a (⟨z, hz, rfl⟩ | ⟨hr, rfl | ⟨j, z, hji, rfl⟩⟩) b hab <;>
      rw [triple_deleteEdges_adj] at hab <;> obtain ⟨h1, h2⟩ := hab
    · rcases b with _ | ⟨j, z'⟩
      · have hz' : z = r := (triple_adj_some_none G r i z).mp h1
        rw [hz'] at hz
        exact Or.inr ⟨hz, Or.inl rfl⟩
      · obtain ⟨rfl, hzz'⟩ := (triple_adj_some_some G r i j z z').mp h1
        refine Or.inl ⟨z', ?_, rfl⟩
        have hne : s(z, z') ≠ s(x, y) := by
          intro h
          apply h2
          rw [Sym2.eq_iff] at h ⊢
          rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
          · exact Or.inl ⟨rfl, rfl⟩
          · exact Or.inr ⟨rfl, rfl⟩
        exact hz.trans (SimpleGraph.Adj.reachable (deleteEdges_adj_of_ne G _ hzz' hne))
    · rcases b with _ | ⟨j, z'⟩
      · exact absurd h1 (triple_adj_none_none G r)
      · have hz' : z' = r := (triple_adj_none_some G r j z').mp h1
        rw [hz']
        by_cases hji : j = i
        · subst hji; exact Or.inl ⟨r, hr, rfl⟩
        · exact Or.inr ⟨hr, Or.inr ⟨j, r, hji, rfl⟩⟩
    · rcases b with _ | ⟨j', z'⟩
      · exact Or.inr ⟨hr, Or.inl rfl⟩
      · obtain ⟨rfl, -⟩ := (triple_adj_some_some G r j j' z z').mp h1
        exact Or.inr ⟨hr, Or.inr ⟨j, z', hji, rfl⟩⟩

theorem triple_isAcyclic (hG : G.IsAcyclic) : (triple G r).IsAcyclic := by
  rw [SimpleGraph.isAcyclic_iff_forall_adj_isBridge]
  intro a b hab
  rw [SimpleGraph.isBridge_iff]
  rcases a with _ | ⟨i, x⟩ <;> rcases b with _ | ⟨j, y⟩
  · exact absurd hab (triple_adj_none_none G r)
  · have hy : y = r := (triple_adj_none_some G r j y).mp hab
    rw [hy]
    exact triple_not_reachable_root G r j
  · have hx : x = r := (triple_adj_some_none G r i x).mp hab
    rw [hx]
    intro h
    apply triple_not_reachable_root G r i
    have : ({s(some (i, r), none)} : Set (Sym2 (Option (Fin 3 × V)))) = {s(none, some (i, r))} := by
      rw [Sym2.eq_swap]
    rw [this] at h
    exact h.symm
  · obtain ⟨rfl, hxy⟩ := (triple_adj_some_some G r i j x y).mp hab
    exact triple_not_reachable_copy G r hG i hxy

/-- **`triple` of a tree is a tree.** -/
theorem triple_isTree (hG : G.IsTree) : (triple G r).IsTree :=
  ⟨triple_connected G r hG.connected, triple_isAcyclic G r hG.isAcyclic⟩

end TripleTree

theorem ternaryTree_isTree : ∀ h, (ternaryTree h).IsTree
  | 0 => ⟨ternaryTree_connected 0, SimpleGraph.isAcyclic_bot⟩
  | h + 1 => triple_isTree _ _ (ternaryTree_isTree h)

theorem extremalTree_isTree : ∀ k, (extremalTree k).IsTree
  | 0 => pathGraph_isTree 1
  | k + 1 => triple_isTree _ _ (extremalTree_isTree k)

end MOSPFormalization
