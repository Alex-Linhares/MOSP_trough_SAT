/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The pathwidth of the Mycielskian

The Mycielskian `μ(G)` of a graph `G` on `V` has vertex set `V ⊕ V ⊕ Unit`:
the originals `v`, the shadows `v'` and the apex `w`. Its edges are `G`'s edges
among the originals, `u' ~ v` whenever `u ~ v` in `G`, and `w ~ v'` for every
`v`; there are no edges among the shadows and none between `w` and the
originals. Mathlib has no Mycielskian, so it is defined here (`mycielskian`).

## Main results

* `pathwidth_mycielskian_le` — `pathwidth (mycielskian G) ≤ 2 * pathwidth G + 1`
  for every finite simple graph `G`. We found no published statement of this
  bound (`reports/mycielski_pathwidth.md` §1 records the search).
* `pathwidth_add_one_le_mycielskian` — `pathwidth G + 1 ≤ pathwidth (mycielskian G)`
  when `G` has a vertex. This is elementary.

## Proofs

*Upper bound*, on vertex separation (`VSEquivPW.lean`, Kinnersley 1992). The
project's convention counts the *suffix* vertices with a neighbour in the
prefix. Given a layout `u_0, …, u_{n-1}` of `G` of vertex separation `p`, lay out
`μ(G)` as `u'_0, u_0, u'_1, u_1, …, u'_{n-1}, u_{n-1}, w` (`mycLayout`). Write
`A_i` for the active suffix of `G` at `i` and `B_i` for the vertices at
positions `≥ i` with a neighbour at a position `< i` (`earlyNbrs`; `B_0 = ∅`,
`B_i ⊆ A_{i-1}`). At the prefix ending in `u_i` the active originals and the
active shadows both lie in `A_i`, plus `w`. At the prefix ending in `u'_i` the
active originals lie in `A_i ∪ (B_i ∩ {u_i})` and the active shadows in
`(B_i ∖ {u_i})'`, plus `w`. Either way at most `2p + 1`
(`vertexSepAt_mycLayout_le`).

*Lower bound*, on path decompositions. In `μ(G)` the set
`A = {w} ∪ {u' : u not isolated}` is connected, and `G` plus an apex adjacent
to every vertex is a minor of `μ(G)` with branch sets `A` for the apex, `{v}`
for a non-isolated `v` and `{v'}` for an isolated `v`. Restricting a path
decomposition of `μ(G)` to the bags between the first and the last bag meeting
`A` (by clamping indices, `exists_decomposition_card_succ_le`), every bag loses
an element of `A`.
-/

import MOSPFormalization.VSEquivPW
import MOSPFormalization.Sandwich
import MOSPFormalization.Minor
import MOSPFormalization.MOSPGraph

set_option linter.unusedSectionVars false

namespace MOSPFormalization

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### The graph -/

/-- Adjacency of the Mycielskian on originals `inl v`, shadows `inr (inl v)` and
the apex `inr (inr ())`. -/
def mycAdj (G : SimpleGraph V) : V ⊕ V ⊕ Unit → V ⊕ V ⊕ Unit → Prop
  | .inl u, .inl v => G.Adj u v
  | .inl u, .inr (.inl v) => G.Adj u v
  | .inl _, .inr (.inr _) => False
  | .inr (.inl u), .inl v => G.Adj u v
  | .inr (.inl _), .inr (.inl _) => False
  | .inr (.inl _), .inr (.inr _) => True
  | .inr (.inr _), .inl _ => False
  | .inr (.inr _), .inr (.inl _) => True
  | .inr (.inr _), .inr (.inr _) => False

/-- The **Mycielskian** of `G`. -/
def mycielskian (G : SimpleGraph V) : SimpleGraph (V ⊕ V ⊕ Unit) where
  Adj := mycAdj G
  symm := ⟨fun x y h => by
    rcases x with u | u | u <;> rcases y with v | v | v <;>
      simp only [mycAdj] at h ⊢ <;> first | exact h | exact h.symm⟩
  loopless := ⟨fun x h => by
    rcases x with u | u | u <;> simp only [mycAdj] at h
    exact G.loopless.irrefl u h⟩

