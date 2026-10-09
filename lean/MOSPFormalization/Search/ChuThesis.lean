/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Chu's thesis, Theorems 6.3.6 and 6.3.8, are false, stated as published

G. Chu, *Improving combinatorial optimization*, PhD thesis, University of Melbourne,
2011 (`literature/chu_2011_phd_thesis_improving_combinatorial_optimization.pdf`), §6.3,
pp. 141–143:

> **Definition 6.3.4.** Let `open(c, S) = |o(c, S)|` and
> `close(c, S) = |{d | o(d, S) ⊆ o(c, S)}|`, i.e., the number of new stacks that will
> open and close respectively if we close c's stack next.

> **Theorem 6.3.6.** Suppose `S` is some sequence, and `q ∉ S` is a customer such that:
> `S ++ [q]` is k-playable, and `close(q, S) ≥ open(q, S)`. If `S` has an extension that
> uses `≤ k` stacks, then `S ++ [q]` also has an extension that uses `≤ k` stacks.

> **Theorem 6.3.8.** Suppose `S` is some sequence, and `q, r ∉ S` are customers such
> that: `S ++ [q]` and `S ++ [r, q]` are both k-playable, and
> `close(q, S) ≥ open(q, S ∪ {r})`. If `S ++ [r]` has an extension that uses `≤ k`
> stacks, then `S ++ [q]` also has an extension that uses `≤ k` stacks.

