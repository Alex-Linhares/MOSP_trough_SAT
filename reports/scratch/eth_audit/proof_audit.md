# Audit of the PROOF of `exact_count_and_sat` (openai/math family 378)

> **Superseded counts (paper 3, item 11, 2026-11-05).** This is a dated scratch record written before Ralph loop0015 and is left as written. Four counts below have since been corrected by the paper (`paper3/ETH_AMBIGUOUS.MD` 04a, 04b, 04d, 04e; paper 3 Section 4, `paper3/scripts/proof_inspection.py`): the statement match is **35 definitions compared, 33 identical, 2 identical up to `noncomputable def` / `noncomputable section`**, not "all 33"; the comparator theorem's statement starts at challenge line **194** (= `Final.lean` 74), not 181; the manifest has **42** packages, not 41; `#print axioms` sits in **8 closure files / 19 commands** (17 files / 35 commands over the family directory, 9 of them never built), and `enable_nanoda: false` is on **413** of 418 JSONs, not 416. The replay (paper 3 Section 5) has since moved the "no build, no recorded axioms, no second kernel" items of the verdict's trust boundary; the comparator run itself remains unreproduced. Everything else here stands.


Scope: the Lean proof of `OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat`
in the read-only clone `/home/al/dev/untrusted/openai-math` (all paths below are relative
to its `lean/` directory). Method: inspection only — `grep`/`sed`/`python3 -I` over the
sources, and two web lookups (the Mathlib commit page, the comparator README). Nothing in
the clone was built, run, imported or evaluated. The companion audit of the STATEMENT is
not duplicated: the comparator statement is taken as written. Scripts:
`closure.py` (import closure, nested-comment stripper, keyword grep; outputs
`closure_modules.json`, `hits.json`) and `defdiff.py` (definition diff), both in this directory.

## Verdict

**No unsoundness found by inspection.** The import closure of the solution (3,091 files,
550,551 lines, all under `OAI/Algorithms/SubexponentialSAT/`) contains, with comments
stripped, zero `axiom`, `sorry`, `admit`, `native_decide`, `ofReduceBool`/`ofReduceNat`,
`implemented_by`, `extern`, `unsafe` or `partial`; its only `set_option`s are two
`quotPrecheck false`; its nine `opaque`s all carry bodies; the toolchain is stock
`v4.34.1` with upstream Mathlib `d13f23b7` (unpatched); the solution theorem's statement is
character-for-character the comparator's after whitespace normalisation, and the 33
definitions it rests on are textually identical in the library and the challenge file. The
final theorem is stated purely over the comparator's own `PrimitiveMachine.step`, so no
internal cost model of the BitProgram compiler can leak into it. The strongest *weakness*
is evidential, not logical: **the repository contains no recorded `#print axioms` output,
no CI that builds the Lean, and `enable_nanoda: false`**, so the claim that this closure
type-checks with only the three permitted axioms rests on OpenAI's unpublished build and
on the Lean 4.34.1 kernel, and nobody outside has replayed it. The proof's trust therefore
rests on: the Lean kernel of `v4.34.1`, Mathlib revision `d13f23b7`, the comparator run
not being reproduced here, and the absence of nanoda replay for this family.

## 1. Inventory

Closure of `OAI/Algorithms/SubexponentialSAT/Main.lean` (which is a 16-line aggregator
importing `SqrtLog/ExecutionNativeFinal` and `SqrtLogSpace/Final`): **3,091 modules
resolved inside `lean/`, all with prefix `OAI.Algorithms.SubexponentialSAT`; 0 modules
elsewhere under `OAI/`**. The closure stops at **50 distinct `Mathlib.*` modules and one
core module, `Lean.Elab.Tactic.Omega`** (imported by `SqrtLogSpace/FiniteFallback.lean:14`
and `SqrtLogSpace/DisjointReuse/SparseCharging.lean:5`; a tactic module, and the closure
has no `elab`/`macro`/`syntax` declarations). Total **550,551 raw lines**. The directory
holds 3,977 `.lean` files, so **886 are not in the closure**; they are not reachable from
`OAI.lean` either (its only SubexponentialSAT import is `Main`, `OAI.lean:49`), hence are
never built by the default target — dead code, not a hole; a raw grep finds no
`sorry`/`axiom`/`native_decide` in them either.

