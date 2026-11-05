# Statement audit: `exact_count_and_sat` (openai/math family 378, "The Exponential Time Hypothesis is False")

Audited 2026-11-05 against the read-only clone at `/home/al/dev/untrusted/openai-math`
(comparator file `lean/ComparatorChallenges/SubexponentialSAT.lean`, 220 lines; `S:` below
means that file, `Sol:` the solution tree `lean/OAI/Algorithms/SubexponentialSAT/`).
Nothing under the clone was executed. Mathlib definitions were read from our own copy
(`/home/al/dev/MOSP/lean/.lake/packages/mathlib`, rev `1192d62`) and re-read at the clone's
pinned revision `d13f23b7` (`lean/lake-manifest.json:11`) from raw.githubusercontent.com;
they agree verbatim. One Lean file of my own (`VarCheck.lean`, here) was compiled with our
toolchain to check a variable-inclusion question; one Python script (`check_encoding.py`)
computes `L` and `runtimeScale`.

## Verdict

**Not refuted.** The comparator statement means what the paper's Lean-verified form says: for
each `k ≥ 2` there is one *finite* multitape Turing machine (finite state set, 3-symbol tape
alphabet, transition table, one head move or one cell write per step) that, on the canonical
encoding of any `k`-CNF on `n` variables, halts with the exact model count in binary on a
named tape, in a number of steps at most `C (L+1)^d 2^{A·n(ln ln(n+16))²/√ln(n+16)}` with
`C, A, d` fixed after `k` and before `n, F`, where `L = Θ(k·n·m)` bits is polynomial in
`n + m` (and, since `m = O(n^k)` for a `Finset` of width-`k` clauses, polynomial in `n`
alone); every execution prefix visits at most `S (L+1)^e` cells. That is a deterministic
`2^{o(n)} · poly(n+m)` algorithm for #k-SAT in the standard sense, and it refutes ETH as
stated. I found no field, definition or quantifier through which the statement could be
kernel-true and mean something weaker. **Weaker than the paper in two honest respects**: the
verified exponent is the paper's weaker `ρ(n) = n(log log n)²/√log n` (Section 6.4), not
Theorem 1.1's `n log log n/√log n` nor the fixed-density `n/√log n`; and the exponent
`runtimeScale(n)` exceeds `n` itself for every `49 < n < e^{5504}` (ratio peaks at 2.17 near
`n ≈ 10^{23.7}`), so even with `A = 1` the verified bound is above `2^n` for all practical
`n`. The second point is a property of the asymptotics, not of the formalisation.

## 1. Is `PrimitiveMachine` finite?

Yes. `S:92-99`:

```
structure PrimitiveMachine where
  tapeCount : ℕ
  stateCount : ℕ
  inputTape : Fin tapeCount
  start : Fin stateCount
  scan : Fin stateCount → Fin tapeCount
  transition : Fin stateCount → Option Bool →
    Bool ⊕ (Fin stateCount × Turing.TM0.Stmt (Option Bool))
```

Field by field: `tapeCount`, `stateCount` are natural numbers (constants of the machine);
`inputTape`, `start` are indices; `scan` is a function on the finite set `Fin stateCount`,
i.e. a table of `stateCount` entries; `transition` is a function on
`Fin stateCount × Option Bool`, a finite domain of `3·stateCount` points, into the finite
codomain `Bool ⊕ (Fin stateCount × Stmt (Option Bool))`. `Turing.TM0.Stmt Γ` is Mathlib's
two-constructor type (`PostTuringMachine.lean:118-120`, identical at rev `d13f23b7`):
`move : Dir → Stmt`, `write : Γ → Stmt`, with `Dir = left | right` (`Tape.lean:421-424`), so
`Stmt (Option Bool)` has exactly 5 values. A Lean function on a finite domain is extensionally
a finite table whatever term defines it, so no field can carry unbounded computation: every
`step` is one lookup in a table of `3·stateCount` rows. Nothing in `Cfg` (`S:103-105`:
`state : Bool ⊕ Fin stateCount`, `tapes : Fin tapeCount → Turing.Tape (Option Bool)`) adds
state beyond tape contents; `Tape` is Mathlib's `head/left/right` with `ListBlank` halves
(`Tape.lean:408-414`), blank = `none`.

