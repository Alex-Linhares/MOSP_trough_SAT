# Number audit: paper2/popularity.md

Document: `paper2/popularity.md`, 411 lines before the audit (447 after).
Claims audited: 58 rows.
Status counts: REPRODUCED 44, MATCHES-RECORD 3, DRIFT 7 (all fixed), STALE 1 (fixed), UNSOURCED 3, UNCHECKED 0.

Main check: `nice -n 10 python3 -m paper2.section2_figures --numbers` (offline, reads only the
caches, writes nothing), plus short offline scripts over `paper2/data/openalex_citations.json`,
`openalex_candidates.json` (through `relevance.kept_works` / `relevance.relevant`) and
`openalex_trends.json` (through `trends.binned`). `pytest tests/test_section2_figures.py`: 3 passed.
Line numbers are those of the document before the audit.

| line | claim | source | check done | status |
|---|---|---|---|---|
| 3 | first measured 2026-09-17 | `git log` of bf2fa43d0 | commit date 2026-09-17 | MATCHES-RECORD |
| 26, 31, 44, 252, 295, 334, 364 | pathwidth 1,213 relevant | `numbers()["names"]["graph path-width"]["relevant"]` | 1,213 records, 1,212 distinct (W4416062387, 2026, returned twice) | REPRODUCED; footnoted as 1,212 distinct (see fixes) |
| 26, 128, 327 | pathwidth 1,571 hits | `numbers()["pathwidth_hits"]` | 1,571 (1,570 distinct) | REPRODUCED |
| 27–37 | relevant / hits per name: GML 110/125, PLA 68/74, MOSP 58/60, VS 55/100, edge 38/95, node 34/127, 1D 11/18, IT 6/10, narrowness 0/35, split bw 0/35, edge sep 0/21 | `numbers()["names"]` | all 22 values equal | REPRODUCED |
| 26, 30 | Kinnersley cited 215 | `openalex_citations.json` (fetched 2026-09-29) | cache 214; 215 was the 2026-09-17 count | DRIFT (fixed: 214) |
| 27, 28 | Möhring 134, Wing 89 | cache | 134, 89 | REPRODUCED |
| 29 | Yanasse 1997 74, Fink & Voss 71 | cache | 75, 71 | DRIFT (fixed: 75) |
| 31, 66, 151 | K&P 1986 cited 294 | cache | 293 | DRIFT (fixed: 293) |
| 32 | K&P 1985 124 | cache | 124 | REPRODUCED |
| 33, 69 | Ohtsuki 107 | cache | 108 | DRIFT (fixed: 108) |
| 35–37 | Kornai & Tuza 44, Fomin 19, Lengauer 77 | cache | 44, 19, 77 | REPRODUCED |
| 34, 74 | Kashiwabara & Fujisawa not indexed | cache `refs` | no ref "5" in cache | REPRODUCED |
| 24–37 | Table 1 reference numbers [1,4] [6,8] [7] [6] [5] [9] [10] [11] [12] [13] [14] [13] | `literature/Linhares and Yanasse - 2002 ...pdf`, p. 1764, Table 1 | pdftotext | REPRODUCED |
| 39–40 | treewidth 6,222 hits, bandwidth minimization 306 | none cached; only in commit bf2fa43d0 text | grep over paper2, reports, data | UNSOURCED (network count of 2026-09-17, never cached) |
| 44–45 | 21× MOSP; other eleven total 380; more than three times | `labelled_relevant` = 380; 1,213/58 = 20.9; 1,213/380 = 3.19 | | REPRODUCED |
| 49–55 | three names zero; IT 6, 1D 11 | `numbers()` | | REPRODUCED |
| 57–58, 337, 367 | MOSP fourth (labels), fifth (phrase rule, VS 65) | `mosp_rank_labels` 4, `mosp_rank_phrase_rule` 5, VS phrase 65 | | REPRODUCED |
| 88–91 | raw unrestricted counts 1,109,296 / 1,755 / 601 / 152 | not cached | grep | UNSOURCED (network, 2026-09-17) |
| 128, 326 | 700 works labelled | `numbers()["labelled"]` | 700 | REPRODUCED |
| 131 | MOSP moves from seventh to fourth | `git show bf2fa43d0:paper2/popularity.md` | MOSP 60 was 7th of 12 there | MATCHES-RECORD |
| 150–152 | nine of eleven indexed problems above the diagonal | cache counts vs relevant | 9 (all but pathwidth and GML) | REPRODUCED |
| 154 | about 5.6 works per Kinnersley citation | 1,213/215 = 5.64 (scatter, 09-17); 1,213/214 = 5.67 (cache) | | DRIFT against the cache (fixed: 5.7, with a note that the figure draws 09-17 counts) |
| 162, 165, 299 | 844 distinct citing works | `citing_works` | 844 | REPRODUCED |
| 165, 299 | 269 cite two or more | `citing_two_or_more` | 269 | REPRODUCED |
| 165–166 | "almost all of those stay inside one discipline" | 269 − 74 = 195 (72%) | | DRIFT (qualitative; fixed: "most (195)") |
| 166, 300, 404 | 74 span two (or more) disciplines | `span_two_or_more_disciplines` | 74 = 72 two + 2 three, excluding LY2002 | REPRODUCED; "two" -> "two or more" fixed |
| 167, 302 | 63 join graph theory to VLSI | `span_gt_vlsi_only` | 63 | REPRODUCED |
| 168, 302 | 6 cite a MOSP paper and a graph-theory paper | `mosp_and_graph_theory` | 6; titles/years: 2001 thesis, 2004 (Yanasse & Limeira "Refinements..."), 2015 graph properties of MOSP, two 2016 VSP/pathwidth, 2017 VSP | REPRODUCED (author names not in cache: titles and years match) |
| 175 | all six except 2001 cite LY2002 | cache | 5 of 6 include LY2002; thesis does not | REPRODUCED |
| 177 | MOSP citers mostly Engineering, 86 of 135 | cache fields | 86 / 135 | REPRODUCED |
| 178 | GT citers mostly CS, 417 of 507 | cache fields | 417 / 507 | REPRODUCED |
| 201, 295 | pathwidth 1,014 over 1970–2024 | `pathwidth_1970_2024` | 1,014 (the duplicate is 2026, outside) | REPRODUCED |
| 203–206 | PLA/GML peak 1980–89; 1D logic none after 2009 | `trends.binned` | GML rate peak 1985, PLA 1980; 1D last work in 2005–09 bin | REPRODUCED |
| 207–210 | node search peaks late 1980s, holds to 2009; edge search early 1990s and 2005–14; VS highest 1985–99 | `trends.binned` rates | node 1.1 at 1985; edge 1.6 at 1990, 1.3/1.0 at 2005/2010; VS 1.6/1.6/1.7 | REPRODUCED |
| 211–212 | MOSP first in 1990s, peaks 2005–14, 12 works 2020–24 | `trends.binned` | 1 (1995), 17, 17, 12 | REPRODUCED |
| 213–215 | pathwidth rate 15 -> 27; 311 in 2020–24 | `pathwidth_rate_1990s` 15.0, `_2020_24` 27.3, `pathwidth_2020_24` 311 | | REPRODUCED |
| 217–223 | citers by decade: Wing mostly Engineering, little after 2000s; Möhring mostly CS; Ohtsuki every decade; K&P peak 2000s; Kinnersley peak 2010s; MOSP papers Engineering, still in 2020s | cache per-ref decades and fields | Wing 74 Eng, 2 in 2010s; Möhring 102 CS; Ohtsuki 1980s–2020s; K&P 1986 peak 2000s (123); Kinnersley 2010s (94); Yanasse 68 Eng, 10 in 2020s | REPRODUCED |
| 234, 288, 309 | caches fetched 2026-09-29 | `candidates_fetched`, `citations_fetched` | both 2026-09-29 | REPRODUCED |
| 241–242 | PDFs at most 6.5 in wide, no text below 7 pt | `pdfinfo`; `section2_figures.py` font sizes | fig2 is 468.8 pt = 6.51 in; fig3 legend `fontsize=6.8` | DRIFT (small; fixed by a dated note) |
| 241 | embedded TrueType fonts | `pdffonts` | DejaVuSans CID TrueType, embedded, all three | REPRODUCED |
| 254 | zero rows had 21, 35, 35 hits | `numbers()` | | REPRODUCED |
| 324, 333 | 2,271 hits | `hits_total` | 2,271 (2,270 distinct) | REPRODUCED |
| 333–334 | 1,593 relevant = 1,213 + 380 | arithmetic on `numbers()` | 1,593 (1,592 distinct) | REPRODUCED; footnoted |
| 336, 346–347 | search games keep 27% and 40% | 34/127 = 26.8%, 38/95 = 40.0% | | REPRODUCED |
| 364 | phrase rule pathwidth 1,215 | `relevant()` over the 1,571 records | 1,215 records; `numbers()` reports 1,214 because it counts a set of ids | REPRODUCED (records; noted in the resolution) |
| 365 | phrase rule other eleven 335 | `phrase_rule_small_total` | 335 | REPRODUCED |
| 366 | ratios 3.2 and 3.6 | 1,213/380, 1,215/335 | 3.19, 3.63 | REPRODUCED |
| 368 | node, edge search phrase rule 11, 12 | `numbers()` | | REPRODUCED |
| 369 | 0, 1, 0 under phrase rule | `numbers()` | | REPRODUCED |
| 371–372 | agree on 543 of 700 (78%) | `labelled_agree_with_phrase_rule` | 543; 77.6% | REPRODUCED |
| 376–377 | disagree on 528 of 1,570 distinct | 1,570 − agree 1,042 | 528 | REPRODUCED |
| 378–379 | 266 kept without the word, 261 no abstract | `numbers()` | 266, 261 | REPRODUCED |
| 382–384 | two real works the rule misses (1991 titles) | not recomputed | | MATCHES-RECORD (titles in the candidate cache not re-searched) |
| 356 | labels made in one session 2026-09-29 | — | not a number checkable from data | UNSOURCED |
| 394–398 | note (a): 1,213 vs 1,212 distinct | `numbers()` `relevant` / `distinct` | 1,213 / 1,212 | REPRODUCED; resolved (see fixes) |
| 399–403 | note (b): four counts moved by one | cache vs 09-17 table | all four confirmed | REPRODUCED; resolved |
| 404–408 | note (c): 74 vs 81 | recomputed: 74 excluding LY2002, 81 including it as OR | | REPRODUCED; resolved |
| 26–37 (header) | citation column undated | — | was 2026-09-17 while the rest is 2026-09-29 | STALE (fixed: column now the 09-29 cache, and dated) |

