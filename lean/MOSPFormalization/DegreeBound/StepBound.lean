/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The unconditional pathwidth cost of a series-parallel reduction (R6)

loop0012 item 11 (reserve), option (3) of its brief: the per-step bound
`pw(H) ≤ pw(H') + 1` for one series-parallel operation, and what follows from it for a whole
reduction with no hypothesis at all. **This is not the reduction lemma (H3)** of
`DegreeBound/Pathwidth.lean` (`ReductionPathwidthBound ρ`, Kneis, Mölle, Richter &
Rossmanith 2009): (H3) charges a reduction `o(n)` — the paper's `O(log n)` — while the bounds
here charge **one per removed vertex**, which is the trivial budget `ρ n = n` and useless for
Corollary 5.2. They are recorded because they are unconditional, cost nothing, and bound the
same quantity.

* `SPStep.isolate_le` — a step at `v` keeps every edge away from `v`: `G − v ≤ H`.
* `SPStep.pathwidth_le` — **R6**: `pathwidth G ≤ pathwidth H + 1` for every step
  (`pathwidth_le_pathwidth_isolate_add_one` and `pathwidth_mono`).
* `SPStep.ndeg_eq_zero`, `SPStep.supp_ssubset` — the acted vertex is isolated afterwards, so
  the support strictly shrinks.
* `SPReduces.adj_of_adj_of_ndeg_pos` — an edge of `G` between two vertices still of positive
  degree in the reduct `H` is an edge of `H` (edges are only ever removed at the acted vertex,
  which stays isolated: `SPReduces.ndeg_eq_zero`).
* `SPReduces.isolateSet_sdiff_le` — `G − (supp G ∖ supp H) ≤ H`.
* `SPReduces.pathwidth_le_add_card_sdiff` — `pathwidth G ≤ pathwidth H + |supp G ∖ supp H|`,
  and `SPReduces.pathwidth_add_card_supp_le`, the same without truncated subtraction:
  `pathwidth G + |supp H| ≤ pathwidth H + |supp G|`.

Checked by brute force before being stated (`reports/scratch/edwards_mcdermid/11_reserve/check.py`,
Part B: every graph on 1–8 vertices, every step vertex, one random maximal reduction per graph,
every prefix; zero violations). Item 02 had R6 on every step of every graph to 9 vertices.
-/
import MOSPFormalization.DegreeBound.Pathwidth

set_option linter.unusedSectionVars false

namespace MOSPFormalization.DegreeBound

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

namespace SPStep

variable {G H : SimpleGraph V} {v : V}

/-- A step at `v` keeps every edge away from `v`: `G − v ≤ H`. -/
theorem isolate_le (h : SPStep G v H) : isolate G v ≤ H := by
  cases h with
  | pendant _ _ => exact le_rfl
  | suppress _ _ _ _ _ => exact le_sup_left
  | triangle _ _ _ _ _ => exact le_rfl

/-- Edges away from the acted vertex survive the step. -/
theorem adj_of_adj (h : SPStep G v H) {a b : V} (hab : G.Adj a b) (ha : a ≠ v) (hb : b ≠ v) :
    H.Adj a b :=
  h.isolate_le ((isolate_adj G v a b).2 ⟨hab, ha, hb⟩)

/-- **R6**: one series-parallel operation costs at most one in pathwidth. -/
theorem pathwidth_le (h : SPStep G v H) : pathwidth G ≤ pathwidth H + 1 :=
  (pathwidth_le_pathwidth_isolate_add_one G v).trans
    (Nat.add_le_add_right (pathwidth_mono h.isolate_le) 1)

/-- The acted vertex is isolated after the step. -/
theorem ndeg_eq_zero (h : SPStep G v H) : ndeg H v = 0 := by
  cases h with
  | pendant _ _ => exact ndeg_isolate_self G v
  | triangle _ _ _ _ _ => exact ndeg_isolate_self G v
  | @suppress x y hx hy _ _ _ =>
    rw [ndeg_eq_zero_iff]
    intro z hz
    rw [SimpleGraph.sup_adj, isolate_adj, SimpleGraph.edge_adj] at hz
    rcases hz with ⟨_, hvv, _⟩ | ⟨⟨rfl, _⟩ | ⟨rfl, _⟩, _⟩
    · exact hvv rfl
    · exact hx.ne rfl
    · exact hy.ne rfl

