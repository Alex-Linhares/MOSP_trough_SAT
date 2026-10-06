# TASK: Revise paper 2 for readability, following the referee-style review

## Philosophy
- **Read first, in full**:
  - `paper2/review_readability.md`, the review this loop executes. Its
    sections 3–9 are your checklist and its top-10 list your priorities.
  - The draft, `paper2/latex/main.tex` and `sec*.tex`, and its PDF.
  - `paper2/plan.md`.
  - The **owner's notes** below. They override the review where they differ.
- **The goal is a paper a reader can follow.** Every section, figure, table and
  theorem must say what question it answers and what the reader should
  conclude. The central question goes in the introduction and is answered in
  the conclusion.
- **Revise the presentation, not the results.** Do not change any theorem's
  content, any number or any claim's strength. When you move or reword a
  claim, keep its source: the Lean name (in the appendix), the CSV, or the
  regenerate command in the `paper2/*.md` documents. If the review asks for
  something the results cannot support, say so in PROGRESS.md, not in the
  paper.
- **Write plainly.** The audience is IJOC readers in OR and computing, not
  graph-minor theorists or Lean users. Define a term before its first use,
  keep paragraphs with topic sentences, keep sentences short, and use
  consistent notation. Use no project-internal vocabulary in the body:
  "csearch", "C engine", file paths, `python -m`, loop names, "our corpus"
  without definition.

## The owner's notes (2026-10-06)
- **The introduction**:
  - Start by defining MOSP with a small worked example. Then show the same
    instance as a gate matrix layout, where the gate order changes which
    nets overlap, and the density (tracks) as the quantity minimised. Then
    the same instance as a graph (the review's panel (d)).
  - Then the pathwidth complex table (Table 1.1, which reproduces Linhares &
    Yanasse 2002 Table 1), then how the table came to be.
  - Use the review's example. It is verified over all 24 orders: patterns
    P1 = {a,b}, P2 = {b,c,d}, P3 = {c,d,e}, P4 = {e,f}; order P1P2P3P4
    peaks at 3, order P1P3P4P2 at 5; 2 orders reach 3, 16 give 4, 6 give 5.
  - Keep the owner's account of how the table was collected: assembled while
    reading the literature during the PhD, never checked, no proof
    restated; in hindsight the thesis's most important finding, hence this
    article. It is in the current `sec1_intro.tex`. Shorten it if the review
    says so, but keep its substance and voice.
- **The names section (now after the equivalences)** must ask: *besides
  pathwidth, which community has been most active?* The answer, from
  `paper2/trends.py` counts of relevant works:

  | | 2005–09 | 2010–14 | 2015–19 | 2020–24 | 2005–24 |
  |---|---:|---:|---:|---:|---:|
  | pathwidth | 114 | 179 | 267 | 311 | 871 |
  | MOSP | 17 | 17 | 5 | 12 | 51 |
  | vertex separation | 7 | 10 | 15 | 0 | 32 |

  MOSP is second, though vertex separation led in 2015–19. The owner's
  point: **it is not a coincidence that Chu & Stuckey were working on MOSP
  when they produced arguably the best exact algorithm for pathwidth.** The
  mechanism, from Chu & Stuckey (2009) §1:
  - MOSP was the subject of the first Constraint Modelling Challenge (May
    2005, 13 entries);
  - Garcia de la Banda & Stuckey won it;
  - Chu & Stuckey built on the winner and closed every open challenge
    instance.

  This is the section's punchline and its bridge to the search section.
  - **Word the "best" claim carefully.** On the benchmarks where published
    exact pathwidth results exist, the search ported to graphs proves more
    instances than reported: Rome 97.0% against 95.6% for Coudert, Mazauric
    & Nisse (2016) at 600 s; VSPLIB trees 50/50 against their 30;
    Harwell-Boeing 39 against their 26. These are comparisons with published
    numbers on other hardware, not a head-to-head.
  - **Verify every number** against `paper2/popularity.md`,
    `paper2/trends.py` and `pathwidth_solver/PLAN.md` before using it.
- **Table numbering** stays section-based (Table 1.1 and so on). Call the
  2002 table "the Linhares–Yanasse table" in prose, so it is not confused with
  our tables.
- **The authors** are Alexandre Linhares and Horacio Hideki Yanasse. Do not
  invent affiliations; leave a marked placeholder.

## A long computation shares the machine
- `paper2.solver_fix_split` is refuting the two never-certified values
  (`Random-125-125-2-2_0`, `-2-3_0`). Its PID is in
  `paper2/data/solver_fix_split.pid`, and a watcher continues it to
  2026-10-13. **Do not stop it, restart it, or edit its files.** If its log
  shows a line beginning `!!!`, record that at the top of PROGRESS.md and end
  the session.
- **Use at most 4 cores.** Find processes by PID, never by command-line text.
- The paper may say these two values are in flight. Take the status from
  `python -m paper2.solver_fix_split --summary`, and mark it as of the date
  you checked.

## Current Focus
Item 01 sets the new structure (section order, appendices, the
data-code-proofs statement). Items 02–07 rewrite one part each. Item 08 is
the whole-paper notation and caption pass. Item 09 writes the conclusion.
Item 10 is a fresh review against `review_readability.md`, and item 11 is the
reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration.

## Acceptance Criteria (per item)
- [ ] The draft builds: `make -C paper2/latex` then `make -C paper2/latex
      check`, with no undefined references or citations. New section files
      go in the Makefile's dependencies (its wildcard is `sec*.tex`; name
      appendix files `sec9_*.tex` or extend the wildcard).
- [ ] `python -m pytest tests/test_paper2_latex.py` passes. Every theorem the
      draft cites keeps its axiom line (`make axioms` if Lean names change).
- [ ] `python3 Ralph_Loops/loop0009/gate.py` passes (lake build, sorry count,
      both pytest suites, LaTeX check).
- [ ] A short entry in PROGRESS.md: what changed, which review points it
      closes (by the review's numbers), the page count before and after, and
      what is left.
- [ ] The item is marked `- [x]`, or `- [!]` with the reason.

## Completion Conditions
An item is DONE when its part reads clearly and the gate passes. If you find
a factual error in the draft while revising, fix it, keep its source, and
record it at the top of PROGRESS.md.

## Important Notes
- Do NOT edit `CLAUDE.md`, any Lean proof, or anything under `solutions/`.
  Do NOT push. Commit nothing yourself; the driver commits.
- Keep `paper2/*.md` documents as the sources of record. The paper is
  rewritten; those documents are not, except to fix an error.
- Print mode: **ending your turn ends the session.** Never end on a
  background wait.