**Theorem 6.3.6** is Chu & Stuckey's (CP 2009) Theorem 1 with the same premise, the same
proof and the same reading of `close`, reworded for `k` stacks ("k-playable", "uses ≤ k
stacks"; this docstring said "word for word" until the number audit of 2026-10-03), so
`chuStuckey_theorem1_false` and `chuStuckey_theorem1_false_literal`
(`PublishedTheorems.lean`) refute it as stated;
`chuThesis_theorem636_false` and `chuThesis_theorem636_false_literal` restate them under
the thesis's number.

**Theorem 6.3.8** is the better move with a premise different from the CP paper's
Theorem 2: `close(q, S) ≥ open(q, S ∪ {r})`, with `close` taken at `S` rather than at
`S ∪ {r}`. The CP refutation (`chuStuckey_theorem2_false`) does not cover it, and this
file proves it false on the same 14-customer `cexGraph` at `k = 6`.

**Reading of the statements**, as in `PublishedTheorems.lean`: an extension of `T` using
`≤ k` stacks exists exactly when `Solvable G k T`; `open` is `openCount`; `close` is
read as `closeCount` (customers not yet closed, the code's reading) or as
`closeCountLiteral` (every customer, closed ones included, the thesis's Definition 6.3.4
read literally, since `d` is unrestricted there).

**Witnesses**, from the brute force in `paper1/thesis_check.py`:

* unclosed reading: `S = {2}`, `r = 3`, `q = 0`, with `close(0, S) = 3 ≥ 2 =
  open(0, S ∪ {3})`. The "no extension" half is the CP Theorem 1 counterexample's
  (`cex_not_solvable_child`).
* literal reading: the unclosed witness serves, since `closeCount ≤ closeCountLiteral`.
  A second witness holds only under the literal reading: `S = {1}`, `r = 6`, `q = 12`,
  where the literal `close(12, S) = 2 = open(12, S ∪ {6})` but the unclosed count is 1.
  Its "no extension" half is an invariant family of four states.

## Main results

* `chuThesis_theorem636_false`, `chuThesis_theorem636_false_literal`;
* `chuThesis_theorem638_false`, `chuThesis_theorem638_false_literal`;
* `chuThesis_theorem638_literal_witness`: the literal-only witness;
* `fink_theorem1_false`: Fink (2012)'s restatement of the definite move, whose premise is
  stronger than the CP one, is false too, on a 15-customer graph.
-/

import MOSPFormalization.Search.PublishedTheorems

namespace MOSPFormalization

namespace Search

open Finset

/-! ### Theorem 6.3.6 is CP Theorem 1 -/

/-- **Chu (2011) Theorem 6.3.6 is false** (unclosed reading of `close`). It is CP 2009
Theorem 1 with the same premise, reworded for `k` stacks, so this is
`chuStuckey_theorem1_false`: at `S = {2}`, `q = 0` on `cexGraph` with `k = 6`. -/
theorem chuThesis_theorem636_false :
    ¬ ∀ (S : Finset (Fin 14)) (q : Fin 14), q ∉ S → stepCost cexGraph S q ≤ 6 →
        openCount cexGraph S q ≤ closeCount cexGraph S q →
        Solvable cexGraph 6 S → Solvable cexGraph 6 (insert q S) :=
  chuStuckey_theorem1_false

/-- **Chu (2011) Theorem 6.3.6 is false** under the literal reading of Definition 6.3.4,
which is `chuStuckey_theorem1_false_literal`. -/
theorem chuThesis_theorem636_false_literal :
    ¬ ∀ (S : Finset (Fin 14)) (q : Fin 14), q ∉ S → stepCost cexGraph S q ≤ 6 →
        openCount cexGraph S q ≤ closeCountLiteral cexGraph S q →
        Solvable cexGraph 6 S → Solvable cexGraph 6 (insert q S) :=
  chuStuckey_theorem1_false_literal

/-! ### Theorem 6.3.8 -/

/-- A solution from `{2, 3}`: `S ++ [r]` with `S = {2}`, `r = 3` has an extension. -/
theorem cexThesis_solvable_r : Solvable cexGraph 6 (insert (3 : Fin 14) {2}) :=
  ⟨[1, 4, 6, 12, 13, 0, 5, 7, 8, 9, 10, 11], by unfold IsClosingOrder; decide, by decide⟩

/-- **Chu (2011) Theorem 6.3.8 is false** (unclosed reading of `close`): on `cexGraph`
with `k = 6`, take `S = {2}`, `r = 3`, `q = 0`. `S ++ [q]` and `S ++ [r, q]` are
playable, `close(q, S) = 3 ≥ 2 = open(q, S ∪ {r})`, `S ++ [r]` has an extension, and
`S ++ [q]` has none. -/
theorem chuThesis_theorem638_false :
    ¬ ∀ (S : Finset (Fin 14)) (r q : Fin 14), r ∉ S → q ∉ S → r ≠ q →
        stepCost cexGraph S q ≤ 6 → stepCost cexGraph S r ≤ 6 →
        stepCost cexGraph (insert r S) q ≤ 6 →
        openCount cexGraph (insert r S) q ≤ closeCount cexGraph S q →
        Solvable cexGraph 6 (insert r S) → Solvable cexGraph 6 (insert q S) := by
  intro h
  have hsol := h {2} 3 0 (by decide) (by decide) (by decide) (by decide) (by decide)
    (by decide) (by decide) cexThesis_solvable_r
  exact cex_not_solvable_child (solvable_cl (G := cexGraph) hsol)

/-- **Chu (2011) Theorem 6.3.8 is false** under the literal reading of Definition 6.3.4
too, by the same witness, since the literal premise is the weaker one. -/
theorem chuThesis_theorem638_false_literal :
    ¬ ∀ (S : Finset (Fin 14)) (r q : Fin 14), r ∉ S → q ∉ S → r ≠ q →
        stepCost cexGraph S q ≤ 6 → stepCost cexGraph S r ≤ 6 →
        stepCost cexGraph (insert r S) q ≤ 6 →
        openCount cexGraph (insert r S) q ≤ closeCountLiteral cexGraph S q →
        Solvable cexGraph 6 (insert r S) → Solvable cexGraph 6 (insert q S) := by
  intro h
  exact chuThesis_theorem638_false fun S r q hr hq hrq h1 h2 h3 hd hs =>
    h S r q hr hq hrq h1 h2 h3 (hd.trans (closeCount_le_closeCountLiteral cexGraph S q)) hs

/-! ### A witness for the literal reading only -/

/-- The states reachable from `{1, 12}` within `6` stacks. -/
def cexThesisFamily : Finset (Finset (Fin 14)) :=
  {{1, 12}, {1, 6, 12}, {1, 12, 13}, {1, 6, 12, 13}}

set_option maxRecDepth 100000 in
theorem cexThesisFamily_closed : ∀ A ∈ cexThesisFamily, ∀ c, c ∉ A →
    stepCost cexGraph A c ≤ 6 → insert c A ∈ cexThesisFamily := by
  decide +kernel

theorem cexThesis_not_solvable_q : ¬ Solvable cexGraph 6 (insert (12 : Fin 14) {1}) :=
  not_solvable_of_invariant cexThesisFamily (by decide) cexThesisFamily_closed (by decide)

theorem cexThesis_solvable_r' : Solvable cexGraph 6 (insert (6 : Fin 14) {1}) :=
  ⟨[2, 3, 4, 12, 13, 0, 5, 7, 8, 9, 10, 11], by unfold IsClosingOrder; decide, by decide⟩

/-- **The literal-only witness to Theorem 6.3.8's failure.** At `S = {1}`, `r = 6`,
`q = 12` on `cexGraph` with `k = 6`: the premises of Theorem 6.3.8 hold with `close`
read literally (`close(12, S) = 2 = open(12, S ∪ {6})`), they fail with the unclosed
reading (`closeCount = 1`), `S ++ [r]` has an extension and `S ++ [q]` has none. -/
theorem chuThesis_theorem638_literal_witness :
    let S : Finset (Fin 14) := {1}
    (6 : Fin 14) ∉ S ∧ (12 : Fin 14) ∉ S ∧ stepCost cexGraph S 12 ≤ 6 ∧
      stepCost cexGraph S 6 ≤ 6 ∧ stepCost cexGraph (insert 6 S) 12 ≤ 6 ∧
      openCount cexGraph (insert 6 S) 12 ≤ closeCountLiteral cexGraph S 12 ∧
      closeCount cexGraph S 12 < openCount cexGraph (insert 6 S) 12 ∧
      Solvable cexGraph 6 (insert 6 S) ∧ ¬ Solvable cexGraph 6 (insert 12 S) := by
  intro S
  exact ⟨by decide, by decide, by decide, by decide, by decide, by decide, by decide,
    cexThesis_solvable_r', cexThesis_not_solvable_q⟩

/-! ### Fink (2012), Teorema 1: a stronger premise, also false

C. Fink, *O problema de minimização de pilhas abertas: novas contribuições*, PhD
thesis, ICMC-USP, 2012 (`literature/fink_2012_phd_thesis_mosp_novas_contribuicoes.pdf`),
pp. 27–28, restates the definite move. It counts `f(α_j, S)`, "the set of items `α_i`"
with `o(α_i, S) ⊆ o(α_j, S)`, `α_i, α_j ∉ S` and `i < j`, and states:

> **Teorema 1.** Seja `|f(α_j, S)| ≥ |o(α_j, S)|` e `S ∪ {α_j}` uma sequência viável,
> então se existe uma solução `U′ = S ∪ {P − S}` para o problema LOSP(k) existe também
> uma solução `U = S ∪ {α_j} ∪ {P − S − {α_j}}`.

Since `i < j`, `q` itself is not counted, so the premise is `closeCount − 1 ≥ open` at
best, strictly stronger than the CP premise: the child must have *fewer* open stacks than
the parent, not merely no more. `cexGraph` does not refute it under any labelling (no
failing state has `closeCount ≥ open + 1`; `paper1/fink_check.py`). Adding a third twin of
customers `3` and `4` does: `finkGraph` is `cexGraph` plus a customer adjacent to `0` and
`2`, with labels `0` and `14` swapped so that the dominated customers precede `q = 14`.
At `S = {2, 3}`, `k = 6`: `f(14, S) = {0, 4}`, `open(14, S) = 2`, `S ++ [14]` costs 6, a
solution from `S` exists, and none from `S ∪ {14}`.
-/

section Fink

variable {V : Type*} [Fintype V] [DecidableEq V] [LinearOrder V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- Fink's `|f(q, S)|`: the customers not in `S`, of smaller index than `q`, whose new
stacks all open with `q`'s. -/
def finkCount (S : Finset V) (q : V) : ℕ :=
  (univ.filter (fun d => d ∉ S ∧ d < q ∧ newlyOpened G S d ⊆ newlyOpened G S q)).card

end Fink

/-- `cexGraph` with a third twin of `3` and `4`, and labels `0` and `14` swapped. -/
def finkEdges : List (ℕ × ℕ) :=
  [(0, 2), (0, 14), (1, 2), (1, 5), (1, 6), (2, 3), (2, 4), (3, 14), (4, 14), (5, 9),
   (5, 11), (5, 12), (6, 8), (6, 13), (7, 9), (7, 10), (7, 13), (7, 14), (8, 9), (8, 10),
   (8, 11), (9, 10), (9, 11), (10, 11), (10, 12), (10, 13), (11, 14), (12, 13)]

/-- The 15-customer graph refuting Fink's Teorema 1. -/
def finkGraph : SimpleGraph (Fin 15) :=
  SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ finkEdges

instance : DecidableRel finkGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ finkEdges ∨ (b.val, a.val) ∈ finkEdges)))

