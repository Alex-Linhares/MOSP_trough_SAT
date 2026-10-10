# Pathwidth on intersection and perfect-graph classes: a survey for Paper 2

*2026-10-09. Literature survey for a possible paper on the applied mathematics
of pathwidth on special graph classes. Not committed.*

## 0. Why this transfers to MOSP, and how to read the table

`MOSP optimum = pathwidth(MOSP graph) + 1` is a sorry-free Lean theorem
(`lean/MOSPFormalization/MOSPGraph.lean`). Pathwidth is also vertex separation
(Kinnersley 1992), node search number − 1 and interval thickness − 1 (Bodlaender
1998, Theorem 29 p. 13, Theorem 57 and Corollary 58 p. 27), so a result stated
under any of these names transfers. **Every graph is a MOSP graph**: give each
edge its own two-customer pattern (Yanasse 1997a, Proposition 5; Fellows &
Langston 1987, Lemma 4.1). Two consequences follow.

- An NP-hardness result on a class C gives an NP-hard MOSP restriction: the
  instances whose MOSP graph lies in C.
- A polynomial algorithm on C solves every MOSP instance whose MOSP graph lies
  in C. Which class a MOSP graph falls in is decided by the matrix, and §4
  measures this on our corpus.

**Status codes.** *Read* means the statement was read in the paper, with page
given. *Read (secondary)* means it was read in a held paper that cites the
original. *Abstract only* means the original's abstract was read. *Snippet* means
only a search-engine summary was seen, so the claim is unverified. *Inferred* means
it is derived here from read statements by a stated containment.
"Held" is the file in `literature/`.

## 1. The table

