# The sources of Section 9 (related work and context)

Fetched by loop0015 item 08 on 2026-11-05 (05:59 UTC) with `curl`, into
`fetched/`, and never executed, imported or rendered: they are read with
`open()` by `paper3/scripts/related_work.py` and with `cat`/`grep` only.
They are the only downloads item 08 made, and they are exactly the three
`TASK.md` allows it (the arXiv abstract page of 2608.14673, the comparator
README, the nanoda README), plus the public metadata records that give
each repository's latest commit and the arXiv record's version dates.

| file | what | URL fetched |
|---|---|---|
| `arxiv_2608.14673_api.xml` | arXiv API record of 2608.14673 (v3): title, authors, abstract, dates, classes, comment | `https://export.arxiv.org/api/query?id_list=2608.14673` |
| `arxiv_2608.14673_abs.html` | the abstract page (for the three version dates) | `https://arxiv.org/abs/2608.14673v3` |
| `comparator_README_master.md` | README of `leanprover/comparator`, `master` branch (208 lines) | `https://raw.githubusercontent.com/leanprover/comparator/master/README.md` |
| `comparator_repo.json` | GitHub API record of the repository (archived, Apache-2.0, pushed 2026-10-14) | `https://api.github.com/repos/leanprover/comparator` |
| `comparator_commits.json` | its latest commit: `865edc14`, 2026-10-14, "doc: migration notice" | `https://api.github.com/repos/leanprover/comparator/commits?per_page=1` |
| `nanoda_README_master.md` | README of `ammkrn/nanoda_lib`, `master` branch (85 lines) | `https://raw.githubusercontent.com/ammkrn/nanoda_lib/master/README.md` |
| `nanoda_repo.json` | GitHub API record (description, Apache-2.0, pushed 2026-10-29) | `https://api.github.com/repos/ammkrn/nanoda_lib` |
| `nanoda_commits.json` | its latest commit: `8de7e0c4`, 2026-10-29 — the commit the replay (item 01) built | `https://api.github.com/repos/ammkrn/nanoda_lib/commits?per_page=1` |

The `main` branch of neither repository exists (`curl -f` on
`.../main/README.md` returned 404 for both); `master` is the default
branch of both, as the API records say.

SHA-256 of every file is printed by `python3 -I paper3/scripts/related_work.py`
and the first twelve hex digits are in the paper's Table 9.1
(`paper3/latex/tables/related_sources.tex`). The script also checks every
sentence Section 9 quotes against the line it cites, in these files, in
the clone at `4eaee875` (`history.md` line 18, `lean/docs/378.md` lines
9/11/17, `lean/ComparatorChallenges/README.md` lines 1/3/9,
`SubexponentialSAT.json`), and in the manuscript extract
(`reports/scratch/eth_audit/paper.txt` lines 170–171 and 3733–3736).

Not fetched, by the download rule: the body of arXiv 2608.14673, the
`lean4export` and `landrun` pages, the book linked from the nanoda README,
any Crossref record, anything from the working group named in
`history.md`, any press report.
