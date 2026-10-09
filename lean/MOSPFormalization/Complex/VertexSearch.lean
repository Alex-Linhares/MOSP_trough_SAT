/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Vertex search (Bienstock, Robertson, Seymour & Thomas 1991) = pathwidth + 1

Bienstock, Robertson, Seymour & Thomas (1991), *Quickly excluding a forest*,
J. Combin. Theory Ser. B 52, 274–283, §5, pp. 282–283 ([BRST]). The fugitive
lives on the vertices; this is the game in which an edgeless graph needs one
searcher, where the node search game of Kirousis & Papadimitriou needs none.

## The source's definition

[BRST] p. 282: "let us say a *search* in G is a sequence (X_1, …, X_m) of
subsets of V(G), such that X_1 = ∅ and for 1 ≤ i < m, either X_{i+1} ⊆ X_i or
X_i ⊆ X_{i+1}. (These are the positions occupied by the searchers at each
stage.) Let B_1 = V(G), and inductively let B_i be the set of all vertices v of
G such that there is a path P of G between v and some vertex of B_{i−1}, with
V(P) ∩ X_i = ∅. (B_i represents the places where the person we are rescuing may
currently be, if we have not found him yet.) The search is *successful* if
B_m = ∅. We want to know if there is a successful search (X_1, …, X_m) with
each |X_i| ≤ n, for some given n. A successful search is *monotone* if
B_1 ⊇ B_2 ⊇ … ⊇ B_m = ∅".

"(5.1) For a graph G and integer n ≥ 0, the following are equivalent:
(i) there is a successful search (X_1, …, X_m) in G with each |X_i| ≤ n;
(ii) there is no blockage in G of order n; (iii) G has path-width ≤ n − 1;
(iv) there is a monotone successful search (X_1, …, X_m) in G with each
|X_i| ≤ n."

Formalised item by item:

* a sequence `(X_1, …, X_m)` is a `List (Finset V)`; `IsVertexSearch` says
  its head is `∅` (so `m ≥ 1`) and that consecutive entries are nested
  (`List.IsChain`, either inclusion);
* `nextRegion G X B` is `B_i` from `B = B_{i−1}` and `X = X_i`: the vertices
  `v` with a `G.Walk v u`, `u ∈ B`, that `IsPath` and whose support misses
  `X`. The path of length zero counts, so `v ∈ B \ X` stays; a vertex of `X`
  is never in the region;
* `regionSeq G X = (B_1, …, B_m)`, with `B_1 = univ` and `X_1` unused;
* `IsSuccessfulVertexSearch`: `B_m = ∅` (the last entry of `regionSeq`);
  `IsMonotoneVertexSearch`: successful and `regionSeq` decreasing;
* `vertexSearchNumber G`: the least `n` with a successful search, each
  `|X_i| ≤ n` ((5.1)(i)); `monotoneVertexSearchNumber G` likewise for (iv).

Blockages ((ii)) are not formalised; the cycle (i) ⇒ (iii) ⇒ (iv) ⇒ (i) is
closed without them.

## What is proved

* `vertexSearchNumber_eq_pathwidth_add_one` — **(i) ⇔ (iii)**: the vertex
  search number is `pw(G) + 1` on every finite graph with a vertex, edgeless
  graphs included; `monotoneVertexSearchNumber_eq_pathwidth_add_one` —
  **(iv) ⇔ (iii)**; `vertexSearch_iff` — (5.1) for each `n`, as stated;
  `vertexSearchNumber_eq_monotoneVertexSearchNumber` — recontamination does
  not help.
  - **(iii) ⇒ (iv)**, BRST's own construction: from a path decomposition
    `(W_0, …, W_L)`, the search `(∅, W_0, W_0 ∩ W_1, W_1, …, W_L)`
    (`PathDecomposition.isMonotoneVertexSearch`). After `W_j`, and after
    `W_j ∩ W_{j+1}`, the region is `V − (W_0 ∪ … ∪ W_j)`
    (`foldl_bagPositions`), because a vertex of `W_0 ∪ … ∪ W_j` with a
    neighbour outside lies in `W_j ∩ W_{j+1}` (`IsBagSequence.boundary`).
  - **(i) ⇒ (iii)**, not by blockages but by **reduction to the node search
    game** of `NodeSearch.lean`, whose full-game lower bound is proved in
    `NodeMonotonicity.lean`: play each change of position as single
    removals and placements (`simMoves`). Every contaminated edge then keeps
    an endpoint in the current region — in the region reachable from
    `B_{i−1}` avoiding the current searchers while they are removed, in
    `B_{i−1}` minus the current searchers while they are placed
    (`touches_runSearch_remove`, `touches_runSearch_place`) — so a
    successful vertex search with `|X_i| ≤ n` clears every edge with at most
    `n` searchers (`isNodeSearch_of_isSuccessfulVertexSearch`), and
    `ns(G) ≤` the vertex search number (`nodeSearch_le_vertexSearchNumber`).
    With an edge, `ns = pw + 1` finishes; edgeless, `pw = 0`
    (`pathwidth_of_edgeless`) and a vertex needs a searcher
    (`one_le_vertexSearchNumber`).
* `vertexSearchNumber_eq_nodeSearch` — with an edge, the vertex search number
  is the node search number.

## Edge cases

* Edgeless with a vertex: `vertexSearchNumber_of_edgeless`, the value is
  `1 = pw + 1` while `ns = 0`. This is where the two games part.
* No vertices: `vertexSearchNumber_of_isEmpty`, the one-position search `(∅)`
  is successful since `B_1 = V(G) = ∅`, so both numbers are `0`, while
  `pw + 1 = 1` (`pathwidth_add_one_of_isEmpty`); the main theorem assumes
  `Nonempty V`.
-/

import MOSPFormalization.Complex.NodeMonotonicity

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Definitions (BRST 1991, §5, p. 282) -/

open Classical in
/-- The contaminated region after the searchers move to `X`, given the region
`B` before the move: "the set of all vertices `v` of `G` such that there is a
path `P` of `G` between `v` and some vertex of `B_{i−1}`, with
`V(P) ∩ X_i = ∅`". The path may have length zero. -/
noncomputable def nextRegion (X B : Finset V) : Finset V :=
  univ.filter fun v => ∃ u ∈ B, ∃ p : G.Walk v u, p.IsPath ∧ ∀ w ∈ p.support, w ∉ X

