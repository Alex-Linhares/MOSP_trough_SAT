/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The SAT encoding

`satisfiability/mosp_encoding.py` turns "is `MOSP(M) ≤ k`?" into a CNF formula
and hands it to a solver. Every optimal value this project reports rests on that
translation being faithful: a witness ordering can be checked by anyone, but the
refutation at `k-1` only means what we claim if the formula it refutes really
says what we think.

This file states and proves that correspondence.

## What is modelled

The variables are modelled as predicates rather than as literals in a clause
list, and each clause family becomes a conjunct of `Encodes`. Two constraint
families are stated by their meaning rather than their implementation:

* **at most one** pattern per position, and one position per pattern, which the
  encoder emits through a ladder encoding;
* **at most `k`** open stacks per step, which the encoder emits through a
  totalizer.

Both are standard cardinality encodings whose correctness is established
elsewhere and independent of MOSP. Modelling their internals here would add bulk
without touching the part that is actually specific to this problem — the
open-stack forcing, which is where our implementation has in fact gone wrong
before.

## What is not modelled

That `mosp_encoding.py` emits exactly these clauses. The gap between this
development and the Python is a reading, not a proof.
-/

import MOSPFormalization.OpenStacks

set_option linter.unusedSectionVars false
set_option linter.unreachableTactic false

open Finset
open scoped Classical

namespace MOSPFormalization

variable {C P : Type*} [Fintype C] [DecidableEq C] [Fintype P] [DecidableEq P]

namespace MOSPInstance

variable (M : MOSPInstance C P) [DecidableRel M.requires]

/-- An assignment to the encoding's three variable families.

`x p t` places pattern `p` at position `t`; `y p t` says `p` is placed at or
before `t`; `o c t` says customer `c`'s stack is open at step `t`. -/
structure Assignment (C P : Type*) where
  x : P → ℕ → Prop
  y : P → ℕ → Prop
  o : C → ℕ → Prop

variable (n : ℕ)

/-- The permutation constraints: every pattern occupies exactly one position,
and every position holds exactly one pattern. -/
def PermutationConstraints (a : Assignment C P) : Prop :=
  (∀ p : P, ∃! t : ℕ, t < n ∧ a.x p t) ∧
  (∀ t : ℕ, t < n → ∃! p : P, a.x p t) ∧
  -- The encoder has no `x` variable beyond the last position, so nothing can be
  -- placed there. Stating it keeps `∃!` from being satisfied by a witness below
  -- `n` while `x` also holds somewhere above it.
  (∀ p t, a.x p t → t < n)

/-- The prefix constraints tying `y` to `x`: `y p t` holds exactly when `p` is
placed at some position at or before `t`. -/
def PrefixConstraints (a : Assignment C P) : Prop :=
  (∀ p t, a.x p t → a.y p t) ∧
  (∀ p t, a.y p t → a.y p (t + 1)) ∧
  (∀ p t, a.y p (t + 1) → a.y p t ∨ a.x p (t + 1)) ∧
  (∀ p, a.y p 0 → a.x p 0)

/-- The open-stack constraints. A customer's stack is forced open when one of
its patterns is placed at this step, or when one of its patterns is placed and
another is not.

These two cases are exactly `isActive`, which is why it must be inclusive at
both ends: a customer whose only pattern sits at step `t` is caught by the first
case, and a definition demanding a pattern strictly beyond `t` would call it
closed while the encoding forces it open. -/
def OpenStackConstraints (a : Assignment C P) : Prop :=
  (∀ c p t, p ∈ M.patterns c → a.x p t → a.o c t) ∧
  (∀ c p q t, p ∈ M.patterns c → q ∈ M.patterns c →
      a.y p t → ¬ a.y q t → a.o c t)

/-- At most `k` stacks open at any step. -/
def WidthConstraint (k : ℕ) (a : Assignment C P) : Prop :=
  ∀ t : ℕ, t < n → (univ.filter (fun c => a.o c t)).card ≤ k

/-- The full encoding of "`MOSP(M) ≤ k`". -/
def Encodes (k : ℕ) (a : Assignment C P) : Prop :=
  PermutationConstraints (Fintype.card P) a ∧
  PrefixConstraints a ∧
  M.OpenStackConstraints a ∧
  WidthConstraint (Fintype.card P) k a

/-- The assignment read off a layout: place each pattern at its own position,
take the prefix relation from that, and open exactly the active stacks. -/
noncomputable def ofLayout (σ : LinearLayout P) : Assignment C P where
  x p t := (σ p).val = t
  y p t := (σ p).val ≤ t
  o c t := M.isActive σ c t

