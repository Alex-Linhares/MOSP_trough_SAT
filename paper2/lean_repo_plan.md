# Moving the Lean for *The pathwidth complex* to its own repository

A plan for the owner (loop0005 item 13, 2026-09-30). Nothing has been moved,
created or pushed. The decision that the proofs get their own repository is
`plan.md`, *Decisions*; on 2026-09-30 its scope was widened to the Lean, the
code and the data, and building it is the paper's last step. This file covers
the Lean part only.

## What the repository is for

Section 3's claims (`equivalences.md`, *Master table*): each Table 1 problem
defined from its source, its exact relation to pathwidth proved, and the
counterexamples to the claims that are false. The repository should build
**sorry-free** and **axiom-clean** (`propext`, `Classical.choice`,
`Quot.sound` only), which the present `lean/` does not quite do: it carries
the §24 conjecture in `Sandwich.lean`, which nothing in section 3 uses but two
section-3 files import. The plan below removes it from the import closure.

## Sizes

| Part | Files | Lines |
|---|---|---|
| Section 3 proper (`Complex/`) | 13 | 7,011 (6,022 through item 13; item 14 added 989) |
| Base needed from `lean/MOSPFormalization/` | 10 + an excerpt of `Sandwich.lean` | 1,392 + ~100 |
| Optional: the pattern-graph counterexample | 3 | 336 |

Toolchain `leanprover/lean4:v4.34.0-rc2` (`lean/lean-toolchain`); Mathlib
`master`, pinned by `lean/lake-manifest.json` at
`1192d6246b462d5d423cccde4066d15b18718ca9`. Pin that commit in the new
`lakefile` rather than `master`, so the paper's build is reproducible; bump it
deliberately once, before submission.

## Dependency order

Each file depends only on files above it (and Mathlib). Names are module
paths under the present `MOSPFormalization/`.

### Tier 0 — base, copied unchanged (all sorry-free)

1. `LinearLayout` — linear orderings of a finite vertex type.
2. `VertexSeparation` ← 1.
3. `PathDecomposition` (Mathlib only).
4. `Pathwidth` ← 3.
5. `LayoutToDecomposition` ← 2, 4.
6. `DecompositionToLayout` ← 2, 4.
7. `VSEquivPW` ← 5, 6: `vertexSeparation_eq_pathwidth` (row 12).
8. `MOSPInstance` (Mathlib only). Also defines `agreementGraph` and
   `IsReduced`, used only by the optional tier.
9. `OpenStacks` ← 1, 8: `mospValue`.
10. `MOSPGraph` ← 4, 6, 9: `mospValue_eq_pathwidth_add_one` (row 1) and the
    Helly lemma `PathDecomposition.exists_bag_of_isClique`, which items 03
    and 05 use.

### Tier 0′ — the bandwidth excerpt of `Sandwich.lean` (new file)

11. **`Bandwidth.lean`** (new) ← 7, 10. `Sandwich.lean` is 1,099 lines and
    carries the one `sorry`; section 3 uses exactly five of its declarations:
    `bandwidthOfLayout`, `bandwidth`, `bandwidth_le_bandwidthOfLayout`,
    `pathwidth_le_bandwidth` (all in its *Bandwidth* block, lines 116–194,
    with the helpers `val_le_of_adj`, `vertexSepAt_le_bandwidthOfLayout`,
    `vertexSepOfLayout_le_bandwidthOfLayout`, `vertexSeparation_le_bandwidth`,
    `pathwidth_le_bandwidthOfLayout`) and `vertexSepAt_le_vertexSepOfLayout`
    (line 232, which needs only `VertexSeparation`). Copy that block into
    `Bandwidth.lean`, keeping namespace `MOSPFormalization` and the names,
    and change the `import MOSPFormalization.Sandwich` of the two files below
    to `import …Bandwidth`. Nothing else changes. **Checked 2026-09-30** by a
    scratch build outside the repository: `Sandwich.lean` lines 108–195 and
    232–240 (the `variable` lines, the *Bandwidth* block and that one lemma)
    under the imports `VSEquivPW` and `MOSPGraph`, with `SplitBandwidth` and
    `EdgeSeparation` re-pointed at it, build without error; their headline
    theorems keep the three standard axioms; and `conjecture_sqrt_tw_f6` is
    no longer in the environment. Every other `Complex/` file reaches
    `Sandwich` only through those two.
    The rest of `Sandwich.lean` (degeneracy, treewidth, `pathGraph_isTree`,
    the branch lemma) belongs to sections 2/5 if the paper uses it; if so,
    move it without `conjecture_sqrt_tw_f6` and `minClosedNeighborhood`,
    which drops the `Mathlib.Analysis.Real.Sqrt` import too.

