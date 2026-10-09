# Pathwidth of trees and sparse graph classes: a survey for paper 3

*Written 2026-10-09 for a possible third paper, "applied mathematics of pathwidth
on special graph classes". The subject is pathwidth, which is the same number as
vertex separation, node search number − 1, interval thickness − 1 and MOSP − 1
(the last proved in Lean in `lean/MOSPFormalization/MOSPGraph.lean`). In every
row below, "pw" can be read as "minimum open stacks − 1 on the MOSP graph".*

**How to read the source column.** A row marked **read** gives a theorem and page
taken from a PDF read for this survey. Page numbers are journal pages where the
PDF has them, and otherwise pages of the held copy. **secondary (X)** means that
we read the statement in paper X, which we hold, and not in the original.
**abstract only** means that the abstract (or a search-engine summary of it) is
all we read. Nothing below is cited from memory. Results we derived ourselves are
labelled *ours*, and none of them has been checked by a referee or by the solver.

**What the search could reach.** OpenAlex worked for about 20 queries and then
ran out of credits for the day (HTTP 429, retry-after 82,584 s). Crossref,
Semantic Scholar and DBLP were also rate-limited or unreachable from this machine
that day. The rest of the search used web search, author pages, arXiv, DMTCS,
Serdica, the Utrecht and UVic repositories, and OEIS. Elsevier
(ScienceDirect), ACM and HAL served a browser check to scripts, and none was
bypassed. Many of those papers are in Elsevier's free open archive, so a browser
can fetch them; they are listed at the end with their DOIs.

---

## 1. The table

