# More members of the pathwidth complex?

Question (a): besides the twelve rows of Linhares & Yanasse (2002) Table 1 and
the thirteenth row paper 2 added (progressive pebbling), which problems equal
pathwidth (or vertex separation, interval thickness, MOSP, ...) up to a fixed
constant, or lie in a band of fixed width around it?

Written 2026-10-09. Every PDF in `literature/` (167 files) and the eleven
Table 1 sources in `paper2/literature/` were converted with `pdftotext` and
searched for the candidate names and for "equivalent to", "equals the
pathwidth", "vertex separation", "interval thickness", "node search",
"path-width"; the hits were read in context. Six scanned PDFs have no text
layer; the two that matter, Ellis, Sudborough & Turner (1994) and Bienstock,
Robertson, Seymour & Thomas (1991), were read page by page as images.
Statements are quoted from the held text, with printed page numbers (PDF page
where the file is a preprint or a thesis).

**Brute-force checks** are in `paper3/complex_members_check.py`, which imports
the definitions of `paper2/complex_check.py`. They use one core and seconds to
minutes. "Atlas" means the `networkx` graph atlas, all 1,252 graphs on 1 to 7
vertices. Run with `python paper3/complex_members_check.py <name>`; the name of
each check is given in the table.

**Labels.**

- **exact**: `f = pw + c` for one constant `c` on every input of the stated
  class, with the input map stated.
- **exact via map**: as exact, but either the map goes only one way (it reduces
  `f` to pathwidth and not back), or the offset depends on the input, or the
  class is a proper subclass. Not candidates for a Table 1.1 row as they stand.
- **band**: `pw + a ≤ f ≤ pw + b` on every input, with both ends attained.
- **related**: bounds or inequalities only. Typically the gap is unbounded, or
  the quantity is a different width parameter.
- **false**: a published claim of equivalence that does not hold, or a
  misprint.

`pw` is the pathwidth of the graph the problem lives on, `vs` its vertex
separation, `ns` its node search number.

## 1. The table

