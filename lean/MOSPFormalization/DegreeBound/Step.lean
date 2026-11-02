/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The step inequality `1 + f⁻(G*) ≤ f⁻(G)` for a connected non-basic graph

Item 07 of loop0012 (`reports/edwards_mcdermid_plan.md` §0.5; `reports/edwards_mcdermid.md`
§2.6 and §7): the heart of the proof of Theorem 3.2 of Edwards & McDermid (2015, pp. 9–12).
With `G` reduced (every degree `0` or `≥ 3`), connected on its support and not basic, `w` a
vertex of maximum degree `Δ` whose lowest-degree neighbour has the smallest possible degree
(the paper's two-key rule; the tie-break is necessary, report §2.4), `G' = G − w` and `G*`
any reduced reduct of `G'`, the inequality `1 + f⁻(G*) ≤ f⁻(G)` holds. Proved in the
global-minimum form `1 + F(G*) ≤ F(G)`, `F H = f H − g' (δ H)` (the paper's equation (1)
and (2)), from which the per-component form follows (`potentialMinus_le_F`,
`potentialMinus_eq_F_of_connected`; report §2.1 (5)).

* `minNbrDeg G u` — the smallest degree among the neighbours of `u` (`0` if none);
  `exists_paper_choice` — a `w` of maximum degree with `minNbrDeg G w ≤ minNbrDeg G u` for
  every other maximum-degree `u` (what item 08 constructs).
* `four_le_degree_of_not_isBasic` — a reduced graph with a non-basic component has
  maximum degree `≥ 4`; `supp_nonempty_of_not_isBasic`.
* `nonbasic_reduct_ne_bot` — `G* ≠ ⊥` for *every* reduct of `G − w` (from the definition of
  `IsBasic` alone: its second clause is existential over reduction sequences, so no
  confluence fact is needed; report §2.1 (6)); `exists_pos_degree_of_ne_bot`.
* **SJ** `one_add_potential_isolate`: `1 + f(G') = f(G) + (Δ − 1) g'(Δ) + g'(Δ − 1) − Σ_{v ∈ N(w)} g'(deg v)`
  (P1 with W4; the paper's (2)–(3)); `j_identity`: the paper's (4) with `j₁, j₂, j₃` for any
  two distinct neighbours `v₁ ≠ v₂` — the identity needs no sorting.
* **S0** `j4_ge` (the hinge, p. 10): `deg_{G'} v = d ≥ 3` ⇒
  `g' d ≤ f(G') − f(G*) + g'(δ(G*))` — `v` survives with degree `≤ d` (R2, W3) or is
  isolated (`potential_sub_ge_of_isolated`, `g'_le_g`).
* `sum_g'_neighbors_ge`: `Σ_{v ∈ N(w)} g'(deg v) ≥ g'(deg v₀) + (Δ − 1) g'(Δ)` for any
  neighbour `v₀` (W3); `sum_g'_neighbors_eq` when every neighbour has one degree.
* `degree_eq_of_reachable` — if no neighbour of `w` is below `Δ` then, by the tie-break, every
  vertex reachable from `w` has degree `Δ` (the paper's "`d(v₁) < Δ` unless `G` is
  `Δ`-regular", which is where the two-key rule enters).
* **S1** `one_add_F_le`: `1 + F G* ≤ F G`, by the paper's cases — regular neighbourhood
  (`δ = Δ`, `j₄ ≥ g'(Δ − 1)`); a vertex `v` with `3 ≤ deg_{G'} v ≤ δ(G)` (`j₄ ≥ g'(δ)`);
  otherwise `δ(G) = 3` with every degree-3 vertex adjacent to `w`, and either a neighbour of
  degree `≥ 4` (`j₄ ≥ g'(Δ − 1)`) or every neighbour of degree 3 (then `G* ≠ ⊥` gives a
  vertex not adjacent to `w` of degree `≥ 3` in `G'`, `j₄ ≥ g'(Δ)`).
  `one_add_potentialMinus_le` is the per-component form; `StepData` bundles the
  hypotheses and `StepData.one_add_potentialMinus_le` is the bundled statement.

Checked before stated (`reports/scratch/edwards_mcdermid/07_step/check.py`, `check.log`,
`summary.json`): every connected graph of minimum degree 3 on `≤ 9` vertices that is not
basic (82,419 graphs), every two-key `w` (133,055 pairs — item 02's S1 count), the canonical
reduct and 3 random ones (never different): `Δ ≥ 4`, `G* ≠ ⊥`, SJ (both forms), S0 on
910,385 (triple, `v`), the neighbour-sum bound on 822,729 (pair, `v₀`), the four cases with
their inequalities (315 / 125,252 / 7,478 / 10 triples), and S1 in both forms: zero
violations. S1′ (every maximum-degree `w`) is false (report §2.4) and is not stated.
-/
import MOSPFormalization.DegreeBound.SPReduction

set_option linter.unusedSectionVars false

namespace MOSPFormalization.DegreeBound

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### The lowest neighbour degree and the paper's choice of `w` -/

section Choice

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The smallest degree among the neighbours of `u` (`0` if `u` has none). -/
def minNbrDeg (u : V) : ℕ :=
  if h : (G.neighborFinset u).Nonempty then (G.neighborFinset u).inf' h (fun v => G.degree v)
  else 0

theorem minNbrDeg_le_of_adj {u v : V} (h : G.Adj u v) : minNbrDeg G u ≤ G.degree v := by
  have hv : v ∈ G.neighborFinset u := (SimpleGraph.mem_neighborFinset _ _ _).2 h
  have hne' : (G.neighborFinset u).Nonempty := ⟨v, hv⟩
  unfold minNbrDeg
  rw [dite_eq_left hne']
  exact inf'_le (fun v => G.degree v) hv

theorem le_minNbrDeg {u : V} {a : ℕ} (hne : ∃ z, G.Adj u z)
    (hall : ∀ v, G.Adj u v → a ≤ G.degree v) : a ≤ minNbrDeg G u := by
  obtain ⟨z, hz⟩ := hne
  have hne' : (G.neighborFinset u).Nonempty := ⟨z, (SimpleGraph.mem_neighborFinset _ _ _).2 hz⟩
  unfold minNbrDeg
  rw [dite_eq_left hne']
  exact (le_inf'_iff hne' _).2 (fun v hv => hall v ((SimpleGraph.mem_neighborFinset _ _ _).1 hv))

theorem exists_adj_degree_eq_minNbrDeg {u : V} (hne : ∃ z, G.Adj u z) :
    ∃ v, G.Adj u v ∧ G.degree v = minNbrDeg G u := by
  obtain ⟨z, hz⟩ := hne
  have hne' : (G.neighborFinset u).Nonempty := ⟨z, (SimpleGraph.mem_neighborFinset _ _ _).2 hz⟩
  unfold minNbrDeg
  rw [dite_eq_left hne']
  obtain ⟨v, hv, h⟩ := exists_mem_eq_inf' hne' (fun v => G.degree v)
  exact ⟨v, (SimpleGraph.mem_neighborFinset _ _ _).1 hv, h.symm⟩

/-- The paper's choice (p. 9): a vertex of maximum degree whose lowest-degree neighbour has
the smallest degree among the maximum-degree vertices. -/
theorem exists_paper_choice (hne : (supp G).Nonempty) :
    ∃ w, (∀ u, G.degree u ≤ G.degree w) ∧
      ∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u := by
  obtain ⟨v, -⟩ := hne
  obtain ⟨m, -, hm⟩ := exists_max_image univ (fun u => G.degree u) ⟨v, mem_univ v⟩
  obtain ⟨w, hwM, hw⟩ := exists_min_image (univ.filter (fun u => G.degree u = G.degree m))
    (fun u => minNbrDeg G u) ⟨m, by simp⟩
  have hwm : G.degree w = G.degree m := (mem_filter.1 hwM).2
  refine ⟨w, fun u => (hm u (mem_univ u)).trans hwm.ge, fun u hu => ?_⟩
  exact hw u (mem_filter.2 ⟨mem_univ u, hu.trans hwm⟩)

end Choice

/-! ### Non-basic graphs: the support is non-empty, the maximum degree is at least 4, and
every reduct of `G − w` is non-empty -/

section NonBasic

variable (G : SimpleGraph V) [DecidableRel G.Adj]

theorem supp_nonempty_of_not_isBasic (hnb : ¬ IsBasic G) : (supp G).Nonempty := by
  by_contra h
  apply hnb
  rintro C ⟨v, -, hv⟩
  rw [ndeg_eq_degree] at hv
  exact absurd ⟨v, mem_supp.2 hv⟩ h

theorem three_le_globalMinDeg (hG : IsSPReduced G) (hne : (supp G).Nonempty) :
    3 ≤ globalMinDeg G := by
  obtain ⟨v, hv, hd⟩ := exists_degree_eq_globalMinDeg G hne
  rw [← hd]
  rcases (isSPReduced_iff G).1 hG v with h0 | h3
  · rw [mem_supp] at hv; omega
  · exact h3

/-- A reduced graph whose maximum degree is below 4 has every non-trivial component cubic,
hence is basic. So a non-basic reduced graph has `Δ ≥ 4` (the paper's "`Δ > 3`", p. 9). -/
theorem four_le_degree_of_not_isBasic (hG : IsSPReduced G) (hnb : ¬ IsBasic G) {w : V}
    (hmax : ∀ u, G.degree u ≤ G.degree w) : 4 ≤ G.degree w := by
  by_contra hlt
  apply hnb
  rintro C ⟨v, hvC, hv⟩
  left
  intro u huC
  rw [ndeg_eq_degree] at hv ⊢
  have hr : G.Reachable u v := by
    rw [SimpleGraph.ConnectedComponent.mem_supp_iff] at huC hvC
    exact SimpleGraph.ConnectedComponent.exact (huC.trans hvC.symm)
  have hupos : 0 < G.degree u := by
    by_cases huv : u = v
    · subst huv; exact hv
    · exact pos_degree_of_reachable_of_ne G hr huv
  rcases (isSPReduced_iff G).1 hG u with h0 | h3
  · omega
  · have := hmax u; omega

/-- If some reduct of `G − w` is empty and the support of `G` is connected, `G` is basic
(its one non-trivial component is of the second kind, witnessed by `w`). -/
theorem isBasic_of_spReduces_bot (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v)
    {w : V} (hw : w ∈ supp G) (hred : SPReduces (isolate G w) ⊥) : IsBasic G := by
  rintro C ⟨v, hvC, hv⟩
  right
  rw [ndeg_eq_degree] at hv
  have hvs : v ∈ supp G := mem_supp.2 hv
  have hmem : ∀ a, a ∈ supp G → a ∈ C.supp := by
    intro a ha
    rw [SimpleGraph.ConnectedComponent.mem_supp_iff] at hvC ⊢
    rw [← hvC]
    exact SimpleGraph.ConnectedComponent.sound (hconn a ha v hvs)
  refine ⟨w, hmem w hw, ?_⟩
  have hres : restrict G C.supp = G :=
    restrict_eq_self (fun a b hab => ⟨hmem a (mem_supp_iff_exists_adj.2 ⟨b, hab⟩),
      hmem b (mem_supp_iff_exists_adj.2 ⟨a, hab.symm⟩)⟩)
  rw [hres]
  exact hred

/-- `G* ≠ ⊥` for every reduct `G*` of `G − w` when `G` is connected on its support and not
basic. No confluence fact: "not basic" is `∀ v, ¬ SPReduces ((G|C) − v) ⊥`. -/
theorem nonbasic_reduct_ne_bot (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v)
    (hnb : ¬ IsBasic G) {w : V} (hw : w ∈ supp G) {Gs : SimpleGraph V}
    (hred : SPReduces (isolate G w) Gs) : Gs ≠ ⊥ := by
  rintro rfl
  exact hnb (isBasic_of_spReduces_bot G hconn hw hred)

end NonBasic

theorem exists_pos_degree_of_ne_bot (Gs : SimpleGraph V) [DecidableRel Gs.Adj] (h : Gs ≠ ⊥) :
    ∃ u, 0 < Gs.degree u := by
  by_contra hall
  push Not at hall
  apply h
  ext a b
  simp only [SimpleGraph.bot_adj, iff_false]
  intro hab
  have := (Gs.degree_pos_iff_exists_adj a).2 ⟨b, hab⟩
  have := hall a
  omega

/-! ### The identity SJ and the hinge S0 -/

section Step

variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- **SJ** (the paper's (2)–(3)): `1 + f(G − w) = f(G) + (Δ − 1) g'(Δ) + g'(Δ − 1) − Σ_{v ∈ N(w)} g'(deg v)`
for `Δ = deg w ≥ 4` (P1 and W4). -/
theorem one_add_potential_isolate {w : V} (h4 : 4 ≤ G.degree w) :
    1 + potential (isolate G w) =
      potential G + ((G.degree w : ℚ) - 1) * g' (G.degree w) + g' (G.degree w - 1)
        - ∑ v ∈ G.neighborFinset w, g' (G.degree v) := by
  rw [potential_isolate]
  have := one_sub_g_eq h4
  linarith

/-- The paper's (4): `1 + f(G − w) = f(G) − j₁ − j₂ − j₃` with
`j₁ = g'(deg v₁) − g'(Δ − 1)`, `j₂ = g'(deg v₂) − g'(Δ)`, `j₃ = Σ_{v ∈ N(w) ∖ {v₁, v₂}} (g'(deg v) − g'(Δ))`,
for **any** two distinct neighbours `v₁ ≠ v₂` of `w` — the identity does not need the
neighbours sorted by degree. -/
theorem j_identity {w v₁ v₂ : V} (h4 : 4 ≤ G.degree w) (h₁ : G.Adj w v₁) (h₂ : G.Adj w v₂)
    (h12 : v₁ ≠ v₂) :
    1 + potential (isolate G w) =
      potential G - (g' (G.degree v₁) - g' (G.degree w - 1)) - (g' (G.degree v₂) - g' (G.degree w))
        - ∑ v ∈ ((G.neighborFinset w).erase v₁).erase v₂, (g' (G.degree v) - g' (G.degree w)) := by
  rw [one_add_potential_isolate G h4]
  have hm₁ : v₁ ∈ G.neighborFinset w := (SimpleGraph.mem_neighborFinset _ _ _).2 h₁
  have hm₂ : v₂ ∈ (G.neighborFinset w).erase v₁ :=
    mem_erase.2 ⟨h12.symm, (SimpleGraph.mem_neighborFinset _ _ _).2 h₂⟩
  rw [← add_sum_erase _ _ hm₁, ← add_sum_erase _ _ hm₂, sum_sub_distrib, sum_const, nsmul_eq_mul,
    card_erase_of_mem hm₂, card_erase_of_mem hm₁, SimpleGraph.card_neighborFinset_eq_degree]
  have hcast : ((G.degree w - 1 - 1 : ℕ) : ℚ) = (G.degree w : ℚ) - 2 := by
    rw [Nat.sub_sub, Nat.cast_sub (by omega)]; norm_num
  rw [hcast]
  ring

/-- Every neighbour's term is at least `g'(Δ)` (W3), so the neighbour sum is at least
`g'(deg v₀) + (Δ − 1) g'(Δ)` for any one neighbour `v₀` (the inside of P2's proof). -/
theorem sum_g'_neighbors_ge (hdeg : ∀ v, G.degree v = 0 ∨ 3 ≤ G.degree v) {w : V}
    (hmax : ∀ v, G.degree v ≤ G.degree w) {v₀ : V} (hv₀ : G.Adj w v₀) :
    g' (G.degree v₀) + ((G.degree w : ℚ) - 1) * g' (G.degree w)
      ≤ ∑ v ∈ G.neighborFinset w, g' (G.degree v) := by
  have hnb : ∀ v ∈ G.neighborFinset w, g' (G.degree w) ≤ g' (G.degree v) := by
    intro v hv
    rw [SimpleGraph.mem_neighborFinset] at hv
    exact g'_antitone_of_three_le (three_le_degree_of_adj G hdeg hv) (hmax v)
  have hv₀mem : v₀ ∈ G.neighborFinset w := (SimpleGraph.mem_neighborFinset _ _ _).2 hv₀
  rw [← add_sum_erase _ _ hv₀mem]
  have hcard : ((G.neighborFinset w).erase v₀).card = G.degree w - 1 := by
    rw [card_erase_of_mem hv₀mem, SimpleGraph.card_neighborFinset_eq_degree]
  have hrest := card_nsmul_le_sum ((G.neighborFinset w).erase v₀) (fun v => g' (G.degree v))
    (g' (G.degree w)) (fun v hv => hnb v (mem_of_mem_erase hv))
  rw [hcard, nsmul_eq_mul] at hrest
  have hpos : 1 ≤ G.degree w := (G.degree_pos_iff_exists_adj w).2 ⟨v₀, hv₀⟩
  have hcast : ((G.degree w - 1 : ℕ) : ℚ) = (G.degree w : ℚ) - 1 := by
    rw [Nat.cast_sub hpos, Nat.cast_one]
  rw [hcast] at hrest
  linarith

/-- When every neighbour of `w` has degree `d`, the neighbour sum is `Δ g'(d)`. -/
theorem sum_g'_neighbors_eq {w : V} {d : ℕ} (hnb : ∀ v, G.Adj w v → G.degree v = d) :
    ∑ v ∈ G.neighborFinset w, g' (G.degree v) = (G.degree w : ℚ) * g' d := by
  rw [sum_congr rfl (fun v hv => by rw [hnb v ((SimpleGraph.mem_neighborFinset _ _ _).1 hv)]),
    sum_const, SimpleGraph.card_neighborFinset_eq_degree, nsmul_eq_mul]

/-- **S0**, the hinge (p. 10): a vertex of degree `d ≥ 3` in `G' = G − w` gives
`j₄ = f(G') − f(G*) + g'(δ(G*)) ≥ g'(d)`: either it survives into `G*` with degree `≤ d`
(so `δ(G*) ≤ d` and `g'` is non-increasing from 3), or it is isolated by the reduction
(so `f(G') − f(G*) ≥ g(d) ≥ g'(d)`). The paper states it for `d ≥ 3`; the hypothesis is not
needed (for `d ≤ 2` the left side is `0 ≤ j₄`), so it is not taken. -/
theorem j4_ge {Gs : SimpleGraph V} [DecidableRel Gs.Adj] (w : V)
    (hred : SPReduces (isolate G w) Gs) (hGs : IsSPReduced Gs) {v : V} {d : ℕ}
    (hv : (isolate G w).degree v = d) :
    g' d ≤ potential (isolate G w) - potential Gs + g' (globalMinDeg Gs) := by
  have hle := hred.potential_le
  have hnn := g'_nonneg (globalMinDeg Gs)
  by_cases h0 : Gs.degree v = 0
  · have h := hred.potential_sub_ge_of_isolated h0
    rw [hv] at h
    have := g'_le_g d
    linarith
  · have hvs : v ∈ supp Gs := mem_supp.2 (Nat.pos_of_ne_zero h0)
    have h1 : globalMinDeg Gs ≤ Gs.degree v := globalMinDeg_le Gs hvs
    have h2 : Gs.degree v ≤ (isolate G w).degree v := hred.degree_le v
    have h3 : 3 ≤ globalMinDeg Gs := three_le_globalMinDeg Gs hGs ⟨v, hvs⟩
    have : g' d ≤ g' (globalMinDeg Gs) := g'_antitone_of_three_le h3 (by omega)
    linarith

/-- `j₄ ≥ 0` always (R2 and W5). -/
theorem j4_nonneg {Gs : SimpleGraph V} [DecidableRel Gs.Adj] (w : V)
    (hred : SPReduces (isolate G w) Gs) :
    0 ≤ potential (isolate G w) - potential Gs + g' (globalMinDeg Gs) := by
  have := hred.potential_le
  have := g'_nonneg (globalMinDeg Gs)
  linarith

/-- The regular case (p. 11): if no neighbour of `w` has degree below `Δ = deg w`, the
two-key rule forces every vertex reachable from `w` to have degree `Δ` — a maximum-degree
vertex `x` has `minNbrDeg G x ≥ minNbrDeg G w = Δ`, so all its neighbours have degree `Δ`,
and this propagates along any walk. This is the paper's "`d(v₁) < Δ` unless `G` is
`Δ`-regular", and the one place the tie-break is used. -/
theorem degree_eq_of_reachable {w : V} (hmax : ∀ u, G.degree u ≤ G.degree w)
    (htie : ∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u)
    (hreg : ∀ v, G.Adj w v → G.degree v = G.degree w) (hpos : 0 < G.degree w) {u : V}
    (h : G.Reachable w u) : G.degree u = G.degree w := by
  have hminw : minNbrDeg G w = G.degree w := by
    obtain ⟨z, hz⟩ := (G.degree_pos_iff_exists_adj w).1 hpos
    apply le_antisymm
    · exact (minNbrDeg_le_of_adj G hz).trans (hreg z hz).le
    · exact le_minNbrDeg G ⟨z, hz⟩ (fun v hv => (hreg v hv).ge)
  have hkey : ∀ x, G.degree x = G.degree w → ∀ y, G.Adj x y → G.degree y = G.degree w := by
    intro x hx y hxy
    apply le_antisymm (hmax y)
    calc G.degree w = minNbrDeg G w := hminw.symm
      _ ≤ minNbrDeg G x := htie x hx
      _ ≤ G.degree y := minNbrDeg_le_of_adj G hxy
  obtain ⟨p⟩ := h
  suffices hw : ∀ x y (p : G.Walk x y), G.degree x = G.degree w → G.degree y = G.degree w from
    hw w u p rfl
  intro x y p
  induction p with
  | nil => exact id
  | cons hadj _ ih => exact fun hx => ih (hkey _ hx _ hadj)

/-! ### S1, the step inequality -/

/-- **S1** in the global-minimum form (the paper's (1)): `1 + F(G*) ≤ F(G)` for `G` reduced,
connected on its support and not basic, `w` the two-key choice, `G*` any reduced reduct of
`G − w`. The four cases of pp. 11–12 are the four branches. -/
theorem one_add_F_le {Gs : SimpleGraph V} [DecidableRel Gs.Adj] {w : V}
    (hG : IsSPReduced G) (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v)
    (hnb : ¬ IsBasic G) (hmax : ∀ u, G.degree u ≤ G.degree w)
    (htie : ∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u)
    (hred : SPReduces (isolate G w) Gs) (hGs : IsSPReduced Gs) :
    1 + F Gs ≤ F G := by
  have hdeg := (isSPReduced_iff G).1 hG
  have hne : (supp G).Nonempty := supp_nonempty_of_not_isBasic G hnb
  have h4 : 4 ≤ G.degree w := four_le_degree_of_not_isBasic G hG hnb hmax
  have hwpos : 0 < G.degree w := by omega
  have hws : w ∈ supp G := mem_supp.2 hwpos
  have hSJ := one_add_potential_isolate G h4
  have hj4nn := j4_nonneg G w hred
  have hδle : globalMinDeg G ≤ G.degree w := globalMinDeg_le G hws
  have h3δ : 3 ≤ globalMinDeg G := three_le_globalMinDeg G hG hne
  unfold F
  -- it suffices: `g'(δ) + (Δ − 1) g'(Δ) + g'(Δ − 1) ≤ S + j₄`
  suffices h : g' (globalMinDeg G) + ((G.degree w : ℚ) - 1) * g' (G.degree w) + g' (G.degree w - 1)
      ≤ ∑ v ∈ G.neighborFinset w, g' (G.degree v)
        + (potential (isolate G w) - potential Gs + g' (globalMinDeg Gs)) by
    linarith
  by_cases hreg : ∀ v, G.Adj w v → G.degree v = G.degree w
  · -- the regular case: `δ = Δ`, `S = Δ g'(Δ)`, a neighbour has degree `Δ − 1 ≥ 3` in `G'`
    have hS := sum_g'_neighbors_eq G hreg
    have hδ : globalMinDeg G = G.degree w := by
      obtain ⟨v, hv, hd⟩ := exists_degree_eq_globalMinDeg G hne
      rw [← hd]
      exact degree_eq_of_reachable G hmax htie hreg hwpos (hconn w hws v hv)
    obtain ⟨v₀, hv₀⟩ := (G.degree_pos_iff_exists_adj w).1 hwpos
    have hd₀ : (isolate G w).degree v₀ = G.degree w - 1 := by
      rw [degree_isolate_of_adj G hv₀, hreg v₀ hv₀]
    have hj := j4_ge G w hred hGs hd₀
    rw [hS, hδ]
    linarith
  · push Not at hreg
    obtain ⟨v₀, hv₀, hne₀⟩ := hreg
    have hlow : G.degree v₀ ≤ G.degree w - 1 := by have := hmax v₀; omega
    have h3₀ : 3 ≤ G.degree v₀ := three_le_degree_of_adj G hdeg hv₀
    have hS₀ := sum_g'_neighbors_ge G hdeg hmax hv₀
    have hg₀ : g' (G.degree w - 1) ≤ g' (G.degree v₀) := g'_antitone_of_three_le h3₀ hlow
    by_cases hA : ∃ v, 3 ≤ (isolate G w).degree v ∧ (isolate G w).degree v ≤ globalMinDeg G
    · -- a vertex of `G'` with `3 ≤ deg ≤ δ(G)`: `j₄ ≥ g'(δ(G))`
      obtain ⟨v, hv3, hvδ⟩ := hA
      have hj := j4_ge G w hred hGs (v := v) rfl
      have : g' (globalMinDeg G) ≤ g' ((isolate G w).degree v) := g'_antitone_of_three_le hv3 hvδ
      linarith
    · push Not at hA
      -- then `δ(G) = 3` and every minimum-degree vertex is adjacent to `w`
      obtain ⟨v₁, hv₁s, hd₁⟩ := exists_degree_eq_globalMinDeg G hne
      have hδ₀ : globalMinDeg G ≤ G.degree v₀ := globalMinDeg_le G (mem_supp.2 (by omega))
      have hv₁w : v₁ ≠ w := by
        intro h; subst h; omega
      have hd' : (isolate G w).degree v₁ = G.degree v₁ - 1 ∨
          (isolate G w).degree v₁ = G.degree v₁ := by
        by_cases h : G.Adj w v₁
        · exact Or.inl (degree_isolate_of_adj G h)
        · exact Or.inr (degree_isolate_of_not_adj G hv₁w h)
      have hδ3 : globalMinDeg G = 3 := by
        by_contra hne3
        rcases hd' with h | h <;> (have := hA v₁; rw [h, hd₁] at this; omega)
      have hadj₁ : G.Adj w v₁ := by
        by_contra hna
        have := hA v₁
        rw [degree_isolate_of_not_adj G hv₁w hna, hd₁, hδ3] at this
        omega
      rw [hδ3]
      by_cases hB : ∃ v, G.Adj w v ∧ 4 ≤ G.degree v
      · -- a neighbour of degree `≥ 4`: it has degree in `[3, Δ − 1]` in `G'`, `j₄ ≥ g'(Δ − 1)`
        obtain ⟨v, hv, hv4⟩ := hB
        have hdv : (isolate G w).degree v = G.degree v - 1 := degree_isolate_of_adj G hv
        have hj := j4_ge G w hred hGs hdv
        have hg : g' (G.degree w - 1) ≤ g' (G.degree v - 1) :=
          g'_antitone_of_three_le (by omega) (by have := hmax v; omega)
        have hS₁ := sum_g'_neighbors_ge G hdeg hmax hadj₁
        rw [hd₁, hδ3] at hS₁
        linarith
      · -- every neighbour has degree 3: `S = Δ g'(3)`; `G* ≠ ⊥` gives `u` off `N[w]` with
        -- `deg_{G'} u = deg_G u ∈ [3, Δ]`, so `j₄ ≥ g'(Δ)`
        push Not at hB
        have hall3 : ∀ v, G.Adj w v → G.degree v = 3 := fun v hv => by
          have := hB v hv; have := three_le_degree_of_adj G hdeg hv; omega
        have hS := sum_g'_neighbors_eq G hall3
        obtain ⟨u, hu⟩ := exists_pos_degree_of_ne_bot Gs (nonbasic_reduct_ne_bot G hconn hnb hws hred)
        have hu3 : 3 ≤ Gs.degree u := by
          rcases (isSPReduced_iff Gs).1 hGs u with h0 | h3
          · omega
          · exact h3
        have hule : Gs.degree u ≤ (isolate G w).degree u := hred.degree_le u
        have huw : ¬ G.Adj w u := by
          intro h
          have := hall3 u h
          have := degree_isolate_of_adj G h
          omega
        have huw' : u ≠ w := by
          intro h; subst h
          rw [degree_isolate_self] at hule
          omega
        have hdu : (isolate G w).degree u = G.degree u := degree_isolate_of_not_adj G huw' huw
        have hj := j4_ge G w hred hGs hdu
        have hgu : g' (G.degree w) ≤ g' (G.degree u) := g'_antitone_of_three_le (by omega) (hmax u)
        have hg3 : g' (G.degree w - 1) ≤ g' 3 := g'_antitone_of_three_le le_rfl (by omega)
        have hgΔ : g' (G.degree w) ≤ g' 3 := g'_antitone_of_three_le le_rfl (by omega)
        have hΔ2 : (2 : ℚ) ≤ (G.degree w : ℚ) := by exact_mod_cast (show 2 ≤ G.degree w by omega)
        have hprod : 0 ≤ ((G.degree w : ℚ) - 2) * (g' 3 - g' (G.degree w)) :=
          mul_nonneg (by linarith) (by linarith)
        rw [hS]
        nlinarith [hprod]

/-- **S1** in the per-component form: `1 + f⁻(G*) ≤ f⁻(G)` (`f⁻ ≤ F` always, `f⁻ = F` on a
connected support). -/
theorem one_add_potentialMinus_le {Gs : SimpleGraph V} [DecidableRel Gs.Adj] {w : V}
    (hG : IsSPReduced G) (hconn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v)
    (hnb : ¬ IsBasic G) (hmax : ∀ u, G.degree u ≤ G.degree w)
    (htie : ∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u)
    (hred : SPReduces (isolate G w) Gs) (hGs : IsSPReduced Gs) :
    1 + potentialMinus Gs ≤ potentialMinus G := by
  have h := one_add_F_le G hG hconn hnb hmax htie hred hGs
  have h1 := potentialMinus_le_F Gs
  rw [potentialMinus_eq_F_of_connected G (supp_nonempty_of_not_isBasic G hnb) hconn]
  linarith

end Step

/-! ### The hypotheses, bundled -/

/-- The data of one step of Theorem 3.2 (p. 9): a reduced graph `G`, connected on its
support and not basic; `w` the two-key choice; `Gs` a reduced reduct of `G − w`. -/
structure StepData (V : Type*) [Fintype V] [DecidableEq V] where
  /-- the graph -/
  G : SimpleGraph V
  [instG : DecidableRel G.Adj]
  /-- a reduced reduct of `G − w` -/
  Gs : SimpleGraph V
  [instGs : DecidableRel Gs.Adj]
  /-- the deleted vertex -/
  w : V
  reduced : IsSPReduced G
  conn : ∀ u ∈ supp G, ∀ v ∈ supp G, G.Reachable u v
  notBasic : ¬ IsBasic G
  maxDeg : ∀ u, G.degree u ≤ G.degree w
  tieBreak : ∀ u, G.degree u = G.degree w → minNbrDeg G w ≤ minNbrDeg G u
  reduces : SPReduces (isolate G w) Gs
  reducedGs : IsSPReduced Gs

attribute [instance] StepData.instG StepData.instGs

namespace StepData

variable (d : StepData V)

theorem one_add_F_le : 1 + F d.Gs ≤ F d.G :=
  DegreeBound.one_add_F_le d.G d.reduced d.conn d.notBasic d.maxDeg d.tieBreak d.reduces
    d.reducedGs

theorem one_add_potentialMinus_le : 1 + potentialMinus d.Gs ≤ potentialMinus d.G :=
  DegreeBound.one_add_potentialMinus_le d.G d.reduced d.conn d.notBasic d.maxDeg d.tieBreak
    d.reduces d.reducedGs

end StepData

end MOSPFormalization.DegreeBound
