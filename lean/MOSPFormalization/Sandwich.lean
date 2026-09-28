/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The sandwich: degeneracy ≤ pathwidth ≤ bandwidth

The certified corpus satisfies `degeneracy(G) + 1 ≤ optimum ≤ bandwidth(G) + 1`
on every one of its instances (`reports/ml_nature.md` §5), and the optimum is
`pathwidth + 1` by Yanasse's equality, proved over the MOSP graph in
`MOSPGraph.lean` (`MOSPInstance.mospValue_eq_pathwidth_add_one`). Both halves are textbook inequalities
about graphs; this file proves them over the repository's definitions and
connects them through Kinnersley's theorem (`VSEquivPW`).

## Definitions

* `bandwidthOfLayout G σ` — the largest stretch `|σ v − σ u|` over the edges
  `uv` of `G` under the layout `σ`; `bandwidth G` is the minimum over layouts.
* `laterNeighbors G σ v` — the neighbours of `v` placed after `v` by `σ`;
  `maxLaterDegree G σ` is the largest such count; `orderingDegeneracy G` is
  its minimum over layouts (the elimination-ordering form of degeneracy: a
  layout in which every vertex has at most `k` neighbours after it).
* `minDegreeIn G S` — the minimum degree of the subgraph induced on `S`;
  `degeneracy G` is its maximum over all vertex subsets (the Lick–White
  form: `G` is `k`-degenerate iff every subgraph has a vertex of degree ≤ `k`).

## Main results

* `vertexSeparation_le_bandwidth`, `pathwidth_le_bandwidth` — the upper half.
  At any cut position `i`, an active suffix vertex is within `b` positions of
  a prefix neighbour, so it sits in the window `(i, i + b]`, which holds `b`
  positions; `σ` is injective.
* `degeneracy_le_orderingDegeneracy`, `orderingDegeneracy_le_vertexSeparation`,
  `degeneracy_le_pathwidth` — the lower half. Every neighbour placed after `v`
  is active at `v`'s own position, so the later-degree is bounded by the
  vertex separation of the layout; and the first vertex of any subset `S`
  under a layout has all its `S`-neighbours after it, so `minDegreeIn S` is
  bounded by the later-degree.
* `degeneracy_le_pathwidth_le_bandwidth` — the sandwich, and
  `mospValue_le_bandwidth_add_one` / `degeneracy_add_one_le_mospValue` in MOSP
  terms, over the MOSP graph on customers (`MOSPGraph.lean`): the upper half
  holds for every instance, the lower half whenever some customer requires some
  pattern, which is when `mospValue = pathwidth + 1` holds. Both are `sorry`-free.
* `orderingDegeneracy_eq_degeneracy` — the two forms of degeneracy coincide.
  The converse direction is the greedy elimination ordering: delete a vertex
  of minimum degree (`deleteVertex`, whose degeneracy is no larger), lay out
  the rest by induction on the number of vertices, and put the deleted vertex
  first.

## Tree decompositions (loop0004 item 12, 2026-09-28)

* `TreeDecomposition`, `treewidth` — a tree on a finite index type with bags,
  covering vertices and edges, the bags containing any vertex inducing a
  connected subtree; the minimum width over all of them.
* `pathGraph_isTree` — Mathlib has `pathGraph_connected` and nothing on its
  acyclicity; every edge `i, i + 1` is a bridge, because a walk from `i` to
  `i + 1` avoiding it would have to cross the cut `{j ≤ i}` along some other
  edge, and the path graph has none (`Walk.exists_boundary_dart`).
* `pathGraph_induce_interval_connected` — the path graph induced on an interval
  is connected, by walking one step at a time.
* `PathDecomposition.toTreeDecomposition`, `treewidth_le_pathwidth` — every path
  decomposition is a tree decomposition on the path graph of its indices, with
  the same width; so `treewidth ≤ pathwidth`, and in MOSP terms
  `MOSPInstance.treewidth_add_one_le_mospValue`.
* `branch_lemma` — **the pathwidth branch lemma** (Fellows & Langston 1987,
  Lemma 4.3; Kinnersley 1992, Corollary 4.2 and the remark before Theorem 4.3):
  three pairwise disjoint *connected* vertex sets of pathwidth `≥ k`, each
  *adjacent to* a vertex `v` outside them, force `pathwidth ≥ k + 1`.
  `branch_lemma_treewidth` is the same with the branches' treewidth. The proof
  is the interval argument: in a decomposition of width `k` each branch fills a
  bag of its own (`exists_bag_subset_of_le_pathwidth_induce`); `v` avoids the
  middle one, and the branch on the far side of it is joined to `v` on the near
  side and to its own bag on the far side, so being connected it crosses the
  middle bag (`exists_mem_bag_of_connected`, `middle_bag_false`). No hypothesis
  on edges *between* the branches is needed.
* `old_branch_statement_false` — the statement this file carried with `sorry`
  until 2026-09-28 asked only that the branches be pairwise non-adjacent,
  neither connected nor attached to `v`, and **was false**: four isolated
  vertices, `v = 0`, branches `{1}`, `{2}`, `{3}`, `k = 0`, pathwidth `0`
  (`pathwidth_bot_fin4`). The literature's forms carry both hypotheses: the
  branches are the components of `G − v` (hence connected) that `v` is
  attached to.

## Stated, not proved

* `conjecture_sqrt_tw_f6` — item 09's one surviving fitted candidate,
  `optimum ≥ ⌊0.9428 √(tw · f(6))⌋`, stated with the optimum read as
  `pathwidth + 1` and labelled worthless there because it is pointwise below
  the proved pair on every certified instance. Left as a statement on purpose.
-/

import MOSPFormalization.VSEquivPW
import MOSPFormalization.MOSPGraph
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Hasse
import Mathlib.Analysis.Real.Sqrt

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Bandwidth -/

/-- The bandwidth of a layout: the largest stretch of an edge. Both orientations
of every edge are in the index set, so natural subtraction computes `|σ v − σ u|`. -/
def bandwidthOfLayout (σ : LinearLayout V) : ℕ :=
  (Finset.univ.filter (fun p : V × V => G.Adj p.1 p.2)).sup
    (fun p => (σ p.2).val - (σ p.1).val)

/-- The bandwidth of a graph: the minimum stretch over all layouts. -/
noncomputable def bandwidth : ℕ :=
  sInf (Set.range (fun σ : LinearLayout V => bandwidthOfLayout G σ))

theorem bandwidth_le_bandwidthOfLayout (σ : LinearLayout V) :
    bandwidth G ≤ bandwidthOfLayout G σ := by
  apply Nat.sInf_le
  exact ⟨σ, rfl⟩

