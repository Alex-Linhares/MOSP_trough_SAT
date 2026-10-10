# *The pathwidth complex*: the LaTeX draft

First full draft, Ralph loop0008 item 08, 2026-10-03; item 09 added Figure 3.1 and
the axiom audit. **25 pages** (article
class, 11 pt, one column, US letter, 1 in margins), no undefined references or
citations, no overfull boxes.

```bash
cd paper1/latex
make            # latexmk -pdf -> main.pdf
make check      # fails on any undefined reference; prints the page count
make tables     # regenerate tables/*.tex from the recorded CSVs (python -m paper1.latex.make_tables)
make refs       # check every DOI of refs.bib against Crossref / DataCite (python -m paper1.latex.check_refs)
make axioms     # every theorem the draft cites has a #print axioms line in paper1/axiom_check.lean,
                # and all are propext / Classical.choice / Quot.sound (python -m paper1.latex.check_axioms)
python -m paper1.latex.check_lean      # every Lean name the draft cites is declared (run from the repo root)
python -m pytest tests/test_paper1_latex.py -q
```

## Files

| file | content | drafted from |
|---|---|---|
| `main.tex` | preamble, title, draft abstract | `../plan.md` |
| `sec1_intro.tex` | 1 Introduction: MOSP, Table 1.1 (the Linhares–Yanasse table), how it came to be, contributions, notation | the first author's thesis; `../plan.md` §1 |
| `sec2_equivalences.tex` | 2 The equivalences (was §3): the problems, Table 2.1 (master table), Figure 2.1 (`../figures/sec3_fig1_chain.pdf`, `python -m paper1.section3_figure`), theorems of the core, bands, false rows | `../problem_transformations.md`, `../equivalences.md`, `../proof_reductions.md` |
| `sec3_names.tex` | 3 The names and the communities (was §2; cut to two pages in loop0009 item 04): one method paragraph, Figure 3.1 (name usage), Table 3.1 (works per period), Table 3.2 (citing works by discipline; replaces the citation-network figure), the 2005 challenge and the graph-benchmark comparison | `../popularity.md`, "For the paper"; Chu & Stuckey (2009) §1; `../solver_fix.md` "Table 1: proved widths" |
| `sec4_search.tex` | 4 The search read as a pathwidth algorithm (was §4.1–4.5): Counterexample 4.4 with **Figure 4.1**, the repair, the other rules, the soundness theorem, the pathwidth reading, prior reports | `../revised_algorithm.md`, `../search_soundness.md`, `../prior_art_counterexample.md` |
| `sec5_results.tex` | 5 Computational results and a dataset (was §4.6–4.7): 5.1 setup (machine, runs, configurations *base* / *with better move* = `default` / `csearch`, corpus, provenance), 5.2 cost and re-certification, 5.3 certificates, 5.4 the dataset | `../solver_fix.md`, `../certificates.md`, `../dataset.md` |
| `sec6_conclusion.tex` | 6 Conclusion: **placeholder**, written last | `../plan.md` §5 |
| `sec7_data.tex` | Data, code and proofs statement (unnumbered); a comment lists the regenerate commands the body used to carry | — |
| `sec9a_appendix_lean.tex` | Appendix A, formal names: one entry per result, `\leanentry{key}{result} \leannames{...}`; the text cites it with `\leanref{key}` | the old `\lean{...}` footnotes |
| `sec9c_appendix_names.tex` | Appendix C, the bibliometric study: method in full, robustness, Table C.1 (names and citations), Figure C.1 (timeline) | `../popularity.md` |
| `sec9b_appendix_machinery.tex` | Appendix B, supporting material: edge cases and the Kirousis–Papadimitriou gap (old §3.3), the thirteenth member (old §3.4), why the published proof fails, the minimality search, Proposition B.1 and Theorem B.2 (old 4.8, 4.9), the split re-certification (Table B.1, was Table 5.2) | as for §2 and §4 |
| `refs.bib` | `../table1.bib` (notes dropped) and every other work cited | checked by `check_refs.py` |
| `tables/*.tex` | generated, do not edit | `make_tables.py` |
| `data/doi_check.json` | Crossref / DataCite responses, fetched 2026-10-03 | `check_refs.py` |