/-! ### The open-stack forcing is exactly `isActive`

The two forcing cases of `OpenStackConstraints` are proved to imply `isActive`,
and conversely every active customer falls into one of them. Together these say
the encoding's `o` variable can be read as "this stack is open" and nothing
weaker or stronger. -/

/-- A pattern of `c` sitting exactly at step `t` opens `c`'s stack there.

This is the case that forced `isActive` to be inclusive: the witness `p` serves
both sides, lying at or before `t` and at or after `t` simultaneously. -/
theorem isActive_of_placed (σ : LinearLayout P) {c : C} {p : P} {t : ℕ}
    (hp : p ∈ M.patterns c) (hx : (σ p).val = t) :
    M.isActive σ c t := by
  constructor
  · exact ⟨p, mem_filter.mpr ⟨hp, hx.le⟩⟩
  · exact ⟨p, mem_filter.mpr ⟨hp, hx.ge⟩⟩

/-- One pattern of `c` placed by step `t` and another not yet placed opens the
stack: the first witnesses the prefix, the second the suffix. -/
theorem isActive_of_split (σ : LinearLayout P) {c : C} {p q : P} {t : ℕ}
    (hp : p ∈ M.patterns c) (hq : q ∈ M.patterns c)
    (hyp : (σ p).val ≤ t) (hyq : ¬ (σ q).val ≤ t) :
    M.isActive σ c t := by
  constructor
  · exact ⟨p, mem_filter.mpr ⟨hp, hyp⟩⟩
  · exact ⟨q, mem_filter.mpr ⟨hq, le_of_lt (not_le.mp hyq)⟩⟩

/-- Conversely, an open stack is always one of the two forcing cases: either a
pattern of `c` sits exactly at `t`, or one is placed by `t` while another is
not. So the encoding forces `o` on precisely the active customers. -/
theorem placed_or_split_of_isActive (σ : LinearLayout P) {c : C} {t : ℕ}
    (h : M.isActive σ c t) :
    (∃ p ∈ M.patterns c, (σ p).val = t) ∨
    (∃ p ∈ M.patterns c, ∃ q ∈ M.patterns c,
        (σ p).val ≤ t ∧ ¬ (σ q).val ≤ t) := by
  obtain ⟨⟨p, hp⟩, ⟨q, hq⟩⟩ := h
  obtain ⟨hpmem, hple⟩ := mem_filter.mp hp
  obtain ⟨hqmem, hqge⟩ := mem_filter.mp hq
  rcases eq_or_lt_of_le hqge with heq | hlt
  · -- `q` sits exactly at `t`
    exact Or.inl ⟨q, hqmem, heq.symm⟩
  · -- `q` lies strictly beyond `t`, so it splits against `p`
    exact Or.inr ⟨p, hpmem, q, hqmem, hple, not_le.mpr hlt⟩

/-! ### Completeness: every good layout satisfies the encoding -/

/-- The layout's assignment opens exactly the active stacks, so the width
constraint is counting `openStacksAt`. The two sides differ only by which
`Decidable` instance the filter uses. -/
theorem card_o_ofLayout (σ : LinearLayout P) (t : ℕ) :
    (univ.filter (fun c => (M.ofLayout σ).o c t)).card = M.openStacksAt σ t := by
  -- The two sides are the same filter under different `Decidable` instances,
  -- which `Finset.filter_congr_decidable` reconciles.
  -- Both sides are the same filter under different `Decidable` instances. The
  -- alternatives are kept because `rfl` only discharges this inside `first`,
  -- where elaboration unfolds further than it does standalone; dropping them
  -- makes the proof fail.
  unfold openStacksAt ofLayout
  first
  | rfl
  | exact congrArg Finset.card (Finset.filter_congr_decidable _ _ _)
  | simp [Finset.filter_congr_decidable]

/-- Each step's open-stack count is bounded by the layout's maximum. -/
theorem openStacksAt_le_maxOpenStacks (σ : LinearLayout P) {t : ℕ}
    (ht : t < Fintype.card P) :
    M.openStacksAt σ t ≤ M.maxOpenStacks σ := by
  have hpos : Fintype.card P ≠ 0 := by omega
  rw [maxOpenStacks]
  rw [dif_neg hpos]
  exact Finset.le_sup' (fun i : Fin (Fintype.card P) => M.openStacksAt σ i.val)
    (mem_univ (⟨t, ht⟩ : Fin (Fintype.card P)))

/-- A layout achieving at most `k` open stacks yields a satisfying assignment.

