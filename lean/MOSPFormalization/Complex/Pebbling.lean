/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Progressive black-white pebbling and Lengauer's Theorem 3

Source: Lengauer, *Black-white pebbles and graph separation*, Acta Informatica 16
(1981) 465–475 (`literature/lengauer_1981_black_white_pebbles_graph_separation.pdf`),
§1–2. Census and brute-force check: `paper2/equivalences.md`, section "Pebbling",
P.1–P.7 (loop0006 items 01–02).

## The game, as Lengauer states it (pp. 466–467)

BWP on a dag: "(i) All vertices start out pebble-free. (ii) All vertices end up
pebble-free. (iii) Each vertex receives and loses a pebble at least once. (iv) A white
pebble can be placed on a pebble-free vertex at any time. (v) A black pebble can be
removed from a vertex at any time. (vi) A white pebble on a vertex v may be turned black
if all of the immediate predecessors of v are pebbled." The progressive game PBWP
replaces (iii) by "(iii') Each vertex receives and loses a pebble *exactly* once". An
instance `(G, K)`, `K` a positive integer, is positive if `G` can be pebbled with at
most `K` pebbles at any instant.

Under (iii') a vertex's history is forced: it receives a white pebble (the only way to
receive one, rule (iv)), may turn it black (vi), and loses it (only black pebbles are
removed, (v)), each exactly once. So a position is a phase per vertex
(`PebblePhase`: `fresh`, `white`, `black`, `done`), a move is `place`, `turn` or `remove`
(`PebbleMove`) with the legality of rules (iv)–(vi) (`PebbleMove.Legal`), and
`PebblesWithin D K` says that the all-`done` position is reachable from the all-`fresh`
one through positions with at most `K` pebbles. `IsPositivePBWP D K` adds `0 < K`, and
`pbw D` is the least `K` (Kirousis & Papadimitriou's `pbw`). This is the same machine
as `progressive_bw_within(d, k, rules="lengauer")` in `paper2/complex_check.py`, which
decided every statement of P.5; `replay_progressive` there replays single plays under
exactly these rules. The game is defined on any `Digraph`; Lengauer's dags are the
acyclic ones, and `G_d` is acyclic (`lengauerD_no_path_two`).

`G_d` (Def. 1b, p. 469): `V_d = V ∪ E`, arcs `v → {v, w}` and `w → {v, w}` for every
edge; the edges of `G` are discarded (`lengauerD`, on `V ⊕ G.edgeSet`).

## What is proved

* `pebblesWithin_lengauerD_iff`: **for every graph and every `K ≥ 0`,
  `PebblesWithin (G_d) (K + 2) ↔ vs(G) ≤ K`.** This is Theorem 3 read with `vs`; it needs
  no hypothesis.
* `isPositiveVSG_iff_isPositivePBWP_lengauerD`: **Theorem 3 as stated** (p. 472),
  "`(G, K)` of VSG is positive iff `(G_d, K + 2)` of PBWP is positive", for every positive
  `K` (Lengauer's instances), with VSG the game of `EdgeSeparation.lean`.
* `pbw_lengauerD`, `pbw_lengauerD_eq_pathwidth`, `pbw_lengauerD_eq_vsg`: **`pbw(G_d) =
  vs(G) + 2 = pw(G) + 2 = VSG(G) + 2` for every graph with an edge.**
* `pbw_lengauerD_of_edgeless`: the edge case item 02 found: **`pbw(G_d) = 1` on an
  edgeless graph with a vertex**, where `vs + 2 = 2`; the number form needs an edge.
* By-products: `three_le_of_pebblesWithin` (an edge forces three pebbles),
  `one_le_of_pebblesWithin`, `exists_seq_of_reflTransGen`, `exists_layout_of_injective`.

## The proof, and how it differs from Lengauer's

Lengauer derives Theorem 3 from Theorem 2 (PBWP on `D` vs VSG on `D_u`) applied to the
depth-one dag `G_d`, followed by Theorem 4 (`isPositiveVSG_iff_triangleGraph`). This
file proves it directly on `G_d`, which avoids Theorem 2's four-step simulation, and
uses the development's outer-boundary convention for vs (`activeSuffix`: later
vertices with a neighbour at or before the cut), which is the natural one for pebbling.

* (⇐, `pebblesWithin_of_layout`) Clear the vertices of `G` in layout order. To clear
  `v`: blacken the pebble-free vertices of `N[v]` (place, turn; sources turn freely), then
  place, turn and remove every edge vertex at `v` not yet cleared (both ends are black),
  then remove `v`. Between steps the black vertices are exactly the active suffix
  (`layoutPos`); during a step at most the new active suffix, `v`, and one edge vertex
  carry pebbles, so `vs + 2`, and `1` on an edgeless graph.
* (⇒, `vertexSeparation_le_of_pebblesWithin`) Lay the vertices of `G` out in the order they
  lose their pebble (`exists_layout_of_injective`). At a cut, let `S` be the vertices
  cleared so far and `B` the active suffix. An edge `{a, b}` with `a ∈ S` turns before
  `a` is cleared, with `b` pebbled, and `b ∉ S` keeps that pebble past the cut. Take the
  cut edge `e = {a, b}` that turns *last* (`outerBoundary_card_le`): at that instant `e`,
  `a`, and every vertex of `B` carry pebbles, and these are `|B| + 2` distinct vertices
  of `G_d`. Hence `|B| ≤ K`.

The Python replay `python -m paper2.complex_check --pebbling-strategy` runs both
constructions on every layout of every graph on at most 7 vertices (5,378,453 plays): the
(⇐) play is legal and within the bound, its removal layout satisfies the (⇒) bound, and
the best layout attains `vs + 2` (`1` if edgeless), with zero failures.
-/

import MOSPFormalization.Complex.EdgeSeparation
import Mathlib.Combinatorics.Digraph.Basic

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace MOSPFormalization

namespace Complex

open Finset Function

/-! ### The progressive black-white pebble game -/

section Game

/-- The four phases of a vertex in a progressive play: never pebbled, carrying a white
pebble, carrying a black pebble, and pebbled and cleared (rule (iii'): each vertex
receives and loses a pebble exactly once). -/
inductive PebblePhase
  | fresh
  | white
  | black
  | done
  deriving DecidableEq

namespace PebblePhase

/-- A vertex is *pebbled* when it carries a pebble of either colour. -/
def Pebbled (p : PebblePhase) : Prop := p = white ∨ p = black

instance (p : PebblePhase) : Decidable p.Pebbled := inferInstanceAs (Decidable (_ ∨ _))

/-- The phases in the order a vertex passes through them. -/
def rank : PebblePhase → ℕ
  | fresh => 0
  | white => 1
  | black => 2
  | done => 3

@[simp] theorem rank_fresh : fresh.rank = 0 := rfl
@[simp] theorem rank_white : white.rank = 1 := rfl
@[simp] theorem rank_black : black.rank = 2 := rfl
@[simp] theorem rank_done : done.rank = 3 := rfl

theorem pebbled_iff_rank (p : PebblePhase) : p.Pebbled ↔ 1 ≤ p.rank ∧ p.rank ≤ 2 := by
  cases p <;> simp [Pebbled, rank]

theorem rank_le_three (p : PebblePhase) : p.rank ≤ 3 := by cases p <;> simp [rank]

theorem eq_done_iff_rank (p : PebblePhase) : p = done ↔ p.rank = 3 := by
  cases p <;> simp [rank]

end PebblePhase

open PebblePhase

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- A position of the game: the phase of every vertex. -/
abbrev PebblePosition (α : Type*) := α → PebblePhase

/-- The three moves: place a white pebble (rule (iv)), turn a white pebble black
(rule (vi)), remove a black pebble (rule (v)). -/
inductive PebbleMove (α : Type*)
  | place (x : α)
  | turn (x : α)
  | remove (x : α)

namespace PebbleMove

/-- The vertex a move acts on. -/
def target : PebbleMove α → α
  | place x => x
  | turn x => x
  | remove x => x

/-- The phase the target is in after the move. -/
def result : PebbleMove α → PebblePhase
  | place _ => white
  | turn _ => black
  | remove _ => done

/-- When a move is legal in position `P` on the dag `D` (arcs `u → v`, `u` an immediate
predecessor of `v`). Progressiveness is built in: a white pebble can only go on a vertex
that has never been pebbled, and a black one, once removed, never returns. -/
def Legal (D : Digraph α) (P : PebblePosition α) : PebbleMove α → Prop
  | place x => P x = fresh
  | turn x => P x = white ∧ ∀ y, D.Adj y x → (P y).Pebbled
  | remove x => P x = black

/-- The position after the move. -/
def apply (m : PebbleMove α) (P : PebblePosition α) : PebblePosition α :=
  Function.update P m.target m.result

end PebbleMove

/-- The number of pebbles on the dag. -/
def numPebbles (P : PebblePosition α) : ℕ := (univ.filter fun x => (P x).Pebbled).card

/-- One legal move, after which at most `K` pebbles are on the dag. -/
def PebbleStep (D : Digraph α) (K : ℕ) (P Q : PebblePosition α) : Prop :=
  ∃ m : PebbleMove α, m.Legal D P ∧ Q = m.apply P ∧ numPebbles Q ≤ K

/-- `D` can be pebbled progressively with at most `K` pebbles: from the pebble-free start
(rule (i)) to the position in which every vertex has received and lost its one pebble
(rules (ii), (iii')), never more than `K` pebbles at any instant. -/
def PebblesWithin (D : Digraph α) (K : ℕ) : Prop :=
  Relation.ReflTransGen (PebbleStep D K) (fun _ => fresh) (fun _ => done)

/-- Lengauer p. 466–467: `(D, K)`, `K` a *positive* integer, is a positive instance of
PBWP. -/
def IsPositivePBWP (D : Digraph α) (K : ℕ) : Prop := 0 < K ∧ PebblesWithin D K

/-- The progressive black-white pebble demand `pbw(D)` (Kirousis & Papadimitriou p. 206). -/
noncomputable def pbw (D : Digraph α) : ℕ := sInf {K | PebblesWithin D K}

theorem PebbleStep.reflTransGen_mono {D : Digraph α} {K K' : ℕ} (hK : K ≤ K')
    {P Q : PebblePosition α} (h : Relation.ReflTransGen (PebbleStep D K) P Q) :
    Relation.ReflTransGen (PebbleStep D K') P Q := by
  induction h with
  | refl => exact .refl
  | tail _ hs ih =>
    obtain ⟨m, hm, hQ, hc⟩ := hs
    exact ih.tail ⟨m, hm, hQ, hc.trans hK⟩

theorem PebblesWithin.mono {D : Digraph α} {K K' : ℕ} (h : PebblesWithin D K) (hK : K ≤ K') :
    PebblesWithin D K' :=
  PebbleStep.reflTransGen_mono hK h

/-- A play as a sequence of positions indexed by time. -/
theorem exists_seq_of_reflTransGen {β : Type*} {r : β → β → Prop} {a b : β}
    (h : Relation.ReflTransGen r a b) :
    ∃ (T : ℕ) (P : ℕ → β), P 0 = a ∧ P T = b ∧ ∀ i < T, r (P i) (P (i + 1)) := by
  induction h with
  | refl => exact ⟨0, fun _ => a, rfl, rfl, fun i hi => absurd hi (Nat.not_lt_zero _)⟩
  | tail _ hbc ih =>
    obtain ⟨T, P, h0, hT, hs⟩ := ih
    rename_i b' c _
    refine ⟨T + 1, fun i => if i ≤ T then P i else c, by simp [h0], by simp, ?_⟩
    intro i hi
    by_cases hiT : i < T
    · simpa [hiT.le, Nat.succ_le_of_lt hiT] using hs i hiT
    · have : i = T := by omega
      subst this
      simpa [hT] using hbc

end Game

/-! ### What a play implies -/

section Plays

open PebblePhase

variable {α : Type*} [Fintype α] [DecidableEq α] {D : Digraph α} {K : ℕ}

theorem PebbleStep.rank_le {P Q : PebblePosition α} (h : PebbleStep D K P Q) (x : α) :
    (P x).rank ≤ (Q x).rank := by
  obtain ⟨m, hm, rfl, -⟩ := h
  unfold PebbleMove.apply
  by_cases hx : x = m.target
  · subst hx
    rw [Function.update_self]
    cases m <;> simp_all [PebbleMove.Legal, PebbleMove.result, PebbleMove.target]
  · rw [Function.update_of_ne hx]

/-- The only move that takes a vertex from unturned to turned is its turn, and it needs
every immediate predecessor pebbled. -/
theorem PebbleStep.of_turned {P Q : PebblePosition α} (h : PebbleStep D K P Q) {x : α}
    (hP : (P x).rank ≤ 1) (hQ : 2 ≤ (Q x).rank) :
    P x = white ∧ ∀ y, D.Adj y x → (P y).Pebbled := by
  obtain ⟨m, hm, rfl, -⟩ := h
  unfold PebbleMove.apply at hQ
  by_cases hx : x = m.target
  · subst hx
    rw [Function.update_self] at hQ
    cases m with
    | place y => simp [PebbleMove.result] at hQ
    | turn y => exact hm
    | remove y =>
      simp only [PebbleMove.Legal] at hm
      simp [PebbleMove.target, hm] at hP
  · rw [Function.update_of_ne hx] at hQ; omega

theorem PebbleStep.numPebbles_le {P Q : PebblePosition α} (h : PebbleStep D K P Q) :
    numPebbles Q ≤ K := by
  obtain ⟨_, _, rfl, hc⟩ := h; exact hc

variable {T : ℕ} {P : ℕ → PebblePosition α}

theorem seq_rank_mono (hs : ∀ i < T, PebbleStep D K (P i) (P (i + 1))) {i j : ℕ}
    (hij : i ≤ j) (hj : j ≤ T) (x : α) : (P i x).rank ≤ (P j x).rank := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ j _ ih => exact (ih (by omega)).trans ((hs j (by omega)).rank_le x)

/-- Every vertex that ends turned was turned at some time `i < T`, with its immediate
predecessors pebbled at that time. -/
theorem seq_exists_turn (hs : ∀ i < T, PebbleStep D K (P i) (P (i + 1))) {x : α}
    (h0 : (P 0 x).rank ≤ 1) (hT : 2 ≤ (P T x).rank) :
    ∃ i < T, (P i x).rank ≤ 1 ∧ P i x = white ∧ ∀ y, D.Adj y x → (P i y).Pebbled := by
  classical
  have hex : ∃ j, j ≤ T ∧ 2 ≤ (P j x).rank := ⟨T, le_rfl, hT⟩
  have hjT : Nat.find hex ≤ T := (Nat.find_spec hex).1
  have hj2 : 2 ≤ (P (Nat.find hex) x).rank := (Nat.find_spec hex).2
  have hj0 : Nat.find hex ≠ 0 := by intro h; rw [h] at hj2; omega
  obtain ⟨i, hi1⟩ : ∃ i, Nat.find hex = i + 1 := ⟨Nat.find hex - 1, by omega⟩
  have hi : (P i x).rank ≤ 1 := by
    by_contra hc
    exact Nat.find_min hex (show i < Nat.find hex by omega) ⟨by omega, by omega⟩
  rw [hi1] at hj2
  exact ⟨i, by omega, hi, (hs i (by omega)).of_turned hi hj2⟩

theorem seq_numPebbles_le (hs : ∀ i < T, PebbleStep D K (P i) (P (i + 1)))
    (h0 : P 0 = fun _ => fresh) {i : ℕ} (hi : i ≤ T) : numPebbles (P i) ≤ K := by
  rcases i with _ | i
  · rw [h0]; simp [numPebbles, Pebbled]
  · exact (hs i (by omega)).numPebbles_le

end Plays

/-! ### Lengauer's `G_d` -/

section Gd

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Lengauer's `G_d` (Def. 1b, p. 469): `V_d = V ∪ E`, with arcs `v → {v, w}` and
`w → {v, w}` for every edge `{v, w}`; the edges of `G` themselves are discarded. -/
def lengauerD : Digraph (V ⊕ G.edgeSet) where
  Adj a b := match a, b with
    | .inl v, .inr e => v ∈ (e : Sym2 V)
    | _, _ => False

variable {G}

@[simp] theorem lengauerD_adj_inl_inr {v : V} {e : G.edgeSet} :
    (lengauerD G).Adj (.inl v) (.inr e) ↔ v ∈ (e : Sym2 V) := Iff.rfl

@[simp] theorem lengauerD_not_adj_to_inl {a : V ⊕ G.edgeSet} {v : V} :
    ¬ (lengauerD G).Adj a (.inl v) := by
  rcases a with u | e <;> exact id

@[simp] theorem lengauerD_not_adj_from_inr {e : G.edgeSet} {b : V ⊕ G.edgeSet} :
    ¬ (lengauerD G).Adj (.inr e) b := by
  rcases b with u | f <;> exact id

variable (G)

/-- `G_d` is a dag of depth one: it has no directed path of length two, hence no cycle. -/
theorem lengauerD_no_path_two (a b c : V ⊕ G.edgeSet) :
    ¬ ((lengauerD G).Adj a b ∧ (lengauerD G).Adj b c) := by
  rintro ⟨hab, hbc⟩
  rcases b with v | e
  · exact lengauerD_not_adj_to_inl hab
  · exact lengauerD_not_adj_from_inr hbc

end Gd

/-! ### The layout a play induces -/

section Lower

open PebblePhase

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]

/-- The vertices outside `S` with a neighbour in `S`: the active suffix of a layout whose
prefix is `S`. -/
def outerBoundary (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Finset V :=
  univ.filter fun w => w ∉ S ∧ ∃ u ∈ S, G.Adj u w

theorem mem_outerBoundary {S : Finset V} {w : V} :
    w ∈ outerBoundary G S ↔ w ∉ S ∧ ∃ u ∈ S, G.Adj u w := by
  simp [outerBoundary]

theorem PebbleStep.eq_target {α : Type*} [Fintype α] [DecidableEq α] {D : Digraph α} {K : ℕ}
    {P Q : PebblePosition α} (h : PebbleStep D K P Q) {x y : α} (hx : P x ≠ Q x)
    (hy : P y ≠ Q y) : x = y := by
  obtain ⟨m, -, rfl, -⟩ := h
  unfold PebbleMove.apply at hx hy
  have h1 : x = m.target := by
    by_contra h; exact hx (Function.update_of_ne h _ _).symm
  have h2 : y = m.target := by
    by_contra h; exact hy (Function.update_of_ne h _ _).symm
  rw [h1, h2]

variable {K T : ℕ} {P : ℕ → PebblePosition (V ⊕ G.edgeSet)}

/-- The heart of Theorem 3 (⇒). Let `S` be the vertices of `G` cleared by time `t`. Take the
edge between `S` and the rest that is turned last; when it turns, it, its endpoint in `S`,
and every vertex of the outer boundary of `S` carry pebbles. -/
theorem outerBoundary_card_le
    (hs : ∀ i < T, PebbleStep (lengauerD G) (K + 2) (P i) (P (i + 1)))
    (h0 : P 0 = fun _ => fresh) (hT : P T = fun _ => done)
    (hc : ∀ i ≤ T, numPebbles (P i) ≤ K + 2) {t : ℕ} (ht : t ≤ T) :
    (outerBoundary G (univ.filter fun v => P t (.inl v) = done)).card ≤ K := by
  classical
  set S := univ.filter fun v => P t (.inl v) = done with hS
  set B := outerBoundary G S with hB
  rcases B.eq_empty_or_nonempty with hBe | ⟨b₀, hb₀⟩
  · rw [hBe]; exact Nat.zero_le _
  -- turn times of all edge vertices
  have hturn : ∀ e : G.edgeSet, ∃ i < T, (P i (.inr e)).rank ≤ 1 ∧ P i (.inr e) = white ∧
      ∀ y, (lengauerD G).Adj y (.inr e) → (P i y).Pebbled := fun e =>
    seq_exists_turn hs (by rw [h0]; simp) (by rw [hT]; simp)
  choose τ hτT hτ1 hτw hτp using hturn
  have hmono := fun {i j} (hij : i ≤ j) (hj : j ≤ T) x => seq_rank_mono hs (P := P) hij hj x
  -- the cut edges
  set C : Finset G.edgeSet := univ.filter fun e => ∃ a ∈ S, ∃ b ∉ S, (e : Sym2 V) = s(a, b)
  obtain ⟨u₀, hu₀S, hu₀⟩ := (mem_outerBoundary.mp hb₀).2
  have hC : C.Nonempty := ⟨⟨s(u₀, b₀), hu₀⟩, by
    simp only [C, mem_filter, mem_univ, true_and]
    exact ⟨u₀, hu₀S, b₀, (mem_outerBoundary.mp hb₀).1, rfl⟩⟩
  obtain ⟨e, heC, hemax⟩ := C.exists_max_image τ hC
  obtain ⟨a, haS, b, hbS, hab⟩ := by simpa [C] using heC
  have hapeb : (P (τ e) (.inl a)).Pebbled :=
    hτp e _ (by simp [hab])
  have haS' : P t (.inl a) = done := by simpa [S] using haS
  -- the last turn happens before `t`
  have hτt : τ e < t := by
    by_contra hle
    have := hmono (not_lt.mp hle) (hτT e).le (.inl a)
    rw [haS'] at this
    have := (pebbled_iff_rank _).mp hapeb
    simp at *; omega
  -- every boundary vertex is pebbled at the last turn
  have hBpeb : ∀ w ∈ B, (P (τ e) (.inl w)).Pebbled := by
    intro w hw
    obtain ⟨hwS, u, huS, huw⟩ := mem_outerBoundary.mp hw
    set e' : G.edgeSet := ⟨s(u, w), huw⟩
    have he'C : e' ∈ C := by
      simp only [C, mem_filter, mem_univ, true_and]; exact ⟨u, huS, w, hwS, rfl⟩
    have hle := hemax e' he'C
    have h1 := (pebbled_iff_rank _).mp (hτp e' (.inl w) (by simp [e']))
    have h2 := hmono hle (hτT e).le (.inl w)
    have h3 := hmono hτt.le ht (.inl w)
    have h4 : (P t (.inl w)).rank ≠ 3 := by
      rw [Ne, ← eq_done_iff_rank]; simpa [S] using hwS
    have h5 := rank_le_three (P t (.inl w))
    rw [pebbled_iff_rank]; omega
  have hsub : insert (.inr e) (insert (.inl a) (B.map Embedding.inl)) ⊆
      univ.filter fun x => (P (τ e) x).Pebbled := by
    intro x hx
    simp only [mem_insert, mem_map, Embedding.inl_apply] at hx
    simp only [mem_filter, mem_univ, true_and]
    rcases hx with rfl | rfl | ⟨w, hw, rfl⟩
    · rw [hτw e]; exact Or.inl rfl
    · exact hapeb
    · exact hBpeb w hw
  have hcard := card_le_card hsub
  rw [card_insert_of_notMem (by simp), card_insert_of_notMem (by
    simp only [mem_map, Embedding.inl_apply, Sum.inl.injEq, not_exists, not_and]
    rintro w hw rfl; exact (mem_outerBoundary.mp hw).1 haS), card_map] at hcard
  have := hc (τ e) (hτT e).le
  unfold numPebbles at this
  omega

/-- A layout listing the vertices in increasing order of an injective key. -/
theorem exists_layout_of_injective {r : V → ℕ} (hr : Injective r) :
    ∃ σ : LinearLayout V, ∀ u v, σ u ≤ σ v ↔ r u ≤ r v := by
  classical
  set s := univ.image r
  have hs : s.card = Fintype.card V := by rw [card_image_of_injective _ hr, card_univ]
  set e := s.orderIsoOfFin hs
  let f : V → Fin (Fintype.card V) := fun v => e.symm ⟨r v, mem_image_of_mem r (mem_univ v)⟩
  have hf : Injective f := by
    intro u v h
    have := congrArg Subtype.val (e.symm.injective h)
    exact hr this
  have hbij : Bijective f := (Fintype.bijective_iff_injective_and_card f).mpr ⟨hf, by simp⟩
  refine ⟨Equiv.ofBijective f hbij, fun u v => ?_⟩
  simp only [Equiv.ofBijective_apply, f, OrderIso.le_iff_le, Subtype.mk_le_mk]

/-- **Theorem 3 (⇒)**: if `G_d` can be pebbled progressively with `K + 2` pebbles, then
`vs(G) ≤ K`. The layout lists the vertices of `G` in the order they lose their pebble. -/
theorem vertexSeparation_le_of_pebblesWithin (h : PebblesWithin (lengauerD G) (K + 2)) :
    vertexSeparation G ≤ K := by
  classical
  obtain ⟨T, P, h0, hT, hs⟩ := exists_seq_of_reflTransGen h
  have hc : ∀ i ≤ T, numPebbles (P i) ≤ K + 2 := by
    intro i hi
    rcases i with _ | i
    · rw [h0]; simp [numPebbles, Pebbled]
    · exact (hs i (by omega)).numPebbles_le
  have hmono := fun {i j} (hij : i ≤ j) (hj : j ≤ T) x => seq_rank_mono hs (P := P) hij hj x
  have hex : ∀ v : V, ∃ t, P t (.inl v) = done := fun v => ⟨T, by rw [hT]⟩
  let r : V → ℕ := fun v => Nat.find (hex v)
  have hrT : ∀ v, r v ≤ T := fun v => Nat.find_min' (hex v) (by rw [hT])
  have hdone : ∀ v t, t ≤ T → (P t (.inl v) = done ↔ r v ≤ t) := by
    intro v t ht
    constructor
    · exact fun h => Nat.find_min' (hex v) h
    · intro hle
      have h1 := hmono hle ht (.inl v)
      have h2 : P (r v) (.inl v) = done := Nat.find_spec (hex v)
      rw [h2] at h1
      rw [eq_done_iff_rank]
      have := rank_le_three (P t (.inl v)); simp at h1; omega
  have hr : Injective r := by
    intro u v huv
    have hu : P (r u) (.inl u) = done := Nat.find_spec (hex u)
    have hv : P (r v) (.inl v) = done := Nat.find_spec (hex v)
    have hpos : r u ≠ 0 := by
      intro h; rw [h, h0] at hu; exact PebblePhase.noConfusion hu
    obtain ⟨i, hi⟩ : ∃ i, r u = i + 1 := ⟨r u - 1, by omega⟩
    have hu' : P i (.inl u) ≠ done := fun h =>
      Nat.find_min (hex u) (show i < r u by omega) h
    have hv' : P i (.inl v) ≠ done := fun h =>
      Nat.find_min (hex v) (show i < r v by omega) h
    rw [hi] at hu; rw [← huv, hi] at hv
    have := (hs i (by have := hrT u; omega)).eq_target (x := .inl u) (y := .inl v)
      (by rw [hu]; exact hu') (by rw [hv]; exact hv')
    exact Sum.inl_injective this
  obtain ⟨σ, hσ⟩ := exists_layout_of_injective hr
  refine (vertexSeparation_le_vertexSepOfLayout G σ).trans ?_
  rw [vertexSepOfLayout_le_iff]
  intro i hi
  set v := σ.symm ⟨i, hi⟩
  have hkey : activeSuffix G σ i = outerBoundary G (univ.filter fun u => P (r v) (.inl u) = done) := by
    have hpre : ∀ u, (σ u).val ≤ i ↔ P (r v) (.inl u) = done := by
      intro u
      rw [hdone u _ (hrT v), ← hσ]
      simp [v, Fin.le_def]
    ext w
    simp only [mem_activeSuffix_iff, mem_outerBoundary, mem_prefixSet_iff, mem_filter,
      mem_univ, true_and, hpre, gt_iff_lt, ← not_le]
  unfold vertexSepAt
  rw [hkey]
  exact outerBoundary_card_le hs h0 hT hc (hrT v)

/-- With an edge `{a, b}`, `G_d` needs three pebbles: when `{a, b}` turns black, `a` and `b`
carry pebbles too. -/
theorem three_le_of_pebblesWithin {a b : V} (hab : G.Adj a b)
    (h : PebblesWithin (lengauerD G) K) : 3 ≤ K := by
  classical
  obtain ⟨T, P, h0, hT, hs⟩ := exists_seq_of_reflTransGen h
  set e : G.edgeSet := ⟨s(a, b), hab⟩
  obtain ⟨i, hiT, -, hw, hp⟩ := seq_exists_turn hs (x := .inr e) (by rw [h0]; simp)
    (by rw [hT]; simp)
  have hsub : ({.inr e, .inl a, .inl b} : Finset (V ⊕ G.edgeSet)) ⊆
      univ.filter fun x => (P i x).Pebbled := by
    intro x hx
    simp only [mem_insert, mem_singleton] at hx
    simp only [mem_filter, mem_univ, true_and]
    rcases hx with rfl | rfl | rfl
    · rw [hw]; exact Or.inl rfl
    · exact hp _ (by simp [e])
    · exact hp _ (by simp [e])
  have hcard := card_le_card hsub
  rw [card_insert_of_notMem (by simp), card_insert_of_notMem (by simp [hab.ne]),
    card_singleton] at hcard
  exact hcard.trans (seq_numPebbles_le hs h0 hiT.le)

/-- With a vertex, one pebble is needed. -/
theorem one_le_of_pebblesWithin (v : V) (h : PebblesWithin (lengauerD G) K) : 1 ≤ K := by
  classical
  obtain ⟨T, P, h0, hT, hs⟩ := exists_seq_of_reflTransGen h
  obtain ⟨i, hiT, -, hw, -⟩ := seq_exists_turn hs (x := .inl v) (by rw [h0]; simp)
    (by rw [hT]; simp)
  have hsub : ({.inl v} : Finset (V ⊕ G.edgeSet)) ⊆ univ.filter fun x => (P i x).Pebbled := by
    intro x hx
    rw [mem_singleton] at hx; subst hx
    simp only [mem_filter, mem_univ, true_and]; rw [hw]; exact Or.inl rfl
  have hcard := card_le_card hsub
  rw [card_singleton] at hcard
  exact hcard.trans (seq_numPebbles_le hs h0 hiT.le)

end Lower

/-! ### The strategy a layout induces -/

section Upper

open PebblePhase

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]
variable {K : ℕ}

local notation "Reach" => Relation.ReflTransGen (PebbleStep (lengauerD G) K)

theorem numPebbles_le_of_subset {α : Type*} [Fintype α] [DecidableEq α] {P : PebblePosition α}
    {Y : Finset α} (h : ∀ x, (P x).Pebbled → x ∈ Y) : numPebbles P ≤ Y.card :=
  card_le_card fun x hx => h x (by simpa using hx)

theorem reach_move {P : PebblePosition (V ⊕ G.edgeSet)} (m : PebbleMove (V ⊕ G.edgeSet))
    (hm : m.Legal (lengauerD G) P) (hc : numPebbles (m.apply P) ≤ K) :
    Reach P (m.apply P) :=
  Relation.ReflTransGen.single ⟨m, hm, rfl, hc⟩

variable (G) in
/-- The positions the strategy passes through: `S` the cleared vertices of `G`, `B` the
black ones, `F` the cleared edge vertices; everything else is pebble-free. -/
def buildPos (S B : Finset V) (F : Finset G.edgeSet) : PebblePosition (V ⊕ G.edgeSet)
  | .inl w => if w ∈ S then done else if w ∈ B then black else fresh
  | .inr e => if e ∈ F then done else fresh

theorem buildPos_pebbled {S B : Finset V} {F : Finset G.edgeSet} {x : V ⊕ G.edgeSet}
    (h : (buildPos G S B F x).Pebbled) : x ∈ B.map Embedding.inl := by
  rcases x with w | e
  · simp only [buildPos] at h
    split_ifs at h with h1 h2 <;> simp_all [Pebbled]
  · simp only [buildPos] at h
    split_ifs at h <;> simp [Pebbled] at h

theorem numPebbles_buildPos_le (S B : Finset V) (F : Finset G.edgeSet) :
    numPebbles (buildPos G S B F) ≤ B.card := by
  have := numPebbles_le_of_subset (fun x h => buildPos_pebbled (S := S) (B := B) (F := F) h)
  rwa [card_map] at this

/-- Blacken one pebble-free vertex of `G`: place a white pebble and turn it (a source). -/
theorem reach_raise {S B : Finset V} {F : Finset G.edgeSet} {x : V} (hxS : x ∉ S) (hxB : x ∉ B)
    (hK : (insert x B).card ≤ K) :
    Reach (buildPos G S B F) (buildPos G S (insert x B) F) := by
  set P₀ := buildPos G S B F
  have h1 : Reach P₀ ((PebbleMove.place (Sum.inl x)).apply P₀) := by
    refine reach_move _ (by simp [PebbleMove.Legal, P₀, buildPos, hxS, hxB]) ?_
    refine (numPebbles_le_of_subset (Y := (insert x B).map Embedding.inl) ?_).trans
      (by rwa [card_map])
    intro y hy
    by_cases hyx : y = .inl x
    · subst hyx; simp
    · rw [PebbleMove.apply, PebbleMove.target, Function.update_of_ne hyx] at hy
      exact map_subset_map.mpr (subset_insert _ _) (buildPos_pebbled hy)
  refine h1.trans ?_
  set P₁ := (PebbleMove.place (Sum.inl x)).apply P₀
  have heq : (PebbleMove.turn (Sum.inl x)).apply P₁ = buildPos G S (insert x B) F := by
    funext y
    rcases y with w | e
    · by_cases hw : w = x
      · subst hw
        simp [PebbleMove.apply, PebbleMove.target, PebbleMove.result, buildPos, hxS]
      · simp [PebbleMove.apply, PebbleMove.target, P₁, P₀, buildPos, hw]
    · simp [PebbleMove.apply, PebbleMove.target, P₁, P₀, buildPos]
  rw [← heq]
  refine reach_move _ ⟨by simp [P₁, PebbleMove.apply, PebbleMove.target, PebbleMove.result],
    fun y hy => absurd hy lengauerD_not_adj_to_inl⟩ ?_
  rw [heq]; exact (numPebbles_buildPos_le _ _ _).trans hK

/-- Clear one edge vertex whose endpoints are black: place, turn, remove. -/
theorem reach_edge {S B : Finset V} {F : Finset G.edgeSet} {e : G.edgeSet} (heF : e ∉ F)
    (hends : ∀ u ∈ (e : Sym2 V), u ∈ B ∧ u ∉ S) (hK : B.card + 1 ≤ K) :
    Reach (buildPos G S B F) (buildPos G S B (insert e F)) := by
  set P₀ := buildPos G S B F
  have hcnt : ∀ P : PebblePosition (V ⊕ G.edgeSet), (∀ y, y ≠ .inr e → P y = P₀ y) →
      numPebbles P ≤ K := by
    intro P hP
    refine (numPebbles_le_of_subset (Y := insert (.inr e) (B.map Embedding.inl)) ?_).trans
      ((card_insert_le _ _).trans (by rwa [card_map]))
    intro y hy
    by_cases hye : y = .inr e
    · subst hye; simp
    · rw [hP y hye] at hy; exact mem_insert_of_mem (buildPos_pebbled hy)
  set P₁ := (PebbleMove.place (Sum.inr e)).apply P₀
  set P₂ := (PebbleMove.turn (Sum.inr e)).apply P₁
  have hP₁ : ∀ y, y ≠ .inr e → P₁ y = P₀ y := fun y hy => by
    simp [P₁, PebbleMove.apply, PebbleMove.target, Function.update_of_ne hy]
  have hP₂ : ∀ y, y ≠ .inr e → P₂ y = P₀ y := fun y hy => by
    simp [P₂, PebbleMove.apply, PebbleMove.target, Function.update_of_ne hy, hP₁ y hy]
  have h1 : Reach P₀ P₁ :=
    reach_move _ (by simp [PebbleMove.Legal, P₀, buildPos, heF]) (hcnt _ hP₁)
  have h2 : Reach P₁ P₂ := by
    refine reach_move _ ⟨by simp [P₁, PebbleMove.apply, PebbleMove.target,
      PebbleMove.result], ?_⟩ (hcnt _ hP₂)
    intro y hy
    rcases y with u | f
    · have hu := hends u hy
      rw [hP₁ _ (by simp)]
      simp [P₀, buildPos, hu.1, hu.2, Pebbled]
    · exact absurd hy lengauerD_not_adj_from_inr
  have heq : (PebbleMove.remove (Sum.inr e)).apply P₂ = buildPos G S B (insert e F) := by
    funext y
    by_cases hye : y = .inr e
    · subst hye; simp [PebbleMove.apply, PebbleMove.target, PebbleMove.result, buildPos]
    · rw [PebbleMove.apply, PebbleMove.target, Function.update_of_ne hye, hP₂ y hye]
      rcases y with w | f
      · simp [P₀, buildPos]
      · have : f ≠ e := fun h => hye (by rw [h])
        simp [P₀, buildPos, this]
  have h3 : Reach P₂ (buildPos G S B (insert e F)) := by
    rw [← heq]
    refine reach_move _ (by simp [P₂, PebbleMove.Legal, PebbleMove.apply, PebbleMove.target,
      PebbleMove.result]) ?_
    rw [heq]; exact (numPebbles_buildPos_le _ _ _).trans (by omega)
  exact h1.trans (h2.trans h3)

/-- Remove the black pebble from a vertex of `G`. -/
theorem reach_clear {S B : Finset V} {F : Finset G.edgeSet} {x : V} (hxS : x ∉ S) (hxB : x ∈ B)
    (hK : B.card ≤ K) :
    Reach (buildPos G S B F) (buildPos G (insert x S) B F) := by
  have heq : (PebbleMove.remove (Sum.inl x)).apply (buildPos G S B F) =
      buildPos G (insert x S) B F := by
    funext y
    rcases y with w | e
    · by_cases hw : w = x
      · subst hw; simp [PebbleMove.apply, PebbleMove.target, PebbleMove.result, buildPos]
      · simp [PebbleMove.apply, PebbleMove.target, buildPos, hw]
    · simp [PebbleMove.apply, PebbleMove.target, buildPos]
  rw [← heq]
  refine reach_move _ (by simp [PebbleMove.Legal, buildPos, hxS, hxB]) ?_
  rw [heq]; exact (numPebbles_buildPos_le _ _ _).trans hK

theorem reach_raise_set {S B : Finset V} {F : Finset G.edgeSet} (X : Finset V)
    (hXS : Disjoint X S) (hXB : Disjoint X B) (hK : (B ∪ X).card ≤ K) :
    Reach (buildPos G S B F) (buildPos G S (B ∪ X) F) := by
  induction X using Finset.induction_on with
  | empty => simp; exact .refl
  | insert x X hx ih =>
    have hxS : x ∉ S := disjoint_left.mp hXS (mem_insert_self _ _)
    have hxB : x ∉ B := disjoint_left.mp hXB (mem_insert_self _ _)
    have hsub : (B ∪ X).card ≤ (B ∪ insert x X).card :=
      card_le_card (union_subset_union le_rfl (subset_insert _ _))
    refine (ih (disjoint_of_subset_left (subset_insert _ _) hXS)
      (disjoint_of_subset_left (subset_insert _ _) hXB) (hsub.trans hK)).trans ?_
    rw [union_insert]
    exact reach_raise hxS (by simp [hxB, hx]) (by rwa [← union_insert])

theorem reach_edge_set {S B : Finset V} {F : Finset G.edgeSet} (Y : Finset G.edgeSet)
    (hYF : Disjoint Y F) (hends : ∀ e ∈ Y, ∀ u ∈ (e : Sym2 V), u ∈ B ∧ u ∉ S)
    (hK : Y.Nonempty → B.card + 1 ≤ K) :
    Reach (buildPos G S B F) (buildPos G S B (F ∪ Y)) := by
  induction Y using Finset.induction_on with
  | empty => simp; exact .refl
  | insert e Y he ih =>
    refine (ih (disjoint_of_subset_left (subset_insert _ _) hYF)
      (fun f hf => hends f (mem_insert_of_mem hf))
      (fun _ => hK (insert_nonempty _ _))).trans ?_
    rw [union_insert]
    exact reach_edge (by simp [disjoint_left.mp hYF (mem_insert_self _ _), he])
      (hends e (mem_insert_self _ _)) (hK (insert_nonempty _ _))

variable (G) in
/-- The edges with an endpoint in `S`. -/
def clearedEdges (S : Finset V) : Finset G.edgeSet :=
  univ.filter fun e => ∃ u ∈ S, u ∈ (e : Sym2 V)

variable (G) in
/-- The position after the strategy has cleared the vertices `S`: their outer boundary is
black, the edges at `S` are cleared, everything else is pebble-free. -/
def layoutPos (S : Finset V) : PebblePosition (V ⊕ G.edgeSet) :=
  buildPos G S (outerBoundary G S) (clearedEdges G S)

/-- One step of the strategy: clear `v`. Blacken the pebble-free vertices of `N[v]`, clear
every edge at `v` not yet cleared, then remove `v`. At most the new boundary, `v`, and one
edge vertex are pebbled at any instant. -/
theorem reach_layoutPos_insert {S : Finset V} {v : V} (hv : v ∉ S)
    (hK1 : (outerBoundary G (insert v S)).card + 1 ≤ K)
    (hK2 : (∃ w, G.Adj v w) → (outerBoundary G (insert v S)).card + 2 ≤ K) :
    Reach (layoutPos G S) (layoutPos G (insert v S)) := by
  classical
  set A := outerBoundary G S
  set A' := outerBoundary G (insert v S)
  set X := univ.filter fun w => (w = v ∨ G.Adj v w) ∧ w ∉ S ∧ w ∉ A
  set B₁ := A ∪ X
  have hB₁ : B₁ ⊆ insert v A' := by
    intro w hw
    rcases mem_union.mp hw with hw | hw
    · obtain ⟨hwS, u, huS, huw⟩ := mem_outerBoundary.mp hw
      by_cases hwv : w = v
      · simp [hwv]
      · exact mem_insert_of_mem (mem_outerBoundary.mpr
          ⟨by simp [hwv, hwS], u, mem_insert_of_mem huS, huw⟩)
    · simp only [X, mem_filter, mem_univ, true_and] at hw
      obtain ⟨hvw | hvw, hwS, -⟩ := hw
      · simp [hvw]
      · exact mem_insert_of_mem (mem_outerBoundary.mpr
          ⟨by simp [hvw.ne.symm, hwS], v, mem_insert_self _ _, hvw⟩)
  have hcard : B₁.card ≤ A'.card + 1 :=
    (card_le_card hB₁).trans (card_insert_le _ _)
  have hvB : v ∈ B₁ := by
    by_cases hvA : v ∈ A
    · exact mem_union_left _ hvA
    · exact mem_union_right _ (by simp [X, hv, hvA])
  set Y := univ.filter fun e : G.edgeSet => v ∈ (e : Sym2 V) ∧ e ∉ clearedEdges G S
  have h1 : Reach (layoutPos G S) (buildPos G S B₁ (clearedEdges G S)) :=
    reach_raise_set X (by rw [disjoint_left]; intro w hw; simp [X] at hw; exact hw.2.1)
      (by rw [disjoint_left]; intro w hw; simp [X] at hw; exact hw.2.2)
      (by have : B₁.card ≤ K := by omega
          exact this)
  have h2 : Reach (buildPos G S B₁ (clearedEdges G S))
      (buildPos G S B₁ (clearedEdges G S ∪ Y)) := by
    refine reach_edge_set Y (by rw [disjoint_left]; intro e he; simp [Y] at he; exact he.2)
      ?_ ?_
    · intro e he u hu
      simp only [Y, mem_filter, mem_univ, true_and] at he
      obtain ⟨hve, heF⟩ := he
      have huS : u ∉ S := fun huS => heF (by simp [clearedEdges]; exact ⟨u, huS, hu⟩)
      refine ⟨?_, huS⟩
      obtain ⟨w, hw⟩ := Sym2.mem_iff_exists.mp hve
      have hvw : G.Adj v w := by
        have := e.2; rw [hw] at this; exact this
      rw [hw, Sym2.mem_iff] at hu
      by_cases huA : u ∈ A
      · exact mem_union_left _ huA
      · rcases hu with rfl | rfl
        · exact mem_union_right _ (by simp [X, huS, huA])
        · exact mem_union_right _ (by simp [X, huS, huA, hvw])
    · rintro ⟨e, he⟩
      simp only [Y, mem_filter, mem_univ, true_and] at he
      obtain ⟨w, hw⟩ := Sym2.mem_iff_exists.mp he.1
      have hvw : G.Adj v w := by
        have := e.2; rw [hw] at this; exact this
      have := hK2 ⟨w, hvw⟩; omega
  have h3 : Reach (buildPos G S B₁ (clearedEdges G S ∪ Y))
      (buildPos G (insert v S) B₁ (clearedEdges G S ∪ Y)) :=
    reach_clear hv hvB (by omega)
  have heq : buildPos G (insert v S) B₁ (clearedEdges G S ∪ Y) = layoutPos G (insert v S) := by
    funext y
    rcases y with w | e
    · simp only [layoutPos, buildPos]
      by_cases hw : w ∈ insert v S
      · simp [hw]
      · have hwv : w ≠ v := fun h => hw (by simp [h])
        have hwS : w ∉ S := fun h => hw (mem_insert_of_mem h)
        have hiff : w ∈ B₁ ↔ w ∈ A' := by
          simp only [B₁, A, A', X, mem_union, mem_filter, mem_univ, true_and,
            mem_outerBoundary, mem_insert, hwv, hwS, false_or, not_false_eq_true,
            true_and, exists_eq_or_imp]
          by_cases hp : ∃ u ∈ S, G.Adj u w <;> simp only [hp] <;> tauto
        exact if_congr Iff.rfl rfl (if_congr hiff rfl rfl)
    · simp only [layoutPos, buildPos]
      have hC : ∀ T : Finset V, e ∈ clearedEdges G T ↔ ∃ u ∈ T, u ∈ (e : Sym2 V) := by
        intro T; simp [clearedEdges]
      have hY : e ∈ Y ↔ v ∈ (e : Sym2 V) ∧ e ∉ clearedEdges G S := by simp [Y]
      have hiff : e ∈ clearedEdges G S ∪ Y ↔ e ∈ clearedEdges G (insert v S) := by
        rw [mem_union, hY, hC, hC]
        simp only [mem_insert, exists_eq_or_imp]
        generalize (∃ u ∈ S, u ∈ (e : Sym2 V)) = p
        generalize (v ∈ (e : Sym2 V)) = q
        exact ⟨fun h => h.elim Or.inr (fun h => Or.inl h.1), fun h => h.elim
          (fun hq => (Classical.em p).elim Or.inl (fun hp => Or.inr ⟨hq, hp⟩)) Or.inl⟩
      exact if_congr hiff rfl rfl
  rw [← heq]
  exact h1.trans (h2.trans h3)

theorem layoutPos_empty : layoutPos G ∅ = fun _ => fresh := by
  funext y; rcases y with w | e <;> simp [layoutPos, buildPos, outerBoundary, clearedEdges]

theorem layoutPos_univ : layoutPos G univ = fun _ => done := by
  funext y
  rcases y with w | ⟨e, he⟩
  · simp [layoutPos, buildPos]
  · simp only [layoutPos, buildPos, clearedEdges, mem_filter, mem_univ, true_and]
    have : ∃ u, u ∈ e := by
      induction e using Sym2.ind with
      | h a b => exact ⟨a, Sym2.mem_mk_left a b⟩
    simp [this]

/-- **Theorem 3 (⇐)**, from any layout: clearing the vertices of `G` in layout order pebbles
`G_d` progressively. The pebbles in play are the active suffix, the vertex being cleared,
and one edge vertex. -/
theorem pebblesWithin_of_layout (σ : LinearLayout V)
    (h1 : ∀ i, i < Fintype.card V → vertexSepAt G σ i + 1 ≤ K)
    (h2 : ∀ i (hi : i < Fintype.card V), (∃ w, G.Adj (σ.symm ⟨i, hi⟩) w) →
      vertexSepAt G σ i + 2 ≤ K) :
    PebblesWithin (lengauerD G) K := by
  classical
  let Tset : ℕ → Finset V := fun i => univ.filter fun v => (σ v).val < i
  have hstep : ∀ i ≤ Fintype.card V, Reach (layoutPos G ∅) (layoutPos G (Tset i)) := by
    intro i hi
    induction i with
    | zero =>
      have : Tset 0 = ∅ := by ext; simp [Tset]
      rw [this]
    | succ i ih =>
      have hi' : i < Fintype.card V := by omega
      set v := σ.symm ⟨i, hi'⟩
      have hins : Tset (i + 1) = insert v (Tset i) := by
        ext u
        simp only [Tset, mem_filter, mem_univ, true_and, mem_insert]
        constructor
        · intro h
          rcases Nat.lt_succ_iff_lt_or_eq.mp h with h | h
          · exact Or.inr h
          · left; simp [v, ← h]
        · rintro (rfl | h)
          · simp [v]
          · omega
      have hvT : v ∉ Tset i := by simp [Tset, v]
      have hbd : outerBoundary G (Tset (i + 1)) = activeSuffix G σ i := by
        ext w
        simp only [mem_outerBoundary, mem_activeSuffix_iff, mem_prefixSet_iff, Tset,
          mem_filter, mem_univ, true_and, Nat.lt_succ_iff, not_le, gt_iff_lt]
      refine (ih (by omega)).trans ?_
      rw [hins]
      rw [hins] at hbd
      refine reach_layoutPos_insert hvT ?_ ?_
      · rw [hbd]; exact h1 i hi'
      · rw [hbd]; exact h2 i hi'
  have hall : Tset (Fintype.card V) = univ := by ext v; simp [Tset]
  have := hstep _ le_rfl
  rw [hall, layoutPos_univ, layoutPos_empty] at this
  exact this

end Upper

/-! ### Theorem 3 -/

section Theorem3

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- **Lengauer (1981) Theorem 3, with `vs`**: for every graph and every `K ≥ 0`,
`vs(G) ≤ K ⇔ G_d` can be pebbled progressively with `K + 2` pebbles. -/
theorem pebblesWithin_lengauerD_iff (K : ℕ) :
    PebblesWithin (lengauerD G) (K + 2) ↔ vertexSeparation G ≤ K := by
  refine ⟨vertexSeparation_le_of_pebblesWithin, fun h => ?_⟩
  obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation G
  have hat : ∀ i, i < Fintype.card V → vertexSepAt G σ i ≤ K := fun i hi =>
    ((vertexSepOfLayout_le_iff G σ _).mp (hσ.trans_le h)) i hi
  exact pebblesWithin_of_layout σ (fun i hi => by have := hat i hi; omega)
    (fun i hi _ => by have := hat i hi; omega)

/-- **Lengauer (1981) Theorem 3, as stated** (p. 472): "The instance `(G, K)` of VSG is
positive if and only if the instance `(G_d, K + 2)` of PBWP is positive", `K` a positive
integer. -/
theorem isPositiveVSG_iff_isPositivePBWP_lengauerD {K : ℕ} (hK : 0 < K) :
    IsPositiveVSG G K ↔ IsPositivePBWP (lengauerD G) (K + 2) := by
  rw [isPositiveVSG_iff, IsPositivePBWP, pebblesWithin_lengauerD_iff]
  omega

/-- **The pebbling number of `G_d`**: `pbw(G_d) = vs(G) + 2` for every graph with an edge. -/
theorem pbw_lengauerD {a b : V} (hab : G.Adj a b) :
    pbw (lengauerD G) = vertexSeparation G + 2 := by
  have hmem : vertexSeparation G + 2 ∈ {K | PebblesWithin (lengauerD G) K} :=
    (pebblesWithin_lengauerD_iff G _).mpr le_rfl
  unfold pbw
  apply le_antisymm
  · exact Nat.sInf_le hmem
  · apply le_csInf ⟨_, hmem⟩
    intro K hK
    have h3 := three_le_of_pebblesWithin hab hK
    obtain ⟨K', rfl⟩ : ∃ K', K = K' + 2 := ⟨K - 2, by omega⟩
    have := (pebblesWithin_lengauerD_iff G K').mp hK
    omega

/-- `pbw(G_d) = pw(G) + 2` for every graph with an edge (with Kinnersley's theorem). -/
theorem pbw_lengauerD_eq_pathwidth {a b : V} (hab : G.Adj a b) :
    pbw (lengauerD G) = pathwidth G + 2 := by
  rw [pbw_lengauerD G hab, vertexSeparation_eq_pathwidth]

/-- `pbw(G_d) = VSG(G) + 2` for every graph with an edge: Theorem 3 as a number. -/
theorem pbw_lengauerD_eq_vsg {a b : V} (hab : G.Adj a b) :
    pbw (lengauerD G) = vsg G + 2 := by
  rw [pbw_lengauerD G hab, vsg_eq_vertexSeparation G hab]

/-- **Edge case**: on an edgeless graph with a vertex, `G_d` is `G` with no arcs and one
pebble suffices, so `pbw(G_d) = 1`, while `vs(G) + 2 = 2` and `VSG(G) + 2 = 3`. The number
form of Theorem 3 needs an edge; the instance forms above do not. -/
theorem pbw_lengauerD_of_edgeless (h : ∀ u v, ¬ G.Adj u v) (v₀ : V) :
    pbw (lengauerD G) = 1 := by
  have hwithin : PebblesWithin (lengauerD G) 1 := by
    have hzero : ∀ (σ : LinearLayout V) i, vertexSepAt G σ i = 0 := by
      intro σ i
      unfold vertexSepAt
      rw [card_eq_zero, eq_empty_iff_forall_notMem]
      intro w hw
      obtain ⟨-, u, -, huw⟩ := (mem_activeSuffix_iff G σ i w).mp hw
      exact h u w huw
    exact pebblesWithin_of_layout (Fintype.equivFin V) (fun i _ => by rw [hzero])
      (fun i _ ⟨w, hw⟩ => absurd hw (h _ _))
  unfold pbw
  apply le_antisymm (Nat.sInf_le (show 1 ∈ {K | PebblesWithin (lengauerD G) K} from hwithin))
  apply le_csInf ⟨1, hwithin⟩
  intro K hK
  exact one_le_of_pebblesWithin v₀ hK

end Theorem3

end Complex

end MOSPFormalization
