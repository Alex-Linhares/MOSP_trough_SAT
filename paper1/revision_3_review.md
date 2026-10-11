# *The pathwidth complex*: proposals for the third revision

Read 2026-10-11 against `paper1/latex/` at commit `92a2cb5cd` (main.pdf, 49
pages). The two earlier reviews (`abstract_nudge_review.md`,
`abstract_nudge_review_2.md`) are not repeated here. Where a point touches one
of them, the new element is stated. Line numbers are those of the `.tex`
files. Nothing but this file was edited.

---

## 1. Where the paper does not yet follow the author's direction

Each proposal is small and keeps the author's style: first person, ", as",
"combined", ", and we", and "however" where the logic turns.

### 1.1 Abstract (`latex/main.tex`)

| file:line | current | proposed |
|---|---|---|
| main.tex:112 | "Two lie in bands one and two wide" | "Two lie in *bands*: they stay within one or two of pathwidth, but not at a fixed offset" (*band* is used here before it is defined; Section 2 defines it at sec2:17) |
| main.tex:115 | "Every relation is machine-checked in Lean." | "Every relation is machine-checked in the Lean proof assistant." (first mention of Lean) |
| main.tex:116–117 | "We call this cluster the *pathwidth complex*, as the literature uses that name more than three times as often…" | "…as the literature uses the name *pathwidth* more than three times as often…" ("that name" can point to *pathwidth complex*, which has no usage count) |
| main.tex:118–121 | "…the open-stacks community produced, by way of the 2005 Constraint Modelling Challenge, the best exact algorithm for MOSP, the customer search of \citet{ChuStuckey2009}, which is also a pathwidth algorithm." | "…the best exact algorithm for MOSP: the *customer search* of Chu and Stuckey (2009), which branches on the order in which customers' stacks close, and which is also a pathwidth algorithm." (the term is undefined, and "2005" appears twice in one sentence) |
| main.tex:121–122 | "two of its published dominance theorems are false" | "two of its published dominance theorems, rules that discard a branch as no better than another, are false" |
| main.tex:123–124 | "our implementation of their algorithm, with one rule off" | see §4. At least name the rule: "with its better move off". |
| main.tex:125 | "Our corrected rule was also found by Tamaki as a lemma" | "Our corrected definite move, the first of the two, was also found by Tamaki as a lemma" (two theorems are false, so "our corrected rule" does not say which) |
| main.tex:129–132 | "…and of as many or more graphs than the best published exact solver on every benchmark set." | "…and, on every benchmark set with published exact counts, as many graphs or more than the published branch and bound of Coudert, Mazauric and Nisse (2016)." (The body never says "best published exact solver". It qualifies the claim by "with published exact counts" at sec5:16, sec6:63 and sec3:121.) |
| main.tex:132–135 | "We also release a dataset of 17,714 distinct graphs from twenty benchmark collections of the twelve problems…" | "…a dataset of 17,714 graphs, distinct up to isomorphism, from twenty benchmark collections for pathwidth and the problems equal to it, the MOSP instances and the Rome graphs among them…" (Two numbers could be confused here: 11,534 Rome *files* against 17,714 dataset *classes*. "The twelve problems" is also wrong for PACE and the other treewidth collections; see §2.) |

### 1.2 Introduction (`latex/sec1_intro.tex`)

