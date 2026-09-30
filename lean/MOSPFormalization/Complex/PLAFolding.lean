/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# PLA folding: not pathwidth + 1; multiple folding is

Table 1 of Linhares & Yanasse (2002), row "PLA folding", source [6] Möhring
(1990).

## The source's definition

Möhring (1990), p. 25, PLAMPP: given the net–gate matrix `M` of one plane of a
PLA, "find a permutation of the gates `G₁, …, Gₙ` and a feasible assignment of
at most two nets to a track (PLA layout) such that the number of tracks is
minimum". Feasible is the MPP condition of p. 18 (`GateMatrix.lean`): nets on
one track share no gate of the augmented matrix `M^π`. The same page: "The
folding allows two (sometimes also more) signals to share a row"; with no cap
on a track this is Möhring's *multiple folding* (p. 36, path partitions), and
the problem is the MPP itself.

Formalised here, on top of `GateMatrix.lean`:

* `IsFolding c π h` — a track assignment for `π` with at most `c` nets on each
  track;
* `foldTracks c` — the fewest tracks over all gate orders and such
  assignments;
* `plaTracks = foldTracks 2` — PLAMPP.

## What is proved

* `pathwidth_add_one_le_plaTracks` and `card_le_two_mul_plaTracks`: every PLA
  layout is an MPP layout and holds at most two nets per track, so
  `max(pw + 1, ⌈|N| / 2⌉) ≤ plaTracks` (when some net meets some gate), and
  `plaTracks ≤ |N|` (`plaTracks_le_card`).
* **Table 1's "equivalent up to ±1" is false for PLA folding as Möhring
  defines it**: on the `n × n` identity matrix (`idMatrix`) the net graph is
  edgeless, `pw + 1 = t = 1`, and `plaTracks = ⌈n / 2⌉`
  (`plaTracks_idMatrix`); at `n = 5`, 3 against 1
  (`plaTracks_idMatrix_five`), and the gap is unbounded
  (`plaTracks_idMatrix_unbounded`). The same holds on *connected* instances
  (several sources assume connectivity): the incidence matrix of a path
  (`pathMatrix n`, nets the `n + 1` vertices, gates the `n` edges) has a
  connected net graph (`netGraph_pathMatrix_connected`), `pw + 1 ≤ 2`
  (`tracks_pathMatrix_le_two`) and `plaTracks ≥ ⌈(n + 1) / 2⌉`;
  `plaTracks_pathMatrix_unbounded`.
* **Multiple folding is exact**: `foldTracks c = t(M)` as soon as
  `c ≥ |N|` (`foldTracks_eq_tracks`), so by `GateMatrix.lean`
  `foldTracks c = pw(netGraph M) + 1` (`foldTracks_eq_pathwidth_add_one`).
  This is the layout form of Möhring's Thm. 3.14 (path partitions ↔
  interval augmentation, `= θ = pw + 1`, Prop. 3.5).

Not formalised: Möhring's Prop. 3.15 (`plaTracks = |V(G)| − s`, `s` the
largest folding set without alternating cycle), Thm. 3.14 in its
path-partition vocabulary, and block / constrained folding (pp. 25–26).
The general relation between PLA folding and pathwidth is only the one-sided
bound above: a PLA layout needs `⌈|N| / 2⌉` tracks regardless of the graph.
-/

import MOSPFormalization.Complex.GateMatrix
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Connected

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

namespace NetGateMatrix

variable {N Gt : Type*} [Fintype N] [DecidableEq N] [Fintype Gt] [DecidableEq Gt]
variable (M : NetGateMatrix N Gt) [DecidableRel M.conn]

/-! ### Definitions from the source -/

/-- A folding with `k` tracks and at most `c` nets per track for the gate order
`π` (Möhring p. 25, with `c = 2` the PLA layout): a track assignment of `M^π`
in which every track holds at most `c` nets. -/
def IsFolding (c : ℕ) {k : ℕ} (π : LinearLayout Gt) (h : N → Fin k) : Prop :=
  M.IsTrackAssignment π h ∧ ∀ i : Fin k, (Finset.univ.filter (fun n => h n = i)).card ≤ c

/-- The fewest tracks of a folding with at most `c` nets per track, over all gate
orders. -/
noncomputable def foldTracks (c : ℕ) : ℕ :=
  sInf {k | ∃ π : LinearLayout Gt, ∃ h : N → Fin k, M.IsFolding c π h}

/-- **PLA folding** (Möhring 1990, p. 25, PLAMPP): at most two nets per track. -/
noncomputable def plaTracks : ℕ := M.foldTracks 2

/-! ### General bounds -/

