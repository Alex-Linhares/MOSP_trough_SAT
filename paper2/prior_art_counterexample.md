# Has anyone found the error in Chu & Stuckey's Theorems 1 and 2? (2026-10-02)

The question: before the paper calls the counterexample to Chu & Stuckey
(2009) Theorems 1 and 2 new, did the authors or anyone else find the error
and correct it? **No correction was found anywhere checked. The later restatement
by the same group repeats the error.**

*Widened 2026-10-03 (loop0008 item 01, "Every citer, swept" below):* 144
citing works, and 24 of the 38 that cite the CP paper read in full. There is
still no correction. A third restatement surfaced: Fink (2012) reproduces
Theorem 1 as true.

*Corrected 2026-10-03 (loop0008 item 02):* Fink's premise is **not** the CP
premise, as item 01 said. It counts only dominated customers of smaller index
than `q`, so `q` itself is excluded and the premise is strictly stronger.
`cexGraph` does not refute it under any labelling. A 15-customer variant does,
in Lean (`fink_theorem1_false`). See "The thesis's theorems in Lean" below.

*Added 2026-10-03 (loop0008 item 03, `revised_algorithm.md` §4.7):* the
pathwidth literature has the **correct form of the rule**, under another name,
though not a report of the error. Tamaki's *commitment lemma* (WG 2011, restated
with proof as Lemma 1 of Kitsunai, Kobayashi, Komuro, Tamaki & Tano,
*Algorithmica* 75, 2016, p. 142) is exactly the repaired definite move when the
target is the child `cl(S ∪ {q})` (Lean: `isHereditarilyDefinite_iff_isCommittable`).
Our soundness proof (Theorem 4.7) is their proof, found independently. The
published Theorem 1 checks their condition at the endpoints only. Their
Corollary 2 (pp. 148–149) even shows that the published premise guarantees a
commitment to *some* intermediate set (Lean: `exists_isCommittable_of_isDefinite`).
None of these papers cites Chu & Stuckey or mentions MOSP. So the paper may
claim the counterexample and the observation that Theorem 1 drops the interior
condition, but **not the repair's soundness as new**. What we found in no
held paper is the matching test for this target (Theorem 4.8), which is a
special case of their minimum-separator computation.

## What was checked

| Source | What it says about the rules |
|---|---|
| Chu & Stuckey (2009), CP, LNCS 5732 (`literature/chu_stuckey_2009.pdf`) | Theorems 1 and 2 as published; false (`Search/PublishedTheorems.lean`). |
| **Chu (2011), PhD thesis, *Improving combinatorial optimization*, Univ. of Melbourne**, ch. 6 (`literature/chu_2011_phd_thesis_improving_combinatorial_optimization.pdf`, Minerva Access hdl:11343/36679) | The later and fuller statement. **Theorem 6.3.6 is Theorem 1 word for word, with the same proof** ("at most open(q, S) extra stacks open, but at least close(q, S) extra stacks closed"). **Theorem 6.3.8, the better move, has a different premise**: `close(q, S) ≥ open(q, S ∪ {r})`, not the CP paper's `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})`. Its proof goes through the definite move. Definition 6.3.4 counts `close(c, S) = |{d : o(d, S) ⊆ o(c, S)}|` with `d` unrestricted, which is the literal reading. **Both theorems are false on `cexGraph`** (below; in Lean, `Search/ChuThesis.lean`). The thesis says its implementation of the better move subsumes the definite move. |
| Chu, Garcia de la Banda & Stuckey (2012), *Constraints* 17, "Exploiting subproblem dominance" (held) | Uses MOSP as a benchmark for generic subproblem dominance (projection keys). Does not restate the definite or better move. |
| Chu & Stuckey (2015), *Constraints* 20, "Dominance breaking constraints" (author PDF `domjournal.pdf`) | Mentions the 2009 paper only in related work, among problem-specific methods whose implementations it calls "somewhat non-rigorous", meaning they prune in the search engine instead of propagating. It points to no error. |
| Beck, Kuroiwa, Lee, **Stuckey** & Zhong (2025), CP 2025, LIPIcs 340, paper 5, "Transition dominance in DIDP" | Cites the 2009 paper as the inspiration for a transition dominance on Graph-Clear (Proposition 14). Does not revisit MOSP or its rules. |
| The 37 citing works listed by Semantic Scholar (2010–2025), including Fink (2012), de Carvalho & Soma (2015), Gonçalves et al. (2016), Frinhani et al. (2018), Martin, Yanasse & Pinto (2022), Kuroiwa & Beck (2023/2026) | None titled or described as a correction. Every held paper in `literature/` was searched for criticism of the rules; there were no hits. |
| Web searches for an erratum, counterexample or "incorrect" with the paper's title | None found. |

