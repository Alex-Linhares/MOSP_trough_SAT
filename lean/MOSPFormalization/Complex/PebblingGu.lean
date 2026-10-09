/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Lengauer's Theorem 2 and Kirousis & Papadimitriou's Theorem 3.1

Sources: Lengauer, *Black-white pebbles and graph separation*, Acta Informatica 16 (1981)
465–475 (`literature/lengauer_1981_black_white_pebbles_graph_separation.pdf`), Def. 1a and
Theorem 2 (pp. 468–471); Kirousis & Papadimitriou, *Searching and pebbling*, TCS 47 (1986)
205–218 (`paper1/literature/10_kirousis_papadimitriou_1986.pdf`), §3, Theorem 3.1 (p. 213).
Census, edge cases and brute-force checks: `paper1/equivalences.md`, P.1–P.9 (loop0006
items 01–04). The game (`PebblesWithin`, `pbw`) is the one of `Pebbling.lean`.

## Definitions

* `lengauerU D` is Lengauer's `G_u` (Def. 1a): `u ≠ w` joined iff an arc joins them either way
  or they have a common immediate successor.
* `BlackMove`, `BlackPebblesWithin`, `pb`: KP's progressive black game (p. 205–206): a pebble
  goes on a never-pebbled vertex all of whose immediate predecessors are pebbled, and is deleted
  at any time.