/-- One net per track is a folding for every capacity `c ≥ 1`. -/
theorem card_mem_foldTracks {c : ℕ} (hc : 1 ≤ c) :
    Fintype.card N ∈ {k | ∃ π : LinearLayout Gt, ∃ h : N → Fin k, M.IsFolding c π h} := by
  refine ⟨Fintype.equivFin Gt, Fintype.equivFin N, ?_, ?_⟩
  · intro n n' hne heq
    exact absurd ((Fintype.equivFin N).injective heq) hne
  · intro i
    refine le_trans (Finset.card_le_one.mpr ?_) hc
    intro a ha b hb
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ha hb
    exact (Fintype.equivFin N).injective (ha.trans hb.symm)

theorem foldTracks_le_card {c : ℕ} (hc : 1 ≤ c) : M.foldTracks c ≤ Fintype.card N :=
  Nat.sInf_le (M.card_mem_foldTracks hc)

theorem exists_isFolding {c : ℕ} (hc : 1 ≤ c) :
    ∃ π : LinearLayout Gt, ∃ h : N → Fin (M.foldTracks c), M.IsFolding c π h :=
  Nat.sInf_mem ⟨_, M.card_mem_foldTracks hc⟩

/-- A folding is a gate matrix layout: `t(M) ≤ foldTracks c`. -/
theorem tracks_le_foldTracks {c : ℕ} (hc : 1 ≤ c) : M.tracks ≤ M.foldTracks c := by
  obtain ⟨π, h, hh, -⟩ := M.exists_isFolding hc
  exact Nat.sInf_le ⟨π, h, hh⟩

/-- A folding with `k` tracks of capacity `c` holds at most `c * k` nets. -/
theorem card_le_mul_of_isFolding {c k : ℕ} {π : LinearLayout Gt} {h : N → Fin k}
    (hh : M.IsFolding c π h) : Fintype.card N ≤ c * k := by
  have := Finset.card_le_mul_card_image (Finset.univ : Finset N) c
    (fun i _ => hh.2 i)
  calc Fintype.card N = (Finset.univ : Finset N).card := rfl
    _ ≤ c * (Finset.univ.image h).card := this
    _ ≤ c * k := by
        apply Nat.mul_le_mul_left
        simpa using Finset.card_le_univ (Finset.univ.image h)

theorem card_le_mul_foldTracks {c : ℕ} (hc : 1 ≤ c) :
    Fintype.card N ≤ c * M.foldTracks c := by
  obtain ⟨π, h, hh⟩ := M.exists_isFolding hc
  exact M.card_le_mul_of_isFolding hh

/-- **Multiple folding is the MPP**: with room for every net on one track, a
folding is just a track assignment, so `foldTracks c = t(M)`. -/
theorem foldTracks_eq_tracks {c : ℕ} (hc : Fintype.card N ≤ c) :
    M.foldTracks c = M.tracks := by
  unfold foldTracks tracks
  congr 1
  ext k
  constructor
  · rintro ⟨π, h, hh, -⟩
    exact ⟨π, h, hh⟩
  · rintro ⟨π, h, hh⟩
    exact ⟨π, h, hh, fun _ => (Finset.card_le_univ _).trans hc⟩

/-- **Multiple folding = pathwidth + 1** (Möhring Thm. 3.14 with Prop. 3.5),
whenever some net meets some gate. -/
theorem foldTracks_eq_pathwidth_add_one {c : ℕ} (hc : Fintype.card N ≤ c)
    (hreq : ∃ n g, M.conn n g) :
    M.foldTracks c = pathwidth M.netGraph + 1 := by
  rw [M.foldTracks_eq_tracks hc, M.tracks_eq_pathwidth_add_one hreq]

/-! ### PLA folding -/

theorem tracks_le_plaTracks : M.tracks ≤ M.plaTracks :=
  M.tracks_le_foldTracks (by omega)

/-- **PLA folding is at least pathwidth + 1** (every PLA layout is an MPP
layout). -/
theorem pathwidth_add_one_le_plaTracks (hreq : ∃ n g, M.conn n g) :
    pathwidth M.netGraph + 1 ≤ M.plaTracks := by
  rw [← M.tracks_eq_pathwidth_add_one hreq]
  exact M.tracks_le_plaTracks

/-- **PLA folding is at least half the nets**, whatever the graph. -/
theorem card_le_two_mul_plaTracks : Fintype.card N ≤ 2 * M.plaTracks :=
  M.card_le_mul_foldTracks (by omega)

theorem plaTracks_le_card : M.plaTracks ≤ Fintype.card N :=
  M.foldTracks_le_card (by omega)

end NetGateMatrix

/-! ### The identity matrix: an edgeless net graph -/

/-- The `n × n` identity matrix: net `i` meets gate `i` only. -/
def idMatrix (n : ℕ) : NetGateMatrix (Fin n) (Fin n) := ⟨fun i g => i = g⟩

