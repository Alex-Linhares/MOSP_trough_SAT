/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# A checked certificate implies the bound

The theorems behind every lower-bound certificate of `reports/obstruction_search.md`
are in `EmptyPair.lean` (Harper's bound), `Minor.lean` (minor monotonicity) and
`Sandwich.lean` (degeneracy ≤ pathwidth, the branch lemma). What they lack is the
statement in the form the checker's output cites, `paper1/obstruction_check.py`:
*this certificate, checked, implies this bound*. This file states those forms, each
first checked by brute force on every graph to 8 vertices
(`reports/scratch/obstruction_search/09_lean/check.py`, 13,598 graphs, 120,841 levels,
271,960 random contraction sequences, zero violations), and closes one concrete
instance of each kind by `decide`.

## Family E (expansion): the contrapositive of Harper

* `pathwidth_ge_of_forall_closedNbhd` — for `j ≤ n`, if every `j`-set `A` has
  `|N[A]| > j + k` then `pathwidth G ≥ k + 1`. This is `exists_closedNbhd_card_le`
  read backwards, and it is what an UNSAT answer at level `(t, b)` certifies
  (`check-expansion`): `pathwidth_ge_of_unsat`, "no `t`-set has `|N[C]| ≤ b`" gives
  `b + 1 ≤ t + pathwidth G`; in MOSP units `MOSPInstance.mospValue_ge_of_unsat`,
  `b + 2 ≤ t + mospValue`. The hypothesis `j ≤ n` is not decorative: for `j > n`
  the premise is vacuous and the conclusion false (checked).

## Family M (minors): the min-degree certificate

* `pathwidth_ge_of_minor_minDegree` — a legal contraction sequence whose result has
  minimum degree `≥ d` on any vertex set `S` proves `pathwidth G ≥ d`. This is the C
  program's `bound` status on a minor (its floor is the degeneracy of the minor) and
  `paper1/dataset.py`'s `minor_certificate`, through `minDegreeIn_le_degeneracy`,
  `degeneracy_le_pathwidth` and `pathwidth_applySeq_le`.
  `pathwidth_ge_of_minor_forall_degree` is the same with the degrees taken in
  `minorOf G seq` itself, as the item phrased it, **with a nonempty-minor hypothesis
  the item's phrasing lacked**: when every vertex is removed the premise is vacuous
  and the statement false (30,785 of the 271,960 checked sequences).
  In MOSP units: `MOSPInstance.mospValue_ge_of_minor_minDegree`.

## The Bool checker, and `decide`

* `checkSeq G seq` — the certificate replay as a `Bool`: every contraction step is an
  edge of the current graph. `checkSeq_sound` (`= true → IsContractionSeq`) and
  `checkSeq_complete`; `minDegreeOfMinor G seq` the minimum degree of the survivors;
  `pathwidth_ge_of_checkSeq` — a sequence the checker accepts, with minimum degree `d`
  on the survivors, proves `pathwidth G ≥ d`. Adjacency after a step is decidable
  (`instDecidableRelContractEdgeAdj`, `instDecidableRelIsolateAdj`, and by recursion
  `applySeq`), and so is `IsContractionSeq` itself.
* `two_le_pathwidth_octGraph` — the 8-cycle with five contractions into vertex `0`:
  the checker accepts the sequence and the triangle left has minimum degree `2`, both
  by `decide`, so `pathwidth ≥ 2`, which is its pathwidth.
* `three_le_pathwidth_k34` — `K_{3,4}` at level `j = 1`: every singleton has
  `|N[A]| = 4 > 1 + 2`, decided over all 128 subsets of `Fin 7`, so `pathwidth ≥ 3`,
  which is its pathwidth.
* `eight_le_mospValue_warwick` — a **record** certificate: the 30-customer bound-gap
  instance `Warwick 1729`, its family-M `bound` certificate (15 contractions) extended by
  7 least-c contractions to a `K₈`, checked by `decide +kernel` on the MOSP graph built from
  the instance's own matrix: every pattern order opens at least 8 stacks (optimum 9).

## What is not here

A refutation by the C program on a minor (`c_status = refutation`) rests on
`Search/`'s soundness theorems and the binary's faithfulness, as before; the branch
certificate's theorem is `branch_lemma_separator` as it stands, and a decidable
connectivity check for it is not attempted. `decide +kernel` reaches further than
expected: the kernel caches closed adjacency terms, so the 22-step certificate on the
30-customer record instance below is checked in seconds; the 125-customer certificates
of items 04–05 were not tried (§9 of the report).
-/

import MOSPFormalization.EmptyPair
import MOSPFormalization.Minor

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### Family E: the contrapositive of Harper's bound -/

section Expansion

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- **Harper's bound, contrapositive form.** For `j ≤ n`: if every `j`-set has a closed
neighbourhood of more than `j + k` vertices, the pathwidth is at least `k + 1`. -/
theorem pathwidth_ge_of_forall_closedNbhd (j k : ℕ) (hj : j ≤ Fintype.card V)
    (h : ∀ A : Finset V, A.card = j → j + k < (closedNbhd G A).card) :
    k + 1 ≤ pathwidth G := by
  obtain ⟨A, hA, hN⟩ := exists_closedNbhd_card_le G j hj
  have := h A hA
  omega

/-- **What an UNSAT level certifies** (`check-expansion`): no `t`-set has `|N[C]| ≤ b`,
hence `b + 1 ≤ t + pathwidth G`, i.e. `pathwidth G ≥ b + 1 − t`. -/
theorem pathwidth_ge_of_unsat (t b : ℕ) (ht : t ≤ Fintype.card V)
    (h : ∀ A : Finset V, A.card = t → ¬ (closedNbhd G A).card ≤ b) :
    b + 1 ≤ t + pathwidth G := by
  obtain ⟨A, hA, hN⟩ := exists_closedNbhd_card_le G t ht
  have := h A hA
  omega

/-- Without `j ≤ n` the statement is false: on one vertex, `j = 2` has no `2`-set, so the
premise holds for every `k`, while the pathwidth is `0`. -/
theorem pathwidth_ge_of_forall_closedNbhd_needs_le :
    ¬ (∀ (j k : ℕ),
        (∀ A : Finset (Fin 1), A.card = j → j + k < (closedNbhd (⊥ : SimpleGraph (Fin 1)) A).card) →
        k + 1 ≤ pathwidth (⊥ : SimpleGraph (Fin 1))) := by
  intro h
  have h1 := h 2 0 (fun A hA => by
    have := A.card_le_univ
    simp only [Fintype.card_fin] at this
    omega)
  have h0 : pathwidth (⊥ : SimpleGraph (Fin 1)) ≤ 0 := by
    let P : PathDecomposition (⊥ : SimpleGraph (Fin 1)) :=
      { length := 0
        bag := fun _ => Finset.univ
        vertex_coverage := fun v => ⟨0, Finset.mem_univ v⟩
        edge_coverage := fun _ _ h => h.elim
        interval := fun _ _ _ _ _ _ _ _ => Finset.mem_univ _ }
    calc pathwidth ⊥ ≤ P.width := pathwidth_le_width _ P
      _ = 0 := by simp [PathDecomposition.width, P]
  omega

end Expansion

namespace MOSPInstance

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]
variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- **An UNSAT level in MOSP units**: no `t`-set of customers has `|N[C]| ≤ b` in the MOSP
graph, hence every pattern order opens at least `b + 2 − t` stacks. -/
theorem mospValue_ge_of_unsat (hreq : ∃ c p, M.requires c p) (t b : ℕ)
    (ht : t ≤ Fintype.card C)
    (h : ∀ A : Finset C, A.card = t → ¬ (closedNbhd M.mospGraph A).card ≤ b) :
    b + 2 ≤ t + M.mospValue := by
  rw [M.mospValue_eq_pathwidth_add_one hreq]
  have := pathwidth_ge_of_unsat M.mospGraph t b ht h
  omega

