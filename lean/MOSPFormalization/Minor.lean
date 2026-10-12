/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Pathwidth is minor-monotone

Contracting an edge never increases pathwidth, and neither does deleting a
vertex or an edge (Fellows & Langston 1987, Lemma 4.2, stated there for gate
matrix layout cost; Bodlaender, Wolle & Koster 2006 for treewidth). This is the
theorem behind the solvers' *minor* proofs: a refutation of `pathwidth H ≤ w`
on a contraction `H` of `G` proves `pathwidth G ≥ w + 1`
(`pathwidth_gt_of_minorOf`), and on the MOSP graph `mospValue > w + 1`
(`MOSPInstance.lt_mospValue_of_minorOf`).

## The contraction

`contractEdge G u v` merges `v` into `u`; `u` keeps its label, exactly as
`pathwidth_solver/pathwidth/minor.py` does (`_contract(adj, alive, v, u)`).
The vertex type does not change: `v` stays as an *isolated* vertex, and the
minor proper is the graph induced on the vertices never removed
(`minorOf`). Adjacency in `contractEdge G u v`: `x ≠ y`, neither is `v`, and
either `x y` is an edge of `G` or one of them is `u` and the other a neighbour
of `v`. So `N(u)` becomes `N(u) ∪ N(v) − {u, v}`, with no loop and no multi-edge.

## The proof

Replace `v` by `u` in every bag. No bag grows. The bags of `u` and of `v` are
intervals that meet, at a bag `i₀` holding the edge `uv`, so their union is an
interval. The now-isolated `v` is kept in bag `i₀` only, whose contents are
left as they were: there `u` and `v` already sat together, so the bag does
not grow either (`PathDecomposition.contract`).

Deletion is the general lemma `pathwidth_le_of_injective`: an injective graph
homomorphism `H →g G` gives `pathwidth H ≤ pathwidth G` (pull every bag back).
It covers induced subgraphs, subgraphs and relabellings at once.

## Sequences

A step is a pair `(v, some u)` (contract `v` into `u`, which must be an edge of
the current graph) or `(v, none)` (delete `v`, the code's `u = -1`; here any
vertex may be deleted, isolated or not). `applySeq` replays a list of steps,
`IsContractionSeq` says each contraction step is an edge when it is applied,
and `minorOf G seq` is `applySeq G seq` induced on the vertices that never
appear as the first component of a step.
-/

import MOSPFormalization.MOSPGraph

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### Width and pathwidth comparisons -/

namespace PathDecomposition

