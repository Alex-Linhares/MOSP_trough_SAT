# How popular is each of the twelve equivalent problems?

First measured 2026-09-17 against OpenAlex; **corrected 2026-09-29**, when a
check of the search results showed that for several names most hits were about
something else (see *Correction* below). Two different questions get two
different answers, and they disagree sharply, so both are given.

- **Problem literature** — works about the problem that use its *name* in
  title or abstract, restricted to Computer Science, Mathematics, Engineering
  and Decision Sciences. This measures how alive the *name* is.
  The restriction to those four fields is there because several of these
  names are ordinary words or phrases that other fields use for something
  else. Unrestricted, "narrowness" returns over a million works, mostly
  physics, optics and medicine; "edge separation" returns aerodynamics papers
  on leading- and trailing-edge flow separation; "open stacks" picks up
  OpenStack, the cloud platform; and "interval thickness" picks up petroleum
  geology. The full list, with the raw counts, is under *Method and its
  limits* below. Even inside the four fields the searches catch other senses
  of the words, so every hit was then checked for relevance.
- **Defining paper citations** — `cited_by_count` for the Table 1 reference that
  Linhares & Yanasse attach to that problem. This measures how much the
  *result* is used, which is not the same thing.

| Problem | Relevant works using the name | (search hits) | Table 1 ref | Citations of that paper |
|---|---:|---:|---|---:|
| Graph path-width | **1,213** | 1,571 | [13] Kinnersley 1992 | 215 |
| Gate matrix layout | 110 | 125 | [6] Möhring 1990 / [8] Wing et al. 1985 | 134 / 89 |
| PLA folding | 68 | 74 | [6] Möhring 1990 | 134 |
| MOSP | 58 | 60 | [1] Yanasse 1997 / [4] Fink & Voss 1999 | 74 / 71 |
| Vertex separation | 55 | 100 | [13] Kinnersley 1992 | 215 |
| Edge search game | 38 | 95 | [10] Kirousis & Papadimitriou 1986 | **294** |
| Node search game | 34 | 127 | [9] Kirousis & Papadimitriou 1985 | 124 |
| One-dimensional logic | 11 | 18 | [7] Ohtsuki et al. 1979 | 107 |
| Interval thickness | 6 | 10 | [5] Kashiwabara & Fujisawa 1979 | not indexed |
| Narrowness | **0** | 35 | [11] Kornai & Tuza 1992 | 44 |
| Split bandwidth | **0** | 35 | [12] Fomin 1998 | 19 |
| Edge separation | **0** | 21 | [14] Lengauer 1981 | 77 |

For scale, outside Table 1 and *not* relevance-checked: **treewidth** 6,222
search hits; **bandwidth minimization** 306.

## What the numbers say

**Pathwidth has absorbed the whole family.** At 1,213 relevant works it is 21×
MOSP and more than three times the other eleven names put together (380).
Anything we want to know about algorithms for this equivalence class was most
likely published under "pathwidth", not under any of the other eleven names.

**Three of the twelve names are not in use at all, and two more barely.**
Narrowness, split bandwidth and edge separation have **no** relevant works:
every search hit was about something else ("narrowing" in term rewriting,
radar interferometry and photonic beam splitters, graph drawing and flow
separation). Split bandwidth is Fomin's own coinage in the very paper Table 1
cites, and nobody adopted it. Interval thickness (6) and one-dimensional logic
(11) are nearly as rare.

**MOSP is one of the better-used names.** At 58 relevant works it ranks fourth
of twelve, behind pathwidth and the two VLSI layout names and ahead of vertex
separation and both search games. The first version of this report, from the
uncorrected counts, said the opposite; it was an artefact of searches that
inflated the graph-theory names with unrelated work.

**Citation counts do not track name usage, and the gap is informative.**
Kirousis & Papadimitriou 1986 is the most-cited paper in the table (294) while
only 38 works use "edge search game" in its sense. The paper is cited as a
foundational graph-searching result, not because people work on the edge
search game as such. The same split is starker for Ohtsuki et al. 1979: 107
citations against 11 works using "one-dimensional logic" — it is cited for its
interval-graph characterisation, and the problem name died with the
technology.

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

