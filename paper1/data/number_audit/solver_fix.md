# Number audit: paper2/solver_fix.md

Document: `paper2/solver_fix.md`, 1,574 lines when audited (1,598 after the fixes).
Audited 2026-10-03, 06:40-07:30. Line numbers below are those of the original 1,574-line file.

Claims audited: 146 rows (repeated mentions grouped). Each row is counted by its first status.

| status | rows |
|---|---:|
| REPRODUCED | 70 |
| MATCHES-RECORD | 58 (two of them, item 10's 00:30 table and its "Still open" paragraph, are also stale now and have notes) |
| DRIFT (fixed) | 6 rows, 7 lines edited |
| STALE (dated note or status update) | 4 |
| UNCHECKED | 5 |
| UNSOURCED | 3 |

`!!!` lines in `paper2/data/solver_fix_split.log`: **none** (checked at the start and the end).

## Table

| line | claim | source | check done | status |
|---|---|---|---|---|
| 26-33 | status: "108 of the 115 ... re-refuted ..., 7 at 125×125 need a long run" | split_results.csv, `--summary` | now 112 re-refuted, 3 in flight | STALE (present tense: updated, with a note) |
| 27-28, 631-636 | 17.4 M whole-search runs at 1-17 vertices (17,431,232), 1.79 M differential calls (1,757,280 + 29,544) | soundness_tables.md | summed | REPRODUCED |
| 32, 1153, 1238 | 11,424 graphs both proved, same width | bench_tables.md, bench.csv | recounted `status` | REPRODUCED |
| 81 | 11 tests, 2.3 s (item 01) | `git show 8a94dd0b7:tests/test_repaired_rules.py` | 11 `def test_`; time not rerun | MATCHES-RECORD |
| 86-87 | digest from commit 392a2bda2, 9,312 decisions, 19,438 nodes | tests/test_repaired_rules.py l.52-54 | grep | MATCHES-RECORD |
| 88-89 | 150 instances, 35,264 decisions matched | loop0007 PROGRESS l.37 | grep | MATCHES-RECORD |
| 90-91 | 60 instances, L in {0,1,4} | test file `range(60)` | grep | MATCHES-RECORD |
| 102-103 | 150 sampled at 5 vertices | test file l.146 | grep | MATCHES-RECORD |
| 129 | labelled row: 33,867 graphs, 6,149,187 / 4,337,313 / 5,946,920 / 0 / 0 / 0 / 3,232,208 | solver_fix_check.json; 33,867 = labelled graphs on 1-6 vertices | compared; counted 1+2+8+64+1024+32768 | REPRODUCED |
| 130 | atlas 7 row: 5,220 (=1,044x5), 1,551,570 / 1,110,315 / 1,782,115 / 780 / 276 / 0 / 584,640 | check.json | compared | MATCHES-RECORD |
| 131 | random row: 600 graphs, 2,994,627 / 2,658,327 / 5,895,953 / 6,959 / 1,943 / 0 / 102,224 | check.json; `range(600)` in solver_fix_check.py | compared | MATCHES-RECORD |
| 132 | pinned row: 5, 26,690 / 23,312 / 109,496 / 1,317 / 974 / 6 / 1,024 | check.json | compared | MATCHES-RECORD |
| 133 | gadget row: 2,000, 5,522,016 / 2,980,090 / 23,204,742 / 268,128 / 7,597 / 296 / 96,000 | check.json | compared | MATCHES-RECORD |
| 134, 136-142 | totals 16,244,090 / 11,109,357 / 36,939,226 / 277,184 / 10,790 / 302 (296 + 6) / 4,016,096; zero failures | check.json `total` | compared, all fail_* = 0 | MATCHES-RECORD |
| 143 | 231 s | check.json `seconds` 230.6 | compared | MATCHES-RECORD |
| 143 | on 12 workers | none (Regenerate says 16) | searched PROGRESS, session log | UNSOURCED |
| 146-149 | Python vs C better move: 117,828 runs, 0 mismatches, pruned on 15,518 | session_it01.jsonl output "117828 mismatch 0 ... pruned 15518" | grep | MATCHES-RECORD |
| 160-161 | ~5 min, ~10 s | check.json 230.6 s | compared | MATCHES-RECORD |
| 208 | 16 tests, 11 s (item 02) | `git show 988e65c1e` | 16 tests; time not rerun | MATCHES-RECORD |
| 211-212 | 25 instances, 36 configurations | test file `range(25)` | grep | MATCHES-RECORD |
| 222-225 | SP4 under a 3,000-node cap; SP2 over 1,000 nodes | test file `max_nodes=3000` | grep | MATCHES-RECORD |
| 245-249 | C/Python families: 400 / 9 / 400 / 300 / 420; sizes 1-8, 8-17, 14-17, 10-24, 10-125; calls 128,300 / 6,450 / 360,350 / 278,850 / 5,040; settings-node differences 0 / 213 / 2,547 / 3,782 / 33 | solver_fix_c_check.json | compared, n_* histograms | REPRODUCED (n-ranges) / MATCHES-RECORD |
| 249 | corpus 420 = 300 at <=40, 58 at 41-64, 62 at 65-125 | `solver_fix_c_check.corpus(300,120,7)` | recomputed sample | REPRODUCED |
| 250-252 | 1,529 instances, 778,990 calls/setting, 1,557,980 calls, 0 disagreements | c_check.json | compared, x2 | MATCHES-RECORD |
| 253-259 | 36.3 M nodes; 6,023 capped; 6,575 differ; 36,263,084 -> 36,274,154 (+0.03%) | c_check.json | compared | MATCHES-RECORD |
| 267-270 | SP2 at 18: 14,281 / 14,291, 0.02 s; SP3 at 33: 1,433,648 / 1,435,137, 1.05 s | session_it02.jsonl output | grep | MATCHES-RECORD |
| 280-281 | ~2 min | c_check.json 101.4 s | compared | MATCHES-RECORD |
| 319-321 | seven tests failed (5 + 1 + 1) | none found beyond the item text | not searched further | UNCHECKED |
| 331 | 8 tests (pathwidth), ~2.5 s | `git show dfd05759d` | 7 functions, one parametrised x2 = 8 | MATCHES-RECORD |
| 337-339 | 30 random graphs, 4-16, 7 configurations | test file at dfd05759d | not opened in detail | UNCHECKED |
| 349-350 | 14 cases instead of 7 | test_identity_mosp.py at dfd05759d | parametrize on repaired x FLAG_SETS | MATCHES-RECORD |
| 371-374 | pw families 400 / 9 / 300 / 300; calls 220,600 / 6,450 / 270,000 / 285,850; impl-calls 1,764,800 / 51,600 / 2,160,000 / 2,286,800; node diffs 90 / 213 / 1,403 / 2,411; max sizes 14, 17, 17, 24 | solver_fix_pw_check.json | compared | MATCHES-RECORD |
| 375, 401 | corpus row 280 = 200 + 80, size **9-125** | `solver_fix_pw_check.corpus(200,80,8)` | recomputed: smallest is 10 customers (10 active) | DRIFT, fixed to 10-125 |
| 376, 402 | wide: 30 graphs, 129-992 vertices, 360 calls, 1,080 impl-calls, 18 | pw_check.json (max_n 992); code n >= 64*4/2+1 = 129 | compared | MATCHES-RECORD |
| 377-385 | 1,319 / 786,620 / 6,291,160 / 12,582,320 / 4,151 / 6,196 capped / 38,645,344 -> 38,654,094 (+0.02%) | pw_check.json | compared | MATCHES-RECORD |
| 390-398 | spot timings Mycielski 5/6, grids, Petersen: 477, 685,211, 631,994, 1,577, 1,283, 130, 96, 25; 0.27-0.30 s | session_it03.jsonl output | grep | MATCHES-RECORD |
| 409-410 | ~7 min, ~3 min | pw_check.json 389.1 s | compared | MATCHES-RECORD |
| 417-422 | +0.004% (n<=40), +0.30% (50-100), -0.01% (125x125), +2.0% (pathwidth), median 1.000 | cost CSVs | recomputed | REPRODUCED |
| 423-425 | about 2% per node, range -0.1% to +5.8%; about 6% pathwidth | cost_overhead.csv; cost_pw.csv | recomputed | REPRODUCED |
| 426-427 | matching fails on **0.03-0.27%** of definite candidates and **0.02%** of better pairs | cost CSVs | recomputed: 0.02% (pw) / 0.07% / 0.11% / 0.13% / 0.27%; better 0.06% (n<=40) and 0.02% elsewhere | DRIFT, fixed to 0.02-0.27% and 0.02-0.06% |
| 428 | stops firing at 0.04-0.08% of filter calls on the hard classes | cost_cs/cs125.csv | 0.039%, 0.079% | REPRODUCED |
| 445-447 | counters: published rules 1.4-5.4% faster per node than pre-counter C | cost_overhead.csv | old/pre = 0.946-0.986 | REPRODUCED |
| 464, 228 | Gate: 1,344 MOSP tests, 110 pathwidth_solver tests (item 04) | loop0007 PROGRESS l.187 | grep | MATCHES-RECORD |
| 479-481 | 5 x 10^7 cap, 22 cores of 32, +-25% load noise | code default; cores not recorded | partly | UNCHECKED |
| 483-488 | Table 1: 6,135 pairs, 0 differ; default 228,147 -> 228,154 (1.00003), 2/1, 1.17 -> 1.15 s; csearch 202,962 -> 202,971 (1.00004), 6/3, 1.01 -> 0.99 s | cost_mosp40.csv | recomputed pairs | REPRODUCED |
| 490-492 | twelve pairs on nine instances, at most 4%, the nine names | cost_mosp40.csv | 9 + 3 pairs, max ratio 1.0396, same names | REPRODUCED |
| 492-496 | old test passed 39,260 / 34,711; matching failed 45 / 23 (0.11%, 0.07%); stopped firing 15 and 6 times, never at <=20 customers; better pairs 17,268, 11 failed | cost_mosp40.csv | recomputed (smallest n with a loss: 30 and 37) | REPRODUCED |
| 500-511 | Table 2, all nine rows and the total 1,358,096,671 -> 1,362,205,210 (1.0030), max/min 1.013/0.996, 118 of 125 finished | cost_cs.csv | recomputed by class | REPRODUCED |
| 513-516 | seconds 1,190.9 -> 1,204.1 (+1.1%); seven censored pairs by name; 7.27e9 / 6.87e9 nodes | cost_cs.csv | recomputed | REPRODUCED |
| 516-522 | counters: 2.38e9 passes, 3.04e6 fails (0.13%); 1.5% on 100-100-6 and 100-50-8; 0.02% on 100-50-2; 1.39e6 of 3.61e9 (0.04%); 7.00e8 pairs, 1.65e5 failed (0.02%) | cost_cs.csv | recomputed | REPRODUCED |
| 526-532 | Table 3: densities 10 / 8 / 6: 628,798 -> 628,799, 0.94 -> 0.88; 28,482,502 -> 28,482,330, 23.9 -> 24.1; 61,858,208 -> 61,850,290, 52.6; densities 4 and 2 capped (5 and 3 pairs) | cost_cs125.csv | recomputed | REPRODUCED |
| 535-541 | 11 finished, ratio 0.99991; 12 capped, 2,178.5 -> 2,144.6 s; 0.27% (1.08e6 of 3.94e8); 0.08%; better 0.02% | cost_cs125.csv | recomputed | REPRODUCED |
| 543-553 | Table 4: every set row, nodes, ratios, seconds; 880 graphs, 731 both proved; 1,340 -> 1,436 s | cost_pw.csv | recomputed (trees from rows, stems collide) | REPRODUCED |
| 555-558 | 149 unproved got the same width; 1,340 graph-settings match recorded widths, zero differences | cost_pw.csv against `pathwidth_solver/bench/results/*.csv` base files | recomputed: 149/0; 1,340/0 against the base files (1,462/0 with the `_w` and capped reruns too) | REPRODUCED |
| 558-559 | Rome median 1.000, max 1.13 grafo7529.93, 2.77e8 -> 3.13e8 | cost_pw.csv | recomputed | REPRODUCED |
| 552 | Rome seed 20261001 | solver_fix_cost.py l.190 | grep | MATCHES-RECORD |
| 560-562 | Dorogovtsev 3,282 vertices, recorded run 4,007 s | bench/results/named.csv (4007.603 s) | grep | MATCHES-RECORD |
| 562 | pool stopped after 1.8 h | none (PROGRESS says only "stopped by PID") | searched PROGRESS, logs | UNSOURCED |
| 564-565 | 0.388 -> 0.412 us/node on Rome, +6% | cost_pw.csv | recomputed 0.3880 / 0.4118 | REPRODUCED |
| 568-571 | 680 components; 1.11e5 of 5.39e8 (0.02%); colouring 0.45%; trees 0; 42,420 of 6.32e8 (0.007%); 1,355,670,489 -> 1,359,336,939 (+0.27%) | cost_pw.csv | recomputed | REPRODUCED |
| 575-587 | Table 5 µs/node and ratios, six instances, two finish below the cap | cost_overhead.csv, cost_tables.md | recomputed medians of 5 | REPRODUCED, except below |
| 582 (orig. 584) | Random-100-100-2-1_0 old / pre-counter = **0.987** | cost_overhead.csv | 0.98649 (tables.md shows 0.9865, rounded twice) | DRIFT, fixed to 0.986 |
| 591-597 | counter summary table (all five rows) | cost CSVs | recomputed | REPRODUCED |
| 604-606 | 9-40 corpus; 125 instances, 118 finished; 23 and 11 finished; 880 graphs, 731 proved | cost CSVs | recomputed | REPRODUCED |
| 605 | Pathwidth: **22-1,000+ vertices** | cost_pw.csv `n` | 4 to 2,916 | DRIFT, fixed to 4-2,916 |
| 609 | per-node +0-6% | overhead | -0.1% to +5.8% | REPRODUCED |
| 615-619 | stage timings (~1, ~22, ~8, ~70, ~10 min) | not rerun (would re-solve) | - | UNCHECKED (budget) |
| 620 | `--stage tables` regenerates cost_tables.md | `write_tables(/tmp/...)` then `diff` | identical to the committed file | REPRODUCED |
| 631-633 | 16,279,232 runs over 40,592 graphs; 1,152,000 over 12,000 gadgets at 12-17; 51,454,712 nodes | soundness_tables.md | summed | REPRODUCED |
| 636-637 | 43,935 at 9-40 (1,757,280 calls), 1,231 at 50-75 (29,544, none censored) | soundness_tables.md | compared | MATCHES-RECORD |
| 638, 721-722, 911, 1359 | `benchmarks.corpus`: 6,374 of 6,376; 6,372 refutation, 2 bound, 2 open | `python -m benchmarks.corpus` | rerun | REPRODUCED |
| 659 | test 1.4 s | not rerun | - | MATCHES-RECORD (historical) |
| 687-692 | port/gadget table rows and totals (52,592 / 290,363 / 17,431,232 / 51,454,712 / 4,203; 344 / 664 / 194 / 3,001) | soundness_tables.md | summed port + gadget | REPRODUCED |
| 700 | relabellings 8 at n<=40, 4 at 50-75 | diff75 runs: 12 runs = 6 labellings x 2 configs (identity + 4 + 1 re-covering) | consistent | MATCHES-RECORD |
| 709-712 | differential table: 37,800 / 6,135 / 1,080 / 151; calls; lattice oracle 10,800 / 2,812 | soundness_tables.md | compared | MATCHES-RECORD |
| 715-719 | 10 refutation calls skipped by §33; 12,310 refutations at 50-75 both settled; 0.998x nodes | diff75.csv.gz against learning/data/ensemble/differential_scale.csv | recomputed: 12,310 pairs, 10 `skipped`, ratio 0.99807 | REPRODUCED |
| 723-724 | `solutions/` untouched since 2026-09-27; digest `229207b225a666a5` | git log; sha256 of repr(sorted (name, value, provenance)) | recomputed digest | REPRODUCED |
| 736-739 | ~12 min, ~19 min | soundness_tables.md: 699.3 s, 1,133.5 s | compared | MATCHES-RECORD |
| 775 | bound recomputed for 33, all reproduced | provenance_tables.md `bound` 33 | compared | MATCHES-RECORD |
| 779-787 | ratchet 859fa9299 2026-09-17 16:24; customer search 3f5faa03b 2026-09-18 19:33; 60a68f4e3; 231f4db73 same afternoon; four SAT files finished before | git log | checked dates (231f4db73 16:52, overnight 1442 file 17:04) | REPRODUCED |
| 788, 821 | SAT 6,226; lattice 2,812; DRAT 5,646; bound 4,909 | provenance_tables.md | compared | MATCHES-RECORD |
| 796-798 | treewidth only extra evidence for 8, all at 40-50; expansion for none | provenance.csv `secondary_evidence` | recounted 8 at n = 40, 50 | REPRODUCED |
| 800-803 | GP1-8 have SAT or bound evidence; SP3, SP4 listed; SP2 SAT | provenance_all.csv.gz | checked flags | REPRODUCED |
| 810-817 | evidence-by-size table | provenance_tables.md | compared | MATCHES-RECORD |
| 819-822 | no isomorph rescue; 113 distinct graphs; no bound above a stored value | provenance_all.csv.gz (`ev_isomorph` 0, `bound_above_value` 0) | recounted | REPRODUCED |
| 827-835 | size table 2 / 12 / 10 / 22 / 20 / 26 / 23 | provenance.csv n_customers, n_patterns | recounted | REPRODUCED |
| 842-849 | certifying-run table 81 / 8 / 7 / 7 / 1 / 11 | provenance.csv `configuration` | recounted | REPRODUCED |
| 851-853 | 96 never used Theorem 2, 19 did | provenance.csv `theorem2` | 96 / 19 | REPRODUCED |
| 855-863 | 94 of 115 already refuted; the 21 listed by name | provenance.csv `repaired_refuted` | 21 NaN, same names | REPRODUCED |
| 865-866 | "the **five** day-long recertify refutations at 125x125, of 4.9e10 to 4.6e11 nodes" | provenance.csv `recertify_nodes` | six counts among the 21 (2-1, 2-4, 2-5, 4-2, 4-4, 4-5), 4.89e10-4.58e11 | DRIFT, fixed to "six" |
| 879 | ~15 s | not rerun (the script writes data files) | - | UNCHECKED (would write) |
| 884 | the list, 115 rows | provenance.csv | 115 | REPRODUCED |
| 898-900 | 108 of 115 (106 of 113 graphs); every listed at 40-100 and 16 of 23 at 125; 9.73e10 nodes in 16.5 core-h | recheck_repaired.csv | recomputed: 108 unsat, 9.734e10, 59,469 s | REPRODUCED |
| 901-903 | 7 censored after 10.1 h, 5.0-6.9e10 nodes | recheck_repaired.csv | 36,214-36,329 s; 4.99-6.88e10 | REPRODUCED |
| 905-908 | 103 old runs finish; 33 pass, 70 fail; 0.11% (3.10e6 of 2.72e9) | recheck_audit.csv | recomputed (2.72e9 are filter calls, i.e. expanded nodes) | REPRODUCED |
| 981-985 | validation: 36,126 calls on 6,005 graphs; 2,000 per family; 14-17 and 8-20 vertices | recheck_validate.json | summed | REPRODUCED |
| 993-996 | 303,895 node checks, 0 disagreements; 718 failing nodes on 662 runs, 223 unsat, all gadgets | validate.json | summed | REPRODUCED |
| 996-999 | cert stage: 58 instances, up to 1.38e6 nodes, counts agree, checker verified all | recheck_cert.csv | recomputed | REPRODUCED |
| 1009-1018 | by-size table: listed / repaired / audit / cert / censored | recheck_tables.md, recheck CSVs | compared | MATCHES-RECORD |
| 1020-1022 | 21 workers, until 06:15; 9.73e10 nodes, 59,469 s | recheck_repaired.csv | nodes and seconds recomputed; workers from command | REPRODUCED |
| 1026-1040 | the 21 expensive rows: nodes, seconds, Theorem 2 (csearch switch) | recheck_repaired.csv (`better_move`) | compared each row | REPRODUCED |
| 1043-1045 | Random-100-100-2 cost 2.5-13x the cost model's pre-fix price | recheck_tables.md price column | 2.5x (2-4), 10.7x (2-1), 13.0x (2-3); 2-2 and 2-5 are priced from other sources | MATCHES-RECORD |
| 1046-1049 | counters: 1.28e11 / 2.64e8 (0.21%) / 1.60e8 / 4.14e10 / 9.29e6 (0.02%) | recheck_repaired.csv | summed | REPRODUCED |
| 1051-1061 | way 2: 1,200 s; 103 unsat (7.57e9 nodes); 33 pass, all Theorem 2 off, by size 2 / 10 / 5 / 6 / 6 / 4; 70 fail at 3,103,541 (0.11% of 2.72e9 filter calls), 3,020,712 definite, 82,829 better; all 8 Theorem-2-on runs fail at the better move; no `sat`, 12 censored | recheck_audit.csv + provenance.csv | recomputed | REPRODUCED |
| 1063-1069 | way 3: 58 fit, all Theorem 2 off, 40-125, 1.38e6 nodes, 12.6 MB; 32 pass, 26 fail at 2,940, all definite; C audit agrees on 58; 57 exceed the cap | recheck_cert.csv | recomputed | REPRODUCED |
| 1073-1081 | 10.1 h; 1.1e6 nodes/s for the price; runs at 1.4-1.9e6 | recheck_repaired.csv | 1.38-1.90e6 nodes/s | REPRODUCED |
| 1083-1091 | long-run table: lower bounds, cost model, recertify, prices, core-hours (12.9 ... 153) | recheck_tables.md, recheck_long.csv | compared | MATCHES-RECORD |
| 1073-1096 | the seven "need a long run" | split_results.csv | four since refuted by item 10 | STALE (dated note added) |
| 1093-1094 | 4-5_0 passed its recertify count (5.52 vs 4.89e10) | recheck_tables.md | compared | MATCHES-RECORD |
| 1095-1096 | all seven old runs fail `CodeNodeRepaired` in their audit | recheck_audit.csv | 105,528-1,081,457 failing nodes each | REPRODUCED |
| 1123-1126 | ~5.5 core-h, ~2 core-h, ~8 min | audit 5.54 h; cert 2.11 h of emit+check+walk | recomputed | REPRODUCED |
| 1140-1141 | 87.1 core-h for way 1, 70.6 the censored; 5.5; 2.1 | recheck CSVs | recomputed 87.05 / 70.54 / 5.54 / 2.11 | REPRODUCED |
| 1155-1158 | 13 old only, all prove at the old width; 24 Rome new | bench_tables.md, bench.csv | recounted | REPRODUCED |
| 1166-1167 | old stems: 50 tree rows, 35 names | cost_pw.csv (35 unique tree names) | recounted | REPRODUCED |
| 1176-1180 | `--hard` default 1.5 x time + 120 s; Dorogovtsev 4,007 s, killed at 1,020 s | bench_tables.md "killed after 1020 s"; named.csv | compared | MATCHES-RECORD |
| 1187 | 4 tests, 6 s | `git show badb92a60` (4 test functions) | counted | MATCHES-RECORD |
| 1220 | load 16 + 8 then 24; first sweep 32 | session commands | not re-traced | UNSOURCED |
| 1224-1226 | grafo6585.97 and grafo9492.80 reproduce 11,322,729 and 956,733 | bench.csv old_nodes | compared | MATCHES-RECORD |
| 1230-1238 | Table 1 (vertex ranges, graphs, proved, both, same, new only, old only) | bench_tables.md, bench.csv | recomputed `n` ranges (named max 3,282 is the killed graph) | REPRODUCED |
| 1242-1245 | 14 Coudert Table 4 graphs match; myciel6/7 unproved; grid sides 5-13; trees at encoded width | `bench/summary.py --dir bench/results/repaired` (read-only) | rerun | REPRODUCED |
| 1246-1248 | Rome passes 10,522 (10,502), +390 (+386), +282 (+295); 11,194 / 11,534 = 97.05% (97.0%); 340 open, all n >= 86 | bench/results{,/repaired}/rome*.csv | recounted | REPRODUCED |
| 1252-1271 | Table 2: 13 graphs, n, widths, old/new nodes and ratios; old 346-597 s; new 386-565 s | bench_tables.md | compared | MATCHES-RECORD |
| 1273-1276 | 24 new-only at 92-100 vertices, at the old upper bound | bench_tables.md | compared | MATCHES-RECORD |
| 1280-1287 | Table 3: all six rows | bench_tables.md | compared | MATCHES-RECORD |
| 1289-1290 | +0.3% to +1.7%; median unchanged; item 04's +2.0% on 731 | bench_tables.md, cost_pw.csv | compared | REPRODUCED |
| 1292-1295 | 43 of 8,269 > 5% extra, 1 saves > 5%; worst grafo6585.97 (97, width 9) 1.64x, 1.13e7 -> 1.86e7 | bench.csv | recomputed | REPRODUCED |
| 1300-1302 | largest proved 957 (nos2); everything above 1,024 unproved | bench.csv | recomputed (22 graphs > 1,024, none proved) | REPRODUCED |
| 1322 | 130.7 core-hours (Rome 111, others 20) | bench/results/repaired/*.csv seconds | summed 130.7 (110.8 / 19.8) | REPRODUCED |
| 1347-1349, 1401-1412, 1453 | item 09: "108 of 115", "Seven are not yet re-refuted", "the seven 125x125 refutations" | split_results.csv | now 112, three in flight | STALE (dated note added) |
| 1385-1392 | proposed CLAUDE.md numbers: 17.4 M, 1.56 M, 12.6 M, +0.004%, +0.3%, -0.01%, +0.3-2%, about 2% | items 01-08 above | consistent | MATCHES-RECORD |
| 1448 | 1,356 MOSP tests across 73 modules, 114 pathwidth_solver tests | PROGRESS l.339/387; `git ls-tree 96728a745 tests/` | 73 modules counted | REPRODUCED |
| 1467-1470 | session it10 lost its connection at 18:57; run stopped at 00:30 | loop0007/loop.log 18:57:48; split.log 00:30:00 | grep | MATCHES-RECORD |
| 1491-1492 | cap doubling to four times the base | not checked in code | - | MATCHES-RECORD (code docstring not opened; no number rerun) |
| 1500-1505 | Split.lean sorry-free; `ExecSplit`, `ExecSplit.exec`, `execSplit_repairedFullFilter_mospValue` | Search/Split.lean | grep: 0 `sorry`, all three present, statement concludes `k < M.mospValue` | MATCHES-RECORD |
| 47-58, 653, 858, 926, 933, 1374-1375 | Lean names: `HasDefiniteMatching`, `IsHereditarilyDefinite`, `isHereditarilyDefinite_iff_hasDefiniteMatching`, `repairedFullFilter`, `codeFullFilter`, `IsRepairedBetter`, `exec_repairedFullFilter_mospValue`, `codeExec_mospValue_of_repaired`, `CodeNodeRepaired`, `CodeRunSound`, `definiteMove_counterexample`, `Exec.sound`, `FilterSound`; `Search/PublishedTheorems.lean`, `Search/DefiniteMatching.lean` | lean/MOSPFormalization/Search/ | grep each | MATCHES-RECORD |
| 93-97 | `DEFINITE_CEX`: S = {2}, k = 6, old keeps [0], repaired keeps [3] | check.json `definite_cex_filter` | compared | MATCHES-RECORD |
| 1529 | run 2026-10-02 15:26 to 2026-10-03 00:30, 24 workers | split.log restart 15:26:25; session_it10 `--workers 24` | grep (an earlier start at 14:12 was restarted at 15:26) | MATCHES-RECORD |
| 1533-1535 | refuted rows 4-1, 4-5, 4-2: tasks 669/7, 616/9, 842/9; nodes 4.97e10, 7.96e10, 7.64e10; waste 1.5e10, 2.7e10, 3.3e10; core-h 18.1, 26.1, 30.2; item 07 censored 5.12, 5.52, 4.99e10 | split_results.csv, split_tables.md | recomputed core_seconds/3600 | REPRODUCED |
| 1536-1539 | partial rows at 00:30: 2-4_0 1,683/39, 4.72e11, 1.82e11, 148.3; 4-4_0 82/2, 8.93e9, 3.57e10, 12.1; 2-1_0, 2-5_0 0/3 | split_tables.md (committed 67f142f74); tasks.csv cut at 00:31 | compared | MATCHES-RECORD as of 00:30; STALE now (note added) |
| 1543-1544 | wall times 53 min, 2 h 19 min, 5 h 36 min | split_results.csv wall_started/finished | 53:13, 2:18:35, 5:35:55 | REPRODUCED |
| 1544-1545 | every task unsat or stopped, no SAT | split_tasks.csv | 0 `sat`, 0 witnesses (statuses: unsat, split, stopped) | REPRODUCED |
| 1546-1547 | 111 re-refuted, 4 open | split_results.csv | now 112, 3 in flight | STALE (dated note added) |
| 1548-1551 | 2-4_0 passed 4.7e11, 2.5x the 1.88e11 price | split_tables.md | 4.72 / 1.88 = 2.51 | MATCHES-RECORD |
| 1550 | "with 320 tasks still queued" (for 2-4_0) | split.log 00:30:00 "320 queued" | that is the whole queue; 2-1_0 and 2-5_0 alone had 260 unstarted children, so 2-4_0 had at most 60 | DRIFT, fixed to "queued across the four open instances" |
| 1553-1554 | 24 tasks in flight recorded as `stopped` | split_tasks.csv | 24 `stopped` rows | REPRODUCED |
| 1563-1569 | four open, in flight, five-day budget, 20 workers, `--until 2026-10-08T00:40` | `ps` of PID 1465015 | command line matches | MATCHES-RECORD; STALE for 2-4_0 (note added) |

## Fixes made

All in `/home/al/dev/MOSP/paper2/solver_fix.md` (original line numbers).

1. l.26-33, status line (present tense): "item 09: documents only)." -> adds "item 10: 4 of the 7 refuted by the root split, so 112 of the 115 are re-refuted, and 3 are in flight)" plus a dated note. Evidence: `solver_fix_split_results.csv`, `--summary`.
2. l.375: pathwidth corpus row size "9-125" -> "10-125". Evidence: `solver_fix_pw_check.corpus(200, 80, 8)` gives 10 to 125 customers, all active.
3. l.401: "corpus instances of 9-125 customers" -> "10-125". Same evidence.
4. l.426-427: "0.03-0.27% of definite-move candidates and 0.02% of better-move pairs" -> "0.02-0.27% ... and 0.02-0.06%". Evidence: the item's own counter table (pathwidth 0.02%, n <= 40 better pairs 0.06%), recomputed from the cost CSVs.
5. l.584: Random-100-100-2-1_0 old / pre-counter "0.987" -> "0.986". Evidence: medians 0.54901 / 0.55653 = 0.98649. `solver_fix_cost_tables.md` prints 0.9865, which rounds twice to 0.987.
6. l.605: "Pathwidth: 22-1,000+ vertices" -> "4-2,916 vertices". Evidence: `solver_fix_cost_pw.csv` column `n`.
7. l.865: "the five day-long recertify refutations" -> "the six recertify refutations". Evidence: `solver_fix_provenance.csv` has six `recertify_nodes` among the 21. The stated range 4.9e10-4.6e11 already spans all six.
8. l.1550: "with 320 tasks still queued" -> "with 320 tasks still queued across the four open instances". Evidence: `solver_fix_split.log` at 00:30:00 counts the whole queue.
9. Dated STALE notes added: item 07 "Needs a long run" (four of seven refuted since); item 09 (108 -> 112, three in flight to 2026-10-08); item 10 after the results bullets (2-4_0 refuted k = 23 at 02:55:23, 1,686 tasks, 4.98e11 nodes, waste 1.82e11, 154.1 core-h, 7.9x item 07's censored count; 112 re-refuted, 3 in flight; the 07:04 `--summary` figures for the three); item 10 "Still open" (2-4_0 refuted, three in flight under the run to 2026-10-08).

## Drifts in other documents

- `paper2/data/solver_fix_cost_tables.md` itself is correct (0.9865 for the 0.98649 ratio). It regenerates byte for byte.
- `CLAUDE.md` says "the five 125x125 recertify counts" (in the `better_move` bug bullet). That was written before the sixth recertify entry (2026-09-29). The records hold six. Not edited (owner's file).
- Not a drift, worth knowing: in `solver_fix_bench_tables.md`, `grafo11470.91` and `grafo8647.91` have identical node counts in both runs (1,150,778,069 and 1,171,540,004). They are probably isomorphic or duplicate Rome graphs. Nothing in the document depends on this.

## Current split run (for the record)

`python -m paper2.solver_fix_split --summary`, 2026-10-03 07:04:
4-1_0, 2-4_0, 4-5_0, 4-2_0 REFUTED. 2-1_0 partial, 196 tasks, 7.55e10 nodes, 39.3 core-h. 2-5_0 partial, 82 tasks, 3.21e10, 36.7. 4-4_0 partial, 337 tasks, 9.0e10, 49.2. PID 1465015 is alive, with `--until 2026-10-08T00:40`. No `!!!` line in the log, and no `sat` task in `solver_fix_split_tasks.csv`.
