/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Chu & Stuckey's Theorems 1 and 2 are false, stated as published

Chu & Stuckey, *Minimizing the maximum number of open stacks by customer
search*, CP 2009, §3.2:

> **Theorem 1.** Suppose `S ++ [q]` is playable and `close(q, S) ≥ open(q, S)`,
> then if `U′ = S ++ R` is a solution, there exists a solution `U = S ++ [q] ++ R′`.

> **Theorem 2.** Suppose `S ++ [q]` and `S ++ [r, q]` are playable and
> `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})` then if `U′ = S ++ [r] ++ R` is a
> solution there exists a solution `U = S ++ [q] ++ R′`.

`DefiniteMove.lean` and `BetterMove.lean` prove the counterexamples
(`definiteMove_counterexample`, `betterMove_counterexample`) in the search's own
terms, with the "no solution" half stated at the free-closed child. This file
states each published implication as a universal claim and proves it false,
with the bridge from the child to `S ∪ {q}` (free moves never hurt,
`solvable_cl`) inside the proof, so a reader can check the refutation against
the published wording directly.

**Reading of the statements.** A solution `S ++ [q] ++ R′` exists exactly when
`S ++ [q]` is playable and `Solvable G k (insert q S)` (`Solvable` asks for some
ordering of the remaining customers after the given closed set, every step
within `k`). `open` is `openCount`. For `close` there are two readings:

* `closeCount`, the customers not yet closed whose new stacks all open with
  `q`'s: the code's reading, and the paper's proof's;
* `closeCountLiteral`, every customer whose new stacks do, closed ones
  included: the literal reading of the paper's definition.

Since `closeCount ≤ closeCountLiteral` (`closeCount_le_closeCountLiteral`), the
literal premise is the weaker one, and both theorems are false under both
readings.

## Main results

* `chuStuckey_theorem1_false`, `chuStuckey_theorem1_false_literal`;
* `chuStuckey_theorem2_false`, `chuStuckey_theorem2_false_literal`.
-/

import MOSPFormalization.Search.BetterMove

namespace MOSPFormalization

namespace Search

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- `close(q, S)` read literally: every customer, closed ones included, whose new stacks
all open with `q`'s. -/
def closeCountLiteral (S : Finset V) (q : V) : ℕ :=
  (univ.filter (fun d => newlyOpened G S d ⊆ newlyOpened G S q)).card

/-- The code's count never exceeds the literal one, so the literal premise is weaker. -/
theorem closeCount_le_closeCountLiteral (S : Finset V) (q : V) :
    closeCount G S q ≤ closeCountLiteral G S q := by
  unfold closeCount closeCountLiteral
  exact card_le_card (filter_subset_filter _ (subset_univ _))

/-- **Chu & Stuckey's Theorem 1 is false** (the code's reading of `close`): on the
14-customer `cexGraph` with `k = 6`, the premises hold at `S = {2}`, `q = 0`, a solution
from `S` exists, and none begins with `q`. -/
theorem chuStuckey_theorem1_false :
    ¬ ∀ (S : Finset (Fin 14)) (q : Fin 14), q ∉ S → stepCost cexGraph S q ≤ 6 →
        openCount cexGraph S q ≤ closeCount cexGraph S q →
        Solvable cexGraph 6 S → Solvable cexGraph 6 (insert q S) := by
  intro h
  have hsol := h {2} 0 (by decide) (by decide) (by decide) cex_solvable
  exact cex_not_solvable_child (solvable_cl (G := cexGraph) hsol)

/-- **Chu & Stuckey's Theorem 1 is false**, under the literal reading of `close` too. -/
theorem chuStuckey_theorem1_false_literal :
    ¬ ∀ (S : Finset (Fin 14)) (q : Fin 14), q ∉ S → stepCost cexGraph S q ≤ 6 →
        openCount cexGraph S q ≤ closeCountLiteral cexGraph S q →
        Solvable cexGraph 6 S → Solvable cexGraph 6 (insert q S) := by
  intro h
  exact chuStuckey_theorem1_false fun S q hq hp hd hs =>
    h S q hq hp (hd.trans (closeCount_le_closeCountLiteral cexGraph S q)) hs

/-- **Chu & Stuckey's Theorem 2 is false** (the code's reading of `close`): on `cexGraph`
with `k = 6`, take `S = ∅`, `r = 2`, `q = 0`. `S ++ [q]` and `S ++ [r, q]` are playable,
`close(q, S ∪ {r}) ≥ open(q, S ∪ {r})`, a solution `S ++ [r] ++ R` exists, and none begins
with `q`. -/
theorem chuStuckey_theorem2_false :
    ¬ ∀ (S : Finset (Fin 14)) (r q : Fin 14), r ∉ S → q ∉ S → r ≠ q →
        stepCost cexGraph S q ≤ 6 → stepCost cexGraph S r ≤ 6 →
        stepCost cexGraph (insert r S) q ≤ 6 →
        openCount cexGraph (insert r S) q ≤ closeCount cexGraph (insert r S) q →
        Solvable cexGraph 6 (insert r S) → Solvable cexGraph 6 (insert q S) := by
  intro h
  have h2 : Solvable cexGraph 6 (insert (2 : Fin 14) ∅) := by simpa using cex_solvable
  have hsol := h ∅ 2 0 (by decide) (by decide) (by decide) (by decide) (by decide)
    (by decide) (by decide) h2
  exact bm_not_searchSol_zero (searchSol_cl_of_solvable (G := cexGraph) _ _ le_rfl hsol)

/-- **Chu & Stuckey's Theorem 2 is false**, under the literal reading of `close` too. -/
theorem chuStuckey_theorem2_false_literal :
    ¬ ∀ (S : Finset (Fin 14)) (r q : Fin 14), r ∉ S → q ∉ S → r ≠ q →
        stepCost cexGraph S q ≤ 6 → stepCost cexGraph S r ≤ 6 →
        stepCost cexGraph (insert r S) q ≤ 6 →
        openCount cexGraph (insert r S) q ≤ closeCountLiteral cexGraph (insert r S) q →
        Solvable cexGraph 6 (insert r S) → Solvable cexGraph 6 (insert q S) := by
  intro h
  exact chuStuckey_theorem2_false fun S r q hr hq hrq h1 h2 h3 hd hs =>
    h S r q hr hq hrq h1 h2 h3 (hd.trans (closeCount_le_closeCountLiteral cexGraph _ q)) hs

end Search

end MOSPFormalization
