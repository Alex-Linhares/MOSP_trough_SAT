# Number audit: paper2/plan.md

Document: `paper2/plan.md`, 249 lines before the audit (265 after).
Claims audited: 48 rows.
Status counts: REPRODUCED 17, MATCHES-RECORD 26, DRIFT 1 (fixed), STALE 4 (dated notes added), UNSOURCED 0, UNCHECKED 0.

Line numbers are those of the document before the audit.

| line | claim | source | check done | status |
|---|---|---|---|---|
| 9 | thesis is 2001 in OpenAlex | `openalex_citations.json` works, W1584759191 | year 2001 | REPRODUCED |
| 12 | L&Y 2002, C&OR 29, 1759–1772 | held PDF | running header "Computers & Operations Research 29 (2002) 1759–1772" | REPRODUCED |
| 17, 22, 195 | twelve references, eleven held; Kashiwabara & Fujisawa missing | `paper2/literature/` (11 PDFs: 01, 04, 06–14), `MANIFEST.md` | ls | REPRODUCED |
| 18–19 | thesis is the most-connected citing work, cites eleven of the twelve | cache: per-work count of Table 1 papers cited | thesis 11 (all indexed problem papers; [5] not indexed); next citing work 6; only LY2002 itself also has 11 | REPRODUCED |
| 31 | pathwidth 1,213 relevant works, >3× the other eleven, only name growing | `section2_figures.numbers()` | 1,213 records (1,212 distinct), 380 others, rate 15.0 -> 27.3 | REPRODUCED (popularity.md now footnotes 1,212 distinct) |
| 33–34 | three names with no relevant works, two with a handful | `numbers()` | 0, 0, 0; 6 and 11 | REPRODUCED |
| 35–36 | VLSI 1980s, graph searching 1990s–2000s, MOSP OR generation | `trends.binned` | see popularity audit | REPRODUCED |
| 37–38 | only six works cite a MOSP paper and a graph-theory paper | `mosp_and_graph_theory` | 6 | REPRODUCED |
| 41–43 | six figures in `figures/` | `ls paper2/figures` | six `table1_*.png` present | REPRODUCED |
| 49–51 | three figures redrawn as `figures/sec2_fig{1,2,3}_*.pdf` | `ls` | present | REPRODUCED |
| 52–53 | MOSP fifth under the phrase rule | `mosp_rank_phrase_rule` | 5 | REPRODUCED |
| 60–62 | L&Y 2002 Prop. 2; F&L 1989 Thm 7; F&L 1987 Lemma 4.1; Yanasse 1997a Prop. 5 | held PDFs | pdftotext: Prop. 2 (L&Y p. 1763), Theorem 7 (F&L 1989), Proposition 5 (Yanasse 1997a); Lemma 4.1 cited in F&L 1987 text | REPRODUCED |
| 63 | Kinnersley 1992 pw = vs | CLAUDE.md, `VSEquivPW.lean` `vertexSeparation_eq_pathwidth` | grep | MATCHES-RECORD |
| 64–68 | K&P 1985/1986, Ellis–Sudborough–Turner 1994 within +2, Kornai & Tuza, Fomin, Ohtsuki, Möhring, Lengauer | `equivalences.md` rows 3–11 | ESuT PDF has no text layer; checked against `equivalences.md` row 7 ("Thm 2.1") | MATCHES-RECORD |
| 70–75 | Lean: `mospValue = pathwidth (mospGraph) + 1`, sorry-free; VS = PW; degeneracy ≤ pw ≤ bandwidth; tw ≤ pw; branch lemma; star counterexample | `MOSPGraph.lean` `mospValue_eq_pathwidth_add_one` (0 `sorry`), `VSEquivPW.lean`, `Sandwich.lean` `degeneracy_le_pathwidth_le_bandwidth`, `MOSPGraphExamples.lean` `star_pathwidth_mospGraph` | grep | MATCHES-RECORD |
| 77 | done 2026-09-30, loop0005 | CLAUDE.md | | MATCHES-RECORD |
| 82–85 | seven exact, two bands, two false, one stated gap (LaPaugh) needed by no row | `equivalences.md` Tally (lines 80–86) | seven exact named; split bandwidth and edge search sandwich; PLA (simple) and edge separation false; `EdgeSearchMonotonicity` needed by no row | MATCHES-RECORD |
| 89 | `revised_algorithm.md` written 2026-10-01 | file | | MATCHES-RECORD |
| 103 | certified corpus of 6,376 | CLAUDE.md, `python -m benchmarks.corpus` table | not rerun | MATCHES-RECORD |
| 104 | ensembles 37,800 at n ≤ 40, 6,747 at 50–75 | CLAUDE.md, `reports/ml_nature.md` §9–§10, §16 | | MATCHES-RECORD |
| 105 | two `better_move` bugs "found by the differential harness" | `reports/better_move_bug.md` line 5 and line 157: the first was found by profiling the C inner loop; only the second (§15) by the harness | | DRIFT (fixed) |
| 105–106 | DRAT proofs for 92% at n ≤ 40 | `reports/ml_nature.md` §17 (92.0%) | | MATCHES-RECORD |
| 106–107 | §15, §17, §32 | `reports/ml_nature.md` headings | §15 harness, §17 DRAT, §32 search certificate | REPRODUCED |
| 107–109 | certificate verifies 6,276 of 6,286 at 9–75 | `paper2/data/certificates/tables.md` totals | default 6,276, csearch 6,275, 0 rejected | MATCHES-RECORD (one configuration; the other added, see fixes) |
| 109–111 | two-key rule §28 and its addendum; ridge §11, §25 | `reports/ml_nature.md` headings; CLAUDE.md | | MATCHES-RECORD |
| 112 | C engine to 1,024 vertices | `pathwidth_solver/TRANSFER.md` line 73 | | MATCHES-RECORD |
| 113 | Rome 11,183 / 11,534 proved, 97.0%, ≤ 600 s per graph | `pathwidth_solver/TRANSFER.md` lines 47–48, 74–75 | 11,183/11,534 = 96.96% | MATCHES-RECORD |
| 114 | transferred 2026-09-30 | CLAUDE.md, TRANSFER.md | | MATCHES-RECORD |
| 117–118 | §4.7, `Search/Layout.lean`, Tamaki's commitment lemma | `revised_algorithm.md` line 1164 "## 4.7"; `Layout.lean` `solvable_of_committable` | grep | MATCHES-RECORD |
| 145–151 | exact core: nine names; bands and false rows dropped | `equivalences.md` Tally | consistent | MATCHES-RECORD |
| 162–168 | hunt table: 11 VLSI circuits; VSPLIB, Small; Rome, PACE 2016–17, freetdi, TreewidthLIB colouring | `paper2/data/dataset/tables.md` collections | 11 circuits; VSPLIB trees/grids/HB, Small 84, Rome, PACE 2016/2017, freetdi, TreewidthLIB colouring 58 | MATCHES-RECORD |
| 173–174 | about 145 experimental papers, 24 instance sets | `benchmarks/hunt_citers.md` line 20 | "about 145 experimental works ... 24 distinct instance collections" | MATCHES-RECORD |
| 177–178 | 17,714 classes from 21,754 files in twenty collections | `data/dataset/tables.md` "all" row; 20 collection rows | | MATCHES-RECORD |
| 179 | 16,087 certified with a witness layout | tables.md provenance "all": 12,552 + 3,535 | 16,087 | REPRODUCED |
| 180 | independent checker `dataset_check.py` | file exists | | MATCHES-RECORD |
| 180–181 | Carvalho & Soma files are customers × patterns, unlike Chu & Stuckey | `dataset.md` §1 lines 84–96 | | MATCHES-RECORD |
| 182 | 10 of 11 VLSI circuits at published best known | tables.md "Against published values" | 10 equal; W4 28 vs 27 (solution) | REPRODUCED |
| 184 | 4 cores × 2 hours | `dataset.md` line 428 (5.7 core-hours inside it) | | MATCHES-RECORD |
| 187 | four requests of `benchmarks/README.md` §2 | README §2 | four bullets | REPRODUCED |
| 190 | cost model §19 | `reports/ml_nature.md` §19 heading | | REPRODUCED |
| 203–204 | Theorem 1 false, loop0006 item 08 | CLAUDE.md; `Search/DefiniteMove.lean` | | MATCHES-RECORD |
| 206–210 | "the solver will be fixed ... after loop0006 ... once the fix is in, re-certified" | `solver_fix.md` status line; `python -m paper2.solver_fix_split --summary` | fix default since 2026-10-01; 112 of 115 re-refuted (108 + 4 at 125×125: 4-1 k=56, 2-4 k=23, 4-5 k=45, 4-2 k=56); 3 partial (2-1, 2-5, 4-4) | STALE (dated note added) |
| 211, 215, 220 | decisions dated 2026-09-29 / 09-30 | CLAUDE.md | | MATCHES-RECORD |
| 235–236 | remaining item 2 (Section 2 figures and method paragraph) to do | `popularity.md` "For the paper"; loop0008 item 06 commit 3cb6ad1d3 | done | STALE (note added) |
| 237–242 | remaining item 3 (lemmas, dedupe, format, checker, price, run) to do | `revised_algorithm.md` §4.7 (item 03), `dataset.md` (item 04) | all but the full run done | STALE (note added) |
| 244–247 | remaining item 5: fix both solvers, re-certify, rerun pathwidth benchmarks | `solver_fix.md` lines 10–33, 1153, 1238 | fix in; 112/115; pathwidth widths agree on all 11,424 graphs both runs proved | STALE (note added) |
| 245 | loop0006 items 08, 10 | CLAUDE.md | | MATCHES-RECORD |
| 186–190 | dataset to-do list (dedupe, format, checker, price) | item-04 paragraph above it already says what is left | | MATCHES-RECORD (already annotated in place) |