/-- Under a layout of bandwidth `b`, a neighbour is at most `b` positions later. -/
theorem val_le_of_adj (σ : LinearLayout V) {u v : V} (h : G.Adj u v) :
    (σ v).val ≤ (σ u).val + bandwidthOfLayout G σ := by
  have hmem : (u, v) ∈ Finset.univ.filter (fun p : V × V => G.Adj p.1 p.2) :=
    Finset.mem_filter.mpr ⟨Finset.mem_univ _, h⟩
  have h := Finset.le_sup (f := fun p : V × V => (σ p.2).val - (σ p.1).val) hmem
  change (σ v).val - (σ u).val ≤ bandwidthOfLayout G σ at h
  omega

/-- Every active suffix vertex at position `i` sits in the window `(i, i + b]`. -/
theorem vertexSepAt_le_bandwidthOfLayout (σ : LinearLayout V) (i : ℕ) :
    vertexSepAt G σ i ≤ bandwidthOfLayout G σ := by
  unfold vertexSepAt
  set b := bandwidthOfLayout G σ
  calc (activeSuffix G σ i).card
      ≤ (Finset.Ioc i (i + b)).card := by
        apply Finset.card_le_card_of_injOn (fun v => (σ v).val)
        · intro v hv
          rw [Finset.mem_coe, mem_activeSuffix_iff] at hv
          obtain ⟨hgt, u, hu, hadj⟩ := hv
          rw [mem_prefixSet_iff] at hu
          have := val_le_of_adj G σ hadj
          rw [Finset.mem_coe, Finset.mem_Ioc]
          show i < (σ v).val ∧ (σ v).val ≤ i + b
          omega
        · intro x _ y _ hxy
          exact σ.injective (Fin.ext hxy)
    _ = b := by rw [Nat.card_Ioc]; omega

theorem vertexSepOfLayout_le_bandwidthOfLayout (σ : LinearLayout V) :
    vertexSepOfLayout G σ ≤ bandwidthOfLayout G σ := by
  unfold vertexSepOfLayout
  by_cases hn : Fintype.card V = 0
  · simp [hn]
  · simp only [dite_eq_right hn]
    apply Finset.sup'_le
    intro i _
    exact vertexSepAt_le_bandwidthOfLayout G σ i.val

/-- **Upper half of the sandwich**: vertex separation is at most bandwidth. -/
theorem vertexSeparation_le_bandwidth :
    vertexSeparation G ≤ bandwidth G := by
  unfold bandwidth
  apply le_csInf
  · exact ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  · intro b ⟨σ, hσ⟩
    rw [← hσ]
    calc vertexSeparation G ≤ vertexSepOfLayout G σ :=
          vertexSeparation_le_vertexSepOfLayout G σ
      _ ≤ bandwidthOfLayout G σ := vertexSepOfLayout_le_bandwidthOfLayout G σ