The tightened queries are now in the code (`QUERIES` in `paper2/trends.py`).
In the first version each was checked only by sampling a few returned titles,
which was not enough; see the correction below. Remaining caveats:

- **These are lower bounds.** A paper can work on pathwidth without putting the
  word in its abstract, and OpenAlex abstract coverage is incomplete for older
  material — which biases against exactly the 1979–1985 VLSI papers here.
- **The relevance check is a judgement.** The eleven smaller names were
  labelled work by work from title, topic, venue and abstract; pathwidth by a
  rule checked on samples of both what it keeps and what it drops, which errs
  by a few percent each way. Both are recorded (below) and can be re-examined.
- **Gate matrix layout and PLA folding overlap**, since Möhring [6] is Table 1's
  reference for both.
- Citation counts are OpenAlex's, which run lower than Google Scholar's.

## Correction, 2026-09-29

The first version of this report counted OpenAlex search hits as works using a
name. They are not. OpenAlex's `title_and_abstract.search` stems words and
ignores punctuation, so a quoted phrase matches far more than the phrase:

| Name | What the search also returned |
|---|---|
| narrowness | "narrowing" in term rewriting and functional logic programming; narrow-band graph cuts in image segmentation |
| split bandwidth | split-bandwidth radar interferometry; photonic crystal fibre beam splitters; speech coders |
| edge separation | edge cuts in graph drawing and network analysis; flow separation |
| node search game | node lookup in peer-to-peer networks and delay-tolerant networks; XML query processing |
| edge search game | edge detection in images; sensor-network data collection; robotics |
| vertex separation | vertex separators in the cut sense; control theory ("separation" of vertices in fuzzy systems) |
| path-width | physical path widths: roads, pedestrian routes, tool paths, vehicle steering; datapath widths |

So every hit was fetched with its title, abstract, topic and venue
(`paper2/relevance.py`, cache `paper2/data/openalex_candidates.json`) and
kept only if it is about the problem in the Table 1 sense. The eleven smaller
names were labelled work by work (700 works, labels in
`paper2/data/relevance_labels.json`); pathwidth, at 1,571 hits, by a rule
(`keep_pathwidth`) checked by reading samples on both sides. The corrected
counts are the table at the top. What changed in the conclusions: MOSP moves
from seventh to fourth; three names fall to zero rather than being merely
small; node search and edge search lose most of their counts; and pathwidth's
lead grows, from larger than the other eleven combined to more than three
times their total. The claim "four of the twelve names are effectively dead"
is replaced by the three-with-none, two-nearly statement above.

## Who cites whom (added 2026-09-29)

![Citation network of the Table 1 papers](figures/table1_citation_network.png)

![Name usage of the twelve problems](figures/table1_popularity.png)

![Name usage against citations of the defining paper](figures/table1_name_vs_citations.png)

The bar chart is on a linear scale on purpose: pathwidth's bar is more than
three times the other eleven put together, which is the first finding above.
The scatter puts the report's two measures against each other, using the
corrected counts. Above the diagonal, the paper Table 1 cites is cited more
often than the problem's name is used: the result is still in use but the
name is not. Nine of the eleven indexed problems sit there, including the
three whose names nobody uses (drawn at the left edge); edge search, with 294
citations against 38 works, and one-dimensional logic are furthest out.
Below the diagonal the name has outgrown its source paper, and only two
problems are there: pathwidth, far below, with about 5.6 works using the name
for every citation of Kinnersley (1992), and gate matrix layout, just below.
MOSP sits just above the line, with the name and the paper at similar counts.

Regenerate with `python -m paper2.citation_graph` (OpenAlex responses cached in
`paper2/data/openalex_citations.json`; `--refresh` re-fetches). The network
has the eleven indexed Table 1 papers plus Linhares & Yanasse (2002) itself on
a circle, coloured by the discipline Table 1 gives their problem, and the 844
distinct works citing them, coloured by OpenAlex field. Kashiwabara & Fujisawa
(1979) has no OpenAlex record and is absent.