| Class | Pathwidth result | Type | Source, theorem, page | Held? file |
|---|---|---|---|---|
| **Trees: characterisation** | For a tree T and k ≥ 1, vs(T) ≤ k if and only if every vertex x has at most two branches (subtrees of T − x) of vertex separation k and all others ≤ k − 1 | exact characterisation | Ellis, Sudborough & Turner 1994, Thm 3.1, p. 63 (**read**, from page images). Also Scheffler 1990, as quoted by Coudert, Huc & Sereni, Thm 5 (secondary) and Möhring 1990, Lemma 3.12 and the "converse" remark, pp. 36, 44 (**read**) | yes: `ellis_sudborough_turner_1994_vertex_separation_search_number.pdf` (scan, no text layer); `mohring_1990_gate_matrix_layout_pla_folding.pdf` |
| Trees: path form | pw(T) ≤ p (p ≥ 2) if and only if some path P has every component of T − P of pathwidth ≤ p − 1 | characterisation | Ellis et al. 1994, in the proof of Thm 3.1, p. 64 (**read**); stated as Thm 6 in Coudert, Huc & Sereni (**read**) | yes |
| **Trees: algorithm** | vs(T) in O(n) time; an optimal layout in O(n log n) | linear algorithm | Ellis et al. 1994, abstract p. 50, Thm 3.4 p. 77, §3.5 p. 77 (**read**) | yes |
| Trees: algorithm, optimal layout | an optimal layout in O(n) | linear algorithm | Skodinis 2003, *J. Algorithms* 47:40–59 (secondary: Mihai & Todinca 2009 p. 1, Petit 2011 Table 5); Peng et al. 2000, *TCS* (secondary: Mihai & Todinca) | no |
| Trees: algorithm (peeling) | track number and an optimal layout in O(\|V\|), by phase labels peeled from the leaves | linear algorithm | Möhring 1990, Thm 4.7, p. 45 (**read**) | yes |
| Trees: distributed | node search number in O(n log n) total time with n messages of log₃ n + 4 bits | distributed algorithm | Coudert, Huc & Mazauric 2012, *Algorithmica* 63:158–190 (abstract only) | no (HAL `inria-00587819` behind a browser check) |
| **Trees: extremal size (closed formula)** | the smallest tree with vs = k has m(k) vertices, m(1) = 2, m(k) = 3m(k−1) + 1, m(k) = ⌊5·3^k/6⌋, so m(5) = 202. Equivalently m(k) = (5·3^(k−1) − 1)/2, which is OEIS A060816, whose entry does not mention trees. Hence vs(T) ≤ 1 + log₃((2n+1)/5) (*ours*, from the recurrence), sharp on the minimal trees | closed formula, sharp | Ellis et al. 1994, §3.2, pp. 67–68 (**read**). The minimal trees are three copies of T(k−1) joined to a new vertex, p. 67 | yes |
| Trees: general bound | pw(T) ≤ log₃(2n + 1) | bound | Scheffler 1990, quoted as Thm 66 in Bodlaender 1998, p. 30 (secondary; the extracted text reads "3 log(2n+1)", and base 3 is consistent with m(k) above) | `1998-Bodlaender-Partial-k-Arboretum-...pdf` |
| Trees: forbidden subtrees | vs(T) ≥ k if and only if T contains a homeomorphic image of a tree in F(k), where F(1) = {K₂} and F(i+1) is three trees of F(i) ∪ S(F(i)) joined to a new vertex | characterisation | Ellis et al. 1994, Thm 3.2, p. 68 (**read**) | yes |
| Trees: acyclic obstructions | minimal acyclic forbidden minors for pathwidth ≤ k, with estimates of their number and size | characterisation, counts | Takahashi, Ueno & Kajitani 1994, *Discrete Math.* 127:293–304 (abstract only) | no (Elsevier open archive) |
| **Paths, stars, caterpillars** | a connected graph has pw ≤ 1 if and only if it is a caterpillar; the obstructions for pw ≤ 1 (2-track gate matrix layout) are K₃ and the subdivided claw S(K₁,₃) | formula (pw ∈ {0, 1}) | Kinnersley & Langston 1994, p. 172 (**read**); Ellis et al. 1994, p. 63: vs(T) = 1 if and only if T has an edge and no subtree homeomorphic to the vs-2 tree of Fig. 3.4 (**read**) | yes: `1994-Kinnersley-Langston-...pdf` |
| Lobsters | pw ≤ 2: take the caterpillar spine as the path P of Thm 3.1, and every component of T − P is a star | bound (*ours*, one line from Ellis et al. Thm 3.1) | derived here; no published statement found | n/a |
| Graphs of pw ≤ 2 | exactly 110 minor obstructions, 10 of them trees; the basis for pw ≤ 3 has at least 122 million elements; conjecture: the trees are the largest obstructions in every basis | characterisation, open conjecture | Kinnersley & Langston 1994, Thm 9.1, p. 198; Lemma 6.1, p. 187; conjecture pp. 198–199 (**read**) | yes |
| Graphs of pw ≤ 2, structure | a 2-connected graph has pw ≤ 2 if and only if it is a "track"; connected graphs of pw ≤ 2 are tracks and bond-trees glued in a path-like way, with fripperies and hairs | structural characterisation | Barát, Hajnal, Lin & Yang 2012, Thm 3.1 and Thm 5.4 (**read**) | **downloaded**: `2012-Barat-Hajnal-Lin-Yang-Structure-Graphs-Path-Width-At-Most-Two-arXiv.pdf` |
| **Complete ternary tree** | pw = height (node search number = height + 1) | closed formula | Kirousis & Papadimitriou 1986, as Thm 68 in Bodlaender 1998, p. 30 (secondary); Möhring 1990, Prop. 3.13, p. 36 (**read**) | yes: `kirousis_papadimitriou_1986.pdf` |
| **Complete binary tree** of depth k (2^(k+1) − 1 vertices) | pw = ⌈k/2⌉ | closed formula | Scheffler 1990, as Thm 67 in Bodlaender 1998, p. 30 (secondary) | Scheffler: no |
| Search number vs vertex separation on trees | vs ≤ s ≤ vs + 2 for all graphs; trees exist with s − vs = 2 (Fig. 3.6: vs 3, cutwidth 5) | bound, tight | Ellis et al. 1994, Thm 2.1, p. 54; §3.3, p. 68 (**read**) | yes |
| Rooted pathwidth of trees | rooted pathwidth = Horton–Strahler number; upward drawings of width ≤ log₂(n+1) | closed (recursive) formula | Biedl 2022, *IPL* 175 (abstract only) | no |
| **Weighted trees** (vertex v stands for a clique module of w(v) true twins) | **NP-hard**, even with weights polynomial in n | hardness | Mihai & Todinca 2009, Thm 4, author copy p. 9 (**read**) | **downloaded**: `2009-Mihai-Todinca-Pathwidth-NP-Hard-Weighted-Trees-FAW-author.pdf` |
| **Octopus graphs** (chordal, clique tree is a spider, every vertex in ≤ 2 maximal cliques) | **NP-hard**; polynomial when every leg has all separators of one size (Thm 5); open for a constant number of legs or legs of constant length | hardness + polynomial subcase + open | Mihai & Todinca 2009, Thm 3 p. 5, Thm 5 p. 10, open questions p. 10 (**read**) | downloaded (as above) |
| Distance-hereditary, circle graphs | NP-hard (corollary of weighted trees) | hardness | Mihai & Todinca 2009, p. 9 (**read**), also crediting their ref. [18] | downloaded |
| **Block graphs** (every 2-connected component a clique) | polynomial; "avenue" technique from trees generalised; answers an open question of Peng et al. | polynomial algorithm | Chou, Ko, Ho & Chen 2008, *DAM* 156:55–75 (secondary: Mihai & Todinca p. 1; abstract via web search) | no (Elsevier open archive) |
| **Unicyclic graphs** (tree plus one edge) | vs in O(n log n), "practical", outputs an optimal layout | polynomial algorithm | Markov 2004, MSc thesis, abstract (**read**); Ellis & Markov 2004, *Inf. Comput.* 192:123–161 (secondary: Petit 2011 Table 5) | **downloaded**: `2004-Markov-Fast-Practical-Algorithm-Vertex-Separation-Unicyclic-Graphs-MSc-UVic.pdf` |
| **Cactus graphs** | characterisation: vs(G) ≤ k if and only if (1) every vertex begets at most two subcacti of separation k and the rest ≤ k − 1, and (2) every cycle has a "k-favourable pair". No practical algorithm: stretchability w.r.t. one vertex pair reduces to two pairs, then three, and so on | characterisation; polynomial only via bounded treewidth | Markov 2007, Thm 1, p. 62; Conclusions p. 71 (**read**); polynomial by Bodlaender & Kloks Cor. 7.4 (**read**) | **downloaded**: `2007-Markov-Vertex-Separation-Cactus-Graphs-SerdicaJComput.pdf` |
| Cycle-disjoint graphs (edge search) | edge search number in polynomial time | polynomial algorithm (edge search, not node search) | "Searching cycle-disjoint graphs", 2007, LNCS (found; abstract not read) | no |
| **Maximal outerplanar graphs** | vs(G) ≤ k if and only if every face has a (k − 1)-affixable child. The author found no practical algorithm and reports earlier attempts that failed | characterisation | Markov 2008, Thm 2, p. 233; Conclusion, §5 (**read**) | **downloaded**: `2008-Markov-Vertex-Separation-Maximal-Outerplanar-Graphs-SerdicaJComput.pdf` |
| **Outerplanar** (biconnected), via the weak dual tree T* | pw(T*) ≤ pw(G) ≤ 2pw(T*) + 2 (Bodlaender & Fomin), improved to pw(G) ≤ 2pw(G*) − 1, tight: for every p and k ∈ {1, …, p+1} there is a biconnected outerplanar graph of pathwidth p + k whose weak dual has pathwidth p | bound, tight interval; gives a linear-time 2-approximation | Bodlaender & Fomin 2002 (TR 2000), Thm 1 (**read**); Coudert, Huc & Sereni 2007, Thms 1, 3, 4 (**read**) | `2009-Coudert-Huc-Sereni-...pdf`; **downloaded**: `2000-Bodlaender-Fomin-Approximation-Pathwidth-Outerplanar-Graphs-TR-UU-CS-2000-23.pdf` |
| Outerplanar (general) | exact in polynomial time, but "already one step in the algorithm requires to work with sets of size O(n¹¹)"; a 3-approximation in O(n log n) (Govindan, Langston & Yan 1998) | polynomial (impractical) + approximation | Bodlaender & Fomin TR p. 1 (**read**); Govindan et al. 1998, *IPL* 68 (secondary: Coudert et al., Petit Table 8) | Govindan: no |
| Outerplanar, 2-connecting | every connected outerplanar graph of pathwidth p has a 2-connected outerplanar supergraph of pathwidth ≤ 16p + 15 | bound | Babu, Basavaraju, Chandran & Rajendraprasad 2014, Lemma 11 (**read**) | **downloaded**: `2014-Babu-...-2-Connecting-Outerplanar-Graphs-Pathwidth-TCS-arXiv.pdf` |
| **Halin graphs** | polynomial (treewidth ≤ 3) but only by the general method; a 3-approximation in O(n) | polynomial (impractical) + approximation | Bodlaender & Kloks Cor. 7.4 (**read**); Fomin & Thilikos 2006, *J. Discrete Alg.* 4:499–510 (secondary: Petit 2011 Table 8) | Fomin & Thilikos: no |
| **Series–parallel** (treewidth ≤ 2) | polynomial, by the general method only. No dedicated algorithm or closed form was found | polynomial (impractical) | Bodlaender & Kloks Cor. 7.4 (**read**); tw ≤ 2: Bodlaender 1998, Thm 41, p. 21 (**read**) | yes |
| Almost trees with parameter k, k-outerplanar | polynomial for fixed k (bounded treewidth) | polynomial (impractical) | Bodlaender & Kloks Cor. 7.4 (**read**) | yes |
| **k-trees, partial k-trees, fixed k** | polynomial for every fixed treewidth bound, since pw ≤ (tw + 1) log n keeps the DP polynomial | polynomial (impractical) | Bodlaender & Kloks 1996, Thm 7.3 and Cor. 7.4, §7 (**read**, held technical report version) | `1996-Bodlaender-Kloks-...pdf` |
| k-paths, k-caterpillars | k-caterpillars are exactly the edge-maximal graphs of pathwidth k (so pw = k); k-paths are C_{k,k−1}, k-rays are the edge-maximal graphs of bandwidth k | characterisation (pw = k) | Proskurowski & Telle 1999, Thm 6.2 and p. 173 (**read**) | **downloaded**: `1999-Proskurowski-Telle-Classes-Graphs-Restricted-Interval-Models-DMTCS.pdf` |
| Chordal, starlike, split | NP-hard; polynomial for primitive starlike graphs and for chordal graphs whose cliques overlap a central clique in a special way | hardness + polynomial subcases | Gustedt 1993 (secondary: Möhring 1990, Thm 4.4, p. 40, Thm 4.9, p. 46 (**read**); Petit 2011 Table 3; Mihai & Todinca Thm 5 proof) | no (Elsevier open archive) |
| Planar, maximum degree 3 | NP-hard | hardness | Monien & Sudborough 1988 (secondary: Petit 2011 Table 3) | no |
| Cographs | closed recursion: ns(G₁ + G₂) = max(ns(G₁), ns(G₂)), ns(G₁ ∗ G₂) = min(\|V₁\| + ns(G₂), \|V₂\| + ns(G₁)); O(n) from the cotree | closed recursion, linear | Möhring 1990, (4.4)–(4.5) and Thm 4.8, p. 46 (**read**) | yes (and `1990-Bodlaender-Mohring-...pdf`, added today by another survey) |
| **Bounded treewidth, general** | pw ≤ (tw + 1) log n (Korach & Solel); pw = O(tw · log n) | bound | Bodlaender & Kloks, Thm 7.1, §7 (**read**); Bodlaender 1998, Cor. 24, p. 10 (**read**) | yes |
| Bounded treewidth, approximation | an O(t √log t)-approximation for graphs of treewidth t; pw ≥ th + 2 ⇒ tw ≥ t or a subdivided complete binary tree of height h + 1 | approximation, structural bound | Groenland, Joret, Nadara & Walczak 2021/2023, abstract (**read**) | yes |
| Classes with small separators | if every graph in a subgraph-closed class has a separator of size f(n), then pw ≤ f(n)(⌈·log n⌉ + 1); pw = O(√n) for planar graphs | bound | Bodlaender 1998, Thms 20–22 and Cor. 23, p. 10 (**read**) | yes |
| Cubic / max-degree-3 graphs | pw ≤ (1/6 + ε)n for n > n(ε) | bound | Fomin & Høie 2006, abstract and proof of Thm 3 (**read**) | `2006-Fomin-Hoie-Pathwidth-Cubic-Graphs-Exact-Algorithms-IPL.pdf` (added today by another survey) |
| Sparse graphs, m edges | pw ≤ m/5.769 + O(log n), with a polynomial-time decomposition | bound | Kneis, Mölle, Richter & Rossmanith 2009, *SIAM J. Discrete Math.* 23:407–427 (abstract only) | no |
| 2-connected, cocircumference k | pw ≤ 3k − 2 (tw ≤ k for every graph) | bound, tight up to a constant | Briański, Joret & Seweryn 2024, abstract (**read**) | **downloaded**: `2024-Brianski-Joret-Seweryn-Pathwidth-vs-Cocircumference-SIDMA-arXiv.pdf` |