instance (n : ℕ) : DecidableRel (idMatrix n).conn := fun i g =>
  (inferInstance : Decidable (i = g))

/-- The identity gate order on `Fin n`. -/
def finLayout (n : ℕ) : LinearLayout (Fin n) := finCongr (Fintype.card_fin n).symm

@[simp] theorem finLayout_val {n : ℕ} (g : Fin n) : (finLayout n g).val = g.val := rfl

theorem idMatrix_not_shareGate {n : ℕ} (π : LinearLayout (Fin n)) {i i' : Fin n}
    (hne : i ≠ i') : ¬ (idMatrix n).ShareGate π i i' := by
  rintro ⟨j, ⟨g₁, g₂, h₁, h₂, a₁, b₁⟩, ⟨g₃, g₄, h₃, h₄, a₂, b₂⟩⟩
  change i = g₁ at h₁; change i = g₂ at h₂; change i' = g₃ at h₃; change i' = g₄ at h₄
  subst h₁ h₂ h₃ h₄
  have : (π i).val = (π i').val := by omega
  exact hne (π.injective (Fin.ext this))

/-- Pairing nets `2a` and `2a + 1` on track `a` is a PLA layout of `idMatrix n`
with `⌈n / 2⌉` tracks. -/
theorem plaTracks_idMatrix_le (n : ℕ) : (idMatrix n).plaTracks ≤ (n + 1) / 2 := by
  have hlt : ∀ i : Fin n, i.val / 2 < (n + 1) / 2 := fun i => by omega
  refine Nat.sInf_le ⟨finLayout n, fun i => ⟨i.val / 2, hlt i⟩, ?_, ?_⟩
  · intro i i' hne _
    exact idMatrix_not_shareGate _ hne
  · intro t
    calc (Finset.univ.filter (fun i : Fin n => (⟨i.val / 2, hlt i⟩ : Fin _) = t)).card
        ≤ (Finset.univ : Finset (Fin 2)).card := by
          apply Finset.card_le_card_of_injOn (fun i => ⟨i.val % 2, Nat.mod_lt _ (by omega)⟩)
            (fun _ _ => Finset.mem_coe.mpr (Finset.mem_univ _))
          intro a ha b hb hab
          simp only [Finset.coe_filter, Finset.mem_univ, true_and, Set.mem_ofPred_eq] at ha hb
          have h1 : a.val / 2 = b.val / 2 := by
            have := congrArg Fin.val (ha.trans hb.symm)
            simpa using this
          have h2 : a.val % 2 = b.val % 2 := by
            have := congrArg Fin.val hab
            simpa using this
          exact Fin.ext (by omega)
      _ = 2 := by simp

/-- `plaTracks (idMatrix n) = ⌈n / 2⌉`. -/
theorem plaTracks_idMatrix (n : ℕ) : (idMatrix n).plaTracks = (n + 1) / 2 := by
  have h₁ := (idMatrix n).card_le_two_mul_plaTracks
  have h₂ := plaTracks_idMatrix_le n
  simp only [Fintype.card_fin] at h₁
  omega

theorem idMatrix_hreq {n : ℕ} (hn : 0 < n) : ∃ i g, (idMatrix n).conn i g :=
  ⟨⟨0, hn⟩, ⟨0, hn⟩, rfl⟩

/-- The identity matrix needs one gate matrix track. -/
theorem tracks_idMatrix {n : ℕ} (hn : 0 < n) : (idMatrix n).tracks = 1 := by
  apply le_antisymm
  · exact Nat.sInf_le ⟨finLayout n, fun _ => 0, fun i i' hne _ => idMatrix_not_shareGate _ hne⟩
  · rw [(idMatrix n).tracks_eq_pathwidth_add_one (idMatrix_hreq hn)]
    omega

/-- The net graph of the identity matrix has pathwidth `0`. -/
theorem pathwidth_idMatrix {n : ℕ} (hn : 0 < n) :
    pathwidth (idMatrix n).netGraph + 1 = 1 := by
  rw [← (idMatrix n).tracks_eq_pathwidth_add_one (idMatrix_hreq hn), tracks_idMatrix hn]

/-- **The counterexample** (item 01): the `5 × 5` identity matrix folds to three
PLA tracks against `pw + 1 = t = 1`, a gap of two. -/
theorem plaTracks_idMatrix_five :
    (idMatrix 5).plaTracks = 3 ∧ pathwidth (idMatrix 5).netGraph + 1 = 1 :=
  ⟨plaTracks_idMatrix 5, pathwidth_idMatrix (by omega)⟩

/-- No additive constant relates PLA folding to pathwidth + 1. -/
theorem plaTracks_idMatrix_unbounded (c : ℕ) :
    pathwidth (idMatrix (2 * c + 3)).netGraph + 1 + c < (idMatrix (2 * c + 3)).plaTracks := by
  rw [pathwidth_idMatrix (by omega), plaTracks_idMatrix]
  omega

/-! ### The incidence matrix of a path: a connected counterexample -/

/-- The incidence matrix of the path on `n + 1` vertices: nets are the vertices
`0, …, n`, gate `g` is the edge `{g, g + 1}`. -/
def pathMatrix (n : ℕ) : NetGateMatrix (Fin (n + 1)) (Fin n) :=
  ⟨fun i g => g.val = i.val ∨ g.val + 1 = i.val⟩

instance (n : ℕ) : DecidableRel (pathMatrix n).conn := fun i g =>
  (inferInstance : Decidable (g.val = i.val ∨ g.val + 1 = i.val))

theorem pathMatrix_adj {n : ℕ} (i : ℕ) (hi : i < n) :
    (pathMatrix n).netGraph.Adj ⟨i, by omega⟩ ⟨i + 1, by omega⟩ :=
  ⟨fun h => by simpa using congrArg Fin.val h, ⟨i, hi⟩, Or.inl rfl, Or.inr rfl⟩

/-- The net graph of `pathMatrix n` is the path, which is connected. -/
theorem netGraph_pathMatrix_connected (n : ℕ) : (pathMatrix n).netGraph.Connected := by
  have key : ∀ i (hi : i < n + 1),
      (pathMatrix n).netGraph.Reachable ⟨0, by omega⟩ ⟨i, hi⟩ := by
    intro i
    induction i with
    | zero => intro _; rfl
    | succ i ih =>
      intro hi
      exact (ih (by omega)).trans (pathMatrix_adj i (by omega)).reachable
  have : Nonempty (Fin (n + 1)) := ⟨0⟩
  exact ⟨fun a b => (key a.val a.isLt).symm.trans (key b.val b.isLt)⟩

/-- Alternating the vertices between two tracks is a gate matrix layout of the
path: `t ≤ 2`. -/
theorem tracks_pathMatrix_le_two (n : ℕ) : (pathMatrix n).tracks ≤ 2 := by
  refine Nat.sInf_le ⟨finLayout n, fun i => ⟨i.val % 2, Nat.mod_lt _ (by omega)⟩, ?_⟩
  intro i i' hne heq
  have hpar : i.val % 2 = i'.val % 2 := by simpa using congrArg Fin.val heq
  have hne' : i.val ≠ i'.val := fun h => hne (Fin.ext h)
  rintro ⟨j, ⟨g₁, g₂, h₁, h₂, a₁, b₁⟩, ⟨g₃, g₄, h₃, h₄, a₂, b₂⟩⟩
  simp only [finLayout_val] at a₁ b₁ a₂ b₂
  change g₁.val = i.val ∨ g₁.val + 1 = i.val at h₁
  change g₂.val = i.val ∨ g₂.val + 1 = i.val at h₂
  change g₃.val = i'.val ∨ g₃.val + 1 = i'.val at h₃
  change g₄.val = i'.val ∨ g₄.val + 1 = i'.val at h₄
  omega

theorem pathMatrix_hreq (n : ℕ) (hn : 0 < n) : ∃ i g, (pathMatrix n).conn i g :=
  ⟨⟨0, by omega⟩, ⟨0, hn⟩, Or.inl rfl⟩

theorem pathwidth_pathMatrix_le (n : ℕ) (hn : 0 < n) :
    pathwidth (pathMatrix n).netGraph + 1 ≤ 2 := by
  rw [← (pathMatrix n).tracks_eq_pathwidth_add_one (pathMatrix_hreq n hn)]
  exact tracks_pathMatrix_le_two n

/-- **Connected counterexample**: the path on seven vertices has `pw + 1 ≤ 2`
and needs at least four PLA tracks. -/
theorem plaTracks_pathMatrix_six :
    pathwidth (pathMatrix 6).netGraph + 1 + 2 ≤ (pathMatrix 6).plaTracks := by
  have h₁ := (pathMatrix 6).card_le_two_mul_plaTracks
  have h₂ := pathwidth_pathMatrix_le 6 (by omega)
  simp only [Fintype.card_fin] at h₁
  omega

/-- On connected instances too, no additive constant relates PLA folding to
pathwidth + 1. -/
theorem plaTracks_pathMatrix_unbounded (c : ℕ) :
    pathwidth (pathMatrix (2 * c + 4)).netGraph + 1 + c < (pathMatrix (2 * c + 4)).plaTracks := by
  have h₁ := (pathMatrix (2 * c + 4)).card_le_two_mul_plaTracks
  have h₂ := pathwidth_pathMatrix_le (2 * c + 4) (by omega)
  simp only [Fintype.card_fin] at h₁
  omega

end Complex

end MOSPFormalization
