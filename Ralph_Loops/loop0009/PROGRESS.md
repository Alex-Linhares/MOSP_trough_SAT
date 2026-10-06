# loop0009 progress

Plan: revise paper 2's draft (`paper2/latex/`) for readability, following
`paper2/review_readability.md` and the owner's notes in `TASK.md`. Items are
in `iterations.md`. Gate: `python3 Ralph_Loops/loop0009/gate.py`. It includes
`make -C paper2/latex check`.

Current: 4/11 SOLVED

## Setup — 2026-10-06

- **The draft** has 26 pages and five sections. Section 1 was written today
  from the first author's thesis (`literature/linhares_2001_phd_thesis_industrial_pattern_sequencing.pdf`).
  Table 1.1 reproduces the Linhares–Yanasse table. Yanasse is now an
  author.
- **The review** (`paper2/review_readability.md`, 617 lines):
  - The paper is reconstructable, but nearly fails in four places: the hinge
    between the halves, inconsistent counts of exact rows, the buried
    dataset, and late stakes.
  - The top 10 changes map to items 01–09.
  - Its Figure 1.1 example was verified by brute force over all 24 orders.
- **In flight.** The split run on `Random-125-125-2-2_0` and `-2-3_0` is
  running, with a watcher continuing it to 2026-10-13. Do not touch it.

---

## Iteration 1 — 2026-10-06 (item 01, the new structure)

### Completed
- **Section order** now: 1 Introduction; 2 The equivalences (was §3);
  3 The names (was §2); 4 The search (was §4.1–4.5); 5 Computational results
  and a dataset (new, was §4.6–4.7); 6 Conclusion (placeholder, was §5); an
  unnumbered *Data, code and proofs* statement; references; Appendix A
  (formal names); Appendix B (supporting material). Files renamed with
  `git mv`; nothing rewritten beyond pointer sentences and cross-references.
- **Old-to-new map, for later items:**

  | old | new | file |
  |---|---|---|
  | §1 | §1 | `sec1_intro.tex` (unchanged) |
  | §3, 3.1, 3.2 | §2, 2.1, 2.2 | `sec2_equivalences.tex` |
  | §3.3 edge cases, K–P gap | App. B.1 (`app:edge`) | `sec9b_appendix_machinery.tex` |
  | §3.4 thirteenth member | App. B.2 (`app:thirteenth`) | same |
  | Table 3.1, Fig 3.1 | Table 2.1, Fig 2.1 | |
  | Theorems 3.3–3.7, Lemmas 3.1–3.2 | 2.3–2.7, 2.1–2.2 | |
  | §2, Table 2.1, Figs 2.1–2.3 | §3, Table 3.1, Figs 3.1–3.3 | `sec3_names.tex` |
  | §4.1–4.5 | §4.1–4.5 (4.4 now holds only Thm 4.8 = old 4.10) | `sec4_search.tex` |
  | "Why the published proof fails" | App. B.3 (`app:whyfails`) | appendix B |
  | minimality search (s4:144–148) | App. B.4 (`app:minimality`) | appendix B |
  | Prop 4.8, Thm 4.9 + proof sketch | Prop B.1, Thm B.2 (`app:machinery`) | appendix B |
  | Thm 4.10, Lemma 4.11 | Thm 4.8, Lemma 4.9 | |
  | §4.6, §4.7 | §5.1 (`sec:practice`), §5.2 (`sec:dataset`) | `sec5_results.tex` (label `sec:results`) |
  | Tables 4.3–4.6 | Tables 5.1–5.4 | |
  | §5 Closing | §6 Conclusion (`sec:closing`) | `sec6_conclusion.tex` |
  | title footnote, paths, `python -m` | Data, code and proofs (`sec:data`) | `sec7_data.tex` (a LaTeX comment there keeps every moved command) |
  | 53 `\lean{}` footnotes + Table 4.1's Lean column | Appendix A, Table A.1, entries A.1–A.60 | `sec9a_appendix_lean.tex` |

