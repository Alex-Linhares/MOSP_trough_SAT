# Second referee report: readability, after revision

**Manuscript:** "The pathwidth complex" (Linhares and Yanasse), draft of
6 October 2026, 37 pages as read (25 of body, a one-page data statement,
3 of references, 9 of appendices).
**Read against:** `paper2/review_readability.md` (the first report), §1–§9.
**Scope:** as before, readability, argument structure, figures and audience.
I did not check the mathematics; I did check internal consistency of the
counts I met.

---

## 0. Overall assessment

The revision fixes the three problems the first report put at the top.

- **The paper now says which question it answers.** The central question
  closes the paragraph that presents Table 1.1 (p. 2) and is the second
  sentence of the abstract. Every section opens by saying which part of it
  the section answers, and Section 6 answers it in its first paragraph.
- **The project is off the page.** No Lean name, file path, `python -m`,
  configuration name or internal date remains in the body. Lean lives in
  Appendix A, behind "(Appendix A, A.n)" pointers, and the repository in a
  one-page data, code and proofs statement.
- **The object is shown first.** Figure 1.1 shows one instance as a
  sequencing problem, a gate matrix and a graph, on p. 2, before any history.

The paper now reads as one argument: a table, which of its rows hold, why
nobody checked, what moving one algorithm across exposed, and what moving the
benchmarks across made possible. What remains is length (Section 8 below)
and a handful of small inconsistencies, five of which are fixed in this pass.

---

## 1. Summary in three sentences, as a reader would now reconstruct it

> Linhares and Yanasse (2002) listed twelve problems from operations
> research, VLSI design and graph theory as equal "plus or minus one" to the
> minimum number of open stacks; this paper proves that eight rows are exact
> (pathwidth or pathwidth plus one, counting pathwidth itself), two are bands
> one and two wide, and two are false, all machine-checked in Lean, and shows
> that the literature uses the name "pathwidth" for the family while the
> open-stacks community, the most active besides, rarely reads graph theory.
> Read as a pathwidth algorithm, the best exact open-stacks search (Chu and
> Stuckey 2009) rests on two false dominance theorems; the correct rule is a
> known pathwidth commitment lemma, which the paper tests with one bipartite
> matching per candidate, and the repaired search is proved sound, costs at
> most 2% more nodes per benchmark set and re-proves all 115 affected
> benchmark optima unchanged. Because one certified pathwidth answers every
> problem in the exact core, the paper releases 17,714 benchmark graphs,
> distinct up to isomorphism, 16,087 with certified pathwidth and a witness
> layout.

**It came easily.** All three sentences could be written from the abstract,
the "What we find" bullets and the section openings, without searching. Each
of the four places where reconstruction failed in the first report now
works:

1. **The hinge between the halves** is said three times, at the right
   places: the central question's second clause (p. 2), the end of §3.3
   ("Two consequences shape the rest of the paper"), and the first sentence
   of Section 4 ("If MOSP is pathwidth, then the best exact MOSP algorithm is
   a pathwidth algorithm").
2. **The counts** agree everywhere: abstract, Table 1.1's caption and
   verdict column, the first bullet, Section 2's opening and summary,
   Table 2.3, the conclusion. "Exact core" is defined once (§2.2) as the
   eight exact rows plus multiple folding and the vertex separator game.
3. **The dataset's purpose** is stated where it is built (§5.4's first
   paragraph), foreshadowed by Theorem 2.4's closing sentence and §3.3.
4. **The stakes** (no wrong whole-instance answer known; no benchmark value
   changed) are in the abstract, the third bullet, the second paragraph of
   Section 4 and Section 5's opening.

---

## 2. The central question

Stated on p. 2 and in the abstract, in the first report's wording. Answered
point by point in the first paragraph of Section 6. **Fixed.**

---

## 3. What is fixed, against the first report's ten changes (§9)