/-- The regions `B, B', B'', …` produced from `B` by the positions `Ys` in turn
(the list has one more entry than `Ys`). -/
noncomputable def regionsFrom : Finset V → List (Finset V) → List (Finset V)
  | B, [] => [B]
  | B, Y :: Ys => B :: regionsFrom (nextRegion G Y B) Ys

/-- The contaminated regions `(B_1, …, B_m)` of a search `(X_1, …, X_m)`:
`B_1 = V(G)`, and `B_i` is computed from `B_{i−1}` and `X_i` for `i ≥ 2`. -/
noncomputable def regionSeq (X : List (Finset V)) : List (Finset V) :=
  regionsFrom G univ X.tail

/-- A **search** in `G` ([BRST] p. 282): a sequence `(X_1, …, X_m)` of subsets of
`V(G)` with `X_1 = ∅` and, for `1 ≤ i < m`, `X_{i+1} ⊆ X_i` or `X_i ⊆ X_{i+1}`. -/
structure IsVertexSearch (X : List (Finset V)) : Prop where
  head_eq : X.head? = some ∅
  chain : X.IsChain fun A B => B ⊆ A ∨ A ⊆ B

/-- A search is **successful** if `B_m = ∅`. -/
def IsSuccessfulVertexSearch (X : List (Finset V)) : Prop :=
  IsVertexSearch X ∧ (regionSeq G X).getLast? = some ∅

/-- A successful search is **monotone** if `B_1 ⊇ B_2 ⊇ … ⊇ B_m`. -/
def IsMonotoneVertexSearch (X : List (Finset V)) : Prop :=
  IsSuccessfulVertexSearch G X ∧ (regionSeq G X).IsChain fun A B => B ⊆ A

/-- The least `n` such that there is a successful search with each `|X_i| ≤ n`
([BRST] (5.1)(i)). -/
noncomputable def vertexSearchNumber : ℕ :=
  sInf {n | ∃ X, IsSuccessfulVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ n}

/-- The least `n` such that there is a monotone successful search with each
`|X_i| ≤ n` ([BRST] (5.1)(iv)). -/
noncomputable def monotoneVertexSearchNumber : ℕ :=
  sInf {n | ∃ X, IsMonotoneVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ n}

/-! ### The region as reachability -/

section Region

variable {G}

theorem freeReach_of_walk {X : Finset V} {v u : V} (p : G.Walk v u)
    (hp : ∀ w ∈ p.support, w ∉ X) : FreeReach G X v u := by
  induction p with
  | nil => exact Relation.ReflTransGen.refl
  | @cons a b c h q ih =>
    have ha : a ∉ X := hp a (by simp)
    have hb : b ∉ X := hp b (by simp [SimpleGraph.Walk.start_mem_support])
    exact Relation.ReflTransGen.head ⟨h, ha, hb⟩
      (ih fun w hw => hp w (by simp [hw]))

theorem exists_walk_of_freeReach {X : Finset V} {v u : V} (h : FreeReach G X v u)
    (hv : v ∉ X) : ∃ p : G.Walk v u, ∀ w ∈ p.support, w ∉ X := by
  induction h using Relation.ReflTransGen.head_induction_on with
  | refl => exact ⟨SimpleGraph.Walk.nil, by simpa using hv⟩
  | @head a b hab _ ih =>
    obtain ⟨q, hq⟩ := ih hab.2.2
    refine ⟨SimpleGraph.Walk.cons hab.1 q, ?_⟩
    intro w hw
    rw [SimpleGraph.Walk.support_cons, List.mem_cons] at hw
    rcases hw with rfl | hw
    · exact hab.2.1
    · exact hq w hw

theorem mem_nextRegion {X B : Finset V} {v : V} :
    v ∈ nextRegion G X B ↔ v ∉ X ∧ ∃ u ∈ B, FreeReach G X v u := by
  classical
  unfold nextRegion
  rw [mem_filter]
  constructor
  · rintro ⟨-, u, hu, p, -, hp⟩
    exact ⟨hp v p.start_mem_support, u, hu, freeReach_of_walk p hp⟩
  · rintro ⟨hv, u, hu, h⟩
    obtain ⟨p, hp⟩ := exists_walk_of_freeReach h hv
    refine ⟨mem_univ _, u, hu, p.toPath, p.toPath.2, fun w hw => hp w ?_⟩
    exact SimpleGraph.Walk.support_toPath_subset_support p hw

theorem not_mem_of_mem_nextRegion {X B : Finset V} {v : V} (h : v ∈ nextRegion G X B) :
    v ∉ X :=
  (mem_nextRegion.mp h).1

/-- A set closed under searcher-free steps backwards. -/
def FreeClosed (X P : Finset V) : Prop := ∀ x y, FreeStep G X x y → y ∈ P → x ∈ P

theorem FreeClosed.of_freeReach {X P : Finset V} (hP : FreeClosed (G := G) X P) {x y : V}
    (h : FreeReach G X x y) (hy : y ∈ P) : x ∈ P := by
  induction h using Relation.ReflTransGen.head_induction_on with
  | refl => exact hy
  | head hab _ ih => exact hP _ _ hab ih

theorem freeClosed_nextRegion (X B : Finset V) : FreeClosed (G := G) X (nextRegion G X B) := by
  intro x y hxy hy
  obtain ⟨-, u, hu, hyu⟩ := mem_nextRegion.mp hy
  exact mem_nextRegion.mpr ⟨hxy.2.1, u, hu, Relation.ReflTransGen.head hxy hyu⟩

theorem nextRegion_mono_left {X X' B : Finset V} (h : X' ⊆ X) :
    nextRegion G X B ⊆ nextRegion G X' B := by
  intro v hv
  obtain ⟨hvX, u, hu, hvu⟩ := mem_nextRegion.mp hv
  exact mem_nextRegion.mpr ⟨fun h' => hvX (h h'), u, hu, hvu.mono h⟩

theorem sdiff_subset_nextRegion (X B : Finset V) : B \ X ⊆ nextRegion G X B := by
  intro v hv
  rw [mem_sdiff] at hv
  exact mem_nextRegion.mpr ⟨hv.2, v, hv.1, Relation.ReflTransGen.refl⟩

theorem nextRegion_empty_univ : nextRegion G ∅ (univ : Finset V) = univ := by
  apply eq_univ_of_forall
  intro v
  exact mem_nextRegion.mpr ⟨notMem_empty v, v, mem_univ v, Relation.ReflTransGen.refl⟩

