# IJOC literature for paper 2 ("The pathwidth complex")

Compiled 2026-10-04 for submission to the *INFORMS Journal on Computing* (IJOC).
Every entry below comes from a Crossref or OpenAlex record, or from a PDF that
was opened and read. Nothing is cited from memory.

## Method

**Source.** OpenAlex source `S165318533` ("INFORMS journal on computing").
It carries all four ISSNs: 0899-1499 (*ORSA Journal on Computing*), 1091-9856,
1526-5528 and 2326-3245. OpenAlex reports 2,725 works.

**1. OpenAlex keyword searches** (2026-10-04), `filter=primary_location.source.id:S165318533&search=<q>&per-page=50`, with
q in: open stacks, pattern sequencing, cutting pattern sequencing, stock cutting
sequencing, cutting stock, pathwidth, path width, treewidth, tree decomposition,
vertex separation, graph layout, linear arrangement, linear ordering, cutwidth,
bandwidth minimization, matrix bandwidth, profile minimization, sumcut, graph
searching, pursuit evasion, search number, gate matrix, VLSI layout, PLA folding,
interval graph, interval thickness, pebbling, register allocation, consecutive
ones, node search, dominance, dominance rules branch and bound, nogood, nogood
learning, certificate, certified optimality, verified, proof, benchmark library,
test instances, instance library, SAT encoding, satisfiability, constraint
programming sequencing, constraint programming scheduling, dynamic programming
sequencing, branch and bound sequencing, talent scheduling, scene scheduling,
rehearsal scheduling, minimization of tool switches, tool switching, column
permutation, sequencing metaheuristic, variable neighborhood search layout,
graph partitioning separator, vertex separator, minimum fill-in, elimination
ordering, chordal, exact algorithm graph, isomorphism symmetry, symmetry
breaking, reproducibility, computational experiments testing, open stack,
flexible machines, job sequencing tools, permutation problems local search,
layout problems, circuit layout, one-dimensional, graph coloring exact, decision
diagrams sequencing, sequence dependent, mixed integer programming formulations
ordering, bin packing exact, cutting pattern, trim loss setups. This gave 707
distinct works, most of them noise from fuzzy matching. Then
`title_and_abstract.search` for: open stacks, pattern sequencing, pathwidth,
path-width, treewidth, tree decomposition, branch decomposition, vertex
separation, cutwidth, bandwidth graph, matrix bandwidth, linear arrangement,
profile minimization. After these, OpenAlex's free daily budget ran out
(HTTP 429, `retryAfter` about 8.8 h), so step 3 replaced the remaining searches.

**2. Citing works** (OpenAlex `filter=cites:<W>`, keeping those in IJOC), for:
Linhares & Yanasse 2002 (W2122148260), Chu & Stuckey 2009 (W1493287964),
Garcia de la Banda & Stuckey 2007 (W2090776450), Yanasse 1997b (W1982726693),
Kinnersley 1992 (W2052867211), Yanasse & Senne 2010 (W2021487162), Fellows &
Langston 1987 (W2000611521), the Linhares thesis (W1584759191); then, with the
source filter applied server side, Becceneri et al. 2004, Faggioli & Bentivoglio
1998, Díaz–Petit–Serna 2002, Ellis–Sudborough–Turner 1994, Bodlaender–Kloks 1996,
Fellows & Langston 1989, LaPaugh 1993, Bienstock & Seymour 1991, Möhring 1990,
Duarte et al. 2012, Bodlaender et al. 2012, Coudert–Mazauric–Nisse 2016 and
Frinhani et al. 2018. IJOC citers found: GdlB&S 2007 (cites LY2002, Yanasse 1997b,
Becceneri 2004, Faggioli 1998); talent scheduling 2011 (cites CS2009, Yanasse
1997b, Becceneri, Faggioli); Caprara et al. 2011 and van Dam & Sotirov 2015 (cite
Díaz–Petit–Serna); Cook & Seymour 2003 and Hicks 2005 I (cite Bodlaender–Kloks);
Doulabi et al. 2016 (cites CS2009). **No IJOC paper cites Kinnersley 1992,
Fellows & Langston, Ellis et al., LaPaugh, Bienstock & Seymour or Möhring.**