section Adj

variable (G : SimpleGraph V) {u v : V} {a b : Unit}

@[simp] theorem myc_adj_inl_inl : (mycielskian G).Adj (.inl u) (.inl v) ↔ G.Adj u v := Iff.rfl
@[simp] theorem myc_adj_inl_sh : (mycielskian G).Adj (.inl u) (.inr (.inl v)) ↔ G.Adj u v :=
  Iff.rfl
@[simp] theorem myc_adj_inl_apex : ¬ (mycielskian G).Adj (.inl u) (.inr (.inr a)) := id
@[simp] theorem myc_adj_sh_inl : (mycielskian G).Adj (.inr (.inl u)) (.inl v) ↔ G.Adj u v :=
  Iff.rfl
@[simp] theorem myc_adj_sh_sh : ¬ (mycielskian G).Adj (.inr (.inl u)) (.inr (.inl v)) := id
@[simp] theorem myc_adj_sh_apex : (mycielskian G).Adj (.inr (.inl u)) (.inr (.inr a)) :=
  trivial
@[simp] theorem myc_adj_apex_inl : ¬ (mycielskian G).Adj (.inr (.inr a)) (.inl u) := id
@[simp] theorem myc_adj_apex_sh : (mycielskian G).Adj (.inr (.inr a)) (.inr (.inl u)) :=
  trivial
@[simp] theorem myc_adj_apex_apex : ¬ (mycielskian G).Adj (.inr (.inr a)) (.inr (.inr b)) := id

end Adj

instance (G : SimpleGraph V) [DecidableRel G.Adj] : DecidableRel (mycielskian G).Adj
  | .inl u, .inl v => inferInstanceAs (Decidable (G.Adj u v))
  | .inl u, .inr (.inl v) => inferInstanceAs (Decidable (G.Adj u v))
  | .inl _, .inr (.inr _) => isFalse id
  | .inr (.inl u), .inl v => inferInstanceAs (Decidable (G.Adj u v))
  | .inr (.inl _), .inr (.inl _) => isFalse id
  | .inr (.inl _), .inr (.inr _) => isTrue trivial
  | .inr (.inr _), .inl _ => isFalse id
  | .inr (.inr _), .inr (.inl _) => isTrue trivial
  | .inr (.inr _), .inr (.inr _) => isFalse id

/-- `μ(G)` has `2n + 1` vertices. -/
theorem card_mycielskian_vertices : Fintype.card (V ⊕ V ⊕ Unit) = 2 * Fintype.card V + 1 := by
  simp only [Fintype.card_sum, Fintype.card_unit]; omega

/-- Sanity check: `μ(K₂)` (the 5-cycle) has 5 edges, counted as 10 ordered pairs. -/
example : (univ.filter (fun p : (Fin 2 ⊕ Fin 2 ⊕ Unit) × (Fin 2 ⊕ Fin 2 ⊕ Unit) =>
    (mycielskian (⊤ : SimpleGraph (Fin 2))).Adj p.1 p.2)).card = 10 := by decide

/-- Sanity check: `μ(C₅)` (the Grötzsch graph) has 20 edges, as 40 ordered pairs. -/
example : (univ.filter (fun p : (Fin 5 ⊕ Fin 5 ⊕ Unit) × (Fin 5 ⊕ Fin 5 ⊕ Unit) =>
    (mycielskian (SimpleGraph.cycleGraph 5)).Adj p.1 p.2)).card = 40 := by decide

/-! ### Upper bound: the interleaved layout -/

section Upper

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Positions in the layout `u'_0, u_0, u'_1, u_1, …, w`. -/
def mycPos (σ : LinearLayout V) : V ⊕ V ⊕ Unit → ℕ
  | .inl u => 2 * (σ u).val + 1
  | .inr (.inl u) => 2 * (σ u).val
  | .inr (.inr _) => 2 * Fintype.card V

theorem mycPos_lt (σ : LinearLayout V) (x : V ⊕ V ⊕ Unit) :
    mycPos σ x < Fintype.card (V ⊕ V ⊕ Unit) := by
  rw [card_mycielskian_vertices]
  rcases x with u | u | u
  · have := (σ u).isLt; simp only [mycPos]; omega
  · have := (σ u).isLt; simp only [mycPos]; omega
  · simp only [mycPos]; omega

