/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Maximum wavefront = pathwidth + 1

A candidate fourteenth member of the pathwidth complex (paper 3), from
numerical linear algebra: the maximum wavefront of a sparse symmetric matrix,
the storage of the frontal matrix in a frontal factorisation.

## The source's definition

Kumfert & Pothen (1997), *Two improved algorithms for envelope and wavefront
reduction*, ICASE Report 97-33 (BIT 37(3)), §2.1, pp. 3–4. The matrix
`A = [a_ij]` is "a sparse symmetric n × n matrix ... whose diagonal elements
are all nonzero". "Consider the ith step of Cholesky factorization where only
the lower triangle of A is stored. An equation (row) k is *active* at the ith
step if k ≥ i and there exists a column l ≤ i such that a_kl ≠ 0. The ith
*wavefront* of A, wf_i(A), is the set of active equations during the ith step
of Cholesky factorization." And: "maxwf(A) = max_{1≤i≤n} |wf_i(A)|". The
ordering is a symmetric permutation `A' = P A P^T`.

Formalised here with the matrix read off a graph, positions `0`-based, an
ordering a `LinearLayout`:

* the nonzero pattern of `A` is `k = l ∨ G.Adj k l` (nonzero diagonal, and an
  off-diagonal nonzero exactly on the edges of the adjacency graph `G`);
* `wavefront G σ i` — the active equations at step `i`: rows `k` at a position
  `≥ i` with a nonzero `a_kl` in a column `l` at a position `≤ i`;
* `maxWavefront G σ` — the maximum over the `n` steps;
* `minMaxWavefront G` — the minimum over all orderings.

Nothing in these definitions mentions separation or path decompositions.

## What is proved

* `wavefront_eq_insert_activeSuffix`, `card_wavefront` — per step, for every
  ordering: `wf_i = {v_i} ∪ activeSuffix σ i`, so `|wf_i| = vertexSepAt σ i + 1`.
  The library's `activeSuffix` counts suffix vertices with a neighbour in the
  prefix, which is exactly the off-diagonal part of the wavefront, so **no
  reversal is needed** in this convention. Against the textbook (Kinnersley)
  convention, which counts prefix vertices with a neighbour in the suffix, the
  wavefront is the boundary of the reversed ordering:
  `wavefront_eq_shackAfterPut_reverse`.
* `maxWavefront_eq_vertexSepOfLayout_add_one` — per ordering, `maxwf = vs + 1`
  whenever `V` is nonempty.
* `minMaxWavefront_eq_vertexSeparation_add_one`,
  `minMaxWavefront_eq_pathwidth_add_one` — the theorem.
* `wavefront_eq_outShackBeforeMove`, `maxWavefront_eq_outNarrowness`,
  `minMaxWavefront_eq_narrowness` — the wavefront is, set for set, Kornai &
  Tuza's out-sequence shack just before `w_i` leaves (`Narrowness.lean`): the
  two definitions coincide verbatim, so minimum maximum wavefront is narrowness
  on every graph, empty or not.

## Edge cases

* No vertices: `minMaxWavefront_of_isEmpty`, the value is `0` while
  `pw + 1 = 1`; the hypothesis of the main theorem is `Nonempty V`.
* Edgeless graphs: each wavefront is the diagonal row alone, so the value is
  `1 = pw + 1`; no special case is needed.
-/

import MOSPFormalization.Complex.Narrowness

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Complex

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Definitions (Kumfert & Pothen 1997, §2.1) -/

/-- The nonzero pattern of a symmetric matrix with nonzero diagonal and
adjacency graph `G`: `a_kl ≠ 0` iff `k = l` or `k ~ l`. -/
def MatrixNonzero (k l : V) : Prop := k = l ∨ G.Adj k l

instance (k l : V) : Decidable (MatrixNonzero G k l) := by
  unfold MatrixNonzero; infer_instance

/-- The `i`th wavefront under the ordering `σ`: the equations (rows) `k` that
are *active* at step `i`, i.e. `k ≥ i` and some column `l ≤ i` has
`a_kl ≠ 0`. -/
def wavefront (σ : LinearLayout V) (i : ℕ) : Finset V :=
  Finset.univ.filter (fun k => i ≤ (σ k).val ∧ ∃ l, (σ l).val ≤ i ∧ MatrixNonzero G k l)

/-- `maxwf` of the permuted matrix: the largest wavefront over the `n` steps. -/
noncomputable def maxWavefront (σ : LinearLayout V) : ℕ :=
  Finset.univ.sup (fun i : Fin (Fintype.card V) => (wavefront G σ i.val).card)