The Semantic Scholar list is not the full citation set (Google Scholar counts
more), so this is "not found", not "does not exist". Before submission:

- run the same check on the Google Scholar citers;
- consider writing to the authors. Stuckey is active (Monash, CP 2025). Telling
  them before publication is courteous, and it is the surest guard against a
  false claim of priority.

## The thesis's versions are false too

`python3 paper2/thesis_check.py` is an independent brute force over all
2^14 closed sets of `cexGraph` at k = 6. It shares no code with the solver or
`search_check.py`. Failures are states where a solution exists, the
premises hold, and no solution follows the move. Two readings of `close`:
customers not yet closed, and the literal one that counts every `d`.

| Statement | Failures (unclosed / literal) | First example |
|---|---|---|
| CP Thm 1 = thesis Thm 6.3.6 | 6 / 19 | S = {2}, q = 0 |
| CP Thm 2 | 8 / 27 | S = ∅, r = 2, q = 0 |
| thesis Thm 6.3.8 | 13 / 22 | S = {2}, r = 3, q = 0, close 3 ≥ open 2 (unclosed); S = {1}, r = 6, q = 12 (literal) |

## What this means for the paper

- Cite the thesis next to the CP paper. Say the thesis restates Theorem 1
  unchanged and states the better move with the premise `close(q, S)`, and that
  both are refuted by the same graph.
- ~~A Lean theorem for the thesis's Theorem 6.3.8 would make the claim
  complete. **It has not been written.**~~ *Written 2026-10-03 (loop0008 item
  02), see "The thesis's theorems in Lean" below.*
- Word the claim as "we found no prior report", not "first".

## The thesis's theorems in Lean (loop0008 item 02, 2026-10-03)

`lean/MOSPFormalization/Search/ChuThesis.lean` states each thesis theorem as
published, as a universal claim over `cexGraph` at k = 6 in the form of
`PublishedTheorems.lean`, and proves it false under both readings of `close`.
No `sorry`; the axioms are `propext`, `Classical.choice` and `Quot.sound`
(`cd lean && lake env lean ../paper2/axiom_check.lean`). The wording quoted in
the file's docstring is from the thesis, §6.3, pp. 141–143 (Definition 6.3.4
on p. 141, Theorem 6.3.6 on p. 142, Theorem 6.3.8 on p. 143, printed page
numbers).

| Thesis statement | Lean theorem | Witness |
|---|---|---|
| Theorem 6.3.6 (= CP Theorem 1 verbatim), unclosed `close` | `chuThesis_theorem636_false` (is `chuStuckey_theorem1_false`) | S = {2}, q = 0 |
| Theorem 6.3.6, literal `close` | `chuThesis_theorem636_false_literal` (is `chuStuckey_theorem1_false_literal`) | the same |
| Theorem 6.3.8, unclosed `close` | `chuThesis_theorem638_false` | S = {2}, r = 3, q = 0: close(0, S) = 3 ≥ 2 = open(0, S ∪ {3}); S ++ [3] extends by [1, 4, 6, 12, 13, 0, 5, 7, 8, 9, 10, 11], S ++ [0] has no extension |
| Theorem 6.3.8, literal `close` | `chuThesis_theorem638_false_literal` | the same (the literal premise is weaker) |
| Theorem 6.3.8, a witness for the literal reading only | `chuThesis_theorem638_literal_witness` | S = {1}, r = 6, q = 12: literal close = 2 = open, unclosed close = 1; S ++ [6] extends, S ++ [12] does not (an invariant family of four states) |
| Fink (2012) Teorema 1 (index-restricted `f`) | `fink_theorem1_false` | on `finkGraph` (15 customers), S = {2, 3}, q = 14 |

The "no extension" half at S = {2}, q = 0 is the CP Theorem 1
counterexample's own (`cex_not_solvable_child`), so the thesis's better move
fails at exactly the state where its definite move does: the proof of 6.3.8
goes through 6.3.6 ("after r is played, q becomes a definite move"), and that
step is the one that breaks.

