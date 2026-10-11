# Nudging *The pathwidth complex* once more: a second review

Reviewed 2026-10-11 against the LaTeX in `paper1/latex/` at commit
`cd692902c` (abstract at `main.tex:103-133`), the notes in `paper1/`,
`pathwidth_solver/` (`TRANSFER.md`, `PLAN.md`, `bench/reference.py`,
`bench/results/repaired/`), `literature/pathwidth_solvers_README.md`, the held
Coudert, Mazauric & Nisse (2016) PDF, and a few web checks (SageMath docs,
GitHub). No file other than this one was changed, and no process was started
or stopped. Line numbers are per file. This review does not repeat
`abstract_nudge_review.md` (called "the first review" below). Where one of its
suggestions is still unapplied and matters here, it is named once.

---

## 1. What moved

The first review's §7 abstract and the current one (`main.tex:105-132`)
contain the same facts in nearly the same order. What changed is who acts and
what comes last.

| | First review §7 | Current abstract | Effect |
|---|---|---|---|
| Naming | "We call the cluster the *pathwidth* complex because ..." | "We call this cluster the \emph{pathwidth complex} because ..." (`:115-117`) | Naming is now an act of the authors. But the term is already introduced at `:108-109`, so the abstract now defines it twice (see §4). |
| MOSP's rank | A clause: "; since 2005 the next most active name is MOSP" | Its own sentence: "Since 2005, the next most active name is MOSP." (`:117-118`) | The authors' community moves from a footnote to a beat of the story. |
| Wrong optimum | "reports a wrong optimum, which a SAT solver and a checked DRAT proof confirm" | "reports an optimum of 7, where our corrected search finds the optimum, 6, which a SAT solver confirms with a checked DRAT proof" (`:122-124`) | Concrete numbers, with the authors' search as the protagonist. The configuration qualifier is now missing (see §4). |
| Soundness | "prove the repaired search sound" | "prove our corrected search sound" (`:126`) | Ownership. |
| 115 values | "It re-proves all 115 ..." | "We re-prove all 115 ..." (`:126-127`) | Agency moves to the authors. |
| Graph solver | "ported to graphs it proves ... 11,194 of the 11,534 Rome graphs" | "ported to graphs, our corrected search proves ..." (`:127-129`) | Ownership. |
| Release | "We release the proofs, both solvers and 17,714 benchmark graphs ... with independent checkers." | "... are open source, together with independent checkers." (`:129-131`) | Release becomes a property claim ("open source"). |
| Closing | none | "We believe ours is currently the best pathwidth solver openly available." (`:131-132`) | The abstract now ends on the solver, not on the dataset. |
| Cost | Not in §7 either. The 2% was in the pre-review abstract. | Absent | Nothing lost relative to §7. Note that "at most 2% more nodes" is good news, not a hedge (see §2.1). |
| Length | about 235 words | 322 words of source (`sed -n 105,132p main.tex \| wc -w`) | Longer than §7. Check IJOC's abstract limit by hand before submission; the INFORMS author pages could not be read by script (`todo.md:27-29`). |

