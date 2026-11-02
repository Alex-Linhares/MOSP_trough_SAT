/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The series-parallel reduction system, basic graphs, degree monotonicity, and the
commutation of deletion with reduction

Item 06 of loop0012 (`reports/edwards_mcdermid_plan.md` §0.5; `reports/edwards_mcdermid.md`
§2.1, §2.6 and §6): the four operations of Edwards & McDermid (2015, p. 8) on `SimpleGraph V`
with removed vertices isolated, their reflexive–transitive closure, "reduced" and "basic", and
the facts the step inequality (item 07) and Theorem 3.2 (item 08) need. Nothing here is about
pathwidth; no confluence fact is stated or used (the paper's Lemma 3.1, which cites Kneis et
al. 2009, is replaced by the local commutation lemma R3/R4).

* `ndeg G v` — the degree as `(G.neighborSet v).ncard`, needing no decidability instance
  (`ndeg_eq_degree` pins it to `G.degree v` under any `DecidableRel G.Adj`); `degSum G`.
* `isolateSet G X` — `G − X` for a finset `X` (`isolateSet_insert`, `isolateSet_singleton`);
  `restrict G S` — the edges inside `S`, every other vertex isolated.
* **The step.** `SPStep G v H` is one operation at `v`: `pendant` (degree 1; operation 2),
  `suppress` (degree 2, non-adjacent neighbours `x, y`; `H = (G − v) ⊔ edge x y`;
  operation 3), `triangle` (degree 2, adjacent neighbours; operation 4). Operation 1 (delete
  an isolated vertex) is the identity on `SimpleGraph V` and is absorbed by the reflexive
  closure (report §2.1 (1)). `SPReduces G H` is `Relation.ReflTransGen` of "some step";
  `IsSPReduced G` is "every degree `0` or `≥ 3`"; `IsBasic G` is "every non-trivial component
  `C` is cubic or has a vertex `v` with `SPReduces ((G|C) − v) ⊥`" (`⊥` = "empty").
* **R1** `SPStep.degSum_lt` (a step lowers the degree sum; `SPStep.ndeg_eq`: by 2 or 4), hence
  `exists_reduced_reduct : ∃ H, SPReduces G H ∧ IsSPReduced H`, and
  `IsSPReduced.eq_of_spReduces` (a reduced graph is a fixed point).
* **R2** `SPStep.ndeg_le`, `SPReduces.ndeg_le` (no degree ever rises), `SPReduces.degree_le`,
  `SPReduces.potential_le` (`f H ≤ f G`), `SPReduces.potential_sub_ge_of_isolated`
  (a vertex of degree `d` isolated by the reduction costs at least `g d`),
  `SPReduces.supp_subset`.
* **R3** `SPStep.isolate_comm`: a step at `v` and a deletion at `w ≠ v` commute — `H − w = G − w`
  (zero steps: `v` pendant at `w`) or `SPStep (G − w) v (H − w)` (one step, of the same kind
  when `w ∉ N(v)`, pendant when `w ∈ N(v)`; the added edge `xy` vanishes with `w ∈ {x, y}`).
  `SPStep.isolateSet_comm` is the finset form (`v ∉ X`).
* **R4** `SPReduces.isolateSet_comm`: `SPReduces G H` and `X ⊆ supp H` ⇒
  `SPReduces (G − X) (H − X)`; `SPReduces.isolate_comm` for one vertex. This is what the
  paper takes from Lemma 3.1: an acted vertex ends isolated, so `X ⊆ supp H` keeps `X` clear of
  every step.
* **R5** `SPStep.sup_of_disjoint`, `SPReduces.sup_of_disjoint`: a step acts inside its
  component — with `K` supported away from `G`, `SPReduces G H → SPReduces (G ⊔ K) (H ⊔ K)`.
* `restrict` lemmas for item 08's disconnected case: `restrict_sup_restrict_compl` (when `S`
  is closed under adjacency), `isolate_restrict`, `restrict_eq_self`.

Every statement was checked by brute force in the form proved here before it was stated
(`reports/scratch/edwards_mcdermid/06_reduction/check_r3.py`: every graph to 9 vertices, every
(graph, step, `w`) for R3 with the constructor kind the proof produces, random finsets for R3X
and R4, random disjoint `K` for R5; item 02 had R1–R5 on every graph to 9). Not here: R6
(`pw G ≤ pw H + 1` per step; optional and not needed by the assembly), uniqueness of the reduct
(measured in item 02, not needed), and any statement about series-parallel graphs.
-/
import MOSPFormalization.DegreeBound.Potential

set_option linter.unusedSectionVars false

namespace MOSPFormalization.DegreeBound

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### The instance-free degree -/

/-- The degree with no decidability instance: the `ncard` of the neighbour set. -/
noncomputable def ndeg (G : SimpleGraph V) (v : V) : ℕ := (G.neighborSet v).ncard

