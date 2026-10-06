# loop0009 — revise paper 2 for readability (paper2/review_readability.md): items

- [x] **01 The new structure.** Set the section order and create the
  appendices, before any section is rewritten.
  - **Order:**
    1. Introduction;
    2. The equivalences (old §3);
    3. The names and the communities (old §2, to be cut to about two pages
       in item 04);
    4. The search, read as a pathwidth algorithm;
    5. Computational results and a dataset (new, from old §4.6–4.7);
    6. Conclusion;
    7. Appendices.
  - **Appendix A** is the formal names: a table mapping each theorem, lemma
    and counterexample in the paper to its Lean name. Move **every** Lean-name
    footnote there, replacing it in the text by a reference such as
    "(Appendix A, A.3)". Keep `make axioms` and the axiom-coverage test
    passing; extend the citation collector to read the appendix if needed.
  - **Appendix B** is the machinery the review names: old §3.3 and §3.4,
    Proposition 4.8, Theorem 4.9, the analysis of why the published proof
    fails, and the minimality search. Move it as is; item 05 decides what
    the body keeps.
  - **A "Data, code and proofs" statement** replaces the title-page footnote
    and every file path and `python -m` command in the body. The repository
    is to be released; leave its URL as a placeholder.
  - **What this item does not do.** Move and relabel only, with no rewriting.
    Fix every cross-reference. Record the old-to-new section map in
    PROGRESS.md for later items.

- [x] **02 The introduction** (review §7 and change 1; the owner's notes).
  - **Figure 1.1**, from the verified example. Panel (a) is the matrix, with
    open stacks in the two orders. Panels (b) and (c) are the gate matrix
    layouts of the two orders, with nets as segments, packed into 3 and 5
    tracks. Panel (d) is the graph, with the bags of the good order's path
    decomposition. Draw it with matplotlib or TikZ as a print vector. Add a
    small test that recomputes the example's numbers.
  - **The paragraphs, in order:**
    1. MOSP, defined;
    2. the same instance as a gate matrix layout, with density;
    3. the same instance as a graph, so the optimum is pathwidth + 1;
    4. Table 1.1 with a "This paper" verdict column (exact / band / false),
       ending on the central question;
    5. how the table came to be (the owner's account, kept);
    6. the headline results with numbers;
    7. the roadmap.
  - **Consistency.** Make the count of exact, band and false rows identical
    in the abstract, the introduction and the equivalences section. Count
    pathwidth itself once and say how it is counted.
  - **The abstract.** Rewrite it to match: the question, then the four
    results.

- [x] **03 The equivalences section** (review §3–5 for old §3).
  - Open with what the section establishes and how it is organised: the
    exact rows, the bands, the false rows.
  - Motivate each theorem before stating it, with one plain sentence after
    each on what it means for the table.
  - Rename Table 3.1's "Proved in" column to "Published source", and give
    Table 3.1 and Figure 3.1 captions that state the conclusion.
  - Move notation here from the introduction.

- [x] **04 The names and the communities** (review change 7; the owner's
  notes).
  - Cut to about two pages, and keep one of Table 2.1 and Figure 2.1.
  - Ask and answer: which name does the literature use? (pathwidth, by far).
    Then: besides pathwidth, which community has been most active? (MOSP,
    with the table in the owner's notes). Then the 2005 Constraint Modelling
    Challenge story, from Chu & Stuckey (2009) §1 (held:
    `literature/chu_stuckey_2009.pdf`), as the bridge: the best exact search
    for this family came from the MOSP community.
  - Word the "best" claim with the published-numbers caveat. Move the
    method's details, Figure 2.2 and the citation analysis to the
    supplement or appendix.
  - Redo or annotate the "OR is an island" figure so its point is visible,
    or drop the claim.

- [x] **05 The search section** (review changes 4 and 5).
  - **Open with the stakes:**
    - two published dominance theorems are false;
    - no wrong answer was ever produced;
    - no certified value changed;
    - the repaired search is proved sound.

    Then state the main theorem informally.
  - **Set it up.** Put the pathwidth reading first, with the dictionary
    (Table 4.1) and the border notation in the first subsection. Then add
    pseudocode for the search (an `algorithm` environment, or a boxed
    listing).
  - **For each rule:** intuition, then the counterexample, the repair and
    the matching test. The matching test is presented as a contribution,
    not under "What we did not find".
  - Move "What a rule must satisfy" to where it is used, and the remaining
    machinery to Appendix B.

- [x] **06 Computational results and the dataset** (review change 6).
  - **An experimental setup subsection:** hardware (read it with `lscpu` and
    `free`; state the core count used), language and compiler, budgets,
    instances and configurations, defined in plain words.
  - **Definitions:** corpus, provenance (certified by refutation, certified
    by bound, upper bound only), DRAT, and the proof object.
  - **The cost of the repair, the re-certification, the certificates, and
    the dataset.** Cut Table 4.5 to about seven columns.
  - **The two in-flight values**, with their status and the date checked.

- [x] **07 Figures and tables, every one** (review §4 and change 9).
  - Every caption states the conclusion.
  - No figure has a title printed inside it.
  - Every table and figure is referenced in the text before it appears, and
    the text says what to see in it.
  - Remove any duplicates.
  - Regenerate any figure that needs it (vector, legible at one column, no
    text under 7 pt), with its script and test.

- [x] **08 Notation and vocabulary, whole paper** (review change 8 and §6).
  - One symbol per object.
  - C for customers or columns, never both.
  - k used consistently between sections, with the off-by-one made explicit
    where width and stacks differ.
  - One symbol for the border.
  - Z for the MOSP value only.
  - One wording for "has a requirement".
  - One name for the one-dimensional-logic graph.
  - Every term defined before use.
  - No project-internal words in the body.
  - Sentences over about 40 words split.
  - **Add a notation table** at the start of the equivalences section.

- [x] **09 The conclusion.** Answer the central question in its first
  paragraph, then:
  - what transfers between the problems, and what does not (bands, false
    rows);
  - what the search episode teaches about published dominance rules;
  - what is open (the missing Kashiwabara & Fujisawa 1979, the gap
    `EdgeSearchMonotonicity`, the two in-flight values, the pathwidth bound
    work).

  Bring in no topic that the body does not cover.

- [x] **10 A second review.** Read the revised PDF cold, as a referee would,
  against `paper2/review_readability.md` §1–§9.
  - Write `paper2/review_readability_2.md`: what is fixed, what is not, and
    any new problems.
  - Then fix the top five new problems.
  - Report the three-sentence reconstruction again; it should now come easily.

- [ ] **11 Reserve.** The best remaining readability gap, one session.