### The same classes on the MOSP side

The MOSP graph is a union of cliques, one per pattern. That gives exact
translations, none of them published as far as we found:

- **The MOSP graph is a forest exactly when** every pattern has at most two
  customers (a pattern with three makes a triangle) and the customer–pattern
  multigraph is acyclic. Polynomial MOSP on trees is stated by Yanasse 1997a,
  PDF p. 6 of the held copy ("MOSPs whose associated graphs are trees can be solved in polynomial
  time (see Yanasse [9])", where [9] is Yanasse 1996, *Pesquisa Operacional*
  16(1):1–26) (**read**). Yanasse & Senne 2010, pre-processing 7, p. 565, lists
  trees, one-trees and complete graphs as easy cases (**read**). Yanasse &
  Limeira 2004 solve tree parts inside a branch and bound and split at
  star-like cut vertices, p. 283 and §4 (**read**). The 1-tree case goes back
  to Lins 1989 and Yanasse 1996 (secondary: Yanasse & Senne 2010, p. 560).
- **Berge-acyclic instances give block graphs** (*ours*, elementary): if the
  incidence graph of customers and patterns is a forest, two patterns share at
  most one customer and every cycle of the MOSP graph lies inside one pattern.
  The blocks are then exactly the patterns, and Chou et al. 2008 make the
  optimum polynomial. This is the "trees of cliques" family that
  `reports/ml_nature.md` §6 found defeats every bound in `_lower_bound`.
