# loop0009 progress

Plan: revise paper 2's draft (`paper2/latex/`) for readability, following
`paper2/review_readability.md` and the owner's notes in `TASK.md`. Items are
in `iterations.md`. Gate: `python3 Ralph_Loops/loop0009/gate.py`. It includes
`make -C paper2/latex check`.

Current: 1/11 SOLVED

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