* `IsDirective G D`: `D` is an acyclic orientation of `G` ("dags whose underlying directed graph
  equals `G`", p. 213); `mpb G` and `mpbw G` are the least demands over directives.

## What is proved

Lengauer's Theorem 2 ("`(G, K)` is a positive instance of PBWP if and only if `(G_u, K − 1)` is
a positive instance of VSG", p. 469):

* `pebblesWithin_iff_lengauerU`: **`PebblesWithin D (K + 1) ↔ vs(G_u) ≤ K` for every digraph
  and every `K ≥ 0`.** Acyclicity is never used, so this holds for the game on any digraph.
* `isPositivePBWP_iff_isPositiveVSG_lengauerU`: Theorem 2 as stated, for every `K ≥ 2`;
  `isPositivePBWP_one_not_isPositiveVSG_zero`: it fails at `K = 1` on an arc-free digraph
  (census P.3), where `(G_u, 0)` is no VSG instance.
* `pbw_eq_vertexSeparation_lengauerU_add_one`, `pbw_eq_pathwidth_lengauerU_add_one`:
  **`pbw(D) = vs(G_u) + 1 = pw(G_u) + 1` for every nonempty digraph**; `pbw_eq_vsg_lengauerU_add_one`
  with VSG when `D` has an arc between distinct vertices.
* `mospGraph_pebbleMatrix`, `pbw_eq_mospValue_pebbleMatrix`: `G_u` is the MOSP graph of the
  matrix whose column `v` is `N⁻[v]`, so **`pbw(D) = Z(M_D)`** (with `MOSPGraph.lean`).

Kirousis & Papadimitriou's Theorem 3.1 ("For any graph G, mpb(G) = ns(G) = mpbw(G)"), as
item 01 settled it:

* `mpb_eq_vertexSeparation_add_one`, `mpbw_eq_vertexSeparation_add_one`, `mpb_eq_mpbw`,
  `mpb_eq_pathwidth_add_one`, `mpbw_eq_pathwidth_add_one`: **`mpb(G) = mpbw(G) = vs(G) + 1 =
  pw(G) + 1` for every nonempty graph**, edgeless ones included.
* `mpb_eq_nodeSearch`: **Theorem 3.1 as stated, `mpb = ns = mpbw`, for every graph with an
  edge** (with `nodeSearch_eq_vertexSeparation_add_one`, `NodeMonotonicity.lean`).
* `mpb_ne_nodeSearch_of_edgeless`: **the first equality is false on edgeless nonempty graphs**:
  `mpb = mpbw = 1`, `ns = 0`.
* By-products: `vertexSeparation_mono` (monotone under adding edges), `layoutOrient_isDirective`,
  `BlackPebblesWithin.pebblesWithin` (a black play is a black-white play).

## The proofs

* **Theorem 2 (⇒), `vertexSeparation_lengauerU_le_of_pebblesWithin`**: Lengauer's own. Lay the
  vertices out in the order they lose their pebble. When `v` is removed, every `G_u`-neighbour
  `w` of the cleared set `S` that is not cleared still carries a pebble: an arc `u → w`, `w → u`
  or a common successor `x` means some turn (of `w`, `u` or `x`) saw `u` and `w` pebbled
  together before `u` was cleared (`outerBoundary_lengauerU_card_le`). With `v`, that is
  `|B| + 1` pebbles just before the removal.
* **Theorem 2 (⇐), `pebblesWithin_of_layout_lengauerU`**: Lengauer's four steps, as an invariant
  on positions (`guPos`): after clearing `S`, the outer boundary of `S` in `G_u` is pebbled,
  black exactly where it has an immediate predecessor in `S`. To clear `v`: whiten the
  pebble-free vertices of `N_u[v]`, turn `v` and every successor of `v` not yet black (their
  predecessors are `G_u`-neighbours of `v`, none cleared), remove `v`
  (`reach_guPos_insert`). At most the new boundary and `v` are pebbled, `vs + 1`.
* **KP (≥), `vertexSeparation_add_one_le_of_directive`**: `G ≤ D_u` for every directive, so
  Theorem 2 (⇒) and `vertexSeparation_mono` give `vs(G) + 1 ≤ pbw(D) ≤ pb(D)`.
* **KP (≤), `blackPebblesWithin_layoutOrient`**: orient along a layout, place black pebbles in
  layout order, clear a vertex as soon as all its neighbours are placed. The pebbles in play are
  Kornai & Tuza's shack (`Narrowness.lean`), whose size is `vs(σ reversed) + 1`
  (`card_shackAfterPut`); take `σ` the reverse of an optimal layout. This is the direct
  proof of census P.3; it avoids node search, LaPaugh and monotonicity.

`python -m paper1.complex_check --pebbling-gu` replays both Theorem 2 constructions on every
layout of `G_u` of every digraph with at most 4 vertices (loops and cycles allowed, 66,067
digraphs) and of every dag on 5, and checks `pbw(D) = vs(G_u) + 1` there by exact search. It
also replays the KP black strategy on every layout of every graph with at most 7 vertices
(5,378,453 plays), under `BlackMove.Legal` and, converted, under the black-white rules. Zero
failures.
-/

import MOSPFormalization.Complex.Pebbling
import MOSPFormalization.Complex.Narrowness
import MOSPFormalization.Complex.NodeMonotonicity
import MOSPFormalization.MOSPGraph

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace MOSPFormalization

namespace Complex

open Finset Function PebblePhase

/-! ### Lengauer's `G_u` -/

section Gu

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- Lengauer's `G_u` (Def. 1a, p. 468): `E_u = {{v, w} | (v, w) ∈ E} ∪ {{v, w} | (v, u),
(w, u) ∈ E for some u}`, "cliques out of the immediate predecessors of every vertex ... and
then ignores edge directions". -/
def lengauerU (D : Digraph α) : SimpleGraph α where
  Adj u w := u ≠ w ∧ (D.Adj u w ∨ D.Adj w u ∨ ∃ x, D.Adj u x ∧ D.Adj w x)
  symm := by
    constructor
    intro u w ⟨hne, h⟩
    refine ⟨hne.symm, ?_⟩
    rcases h with h | h | ⟨x, h1, h2⟩
    · exact Or.inr (Or.inl h)
    · exact Or.inl h
    · exact Or.inr (Or.inr ⟨x, h2, h1⟩)
  loopless := ⟨fun _ h => h.1 rfl⟩

instance (D : Digraph α) [DecidableRel D.Adj] : DecidableRel (lengauerU D).Adj :=
  fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

theorem lengauerU_adj {D : Digraph α} {u w : α} :
    (lengauerU D).Adj u w ↔ u ≠ w ∧ (D.Adj u w ∨ D.Adj w u ∨ ∃ x, D.Adj u x ∧ D.Adj w x) :=
  Iff.rfl

end Gu

/-! ### More about plays -/

section Plays

variable {α : Type*} [Fintype α] [DecidableEq α] {D : Digraph α} {K : ℕ}

/-- A move raises the phase of its target by exactly one. -/
theorem PebbleStep.rank_le_succ {P Q : PebblePosition α} (h : PebbleStep D K P Q) (x : α) :
    (Q x).rank ≤ (P x).rank + 1 := by
  obtain ⟨m, hm, rfl, -⟩ := h
  unfold PebbleMove.apply
  by_cases hx : x = m.target
  · subst hx
    rw [Function.update_self]
    cases m <;> simp_all [PebbleMove.Legal, PebbleMove.result, PebbleMove.target]
  · rw [Function.update_of_ne hx]; omega

/-- With a vertex, every play uses a pebble. -/
theorem one_le_of_pebblesWithin' (v : α) (h : PebblesWithin D K) : 1 ≤ K := by
  obtain ⟨T, P, h0, hT, hs⟩ := exists_seq_of_reflTransGen h
  obtain ⟨i, hiT, -, hw, -⟩ := seq_exists_turn hs (x := v) (by rw [h0]; simp)
    (by rw [hT]; simp)
  have hsub : ({v} : Finset α) ⊆ univ.filter fun x => (P i x).Pebbled := by
    intro x hx
    rw [mem_singleton] at hx; subst hx
    simp only [mem_filter, mem_univ, true_and]; rw [hw]; exact Or.inl rfl
  have hcard := card_le_card hsub
  rw [card_singleton] at hcard
  exact hcard.trans (seq_numPebbles_le hs h0 hiT.le)

theorem pebblesWithin_of_isEmpty [IsEmpty α] (K : ℕ) : PebblesWithin D K := by
  have : (fun _ : α => fresh) = fun _ => done := funext fun x => isEmptyElim x
  unfold PebblesWithin; rw [this]

end Plays

/-! ### Theorem 2 (⇒): the layout a play induces -/

section Lower

variable {α : Type*} [Fintype α] [DecidableEq α] {D : Digraph α} [DecidableRel D.Adj]
variable {K T : ℕ} {P : ℕ → PebblePosition α}

/-- The heart of Theorem 2 (⇒) (Lengauer's three cases, p. 470). Let `v` lose its pebble in
the step from `t` to `t + 1`, and `S` be the vertices cleared by `t + 1`. Every `G_u`-neighbour
`w ∉ S` of a vertex `u ∈ S` carries a pebble at `t`: some turn saw `u` and `w` pebbled together
(`w`'s turn if `u → w`, `u`'s if `w → u`, a common successor's otherwise), before `u` was
cleared. With `v` itself, that is `|B| + 1` pebbles at `t`. -/
theorem outerBoundary_lengauerU_card_le
    (hs : ∀ i < T, PebbleStep D (K + 1) (P i) (P (i + 1)))
    (h0 : P 0 = fun _ => fresh) (hT : P T = fun _ => done)
    {t : ℕ} (ht : t + 1 ≤ T) {v : α} (hv0 : P t v ≠ done) (hv1 : P (t + 1) v = done) :
    (outerBoundary (lengauerU D) (univ.filter fun u => P (t + 1) u = done)).card ≤ K := by
  classical
  set S := univ.filter fun u => P (t + 1) u = done with hS
  set B := outerBoundary (lengauerU D) S with hB
  have hmono := fun {i j} (hij : i ≤ j) (hj : j ≤ T) x => seq_rank_mono hs (P := P) hij hj x
  have hturn : ∀ x : α, ∃ i < T, (P i x).rank ≤ 1 ∧ P i x = white ∧
      ∀ y, D.Adj y x → (P i y).Pebbled := fun x =>
    seq_exists_turn hs (by rw [h0]; simp) (by rw [hT]; simp)
  -- a pebbled vertex that is cleared by `t + 1` was pebbled at a time `≤ t`
  have hbefore : ∀ i ≤ T, ∀ u ∈ S, (P i u).Pebbled → i ≤ t := by
    intro i hi u hu hp
    by_contra hlt
    have h1 := hmono (show t + 1 ≤ i by omega) hi u
    have h2 : P (t + 1) u = done := by simpa [S] using hu
    rw [h2] at h1
    have := (pebbled_iff_rank _).mp hp
    simp at h1; omega
  have hBpeb : ∀ w ∈ B, (P t w).Pebbled := by
    intro w hw
    obtain ⟨hwS, u, huS, huw⟩ := mem_outerBoundary.mp hw
    have hmeet : ∃ i ≤ T, (P i u).Pebbled ∧ (P i w).Pebbled := by
      obtain ⟨-, h | h | ⟨x, hux, hwx⟩⟩ := huw
      · obtain ⟨i, hiT, -, hiw, hp⟩ := hturn w
        exact ⟨i, hiT.le, hp u h, by rw [hiw]; exact Or.inl rfl⟩
      · obtain ⟨i, hiT, -, hiu, hp⟩ := hturn u
        exact ⟨i, hiT.le, by rw [hiu]; exact Or.inl rfl, hp w h⟩
      · obtain ⟨i, hiT, -, -, hp⟩ := hturn x
        exact ⟨i, hiT.le, hp u hux, hp w hwx⟩
    obtain ⟨i, hiT, hpu, hpw⟩ := hmeet
    have hit := hbefore i hiT u huS hpu
    have h1 := (pebbled_iff_rank _).mp hpw
    have h2 := hmono hit (by omega) w
    have h3 := hmono (show t ≤ t + 1 by omega) ht w
    have h4 : (P (t + 1) w).rank ≠ 3 := by
      rw [Ne, ← eq_done_iff_rank]; simpa [S] using hwS
    have h5 := rank_le_three (P (t + 1) w)
    rw [pebbled_iff_rank]; omega
  have hvpeb : (P t v).Pebbled := by
    have h1 := (hs t (by omega)).rank_le_succ v
    rw [hv1] at h1
    have h2 : (P t v).rank ≠ 3 := by rw [Ne, ← eq_done_iff_rank]; exact hv0
    have h3 := rank_le_three (P t v)
    rw [pebbled_iff_rank]; simp at h1; omega
  have hvS : v ∈ S := by simp [S, hv1]
  have hsub : insert v B ⊆ univ.filter fun x => (P t x).Pebbled := by
    intro x hx
    simp only [mem_insert] at hx
    simp only [mem_filter, mem_univ, true_and]
    rcases hx with rfl | hx
    · exact hvpeb
    · exact hBpeb x hx
  have hcard := card_le_card hsub
  rw [card_insert_of_notMem (fun h => (mem_outerBoundary.mp h).1 hvS)] at hcard
  have := seq_numPebbles_le hs h0 (show t ≤ T by omega)
  unfold numPebbles at this
  have hBc : B.card = (outerBoundary (lengauerU D) S).card := rfl
  show B.card ≤ K
  omega

/-- **Theorem 2 (⇒)**, with `vs`: if `D` can be pebbled progressively with `K + 1` pebbles,
then `vs(G_u) ≤ K`. The layout lists the vertices in the order they lose their pebble. -/
theorem vertexSeparation_lengauerU_le_of_pebblesWithin (h : PebblesWithin D (K + 1)) :
    vertexSeparation (lengauerU D) ≤ K := by
  classical
  obtain ⟨T, P, h0, hT, hs⟩ := exists_seq_of_reflTransGen h
  have hmono := fun {i j} (hij : i ≤ j) (hj : j ≤ T) x => seq_rank_mono hs (P := P) hij hj x
  have hex : ∀ v : α, ∃ t, P t v = done := fun v => ⟨T, by rw [hT]⟩
  let r : α → ℕ := fun v => Nat.find (hex v)
  have hrT : ∀ v, r v ≤ T := fun v => Nat.find_min' (hex v) (by rw [hT])
  have hdone : ∀ v t, t ≤ T → (P t v = done ↔ r v ≤ t) := by
    intro v t ht
    constructor
    · exact fun h => Nat.find_min' (hex v) h
    · intro hle
      have h1 := hmono hle ht v
      have h2 : P (r v) v = done := Nat.find_spec (hex v)
      rw [h2] at h1
      rw [eq_done_iff_rank]
      have := rank_le_three (P t v); simp at h1; omega
  have hpos : ∀ v, r v ≠ 0 := by
    intro v h
    have hv : P (r v) v = done := Nat.find_spec (hex v)
    rw [h, h0] at hv; exact PebblePhase.noConfusion hv
  have hprev : ∀ v, P (r v - 1) v ≠ done := fun v h =>
    Nat.find_min (hex v) (show r v - 1 < r v by have := hpos v; omega) h
  have hr : Injective r := by
    intro u v huv
    have hu : P (r u) u = done := Nat.find_spec (hex u)
    have hv : P (r v) v = done := Nat.find_spec (hex v)
    obtain ⟨i, hi⟩ : ∃ i, r u = i + 1 := ⟨r u - 1, by have := hpos u; omega⟩
    have hu' : P i u ≠ done := by have := hprev u; rwa [hi] at this
    have hv' : P i v ≠ done := by have := hprev v; rwa [← huv, hi] at this
    rw [hi] at hu; rw [← huv, hi] at hv
    exact (hs i (by have := hrT u; omega)).eq_target (x := u) (y := v)
      (by rw [hu]; exact hu') (by rw [hv]; exact hv')
  obtain ⟨σ, hσ⟩ := exists_layout_of_injective hr
  refine (vertexSeparation_le_vertexSepOfLayout _ σ).trans ?_
  rw [vertexSepOfLayout_le_iff]
  intro i hi
  set v := σ.symm ⟨i, hi⟩
  have hkey : activeSuffix (lengauerU D) σ i =
      outerBoundary (lengauerU D) (univ.filter fun u => P (r v) u = done) := by
    have hpre : ∀ u, (σ u).val ≤ i ↔ P (r v) u = done := by
      intro u
      rw [hdone u _ (hrT v), ← hσ]
      simp [v, Fin.le_def]
    ext w
    simp only [mem_activeSuffix_iff, mem_outerBoundary, mem_prefixSet_iff, mem_filter,
      mem_univ, true_and, hpre, gt_iff_lt, ← not_le]
  unfold vertexSepAt
  rw [hkey]
  obtain ⟨t, ht⟩ : ∃ t, r v = t + 1 := ⟨r v - 1, by have := hpos v; omega⟩
  have hv1 : P (t + 1) v = done := by rw [← ht]; exact Nat.find_spec (hex v)
  have hv0 : P t v ≠ done := by have := hprev v; rwa [ht] at this
  rw [ht]
  exact outerBoundary_lengauerU_card_le hs h0 hT (by rw [← ht]; exact hrT v) hv0 hv1

end Lower

/-! ### Theorem 2 (⇐): the strategy a layout induces -/

section Upper

variable {α : Type*} [Fintype α] [DecidableEq α] {D : Digraph α} [DecidableRel D.Adj]
variable {K : ℕ}

local notation "Reach" => Relation.ReflTransGen (PebbleStep D K)

/-- The positions the strategy passes through: `S` cleared, `Bl` black, `Wh` white (black
wins), everything else pebble-free. -/
def gpos (S Bl Wh : Finset α) : PebblePosition α := fun w =>
  if w ∈ S then done else if w ∈ Bl then black else if w ∈ Wh then white else fresh

theorem gpos_pebbled {S Bl Wh : Finset α} {x : α} (h : (gpos S Bl Wh x).Pebbled) :
    x ∈ (Bl ∪ Wh) \ S := by
  simp only [gpos] at h
  split_ifs at h with h1 h2 h3 <;> simp_all [Pebbled]

theorem numPebbles_gpos_le (S Bl Wh : Finset α) :
    numPebbles (gpos S Bl Wh) ≤ ((Bl ∪ Wh) \ S).card :=
  numPebbles_le_of_subset fun _ h => gpos_pebbled h

theorem reach_single {P Q : PebblePosition α} (m : PebbleMove α) (hm : m.Legal D P)
    (hQ : Q = m.apply P) (hc : numPebbles Q ≤ K) : Reach P Q :=
  Relation.ReflTransGen.single ⟨m, hm, hQ, hc⟩

/-- Place a white pebble on `x` (nothing to do if `x` is already pebbled). -/
theorem reach_place {S Bl Wh : Finset α} {x : α} (hxS : x ∉ S)
    (hK : ((Bl ∪ insert x Wh) \ S).card ≤ K) :
    Reach (gpos S Bl Wh) (gpos S Bl (insert x Wh)) := by
  by_cases hx : x ∈ Bl ∨ x ∈ Wh
  · have : gpos S Bl (insert x Wh) = gpos S Bl Wh := by
      funext w
      by_cases hw : w = x
      · subst hw; rcases hx with hx | hx <;> simp [gpos, hx]
      · simp [gpos, hw]
    rw [this]
  · push Not at hx
    refine reach_single (.place x) (by simp [PebbleMove.Legal, gpos, hxS, hx.1, hx.2]) ?_
      ((numPebbles_gpos_le _ _ _).trans hK)
    funext w
    by_cases hw : w = x
    · subst hw; simp [PebbleMove.apply, PebbleMove.target, PebbleMove.result, gpos, hxS, hx.1]
    · simp [PebbleMove.apply, PebbleMove.target, gpos, hw]

/-- Turn the white pebble on `x` black (nothing to do if it is black already). -/
theorem reach_turn {S Bl Wh : Finset α} {x : α} (hxS : x ∉ S) (hx : x ∈ Bl ∨ x ∈ Wh)
    (hpred : x ∉ Bl → ∀ y, D.Adj y x → y ∉ S ∧ (y ∈ Bl ∨ y ∈ Wh))
    (hK : ((insert x Bl ∪ Wh) \ S).card ≤ K) :
    Reach (gpos S Bl Wh) (gpos S (insert x Bl) Wh) := by
  by_cases hxB : x ∈ Bl
  · rw [insert_eq_of_mem hxB]
  · have hxW : x ∈ Wh := hx.resolve_left hxB
    refine reach_single (.turn x) ⟨by simp [gpos, hxS, hxB, hxW], fun y hy => ?_⟩ ?_
      ((numPebbles_gpos_le _ _ _).trans hK)
    · obtain ⟨hyS, hyB | hyW⟩ := hpred hxB y hy
      · simp [gpos, hyS, hyB, Pebbled]
      · by_cases hyB : y ∈ Bl <;> simp [gpos, hyS, hyB, hyW, Pebbled]
    · funext w
      by_cases hw : w = x
      · subst hw; simp [PebbleMove.apply, PebbleMove.target, PebbleMove.result, gpos, hxS]
      · simp [PebbleMove.apply, PebbleMove.target, gpos, hw]

/-- Remove the black pebble from `x`. -/
theorem reach_remove {S Bl Wh : Finset α} {x : α} (hxS : x ∉ S) (hxB : x ∈ Bl)
    (hK : ((Bl ∪ Wh) \ insert x S).card ≤ K) :
    Reach (gpos S Bl Wh) (gpos (insert x S) Bl Wh) := by
  refine reach_single (.remove x) (by simp [PebbleMove.Legal, gpos, hxS, hxB]) ?_
    ((numPebbles_gpos_le _ _ _).trans hK)
  funext w
  by_cases hw : w = x
  · subst hw; simp [PebbleMove.apply, PebbleMove.target, PebbleMove.result, gpos]
  · simp [PebbleMove.apply, PebbleMove.target, gpos, hw]

theorem reach_place_set {S Bl Wh : Finset α} (X : Finset α) (hXS : Disjoint X S)
    (hK : ((Bl ∪ (Wh ∪ X)) \ S).card ≤ K) :
    Reach (gpos S Bl Wh) (gpos S Bl (Wh ∪ X)) := by
  induction X using Finset.induction_on with
  | empty => simp only [union_empty]; exact .refl
  | insert x X hx ih =>
    have hsub : ((Bl ∪ (Wh ∪ X)) \ S).card ≤ ((Bl ∪ (Wh ∪ insert x X)) \ S).card :=
      card_le_card (sdiff_subset_sdiff (union_subset_union le_rfl
        (union_subset_union le_rfl (subset_insert _ _))) le_rfl)
    refine (ih (disjoint_of_subset_left (subset_insert _ _) hXS) (hsub.trans hK)).trans ?_
    rw [union_insert]
    exact reach_place (disjoint_left.mp hXS (mem_insert_self _ _)) (by rwa [← union_insert])

theorem reach_turn_set {S Bl Wh : Finset α} (Z : Finset α)
    (hZ : ∀ z ∈ Z, z ∉ S ∧ (z ∈ Bl ∨ z ∈ Wh) ∧
      (z ∉ Bl → ∀ y, D.Adj y z → y ∉ S ∧ (y ∈ Bl ∨ y ∈ Wh)))
    (hK : ((Bl ∪ Wh) \ S).card ≤ K) (hZW : Z ⊆ Bl ∪ Wh) :
    Reach (gpos S Bl Wh) (gpos S (Bl ∪ Z) Wh) := by
  induction Z using Finset.induction_on with
  | empty => simp only [union_empty]; exact .refl
  | insert z Z hz ih =>
    have hZ' : ∀ y ∈ Z, _ := fun y hy => hZ y (mem_insert_of_mem hy)
    refine (ih hZ' ((subset_insert _ _).trans hZW)).trans ?_
    rw [union_insert]
    obtain ⟨hzS, hzBW, hzp⟩ := hZ z (mem_insert_self _ _)
    refine reach_turn hzS (hzBW.imp_left (fun h => mem_union_left _ h)) (fun hn y hy => ?_) ?_
    · obtain ⟨hyS, hy'⟩ := hzp (fun h => hn (mem_union_left _ h)) y hy
      exact ⟨hyS, hy'.imp_left (fun h => mem_union_left _ h)⟩
    · refine le_trans (card_le_card (sdiff_subset_sdiff ?_ le_rfl)) hK
      intro w hw
      simp only [mem_union, mem_insert] at hw
      rcases hw with (rfl | hw | hw) | hw
      · exact hZW (mem_insert_self _ _)
      · exact mem_union_left _ hw
      · exact hZW (mem_insert_of_mem hw)
      · exact mem_union_right _ hw

variable (D) in
/-- The black vertices after the strategy has cleared `S`: the vertices of the outer boundary
with an immediate predecessor in `S`. -/
def guBlack (S : Finset α) : Finset α :=
  (outerBoundary (lengauerU D) S).filter fun w => ∃ u ∈ S, D.Adj u w

variable (D) in
/-- The white vertices: the rest of the outer boundary. -/
def guWhite (S : Finset α) : Finset α :=
  (outerBoundary (lengauerU D) S).filter fun w => ¬ ∃ u ∈ S, D.Adj u w

variable (D) in
/-- The position after the strategy has cleared `S`. -/
def guPos (S : Finset α) : PebblePosition α := gpos S (guBlack D S) (guWhite D S)

theorem guBlack_union_guWhite (S : Finset α) :
    guBlack D S ∪ guWhite D S = outerBoundary (lengauerU D) S := by
  ext w
  simp only [guBlack, guWhite, mem_union, mem_filter]
  by_cases h : ∃ u ∈ S, D.Adj u w <;> simp [h]

/-- One step of the strategy (Lengauer's four steps, pp. 470–471): whiten the pebble-free
`G_u`-neighbours of `v`, turn `v` and its successors black, remove `v`. At most the new outer
boundary and `v` carry pebbles. -/
theorem reach_guPos_insert {S : Finset α} {v : α} (hv : v ∉ S)
    (hK : (outerBoundary (lengauerU D) (insert v S)).card + 1 ≤ K) :
    Reach (guPos D S) (guPos D (insert v S)) := by
  classical
  set U := lengauerU D
  set B := outerBoundary U S
  set B' := outerBoundary U (insert v S)
  set Bl := guBlack D S
  set Wh := guWhite D S
  have hBW : Bl ∪ Wh = B := guBlack_union_guWhite S
  have hBlB : Bl ⊆ B := hBW ▸ subset_union_left
  have hWhB : Wh ⊆ B := hBW ▸ subset_union_right
  have hmemB : ∀ w, w ∈ B ↔ w ∉ S ∧ ∃ u ∈ S, U.Adj u w := fun w => mem_outerBoundary
  have hmemB' : ∀ w, w ∈ B' ↔ w ∉ insert v S ∧ ∃ u ∈ insert v S, U.Adj u w :=
    fun w => mem_outerBoundary
  have hmemBl : ∀ w, w ∈ Bl ↔ w ∈ B ∧ ∃ u ∈ S, D.Adj u w := by
    intro w; simp [Bl, guBlack, B, U]
  -- the vertices to whiten
  set X := univ.filter fun w => (w = v ∨ U.Adj v w) ∧ w ∉ S ∧ w ∉ B
  -- the vertices to turn
  set Z := insert v (univ.filter fun w => D.Adj v w ∧ w ∉ S)
  have hBsub : B ⊆ insert v B' := by
    intro w hw
    obtain ⟨hwS, u, huS, huw⟩ := (hmemB w).mp hw
    by_cases hwv : w = v
    · simp [hwv]
    · exact mem_insert_of_mem ((hmemB' w).mpr ⟨by simp [hwv, hwS], u, mem_insert_of_mem huS, huw⟩)
  have hnbr : ∀ w, U.Adj v w → w ∉ S → w ∈ B' := fun w hvw hwS =>
    (hmemB' w).mpr ⟨by simp [hvw.ne.symm, hwS], v, mem_insert_self _ _, hvw⟩
  have hXsub : X ⊆ insert v B' := by
    intro w hw
    simp only [X, mem_filter, mem_univ, true_and] at hw
    obtain ⟨rfl | hvw, hwS, -⟩ := hw
    · exact mem_insert_self _ _
    · exact mem_insert_of_mem (hnbr w hvw hwS)
  have hZsub : Z ⊆ insert v B' := by
    intro w hw
    simp only [Z, mem_insert, mem_filter, mem_univ, true_and] at hw
    rcases hw with rfl | ⟨hvw, hwS⟩
    · exact mem_insert_self _ _
    · by_cases hwv : w = v
      · simp [hwv]
      · exact mem_insert_of_mem (hnbr w ⟨Ne.symm hwv, Or.inl hvw⟩ hwS)
  -- every non-cleared `G_u`-neighbour of `v`, and `v`, is pebbled once `X` is white
  have hcover : ∀ w, (w = v ∨ U.Adj v w) → w ∉ S → w ∈ Bl ∨ w ∈ Wh ∪ X := by
    intro w hw hwS
    by_cases hwB : w ∈ B
    · rw [← hBW] at hwB
      rcases mem_union.mp hwB with h | h
      · exact Or.inl h
      · exact Or.inr (mem_union_left _ h)
    · exact Or.inr (mem_union_right _ (by simp [X, hw, hwS, hwB]))
  have hcard : ((Bl ∪ (Wh ∪ X)) \ S).card ≤ K := by
    refine le_trans (card_le_card ?_) ((card_insert_le v B').trans hK)
    intro w hw
    simp only [mem_sdiff, mem_union] at hw
    rcases hw.1 with h | h | h
    · exact hBsub (hBlB h)
    · exact hBsub (hWhB h)
    · exact hXsub h
  have h1 : Reach (guPos D S) (gpos S Bl (Wh ∪ X)) :=
    reach_place_set X (by rw [disjoint_left]; intro w hw; simp [X] at hw; exact hw.2.1) hcard
  have hZprop : ∀ z ∈ Z, z ∉ S ∧ (z ∈ Bl ∨ z ∈ Wh ∪ X) ∧
      (z ∉ Bl → ∀ y, D.Adj y z → y ∉ S ∧ (y ∈ Bl ∨ y ∈ Wh ∪ X)) := by
    intro z hz
    simp only [Z, mem_insert, mem_filter, mem_univ, true_and] at hz
    -- a vertex outside `S` with a predecessor in `S` is black
    have hblack : ∀ w, w ∉ S → w ∉ Bl → ∀ y, D.Adj y w → y ∉ S := by
      intro w hwS hwB y hy hyS
      have hyw : y ≠ w := fun h => hwS (h ▸ hyS)
      exact hwB ((hmemBl w).mpr ⟨(hmemB w).mpr ⟨hwS, y, hyS, hyw, Or.inl hy⟩, y, hyS, hy⟩)
    rcases hz with rfl | ⟨hvz, hzS⟩
    · refine ⟨hv, hcover z (Or.inl rfl) hv, fun hzB y hy => ⟨hblack z hv hzB y hy, ?_⟩⟩
      by_cases hyz : y = z
      · exact hcover y (Or.inl hyz) (hyz ▸ hv)
      · exact hcover y (Or.inr ⟨Ne.symm hyz, Or.inr (Or.inl hy)⟩) (hblack z hv hzB y hy)
    · by_cases hzv : z = v
      · subst hzv
        refine ⟨hv, hcover z (Or.inl rfl) hv, fun hzB y hy => ⟨hblack z hv hzB y hy, ?_⟩⟩
        by_cases hyz : y = z
        · exact hcover y (Or.inl hyz) (hyz ▸ hv)
        · exact hcover y (Or.inr ⟨Ne.symm hyz, Or.inr (Or.inl hy)⟩) (hblack z hv hzB y hy)
      · refine ⟨hzS, hcover z (Or.inr ⟨Ne.symm hzv, Or.inl hvz⟩) hzS,
          fun hzB y hy => ⟨hblack z hzS hzB y hy, ?_⟩⟩
        have hyS := hblack z hzS hzB y hy
        by_cases hyv : y = v
        · exact hcover y (Or.inl hyv) hyS
        · by_cases hyz : y = z
          · subst hyz; exact hcover y (Or.inr ⟨Ne.symm hzv, Or.inl hvz⟩) hyS
          · exact hcover y (Or.inr ⟨Ne.symm hyv, Or.inr (Or.inr ⟨z, hvz, hy⟩)⟩) hyS
  have h2 : Reach (gpos S Bl (Wh ∪ X)) (gpos S (Bl ∪ Z) (Wh ∪ X)) := by
    refine reach_turn_set Z hZprop (le_trans (card_le_card ?_) hcard) ?_
    · intro w hw; simpa [union_assoc] using hw
    · intro z hz
      rcases (hZprop z hz).2.1 with h | h
      · exact mem_union_left _ h
      · exact mem_union_right _ h
  have h3 : Reach (gpos S (Bl ∪ Z) (Wh ∪ X)) (gpos (insert v S) (Bl ∪ Z) (Wh ∪ X)) := by
    refine reach_remove hv (mem_union_right _ (mem_insert_self _ _)) ?_
    refine le_trans (card_le_card ?_) (show B'.card ≤ K by omega)
    intro w hw
    simp only [mem_sdiff, mem_union, mem_insert, not_or] at hw
    obtain ⟨hw, hwv, hwS⟩ := hw
    have : w ∈ insert v B' := by
      rcases hw with (h | h) | (h | h)
      · exact hBsub (hBlB h)
      · exact hZsub h
      · exact hBsub (hWhB h)
      · exact hXsub h
    exact (mem_insert.mp this).resolve_left hwv
  have heq : gpos (insert v S) (Bl ∪ Z) (Wh ∪ X) = guPos D (insert v S) := by
    funext w
    simp only [guPos, gpos]
    by_cases hw : w ∈ insert v S
    · simp [hw]
    · have hwv : w ≠ v := fun h => hw (by simp [h])
      have hwS : w ∉ S := fun h => hw (mem_insert_of_mem h)
      have hbl : w ∈ Bl ∪ Z ↔ w ∈ guBlack D (insert v S) := by
        simp only [guBlack, mem_filter, mem_union]
        constructor
        · rintro (h | h)
          · obtain ⟨hwB, u, huS, huw⟩ := (hmemBl w).mp h
            exact ⟨(mem_insert.mp (hBsub hwB)).resolve_left hwv, u, mem_insert_of_mem huS, huw⟩
          · simp only [Z, mem_insert, mem_filter, mem_univ, true_and, hwv, false_or] at h
            exact ⟨hnbr w ⟨Ne.symm hwv, Or.inl h.1⟩ hwS, v, mem_insert_self _ _, h.1⟩
        · rintro ⟨-, u, hu, huw⟩
          rcases mem_insert.mp hu with rfl | huS
          · right; simp [Z, huw, hwS]
          · left
            have huw' : u ≠ w := fun h => hwS (h ▸ huS)
            exact (hmemBl w).mpr ⟨(hmemB w).mpr ⟨hwS, u, huS, huw', Or.inl huw⟩, u, huS, huw⟩
      have hwh : w ∉ Bl ∪ Z → (w ∈ Wh ∪ X ↔ w ∈ guWhite D (insert v S)) := by
        intro hn
        have hnb : w ∉ guBlack D (insert v S) := fun h => hn (hbl.mpr h)
        have hB'iff : w ∈ guWhite D (insert v S) ↔ w ∈ B' := by
          simp only [guWhite, mem_filter]
          exact ⟨fun h => h.1, fun h => ⟨h, fun hex => hnb (by
            simp only [guBlack, mem_filter]; exact ⟨h, hex⟩)⟩⟩
        rw [hB'iff]
        constructor
        · intro h
          rcases mem_union.mp h with h | h
          · exact (mem_insert.mp (hBsub (hWhB h))).resolve_left hwv
          · exact (mem_insert.mp (hXsub h)).resolve_left hwv
        · intro h
          obtain ⟨-, u, hu, huw⟩ := (hmemB' w).mp h
          rcases mem_insert.mp hu with rfl | huS
          · rcases hcover w (Or.inr huw) hwS with h' | h'
            · exact absurd (mem_union_left _ h') hn
            · exact h'
          · have hwB : w ∈ B := (hmemB w).mpr ⟨hwS, u, huS, huw⟩
            rw [← hBW] at hwB
            rcases mem_union.mp hwB with h' | h'
            · exact absurd (mem_union_left _ h') hn
            · exact mem_union_left _ h'
      simp only [hw, ↓reduceIte]
      by_cases hb : w ∈ Bl ∪ Z
      · have hb' := hbl.mp hb
        simp only [hb, hb', ↓reduceIte]
      · have hb' : w ∉ guBlack D (insert v S) := fun h => hb (hbl.mpr h)
        simp only [hb, hb', ↓reduceIte]
        exact if_congr (hwh hb) rfl rfl
  rw [← heq]
  exact h1.trans (h2.trans h3)

theorem guPos_empty : guPos D ∅ = fun _ => fresh := by
  funext w; simp [guPos, gpos, guBlack, guWhite, outerBoundary]

theorem guPos_univ : guPos D univ = fun _ => done := by
  funext w; simp [guPos, gpos]

/-- **Theorem 2 (⇐)**, from any layout of `G_u`: clearing the vertices in layout order pebbles
`D` progressively with at most `vs + 1` pebbles. -/
theorem pebblesWithin_of_layout_lengauerU (σ : LinearLayout α)
    (h : ∀ i, i < Fintype.card α → vertexSepAt (lengauerU D) σ i + 1 ≤ K) :
    PebblesWithin D K := by
  classical
  let Tset : ℕ → Finset α := fun i => univ.filter fun v => (σ v).val < i
  have hstep : ∀ i ≤ Fintype.card α, Reach (guPos D ∅) (guPos D (Tset i)) := by
    intro i hi
    induction i with
    | zero =>
      have : Tset 0 = ∅ := by ext; simp [Tset]
      rw [this]
    | succ i ih =>
      have hi' : i < Fintype.card α := by omega
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
      have hbd : outerBoundary (lengauerU D) (Tset (i + 1)) = activeSuffix (lengauerU D) σ i := by
        ext w
        simp only [mem_outerBoundary, mem_activeSuffix_iff, mem_prefixSet_iff, Tset,
          mem_filter, mem_univ, true_and, Nat.lt_succ_iff, not_le, gt_iff_lt]
      refine (ih (by omega)).trans ?_
      rw [hins]
      rw [hins] at hbd
      refine reach_guPos_insert hvT ?_
      rw [hbd]; exact h i hi'
  have hall : Tset (Fintype.card α) = univ := by ext v; simp [Tset]
  have := hstep _ le_rfl
  rw [hall, guPos_univ, guPos_empty] at this
  exact this

end Upper

/-! ### Theorem 2 -/

section Theorem2

variable {α : Type*} [Fintype α] [DecidableEq α] (D : Digraph α) [DecidableRel D.Adj]

/-- **Lengauer (1981) Theorem 2, with `vs`**: for every digraph and every `K ≥ 0`,
`D` can be pebbled progressively with `K + 1` pebbles iff `vs(G_u) ≤ K`. Acyclicity is not
used: the statement holds for the game on any digraph. -/
theorem pebblesWithin_iff_lengauerU (K : ℕ) :
    PebblesWithin D (K + 1) ↔ vertexSeparation (lengauerU D) ≤ K := by
  refine ⟨vertexSeparation_lengauerU_le_of_pebblesWithin, fun h => ?_⟩
  obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation (lengauerU D)
  exact pebblesWithin_of_layout_lengauerU σ fun i hi => by
    have := ((vertexSepOfLayout_le_iff _ σ _).mp (hσ.trans_le h)) i hi
    omega

/-- **Lengauer (1981) Theorem 2, as stated** (p. 469): "`(G, K)` is a positive instance of
PBWP if and only if `(G_u, K − 1)` is a positive instance of VSG", for every `K ≥ 2`. -/
theorem isPositivePBWP_iff_isPositiveVSG_lengauerU {K : ℕ} (hK : 2 ≤ K) :
    IsPositivePBWP D K ↔ IsPositiveVSG (lengauerU D) (K - 1) := by
  obtain ⟨K', rfl⟩ : ∃ K', K = K' + 1 := ⟨K - 1, by omega⟩
  rw [isPositiveVSG_iff, IsPositivePBWP, pebblesWithin_iff_lengauerU]
  simp only [Nat.add_sub_cancel]
  omega

/-- **The edge case at `K = 1`** (census P.3): on a nonempty digraph with no arcs,
`(D, 1)` is a positive instance of PBWP, while `(G_u, 0)` is no instance of VSG. Theorem 2
as stated fails there; read with `vs` (`pebblesWithin_iff_lengauerU`) it holds. -/
theorem isPositivePBWP_one_not_isPositiveVSG_zero (h : ∀ u v, ¬ D.Adj u v) :
    IsPositivePBWP D 1 ∧ ¬ IsPositiveVSG (lengauerU D) (1 - 1) := by
  refine ⟨⟨Nat.one_pos, (pebblesWithin_iff_lengauerU D 0).mpr ?_⟩, fun h' => ?_⟩
  · obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation (lengauerU D)
    rw [← hσ, Nat.le_zero, ← Nat.le_zero, vertexSepOfLayout_le_iff]
    intro i _
    unfold vertexSepAt
    rw [Nat.le_zero, card_eq_zero, eq_empty_iff_forall_notMem]
    intro w hw
    obtain ⟨-, u, -, huw⟩ := (mem_activeSuffix_iff _ σ i w).mp hw
    obtain ⟨-, h1 | h1 | ⟨x, h1, -⟩⟩ := huw
    · exact h _ _ h1
    · exact h _ _ h1
    · exact h _ _ h1
  · exact absurd ((isPositiveVSG_iff _ _).mp h').1 (by simp)

/-- **The pebbling number**: `pbw(D) = vs(G_u) + 1` for every nonempty digraph. -/
theorem pbw_eq_vertexSeparation_lengauerU_add_one [Nonempty α] :
    pbw D = vertexSeparation (lengauerU D) + 1 := by
  have hmem : vertexSeparation (lengauerU D) + 1 ∈ {K | PebblesWithin D K} :=
    (pebblesWithin_iff_lengauerU D _).mpr le_rfl
  unfold pbw
  apply le_antisymm (Nat.sInf_le hmem)
  apply le_csInf ⟨_, hmem⟩
  intro K hK
  have h1 := one_le_of_pebblesWithin' (Classical.arbitrary α) hK
  obtain ⟨K', rfl⟩ : ∃ K', K = K' + 1 := ⟨K - 1, by omega⟩
  have := (pebblesWithin_iff_lengauerU D K').mp hK
  omega

/-- `pbw(D) = pw(G_u) + 1` for every nonempty digraph (with Kinnersley's theorem). -/
theorem pbw_eq_pathwidth_lengauerU_add_one [Nonempty α] :
    pbw D = pathwidth (lengauerU D) + 1 := by
  rw [pbw_eq_vertexSeparation_lengauerU_add_one, vertexSeparation_eq_pathwidth]

/-- `pbw(D) = VSG(G_u) + 1` when `D` has an arc between two distinct vertices: Theorem 2 as a
number, with Lengauer's VSG. -/
theorem pbw_eq_vsg_lengauerU_add_one {u v : α} (huv : u ≠ v) (h : D.Adj u v) :
    pbw D = vsg (lengauerU D) + 1 := by
  have : Nonempty α := ⟨u⟩
  rw [pbw_eq_vertexSeparation_lengauerU_add_one,
    vsg_eq_vertexSeparation (lengauerU D) (show (lengauerU D).Adj u v from ⟨huv, Or.inl h⟩)]

/-- The MOSP instance of a digraph (census P.2): a customer and a product per vertex, product
`p` needed by `p` and by its immediate predecessors, i.e. column `p` is `N⁻[p]`. -/
def pebbleMatrix : MOSPInstance α α := ⟨fun c p => c = p ∨ D.Adj c p⟩

instance : DecidableRel (pebbleMatrix D).requires :=
  fun _ _ => inferInstanceAs (Decidable (_ ∨ _))

/-- `G_u` is the MOSP graph of the matrix whose columns are the closed in-neighbourhoods. -/
theorem mospGraph_pebbleMatrix : (pebbleMatrix D).mospGraph = lengauerU D := by
  ext c d
  rw [MOSPInstance.mospGraph_adj_iff, lengauerU_adj]
  simp only [pebbleMatrix]
  constructor
  · rintro ⟨hne, p, hc | hc, hd | hd⟩
    · exact absurd (hc.trans hd.symm) hne
    · subst hc; exact ⟨hne, Or.inr (Or.inl hd)⟩
    · subst hd; exact ⟨hne, Or.inl hc⟩
    · exact ⟨hne, Or.inr (Or.inr ⟨p, hc, hd⟩)⟩
  · rintro ⟨hne, h | h | ⟨x, h1, h2⟩⟩
    · exact ⟨hne, d, Or.inr h, Or.inl rfl⟩
    · exact ⟨hne, c, Or.inl rfl, Or.inr h⟩
    · exact ⟨hne, x, Or.inr h1, Or.inr h2⟩

/-- **`pbw(D) = Z(M_D)`**: the progressive black-white pebble demand of a nonempty digraph is
the minimum number of open stacks of its MOSP instance (with `MOSPGraph.lean`). -/
theorem pbw_eq_mospValue_pebbleMatrix [Nonempty α] :
    pbw D = (pebbleMatrix D).mospValue := by
  obtain ⟨c⟩ := ‹Nonempty α›
  rw [MOSPInstance.mospValue_eq_pathwidth_add_one _ ⟨c, c, Or.inl rfl⟩,
    mospGraph_pebbleMatrix, pbw_eq_pathwidth_lengauerU_add_one]

end Theorem2

/-! ### Kirousis & Papadimitriou's black game, and directives -/

section BlackGame

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- The moves of the progressive black pebble game (KP p. 205): place a pebble on a vertex
all of whose immediate predecessors are pebbled (rule (i)), delete a pebble (rule (ii)). -/
inductive BlackMove (α : Type*)
  | place (x : α)
  | remove (x : α)

namespace BlackMove

/-- Legality; progressiveness ("each vertex can be pebbled only once", p. 206) is built in:
only a never-pebbled vertex receives a pebble. -/
def Legal (D : Digraph α) (P : PebblePosition α) : BlackMove α → Prop
  | place x => P x = fresh ∧ ∀ y, D.Adj y x → (P y).Pebbled
  | remove x => P x = black

/-- The position after the move. -/
def apply : BlackMove α → PebblePosition α → PebblePosition α
  | place x, P => Function.update P x black
  | remove x, P => Function.update P x done

end BlackMove

/-- One legal move of the black game, after which at most `K` pebbles are on the graph. -/
def BlackStep (D : Digraph α) (K : ℕ) (P Q : PebblePosition α) : Prop :=
  ∃ m : BlackMove α, m.Legal D P ∧ Q = m.apply P ∧ numPebbles Q ≤ K

/-- `D` can be pebbled progressively in the black game with at most `K` pebbles. -/
def BlackPebblesWithin (D : Digraph α) (K : ℕ) : Prop :=
  Relation.ReflTransGen (BlackStep D K) (fun _ => fresh) (fun _ => done)

/-- The progressive black pebble demand `pb(D)` (KP p. 206). -/
noncomputable def pb (D : Digraph α) : ℕ := sInf {K | BlackPebblesWithin D K}

theorem numPebbles_update_white_eq_black (P : PebblePosition α) (x : α) :
    numPebbles (Function.update P x white) = numPebbles (Function.update P x black) := by
  unfold numPebbles
  congr 1
  apply filter_congr
  intro y _
  by_cases hy : y = x
  · subst hy; simp [Pebbled]
  · simp [Function.update_of_ne hy]

/-- A black move is a black-white play of one or two moves: place white and turn at once. -/
theorem BlackStep.reflTransGen {D : Digraph α} {K : ℕ} {P Q : PebblePosition α}
    (h : BlackStep D K P Q) : Relation.ReflTransGen (PebbleStep D K) P Q := by
  obtain ⟨m, hm, rfl, hc⟩ := h
  cases m with
  | place x =>
    obtain ⟨hx, hp⟩ := hm
    set P₁ := (PebbleMove.place x).apply P
    have hP₁ : P₁ = Function.update P x white := rfl
    refine Relation.ReflTransGen.head (b := P₁) ⟨.place x, hx, rfl, ?_⟩
      (Relation.ReflTransGen.single ⟨.turn x, ⟨by simp [hP₁], fun y hy => ?_⟩, ?_, hc⟩)
    · rw [hP₁, numPebbles_update_white_eq_black]; exact hc
    · by_cases hyx : y = x
      · subst hyx; simp [hP₁, Pebbled]
      · rw [hP₁, Function.update_of_ne hyx]; exact hp y hy
    · simp [hP₁, BlackMove.apply, PebbleMove.apply, PebbleMove.target, PebbleMove.result]
  | remove x =>
    exact Relation.ReflTransGen.single ⟨.remove x, hm, rfl, hc⟩

/-- Every progressive black pebbling is a progressive black-white pebbling. -/
theorem BlackPebblesWithin.pebblesWithin {D : Digraph α} {K : ℕ}
    (h : BlackPebblesWithin D K) : PebblesWithin D K := by
  have key : ∀ {P Q : PebblePosition α}, Relation.ReflTransGen (BlackStep D K) P Q →
      Relation.ReflTransGen (PebbleStep D K) P Q := by
    intro P Q h
    induction h with
    | refl => exact .refl
    | tail _ hs ih => exact ih.trans hs.reflTransGen
  exact key h

/-- `D` is a **directive** of `G` (KP p. 213): a dag "whose underlying directed graph equals
`G`", i.e. an acyclic orientation of `G`. -/
structure IsDirective (G : SimpleGraph α) (D : Digraph α) : Prop where
  adj_of : ∀ u v, D.Adj u v → G.Adj u v
  orient : ∀ u v, G.Adj u v → D.Adj u v ∨ D.Adj v u
  antisymm : ∀ u v, D.Adj u v → ¬ D.Adj v u
  acyclic : ∀ v, ¬ Relation.TransGen D.Adj v v

/-- `mpb(G) = min_{D ∈ Δ(G)} pb(D)` (KP p. 213). -/
noncomputable def mpb (G : SimpleGraph α) : ℕ :=
  sInf {K | ∃ D : Digraph α, IsDirective G D ∧ BlackPebblesWithin D K}

/-- `mpbw(G) = min_{D ∈ Δ(G)} pbw(D)` (KP p. 213). -/
noncomputable def mpbw (G : SimpleGraph α) : ℕ :=
  sInf {K | ∃ D : Digraph α, IsDirective G D ∧ PebblesWithin D K}

end BlackGame

/-! ### Kirousis & Papadimitriou's Theorem 3.1 -/

section KP

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Vertex separation is monotone under adding edges. -/
theorem vertexSeparation_mono {H : SimpleGraph V} [DecidableRel H.Adj] (hGH : G ≤ H) :
    vertexSeparation G ≤ vertexSeparation H := by
  obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation H
  refine (vertexSeparation_le_vertexSepOfLayout G σ).trans ?_
  rw [← hσ, vertexSepOfLayout_le_iff]
  intro i hi
  refine le_trans (card_le_card fun w hw => ?_) (vertexSepAt_le_vertexSepOfLayout H σ ⟨i, hi⟩)
  obtain ⟨h1, u, hu, huw⟩ := (mem_activeSuffix_iff G σ i w).mp hw
  exact (mem_activeSuffix_iff H σ i w).mpr ⟨h1, u, hu, hGH huw⟩

/-- The lower bound: every progressive black-white pebbling of a directive of a nonempty `G`
uses at least `vs(G) + 1` pebbles, because `G ≤ D_u` (Lengauer's Theorem 2). -/
theorem vertexSeparation_add_one_le_of_directive [Nonempty V] {D : Digraph V}
    (hD : IsDirective G D) {K : ℕ} (h : PebblesWithin D K) : vertexSeparation G + 1 ≤ K := by
  classical
  have h1 := one_le_of_pebblesWithin' (Classical.arbitrary V) h
  obtain ⟨K', rfl⟩ : ∃ K', K = K' + 1 := ⟨K - 1, by omega⟩
  have hU := vertexSeparation_lengauerU_le_of_pebblesWithin h
  have hle : G ≤ lengauerU D := fun u v huv =>
    ⟨huv.ne, (hD.orient u v huv).elim Or.inl (fun h => Or.inr (Or.inl h))⟩
  have := vertexSeparation_mono G hle
  omega

/-- The orientation of `G` along a layout: `u → w` iff `u` comes first. -/
def layoutOrient (σ : LinearLayout V) : Digraph V where
  Adj u w := G.Adj u w ∧ σ u < σ w

theorem layoutOrient_isDirective (σ : LinearLayout V) : IsDirective G (layoutOrient G σ) where
  adj_of _ _ h := h.1
  orient u v h := by
    rcases lt_trichotomy (σ u) (σ v) with hlt | heq | hgt
    · exact Or.inl ⟨h, hlt⟩
    · exact absurd (σ.injective heq) h.ne
    · exact Or.inr ⟨h.symm, hgt⟩
  antisymm _ _ h h' := lt_asymm h.2 h'.2
  acyclic v h := by
    have : ∀ a b, Relation.TransGen (layoutOrient G σ).Adj a b → σ a < σ b := by
      intro a b hab
      induction hab with
      | single h => exact h.2
      | tail _ h ih => exact ih.trans h.2
    exact lt_irrefl _ (this v v h)

end KP

section KPStrategy

variable {V : Type*} [Fintype V] [DecidableEq V] {G : SimpleGraph V} [DecidableRel G.Adj]
variable {K : ℕ} (σ : LinearLayout V)

local notation "BReach" => Relation.ReflTransGen (BlackStep (layoutOrient G σ) K)

variable (G) in
/-- After the first `i` vertices of `σ` are placed: those with no later neighbour are
cleared. -/
def kpDone (i : ℕ) : Finset V :=
  univ.filter fun w => (σ w).val < i ∧ ∀ u, G.Adj w u → (σ u).val < i

variable (G) in
/-- ... and those with a neighbour at `i` or later carry black pebbles (Kinnersley's
`V_L(i − 1)`, Kornai & Tuza's shack). -/
def kpBlack (i : ℕ) : Finset V :=
  univ.filter fun w => (σ w).val < i ∧ ∃ u, G.Adj w u ∧ i ≤ (σ u).val

theorem breach_place {S Bl : Finset V} {x : V} (hxS : x ∉ S) (hxB : x ∉ Bl)
    (hp : ∀ y, (layoutOrient G σ).Adj y x → y ∉ S ∧ y ∈ Bl)
    (hK : ((insert x Bl ∪ ∅) \ S).card ≤ K) :
    BReach (gpos S Bl ∅) (gpos S (insert x Bl) ∅) := by
  refine Relation.ReflTransGen.single ⟨.place x, ⟨by simp [gpos, hxS, hxB], fun y hy => ?_⟩,
    ?_, (numPebbles_gpos_le _ _ _).trans hK⟩
  · obtain ⟨hyS, hyB⟩ := hp y hy; simp [gpos, hyS, hyB, Pebbled]
  · funext w
    by_cases hw : w = x
    · subst hw; simp [BlackMove.apply, gpos, hxS]
    · simp [BlackMove.apply, gpos, hw]

theorem breach_remove_set {S Bl : Finset V} (R : Finset V) (hRS : Disjoint R S) (hRB : R ⊆ Bl)
    (hK : ((Bl ∪ ∅) \ S).card ≤ K) :
    BReach (gpos S Bl ∅) (gpos (S ∪ R) Bl ∅) := by
  induction R using Finset.induction_on with
  | empty => simp only [union_empty]; exact .refl
  | insert x R hx ih =>
    have hxS : x ∉ S := disjoint_left.mp hRS (mem_insert_self _ _)
    refine (ih (disjoint_of_subset_left (subset_insert _ _) hRS)
      ((subset_insert _ _).trans hRB)).trans ?_
    rw [union_insert]
    have hxSR : x ∉ S ∪ R := by simp [hxS, hx]
    have hxB : x ∈ Bl := hRB (mem_insert_self _ _)
    refine Relation.ReflTransGen.single ⟨.remove x, by simp [BlackMove.Legal, gpos, hxSR, hxB],
      ?_, (numPebbles_gpos_le _ _ _).trans (le_trans (card_le_card
        (sdiff_subset_sdiff le_rfl (subset_union_left.trans (subset_insert _ _)))) hK)⟩
    funext w
    by_cases hw : w = x
    · subst hw; simp [BlackMove.apply, gpos]
    · simp [BlackMove.apply, gpos, hw]

/-- One step of the black strategy: place `vᵢ` (its predecessors are its earlier neighbours,
all black), then clear every vertex with no neighbour after `i`. The pebbles in play are
Kornai & Tuza's shack just after `vᵢ` is put in. -/
theorem breach_step {i : ℕ} (hi : i < Fintype.card V)
    (hK : (shackAfterPut G σ i).card ≤ K) :
    BReach (gpos (kpDone G σ i) (kpBlack G σ i) ∅)
      (gpos (kpDone G σ (i + 1)) (kpBlack G σ (i + 1)) ∅) := by
  classical
  set v := σ.symm ⟨i, hi⟩
  have hv : (σ v).val = i := by simp [v]
  have hσeq : ∀ w, (σ w).val = i → w = v := fun w hw => by
    rw [Equiv.eq_symm_apply]; exact Fin.ext hw
  set S := kpDone G σ i
  set Bl := insert v (kpBlack G σ i)
  have hshack : Bl ⊆ shackAfterPut G σ i := by
    intro w hw
    rw [mem_shackAfterPut_iff]
    rcases mem_insert.mp hw with h | hw
    · rw [h]; exact ⟨hv.le, v, Or.inl rfl, hv.ge⟩
    · simp only [kpBlack, mem_filter, mem_univ, true_and] at hw
      obtain ⟨h1, u, hu, h2⟩ := hw
      exact ⟨h1.le, u, Or.inr hu, h2⟩
  have hcard : ((Bl ∪ ∅) \ S).card ≤ K :=
    le_trans (card_le_card (by rw [union_empty]; exact sdiff_subset.trans hshack)) hK
  have h1 : BReach (gpos S (kpBlack G σ i) ∅) (gpos S Bl ∅) := by
    refine breach_place σ (by simp [S, kpDone, hv]) (by simp [kpBlack, hv]) ?_ hcard
    intro y ⟨hyv, hlt⟩
    rw [Fin.lt_def, hv] at hlt
    refine ⟨fun h => ?_, ?_⟩
    · simp only [S, kpDone, mem_filter, mem_univ, true_and] at h
      exact absurd (h.2 v hyv) (by omega)
    · simp only [kpBlack, mem_filter, mem_univ, true_and]
      exact ⟨hlt, v, hyv, hv.ge⟩
  set R := Bl.filter fun w => ∀ u, G.Adj w u → (σ u).val ≤ i
  have hRS : Disjoint R S := by
    rw [disjoint_left]
    intro w hw hwS
    simp only [R, Bl, mem_filter, mem_insert] at hw
    simp only [S, kpDone, mem_filter, mem_univ, true_and] at hwS
    rcases hw.1 with rfl | hw'
    · omega
    · simp only [kpBlack, mem_filter, mem_univ, true_and] at hw'
      obtain ⟨-, u, hu, h⟩ := hw'
      have := hwS.2 u hu; omega
  have h2 : BReach (gpos S Bl ∅) (gpos (S ∪ R) Bl ∅) :=
    breach_remove_set σ R hRS (filter_subset _ _) hcard
  have heq : gpos (S ∪ R) Bl ∅ = gpos (kpDone G σ (i + 1)) (kpBlack G σ (i + 1)) ∅ := by
    have hdone : ∀ w, w ∈ S ∪ R ↔ w ∈ kpDone G σ (i + 1) := by
      intro w
      simp only [S, R, Bl, kpDone, kpBlack, mem_union, mem_filter, mem_insert, mem_univ,
        true_and]
      constructor
      · rintro (⟨h1, h2⟩ | ⟨h1 | ⟨h1, -⟩, h2⟩)
        · exact ⟨by omega, fun u hu => by have := h2 u hu; omega⟩
        · subst h1; exact ⟨by omega, fun u hu => by have := h2 u hu; omega⟩
        · exact ⟨by omega, fun u hu => by have := h2 u hu; omega⟩
      · rintro ⟨h1, h2⟩
        rcases Nat.lt_succ_iff_lt_or_eq.mp h1 with h1 | h1
        · by_cases hall : ∀ u, G.Adj w u → (σ u).val < i
          · exact Or.inl ⟨h1, hall⟩
          · push Not at hall
            obtain ⟨u, hu, hge⟩ := hall
            exact Or.inr ⟨Or.inr ⟨h1, u, hu, hge⟩, fun u hu => by have := h2 u hu; omega⟩
        · exact Or.inr ⟨Or.inl (hσeq w h1), fun u hu => by have := h2 u hu; omega⟩
    have hblack : ∀ w, w ∉ kpDone G σ (i + 1) → (w ∈ Bl ↔ w ∈ kpBlack G σ (i + 1)) := by
      intro w hwd
      simp only [kpDone, mem_filter, mem_univ, true_and, not_and, not_forall] at hwd
      simp only [Bl, kpBlack, mem_insert, mem_filter, mem_univ, true_and]
      constructor
      · rintro (rfl | ⟨h1, -⟩)
        · obtain ⟨u, hu, hlt⟩ := hwd (by omega)
          exact ⟨by omega, u, hu, by omega⟩
        · obtain ⟨u, hu, hlt⟩ := hwd (by omega)
          exact ⟨by omega, u, hu, by omega⟩
      · rintro ⟨h1, u, hu, h2⟩
        rcases Nat.lt_succ_iff_lt_or_eq.mp h1 with h1 | h1
        · exact Or.inr ⟨h1, u, hu, by omega⟩
        · exact Or.inl (hσeq w h1)
    funext w
    simp only [gpos, notMem_empty, ↓reduceIte]
    by_cases hw : w ∈ kpDone G σ (i + 1)
    · have hw' := (hdone w).mpr hw
      simp only [hw, hw', ↓reduceIte]
    · have hw' : w ∉ S ∪ R := fun h => hw ((hdone w).mp h)
      simp only [hw, hw', ↓reduceIte]
      exact if_congr (hblack w hw) rfl rfl
  rw [← heq]
  exact h1.trans h2

/-- **KP Theorem 3.1 (≤), for the black game**: orienting `G` along a layout `σ` and pebbling
in layout order uses, at step `i`, the shack of `σ` just after `vᵢ` is put in, which has
`vs(σ reversed)` plus one vertices. -/
theorem blackPebblesWithin_layoutOrient
    (h : ∀ i, i < Fintype.card V → (shackAfterPut G σ i).card ≤ K) :
    BlackPebblesWithin (layoutOrient G σ) K := by
  have hstep : ∀ i ≤ Fintype.card V,
      BReach (gpos (kpDone G σ 0) (kpBlack G σ 0) ∅) (gpos (kpDone G σ i) (kpBlack G σ i) ∅) := by
    intro i hi
    induction i with
    | zero => exact .refl
    | succ i ih => exact (ih (by omega)).trans (breach_step σ (by omega) (h i (by omega)))
  have h0 : gpos (kpDone G σ 0) (kpBlack G σ 0) ∅ = fun _ => fresh := by
    funext w; simp [gpos, kpDone, kpBlack]
  have hn : gpos (kpDone G σ (Fintype.card V)) (kpBlack G σ (Fintype.card V)) ∅ =
      fun _ => done := by
    funext w
    have : w ∈ kpDone G σ (Fintype.card V) := by
      simp only [kpDone, mem_filter, mem_univ, true_and]
      exact ⟨(σ w).isLt, fun u _ => (σ u).isLt⟩
    simp [gpos, this]
  have := hstep _ le_rfl
  rw [h0, hn] at this
  exact this

end KPStrategy

section KPTheorem

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- There is a directive of `G` that can be pebbled in the black game with `vs(G) + 1`
pebbles: orient along the reverse of an optimal layout. -/
theorem exists_directive_blackPebblesWithin [Nonempty V] :
    ∃ D : Digraph V, IsDirective G D ∧ BlackPebblesWithin D (vertexSeparation G + 1) := by
  obtain ⟨σ₀, hσ₀⟩ := exists_layout_vertexSeparation G
  refine ⟨layoutOrient G (reverseLayout σ₀), layoutOrient_isDirective G _,
    blackPebblesWithin_layoutOrient _ fun i hi => ?_⟩
  have := card_shackAfterPut G (reverseLayout σ₀) ⟨i, hi⟩
  rw [reverseLayout_reverseLayout] at this
  rw [this, ← hσ₀]
  exact Nat.add_le_add_right (vertexSepAt_le_vertexSepOfLayout G σ₀ _) 1

/-- `mpbw(G) ≤ mpb(G)` (KP p. 213, "immediate"). -/
theorem mpbw_le_mpb [Nonempty V] : mpbw G ≤ mpb G := by
  obtain ⟨D, hD, hb⟩ := exists_directive_blackPebblesWithin G
  refine le_csInf ⟨vertexSeparation G + 1, D, hD, hb⟩ ?_
  rintro K ⟨D', hD', hK⟩
  exact Nat.sInf_le ⟨D', hD', hK.pebblesWithin⟩

/-- **Kirousis & Papadimitriou (1986) Theorem 3.1, with Theorem 4.1, as item 01 settled it**:
`mpb(G) = vs(G) + 1` for every nonempty graph. -/
theorem mpb_eq_vertexSeparation_add_one [Nonempty V] : mpb G = vertexSeparation G + 1 := by
  obtain ⟨D, hD, hb⟩ := exists_directive_blackPebblesWithin G
  refine le_antisymm (Nat.sInf_le (show vertexSeparation G + 1 ∈
    {K | ∃ D : Digraph V, IsDirective G D ∧ BlackPebblesWithin D K} from ⟨D, hD, hb⟩)) ?_
  refine le_csInf ⟨vertexSeparation G + 1, D, hD, hb⟩ ?_
  rintro K ⟨D', hD', hK⟩
  exact vertexSeparation_add_one_le_of_directive G hD' hK.pebblesWithin

/-- `mpbw(G) = vs(G) + 1` for every nonempty graph. -/
theorem mpbw_eq_vertexSeparation_add_one [Nonempty V] : mpbw G = vertexSeparation G + 1 := by
  obtain ⟨D, hD, hb⟩ := exists_directive_blackPebblesWithin G
  refine le_antisymm (Nat.sInf_le (show vertexSeparation G + 1 ∈
    {K | ∃ D : Digraph V, IsDirective G D ∧ PebblesWithin D K} from ⟨D, hD, hb.pebblesWithin⟩)) ?_
  refine le_csInf ⟨vertexSeparation G + 1, D, hD, hb.pebblesWithin⟩ ?_
  rintro K ⟨D', hD', hK⟩
  exact vertexSeparation_add_one_le_of_directive G hD' hK

/-- `mpb(G) = mpbw(G)`: the second equality of Theorem 3.1, on every nonempty graph. -/
theorem mpb_eq_mpbw [Nonempty V] : mpb G = mpbw G := by
  rw [mpb_eq_vertexSeparation_add_one, mpbw_eq_vertexSeparation_add_one]

/-- `mpb(G) = mpbw(G) = pw(G) + 1` (with Kinnersley's theorem). -/
theorem mpb_eq_pathwidth_add_one [Nonempty V] : mpb G = pathwidth G + 1 := by
  rw [mpb_eq_vertexSeparation_add_one, vertexSeparation_eq_pathwidth]

theorem mpbw_eq_pathwidth_add_one [Nonempty V] : mpbw G = pathwidth G + 1 := by
  rw [mpbw_eq_vertexSeparation_add_one, vertexSeparation_eq_pathwidth]

/-- **Theorem 3.1 as stated**, `mpb(G) = ns(G) = mpbw(G)`, for every graph with an edge
(with the full node search game of `NodeMonotonicity.lean`). -/
theorem mpb_eq_nodeSearch {u v : V} (huv : G.Adj u v) :
    mpb G = nodeSearch G ∧ nodeSearch G = mpbw G := by
  have : Nonempty V := ⟨u⟩
  rw [mpb_eq_vertexSeparation_add_one, mpbw_eq_vertexSeparation_add_one,
    nodeSearch_eq_vertexSeparation_add_one G huv]
  exact ⟨rfl, rfl⟩

/-- **The first equality of Theorem 3.1 is false on edgeless nonempty graphs** (census P.3):
there `ns(G) = 0`, but every vertex must receive a pebble, so `mpb(G) = mpbw(G) = 1`. -/
theorem mpb_ne_nodeSearch_of_edgeless [Nonempty V] (h : ∀ u v, ¬ G.Adj u v) :
    mpb G = 1 ∧ mpbw G = 1 ∧ nodeSearch G = 0 := by
  have hvs : vertexSeparation G = 0 := by
    obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation G
    rw [← hσ, ← Nat.le_zero, vertexSepOfLayout_le_iff]
    intro i _
    unfold vertexSepAt
    rw [Nat.le_zero, card_eq_zero, eq_empty_iff_forall_notMem]
    intro w hw
    obtain ⟨-, u, -, huw⟩ := (mem_activeSuffix_iff G σ i w).mp hw
    exact h u w huw
  refine ⟨?_, ?_, nodeSearch_of_edgeless G h⟩
  · rw [mpb_eq_vertexSeparation_add_one, hvs]
  · rw [mpbw_eq_vertexSeparation_add_one, hvs]

end KPTheorem

end Complex

end MOSPFormalization