**3. The whole IJOC catalogue from Crossref** (2026-10-04),
`https://api.crossref.org/journals/{1091-9856,1526-5528,0899-1499}/works?rows=1000&cursor=...`.
This gave 2,657 distinct DOIs, 2,435 of them with abstracts. Regular expressions
were run over title and abstract for these topics: open stacks / pattern
sequencing; path-, tree-, branch- and clique-width and decompositions; vertex
separation, cutwidth, bandwidth, linear arrangement, profile, linear ordering,
fill-in; gate matrix, VLSI, PLA, logic arrays, folding; graph search, pursuit,
pebbling, register allocation, interval graphs, consecutive ones; dominance,
nogoods, memoisation, conflict analysis; certificates, verification, proofs,
exact/rational/safe computation, round-off, reproducibility; benchmark
libraries; SAT and CP; talent scheduling, tool switching, column permutation;
dynamic programming; decision diagrams; zero forcing and minimum rank. About 55
shortlisted works had their abstracts read in full. Because this step scans the
whole catalogue rather than ranking search results, it is the completeness
check: **no IJOC title or abstract contains "pathwidth", "path-width" or
"vertex separation"**, and only two contain "open stacks".

**4. Held papers' reference lists.** `pdftotext` over all 76 PDFs in
`literature/`, grepping for "INFORMS J", "Journal on Computing" and "ORSA J".
Most hits were false positives (*SIAM Journal on Computing*). The IJOC
references found were: Garcia de la Banda & Stuckey 2007 (cited by nine held
papers); Belov & Scheithauer 2007 (Martin, Yanasse & Pinto 2022); Caprara,
Letchford & Salazar-González 2011 (Petit 2011); Hicks 2005 (Kaneda, Kobayashi
& Tamaki 2026); and Jain & Grossmann 2001 and Williams & Yan 2001 (Chu 2011
thesis; both rejected, being general MILP/CP modelling).

**Open access** was checked with Unpaywall
(`api.unpaywall.org/v2/<doi>?email=research@example.org`), the arXiv API and a
web search for author copies. Pages that served a bot challenge (HAL, Edinburgh
Research Explorer, people.eng.unimelb.edu.au) were **not** worked around.
pubsonline.informs.org was not used.

## Kept papers (27)

Status: **held** = in `literature/` before today; **downloaded** = fetched
today, legal open copy; **missing** = no open copy obtainable by script. "Cited"
means the key is in `paper1/latex/refs.bib`. None of the 27 is cited in the
draft.