theorem mycPos_injective (σ : LinearLayout V) :
    Function.Injective (fun x => (⟨mycPos σ x, mycPos_lt σ x⟩ :
      Fin (Fintype.card (V ⊕ V ⊕ Unit)))) := by
  intro x y h
  simp only [Fin.mk.injEq] at h
  rcases x with u | u | u <;> rcases y with v | v | v <;> simp only [mycPos] at h
  · exact congrArg _ (σ.injective (Fin.ext (by omega)))
  · omega
  · omega
  · omega
  · exact congrArg _ (congrArg _ (σ.injective (Fin.ext (by omega))))
  · have := (σ u).isLt; omega
  · omega
  · have := (σ v).isLt; omega
  · rfl

/-- The layout `u'_0, u_0, u'_1, u_1, …, u'_{n-1}, u_{n-1}, w` of `μ(G)`. -/
noncomputable def mycLayout (σ : LinearLayout V) : LinearLayout (V ⊕ V ⊕ Unit) :=
  Equiv.ofBijective _ ((Fintype.bijective_iff_injective_and_card _).mpr
    ⟨mycPos_injective σ, by simp⟩)

theorem mycLayout_val (σ : LinearLayout V) (x : V ⊕ V ⊕ Unit) :
    (mycLayout σ x).val = mycPos σ x := rfl

theorem card_activeSuffix_le_vertexSepOfLayout (σ : LinearLayout V) (i : ℕ) :
    (activeSuffix G σ i).card ≤ vertexSepOfLayout G σ := by
  rcases (activeSuffix G σ i).eq_empty_or_nonempty with h | ⟨u, hu⟩
  · simp [h]
  · have hi : i < Fintype.card V := by
      have := ((mem_activeSuffix_iff G σ i u).mp hu).1
      have := (σ u).isLt
      omega
    exact vertexSepAt_le_vertexSepOfLayout G σ ⟨i, hi⟩

/-- The vertices at positions `≥ i` with a neighbour at a position `< i`. -/
def earlyNbrs (σ : LinearLayout V) (i : ℕ) : Finset V :=
  univ.filter (fun u => i ≤ (σ u).val ∧ ∃ z, (σ z).val < i ∧ G.Adj z u)

theorem card_earlyNbrs_le (σ : LinearLayout V) (i : ℕ) :
    (earlyNbrs G σ i).card ≤ vertexSepOfLayout G σ := by
  rcases Nat.eq_zero_or_pos i with rfl | hi
  · simp [earlyNbrs]
  · refine le_trans (card_le_card ?_) (card_activeSuffix_le_vertexSepOfLayout G σ (i - 1))
    intro u hu
    simp only [earlyNbrs, mem_filter, mem_univ, true_and] at hu
    obtain ⟨h1, z, hz, hadj⟩ := hu
    rw [mem_activeSuffix_iff]
    exact ⟨by omega, z, by rw [mem_prefixSet_iff]; omega, hadj⟩

