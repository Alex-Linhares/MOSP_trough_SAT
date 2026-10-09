/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# One-dimensional logic: tracks = interval thickness = pathwidth + 1

Table 1 of Linhares & Yanasse (2002), row "one-dimensional logic", source [7]
Ohtsuki, Mori, Kuh, Kashiwabara & Fujisawa (1979), "One-dimensional logic gate
assignment and interval graphs", IEEE Trans. Circuits Syst. 26(9), 675–684.

## The source's definition

Ohtsuki et al. §II (pp. 676–677). Gates `T` and nets `V`; `V(t)` is the set of
nets connected to gate `t`, `T(v)` the set of gates of net `v`, and without
loss of generality `|V(t)| ≥ 1` and `|T(v)| ≥ 2` (eqs. (3)–(4)). "For each
permutation of modules we can draw horizontal intervals corresponding to nets,
from which we obtain an interval graph corresponding to the gate sequence. The
set of vertices of the interval graph is the set of nets. The vertices are
adjacent if and only if the corresponding intervals intersect" (the intervals
are closed). "The necessary number of tracks is the chromatic number of the
corresponding interval graph." The connection graph (eqs. (5)–(6)) is
`H = (V, E)`, `E = {(x, y) | ∃ t, x, y ∈ V(t)}`. The problem (p. 677): find the
placement minimising the number of tracks, restated as "given a graph `H`, find
a supergraph by adding a set of edges, which is an interval graph and has the
least clique number". The boundary gates `t_l, t_r` are ignored "for the time
being" (§II); here they are ordinary gates, as eq. (6) treats them.

Formalised without reference to stacks, bags or pathwidth:

* `LogicArray N T` — the relation "net `v` is connected to gate `t`"
  (`v ∈ V(t)`), with `IsOhtsuki` for eqs. (3)–(4);
* `connectionGraph` — `H` of eq. (6);
* `OnInterval π v j` — position `j` lies in the closed interval of net `v`
  under the gate sequence `π` (between its leftmost and rightmost gate);
* `placementGraph π` — the interval graph of the gate sequence `π`;
* `tracksFor π` — its chromatic number (as the least `k` with a proper
  `k`-colouring), and `tracks` — the least over all gate sequences.

## What is proved

Ohtsuki's own route, through interval graphs (item 05):

* `connectionGraph_le_placementGraph`: "It is obvious that `H` is a subgraph of
  the interval graph" (p. 677);
* `placementModel`: the placement graph is an interval graph, when every net
  has a gate;
