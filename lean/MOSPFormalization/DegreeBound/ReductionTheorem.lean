/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Theorem 3.2: the reduction theorem, by induction on the support

Item 08 of loop0012 (`reports/edwards_mcdermid_plan.md` §0.5; `reports/edwards_mcdermid.md`
§2.6 and §8): Theorem 3.2 of Edwards & McDermid (2015, p. 9) in the one-vertex-type design.
For every `G` with every degree `0` or `≥ 3` and `G ≠ ⊥` there are `X ⊆ supp G` and a graph `B`
with `SPReduces (G − X) B`, `B ≠ ⊥`, `B` reduced and basic (every non-trivial component cubic or
of the second kind), and `|X| + f⁻(B) ≤ f⁻(G)`. The paper's `r(G − X)` (a function) is replaced
by "some reduced reduct `B` of `G − X`", and its appeal to the confluence of the reduction system
(Lemma 3.1, citing Kneis et al. 2009) by the commutation lemma R4 of item 06 — no confluence fact
is stated or used anywhere.

* `IsReductionSet G X B` — the six clauses of the conclusion, as a `Prop`-valued structure.
* **T1** `exists_reduction_set`: `IsSPReduced G → G ≠ ⊥ → ∃ X B (_ : DecidableRel B.Adj), IsReductionSet G X B`;
  `exists_reduction_set_and` is the same statement as a conjunction (report §2.6's form). The
  proof is `exists_reduction_set_of_card`, a strong induction on `|supp G|` with the paper's
  three cases: basic (`isReductionSet_empty`: `X = ∅`, `B = G`); the support disconnected
  (`exists_reduction_set_of_split`: `C` the vertex set of the component of a support vertex `u`
  not reaching a support vertex `v`, `G = G|C ⊔ G|Cᶜ`, the induction hypothesis on each half,
  and `isReductionSet_sup`, which unions the two reduction sets); connected and not basic
  (`isReductionSet_insert`: the two-key `w` of item 07, a reduced reduct `G*` of `G − w`
  (`exists_reduced_reduct`), the induction hypothesis on `G*` giving `X*`, `B`, and
  `X = insert w X*`, with `(G − w) − X* →* G* − X*` from R4 and `|X| + f⁻(B) ≤ 1 + f⁻(G*) ≤ f⁻(G)`
  from S1).
* **Disjoint unions.** `isSPReduced_sup`, `isBasic_sup`: with `G₁`, `G₂` of disjoint supports
  (`∀ a, (∃ z, G₁.Adj a z) → ∀ z, ¬ G₂.Adj a z`), "reduced" and "basic" pass to `G₁ ⊔ G₂`. The
  basic case goes through `isBasic_clause_of_agree`: if `H ≥ G₁` agrees with `G₁` at every
  vertex that has a `G₁`-edge, then the `H`-component of such a vertex is its `G₁`-component as a
  vertex set (`supp_eq_of_agree`, via `reachable_iff_of_agree`), has the same degrees, and the
  same restriction, so the clause of `IsBasic` transfers. `isolateSet_sup`,
  `isolateSet_union_of_forall_not_adj` are the identities that put `G − (X₁ ∪ X₂)` in the form
  `(G|C − X₁) ⊔ (G|Cᶜ − X₂)`; `ndeg_restrict_of_mem`, `ndeg_restrict_of_not_mem`,
  `isSPReduced_restrict` give the degrees of a half.
* **Basic graphs per component** (what item 09 uses). `isBasic_component`: the clause of
  `IsBasic`, read with `G.degree` and `compFinset`; `compPotential_cubic`: a cubic component
  `C` has `compPotential G C = |C|/6 − 1/6`; `compPotential_ge_five_sixths`: in a reduced graph a
  component with a vertex of degree `≥ 4` has `compPotential ≥ 5/6` (and `five_le_card_compFinset`:
  at least 5 vertices); `compPotential_cubic_or_ge_five_sixths`: in a reduced graph every
  non-trivial component is one or the other. The item's "second kind ⇒ `≥ 5/6`" is not the right
  hypothesis (`K₄` is cubic *and* of the second kind, with `f⁻ = 1/2`; report §2.1 (3)): the
  floor is for non-cubic components, basic or not.

Every statement was checked by brute force in the form proved here before it was stated
(`reports/scratch/edwards_mcdermid/08_reduction/check.py`: every graph on 1–9 vertices,
288,266 graphs, with the Lean induction replayed on each of the 89,972 reduced non-empty ones
and on 8,212 random disjoint unions of reduced graphs; zero violations). Nothing here is about
pathwidth (item 09) or about the hypotheses (H1), (H3); the reduct `B` is not claimed unique.
-/
import MOSPFormalization.DegreeBound.Step

set_option linter.unusedSectionVars false

namespace MOSPFormalization.DegreeBound

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### Small instance-free facts -/

theorem exists_adj_of_ndeg_pos {G : SimpleGraph V} {v : V} (h : 0 < ndeg G v) :
    ∃ z, G.Adj v z := by
  by_contra hno
  push Not at hno
  rw [ndeg_eq_zero_iff.2 hno] at h
  exact lt_irrefl 0 h

theorem ne_bot_of_adj {G : SimpleGraph V} {a b : V} (h : G.Adj a b) : G ≠ ⊥ := by
  rintro rfl
  exact (SimpleGraph.bot_adj a b).1 h

theorem exists_adj_of_reachable_of_ne {G : SimpleGraph V} {u v : V} (h : G.Reachable u v)
    (hne : u ≠ v) : ∃ z, G.Adj u z := by
  obtain ⟨p⟩ := h
  cases p with
  | nil => exact absurd rfl hne
  | cons hadj _ => exact ⟨_, hadj⟩

theorem eq_of_reachable_of_forall_not_adj {G : SimpleGraph V} {u v : V} (h : G.Reachable u v)
    (hu : ∀ z, ¬ G.Adj u z) : u = v := by
  by_contra hne
  obtain ⟨z, hz⟩ := exists_adj_of_reachable_of_ne h hne
  exact hu z hz

/-- A subgraph has a smaller support. -/
theorem supp_subset_of_le {G G' : SimpleGraph V} [DecidableRel G.Adj] [DecidableRel G'.Adj]
    (h : G ≤ G') : supp G ⊆ supp G' := by
  intro v hv
  rw [mem_supp, ← ndeg_eq_degree] at hv ⊢
  exact lt_of_lt_of_le hv (ndeg_le_of_le h v)

/-- `f⁻` does not depend on the decidability instance. -/
theorem potentialMinus_congr {G G' : SimpleGraph V} (i : DecidableRel G.Adj)
    (i' : DecidableRel G'.Adj) (h : G = G') :
    @potentialMinus V _ _ G i = @potentialMinus V _ _ G' i' := by
  subst h
  have : i = i' := Subsingleton.elim _ _
  subst this
  rfl

/-- R2 in the vocabulary of edges: a vertex with an edge in the reduct had one before. -/
theorem SPReduces.exists_adj_of_exists_adj {G H : SimpleGraph V} (h : SPReduces G H) {a : V}
    (ha : ∃ z, H.Adj a z) : ∃ z, G.Adj a z := by
  by_contra hno
  push Not at hno
  obtain ⟨z, hz⟩ := ha
  exact h.not_adj_of_not_adj hno z hz

/-! ### `restrict` on a set closed under adjacency -/

section Restrict

variable {G : SimpleGraph V} {S : Set V}

theorem neighborSet_restrict_of_mem (hS : ∀ a b, G.Adj a b → (a ∈ S ↔ b ∈ S)) {x : V}
    (hx : x ∈ S) : (restrict G S).neighborSet x = G.neighborSet x := by
  ext z
  simp only [SimpleGraph.mem_neighborSet, restrict_adj]
  exact ⟨fun h => h.1, fun h => ⟨h, hx, (hS x z h).1 hx⟩⟩

theorem ndeg_restrict_of_mem (hS : ∀ a b, G.Adj a b → (a ∈ S ↔ b ∈ S)) {x : V} (hx : x ∈ S) :
    ndeg (restrict G S) x = ndeg G x := by
  unfold ndeg
  rw [neighborSet_restrict_of_mem hS hx]

theorem ndeg_restrict_of_not_mem {x : V} (hx : x ∉ S) : ndeg (restrict G S) x = 0 :=
  ndeg_eq_zero_iff.2 (fun _ hz => hx hz.2.1)

/-- A reduced graph restricted to a set closed under adjacency is reduced. -/
theorem isSPReduced_restrict (hG : IsSPReduced G) (hS : ∀ a b, G.Adj a b → (a ∈ S ↔ b ∈ S)) :
    IsSPReduced (restrict G S) := by
  intro x
  by_cases hx : x ∈ S
  · rw [ndeg_restrict_of_mem hS hx]; exact hG x
  · rw [ndeg_restrict_of_not_mem hx]; exact Or.inl rfl

theorem adj_closed_compl (hS : ∀ a b, G.Adj a b → (a ∈ S ↔ b ∈ S)) :
    ∀ a b, G.Adj a b → (a ∈ Sᶜ ↔ b ∈ Sᶜ) := fun a b hab => by
  simp only [Set.mem_compl_iff]
  exact not_congr (hS a b hab)

/-- The vertex set of a connected component is closed under adjacency. -/
theorem adj_closed_supp_connectedComponent (u : V) :
    ∀ a b, G.Adj a b →
      (a ∈ (G.connectedComponentMk u).supp ↔ b ∈ (G.connectedComponentMk u).supp) := by
  intro a b hab
  simp only [SimpleGraph.ConnectedComponent.mem_supp_iff]
  rw [SimpleGraph.ConnectedComponent.connectedComponentMk_eq_of_adj hab]

end Restrict

/-! ### Disjoint unions: "reduced" passes to the union -/

section Sup

variable {G₁ G₂ : SimpleGraph V}

theorem ndeg_sup_of_forall_not_adj_right {v : V} (h : ∀ z, ¬ G₂.Adj v z) :
    ndeg (G₁ ⊔ G₂) v = ndeg G₁ v := by
  unfold ndeg
  congr 1
  ext z
  simp only [SimpleGraph.mem_neighborSet, SimpleGraph.sup_adj]
  exact ⟨fun h' => h'.resolve_right (h z), Or.inl⟩

theorem ndeg_sup_of_forall_not_adj_left {v : V} (h : ∀ z, ¬ G₁.Adj v z) :
    ndeg (G₁ ⊔ G₂) v = ndeg G₂ v := by
  rw [sup_comm]
  exact ndeg_sup_of_forall_not_adj_right h

/-- Two reduced graphs with disjoint supports have a reduced union. -/
theorem isSPReduced_sup (h₁ : IsSPReduced G₁) (h₂ : IsSPReduced G₂)
    (hdisj : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, ¬ G₂.Adj a z) : IsSPReduced (G₁ ⊔ G₂) := by
  intro v
  by_cases h : ∃ z, G₁.Adj v z
  · rw [ndeg_sup_of_forall_not_adj_right (hdisj v h)]; exact h₁ v
  · push Not at h
    rw [ndeg_sup_of_forall_not_adj_left h]; exact h₂ v

theorem disjoint_supp_of_forall_not_adj [DecidableRel G₁.Adj] [DecidableRel G₂.Adj]
    (hdisj : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, ¬ G₂.Adj a z) : Disjoint (supp G₁) (supp G₂) := by
  rw [Finset.disjoint_left]
  intro a h1 h2
  obtain ⟨z', hz'⟩ := mem_supp_iff_exists_adj.1 h2
  exact hdisj a (mem_supp_iff_exists_adj.1 h1) z' hz'

end Sup

/-! ### Components of a graph that agrees with `G₁` at every `G₁`-vertex, and "basic" on a
disjoint union -/

section Agree

variable {G₁ H : SimpleGraph V}

/-- If `H ≥ G₁` agrees with `G₁` at every vertex that has a `G₁`-edge, reachability from such a
vertex is the same in `H` and in `G₁` (a walk in `H` from it never leaves `G₁`). -/
theorem reachable_iff_of_agree (hle : G₁ ≤ H)
    (hH : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, H.Adj a z ↔ G₁.Adj a z) {v x : V}
    (hv : ∃ z, G₁.Adj v z) : H.Reachable v x ↔ G₁.Reachable v x := by
  refine ⟨fun h => ?_, fun h => h.mono hle⟩
  suffices hw : ∀ a b (p : H.Walk a b), (∃ z, G₁.Adj a z) → G₁.Reachable a b by
    obtain ⟨p⟩ := h
    exact hw v x p hv
  intro a b p
  induction p with
  | nil => exact fun _ => SimpleGraph.Reachable.refl _
  | cons hab _ ih =>
    intro ha
    have hab' := (hH _ ha _).1 hab
    exact hab'.reachable.trans (ih ⟨_, hab'.symm⟩)

/-- The `H`-component of such a vertex is its `G₁`-component, as a vertex set. -/
theorem supp_eq_of_agree (hle : G₁ ≤ H)
    (hH : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, H.Adj a z ↔ G₁.Adj a z) {K : H.ConnectedComponent}
    {v : V} (hvK : v ∈ K.supp) (hv : ∃ z, G₁.Adj v z) :
    K.supp = (G₁.connectedComponentMk v).supp := by
  have hvK' : H.connectedComponentMk v = K := hvK
  ext x
  show H.connectedComponentMk x = K ↔ G₁.connectedComponentMk x = G₁.connectedComponentMk v
  rw [← hvK', SimpleGraph.ConnectedComponent.eq, SimpleGraph.ConnectedComponent.eq,
    SimpleGraph.reachable_comm, reachable_iff_of_agree hle hH hv, SimpleGraph.reachable_comm]

theorem adj_iff_of_mem_supp_of_agree (hle : G₁ ≤ H)
    (hH : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, H.Adj a z ↔ G₁.Adj a z) {K : H.ConnectedComponent}
    {v : V} (hvK : v ∈ K.supp) (hv : ∃ z, G₁.Adj v z) {x : V} (hx : x ∈ K.supp) :
    ∀ z, H.Adj x z ↔ G₁.Adj x z := by
  have hx' : G₁.Reachable x v := by
    rw [supp_eq_of_agree hle hH hvK hv] at hx
    exact SimpleGraph.ConnectedComponent.exact hx
  by_cases hxv : x = v
  · rw [hxv]; exact hH v hv
  · exact hH x (exists_adj_of_reachable_of_ne hx' hxv)

/-- The clause of `IsBasic` for a component of `H` containing a `G₁`-vertex follows from
`IsBasic G₁`: the component, its degrees and its restriction are those of `G₁`. -/
theorem isBasic_clause_of_agree (h₁ : IsBasic G₁) (hle : G₁ ≤ H)
    (hH : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, H.Adj a z ↔ G₁.Adj a z) {K : H.ConnectedComponent}
    {v : V} (hvK : v ∈ K.supp) (hv : ∃ z, G₁.Adj v z) :
    (∀ x ∈ K.supp, ndeg H x = 3) ∨ ∃ x ∈ K.supp, SPReduces (isolate (restrict H K.supp) x) ⊥ := by
  have hK := supp_eq_of_agree hle hH hvK hv
  have hagree : ∀ x ∈ K.supp, ∀ z, H.Adj x z ↔ G₁.Adj x z :=
    fun x hx => adj_iff_of_mem_supp_of_agree hle hH hvK hv hx
  have hdeg : ∀ x ∈ K.supp, ndeg H x = ndeg G₁ x := fun x hx => by
    unfold ndeg
    congr 1
    ext z
    simp only [SimpleGraph.mem_neighborSet]
    exact hagree x hx z
  have hres : restrict H K.supp = restrict G₁ K.supp := by
    ext a b
    simp only [restrict_adj]
    constructor
    · rintro ⟨h, ha, hb⟩; exact ⟨(hagree a ha b).1 h, ha, hb⟩
    · rintro ⟨h, ha, hb⟩; exact ⟨(hagree a ha b).2 h, ha, hb⟩
  obtain ⟨z, hz⟩ := hv
  rcases h₁ (G₁.connectedComponentMk v)
      ⟨v, (SimpleGraph.ConnectedComponent.mem_supp_iff _ _).2 rfl, ndeg_pos_of_adj hz⟩
    with hcub | ⟨x, hx, hred⟩
  · left
    intro x hx
    rw [hdeg x hx]
    exact hcub x (by rw [← hK]; exact hx)
  · right
    refine ⟨x, by rw [hK]; exact hx, ?_⟩
    rw [hres, hK]
    exact hred

end Agree

/-- Two basic graphs with disjoint supports have a basic union: every component of the union
is a component of one of the two. -/
theorem isBasic_sup {G₁ G₂ : SimpleGraph V} (h₁ : IsBasic G₁) (h₂ : IsBasic G₂)
    (hdisj : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, ¬ G₂.Adj a z) : IsBasic (G₁ ⊔ G₂) := by
  rintro K ⟨v, hvK, hv⟩
  obtain ⟨z, hz⟩ := exists_adj_of_ndeg_pos hv
  rcases (SimpleGraph.sup_adj _ _ _ _).1 hz with hz | hz
  · exact isBasic_clause_of_agree h₁ le_sup_left
      (fun a ha z => ⟨fun h => ((SimpleGraph.sup_adj _ _ _ _).1 h).resolve_right (hdisj a ha z),
        Or.inl⟩) hvK ⟨z, hz⟩
  · have hdisj' : ∀ a, (∃ z, G₂.Adj a z) → ∀ z, ¬ G₁.Adj a z :=
      fun a ⟨z', hz'⟩ z'' hz'' => hdisj a ⟨z'', hz''⟩ z' hz'
    exact isBasic_clause_of_agree h₂ le_sup_right
      (fun a ha z => ⟨fun h => ((SimpleGraph.sup_adj _ _ _ _).1 h).resolve_left (hdisj' a ha z),
        Or.inr⟩) hvK ⟨z, hz⟩

/-! ### `isolateSet` across a union, and with vertices off the support -/

theorem isolateSet_sup (G₁ G₂ : SimpleGraph V) (X : Finset V) :
    isolateSet (G₁ ⊔ G₂) X = isolateSet G₁ X ⊔ isolateSet G₂ X := by
  ext a b
  simp only [isolateSet_adj, SimpleGraph.sup_adj]
  tauto

theorem isolateSet_union_of_forall_not_adj (G : SimpleGraph V) {X Y : Finset V}
    (hY : ∀ y ∈ Y, ∀ z, ¬ G.Adj y z) : isolateSet G (X ∪ Y) = isolateSet G X := by
  ext a b
  simp only [isolateSet_adj, Finset.mem_union, not_or]
  constructor
  · rintro ⟨h, ⟨ha, -⟩, ⟨hb, -⟩⟩; exact ⟨h, ha, hb⟩
  · rintro ⟨h, ha, hb⟩
    exact ⟨h, ⟨ha, fun hY' => hY a hY' b h⟩, ⟨hb, fun hY' => hY b hY' a h.symm⟩⟩

theorem isolateSet_union_of_forall_not_adj_left (G : SimpleGraph V) {X Y : Finset V}
    (hY : ∀ y ∈ Y, ∀ z, ¬ G.Adj y z) : isolateSet G (Y ∪ X) = isolateSet G X := by
  rw [Finset.union_comm]
  exact isolateSet_union_of_forall_not_adj G hY

/-! ### Basic graphs, read per component (what item 09 uses) -/

section Components

variable (G : SimpleGraph V) [DecidableRel G.Adj]

theorem mem_compFinset_iff_mem_supp {C : G.ConnectedComponent} {u : V} :
    u ∈ compFinset G C ↔ u ∈ C.supp := by
  rw [mem_compFinset]
  exact Iff.rfl

/-- The clause of `IsBasic`, with `G.degree` and `compFinset`: a component with a vertex of
positive degree is cubic or of the second kind. -/
theorem isBasic_component (hb : IsBasic G) {C : G.ConnectedComponent} {v : V}
    (hv : v ∈ compFinset G C) (hpos : 0 < G.degree v) :
    (∀ u ∈ compFinset G C, G.degree u = 3) ∨
      ∃ u ∈ compFinset G C, SPReduces (isolate (restrict G C.supp) u) ⊥ := by
  rcases hb C ⟨v, (mem_compFinset_iff_mem_supp G).1 hv, by rw [ndeg_eq_degree]; exact hpos⟩
    with h | ⟨u, hu, h⟩
  · left
    intro u hu
    rw [← ndeg_eq_degree]
    exact h u ((mem_compFinset_iff_mem_supp G).1 hu)
  · right
    exact ⟨u, (mem_compFinset_iff_mem_supp G).2 hu, h⟩

/-- A vertex and its neighbours lie in its component. -/
theorem insert_neighborFinset_subset_compFinset {C : G.ConnectedComponent} {v : V}
    (hv : v ∈ compFinset G C) : insert v (G.neighborFinset v) ⊆ compFinset G C := by
  intro u hu
  rw [Finset.mem_insert] at hu
  rcases hu with rfl | hu
  · exact hv
  · rw [SimpleGraph.mem_neighborFinset] at hu
    have hv' := (mem_compFinset G).1 hv
    exact (mem_compFinset G).2
      ((SimpleGraph.ConnectedComponent.connectedComponentMk_eq_of_adj hu).symm.trans hv')

/-- A component with a vertex of degree `≥ 4` has at least 5 vertices. -/
theorem five_le_card_compFinset {C : G.ConnectedComponent} {v : V} (hv : v ∈ compFinset G C)
    (h4 : 4 ≤ G.degree v) : 5 ≤ (compFinset G C).card := by
  have hnot : v ∉ G.neighborFinset v := by
    rw [SimpleGraph.mem_neighborFinset]; exact G.loopless.irrefl v
  have := Finset.card_le_card (insert_neighborFinset_subset_compFinset G hv)
  rw [Finset.card_insert_of_notMem hnot, SimpleGraph.card_neighborFinset_eq_degree] at this
  omega

/-- **B1 per component**: a cubic component `C` has `compPotential G C = |C|/6 − 1/6`. -/
theorem compPotential_cubic {C : G.ConnectedComponent}
    (hcub : ∀ u ∈ compFinset G C, G.degree u = 3) :
    compPotential G C = ((compFinset G C).card : ℚ) / 6 - 1 / 6 := by
  have hmin : minDeg G C = 3 := by
    obtain ⟨v, hv, hd⟩ := exists_degree_eq_minDeg G C
    rw [← hd, hcub v hv]
  unfold compPotential
  rw [hmin, g'_three, sum_congr rfl (fun u hu => by rw [hcub u hu, g_three]), sum_const,
    nsmul_eq_mul]
  ring

/-- **The floor per component**: every degree `0` or `≥ 3`, and a vertex of degree `≥ 4` in
`C` ⇒ `5/6 ≤ compPotential G C` (`g 4 + 4 g 3 − 1/6`). This is the statement behind the
item's "second kind ⇒ `≥ 5/6`": the hypothesis is "not cubic", not "second kind" (`K₄` is
both cubic and of the second kind, with `f⁻ = 1/2`; report §2.1 (3)). -/
theorem compPotential_ge_five_sixths {C : G.ConnectedComponent}
    (hdeg : ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v) {v₁ : V} (hv₁ : v₁ ∈ compFinset G C)
    (h4 : 4 ≤ G.degree v₁) : 5 / 6 ≤ compPotential G C := by
  unfold compPotential
  have hg' := g'_le_sixth (minDeg G C)
  have h1 : ∑ u ∈ insert v₁ (G.neighborFinset v₁), g (G.degree u)
      ≤ ∑ u ∈ compFinset G C, g (G.degree u) :=
    sum_le_sum_of_subset_of_nonneg (insert_neighborFinset_subset_compFinset G hv₁)
      (fun u _ _ => g_nonneg _)
  have hnot : v₁ ∉ G.neighborFinset v₁ := by
    rw [SimpleGraph.mem_neighborFinset]; exact G.loopless.irrefl v₁
  rw [sum_insert hnot] at h1
  have h2 : g 4 ≤ g (G.degree v₁) := g_monotone h4
  have h3 : ((G.neighborFinset v₁).card : ℚ) * (1 / 6)
      ≤ ∑ u ∈ G.neighborFinset v₁, g (G.degree u) := by
    have := card_nsmul_le_sum (G.neighborFinset v₁) (fun u => g (G.degree u)) (1 / 6)
      (fun u hu => by
        rw [SimpleGraph.mem_neighborFinset] at hu
        rw [← g_three]; exact g_monotone (three_le_degree_of_adj G hdeg hu))
    rwa [nsmul_eq_mul] at this
  rw [SimpleGraph.card_neighborFinset_eq_degree] at h3
  have h4' : (4 : ℚ) ≤ (G.degree v₁ : ℚ) := by exact_mod_cast h4
  rw [g_four] at h2
  linarith

/-- In a reduced graph, a component with a vertex of positive degree is cubic (and then
`compPotential = |C|/6 − 1/6`) or has `compPotential ≥ 5/6`. -/
theorem compPotential_cubic_or_ge_five_sixths (hG : IsSPReduced G) {C : G.ConnectedComponent}
    {v : V} (hv : v ∈ compFinset G C) (hpos : 0 < G.degree v) :
    compPotential G C = ((compFinset G C).card : ℚ) / 6 - 1 / 6 ∨ 5 / 6 ≤ compPotential G C := by
  by_cases hcub : ∀ u ∈ compFinset G C, G.degree u = 3
  · exact Or.inl (compPotential_cubic G hcub)
  · right
    push Not at hcub
    obtain ⟨u, hu, hne3⟩ := hcub
    have hdeg := (isSPReduced_iff G).1 hG
    have hupos : 0 < G.degree u := by
      by_cases huv : u = v
      · rw [huv]; exact hpos
      · refine pos_degree_of_reachable_of_ne G ?_ huv
        have hu' := (mem_compFinset G).1 hu
        have hv' := (mem_compFinset G).1 hv
        exact SimpleGraph.ConnectedComponent.exact (hu'.trans hv'.symm)
    have h4 : 4 ≤ G.degree u := by rcases hdeg u with h | h <;> omega
    exact compPotential_ge_five_sixths G hdeg hu h4

end Components

/-! ### Theorem 3.2 -/

/-- The conclusion of Theorem 3.2 for `G`: `X` is a *reduction set* with basic reduct `B` —
`X ⊆ supp G`, `G − X →* B`, `B ≠ ⊥`, `B` reduced and basic, `|X| + f⁻(B) ≤ f⁻(G)`. -/
structure IsReductionSet (G : SimpleGraph V) [DecidableRel G.Adj] (X : Finset V)
    (B : SimpleGraph V) [DecidableRel B.Adj] : Prop where
  subset_supp : X ⊆ supp G
  reduces : SPReduces (isolateSet G X) B
  ne_bot : B ≠ ⊥
  reduced : IsSPReduced B
  basic : IsBasic B
  card_add_le : (X.card : ℚ) + potentialMinus B ≤ potentialMinus G

namespace IsReductionSet

variable {G B : SimpleGraph V} [DecidableRel G.Adj] [DecidableRel B.Adj] {X : Finset V}

/-- `|X| ≤ f⁻(G)` (every `f⁻` is non-negative). -/
theorem card_le_potentialMinus (h : IsReductionSet G X B) : (X.card : ℚ) ≤ potentialMinus G :=
  by have := h.card_add_le; have := potentialMinus_nonneg B; linarith

/-- The statement does not depend on the decidability instance of `G`. -/
theorem congr_left {G' : SimpleGraph V} (i : DecidableRel G.Adj) (i' : DecidableRel G'.Adj)
    (hGG' : G = G') (h : @IsReductionSet V _ _ G i X B _) :
    @IsReductionSet V _ _ G' i' X B _ := by
  subst hGG'
  have : i = i' := Subsingleton.elim _ _
  subst this
  exact h

end IsReductionSet

/-- **The basic case**: `X = ∅`, `B = G`. -/
theorem isReductionSet_empty {G : SimpleGraph V} [DecidableRel G.Adj] (hG : IsSPReduced G)
    (hne : G ≠ ⊥) (hb : IsBasic G) : IsReductionSet G ∅ G where
  subset_supp := Finset.empty_subset _
  reduces := by rw [isolateSet_empty]; exact SPReduces.refl G
  ne_bot := hne
  reduced := hG
  basic := hb
  card_add_le := by simp

/-- **The connected non-basic step** (the paper's induction step, p. 9): `G` reduced, connected on
its support and not basic, `w` the two-key choice, `G*` a reduced reduct of `G − w`; a reduction
set `X*` of `G*` gives the reduction set `insert w X*` of `G`. `(G − w) − X* →* G* − X*` is R4
(`X* ⊆ supp G*`, so no step of `G − w →* G*` acts in `X*`), and
`|X| + f⁻(B) = 1 + |X*| + f⁻(B) ≤ 1 + f⁻(G*) ≤ f⁻(G)` is S1. -/
theorem isReductionSet_insert {G Gs B : SimpleGraph V} [DecidableRel G.Adj] [DecidableRel Gs.Adj]
    [DecidableRel B.Adj] (hG : IsSPReduced G)
    (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v) (hnb : ¬ IsBasic G) {w : V}
    (hmax : ∀ u, G.degree u ≤ G.degree w)
    (htie : ∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u)
    (hred : SPReduces (isolate G w) Gs) (hGs : IsSPReduced Gs) {Xs : Finset V}
    (h : IsReductionSet Gs Xs B) : IsReductionSet G (insert w Xs) B := by
  have h4 : 4 ≤ G.degree w := four_le_degree_of_not_isBasic G hG hnb hmax
  have hws : w ∈ supp G := mem_supp.2 (by omega)
  have hsub : supp Gs ⊆ supp G := hred.supp_subset.trans (supp_isolate_subset G w)
  have hwGs : w ∉ supp Gs := fun hw => by
    have := hred.supp_subset hw
    rw [mem_supp, degree_isolate_self] at this
    exact lt_irrefl 0 this
  have hwXs : w ∉ Xs := fun hw => hwGs (h.subset_supp hw)
  refine ⟨Finset.insert_subset hws (h.subset_supp.trans hsub), ?_, h.ne_bot, h.reduced, h.basic,
    ?_⟩
  · rw [isolateSet_insert, ← isolateSet_comm_isolate]
    exact (hred.isolateSet_comm
      (fun x hx => mem_supp_iff_exists_adj.1 (h.subset_supp hx))).trans h.reduces
  · rw [Finset.card_insert_of_notMem hwXs]
    push_cast
    have h1 := one_add_potentialMinus_le G hG hconn hnb hmax htie hred hGs
    have h2 := h.card_add_le
    linarith

/-- **The disconnected case, assembled**: reduction sets of two graphs with disjoint supports
union to a reduction set of their union. `G₁ ⊔ G₂ − (X₁ ∪ X₂) = (G₁ − X₁) ⊔ (G₂ − X₂)`, both
reductions lift by R5, `B₁ ⊔ B₂` is reduced and basic (`isSPReduced_sup`, `isBasic_sup`), and
`f⁻` is additive on both sides (`potentialMinus_add`). -/
theorem isReductionSet_sup {G₁ G₂ B₁ B₂ : SimpleGraph V} [DecidableRel G₁.Adj]
    [DecidableRel G₂.Adj] [DecidableRel B₁.Adj] [DecidableRel B₂.Adj] {X₁ X₂ : Finset V}
    (h₁ : IsReductionSet G₁ X₁ B₁) (h₂ : IsReductionSet G₂ X₂ B₂)
    (hdisj : ∀ a, (∃ z, G₁.Adj a z) → ∀ z, ¬ G₂.Adj a z) :
    IsReductionSet (G₁ ⊔ G₂) (X₁ ∪ X₂) (B₁ ⊔ B₂) := by
  -- a vertex with a `B₁`-edge has a `G₁`-edge (R2), and likewise on the right
  have hB₁ : ∀ a, (∃ z, B₁.Adj a z) → ∃ z, G₁.Adj a z := fun a ha => by
    obtain ⟨z, hz⟩ := h₁.reduces.exists_adj_of_exists_adj ha
    exact ⟨z, hz.1⟩
  have hB₂ : ∀ a, (∃ z, B₂.Adj a z) → ∃ z, G₂.Adj a z := fun a ha => by
    obtain ⟨z, hz⟩ := h₂.reduces.exists_adj_of_exists_adj ha
    exact ⟨z, hz.1⟩
  have hdisj' : ∀ a, (∃ z, G₂.Adj a z) → ∀ z, ¬ G₁.Adj a z :=
    fun a ⟨z', hz'⟩ z'' hz'' => hdisj a ⟨z'', hz''⟩ z' hz'
  have hdisjB : ∀ a, (∃ z, B₁.Adj a z) → ∀ z, ¬ B₂.Adj a z := fun a ha z hz => by
    obtain ⟨z', hz'⟩ := hB₂ a ⟨z, hz⟩
    exact hdisj a (hB₁ a ha) z' hz'
  have hX₁ : ∀ a ∈ X₁, ∃ z, G₁.Adj a z :=
    fun a ha => mem_supp_iff_exists_adj.1 (h₁.subset_supp ha)
  have hX₂ : ∀ a ∈ X₂, ∃ z, G₂.Adj a z :=
    fun a ha => mem_supp_iff_exists_adj.1 (h₂.subset_supp ha)
  have hsupp : Disjoint (supp G₁) (supp G₂) := disjoint_supp_of_forall_not_adj hdisj
  have hsuppB : Disjoint (supp B₁) (supp B₂) := disjoint_supp_of_forall_not_adj hdisjB
  refine ⟨?_, ?_, ?_, isSPReduced_sup h₁.reduced h₂.reduced hdisjB,
    isBasic_sup h₁.basic h₂.basic hdisjB, ?_⟩
  · exact Finset.union_subset (h₁.subset_supp.trans (supp_subset_of_le le_sup_left))
      (h₂.subset_supp.trans (supp_subset_of_le le_sup_right))
  · have e : isolateSet (G₁ ⊔ G₂) (X₁ ∪ X₂) = isolateSet G₁ X₁ ⊔ isolateSet G₂ X₂ := by
      rw [isolateSet_sup,
        isolateSet_union_of_forall_not_adj G₁ (fun y hy z hz => hdisj' y (hX₂ y hy) z hz),
        isolateSet_union_of_forall_not_adj_left G₂ (fun y hy z hz => hdisj y (hX₁ y hy) z hz)]
    rw [e]
    have s1 : SPReduces (isolateSet G₁ X₁ ⊔ isolateSet G₂ X₂) (B₁ ⊔ isolateSet G₂ X₂) :=
      h₁.reduces.sup_of_disjoint (fun a b hab z haz => hdisj' a ⟨b, hab.1⟩ z haz.1)
    have s2 : SPReduces (isolateSet G₂ X₂ ⊔ B₁) (B₂ ⊔ B₁) :=
      h₂.reduces.sup_of_disjoint (fun a b hab z haz => hdisj a (hB₁ a ⟨b, hab⟩) z haz.1)
    rw [sup_comm (isolateSet G₂ X₂) B₁, sup_comm B₂ B₁] at s2
    exact s1.trans s2
  · intro hbot
    apply h₁.ne_bot
    have hle : B₁ ≤ B₁ ⊔ B₂ := le_sup_left
    rw [hbot] at hle
    exact le_bot_iff.1 hle
  · have hXX : Disjoint X₁ X₂ := Finset.disjoint_left.2 (fun a ha₁ ha₂ => by
      obtain ⟨z, hz⟩ := hX₂ a ha₂
      exact hdisj a (hX₁ a ha₁) z hz)
    rw [Finset.card_union_of_disjoint hXX, Nat.cast_add, potentialMinus_add hsuppB,
      potentialMinus_add hsupp]
    have := h₁.card_add_le
    have := h₂.card_add_le
    linarith

/-- **The disconnected case**: with `C` closed under adjacency, `u ∈ C` and `v ∉ C` both in the
support, `G = G|C ⊔ G|Cᶜ` with both halves reduced, non-empty and of smaller support; the
induction hypothesis on each and `isReductionSet_sup`. -/
theorem exists_reduction_set_of_split {G : SimpleGraph V} [DecidableRel G.Adj]
    (hG : IsSPReduced G)
    (ih : ∀ (H : SimpleGraph V) [DecidableRel H.Adj], (supp H).card < (supp G).card →
      IsSPReduced H → H ≠ ⊥ →
        ∃ (X : Finset V) (B : SimpleGraph V) (_ : DecidableRel B.Adj), IsReductionSet H X B)
    {C : Set V} (hC : ∀ a b, G.Adj a b → (a ∈ C ↔ b ∈ C)) {u v : V} (hu : u ∈ supp G)
    (huC : u ∈ C) (hv : v ∈ supp G) (hvC : v ∉ C) :
    ∃ (X : Finset V) (B : SimpleGraph V) (_ : DecidableRel B.Adj), IsReductionSet G X B := by
  classical
  have hCc := adj_closed_compl hC
  have hGeq : restrict G C ⊔ restrict G Cᶜ = G := restrict_sup_restrict_compl hC
  obtain ⟨z₁, hz₁⟩ := mem_supp_iff_exists_adj.1 hu
  obtain ⟨z₂, hz₂⟩ := mem_supp_iff_exists_adj.1 hv
  have hne₁ : restrict G C ≠ ⊥ :=
    ne_bot_of_adj (G := restrict G C) ⟨hz₁, huC, (hC u z₁ hz₁).1 huC⟩
  have hne₂ : restrict G Cᶜ ≠ ⊥ :=
    ne_bot_of_adj (G := restrict G Cᶜ) ⟨hz₂, hvC, fun h => hvC ((hC v z₂ hz₂).2 h)⟩
  have hlt₁ : (supp (restrict G C)).card < (supp G).card := by
    refine Finset.card_lt_card
      ((Finset.ssubset_iff_of_subset (supp_subset_of_le (restrict_le G C))).2 ⟨v, hv, ?_⟩)
    intro h
    obtain ⟨z, hz⟩ := mem_supp_iff_exists_adj.1 h
    exact hvC hz.2.1
  have hlt₂ : (supp (restrict G Cᶜ)).card < (supp G).card := by
    refine Finset.card_lt_card
      ((Finset.ssubset_iff_of_subset (supp_subset_of_le (restrict_le G Cᶜ))).2 ⟨u, hu, ?_⟩)
    intro h
    obtain ⟨z, hz⟩ := mem_supp_iff_exists_adj.1 h
    exact hz.2.1 huC
  obtain ⟨X₁, B₁, instB₁, h₁⟩ := ih (restrict G C) hlt₁ (isSPReduced_restrict hG hC) hne₁
  obtain ⟨X₂, B₂, instB₂, h₂⟩ := ih (restrict G Cᶜ) hlt₂ (isSPReduced_restrict hG hCc) hne₂
  have hdisj : ∀ a, (∃ z, (restrict G C).Adj a z) → ∀ z, ¬ (restrict G Cᶜ).Adj a z :=
    fun a ⟨_, hz⟩ _ hz' => hz'.2.1 hz.2.1
  exact ⟨X₁ ∪ X₂, B₁ ⊔ B₂, inferInstance,
    IsReductionSet.congr_left _ _ hGeq (isReductionSet_sup h₁ h₂ hdisj)⟩

/-- Theorem 3.2 by strong induction on the size of the support. -/
theorem exists_reduction_set_of_card (n : ℕ) :
    ∀ (G : SimpleGraph V) [DecidableRel G.Adj], (supp G).card = n → IsSPReduced G → G ≠ ⊥ →
      ∃ (X : Finset V) (B : SimpleGraph V) (_ : DecidableRel B.Adj), IsReductionSet G X B := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
  intro G instG hn hG hne
  by_cases hbasic : IsBasic G
  · exact ⟨∅, G, instG, isReductionSet_empty hG hne hbasic⟩
  by_cases hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v
  · -- connected on its support and not basic
    obtain ⟨w, hmax, htie⟩ := exists_paper_choice G (supp_nonempty_of_not_isBasic G hbasic)
    have h4 : 4 ≤ G.degree w := four_le_degree_of_not_isBasic G hG hbasic hmax
    have hws : w ∈ supp G := mem_supp.2 (by omega)
    obtain ⟨Gs, hred, hGs⟩ := exists_reduced_reduct (isolate G w)
    let instGs : DecidableRel Gs.Adj := Classical.decRel _
    have hGsne : Gs ≠ ⊥ := nonbasic_reduct_ne_bot G hconn hbasic hws hred
    have hsub : supp Gs ⊆ supp G := hred.supp_subset.trans (supp_isolate_subset G w)
    have hwGs : w ∉ supp Gs := fun hw => by
      have := hred.supp_subset hw
      rw [mem_supp, degree_isolate_self] at this
      exact lt_irrefl 0 this
    have hlt : (supp Gs).card < n := by
      rw [← hn]
      exact Finset.card_lt_card ((Finset.ssubset_iff_of_subset hsub).2 ⟨w, hws, hwGs⟩)
    obtain ⟨Xs, B, instB, hB⟩ := ih _ hlt Gs rfl hGs hGsne
    exact ⟨insert w Xs, B, instB, isReductionSet_insert hG hconn hbasic hmax htie hred hGs hB⟩
  · -- the support is disconnected: split off the component of `u`
    push Not at hconn
    obtain ⟨u, hu, v, hv, huv⟩ := hconn
    exact exists_reduction_set_of_split hG
      (fun H instH hlt hH hHne => @ih _ (lt_of_lt_of_eq hlt hn) H instH rfl hH hHne)
      (adj_closed_supp_connectedComponent u) hu
      ((SimpleGraph.ConnectedComponent.mem_supp_iff _ _).2 rfl) hv
      (fun h => huv (SimpleGraph.ConnectedComponent.exact h).symm)

/-- **Theorem 3.2** (Edwards & McDermid 2015, p. 9; **T1**). For every graph with every degree
`0` or `≥ 3` and at least one edge there are `X ⊆ supp G` and a basic reduced graph `B ≠ ⊥`
with `G − X →* B` and `|X| + f⁻(B) ≤ f⁻(G)`. The paper's `r(G − X)` is "some reduced reduct `B`";
the instance on `B` is carried in the existential so that `f⁻(B)` can be written. -/
theorem exists_reduction_set (G : SimpleGraph V) [DecidableRel G.Adj] (hG : IsSPReduced G)
    (hne : G ≠ ⊥) :
    ∃ (X : Finset V) (B : SimpleGraph V) (_ : DecidableRel B.Adj), IsReductionSet G X B :=
  exists_reduction_set_of_card _ G rfl hG hne

/-- T1 in the conjunction form of report §2.6. -/
theorem exists_reduction_set_and (G : SimpleGraph V) [DecidableRel G.Adj] (hG : IsSPReduced G)
    (hne : G ≠ ⊥) :
    ∃ (X : Finset V) (B : SimpleGraph V) (_ : DecidableRel B.Adj),
      X ⊆ supp G ∧ SPReduces (isolateSet G X) B ∧ B ≠ ⊥ ∧ IsSPReduced B ∧ IsBasic B ∧
        (X.card : ℚ) + potentialMinus B ≤ potentialMinus G := by
  obtain ⟨X, B, inst, h⟩ := exists_reduction_set G hG hne
  exact ⟨X, B, inst, h.subset_supp, h.reduces, h.ne_bot, h.reduced, h.basic, h.card_add_le⟩

end MOSPFormalization.DegreeBound