/-- **The interleaved layout of `μ(G)` has vertex separation at most `2p + 1`** at
every position, `p` the vertex separation of the layout of `G`. -/
theorem vertexSepAt_mycLayout_le (σ : LinearLayout V) (t : ℕ) :
    vertexSepAt (mycielskian G) (mycLayout σ) t ≤ 2 * vertexSepOfLayout G σ + 1 := by
  have hA := card_activeSuffix_le_vertexSepOfLayout G σ
  have hB := card_earlyNbrs_le G σ
  let e₁ : V ↪ V ⊕ V ⊕ Unit := ⟨Sum.inl, Sum.inl_injective⟩
  let e₂ : V ↪ V ⊕ V ⊕ Unit := ⟨fun v => Sum.inr (Sum.inl v), fun a b h => by simpa using h⟩
  have hinj : ∀ {u z : V}, G.Adj z u → (σ z).val ≠ (σ u).val := fun hzu e =>
    G.ne_of_adj hzu (σ.injective (Fin.ext e))
  unfold vertexSepAt
  obtain ⟨i, rfl | rfl⟩ := Nat.even_or_odd' t
  · -- the prefix ends in the shadow `u'_i`
    set A := activeSuffix G σ i
    set B := earlyNbrs G σ i
    have hAi : A.card ≤ vertexSepOfLayout G σ := hA i
    have hBi : B.card ≤ vertexSepOfLayout G σ := hB i
    have hsub : activeSuffix (mycielskian G) (mycLayout σ) (2 * i) ⊆
        ((A ∪ B.filter (fun u => (σ u).val = i)).map e₁ ∪
          (B.filter (fun u => ¬ (σ u).val = i)).map e₂) ∪ {Sum.inr (Sum.inr ())} := by
      intro x hx
      rw [mem_activeSuffix_iff] at hx
      obtain ⟨hx, y, hy, hxy⟩ := hx
      rw [mem_prefixSet_iff, mycLayout_val] at hy
      rw [mycLayout_val] at hx
      rcases x with u | u | ⟨⟩
      · simp only [mycPos] at hx
        apply mem_union_left; apply mem_union_left
        refine mem_map_of_mem e₁ (?_ : u ∈ _)
        rcases y with z | z | ⟨⟩
        · simp only [mycPos] at hy
          simp only [myc_adj_inl_inl] at hxy
          by_cases h : (σ u).val = i
          · exact mem_union_right _ (mem_filter.mpr
              ⟨mem_filter.mpr ⟨mem_univ _, by omega, z, by omega, hxy⟩, h⟩)
          · exact mem_union_left _ ((mem_activeSuffix_iff G σ i u).mpr
              ⟨by omega, z, by rw [mem_prefixSet_iff]; omega, hxy⟩)
        · simp only [mycPos] at hy
          simp only [myc_adj_sh_inl] at hxy
          have := hinj hxy
          by_cases h : (σ u).val = i
          · exact mem_union_right _ (mem_filter.mpr
              ⟨mem_filter.mpr ⟨mem_univ _, by omega, z, by omega, hxy⟩, h⟩)
          · exact mem_union_left _ ((mem_activeSuffix_iff G σ i u).mpr
              ⟨by omega, z, by rw [mem_prefixSet_iff]; omega, hxy⟩)
        · simp at hxy
      · simp only [mycPos] at hx
        apply mem_union_left; apply mem_union_right
        refine mem_map_of_mem e₂ (?_ : u ∈ _)
        rcases y with z | z | ⟨⟩
        · simp only [mycPos] at hy
          simp only [myc_adj_inl_sh] at hxy
          exact mem_filter.mpr ⟨mem_filter.mpr ⟨mem_univ _, by omega, z, by omega, hxy⟩,
            by omega⟩
        · simp at hxy
        · simp only [mycPos] at hy
          have := (σ u).isLt
          omega
      · exact mem_union_right _ (mem_singleton_self _)
    calc (activeSuffix (mycielskian G) (mycLayout σ) (2 * i)).card
        ≤ (((A ∪ B.filter (fun u => (σ u).val = i)).map e₁ ∪
          (B.filter (fun u => ¬ (σ u).val = i)).map e₂) ∪ {Sum.inr (Sum.inr ())}).card :=
          card_le_card hsub
      _ ≤ (A ∪ B.filter (fun u => (σ u).val = i)).card +
          (B.filter (fun u => ¬ (σ u).val = i)).card + 1 := by
          refine (card_union_le _ _).trans ?_
          rw [card_singleton]
          refine Nat.add_le_add_right ((card_union_le _ _).trans ?_) 1
          rw [card_map, card_map]
      _ ≤ A.card + B.card + 1 := by
          have h1 := card_union_le A (B.filter (fun u => (σ u).val = i))
          have h2 := card_filter_add_card_filter_not (s := B)
            (fun u => (σ u).val = i)
          omega
      _ ≤ 2 * vertexSepOfLayout G σ + 1 := by
          omega
  · -- the prefix ends in the original `u_i`
    set A := activeSuffix G σ i
    have hAi : A.card ≤ vertexSepOfLayout G σ := hA i
    have hsub : activeSuffix (mycielskian G) (mycLayout σ) (2 * i + 1) ⊆
        (A.map e₁ ∪ A.map e₂) ∪ {Sum.inr (Sum.inr ())} := by
      intro x hx
      rw [mem_activeSuffix_iff] at hx
      obtain ⟨hx, y, hy, hxy⟩ := hx
      rw [mem_prefixSet_iff, mycLayout_val] at hy
      rw [mycLayout_val] at hx
      rcases x with u | u | ⟨⟩
      · simp only [mycPos] at hx
        apply mem_union_left; apply mem_union_left
        refine mem_map_of_mem e₁ (?_ : u ∈ _)
        rcases y with z | z | ⟨⟩
        · simp only [mycPos] at hy
          simp only [myc_adj_inl_inl] at hxy
          exact (mem_activeSuffix_iff G σ i u).mpr
            ⟨by omega, z, by rw [mem_prefixSet_iff]; omega, hxy⟩
        · simp only [mycPos] at hy
          simp only [myc_adj_sh_inl] at hxy
          exact (mem_activeSuffix_iff G σ i u).mpr
            ⟨by omega, z, by rw [mem_prefixSet_iff]; omega, hxy⟩
        · simp at hxy
      · simp only [mycPos] at hx
        apply mem_union_left; apply mem_union_right
        refine mem_map_of_mem e₂ (?_ : u ∈ _)
        rcases y with z | z | ⟨⟩
        · simp only [mycPos] at hy
          simp only [myc_adj_inl_sh] at hxy
          exact (mem_activeSuffix_iff G σ i u).mpr
            ⟨by omega, z, by rw [mem_prefixSet_iff]; omega, hxy⟩
        · simp at hxy
        · simp only [mycPos] at hy
          have := (σ u).isLt
          omega
      · exact mem_union_right _ (mem_singleton_self _)
    calc (activeSuffix (mycielskian G) (mycLayout σ) (2 * i + 1)).card
        ≤ ((A.map e₁ ∪ A.map e₂) ∪ {Sum.inr (Sum.inr ())}).card := card_le_card hsub
      _ ≤ A.card + A.card + 1 := by
          refine (card_union_le _ _).trans ?_
          rw [card_singleton]
          refine Nat.add_le_add_right ((card_union_le _ _).trans ?_) 1
          rw [card_map, card_map]
      _ ≤ 2 * vertexSepOfLayout G σ + 1 := by
          omega