**Fink (2012), with a stronger premise, is false too.** Fink's Teorema 1
(p. 28) uses `|f(α_j, S)| ≥ |o(α_j, S)|`, where `f(α_j, S)` is the set of
items `α_i` with `o(α_i, S) ⊆ o(α_j, S)`, `α_i, α_j ∉ S` and `i < j` (p. 27).
Because `i < j`, `q` itself is never counted, so the premise asks for
`close(q, S) − 1 ≥ open(q, S)` at best: the child must have strictly fewer
open stacks than the parent. That is stronger than the CP premise, and
`cexGraph` does **not** refute it under any labelling of its vertices: no
failing state there has `close ≥ open + 1`. A random search found no failure
either, over about 41,700 random graphs on 6–12 vertices (3 × 300 s, edge
probability 0.15–0.6, every k; the script was not kept). One more twin
does it. `finkGraph` is `cexGraph` plus a customer adjacent to 0 and 2, a third
twin of 3 and 4, with labels 0 and 14 swapped so that the dominated customers
precede q. At S = {2, 3}, k = 6, q = 14: `f(14, S) = {0, 4}`,
`open(14, S) = 2`, `S ++ [14]` costs 6, a solution from S exists
(0, 1, 4, 6, 12, 13, 7, 5, 8, 9, 10, 11, 14), and none from S ∪ {14} (an
invariant family of 12 states). Lean: `fink_theorem1_false`, with Fink's count
as `finkCount`. Brute force: `python3 -m paper2.fink_check` (three failing
states on `finkGraph`, none on `cexGraph`).

Regenerate: `cd lean && lake build MOSPFormalization.Search.ChuThesis`; the
brute force that found the witnesses is `python3 paper2/thesis_check.py`.

## Every citer, swept (loop0008 item 01, 2026-10-03)

**Question.** Has any work that cites Chu & Stuckey (2009) or Chu (2011)
restated, implemented, tested or corrected the definite move or the better
move? That means CP Theorems 1 and 2, or thesis Theorems 6.3.6 and 6.3.8.

**Method.** All of it is regenerated by `python3 -m paper2.prior_art_sweep`
(add `--refresh` to re-query the indexes). The outputs are
`paper2/data/prior_art/citers.csv` (one row per work, with keyword counts) and
`hits.txt` (every hit in context). The verdicts below were written by hand,
from reading those hits and the surrounding pages.

- **Indexes**, queried 2026-10-03:
  - OpenAlex `cites:` on the CP paper (W1493287964, 27 works), the thesis
    (W2278850436, 65) and its IJCAI 2013 extended abstract (W2295506942, 1);
  - Semantic Scholar's citation lists for the same three (37, 100 and 3);
  - OpenCitations, the open index built from Crossref references (16 for the
    CP DOI). Crossref's own cited-by list is open only to its members; its
    public count for the CP DOI is 15.

  Merged by DOI, else by normalised title, this gives **144 distinct works**:
  41 index entries for the CP paper, and 103 works that cite only the thesis
  or its abstract. Google Scholar was not used (it blocks automated access).
- **Full texts.** The script downloads every open-access PDF any index lists.
  Further copies were found by web search and fetched by hand (author pages,
  institutional repositories, Dagstuhl, IJCAI); their URLs are in `HELD` in the
  script. Unpaywall was queried for every DOI without a full text and found
  nothing more for the CP citers. Downloaded PDFs are kept under
  `paper2/data/prior_art/fulltext/`, git-ignored.
- **Search.** Each text was searched for:
  - `definite move`, `better move`, `old move` and `customer search`;
  - `6.3.6` and `6.3.8`;
  - `open stack(s)` and the citation itself;
  - `counterexample`, `incorrect`, `erratum`, `does not hold`, `is false` and
    `unsound`.

  Every passage that mentions open stacks or cites the paper was read in
  context.

### The works citing the CP paper

There are 41 index entries. Three are not citing works:
- the thesis itself (W009), examined above;
- the CPAIOR 2015 proceedings volume (W027), which duplicates Chu & Stuckey
  (2015);
- an ARCH-COMP 2019 report (W053), which OpenAlex links to the paper. Its full
  text was read and contains no such reference.

That leaves **38 citing works, of which 24 were read in full (63%)**. Two of the
unread 14, the ITOR papers on data envelopment analysis (W117, W134), look like
false index links: OpenAlex and OpenCitations both list them, but their titles
have nothing to do with the problem.