- **Appendix A.** Every `\lean{...}` footnote is now `\leanref{key}`, printing
  "(Appendix A, A.n)"; the entries are `\leanentry{key}{result} \leannames{...}`
  rows of a longtable, grouped by section. Table 4.1's Lean column moved there
  (A.47–A.52). The axioms sentence and its footnote (old s3:20–26) and "All
  Lean names in this section are in Search/…" (old s4:26–28) moved to the
  appendix preamble; the body keeps a one-line pointer. The split's soundness,
  cited before only as a file path, is entry A.53 (both names already had
  axiom lines). `check_lean.py` now reads `\leannames{}` too; cited names
  went from 89 to 91 (the two split theorems), none lost; `check_axioms
  --no-lean`: 0 uncovered.
- **Data, code and proofs** statement with a boxed URL placeholder; removed all
  `python -m` commands and file paths from the body (s2:65–68, s3:233,
  Fig 4.1 caption, s4:325, s4:438, s4:485–487, s4:566) and the title footnote.
  Authors carry boxed "affiliation to be added" placeholders.
- `paper2/latex/README.md` file and table lists updated to the new numbering.
- **Review points closed:** change 3 in part (Lean footnotes, paths, commands,
  title footnote; `csearch`/`default`, "C engine", "our corpus", "Since 1
  October 2026" remain for items 06/08); change 6 structurally (Section 5
  exists, no setup yet); change 7's reorder (not the cut); change 10's
  appendix moves (Section 3.3, 3.4, proof-failure analysis, minimality search,
  Prop 4.8/Thm 4.9); §3 "axioms footnote" and §6.6.
- **Pages:** 26 before, 29 after (Appendix A's table is ~2.5 pages; the
  body is about the same length).

- **Gate:** `python3 Ralph_Loops/loop0009/gate.py` → GATE PASS (lake build ok,
  sorry 1/1, 1411 passed, pathwidth_solver 114 passed, no undefined
  references, 29 pages). `tests/test_paper2_latex.py`: 6 passed.

### Blockers
- None. Split run (PID 2185545) alive; no `!!!` line in its log.
- **Gate pitfall, for every later item:** if `main.pdf` is stale, the gate's
  `make check` rebuilds it, pdflatex prints a Latin-1 byte (from "Möhring"),
  and `gate.py` dies with `UnicodeDecodeError` in `subprocess.run(text=True)`.
  Run `make -C paper2/latex` before the gate. (`gate.py` was not edited.)

### Next
- Item 02, the introduction. Note for it and item 04: the names section still
  says "This section asks a prior question" and points forward to §2 as if it
  came later — reword in item 04. Table 1.1 has no verdict column yet.
- Item 05 decides what of Appendix B returns to the body. The Lean-proof
  remarks inside proofs (Thm 4.2 "goes through narrowness", Thm 4.7's Mathlib
  Hall remark, the crusade-argument remark after Thm 2.5) were left in place;
  candidates for Appendix A.
- Appendix A's names column could be one name per line (item 07).

---

## Iteration 2 — 2026-10-06 (item 02, the introduction)

**Status update, not an error:** `python -m paper2.solver_fix_split --summary`
(checked 2026-10-06) shows the three re-certifications that Section 5 called
"still running" (`Random-125-125-2-1_0`, `-2-5_0`, `-4-4_0`) are now REFUTED,
so all 115 customer-search values are re-refuted, none changed. Section 5's
sentence now says "all 115 (as of 6 October 2026)" and that Table 5.2 was read
on 3 October; **Table 5.2 itself (`tables/split.tex`) was not regenerated** —
`make_tables.split_table()` would now also print the two never-certified
values (`-2-2_0`, `-2-3_0`, both partial). Item 06 should regenerate it and
decide how to present those two.

