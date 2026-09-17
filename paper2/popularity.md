# How popular is each of the twelve equivalent problems?

Measured 2026-09-17 against OpenAlex. Two different questions get two different
answers, and they disagree sharply, so both are given.

- **Problem literature** — works whose *title or abstract* uses the problem's
  name, restricted to Computer Science, Mathematics, Engineering and Decision
  Sciences. This measures how alive the *name* is.
- **Defining paper citations** — `cited_by_count` for the Table 1 reference that
  Linhares & Yanasse attach to that problem. This measures how much the
  *result* is used, which is not the same thing.

| Problem | Works using the name | Table 1 ref | Citations of that paper |
|---|---:|---|---:|
| Graph path-width | **1,609** | [13] Kinnersley 1992 | 215 |
| Node search game | 127 | [9] Kirousis & Papadimitriou 1985 | 124 |
| Gate matrix layout | 126 | [6] Möhring 1990 / [8] Wing et al. 1985 | 134 / 89 |
| Vertex separation | 105 | [13] Kinnersley 1992 | 215 |
| Edge search game | 94 | [10] Kirousis & Papadimitriou 1986 | **294** |
| PLA folding | 74 | [6] Möhring 1990 | 134 |
| MOSP | 60 | [1] Yanasse 1997 / [4] Fink & Voss 1999 | 74 / 71 |
| Narrowness | 35 | [11] Kornai & Tuza 1992 | 44 |
| Split bandwidth | 35 | [12] Fomin 1998 | 19 |
| Edge separation | 22 | [14] Lengauer 1981 | 77 |
| One-dimensional logic | 18 | [7] Ohtsuki et al. 1979 | 107 |
| Interval thickness | 10 | [5] Kashiwabara & Fujisawa 1979 | not indexed |

For scale, outside Table 1: **treewidth** 6,222 works; **bandwidth
minimization** 306.

## What the numbers say

**Pathwidth has absorbed the whole family.** At 1,609 works it is 27× MOSP and
larger than the other eleven names put together. Anything we want to know about
algorithms for this equivalence class was most likely published under
"pathwidth", not under any of the other eleven names. Its sibling treewidth is
another 4× larger again.

**Citation counts do not track name usage, and the gap is informative.**
Kirousis & Papadimitriou 1986 is the most-cited paper in the table (294) while
"edge search game" is only the fifth most-used name (94). The paper is cited as
a foundational graph-searching result, not because people are working on the
edge search game as such. The same split is starker for Ohtsuki et al. 1979:
107 citations against 18 works using "one-dimensional logic" — it is cited for
its interval-graph characterisation, and the problem name died with the
technology.

**Four of the twelve names are effectively dead.** Interval thickness (10),
one-dimensional logic (18), edge separation (22) and split bandwidth (35).
Split bandwidth is the sharpest case: it is Fomin's own coinage in the very
paper Table 1 cites, it has 19 citations, and nobody adopted it. Edge
separation in Lengauer's pebbling sense returns **zero** works — the phrase
survives in the literature only as aerodynamics ("leading-edge separation").

**MOSP is smaller than most of its own synonyms.** At 60 works it sits below
node search, gate matrix layout, vertex separation, edge search and PLA folding.
The operations-research community working on this problem is a minority of the
people working on the equivalence class.

**Kashiwabara & Fujisawa 1979 has no OpenAlex record at all**, so no citation
count exists for it. That is the same fact that made it undownloadable: a 1979
ISCAS proceedings paper that was never digitised is invisible to modern
bibliometrics, whatever its actual influence.

## Method and its limits

Counts come from OpenAlex `title_and_abstract.search` with
`primary_topic.field.id` restricted to fields 17, 26, 22 and 18. Raw unrestricted
counts are useless for several of these terms and were discarded after
inspecting sample titles:

| Term | Raw count | What it was actually counting |
|---|---:|---|
| "narrowness" | 1,109,296 | "narrow" in physics, optics, medicine |
| "edge separation" | 1,755 | trailing- and leading-edge separation in aerodynamics |
| "open stacks" | 601 | includes OpenStack, the cloud platform |
| "interval thickness" | 152 | includes petroleum-reservoir stratigraphy |

The tightened queries are in this repository's session record; each was checked
by sampling returned titles. Remaining caveats:

- **These are lower bounds.** A paper can work on pathwidth without putting the
  word in its abstract, and OpenAlex abstract coverage is incomplete for older
  material — which biases against exactly the 1979–1985 VLSI papers here.
- **"Narrowness" at 35** uses the phrase "narrowness of a graph"; the looser
  `"narrowness" AND "graph"` gives 2,981, almost all spurious. Treat 35 as the
  honest figure and note that only 7 works pair "narrowness" with "pathwidth".
- **Gate matrix layout and PLA folding overlap**, since Möhring [6] is Table 1's
  reference for both.
- Citation counts are OpenAlex's, which run lower than Google Scholar's.
