# paper2 — the mathematics of MOSP

A workspace for the mathematical side of the problem only: the equivalences, the
graph parameters, the bounds and the proofs. No solver code, no benchmarks, no
engineering. Those live in the rest of the repository.

## Contents

- `literature/` — source papers, named by their bracket number in Linhares &
  Yanasse (2002). `literature/MANIFEST.md` is the index and status record;
  `literature/SOURCES.txt` records where each file came from.
- `table1.bib` — BibTeX for Table 1's twelve references, keyed `LY2002ref<n>`.

## Step 1 (done): the Table 1 corpus

Table 1 of Linhares & Yanasse (2002) lists twelve problems across operations
research, VLSI design and graph theory and asserts they are equivalent up to ±1.
It cites fourteen bracket numbers, but two references are repeated ([6] for both
gate matrix layout and PLA folding, [13] for both path-width and vertex
separation), so the table rests on **twelve distinct papers**.

Five of the twelve are now held in `literature/`; seven could not be obtained
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

Missing, with the role Table 1 gives each:

| Ref | Reference | Role | Why not held |
|---|---|---|---|
| [1] | Yanasse, H.H. (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *EJOR* 100(3), 454–463. DOI 10.1016/S0377-2217(97)84107-0 | MOSP | Elsevier paywall |
| [5] | Kashiwabara, T. & Fujisawa, T. (1979). NP-completeness of the problem of finding a minimum clique number interval graph containing a given graph as a subgraph. *Proc. 1979 IEEE ISCAS*, Tokyo, 657–660. No DOI | interval thickness | 1979 proceedings, never digitised |
| [6] | Möhring, R.H. (1990). Graph problems related to gate matrix layout and PLA folding. In *Computational Graph Theory*, Computing Supplementum 7, Springer Wien, 17–51. DOI 10.1007/978-3-7091-9076-0_2 | gate matrix layout, PLA folding | Springer paywall; author pages retired |
| [7] | Ohtsuki, T., Mori, H., Kuh, E.S., Kashiwabara, T. & Fujisawa, T. (1979). One-dimensional logic gate assignment and interval graphs. *IEEE TCAS* 26(9), 675–684. DOI 10.1109/TCS.1979.1084695 | one-dimensional logic | IEEE paywall |
| [8] | Wing, O., Huang, S. & Wang, R. (1985). Gate matrix layout. *IEEE TCAD* 4(3), 220–231. DOI 10.1109/TCAD.1985.1270118 | gate matrix layout | IEEE paywall |
| [13] | Kinnersley, N.G. (1992). The vertex separation number of a graph equals its path-width. *IPL* 42(6), 345–350. DOI 10.1016/0020-0190(92)90234-M | path-width, vertex separation | Elsevier paywall |
| [14] | Lengauer, T. (1981). Black-white pebbles and graph separation. *Acta Informatica* 16(4), 465–475. DOI 10.1007/BF00264496 | edge separation | Springer paywall |

[9] has since been obtained exactly that way — it was never paywalled, only
blocked to non-browser clients, and opening the DOI in a browser fetched it.
That leaves the seven above, all of which are real paywalls or undigitised
material rather than access-mechanism problems.

The same seven are recorded in the repository-wide registry at
`../literature/MISSING.md`, cross-referenced by bracket number.

Of the two papers carrying the most weight for this project, one is now in
hand and one is not. [9] Kirousis & Papadimitriou 1985, the interval-thickness =
node-search-number link, is held. [13] Kinnersley, the vertex-separation =
pathwidth theorem the Lean formalization proves, is still missing, and we
continue to work from secondary statements of it.

## A caution carried over from the main project

The repository's `CLAUDE.md` records that the MOSP graph (nodes = item types,
`M @ M^T`) and the pattern connection graph (nodes = patterns, `M^T @ M`) were
swapped here for a while, and that the pathwidth equivalence concerns the first.
Table 1's equivalences are stated at the level of problems, not of a particular
graph construction, so re-deriving each one explicitly — saying which graph,
and which ±1 — is the natural first piece of mathematics to do here.