| # | Year | Authors | Title | Vol(No):pp | DOI | Why relevant | Status | File |
|---|---|---|---|---|---|---|---|---|
| 1 | 2007 | Garcia de la Banda, Stuckey | Dynamic Programming to Minimize the Maximum Number of Open Stacks | 19(4):607–617 | 10.1287/ijoc.1060.0205 | The IJOC MOSP paper. Winner of the 2005 Modelling Challenge. Defines the customer (= MOSP) graph. Lemma 1 is the *product-level* "definite choice" with a proof. Ties its exactly-N search to Linhares & Yanasse's FPT remark. | held; **not cited** | `2007-Garcia-de-la-Banda-Stuckey-Dynamic-Programming-Minimize-Maximum-Open-Stacks-IJOC.pdf` |
| 2 | 2007 | Belov, Scheithauer | Setup and Open-Stacks Minimization in One-Dimensional Stock Cutting | 19(1):27–35 | 10.1287/ijoc.1050.0132 | MOSP inside cutting stock, the setting MOSP comes from. Cited by Martin, Yanasse & Pinto 2022. | missing | — |
| 3 | 2011 | Garcia de la Banda, Stuckey, Chu | Solving Talent Scheduling with Dynamic Programming | 23(1):120–137 | 10.1287/ijoc.1090.0378 | Open-stacks-like sequencing problem with the same DP and bound machinery. Cites Chu & Stuckey 2009. | missing (author copy behind a bot check at people.eng.unimelb.edu.au/pstuckey/papers/rehearsal.pdf) | — |
| 4 | 2005 | Caprara, Salazar-González | Laying Out Sparse Graphs with Provably Minimum Bandwidth | 17(3):356–373 | 10.1287/ijoc.1040.0083 | Exact bandwidth, one end of the degeneracy ≤ pw ≤ bw sandwich. Proven optima on benchmark graphs. | missing | — |
| 5 | 2011 | Caprara, Letchford, Salazar-González | Decorous Lower Bounds for Minimum Linear Arrangement | 23(1):26–40 | 10.1287/ijoc.1100.0390 | Linear arrangement, a layout sibling. Its abstract says even the order of magnitude of most benchmark optima is unknown, which frames our certified dataset. | **downloaded** (published version, Lancaster EPrints) | `2011-Caprara-Letchford-Salazar-Gonzalez-Decorous-Lower-Bounds-Minimum-Linear-Arrangement-IJOC.pdf` |
| 6 | 2015 | van Dam, Sotirov | On Bounding the Bandwidth of Graphs with Symmetry | 27(1):75–88 | 10.1287/ijoc.2014.0611 | Bandwidth lower bounds (SDP) and a reverse Cuthill–McKee upper bound, which we also use (`bw_rcm`). | **downloaded** (arXiv 1212.0694v3, preprint) | `2015-van-Dam-Sotirov-Bounding-Bandwidth-Graphs-Symmetry-IJOC-arXiv.pdf` |
| 7 | 2008 | Anjos, Vannelli | Computing Globally Optimal Solutions for Single-Row Layout Problems Using SDP and Cutting Planes | 20(4):611–617 | 10.1287/ijoc.1080.0270 | Exact linear placement, a weighted linear-arrangement relative. Low. | missing | — |
| 8 | 2010 | Buchheim, Wiegele, Zheng | Exact Algorithms for the Quadratic Linear Ordering Problem | 22(1):168–177 | 10.1287/ijoc.1090.0318 | Its abstract says the problem includes linear arrangement via betweenness. Exact layout methods in IJOC. Low. | missing | — |
| 9 | 2005 | Hicks | Planar Branch Decompositions I: The Ratcatcher | 17(4):402–412 | 10.1287/ijoc.1040.0075 | IJOC precedent for exact computation of a width parameter (branchwidth). Cites Bodlaender–Kloks. | missing | — |
| 10 | 2005 | Hicks | Planar Branch Decompositions II: The Cycle Method | 17(4):413–421 | 10.1287/ijoc.1040.0074 | Companion paper: optimal branch decompositions in practice. | missing | — |
| 11 | 2003 | Cook, Seymour | Tour Merging via Branch-Decomposition | 15(3):233–248 | 10.1287/ijoc.15.3.233.16078 | Width decompositions used computationally in IJOC; separator-based heuristic. | missing | — |
| 12 | 2013 | Margulies, Ma, Hicks | The Cunningham-Geelen Method in Practice | 25(4):599–610 | 10.1287/ijoc.1120.0524 | DP over width decompositions measured against a MIP solver. Low. | missing | — |
| 13 | 2010 | Fischetti, Salvagnin | Pruning Moves | 22(1):108–119 | 10.1287/ijoc.1090.0329 | Dominance between B&B nodes turned into "nogoods". The closest IJOC treatment of dominance-based pruning, which is the mechanism behind our false refutations. | missing | — |
| 14 | 2012 | Sewell, Jacobson | A Branch, Bound, and Remember Algorithm for SALBP | 24(3):433–442 | 10.1287/ijoc.1110.0462 | Memory to eliminate redundant subproblems, as in Chu & Stuckey's memo. Closed an open benchmark. | missing | — |
| 15 | 2024 | Coppé, Gillard, Schaus | Decision Diagram-Based Branch-and-Bound with Caching for Dominance and Suboptimality Detection | 36(6):1522–1542 | 10.1287/ijoc.2022.0340 | Dominance plus caching inside exact DP-based B&B. A modern IJOC counterpart to our §4. | **downloaded** (arXiv 2211.13118v5, preprint) | `2024-Coppe-Gillard-Schaus-DD-Branch-and-Bound-Caching-Dominance-IJOC-arXiv.pdf` |
| 16 | 2016 | Bergman, Cire, van Hoeve, Hooker | Discrete Optimization with Decision Diagrams | 28(1):47–66 | 10.1287/ijoc.2015.0648 | DP-model B&B. Diagram width and variable order are layout questions. Medium-low. | missing (the U Toronto repository file is only the 3-page online supplement) | — |
| 17 | 2022 | Castro, Cire, Beck | Decision Diagrams for Discrete Optimization: A Survey | 34(4):2271–2295 | 10.1287/ijoc.2022.1170 | Survey to cite for the DD/DP line. Low. | **downloaded** (arXiv 2201.11536v1, preprint) | `2022-Castro-Cire-Beck-Decision-Diagrams-Discrete-Optimization-Survey-IJOC-arXiv.pdf` |
| 18 | 2025 | Zhang, Beck | Domain-Independent Dynamic Programming and CP Approaches for Assembly Line Balancing with Setups | 37(4):977–997 | 10.1287/ijoc.2024.0603 | DIDP in IJOC. The draft already cites Beck et al. CP 2025 on transition dominance in DIDP. | **downloaded** (arXiv 2403.06780, submitted version) | `2025-Zhang-Beck-DIDP-CP-Assembly-Line-Balancing-Setups-IJOC-arXiv.pdf` |
| 19 | 2012 | Malapert, Cambazard, Guéret, Jussien, Langevin, Rousseau | An Optimal Constraint Programming Approach to the Open-Shop Problem | 24(2):228–244 | 10.1287/ijoc.1100.0446 | CP with nogood recording that closes benchmarks. Low. | missing | — |
| 20 | 2017 | Fukasawa, Poirrier | Numerically Safe Lower Bounds for the CVRP | 29(3):544–557 | 10.1287/ijoc.2017.0747 | Its abstract: unsound pruning "may lead to inappropriate pruning. As a consequence, optimal solutions may be cut off". The closest IJOC analogue to our false refutations (numerical rather than logical cause). | missing | — |
| 21 | 2009 | Cook, Dash, Fukasawa, Goycoolea | Numerically Safe Gomory Mixed-Integer Cuts | 21(4):641–649 | 10.1287/ijoc.1090.0324 | Safe (provably valid) pruning in exact solvers. Low-medium. | missing (Unpaywall lists only catalogue records) | — |
| 22 | 2024 | Halbig, Hümbs, Rösel, Schewe, Weninger | Computing Optimality Certificates for Convex MINLP | 36(6):1579–1610 | 10.1287/ijoc.2022.0099 | Optimality certificates and their size. Our refutation certificate (§32) is in the same spirit. | missing (Edinburgh preprint behind a bot check) | — |
| 23 | 2025 | Eifler, Nicolas-Thouvenin, Gleixner | Combining Precision Boosting with LP Iterative Refinement for Exact Linear Optimization | 37(4):933–944 | 10.1287/ijoc.2023.0409 | IJOC's exact/verified-solving line (exact MIP). Context for "certified optima". Low. | **downloaded** (arXiv 2311.08037, preprint) | `2025-Eifler-Nicolas-Thouvenin-Gleixner-Precision-Boosting-LP-Iterative-Refinement-Exact-LP-IJOC-arXiv.pdf` |
| 24 | 2022 | Hendel, Anderson, Le Bodic, Pfetsch | Estimating the Size of Branch-and-Bound Trees | 34(2):934–952 | 10.1287/ijoc.2021.1103 | Search-tree size prediction. Our censored cost model of node counts is the same question for the customer search. | **downloaded** (ZIB-Report 20-02 via Optimization Online, preprint) | `2022-Hendel-Anderson-Le-Bodic-Pfetsch-Estimating-Size-Branch-and-Bound-Trees-IJOC-ZIB-Report.pdf` |
| 25 | 2022 | Gmys | Exactly Solving Hard Permutation Flowshop Scheduling Problems on Peta-Scale GPU-Accelerated Supercomputers | 34(5):2502–2522 | 10.1287/ijoc.2022.1193 | Closing open benchmark instances of a permutation problem with large parallel B&B. A precedent for our day-long certifications. | missing (HAL copy hal-03689608 behind a bot check) | — |
| 26 | 1993 | Barr, Hickman | Reporting Computational Experiments with Parallel Algorithms | 5(1):2–18 | 10.1287/ijoc.5.1.2 | How to report parallel compute. We quote days on 25 cores plus core-hours. Low. | missing | — |
| 27 | 2026 | Qiu, Cherniavskii, Goldengorin, Pardalos | A Computational Study of the Tool Replacement Problem | 38(1):86–101 | 10.1287/ijoc.2023.0474 | Tool switching, the "flexible machines" sibling in Linhares & Yanasse's title. Low. | missing | — |