Twenty largest files (lines): `SqrtLogSpace/DisjointReuse/SparsePriorityProgram` 2,873;
`SqrtLog/MomentsAssemblyProgram` 2,502; `SqrtLog/LeafRingSetupProgramNative` 2,019;
`SqrtLog/LeafParametersProgramNative` 1,953; `SqrtLogSpace/SignatureTupleRefinement`
1,800; `SubexpSymbolicCost` 1,622; `SqrtLogSpace/SparseCodeProgram` 1,580;
`SqrtLogSpace/SignatureTupleComplete` 1,385; `SqrtLogSpace/HashGreedyProgram` 1,298;
`SqrtLogSpace/HighQueryAdapter` 1,256; `SqrtLogSpace/CodeCandidateProgram` 1,235;
`SqrtLogSpace/SignatureHeadLoaderCore` 1,233; `SqrtLogSpace/FactorTableProgram` 1,218;
`SqrtLogSpace/FactorTableNative` 1,217; `ExecClauseCost` 1,212; `ExecSparsifyWorklist`
1,167; `SqrtLogSpace/SignatureTupleLoader` 1,150; `SqrtLogSpace/SignatureTupleProgram`
1,148; `SqrtLog/LayoutBinomialProgramCell` 1,114; `SubexpKernelControl` 1,096.

## 2. Keyword sweep (comments stripped, nested `/- -/` handled; line counts)

| keyword | count | assessment |
|---|---|---|
| `axiom`, `sorry`, `sorryAx`, `admit` | 0, 0, 0, 0 | — |
| `native_decide`, `ofReduceBool`, `ofReduceNat` | 0, 0, 0 | no compiler trust |
| `implemented_by`, `extern`, `unsafe`, `partial` | 0, 0, 0, 0 | — |
| `opaque` | 9 | all have `:=` bodies (see below) |
| `noncomputable` | 1,048 | classical existence; irrelevant to kernel soundness |
| `set_option` | 2 | both `quotPrecheck false` (`SqrtLog/LeafProgramPreparedRecoveryQuery.lean:15`, `…RecoveryWitness.lean:14`): disables a notation precheck for `local notation`; harmless |
| `maxHeartbeats`, `maxRecDepth`, `autoImplicit`, `skipKernelTC`, `bootstrap.*`, `trust` | 0 | lakefile sets `autoImplicit := false` globally (`lakefile.lean:9`) |
| `decide` | 14,034 | tactic/`Decidable.decide`; kernel-evaluated, fine |
| `Classical.choice` (explicit) | 4 | permitted |
| `propext` (explicit) | 4 | permitted |
| `open Classical` / `attribute [local instance] Classical.propDecidable` | 8 / 7 | permitted |
| `elab`, `macro`, `syntax`, `simproc`, `csimp` | 0 | no metaprogramming in the closure |
| `instance` (non-local) / `local instance` | 148 / 40 | all `Fintype`/`Decidable`/algebraic instances built by `inferInstanceAs`, `Fintype.ofFinite`, `⟨by decide⟩`, or structure fields; no instance can be "inconsistent" without an axiom, and there are none |
| `termination_by` / `decreasing_by` | 9 / 5 | well-founded recursion, kernel-checked |

The nine `opaque`s: `queryRecovery` (`SqrtLog/LeafProgramPreparedRecoveryQuery.lean:59`,
body at `:86` `… := by`), `rawRecovery` and `fixedRecovery`
(`…RecoveryWitness.lean:178,198`, bodies `:= by`), and six `private opaque …Ports…`
subtype constants (`SqrtLog/LeafProgramQueryCleanup.lean:22`,
`SqrtLogSpace/DisjointReuse/SparseDFSProgram.lean:76`, `SqrtLogSpace/HashMarkedReturn.lean:14`,
`SqrtLogSpace/HeadSumAssembly.lean:24`, `SqrtLogSpace/NativeCode.lean:51`,
`SqrtLogSpace/NativeProgram.lean:106`), each `: {ports // ports = …} :=` with a value. An
`opaque` with a body is a definition whose unfolding is hidden; the kernel checks the
body against the type, so nothing is assumed.