- **The communities barely touch.** 269 of the 844 citing works cite two or
  more Table 1 papers, but almost all of those stay inside one discipline. 74
  span two disciplines, and 63 of those join graph theory to VLSI design.
- **The operations-research side is an island.** Only 6 works cite both a MOSP
  paper (Yanasse 1997, Fink & Voss 1999, or Linhares & Yanasse 2002) and a
  graph-theory paper. Two are from the Table 1 authors themselves (Linhares
  & Yanasse 2001; Yanasse & Limeira 2004). One is MOSP work (Lopes &
  Valério de Carvalho 2015, on graph properties of MOSP). Three are pathwidth
  or vertex-separation work from computer science (Fraire-Huacuja,
  Castillo-García and colleagues, two papers in 2016; Ding et al. 2017). Every
  one of the six except the 2001 paper cites Linhares & Yanasse (2002).
- **The fields follow the disciplines.** Works citing the MOSP papers are
  mostly Engineering (86 of 135); works citing the graph-theory papers are
  mostly Computer Science (417 of 507).

Counts are OpenAlex's, which misses citations Google Scholar has, so these are
lower bounds on how connected the literature is. The field of a citing work is
OpenAlex's `primary_topic` assignment, which is automatic.

## Growing and fading over the decades (added 2026-09-29)

![When each name was alive](figures/table1_trends_heatmap.png)

![Each name's rate over time](figures/table1_trends_small_multiples.png)

![Who keeps citing each Table 1 paper](figures/table1_citers_by_decade.png)

Regenerate with `python -m paper2.trends` (yearly totals for the four fields
cached in `paper2/data/openalex_trends.json`; relevant works from
`paper2/relevance.py`). Counts are turned into **rates**, works per million
published in the same four fields in the same five-year period, because those
fields publish many times more now than in 1980 and raw counts rise for nearly
every name. The heatmap scales each row to its own peak, so every row reaches
full colour once and the figure reads as a timeline of when each name was
alive; the small multiples show the rates themselves. The heatmap's row
totals, and the periods, run 1970-2024, since 2025-26 is not fully indexed;
that is why pathwidth shows 1,014 there against 1,213 over all years.

- **The VLSI names belong to the 1980s.** PLA folding and gate matrix layout
  peak in 1980-89 and fall to almost nothing after 2010; one-dimensional
  logic, never common, has no relevant work after 2009. The technology they
  described was superseded, and the names went with it.
- **The graph-searching names peak later and fade.** Node search peaks in
  the late 1980s and holds through 2009; edge search peaks in the early 1990s
  and again in 2005-14; vertex separation is highest in 1985-99; all three
  are in decline, and interval thickness is a handful of works throughout.
- **MOSP is the operations-research generation.** It first appears in the
  1990s, peaks in 2005-14, and is still active (12 works in 2020-24).
- **Only pathwidth is growing.** Its rate has roughly doubled since the
  1990s, from about 15 to 27 works per million, and 311 relevant works in
  2020-24 are more than the whole history of any other name. It is the one
  name in the family still gaining ground.
- **Citations tell a similar story.** Wing, Huang & Wang (1985) is cited
  mostly from Engineering and hardly at all after the 2000s; Möhring (1990),
  mostly from Computer Science, falls away after the 2000s too; Ohtsuki et al.
  (1979) is the exception among the VLSI papers, still cited in every decade.
  Kirousis & Papadimitriou peak in the 2000s. Kinnersley (1992) is cited most
  in the 2010s, mostly from Computer Science. The MOSP papers are cited mostly
  from Engineering, and still in the 2020s.

Caveats: OpenAlex's abstract coverage is thin before about 1990 (shaded in
the figures), which undercounts exactly the early VLSI names, so their decline
from a peak in the 1980s may be steeper than their real history; and names
with a few works per period (interval thickness, one-dimensional logic) move
by whole cells on one paper, so their rows are anecdote, not trend.