end MOSPInstance

/-! ### Decidable adjacency along a contraction sequence -/

instance instDecidableRelContractEdgeAdj (G : SimpleGraph V) [DecidableRel G.Adj] (u v : V) :
    DecidableRel (contractEdge G u v).Adj := fun x y =>
  inferInstanceAs (Decidable (x ≠ y ∧ x ≠ v ∧ y ≠ v ∧
    (G.Adj x y ∨ (x = u ∧ G.Adj v y) ∨ (y = u ∧ G.Adj v x))))

instance instDecidableRelIsolateAdj (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    DecidableRel (isolate G v).Adj := fun x y =>
  inferInstanceAs (Decidable (G.Adj x y ∧ x ≠ v ∧ y ≠ v))

instance instDecidableRelApplyStepAdj (G : SimpleGraph V) [DecidableRel G.Adj] :
    (s : V × Option V) → DecidableRel (applyStep G s).Adj
  | (v, some u) => inferInstanceAs (DecidableRel (contractEdge G u v).Adj)
  | (v, none) => inferInstanceAs (DecidableRel (isolate G v).Adj)

/-- Adjacency after replaying a sequence is decidable (by recursion on the sequence). -/
@[instance_reducible]
def decidableRelApplySeqAdj (G : SimpleGraph V) [DecidableRel G.Adj] :
    (seq : List (V × Option V)) → DecidableRel (applySeq G seq).Adj
  | [] => inferInstanceAs (DecidableRel G.Adj)
  | s :: rest => @decidableRelApplySeqAdj (applyStep G s) (instDecidableRelApplyStepAdj G s) rest

instance instDecidableRelApplySeqAdj (G : SimpleGraph V) [DecidableRel G.Adj]
    (seq : List (V × Option V)) : DecidableRel (applySeq G seq).Adj :=
  decidableRelApplySeqAdj G seq

instance instDecidableStepValid (G : SimpleGraph V) [DecidableRel G.Adj] :
    (s : V × Option V) → Decidable (StepValid G s)
  | (v, some u) => inferInstanceAs (Decidable (G.Adj u v))
  | (_, none) => inferInstanceAs (Decidable True)

/-- Legality of a sequence is decidable. -/
@[instance_reducible]
def decidableIsContractionSeq (G : SimpleGraph V) [DecidableRel G.Adj] :
    (seq : List (V × Option V)) → Decidable (IsContractionSeq G seq)
  | [] => inferInstanceAs (Decidable True)
  | s :: rest =>
    @instDecidableAnd _ _ (instDecidableStepValid G s)
      (@decidableIsContractionSeq (applyStep G s) (instDecidableRelApplyStepAdj G s) rest)

instance instDecidableIsContractionSeq (G : SimpleGraph V) [DecidableRel G.Adj]
    (seq : List (V × Option V)) : Decidable (IsContractionSeq G seq) :=
  decidableIsContractionSeq G seq

/-! ### The Bool checker -/

/-- The certificate replay as a `Bool`: every contraction step `(v, some u)` must be an edge
`uv` of the graph at that moment; a deletion `(v, none)` is always allowed. This is what
`paper1/obstruction_check.py`'s own replay checks, step by step. -/
def checkSeq (G : SimpleGraph V) [DecidableRel G.Adj] : List (V × Option V) → Bool
  | [] => true
  | (v, some u) :: rest => decide (G.Adj u v) && checkSeq (contractEdge G u v) rest
  | (v, none) :: rest => checkSeq (isolate G v) rest

/-- A sequence the checker accepts is a legal contraction sequence. -/
theorem checkSeq_sound (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∀ seq : List (V × Option V), checkSeq G seq = true → IsContractionSeq G seq
  | [], _ => trivial
  | (v, some u) :: rest, h => by
    simp only [checkSeq, Bool.and_eq_true, decide_eq_true_eq] at h
    exact ⟨h.1, checkSeq_sound (contractEdge G u v) rest h.2⟩
  | (v, none) :: rest, h => ⟨trivial, checkSeq_sound (isolate G v) rest h⟩

/-- And conversely: the checker accepts every legal sequence. -/
theorem checkSeq_complete (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∀ seq : List (V × Option V), IsContractionSeq G seq → checkSeq G seq = true
  | [], _ => rfl
  | (v, some u) :: rest, h => by
    simp only [checkSeq, Bool.and_eq_true, decide_eq_true_eq]
    exact ⟨h.1, checkSeq_complete (contractEdge G u v) rest h.2⟩
  | (v, none) :: rest, h => checkSeq_complete (isolate G v) rest h.2

theorem checkSeq_iff (G : SimpleGraph V) [DecidableRel G.Adj] (seq : List (V × Option V)) :
    checkSeq G seq = true ↔ IsContractionSeq G seq :=
  ⟨checkSeq_sound G seq, checkSeq_complete G seq⟩

/-! ### Family M: the min-degree certificate -/

section Minor

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- **The min-degree minor certificate.** A legal contraction sequence whose result has
minimum degree at least `d` on some vertex set `S` proves `pathwidth G ≥ d`: the C
program's `bound` status on a minor, and `paper1/dataset.py`'s `minor_certificate`. The
removed vertices are isolated in `applySeq G seq`, so `S = univ \ removed seq` reads the
degrees of the minor itself (`degree_minorOf_eq`). -/
theorem pathwidth_ge_of_minor_minDegree (seq : List (V × Option V)) (h : IsContractionSeq G seq)
    (S : Finset V) {d : ℕ} (hd : d ≤ minDegreeIn (applySeq G seq) S) : d ≤ pathwidth G :=
  hd.trans ((minDegreeIn_le_degeneracy _ S).trans
    ((degeneracy_le_pathwidth _).trans (pathwidth_applySeq_le G seq h)))

/-- The minimum degree of the survivors after the replay: the minor's minimum degree,
computably. -/
def minDegreeOfMinor (seq : List (V × Option V)) : ℕ :=
  minDegreeIn (applySeq G seq) (Finset.univ \ removed seq)

/-- **A checked certificate implies the bound.** A sequence `checkSeq` accepts whose
survivors have minimum degree at least `d` proves `pathwidth G ≥ d`. On a concrete graph
with decidable adjacency both premises are decided by `decide`. -/
theorem pathwidth_ge_of_checkSeq (seq : List (V × Option V)) (hc : checkSeq G seq = true)
    {d : ℕ} (hd : d ≤ minDegreeOfMinor G seq) : d ≤ pathwidth G :=
  pathwidth_ge_of_minor_minDegree G seq (checkSeq_sound G seq hc) _ hd

/-- The minor's adjacency is decidable (it is `applySeq`'s, on the survivors). -/
instance instDecidableRelMinorOfAdj (seq : List (V × Option V)) :
    DecidableRel (minorOf G seq).Adj := fun a b =>
  inferInstanceAs (Decidable ((applySeq G seq).Adj a.1 b.1))

/-- The degree of a survivor in `minorOf G seq` is its degree in `applySeq G seq` counted on
the survivors. -/
theorem degree_minorOf_eq (seq : List (V × Option V)) (v : V) (hv : v ∉ removed seq) :
    (minorOf G seq).degree ⟨v, hv⟩ = degreeIn (applySeq G seq) (Finset.univ \ removed seq) v := by
  rw [← SimpleGraph.card_neighborFinset_eq_degree]
  unfold degreeIn
  refine Finset.card_bij (fun a _ => a.val) ?_ ?_ ?_
  · intro a ha
    rw [SimpleGraph.mem_neighborFinset] at ha
    rw [Finset.mem_filter, Finset.mem_sdiff]
    exact ⟨⟨Finset.mem_univ _, a.2⟩, ha⟩
  · intro a _ b _ hab
    exact Subtype.ext hab
  · intro u hu
    rw [Finset.mem_filter, Finset.mem_sdiff] at hu
    exact ⟨⟨u, hu.1.2⟩, by rw [SimpleGraph.mem_neighborFinset]; exact hu.2, rfl⟩

/-- The item's phrasing, corrected: if the minor is **nonempty** and every one of its
vertices has degree at least `d` in it, then `pathwidth G ≥ d`. Without the nonemptiness
the premise is vacuous once every vertex is removed, and the statement false. -/
theorem pathwidth_ge_of_minor_forall_degree (seq : List (V × Option V))
    (h : IsContractionSeq G seq) (hne : ∃ v, v ∉ removed seq) {d : ℕ}
    (hd : ∀ v (hv : v ∉ removed seq), d ≤ (minorOf G seq).degree ⟨v, hv⟩) :
    d ≤ pathwidth G := by
  apply pathwidth_ge_of_minor_minDegree G seq h (Finset.univ \ removed seq)
  unfold minDegreeIn
  obtain ⟨v, hv⟩ := hne
  have hS : (Finset.univ \ removed seq).Nonempty :=
    ⟨v, Finset.mem_sdiff.mpr ⟨Finset.mem_univ v, hv⟩⟩
  split_ifs
  apply Finset.le_inf'
  intro u hu
  have hu' : u ∉ removed seq := (Finset.mem_sdiff.mp hu).2
  rw [← degree_minorOf_eq G seq u hu']
  exact hd u hu'

/-- The phrasing without nonemptiness is false: on one vertex, deleting it leaves no survivor,
so "every survivor has degree `≥ 1`" holds, while the pathwidth is `0`. -/
theorem pathwidth_ge_of_minor_forall_degree_needs_nonempty :
    ¬ (∀ (seq : List (Fin 1 × Option (Fin 1))),
        IsContractionSeq (⊥ : SimpleGraph (Fin 1)) seq → ∀ d : ℕ,
        (∀ v (hv : v ∉ removed seq), d ≤ (minorOf (⊥ : SimpleGraph (Fin 1)) seq).degree ⟨v, hv⟩) →
        d ≤ pathwidth (⊥ : SimpleGraph (Fin 1))) := by
  intro h
  have h1 := h [(0, none)] ⟨trivial, trivial⟩ 1 (fun v hv => by
    obtain rfl : v = 0 := Subsingleton.elim _ _
    exact absurd (by decide : (0 : Fin 1) ∈ removed [((0 : Fin 1), (none : Option (Fin 1)))]) hv)
  have h0 : pathwidth (⊥ : SimpleGraph (Fin 1)) ≤ 0 := by
    let P : PathDecomposition (⊥ : SimpleGraph (Fin 1)) :=
      { length := 0
        bag := fun _ => Finset.univ
        vertex_coverage := fun v => ⟨0, Finset.mem_univ v⟩
        edge_coverage := fun _ _ h => h.elim
        interval := fun _ _ _ _ _ _ _ _ => Finset.mem_univ _ }
    calc pathwidth ⊥ ≤ P.width := pathwidth_le_width _ P
      _ = 0 := by simp [PathDecomposition.width, P]
  omega

end Minor

namespace MOSPInstance

variable {C Pt : Type*} [Fintype C] [DecidableEq C] [Fintype Pt] [DecidableEq Pt]
variable (M : MOSPInstance C Pt) [DecidableRel M.requires]

/-- **The min-degree minor certificate in MOSP units**: a legal contraction sequence of the
MOSP graph whose result has minimum degree at least `d` on `S` proves that every pattern
order opens at least `d + 1` stacks. -/
theorem mospValue_ge_of_minor_minDegree (hreq : ∃ c p, M.requires c p)
    (seq : List (C × Option C)) (h : IsContractionSeq M.mospGraph seq) (S : Finset C) {d : ℕ}
    (hd : d ≤ minDegreeIn (applySeq M.mospGraph seq) S) : d + 1 ≤ M.mospValue := by
  rw [M.mospValue_eq_pathwidth_add_one hreq]
  have := pathwidth_ge_of_minor_minDegree M.mospGraph seq h S hd
  omega

end MOSPInstance

/-! ### Two concrete certificates, closed by `decide` -/

/-- The 8-cycle `0 – 1 – … – 7 – 0`. -/
def octEdges : List (ℕ × ℕ) := [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (0, 7)]

def octGraph : SimpleGraph (Fin 8) := SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ octEdges

instance : DecidableRel octGraph.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ octEdges ∨ (b.val, a.val) ∈ octEdges)))

