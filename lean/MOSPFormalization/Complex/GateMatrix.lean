/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Gate matrix layout = MOSP = pathwidth + 1

Table 1 of Linhares & Yanasse (2002), row "gate matrix layout", sources [6]
Möhring (1990) and [8] Wing, Huang & Wang (1985).

## The source's definition

Möhring (1990), p. 18 (the matrix permutation problem MPP, which is the gate
matrix permutation problem GMPP of pp. 23–24 with no restriction): an `m × n`
*net–gate matrix* `M`, rows nets, columns gates. For a permutation `π` of the
gates, the *augmented matrix* `M^π` fills in every `0` between the leftmost
and the rightmost `1` of each row. "Nets of the augmented net-gate matrix may
share the same row (called track) if they have no gate in common." MPP: "Find
a permutation of the columns and an assignment of the augmented rows (nets) to
tracks such that the number of tracks is minimum"; the minimum is `t(M)`.
Wing, Huang & Wang (1985), p. 222, Problem 1, is the same problem with gate
and net assignment functions `f : G → C`, `h : N → R`, minimising `card R`.

Formalised here without reference to stacks or pathwidth:

* `NetGateMatrix N Gt` — the relation "net `n` is connected to gate `g`";
* `augmented π n j` — entry `(n, j)` of `M^π` is `1` (column `j` lies between
  the leftmost and rightmost gate of `n`);
* `ShareGate π n n'` — the augmented rows of `n` and `n'` have a gate in common;
* `IsTrackAssignment π h` — `h : N → Fin k` puts no two such nets on one track;
* `tracksFor π` — the fewest tracks for a fixed gate order, and
  `tracks = t(M)` — the fewest over all gate orders.

## What is proved

* `tracksFor_eq_maxOpenStacks` (Möhring p. 31, the left-edge algorithm): for a
  fixed gate order, the minimum number of tracks equals the maximum column sum
  of `M^π` (`columnSum_eq_openStacksAt`), which is `maxOpenStacks π` of the
  MOSP instance with the *same* matrix. The lower bound is a pigeonhole at one
  column; the upper bound is the greedy colouring of intervals by left
  endpoint (`exists_isTrackAssignment`), done as an induction on the nets in
  order of their leftmost gate.
* `tracks_eq_mospValue` (Linhares & Yanasse 2002, Prop. 2): `t(M) = Z_MOSP(M)`
  under the **identity** map `toMOSP` — nets are customers (piece types), gates
  are patterns; no transposition (item 01, `paper2/equivalences.md` §2).
* `tracks_eq_pathwidth_add_one` (Möhring Prop. 3.5; Fellows & Langston 1989
  Thm. 7): `t(M) = pw(netGraph M) + 1`, where `netGraph` is Möhring's net
  adjacency graph (p. 29: the intersection graph of the rows), shown equal to
  the MOSP graph (`netGraph_eq_mospGraph`) and closed by
  `mospValue_eq_pathwidth_add_one`.

## Edge cases

All three equalities assume some net is connected to some gate. Without that,
no two nets ever share a gate, so one track holds everything:
`tracks_eq_one_of_forall_not` (`t = 1` when there is a net, while
`Z = pw + 1 - 1 = 0`) and `tracks_eq_zero_of_isEmpty` (`t = 0` with no nets).
Nets connected to no gate are allowed and cost nothing: their augmented row is
empty and they may share any track. Möhring's own setting (every net meets at
least one gate) satisfies the hypothesis whenever there is a net.
-/

import MOSPFormalization.MOSPGraph

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

/-- A net–gate matrix (Möhring 1990, p. 18): `conn n g` means entry `(n, g)` is
`1`, i.e. net `n` is connected to gate `g`. Rows are nets, columns gates. -/
structure NetGateMatrix (N Gt : Type*) where
  conn : N → Gt → Prop

variable {N Gt : Type*} [Fintype N] [DecidableEq N] [Fintype Gt] [DecidableEq Gt]

namespace NetGateMatrix

variable (M : NetGateMatrix N Gt) [DecidableRel M.conn]

/-! ### Definitions from the source -/