* `tracksFor_eq_cliqueNum`: for every placement, chromatic number = clique
  number ("it is well known that the chromatic number of an interval graph is
  equal to the clique number", p. 676), here proved for placement graphs by
  the left-edge argument of `GateMatrix.lean`;
* `exists_placementGraph_le`: the half of **Theorem 3** (p. 678) that the
  equality needs — from any interval supergraph `Ĥ` of `H`, the gate sequence
  sorted by `d(t)` (a point of `Ĥ`'s model common to the intervals of `V(t)`,
  eq. (10)) has its interval graph inside `Ĥ`. Ohtsuki pick `d(t)` among the
  dominant cliques of `Ĥ`; here `d(t)` is the largest left endpoint over
  `V(t)`, which lies in every interval of `V(t)` because `V(t)` is a clique.
  Minimality of the augmentation is what gives equality in Theorem 3 and is not
  needed for the track count;
* `tracks_eq_intervalThickness`: **min tracks = θ(H)**, when every net has a
  gate (weaker than eq. (4));
* `tracks_eq_pathwidth_add_one_of_forall_exists`: `tracks = pw(H) + 1`, through
  Möhring Prop. 3.5 (`intervalThickness_eq_pathwidth_add_one`).

And the identification with gate matrix layout (Wing, Huang & Wang 1985 cite
[7] for exactly this problem):

* `colorable_iff_isTrackAssignment`, `tracks_eq_gateMatrix_tracks`: a proper
  colouring of the placement graph is a track assignment of `GateMatrix.lean`,
  so `tracks` is `t(M)` for the same matrix, with no hypothesis;
* `tracks_eq_pathwidth_add_one`: `tracks = pw(H) + 1` whenever some net meets
  some gate (nets with no gate allowed).

## Edge cases

No nets: `tracks = 0` (`tracks_of_isEmpty`), and `θ = 0` too. Nets but no
connection at all: `tracks = 1` (`tracks_eq_one_of_forall_not`), while
`pw + 1 = 1` as well, but the MOSP value is `0`. Under Ohtsuki's eqs. (3)–(4)
every net has a gate, so `IsOhtsuki.tracks_eq_intervalThickness` and
`IsOhtsuki.tracks_eq_pathwidth_add_one` carry no further hypothesis (the second
needs a net).

## The boundary-gate variant (§IV), not formalised as an equality

§IV pins `t_l` and `t_r` at the two ends. Item 02 found the pinned optimum
equal to `pw(H) + 1` or one more on every instance checked, never a fixed
offset, and whether the gap reaches 2 is open (`paper1/equivalences.md` §3).
Only the trivial direction is proved: `pathwidth_add_one_le_tracksPinned`.
-/

import MOSPFormalization.Complex.GateMatrix
import MOSPFormalization.Complex.IntervalThickness
import Mathlib.Combinatorics.SimpleGraph.Coloring.Vertex

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

/-- A one-dimensional logic array (Ohtsuki et al. 1979, §II): `conn v t` means
net `v` is connected to gate `t`, i.e. `v ∈ V(t)` and `t ∈ T(v)`. -/
structure LogicArray (N T : Type*) where
  conn : N → T → Prop

variable {N T : Type*} [Fintype N] [DecidableEq N] [Fintype T] [DecidableEq T]

namespace LogicArray

variable (A : LogicArray N T) [DecidableRel A.conn]

/-! ### Definitions from the source -/

/-- Ohtsuki's standing assumptions, eqs. (3)–(4): every gate has a net
(`|V(t)| ≥ 1`) and every net has two gates (`|T(v)| ≥ 2`). -/
def IsOhtsuki : Prop :=
  (∀ t, ∃ v, A.conn v t) ∧ (∀ v, ∃ t t', t ≠ t' ∧ A.conn v t ∧ A.conn v t')

/-- The connection graph `H` (eqs. (5)–(6)): nets adjacent iff they have a
common gate. -/
def connectionGraph : SimpleGraph N where
  Adj x y := x ≠ y ∧ ∃ t, A.conn x t ∧ A.conn y t
  symm := ⟨fun _ _ ⟨hne, t, h₁, h₂⟩ => ⟨hne.symm, t, h₂, h₁⟩⟩
  loopless := ⟨fun _ ⟨hne, _⟩ => hne rfl⟩

/-- Position `j` lies in the closed interval drawn for net `v` under the gate
sequence `π`: between the position of a gate of `v` and the position of a gate
of `v` (p. 676, Fig. 2). -/
def OnInterval (π : LinearLayout T) (v : N) (j : ℕ) : Prop :=
  ∃ t t', A.conn v t ∧ A.conn v t' ∧ (π t).val ≤ j ∧ j ≤ (π t').val

/-- The interval graph of the gate sequence `π` (p. 676, Fig. 3): nets adjacent
iff their closed intervals intersect. -/
def placementGraph (π : LinearLayout T) : SimpleGraph N where
  Adj u v := u ≠ v ∧ ∃ j, A.OnInterval π u j ∧ A.OnInterval π v j
  symm := ⟨fun _ _ ⟨hne, j, h₁, h₂⟩ => ⟨hne.symm, j, h₂, h₁⟩⟩
  loopless := ⟨fun _ ⟨hne, _⟩ => hne rfl⟩

/-- The number of tracks for the gate sequence `π`: "the chromatic number of
the corresponding interval graph" (p. 676), as the least `k` for which it has
a proper `k`-colouring (tracks are colours). -/
noncomputable def tracksFor (π : LinearLayout T) : ℕ :=
  sInf {k | (A.placementGraph π).Colorable k}

/-- The **minimum number of tracks** over all gate sequences: the value of the
linear placement problem of §II–III. -/
noncomputable def tracks : ℕ :=
  sInf {k | ∃ π : LinearLayout T, (A.placementGraph π).Colorable k}

/-- The §IV variant: the boundary gates `tl`, `tr` sit at the two ends. -/
noncomputable def tracksPinned (tl tr : T) : ℕ :=
  sInf {k | ∃ π : LinearLayout T, (π tl).val = 0 ∧ (π tr).val + 1 = Fintype.card T ∧
    (A.placementGraph π).Colorable k}

/-! ### Basic facts -/

/-- `tracksFor π` is attained. -/
theorem colorable_tracksFor (π : LinearLayout T) :
    (A.placementGraph π).Colorable (A.tracksFor π) :=
  Nat.sInf_mem (s := {k | (A.placementGraph π).Colorable k})
    ⟨_, (A.placementGraph π).colorable_of_fintype⟩

theorem tracks_le_tracksFor (π : LinearLayout T) : A.tracks ≤ A.tracksFor π :=
  Nat.sInf_le ⟨π, A.colorable_tracksFor π⟩

/-- `tracks` is attained by some gate sequence. -/
theorem exists_colorable_tracks : ∃ π : LinearLayout T, (A.placementGraph π).Colorable A.tracks :=
  Nat.sInf_mem (s := {k | ∃ π : LinearLayout T, (A.placementGraph π).Colorable k})
    ⟨_, Fintype.equivFin T, (A.placementGraph _).colorable_of_fintype⟩

/-- "`H` is a subgraph of the interval graph" of every placement (p. 677): a
common gate `t` lies in both nets' intervals. -/
theorem connectionGraph_le_placementGraph (π : LinearLayout T) :
    A.connectionGraph ≤ A.placementGraph π := by
  rintro x y ⟨hne, t, hx, hy⟩
  exact ⟨hne, (π t).val, ⟨t, t, hx, hx, le_rfl, le_rfl⟩, ⟨t, t, hy, hy, le_rfl, le_rfl⟩⟩

/-! ### The same matrix as a gate matrix -/

/-- The same relation read as a net–gate matrix (Möhring 1990, p. 18). -/
def toNetGate : NetGateMatrix N T := ⟨A.conn⟩

instance : DecidableRel A.toNetGate.conn := fun v t =>
  (inferInstance : Decidable (A.conn v t))

theorem onInterval_iff_isActive (π : LinearLayout T) (v : N) (j : ℕ) :
    A.OnInterval π v j ↔ A.toNetGate.toMOSP.isActive π v j :=
  A.toNetGate.augmented_iff_isActive π v j

theorem connectionGraph_eq_netGraph : A.connectionGraph = A.toNetGate.netGraph := rfl

/-- A proper colouring of the placement graph is exactly a track assignment of
the gate matrix for the same gate order. -/
theorem colorable_iff_isTrackAssignment (π : LinearLayout T) (k : ℕ) :
    (A.placementGraph π).Colorable k ↔ ∃ h : N → Fin k, A.toNetGate.IsTrackAssignment π h := by
  constructor
  · rintro ⟨C⟩
    exact ⟨C, fun n n' hne heq hs => C.valid ⟨hne, hs⟩ heq⟩
  · rintro ⟨h, hh⟩
    exact ⟨SimpleGraph.Coloring.mk h (fun {u v} huv heq => hh u v huv.1 heq huv.2)⟩

theorem tracksFor_eq_gateMatrix_tracksFor (π : LinearLayout T) :
    A.tracksFor π = A.toNetGate.tracksFor π := by
  unfold tracksFor NetGateMatrix.tracksFor
  congr 1
  ext k
  exact A.colorable_iff_isTrackAssignment π k

/-- **One-dimensional logic = gate matrix layout** on the same matrix, with no
hypothesis. -/
theorem tracks_eq_gateMatrix_tracks : A.tracks = A.toNetGate.tracks := by
  unfold tracks NetGateMatrix.tracks
  congr 1
  ext k
  exact exists_congr fun π => A.colorable_iff_isTrackAssignment π k

/-- **Tracks = pathwidth + 1** of the connection graph, whenever some net meets
some gate, through the gate matrix row (`GateMatrix.lean`). -/
theorem tracks_eq_pathwidth_add_one (hreq : ∃ v t, A.conn v t) :
    A.tracks = pathwidth A.connectionGraph + 1 := by
  rw [A.tracks_eq_gateMatrix_tracks, A.connectionGraph_eq_netGraph]
  exact A.toNetGate.tracks_eq_pathwidth_add_one hreq

/-! ### Edge cases -/

/-- No nets, no tracks. -/
theorem tracks_of_isEmpty [IsEmpty N] : A.tracks = 0 := by
  rw [A.tracks_eq_gateMatrix_tracks]
  exact A.toNetGate.tracks_eq_zero_of_isEmpty

/-- Nets but no connection: one track, while `pw(H) + 1 = 1` as well. -/
theorem tracks_eq_one_of_forall_not [Nonempty N] (hnone : ∀ v t, ¬ A.conn v t) :
    A.tracks = 1 := by
  rw [A.tracks_eq_gateMatrix_tracks]
  exact A.toNetGate.tracks_eq_one_of_forall_not hnone

/-! ### Chromatic number = clique number for a placement -/

/-- The nets open at position `j` form a clique of the placement graph. -/
theorem activeSet_isClique (π : LinearLayout T) (j : ℕ) :
    (A.placementGraph π).IsClique (A.toNetGate.toMOSP.activeSet π j : Set N) := by
  intro u hu v hv huv
  simp only [Finset.mem_coe, MOSPInstance.mem_activeSet_iff] at hu hv
  exact ⟨huv, j, (A.onInterval_iff_isActive π u j).mpr hu,
    (A.onInterval_iff_isActive π v j).mpr hv⟩

/-- A clique of the placement graph needs as many tracks as it has nets. -/
theorem cliqueNum_le_tracksFor (π : LinearLayout T) :
    (A.placementGraph π).cliqueNum ≤ A.tracksFor π := by
  obtain ⟨s, hs⟩ := (A.placementGraph π).exists_isNClique_cliqueNum
  rw [← hs.card_eq]
  exact hs.isClique.card_le_of_colorable (A.colorable_tracksFor π)

/-- The largest column of the augmented matrix is a clique. -/
theorem maxOpenStacks_le_cliqueNum (π : LinearLayout T) :
    A.toNetGate.toMOSP.maxOpenStacks π ≤ (A.placementGraph π).cliqueNum := by
  unfold MOSPInstance.maxOpenStacks
  split_ifs with h
  · exact Nat.zero_le _
  · apply Finset.sup'_le
    intro j _
    rw [← MOSPInstance.card_activeSet]
    exact (A.activeSet_isClique π j).card_le_cliqueNum

/-- **Chromatic number = clique number** of a placement graph (p. 676), by the
left-edge colouring of `GateMatrix.lean`. -/
theorem tracksFor_eq_cliqueNum (π : LinearLayout T) (hreq : ∃ v t, A.conn v t) :
    A.tracksFor π = (A.placementGraph π).cliqueNum := by
  refine le_antisymm ?_ (A.cliqueNum_le_tracksFor π)
  rw [A.tracksFor_eq_gateMatrix_tracksFor, A.toNetGate.tracksFor_eq_maxOpenStacks π hreq]
  exact A.maxOpenStacks_le_cliqueNum π

/-! ### The placement graph is an interval graph -/

/-- The position of the rightmost gate of net `v` under `π` (`0` for a net with
no gate). The leftmost is `NetGateMatrix.first`. -/
noncomputable def last (π : LinearLayout T) (v : N) : ℕ :=
  if hv : (A.toNetGate.toMOSP.patterns v).Nonempty then
    ((A.toNetGate.toMOSP.patterns v).image (fun t => (π t).val)).max' (hv.image _)
  else 0

theorem le_last (π : LinearLayout T) {v : N} {t : T} (ht : A.conn v t) :
    (π t).val ≤ A.last π v := by
  have hmem : t ∈ A.toNetGate.toMOSP.patterns v :=
    (A.toNetGate.toMOSP.mem_patterns_iff v t).mpr ht
  have hv : (A.toNetGate.toMOSP.patterns v).Nonempty := ⟨t, hmem⟩
  unfold last
  simp only [hv, ↓reduceDIte]
  exact Finset.le_max' _ _ (Finset.mem_image_of_mem (fun t => (π t).val) hmem)

theorem exists_eq_last (π : LinearLayout T) {v : N} {t : T} (ht : A.conn v t) :
    ∃ t₀, A.conn v t₀ ∧ (π t₀).val = A.last π v := by
  have hv : (A.toNetGate.toMOSP.patterns v).Nonempty :=
    ⟨t, (A.toNetGate.toMOSP.mem_patterns_iff v t).mpr ht⟩
  have hmem := Finset.max'_mem
    ((A.toNetGate.toMOSP.patterns v).image (fun t => (π t).val)) (hv.image _)
  obtain ⟨t₀, ht₀, heq⟩ := Finset.mem_image.mp hmem
  refine ⟨t₀, (A.toNetGate.toMOSP.mem_patterns_iff v t₀).mp ht₀, ?_⟩
  unfold last
  simp only [hv, ↓reduceDIte]
  exact heq

/-- For a net with a gate, its interval is `[first, last]`. -/
theorem onInterval_iff_between (π : LinearLayout T) {v : N} (hv : ∃ t, A.conn v t) (j : ℕ) :
    A.OnInterval π v j ↔ A.toNetGate.first π v ≤ j ∧ j ≤ A.last π v := by
  obtain ⟨t, ht⟩ := hv
  constructor
  · rintro ⟨a, b, ha, hb, haj, hjb⟩
    exact ⟨(A.toNetGate.first_le π ha).trans haj, hjb.trans (A.le_last π hb)⟩
  · rintro ⟨h₁, h₂⟩
    obtain ⟨a, ha, ha'⟩ := A.toNetGate.exists_eq_first π ht
    obtain ⟨b, hb, hb'⟩ := A.exists_eq_last π ht
    exact ⟨a, b, ha, hb, ha' ▸ h₁, hb' ▸ h₂⟩

/-- The interval model of a placement: net `v` gets `[first v, last v]`. Needs
every net to have a gate (Ohtsuki's eq. (4) gives two). -/
noncomputable def placementModel (π : LinearLayout T) (hgate : ∀ v, ∃ t, A.conn v t) :
    IntervalModel ℕ (A.placementGraph π) where
  left := A.toNetGate.first π
  right := A.last π
  left_le_right v := by
    obtain ⟨t, ht⟩ := hgate v
    exact (A.toNetGate.first_le π ht).trans (A.le_last π ht)
  adj_iff u v huv := by
    show (u ≠ v ∧ ∃ j, A.OnInterval π u j ∧ A.OnInterval π v j) ↔ _
    simp only [A.onInterval_iff_between π (hgate u), A.onInterval_iff_between π (hgate v)]
    constructor
    · rintro ⟨-, j, ⟨h₁, h₂⟩, h₃, h₄⟩
      exact ⟨h₁.trans h₄, h₃.trans h₂⟩
    · rintro ⟨h₁, h₂⟩
      refine ⟨huv, max (A.toNetGate.first π u) (A.toNetGate.first π v),
        ⟨le_max_left _ _, max_le ?_ h₂⟩, le_max_right _ _, max_le h₁ ?_⟩
      · obtain ⟨t, ht⟩ := hgate u
        exact (A.toNetGate.first_le π ht).trans (A.le_last π ht)
      · obtain ⟨t, ht⟩ := hgate v
        exact (A.toNetGate.first_le π ht).trans (A.le_last π ht)

theorem isIntervalGraph_placementGraph (π : LinearLayout T) (hgate : ∀ v, ∃ t, A.conn v t) :
    IsIntervalGraph (A.placementGraph π) :=
  ⟨A.placementModel π hgate⟩

/-! ### Theorem 3: a gate sequence from an interval supergraph -/

/-- **Ohtsuki et al. Theorem 3**, the inclusion `E* ⊆ Ê` of its proof: for any
interval supergraph `Ĥ` of the connection graph, with a model in `ℕ`, some gate
sequence has its interval graph inside `Ĥ`. Each gate `t` is given the point
`d(t)`, the largest left endpoint over `V(t)`, which lies in every interval of
`V(t)` because `V(t)` is a clique of `Ĥ` (eq. (10)); gates are sorted by `d`
(eq. (11)). A net open at position `j` then has `d` of the gate at `j` inside
its interval, so two nets open at `j` intersect in `Ĥ`'s model. -/
theorem exists_placementGraph_le {Hh : SimpleGraph N} (m : IntervalModel ℕ Hh)
    (hle : A.connectionGraph ≤ Hh) :
    ∃ π : LinearLayout T, A.placementGraph π ≤ Hh := by
  classical
  let d : T → ℕ := fun t => (Finset.univ.filter (fun v => A.conn v t)).sup m.left
  have hd_ge : ∀ t v, A.conn v t → m.left v ≤ d t := fun t v hv =>
    Finset.le_sup (f := m.left) (Finset.mem_filter.mpr ⟨Finset.mem_univ _, hv⟩)
  have hd_le : ∀ t v, A.conn v t → d t ≤ m.right v := by
    intro t v hv
    obtain ⟨u, hu, hdu⟩ := Finset.exists_mem_eq_sup
      (Finset.univ.filter (fun v => A.conn v t))
      ⟨v, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hv⟩⟩ m.left
    have hu' : A.conn u t := (Finset.mem_filter.mp hu).2
    change (Finset.univ.filter (fun v => A.conn v t)).sup m.left ≤ m.right v
    rw [hdu]
    by_cases huv : u = v
    · subst huv; exact m.left_le_right u
    · exact ((m.adj_iff u v huv).mp (hle ⟨huv, t, hu', hv⟩)).1
  obtain ⟨π, hπ⟩ := exists_layout_sorted d
  have hmono : ∀ s t, (π s).val ≤ (π t).val → d s ≤ d t := fun s t h =>
    not_lt.mp (fun hlt => absurd (hπ t s hlt) (not_lt.mpr h))
  refine ⟨π, fun u v ⟨huv, j, hu, hv⟩ => ?_⟩
  obtain ⟨a, b, ha, hb, haj, hjb⟩ := hu
  obtain ⟨a', b', ha', hb', haj', hjb'⟩ := hv
  have hj : j < Fintype.card T := lt_of_le_of_lt hjb (π b).isLt
  have hπt : (π (π.symm ⟨j, hj⟩)).val = j := by simp
  apply (m.adj_iff u v huv).mpr
  have h₁ := hd_ge a u ha
  have h₂ := hmono a (π.symm ⟨j, hj⟩) (by omega)
  have h₃ := hmono (π.symm ⟨j, hj⟩) b (by omega)
  have h₄ := hd_le b u hb
  have h₁' := hd_ge a' v ha'
  have h₂' := hmono a' (π.symm ⟨j, hj⟩) (by omega)
  have h₃' := hmono (π.symm ⟨j, hj⟩) b' (by omega)
  have h₄' := hd_le b' v hb'
  omega

/-! ### The equality -/

/-- **Minimum tracks = interval thickness of the connection graph** (Ohtsuki et
al. §II–III: "find a supergraph … which is an interval graph and has the least
clique number"), whenever every net has a gate. Lower bound: every placement
graph is an interval supergraph of `H` whose chromatic number is at least its
clique number. Upper bound: Theorem 3 turns an optimal interval supergraph into
a placement whose graph lies inside it, and a placement graph's chromatic
number is its clique number. -/
theorem tracks_eq_intervalThickness (hgate : ∀ v, ∃ t, A.conn v t) :
    A.tracks = intervalThickness A.connectionGraph := by
  apply le_antisymm
  · rcases isEmpty_or_nonempty N with hN | hN
    · rw [A.tracks_of_isEmpty]
      exact Nat.zero_le _
    · obtain ⟨v, t, ht⟩ : ∃ v t, A.conn v t := by
        obtain ⟨v⟩ := hN
        obtain ⟨t, ht⟩ := hgate v
        exact ⟨v, t, ht⟩
      obtain ⟨D, -⟩ := exists_pathDecomposition_width_eq A.connectionGraph
      have hne : {k | ∃ H : SimpleGraph N, A.connectionGraph ≤ H ∧ IsIntervalGraph H ∧
          H.cliqueNum = k}.Nonempty :=
        ⟨_, bagGraph D, le_bagGraph D, isIntervalGraph_bagGraph D, rfl⟩
      obtain ⟨Hh, hle, ⟨m⟩, hk⟩ := Nat.sInf_mem hne
      obtain ⟨π, hπ⟩ := A.exists_placementGraph_le m hle
      unfold intervalThickness
      rw [← hk]
      refine (A.tracks_le_tracksFor π).trans ?_
      rw [A.tracksFor_eq_cliqueNum π ⟨v, t, ht⟩]
      obtain ⟨s, hs⟩ := (A.placementGraph π).exists_isNClique_cliqueNum
      rw [← hs.card_eq]
      exact (hs.isClique.mono hπ).card_le_cliqueNum
  · obtain ⟨π, hπ⟩ := A.exists_colorable_tracks
    have hθ : intervalThickness A.connectionGraph ≤ (A.placementGraph π).cliqueNum :=
      Nat.sInf_le ⟨A.placementGraph π, A.connectionGraph_le_placementGraph π,
        A.isIntervalGraph_placementGraph π hgate, rfl⟩
    obtain ⟨s, hs⟩ := (A.placementGraph π).exists_isNClique_cliqueNum
    refine hθ.trans ?_
    rw [← hs.card_eq]
    exact hs.isClique.card_le_of_colorable hπ

/-- `tracks = pw(H) + 1` by Ohtsuki's route: min tracks = θ(H) (above) and
θ = pw + 1 (Möhring Prop. 3.5, `IntervalThickness.lean`). -/
theorem tracks_eq_pathwidth_add_one_of_forall_exists [Nonempty N]
    (hgate : ∀ v, ∃ t, A.conn v t) :
    A.tracks = pathwidth A.connectionGraph + 1 := by
  rw [A.tracks_eq_intervalThickness hgate, intervalThickness_eq_pathwidth_add_one]

/-- Under Ohtsuki's assumptions (3)–(4): min tracks = θ(H). -/
theorem IsOhtsuki.tracks_eq_intervalThickness (h : A.IsOhtsuki) :
    A.tracks = intervalThickness A.connectionGraph :=
  A.tracks_eq_intervalThickness fun v => by
    obtain ⟨t, -, -, ht, -⟩ := h.2 v
    exact ⟨t, ht⟩

/-- Under Ohtsuki's assumptions (3)–(4), with at least one net:
min tracks = pw(H) + 1. -/
theorem IsOhtsuki.tracks_eq_pathwidth_add_one [Nonempty N] (h : A.IsOhtsuki) :
    A.tracks = pathwidth A.connectionGraph + 1 := by
  rw [h.tracks_eq_intervalThickness, intervalThickness_eq_pathwidth_add_one]

/-! ### The boundary-gate variant (§IV): the trivial direction only -/

/-- A pinned placement is a placement, so the §IV value is at least
`pw(H) + 1`, when a pinned placement exists and some net meets some gate.
The converse band `≤ pw(H) + 2` observed by item 02 is not proved. -/
theorem pathwidth_add_one_le_tracksPinned {tl tr : T} (hreq : ∃ v t, A.conn v t)
    (hex : ∃ π : LinearLayout T, (π tl).val = 0 ∧ (π tr).val + 1 = Fintype.card T) :
    pathwidth A.connectionGraph + 1 ≤ A.tracksPinned tl tr := by
  obtain ⟨π, h₁, h₂⟩ := hex
  have hne : {k | ∃ π : LinearLayout T, (π tl).val = 0 ∧ (π tr).val + 1 = Fintype.card T ∧
      (A.placementGraph π).Colorable k}.Nonempty :=
    ⟨_, π, h₁, h₂, (A.placementGraph π).colorable_of_fintype⟩
  obtain ⟨σ, -, -, hσ⟩ := Nat.sInf_mem hne
  rw [← A.tracks_eq_pathwidth_add_one hreq]
  exact Nat.sInf_le ⟨σ, hσ⟩

end LogicArray

end Complex

end MOSPFormalization
