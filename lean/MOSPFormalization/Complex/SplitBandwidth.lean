/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Split bandwidth: `pw ≤ sb ≤ pw + 1`

Table 1 of Linhares & Yanasse (2002), row "split bandwidth", source [12]
Fomin (1998), *Helicopter search problems, bandwidth and pathwidth*, Discrete
Applied Mathematics 85, 59–70.

## The source's definition

Fomin §3.2 (preprint p. 7): "Let v be a vertex of Γ and let M, N be a
partition of the neighbourhood of v (either may be empty). Node splitting of
v: delete vertex v with all incident edges, add new vertices u and w with edge
(u, w), and make u adjacent to all vertices of M and w to all vertices of N.
A graph Γ* is said to be a split of Γ if Γ* can be obtained from Γ by a
sequence of node splittings. The split bandwidth of graph Γ, denoted by
sb(Γ), is min{b(Γ*) : Γ* is a split of Γ}."

Formalised as that, and nothing else:

* `IsNodeSplitting G H` — `H` (on `W`) is obtained from `G` (on `V`) by one
  node splitting: a vertex `v`, two distinct new vertices `u, w` joined by an
  edge, and a bijection `f` from the other vertices of `G` onto the other
  vertices of `H` preserving adjacency; each neighbour of `v` becomes adjacent
  to exactly one of `u` (its class `M`) and `w` (its class `N`), and nothing
  else becomes adjacent to them. Vertices are named up to the bijection, so the
  relation is between graphs, not between labelled vertex sets.
* `IsSplit G H` — `H` is obtained from a copy of `G` by a finite sequence of
  node splittings (the empty sequence included: every graph is a split of
  itself, up to isomorphism).
* `splitBandwidth G` — the least `bandwidth H` over all splits `H` of `G`
  with finitely many vertices, `bandwidth` being `Sandwich.lean`'s.

Nothing in these definitions mentions paths, decompositions or separation.

## What is proved

* `pathwidth_le_splitBandwidth` — the lower half of **Theorem 8** (p. 11):
  `pw(G) ≤ sb(G)`, for every finite graph. Fomin's argument: `G` is a minor
  of each of its splits, pathwidth is minor-monotone, and `pw ≤ b`. Only the
  special case splits need is proved (`pathwidth_le_of_isNodeSplitting`):
  merging `u` and `w` back into `v` in every bag of a path decomposition of
  the split gives a path decomposition of `G` of no larger width, because the
  bags holding `u` and those holding `w` are two intervals that meet (at the
  bag holding the edge `uw`). General minor-monotonicity is not needed and not
  formalised. The step `pw ≤ b` is `pathwidth_le_bandwidth` (`Sandwich.lean`).
* `splitBandwidth_le_pathwidth_add_one` — the upper half, `sb(G) ≤ pw(G) + 1`,
  for every finite graph. Fomin goes through interval bandwidth (`sb = ib`,
  Thm 6) and a path decomposition with bags of equal size. Here the split is
  built directly from an in-sequence `σ` of narrowness `ν(σ)` (item 04,
  `Narrowness.lean`): vertex `v` is replaced by a path of copies `(v, i)`, one
  for each step `i` at which `v` is in Kornai & Tuza's shack
  (`shackAfterPut σ i`, the interval `σ v ≤ i ≤ max_{u ∈ N[v]} σ u`), and the
  edge `uv` is attached to the copies at step `max(σ u, σ v)`. Ordering the
  copies by `(i, σ v)` lexicographically, every edge stretches over copies
  whose vertices lie in one shack, so the bandwidth is at most `ν(σ)`
  (`bandwidth_stage_le`, through `bandwidth_le_of_key`); with `ν = pw + 1` (Kornai & Tuza Prop. 3.1,
  item 04) this is the bound. That the construction *is* a split, i.e. is
  reached by node splittings one at a time, is proved by adding the copies in
  the same lexicographic order (`isSplit_stage`): each new copy `(v, i)` is a
  node splitting of `(v, i − 1)`, which hands the attachments at step `≥ i` to
  the new copy.
* `pathwidth_le_splitBandwidth_le_pathwidth_add_one` — **Theorem 8**:
  `pw(G) ≤ sb(G) ≤ pw(G) + 1`.

Both ends are attained (the checker, item 02): `sb(K₂) = 1 = pw(K₂)` and
`sb(K_{1,3}) = 2 = pw(K_{1,3}) + 1`. That is why this is a **sandwich**, not an
equality; which of the two values a graph takes is left open by Fomin's
concluding remarks. Neither value is proved in Lean: the second needs a lower
bound over every split of `K_{1,3}`.

## Edge cases

Fomin considers "only connected graphs with at least two vertices" (p. 1);
both inequalities are proved here for every finite graph, connected or not,
including the empty graph (where `pw = sb = 0`).
-/

import MOSPFormalization.Sandwich
import MOSPFormalization.Complex.Narrowness

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

universe u

open Function

/-! ### Node splitting (Fomin §3.2) -/

section Defs

variable {V W : Type u}