| Class | Complexity / formula | Algorithm & time | Source, theorem, page (status) | Held? |
|---|---|---|---|---|
| **Interval** | **pw = tw = ω − 1** (so MOSP = ω) | recognition + max clique, linear | Bodlaender 1998 Thm 29 p. 13 (pw ≤ k−1 ⇔ interval thickness ≤ k) (read); Bodlaender & Möhring TR 1990 Lemma 2.1 p. 4: χ = ω = tw + 1 = pw + 1 (read) | `1998-Bodlaender-Partial-k-Arboretum...`, `1990-Bodlaender-Mohring-...` |
| **Proper interval** | pw = ω − 1. Also bandwidth = ω − 1 | linear | Bodlaender 1998 Thm 52 p. 25 (bw ≤ ω − 1), Thm 53 p. 25 (Kaplan–Shamir: bandwidth = proper pathwidth) (read) | arboretum |
| **Threshold** | pw = ω − 1 | linear | *Inferred*: threshold ⊂ cograph ∩ interval (a standard containment, not read here). Krishna et al. 2010 on *parameterized* threshold graphs: title only | no |
| **Cographs** | **pw = tw** (Thm 3.2). Closed recursion: pw(G ∪ H) = max, **pw(G × H) = min(pw(G) + \|W\|, pw(H) + \|V\|)** (Lemma 3.4) | O(n) from the cotree, O(n + e) from the graph; the decomposition and an optimal node search in O(n) | Bodlaender & Möhring TR RUU-CS-90-7: Lemma 3.4 p. 6, Thm 3.2 p. 7, Thms 4.1–4.5 pp. 7–10 (read); SIAM JDM 6 (1993) 181–188 abstract (read); Möhring 1990 (4.4)–(4.5), Thm 4.8 p. 46 (read) | `1990-Bodlaender-Mohring-Pathwidth-Treewidth-Cographs-TR-RUU-CS-90-7.pdf` |
| **Permutation** | **pw = tw** | O(nk²) decision given the matching diagram; O(n²) with no model (via trapezoid); 2-approx pw ≤ 2tw in O(nk) | Bodlaender, Kloks & Kratsch TR 1992 abstract p. 1 (read) = SIAM JDM 8 (1995) 606–616 abstract (read); BKKM 1995 TR abstract p. 1 (read); Kloks & Bodlaender TR RUU-CS-92-29 abstract p. 1 (read). Meister 2010 gives linear-time *treewidth*, so linear pw too (title only, inferred) | `1992-Bodlaender-Kloks-Kratsch-...`, `1992-Kloks-Bodlaender-...` |
| **Trapezoid, d-trapezoid** | **pw = tw** (AT-free) | O(n·tw^(d−1)) given a d-trapezoid model; trapezoid O(n²) with no model | Bodlaender, Kloks, Kratsch & Müller TR UU-CS-95-34, abstract p. 1, Thm 2.2 p. 5 (read) | `1995-Bodlaender-Kloks-Kratsch-Muller-...` |
| **Cocomparability of bounded dimension** | pw = tw, polynomial | — | Kloks, Kratsch & Spinrad (WG 1993), cited in BKKM TR p. 2 (read secondary) | no |
| **Comparability graphs of interval orders** (= co-interval) | pw = tw, linear | linear | Garbe 1995 (WG'94, LNCS 903): snippet; listed as "cointerval graphs [16]" in BKKM TR p. 2 (read secondary) | no |
| **Cocomparability** | **pw = tw**, but **NP-complete** | approximation: pw = O(tw²) after an O(n³) colouring | pw = tw: Möhring 1996 via Bodlaender 1998 Thm 99 p. 41, and BKKM TR Thm 2.2 p. 5 (read secondary). NP: tw NP-complete on cocomparability, Bodlaender 1997 p. 2 (read). Approximation: Kloks & Bodlaender TR abstract (read). Habib & Möhring 1994 (Order 11): not held | `1997-Bodlaender-Treewidth-Algorithmic-...` |
| **Cobipartite** | NP-complete | — | "treewidth (resp. pathwidth) … NP-complete on cobipartite graphs [Arnborg, Corneil & Proskurowski 1987]": BKKM TR p. 2 (read secondary) | no |
| **AT-free** | **pw = tw** (every minimal triangulation is interval); NP-hard (contains cobipartite) | O(n⁵R + n³R³), with R the number of minimal separators | Möhring 1996 (DAM 64): Bodlaender 1998 Thm 99 p. 41 (read secondary); Kloks, Kratsch & Spinrad 1997: BKKM TR p. 3 (read secondary) | no |
| **Circular-arc** | **polynomial; pw ≠ tw in general**. pw ≤ 2ω − 1; proper circular-arc pw ≤ 2ω − 2 | **O(n²)** | Suchan & Todinca 2007, abstract and pp. 1–2 (read); Bodlaender 1998 Cor 31 p. 13 and Cor 55 p. 26 (read) | `2007-Suchan-Todinca-Pathwidth-Circular-Arc-Graphs-WG.pdf` |
| **Split** | polynomial (tw = ω − 1, pw not) | polynomial (Gustedt) | Möhring 1990 p. 46: "Similar arguments yield also a polynomial algorithm for split graphs" (read). Gustedt 1993: snippet says polynomial for *k*-starlike graphs, a generalisation of split graphs | Möhring held; Gustedt **not** |
| **Starlike chordal** (a central clique; every other maximal clique meets only it) | NP-hard. Polynomial under the overlap condition (4.6) | O(\|V\|³) under (4.6) | Möhring 1990 Thm 4.4 pp. 40–41 (Gustedt's reduction, read); Thm 4.9 p. 46 (read) | `mohring_1990_...` |
| **Chordal** | **NP-complete**; no good approximation known (1992) | — | Gustedt 1993 via Möhring 1990 Thm 4.4 p. 40 (read) and Díaz–Petit–Serna 2002 Table III p. 323 (read); Kloks & Bodlaender TR p. 2 (read) | Díaz, Möhring held; Gustedt **not** |
| **Chordal dominoes** (every vertex in ≤ 2 maximal cliques) | NP-complete | — | Kloks, Kratsch & Müller, "Dominoes", WG'94: snippet only | no |
| **Cotriangulated** (complement chordal) | approximation pw ≤ 3tw + 4 | O(n²) | Kloks & Bodlaender TR abstract p. 1 (read) | `1992-Kloks-Bodlaender-...` |
| **Bipartite** | NP-complete | — | Díaz–Petit–Serna Table III p. 323, citing Goldberg, Golumbic, Kaplan & Shamir 1995 (read secondary); Kloks & Bodlaender TR p. 2 (read); BKKM TR p. 2, citing Kloks 1994 (read) | Díaz held |
| **Convex bipartite** | approximation pw ≤ 2tw + 1 | O(nk) | Kloks & Bodlaender TR abstract (read) | yes |
| **Biconvex bipartite** | linear (tw and pw) | linear | Peng & Yang 2007 (TAMC): snippet | no |
| **Chordal bipartite** | tw polynomial (Kloks & Kratsch); **pw reported NP-complete, source unidentified** | — | tw: Kloks & Kratsch TR RUU-CS-92-28 abstract (read). pw: snippet only, **verify** | `1992-Kloks-Kratsch-...` |
| **Distance-hereditary** | **NP-hard** (open in 1990); tw linear | — | Kloks, Bodlaender, Müller & Kratsch, ESA 1993, cited in Adler, Kanté & Kwon arXiv:1403.1081 p. 2 (read secondary); open in Möhring 1990 p. 46 and Bodlaender & Möhring TR p. 10 (read); linear rank-width O(n² log² n) on the same class, Thm 6.1 p. 2 (read) | `2014-Adler-Kante-Kwon-...` |
| **Trees / forests** | polynomial | O(n) value (Ellis, Sudborough & Turner); O(n) layout (Skodinis 2000); peeling algorithm O(\|V\|) (Möhring Thm 4.7 p. 45) | Díaz–Petit–Serna Table IV pp. 327–329 (read); Möhring 1990 (read) | Ellis et al. held |
| **Weighted trees** | NP-hard | — | Mihai & Todinca 2009: title only | no |
| **Unicyclic** | polynomial | O(n log n) (Ellis & Markov 2004) | Suchan & Todinca p. 2 (read secondary) | no |
| **Bounded treewidth** (outerplanar, Halin, series-parallel) | polynomial | Bodlaender & Kloks 1996: linear for fixed k, huge constants; no combinatorial algorithm known for outerplanar or Halin | Suchan & Todinca p. 2 (read); Coudert, Huc & Sereni pp. 2–3 (read) | yes |
| **Planar, max degree 3** | NP-complete | — | Monien & Sudborough 1988, Díaz–Petit–Serna Table III p. 323 (read secondary) | no |
| **Grid graphs, unit disk graphs** | NP-complete | — | Díaz et al. 2001a, Table III p. 323 (read secondary) | no |
| **n-dimensional grids** | polynomial | O(n²) (Bollobás & Leader) | Díaz–Petit–Serna Table IV (read secondary) | no |
| **Cubic** | bound pw ≤ n/6 + εn | — | Fomin & Høie 2006, abstract p. 191 (read) | `2006-Fomin-Hoie-...` |
| **Circle graphs** | tw polynomial (Kloks 1993); **pw: no result found** | — | Bodlaender 1997 p. 2 (tw) (read) | — |

## 2. The landscape in words

Read it as a containment diagram drawn left to right, from easy to hard.

**Polynomial, with pw = tw.** These classes all sit inside **AT-free**, and they
inherit pw = tw from Möhring's theorem:
interval ⊂ cointerval-type classes; cographs ⊃ threshold; permutation ⊂
trapezoid ⊂ d-trapezoid ⊂ cocomparability of bounded dimension ⊂
**cocomparability** ⊂ **AT-free**. pw = tw holds on the whole of AT-free. It
becomes NP-hard at **cocomparability**, already on **cobipartite** graphs,
because there treewidth itself is NP-hard. So pw = tw does not make a class easy.
It moves the difficulty from pathwidth to treewidth, where solvers are much
stronger.

**Polynomial, with pw ≠ tw.** Trees (tw = 1, pw unbounded), unicyclic graphs,
bounded treewidth (through Bodlaender–Kloks, impractical), **circular-arc**
(O(n²); the one non-trivial class whose pathwidth algorithm owes nothing to
treewidth) and **split** graphs. Among these classes the pw > tw phenomenon of
`reports/ml_nature.md` §6 is possible.

**NP-hard.** Chordal (even starlike, even chordal dominoes), bipartite,
cobipartite, cocomparability, distance-hereditary, planar of maximum degree 3,
grids and unit disk graphs, weighted trees. The boundary inside chordal graphs is
the overlap structure of the maximal cliques (Möhring 1990 p. 41): split and
*k*-starlike are easy, starlike is hard. Inside bipartite graphs, biconvex is
easy and general bipartite is hard. Chordal bipartite is reported hard but this is
unverified. The tree-like rank-width-1 class, distance-hereditary, is hard even
though linear rank-width is polynomial on it.

**Open or unfound.** Circle graphs, chordal bipartite (verify the claim), a
combinatorial algorithm for outerplanar or Halin graphs, and whether a class
between split and *k*-starlike has a sharper boundary.

## 3. Classes where pw = tw, and our pw > tw finding

`reports/ml_nature.md` §6/§21/§27 found pw > tw on many MOSP instances (exact
pw > tw on 375 corpus instances in `learning/data/ensemble/extremal_corpus_tw.csv`).
Möhring's theorem gives a structural reason. **pw > tw requires an asteroidal
triple**: no AT-free graph can have pw > tw. Checked on the corpus (§4): all 375
instances with exact pw > tw are non-AT-free, and on all 2,830 AT-free instances
with exact treewidth, `tw + 1 = optimum`, with zero exceptions. The bound-defeating
family of CLAUDE.md, "trees of cliques with branching", is exactly where
asteroidal triples live: three branches at a hub give an asteroidal triple. This
connects the branch lemma, which is Fellows & Langston 1987 Lemma 4.3 and Möhring
1990 Lemma 3.12, p. 36, to Möhring 1996.

## 4. What our corpus is made of (measured 2026-10-09)

`paper2/class_scan.py` (one niced process, about 1 minute; output
`paper2/class_scan.json`) tests every certified corpus MOSP graph:

| | instances (6,376) | non-complete instances (4,707) | distinct graphs (3,667, by `graph_cert`) |
|---|---|---|---|
| complete | 1,669 | — | 5 |
| interval | 2,524 | 855 | 222 |
| cograph | 2,573 | 904 | 129 |
| chordal | 2,617 | 948 | 309 |
| split | 2,401 | 732 | 122 |
| AT-free | 3,707 | 2,038 | 1,055 |
| co-disconnected (a join) | 4,250 | 2,581 | 1,593 |
| bipartite | 30 | — | 20 |

**Checks against the certified optima, all passed.** The Bodlaender–Möhring
recursion, generalised to k co-components as `pw = min_i (pw(G_i) + n − |V_i|)`
(derived by induction from Lemma 3.4(iv)), reproduces the optimum on **all 2,573
cograph instances**. ω equals the optimum on **all 2,524 interval instances**.
On AT-free instances, `tw + 1` equals the optimum on all 2,830 with exact
treewidth. These are independent confirmations of three theorems on our data, and
of our certified values on those instances.

**Per collection.** Harvey and Simonis account for almost all the easy-class
instances. Chu & Stuckey has 0 chordal, 0 cograph and 8 AT-free instances out of
200 (the dense `Random-30-30-10`, `Random-50-100-10`), with 33 joins.
Faggioli–Bentivoglio has 33 interval and 51 AT-free out of 300. **SCOOP
(industrial)** has 3 interval out of 24 (`B_39Q18_82`, `B_CARLET_137`,
`B_CUC28A_138`: optimum = ω, solved by a clique computation) and 7 chordal. The
real instances are sparse and mostly outside the easy classes, which is an honest
negative for the "industrial instances are easy" story.

## 5. Applied-math opportunities

1. **Join (co-component) decomposition as a MOSP preprocessing rule.** If the
   complement of the MOSP graph is disconnected, with co-components G₁ … G_k (every
   customer of one group shares a product with every customer of every other), then
   `MOSP(G) = min_i (MOSP(G_i) + n − |V_i|)`. This is Bodlaender–Möhring Lemma 3.4(iv)
   and Möhring's (4.5), translated through the Lean equality. It is **not** among
   the six operations of Yanasse & Senne 2010 (read: they decompose by components
   only, never by complement components). It applies to **4,250 of 6,376 corpus
   instances**, 33 of them Chu & Stuckey. Recursing on components and co-components
   leaves a largest prime piece smaller than n on 1,609 distinct non-cograph graphs,
   and at most n/2 on 12.6% of non-cograph instances (`Random-50-100-10-2`: 50
   customers down to a 6-vertex prime piece). The rule is exact, cheap (O(n + m)
   modular decomposition) and a natural Lean target: its proof is the complete-bipartite
   containment lemma (TR Lemma 3.2 p. 5), a sibling of the Helly lemma
   `PathDecomposition.exists_bag_of_isClique` already proved. This is the
   strongest practical item. It may be **unstated in the MOSP literature**, which
   needs checking against Becceneri et al. 2004 and Yanasse–Limeira 2004 (held:
   the latter handles trees and stars only).

2. **AT-free MOSP graphs: solve by treewidth.** On AT-free MOSP graphs pw = tw
   (Möhring 1996). So the optimum is exact treewidth + 1, and an optimal sequence
   comes from any *minimal* triangulation of minimum width, which is interval, so
   its clique path orders the patterns (the construction of `MOSPGraph.lean`). This
   brings PACE-grade treewidth solvers (Tamaki, held) to bear on 3,707 corpus
   instances. AT-free recognition and asteroidal-triple witnesses also give a
   **certificate-of-gap tool**: an instance whose `lb_best` misses the optimum
   *and* is AT-free can only be closed by a better treewidth bound, never by a
   pathwidth-specific argument. A conjecture to test with our solver and the
   census (`learning/pwtw_exhaust.py`): *pw − tw ≤ f(number of asteroidal triples,
   or the asteroidal number)*. The census already has every graph to 11 vertices.

3. **Cheap exact layers before search.** (a) Interval MOSP graph ⇒ optimum = ω,
   linear time (Lekkerkerker–Boland: chordal and AT-free; or Booth–Lueker). (b)
   Cograph ⇒ the linear-time formula. (c) Circular-arc ⇒ Suchan–Todinca O(n²).
   (d) Permutation or trapezoid ⇒ O(n²). (a) and (b) cover 2,573–2,617 corpus
   instances and 3 SCOOP ones. These also give the paper a crisp practical
   statement: *a cutting instance whose MOSP graph is interval (for example, every
   customer's products are consecutive in some product order) or a cograph is
   solved in linear time*, with the matrix conditions to state.

4. **NP-hardness transfers, stated in MOSP vocabulary.** Möhring's Thm 4.4
   construction *is* a MOSP instance with one pattern per maximal clique (pp.
   40–41). Chordal dominoes give **MOSP NP-hard even when every customer orders at
   most two products and the MOSP graph is chordal** (if the Kloks–Kratsch–Müller
   statement holds; to verify), the dual of the two-customers-per-pattern
   hardness of Yanasse 1997a. Bipartite hardness gives NP-hardness for
   triangle-free instances with two customers per pattern.

5. **Open questions our solver can probe.** Pathwidth of circle graphs; the claimed
   hardness on chordal bipartite graphs; the split/starlike boundary (Gustedt's
   *k*-starlike exponent); random-graph membership: at what density does a random
   MOSP graph become AT-free or co-disconnected? The phase-transition data in
   `learning/hardness_map.py` predicts the joins sit on the dense side of the
   ridge. That would explain why dense instances are easy in nodes, as §11 found.

## 6. Papers to obtain

| Paper | DOI / locator | Why | Obstacle |
|---|---|---|---|
| Gustedt (1993) On the pathwidth of chordal graphs. DAM 45:233–248 | 10.1016/0166-218X(93)90012-D | chordal NP-hardness, split and *k*-starlike algorithms | Elsevier open archive (bronze OA), bot check refused |
| Habib & Möhring (1994) Treewidth of cocomparability graphs and a new order-theoretic parameter. Order 11:47–60 | 10.1007/BF01462229 | pw = tw on cocomparability | paywalled |
| Möhring (1996) Triangulating graphs without asteroidal triples. DAM 64:281–287 | DOI not resolved (rate-limited) | **AT-free pw = tw**, the theorem behind §3 | Elsevier |
| Kloks, Kratsch & Spinrad (1997) On treewidth and minimum fill-in of AT-free graphs. TCS 175 | 10.1016/S0304-3975(96)00206-X | O(n⁵R + n³R³) algorithm | OA at research.utwente.nl, bot check refused |
| Kloks, Kratsch & Spinrad, Treewidth and pathwidth of cocomparability graphs of bounded dimension | 10.1007/BFb0045387 | bounded-dimension algorithm | TU/e repository, bot check |
| Garbe (1995) Tree-width and path-width of comparability graphs of interval orders. WG'94, LNCS 903:26–37 | 10.1007/3-540-59071-4_35 | linear-time co-interval | paywalled |
| Kloks, Kratsch & Müller (1995) Dominoes. WG'94, LNCS 903 | 10.1007/3-540-59071-4_41 | chordal-domino NP-completeness (MOSP with ≤ 2 products per customer) | paywalled |
| Kloks, Bodlaender, Müller & Kratsch (1993) Computing treewidth and minimum fill-in: all you need are the minimal separators. ESA, LNCS 726:260–271 | 10.1007/3-540-57273-2_61 | distance-hereditary pathwidth NP-hard | paywalled |
| Suchan & Todinca (2007) Pathwidth of circular-arc graphs. WG, LNCS 4769:258–269 | 10.1007/978-3-540-74839-7_25 | published version (author copy held) | — |
| Peng & Yang (2007) On the treewidth and pathwidth of biconvex bipartite graphs. TAMC, LNCS 4484:244–255 | 10.1007/978-3-540-72504-6_22 | biconvex linear; chordal bipartite claim | paywalled |
| Mihai & Todinca (2009) Pathwidth is NP-hard for weighted trees. FAW, LNCS 5598:181–195 | 10.1007/978-3-642-02270-8_20 | weighted-tree hardness | paywalled (HAL record, no file) |
| Krishna et al. (2010) Pathwidth and searching in parameterized threshold graphs. LNCS | 10.1007/978-3-642-11440-3_27 | threshold generalisation | paywalled |
| Bodlaender & Möhring (1993) SIAM JDM 6:181–188 | 10.1137/0406014 | published version (TR held) | paywalled |
| Bodlaender, Kloks & Kratsch (1995) SIAM JDM 8:606–616 | 10.1137/S089548019223992X | published version (TR held) | paywalled |
| Arnborg, Corneil & Proskurowski (1987) Complexity of finding embeddings in a k-tree. SIAM JADM 8:277–284 | 10.1137/0608024 | cobipartite NP-hardness | paywalled |
| Goldberg, Golumbic, Kaplan & Shamir (1995) Four strikes against physical mapping of DNA. J. Comput. Biol. 2:139–152 | 10.1089/cmb.1995.2.139 | bipartite NP-hardness; interval sandwich | paywalled |
| Kaplan & Shamir (1996) Pathwidth, bandwidth and completion problems to proper interval graphs with small cliques. SIAM J. Comput. 25:540–561 | DOI not resolved | proper interval / bandwidth = proper pathwidth | paywalled |
| Monien & Sudborough (1988) Min cut is NP-complete for edge weighted trees. TCS 58:209–229 | DOI not resolved | planar max-degree-3 hardness | Elsevier |
| Broersma, Dahlhaus & Kloks (2000) DAM | 10.1016/S0166-218X(99)00146-8 | distance-hereditary treewidth linear | OA, bot check |
| Meister (2010) TCS 411 | 10.1016/j.tcs.2010.06.017 | linear permutation treewidth = pathwidth | OA, bot check |
| Fomin, Heggernes & Mihai (2010) Networks 56:207–214 | 10.1002/net.20373 | mixed search on interval and split graphs | paywalled |
| Kloks (1994) Treewidth: Computations and Approximations, LNCS 842 | — | bipartite NP-hardness, general reference | book |

## 7. New PDFs in `literature/` (all verified: opened, page count checked, text or images read)

- `1990-Bodlaender-Mohring-Pathwidth-Treewidth-Cographs-TR-RUU-CS-90-7.pdf` (UU repository; scanned, read as images)
- `1992-Bodlaender-Kloks-Kratsch-Treewidth-Pathwidth-Permutation-Graphs-TR-UU.pdf` (UU; scanned)
- `1992-Kloks-Bodlaender-Approximating-Treewidth-Pathwidth-Perfect-Graphs-TR-RUU-CS-92-29.pdf` (UU; scanned)
- `1992-Kloks-Kratsch-Treewidth-Chordal-Bipartite-Graphs-TR-RUU-CS-92-28.pdf` (UU; scanned)
- `1995-Bodlaender-Kloks-Kratsch-Muller-Treewidth-Fill-in-d-Trapezoid-Graphs-TR-UU-CS-95-34.pdf` (TU/e)
- `1997-Bodlaender-Treewidth-Algorithmic-Techniques-Results-MFCS.pdf` (UU)
- `2006-Fomin-Hoie-Pathwidth-Cubic-Graphs-Exact-Algorithms-IPL.pdf` (author page)
- `2007-Suchan-Todinca-Pathwidth-Circular-Arc-Graphs-WG.pdf` (author page, Orléans)
- `2014-Adler-Kante-Kwon-Linear-Rank-Width-Distance-Hereditary-Graphs-I-arXiv.pdf` (arXiv:1403.1081)

The UU DSpace handles are fetched through its REST API
(`/server/api/pid/find?id=hdl:1874/<n>` → bundles → bitstreams). The HTML front end
is JavaScript-only, so this is the way into these Utrecht technical reports.
