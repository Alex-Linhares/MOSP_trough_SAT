/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Node search is monotone: `ns = mns = vs + 1`

Loop0005 item 14, the reserve. Closes the named gap `NodeSearchMonotonicity`
of `NodeSearch.lean`: recontamination does not help in the node search game
of Kirousis & Papadimitriou (1985, [9] p. 181; 1986, [10] §2), and so
**[10] Theorem 4.1 holds for the full game**: `ns(G) = vs(G) + 1` on every
finite graph with an edge.

## The argument

Not the route of [10] (Theorem 2.3, reducing to LaPaugh's theorem for edge
search), but the *crusade* method of Bienstock & Seymour (1991, "Monotonicity
in graph searching", J. Algorithms 12, 239–245), run on **vertex sets** with
the **outer vertex boundary** `∂A = N(A) \ A` as the measure:

1. `card_outerBd_inter_add_union` — `|∂|` is submodular, because
   `|∂A| = |N[A]| − |A|`, `N[A ∪ B] = N[A] ∪ N[B]` and
   `N[A ∩ B] ⊆ N[A] ∩ N[B]`.
2. `IsChain` — a chain (crusade) of width `≤ K` is a sequence of vertex sets
   from `∅` to `V`, each step adding at most one vertex and removing any
   number, every set with `|∂| ≤ K`.
3. `exists_monotone_chain` — **the crusade lemma**: a chain of width `≤ K`
   can be made increasing. Take one of least total weight
   `Σ (|∂X_i| · (|V| + 1) + |X_i|)`; if `X_j ⊄ X_{j+1}`, replace `X_j` by
   `X_j ∩ X_{j+1}` (if that does not enlarge its boundary) or else
   `X_{j+1}` by `X_j ∪ X_{j+1}` (whose boundary is then smaller, by
   submodularity); either way the weight falls.
4. `vertexSeparation_le_of_monotone_chain` — an increasing chain is a layout
   (order by entry index) whose prefixes are the chain's sets and whose active
   suffixes are their outer boundaries, so `vs ≤ K`.
5. `exists_chain_step`, `vertexSeparation_add_one_le_of_isNodeSearch` — any
   strategy with `≤ k` searchers, recontamination allowed, yields a chain of
   width `≤ k − 1`: follow the *clean set* (vertices touching no contaminated
   edge). In a closed position its boundary is guarded
   (`outerBd_cleanSet_subset`); a vertex that becomes clean carries a searcher
   (`mem_guards_of_newly_clean`); so every set strictly between the clean set
   after a move and its intersection with the one before contains a searcher
   and misses one of the `≤ k` from its boundary; the intersection itself is
   the old clean set unless the move deleted a searcher, leaving `≤ k − 1`.

## Main results

* `nodeSearch_eq_vertexSeparation_add_one` — [10] Theorem 4.1, full game,
  every graph with an edge; `nodeSearch_eq_pathwidth_add_one`.
* `nodeSearchMonotonicity : NodeSearchMonotonicity G` — for **every** finite
  graph, edgeless included (both numbers are `0` there).
* `nodeSearch_eq_intervalThickness` — [9]'s Theorem, full game, graphs with
  an edge (it fails on edgeless graphs: `IntervalSearch.lean`);
  `nodeSearch_chain`: `θ = ns = mns = vs + 1 = pw + 1`.
* `NetGateMatrix.tracks_eq_nodeSearch` — Möhring (1990) Theorem 3.9, full
  game, when two nets share a gate.

The chain machinery (items 1–4) is reused for edge search in
`EdgeSearchFull.lean`.
-/

import MOSPFormalization.Complex.KirousisPapadimitriouGap
import MOSPFormalization.Complex.IntervalSearch

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### The outer vertex boundary and its submodularity -/

/-- The outer vertex boundary of `A`: the vertices outside `A` with a neighbour
in `A`. -/
def outerBd (A : Finset V) : Finset V :=
  univ.filter fun w => w ∉ A ∧ ∃ u ∈ A, G.Adj u w

theorem mem_outerBd {A : Finset V} {w : V} :
    w ∈ outerBd G A ↔ w ∉ A ∧ ∃ u ∈ A, G.Adj u w := by
  simp [outerBd]

/-- The closed neighbourhood of a set. -/
def closedNbhd (A : Finset V) : Finset V := A ∪ outerBd G A

theorem card_closedNbhd (A : Finset V) :
    (closedNbhd G A).card = A.card + (outerBd G A).card := by
  unfold closedNbhd
  rw [card_union_of_disjoint]
  rw [disjoint_left]
  intro w hw hw'
  exact ((mem_outerBd G).mp hw').1 hw

theorem mem_closedNbhd {A : Finset V} {w : V} :
    w ∈ closedNbhd G A ↔ w ∈ A ∨ ∃ u ∈ A, G.Adj u w := by
  unfold closedNbhd
  rw [mem_union, mem_outerBd]
  tauto

theorem closedNbhd_union (A B : Finset V) :
    closedNbhd G (A ∪ B) = closedNbhd G A ∪ closedNbhd G B := by
  ext w
  simp only [mem_closedNbhd, mem_union]
  constructor
  · rintro ((h | h) | ⟨u, hu | hu, huw⟩)
    · exact Or.inl (Or.inl h)
    · exact Or.inr (Or.inl h)
    · exact Or.inl (Or.inr ⟨u, hu, huw⟩)
    · exact Or.inr (Or.inr ⟨u, hu, huw⟩)
  · rintro ((h | ⟨u, hu, huw⟩) | (h | ⟨u, hu, huw⟩))
    · exact Or.inl (Or.inl h)
    · exact Or.inr ⟨u, Or.inl hu, huw⟩
    · exact Or.inl (Or.inr h)
    · exact Or.inr ⟨u, Or.inr hu, huw⟩

theorem closedNbhd_inter_subset (A B : Finset V) :
    closedNbhd G (A ∩ B) ⊆ closedNbhd G A ∩ closedNbhd G B := by
  intro w hw
  rw [mem_closedNbhd] at hw
  rw [mem_inter, mem_closedNbhd, mem_closedNbhd]
  rcases hw with h | ⟨u, hu, huw⟩
  · rw [mem_inter] at h
    exact ⟨Or.inl h.1, Or.inl h.2⟩
  · rw [mem_inter] at hu
    exact ⟨Or.inr ⟨u, hu.1, huw⟩, Or.inr ⟨u, hu.2, huw⟩⟩

/-- **Submodularity** of the outer vertex boundary. -/
theorem card_outerBd_inter_add_union (A B : Finset V) :
    (outerBd G (A ∩ B)).card + (outerBd G (A ∪ B)).card ≤
      (outerBd G A).card + (outerBd G B).card := by
  have h1 := card_closedNbhd G (A ∩ B)
  have h2 := card_closedNbhd G (A ∪ B)
  have h3 := card_closedNbhd G A
  have h4 := card_closedNbhd G B
  have h5 := card_union_add_card_inter A B
  have h6 := card_union_add_card_inter (closedNbhd G A) (closedNbhd G B)
  have h7 := card_le_card (closedNbhd_inter_subset G A B)
  rw [← closedNbhd_union] at h6
  omega

/-! ### Chains of vertex sets -/

/-- A chain from `A` to `B` of width `≤ K`: sets `X 0 = A, …, X n = B`, each
step adding at most one vertex (and removing any number), every set with an
outer boundary of at most `K` vertices. This is a *crusade* in the sense of
Bienstock & Seymour (1991), over vertex sets instead of edge sets. -/
structure IsChain (K : ℕ) (A B : Finset V) (n : ℕ) (X : ℕ → Finset V) : Prop where
  start : X 0 = A
  stop : X n = B
  step : ∀ i < n, (X (i + 1) \ X i).card ≤ 1
  width : ∀ i ≤ n, (outerBd G (X i)).card ≤ K

variable {G}

theorem IsChain.trans {K : ℕ} {A B C : Finset V} {n m : ℕ} {X Y : ℕ → Finset V}
    (hX : IsChain G K A B n X) (hY : IsChain G K B C m Y) :
    IsChain G K A C (n + m) (fun i => if i ≤ n then X i else Y (i - n)) where
  start := by simpa using hX.start
  stop := by
    by_cases hm : m = 0
    · subst hm
      simp only [Nat.add_zero, le_refl, ↓reduceIte]
      rw [hX.stop, ← hY.stop, hY.start]
    · simp only [show ¬ n + m ≤ n by omega, ↓reduceIte, Nat.add_sub_cancel_left]
      exact hY.stop
  step := by
    intro i hi
    by_cases h1 : i + 1 ≤ n
    · simp only [h1, show i ≤ n by omega, ↓reduceIte]
      exact hX.step i (by omega)
    · by_cases h2 : i = n
      · subst h2
        simp only [h1, le_refl, ↓reduceIte]
        have := hY.step 0 (by omega)
        rw [hY.start, ← hX.stop] at this
        simpa [Nat.add_sub_cancel_left] using this
      · simp only [h1, show ¬ i ≤ n by omega, ↓reduceIte]
        have := hY.step (i - n) (by omega)
        rwa [show i - n + 1 = i + 1 - n by omega] at this
  width := by
    intro i hi
    by_cases h : i ≤ n
    · simp only [h, ↓reduceIte]
      exact hX.width i h
    · simp only [h, ↓reduceIte]
      exact hY.width (i - n) (by omega)

/-- A chain through an interval `[A, B]` all of whose sets are narrow. -/
theorem exists_chain_of_interval {K : ℕ} {A B : Finset V} (hAB : A ⊆ B)
    (hgood : ∀ C, A ⊆ C → C ⊆ B → (outerBd G C).card ≤ K) :
    ∃ n X, IsChain G K A B n X := by
  induction h : (B \ A).card generalizing A with
  | zero =>
    have : A = B := Subset.antisymm hAB (by
      intro x hx
      by_contra hxA
      have : x ∈ B \ A := mem_sdiff.mpr ⟨hx, hxA⟩
      rw [card_eq_zero.mp h] at this
      simp at this)
    subst this
    exact ⟨0, fun _ => A, rfl, rfl, fun i hi => absurd hi (Nat.not_lt_zero _),
      fun i _ => hgood A subset_rfl subset_rfl⟩
  | succ k ih =>
    obtain ⟨b, hb⟩ : (B \ A).Nonempty := card_pos.mp (by omega)
    rw [mem_sdiff] at hb
    have hA' : insert b A ⊆ B := insert_subset hb.1 hAB
    have hcard : (B \ insert b A).card = k := by
      have : B \ A = insert b (B \ insert b A) := by
        ext x
        simp only [mem_sdiff, mem_insert]
        constructor
        · rintro ⟨hx, hxA⟩
          by_cases hxb : x = b
          · exact Or.inl hxb
          · exact Or.inr ⟨hx, by tauto⟩
        · rintro (rfl | ⟨hx, hxA⟩)
          · exact hb
          · exact ⟨hx, fun h => hxA (Or.inr h)⟩
      rw [this, card_insert_of_notMem (by simp)] at h
      omega
    obtain ⟨n, X, hX⟩ := ih hA' (fun C hC hCB => hgood C ((subset_insert _ _).trans hC) hCB)
      hcard
    have h1 : IsChain G K A (insert b A) 1 (fun i => if i = 0 then A else insert b A) :=
      { start := rfl
        stop := rfl
        step := by
          intro i hi
          obtain rfl : i = 0 := by omega
          simp only [↓reduceIte, show (0 + 1 = 0) = False by simp]
          calc (insert b A \ A).card ≤ ({b} : Finset V).card := by
                apply card_le_card
                intro x hx
                simp only [mem_sdiff, mem_insert] at hx
                simp only [mem_singleton]
                tauto
            _ = 1 := card_singleton b
        width := by
          intro i hi
          by_cases h0 : i = 0
          · simp only [h0, ↓reduceIte]
            exact hgood A subset_rfl hAB
          · simp only [h0, ↓reduceIte]
            exact hgood _ (subset_insert _ _) hA' }
    exact ⟨_, _, h1.trans hX⟩

/-! ### Uncrossing: a chain can be made increasing -/

/-- The weight used to uncross: boundary first, then size. -/
def chainWeight (G : SimpleGraph V) [DecidableRel G.Adj] (C : Finset V) : ℕ :=
  (outerBd G C).card * (Fintype.card V + 1) + C.card

theorem sum_lt_of_update {n : ℕ} {X Y : ℕ → Finset V} {j : ℕ} (hj : j ≤ n)
    (hY : ∀ i, i ≠ j → Y i = X i) (hlt : chainWeight G (Y j) < chainWeight G (X j)) :
    ∑ i ∈ range (n + 1), chainWeight G (Y i) < ∑ i ∈ range (n + 1), chainWeight G (X i) := by
  apply sum_lt_sum
  · intro i _
    by_cases hij : i = j
    · subst hij; exact hlt.le
    · rw [hY i hij]
  · exact ⟨j, mem_range.mpr (by omega), hlt⟩

/-- **Bienstock & Seymour (1991), the crusade lemma, for vertex sets.** If
there is a chain from `∅` to `univ` of width `≤ K`, there is an increasing one:
take one of least total weight; if some step `X j ⊄ X (j + 1)`, submodularity
lets `X j` be replaced by `X j ∩ X (j + 1)` or `X (j + 1)` by
`X j ∪ X (j + 1)`, lowering the weight. -/
theorem exists_monotone_chain {K n : ℕ} {X : ℕ → Finset V}
    (hX : IsChain G K ∅ univ n X) :
    ∃ Y, IsChain G K ∅ univ n Y ∧ ∀ i < n, Y i ⊆ Y (i + 1) := by
  induction h : ∑ i ∈ range (n + 1), chainWeight G (X i) using Nat.strong_induction_on
    generalizing X with
  | _ m ih =>
  by_cases hmono : ∀ i < n, X i ⊆ X (i + 1)
  · exact ⟨X, hX, hmono⟩
  push Not at hmono
  obtain ⟨j, hjn, hj⟩ := hmono
  set a := X j with ha
  set b := X (j + 1) with hb
  have hj0 : j ≠ 0 := by
    rintro rfl
    apply hj
    rw [ha, hX.start]
    exact empty_subset _
  have hsub := card_outerBd_inter_add_union G a b
  have hab : (a ∩ b).card < a.card := card_lt_card ⟨inter_subset_left, fun h' =>
    hj (fun x hx => (mem_inter.mp (h' hx)).2)⟩
  by_cases hcase : (outerBd G (a ∩ b)).card ≤ (outerBd G a).card
  · -- replace `X j` by `X j ∩ X (j + 1)`
    let Y := Function.update X j (a ∩ b)
    have hYj : Y j = a ∩ b := Function.update_self _ _ _
    have hYo : ∀ i, i ≠ j → Y i = X i := fun i hi => Function.update_of_ne hi _ _
    have hY : IsChain G K ∅ univ n Y :=
      { start := by rw [hYo 0 (Ne.symm hj0)]; exact hX.start
        stop := by rw [hYo n (by omega)]; exact hX.stop
        step := by
          intro i hi
          by_cases h1 : i + 1 = j
          · rw [h1, hYj, hYo i (by omega)]
            refine (card_le_card ?_).trans (hX.step i hi)
            rw [h1]
            exact sdiff_subset_sdiff inter_subset_left subset_rfl
          · by_cases h2 : i = j
            · subst h2
              rw [hYj, hYo (i + 1) (by omega)]
              refine (card_le_card ?_).trans (hX.step i hi)
              intro x hx
              simp only [mem_sdiff, mem_inter, not_and] at hx ⊢
              exact ⟨hx.1, fun h => hx.2 h hx.1⟩
            · rw [hYo i h2, hYo (i + 1) h1]
              exact hX.step i hi
        width := by
          intro i hi
          by_cases h2 : i = j
          · subst h2
            rw [hYj]
            exact hcase.trans (hX.width i hi)
          · rw [hYo i h2]
            exact hX.width i hi }
    have hlt : chainWeight G (Y j) < chainWeight G (X j) := by
      rw [hYj]
      unfold chainWeight
      have := Nat.mul_le_mul_right (Fintype.card V + 1) hcase
      rw [← ha]
      omega
    exact ih _ (h ▸ sum_lt_of_update (by omega) hYo hlt) hY rfl
  · -- replace `X (j + 1)` by `X j ∪ X (j + 1)`
    push Not at hcase
    have hlt' : (outerBd G (a ∪ b)).card < (outerBd G b).card := by omega
    let Y := Function.update X (j + 1) (a ∪ b)
    have hYj : Y (j + 1) = a ∪ b := Function.update_self _ _ _
    have hYo : ∀ i, i ≠ j + 1 → Y i = X i := fun i hi => Function.update_of_ne hi _ _
    have hY : IsChain G K ∅ univ n Y :=
      { start := by rw [hYo 0 (by omega)]; exact hX.start
        stop := by
          by_cases hn : n = j + 1
          · rw [hn, hYj, hb, ← hn, hX.stop]
            simp
          · rw [hYo n hn]; exact hX.stop
        step := by
          intro i hi
          by_cases h1 : i = j
          · subst h1
            rw [hYj, hYo i (by omega), ← ha]
            refine (card_le_card ?_).trans (hX.step i hi)
            intro x hx
            simp only [mem_sdiff, mem_union] at hx ⊢
            exact ⟨hx.1.resolve_left hx.2, hx.2⟩
          · by_cases h2 : i = j + 1
            · subst h2
              rw [hYj, hYo (j + 1 + 1) (by omega)]
              refine (card_le_card ?_).trans (hX.step (j + 1) hi)
              exact sdiff_subset_sdiff subset_rfl subset_union_right
            · rw [hYo i h2, hYo (i + 1) (by omega)]
              exact hX.step i hi
        width := by
          intro i hi
          by_cases h2 : i = j + 1
          · subst h2
            rw [hYj]
            exact hlt'.le.trans (hX.width _ hi)
          · rw [hYo i h2]
            exact hX.width i hi }
    have hlt : chainWeight G (Y (j + 1)) < chainWeight G (X (j + 1)) := by
      rw [hYj]
      unfold chainWeight
      have hc : (a ∪ b).card ≤ Fintype.card V := card_le_univ _
      have := Nat.mul_le_mul_right (Fintype.card V + 1) (Nat.succ_le_of_lt hlt')
      rw [Nat.succ_mul] at this
      rw [← hb]
      omega
    exact ih _ (h ▸ sum_lt_of_update (by omega) hYo hlt) hY rfl

/-! ### An increasing chain is a layout -/

variable (G) in
/-- An increasing chain from `∅` to `univ` of width `≤ K` gives `vs(G) ≤ K`:
order the vertices by the index at which they enter. Every prefix of that
layout is a set of the chain, and its active suffix is the set's outer
boundary. -/
theorem vertexSeparation_le_of_monotone_chain {K n : ℕ} {X : ℕ → Finset V}
    (hX : IsChain G K ∅ univ n X) (hmono : ∀ i < n, X i ⊆ X (i + 1)) :
    vertexSeparation G ≤ K := by
  have hle : ∀ i i', i ≤ i' → i' ≤ n → X i ⊆ X i' := by
    intro i i' hii'
    induction i', hii' using Nat.le_induction with
    | base => exact fun _ => subset_rfl
    | succ i' _ ih => exact fun h => (ih (by omega)).trans (hmono i' (by omega))
  have hin : ∀ v, v ∈ X n := fun v => by rw [hX.stop]; exact mem_univ v
  let τ : V → ℕ := fun v => sInf {i | v ∈ X i}
  have hτmem : ∀ v, v ∈ X (τ v) := fun v => Nat.sInf_mem (s := {i | v ∈ X i}) ⟨n, hin v⟩
  have hτn : ∀ v, τ v ≤ n := fun v => Nat.sInf_le (hin v)
  have hτmin : ∀ v i, i < τ v → v ∉ X i := fun v i hi => Nat.notMem_of_lt_sInf hi
  have hmem : ∀ v i, i ≤ n → (v ∈ X i ↔ τ v ≤ i) := by
    intro v i hi
    constructor
    · intro h
      by_contra hlt
      exact hτmin v i (by omega) h
    · intro h
      exact hle _ _ h hi (hτmem v)
  obtain ⟨σ, hσ⟩ := exists_layout_sorted τ
  have hvs : vertexSepOfLayout G σ ≤ K := by
    rw [vertexSepOfLayout_le_iff]
    intro i hi
    set v := σ.symm ⟨i, hi⟩ with hv
    have hσv : (σ v).val = i := by simp [hv]
    have hpre : ∀ u, u ∈ prefixSet σ i ↔ u ∈ X (τ v) := by
      intro u
      rw [mem_prefixSet_iff, hmem u _ (hτn v)]
      constructor
      · intro hu
        by_contra hlt
        have := hσ v u (by omega)
        omega
      · intro hu
        by_contra hgt
        rcases Nat.lt_or_ge (τ u) (τ v) with hlt | hge
        · have := hσ u v hlt
          omega
        · have heq : τ u = τ v := le_antisymm hu hge
          have huv : u ≠ v := by
            rintro rfl
            omega
          have hτ0 : τ v ≠ 0 := by
            intro h0
            have := hτmem v
            rw [h0, hX.start] at this
            simp at this
          have hstep := hX.step (τ v - 1) (by have := hτn v; omega)
          rw [show τ v - 1 + 1 = τ v by omega] at hstep
          have hsub : ({u, v} : Finset V) ⊆ X (τ v) \ X (τ v - 1) := by
            intro x hx
            rw [mem_insert, mem_singleton] at hx
            rw [mem_sdiff]
            rcases hx with hx | hx
            · rw [hx]
              exact ⟨heq ▸ hτmem u, hτmin u _ (by omega)⟩
            · rw [hx]
              exact ⟨hτmem v, hτmin v _ (by omega)⟩
          have := (card_le_card hsub).trans hstep
          rw [card_pair huv] at this
          omega
    have hact : activeSuffix G σ i = outerBd G (X (τ v)) := by
      ext w
      rw [mem_activeSuffix_iff, mem_outerBd]
      constructor
      · rintro ⟨hw, u, hu, huw⟩
        refine ⟨fun h => ?_, u, (hpre u).mp hu, huw⟩
        have := (hpre w).mpr h
        rw [mem_prefixSet_iff] at this
        omega
      · rintro ⟨hw, u, hu, huw⟩
        refine ⟨?_, u, (hpre u).mpr hu, huw⟩
        by_contra h
        exact hw ((hpre w).mp ((mem_prefixSet_iff _ _ _).mpr (by omega)))
    unfold vertexSepAt
    rw [hact]
    exact hX.width _ (hτn v)
  exact (vertexSeparation_le_vertexSepOfLayout G σ).trans hvs

/-! ### From any strategy to a chain -/

section Game

open Classical in
/-- The vertices touching no contaminated edge. -/
noncomputable def cleanSet (s : SearchState V) : Finset V :=
  univ.filter fun v => ∀ e ∈ s.contaminated, v ∉ e

theorem mem_cleanSet {s : SearchState V} {v : V} :
    v ∈ cleanSet s ↔ ∀ e ∈ s.contaminated, v ∉ e := by
  classical
  simp [cleanSet]

/-- In a closed position, a vertex outside the clean set with a clean
neighbour carries a searcher: otherwise the gas would spread from it to the
edge joining it to that neighbour. -/
theorem outerBd_cleanSet_subset {s : SearchState V} (hs : IsClosed (G := G) s) :
    outerBd G (cleanSet s) ⊆ s.guards := by
  intro w hw
  obtain ⟨hwA, v, hvA, hvw⟩ := (mem_outerBd G).mp hw
  rw [mem_cleanSet] at hwA hvA
  push Not at hwA
  obtain ⟨f, hf, hwf⟩ := hwA
  by_contra hwS
  have := hs s(v, w) (G.mem_edgeSet.mpr hvw) f hf w (Sym2.mem_mk_right _ _) w hwf hwS
    Relation.ReflTransGen.refl
  exact hvA _ this (Sym2.mem_mk_left _ _)

/-- A vertex that becomes clean in a step carries a searcher after it: its last
contaminated edge was cleared, so both its endpoints are guarded. -/
theorem mem_guards_of_newly_clean {s : SearchState V} {m : SearchMove V} {v : V}
    (hv' : v ∈ cleanSet (searchStep G s m)) (hv : v ∉ cleanSet s) :
    v ∈ (searchStep G s m).guards := by
  rw [mem_cleanSet] at hv hv'
  push Not at hv
  obtain ⟨e, he, hve⟩ := hv
  by_contra hvS
  exact hv' e (mem_step_of_mem he fun hg => hvS (hg v hve)) hve

/-- A step that removes no searcher recontaminates nothing (from a closed
position). -/
theorem step_subset_of_guards_subset {s : SearchState V} (hs : IsClosed (G := G) s)
    {m : SearchMove V} (hm : s.guards ⊆ (searchStep G s m).guards) :
    (searchStep G s m).contaminated ⊆ s.contaminated := by
  rintro e (he | ⟨heE, f, hf, x, hx, y, hy, hxS, hxy⟩)
  · exact he.1
  · exact hs e heE f hf.1 x hx y hy (fun h => hxS (hm h)) (hxy.mono hm)

/-- **One move as a chain.** From a closed position with at most `k` searchers
before and after the move, and a clean set of boundary `≤ k - 1`, there is a
chain of width `≤ k - 1` from the clean set before to the clean set after:
first shrink to their intersection, then add the newly clean vertices one at a
time. Every set strictly between has a guarded vertex inside it, so its
boundary misses at least one of the `≤ k` searchers; the one exception, the
intersection itself, is the old clean set unless the move deleted a searcher,
and then only `k - 1` are left. -/
theorem exists_chain_step {s : SearchState V} (hs : IsClosed (G := G) s) (m : SearchMove V)
    {k : ℕ} (hS : s.guards.card ≤ k) (hS' : (searchStep G s m).guards.card ≤ k)
    (hA : (outerBd G (cleanSet s)).card ≤ k - 1) :
    ∃ n X, IsChain G (k - 1) (cleanSet s) (cleanSet (searchStep G s m)) n X := by
  set s' := searchStep G s m with hs'
  set A := cleanSet s
  set A' := cleanSet s'
  have hbd' : outerBd G A' ⊆ s'.guards := outerBd_cleanSet_subset (isClosed_step s m)
  have hgood : ∀ C, A ∩ A' ⊆ C → C ⊆ A' → (outerBd G C).card ≤ k - 1 := by
    intro C h1 h2
    have hsub : outerBd G C ⊆ s'.guards \ C := by
      intro w hw
      obtain ⟨hwC, v, hvC, hvw⟩ := (mem_outerBd G).mp hw
      refine mem_sdiff.mpr ⟨?_, hwC⟩
      by_cases hwA' : w ∈ A'
      · exact mem_guards_of_newly_clean hwA' fun hwA => hwC (h1 (mem_inter.mpr ⟨hwA, hwA'⟩))
      · exact hbd' ((mem_outerBd G).mpr ⟨hwA', v, h2 hvC, hvw⟩)
    by_cases hx : ∃ x ∈ C, x ∈ s'.guards
    · obtain ⟨x, hxC, hxS⟩ := hx
      have h3 : s'.guards \ C ⊆ s'.guards.erase x := by
        intro w hw
        rw [mem_sdiff] at hw
        exact mem_erase.mpr ⟨fun h => hw.2 (h ▸ hxC), hw.1⟩
      have := (card_le_card (hsub.trans h3))
      rw [card_erase_of_mem hxS] at this
      omega
    · push Not at hx
      by_cases hlt : s'.guards.card < k
      · have := card_le_card (hsub.trans sdiff_subset)
        omega
      · have hgrow : s.guards ⊆ s'.guards := by
          cases m with
          | place u => exact subset_insert _ _
          | remove u =>
            change s.guards ⊆ s.guards.erase u
            by_cases hu : u ∈ s.guards
            · exfalso
              apply hlt
              change (s.guards.erase u).card < k
              rw [card_erase_of_mem hu]
              have := card_pos.mpr ⟨u, hu⟩
              omega
            · rw [erase_eq_of_notMem hu]
        have hAA' : A ⊆ A' := by
          intro v hv
          rw [mem_cleanSet] at hv ⊢
          exact fun e he => hv e (step_subset_of_guards_subset hs hgrow he)
        have hC : C = A := by
          apply Subset.antisymm
          · intro x hxC
            by_contra hxA
            exact hx x hxC (mem_guards_of_newly_clean (h2 hxC) hxA)
          · intro x hxA
            exact h1 (mem_inter.mpr ⟨hxA, hAA' hxA⟩)
        rw [hC]
        exact hA
  have h1 : IsChain G (k - 1) A (A ∩ A') 1 (fun i => if i = 0 then A else A ∩ A') :=
    { start := rfl
      stop := rfl
      step := by
        intro i hi
        obtain rfl : i = 0 := by omega
        simp only [↓reduceIte, show (0 + 1 = 0) = False by simp]
        rw [sdiff_eq_empty_iff_subset.mpr inter_subset_left, card_empty]
        exact Nat.zero_le _
      width := by
        intro i hi
        by_cases h0 : i = 0
        · simp only [h0, ↓reduceIte]
          exact hA
        · simp only [h0, ↓reduceIte]
          exact hgood _ subset_rfl inter_subset_right }
  obtain ⟨n, X, hX⟩ := exists_chain_of_interval inter_subset_right hgood
  exact ⟨_, _, h1.trans hX⟩

variable (G) in
/-- **The lower half of [10] Theorem 4.1 for the full game.** Any strategy —
recontamination allowed — clearing a graph with an edge with at most `k`
searchers gives `vs(G) + 1 ≤ k`. -/
theorem vertexSeparation_add_one_le_of_isNodeSearch {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) {k : ℕ}
    {ms : List (SearchMove V)} (h : IsNodeSearch G k ms) :
    vertexSeparation G + 1 ≤ k := by
  have hk2 := two_le_of_isNodeSearch G h₀ h
  obtain ⟨hclr, hcost⟩ := h
  let st : ℕ → SearchState V := fun t => runSearch G (searchInit G) (ms.take t)
  have hcard : ∀ t, (st t).guards.card ≤ k :=
    fun t => (card_le_searchCost_take _ _ t).trans hcost
  have hclosed : ∀ t, IsClosed (G := G) (st t) :=
    fun t => isClosed_runSearch isClosed_init _
  have key : ∀ t ≤ ms.length, ∃ n X, IsChain G (k - 1) ∅ (cleanSet (st t)) n X := by
    intro t ht
    induction t with
    | zero =>
      have h0 : st 0 = searchInit G := by simp [st, runSearch]
      rw [h0]
      refine exists_chain_of_interval (empty_subset _) fun C _ hC => ?_
      rw [card_eq_zero.mpr]
      · exact Nat.zero_le _
      · apply eq_empty_of_forall_notMem
        intro w hw
        obtain ⟨-, v, hvC, hvw⟩ := (mem_outerBd G).mp hw
        have := mem_cleanSet.mp (hC hvC)
        exact this s(v, w) (G.mem_edgeSet.mpr hvw) (Sym2.mem_mk_left _ _)
    | succ t ih =>
      obtain ⟨n, X, hX⟩ := ih (by omega)
      have hstep : st (t + 1) = searchStep G (st t) ms[t] :=
        runSearch_take_succ (G := G) (searchInit G) ms (by omega)
      have hA : (outerBd G (cleanSet (st t))).card ≤ k - 1 := by
        have := hX.width n le_rfl
        rwa [hX.stop] at this
      obtain ⟨n', Y, hY⟩ := exists_chain_step (hclosed t) ms[t] (hcard t)
        (hstep ▸ hcard (t + 1)) hA
      rw [hstep]
      exact ⟨_, _, hX.trans hY⟩
  obtain ⟨n, X, hX⟩ := key ms.length le_rfl
  have hfin : cleanSet (st ms.length) = univ := by
    apply eq_univ_of_forall
    intro v
    rw [mem_cleanSet]
    intro e he
    have : st ms.length = runSearch G (searchInit G) ms := by simp [st]
    rw [this, hclr] at he
    exact absurd he (Set.notMem_empty e)
  rw [hfin] at hX
  obtain ⟨Y, hY, hYmono⟩ := exists_monotone_chain hX
  have := vertexSeparation_le_of_monotone_chain G hY hYmono
  omega

end Game

/-! ### The full theorems -/

section Main

variable (G)

/-- **Kirousis & Papadimitriou (1986), Theorem 4.1, for the full game.** For
every graph with at least one edge, `ns(G) = vs(G) + 1`. -/
theorem nodeSearch_eq_vertexSeparation_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G = vertexSeparation G + 1 := by
  refine le_antisymm (nodeSearch_le_vertexSeparation_add_one G h₀) ?_
  obtain ⟨ms, hms⟩ := Nat.sInf_mem (s := {k | ∃ ms, IsNodeSearch G k ms})
    ⟨_, shackStrategy G (Fintype.equivFin V), (shackStrategy_isMonotone G _).1⟩
  exact vertexSeparation_add_one_le_of_isNodeSearch G h₀ hms

/-- With Kinnersley's theorem: `ns(G) = pw(G) + 1` for every graph with an edge. -/
theorem nodeSearch_eq_pathwidth_add_one {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G = pathwidth G + 1 := by
  rw [nodeSearch_eq_vertexSeparation_add_one G h₀, vertexSeparation_eq_pathwidth]

/-- **Recontamination does not help** ([10] Theorem 2.3), for every finite
graph: the named gap of `NodeSearch.lean`, discharged. On a graph with an edge
both numbers are `vs + 1`; on an edgeless graph both are `0`. -/
theorem nodeSearchMonotonicity : NodeSearchMonotonicity G := by
  unfold NodeSearchMonotonicity
  by_cases h : ∃ u v, G.Adj u v
  · obtain ⟨u, v, huv⟩ := h
    rw [nodeSearch_eq_vertexSeparation_add_one G huv,
      monotoneNodeSearch_eq_vertexSeparation_add_one G huv]
  · push Not at h
    rw [nodeSearch_of_edgeless G h, monotoneNodeSearch_of_edgeless G h]

/-- **Kirousis & Papadimitriou (1985), the Theorem, for the full game**: on
every graph with an edge, `ns(G) = θ(G)`. -/
theorem nodeSearch_eq_intervalThickness {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    nodeSearch G = intervalThickness G :=
  nodeSearch_eq_intervalThickness_of_monotonicity G (nodeSearchMonotonicity G) h₀

/-- The chain of section 3 with the full game at its centre:
`θ = ns = mns = vs + 1 = pw + 1` on every graph with an edge. -/
theorem nodeSearch_chain {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    intervalThickness G = nodeSearch G ∧ nodeSearch G = monotoneNodeSearch G ∧
      monotoneNodeSearch G = vertexSeparation G + 1 ∧
      vertexSeparation G + 1 = pathwidth G + 1 :=
  ⟨(nodeSearch_eq_intervalThickness G h₀).symm, nodeSearchMonotonicity G,
    monotoneNodeSearch_eq_vertexSeparation_add_one G h₀,
    by rw [vertexSeparation_eq_pathwidth]⟩

end Main

namespace NetGateMatrix

variable {N Gt : Type*} [Fintype N] [DecidableEq N] [Fintype Gt] [DecidableEq Gt]
variable (M : NetGateMatrix N Gt) [DecidableRel M.conn] [DecidableRel M.netGraph.Adj]

/-- **Möhring (1990), Theorem 3.9, for the full game**: when two nets share a
gate, the least number of tracks equals the node search number of the net
graph. -/
theorem tracks_eq_nodeSearch {n₀ n₁ : N} (h₀ : M.netGraph.Adj n₀ n₁) :
    M.tracks = nodeSearch M.netGraph :=
  M.tracks_eq_nodeSearch_of_monotonicity (nodeSearchMonotonicity _) h₀

end NetGateMatrix

end Complex

end MOSPFormalization