Counts: 27 kept; 1 held before today; 7 downloaded today (6 preprint or
submitted versions, 1 published version from an institutional repository); 19
missing.

## Borderline, rejected

- Fast & Hicks 2017, branch decomposition for p-median (10.1287/ijoc.2016.0743): an application of branchwidth, not a computation of it.
- Moonen & Spieksma 2006, loading problem with bounded clique width (10.1287/ijoc.1040.0124): a different width parameter.
- Bodlaender, Hendriks, Grigoriev, Grigorieva 2010, valve location (10.1287/ijoc.1090.0365): treewidth appears only as a hardness class.
- Pferschy & Schauer 2016, QKP approximation on bounded-treewidth graphs (10.1287/ijoc.2015.0678): approximation, off topic.
- Brimkov, Mikesell & Hicks 2021, zero forcing (10.1287/ijoc.2020.1032), and Hicks et al. 2022, minimum rank (10.1287/ijoc.2022.1219): SAT-based exact algorithms for a graph parameter, but the abstracts do not mention pathwidth. Revisit only if a held source ties zero forcing to pathwidth.
- Bergman, Cire, van Hoeve, Hooker 2014, BDD bounds (10.1287/ijoc.2013.0561), and Cappart et al. 2022, RL variable orderings for DDs (10.1287/ijoc.2022.1194): covered by #16 and #17.
- Campos, Laguna & Martí 2005, scatter/tabu search for permutation problems (10.1287/ijoc.1030.0057): the abstract does not name its four problems.
- Laguna & Martí 1999, 2-layer crossing minimisation (10.1287/ijoc.11.1.44), and Chimani & Hungerländer 2013, multilevel vertical orderings (10.1287/ijoc.1120.0525): graph-drawing orderings, not width objectives.
- Happach, Hellerstein & Lidbetter 2022, min sum ordering (10.1287/ijoc.2021.1124): sum objectives; "search" there is not graph searching.
- Witzig & Gleixner 2020 (10.1287/ijoc.2020.0973), Berthold & Witzig 2021 (10.1287/ijoc.2020.1050), Mexi et al. 2025 (10.1287/ijoc.2024.0999): conflict analysis in MIP, analogous to nogoods. Optional if §4 wants a MIP parallel.
- Escobedo & Moreno-Centeno 2015, round-off-free factorisations (10.1287/ijoc.2015.0653): too far from combinatorial certification.
- Heßler & Irnich 2023, partial dominance in labelling (10.1287/ijoc.2022.1255): VRP-specific.
- Hashemi Doulabi, Rousseau & Pesant 2016 (10.1287/ijoc.2015.0686): OpenAlex says it cites Chu & Stuckey 2009; operating-room scheduling with its own dominance rules. Already listed in `literature/MISSING.md`.
- Degraeve & Peeters 2003 (10.1287/ijoc.15.1.58.15156) and Degraeve & Schrage 1999 (10.1287/ijoc.11.4.406): cutting stock, no sequencing.
- Proll & Smith 1998, template design ILP vs CP (10.1287/ijoc.10.3.265): pattern design, not sequencing.
- Jordan & Drexl 1995, CP vs MIP for batch sequencing (10.1287/ijoc.7.2.160): generic.
- McGeoch 1996, experimental method for algorithms (10.1287/ijoc.8.1.1): optional companion to #26.
- Grimes & Hebrard 2015, conflict-directed search for job shop (10.1287/ijoc.2014.0625): generic CP search.
- Pavlik, Sewell & Jacobson 2022, IDDIB bidirectional search (10.1287/ijoc.2021.1116): shortest paths.
- Koehler 2007, no-free-lunch conditions (10.1287/ijoc.1060.0194): reached only through a wrong first DOI guess for GdlB&S 2007; irrelevant.