- **Octopus graphs are MOSP instances in which every customer orders at most
  two products** (*ours*): take the maximal cliques as patterns. Each vertex
  lies in at most two cliques, so each row of the matrix has at most two ones,
  and the pattern-overlap structure is a spider. Mihai & Todinca Thm 3 therefore
  makes MOSP NP-hard even with row sums ≤ 2 and a spider-shaped overlap
  structure. *To check*: whether Linhares & Yanasse 2002 or Linhares 2001
  already state hardness for row sums ≤ 2.
- **Weighted trees are tree instances with duplicated customers** (*ours*): a
  vertex of weight w becomes w identical rows, which are true twins in the MOSP
  graph. Mihai & Todinca Thm 4 then says that MOSP is NP-hard on
  edge-incidence matrices of trees whose rows are repeated polynomially often,
  while without repetition the problem is linear. Consequence for
  preprocessing: Yanasse & Senne's equivalent-node reduction (pre-processing 5,
  not implemented here) cannot be expected to give a polynomial algorithm once
  twins are collapsed into weights.
- **Our corpus contains almost none of these classes** (computed from
  `learning/data/instances.csv`, 6,376 instances): 6 forests, 42 with cyclomatic
  number ≤ 1, 96 with min-fill treewidth ≤ 2. All of the forest and unicyclic
  ones are 10–30-customer Warwick challenge instances ("2 orders per product")
  with optimum 2 or 3. The one published tree benchmark, the 50 VSPLIB trees,
  consists only of Ellis–Sudborough–Turner *minimal* trees T(3), T(4) and
  T(5) with 22, 67 and 202 vertices (Duarte et al. 2012, §5, **read**). They
  are extremal and do not represent trees in general. `pathwidth_solver/`
  solves all 50.

