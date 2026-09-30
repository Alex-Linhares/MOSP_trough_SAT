/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Edge separation: what Lengauer (1981) actually proves

Table 1 of Linhares & Yanasse (2002), row "edge separation", source [14]
Lengauer (1981), *Black-white pebbles and graph separation*, Acta Informatica
16, 465–475.

[14] defines no "edge separation" number equivalent to pathwidth. It defines
(p. 467) a **vertex** separator game, VSG, and says (p. 468) that "if we use
edge separators instead of vertex separators in the above definition, we
define a well known problem on undirected graphs, namely, the min-cut linear
arrangement problem" — cutwidth. Its Definition 6 (p. 473) is the *modified*
min-cut linear arrangement problem. This file formalises all three from the
source and proves what holds and what fails.

## The source's definitions

* **VSG** (p. 467, unnumbered): "(i) All vertices start out pebble-free.
  (ii) All vertices end up pebbled. (iii) A move consists of placing a pebble
  on a pebble-free vertex. The vertex cut after the i-th move consists of all
  vertices that are pebble-free and adjacent to a pebbled vertex after the
  i-th move." A strategy `S` is the order of the moves (`VSGStrategy`,
  `pebbledAfter`, `vertexCut`); `VSG(S)` is the largest cut
  (`vsgOfStrategy`); an instance `(G, K)`, `K` a *positive* integer, is
  positive if some `S` has `VSG(S) ≤ K` (`IsPositiveVSG`); `vsg G` is the
  least such `K`.
* **G_du** (p. 472): `V_du = V ∪ {e' | e ∈ E}`,
  `E_du = E ∪ {{v, e'}, {w, e'} | e = {v, w} ∈ E}` — a triangle on every edge
  (`triangleGraph`, on `V ⊕ G.edgeSet`).
* **Min-cut linear arrangement** (p. 468, by reference): the number of edges
  passing *between* consecutive positions (`cutAt`, `cutwidth`).
* **Definition 6, MMCLA** (p. 473): a labelling `λ` with
  `width(v_i) = |{{v_j1, v_j2} ∈ E | λ(v_j1) < i < λ(v_j2)}|`, edges passing
  strictly *over* a position (`modCutAt`, `modCutwidth`).

Edges are counted as ordered pairs `(u, v)` with `u` before `v`, which is one
pair per edge.

## What is proved

* `vsgOfStrategy_eq`: the cut after move `i + 1` is the development's
  `activeSuffix` at `i`, so `VSG(S) = vs` of the layout `S⁻¹` — no reversal is
  needed in this development's convention.
* `vsg_eq_max`: `vsg G = max 1 (vs G)`; so `vsg_eq_pathwidth`:
  **VSG = pw for every graph with an edge**, and `vsg_eq_one_of_edgeless`:
  VSG = 1 on edgeless graphs (the positivity of `K`), where `vs = pw = 0`.
* **Theorem 4** (p. 472): `vertexSeparation_triangleGraph`,
  `vs(G_du) = vs(G) + 1` for every `G` with an edge (hence
  `pathwidth_triangleGraph`), and in Lengauer's form
  `isPositiveVSG_iff_triangleGraph`: `(G, K)` positive ⇔ `(G_du, K + 1)`
  positive, whenever `G` has an edge or `K > 0`. **The exception is real**:
  `isPositiveVSG_triangleGraph_counterexample` — on an edgeless graph
  `(G, 0)` is not an instance at all while `(G_du, 1)` is positive. The upper
  bound is Lengauer's construction (each `e'` pebbled just before the first of
  its endpoints); the lower bound is not his normal-form Lemma 5 but a direct
  induction along the layout `G_du` induces on `V`: at the first position `p`
  where the cut of `G` is big, either an edge vertex `e'` at the vertex just
  pebbled is still unpebbled (one extra vertex on the cut of `G_du`), or all
  are pebbled, and just before that vertex the cut of `G_du` holds it too.
* The cutwidth readings fail. `vertexSeparation_le_cutwidth`: `vs ≤ cw` (so the
  failure is one-sided). `two_mul_cutwidth_starGraph`: `n ≤ 2 cw(K_{1,n})`;
  `two_mul_modCutwidth_starGraph`: `n ≤ 2 mcw(K_{1,n}) + 2`; and
  `pathwidth_starGraph_le_one`. Hence
  `pathwidth_add_two_lt_cutwidth_star7` (`K_{1,7}`: `cw ≥ 4 > pw + 2`, so `cw`
  is not within ±1 of the open-stack value `pw + 1`),
  `pathwidth_add_two_lt_modCutwidth_star9` (`K_{1,9}`, `mcw ≥ 4`), and
  `cutwidth_unbounded`, `modCutwidth_unbounded`: no additive constant relates
  either to pathwidth. The two stars are the instances of item 01; the checker
  (`paper2/complex_check.py`, item 02) gives `cw(K_{1,7}) = mcw(K_{1,9}) = 4`
  exactly.
-/

import MOSPFormalization.Sandwich
import MOSPFormalization.VSEquivPW
import MOSPFormalization.MOSPGraph
import MOSPFormalization.Complex.SplitBandwidth

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace MOSPFormalization

namespace Complex

open Finset Function

section Helpers

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

theorem exists_layout_vertexSeparation :
    ∃ σ : LinearLayout V, vertexSepOfLayout G σ = vertexSeparation G :=
  Nat.sInf_mem (s := Set.range fun σ : LinearLayout V => vertexSepOfLayout G σ)
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩

theorem vertexSepOfLayout_le_iff (σ : LinearLayout V) (b : ℕ) :
    vertexSepOfLayout G σ ≤ b ↔ ∀ i < Fintype.card V, vertexSepAt G σ i ≤ b := by
  constructor
  · intro h i hi
    exact (vertexSepAt_le_vertexSepOfLayout G σ ⟨i, hi⟩).trans h
  · intro h
    unfold vertexSepOfLayout
    split_ifs with hn
    · exact Nat.zero_le _
    · exact Finset.sup'_le _ _ fun i _ => h i.val i.isLt

theorem exists_vertexSepAt_eq (σ : LinearLayout V) (hn : 0 < Fintype.card V) :
    ∃ i < Fintype.card V, vertexSepOfLayout G σ = vertexSepAt G σ i := by
  unfold vertexSepOfLayout
  simp only [dite_eq_right (show Fintype.card V ≠ 0 by omega)]
  obtain ⟨i, -, hi⟩ := Finset.exists_mem_eq_sup' (Finset.univ_nonempty_iff.mpr ⟨⟨0, hn⟩⟩)
    (fun i : Fin (Fintype.card V) => vertexSepAt G σ i.val)
  exact ⟨i.val, i.isLt, hi⟩

