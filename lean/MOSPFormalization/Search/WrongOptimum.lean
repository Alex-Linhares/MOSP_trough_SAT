/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The previous algorithm reports a wrong optimum

Chu & Stuckey's (2009) customer search, with the definite move as published (Theorem 1,
premise `close ≥ open`), the subset rule, the old move (Theorem 3) and the memo, better move
off, refutes `k = 6` on the 34-customer instance of `paper1/data/false_refutation/`, although
a closing order of cost 6 exists. It would report the optimum as 7; the optimum is 6. This file
proves that, in the kernel, with no `native_decide`.

## The model

`BitSearch.node` is the search as the Python reference `decide` of
`satisfiability/customer_search.py` runs it (`repaired_rules=False`, `definite_move`,
`subset_rule`, `old_move`, `better_move=False`), on bitmasks, line for line:

* a call `node C O Q` is the reference's `search(closed, opened, seen)`: `C` the closed
  customers on entry, `O = O(C)`, `Q` the old moves inherited (`seen`);
* **free moves** (`Py:294–301`): `S = C ∪ {i : N[i] ⊆ O}`;
* **done** (`Py:303`), then the **memo** (`Py:305`, the C's `memo_has`), when it is on;
* **old move**, the node side (`Py:309–311`): `Q ← Q ∩ R(S)`, candidates `R(S) ∖ Q`;
* the **cost cut** (`Py:350–358`): `|(O ∪ N[x]) ∖ S| ≤ k`;
* the **definite move as published** (`Py:457–474`): the first playable `q` in index order with
  `|o(q,S)| ≤ |{d ∈ R(S) : o(d,S) ⊆ o(q,S)}|` is kept alone;
* else the **subset rule** (`Py:483–499`): `r` goes if some `d ∈ R(S)`, `d ≠ r`, has
  `o(d,S) ⊆ o(r,S)` and (`o(d,S) ≠ o(r,S)` or `d < r`); if every candidate would go, all stay;
* the children in the order `(cost, index)` (`Py:367–368`, `playable.sort()`);
* each child `x` is called on `S ∪ {x}`, `O ∪ N[x]` with the inherited old moves
  `{q ∈ seen : |(O ∪ N[q] ∪ N[x]) ∖ (S ∪ {q})| ≤ k}` (`Py:385–403`), and a refuted child joins
  `seen` (`Py:411`); the node counter is the reference's;
* a node whose loop completes is recorded in the memo, when it is on (`Py:416–417`, `C:642`).

With the memo off this is the Python reference exactly (which drops the memo under old move,
`Py:252–257`); with it on it is the C (`customer_search.c`, `search`), which runs both, as Chu &
Stuckey do.

## What is proved

* **The model is the search of the existing development.** `node_spec`: every answer
  `unsat` of `BitSearch.node` is a run `Exec G k F` (`Memo.lean`) in which `F` is `codeFilter`
  (`SubsetRule.lean`: the definite move with the code's premise `IsDefinite`, then the subset
  rule), every old move inherited is exactly the set passing the code's test, every child
  order is the computed one, and the memo is recorded at every completed node or never. This
  is proved for every graph and every `k`, from the bitmask encoding (`dec`), with no
  assumption on the instance.
* **The run on the instance, in the kernel.**
  - `previousAlgorithm_refutes_six` / `previousAlgorithm_refutes_six_memo_off`: the
    previous algorithm answers `unsat` at `k = 6`, with the memo (526 nodes, the C's count)
    and without it (839 nodes, the Python reference's count);
  - `previousAlgorithm_trace_eq_python`: without the memo the model makes exactly the
    calls the Python reference makes, in the same order, entered with the same bitmasks
    (`WrongOptimumData.pythonTrace`, captured from the running reference by
    `paper1/wrong_optimum_trace.py`);
  - `previousAlgorithm_finds_seven`: at `k = 7` it answers `sat`, so the reported optimum is 7.
* **The truth.** `solvable_six`: the closing order of `solutions34.json` costs 6.
  `not_solvable_five`: no closing order costs 5, by a run of the search with the subset rule,
  old move and memo and *without* the definite move, whose filter is proved node-sound
  (`subsetFilter_sound`), so `exec_root_sound` applies. Hence `pathwidth_eq_five` and
  `mospValue_eq_six` for the instance `M34`, through `mospValue = pathwidth + 1`.
* **The main theorem**, `previousAlgorithm_wrong_optimum`: the previous algorithm refutes 6
  and finds 7, so it reports 7, while `mospValue M34 = 6` and `pw(G_M34) = 5`; its refutation
  is an `Exec` run of `codeFilter` from the root, and the code's filter is therefore not
  node-sound on this instance (`not_filterSound_codeFilter`): the node-level failure of
  `not_codeFilterSound_cexGraph` reaches the root answer.

## Cost

Every run is checked by `decide +kernel`, with no `native_decide`: the axioms are `propext`,
`Classical.choice` and `Quot.sound` (`paper1/axiom_check.lean`). On a loaded 32-core machine
the file takes about four minutes: the adjacency check 8 s, the memo-on refutation of 6 64 s,
the memo-off run with its trace 97 s, `k = 7` 24 s, `k = 5` 40 s.

## What is assumed rather than proved

The correspondence between `BitSearch.node` and the Python and C code is by reading
(the line references above) and by test (the trace and the node counts, checked here in the
kernel; mutated traces are rejected, `paper1/wrong_optimum_trace.py --mutate`). The
encodings differ from the code only where the difference is invisible on canonical bitmasks:
`o(d,S) ≠ o(r,S)` and the subset test are taken on the low `n` bits, the done test is
`|S| = n`, and the popcount counts the low `n` bits.
-/

import MOSPFormalization.Search.Memo
import MOSPFormalization.Search.WrongOptimumData
import Mathlib.Data.List.Sort

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

namespace BitSearch

open Finset

/-! ### The model -/

variable {n : ℕ}

/-- `a & ~b`. -/
def andNot (a b : ℕ) : ℕ := a ^^^ (a &&& b)

/-- The number of set bits among bits `0, …, j − 1` of `m`. -/
def popc : ℕ → ℕ → ℕ
  | 0, _ => 0
  | j + 1, m => popc j m + (m.testBit j).toNat

/-- The low `n` bits of `m`. -/
def low (n m : ℕ) : ℕ := m &&& (2 ^ n - 1)

/-- `a ⊆ b` on the low `n` bits. -/
def subB (n a b : ℕ) : Bool := low n (andNot a b) == 0

/-- `a = b` on the low `n` bits. -/
def eqB (n a b : ℕ) : Bool := low n (a ^^^ b) == 0

/-- The bitmask of `{i : p i}`. -/
def maskOf (p : Fin n → Bool) : ℕ :=
  (List.finRange n).foldr (fun i acc => if p i then acc ||| 2 ^ i.val else acc) 0

/-- A configuration: the closed neighbourhoods `N[i]` as bitmasks, the budget `k`, the definite
move as published on or off, the memo on or off. Subset rule and old move are always on. -/
structure Cfg (n : ℕ) where
  nb : Fin n → ℕ
  k : ℕ
  definite : Bool
  memo : Bool

/-- A call's answer: a solution, a refutation, or out of fuel (never reached in the runs here). -/
inductive Res
  | sat
  | unsat
  | fuel
  deriving DecidableEq, Repr

/-- What the run threads: the memo, the node counter, and the calls made, latest first. -/
structure St where
  memo : List ℕ
  nodes : ℕ
  trace : List (ℕ × ℕ)
  deriving DecidableEq, Repr

variable (c : Cfg n)

/-- The stacks open when `x` closes after `S` (`O = O(S)`), counting `x`. -/
def cost (S O : ℕ) (x : Fin n) : ℕ := popc n (andNot (O ||| c.nb x) S)

/-- `o(d, S) = N[d] ∖ O(S)`. -/
def opensOf (O : ℕ) (d : Fin n) : ℕ := andNot (c.nb d) O

/-- The published premise of the definite move, `open(q,S) ≤ close(q,S)`. -/
def isDefB (S O : ℕ) (q : Fin n) : Bool :=
  decide (popc n (opensOf c O q) ≤ ((List.finRange n).filter
    (fun (d : Fin n) => !S.testBit d && subB n (opensOf c O d) (opensOf c O q))).length)

/-- Some remaining `d` dominates `r` in the subset rule's sense, with the index tie-break. -/
def dominatedB (S O : ℕ) (r : Fin n) : Bool :=
  (List.finRange n).any (fun (d : Fin n) => !S.testBit d &&
    subB n (opensOf c O d) (opensOf c O r) && decide (d ≠ r) &&
    (!eqB n (opensOf c O d) (opensOf c O r) || decide (d < r)))

/-- The playable candidates, in index order. -/
def playL (S O Q : ℕ) : List (Fin n) :=
  (List.finRange n).filter
    (fun (x : Fin n) => !S.testBit x && !Q.testBit x && decide (cost c S O x ≤ c.k))

/-- The dominance filter: the definite move (if on), else the subset rule with its fallback. -/
def filterL (S O Q : ℕ) : List (Fin n) :=
  match (if c.definite then (playL c S O Q).filter (isDefB c S O) else []) with
  | q :: _ => [q]
  | [] =>
    if ((playL c S O Q).filter (fun r => !dominatedB c S O r)).isEmpty then playL c S O Q
    else (playL c S O Q).filter (fun r => !dominatedB c S O r)

/-- The order of `(cost, index)` pairs. -/
def keyLe (a b : ℕ × Fin n) : Prop := a.1 < b.1 ∨ (a.1 = b.1 ∧ a.2 ≤ b.2)

instance : DecidableRel (keyLe (n := n)) := fun a b => by unfold keyLe; infer_instance

/-- The children in the reference's order, cheapest first, ties by index. -/
def childrenL (S O Q : ℕ) : List (Fin n) :=
  (((filterL c S O Q).map (fun x => (cost c S O x, x))).insertionSort keyLe).map Prod.snd

/-- The old moves the child `x` inherits from `seen`. -/
def inherit (S O seen : ℕ) (x : Fin n) : ℕ :=
  maskOf (fun (q : Fin n) => seen.testBit q &&
    decide (popc n (andNot (O ||| c.nb q ||| c.nb x) (S ||| 2 ^ q.val)) ≤ c.k))

/-- The loop over the children of the node `S` (with `O = O(S)`). -/
def loop (rec : ℕ → ℕ → ℕ → St → Res × St) (S O : ℕ) :
    List (Fin n) → ℕ → St → Res × St
  | [], _, st => (.unsat, st)
  | x :: l, seen, st =>
    match rec (S ||| 2 ^ x.val) (O ||| c.nb x) (inherit c S O seen x)
        { st with nodes := st.nodes + 1 } with
    | (.unsat, st') => loop rec S O l (seen ||| 2 ^ x.val) st'
    | r => r

/-- A call of the search on `C` (closed on entry), `O = O(C)`, inherited old moves `Q`. -/
def node : ℕ → ℕ → ℕ → ℕ → St → Res × St
  | 0, _, _, _, st => (.fuel, st)
  | f + 1, C, O, Q, st =>
    let st := { st with trace := (C, Q) :: st.trace }
    let S := maskOf (fun (i : Fin n) => C.testBit i || subB n (c.nb i) O)
    if popc n S = n then (.sat, st)
    else if c.memo && st.memo.contains S then (.unsat, st)
    else
      let Q' := maskOf (fun (i : Fin n) => Q.testBit i && !S.testBit i)
      match loop c (node f) S O (childrenL c S O Q') Q' st with
      | (.unsat, st') => (.unsat, if c.memo then { st' with memo := S :: st'.memo } else st')
      | r => r

/-- The search from the root. -/
def run (fuel : ℕ) : Res × St := node c fuel 0 0 0 ⟨[], 0, []⟩

/-- The cost of a closing order from `S` (`O = O(S)`), on bitmasks. -/
def ordCost : ℕ → ℕ → List (Fin n) → ℕ
  | _, _, [] => 0
  | S, O, x :: l => max (cost c S O x) (ordCost (S ||| 2 ^ x.val) (O ||| c.nb x) l)

/-! ### Decoding bitmasks -/

/-- The set a bitmask stands for. -/
def dec (m : ℕ) : Finset (Fin n) := univ.filter (fun i => m.testBit i.val = true)

@[simp] theorem mem_dec {m : ℕ} {i : Fin n} : i ∈ (dec m : Finset (Fin n)) ↔ m.testBit i.val = true := by
  simp [dec]

theorem testBit_andNot (a b i : ℕ) : (andNot a b).testBit i = (a.testBit i && !b.testBit i) := by
  simp only [andNot, Nat.testBit_xor, Nat.testBit_and]
  cases a.testBit i <;> cases b.testBit i <;> rfl

theorem dec_or (a b : ℕ) : (dec (a ||| b) : Finset (Fin n)) = dec a ∪ dec b := by
  ext i; simp [Nat.testBit_or]

theorem dec_andNot (a b : ℕ) : (dec (andNot a b) : Finset (Fin n)) = dec a \ dec b := by
  ext i; simp [testBit_andNot]

theorem dec_xor_eq_empty_iff (a b : ℕ) :
    (dec (a ^^^ b) : Finset (Fin n)) = ∅ ↔ (dec a : Finset (Fin n)) = dec b := by
  constructor
  · intro h; ext i
    have := Finset.ext_iff.1 h i
    simp only [mem_dec, Nat.testBit_xor, Finset.notMem_empty, iff_false] at this
    simp only [mem_dec]
    cases ha : a.testBit i <;> cases hb : b.testBit i <;> simp_all
  · intro h; ext i
    have := Finset.ext_iff.1 h i
    simp only [mem_dec] at this
    simp only [mem_dec, Nat.testBit_xor, Finset.notMem_empty, iff_false]
    cases ha : a.testBit i <;> cases hb : b.testBit i <;> simp_all

theorem dec_two_pow (x : Fin n) : (dec (2 ^ x.val) : Finset (Fin n)) = {x} := by
  ext i; simp [Nat.testBit_two_pow, Fin.ext_iff, eq_comm]

theorem dec_or_two_pow (S : ℕ) (x : Fin n) :
    (dec (S ||| 2 ^ x.val) : Finset (Fin n)) = insert x (dec S) := by
  rw [dec_or, dec_two_pow, Finset.union_comm, ← Finset.insert_eq]

@[simp] theorem dec_zero : (dec 0 : Finset (Fin n)) = ∅ := by ext i; simp

theorem testBit_foldr (p : Fin n → Bool) (j : ℕ) : ∀ L : List (Fin n),
    (L.foldr (fun i acc => if p i then acc ||| 2 ^ i.val else acc) 0).testBit j = true ↔
      ∃ i ∈ L, p i = true ∧ i.val = j
  | [] => by simp
  | i :: L => by
    rw [List.foldr_cons]
    have ih := testBit_foldr p j L
    split_ifs with h
    · rw [Nat.testBit_or, Bool.or_eq_true, ih, Nat.testBit_two_pow]
      simp only [List.mem_cons, decide_eq_true_eq]
      constructor
      · rintro (⟨i', hi', hp, rfl⟩ | rfl)
        · exact ⟨i', Or.inr hi', hp, rfl⟩
        · exact ⟨i, Or.inl rfl, h, rfl⟩
      · rintro ⟨i', rfl | hi', hp, rfl⟩
        · exact Or.inr rfl
        · exact Or.inl ⟨i', hi', hp, rfl⟩
    · rw [ih]
      simp only [List.mem_cons]
      constructor
      · rintro ⟨i', hi', hp, rfl⟩; exact ⟨i', Or.inr hi', hp, rfl⟩
      · rintro ⟨i', rfl | hi', hp, rfl⟩
        · simp_all
        · exact ⟨i', hi', hp, rfl⟩

theorem testBit_maskOf (p : Fin n → Bool) (i : Fin n) : (maskOf p).testBit i.val = p i := by
  have := testBit_foldr p i.val (List.finRange n)
  unfold maskOf
  cases h : p i
  · cases h' : (List.foldr (fun i acc => if p i = true then acc ||| 2 ^ i.val else acc) 0
      (List.finRange n)).testBit i.val
    · rfl
    · obtain ⟨i', -, hp, he⟩ := this.1 h'
      rw [Fin.ext he] at hp; simp_all
  · exact this.2 ⟨i, List.mem_finRange i, h, rfl⟩

theorem dec_maskOf (p : Fin n → Bool) : (dec (maskOf p) : Finset (Fin n)) = univ.filter (p · = true) := by
  ext i; simp [testBit_maskOf]

theorem popc_eq_card_range (m : ℕ) : ∀ j, popc j m = ((Finset.range j).filter (fun i => m.testBit i = true)).card
  | 0 => rfl
  | j + 1 => by
    rw [popc, popc_eq_card_range m j, Finset.range_add_one, Finset.filter_insert]
    split_ifs with h
    · rw [Finset.card_insert_of_notMem (by simp), h]; rfl
    · simp only [Bool.not_eq_true] at h; rw [h]; rfl

theorem popc_eq_card (m : ℕ) : popc n m = (dec m : Finset (Fin n)).card := by
  rw [popc_eq_card_range]
  refine (Finset.card_bij (fun (i : Fin n) _ => i.val) ?_ ?_ ?_).symm
  · intro i hi; simp only [mem_dec] at hi; simp [hi, i.isLt]
  · intro a _ b _ h; exact Fin.ext h
  · intro j hj
    simp only [Finset.mem_filter, Finset.mem_range] at hj
    exact ⟨⟨j, hj.1⟩, by simp [hj.2], rfl⟩

theorem low_eq_zero_iff (m : ℕ) : low n m = 0 ↔ (dec m : Finset (Fin n)) = ∅ := by
  constructor
  · intro h; ext i
    have := congrArg (fun x => Nat.testBit x i.val) h
    simp only [low, Nat.testBit_and, Nat.testBit_two_pow_sub_one, i.isLt, decide_true,
      Bool.and_true, Nat.zero_testBit] at this
    simp [this]
  · intro h
    apply Nat.eq_of_testBit_eq
    intro j
    simp only [low, Nat.testBit_and, Nat.testBit_two_pow_sub_one, Nat.zero_testBit]
    by_cases hj : j < n
    · have := Finset.ext_iff.1 h ⟨j, hj⟩
      simp only [mem_dec, Finset.notMem_empty, iff_false, Bool.not_eq_true] at this
      simp [this]
    · simp [hj]

theorem subB_iff (a b : ℕ) : subB n a b = true ↔ (dec a : Finset (Fin n)) ⊆ dec b := by
  rw [subB, beq_iff_eq, low_eq_zero_iff, dec_andNot, Finset.sdiff_eq_empty_iff_subset]

theorem eqB_iff (a b : ℕ) : eqB n a b = true ↔ (dec a : Finset (Fin n)) = dec b := by
  rw [eqB, beq_iff_eq, low_eq_zero_iff, dec_xor_eq_empty_iff]

theorem length_filter_finRange (p : Fin n → Bool) :
    ((List.finRange n).filter p).length = (univ.filter (fun i => p i = true)).card := by
  rw [← List.toFinset_card_of_nodup ((List.nodup_finRange n).filter _)]
  congr 1; ext i; simp

/-- The head of an index-ordered filter is the least member. -/
theorem head_eq_min' {p : Fin n → Bool} {q : Fin n} {rest : List (Fin n)}
    (h : (List.finRange n).filter p = q :: rest) (s : Finset (Fin n))
    (hs : ∀ x, x ∈ s ↔ p x = true) (hne : s.Nonempty) : s.min' hne = q := by
  have hpw : ((List.finRange n).filter p).Pairwise (· < ·) :=
    (List.pairwise_lt_finRange n).filter _
  rw [h, List.pairwise_cons] at hpw
  have hmem : ∀ x, x ∈ s ↔ x = q ∨ x ∈ rest := by
    intro x
    rw [hs, ← List.mem_cons, ← h, List.mem_filter]
    simp [List.mem_finRange]
  have hq : q ∈ s := (hmem q).2 (Or.inl rfl)
  rcases (hmem _).1 (s.min'_mem hne) with h1 | h1
  · exact h1
  · exact absurd (s.min'_le q hq) (not_le.2 (hpw.1 _ h1))

/-! ### The model computes the search of the development -/

variable (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]

/-- The filter the model computes, in the development's terms: `codeFilter` (`SubsetRule.lean`)
with the definite move, the subset rule alone without it. -/
def specFilter (k : ℕ) (definite : Bool) (S Q : Finset (Fin n)) : Finset (Fin n) :=
  if definite then codeFilter G k S Q else subsetFilter G S (playable G k S ((univ \ S) \ Q))

/-- The memo as a set of states. -/
def memoSet (L : List ℕ) : Set (Finset (Fin n)) := {T | ∃ m ∈ L, dec m = T}

theorem memoSet_cons (m : ℕ) (L : List ℕ) :
    (memoSet (m :: L) : Set (Finset (Fin n))) = insert (dec m) (memoSet L) := by
  ext T; simp [memoSet, eq_comm]

@[simp] theorem memoSet_nil : (memoSet [] : Set (Finset (Fin n))) = ∅ := by
  ext T; simp [memoSet]

variable {G c}

section Node

variable (hnb : ∀ i, (dec (c.nb i) : Finset (Fin n)) = nbhd G i)
include hnb

variable {S O : ℕ} (hO : (dec O : Finset (Fin n)) = opened G (dec S))
include hO

theorem cost_eq (x : Fin n) : cost c S O x = stepCost G (dec S) x := by
  rw [cost, popc_eq_card, dec_andNot, dec_or, hnb, hO, stepCost, opened_insert,
    Finset.union_comm]

theorem dec_opensOf (d : Fin n) : (dec (opensOf c O d) : Finset (Fin n)) = newlyOpened G (dec S) d := by
  rw [opensOf, dec_andNot, hnb, hO, newlyOpened]

theorem isDefB_iff (q : Fin n) : isDefB c S O q = true ↔ IsDefinite G (dec S) q := by
  rw [isDefB, decide_eq_true_iff, popc_eq_card, dec_opensOf hnb hO, length_filter_finRange,
    IsDefinite, openCount, closeCount]
  apply iff_of_eq; congr 2; ext d
  simp [subB_iff, dec_opensOf hnb hO]

theorem dominatedB_iff (r : Fin n) : dominatedB c S O r = true ↔ IsSubsetDominated G (dec S) r := by
  have key : ∀ d : Fin n, ((!S.testBit d && subB n (opensOf c O d) (opensOf c O r) &&
      decide (d ≠ r) && (!eqB n (opensOf c O d) (opensOf c O r) || decide (d < r))) = true) ↔
      (d ∈ univ \ dec S ∧ Dominates G (dec S) d r) := by
    intro d
    have e1 := subB_iff (n := n) (opensOf c O d) (opensOf c O r)
    have e2 := eqB_iff (n := n) (opensOf c O d) (opensOf c O r)
    rw [dec_opensOf hnb hO, dec_opensOf hnb hO] at e1 e2
    simp only [Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true', decide_eq_true_eq,
      Bool.eq_false_iff, ne_eq, e1, e2, Dominates, mem_sdiff, mem_univ, mem_dec, true_and]
    tauto
  rw [dominatedB, List.any_eq_true, IsSubsetDominated]
  constructor
  · rintro ⟨d, -, hd⟩; exact ⟨d, ((key d).1 hd).1, ((key d).1 hd).2⟩
  · rintro ⟨d, hd, hdom⟩; exact ⟨d, List.mem_finRange d, (key d).2 ⟨hd, hdom⟩⟩

theorem mem_playL (Q : ℕ) (x : Fin n) :
    x ∈ playL c S O Q ↔ x ∈ playable G c.k (dec S) ((univ \ dec S) \ dec Q) := by
  simp [playL, playable, cost_eq hnb hO]

theorem mem_filterL (Q : ℕ) (x : Fin n) :
    x ∈ filterL c S O Q ↔ x ∈ specFilter G c.k c.definite (dec S) (dec Q) := by
  set P := playable G c.k (dec S) ((univ \ dec S) \ dec Q) with hP
  have hsub : ∀ y, y ∈ (playL c S O Q).filter (fun r => !dominatedB c S O r) ↔
      y ∈ subsetKept G (dec S) P := by
    intro y
    simp only [List.mem_filter, ← mem_playL hnb hO, subsetKept, Finset.mem_filter, hP,
      Bool.not_eq_true', Bool.eq_false_iff, ne_eq, dominatedB_iff hnb hO]
  have hsubset : x ∈ (if ((playL c S O Q).filter (fun r => !dominatedB c S O r)).isEmpty then
      playL c S O Q else (playL c S O Q).filter (fun r => !dominatedB c S O r)) ↔
      x ∈ subsetFilter G (dec S) P := by
    unfold subsetFilter
    by_cases hK : subsetKept G (dec S) P = ∅
    · have : ((playL c S O Q).filter (fun r => !dominatedB c S O r)).isEmpty = true := by
        rw [List.isEmpty_iff, List.eq_nil_iff_forall_not_mem]
        intro y hy; rw [hsub, hK] at hy; simp at hy
      simp only [this, ↓reduceIte, mem_playL hnb hO, ← hP, hK]
    · have : ((playL c S O Q).filter (fun r => !dominatedB c S O r)).isEmpty = false := by
        rw [Bool.eq_false_iff, ne_eq, List.isEmpty_iff, List.eq_nil_iff_forall_not_mem]
        intro hall
        obtain ⟨y, hy⟩ := Finset.nonempty_iff_ne_empty.2 hK
        exact hall y ((hsub y).2 hy)
      simp only [this, hK, Bool.false_eq_true, ↓reduceIte, hsub]
  unfold filterL specFilter
  cases hdef : c.definite
  · simpa using hsubset
  · simp only [↓reduceIte, codeFilter, definiteThenSubset]
    rw [← hP]
    have hLD : ∀ y, y ∈ (playL c S O Q).filter (isDefB c S O) ↔ y ∈ P.filter (IsDefinite G (dec S)) := by
      intro y; simp [mem_playL hnb hO, isDefB_iff hnb hO, hP]
    rcases hL : (playL c S O Q).filter (isDefB c S O) with _ | ⟨q, rest⟩
    · have hemp : ¬ (P.filter (IsDefinite G (dec S))).Nonempty := by
        rintro ⟨y, hy⟩; rw [← hLD, hL] at hy; simp at hy
      simp only [hemp, ↓reduceDIte]
      exact hsubset
    · have hne : (P.filter (IsDefinite G (dec S))).Nonempty := ⟨q, (hLD q).1 (by simp [hL])⟩
      simp only [hne, ↓reduceDIte, List.mem_singleton, Finset.mem_singleton]
      rw [head_eq_min' (q := q) (rest := rest)]
      · rw [playL, List.filter_filter] at hL; exact hL
      · intro y
        rw [← hLD]
        simp only [playL, List.filter_filter, List.mem_filter, List.mem_finRange, true_and,
          Bool.and_eq_true]

end Node

theorem mem_childrenL (S O Q : ℕ) (x : Fin n) : x ∈ childrenL c S O Q ↔ x ∈ filterL c S O Q := by
  unfold childrenL
  rw [List.mem_map]
  constructor
  · rintro ⟨a, ha, rfl⟩
    rw [(List.perm_insertionSort _ _).mem_iff, List.mem_map] at ha
    obtain ⟨y, hy, rfl⟩ := ha
    exact hy
  · intro hx
    exact ⟨(cost c S O x, x),
      (List.perm_insertionSort _ _).mem_iff.2 (List.mem_map.2 ⟨x, hx, rfl⟩), rfl⟩

theorem popc_eq_n_iff (m : ℕ) : popc n m = n ↔ (dec m : Finset (Fin n)) = univ := by
  rw [popc_eq_card]
  constructor
  · intro h; exact Finset.eq_univ_of_card _ (by simpa using h)
  · intro h; rw [h]; simp

/-! ### The two filters as filters of `Exec` -/

theorem specFilter_playable (k : ℕ) (b : Bool) : FilterPlayable G k (specFilter G k b) := by
  intro S Q x hx
  have hP : x ∈ playable G k S ((univ \ S) \ Q) := by
    unfold specFilter at hx
    cases b
    · exact subsetFilter_subset _ _ (by simpa using hx)
    · simp only [↓reduceIte, codeFilter, definiteThenSubset] at hx
      split_ifs at hx with h
      · rw [Finset.mem_singleton] at hx
        subst hx
        exact (mem_filter.1 (min'_mem _ h)).1
      · exact subsetFilter_subset _ _ hx
  obtain ⟨hK, hk⟩ := mem_filter.1 hP
  exact ⟨(mem_sdiff.1 (mem_sdiff.1 hK).1).2, hk⟩

/-- Without the definite move the filter is the subset rule alone, which is node-sound. -/
theorem specFilter_false_sound (k : ℕ) : FilterSound G k (specFilter G k false) :=
  fun _ _ _ hS hQ hs => subsetFilter_sound hQ hs hS

section Exec

variable (hnb : ∀ i, (dec (c.nb i) : Finset (Fin n)) = nbhd G i)
include hnb

/-- The free moves: `S = C ∪ {i : N[i] ⊆ O(C)}` is `cl(C)`. -/
theorem dec_freeClose {C O : ℕ} (hO : (dec O : Finset (Fin n)) = opened G (dec C)) :
    (dec (maskOf (fun (i : Fin n) => C.testBit i || subB n (c.nb i) O)) : Finset (Fin n)) =
      cl G (dec C) := by
  ext i
  simp only [dec_maskOf, mem_filter, mem_univ, true_and, Bool.or_eq_true, subB_iff, hnb, hO,
    cl, mem_finished]
  constructor
  · rintro (h | h)
    · exact fun v hv => mem_opened.2 ⟨i, mem_dec.2 h, hv⟩
    · exact h
  · exact Or.inr

/-- The old moves a child inherits are exactly those passing the code's test. -/
theorem dec_inherit {S O : ℕ} (hO : (dec O : Finset (Fin n)) = opened G (dec S)) (seen : ℕ)
    (x : Fin n) :
    (dec (inherit c S O seen x) : Finset (Fin n)) =
      (dec seen).filter (fun q => stepCost G (insert q (dec S)) x ≤ c.k) := by
  ext q
  simp only [inherit, dec_maskOf, mem_filter, mem_univ, true_and, Bool.and_eq_true,
    decide_eq_true_eq, mem_dec]
  rw [popc_eq_card, dec_andNot, dec_or, dec_or, dec_or_two_pow, hnb, hnb, hO, stepCost,
    opened_insert, opened_insert]
  have : opened G (dec S) ∪ nbhd G q ∪ nbhd G x = nbhd G x ∪ (nbhd G q ∪ opened G (dec S)) := by
    ext v; simp only [mem_union]; tauto
  rw [this]

theorem dec_child {S O : ℕ} (hO : (dec O : Finset (Fin n)) = opened G (dec S)) (x : Fin n) :
    (dec (O ||| c.nb x) : Finset (Fin n)) = opened G (dec (S ||| 2 ^ x.val)) := by
  rw [dec_or_two_pow, dec_or, hnb, hO, opened_insert, Finset.union_comm]

/-- The loop of a node is a loop of `Exec`. -/
theorem loop_spec {S O : ℕ} (hO : (dec O : Finset (Fin n)) = opened G (dec S))
    (rec : ℕ → ℕ → ℕ → St → Res × St)
    (hrec : ∀ C' O' Q' st, (dec O' : Finset (Fin n)) = opened G (dec C') →
      (rec C' O' Q' st).1 = .unsat →
      Exec G c.k (specFilter G c.k c.definite) (memoSet st.memo) (cl G (dec C')) (dec Q') none
        (memoSet (rec C' O' Q' st).2.memo)) :
    ∀ (l : List (Fin n)) (seen : ℕ) (st : St), (loop c rec S O l seen st).1 = .unsat →
      Exec G c.k (specFilter G c.k c.definite) (memoSet st.memo) (dec S) (dec seen) (some l)
        (memoSet (loop c rec S O l seen st).2.memo)
  | [], _, _, _ => Exec.nil
  | x :: l, seen, st, h => by
    rcases hr : rec (S ||| 2 ^ x.val) (O ||| c.nb x) (inherit c S O seen x)
      { st with nodes := st.nodes + 1 } with ⟨res, st'⟩
    cases res with
    | sat => simp [loop, hr] at h
    | fuel => simp [loop, hr] at h
    | unsat =>
      simp only [loop, hr] at h ⊢
      have hc := hrec _ _ _ _ (dec_child hnb hO x) (by rw [hr])
      rw [hr, dec_or_two_pow] at hc
      have hl := loop_spec hO rec hrec l (seen ||| 2 ^ x.val) st' h
      rw [dec_or_two_pow] at hl
      exact Exec.cons x l (by rw [dec_inherit hnb hO]) hc hl

/-- **The model is a run of the development's search.** Every `unsat` answer of
`BitSearch.node` is an `Exec` run with the filter `specFilter` (`codeFilter` when the definite
move is on), the computed child order, exactly the inherited old moves, and the memo recorded
at every completed node when it is on. -/
theorem node_spec : ∀ (f C O Q : ℕ) (st : St), (dec O : Finset (Fin n)) = opened G (dec C) →
    (node c f C O Q st).1 = .unsat →
    Exec G c.k (specFilter G c.k c.definite) (memoSet st.memo) (cl G (dec C)) (dec Q) none
      (memoSet (node c f C O Q st).2.memo)
  | 0, _, _, _, _, _, h => by simp [node] at h
  | f + 1, C, O, Q, st, hO, h => by
    have hS := dec_freeClose hnb hO
    set Sm := maskOf (fun (i : Fin n) => C.testBit i || subB n (c.nb i) O) with hSm
    have hOS : (dec O : Finset (Fin n)) = opened G (dec Sm) := by rw [hS, opened_cl, hO]
    set Qm := maskOf (fun (i : Fin n) => Q.testBit i && !Sm.testBit i) with hQm
    have hQ : (dec Qm : Finset (Fin n)) = dec Q \ cl G (dec C) := by
      rw [hQm, dec_maskOf, ← hS]; ext i; simp
    simp only [node] at h ⊢
    rw [← hSm, ← hQm] at h ⊢
    by_cases h1 : popc n Sm = n
    · simp [h1] at h
    by_cases h2 : (c.memo && st.memo.contains Sm) = true
    · simp only [h1, h2, ↓reduceIte] at h ⊢
      refine Exec.hit ⟨Sm, ?_, hS⟩
      simp only [Bool.and_eq_true, List.contains_iff_mem] at h2
      exact h2.2
    simp only [h1, h2, ↓reduceIte, Bool.false_eq_true] at h ⊢
    rcases hl : loop c (node c f) Sm O (childrenL c Sm O Qm) Qm
      { st with trace := (C, Q) :: st.trace } with ⟨res, st'⟩
    cases res with
    | sat => simp [hl] at h
    | fuel => simp [hl] at h
    | unsat =>
      have hloop := loop_spec hnb hOS (node c f)
        (fun C' O' Q' st hO' h' => node_spec f C' O' Q' st hO' h') _ Qm _ (by rw [hl])
      rw [hl, hS, hQ] at hloop
      have hne : cl G (dec C) ≠ univ := fun he => h1 ((popc_eq_n_iff Sm).2 (hS.trans he))
      have hmem : ∀ x, x ∈ childrenL c Sm O Qm ↔
          x ∈ specFilter G c.k c.definite (cl G (dec C)) (dec Q \ cl G (dec C)) := by
        intro x; rw [mem_childrenL, mem_filterL hnb hOS, hS, hQ]
      have := Exec.node (G := G) (k := c.k) (F := specFilter G c.k c.definite) _ c.memo hne hmem
        hloop
      cases hm : c.memo
      · simpa [hm] using this
      · simpa [hm, memoSet_cons, hS] using this

/-- **A refutation by the model from the root is an `Exec` refutation from the root.** -/
theorem run_spec (fuel : ℕ) (h : (run c fuel).1 = .unsat) :
    Exec G c.k (specFilter G c.k c.definite) ∅ ∅ ∅ none (memoSet (run c fuel).2.memo) := by
  have := node_spec hnb fuel 0 0 0 ⟨[], 0, []⟩ (by simp [opened_empty]) h
  simp only [dec_zero, cl_empty, memoSet_nil] at this
  exact this

/-- The cost of a closing order, on bitmasks, is `orderCost`. -/
theorem ordCost_eq : ∀ (l : List (Fin n)) (S O : ℕ),
    (dec O : Finset (Fin n)) = opened G (dec S) → ordCost c S O l = orderCost G (dec S) l
  | [], _, _, _ => rfl
  | x :: l, S, O, hO => by
    rw [ordCost, orderCost, cost_eq hnb hO, ordCost_eq l _ _ (dec_child hnb hO x),
      dec_or_two_pow]

end Exec

end BitSearch

/-! ### The instance -/

namespace WrongOptimum

open BitSearch Finset

/-- The instance `instance34.mosp`: customer `c` needs pattern `p` iff `c` is an end of the
edge `patternEdges[p]`. 34 customers, 61 patterns, two customers per pattern. -/
def M34 : MOSPInstance (Fin 34) (Fin 61) where
  requires c p := c.val = (patternEdges.getD p.val (0, 0)).1 ∨
    c.val = (patternEdges.getD p.val (0, 0)).2

instance : DecidableRel M34.requires := fun _ _ => inferInstanceAs (Decidable (_ ∨ _))

/-- Its MOSP graph: 34 vertices, 61 edges. -/
abbrev G34 : SimpleGraph (Fin 34) := M34.mospGraph

/-- `N[i]` as a bitmask (`WrongOptimumData.nbList`). -/
def nb34 (i : Fin 34) : ℕ := nbList.getD i.val 0

set_option maxRecDepth 10000 in
theorem nb34_testBit : ∀ i j : Fin 34, (nb34 i).testBit j.val = decide (j = i ∨ G34.Adj i j) := by
  decide +kernel

/-- The masks are the closed neighbourhoods of the MOSP graph. -/
theorem hnb34 (i : Fin 34) : (dec (nb34 i) : Finset (Fin 34)) = nbhd G34 i := by
  ext j; rw [mem_dec, nb34_testBit, mem_nbhd, decide_eq_true_iff]

/-- **The previous algorithm**: definite move as published, subset rule, old move, the memo on
or off, better move off, budget `k`. -/
def published (k : ℕ) (memo : Bool) : Cfg 34 := ⟨nb34, k, true, memo⟩

/-- The same search without the definite move, which is sound. -/
def subsetOnly (k : ℕ) : Cfg 34 := ⟨nb34, k, false, true⟩

/-- A run's answer and node count. -/
def summary (r : Res × St) : Res × ℕ := (r.1, r.2.nodes)

/-- A run's answer, node count, and calls in the order made. -/
def summaryTrace (r : Res × St) : Res × ℕ × List (ℕ × ℕ) := (r.1, r.2.nodes, r.2.trace.reverse)

/-! #### The runs, in the kernel -/

set_option maxHeartbeats 0 in
/-- **The previous algorithm refutes `k = 6`**, with the memo, in 526 nodes: the C's count. -/
theorem published_six_memo : summary (run (published 6 true) 40) = (.unsat, cNodes) := by
  decide +kernel

set_option maxHeartbeats 0 in
/-- **Without the memo it refutes `k = 6` too, making exactly the Python reference's calls**:
the same 840 calls, in the same order, entered with the same bitmasks, 839 nodes. -/
theorem published_six_trace :
    summaryTrace (run (published 6 false) 40) = (.unsat, pythonNodes, pythonTrace) := by
  decide +kernel

set_option maxHeartbeats 0 in
/-- At `k = 7` the previous algorithm finds a solution. -/
theorem published_seven : (run (published 7 true) 40).1 = .sat := by
  decide +kernel

set_option maxHeartbeats 0 in
/-- Without the definite move, the search refutes `k = 5` (251 nodes). -/
theorem subsetOnly_five : (run (subsetOnly 5) 40).1 = .unsat := by
  decide +kernel

theorem summary_fst (r : Res × St) : (summary r).1 = r.1 := rfl

theorem summaryTrace_fst (r : Res × St) : (summaryTrace r).1 = r.1 := rfl

theorem summaryTrace_trace (r : Res × St) : (summaryTrace r).2.2 = r.2.trace.reverse := rfl

/-- **The previous algorithm refutes `k = 6`** (memo on, the C). -/
theorem previousAlgorithm_refutes_six : (run (published 6 true) 40).1 = .unsat := by
  have h := congrArg Prod.fst published_six_memo
  rw [summary_fst] at h
  exact h

/-- **The previous algorithm refutes `k = 6`** (memo off, the Python reference). -/
theorem previousAlgorithm_refutes_six_memo_off : (run (published 6 false) 40).1 = .unsat := by
  have h := congrArg Prod.fst published_six_trace
  rw [summaryTrace_fst] at h
  exact h

/-- The memo-off run makes exactly the calls of the Python reference. -/
theorem previousAlgorithm_trace_eq_python :
    (run (published 6 false) 40).2.trace.reverse = pythonTrace := by
  have h := congrArg (fun r => r.2.2) published_six_trace
  simp only [summaryTrace_trace] at h
  exact h

/-! #### The truth -/

/-- The closing order of `solutions34.json` (`repaired_rules`). -/
def witness : List (Fin 34) := witnessOrder.map (fun i => ⟨i % 34, Nat.mod_lt _ (by decide)⟩)

/-- **Six stacks suffice**: the witness closes every customer at cost 6. -/
theorem solvable_six : Solvable G34 6 ∅ := by
  refine ⟨witness, ⟨by decide +kernel, fun x => by simp only [Finset.notMem_empty, not_false_eq_true, iff_true]; revert x; decide +kernel⟩, ?_⟩
  rw [← dec_zero (n := 34), ← ordCost_eq (c := published 6 true) hnb34 witness 0 0 (by simp [opened_empty])]
  decide +kernel

/-- **Five do not**: the sound search (subset rule, old move, memo) refutes `k = 5`. -/
theorem not_solvable_five : ¬ Solvable G34 5 ∅ :=
  exec_root_sound (specFilter_false_sound 5) (specFilter_playable 5 false)
    (run_spec (c := subsetOnly 5) hnb34 40 subsetOnly_five)

theorem pathwidth_eq_five : pathwidth G34 = 5 := by
  have h6 := solvable_empty_iff.1 solvable_six
  have h5 := mt solvable_empty_iff.2 not_solvable_five
  rw [searchSol_empty_iff_pathwidth_add_one_le] at h6 h5
  omega

theorem hreq34 : ∃ c p, M34.requires c p := ⟨0, 0, Or.inl rfl⟩

theorem mospValue_eq_six : M34.mospValue = 6 := by
  have h6 := solvable_empty_iff.1 solvable_six
  have h5 := mt solvable_empty_iff.2 not_solvable_five
  rw [searchSol_mospGraph_iff_mospValue_le M34 hreq34] at h6 h5
  omega

/-! #### The wrong answer -/

/-- The previous algorithm's refutation of 6 is a run of the development's search with the
code's filter (`codeFilter`: the definite move as published, then the subset rule), old move
and memo, from the root. -/
theorem exec_codeFilter_six : ∃ M', Exec G34 6 (codeFilter G34 6) ∅ ∅ ∅ none M' :=
  ⟨_, run_spec (c := published 6 true) hnb34 40 previousAlgorithm_refutes_six⟩

/-- **The node-level failure reaches the root**: on this instance the code's filter is not
node-sound at `k = 6` (compare `not_codeFilterSound_cexGraph`), because a run of it from the
root refutes a solvable instance. -/
theorem not_filterSound_codeFilter : ¬ FilterSound G34 6 (codeFilter G34 6) := by
  intro hF
  obtain ⟨M', hE⟩ := exec_codeFilter_six
  have hP : FilterPlayable G34 6 (codeFilter G34 6) := specFilter_playable (G := G34) 6 true
  exact exec_root_sound hF hP hE solvable_six

/-- **The previous algorithm reports a wrong optimum.** On the 34-customer instance `M34`,
Chu & Stuckey's (2009) customer search with the definite move as published, the subset rule,
the old move and the memo (better move off) refutes `k = 6` and finds a solution at `k = 7`, so
it reports the optimum 7, its refutation is a run of the modelled search with the code's
filter; yet `mospValue M34 = 6` and the pathwidth of its MOSP graph is 5, not 6. -/
theorem previousAlgorithm_wrong_optimum :
    (run (published 6 true) 40).1 = .unsat ∧ (run (published 7 true) 40).1 = .sat ∧
      (∃ M', Exec G34 6 (codeFilter G34 6) ∅ ∅ ∅ none M') ∧
      Solvable G34 6 ∅ ∧ M34.mospValue = 6 ∧ pathwidth M34.mospGraph = 5 :=
  ⟨previousAlgorithm_refutes_six, published_seven, exec_codeFilter_six, solvable_six,
    mospValue_eq_six, pathwidth_eq_five⟩

end WrongOptimum

end Search

end MOSPFormalization