| file:line | current | proposed |
|---|---|---|
| sec1:24–25 | "We showed MOSP to be NP-hard \citep{Linhares2001,LY2002}." | Delete. sec1:153–155 already says it, in the history where it belongs (see §3, move 3). |
| sec1:65–71 | The wavefront is presented as a fourth reading of the matrix, with no sign that it is new. | Add at the end: "This fourth reading is not in our 2002 table, and we add it below." The reader then sees it below the rule of Table 1.1 without surprise. |
| sec1:130 | "\citet{LY2002} collected twelve such problems" | "We collected twelve such problems \citep{LY2002}" (ownership; the intro is otherwise "our table") |
| sec1:140–142 | "We call the problems that are, on every input, pathwidth or pathwidth plus one the *pathwidth complex*" | Keep, but Section 2 gives the same set a second name, the *exact core* (sec2:282). Either say so here ("…the pathwidth complex; Section 2 calls its members the exact core") or use one name throughout. See §2, item C. |
| sec1:142–146 | One sentence: "Pathwidth is the quantity through which every true relation … (Section 2), and it is the name the literature uses, more than three times as often as the other eleven names of the table together (Section 3); a reader who searches … misses most of what is known." | "Pathwidth is the quantity through which every true relation in the table is proved (Section 2). It is also the name the literature uses, more than three times as often as the other eleven names combined (Section 3), so a reader who searches under "open stacks" or "gate matrix layout" misses most of what is known." |
| sec1:152–153 | "The table is ours, and it has a history that explains why that question, which of its equalities are true, is still open." | "The table is ours, and its history explains why no one checked which of its equalities are true." (Plainer. The current wording restates only half of "the question".) |
| sec1:156–158 | "Each came with a reference and nothing else. No row's relation to open stacks was checked, no published proof was restated, and no graph said which problem reduces to which." | "Each came with a reference and nothing else: no row's relation to open stacks was checked, and no published proof was restated." (The graph clause repeats sec1:135.) |
| sec1:167–168 | "the idea on which the exact search of Section 4 branches" | "the idea on which Chu and Stuckey's customer search (Section 4) branches" (this is the first mention of the search in the introduction, so name it) |
| sec1:188–194 | The wavefront is explained a second time ("the frontal method for a sparse symmetric matrix stores, at each step, the wavefront: …") | "From numerical linear algebra, the wavefront of the frontal method, met above, is the problem of the table: the least maximum wavefront is the pathwidth of the matrix's graph plus one, on every nonempty matrix." |
| sec1:195 | "prove all three relations in Lean" | "prove all three relations in the Lean proof assistant" (first use of Lean in the body text; it is otherwise defined only at sec1:250) |
| sec1:198–200 | "For the wavefront the equality itself is ours. It is elementary, the wavefront being narrowness read in another form, but no source we hold states it." | "For the wavefront the equality itself is ours: it is elementary, as the wavefront is narrowness read in another form, but no source we have read states it." |
| sec1:208 | "lie in bands one and two wide" | "lie in *bands*: within one and two of pathwidth, but not at a fixed offset" |
| sec1:213–215 | "…more than three times as many relevant works as the other eleven names together" | "…combined" |
| sec1:219–221 | "The best exact algorithm for MOSP, the customer search of \citet{ChuStuckey2009}, is also a pathwidth algorithm." | "The best exact algorithm for MOSP, the *customer search* of Chu and Stuckey (2009), which we call the previous algorithm, branches on the order in which customers' stacks close, and it is also a pathwidth algorithm." This defines "the previous algorithm" before sec1:236 uses it. Today the introduction uses it with no antecedent. |
| sec1:221–223 | "two of its published dominance theorems are false … each can discard the last solution at a node" | "two of its published dominance theorems, the *definite move* and the *better move*, are false … each can discard the last remaining solution at a node of the search tree" (names both rules, which the next sentences need, and explains "node") |
| sec1:224–226 | "their algorithm obtains an optimum of 7, while our corrected version obtains 6, provable also by a SAT solver" | Keep the author's sentence, and add the configuration (see §4): "our implementation of their algorithm, with its better move off, obtains an optimum of 7, while our corrected version obtains 6, provable also by a SAT (Boolean satisfiability) solver". |
| sec1:226 | "Our corrected rule was also found by Tamaki" | "Our corrected definite move was also found by Tamaki" (the author's own phrase) |
| sec1:228–229 | "It costs at most 2% more search nodes over each benchmark set." | "Our correction costs at most 2% more search nodes on each benchmark set we measured." ("It" could be the matching or the search.) |
| sec1:229–230 | "Ported to graphs, it is an exact pathwidth solver" | "Ported to graphs, our corrected search is an exact pathwidth solver" |
| sec1:231–232 | "the 11,534 Rome graphs … all 50 VSPLIB trees and 39 of the 73 Harwell–Boeing graphs" | "…of the 11,534 Rome graphs, a graph-drawing benchmark of 10 to 110 vertices, within 600 seconds each; all 50 trees of VSPLIB, a benchmark library for vertex separation; and 39 of its 73 Harwell–Boeing graphs, the sparsity patterns of engineering matrices" (all three are undefined at first use; the reader's note asked "What are Rome graphs?") |
| sec1:236–237 | "re-proved all 115 benchmark optima that rested on the previous algorithm, and none changed" | "…all 115 benchmark optima, on 113 distinct graphs, that rested on the previous algorithm, and none changed" (sec5:127 gives the 113 only in Section 5) |
| sec1:237–239 | "We release 17,714 graphs, distinct up to isomorphism, from twenty benchmark collections of the twelve problems" | "…from twenty benchmark collections, of MOSP, VLSI layout, vertex separation, graph drawing and treewidth" (see §2, item C) |
| sec1:248–249 | "answers the question this paper asks: which equalities of the table are true, and what follows from them" | "returns to the question this paper asks" (the paraphrase differs from sec1:147–150 and sec6:10–12) |
| sec1:250 | "Every theorem we state is machine-checked in the Lean 4 proof assistant." | "Every theorem we state is machine-checked in the Lean 4 proof assistant, unless the text says otherwise." (Matches sec2:26 and app A:8–9. LaPaugh's es = pes is stated and not proved, sec2:343.) |
| sec1:253–258 | Two `\pageref{sec:data}` in three lines | "…and Appendix C the bibliometric method. The Lean development, both solvers, the dataset and an independent checker for each are openly available, the code and proofs as open source under the MIT licence (page N)." |

### 1.3 Section 2 (`sec2_equivalences.tex`)

| file:line | current | proposed |
|---|---|---|
| sec2:282–285 | "the *exact core*: the eight exact rows, with multiple folding and the vertex separator game, and the three members outside the table" (thirteen problems) | Keep, and state the count once: "thirteen problems, or twelve if multiple folding is counted with gate matrix layout, which it equals". See §2, item C. |
| sec2:374–375 | "one published proof has a gap that we repair" | "…a gap that we correct" (the direction is "never repaired") |
| sec2:391 | "Kashiwabara and Fujisawa (1979), is not held" | "…is one we could not obtain" ("held" is project jargon; also at sec6:84, sec1:200, sec4:215, 570, 603 "papers we hold" → "papers we have read") |
| sec2:13 | "the first half of our question" | Good. The second half is never marked as such: see §3, move 5. |

### 1.4 Section 3 (`sec3_names.tex`)

| file:line | current | proposed |
|---|---|---|
| sec3:28 | "So we read the 2,271 hits and kept the 1,593…" | "So we checked the 2,271 hits…" (sec3:30 says that the 1,571 pathwidth hits were filtered by a rule, not read) |
| sec3:43–44, 54 | "together" (twice) | "combined" |
| sec3:104–106 | "…is also, on the published evidence, among the strongest exact algorithms for pathwidth" | "…on our measurements (Section 5)…" (the evidence is our port, not a published result) |
| sec3:119–122 | "The customer search reads an instance only through its MOSP graph …, so it decides pathwidth. Ported to graphs, it proves more instances than reported…" | "…Ported to graphs, our corrected version of it proves more instances than reported…" ("it" is Chu and Stuckey's search, but the numbers are ours) |
| sec3:125–126 | "VSPLIB trees … Harwell–Boeing graphs" | Defined once in the introduction (above). If not, define them here. |
| sec3:132–134 | "It finds that the search's first dominance rule is, in correct form, a theorem already known in the pathwidth literature, and that two of its published theorems are false." | "It finds that two of the search's published dominance theorems are false, and that the first, the definite move, is in its corrected form a lemma already known in the pathwidth literature." (falsity first; "first dominance rule" is unnamed) |

### 1.5 Section 4 (`sec4_search.tex`)

| file:line | current | proposed |
|---|---|---|
| sec4:29 | "The error is hard to make bite" | "The error rarely shows" |
| sec4:29–33 | "…on every benchmark the previous algorithm, the search as \citet{ChuStuckey2009} publish it, answers correctly, and the first whole instance on which it reports a wrong optimum has 34 customers and needs the old move to pass a false refutation on to later branches" | "…answers correctly, and the only whole instance we found on which our implementation of it reports a wrong optimum, with the better move off, has 34 customers. There the *old move*, a rule that lets a failed sibling prune later branches, passes a false refutation on." ("First" implies a sequence. "Old move" is used here and defined only at sec4:190. The configuration is missing, see §4.) |
| sec4:33–35 | "And when we proved every benchmark optimum that rested on the search again with our corrected rules, no value changed" | "And when our corrected search re-proved every benchmark optimum that rested on the previous algorithm, no value changed" |
| sec4:201–203 | "discards a move r by citing a *covering*, a kept move c with …" | "…by citing a *covering*, or *link*, from r to a kept move c with …" ("link" is used at sec4:395, 412 and 444 without definition) |
| sec4:428–431 | "one implementation of the search declines to run both for that reason" | Name it, as the paper names everything else (Chu 2011? another code?). As it stands, "one implementation" is a vague reference. |
| sec4:490–494 | One 5-line sentence: "On the resulting 34-customer instance (Figure 4.3), our implementation of the previous algorithm, with its definite move, the subset rule and the old move and with the better move off, answers that 6 stacks do not suffice, and it answers yes at 7, so it reports an optimum of 7, with a refutation as its proof" | "On the resulting 34-customer instance (Figure 4.3), we ran our implementation of the previous algorithm with its definite move, the subset rule and the old move, and with the better move off. It answers that 6 stacks do not suffice and that 7 do, so it reports an optimum of 7, with a refutation as its proof." |
| sec4:494–495 | "Yet the layout of Figure 4.3(b) uses 6 tracks" | "Yet the order of Figure 4.3(b) keeps at most 6 stacks open (6 tracks, in the figure's gate matrix reading)" (the paragraph is in stacks, and switches to tracks without saying so) |
| sec4:499 | "with a DRAT proof that the independent checker drat-trim verifies" | "…with a proof in DRAT, the standard proof format of SAT solvers, which the independent checker drat-trim verifies" (first use of DRAT in the body; it is defined at sec5:120, later) |
| sec4:506 | "(\repofile{paper1/data/false_refutation/}, Section~\ref{sec:data})" | **Prints "Section 6", the Conclusion**: the data statement is a `\section*` and inherits the counter (main.aux: `sec:data}{{6}`). Use "page~\pageref{sec:data}" as the introduction does. |
| sec4:511–512 | "A 34-customer instance, whose 34 nets must be laid out on 61 gates." | "A 34-customer instance with 61 patterns, drawn as a gate matrix layout of 34 nets on 61 gates." |
| sec4:600–601 | "in the 56 works we read in full of the 141 that cite the customer search's papers" | Fine; App B.6 agrees (24 + 32 = 56). |

### 1.6 Section 5 (`sec5_results.tex`)

| file:line | current | proposed |
|---|---|---|
| sec5:16–17 | "it proves as many or more graphs than the published branch and bound" | add "of \citet{CoudertMazauricNisse2016}" (first mention in the section) |
| sec5:43 | "report time only in core-hours" | "report time only in *core-hours*, the hours of one core summed over workers (32 workers for one hour make 32 core-hours)" (used throughout, never defined) |
| sec5:53–55 | "This is the setting under which the customer search certified the benchmark values it proved." | "This is the setting under which our implementation of the previous algorithm certified the benchmark values it proved." (ownership, and it says which search) |
| sec5:62 | "the 24 industrial SCOOP instances" | "the 24 industrial instances of the SCOOP project" plus one clause on what SCOOP was, or a citation |
| sec5:64–65 | "the generator's density class" | "the generator's density class (roughly, the number of customers per pattern)" (density classes 2 and 4 return at sec5:130) |
| sec5:65–66 | "The graph benchmarks are those of Section 3 and Table 5.4." | "The graph benchmarks are those of Table 5.4." (Section 3 names only Rome, VSPLIB trees and Harwell–Boeing) |
| sec5:108–109 | "The cost per node is also small: about 2% in the C implementation" | "The time per node also rises, by about 2% in the C implementation, measured…" (a second "2%" in the paragraph that states the 2% node bound; a reader will merge the two) |
| sec5:113–114 | "No published optimum changed under our corrected rules." | "None of the 115 values changed under our corrected rules." (some of the 115 are our own certified values, not published optima) |
| sec5:144–145 | "it has refuted 7,217 subtrees so far, using about 1,150 core-hours" | **Stale.** Table B.1 (tables/split.tex, read 2026-10-11 19:59) has 15,604 tasks and 2,120.8 core-hours. Regenerate the sentence from the same read, or write "(Table B.1)" and drop the numbers. |
| sec5:151–152 | "on the 11,915 graph benchmarks it was run on" | "on the 11,915 benchmark graphs it was run on, counted as files" (this sits next to 11,534 Rome graphs and 17,714 dataset classes) |
| sec5:158 | "On the fourteen colouring graphs" | "On the fourteen graph-colouring benchmarks of TreewidthLIB" |
| sec5:172–173 | "the comparison that would settle the question" | "the comparison that would settle which solver is stronger" (names the question) |
| sec5:239 | "…and the maximum wavefront take w+1: twelve problems in all." | See §2, item C (thirteen in sec2:282–285). |
| sec5:258 | "Harwell-Boeing" (hyphen, also in tables/dataset.tex) | "Harwell–Boeing" (en dash, as in sec1:232, sec3:126, tables/graphs.tex) |
| sec5:274–277 | "the VSPLIB sets \citep{Duarte2012} and the Small graphs … and treewidth collections used as pathwidth benchmarks \citep{TreewidthLIB,freetdi,PACE2016,PACE2017}" | Say what each is, one clause each: "the Small graphs, a bandwidth benchmark \citep{MartiCamposPinana2008}; TreewidthLIB, a library of treewidth benchmarks, of which we use the graph-colouring set; the freetdi named graphs and the control-flow graphs of compiled programs; and the instances of the PACE 2016 and 2017 challenges in parameterized algorithms, treewidth track". |
| sec5:278–279 | "Of the 17,714 classes, 16,087 carry a certified pathwidth with a witness layout and 862 a witnessed upper bound." | Add "and 765 have no witnessed value yet" (Table 5.4 bottom row), so that the three numbers sum to 17,714 and sec5:288's 16,949 can be read. |
| sec5:285–288 | "It re-reads all 20,987 member files … It reports no failure on the 16,949 records." | Say why 20,987 and not 21,754 files, and that 16,949 = 16,087 + 862, the records with a witness. Neither number is explained. |

### 1.7 Conclusion and data statement (`sec6_conclusion.tex`, `sec7_data.tex`)

| file:line | current | proposed |
|---|---|---|
| sec6:22–26 | "And one certified pathwidth answers every problem in the exact core at once, which is what made a single dataset for twelve problems possible, three of them problems the table did not list, one from a fourth discipline, numerical linear algebra." | "And one certified pathwidth answers every problem of the exact core at once, which made a single dataset for all of them possible, including the three the table did not list." ("twelve problems" here is not the twelve of sec6:11; the fourth discipline was already said at sec6:25–26 and in the abstract) |
| sec6:50 | "Three things in this paper bear on that." | "Three findings of this paper bear on the soundness of dominance rules." ("that" has two candidate antecedents) |
| sec6:51 | "the commitment lemma" | Fine. Defined in Section 4.6. |
| sec6:56–57 | "at most 2% more nodes per benchmark set" | "at most 2% more nodes in each row of Table 5.1" (the graph row of tables/cost.tex mixes four sets) |
| sec6:84 | "is not held" | "is one we could not obtain" |
| sec6:98–102 | "As of 9 October 2026 the split search is still refuting…" | Date it to the same read as Table B.1 (11 October), or write "at the time of writing (Table B.1)". |
| sec6:102 | "Of the 17,714 classes of the dataset, 1,627 have no certified pathwidth." | Possibly stale by one: see §2, item A. |
| sec7:31–32 | "The largest refutations can only be re-run, at up to 1,128 core-hours each" | "…at up to 1,128 core-hours for the largest finished one, and more for the one in flight" (Table B.1 has 2,120.8 core-hours on Random-125-125-2-2_0 so far) |
| sec7:33 | "one corpus value is still open (Section~\ref{sec:closing})" | "(Section 5.2)": that is where the open value is described |
| sec7:47–48 | "with the optimum the previous algorithm reports and its order" | "with the optimum our implementation of the previous algorithm reports with the better move off, and its order" (see §4) |

### 1.8 Appendices

| file:line | current | proposed |
|---|---|---|
| sec9b:75–76 | "The repair orders the vertices by clearing time" | "The correction orders…" |
| sec9b:214 | Table B.1 caption: "(read 9 October 2026)" | tables/split.tex says "read 2026-10-11 19:59". Make the caption match, or have make_tables write the date into the caption. |
| main.tex:98 | "Draft, 6 October 2026" | The content is as of 9–11 October. Update the date. |

---

## 2. Consistency checks

Checked and consistent (no action): **11,194 / 11,534** (abstract, sec1:231,
sec3:123, tables/graphs.tex; 97.1% = 11,194/11,534); 24 corrected-only minus 13
previous-only = 11,194 − 11,183; graph table totals (11,915; 11,448; 11,437);
**eight rows exact** (main:110, sec1:76, 204; sec2:20, 149, 379; sec3:13;
sec6:12), and the seven named at sec2:381–383; **bands one and two wide**
(main:112, sec1:208, sec2:384, sec6:14–15); **three new members** (main:113,
sec1:141, 178, sec2:285, sec6:24); 844 citing works and six that cite both
(sec1:174, sec3:89, 96, communities table); 1,213, 380, "21 times" and "three
times" (sec3:53–54; 1,213/58 = 20.9, 1,213/380 = 3.19); 51 / 32 / 28 (sec3:77,
periods table); 6,275 / 6,286 and 35.5 MB (sec5:221, certificates table); the
seven split values, 18 to 369 core-hours and 1,112.6 in total (sec5:134, Table
B.1, which sums to 1,112.6); 6,259 + 115 = 6,374 (sec5:114–125); MOSP corpus
5,806 + 46 + 200 + 300 + 24 = 6,376; Rome's 327 open classes = 326 + 1;
1,627 = 17,714 − 16,087; 154 classes above 1,024 vertices (sec5:35, sec6:107);
the Figure 1.1 counts (2 orders reach 3, 16 give 4, 6 give 5; re-verified by
enumeration); the worked costs 2, 3, 3, 2 at sec4:92.

Inconsistencies, with fixes:

**A. The dataset is one certification behind the corpus.** sec5:78–80 says
6,375 of 6,376 corpus values are certified, Random-125-125-2-3_0 having been
certified on 9 October. Table 5.4 (tables/dataset.tex) still lists *MOSP: Chu &
Stuckey* as 198 certified and 2 upper bound only. The dataset's
`values.csv.gz` (built 9 Oct 21:14) still has Random-125-125-2-3_0 at
`solution`, although `solutions/Random-125-125-2-3_0.json` (written 21:13) is
`certified:refutation`. If the class is not shared with another file, the
headline numbers become **16,088** certified and **1,626** open, in the
abstract (main:134), sec1:239, sec5:21, 278, sec5:256 caption, sec6:102, and
the Chu & Stuckey row becomes 199 / 1. Fix: rebuild the dataset index after the
split result, then regenerate the tables. If the rebuild has to wait, state the
dataset's date in the Table 5.4 caption.

**B. The split run in flight: text and table disagree.** sec5:144–145 says
7,217 subtrees and about 1,150 core-hours. Table B.1 says 15,604 tasks and
2,120.8. sec6:99 says "as of 9 October", the Table B.1 caption says "read 9
October 2026" and tables/split.tex says it was read 2026-10-11. sec7:31–32 says
"up to 1,128 core-hours each". Fix: one read date everywhere, and the numbers
in the text taken from that read (or referred to the table).

**C. "Twelve problems" means three different sets.**
- The table's twelve rows: main:105, sec1:130, sec3:14, sec6:11.
- The dataset's "twelve problems": main:133 ("twenty benchmark collections of
  the twelve problems"), sec1:238, sec6:24 ("a single dataset for twelve
  problems possible, three of them problems the table did not list") and
  sec5:239 ("twelve problems in all": three at w, nine at w + 1, with multiple
  folding absorbed into gate matrix layout).
- The exact core defined at sec2:282–285: eight rows + multiple folding + VSG +
  three members = **thirteen**.

A reader who meets "the twelve problems" in the abstract's dataset sentence
will read it as the table's twelve, which include the two false rows and the
two bands. Fix: reserve "twelve" for the table. Say "every problem of the
exact core" for the dataset (main:133, sec1:238, sec6:24), and at sec5:239
write "twelve problems in all, counting multiple folding with gate matrix
layout". Also name the PACE, TreewidthLIB and freetdi collections honestly:
they are treewidth collections used as pathwidth benchmarks (sec5:277), not
benchmarks "of the twelve problems".

**D. Two names for one set: *pathwidth complex* and *exact core*.** At
sec1:140–142 the pathwidth complex is "the problems that are, on every input,
pathwidth or pathwidth plus one". At sec2:282 that same set is the *exact
core*. At sec6:16–18 "the family is a pathwidth complex: its exact members are
one quantity", which makes the complex the whole family, bands included. The
abstract (main:116) has "this cluster". Fix (the author decides): either the
complex is the exact core (then say so at sec2:282 and reword sec6:16–18), or
the complex is the whole family and the exact core is its centre (then reword
sec1:140–142).

**E. 115 / 113.** The abstract (main:127), sec1:236, sec5:14, sec5:125–128 and
sec6:57 all say 115, and only sec5:127–128 explains "115 entries on 113
distinct graphs". Fix: add "on 113 distinct graphs" once in the introduction
(sec1:236). Optimum is per graph, and a reader who counts graphs will
otherwise find 113.

**F. "2%" is two different measurements.** The node bound "at most 2% more
nodes" appears at sec1:229, sec4:43, sec5:12, sec5:92 (caption), 107 and
sec6:56. A time-per-node "about 2%" is at sec5:108. The node bound is also
stated in four forms: "over each benchmark set" (sec1:229, sec5:12), "on each
benchmark set" (sec4:43), "in total" (Table 5.1 caption), and "per benchmark
set" (sec6:56). The table's rows are not benchmark sets (the graph row merges
VSPLIB, colouring, named and 500 Rome). Fix: one form, "at most 2% more nodes
in each row of Table 5.1", or "on each group of benchmarks we measured". Call
the second number "time per node".

**G. Cross-reference that prints the wrong section.** sec4:506
`Section~\ref{sec:data}` prints "Section 6", the Conclusion (see 1.5).
sec7:33 points to the Conclusion for the open value when Section 5.2 describes
it. All other `\ref`s point where they say: checked against main.aux, and the
log has no undefined references.

**H. Captions against text.**
- Table 1.1 caption (sec1:75–84) and Table 2.2 caption (sec2:149–156) agree
  with the text.
- Figure 4.3 caption (sec4:511–518) carries the configuration ("our
  implementation, better move off"), as does sec4:490–492. The
  introduction (sec1:224) and the data statement (sec7:47–48) do not; see §4.
- Table 5.1 caption: "Our correction never changed an answer and costs at
  most 2% more nodes in total". This is true per row, but "in total" is a
  third wording (item F).
- Table B.1 caption date (item B).
- The Table 5.4 caption (sec5:258) and tables/dataset.tex spell
  "Harwell-Boeing" with a hyphen. Everywhere else it has an en dash.

**I. "Strongest exact pathwidth solver openly available"** (main:135–136,
sec6:65–66) against sec5:171: "Their branch and bound is openly available in
SageMath" and beats ours on M7. The two statements sit uneasily together. The
second review (§3) and todo.md already cover the experiment; this is listed
here only as a consistency point, for §4's companion decision.

**J. "Every theorem … is machine-checked"** (sec1:250) against "unless the
text says otherwise" (sec2:26, App A:8–9) and the stated, unproved es = pes
(sec2:343, sec6:82). Fix as in 1.2.

---

## 3. The introduction's story, as one reading

Paragraph by paragraph:

1. sec1:12–25 introduces MOSP by an example. Clear. It ends on an orphan
   sentence (NP-hardness) that belongs to the history.
2. sec1:41–51 shows that gate matrix layout computes the same number. Clear.
3. sec1:53–63 introduces the graph and pathwidth. Clear. This paragraph is the
   heart of the paper.
4. sec1:65–71 introduces the wavefront. Clear, but it does not say that this
   reading is *new*. The reader learns that only from the table's bottom rows
   and from paragraph 7, which explains the wavefront a second time.
5. sec1:130–150 makes four points at once: the table, the two readings of
   "plus or minus one", the definition of the complex together with the name
   count, and **the question**. The question arrives before the reader knows
   why it matters.
6. sec1:152–176 gives the history and why it matters ("every result
   transfers"), then the communities that never checked. The stakes come here,
   *after* the question.
7. sec1:178–200 adds the three more members. Clear, but it repeats the
   wavefront.
8. "What we find": four bullets. The third is the longest paragraph in the
   introduction and carries three results: the false theorems, Tamaki and the
   matching test, and the solver.
9. "How to read": restates the question in a third wording.

"The question this paper asks" is stated once, clearly, at sec1:147–150, and
repeated verbatim at sec6:10–12. Three places drift from it. sec1:152 restates
half of it ("that question, which of its equalities are true"). sec1:248
paraphrases it ("what follows from them"). sec2:13 claims its "first half", but
no section claims the second half.

Five proposed moves:

1. **Put the question after the stakes.** Move sec1:147–150 ("This paper asks:
   …") to the end of the history paragraph, after "If it is true, *every
   result* … transfers to *all* the others" (sec1:170). Paragraph 5 then ends
   on the definition of the complex and the name count. Paragraph 6 ends:
   history → used to justify algorithms → stakes → the communities never
   checked → **the question**.
2. **Gather the communities.** Move sec1:173–176 ("The communities that could
   have checked the table rarely read each other: of 844 works …") so that it
   follows the name-count sentence at sec1:146. Both are about names and
   communities, and they lead into Section 3. The history paragraph keeps
   "Looking back, the table was the thesis's most important finding…".
3. **Remove the duplicate NP-hardness.** Delete sec1:24–25. sec1:153–155
   already says that the thesis proved MOSP NP-hard.
4. **Say once that the wavefront is new, and explain it once.** Add the
   flagging clause at the end of sec1:71, and cut sec1:188–194 to a
   back-reference (see 1.2).
5. **Mark the second half of the question.** Add one sentence at the start of
   Section 3 (sec3:13–14), or of Section 4 if Section 3 is read as context:
   "The second half of our question, what follows when results, algorithms
   and benchmarks are moved between the problems through pathwidth, is the
   subject of Sections 3 to 5." Then make sec1:248 "returns to the question"
   rather than paraphrasing it.

Optionally, split the third "What we find" bullet in two: "*Two false theorems,
and our correction*" (the first three sentences, Tamaki, the matching test, 2%)
and "*A pathwidth solver*" (the port and the benchmark counts).

---

## 4. For the author to decide: the configuration of the wrong optimum

**Section 4 still carries the precision. The introduction no longer does, and
the abstract carries it only obliquely.** The body is exact at sec4:490–492:
our implementation, with the definite move, the subset rule and the old move,
and with the better move off. sec4:501–504 adds that with the better move on
(or the old move off) the previous algorithm answers this instance correctly,
and that whether it can fail in that configuration is open. The Figure 4.3
caption (sec4:513) and the Conclusion (sec6:47–48) say the same. Two body
sentences undercut it, however:
- sec4:29–33 defines the previous algorithm as "the search as Chu and Stuckey
  publish it" and then speaks of "the first whole instance on which it reports
  a wrong optimum".
- The data statement (sec7:47–48) says "the optimum the previous algorithm
  reports".

There is also a fact the paper does not yet cite, and a referee from that
group will raise it. Chu and Stuckey write, on p. 6 of the preprint the paper
cites (`literature/chu_stuckey_2009.pdf`, §3.2): "Our implementation of 'better
move' subsumes 'definite move' so we will simply consider them as one
improvement". Their experiments switch "better move" on or off as a unit
(their §4, p. 9). The failing configuration, with the definite move on and the
better move off, is therefore one that their paper neither runs nor describes,
and with their published configuration ("better move", "old move" and nogood
recording on) this instance is answered correctly. The paper cites the same
point from Chu (2011, §6.3.2) only in `false_refutation.md`, not in the text.

Recommendations:
- The **abstract** is safe in substance ("our implementation of their
  algorithm, with one rule off") but vague. "With its better move off" names
  the rule at no cost.
- The **introduction is not safe**. "Their algorithm obtains an optimum of 7"
  (sec1:224) states, about named colleagues' algorithm, a result that sec4:502
  says their published configuration does not produce. Keep the author's
  sentence and insert the configuration: "our implementation of their
  algorithm, with its better move off, obtains an optimum of 7, while our
  corrected version obtains 6, provable also by a SAT solver".
- In **Section 4**, add one sentence after sec4:504 quoting Chu and Stuckey
  p. 6. The paper should say itself that the failing configuration separates
  two rules that they implement as one, and that their published configuration
  is correct on this instance. The point does not weaken the result. The
  theorems are false in Lean whatever the configuration, and the instance
  shows that a false theorem can produce a wrong optimum. It forestalls the
  obvious reply.
- Fix sec4:29–33 and sec7:47–48 as in 1.5 and 1.7.

---

## Summary: the ten highest-value changes, in order

1. Put the configuration into the introduction's wrong-optimum sentence
   (sec1:224), quote Chu and Stuckey p. 6 ("better move subsumes definite
   move") after sec4:504, and fix sec4:29–33 and sec7:47–48 (§4).
2. Rebuild the dataset after the 9 October certification. Table 5.4 still has
   Random-125-125-2-3_0 as upper bound only, so 16,087 / 1,627 are probably
   16,088 / 1,626 in the abstract, introduction, Section 5 and Conclusion
   (§2.A).
3. Bring the in-flight split numbers into agreement: sec5:144 (7,217, 1,150
   core-hours) against Table B.1 (15,604, 2,120.8); one read date everywhere;
   sec7:31–32 "up to 1,128 core-hours" (§2.B).
4. Reserve "twelve" for the table's rows, and fix the dataset's "twelve
   problems" at main:133, sec1:238, sec5:239 and sec6:24 against the thirteen
   of sec2:282–285 (§2.C).
5. Define the benchmarks at first use: Rome, VSPLIB, Harwell–Boeing in the
   introduction (sec1:231–232); TreewidthLIB, freetdi, PACE, SCOOP and the
   density class in Section 5 (sec5:62–65, 274–277).
6. Define the search vocabulary at first use: the customer search and the
   previous algorithm (sec1:219–221, main:120), the definite move and better
   move (sec1:221), old move (sec4:32), link (sec4:202), DRAT (sec4:499),
   core-hours (sec5:43), band (main:112, sec1:208).
7. Fix the abstract's ambiguous antecedents: "that name" (main:116), "our
   corrected rule" (main:125), and "best published exact solver on every
   benchmark set" (main:130–132).
8. Move the introduction's question after its stakes, gather the communities
   sentences, and flag the wavefront as new once (§3, moves 1, 2, 4).
9. Separate the two 2% figures and give the node bound one wording (§2.F,
   sec5:108).
10. Fix sec4:506 (`\ref{sec:data}` prints "Section 6"), unify one name for the
    exact problems (pathwidth complex or exact core, §2.D), and replace
    "together" with "combined" and "repair" with "correct" (sec1:145, 215;
    sec3:43, 54; sec2:375; sec9b:76).