theorem one_le_vertexSepOfLayout {u v : V} (huv : G.Adj u v) (σ : LinearLayout V) :
    1 ≤ vertexSepOfLayout G σ := by
  wlog h : σ u < σ v generalizing u v
  · have hne : σ u ≠ σ v := fun h' => huv.ne (σ.injective h')
    exact this huv.symm (lt_of_le_of_ne (not_lt.mp h) (Ne.symm hne))
  refine le_trans ?_ (vertexSepAt_le_vertexSepOfLayout G σ (σ u))
  unfold vertexSepAt
  refine Finset.card_pos.mpr ⟨v, ?_⟩
  rw [mem_activeSuffix_iff]
  exact ⟨h, u, by rw [mem_prefixSet_iff], huv⟩

theorem one_le_vertexSeparation {u v : V} (huv : G.Adj u v) : 1 ≤ vertexSeparation G := by
  obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation G
  rw [← hσ]
  exact one_le_vertexSepOfLayout G huv σ

theorem vertexSeparation_eq_zero_of_edgeless (h : ∀ u v, ¬ G.Adj u v) :
    vertexSeparation G = 0 := by
  refine Nat.eq_zero_of_le_zero ((vertexSeparation_le_vertexSepOfLayout G
    (Fintype.equivFin V)).trans ?_)
  rw [vertexSepOfLayout_le_iff]
  intro i _
  unfold vertexSepAt
  rw [Nat.le_zero, Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
  intro v hv
  rw [mem_activeSuffix_iff] at hv
  obtain ⟨-, u, -, huv⟩ := hv
  exact h u v huv

end Helpers

/-! ### Lengauer's vertex separator game -/

section VSG

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- A strategy for VSG: move `j` (counting from `0`) places a pebble on `S j`. Every
vertex is pebbled exactly once (rules (ii), (iii)). -/
abbrev VSGStrategy (V : Type*) [Fintype V] := Fin (Fintype.card V) ≃ V

/-- The pebbled vertices after the first `i` moves. -/
def pebbledAfter (S : VSGStrategy V) (i : ℕ) : Finset V :=
  Finset.univ.filter fun v => (S.symm v).val < i

/-- Lengauer p. 467: "The vertex cut after the i-th move consists of all vertices that
are pebble-free and adjacent to a pebbled vertex after the i-th move." -/
def vertexCut (S : VSGStrategy V) (i : ℕ) : Finset V :=
  Finset.univ.filter fun v => v ∉ pebbledAfter S i ∧ ∃ u ∈ pebbledAfter S i, G.Adj u v

/-- `VSG(S)`: the largest vertex cut over the course of the strategy (moves `0..n`). -/
def vsgOfStrategy (S : VSGStrategy V) : ℕ :=
  (Finset.range (Fintype.card V + 1)).sup fun i => (vertexCut G S i).card

/-- Lengauer p. 467: `(G, K)` is positive "if VSG(S) ≤ K" for some strategy, `K` a
positive integer. -/
def IsPositiveVSG (K : ℕ) : Prop :=
  0 < K ∧ ∃ S : VSGStrategy V, vsgOfStrategy G S ≤ K

/-- `VSG(G)`: the least `K` for which `(G, K)` is positive. -/
noncomputable def vsg : ℕ := sInf {K | IsPositiveVSG G K}

theorem vertexCut_zero (S : VSGStrategy V) : vertexCut G S 0 = ∅ := by
  ext v; simp [vertexCut, pebbledAfter]

/-- The cut after move `i + 1` is the active suffix at position `i` of the layout `S⁻¹`. -/
theorem vertexCut_succ (S : VSGStrategy V) (i : ℕ) :
    vertexCut G S (i + 1) = activeSuffix G S.symm i := by
  ext v
  simp only [vertexCut, pebbledAfter, Finset.mem_filter, Finset.mem_univ, true_and,
    mem_activeSuffix_iff, mem_prefixSet_iff, Nat.lt_succ_iff, not_le]

theorem vsgOfStrategy_eq (S : VSGStrategy V) :
    vsgOfStrategy G S = vertexSepOfLayout G S.symm := by
  apply le_antisymm
  · refine Finset.sup_le fun i hi => ?_
    rcases i with _ | i
    · simp [vertexCut_zero]
    · rw [vertexCut_succ]
      have : i < Fintype.card V := by simp at hi; omega
      exact vertexSepAt_le_vertexSepOfLayout G S.symm ⟨i, this⟩
  · rw [vertexSepOfLayout_le_iff]
    intro i hi
    unfold vertexSepAt
    rw [← vertexCut_succ]
    exact Finset.le_sup (f := fun i => (vertexCut G S i).card)
      (Finset.mem_range.mpr (by omega))

theorem isPositiveVSG_iff (K : ℕ) :
    IsPositiveVSG G K ↔ 0 < K ∧ vertexSeparation G ≤ K := by
  constructor
  · rintro ⟨hK, S, hS⟩
    refine ⟨hK, (vertexSeparation_le_vertexSepOfLayout G S.symm).trans ?_⟩
    rwa [← vsgOfStrategy_eq]
  · rintro ⟨hK, h⟩
    obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation G
    refine ⟨hK, σ.symm, ?_⟩
    rw [vsgOfStrategy_eq, Equiv.symm_symm, hσ]
    exact h

/-- `VSG(G) = max(1, vs(G))`. -/
theorem vsg_eq_max : vsg G = max 1 (vertexSeparation G) := by
  unfold vsg
  apply le_antisymm
  · apply Nat.sInf_le
    show IsPositiveVSG G _
    rw [isPositiveVSG_iff]
    omega
  · apply le_csInf ⟨max 1 (vertexSeparation G), by
      show IsPositiveVSG G _
      rw [isPositiveVSG_iff]; omega⟩
    intro K hK
    have := (isPositiveVSG_iff G K).mp hK
    omega

/-- **VSG = vs** for every graph with an edge. -/
theorem vsg_eq_vertexSeparation {u v : V} (huv : G.Adj u v) :
    vsg G = vertexSeparation G := by
  have := one_le_vertexSeparation G huv
  rw [vsg_eq_max]; omega

/-- **VSG = pw** for every graph with an edge (with Kinnersley's theorem). -/
theorem vsg_eq_pathwidth {u v : V} (huv : G.Adj u v) : vsg G = pathwidth G := by
  rw [vsg_eq_vertexSeparation G huv, vertexSeparation_eq_pathwidth]

/-- On an edgeless graph VSG is `1`, by the positivity of `K`, while `vs = pw = 0`. -/
theorem vsg_eq_one_of_edgeless (h : ∀ u v, ¬ G.Adj u v) : vsg G = 1 := by
  rw [vsg_eq_max, vertexSeparation_eq_zero_of_edgeless G h]; rfl

end VSG

/-! ### Theorem 4: a triangle on every edge adds exactly one -/

section Triangle

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Lengauer's `G_du` (p. 472): a new vertex `e'` for each edge `e = {v, w}`, adjacent to
`v` and `w`. -/
def triangleGraph : SimpleGraph (V ⊕ G.edgeSet) where
  Adj a b := match a, b with
    | .inl u, .inl v => G.Adj u v
    | .inl v, .inr e => v ∈ (e : Sym2 V)
    | .inr e, .inl v => v ∈ (e : Sym2 V)
    | .inr _, .inr _ => False
  symm := ⟨by
    intro a b h
    rcases a with u | e <;> rcases b with v | f
    · exact G.symm.symm _ _ h
    · exact h
    · exact h
    · exact h⟩
  loopless := ⟨by
    intro a h
    rcases a with u | e
    · exact G.loopless.irrefl u h
    · exact h⟩

instance : DecidableRel (triangleGraph G).Adj := fun a b =>
  match a, b with
  | .inl u, .inl v => inferInstanceAs (Decidable (G.Adj u v))
  | .inl v, .inr e => inferInstanceAs (Decidable (v ∈ (e : Sym2 V)))
  | .inr e, .inl v => inferInstanceAs (Decidable (v ∈ (e : Sym2 V)))
  | .inr _, .inr _ => inferInstanceAs (Decidable False)

variable {G}

@[simp] theorem triangleGraph_adj_inl_inl {u v : V} :
    (triangleGraph G).Adj (.inl u) (.inl v) ↔ G.Adj u v := Iff.rfl

@[simp] theorem triangleGraph_adj_inl_inr {v : V} {e : G.edgeSet} :
    (triangleGraph G).Adj (.inl v) (.inr e) ↔ v ∈ (e : Sym2 V) := Iff.rfl

@[simp] theorem triangleGraph_adj_inr_inl {v : V} {e : G.edgeSet} :
    (triangleGraph G).Adj (.inr e) (.inl v) ↔ v ∈ (e : Sym2 V) := Iff.rfl

@[simp] theorem triangleGraph_adj_inr_inr {e f : G.edgeSet} :
    ¬ (triangleGraph G).Adj (.inr e) (.inr f) := id

variable (G)

theorem triangleGraph_edgeless (h : ∀ u v, ¬ G.Adj u v) :
    ∀ a b, ¬ (triangleGraph G).Adj a b := by
  have hE : IsEmpty G.edgeSet := ⟨fun ⟨e, he⟩ => by
    induction e using Sym2.ind with
    | h a b => exact h a b he⟩
  rintro (u | e) (v | f)
  · exact h u v
  · exact fun _ => hE.false f
  · exact fun _ => hE.false e
  · exact fun _ => hE.false e

/-- The lower half of Theorem 4, for one layout `τ` of `G_du`. -/
theorem vertexSeparation_add_one_le_of_layout {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀)
    (τ : LinearLayout (V ⊕ G.edgeSet)) :
    vertexSeparation G + 1 ≤ vertexSepOfLayout (triangleGraph G) τ := by
  set W := vertexSepOfLayout (triangleGraph G) τ with hW
  obtain ⟨σ, hσ⟩ := exists_layout_sorted (fun v : V => τ (Sum.inl v))
  have hlt : ∀ a b : V, (σ a).val < (σ b).val ↔ τ (.inl a) < τ (.inl b) := by
    intro a b
    refine ⟨fun h => ?_, hσ a b⟩
    rcases lt_trichotomy (τ (.inl a)) (τ (.inl b)) with h' | h' | h'
    · exact h'
    · have := Sum.inl_injective (τ.injective h'); subst this; omega
    · have := hσ b a h'; omega
  have hle : ∀ a b : V, (σ a).val ≤ (σ b).val ↔ τ (.inl a) ≤ τ (.inl b) := by
    intro a b
    rw [← not_lt, ← not_lt, hlt]
  have hcut : ∀ i < Fintype.card (V ⊕ G.edgeSet),
      (activeSuffix (triangleGraph G) τ i).card ≤ W := fun i hi =>
    vertexSepAt_le_vertexSepOfLayout _ τ ⟨i, hi⟩
  have hlt' : ∀ a b : V, (σ a).val < (σ b).val ↔ (τ (.inl a)).val < (τ (.inl b)).val :=
    fun a b => (hlt a b).trans Fin.lt_def
  have hle' : ∀ a b : V, (σ a).val ≤ (σ b).val ↔ (τ (.inl a)).val ≤ (τ (.inl b)).val :=
    fun a b => (hle a b).trans Fin.le_def
  have hne : ∀ a b : V, a ≠ b → (σ a).val ≠ (σ b).val :=
    fun a b hab h => hab (σ.injective (Fin.ext h))
  have hτne : ∀ (a : V) (e : G.edgeSet), (τ (.inl a)).val ≠ (τ (.inr e)).val :=
    fun a e h => Sum.inl_ne_inr (τ.injective (Fin.ext h))
  -- one step: the vertex `x` at position `p`
  have step : ∀ p (hp : p < Fintype.card V),
      (∃ a ∈ activeSuffix G σ p, G.Adj (σ.symm ⟨p, hp⟩) a) →
        (activeSuffix G σ p).card + 1 ≤ W := by
    intro p hp ⟨a, ha, hxa⟩
    set x := σ.symm ⟨p, hp⟩ with hx
    have hσx : (σ x).val = p := by simp [hx]
    have hxA : x ∉ activeSuffix G σ p := by
      rw [mem_activeSuffix_iff]; omega
    let z : ∀ b, G.Adj x b → G.edgeSet := fun b hxb => ⟨s(x, b), hxb⟩
    have hA : ∀ c ∈ activeSuffix G σ p, (τ (.inl x)).val < (τ (.inl c)).val ∧
        ∃ u, G.Adj u c ∧ (σ u).val ≤ p := by
      intro c hc
      rw [mem_activeSuffix_iff] at hc
      obtain ⟨hc, u, hu, huc⟩ := hc
      rw [mem_prefixSet_iff] at hu
      exact ⟨(hlt' x c).mp (by omega), u, huc, hu⟩
    have hcard : ((activeSuffix G σ p).image Sum.inl :
        Finset (V ⊕ G.edgeSet)).card = (activeSuffix G σ p).card :=
      Finset.card_image_of_injective _ Sum.inl_injective
    by_cases h1 : ∃ b ∈ activeSuffix G σ p, ∃ hxb : G.Adj x b,
        (τ (.inl x)).val < (τ (.inr (z b hxb))).val
    · -- an edge vertex at `x` is still unpebbled just after `x`
      obtain ⟨b, -, hxb, hb⟩ := h1
      set i := (τ (.inl x)).val
      have hsub : insert (Sum.inr (z b hxb)) ((activeSuffix G σ p).image Sum.inl) ⊆
          activeSuffix (triangleGraph G) τ i := by
        intro y hy
        rw [mem_activeSuffix_iff]
        rcases Finset.mem_insert.mp hy with rfl | hy
        · exact ⟨hb, .inl x, by rw [mem_prefixSet_iff], Sym2.mem_mk_left _ _⟩
        · obtain ⟨c, hc, rfl⟩ := Finset.mem_image.mp hy
          obtain ⟨hc1, u, huc, hu⟩ := hA c hc
          refine ⟨hc1, .inl u, ?_, huc⟩
          rw [mem_prefixSet_iff]
          exact (hle' u x).mp (by omega)
      have := Finset.card_le_card hsub
      rw [Finset.card_insert_of_notMem (by simp), hcard] at this
      exact this.trans (hcut i (τ (.inl x)).isLt)
    · -- all edge vertices at `x` are pebbled before `x`
      push Not at h1
      have h1' : ∀ b ∈ activeSuffix G σ p, ∀ hxb : G.Adj x b,
          (τ (.inr (z b hxb))).val < (τ (.inl x)).val := fun b hb hxb =>
        lt_of_le_of_ne (h1 b hb hxb) (Ne.symm (hτne _ _))
      have hpos := h1' a ha hxa
      set i := (τ (.inl x)).val - 1
      have hsub : insert (Sum.inl x) ((activeSuffix G σ p).image Sum.inl) ⊆
          activeSuffix (triangleGraph G) τ i := by
        intro y hy
        rw [mem_activeSuffix_iff]
        rcases Finset.mem_insert.mp hy with rfl | hy
        · refine ⟨by omega, .inr (z a hxa), ?_, Sym2.mem_mk_left _ _⟩
          rw [mem_prefixSet_iff]; omega
        · obtain ⟨c, hc, rfl⟩ := Finset.mem_image.mp hy
          obtain ⟨hc1, u, huc, hu⟩ := hA c hc
          refine ⟨by omega, ?_⟩
          by_cases hux : u = x
          · subst hux
            refine ⟨.inr (z c huc), ?_, Sym2.mem_mk_right _ _⟩
            rw [mem_prefixSet_iff]
            have := h1' c hc huc; omega
          · refine ⟨.inl u, ?_, huc⟩
            rw [mem_prefixSet_iff]
            have := (hlt' u x).mp (by have := hne u x hux; omega)
            omega
      have := Finset.card_le_card hsub
      rw [Finset.card_insert_of_notMem (by simpa using hxA), hcard] at this
      exact this.trans (hcut i (by have := (τ (.inl x)).isLt; omega))
  -- otherwise the cut at `p` is already a cut at `p - 1`
  have back : ∀ p (hp : p < Fintype.card V),
      (∀ a ∈ activeSuffix G σ p, ¬ G.Adj (σ.symm ⟨p, hp⟩) a) →
        ∀ c ∈ activeSuffix G σ p, (σ c).val > p ∧ ∃ u, G.Adj u c ∧ (σ u).val < p := by
    intro p hp h c hc
    have hc' := hc
    rw [mem_activeSuffix_iff] at hc'
    obtain ⟨hc1, u, hu, huc⟩ := hc'
    rw [mem_prefixSet_iff] at hu
    refine ⟨hc1, u, huc, lt_of_le_of_ne hu fun hup => h c hc ?_⟩
    have : u = σ.symm ⟨p, hp⟩ := by
      rw [Equiv.eq_symm_apply]; exact Fin.ext hup
    rwa [← this]
  have claim : ∀ p, (activeSuffix G σ p).card = 0 ∨ (activeSuffix G σ p).card + 1 ≤ W := by
    intro p
    induction p with
    | zero =>
      by_cases hp : 0 < Fintype.card V
      · by_cases h : ∃ a ∈ activeSuffix G σ 0, G.Adj (σ.symm ⟨0, hp⟩) a
        · exact Or.inr (step 0 hp h)
        · push Not at h
          left
          rw [Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
          intro c hc
          obtain ⟨-, u, -, hu⟩ := back 0 hp h c hc
          omega
      · left
        rw [Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
        intro c hc
        rw [mem_activeSuffix_iff] at hc
        have := (σ c).isLt; omega
    | succ q ih =>
      by_cases hp : q + 1 < Fintype.card V
      · by_cases h : ∃ a ∈ activeSuffix G σ (q + 1), G.Adj (σ.symm ⟨q + 1, hp⟩) a
        · exact Or.inr (step _ hp h)
        · push Not at h
          have hsub : activeSuffix G σ (q + 1) ⊆ activeSuffix G σ q := by
            intro c hc
            obtain ⟨hc1, u, huc, hu⟩ := back _ hp h c hc
            rw [mem_activeSuffix_iff]
            exact ⟨by omega, u, by rw [mem_prefixSet_iff]; omega, huc⟩
          have := Finset.card_le_card hsub
          omega
      · left
        rw [Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
        intro c hc
        rw [mem_activeSuffix_iff] at hc
        have := (σ c).isLt; omega
  have hn : 0 < Fintype.card V := Fintype.card_pos_iff.mpr ⟨u₀⟩
  obtain ⟨j, -, hj⟩ := exists_vertexSepAt_eq G σ hn
  have h1 := one_le_vertexSepOfLayout G h₀ σ
  have hvs := vertexSeparation_le_vertexSepOfLayout G σ
  rcases claim j with h | h
  · unfold vertexSepAt at hj; omega
  · unfold vertexSepAt at hj; omega

theorem vertexSeparation_add_one_le_triangleGraph {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    vertexSeparation G + 1 ≤ vertexSeparation (triangleGraph G) := by
  obtain ⟨τ, hτ⟩ := exists_layout_vertexSeparation (triangleGraph G)
  rw [← hτ]
  exact vertexSeparation_add_one_le_of_layout G h₀ τ

/-- The upper half of Theorem 4, by Lengauer's construction: take an optimal layout `σ`
of `G` and pebble each `e'` just before the first of its two endpoints. -/
theorem vertexSeparation_triangleGraph_le (hn : 0 < Fintype.card V) :
    vertexSeparation (triangleGraph G) ≤ vertexSeparation G + 1 := by
  obtain ⟨σ, hσ⟩ := exists_layout_vertexSeparation G
  set n := Fintype.card V
  have hends : ∀ e : G.edgeSet, ∃ a b : V, (e : Sym2 V) = s(a, b) ∧
      (σ a).val < (σ b).val ∧ G.Adj a b := by
    rintro ⟨e, he⟩
    induction e using Sym2.ind with
    | h a b =>
      have hab : (σ a).val ≠ (σ b).val := fun h => G.ne_of_adj he (σ.injective (Fin.ext h))
      rcases Nat.lt_or_gt_of_ne hab with h | h
      · exact ⟨a, b, rfl, h, he⟩
      · exact ⟨b, a, Sym2.eq_swap, h, G.symm.symm _ _ he⟩
  choose lo up hlohi hlohi_lt hlohi_adj using hends
  have hmem : ∀ (e : G.edgeSet) (v : V), v ∈ (e : Sym2 V) ↔ v = lo e ∨ v = up e := by
    intro e v; rw [hlohi e, Sym2.mem_iff]
  have hne : ∀ a b : V, a ≠ b → (σ a).val ≠ (σ b).val :=
    fun a b hab h => hab (σ.injective (Fin.ext h))
  let kA : V ⊕ G.edgeSet → ℕ
    | .inl v => 2 * (σ v).val + 1
    | .inr e => 2 * (σ (lo e)).val
  let kB : V ⊕ G.edgeSet → ℕ
    | .inl _ => 0
    | .inr e => (σ (up e)).val
  have hkA1 : ∀ v, kA (.inl v) = 2 * (σ v).val + 1 := fun _ => rfl
  have hkA2 : ∀ e, kA (.inr e) = 2 * (σ (lo e)).val := fun _ => rfl
  have hkB1 : ∀ v, kB (.inl v) = 0 := fun _ => rfl
  have hkB2 : ∀ e, kB (.inr e) = (σ (up e)).val := fun _ => rfl
  have hkB : ∀ y, kB y < n := by
    rintro (v | e)
    · exact hn
    · exact (σ (up e)).isLt
  let key : V ⊕ G.edgeSet → ℕ := fun y => kA y * n + kB y
  have hkey_lt : ∀ y z, key y < key z ↔ kA y < kA z ∨ (kA y = kA z ∧ kB y < kB z) :=
    fun y z => key_lt_iff (hkB y) (hkB z)
  have hkey : Injective key := by
    intro y z h
    have h' := (key_eq_iff (hkB y) (hkB z)).mp h
    rcases y with v | e <;> rcases z with w | f
    · simp only [kA] at h'
      exact congrArg Sum.inl (σ.injective (Fin.ext (by omega)))
    · simp only [kA] at h'; omega
    · simp only [kA] at h'; omega
    · simp only [kA, kB] at h'
      have h1 : lo e = lo f := σ.injective (Fin.ext (by omega))
      have h2 : up e = up f := σ.injective (Fin.ext h'.2)
      exact congrArg Sum.inr (Subtype.ext (by rw [hlohi e, hlohi f, h1, h2]))
  obtain ⟨τ, hτ⟩ := exists_layout_sorted key
  have hτlt : ∀ y z, (τ y).val < (τ z).val ↔ key y < key z := by
    intro y z
    refine ⟨fun h => ?_, hτ y z⟩
    rcases lt_trichotomy (key y) (key z) with h' | h' | h'
    · exact h'
    · have := hkey h'; subst this; omega
    · have := hτ z y h'; omega
  refine (vertexSeparation_le_vertexSepOfLayout _ τ).trans ?_
  rw [vertexSepOfLayout_le_iff]
  intro i hi
  set z₀ := τ.symm ⟨i, hi⟩
  have hz₀ : (τ z₀).val = i := by simp [z₀]
  -- membership in the cut, in terms of the key of the last pebbled vertex `z₀`
  have hact : ∀ y, y ∈ activeSuffix (triangleGraph G) τ i →
      key z₀ < key y ∧ ∃ w, ¬ key z₀ < key w ∧ (triangleGraph G).Adj w y := by
    intro y hy
    rw [mem_activeSuffix_iff] at hy
    obtain ⟨hy, w, hw, hwy⟩ := hy
    rw [mem_prefixSet_iff] at hw
    exact ⟨(hτlt z₀ y).mp (by omega), w, fun h => by have := (hτlt z₀ w).mpr h; omega, hwy⟩
  have hvs : ∀ p < n, (activeSuffix G σ p).card ≤ vertexSeparation G := fun p hp =>
    hσ ▸ vertexSepAt_le_vertexSepOfLayout G σ ⟨p, hp⟩
  have hcard : ∀ p, ((activeSuffix G σ p).image Sum.inl :
      Finset (V ⊕ G.edgeSet)).card = (activeSuffix G σ p).card := fun p =>
    Finset.card_image_of_injective _ Sum.inl_injective
  unfold vertexSepAt
  rcases hz : z₀ with x | e₀
  · -- the last move pebbled an original vertex `x`: the cut is the cut of `G`
    have hsub : activeSuffix (triangleGraph G) τ i ⊆
        (activeSuffix G σ (σ x).val).image Sum.inl := by
      intro y hy
      obtain ⟨hy1, w, hw1, hwy⟩ := hact y hy
      rw [hz] at hy1 hw1
      replace hy1 := (hkey_lt (Sum.inl x) y).mp hy1
      replace hw1 : ¬ (kA (Sum.inl x) < kA w ∨ (kA (Sum.inl x) = kA w ∧ kB (Sum.inl x) < kB w)) :=
        fun h => hw1 ((hkey_lt (Sum.inl x) w).mpr h)
      simp only [hkA1, hkA2, hkB1, hkB2] at hy1 hw1
      rcases y with v | e
      · refine Finset.mem_image.mpr ⟨v, ?_, rfl⟩
        simp only [hkA1, hkA2, hkB1, hkB2] at hy1
        rw [mem_activeSuffix_iff]
        refine ⟨by omega, ?_⟩
        rcases w with u | e
        · simp only [hkA1, hkA2, hkB1, hkB2] at hw1
          exact ⟨u, by rw [mem_prefixSet_iff]; omega, hwy⟩
        · simp only [hkA1, hkA2, hkB1, hkB2] at hw1
          rw [triangleGraph_adj_inr_inl, hmem] at hwy
          rcases hwy with rfl | rfl
          · omega
          · exact ⟨lo e, by rw [mem_prefixSet_iff]; omega, hlohi_adj e⟩
      · simp only [hkA1, hkA2, hkB1, hkB2] at hy1
        rcases w with u | f
        · simp only [hkA1, hkA2, hkB1, hkB2] at hw1
          rw [triangleGraph_adj_inl_inr, hmem] at hwy
          have := hlohi_lt e
          rcases hwy with rfl | rfl <;> omega
        · exact absurd hwy triangleGraph_adj_inr_inr
    refine (Finset.card_le_card hsub).trans ?_
    rw [hcard]
    exact (hvs _ (σ x).isLt).trans (Nat.le_succ _)
  · -- the last move pebbled an edge vertex `e₀`: at most its first endpoint is added
    have hsub : activeSuffix (triangleGraph G) τ i ⊆
        insert (Sum.inl (lo e₀)) ((activeSuffix G σ (σ (lo e₀)).val).image Sum.inl) := by
      intro y hy
      obtain ⟨hy1, w, hw1, hwy⟩ := hact y hy
      rw [hz] at hy1 hw1
      replace hy1 := (hkey_lt (Sum.inr e₀) y).mp hy1
      replace hw1 : ¬ (kA (Sum.inr e₀) < kA w ∨ (kA (Sum.inr e₀) = kA w ∧ kB (Sum.inr e₀) < kB w)) :=
        fun h => hw1 ((hkey_lt (Sum.inr e₀) w).mpr h)
      simp only [hkA1, hkA2, hkB1, hkB2] at hy1 hw1
      have hlt₀ := hlohi_lt e₀
      rcases y with v | e
      · simp only [hkA1, hkA2, hkB1, hkB2] at hy1
        by_cases hvm : v = lo e₀
        · subst hvm; exact Finset.mem_insert_self _ _
        refine Finset.mem_insert_of_mem (Finset.mem_image.mpr ⟨v, ?_, rfl⟩)
        have := hne v (lo e₀) hvm
        rw [mem_activeSuffix_iff]
        refine ⟨by omega, ?_⟩
        rcases w with u | e
        · simp only [hkA1, hkA2, hkB1, hkB2] at hw1
          exact ⟨u, by rw [mem_prefixSet_iff]; omega, hwy⟩
        · simp only [hkA1, hkA2, hkB1, hkB2] at hw1
          rw [triangleGraph_adj_inr_inl, hmem] at hwy
          rcases hwy with rfl | rfl
          · omega
          · exact ⟨lo e, by rw [mem_prefixSet_iff]; omega, hlohi_adj e⟩
      · simp only [hkA1, hkA2, hkB1, hkB2] at hy1
        rcases w with u | f
        · simp only [hkA1, hkA2, hkB1, hkB2] at hw1
          rw [triangleGraph_adj_inl_inr, hmem] at hwy
          have := hlohi_lt e
          rcases hwy with rfl | rfl <;> omega
        · exact absurd hwy triangleGraph_adj_inr_inr
    refine (Finset.card_le_card hsub).trans ((Finset.card_insert_le _ _).trans ?_)
    rw [hcard]
    exact Nat.succ_le_succ (hvs _ (σ (lo e₀)).isLt)

/-- **Lengauer, Theorem 4**, as an equation: a triangle on every edge raises the vertex
separation by exactly one, for every graph with an edge. -/
theorem vertexSeparation_triangleGraph {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    vertexSeparation (triangleGraph G) = vertexSeparation G + 1 :=
  le_antisymm (vertexSeparation_triangleGraph_le G (Fintype.card_pos_iff.mpr ⟨u₀⟩))
    (vertexSeparation_add_one_le_triangleGraph G h₀)

theorem pathwidth_triangleGraph {u₀ v₀ : V} (h₀ : G.Adj u₀ v₀) :
    pathwidth (triangleGraph G) = pathwidth G + 1 := by
  rw [← vertexSeparation_eq_pathwidth, ← vertexSeparation_eq_pathwidth,
    vertexSeparation_triangleGraph G h₀]

/-- **Lengauer, Theorem 4**, in his form: `(G, K)` is positive for VSG iff `(G_du, K + 1)`
is, whenever `G` has an edge or `K > 0`. -/
theorem isPositiveVSG_iff_triangleGraph (K : ℕ) (h : (∃ u v, G.Adj u v) ∨ 0 < K) :
    IsPositiveVSG G K ↔ IsPositiveVSG (triangleGraph G) (K + 1) := by
  rw [isPositiveVSG_iff, isPositiveVSG_iff]
  by_cases hE : ∃ u v, G.Adj u v
  · obtain ⟨u, v, huv⟩ := hE
    rw [vertexSeparation_triangleGraph G huv]
    have := one_le_vertexSeparation G huv
    omega
  · push Not at hE
    rw [vertexSeparation_eq_zero_of_edgeless G hE,
      vertexSeparation_eq_zero_of_edgeless _ (triangleGraph_edgeless G hE)]
    rcases h with ⟨u, v, huv⟩ | h
    · exact absurd huv (hE u v)
    · omega

/-- The exception in Theorem 4 is real: on an edgeless graph `(G, 0)` is not positive
(`K` must be positive) but `(G_du, 1)` is. -/
theorem isPositiveVSG_triangleGraph_counterexample (h : ∀ u v, ¬ G.Adj u v) :
    ¬ IsPositiveVSG G 0 ∧ IsPositiveVSG (triangleGraph G) 1 := by
  rw [isPositiveVSG_iff, isPositiveVSG_iff,
    vertexSeparation_eq_zero_of_edgeless _ (triangleGraph_edgeless G h)]
  omega

end Triangle

/-! ### Min-cut linear arrangement and its modified form -/

section Cutwidth

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Edges passing between positions `i` and `i + 1` (an ordered pair per edge, earlier end
first). -/
def cutAt (σ : LinearLayout V) (i : ℕ) : ℕ :=
  (Finset.univ.filter fun p : V × V =>
    G.Adj p.1 p.2 ∧ (σ p.1).val ≤ i ∧ i < (σ p.2).val).card

/-- Lengauer Def. 6: edges passing strictly over the vertex at position `i`. -/
def modCutAt (σ : LinearLayout V) (i : ℕ) : ℕ :=
  (Finset.univ.filter fun p : V × V =>
    G.Adj p.1 p.2 ∧ (σ p.1).val < i ∧ i < (σ p.2).val).card

noncomputable def cutwidthOfLayout (σ : LinearLayout V) : ℕ :=
  Finset.univ.sup fun i : Fin (Fintype.card V) => cutAt G σ i

noncomputable def modCutwidthOfLayout (σ : LinearLayout V) : ℕ :=
  Finset.univ.sup fun i : Fin (Fintype.card V) => modCutAt G σ i

/-- Cutwidth: the min-cut linear arrangement problem (Lengauer p. 468). -/
noncomputable def cutwidth : ℕ :=
  sInf (Set.range fun σ : LinearLayout V => cutwidthOfLayout G σ)

/-- Modified cutwidth: the MMCLA of Lengauer Def. 6. -/
noncomputable def modCutwidth : ℕ :=
  sInf (Set.range fun σ : LinearLayout V => modCutwidthOfLayout G σ)

theorem exists_layout_cutwidth : ∃ σ : LinearLayout V, cutwidthOfLayout G σ = cutwidth G :=
  Nat.sInf_mem (s := Set.range fun σ : LinearLayout V => cutwidthOfLayout G σ)
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩

theorem exists_layout_modCutwidth :
    ∃ σ : LinearLayout V, modCutwidthOfLayout G σ = modCutwidth G :=
  Nat.sInf_mem (s := Set.range fun σ : LinearLayout V => modCutwidthOfLayout G σ)
    ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩

theorem cutAt_le_cutwidthOfLayout (σ : LinearLayout V) {i : ℕ} (hi : i < Fintype.card V) :
    cutAt G σ i ≤ cutwidthOfLayout G σ :=
  Finset.le_sup (f := fun i : Fin (Fintype.card V) => cutAt G σ i) (Finset.mem_univ ⟨i, hi⟩)

theorem modCutAt_le_modCutwidthOfLayout (σ : LinearLayout V) {i : ℕ}
    (hi : i < Fintype.card V) : modCutAt G σ i ≤ modCutwidthOfLayout G σ :=
  Finset.le_sup (f := fun i : Fin (Fintype.card V) => modCutAt G σ i) (Finset.mem_univ ⟨i, hi⟩)

/-- Each vertex of the active suffix at `i` is the later end of an edge across the gap. -/
theorem vertexSepAt_le_cutAt (σ : LinearLayout V) (i : ℕ) :
    vertexSepAt G σ i ≤ cutAt G σ i := by
  unfold vertexSepAt cutAt
  refine le_trans (Finset.card_le_card ?_) (Finset.card_image_le (f := Prod.snd))
  intro v hv
  rw [mem_activeSuffix_iff] at hv
  obtain ⟨hv, u, hu, huv⟩ := hv
  rw [mem_prefixSet_iff] at hu
  exact Finset.mem_image.mpr ⟨(u, v), by simp [huv, hu, hv], rfl⟩

/-- `vs ≤ cw`: cutwidth fails to be `pw ± 1` only from above. -/
theorem vertexSeparation_le_cutwidth : vertexSeparation G ≤ cutwidth G := by
  obtain ⟨σ, hσ⟩ := exists_layout_cutwidth G
  rw [← hσ]
  refine (vertexSeparation_le_vertexSepOfLayout G σ).trans ?_
  rw [vertexSepOfLayout_le_iff]
  intro i hi
  exact (vertexSepAt_le_cutAt G σ i).trans (cutAt_le_cutwidthOfLayout G σ hi)

theorem pathwidth_le_cutwidth : pathwidth G ≤ cutwidth G :=
  vertexSeparation_eq_pathwidth G ▸ vertexSeparation_le_cutwidth G

end Cutwidth

/-! ### Stars -/

section Star

/-- The star `K_{1,n}` on `Fin (n + 1)`, centre `0`. -/
def starGraph (n : ℕ) : SimpleGraph (Fin (n + 1)) where
  Adj a b := a ≠ b ∧ (a = 0 ∨ b = 0)
  symm := ⟨fun _ _ h => ⟨h.1.symm, h.2.symm⟩⟩
  loopless := ⟨fun _ h => h.1 rfl⟩

instance (n : ℕ) : DecidableRel (starGraph n).Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ (a = 0 ∨ b = 0)))

theorem starGraph_adj {n : ℕ} {a b : Fin (n + 1)} :
    (starGraph n).Adj a b ↔ a ≠ b ∧ (a = 0 ∨ b = 0) := Iff.rfl

/-- `pw(K_{1,n}) ≤ 1`: pebble the centre last. -/
theorem pathwidth_starGraph_le_one (n : ℕ) : pathwidth (starGraph n) ≤ 1 := by
  rw [← vertexSeparation_eq_pathwidth]
  let σ : LinearLayout (Fin (n + 1)) := Fin.revPerm.trans (finCongr (Fintype.card_fin _).symm)
  have hσ : ∀ v, (σ v).val = n - v.val := by
    intro v; simp [σ, Fin.val_rev]
  refine (vertexSeparation_le_vertexSepOfLayout _ σ).trans ?_
  rw [vertexSepOfLayout_le_iff]
  intro i _
  unfold vertexSepAt
  refine (Finset.card_le_card (t := {0}) ?_).trans (by simp)
  intro v hv
  rw [mem_activeSuffix_iff] at hv
  obtain ⟨hv, u, hu, huv⟩ := hv
  rw [mem_prefixSet_iff] at hu
  rw [hσ] at hv hu
  rw [Finset.mem_singleton]
  by_contra hv0
  rcases huv.2 with rfl | rfl
  · simp at hu; have := v.isLt; omega
  · exact hv0 rfl

section Count

variable {n : ℕ} (σ : LinearLayout (Fin (n + 1)))

/-- Leaves before the centre and after it. -/
private theorem card_before_add_card_after :
    (Finset.univ.filter fun v => (σ v).val < (σ 0).val).card +
      (Finset.univ.filter fun v => (σ 0).val < (σ v).val).card = n := by
  rw [← Finset.card_union_of_disjoint (Finset.disjoint_filter.mpr fun _ _ h h' => by omega)]
  have : (Finset.univ.filter fun v : Fin (n + 1) => (σ v).val < (σ 0).val) ∪
      (Finset.univ.filter fun v => (σ 0).val < (σ v).val) = Finset.univ.erase 0 := by
    ext v
    simp only [Finset.mem_union, Finset.mem_filter, Finset.mem_univ, true_and,
      Finset.mem_erase, and_true]
    constructor
    · rintro (h | h) rfl <;> omega
    · intro h
      have : (σ v).val ≠ (σ 0).val := fun h' => h (σ.injective (Fin.ext h'))
      omega
  rw [this, Finset.card_erase_of_mem (Finset.mem_univ _)]
  simp

/-- A set of leaves on one side gives as many edges of the centre inside a window. -/
private theorem card_le_pairs (S : Finset (Fin (n + 1))) (P : Fin (n + 1) × Fin (n + 1) → Prop)
    [DecidablePred P] (hS : ∀ v ∈ S, v ≠ 0 ∧ P (0, v)) :
    S.card ≤ (Finset.univ.filter fun p => (starGraph n).Adj p.1 p.2 ∧ P p).card := by
  rw [← Finset.card_image_of_injective S (f := fun v => ((0 : Fin (n + 1)), v))
    (fun a b h => (Prod.mk.inj h).2)]
  refine Finset.card_le_card fun p hp => ?_
  obtain ⟨v, hv, rfl⟩ := Finset.mem_image.mp hp
  obtain ⟨h0, hP⟩ := hS v hv
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  exact ⟨⟨Ne.symm h0, Or.inl rfl⟩, hP⟩

private theorem card_le_pairs' (S : Finset (Fin (n + 1)))
    (P : Fin (n + 1) × Fin (n + 1) → Prop)
    [DecidablePred P] (hS : ∀ v ∈ S, v ≠ 0 ∧ P (v, 0)) :
    S.card ≤ (Finset.univ.filter fun p => (starGraph n).Adj p.1 p.2 ∧ P p).card := by
  rw [← Finset.card_image_of_injective S (f := fun v => (v, (0 : Fin (n + 1))))
    (fun a b h => (Prod.mk.inj h).1)]
  refine Finset.card_le_card fun p hp => ?_
  obtain ⟨v, hv, rfl⟩ := Finset.mem_image.mp hp
  obtain ⟨h0, hP⟩ := hS v hv
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  exact ⟨⟨h0, Or.inr rfl⟩, hP⟩

theorem two_mul_cutwidthOfLayout_starGraph : n ≤ 2 * cutwidthOfLayout (starGraph n) σ := by
  have hsum := card_before_add_card_after σ
  set c := (σ 0).val with hc
  have hcn : c < Fintype.card (Fin (n + 1)) := (σ 0).isLt
  have hR : (Finset.univ.filter fun v => c < (σ v).val).card ≤ cutAt (starGraph n) σ c :=
    card_le_pairs _ _ fun v hv => by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv
      exact ⟨fun h => by subst h; omega, le_refl _, hv⟩
  have hL : (Finset.univ.filter fun v => (σ v).val < c).card ≤
      cutAt (starGraph n) σ (c - 1) :=
    card_le_pairs' _ _ fun v hv => by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv
      exact ⟨fun h => by subst h; omega, by dsimp only; omega, by dsimp only; omega⟩
  have h1 := cutAt_le_cutwidthOfLayout (starGraph n) σ hcn
  have h2 := cutAt_le_cutwidthOfLayout (starGraph n) σ (i := c - 1) (by omega)
  omega

theorem two_mul_modCutwidthOfLayout_starGraph :
    n ≤ 2 * modCutwidthOfLayout (starGraph n) σ + 2 := by
  have hsum := card_before_add_card_after σ
  set c := (σ 0).val with hc
  have hcard : Fintype.card (Fin (n + 1)) = n + 1 := Fintype.card_fin _
  -- leaves after `c + 1`, and before `c - 1`
  have hR : (Finset.univ.filter fun v => c < (σ v).val).card ≤
      (Finset.univ.filter fun v => c + 1 < (σ v).val).card + 1 := by
    by_cases hc1 : c + 1 < Fintype.card (Fin (n + 1))
    · refine (Finset.card_le_card (t := insert (σ.symm ⟨c + 1, hc1⟩)
        (Finset.univ.filter fun v => c + 1 < (σ v).val)) ?_).trans (Finset.card_insert_le _ _)
      intro v hv
      simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv
      rw [Finset.mem_insert, Finset.mem_filter]
      by_cases h : (σ v).val = c + 1
      · left; rw [Equiv.eq_symm_apply]; exact Fin.ext h
      · right; exact ⟨Finset.mem_univ _, by omega⟩
    · have : (Finset.univ.filter fun v => c < (σ v).val) = ∅ := by
        rw [Finset.filter_eq_empty_iff]
        intro v _ h; have := (σ v).isLt; omega
      rw [this]; simp
  have hL : (Finset.univ.filter fun v => (σ v).val < c).card ≤
      (Finset.univ.filter fun v => (σ v).val + 1 < c).card + 1 := by
    by_cases hc1 : 1 ≤ c
    · refine (Finset.card_le_card (t := insert (σ.symm ⟨c - 1, by
          have := (σ 0).isLt; omega⟩)
        (Finset.univ.filter fun v => (σ v).val + 1 < c)) ?_).trans (Finset.card_insert_le _ _)
      intro v hv
      simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv
      rw [Finset.mem_insert, Finset.mem_filter]
      by_cases h : (σ v).val = c - 1
      · left; rw [Equiv.eq_symm_apply]; exact Fin.ext h
      · right; exact ⟨Finset.mem_univ _, by omega⟩
    · have : (Finset.univ.filter fun v => (σ v).val < c) = ∅ := by
        rw [Finset.filter_eq_empty_iff]
        intro v _ h; omega
      rw [this]; simp
  have hR' : (Finset.univ.filter fun v => c + 1 < (σ v).val).card ≤
      modCutAt (starGraph n) σ (c + 1) :=
    card_le_pairs _ _ fun v hv => by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv
      exact ⟨fun h => by subst h; omega, by dsimp only; omega, hv⟩
  have hL' : (Finset.univ.filter fun v => (σ v).val + 1 < c).card ≤
      modCutAt (starGraph n) σ (c - 1) :=
    card_le_pairs' _ _ fun v hv => by
      simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hv
      exact ⟨fun h => by subst h; omega, by dsimp only; omega, by dsimp only; omega⟩
  have hc0 : c < n + 1 := by have := (σ 0).isLt; omega
  have h2 := modCutAt_le_modCutwidthOfLayout (starGraph n) σ (i := c - 1) (by omega)
  by_cases hc1 : c + 1 < n + 1
  · have h1 := modCutAt_le_modCutwidthOfLayout (starGraph n) σ (i := c + 1) (by omega)
    omega
  · have : (Finset.univ.filter fun v => c < (σ v).val) = ∅ := by
      rw [Finset.filter_eq_empty_iff]
      intro v _ h; have := (σ v).isLt; omega
    rw [this, Finset.card_empty] at hsum
    omega

end Count

/-- `cw(K_{1,n}) ≥ n / 2`. -/
theorem two_mul_cutwidth_starGraph (n : ℕ) : n ≤ 2 * cutwidth (starGraph n) := by
  obtain ⟨σ, hσ⟩ := exists_layout_cutwidth (starGraph n)
  rw [← hσ]; exact two_mul_cutwidthOfLayout_starGraph σ

/-- `mcw(K_{1,n}) ≥ n / 2 − 1`. -/
theorem two_mul_modCutwidth_starGraph (n : ℕ) : n ≤ 2 * modCutwidth (starGraph n) + 2 := by
  obtain ⟨σ, hσ⟩ := exists_layout_modCutwidth (starGraph n)
  rw [← hσ]; exact two_mul_modCutwidthOfLayout_starGraph σ

/-- **Cutwidth is not `pw ± 1`**: on `K_{1,7}`, `cw ≥ 4` while `pw ≤ 1`, so `cw` exceeds
both `pw + 1` and the open-stack value `pw + 1` by more than one. -/
theorem pathwidth_add_two_lt_cutwidth_star7 :
    pathwidth (starGraph 7) + 2 < cutwidth (starGraph 7) := by
  have := two_mul_cutwidth_starGraph 7
  have := pathwidth_starGraph_le_one 7
  omega

/-- **Modified cutwidth (Def. 6) is not `pw ± 1`**: on `K_{1,9}`, `mcw ≥ 4`, `pw ≤ 1`. -/
theorem pathwidth_add_two_lt_modCutwidth_star9 :
    pathwidth (starGraph 9) + 2 < modCutwidth (starGraph 9) := by
  have := two_mul_modCutwidth_starGraph 9
  have := pathwidth_starGraph_le_one 9
  omega

/-- No additive constant relates cutwidth to pathwidth. -/
theorem cutwidth_unbounded (k : ℕ) :
    ∃ n, pathwidth (starGraph n) + k ≤ cutwidth (starGraph n) :=
  ⟨2 * k + 2, by
    have := two_mul_cutwidth_starGraph (2 * k + 2)
    have := pathwidth_starGraph_le_one (2 * k + 2)
    omega⟩

/-- No additive constant relates modified cutwidth to pathwidth. -/
theorem modCutwidth_unbounded (k : ℕ) :
    ∃ n, pathwidth (starGraph n) + k ≤ modCutwidth (starGraph n) :=
  ⟨2 * k + 4, by
    have := two_mul_modCutwidth_starGraph (2 * k + 4)
    have := pathwidth_starGraph_le_one (2 * k + 4)
    omega⟩

end Star

end Complex

end MOSPFormalization
