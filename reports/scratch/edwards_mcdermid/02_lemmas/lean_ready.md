### 2.6 The Lean-ready list for items 03–09

Every graph is a `SimpleGraph V` on one finite vertex type with decidable
equality and adjacency; `G − w` is `G.isolate w` (`Minor.lean`), `G − X` the
fold of `isolate` over `X : Finset V`; `supp G` is the finset of vertices of
positive degree; "`G` is reduced" (`IsSPReduced G`) is `∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v`.
Hypotheses are written as they should appear in the Lean statement; the last
column is the existing lemma or the earlier item each rests on.

**`DegreeBound/Weights.lean` (item 03)** — `g : ℕ → ℚ`, `g' n = g n − g (n − 1)`.

| name | statement | rests on |
|---|---|---|
| `g_zero, g_one, g_two, g_three` | `g 0 = g 1 = g 2 = 0`, `g 3 = 1/6` | definition |
| `g_recurrence` (W1) | `4 ≤ n → n * g n = (n − 2) * g (n − 1) + g (n − 2) + 1` | definition (well-founded recursion) |
| `g_table` | `g 4 = 1/3`, `g 5 = 13/30`, `g 6 = 23/45`, `g 7 = 359/630`, `g 8 = 1553/2520`; `g' 3 = g' 4 = 1/6`, `g' 5 = 1/10` | `norm_num` on the recurrence |
| `g_monotone` (W2, Lemma 8.3) | `Monotone g` | the coupled invariant `g (n−1) ≤ g n ≤ (1 + g (n−1))/2` by induction |
| `g'_recurrence` | `5 ≤ n → n * g' n = (n − 3) * g' (n − 1) + g' (n − 2)` | W1 twice |
| `g'_antitone_of_three_le` (W3, Lemma 8.4) | `3 ≤ m → m ≤ n → g' n ≤ g' m` | the sandwich `g' (n−1) ≥ g' n ≥ g' (n−1)/3` by induction from `g'_recurrence` |
| `one_sub_g_eq` (W4, property 6) | `4 ≤ n → 1 − g n = (n − 1) * g' n + g' (n − 1)` | W1 rearranged |
| `g_nonneg, g_lt_one, g'_nonneg, g'_le_sixth` (W5) | `0 ≤ g n`, `g n < 1`, `0 ≤ g' n`, `g' n ≤ 1/6` | W2, W3, the coupled invariant |
| `g'_le_g` | `g' n ≤ g n` | `g_nonneg` at `n − 1` (used by S0) |
| `g_closed_form` (Lemma 8.1, optional) | `2 ≤ n → g n = (7/2) A n / n! + (3/2) (−1)^n / n! − 5/2` with `A` the alternating factorial | induction; not needed downstream |

**`DegreeBound/CutLemma.lean` (item 04)** — `boundary G S := S.filter (fun v => ∃ u, u ∉ S ∧ G.Adj v u)`.