### Completed
- **`sec1_intro.tex` rewritten** in the review's §7.2 order: (1) MOSP defined
  on the review's example; (2) the same instance as a gate matrix layout, with
  density = tracks; (3) the same instance as a graph, bags of order A, so
  optimum = pathwidth + 1 (points to Thm 2.4); (4) Table 1.1 + the two readings
  of "±1", ending on the central question (review §2 wording); (5) the owner's
  account of how the table came to be, kept in substance and voice, with the
  García de la Banda–Stuckey quote and "so whether it is true matters"; the
  NP-hardness reduction detail, the duplicated quotation and the "§7.1 does not
  mention it" aside are cut; (6) "What we find", four bullets with numbers;
  (7) "How to read the paper", with the one-sentence Lean statement.
- **Figure 1.1** (`paper2/intro_figure.py` → `paper2/figures/sec1_fig1_example.{pdf,png}`,
  matplotlib vector, fonts ≥ 7 pt, 6.5 in): (a) matrix with open intervals and
  both profiles, (b)/(c) gate matrix layouts packed by the left-edge algorithm
  into 3 and 5 tracks, (d) the MOSP graph and the bags of order A. Every number
  is recomputed in the script. **Test** `tests/test_intro_figure.py` (5 tests):
  profiles 2 3 3 2 / 2 4 5 3; peaks over the 24 orders {3: 2, 4: 16, 5: 6};
  left-edge tracks = peak and no overlap on a track; brute-force vs = 2 = optimum
  − 1; the bags of A are a path decomposition; print limits.
- **Table 1.1** has a shaded "This paper" column (exact / band / false, with
  footnotes for the exact variants of the two false rows); the original caption
  is now quoted, so its "on the literature" reads as the original's.
- **Counts made identical** in the abstract, intro (caption, bullet) and
  Section 2's summary: *eight exact counting the pathwidth row itself, two
  bands, two false*; the two exact variants (multiple folding, VSG) named
  separately. Table 2.1's path-width status changed from "definition" to
  "exact" to match.
- **Abstract rewritten**: problem, question, then the four results. No
  "Tamaki" or "both of our solvers".
- **Notation paragraph moved** verbatim from the intro to the start of
  Section 2 (item 03 polishes it; the C = columns vs customers clash remains
  for item 08).
