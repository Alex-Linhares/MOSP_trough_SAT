/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The pathwidth assembly: Lemma 5.1 and Corollary 5.2 of Edwards & McDermid (2015), conditional on
two named hypotheses

Item 09 of loop0012 (`reports/edwards_mcdermid_plan.md` §0.3, §0.5; `reports/edwards_mcdermid.md`
§2.6 and §9). This file closes the development: the degree-sequence upper bound on pathwidth,

  `pw(G) ≤ f⁻(G) + τ(n) + 2 ρ(n) + 1`               for every `G` with every degree `0` or `≥ 3`,
  `pw(G) ≤ Σ_v g(deg_B(v)) + τ(n) + 3 ρ(n) + 1`     for every `G` and every reduced reduct `B` of `G`,
  `pw(G) ≤ Σ_v g(deg_G(v)) + τ(n) + 3 ρ(n) + 1`     for every `G`,

is proved from Theorem 3.2 (`exists_reduction_set`, item 08) and the graph lemmas of the
repository, **conditional on two cited results that are stated as named `Prop`s and never
asserted**:

* `CubicPathwidthBound τ` — **(H1)**, the cubic base case (Fomin & Høie 2006, Theorem 5, as the
  paper restates it on p. 19: "there is a function `τ`, with `τ(n) = o(n)`, such that
  `pw(G) ≤ n/6 − 1/6 + τ(n) + O(log n)`" for 3-regular `G`);
* `ReductionPathwidthBound ρ` — **(H3)**, the reduction lemma (Kneis, Mölle, Richter &
  Rossmanith 2009, as the paper uses it on p. 20: "`pw(G − X_G) = pw(r(G − X_G)) + O(log n)`",
  and "series-parallel graphs … The pathwidth of these graphs is `O(log n)`", p. 5).

The paper gives no constants for either (`τ(n) = o(n)`, the `O(log n)` unspecified), so each
hypothesis is parameterised by a budget `ℕ → ℚ` and every theorem carries the budgets it uses:
`τ` once (applied to a cubic component on at most `n` vertices, which is where `Monotone τ`
enters), `ρ` once per use of (H3) — inside a basic component of the second kind (`C − v →* ⊥`),
for `G − X →* B` in Lemma 5.1, and for `G →* B` in Corollary 5.2 — and `+ 1` for the deleted
vertex `v` of a second-kind component. The paper's `τ(n) + O(log n)` is this with
`ρ = O(log n)`. Two side conditions on the budgets are needed and stated: `Monotone τ` (the
paper: "We can also assume that `τ` is an increasing function of `n`") and `0 ≤ τ n` (a cubic
component may be absent, and then the `τ` term is pure slack); `0 ≤ ρ n` is *derived* from
(H3) (`ReductionPathwidthBound.nonneg`, by `G →* G` in zero steps on `n` vertices).

* `pathwidth_bot`: `pathwidth ⊥ = 0` (one singleton bag per vertex).
* `pathwidth_le_pathwidth_isolateSet_add_card`: `pathwidth G ≤ pathwidth (G − X) + |X|`, from
  `pathwidth_le_pathwidth_induce_add_card_compl` (`TreeBound.lean`) and the embedding
  `G[Xᶜ] → G − X` (`pathwidth_induce_compl_le_isolateSet`); the one-vertex case
  `pathwidth_le_pathwidth_isolate_add_one`.
* `pathwidth_le_rat_of_forall_connected`: `pathwidth G ≤ b` in `ℚ` as soon as every connected
  vertex set `C` has `pathwidth G[C] ≤ b` and `0 ≤ b` — `pathwidth_induce_le_of_forall_connected`
  (`TreeBound.lean`) at `⌊b⌋₊`. The paper's "`pw(G) = max_i pw(G_i)`" ("the fact that we have a
  maximum rather than a sum here is crucial").
* Components: `connected_induce_compFinset`, `degree_induce_of_forall_adj_mem`,
  `degree_induce_compFinset`,
  `subset_compFinset_of_connected`, `pathwidth_induce_compFinset_le_restrict`,
  `induce_eq_bot_of_forall_degree_eq_zero`.
* `pathwidth_induce_compFinset_le`: a non-trivial component `C` of a reduced basic graph has
  `pathwidth G[C] ≤ compPotential G C + τ n + ρ n + 1` — cubic by (H1) on `G[C]` and
  `compPotential_cubic` (`|C|/6 − 1/6`, "this is where we use the negative term"); second kind by
  `G[C] ≤ G|C`, one deletion, (H3) to `⊥`, and `compPotential_nonneg`.
* `pathwidth_basic_le`: for reduced basic `B`, `pathwidth B ≤ f⁻(B) + τ n + ρ n + 1` (the max over
  the components, each bounded by its own term and `compPotential ≤ f⁻`).
* `pathwidth_le_of_isReductionSet` and **A1** `pathwidth_le_potentialMinus_of_hypotheses`
  (**Lemma 5.1**): for reduced `G ≠ ⊥`, `pathwidth G ≤ f⁻(G) + τ n + 2 ρ n + 1`, from T1,
  `pathwidth G ≤ pathwidth (G − X) + |X|`, (H3) on `G − X →* B` and `pathwidth_basic_le`;
  `pathwidth_le_potential_of_hypotheses` is the paper's displayed form with `f` in place of `f⁻`.
* **A2** `pathwidth_le_degreeSum_of_hypotheses` (**Corollary 5.2**): for every `G` and every
  reduced reduct `B` of `G`, `pathwidth G ≤ Σ_v g (B.degree v) + τ n + 3 ρ n + 1` (no `G ≠ ⊥`
  needed: if `B = ⊥` the bound is the non-negativity of the budgets);
  `pathwidth_le_histogram_of_hypotheses`: the same with `G`'s own degree histogram, by R2
  (`SPReduces.potential_le`, reduction never raises a surviving degree, and `g` is monotone) —
  the corollary's displayed "`=`" is a "`≤`" (plan §0.4 (6)).

Every deterministic statement here was checked by brute force in the form proved before it was
stated (`reports/scratch/edwards_mcdermid/09_assembly/check.py`: every graph on 1–8 vertices,
13,598 graphs, every vertex set `X` and every connected vertex set `C`; 500 random graphs at
`n ≤ 12`; zero violations). What is **not** claimed: (H1) or (H3) themselves, or any value of
`τ`, `ρ`; Theorem 5.3 (its averaging lemma is Edwards & Farr's); that the budgets are tight.
-/
import MOSPFormalization.DegreeBound.ReductionTheorem
import MOSPFormalization.DegreeBound.CutLemma
import MOSPFormalization.TreeBound
import MOSPFormalization.Minor

set_option linter.unusedSectionVars false

namespace MOSPFormalization.DegreeBound

open Finset

universe u

/-! ### The two named hypotheses (cited, never asserted) -/

/-- **(H1) The cubic base case**, a named `Prop` with budget `τ`. Edwards & McDermid 2015, p. 19:
"Fomin and Høie [12] showed that a 3-regular graph `G` with `m` edges has pathwidth at most
`(1/9 + o(1)) m + O(log n) = (1/6 + o(1)) n + O(log n)`. Hence for 3-regular graphs, there is a
function `τ`, with `τ(n) = o(n)`, such that `pw(G) ≤ n/6 − 1/6 + τ(n) + O(log n)` (the negative
term is needed below). We can also assume that `τ` is an increasing function of `n`." Fomin & Høie
2006, Theorem 5: "For any `ε > 0`, there exists an integer `n_ε` such that for every graph `G`
with maximum vertex degree at most three and with `|V(G)| > n_ε`, `pw(G) ≤ (1/6 + ε)|V(G)|`."
The `O(log n)` of the paper's restatement is folded into `τ`; the paper gives no constants, and
none is asserted here. -/
def CubicPathwidthBound (τ : ℕ → ℚ) : Prop :=
  ∀ (W : Type u) [Fintype W] [DecidableEq W] (G : SimpleGraph W) [DecidableRel G.Adj],
    G.Connected → (∀ v, G.degree v = 3) →
      (pathwidth G : ℚ) ≤ (Fintype.card W : ℚ) / 6 - 1 / 6 + τ (Fintype.card W)

/-- **(H3) The reduction lemma**, a named `Prop` with budget `ρ`: a series-parallel reduction
sequence raises the pathwidth by at most `ρ(n)`. Edwards & McDermid 2015, p. 20: "It follows from
the results of [21] that `pw(G) ≤ |X_G| + pw(G − X_G)` and that
`pw(G − X_G) = pw(r(G − X_G)) + O(log n)`"; and p. 5: "series-parallel graphs have treewidth at
most 2. The pathwidth of these graphs is `O(log n)`" (the case `H = ⊥`). Reference [21] is
Kneis, Mölle, Richter & Rossmanith, *SIAM J. Discrete Math.* 23(1):407–427, 2009, which is not
held (`literature/MISSING.md`). The direction `pw(H) ≤ pw(G)` is unconditional (`r(G)` is a
minor of `G`) and not needed. -/
def ReductionPathwidthBound (ρ : ℕ → ℚ) : Prop :=
  ∀ (W : Type u) [Fintype W] [DecidableEq W] (G H : SimpleGraph W),
    SPReduces G H → (pathwidth G : ℚ) ≤ pathwidth H + ρ (Fintype.card W)

/-- (H3) forces a non-negative budget: `G →* G` in zero steps on `n` vertices. -/
theorem ReductionPathwidthBound.nonneg {ρ : ℕ → ℚ} (h : ReductionPathwidthBound.{u} ρ) (n : ℕ) :
    0 ≤ ρ n := by
  have := h (ULift.{u} (Fin n)) ⊥ ⊥ (SPReduces.refl _)
  rw [Fintype.card_ulift, Fintype.card_fin] at this
  linarith

variable {V : Type u} [Fintype V] [DecidableEq V]

/-! ### Graph lemmas: the edgeless graph, deleting a vertex set, the maximum over components -/

/-- The edgeless graph has pathwidth `0`: one singleton bag per vertex. -/
theorem pathwidth_bot : pathwidth (⊥ : SimpleGraph V) = 0 := by
  apply Nat.eq_zero_of_le_zero
  let e := Fintype.equivFin V
  let P : PathDecomposition (⊥ : SimpleGraph V) :=
    { length := Fintype.card V
      bag := fun i => univ.filter (fun v => (e v : ℕ) = i.val)
      vertex_coverage := fun v => ⟨⟨e v, Nat.lt_succ_of_lt (e v).isLt⟩, by simp⟩
      edge_coverage := fun _ _ h => ((SimpleGraph.bot_adj _ _).1 h).elim
      interval := fun v i j k hij hjk hi hk => by
        simp only [mem_filter, mem_univ, true_and] at hi hk ⊢
        have h1 : i.val ≤ j.val := hij
        have h2 : j.val ≤ k.val := hjk
        omega }
  refine (pathwidth_le_width _ P).trans (PathDecomposition.width_le_of_forall_card_le P ?_)
  intro i
  show (univ.filter (fun v => (e v : ℕ) = i.val)).card ≤ 0 + 1
  rw [zero_add]
  refine card_le_one.2 (fun a ha b hb => e.injective (Fin.ext ?_))
  simp only [mem_filter, mem_univ, true_and] at ha hb
  omega

/-- `G[Xᶜ]` embeds in `G − X` (the vertices of `X` are isolated there). -/
theorem pathwidth_induce_compl_le_isolateSet (G : SimpleGraph V) (X : Finset V) :
    pathwidth (G.induce (↑(Xᶜ) : Set V)) ≤ pathwidth (isolateSet G X) :=
  pathwidth_le_of_injective
    (⟨Subtype.val, fun {a b} h =>
      ⟨h, Finset.mem_compl.1 (Finset.mem_coe.1 a.2), Finset.mem_compl.1 (Finset.mem_coe.1 b.2)⟩⟩ :
      G.induce (↑(Xᶜ) : Set V) →g isolateSet G X) Subtype.val_injective

/-- **Deleting a vertex set costs at most its size**: `pathwidth G ≤ pathwidth (G − X) + |X|`
(the paper's "`pw(G) ≤ |X_G| + pw(G − X_G)`", which it attributes to [21]; here it is
`pathwidth_le_pathwidth_induce_add_card_compl` of `TreeBound.lean`). -/
theorem pathwidth_le_pathwidth_isolateSet_add_card (G : SimpleGraph V) (X : Finset V) :
    pathwidth G ≤ pathwidth (isolateSet G X) + X.card := by
  have h := pathwidth_le_pathwidth_induce_add_card_compl G Xᶜ
  rw [compl_compl] at h
  exact h.trans (Nat.add_le_add_right (pathwidth_induce_compl_le_isolateSet G X) _)

/-- `pathwidth G ≤ pathwidth (G − w) + 1`. -/
theorem pathwidth_le_pathwidth_isolate_add_one (G : SimpleGraph V) (w : V) :
    pathwidth G ≤ pathwidth (isolate G w) + 1 := by
  have h := pathwidth_le_pathwidth_isolateSet_add_card G {w}
  rwa [isolateSet_singleton, card_singleton] at h

/-- **The maximum over components, in `ℚ`**: if every connected vertex set `C` has
`pathwidth G[C] ≤ b` and `0 ≤ b`, then `pathwidth G ≤ b`. The paper's
"`pw(G) = max_i pw(G_i)` (Note that the fact that we have a maximum rather than a sum here is
crucial.)" -/
theorem pathwidth_le_rat_of_forall_connected (G : SimpleGraph V) [DecidableRel G.Adj] {b : ℚ}
    (hb : 0 ≤ b)
    (h : ∀ C : Finset V, (G.induce (↑C : Set V)).Connected →
      (pathwidth (G.induce (↑C : Set V)) : ℚ) ≤ b) :
    (pathwidth G : ℚ) ≤ b := by
  have hk : pathwidth G ≤ ⌊b⌋₊ := by
    rw [← pathwidth_induce_univ G]
    exact pathwidth_induce_le_of_forall_connected G univ ⌊b⌋₊
      (fun C _ hc => Nat.le_floor (h C hc))
  calc (pathwidth G : ℚ) ≤ (⌊b⌋₊ : ℚ) := by exact_mod_cast hk
    _ ≤ b := Nat.floor_le hb

/-! ### Components of a graph on `V`, as induced subgraphs -/

section Components

variable (G : SimpleGraph V) [DecidableRel G.Adj]

theorem coe_compFinset (C : G.ConnectedComponent) : (↑(compFinset G C) : Set V) = C.supp := by
  ext v
  exact mem_compFinset_iff_mem_supp G

/-- The induced subgraph on a component is connected. -/
theorem connected_induce_compFinset (C : G.ConnectedComponent) :
    (G.induce (↑(compFinset G C) : Set V)).Connected := by
  rw [coe_compFinset]
  exact (SimpleGraph.ConnectedComponent.maximal_connected_induce_supp C).1

/-- Degrees in an induced subgraph: if every neighbour of `v` lies in `s`, the degree of `v` in
`G[s]` is its degree in `G` (by the bijection `a ↦ ↑a` of neighbour finsets; Mathlib's
`degree_induce_of_neighborSet_subset` is the same statement under a `DecidablePred`-built
`Fintype` instance that does not unify with the one of a coerced finset). -/
theorem degree_induce_of_forall_adj_mem {s : Set V} [Fintype ↥s] (v : ↥s)
    (h : ∀ u, G.Adj v u → u ∈ s) :
    (G.induce s).degree v = G.degree v := by
  rw [← SimpleGraph.card_neighborFinset_eq_degree, ← SimpleGraph.card_neighborFinset_eq_degree]
  refine Finset.card_bij (fun a _ => a.val) ?_ ?_ ?_
  · intro a ha
    rw [SimpleGraph.mem_neighborFinset] at ha ⊢
    exact ha
  · intro a _ b _ hab
    exact Subtype.ext hab
  · intro u hu
    rw [SimpleGraph.mem_neighborFinset] at hu
    exact ⟨⟨u, h u hu⟩, by rw [SimpleGraph.mem_neighborFinset]; exact hu, rfl⟩

/-- Degrees inside a component are the degrees in `G` (every neighbour lies in the component). -/
theorem degree_induce_compFinset {C : G.ConnectedComponent}
    (v : ↥(↑(compFinset G C) : Set V)) :
    (G.induce (↑(compFinset G C) : Set V)).degree v = G.degree v := by
  refine degree_induce_of_forall_adj_mem G v (fun u hu => ?_)
  exact insert_neighborFinset_subset_compFinset G (Finset.mem_coe.1 v.2)
    (Finset.mem_insert_of_mem ((SimpleGraph.mem_neighborFinset G v u).2 hu))

/-- A connected vertex set lies inside the component of any of its vertices. -/
theorem subset_compFinset_of_connected {C : Finset V} (hc : (G.induce (↑C : Set V)).Connected)
    {v : V} (hv : v ∈ C) : C ⊆ compFinset G (G.connectedComponentMk v) := by
  intro u hu
  rw [mem_compFinset_mk]
  have := hc.preconnected ⟨u, Finset.mem_coe.2 hu⟩ ⟨v, Finset.mem_coe.2 hv⟩
  exact this.map (SimpleGraph.Embedding.induce (↑C : Set V)).toHom

/-- `G[C]` embeds in `G|C` (the restriction on `V`, every other vertex isolated). -/
theorem pathwidth_induce_compFinset_le_restrict (C : G.ConnectedComponent) :
    pathwidth (G.induce (↑(compFinset G C) : Set V)) ≤ pathwidth (restrict G C.supp) :=
  pathwidth_le_of_injective
    (⟨Subtype.val, fun {a b} h =>
      ⟨h, (mem_compFinset_iff_mem_supp G).1 (Finset.mem_coe.1 a.2),
        (mem_compFinset_iff_mem_supp G).1 (Finset.mem_coe.1 b.2)⟩⟩ :
      G.induce (↑(compFinset G C) : Set V) →g restrict G C.supp) Subtype.val_injective

/-- A vertex set of isolated vertices induces the edgeless graph. -/
theorem induce_eq_bot_of_forall_degree_eq_zero {C : Finset V} (h : ∀ v ∈ C, G.degree v = 0) :
    G.induce (↑C : Set V) = ⊥ := by
  ext a b
  constructor
  · intro hab
    have hpos : 0 < G.degree a := (G.degree_pos_iff_exists_adj a).2 ⟨b, hab⟩
    have := h a (Finset.mem_coe.1 a.2)
    omega
  · intro h
    exact ((SimpleGraph.bot_adj _ _).1 h).elim

/-- `compPotential G C ≤ f⁻(G)`: every other component contributes `≥ 0`. -/
theorem compPotential_le_potentialMinus (C : G.ConnectedComponent) :
    compPotential G C ≤ potentialMinus G := by
  rw [potentialMinus_eq_sum_compPotential]
  exact single_le_sum (fun D _ => compPotential_nonneg G D) (mem_univ C)

end Components

/-! ### Lemma 5.1: basic graphs, then every reduced graph -/

/-- **The per-component bound** (Lemma 5.1's first paragraph). A non-trivial component `C` of a
reduced basic graph has `pathwidth G[C] ≤ compPotential G C + τ n + ρ n + 1`: if cubic, by (H1)
on `G[C]` with `compPotential G C = |C|/6 − 1/6` ("this is where we use the negative term") and
`τ |C| ≤ τ n`; if of the second kind, `G[C]` embeds in `G|C`, deleting `u` costs one, and (H3)
takes `(G|C) − u →* ⊥` to `pathwidth ⊥ = 0`, so `pathwidth G[C] ≤ ρ n + 1 ≤ compPotential G C +
τ n + ρ n + 1`. -/
theorem pathwidth_induce_compFinset_le {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    (G : SimpleGraph V) [DecidableRel G.Adj] (hb : IsBasic G) {C : G.ConnectedComponent} {v : V}
    (hv : v ∈ compFinset G C) (hpos : 0 < G.degree v) :
    (pathwidth (G.induce (↑(compFinset G C) : Set V)) : ℚ) ≤
      compPotential G C + τ (Fintype.card V) + ρ (Fintype.card V) + 1 := by
  have hρ := h3.nonneg (Fintype.card V)
  rcases isBasic_component G hb hv hpos with hcub | ⟨u, _, hred⟩
  · -- cubic: (H1) on the component
    have hc := h1 _ (G.induce (↑(compFinset G C) : Set V)) (connected_induce_compFinset G C)
      (fun w => by rw [degree_induce_compFinset]; exact hcub w (Finset.mem_coe.1 w.2))
    simp only [Finset.coe_sort_coe, Fintype.card_coe] at hc
    rw [compPotential_cubic G hcub]
    have hmono : τ (compFinset G C).card ≤ τ (Fintype.card V) := hτ (Finset.card_le_univ _)
    linarith
  · -- second kind: one deletion, then (H3) to `⊥`
    have h₁ := pathwidth_induce_compFinset_le_restrict G C
    have h₂ := pathwidth_le_pathwidth_isolate_add_one (restrict G C.supp) u
    have h₃ := h3 V _ _ hred
    rw [pathwidth_bot] at h₃
    have h₄ := compPotential_nonneg G C
    have hτn := hτ0 (Fintype.card V)
    have h₅ : (pathwidth (G.induce (↑(compFinset G C) : Set V)) : ℚ) ≤
        (pathwidth (isolate (restrict G C.supp) u) : ℚ) + 1 := by
      exact_mod_cast h₁.trans h₂
    push_cast at h₃
    linarith

/-- **Lemma 5.1 for basic graphs**: `pathwidth B ≤ f⁻(B) + τ n + ρ n + 1` for every reduced basic
`B` (the maximum over the components; a connected vertex set with an edge lies in a non-trivial
component, and one without edges induces `⊥`). -/
theorem pathwidth_basic_le {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    (B : SimpleGraph V) [DecidableRel B.Adj] (hb : IsBasic B) :
    (pathwidth B : ℚ) ≤ potentialMinus B + τ (Fintype.card V) + ρ (Fintype.card V) + 1 := by
  have hρ := h3.nonneg (Fintype.card V)
  have hτn := hτ0 (Fintype.card V)
  have hf := potentialMinus_nonneg B
  refine pathwidth_le_rat_of_forall_connected B (by linarith) (fun C hc => ?_)
  by_cases hdeg : ∀ v ∈ C, B.degree v = 0
  · rw [induce_eq_bot_of_forall_degree_eq_zero B hdeg, pathwidth_bot]
    push_cast
    linarith
  · push Not at hdeg
    obtain ⟨v, hv, hv0⟩ := hdeg
    have hpos : 0 < B.degree v := Nat.pos_of_ne_zero hv0
    have hmono := pathwidth_induce_mono B (subset_compFinset_of_connected B hc hv)
    have hcomp := pathwidth_induce_compFinset_le h1 h3 hτ hτ0 B hb (self_mem_compFinset B v) hpos
    have hle := compPotential_le_potentialMinus B (B.connectedComponentMk v)
    have hmono' : (pathwidth (B.induce (↑C : Set V)) : ℚ) ≤
        pathwidth (B.induce (↑(compFinset B (B.connectedComponentMk v)) : Set V)) := by
      exact_mod_cast hmono
    linarith

/-- The assembly for any reduction set (Theorem 3.2's conclusion):
`pathwidth G ≤ pathwidth (G − X) + |X| ≤ pathwidth B + ρ n + |X| ≤ f⁻(B) + |X| + τ n + 2 ρ n + 1
≤ f⁻(G) + τ n + 2 ρ n + 1`. -/
theorem pathwidth_le_of_isReductionSet {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    {G B : SimpleGraph V} [DecidableRel G.Adj] [DecidableRel B.Adj] {X : Finset V}
    (h : IsReductionSet G X B) :
    (pathwidth G : ℚ) ≤ potentialMinus G + τ (Fintype.card V) + 2 * ρ (Fintype.card V) + 1 := by
  have hX : (pathwidth G : ℚ) ≤ pathwidth (isolateSet G X) + X.card := by
    exact_mod_cast pathwidth_le_pathwidth_isolateSet_add_card G X
  have hred := h3 V _ _ h.reduces
  have hbasic := pathwidth_basic_le h1 h3 hτ hτ0 B h.basic
  have hcard := h.card_add_le
  linarith

/-- **A1, Lemma 5.1** (Edwards & McDermid 2015, p. 19, the form its proof establishes): for every
`G` with every degree `0` or `≥ 3` and at least one edge,
`pathwidth G ≤ f⁻(G) + τ n + 2 ρ n + 1`, conditional on (H1) with a monotone non-negative
budget `τ` and on (H3) with budget `ρ`. -/
theorem pathwidth_le_potentialMinus_of_hypotheses {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    (G : SimpleGraph V) [DecidableRel G.Adj] (hG : IsSPReduced G) (hne : G ≠ ⊥) :
    (pathwidth G : ℚ) ≤ potentialMinus G + τ (Fintype.card V) + 2 * ρ (Fintype.card V) + 1 := by
  obtain ⟨X, B, instB, h⟩ := exists_reduction_set G hG hne
  exact pathwidth_le_of_isReductionSet h1 h3 hτ hτ0 h

/-- **Lemma 5.1 as displayed**: `pathwidth G ≤ Σ_v g(deg v) + τ n + 2 ρ n + 1` for reduced
`G ≠ ⊥` (`f⁻ ≤ f`). -/
theorem pathwidth_le_potential_of_hypotheses {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    (G : SimpleGraph V) [DecidableRel G.Adj] (hG : IsSPReduced G) (hne : G ≠ ⊥) :
    (pathwidth G : ℚ) ≤
      ∑ v, g (G.degree v) + τ (Fintype.card V) + 2 * ρ (Fintype.card V) + 1 := by
  have h := pathwidth_le_potentialMinus_of_hypotheses h1 h3 hτ hτ0 G hG hne
  have h' := potentialMinus_le_potential G
  unfold potential at h'
  linarith

/-! ### Corollary 5.2 -/

/-- **A2, Corollary 5.2** (Edwards & McDermid 2015, p. 20): for every `G` and every reduced
reduct `B` of `G` (the paper's `r(G)`),
`pathwidth G ≤ Σ_v g(deg_B v) + τ n + 3 ρ n + 1`, conditional on (H1) with a monotone
non-negative budget `τ` and on (H3) with budget `ρ`. No `G ≠ ⊥` is needed: when `B = ⊥` the
bound is the non-negativity of the budgets. -/
theorem pathwidth_le_degreeSum_of_hypotheses {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    (G : SimpleGraph V) {B : SimpleGraph V} [DecidableRel B.Adj] (hGB : SPReduces G B)
    (hB : IsSPReduced B) :
    (pathwidth G : ℚ) ≤
      ∑ v, g (B.degree v) + τ (Fintype.card V) + 3 * ρ (Fintype.card V) + 1 := by
  have hρ := h3.nonneg (Fintype.card V)
  have hτn := hτ0 (Fintype.card V)
  have hred := h3 V _ _ hGB
  have hpot : potentialMinus B ≤ potential B := potentialMinus_le_potential B
  have hp0 : 0 ≤ potential B := potential_nonneg B
  have hsum : potential B = ∑ v, g (B.degree v) := rfl
  by_cases hne : B = ⊥
  · subst hne
    rw [pathwidth_bot] at hred
    push_cast at hred
    linarith
  · have hA1 := pathwidth_le_potentialMinus_of_hypotheses h1 h3 hτ hτ0 B hB hne
    linarith

/-- **Corollary 5.2 with `G`'s own degree histogram**: `pathwidth G ≤ Σ_v g(deg_G v) + τ n +
3 ρ n + 1` for every `G`, since reduction never raises a surviving degree and `g` is monotone
(R2, `SPReduces.potential_le`). The paper's displayed "`=`" is this "`≤`". -/
theorem pathwidth_le_histogram_of_hypotheses {τ ρ : ℕ → ℚ} (h1 : CubicPathwidthBound.{u} τ)
    (h3 : ReductionPathwidthBound.{u} ρ) (hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    (pathwidth G : ℚ) ≤
      ∑ v, g (G.degree v) + τ (Fintype.card V) + 3 * ρ (Fintype.card V) + 1 := by
  classical
  obtain ⟨B, hGB, hB⟩ := exists_reduced_reduct G
  have h := pathwidth_le_degreeSum_of_hypotheses h1 h3 hτ hτ0 G hGB hB
  have hle : potential B ≤ potential G := SPReduces.potential_le hGB
  unfold potential at hle
  linarith

end MOSPFormalization.DegreeBound
