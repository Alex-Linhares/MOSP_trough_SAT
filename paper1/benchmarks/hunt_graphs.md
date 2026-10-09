# Benchmark hunt: graph collections (pathwidth, VSP, interval thickness, node search, narrowness)

Compiled 2026-09-30. Every URL below was fetched on that date unless marked
**UNVERIFIED**. Sizes (n = vertices, m = undirected edges after removing loops
and duplicate edges) were computed from the downloaded files, not copied from
the papers; where a paper or page says something different it is noted.
Local paths are relative to `paper1/benchmarks/raw/`.

No collection was found that was built for interval thickness, node search
number or narrowness specifically. Every experimental paper found for those
problems states them as pathwidth / vertex separation and uses the sets below
(VSPLIB's own page states the equivalences VS = PW = IT = SN - 1). The one
graph-searching experimental paper found (Bannach & Berndt, WADS 2019,
doi:10.1007/978-3-030-24766-9_4, arXiv:1905.01134) uses DIMACS coloring and
PACE named graphs, both below.

## Summary

| Collection | Made for | # instances | n range | m range | Optima published? | Downloaded? | Local path |
|---|---|---|---|---|---|---|---|
| VSPLIB 2012 (HB, Grids, Trees) | VSP | 173 (73 + 50 + 50) | 22–2916 | 21–7442 | Grids and trees known by construction; HB best-known (heuristic) only, in `vsp_results.xlsx` | yes (0.8 MB) | `vsplib/` |
| Small (Martí, Campos, Piñana 2008), from CMPLIB 2010 | bandwidth, later cutwidth; used for VSP/pathwidth | 84 | 16–24 | 18–49 | pathwidth for all 84 in Mallach (2018) Tables 4–5 (paper only) | yes (in CMPLIB, 0.5 MB) | `cmplib_small/` |
| CMPLIB 2010 Grids and HB | cutwidth (not an equivalent problem) | 81 + 87 | 18–729 / 30–685 | – / 46–41686 | cutwidth best-knowns only | yes (same archive) | `cmplib_small/` |
| TreewidthLIB (full) | treewidth; used for pathwidth by Kobayashi et al. 2014, Mallach 2018 | unknown now (Kobayashi used 207 with listed bounds) | – | – | treewidth bounds were on the site | **no: graph files no longer served** | – |
| TreewidthLIB DIMACS-coloring subset (`coloring.zip`) | treewidth | 58 graphs + 24 preprocessed (`-pp`) | 5–864 | 5–19095 | no (bounds were on the lost pages) | yes (1.3 MB) | `treewidthlib/` |
| PACE 2016 Track A (testbed) | treewidth | 283 (+8 corner cases) | 9–24,643,531 | 20–32,936,288 | tw for 208 in `instances/instances.csv` | yes (147 MB) | `pace2016_tw/` |
| PACE 2017 Track A exact | treewidth | 200 | 48–3706 | 96–419,877 | yes, optimal `.td` for all 200 (tw 6–908) | yes (200 MB, with heuristic) | `pace2017_tw/` |
| PACE 2017 Track A heuristic | treewidth | 200 | 7–15,531,867 | 9–23,824,624 | no | yes (same archive) | `pace2017_tw/` |
| PACE 2017 bonus | treewidth | 100 | 92–420 | 212–874 | tw for 91 (`instances.csv`, `.td`) | yes (0.3 MB) | `pace2017_tw_bonus/` |
| Named graphs (freetdi) | treewidth (PACE 2016 source) | 150 | 4–3282 | 6–6561 | `.td` per graph (upper bounds; widths in comments) | yes (0.4 MB) | `freetdi_named-graphs/` |
| Control-flow graphs (freetdi) | treewidth (PACE 2016 source) | 1817 `.gr` | 1–1452 | 0–1591 | `.td` per graph | yes (57 MB) | `freetdi_CFGs/` |
| Rome graphs | graph drawing; used for pathwidth by Biedl et al. 2013, Coudert et al. 2014 | 11,534 files (papers: 11,528 / 11,529) | 10–110 | 9–158 | no per-graph values published (only aggregate solve rates) | yes (4.7 MB) | `rome/` |
| Harwell-Boeing (original matrices) | sparse linear algebra; source of VSPLIB/CMPLIB HB | 292 matrices | – | – | no | no (source only; VSPLIB copy used) | – |
| DIMACS coloring | graph colouring; source of TreewidthLIB subset | ~80 | – | – | no | no (TreewidthLIB copy held) | – |
| UAI 2014 graphs, SAT-competition Gaifman graphs, road graphs, transit graphs | treewidth heuristic | – | – | – | no | no (not used for pathwidth in any paper found) | – |

## Archives and checksums

| Archive | Bytes | sha256 | Source revision |
|---|---|---|---|
| `vsplib/VSPLIB_2012.zip` | 830,063 | `cce56b1e5beed89458fd8b7f38416a046626dcd60fd61ab99815f4a6f079bda9` | – |
| `vsplib/vsp_results.xlsx` | 58,114 | `a158434deeabe342dc155570bc77076a9cd071c752499c94161fde4004ac4c33` | – |
| `cmplib_small/CMPLIB_2010.zip` | 539,148 | `47d4f2261e5221f2e907aa2ff967b5cb5bc1c999402b7d8c1aacdf51e7601f92` | – |
| `treewidthlib/coloring.zip` | 1,318,440 | `b77907f1db85ae7a1e0c442651be5f0874bf26d4476e3e68671d882a6bd99a02` | – |
| `pace2016_tw/PACE-treewidth-testbed-master.zip` | 146,581,282 | `95e156bb29089403333b6001af8e57fa84e9df8958d66caa7b4069b98175e594` | holgerdell/PACE-treewidth-testbed @ `99b9eec348d2a6f37cfb2f61f79745bd0a7b0b02` (2018-08-30) |
| `pace2017_tw/Treewidth-PACE-2017-instances-master.zip` | 200,241,494 | `c787f3292325782a459ac7c6cac7ddcf2944c2d5dddbb6f58a8bd138550fb4d4` | PACE-challenge/Treewidth-PACE-2017-instances @ `44e40b0ce87d2360f6114ba2aa503ef8df5e9256` (2020-07-02) |
| `pace2017_tw_bonus/Treewidth-PACE-2017-bonus-instances-master.zip` | 271,866 | `82dc7ec3468e30b5c1717b0bcb2f4371d8a1c6f25505004c9df6795ccf3f3dd0` | PACE-challenge/Treewidth-PACE-2017-bonus-instances @ `a6cd8149a0cdba96f99bc578c99cd0459f6e4ec8` (2020-07-02) |
| `freetdi_named-graphs/named-graphs-master.zip` | 429,090 | `802c392c15aeaee3ba89b7d3c8456457bb3586201a88e9a10e6895bcc52a2e3b` | freetdi/named-graphs @ `2719d7c01a183f780075f285caab4d321e9ea307` (2016-09-27) |
| `freetdi_CFGs/CFGs-master.zip` | 56,814,840 | `858ce8aede1290945dd3fa195077fc7777bec5f15ddc32a7ff7c6ff6730fd928` | freetdi/CFGs @ `2d2ab67e68b22e825345e5e18eb9b82244d6984c` (2018-07-19) |
| `rome/rome-graphml.tgz` | 4,692,225 | `94f0b300a347d4856b37e4650b6cdf6d2999d22159f5cc0d7aa9bedc42b16d89` | – |

GitHub branch zips (codeload) are regenerated on demand and are not
guaranteed byte-stable; the commit hash is the durable identifier. Each archive
is unpacked beside it in `unpacked/` (the `__MACOSX` folders of the two
optsicom zips were deleted). PACE 2017 heuristic instances are `.gr.xz` inside
the archive and are left compressed; unpacked they would be about 1 GB.

---

## VSPLIB 2012

- **Problem**: vertex separation (the page also states VS = PW = IT = SN − 1 = GML + 1).
- **Made by / cite**: A. Duarte, L. F. Escudero, R. Martí, N. Mladenović, J. J. Pantrigo, J. Sánchez-Oro, "Variable neighborhood search for the vertex separation problem", *Computers & Operations Research* 39(12):3247–3255, 2012, doi:10.1016/j.cor.2012.04.017. Later used by Sánchez-Oro, Pantrigo, Duarte, *C&OR* 2014, doi:10.1016/j.cor.2013.11.008; Coudert–Mazauric–Nisse 2014; Mallach 2018; Jain–Saran–Srivastava arXiv:1702.05710; Fraire-Huacuja, Castillo-García et al. (IJCOPI 6(1), 2015).
- **URLs**: page https://grafo.etsii.urjc.es/optsicom/vsp.html (200); archive https://grafo.etsii.urjc.es/optsicom/vsp/vsp-files/VSPLIB_2012.zip (200); results https://grafo.etsii.urjc.es/optsicom/vsp/vsp-files/vsp_results.xlsx (200). The URL cited in the papers, http://www.optsicom.es/vsp/, now redirects to https://www.optsicom.es/, which does not answer. The grafo.etsii.urjc.es server (GRAFO group, Universidad Rey Juan Carlos, where Duarte, Pantrigo and Sánchez-Oro work) is served from GitHub Pages; it is the group's own host, so treated as official.
- **Licence**: none stated.
- **Format**: text, `.mtx.rnd`. Line 1 `Nombre del problema: <name>`, line 2 `n n k`, then one edge `u v` per line, 1-based. HB files list each edge once (k = m); grid and tree files list each edge in both directions (k = 2m).
- **Contents** (verified): `hb/` 73 graphs, n 24–960, m 46–7442; `grids/` 50 square grids λ×λ, 5 ≤ λ ≤ 54, n 25–2916, m 40–5724; `tree/1rot, 2rot, 3rot` 50 trees (19 + 19 + 12), n 22–202, m 21–201. The trees are the minimal trees of Ellis–Sudborough–Turner 1994 with VS 3, 4, 5 (n = 22, 67, 202); the file name `TREE_<n>_<vs>_rot<i>` carries the optimum. The same file names recur across the three `rot` folders with different content.
- **Discrepancy**: the page says HB edges range 34–3721; the files give 46–7442 (unique undirected, loops removed). **Resolved 2026-09-30: the files are right and the page is wrong.** Every file is a
  simple graph: no self-loops, no edge stored in both directions, and each header
  matches its line count. The originals in the NIST Matrix Market store the lower
  triangle with the diagonal, so edges = entries − vertices, and both ends of the
  range match the files: `nos3` has 960 × 960 and 8,402 entries, so 7,442 edges;
  `can___24` has 24 × 24 and 92 entries, so 68 edges. The page's 3,721 and 34 are
  exactly half of those two values. Its minimum is also inconsistent, since
  `bcspwr01`, with 46 edges, would halve to 23. Ding et al. (2017) repeat the
  page's figure.
- **Optima**: grids VS = λ, trees VS = the value in the name — both by construction. HB: only GVNS values and times in `vsp_results.xlsx` (heuristic, not proofs). The xlsx reports 6 for several `TREE_202_5` trees whose optimum is 5, so its tree column is not an optimum column. Coudert et al. (2014) proved exact pathwidth for grids up to λ = 13, trees up to n = 67 and 26 HB graphs (values not tabulated in the SEA paper); Mallach (2018) Tables 2–3 give exact pathwidth for 20 HB, 6 grids and 20 trees with n ≤ 100.
- **Overlap**: the HB graphs are Harwell-Boeing matrices; 36 names also appear in CMPLIB's HB set, randomly relabelled (`.rnd`), and 31 of those 36 agree in n, m and degree sequence; 5 (`bcsstk20`, `bcsstk22`, `dwt__234`, `nos1`, `nos2`) have fewer vertices in CMPLIB than in VSPLIB, so the two sets are not interchangeable.

## Small (Martí, Campos, Piñana 2008) — held as part of CMPLIB 2010

- **Problem**: introduced for matrix bandwidth; reused for cutwidth (CMPLIB) and for VSP/pathwidth (Mallach 2018 "Small", 84 instances; Fraire-Huacuja et al. 2015; Jain et al. 2017).
- **Cite**: R. Martí, V. Campos, E. Piñana, "A branch and bound algorithm for the matrix bandwidth minimization", *EJOR* 186(2):513–528, 2008, doi:10.1016/j.ejor.2007.02.004. CMPLIB: R. Martí, J. J. Pantrigo, A. Duarte, E. G. Pardo, "Branch and bound for the cutwidth minimization problem", *C&OR* 40(1):137–149, 2013, doi:10.1016/j.cor.2012.05.016.
- **URLs**: page https://grafo.etsii.urjc.es/optsicom/cutwidth.html (200) and https://grafo.etsii.urjc.es/cutwidth/ (200); archive https://grafo.etsii.urjc.es/optsicom/cutwidth/cwp-files/CMPLIB_2010.zip (200). No separate download of the bandwidth paper's own copy was found; the CMPLIB copy is from an author group of both papers. **Not verified** that it is byte-identical to the set Mallach used, but the counts (84, n 16–24, m 18–49) match his description.
- **Licence**: none stated.
- **Format**: `small/` and `harwellboeing/` as VSPLIB (name line, `n n m`, edges); `grids/` as a name line followed by a full adjacency matrix (see `Readme.txt`).
- **Contents**: `small/` 84 graphs, n 16–24, m 18–49 (verified); `grids/` 81 rectangular grids w×h, w, h ∈ {3, 6, …, 27}; `harwellboeing/` 87 graphs n 30–685, m 46–41686.
- **Optima**: pathwidth for the 84 Small graphs is tabulated in Mallach (2018) Tables 4–5 (73 solved easily by all formulations; all have values in the tables — check the paper for any marked unsolved). Cutwidth best-knowns in `CMP_BestKnown.xls` on the page (not downloaded; cutwidth is not an equivalent problem). The rectangular grids have known pathwidth min(w, h) but are not a pathwidth benchmark in any paper found.

## TreewidthLIB

- **Problem**: treewidth and related (branchwidth, fill-in); used for pathwidth by Kobayashi, Komuro, Tamaki (SEA 2014, 207 instances, doi:10.1007/978-3-319-07959-2_33) and Mallach (2018, 17 instances: barley, david, huck, mainuk, mildew, myciel2–5, queen5_5 … queen10_10, queen8_12, water).
- **Made by**: J.-W. van den Broek and H. L. Bodlaender, Utrecht University. No paper of record; cite the web site (Kobayashi et al. cite it as "van den Broek, J., Bodlaender, H.L.: TreewidthLIB, http://www.cs.uu.nl/research/projects/treewidthlib/").
- **URLs**: http://www.cs.uu.nl/research/projects/treewidthlib/ → https://ics.uu.nl/research/projects/treewidthlib/ gives **404**. http://people.cs.uu.nl/hansb/treewidthlib/ does not resolve. The successor https://webspace.science.uu.nl/~bodla101/treewidthlib/ (200) is a bare directory listing containing only `coloring.zip` (2011-11-16) and an image. The Wayback Machine holds the site's front pages (2007, 2012, 2015) but, per its CDX index, none of the graph pages or graph files. **The full library is not downloadable from any official source.** Kobayashi et al. (2014) Tables 1, 5, 6 and Mallach (2018) Table 1 are now the only record of pathwidth on it.
- **What was downloaded**: `coloring.zip` from the official Utrecht server: the DIMACS colouring graphs in TreewidthLIB's `.dgf` format — 58 original graphs (anna, david, fpsol2.i.*, games120, homer, huck, inithx.i.*, jean, le450_*, miles*, mulsol.i.*, myciel2–7, queen5_5 … queen16_16, queen8_12, school1, school1_nsh, zeroin.i.*), n 5–864, m 5–19095, and 24 preprocessed versions (`-pp`, n 22–448) which preserve treewidth but not pathwidth and should be excluded, as Kobayashi et al. did.
- **Format**: DIMACS-like: `c` comments, `p edge n k`, `e u v` lines (the `p` count can list both directions).
- **Licence**: none stated.
- **Optima**: the site listed treewidth lower and upper bounds; those pages are lost. For 13 of Mallach's 17 (david, huck, myciel2–5, queens) the graphs are in `coloring.zip`; barley, mainuk, mildew, water (probabilistic networks) are not held. **Missing: ask Bodlaender for the archive.**

## PACE 2016 Track A (treewidth)

- **Made by / cite**: H. Dell, T. Husfeldt, B. M. P. Jansen, P. Kaski, C. Komusiewicz, F. A. Rosamond, "The First Parameterized Algorithms and Computational Experiments Challenge", IPEC 2016, LIPIcs 63:30, doi:10.4230/LIPIcs.IPEC.2016.30. Testbed by H. Dell and F. Salfelder.
- **URLs**: https://pacechallenge.org/2016/treewidth/ (200). Its instance link http://bit.ly/pace16-tw-instances-20160307 → http://people.mmci.uni-saarland.de/~hdell/pace16/pace16-tw-instances-20160307.tar.gz is **dead** (redirects to the MMCI home page). Instances taken instead from the organiser's repository https://github.com/holgerdell/PACE-treewidth-testbed (200), "all benchmark instances" of Track A.
- **Licence**: repository GPL-3.0 (code); instances not separately licensed. The 2016 page itself asks for CC0 for data.
- **Format**: `.gr` (PACE: `p tw n m`, one edge per line, 1-based).
- **Contents**: `instances/pace16/100` 193 (n 9–3282), `1000` 12, `3600` 1, `unsolved` 77 (n 50–24.6 M; the heuristic-scale graphs), plus 8 corner-case graphs. Sources: named graphs, control-flow graphs, DIMACS colouring, road graphs, transit graphs.
- **Optima**: `instances/instances.csv` gives treewidth+1 for 208 instances.
- **Overlap**: 78 of the 150 freetdi named graphs appear by file name in this testbed.

## PACE 2017 Track A (treewidth), exact and heuristic

- **Cite**: H. Dell, C. Komusiewicz, N. Talmon, M. Weller, "The PACE 2017 Parameterized Algorithms and Computational Experiments Challenge: The Second Iteration", IPEC 2017, LIPIcs 89:30, doi:10.4230/LIPIcs.IPEC.2017.30.
- **URLs**: https://pacechallenge.org/2017/treewidth/ (200); https://github.com/PACE-challenge/Treewidth-PACE-2017-instances (200); index of all treewidth sets https://github.com/PACE-challenge/Treewidth (200).
- **Licence**: CC0 1.0 (stated in the repository README and LICENSE).
- **Format**: `.gr.xz`; optimal decompositions `.td.xz` (PACE `.td` format).
- **Contents**: `gr/exact/` ex001–ex200, n 48–3706, m 96–419,877; `gr/heuristic/` he001–he200, n 7–15.5 M, m 9–23.8 M; `gr/*/sources.txt` maps each to its origin (SAT Gaifman graphs, UAI 2014 networks, road graphs, transit graphs, treedecomposition.com).
- **Optima**: `td/exact/` optimal tree decompositions for all 200 exact instances (tw 6–908). None for heuristic.
- **Pathwidth use**: none found in a pathwidth paper; included because the task asks for treewidth sets and they carry certified treewidth, a lower bound on pathwidth.

## PACE 2017 bonus instances

- **URL**: https://github.com/PACE-challenge/Treewidth-PACE-2017-bonus-instances (200). CC0 1.0. Same citation and format as above.
- **Contents**: 100 instances, n 92–420, m 212–874; `instances.csv` gives treewidth for 91 and "?" for 9; `td/` 91 optimal decompositions. Built to need ~1000× the 2017 winners' speed.

## Named graphs and control-flow graphs (freetdi)

- **Made by**: L. Larisch, F. Salfelder (tdlib). Named graphs extracted from SageMath `sage.graphs`; CFGs from SDCC 3.7.0 register allocation over the SDCC standard library, Whetstone, Dhrystone, Coremark, stdcbench, Contiki, FUZIX, NuttX, Atomthreads.
- **URLs**: https://github.com/freetdi/named-graphs (200), https://github.com/freetdi/CFGs (200). Licence CC0 1.0 (LICENCE / LICENSE files).
- **Contents**: named graphs 150 `.gr`/`.dot`/`.td`, n 4–3282, m 6–6561; CFGs 1817 `.gr`, n 1–1452, m 0–1591 (many trivial graphs; also 11,090 `.dot`).
- **Optima**: `.td` files carry a decomposition and its width (upper bound; exactness not stated per file).
- **Note**: control-flow graphs have tiny treewidth by construction (Thorup 1998) and are the natural home of the register-allocation application of vertex separation cited on the VSPLIB page.

## Rome graphs

- **Made by / cite**: G. Di Battista, A. Garg, G. Liotta, R. Tamassia, E. Tassinari, F. Vargiu, "An experimental comparison of four graph drawing algorithms", *Computational Geometry* 7(5–6):303–325, 1997, doi:10.1016/S0925-7721(96)00005-3.
- **Used for pathwidth by**: T. Biedl et al., "Using ILP/SAT to determine pathwidth, visibility representations, and other grid-based graph drawings", GD 2013, LNCS 8242:460–471, doi:10.1007/978-3-319-03841-4_40 (17% solved in 10 min); D. Coudert, D. Mazauric, N. Nisse, SEA 2014, LNCS 8504:46–58, doi:10.1007/978-3-319-07959-2_5 (95.6% solved; all with n ≤ 82), journal version *ACM JEA* 21:1.3, 2016, doi:10.1145/2851494 (not read).
- **URLs**: the papers cite http://www.graphdrawing.org/download/rome-graphml.tgz, now 404 after redirecting to graphdrawing.unipg.it. Current official copy: https://graphdrawing.unipg.it/data/rome-graphml.tgz (200), linked from https://graphdrawing.unipg.it/data.html.
- **Licence**: none stated.
- **Format**: GraphML, one file `grafo<id>.<n>.graphml`, undirected.
- **Contents**: 11,534 files (the papers say 11,529 and 11,528), n 10–110 (Coudert et al. say ≤ 100), m 9–158. 150 file contents occur more than once byte for byte, so the count of distinct graphs is lower; **not yet deduplicated up to isomorphism**.
- **Optima**: no per-graph pathwidth published; Coudert et al. give only the solved/unsolved distribution by n. The per-graph values would be new. (2026-09-30: the transferred solver in `../../pathwidth_solver/` has proved 11,183 of the 11,534 at ≤ 600 s each; not yet deduplicated or in the dataset.)

## Source collections recorded, not downloaded

- **Harwell-Boeing** (I. S. Duff, R. G. Grimes, J. G. Lewis, "Sparse matrix test problems", *ACM TOMS* 15(1):1–14, 1989, doi:10.1145/62038.62043): https://math.nist.gov/MatrixMarket/data/Harwell-Boeing/ (200), https://sparse.tamu.edu/HB (200). The VSPLIB and CMPLIB HB graphs derive from it; Mallach's 20 HB graphs are from it directly. Not downloaded: the derived sets are what the literature measured.
- **DIMACS colouring**: https://mat.tepper.cmu.edu/COLOR/instances.html (200; the old mat.gsia.cmu.edu host no longer resolves). Superset of TreewidthLIB's `coloring.zip`.
- **Other PACE treewidth heuristic sets**, listed at https://github.com/PACE-challenge/Treewidth: UAI 2014 graphs https://github.com/PACE-challenge/UAI-2014-competition-graphs (200), SAT-competition Gaifman graphs (release asset, 61 MB), road graphs https://github.com/ben-strasser/road-graphs-pace16 (200), transit graphs https://github.com/daajoe/transit_graphs and https://github.com/daajoe/PACE2016_transit_graphs (200). Heuristic-scale; not used in any pathwidth paper found; their exact-scale pieces are already inside the PACE 2016/2017 sets.

## Papers checked for their instances

| Paper | Instances used |
|---|---|
| Duarte et al. 2012, C&OR, doi:10.1016/j.cor.2012.04.017 | VSPLIB (defines it) |
| Biedl et al. GD 2013, doi:10.1007/978-3-319-03841-4_40 | Rome graphs (per Coudert et al.; paper not read) |
| Coudert, Mazauric, Nisse SEA 2014, doi:10.1007/978-3-319-07959-2_5 | Rome graphs, VSPLIB, random digraphs generated with Sage `RandomDirectedGNM` (not a collection) |
| Kobayashi, Komuro, Tamaki SEA 2014, doi:10.1007/978-3-319-07959-2_33 | TreewidthLIB, 207 instances (108 for the search-space study) |
| Sánchez-Oro, Pantrigo, Duarte 2014, doi:10.1016/j.cor.2013.11.008 | VSPLIB (from title and group; **not read**) |
| Fraire-Huacuja, Castillo-García et al., IJCOPI 6(1) 2015 | 108 instances with n ≤ 50: 5 grids (n 9–49; the 3×3 and 4×4 are not in VSPLIB), 15 trees n = 22, 4 HB, 84 Small |
| Jain, Saran, Srivastava, arXiv:1702.05710 (2017) | 248: Small, HB, Grids, Trees |
| Mallach 2018, JDA, doi:10.1016/j.jda.2018.11.012 | 147: 17 TreewidthLIB, 6 grids + 20 trees (VSPLIB), 20 Harwell-Boeing, 84 Small |
| Bannach & Berndt WADS 2019, doi:10.1007/978-3-030-24766-9_4 | DIMACS colouring and PACE named graphs (graph searching) |

**Not found**: the "Ding et al. 2017 IEEE Access" paper from the brief (searches returned nothing matching); any collection made for interval thickness, node search number or narrowness; a downloadable TreewidthLIB.
