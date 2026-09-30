/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Node search, monotone: `mns = vs + 1`

Table 1 of Linhares & Yanasse (2002), row "node search game", source [9]
Kirousis & Papadimitriou (1985), *Interval graphs and searching*, Discrete
Mathematics 55, 181–184; the relation to vertex separation is [10] Kirousis &
Papadimitriou (1986), *Searching and pebbling*, Theoretical Computer Science
47, 205–218, Theorem 4.1.

## The source's definition

[9] p. 181: "A searching strategy S is a sequence of moves where the player
either places a searcher on a node of the graph that carries no searcher or
deletes the searcher of a guarded node. The edges of the graph are initially
considered contaminated by a gas. The object of a searching strategy is to
clear all edges. The clearing of an edge is accomplished once both its
endpoints concurrently carry a searcher. A clear edge may be recontaminated
once there appears a path that carries no searchers and that connects this
edge with a contaminated one." The node search number `ns(G)` is the least
maximum number of searchers of a strategy clearing all edges (p. 182; the same
in [10] §2, p. 208). A strategy is *recontamination-free* (monotone) if no
move recontaminates an edge ([10] §2, `pns`).

Formalised as the game itself, not as a formula:

* `SearchState` — the guarded nodes and the contaminated edges;
* `SearchMove` — `place v` or `remove v`;
* `searchStep` — the guard set changes, every edge with both endpoints guarded
  is cleared, and then every edge joined to a still-contaminated edge by a
  searcher-free path (`FreeReach`: a path all of whose vertices are unguarded,
  from an endpoint of the one to an endpoint of the other) is contaminated
  (`recontaminate`). This is the same semantics as `paper2/complex_check.py`'s
  `node_search`;
* `searchCost` — the largest number of searchers over the states of the run;
* `NoRecontamination` — no move enlarges the contaminated set;
* `nodeSearch` (all strategies) and `monotoneNodeSearch` (recontamination-free
  strategies), each the least cost of a strategy that clears every edge.

A move that the source forbids — placing on a guarded node, removing from an
unguarded one — leaves the guard set as it is; allowing it changes no value,
because on the states a run reaches the step it makes is the identity on the
guards and cannot lower the cost.

Nothing in these definitions mentions layouts, separation or decompositions.

## What is proved

* `monotoneNodeSearch_eq_vertexSeparation_add_one` — **[10] Theorem 4.1 for
  the monotone game**: for every graph with at least one edge,
  `mns(G) = vs(G) + 1`; hence `monotoneNodeSearch_eq_pathwidth_add_one`.
  - `≤`: the shack process of Kornai & Tuza (item 04) is a monotone strategy:
    place `vᵢ`, then remove every vertex with no neighbour after `vᵢ`
    (`shackStrategy`). It clears every edge, never recontaminates, and its
    largest guard set is the shack, so it costs `ν(σ)`
    (`shackStrategy_isMonotone`), and `ν(σ) = vs(σ reversed) + 1`.
  - `≥`: from a monotone strategy, order the vertices by the time `τ(v)` from
    which no contaminated edge touches `v`. At the time `t = τ(vᵢ)` every
    vertex after position `i` with a neighbour at or before it carries a
    searcher — either its last contaminated edge was cleared at `t`, or it
    still has a contaminated edge and an unguarded endpoint would spread the
    gas back onto the clear edge to its earlier neighbour — and so does `vᵢ`
    itself, whose last contaminated edge was cleared at `t`
    (`vertexSeparation_add_one_le_of_monotone`). [10] p. 217 orders instead
    by the time a node *first accepts* a searcher and counts earlier nodes
    with a later neighbour, claiming they all carry searchers (its (2)). A
    monotone strategy may guard a node and delete the searcher before any of
    its edges is clear, and then the claim fails: on `K_{1,3}`, placing and
    deleting each leaf in turn and then searching from the centre costs 2, but
    first acceptance orders the leaves before the centre, and three leaves
    precede their neighbour. Deleting such useless placements repairs [10]'s
    argument; ordering by clearing time does not need the repair.
* Edge case: on an edgeless graph `mns = ns = 0` (the empty strategy), while
  `vs + 1 = 1` whenever there is a vertex (`monotoneNodeSearch_of_edgeless`,
  `nodeSearch_of_edgeless`). This is the exception recorded by item 01.
* `nodeSearch_le_monotoneNodeSearch` — the trivial half of monotonicity, so
  `ns ≤ vs + 1` for every graph with an edge.

## Not proved: the full game

