# Paper 2, "The pathwidth complex": the LaTeX draft

First full draft, Ralph loop0008 item 08, 2026-10-03; item 09 added Figure 3.1 and
the axiom audit. **25 pages** (article
class, 11 pt, one column, US letter, 1 in margins), no undefined references or
citations, no overfull boxes.

```bash
cd paper2/latex
make            # latexmk -pdf -> main.pdf
make check      # fails on any undefined reference; prints the page count
make tables     # regenerate tables/*.tex from the recorded CSVs (python -m paper2.latex.make_tables)
make refs       # check every DOI of refs.bib against Crossref / DataCite (python -m paper2.latex.check_refs)
make axioms     # every theorem the draft cites has a #print axioms line in paper2/axiom_check.lean,
                # and all are propext / Classical.choice / Quot.sound (python -m paper2.latex.check_axioms)
python -m paper2.latex.check_lean      # every Lean name the draft cites is declared (run from the repo root)
python -m pytest tests/test_paper2_latex.py -q
```

## Files

| file | content | drafted from |
|---|---|---|
| `main.tex` | preamble, title, draft abstract | `../plan.md` |
| `sec1_intro.tex` | **placeholder**: waits on the owner's thesis; draft contribution list, notation | `../plan.md` §1 |
| `sec2_names.tex` | method, Table 2.1, Figures 2.1–2.3 | `../popularity.md`, "For the paper" |
| `sec3_equivalences.tex` | the problems, Table 3.1 (master table), Figure 3.1 (`../figures/sec3_fig1_chain.pdf`, `python -m paper2.section3_figure`), theorems with proofs of the core, bands, false rows, edge cases, the Kirousis & Papadimitriou gap, pebbling | `../problem_transformations.md`, `../equivalences.md`, `../proof_reductions.md` |
| `sec4_search.tex` | the search, Counterexample 4.4 with **Figure 4.1**, the repair, the other rules, the soundness theorem, the pathwidth reading, prior reports, cost, re-certification, certificates, the dataset | `../revised_algorithm.md`, `../solver_fix.md`, `../prior_art_counterexample.md`, `../certificates.md`, `../dataset.md` |
| `sec5_closing.tex` | **placeholder**: written last | `../plan.md` §5 |
| `refs.bib` | `../table1.bib` (notes dropped) and every other work cited | checked by `check_refs.py` |
| `tables/*.tex` | generated, do not edit | `make_tables.py` |
| `data/doi_check.json` | Crossref / DataCite responses, fetched 2026-10-03 | `check_refs.py` |

Every theorem carries its Lean names in a footnote (`\lean{...}`); figures are
the PDFs in `../figures/`, unchanged.

## Tables and where their numbers come from

| table | source | regenerated |
|---|---|---|
| 2.1 name usage | `paper2.section2_figures.numbers()`, OpenAlex caches of 2026-09-29 | offline |
| 4.3 cost of the repair | `../data/solver_fix_cost_{mosp40,cs,cs125,pw}.csv` | reproduces `revised_algorithm.md` §4.6.2 exactly |
| 4.4 re-certification | `../data/solver_fix_split_{tasks,results}.csv`, **read at build time of the tables** | changes while the split run is in flight; rerun `make tables` on the day |
| 4.5 certificates | `../data/certificates/repaired.csv` | reproduces `certificates.md` §3 |
| 4.6 dataset | `../data/dataset/{index,classes}.csv.gz` | reproduces `data/dataset/tables.md` |
| 3.1, 4.1, 4.2 | written from the documents named above | by hand |

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
  redrawn for print by `python -m paper2.section3_figure` (463.7 pt wide, no
  text below 7 pt, relations without Lean names). The working figure
  `../figures/equivalence_chain.pdf`, with every Lean name, is unchanged.