| Year | Authors | Venue | DOI | Full text read | What it says about the rules | Correction |
|---|---|---|---|---|---|---|
| 2010 | Chu, Garcia de la Banda & Stuckey | CPAIOR 2010, LNCS 6140 | 10.1007/978-3-642-13520-0_10 | yes, figshare 20365215 | Benchmarks MOSP with a model that "uses customer search and some complex conditional dominance breaking constraints" (§6). This is an **implementation** of the rules in a CP model. They are not stated. | none |
| 2010 | Garcia de la Banda, Stuckey & Chu | IJOC 23(1) | 10.1287/ijoc.1090.0378 | yes, author copy | Calls the CP 2009 solver "the best current solution" for MOSP, and says almost none of its improvements carry over to talent scheduling (§6). | none |
| 2010 | Arbib, Marinelli & Ventura | TRCS 007/2010 (report) | — | yes, Optimization Online | Cites the CP paper as a "breakthrough", for its lower bound in a branch and bound (§1). | none |
| 2010 | Stivala | PhD thesis, Melbourne | — | **no** | (RNA and protein structure; probably cited for dynamic programming or caching) | — |
| 2010 | De Giovanni, Massi & Pezzella | technical report | — | **no** | (genetic algorithm for MOSP) | — |
| 2011 | Chu, Garcia de la Banda & Stuckey | *Constraints* 17 | 10.1007/s10601-011-9112-9 | yes, `literature/` | §4.1 restates the customer-search model in MiniZinc. §9.2's experiments add "conditional dominance breaking constraints [CP 2009]". This is an **implementation**; the rules are not stated. | none |
| 2011 | de Carvalho & Soma | *Gestão & Produção* 18(2) | 10.1590/s0104-530x2011000200006 | yes, SciELO | Takes the SP3 and SP4 optima from Chu & Stuckey. | none |
| 2011 | Lopes | PhD thesis, U. Minho | — | yes, RepositoriUM | One sentence in the §2.3 survey: nogood recording, "a branch-and-bound strategy based on choosing which stack to close next and several pruning schemes". | none |
| 2011 | Arbib, Marinelli & Pezzella | *IJPE* | 10.1016/j.ijpe.2011.12.003 | **no** | (batch scheduling with buffers; tabu search) | — |
| 2012 | Chu & Stuckey | CP 2012, LNCS 7514 | 10.1007/978-3-642-33558-7_4 | yes, author copy | MOSP appears only in related work (§5), among problem-specific dominance methods whose implementations are "often quite ad-hoc", where "it is not clear whether they can be correctly combined with other constraint programming techniques". This is a general caution and names no error. | none |
| 2012 | Chu & Stuckey | "Inter-problem nogood learning" (report) | — | yes, author copy | Uses MOSP as a benchmark for reusing nogoods; the rules are not mentioned. | none |
| 2012 | Chu & Stuckey | CP 2012, LNCS 7514, "Inter-instance nogood learning" | 10.1007/978-3-642-33558-7_19 | **no** (the report version above was read) | — | — |
| **2012** | **Fink** | **PhD thesis, ICMC-USP** | 10.11606/t.55.2012.tde-19022013-084858 | **yes**, saved as `literature/fink_2012_phd_thesis_mosp_novas_contribuicoes.pdf` | **Restates Theorem 1**, the definite move, in Portuguese (pp. 27–28, "Teorema 1"). With `f(α_j, S) = {α_i : o(α_i, S) ⊆ o(α_j, S)}`, the premise is `|f(α_j, S)| ≥ |o(α_j, S)|` and `S ∪ {α_j}` viable; the conclusion is that if a solution extends S, one extends `S ∪ {α_j}`. ~~This is the CP premise, with `close` counted as the size of the dominated set.~~ *Corrected (item 02):* `f` is defined just before (p. 27) by `o(α_i, S) ⊆ o(α_j, S)`, `α_i, α_j ∉ S` **and `i < j`**, so `α_j` itself is not counted and the premise is strictly stronger than the CP one; false on a 15-customer graph, not on `cexGraph` (`fink_theorem1_false`). It is stated, not tested. The better move is not restated. | **none**: the theorem is reproduced as true |
| 2013 | Chu | IJCAI 2013 (extended abstract of the thesis) | — | yes, ijcai.org | Says the thesis's MOSP solver gains orders of magnitude from "dominance rules and relaxations"; does not state them. | none |
| 2013 / 2021 | Leo, Mears, Tack & Garcia de la Banda | CP 2013; *AIJ* 2021 | 10.1016/j.artint.2021.103599 | yes, Monash OA (the *AIJ* version) | Cites the paper as an example of a model improvement worth "several orders" of magnitude (§1). | none |
| 2013 | De Giovanni, Massi & Pezzella | *IJPR* 51(3) | 10.1080/00207543.2012.657256 | **no** | (adaptive genetic algorithm for MOSP) | — |
| 2013 | De Giovanni, Massi, Pezzella, Pfetsch, Rinaldi & Ventura | *ITOR* 20(5) | 10.1111/itor.12025 | **no** | (heuristic and **exact** method for gate matrix connection cost: the unread work most likely to reuse the rules) | — |
| 2014 | Gonçalves, Resende & Costa | *ITOR* | 10.1111/itor.12109 | yes, `literature/` | Calls it a dynamic program simplified by the properties of Becceneri et al. and Yuen & Richardson (§1), and lists it as "DP2" among the methods compared. | none |
| 2014 | Chu & Stuckey | *Constraints* 20 | 10.1007/s10601-014-9173-7 | yes, Springer OA | The same related-work passage (§6), adding that such methods perform "a somewhat non-rigorous propagation of a dominance breaking constraint directly in the search engine". It names no error. | none |
| 2014 | Carvalho & Soma | *JORS* 66 | 10.1057/jors.2014.60 | **no** | (breadth-first heuristic) | — |
| 2014 | Arbib, Marinelli & Ventura | *ITOR* | 10.1111/itor.12134 | **no** (its 2010 report was read) | — | — |
| 2015 | Chu & Stuckey | CPAIOR 2015, LNCS 9075 | 10.1007/978-3-319-18008-3_8 | yes, author copy | Uses the MOSP customer model and its "opens the fewest new stacks" value heuristic (§5). The dominance rules are not mentioned. | none |
| 2016 | Doulabi, Rousseau & Pesant | IJOC 28(3) | 10.1287/ijoc.2015.0686 | **no** | (operating-room scheduling) | — |
| 2017 | Lima & Carvalho | *C&IE* 112 | 10.1016/j.cie.2017.08.016 | **no** | (descent local search for MOSP) | — |
| 2018 | Frinhani, Carvalho & Soma | *PLoS ONE* | 10.1371/journal.pone.0203076 | yes, `literature/` | "The original code of the Chu & Stuckey method ... was compiled and run as recommended by the authors to obtain the optimal values." This is an **implementation used** as the source of optima; nothing is said about its soundness. | none |
| 2018 | de Freitas & Penna | arXiv 1804.03954 (*ITOR*) | 10.48550/arxiv.1804.03954 | yes, arXiv | The paper is in the reference list only. The text cites Murray & Chu (2015), so the reference looks like a mistake. | none |
| 2018 | Santos & Carvalho | *ASOC* | 10.1016/j.asoc.2018.08.017 | **no** | (adaptive large neighbourhood search, gate matrix layout) | — |
| 2018 | Prestwich, Rossi, Tarim & Visentin | GCAI 2018, EPiC 55 | 10.29007/gscn | yes, EasyChair OA | Cites it as CP emulating "solving each subproblem once" by memoisation (§1). | none |
| 2019 | Costa, Yanasse & Nascimento | SBPO 2019 | 10.59254/sbpo-2019-106958 | yes, proceedings | Takes optima from Chu & Stuckey (Table 3), and their remark that sparse instances are harder. | none |
| 2019 | Visentin, Prestwich, Rossi & Tarim | WCGO 2019 | 10.1007/978-3-030-21803-4_42 | **no** (Edinburgh repository refused, 403; the GCAI 2018 version above was read) | — | — |
| 2021 | Martin, Yanasse & Pinto | *ITOR* 29 | 10.1111/itor.13053 | yes, `literature/` | Calls it the best algorithm in the literature. Takes the optima of Frinhani et al., "who made use of the algorithm of Chu & Stuckey". | none |
| 2022 | Camanho, Barbosa & Henriques | *ITOR* | 10.1111/itor.13129 | **no** | (efficiency analysis; probably a false link) | — |
| 2022 | Kuroiwa & Beck | ICAPS 2023 | 10.1609/icaps.v33i1.27200 | yes, AAAI OA | Writes customer search as a dynamic program, `V(R, O)`, with **no dominance rules**, and benchmarks it on the Chu & Stuckey instances. | none |
| 2022 | Doolaard & Yorke-Smith | *AMAI* | 10.1007/s10472-022-09816-z | yes, Springer OA | Uses the MiniZinc open-stacks benchmark, with MOSP defined after Chu & Stuckey. | none |
| 2024 | Lima, Santos & Carvalho | arXiv (Δ-evaluation) | — | yes, `literature/` | Says Chu & Stuckey "improved this method by ... adding new pruning methods in a branch and bound"; uses their instances. | none |
| 2024 | Kuroiwa & Beck | *AIJ* (arXiv 2401.13883) | 10.1016/j.artint.2026.104506 | yes, arXiv | The same dynamic program, again without the dominance rules (App. B.4). | none |
| 2024 | Amirteimoori, Jradi & Ruggiero | *ITOR* | 10.1111/itor.13560 | **no** | (managerial ability, efficiency; probably a false link) | — |
| 2025 | Beck, Kuroiwa, Lee, Stuckey & Zhong | CP 2025, LIPIcs 340, 5 | 10.4230/lipics.cp.2025.5 | yes, Dagstuhl OA | Says its general transition-dominance proof (Prop. 3, App. A) is "inspired by Chu and Stuckey", and builds a Graph-Clear exchange rule (Prop. 14) on the MOSP customer search. The MOSP rules themselves are not restated. Prop. 3 needs the dominance relation to be **irreflexive**. Example 6 and §4 warn that two transitions which dominate each other can turn a satisfiable instance unsatisfiable. That is the general form of our first `better_move` bug, the cycle of `reports/better_move_bug.md`, though it says nothing about the premises of Theorems 1 and 2. | none (for MOSP) |

