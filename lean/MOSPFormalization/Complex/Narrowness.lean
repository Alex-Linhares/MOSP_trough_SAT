/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Narrowness = pathwidth + 1

Table 1 of Linhares & Yanasse (2002), row "narrowness", source [11] Kornai &
Tuza (1992), *Narrowness, path-width, and their application in natural
language processing*, Discrete Applied Mathematics 36, 87–92.

## The source's definition

Kornai & Tuza §2 (p. 2): a graph is moved from the inner memory (IM) to the
outer memory (OM) through the *shack*. For an in-sequence `(v₁, …, vₙ)` of
the vertices, "In the i-th step, put vertex vᵢ from the IM into the shack;
move all vⱼ (j ≤ i) with no neighbors vₖ, k > i, from the shack to the OM;
then go to the (i+1)-st step. The maximum number of vertices in the shack
during this process ... will be called the narrowness of the in-sequence".
"Definition. [TK] The narrowness ν(G) of a graph G = (V, E) is the minimum
value of ν(v₁, …, vₙ) taken over all permutations."

The dual (same page): for an out-sequence `(w₁, …, wₙ)`, "For each v ∈ V
there is a smallest subscript i such that v = wᵢ or v is adjacent to wᵢ.
Putting v into the shack just before wᵢ is moved to the OM, the largest number
of vertices in the shack during this process" is the narrowness of the
out-sequence.

Formalised here as the process, not as a formula (positions are `0`-based, a
sequence is a `LinearLayout`):

* `MovedAt σ i v` — at step `i`, `v` is one of the `vⱼ` (`j ≤ i`) with no
  neighbour `vₖ`, `k > i`, so it is moved to the OM;
* `shackAfterPut σ i` — the shack just after `vᵢ` is put in: every vertex put
  in at a step `≤ i` and moved out at no step `< i`;
* `shackAfterMove σ i` — the shack at the end of step `i`;
* `inNarrowness σ` — the maximum of both, over all steps;
* `narrowness G` — the minimum over all in-sequences;
* `outShackBeforeMove`, `outShackAfterMove`, `outNarrowness` — the dual, with
  "v has been put in by step `i`" read as "the smallest subscript is `≤ i`",
  i.e. some `u ∈ N[v]` has position `≤ i`.

Nothing in these definitions mentions separation or path decompositions.

## What is proved

* `inNarrowness_eq_vertexSepOfLayout_reverse` — per sequence, not only at the
  optimum: `ν(σ) = vs(σ reversed) + 1` whenever `V` is nonempty. The shack just
  after `vᵢ` is put in is `vᵢ` together with the earlier vertices that still
  have a neighbour at `i` or later, which is the active suffix of the reversed
  layout at the mirrored position (`shackAfterPut_eq_insert_activeSuffix`); the
  end-of-step shack is contained in it (`shackAfterMove_subset_shackAfterPut`).
  The reversal is only a convention: `activeSuffix` counts suffix vertices
  with a neighbour in the prefix, Kornai & Tuza's shack counts prefix vertices
  with a neighbour in the suffix.
* `outNarrowness_reverse` and `exists_inNarrowness_iff_exists_outNarrowness`
  — **Proposition 2.1**: "there is an in-sequence of narrowness k if and only
  if there is an out-sequence of narrowness k", by their proof: the
  in-sequence `(vᵢ)` and the out-sequence `wᵢ = vₙ₊₁₋ᵢ` have the same
  narrowness. Hence `outNarrownessGraph_eq_narrowness`.
* `narrowness_eq_vertexSeparation_add_one` and
  `narrowness_eq_pathwidth_add_one` — **Proposition 3.1**: "For every graph G
  with at least one vertex, ν(G) = π(G) + 1." Proved through
  `vertexSeparation_eq_pathwidth` (Kinnersley 1992) rather than by Kornai &
  Tuza's direct construction; their `Xᵢ` (the shack just after `vᵢ` is put in)
  is exactly `shackAfterPut σ i`.

## Edge cases

* No vertices: `narrowness_of_isEmpty`, `ν = 0` while `pw + 1 = 1`; this is
  why Prop. 3.1 says "with at least one vertex". The hypothesis is
  `Nonempty V`.