/-- Contract `7, 6, 5, 4, 3` into `0`, one after the other: the triangle `{0, 1, 2}` is left. -/
def octSeq : List (Fin 8 × Option (Fin 8)) :=
  [(7, some 0), (6, some 0), (5, some 0), (4, some 0), (3, some 0)]

theorem octSeq_checked : checkSeq octGraph octSeq = true := by decide

set_option maxRecDepth 10000 in
theorem octSeq_minDegree : minDegreeOfMinor octGraph octSeq = 2 := by decide

/-- **A min-degree certificate closed by `decide`**: the 8-cycle has pathwidth at least `2`
(it is exactly `2`). -/
theorem two_le_pathwidth_octGraph : 2 ≤ pathwidth octGraph :=
  pathwidth_ge_of_checkSeq octGraph octSeq octSeq_checked (by rw [octSeq_minDegree])

/-- `K_{3,4}`: parts `{0, 1, 2}` and `{3, 4, 5, 6}`. -/
def k34 : SimpleGraph (Fin 7) := SimpleGraph.fromRel fun a b => a.val < 3 ∧ 3 ≤ b.val

instance : DecidableRel k34.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val < 3 ∧ 3 ≤ b.val) ∨ (b.val < 3 ∧ 3 ≤ a.val))))

set_option maxRecDepth 10000 in
/-- Every singleton of `K_{3,4}` has a closed neighbourhood of at least `4 > 1 + 2` vertices,
decided over all `128` subsets of `Fin 7`. -/
theorem k34_level_one : ∀ A : Finset (Fin 7), A.card = 1 → 1 + 2 < (closedNbhd k34 A).card := by
  decide

