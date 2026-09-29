# paper2 — the mathematics of MOSP

A workspace for the mathematical side of the problem only: the equivalences, the
graph parameters, the bounds and the proofs. No solver code, no benchmarks, no
engineering. Those live in the rest of the repository.

## Contents

- `literature/` — source papers, named by their bracket number in Linhares &
  Yanasse (2002). `literature/MANIFEST.md` is the index and status record;
  `literature/SOURCES.txt` records where each file came from.
- `table1.bib` — BibTeX for Table 1's twelve references, keyed `LY2002ref<n>`.
- `citation_graph.py` — the citation network and popularity figures in
  `figures/`, from OpenAlex (cached in `data/`); discussed at the end of
  `popularity.md`.
- `popularity.md` — the full popularity measurement: method, the contaminated
  raw counts that were discarded, and the caveats. The table itself is
  reproduced under Step 2 below.

## Step 1 (done): the Table 1 corpus

Table 1 of Linhares & Yanasse (2002) lists twelve problems across operations
research, VLSI design and graph theory and asserts they are equivalent up to ±1.
It cites fourteen bracket numbers, but two references are repeated ([6] for both
gate matrix layout and PLA folding, [13] for both path-width and vertex
separation), so the table rests on **twelve distinct papers**.

Eleven of the twelve are now held in `literature/` (Möhring only as a two-page preview); one could not be obtained
from any open source. The full breakdown, including why each of the seven
failed and what route to try next, is in `literature/MANIFEST.md`.

Held:

| Ref | Paper | Role in Table 1 |
|---|---|---|
| [4] | Fink & Voss 1999 | MOSP |
| [9] | Kirousis & Papadimitriou 1985 | node search game |
| [10] | Kirousis & Papadimitriou 1986 | edge search game |
| [11] | Kornai & Tuza 1992 | narrowness |
| [12] | Fomin 1998 | split bandwidth |
| [13] | Kinnersley 1992 | path-width, vertex separation (obtained 2026-09-27) |
| [1] | Yanasse 1997 | MOSP (obtained 2026-09-27) |
| [6] | Möhring 1990 | gate matrix layout, PLA folding (two-page preview only, 2026-09-27) |
| [7] | Ohtsuki et al. 1979 | one-dimensional logic (obtained 2026-09-27) |
| [8] | Wing, Huang & Wang 1985 | gate matrix layout (obtained 2026-09-27) |
| [14] | Lengauer 1981 | edge separation (obtained 2026-09-27) |

Missing, with the role Table 1 gives each:

| Ref | Reference | Role | Why not held |
|---|---|---|---|
| [5] | Kashiwabara, T. & Fujisawa, T. (1979). NP-completeness of the problem of finding a minimum clique number interval graph containing a given graph as a subgraph. *Proc. 1979 IEEE ISCAS*, Tokyo, 657–660. No DOI | interval thickness | 1979 proceedings, never digitised |
| [6] | Möhring, R.H. (1990). Graph problems related to gate matrix layout and PLA folding. In *Computational Graph Theory*, Computing Supplementum 7, Springer Wien, 17–51. DOI 10.1007/978-3-7091-9076-0_2 | gate matrix layout, PLA folding | only the two-page preview held; full chapter still wanted |

[9] has since been obtained exactly that way — it was never paywalled, only
blocked to non-browser clients, and opening the DOI in a browser fetched it.
That leaves the seven above, all of which are real paywalls or undigitised
material rather than access-mechanism problems.

The same seven are recorded in the repository-wide registry at
`../literature/MISSING.md`, cross-referenced by bracket number.

The two papers carrying the most weight for this project are both in hand.
[9] Kirousis & Papadimitriou 1985, the interval-thickness = node-search-number
link, and, since 2026-09-27, [13] Kinnersley, the vertex-separation = pathwidth
theorem: its Theorem 3.1 is proved by exactly the two constructions the Lean
formalization uses, so `VSEquivPW.lean` formalises the published proof and not
a secondary statement. With Fellows & Langston 1989 (Theorem 7) and 1987
(Lemma 4.1), also obtained that day, every link from open stacks to pathwidth
is a held paper; see `literature/MANIFEST.md`, "Beyond Table 1".

## Step 2 (done): how popular is each of the twelve problems?

Measured against OpenAlex, 2026-09-17, and corrected 2026-09-29 after a
relevance check showed most search hits for several names were about something
else. Two measures, because they disagree sharply: works about the problem
that use its *name* in title or abstract (restricted to computer science,
mathematics, engineering and decision sciences), and citations of the Table 1
paper attached to that problem. Method, the correction and the caveats are in
`popularity.md`, with figures on citations and on growth over the decades.

| Problem | Relevant works using the name | Table 1 ref | Citations of that paper |
|---|---:|---|---:|
| Graph path-width | **1,213** | [13] Kinnersley 1992 | 215 |
| Gate matrix layout | 110 | [6] Möhring 1990 / [8] Wing et al. 1985 | 134 / 89 |
| PLA folding | 68 | [6] Möhring 1990 | 134 |
| MOSP | 58 | [1] Yanasse 1997 / [4] Fink & Voss 1999 | 74 / 71 |
| Vertex separation | 55 | [13] Kinnersley 1992 | 215 |
| Edge search game | 38 | [10] Kirousis & Papadimitriou 1986 | **294** |
| Node search game | 34 | [9] Kirousis & Papadimitriou 1985 | 124 |
| One-dimensional logic | 11 | [7] Ohtsuki et al. 1979 | 107 |
| Interval thickness | 6 | [5] Kashiwabara & Fujisawa 1979 | not indexed |
| Narrowness | 0 | [11] Kornai & Tuza 1992 | 44 |
| Split bandwidth | 0 | [12] Fomin 1998 | 19 |
| Edge separation | 0 | [14] Lengauer 1981 | 77 |

For scale, outside Table 1: **treewidth** 6,222 works, **bandwidth
minimization** 306.

Four things worth carrying into the mathematics:

- **Pathwidth has absorbed the family** — 1,213 relevant works, 21× MOSP,
  more than three times the other eleven names combined, and the only name
  still growing. Whatever is known about this equivalence class was most
  likely published under "pathwidth", not under any other name here.
- **Citations do not track name usage.** Kirousis & Papadimitriou 1986 is the
  most-cited paper in the table (294) while only 38 works use "edge search
  game" in its sense; it is cited as a foundational graph-searching result,
  not as a problem people work on. Ohtsuki et al. 1979 is starker: 107
  citations against 11 works using "one-dimensional logic".
- **MOSP is one of the better-used names**, fourth of twelve, ahead of vertex
  separation and both search games. (The uncorrected counts said the opposite.)
- **Three names are not in use at all**: narrowness, split bandwidth and edge
  separation have no relevant works. Split bandwidth is Fomin's own coinage in
  the paper Table 1 cites, has 19 citations, and was never adopted. Interval
  thickness (6) and one-dimensional logic (11) are nearly as rare.

Counts are lower bounds: a paper can work on pathwidth without putting the word
in its abstract, and OpenAlex's thin abstract coverage of older material biases
against exactly the 1979–85 VLSI entries. `popularity.md` records which raw
counts were discarded as contaminated and why.

## A caution carried over from the main project

The repository's `CLAUDE.md` records that the MOSP graph (nodes = item types,
`M @ M^T`) and the pattern connection graph (nodes = patterns, `M^T @ M`) were
swapped here for a while, and that the pathwidth equivalence concerns the first.
Table 1's equivalences are stated at the level of problems, not of a particular
graph construction, so re-deriving each one explicitly — saying which graph,
and which ±1 — is the natural first piece of mathematics to do here.
