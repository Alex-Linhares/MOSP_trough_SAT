# Number audit: paper2/equivalences.md

Document: `paper2/equivalences.md`, 1,944 lines at audit start (1,948 after fixes).
Auditor: loop0008 item 07, 2026-10-03.
Claims audited (rows below, repeated mentions grouped): 112.

| status | rows |
|---|---|
| REPRODUCED | 6 |
| MATCHES-RECORD | 103 |
| DRIFT | 1 (fixed) |
| STALE | 1 (dated note added) |
| UNSOURCED | 0 |
| UNCHECKED | 1 |

Sources used: `paper2/data/complex_check.json` (seconds 146.6, seed 20260930),
`pebbling_check.json` (279.4 s), `pebbling_gu_check.json` (9.4 s),
`pebbling_strategy_check.json` (8.8 s), git history of `paper2/axiom_check.lean`
and `tests/test_pebbling_check.py`, grep of every backticked Lean name (393
backticked tokens; every Lean identifier among them is defined, and every
Python helper named exists in `complex_check.py`), and the held PDFs
(`pdftotext -layout`; EST 1994 and Wing et al. 1985 are image-only and were
read as rendered page images).

## Table

### Lean, sorries, axioms

| line | claim | source | check | status |
|---|---|---|---|---|
| 61-63, 691, 746, 799, 843, 903, 966, 1036, 1078, 1153, 1235, 1300, 1783, 1860 | every listed theorem depends only on propext, Classical.choice, Quot.sound; each file sorry-free | `paper2/axiom_check.lean`; grep `sorry` | every master-table Lean name appears in axiom_check.lean; the only `sorry` in `lean/MOSPFormalization` is Sandwich.lean:1008 | MATCHES-RECORD |
| 65-79, 164-177, 704-1002, 1045-1062, 1097-1121, 1173-1212, 1241-1263, 1303-1314, 1802-1808, 1876-1886 | every Lean theorem name and its file (~250 names) | grep `theorem|lemma|def` over `lean/MOSPFormalization/**` | all defined; file attributions in the master table checked one by one (e.g. `nodeSearch_ne_intervalThickness_of_edgeless` in IntervalSearch.lean, `vertexSeparation_eq_pathwidth` in VSEquivPW.lean, `mospValue_eq_pathwidth_add_one` in MOSPGraph.lean under namespace MOSPInstance) | MATCHES-RECORD |
| 110-116, 1126, 1216, 1289 | no allowed sorries added; the one sorry is `conjecture_sqrt_tw_f6` | `Ralph_Loops/loop0005/allowed_sorries.txt` (header only), grep | as stated | MATCHES-RECORD |
| 116 | SplitBandwidth.lean and EdgeSeparation.lean import Sandwich.lean | grep imports | exactly those two Complex files | MATCHES-RECORD |
| 1053-1062 | `plaTracks_idMatrix` = ⌈n/2⌉; `_five` 3 vs 1; `_unbounded` on I_{2c+3}; `plaTracks_pathMatrix_six` pw+1+2 ≤ pla on P_7 | theorem statements | statements read | MATCHES-RECORD |
| 998-1001 | `n ≤ 2 cw(K_{1,n})`, `n ≤ 2 mcw + 2`, star7 / star9 counterexamples | theorem statements | as stated | MATCHES-RECORD |
| 994, 1879, 1882 | Thm 4 Lean form hypothesis "edge or K > 0"; Thm 2 Lean form `2 ≤ K`; VSG form needs an arc u ≠ v | theorem statements | as stated | MATCHES-RECORD |
| 1261-1263 | `tracks_ne_monotoneNodeSearch_one`: 1 track, mns 0 on [1] | theorem statement | as stated | MATCHES-RECORD |
| 136-139 | KP claim (2) false on K_{1,3}, Lean, written outside the loop 2026-09-30 | `KirousisPapadimitriouGap.lean`, commit 623189e9b 2026-09-30 14:19 | as stated | MATCHES-RECORD |
| 1143-1144 | KP gap "checked by hand, not in Lean" (item 10) | as above | superseded the same day by `kirousisPapadimitriou_claim2_false` | STALE (note added) |
| 1285-1288 | axiom_check: 33 theorems + control | `git show 3ac017697:paper2/axiom_check.lean` | 34 `#print axioms` lines = 33 + control | MATCHES-RECORD |
| 1300-1301 | item 14: 11 new lines, 44 theorems in all | `git show cde7332d5:...` | 45 lines (11 new) = 44 + control | MATCHES-RECORD |
| 8, 1301 | built one item per session, 2026-09-30 | git log of Complex/*.lean | all loop0005 commits dated 2026-09-30 | MATCHES-RECORD |
| 1284, 1291 | chain figure `.dot/.pdf/.png`; `lean_repo_plan.md` | ls | present | MATCHES-RECORD |

### Brute-force check (item 02), `complex_check.json`

| line | claim | source | check | status |
|---|---|---|---|---|
| 594 | 2.5 min on 32 cores | json `seconds` 146.6 | 2.4 min | MATCHES-RECORD |
| 622-625 | 1,252 atlas graphs; 400 random (seed 20260930); 630 classes + 1,500 random = 2,130 matrices; 1,027 Ohtsuki boundary instances | json `stats` | 1252, 400, 630, 2130, seed 20260930; 1,027 in ohtsuki_boundary | MATCHES-RECORD |
| 626-627, 172, 1225, 1230 | edge search to 20 edges: 1,632 graphs; 2-expansion 181; G_du 680 | json summary S6, S10 | as stated | MATCHES-RECORD |
| 166-177, 633-653, 837, 1146-1148, 1275-1277 | every checked / failed pair of the results table (2,130; 452; 1,027; 1,652; 208; 1,644; 8; 1,302; 341; 738) | json `summary` | all 21 rows match | MATCHES-RECORD |
| 604 | event-word and model-search θ agree on all 208 graphs to 6 vertices | json S4 | 208 / 0 | MATCHES-RECORD |
| 646 | per-sequence ν = vs + 1 tested on C5, all 120 orders | `tests/test_complex_check.py` l. 66-68 | permutations of range(5) | MATCHES-RECORD |
| 650, 1029 | Thm 7 on 7 graphs, N ≤ 4 | json `lengauer_thm7` | 7 graphs, N 2..4, all hold | MATCHES-RECORD |
| 282-283, 637, 895 | 980 gap 0, 47 gap 1 | json `ohtsuki_boundary.random` | 980 / 47 | MATCHES-RECORD |
| 277-281 | kK_2 checked k = 1..4, tracks = pw+1; path instance 3 pinned vs 2 free | json `ohtsuki_boundary` 1-4, path | as stated | MATCHES-RECORD |
| 898 | 120 inner-gate orders | 5 inner gates, 5! | arithmetic | MATCHES-RECORD |
| 655-658, 402, 408, 1223 | es − vs ∈ {0,1,2} (K_2 0, K_{1,3} 1, K_{3,3} 2, es 5); ib − pw ∈ {0,1}; cw − (pw+1) ∈ [−1, 7]; mcw − (pw+1) ∈ [−2, 3]; K_2 mcw 0 | json `value_sets`, `named` | as stated | MATCHES-RECORD |
| 511-514, 659, 1031 | cw(K_{1,7}) = 4, mcw(K_{1,9}) = 4; cw(K_{1,n}) = ⌈n/2⌉, mcw = ⌈n/2⌉ − 1 | json `named` K1,7 (cw 4, mcw 3), K1,9 (cw 5, mcw 4) | consistent with both formulas | MATCHES-RECORD |
| 659-663, 315, 1055 | I_3, I_4, I_5 fold to 2,2,3 vs t = 1; P_5, P_6, P_7 to 3,3,4 vs t = 2; exhaustive range PLA − (pw+1) ∈ {0,1} | json `pla`, value_sets | as stated | MATCHES-RECORD |
| 665-673, 453-456, 956-957 | sb via ≤ 3 splittings on six graphs equals ib; K_{1,3}: 2 = pw + 1, K_2: 1 | json `split_bandwidth` | as stated | MATCHES-RECORD |

### Pebbling (loop0006), `pebbling_*.json`

| line | claim | source | check | status |
|---|---|---|---|---|
| 1446-1448, 1503 | 1,100 labelled dags ≤ 5 vertices (arcs i<j) | Σ 2^C(n,2), n = 0..5 | 1+1+2+8+64+1024 = 1,100; agreement also covered by P.7's 53,868 | REPRODUCED (count) |
| 1524 | 461 labelled graphs, |V| ≤ 5, |V|+|E| ≤ 9 | enumeration by hand | 1+1+2+8+63+386 = 461 | REPRODUCED (count) |
| 1567 | 1,099 labelled nonempty graphs ≤ 5 vertices | Σ 2^C(n,2), n = 1..5 | 1,099 | REPRODUCED (count) |
| 1687 | `--pebbling` 279 s on 32 cores | json `seconds` 279.4 | | MATCHES-RECORD |
| 1695-1698 | 33,868 exhaustive dags; 20,000 random on 7 vertices; seed 20260930 | json stats (dags 53,868) | 1,100 + 2^15 = 33,868 | MATCHES-RECORD |
| 1699-1701 | 299 G_d graphs, largest G_d 14 vertices | json `gd_graphs`, `gd_bound_V_plus_E` | | MATCHES-RECORD |
| 1702-1704 | 1,252 directive graphs; up to 5,040 orientations for K₇; ns to 6 vertices, 202 graphs | json, 7! = 5,040 | | MATCHES-RECORD |
| 1705-1706, 1768 | 4,394 rooted trees to 11 vertices | json `rooted_trees`; Σ n·t(n) | 4,394 | MATCHES-RECORD |
| 1707-1709, 1737 | 359,744 live positions on dags ≤ 5 | json `lemma_live_positions` | | MATCHES-RECORD |
| 1716-1737 | every checked / failed pair of the P.5 table (53,868; 53,867; 33,867; 33,861; 299; 292; 7; 1,252; 202; 6; 4,394) | json `summary` | all 22 rows match | MATCHES-RECORD |
| 1741-1753 | named-instance table (G_d of K₂, K₃, K₄, C₄, P₄, K₁,₃; ternary out/in-tree; K₁,₄) and gap 0, 1, 2 for n = 2, 3, 4 | json `named` | every cell matches | MATCHES-RECORD |
| 1757-1766 | spider counterexample: 7 vertices, legs of length 2, pbw = pb = 3, bw = b = 2 | json `out_tree_examples[0]` | as stated | MATCHES-RECORD |
| 1765-1767 | no out-tree ≤ 6 vertices has a gap; 7 of 77 at 7, 24 of 184 at 8, 99 of 423 at 9 | recomputed with `complex_check.rooted_trees`, `pbw(...,'kp')`, `bw_unrestricted` | 0 at n ≤ 6; 7/77, 24/184, 99/423 | REPRODUCED |
| 1767-1770 | gap 1 on 1,559, 0 on the rest, never 2; in-trees: repebbling never helped | json `out_trees_by_pbw_minus_bw` {0: 2835, 1: 1559}; P8 rows 0 failed | see note below | MATCHES-RECORD |
| 1777-1778 | in-spider demand 4 | `tests/test_pebbling_check.py` l. 41 | (SPIDER_IN, 4, 4, 4, 4) | MATCHES-RECORD |
| 1690 | eight hand-computed dags | test l. 189 list | 8 entries | MATCHES-RECORD |
| 1841-1844 | `--pebbling-strategy` 9 s; 1,252 graphs; 5,378,453 plays; zero failures | `pebbling_strategy_check.json` (8.8 s) | | MATCHES-RECORD |
| 1853 | five new tests (item 03) | `def test_` count 13 → 18 between ac807e152 and f2fe5a47d | 5 | MATCHES-RECORD |
| 1890, 1931-1932 | 66,067 digraphs ≤ 4 vertices with loops; 1,024 dags on 5 | `pebbling_gu_check.json`; Σ 2^(n²) | 1+2+16+512+65,536 = 66,067 | MATCHES-RECORD |
| 1927, 1937-1938 | `--pebbling-gu` 9 s; 1,252 graphs, 5,378,453 plays; zero failures | json (9.4 s) | | MATCHES-RECORD |
| 1943 | 16 new tests, 41 in the file | pytest --collect-only now: 41; at f2fe5a47d: 25 | 41 − 25 = 16 | REPRODUCED |

### Literature citations (page, theorem, equation numbers)

| line | claim | source | check | status |
|---|---|---|---|---|
| 21-26, 150 | L&Y 2002: Table 1 on p. 1764, not p. 1762 (Fig. 1); the quote | L&Y PDF | Table 1 p. 1764; Fig. 1 p. 1762; the quote begins at the foot of p. 1763 and ends on p. 1764 | MATCHES-RECORD |
| 22 | `literature/MANIFEST.md` gave 1762 until 2026-09-30 | `paper2/literature/MANIFEST.md` l. 5; commit cd012cc68 | | MATCHES-RECORD |
| 199-200, 610 | L&Y p. 1760 eqs. (1)-(2) | PDF | p. 1760 | MATCHES-RECORD |
| 227-228 | L&Y p. 1762 eq. (3) | PDF | p. 1762 | MATCHES-RECORD |
| 238-239 | L&Y Prop. 2 p. 1763 "follows trivially from their definitions" | PDF | p. 1763 | MATCHES-RECORD |
| 508-509 | L&Y Prop. 1 uses modified cutwidth "from Garey & Johnson" | PDF p. 1761: "Modified cutwidth (MCUT) [3]", [3] = Downey & Fellows | wrong attribution | DRIFT (fixed) |
| 191-195 | Yanasse 1997 [1] p. 455 quote; Props. 1-2 on tool switching | `01_yanasse_1997.pdf` | p. 455; Props. 1-2 on p. 457 relate MOSP to MTSP | MATCHES-RECORD |
| 196-199 | Fink & Voss §1.1.1, preprint p. 2, rows = patterns | `04_fink_voss_1999.pdf` | as stated | MATCHES-RECORD |
| 204, 207 | Yanasse 1997a Prop. 5 | PDF | Prop. 5 is the two-panel transformation | MATCHES-RECORD |
| 217-228, 611 | Möhring p. 18 MPP definition and quotes | `06_mohring_1990.pdf` (printed p. = pdf p. + 16) | p. 18 | MATCHES-RECORD |
| 223-224 | GMPP pp. 23-24 | PDF | introduced at the foot of p. 22, figure p. 23, problem statement p. 24; "pp. 23-24" holds the statement | MATCHES-RECORD (pp. 22-24 would be exact) |
| 243-247 | Wing p. 221 realizability; Möhring p. 24 p/n split and multi-row nets | page images; Möhring p. 24 | as stated | MATCHES-RECORD |
| 225-231 | Wing p. 222 Problem 1 quote, "connection graph H", cites Ohtsuki as [3] | page image p. 222 | as stated | MATCHES-RECORD |
| 229-242, 816 | Möhring p. 29 net adjacency graph, Thm 3.2 p. 29; p. 31 left edge; Prop. 3.5 p. 32; Thm 3.4 | PDF | Thm 3.2 p. 29, left-edge sentence and "interval thickness" p. 31, Thm 3.4 and Prop. 3.5 p. 32 | MATCHES-RECORD |
| 295-312, 1070-1072 | PLAMPP p. 25; Prop. 3.15 p. 38; block/constrained pp. 25-26; path partition p. 36, Thm 3.14 p. 36; Prop. 3.16; Thms 4.5-4.6 | PDF | 3.14 p. 36; 3.15, 3.16 p. 38; 4.5 p. 41, 4.6 p. 42 | MATCHES-RECORD |
| 326-331 | Möhring p. 28 eq. (3.2), p. 31 definition | PDF | as stated | MATCHES-RECORD |
| 370, 547-548, 1253 | Möhring Thm 3.9 p. 34, `ns = t` | PDF | "3.9 Theorem: For any graph G, ns(G) = t(G)", p. 34 | MATCHES-RECORD |
| 254-291, 845-866 | Ohtsuki §II pp. 676-677, eqs. (3)-(6), problem p. 677, Thm 3 p. 678, §IV p. 680 eq. (14), "obvious that H is a subgraph" p. 677, chromatic number p. 676, NP-complete citing [11] | `07_ohtsuki_et_al_1979.pdf` | §IV starts p. 679; the boundary condition and eq. (14) are on p. 680; the rest as stated | MATCHES-RECORD |
| 326, 345-361 | K&P 1985 [9]: strategy p. 181, θ definition, Theorem, Lemma p. 182 | `09_...1985.pdf` (Discrete Math. 55, 181-184) | as stated | MATCHES-RECORD |
| 353-365, 387-399, 1080, 1155 | K&P 1986 [10]: §2 p. 208; Thm 2.1 (LaPaugh) and Cor. 2.2 p. 208; Thm 2.3 and the band p. 209 with Figs. 1-3 (es 1/ns 2; 2/2; 5/4); Cor. 2.4 p. 210; Thm 2.5 p. 211; Thm 4.1 p. 216; Turner p. 216 | `10_...1986.pdf` | as stated | MATCHES-RECORD |
| 1131-1134 | [10] p. 217, claim (2) | PDF | proof starts p. 216; (1)-(3) on p. 217 | MATCHES-RECORD |
| 1411-1427, 1531, 1580-1587 | KP pp. 205-206 games; p. 213 directives and Thm 3.1; Cor. 2.4 p. 210; Prop. 3.2, Thm 3.3, star example p. 214 | PDF | as stated | MATCHES-RECORD |
| 421-435, 749, 773-777 | Kornai & Tuza preprint §2 p. 2; Definition; Prop. 2.1; Prop. 3.1 p. 3 | `11_kornai_tuza_1992.pdf` | as stated | MATCHES-RECORD |
| 439-452, 905 | Fomin §3.2 preprint p. 7; "connected, ≥ 2 vertices" p. 1; Thm 8 p. 11; Thms 2, 3, 6 | `12_fomin_1998.pdf` | Thm 2 p. 3, Thm 3 p. 5, Thm 6 p. 8, Thm 8 p. 11 | MATCHES-RECORD |
| 464-470, 525-533, 601-602 | Kinnersley p. 346 definitions and Thm 3.1; Cor. 3.2 p. 347 | `13_kinnersley_1992.pdf` | as stated | MATCHES-RECORD |
| 477-509, 1374-1403, 1454-1532, 1588-1593 | Lengauer: BWP p. 466 (footnote 1); PBWP, VSG, directed-trees remark p. 467; Def. 1a and the edge version p. 468; Def. 1b, Thm 2, "three pebbles" p. 469; invariants (a)-(d) pp. 470-471; Thms 3, 4 and Lemma 5 p. 472; Def. 6 p. 473; §4 p. 475; Acta Inf. 16, 465-475 | `14_lengauer_1981.pdf` | as stated | MATCHES-RECORD |
| 393-405, 527, 1155, 1222-1224 | EST 1994: multigraphs and loops p. 50; vs definition p. 52; search game p. 53; Thm 2.1 p. 54; K_{3,3} vs 3, s 5, §3.3 Fig. 3.6, Thm 2.2 p. 57 | page images | as stated | MATCHES-RECORD |
| 166, 208-209 | F&L 1987 Lemma 4.1; F&L 1989 Thm 7 | PDFs | Lemma 4.1 p. 159, Thm 7 p. 503 | MATCHES-RECORD |
| 170, 324 | [5] Kashiwabara & Fujisawa not held | `paper2/literature/` | no 05_ file | MATCHES-RECORD |
| 1408 | VSG `≤` read as `<` by pdftotext | page image | not rechecked on the image | UNCHECKED |

Note on 1767-1770: I started a full rerun of the tree checks (n ≤ 11, one
core) for the 1,559 and in-tree figures. I stopped it after about 4 CPU-minutes
because the recorded run took 144 s on 32 cores, which is more than an hour on
one core. The figures rest on the JSON. The n ≤ 9 rerun reproduced the
by-size counts exactly.

## Fixes made

1. `paper2/equivalences.md` l. 508-510 (§11): "(L&Y 2002 Prop. 1 uses modified
   cutwidth, from Garey & Johnson, ...)" -> "(L&Y 2002 Prop. 1, p. 1761, uses
   modified cutwidth, citing Downey & Fellows [3] for it, ...)". Evidence: L&Y
   p. 1761, "Modified cutwidth (MCUT) [3]", reference [3] = Downey & Fellows,
   *Fixed-parameter tractability and completeness I*. Garey & Johnson is [19]
   and is not cited there.
2. `paper2/equivalences.md` l. 1144 (Item 10, "A gap in [10]'s proof"): added
   "*(2026-10-03, number audit: since proved in Lean the same day, outside the
   loop, as `kirousisPapadimitriou_claim2_false`, ...)*" after "Checked by hand,
   not in Lean". STALE: commit 623189e9b (2026-09-30 14:19) came after item 10
   (6cd372ff7).

## Drifts in other documents

None found in passing.
