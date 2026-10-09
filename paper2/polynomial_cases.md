# Polynomial special cases of the pathwidth complex

*2026-10-09. Question (b) for paper 3: which special cases of the pathwidth complex
can be solved in polynomial time? This note builds on the four surveys in this
folder and does not repeat them. It reads first-hand the sixteen papers obtained
on 2026-10-09 that no agent had read, and it corrects the surveys where those
papers disagree with them (§5). Not committed.*

**Conventions.** pw = pathwidth = vertex separation (Kinnersley 1992) = node
search − 1 = interval thickness − 1. For a 0/1 matrix M (rows = customers,
columns = patterns), the MOSP graph G_M has the customers as vertices and an edge
between two customers when they share a pattern, so every pattern is a clique.
Then MOSP(M) = pw(G_M) + 1, which is `MOSPGraph.lean`. "Dominance-reduced" means
that empty, duplicate and dominated columns have been removed (Yanasse & Senne
pre-processing 2). This never changes the optimum.

**Status codes.**
- **read** means read first-hand for this note, with the page from the held PDF
  (journal page where the PDF has one).
- **read (survey)** means a survey of 2026-10-09 read it first-hand, and it is
  not re-read here.
- **secondary (X)** means the statement was read only as quoted in the held paper X.
- **preview** means only the abstract and first page were read, from the 2-page
  Springer preview in `literature/`.
- **ours** means a derivation made here. Its proof is given or sketched, and every
  *ours* item was checked against the exact solver (§6), unless the text says
  otherwise.

---

## 1. Graph classes: where pathwidth is polynomial, NP-hard or open

In the "corpus" column, *inst* counts certified corpus instances (6,376) and
*graphs* counts distinct MOSP graphs (3,667) whose MOSP graph is in the class
(`paper2/poly_scan.py`, `paper2/class_scan.py`). "—" means the class was not
recognised in the scan.

### 1a. Closed formulas

| Class | pw | Algorithm | Source, theorem, page (status) | Corpus inst / graphs |
|---|---|---|---|---|
| Complete K_n | n − 1 | none needed | clique containment (Chou et al. 2008, p. 58, read) | 1,669 / 5 |
| Disjoint cliques (cluster graphs) | ω − 1 | max column sum | elementary | (inside interval) |
| Max degree ≤ 2 (paths and cycles) | 0 if edgeless, 2 if some cycle, else 1 | linear | elementary; C_n: Becceneri et al. 2004 p. 2317 (read, see §5 (r)) | 40 / —, formula agrees on all 40 |
| Caterpillar forests | ≤ 1 | linear (caterpillar test) | Kinnersley & Langston 1994, p. 172 (read (survey)) | (inside forest) |
| **Interval** | **ω − 1** | linear recognition + max clique | interval completion of itself; KKS 1997 Lemma 2.1, p. 311 (read); Bodlaender 1998 Thm 29 (read (survey)) | **2,524 / 222**, ω = opt on all |
| Proper interval | ω − 1 (= bandwidth) | linear | Bodlaender 1998 Thms 52–53 (read (survey)) | — |
| **Cographs** | recursion: pw(G+H) = max, pw(G∗H) = min(pw(G)+\|H\|, pw(H)+\|G\|) | O(n) from the cotree, O(n+m) from the graph | Möhring 1990 (4.4)–(4.5), Thm 4.8, p. 46 (read); Bodlaender & Möhring TR Lemma 3.4 (read (survey)) | **2,573 / 129**, formula = opt on all |
| Join of k graphs (complement disconnected) | min_i pw(G_i) + n − \|V_i\| | O(n+m) split, then recurse | ours, by induction from (4.5); checked 100/100 (§6) | 4,250 / 1,593 (class_scan) |
| Complete multipartite, wheels | Σn_i − max n_i; 3 | join formula | survey_products_structured.md | — |
| **Split** (clique K, independent I) | **ω − 1 or ω** (Gustedt Lemma 2.8). Ours: **ω − 1 iff some x, y ∈ K (x = y allowed) have every p ∈ I non-adjacent to x or to y**, where K is a maximum clique with V∖K independent | O(n³) (Gustedt, k = 1 of Thm 7.1); the criterion takes O(ω²·\|I\|) | Gustedt 1993 Lemma 2.8, p. 237; p. 235 (read). Criterion ours, proof in §2.2; checked 300/300 and on the corpus | **2,401 / 122**, criterion = opt on all |
| Complete ternary tree | height | — | Möhring Prop. 3.13 (read (survey)) | 0 |
| Complete binary tree, depth k | ⌈k/2⌉ | — | Scheffler 1990 (secondary: Bodlaender 1998 Thm 67) | 0 |
| Grids P_h □ P_w | min(h, w) | — | **Ellis & Warren 2008 Thm 4.1, p. 549 (read)** | 0 |
| Cylinders P_h □ C_w | min(2h, w) | — | **Ellis & Warren Thm 5.1, p. 550 (read)** | 0 |
| Tori C_h □ C_w | min(2h, 2w) if h ≠ w; 2h − 1 if h = w | — | **Ellis & Warren Thm 7.1, p. 555 (read)** | 0 |
| Orb-webs (h, w) | min(h, 2w + 1) | — | Ellis & Warren Thm 6.1, p. 551 (read) | 0 |
| Hypercubes, 3D grids, rook graphs, L(K_n), … | see survey_products_structured.md | — | there | 0 |