Since loop0009 item 01 the Lean names are in Appendix A, not in footnotes; the
text cites an entry with `\leanref{key}`, and `check_lean.py` / `check_axioms.py`
read the `\leannames{...}` cells. Figures are the PDFs in `../figures/`.

## Tables and where their numbers come from

| table | source | regenerated |
|---|---|---|
| 3.1 works per period | `paper1.section2_figures.numbers()["periods_2005_24"]` (`paper1.trends.binned`) | offline |
| 3.2 citing works by discipline | `paper1.section2_figures.numbers()["discipline_sets"]`, citation cache of 2026-09-29 | offline |
| C.1 name usage | `paper1.section2_figures.numbers()`, OpenAlex caches of 2026-09-29 | offline |
| 5.1 cost of the repair (MOSP and graph parts) | `../data/solver_fix_cost_{mosp40,cs,cs125,pw}.csv` | reproduces `revised_algorithm.md` §4.6.2 exactly |
| B.1 split re-certification (was 5.2; rule before the two never-certified values) | `../data/solver_fix_split_{tasks,results}.csv`, **read at build time of the tables** | changes while the split run is in flight; rerun `make tables` on the day |
| 5.2 certificates | `../data/certificates/repaired.csv` | seven columns, `csearch` only; both configurations' totals in trailing comments, reproducing `certificates.md` §3 |
| 5.3 dataset | `../data/dataset/{index,classes}.csv.gz` | reproduces `data/dataset/tables.md` |
| 2.1, 4.1, 4.2, A.1 | written from the documents named above | by hand |

## The template: to obtain

The INFORMS Journal on Computing LaTeX class was **not obtained**. On
2026-10-03 every INFORMS author page tried refused scripted access with HTTP
403 (`pubsonline.informs.org/page/ijoc/submission-guidelines`,
`pubsonline.informs.org/authorportal/latex-style-files`,
`www.informs.org/Publications/Author-Portal/LaTeX-Style-Files`), and so did a
fetch through the web tool. The journal's formatting rules could not be read
either, so the layout here is a stand-in, not the journal's stated rules. To
do by hand: download the class from the INFORMS author portal, then switch
`\documentclass` and the bibliography style (`plainnat` here, author-year).
What was reachable: the journal's software-and-data repository template,
`https://github.com/INFORMSJoC/2019.0000` (fetched 2026-10-03), which is the
model for the paper's own repository (`../plan.md`, *Decisions*).

## Known limits of the draft

- Sections 1 and 5 are placeholders, as the item asks.
- Table 4.4 is a snapshot: three of its seven re-certifications are in flight
  until 2026-10-08. Rerun `make tables && make` before quoting it.
- *(Fixed in item 09.)* natbib breaks ties between same-author, same-year
  entries by cite key, so the EJOR paper's key is `Yanasse1997b` (table1.bib's
  `LY2002ref1`), and the labels now match the project's: *Pesquisa Operacional*
  1997a, EJOR 1997b.
- Not held, cited for statements recorded in `../equivalences.md`: Bienstock &
  Seymour (1991), LaPaugh (1993). Kashiwabara & Fujisawa (1979) is not held and
  has no DOI. The deficiency form of Hall's theorem is used without a citation
  (Ore 1955 is not held).
- *(Fixed in item 09.)* The equivalence chain is in the draft as Figure 3.1,
  redrawn for print by `python -m paper1.section3_figure` (463.7 pt wide, no
  text below 7 pt, relations without Lean names). The working figure
  `../figures/equivalence_chain.pdf`, with every Lean name, is unchanged.
