# loop0008 — strengthen paper 2 toward a first full draft: items

- [x] **01 Prior-art sweep of every work citing Chu & Stuckey (2009).**
  - **List the citers.** Use OpenAlex (`cites:` filter on the work with DOI
    10.1007/978-3-642-04244-7_21) and Crossref, plus the citers of Chu's 2011
    thesis (hdl:11343/36679) where indexed. Google Scholar blocks automated
    access, so do not use it.
  - **Read each citer.** Fetch every open-access full text and search it for a
    restatement, implementation, test or correction of the definite move or the
    better move: Theorems 1 and 2, or the thesis's Theorems 6.3.6 and 6.3.8.
    Read the hits in context.
  - **Output.** A table appended to `paper2/prior_art_counterexample.md`, one
    row per citer: year, authors, venue, DOI, full text read (yes/no and
    where), what it says about the rules, and any correction. Then a closing
    verdict worded to the evidence, with the share read in full. List the works
    that could not be read under `literature/MISSING.md`, so the owner can
    fetch them.
  - Save open-access PDFs that restate the rules in `literature/`.

- [x] **02 The thesis's Theorem 6.3.8 is false, in Lean.**
  - **The theorem.** In a new file `lean/MOSPFormalization/Search/ChuThesis.lean`,
    prove that Chu (2011) Theorem 6.3.8 is false on `cexGraph` at k = 6. Its
    premise is `close(q, S) ≥ open(q, S ∪ {r})`, not the CP paper's. State the
    published wording as a universal claim, as `PublishedTheorems.lean` does,
    under both readings of `close`: `closeCount` and `closeCountLiteral`. The
    brute force in `paper2/thesis_check.py` gives witnesses: S = {2}, r = 3,
    q = 0 (unclosed reading); S = {1}, r = 6, q = 12 (literal).
  - **The record of Theorem 6.3.6.** Also record, as a theorem or a docstring
    pointer, that Theorem 6.3.6 is Theorem 1 verbatim, so
    `chuStuckey_theorem1_false` refutes it.
  - **Downstream text.** Update `paper2/prior_art_counterexample.md` (the
    Lean theorem now exists) and `paper2/revised_algorithm.md` (cite the
    thesis beside the CP paper wherever the published rules are stated or
    refuted). Add the file to `paper2/axiom_check.lean`.

- [x] **03 Section 4 in pathwidth language.**
  - **The new subsection.** Add one to `paper2/revised_algorithm.md` (its
    place in the section is your call, stated in PROGRESS.md). It restates the
    search and every rule as statements about vertex layouts of a graph: the
    closing order is a layout, `open` and `close` are boundary changes, and
    the search decides `vs(G) ≤ k`. A reader from the pathwidth literature
    should see a pathwidth algorithm with a proved repair, not a MOSP-only
    result.
  - **What it must cover.** Rule by rule: the free move, the definite move
    (published and repaired), the subset rule, the better move (published and
    repaired), the old move and the memo. Each is a lemma in layout terms,
    with the Lean theorem that proves it, citing the MOSP-to-pathwidth bridge
    (`MOSPGraph.lean`, `pathwidth_solver/`).
  - **Related pathwidth work.** Relate the rules to known pathwidth search
    rules with citations from held papers. For example, Coudert, Mazauric &
    Nisse's greedy step is the definite move's counterpart (see
    `literature/MISSING.md`). Say what is the same and what differs.