* Isolated vertices and disconnected graphs need nothing special: an isolated
  vertex is put in and moved out in the same step, costing one place; so an
  edgeless nonempty graph has `ν = 1 = pw + 1`.
-/

import MOSPFormalization.VSEquivPW

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### In-sequences (Kornai & Tuza §2) -/

/-- At step `i` of the in-sequence `σ`, vertex `v` is moved from the shack to
the OM: it has been put in (`σ v ≤ i`) and has no neighbour at a position
`> i`. -/
def MovedAt (σ : LinearLayout V) (i : ℕ) (v : V) : Prop :=
  (σ v).val ≤ i ∧ ∀ u, G.Adj v u → (σ u).val ≤ i

instance (σ : LinearLayout V) (i : ℕ) (v : V) : Decidable (MovedAt G σ i v) := by
  unfold MovedAt; infer_instance

/-- The shack just after `vᵢ` is put in at step `i`: every vertex put in at a
step `≤ i` and moved to the OM at no earlier step. -/
def shackAfterPut (σ : LinearLayout V) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => (σ v).val ≤ i ∧ ∀ i' < i, ¬ MovedAt G σ i' v)

/-- The shack at the end of step `i`, after the moves to the OM. -/
def shackAfterMove (σ : LinearLayout V) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => (σ v).val ≤ i ∧ ∀ i' ≤ i, ¬ MovedAt G σ i' v)

/-- The narrowness `ν(v₁, …, vₙ)` of an in-sequence: the maximum number of
vertices in the shack during the process (Kornai & Tuza §2). -/
noncomputable def inNarrowness (σ : LinearLayout V) : ℕ :=
  Finset.univ.sup (fun i : Fin (Fintype.card V) =>
    max (shackAfterPut G σ i.val).card (shackAfterMove G σ i.val).card)

/-- **Narrowness** `ν(G)` (Kornai & Tuza §2, Definition, after [TK]): the
minimum narrowness over all in-sequences. -/
noncomputable def narrowness : ℕ :=
  sInf (Set.range (fun σ : LinearLayout V => inNarrowness G σ))

/-! ### Out-sequences (Kornai & Tuza §2, the "dual" version) -/

/-- By step `i` of the out-sequence `τ`, vertex `v` has been put into the
shack: the smallest subscript `j` with `v = w_j` or `v` adjacent to `w_j` is at
most `i`. -/
def EnteredBy (τ : LinearLayout V) (i : ℕ) (v : V) : Prop :=
  ∃ u, (u = v ∨ G.Adj v u) ∧ (τ u).val ≤ i

instance (τ : LinearLayout V) (i : ℕ) (v : V) : Decidable (EnteredBy G τ i v) := by
  unfold EnteredBy; infer_instance

/-- The shack just before `wᵢ` is moved to the OM. -/
def outShackBeforeMove (τ : LinearLayout V) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => EnteredBy G τ i v ∧ i ≤ (τ v).val)

/-- The shack just after `wᵢ` is moved to the OM. -/
def outShackAfterMove (τ : LinearLayout V) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun v => EnteredBy G τ i v ∧ i < (τ v).val)

/-- The narrowness of an out-sequence: the largest number of vertices in the
shack during the process. -/
noncomputable def outNarrowness (τ : LinearLayout V) : ℕ :=
  Finset.univ.sup (fun i : Fin (Fintype.card V) =>
    max (outShackBeforeMove G τ i.val).card (outShackAfterMove G τ i.val).card)

/-- The minimum narrowness over all out-sequences. -/
noncomputable def outNarrownessGraph : ℕ :=
  sInf (Set.range (fun τ : LinearLayout V => outNarrowness G τ))

/-! ### The shacks in closed form -/

theorem mem_shackAfterPut_iff (σ : LinearLayout V) (i : ℕ) (v : V) :
    v ∈ shackAfterPut G σ i ↔
      (σ v).val ≤ i ∧ ∃ u, (u = v ∨ G.Adj v u) ∧ i ≤ (σ u).val := by
  simp only [shackAfterPut, Finset.mem_filter, Finset.mem_univ, true_and, MovedAt,
    not_and, not_forall]
  constructor
  · rintro ⟨hle, hnot⟩
    refine ⟨hle, ?_⟩
    rcases Nat.eq_or_lt_of_le hle with heq | hlt
    · exact ⟨v, Or.inl rfl, heq.ge⟩
    · obtain ⟨u, hadj, hu⟩ := hnot (i - 1) (by omega) (by omega)
      exact ⟨u, Or.inr hadj, by omega⟩
  · rintro ⟨hle, u, hu, hiu⟩
    refine ⟨hle, fun i' hi' hvi' => ?_⟩
    rcases hu with rfl | hadj
    · omega
    · exact ⟨u, hadj, by omega⟩