This is the direction that says the encoding is not too strong: if a sequence
exists, the solver will find the formula satisfiable. -/
theorem encodes_ofLayout (σ : LinearLayout P) {k : ℕ}
    (hk : M.maxOpenStacks σ ≤ k) :
    M.Encodes k (M.ofLayout σ) := by
  refine ⟨⟨?_, ?_, ?_⟩, ⟨?_, ?_, ?_, ?_⟩, ⟨?_, ?_⟩, ?_⟩
  · -- every pattern occupies exactly one position: its own
    intro p
    exact ⟨(σ p).val, ⟨(σ p).isLt, rfl⟩, fun t ht => ht.2.symm⟩
  · -- every position holds exactly one pattern
    intro t ht
    refine ⟨σ.symm ⟨t, ht⟩, by simp [ofLayout], ?_⟩
    intro p hp
    have : σ p = (⟨t, ht⟩ : Fin (Fintype.card P)) := Fin.ext hp
    simpa using congrArg σ.symm this
  · -- nothing is placed beyond the last position
    intro p t hx
    exact hx ▸ (σ p).isLt
  · exact fun p t h => h.le
  · exact fun p t h => Nat.le_succ_of_le h
  · intro p t h
    rcases Nat.lt_or_ge (σ p).val (t + 1) with hlt | hge
    · exact Or.inl (Nat.lt_succ_iff.mp hlt)
    · exact Or.inr (Nat.le_antisymm h hge)
  · exact fun p h => Nat.le_zero.mp h
  · exact fun c p t hp hx => M.isActive_of_placed σ hp hx
  · exact fun c p q t hp hq hyp hyq => M.isActive_of_split σ hp hq hyp hyq
  · -- width: each step's count is at most the layout's maximum, hence at most k
    intro t ht
    rw [M.card_o_ofLayout σ t]
    exact le_trans (M.openStacksAt_le_maxOpenStacks σ ht) hk

/-! ### Soundness: every satisfying assignment yields a good layout

The converse direction, and the one the solver's refutations actually rest on:
if the formula is satisfiable then a sequence exists, so UNSAT at `k-1` really
does mean no sequence achieves `k-1`. -/

/-- The position a satisfying assignment gives to pattern `p`. -/
noncomputable def posOf (a : Assignment C P)
    (h : PermutationConstraints (Fintype.card P) a) (p : P) : ℕ :=
  (h.1 p).choose

theorem posOf_lt (a : Assignment C P)
    (h : PermutationConstraints (Fintype.card P) a) (p : P) :
    posOf a h p < Fintype.card P :=
  (h.1 p).choose_spec.1.1

theorem x_posOf (a : Assignment C P)
    (h : PermutationConstraints (Fintype.card P) a) (p : P) :
    a.x p (posOf a h p) :=
  (h.1 p).choose_spec.1.2

theorem posOf_unique (a : Assignment C P)
    (h : PermutationConstraints (Fintype.card P) a) {p : P} {t : ℕ}
    (hx : a.x p t) : posOf a h p = t :=
  ((h.1 p).choose_spec.2 t ⟨h.2.2 p t hx, hx⟩).symm

/-- Reading a layout off a satisfying assignment.

The permutation constraints say each pattern takes exactly one position and each
position takes exactly one pattern, which is precisely a bijection. -/
noncomputable def layoutOf (a : Assignment C P)
    (h : PermutationConstraints (Fintype.card P) a) : LinearLayout P := by
  refine Equiv.ofBijective (fun p => (⟨posOf a h p, posOf_lt a h p⟩ :
      Fin (Fintype.card P))) ⟨?_, ?_⟩
  · -- injective: two patterns at one position contradict the second constraint
    intro p q hpq
    have hp := x_posOf a h p
    have hq := x_posOf a h q
    have hval : posOf a h p = posOf a h q := congrArg Fin.val hpq
    rw [hval] at hp
    obtain ⟨_, _, huniq⟩ := h.2.1 (posOf a h q) (posOf_lt a h q)
    exact (huniq p hp).trans (huniq q hq).symm
  · -- surjective: every position is occupied, by the pattern the constraint gives
    intro i
    obtain ⟨p, hp, _⟩ := h.2.1 i.val i.isLt
    exact ⟨p, Fin.ext (posOf_unique a h hp)⟩

@[simp] theorem layoutOf_val (a : Assignment C P)
    (h : PermutationConstraints (Fintype.card P) a) (p : P) :
    ((layoutOf a h) p).val = posOf a h p := rfl

