# Pathwidth / Vertex Separation — literature

Collected 2026-09-25, extended 2026-09-27. Files are open-access copies (arXiv, HAL,
institutional repositories, author pages) or publisher PDFs obtained via library access. Pathwidth pw(G) = vertex separation number vs(G)
(Kinnersley 1992) = node search number − 1 = interval thickness − 1.

## 1. Practical exact solvers (start here for an implementation)

| File | Method | Notes |
|---|---|---|
| `2016-Coudert-Mazauric-Nisse-Branch-and-Bound-Pathwidth-Directed-Pathwidth-JEA.pdf` | Branch & bound over vertex orderings (vertex-separation view), with preprocessing and pruning rules; also directed pathwidth | ACM J. Exp. Algorithmics 21 (2016). State of the art in practice: exact for graphs ≲ 60–100 vertices in minutes; good anytime heuristic. Implemented in SageMath (`sage.graphs.graph_decompositions.vertex_separation`). |
| `2014-Coudert-Mazauric-Nisse-Branch-and-Bound-Pathwidth-INRIA-RR-8470.pdf` | Research-report version of the above (SEA 2014) | 300 pages because of full experimental tables. |
| `2012-Bodlaender-Fomin-Koster-Kratsch-Thilikos-Note-Exact-Algorithms-Vertex-Ordering-TOCS.pdf` | O*(2^n) dynamic programming over vertex subsets (Held–Karp style) for pathwidth and other vertex-ordering problems; O*(4^n) poly-space variant | Theory Comput. Syst. 50 (2012). The baseline DP that B&B and PID methods refine. |
| `2019-Bannach-Berndt-Positive-Instance-Driven-DP-Graph-Searching-WADS.pdf` | Positive-instance-driven DP (Tamaki's paradigm) for graph-searching numbers, including node search number = pw+1 | WADS 2019. Competitive exact approach, complementary to B&B. |
| `2022-Bannach-Berndt-Recent-Advances-Positive-Instance-Driven-Graph-Searching-Algorithms.pdf` | Journal version of the WADS paper: unified PID algorithm for treewidth / pathwidth / treedepth via configuration graphs of two-player games, plus a randomized data structure for enumerating subproblems | Algorithms 15(2):42 (2022), open access. Read this instead of the WADS version. |
| `2017-Tamaki-Positive-Instance-Driven-DP-Treewidth-ESA-arXiv.pdf` | The original positive-instance-driven DP (for treewidth, via Bouchitté–Todinca minimal separators / potential maximal cliques). Won PACE 2017. | ESA 2017 / J. Comb. Optim. 2019 / arXiv 1704.05286. Treewidth, not pathwidth, but the PID papers above assume it. |
| `2017-Lodha-Ordyniak-Szeider-SAT-Encodings-Special-Treewidth-Pathwidth-SAT.pdf` | SAT encoding (ordering/partition based) for pathwidth and special treewidth | SAT 2017. Good for small–medium instances; easy to implement with any SAT solver. |
| `2013-Biedl-et-al-ILP-SAT-Pathwidth-Grid-Based-Drawings-GD.pdf` | Generic ILP/SAT grid formulation covering pathwidth (and bandwidth, cutwidth, …) | GD 2013 / arXiv 1308.6778. |
| `2018-Mallach-Linear-Ordering-MIP-Formulations-Vertex-Separation-Pathwidth-JDA.pdf` | Linear-ordering MIP for vertex separation; proves earlier position/set-assignment MIPs have LP bound 0 and gives a formulation with nonzero LP lower bounds | J. Discrete Algorithms 52–53 (2018), journal version of IWOCA 2017. Obtained 2026-09-27 (Elsevier open archive). Main use: lower bounds. |
| `2016-Kitsunai-Kobayashi-Komuro-Tamaki-Tano-Computing-Directed-Pathwidth-1.89n-Algorithmica.pdf` | O(1.89^n) DP over *commitments* for directed pathwidth (hence pathwidth); the search-space reduction is also practical | Algorithmica 75 (2016), journal version of IPEC 2012. Obtained 2026-09-27. Best exponential bound. |
| `2014-Kobayashi-Komuro-Tamaki-Search-Space-Reduction-Commitments-Pathwidth-Experimental-SEA.pdf` | Basic DFS over vertex sequences pruned by Tamaki's commitments, classified by *depth*; depth-1 commitments found extremely effective, depth 2–10 of little further use; TreewidthLIB experiments. The competing B&B to Coudert et al. | SEA 2014, LNCS 8504, 388–399. Obtained 2026-09-28 (full chapter; the whole SEA 2014 volume is in `~/Downloads`). **Read 2026-09-28; the citer-based reconstruction below was right.** Algorithm 1 = memoized backtrack search over k-feasible vertex sets with a *failure table* (= our memo) and an oracle f_d returning a k-committable extension of depth ≤ d; f_1 (exhaustive depth-1 check) is exactly our free moves + definite move (Chu & Stuckey Thm 1). *Corrected 2026-10-03 (loop0008 item 03): a depth-1 commitment is a move with `open(q, S) ≤ 1` (Lean `isCommittable_insert_iff`), so f_1 covers the free moves and only that case of the definite move, which reaches deeper and is false as published; see `paper1/revised_algorithm.md` §4.7.* They have **no** subset rule, old move or better move, so our search prunes at least as much per node. Exact, not heuristic (Bannach & Berndt 2022 misfile it). Java, single thread, 2.14 GHz, 1 GB heap, 30-min cap, no vertex limit: 145 of the 162 TreewidthLIB instances with ≤ 300 vertices solved (Table 5); Table 6 times: queen9_9 94 s, 1f9m 60 s, graph01 1272 s, fpsol2.i.1 (n=496) pw 67 in 323 s, anna TLE at ub 14, tsp225 5.1 s (Coudert et al.: 117 s), celar06 5.1 s. Depth-d oracles for d ≥ 2 cut the state count by only a few % more (Table 2). |

Reading notes on Kobayashi–Komuro–Tamaki (SEA 2014), reconstructed from citers on 2026-09-27 before the PDF was obtained:
  *Reconstructed from citers (2026-09-27):* a basic DFS over vertex sequences σ with d(σ) ≤ k, pruned by Tamaki's commitments (Lemma 1 = Commitment Lemma; definition of k-committable extension as in Kitsunai et al. §3). Their own text: "the use of commitments in their full generality does not result in practically efficient" algorithms, so they classify commitments by *depth* and find depth-1 "extremely effective", depth 2–10 of "limited" extra benefit with "little hope for effective heuristics based on commitments with such depth". Evaluated on TreewidthLIB; computed pathwidth of "many instances for which the exact pathwidth was not previously known". Bannach & Berndt (2022) file it under heuristics. Coudert et al. (JEA 2016 §5): "very similar" B&B, better on some TreewidthLIB instances, a gap they close by randomly relabelling vertices (tie-breaking). Depth-1 commitment ≈ the push/fullset rules of Kitsunai §3 (Prop. 3, Lemma 2), which Suchan–Villanger call the *component push rule*.

Still missing (paywalled; no open-access copy found on OpenAlex as of 2026-09-27). These are the
practical state of the art beyond Coudert–Mazauric–Nisse and should be obtained via library access:
- Tamaki. *A polynomial time algorithm for bounded directed pathwidth.* WG 2011, LNCS 7551. O(m n^{k+1}) XP algorithm; introduces the *commitments* used by the two papers above. https://doi.org/10.1007/978-3-642-25870-1_30
  **Largely superseded by the held Kitsunai et al. (Algorithmica 2016):** its §3 restates the commitment definitions and the Commitment Lemma with proof, and its §7 gives the *corrected* XP algorithm (Search/Exhaust/Dig, O(m n^{2k}/(k−1)!)), because — per Kitsunai et al. and Kitsunai–Kobayashi–Tamaki (arXiv 1507.01934) — "this algorithm as presented in [WG 2011] is flawed". Low priority to obtain; only its §6 (open problem: is directed pathwidth FPT?) is not reproduced.
- Fraire-Huacuja, Castillo-García, López-Locés, Martínez Flores, Pazos, González Barbosa, Carpio. *Integer linear programming formulation and exact algorithm for computing pathwidth.* LNCS 9849 (2016). ILP (IPPW) and B&B (BBPW) benchmarked against SageMath. https://doi.org/10.1007/978-3-319-47054-2_44
- Solano, Pióro. *Lightpath reconfiguration in WDM networks.* J. Opt. Commun. Netw. 2 (2010). The original pathwidth B&B that Coudert et al. extended. Historical.
- Bannach, Berndt, Schuster, Wienöbst. *PACE solver description: PID*.* IPEC 2020. PID applied to treedepth; open access. https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2020.28

Benchmark summary (2026-09-27 reading of the experimental sections): Coudert–Mazauric–Nisse solve every graph
under 60 vertices in ≤10 min, 95.6% of the Rome graphs (all with ≤82 vertices), 139/322 TreewidthLIB graphs
and 27/62 TSP Delaunay triangulations; large instances are solvable only when dense (queen10_10, miles1500,
mulsol.i.5) or of tiny pathwidth (diabetes n=413 pw=6, nos2 n=957 pw=3). Hard open cases: Mycielski M8
(n=191, pw ≤ 72), grids beyond 13×13. Lodha–Ordyniak–Szeider SAT: named graphs up to ~27 vertices, grids up to
9×9, K_123. Biedl et al. SAT: 17% of Rome graphs, nothing with n+m > 70. Bannach–Berndt WADS 2019 reports only
state-space sizes, no pathwidth running times. No dedicated exact pathwidth solver paper found from 2020 on;
pathwidth has never been a PACE track.

## 2. Exponential-time exact algorithms (theory)

| File | Result |
|---|---|
| `2009-Suchan-Villanger-Computing-Pathwidth-Faster-Than-2n-IWPEC.pdf` | First O*(c^n) algorithm with c < 2 (c = 1.9657). |
| `2021-Kobayashi-Nakahata-Note-Exponential-Time-Algorithms-Linearwidth-arXiv.pdf` | O*(2^n) DP for linearwidth (edge-ordering analogue of pathwidth), improving the trivial O*(2^m). 4-page note, arXiv 2010.02388. |
| `2025-Exponential-Time-Approximation-Schemes-Vertex-Ordering-ITCS.pdf` | Exponential-time approximation schemes beating both exact running times and poly-time ratios; covers pathwidth, cutwidth, OLA, FAS via a "balanced-cut" approach. ITCS 2025 / arXiv 2502.10909. |

## 3. Fixed-parameter (bounded-k) algorithms

| File | Result |
|---|---|
| `1996-Bodlaender-Kloks-Efficient-Constructive-Algorithms-Pathwidth-Treewidth-JAlg.pdf` | Linear-time (for fixed k) DP over a tree decomposition deciding pw ≤ k and constructing the decomposition. J. Algorithms 21 (1996). Foundation of all FPT pathwidth algorithms. |
| `2016-Furer-Faster-Computation-of-Path-Width-IWOCA.pdf` | 2^{O(k^2)} n algorithm, improving Bodlaender–Kloks' 2^{O(k^3)} n. IWOCA 2016 / arXiv 1606.06566. |
| `1996-Cattell-Dinneen-Fellows-Simple-Linear-Time-Path-Decompositions-Small-Width-IPL.pdf` | Simple linear-time algorithm giving a path decomposition of width ≤ 2k+1 (or certifying pw > k). IPL 1996. |
| `1994-Kinnersley-Langston-Obstruction-Set-Isolation-Gate-Matrix-Layout-DAM.pdf` | Forbidden-minor (obstruction set) characterization; 110 obstructions for pathwidth 2 (gate matrix layout with 3 tracks). DAM 54 (1994). |

## 4. Approximation algorithms

| File | Result |
|---|---|
| `1991-Bodlaender-Gilbert-Hafsteinsson-Kloks-Approximating-Treewidth-Pathwidth-Min-Elimination-Tree-Height-WG.pdf` | O(log^2 n)-approximation for pathwidth via recursive separators. WG 1991 (Test-of-Time award 2024); journal version J. Algorithms 18 (1995). |
| `2008-Feige-Hajiaghayi-Lee-Improved-Approximation-Min-Weight-Vertex-Separators-SICOMP.pdf` | O(√log n)-approx for min-ratio vertex cuts via SDP; gives O(k√log k)-width tree decompositions and improved pathwidth approximations. STOC 2005 / SICOMP 38 (2008). |
| `2023-Bansal-Katzelnick-On-Approximating-Cutwidth-and-Pathwidth-arXiv.pdf` | log^{1+o(1)} n approximation for pathwidth and cutwidth (new metric decomposition for min-max objectives). FOCS 2024 / arXiv 2311.15639. Current best poly-time ratio for general graphs. |
| `2021-Groenland-Joret-Nadara-Walczak-Approximating-Pathwidth-Small-Treewidth-SODA-TALG.pdf` | O(t√log t)-approximation for graphs of treewidth t (first f(t)-approximation). SODA 2021 / ACM TALG 2023. |
| `2024-Bodlaender-Approximation-Algorithms-Treewidth-Pathwidth-Treedepth-Short-Survey-WG.pdf` | Short survey of old and new approximation algorithms for treewidth, pathwidth, treedepth. WG 2024. |

## 5. Heuristics / metaheuristics (large graphs)

| File | Method |
|---|---|
| `2012-Duarte-et-al-VNS-Vertex-Separation-Problem-COR.pdf` | Variable Neighborhood Search plus a 0-1 model for the vertex separation problem. Computers & OR 39 (2012). Benchmark instances at https://grafo.etsii.urjc.es/optsicom/vsp.html |
| `2017-Construction-Heuristics-Vertex-Separation-Minimization-arXiv.pdf` | Polynomial-time greedy construction heuristics for vertex separation. arXiv 1702.05710. |

## 6. Structure, special classes, surveys

| File | Content |
|---|---|
| `1998-Bodlaender-Partial-k-Arboretum-Bounded-Treewidth-TCS.pdf` | Survey of treewidth/pathwidth theory and relations to other parameters. TCS 209 (1998). |
| `2009-Coudert-Huc-Sereni-Pathwidth-of-Outerplanar-Graphs-JGT.pdf` | Pathwidth of outerplanar graphs vs. their duals (pw(G) ≤ 2 pw(G*) + 1). J. Graph Theory 2007. |
| `2011-Petit-Addenda-Survey-Layout-Problems-BEATCS.pdf` | Addenda (2002–2011) to Díaz–Petit–Serna, "A survey of graph layout problems", ACM Comput. Surv. 34 (2002). The original survey (https://doi.org/10.1145/568522.568523) is held since 2026-09-30 as `diaz_petit_serna_2002_survey_graph_layout_problems.pdf`. |

Classical paywalled references:
- Skodinis. *Construction of linear tree-layouts which are optimal with respect to vertex separation in linear time.* J. Algorithms 47 (2003).
- Robertson, Seymour. *Graph Minors I: Excluding a forest.* JCTB 35 (1983). Introduces pathwidth.
- Bodlaender, Kloks. *Better algorithms for the pathwidth and treewidth of graphs.* ICALP 1991.

## 7. Equivalent problems and classical roots

Pathwidth was rediscovered independently in several communities. Their exact algorithms and benchmarks
are directly transferable: pw(G) = vs(G) = (gate matrix layout tracks) − 1 = (max open stacks) − 1 on the
appropriate graph. Added 2026-09-27.

### Vertex separation / pebbling / nonconstructive FPT

| File | Content |
|---|---|
| `kinnersley_1992_vertex_separation_equals_pathwidth.pdf` | vs(G) = pw(G). IPL 42 (1992). The identity everything in §1 relies on. |
| `ellis_sudborough_turner_1994_vertex_separation_search_number.pdf` | Linear-time vertex separation of trees and O(n log n) optimal tree layouts; vs = node search number − 1. Information and Computation 113(1):50–79 (1994). Scanned copy (30 pp.). Obtained 2026-09-28. Basis for solving tree components exactly (plan phase 5). |
| `lengauer_1981_black_white_pebbles_graph_separation.pdf` | Vertex separator game; relates black-white pebbling of DAGs to separators of undirected graphs. Acta Informatica 16 (1981). Origin of the vertex-separation view. |
| `fellows_langston_1987_nonconstructive_advances_ipl.pdf` | Graph-minor theorem ⇒ polynomial (nonconstructive) algorithms for fixed-k gate matrix layout / pathwidth. IPL 26 (1987). Poor OCR scan. |
| `fellows_langston_1989_search_decision_efficiency_stoc.pdf` | Self-reduction turning nonconstructive decision algorithms into constructive search algorithms (extended abstract). STOC 1989. |

### Gate matrix layout (VLSI)

| File | Content |
|---|---|
| `ohtsuki_mori_kuh_kashiwabara_fujisawa_1979_one_dimensional_logic.pdf` | Gate assignment = interval-graph augmentation with minimum clique; the earliest pathwidth-equivalent formulation. IEEE Trans. Circuits & Systems CAS-26 (1979). |
| `wing_huang_wang_1985_gate_matrix_layout.pdf` | Graph-theoretic model of gate matrix layout, min number of tracks. IEEE TCAD 4(3) (1985). |
| `mohring_1990_gate_matrix_layout_pla_folding.pdf` | Full 35-page survey of the graph problems behind gate matrix layout and PLA folding: interval-graph augmentation with minimum clique size (= pathwidth + 1), node search, vertex separation, the MPQ-tree and interval-order machinery, matching problems with side constraints. Computing Suppl. 7 (Computational Graph Theory, Tinhofer–Mayr–Noltemeier–Sysło eds.), 17–51, Springer 1990. Extracted 2026-09-27 from the full book PDF (pp. 20–54 of the file; book kept in `~/Downloads`). Replaces the 2-page preview. |

### Minimization of open stacks (MOSP, cutting/pattern sequencing)

MOSP on a set of patterns is pathwidth (+1) of the piece graph; MOSP solvers are a mature exact-solver
lineage (2005 Constraint Modelling Challenge; Chu & Stuckey 2009) that the pathwidth literature mostly ignores.

| File | Content |
|---|---|
| `yanasse_1997b_pattern_sequencing_open_stacks_ejor.pdf` | Defines MOSP, complexity, first exact approaches. EJOR 100 (1997). |
| `yanasse_1997a_transformation_pattern_sequencing_wood.pdf` | Reduction: every MOSP instance is equivalent to one where each pattern has ≤ 2 piece types (i.e. a graph). Pesquisa Operacional 17(1) (1997). |
| `becceneri_yanasse_soma_2004_method_mosp_cutting.pdf` | Exact method for MOSP within a cutting process. Computers & OR 31 (2004). |
| `2004-Yanasse-Limeira-Refinements-Enumeration-Scheme-Pattern-Sequencing-ITOR.pdf` | Refinements of the MOSP branch-and-bound: represent MOSP as graph traversal, split the MOSP graph into parts solved independently, solve special-topology parts (trees, stars) exactly in polynomial time and branch only on the 'complex' parts; the local dominance rule the later Brazilian exact methods cite. Limited computational results. ITOR 11(3) (2004). Obtained 2026-09-27. |
| `2010-Yanasse-Senne-Minimization-Open-Stacks-Review-Properties-Preprocessing-EJOR.pdf` | Review of MOSP structural properties and preprocessing (dominance, reductions). EJOR 203 (2010). Preprocessing rules transfer to pathwidth. |
| `2015-Lopes-Valerio-de-Carvalho-Graph-Properties-Minimization-Open-Stacks-New-Integer-Programming-Model-PesqOper.pdf` | MOSP as *interval graph completion* of the MOSP graph (min clique number), with a 20-page tutorial on interval / comparability / chordal graphs and the layout-problem zoo (§3 lists pathwidth, cutwidth, vertex separation); derives an IP model from Olariu's interval-graph characterization; tests on the 2005 challenge instances (optimum found fast, proof of optimality slow on symmetric instances). Pesquisa Operacional 35(2):213–250 (2015), open access on SciELO, doi 10.1590/0101-7438.2015.035.02.0213. Obtained 2026-09-27. |
| `2007-Garcia-de-la-Banda-Stuckey-Dynamic-Programming-Minimize-Maximum-Open-Stacks-IJOC.pdf` | Winner of the 2005 Constraint Modelling Challenge: DP over subsets of closed customers with pruning, symmetry and memoization — the O*(2^n) pathwidth DP made practical (≈100–150 patterns). Chu & Stuckey (CP 2009, held in `~/dev/MOSP/literature/`) extends it. INFORMS J. Computing 19(4) (2007); author preprint, obtained 2026-09-27. |
| `2012-Chu-Garcia-de-la-Banda-Stuckey-Exploiting-Subproblem-Dominance-Constraint-Programming-Constraints.pdf` | General treatment of subproblem dominance in CP search: cache keys characterising subproblems, fail when the current one is dominated by a cached one; the generalisation of the nogood/dominance machinery of Chu & Stuckey CP 2009, with open stacks among the applications. Constraints 17(1):1–38 (2012). Obtained 2026-09-28. |
| `2005-Smith-Gent-Constraint-Modelling-Challenge-2005-Proceedings-and-Report.pdf` | Full proceedings (101 pp.) of the first Constraint Modelling Challenge, IJCAI 2005 workshop: the organisers' report (preprocessing steps, lower bounds, survey of the 13 entries' approaches) followed by all 13 entries. Defines the benchmark instances (incl. SP2–SP4, unsolved at the time) that every later MOSP paper uses. Retrieved 2026-09-27 from the live site https://sites.cs.st-andrews.ac.uk/people/ipg1/challenge/ (identical to the Wayback copy). |
| `2005-Smith-Gent-Constraint-Modelling-Challenge-2005-Report-Slides.pdf` | Organisers' 28-slide summary of the above. |
| `2024-Lima-Santos-Carvalho-Delta-Evaluation-Function-Column-Permutation-Problems-arXiv.pdf` | Treats MOSP and gate matrix layout as one *column permutation problem* on a sparse binary matrix (consecutive-ones view) and gives a Δ-evaluation for local-search moves, compared against full re-evaluation and Frinhani et al.'s indirect evaluation on the standard MOSP/GMLP instance sets. Heuristic side only (no exact method); its §2 is a compact up-to-date MOSP/GMLP literature review naming Gonçalves et al. (2016) BRKGA as MOSP state of the art. arXiv 2409.04926 (2024). Obtained 2026-09-27. |

The full MOSP corpus (Chu & Stuckey CP 2009, Linhares & Yanasse 2002, the Yanasse–Becceneri–Soma bounds
papers, Kirousis–Papadimitriou, Kornai–Tuza, Fomin, …) is in this folder and in `../paper1/literature/`
(see `MISSING.md` and `../paper1/literature/MANIFEST.md`). The challenge instances (`ChallengeInstances2005.tgz`,
`problems_*.txt`) are also on that site.

*Transfer note, 2026-09-30.* This file was `~/dev/pathwidth/literature/README.md`, copied here with the
papers (`../pathwidth_solver/TRANSFER.md`). Eleven of its files (Ohtsuki et al., Lengauer, Wing et al., Fellows & Langston
1987 and 1989, Möhring, Kinnersley, Ellis et al., Yanasse 1997a and 1997b, Becceneri et al.) were byte-identical
to files this folder already held and were not copied; the table rows above now name the held copies.

## 8. Adjacent width solvers (treewidth / branchwidth) worth imitating

Not pathwidth papers, but the practical exact-solver work of the Tamaki group (Meiji / Hokkaido), whose
2024–2027 KAKENHI project is titled *Making treewidth and pathwidth practical*. Watch `au:Tamaki_Hisao`
and `au:Kobayashi_Yasuaki` on arXiv; code at https://github.com/twalgor (repos `tw`, `RTW`, `bw`).
Added 2026-09-27. The 2025 planar potential-maximal-cliques paper (arXiv 2506.12635) was read and left out.

| File | Content | Transfer to pathwidth / MOSP |
|---|---|---|
| `2022-Tamaki-Heuristic-Computation-Exact-Treewidth-arXiv.pdf` | Parallel upper- and lower-bound heuristics that converge to tw(G). Lower bound: start from a greedy contraction, compute its width exactly, then *Lift* to a minor of strictly larger width; each bound is certified by the minor. PACE 2017 bonus set (n ≈ 100–330): 62/91 closed, 20 more within 1, in 30 min. arXiv 2202.07793. | **High.** Pathwidth is minor-monotone, so the certified-minor lower bound scheme applies directly; it is the natural upgrade of the contraction-degeneracy bound (Yanasse–Becceneri–Soma 1999 LB5) used in `~/dev/MOSP`, and attacks the optimality-proof bottleneck Coudert et al. report. The Lift guidance (safe minimal separators crossing a critical fill) and the BT upper bound do not transfer; clique-separator preprocessing is unsafe for pathwidth. |
| `2026-Kaneda-Kobayashi-Tamaki-Fast-Practical-Single-Exponential-Algorithms-Branchwidth-arXiv.pdf` | O*(4^n) hypergraph and O(3.293^n) graph algorithms for branchwidth via a recurrence over *vertex* subsets (same concept as the Kobayashi–Nakahata linearwidth note in §2). Solves 110–112/150 named graphs and 155–165/200 PACE treedepth instances in 10 min vs 49/43 for the SAT encoding. arXiv 2605.17396. Java code: github.com/twalgor/bw. | **Medium.** Shows how a subset recurrence becomes a practical solver; the linearwidth kinship is the closest thing to pathwidth. First output of the treewidth/pathwidth grant. |
| `2023-Tamaki-Contraction-Recursive-Algorithm-Treewidth-arXiv.pdf` | RTW: certifying recursion on edge contractions with safe separators and PMCs. Solves 98/100 PACE 2017 bonus instances (PID: 68). arXiv 2307.01318. Code: github.com/twalgor/RTW. | **Low.** Minimal-separator / PMC machinery has no pathwidth analogue; keep for the recursion-on-contractions design pattern (contraction is also Coudert et al.'s preprocessing tool). |

## Code
- SageMath `vertex_separation` module: implementations of the Coudert–Mazauric–Nisse B&B, the O*(2^n) DP, and MILP formulations.
  https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/graph_decompositions/vertex_separation.html