## For the owner to fetch (paywalled, by importance)

1. Fischetti & Salvagnin 2010, *Pruning Moves*, 10.1287/ijoc.1090.0329. Dominance pruning and nogoods in IJOC; §4's soundness discussion should engage it.
2. Fukasawa & Poirrier 2017, 10.1287/ijoc.2017.0747. IJOC's own statement that unsound pruning cuts off optima.
3. Garcia de la Banda, Stuckey & Chu 2011, talent scheduling, 10.1287/ijoc.1090.0378. An author copy exists at people.eng.unimelb.edu.au/pstuckey/papers/rehearsal.pdf behind a browser check, so a browser fetch should work.
4. Belov & Scheithauer 2007, 10.1287/ijoc.1050.0132.
5. Caprara & Salazar-González 2005, exact bandwidth, 10.1287/ijoc.1040.0083.
6. Halbig et al. 2024, optimality certificates, 10.1287/ijoc.2022.0099. Preprint at research.ed.ac.uk/files/411366786/optimality_certificates_preprint.pdf behind a browser check.
7. Sewell & Jacobson 2012, BB&R, 10.1287/ijoc.1110.0462.
8. Gmys 2022, 10.1287/ijoc.2022.1193. HAL hal-03689608 behind a browser check.
9. Hicks 2005 I and II, 10.1287/ijoc.1040.0075 and 10.1287/ijoc.1040.0074.
10. Bergman, Cire, van Hoeve & Hooker 2016, 10.1287/ijoc.2015.0648.
11. Cook & Seymour 2003, 10.1287/ijoc.15.3.233.16078.
12. Cook, Dash, Fukasawa & Goycoolea 2009, 10.1287/ijoc.1090.0324.
13. Malapert et al. 2012, 10.1287/ijoc.1100.0446.
14. Barr & Hickman 1993, 10.1287/ijoc.5.1.2.
15. Margulies, Ma & Hicks 2013, 10.1287/ijoc.1120.0524.
16. Anjos & Vannelli 2008, 10.1287/ijoc.1080.0270; Buchheim, Wiegele & Zheng 2010, 10.1287/ijoc.1090.0318; Qiu et al. 2026, 10.1287/ijoc.2023.0474.