### 1b. Polynomial algorithms

| Class | Complexity | Algorithm | Source, theorem, page (status) | Corpus inst / graphs |
|---|---|---|---|---|
| **Trees / forests** | **O(n)** value and layout | labelling (Ellis–Sudborough–Turner), peeling (Möhring), avenues (Peng et al. 1998; Skodinis) | Möhring Thm 4.7, p. 45 (read): track number and optimal layout in O(\|V\|). Ellis et al. 1994 Thm 3.4 (read (survey)). Scheffler's three-branch rule is quoted as Lemma 8 in Peng et al. 2000, p. 434 (read) | 6 / 6 |
| **Unicyclic** (tree + 1 edge) | **O(n log n)**, with an optimal layout | Ellis–Markov reduction to tree layouts | **Ellis & Markov 2004 abstract p. 123; complexity §, p. 160 (read)** | 64 pseudoforests / 45 |
| **Block graphs** | **O(c² + bc + n)** (c cut vertices, b blocks), so O(n²); the bound is tight (Fig. 10) | avenues generalised to blocks; Thm 4: ns ≤ k ⇔ VC_k and BC_k | **Chou, Ko, Ho & Chen 2008 Thm 4, p. 59; Thm 24, p. 73; Thm 26, p. 74 (read)**. Thm 4 checked 250/250 (§6) | 1,688 (1,669 complete) / 24 |
| Complete graph with trees attached (a block graph) | polynomial | procedures CompleteGraph1, CompleteGraph | Yanasse, Becceneri & Soma 1999, Props 4–5, held copy pp. 9–11 (read; proof sketched, not checked by us) | inside block |
| **Circular-arc** | **O(n²)**; pw ≠ tw in general | min-width linear triangulation of the clique-cycle polygon | **Suchan & Todinca 2007 Thm 1, p. 3 (clique cycle decomposition); Thm 5; Thm 6, p. 10 (read)** | not recognised |
| Permutation | **linear**, given the permutation π: tw = pw, and an interval model of a minimum-ω minimal triangulation in O(n) | minimal separation lines graph | **Meister 2010 Thm 4.4 (from BKK), p. 3689; Thm 5.13 and text, p. 3699 (read; "pathwidth" not named there, so the inference is ours)**. O(n²) with no model: BKKM TR abstract (read) | — |
| Trapezoid; d-trapezoid | O(n²) with no model; O(n·tw^(d−1)) given the model; O(n^(3d+3)) with no model | — | BKKM 1995 TR abstract (read); **KKS 1997 Cor. 9.1, p. 334 (read)** | — |
| Cocomparability of dimension ≤ d | O(n^(3d+3)), no model needed | list ≤ (2n−3)^d minimal separators, then Thm 8.1 | **KKS 1997 Cor. 9.1, p. 334 (read)**; Kloks 1994 ch. 12 (preview) | — |
| **AT-free with R minimal separators** | **O(n⁵R + n³R³)**; pw = tw | every minimal triangulation is interval (Möhring 1996) | **KKS 1997 Thm 2.13 / Cor. 2.14, p. 316; Cor. 8.2, p. 333 (read)**; Möhring 1996 not held | 3,707 / 1,055 (poly only where R is polynomial) |
| Cointerval (comparability graphs of interval orders) | linear; tw = pw | explicit decomposition | Garbe 1995 abstract (preview) | — |
| Biconvex bipartite | linear | biclique concatenation | Peng & Yang 2007 abstract, p. 244 (preview) | — |
| Threshold + 1 vertex, threshold + 2 edges | polynomial | — | Krishna et al. 2010 abstract (preview) | — |
| **Primitive starlike** (peripheral cliques pairwise disjoint) | **O(n²)** | generalised partition, pseudo-polynomial DP | **Gustedt Thm 5.8, p. 243 (read)** | see §2 (S2) |
| **k-starlike** (each peripheral clique has ≤ k vertices outside the centre) | **O(n^(2k+1))** | DP over sorted decompositions | **Gustedt Thm 7.1, p. 246 (read)** | see §2 |
| Starlike, small centre | O(4^(α₀)·r + n), α₀ = central clique size (FPT in α₀) | Algorithm 6.3 | **Gustedt Thm 6.4, p. 246 (read)** | see §2 |
| Octopus, every leg's separators of equal size | polynomial | reduce to primitive starlike | **Mihai & Todinca 2009 Thm 5, author copy p. 10 (read)** | — |
| Bounded treewidth t (cactus, outerplanar, Halin, series–parallel, k-outerplanar, almost-trees) | polynomial for fixed t, **impractical** (full sets of size O(n^(4t+3))) | Bodlaender–Kloks DP | **Bodlaender & Kloks TR Thm 7.3, Cor. 7.4, p. 35 (read)** | tw ≤ 2: 96 / 76 (27 inst not covered by a practical class) |
| **pw ≤ k, k fixed** (MOSP "≤ k stacks?") | **linear** for each k | tree decomposition of width ≤ k, then Thm 6.1(ii) | **Bodlaender & Kloks Thm 6.1, pp. 33–34 (read)**; O(n²) nonconstructive: Möhring Thm 3.8, p. 33 (read); MOSP ∈ FPT: Linhares & Yanasse 2002 Cor. 1, p. 1764 (read) | all |
| pw ≤ 1 / pw ≤ 2 | linear: caterpillars / 110 minor obstructions | — | Kinnersley & Langston 1994 (read (survey)); acyclic obstructions for pw ≤ k have (5·3^k − 1)/2 vertices and more than (k!)² of them; counts 1, 1, 10, 117,480, 14,403,197,619,396,707,660 for k = 0…4: **Takahashi, Ueno & Kajitani 1994 Cor. 2.14, p. 299 (read)** | — |