/-- The minimum maximum wavefront over all symmetric orderings. -/
noncomputable def minMaxWavefront : ℕ :=
  sInf (Set.range (fun σ : LinearLayout V => maxWavefront G σ))

/-! ### The wavefront at one step -/

theorem mem_wavefront_iff (σ : LinearLayout V) (i : ℕ) (k : V) :
    k ∈ wavefront G σ i ↔
      i ≤ (σ k).val ∧ ∃ l, (σ l).val ≤ i ∧ (k = l ∨ G.Adj k l) := by
  unfold wavefront
  rw [Finset.mem_filter]
  simp only [MatrixNonzero, Finset.mem_univ, true_and]

/-- Kumfert & Pothen's graph form: the `i`th wavefront is `v_i` together with
the unnumbered neighbours of `v_1, …, v_i`, which is the active suffix. -/
theorem wavefront_eq_insert_activeSuffix (σ : LinearLayout V)
    (i : Fin (Fintype.card V)) :
    wavefront G σ i.val = insert (σ.symm i) (activeSuffix G σ i.val) := by
  ext k
  rw [mem_wavefront_iff, Finset.mem_insert, mem_activeSuffix_iff]
  simp only [mem_prefixSet_iff]
  constructor
  · rintro ⟨hle, l, hl, hkl⟩
    rcases Nat.eq_or_lt_of_le hle with heq | hlt
    · left
      rw [Equiv.eq_symm_apply]
      exact Fin.ext heq.symm
    · right
      rcases hkl with rfl | hadj
      · omega
      · exact ⟨hlt, l, hl, hadj.symm⟩
  · rintro (rfl | ⟨hgt, u, hu, hadj⟩)
    · simp only [Equiv.apply_symm_apply]
      exact ⟨le_rfl, σ.symm i, by simp, Or.inl rfl⟩
    · exact ⟨hgt.le, u, hu, Or.inr hadj.symm⟩

/-- Per step: `|wf_i| = vertexSepAt σ i + 1`. -/
theorem card_wavefront (σ : LinearLayout V) (i : Fin (Fintype.card V)) :
    (wavefront G σ i.val).card = vertexSepAt G σ i.val + 1 := by
  rw [wavefront_eq_insert_activeSuffix, Finset.card_insert_of_notMem]
  · rfl
  · rw [mem_activeSuffix_iff]
    simp

/-! ### Per ordering and at the optimum -/

/-- Per ordering: `maxwf(σ) = vs(σ) + 1` whenever `V` is nonempty. -/
theorem maxWavefront_eq_vertexSepOfLayout_add_one [Nonempty V] (σ : LinearLayout V) :
    maxWavefront G σ = vertexSepOfLayout G σ + 1 := by
  have hn : Fintype.card V ≠ 0 := Fintype.card_ne_zero
  unfold maxWavefront
  simp only [card_wavefront]
  unfold vertexSepOfLayout
  simp only [hn, ↓reduceDIte]
  apply le_antisymm
  · refine Finset.sup_le fun j _ => ?_
    have := Finset.le_sup' (fun j : Fin (Fintype.card V) =>
      vertexSepAt G σ j.val) (Finset.mem_univ j)
    omega
  · have h0 : (⟨0, Nat.pos_of_ne_zero hn⟩ : Fin (Fintype.card V)) ∈ Finset.univ :=
      Finset.mem_univ _
    have hpos := Finset.le_sup (f := fun j : Fin (Fintype.card V) =>
      vertexSepAt G σ j.val + 1) h0
    have : Finset.univ.sup' (Finset.univ_nonempty_iff.mpr ⟨⟨0, Nat.pos_of_ne_zero hn⟩⟩)
        (fun j : Fin (Fintype.card V) => vertexSepAt G σ j.val) ≤
        Finset.univ.sup (fun j : Fin (Fintype.card V) =>
          vertexSepAt G σ j.val + 1) - 1 := by
      refine Finset.sup'_le _ _ fun j _ => ?_
      have := Finset.le_sup (f := fun j : Fin (Fintype.card V) =>
        vertexSepAt G σ j.val + 1) (Finset.mem_univ j)
      omega
    omega