## Fixes made

All in `/home/al/dev/MOSP/paper2/popularity.md`.

- Lines 20–22: the citation column is dated, "OpenAlex's count as cached on 2026-09-29", with a dated
  audit note listing the four counts that moved. Evidence: `numbers()["cited_by"]`.
- Table: Kinnersley 215 -> 214 (two rows), Yanasse 1997 74 -> 75, K&P 1986 **294** -> **293**,
  Ohtsuki 107 -> 108. Same evidence.
- Table: pathwidth **1,213** gets a footnote, "1,212 distinct works: OpenAlex returned one record
  (`W4416062387`, 2026) twice ... every count in this report counts records. The same holds for
  the 1,571 hits (1,570 distinct)."
- Line 66: (294) -> (293). Line 69: 107 -> 108. Line 151: 294 -> 293.
- Line 154: "about 5.6 works" -> "about 5.7 works" (1,213/214), plus a dated note that the scatter
  figure still draws the 2026-09-17 counts carried by hand in `SCATTER` (`citation_graph.py`);
  no point changes side of the diagonal.
- Lines 165–166: "almost all of those stay inside one discipline. 74 span two disciplines" ->
  "most of those (195) stay inside one discipline. 74 span two or more disciplines (72 two,
  2 three), counting the eleven problem papers and not Linhares & Yanasse (2002)", with a dated note.