theorem shackAfterMove_subset_shackAfterPut (σ : LinearLayout V) (i : ℕ) :
    shackAfterMove G σ i ⊆ shackAfterPut G σ i := by
  intro v hv
  simp only [shackAfterMove, shackAfterPut, Finset.mem_filter, Finset.mem_univ,
    true_and] at hv ⊢
  exact ⟨hv.1, fun i' hi' => hv.2 i' hi'.le⟩

theorem outShackAfterMove_subset_outShackBeforeMove (τ : LinearLayout V) (i : ℕ) :
    outShackAfterMove G τ i ⊆ outShackBeforeMove G τ i := by
  intro v hv
  simp only [outShackAfterMove, outShackBeforeMove, Finset.mem_filter,
    Finset.mem_univ, true_and] at hv ⊢
  exact ⟨hv.1, hv.2.le⟩

/-- The maximum is reached just after an insertion. -/
theorem inNarrowness_eq_sup (σ : LinearLayout V) :
    inNarrowness G σ = Finset.univ.sup (fun i : Fin (Fintype.card V) =>
      (shackAfterPut G σ i.val).card) := by
  unfold inNarrowness
  congr 1
  funext i
  exact max_eq_left (Finset.card_le_card (shackAfterMove_subset_shackAfterPut G σ i))

/-- The maximum is reached just before a removal. -/
theorem outNarrowness_eq_sup (τ : LinearLayout V) :
    outNarrowness G τ = Finset.univ.sup (fun i : Fin (Fintype.card V) =>
      (outShackBeforeMove G τ i.val).card) := by
  unfold outNarrowness
  congr 1
  funext i
  exact max_eq_left
    (Finset.card_le_card (outShackAfterMove_subset_outShackBeforeMove G τ i))

/-! ### Reversal -/

/-- The reverse of a sequence: position `i` goes to `n - 1 - i`. -/
def reverseLayout (σ : LinearLayout V) : LinearLayout V :=
  σ.trans Fin.revPerm

@[simp] theorem reverseLayout_apply_val (σ : LinearLayout V) (v : V) :
    (reverseLayout σ v).val = Fintype.card V - 1 - (σ v).val := by
  simp only [reverseLayout, Equiv.trans_apply, Fin.revPerm_apply, Fin.val_rev]
  omega

@[simp] theorem reverseLayout_reverseLayout (σ : LinearLayout V) :
    reverseLayout (reverseLayout σ) = σ := by
  ext v
  simp only [reverseLayout, Equiv.trans_apply, Fin.revPerm_apply, Fin.rev_rev]

theorem sup_comp_rev {n : ℕ} (f : Fin n → ℕ) :
    Finset.univ.sup (fun i => f (Fin.rev i)) = Finset.univ.sup f := by
  apply le_antisymm
  · exact Finset.sup_le fun i _ => Finset.le_sup (f := f) (Finset.mem_univ _)
  · refine Finset.sup_le fun i _ => ?_
    have := Finset.le_sup (f := fun i => f (Fin.rev i)) (Finset.mem_univ (Fin.rev i))
    simpa only [Fin.rev_rev] using this

