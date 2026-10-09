/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Edge search, progressive: `vs ≤ s ≤ vs + 2`

Table 1 of Linhares & Yanasse (2002), row "edge search game", source [10]
Kirousis & Papadimitriou (1986), *Searching and pebbling*, Theoretical Computer
Science 47, 205–218, §2 p. 208 (the game of Parsons 1976 and Megiddo et al.).
The relation to vertex separation is Ellis, Sudborough & Turner (1994), *The
vertex separation and search number of a graph*, Information and Computation
113, 50–79, Theorem 2.1 (p. 54): `vs(G) ≤ s(G) ≤ vs(G) + 2`, from Lemma 2.1
(`vs ≤ s`, p. 55) and Lemma 2.2 (`s ≤ vs + 2`, p. 56, the procedure
`search1`).

## The source's definition

EST p. 53: "A search step is one of the following operations: (a) the placing
of a searcher on a vertex, (b) the movement of a searcher along an edge, (c)
the removal of a searcher from a vertex. A search sequence is a sequence of
search steps. Initially, all the edges of the graph are contaminated. We say
that an edge `e = {x, y}` becomes clear if either there is a searcher on `x`
and a second searcher is moved from `x` to `y` or there is a searcher on `x`,
all edges incident to `x` except `e` are clear, and the searcher on `x` is
moved along `e` to `y`. A clear edge `e` could become contaminated again by the
movement or deletion of a searcher which results in a path without searchers
from a contaminated edge to `e`. A search strategy for a graph is a search
sequence that results in all edges being simultaneously clear. The search
number of a graph is the minimum number of searchers for which a search
strategy exists." A strategy that recontaminates no edge is *progressive*
(p. 53). The same game is [10] §2, p. 208.

Formalised as the game itself:

* `EdgeState` — how many searchers stand on each vertex (several may share a
  vertex: `search1` places a second searcher on a guarded vertex), and the
  contaminated edges;
* `EdgeMove` — `place v`, `remove v`, `slide u v`;
* `edgeStep` — the counts change; a slide from a guarded `u` along an edge
  `uv` clears `uv`; then every edge joined to a still-contaminated edge by a
  searcher-free path is contaminated (`recontaminate`, shared with
  `NodeSearch.lean`). The source's two clearing cases are one rule here: if
  `u` keeps a searcher, nothing can reach `uv` through `u`; if `u` is left
  empty with another contaminated edge, the gas comes straight back, so the
  slide clears `uv` exactly when the source says it does. This is the
  semantics of `paper1/complex_check.py`'s `edge_search`;
* `edgeCost` — the largest total number of searchers over the run;
  `Progressive` — no move enlarges the contaminated set;
* `edgeSearch` / `progressiveEdgeSearch` — the least cost of a (progressive)
  strategy clearing every edge.

A move the source does not allow (removing from an empty vertex, sliding from
an empty vertex or along a non-edge) changes no count and clears nothing.

Nothing in these definitions mentions layouts or separation.

## What is proved

* `progressiveEdgeSearch_le_vertexSeparation_add_two` — **EST Lemma 2.2**,
  by `search1`: for a layout, place the next vertex `x`; for each earlier
  neighbour `y`, add a searcher on `y` and slide it to `x`, then remove a
  searcher from `x`; then remove the searchers of vertices with no neighbour
  still to come (`edgeStrategy`). The layout is Kornai & Tuza's in-sequence
  of item 04: between phases the searchers sit one each on the shack minus the
  vertex about to enter, and a phase adds at most two, so the cost is
  `ν(σ) + 1` and `ν(σ) = vs(σ reversed) + 1`. The strategy is progressive,
  which the proof shows by keeping the cleared set closed: every unguarded
  vertex touching a cleared edge has all its edges cleared (`SafeClear`).
* `vertexSeparation_le_of_progressive` — **EST Lemma 2.1 for progressive
  strategies**. Not EST's argument, which orders vertices by the time they
  first receive a searcher and needs "irredundant" strategies first. As for
  node search (`NodeSearch.lean`), vertices are ordered by the time `τ(v)`
  from which no contaminated edge touches them, ties broken by putting a
  vertex that is unguarded at that time first. A later vertex with an earlier
  neighbour is guarded at `τ(v)`: otherwise the gas would spread back onto
  the clear edge to that neighbour; and at most one unguarded vertex becomes
  clear per step, because a step clears at most the one edge it slides along
  and the searcher arrives at its far end (`clear_step_unique`).
* Hence **EST Theorem 2.1 for the progressive game**:
  `vertexSeparation_le_progressiveEdgeSearch`,
  `progressiveEdgeSearch_le_vertexSeparation_add_two`, and the pathwidth forms.
  No hypothesis: both hold on every finite graph, the edgeless and empty ones
  included (there `s = vs = 0`).
* `edgeSearch_le_vertexSeparation_add_two` — the half of Theorem 2.1 that
  needs no monotonicity.
* With node search (item 10, `mns = vs + 1` on a graph with an edge): [10]
  p. 209's `ns − 1 ≤ es ≤ ns + 1` for the two monotone games
  (`monotoneNodeSearch_sub_one_le_progressiveEdgeSearch`,
  `progressiveEdgeSearch_le_monotoneNodeSearch_add_one`).
* Edge cases: `progressiveEdgeSearch_of_edgeless`, `edgeSearch_of_edgeless`
  (`= 0`, the empty strategy).

## Not proved: the full game

LaPaugh (1993), recontamination does not help, is stated as the proposition
`EdgeSearchMonotonicity` (`edgeSearch = progressiveEdgeSearch`) and not
asserted; `vertexSeparation_le_edgeSearch_of_monotonicity` derives the
missing half of Theorem 2.1 from it. No `sorry` stands for it. That all three
values `vs, vs + 1, vs + 2` occur (`K₂` has `s = vs = 1`; `K₃,₃` has
`s = 5 = vs + 2`, EST p. 57) is checked by `paper1/complex_check.py`, not
here.
-/

import MOSPFormalization.Complex.NodeSearch

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### The game (Parsons; [10] §2; EST p. 53) -/

/-- A search step: place a searcher, remove one, or move one along an edge. -/
inductive EdgeMove (V : Type*)
  | place (v : V)
  | remove (v : V)
  | slide (u v : V)

/-- A position: the number of searchers on each vertex and the contaminated
edges. -/
structure EdgeState (V : Type*) where
  count : V → ℕ
  contaminated : Set (Sym2 V)

/-- The vertices carrying at least one searcher. -/
def supp (c : V → ℕ) : Finset V := Finset.univ.filter fun v => c v ≠ 0

theorem mem_supp {c : V → ℕ} {v : V} : v ∈ supp c ↔ c v ≠ 0 := by
  unfold supp
  exact ⟨fun h => (Finset.mem_filter.mp h).2, fun h => Finset.mem_filter.mpr ⟨Finset.mem_univ _, h⟩⟩

/-- The guarded vertices of a position. -/
def EdgeState.guards (s : EdgeState V) : Finset V := supp s.count

/-- The counts after a move. -/
def edgeCount : EdgeMove V → (V → ℕ) → V → ℕ
  | .place v, c => fun w => if w = v then c w + 1 else c w
  | .remove v, c => fun w => if w = v then c w - 1 else c w
  | .slide u v, c =>
    if G.Adj u v ∧ c u ≠ 0 then fun w => if w = v then c w + 1 else if w = u then c w - 1 else c w
    else c