theorem vertexSepOfLayout_mycLayout_le (σ : LinearLayout V) :
    vertexSepOfLayout (mycielskian G) (mycLayout σ) ≤ 2 * vertexSepOfLayout G σ + 1 := by
  have key := vertexSepAt_mycLayout_le G σ
  generalize 2 * vertexSepOfLayout G σ + 1 = q at key ⊢
  unfold vertexSepOfLayout
  split_ifs
  · exact Nat.zero_le _
  · exact Finset.sup'_le _ _ (fun j _ => key j.val)

end Upper

/-- **`pw(μ(G)) ≤ 2 pw(G) + 1`** for every finite simple graph `G`. We found no
published statement of this bound (`reports/mycielski_pathwidth.md`). The layout
`u'_0, u_0, u'_1, u_1, …, w` built from an optimal layout of `G` witnesses it. -/
theorem pathwidth_mycielskian_le (G : SimpleGraph V) :
    pathwidth (mycielskian G) ≤ 2 * pathwidth G + 1 := by
  classical
  rw [← vertexSeparation_eq_pathwidth (mycielskian G), ← vertexSeparation_eq_pathwidth G]
  obtain ⟨σ, hσ⟩ := Nat.sInf_mem (s := Set.range (fun σ : LinearLayout V =>
    vertexSepOfLayout G σ)) ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  calc vertexSeparation (mycielskian G)
      ≤ vertexSepOfLayout (mycielskian G) (mycLayout σ) :=
        vertexSeparation_le_vertexSepOfLayout _ _
    _ ≤ 2 * vertexSepOfLayout G σ + 1 := vertexSepOfLayout_mycLayout_le G σ
    _ = 2 * vertexSeparation G + 1 := by
        rw [show vertexSepOfLayout G σ = vertexSeparation G from hσ]