/-- Pathwidth is at most bandwidth (through Kinnersley's theorem). -/
theorem pathwidth_le_bandwidth :
    pathwidth G ≤ bandwidth G := by
  rw [← vertexSeparation_eq_pathwidth]
  exact vertexSeparation_le_bandwidth G

/-- The layout-level form the corpus checks: any one layout's bandwidth (in the
corpus, reverse Cuthill–McKee's `bw_rcm`) bounds the pathwidth. -/
theorem pathwidth_le_bandwidthOfLayout (σ : LinearLayout V) :
    pathwidth G ≤ bandwidthOfLayout G σ :=
  (pathwidth_le_bandwidth G).trans (bandwidth_le_bandwidthOfLayout G σ)

/-! ### Degeneracy, elimination-ordering form -/

/-- The neighbours of `v` placed after `v` by `σ`. -/
def laterNeighbors (σ : LinearLayout V) (v : V) : Finset V :=
  Finset.univ.filter (fun u => G.Adj v u ∧ (σ v).val < (σ u).val)

theorem mem_laterNeighbors_iff (σ : LinearLayout V) (v u : V) :
    u ∈ laterNeighbors G σ v ↔ G.Adj v u ∧ (σ v).val < (σ u).val := by
  simp [laterNeighbors]

/-- The largest number of later neighbours of any vertex under `σ`. -/
def maxLaterDegree (σ : LinearLayout V) : ℕ :=
  Finset.univ.sup (fun v => (laterNeighbors G σ v).card)

/-- Degeneracy in elimination-ordering form: the least `k` such that some
layout gives every vertex at most `k` neighbours after it. -/
noncomputable def orderingDegeneracy : ℕ :=
  sInf (Set.range (fun σ : LinearLayout V => maxLaterDegree G σ))

theorem orderingDegeneracy_le_maxLaterDegree (σ : LinearLayout V) :
    orderingDegeneracy G ≤ maxLaterDegree G σ := by
  apply Nat.sInf_le
  exact ⟨σ, rfl⟩

theorem card_laterNeighbors_le_maxLaterDegree (σ : LinearLayout V) (v : V) :
    (laterNeighbors G σ v).card ≤ maxLaterDegree G σ :=
  Finset.le_sup (f := fun v => (laterNeighbors G σ v).card) (Finset.mem_univ v)

/-- Every later neighbour of `v` is active at `v`'s own position. -/
theorem laterNeighbors_subset_activeSuffix (σ : LinearLayout V) (v : V) :
    laterNeighbors G σ v ⊆ activeSuffix G σ (σ v).val := by
  intro u hu
  rw [mem_laterNeighbors_iff] at hu
  rw [mem_activeSuffix_iff]
  exact ⟨hu.2, v, by rw [mem_prefixSet_iff], hu.1⟩

theorem vertexSepAt_le_vertexSepOfLayout (σ : LinearLayout V) (i : Fin (Fintype.card V)) :
    vertexSepAt G σ i.val ≤ vertexSepOfLayout G σ := by
  unfold vertexSepOfLayout
  have hn : Fintype.card V ≠ 0 := by
    have := i.isLt; omega
  simp only [dite_eq_right hn]
  exact Finset.le_sup' (fun j : Fin (Fintype.card V) => vertexSepAt G σ j.val)
    (Finset.mem_univ i)

theorem card_laterNeighbors_le_vertexSepOfLayout (σ : LinearLayout V) (v : V) :
    (laterNeighbors G σ v).card ≤ vertexSepOfLayout G σ :=
  calc (laterNeighbors G σ v).card
      ≤ (activeSuffix G σ (σ v).val).card :=
        Finset.card_le_card (laterNeighbors_subset_activeSuffix G σ v)
    _ = vertexSepAt G σ (σ v).val := rfl
    _ ≤ vertexSepOfLayout G σ := vertexSepAt_le_vertexSepOfLayout G σ (σ v)

theorem maxLaterDegree_le_vertexSepOfLayout (σ : LinearLayout V) :
    maxLaterDegree G σ ≤ vertexSepOfLayout G σ := by
  apply Finset.sup_le
  intro v _
  exact card_laterNeighbors_le_vertexSepOfLayout G σ v

/-- **Lower half of the sandwich, ordering form**: every layout is a
degeneracy ordering of width at most its vertex separation. -/
theorem orderingDegeneracy_le_vertexSeparation :
    orderingDegeneracy G ≤ vertexSeparation G := by
  unfold vertexSeparation
  apply le_csInf
  · exact ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  · intro b ⟨σ, hσ⟩
    rw [← hσ]
    calc orderingDegeneracy G ≤ maxLaterDegree G σ :=
          orderingDegeneracy_le_maxLaterDegree G σ
      _ ≤ vertexSepOfLayout G σ := maxLaterDegree_le_vertexSepOfLayout G σ

/-! ### Degeneracy, subgraph form -/

/-- The degree of `v` inside the subgraph induced on `S`. -/
def degreeIn (S : Finset V) (v : V) : ℕ :=
  (S.filter (fun u => G.Adj v u)).card

/-- The minimum degree of the subgraph induced on `S` (`0` for the empty set). -/
def minDegreeIn (S : Finset V) : ℕ :=
  if h : S.Nonempty then S.inf' h (degreeIn G S) else 0

/-- Degeneracy in subgraph form: the largest minimum degree of an induced subgraph. -/
def degeneracy : ℕ :=
  (Finset.univ : Finset (Finset V)).sup (minDegreeIn G)

theorem minDegreeIn_le_degeneracy (S : Finset V) :
    minDegreeIn G S ≤ degeneracy G :=
  Finset.le_sup (f := minDegreeIn G) (Finset.mem_univ S)

theorem degeneracy_le_of_forall (k : ℕ) (h : ∀ S : Finset V, minDegreeIn G S ≤ k) :
    degeneracy G ≤ k :=
  Finset.sup_le (fun S _ => h S)

/-- The first vertex of `S` under `σ` has all of its `S`-neighbours after it. -/
theorem degreeIn_le_card_laterNeighbors (σ : LinearLayout V) (S : Finset V) {v : V}
    (hv : v ∈ S) (hmin : ∀ u ∈ S, (σ v).val ≤ (σ u).val) :
    degreeIn G S v ≤ (laterNeighbors G σ v).card := by
  apply Finset.card_le_card
  intro u hu
  rw [Finset.mem_filter] at hu
  rw [mem_laterNeighbors_iff]
  refine ⟨hu.2, ?_⟩
  have hle := hmin u hu.1
  have hne : u ≠ v := fun heq => by subst heq; exact G.ne_of_adj hu.2 rfl
  have hne' : (σ u).val ≠ (σ v).val := fun heq =>
    hne (σ.injective (Fin.ext heq))
  omega

/-- Every subset's minimum induced degree is bounded by the later-degree of any layout. -/
theorem minDegreeIn_le_maxLaterDegree (σ : LinearLayout V) (S : Finset V) :
    minDegreeIn G S ≤ maxLaterDegree G σ := by
  unfold minDegreeIn
  by_cases hS : S.Nonempty
  · simp only [dite_eq_left hS]
    obtain ⟨v, hv, hmin⟩ := Finset.exists_min_image S (fun u => (σ u).val) hS
    calc S.inf' hS (degreeIn G S) ≤ degreeIn G S v := Finset.inf'_le _ hv
      _ ≤ (laterNeighbors G σ v).card := degreeIn_le_card_laterNeighbors G σ S hv hmin
      _ ≤ maxLaterDegree G σ := card_laterNeighbors_le_maxLaterDegree G σ v
  · simp [dite_eq_right hS]

/-- The subgraph form is bounded by the ordering form. -/
theorem degeneracy_le_orderingDegeneracy :
    degeneracy G ≤ orderingDegeneracy G := by
  unfold orderingDegeneracy
  apply le_csInf
  · exact ⟨_, ⟨Fintype.equivFin V, rfl⟩⟩
  · intro b ⟨σ, hσ⟩
    rw [← hσ]
    exact degeneracy_le_of_forall G _ (minDegreeIn_le_maxLaterDegree G σ)

/-- **Lower half of the sandwich**: degeneracy is at most vertex separation. -/
theorem degeneracy_le_vertexSeparation :
    degeneracy G ≤ vertexSeparation G :=
  (degeneracy_le_orderingDegeneracy G).trans (orderingDegeneracy_le_vertexSeparation G)

/-- Degeneracy is at most pathwidth (through Kinnersley's theorem). -/
theorem degeneracy_le_pathwidth :
    degeneracy G ≤ pathwidth G := by
  rw [← vertexSeparation_eq_pathwidth]
  exact degeneracy_le_vertexSeparation G

/-- **The sandwich**: `degeneracy ≤ pathwidth ≤ bandwidth`, for every finite simple graph. -/
theorem degeneracy_le_pathwidth_le_bandwidth :
    degeneracy G ≤ pathwidth G ∧ pathwidth G ≤ bandwidth G :=
  ⟨degeneracy_le_pathwidth G, pathwidth_le_bandwidth G⟩

/-! ### In MOSP terms -/

namespace MOSPInstance

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]
variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- The upper half of the corpus sandwich, `optimum ≤ bandwidth + 1`, over the MOSP
graph, for every instance: `mospValue_le_pathwidth_add_one` needs no hypothesis. -/
theorem mospValue_le_bandwidth_add_one :
    M.mospValue ≤ bandwidth M.mospGraph + 1 :=
  M.mospValue_le_pathwidth_add_one.trans
    (Nat.add_le_add_right (pathwidth_le_bandwidth M.mospGraph) 1)

/-- The lower half of the corpus sandwich, `degeneracy + 1 ≤ optimum`, over the MOSP
graph, whenever some customer requires some pattern — the hypothesis of Yanasse's
equality `mospValue_eq_pathwidth_add_one`, without which `mospValue = 0`. -/
theorem degeneracy_add_one_le_mospValue (h : ∃ c p, M.requires c p) :
    degeneracy M.mospGraph + 1 ≤ M.mospValue := by
  rw [M.mospValue_eq_pathwidth_add_one h]
  exact Nat.add_le_add_right (degeneracy_le_pathwidth M.mospGraph) 1

end MOSPInstance

/-! ### The two forms of degeneracy coincide

The converse of `degeneracy_le_orderingDegeneracy`: the greedy elimination ordering —
remove a vertex of minimum degree, order the rest by induction, put the removed vertex
first — has later-degree at most the subgraph-form degeneracy at every step, because
the subgraph-form degeneracy of an induced subgraph is at most that of the graph. -/

universe u

/-- `G` with the vertex `v` deleted: the subgraph induced on `{u // u ≠ v}`. -/
abbrev deleteVertex (v : V) : SimpleGraph {u : V // u ≠ v} :=
  G.comap (Subtype.val : {u : V // u ≠ v} → V)

instance (v : V) : DecidableRel (deleteVertex G v).Adj :=
  fun a b => ‹DecidableRel G.Adj› a.1 b.1

/-- Deleting a vertex does not raise the subgraph-form degeneracy. -/
theorem degeneracy_deleteVertex_le (v : V) :
    degeneracy (deleteVertex G v) ≤ degeneracy G := by
  apply degeneracy_le_of_forall
  intro S'
  unfold minDegreeIn
  by_cases hS' : S'.Nonempty
  · simp only [dite_eq_left hS']
    have hS : (S'.map (Function.Embedding.subtype _)).Nonempty := Finset.Nonempty.map hS'
    obtain ⟨w, hw, hwmin⟩ :=
      Finset.exists_mem_eq_inf' hS (degreeIn G (S'.map (Function.Embedding.subtype _)))
    obtain ⟨w', hw', rfl⟩ := Finset.mem_map.mp hw
    calc S'.inf' hS' (degreeIn (deleteVertex G v) S')
        ≤ degreeIn (deleteVertex G v) S' w' := Finset.inf'_le _ hw'
      _ = degreeIn G (S'.map (Function.Embedding.subtype _)) (Function.Embedding.subtype _ w') := by
          unfold degreeIn
          rw [Finset.filter_map, Finset.card_map]
          rfl
      _ = (S'.map (Function.Embedding.subtype _)).inf' hS
            (degreeIn G (S'.map (Function.Embedding.subtype _))) := hwmin.symm
      _ ≤ degeneracy G := by
          have h := minDegreeIn_le_degeneracy G (S'.map (Function.Embedding.subtype _))
          unfold minDegreeIn at h
          rwa [dite_eq_left hS] at h
  · simp [dite_eq_right hS']

/-- The greedy elimination ordering, by induction on the number of vertices: some
layout has later-degree at most the subgraph-form degeneracy. -/
theorem exists_layout_maxLaterDegree_le_degeneracy :
    ∀ (n : ℕ) {V : Type u} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
      Fintype.card V = n → ∃ σ : LinearLayout V, maxLaterDegree G σ ≤ degeneracy G := by
  intro n
  induction n with
  | zero =>
    intro V _ _ G _ hn
    refine ⟨Fintype.equivFin V, ?_⟩
    have hempty : IsEmpty V := Fintype.card_eq_zero_iff.mp hn
    exact Finset.sup_le fun x _ => (hempty.false x).elim
  | succ n ih =>
    intro V _ _ G _ hn
    have hne : (Finset.univ : Finset V).Nonempty :=
      Finset.univ_nonempty_iff.mpr (Fintype.card_pos_iff.mp (by omega))
    -- a vertex of minimum degree
    obtain ⟨v, -, hv⟩ := Finset.exists_mem_eq_inf' hne (degreeIn G Finset.univ)
    have hvdeg : degreeIn G Finset.univ v ≤ degeneracy G := by
      rw [← hv]
      have h := minDegreeIn_le_degeneracy G Finset.univ
      unfold minDegreeIn at h
      simpa [dite_eq_left hne] using h
    -- the rest, by induction
    have hW : Fintype.card {u : V // u ≠ v} = n := by
      rw [Fintype.card_subtype, Finset.filter_ne', Finset.card_erase_of_mem (Finset.mem_univ v),
        Finset.card_univ, hn]
      rfl
    obtain ⟨σ', hσ'⟩ := ih (deleteVertex G v) hW
    have hcard : Fintype.card {u : V // u ≠ v} + 1 = Fintype.card V := by omega
    -- `v` first, then the rest in the order `σ'`
    let σ : LinearLayout V :=
      (Equiv.optionSubtypeNe v).symm.trans ((Equiv.optionCongr σ').trans
        ((finSuccEquiv (Fintype.card {u : V // u ≠ v})).symm.trans (finCongr hcard)))
    have hσv : (σ v).val = 0 := by
      simp [σ, finSuccEquiv_symm_none]
    have hσu : ∀ u : {u : V // u ≠ v}, (σ u.1).val = (σ' u).val + 1 := by
      intro u
      simp [σ, Equiv.optionSubtypeNe_symm_of_ne u.2, finSuccEquiv_symm_some]
    refine ⟨σ, ?_⟩
    apply Finset.sup_le
    intro x _
    by_cases hx : x = v
    · subst hx
      calc (laterNeighbors G σ x).card ≤ degreeIn G Finset.univ x := by
            apply Finset.card_le_card
            intro u hu
            rw [mem_laterNeighbors_iff] at hu
            exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hu.1⟩
        _ ≤ degeneracy G := hvdeg
    · have h1 : (σ x).val = (σ' ⟨x, hx⟩).val + 1 := hσu ⟨x, hx⟩
      calc (laterNeighbors G σ x).card
          ≤ ((laterNeighbors (deleteVertex G v) σ' ⟨x, hx⟩).map
              (Function.Embedding.subtype _)).card := by
            apply Finset.card_le_card
            intro u hu
            rw [mem_laterNeighbors_iff] at hu
            have hu_ne : u ≠ v := by
              intro huv
              rw [huv, hσv] at hu
              omega
            have h2 : (σ u).val = (σ' ⟨u, hu_ne⟩).val + 1 := hσu ⟨u, hu_ne⟩
            rw [Finset.mem_map]
            refine ⟨⟨u, hu_ne⟩, ?_, rfl⟩
            rw [mem_laterNeighbors_iff]
            exact ⟨hu.1, by omega⟩
        _ = (laterNeighbors (deleteVertex G v) σ' ⟨x, hx⟩).card := Finset.card_map _
        _ ≤ maxLaterDegree (deleteVertex G v) σ' :=
            card_laterNeighbors_le_maxLaterDegree (deleteVertex G v) σ' ⟨x, hx⟩
        _ ≤ degeneracy (deleteVertex G v) := hσ'
        _ ≤ degeneracy G := degeneracy_deleteVertex_le G v

/-- The converse of `degeneracy_le_orderingDegeneracy`. -/
theorem orderingDegeneracy_le_degeneracy :
    orderingDegeneracy G ≤ degeneracy G := by
  obtain ⟨σ, hσ⟩ := exists_layout_maxLaterDegree_le_degeneracy (Fintype.card V) G rfl
  exact (orderingDegeneracy_le_maxLaterDegree G σ).trans hσ

/-- The two forms of degeneracy coincide. -/
theorem orderingDegeneracy_eq_degeneracy :
    orderingDegeneracy G = degeneracy G :=
  le_antisymm (orderingDegeneracy_le_degeneracy G) (degeneracy_le_orderingDegeneracy G)

/-! ### Tree decompositions -/

/-- A tree decomposition of `G`: a tree `T` on a finite index type with a bag at each
node, covering every vertex and every edge, such that the nodes whose bags contain
any given vertex induce a connected subgraph of `T`. -/
structure TreeDecomposition (G : SimpleGraph V) where
  /-- The index type of the decomposition. -/
  ι : Type
  [instFintype : Fintype ι]
  [instDecidableEq : DecidableEq ι]
  /-- The tree. -/
  T : SimpleGraph ι
  isTree : T.IsTree
  /-- The bag at each node. -/
  bag : ι → Finset V
  vertex_coverage : ∀ v : V, ∃ i, v ∈ bag i
  edge_coverage : ∀ u v : V, G.Adj u v → ∃ i, u ∈ bag i ∧ v ∈ bag i
  /-- The nodes whose bags contain `v` induce a connected subgraph of `T`. -/
  connected : ∀ v : V, (T.induce {i | v ∈ bag i}).Connected

namespace TreeDecomposition

variable {G}

attribute [instance] TreeDecomposition.instFintype TreeDecomposition.instDecidableEq

/-- The width of a tree decomposition: the largest bag size minus one. -/
noncomputable def width (D : TreeDecomposition G) : ℕ :=
  (Finset.univ : Finset D.ι).sup (fun i => (D.bag i).card) - 1

end TreeDecomposition

/-- The treewidth of a graph: the minimum width over tree decompositions. -/
noncomputable def treewidth : ℕ :=
  sInf (Set.range (fun D : TreeDecomposition G => D.width))

section TreeDecompositions

open SimpleGraph

/-! #### The path graph is a tree

Mathlib (as of 2026-09) proves `pathGraph_connected` and nothing about the acyclicity
of `pathGraph`; these lemmas fill that in for the tree decomposition below. -/

theorem pathGraph_isBridge_succ {n : ℕ} (u v : Fin (n + 1)) (h : u.val + 1 = v.val) :
    (pathGraph (n + 1)).IsBridge s(u, v) := by
  rw [isBridge_iff]
  rintro ⟨p⟩
  obtain ⟨d, -, hdS, hdnS⟩ :=
    p.exists_boundary_dart {x : Fin (n + 1) | x.val ≤ u.val} (by simp) (by simp; omega)
  have hadj := d.adj
  rw [deleteEdges_adj, pathGraph_adj] at hadj
  simp only [Set.mem_ofPred_eq, not_le] at hdS hdnS
  apply hadj.2
  rw [Set.mem_singleton_iff, Sym2.eq_iff]
  left
  constructor <;> apply Fin.ext <;> omega

theorem pathGraph_isAcyclic (n : ℕ) : (pathGraph n).IsAcyclic := by
  rw [isAcyclic_iff_forall_adj_isBridge]
  intro u v huv
  cases n with
  | zero => exact u.elim0
  | succ n =>
    rw [pathGraph_adj] at huv
    rcases huv with h | h
    · exact pathGraph_isBridge_succ u v h
    · rw [Sym2.eq_swap]; exact pathGraph_isBridge_succ v u h

theorem pathGraph_isTree (n : ℕ) : (pathGraph (n + 1)).IsTree :=
  ⟨pathGraph_connected n, pathGraph_isAcyclic (n + 1)⟩

theorem pathGraph_induce_interval_connected {n : ℕ} (S : Set (Fin (n + 1)))
    (hS : ∀ i j k : Fin (n + 1), i ≤ j → j ≤ k → i ∈ S → k ∈ S → j ∈ S) (hne : S.Nonempty) :
    ((pathGraph (n + 1)).induce S).Connected := by
  have key : ∀ d : ℕ, ∀ a b : S, b.1.val = a.1.val + d →
      ((pathGraph (n + 1)).induce S).Reachable a b := by
    intro d
    induction d with
    | zero =>
      intro a b h
      have : a = b := Subtype.ext (Fin.ext (by omega))
      rw [this]
    | succ d ih =>
      intro a b h
      have ha1 : a.1.val + 1 < n + 1 := by have := b.1.isLt; omega
      let a' : Fin (n + 1) := ⟨a.1.val + 1, ha1⟩
      have ha'S : a' ∈ S :=
        hS a.1 a' b.1 (Fin.le_def.mpr (Nat.le_succ _))
          (Fin.le_def.mpr (show a.1.val + 1 ≤ b.1.val by omega)) a.2 b.2
      have hadj : ((pathGraph (n + 1)).induce S).Adj a ⟨a', ha'S⟩ := by
        rw [induce_adj, pathGraph_adj]; left; rfl
      exact hadj.reachable.trans (ih ⟨a', ha'S⟩ b (show b.1.val = a.1.val + 1 + d by omega))
  have : Nonempty S := hne.to_subtype
  refine ⟨fun a b => ?_⟩
  rcases le_total a.1.val b.1.val with h | h
  · exact key (b.1.val - a.1.val) a b (by omega)
  · exact (key (a.1.val - b.1.val) b a (by omega)).symm


variable {G}

/-- Every path decomposition is a tree decomposition on the path graph of its indices:
the interval property is exactly the connectivity condition. -/
def PathDecomposition.toTreeDecomposition (P : PathDecomposition G) : TreeDecomposition G where
  ι := Fin (P.length + 1)
  T := pathGraph (P.length + 1)
  isTree := pathGraph_isTree P.length
  bag := P.bag
  vertex_coverage := P.vertex_coverage
  edge_coverage := P.edge_coverage
  connected := fun v => pathGraph_induce_interval_connected _
    (fun i j k hij hjk hi hk => P.interval v i j k hij hjk hi hk)
    (by obtain ⟨i, hi⟩ := P.vertex_coverage v; exact ⟨i, hi⟩)

theorem PathDecomposition.toTreeDecomposition_width (P : PathDecomposition G) :
    P.toTreeDecomposition.width = P.width := by
  simp only [TreeDecomposition.width, PathDecomposition.width, Finset.sup'_eq_sup]
  rfl


theorem treewidth_le_width (P : PathDecomposition G) : treewidth G ≤ P.width := by
  rw [← P.toTreeDecomposition_width]
  exact Nat.sInf_le ⟨P.toTreeDecomposition, rfl⟩

/-- **Item 09's first theorem**, `optimum ≥ tw + 1` through `optimum = pw + 1`:
treewidth is at most pathwidth. -/
theorem treewidth_le_pathwidth : treewidth G ≤ pathwidth G := by
  unfold pathwidth
  apply le_csInf
  · exact ⟨_, ⟨PathDecomposition.trivial G, rfl⟩⟩
  · rintro b ⟨P, rfl⟩
    exact treewidth_le_width P

/-! #### The branch lemma -/

/-- Restricting a path decomposition to the subgraph induced on `A`. -/
def PathDecomposition.restrict (P : PathDecomposition G) (A : Finset V) :
    PathDecomposition (G.induce (↑A : Set V)) where
  length := P.length
  bag := fun i => (P.bag i).subtype (fun x => x ∈ A)
  vertex_coverage := fun v => by
    obtain ⟨i, hi⟩ := P.vertex_coverage v.1
    exact ⟨i, Finset.mem_subtype.mpr hi⟩
  edge_coverage := fun u v h => by
    obtain ⟨i, hu, hv⟩ := P.edge_coverage u.1 v.1 h
    exact ⟨i, Finset.mem_subtype.mpr hu, Finset.mem_subtype.mpr hv⟩
  interval := fun v i j k hij hjk hi hk =>
    Finset.mem_subtype.mpr
      (P.interval v.1 i j k hij hjk (Finset.mem_subtype.mp hi) (Finset.mem_subtype.mp hk))

/-- A connected vertex set with a vertex in a bag at or before `j` and one in a bag at
or after `j` has a vertex in bag `j`: walk from one to the other; consecutive vertices
share a bag, so the first step whose shared bag passes `j` leaves a vertex in bag `j`. -/
theorem PathDecomposition.exists_mem_bag_of_connected (P : PathDecomposition G) (Z : Finset V)
    (hconn : (G.induce (↑Z : Set V)).Connected) {z z' : V} (hz : z ∈ Z) (hz' : z' ∈ Z)
    {b b' j : Fin (P.length + 1)} (hzb : z ∈ P.bag b) (hz'b' : z' ∈ P.bag b')
    (hbj : b ≤ j) (hjb' : j ≤ b') : ∃ w ∈ Z, w ∈ P.bag j := by
  have key : ∀ (u w : (↑Z : Set V)) (_ : (G.induce (↑Z : Set V)).Walk u w)
      (b : Fin (P.length + 1)), u.1 ∈ P.bag b → b ≤ j →
      (∃ b', w.1 ∈ P.bag b' ∧ j ≤ b') → ∃ x ∈ Z, x ∈ P.bag j := by
    intro u w p
    induction p with
    | @nil u =>
      intro b hub hbj ⟨b', hwb', hjb'⟩
      exact ⟨_, Finset.mem_coe.mp u.2, P.interval _ b j b' hbj hjb' hub hwb'⟩
    | @cons x y w' hxy p ih =>
      intro b hxb hbj hw
      obtain ⟨c, hxc, hyc⟩ := P.edge_coverage x.1 y.1 hxy
      rcases le_or_gt c j with hcj | hjc
      · exact ih c hyc hcj hw
      · exact ⟨x.1, Finset.mem_coe.mp x.2, P.interval x.1 b j c hbj hjc.le hxb hxc⟩
  obtain ⟨p⟩ := hconn.preconnected ⟨z, Finset.mem_coe.mpr hz⟩ ⟨z', Finset.mem_coe.mpr hz'⟩
  exact key _ _ p b hzb hbj ⟨b', hz'b', hjb'⟩

/-- The middle bag. Three bags `iX < iY < iZ`, the middle one inside `Y`, the outer two
meeting `X` and `Z`; `v ∉ Y` is adjacent to both `X` and `Z`, which are connected. Then
`v`'s interval avoids `iY`, so it lies on one side; the branch on the other side is
joined to `v` there and to its own bag beyond `iY`, and crosses bag `iY` — impossible. -/
theorem PathDecomposition.middle_bag_false (P : PathDecomposition G) (v : V) (X Y Z : Finset V)
    (hvY : v ∉ Y) (hXY : Disjoint X Y) (hYZ : Disjoint Y Z)
    (hconnX : (G.induce (↑X : Set V)).Connected) (hconnZ : (G.induce (↑Z : Set V)).Connected)
    (hadjX : ∃ x ∈ X, G.Adj v x) (hadjZ : ∃ z ∈ Z, G.Adj v z)
    {iX iY iZ : Fin (P.length + 1)} (h1 : iX < iY) (h2 : iY < iZ)
    (hX : ∃ x ∈ X, x ∈ P.bag iX) (hY : P.bag iY ⊆ Y) (hZ : ∃ z ∈ Z, z ∈ P.bag iZ) : False := by
  have hvY' : v ∉ P.bag iY := fun h => hvY (hY h)
  rw [P.mem_bag_iff_between, not_and_or, not_le, not_le] at hvY'
  rcases hvY' with hlt | hlt
  · obtain ⟨x, hxX, hvx⟩ := hadjX
    obtain ⟨c, hvc, hxc⟩ := P.edge_coverage v x hvx
    have hc : P.firstBag v ≤ c := ((P.mem_bag_iff_between v c).mp hvc).1
    obtain ⟨x', hx'X, hx'⟩ := hX
    obtain ⟨w, hwX, hw⟩ :=
      P.exists_mem_bag_of_connected X hconnX hx'X hxX hx' hxc h1.le (hlt.le.trans hc)
    exact Finset.disjoint_left.mp hXY hwX (hY hw)
  · obtain ⟨z, hzZ, hvz⟩ := hadjZ
    obtain ⟨c, hvc, hzc⟩ := P.edge_coverage v z hvz
    have hc : c ≤ P.lastBag v := ((P.mem_bag_iff_between v c).mp hvc).2
    obtain ⟨z', hz'Z, hz'⟩ := hZ
    obtain ⟨w, hwZ, hw⟩ :=
      P.exists_mem_bag_of_connected Z hconnZ hzZ hz'Z hzc hz' (hc.trans hlt.le) h2.le
    exact Finset.disjoint_left.mp hYZ (hY hw) hwZ

/-- A full bag. If the subgraph induced on `A` has pathwidth at least `k` and `P` has
width at most `k`, some bag of `P` consists of vertices of `A` only, and is nonempty:
restricting `P` to `A` gives a decomposition of `G[A]`, whose largest bag has at least
`k + 1` vertices of `A`, and no bag of `P` has more than `k + 1` vertices. -/
theorem PathDecomposition.exists_bag_subset_of_le_pathwidth_induce (P : PathDecomposition G)
    (A : Finset V) (hAne : A.Nonempty) (k : ℕ) (hA : k ≤ pathwidth (G.induce (↑A : Set V)))
    (hw : P.width ≤ k) : ∃ i, P.bag i ⊆ A ∧ (P.bag i).Nonempty := by
  have hle : k ≤ (P.restrict A).width := hA.trans (pathwidth_le_width _ (P.restrict A))
  unfold PathDecomposition.width at hle
  obtain ⟨i, -, hi⟩ := Finset.exists_mem_eq_sup' (Finset.univ_nonempty_iff.mpr
    ⟨⟨0, Nat.zero_lt_succ _⟩⟩) (fun i : Fin ((P.restrict A).length + 1) => ((P.restrict A).bag i).card)
  rw [hi] at hle
  have hpos : 1 ≤ ((P.restrict A).bag i).card := by
    obtain ⟨a, ha⟩ := hAne
    obtain ⟨j, hj⟩ := P.vertex_coverage a
    have h1 : 1 ≤ ((P.restrict A).bag j).card :=
      Finset.card_pos.mpr ⟨⟨a, ha⟩, Finset.mem_subtype.mpr hj⟩
    rw [← hi]
    exact h1.trans (Finset.le_sup' (fun i : Fin ((P.restrict A).length + 1) =>
      ((P.restrict A).bag i).card) (Finset.mem_univ j))
  have hcard : k + 1 ≤ ((P.bag i).filter (fun x => x ∈ A)).card := by
    have : ((P.restrict A).bag i).card = ((P.bag i).filter (fun x => x ∈ A)).card :=
      Finset.card_subtype _ _
    omega
  have hbag : (P.bag i).card ≤ k + 1 :=
    (P.bag_card_le_width_add_one i).trans (Nat.succ_le_succ hw)
  have heq : (P.bag i).filter (fun x => x ∈ A) = P.bag i :=
    Finset.eq_of_subset_of_card_le (Finset.filter_subset _ _) (by omega)
  have hcard' := congrArg Finset.card heq
  refine ⟨i, fun x hx => ?_, Finset.card_pos.mp (by omega)⟩
  rw [← heq] at hx
  exact (Finset.mem_filter.mp hx).2

/-- **The pathwidth branch lemma** (Fellows & Langston 1987, Lemma 4.3; Kinnersley 1992,
Corollary 4.2 and the remark before Theorem 4.3). Three pairwise disjoint, connected
vertex sets, each of pathwidth at least `k` and each adjacent to a vertex `v` outside
them, force pathwidth at least `k + 1`. In a decomposition of width `k` each branch fills
a bag of its own; `v` avoids the middle one, and the branch on the far side of it from `v`
would have to cross it (`middle_bag_false`). No hypothesis on edges between the branches
is needed. -/
theorem branch_lemma (v : V) (A B D : Finset V) (k : ℕ)
    (hvA : v ∉ A) (hvB : v ∉ B) (hvD : v ∉ D)
    (hAB : Disjoint A B) (hAD : Disjoint A D) (hBD : Disjoint B D)
    (hconnA : (G.induce (↑A : Set V)).Connected) (hconnB : (G.induce (↑B : Set V)).Connected)
    (hconnD : (G.induce (↑D : Set V)).Connected)
    (hadjA : ∃ a ∈ A, G.Adj v a) (hadjB : ∃ b ∈ B, G.Adj v b) (hadjD : ∃ d ∈ D, G.Adj v d)
    (hA : k ≤ pathwidth (G.induce (↑A : Set V))) (hB : k ≤ pathwidth (G.induce (↑B : Set V)))
    (hD : k ≤ pathwidth (G.induce (↑D : Set V))) :
    k + 1 ≤ pathwidth G := by
  have hne : (Set.range (fun P : PathDecomposition G => P.width)).Nonempty :=
    ⟨_, PathDecomposition.trivial G, rfl⟩
  obtain ⟨P, hP⟩ := Nat.sInf_mem hne
  change P.width = pathwidth G at hP
  rw [← hP]
  by_contra hcon
  have hw : P.width ≤ k := by omega
  obtain ⟨iA, hiA, hneA⟩ := P.exists_bag_subset_of_le_pathwidth_induce A
    (by obtain ⟨a, ha, -⟩ := hadjA; exact ⟨a, ha⟩) k hA hw
  obtain ⟨iB, hiB, hneB⟩ := P.exists_bag_subset_of_le_pathwidth_induce B
    (by obtain ⟨b, hb, -⟩ := hadjB; exact ⟨b, hb⟩) k hB hw
  obtain ⟨iD, hiD, hneD⟩ := P.exists_bag_subset_of_le_pathwidth_induce D
    (by obtain ⟨d, hd, -⟩ := hadjD; exact ⟨d, hd⟩) k hD hw
  have hA' : ∃ a ∈ A, a ∈ P.bag iA := by obtain ⟨a, ha⟩ := hneA; exact ⟨a, hiA ha, ha⟩
  have hB' : ∃ b ∈ B, b ∈ P.bag iB := by obtain ⟨b, hb⟩ := hneB; exact ⟨b, hiB hb, hb⟩
  have hD' : ∃ d ∈ D, d ∈ P.bag iD := by obtain ⟨d, hd⟩ := hneD; exact ⟨d, hiD hd, hd⟩
  have nAB : iA ≠ iB := fun h => by
    subst h; obtain ⟨x, hx⟩ := hneA; exact Finset.disjoint_left.mp hAB (hiA hx) (hiB hx)
  have nAD : iA ≠ iD := fun h => by
    subst h; obtain ⟨x, hx⟩ := hneA; exact Finset.disjoint_left.mp hAD (hiA hx) (hiD hx)
  have nBD : iB ≠ iD := fun h => by
    subst h; obtain ⟨x, hx⟩ := hneB; exact Finset.disjoint_left.mp hBD (hiB hx) (hiD hx)
  rcases lt_or_gt_of_ne nAB with hab | hab <;> rcases lt_or_gt_of_ne nAD with had | had <;>
    rcases lt_or_gt_of_ne nBD with hbd | hbd <;>
    first
    | exact P.middle_bag_false v A B D hvB hAB hBD hconnA hconnD hadjA hadjD hab hbd hA' hiB hD'
    | exact P.middle_bag_false v A D B hvD hAD hBD.symm hconnA hconnB hadjA hadjB had hbd hA' hiD hB'
    | exact P.middle_bag_false v D A B hvA hAD.symm hAB hconnD hconnB hadjD hadjB had hab hD' hiA hB'
    | exact P.middle_bag_false v B A D hvA hAB.symm hAD hconnB hconnD hadjB hadjD hab had hB' hiA hD'
    | exact P.middle_bag_false v B D A hvD hBD hAD.symm hconnB hconnA hadjB hadjA hbd had hB' hiD hA'
    | exact P.middle_bag_false v D B A hvB hBD.symm hAB.symm hconnD hconnA hadjD hadjA hbd hab hD' hiB hA'


/-- The branch lemma with the branches' treewidth in place of their pathwidth
(the form `reports/ml_nature.md` §24 states), through `treewidth_le_pathwidth`. -/
theorem branch_lemma_treewidth (v : V) (A B D : Finset V) (k : ℕ)
    (hvA : v ∉ A) (hvB : v ∉ B) (hvD : v ∉ D)
    (hAB : Disjoint A B) (hAD : Disjoint A D) (hBD : Disjoint B D)
    (hconnA : (G.induce (↑A : Set V)).Connected) (hconnB : (G.induce (↑B : Set V)).Connected)
    (hconnD : (G.induce (↑D : Set V)).Connected)
    (hadjA : ∃ a ∈ A, G.Adj v a) (hadjB : ∃ b ∈ B, G.Adj v b) (hadjD : ∃ d ∈ D, G.Adj v d)
    (hA : k ≤ treewidth (G.induce (↑A : Set V))) (hB : k ≤ treewidth (G.induce (↑B : Set V)))
    (hD : k ≤ treewidth (G.induce (↑D : Set V))) :
    k + 1 ≤ pathwidth G :=
  branch_lemma v A B D k hvA hvB hvD hAB hAD hBD hconnA hconnB hconnD hadjA hadjB hadjD
    (hA.trans (treewidth_le_pathwidth (G := G.induce (↑A : Set V))))
    (hB.trans (treewidth_le_pathwidth (G := G.induce (↑B : Set V))))
    (hD.trans (treewidth_le_pathwidth (G := G.induce (↑D : Set V))))

end TreeDecompositions

namespace MOSPInstance

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]
variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- `optimum ≥ treewidth + 1` over the MOSP graph — the theorem `reports/ml_nature.md`
§21 uses as the honest reference for the bound work — whenever some customer requires
some pattern. -/
theorem treewidth_add_one_le_mospValue (h : ∃ c p, M.requires c p) :
    treewidth M.mospGraph + 1 ≤ M.mospValue := by
  rw [M.mospValue_eq_pathwidth_add_one h]
  exact Nat.add_le_add_right treewidth_le_pathwidth 1

end MOSPInstance

/-! ### Statements without proofs -/

/-- `f(t)`: the smallest closed neighbourhood of a set of `t` vertices (`0` when no
such set exists). The expansion bound of `satisfiability/expansion_bound.py`. -/
noncomputable def minClosedNeighborhood (t : ℕ) : ℕ :=
  sInf ((fun S : Finset V => (S ∪ S.biUnion (fun v => Finset.univ.filter (G.Adj v))).card) ''
    {S | S.card = t})

/-- **Item 09's surviving fitted candidate**, stated as a conjecture with the optimum
read as `pathwidth + 1`. Valid on 50,948 certified instances, undefeated by 20,100
adversarial evaluations, and pointwise at most `max(lb_best, tw + 1)` on every one of
them, so proving it would prove nothing new (`reports/ml_nature.md` §24). -/
theorem conjecture_sqrt_tw_f6 (hV : 6 ≤ Fintype.card V) :
    ⌊(0.9428 : ℝ) * Real.sqrt ((treewidth G : ℝ) * (minClosedNeighborhood G 6 : ℝ))⌋₊
      ≤ pathwidth G + 1 := by
  sorry

/-! ### Hand-checked values

The definitions above are only worth the theorems about them if they compute the
textbook quantities. `learning/sandwich.py` brute-forces the same definitions in
Python and compares them with networkx on every graph on at most five vertices;
these are the smallest cases, decided in the kernel. -/

/-- The path on three vertices, `0 – 1 – 2`. -/
def path3 : SimpleGraph (Fin 3) where
  Adj a b := a.val + 1 = b.val ∨ b.val + 1 = a.val
  symm := ⟨fun {a b} h => by omega⟩
  loopless := ⟨fun a h => by omega⟩

instance : DecidableRel path3.Adj := fun a b => by unfold path3; simp only; infer_instance

/-- The identity layout `0, 1, 2`. -/
def idLayout3 : LinearLayout (Fin 3) := Equiv.refl _

example : degeneracy path3 = 1 := by decide
example : minDegreeIn path3 Finset.univ = 1 := by decide
example : maxLaterDegree path3 idLayout3 = 1 := by decide
example : vertexSepAt path3 idLayout3 0 = 1 := by decide
example : bandwidthOfLayout path3 idLayout3 = 1 := by decide
/-- The triangle: every vertex has degree 2 in the whole graph, and a layout stretches
one edge across the middle vertex. -/
example : degeneracy (⊤ : SimpleGraph (Fin 3)) = 2 := by decide
example : bandwidthOfLayout (⊤ : SimpleGraph (Fin 3)) idLayout3 = 2 := by decide
/-- No edges: every quantity is zero. -/
example : degeneracy (⊥ : SimpleGraph (Fin 3)) = 0 := by decide
example : bandwidthOfLayout (⊥ : SimpleGraph (Fin 3)) idLayout3 = 0 := by decide

/-- The spider `K_{1,3}` with every edge subdivided: `0` is the centre, `1 2 3` its
neighbours, `4 5 6` the leaves. Treewidth 1, pathwidth 2 — the smallest classic gap. -/
def spider : SimpleGraph (Fin 7) where
  Adj a b := (a.val = 0 ∧ 1 ≤ b.val ∧ b.val ≤ 3) ∨ (b.val = 0 ∧ 1 ≤ a.val ∧ a.val ≤ 3)
    ∨ (a.val + 3 = b.val ∧ 1 ≤ a.val) ∨ (b.val + 3 = a.val ∧ 1 ≤ b.val)
  symm := ⟨fun {a b} h => by omega⟩
  loopless := ⟨fun a h => by omega⟩

instance : DecidableRel spider.Adj := fun a b => by unfold spider; simp only; infer_instance

/-- The identity layout: centre first, then its neighbours, then the leaves. -/
def spiderLayout : LinearLayout (Fin 7) := Equiv.refl _

-- Degeneracy 1 (a forest), decided over all 128 vertex subsets.
set_option maxRecDepth 10000 in
example : degeneracy spider = 1 := by decide
-- Centre first: three neighbours placed after it, and three active after the cut.
example : maxLaterDegree spider spiderLayout = 3 := by decide
example : vertexSepAt spider spiderLayout 0 = 3 := by decide
example : bandwidthOfLayout spider spiderLayout = 3 := by decide

/-! ### The counterexample to the statement without attachment -/

/-- Four isolated vertices have pathwidth `0`: one singleton bag each. -/
theorem pathwidth_bot_fin4 : pathwidth (⊥ : SimpleGraph (Fin 4)) = 0 := by
  apply Nat.eq_zero_of_le_zero
  let P : PathDecomposition (⊥ : SimpleGraph (Fin 4)) :=
    { length := 3
      bag := fun i => {i}
      vertex_coverage := fun v => ⟨v, Finset.mem_singleton_self v⟩
      edge_coverage := fun _ _ h => h.elim
      interval := fun v i j k hij hjk hi hk => by
        rw [Finset.mem_singleton] at hi hk ⊢
        subst hi
        exact le_antisymm (hk ▸ hjk) hij |>.symm }
  calc pathwidth ⊥ ≤ P.width := pathwidth_le_width _ P
    _ = 0 := by
      simp [PathDecomposition.width, P]

/-- The branch statement **without** attachment and connectivity is false: for four
isolated vertices, `v = 0` and the singleton branches `{1}`, `{2}`, `{3}`, every
hypothesis of the old `branch_lemma` holds with `k = 0` (the branches are pairwise
non-adjacent and have treewidth `≥ 0`), but the pathwidth is `0`, not `≥ 1`. -/
theorem old_branch_statement_false :
    ¬ (∀ (v : Fin 4) (A B D : Finset (Fin 4)) (k : ℕ), v ∉ A → v ∉ B → v ∉ D →
        Disjoint A B → Disjoint A D → Disjoint B D →
        (∀ a b, a ∈ A → b ∈ B ∪ D → ¬ (⊥ : SimpleGraph (Fin 4)).Adj a b) →
        (∀ b d, b ∈ B → d ∈ D → ¬ (⊥ : SimpleGraph (Fin 4)).Adj b d) →
        k ≤ treewidth ((⊥ : SimpleGraph (Fin 4)).induce (↑A : Set (Fin 4))) →
        k ≤ treewidth ((⊥ : SimpleGraph (Fin 4)).induce (↑B : Set (Fin 4))) →
        k ≤ treewidth ((⊥ : SimpleGraph (Fin 4)).induce (↑D : Set (Fin 4))) →
        k + 1 ≤ pathwidth (⊥ : SimpleGraph (Fin 4))) := by
  intro h
  have := h 0 {1} {2} {3} 0 (by decide) (by decide) (by decide) (by decide) (by decide) (by decide)
    (fun _ _ _ _ h => h) (fun _ _ _ _ h => h) (Nat.zero_le _) (Nat.zero_le _) (Nat.zero_le _)
  rw [pathwidth_bot_fin4] at this
  omega

end MOSPFormalization