### Tier 1 — section 3 (`Complex/`), in build order

12. `GateMatrix` ← 10 (row 2).
13. `Narrowness` ← 7 (row 8).
14. `IntervalThickness` ← 7, 10 (row 5).
15. `OneDimLogic` ← 12, 14 (row 3).
16. `PLAFolding` ← 12 (row 4).
17. `SplitBandwidth` ← 11, 13 (row 9). Imports `Sandwich` today.
18. `EdgeSeparation` ← 7, 10, 11, 17 (rows 11, 12). Imports `Sandwich` today.
19. `NodeSearch` ← 18 (row 6).
20. `KirousisPapadimitriouGap` ← 19 (the error in [10]'s proof;
    `proof_reductions.md`). Written outside loop0005; belongs with section 3
    since the paper reports the gap.
21. `EdgeSearch` ← 19 (row 7).
22. `IntervalSearch` ← 12, 14, 19 (rows 5, 6: `intervalSearch_chain`).
22a. `NodeMonotonicity` ← 20, 22 (item 14: rows 5, 6 for the full game,
    `nodeSearchMonotonicity`, `nodeSearch_chain`). It uses only
    `two_le_of_isNodeSearch` from `KirousisPapadimitriouGap`; if that file is
    left out, copy it together with `contaminated_eq_of_searchCost_le_one` and whatever that uses.
22b. `EdgeSearchFull` ← 21, 22a (item 14: row 7 for the full game,
    `vertexSeparation_le_edgeSearch_le_add_two`).

Parallelism: 12–14 are independent; so are 15–17 once their parents are
built; 20–22 are independent of each other.

### Tier 2 — optional: the "wrong graph" counterexample

23. `Reduction` ← 7, 9 (one surviving lemma; the false pattern-graph
    statements were deleted; the word `sorry` appears only in comments).
24. `Examples` ← 23.
25. `MOSPGraphExamples` ← 10, 24: the four-customer star on which
    `pathwidth(pattern graph) + 1 = 2` against `mospValue = 4`. The paper
    needs it if section 3 discusses which graph Table 1 means; it depends on
    nothing in `Complex/`.

## What stays behind

`ForMathlib/` (Mathlib-candidate restatements, not imported by anything in
section 3), `Check.lean` and `Encoding.lean` (the SAT encoding, item 7 of the
solver's certificate chain), and the rest of `Sandwich.lean` unless sections
2/5 claim it. Nothing in section 3 imports them.

## Renames to consider at the move (not done here)

- Namespace `MOSPFormalization.Complex` → e.g. `PathwidthComplex`; the base
  files' `MOSPFormalization` → the same root, so the paper cites one prefix.
  A pure rename: do it with the move, in one commit, and rebuild.
- `Complex/Basic.lean` never became necessary (no shared helper needed
  generalising); the reusable helpers live where they were first proved
  (`EdgeSeparation.lean` *Helpers*, `SplitBandwidth.lean`'s
  `bandwidth_le_of_key` and `pathwidth_le_of_map`, `PLAFolding.lean`'s
  `finLayout`). Collecting them is optional tidying.

## Checks the new repository should run

1. `lake build` with no warnings about `sorry`.
2. `grep` for `sorry` and `axiom` outside comments: zero (the gate's
   `strip_comments` in `Ralph_Loops/loop0005/gate.py` can be copied).
3. `paper2/axiom_check.lean`, moved to the repository root and with its
   control line (`conjecture_sqrt_tw_f6`) deleted: `#print axioms` on the 44
   theorems section 3 names (33 through item 13, 11 added by item 14), each expected to show exactly `propext`,
   `Classical.choice`, `Quot.sound`.
4. The checker `paper2/complex_check.py` and `tests/test_complex_check.py`
   stay in this repository (Python, part of the dataset side), or go into the
   paper's code deposit; they share no code with the Lean.

## Move procedure

1. New repository, `lean-toolchain` and a `lakefile.lean` copied from `lean/`,
   Mathlib pinned to the commit above; `lake exe cache get`.
2. Copy tiers 0, 1 (and 2 if wanted) preserving paths; create
   `Bandwidth.lean` from the `Sandwich.lean` excerpt; change the two imports.
3. Root module importing every file, as `lean/MOSPFormalization.lean` does.
4. Build, run checks 1–3. Only then apply the renames, and rebuild.
5. In this repository, leave `lean/` as it is: `MOSPGraph.lean` and the rest
   remain the solver project's formal record; `CLAUDE.md` points to them.