### The works citing only the thesis

There are **103** of them: 100 cite the thesis and 3 the IJCAI abstract.
**32 were read in full (31%).** Two of those mention open stacks or Chu &
Stuckey in the text, and neither touches the rules:
- Medema et al. (2024, *Constraints*) cites the projection-key caching;
- Prestwich et al. (above) appears in both lists.

The rest cite the thesis for lazy clause generation, Chuffed, nogoods or
symmetry. The unread 71 are listed in `citers.csv`. Judged by title and venue,
all are constraint-solver applications or techniques, from register allocation
to rostering. One unread work could touch the rules: Gange, Chu & Stuckey,
"Certifying optimality in constraint programming" (2019). The author page
blocked the fetch.

### Verdict

Of the **38 works citing the CP paper, 24 were read in full (63%)**; of the 103
citing only the thesis, 32 (31%).

- **No work read restates the better move.**
- **One restates the definite move:** Fink (2012), pp. 27–28, with a premise
  stronger than the CP one (it counts only dominated customers of smaller
  index, not `q`). It is reproduced as true, not tested and not corrected.
  *Corrected in item 02:* `cexGraph` does not refute it; a 15-customer variant
  with a third twin does (`fink_theorem1_false`).
- **Three use an implementation of the rules:**
  - Chu, Garcia de la Banda & Stuckey (2010, 2012): dominance-breaking
    constraints in a CP model;
  - Frinhani et al. (2018): the original C code, run to obtain the optima that
    Martin, Yanasse & Pinto (2022) then reuse.

  None reports a failure.
- **No work read gives a counterexample, an erratum or a correction**, in the
  CP citers or the thesis citers.

So, over this set, **we found no prior report of the error**. Of the unread
works, the one most likely to bear on it is De Giovanni et al. (2013, *ITOR*),
an exact method for gate matrix connection cost. It and the other unread
citers are listed in `literature/MISSING.md` for the owner to fetch. This
check replaces the Semantic Scholar–only row of the first table above. The
remaining guards are unchanged: run Google Scholar by hand, and consider
writing to the authors.

**For the paper.** Cite Fink (2012) beside the CP paper and the thesis, as a
later restatement of Theorem 1, with a stronger premise that a one-vertex
extension of the counterexample also refutes (`fink_theorem1_false`). Cite
Frinhani et al. (2018) as the route by which values computed with the
published rules entered the literature's tables of optima. Cite Beck et al.
(2025), Prop. 3 and Example 6, as the general observation that mutually
dominating moves must be tie-broken. It concerns the cycle, not the premise.