/-- **Minimum maximum wavefront = vertex separation + 1**, for every graph with
at least one vertex. -/
theorem minMaxWavefront_eq_vertexSeparation_add_one [Nonempty V] :
    minMaxWavefront G = vertexSeparation G + 1 := by
  have hne : (Set.range (fun σ : LinearLayout V => vertexSepOfLayout G σ)).Nonempty :=
    ⟨_, Fintype.equivFin V, rfl⟩
  have hne' : (Set.range (fun σ : LinearLayout V => maxWavefront G σ)).Nonempty :=
    ⟨_, Fintype.equivFin V, rfl⟩
  apply le_antisymm
  · obtain ⟨σ₀, hσ₀⟩ := Nat.sInf_mem hne
    refine le_trans (Nat.sInf_le ⟨σ₀, rfl⟩) ?_
    show maxWavefront G σ₀ ≤ _
    rw [maxWavefront_eq_vertexSepOfLayout_add_one]
    have h : vertexSepOfLayout G σ₀ = vertexSeparation G := hσ₀
    rw [h]
  · obtain ⟨σ₁, hσ₁⟩ := Nat.sInf_mem hne'
    have h : maxWavefront G σ₁ = minMaxWavefront G := hσ₁
    rw [← h, maxWavefront_eq_vertexSepOfLayout_add_one]
    exact Nat.add_le_add_right (vertexSeparation_le_vertexSepOfLayout G _) 1

/-- **Minimum maximum wavefront = pathwidth + 1**, for every graph with at
least one vertex (via Kinnersley 1992, `vertexSeparation_eq_pathwidth`). -/
theorem minMaxWavefront_eq_pathwidth_add_one [Nonempty V] :
    minMaxWavefront G = pathwidth G + 1 := by
  rw [minMaxWavefront_eq_vertexSeparation_add_one, vertexSeparation_eq_pathwidth]

/-- With no vertices there are no steps: the value is `0`, while `pw + 1 = 1`. -/
theorem minMaxWavefront_of_isEmpty [IsEmpty V] : minMaxWavefront G = 0 := by
  have h : ∀ σ : LinearLayout V, maxWavefront G σ = 0 := by
    intro σ
    unfold maxWavefront
    have : Fintype.card V = 0 := Fintype.card_eq_zero
    apply Nat.eq_zero_of_le_zero
    refine Finset.sup_le fun i _ => ?_
    exact absurd i.isLt (by omega)
  unfold minMaxWavefront
  apply Nat.eq_zero_of_le_zero
  exact le_trans (Nat.sInf_le ⟨Fintype.equivFin V, rfl⟩) (h _).le

/-! ### The wavefront is Kornai & Tuza's out-sequence shack -/

/-- Set for set, the `i`th wavefront is the out-sequence shack just before
`w_i` is moved to the outer memory (Kornai & Tuza 1992, §2). -/
theorem wavefront_eq_outShackBeforeMove (τ : LinearLayout V) (i : ℕ) :
    wavefront G τ i = outShackBeforeMove G τ i := by
  ext k
  rw [mem_wavefront_iff, outShackBeforeMove, Finset.mem_filter]
  simp only [EnteredBy, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨hle, l, hl, hkl⟩
    exact ⟨⟨l, hkl.imp_left Eq.symm, hl⟩, hle⟩
  · rintro ⟨⟨l, hkl, hl⟩, hle⟩
    exact ⟨hle, l, hl, hkl.imp_left Eq.symm⟩

/-- Against the textbook convention (prefix vertices with a neighbour in the
suffix): the `i`th wavefront of `τ` is Kornai & Tuza's in-sequence shack of the
reversed ordering at the mirrored step. -/
theorem wavefront_eq_shackAfterPut_reverse (τ : LinearLayout V)
    (i : Fin (Fintype.card V)) :
    wavefront G τ i.val = shackAfterPut G (reverseLayout τ) (Fin.rev i).val := by
  rw [wavefront_eq_outShackBeforeMove, ← outShackBeforeMove_reverse,
    reverseLayout_reverseLayout, Fin.rev_rev]

theorem maxWavefront_eq_outNarrowness (τ : LinearLayout V) :
    maxWavefront G τ = outNarrowness G τ := by
  rw [outNarrowness_eq_sup]
  unfold maxWavefront
  simp only [wavefront_eq_outShackBeforeMove]

/-- Minimum maximum wavefront is narrowness, on every graph (empty or not). -/
theorem minMaxWavefront_eq_narrowness :
    minMaxWavefront G = narrowness G := by
  rw [← outNarrownessGraph_eq_narrowness]
  unfold minMaxWavefront outNarrownessGraph
  simp only [maxWavefront_eq_outNarrowness]

end Complex

end MOSPFormalization