/-- The states reachable from `{2, 3, 14}` within `6` stacks. -/
def finkFamily : Finset (Finset (Fin 15)) :=
  {{2, 3, 14}, {0, 2, 3, 14}, {2, 3, 4, 14}, {0, 1, 2, 3, 14}, {0, 2, 3, 4, 14},
   {1, 2, 3, 4, 14}, {0, 1, 2, 3, 4, 14}, {0, 2, 3, 4, 5, 14}, {0, 2, 3, 4, 6, 14},
   {0, 2, 3, 4, 7, 14}, {0, 1, 2, 3, 4, 5, 14}, {0, 1, 2, 3, 4, 6, 14}}

set_option maxRecDepth 100000 in
theorem finkFamily_closed : ∀ A ∈ finkFamily, ∀ c, c ∉ A →
    stepCost finkGraph A c ≤ 6 → insert c A ∈ finkFamily := by
  decide +kernel

theorem fink_not_solvable : ¬ Solvable finkGraph 6 (insert (14 : Fin 15) {2, 3}) :=
  not_solvable_of_invariant finkFamily (by decide) finkFamily_closed (by decide)

theorem fink_solvable : Solvable finkGraph 6 ({2, 3} : Finset (Fin 15)) :=
  ⟨[0, 1, 4, 6, 12, 13, 7, 5, 8, 9, 10, 11, 14], by unfold IsClosingOrder; decide, by decide⟩

/-- **Fink (2012) Teorema 1 is false**: on `finkGraph` with `k = 6`, at `S = {2, 3}` and
`q = 14`, `|f(q, S)| = 2 ≥ 2 = open(q, S)`, `S ++ [q]` is playable, a solution from `S`
exists, and none begins with `q`. -/
theorem fink_theorem1_false :
    ¬ ∀ (S : Finset (Fin 15)) (q : Fin 15), q ∉ S → stepCost finkGraph S q ≤ 6 →
        openCount finkGraph S q ≤ finkCount finkGraph S q →
        Solvable finkGraph 6 S → Solvable finkGraph 6 (insert q S) := by
  intro h
  exact fink_not_solvable (h {2, 3} 14 (by decide) (by decide) (by decide) fink_solvable)

end Search

end MOSPFormalization
