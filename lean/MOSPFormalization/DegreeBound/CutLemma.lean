/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The cut lemma and its iterated form

Item 04 of loop0012 (`reports/edwards_mcdermid_plan.md` §0.4 (3), §0.5;
`reports/edwards_mcdermid.md` §2.1 (2) and §4): the one-cut transfer — a vertex
partition with its two boundaries bounds the pathwidth of the whole by the
pathwidths of the two sides — and its recursive iteration. Neither depends on
the two named hypotheses of the Edwards–McDermid formalisation
(`CubicPathwidthBound`, `ReductionPathwidthBound`, item 09); both are tools for
every graph.

* `boundaryTo G A B` — the vertices of `A` with a neighbour in `B`;
  `boundary G A` — the vertices of `A` with a neighbour outside `A`
  (`boundary_eq_boundaryTo_compl`).
* `pathwidth_induce_mono` — `T ⊆ U → pathwidth G[T] ≤ pathwidth G[U]`.
* `pathwidth_induce_le_induce_add_card_sdiff` — `pathwidth G[U] ≤ pathwidth G[T] + |U ∖ T|` for
  any two vertex sets, the relative form of `pathwidth_le_pathwidth_induce_add_card_compl`
  (`TreeBound.lean`); the brute-force check had it for `T ⊆ U` and the proof needed no
  inclusion, so the check was extended to every pair.
* `pathwidth_induce_union_le_max_add_boundaryTo` — for disjoint `S₁`, `S₂`,
  `pathwidth G[S₁ ∪ S₂] ≤ max (pathwidth G[S₁]) (pathwidth G[S₂]) + |∂(S₁ → S₂)|`:
  delete the boundary (the lemma above), the rest is a disjoint union with no edge
  between the sides (`pathwidth_induce_union_le_max`), and `G[S₁ ∖ ∂] ≤ G[S₁]`.
* **C1s** `pathwidth_induce_union_le_max_add_min` (relative) and
  `pathwidth_le_max_add_min_boundary` (global): the separator form
  `pathwidth G ≤ max (pathwidth G[S]) (pathwidth G[Sᶜ]) + min |∂S| |∂Sᶜ|`.
* **C1** `pathwidth_le_cut`: the item's three-term form
  `pathwidth G ≤ max (max (pathwidth G[S] + |∂S|) (pathwidth G[Sᶜ] + |∂Sᶜ|)) (|∂S| + |∂Sᶜ| − 1)`,
  a corollary of C1s (`max a b + min c d ≤ max (a + c) (b + d)`); stated as the
  item asks, with the `− 1` in `ℕ`.
* **C2s** `BisectionTree G S bs k` — a recursive bisection of `S` given level by level:
  `bs = []` means `pathwidth G[S] ≤ k`; `bs = b :: bs'` means `S` splits into two
  disjoint parts whose smaller boundary (`min`) has at most `b` vertices, each part
  carrying a `BisectionTree` for `bs'`. `pathwidth_le_of_bisectionTree`:
  `BisectionTree G univ bs k → pathwidth G ≤ k + bs.sum`; by induction on `bs` through
  the relative C1s, so it never needs a nested `induce`.
* **C2** `BisectionTreeMax` is the same with the larger boundary (`max`) budgeted, as the
  item's text has it; it implies `BisectionTree` (`bisectionTree_of_bisectionTreeMax`),
  and `pathwidth_le_of_bisectionTreeMax_two_mul` is the item's `pathwidth G ≤ k + 2 bs.sum`
  (the factor 2 is slack: `pathwidth_le_of_bisectionTreeMax` has `k + bs.sum`).