/-- Under a satisfying assignment, `y p t` says exactly that `p` is placed by
step `t`. The prefix constraints pin it down in both directions. -/
theorem y_iff_posOf_le (a : Assignment C P)
    (hperm : PermutationConstraints (Fintype.card P) a)
    (hpre : PrefixConstraints a) (p : P) (t : ℕ) :
    a.y p t ↔ posOf a hperm p ≤ t := by
  induction t with
  | zero =>
      constructor
      · intro hy
        exact Nat.le_zero.mpr (posOf_unique a hperm (hpre.2.2.2 p hy))
      · intro hle
        have : posOf a hperm p = 0 := Nat.le_zero.mp hle
        exact hpre.1 p 0 (this ▸ x_posOf a hperm p)
  | succ t ih =>
      constructor
      · intro hy
        rcases hpre.2.2.1 p t hy with hprev | hxsucc
        · exact Nat.le_succ_of_le (ih.mp hprev)
        · exact le_of_eq (posOf_unique a hperm hxsucc)
      · intro hle
        rcases Nat.lt_or_ge (posOf a hperm p) (t + 1) with hlt | hge
        · exact hpre.2.1 p t (ih.mpr (Nat.lt_succ_iff.mp hlt))
        · have heq : posOf a hperm p = t + 1 := Nat.le_antisymm hle hge
          exact hpre.1 p (t + 1) (heq ▸ x_posOf a hperm p)

/-- Every active customer has its `o` variable forced true.

This is where the forcing clauses do their work: an open stack is one of the two
cases of `placed_or_split_of_isActive`, and each case has a clause forcing `o`. -/
theorem o_of_isActive {a : Assignment C P}
    (hperm : PermutationConstraints (Fintype.card P) a)
    (hpre : PrefixConstraints a) (hopen : M.OpenStackConstraints a)
    {c : C} {t : ℕ} (hact : M.isActive (layoutOf a hperm) c t) :
    a.o c t := by
  rcases M.placed_or_split_of_isActive (layoutOf a hperm) hact with
    ⟨p, hp, hx⟩ | ⟨p, hp, q, hq, hple, hqgt⟩
  · exact hopen.1 c p t hp (by rw [← hx]; exact x_posOf a hperm p)
  · refine hopen.2 c p q t hp hq ?_ ?_
    · exact (y_iff_posOf_le a hperm hpre p t).mpr (by simpa using hple)
    · exact fun hy => hqgt (by simpa using (y_iff_posOf_le a hperm hpre q t).mp hy)

/-- A satisfying assignment yields a layout achieving at most `k` open stacks.

This is the direction the refutations rest on. The encoding only ever *forces*
`o` true, never false, so a satisfying assignment may open stacks that are not
active; that is harmless, because the active customers are a subset of those
with `o` set, and the width constraint bounds the larger set. -/
theorem maxOpenStacks_layoutOf_le {a : Assignment C P} {k : ℕ}
    (h : M.Encodes k a) :
    M.maxOpenStacks (layoutOf a h.1) ≤ k := by
  obtain ⟨hperm, hpre, hopen, hwidth⟩ := h
  rw [maxOpenStacks]
  split
  · exact Nat.zero_le k
  · refine Finset.sup'_le _ _ ?_
    intro i _
    refine le_trans (Finset.card_le_card ?_) (hwidth i.val i.isLt)
    intro c hc
    have hact : M.isActive (layoutOf a hperm) c i.val := (mem_filter.mp hc).2
    exact mem_filter.mpr ⟨mem_univ c, M.o_of_isActive hperm hpre hopen hact⟩

/-- **The encoding is faithful.** A satisfying assignment exists exactly when
some production sequence keeps at most `k` stacks open.

Read left to right, a refutation means no sequence achieves `k`: this is what
licenses reporting UNSAT at `k-1` together with a witness at `k` as a proof of
optimality. Read right to left, the encoding never rules out a sequence that
exists. -/
theorem encodes_iff_mospValue_le (k : ℕ) [Nonempty (LinearLayout P)] :
    (∃ a : Assignment C P, M.Encodes k a) ↔ M.mospValue ≤ k := by
  constructor
  · rintro ⟨a, ha⟩
    exact le_trans (M.mospValue_le_maxOpenStacks (layoutOf a ha.1))
      (M.maxOpenStacks_layoutOf_le ha)
  · intro hle
    -- `mospValue` is an infimum over a nonempty set of naturals, so it is
    -- attained; that layout satisfies the encoding.
    obtain ⟨σ, hσ⟩ : ∃ σ : LinearLayout P, M.maxOpenStacks σ = M.mospValue :=
      Nat.sInf_mem (Set.range_nonempty _)
    exact ⟨M.ofLayout σ, M.encodes_ofLayout σ (hσ ▸ hle)⟩

end MOSPInstance

end MOSPFormalization