- `\usepackage{colortbl}` added to `main.tex`.
- **Numbers verified**: the 2005–24 counts of the owner's table recomputed
  from `paper2.trends.binned` on `data/openalex_trends.json` (pathwidth 871,
  MOSP 51, vertex separation 32; gate matrix layout only 9, so "most active
  over 2005–2024" holds; all-time MOSP is 4th, behind GML and PLA, so the intro
  says "over 2005–2024"); 1,213 vs 380 (`tables/names.tex`); 844 / six
  (`sec3_names.tex`, `popularity.md`); ≤ 2% node totals (`tables/cost.tex`,
  worst total ratio 1.020; single pairs reach 1.040, so the wording is "over
  each benchmark set … total"); 17,714 / 16,087 (Section 5).
- **Review points closed:** change 1 (whole); change 2 in part (verdict column,
  "Linhares–Yanasse table" in the intro and caption, identical counts; the
  "Proved in" rename and "Table 1" elsewhere are items 03/08); §2 central
  question (placed at end of P4 and as sentence 2–3 of the abstract);
  §3 Title/abstract points except the title; §3 Section 1 bullets (one-sentence
  definition split, NP-hardness detail cut, the duplicated quotation merged,
  self-assessment now follows the transfer sentence, "so whether it is true
  matters" added, §7.1 aside cut, contributions → headline results, roadmap
  added, notation moved); §7.2–7.3 (Figure 1.1 as specified); §6.3 item 5
  (Φ vs Π: one quotation now).
- **Pages:** 29 before, 30 after (Figure 1.1 and the verdict column).
- **Gate:** `python3 Ralph_Loops/loop0009/gate.py` → GATE PASS (lake build ok,
  1416 passed / 2 skipped / 1 xfailed, pathwidth_solver 114 passed, no
  undefined references, 30 pages). `tests/test_paper2_latex.py` +
  `tests/test_intro_figure.py`: 11 passed.

### Blockers
- None. Split run PID 2185545 alive; no `!!!` line in its log.
- **Not done, deliberately:** the title still overstates (review §3, "one
  width", "a solver proved sound"); changing it is the owner's call. Noted for
  item 10 / the owner.

### Next
- Item 03, the equivalences section. Its opening still quotes the 2002
  sentence that the intro now quotes; cut it to a back-reference. "Table~1"
  is still used for the 2002 table in Sections 2–5 (34 occurrences): rename to
  "the Linhares–Yanasse table" in items 03/04/08. "Exact core" is still used
  without definition in Section 5 and Appendix A.
- Item 06: regenerate `tables/split.tex` (see the status note above) and
  present the two never-certified values with the date checked.
- The draft date in `main.tex` still reads 3 October 2026.

---

## Iteration 3 — 2026-10-06 (item 03, the equivalences section)

### Completed
- **`sec2_equivalences.tex` rewritten for readability; no theorem, number or
  claim changed.**
  - **Opening** now says what the section answers (the first half of the
    central question), defines exact / band / false in terms of the intro's two
    readings of "±1", gives the answer (8 / 2 / 2) and the organisation. The
    2002 quotation and the two readings are no longer repeated (back-reference
    to Section 1). One sentence on Lean + Appendix A, and "where a result is
    published we cite the proof and do not repeat it".
  - **2.1 The problems:** pathwidth, vertex separation, MOSP and gate matrix
    layout kept in full (with "interval property" named and Figure 1.1
    referenced); the other eight in a new **Table 2.1**, one line of intuition
    each ("progressive" now defined; "bandwidth" defined). Their formal
    definitions moved verbatim to new **Appendix B.1** (`app:defs`).
  - **2.2 What is true** (`sec:true`) has run-in headings *The hub*, *The exact
    core*, *Bands*, *False rows*. Each theorem is motivated before and
    followed by a "For the table, …" sentence.
  - **Helly lemma folded** into the proof of Lemma 2.1 (cliques sit in a bag);
    "Two lemmas carry most of the exact rows" replaced by an accurate
    statement (the lemma serves the MOSP theorem). Theorem 2.2 (vs = pw) is
    headed "known", sketch cut to three sentences.
  - **Theorem 2.3 (MOSP = pw + 1)** is announced through Figure 1.1(d) (the
    active sets of the good order are the bags).
  - **Pattern graph remark** motivated with Yanasse & Senne (2010), new bib
    entry `YanasseSenne2010` (DOI 10.1016/j.ejor.2009.09.017, verified by
    `check_refs`, cache updated).
  - **"Exact core" defined** (the eight exact rows plus multiple folding and
    the vertex separator game), matching Section 5's list.
  - **Left-edge algorithm cited** (Möhring 1990, p. 31, as in
    `equivalences.md`).
  - **Bands:** the arithmetic is spelled out (sb ∈ [Z−1, Z], es ∈ [Z−1, Z+1]),
    in the text and in the summary. The brute-force values are said once to be
    computed, not proved; "Fomin" now cited by key.
  - **Crusade-argument remark moved to Appendix A's preamble**, with a new
    sentence there listing what is computed rather than proved (band ends,
    the minimality search, Section 5's results).
  - **Misattribution of edge separation** is now a footnote of Table 2.2.
  - **Table 2.2 (was 2.1):** column "Proved in" → "Published source"; caption
    leads with the conclusion.
  - **Figure 2.1:** caption leads with the conclusion; **mpb removed** from the
    figure (it is defined only in Appendix B.2); VSG moved into its slot.
    `paper2/section3_figure.py` regenerated; `tests/test_section3_figure.py`
    updated (asserts mpb is not drawn).
  - "Table~1" → "the Linhares–Yanasse table" throughout Section 2 and in
    Appendix B.2; one name, "net graph H", for the one-dimensional-logic graph
    in Section 2.
- **Review points closed:** §3 Section 3 bullets (opening, axioms footnote
  already gone, 3.1 compact table + appendix definitions, "progressive",
  connection/net graph, run-in headings, "two lemmas", pattern graph remark,
  crusade remark, brute-force footnote, misattribution, summary arithmetic);
  §4 Table 3.1 (rename, conclusion caption, misattribution footnote) and
  Figure 3.1 (conclusion caption, mpb dropped); §5 rows Lemma 3.1–3.7 and the
  star remark; change 2's "Published source" rename; §6.2 "exact core",
  "left-edge algorithm", "crusade argument", "progressive"; §6.3 item 8 within
  Section 2.
- **Pages:** 30 before, 32 after (new Table 2.1 and Appendix B.1).
- **Gate:** `python3 Ralph_Loops/loop0009/gate.py` → GATE PASS (lake build ok,
  sorry 1/1, 1416 passed / 2 skipped / 1 xfailed, pathwidth_solver 114 passed,
  no undefined references, 32 pages). `tests/test_paper2_latex.py` +
  `tests/test_section3_figure.py`: pass.

### Blockers
- None. Split run PID 2185545 alive; no `!!!` line in its log.

### Next
- Item 04 (names): Section 3 starts on a new page, leaving half of page 9
  blank (placeins flushes Section 2's floats); check after Section 3 is cut.
  Section 3 still says "Table~1" (≈10 times) and "This section asks a prior
  question".
- Item 07: the figure file is still named `sec3_fig1_chain` (Figure 2.1);
  rename with the script if desired. Figure 2.1 still has 15 nodes (adds
  multiple folding, VSG, pes, mns to the twelve); the caption explains them.
- Item 08: Section 5 says "Table~1's exact core"; now that "exact core" is
  defined in Section 2, drop "Table~1's". The notation table for Section 2 is
  item 08's. Theorem and lemma counters are shared (Lemma 2.1, Theorem 2.2).

---

## Iteration 4 — 2026-10-06 (item 04, the names and the communities)

**A number to note, not an error in the draft:** the owner's notes give Rome
"97.0% against 95.6%". 97.0% is the *pre-repair* count (11,183 / 11,534).
The repaired rules, which are the default the paper describes, prove 11,194 /
11,534 = 97.05%, printed as **97.1%** (`paper2/solver_fix.md`, "Table 1:
proved widths"). The paper uses the repaired figure. VSPLIB trees 50 vs 30 and
HB 39 vs 26 are the same under both rule sets; Coudert et al.'s figures (95.6%
in 10 min; trees n ≤ 67 = 30; hb 26) are from `pathwidth_solver/bench/reference.py`.

### Completed
- **`sec3_names.tex` rewritten and cut to about two pages** (p. 10 bottom to
  p. 12 top, plus Figure 3.1). Order: opening that states the two questions
  (which name? besides pathwidth, which community?) and why they matter (a
  result under one name is invisible under another); one *How we counted*
  paragraph (one annotator with model assistance; phrase rule agrees on 78%,
  same conclusions; lower bounds); **3.1 Pathwidth has absorbed the family**
  (Figure 3.1, caption leads with the conclusion; the "most likely published
  under pathwidth" sentence); **3.2 Besides pathwidth, open stacks** (new
  Table 3.1, the owner's period table: pathwidth 871, MOSP 51, vertex
  separation 32 over 2005–24; vertex separation led only in 2015–19; edge
  search 28 next; and new Table 3.2, the island); **3.3 From an open-stacks
  challenge to a pathwidth solver** (Chu & Stuckey 2009 §1: May 2005
  challenge, 13 entries, García de la Banda & Stuckey won, an order of
  magnitude faster; Chu & Stuckey branched on closing customers, 5–6 orders
  faster, closed every open challenge instance in 10 s; then the graph
  benchmark comparison with the caveat "published numbers on other hardware,
  not a head-to-head run"), ending on the two consequences (the bridge to §4
  and §5). "Commitment lemma" replaced by "a theorem already known in the
  pathwidth literature"; "Table~1" gone from the section.
- **The island made visible**: the citation-network figure is dropped from the
  paper (script and PDF kept) and replaced by **Table 3.2**, a 3×3
  "works citing X, of which also cite Y" table: OR 135 → 6 cite graph theory
  (4%), VLSI 285 → 65 (23%). The 2002 paper counts as OR, as the existing "six"
  did; with it counted, the cells sum to 844.
- **New Appendix C** (`sec9c_appendix_names.tex`, `app:names`): the full
  method and robustness paragraphs (minus "The check changed the counts and
  two of the conclusions"), Table C.1 (the old names table with citations; the
  1,212/1,213 note now said once, here), the citations-vs-usage point and the
  Fomin aside, and Figure C.1 (timeline; caption leads with the conclusion
  and explains why row totals differ from Table C.1, which closes the review's
  57/58, 53/55 consistency point).
- **Generators**: `paper2.section2_figures.numbers()` now returns
  `discipline_sets` and `periods_2005_24`; `make_tables.periods_table()` and
  `communities_table()` write `tables/periods.tex` and `tables/communities.tex`
  (only these and `names.tex` were regenerated; `split.tex` was not touched,
  it is item 06's). Names table header → "Reference in the 2002 table", row
  "Pathwidth". Figure labels unified ("pathwidth", "edge search", "node
  search"; legend "discipline in the 2002 table"); Figures 3.1 and C.1
  regenerated. Two tests added to `tests/test_section2_figures.py` (period
  counts incl. the next names; the discipline sets and the table cells).
- Intro roadmap mentions Appendix C; `paper2/latex/README.md` updated.
- **Review points closed:** change 7 (whole: reorder done in item 01; one
  method paragraph; usage and communities results; bridge to §4; Figure 2.2,
  citations-vs-usage and method detail moved out; "the check changed" cut);
  change 9 for Table 2.1/Figure 2.1 (one kept in body), Figure 2.2, Figure
  2.3 (replaced), the 1,212/1,213 note said once; §3 Section 2 bullets
  ("prior question" gone, motivation sentence added, method one paragraph,
  key sentence moved up, citations point and Fomin aside moved, 2.3 to
  appendix, "commitment lemma" removed); §4 Table 2.1, Figures 2.1–2.3
  (label consistency, conclusion captions); §6.1 transition End of §1 → names.
- **Pages:** 32 before, 32 after (body about one page shorter; Appendix C
  adds about one).
- **Gate:** `python3 Ralph_Loops/loop0009/gate.py` → GATE PASS (lake build ok,
  sorry 1/1, 1418 passed / 2 skipped / 1 xfailed, pathwidth_solver 114
  passed, no undefined references, 32 pages). Rebuilt afterwards for the
  names-table label change: `make check` clean, 32 pages;
  `tests/test_paper2_latex.py` + `tests/test_section2_figures.py`: 12 passed.

### Blockers
- None. Split run PID 2185545 alive; no `!!!` line. `--summary` (checked
  2026-10-06): `-2-2_0` and `-2-3_0` still partial; the other six REFUTED.

### Next
- Item 05 (search): §4's opening should echo the bridge ("If MOSP is
  pathwidth, the best MOSP algorithm is a pathwidth algorithm"); the review's
  s4:369–372 point ("this is the isolation measured in Section 3") now refers
  to Table 3.2. §4 already explains Chu & Stuckey place MOSP among "graph
  path-width"; avoid repeating §3.3's challenge story there.
- Item 07/08: Figure files are still named `sec2_fig*` (now Figure 3.1 and
  C.1); `sec2_fig3_citation_network.pdf` is unused by the paper. Appendix
  order is A, B, C with C the bibliometrics; if item 05 restructures B, keep
  `app:names`.
- The section title is "The names and the communities"; the intro's "How to
  read" sentence still matches.
