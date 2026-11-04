/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The formal frame of loop0014: `SubexpCount`, `PathwidthSubexp`, `PathwidthSubexpOn`

Item 02 of `reports/subexp_pathwidth_plan.md` (§0.4.1, §0.5); `reports/subexp_pathwidth.md` §2.
Everything the loop proves about a subexponential exact algorithm for pathwidth is stated
against the three `Prop`s of this file:

* `SubexpCount k` — the comparator statement `exact_count_and_sat k` of OpenAI's family 378
  (*The Exponential Time Hypothesis is False*, 2026-10-25), **restated as a `def` of a `Prop`,
  never proved and never an axiom**: one fixed primitive multi-tape machine exactly counts the
  satisfying assignments of every CNF of width `≤ k` on `n` variables, in the collection's
  canonical encoding of bit length `L`, in time `≤ C (L + 1)^d · 2^(A · ρ(n))` with
  `ρ(n) = n (log log(n + 16))² / √log(n + 16)`, visiting at most `S (L + 1)^e` tape cells at
  every step. The body is the comparator's statement character for character (the binder
  `hk : 2 ≤ k` becomes the hypothesis of `ExactCountAndSat`); the machine model, the encoding
  and `runtimeBound` are the verbatim copy in `PrimitiveMachine.lean`. This is the *verified*
  exponent, the weaker one (`reports/subexp_pathwidth.md` §1.0): the paper's
  `n log log n / √log n` and `n / √log n` are not in the Lean library and are not restated.
