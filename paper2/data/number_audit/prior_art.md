# Number audit: `paper2/prior_art_counterexample.md` (2026-10-03, loop0008 item 07)

- Document: `paper2/prior_art_counterexample.md`, 271 lines before this audit, 276 after.
  Line numbers below are those **before** the fixes.
- Claims audited: 51 rows (repeated mentions grouped).
- Status counts: REPRODUCED 32, MATCHES-RECORD 15, DRIFT 2 (both fixed), STALE 0, UNSOURCED 1, UNCHECKED 1.

Method.
- **`prior_art_sweep.py` was not rerun.** Its `main` rewrites `citers.csv` and
  `hits.txt`. Step 2 also goes to the network for any full text it lacks. So
  every count was recomputed with `csv` from `paper2/data/prior_art/citers.csv`,
  and the per-index counts from the cached index JSON files.
- `python3 -m paper2.fink_check` was run (0.17 s), and so was
  `python3 paper2/thesis_check.py` (2.4 s).
- Lean statements were read in `Search/ChuThesis.lean`, `PublishedTheorems.lean`,
  `DefiniteMove.lean` and `Layout.lean`. Grep finds no `sorry` in `ChuThesis.lean`.
- PDFs were read with `pdftotext -layout`, using printed page numbers.
- The full texts under `fulltext/` were searched for each quoted phrase, to find
  its section.

