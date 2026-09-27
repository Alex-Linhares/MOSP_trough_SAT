/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The pattern-graph reduction, withdrawn

This file used to state

  `mosp_le_pathwidth_add_one : M.IsReduced → M.mospValue ≤ pathwidth M.agreementGraph + 1`

with a `sorry` in its core step (`openStacksAt_le_bag_card`, "needs Hall's
theorem"), together with `maxOpenStacks_le_width_add_one`,
`mospValue_le_width_add_one` and a tightness claim
`exists_instance_achieving_equality`, also `sorry`. **All of them are false**,
which is why the `sorry` could never be closed: the agreement graph has
*patterns* as vertices, and the pathwidth equivalence of Yanasse (1997c) is about
the **MOSP graph**, whose vertices are *customers* (see `CLAUDE.md`, "Terminology
Correction"). They have been deleted rather than left standing as open gaps.

Counterexample (`MOSPGraphExamples.lean`, `star_refutes_pattern_graph_bound`):
one pattern `p` and four customers `c₁, …, c₄` with `c_j` requiring `{p, q_j}`.
The instance is reduced, every order produces `p` at some step and all four
stacks are open there, so `mospValue = 4`; the agreement graph is the star
`K_{1,4}`, of pathwidth `1`, so `pathwidth + 1 = 2`.

The true theorem, `mospValue = pathwidth (mospGraph) + 1` whenever some
customer requires some pattern, is proved without `sorry` in `MOSPGraph.lean`
(`MOSPInstance.mospValue_eq_pathwidth_add_one`); it needs no `IsReduced`.

What remains below is the one lemma of the old development that is true: an
agreement-graph observation about the active suffix, kept because it is correct
and self-contained, though nothing depends on it.
-/

import MOSPFormalization.VSEquivPW
import MOSPFormalization.OpenStacks

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]

namespace MOSPInstance

variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- A customer with a pattern at or before `i` and one strictly after `i` has a
    pattern in the active suffix of the agreement graph.

    The strict hypothesis is stated explicitly rather than taken from
    `isActive`, which no longer implies it. `isActive` is inclusive at both
    ends, so a customer requiring a single pattern is active at that pattern's
    own position while having nothing strictly beyond it — and the argument
    below needs two distinct patterns, one on each side. Such a customer opens
    and closes in one step and never contributes to a separator, so nothing is
    lost; it simply is not this lemma's business. -/
theorem active_customer_has_activeSuffix_pattern (σ : LinearLayout Pt) (c : C) (i : ℕ)
    (hpre : ((M.patterns c).filter (fun p => (σ p).val ≤ i)).Nonempty)
    (hsuf : ((M.patterns c).filter (fun p => (σ p).val > i)).Nonempty) :
    ∃ p, M.requires c p ∧ p ∈ activeSuffix M.agreementGraph σ i := by
  obtain ⟨p, hp⟩ := hsuf
  obtain ⟨q, hq⟩ := hpre
  have hp_mem := Finset.mem_filter.mp hp
  have hq_mem := Finset.mem_filter.mp hq
  have hp_req : M.requires c p := (Finset.mem_filter.mp hp_mem.1).2
  have hq_req : M.requires c q := (Finset.mem_filter.mp hq_mem.1).2
  refine ⟨p, hp_req, ?_⟩
  rw [mem_activeSuffix_iff]
  exact ⟨hp_mem.2, q, by rw [mem_prefixSet_iff]; exact hq_mem.2,
    ⟨fun heq => by subst heq; omega, c, hq_req, hp_req⟩⟩

end MOSPInstance

end MOSPFormalization