### 1c. Approximation only (exact complexity open in practice)

| Class | Result | Source (status) |
|---|---|---|
| Halin | linear time, returns k with k − 1 ≤ pw ≤ lw ≤ 3k (k = pw(skeleton) + 1) | **Fomin & Thilikos 2006 Thm 9, p. 509 (read)**. p. 500: "no explicit algorithm is known for graphs of treewidth 2"; no efficient exact or approximate algorithm for any class of treewidth ≥ 3 |
| Outerplanar (biconnected) | pw(T*) ≤ pw ≤ 2pw(T*) + 2 | Bodlaender & Fomin TR (read (survey)) |
| Cocomparability, cotriangulated, convex | pw = O(tw²), ≤ 3tw + 4, ≤ 2tw + 1 | Kloks & Bodlaender TR (read (survey)) |

### 1d. NP-hard

| Class | Source (status) |
|---|---|
| **Chordal** | **Gustedt Thm 4.1, p. 239 (read)** |
| **Starlike** (a central clique, every other maximal clique meets only it) | **Gustedt Cor. 4.3, p. 241 (read)** |
| **Octopus** (chordal, the clique tree a spider, every vertex in ≤ 2 maximal cliques) | **Mihai & Todinca Thm 3, author copy p. 5 (read)** |
| Chordal dominoes (every vertex in ≤ 2 maximal cliques) | Kloks, Kratsch & Müller 1995 abstract (preview); implied by octopus |
| **Weighted trees** (= trees with clique modules) | **Mihai & Todinca Thm 4, p. 9 (read)** |
| **Distance-hereditary, circle** | **Mihai & Todinca pp. 1–2 and p. 9 (read)**: DH ⊂ circle |
| Bipartite distance-hereditary; hence **chordal bipartite** | KBMK ESA'93 (secondary: Peng et al. 2000 p. 430, Chou p. 56, read); chordal bipartite "implied from [14]": Peng & Yang 2007 p. 245 (preview) |
| **Cobipartite**, hence cocomparability and AT-free | ACP 1987 (secondary: **KKS 1997 p. 309, read**; KBMK ESA'93 preview p. 1) |
| Bipartite | KBMK ESA'93 preview p. 1 citing [20] (preview) |
| Planar, maximum degree 3 | Monien & Sudborough 1988 (secondary: Ellis & Warren p. 545, Chou p. 56, read) |
| Line graphs of graphs with pendant edges (MOSP with ≤ 2 products per customer) | **Linhares & Yanasse 2002 Prop. 1, p. 1761 (read)**, from modified cutwidth |
| General | Kashiwabara & Fujisawa 1979 (not held); Linhares & Yanasse Prop. 1 |

### 1e. Open (as stated in the papers)

- **Octopus graphs with a constant number of legs, or with legs of constant
  length** (Mihai & Todinca, author copy p. 10, read). With a constant number of
  cliques the problem is polynomial, because there are finitely many foldings.
- **A practical exact algorithm for treewidth-2 classes**: series–parallel,
  outerplanar, cactus (Fomin & Thilikos p. 500; Bodlaender & Kloks §8 (read);
  Markov 2007, 2008 (read (survey))), and Halin.
- **Distance-hereditary graphs** were open in Möhring 1990, p. 46 (read). They
  are now settled as NP-hard.
- **Biconvex bipartite pathwidth** is called "unknown" in Peng & Yang's
  introduction, p. 245, and is solved there (linear).
- Classes not settled in anything read here: interval bigraphs, permutation
  bipartite with weights, **bounded asteroidal number**, and **chordal with
  bounded leafage**. The last is the natural parameter between starlike (hard)
  and interval (leafage 2); no source was found.

---

## 2. Translation to the MOSP matrix

### 2.1 Matrix conditions

| Matrix condition (rows = customers, columns = patterns) | G_M | MOSP complexity | Proof / source |
|---|---|---|---|
| Each customer in ≤ 1 pattern (row sums ≤ 1) | disjoint cliques | **= max column sum** | trivial |
| **Row sums ≤ 2 and column sums ≤ 2** (dominance-reduced) | max degree 2 | **1, 2 or 3** (3 iff some cycle) | elementary; 40 corpus instances, all agree |
| **Column sums ≤ 2** (≤ 2 customers per pattern) | any graph | **NP-hard** | Yanasse 1997a Prop. 5 (read (survey)) |
| …and G_M planar with max degree 3 | — | NP-hard | Monien & Sudborough (secondary) |
| …and triangle-free with the customers split into two sides | bipartite | NP-hard | (preview) |
| **Row sums ≤ 2** (each customer needs ≤ 2 products) | line graph of the pattern multigraph | **NP-hard** | **Linhares & Yanasse 2002 Prop. 1, p. 1761 (read)**. Still NP-hard when, in addition, G_M is chordal and the patterns' overlaps form a spider: **Mihai & Todinca Thm 3** (octopus) |
| **Consecutive ones in the rows** (the dominance-reduced matrix has a column order in which every customer's patterns are consecutive) | interval, and the matrix is conformal | **= max column sum**; the C1P order is optimal | ours: the C1P order opens a customer only on its own patterns. **Equivalence (ours): row-C1P after dominance ⇔ G_M interval and every maximal clique of G_M inside one pattern** (⇒ by Helly on intervals; ⇐ the patterns are then the maximal cliques, KKS Lemma 2.1, p. 311). The value claim was checked 200/200. Corpus: **21** instances |
| **Consecutive ones in the columns** (a customer order in which every pattern is a block of consecutive customers) | **proper** interval | **= max column sum** | ours: u < w < v and uv in a pattern put w in that pattern, so G_M is umbrella-free. Any clique lies in one pattern, so ω = max column sum. After dominance, sorting the blocks by left end makes every customer's run consecutive, which gives row-C1P as well. Checked 200/200 |
| **G_M interval** (no matrix condition needed) | interval | **= ω(G_M)**, which can exceed the max column sum (three 2-patterns on a triangle give 3 against 2) | Möhring Thm 3.2, p. 29 (read). Corpus: 2,524, of which only 21 are conformal. ω > max column sum on 4,992 of 6,376 corpus instances |
| **Circular ones in the rows** (columns on a cycle, every customer an arc) | circular-arc; the columns *are* a clique cycle decomposition | **O(n²)** | **Suchan & Todinca Lemma 2, Thm 1 (p. 3), Thm 6 (p. 10) (read)**. Every circular-arc graph arises. Recognition: Booth–Lueker / Tucker, not held. Consequence pw ≤ 2ω − 1 checked 150/150 |
| **Berge-acyclic**: customer–pattern incidence graph a forest (dominance-reduced) | **block graph**, whose blocks are the patterns | **O(c² + bc + n)** | ours, proof in §2.2; Chou Thm 26. Checked 300/300. The converse fails (three 2-patterns on a triangle), so test G_M itself: 1,688 / 24 block graphs in the corpus, 19 instances non-complete |
| …and every pattern has 2 customers | forest | **O(n)** | Möhring Thm 4.7 |
| Incidence graph with one cycle and 2-customer patterns | unicyclic | O(n log n) | Ellis & Markov 2004 |
| **Join (complement split)**: customers split into groups V_1…V_k, every cross-group pair sharing some pattern | join | **MOSP(M) = min_i MOSP(M[V_i]) + n − \|V_i\|**, exact and recursive | Möhring (4.5), p. 46 (read), induction ours; checked 100/100 and on 2,573 cographs. Applies to 4,250 instances |
| Fully decomposable by components and joins | cograph | linear | Möhring Thm 4.8 |
| **Central pattern**: a pattern P₀ contains every customer who needs ≥ 2 patterns (customers outside P₀ need exactly one) | starlike (chordal, star clique tree centred at P₀) | **NP-hard** in general; **O(4^\|P₀\|·r + n)**; **O(n^(2k+1))** if every other pattern has ≤ k customers outside P₀; **O(n²)** if the other patterns are pairwise disjoint | ours (bags P₀, P_i form a clique star decomposition); **Gustedt Cor. 4.3, Thms 6.4, 7.1, 5.8 (read)**. Gustedt's hardness instance *is* such a matrix: P₀ = V(G), one pattern per edge {u, w} plus n private customers. Corpus: **5** instances (all Simonis) |
| …with k = 1: every other pattern has exactly one customer outside P₀ | split | **∈ {ω, ω + 1}**, decided by the two-vertex criterion | Gustedt Lemma 2.8; criterion ours |
| **Two patterns together contain every customer** | cobipartite (two cliques) | **NP-hard** | ours, translation: any cobipartite graph is realised by its two cliques plus the cross edges as 2-patterns; ACP 1987 via KKS p. 309 |
| Each customer in ≤ 2 *maximal* patterns, G_M chordal | chordal domino | NP-hard | preview; octopus |
| Duplicate customers (identical rows) on a tree instance | weighted tree | **NP-hard**, although the instance without duplicates is linear | Mihai & Todinca Thm 4: collapsing twins into weights (Yanasse–Senne pre-processing 5) cannot give a polynomial algorithm |
| Fixed number of stacks k | — | **linear** decision for each fixed k | Bodlaender & Kloks Thm 6.1 |

### 2.2 Proofs of the *ours* items

- **Split criterion.** Choose K a maximum clique with V∖K = I independent. Every
  p ∈ I has N(p) ⊊ K. Some bag of any path decomposition contains K (Helly). If
  the width is |K| − 1, that bag is exactly K, so every p lies strictly left or
  right of it. A central vertex used by a left p stays alive until the K-bag, so
  the bag of the last left p holds ∪_{left} N(p) plus p. Hence width |K| − 1 ⇔ I
  splits into L and R with ∪_L N ≠ K and ∪_R N ≠ K ⇔ some x, y ∈ K have every p
  missing x (go left) or missing y (go right). Sufficiency is by the explicit
  bags (∪_{q ≤ p} N(q)) ∪ {p}, then K, then the symmetric right side. Note that a
  maximum clique need not have an independent complement (`poly_scan.py` first
  picked one that did not, and got 7 false mismatches).
- **Berge-acyclic ⇒ block graph.** A cycle of G_M that uses at least two distinct
  patterns P₁…P_m (consecutive patterns distinct, with distinct transition
  customers u_i ∈ P_i ∩ P_{i+1}) gives a closed walk P₁u₁P₂…P_m u_m P₁ in the
  incidence forest that never backtracks. That is impossible, so every cycle lies
  in one pattern's clique, every 2-connected subgraph is a clique, and the blocks
  are the (maximal) patterns. Dominance must be applied first: Q ⊂ P with
  |Q| ≥ 2 makes a 4-cycle in the incidence graph.
- **Column-C1P and row-C1P**: as in the table.

### 2.3 What the matrix view adds

- **The clique cycle decomposition of Suchan & Todinca is the MOSP matrix.**
  Their Definition 4, Algorithm FillFolding and Theorem 2 (pp. 4–5, read) say:
  for *any* edge clique cover X of G, every minimal interval completion of G is
  FillFolding(G, Q) for some ordering Q of X. Read with X = the patterns, this is
  exactly "some pattern sequence realises pw(G_M) + 1", an independent 2007
  graph-theoretic proof of MOSP = pw + 1. Mihai & Todinca (Thm 1, p. 4) restate
  it. Paper 2 should cite it beside Fellows–Langston and Yanasse.
- The useful *recognisable* layers are, in order of corpus yield: complete,
  interval (ω), cograph or join (formula), split (criterion), block (Chou),
  unicyclic (Ellis–Markov). All of these test G_M, not the matrix. The matrix
  conditions (C1P, circular ones, Berge-acyclic, central pattern) are sufficient
  conditions that are easier to state to an OR reader.

---

## 3. Input-specific cases for the other members

The table below says, for each member, which graph carries its value, and
therefore which input condition makes it polynomial.

| Member | Natural input | Graph whose pw + c it equals | Polynomial cases, in input terms |
|---|---|---|---|
| **Gate matrix layout** | net–gate matrix (nets = rows) | incompatibility graph = G_M (Möhring Lemma 3.1, Thm 3.2, p. 29, read) | identical to §2. Möhring lists: tree incompatibility graph O(n) (Thm 4.7, p. 45), cographs O(n) (Thm 4.8), the chordal overlap condition (4.6) (Thm 4.9, p. 46, from Gustedt), split graphs (p. 46), a fixed number of tracks O(n²) nonconstructive (Thm 3.8, p. 33), and O(n^(2k²+4k+8)) by DP [EST87] (p. 33). 2 tracks ⇔ caterpillar forest; 3 tracks ⇔ none of 110 obstructions (Kinnersley–Langston). Möhring p. 49: on-line algorithms that fail on interval inputs [DKL87] are fixed by MPQ-trees |
| **One-dimensional logic** | gates with their net sets | connection graph H = G_M with gates as patterns | identical to §2 (gates ↔ patterns, nets ↔ customers) |
| **Multiple PLA folding** | net–gate matrix | = GML (paper 2 (E8)) | as GML |
| Simple PLA folding (≤ 2 nets per track) | net–gate matrix | *not* in the complex (paper 2, false as stated) | Möhring p. 47 (read): constrained PLA folding on trees [Hu & Kuo 1987]; block folding and constrained block folding on partial k-trees; orderability polynomial for constrained folding [Ravi 1988]. NP-hard in general (Thms 4.1–4.6) |
| **Interval thickness, node search, vertex separation, narrowness, Lengauer's VSG, minimum progressive pebbling of a graph** | a graph | the input graph | §1 directly. Node search on trees and block graphs comes with optimal *strategies* in O(n) (Chou Thm 24, p. 73) |
| **Progressive black–white pebbling of a dag D** | a dag | the moral graph D_u (arcs + a clique on each in-neighbourhood) = G_{M_D}, column v = N⁻[v] (paper 2 (E11)) | **out-forests** (in-degree ≤ 1): D_u = the underlying forest, O(n). **In-forests** (out-degree ≤ 1, expression trees): M_D is Berge-acyclic, so D_u is a **block graph**, O(n²) by Chou (ours; checked 200/200). Any dag whose moral graph is interval, a cograph, split, … |
| Pebbling of G_d (pw + 2) | a graph | the graph | §1 |
| Edge search (band vs ≤ es ≤ vs + 2, not exact) | a graph | — | NP-complete (Megiddo et al. 1988 Thm 1, p. 20); **trees: linear value (Thm 3, p. 28), strategy O(n log n) (Thm 4, p. 32)**, linear strategy (Peng et al. 2000 Thm 24, p. 443); sprout trees es = ns (Thm 20, p. 438); es ≤ 3 recognisable in linear time (Megiddo Thm 7, p. 41) (all read). Every polynomial class in §1 gives es within +2 |
| Split bandwidth (pw ≤ sb ≤ pw + 1) | a graph | — | every §1 class gives sb within 1 |
| Random 3-GML | random n × m Boolean matrix, m = n^α | — | not a polynomial case but the matching threshold: **Karoński & Szymkowiak 2001 Thm 1, p. 180 (read)**: Pr(yes for 3-GML) → 1 if p ≪ p₃*, → 0 if p ≫ p₃*, with p₃* = m^(−1/4) n^(−1) for α ≤ 40/21 and m^(−1/2) n^(−11/21) for α > 40/21 |

### MOSP literature special cases

| Case (in their graph: nodes = item types, arcs = 2-patterns) | Status | Source |
|---|---|---|
| Trees | polynomial | Yanasse (1997, SBPO, "An exact algorithm for the tree case"), not held; cited by Yanasse & Senne 2010 p. 560, and by Yanasse 1997a p. 6 as Yanasse [9] (1996) (read). The algorithm deletes vertices of degree ≥ 3 and combines optimal sub-sequences (YBS 1999 p. 9, read) |
| 1-trees (unicyclic) | polynomial | Yanasse 1996, *Pesquisa Operacional* 16(1):1–26, not held (secondary: YS 2010 p. 560; YBS 1997 p. 3; YBS 1999 p. 3). **Lins 1989 is a heuristic** for 1-trees, not an exact algorithm (secondary, same pages) |
| "0-1 common vertex polygon" graphs | polynomial | Yanasse 1996 (secondary: YBS 1999 p. 3); definition unseen |
| Complete graph with trees attached | polynomial | YBS 1998 SBPO (secondary: YS 2010 p. 560); **stated and proved in YBS 1999 Props 4–5 (read)**. It is a block graph, so Chou 2008 covers it |
| Complete graphs | trivial (= n) | YS 2010 p. 565 |
| Recognition cost of trees, one-trees, complete | O(m), O(m), O(m²) | YS 2010 pre-processing 7, p. 565 (read) |
| Trees inside a branch and bound; split at star cut vertices | exact on the tree parts | Yanasse & Limeira 2004 (read (survey)); Becceneri et al. 2004 p. 2317 (read) also solves trees, cycles and 1-tree components exactly |
| Fixed k | FPT | Linhares & Yanasse 2002 Cor. 1, p. 1764 (read) |

---

## 4. Corpus impact

From `paper2/poly_scan.py` → `poly_scan.json` (one process, about 2 minutes).
Every formula was checked against the certified optimum with zero mismatches:
- ω on 2,524 interval instances;
- the split criterion on 2,401;
- the join recursion on 2,999 resolved instances;
- the degree-2 formula on 40.

| Layer | Instances (of 6,376) | Non-complete | Distinct graphs |
|---|---|---|---|
| complete (opt = n) | 1,669 | — | 5 |
| interval (opt = ω) | 2,524 | 855 | 222 |
| cograph (formula) | 2,573 | 904 | 129 |
| interval or cograph | 2,855 | 1,186 | — |
| split, beyond interval or cograph | +20 | | |
| block, beyond interval, cograph and split | +10 | | |
| forest / pseudoforest | 6 / 64 | | 6 / 45 |
| **any class at top level** | **2,935** | | |
| **recursively: every prime piece of the component / co-component split in a practical class** | **3,059** (48.0%) | **1,390** | 436 |
| … of which only through the recursion | 124 | | |
| … whose pieces need block or unicyclic algorithms (not implemented) | 60 | | 41 |
| treewidth ≤ 2 but no practical class (polynomial in theory only) | 27 | | |
| AT-free, not covered (pw = tw, exact treewidth) | 728 | | |

Prime pieces used: interval 404 instances, unicyclic 50, split 22, block 10.

**Per collection (practical / total)**:

| Collection | Practical / total |
|---|---|
| Simonis | 2,111 / 3,630 |
| Harvey | 894 / 2,130 |
| Faggioli–Bentivoglio | 36 / 300 |
| Challenge | 7 / 46 |
| Wilson | 7 / 20 |
| SCOOP | 3 / 24 (B_39Q18_82, B_CARLET_137, B_CUC28A_138, all interval) |
| **Chu & Stuckey** | **1 / 200** (Random-30-30-10-5, a split piece) |
| Shaw | 0 / 25 |
| Miller | 0 / 1 |

The matrix conditions yield little:
- row-C1P after dominance: 21;
- central pattern (starlike): 5;
- Berge-acyclic with 2-patterns (forest): 6;
- row and column sums ≤ 2: 40.

The honest reading: the layers solve almost half the corpus, but almost all of
it in the challenge collections, and **1 of the 200 hard Chu & Stuckey
instances**. As a part-1 contribution they decide nothing about hard instances.
This is consistent with the plan's kill criterion, which is to be measured in
nodes.

---

## 5. Corrections to the four surveys and the plan

(a) **Peng et al. 2000 (TCS 240) is about *edge* search.** Its contributions are:
- a linear-time optimal edge-search strategy for trees (Thm 24, p. 443);
- es = ns on sprout trees (Thm 20);
- a linear min-cut layout for degree-3 trees (Thm 25).

For linear node search on trees it cites Scheffler (1990, 1992) and Möhring Thm
4.7 (p. 430–431). The linear optimal node-search *strategy* is Peng et al.,
COCOON'98, LNCS 1449:279–288 (Chou ref. [24]). This corrects
survey_trees_sparse.md (row "Trees: algorithm, optimal layout") and Mihai &
Todinca's attribution [25].

(b) **Circle graphs: pathwidth is NP-hard.** Mihai & Todinca p. 2: DH ⊂ circle,
and DH is NP-hard (also their Thm 4 corollary, p. 9). survey_intersection_classes.md
said "pw: no result found". The trees survey had this right.

(c) **Chordal bipartite: the source is identified.** Peng & Yang 2007 (preview,
p. 245) say NP-completeness is "implied from [14]", the bipartite
distance-hereditary hardness of Kloks, Bodlaender, Müller & Kratsch (ESA'93). That
attribution is confirmed in Peng et al. 2000 p. 430 and Chou p. 56. The result is
still second-hand.

(d) **Split graphs.** Gustedt Lemma 2.8 (p. 237) gives pw ∈ {ω − 1, ω}, and the
algorithm is O(|V|³) (p. 235). We add an explicit criterion (§1a). The
intersection survey's "tw = ω − 1, pw not" is right but incomplete.

(e) **Gustedt, first-hand.** The results, all read, are:
- chordal NP-complete (Thm 4.1, p. 239);
- starlike NP-complete (Cor. 4.3, p. 241);
- primitive starlike O(n²) (Thm 5.8, p. 243);
- starlike O(4^(α₀)·r + n) (Thm 6.4);
- k-starlike O(n^(2k+1)) (Thm 7.1, p. 246).

The surveys had these only from snippets or through Möhring.

(f) **KKS 1997, first-hand.** O(n⁵R + n³R³) for both tw and pw (Cor. 8.2, p. 333).
The statement of Möhring's AT-free theorem is Thm 2.13 / Cor. 2.14 (p. 316). Its
proof (Möhring 1996) is still not held. Cocomparability of dimension d is
O(n^(3d+3)) without a model (Cor. 9.1, p. 334).

(g) **Permutation graphs.** Meister 2010 never says "pathwidth". The linear-time
pathwidth (given π) is an inference from Thm 4.4 and the text after Thm 5.13
(p. 3699), not a stated theorem. Mark it *ours, from read statements*.

(h) **Halin.** Fomin & Thilikos Thm 9 is "k − 1 ≤ pw ≤ lw ≤ 3k", with k =
pw(skeleton) + 1. That is a factor-3 approximation of linear width, not of pw
exactly. Confirmed first-hand.

(i) **Takahashi et al. 1994**, first-hand: Cor. 2.14, p. 299. Tree obstructions
for pw ≤ k have (5·3^k − 1)/2 vertices, more than (k!)² of them, with the exact
counts in §1b. This agrees with the trees survey's m(k), shifted by one, and
upgrades the random survey's E6 ("super-exponential") to a stated bound.

(j) **Ellis & Warren 2008**, first-hand: the products survey's *measured*
pw(C_m □ P_n) = min(m, 2n) and pw(C_m □ C_n) = 2m (m < n) are theorems
(Thms 5.1, 7.1). These are not new values.

(k) **Chou et al. 2008**, first-hand: O(c² + bc + n), tight (p. 74), not just
"polynomial". The open question it answers was posed in Peng's 1999 PhD thesis.

(l) **Ellis & Markov 2004**, first-hand: O(n log n) with an optimal layout.

(m) **Coudert, Huc & Mazauric 2012**, first-hand: the abstract matches the trees
survey.

(n) **Megiddo et al. 1988**, first-hand: also a linear recognition of edge search
number 3 (Thm 7, p. 41), which the surveys did not list.

(o) **Karoński & Szymkowiak 2001**, first-hand: the threshold is in §3. The random
survey (R19) had the abstract only.

(p) **Harper 1966 / 1999, Wang–Wu–Dumitrescu 2009**, first-hand:
- Harper 1966 proves that Hales numberings are bandwidth-optimal on Q_n (Thm 1,
  p. 388), but only *states* the formula Σ C(m, ⌊m/2⌋), "by induction" (III(d),
  p. 393).
- Wang et al. give its first simple proof (their Thm 2 is Harper's).
- Both are about bandwidth. Pathwidth of Q_n remains Chandran–Kavitha.
- Harper 1999: the vertex-isoperimetric problem on Hamming graphs has *no nested
  solutions* (abstract, p. 285). There is only an asymptotically sharp
  continuous lower bound, so pw(K_q^d) has no formula from this route.

(q) **Broersma, Dahlhaus & Kloks 2000** gives linear *treewidth* on DH graphs
(Thm 54, p. 399) and nothing on pathwidth. Citing it beside pathwidth hardness
is fine, but it is not a pathwidth result.

(r) **Becceneri et al. 2004, p. 2317**: "if G is a polygon then the MOSP is
solved in linear time and ξ = 2". Under the count used in this repository and in
Linhares–Yanasse, a polygon has optimum **3** (pw(C_n) = 2; checked for n =
3…14). ξ = 2 holds only if a stack counts as closed during its last pattern. This
is a convention difference to note, or an error.

(s) **The plan and the trees survey on Berge-acyclic instances.** The claim holds
(proof §2.2, 300/300 checks), but only **after dominance**: a dominated pattern
creates an incidence cycle. The converse fails, so the practical test is "G_M is
a block graph", not the matrix condition. The plan's "read second-hand" for Chou
is now first-hand.

(t) **The trees survey's "to check" item.** Linhares & Yanasse 2002 Prop. 1
already gives NP-hardness with ≤ 2 products per customer: the rows are the edges
of G plus single-1 padding rows (p. 1761). The plan already says so. The octopus
result adds chordality and a spider overlap.

(u) **Intersection survey §5 item 4.** Its hedged statement "chordal + ≤ 2
products per customer is NP-hard (if KKM holds)" is confirmed independently and
first-hand by Mihai & Todinca Thm 3, because octopus graphs are chordal dominoes.

(v) **Yanasse, Becceneri & Soma 1999, Props 4–5**, held and read, solve
"complete graph with trees attached", a block-graph case nine years before Chou.
The surveys list only the unheld 1998 SBPO version. Prop. 4 carries an ordering
hypothesis ((fpw_i, pw_i) totally ordered). The proof is an informal counting
argument and was not checked here.

(w) **Suchan & Todinca 2007 Thm 2** (any edge clique cover realises every minimal
interval completion by a folding) is an independent proof of MOSP = pw + 1 for
arbitrary pattern sets (§2.3). None of the surveys noticed it.

---

## 6. Checks run

`paper2/poly_checks/checks.py` (one core, niced). Exact pathwidth comes from
`pathwidth_solver`, refutation-proved, and at n ≤ 18 also from the subset DP.
Output is in `poly_checks/checks.out`.

| Check | Result |
|---|---|
| Chou et al. Thm 4 (block graphs, n 4-15) | 150/150 agree |
| Chou Thm 4 on random trees (n 5-16) | 100/100 agree |
| split criterion (n 3-19; pw=omega-1 on 286, omega on 14) | 300/300 agree |
| Berge-acyclic matrix => block MOSP graph | 300/300 agree |
| row-C1P => MOSP = max column sum | 200/200 agree |
| column-C1P => MOSP = max column sum | 200/200 agree |
| circular-ones rows => pw <= 2 omega - 1 | 150/150 agree |
| in-forest dag => moral graph D_u is a block graph | 200/200 agree |
| polygon C_n, n 3-14: MOSP = 3 | 12/12 agree |
| join rule pw = min_i pw(G_i) + n − \|V_i\| | 100/100 agree |

The split sample is skewed: 286 of the 300 have pw = ω − 1. The ω-case was hit 14 times, and on the corpus 2,401 times with no mismatch. The row-C1P check tests MOSP = max column sum; the ⇔ with interval-and-conformal is proved, not sampled. Chou's Theorem 4 was implemented as a recursion that is exponential in practice (n ≤ 16), as a check of the theorem, not of its algorithm.

---

## 7. Papers to obtain

| Paper | Why |
|---|---|
| Yanasse (1996) Minimization of open orders: polynomial algorithms for some special cases, *Pesquisa Operacional* 16(1):1–26 (also INPE/LAC TR 007) | the MOSP-side origin: tree, 1-tree, "0-1 common vertex polygon" |
| Yanasse (1997) An exact algorithm for the tree case of the MOSP, XXIX SBPO | the tree algorithm |
| Yanasse, Becceneri & Soma (1998), XXX SBPO | complete graph with trees (the 1999 paper has the content) |
| Lins (1989) *Pesquisa Operacional* 9:40–54 | 1-tree instances in practice |
| Möhring (1996) Triangulating graphs without asteroidal triples, *DAM* 64:281–287 | the proof of AT-free ⇒ pw = tw |
| Peng, Ho, Hsu, Ko & Tang (1998) LNCS 1449:279–288 | linear optimal node search on trees |
| Peng, Ko, Ho, Hsu & Tang (2000) Graph searching on some subclasses of chordal graphs, *Algorithmica* 27:395–426 | interval, split, k-starlike search strategies |
| Peng (1999) PhD thesis, National Tsing Hua University | the block-graph question |
| Skodinis (2003) *J. Algorithms* 47:40–59; Scheffler (1990, 1992) | linear tree layouts |
| Kloks, Bodlaender, Müller & Kratsch (1993) ESA, full text (preview only) | bipartite DH, hence chordal bipartite, NP-hardness |
| Kloks, Kratsch & Müller (1995) Dominoes, full text (preview only) | chordal domino hardness proof |
| Peng & Yang (2007) TAMC, full text (preview only) | biconvex linear algorithm |
| Garbe (1995) WG, full; Krishna et al. (2010), full | cointerval; threshold + 1v |
| Arnborg, Corneil & Proskurowski (1987) *SIAM JADM* 8 | cobipartite hardness (the "two patterns cover everyone" MOSP result) |
| Monien & Sudborough (1988) *TCS* 58 | planar degree-3 hardness |
| Kashiwabara & Fujisawa (1979) | original NP-completeness (also missing for paper 2) |
| Booth & Lueker (1976) PQ-trees; Tucker (1970) circular ones | recognition of the matrix conditions in §2 |
| Heggernes, Suchan, Todinca & Villanger (2006) TR RR-2006-09 (LIFO) | the folding characterisation of minimal interval completions |
| Hu & Kuo (1987) *Networks* 17; Ravi (1988) | PLA folding on trees |
| Deo, Krishnamoorthy & Langston (1987) *IEEE TCAD* 6 | GML exact and approximate |