**What these lemmas do not give.** Fomin & Høie (2006) reach `pw ≤ (1/6 + ε) n` for
cubic graphs with **one** level — a Monien–Preis bisection with at most `(1/6 + ε/2) n`
cut edges, their Lemma 4 on each side (a path decomposition of a graph of maximum degree
3 of width at most `max{|X|, n/3 + 1} + (2/3) log₃ n + 1` whose *last* bag is a
prescribed set `X`), and a sweep across the boundary that holds the middle bags at
`|∂V₁| + 1` — not by iterating C2: iterating C2s with Monien–Preis cuts of `(1/6 + ε)`
of each piece sums to `n/3`. Lemma 4 and the sweep are stated in
`reports/edwards_mcdermid.md` §4 and are not proved here.

Every statement was checked by brute force before it was stated
(`reports/scratch/edwards_mcdermid/04_cut/check.py`): the relative forms on every
ordered pair of disjoint vertex sets of every graph to 7 vertices, the global forms on
every partition, the bisection forms on 2,000 random graphs at 10–12 vertices.
-/
import MOSPFormalization.TreeBound
import MOSPFormalization.Minor

set_option linter.unusedSectionVars false

namespace MOSPFormalization

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-! ### Boundaries -/

/-- The vertices of `A` with a neighbour in `B`. -/
def boundaryTo (A B : Finset V) : Finset V := A.filter (fun a => ∃ b ∈ B, G.Adj a b)

/-- The boundary of `A`: the vertices of `A` with a neighbour outside `A`. -/
def boundary (A : Finset V) : Finset V := A.filter (fun a => ∃ b, b ∉ A ∧ G.Adj a b)

theorem boundaryTo_subset (A B : Finset V) : boundaryTo G A B ⊆ A := Finset.filter_subset _ _

theorem boundary_subset (A : Finset V) : boundary G A ⊆ A := Finset.filter_subset _ _

theorem mem_boundaryTo {A B : Finset V} {a : V} :
    a ∈ boundaryTo G A B ↔ a ∈ A ∧ ∃ b ∈ B, G.Adj a b := Finset.mem_filter

theorem mem_boundary {A : Finset V} {a : V} :
    a ∈ boundary G A ↔ a ∈ A ∧ ∃ b, b ∉ A ∧ G.Adj a b := Finset.mem_filter

/-- The boundary of `A` is its boundary towards the complement. -/
theorem boundary_eq_boundaryTo_compl (A : Finset V) : boundary G A = boundaryTo G A Aᶜ := by
  ext a
  simp [mem_boundary, mem_boundaryTo]

/-- No edge leaves `A ∖ ∂(A → B)` for `B`. -/
theorem not_adj_of_mem_sdiff_boundaryTo {A B : Finset V} {a b : V}
    (ha : a ∈ A \ boundaryTo G A B) (hb : b ∈ B) : ¬ G.Adj a b := fun h =>
  (Finset.mem_sdiff.mp ha).2 ((mem_boundaryTo G).mpr ⟨(Finset.mem_sdiff.mp ha).1, b, hb, h⟩)

/-! ### Induced subgraphs of induced subgraphs -/

/-- Monotonicity under vertex inclusion: `T ⊆ U → pathwidth G[T] ≤ pathwidth G[U]`. -/
theorem pathwidth_induce_mono {T U : Finset V} (h : T ⊆ U) :
    pathwidth (G.induce (↑T : Set V)) ≤ pathwidth (G.induce (↑U : Set V)) :=
  pathwidth_le_of_injective (G.induceHomOfLE (Finset.coe_subset.mpr h)).toHom
    (G.induceHomOfLE (Finset.coe_subset.mpr h)).injective

/-- The pathwidth of `G` is that of `G[univ]`. -/
theorem pathwidth_induce_univ : pathwidth (G.induce (↑(Finset.univ : Finset V) : Set V)) = pathwidth G := by
  rw [Finset.coe_univ]
  exact pathwidth_eq_of_iso (SimpleGraph.induceUnivIso G)