/-- The support strictly shrinks at every step. -/
theorem supp_ssubset [DecidableRel G.Adj] [DecidableRel H.Adj] (h : SPStep G v H) :
    supp H ⊂ supp G := by
  refine Finset.ssubset_iff_subset_ne.2 ⟨(SPReduces.single h).supp_subset, fun heq => ?_⟩
  have hv : v ∈ supp G := mem_supp_iff_exists_adj.2 h.exists_adj
  rw [← heq, mem_supp, ← ndeg_eq_degree, h.ndeg_eq_zero] at hv
  exact lt_irrefl 0 hv

end SPStep

namespace SPReduces

variable {G H : SimpleGraph V}

/-- An edge of `G` between two vertices that still have positive degree in the reduct `H`
is an edge of `H`: edges are only removed at the acted vertex, which stays isolated. -/
theorem adj_of_adj_of_ndeg_pos (h : SPReduces G H) {a b : V} (hab : G.Adj a b)
    (ha : 0 < ndeg H a) (hb : 0 < ndeg H b) : H.Adj a b := by
  unfold SPReduces at h
  revert hab
  induction h using Relation.ReflTransGen.head_induction_on with
  | refl => exact fun hab => hab
  | @head G' K hstep h' ih =>
    intro hab
    obtain ⟨v, hstep⟩ := hstep
    have hv : ndeg H v = 0 := SPReduces.ndeg_eq_zero h' hstep.ndeg_eq_zero
    refine ih (hstep.adj_of_adj hab ?_ ?_)
    · rintro rfl; rw [hv] at ha; exact lt_irrefl 0 ha
    · rintro rfl; rw [hv] at hb; exact lt_irrefl 0 hb

/-- `G − (supp G ∖ supp H) ≤ H`: deleting the vertices a reduction removes leaves a subgraph
of the reduct. -/
theorem isolateSet_sdiff_le [DecidableRel G.Adj] [DecidableRel H.Adj] (h : SPReduces G H) :
    isolateSet G (supp G \ supp H) ≤ H := by
  intro a b hab
  rw [isolateSet_adj] at hab
  obtain ⟨hab, ha, hb⟩ := hab
  have ha' : a ∈ supp H := by
    by_contra hna
    exact ha (Finset.mem_sdiff.2 ⟨mem_supp_iff_exists_adj.2 ⟨b, hab⟩, hna⟩)
  have hb' : b ∈ supp H := by
    by_contra hnb
    exact hb (Finset.mem_sdiff.2 ⟨mem_supp_iff_exists_adj.2 ⟨a, hab.symm⟩, hnb⟩)
  rw [mem_supp, ← ndeg_eq_degree] at ha' hb'
  exact h.adj_of_adj_of_ndeg_pos hab ha' hb'

/-- The unconditional pathwidth bound along a reduction: one per removed vertex. **Not**
the reduction lemma (H3), whose budget is `o(n)`. -/
theorem pathwidth_le_add_card_sdiff [DecidableRel G.Adj] [DecidableRel H.Adj]
    (h : SPReduces G H) : pathwidth G ≤ pathwidth H + (supp G \ supp H).card :=
  (pathwidth_le_pathwidth_isolateSet_add_card G _).trans
    (Nat.add_le_add_right (pathwidth_mono h.isolateSet_sdiff_le) _)

/-- The same bound without truncated subtraction. -/
theorem pathwidth_add_card_supp_le [DecidableRel G.Adj] [DecidableRel H.Adj]
    (h : SPReduces G H) : pathwidth G + (supp H).card ≤ pathwidth H + (supp G).card := by
  have h1 := h.pathwidth_le_add_card_sdiff
  have h2 : (supp G \ supp H).card = (supp G).card - (supp H).card :=
    Finset.card_sdiff_of_subset h.supp_subset
  have h3 : (supp H).card ≤ (supp G).card := Finset.card_le_card h.supp_subset
  omega

end SPReduces

end MOSPFormalization.DegreeBound
