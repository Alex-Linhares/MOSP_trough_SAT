# TASK: The pathwidth complex — state and prove the equivalences of Table 1

## Philosophy
- Read `paper2/plan.md` first (section 3 is what this loop builds), then
  `paper2/README.md`, `paper2/literature/MANIFEST.md`, and the block of
  `CLAUDE.md` headed "The MOSP–pathwidth chain, closed on held papers". The
  twelve problems are those of Table 1 of Linhares & Yanasse (2002)
  (`literature/Linhares and Yanasse - 2002 - Connections between cutting-pattern
  sequencing, VL.pdf`, and `paper2/table1.bib`); their source papers are in
  `paper2/literature/`, named by Table 1 bracket number.
- **Table 1 asserts; it does not prove, and it may be wrong.** Its claim is
  "equivalent up to ±1". Already known from reading the sources: Fomin (1998)
  proves a *sandwich* `pw ≤ sb ≤ pw + 1`, not an equality (Theorem 8);
  Lengauer (1981) is about a *vertex* separator game, and the edge version he
  mentions, min-cut linear arrangement, is not equivalent to pathwidth — his
  Definition 6 ("modified" min-cut) may be what Table 1 means; Kornai & Tuza
  (1992) Proposition 3.1 is an exact equality `ν = pw + 1`; Ellis, Sudborough &
  Turner (1994) prove `vs ≤ s ≤ vs + 2` for the edge search number. Every
  statement is taken from the source, checked on small instances, and only
  then formalised.
- **State before you prove, and check before you state.** Two `sorry`s in
  this development hid false statements, not hard ones (`CLAUDE.md`, loop0004
  lessons). A Lean statement is written only after item 02's brute-force
  checker agrees with it on every small instance it can reach.
- **No `sorry`, no `axiom`.** Phase-2 items (03-09) end sorry-free or are
  marked blocked with the precise obstacle. Only phase-3 items (10-12, 14) may
  leave a stated gap, and only by adding a line to
  `Ralph_Loops/loop0005/allowed_sorries.txt` with the reason, mirrored in
  `paper2/equivalences.md`. The gate counts them.
- **One definition per problem, faithful to its source**, not a definition
  reverse-engineered from pathwidth. A theorem `X = pw + 1` where X was
  defined as `pw + 1` proves nothing. Cite the source's definition (paper,
  page, numbered definition) in the docstring.
- **Graph conventions.** Reuse `SimpleGraph`, `pathwidth`, `vertexSeparation`,
  `PathDecomposition`, `mospGraph` from the existing development
  (`lean/MOSPFormalization/`). State for finite vertex types. State edge
  cases explicitly (empty graph, isolated vertices, disconnected graphs):
  several of the sources assume connected graphs with at least one edge.

## Current Focus
Phase 1 (items 01-02): settle every statement, no Lean. Phase 2 (03-09):
prove the equivalences that are within reach. Phase 3 (10-12): graph
searching, where the full theorems need monotonicity arguments; prove the
monotone versions and state the rest as named gaps. Then 13 (assemble) and
14 (reserve).

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration.

## Acceptance Criteria (per item)
- [ ] Lean code lives in `lean/MOSPFormalization/Complex/<Name>.lean`, one
      file per problem (plus shared helpers in `Complex/Basic.lean`), each
      imported from `lean/MOSPFormalization.lean`, each with a module
      docstring naming the source and the exact statement proved.
- [ ] Python (the checker, item 02) lives in `paper2/complex_check.py`, runs
      as `python -m paper2.complex_check`, and has tests in
      `tests/test_complex_check.py` on hand-checkable graphs.
- [ ] `paper2/equivalences.md` is updated: the item's row of the master table
      (problem, source definition, the graph it lives on, the exact relation
      to pathwidth, where it is proved, Lean theorem name, status), plus a
      short section for the item.
- [ ] `python3 Ralph_Loops/loop0005/gate.py` passes (lake build, imports,
      sorry/axiom count, pytest ~2.5 min).
- [ ] The item is marked `- [x]` (done) or `- [!]` (blocked, with a reason in
      PROGRESS.md) in `iterations.md`.

## Completion Conditions
An item is DONE when either:
1. **Solved**: meets all criteria, OR
2. **Blocked**: documented in PROGRESS.md with the specific obstacle (the
   lemma that would be needed, what Mathlib lacks, the size of the gap). A
   precise statement of what cannot be done in the session is a deliverable.
   An item that turns out to be **false as Table 1 states it** is DONE when
   the correct relation is stated and a counterexample to the original is
   proved in Lean (as `MOSPGraphExamples.lean` does for the pattern graph).

## Context
- **Lean**: `lean/` (Lake project, Mathlib master, toolchain in
  `lean/lean-toolchain`). Build: `cd lean && lake build` (seconds when cached;
  rebuilding one file takes minutes). Existing results to build on:
  `MOSPGraph.lean` (`mospValue_eq_pathwidth_add_one`, the Helly lemma
  `PathDecomposition.exists_bag_of_isClique`), `VSEquivPW.lean` (vertex
  separation = pathwidth), `Sandwich.lean` (degeneracy ≤ pw ≤ bandwidth,
  `pathGraph_isTree`, treewidth ≤ pathwidth, the corrected branch lemma),
  `MOSPGraphExamples.lean` (how a counterexample is proved), `Check.lean`
  (how `decide` checks small instances).
- **Sources**: `paper2/literature/` — [1] Yanasse 1997, [4] Fink & Voss 1999,
  [6] Möhring 1990 (full chapter, 35 pp.), [7] Ohtsuki et al. 1979, [8] Wing,
  Huang & Wang 1985, [9] Kirousis & Papadimitriou 1985, [10] 1986, [11]
  Kornai & Tuza 1992, [12] Fomin 1998, [13] Kinnersley 1992, [14] Lengauer
  1981. [5] Kashiwabara & Fujisawa 1979 is **not held**; interval thickness is
  stated from [9] and Möhring [6] instead. Also `literature/`:
  `ellis_sudborough_turner_1994_vertex_separation_search_number.pdf`,
  `fellows_langston_1987_*`, `fellows_langston_1989_*`,
  `yanasse_1997a_*`. Read PDFs with the Read tool (`pages` parameter) or
  `pdftotext`.
- **Testing**: `python3 Ralph_Loops/loop0005/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md`, `lean/MOSPFormalization/MOSPGraph.lean`,
  `VSEquivPW.lean` or other existing proved files except to add an import to
  the root `lean/MOSPFormalization.lean`; build on them from `Complex/`. If an
  existing lemma needs generalising, copy it into `Complex/Basic.lean` under a
  new name and say so.
- Do NOT create a GitHub repository or push anything; the Lean for the paper
  will be moved to its own repository by the owner. Item 13 writes the move
  plan.
- Do NOT touch `solutions/`, the solver, or any benchmark driver.
- Commit nothing yourself; the driver commits after the gate passes.
- You are running in print mode: **ending your turn ends the session.** Do
  not end it waiting on a background job. Run builds in the foreground; a
  full rebuild of one file can take several minutes and that is fine.
- When stopping a background process, match its PID, never a bare
  `pkill -f <word>` (it has killed a session's own shell before).
- Another project's loop (`~/dev/Kemp_Tanembaum_matlab_code`) may be using
  cores; it is not yours to touch.
- If a proof is not converging, stop at a clean state: keep the proved lemmas,
  delete the broken ones, and write the obstacle down. A half-proof with
  `sorry` is not a clean state.