/-- The relative deletion lemma: `pathwidth G[U] ≤ pathwidth G[T] + |U ∖ T|` for any two
vertex sets (`pathwidth_le_pathwidth_induce_add_card_compl` applied inside `G[U]` to
`U ∩ T`, which embeds in `G[T]`); no inclusion between `T` and `U` is needed. -/
theorem pathwidth_induce_le_induce_add_card_sdiff (T U : Finset V) :
    pathwidth (G.induce (↑U : Set V)) ≤ pathwidth (G.induce (↑T : Set V)) + (U \ T).card := by
  -- the vertices of `G[U]` that lie in `T`
  let S : Finset (↑(↑U : Set V)) := Finset.univ.filter (fun x => x.val ∈ T)
  have h1 := pathwidth_le_pathwidth_induce_add_card_compl (G.induce (↑U : Set V)) S
  -- `G[U][S]` embeds in `G[T]`
  have h2 : pathwidth ((G.induce (↑U : Set V)).induce (↑S : Set ↑(↑U : Set V))) ≤
      pathwidth (G.induce (↑T : Set V)) := by
    refine pathwidth_le_of_injective
      (⟨fun x => ⟨x.val.val, (Finset.mem_filter.mp (Finset.mem_coe.mp x.2)).2⟩,
        fun {x y} hxy => hxy⟩ : (G.induce (↑U : Set V)).induce (↑S : Set ↑(↑U : Set V)) →g
          G.induce (↑T : Set V)) ?_
    intro x y hxy
    have hv := congrArg Subtype.val hxy
    exact Subtype.ext (Subtype.ext hv)
  -- the complement of `S` in `G[U]` injects into `U ∖ T`
  have h3 : Sᶜ.card ≤ (U \ T).card := by
    refine Finset.card_le_card_of_injOn (fun x => x.val) ?_ Subtype.val_injective.injOn
    intro x hx
    have hx' := Finset.mem_compl.mp hx
    simp only [S, Finset.mem_filter, Finset.mem_univ, true_and] at hx'
    exact Finset.mem_sdiff.mpr ⟨Finset.mem_coe.mp x.2, hx'⟩
  omega

/-! ### C1s: the separator form of the cut lemma -/

/-- One side of the cut lemma: for disjoint `S₁`, `S₂`,
`pathwidth G[S₁ ∪ S₂] ≤ max (pathwidth G[S₁]) (pathwidth G[S₂]) + |∂(S₁ → S₂)|`. -/
theorem pathwidth_induce_union_le_max_add_boundaryTo (S₁ S₂ : Finset V) (hd : Disjoint S₁ S₂) :
    pathwidth (G.induce (↑(S₁ ∪ S₂) : Set V)) ≤
      max (pathwidth (G.induce (↑S₁ : Set V))) (pathwidth (G.induce (↑S₂ : Set V))) +
        (boundaryTo G S₁ S₂).card := by
  set B := boundaryTo G S₁ S₂ with hB
  set T := (S₁ \ B) ∪ S₂ with hT
  -- delete the boundary: at most `|B|` vertices
  have h1 := pathwidth_induce_le_induce_add_card_sdiff G T (S₁ ∪ S₂)
  have hcard : ((S₁ ∪ S₂) \ T).card ≤ B.card := by
    apply Finset.card_le_card
    intro x hx
    simp only [hT, Finset.mem_sdiff, Finset.mem_union, not_or, not_and, not_not] at hx
    rcases hx.1 with h | h
    · exact hx.2.1 h
    · exact absurd h hx.2.2
  -- the rest is a disjoint union with no edge between the sides
  have h2 : pathwidth (G.induce (↑T : Set V)) ≤
      max (pathwidth (G.induce (↑(S₁ \ B) : Set V))) (pathwidth (G.induce (↑S₂ : Set V))) :=
    pathwidth_induce_union_le_max G (S₁ \ B) S₂
      (Finset.disjoint_of_subset_left Finset.sdiff_subset hd)
      (fun a ha b hb => not_adj_of_mem_sdiff_boundaryTo G ha hb)
  have h3 : pathwidth (G.induce (↑(S₁ \ B) : Set V)) ≤ pathwidth (G.induce (↑S₁ : Set V)) :=
    pathwidth_induce_mono G Finset.sdiff_subset
  omega