/-- The shack just after `vᵢ` is put in is `vᵢ` together with the active
suffix of the reversed sequence at the mirrored position. -/
theorem shackAfterPut_eq_insert_activeSuffix (σ : LinearLayout V)
    (i : Fin (Fintype.card V)) :
    shackAfterPut G σ i.val =
      insert (σ.symm i) (activeSuffix G (reverseLayout σ) (Fin.rev i).val) := by
  ext v
  rw [mem_shackAfterPut_iff, Finset.mem_insert, mem_activeSuffix_iff]
  have hσv := (σ v).isLt
  have hi := i.isLt
  simp only [reverseLayout_apply_val, Fin.val_rev, mem_prefixSet_iff]
  constructor
  · rintro ⟨hle, u, hu, hiu⟩
    rcases Nat.eq_or_lt_of_le hle with heq | hlt
    · left
      rw [Equiv.eq_symm_apply]
      exact Fin.ext heq
    · right
      rcases hu with rfl | hadj
      · omega
      · refine ⟨by omega, u, ?_, hadj.symm⟩
        have := (σ u).isLt
        omega
  · rintro (rfl | ⟨hgt, u, hu, hadj⟩)
    · simp only [Equiv.apply_symm_apply]
      exact ⟨le_rfl, σ.symm i, Or.inl rfl, by simp⟩
    · have := (σ u).isLt
      exact ⟨by omega, u, Or.inr hadj.symm, by omega⟩

theorem card_shackAfterPut (σ : LinearLayout V) (i : Fin (Fintype.card V)) :
    (shackAfterPut G σ i.val).card =
      vertexSepAt G (reverseLayout σ) (Fin.rev i).val + 1 := by
  rw [shackAfterPut_eq_insert_activeSuffix, Finset.card_insert_of_notMem]
  · rfl
  · rw [mem_activeSuffix_iff]
    simp only [Equiv.apply_symm_apply, reverseLayout_apply_val, Fin.val_rev]
    omega

/-- Per sequence: the narrowness of an in-sequence is the vertex separation of
the reversed sequence plus one. -/
theorem inNarrowness_eq_vertexSepOfLayout_reverse [Nonempty V] (σ : LinearLayout V) :
    inNarrowness G σ = vertexSepOfLayout G (reverseLayout σ) + 1 := by
  have hn : Fintype.card V ≠ 0 := Fintype.card_ne_zero
  rw [inNarrowness_eq_sup]
  simp only [card_shackAfterPut]
  rw [sup_comp_rev (fun j => vertexSepAt G (reverseLayout σ) j.val + 1)]
  unfold vertexSepOfLayout
  simp only [hn, ↓reduceDIte]
  apply le_antisymm
  · refine Finset.sup_le fun j _ => ?_
    have := Finset.le_sup' (fun j : Fin (Fintype.card V) =>
      vertexSepAt G (reverseLayout σ) j.val) (Finset.mem_univ j)
    omega
  · have h0 : (⟨0, Nat.pos_of_ne_zero hn⟩ : Fin (Fintype.card V)) ∈ Finset.univ :=
      Finset.mem_univ _
    have hpos := Finset.le_sup (f := fun j : Fin (Fintype.card V) =>
      vertexSepAt G (reverseLayout σ) j.val + 1) h0
    have : Finset.univ.sup' (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero hn⟩⟩)
        (fun j : Fin (Fintype.card V) => vertexSepAt G (reverseLayout σ) j.val) ≤
        Finset.univ.sup (fun j : Fin (Fintype.card V) =>
          vertexSepAt G (reverseLayout σ) j.val + 1) - 1 := by
      refine Finset.sup'_le _ _ fun j _ => ?_
      have := Finset.le_sup (f := fun j : Fin (Fintype.card V) =>
        vertexSepAt G (reverseLayout σ) j.val + 1) (Finset.mem_univ j)
      omega
    omega

/-! ### Proposition 2.1: in- and out-sequences -/

/-- The shack just before `w_{n-1-i}` leaves in the reversed out-sequence is
the shack just after `vᵢ` enters in the in-sequence. -/
theorem outShackBeforeMove_reverse (σ : LinearLayout V) (i : Fin (Fintype.card V)) :
    outShackBeforeMove G (reverseLayout σ) (Fin.rev i).val = shackAfterPut G σ i.val := by
  ext v
  rw [mem_shackAfterPut_iff]
  simp only [outShackBeforeMove, EnteredBy, Finset.mem_filter, Finset.mem_univ,
    true_and, reverseLayout_apply_val, Fin.val_rev]
  have hσv := (σ v).isLt
  have hi := i.isLt
  constructor
  · rintro ⟨⟨u, hu, hle⟩, hge⟩
    have := (σ u).isLt
    exact ⟨by omega, u, hu, by omega⟩
  · rintro ⟨hle, u, hu, hge⟩
    have := (σ u).isLt
    exact ⟨⟨u, hu, by omega⟩, by omega⟩