theorem ndeg_eq_degree (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    ndeg G v = G.degree v := by
  rw [ndeg, Set.ncard_eq_toFinset_card', ← SimpleGraph.neighborFinset_def,
    SimpleGraph.card_neighborFinset_eq_degree]

theorem ndeg_eq_zero_iff {G : SimpleGraph V} {v : V} : ndeg G v = 0 ↔ ∀ z, ¬ G.Adj v z := by
  rw [ndeg, Set.ncard_eq_zero (Set.toFinite _), Set.eq_empty_iff_forall_notMem]
  simp only [SimpleGraph.mem_neighborSet]

theorem ndeg_pos_of_adj {G : SimpleGraph V} {v z : V} (h : G.Adj v z) : 0 < ndeg G v := by
  rw [ndeg, Set.ncard_pos (Set.toFinite _)]
  exact ⟨z, h⟩

theorem ndeg_le_of_le {G G' : SimpleGraph V} (h : G ≤ G') (u : V) : ndeg G u ≤ ndeg G' u :=
  Set.ncard_le_ncard (fun _ hz => h hz) (Set.toFinite _)

theorem ndeg_bot (v : V) : ndeg (⊥ : SimpleGraph V) v = 0 := by
  rw [ndeg_eq_zero_iff]; simp

theorem ndeg_eq_one_iff {G : SimpleGraph V} {v : V} :
    ndeg G v = 1 ↔ ∃ x, G.Adj v x ∧ ∀ z, G.Adj v z → z = x := by
  rw [ndeg, Set.ncard_eq_one]
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨x, ?_, fun z hz => ?_⟩
    · show x ∈ G.neighborSet v
      rw [hx]; exact Set.mem_singleton x
    · have : z ∈ G.neighborSet v := hz
      rw [hx] at this; exact this
  · rintro ⟨x, hx, hall⟩
    refine ⟨x, Set.ext fun z => ⟨fun hz => hall z hz, fun hz => ?_⟩⟩
    rw [Set.mem_singleton_iff] at hz; subst hz; exact hx

theorem ndeg_eq_two_iff {G : SimpleGraph V} {v : V} :
    ndeg G v = 2 ↔ ∃ x y, x ≠ y ∧ G.Adj v x ∧ G.Adj v y ∧ ∀ z, G.Adj v z → z = x ∨ z = y := by
  rw [ndeg, Set.ncard_eq_two]
  constructor
  · rintro ⟨x, y, hxy, hN⟩
    refine ⟨x, y, hxy, ?_, ?_, fun z hz => ?_⟩
    · show x ∈ G.neighborSet v
      rw [hN]; exact Set.mem_insert x {y}
    · show y ∈ G.neighborSet v
      rw [hN]; exact Set.mem_insert_of_mem x (Set.mem_singleton y)
    · have : z ∈ G.neighborSet v := hz
      rw [hN] at this; simpa using this
  · rintro ⟨x, y, hxy, hx, hy, hall⟩
    refine ⟨x, y, hxy, Set.ext fun z => ⟨fun hz => by simpa using hall z hz, fun hz => ?_⟩⟩
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hz
    rcases hz with rfl | rfl
    · exact hx
    · exact hy

/-- The degree sum, the measure a step lowers. -/
noncomputable def degSum (G : SimpleGraph V) : ℕ := ∑ v, ndeg G v

/-! ### Deleting one vertex, a finset of vertices; restricting to a set -/

theorem isolate_comm (G : SimpleGraph V) (a b : V) :
    isolate (isolate G a) b = isolate (isolate G b) a := by
  ext x y; simp only [isolate_adj]; tauto

theorem isolate_sup (G₁ G₂ : SimpleGraph V) (w : V) :
    isolate (G₁ ⊔ G₂) w = isolate G₁ w ⊔ isolate G₂ w := by
  ext x y; simp only [isolate_adj, SimpleGraph.sup_adj]; tauto

theorem isolate_edge_left (x y : V) : isolate (SimpleGraph.edge x y) x = ⊥ := by
  ext a b; simp only [isolate_adj, SimpleGraph.edge_adj, SimpleGraph.bot_adj, iff_false]
  rintro ⟨⟨⟨rfl, rfl⟩ | ⟨rfl, rfl⟩, -⟩, ha, hb⟩
  · exact ha rfl
  · exact hb rfl

theorem isolate_edge_right (x y : V) : isolate (SimpleGraph.edge x y) y = ⊥ := by
  rw [SimpleGraph.edge_comm, isolate_edge_left]

theorem isolate_edge_of_ne {x y w : V} (hx : w ≠ x) (hy : w ≠ y) :
    isolate (SimpleGraph.edge x y) w = SimpleGraph.edge x y := by
  ext a b; simp only [isolate_adj, SimpleGraph.edge_adj]
  constructor
  · exact fun h => h.1
  · rintro ⟨⟨rfl, rfl⟩ | ⟨rfl, rfl⟩, hab⟩
    · exact ⟨⟨Or.inl ⟨rfl, rfl⟩, hab⟩, hx.symm, hy.symm⟩
    · exact ⟨⟨Or.inr ⟨rfl, rfl⟩, hab⟩, hy.symm, hx.symm⟩

theorem isolate_eq_self_of_forall_not_adj {G : SimpleGraph V} {v : V} (h : ∀ z, ¬ G.Adj v z) :
    isolate G v = G := by
  ext a b; simp only [isolate_adj]
  constructor
  · exact fun h => h.1
  · intro hab
    refine ⟨hab, ?_, ?_⟩
    · rintro rfl; exact h b hab
    · rintro rfl; exact h a hab.symm

theorem isolate_eq_self_of_ndeg_eq_zero {G : SimpleGraph V} {v : V} (h : ndeg G v = 0) :
    isolate G v = G :=
  isolate_eq_self_of_forall_not_adj (ndeg_eq_zero_iff.1 h)

theorem neighborSet_isolate (G : SimpleGraph V) (w u : V) :
    (isolate G w).neighborSet u = if u = w then ∅ else G.neighborSet u \ {w} := by
  ext z
  simp only [SimpleGraph.mem_neighborSet, isolate_adj]
  split_ifs with h
  · subst h; simp
  · simp [h]

theorem ndeg_isolate_le (G : SimpleGraph V) (w u : V) : ndeg (isolate G w) u ≤ ndeg G u :=
  ndeg_le_of_le (isolate_le G w) u

theorem ndeg_isolate_self (G : SimpleGraph V) (w : V) : ndeg (isolate G w) w = 0 := by
  rw [ndeg_eq_zero_iff]; intro z hz; exact hz.2.1 rfl

/-- `G − X`: every edge at a vertex of `X` deleted, `X` kept isolated. -/
def isolateSet (G : SimpleGraph V) (X : Finset V) : SimpleGraph V where
  Adj a b := G.Adj a b ∧ a ∉ X ∧ b ∉ X
  symm := ⟨fun _ _ ⟨h, ha, hb⟩ => ⟨h.symm, hb, ha⟩⟩
  loopless := ⟨fun a h => G.loopless.irrefl a h.1⟩

instance instDecidableRelIsolateSetAdj (G : SimpleGraph V) [DecidableRel G.Adj] (X : Finset V) :
    DecidableRel (isolateSet G X).Adj :=
  fun a b => inferInstanceAs (Decidable (G.Adj a b ∧ a ∉ X ∧ b ∉ X))

theorem isolateSet_adj (G : SimpleGraph V) (X : Finset V) (a b : V) :
    (isolateSet G X).Adj a b ↔ G.Adj a b ∧ a ∉ X ∧ b ∉ X := Iff.rfl

theorem isolateSet_le (G : SimpleGraph V) (X : Finset V) : isolateSet G X ≤ G :=
  fun _ _ h => h.1

theorem isolateSet_empty (G : SimpleGraph V) : isolateSet G ∅ = G := by
  ext a b; simp [isolateSet_adj]

theorem isolateSet_singleton (G : SimpleGraph V) (w : V) : isolateSet G {w} = isolate G w := by
  ext a b; simp [isolateSet_adj, isolate_adj]

theorem isolateSet_insert (G : SimpleGraph V) (w : V) (X : Finset V) :
    isolateSet G (insert w X) = isolate (isolateSet G X) w := by
  ext a b; simp only [isolateSet_adj, isolate_adj, Finset.mem_insert, not_or]; tauto

theorem isolateSet_comm_isolate (G : SimpleGraph V) (X : Finset V) (w : V) :
    isolateSet (isolate G w) X = isolate (isolateSet G X) w := by
  ext a b; simp only [isolateSet_adj, isolate_adj]; tauto

theorem ndeg_isolateSet_le (G : SimpleGraph V) (X : Finset V) (u : V) :
    ndeg (isolateSet G X) u ≤ ndeg G u :=
  ndeg_le_of_le (isolateSet_le G X) u

/-- `G|S`: the edges inside `S`, every other vertex isolated (the paper's component `G_i`
kept on the vertex type `V`). -/
def restrict (G : SimpleGraph V) (S : Set V) : SimpleGraph V where
  Adj a b := G.Adj a b ∧ a ∈ S ∧ b ∈ S
  symm := ⟨fun _ _ ⟨h, ha, hb⟩ => ⟨h.symm, hb, ha⟩⟩
  loopless := ⟨fun a h => G.loopless.irrefl a h.1⟩

theorem restrict_adj (G : SimpleGraph V) (S : Set V) (a b : V) :
    (restrict G S).Adj a b ↔ G.Adj a b ∧ a ∈ S ∧ b ∈ S := Iff.rfl

theorem restrict_le (G : SimpleGraph V) (S : Set V) : restrict G S ≤ G := fun _ _ h => h.1

theorem restrict_eq_self {G : SimpleGraph V} {S : Set V} (h : ∀ a b, G.Adj a b → a ∈ S ∧ b ∈ S) :
    restrict G S = G := by
  ext a b; simp only [restrict_adj]
  exact ⟨fun h => h.1, fun hab => ⟨hab, h a b hab⟩⟩

/-- When no edge crosses `S`, `G` is the disjoint union of `G|S` and `G|Sᶜ`. -/
theorem restrict_sup_restrict_compl {G : SimpleGraph V} {S : Set V}
    (h : ∀ a b, G.Adj a b → (a ∈ S ↔ b ∈ S)) : restrict G S ⊔ restrict G Sᶜ = G := by
  ext a b
  simp only [SimpleGraph.sup_adj, restrict_adj, Set.mem_compl_iff]
  constructor
  · rintro (⟨hab, -, -⟩ | ⟨hab, -, -⟩) <;> exact hab
  · intro hab
    by_cases ha : a ∈ S
    · exact Or.inl ⟨hab, ha, (h a b hab).1 ha⟩
    · exact Or.inr ⟨hab, ha, fun hb => ha ((h a b hab).2 hb)⟩

theorem isolate_restrict (G : SimpleGraph V) (S : Set V) (v : V) :
    isolate (restrict G S) v = restrict (isolate G v) S := by
  ext a b; simp only [isolate_adj, restrict_adj]; tauto

theorem restrict_adj_imp_not_adj_compl {G : SimpleGraph V} {S : Set V} {a b z : V}
    (h : (restrict G Sᶜ).Adj a b) : ¬ (restrict G S).Adj a z :=
  fun h' => h.2.1 h'.2.1

/-! ### The step relation -/

/-- One series-parallel operation at `v` (Edwards & McDermid p. 8, operations 2–4; operation
1 is the identity here). The removed vertex `v` is left isolated. -/
inductive SPStep (G : SimpleGraph V) (v : V) : SimpleGraph V → Prop
  /-- Operation 2: `v` has the single neighbour `x`; delete `v`. -/
  | pendant {x : V} (hx : G.Adj v x) (hall : ∀ z, G.Adj v z → z = x) : SPStep G v (isolate G v)
  /-- Operation 3: `v` has exactly the two non-adjacent neighbours `x ≠ y`; delete `v` and
  add the edge `xy`. -/
  | suppress {x y : V} (hx : G.Adj v x) (hy : G.Adj v y) (hxy : x ≠ y)
      (hall : ∀ z, G.Adj v z → z = x ∨ z = y) (hnadj : ¬ G.Adj x y) :
      SPStep G v (isolate G v ⊔ SimpleGraph.edge x y)
  /-- Operation 4: `v` has exactly the two adjacent neighbours `x ≠ y`; delete `v`. -/
  | triangle {x y : V} (hx : G.Adj v x) (hy : G.Adj v y) (hxy : x ≠ y)
      (hall : ∀ z, G.Adj v z → z = x ∨ z = y) (hadj : G.Adj x y) : SPStep G v (isolate G v)

/-- The reflexive–transitive closure of "some step". `SPReduces G ⊥` is the paper's
"`r(G)` is empty". -/
def SPReduces (G H : SimpleGraph V) : Prop :=
  Relation.ReflTransGen (fun G H => ∃ v, SPStep G v H) G H

/-- Every degree is `0` or at least `3`: no operation applies. -/
def IsSPReduced (G : SimpleGraph V) : Prop := ∀ v, ndeg G v = 0 ∨ 3 ≤ ndeg G v

/-- Basic (paper p. 8): every non-trivial component `C` is cubic, or some `v ∈ C` has
`r((G|C) − v)` empty. -/
def IsBasic (G : SimpleGraph V) : Prop :=
  ∀ C : G.ConnectedComponent, (∃ v ∈ C.supp, 0 < ndeg G v) →
    (∀ v ∈ C.supp, ndeg G v = 3) ∨ ∃ v ∈ C.supp, SPReduces (isolate (restrict G C.supp) v) ⊥

theorem isSPReduced_iff (G : SimpleGraph V) [DecidableRel G.Adj] :
    IsSPReduced G ↔ ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v := by
  simp only [IsSPReduced, ndeg_eq_degree]

theorem isSPReduced_bot : IsSPReduced (⊥ : SimpleGraph V) := fun v => Or.inl (ndeg_bot v)

theorem isBasic_bot : IsBasic (⊥ : SimpleGraph V) := by
  rintro C ⟨v, -, hv⟩
  rw [ndeg_bot] at hv
  exact absurd hv (lt_irrefl 0)

namespace SPReduces

theorem refl (G : SimpleGraph V) : SPReduces G G := Relation.ReflTransGen.refl

theorem trans {G H K : SimpleGraph V} (h₁ : SPReduces G H) (h₂ : SPReduces H K) :
    SPReduces G K := Relation.ReflTransGen.trans h₁ h₂

theorem single {G H : SimpleGraph V} {v : V} (h : SPStep G v H) : SPReduces G H :=
  Relation.ReflTransGen.single ⟨v, h⟩

theorem head {G H K : SimpleGraph V} {v : V} (h : SPStep G v H) (h' : SPReduces H K) :
    SPReduces G K := Relation.ReflTransGen.head ⟨v, h⟩ h'

theorem tail {G H K : SimpleGraph V} {v : V} (h : SPReduces G H) (h' : SPStep H v K) :
    SPReduces G K := Relation.ReflTransGen.tail h ⟨v, h'⟩

end SPReduces

/-! ### One step: degrees (R1, R2) -/

namespace SPStep

variable {G H : SimpleGraph V} {v : V}

/-- After a step at `v`, `v` is isolated. -/
theorem not_adj (h : SPStep G v H) (z : V) : ¬ H.Adj v z := by
  cases h with
  | pendant hx hall => exact fun h' => h'.2.1 rfl
  | triangle hx hy hxy hall hadj => exact fun h' => h'.2.1 rfl
  | @suppress x y hx hy hxy hall hnadj =>
    rintro (h' | h')
    · exact h'.2.1 rfl
    · rw [SimpleGraph.edge_adj] at h'
      rcases h'.1 with ⟨rfl, -⟩ | ⟨rfl, -⟩
      · exact G.ne_of_adj hx rfl
      · exact G.ne_of_adj hy rfl

theorem ndeg_self (h : SPStep G v H) : ndeg H v = 0 :=
  ndeg_eq_zero_iff.2 h.not_adj

theorem exists_adj (h : SPStep G v H) : ∃ x, G.Adj v x := by
  cases h with
  | pendant hx _ => exact ⟨_, hx⟩
  | suppress hx _ _ _ _ => exact ⟨_, hx⟩
  | triangle hx _ _ _ _ => exact ⟨_, hx⟩

theorem ndeg_pos (h : SPStep G v H) : 0 < ndeg G v :=
  let ⟨_, hx⟩ := h.exists_adj; ndeg_pos_of_adj hx

/-- A step acts at a vertex of degree 1 or 2. -/
theorem ndeg_eq (h : SPStep G v H) : ndeg G v = 1 ∨ ndeg G v = 2 := by
  cases h with
  | pendant hx hall => exact Or.inl (ndeg_eq_one_iff.2 ⟨_, hx, hall⟩)
  | suppress hx hy hxy hall _ => exact Or.inr (ndeg_eq_two_iff.2 ⟨_, _, hxy, hx, hy, hall⟩)
  | triangle hx hy hxy hall _ => exact Or.inr (ndeg_eq_two_iff.2 ⟨_, _, hxy, hx, hy, hall⟩)

/-- The degree at `x` after suppressing `v` (which was adjacent to `x`) and adding `xy`. -/
theorem ndeg_isolate_sup_edge_left (G : SimpleGraph V) {v x y : V} (hx : G.Adj v x) (hxy : x ≠ y) :
    ndeg (isolate G v ⊔ SimpleGraph.edge x y) x ≤ ndeg G x := by
  have hsub : (isolate G v ⊔ SimpleGraph.edge x y).neighborSet x ⊆
      (G.neighborSet x \ {v}) ∪ {y} := by
    intro z hz
    simp only [SimpleGraph.mem_neighborSet, SimpleGraph.sup_adj, isolate_adj,
      SimpleGraph.edge_adj] at hz
    simp only [Set.mem_union, Set.mem_sdiff, SimpleGraph.mem_neighborSet, Set.mem_singleton_iff]
    rcases hz with ⟨h, -, hzv⟩ | ⟨⟨-, rfl⟩ | ⟨rfl, -⟩, -⟩
    · exact Or.inl ⟨h, hzv⟩
    · exact Or.inr rfl
    · exact absurd rfl hxy
  have hv : v ∈ G.neighborSet x := hx.symm
  calc ndeg (isolate G v ⊔ SimpleGraph.edge x y) x
      ≤ ((G.neighborSet x \ {v}) ∪ {y}).ncard := Set.ncard_le_ncard hsub (Set.toFinite _)
    _ ≤ (G.neighborSet x \ {v}).ncard + ({y} : Set V).ncard := Set.ncard_union_le _ _
    _ = (G.neighborSet x \ {v}).ncard + 1 := by rw [Set.ncard_singleton]
    _ = ndeg G x := Set.ncard_sdiff_singleton_add_one hv (Set.toFinite _)

theorem ndeg_isolate_sup_edge_of_ne (G : SimpleGraph V) {v x y u : V} (hux : u ≠ x) (huy : u ≠ y) :
    ndeg (isolate G v ⊔ SimpleGraph.edge x y) u ≤ ndeg G u := by
  apply Set.ncard_le_ncard _ (Set.toFinite _)
  intro z hz
  simp only [SimpleGraph.mem_neighborSet, SimpleGraph.sup_adj, isolate_adj,
    SimpleGraph.edge_adj] at hz
  rcases hz with ⟨h, -, -⟩ | ⟨⟨rfl, -⟩ | ⟨rfl, -⟩, -⟩
  · exact h
  · exact absurd rfl hux
  · exact absurd rfl huy

/-- **R2, one step**: no degree rises. -/
theorem ndeg_le (h : SPStep G v H) (u : V) : ndeg H u ≤ ndeg G u := by
  cases h with
  | pendant _ _ => exact ndeg_isolate_le G v u
  | triangle _ _ _ _ _ => exact ndeg_isolate_le G v u
  | @suppress x y hx hy hxy hall hnadj =>
    by_cases hux : u = x
    · subst hux; exact ndeg_isolate_sup_edge_left G hx hxy
    by_cases huy : u = y
    · subst huy
      rw [SimpleGraph.edge_comm]
      exact ndeg_isolate_sup_edge_left G hy hxy.symm
    exact ndeg_isolate_sup_edge_of_ne G hux huy

/-- **R1**: a step lowers the degree sum. -/
theorem degSum_lt (h : SPStep G v H) : degSum H < degSum G :=
  Finset.sum_lt_sum (fun u _ => h.ndeg_le u) ⟨v, Finset.mem_univ v, by
    rw [h.ndeg_self]; exact h.ndeg_pos⟩

end SPStep

/-! ### Reduced graphs: termination and fixed points (R1′) -/

theorem not_isSPReduced_iff {G : SimpleGraph V} :
    ¬ IsSPReduced G ↔ ∃ v, ndeg G v = 1 ∨ ndeg G v = 2 := by
  simp only [IsSPReduced, not_forall, not_or]
  constructor
  · rintro ⟨v, h0, h3⟩; exact ⟨v, by omega⟩
  · rintro ⟨v, h⟩; exact ⟨v, by omega, by omega⟩

/-- A vertex of degree 1 or 2 admits a step. -/
theorem exists_spStep_of_ndeg {G : SimpleGraph V} {v : V} (h : ndeg G v = 1 ∨ ndeg G v = 2) :
    ∃ H, SPStep G v H := by
  rcases h with h | h
  · obtain ⟨x, hx, hall⟩ := ndeg_eq_one_iff.1 h
    exact ⟨_, SPStep.pendant hx hall⟩
  · obtain ⟨x, y, hxy, hx, hy, hall⟩ := ndeg_eq_two_iff.1 h
    by_cases hadj : G.Adj x y
    · exact ⟨_, SPStep.triangle hx hy hxy hall hadj⟩
    · exact ⟨_, SPStep.suppress hx hy hxy hall hadj⟩

theorem exists_spStep_of_not_isSPReduced {G : SimpleGraph V} (h : ¬ IsSPReduced G) :
    ∃ v H, SPStep G v H := by
  obtain ⟨v, hv⟩ := not_isSPReduced_iff.1 h
  obtain ⟨H, hH⟩ := exists_spStep_of_ndeg hv
  exact ⟨v, H, hH⟩

/-- A reduced graph admits no step. -/
theorem IsSPReduced.not_spStep {G H : SimpleGraph V} (hG : IsSPReduced G) {v : V} :
    ¬ SPStep G v H := fun h => by
  rcases hG v with h0 | h3 <;> rcases h.ndeg_eq with h1 | h2 <;> omega

/-- **R1′**: every graph reduces to a reduced graph. -/
theorem exists_reduced_reduct (G : SimpleGraph V) : ∃ H, SPReduces G H ∧ IsSPReduced H := by
  induction' hn : degSum G using Nat.strong_induction_on with n ih generalizing G
  by_cases hred : IsSPReduced G
  · exact ⟨G, SPReduces.refl G, hred⟩
  · obtain ⟨v, H, hstep⟩ := exists_spStep_of_not_isSPReduced hred
    obtain ⟨K, hK, hKred⟩ := ih (degSum H) (hn ▸ hstep.degSum_lt) H rfl
    exact ⟨K, SPReduces.head hstep hK, hKred⟩

/-- A reduced graph is a fixed point of reduction. -/
theorem IsSPReduced.eq_of_spReduces {G H : SimpleGraph V} (hG : IsSPReduced G)
    (h : SPReduces G H) : H = G := by
  rcases Relation.ReflTransGen.cases_head h with rfl | ⟨K, ⟨v, hstep⟩, -⟩
  · rfl
  · exact absurd hstep hG.not_spStep

/-! ### Reduction sequences: degrees and the potential (R2) -/

namespace SPReduces

variable {G H : SimpleGraph V}

/-- **R2**: no degree ever rises along a reduction. -/
theorem ndeg_le (h : SPReduces G H) (u : V) : ndeg H u ≤ ndeg G u := by
  induction h with
  | refl => exact le_rfl
  | tail _ hstep ih =>
    obtain ⟨v, hstep⟩ := hstep
    exact (hstep.ndeg_le u).trans ih

theorem degree_le [DecidableRel G.Adj] [DecidableRel H.Adj] (h : SPReduces G H) (u : V) :
    H.degree u ≤ G.degree u := by
  rw [← ndeg_eq_degree, ← ndeg_eq_degree]; exact h.ndeg_le u

theorem ndeg_eq_zero (h : SPReduces G H) {u : V} (hu : ndeg G u = 0) : ndeg H u = 0 :=
  Nat.le_zero.1 (hu ▸ h.ndeg_le u)

theorem not_adj_of_not_adj (h : SPReduces G H) {u : V} (hu : ∀ z, ¬ G.Adj u z) (z : V) :
    ¬ H.Adj u z :=
  ndeg_eq_zero_iff.1 (h.ndeg_eq_zero (ndeg_eq_zero_iff.2 hu)) z

theorem supp_subset [DecidableRel G.Adj] [DecidableRel H.Adj] (h : SPReduces G H) :
    supp H ⊆ supp G := by
  intro u hu
  rw [mem_supp] at hu ⊢
  exact lt_of_lt_of_le hu (h.degree_le u)

/-- **R2 for the potential**: `f H ≤ f G`. -/
theorem potential_le [DecidableRel G.Adj] [DecidableRel H.Adj] (h : SPReduces G H) :
    potential H ≤ potential G :=
  Finset.sum_le_sum fun u _ => g_monotone (h.degree_le u)

/-- A vertex of degree `d` in `G` that the reduction isolates costs at least `g d`. -/
theorem potential_sub_ge_of_isolated [DecidableRel G.Adj] [DecidableRel H.Adj]
    (h : SPReduces G H) {u : V} (hu : H.degree u = 0) :
    g (G.degree u) ≤ potential G - potential H := by
  unfold potential
  rw [← Finset.sum_sub_distrib]
  have hterm : g (G.degree u) = g (G.degree u) - g (H.degree u) := by rw [hu, g_zero, sub_zero]
  rw [hterm]
  exact Finset.single_le_sum (f := fun w => g (G.degree w) - g (H.degree w))
    (fun w _ => sub_nonneg.2 (g_monotone (h.degree_le w))) (Finset.mem_univ u)

end SPReduces

/-! ### Commutation of deletion with a step (R3) and with a reduction (R4) -/

namespace SPStep

variable {G H : SimpleGraph V} {v : V}

/-- **R3**: a step at `v` and the deletion of `w ≠ v` commute, in zero steps (`v` pendant at
`w`) or one (the same kind of step when `w ∉ N(v)`; a pendant deletion when `w ∈ N(v)`; the
added edge `xy` of a suppression vanishes with `w ∈ {x, y}`). -/
theorem isolate_comm (h : SPStep G v H) {w : V} (hw : w ≠ v) :
    isolate H w = isolate G w ∨ SPStep (isolate G w) v (isolate H w) := by
  cases h with
  | @pendant x hx hall =>
    by_cases hwx : w = x
    · subst hwx
      left
      rw [MOSPFormalization.DegreeBound.isolate_comm]
      apply isolate_eq_self_of_forall_not_adj
      intro z hz
      exact hz.2.2 (hall z hz.1)
    · right
      rw [MOSPFormalization.DegreeBound.isolate_comm]
      exact SPStep.pendant (x := x) ⟨hx, hw.symm, Ne.symm hwx⟩ (fun z hz => hall z hz.1)
  | @triangle x y hx hy hxy hall hadj =>
    right
    rw [MOSPFormalization.DegreeBound.isolate_comm]
    by_cases hwx : w = x
    · subst hwx
      refine SPStep.pendant (x := y) ⟨hy, hw.symm, hxy.symm⟩ (fun z hz => ?_)
      rcases hall z hz.1 with rfl | rfl
      · exact absurd rfl hz.2.2
      · rfl
    by_cases hwy : w = y
    · subst hwy
      refine SPStep.pendant (x := x) ⟨hx, hw.symm, hxy⟩ (fun z hz => ?_)
      rcases hall z hz.1 with rfl | rfl
      · rfl
      · exact absurd rfl hz.2.2
    exact SPStep.triangle ⟨hx, hw.symm, Ne.symm hwx⟩ ⟨hy, hw.symm, Ne.symm hwy⟩ hxy
      (fun z hz => hall z hz.1) ⟨hadj, Ne.symm hwx, Ne.symm hwy⟩
  | @suppress x y hx hy hxy hall hnadj =>
    right
    rw [isolate_sup]
    by_cases hwx : w = x
    · subst hwx
      rw [isolate_edge_left, sup_bot_eq, MOSPFormalization.DegreeBound.isolate_comm]
      refine SPStep.pendant (x := y) ⟨hy, hw.symm, hxy.symm⟩ (fun z hz => ?_)
      rcases hall z hz.1 with rfl | rfl
      · exact absurd rfl hz.2.2
      · rfl
    by_cases hwy : w = y
    · subst hwy
      rw [isolate_edge_right, sup_bot_eq, MOSPFormalization.DegreeBound.isolate_comm]
      refine SPStep.pendant (x := x) ⟨hx, hw.symm, hxy⟩ (fun z hz => ?_)
      rcases hall z hz.1 with rfl | rfl
      · rfl
      · exact absurd rfl hz.2.2
    rw [isolate_edge_of_ne hwx hwy, MOSPFormalization.DegreeBound.isolate_comm]
    exact SPStep.suppress ⟨hx, hw.symm, Ne.symm hwx⟩ ⟨hy, hw.symm, Ne.symm hwy⟩ hxy
      (fun z hz => hall z hz.1) (fun h' => hnadj h'.1)

/-- **R3, finset form**: a step at `v ∉ X` and the deletion of `X` commute in zero or one step. -/
theorem isolateSet_comm (h : SPStep G v H) {X : Finset V} (hv : v ∉ X) :
    isolateSet H X = isolateSet G X ∨ SPStep (isolateSet G X) v (isolateSet H X) := by
  induction X using Finset.induction_on with
  | empty => right; rw [isolateSet_empty, isolateSet_empty]; exact h
  | insert w X hwX ih =>
    have hwv : w ≠ v := fun e => hv (e ▸ Finset.mem_insert_self w X)
    have hvX : v ∉ X := fun e => hv (Finset.mem_insert_of_mem e)
    rw [isolateSet_insert, isolateSet_insert]
    rcases ih hvX with heq | hstep
    · left; rw [heq]
    · exact hstep.isolate_comm hwv

/-- **R5**: a step acts inside its component — adding a graph `K` whose edges avoid the
support of `G` commutes with the step. -/
theorem sup_of_disjoint (h : SPStep G v H) {K : SimpleGraph V}
    (hK : ∀ a b, K.Adj a b → ∀ z, ¬ G.Adj a z) : SPStep (G ⊔ K) v (H ⊔ K) := by
  have hKv : ∀ z, ¬ K.Adj v z := fun z hz => by
    obtain ⟨x, hx⟩ := h.exists_adj
    exact hK v z hz x hx
  have hiso : isolate (G ⊔ K) v = isolate G v ⊔ K := by
    rw [isolate_sup, isolate_eq_self_of_forall_not_adj hKv]
  have hadjG : ∀ z, (G ⊔ K).Adj v z ↔ G.Adj v z := fun z =>
    ⟨fun h' => h'.resolve_right (hKv z), Or.inl⟩
  cases h with
  | @pendant x hx hall =>
    rw [← hiso]
    exact SPStep.pendant (x := x) (Or.inl hx) (fun z hz => hall z ((hadjG z).1 hz))
  | @triangle x y hx hy hxy hall hadj =>
    rw [← hiso]
    exact SPStep.triangle (Or.inl hx) (Or.inl hy) hxy (fun z hz => hall z ((hadjG z).1 hz))
      (Or.inl hadj)
  | @suppress x y hx hy hxy hall hnadj =>
    rw [sup_right_comm, ← hiso]
    refine SPStep.suppress (Or.inl hx) (Or.inl hy) hxy (fun z hz => hall z ((hadjG z).1 hz)) ?_
    rintro (h' | h')
    · exact hnadj h'
    · exact hK x y h' v hx.symm

end SPStep

namespace SPReduces

variable {G H : SimpleGraph V}

/-- An acted-on vertex ends isolated: if `w` has a neighbour in `H` then no step of
`SPReduces G H` acts at `w`. The form R4 needs. -/
theorem not_spStep_of_adj {K : SimpleGraph V} (h : SPReduces K H) {w z : V} (hz : H.Adj w z)
    {G' : SimpleGraph V} (hstep : SPStep G' w K) : False := by
  have h0 : ndeg H w = 0 := h.ndeg_eq_zero hstep.ndeg_self
  exact absurd h0 (Nat.pos_iff_ne_zero.1 (ndeg_pos_of_adj hz))

/-- **R4, finset form** (what the paper takes from its Lemma 3.1): a reduction `G →* H` and
the deletion of a finset `X ⊆ supp H` commute: `G − X →* H − X`. -/
theorem isolateSet_comm (h : SPReduces G H) {X : Finset V} (hX : ∀ w ∈ X, ∃ z, H.Adj w z) :
    SPReduces (isolateSet G X) (isolateSet H X) := by
  unfold SPReduces at h
  induction h using Relation.ReflTransGen.head_induction_on with
  | refl => exact SPReduces.refl _
  | @head a c hstep hrest ih =>
    obtain ⟨v, hv⟩ := hstep
    have hvX : v ∉ X := fun hvX => by
      obtain ⟨z, hz⟩ := hX v hvX
      exact SPReduces.not_spStep_of_adj hrest hz hv
    rcases hv.isolateSet_comm hvX with heq | hstep'
    · rw [← heq]; exact ih
    · exact SPReduces.head hstep' ih

/-- **R4, one vertex**: `SPReduces G H` and `w` non-isolated in `H` ⇒
`SPReduces (G − w) (H − w)`. -/
theorem isolate_comm (h : SPReduces G H) {w : V} (hw : ∃ z, H.Adj w z) :
    SPReduces (isolate G w) (isolate H w) := by
  rw [← isolateSet_singleton, ← isolateSet_singleton]
  exact h.isolateSet_comm (fun u hu => by rw [Finset.mem_singleton] at hu; subst hu; exact hw)

/-- The other case of R4's hypothesis: a vertex isolated in `G` is isolated in `H`, and both
deletions are the identity. -/
theorem isolate_comm_of_isolated (h : SPReduces G H) {w : V} (hw : ∀ z, ¬ G.Adj w z) :
    SPReduces (isolate G w) (isolate H w) := by
  rw [isolate_eq_self_of_forall_not_adj hw,
    isolate_eq_self_of_forall_not_adj (h.not_adj_of_not_adj hw)]
  exact h

/-- **R5, lifted**: `SPReduces G H → SPReduces (G ⊔ K) (H ⊔ K)` when `K`'s edges avoid the
support of `G`. -/
theorem sup_of_disjoint (h : SPReduces G H) {K : SimpleGraph V}
    (hK : ∀ a b, K.Adj a b → ∀ z, ¬ G.Adj a z) : SPReduces (G ⊔ K) (H ⊔ K) := by
  unfold SPReduces at h
  induction h with
  | refl => exact SPReduces.refl _
  | @tail b c hGb hstep ih =>
    obtain ⟨v, hv⟩ := hstep
    have hKb : ∀ a b', K.Adj a b' → ∀ z, ¬ b.Adj a z := fun a b' hab' =>
      SPReduces.not_adj_of_not_adj hGb (hK a b' hab')
    exact SPReduces.tail ih (hv.sup_of_disjoint hKb)

/-- R5 in the vocabulary of supports. -/
theorem sup_of_disjoint_supp [DecidableRel G.Adj] (h : SPReduces G H) {K : SimpleGraph V}
    [DecidableRel K.Adj] (hK : Disjoint (supp K) (supp G)) : SPReduces (G ⊔ K) (H ⊔ K) := by
  refine h.sup_of_disjoint fun a b hab z haz => ?_
  have ha : a ∈ supp K := mem_supp_iff_exists_adj.2 ⟨b, hab⟩
  have ha' : a ∈ supp G := mem_supp_iff_exists_adj.2 ⟨z, haz⟩
  exact Finset.disjoint_left.1 hK ha ha'

end SPReduces

end MOSPFormalization.DegreeBound