/-- **C1s, relative form.** For disjoint `S₁`, `S₂`,
`pathwidth G[S₁ ∪ S₂] ≤ max (pathwidth G[S₁]) (pathwidth G[S₂]) + min |∂(S₁ → S₂)| |∂(S₂ → S₁)|`. -/
theorem pathwidth_induce_union_le_max_add_min (S₁ S₂ : Finset V) (hd : Disjoint S₁ S₂) :
    pathwidth (G.induce (↑(S₁ ∪ S₂) : Set V)) ≤
      max (pathwidth (G.induce (↑S₁ : Set V))) (pathwidth (G.induce (↑S₂ : Set V))) +
        min (boundaryTo G S₁ S₂).card (boundaryTo G S₂ S₁).card := by
  have h1 := pathwidth_induce_union_le_max_add_boundaryTo G S₁ S₂ hd
  have h2 := pathwidth_induce_union_le_max_add_boundaryTo G S₂ S₁ hd.symm
  rw [Finset.union_comm] at h2
  omega

/-- **C1s.** `pathwidth G ≤ max (pathwidth G[S]) (pathwidth G[Sᶜ]) + min |∂S| |∂Sᶜ|`. -/
theorem pathwidth_le_max_add_min_boundary (S : Finset V) :
    pathwidth G ≤
      max (pathwidth (G.induce (↑S : Set V))) (pathwidth (G.induce (↑Sᶜ : Set V))) +
        min (boundary G S).card (boundary G Sᶜ).card := by
  have h := pathwidth_induce_union_le_max_add_min G S Sᶜ disjoint_compl_right
  rw [Finset.union_compl, pathwidth_induce_univ] at h
  rw [boundary_eq_boundaryTo_compl, boundary_eq_boundaryTo_compl, compl_compl]
  exact h

/-- **C1**, the item's three-term form:
`pathwidth G ≤ max (max (pathwidth G[S] + |∂S|) (pathwidth G[Sᶜ] + |∂Sᶜ|)) (|∂S| + |∂Sᶜ| − 1)`.
The last term is never the binding one; it is kept because Fomin & Høie's
`P₁, P₂, P₃` construction has it. -/
theorem pathwidth_le_cut (S : Finset V) :
    pathwidth G ≤
      max (max (pathwidth (G.induce (↑S : Set V)) + (boundary G S).card)
               (pathwidth (G.induce (↑Sᶜ : Set V)) + (boundary G Sᶜ).card))
          ((boundary G S).card + (boundary G Sᶜ).card - 1) := by
  have h := pathwidth_le_max_add_min_boundary G S
  omega

/-! ### C2: the iterated form -/

/-- A recursive bisection of `S`, level by level: `BisectionTree G S [] k` says
`pathwidth G[S] ≤ k`; `BisectionTree G S (b :: bs) k` says `S` is the disjoint union of
two parts whose smaller boundary has at most `b` vertices, each a `BisectionTree` for
`bs`. -/
def BisectionTree : Finset V → List ℕ → ℕ → Prop
  | S, [], k => pathwidth (G.induce (↑S : Set V)) ≤ k
  | S, b :: bs, k => ∃ S₁ S₂ : Finset V, S₁ ∪ S₂ = S ∧ Disjoint S₁ S₂ ∧
      min (boundaryTo G S₁ S₂).card (boundaryTo G S₂ S₁).card ≤ b ∧
      BisectionTree S₁ bs k ∧ BisectionTree S₂ bs k