**In emphasis.** The abstract now reads as the authors' paper about the
authors' table, the authors' community and the authors' solver. Chu & Stuckey
appear as the source of the search that the authors corrected. This is a
legitimate frame: the table, the correction, the matching test and the port
to graphs are theirs. It is also a frame that puts more weight on two
sentences that the body supports less than the rest, the release ("open
source") and the solver claim ("best ... openly available"). §3 and §4 deal
with these two.

**In voice.** First person throughout, with one hole: "the previous
algorithm" (`:122`, `:127`). In a first-person abstract that opens with "In
2001 and 2002 we listed ...", a reader can take "the previous algorithm" to
mean *our* previous algorithm. In the body this is harmless, because each use
follows a citation. In the abstract it is a real ambiguity (fix in §4 and §5).

---

## 2. Nudging the body once more in this direction

Format: `file:line` | current | proposed. Only small edits. Where the
mechanical rename to "our corrected" left a sentence awkward, the row is
marked **[rename]**.

### 2.1 Introduction (`sec1_intro.tex`)

| file:line | current | proposed |
|---|---|---|
| `sec1_intro.tex:24-25` | "MOSP is NP-hard \citep{Linhares2001,LY2002}." | "We showed MOSP to be NP-hard \citep{Linhares2001,LY2002}." This was suggested in the first review and is still unapplied. It is the one place before the table where the first-person frame can be set up in four words. |
| `sec1_intro.tex:219` | "\emph{Our corrected search, and a pathwidth solver.}" | Keep. |
| `sec1_intro.tex:224-226` | "but on a 34-customer instance it reports an optimum of 7 where the optimum is 6, which a SAT solver confirms ..." | "but on a 34-customer instance our implementation of it, with the better move off, reports an optimum of 7 where the optimum is 6, which a SAT solver confirms ..." The body states the configuration (`sec4_search.tex:489-491`) and so does the conclusion (`sec6_conclusion.tex:46-47`). The intro bullet is the only summary that drops it. |
| `sec1_intro.tex:228-230` **[rename]** | "and prove the corrected search sound. Over each benchmark set it changes the total number of search nodes by at most 2\%." | "and prove our corrected search sound. It costs at most 2\% more search nodes over each benchmark set." "It" currently has two possible antecedents (the matching test, the search), and "changes ... by at most" reads as a hedge. Written as a cost, it reads as a selling point. |
| `sec1_intro.tex:230-233` | "Ported to graphs, it proves the pathwidth of 11,194 of the 11,534 Rome graphs within 600 seconds each, all 50 VSPLIB trees and 39 of the 73 Harwell--Boeing graphs (Sections ...)." | "Ported to graphs, it is an exact pathwidth solver, which we release: it proves the pathwidth of 11,194 of the 11,534 Rome graphs within 600 seconds each, all 50 VSPLIB trees and 39 of the 73 Harwell--Boeing graphs, more on each set than the published branch and bound of \citet{CoudertMazauricNisse2016} (Sections ...)." This is where the abstract's closing sentence gets its first support in the body (see §3.6). |
| `sec1_intro.tex:234-236` | "re-proved all 115 benchmark optima that rested on the previous algorithm, and none changed (as of 9 October 2026)." | Drop "(as of 9 October 2026)". All 115 were finished by 2026-10-04 (`solver_fix.md:1605-1613`). The date belongs to the two never-certified values (`sec5_results.tex:155-163`), not to the 115. Here it reads as a hedge that is not needed. |
| `sec1_intro.tex:236` | "We release 17,714 graphs" | Keep. It is already the right voice. |
| `sec1_intro.tex:246-247` | "Section~\ref{sec:results} reports its cost and the dataset" | "Section~\ref{sec:results} reports what our corrected search costs, how it performs as a pathwidth solver, and the dataset" |
| `sec1_intro.tex:254-255` | "The Lean development, both solvers, the dataset and an independent checker for each are released with the paper." | "The Lean development, both solvers, the dataset and an independent checker for each are open source, under the MIT licence (page~\pageref{sec:data})." Do this only once the URL is in `sec7_data.tex` (see §4.1). |

### 2.2 Conclusion (`sec6_conclusion.tex`)

| file:line | current | proposed |
|---|---|---|
| `sec6_conclusion.tex:19-21` | "Read as a pathwidth algorithm, the best exact open-stacks search turned out to rest on two false dominance theorems, and the rule that corrects them was already known in the pathwidth literature." | "... turned out to rest on two false dominance theorems; the rule that corrects one of them was already known in the pathwidth literature, and with it and our corrected better move the search is sound." As written, "the rule that corrects them" says that one known rule corrects both theorems. The known rule (Tamaki's commitment lemma) corrects the definite move only. The corrected better move is "none found / proved here" (`sec4_search.tex:593`). |
| `sec6_conclusion.tex:43` | "where the previous algorithm lost the last solution" | "where the previous algorithm \citep{ChuStuckey2009} lost ...". This is the first use in the section; the citation now comes only at `:64`. |
| `sec6_conclusion.tex:54-57` **[rename]** | "The repair is cheap, one bipartite matching per candidate and at most 2\% more nodes per benchmark set, and it changed none of the 115 benchmark optima it re-proved." | "Our correction is cheap: one bipartite matching per candidate and at most 2\% more nodes per benchmark set. Our corrected search re-proved all 115 benchmark optima that rested on the previous algorithm, and changed none." This avoids the noun "the repair" and avoids "it ... re-proved" with "the repair" as subject: a repair does not prove anything. |
| `sec6_conclusion.tex:59-63` | "Use our corrected search as an exact pathwidth solver: on the benchmarks with published exact pathwidth results it proves more graphs than reported (Table~\ref{tab:graphs})." | "Use our corrected search as an exact pathwidth solver. On every benchmark set with published exact pathwidth counts it proves more graphs than the published branch and bound of \citet{CoudertMazauricNisse2016} (Table~\ref{tab:graphs}). We believe it is currently the strongest exact pathwidth solver openly available, and it is open source." This is the body home for the abstract's closing sentence (§3.6), with the evidence one reference away. |
| `sec6_conclusion.tex:84-86` | the limit on comparisons | Keep. Add, after "\citet{CoudertMazauricNisse2016}": "; on one graph they report, the Mycielski graph $M_7$ (95 vertices), their tuned branch and bound proves the pathwidth in about 10 minutes and our search does not within 25 minutes". When the SageMath run of §3.5 is done, replace the whole item with its result. |
| `sec6_conclusion.tex:92-105` | open problems | Keep. Optionally end the paper on the release rather than on lower bounds: "Every value, layout and certificate above is in our repository, and the solver that produced them is open source." |

### 2.3 Section 4: how "our corrected search" is framed (`sec4_search.tex`)

Principle: **"our corrected" fits the search, the better move and the matching
test. It should not be attached to the definite move's premise, which the
paper itself says is Tamaki's commitment lemma and "not new"
(`sec4_search.tex:327-330`, Table 4.2 row "definite move, corrected ...
known").** The bare "the corrected definite move", without "our", is right,
and so is the theorem title at `:313`. Do not "upgrade" those uses to "our".

| file:line | current | proposed |
|---|---|---|
| `sec4_search.tex:12-24` | "... and ported to graphs it is an exact pathwidth solver (Sections ...)." | "... and ported to graphs, our corrected search is an exact pathwidth solver, which we release (Sections ...)." |
| `sec4_search.tex:29-30` | "on every benchmark the previous algorithm answers correctly" | "on every benchmark the previous algorithm, the search as \citet{ChuStuckey2009} publish it, answers correctly". This is the term's first use in Section 4. The citation at `:15` names "the customer search", not "the previous algorithm", so the term needs a definition here, once. |
| `sec4_search.tex:32-34` | "And when every benchmark optimum that rested on the search was proved again with corrected rules, no value changed" | "And when we proved every benchmark optimum that rested on the search again with our corrected rules, no value changed" |
| `sec4_search.tex:41-43` **[rename]** | "The repair costs at most 2\% more search nodes on each benchmark set" | "Our correction costs at most 2\% more search nodes on each benchmark set" |
| `sec4_search.tex:219` **[rename]** | "\subsection{The definite move is false as published, and its repair is a matching}" | "\subsection{The definite move is false as published, and its correction is a matching test}" |
| `sec4_search.tex:296` **[rename]** | "\paragraph{The repair.} The fix is to require ..." | "\paragraph{The correction.} We require ..." |
| `sec4_search.tex:300` **[rename]** | "In the counterexample the repair fails at $B=\{2,3,4\}$" | "In the counterexample the hereditary condition fails at $B=\{2,3,4\}$". "The repair fails" reads as "the fix does not work", which is the opposite of what is meant. This is the worst sentence the rename left behind. |
| `sec4_search.tex:302` **[rename]** | "The proof that the repair is sound needs one inequality." | "The proof that the corrected rule is sound needs one inequality." |
| `sec4_search.tex:341` **[rename]** | "\begin{theorem}[the repair is a matching condition]" | "[the corrected premise is a matching condition]". Change it together with `sec9a_appendix_lean.tex:84`. |
| `sec4_search.tex:347`, `:352` **[rename]** | "The sets of the repair are $B=S\cup D$"; "exactly when the repair holds" | "The sets of the hereditary condition are ..."; "exactly when the hereditary condition holds" |
| `sec4_search.tex:333-336` | "this cheap test is the algorithmic contribution of the section; we did not find it in the papers we hold" | Keep, and make it first person: "this cheap test is our algorithmic contribution in this section; we did not find it in the papers we hold". |
| `sec4_search.tex:400` **[rename]** | "\emph{Repair and test.}" | "\emph{Correction and test.}" |
| `sec4_search.tex:435`, `:451` | "Our corrected search is sound" (subsection, theorem) | Keep. These are the right places for "our". |
| `sec4_search.tex:455` | "the better move cite only under the corrected premise" | Keep. |
| `sec4_search.tex:494` | "our corrected search finds it and refutes 5, so the optimum is 6" | Keep. Here "finds" is followed by "and refutes 5", so the claim is complete (compare the abstract, §4.3). |
| `sec4_search.tex:547-548` **[rename]** | "Committing there when the matching fails is a second repair that gives up no pruning; we have not built it." | "... is a second correction, which gives up no pruning; we have not built it." |
| `sec4_search.tex:564-577`, Table 4.2 | "the corrected definite move are known pathwidth results" | Keep as is, without "our" (see the principle above). |

**Lean names that still say "repaired".** `sec9a_appendix_lean.tex:83, 91, 98,
107, 116` print `solvable_cl_insert_of_hereditarilyDefinite` (fine),
`IsRepairedBetter`, `searchSol_cl_insert_of_repairedBetter`,
`exec_repairedFullFilter_sound`, `execSplit_repairedFullFilter_sound` and
`repairedFullFilter_sound`. These sit beside text that now says "corrected",
for example A.98 "our corrected search is sound —
exec_repairedFullFilter_sound". Renaming the Lean declarations would mean a
Lean rebuild plus updates to `check_lean.py` and the axiom check, and is not
worth it before submission. Instead, add one sentence to the appendix's
opening paragraph (`sec9a_appendix_lean.tex:8-14`): "Lean names use
\texttt{repaired} for what the text calls \emph{corrected}." The internal
label `thm:repaired` and the comment in `tables/certificates.tex:1` are
invisible and can stay.

Other uses of "repair" to change, or to keep on purpose:

- `sec9a_appendix_lean.tex:84`: "the repair is a matching condition". Follow
  the theorem title.
- `sec9b_appendix_machinery.tex:178` **[rename]**: "the filter definite $\to$
  subset $\to$ better with both repairs is node-sound" becomes "with both
  corrections".
- `sec2_equivalences.tex:375` ("one published proof has a gap that we
  repair") and `sec9b_appendix_machinery.tex:76`: these concern the
  Kirousis–Papadimitriou proof, not the search. **Keep "repair" there.** It
  usefully keeps the two corrections apart.

**A second ambiguity: two corrected objects.** The paper now has "our
corrected table" (`sec6_conclusion.tex:59`, "Cite the corrected table") and
"our corrected search". At `sec6_conclusion.tex:59-61` they are two sentences
apart. Fix it in one word: "Cite our table as corrected here, Table~\ref{tab:master}, ...".

### 2.4 Section 5 (`sec5_results.tex`)

| file:line | current | proposed |
|---|---|---|
| `sec5_results.tex:12` **[rename]** | "What does the repair cost? Under our corrected rules, the total number ... changes by at most 2\%." | "What does our correction cost? At most 2\% more search nodes over each benchmark set." |
| `sec5_results.tex:14` | "All 115 that rested on the previous algorithm were proved again" | "... rested on the previous algorithm \citep{ChuStuckey2009} were proved again". This is the section's first use, and the first review asked for a citation on first use per section. |
| `sec5_results.tex:17-19` | "Finally, what does it make possible? A dataset of 17,714 graphs ..." | Add a fifth question before it, because the abstract now ends on the solver: "How good a pathwidth solver is it? On every benchmark set with published exact counts it proves more graphs than the published branch and bound." |
| `sec5_results.tex:30-31` | "The corrected tests are the default in every implementation" | "Our corrected tests are the default in every implementation" |
| `sec5_results.tex:79` **[rename]** | "\subsection{The cost of the repair, and the benchmark values}" | "\subsection{The cost of our correction, and the benchmark values}" |
| `sec5_results.tex:89` **[rename]** | caption "The repair never changed an answer and changes the total node count by at most 2\%." | "Our correction never changed an answer and costs at most 2\% more nodes in total." |
| `sec5_results.tex:110-118` | "Graph benchmarks" paragraph | Make this a subsection, "Our corrected search as a pathwidth solver", and add two sentences of evidence that the paper holds but does not print (§3.2): the times on the 14 TreewidthLIB graphs of their Table 4, and the Mycielski graph $M_7$, which they prove and we do not. Proposed text is in §3.6. |
| Table `tab:graphs` (`tables/graphs.tex`) | the TreewidthLIB row says "all 14 held agree" | "14 of 14 agree; faster on all 14" (and a footnote with the ratio range). Optionally add a "Mycielski $M_7$" row: "not proved in 1,500 s" against "proved, 10 min (tuned)". Printing the loss makes the wins credible. |
| `tables/graphs.tex:8` | "Rome & 10--110 & 11,534 & 11,194" | Check against `tables/dataset.tex:19`, which gives Rome 11,199 certified. The difference is presumably by-bound certification or the 3,600 s run (`rome_3600s.csv`), but a referee who reads both tables will ask. One clause in the dataset caption or in §5.4 settles it. |
| `sec5_results.tex:268` | "it rests on our corrected search" | Keep. |

### 2.5 Section 7, data (`sec7_data.tex`)

| file:line | current | proposed |
|---|---|---|
| `sec7_data.tex:24-26` | "Everything this paper reports can be re-run from its repository, \fbox{URL to be added on release}, and most of it can be checked without re-running." | "Our code, proofs and data are open source, under the MIT licence, at \url{...}. Everything this paper reports can be re-run from there, and most of it can be checked without re-running." The repository is already public under MIT (§4.1), so the sentence can lead with that. |
| `sec7_data.tex:35-37` | "the source of both solvers, the open-stacks customer search and the graph pathwidth solver, in C and in Python, with the rules of the previous algorithm and the corrected rules;" | "the source of both our solvers, the open-stacks customer search and the graph pathwidth solver, in C and in Python, with our corrected rules as the default and the rules of the previous algorithm \citep{ChuStuckey2009} as an option;" This is the first use in the section, and the second half is now true by `sec5_results.tex:30-31`. |
| `sec7_data.tex:38-39` | dataset bullet | Add: "the benchmark graphs keep the terms of their original distributions". The dataset redistributes Rome, VSPLIB, TreewidthLIB, PACE and other graphs, and the MIT licence on the repository does not relicense them (§4.1). |
| new bullet | — | "the graph pathwidth solver as a standalone package (\repofile{pathwidth\_solver/}), with the scripts that produced Table~\ref{tab:graphs} and the published values it is compared with (\repofile{pathwidth\_solver/bench/reference.py})". If "ours is the best openly available" is to be claimed, a reader must be able to find and run "ours" without reading a 59,000-file research tree. |

---

## 3. The claim "We believe ours is currently the best pathwidth solver openly available"

### 3.1 What it needs

The sentence makes three claims:

- **(a) "best"**, which is a comparison;
- **(b) "pathwidth solver"**, an unqualified category that includes heuristics
  and solvers for any graph size;
- **(c) "openly available"**, a restriction on what the comparison is
  against.

"We believe" softens the claim but does not exempt it from evidence. A
referee will read it as "the authors claim the best, and believe it". The
body currently supports a weaker phrase: "among the strongest exact
algorithms for pathwidth, on the published evidence"
(`sec3_names.tex:104-106`). **The abstract now claims more than any sentence
in the body.**

### 3.2 What evidence the paper holds

**Printed in the paper** (Table `tab:graphs`, `sec3_names.tex:119-128`,
`sec5_results.tex:110-118`): counts against Coudert, Mazauric & Nisse (2016)
(CMN), taken from their paper, not from runs.

| Set | Ours (600 s) | CMN (10 min) | Strength of the evidence |
|---|---|---|---|
| Rome, 11,534 | 11,194 (97.1%) | 95.6% (their Table 3: 11,027 of 11,529) | **Moderate.** The margin is 1.5 points, about 170 graphs. CMN ran on a "3.20 GHz Xeon" around 2014 (2016 PDF, §4); we ran on a Ryzen 9 9950X with up to 32 concurrent workers (`sec5_results.tex:24-40`). A single-core speed factor of 2–3× between the two machines is plausible, and a 2–3× time budget could close much of a 1.5-point gap, because the unsolved graphs sit near the cap (`sec5_results.tex:115-116`). Note also that CMN solved every graph with at most 82 vertices. |
| VSPLIB trees, 50 | 50 | 30 | **Weak as evidence of a general solver.** Trees have linear-time exact algorithms (Ellis, Sudborough & Turner 1994, held). A referee will say a tree benchmark measures nothing that matters. |
| VSPLIB Harwell–Boeing, 73 | 39 | 26 | **Strongest of the counts.** It is a 50% margin, which no plausible hardware factor explains. |
| VSPLIB grids, 50 | 9 | 9 (sides 5–13) | **A tie.** Neither proves a grid beyond 13×13. |
| TreewidthLIB colouring | 31 of 58; "all 14 held agree" | 14 (their Table 4) | **Not printed as a comparison.** See below. |

**Held but not printed** (`pathwidth_solver/bench/results/repaired/coloring.csv`
against `bench/reference.py`, CMN Table 4):

- *Times on CMN's 14 TreewidthLIB graphs.* Our search is faster on all 14:
  - david: 0.65 s against 99.5 s;
  - miles750: 0.028 s against 51.2 s;
  - mulsol.i.5: 0.11 s against 67.3 s;
  - zeroin.i.1: 0.012 s against 0.94 s;
  - queen10_10: 3.0 s against 25.9 s;
  - queen8_12: 0.62 s against 4.26 s;
  - games120: 99.2 s against 148.4 s;
  - queen7_7 and queen8_8: 1.4× faster.

  So on 6 or 7 of the 14 the margin is 10× to 1,800×, beyond any hardware
  factor. On games120, queen7_7 and queen8_8 the margin is within it. This is
  better evidence than the Rome count and it is not in the paper.
- *Beyond CMN's table.* queen11_11 = 87 in 37 s and queen12_12 = 103 in 391 s
  are proved (CMN report up to queen10_10). fpsol2.i.1 (496 vertices) is
  pw 67 in 5.7 s, against 323 s for Kobayashi, Komuro & Tamaki (2014, Table 6,
  Java at 2.14 GHz; `literature/pathwidth_solvers_README.md`).
- *A loss.* **CMN prove the Mycielski graph $M_7$ (`myciel6`, 95 vertices,
  pw 38) in about 10 minutes** with tuned prefix storage (2016 PDF, Table 1 and
  the text after Table 2). Our search has not proved it in 600 s, nor in
  1,500 s with the better move on, with or without degree fan order (lower
  bound 25, width 38; `bench/results/myciel6_bettermove.log`,
  `repaired/coloring.csv`). `pathwidth_solver/PLAN.md:183` already records
  this as "the only C-engine miss". With the claim "best", a referee who knows
  CMN will find this graph. The paper should print it first.
- *Size limit.* The C engine handles components of at most 1,024 vertices
  (`sec5_results.tex:31-33`). SageMath's BAB has no stated limit. For large
  graphs, heuristics (Duarte et al. 2012, VNS on VSPLIB) are the practical
  tools, so an unqualified "best pathwidth solver" (no "exact") is false on
  large graphs.

### 3.3 Other exact solvers, and whether they are openly available

| Solver | Openly available? | Compared in the paper? | Notes |
|---|---|---|---|
| **CMN branch and bound (BAB)** | **Yes, in SageMath**, `sage.graphs.graph_decompositions.vertex_separation`, `algorithm="BAB"`, implemented by Coudert (2015), GPL. Checked in the SageMath docs on 2026-10-11. | With published numbers only. | CMN's conclusion: "the branch-and-bound algorithm presented in this paper (without the pre-processing phase) is now included in Sagemath and so it can be used by others to perform comparisons on a fair basis." **That sentence invites exactly the experiment the paper has not run**, and a referee from that community will quote it. Note that the published numbers are for BAB-*GPP*, with preprocessing, so Sage's BAB is probably weaker than the published baseline. |
| SageMath "exponential" DP (Cohen 2011) and MILP (Coudert 2012) | Yes, in SageMath. | No. | The DP is limited to fewer than 32 vertices. CMN show both are dominated by their BAB (2016, §4.2). One line in the paper suffices. |
| Kobayashi, Komuro & Tamaki (2014, SEA), commitment DFS | **Not found.** No public code located; the Tamaki group's GitHub (`github.com/twalgor`, repo `tw`) is treewidth only (README: "implementations of treewidth algorithms"). | Cited in Section 4 for its rules, not in Table `tab:graphs`. | **The closest competitor.** CMN (2016, conclusion) say it is "very similar" and better on some TreewidthLIB instances. They solve 145 of the 162 TreewidthLIB graphs with at most 300 vertices in 30 minutes. We hold only the 58-graph colouring subset of TreewidthLIB, so the paper cannot compare on their set. If the code is not public, "openly available" is exactly what separates "ours" from it. That is honest, but the paper should say so. |
| Kitsunai, Kobayashi, Komuro, Tamaki & Tano (2016), O(1.89^n) commitment DP | No public code found. | Cited (Section 4). | Mostly a theoretical bound. |
| Bannach & Berndt (2019/2022), positive-instance-driven graph searching for pathwidth | No pathwidth code found. The arXiv page links none. Their public repositories (Jdrasil, PID-Star) are treewidth and treedepth. | No. | The README notes they report only state-space sizes, no pathwidth running times. |
| Suchan & Villanger (2009); Bodlaender et al. (2012) | Theory; no implementations. | Cited. | Not competitors in practice. |
| SAT/MIP: Biedl et al. (2013), Lodha, Ordyniak & Szeider (2017), Mallach (2018), the 0-1 model of Duarte et al. (2012), Fraire-Huacuja et al. (2016) | Encodings are reproducible from the papers. Biedl et al.: "no implementations are provided" (CMN 2016, §4.2). The others were not checked. | No (Mallach is used only to check the Small graphs, `sec5_results.tex:271-272`). | Published results are far weaker: 17% of Rome for Biedl et al.; about 27 vertices for Lodha et al. One sentence citing CMN's comparison suffices. **Fraire-Huacuja et al. (2016) benchmarked an ILP and a B&B against SageMath and is not held** (`literature/pathwidth_solvers_README.md`, "Still missing"). A referee may know it; obtain it before claiming "best". |
| PACE | Pathwidth has never been a PACE track: 2016 and 2017 were treewidth (with minimum fill-in in 2017), 2020 treedepth (`literature/pathwidth_solvers_README.md`; confirm 2026 by hand). | Their instances are used in the dataset. | PACE treewidth solvers give lower bounds on pathwidth, not pathwidth. There is no "pathwidth champion" to beat, which helps the claim. |

**Summary.** The only openly available exact pathwidth solver of known
strength is CMN's BAB in SageMath. The paper compares against CMN's published
BAB-GPP numbers, a stronger and older baseline, on other hardware. It never
runs the open code.

### 3.4 What a referee would ask

1. "You claim the best openly available solver. CMN put their code in
   SageMath precisely so that comparisons could be made on a fair basis. Why
   did you not run it on your machine?"
2. "Rome 97.1% against 95.6% is a decade of hardware apart. What is your
   result at 200 s, or theirs on your machine?"
3. "The trees are polynomial. Remove them, and what remains is HB 39 against
   26, a tie on grids, and Rome."
4. "CMN prove $M_7$ in ten minutes. Do you?"
5. "How do you compare with Kobayashi, Komuro & Tamaki (2014) on TreewidthLIB,
   which CMN say beats them on some instances?"
6. "Is the solver usable on its own: an input format, a command line,
   documentation?"

### 3.5 The experiment that would settle it

**Head to head against SageMath's `vertex_separation(G, algorithm="BAB")`, on
the same machine, one core each, same cap.** Run it after the active split
run finishes, so that load noise does not affect either side.

- Instances:
  - the 500-graph Rome sample already used in Table `tab:cost`;
  - all 173 VSPLIB graphs (trees, HB, grids);
  - the 58 TreewidthLIB colouring graphs;
  - myciel3–7.
- Cap: 600 s, with the 10/120/600 s staging applied to both, or a single 600 s
  run applied to both.
- Report:
  - graphs proved;
  - a cactus plot (proved graphs against time);
  - per-graph speed ratios on the graphs both prove.
- Cost: at most about 790 graphs × 600 s × 2 solvers ≈ 260 core-hours in the
  worst case, and in practice far less, because most graphs finish in
  seconds. That is a few hours on the 9950X.

If Sage's BAB is beaten on these sets, the sentence becomes defensible as
"best among openly available exact solvers on standard benchmarks". If it
proves $M_7$ and we do not, print that in the same table.

Optionally, write to Tamaki or Kobayashi for the SEA 2014 code. If it is
private, say "no implementation of \citet{KobayashiKomuroTamaki2014} is
public", which makes "openly available" a factual qualifier rather than a
convenient one.

### 3.6 Proposed wording

**Strongest wording the current evidence supports** (published-number
comparison only):

> On every benchmark set for which exact pathwidth counts are published, it
> proves more graphs than the published branch and bound of Coudert, Mazauric
> and Nisse (2016), and on the fourteen graphs whose times they report it is
> faster on every one.

For the abstract, in fewer words:

> ... proves the pathwidth of 11,194 of the 11,534 Rome graphs, more on every
> benchmark set than the best published exact solver.

"Best published exact solver" is defensible: CMN is the reference baseline
that every later exact paper (Mallach 2018, Bannach & Berndt 2022) compares
to. The trees inflate "every set", but the grids tie, so "more on every set"
needs "or as many": write "as many or more on every set".

**A defensible form of the author's sentence**, keeping "we believe" and
"openly available":

> We believe ours is currently the strongest exact pathwidth solver openly
> available.

There are two changes, and both are needed:

- **"exact"** limits the claim to the category that was compared. Without it,
  the claim covers heuristics for large graphs, where it is false at the
  1,024-vertex limit.
- **"strongest"** for "best" is optional. "Best" is acceptable once §3.5 is
  run. Before that, "strongest" reads as "proves the most", which is what the
  counts show, while "best" also suggests "fastest on everything", which
  $M_7$ contradicts.

If the author wants to keep "best" before the SageMath run:

> We believe ours is currently the best exact pathwidth solver openly
> available.

This is defensible only if the body prints the $M_7$ loss and the
"published numbers, other hardware" caveat right next to the comparison.

**Where the evidence should sit:**

- **Section 5 (primary):** a subsection "Our corrected search as a pathwidth
  solver", containing:
  - Table `tab:graphs`;
  - the 14-graph timing line;
  - the $M_7$ row;
  - after §3.5, the SageMath head-to-head;
  - one sentence on Kobayashi–Komuro–Tamaki and code availability.
- **Section 3 (`sec3_names.tex:119-128`):** shrink to two sentences and a
  pointer, as the first review proposed. Change "among the strongest exact
  algorithms for pathwidth" (`:105-106`) to match whatever the abstract says.
- **Introduction, bullet 3 (`sec1_intro.tex:230-233`):** one clause (§2.1).
- **Conclusion, "What a reader can do" (`sec6_conclusion.tex:61-63`):** the
  belief sentence itself (§2.2), with the limit kept at `:84-86`.

Then the abstract's closing sentence repeats a claim the body argues, instead
of introducing one.

---

## 4. Overclaims introduced by the new edits

### 4.1 "are open source"

The phrase is **true in fact, but the paper does not show it.** I checked the
GitHub API on 2026-10-11: `github.com/Alex-Linhares/MOSP_trough_SAT` is
public, licensed MIT (`LICENSE`, "Copyright (c) 2026 Alexandre Linhares"),
and its last push is `cd692902c`, today. It holds:

- the Lean development;
- both solvers;
- the dataset (`paper1/data/dataset/pathwidth_dataset.jsonl.gz` and the
  files beside it);
- the 34-customer instance with its DRAT proof
  (`paper1/data/false_refutation/`).

So the first review's "not yet true" (its item 12) is out of date. What is
still wrong or risky:

- **The paper gives no URL** (`sec7_data.tex:25`, the boxed placeholder). An
  "open source" claim with no address cannot be checked by the reader. Add
  the URL, or say "will be open source on publication".
- **The public repository is the working tree, not the paper's artefact.**
  - It has about 59,000 tracked files.
  - It has a misspelt name ("trough").
  - Its CLAUDE.md, reports and loop logs are not meant for readers.

  IJOC wants its own code-and-data repository with a DOI (`todo.md:35-37`).
  Either point the paper at a curated repository, or at least at a tagged
  release and a subdirectory.
- **Data licensing.** The dataset includes third-party graphs (Rome, VSPLIB,
  TreewidthLIB, PACE, freetdi, Martí et al., the MOSP collections). The MIT
  licence on the repository does not relicense them. "Open source" fits code
  and proofs. For the data, write "openly available".
- **The counterexample is already public.** `todo.md:19-20` still has
  "Decide whether to write to Peter Stuckey (and Geoffrey Chu) before the
  counterexample and the 34-customer wrong optimum become public." The wrong
  optimum, its checker and the paper draft are in a public repository today.
  This is not an error in the paper, but the author should know that this
  decision has already been made by default. If the author still wants to
  write to them before publication, now is the time.

### 4.2 "We re-prove all 115 benchmark optima that rested on the previous algorithm, changing none"

**Supported.** `solver_fix.md:1612-1614`: "All 115 values that rested only on
the customer search are now re-refuted under the repaired rules, all unsat,
with no value changed". The last four were finished on 2026-10-04. The body
says the same at `sec5_results.tex:143-145`. Two small precisions:

- **115 values on 113 distinct graphs.** SP3 and SP4 are each stored twice
  (`solver_fix.md:822-823`). "115 benchmark optima" is fine, since they are
  115 benchmark entries, but the body could say "(113 distinct graphs)" once,
  in Section 5, so that no referee counts them and finds 113.
- **"Re-prove"** means a refutation by our corrected search, whose rules are
  proved in Lean and whose code is tested and certified, not proved
  (`sec4_search.tex:464-475`). For the seven 125-customer values there is no
  certificate (`sec5_results.tex:207-208`). "Re-prove" is acceptable OR usage
  and the body qualifies it. No change is needed in the abstract.
- The new value `Random-125-125-2-3_0` (certified on 9 October) is not one of
  the 115. It is correctly kept apart (`sec5_results.tex:155-163`).

### 4.3 "the previous algorithm reports an optimum of 7, where our corrected search finds the optimum, 6, which a SAT solver confirms with a checked DRAT proof"

Three issues:

- **The configuration has disappeared.**
  - The failing run is our implementation, with the better move off
    (`sec4_search.tex:489-491`).
  - With the better move on, the instance is answered correctly, and Chu
    (2011, §6.3.2) says their implementation's better move subsumes the
    definite move.
  - Chu & Stuckey's own code was not run.

  In the abstract, "the previous algorithm reports" reads as a statement
  about their program. This is the most consequential overclaim in the new
  abstract, because it is a claim about named colleagues' code.
- **"Finds" undersells, and the reference of "which" is loose.** What
  establishes 6 is a witness order (6 is achievable) and a refutation of 5,
  done by our corrected search and, independently, by SAT with a DRAT proof.
  Any heuristic might "find" 6. As written, "which a SAT solver confirms"
  attaches to "the optimum, 6", while the DRAT proof certifies that 5 is
  infeasible.
- **"The previous algorithm" is ambiguous in a first-person abstract** (§1).

Proposed:

> ... on a 34-customer instance our implementation of their search, with one
> rule off, reports an optimum of 7. Our corrected search proves the optimum is
> 6, as does a SAT solver with a DRAT proof checked by drat-trim.

### 4.4 "We believe ours is currently the best pathwidth solver openly available"

See §3: add "exact"; print the $M_7$ loss; run SageMath's BAB, or say
explicitly that the comparison uses published numbers. As it stands, it is
the one sentence in the abstract that the body does not state.

### 4.5 Smaller points

- **The name is defined twice.** `main.tex:108-109` "We show that most of them
  form a \emph{pathwidth complex}" and `:115-117` "We call this cluster the
  \emph{pathwidth complex} because ...". Keep the author's "We call this
  cluster ..." sentence, and make the first one undefined: "We show that most
  of them are, mathematically, one problem: pathwidth, studied independently
  by communities that rarely cite one another." Then "We call this cluster the
  *pathwidth complex*" is the actual naming.
- **A name is not a community.** `:117-119` "Since 2005, the next most active
  name is MOSP. That community produced ...". "That community" has a *name*
  as its antecedent. Write "... is MOSP, and the open-stacks community
  produced, by way of ...". The first review's warning that the census counts
  names, not communities (its item 5), applies to this exact join.
- **"Every relation is machine-checked in Lean"** (`:115`): unchanged and
  covered by the first review. Not repeated.
- **Deleting the 2% clause is not lost hedging.** "At most 2% more nodes" is
  evidence that the correction is cheap, which helps the authors' algorithm.
  The deletion from the abstract is the author's choice. The body should
  keep it, rephrased as a cost (§2.1, §2.4).

---

## 5. A proposed abstract, version 3

The current abstract with minimal edits. Everything not mentioned is the
author's text verbatim. The edits:

- un-define the name in sentence 2;
- name versus community;
- the wrong-optimum sentence, with configuration and proof;
- "their search" for "the previous algorithm";
- "openly available" plus a URL for the release;
- "exact" in the closing sentence, with the comparison that supports it.

> In 2001 and 2002 we listed twelve problems from operations research, VLSI
> design and graph theory, the minimization of open stacks problem (MOSP) among
> them, as equal "plus or minus one", and gave no proofs. We show that most of
> them are, mathematically, one quantity, pathwidth, studied independently by
> communities that rarely cite one another. We correct our table. Eight rows
> are exact, counting pathwidth itself: each equals pathwidth or pathwidth plus
> one. Two lie in bands one and two wide, and two are false as stated. We add
> three members the table missed, among them the maximum wavefront of sparse
> matrix elimination, which brings a fourth discipline, numerical linear
> algebra, into the family. Every relation is machine-checked in Lean. We call
> this cluster the *pathwidth complex* because the literature uses that name
> more than three times as often as the other eleven names together. Since
> 2005, the next most active name is MOSP, and the open-stacks community
> produced, by way of the 2005 Constraint Modelling Challenge, the best exact
> algorithm for MOSP, the customer search of Chu and Stuckey (2009), which is
> also a pathwidth algorithm. We prove in Lean that two of its published
> dominance theorems are false. On a 34-customer instance our implementation of
> their search, with one rule off, reports an optimum of 7; our corrected search
> proves the optimum is 6, as does a SAT solver with a checked DRAT proof. The
> correct rule was already known for pathwidth; we test it with one bipartite
> matching per candidate and prove our corrected search sound. We re-prove all
> 115 benchmark optima that rested on their search, changing none. Ported to
> graphs, our corrected search proves the pathwidth of 11,194 of the 11,534
> Rome graphs, and as many or more graphs than the best published exact solver
> on every benchmark set. The proofs and both solvers are open source, and
> 17,714 benchmark graphs, distinct up to isomorphism, 16,087 of them with a
> certified pathwidth, are openly available with independent checkers. We
> believe ours is currently the best exact pathwidth solver openly available.

This is about 320 words, the same length as the current abstract. If it must
be shorter, cut in this order:

1. "which brings a fourth discipline, numerical linear algebra, into the
   family";
2. "distinct up to isomorphism";
3. the Rome count, keeping "as many or more ... on every benchmark set".

Before submission:

- Once the SageMath head-to-head (§3.5) is done, replace "than the best
  published exact solver" with "than the branch and bound in SageMath, run on
  the same machine". The closing sentence then needs no defence beyond the
  table.
- Until the paper prints the $M_7$ loss next to Table `tab:graphs`, prefer
  "strongest" to "best" in the last sentence.

---

## Summary

**Top changes**

1. Abstract `:122-124`: restore the configuration ("our implementation of
   their search, with one rule off") and replace "finds the optimum, 6" with
   "proves the optimum is 6". Use "their search" for "the previous algorithm",
   which reads as *the authors'* previous algorithm in a first-person abstract.
2. Fix the rename leftovers:
   - "the repair fails at B" (`sec4_search.tex:300`) reads as "the fix does
     not work";
   - Theorem title "the repair is a matching condition" (`:341`);
   - "The repair costs / is cheap / never changed" (`sec4_search.tex:41`,
     `sec5_results.tex:12, 79, 89`, `sec6_conclusion.tex:54`);
   - add one sentence in Appendix A saying that the Lean `repaired*` names
     mean "corrected".

   Do not attach "our" to the corrected definite move, which is Tamaki's
   commitment lemma.
3. "Open source" is in fact true: the GitHub repository is public, under MIT,
   and pushed today. But the paper has no URL. The repository is the working
   tree, not an IJOC artefact. The data needs "openly available", not "open
   source". And the 34-customer counterexample is already public, which
   overtakes the open to-do item about writing to Stuckey.
4. Give the solver its own subsection in Section 5, with the unprinted
   evidence:
   - faster than CMN on all 14 of their Table 4 graphs, 10× to 1,800× on
     about half of them;
   - fpsol2.i.1 in 5.7 s against 323 s for Kobayashi, Komuro & Tamaki;
   - the loss on $M_7$.

   Echo it in intro bullet 3 and in the conclusion.

**Verdict on the solver claim.** As written ("best pathwidth solver openly
available"), it is not yet defensible:

- it lacks "exact";
- it rests only on published numbers from a decade-old machine;
- the only openly available competitor, CMN's BAB in SageMath, was never run,
  although its authors explicitly invited fair comparisons;
- CMN prove $M_7$, which we do not.

"We believe ours is currently the strongest exact pathwidth solver openly
available" is defensible now, provided the body prints the comparison, its
hardware caveat and the $M_7$ loss. A few hours of head-to-head runs against
SageMath's `vertex_separation(algorithm="BAB")` on the same machine would make
"best" defensible too.