/-- If every bag has at most `k + 1` vertices, the width is at most `k`. -/
theorem width_le_of_forall_card_le {G : SimpleGraph V} (P : PathDecomposition G) {k : ℕ}
    (h : ∀ i, (P.bag i).card ≤ k + 1) : P.width ≤ k := by
  unfold width
  have : Finset.sup' (Finset.univ (α := Fin (P.length + 1)))
      (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
      (fun i => (P.bag i).card) ≤ k + 1 := Finset.sup'_le _ _ (fun i _ => h i)
  omega

end PathDecomposition

/-- To compare pathwidths it suffices to turn each decomposition of `G` into one
of `H` that is no wider. -/
theorem pathwidth_le_of_forall_decomposition {W : Type*} [Fintype W] [DecidableEq W]
    {G : SimpleGraph V} {H : SimpleGraph W}
    (h : ∀ P : PathDecomposition G, ∃ Q : PathDecomposition H, Q.width ≤ P.width) :
    pathwidth H ≤ pathwidth G := by
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq G
  obtain ⟨Q, hQ⟩ := h P
  exact (pathwidth_le_width H Q).trans (hP ▸ hQ)

/-! ### Deletion: injective homomorphisms -/

namespace PathDecomposition

variable {W : Type*} [Fintype W] [DecidableEq W] {G : SimpleGraph V} {H : SimpleGraph W}

/-- Pull a path decomposition back along an injective homomorphism `H →g G`. -/
def comap (P : PathDecomposition G) (f : H →g G) : PathDecomposition H where
  length := P.length
  bag i := Finset.univ.filter (fun a => f a ∈ P.bag i)
  vertex_coverage a := by
    obtain ⟨i, hi⟩ := P.vertex_coverage (f a)
    exact ⟨i, by simpa using hi⟩
  edge_coverage a b hab := by
    obtain ⟨i, hi, hj⟩ := P.edge_coverage (f a) (f b) (f.map_adj hab)
    exact ⟨i, by simpa using hi, by simpa using hj⟩
  interval a i j k hij hjk hi hk := by
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi hk ⊢
    exact P.interval (f a) i j k hij hjk hi hk

theorem comap_width_le (P : PathDecomposition G) (f : H →g G) (hf : Function.Injective f) :
    (P.comap f).width ≤ P.width := by
  apply width_le_of_forall_card_le
  intro i
  refine le_trans ?_ (P.bag_card_le_width_add_one i)
  apply Finset.card_le_card_of_injOn f
  · intro a ha
    simpa [comap] using ha
  · exact hf.injOn

end PathDecomposition

/-- An injective graph homomorphism `H →g G` (an isomorphism onto a subgraph of
`G`) gives `pathwidth H ≤ pathwidth G`. -/
theorem pathwidth_le_of_injective {W : Type*} [Fintype W] [DecidableEq W]
    {G : SimpleGraph V} {H : SimpleGraph W} (f : H →g G) (hf : Function.Injective f) :
    pathwidth H ≤ pathwidth G :=
  pathwidth_le_of_forall_decomposition fun P => ⟨P.comap f, P.comap_width_le f hf⟩

/-- **Edge deletion**: a subgraph on the same vertices has no larger pathwidth. -/
theorem pathwidth_mono {G H : SimpleGraph V} (h : H ≤ G) : pathwidth H ≤ pathwidth G :=
  pathwidth_le_of_injective ⟨id, fun hab => h hab⟩ Function.injective_id

/-- **Vertex deletion**: an induced subgraph has no larger pathwidth. -/
theorem pathwidth_induce_le (G : SimpleGraph V) (S : Set V) [DecidablePred (· ∈ S)] :
    pathwidth (G.induce S) ≤ pathwidth G :=
  pathwidth_le_of_injective (SimpleGraph.Embedding.induce S).toHom Subtype.val_injective

/-- Isomorphic graphs have equal pathwidth. -/
theorem pathwidth_eq_of_iso {W : Type*} [Fintype W] [DecidableEq W]
    {G : SimpleGraph V} {H : SimpleGraph W} (e : G ≃g H) : pathwidth G = pathwidth H :=
  le_antisymm (pathwidth_le_of_injective e.toEmbedding.toHom e.injective)
    (pathwidth_le_of_injective e.symm.toEmbedding.toHom e.symm.injective)

/-! ### Edge contraction -/

/-- Contract `v` into `u`: `u` keeps its label and gains the neighbours of `v`,
and `v` is left isolated. Matches `_contract(adj, alive, v, u)` in
`pathwidth_solver/pathwidth/minor.py` on every vertex other than `v`. -/
def contractEdge (G : SimpleGraph V) (u v : V) : SimpleGraph V where
  Adj x y := x ≠ y ∧ x ≠ v ∧ y ≠ v ∧
    (G.Adj x y ∨ (x = u ∧ G.Adj v y) ∨ (y = u ∧ G.Adj v x))
  symm := by
    constructor
    intro x y ⟨hxy, hx, hy, h⟩
    refine ⟨hxy.symm, hy, hx, ?_⟩
    rcases h with h | ⟨rfl, h⟩ | ⟨rfl, h⟩
    · exact Or.inl h.symm
    · exact Or.inr (Or.inr ⟨rfl, h⟩)
    · exact Or.inr (Or.inl ⟨rfl, h⟩)
  loopless := ⟨fun _ h => h.1 rfl⟩

/-- Delete every edge at `v`, leaving it isolated: vertex deletion on a fixed
vertex type (the code's step `(v, -1)`). -/
def isolate (G : SimpleGraph V) (v : V) : SimpleGraph V where
  Adj x y := G.Adj x y ∧ x ≠ v ∧ y ≠ v
  symm := ⟨fun _ _ ⟨h, hx, hy⟩ => ⟨h.symm, hy, hx⟩⟩
  loopless := ⟨fun x h => G.loopless.irrefl x h.1⟩

theorem isolate_le (G : SimpleGraph V) (v : V) : isolate G v ≤ G := fun _ _ h => h.1

namespace PathDecomposition

variable {G : SimpleGraph V}

/-- The bags of the contracted decomposition: `v` replaced by `u` everywhere,
except in the bag `i₀`, which is kept as it is. -/
def contractBag (P : PathDecomposition G) (u v : V) (i₀ i : Fin (P.length + 1)) : Finset V :=
  if i = i₀ then P.bag i else (P.bag i).image (fun x => if x = v then u else x)

variable (P : PathDecomposition G) {u v : V} {i₀ : Fin (P.length + 1)}

theorem mem_contractBag_self (huv : u ≠ v) (hv : v ∈ P.bag i₀) (i : Fin (P.length + 1)) :
    v ∈ P.contractBag u v i₀ i ↔ i = i₀ := by
  unfold contractBag
  split_ifs with hi
  · simp [hi, hv]
  · simp only [Finset.mem_image, hi, iff_false, not_exists, not_and]
    intro x _ hx
    split_ifs at hx with h
    · exact huv hx
    · exact h hx

theorem mem_contractBag_of_ne (hu : u ∈ P.bag i₀) {x : V} (hx : x ≠ v)
    (i : Fin (P.length + 1)) :
    x ∈ P.contractBag u v i₀ i ↔ x ∈ P.bag i ∨ (x = u ∧ v ∈ P.bag i) := by
  unfold contractBag
  split_ifs with hi
  · subst hi
    constructor
    · exact Or.inl
    · rintro (h | ⟨rfl, _⟩)
      · exact h
      · exact hu
  · simp only [Finset.mem_image]
    constructor
    · rintro ⟨y, hy, hyx⟩
      split_ifs at hyx with h
      · subst h; exact Or.inr ⟨hyx.symm, hy⟩
      · subst hyx; exact Or.inl hy
    · rintro (h | ⟨rfl, h⟩)
      · exact ⟨x, h, by simp [hx]⟩
      · exact ⟨v, h, by simp⟩

theorem contractBag_card_le (i : Fin (P.length + 1)) :
    (P.contractBag u v i₀ i).card ≤ (P.bag i).card := by
  unfold contractBag
  split_ifs
  · exact le_rfl
  · exact Finset.card_image_le

/-- The decomposition of `contractEdge G u v` obtained from one of `G`, given a
bag `i₀` holding both ends of the edge `uv`. -/
def contract (huv : G.Adj u v) (hu : u ∈ P.bag i₀) (hv : v ∈ P.bag i₀) :
    PathDecomposition (contractEdge G u v) where
  length := P.length
  bag := P.contractBag u v i₀
  vertex_coverage x := by
    by_cases hx : x = v
    · subst hx; exact ⟨i₀, (P.mem_contractBag_self huv.ne hv i₀).mpr rfl⟩
    · obtain ⟨i, hi⟩ := P.vertex_coverage x
      exact ⟨i, (P.mem_contractBag_of_ne hu hx i).mpr (Or.inl hi)⟩
  edge_coverage x y hxy := by
    obtain ⟨_, hx, hy, h⟩ := hxy
    rcases h with h | ⟨rfl, h⟩ | ⟨rfl, h⟩
    · obtain ⟨i, hxi, hyi⟩ := P.edge_coverage x y h
      exact ⟨i, (P.mem_contractBag_of_ne hu hx i).mpr (Or.inl hxi),
        (P.mem_contractBag_of_ne hu hy i).mpr (Or.inl hyi)⟩
    · obtain ⟨i, hvi, hyi⟩ := P.edge_coverage v y h
      exact ⟨i, (P.mem_contractBag_of_ne hu hx i).mpr (Or.inr ⟨rfl, hvi⟩),
        (P.mem_contractBag_of_ne hu hy i).mpr (Or.inl hyi)⟩
    · obtain ⟨i, hvi, hxi⟩ := P.edge_coverage v x h
      exact ⟨i, (P.mem_contractBag_of_ne hu hx i).mpr (Or.inl hxi),
        (P.mem_contractBag_of_ne hu hy i).mpr (Or.inr ⟨rfl, hvi⟩)⟩
  interval x i j k hij hjk hi hk := by
    by_cases hx : x = v
    · subst hx
      rw [P.mem_contractBag_self huv.ne hv] at hi hk ⊢
      subst hi; subst hk
      exact le_antisymm hjk hij
    · rw [P.mem_contractBag_of_ne hu hx] at hi hk ⊢
      by_cases hxu : x = u
      · subst hxu
        have hi' : x ∈ P.bag i ∨ v ∈ P.bag i := hi.imp id And.right
        have hk' : x ∈ P.bag k ∨ v ∈ P.bag k := hk.imp id And.right
        rcases hi' with hi' | hi' <;> rcases hk' with hk' | hk'
        · exact Or.inl (P.interval x i j k hij hjk hi' hk')
        · rcases le_total j i₀ with hj | hj
          · exact Or.inl (P.interval x i j i₀ hij hj hi' hu)
          · exact Or.inr ⟨rfl, P.interval v i₀ j k hj hjk hv hk'⟩
        · rcases le_total j i₀ with hj | hj
          · exact Or.inr ⟨rfl, P.interval v i j i₀ hij hj hi' hv⟩
          · exact Or.inl (P.interval x i₀ j k hj hjk hu hk')
        · exact Or.inr ⟨rfl, P.interval v i j k hij hjk hi' hk'⟩
      · have hi' : x ∈ P.bag i := hi.resolve_right (fun h => hxu h.1)
        have hk' : x ∈ P.bag k := hk.resolve_right (fun h => hxu h.1)
        exact Or.inl (P.interval x i j k hij hjk hi' hk')

theorem contract_width_le (huv : G.Adj u v) (hu : u ∈ P.bag i₀) (hv : v ∈ P.bag i₀) :
    (P.contract huv hu hv).width ≤ P.width :=
  width_le_of_forall_card_le _ fun i =>
    (P.contractBag_card_le i).trans (P.bag_card_le_width_add_one i)

end PathDecomposition

/-- **Contracting an edge never increases pathwidth.** -/
theorem pathwidth_contractEdge_le (G : SimpleGraph V) {u v : V} (huv : G.Adj u v) :
    pathwidth (contractEdge G u v) ≤ pathwidth G :=
  pathwidth_le_of_forall_decomposition fun P => by
    obtain ⟨i₀, hu, hv⟩ := P.edge_coverage u v huv
    exact ⟨P.contract huv hu hv, P.contract_width_le huv hu hv⟩

/-- The same with the contracted vertex removed: the minor on the remaining
vertices. -/
theorem pathwidth_contractEdge_induce_le (G : SimpleGraph V) {u v : V} (huv : G.Adj u v) :
    pathwidth ((contractEdge G u v).induce {x | x ≠ v}) ≤ pathwidth G :=
  (pathwidth_induce_le _ _).trans (pathwidth_contractEdge_le G huv)

/-! ### Contraction sequences -/

/-- One step of a contraction sequence, in the code's `(v, u)` order: `(v, some u)`
contracts `v` into `u`, `(v, none)` deletes `v` (the code's `u = -1`). -/
def applyStep (G : SimpleGraph V) : V × Option V → SimpleGraph V
  | (v, some u) => contractEdge G u v
  | (v, none) => isolate G v

/-- A step is legal when its contraction is an edge of the current graph. -/
def StepValid (G : SimpleGraph V) : V × Option V → Prop
  | (v, some u) => G.Adj u v
  | (_, none) => True

/-- Replay a sequence of steps. -/
def applySeq : SimpleGraph V → List (V × Option V) → SimpleGraph V
  | G, [] => G
  | G, s :: rest => applySeq (applyStep G s) rest

/-- Every step is legal at the moment it is applied (what `replay` checks). -/
def IsContractionSeq : SimpleGraph V → List (V × Option V) → Prop
  | _, [] => True
  | G, s :: rest => StepValid G s ∧ IsContractionSeq (applyStep G s) rest

/-- The vertices a sequence removes: the first component of every step. -/
def removed (seq : List (V × Option V)) : Finset V := (seq.map Prod.fst).toFinset

/-- The minor a sequence produces: the replayed graph on the vertices it never
removed. -/
def minorOf (G : SimpleGraph V) (seq : List (V × Option V)) :
    SimpleGraph {x : V // x ∉ removed seq} :=
  (applySeq G seq).induce {x | x ∉ removed seq}

theorem pathwidth_applyStep_le (G : SimpleGraph V) (s : V × Option V) (hs : StepValid G s) :
    pathwidth (applyStep G s) ≤ pathwidth G := by
  obtain ⟨v, _ | u⟩ := s
  · exact pathwidth_mono (isolate_le G v)
  · exact pathwidth_contractEdge_le G hs

/-- **Iterated contraction**: replaying a legal sequence never increases pathwidth. -/
theorem pathwidth_applySeq_le (G : SimpleGraph V) (seq : List (V × Option V))
    (h : IsContractionSeq G seq) : pathwidth (applySeq G seq) ≤ pathwidth G := by
  induction seq generalizing G with
  | nil => exact le_rfl
  | cons s rest ih =>
    exact (ih (applyStep G s) h.2).trans (pathwidth_applyStep_le G s h.1)

/-- **Minor monotonicity for a contraction sequence.** -/
theorem pathwidth_minorOf_le (G : SimpleGraph V) (seq : List (V × Option V))
    (h : IsContractionSeq G seq) : pathwidth (minorOf G seq) ≤ pathwidth G :=
  (pathwidth_induce_le _ _).trans (pathwidth_applySeq_le G seq h)

/-- **Every minor**: a subgraph of the minor of a legal sequence (edge deletions
last) has no larger pathwidth. Any minor of `G` is of this form, up to
isomorphism (`pathwidth_eq_of_iso`): contract a spanning tree of each branch set,
delete the vertices in no branch set, then delete the surplus edges. -/
theorem pathwidth_le_of_le_minorOf (G : SimpleGraph V) (seq : List (V × Option V))
    (h : IsContractionSeq G seq) {H : SimpleGraph {x : V // x ∉ removed seq}}
    (hH : H ≤ minorOf G seq) : pathwidth H ≤ pathwidth G :=
  (pathwidth_mono hH).trans (pathwidth_minorOf_le G seq h)

/-- **The certificate theorem**: if the minor of a legal contraction sequence has
pathwidth above `w`, so has the graph. A refutation of `pathwidth H ≤ w` on the
minor `H` proves `pathwidth G ≥ w + 1`. -/
theorem pathwidth_gt_of_minorOf (G : SimpleGraph V) (seq : List (V × Option V))
    (h : IsContractionSeq G seq) {w : ℕ} (hw : w < pathwidth (minorOf G seq)) :
    w < pathwidth G :=
  lt_of_lt_of_le hw (pathwidth_minorOf_le G seq h)

/-- The certificate theorem for a minor given on its own vertex type (the code's
`0..m-1` with `labels`), through any isomorphism to `minorOf G seq`. -/
theorem pathwidth_gt_of_iso_minorOf {W : Type*} [Fintype W] [DecidableEq W]
    (G : SimpleGraph V) (seq : List (V × Option V)) (h : IsContractionSeq G seq)
    {H : SimpleGraph W} (e : H ≃g minorOf G seq) {w : ℕ} (hw : w < pathwidth H) :
    w < pathwidth G :=
  pathwidth_gt_of_minorOf G seq h (by rwa [← pathwidth_eq_of_iso e])

/-! ### The MOSP corollary -/

namespace MOSPInstance

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]
variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- **Minor proofs for MOSP**: a legal contraction sequence of the MOSP graph whose
minor has pathwidth above `w` proves that every pattern order opens more than
`w + 1` stacks. No hypothesis on the instance is needed: without any
requirement the MOSP graph is edgeless and no minor has positive pathwidth. -/
theorem lt_mospValue_of_minorOf (seq : List (C × Option C))
    (h : IsContractionSeq M.mospGraph seq) {w : ℕ}
    (hw : w < pathwidth (minorOf M.mospGraph seq)) : w + 1 < M.mospValue := by
  have hG := pathwidth_gt_of_minorOf M.mospGraph seq h hw
  by_cases hreq : ∃ c p, M.requires c p
  · rw [M.mospValue_eq_pathwidth_add_one hreq]
    omega
  · simp only [not_exists] at hreq
    rw [M.pathwidth_mospGraph_eq_zero_of_forall_not hreq] at hG
    omega

end MOSPInstance

end MOSPFormalization