---

## 2. Open problems and applied-mathematics opportunities

Ranked by value per unit of effort for this repository.

### 2.1 Pathwidth of random trees: no limit law found (highest value)

- **Status.** Exact pathwidth of trees is linear time (Ellis et al. 1994; Skodinis
  2003). The worst case is pinned down exactly: m(k) = (5·3^(k−1) − 1)/2, so
  pw ≤ 1 + log₃((2n+1)/5). We found **no published distribution or limit
  theorem for the pathwidth of a random tree**, whether uniform labelled,
  Galton–Watson or random recursive. Queries to OpenAlex and to web search
  returned the Horton–Strahler literature (the binary "two-branch" analogue,
  ~log₄ n for random binary trees in the Flajolet–Raoult–Vuillemin line) and
  Biedl's equality "rooted pathwidth = Horton–Strahler number", but nothing for
  the unrooted, three-branch recursion of Thm 3.1. OEIS has no sequence about
  pathwidth: a full-text search for "pathwidth" returns one unrelated hit, and
  A060816 = m(k) does not mention trees.
- **Opportunity.** Implement the Ellis–Sudborough–Turner labelling (already
  phase 5 in `pathwidth_solver/TODO.md`). Cross-check it against the exact
  solver on all trees with up to about 20 vertices, then measure E[pw] and its
  concentration for random trees up to 10⁶–10⁷ vertices, which is minutes of
  CPU. Conjecture and then prove pw(T_n) / log n → c for each model, a
  "ternary Strahler number". Publish the counting sequences (unlabelled trees
  by n and pathwidth, the minimal-tree counts |T(k)|) in OEIS. Cheap,
  self-contained, and the exact solver provides an independent oracle.