| name | statement | rests on |
|---|---|---|
| `pathwidth_le_max_add_min_boundary` (C1s) | `pathwidth G ≤ max (pathwidth (G.induce ↑S)) (pathwidth (G.induce ↑Sᶜ)) + min |∂S| |∂Sᶜ|` | `pathwidth_le_pathwidth_induce_add_card_compl` with the complement `∂S`; `pathwidth_induce_union_le_max` on `S ∖ ∂S` and `Sᶜ` (no edge between them); `pathwidth_le_of_injective` for `G[S ∖ ∂S] ≤ G[S]` |
| `pathwidth_le_cut` (C1) | `pathwidth G ≤ max (max (pathwidth G[S] + |∂S|) (pathwidth G[Sᶜ] + |∂Sᶜ|)) (|∂S| + |∂Sᶜ| − 1)` | C1s and `max a b + min c d ≤ max (a + c) (b + d)` |
| `BisectionTree G S bs k` | `BisectionTree S [] k := pathwidth G[S] ≤ k`; `BisectionTree S (b :: bs) k := ∃ S₁ S₂, S₁ ∪ S₂ = S ∧ Disjoint S₁ S₂ ∧ min |∂_{G[S]} S₁| |∂_{G[S]} S₂| ≤ b ∧ BisectionTree S₁ bs k ∧ BisectionTree S₂ bs k` | definition (`Prop` by recursion on the list) |
| `pathwidth_le_of_bisectionTree` (C2s) | `BisectionTree G univ bs k → pathwidth G ≤ k + bs.sum` | C1s by induction on `bs` (within `G[S]`; `induce_induce` or `pathwidth_eq_of_iso`) |
| `pathwidth_le_of_bisectionTree_two_mul` (C2, the item's form) | with `max |∂S₁| |∂S₂| ≤ b` in place of the min: `pathwidth G ≤ k + 2 * bs.sum` | C2s and `min ≤ max ≤ 2 max`; stated so the item's text has its lemma, but C2s is what to use |

A note the file should carry (plan §0.4 (3)): Fomin–Høie reach `n/6` with **one** level and their Lemma 4 (the boundary as the *last* bag of a degree-3 decomposition), not by iterating C2; iterating C2s with Monien–Preis cuts of `(1/6 + ε)` of each piece sums to `n/3`.

**`DegreeBound/Potential.lean` (item 05)** — `f G := ∑ v, g (G.degree v)`; `minDeg G C := (C.supp.toFinset).inf' _ (G.degree ·)` for `C : G.ConnectedComponent`; `fminus G := f G − ∑ C, g' (minDeg G C)`; `F G := f G − g' (δ G)` with `δ G` the minimum degree over `supp G` (`0` if empty).

| name | statement | rests on |
|---|---|---|
| `degree_isolate` | `(G.isolate w).degree v = if v = w then 0 else if G.Adj v w then G.degree v − 1 else G.degree v` | `Minor.lean` `isolate` |
| `f_isolate` (P1) | `f (G.isolate w) = f G − g (G.degree w) − ∑ v ∈ G.neighborFinset w, g' (G.degree v)` | `degree_isolate`, `Finset.sum` split over `{w}`, `N(w)`, the rest |
| `f_isolate_le_sub_one` (P2) | `IsSPReduced G → (∀ v, G.degree v ≤ Δ) → G.degree w = Δ → 4 ≤ Δ → (∃ v ∈ N(w), G.degree v ≤ Δ − 1) → f (G.isolate w) ≤ f G − 1` | P1, W3 (`g' (deg v) ≥ g' Δ` for `v ∈ N(w)` since `3 ≤ deg v ≤ Δ`; `g' (deg v₁) ≥ g' (Δ − 1)`), W4 |
| `f_isolate_regular` (P2, regular) | `IsSPReduced G → (∀ v ∈ supp G, G.degree v = Δ) → 4 ≤ Δ → G.degree w = Δ → f (G.isolate w) = f G − 1 + g' (Δ − 1) − g' Δ` | P1, W4 (an equality; fails at `Δ = 3`, where W4 does not hold) |
| `fminus_le_F` | `fminus G ≤ F G` | each `g' (minDeg C) ≥ 0` and one component attains `δ G` |
| `fminus_eq_F_of_connected` | `supp G` connected (one component) → `fminus G = F G` | definition |
| `fminus_eq_sum_components` (B1 additivity) | `fminus G = ∑ C, fminus (G.restrict C)` | `f` splits over components; `restrict C` has `C` as its only non-trivial component |
| `fminus_component_nonneg` | `0 ≤ fminus (G.restrict C)` | `f ≥ g (δ) ≥ g' (δ)` (`g'_le_g`) |
| `fminus_cubic` (B1) | `supp G` connected, `∀ v ∈ supp G, G.degree v = 3`, `|supp G| = N` → `fminus G = N/6 − 1/6` | `g 3 = g' 3 = 1/6` |
| `fminus_ge_five_sixths_of_not_cubic` (B1 floor, optional) | `supp G` connected, every degree `0 ∨ ≥ 3`, some degree `≥ 4` → `5/6 ≤ fminus G` | `g 4 + 4 g 3 − 1/6`; not needed by A1 (which uses only `fminus_component_nonneg`) |

**`DegreeBound/SPReduction.lean` (item 06)** — `SPStep G v H` ("one operation at `v`"): `G.degree v = 1 ∧ H = G.isolate v`, or `G.degree v = 2` with neighbours `x ≠ y` and `H = (G.isolate v) ⊔ edge x y` when `¬ G.Adj x y`, `H = G.isolate v` when `G.Adj x y`. `SPReduces := Relation.ReflTransGen (fun G H => ∃ v, SPStep G v H)`. `IsSPReduced G := ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v`. `IsBasic G := ∀ C : G.ConnectedComponent, C nontrivial → (∀ v ∈ C, G.degree v = 3) ∨ ∃ v ∈ C, SPReduces ((G.restrict C).isolate v) ⊥`.

| name | statement | rests on |
|---|---|---|
| `SPStep.edgeFinset_card_lt` (R1) | `SPStep G v H → H.edgeFinset.card < G.edgeFinset.card` | case analysis; operation 3 removes two edges and adds one |
| `exists_reduced_reduct` (R1′) | `∃ H, SPReduces G H ∧ IsSPReduced H` | well-founded induction on the edge count via R1 |
| `SPStep.degree_le` (R2) | `SPStep G v H → ∀ u, H.degree u ≤ G.degree u` | case analysis (operation 3 keeps `x, y`; `v` drops to 0) |
| `SPReduces.degree_le` (R2) | `SPReduces G H → ∀ u, H.degree u ≤ G.degree u` | `ReflTransGen` induction |
| `SPReduces.f_le` (R2) | `SPReduces G H → f H ≤ f G` | R2 and W2 |
| `SPReduces.f_sub_ge_of_isolated` (R2) | `SPReduces G H → H.degree u = 0 → g (G.degree u) ≤ f G − f H` | R2 termwise, W2, `g 0 = 0` |
| `SPStep.isolate_comm` (R3) | `SPStep G v H → w ≠ v → H.isolate w = G.isolate w ∨ SPStep (G.isolate w) v (H.isolate w)` | case analysis on `w ∈ N(v)`, on `w ∈ {x, y}`, and on the operation; `isolate` commutes with `isolate` and absorbs the added edge `xy` when `w ∈ {x, y}` |
| `SPReduces.isolate_comm` (R4, one vertex) | `SPReduces G H → w ∉ acted → SPReduces (G.isolate w) (H.isolate w)` | R3 along the sequence (`acted` = the vertices the steps act on; or the hypothesis `H.degree w ≠ 0 ∨ G.degree w = 0`, since an acted vertex ends isolated) |
| `SPReduces.isolateSet_comm` (R4) | `SPReduces G H → (∀ w ∈ X, w ∉ acted) → SPReduces (G − X) (H − X)` | induction on `X` |
| `SPStep.sup_of_disjoint` (R5, the lift) | `SPStep G v H → Disjoint (supp K) (supp G) → SPStep (G ⊔ K) v (H ⊔ K)`, hence `SPReduces G H → SPReduces (G ⊔ K) (H ⊔ K)` (a step at `v` acts inside the component of `v`; the check verifies the equivalent identity `step (G|C ⊔ G|Cᶜ) v = step (G|C) v ⊔ G|Cᶜ`) | case analysis; `x, y ∈ supp G`, so the added edge lies in `G`'s side |
| `pathwidth_le_SPStep_add_one` (R6, optional) | `SPStep G v H → pathwidth G ≤ pathwidth H + 1` | add `v` to a bag containing `N_G(v)` (`PathDecomposition.exists_bag_of_isClique`-style for the edge `xy`, or `pathwidth_le_pathwidth_erase_add_one` after `pathwidth_mono`); not what A1 needs, which is (H3) |

**`DegreeBound/Step.lean` (item 07)** — `w` is the paper's choice: `(∀ u, G.degree u ≤ G.degree w)` and `(∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u)` with `minNbrDeg G u := (G.neighborFinset u).inf' _ (G.degree ·)`.

| name | statement | rests on |
|---|---|---|
| `j_identity` (SJ, paper (2)–(4)) | `IsSPReduced G → G.degree w = Δ → 4 ≤ Δ → neighbours `v₁, …` sorted by degree → `1 + f (G.isolate w) = f G − j₁ − j₂ − j₃` | P1, W4 |
| `j4_ge` (S0, the hinge) | `SPReduces (G.isolate w) G* → IsSPReduced G* → (G.isolate w).degree v = d → 3 ≤ d → g' d ≤ f (G.isolate w) − f G* + g' (δ G*)` | R2 (`f G* ≤ f (G − w)`), W3 (`δ G* ≤ deg_{G*} v ≤ d` if `v` survives), R2 (`f (G − w) − f G* ≥ g d` if `v` is isolated), `g'_le_g` |
| `step_inequality` (S1) | `supp G` connected, `IsSPReduced G`, `G ≠ ⊥`, `¬ IsBasic G`, `w` the paper's choice, `SPReduces (G.isolate w) G*`, `IsSPReduced G*` → `1 + f G* − g' (δ G*) ≤ f G − g' (δ G)` | SJ, S0, W3, W5, the paper's four cases (regular; a surviving vertex with `3 ≤ d ≤ δ G`; `δ G = 3` with every degree-3 vertex next to `w` and `d(v_Δ) > 3`; all neighbours of degree 3 and reduced away, `G* ≠ ⊥` gives a vertex not adjacent to `w` with `d_{G−w}(v) ≥ 3`) |
| `step_inequality_fminus` (S1, per-component form) | same hypotheses → `1 + fminus G* ≤ fminus G` | S1, `fminus_le_F`, `fminus_eq_F_of_connected` |
| `nonbasic_reduct_ne_bot` | `supp G` connected, `IsSPReduced G`, `¬ IsBasic G`, `SPReduces (G.isolate w) G*` → `G* ≠ ⊥` | the definition of `IsBasic` alone: its second-kind clause is `∃ v, SPReduces (G.isolate v) ⊥` (existential over reduction sequences), so `G* = ⊥` would make `G` basic. No confluence fact is needed anywhere in the chain (§2.1) |

S1′ (every maximum-degree `w`) is **false** (§2.4) and must not be stated; item 07 picks `w` by `Finset.exists_max_image` over the maximum-degree vertices with `minNbrDeg` as the key.

**`DegreeBound/ReductionTheorem.lean` (item 08)**

| name | statement | rests on |
|---|---|---|
| `exists_reduction_set` (T1, Theorem 3.2) | `IsSPReduced G → G ≠ ⊥ → ∃ X B, X ⊆ supp G ∧ SPReduces (G − X) B ∧ B ≠ ⊥ ∧ IsSPReduced B ∧ IsBasic B ∧ (X.card : ℚ) + fminus B ≤ fminus G` | strong induction on `|supp G|`; basic: `X = ∅`; disconnected: the induction hypothesis on one component and on the rest, R5 to lift both reductions, B1 additivity; connected non-basic: `w` by the paper's choice, `exists_reduced_reduct` for `G*`, S1 (per-component form), the induction hypothesis on `G*` giving `X*, B`, R4 for `SPReduces (G − w − X*) (G* − X*)` (`X* ⊆ supp G*` is disjoint from the acted vertices), transitivity, `X = insert w X*` |

**`DegreeBound/Pathwidth.lean` (item 09)**

| name | statement | rests on |
|---|---|---|
| `CubicPathwidthBound τ` | `∀ (W) (G : SimpleGraph W), G.Connected → (∀ v, G.degree v = 3) → (pathwidth G : ℚ) ≤ |W|/6 − 1/6 + τ |W|` | named `Prop`, Fomin & Høie 2006 Theorem 5 |
| `ReductionPathwidthBound ρ` | `∀ (W) (G H : SimpleGraph W), SPReduces G H → (pathwidth G : ℚ) ≤ pathwidth H + ρ |W|` | named `Prop`, Kneis et al. 2009 |
| `pathwidth_le_pathwidth_isolateSet_add_card` | `pathwidth G ≤ pathwidth (G − X) + X.card` | `pathwidth_le_pathwidth_induce_add_card_compl` on `Xᶜ` and `pathwidth_le_of_injective` (`G[Xᶜ] → G − X`) |
| `pathwidth_eq_pathwidth_induce_supp` | `pathwidth G = pathwidth (G.induce ↑(supp G))` | `pathwidth_le_of_injective` both ways (isolated vertices go in any bag) |
| `pathwidth_le_max_components` | `(∀ C, pathwidth (G.restrict C) ≤ k) → pathwidth G ≤ k` | `pathwidth_induce_le_of_forall_connected` |
| `pathwidth_basic_le` | `CubicPathwidthBound τ → ReductionPathwidthBound ρ → Monotone τ → Monotone ρ → IsBasic B → IsSPReduced B → (pathwidth B : ℚ) ≤ fminus B + τ n + ρ n + 1` | per component: cubic by (H1) and `fminus_cubic`; second kind by `pathwidth_le_pathwidth_erase_add_one`, (H3) to `⊥`, `fminus_component_nonneg`; then the max over components and additivity |
| `pathwidth_le_potential_of_hypotheses` (A1) | … `→ IsSPReduced G → (pathwidth G : ℚ) ≤ fminus G + τ n + 2 ρ n + 1` | T1, `pathwidth_le_pathwidth_isolateSet_add_card`, (H3) for `G − X →* B`, `pathwidth_basic_le` |
| `pathwidth_le_degreeSum_of_hypotheses` (A2) | … `→ ∀ G, (pathwidth G : ℚ) ≤ ∑ v, g (H.degree v) + τ n + 3 ρ n + 1` for every reduced reduct `H` of `G`, and `≤ ∑ v, g (G.degree v) + …` | `exists_reduced_reduct`, (H3) for `G →* H`, A1, `fminus ≤ f` (W5), R2 and W2 |

`paper1/axiom_check.lean` gets a `#print axioms` line for every row; `learning/sandwich.py --stage degree_bound` pins `g` to the table and `fminus` to `learning.edwards_mcdermid.fminus` on 500 random graphs.