/-! ### Lower bound: restricting a decomposition to a connected set -/

/-- Let `β : V → W` be injective, avoid `A ⊆ W`, carry `G`'s edges into common
bags of `P`, and send every vertex into a bag shared with some element of `A`;
and let every element of `A` share a bag with `c ∈ A`. Then `G` has a path
decomposition each of whose bags is smaller than some bag of `P`. -/
theorem exists_decomposition_card_succ_le {W : Type*} [Fintype W] [DecidableEq W]
    {H : SimpleGraph W} (P : PathDecomposition H) {G : SimpleGraph V}
    (β : V → W) (hβ : Function.Injective β) (A : Finset W) {c : W} (hc : c ∈ A)
    (hAc : ∀ a ∈ A, ∃ i, c ∈ P.bag i ∧ a ∈ P.bag i)
    (hdisj : ∀ v, β v ∉ A)
    (hnbr : ∀ v, ∃ a ∈ A, ∃ i, β v ∈ P.bag i ∧ a ∈ P.bag i)
    (hedge : ∀ u v, G.Adj u v → ∃ i, β u ∈ P.bag i ∧ β v ∈ P.bag i) :
    ∃ Q : PathDecomposition G, ∀ j, ∃ i, (Q.bag j).card + 1 ≤ (P.bag i).card := by
  have hne : A.Nonempty := ⟨c, hc⟩
  set l := A.inf' hne P.firstBag with hl_def
  set r := A.sup' hne P.lastBag with hr_def
  have hlr : ∀ a ∈ A, ∀ i, a ∈ P.bag i → l ≤ i ∧ i ≤ r := by
    intro a ha i hi
    rw [P.mem_bag_iff_between] at hi
    exact ⟨(inf'_le _ ha).trans hi.1, hi.2.trans (le_sup' _ ha)⟩
  let cl : Fin (P.length + 1) → Fin (P.length + 1) := fun i =>
    ⟨max l.val (min i.val r.val), by have := l.isLt; have := r.isLt; omega⟩
  have hcl : ∀ i, (cl i).val = max l.val (min i.val r.val) := fun _ => rfl
  have hlr' : l ≤ r := (inf'_le _ hc).trans ((P.firstBag_le_lastBag c).trans (le_sup' _ hc))
  rw [Fin.le_def] at hlr'
  -- a vertex in bag `k` and in a bag of `[l, r]` is in bag `cl k`
  have key : ∀ x k i, x ∈ P.bag k → x ∈ P.bag i → l ≤ i → i ≤ r → x ∈ P.bag (cl k) := by
    intro x k i hk hi hli hir
    rw [Fin.le_def] at hli hir
    by_cases h : k.val ≤ i.val
    · exact P.interval x k (cl k) i (Fin.le_def.mpr (by rw [hcl]; omega))
        (Fin.le_def.mpr (by rw [hcl]; omega)) hk hi
    · exact P.interval x i (cl k) k (Fin.le_def.mpr (by rw [hcl]; omega))
        (Fin.le_def.mpr (by rw [hcl]; omega)) hi hk
  have hcov : ∀ v, ∃ i, l ≤ i ∧ i ≤ r ∧ β v ∈ P.bag i := by
    intro v
    obtain ⟨a, ha, i, hvi, hai⟩ := hnbr v
    exact ⟨i, (hlr a ha i hai).1, (hlr a ha i hai).2, hvi⟩
  -- every bag in `[l, r]` meets `A`
  have hmeet : ∀ j, l ≤ j → j ≤ r → ∃ a ∈ A, a ∈ P.bag j := by
    obtain ⟨a1, ha1, hl1⟩ := exists_mem_eq_inf' hne P.firstBag
    obtain ⟨a2, ha2, hr2⟩ := exists_mem_eq_sup' hne P.lastBag
    obtain ⟨k1, hc1, ha1'⟩ := hAc a1 ha1
    obtain ⟨k2, hc2, ha2'⟩ := hAc a2 ha2
    have hc1' := (P.mem_bag_iff_between c k1).mp hc1
    have hc2' := (P.mem_bag_iff_between c k2).mp hc2
    intro j hlj hjr
    by_cases hcj : c ∈ P.bag j
    · exact ⟨c, hc, hcj⟩
    rw [P.mem_bag_iff_between] at hcj
    by_cases hfj : P.firstBag c ≤ j
    · have hlt : P.lastBag c < j := not_le.mp (fun h => hcj ⟨hfj, h⟩)
      exact ⟨a2, ha2, P.interval a2 k2 j (P.lastBag a2) (hc2'.2.trans hlt.le)
        (hjr.trans (le_of_eq hr2)) ha2' (P.mem_bag_lastBag a2)⟩
    · exact ⟨a1, ha1, P.interval a1 (P.firstBag a1) j k1 ((le_of_eq hl1.symm).trans hlj)
        ((not_le.mp hfj).le.trans hc1'.1) (P.mem_bag_firstBag a1) ha1'⟩
  refine ⟨{
    length := P.length
    bag := fun k => univ.filter (fun v => β v ∈ P.bag (cl k))
    vertex_coverage := ?_
    edge_coverage := ?_
    interval := ?_ }, ?_⟩
  · intro v
    obtain ⟨i, hli, hir, hvi⟩ := hcov v
    exact ⟨i, mem_filter.mpr ⟨mem_univ _, key _ i i hvi hvi hli hir⟩⟩
  · intro u v huv
    obtain ⟨k, hu, hv⟩ := hedge u v huv
    obtain ⟨iu, hliu, hiur, hu'⟩ := hcov u
    obtain ⟨iv, hliv, hivr, hv'⟩ := hcov v
    exact ⟨k, mem_filter.mpr ⟨mem_univ _, key _ k iu hu hu' hliu hiur⟩,
      mem_filter.mpr ⟨mem_univ _, key _ k iv hv hv' hliv hivr⟩⟩
  · intro v i j k hij hjk hi hk
    simp only [mem_filter, mem_univ, true_and] at hi hk ⊢
    rw [Fin.le_def] at hij hjk
    exact P.interval (β v) (cl i) (cl j) (cl k) (Fin.le_def.mpr (by rw [hcl, hcl]; omega))
      (Fin.le_def.mpr (by rw [hcl, hcl]; omega)) hi hk
  · intro k
    refine ⟨cl k, ?_⟩
    obtain ⟨a, ha, hak⟩ := hmeet (cl k) (Fin.le_def.mpr (by rw [hcl]; omega))
      (Fin.le_def.mpr (by rw [hcl]; omega))
    have h1 : (univ.filter (fun v => β v ∈ P.bag (cl k))).card ≤ ((P.bag (cl k)).erase a).card := by
      apply card_le_card_of_injOn β
      · intro v hv
        exact mem_erase.mpr ⟨fun e => hdisj v (e ▸ ha), (mem_filter.mp hv).2⟩
      · exact hβ.injOn
    rw [card_erase_of_mem hak] at h1
    have := card_pos.mpr ⟨a, hak⟩
    show (univ.filter (fun v => β v ∈ P.bag (cl k))).card + 1 ≤ _
    omega

/-- **`pw(G) + 1 ≤ pw(μ(G))`** when `G` has a vertex. Elementary: `G` plus an apex
over all its vertices is a minor of `μ(G)`, with branch set
`{w} ∪ {u' : u not isolated}` for the apex and `{v'}` for an isolated `v`. -/
theorem pathwidth_add_one_le_mycielskian (G : SimpleGraph V) [Nonempty V] :
    pathwidth G + 1 ≤ pathwidth (mycielskian G) := by
  classical
  obtain ⟨P, hP⟩ := exists_pathDecomposition_width_eq (mycielskian G)
  let e₂ : V ↪ V ⊕ V ⊕ Unit := ⟨fun v => Sum.inr (Sum.inl v), fun a b h => by simpa using h⟩
  let apex : V ⊕ V ⊕ Unit := Sum.inr (Sum.inr ())
  let A : Finset (V ⊕ V ⊕ Unit) := (univ.filter (fun u => ∃ v, G.Adj u v)).map e₂ ∪ {apex}
  let β : V → V ⊕ V ⊕ Unit := fun v =>
    if ∃ u, G.Adj v u then Sum.inl v else Sum.inr (Sum.inl v)
  have hβ : Function.Injective β := by
    intro a b h
    by_cases ha : ∃ u, G.Adj a u <;> by_cases hb : ∃ u, G.Adj b u <;>
      simp [β, ha, hb] at h <;> exact h
  have hdisj : ∀ v, β v ∉ A := by
    intro v
    by_cases hv : ∃ u, G.Adj v u
    · simp [β, A, hv, e₂, apex]
    · simp only [β, A, hv, e₂, apex, ite_false, mem_union, mem_map, mem_filter, mem_univ,
        true_and, mem_singleton, Sum.inr.injEq, reduceCtorEq, or_false, not_exists, not_and]
      intro x hx h
      have hxv : x = v := by
        have h' : Sum.inr (Sum.inl x) = (Sum.inr (Sum.inl v) : V ⊕ V ⊕ Unit) := h
        simpa using h'
      exact hv (hxv ▸ hx)
  have hapexA : apex ∈ A := mem_union_right _ (mem_singleton_self _)
  have hAc : ∀ a ∈ A, ∃ i, apex ∈ P.bag i ∧ a ∈ P.bag i := by
    intro a ha
    rcases mem_union.mp ha with ha | ha
    · obtain ⟨u, -, rfl⟩ := mem_map.mp ha
      exact P.edge_coverage apex (e₂ u) (myc_adj_apex_sh G)
    · rw [mem_singleton.mp ha]
      obtain ⟨i, hi⟩ := P.vertex_coverage apex
      exact ⟨i, hi, hi⟩
  have hnbr : ∀ v, ∃ a ∈ A, ∃ i, β v ∈ P.bag i ∧ a ∈ P.bag i := by
    intro v
    by_cases hv : ∃ u, G.Adj v u
    · obtain ⟨u, hu⟩ := hv
      refine ⟨e₂ u, mem_union_left _ (mem_map_of_mem _
        (mem_filter.mpr ⟨mem_univ _, v, hu.symm⟩)), ?_⟩
      have hβv : β v = Sum.inl v := by simp [β, show ∃ u, G.Adj v u from ⟨u, hu⟩]
      rw [hβv]
      exact P.edge_coverage _ _ ((myc_adj_inl_sh G).mpr hu)
    · have hβv : β v = Sum.inr (Sum.inl v) := by simp only [β]; exact ite_eq_right_of_eq_false _ _ (eq_false hv)
      refine ⟨apex, hapexA, ?_⟩
      rw [hβv]
      exact P.edge_coverage _ _ (myc_adj_sh_apex G)
  have hedge : ∀ u v, G.Adj u v → ∃ i, β u ∈ P.bag i ∧ β v ∈ P.bag i := by
    intro u v huv
    have hβu : β u = Sum.inl u := by simp [β, show ∃ x, G.Adj u x from ⟨v, huv⟩]
    have hβv : β v = Sum.inl v := by simp [β, show ∃ x, G.Adj v x from ⟨u, huv.symm⟩]
    rw [hβu, hβv]
    exact P.edge_coverage _ _ ((myc_adj_inl_inl G).mpr huv)
  obtain ⟨Q, hQ⟩ := exists_decomposition_card_succ_le P β hβ A hapexA hAc hdisj hnbr hedge
  have hQw : Q.width ≤ P.width - 1 := by
    apply Q.width_le_of_forall_card_le
    intro j
    obtain ⟨i, hi⟩ := hQ j
    have := P.bag_card_le_width_add_one i
    omega
  have hPw : 1 ≤ P.width := by
    obtain ⟨j, hj⟩ := Q.vertex_coverage (Classical.arbitrary V)
    obtain ⟨i, hi⟩ := hQ j
    have := card_pos.mpr ⟨_, hj⟩
    have := P.bag_card_le_width_add_one i
    omega
  have := pathwidth_le_width G Q
  omega

end MOSPFormalization