- **MOSP angle.** A random MOSP instance with two customers per product and
  acyclic overlaps *is* a random tree, so this gives the expected optimum of
  that instance family in closed form.

### 2.2 Trees of cliques: block graphs (polynomial) against octopus graphs (NP-hard)

- **Status.** Pathwidth is polynomial on block graphs (Chou et al. 2008) and
  NP-hard on octopus graphs and weighted trees (Mihai & Todinca 2009, Thms 3–4).
  Both families are natural MOSP instances (§1, MOSP side). Mihai & Todinca leave
  two questions open (p. 10): **is pathwidth polynomial on octopus graphs with
  a constant number of legs, or with legs of constant length?** They also ask
  whether pathwidth can be approximated within a constant factor on chordal
  graphs or on weighted trees.
- **Opportunity.** (a) A block-graph MOSP generator whose optimum is known in
  polynomial time at any size, which tests the customer search and every bound
  far beyond 125 customers. It would be the first MOSP benchmark with certified
  optima at 10³–10⁴ customers. (b) Octopus instances generated from Mihai &
  Todinca's balanced 0-1 systems as a *provably hard* MOSP family with row sums
  ≤ 2. (c) Their open questions are concrete and small enough to probe with the
  exact solver: run octopuses with 3–4 legs and look for a DP or a
  counterexample to leg contiguity. This is the family `reports/ml_nature.md` §6
  and §38 identified as defeating the bounds, so a polynomial algorithm on
  block graphs is also a candidate *bound*: exact pathwidth of a spanning
  block-graph subgraph is a valid lower bound by subgraph monotonicity.

### 2.3 Outerplanar, cactus, Halin, series–parallel: polynomial in theory, no practical exact algorithm

- **Status.** Exact pathwidth is polynomial on all of these through Bodlaender &
  Kloks (Cor. 7.4), with exponents such as "sets of size O(n¹¹)" for outerplanar
  graphs (Bodlaender & Fomin). Practical exact algorithms exist only for trees
  and unicyclic graphs. Markov's characterisations for cacti (2007) and
  maximal outerplanar graphs (2008) stop short of an algorithm, and the author
  says so. Bodlaender & Kloks (§8, Final Remarks) name "more efficient algorithms for the
  pathwidth of outerplanar graphs, Halin graphs, or graphs with treewidth 2 or
  3" as open. Bodlaender & Fomin (§5) ask for fast exact or additive-constant
  algorithms on outerplanar graphs. Coudert, Huc & Sereni (Problem 1) ask
  whether ½pw(G*) − c ≤ pw(G) ≤ 2pw(G*) + c for every 2-connected planar graph.