/-- Entry `(n, j)` of the augmented matrix `M^π`: column position `j` lies
between the leftmost and the rightmost gate of net `n` under the gate order `π`
(Möhring p. 18). -/
def augmented (π : LinearLayout Gt) (n : N) (j : ℕ) : Prop :=
  ∃ g g', M.conn n g ∧ M.conn n g' ∧ (π g).val ≤ j ∧ j ≤ (π g').val

/-- Two nets have a gate in common in the augmented matrix `M^π`, so they may
not share a track. -/
def ShareGate (π : LinearLayout Gt) (n n' : N) : Prop :=
  ∃ j, M.augmented π n j ∧ M.augmented π n' j

/-- A track assignment with `k` tracks for the gate order `π`: nets on the same
track have no gate in common in `M^π`. -/
def IsTrackAssignment {k : ℕ} (π : LinearLayout Gt) (h : N → Fin k) : Prop :=
  ∀ n n', n ≠ n' → h n = h n' → ¬ M.ShareGate π n n'

/-- The minimum number of tracks for a fixed gate order `π`. -/
noncomputable def tracksFor (π : LinearLayout Gt) : ℕ :=
  sInf {k | ∃ h : N → Fin k, M.IsTrackAssignment π h}

/-- **Gate matrix layout cost** `t(M)` (Möhring p. 18, MPP; Wing, Huang & Wang
1985, Problem 1): the minimum number of tracks over all gate permutations and
track assignments. -/
noncomputable def tracks : ℕ :=
  sInf {k | ∃ π : LinearLayout Gt, ∃ h : N → Fin k, M.IsTrackAssignment π h}

/-- The net adjacency graph (Möhring p. 29): nets adjacent iff their rows of
`M` (not `M^π`) have a common gate. -/
def netGraph : SimpleGraph N where
  Adj n n' := n ≠ n' ∧ ∃ g, M.conn n g ∧ M.conn n' g
  symm := ⟨fun _ _ ⟨hne, g, h₁, h₂⟩ => ⟨hne.symm, g, h₂, h₁⟩⟩
  loopless := ⟨fun _ ⟨hne, _⟩ => hne rfl⟩

open Classical in
/-- The number of `1`s in column `j` of the augmented matrix `M^π`. -/
noncomputable def columnSum (π : LinearLayout Gt) (j : ℕ) : ℕ :=
  (Finset.univ.filter (fun n => M.augmented π n j)).card

/-! ### The identity map to MOSP -/

/-- The MOSP instance with the same matrix: nets are customers, gates are
patterns (Linhares & Yanasse 2002, Prop. 2). -/
def toMOSP : MOSPInstance N Gt := ⟨M.conn⟩

instance : DecidableRel M.toMOSP.requires := fun n g =>
  (inferInstance : Decidable (M.conn n g))

theorem netGraph_eq_mospGraph : M.netGraph = M.toMOSP.mospGraph := by
  ext n n'
  rfl

theorem augmented_iff_isActive (π : LinearLayout Gt) (n : N) (j : ℕ) :
    M.augmented π n j ↔ M.toMOSP.isActive π n j := by
  rw [MOSPInstance.isActive_iff]
  constructor
  · rintro ⟨g, g', hg, hg', h₁, h₂⟩
    exact ⟨⟨g, hg, h₁⟩, ⟨g', hg', h₂⟩⟩
  · rintro ⟨⟨g, hg, h₁⟩, ⟨g', hg', h₂⟩⟩
    exact ⟨g, g', hg, hg', h₁, h₂⟩

/-- The column sums of `M^π` are the open-stack counts of the MOSP instance. -/
theorem columnSum_eq_openStacksAt (π : LinearLayout Gt) (j : ℕ) :
    M.columnSum π j = M.toMOSP.openStacksAt π j := by
  unfold columnSum MOSPInstance.openStacksAt
  congr 1
  ext n
  simp [M.augmented_iff_isActive]

theorem shareGate_comm (π : LinearLayout Gt) {n n' : N} :
    M.ShareGate π n n' → M.ShareGate π n' n := by
  rintro ⟨j, h₁, h₂⟩
  exact ⟨j, h₂, h₁⟩

/-! ### Lower bound: a pigeonhole at one column -/

/-- Nets open at the same column need distinct tracks. -/
theorem openStacksAt_le_of_isTrackAssignment (π : LinearLayout Gt) {k : ℕ}
    (h : N → Fin k) (hh : M.IsTrackAssignment π h) (j : ℕ) :
    M.toMOSP.openStacksAt π j ≤ k := by
  rw [← M.toMOSP.card_activeSet]
  calc (M.toMOSP.activeSet π j).card ≤ (Finset.univ : Finset (Fin k)).card := by
        apply Finset.card_le_card_of_injOn h (fun _ _ => Finset.mem_coe.mpr (Finset.mem_univ _))
        intro n hn n' hn' heq
        by_contra hne
        rw [Finset.mem_coe, MOSPInstance.mem_activeSet_iff] at hn hn'
        exact hh n n' hne heq ⟨j, (M.augmented_iff_isActive π n j).mpr hn,
          (M.augmented_iff_isActive π n' j).mpr hn'⟩
    _ = k := by simp

theorem maxOpenStacks_le_of_isTrackAssignment (π : LinearLayout Gt) {k : ℕ}
    (h : N → Fin k) (hh : M.IsTrackAssignment π h) :
    M.toMOSP.maxOpenStacks π ≤ k := by
  unfold MOSPInstance.maxOpenStacks
  by_cases hn : Fintype.card Gt = 0
  · simp [hn]
  · simp only [dite_eq_right hn]
    exact Finset.sup'_le _ _ (fun j _ => M.openStacksAt_le_of_isTrackAssignment π h hh j.val)

/-! ### Upper bound: the left-edge algorithm -/

/-- The position of the leftmost gate of net `n` under `π` (`0` for a net with
no gate, which conflicts with nothing). -/
noncomputable def first (π : LinearLayout Gt) (n : N) : ℕ :=
  if hn : (M.toMOSP.patterns n).Nonempty then
    ((M.toMOSP.patterns n).image (fun g => (π g).val)).min' (hn.image _)
  else 0

theorem first_le (π : LinearLayout Gt) {n : N} {g : Gt} (hg : M.conn n g) :
    M.first π n ≤ (π g).val := by
  have hmem : g ∈ M.toMOSP.patterns n := (M.toMOSP.mem_patterns_iff n g).mpr hg
  have hn : (M.toMOSP.patterns n).Nonempty := ⟨g, hmem⟩
  unfold first
  simp only [hn, ↓reduceDIte]
  exact Finset.min'_le _ _ (Finset.mem_image_of_mem _ hmem)

theorem exists_eq_first (π : LinearLayout Gt) {n : N} {g : Gt} (hg : M.conn n g) :
    ∃ g₀, M.conn n g₀ ∧ (π g₀).val = M.first π n := by
  have hn : (M.toMOSP.patterns n).Nonempty := ⟨g, (M.toMOSP.mem_patterns_iff n g).mpr hg⟩
  have hmem := Finset.min'_mem ((M.toMOSP.patterns n).image (fun g => (π g).val)) (hn.image _)
  obtain ⟨g₀, hg₀, heq⟩ := Finset.mem_image.mp hmem
  refine ⟨g₀, (M.toMOSP.mem_patterns_iff n g₀).mp hg₀, ?_⟩
  unfold first
  simp only [hn, ↓reduceDIte]
  exact heq

/-- The heart of the left-edge argument: if `x` conflicts with `a` and starts no
later than `a`, then `x` and `a` are both open at `a`'s leftmost gate. -/
theorem isActive_first_of_shareGate (π : LinearLayout Gt) {x a : N}
    (hxa : M.ShareGate π x a) (hle : M.first π x ≤ M.first π a) :
    M.toMOSP.isActive π x (M.first π a) ∧ M.toMOSP.isActive π a (M.first π a) := by
  obtain ⟨j, ⟨g₁, g₂, hg₁, hg₂, _, hj₂⟩, ⟨g₃, g₄, hg₃, hg₄, hj₃, _⟩⟩ := hxa
  obtain ⟨g₀, hg₀, h₀⟩ := M.exists_eq_first π hg₃
  obtain ⟨g₅, hg₅, h₅⟩ := M.exists_eq_first π hg₁
  have h₃ := M.first_le π hg₃
  constructor
  · rw [← M.augmented_iff_isActive]
    exact ⟨g₅, g₂, hg₅, hg₂, by omega, by omega⟩
  · rw [← M.augmented_iff_isActive]
    exact ⟨g₀, g₀, hg₀, hg₀, by omega, by omega⟩

/-- **Left-edge algorithm** (Möhring p. 31): `maxOpenStacks π` tracks suffice
for the gate order `π`, when some net meets some gate. Nets are coloured in
order of their leftmost gate; a net's earlier conflicts are all open at its
leftmost gate, together with it, so fewer than `maxOpenStacks π` colours are
blocked. -/
theorem exists_isTrackAssignment (π : LinearLayout Gt) (hreq : ∃ n g, M.conn n g) :
    ∃ h : N → Fin (M.toMOSP.maxOpenStacks π), M.IsTrackAssignment π h := by
  classical
  set w := M.toMOSP.maxOpenStacks π with hw_def
  have hw : 1 ≤ w := M.toMOSP.one_le_maxOpenStacks π hreq
  suffices H : ∀ S : Finset N, ∃ h : N → Fin w,
      ∀ x ∈ S, ∀ y ∈ S, x ≠ y → h x = h y → ¬ M.ShareGate π x y by
    obtain ⟨h, hh⟩ := H Finset.univ
    exact ⟨h, fun x y hne heq => hh x (Finset.mem_univ _) y (Finset.mem_univ _) hne heq⟩
  intro S
  induction S using Finset.induction_on_max_value (M.first π) with
  | empty => exact ⟨fun _ => ⟨0, hw⟩, by simp⟩
  | insert a s ha hmax ih =>
    obtain ⟨h, hh⟩ := ih
    set B := s.filter (fun x => M.ShareGate π x a) with hB
    have hBw : B.card < w := by
      rcases Nat.eq_zero_or_pos B.card with h0 | hpos
      · omega
      obtain ⟨x, hx⟩ := Finset.card_pos.mp hpos
      obtain ⟨hxs, hxa⟩ := Finset.mem_filter.mp hx
      have hacti := (M.isActive_first_of_shareGate π hxa (hmax x hxs)).2
      have hsub : insert a B ⊆ M.toMOSP.activeSet π (M.first π a) := by
        intro y hy
        rw [MOSPInstance.mem_activeSet_iff]
        rcases Finset.mem_insert.mp hy with rfl | hy
        · exact hacti
        · obtain ⟨hys, hya⟩ := Finset.mem_filter.mp hy
          exact (M.isActive_first_of_shareGate π hya (hmax y hys)).1
      have haB : a ∉ B := fun haB => ha (Finset.mem_filter.mp haB).1
      have hcard := Finset.card_le_card hsub
      rw [Finset.card_insert_of_notMem haB, M.toMOSP.card_activeSet] at hcard
      have := M.toMOSP.openStacksAt_le_maxOpenStacks π
        (M.toMOSP.lt_card_of_isActive π hacti)
      omega
    have hlt : (B.image h).card < (Finset.univ : Finset (Fin w)).card := by
      rw [Finset.card_univ, Fintype.card_fin]
      exact lt_of_le_of_lt Finset.card_image_le hBw
    obtain ⟨c, -, hc⟩ := Finset.exists_mem_notMem_of_card_lt_card hlt
    refine ⟨Function.update h a c, ?_⟩
    -- a net of `s` conflicting with `a` does not have colour `c`
    have hfree : ∀ y ∈ s, M.ShareGate π y a → h y ≠ c := by
      intro y hys hya hyc
      exact hc (Finset.mem_image.mpr ⟨y, Finset.mem_filter.mpr ⟨hys, hya⟩, hyc⟩)
    intro x hx y hy hne heq
    have hxa : x = a ∨ x ∈ s := Finset.mem_insert.mp hx
    have hya : y = a ∨ y ∈ s := Finset.mem_insert.mp hy
    rcases hxa with rfl | hxs <;> rcases hya with rfl | hys
    · exact absurd rfl hne
    · have hy_ne : y ≠ x := fun e => ha (e ▸ hys)
      rw [Function.update_self, Function.update_of_ne hy_ne] at heq
      exact fun hs => hfree y hys (M.shareGate_comm π hs) heq.symm
    · have hx_ne : x ≠ y := fun e => ha (e ▸ hxs)
      rw [Function.update_self, Function.update_of_ne hx_ne] at heq
      exact fun hs => hfree x hxs hs heq
    · have hx_ne : x ≠ a := fun e => ha (e ▸ hxs)
      have hy_ne : y ≠ a := fun e => ha (e ▸ hys)
      rw [Function.update_of_ne hx_ne, Function.update_of_ne hy_ne] at heq
      exact hh x hxs y hys hne heq

/-! ### The equalities -/

/-- **Left-edge theorem** (Möhring p. 31): for a fixed gate order, the minimum
number of tracks is the maximum column sum of the augmented matrix, i.e. the
maximum number of open stacks of the same matrix read as a MOSP instance. -/
theorem tracksFor_eq_maxOpenStacks (π : LinearLayout Gt) (hreq : ∃ n g, M.conn n g) :
    M.tracksFor π = M.toMOSP.maxOpenStacks π := by
  obtain ⟨h, hh⟩ := M.exists_isTrackAssignment π hreq
  have hmem : M.toMOSP.maxOpenStacks π ∈ {k | ∃ h : N → Fin k, M.IsTrackAssignment π h} :=
    ⟨h, hh⟩
  unfold tracksFor
  apply le_antisymm (Nat.sInf_le hmem)
  apply le_csInf ⟨_, hmem⟩
  rintro k ⟨h', hh'⟩
  exact M.maxOpenStacks_le_of_isTrackAssignment π h' hh'

/-- **Gate matrix layout = MOSP** (Linhares & Yanasse 2002, Prop. 2), under the
identity map on the matrix: `t(M) = Z_MOSP(M)`. -/
theorem tracks_eq_mospValue (hreq : ∃ n g, M.conn n g) :
    M.tracks = M.toMOSP.mospValue := by
  obtain ⟨σ, hσ⟩ := M.toMOSP.exists_maxOpenStacks_eq_mospValue
  obtain ⟨h, hh⟩ := M.exists_isTrackAssignment σ hreq
  have hmem : M.toMOSP.maxOpenStacks σ ∈
      {k | ∃ π : LinearLayout Gt, ∃ h : N → Fin k, M.IsTrackAssignment π h} := ⟨σ, h, hh⟩
  unfold tracks
  apply le_antisymm
  · rw [← hσ]
    exact Nat.sInf_le hmem
  · apply le_csInf ⟨_, hmem⟩
    rintro k ⟨π, h', hh'⟩
    exact (M.toMOSP.mospValue_le_maxOpenStacks π).trans
      (M.maxOpenStacks_le_of_isTrackAssignment π h' hh')

/-- **Gate matrix layout = pathwidth + 1** (Möhring 1990, Prop. 3.5; Fellows &
Langston 1989, Thm. 7): `t(M) = pw(netGraph M) + 1`, whenever some net meets
some gate. -/
theorem tracks_eq_pathwidth_add_one (hreq : ∃ n g, M.conn n g) :
    M.tracks = pathwidth M.netGraph + 1 := by
  rw [M.tracks_eq_mospValue hreq, M.netGraph_eq_mospGraph]
  exact M.toMOSP.mospValue_eq_pathwidth_add_one hreq

/-! ### Degenerate cases -/

/-- With no connection at all and at least one net, one track is needed and
suffices, while `Z_MOSP = 0`: the hypothesis above is necessary. -/
theorem tracks_eq_one_of_forall_not [Nonempty N] (hnone : ∀ n g, ¬ M.conn n g) :
    M.tracks = 1 := by
  have hmem : 1 ∈ {k | ∃ π : LinearLayout Gt, ∃ h : N → Fin k, M.IsTrackAssignment π h} :=
    ⟨Fintype.equivFin Gt, fun _ => 0, fun n _ _ _ ⟨_, ⟨g, _, hg, _⟩, _⟩ => hnone n g hg⟩
  apply le_antisymm (Nat.sInf_le hmem)
  apply le_csInf ⟨1, hmem⟩
  rintro k ⟨_, h, _⟩
  obtain ⟨n⟩ := ‹Nonempty N›
  exact Nat.one_le_iff_ne_zero.mpr (fun hk => by subst hk; exact (h n).elim0)

/-- With no nets, no tracks. -/
theorem tracks_eq_zero_of_isEmpty [IsEmpty N] : M.tracks = 0 :=
  Nat.eq_zero_of_le_zero (Nat.sInf_le ⟨Fintype.equivFin Gt, isEmptyElim, fun n => isEmptyElim n⟩)

end NetGateMatrix

end Complex

end MOSPFormalization