- Line 242: dated note, Figure 2.2's PDF is 6.51 in wide and Figure 2.3's legend is 6.8 pt.
- Figure 2.1 caption: adds "OpenAlex returned one pathwidth record twice, so pathwidth's 1,213 are
  1,212 distinct works."
- Method paragraph: footnote `[^dup]` on "1,213 for pathwidth": counts are records as in the
  figures; 1,212 distinct relevant pathwidth works, 1,592 in all, among 2,270 distinct hits.
- Notes for the number audit: (a), (b), (c) each get a dated "Resolved/Checked 2026-10-03" line.
  Decision for (a): the paper quotes records (1,213, as the figure draws it) and footnotes 1,212
  distinct. Decision for (b): one date, the 2026-09-29 cache, throughout. (c): 74 confirmed under
  the caption's definition, 81 with LY2002 counted as OR.

## Drifts in other documents

- `paper2/citation_graph.py`, `SCATTER` (lines 218–237): hard-codes the 2026-09-17 citation counts
  (215, 294, 74, 107) and says "from popularity.md". `popularity.md` now quotes the 2026-09-29 cache
  (214, 293, 75, 108). Either read the counts from `CITE_CACHE` or leave the scatter as is; it is
  not a paper figure. Not edited (code, not my document).
- `paper2/section2_figures.py` line 258: Figure 2.3's legend at `fontsize=6.8`, below the 7 pt the
  text promises; Figure 2.2 crops to 6.51 in. Cosmetic. Not edited.
- `paper2/section2_figures.py` `numbers()`: `phrase_rule` counts distinct ids (1,214 for
  pathwidth) while `relevant` counts records (1,213); `popularity.md` quotes the record count 1,215
  for the phrase rule. Harmless, but the two columns are not counted the same way.