| # | Problem | Discipline | Input, and map to the graph | Relation to `pw` | Source: theorem, page (held file) | Brute force | In paper 2? |
|---|---|---|---|---|---|---|---|
| 1 | Linear gate assignment (LGAP) | VLSI | net-gate matrix; nets → vertices, a clique per gate | exact, `pw + 1`: it is gate matrix layout under another name | Linhares 2001 thesis, Ch. 1 p. 2 and Ch. 3 (`linhares_2001_phd_thesis_…`); Fomin 1998 ref. [26] "one dimensional logic gate assignment" (`paper2/literature/12_fomin_1998.pdf`) | — | yes (rows 2, 3) |
| 2 | Interval graph augmentation, minimum clique (IGAP) | graph theory | graph | exact, `pw + 1` (it is interval thickness) | Möhring 1990 Thm 3.3, p. 32; Bodlaender 1998 Thm 29, p. 13 | — | yes (row 5) |
| 3 | Minimum path partition with no alternating cycle | VLSI (PLA folding) | incompatibility graph | exact, `pw + 1` (= interval augmentation = multiple folding) | Möhring 1990 Thm 3.14, p. 36 | — | yes (row 4, footnote a) |
| 4 | Least progressive black, or black-white, pebble demand over all orientations | computation | undirected graph → its acyclic orientations | exact, `pw + 1` | Bodlaender 1998 Thm 2(5–6), p. 4, and Thm 63, p. 29, citing Kirousis & Papadimitriou 1986 | — | yes (row 13) |
| 5 | Helicopter search with bounded robber speed; interval bandwidth | graph searching | graph | band `pw` to `pw + 1` (equal to split bandwidth) | Fomin 1998 Thms 3, 6, 8 (`paper2/literature/12_fomin_1998.pdf`) | — | yes (row 9) |
| 6 | Edge search of the 2-expansion | graph searching | each edge subdivided twice | exact via map: `es(G) = vs(G'')` | Ellis, Sudborough & Turner 1994 Thm 2.2, p. 57 | paper 2 did it (181 graphs) | yes (row 7 notes) |
| 7 | Lengauer's vertex separator game | graph theory | graph | exact, `vs` (graphs with an edge) | Lengauer 1981 p. 467 | paper 2 | yes (row 11, footnote b) |
| 8 | **Maximum wavefront** (frontal Gaussian elimination of a sparse symmetric matrix) | numerical linear algebra | symmetric matrix → its nonzero graph; an elimination order is a vertex order | **exact, `pw + 1`** on every graph with a vertex | no theorem in a held source; definition via Diaz, Petit & Serna 2002 ref. Everstine 1979 ("matrix profile and wavefront"). Proof sketch in §2 | `wave`: 1,252/1,252 atlas graphs, `wf − pw = 1` | no |
| 9 | **Search for an invisible fugitive that lives on the vertices**: searchers form sets `X_i`, each a subset or a superset of the one before | graph searching | graph | **exact, `pw + 1` on every graph**, including edgeless graphs, where node search is 0 | Bienstock, Robertson, Seymour & Thomas 1991, (5.1)(i)⇔(iii), p. 282 | `brst`: 208/208 graphs on 1–6 vertices | no (a variant of row 6, without row 6's edgeless exception) |
| 10 | **Blockages** (the obstruction dual to path decompositions) | structural graph theory | graph | **exact, `pw`**: the largest order of a blockage is `pw` | BRST 1991, (2.1), p. 276: "There is a blockage of order n if and only if G has path-width ≥ n" | not done (needs set systems) | no |
| 11 | **Edge search of the tripled graph** (every edge replaced by three parallel edges) | graph searching | graph `G` → multigraph `G_e` | **exact, `pw(G) + 2`** for `G` with an edge | Kirousis & Papadimitriou 1986 Thm 2.3 proof, pp. 209–210 (gives `ns(G) ≤ es(G_e) − 1`); EST 1994 Thm 2.1, p. 54 (gives `es ≤ vs + 2`, multigraphs allowed, p. 50) | `triple`: 14/14 graphs with an edge on ≤ 4 vertices, `es(G_e) − pw = 2` (the 5-vertex run did not finish within its 550 s cap) | no |
| 12 | **Least tool-magazine capacity with no avoidable tool switch** (MTSP threshold) | flexible manufacturing | jobs → patterns, tools → customers | **exact, `pw + 1`**: the least `C` for which the minimum number of switches equals the trivial bound `M − C` is the MOSP optimum | Yanasse 1997b Prop. 1 and the formulation after it, p. 457 (`yanasse_1997b_…`); converse in the text on the same page | `mtsp`: 300/300 random instances (≤ 7 tools, ≤ 6 jobs, switches by KTNS) | no |
| 13 | Modified cutwidth through the padded incidence matrix | graph theory / OR | `G` → matrix `P'`: a row per edge, then single-1 rows so every column sums to `Δ(G)`; its MOSP graph is the line graph plus pendant cliques | exact via map, one way: `mcw(G) = pw(H_G) + 1 − Δ(G)`; on Δ-regular graphs `mcw(G) = pw(L(G)) + 1 − Δ` | Linhares & Yanasse 2002 Lemma 2, p. 1762; thesis Lemma 2.2, p. 10 | `mcut`: 280/280 atlas graphs with `|E| + padding ≤ 15` | no; paper 2 has only `mcw` against `pw` of the same graph (unbounded) |
| 14 | Directed pathwidth / directed vertex separation; routing reconfiguration in WDM networks | graph theory; optical networks | digraph; a graph `G` → symmetric digraph `Ĝ` | exact via map on symmetric digraphs: `dpw(Ĝ) = pw(G)`; elsewhere a generalisation (acyclic digraphs have `dpw = 0`) | Coudert, Mazauric & Nisse 2016 §1, p. 2 (`2016-Coudert-Mazauric-Nisse-…`): "if D is symmetric … dpw(D) equals the pathwidth of the underlying undirected graph"; `dpw = dvs` p. 4; Kitsunai et al. 2016 §1, p. 2 | — | no |
| 15 | Weighted pathwidth (vertex weights) | graph theory | weighted `G` → each vertex blown up to a clique module of its weight | exact via map, one way: weighted `pw(G) = pw(blow-up)` | Mihai & Todinca 2009 Observation 1, p. 3 | — | no |
| 16 | Edge search on sprout trees | graph searching | trees in which every internal vertex has a leaf | exact on the class: `es = ns = pw + 1` | Peng, Ho, Hsu, Ko & Tang 2000 Thm 20, p. 438 | — | no (row 7 is a band) |
| 17 | **Linear-width** (Thomas) | structural graph theory; ZDD enumeration | graph; an edge order | **band, `pw` to `pw + 1`**, for graphs with `lw ≥ 1` | Kobayashi & Nakahata 2021 Lemma 2, p. 2, correcting Fomin & Thilikos 2006 Lemma 2, p. 502 (false for `K_2`) | `lw`: 1,233 atlas graphs (≤ 16 edges): `lw − pw = 0` on 1,071, `+1` on 150, `−1` on 12, all 12 with `lw = 0` (matchings plus isolated vertices) | no |
| 18 | **Mixed search** = **3-proper pathwidth** (Takahashi, Ueno & Kajitani) | graph searching | graph | **band, `pw` to `pw + 1`** | `ms = ` 3-proper `pw`: Bodlaender 1998 Thm 62, p. 28 (primary not held). The band follows from the simulations of Bodlaender's Lemma 56, p. 26 (§3) | `mixed`: graphs with an edge on ≤ 6 vertices, `ms − pw = 0` on 171, `+1` on 31 | no |
| 19 | **Process number** (rerouting in connection-oriented networks) | telecommunications | graph (symmetric digraph) | **band, `vs` to `vs + 1`** | Coudert, Huc & Mazauric 2012 §2.4, p. 5: "It was proved by Coudert et al. [5] that vs(G) ≤ pn(G) ≤ vs(G) + 1" (primary not held) | not done | no |
| 20 | Weinberger arrays with the input and output gates pinned to the ends (Möhring's WMPP) | VLSI | net-gate matrix with two fixed end columns | band, lower half only: `≥ pw + 1`; gap 0 or 1 in every case tried; no upper bound proved | Möhring 1990 WMPP, p. 21. Fellows & Langston 1987 p. 159 and Kinnersley & Langston 1994 §3 call Weinberger arrays identical to gate matrix layout, which holds when nothing is pinned | `wein`: 275 random instances, gap `{0: 217, 1: 58}`; paper 2's 1,027 for the analogous §IV one-dimensional logic, max 1 | partly (paper 2 row 3 notes, §IV variant) |
| 21 | Cutwidth on graphs of maximum degree 3 | VLSI / graph theory | subcubic graph | band on the class, `pw` to `pw + 2` (cutwidth = edge search there) | EST 1994 p. 53, citing Makedon & Sudborough 1983 (not held); also p. 57 (`K_{3,3}`: `vs = 3`, `cw = s = 5`) | `cw3`: 253 subcubic atlas graphs, `cw − pw ∈ {0: 128, 1: 122, 2: 3}`; over all atlas graphs the gap reaches 6 | no |
| 22 | Connected pathwidth; connected search number | graph searching | graph | related: `pw ≤ cpw ≤ 2pw + 1`, "the factor 2 in the bound is tight" | Dereniowski 2011 Thm 2, p. 20, and p. 3 | — | no |
| 23 | Proper pathwidth (Kaplan & Shamir) = bandwidth | graph theory; sparse matrices | graph | related: `pw ≤ bw`, unbounded (stars) | Bodlaender 1998 Thm 53, p. 25, Thm 44, p. 23; Diaz, Petit & Serna 2002 Thm 3.2, p. 322 | — | no |
| 24 | Topological bandwidth | VLSI | graph | related: `pw ≤ tbw` | Bodlaender 1998 Thm 45, p. 23 | — | no |
| 25 | Register sufficiency of a fixed DAG = progressive black pebbling of a fixed DAG | compilers | DAG; topological orders only | related: `RS(D) ≥ vs(D_u)`, unbounded (an in-star: leaves → centre, `RS = k`, `pw = 1`); the minimum over orientations is `vs` (row 4) | Bansal & Katzelnick 2023, App., p. 25 (definition as min over topological orders of the vertex cut); Duarte et al. 2012 p. 3248 ("the number of registers … is precisely the Vertex Separation number of the ordering") | — (the in-star is checked by hand) | no |
| 26 | Register function (Strahler number) of expression trees | compilers | binary tree | related: no relation to `pw` stated in the held source | Flajolet, Raoult & Vuillemin 1979 | — | no |
| 27 | Black, and black-white, pebbling without the progressive restriction | computation | DAG | related: black-white demand `≤ (max in-degree + 1) · ns` | Bodlaender 1998 Thm 64, p. 29 (KP 1986) | — | no |
| 28 | Profile = sum cut = interval graph completion with fewest added edges = total vertex separation | sparse matrices; archaeology; clone fingerprinting | graph | related: these are the sum versions of the max objectives (profile against `vs`) | Diaz, Petit & Serna 2002 §3, p. 319 | — | no |
| 29 | Minimum front size (multifrontal elimination) | sparse matrices | graph | related: a treewidth parameter, not a pathwidth one (grouped with treewidth and approximated with no `log n` factor) | Feige, Hajiaghayi & Lee 2008 Cor. 6.5, p. 22 (citing Bodlaender, Gilbert, Hafsteinsson & Kloks 1995, not held) | — | no |
| 30 | Treewidth and its games (Seymour–Thomas visible robber; inert fugitive, Dendris et al.) | graph searching | graph | related: `tw ≤ pw = O(tw log n)` | Bodlaender 1998 Thms 59–60, pp. 27–28, Cor. 24, p. 10 | — | no |
| 31 | Tree-depth / vertex ranking | graph theory | graph | related: `tw ≤ pw ≤ td ≤ tw · log² n` | Bodlaender 2024 p. 13; Bannach & Berndt 2022 p. 4 | — | no |
| 32 | Linear rank-width | graph theory | graph | related: equals `pw` on forests (Adler & Kanté, cited); at most 1 on complete graphs | Adler, Kanté & Kwon 2014 p. 3 | — | no |
| 33 | Hypergraph cutwidth of the pattern hypergraph (open stacks counted between consecutive patterns) | VLSI / OR | MOSP matrix; patterns are vertices, customers are hyperedges | related: a star of `k` customers gives MOSP `k` against `⌈k/2⌉`; unbounded | mentioned in EST 1994 p. 54 (Miller & Sudborough, not held) | `cut`: stars `k = 2..6` give 2/1, 3/2, 4/2, 5/3, 6/3; random, MOSP − cut ∈ {0,…,3} | no |
| 34 | q-proper interval subgraphs (Proskurowski & Telle) | graph theory | graph | related: a family of parameters from bandwidth (`q = 0`) to pathwidth (`q = k`) | Proskurowski & Telle 1999, abstract and §4 | — | no |
| 35 | Separable-pairs objective `g` (Truchet, Bourdon & Codognet), a local-search surrogate for MOSP | constraint programming | MOSP matrix | related: a count of pairs, not `pw + c`. The authors claim only "intuitively … they behave in the same way … except in rare cases"; the challenge report states it as "equivalent" | Truchet et al. 2005, entry in the Challenge proceedings, PDF p. 85; Smith & Gent report, p. 6 (`2005-Smith-Gent-…`) | `truchet`: some `g`-maximiser is MOSP-optimal on 2,996/2,996 random and 373/373 graph-incidence instances; nothing proved | no |
| 36 | Number of tracks in channel routing (left-edge algorithm) | VLSI | fixed column order | related: the density of one fixed order, so there is no minimisation over orders; it is the inner step of gate matrix layout | Möhring 1990 p. 31 (left-edge, Hashimoto & Stevens 1971) | — | no |
| 37 | DNA physical mapping in the presence of false negatives | computational biology | — | claimed "equivalent to VERTEX SEPARATION [GGKS95]": **not verified in a held source** | Markov 2004 MSc thesis, Ch. 1, PDF p. 12 | — | no |
| 38 | Zero-visibility cops and robber | graph searching | — | **not verified in a held source**; from memory, related only (one-sided bound) | none held | — | no |
| 39 | Fast searching | graph searching | — | **not verified in a held source** | none held | — | no |
| 40 | Minimization of order spread (MORP) | cutting / OR | MOSP matrix | false: not equivalent. MORP is the largest span, so one pattern shared by `k` single-pattern customers gives MOSP `k`, MORP 1 | Linhares & Yanasse 2002 Prop. 3, p. 1767; thesis Prop. 2.3, p. 19 | — | no |
| 41 | Minimization of discontinuities (MDP) | cutting / OR | MOSP matrix | false: not equivalent (a sum) | Linhares & Yanasse 2002 Props. 4–5, p. 1767 | — | no |
| 42 | Minimization of tool switches (MTSP), as a value | flexible manufacturing | MOSP matrix plus capacity `C` | false: not equivalent; "MOSP is equivalent to MTSP only when C = C*" (but see row 12) | Yanasse 1997b p. 457; Linhares & Yanasse 2002 Prop. 6, p. 1767; Lopes & Valério de Carvalho 2015 p. 217 | — | no |
| 43 | "Modified Cutwidth" in the list of problems equivalent to the column permutation problem | — | same graph | false as stated: `mcw` is unbounded against `pw` (stars, paper 2 row 11); true only through the padded map of row 13 | Lima, Santos & de Carvalho 2024, p. 2 | `mcut`: on the same graph, `mcw − pw ∈ {−1: 228, 0: 51, 1: 1}` on the small graphs; stars make it unbounded | yes (row 11 refutes `mcw`); the claim is new |
| 44 | Diaz, Petit & Serna Theorem 3.1, "MINVS(G) = MINPW(G) = MINSN(G) − 1 = MINGML(G) + 1" | — | — | false (a misprint): gate matrix layout is `pw + 1`, so the last term should be `MINGML(G) − 1` | Diaz, Petit & Serna 2002 Thm 3.1, p. 322 | — | no |
| 45 | Makedon et al.: "the node search number is at most the topological bandwidth" | — | — | false: `K_k` has topological bandwidth `k − 1` and node search number `k` | Bodlaender 1998 p. 23 | — | no |

Rows 1–7 restate members that paper 2 already has, under another name or a
transformation. They are listed so that the count of what was checked is
honest.

## 2. New exact members: candidates for rows 14, 15, … of Table 1.1

Five relations are exact, hold on every input of a natural class, and are not in
paper 2. They are ordered by how well they fit the table: a named problem from
another discipline first, then the reformulations.

**(i) Maximum wavefront of a symmetric matrix: `pw + 1`** (row 8; numerical
linear algebra). Order the rows and columns of a symmetric matrix by
`v_1, …, v_n`, and let `V_i = {v_1, …, v_i}`. In the frontal method the
wavefront at step `i` is the set of rows that are active: `v_i` together with
the unordered neighbours of `V_i`, i.e. `{v_i} ∪ (N(V_i) \ V_i)`. Its size is
`1 + |N(V_i) \ V_i|`. Now read the order backwards. The set `V \ V_i` is a
prefix of the reversed order, and its inner boundary (its vertices with a
neighbour outside it) is exactly `N(V_i) \ V_i`. So the largest wavefront of an
order is `1 + vs` of the reversed order, and minimising over orders gives
`min max wavefront = vs + 1 = pw + 1` on every graph with a vertex. Some
authors do not count `v_i` itself; then the offset is 0. Either way the offset
is fixed. The brute-force check agrees on all 1,252 atlas graphs. **Evidence
gap:** no held paper states the definition or the equality. The survey only
cites Everstine (1979) for "matrix profile and wavefront". The equality is
folklore in sparse-matrix work, and Kumfert & Pothen (1997) or Everstine (1979)
must be obtained before it is cited. This is the cleanest new member: a
different discipline, a min-max over orders, and a fixed offset.

**(ii) Bienstock–Robertson–Seymour–Thomas search: `pw + 1` on every graph**
(row 9; graph searching). BRST 1991 (5.1), p. 282, defines a search as a
sequence of searcher sets `X_1 = ∅, X_2, …, X_m`, each a subset or a superset
of the one before. The fugitive sits on vertices, is invisible, and is
arbitrarily fast. They prove: "there is a successful search with each
`|X_i| ≤ n`" ⇔ "G has path-width ≤ n − 1" ⇔ "there is a monotone one". This is
node search with the fugitive on the vertices instead of the edges. The
difference matters exactly where paper 2 found row 6 false: on edgeless graphs
node search is 0, but this game needs 1 = `pw + 1`. So BRST's game is the exact
version of row 6, with no hypothesis, and its monotonicity comes with it,
proved from the blockage theorem rather than from LaPaugh. Brute force:
208/208 graphs on 1–6 vertices, edgeless graphs included.

**(iii) Blockages: the largest order is `pw`** (row 10). BRST 1991 (2.1),
p. 276. This is a min-max dual: `pw` is the maximum of an obstruction, not the
minimum over layouts. It belongs in the table as a certificate of lower bounds
rather than as a problem from another field. It is the pathwidth analogue of
Seymour & Thomas's havens and brambles for treewidth.

**(iv) Edge search of the tripled graph: `pw + 2`** (row 11). Replace every edge
of `G` by three parallel edges to get `G_e`. Kirousis & Papadimitriou's proof
of Thm 2.3 (pp. 209–210) turns an edge search of `G_e` into a node search of
`G` with one searcher fewer, so `ns(G) ≤ es(G_e) − 1`. Ellis, Sudborough &
Turner Thm 2.1 (p. 54; multigraphs allowed, p. 50) gives
`es(G_e) ≤ vs(G_e) + 2 = vs(G) + 2`. Together, for `G` with an edge,
`es(G_e) = ns(G) + 1 = pw(G) + 2`. Neither paper states the equality, but
both halves are in held sources. It does to edge search what row 13c (`G_d`)
does to pebbling: it turns the band of row 7 into an exact relation on a
derived input class. The check used two of the three parallel copies
subdivided once, which keeps the graph simple and does not change the
edge-search number (KP p. 209). Brute force: 14/14 graphs with an edge on ≤ 4
vertices give `es(G_e) − pw = 2`.

**(v) MTSP threshold: the least tool-magazine capacity with no avoidable switch
is `pw + 1`** (row 12; flexible manufacturing). Yanasse 1997b, p. 457: with `M`
tools, every tool is loaded once, so at least `M − C` switches are needed.
Prop. 1: this bound is attained when `C ≥ C*`, the MOSP optimum, by following
an optimal MOSP sequence. The same page reformulates MOSP as "Minimize C
subject to Σ switches = M − C". The converse is also true: if `C < C*`, every
sequence has a job at which more than `C` tools are open (needed at or before
it and at or after it). One of them is out of the magazine at some point
between two of its uses, so it is loaded twice, which is a switch beyond
`M − C`. So `C*` is the least `C` for which `MTSP_C = M − C`. This is a
threshold characterisation, of the same kind as "a graph has gate matrix layout
cost `k` iff …". It ties tool switching, which is not equivalent as a value (row 42), to
the complex. Brute force: 300/300 random instances, with switches of a fixed
sequence computed by KTNS (Tang & Denardo 1988, optimal for a fixed sequence).

Of these, (i) and (ii) are new rows in the sense of Table 1.1: a problem, a
discipline, a fixed offset. (iii) is a dual characterisation. (iv) and (v) are
exact reformulations of problems the complex already discusses (edge search,
tool switching). They can be recorded the way paper 2 records 13b and 13c.

**Exact via a map, not candidates as they stand** (rows 13–16):

- **Modified cutwidth.** Linhares & Yanasse 2002 Lemma 2 (p. 1762) is exact for
  every layout, not only at the optimum: `Z_MOSP(P') = Z_MCUT(G) + C`. So
  `mcw(G) = pw(H_G) + 1 − Δ(G)`. The offset depends on the input, and the
  reduction goes one way. On a class of Δ-regular graphs no padding is needed,
  so `mcw(G) = pw(L(G)) + 1 − Δ`, a fixed offset against the line graph. For
  example, `mcw = pw(L(G)) − 2` on cubic graphs. Fellows & Langston 1989 Thm 8
  (p. 504) also measures modified min cut through the line graph, but gives
  only `pw(L(G)) ≤ 3k + 1`. Brute force: 280/280.
- **Directed pathwidth** on symmetric digraphs (`dpw(Ĝ) = pw(G)`), and its
  application, routing reconfiguration in WDM networks (CMN 2016 p. 2). Exact
  on the symmetric class only.
- **Weighted pathwidth** = pathwidth of the clique-module blow-up (Mihai &
  Todinca, Obs. 1). It applies directly to MOSP with weighted customers. One way.
- **Edge search on sprout trees** = `ns` = `pw + 1` (Peng et al. Thm 20). Exact on
  a subclass only.

## 3. Bands and near-misses, and why they are not exact

- **Linear-width (row 17)**, band `{pw, pw + 1}`. Both ends occur: `lw = pw` on
  paths, cycles, stars, `K_3`, `K_4`; `lw = pw + 1` on `K_{2,3}` (2 against 3)
  and `K_{3,3}` (3 against 4), and on 150 atlas graphs in all. It is not a fixed
  offset, because an edge order can keep a degree-1 end out of the boundary on
  some graphs and not on others. Fomin & Thilikos 2006 Lemma 2 states the band "for any graph". It is
  **false for `K_2`** (`pw = 1`, `lw = 0`) and for every matching. Kobayashi &
  Nakahata 2021 restrict it to `lw ≥ 1`, and our check confirms that the only
  exceptions are the 12 small graphs with `lw = 0`. By Bienstock & Seymour
  (cited in Fomin & Thilikos p. 502) linear-width is the mixed search number for
  graphs without vertices of degree 1, which links rows 17 and 18.
- **Mixed search (row 18)**, band `{pw, pw + 1}`. The upper bound holds because
  node-search moves are mixed-search moves, so `ms ≤ ns = pw + 1`. For the lower
  bound, replace each slide `u → v` by "place on `v`, remove from `u`", which
  turns a mixed search into a node search with at most one more searcher, so
  `pw + 1 = ns ≤ ms + 1`. This is Bodlaender's Lemma 56 argument (p. 26). Both
  ends occur: `ms(K_n) = pw` (slide the last searcher in), and
  `ms(K_{1,3}) = 2 = pw + 1`, where linear-width is 1. This is why the
  Bienstock–Seymour identity `lw = ms` needs minimum degree 2. Computed values:
  `ms(K_3) = 2`, `ms(K_{2,3}) = 3`, `ms(K_{3,3}) = 4`.
  Brute force: 202 graphs, `{0: 171, 1: 31}`.
- **Process number (row 19)**, band `{vs, vs + 1}`. Stated, not proved, in a
  held source. Coudert, Huc & Mazauric 2012 give star 1, path 2, cycle 3,
  `n × n` grid `n + 1`, so `pn = vs` occurs (star, grid) and `pn = vs + 1`
  occurs (path, cycle). On trees, process number has the same three-branch
  (Parsons) rule as `es`, `ns`, `vs` for `p ≥ 2` (their Thm 2, p. 6). A new
  discipline (optical network rerouting), so it is worth obtaining the primary
  and adding it beside split bandwidth as a band row.
- **Weinberger arrays (row 20).** Unpinned, they are gate matrix layout
  (FL 1987 p. 159; Devadas 1986 §2.3: "the one-dimensional placement algorithms
  for a Weinberger array apply equally well to a gate matrix"). Möhring's WMPP
  pins the input gate `G_0` and the output gate `G_{n+1}` to the ends. That is
  the analogue of Ohtsuki's §IV boundary gates, for which paper 2 proved only
  `≥ pw + 1`. Our 275 new random instances never exceed `pw + 2`, the same as
  paper 2's 1,027. Not exact: the pin costs a track on some instances (gap 1 on
  58 of 275) and nothing on others.
- **Cutwidth on subcubic graphs (row 21).** Cutwidth equals the edge search
  number when the maximum degree is 3, so on that class cutwidth inherits row
  7's band `{pw, pw + 2}`. Brute force sees all three values. On general graphs
  the gap is unbounded (paper 2 row 11). This is the only sense in which Table
  1's "edge separation", read as cutwidth, belongs to the complex.
- **Hypergraph cutwidth (row 33)** is the nearest near-miss on the matrix side.
  It counts a customer as open *between* two patterns, where MOSP counts it *at*
  a pattern. A customer whose patterns are all at one position never counts, and
  a star of `k` customers halves the value. So it is not a band.
- **Connected pathwidth (row 22).** It is within a factor of 2, and the factor
  is tight (Dereniowski p. 3), so no additive band exists. The contrast is
  worth a sentence: connected *treewidth* equals treewidth (Fraigniaud & Nisse,
  cited p. 3).
- **Register sufficiency (row 25).** It is vertex separation restricted to
  topological orders, so `RS ≥ vs`, with an unbounded gap (in-star). Minimising
  over all orientations removes the restriction and gives back `vs` (row 4).
  Register allocation enters the complex only through that minimisation.
- **Sum versions (row 28).** Profile, sum cut, min-fill interval completion and
  total vertex separation are the `Σ` analogues of `vs`, so they have no
  constant relation to `pw`. The Truchet surrogate (row 35) is of this kind too
  (it maximises separated pairs, i.e. minimises interval-completion edges).
  Whether some `g`-optimal order is always MOSP-optimal is open: no
  counterexample in 3,369 small instances, but the authors claim nothing.
- **Front size versus wavefront (rows 29, 8).** The two sparse-matrix
  parameters are easily confused. The multifrontal *front size* is a treewidth
  quantity. The frontal-method *wavefront* is a pathwidth quantity, and exact.
- **Treewidth relations (rows 30, 31)**: `tw ≤ pw ≤ td`, with
  `pw = O(tw log n)`. These are inequalities, not equalities, in both
  directions.

## 4. Papers to obtain

1. Takahashi, Ueno & Kajitani 1995, "Mixed searching and proper-path-width",
   *TCS* 137, 253–268: primary for row 18 (`ms` = 3-proper `pw`; monotonicity).
2. Coudert, Perennes, Pham & Sereni 2007, "Rerouting requests in WDM networks"
   (AlgoTel); and Coudert & Sereni 2011, "Characterization of graphs and
   digraphs with small process number", *DAM* 159: primary for row 19
   (`vs ≤ pn ≤ vs + 1`).
3. Everstine 1979, "A comparison of three resequencing algorithms for the
   reduction of matrix profile and wavefront", *IJNME* 14, 837–853; and Kumfert
   & Pothen 1997, "Two improved algorithms for envelope and wavefront
   reduction", *BIT* 37: definition of the wavefront, for row 8.
4. Bodlaender, Gilbert, Hafsteinsson & Kloks 1995, "Approximating treewidth,
   pathwidth, frontsize, and shortest elimination tree", *J. Algorithms* 18,
   238–255 (only the WG'91 version without frontsize is held, and it is a
   scan): for row 29.
5. Goldberg, Golumbic, Kaplan & Shamir 1995, "Four strikes against physical
   mapping of DNA", *J. Comput. Biol.* 2, 139–152: for row 37.
6. Makedon & Sudborough 1983/1989 (cutwidth = search number at maximum degree
   3): primary for row 21. Makedon, Papadimitriou & Sudborough 1985
   (topological bandwidth), for row 45.
7. Bienstock & Seymour 1991, "Monotonicity in graph searching", *J. Algorithms*
   12: the mixed search / linear-width link.
8. Kaplan & Shamir 1996, "Pathwidth, bandwidth and completion problems to
   proper interval graphs with small cliques", *SICOMP* 25: row 23.
9. Yang & Cao 2008 (directed vertex separation = directed pathwidth): row 14.
10. Dereniowski, Dyer, Tifenbach & Yang 2015, "Zero-visibility cops and robber
    and the pathwidth of a graph", *J. Comb. Optim.*; Dyer, Yang & Yaşar 2008,
    "On the fast searching problem": rows 38–39.
11. Adler & Kanté 2015, "Linear rank-width and linear clique-width of trees",
    *TCS* 589: row 32.
12. Sethi 1975, "Complete register allocation problems", *SICOMP* 4; Bodlaender,
    Gustedt & Telle 1998 (SODA): row 25.
13. Tang & Denardo 1988, "Models arising from a flexible manufacturing machine,
    part I", *Oper. Res.* 36 (KTNS optimality, used in the row 12 check).
14. Still missing from paper 2: Kashiwabara & Fujisawa 1979.

## Counts

45 candidates checked (rows 1–45). Of these, 7 restate members paper 2
already has (rows 1–7). The other 38:

| class | rows | count |
|---|---|---|
| exact, new, on a natural class (Table 1.1 candidates) | 8, 9, 10, 11, 12 | 5 |
| exact via a map (one-way, input-dependent offset, or a subclass) | 13, 14, 15, 16 | 4 |
| band | 17, 18, 19, 20, 21 | 5 |
| related (bounds only, or a different parameter) | 22–36 | 15 |
| not verified in a held source | 37, 38, 39 | 3 |
| false, or misprinted | 40–45 | 6 |

Brute-force checks run: wavefront, BRST search, tripled-edge search, MTSP
threshold, padded modified cutwidth, linear-width, mixed search, subcubic
cutwidth, hypergraph cutwidth, pinned Weinberger, Truchet surrogate (11). None
disagreed with the statement it tested.