/-- The edge a move clears: the edge a searcher slides along. -/
def clearedBy : EdgeMove V → (V → ℕ) → Set (Sym2 V)
  | .slide u v, c => if G.Adj u v ∧ c u ≠ 0 then {s(u, v)} else ∅
  | .place _, _ => ∅
  | .remove _, _ => ∅

/-- One move: change the counts, clear the edge slid along, then let the gas
spread through searcher-free paths. -/
def edgeStep (s : EdgeState V) (m : EdgeMove V) : EdgeState V :=
  let c' := edgeCount G m s.count
  let D := s.contaminated \ clearedBy G m s.count
  ⟨c', D ∪ recontaminate G (supp c') D⟩

/-- The start: no searcher, every edge contaminated. -/
def edgeInit : EdgeState V := ⟨fun _ => 0, G.edgeSet⟩

/-- The position after a sequence of moves. -/
def edgeRun (s : EdgeState V) (ms : List (EdgeMove V)) : EdgeState V :=
  ms.foldl (edgeStep G) s

/-- The largest total number of searchers over the positions of a run. -/
def edgeCost : EdgeState V → List (EdgeMove V) → ℕ
  | s, [] => ∑ v, s.count v
  | s, m :: ms => max (∑ v, s.count v) (edgeCost (edgeStep G s m) ms)

/-- No move of the run recontaminates an edge (EST p. 53: *progressive*). -/
def Progressive : EdgeState V → List (EdgeMove V) → Prop
  | _, [] => True
  | s, m :: ms => (edgeStep G s m).contaminated ⊆ s.contaminated ∧
      Progressive (edgeStep G s m) ms

/-- A search strategy with at most `k` searchers. -/
def IsEdgeSearch (k : ℕ) (ms : List (EdgeMove V)) : Prop :=
  (edgeRun G (edgeInit G) ms).contaminated = ∅ ∧ edgeCost G (edgeInit G) ms ≤ k

/-- A progressive search strategy with at most `k` searchers. -/
def IsProgressiveEdgeSearch (k : ℕ) (ms : List (EdgeMove V)) : Prop :=
  IsEdgeSearch G k ms ∧ Progressive G (edgeInit G) ms

/-- The search number `s(G)` (EST p. 53; `es(G)` in [10]). -/
noncomputable def edgeSearch : ℕ := sInf {k | ∃ ms, IsEdgeSearch G k ms}

/-- The least cost of a progressive strategy. -/
noncomputable def progressiveEdgeSearch : ℕ :=
  sInf {k | ∃ ms, IsProgressiveEdgeSearch G k ms}

/-- **LaPaugh (1993)**, stated and not asserted: recontamination does not
help. -/
def EdgeSearchMonotonicity : Prop := edgeSearch G = progressiveEdgeSearch G

/-! ### Basic facts -/

section Basic

variable {G}

/-- One searcher on each vertex of `S`. -/
def ind (S : Finset V) : V → ℕ := fun w => if w ∈ S then 1 else 0

theorem supp_ind (S : Finset V) : supp (ind S) = S := by
  ext w
  by_cases h : w ∈ S <;> simp [supp, ind, h]

theorem sum_ind (S : Finset V) : ∑ w, ind S w = S.card := by
  simp only [ind, Finset.sum_boole, Nat.cast_id]
  congr 1
  ext w
  simp

theorem supp_add_at {S : Finset V} {u : V} (hu : u ∈ S) :
    supp (fun w => if w = u then ind S w + 1 else ind S w) = S := by
  ext w
  rw [mem_supp]
  by_cases hw : w = u
  · subst hw
    simp [ind, hu]
  · by_cases hwS : w ∈ S <;> simp [ind, hw, hwS]

theorem card_supp_le_sum (c : V → ℕ) : (supp c).card ≤ ∑ v, c v := by
  calc (supp c).card = ∑ v ∈ supp c, 1 := Finset.card_eq_sum_ones _
    _ ≤ ∑ v ∈ supp c, c v := Finset.sum_le_sum fun v hv =>
        Nat.one_le_iff_ne_zero.mpr (Finset.mem_filter.mp hv).2
    _ ≤ ∑ v, c v := Finset.sum_le_sum_of_subset (Finset.subset_univ _)

theorem sum_add_at (c : V → ℕ) (u : V) :
    ∑ w, (if w = u then c w + 1 else c w) = (∑ w, c w) + 1 := by
  have h : ∀ w, (if w = u then c w + 1 else c w) = c w + if w = u then 1 else 0 := by
    intro w
    split_ifs <;> rfl
  simp [h, Finset.sum_add_distrib]

/-- Every contaminated edge after a step either was contaminated and not
cleared, or was reached by the gas. -/
theorem sdiff_subset_step (s : EdgeState V) (m : EdgeMove V) :
    s.contaminated \ clearedBy G m s.count ⊆ (edgeStep G s m).contaminated :=
  Set.subset_union_left

theorem mem_clearedBy {m : EdgeMove V} {c : V → ℕ} {e : Sym2 V} (he : e ∈ clearedBy G m c) :
    ∃ a b, m = .slide a b ∧ G.Adj a b ∧ c a ≠ 0 ∧ e = s(a, b) := by
  cases m with
  | place v => simp [clearedBy] at he
  | remove v => simp [clearedBy] at he
  | slide a b =>
    simp only [clearedBy] at he
    split_ifs at he with h
    · exact ⟨a, b, rfl, h.1, h.2, he⟩
    · simp at he

theorem mem_supp_slide {c : V → ℕ} {a b : V} (h : G.Adj a b ∧ c a ≠ 0) :
    b ∈ supp (edgeCount G (.slide a b) c) := by
  simp [supp, edgeCount, h]