- **Opportunity.** (a) Measure the ratio pw(G)/pw(T*) on random maximal
  outerplanar graphs, where T* is the weak dual tree, computed in linear time,
  and pw(G) comes from the exact solver at 50–500 vertices. The interval
  [pw(T*), 2pw(T*) − 1] is tight in the worst case (Coudert et al. Thm 3), but
  its typical position is unknown. (b) Build benchmark sets of cacti, random
  maximal outerplanar, Halin and series–parallel graphs with exact pathwidth.
  None exists (`paper1/benchmarks/README.md` lists none), and the
  ~O(n log n)-sized dual tree gives a certified 2-approximation as a sanity
  check. (c) Test the Kinnersley–Langston conjecture that trees are the largest
  obstructions, on the project's ≤ 11-vertex census (`learning/pwtw_exhaust.py`)
  and on all trees to 20 vertices.

### 2.4 Smaller items

- The search-number gap vs ≤ s ≤ vs + 2 is tight on trees (Ellis et al. Fig. 3.6).
  Counting how often s = vs + 2 on random trees is free once 2.1 exists. It
  bears on `lean/MOSPFormalization/Complex/EdgeSearch*.lean`.
- Caterpillars and lobsters, pw ≤ 1 and pw ≤ 2: trivial, but the MOSP reading
  ("two customers per product, acyclic, spine-shaped" gives optimum ≤ 2 or ≤ 3)
  explains the Warwick "2 orders per product" optima of 2–3 in our corpus.
- Cographs have a closed recursion (Möhring (4.4)–(4.5)). Cograph MOSP graphs
  arise when patterns nest or are disjoint, which could be a structured
  generator family. It belongs to another survey's classes.

---

## 3. Papers to obtain (paywalled or behind a browser check)

The DOIs were taken from OpenAlex, Unpaywall and web search results on
2026-10-09. "Open archive" means Unpaywall reports a free publisher copy that
was blocked to scripts by a browser check, so a person with a browser can fetch
it.