## 3. Permitted axioms, axiom audit, nanoda

`ComparatorChallenges/SubexponentialSAT.json`: `permitted_axioms` = `propext`,
`Quot.sound`, `Classical.choice`; `definition_names: []`; `enable_nanoda: false`.
`formalization.yaml:1683-1685` registers the same declaration and file.

**No axiom-audit output exists in the repository.** `Final.lean:197-201` ends with five
`#print axioms` commands (for `compiled_exact_count_and_sat`, `exact_count_and_sat`,
`exact_count_eth`, `sat_polynomial_space`, `original_sat_main`), but their output is
only produced at build time and is recorded nowhere (`grep -r "depends on axioms"` over
the repository: nothing). `.github/workflows/` contains only `lock-prs.yml` (locks PR
conversations); **no CI builds or checks the Lean**. `ComparatorChallenges/README.md`
only says: install `comparator`, `landrun`, `lean4export`; `lake update`; `lake exe cache
get`; `lake env comparator <json>`.

Per the comparator README (leanprover/comparator, fetched 2026-11-05): comparator builds
challenge and solution under the `landrun` sandbox, exports both environments with
`lean4export`, checks that each theorem in `theorem_names` has in the solution the same
statement as in the challenge with **all declarations used in the statement matching**,
checks the proof bodies use only `permitted_axioms`, and has the Lean kernel accept the
proof. **nanoda** is an independent Lean 4 kernel written in Rust; `enable_nanoda: true`
(legacy; the newer form is `external_kernels`) replays the exported environment through
it, so a bug in the C++ kernel would have to be shared by a second implementation. With
`false`, this family's trust in the kernel is single-implementation.

## 4. Statement match