That recontamination does not help, `ns = mns` ([10] Theorem 2.3, from
LaPaugh's theorem for edge search, [10] Theorem 2.1), is stated as the
proposition `NodeSearchMonotonicity` and not asserted. With it,
`vs + 1 ≤ ns` follows from the theorem proved here. It is recorded in
`paper2/equivalences.md` as a named gap; no `sorry` stands for it.
-/

import MOSPFormalization.Complex.EdgeSeparation

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### The game (Kirousis & Papadimitriou 1985, p. 181) -/

/-- A move: place a searcher on a node, or delete the searcher of a node. -/
inductive SearchMove (V : Type*)
  | place (v : V)
  | remove (v : V)

/-- A position of the game: the guarded nodes and the contaminated edges. -/
structure SearchState (V : Type*) where
  guards : Finset V
  contaminated : Set (Sym2 V)

/-- The guard set after a move. -/
def SearchMove.applyTo : SearchMove V → Finset V → Finset V
  | .place v, S => insert v S
  | .remove v, S => S.erase v

/-- Both endpoints of `e` carry a searcher. -/
def Guarded (S : Finset V) (e : Sym2 V) : Prop := ∀ x ∈ e, x ∈ S

/-- One step of a searcher-free path: adjacent, both unguarded. -/
def FreeStep (S : Finset V) (x y : V) : Prop := G.Adj x y ∧ x ∉ S ∧ y ∉ S

/-- `x` and `y` are joined by a path that carries no searchers (the path of
length zero included, when `x` is unguarded). -/
def FreeReach (S : Finset V) : V → V → Prop := Relation.ReflTransGen (FreeStep G S)

/-- The edges that a set `D` of contaminated edges recontaminates when the
guards are `S`: those joined to an edge of `D` by a searcher-free path. -/
def recontaminate (S : Finset V) (D : Set (Sym2 V)) : Set (Sym2 V) :=
  {e | e ∈ G.edgeSet ∧ ∃ f ∈ D, ∃ x ∈ e, ∃ y ∈ f, x ∉ S ∧ FreeReach G S x y}

/-- One move: change the guards, clear the edges whose endpoints are both
guarded, then let the gas spread through unguarded paths. -/
def searchStep (s : SearchState V) (m : SearchMove V) : SearchState V :=
  let S' := m.applyTo s.guards
  let D := {e | e ∈ s.contaminated ∧ ¬ Guarded S' e}
  ⟨S', D ∪ recontaminate G S' D⟩

/-- The start: no searcher, every edge contaminated. -/
def searchInit : SearchState V := ⟨∅, G.edgeSet⟩

/-- The position after a sequence of moves. -/
def runSearch (s : SearchState V) (ms : List (SearchMove V)) : SearchState V :=
  ms.foldl (searchStep G) s

/-- The largest number of searchers over the positions of a run. -/
def searchCost : SearchState V → List (SearchMove V) → ℕ
  | s, [] => s.guards.card
  | s, m :: ms => max s.guards.card (searchCost (searchStep G s m) ms)

/-- No move of the run recontaminates an edge. -/
def NoRecontamination : SearchState V → List (SearchMove V) → Prop
  | _, [] => True
  | s, m :: ms => (searchStep G s m).contaminated ⊆ s.contaminated ∧
      NoRecontamination (searchStep G s m) ms

/-- A strategy clearing every edge with at most `k` searchers. -/
def IsNodeSearch (k : ℕ) (ms : List (SearchMove V)) : Prop :=
  (runSearch G (searchInit G) ms).contaminated = ∅ ∧ searchCost G (searchInit G) ms ≤ k

/-- A recontamination-free strategy clearing every edge with at most `k`
searchers. -/
def IsMonotoneNodeSearch (k : ℕ) (ms : List (SearchMove V)) : Prop :=
  IsNodeSearch G k ms ∧ NoRecontamination G (searchInit G) ms

/-- The node search number `ns(G)` ([9] p. 182). -/
noncomputable def nodeSearch : ℕ := sInf {k | ∃ ms, IsNodeSearch G k ms}

/-- The monotone node search number: the least cost of a recontamination-free
strategy ([10] §2). -/
noncomputable def monotoneNodeSearch : ℕ := sInf {k | ∃ ms, IsMonotoneNodeSearch G k ms}

/-- **[10] Theorem 2.3** (from LaPaugh's theorem), stated and not asserted:
recontamination does not help. -/
def NodeSearchMonotonicity : Prop := nodeSearch G = monotoneNodeSearch G

/-! ### Basic facts about the game -/

section Basic

variable {G}

theorem freeReach_not_mem {S : Finset V} {x y : V} (h : FreeReach G S x y) (hx : x ∉ S) :
    y ∉ S := by
  induction h with
  | refl => exact hx
  | tail _ hyz _ => exact hyz.2.2

theorem FreeReach.mono {S T : Finset V} (hST : S ⊆ T) {x y : V} (h : FreeReach G T x y) :
    FreeReach G S x y := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | tail _ hyz ih =>
    exact ih.tail ⟨hyz.1, fun h => hyz.2.1 (hST h), fun h => hyz.2.2 (hST h)⟩

/-- Two vertices of an edge are equal or adjacent. -/
theorem eq_or_adj_of_mem_edgeSet {e : Sym2 V} (he : e ∈ G.edgeSet) {x y : V} (hx : x ∈ e)
    (hy : y ∈ e) : x = y ∨ G.Adj x y := by
  induction e using Sym2.ind with
  | h a b =>
    rw [SimpleGraph.mem_edgeSet] at he
    rw [Sym2.mem_iff] at hx hy
    rcases hx with rfl | rfl <;> rcases hy with rfl | rfl
    · exact Or.inl rfl
    · exact Or.inr he
    · exact Or.inr he.symm
    · exact Or.inl rfl

/-- The contaminated set is closed under spreading through the unguarded
vertices. -/
def IsClosed (s : SearchState V) : Prop :=
  ∀ e ∈ G.edgeSet, ∀ f ∈ s.contaminated, ∀ x ∈ e, ∀ y ∈ f, x ∉ s.guards →
    FreeReach G s.guards x y → e ∈ s.contaminated

theorem isClosed_init : IsClosed (G := G) (searchInit G) :=
  fun _ he _ _ _ _ _ _ _ _ => he

theorem isClosed_step (s : SearchState V) (m : SearchMove V) :
    IsClosed (G := G) (searchStep G s m) := by
  intro e he f hf x hx y hy hxS hxy
  simp only [searchStep] at hf hxS hxy ⊢
  rcases hf with hf | ⟨hfE, f₀, hf₀, x', hx', y', hy', hx'S, hx'y'⟩
  · exact Or.inr ⟨he, f, hf, x, hx, y, hy, hxS, hxy⟩
  · refine Or.inr ⟨he, f₀, hf₀, x, hx, y', hy', hxS, ?_⟩
    have hyS := freeReach_not_mem hxy hxS
    rcases eq_or_adj_of_mem_edgeSet hfE hy hx' with rfl | hadj
    · exact hxy.trans hx'y'
    · exact (hxy.tail ⟨hadj, hyS, hx'S⟩).trans hx'y'

theorem isClosed_runSearch {s : SearchState V} (hs : IsClosed (G := G) s)
    (ms : List (SearchMove V)) : IsClosed (G := G) (runSearch G s ms) := by
  induction ms generalizing s with
  | nil => exact hs
  | cons m ms ih => exact ih (isClosed_step s m)

theorem contaminated_step_subset_edgeSet {s : SearchState V}
    (hs : s.contaminated ⊆ G.edgeSet) (m : SearchMove V) :
    (searchStep G s m).contaminated ⊆ G.edgeSet := by
  rintro e (he | he)
  · exact hs he.1
  · exact he.1

theorem contaminated_runSearch_subset_edgeSet {s : SearchState V}
    (hs : s.contaminated ⊆ G.edgeSet) (ms : List (SearchMove V)) :
    (runSearch G s ms).contaminated ⊆ G.edgeSet := by
  induction ms generalizing s with
  | nil => exact hs
  | cons m ms ih => exact ih (contaminated_step_subset_edgeSet hs m)

/-- Every contaminated edge after a step has an unguarded endpoint. -/
theorem not_guarded_of_mem_step {s : SearchState V} {m : SearchMove V} {e : Sym2 V}
    (he : e ∈ (searchStep G s m).contaminated) :
    ¬ Guarded (searchStep G s m).guards e := by
  rcases he with he | ⟨-, -, -, x, hx, -, -, hxS, -⟩
  · exact he.2
  · exact fun h => hxS (h x hx)

/-- An edge contaminated before a step and not guarded after it stays
contaminated. -/
theorem mem_step_of_mem {s : SearchState V} {m : SearchMove V} {e : Sym2 V}
    (he : e ∈ s.contaminated) (hg : ¬ Guarded (searchStep G s m).guards e) :
    e ∈ (searchStep G s m).contaminated :=
  Or.inl ⟨he, hg⟩

/-- Placing a searcher on a closed position recontaminates nothing. -/
theorem step_place_subset {s : SearchState V} (hs : IsClosed (G := G) s) (v : V) :
    (searchStep G s (.place v)).contaminated ⊆ s.contaminated := by
  rintro e (he | ⟨heE, f, hf, x, hx, y, hy, hxS, hxy⟩)
  · exact he.1
  · simp only [SearchMove.applyTo] at hxS hxy
    have hsub : s.guards ⊆ insert v s.guards := Finset.subset_insert _ _
    exact hs e heE f hf.1 x hx y hy (fun h => hxS (hsub h)) (hxy.mono hsub)

/-- Removing the searcher of a node that touches no contaminated edge, from a
closed position, recontaminates nothing. -/
theorem step_remove_subset {s : SearchState V} (hs : IsClosed (G := G) s) (v : V)
    (hv : ∀ e ∈ s.contaminated, v ∉ e) :
    (searchStep G s (.remove v)).contaminated ⊆ s.contaminated := by
  rintro e (he | ⟨heE, f, hf, x, hx, y, hy, hxS, hxy⟩)
  · exact he.1
  · simp only [SearchMove.applyTo] at hxS hxy
    have hfC : f ∈ s.contaminated := hf.1
    -- along the path, every vertex is not `v`, is unguarded, and all its edges
    -- are contaminated
    have key : ∀ z, FreeReach G (s.guards.erase v) z y → z ∉ s.guards.erase v →
        z ≠ v ∧ ∀ e' ∈ G.edgeSet, z ∈ e' → e' ∈ s.contaminated := by
      intro z hz
      induction hz using Relation.ReflTransGen.head_induction_on with
      | refl =>
        intro hyS
        have hyv : y ≠ v := fun h => hv f hfC (h ▸ hy)
        have hyS' : y ∉ s.guards := fun h => hyS (Finset.mem_erase.mpr ⟨hyv, h⟩)
        exact ⟨hyv, fun e' he' hye' =>
          hs e' he' f hfC y hye' y hy hyS' Relation.ReflTransGen.refl⟩
      | @head a b hab _ ih =>
        intro haS
        obtain ⟨hadj, -, hbS⟩ := hab
        obtain ⟨-, hb⟩ := ih hbS
        have hab' : s(a, b) ∈ s.contaminated :=
          hb _ (G.mem_edgeSet.mpr hadj) (Sym2.mem_mk_right _ _)
        have hav : a ≠ v := by
          rintro rfl
          exact hv _ hab' (Sym2.mem_mk_left _ _)
        have haS' : a ∉ s.guards := fun h => haS (Finset.mem_erase.mpr ⟨hav, h⟩)
        exact ⟨hav, fun e' he' hae' =>
          hs e' he' _ hab' a hae' a (Sym2.mem_mk_left _ _) haS' Relation.ReflTransGen.refl⟩
    exact (key x hxy hxS).2 e heE hx

/-! ### Runs -/

theorem runSearch_append (s : SearchState V) (ms ms' : List (SearchMove V)) :
    runSearch G s (ms ++ ms') = runSearch G (runSearch G s ms) ms' :=
  List.foldl_append

theorem card_le_searchCost (s : SearchState V) (ms : List (SearchMove V)) :
    s.guards.card ≤ searchCost G s ms := by
  cases ms with
  | nil => exact le_rfl
  | cons m ms => exact le_max_left _ _

theorem searchCost_append (s : SearchState V) (ms ms' : List (SearchMove V)) :
    searchCost G s (ms ++ ms') =
      max (searchCost G s ms) (searchCost G (runSearch G s ms) ms') := by
  induction ms generalizing s with
  | nil => exact (max_eq_right (card_le_searchCost s ms')).symm
  | cons m ms ih =>
    simp only [List.cons_append, searchCost, ih]
    rw [max_assoc]
    rfl

theorem noRecontamination_append (s : SearchState V) (ms ms' : List (SearchMove V)) :
    NoRecontamination G s (ms ++ ms') ↔
      NoRecontamination G s ms ∧ NoRecontamination G (runSearch G s ms) ms' := by
  induction ms generalizing s with
  | nil => simp [NoRecontamination, runSearch]
  | cons m ms ih =>
    simp only [List.cons_append, NoRecontamination, ih]
    exact ⟨fun h => ⟨⟨h.1, h.2.1⟩, h.2.2⟩, fun h => ⟨h.1.1, h.1.2, h.2⟩⟩

theorem runSearch_take_succ (s : SearchState V) (ms : List (SearchMove V)) {t : ℕ}
    (ht : t < ms.length) :
    runSearch G s (ms.take (t + 1)) = searchStep G (runSearch G s (ms.take t)) ms[t] := by
  rw [List.take_add_one, List.getElem?_eq_getElem ht, runSearch_append]
  rfl

theorem card_le_searchCost_take (s : SearchState V) (ms : List (SearchMove V)) (t : ℕ) :
    (runSearch G s (ms.take t)).guards.card ≤ searchCost G s ms := by
  induction ms generalizing s t with
  | nil => simpa [runSearch] using card_le_searchCost s []
  | cons m ms ih =>
    cases t with
    | zero => exact card_le_searchCost s _
    | succ t => exact (ih (searchStep G s m) t).trans (le_max_right _ _)

theorem noRecontamination_take {s : SearchState V} {ms : List (SearchMove V)}
    (h : NoRecontamination G s ms) {t : ℕ} (ht : t < ms.length) :
    (runSearch G s (ms.take (t + 1))).contaminated ⊆
      (runSearch G s (ms.take t)).contaminated := by
  induction ms generalizing s t with
  | nil => simp at ht
  | cons m ms ih =>
    cases t with
    | zero => exact h.1
    | succ t =>
      exact ih h.2 (by simpa using ht)

end Basic

/-! ### From a monotone strategy to a layout -/

section Lower

/-- **The lower half of [10] Theorem 4.1, monotone game.** A recontamination-free
strategy with at most `k` searchers clearing a graph with an edge gives
`vs(G) + 1 ≤ k`: order the vertices by the time from which no contaminated
edge touches them. -/
theorem vertexSeparation_add_one_le_of_monotone {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) {k : ℕ}
    {ms : List (SearchMove V)} (h : IsMonotoneNodeSearch G k ms) :
    vertexSeparation G + 1 ≤ k := by
  obtain ⟨⟨hclr, hcost⟩, hmono⟩ := h
  set L := ms.length with hL
  let st : ℕ → SearchState V := fun t => runSearch G (searchInit G) (ms.take t)
  let Clear : V → ℕ → Prop := fun v t => ∀ e ∈ (st t).contaminated, v ∉ e
  have hstL : st L = runSearch G (searchInit G) ms := by
    simp only [st, hL, List.take_length]
  have hClearL : ∀ v, Clear v L := by
    intro v e he
    rw [hstL, hclr] at he
    exact absurd he (Set.notMem_empty e)
  let τ : V → ℕ := fun v => sInf {t | Clear v t}
  have hτmem : ∀ v, Clear v (τ v) := fun v => Nat.sInf_mem (s := {t | Clear v t}) ⟨L, hClearL v⟩
  have hτL : ∀ v, τ v ≤ L := fun v => Nat.sInf_le (hClearL v)
  have hτmin : ∀ v t, t < τ v → ¬ Clear v t := fun v t ht => Nat.notMem_of_lt_sInf ht
  -- the contaminated sets decrease
  have hanti : ∀ t t', t ≤ t' → t' ≤ L → (st t').contaminated ⊆ (st t).contaminated := by
    intro t t' htt'
    induction t', htt' using Nat.le_induction with
    | base => exact fun _ => subset_rfl
    | succ t' _ ih =>
      intro hle
      exact (noRecontamination_take hmono (by omega)).trans (ih (by omega))
  have hClear_after : ∀ v t, τ v ≤ t → t ≤ L → Clear v t :=
    fun v t hvt htL e he => hτmem v e (hanti _ _ hvt htL he)
  have hclosed : ∀ t, IsClosed (G := G) (st t) :=
    fun t => isClosed_runSearch isClosed_init _
  have hcard : ∀ t, (st t).guards.card ≤ k :=
    fun t => (card_le_searchCost_take _ _ t).trans hcost
  -- a vertex with a neighbour is not clear at the start
  have hpos : ∀ v w, G.Adj v w → 0 < τ v := by
    intro v w hvw
    by_contra h0
    have h0' : τ v = 0 := by omega
    have := hτmem v
    rw [h0'] at this
    exact this s(v, w) (by simpa [st, runSearch, searchInit] using hvw) (Sym2.mem_mk_left _ _)
  -- at the time a vertex becomes clear, it carries a searcher
  have hlast : ∀ v, 0 < τ v → v ∈ (st (τ v)).guards := by
    intro v hv
    obtain ⟨t, htv⟩ : ∃ t, τ v = t + 1 := ⟨τ v - 1, by omega⟩
    have htL : t < ms.length := by have := hτL v; omega
    obtain ⟨e, he, hve⟩ : ∃ e ∈ (st t).contaminated, v ∈ e := by
      by_contra hne
      push Not at hne
      exact hτmin v t (by omega) hne
    have hstep : st (t + 1) = searchStep G (st t) ms[t] :=
      runSearch_take_succ (G := G) (searchInit G) ms htL
    rw [htv]
    by_contra hvS
    have hng : ¬ Guarded (st (t + 1)).guards e := fun hg => hvS (hg v hve)
    rw [hstep] at hng
    have h1 := mem_step_of_mem he hng
    rw [← hstep, ← htv] at h1
    exact hτmem v e h1 hve
  -- a later neighbour of a clear vertex carries a searcher
  have hguard : ∀ u w t, G.Adj u w → τ u ≤ t → t ≤ τ w → 0 < t →
      w ∈ (st t).guards := by
    intro u w t huw hut htw ht
    rcases Nat.eq_or_lt_of_le htw with heq | hlt
    · rw [heq]
      exact hlast w (by omega)
    · obtain ⟨f, hf, hwf⟩ : ∃ f ∈ (st t).contaminated, w ∈ f := by
        by_contra hne
        push Not at hne
        exact hτmin w t hlt hne
      by_contra hwS
      have := hclosed t s(u, w) (G.mem_edgeSet.mpr huw) f hf w (Sym2.mem_mk_right _ _) w hwf
        hwS Relation.ReflTransGen.refl
      exact hClear_after u t hut (by have := hτL w; omega) _ this (Sym2.mem_mk_left _ _)
  -- the layout
  obtain ⟨σ, hσ⟩ := exists_layout_sorted τ
  have hk1 : 1 ≤ k := by
    have h1 := hlast u₀ (hpos u₀ v₀ h₀)
    have := hcard (τ u₀)
    have : 0 < (st (τ u₀)).guards.card := Finset.card_pos.mpr ⟨u₀, h1⟩
    omega
  have hvs : vertexSepOfLayout G σ ≤ k - 1 := by
    rw [vertexSepOfLayout_le_iff]
    intro i hi
    rcases (activeSuffix G σ i).eq_empty_or_nonempty with hemp | ⟨w₀, hw₀⟩
    · unfold vertexSepAt
      rw [hemp, Finset.card_empty]
      exact Nat.zero_le _
    · set v := σ.symm ⟨i, hi⟩ with hv
      have hσv : (σ v).val = i := by simp [hv]
      have hpre : ∀ u, (σ u).val ≤ i → τ u ≤ τ v := by
        intro u hu
        by_contra hlt
        have := hσ v u (by omega)
        omega
      have hsuf : ∀ w, i < (σ w).val → τ v ≤ τ w := by
        intro w hw
        by_contra hlt
        have := hσ w v (by omega)
        omega
      obtain ⟨-, u₁, hu₁, hu₁w₀⟩ := (mem_activeSuffix_iff G σ i w₀).mp hw₀
      rw [mem_prefixSet_iff] at hu₁
      have htpos : 0 < τ v := lt_of_lt_of_le (hpos u₁ w₀ hu₁w₀) (hpre u₁ hu₁)
      have hsub : insert v (activeSuffix G σ i) ⊆ (st (τ v)).guards := by
        intro w hw
        rcases Finset.mem_insert.mp hw with hwv | hw
        · rw [hwv]
          exact hlast v htpos
        · obtain ⟨hwi, u, hu, huw⟩ := (mem_activeSuffix_iff G σ i w).mp hw
          rw [mem_prefixSet_iff] at hu
          exact hguard u w (τ v) huw (hpre u hu) (hsuf w hwi) htpos
      have hvn : v ∉ activeSuffix G σ i := by
        rw [mem_activeSuffix_iff]
        omega
      have := (Finset.card_le_card hsub).trans (hcard (τ v))
      rw [Finset.card_insert_of_notMem hvn] at this
      unfold vertexSepAt
      omega
  have := vertexSeparation_le_vertexSepOfLayout G σ
  omega

end Lower

/-! ### The shack process is a monotone strategy -/

section Upper

/-- Step `i` of Kornai & Tuza's shack process as moves of the search game:
place `vᵢ`, then delete the searcher of every vertex moved to the OM at step
`i` (`MovedAt`). A vertex already deleted is deleted again, which changes
nothing. -/
noncomputable def shackPhase (σ : LinearLayout V) (i : ℕ) : List (SearchMove V) :=
  if h : i < Fintype.card V then
    .place (σ.symm ⟨i, h⟩) :: ((Finset.univ.filter (MovedAt G σ i)).toList.map .remove)
  else []

/-- The shack process as a search strategy. -/
noncomputable def shackStrategy (σ : LinearLayout V) : List (SearchMove V) :=
  (List.range (Fintype.card V)).flatMap (shackPhase G σ)

/-- The searchers between phases: vertices before position `i` with a
neighbour at `i` or later. -/
def shackGuards (σ : LinearLayout V) (i : ℕ) : Finset V :=
  Finset.univ.filter fun v => (σ v).val < i ∧ ∃ u, G.Adj v u ∧ i ≤ (σ u).val

/-- The edges that may still be contaminated before phase `i`. -/
def notYetCleared (σ : LinearLayout V) (i : ℕ) : Set (Sym2 V) :=
  {e | ∃ x ∈ e, i ≤ (σ x).val}

theorem insert_shackGuards (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V) :
    insert (σ.symm ⟨i, hi⟩) (shackGuards G σ i) = shackAfterPut G σ i := by
  ext v
  rw [Finset.mem_insert, mem_shackAfterPut_iff]
  simp only [shackGuards, Finset.mem_filter, Finset.mem_univ, true_and]
  constructor
  · rintro (rfl | ⟨hv, u, huv, hu⟩)
    · simp
    · exact ⟨hv.le, u, Or.inr huv, hu⟩
  · rintro ⟨hv, u, hu, hiu⟩
    rcases Nat.eq_or_lt_of_le hv with heq | hlt
    · left
      rw [Equiv.eq_symm_apply]
      exact Fin.ext heq
    · right
      rcases hu with rfl | huv
      · omega
      · exact ⟨hlt, u, huv, hiu⟩

theorem shackAfterPut_sdiff_moved (σ : LinearLayout V) (i : ℕ) :
    shackAfterPut G σ i \ Finset.univ.filter (MovedAt G σ i) = shackGuards G σ (i + 1) := by
  ext v
  rw [Finset.mem_sdiff, mem_shackAfterPut_iff]
  simp only [shackGuards, MovedAt, Finset.mem_filter, Finset.mem_univ, true_and, not_and,
    not_forall, not_le]
  constructor
  · rintro ⟨⟨hv, -⟩, hmv⟩
    obtain ⟨u, huv, hu⟩ := hmv hv
    exact ⟨by omega, u, huv, by omega⟩
  · rintro ⟨hv, u, huv, hu⟩
    exact ⟨⟨by omega, u, Or.inr huv, by omega⟩, fun _ => ⟨u, huv, by omega⟩⟩

/-- The deletions of a phase: none recontaminates, and none adds a searcher. -/
theorem removals_spec (σ : LinearLayout V) (i : ℕ) (P : Finset V) (l : List V)
    (hl : ∀ u ∈ l, MovedAt G σ i u) (s : SearchState V) (hsP : s.guards ⊆ P)
    (hsH : s.contaminated ⊆ notYetCleared σ (i + 1)) (hsE : s.contaminated ⊆ G.edgeSet)
    (hs : IsClosed (G := G) s) :
    NoRecontamination G s (l.map .remove) ∧ searchCost G s (l.map .remove) ≤ P.card ∧
      (runSearch G s (l.map .remove)).guards = s.guards \ l.toFinset ∧
      (runSearch G s (l.map .remove)).contaminated ⊆ s.contaminated := by
  induction l generalizing s with
  | nil =>
    exact ⟨trivial, Finset.card_le_card hsP, by simp [runSearch], by simp [runSearch]⟩
  | cons u l ih =>
    have hu := hl u (List.mem_cons_self ..)
    have hv : ∀ e ∈ s.contaminated, u ∉ e := by
      intro e he hue
      obtain ⟨x, hx, hix⟩ := hsH he
      rcases eq_or_adj_of_mem_edgeSet (hsE he) hue hx with rfl | hux
      · have := hu.1; omega
      · have := hu.2 x hux; omega
    have hsub := step_remove_subset hs u hv
    set s' := searchStep G s (.remove u) with hs'
    have hg' : s'.guards = s.guards.erase u := rfl
    obtain ⟨h1, h2, h3, h4⟩ := ih (fun w hw => hl w (List.mem_cons_of_mem _ hw)) s'
      (hg' ▸ (Finset.erase_subset _ _).trans hsP) (hsub.trans hsH) (hsub.trans hsE)
      (isClosed_step s _)
    refine ⟨⟨hsub, h1⟩, max_le (Finset.card_le_card hsP) h2, ?_, h4.trans hsub⟩
    change (runSearch G s' (l.map .remove)).guards = _
    rw [h3, hg']
    ext w
    simp only [Finset.mem_sdiff, Finset.mem_erase, List.mem_toFinset, List.mem_cons]
    tauto

/-- One phase of the shack strategy. -/
theorem shackPhase_spec (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V)
    (s : SearchState V) (hsG : s.guards = shackGuards G σ i)
    (hsH : s.contaminated ⊆ notYetCleared σ i) (hsE : s.contaminated ⊆ G.edgeSet)
    (hs : IsClosed (G := G) s) :
    NoRecontamination G s (shackPhase G σ i) ∧
      searchCost G s (shackPhase G σ i) ≤ (shackAfterPut G σ i).card ∧
      (runSearch G s (shackPhase G σ i)).guards = shackGuards G σ (i + 1) ∧
      (runSearch G s (shackPhase G σ i)).contaminated ⊆ notYetCleared σ (i + 1) := by
  set v := σ.symm ⟨i, hi⟩ with hv
  have hσv : (σ v).val = i := by simp [hv]
  set s₁ := searchStep G s (.place v) with hs₁
  have hg₁ : s₁.guards = shackAfterPut G σ i := by
    change insert v s.guards = _
    rw [hsG, hv, insert_shackGuards]
  have hsub₁ := step_place_subset hs v
  have hH₁ : s₁.contaminated ⊆ notYetCleared σ (i + 1) := by
    intro e he
    have hng := not_guarded_of_mem_step he
    obtain ⟨x, hx, hix⟩ := hsH (hsub₁ he)
    by_contra hall
    simp only [notYetCleared, Set.mem_ofPred_eq, not_exists, not_and, not_le] at hall
    apply hng
    intro z hz
    change z ∈ insert v s.guards
    rw [hsG, Finset.mem_insert]
    have hzi := hall z hz
    rcases Nat.lt_succ_iff_lt_or_eq.mp hzi with hlt | heq
    · right
      have hxz : z ≠ x := by
        rintro rfl
        omega
      rcases eq_or_adj_of_mem_edgeSet (hsE (hsub₁ he)) hz hx with h | hzx
      · exact absurd h hxz
      · simp only [shackGuards, Finset.mem_filter, Finset.mem_univ, true_and]
        exact ⟨hlt, x, hzx, hix⟩
    · left
      rw [hv, Equiv.eq_symm_apply]
      exact Fin.ext heq
  obtain ⟨h1, h2, h3, h4⟩ := removals_spec G σ i (shackAfterPut G σ i)
    (Finset.univ.filter (MovedAt G σ i)).toList
    (fun u hu => by simpa using hu) s₁ hg₁.le hH₁ (hsub₁.trans hsE) (isClosed_step s _)
  simp only [shackPhase, hi, ↓reduceDIte]
  refine ⟨⟨hsub₁, h1⟩, ?_, ?_, h4.trans hH₁⟩
  · refine max_le ?_ h2
    rw [hsG, ← insert_shackGuards G σ hi]
    exact Finset.card_le_card (Finset.subset_insert _ _)
  · change (runSearch G s₁ _).guards = _
    rw [h3, hg₁, Finset.toList_toFinset, shackAfterPut_sdiff_moved]

/-- **The upper half of [10] Theorem 4.1, monotone game.** The shack process of
an in-sequence `σ` is a recontamination-free strategy clearing every edge with
`ν(σ)` searchers. -/
theorem shackStrategy_isMonotone (σ : LinearLayout V) :
    IsMonotoneNodeSearch G (inNarrowness G σ) (shackStrategy G σ) := by
  have key : ∀ i ≤ Fintype.card V,
      let r := runSearch G (searchInit G) ((List.range i).flatMap (shackPhase G σ))
      r.guards = shackGuards G σ i ∧ r.contaminated ⊆ notYetCleared σ i ∧
        NoRecontamination G (searchInit G) ((List.range i).flatMap (shackPhase G σ)) ∧
        searchCost G (searchInit G) ((List.range i).flatMap (shackPhase G σ)) ≤
          inNarrowness G σ := by
    intro i hi
    induction i with
    | zero =>
      refine ⟨?_, ?_, trivial, ?_⟩
      · ext v
        simp [runSearch, searchInit, shackGuards]
      · intro e he
        induction e using Sym2.ind with
        | h a b => exact ⟨a, Sym2.mem_mk_left _ _, Nat.zero_le _⟩
      · simp [searchCost, searchInit]
    | succ i ih =>
      obtain ⟨hg, hH, hm, hc⟩ := ih (by omega)
      set pre := (List.range i).flatMap (shackPhase G σ) with hpre
      have hsplit : (List.range (i + 1)).flatMap (shackPhase G σ) = pre ++ shackPhase G σ i := by
        rw [List.range_succ, List.flatMap_append]
        simp [hpre]
      have hE := contaminated_runSearch_subset_edgeSet (G := G)
        (s := searchInit G) (fun _ h => h) pre
      obtain ⟨p1, p2, p3, p4⟩ := shackPhase_spec G σ (by omega) _ hg hH hE
        (isClosed_runSearch isClosed_init pre)
      simp only [hsplit, runSearch_append, searchCost_append, noRecontamination_append]
      exact ⟨p3, p4, ⟨hm, p1⟩, max_le hc (p2.trans (card_shackAfterPut_le_inNarrowness G σ i
        (by omega)))⟩
  obtain ⟨-, hH, hm, hc⟩ := key (Fintype.card V) le_rfl
  refine ⟨⟨?_, hc⟩, hm⟩
  apply Set.eq_empty_of_subset_empty
  intro e he
  obtain ⟨x, -, hx⟩ := hH he
  exact absurd (σ x).isLt (by omega)

end Upper

/-! ### Theorem 4.1 for the monotone game -/

section Main

theorem monotoneNodeSearch_le_inNarrowness (σ : LinearLayout V) :
    monotoneNodeSearch G ≤ inNarrowness G σ :=
  Nat.sInf_le ⟨shackStrategy G σ, shackStrategy_isMonotone G σ⟩

/-- **Kirousis & Papadimitriou (1986), Theorem 4.1, for the monotone game.**
For every graph with at least one edge, `mns(G) = vs(G) + 1`. -/
theorem monotoneNodeSearch_eq_vertexSeparation_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    monotoneNodeSearch G = vertexSeparation G + 1 := by
  have : Nonempty V := ⟨u₀⟩
  apply le_antisymm
  · obtain ⟨σ₀, hσ₀⟩ := exists_layout_vertexSeparation G
    have := monotoneNodeSearch_le_inNarrowness G (reverseLayout σ₀)
    rwa [inNarrowness_eq_vertexSepOfLayout_reverse, reverseLayout_reverseLayout, hσ₀] at this
  · obtain ⟨ms, hms⟩ := Nat.sInf_mem (s := {k | ∃ ms, IsMonotoneNodeSearch G k ms})
      ⟨_, Fintype.equivFin V |> shackStrategy G, shackStrategy_isMonotone G _⟩
    exact vertexSeparation_add_one_le_of_monotone G h₀ hms

/-- With Kinnersley's theorem: `mns(G) = pw(G) + 1` for every graph with an edge. -/
theorem monotoneNodeSearch_eq_pathwidth_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    monotoneNodeSearch G = pathwidth G + 1 := by
  rw [monotoneNodeSearch_eq_vertexSeparation_add_one G h₀, vertexSeparation_eq_pathwidth]

/-- A monotone strategy is a strategy. -/
theorem nodeSearch_le_monotoneNodeSearch : nodeSearch G ≤ monotoneNodeSearch G := by
  obtain ⟨ms, hms⟩ := Nat.sInf_mem (s := {k | ∃ ms, IsMonotoneNodeSearch G k ms})
    ⟨_, shackStrategy G (Fintype.equivFin V), shackStrategy_isMonotone G _⟩
  exact Nat.sInf_le ⟨ms, hms.1⟩

/-- The half of Theorem 4.1 that needs no monotonicity: `ns(G) ≤ vs(G) + 1`. -/
theorem nodeSearch_le_vertexSeparation_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G ≤ vertexSeparation G + 1 :=
  (nodeSearch_le_monotoneNodeSearch G).trans
    (monotoneNodeSearch_eq_vertexSeparation_add_one G h₀).le

/-- Granting monotonicity ([10] Thm 2.3), the full theorem follows. -/
theorem nodeSearch_eq_vertexSeparation_add_one_of_monotonicity
    (hmono : NodeSearchMonotonicity G) {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G = vertexSeparation G + 1 := by
  rw [hmono, monotoneNodeSearch_eq_vertexSeparation_add_one G h₀]

/-! ### Edgeless graphs -/

/-- On an edgeless graph the empty strategy clears everything: `mns = 0`, while
`vs + 1 = 1` as soon as there is a vertex. -/
theorem monotoneNodeSearch_of_edgeless (h : ∀ u v, ¬ G.Adj u v) :
    monotoneNodeSearch G = 0 := by
  apply Nat.eq_zero_of_le_zero
  refine Nat.sInf_le ⟨[], ⟨?_, ?_⟩, trivial⟩
  · ext e
    induction e using Sym2.ind with
    | h a b => simpa [runSearch, searchInit] using h a b
  · simp [searchCost, searchInit]

theorem nodeSearch_of_edgeless (h : ∀ u v, ¬ G.Adj u v) : nodeSearch G = 0 :=
  Nat.eq_zero_of_le_zero ((nodeSearch_le_monotoneNodeSearch G).trans
    (monotoneNodeSearch_of_edgeless G h).le)

/-- The exception is real: on a nonempty edgeless graph `mns = 0 ≠ vs + 1`. -/
theorem monotoneNodeSearch_ne_vertexSeparation_add_one_of_edgeless [Nonempty V]
    (h : ∀ u v, ¬ G.Adj u v) : monotoneNodeSearch G ≠ vertexSeparation G + 1 := by
  rw [monotoneNodeSearch_of_edgeless G h]
  omega

end Main

end Complex

end MOSPFormalization