theorem regionsFrom_getLast? (B : Finset V) (Ys : List (Finset V)) :
    (regionsFrom G B Ys).getLast? = some (Ys.foldl (fun B Y => nextRegion G Y B) B) := by
  induction Ys generalizing B with
  | nil => rfl
  | cons Y Ys ih =>
    rw [regionsFrom, List.foldl_cons, ← ih]
    cases h : regionsFrom G (nextRegion G Y B) Ys with
    | nil => cases Ys <;> simp [regionsFrom] at h
    | cons a l => simp

theorem regionsFrom_head? (B : Finset V) (Ys : List (Finset V)) :
    (regionsFrom G B Ys).head? = some B := by
  cases Ys <;> rfl

theorem isChain_regionsFrom_append {R : Finset V → Finset V → Prop} (B : Finset V)
    (l₁ l₂ : List (Finset V)) :
    (regionsFrom G B (l₁ ++ l₂)).IsChain R ↔ (regionsFrom G B l₁).IsChain R ∧
      (regionsFrom G (l₁.foldl (fun B Y => nextRegion G Y B) B) l₂).IsChain R := by
  induction l₁ generalizing B with
  | nil => simp [regionsFrom]
  | cons Y l₁ ih =>
    simp only [List.cons_append, regionsFrom, List.foldl_cons]
    rw [List.isChain_cons, List.isChain_cons, ih, regionsFrom_head?, regionsFrom_head?]
    tauto

end Region

/-! ### From a vertex search to a node search -/

section Reduction

variable {G}

/-- Every edge of `D` has an endpoint in `P`. -/
def Touches (D : Set (Sym2 V)) (P : Finset V) : Prop := ∀ e ∈ D, ∃ x ∈ e, x ∈ P

theorem Touches.mono {D : Set (Sym2 V)} {P Q : Finset V} (h : Touches D P) (hPQ : P ⊆ Q) :
    Touches D Q := fun e he =>
  let ⟨x, hx, hxP⟩ := h e he
  ⟨x, hx, hPQ hxP⟩

/-- One node-search move keeps the contaminated edges touching `P`, provided
`P` is unguarded, closed under searcher-free steps, and touched by every
contaminated edge that the move does not clear. -/
theorem touches_step {s : SearchState V} (hs : s.contaminated ⊆ G.edgeSet) (m : SearchMove V)
    {P : Finset V} (hP1 : ∀ v ∈ P, v ∉ m.applyTo s.guards)
    (hP2 : FreeClosed (G := G) (m.applyTo s.guards) P)
    (hD : ∀ e ∈ s.contaminated, ¬ Guarded (m.applyTo s.guards) e → ∃ x ∈ e, x ∈ P) :
    Touches (searchStep G s m).contaminated P := by
  intro e he
  simp only [searchStep] at he
  rcases he with ⟨he, hg⟩ | ⟨-, f, ⟨hf, hfg⟩, x, hx, y, hy, hxS, hxy⟩
  · exact hD e he hg
  · refine ⟨x, hx, hP2.of_freeReach hxy ?_⟩
    obtain ⟨z, hz, hzP⟩ := hD f hf hfg
    rcases eq_or_adj_of_mem_edgeSet (hs hf) hy hz with rfl | hadj
    · exact hzP
    · exact hP2 _ _ ⟨hadj, freeReach_not_mem hxy hxS, hP1 z hzP⟩ hzP

theorem guards_runSearch_remove (s : SearchState V) (l : List V) :
    (runSearch G s (l.map .remove)).guards = s.guards \ l.toFinset := by
  induction l generalizing s with
  | nil => simp [runSearch]
  | cons v l ih =>
    change (runSearch G (searchStep G s (.remove v)) (l.map .remove)).guards = _
    rw [ih]
    ext x
    simp only [searchStep, SearchMove.applyTo, mem_sdiff, mem_erase, List.toFinset_cons,
      mem_insert, List.mem_toFinset]
    tauto

theorem guards_runSearch_place (s : SearchState V) (l : List V) :
    (runSearch G s (l.map .place)).guards = s.guards ∪ l.toFinset := by
  induction l generalizing s with
  | nil => simp [runSearch]
  | cons v l ih =>
    change (runSearch G (searchStep G s (.place v)) (l.map .place)).guards = _
    rw [ih]
    ext x
    simp only [searchStep, SearchMove.applyTo, mem_union, List.toFinset_cons,
      mem_insert, List.mem_toFinset]
    tauto

/-- Removing searchers one at a time: the contaminated edges keep touching the
region reachable from `B` avoiding the current searchers. -/
theorem touches_runSearch_remove {B : Finset V} (l : List V) (s : SearchState V)
    (hs : s.contaminated ⊆ G.edgeSet) (h : Touches s.contaminated (nextRegion G s.guards B)) :
    Touches (runSearch G s (l.map .remove)).contaminated
      (nextRegion G (runSearch G s (l.map .remove)).guards B) := by
  induction l generalizing s with
  | nil => simpa [runSearch] using h
  | cons v l ih =>
    apply ih (searchStep G s (.remove v)) (contaminated_step_subset_edgeSet hs _)
    apply touches_step hs
    · intro w hw
      exact not_mem_of_mem_nextRegion hw
    · exact freeClosed_nextRegion _ _
    · intro e he _
      obtain ⟨x, hx, hxP⟩ := h e he
      exact ⟨x, hx, nextRegion_mono_left (erase_subset _ _) hxP⟩

