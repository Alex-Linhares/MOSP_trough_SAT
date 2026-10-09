# Number audit: `paper2/revised_algorithm.md`

Document: `/home/al/dev/MOSP/paper2/revised_algorithm.md`, 1,518 lines when audited (1,537 after the fixes; line numbers in the table are pre-fix).
Auditor: loop0008 item 07, 2026-10-03.

Claims audited: about 140 individual numbers and names, grouped into 94 rows below.

| status | count (rows) |
|---|---|
| REPRODUCED | 23 |
| MATCHES-RECORD | 64 |
| DRIFT | 2 (both fixed) |
| STALE | 4 (all annotated or updated) |
| UNSOURCED | 0 |
| UNCHECKED | 1 |

Scripts rerun (all cheap, read-only): `python3 -m paper2.fink_check` (0.2 s), `python3 paper2/thesis_check.py` (2.6 s), `python3 -m paper2.solver_fix_split --summary` (read-only), and a scratch brute force `/tmp/ra/chk.py` (independent of the repository code) for every counterexample number.

## Table

| line | claim (short, with the value) | source | check done | status |
|---|---|---|---|---|
| 8–12 | Search/ has "ten files", no `sorry`, axioms propext/choice/Quot.sound | `ls lean/MOSPFormalization/Search/`; grep `sorry`; `paper2/axiom_check.lean` | 11 files now (`Split.lean` added 2026-10-02, loop0007 item 10); no `sorry` in any; axiom_check has no `Split` entry | STALE (fixed: eleven files, `Split` named, axiom_check caveat) |
| 24, 209 | `mospValue_eq_pathwidth_add_one` | Lean grep | exists | MATCHES-RECORD |
| 37, 308–328 | Counterexample 4.5: 14 customers, 26 edges, edge list | `cexEdges` in `Search/DefiniteMove.lean`; `fink_check.CEX_EDGES` | edge lists identical; 26 counted | REPRODUCED |
| 66–68 | "108 re-refuted ... the other 7 need a longer run" | `solver_fix_split --summary` 07:05 | 4 of the 7 refuted by the split: 112 of 115, 3 open | STALE (updated, dated note) |
| 79 | "all functions c(p) ... same minimum number of stacks", PDF p. 4 | chu_stuckey_2009.pdf | on p. 4 | MATCHES-RECORD |
| 101 | cost formula `|O(S) − S ∪ o(c, S)|`, PDF p. 4 | same | p. 4 | MATCHES-RECORD |
| 167–169 | K2, one closed, k = 0 needs one stack | arithmetic | trivially true | REPRODUCED |
| 274–279 | Theorem 1 §3.1, PDF p. 6; close def PDF p. 4 | chu_stuckey_2009.pdf | Theorem 1 on p. 6, close def p. 4 | MATCHES-RECORD |
| 278–279, 41 | Chu (2011) Thm 6.3.6 p. 142, Def 6.3.4 p. 141, chapter 6 | thesis PDF (printed pages) | Thm 6.3.6 printed 142, Def 6.3.4 printed 141 | MATCHES-RECORD (see note on "word for word") |
| 316 | O(S) = {1,2,3,4}, b(S) = 3, S a state | /tmp/ra/chk.py | same | REPRODUCED |
| 317–318 | o(0,S) = {0,7,11}, open = 3, cost = 6 | chk.py | same | REPRODUCED |
| 319–321 | dominated set {0,3,4}, close = 3, o(3)=o(4)={0} | chk.py | same | REPRODUCED |
| 322 | 0 is the first definite candidate | chk.py | definite-premise playable = [0,3,4] | REPRODUCED |
| 323–324 | order 1,3,4,6,12,13,0,5,7,8,9,10,11 costs ≤ 6 | chk.py; Lean `cex_solvable` | cost exactly 6 | REPRODUCED |
| 325–327 | child X = {0,2,3,4}, Sol_6(X) false, seven reachable sets | chk.py; Lean `cexFamily` | 7 sets in `cexFamily`; 7 reachable in chk.py; Sol false | REPRODUCED |
| 339–354 | Lean names `definiteMove_counterexample`, `chuStuckey_theorem1_false(_literal)`, `chuThesis_theorem636_false(_literal)`, `fink_theorem1_false` | Lean grep | all exist | MATCHES-RECORD |
| 349–354 | Fink (2012) pp. 27–28; 15-customer graph refutes it; Counterexample 4.5 graph does not under any labelling | fink_2012 PDF; `python3 -m paper2.fink_check` | Teorema 1 printed p. 28, setup p. 27; fink_check: cexGraph 0 failures any labelling, finkGraph 3 failures | REPRODUCED |
| 358–359 | "at most open(q,S) extra stacks open ... close(q,S) extra stacks closed", PDF p. 6 | chu_stuckey_2009.pdf | p. 6 | MATCHES-RECORD |
| 366–369 | T = {2,3,4}: N[0]\O(T) = {7,11}, X\T = {0}, b(T) = 2, b(T∪X) = 3 | chk.py | same | REPRODUCED |
| 376–378 | edges 0–3, 1–2: open = close = 2; 1,2,0,3 costs 2; 0,1,2,3 costs 3 | chk.py | same | REPRODUCED |
| 387 | b({2,3,4}) = 2 < 3 = b(X) | chk.py | same | REPRODUCED |
| 444–449, 1387 | Corollary/Lemma 4.24 Lean names | Lean grep | exist | MATCHES-RECORD |
| 470, 476–484 | Ore 1955; Mathlib `Finset.all_card_le_biUnion_card_iff_existsInjective'` | Mathlib `Combinatorics/Hall/Finite.lean:242` | exists (Ore 1955 not held, not checked) | MATCHES-RECORD |
| 496–499 | subset rule quote, §2, PDF p. 5 | chu_stuckey_2009.pdf | p. 5 | MATCHES-RECORD |
| 551–561 | Counterexample 4.11: 7 customers, edges, S = {2}, k = 3, playable {0,3,5}, o values, order 0,3,1,4,5,6, no solution from {2,5} | chk.py; Lean `tieEdges`, `noTieBreak_counterexample` | all reproduced | REPRODUCED |
| 568–571 | Theorem 2 §3.2 PDF p. 6; "conditions imply ... definite move" | chu_stuckey_2009.pdf | p. 6 | MATCHES-RECORD |
| 604–617 | Counterexample 4.13: root, no definite fires, 0 and 2 survive subset, premises 3/4 hold for r=2,q=0 (3: 6 ≤ 6; open' = close' = 3), {2} solvable, {0} not, filter keeps 1 | chk.py | all reproduced; kept = [0,1,5,6,7,8,12] | REPRODUCED |
| 611 | invariant family of 18 sets `bmFamily` | `Search/BetterMove.lean:328` | 18 sets counted | MATCHES-RECORD |
| 619–626 | Thm 6.3.8 quote, p. 143 | thesis PDF | printed p. 143, wording matches | MATCHES-RECORD |
| 628–635 | thesis witness S={2}, r=3, q=0: close 3 ≥ 2 open; costs 6 and 5; extension 1,4,6,...; literal witness S={1}, r=6, q=12 holds under literal only | chk.py | close 3, open' 2, costs 6/5, extension cost 6; literal: close 1 (code) vs 2 (literal), open 2, costs 6/6, Sol(S·6) true, Sol(S·12) false | REPRODUCED |
| 638–640 | thesis_check: 2^14 sets, 13 failing triples (code), 22 (literal) | `python3 paper2/thesis_check.py` | 13 and 22 | REPRODUCED |
| 677–685 | Bug A: 12-customer graph, k = 4; Bug B: 8 customers, S = {2}, k = 4, drops 3 citing 0 and 0 citing 3 | `Search/BetterMove.lean` (`bugAEdges`, `bugBEdges`, docstrings) | match; Sol_4({2}) true on bugB (chk.py) | MATCHES-RECORD |
| 689–694 | Theorem 3 §3.3, PDF p. 7, "immediately be pruned" | PDF | p. 7 | MATCHES-RECORD |
| 722–728 | path 4–0–2–1–3, k = 2: c = 3 playable, cost({2},3) = 3, Sol_2({1,2,3}) true, Sol_2({2}) false | chk.py | same | REPRODUCED |
| 726–727 | smallest such graph, exhaustive to 5 vertices | `search_soundness.md:1670–1671` | stated there | MATCHES-RECORD |
| 728 | "is in fact crucial", PDF p. 7 | PDF | p. 7 | MATCHES-RECORD |
| 742 | nogood quote "(PDF p. 4)" | chu_stuckey_2009.pdf | the sentence is on p. 5 (line 26 of p. 5) | DRIFT (fixed → p. 5) |
| 837–838 | one isolated customer, k = 1, Q = {0} (`exec_fake_oldMove`) | Lean grep | exists | MATCHES-RECORD |
| 855–861 | the five `exec_repairedFullFilter_*` theorems | Lean grep | all exist | MATCHES-RECORD |
| 879–885 | default since 2026-10-01, loop0007 items 01–03 | `solver_fix.md` status line | matches | MATCHES-RECORD |
| 904 | 16,244,090 node checks, graphs 1–17 vertices, exhaustive to 6 | `solver_fix.md:125–137` | total 16,244,090; families 1–6 … 14–17 | MATCHES-RECORD |
| 905 | matching vs hereditary: 36,939,226 candidates | `solver_fix.md:134,139` | same | MATCHES-RECORD |
| 906 | C vs Python MOSP: 1,557,980 calls, 1,529 instances, ≤ 125 customers | `solver_fix.md:240–252` | 778,990 per setting × 2 = 1,557,980; 1,529; up to 125 | REPRODUCED (arithmetic from record) |
| 907 | graph solver: 12,582,320 calls, 1,319 graphs, 4–992 vertices | `solver_fix.md:368–379` | same | MATCHES-RECORD |
| 908 | 17,431,232 runs, 52,592 graphs, 1–17 vertices, 64 configurations, 51,454,712 nodes | `solver_fix.md:633,665,684–692` | same | MATCHES-RECORD |
| 909 | differential: 9–75 customers, 1,786,824 calls, zero disagreements | `solver_fix.md:704–712` | 1,511,880 + 245,400 + 25,920 + 3,624 = 1,786,824 | REPRODUCED (sum of recorded rows) |
| 911–912 | ≤ 128 stacks single-word C, 64·WORDS multiword | `solver_fix.md:179,299` | same | MATCHES-RECORD |
| 922–926 | `codeFullFilter_cex`, `not_codeFilterSound_cexGraph`, `CodeRunSound`, `CodeNodeRepaired` etc. | Lean grep | all exist | MATCHES-RECORD |
| 952–963 | 58 of 570,206 runs lose a node; 29 graphs × 2 L; k = opt only; smallest 14; 26 runs cascade at 83 nodes; CodeNodeRepaired 1,781,000 of 1,782,100, fails at 1,100 | `search_soundness.md:2027–2049` | all match | MATCHES-RECORD |
| 966–968 | 6,374 certified; 115 values, 113 distinct graphs, 40–125 customers | `solver_fix.md:916`; CLAUDE.md corpus table | match | MATCHES-RECORD |
| 971–978 | 103 finish in 1,200 s; 33 pass; 70 fail at 0.11% of nodes; all 8 Theorem-2 runs fail at the better move; all 70 re-refuted | `solver_fix.md:1051–1062`, `solver_fix_recheck_tables.md` | same (3,103,541 of 2.72 × 10⁹) | MATCHES-RECORD |
| 989–992 | 58 certificates walked, 32 meet repaired premises | `solver_fix.md:1064–1067` | same | MATCHES-RECORD |
| 996 | none of the 115 values changed | `solver_fix_recheck_tables.md` (changed = 0); split summary (4 more refuted at value − 1) | still true | MATCHES-RECORD |
| 1009–1014 | item 06: 33,867 graphs (1–6), 26,100 (7), 6,000 random 8–16; node checks 111,288,536 / 90,915,044 / 355,181,036 | `search_soundness.md:923–941` | same | MATCHES-RECORD |
| 1015–1016 | Bug A first fails at 12 vertices, Bug B first loses a node at 8 | `search_soundness.md:962–970, 1015–1017` | same | MATCHES-RECORD |
| 1017–1018 | port matched C on all 4,418,084 runs | `search_soundness.md:952` | same | MATCHES-RECORD |
| 1021–1026 | smallest definite-move loss 14 customers; none to 9 vertices (exhaustive); none on 88,802 connected 10-vertex graphs ≤ 14 edges; 14 customers 26 edges after minimising | `search_soundness.md:1276–1287` | same | MATCHES-RECORD |
| 1027 | repair: zero losses in 2.05 G premise checks | `search_soundness.md:1289` | same | MATCHES-RECORD |
| 1028–1030 | 600,000 random graphs 10–18; 90,000 gadget graphs 12–17 | `search_soundness.md:1293–1296` | same | MATCHES-RECORD |
| 1030–1032 | item 12: 570,206 searches, zero wrong answers | `search_soundness.md:2027,2049` | same | MATCHES-RECORD |
| 1099 | corpus 9–40: 6,135 of 6,135, ratios 1.00003, 1.00004 | `solver_fix.md:487–488` | same | MATCHES-RECORD |
| 1100 | C&S 50–100: 118 of 125, 1.0030, worst class 100-50-4 1.010, worst pair 1.013 | `solver_fix.md:505,511` | same | MATCHES-RECORD |
| 1101 | 125 × 125 to 2 × 10⁸ nodes: 11 of 23, 0.9999 | `solver_fix.md` Table 3 (5+5+1 finished; 0.99991) | same | MATCHES-RECORD |
| 1102 | graph pathwidth: 22 to over 1,000 vertices, 731 of 880, 1.020 | `solver_fix.md:553,606` | same | MATCHES-RECORD |
| 1103 | graph benchmarks rerun: 8,456 pairs, up to 957 vertices, 1.003–1.017 per set, median 1.000, worst 1.64 | `solver_fix.md:1280–1301` | 18+102+9+32+26+8,269 = 8,456; set ratios 1.0031–1.0167; worst 1.644 (`grafo6585.97`); `nos2` 957 | REPRODUCED (sum of recorded rows) |
| 1105–1113 | per node ≈ 2% MOSP C (−0.1% to +5.8%), ≈ 6% graph solver; matching fails on 0.07–0.27% of definite candidates (0.07–0.11% at 9–40, 0.13% at 50–100, 0.27% at 125); better pairs 0.02–0.06%; definite stops firing 0.007–0.08% | `solver_fix.md:418–428, 585–597` | all within the recorded table (the summary there says 0.03–0.27% because it includes the graph solver's 0.02%) | MATCHES-RECORD |
| 1115–1118 | longest refutations censored on both sides (`Random-100-100-2`, 125×125 d 2 & 4) | `solver_fix.md:512–515`, Table 3 | same | MATCHES-RECORD |
| 1129–1144 | "108 of 115 done, 7 left"; 6,259 of 6,374 independent; 108 (106 of 113 graphs; 16 of 23 at 125 × 125); 9.73 × 10¹⁰ nodes; 7 named; censored after 10.1 h at 5.0–6.9 × 10¹⁰; priced 13–153 core-h | `solver_fix_recheck_tables.md` (Needs a long run), `solver_fix.md:898–900,1022`; split summary | historical numbers all match their record (3.63 × 10⁴ s = 10.1 h; 4.99–6.88 × 10¹⁰; 12.9–153 core-h; 6,374 − 115 = 6,259); but superseded: 112 of 115, 110 of 113 graphs, 20 of 23 at 125 × 125 | STALE (status line updated, dated note added with split figures) |
| 1155–1157 | 6,276 refutations verify, none rejected, 10 instances at 75 customers time out at 60 s; `DEFINITE_CEX` published certificate rejected | `certificates.md:113–151,186–200`, `data/certificates/tables.md` | 6,276 of 6,286 (`default`); the 10 are SP3, SP3_0, Random-75-75-2-*, -4-{3,4,5}, all 75 customers | MATCHES-RECORD |
| 1158–1162 | root split "proposed and not built" | `solver_fix.md` item 10; `Search/Split.lean`; `solver_fix_split.py` | built 2026-10-02/03 and running | STALE (dated note added) |
| 1173–1174 | Chu & Stuckey PDF p. 1: "graph path-width and gate matrix layout", 12 equivalent problems | PDF p. 1 | "see [3] for a list of 12 equivalent problems" | MATCHES-RECORD |
| 1184–1196 | page ranges: SEA Coudert pp. 46–58; Kobayashi pp. 388–399; Kitsunai Algorithmica 75, pp. 138–157; Suchan & Villanger pp. 324–335; Bodlaender et al. TOCS 50 pp. 420–432 | PDF headers | all match (Suchan & Villanger PDF has no printed numbers: 12 pages, offset 323 assumed) | MATCHES-RECORD |
| 1203 | Kobayashi notation N(T), d(T) p. 390 | PDF | printed 390 | MATCHES-RECORD |
| 1206 | w-feasible / vs: Kobayashi p. 391; Kitsunai "p. 141" | PDFs | Kobayashi 391 correct; Kitsunai defines k-feasible on p. 141 but the (directed) vertex separation number on p. 142 | DRIFT (fixed → pp. 141–142) |
| 1208 | Coudert ν(L,i), SEA pp. 48–49 | PDF | defined across 48–49 | MATCHES-RECORD |
| 1209 | Bodlaender et al. Kinnersley form p. 428 | PDF | Definition 6 / Theorem 7 on 428 | MATCHES-RECORD |
| 1241–1244 | full set: Suchan & Villanger p. 328; Kitsunai fullset p. 143 | PDFs | 328 (by offset); 143 | MATCHES-RECORD |
| 1258 | Kobayashi Algorithm 1, p. 393 | PDF | printed 393 | MATCHES-RECORD |
| 1269–1275 | Coudert §3.2 pp. 51–52; §3.1; Kitsunai Lemma 2 p. 143 | PDFs | §3.2 starts p. 51; Lemma 2 p. 143 | MATCHES-RECORD |
| 1278–1281 | Chu & Stuckey ten references, none a pathwidth algorithm | PDF reference list | 10 references, none on pathwidth algorithms | REPRODUCED |
| 1291–1295 | Kitsunai committable def p. 142, Lemma 1 p. 142, proof pp. 142–143, Proposition 1 p. 141 | PDF | Lemma 1 p. 142, proof ends p. 143 (Corollary 1 follows), Prop. 1 p. 141 | MATCHES-RECORD |
| 1326–1327 | Suchan & Villanger p. 328; Kitsunai Prop. 3 p. 143 | PDFs | same | MATCHES-RECORD |
| 1355–1357 | d(X) = 3 = d(S), d({2,3,4}) = 2 | chk.py; Lean `cex_isDefinite_not_isCommittable` | same | REPRODUCED |
| 1359–1361, 1403–1406 | Kitsunai Lemma 10 & Corollary 2 pp. 148–149, O(km) | PDF | Lemma 10 and Cor. 2 on 148, proof and O(km) running to 149 | MATCHES-RECORD |
| 1373 | W = {2,3,4}, border 2 vs 3 | chk.py; `cex_isCommittable_234` | same | REPRODUCED |
| 1379–1380 | matching fails on 0.07–0.27% | as line 1105 | same | MATCHES-RECORD |
| 1382 | Kobayashi depth, p. 392 | PDF | 392 | MATCHES-RECORD |
| 1389–1393 | Coudert SEA Lemma 3 p. 49, JEA Lemma 6 | PDFs | Lemma 3 on 49; JEA Lemma 6 present | MATCHES-RECORD |
| 1393–1394 | Suchan & Villanger Rule 1, p. 330 | PDF (pdf page 7 → 330 by offset) | Monotone Push Rule on that page, |N(u) ∩ Ũ| = 1 | MATCHES-RECORD |
| 1397–1399 | Kobayashi "extremely effective", depth 2–10 adds little (abstract p. 388; Table 2 p. 394) | PDF | abstract p. 388; Table 2 on 394 | MATCHES-RECORD |
| 1403–1404 | Kobayashi O(n^d), p. 393 | PDF | 393 | MATCHES-RECORD |
| 1433, 1462, 1475 | Coudert Lemma 4 SEA p. 50; JEA Lemma 7; Bodlaender Theorem 1 p. 422, §5.3 p. 428 | PDFs | same | MATCHES-RECORD |
| 1515–1518 | axiom_check heading "loop0008 item 03" | `paper2/axiom_check.lean:181` | present | MATCHES-RECORD |
| 470 | Ore (1955) as the source of the deficiency form | not held in `literature/` | not checkable without the paper | UNCHECKED |

## Fixes made

All in `/home/al/dev/MOSP/paper2/revised_algorithm.md`.

1. Lines 8–13: "ten files (… `Layout`)" → "eleven files (… `Layout`, and `Split`, added 2026-10-02 for the root split of section 4.6.3)", with the caveat that `axiom_check.lean` does not yet print `Split`'s theorems. Evidence: `ls lean/MOSPFormalization/Search/` (11 `.lean` files); `grep sorry` empty; no `Split` entry in `axiom_check.lean`.
2. Lines 66–69: "108 have been re-refuted … the other 7 need a longer run" → "112 … the other 3 are still running", with a dated note. Evidence: `solver_fix_split --summary`: 4-1_0, 2-4_0, 4-5_0, 4-2_0 REFUTED.
3. Line 742 (now 744): nogood quote "(PDF p. 4)" → "(PDF p. 5)". Evidence: `pdftotext -f 5 -l 5 chu_stuckey_2009.pdf`, line 26.
4. Lines 1129–1131: status heading "108 of 115 done, 7 left" → "112 of 115 done, 3 left", marked as an audit update. A dated note after the bullet gives the split's figures: four refuted at k = 56, 45, 56 and 23, 7.04 × 10¹¹ nodes (4.97e10 + 4.98e11 + 7.96e10 + 7.64e10), 228.5 core-hours (18.1 + 154.1 + 26.1 + 30.2), 110 of 113 distinct graphs, 20 of 23 at 125 × 125, 2-4_0 at 154.1 core-hours against a price of 47.5, and 3 in flight. The historical 108 / 9.73 × 10¹⁰ text is kept.
5. Lines 1158–1162: "A faster route for the 7, proposed and not built" kept, with a dated note that it has since been built (`cs_split_expand`, `cs_split_decide`, `paper2/solver_fix_split.py`, `Search/Split.lean` with `execSplit_repairedFullFilter_mospValue`). The note also says that tasks run with an empty memo but do inherit old moves. The original text says "with no old moves".
6. Line 1206 (now 1219): "Kitsunai et al., p. 141" → "pp. 141–142". Evidence: k-feasible is defined on p. 141 and the vertex separation number on p. 142.

## Drifts in other documents (not edited)

- `paper2/solver_fix.md:29–31`, the status paragraph ("108 of the 115 … 7 at 125 × 125 need a long run"), and `:1348` and `:1401–1404` are stale against the split summary. They should read 112 of 115, 3 open. Item 10's own section covers the split, but the top status line was not updated.
- `paper2/data/solver_fix_split_tables.md` still shows `Random-125-125-2-4_0` as partial (1,683 tasks, 148.3 core-h) and 2-1_0 / 2-5_0 at 0 tasks. `--summary` reports 2-4_0 REFUTED at 1,686 tasks and 154.1 core-h. Regenerating it needs `--tables`, which this audit was told not to run.
- Wording, not a number: lines 41 and 278 say the thesis restates Theorem 1 "verbatim" / "word for word". The thesis's Theorem 6.3.6 (printed p. 142) has the same content but different words. It says "S ++ [q] is k-playable … If S has an extension that uses ≤ k stacks, then S ++ [q] also has an extension", where the paper says "U′ = S ++ R is a solution". "Restates it with the same premise and proof" would be accurate. Not changed, because it is not a quantitative claim.