/-- Kornai & Tuza's proof of Prop. 2.1: the in-sequence `(vᵢ)` and the
out-sequence `wᵢ = vₙ₊₁₋ᵢ` have the same narrowness. -/
theorem outNarrowness_reverse (σ : LinearLayout V) :
    outNarrowness G (reverseLayout σ) = inNarrowness G σ := by
  rw [outNarrowness_eq_sup, inNarrowness_eq_sup,
    ← sup_comp_rev (fun i : Fin (Fintype.card V) =>
      (outShackBeforeMove G (reverseLayout σ) i.val).card)]
  simp only [outShackBeforeMove_reverse]

/-- **Kornai & Tuza, Proposition 2.1.** For any graph `G`, there is an
in-sequence of narrowness `k` if and only if there is an out-sequence of
narrowness `k`. -/
theorem exists_inNarrowness_iff_exists_outNarrowness (k : ℕ) :
    (∃ σ : LinearLayout V, inNarrowness G σ = k) ↔
      ∃ τ : LinearLayout V, outNarrowness G τ = k := by
  constructor
  · rintro ⟨σ, hσ⟩
    exact ⟨reverseLayout σ, by rw [outNarrowness_reverse, hσ]⟩
  · rintro ⟨τ, hτ⟩
    refine ⟨reverseLayout τ, ?_⟩
    rw [← outNarrowness_reverse, reverseLayout_reverseLayout, hτ]

/-- "This latter approach leads to the same definition of narrowness." -/
theorem outNarrownessGraph_eq_narrowness :
    outNarrownessGraph G = narrowness G := by
  unfold outNarrownessGraph narrowness
  congr 1
  ext k
  exact (exists_inNarrowness_iff_exists_outNarrowness G k).symm

/-! ### Proposition 3.1 -/

theorem narrowness_eq_vertexSeparation_add_one [Nonempty V] :
    narrowness G = vertexSeparation G + 1 := by
  have hne : (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ)).Nonempty :=
    ⟨_, Fintype.equivFin V, rfl⟩
  have hne' : (Set.range (fun σ : LinearLayout V => inNarrowness G σ)).Nonempty :=
    ⟨_, Fintype.equivFin V, rfl⟩
  apply le_antisymm
  · obtain ⟨σ₀, hσ₀⟩ := Nat.sInf_mem hne
    refine le_trans (Nat.sInf_le ⟨reverseLayout σ₀, rfl⟩) ?_
    simp only [inNarrowness_eq_vertexSepOfLayout_reverse, reverseLayout_reverseLayout]
    have h : vertexSepOfLayout G σ₀ = vertexSeparation G := hσ₀
    rw [h]
  · obtain ⟨σ₁, hσ₁⟩ := Nat.sInf_mem hne'
    have h : inNarrowness G σ₁ = narrowness G := hσ₁
    rw [← h, inNarrowness_eq_vertexSepOfLayout_reverse]
    exact Nat.add_le_add_right (vertexSeparation_le_vertexSepOfLayout G _) 1

/-- **Kornai & Tuza, Proposition 3.1.** For every graph `G` with at least one
vertex, `ν(G) = π(G) + 1`. -/
theorem narrowness_eq_pathwidth_add_one [Nonempty V] :
    narrowness G = pathwidth G + 1 := by
  rw [narrowness_eq_vertexSeparation_add_one, vertexSeparation_eq_pathwidth]

/-- With no vertices the shack is never used: `ν = 0`, while `π + 1 = 1`. -/
theorem narrowness_of_isEmpty [IsEmpty V] : narrowness G = 0 := by
  have h : ∀ σ : LinearLayout V, inNarrowness G σ = 0 := by
    intro σ
    unfold inNarrowness
    have : Fintype.card V = 0 := Fintype.card_eq_zero
    apply Nat.eq_zero_of_le_zero
    refine Finset.sup_le fun i _ => ?_
    exact absurd i.isLt (by omega)
  unfold narrowness
  apply Nat.eq_zero_of_le_zero
  exact le_trans (Nat.sInf_le ⟨Fintype.equivFin V, rfl⟩) (h _).le

end Complex

end MOSPFormalization