## Fixes made

All in `/home/al/dev/MOSP/paper2/plan.md`.

- Line 105: "two `better_move` bugs found by the differential harness" -> "two `better_move` bugs,
  the first found by profiling the C inner loop (`../reports/better_move_bug.md`) and the second by
  the differential harness". Evidence: `reports/better_move_bug.md` lines 5 and 157.
- Line 108: "verifies 6,276 of 6,286 corpus refutations at 9–75 customers" -> adds "(6,275 under
  the `csearch` configuration; none rejected; ...)". Evidence: `data/certificates/tables.md`,
  "Totals per configuration".
- Decisions, the definite move (after line 210): dated note, the fix is the default since
  2026-10-01 (loop0007); 112 of 115 values re-refuted with no answer changed, 3 at 125 × 125
  running; pathwidth benchmarks rerun in loop0007 item 08.
- Remaining work item 2: "(Done 2026-10-03, loop0008 item 06)".
- Remaining work item 3: dated note, lemmas done (item 03), dataset deduplicated, formatted,
  checked and priced (item 04); the full run is what is left.
- Remaining work item 5: dated note, done except three re-certifications; same numbers;
  pathwidth widths agree on all 11,424 graphs both runs proved.

## Drifts in other documents

- `paper2/solver_fix.md` lines 28–31 (status paragraph): "108 of the 115 ... and 7 at 125 × 125
  need a long run" is STALE. `python -m paper2.solver_fix_split --summary` now shows 4 of the 7
  refuted (`Random-125-125-4-1_0` k=56, `-2-4_0` k=23, `-4-5_0` k=45, `-4-2_0` k=56) and 3 partial
  (`-2-1_0`, `-2-5_0`, `-4-4_0`): 112 of 115 re-refuted. Not edited (not my document).