/-- The same with the larger boundary budgeted at each split (the item's C2). -/
def BisectionTreeMax : Finset V → List ℕ → ℕ → Prop
  | S, [], k => pathwidth (G.induce (↑S : Set V)) ≤ k
  | S, b :: bs, k => ∃ S₁ S₂ : Finset V, S₁ ∪ S₂ = S ∧ Disjoint S₁ S₂ ∧
      max (boundaryTo G S₁ S₂).card (boundaryTo G S₂ S₁).card ≤ b ∧
      BisectionTreeMax S₁ bs k ∧ BisectionTreeMax S₂ bs k

@[simp] theorem bisectionTree_nil (S : Finset V) (k : ℕ) :
    BisectionTree G S [] k ↔ pathwidth (G.induce (↑S : Set V)) ≤ k := Iff.rfl

theorem bisectionTree_cons (S : Finset V) (b : ℕ) (bs : List ℕ) (k : ℕ) :
    BisectionTree G S (b :: bs) k ↔ ∃ S₁ S₂ : Finset V, S₁ ∪ S₂ = S ∧ Disjoint S₁ S₂ ∧
      min (boundaryTo G S₁ S₂).card (boundaryTo G S₂ S₁).card ≤ b ∧
      BisectionTree G S₁ bs k ∧ BisectionTree G S₂ bs k := Iff.rfl

/-- **C2s, relative form.** `BisectionTree G S bs k → pathwidth G[S] ≤ k + bs.sum`. -/
theorem pathwidth_induce_le_of_bisectionTree :
    ∀ (bs : List ℕ) (S : Finset V) (k : ℕ), BisectionTree G S bs k →
      pathwidth (G.induce (↑S : Set V)) ≤ k + bs.sum
  | [], S, k, h => by simpa using h
  | b :: bs, S, k, ⟨S₁, S₂, hS, hd, hb, h₁, h₂⟩ => by
    have ih₁ := pathwidth_induce_le_of_bisectionTree bs S₁ k h₁
    have ih₂ := pathwidth_induce_le_of_bisectionTree bs S₂ k h₂
    have hc := pathwidth_induce_union_le_max_add_min G S₁ S₂ hd
    rw [hS] at hc
    simp only [List.sum_cons]
    omega

/-- **C2s.** A bisection tree of the whole vertex set with level budgets `bs` and leaf
pathwidth `k` gives `pathwidth G ≤ k + bs.sum`. -/
theorem pathwidth_le_of_bisectionTree (bs : List ℕ) (k : ℕ)
    (h : BisectionTree G Finset.univ bs k) : pathwidth G ≤ k + bs.sum := by
  have := pathwidth_induce_le_of_bisectionTree G bs Finset.univ k h
  rwa [pathwidth_induce_univ] at this

/-- Budgeting the larger boundary budgets the smaller one. -/
theorem bisectionTree_of_bisectionTreeMax :
    ∀ (bs : List ℕ) (S : Finset V) (k : ℕ), BisectionTreeMax G S bs k → BisectionTree G S bs k
  | [], _, _, h => h
  | _ :: bs, _, k, ⟨S₁, S₂, hS, hd, hb, h₁, h₂⟩ =>
    ⟨S₁, S₂, hS, hd, le_trans (min_le_max) hb,
      bisectionTree_of_bisectionTreeMax bs S₁ k h₁, bisectionTree_of_bisectionTreeMax bs S₂ k h₂⟩

/-- **C2 with the larger boundary budgeted**: still `pathwidth G ≤ k + bs.sum`. -/
theorem pathwidth_le_of_bisectionTreeMax (bs : List ℕ) (k : ℕ)
    (h : BisectionTreeMax G Finset.univ bs k) : pathwidth G ≤ k + bs.sum :=
  pathwidth_le_of_bisectionTree G bs k (bisectionTree_of_bisectionTreeMax G bs _ k h)

/-- **C2, the item's form**: `pathwidth G ≤ k + 2 bs.sum` when every level-`i` split has both
boundaries of size at most `bs[i]`. The factor 2 is slack (`pathwidth_le_of_bisectionTreeMax`). -/
theorem pathwidth_le_of_bisectionTreeMax_two_mul (bs : List ℕ) (k : ℕ)
    (h : BisectionTreeMax G Finset.univ bs k) : pathwidth G ≤ k + 2 * bs.sum := by
  have := pathwidth_le_of_bisectionTreeMax G bs k h
  omega

end MOSPFormalization