The solution file **does not import** `ComparatorChallenges/SubexponentialSAT.lean`
(`SqrtLogSpace/Final.lean:1-3` imports `NativeLargeEntry`, `SqrtLogSpace.Statement`,
`SqrtLog.StatementCanonical`). It re-declares every definition under the same full names:
`SAT.lean` (`Assignment`, `Literal` with `deriving DecidableEq`, `Clause`, `CNF`, the three
`eval`s, `WidthAtMost`, `satisfyingAssignments`, `count`, under `variable {V : Type u}
[DecidableEq V]` and `section Finite … [Fintype V]`), `BinaryArithmetic.lean` (`bitVal`,
`toNat`), `Encoding.lean` (nine definitions), `Computation.lean` (`Trace`,
`PrimitiveMachine`, `Cfg`, `step`, `init`), `SqrtLog/StatementScale.lean` (`runtimeScale`,
`runtimeBound`), `SqrtLogSpace/VisitedTape.lean` (`LocatedCfg`, `locatedInit`,
`headDisplacement`, `monitor`, `locatedStep`, `visitedSpace`) and
`SqrtLogSpace/EncodingBounds.lean:17` (`countWord`). `defdiff.py` finds **all 33 textually
identical** after whitespace normalisation; the only differences are `noncomputable def`
(challenge) versus `noncomputable section` (library) for `runtimeScale`/`runtimeBound`,
invisible to the kernel. Namespaces coincide (`OAI.Algorithms` + `SubexponentialSAT.X`
in the library equals the challenge's `OAI.Algorithms.SubexponentialSAT.X`). The theorem
statement from `theorem exact_count_and_sat` to `:= by` is **identical, 1,124 characters,
in both files** (`ComparatorChallenges/SubexponentialSAT.lean:181`, `Final.lean:74`).
Comparator enforces this at the exported-constant level, so a textual match is a
necessary sanity check, not the guarantee; a `definitionally different` library
definition under the same name would make comparator fail, not pass silently.

## 5. Proof structure

- **The machine.** `exact_count_and_sat` (`Final.lean:74-104`) instantiates
  `machine := GuardedCompiler.primitive program`, `countTape := 256`, `answerTape := 1216`
  (both `: Fin 1220`) from `compiled_exact_count_and_sat` (`Final.lean:10-72`), where
  `program : BitProgram.Program 80 1220 labels` is
  `Native.countingProgram cutoff k (NativeLeafProgram.command k)` (`NativeOuter.lean:16`):
  a first-order program over 80 one-bit registers, 1,220 Boolean stacks and a finite label
  set (`BitProgram.lean:10-30`). `GuardedCompiler.primitive` (`GuardedCompiler.lean:131`) is
  a `noncomputable abbrev`: it takes the explicit transition table `transition p`
  (`:30-47`, by cases on the instruction) and `selected p` (`:14-17`), feeds it to the
  stack compiler's `controller`, and reindexes the finite state type to `Fin stateCount`
  through `Fintype.equivFin`. So the machine is a **concrete table defined by pattern
  matching on the program**, composed with a classical renaming of states; the theorem is
  existential, so the noncomputability costs nothing logically. The `cutoff` and constants
  are also obtained non-constructively (`NativeLargeEntry.lean:48` uses
  `Filter.eventually_atTop`), which is fine for an `∃`.
- **The time bound.** `NativeLargeEntry.run` (`NativeLargeEntry.lean:11-33`) gives, for
  `cutoff < n`, a trace with `time ≤ runtimeBound C A d L n`; `A := 256 + At`
  (`:51`), `At` from `NativeLeafContract.uniform_contract` (`:39`). The
  `2^{A·runtimeScale n}` factor is assembled by `runtime_of_tree_and_leaf` (`:46`,
  `NativeOuterBudgets`) from the DFS visit bound of `Native.outer_from_setup`
  (`NativeOuter.lean:36-71`: `visits ≤ (… n + 1)^2 · 2^{n / sparsifySchedule n}`) and the
  leaf time `leafTime_runtimeBound`. For `n ≤ cutoff`, `Native.entry_small_primitive`
  (`NativeEntry.lean:81-100`) gives `time ≤ 28700·(L+1)^2` via the finite scanner of
  `FiniteFallback.lean`; `NativeOuterBudgets.runtime_with_fallback` (`:297`) and
  `space_with_fallback` (`:317`) fold both branches into `runtimeBound (C+28700) (A+1)
  (d+2)` and `(S+5022741)(L+1)^{e+2}` (`Final.lean:37-39`).
- **The compile lemma — where a hidden cost model would live.** `GuardedCompiler.
  primitive_execution` (`:160`): `BitProgram.RunsIn p n a b → RunsIn (primitive p).step
  (7*n) …`, with `compiler_overhead = 7` proved (`:152`); `CompileSpace.compile_word_answer_
  space` (`CompileSpace.lean:125-147`): from a BitProgram trace with per-prefix stack
  bound, a `Trace (locatedStep (primitive p))` of length `≤ 7·sourceSteps` whose
  `visitedSpace ≤ s·(bound + input.length + 15)`; `primitive_located_step` (`:600`) is
  the per-step version. **Their conclusions are stated over the comparator's own
  `locatedStep`/`Trace`/`visitedSpace`, and `time` in the final theorem is literally the
  length of a `Computation.Trace` of `PrimitiveMachine.step`.** No cost function defined by
  the compiler appears in the final statement; a wrong cost model would make these lemmas
  unprovable, not the theorem false. This is the decisive structural point.
- **Correctness of the count.** `Native.outer_from_setup` (`NativeOuter.lean:56-58`)
  yields `final.stacks ABI.countStack = countWord (SAT.count F)` and
  `final.stacks ABI.answerStack = [decide (0 < SAT.count F)]`, from
  `canonical_dfs_execution`; `Native.counting_primitive_from_entry` (`:73-95`) transports
  these to tapes of the primitive machine (`Turing.Tape.mk₁ ((countWord …).map some)`).
  `countWord_toNat` and `countWord_count_length` (`EncodingBounds.lean`) supply the
  decoding and length clauses. All are theorems about the concrete step function;
  the arithmetic content (sparsification, ring/moment computations) lies in the
  ~3,000 files beneath and was not read.
- Lemmas the proof rests on, with character: `NativeLargeEntry.run` (construction);
  `Native.entry_small_primitive` (construction; finite scanner); `NativeOuterBudgets.
  runtime_with_fallback`/`space_with_fallback` (real-analytic inequalities);
  `GuardedCompiler.primitive_execution`/`primitive_located_step` (construction, step
  simulation); `CompileSpace.compile_word_answer_space` (construction);
  `Native.outer_from_setup` and `counting_primitive_from_entry` (construction);
  `NativeLeafContract.uniform_contract` (abstract contract instantiated by the leaf
  program); `runtime_of_tree_and_leaf` (abstract arithmetic).

## 6. Build configuration

`lakefile.lean:89`: `@[default_target] lean_lib OAI`, root `OAI.lean`, whose line 49
imports `OAI.Algorithms.SubexponentialSAT.Main`; so `lake build` with the default target
elaborates exactly this closure. **The 886 non-closure files are never built** (dead).
`lakefile.lean:7-8`: `fixedToolchain := true`, `autoImplicit := false`. `lean-toolchain`:
`leanprover/lean4:v4.34.1`. `lake-manifest.json`: `mathlib` at
`https://github.com/leanprover-community/mathlib4.git` rev `d13f23b723b8a846827a245b89c10fc7d3f11612`
— confirmed on GitHub as upstream commit "chore: bump toolchain to v4.34.1" (author
Garmelon), consistent with the toolchain; **no patch file for Mathlib** exists in
`patches/` (23 patches, all for third-party packages: AINTLIB, PrimeNumberTheoremAnd,
carleson, iut, …), none of which this closure imports. 41 manifest packages, all
upstream URLs; the `lana-agents/*` packages are OpenAI's own and irrelevant here. **Build
hooks exist and should be read before running `lake`**: a `run_cmd` block
(`lakefile.lean:290-304`) executes at configuration time, calling `unsafe
env.evalConstCheck` and `preparePatchedDependencies`, which `git clone`s and `git apply`s
patches into `.lake/packages/<dep>` for eleven dependencies; a `post_update` hook
(`:306-371`) verifies/applies patches for twelve more. They touch only `.lake/packages`,
and only non-Mathlib packages, but they are arbitrary IO run by `lake`, which is one reason
this audit did not build.

## 7. Dates and consistency

`preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex:25`:
`\date{17 October 2026, revised 25 October 2026}`; the README carries only "October 25,
2026" and no version notes. `history.md` (Oct 26, 2026): the paper and Lean were added
"immediately" at the request of the Impagliazzo–Paturi–Williams working group; the Oct 29
entry ("Formalization Fix") concerns only the Hodge/CM family; **no correction or
retraction entry for 378**. `lean/docs/378.md` states the Lean proves time
`(L+1)^{O_k(1)} 2^{O_k(n (log log n)^2/√log n)}` with `L` the encoding bit length, versus
the manuscript's `(n+m)^{O_k(1)} 2^{O_k(n log log n/√log n)}`; `CONTENTS.md:9154` and
`overview.tex:363` quote the abstract's `2^{n/(log n)^{1/2+o(1)}}`. `Final.lean:104-147`
(`exact_count_eth`) does convert `(L+1)^d` to `(n + F.card + 1)^{2d}` for `n ≥ 20`, so the
`(n+m)` polynomial form is in Lean too; the sharper `log log n` (unsquared) exponent is not.

## What this audit does not establish

- **I did not build, export or replay the proof.** Zero `sorry`/`axiom` by grep is
  necessary, not sufficient: a file could fail to elaborate, and only `lake build` plus
  `#print axioms` (or comparator) shows the closure type-checks with the three permitted
  axioms. The repository offers no recorded evidence of either.
- I did not read the ~3,000 files of algorithmic content (sparsification, ring
  arithmetic, DFS) — only the spine from `Final.lean` down to the compiler lemmas. The
  argument above is that their correctness is kernel-enforced, not that I verified it.
- Mathlib `d13f23b7` and Lean `v4.34.1` are trusted as upstream; I did not audit either.
- Whether the comparator statement means what the paper claims (encoding, `runtimeScale`,
  `LocatedCfg` instrumentation, noncomputable machine) is the other agent's audit.
- The kernel check is single-implementation (`enable_nanoda: false`); no second kernel
  has replayed this family.