| # | Change | Status |
|---|---|---|
| 1 | Introduction around a worked example and the central question | **Fixed.** Order P1–P7 of the first report's §7.2; Figure 1.1 with all four panels. |
| 2 | Answer on p. 2; "Table 1" naming; "Published source"; identical counts | **Fixed.** Verdict column in Table 1.1; "the Linhares–Yanasse table" throughout; counts identical. |
| 3 | Remove the project from the page | **Fixed.** Appendix A and the data statement; no internal vocabulary left in the body. |
| 4 | Section 4: pathwidth reading first, stakes, Algorithm 1, rule criteria where used | **Fixed.** Table 4.1 and the border notation in §4.1, Algorithm 4.1, a worked example, "What a rule must satisfy" in §4.5. |
| 5 | §4.3 order: intuition → counterexample → repair → matching test | **Fixed.** The matching test is announced as the section's algorithmic contribution; "In words" precedes Theorem 4.7. |
| 6 | Computation and data as their own section, with a setup | **Fixed.** Section 5 with §5.1 Experimental setup (machine, compiler, workers, nodes, pairs, descents, configurations, provenance). The three runs "in flight" in the first report are finished; see §4 below for the two values that remain. |
| 7 | Names section after the equivalences, shortened, ending on the bridge | **Fixed.** Two pages; one method paragraph; Table 3.2 replaces the network figure and makes the island visible (4% against 23%). |
| 8 | Unify notation | **Fixed**, with one slip found in this pass (new problem 1). Notation table 2.1. |
| 9 | Captions state conclusions; redundant displays cut | **Fixed.** Every caption now leads with its conclusion; Figure 4.1 has no in-image title and a second panel. |
| 10 | Machinery to appendices; conclusion answers the question | **Fixed.** Appendices A–C; Section 6 answers, advises, lists limits and open problems. |

Section-level points of the first report's §3–§6 not listed above were
checked one by one; all are closed except those in §4 below.

---

## 4. What is not fixed