* `PathwidthSubexpOn C` — "some primitive machine decides `pathwidth G ≤ k` for every graph
  `G` in the class `C` and every `k`, in time `2^{o(n)} · poly(L)`": a machine, constants
  `c > 0`, `d`, and an exponent `f = o(n)` (`Asymptotics.IsLittleO`, so `2^(f n)` is
  `2^{o(n)}` in the number of vertices), such that on the canonical input `encodeGraph G k`
  (`n` and `k` in the collection's unary code, then the `n²` adjacency bits) the machine halts
  in the answer state `decide (pathwidth G ≤ k)` within `c (L + 1)^d 2^(f n)` steps. A class is
  `GraphClass := ∀ n, SimpleGraph (Fin n) → Prop` (the item's `SimpleGraph → Prop` is not a
  type; nothing requires the class to be closed under isomorphism).
* `PathwidthSubexp` — the same over every graph.

The parameter is the number of vertices `n`, never the input length (`TASK.md`: on dense
graphs `L = Θ(n²)`), which is why `f` is `o(n)` and the polynomial factor is in `L`.

The machine model is the one the counting theorem is stated in, so a transfer theorem
`SubexpCount k → PathwidthSubexpOn C` (item 09, if any) is a statement about one machine
model and needs no translation between models; the price, recorded in the report, is that
such a theorem needs a composition fact about primitive machines (a polynomial-time encoder
followed by the counting machine), which the comparator does not state and which would be
carried as a further named `Prop`. An abstract notion ("a function with a time function")
was rejected because without a cost model `∃ f, ∃ T, …` is provable outright and the
hypothesis would be vacuous.

Proved here:

* `SubexpCount.anti`: `SubexpCount k → k' ≤ k → SubexpCount k'` (a width-`≤ k'` formula has
  width `≤ k`; the same machine and constants).
* `PathwidthSubexpOn.mono`: a machine for a class is a machine for every subclass.
* `pathwidthSubexp_iff`: `PathwidthSubexp ↔ PathwidthSubexpOn (fun _ _ => True)`.
* `pathwidthSubexpOn_iff_vertexSeparation`: the same `Prop` with `vertexSeparation` in place
  of `pathwidth` (Kinnersley, `vertexSeparation_eq_pathwidth`), for item 08, whose statements
  are against `VertexSeparation.lean`.
* `Trace.config_of_locatedStep`: a trace of the located (space-monitoring) step projects to a
  trace of the plain step, so the time bound of `SubexpCount` is a bound on `machine.step`.
* `runtimeScale_isLittleO`, `isSubexpExponent_runtimeScale`: the verified exponent
  `A · ρ(n)` is `o(n)`, so `runtimeBound C A d L n` is of the form `PathwidthSubexpOn` asks
  for (`runtimeBound_eq`). The analytic content is `(log y)² / √y → 0`.

Every statement here is a definition or a trivial lemma; nothing was brute-force checked
because nothing is a reduction or an encoding of pathwidth (TASK.md's check applies to those;
`encodeGraph_length` is the one computation, proved). What this file does **not** claim:
that `SubexpCount k` holds for any `k`; that any `PathwidthSubexpOn C` holds; that the
`PrimitiveMachine` model is robust (polynomially equivalent to any other); or that the
theorem of the paper beyond the comparator statement is restated.
-/
import MOSPFormalization.SubexpPathwidth.PrimitiveMachine
import MOSPFormalization.VSEquivPW

set_option linter.unusedSectionVars false

namespace MOSPFormalization.SubexpPathwidth

open OAI.Algorithms.SubexponentialSAT
open OAI.Algorithms.SubexponentialSAT.Computation
open OAI.Algorithms.SubexponentialSAT.SqrtLogSpace
open OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement
open Asymptotics Filter

/-! ### The hypothesis: the comparator statement as a `Prop` -/

/-- **The counting hypothesis, for width `k`**: the body of `exact_count_and_sat k` in
`lean/ComparatorChallenges/SubexponentialSAT.lean` of the OpenAI collection, character for
character. Never proved here, never an axiom. -/
def SubexpCount (k : ℕ) : Prop :=
  ∃ (machine : Computation.PrimitiveMachine)
    (countTape answerTape : Fin machine.tapeCount)
    (C A S : ℝ) (d e : ℕ),
    0 < C ∧ 0 < A ∧ 0 < S ∧ 0 < d ∧ 0 < e ∧
    ∀ (n : ℕ) (F : SAT.CNF (Fin n)), SAT.WidthAtMost k F →
      ∃ (time : ℕ) (final : LocatedCfg machine),
        Computation.Trace (locatedStep machine) time
          (locatedInit machine (Encoding.encodeCNF F)) final ∧
        final.config.tapes countTape =
          Turing.Tape.mk₁ ((countWord (SAT.count F)).map some) ∧
        final.config.tapes answerTape =
          Turing.Tape.mk₁ [some (decide (0 < SAT.count F))] ∧
        final.config.state = Sum.inl (decide (0 < SAT.count F)) ∧
        BinaryArithmetic.toNat (countWord (SAT.count F)) = SAT.count F ∧
        (countWord (SAT.count F)).length ≤ n + 1 ∧
        (time : ℝ) ≤ OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement.runtimeBound C A d
          (Encoding.formulaBitLength F) n ∧
        ∀ (prefixSteps : ℕ) (intermediate : LocatedCfg machine),
          prefixSteps ≤ time →
          Computation.Trace (locatedStep machine) prefixSteps
            (locatedInit machine (Encoding.encodeCNF F)) intermediate →
          (visitedSpace intermediate : ℝ) ≤
            S * ((Encoding.formulaBitLength F : ℝ) + 1) ^ e

/-- The comparator theorem in full: `SubexpCount k` for every `k ≥ 2`. A `Prop`, not asserted. -/
def ExactCountAndSat : Prop := ∀ k : ℕ, 2 ≤ k → SubexpCount k

/-- A machine for width `k` is a machine for every smaller width: `WidthAtMost k' F → WidthAtMost k F`. -/
theorem SubexpCount.anti {k k' : ℕ} (h : SubexpCount k) (hk : k' ≤ k) : SubexpCount k' := by
  obtain ⟨machine, countTape, answerTape, C, A, S, d, e, hC, hA, hS, hd, he, hmain⟩ := h
  refine ⟨machine, countTape, answerTape, C, A, S, d, e, hC, hA, hS, hd, he, ?_⟩
  intro n F hF
  exact hmain n F (fun c hc => le_trans (hF c hc) hk)

theorem ExactCountAndSat.subexpCount (h : ExactCountAndSat) {k : ℕ} (hk : 2 ≤ k) :
    SubexpCount k := h k hk

/-! ### The runtime bound is `2^{o(n)} · poly(L)` -/

/-- An exponent `f` with `2^(f n) = 2^{o(n)}`: `f = o(n)` as `n → ∞`. -/
def IsSubexpExponent (f : ℕ → ℝ) : Prop := f =o[atTop] (fun n : ℕ => (n : ℝ))

/-- `runtimeBound C A d L n = C (L + 1)^d 2^(A · runtimeScale n)`, by definition. -/
theorem runtimeBound_eq (C A : ℝ) (d L n : ℕ) :
    runtimeBound C A d L n = C * ((L : ℝ) + 1) ^ d * (2 : ℝ) ^ (A * runtimeScale n) := rfl

/-- `(log y)² / √y → 0` as `y → ∞`. -/
theorem tendsto_log_sq_div_sqrt :
    Tendsto (fun y : ℝ => (Real.log y) ^ 2 / Real.sqrt y) atTop (nhds 0) := by
  have h := isLittleO_log_rpow_rpow_atTop (2 : ℝ) (by norm_num : (0 : ℝ) < 1 / 2)
  have h' : (fun y : ℝ => (Real.log y) ^ 2) =o[atTop] (fun y : ℝ => Real.sqrt y) := by
    refine h.congr' ?_ ?_
    · filter_upwards with y
      exact Real.rpow_two _
    · filter_upwards [eventually_ge_atTop (0 : ℝ)] with y hy
      rw [Real.sqrt_eq_rpow]
  exact h'.tendsto_div_nhds_zero

/-- The verified runtime scale `ρ(n) = n (log log(n + 16))² / √log(n + 16)` is `o(n)`. -/
theorem runtimeScale_isLittleO :
    (fun n : ℕ => runtimeScale n) =o[atTop] (fun n : ℕ => (n : ℝ)) := by
  have hlog : Tendsto (fun n : ℕ => Real.log ((n : ℝ) + 16)) atTop atTop :=
    Real.tendsto_log_atTop.comp (tendsto_atTop_add_const_right _ _ tendsto_natCast_atTop_atTop)
  have hq : Tendsto (fun n : ℕ => (Real.log (Real.log ((n : ℝ) + 16))) ^ 2 /
      Real.sqrt (Real.log ((n : ℝ) + 16))) atTop (nhds 0) :=
    tendsto_log_sq_div_sqrt.comp hlog
  have h1 : (fun n : ℕ => (Real.log (Real.log ((n : ℝ) + 16))) ^ 2 /
      Real.sqrt (Real.log ((n : ℝ) + 16))) =o[atTop] (fun _ : ℕ => (1 : ℝ)) :=
    (isLittleO_one_iff ℝ).mpr hq
  have h2 := h1.mul_isBigO (isBigO_refl (fun n : ℕ => (n : ℝ)) atTop)
  refine h2.congr' ?_ ?_
  · filter_upwards with n
    simp only [runtimeScale]
    ring
  · filter_upwards with n
    simp

/-- The verified exponent `A · ρ(n)` is a subexponential exponent, for every `A`. -/
theorem isSubexpExponent_runtimeScale (A : ℝ) :
    IsSubexpExponent (fun n : ℕ => A * runtimeScale n) :=
  (runtimeScale_isLittleO.const_mul_left A)

/-! ### Traces of the located step project to traces of the plain step -/

theorem LocatedCfg.monitor_config {machine : PrimitiveMachine} (c : LocatedCfg machine)
    (x : machine.Cfg) : (c.monitor x).config = x := by
  unfold LocatedCfg.monitor
  rcases hs : c.config.state with b | q
  · rfl
  · simp only [Sum.elim_inr]
    rcases machine.transition q (c.config.tapes (machine.scan q)).head with b' | ⟨q', a⟩
    · rfl
    · rfl

/-- A trace of the located step is a trace of the plain step on the configurations. -/
theorem Trace.config_of_locatedStep {machine : PrimitiveMachine} {t : ℕ}
    {c c' : LocatedCfg machine} (h : Trace (locatedStep machine) t c c') :
    Trace machine.step t c.config c'.config := by
  induction h with
  | refl a => exact Trace.refl _
  | cons hs _ ih =>
    rename_i a b c''
    simp only [locatedStep, Option.map_eq_some_iff] at hs
    obtain ⟨x, hx, rfl⟩ := hs
    rw [LocatedCfg.monitor_config] at ih
    exact Trace.cons hx ih

/-! ### The canonical input of a pathwidth decision instance -/

/-- The canonical input of the instance `(G, k)`, `G` a graph on `Fin n`: `n` in the
collection's unary code (`encodeNat`), then `k`, then the `n²` adjacency bits row by row. -/
noncomputable def encodeGraph {n : ℕ} (G : SimpleGraph (Fin n)) (k : ℕ) : List Bool :=
  open Classical in
  Encoding.encodeNat n ++ Encoding.encodeNat k ++
    (List.finRange n).flatMap (fun i => (List.finRange n).map (fun j => decide (G.Adj i j)))

theorem encodeGraph_length {n : ℕ} (G : SimpleGraph (Fin n)) (k : ℕ) :
    (encodeGraph G k).length = (n + 1) + (k + 1) + n * n := by
  simp [encodeGraph, Encoding.encodeNat, List.length_flatMap, List.map_const']
  ring

/-! ### The subexponential-pathwidth predicates -/

/-- A class of graphs, one predicate per vertex count. -/
abbrev GraphClass := ∀ n : ℕ, SimpleGraph (Fin n) → Prop

/-- `PathwidthSubexpOn C`: some primitive machine decides `pathwidth G ≤ k` for every `G` in
the class `C` and every `k`, on the canonical input, in time `c (L + 1)^d 2^(f n)` with
`f = o(n)` in the number of vertices `n`. -/
def PathwidthSubexpOn (C : GraphClass) : Prop :=
  ∃ (machine : PrimitiveMachine) (c : ℝ) (d : ℕ) (f : ℕ → ℝ),
    0 < c ∧ IsSubexpExponent f ∧
    ∀ (n : ℕ) (G : SimpleGraph (Fin n)) (k : ℕ), C n G →
      ∃ (time : ℕ) (final : machine.Cfg),
        Trace machine.step time (machine.init (encodeGraph G k)) final ∧
        final.state = Sum.inl (@decide (pathwidth G ≤ k) (Classical.propDecidable _)) ∧
        (time : ℝ) ≤ c * (((encodeGraph G k).length : ℝ) + 1) ^ d * (2 : ℝ) ^ (f n)

/-- `PathwidthSubexp`: the same over every graph. -/
def PathwidthSubexp : Prop :=
  ∃ (machine : PrimitiveMachine) (c : ℝ) (d : ℕ) (f : ℕ → ℝ),
    0 < c ∧ IsSubexpExponent f ∧
    ∀ (n : ℕ) (G : SimpleGraph (Fin n)) (k : ℕ),
      ∃ (time : ℕ) (final : machine.Cfg),
        Trace machine.step time (machine.init (encodeGraph G k)) final ∧
        final.state = Sum.inl (@decide (pathwidth G ≤ k) (Classical.propDecidable _)) ∧
        (time : ℝ) ≤ c * (((encodeGraph G k).length : ℝ) + 1) ^ d * (2 : ℝ) ^ (f n)

/-- Monotonicity in the class: a machine for `C` is a machine for every `C' ⊆ C`. -/
theorem PathwidthSubexpOn.mono {C C' : GraphClass} (h : PathwidthSubexpOn C)
    (hsub : ∀ n G, C' n G → C n G) : PathwidthSubexpOn C' := by
  obtain ⟨machine, c, d, f, hc, hf, hmain⟩ := h
  exact ⟨machine, c, d, f, hc, hf, fun n G k hG => hmain n G k (hsub n G hG)⟩

/-- `PathwidthSubexp` is the class-restricted notion on the class of all graphs. -/
theorem pathwidthSubexp_iff : PathwidthSubexp ↔ PathwidthSubexpOn (fun _ _ => True) := by
  constructor
  · rintro ⟨machine, c, d, f, hc, hf, hmain⟩
    exact ⟨machine, c, d, f, hc, hf, fun n G k _ => hmain n G k⟩
  · rintro ⟨machine, c, d, f, hc, hf, hmain⟩
    exact ⟨machine, c, d, f, hc, hf, fun n G k => hmain n G k trivial⟩

open Classical in
/-- The decision bit is the same for vertex separation (Kinnersley). -/
theorem decide_pathwidth_le_eq {n : ℕ} (G : SimpleGraph (Fin n)) (k : ℕ) :
    @decide (pathwidth G ≤ k) (Classical.propDecidable _) =
      @decide (vertexSeparation G ≤ k) (Classical.propDecidable _) :=
  decide_eq_decide.mpr (by rw [vertexSeparation_eq_pathwidth])

open Classical in
/-- `PathwidthSubexpOn C`, stated with `vertexSeparation` in place of `pathwidth`, for the
statements of item 08 that are made against `VertexSeparation.lean`. -/
theorem pathwidthSubexpOn_iff_vertexSeparation (C : GraphClass) :
    PathwidthSubexpOn C ↔
    ∃ (machine : PrimitiveMachine) (c : ℝ) (d : ℕ) (f : ℕ → ℝ),
      0 < c ∧ IsSubexpExponent f ∧
      ∀ (n : ℕ) (G : SimpleGraph (Fin n)) (k : ℕ), C n G →
        ∃ (time : ℕ) (final : machine.Cfg),
          Trace machine.step time (machine.init (encodeGraph G k)) final ∧
          final.state = Sum.inl (@decide (vertexSeparation G ≤ k) (Classical.propDecidable _)) ∧
          (time : ℝ) ≤ c * (((encodeGraph G k).length : ℝ) + 1) ^ d * (2 : ℝ) ^ (f n) := by
  simp only [PathwidthSubexpOn, decide_pathwidth_le_eq]

end MOSPFormalization.SubexpPathwidth