- [x] **04 Section 4's dataset, defined and priced.**
  - **Write `paper2/dataset.md`.** It defines the benchmark dataset the paper
    promises: every instance, from the collections in
    `paper2/benchmarks/README.md` and the MOSP corpus, of a problem proved
    exactly equivalent to pathwidth.
  - **Deduplicate** by isomorphism class (`learning/canonical.py`, nauty
    certificates), across collections and across problems. Report counts per
    collection before and after.
  - **One file format**: graph, provenance (`certified:refutation`,
    `certified:bound`, `solution`), width, witness layout, source collection,
    and the problem it came from.
  - **An independent checker**, `paper2/dataset_check.py`, sharing no code
    with the solvers. It re-measures every witness's width, checks that each
    `certified:bound` value equals an independently computed lower bound, and
    reports the provenance mix. Include tests.
  - **Price the full certification run.** Use node counts already recorded
    (`pathwidth_solver/bench/results/`, the compute ledger) and the cost model.
    Report it in core-hours, by collection.
  - **Run** only what fits in 4 cores × 2 hours, and say what is left.

- [x] **05 Certificates for the repaired rules.**
  - **The extension.** Extend the customer search's proof object
    (`learning/search_certificate.py`, `reports/ml_nature.md` §32) to the
    repaired rules. Each definite move and each better-move drop carries its
    witness: the matching that `HasDefiniteMatching` asks for, and for the
    better move the premise data.
  - **The checker** recomputes each premise from the graph alone, verifies the
    matching, and replays the residual tree. It shares no code with the search.
  - **Verification.** Verify certificates on the corpus instances at 41-75
    customers under the repaired rules, at most 4 cores. Report how many
    verify, the certificate sizes, and the checking times.
  - **Hand-built failures.** Show the checker rejects a certificate built from
    the published rules on `DEFINITE_CEX`, and one with a corrupted matching.
  - **Report.** Write `paper2/certificates.md` and add tests. Propose a C
    emitter; do not build it.

- [x] **06 Section 2: three figures and the method paragraph.**
  - **Choose the three figures** from `paper2/figures/` (popularity, citation
    graph, trends) that best carry section 2, with a one-paragraph reason for
    each.
  - **Write the method paragraph.** It covers the OpenAlex queries, the
    stem-matching contamination, the relevance filter and hand labels
    (`paper2/relevance.py`), and the corrected counts. Use plain, checkable
    wording, with the regenerate commands.
  - **Where it goes.** Write both into `paper2/popularity.md` under a heading
    "For the paper". If a figure needs a print-quality version (vector, legible
    in one column), regenerate it.

- [x] **07 Audit every number in paper 2.**
  - **Scope.** Every quantitative claim in `paper2/revised_algorithm.md`,
    `equivalences.md`, `problem_transformations.md`, `solver_fix.md`,
    `popularity.md`, `prior_art_counterexample.md` and `plan.md`.
  - **For each claim:** the file and line, the value, its source (a regenerate
    command, a CSV, a Lean theorem), and whether it reproduces now. Rerun only
    what fits in 4 cores × 1 hour; check the rest against its recorded data.
  - **Output.** Write `paper2/number_audit.md`. Fix every drift in the source
    documents (never in `CLAUDE.md`) and list each fix.
  - **The open re-certifications.** For the values `paper2.solver_fix_split`
    is still refuting, state their current status from its files, and say they
    are in flight.

- [x] **08 The LaTeX draft.**
  - **Location and class.** `paper2/latex/`: `main.tex`, one file per section,
    and `refs.bib`, built from `table1.bib` and every work cited in sections 2-4.
    Use the INFORMS Journal on Computing class if a copy can be obtained from
    INFORMS's author page. Otherwise use `article`, formatted to the journal's
    stated rules, and record the template as "to obtain".
  - **Sections.**
    - Section 1 and section 5 are marked placeholders. Section 1 waits on the
      owner's thesis, section 5 on the rest.
    - Sections 2-4 are drafted from their markdown sources, not pasted.
      Theorems are stated with their Lean names in a footnote or margin note,
      and the counterexample is Figure 4.1.
    - Tables are made from the CSVs.
  - **Build.** It must build with `latexmk -pdf` with no undefined references.
    Add a `Makefile` target. Record the page count.

- [ ] **09 Reserve.** The best remaining gap from items 01-08, one session.