- **The title.** It is now "The pathwidth complex", which no longer
  overstates (the first report's objection was to "one width" and "a solver
  proved sound"). It also says little to an IJOC reader who does not know
  the term; a subtitle naming open stacks would help. The owner's call.
- **Length.** The first report expected the body to lose 5–6 pages while
  gaining Figure 1.1 and Algorithm 1. It went from about 22 to 25 pages: the
  figure, the algorithm, a worked example, Table 2.1 (notation), Table 2.2
  (problems in one line), the experimental setup and the conclusion are all
  additions the first report asked for, and the moves to appendices did not
  pay for them. IJOC has no hard page limit, but a referee will notice
  Section 4 (pp. 12–20). Candidates if it must shrink: the §4.2 bullet list
  repeats intuitions that §4.3–§4.4 give again; §4.6's paragraph on the
  least-border commitment ("a second repair ... we have not built it") could
  go to Appendix B; Table 4.1 and Table 4.2 overlap in three rows.
- **"Online supplement" versus appendix.** The first report suggested an
  online supplement for the bibliometric method, the split table, the full
  certificate table and the prior-art log. They went to Appendices B and C
  instead. This is a defensible choice (one document, one reviewable object),
  but it is why the PDF is 37 pages.
- **Two values are still "in flight".** §5.2, Table B.1 and Section 6 say
  that `Random-125-125-2-2_0` and `-2-3_0` were never certified and are being
  refuted (dated 6 October 2026). They are now clearly separated from the
  115 re-certified values and do not affect any claim, which answers the
  first report's concern about the three runs of its time. A referee will
  still ask; resolve before submission if the run allows.

---

## 5. New problems

Found on this reading; none was in the first report, and most were
introduced or exposed by the revision. Ranked by how much they would cost a
reader.

1. **An undefined symbol in a theorem.** Theorem 2.6(1) and Table 2.3 write
   $\lceil |N|/2\rceil$ for the number of nets over two. $N$ appears nowhere
   else as a set of nets, and the notation table reserves $N[c]$ for a closed
   neighbourhood. The nets are the rows $C$. *(Fixed: $|C|$, with "net set
   $C$" in the theorem.)*
2. **"Nine problems" does not add up.** Section 6 says the dataset serves
   "nine problems", while "exact core" is defined as ten (the eight exact
   rows plus multiple folding and the vertex separator game), and §5.4 lists
   "gate matrix layout with multiple folding" as if it were one problem with
   an option. The nine comes from multiple folding being gate matrix layout
   itself (Table 2.2). *(Fixed: §5.4 now says "gate matrix layout (which
   multiple folding equals) ...: nine problems in all".)*
3. **"Five collections" that are four.** §5.1 defined the MOSP corpus as "five
   public open-stacks collections" and then named four, one with a second
   copy. *(Fixed: "four public open-stacks collections, one of which is
   distributed twice".)*
4. **A caption that hides the largest open group but two.** Table 5.3's
   caption said the open classes are "mostly" in PACE, the VSPLIB grids and
   Harwell–Boeing, and two MOSP sets. Counted, the Rome graphs hold 327 open
   classes, more than the grids (41) and Harwell–Boeing (33) together; the
   caption was ranking by share and did not say so. It also wrote "Carvalho
   and Soma" where the text cites "de Carvalho and Soma". *(Fixed: "Largely
   open: PACE, the VSPLIB grids and Harwell-Boeing, and the MOSP sets of de
   Carvalho and Soma and of Frinhani et al.; Rome's 327 open classes are
   under 3% of it.")*
5. **A promise the paper does not keep.** "How to read the paper" said "the
   proofs are given in the text", while §2.2 says of the exact core "We do
   not reprove them on paper". *(Fixed: "each proof is given or cited in the
   text".)*

Smaller, not fixed in this pass:

6. Appendix A's entry A.39 still called the better move's two requirements
   "implementation faults", the project history the body had reframed.
   *(Fixed as a one-line label change, beside the five.)*
7. Theorem 2.4(3), one-dimensional logic: "if every net lies on a gate, the
   fewest tracks is θ(H), and if some gate connects a net it is pw(H) + 1"
   reads as two conditions that sound alike. Say "if every net meets at least
   one gate ...; if at least one net meets a gate ...".
8. Table 4.2: the published definite move has "–" in the counterpart column
   while the published better move has "none found". If the dash means "its
   counterpart is the endpoint case of the commitment condition" (Lemma 4.9),
   say so.
9. Table 5.1's second column is headed "Vertices" for the open-stacks rows,
   which are counted in customers. "Size" or a footnote.
10. Section 6's open problems introduce two numbers the body no longer
    carries: the 1,024-vertex-per-component limit of the implementation and
    the 154 classes above it. One sentence in §5.1 (setup) would give them a
    home.
11. Section 4.2's bullet list and §4.3–§4.4 each give the intuition for the
    definite move ("it seems safe to close q at once"); one of the two can go.

---

## 6. Figures and tables

All 19 floats were re-read. Every caption leads with its conclusion, every
float prints on or after the page of its first reference, and no figure has
an in-image title. Figure 1.1 does what the first report's §7.3 asked; panel
(d) carries the hub theorem before it is stated. Figure 4.1(b) now shows the
repair, and with panel (a) explains Section 4.3 in one picture. Table 3.2 is
the best new display: the island that Figure 2.3 failed to show is now one
number per cell.

---

## 7. Audience

An IJOC reader who knows MOSP and branch and bound, and nothing about
pathwidth or Lean, can now follow the body: path decompositions are shown
before they are defined, search games and pebbling are one line each with
definitions in Appendix B, and Lean appears in one sentence of the
introduction and in Appendix A. The experimental setup meets IJOC's
expectations; the data, code and proofs statement has a placeholder URL.

---

## 8. Remaining priorities, in order

1. Decide the title (a subtitle naming open stacks).
2. Resolve or freeze the two in-flight values before submission.
3. If length must come down, cut in Section 4 first (§4 above).
4. Items 7–11 of §5, each a sentence.
5. Fill the affiliations and the repository URL.