/-- Placing searchers one at a time: the contaminated edges keep touching
`B` minus the current searchers. -/
theorem touches_runSearch_place {X B : Finset V} (hBX : ∀ v ∈ B, v ∉ X)
    (hB : FreeClosed (G := G) X B) (l : List V) (s : SearchState V)
    (hs : s.contaminated ⊆ G.edgeSet) (hX : X ⊆ s.guards)
    (h : Touches s.contaminated (B \ s.guards)) :
    Touches (runSearch G s (l.map .place)).contaminated
      (B \ (runSearch G s (l.map .place)).guards) := by
  induction l generalizing s with
  | nil => simpa [runSearch] using h
  | cons v l ih =>
    have hX' : X ⊆ insert v s.guards := hX.trans (subset_insert _ _)
    apply ih (searchStep G s (.place v)) (contaminated_step_subset_edgeSet hs _) hX'
    apply touches_step hs
    · intro w hw
      exact (mem_sdiff.mp hw).2
    · intro x y hxy hy
      rw [mem_sdiff] at hy ⊢
      exact ⟨hB x y ⟨hxy.1, fun h => hxy.2.1 (hX' h), fun h => hxy.2.2 (hX' h)⟩ hy.1,
        hxy.2.1⟩
    · intro e he hg
      obtain ⟨z, hz, hzP⟩ := h e he
      rw [mem_sdiff] at hzP
      by_cases hzS : z ∈ insert v s.guards
      · simp only [Guarded, not_forall] at hg
        obtain ⟨w, hw, hwS⟩ := hg
        rcases eq_or_adj_of_mem_edgeSet (hs he) hw hz with rfl | hadj
        · exact absurd hzS hwS
        · exact ⟨w, hw, mem_sdiff.mpr
            ⟨hB w z ⟨hadj, fun h => hwS (hX' h), hBX z hzP.1⟩ hzP.1, hwS⟩⟩
      · exact ⟨z, hz, mem_sdiff.mpr ⟨hzP.1, hzS⟩⟩

theorem searchCost_remove_le (s : SearchState V) (l : List V) :
    searchCost G s (l.map .remove) ≤ s.guards.card := by
  induction l generalizing s with
  | nil => exact le_rfl
  | cons v l ih =>
    simp only [List.map_cons, searchCost]
    refine max_le le_rfl ((ih _).trans ?_)
    exact card_le_card (erase_subset _ _)

theorem searchCost_place_le (s : SearchState V) (l : List V) :
    searchCost G s (l.map .place) ≤ (s.guards ∪ l.toFinset).card := by
  induction l generalizing s with
  | nil => simp [searchCost]
  | cons v l ih =>
    simp only [List.map_cons, searchCost]
    refine max_le (card_le_card subset_union_left) ((ih _).trans (card_le_card ?_))
    intro x
    simp only [searchStep, SearchMove.applyTo, mem_union, mem_insert, List.toFinset_cons,
      List.mem_toFinset]
    tauto

/-- The node-search moves taking the searchers from `A` to `C`: remove those of
`A \ C`, then place those of `C \ A`, one at a time. -/
noncomputable def transitionMoves (A C : Finset V) : List (SearchMove V) :=
  (A \ C).toList.map .remove ++ (C \ A).toList.map .place

/-- The node-search strategy simulating the positions `Cs` from `A`. -/
noncomputable def simMoves : Finset V → List (Finset V) → List (SearchMove V)
  | _, [] => []
  | A, C :: Cs => transitionMoves A C ++ simMoves C Cs

/-- One step of the search, simulated: from searchers `A` and a region `B`
touched by every contaminated edge, the moves to `C` (a subset or a superset of
`A`) leave the searchers on `C` and every contaminated edge touching the next
region, with at most `max |A| |C|` searchers on the way. -/
theorem transition_spec {A B C : Finset V} (s : SearchState V) (hsA : s.guards = A)
    (hs : s.contaminated ⊆ G.edgeSet) (h : Touches s.contaminated B)
    (hBA : ∀ v ∈ B, v ∉ A) (hB : FreeClosed (G := G) A B) (hAC : C ⊆ A ∨ A ⊆ C) :
    (runSearch G s (transitionMoves A C)).guards = C ∧
      Touches (runSearch G s (transitionMoves A C)).contaminated (nextRegion G C B) ∧
      searchCost G s (transitionMoves A C) ≤ max A.card C.card := by
  unfold transitionMoves
  rw [runSearch_append, searchCost_append]
  rcases hAC with hCA | hAC
  · have hnil : (C \ A).toList = [] := by
      rw [Finset.toList_eq_nil, sdiff_eq_empty_iff_subset]
      exact hCA
    rw [hnil]
    have hg : (runSearch G s ((A \ C).toList.map .remove)).guards = C := by
      rw [guards_runSearch_remove, hsA, Finset.toList_toFinset, Finset.sdiff_sdiff_eq_self hCA]
    have hBsub : B ⊆ nextRegion G s.guards B := by
      rw [hsA]
      intro v hv
      exact sdiff_subset_nextRegion A B (mem_sdiff.mpr ⟨hv, hBA v hv⟩)
    have ht := touches_runSearch_remove (B := B) (A \ C).toList s hs (h.mono hBsub)
    refine ⟨?_, ?_, ?_⟩
    · simpa [runSearch] using hg
    · rw [hg] at ht
      simpa [runSearch] using ht
    · refine max_le ((searchCost_remove_le _ _).trans (by rw [hsA]; exact le_max_left _ _)) ?_
      simp only [List.map_nil, searchCost, hg]
      exact le_max_right _ _
  · have hnil : (A \ C).toList = [] := by
      rw [Finset.toList_eq_nil, sdiff_eq_empty_iff_subset]
      exact hAC
    rw [hnil]
    simp only [List.map_nil]
    have h0 : runSearch G s [] = s := rfl
    rw [h0]
    have hg : (runSearch G s ((C \ A).toList.map .place)).guards = C := by
      rw [guards_runSearch_place, hsA, Finset.toList_toFinset, union_sdiff_of_subset hAC]
    have hBsub : B ⊆ B \ s.guards := by
      rw [hsA]
      intro v hv
      exact mem_sdiff.mpr ⟨hv, hBA v hv⟩
    have ht := touches_runSearch_place hBA hB (C \ A).toList s hs hsA.ge (h.mono hBsub)
    rw [hg] at ht
    refine ⟨hg, ht.mono ?_, ?_⟩
    · intro v hv
      rw [mem_sdiff] at hv
      exact sdiff_subset_nextRegion C B (mem_sdiff.mpr hv)
    · refine max_le (by simp [searchCost, hsA]) ?_
      refine (searchCost_place_le _ _).trans ?_
      rw [hsA, Finset.toList_toFinset, union_sdiff_of_subset hAC]
      exact le_max_right _ _

/-- The whole simulation. -/
theorem simMoves_spec (Cs : List (Finset V)) : ∀ (A B : Finset V) (s : SearchState V) (n : ℕ),
    s.guards = A → s.contaminated ⊆ G.edgeSet → Touches s.contaminated B →
    (∀ v ∈ B, v ∉ A) → FreeClosed (G := G) A B →
    (A :: Cs).IsChain (fun A B => B ⊆ A ∨ A ⊆ B) → (∀ Y ∈ A :: Cs, Y.card ≤ n) →
    Touches (runSearch G s (simMoves A Cs)).contaminated
        (Cs.foldl (fun B Y => nextRegion G Y B) B) ∧
      searchCost G s (simMoves A Cs) ≤ n := by
  induction Cs with
  | nil =>
    intro A B s n hsA _ h _ _ _ hn
    refine ⟨h, ?_⟩
    simp only [simMoves, searchCost, hsA]
    exact hn A (List.mem_singleton_self A)
  | cons C Cs ih =>
    intro A B s n hsA hs h hBA hB hch hn
    rw [List.isChain_cons_cons] at hch
    obtain ⟨hg, ht, hc⟩ := transition_spec s hsA hs h hBA hB hch.1
    have := ih C (nextRegion G C B) _ n hg (contaminated_runSearch_subset_edgeSet hs _) ht
      (fun v hv => not_mem_of_mem_nextRegion hv) (freeClosed_nextRegion C B) hch.2
      (fun Y hY => hn Y (List.mem_cons_of_mem A hY))
    simp only [simMoves, List.foldl_cons]
    rw [runSearch_append, searchCost_append]
    refine ⟨this.1, max_le (hc.trans (max_le (hn A (by simp)) (hn C (by simp)))) this.2⟩

variable (G) in
/-- **A vertex search is a node search.** A successful search `(X_1, …, X_m)`
with each `|X_i| ≤ n`, played as single placements and removals, clears every
edge with at most `n` searchers: throughout, every contaminated edge has an
endpoint in the contaminated region `B_i`. -/
theorem isNodeSearch_of_isSuccessfulVertexSearch {X : List (Finset V)} {n : ℕ}
    (hX : IsSuccessfulVertexSearch G X) (hn : ∀ Y ∈ X, Y.card ≤ n) :
    IsNodeSearch G n (simMoves ∅ X.tail) := by
  obtain ⟨⟨hhead, hch⟩, hlast⟩ := hX
  obtain ⟨Xs, rfl⟩ : ∃ Xs, X = ∅ :: Xs := by
    cases X with
    | nil => simp at hhead
    | cons Y Ys => simp at hhead; exact ⟨Ys, by rw [hhead]⟩
  have hspec := simMoves_spec Xs ∅ univ (searchInit G) n rfl (subset_refl _)
    (by
      intro e _
      induction e using Sym2.ind with
      | h a b => exact ⟨a, Sym2.mem_mk_left a b, mem_univ a⟩)
    (fun v _ h => notMem_empty v h)
    (fun x _ _ _ => mem_univ x) hch hn
  unfold regionSeq at hlast
  rw [List.tail_cons, regionsFrom_getLast?, Option.some_inj] at hlast
  rw [hlast] at hspec
  refine ⟨?_, hspec.2⟩
  apply Set.eq_empty_of_forall_notMem
  intro e he
  obtain ⟨x, -, hx⟩ := hspec.1 e he
  exact notMem_empty x hx

end Reduction

/-! ### From a path decomposition to a monotone search ([BRST] (iii) ⇒ (iv)) -/

section Upper

/-- [BRST] p. 283: from a path decomposition `(W_0, …, W_L)`, the positions
`W_0, W_0 ∩ W_1, W_1, …, W_{L−1} ∩ W_L, W_L` (the search is these after `∅`). -/
def bagPositions (W : ℕ → Finset V) : ℕ → List (Finset V)
  | 0 => [W 0]
  | j + 1 => bagPositions W j ++ [W j ∩ W (j + 1), W (j + 1)]

/-- `W_0 ∪ … ∪ W_j`. -/
def bagsUpTo (W : ℕ → Finset V) (j : ℕ) : Finset V := (range (j + 1)).biUnion W

theorem mem_bagsUpTo {W : ℕ → Finset V} {j : ℕ} {v : V} :
    v ∈ bagsUpTo W j ↔ ∃ i ≤ j, v ∈ W i := by
  simp only [bagsUpTo, mem_biUnion, mem_range]
  constructor
  · rintro ⟨i, hi, hv⟩
    exact ⟨i, by omega, hv⟩
  · rintro ⟨i, hi, hv⟩
    exact ⟨i, by omega, hv⟩

theorem subset_bagsUpTo (W : ℕ → Finset V) (j : ℕ) : W j ⊆ bagsUpTo W j :=
  fun _ hv => mem_bagsUpTo.mpr ⟨j, le_rfl, hv⟩

theorem bagsUpTo_mono (W : ℕ → Finset V) (j : ℕ) : bagsUpTo W j ⊆ bagsUpTo W (j + 1) := by
  intro v hv
  obtain ⟨i, hi, hv⟩ := mem_bagsUpTo.mp hv
  exact mem_bagsUpTo.mpr ⟨i, by omega, hv⟩

theorem bagsUpTo_succ_sdiff (W : ℕ → Finset V) (j : ℕ) :
    bagsUpTo W (j + 1) \ bagsUpTo W j ⊆ W (j + 1) := by
  intro v hv
  rw [mem_sdiff, mem_bagsUpTo, mem_bagsUpTo] at hv
  obtain ⟨⟨i, hi, hv⟩, hn⟩ := hv
  rcases Nat.lt_or_ge i (j + 1) with h | h
  · exact absurd ⟨i, by omega, hv⟩ hn
  · obtain rfl : i = j + 1 := by omega
    exact hv

variable {G}

/-- The two properties of a path decomposition that the search uses, for bags
indexed by all of `ℕ`. -/
structure IsBagSequence (W : ℕ → Finset V) : Prop where
  edge : ∀ u v, G.Adj u v → ∃ j, u ∈ W j ∧ v ∈ W j
  interval : ∀ v i j k, i ≤ j → j ≤ k → v ∈ W i → v ∈ W k → v ∈ W j

/-- A vertex of `W_0 ∪ … ∪ W_j` with a neighbour outside lies in `W_j ∩ W_{j+1}`. -/
theorem IsBagSequence.boundary {W : ℕ → Finset V} (hW : IsBagSequence (G := G) W) {j : ℕ}
    {x y : V} (hx : x ∈ bagsUpTo W j) (hy : y ∉ bagsUpTo W j) (hxy : G.Adj x y) :
    x ∈ W j ∧ x ∈ W (j + 1) := by
  obtain ⟨i, hi, hxi⟩ := mem_bagsUpTo.mp hx
  obtain ⟨l, hxl, hyl⟩ := hW.edge x y hxy
  have hl : j < l := by
    by_contra h
    exact hy (mem_bagsUpTo.mpr ⟨l, by omega, hyl⟩)
  exact ⟨hW.interval x i j l hi hl.le hxi hxl, hW.interval x i (j + 1) l (by omega) hl hxi hxl⟩

/-- The region after moving to `Y`, from the complement of `U`, is the
complement of `U'`, when `U ⊆ U'`, `U' \ U ⊆ Y ⊆ U'`, and every vertex of `U'`
with a neighbour outside lies in `Y`. -/
theorem nextRegion_compl {Y U U' : Finset V} (hUU' : U ⊆ U') (hY : U' \ U ⊆ Y) (hYU : Y ⊆ U')
    (hbd : ∀ x y, x ∈ U' → y ∉ U' → G.Adj x y → x ∈ Y) :
    nextRegion G Y (univ \ U) = univ \ U' := by
  ext v
  rw [mem_nextRegion, mem_sdiff]
  constructor
  · rintro ⟨hvY, u, hu, hvu⟩
    refine ⟨mem_univ v, fun hv => ?_⟩
    have key : ∀ a, FreeReach G Y a u → a ∈ U' → a ∉ Y → u ∈ U' := by
      intro a ha
      induction ha using Relation.ReflTransGen.head_induction_on with
      | refl => exact fun h _ => h
      | @head a b hab _ ih =>
        intro haU haY
        have hbU : b ∈ U' := by
          by_contra hb
          exact haY (hbd a b haU hb hab.1)
        exact ih hbU hab.2.2
    have huU := key v hvu hv hvY
    have huY := freeReach_not_mem hvu hvY
    exact huY (hY (mem_sdiff.mpr ⟨huU, (mem_sdiff.mp hu).2⟩))
  · rintro ⟨-, hv⟩
    exact ⟨fun h => hv (hYU h), v, mem_sdiff.mpr ⟨mem_univ v, fun h => hv (hUU' h)⟩,
      Relation.ReflTransGen.refl⟩

theorem foldl_bagPositions {W : ℕ → Finset V} (hW : IsBagSequence (G := G) W) (j : ℕ) :
    (bagPositions W j).foldl (fun B Y => nextRegion G Y B) univ = univ \ bagsUpTo W j := by
  induction j with
  | zero =>
    simp only [bagPositions, List.foldl_cons, List.foldl_nil]
    have h := nextRegion_compl (G := G) (U := ∅) (U' := bagsUpTo W 0) (Y := W 0)
      (empty_subset _) ?_ (subset_bagsUpTo W 0) ?_
    · rwa [sdiff_empty] at h
    · intro v hv
      obtain ⟨i, hi, hv⟩ := mem_bagsUpTo.mp (mem_sdiff.mp hv).1
      obtain rfl : i = 0 := by omega
      exact hv
    · intro x y hx hy hxy
      exact (hW.boundary hx hy hxy).1
  | succ j ih =>
    simp only [bagPositions, List.foldl_append, List.foldl_cons, List.foldl_nil, ih]
    rw [nextRegion_compl subset_rfl (by simp) ((inter_subset_left).trans (subset_bagsUpTo W j))
      (fun x y hx hy hxy => mem_inter.mpr (hW.boundary hx hy hxy))]
    rw [nextRegion_compl (bagsUpTo_mono W j) (bagsUpTo_succ_sdiff W j) (subset_bagsUpTo W _)]
    intro x y hx hy hxy
    exact (hW.boundary hx hy hxy).1

theorem isChain_regionsFrom_bagPositions {W : ℕ → Finset V} (hW : IsBagSequence (G := G) W)
    (j : ℕ) : (regionsFrom G univ (bagPositions W j)).IsChain fun A B => B ⊆ A := by
  induction j with
  | zero =>
    simp only [bagPositions, regionsFrom]
    exact List.IsChain.cons_cons (subset_univ _) (List.isChain_singleton _)
  | succ j ih =>
    simp only [bagPositions]
    rw [isChain_regionsFrom_append, foldl_bagPositions hW]
    refine ⟨ih, ?_⟩
    have h1 := foldl_bagPositions hW (j + 1)
    simp only [bagPositions, List.foldl_append, List.foldl_cons, List.foldl_nil,
      foldl_bagPositions hW j] at h1
    simp only [regionsFrom]
    have h0 : nextRegion G (W j ∩ W (j + 1)) (univ \ bagsUpTo W j) = univ \ bagsUpTo W j :=
      nextRegion_compl subset_rfl (by simp) ((inter_subset_left).trans (subset_bagsUpTo W j))
        (fun x y hx hy hxy => mem_inter.mpr (hW.boundary hx hy hxy))
    rw [h0] at h1 ⊢
    rw [h1]
    refine List.IsChain.cons_cons subset_rfl (List.IsChain.cons_cons ?_ (List.isChain_singleton _))
    exact sdiff_subset_sdiff subset_rfl (bagsUpTo_mono W j)

theorem getLast?_bagPositions (W : ℕ → Finset V) (j : ℕ) :
    (bagPositions W j).getLast? = some (W j) := by
  cases j <;> simp [bagPositions]

theorem isChain_bagPositions (W : ℕ → Finset V) (j : ℕ) :
    ((∅ : Finset V) :: bagPositions W j).IsChain fun A B => B ⊆ A ∨ A ⊆ B := by
  induction j with
  | zero =>
    simp only [bagPositions]
    exact List.IsChain.cons_cons (Or.inr (empty_subset _)) (List.isChain_singleton _)
  | succ j ih =>
    simp only [bagPositions]
    rw [← List.cons_append]
    refine List.IsChain.append ih
      (List.IsChain.cons_cons (Or.inr inter_subset_right) (List.isChain_singleton _)) ?_
    intro x hx y hy
    have hx' : x = W j := by
      cases j with
      | zero => simpa [bagPositions] using hx.symm
      | succ j =>
        rw [List.getLast?_cons, getLast?_bagPositions] at hx
        simpa using hx.symm
    simp only [List.head?_cons, Option.mem_def, Option.some.injEq] at hy
    rw [hx', ← hy]
    exact Or.inl inter_subset_left

theorem card_le_of_mem_bagPositions {W : ℕ → Finset V} {k : ℕ} (hk : ∀ i, (W i).card ≤ k)
    (j : ℕ) : ∀ Y ∈ bagPositions W j, Y.card ≤ k := by
  induction j with
  | zero =>
    intro Y hY
    simp only [bagPositions, List.mem_singleton] at hY
    rw [hY]
    exact hk 0
  | succ j ih =>
    intro Y hY
    simp only [bagPositions, List.mem_append, List.mem_cons, List.not_mem_nil,
      or_false] at hY
    rcases hY with hY | rfl | rfl
    · exact ih Y hY
    · exact (card_le_card inter_subset_left).trans (hk j)
    · exact hk (j + 1)

/-- The search built from bags whose union is everything is monotone and
successful. -/
theorem isMonotoneVertexSearch_bagPositions {W : ℕ → Finset V} (hW : IsBagSequence (G := G) W)
    {L : ℕ} (hcov : bagsUpTo W L = univ) :
    IsMonotoneVertexSearch G (∅ :: bagPositions W L) := by
  refine ⟨⟨⟨rfl, isChain_bagPositions W L⟩, ?_⟩, ?_⟩
  · unfold regionSeq
    rw [List.tail_cons, regionsFrom_getLast?, foldl_bagPositions hW, hcov, sdiff_self]
    rfl
  · exact isChain_regionsFrom_bagPositions hW L

variable (G)

/-- The bags of a path decomposition, indexed by `ℕ` (constant after the last). -/
def _root_.MOSPFormalization.PathDecomposition.natBag (P : PathDecomposition G) (i : ℕ) : Finset V :=
  P.bag ⟨min i P.length, by omega⟩

theorem _root_.MOSPFormalization.PathDecomposition.isBagSequence_natBag (P : PathDecomposition G) :
    IsBagSequence (G := G) P.natBag where
  edge u v huv := by
    obtain ⟨i, hu, hv⟩ := P.edge_coverage u v huv
    refine ⟨i.val, ?_, ?_⟩ <;>
    · unfold PathDecomposition.natBag
      have : (⟨min i.val P.length, by omega⟩ : Fin (P.length + 1)) = i := by
        ext
        simp only
        omega
      rwa [this]
  interval v i j k hij hjk hi hk := by
    unfold PathDecomposition.natBag at *
    refine P.interval v _ _ _ ?_ ?_ hi hk
    · exact Fin.mk_le_mk.mpr (min_le_min_right _ hij)
    · exact Fin.mk_le_mk.mpr (min_le_min_right _ hjk)

theorem _root_.MOSPFormalization.PathDecomposition.bagsUpTo_natBag (P : PathDecomposition G) :
    bagsUpTo P.natBag P.length = univ := by
  apply eq_univ_of_forall
  intro v
  obtain ⟨i, hi⟩ := P.vertex_coverage v
  refine mem_bagsUpTo.mpr ⟨i.val, by omega, ?_⟩
  unfold PathDecomposition.natBag
  have : (⟨min i.val P.length, by omega⟩ : Fin (P.length + 1)) = i := by
    ext
    simp only
    omega
  rw [this]
  exact hi

/-- **[BRST] (iii) ⇒ (iv)**: a path decomposition with bags of size at most `n`
gives a monotone successful search with each `|X_i| ≤ n`, namely
`(∅, W_0, W_0 ∩ W_1, W_1, …, W_L)`. -/
theorem _root_.MOSPFormalization.PathDecomposition.isMonotoneVertexSearch (P : PathDecomposition G) :
    IsMonotoneVertexSearch G (∅ :: bagPositions P.natBag P.length) ∧
      ∀ Y ∈ (∅ :: bagPositions P.natBag P.length), Y.card ≤ P.width + 1 := by
  refine ⟨isMonotoneVertexSearch_bagPositions P.isBagSequence_natBag P.bagsUpTo_natBag, ?_⟩
  intro Y hY
  rw [List.mem_cons] at hY
  rcases hY with rfl | hY
  · simp
  · exact card_le_of_mem_bagPositions (fun i => P.bag_card_le_width_add_one _) _ Y hY

end Upper

/-! ### The theorem -/

section Main

theorem exists_monotoneVertexSearch_pathwidth :
    ∃ X, IsMonotoneVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ pathwidth G + 1 := by
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq G
  obtain ⟨h1, h2⟩ := P.isMonotoneVertexSearch
  exact ⟨_, h1, hP ▸ h2⟩

theorem monotoneVertexSearchNumber_le_pathwidth_add_one :
    monotoneVertexSearchNumber G ≤ pathwidth G + 1 :=
  Nat.sInf_le (exists_monotoneVertexSearch_pathwidth G)

/-- Monotone searches are searches. -/
theorem vertexSearchNumber_le_monotoneVertexSearchNumber :
    vertexSearchNumber G ≤ monotoneVertexSearchNumber G := by
  obtain ⟨X, hX, hn⟩ := Nat.sInf_mem (s := {n | ∃ X, IsMonotoneVertexSearch G X ∧
    ∀ Y ∈ X, Y.card ≤ n}) ⟨_, exists_monotoneVertexSearch_pathwidth G⟩
  exact Nat.sInf_le ⟨X, hX.1, hn⟩

/-- An optimal successful search exists. -/
theorem exists_vertexSearch_optimal :
    ∃ X, IsSuccessfulVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ vertexSearchNumber G := by
  obtain ⟨X, hX, hn⟩ := exists_monotoneVertexSearch_pathwidth G
  exact Nat.sInf_mem (s := {n | ∃ X, IsSuccessfulVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ n})
    ⟨_, X, hX.1, hn⟩

/-- **A vertex search is a node search**: `ns(G) ≤` the vertex search number,
on every graph. -/
theorem nodeSearch_le_vertexSearchNumber : nodeSearch G ≤ vertexSearchNumber G := by
  obtain ⟨X, hX, hn⟩ := exists_vertexSearch_optimal G
  exact Nat.sInf_le ⟨_, isNodeSearch_of_isSuccessfulVertexSearch G hX hn⟩

theorem foldl_nextRegion_of_forall_empty (Ys : List (Finset V)) (h : ∀ Y ∈ Ys, Y = ∅) :
    Ys.foldl (fun B Y => nextRegion G Y B) univ = univ := by
  induction Ys with
  | nil => rfl
  | cons Y Ys ih =>
    rw [List.foldl_cons, h Y (by simp), nextRegion_empty_univ]
    exact ih fun Z hZ => h Z (List.mem_cons_of_mem Y hZ)

/-- With a vertex, no search without searchers succeeds. -/
theorem one_le_vertexSearchNumber [Nonempty V] : 1 ≤ vertexSearchNumber G := by
  by_contra hlt
  obtain ⟨X, ⟨-, hlast⟩, hn⟩ := exists_vertexSearch_optimal G
  have h0 : ∀ Y ∈ X.tail, Y = ∅ := fun Y hY =>
    card_eq_zero.mp (Nat.le_zero.mp ((hn Y (List.mem_of_mem_tail hY)).trans (by omega)))
  unfold regionSeq at hlast
  rw [regionsFrom_getLast?, foldl_nextRegion_of_forall_empty G _ h0, Option.some_inj] at hlast
  obtain ⟨v⟩ := ‹Nonempty V›
  exact notMem_empty v (hlast ▸ mem_univ v)

/-- An edgeless graph has pathwidth `0`. -/
theorem pathwidth_of_edgeless (h : ∀ u v, ¬ G.Adj u v) : pathwidth G = 0 := by
  apply Nat.eq_zero_of_le_zero
  refine (pathwidth_le_vertexSeparation G).trans
    ((vertexSeparation_le_vertexSepOfLayout G (Fintype.equivFin V)).trans ?_)
  unfold vertexSepOfLayout
  split_ifs
  · exact le_rfl
  · refine Finset.sup'_le _ _ fun i _ => ?_
    simp [vertexSepAt, activeSuffix, h]

/-- **[BRST] (i) ⇒ (iii)**: `pw(G) + 1 ≤` the vertex search number, for every
graph with a vertex. With an edge, through the node search game
(`isNodeSearch_of_isSuccessfulVertexSearch` and `ns = pw + 1`,
`NodeMonotonicity.lean`); edgeless, because `pw = 0` and a vertex needs a
searcher. -/
theorem pathwidth_add_one_le_vertexSearchNumber [Nonempty V] :
    pathwidth G + 1 ≤ vertexSearchNumber G := by
  by_cases h : ∃ u v, G.Adj u v
  · obtain ⟨u, v, huv⟩ := h
    rw [← nodeSearch_eq_pathwidth_add_one G huv]
    exact nodeSearch_le_vertexSearchNumber G
  · push Not at h
    rw [pathwidth_of_edgeless G h]
    exact one_le_vertexSearchNumber G

/-- **Bienstock, Robertson, Seymour & Thomas (1991), (5.1), (i) ⇔ (iii)**: the
vertex search number is `pw(G) + 1` on every finite graph with a vertex,
edgeless graphs included. -/
theorem vertexSearchNumber_eq_pathwidth_add_one [Nonempty V] :
    vertexSearchNumber G = pathwidth G + 1 :=
  le_antisymm ((vertexSearchNumber_le_monotoneVertexSearchNumber G).trans
    (monotoneVertexSearchNumber_le_pathwidth_add_one G))
    (pathwidth_add_one_le_vertexSearchNumber G)

/-- **[BRST] (5.1), (iv) ⇔ (iii)**: the monotone vertex search number is
`pw(G) + 1` as well. -/
theorem monotoneVertexSearchNumber_eq_pathwidth_add_one [Nonempty V] :
    monotoneVertexSearchNumber G = pathwidth G + 1 :=
  le_antisymm (monotoneVertexSearchNumber_le_pathwidth_add_one G)
    ((pathwidth_add_one_le_vertexSearchNumber G).trans
      (vertexSearchNumber_le_monotoneVertexSearchNumber G))

/-- Recontamination does not help the vertex search. -/
theorem vertexSearchNumber_eq_monotoneVertexSearchNumber [Nonempty V] :
    vertexSearchNumber G = monotoneVertexSearchNumber G := by
  rw [vertexSearchNumber_eq_pathwidth_add_one, monotoneVertexSearchNumber_eq_pathwidth_add_one]

/-- **[BRST] (5.1) as stated**, for each `n`, (i) ⇔ (iii) ⇔ (iv): a successful
search with each `|X_i| ≤ n` exists iff `pw(G) ≤ n − 1` (read `pw(G) + 1 ≤ n`,
which is the same for `n ≥ 1`; with `n = 0` neither side holds when `V` is
nonempty) iff a monotone one exists. -/
theorem vertexSearch_iff [Nonempty V] (n : ℕ) :
    ((∃ X, IsSuccessfulVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ n) ↔ pathwidth G + 1 ≤ n) ∧
      ((∃ X, IsMonotoneVertexSearch G X ∧ ∀ Y ∈ X, Y.card ≤ n) ↔ pathwidth G + 1 ≤ n) := by
  obtain ⟨X₀, hX₀, hn₀⟩ := exists_monotoneVertexSearch_pathwidth G
  refine ⟨⟨fun h => ?_, fun h => ⟨X₀, hX₀.1, fun Y hY => (hn₀ Y hY).trans h⟩⟩,
    ⟨fun h => ?_, fun h => ⟨X₀, hX₀, fun Y hY => (hn₀ Y hY).trans h⟩⟩⟩
  · rw [← vertexSearchNumber_eq_pathwidth_add_one]
    exact Nat.sInf_le h
  · rw [← monotoneVertexSearchNumber_eq_pathwidth_add_one]
    exact Nat.sInf_le h

/-- With an edge, the vertex search number is the node search number of
Kirousis & Papadimitriou (both are `pw + 1`). -/
theorem vertexSearchNumber_eq_nodeSearch {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    vertexSearchNumber G = nodeSearch G := by
  have : Nonempty V := ⟨u₀⟩
  rw [vertexSearchNumber_eq_pathwidth_add_one, nodeSearch_eq_pathwidth_add_one G h₀]

/-- Edgeless graphs, where the two games part: one searcher visiting each
vertex in turn is needed and enough for the vertex search, while the node
search needs none. -/
theorem vertexSearchNumber_of_edgeless [Nonempty V] (h : ∀ u v, ¬ G.Adj u v) :
    vertexSearchNumber G = 1 ∧ nodeSearch G = 0 := by
  rw [vertexSearchNumber_eq_pathwidth_add_one, pathwidth_of_edgeless G h]
  exact ⟨rfl, nodeSearch_of_edgeless G h⟩

/-- With no vertices, the one-position search `(∅)` is successful (`B_1 = V(G) = ∅`):
both numbers are `0`, while `pw + 1 = 1`. -/
theorem vertexSearchNumber_of_isEmpty [IsEmpty V] :
    vertexSearchNumber G = 0 ∧ monotoneVertexSearchNumber G = 0 := by
  have hX : IsMonotoneVertexSearch G [∅] := by
    refine ⟨⟨⟨rfl, List.isChain_singleton _⟩, ?_⟩, ?_⟩
    · simp [regionSeq, regionsFrom, Finset.univ_eq_empty]
    · simp [regionSeq, regionsFrom]
  have hc : ∀ Y ∈ ([∅] : List (Finset V)), Y.card ≤ 0 := by simp
  exact ⟨Nat.eq_zero_of_le_zero (Nat.sInf_le ⟨_, hX.1, hc⟩),
    Nat.eq_zero_of_le_zero (Nat.sInf_le ⟨_, hX, hc⟩)⟩

theorem pathwidth_add_one_of_isEmpty [IsEmpty V] : pathwidth G + 1 = 1 := by
  have := pathwidth_le_card_sub_one G
  rw [Fintype.card_eq_zero] at this
  omega

end Main

end Complex

end MOSPFormalization
