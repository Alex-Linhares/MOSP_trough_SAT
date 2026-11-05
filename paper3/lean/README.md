# The companion Lean of paper 3

*Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.*

Paper 3's Section 8 ("The statement in our Lean"). Nothing here is a Lean
source file of its own beyond the audit: the companion Lean is two files of
our library, left where loop0014 wrote them by the owner's decision of
2026-11-05 (`paper3/ETH_AMBIGUOUS.MD`, S3 resolved: "leave the Lean where it
is"; the original brief of item 07, which moved them to
`lean/MOSPFormalization/ETH/`, is superseded, entry 07a).

## The files

| file | what it is | lines |
|---|---|---|
| `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean` | a verbatim copy of lines 1–190 and 220 of `lean/ComparatorChallenges/SubexponentialSAT.lean` in the OpenAI collection (commit `4eaee875`, SHA-256 `4183b205…`), after a 30-line header (source, commit, hash, Apache 2.0 licence). Definitions only: the formulas and their count, the canonical encoding, the multitape `PrimitiveMachine`, `Trace`, `runtimeScale` (ρ(n) = n (ln ln(n+16))² / √ln(n+16)), `runtimeBound`, `countWord`, the located configuration, `locatedStep`, `visitedSpace`. The theorem and its `sorry` (clone lines 191–219) are not copied. | 221; the copy is lines 31–221 |
| `lean/MOSPFormalization/SubexpPathwidth/Frame.lean` | `SubexpCount (k : ℕ) : Prop` (lines 84–107), the comparator theorem's body character for character; `ExactCountAndSat : Prop := ∀ k, 2 ≤ k → SubexpCount k` (110); the lemmas `SubexpCount.anti` (113), `ExactCountAndSat.subexpCount` (119), `IsSubexpExponent` (125), `runtimeBound_eq` (128), `tendsto_log_sq_div_sqrt` (132), `runtimeScale_isLittleO` (144), `isSubexpExponent_runtimeScale` (163), `LocatedCfg.monitor_config` (169), `Trace.config_of_locatedStep` (180). Lines 192–268 belong to the other study and are not cited by the paper. | 268 |

Both files are imported by `lean/MOSPFormalization.lean` (lines 76–77) and
built by `lake build` in `lean/`; the loop's gate checks after every session
that the whole library has no `sorry` and no `axiom` declaration.

## The names the paper cites

Appendix A of the paper (`paper3/latex/secA_appendix_lean.tex`), eight rows:
the copied vocabulary (ten `OAI.Algorithms.SubexponentialSAT.…` names),
`SubexpCount`, `ExactCountAndSat`, `SubexpCount.anti` with
`ExactCountAndSat.subexpCount`, `runtimeBound_eq`, `tendsto_log_sq_div_sqrt`
with `runtimeScale_isLittleO`, `IsSubexpExponent` with
`isSubexpExponent_runtimeScale`, `LocatedCfg.monitor_config` with
`Trace.config_of_locatedStep`. All under the namespace
`MOSPFormalization.SubexpPathwidth` except the copy, whose namespaces are the
source's.

## The audit

`axiom_check.lean` prints the axioms of those 21 declarations, in the pattern
of `paper1/axiom_check.lean` (without its `sorryAx` control line: this paper's
acceptance rule is that every line is on the three standard axioms, entry
07b). Run from `lean/`:

```bash
cd lean && lake env lean ../paper3/lean/axiom_check.lean > ../paper3/lean/axiom_check.log
```

`axiom_check.log` is the committed output (2026-11-05 05:30 UTC, repository
commit `95eb564a0`, Lean 4.34.0-rc2 commit `6a10ac8c`, Lake 5.0.0, Mathlib
`1192d6246b46` from `lean/lake-manifest.json` — our library's toolchain, not
the clone's `v4.34.1` / `d13f23b7`): 19 lines on exactly
`[propext, Classical.choice, Quot.sound]`; `Computation.Trace` on no axiom
(an inductive definition); `SqrtLogSpace.countWord` on `[propext, Quot.sound]`;
`sorryAx` on none.

## The re-diff

`python3 -I paper3/scripts/lean_rediff.py` (from the repository root; `--check`
verifies without writing) reads the clone with `open()` only and writes
`rediff.log`:

1. **the copy**: our lines 31–221 against the clone's lines 1–190 followed
   by 220, byte for byte — identical (191 lines each side, diff empty); the
   clone's SHA-256 and commit as the header records;
2. **the statement**: the body of `SubexpCount` (Frame.lean 85–107) against
   the body of `exact_count_and_sat` (clone 195–217, `:= by` removed) —
   identical after whitespace normalisation (1,073 characters) and line by
   line after stripping indentation (23 lines; ours sit two columns further
   left, a `def` body against a `theorem` type);
3. **no `sorry`, no `axiom`** in either of our files outside the header
   comment; the clone's one `sorry` is at line 218, outside the copied range.

Exit status is non-zero if any check fails.

## What this does not claim

`SubexpCount k` is a `def` of a `Prop`, never proved here and never an axiom;
the copy is definitions only (the proof's 3,091 modules are not copied); no
`#eval` can evaluate `runtimeScale` (it is `noncomputable`, over real
logarithms — every number in the paper's Section 2 is from a Python script);
the statement match is textual, not a `lean4export`-level check; the lemmas
fix the shape of the bound and the limit of the exponent and say nothing
about any machine's running time, the constants, or the manuscript's
unverified exponents.