/-- The contaminated set after a step is closed under spreading. -/
theorem isClosed_edgeStep (s : EdgeState V) (m : EdgeMove V) :
    IsClosed (G := G) (⟨(edgeStep G s m).guards, (edgeStep G s m).contaminated⟩ :
      SearchState V) := by
  intro e he f hf x hx y hy hxS hxy
  simp only [edgeStep, EdgeState.guards] at hf hxS hxy ⊢
  rcases hf with hf | ⟨hfE, f₀, hf₀, x', hx', y', hy', hx'S, hx'y'⟩
  · exact Or.inr ⟨he, f, hf, x, hx, y, hy, hxS, hxy⟩
  · refine Or.inr ⟨he, f₀, hf₀, x, hx, y', hy', hxS, ?_⟩
    have hyS := freeReach_not_mem hxy hxS
    rcases eq_or_adj_of_mem_edgeSet hfE hy hx' with rfl | hadj
    · exact hxy.trans hx'y'
    · exact (hxy.tail ⟨hadj, hyS, hx'S⟩).trans hx'y'

/-- At most one unguarded vertex stops touching contaminated edges in one
step: a step clears at most the edge it slides along, and the searcher ends
on the far end of it. -/
theorem clear_step_unique {s : EdgeState V} {m : EdgeMove V} {x y : V} (hxy : x ≠ y)
    {e f : Sym2 V} (he : e ∈ s.contaminated) (hxe : x ∈ e)
    (he' : e ∉ (edgeStep G s m).contaminated) (hf : f ∈ s.contaminated) (hyf : y ∈ f)
    (hf' : f ∉ (edgeStep G s m).contaminated) (hxS : x ∉ (edgeStep G s m).guards)
    (hyS : y ∉ (edgeStep G s m).guards) : False := by
  have hce : e ∈ clearedBy G m s.count := by
    by_contra h
    exact he' (sdiff_subset_step s m ⟨he, h⟩)
  have hcf : f ∈ clearedBy G m s.count := by
    by_contra h
    exact hf' (sdiff_subset_step s m ⟨hf, h⟩)
  obtain ⟨a, b, rfl, hab, ha, rfl⟩ := mem_clearedBy hce
  simp only [clearedBy, hab, ha, ne_eq, not_false_eq_true, and_self, ite_true,
    Set.mem_singleton_iff] at hcf
  subst hcf
  have hb : b ∈ (edgeStep G s (.slide a b)).guards := mem_supp_slide ⟨hab, ha⟩
  rw [Sym2.mem_iff] at hxe hyf
  rcases hxe with rfl | rfl
  · rcases hyf with rfl | rfl
    · exact hxy rfl
    · exact hyS hb
  · exact hxS hb

/-! ### Runs -/

theorem edgeRun_append (s : EdgeState V) (ms ms' : List (EdgeMove V)) :
    edgeRun G s (ms ++ ms') = edgeRun G (edgeRun G s ms) ms' :=
  List.foldl_append

theorem sum_le_edgeCost (s : EdgeState V) (ms : List (EdgeMove V)) :
    ∑ v, s.count v ≤ edgeCost G s ms := by
  cases ms with
  | nil => exact le_rfl
  | cons m ms => exact le_max_left _ _

theorem edgeCost_append (s : EdgeState V) (ms ms' : List (EdgeMove V)) :
    edgeCost G s (ms ++ ms') = max (edgeCost G s ms) (edgeCost G (edgeRun G s ms) ms') := by
  induction ms generalizing s with
  | nil => exact (max_eq_right (sum_le_edgeCost s ms')).symm
  | cons m ms ih =>
    simp only [List.cons_append, edgeCost, ih]
    rw [max_assoc]
    rfl

theorem progressive_append (s : EdgeState V) (ms ms' : List (EdgeMove V)) :
    Progressive G s (ms ++ ms') ↔
      Progressive G s ms ∧ Progressive G (edgeRun G s ms) ms' := by
  induction ms generalizing s with
  | nil => simp [Progressive, edgeRun]
  | cons m ms ih =>
    simp only [List.cons_append, Progressive, ih]
    exact ⟨fun h => ⟨⟨h.1, h.2.1⟩, h.2.2⟩, fun h => ⟨h.1.1, h.1.2, h.2⟩⟩

theorem edgeRun_take_succ (s : EdgeState V) (ms : List (EdgeMove V)) {t : ℕ}
    (ht : t < ms.length) :
    edgeRun G s (ms.take (t + 1)) = edgeStep G (edgeRun G s (ms.take t)) ms[t] := by
  rw [List.take_add_one, List.getElem?_eq_getElem ht, edgeRun_append]
  rfl

theorem sum_le_edgeCost_take (s : EdgeState V) (ms : List (EdgeMove V)) (t : ℕ) :
    ∑ v, (edgeRun G s (ms.take t)).count v ≤ edgeCost G s ms := by
  induction ms generalizing s t with
  | nil => simpa [edgeRun] using sum_le_edgeCost s []
  | cons m ms ih =>
    cases t with
    | zero => exact sum_le_edgeCost s _
    | succ t => exact (ih (edgeStep G s m) t).trans (le_max_right _ _)

theorem progressive_take {s : EdgeState V} {ms : List (EdgeMove V)}
    (h : Progressive G s ms) {t : ℕ} (ht : t < ms.length) :
    (edgeRun G s (ms.take (t + 1))).contaminated ⊆ (edgeRun G s (ms.take t)).contaminated := by
  induction ms generalizing s t with
  | nil => simp at ht
  | cons m ms ih =>
    cases t with
    | zero => exact h.1
    | succ t => exact ih h.2 (by simpa using ht)

/-! ### Closed cleared sets -/

variable (G) in
/-- The cleared set `K` is safe for the guards `S`: an unguarded vertex
touching a cleared edge has all its edges cleared. -/
def SafeClear (S : Finset V) (K : Set (Sym2 V)) : Prop :=
  ∀ x ∉ S, ∀ e ∈ K, x ∈ e → ∀ f ∈ G.edgeSet, x ∈ f → f ∈ K

/-- The gas cannot reach a safe cleared set. -/
theorem not_mem_of_mem_recontaminate {S : Finset V} {K D : Set (Sym2 V)}
    (hsafe : SafeClear G S K) (hD : D ⊆ G.edgeSet) (hDK : ∀ f ∈ D, f ∉ K) {e : Sym2 V}
    (he : e ∈ recontaminate G S D) : e ∉ K := by
  intro heK
  obtain ⟨-, f, hf, x, hx, y, hy, hxS, hxy⟩ := he
  have key : ∀ z, FreeReach G S x z → ∀ f' ∈ G.edgeSet, z ∈ f' → f' ∈ K := by
    intro z hz
    induction hz with
    | refl => exact hsafe x hxS e heK hx
    | @tail b c _ hbc ih =>
      have hbcK := ih _ (G.mem_edgeSet.mpr hbc.1) (Sym2.mem_mk_left _ _)
      exact hsafe c hbc.2.2 _ hbcK (Sym2.mem_mk_right _ _)
  exact hDK f hf (key y hxy f (hD hf) hy)

/-- A step into a safe cleared set: the contaminated edges are exactly the
uncleared ones, and nothing was recontaminated. -/
theorem edgeStep_of_safe {s : EdgeState V} {m : EdgeMove V} {K : Set (Sym2 V)}
    (hK : s.contaminated = G.edgeSet \ K)
    (hsafe : SafeClear G (supp (edgeCount G m s.count)) (K ∪ clearedBy G m s.count)) :
    (edgeStep G s m).contaminated = G.edgeSet \ (K ∪ clearedBy G m s.count) ∧
      (edgeStep G s m).contaminated ⊆ s.contaminated := by
  have hD : s.contaminated \ clearedBy G m s.count = G.edgeSet \ (K ∪ clearedBy G m s.count) := by
    rw [hK, Set.sdiff_sdiff]
  have heq : (edgeStep G s m).contaminated = G.edgeSet \ (K ∪ clearedBy G m s.count) := by
    apply Set.Subset.antisymm
    · rintro e (he | he)
      · rwa [← hD]
      · rw [hD] at he
        exact ⟨he.1, not_mem_of_mem_recontaminate hsafe Set.sdiff_subset
          (fun f hf => hf.2) he⟩
    · rw [← hD]
      exact sdiff_subset_step s m
  refine ⟨heq, ?_⟩
  rw [heq, hK]
  exact Set.sdiff_subset_sdiff_right Set.subset_union_left

end Basic

/-! ### `search1` is a progressive strategy (EST Lemma 2.2) -/

section Upper

/-- The edges with both endpoints before position `i`. -/
def clearedBefore (σ : LinearLayout V) (i : ℕ) : Set (Sym2 V) := {e | ∀ x ∈ e, (σ x).val < i}

/-- The edges from `v` to the vertices of a list. -/
def star (v : V) (l : List V) : Set (Sym2 V) := {e | ∃ u ∈ l, e = s(u, v)}

@[simp] theorem star_nil (v : V) : star v [] = ∅ := by simp [star]

theorem star_append_singleton (v u : V) (l : List V) :
    star v (l ++ [u]) = star v l ∪ {s(u, v)} := by
  ext e
  simp only [star, List.mem_append, List.mem_singleton, Set.mem_union, Set.mem_ofPred_eq,
    Set.mem_singleton_iff]
  constructor
  · rintro ⟨w, hw | rfl, rfl⟩
    · exact Or.inl ⟨w, hw, rfl⟩
    · exact Or.inr rfl
  · rintro (⟨w, hw, rfl⟩ | rfl)
    · exact ⟨w, Or.inl hw, rfl⟩
    · exact ⟨u, Or.inr rfl, rfl⟩

/-- The earlier neighbours of `v` before position `i`. -/
noncomputable def leftNbrs (σ : LinearLayout V) (i : ℕ) (v : V) : List V :=
  (Finset.univ.filter fun u => (σ u).val < i ∧ G.Adj u v).toList

/-- Add a searcher on `u`, slide it to `v`, remove a searcher from `v`. -/
def slideMoves (v u : V) : List (EdgeMove V) := [.place u, .slide u v, .remove v]

/-- Phase `i` of `search1` (EST p. 56) on the vertex `x` at position `i`: place a
searcher on `x`; for each earlier neighbour `y`, add a searcher to `y`, move it
from `y` to `x`, remove a searcher from `x`; then remove the searchers of the
vertices with no neighbour after position `i` (`MovedAt`). -/
noncomputable def edgePhase (σ : LinearLayout V) (i : ℕ) : List (EdgeMove V) :=
  if h : i < Fintype.card V then
    .place (σ.symm ⟨i, h⟩) :: ((leftNbrs G σ i (σ.symm ⟨i, h⟩)).flatMap (slideMoves (σ.symm ⟨i, h⟩))
      ++ (Finset.univ.filter (MovedAt G σ i)).toList.map .remove)
  else []

/-- `search1` as a search strategy. -/
noncomputable def edgeStrategy (σ : LinearLayout V) : List (EdgeMove V) :=
  (List.range (Fintype.card V)).flatMap (edgePhase G σ)

theorem safe_clearedBefore (σ : LinearLayout V) (i : ℕ) {S : Finset V}
    (hS : shackGuards G σ i ⊆ S) : SafeClear G S (clearedBefore σ i) := by
  intro x hxS e he hxe f hf hxf z hz
  have hxi := he x hxe
  rcases eq_or_adj_of_mem_edgeSet hf hxf hz with rfl | hxz
  · exact hxi
  · by_contra hzi
    apply hxS
    apply hS
    simp only [shackGuards, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨hxi, z, hxz, by omega⟩

theorem shackGuards_subset_shackAfterPut (σ : LinearLayout V) {i : ℕ}
    (hi : i < Fintype.card V) : shackGuards G σ i ⊆ shackAfterPut G σ i := by
  rw [← insert_shackGuards G σ hi]
  exact Finset.subset_insert _ _

theorem safe_star (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V) {S : Finset V}
    (hS : shackAfterPut G σ i ⊆ S) (l : List V)
    (hl : ∀ u ∈ l, (σ u).val < i ∧ G.Adj u (σ.symm ⟨i, hi⟩)) :
    SafeClear G S (clearedBefore σ i ∪ star (σ.symm ⟨i, hi⟩) l) := by
  set v := σ.symm ⟨i, hi⟩ with hv
  have hσv : (σ v).val = i := by simp [hv]
  have hvS : v ∈ S := hS ((mem_shackAfterPut_iff G σ i v).mpr ⟨hσv.le, v, Or.inl rfl, hσv.ge⟩)
  intro x hxS e he hxe f hf hxf
  rcases he with he | ⟨u, hu, rfl⟩
  · exact Or.inl (safe_clearedBefore G σ i
      ((shackGuards_subset_shackAfterPut G σ hi).trans hS) x hxS e he hxe f hf hxf)
  · exfalso
    obtain ⟨hui, huv⟩ := hl u hu
    have huS : u ∈ S := hS ((mem_shackAfterPut_iff G σ i u).mpr
      ⟨hui.le, v, Or.inr huv, hσv.ge⟩)
    rw [Sym2.mem_iff] at hxe
    rcases hxe with rfl | rfl
    · exact hxS huS
    · exact hxS hvS

/-- One round `slideMoves`: from one searcher on each vertex of `S`, the
counts come back to one on each, the edge `uv` is cleared, and at most one
extra searcher is used. -/
theorem slideMoves_spec (S : Finset V) (K : Set (Sym2 V)) {u v : V} (hu : u ∈ S) (hv : v ∈ S)
    (huv : G.Adj u v) (s : EdgeState V) (hc : s.count = ind S)
    (hK : s.contaminated = G.edgeSet \ K) (h1 : SafeClear G S K)
    (h2 : SafeClear G S (K ∪ {s(u, v)})) :
    (edgeRun G s (slideMoves v u)).count = ind S ∧
      (edgeRun G s (slideMoves v u)).contaminated = G.edgeSet \ (K ∪ {s(u, v)}) ∧
      Progressive G s (slideMoves v u) ∧ edgeCost G s (slideMoves v u) ≤ S.card + 1 := by
  have hne : u ≠ v := huv.ne
  -- after `place u`
  set s₁ := edgeStep G s (.place u) with hs₁
  have hc₁ : s₁.count = fun w => if w = u then ind S w + 1 else ind S w := by
    simp only [hs₁, edgeStep, edgeCount, hc]
  have hS₁ : supp s₁.count = S := by
    rw [hc₁, supp_add_at hu]
  have hcl₁ : clearedBy G (.place u) s.count = ∅ := rfl
  obtain ⟨hK₁, hsub₁⟩ := edgeStep_of_safe (G := G) (m := .place u) hK
    (by rw [hcl₁, Set.union_empty]; exact hS₁ ▸ h1)
  rw [hcl₁, Set.union_empty] at hK₁
  -- after `slide u v`
  have hcond : G.Adj u v ∧ s₁.count u ≠ 0 := ⟨huv, by rw [hc₁]; simp⟩
  set s₂ := edgeStep G s₁ (.slide u v) with hs₂
  have hc₂ : s₂.count = fun w => if w = v then ind S w + 1 else ind S w := by
    simp only [hs₂, edgeStep, edgeCount, hcond, ne_eq, not_false_eq_true, and_self, ite_true]
    funext w
    rw [hc₁]
    by_cases hwv : w = v
    · subst hwv
      simp [hne.symm]
    · by_cases hwu : w = u
      · subst hwu
        simp [hwv]
      · simp [hwv, hwu]
  have hS₂ : supp s₂.count = S := by
    rw [hc₂, supp_add_at hv]
  have hcl₂ : clearedBy G (.slide u v) s₁.count = {s(u, v)} := by
    simp only [clearedBy, hcond, ne_eq, not_false_eq_true, and_self, ite_true]
  obtain ⟨hK₂, hsub₂⟩ := edgeStep_of_safe (G := G) (m := .slide u v) hK₁
    (by rw [hcl₂]; exact hS₂ ▸ h2)
  rw [hcl₂] at hK₂
  -- after `remove v`
  set s₃ := edgeStep G s₂ (.remove v) with hs₃
  have hc₃ : s₃.count = ind S := by
    simp only [hs₃, edgeStep, edgeCount]
    funext w
    rw [hc₂]
    by_cases hwv : w = v
    · subst hwv
      simp
    · simp [hwv]
  have hcl₃ : clearedBy G (.remove v) s₂.count = ∅ := rfl
  obtain ⟨hK₃, hsub₃⟩ := edgeStep_of_safe (G := G) (m := .remove v) hK₂
    (by
      rw [hcl₃, Set.union_empty]
      have : supp (edgeCount G (.remove v) s₂.count) = S := by
        change supp s₃.count = S
        rw [hc₃, supp_ind]
      exact this ▸ h2)
  rw [hcl₃, Set.union_empty] at hK₃
  have hsum₁ : ∑ w, s₁.count w = S.card + 1 := by rw [hc₁, sum_add_at, sum_ind]
  have hsum₂ : ∑ w, s₂.count w = S.card + 1 := by rw [hc₂, sum_add_at, sum_ind]
  refine ⟨hc₃, hK₃, ⟨hsub₁, hsub₂, hsub₃, trivial⟩, ?_⟩
  simp only [slideMoves, edgeCost]
  rw [← hs₁, ← hs₂, ← hs₃, hc, hsum₁, hsum₂, hc₃, sum_ind]
  omega

theorem slides_spec (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V) (l d : List V)
    (hl : ∀ u ∈ d ++ l, (σ u).val < i ∧ G.Adj u (σ.symm ⟨i, hi⟩)) (s : EdgeState V)
    (hc : s.count = ind (shackAfterPut G σ i))
    (hK : s.contaminated = G.edgeSet \ (clearedBefore σ i ∪ star (σ.symm ⟨i, hi⟩) d)) :
    (edgeRun G s (l.flatMap (slideMoves (σ.symm ⟨i, hi⟩)))).count = ind (shackAfterPut G σ i) ∧
      (edgeRun G s (l.flatMap (slideMoves (σ.symm ⟨i, hi⟩)))).contaminated =
        G.edgeSet \ (clearedBefore σ i ∪ star (σ.symm ⟨i, hi⟩) (d ++ l)) ∧
      Progressive G s (l.flatMap (slideMoves (σ.symm ⟨i, hi⟩))) ∧
      edgeCost G s (l.flatMap (slideMoves (σ.symm ⟨i, hi⟩))) ≤
        (shackAfterPut G σ i).card + 1 := by
  set v := σ.symm ⟨i, hi⟩ with hv
  have hσv : (σ v).val = i := by simp [hv]
  induction l generalizing s d with
  | nil =>
    refine ⟨hc, by simpa [edgeRun] using hK, trivial, ?_⟩
    simp only [List.flatMap_nil, edgeCost, hc, sum_ind]
    omega
  | cons u l ih =>
    have hu := hl u (by simp)
    have huS : u ∈ shackAfterPut G σ i := (mem_shackAfterPut_iff G σ i u).mpr
      ⟨hu.1.le, v, Or.inr hu.2, hσv.ge⟩
    have hvS : v ∈ shackAfterPut G σ i := (mem_shackAfterPut_iff G σ i v).mpr
      ⟨hσv.le, v, Or.inl rfl, hσv.ge⟩
    have hd : ∀ w ∈ d, (σ w).val < i ∧ G.Adj w v := fun w hw => hl w (by simp [hw])
    have hdu : ∀ w ∈ d ++ [u], (σ w).val < i ∧ G.Adj w v := by
      intro w hw
      rcases List.mem_append.mp hw with hw | hw
      · exact hd w hw
      · rw [List.mem_singleton.mp hw]
        exact hu
    have h2 := safe_star G σ hi subset_rfl (d ++ [u]) hdu
    rw [star_append_singleton, ← Set.union_assoc] at h2
    obtain ⟨t1, t2, t3, t4⟩ := slideMoves_spec G (shackAfterPut G σ i) _ huS hvS hu.2 s hc hK
      (safe_star G σ hi subset_rfl d hd) h2
    rw [Set.union_assoc, ← star_append_singleton] at t2
    obtain ⟨r1, r2, r3, r4⟩ := ih (d := d ++ [u]) (hl := by simpa using hl) (hc := t1) (hK := t2)
    simp only [List.append_assoc, List.singleton_append] at r2
    simp only [List.flatMap_cons, edgeRun_append, edgeCost_append, progressive_append]
    exact ⟨r1, r2, ⟨t3, r3⟩, max_le t4 r4⟩

theorem removals_spec_edge (σ : LinearLayout V) (i : ℕ) (l : List V)
    (hl : ∀ u ∈ l, MovedAt G σ i u) (P : Finset V) (hP : shackGuards G σ (i + 1) ⊆ P)
    (s : EdgeState V) (hc : s.count = ind P)
    (hK : s.contaminated = G.edgeSet \ clearedBefore σ (i + 1)) :
    (edgeRun G s (l.map .remove)).count = ind (P \ l.toFinset) ∧
      (edgeRun G s (l.map .remove)).contaminated = G.edgeSet \ clearedBefore σ (i + 1) ∧
      Progressive G s (l.map .remove) ∧ edgeCost G s (l.map .remove) ≤ P.card := by
  induction l generalizing P s with
  | nil =>
    refine ⟨by simpa [edgeRun] using hc, hK, trivial, ?_⟩
    simp [edgeCost, hc, sum_ind]
  | cons u l ih =>
    have hu := hl u (List.mem_cons_self ..)
    have huG : u ∉ shackGuards G σ (i + 1) := by
      simp only [shackGuards, Finset.mem_filter, Finset.mem_univ, true_and, not_and,
        not_exists]
      intro _ w huw hw
      have := hu.2 w huw
      omega
    set s₁ := edgeStep G s (.remove u) with hs₁
    have hc₁ : s₁.count = ind (P.erase u) := by
      simp only [hs₁, edgeStep, edgeCount, hc]
      funext w
      by_cases hwu : w = u
      · subst hwu
        by_cases hwP : w ∈ P <;> simp [ind, hwP]
      · simp [ind, hwu]
    have hPu : shackGuards G σ (i + 1) ⊆ P.erase u := by
      intro w hw
      exact Finset.mem_erase.mpr ⟨fun h => huG (h ▸ hw), hP hw⟩
    have hcl : clearedBy G (.remove u) s.count = ∅ := rfl
    obtain ⟨hK₁, hsub₁⟩ := edgeStep_of_safe (G := G) (m := .remove u) hK
      (by
        rw [hcl, Set.union_empty]
        have : supp (edgeCount G (.remove u) s.count) = P.erase u := by
          change supp s₁.count = _
          rw [hc₁, supp_ind]
        exact this ▸ safe_clearedBefore G σ (i + 1) hPu)
    rw [hcl, Set.union_empty] at hK₁
    obtain ⟨r1, r2, r3, r4⟩ := ih (fun w hw => hl w (List.mem_cons_of_mem _ hw)) (P.erase u)
      hPu s₁ hc₁ hK₁
    refine ⟨?_, r2, ⟨hsub₁, r3⟩, ?_⟩
    · change (edgeRun G s₁ (l.map .remove)).count = _
      rw [r1]
      congr 1
      ext w
      simp only [Finset.mem_sdiff, Finset.mem_erase, List.mem_toFinset, List.mem_cons]
      tauto
    · simp only [List.map_cons, edgeCost]
      rw [← hs₁, hc, sum_ind]
      exact max_le le_rfl (r4.trans (Finset.card_erase_le))

theorem diff_clearedBefore_succ (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V) :
    G.edgeSet \ (clearedBefore σ i ∪ star (σ.symm ⟨i, hi⟩) (leftNbrs G σ i (σ.symm ⟨i, hi⟩))) =
      G.edgeSet \ clearedBefore σ (i + 1) := by
  set v := σ.symm ⟨i, hi⟩ with hv
  have hσv : (σ v).val = i := by simp [hv]
  have hinj : ∀ a, (σ a).val = i → a = v := by
    intro a ha
    apply σ.injective
    exact Fin.ext (ha.trans hσv.symm)
  ext e
  induction e using Sym2.ind with
  | h a b =>
    simp only [Set.mem_sdiff, SimpleGraph.mem_edgeSet, Set.mem_union, clearedBefore, star,
      leftNbrs, Finset.mem_toList, Finset.mem_filter, Finset.mem_univ, true_and,
      Set.mem_ofPred_eq, Sym2.forall_mem_pair]
    constructor
    · rintro ⟨hab, hn⟩
      refine ⟨hab, fun ⟨ha, hb⟩ => hn ?_⟩
      by_cases h : (σ a).val < i ∧ (σ b).val < i
      · exact Or.inl h
      · right
        rcases Nat.lt_succ_iff_lt_or_eq.mp ha with ha' | ha'
        · have hb' : (σ b).val = i := by omega
          obtain rfl := hinj b hb'
          exact ⟨a, ⟨ha', hab⟩, rfl⟩
        · obtain rfl := hinj a ha'
          have hb' : (σ b).val ≠ i := fun h => hab.ne (hinj b h).symm
          exact ⟨b, ⟨by omega, hab.symm⟩, Sym2.eq_swap⟩
    · rintro ⟨hab, hn⟩
      refine ⟨hab, ?_⟩
      rintro (⟨ha, hb⟩ | ⟨u, ⟨hu, -⟩, he⟩)
      · exact hn ⟨by omega, by omega⟩
      · apply hn
        rcases Sym2.eq_iff.mp he with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> exact ⟨by omega, by omega⟩

/-- One phase of `search1`. -/
theorem edgePhase_spec (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V)
    (s : EdgeState V) (hc : s.count = ind (shackGuards G σ i))
    (hK : s.contaminated = G.edgeSet \ clearedBefore σ i) :
    (edgeRun G s (edgePhase G σ i)).count = ind (shackGuards G σ (i + 1)) ∧
      (edgeRun G s (edgePhase G σ i)).contaminated = G.edgeSet \ clearedBefore σ (i + 1) ∧
      Progressive G s (edgePhase G σ i) ∧
      edgeCost G s (edgePhase G σ i) ≤ (shackAfterPut G σ i).card + 1 := by
  set v := σ.symm ⟨i, hi⟩ with hv
  have hσv : (σ v).val = i := by simp [hv]
  have hvG : v ∉ shackGuards G σ i := by
    simp [shackGuards, hσv]
  set s₁ := edgeStep G s (.place v) with hs₁
  have hc₁ : s₁.count = ind (shackAfterPut G σ i) := by
    simp only [hs₁, edgeStep, edgeCount, hc]
    rw [← insert_shackGuards G σ hi]
    funext w
    by_cases hwv : w = v
    · subst hwv
      simp [ind, hvG, ← hv]
    · simp [ind, hwv, ← hv]
  have hcl : clearedBy G (.place v) s.count = ∅ := rfl
  obtain ⟨hK₁, hsub₁⟩ := edgeStep_of_safe (G := G) (m := .place v) hK
    (by
      rw [hcl, Set.union_empty]
      have : supp (edgeCount G (.place v) s.count) = shackAfterPut G σ i := by
        change supp s₁.count = _
        rw [hc₁, supp_ind]
      exact this ▸ safe_clearedBefore G σ i (shackGuards_subset_shackAfterPut G σ hi))
  rw [hcl, Set.union_empty] at hK₁
  obtain ⟨t1, t2, t3, t4⟩ := slides_spec G σ hi (leftNbrs G σ i v) []
    (by
      intro u hu
      simpa [leftNbrs] using hu) s₁ hc₁ (by simpa using hK₁)
  rw [List.nil_append, diff_clearedBefore_succ G σ hi] at t2
  obtain ⟨r1, r2, r3, r4⟩ := removals_spec_edge G σ i
    (Finset.univ.filter (MovedAt G σ i)).toList (fun u hu => by simpa using hu)
    (shackAfterPut G σ i) (by rw [← shackAfterPut_sdiff_moved]; exact Finset.sdiff_subset)
    _ t1 t2
  simp only [edgePhase, hi, ↓reduceDIte]
  refine ⟨?_, ?_, ?_, ?_⟩
  · change (edgeRun G s₁ _).count = _
    rw [edgeRun_append, r1, Finset.toList_toFinset, shackAfterPut_sdiff_moved]
  · change (edgeRun G s₁ _).contaminated = _
    rw [edgeRun_append, r2]
  · exact ⟨hsub₁, (progressive_append _ _ _).mpr ⟨t3, r3⟩⟩
  · simp only [edgeCost]
    rw [← hs₁, edgeCost_append, hc, sum_ind]
    refine max_le ?_ (max_le t4 (r4.trans (Nat.le_succ _)))
    exact (Finset.card_le_card (shackGuards_subset_shackAfterPut G σ hi)).trans (Nat.le_succ _)

/-- **EST Lemma 2.2, per layout.** `search1` on an in-sequence `σ` is a progressive
search strategy with `ν(σ) + 1` searchers. -/
theorem edgeStrategy_isProgressive (σ : LinearLayout V) :
    IsProgressiveEdgeSearch G (inNarrowness G σ + 1) (edgeStrategy G σ) := by
  have key : ∀ i ≤ Fintype.card V,
      (edgeRun G (edgeInit G) ((List.range i).flatMap (edgePhase G σ))).count =
          ind (shackGuards G σ i) ∧
        (edgeRun G (edgeInit G) ((List.range i).flatMap (edgePhase G σ))).contaminated =
          G.edgeSet \ clearedBefore σ i ∧
        Progressive G (edgeInit G) ((List.range i).flatMap (edgePhase G σ)) ∧
        edgeCost G (edgeInit G) ((List.range i).flatMap (edgePhase G σ)) ≤
          inNarrowness G σ + 1 := by
    intro i hi
    induction i with
    | zero =>
      refine ⟨?_, ?_, trivial, ?_⟩
      · funext w
        simp [edgeRun, edgeInit, shackGuards, ind]
      · ext e
        induction e using Sym2.ind with
        | h a b =>
          simp only [edgeRun, List.flatMap_nil, List.range_zero, List.foldl_nil, edgeInit,
            clearedBefore, Set.mem_sdiff, Nat.not_lt_zero]
          exact ⟨fun h => ⟨h, fun h' => h' a (Sym2.mem_mk_left _ _)⟩, fun h => h.1⟩
      · simp [edgeCost, edgeInit]
    | succ i ih =>
      obtain ⟨hc, hK, hm, hcost⟩ := ih (by omega)
      set pre := (List.range i).flatMap (edgePhase G σ) with hpre
      have hsplit : (List.range (i + 1)).flatMap (edgePhase G σ) = pre ++ edgePhase G σ i := by
        rw [List.range_succ, List.flatMap_append]
        simp [hpre]
      obtain ⟨p1, p2, p3, p4⟩ := edgePhase_spec G σ (by omega) _ hc hK
      simp only [hsplit, edgeRun_append, edgeCost_append, progressive_append]
      exact ⟨p1, p2, ⟨hm, p3⟩, max_le hcost (p4.trans (Nat.add_le_add_right
        (card_shackAfterPut_le_inNarrowness G σ i (by omega)) 1))⟩
  obtain ⟨-, hK, hm, hc⟩ := key (Fintype.card V) le_rfl
  refine ⟨⟨?_, hc⟩, hm⟩
  have hK' : edgeRun G (edgeInit G) (edgeStrategy G σ) =
      edgeRun G (edgeInit G) ((List.range (Fintype.card V)).flatMap (edgePhase G σ)) := rfl
  rw [hK', hK]
  apply Set.eq_empty_of_subset_empty
  rintro e ⟨-, he⟩
  exact he fun x _ => (σ x).isLt

end Upper

/-! ### From a progressive strategy to a layout (EST Lemma 2.1) -/

section Lower

/-- **EST Lemma 2.1 for progressive strategies.** A progressive strategy with at
most `k` searchers gives `vs(G) ≤ k`: order the vertices by the time from which
no contaminated edge touches them, a vertex unguarded at that time first. -/
theorem vertexSeparation_le_of_progressive {k : ℕ} {ms : List (EdgeMove V)}
    (h : IsProgressiveEdgeSearch G k ms) : vertexSeparation G ≤ k := by
  obtain ⟨⟨hclr, hcost⟩, hmono⟩ := h
  set L := ms.length with hL
  let st : ℕ → EdgeState V := fun t => edgeRun G (edgeInit G) (ms.take t)
  let Clear : V → ℕ → Prop := fun v t => ∀ e ∈ (st t).contaminated, v ∉ e
  have hstL : st L = edgeRun G (edgeInit G) ms := by
    simp only [st, hL, List.take_length]
  have hClearL : ∀ v, Clear v L := by
    intro v e he
    rw [hstL, hclr] at he
    exact absurd he (Set.notMem_empty e)
  let τ : V → ℕ := fun v => sInf {t | Clear v t}
  have hτmem : ∀ v, Clear v (τ v) := fun v => Nat.sInf_mem (s := {t | Clear v t}) ⟨L, hClearL v⟩
  have hτL : ∀ v, τ v ≤ L := fun v => Nat.sInf_le (hClearL v)
  have hτmin : ∀ v t, t < τ v → ¬ Clear v t := fun v t ht => Nat.notMem_of_lt_sInf ht
  have hanti : ∀ t t', t ≤ t' → t' ≤ L → (st t').contaminated ⊆ (st t).contaminated := by
    intro t t' htt'
    induction t', htt' using Nat.le_induction with
    | base => exact fun _ => subset_rfl
    | succ t' _ ih =>
      intro hle
      exact (progressive_take hmono (by omega)).trans (ih (by omega))
  have hClear_after : ∀ v t, τ v ≤ t → t ≤ L → Clear v t :=
    fun v t hvt htL e he => hτmem v e (hanti _ _ hvt htL he)
  have hstep : ∀ t (ht : t < ms.length), st (t + 1) = edgeStep G (st t) (ms[t]'ht) :=
    fun t ht => edgeRun_take_succ (G := G) (edgeInit G) ms ht
  -- every position but the first is closed
  have hclosed : ∀ t, 0 < t → t ≤ L →
      IsClosed (G := G) (⟨(st t).guards, (st t).contaminated⟩ : SearchState V) := by
    intro t ht htL
    obtain ⟨t', rfl⟩ : ∃ t', t = t' + 1 := ⟨t - 1, by omega⟩
    rw [hstep t' (by omega)]
    exact isClosed_edgeStep _ _
  have hcard : ∀ t, (st t).guards.card ≤ k :=
    fun t => (card_supp_le_sum _).trans ((sum_le_edgeCost_take _ _ t).trans hcost)
  -- a vertex with a neighbour is not clear at the start
  have hpos : ∀ v w, G.Adj v w → 0 < τ v := by
    intro v w hvw
    by_contra h0
    have h0' : τ v = 0 := by omega
    have := hτmem v
    rw [h0'] at this
    exact this s(v, w) (by simpa [st, edgeRun, edgeInit] using hvw) (Sym2.mem_mk_left _ _)
  -- the sort key: clearing time, a vertex unguarded at that time first
  let g : V → ℕ := fun v => if v ∈ (st (τ v)).guards then 1 else 0
  have hg : ∀ v, g v ≤ 1 := fun v => by simp only [g]; split_ifs <;> omega
  obtain ⟨σ, hσ⟩ := exists_layout_sorted fun v => 2 * τ v + g v
  have hvs : vertexSepOfLayout G σ ≤ k := by
    rw [vertexSepOfLayout_le_iff]
    intro i hi
    set v := σ.symm ⟨i, hi⟩ with hv
    have hσv : (σ v).val = i := by simp [hv]
    have hpre : ∀ u, (σ u).val ≤ i → 2 * τ u + g u ≤ 2 * τ v + g v := by
      intro u hu
      by_contra hlt
      have := hσ v u (by omega)
      omega
    have hsuf : ∀ w, i < (σ w).val → 2 * τ v + g v ≤ 2 * τ w + g w := by
      intro w hw
      by_contra hlt
      have := hσ w v (by omega)
      omega
    have hsub : activeSuffix G σ i ⊆ (st (τ v)).guards := by
      intro w hw
      obtain ⟨hwi, u, hu, huw⟩ := (mem_activeSuffix_iff G σ i w).mp hw
      rw [mem_prefixSet_iff] at hu
      have h1 := hpre u hu
      have h2 := hsuf w hwi
      have hgu := hg u
      have hgv := hg v
      have hgw := hg w
      have hτuv : τ u ≤ τ v := by omega
      have hτvw : τ v ≤ τ w := by omega
      have hwpos := hpos w u huw.symm
      rcases Nat.lt_or_eq_of_le hτvw with hlt | heq
      · -- `w` still touches a contaminated edge; unguarded, it would spread the gas
        -- to the clear edge `uw`
        obtain ⟨f, hf, hwf⟩ : ∃ f ∈ (st (τ v)).contaminated, w ∈ f := by
          by_contra hne
          push Not at hne
          exact hτmin w (τ v) hlt hne
        by_contra hwS
        have hvpos : 0 < τ v := by
          by_contra h0
          have h0' : τ v = 0 := by omega
          rw [h0'] at hf hwS
          -- at time 0 there is no searcher at all
          exact hwS (by
            have := hτmem u
            have hu0 : τ u = 0 := by omega
            rw [hu0] at this
            exact absurd (this s(u, w) (by simpa [st, edgeRun, edgeInit] using huw)
              (Sym2.mem_mk_left _ _)) (by simp))
        have := hclosed (τ v) hvpos (hτL v) s(u, w) (G.mem_edgeSet.mpr huw) f hf w
          (Sym2.mem_mk_right _ _) w hwf hwS Relation.ReflTransGen.refl
        exact hClear_after u (τ v) hτuv (hτL v) _ this (Sym2.mem_mk_left _ _)
      · -- same clearing time: the tie-break, and at most one unguarded vertex per step
        by_cases hwS : w ∈ (st (τ w)).guards
        · rwa [heq]
        · exfalso
          have hgw0 : g w = 0 := by simp [g, hwS]
          have hgv0 : g v = 0 := by omega
          have hvS : v ∉ (st (τ v)).guards := by
            intro hvS
            simp [g, hvS] at hgv0
          have hvw : v ≠ w := by
            rintro rfl
            omega
          obtain ⟨t, ht⟩ : ∃ t, τ v = t + 1 := ⟨τ v - 1, by omega⟩
          have htL : t < L := by have := hτL v; omega
          obtain ⟨e, he, hve⟩ : ∃ e ∈ (st t).contaminated, v ∈ e := by
            by_contra hne
            push Not at hne
            exact hτmin v t (by omega) hne
          obtain ⟨f, hf, hwf⟩ : ∃ f ∈ (st t).contaminated, w ∈ f := by
            by_contra hne
            push Not at hne
            exact hτmin w t (by omega) hne
          have hs1 := hstep t (by omega)
          have hCv : ∀ e' ∈ (st (t + 1)).contaminated, v ∉ e' := by
            intro e' he'
            have := hτmem v
            rw [ht] at this
            exact this e' he'
          have hCw : ∀ e' ∈ (st (t + 1)).contaminated, w ∉ e' := by
            intro e' he'
            have := hτmem w
            rw [← heq, ht] at this
            exact this e' he'
          rw [ht] at hvS
          rw [← heq, ht] at hwS
          rw [hs1] at hCv hCw hvS hwS
          exact clear_step_unique hvw he hve (fun h => hCv e h hve) hf hwf
            (fun h => hCw f h hwf) hvS hwS
    unfold vertexSepAt
    exact (Finset.card_le_card hsub).trans (hcard _)
  exact (vertexSeparation_le_vertexSepOfLayout G σ).trans hvs

end Lower

/-! ### Theorem 2.1 for the progressive game -/

section Main

/-- **EST Lemma 2.2, progressive**: `s(G) ≤ vs(G) + 2` with a progressive
strategy. -/
theorem progressiveEdgeSearch_le_vertexSeparation_add_two :
    progressiveEdgeSearch G ≤ vertexSeparation G + 2 := by
  rcases isEmpty_or_nonempty V with hV | hV
  · refine Nat.sInf_le ⟨[], ⟨?_, ?_⟩, trivial⟩
    · ext e
      induction e using Sym2.ind with
      | h a b => exact isEmptyElim a
    · simp [edgeCost, edgeInit]
  · obtain ⟨σ₀, hσ₀⟩ := exists_layout_vertexSeparation G
    have h := edgeStrategy_isProgressive G (reverseLayout σ₀)
    rw [inNarrowness_eq_vertexSepOfLayout_reverse, reverseLayout_reverseLayout, hσ₀] at h
    exact Nat.sInf_le ⟨_, h⟩

/-- **EST Lemma 2.1, progressive**: `vs(G) ≤ s(G)` for progressive strategies. -/
theorem vertexSeparation_le_progressiveEdgeSearch :
    vertexSeparation G ≤ progressiveEdgeSearch G := by
  rcases isEmpty_or_nonempty V with hV | hV
  · have : vertexSeparation G = 0 := by
      apply Nat.eq_zero_of_le_zero
      refine (vertexSeparation_le_vertexSepOfLayout G (Fintype.equivFin V)).trans ?_
      simp [vertexSepOfLayout]
    omega
  · obtain ⟨ms, hms⟩ := Nat.sInf_mem (s := {k | ∃ ms, IsProgressiveEdgeSearch G k ms})
      ⟨_, _, edgeStrategy_isProgressive G (Fintype.equivFin V)⟩
    exact vertexSeparation_le_of_progressive G hms

/-- **Ellis, Sudborough & Turner (1994), Theorem 2.1, for the progressive game**:
`vs(G) ≤ s(G) ≤ vs(G) + 2`, on every finite graph. -/
theorem vertexSeparation_le_progressiveEdgeSearch_le_add_two :
    vertexSeparation G ≤ progressiveEdgeSearch G ∧
      progressiveEdgeSearch G ≤ vertexSeparation G + 2 :=
  ⟨vertexSeparation_le_progressiveEdgeSearch G,
    progressiveEdgeSearch_le_vertexSeparation_add_two G⟩

/-- With Kinnersley's theorem: `pw(G) ≤ s(G) ≤ pw(G) + 2`, progressive game. -/
theorem pathwidth_le_progressiveEdgeSearch_le_add_two :
    pathwidth G ≤ progressiveEdgeSearch G ∧ progressiveEdgeSearch G ≤ pathwidth G + 2 := by
  rw [← vertexSeparation_eq_pathwidth]
  exact vertexSeparation_le_progressiveEdgeSearch_le_add_two G

/-- A progressive strategy is a strategy. -/
theorem edgeSearch_le_progressiveEdgeSearch : edgeSearch G ≤ progressiveEdgeSearch G := by
  rcases Nat.eq_zero_or_pos (Fintype.card V) with h0 | hpos
  · have : IsEmpty V := Fintype.card_eq_zero_iff.mp h0
    apply Nat.sInf_le
    refine ⟨[], ?_, ?_⟩
    · ext e
      induction e using Sym2.ind with
      | h a b => exact isEmptyElim a
    · simp [edgeCost, edgeInit]
  · obtain ⟨ms, hms⟩ := Nat.sInf_mem (s := {k | ∃ ms, IsProgressiveEdgeSearch G k ms})
      ⟨_, _, edgeStrategy_isProgressive G (Fintype.equivFin V)⟩
    exact Nat.sInf_le ⟨ms, hms.1⟩

/-- The half of Theorem 2.1 that needs no monotonicity: `s(G) ≤ vs(G) + 2`. -/
theorem edgeSearch_le_vertexSeparation_add_two :
    edgeSearch G ≤ vertexSeparation G + 2 :=
  (edgeSearch_le_progressiveEdgeSearch G).trans
    (progressiveEdgeSearch_le_vertexSeparation_add_two G)

theorem edgeSearch_le_pathwidth_add_two : edgeSearch G ≤ pathwidth G + 2 := by
  rw [← vertexSeparation_eq_pathwidth]
  exact edgeSearch_le_vertexSeparation_add_two G

/-- Granting LaPaugh's theorem, the full Theorem 2.1 follows. -/
theorem vertexSeparation_le_edgeSearch_of_monotonicity (hmono : EdgeSearchMonotonicity G) :
    vertexSeparation G ≤ edgeSearch G := by
  rw [hmono]
  exact vertexSeparation_le_progressiveEdgeSearch G

/-- **[10] p. 209, monotone games**: `ns − 1 ≤ es` on a graph with an edge. -/
theorem monotoneNodeSearch_sub_one_le_progressiveEdgeSearch {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    monotoneNodeSearch G - 1 ≤ progressiveEdgeSearch G := by
  rw [monotoneNodeSearch_eq_vertexSeparation_add_one G h₀, Nat.add_sub_cancel]
  exact vertexSeparation_le_progressiveEdgeSearch G

/-- **[10] p. 209, monotone games**: `es ≤ ns + 1` on a graph with an edge. -/
theorem progressiveEdgeSearch_le_monotoneNodeSearch_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    progressiveEdgeSearch G ≤ monotoneNodeSearch G + 1 := by
  rw [monotoneNodeSearch_eq_vertexSeparation_add_one G h₀]
  exact progressiveEdgeSearch_le_vertexSeparation_add_two G

/-! ### Edgeless graphs -/

theorem progressiveEdgeSearch_of_edgeless (h : ∀ u v, ¬ G.Adj u v) :
    progressiveEdgeSearch G = 0 := by
  apply Nat.eq_zero_of_le_zero
  refine Nat.sInf_le ⟨[], ⟨?_, ?_⟩, trivial⟩
  · ext e
    induction e using Sym2.ind with
    | h a b => simpa [edgeRun, edgeInit] using h a b
  · simp [edgeCost, edgeInit]

theorem edgeSearch_of_edgeless (h : ∀ u v, ¬ G.Adj u v) : edgeSearch G = 0 :=
  Nat.eq_zero_of_le_zero ((edgeSearch_le_progressiveEdgeSearch G).trans
    (progressiveEdgeSearch_of_edgeless G h).le)

end Main

end Complex

end MOSPFormalization
