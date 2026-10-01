# paper2 — the mathematics of MOSP

The workspace for the second paper, *The pathwidth complex* (`plan.md`): the
equivalences of Table 1, the graph parameters, the bounds and the proofs, the
popularity measurement, and the catalogue of benchmark collections for the
dataset. No solver code: the MOSP solver lives in the rest of the repository,
the graph pathwidth solver in `../pathwidth_solver/`.

## Contents

- `plan.md` — the plan for the paper, *The pathwidth complex*: five sections,
  what each argues, what exists, what is still to do, the decisions taken
  (venue: INFORMS Journal on Computing first) and the remaining work in order.
- `problem_transformations.md` — section 3 in paper form: each Table 1 problem
  as Instance / Question, then the transformations from equalities to bands to
  what is unproved or false, with sources and Lean names.
- `revised_algorithm.md` — section 4 in paper form: the customer search, its
  rules, the repaired Theorems 1 and 2, and the soundness theorem.
- `proof_reductions.md` — faults found in published proofs of the reductions,
  with the corrected arguments (first: Kirousis & Papadimitriou 1986, Thm 4.1).
- `equivalences.md` — section 3: the master table of the twelve Table 1
  problems (relation to pathwidth, Lean theorem, status), the chain figure
  (`figures/equivalence_chain.{dot,pdf,png}`), the gap and sorry inventory,
  and the per-item record of Ralph loop0005.
- `complex_check.py` — brute-force checker for every section-3 statement
  (`python -m paper2.complex_check`; tests in `tests/test_complex_check.py`).
- `axiom_check.lean` — `#print axioms` on every theorem section 3 names
  (`cd lean && lake env lean ../paper2/axiom_check.lean`).
- `lean_repo_plan.md` — which Lean files move to the paper's own repository,
  in what order, and what they need from `lean/MOSPFormalization/`.
- `literature/` — source papers, named by their bracket number in Linhares &
  Yanasse (2002). `literature/MANIFEST.md` is the index and status record;
  `literature/SOURCES.txt` records where each file came from.
- `table1.bib` — BibTeX for Table 1's twelve references, keyed `LY2002ref<n>`.
- `popularity.md` — the full popularity measurement: method, the contaminated
  raw counts that were discarded, and the caveats. The table itself is
  reproduced under Step 2 below.
- `citation_graph.py` — the citation network and popularity figures, from
  OpenAlex (`python -m paper2.citation_graph`); discussed at the end of
  `popularity.md`.
- `trends.py` — growth and decline of each name, and citers by decade
  (`python -m paper2.trends`).
- `relevance.py` — the relevance filter behind the 2026-09-29 correction of
  the name counts (`python -m paper2.relevance`).
- `figures/` — the popularity and trend figures and the equivalence chain.
- `data/` — the OpenAlex caches, the relevance labels, and
  `complex_check.json`, the brute-force check's output.
- `benchmarks/` — the benchmark hunt for section 4, restricted to the
  problems proved exactly equivalent: `README.md` is the catalogue, with
  `hunt_graphs.md`, `hunt_matrix.md` and `hunt_citers.md` behind it; downloads
  go to `benchmarks/raw/`, which is git-ignored.

## Step 1 (done): the Table 1 corpus

Table 1 of Linhares & Yanasse (2002) lists twelve problems across operations
research, VLSI design and graph theory and asserts they are equivalent up to ±1.
It cites fourteen bracket numbers, but two references are repeated ([6] for both
gate matrix layout and PLA folding, [13] for both path-width and vertex
separation), so the table rests on **twelve distinct papers**.

Eleven of the twelve are now held in `literature/`, Möhring (1990) as the
full 35-page chapter; one, Kashiwabara & Fujisawa (1979), could not be
obtained from any source. The full breakdown, and the route still worth
trying for [5], is in `literature/MANIFEST.md`.

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
| [6] | Möhring 1990 | gate matrix layout, PLA folding (full 35-page chapter, obtained 2026-09-27) |
| [7] | Ohtsuki et al. 1979 | one-dimensional logic (obtained 2026-09-27) |
| [8] | Wing, Huang & Wang 1985 | gate matrix layout (obtained 2026-09-27) |
| [14] | Lengauer 1981 | edge separation (obtained 2026-09-27) |

Missing, with the role Table 1 gives it:

| Ref | Reference | Role | Why not held |
|---|---|---|---|
| [5] | Kashiwabara, T. & Fujisawa, T. (1979). NP-completeness of the problem of finding a minimum clique number interval graph containing a given graph as a subgraph. *Proc. 1979 IEEE ISCAS*, Tokyo, 657–660. No DOI | interval thickness | 1979 proceedings, never digitised |

Of the seven once missing, [9] was obtained by opening the DOI in a browser
(it was never paywalled, only blocked to non-browser clients), five were sent
by H. Yanasse on 2026-09-27, and Möhring's chapter was extracted from the book
the same day. [5] is undigitised 1979 proceedings.

The repository-wide registry `../literature/MISSING.md` records the same
history, cross-referenced by bracket number.

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

## Step 3 (done, 2026-09-30, Ralph loop0005): the equivalences, proved

Every Table 1 row is settled and proved in Lean
(`../lean/MOSPFormalization/Complex/`, 13 files; axioms `propext`,
`Classical.choice` and `Quot.sound` only, `axiom_check.lean`). Seven problems
equal pathwidth or pathwidth + 1, split bandwidth and edge search are bands,
and simple PLA folding and edge separation (read as cutwidth) are false as
Table 1 states them. The one named gap, LaPaugh's `es = pes`, is used by no
row. The paper form is `problem_transformations.md`, the evidence
`equivalences.md`, faults in published proofs `proof_reductions.md`.

## What remains

The benchmark hunt is done (`benchmarks/README.md`). What is left — the
thesis, the paper's figures, the dominance rules as layout lemmas, the
dataset run, the draft, and last the paper's own repository — is listed in
order under *Remaining work* in `plan.md`.

## A caution carried over from the main project

The repository's `CLAUDE.md` records that the MOSP graph (nodes = item types,
`M @ M^T`) and the pattern connection graph (nodes = patterns, `M^T @ M`) were
swapped here for a while, and that the pathwidth equivalence concerns the first.
Table 1's equivalences are stated at the level of problems, not of a particular
graph construction, so re-deriving each one explicitly — saying which graph,
and which ±1 — was the first piece of mathematics done here (Step 3; for MOSP
the graph is the MOSP graph, `MOSPGraph.lean`, and the statement over the
pattern graph is false, `MOSPGraphExamples.lean`).