/-- `H` is obtained from `G` by one **node splitting** (Fomin §3.2): the vertex
`v` of `G` is deleted and replaced by two new vertices `u ≠ w` with the edge
`uw`; the remaining vertices of `G` correspond to those of `H` other than
`u, w` through the bijection `f`, which preserves adjacency; and the
neighbourhood of `v` is partitioned into `M = {x : f x ~ u}` and
`N = {x : f x ~ w}`. -/
def IsNodeSplitting (G : SimpleGraph V) (H : SimpleGraph W) : Prop :=
  ∃ (v : V) (u w : W) (f : {x // x ≠ v} → W),
    u ≠ w ∧ Injective f ∧ (∀ x, f x ≠ u ∧ f x ≠ w) ∧
    (∀ y, y ≠ u → y ≠ w → ∃ x, f x = y) ∧
    H.Adj u w ∧
    (∀ x y : {x // x ≠ v}, G.Adj x.val y.val ↔ H.Adj (f x) (f y)) ∧
    (∀ x : {x // x ≠ v}, G.Adj x.val v ↔ (H.Adj (f x) u ∨ H.Adj (f x) w)) ∧
    (∀ x, ¬ (H.Adj (f x) u ∧ H.Adj (f x) w))

/-- `H` is a **split** of `G` (Fomin §3.2): it is obtained from (a copy of) `G`
by a finite sequence of node splittings. -/
inductive IsSplit (G : SimpleGraph V) : {W : Type u} → SimpleGraph W → Prop
  | iso {W : Type u} {H : SimpleGraph W} : Nonempty (G ≃g H) → IsSplit G H
  | step {W₁ W₂ : Type u} {H : SimpleGraph W₁} {K : SimpleGraph W₂} :
      IsSplit G H → IsNodeSplitting H K → IsSplit G K

/-- The **split bandwidth** `sb(G)` (Fomin §3.2): the least bandwidth of a
split of `G` (with finitely many vertices, so that the bandwidth is defined). -/
noncomputable def splitBandwidth (G : SimpleGraph V) : ℕ :=
  sInf {b | ∃ (W : Type u) (_ : Fintype W) (_ : DecidableEq W) (H : SimpleGraph W)
    (_ : DecidableRel H.Adj), IsSplit G H ∧ bandwidth H = b}

/-- A node splitting has one vertex more: the old vertex type is finite when
the new one is. -/
theorem IsNodeSplitting.finite {G : SimpleGraph V} {H : SimpleGraph W}
    (h : IsNodeSplitting G H) [Finite W] : Finite V := by
  classical
  obtain ⟨v, u, w, f, -, hinj, -⟩ := h
  refine Finite.of_injective (fun x : V => if hx : x = v then (none : Option W)
    else some (f ⟨x, hx⟩)) ?_
  intro x y hxy
  by_cases hx : x = v <;> by_cases hy : y = v
  · rw [hx, hy]
  · simp [hx, hy] at hxy
  · simp [hx, hy] at hxy
  · simp only [hx, hy, dite_false, Option.some.injEq] at hxy
    exact congrArg Subtype.val (hinj hxy)

/-- A node splitting followed by an isomorphism is a node splitting. -/
theorem IsNodeSplitting.trans_iso {W' : Type u} {G : SimpleGraph V}
    {H : SimpleGraph W} {K : SimpleGraph W'}
    (h : IsNodeSplitting G H) (e : H ≃g K) : IsNodeSplitting G K := by
  obtain ⟨v, u, w, f, huw, hinj, hne, hsurj, hadj, hG, hv, hex⟩ := h
  refine ⟨v, e u, e w, fun x => e (f x), ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact fun h => huw (e.injective h)
  · exact e.injective.comp hinj
  · exact fun x => ⟨fun h => (hne x).1 (e.injective h),
      fun h => (hne x).2 (e.injective h)⟩
  · intro y hyu hyw
    obtain ⟨x, hx⟩ := hsurj (e.symm y) (fun h => hyu (by rw [← h]; simp))
      (fun h => hyw (by rw [← h]; simp))
    exact ⟨x, by simp only [hx]; exact e.apply_symm_apply y⟩
  · exact e.map_rel_iff.mpr hadj
  · intro x y; rw [hG]; exact e.map_rel_iff.symm
  · intro x; rw [hv, e.map_rel_iff, e.map_rel_iff]
  · intro x; rw [e.map_rel_iff, e.map_rel_iff]; exact hex x

/-- Splits are closed under isomorphism. -/
theorem IsSplit.trans_iso {W' : Type u} {G : SimpleGraph V}
    {H : SimpleGraph W} {K : SimpleGraph W'}
    (h : IsSplit G H) (e : H ≃g K) : IsSplit G K := by
  cases h with
  | iso h => exact IsSplit.iso ⟨h.some.trans e⟩
  | step h₁ h₂ => exact IsSplit.step h₁ (h₂.trans_iso e)

end Defs

/-! ### The lower bound: a split does not have smaller pathwidth -/

section Lower

variable {V W : Type u} [Fintype V] [DecidableEq V] [Fintype W] [DecidableEq W]

/-- An optimal path decomposition exists. -/
theorem exists_pathDecomposition_width_eq (H : SimpleGraph W) :
    ∃ P : PathDecomposition H, P.width = pathwidth H := by
  obtain ⟨P, hP⟩ := Nat.sInf_mem (s := Set.range fun P : PathDecomposition H => P.width)
    ⟨_, PathDecomposition.trivial H, rfl⟩
  exact ⟨P, hP⟩

/-- Mapping every bag of a path decomposition of `H` through `q : W → V` gives a
path decomposition of `G` of no larger width, provided `q` is onto, every edge of
`G` lifts to an edge of `H`, and the images keep the interval property. -/
theorem pathwidth_le_of_map (G : SimpleGraph V) (H : SimpleGraph W) (q : W → V)
    (hsurj : Surjective q)
    (hedge : ∀ a b, G.Adj a b → ∃ y z, q y = a ∧ q z = b ∧ H.Adj y z)
    (hint : ∀ P : PathDecomposition H, ∀ (x : V) (i j k : Fin (P.length + 1)),
      i ≤ j → j ≤ k → (∃ y ∈ P.bag i, q y = x) → (∃ y ∈ P.bag k, q y = x) →
      ∃ y ∈ P.bag j, q y = x) :
    pathwidth G ≤ pathwidth H := by
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq H
  let Q : PathDecomposition G :=
    { length := P.length
      bag := fun i => (P.bag i).image q
      vertex_coverage := by
        intro x
        obtain ⟨y, rfl⟩ := hsurj x
        obtain ⟨i, hi⟩ := P.vertex_coverage y
        exact ⟨i, Finset.mem_image_of_mem q hi⟩
      edge_coverage := by
        intro a b hab
        obtain ⟨y, z, rfl, rfl, hyz⟩ := hedge a b hab
        obtain ⟨i, hy, hz⟩ := P.edge_coverage y z hyz
        exact ⟨i, Finset.mem_image_of_mem q hy, Finset.mem_image_of_mem q hz⟩
      interval := by
        intro x i j k hij hjk hi hk
        simp only [Finset.mem_image] at hi hk ⊢
        exact hint P x i j k hij hjk hi hk }
  have hw : Q.width ≤ P.width := by
    unfold PathDecomposition.width
    have : Finset.univ.sup' (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
        (fun i => (Q.bag i).card) ≤ Finset.univ.sup'
        (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.zero_lt_succ _⟩⟩)
        (fun i => (P.bag i).card) :=
      Finset.sup'_le _ _ fun i _ => (Finset.card_image_le).trans
        (Finset.le_sup' (fun i => (P.bag i).card) (Finset.mem_univ i))
    exact Nat.sub_le_sub_right this 1
  calc pathwidth G ≤ Q.width := pathwidth_le_width G Q
    _ ≤ P.width := hw
    _ = pathwidth H := hP

/-- Isomorphic graphs: `pw(G) ≤ pw(H)`. -/
theorem pathwidth_le_of_iso (G : SimpleGraph V) (H : SimpleGraph W) (e : G ≃g H) :
    pathwidth G ≤ pathwidth H := by
  refine pathwidth_le_of_map G H e.symm e.symm.surjective ?_ ?_
  · intro a b hab
    exact ⟨e a, e b, by simp, by simp, e.map_rel_iff.mpr hab⟩
  · intro P x i j k hij hjk ⟨y, hy, hyx⟩ ⟨z, hz, hzx⟩
    have hyz : y = z := e.symm.injective (hyx.trans hzx.symm)
    subst hyz
    exact ⟨y, P.interval y i j k hij hjk hy hz, hyx⟩

/-- **One node splitting does not decrease pathwidth**: merge `u` and `w` back
into `v` in every bag. This is the special case of minor-monotonicity that
Fomin's lower bound uses (the split contracts back to `G` along `uw`). -/
theorem pathwidth_le_of_isNodeSplitting (G : SimpleGraph V) (H : SimpleGraph W)
    (h : IsNodeSplitting G H) : pathwidth G ≤ pathwidth H := by
  obtain ⟨v, u, w, f, huw, hinj, hne, hsurj, hadj, hG, hv, -⟩ := h
  let q : W → V := fun y => if hy : ∃ x, f x = y then (Classical.choose hy).val else v
  have hqf : ∀ x, q (f x) = x.val := by
    intro x
    have hy : ∃ x', f x' = f x := ⟨x, rfl⟩
    simp only [q, hy, dite_true]
    exact congrArg Subtype.val (hinj (Classical.choose_spec hy))
  have hqu : q u = v := by
    have : ¬ ∃ x, f x = u := fun ⟨x, hx⟩ => (hne x).1 hx
    simp only [q, this, dite_false]
  have hqw : q w = v := by
    have : ¬ ∃ x, f x = w := fun ⟨x, hx⟩ => (hne x).2 hx
    simp only [q, this, dite_false]
  -- the fibres of `q`
  have hfib : ∀ y, q y = v → y = u ∨ y = w := by
    intro y hy
    by_contra hc
    rw [not_or] at hc
    obtain ⟨x, rfl⟩ := hsurj y hc.1 hc.2
    rw [hqf] at hy
    exact x.2 hy
  have hfib' : ∀ y (x : {x // x ≠ v}), q y = x.val → y = f x := by
    intro y x hy
    by_cases hyu : y = u
    · rw [hyu, hqu] at hy; exact absurd hy.symm x.2
    by_cases hyw : y = w
    · rw [hyw, hqw] at hy; exact absurd hy.symm x.2
    obtain ⟨x', rfl⟩ := hsurj y hyu hyw
    rw [hqf] at hy
    rw [Subtype.ext hy]
  refine pathwidth_le_of_map G H q ?_ ?_ ?_
  · intro x
    by_cases hx : x = v
    · exact ⟨u, by rw [hqu, hx]⟩
    · exact ⟨f ⟨x, hx⟩, hqf _⟩
  · intro a b hab
    by_cases ha : a = v
    · subst ha
      have hb : b ≠ a := fun h => hab.ne h.symm
      rcases (hv ⟨b, hb⟩).mp hab.symm with h' | h'
      · exact ⟨u, f ⟨b, hb⟩, hqu, hqf _, h'.symm⟩
      · exact ⟨w, f ⟨b, hb⟩, hqw, hqf _, h'.symm⟩
    by_cases hb : b = v
    · subst hb
      rcases (hv ⟨a, ha⟩).mp hab with h' | h'
      · exact ⟨f ⟨a, ha⟩, u, hqf _, hqu, h'⟩
      · exact ⟨f ⟨a, ha⟩, w, hqf _, hqw, h'⟩
    · exact ⟨f ⟨a, ha⟩, f ⟨b, hb⟩, hqf _, hqf _, (hG ⟨a, ha⟩ ⟨b, hb⟩).mp hab⟩
  · intro P x i j k hij hjk ⟨y, hy, hyx⟩ ⟨z, hz, hzx⟩
    by_cases hx : x = v
    · subst hx
      -- the bags holding `u` or `w`: two intervals meeting at the edge `uw`
      obtain ⟨l, hlu, hlw⟩ := P.edge_coverage u w hadj
      have key : ∀ t, t = u ∨ t = w → ∀ m : Fin (P.length + 1), t ∈ P.bag m →
          ∀ j, ((m ≤ j ∧ j ≤ l) ∨ (l ≤ j ∧ j ≤ m)) → t ∈ P.bag j := by
        intro t ht m hm j hj
        have htl : t ∈ P.bag l := by rcases ht with rfl | rfl <;> assumption
        rcases hj with ⟨h1, h2⟩ | ⟨h1, h2⟩
        · exact P.interval t m j l h1 h2 hm htl
        · exact P.interval t l j m h1 h2 htl hm
      rcases le_total j l with hjl | hlj
      · exact ⟨y, key y (hfib y hyx) i hy j (Or.inl ⟨hij, hjl⟩), hyx⟩
      · exact ⟨z, key z (hfib z hzx) k hz j (Or.inr ⟨hlj, hjk⟩), hzx⟩
    · have hy' := hfib' y ⟨x, hx⟩ hyx
      have hz' := hfib' z ⟨x, hx⟩ hzx
      subst hy' hz'
      exact ⟨_, P.interval _ i j k hij hjk hy hz, hyx⟩

/-- A split has pathwidth at least that of the graph. -/
theorem IsSplit.pathwidth_le {G : SimpleGraph V} {W' : Type u} {H : SimpleGraph W'}
    (h : IsSplit G H) : ∀ [Fintype W'] [DecidableEq W'], pathwidth G ≤ pathwidth H := by
  induction h with
  | iso h => intros; exact pathwidth_le_of_iso G _ h.some
  | @step W₁ W₂ H₁ K _ hs ih =>
    intro _ _
    classical
    have : Finite W₁ := hs.finite
    let _ : Fintype W₁ := Fintype.ofFinite W₁
    exact ih.trans (pathwidth_le_of_isNodeSplitting H₁ K hs)

/-- Every graph is a split of itself, so the set defining `sb` is nonempty. -/
theorem isSplit_refl (G : SimpleGraph V) : IsSplit G G := IsSplit.iso ⟨SimpleGraph.Iso.refl⟩

theorem splitBandwidth_le_bandwidth (G : SimpleGraph V) [DecidableRel G.Adj] :
    splitBandwidth G ≤ bandwidth G :=
  Nat.sInf_le ⟨V, inferInstance, inferInstance, G, inferInstance, isSplit_refl G, rfl⟩

/-- **Theorem 8, lower half** (Fomin 1998): `pw(G) ≤ sb(G)`. -/
theorem pathwidth_le_splitBandwidth (G : SimpleGraph V) : pathwidth G ≤ splitBandwidth G := by
  classical
  unfold splitBandwidth
  apply le_csInf
  · exact ⟨bandwidth G, V, inferInstance, inferInstance, G, inferInstance, isSplit_refl G, rfl⟩
  rintro b ⟨W', _, _, H, _, hs, rfl⟩
  exact hs.pathwidth_le.trans (pathwidth_le_bandwidth H)

end Lower

/-! ### Bandwidth from a sorting key -/

section Key

variable {W : Type u} [Fintype W] [DecidableEq W]

/-- Sorting the vertices by an injective key gives a layout in which the stretch of
an edge `yz` is the number of vertices whose key lies in `[key y, key z)`. -/
theorem bandwidth_le_of_key (H : SimpleGraph W) [DecidableRel H.Adj] (key : W → ℕ)
    (hkey : Injective key) (b : ℕ)
    (hb : ∀ y z, H.Adj y z → key y < key z →
      (Finset.univ.filter fun x => key y ≤ key x ∧ key x < key z).card ≤ b) :
    bandwidth H ≤ b := by
  let pos : W → ℕ := fun y => (Finset.univ.filter fun x => key x < key y).card
  have hpos_lt : ∀ y, pos y < Fintype.card W := by
    intro y
    apply Finset.card_lt_card
    refine Finset.ssubset_iff_of_subset (Finset.filter_subset _ _) |>.mpr ⟨y, ?_, ?_⟩
    · exact Finset.mem_univ y
    · simp
  have hpos_split : ∀ y z, key y < key z →
      pos z = pos y + (Finset.univ.filter fun x => key y ≤ key x ∧ key x < key z).card := by
    intro y z hyz
    simp only [pos]
    rw [← Finset.card_filter_add_card_filter_not
      (s := Finset.univ.filter fun x => key x < key z) (p := fun x => key x < key y)]
    congr 2
    · ext x; simp only [Finset.mem_filter, Finset.mem_univ, true_and]; omega
    · ext x; simp only [Finset.mem_filter, Finset.mem_univ, true_and]; omega
  have hpos_mono : ∀ y z, key y < key z → pos y < pos z := by
    intro y z hyz
    rw [hpos_split y z hyz]
    have : 0 < (Finset.univ.filter fun x => key y ≤ key x ∧ key x < key z).card :=
      Finset.card_pos.mpr ⟨y, by simp [hyz]⟩
    omega
  let f : W → Fin (Fintype.card W) := fun y => ⟨pos y, hpos_lt y⟩
  have hf : Injective f := by
    intro y z hyz
    have h : pos y = pos z := congrArg Fin.val hyz
    by_contra hne
    rcases Nat.lt_or_gt_of_ne (fun h' => hne (hkey h')) with h' | h'
    · exact absurd h (hpos_mono y z h').ne
    · exact absurd h (hpos_mono z y h').ne'
  let σ : LinearLayout W :=
    Equiv.ofBijective f ((Fintype.bijective_iff_injective_and_card f).mpr ⟨hf, by simp⟩)
  refine (bandwidth_le_bandwidthOfLayout H σ).trans ?_
  unfold bandwidthOfLayout
  refine Finset.sup_le fun p hp => ?_
  have hadj : H.Adj p.1 p.2 := (Finset.mem_filter.mp hp).2
  change pos p.2 - pos p.1 ≤ b
  rcases Nat.lt_or_gt_of_ne (fun h' => hadj.ne (hkey h')) with h' | h'
  · rw [hpos_split _ _ h']
    have := hb _ _ hadj h'
    omega
  · have := hpos_mono _ _ h'
    omega

end Key

theorem key_lt_iff {n a b s t : ℕ} (hs : s < n) (ht : t < n) :
    a * n + s < b * n + t ↔ a < b ∨ (a = b ∧ s < t) := by
  constructor
  · intro h
    by_contra hc
    rw [not_or, not_and_or] at hc
    rcases Nat.lt_or_ge b a with hab | hab
    · have : (b + 1) * n ≤ a * n := Nat.mul_le_mul_right n hab
      rw [Nat.succ_mul] at this
      omega
    · have hab' : a = b := by omega
      subst hab'
      omega
  · rintro (h | ⟨rfl, h⟩)
    · have : (a + 1) * n ≤ b * n := Nat.mul_le_mul_right n h
      rw [Nat.succ_mul] at this
      omega
    · omega

theorem key_eq_iff {n a b s t : ℕ} (hs : s < n) (ht : t < n) :
    a * n + s = b * n + t ↔ a = b ∧ s = t := by
  constructor
  · intro h
    have h1 : ¬ (a < b ∨ (a = b ∧ s < t)) := fun h' => by
      have := (key_lt_iff (a := a) (b := b) hs ht).mpr h'; omega
    have h2 : ¬ (b < a ∨ (b = a ∧ t < s)) := fun h' => by
      have := (key_lt_iff (a := b) (b := a) ht hs).mpr h'; omega
    omega
  · rintro ⟨rfl, rfl⟩; rfl

/-! ### The upper bound: a split from an in-sequence

Fix an in-sequence `σ`. The copy `(v, i)` exists when `v` is in Kornai & Tuza's
shack just after step `i` (`shackAfterPut σ i`: `σ v ≤ i ≤ max_{u ∈ N[v]} σ u`).
Its key is `i · n + σ v`. At stage `c` only the first copy `(v, σ v)` of each
vertex and the copies of key `≤ c` are present; the edge `uv` is attached, at
each end, to the latest present copy not beyond step `max(σ u, σ v)`. Stage 0 is
`G`; each stage adds at most one copy, by a node splitting; the last stage has
every copy, and its bandwidth is at most `ν(σ)`. -/

section Upper

variable {V : Type u} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj] (σ : LinearLayout V)

/-- The copy `p = (v, i)` is present at stage `c`. -/
def InStage (c : ℕ) (p : V × ℕ) : Prop :=
  p.1 ∈ shackAfterPut G σ p.2 ∧
    (p.2 = (σ p.1).val ∨ p.2 * Fintype.card V + (σ p.1).val ≤ c)

/-- The copy `(v, a)` carries, at stage `c`, the attachments of `v` at step `m`:
it is the latest copy of `v` present at stage `c` not beyond `m`. -/
def Att (c : ℕ) (v : V) (a m : ℕ) : Prop :=
  a ≤ m ∧ (a = m ∨ ¬ InStage G σ c (v, a + 1))

/-- Adjacency of copies at stage `c`: consecutive copies of one vertex, or the two
attachment copies of an edge `uv` at step `max(σ u, σ v)`. -/
def AdjAt (c : ℕ) (p q : V × ℕ) : Prop :=
  (p.1 = q.1 ∧ (p.2 + 1 = q.2 ∨ q.2 + 1 = p.2)) ∨
    (G.Adj p.1 q.1 ∧ Att G σ c p.1 p.2 (max (σ p.1).val (σ q.1).val) ∧
      Att G σ c q.1 q.2 (max (σ p.1).val (σ q.1).val))

theorem AdjAt.symm {c : ℕ} {p q : V × ℕ} (h : AdjAt G σ c p q) : AdjAt G σ c q p := by
  rcases h with ⟨h1, h2⟩ | ⟨h1, h2, h3⟩
  · exact Or.inl ⟨h1.symm, h2.symm⟩
  · refine Or.inr ⟨h1.symm, ?_, ?_⟩ <;> rwa [max_comm]

theorem AdjAt.irrefl {c : ℕ} (p : V × ℕ) : ¬ AdjAt G σ c p p := by
  rintro (⟨-, h⟩ | ⟨h, -⟩)
  · omega
  · exact h.ne rfl

/-- The copies present at stage `c`. -/
def Stage (c : ℕ) := {p : V × ℕ // InStage G σ c p}

/-- The graph at stage `c`. -/
def stageGraph (c : ℕ) : SimpleGraph (Stage G σ c) where
  Adj x y := AdjAt G σ c x.val y.val
  symm := ⟨fun _ _ h => AdjAt.symm G σ h⟩
  loopless := ⟨fun x h => AdjAt.irrefl G σ x.val h⟩

theorem inStage_lt {c : ℕ} {p : V × ℕ} (h : InStage G σ c p) : p.2 < Fintype.card V := by
  obtain ⟨-, w, -, hw⟩ := (mem_shackAfterPut_iff G σ _ _).mp h.1
  have := (σ w).isLt
  omega

theorem inStage_ge {c : ℕ} {p : V × ℕ} (h : InStage G σ c p) : (σ p.1).val ≤ p.2 :=
  ((mem_shackAfterPut_iff G σ _ _).mp h.1).1

instance (c : ℕ) : Finite (Stage G σ c) :=
  Finite.of_injective (fun x : Stage G σ c =>
    (x.val.1, (⟨x.val.2, inStage_lt G σ x.prop⟩ : Fin (Fintype.card V)))) (by
    intro x y h
    simp only [Prod.mk.injEq, Fin.mk.injEq] at h
    exact Subtype.ext (Prod.ext h.1 h.2))

noncomputable instance (c : ℕ) : Fintype (Stage G σ c) := Fintype.ofFinite _

noncomputable instance (c : ℕ) : DecidableEq (Stage G σ c) := Classical.decEq _

/-- The copies of a vertex present at a stage form an interval starting at its
first copy. -/
theorem inStage_of_le {c : ℕ} {v : V} {a a' : ℕ} (h : InStage G σ c (v, a))
    (h1 : (σ v).val ≤ a') (h2 : a' ≤ a) : InStage G σ c (v, a') := by
  obtain ⟨hs, hk⟩ := h
  obtain ⟨-, w, hw, haw⟩ := (mem_shackAfterPut_iff G σ _ _).mp hs
  refine ⟨(mem_shackAfterPut_iff G σ _ _).mpr ⟨h1, w, hw, by simp only at haw ⊢; omega⟩, ?_⟩
  simp only at hk ⊢
  rcases hk with hk | hk
  · left; omega
  · right
    have := Nat.mul_le_mul_right (Fintype.card V) h2
    omega

theorem inStage_mono {c c' : ℕ} (hc : c ≤ c') {p : V × ℕ} (h : InStage G σ c p) :
    InStage G σ c' p :=
  ⟨h.1, h.2.imp id (fun h' => h'.trans hc)⟩

theorem first_inStage (c : ℕ) (v : V) : InStage G σ c (v, (σ v).val) :=
  ⟨(mem_shackAfterPut_iff G σ _ _).mpr ⟨le_rfl, v, Or.inl rfl, le_rfl⟩, Or.inl rfl⟩

/-- Stage 0 is `G`. -/
noncomputable def stageZeroIso : G ≃g stageGraph G σ 0 where
  toFun v := ⟨(v, (σ v).val), first_inStage G σ 0 v⟩
  invFun x := x.val.1
  left_inv v := rfl
  right_inv x := by
    obtain ⟨⟨v, a⟩, hs, hk⟩ := x
    have hn : 0 < Fintype.card V := Fintype.card_pos_iff.mpr ⟨v⟩
    have ha : a = (σ v).val := by
      simp only at hk
      rcases hk with hk | hk
      · exact hk
      · have : a * Fintype.card V = 0 := by omega
        rcases Nat.mul_eq_zero.mp this with h | h <;> omega
    subst ha
    rfl
  map_rel_iff' := by
    intro v w
    change AdjAt G σ 0 (v, _) (w, _) ↔ G.Adj v w
    have hatt : ∀ z : V, ∀ m, (σ z).val ≤ m → Att G σ 0 z (σ z).val m := by
      intro z m hm
      refine ⟨hm, Or.inr ?_⟩
      rintro ⟨-, hk⟩
      simp only at hk
      have : ((σ z).val + 1) * Fintype.card V =
          (σ z).val * Fintype.card V + Fintype.card V := Nat.succ_mul _ _
      have := (σ z).isLt
      omega
    constructor
    · rintro (⟨rfl, h⟩ | ⟨h, -⟩)
      · simp only at h; omega
      · exact h
    · intro h
      exact Or.inr ⟨h, hatt v _ (le_max_left _ _), hatt w _ (le_max_right _ _)⟩

theorem inStage_succ {c : ℕ} {p : V × ℕ} (h : InStage G σ (c + 1) p)
    (h' : ¬ InStage G σ c p) :
    p.2 * Fintype.card V + (σ p.1).val = c + 1 ∧ p.2 ≠ (σ p.1).val := by
  obtain ⟨hs, hk⟩ := h
  have : ¬ (p.2 = (σ p.1).val ∨ p.2 * Fintype.card V + (σ p.1).val ≤ c) :=
    fun hk' => h' ⟨hs, hk'⟩
  omega

/-- **One stage is one node splitting** (or nothing). If stage `c + 1` adds the
copy `(v, j + 1)`, it is the splitting of `(v, j)` into `(v, j)` and `(v, j + 1)`:
`M` is the path neighbour `(v, j − 1)` and the attachments at step `j`, `N` the
attachments at steps `> j`. -/
theorem isSplit_stage_succ (c : ℕ) (h : IsSplit G (stageGraph G σ c)) :
    IsSplit G (stageGraph G σ (c + 1)) := by
  by_cases hnew : ∃ p, InStage G σ (c + 1) p ∧ ¬ InStage G σ c p
  · obtain ⟨⟨v, i⟩, hin, hout⟩ := hnew
    obtain ⟨hkey, hne⟩ := inStage_succ G σ hin hout
    have hge := inStage_ge G σ hin
    simp only at hkey hne hge
    obtain ⟨j, rfl⟩ : ∃ j, i = j + 1 := ⟨i - 1, by omega⟩
    have hvlt := (σ v).isLt
    have hsucc : (j + 1) * Fintype.card V = j * Fintype.card V + Fintype.card V :=
      Nat.succ_mul _ _
    have hsucc2 : (j + 1 + 1) * Fintype.card V =
        (j + 1) * Fintype.card V + Fintype.card V := Nat.succ_mul _ _
    -- `(v, j + 1)` is the only new copy
    have honly : ∀ q, InStage G σ (c + 1) q → ¬ InStage G σ c q → q = (v, j + 1) := by
      intro q hq hq'
      obtain ⟨hk, -⟩ := inStage_succ G σ hq hq'
      have hqlt := (σ q.1).isLt
      have := (key_eq_iff hqlt hvlt).mp (hk.trans hkey.symm)
      exact Prod.ext (σ.injective (Fin.ext this.2)) this.1
    have hj_in : InStage G σ c (v, j) := by
      have h1 := inStage_of_le G σ hin (a' := j) (by omega) (by omega)
      by_contra hc
      have := honly _ h1 hc
      simp at this
    have hj1_out : ¬ InStage G σ c (v, j + 1) := hout
    have hj2_out : ¬ InStage G σ (c + 1) (v, j + 1 + 1) := by
      rintro ⟨-, hk⟩
      simp only at hk
      omega
    have hj2_out' : ¬ InStage G σ c (v, j + 1 + 1) :=
      fun h => hj2_out (inStage_mono G σ (Nat.le_succ c) h)
    have hAttEq : ∀ z a m, (z, a) ≠ (v, j) →
        (Att G σ c z a m ↔ Att G σ (c + 1) z a m) := by
      intro z a m hza
      unfold Att
      have : InStage G σ c (z, a + 1) ↔ InStage G σ (c + 1) (z, a + 1) := by
        refine ⟨inStage_mono G σ (Nat.le_succ c), fun h1 => ?_⟩
        by_contra hc
        have := honly _ h1 hc
        simp only [Prod.mk.injEq] at this
        exact hza (Prod.ext this.1 (by show a = j; omega))
      rw [this]
    have hAtt_c_vj : ∀ m, Att G σ c v j m ↔ j ≤ m :=
      fun m => ⟨fun h => h.1, fun h => ⟨h, Or.inr hj1_out⟩⟩
    have hAtt_c1_vj : ∀ m, Att G σ (c + 1) v j m ↔ j = m :=
      fun m => ⟨fun h => h.2.resolve_right (not_not.mpr hin), fun h => ⟨h.le, Or.inl h⟩⟩
    have hAtt_c1_vj1 : ∀ m, Att G σ (c + 1) v (j + 1) m ↔ j + 1 ≤ m :=
      fun m => ⟨fun h => h.1, fun h => ⟨h, Or.inr hj2_out⟩⟩
    -- the neighbours of the split copy
    have hnbr : ∀ z a, InStage G σ c (z, a) → (z, a) ≠ (v, j) →
        (AdjAt G σ c (z, a) (v, j) ↔
          AdjAt G σ (c + 1) (z, a) (v, j) ∨ AdjAt G σ (c + 1) (z, a) (v, j + 1)) := by
      intro z a hza hne'
      dsimp only [AdjAt]
      rw [hAttEq z a _ hne', hAtt_c_vj, hAtt_c1_vj, hAtt_c1_vj1]
      constructor
      · rintro (⟨hz, hp⟩ | ⟨hg, ha, hm⟩)
        · exact Or.inl (Or.inl ⟨hz, hp⟩)
        · rcases Nat.eq_or_lt_of_le hm with hm | hm
          · exact Or.inl (Or.inr ⟨hg, ha, hm⟩)
          · exact Or.inr (Or.inr ⟨hg, ha, hm⟩)
      · rintro ((⟨hz, hp⟩ | ⟨hg, ha, hm⟩) | (⟨hz, hp⟩ | ⟨hg, ha, hm⟩))
        · exact Or.inl ⟨hz, hp⟩
        · exact Or.inr ⟨hg, ha, hm.le⟩
        · exfalso
          rcases hp with hp | hp
          · exact hne' (Prod.ext hz (by show a = j; omega))
          · have : (z, a) = (v, j + 1 + 1) := Prod.ext hz (by show a = j + 1 + 1; omega)
            rw [this] at hza
            exact hj2_out' hza
        · exact Or.inr ⟨hg, ha, by omega⟩
    have hexcl : ∀ z a, ¬ (AdjAt G σ (c + 1) (z, a) (v, j) ∧
        AdjAt G σ (c + 1) (z, a) (v, j + 1)) := by
      rintro z a ⟨h1, h2⟩
      dsimp only [AdjAt] at h1 h2
      rw [hAtt_c1_vj] at h1
      rw [hAtt_c1_vj1] at h2
      rcases h1 with ⟨hz, hp⟩ | ⟨hg, -, hm⟩ <;> rcases h2 with ⟨hz', hp'⟩ | ⟨hg', -, hm'⟩
      · omega
      · exact hg'.ne hz
      · exact hg.ne hz'
      · omega
    let s : Stage G σ c := ⟨(v, j), hj_in⟩
    let u' : Stage G σ (c + 1) := ⟨(v, j), inStage_mono G σ (Nat.le_succ c) hj_in⟩
    let w' : Stage G σ (c + 1) := ⟨(v, j + 1), hin⟩
    let f : {x : Stage G σ c // x ≠ s} → Stage G σ (c + 1) :=
      fun x => ⟨x.val.val, inStage_mono G σ (Nat.le_succ c) x.val.prop⟩
    have hfx : ∀ x : {x : Stage G σ c // x ≠ s}, x.val.val ≠ (v, j) :=
      fun x h => x.prop (Subtype.ext h)
    have hsplit : IsNodeSplitting (stageGraph G σ c) (stageGraph G σ (c + 1)) := by
      refine ⟨s, u', w', f, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
      · intro h
        have := congrArg (fun x : Stage G σ (c + 1) => x.val.2) h
        simp [u', w'] at this
      · intro x y h
        have h' : (f x).val = (f y).val := congrArg Subtype.val h
        exact Subtype.ext (Subtype.ext h')
      · intro x
        refine ⟨fun h => hfx x (congrArg Subtype.val h), fun h => ?_⟩
        have hx := x.val.prop
        rw [show x.val.val = (v, j + 1) from congrArg Subtype.val h] at hx
        exact hj1_out hx
      · intro y hyu hyw
        have hy1 : y.val ≠ (v, j) := fun h => hyu (Subtype.ext h)
        have hy2 : y.val ≠ (v, j + 1) := fun h => hyw (Subtype.ext h)
        have hyc : InStage G σ c y.val := by
          by_contra hc
          exact hy2 (honly _ y.prop hc)
        exact ⟨⟨⟨y.val, hyc⟩, fun h => hy1 (congrArg Subtype.val h)⟩, rfl⟩
      · exact Or.inl ⟨rfl, Or.inl rfl⟩
      · intro x y
        show AdjAt G σ c x.val.val y.val.val ↔ AdjAt G σ (c + 1) x.val.val y.val.val
        dsimp only [AdjAt]
        rw [hAttEq x.val.val.1 x.val.val.2 _ (hfx x), hAttEq y.val.val.1 y.val.val.2 _ (hfx y)]
      · intro x
        exact hnbr x.val.val.1 x.val.val.2 x.val.prop (hfx x)
      · intro x
        exact hexcl x.val.val.1 x.val.val.2
    exact IsSplit.step h hsplit
  · have hsame : ∀ p, InStage G σ c p ↔ InStage G σ (c + 1) p := by
      intro p
      refine ⟨inStage_mono G σ (Nat.le_succ c), fun h' => ?_⟩
      by_contra hc
      exact hnew ⟨p, h', hc⟩
    have hAtt : ∀ z a m, Att G σ c z a m ↔ Att G σ (c + 1) z a m := by
      intro z a m
      unfold Att
      rw [hsame]
    refine h.trans_iso ⟨Equiv.subtypeEquivRight hsame, ?_⟩
    intro x y
    show AdjAt G σ (c + 1) x.val y.val ↔ AdjAt G σ c x.val y.val
    dsimp only [AdjAt]
    simp only [hAtt]

/-- Every stage is a split of `G`. -/
theorem isSplit_stage (c : ℕ) : IsSplit G (stageGraph G σ c) := by
  induction c with
  | zero => exact IsSplit.iso ⟨stageZeroIso G σ⟩
  | succ c ih => exact isSplit_stage_succ G σ c ih

/-- At the last stage an attachment copy sits exactly at the attachment step. -/
theorem att_full {z z' : V} {a : ℕ}
    (hz : InStage G σ (Fintype.card V * Fintype.card V) (z, a)) (hadj : G.Adj z z')
    (hatt : Att G σ (Fintype.card V * Fintype.card V) z a (max (σ z).val (σ z').val)) :
    a = max (σ z).val (σ z').val := by
  obtain ⟨hle, h | h⟩ := hatt
  · exact h
  by_cases hne : a = max (σ z).val (σ z').val
  · exact hne
  exfalso
  apply h
  have hza := inStage_ge G σ hz
  simp only at hza
  have hlt := (σ z').isLt
  have hzlt := (σ z).isLt
  have ham : a + 1 ≤ (σ z').val := by
    rcases Nat.eq_or_lt_of_le hle with h' | h'
    · exact absurd h' hne
    · rcases le_total (σ z).val (σ z').val with h'' | h''
      · rw [max_eq_right h''] at h'; omega
      · rw [max_eq_left h''] at h'; omega
  have hmul := Nat.mul_le_mul_right (Fintype.card V) (show a + 1 + 1 ≤ Fintype.card V by omega)
  have hsucc : (a + 1 + 1) * Fintype.card V = (a + 1) * Fintype.card V + Fintype.card V :=
    Nat.succ_mul _ _
  refine ⟨(mem_shackAfterPut_iff G σ _ _).mpr ⟨by simp only; omega, z', Or.inr hadj, ham⟩, ?_⟩
  right
  simp only
  omega

theorem card_shackAfterPut_le_inNarrowness (a : ℕ) (ha : a < Fintype.card V) :
    (shackAfterPut G σ a).card ≤ inNarrowness G σ := by
  rw [inNarrowness_eq_sup]
  exact Finset.le_sup (f := fun i : Fin (Fintype.card V) => (shackAfterPut G σ i.val).card)
    (Finset.mem_univ ⟨a, ha⟩)

/-- The bandwidth of the last stage is at most the narrowness of `σ`. -/
theorem bandwidth_stage_le [DecidableRel (stageGraph G σ (Fintype.card V * Fintype.card V)).Adj] :
    bandwidth (stageGraph G σ (Fintype.card V * Fintype.card V)) ≤ inNarrowness G σ := by
  let key : Stage G σ (Fintype.card V * Fintype.card V) → ℕ := fun x => x.val.2 * Fintype.card V + (σ x.val.1).val
  have hkey : Injective key := by
    intro x y h
    have := (key_eq_iff (σ x.val.1).isLt (σ y.val.1).isLt).mp h
    exact Subtype.ext (Prod.ext (σ.injective (Fin.ext this.2)) this.1)
  -- a set of copies all in the shack at step `a`
  have hcount : ∀ (a : ℕ) (v : V), (σ v).val ≤ a → a < Fintype.card V →
      ∀ S : Finset (Stage G σ (Fintype.card V * Fintype.card V)), (∀ z ∈ S, (z.val.2 = a ∧ (σ v).val ≤ (σ z.val.1).val) ∨
        (z.val.2 = a + 1 ∧ (σ z.val.1).val < (σ v).val)) → S.card ≤ inNarrowness G σ := by
    intro a v hva ha S hS
    calc S.card ≤ (shackAfterPut G σ a).card := by
          apply Finset.card_le_card_of_injOn (fun z => z.val.1)
          · intro z hz
            have hzs := z.prop.1
            rw [Finset.mem_coe]
            rcases hS z hz with ⟨h1, -⟩ | ⟨h1, h2⟩
            · rw [h1] at hzs; exact hzs
            · rw [h1, mem_shackAfterPut_iff] at hzs
              obtain ⟨-, w, hw, haw⟩ := hzs
              refine (mem_shackAfterPut_iff G σ _ _).mpr ⟨?_, w, hw, by omega⟩
              show (σ z.val.1).val ≤ a
              omega
          · intro z1 hz1 z2 hz2 h
            have h' : z1.val.1 = z2.val.1 := h
            have hσ : (σ z1.val.1).val = (σ z2.val.1).val := by rw [h']
            refine Subtype.ext (Prod.ext h' ?_)
            rcases hS z1 hz1 with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
              rcases hS z2 hz2 with ⟨h3, h4⟩ | ⟨h3, h4⟩ <;> omega
      _ ≤ inNarrowness G σ := card_shackAfterPut_le_inNarrowness G σ a ha
  refine bandwidth_le_of_key _ key hkey _ ?_
  intro x y hxy hlt
  have hxlt := (σ x.val.1).isLt
  have hylt := (σ y.val.1).isLt
  have hxa := inStage_lt G σ x.prop
  have hxg := inStage_ge G σ x.prop
  apply hcount x.val.2 x.val.1 hxg hxa
  intro z hz
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hz
  have hzlt := (σ z.val.1).isLt
  simp only [key] at hz hlt
  have h1 := (key_lt_iff (a := z.val.2) (b := x.val.2) hzlt hxlt).not.mp (by omega)
  have h2 := (key_lt_iff (a := z.val.2) (b := y.val.2) hzlt hylt).mp (by omega)
  have h3 := (key_lt_iff (a := x.val.2) (b := y.val.2) hxlt hylt).mp hlt
  rcases hxy with ⟨he, hp⟩ | ⟨hg, ha, hb⟩
  · have hσ : (σ x.val.1).val = (σ y.val.1).val := by rw [he]
    omega
  · have e1 : x.val.2 = max (σ x.val.1).val (σ y.val.1).val := att_full G σ x.prop hg ha
    have e2 : y.val.2 = max (σ x.val.1).val (σ y.val.1).val := by
      have := att_full G σ y.prop hg.symm (by rwa [max_comm] at hb)
      rwa [max_comm] at this
    rcases le_total (σ x.val.1).val (σ y.val.1).val with hm | hm
    · rw [max_eq_right hm] at e1 e2; omega
    · rw [max_eq_left hm] at e1 e2; omega

/-- `sb(G) ≤ ν(σ)` for every in-sequence `σ`. -/
theorem splitBandwidth_le_inNarrowness : splitBandwidth G ≤ inNarrowness G σ := by
  classical
  unfold splitBandwidth
  refine (Nat.sInf_le ?_).trans (bandwidth_stage_le G σ)
  exact ⟨Stage G σ (Fintype.card V * Fintype.card V), inferInstance,
    inferInstance, stageGraph G σ _, inferInstance, isSplit_stage G σ _, rfl⟩

/-- **Theorem 8, upper half** (Fomin 1998): `sb(G) ≤ pw(G) + 1`. -/
theorem splitBandwidth_le_pathwidth_add_one : splitBandwidth G ≤ pathwidth G + 1 := by
  obtain ⟨σ, hσ⟩ := Nat.sInf_mem (s := Set.range fun σ : LinearLayout V => inNarrowness G σ)
    ⟨_, Fintype.equivFin V, rfl⟩
  have hle := splitBandwidth_le_inNarrowness G σ
  change inNarrowness G σ = narrowness G at hσ
  rw [hσ] at hle
  rcases isEmpty_or_nonempty V with hV | hV
  · rw [narrowness_of_isEmpty] at hle; omega
  · rwa [narrowness_eq_pathwidth_add_one] at hle

/-- **Fomin (1998), Theorem 8**: `pw(G) ≤ sb(G) ≤ pw(G) + 1`, for every finite
graph (Fomin states it for connected graphs with at least two vertices). -/
theorem pathwidth_le_splitBandwidth_le_pathwidth_add_one :
    pathwidth G ≤ splitBandwidth G ∧ splitBandwidth G ≤ pathwidth G + 1 :=
  ⟨pathwidth_le_splitBandwidth G, splitBandwidth_le_pathwidth_add_one G⟩

end Upper

end Complex

end MOSPFormalization