| Paper | DOI | Why |
|---|---|---|
| Skodinis, K. (2003). Construction of linear tree-layouts which are optimal with respect to vertex separation in linear time. *J. Algorithms* 47(1):40–59 | 10.1016/S0196-6774(02)00225-0 | The O(n) optimal-layout algorithm to implement |
| Scheffler, P. (1990). A linear algorithm for the pathwidth of trees. In *Topics in Combinatorics and Graph Theory*, Physica, 613–620 | 10.1007/978-3-642-46908-4_70 | Primary source of log₃(2n+1) and the complete-binary-tree formula |
| Peng, S.-L. et al. (2000). Edge and node searching problems on trees. *Theoretical Computer Science* (volume and pages to be taken from the DOI record) | 10.1016/S0304-3975(99)00241-8 | Linear node search on trees, avenue concept (open archive) |
| Chou, H.-H., Ko, M.-T., Ho, C.-W. & Chen, G.-H. (2008). Node-searching problem on block graphs. *DAM* 156(1):55–75 | 10.1016/j.dam.2007.08.007 | Polynomial on block graphs, the key for 2.2 (open archive) |
| Ellis, J. & Markov, M. (2004). Computing the vertex separation of unicyclic graphs. *Inf. Comput.* 192(2):123–161 | 10.1016/j.ic.2004.03.005 | Journal version of the held thesis (open archive) |
| Fomin, F. V. & Thilikos, D. M. (2006). A 3-approximation for the pathwidth of Halin graphs. *J. Discrete Algorithms* 4(4):499–510 | 10.1016/j.jda.2005.06.004 | Halin row (open archive) |
| Gustedt, J. (1993). On the pathwidth of chordal graphs. *Discrete Applied Mathematics* (volume and pages to be taken from the DOI record) | 10.1016/0166-218X(93)90012-D | Hardness on chordal, starlike and split graphs; polynomial on primitive starlike (open archive) |
| Takahashi, A., Ueno, S. & Kajitani, Y. (1994). Minimal acyclic forbidden minors for the family of graphs with bounded path-width. *Discrete Math.* 127:293–304 | 10.1016/0012-365X(94)90092-2 | Tree obstructions and their counts (open archive) |
| Megiddo, N., Hakimi, S. L., Garey, M. R., Johnson, D. S. & Papadimitriou, C. H. (1988). The complexity of searching a graph. *J. ACM* 35(1):18–44 | 10.1145/42267.42268 | Linear edge search on trees (ACM, OA flag set, blocked to scripts) |
| Mihai, R. & Todinca, I. (2009). Pathwidth is NP-hard for weighted trees. *FAW 2009*, LNCS 5598, 181–195 | 10.1007/978-3-642-02270-8_20 | Published version (author copy held) |
| Bodlaender, H. L. & Fomin, F. V. (2002). Approximation of pathwidth of outerplanar graphs. *J. Algorithms* 43(2):190–200 | 10.1016/S0196-6774(02)00001-9 | Journal version (TR held) |
| Govindan, R., Langston, M. A. & Yan, X. (1998). Approximating the pathwidth of outerplanar graphs. *IPL* 68(1):17–23 | 10.1016/S0020-0190(98)00139-2 (worked out from ScienceDirect PII S0020019098001392; not resolved) | 3-approximation, outerplanar |
| Kneis, J., Mölle, D., Richter, S. & Rossmanith, P. (2009). A bound on the pathwidth of sparse graphs with applications to exact algorithms. *SIAM J. Discrete Math.* 23(1):407–427 | 10.1137/080715482 | m/5.769 bound |
| Biedl, T. (2022). Horton–Strahler number, rooted pathwidth and upward drawings of trees. *IPL* 175 | 10.1016/j.ipl.2021.106230 | Strahler link, for 2.1 |
| Coudert, D., Huc, F. & Mazauric, D. (2012). A distributed algorithm for computing the node search number in trees. *Algorithmica* 63:158–190 | 10.1007/s00453-011-9524-3 | Hierarchical decomposition of trees (HAL inria-00587819 behind a browser check) |
| Korach, E. & Solel, N. Tree-width, path-width, and cutwidth (cited as [15] by Bodlaender & Kloks; venue details not retrieved because of the rate limits) | not retrieved | Primary source of pw ≤ (tw+1) log n |
| Suderman, M. (2004). Pathwidth and layered drawings of trees. *Int. J. Comput. Geom. Appl.* | 10.1142/S0218195904001433 | Tree pathwidth in drawing |
| Searching cycle-disjoint graphs (2007), LNCS (authors and volume to be taken from the DOI record) | 10.1007/978-3-540-73556-4_6 | Cactus-like class, edge search |
| Yanasse, H. H. (1996). Minimization of open orders: polynomial algorithms for some special cases. *Pesquisa Operacional* 16(1):1–26 | none found | MOSP on trees and 1-trees, the MOSP-side origin |
| Lins, S. (1989). Traversing trees and scheduling tasks for duplex corrugator machines. *Pesquisa Operacional* 9:40–54 | none found | 1-tree MOSP instances arising in practice |
| Yanasse, Becceneri & Soma (1998), polynomial MOSP for a complete graph with trees attached (cited by Yanasse & Senne 2010, p. 560; full reference to be taken from there) | none found | MOSP special case |
| Monien & Sudborough, NP-hardness of cutwidth on edge-weighted trees (cited as [21] by Mihai & Todinca; details to be taken from there) | not retrieved | Technique behind the weighted-tree hardness |

Also found and not pursued: Updating the vertex separation of a dynamically
changing tree (Waterloo thesis, 2004, hdl 10012/1163, open access);
Dereniowski, From pathwidth to connected pathwidth (STACS 2011, open access);
Lee & Sidiropoulos, Pathwidth, trees, and random embeddings (arXiv 0910.1409),
which is about metric embeddings and not about the pathwidth of random trees.