## What the draft should cite, and where

- **§4, opening and "The definite move is false as published": Garcia de la Banda & Stuckey (2007), #1.** This is the most important gap. The paper is held, it is the IJOC paper on our problem, and the draft does not cite it. Its Lemma 1 (p. 4 of the held PDF) is the *product-level* definite choice: if c(p) ⊆ o(S), an optimal order of S starts with p. It is proved by an exchange argument that reads as correct. That makes it the natural foil for Chu & Stuckey's *customer-level* Theorem 1, which §4 shows false. The same paper defines the customer graph (the MOSP graph). It also attributes the speed of its exactly-N-stacks search to the problem being "fixed parameter tractable (Linhares and Yanasse 2002)", which is the pathwidth connection, stated in IJOC without the word.
- **§4, "The other rules" and "The repaired search is sound":** Fischetti & Salvagnin (2010) on dominance and nogoods; Sewell & Jacobson (2012) on memoised B&B; Coppé, Gillard & Schaus (2024) on caching and dominance in DP-based B&B, beside the existing Beck et al. (2025) and Zhang & Beck (2025). Fukasawa & Poirrier (2017) and Cook et al. (2009), for the point that pruning must be sound or optima are lost.
- **§4, proof object and dataset:** Halbig et al. (2024) for optimality certificates; Eifler, Nicolas-Thouvenin & Gleixner (2025) for IJOC's exact-solving line; Caprara, Letchford & Salazar-González (2011) for benchmarks whose optima are not even known to order of magnitude, against which a certified dataset is the contribution; Hicks (2005), and Cook & Seymour (2003) if space allows, as IJOC's earlier exact width computations.
- **§4, "The revised algorithm in practice":** Hendel et al. (2022) beside the node-count cost model; Gmys (2022) as a precedent for spending large compute to close open instances; Barr & Hickman (1993) for how the core-hours are reported.
- **§3 or §2, the problems:** Belov & Scheithauer (2007) for MOSP in its cutting-stock setting; talent scheduling (2011) as an open-stacks-type relative; Caprara & Salazar-González (2005) and van Dam & Sotirov (2015) where bandwidth appears (the pw ≤ bw end of the sandwich, and `bw_rcm`). Linear-arrangement and DD papers are optional.

## Notes for submission

- IJOC publishes a separate "Code and Data Repository" DOI for each paper (the `.cd` suffix in the Crossref records, e.g. 10.1287/ijoc.2022.0130.cd). The paper's repository, the last step in `plan.md`, should be planned in that form.