/-- **An expansion certificate closed by `decide`**: `K_{3,4}` has pathwidth at least `3`
(it is exactly `3`). -/
theorem three_le_pathwidth_k34 : 3 ≤ pathwidth k34 :=
  pathwidth_ge_of_forall_closedNbhd k34 1 2 (by decide) k34_level_one

/-! ### A record certificate, closed by `decide`: `Warwick 1729` (30 customers)

`Warwick 1729: balanced orders, 3 orders per product` (Harvey's `wbo_30_30`) is the one
bound-gap instance of the 338 whose family-M certificate on record has the C program's
`bound` status: `reports/scratch/obstruction_search/04_minor/certificates/Warwick_1729__balanced_orders__3_orders_per_product/ladder.json`,
a 15-step contraction to a 15-vertex minor with `lower = 7`, floor 8 against the optimum 9.
That `lower` is the C program's contraction degeneracy of the minor, not its minimum degree
(which is 5): the certificate implicitly contracts further. Here the record's 15 steps are
extended by 7 least-c contractions (`reports/scratch/obstruction_search/09_lean/warwick_extension.json`)
to an 8-vertex minor of minimum degree 7 — a `K₈` — and the whole 22-step sequence is
checked by `decide +kernel` directly on the MOSP graph of the instance, defined from its
0/1 matrix (`warwickOnes`, 90 requirements): **every pattern order of `Warwick 1729` opens
at least 8 stacks.** The kernel evaluates the 22 nested contractions in a few seconds; the
record's refutation certificate for 9 (`search.json`, a C refutation on a 17-vertex minor)
is not covered, as stated above. -/

/-- The requirements of `Warwick 1729` as `(customer, pattern)` pairs, 0-based rows and
columns of `wbo_30_30.txt`. -/
def warwickOnes : List (ℕ × ℕ) :=
  [(0, 18), (1, 7), (1, 8), (1, 14), (1, 20), (2, 4), (2, 15), (2, 20), (2, 26), (3, 6),
   (3, 10), (3, 14), (4, 6), (4, 22), (4, 27), (5, 1), (5, 8), (5, 13), (5, 21), (6, 0),
   (6, 16), (6, 19), (6, 28), (6, 29), (7, 7), (7, 21), (8, 8), (8, 12), (8, 15), (9, 3),
   (10, 17), (11, 10), (11, 23), (12, 5), (12, 6), (12, 17), (12, 26), (13, 1), (13, 9),
   (14, 10), (14, 12), (14, 28), (15, 9), (15, 11), (15, 24), (16, 22), (16, 23),
   (16, 25), (16, 27), (17, 4), (17, 18), (18, 13), (18, 20), (18, 29), (19, 2), (20, 2),
   (20, 29), (21, 1), (21, 15), (22, 2), (22, 5), (22, 7), (22, 9), (22, 11), (22, 24),
   (22, 25), (23, 11), (24, 16), (24, 18), (25, 3), (25, 4), (25, 25), (25, 27), (26, 0),
   (26, 5), (26, 19), (26, 26), (26, 28), (27, 0), (27, 17), (27, 23), (28, 22), (29, 3),
   (29, 12), (29, 13), (29, 14), (29, 16), (29, 19), (29, 21), (29, 24)]

/-- The instance: customer `c` requires pattern `p` iff `(c, p)` is listed. -/
def warwickInstance : MOSPInstance (Fin 30) (Fin 30) where
  requires c p := (c.val, p.val) ∈ warwickOnes

instance : DecidableRel warwickInstance.requires := fun c p =>
  inferInstanceAs (Decidable ((c.val, p.val) ∈ warwickOnes))

/-- The record's 15 contractions (`ladder.json`, pairs `(v, u)`: `v` into `u`) followed by
the 7 least-c contractions that bring the minor to minimum degree 7. -/
def warwickSeq : List (Fin 30 × Option (Fin 30)) :=
  [(0, some 17), (9, some 25), (10, some 27), (19, some 20), (23, some 15), (28, some 4),
   (15, some 13), (17, some 24), (20, some 18), (4, some 16), (7, some 5), (11, some 27),
   (13, some 21), (24, some 25), (16, some 25), (21, some 2), (8, some 14), (3, some 1),
   (5, some 14), (6, some 18), (12, some 26), (27, some 14)]

set_option maxRecDepth 100000 in
/-- The checker accepts the sequence on the instance's MOSP graph. -/
theorem warwickSeq_checked : checkSeq warwickInstance.mospGraph warwickSeq = true := by
  decide +kernel

set_option maxRecDepth 100000 in
/-- The eight survivors all have degree at least `7` in the minor. -/
theorem warwickSeq_minDegree : 7 ≤ minDegreeOfMinor warwickInstance.mospGraph warwickSeq := by
  decide +kernel

/-- `Warwick 1729` has pathwidth at least `7`. -/
theorem seven_le_pathwidth_warwick : 7 ≤ pathwidth warwickInstance.mospGraph :=
  pathwidth_ge_of_checkSeq _ warwickSeq warwickSeq_checked warwickSeq_minDegree

/-- **A record certificate implies the record's bound**: every pattern order of
`Warwick 1729` opens at least `8` stacks (the certified optimum is `9`). -/
theorem eight_le_mospValue_warwick : 8 ≤ warwickInstance.mospValue :=
  warwickInstance.mospValue_ge_of_minor_minDegree ⟨0, 18, by decide⟩ warwickSeq
    (checkSeq_sound _ warwickSeq warwickSeq_checked) _ warwickSeq_minDegree

end MOSPFormalization