| line | claim (short, with the value) | source | check done | status |
|---|---|---|---|---|
| 8-9 | "144 citing works" | `citers.csv` | 144 rows, but 3 are not citing works (W009 thesis, W027 proceedings volume, W053 ARCH-COMP); l. 147 says "144 distinct works" correctly | DRIFT (fixed: "144 index entries (141 citing works)") |
| 9, 175, 238 | 24 of the 38 CP citers read in full, 63%; 14 unread | `citers.csv`: 41 rows cite `cp2009`, 26 with `fulltext`; minus W009, W027, W053 → 38 and 24; 24/38 = 63.2% | recomputed | REPRODUCED |
| 16-17, 97, 115 | 15-customer variant refutes Fink; `fink_theorem1_false` | `ChuThesis.lean:192` (`Fin 15`), `:218` | statement read | MATCHES-RECORD |
| 22-23 | Tamaki WG 2011; Kitsunai et al., *Algorithmica* 75, 2016, Lemma 1 on p. 142 | Kitsunai PDF | header "Algorithmica (2016) 75:138–157"; "Lemma 1 (Commitment Lemma [25])" on p. 142, proof ending on p. 143; ref. [25] is Tamaki, WG 2011, LNCS 6986 | REPRODUCED |
| 24, 28 | `isHereditarilyDefinite_iff_isCommittable`, `exists_isCommittable_of_isDefinite` | `Layout.lean:181, 297` | exist | MATCHES-RECORD |
| 26, 32 | our Theorem 4.7 (soundness) and Theorem 4.8 (matching test) | `revised_algorithm.md` l. 406, 460 | titles match | MATCHES-RECORD |
| 27 | Corollary 2 on pp. 148-149 | Kitsunai PDF | Corollary 2 is stated on p. 148, and the argument runs onto p. 149 | REPRODUCED |
| 29 | none of these papers cites Chu & Stuckey or mentions MOSP | Kitsunai PDF | grep finds no "Chu", "Stuckey", "open stack" or "MOSP". Tamaki 2011 and Kobayashi et al. 2014 were not re-grepped | MATCHES-RECORD |
| 39 | CP 2009, LNCS 5732; `Search/PublishedTheorems.lean` | `PublishedTheorems.lean:70, 79` | theorems exist | MATCHES-RECORD |
| 40, 86-88 | thesis, hdl:11343/36679, §6.3. Def. 6.3.4 on p. 141, Thm 6.3.6 on p. 142, Thm 6.3.8 on p. 143. 6.3.6 matches CP Thm 1 word for word. 6.3.8 has premise `close(q,S) ≥ open(q,S∪{r})`. "better move subsumes definite" | thesis PDF | printed pp. 141/142/143 = pdf pp. 164/165/166. Quotes and premises match, and "Our implementation of better move subsumes definite" is on p. 143. hdl matches `HELD` in the sweep script | REPRODUCED |
| 41, 187 | Chu, Garcia de la Banda & Stuckey, *Constraints* 17; §4.1 model, §9.2 "conditional dominance breaking constraints" | held PDF | §4.1 "Minimization of open stacks", §9.2 "MOSP" | REPRODUCED |
| 42, 200 | Chu & Stuckey, *Constraints* 20, "somewhat non-rigorous", §6 | `fulltext/W024.pdf` | phrase found in §6 "Related work". `citers.csv` year is 2014 (online); the first table says 2015 (volume) | REPRODUCED |
| 43, 219 | Beck et al., CP 2025, LIPIcs 340, paper 5: Prop. 3 (irreflexive), App. A, Prop. 14 (Graph-Clear), Example 6 in §4, "inspired by Chu and Stuckey" | `fulltext/manual/beck_2025_cp.pdf` | DOI `LIPIcs.CP.2025.5`. Every item found, Example 6 within §4 | REPRODUCED |
| 44 | 37 citing works on Semantic Scholar, 2010-2025 | `s2_cites_cp2009.json` | 37 entries, years 2010 to 2025 | REPRODUCED |
| 57-58 | brute force over the 2^14 closed sets of `cexGraph`, k = 6 | `thesis_check.py` | `n, K = 14, 6` | MATCHES-RECORD |
| 63-67 | failures 6 / 19 (Thm 1 = 6.3.6), 8 / 27 (CP Thm 2), 13 / 22 (6.3.8); first examples S = {2}, q = 0; S = ∅, r = 2, q = 0; S = {2}, r = 3, q = 0 (close 3 ≥ open 2); S = {1}, r = 6, q = 12 | `python3 paper2/thesis_check.py` | output: 6, 13, 8, 19, 22, 27 with the same first examples, `([2], 3, 0, 3, 2)` and `([1], 6, 12, 2, 2)` | REPRODUCED |
| 84-85 | no `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound` | grep: 0 `sorry` in `ChuThesis.lean`. `axiom_check.lean` l. 173-179 lists the six theorems; `session_it02.log` l. 169 records the axioms | `lake env lean` not run (budget rule) | MATCHES-RECORD |
| 92-93 | `chuThesis_theorem636_false(_literal)` "is" `chuStuckey_theorem1_false(_literal)` | `ChuThesis.lean:73-87` | proof terms are exactly those theorems | MATCHES-RECORD |
| 94 | `chuThesis_theorem638_false`. S = {2}, r = 3, q = 0, close 3 ≥ 2 = open. S ++ [3] extends by [1, 4, 6, 12, 13, 0, 5, 7, 8, 9, 10, 11]. S ++ [0] has no extension | `ChuThesis.lean:91-108` (`cexThesis_solvable_r`, `cex_not_solvable_child`); thesis_check | sequence identical | MATCHES-RECORD |
| 95 | `chuThesis_theorem638_false_literal`: the same witness | `ChuThesis.lean:110` | proved from the unclosed version via `closeCount_le_closeCountLiteral` | MATCHES-RECORD |
| 96 | literal witness S = {1}, r = 6, q = 12. Literal close = 2 = open, unclosed close = 1. Invariant family of four states | `ChuThesis.lean:122-151` (`cexThesisFamily` has 4 sets); thesis_check `([1], 6, 12, 2, 2)` | checked | REPRODUCED |
| 99-100 | `cex_not_solvable_child` | `DefiniteMove.lean:380` | statement is ¬Solvable cexGraph 6 (cl (insert 0 {2})) | MATCHES-RECORD |
| 105-108, 194, 242 | Fink Teorema 1 on p. 28; `f` with `i < j` defined on p. 27; pp. 27-28 | `literature/fink_2012_*.pdf` | printed p. 27 (pdf 45) defines f with "αi, αj ∉ S e i < j"; Teorema 1 on printed p. 28 (pdf 46) | REPRODUCED |
| 110-112 | `cexGraph` never refutes Fink under any labelling | `python3 -m paper2.fink_check` | "cexGraph, k = 6, any labelling: 0 failures" | REPRODUCED |
| 112-114 | random search: about 41,700 graphs on 6-12 vertices, 3 × 300 s, p 0.15-0.6; script not kept | `Ralph_Loops/loop0008/PROGRESS.md` l. 149; `session_it02.log` l. 164 | record only. It cannot be rerun, because the script was not kept | MATCHES-RECORD |
| 115-117 | `finkGraph` = `cexGraph` plus a customer adjacent to 0 and 2 (a third twin of 3, 4), with labels 0 and 14 swapped | `finkEdges` vs `cexEdges` | the new vertex 0 is adjacent to {2, 14}. Old 0 is now 14, with neighbours {3, 4, 7, 11} plus the new 0 | MATCHES-RECORD |
| 118-120 | S = {2, 3}, k = 6, q = 14. f = {0, 4}, open = 2, S ++ [14] costs 6. Solution (0, 1, 4, 6, 12, 13, 7, 5, 8, 9, 10, 11, 14). Invariant family of 12 states | fink_check; `ChuThesis.lean:203-224` | fink_check prints `S = [2, 3], q = 14, f = [0, 4], open = 2`. `finkFamily` has 12 sets. `fink_solvable` has the same sequence. Cost ≤ 6 holds by `decide` | REPRODUCED |
| 121-122 | fink_check: three failing states on `finkGraph`, none on `cexGraph` | `python3 -m paper2.fink_check` | 3 failures (S = {0,2}, {2,3}, {2,4}, q = 14) and 0 | REPRODUCED |
| 140-141 | OpenAlex: CP 27, thesis 65, IJCAI 1; IDs W1493287964, W2278850436, W2295506942 | `openalex_cites_*.json` (`meta.count`); `TARGETS` in script | 27, 65, 1; IDs match | REPRODUCED |
| 142 | Semantic Scholar: 37, 100, 3 | `s2_cites_*.json` | 37, 100, 3 | REPRODUCED |
| 143-144 | OpenCitations: 16 for the CP DOI | `opencitations_cites_cp2009.json` | 16 | REPRODUCED |
| 145 | Crossref public cited-by count for the CP DOI: 15 | none | no Crossref response is cached; grep of `paper2/` for crossref data finds none | UNSOURCED |
| 147-148, 223 | 144 distinct works = 41 CP index entries + 103 thesis/abstract-only (100 thesis, 3 IJCAI) | `citers.csv` `cites` column: cp2009 39, cp2009+thesis2011 2, thesis2011 100, ijcai2013 3 | recomputed | REPRODUCED |
| 168-173 | three non-citing entries: W009 thesis, W027 CPAIOR 2015 volume, W053 ARCH-COMP 2019 | `citers.csv` | W027 DOI is `10.1007/978-3-319-18008-3` (the volume); W053 has `sources = openalex` | REPRODUCED |
| 176-178 | W117, W134: ITOR DEA papers listed by OpenAlex and OpenCitations | `citers.csv` `sources = openalex+opencitations`, no full text | checked | REPRODUCED |
| 180-219 | table: 38 rows, 24 "yes", 14 "no"; every DOI in the table is in `citers.csv` | doc vs CSV | 38 / 24 / 14. All DOIs present. The unread set {W002, W004, W007, W013, W015, W018, W022, W025, W032, W052, W066, W087, W117, W134} matches the 14 "no" rows | REPRODUCED |
| 182 | Chu et al. 2010, "uses customer search and some complex conditional dominance breaking constraints", §6 | `fulltext/manual/chu_garcia_stuckey_2010_equivalence.pdf` | quote is in §6 "Experiments" | REPRODUCED |
| 183 | Garcia de la Banda et al. IJOC, "the best current solution", §6 | `manual/garcia_stuckey_chu_2011_talent.pdf` | §6 "Related Work" | REPRODUCED |
| 184 | Arbib et al. 2010, "breakthrough", §1 | `manual/arbib_2010_trcs.pdf` | §1 | REPRODUCED |
| 189 | Lopes 2011, §2.3 survey sentence | `manual/lopes_2011_thesis.pdf` | in §2.3.3 | REPRODUCED |
| 191 | Chu & Stuckey CP 2012, "often quite ad-hoc", §5 | `manual/chu_stuckey_2012_dominance.pdf` | §5 "Related Work" | REPRODUCED |
| 196 | Leo et al., "several orders", §1 | `manual/leo_2013_cp.pdf` (CP version; the doc read the AIJ version) | §1 in the CP version. The AIJ version was not re-read | MATCHES-RECORD |
| 199 | Gonçalves et al. §1; "DP2" | `literature/goncalves_2016_brkga_mosp.pdf` | Yuen & Richardson in §1; "DP2 ... Chu and Stuckey (2009)" in the methods table | REPRODUCED |
| 203 | Chu & Stuckey CPAIOR 2015, "opens the fewest new stacks", §5 | `manual/chu_stuckey_2015_value.pdf` | in §5 (also in §4) | REPRODUCED |
| 209 | Prestwich et al. GCAI 2018, §1 | `fulltext/W080.pdf` | "solving each subproblem once only has been emulated in CP [4]" in §1 | REPRODUCED |
| 210 | Costa et al. SBPO 2019, Table 3 | `fulltext/W086.pdf` | "Tabela 3" | REPRODUCED |
| 217 | Kuroiwa & Beck AIJ, App. B.4 | `fulltext/W131.pdf` | "presented in Appendix B.4" | REPRODUCED |
| 224, 238-239 | 32 thesis-only works read, 31%; 71 unread | `citers.csv`: 32 of the 103 with full text, 32/103 = 31.1%; 103 − 32 = 71 | recomputed | REPRODUCED |
| 224-227 | "Two of those [32] mention open stacks or Chu & Stuckey ... Prestwich et al. appears in both lists" | `citers.csv`; S2 / OpenAlex caches; full texts W085, W132, W143 | Prestwich et al. (W080) cites only the CP paper (S2 CP list only). The two works in both lists are Leo et al. (W019) and Chu's IJCAI abstract (W020). Of the 32, only Medema et al. (W132) mention MOSP in the text. W085 and W143 match "Chu & Stuckey" only in reference lists for other papers | DRIFT (fixed) |
| 232-233 | Gange, Chu & Stuckey, "Certifying optimality in constraint programming" (2019) | `citers.csv` W081: 2019, authors "G. Gange; P. J. Stuckey" | the year matches. The index lists two authors, not three. Settling this needs the paper, which is not held and could not be fetched | UNCHECKED |
| 247-251 | three works use an implementation: Chu et al. 2010 and 2012, Frinhani et al. 2018 | table rows | consistent with the table | MATCHES-RECORD |

## Fixes made

All in `paper2/prior_art_counterexample.md`:

1. l. 8-9: "144 citing works" → "144 index entries (141 citing works)". Evidence:
   `citers.csv` (144 rows; W009, W027 and W053 are not citing works, as l. 168-173 say).
2. l. 224-227: "Two of those mention open stacks or Chu & Stuckey ... Prestwich et al.
   (above) appears in both lists." → "One of those mentions ...: Medema et al." Added:
   the two reference-list-only matches (Geibinger et al. 2019, Kletzander et al. 2026),
   the two works that are really in both lists (Leo et al., Chu's IJCAI abstract), and a
   dated audit note. Evidence: `citers.csv` `cites` column (W080 = `cp2009`; W019,
   W020 = `cp2009+thesis2011`); `s2_cites_thesis2011.json` lacks Prestwich et al.;
   `pdftotext` of W085 and W143 shows the matches only in their bibliographies.

## Drifts in other documents

None found in the sources consulted. One small inconsistency inside the document,
left as it is: Chu & Stuckey's "Dominance breaking constraints" is dated 2015 in the
first table (volume year) and 2014 in the sweep table (`citers.csv`, online year).