What bounds the table's size: the quantifier order in `S:194-199`. `∃ machine` (hence
`tapeCount`, `stateCount`) comes after `(k) (hk : 2 ≤ k)` and before `∀ n F`, so the table is
`O_k(1)`: fixed per `k`, no explicit function of `k` (standard for an `O_k(1)` claim). The
solution's witness is `GuardedCompiler.primitive program` with `program : BitProgram.Program
80 1220 labels` (`Sol:SqrtLogSpace/Final.lean:100,105`), 1,220 tapes and finitely many
labels. `tapeCount = 0` is excluded because `countTape : Fin machine.tapeCount` must exist.

## 2. Time and `Trace`

`S:87-90`:

```
inductive Trace {α} (step : α → Option α) : ℕ → α → α → Prop
  | refl (a : α) : Trace step 0 a a
  | cons {n} {a b c} : step a = some b → Trace step n b c → Trace step (n + 1) a c
```

`Trace step t a c` holds iff `c` is reached from `a` by exactly `t` successful applications
of `step`; `refl` reaches only `a` itself. No other constructor exists, so a trace of length
0 to a different configuration, or a non-computation, is impossible. The step relation is
`locatedStep machine = (machine.step c.config).map c.monitor` (`S:184-186`): `step`
(`S:107-119`) halts (`none`) in an `inl` state, else reads the head cell of the one tape
`scan q`, and either halts with the answer or writes one symbol or moves that one head by one
cell and updates the state; `monitor` (`S:166-182`) only updates the recorded head position
and its running min/max. So `time` is the number of primitive transitions, each of bounded
work (one 3-way read, one write or one move, on one tape). Because `step` is a function the
run is deterministic, and `S:207` requires `final.config.state = Sum.inl …`, a halting
state (`step` returns `none` there), so `final` is the unique halting configuration.

## 3. The input encoding

`S:55-79`. `encodeNat n = replicate n true ++ [false]` (unary, `n+1` bits); `frame` doubles a
bit string and appends a terminator (`2ℓ+1`); `encodeList enc` prefixes each element's frame
with `true` and ends with `[false]`; `literalCode l = 2·var + [positive] ≤ 2n−1`;
`clauseNumbers` sorts a clause's codes, `cnfNumbers` sorts the clauses; `encodeCNF F =
encodeNat n ++ encodeList (encodeList encodeNat) (cnfNumbers F)`; `formulaBitLength` is its
length. Counting: a clause of `j ≤ k` literals costs `2j(4n+1)+4` bits, so

`L = formulaBitLength F ≤ n + 2 + m(2k(4n+1) + 4) = O(k·n·m)`,

polynomial in `n + m` (the solution proves `(L+1)^d ≤ (8k+7)^d (n+|F|+1)^{2d}`,
`Sol:SqrtLogSpace/Statement.lean:9-14`). `check_encoding.py` emulates the definitions:
`n,m,k = 125,500,4` gives `L = 1,006,223 ≤ 2,006,127`; `1000,4000,3` gives `47.9M ≤ 96.0M`.
Nothing is exponential: unary `n` and unary literal codes are linear in `n`. Also `n` is part
of the input (`encodeNat n` prefix), so variables absent from every clause are known to the
machine, which matters for counting. For fixed `k` the `Finset` structure caps
`m ≤ Σ_{j≤k} C(2n, j) = O(n^k)` (2,604,376 at `n = 125, k = 3`), so the whole bound is
`2^{o(n)}` in `n` alone.

## 4. Quantifier order of the constants

`S:194-199`: `(k) (hk) : ∃ machine countTape answerTape (C A S : ℝ) (d e : ℕ), 0 < C ∧ … ∧
∀ (n : ℕ) (F : SAT.CNF (Fin n)), WidthAtMost k F → ∃ time final, …`. Machine and the five
constants are chosen after `k` and before `n` and `F`; `time` and `final` are the only
existentials inside. No constant can depend on `n` or `F`. `d > 0` and `e > 0` are required
but could be any naturals (that is `O_k(1)`). The bound at `S:210-211` is
`runtimeBound C A d (formulaBitLength F) n = C (L+1)^d 2^{A·runtimeScale n}` (`S:136-139`;
real-exponent power, positive). The theorem holds for all `n`, with no `n ≥ 20` proviso
(the paper has one; the solution's auxiliary `exact_count_eth`, `Sol:Final.lean:104-109`,
keeps `20 ≤ n`, the exported theorem does not).

## 5. `runtimeScale`

`S:132-134`: `runtimeScale n = n·(ln ln(n+16))² / √ln(n+16)`, natural logarithms (the paper
says "log denotes the natural logarithm", p. 1). The `+16` shift keeps `ln ln` defined and
positive at small `n` (`ln 16 = 2.77 > e^{…}`); for `n ≥ 20` the solution proves
`runtimeScale n ≤ 4·ρ(n)` with `ρ` in base 2 (`Sol:SqrtLogSpace/Asymptotics.lean:10,190`),
and `runtimeScale(n)/ρ(n) → 1`. So `A·runtimeScale n = O_k(ρ(n))`, the paper's Section 6.4
exponent. `(ln ln x)²/√ln x → 0`, so `2^{A·runtimeScale n} = 2^{o(n)}` for any fixed `A`:
the claim is genuinely subexponential. The honest numbers (`check_encoding.py`):
`runtimeScale(n)/n` is 0.86 at `n = 20`, crosses 1 at `n ≈ 49`, is 1.11 at 100, 1.42 at
10³, 1.85 at 10⁶, 2.10 at 10¹², peaks at 2.17 near `n = e^{e^4} ≈ 10^{23.7}`, and falls
below 1 again only at `ln(n+16) ≈ 5504`, i.e. `n ≈ e^{5504} ≈ 10^{2390}`. Thus for every
practical `n` the verified exponent is at least `n` even at `A = 1`, and `A` is an unstated
constant of the proof. That is what the theorem says; it is not a refutation.

## 6. The output and `SAT.count`

`S:17-47`: `Literal` is a variable with a sign; `Clause = Finset (Literal V)`, `CNF = Finset
(Clause V)`; `Literal.eval a l = (a l.variable == l.positive)`; `Clause.eval` is "some
literal true", `CNF.eval` "every clause true"; `satisfyingAssignments F = univ.filter (F.eval
· = true)` over `Assignment (Fin n) = Fin n → Bool` (all `2^n` assignments, `Pi` Fintype);
`count F` is its cardinality. I confirmed by `decide` in `VarCheck.lean` that `count ∅ = 4`
on `Fin 2` and `count {∅} = 0` on `Fin 1`. `WidthAtMost k F = ∀ C ∈ F, C.card ≤ k` (`S:38`).
The `Finset` choices change nothing about meaning: duplicate clauses and duplicate literals
collapse (same satisfying set), the empty clause is allowed and unsatisfiable, a tautological
clause `{x, ¬x}` is allowed and counts 2 toward the width — all consistent with the paper's
"repeating a literal permits clauses with fewer than `k` literals".

Output: `S:203-206` require `final.config.tapes countTape = Tape.mk₁ ((countWord (count F)).map
some)` and `tapes answerTape = Tape.mk₁ [some (decide (0 < count F))]`; `countWord a = if a =
0 then [false] else a.bits` (`S:147`, LSB first) with `S:208` `toNat (countWord …) = count F`
pinning the decoding (`S:5-9`) and `S:209` its length `≤ n+1`. `Tape.mk₁` (`Tape.lean:494`)
puts the head on the first bit with blank (`none`) elsewhere; tape equality is in the
`ListBlank` quotient, so only trailing blanks are identified. The halting state (`S:207`)
also carries the decision bit. The count is in binary; the input is unary-ish; both fine.

## 7. The comparator mechanism

`SubexponentialSAT.json`: `challenge_module` = the comparator file, `solution_module` =
`OAI.Algorithms.SubexponentialSAT.Main` (which imports `SqrtLogSpace.Final`, where the
theorem is proved, `Sol:Final.lean:74-102`), `theorem_names` = the one theorem,
`definition_names: []` (no definition holes), `permitted_axioms` = `propext`, `Quot.sound`,
`Classical.choice`, `enable_nanoda: false`. `lean/ComparatorChallenges/README.md` only gives
the invocation; the tool's own README (leanprover/comparator, now `lake comparator` in core
v4.35) describes the check: build challenge and solution under a `landrun` sandbox, export
both with `lean4export`, verify that **all declarations used in the statements of the named
theorems are the same in both environments** (exported declarations, not names), verify the
solution's theorem bodies use only the permitted axioms, replay the solution into the Lean
kernel. So matching is by exported content of every definition the statement depends on,
not by name. I compared the solution's definitions textually with the comparator's for every
declaration the statement uses — `PrimitiveMachine`, `Cfg`, `step`, `init`
(`Sol:Computation.lean:273-310`), `Trace` (`:20-23`), `encodeNat … formulaBitLength`
(`Sol:Encoding.lean:18,51,87,141,164,185,200-207`), `LocatedCfg … visitedSpace`
(`Sol:SqrtLogSpace/VisitedTape.lean:14-62`), `countWord` (`EncodingBounds.lean:17`),
`runtimeScale`, `runtimeBound` (`SqrtLog/StatementScale.lean:18-38`), the SAT definitions
(`Sol:SAT.lean:14-83,238-241`), `bitVal`/`toNat` (`BinaryArithmetic.lean:16-20`) — and found
them identical. One apparent difference, the position of `variable [DecidableEq V]`
(`S:27` before `Literal.eval`, `Sol:SAT.lean` after), is immaterial: Lean omits an unused
instance variable from a definition's type (`VarCheck.lean`: both `Literal.eval` and
`Clause.eval` have no `DecidableEq` argument in either variant). `enable_nanoda: false` is
the setting on 416 of the 418 challenge JSONs, so no second kernel was run for this one, as
for nearly all; the `patches/` directory touches other libraries only, none Mathlib. I could
not run the comparator (forbidden); that it passed is the repository's claim, and what this
audit establishes is that *if* it passed, the statement checked is the one analysed here.

## 8. The paper's companion claims (not audited)

Supported by the Lean statement (they need only a deterministic `poly(n+m)·2^{O_k(ρ(n))}`
#k-SAT counter): refutation of ETH, SETH, Gap-ETH, NSETH, #ETH and their bounded-error
randomised forms (Section 1.1.1, p. 4); the Set Splitting consequence (1.1.3); Corollary 1.3
(independent sets, `q`-colourings, perfect matchings in `2^{o(v)}`/`2^{o(v+e)}`) via its
counting-preserving reductions; Corollary C.1 (`E^NP ⊄ SIZE(O(n))`, needs only `2^{o(n)}`
3-SAT decision); Corollary C.2 (inversion of constant-locality maps, stated with `ρ(n)`);
Corollary 1.2 up to its unformalised randomised reduction. **Not supported** by the Lean
statement: Theorem 1.1's sharper exponents `n log log n/√log n` and, for `m ≤ Dn`,
`n/√log n`; hence Corollary 1.4's quantitative `c·n√log n` circuit bound, whose proof
(Appendix C, pp. 51-52) uses the fixed-density `2^{AV/√log V}` bound explicitly. The
reductions themselves (circuit-to-CNF, the fine-grained transfers of 1.1.3) are on paper
only. The paper's own time model is "bit operations" with a multitape simulation argument
(p. 52); the Lean model is a multitape TM, which is polynomially equivalent and sufficient.

## What this audit does not establish

- That the comparator run passed, or that the solution's 300-odd files contain no `sorry`
  or axiom beyond the permitted three: not re-run (the clone must not be executed). The
  claim rests on the repository's report and on Lean's kernel.
- The proof's mathematics (Sections 3-6, Appendix D) and the paper's sharper bounds.
- Equality of Mathlib at `d13f23b7` with ours beyond the files quoted (`Tape.lean`,
  `PostTuringMachine.lean`, fetched at that revision and identical).
- Any explicit value of `C, A, S, d, e` or of the machine's state count; the statement
  asserts existence only. The proof constructs the machine from an explicit program, so a
  value is in principle extractable, but it was not extracted here.
- Practical running time: by point 5 the verified bound exceeds `2^n` for all `n < e^{5504}`.
