# Referee report: readability and argument structure

**Manuscript:** "The pathwidth complex: twelve problems, one width, and a solver proved sound" (Linhares and Yanasse), draft of 3 October 2026, 26 pages.
**Venue:** INFORMS Journal on Computing.
**Scope of this report:** readability, argument structure, figures and audience. I did not check the mathematics or the numbers.

Location keys used below:
- `s1:38` means `sec1_intro.tex`, line 38. Likewise `s2` (`sec2_names.tex`), `s3` (`sec3_equivalences.tex`), `s4` (`sec4_search.tex`), `s5` (`sec5_closing.tex`), `main` (`main.tex`).
- "p. 9" is a page of the built `main.pdf`.

---

## 0. Overall assessment

The paper has three strong results:

1. A settled version of a table that has been cited as an equivalence for twenty years.
2. A false published dominance theorem in the best exact MOSP algorithm, with a counterexample, a cheap repair and a proof that the repair is sound.
3. A large certified dataset.

Each result is clearly written at the level of the paragraph. The problem is at the level of the paper. Three things make it hard to follow.

- **It never says which question it is answering.** The reader meets a history (Section 1), then a bibliometric study of names (Section 2), then a catalogue of proofs (Section 3), then a ten-page audit of one algorithm (Section 4), which also contains, as its last subsection, a dataset. The only sentences that tie these together are the last paragraph of Section 2 (`s2:174–180`, p. 5). By then the reader has read five pages without knowing why.
- **It is written for someone who already knows the project.** There are 53 footnotes with Lean identifiers, several file paths and `python -m` commands, configuration names (`csearch`, `default`), "our MOSP corpus", "the C engine", and dates such as "Since 1 October 2026". There is also internal history, such as "The check changed the counts and two of the conclusions" (`s2:45`), which refers to a version of the study the reader never saw.
- **The main object is never shown.** No figure or example shows an open-stacks instance, a gate matrix, or a path decomposition. The formal definition of MOSP first appears on p. 9 (`s3:42`). An IJOC reader who does not already know MOSP has nothing to hold on to for the first eight pages.

All three can be fixed without new results. The authors' proposed opening (a worked example, then the table) is the right idea. Section 7 of this report makes it precise.

---

## 1. Summary in three sentences, as a reader would reconstruct it

> Linhares and Yanasse (2002) listed twelve problems from operations research, VLSI design and graph theory as equal "up to one" to the minimum number of open stacks, without proofs. This paper states each problem precisely and proves, in Lean, that eight of them (counting pathwidth itself) are exactly pathwidth or pathwidth plus one, that two lie in bands of width one and two, and that two are false as stated; a citation census shows the literature has settled on the name "pathwidth" and that the three communities rarely cite each other. Reading the best exact MOSP algorithm (Chu and Stuckey 2009) as a pathwidth search exposes two false published dominance theorems; the paper gives the correct rule (Tamaki's commitment lemma, tested by one bipartite matching), proves the repaired search sound, re-certifies the affected benchmark values with none changed, and releases a dataset of 17,714 graph classes with certified pathwidth.

**Where reconstruction failed or nearly failed:**

1. **The link between the two halves.** Why does a paper that settles a table of equivalences then spend ten pages on one MOSP algorithm? I found the answer only in `s2:174–178`: "a result on any of the twelve problems should be stated, and searched for, as a result on pathwidth; Section 4 does this ...". That sentence is the hinge of the whole paper, and it is buried at the end of the bibliometric section.
2. **The counts.** I needed three passes to settle "eight exact rows".
   - The abstract (`main:92`) says "seven of the twelve, and two variants".
   - The introduction (`s1:55–57`) says "one is pathwidth itself, seven are exactly pathwidth plus a constant".
   - The Section 3 summary (`s3:292–295`) lists seven "with pathwidth itself as the reference".
   - Section 4.7 (`s4:532–535`) lists nine members of the "exact core".

   A reader adding up to twelve will not land on the same number twice.
3. **What the dataset is for.** It appears as Section 4.7, inside a section about the soundness of a search. Its purpose ("one certified width answers every problem in the exact core") is stated only at `s4:531`.
4. **Whether the error matters in practice.** The reader learns that no wrong whole-instance answer is known (`s4:332–333`, p. 18) and that no corpus value changed (`s4:482`, p. 21) only after eight pages on the error. These facts set the stakes and belong at the start of Section 4 and in the introduction.

---

## 2. The central question

**Is it stated?** Not as a question. The nearest candidates are:

- `s1:41–44`, p. 1: "This article does what the thesis did not: it states each problem precisely, proves what is true and refutes what is not, and then takes the strongest exact algorithm in the family through the same check." This states a programme, not a question. "Through the same check" is vague: an algorithm is not checked the way an equivalence is.
- `s2:14–15`: "This section asks a prior question: when the literature studies that quantity, which name does it use?" This is a section-level question, and the section itself admits it comes "prior" to the real one.
- `s4:75–76`: "The rest of the section asks whether the pruning rules preserve that meaning." This is a good, crisp question, but it is local to Section 4.

**Is it stated early enough?** No. A reader cannot say what the paper is trying to find out until p. 5.

**Proposed one-sentence central question:**

> *Linhares and Yanasse (2002) listed twelve problems as equal "up to one": which of these equalities are true, and what follows when results, algorithms and benchmarks are moved freely between the twelve problems through pathwidth?*

The second clause is what unifies the paper:

| Part of the paper | What it contributes to the question |
|---|---|
| Section 2 | The literature does not move results between the problems (separate names, separate communities). |
| Section 4.1–4.5 | Moving one algorithm across exposes a false theorem and finds the correct rule already in the pathwidth literature. |
| Section 4.7 | Moving the benchmarks across gives one dataset that answers nine problems. |

**Where it should go:**

- As the last sentence of the paragraph that presents Table 1.1. In the restructured introduction (Section 7 below) that is paragraph 4, on p. 2.
- Repeated, as the second sentence, in the abstract.
- Answered point by point in the first paragraph of Section 5.

Each section should then open with one sentence saying which part of the question it answers. Suggested opening sentences are given in Section 3 of this report.

---

## 3. Section by section

### Title and abstract (`main:77–107`)

- **Title.** "twelve problems, one width, and a solver proved sound" makes three promises. Two of them overstate:
  - Only eight of the twelve problems are "one width"; two rows are false.
  - What is proved sound is a search algorithm specified in Lean, not the solver code (the paper says so carefully at `s4:319`).

  Consider: "The pathwidth complex: which of twelve 'equivalent' problems are equivalent, and a repaired exact search for open stacks".
- **Abstract.**
  - It opens with history, not with the problem. Start with one sentence saying what MOSP is and why it matters.
  - Fix the "seven of the twelve" count (see Section 1 of this report).
  - Do not use "Tamaki's commitment lemma" unglossed. Say "a known rule from exact pathwidth algorithms".
  - The phrase "Run as the default in both of our solvers" is project-internal. Say "In our implementation, ...".

### Section 1, Introduction (pp. 1–3)

**Question it answers (currently):** where the table came from. **Point:** the table was assembled without proofs and has been read as an equivalence. **How it serves the central question:** it motivates the question but never asks it.

**Where the reader is lost:**

- `s1:7–10`: MOSP is defined in one 50-word sentence, in cutting vocabulary ("patterns are cut", "piece type has a stack"). Later the paper switches to "customers", "products" and "patterns" (`s1:110–111`, `s3:42`, `s4:34`). No example or picture follows.
- `s1:12–17`: the NP-hardness reduction from modified cutwidth, with "padding the edge–vertex incidence matrix ... every column has the same sum C". This is a detail of the thesis that the paper never uses again, and "modified cutwidth" is not defined until `s3:77`. Cut it, or reduce it to "the thesis proved MOSP NP-hard (Linhares 2001; Linhares and Yanasse 2002)".
- `s1:23–36` and `s1:46–57`: **the same content twice.** Both paragraphs introduce the table with the same quotation. The first quotes the thesis and writes "f(Φ)". The second quotes the 2002 paper and writes "f(Π)". The reader thinks the two quotations are different claims. Merge them into one paragraph and one quotation.
- `s1:38`: "Looking back, the table was the thesis's most important finding." This is the authors' self-assessment, and it will read as self-promotion to a referee. The next sentence makes the real point ("if that is true, then every result about any one of them transfers"). Lead with that sentence.
- `s1:33–35`: the quotation from García de la Banda and Stuckey is good evidence that the table is relied on. Say why it matters: "So the table is already used to justify algorithms, in this journal; whether it is true matters."
- `s1:36`: "The thesis's own summary of findings (§7.1) does not mention the table at all." This is a curiosity that interrupts the argument. Cut it.
- **Contributions (`s1:87–106`):**
  - The bullets are long. Two of them run to 42 and 54 words (`s1:87`, `s1:96`).
  - They use undefined terms: "vertex-separation search", "exact core", "certified pathwidth", "witness layout", "proof object".
  - They are ordered by section, not by importance. For IJOC the search repair and the dataset are the computing contributions and should come first or second.
- **No roadmap and no headline results.** The introduction never says, in plain words, "two rows of the table are false", or "the strongest exact MOSP algorithm rests on a false theorem; we repair it for a few percent in nodes, and no benchmark value changes". These are the sentences a reader remembers.
- **Notation (`s1:108–114`).** It sits at the end of the introduction, before Section 2, which uses none of it. Move it to the start of Section 3. Note also the conflict: here **C** denotes the *columns* (patterns), while in Section 4 (`s4:34`) **C** is the set of *customers* (rows).

**Cut, move or add:** see Section 7 of this report for the full restructuring.

### Section 2, "One complex, twelve names" (pp. 3–7)

**Question it answers:** which name does the literature use for the shared quantity, and do the communities read each other? **Points:** (a) pathwidth dominates; (b) citation counts do not follow name usage; (c) the names belong to different decades; (d) the communities rarely cite each other.

**How it serves the central question:** only point (d), plus the last paragraph, serves it directly. Point (d) explains why the error in Section 4 went unnoticed and why the correct rule was sitting unread in the pathwidth literature. Point (a) justifies the paper's name. Points (b) and (c) are interesting but do not advance the argument.

**Placement problem.** The section title and its first paragraph (`s2:16–18`: "the problems are one object seen from three disciplines") assume the result of Section 3, which the reader has not yet seen. The text admits this: "This section asks a prior question" (`s2:14`). **Recommendation:** put Section 3 first, then a shortened Section 2 as the bridge to Section 4. Its message becomes: the problems are one, but the literatures are not, and here is what that cost.

**Subsection notes:**

- **2 (intro), `s2:16`:** "The answer gives the paper its title." This is fine, but it is the only motivation offered for the section. Add one sentence: "This matters because a result proved under one name is invisible to readers of the others; Section 4 is an example."
- **2.1 Method (`s2:20–68`, three paragraphs plus caveats).** This is too long for the main text of an OR journal, and it reads as defensive.
  - `s2:45`: "The check changed the counts and two of the conclusions." This refers to an earlier, unpublished count. Cut it.
  - `s2:56–57`: "The labels were made in one model-assisted session, record a yes or no per work and not the reason". A referee will press on this. Describe the labelling protocol precisely in the supplement. In the text, one sentence is enough: "one annotator with model assistance; a mechanical phrase rule agrees on 78% and gives the same conclusions".
  - Keep in the main text one paragraph covering: the source (OpenAlex), the restriction to four fields, the relevance filter, and the robustness check. Move the stemming examples, the 2,271/700/1,571 breakdown and the footnoted paths to an online supplement.
- **2.2 (`s2:70–115`)** makes two points. The second, "Citation counts do not track name usage" (`s2:110–115`), answers a question nobody asked. Cut it or make it a footnote.
  - `s2:99–100`: "Anything one would want to know about algorithms for this class of problems was most likely published under 'pathwidth'." This is the key sentence of the section. Move it to the section's first paragraph and to the introduction.
  - `s2:105`: "Split bandwidth is Fomin's own coinage ... and nobody adopted it." This is a nice aside, but it is an aside.
- **2.3 Three generations (`s2:117–144`).** The point ("only pathwidth is growing") takes one sentence. The paragraph spends four sentences on how the shading works, and that belongs in the caption. The subsection and Figure 2.2 are candidates for the supplement.
- **2.4 (`s2:146–180`).** This is the subsection that matters, and it is good. Two fixes:
  - `s2:178`: "a published error that the pathwidth literature's commitment lemma rules out". "Commitment lemma" is undefined until p. 19. Say "a rule already known, in correct form, in the pathwidth literature".
  - `s2:179`: "a benchmark for any problem in the exact core is a pathwidth benchmark". "Exact core" has not been defined. In the current order it is first named in Theorem 3.5's heading (p. 11), and it is never formally defined anywhere.

### Section 3, "The equivalences, proved" (pp. 8–13)

**Question it answers:** which entries of the table are true, and in what sense? **Point:** eight rows are exact, two are bands, two are false, and every relation goes through pathwidth. **How it serves the central question:** directly. This is half of the answer.

- **Opening (`s3:8–27`).** The distinction between the *literal* and the *fixed-offset* readings of "±1" (`s3:12–16`) is the most useful conceptual tool in the paper. It is the lens through which "exact" and "band" make sense. Promote it to the introduction as well, in one sentence.
- **The axioms footnote (`s3:20–26`).** The sentence about `propext`, `Classical.choice` and `Quot.sound`, and the footnote about one `sorry`, mean nothing to an IJOC reader. Replace them with: "All theorems below are verified in the Lean proof assistant; Appendix A lists the formal statements." Put axioms and `sorry`s in the appendix.
- **3.1 The problems (`s3:29–81`).** This is a necessary reference list, but it is dense. Every item is a single long question, and the search games (`s3:60–67`) involve recontamination, which will lose OR readers.
  - Recommendation: keep MOSP, gate matrix layout, pathwidth and vertex separation in full in the main text, with the introduction's example illustrating them.
  - Give the other eight in a compact table, one line of intuition each, and put the formal definitions in an appendix.
  - Also: "progressive" strategies (`s3:66`) is undefined.
  - The one-dimensional logic graph is called the "connection graph H" here (`s3:51`) but the "net graph" in Table 3.1's caption (`s3:88`). Use one name.
- **3.2 What is true (`s3:83–256`).** The section correctly puts the summary (Table 3.1, Figure 3.1) before the proofs. It then makes four points in a row (the hub theorem, the remaining exact rows, the bands, the false rows) with no internal headings. Add run-in headings: *The hub*, *The exact core*, *Bands*, *False rows*.
  - `s3:131`: "Two lemmas carry most of the exact rows." Theorem 3.5's items then cite their published sources, not these lemmas. Say which rows use them. As far as I can tell they are only used for Theorem 3.4.
  - **The pattern graph remark (`s3:189–193`)** appears without motivation: why would a reader think of the pattern graph? Say: "The literature also uses a second graph, with patterns as vertices (Yanasse and Senne 2010), and it is natural to expect it to work as well; it does not." Otherwise move it to a footnote.
  - **`s3:221–223`:** "follows the crusade argument of Bienstock and Seymour (1991), not the reduction to edge search of LaPaugh (1993) ..." This is a proof-engineering remark. Move it to the appendix.
  - **`s3:233–236`, the "brute-force check" footnote.** Values that "come from a brute-force check ..., not from Lean", followed by a `python -m` command, will confuse a reader who has just been told that everything is in Lean. Say once, in the appendix, which facts are computed and which are proved.
  - **`s3:254–256`:** "The edge-separation row is also misattributed". This is a good point, but it is easy to miss. Put it in Table 3.1.
- **3.3 Edge cases and a gap in a published proof (`s3:258–278`).** This subsection makes **two unrelated points**: degenerate inputs, and a gap in the proof of Kirousis and Papadimitriou. Neither answers a question the reader has. Move both to an appendix. Keep a one-sentence pointer: "Several published equalities need a nondegeneracy hypothesis, and one published proof has a gap that we repair; see Appendix B."
- **3.4 A thirteenth member (`s3:280–290`)** answers a question nobody asked. It introduces five new symbols (pbw, $G_d$, $D_u$, mpb, and a second pebbling game) in one paragraph. The "minimum progressive pebbling number" of Kirousis and Papadimitriou and Lengauer's "progressive black-white pebbling" are two different games presented side by side. Move the subsection to an appendix, and remove mpb from Figure 3.1 (or keep it, with a definition).
- **Summary (`s3:292–301`).** Good. Make its count agree with the abstract and introduction. `s3:296–297` says the bands "meet the literal reading of Table 1 and not the fixed offset", but leaves the arithmetic to the reader. Spell it out: relative to $Z=\pw+1$, $\sbw \in [Z-1, Z]$ and $\es \in [Z-1, Z+1]$, so both stay within one of $Z$, but neither is a fixed offset.

### Section 4, "An exact open-stacks search, read as a pathwidth solver" (pp. 13–23)

This section is ten pages, nearly half the body, and contains three papers' worth of material:

1. The search and its soundness (4.1–4.5).
2. Computational results (4.6).
3. A dataset (4.7).

**Question it answers:** are the published pruning rules of the best exact MOSP algorithm sound, and what does the pathwidth literature say about them? **Point:** two are false; the correct rule is a known pathwidth lemma with a cheap matching test; the repaired search is sound and cheap.

**Structural problems:**

- **The section's title promises "read as a pathwidth solver", but the reading arrives last.** The dictionary between the two vocabularies (Table 4.1) is in 4.5, on p. 19. Sections 4.1–4.4 are written entirely in MOSP vocabulary ($b(T)$, open stacks, customers). Move Table 4.1 and the paragraph `s4:338–342` into 4.1, so that the reader carries both vocabularies from the start. Section 4.5 then becomes "The repair is a known pathwidth lemma", which is the payoff of the section.
- **There is no overview of the algorithm.** The search is introduced through a block of six definitions (`s4:37–43`), then rules appear one by one across four subsections. Add **Algorithm 1**, pseudocode of the customer search, with one line each for free closure, memo lookup, cost cut, the three filters and old-move inheritance. Each rule's subsection can then point to its line.
- **The stakes come too late.** "No whole instance on which the published rules answer *unsat* wrongly is known" (`s4:332–333`) and "no value changed" (`s4:482`) should be in the second paragraph of the section, along with the main theorem stated informally.
- **4.6 and 4.7 are not about reading the search as a pathwidth solver.** Make them their own section, "Computational results and a dataset". IJOC readers look for that section by name.

**Subsection notes:**

- **Opening (`s4:10–28`).** `s4:21`: "finds three things". The third ("the whole repaired search is proved sound in Lean") is not a finding, it is a contribution. Restate as: two published rules are false; the correct rule was already known for pathwidth and costs one matching; the repaired search is provably sound and costs a few percent. Then add the stakes sentence.
  - `s4:26–28`: "All Lean names in this section are in `lean/MOSPFormalization/Search/`, which has no `sorry` and the standard axioms only." Move to the appendix.
- **4.1 (`s4:30–89`).** The six definitions in one display are hard to absorb. Give one small example: a 4-vertex path, one state, and the value of each quantity.
  - The proof of Theorem 4.2 (`s4:66–72`) uses a fourth symbol for the border, $\partial S_i$. Section 4.5 uses $N(T)$ and $d(T)$, and $N$ clashes with $N[c]$. Use one symbol for the border throughout.
  - **"What a rule must satisfy" (`s4:78–89`)** comes before any rule is described. It uses "old moves" (defined in 4.3, `s4:79`) and the notions of covering and chains. Its 43-word sentence at `s4:85–88` is the densest in the paper. **Move the whole paragraph to the start of 4.4**, where it is used.
  - The off-by-one shift in $k$ will trip readers. In Section 3, $k$ bounds the pathwidth ($|X_i|\le k+1$). In Section 4, $k$ bounds the stacks, so $\Sol_k(\emptyset)\iff \pw+1\le k$. Flag this explicitly at `s4:34`, or rename the stack bound (for example $s$).
  - `s4:63` and `s4:316`: "an instance $M$ with a requirement". Section 3 says "$M$ has a 1". Use one phrase.
- **4.2 (`s4:91–220`).** This is the paper's best subsection, and it would be better still with the order changed: intuition, then counterexample, then repair, then the matching test.
  - Before the quoted theorem, say in one sentence why the rule looks right: "if closing q now leaves no more stacks open than before, it seems safe to close it immediately". Lemma 4.3 then confirms that this is exactly what the premise says, and the counterexample shows why it fails ("an intermediate set is cheaper still").
  - The quotation (`s4:96–98`) uses Chu and Stuckey's notation ("S ++ [q]", "U′", "R′", "solution") without a gloss. Add one: "++ is concatenation of closing sequences".
  - `s4:101–102`: "We read d as ranging over customers not yet closed, as the code does". Whose code, Chu and Stuckey's or yours? Say which.
  - `s4:142–151` is one paragraph with four points: refuted under both readings, minimality by exhaustion, how the counterexample was found, and Fink's variant. Keep the first and last in the main text, and move the minimality search and the discovery story to the appendix.
  - "Why the published proof fails" (`s4:153–165`) is valuable to specialists. For IJOC, keep its first two sentences (the intuition) and move the rest, including the "second, independent slip", to the appendix.
  - **Theorem 4.7, the matching test, is the paper's main algorithmic novelty, and it is presented as an aside** ("What we did not find in the papers we hold is the following cheap form of the test", `s4:198–199`). Lead with it instead: "The repaired rule seems to require checking exponentially many intermediate sets. It does not: ...".
  - The "In words" paragraph (`s4:216–220`) is excellent. Move it *before* the theorem.
  - Lemma 4.5 (submodularity) arrives without motivation. Add: "The proof needs one inequality."
- **4.3 The other rules (`s4:222–283`).** Each paragraph does three things: it quotes the rule, proves it sound, and shows that its tie-break or test is necessary. That is consistent, which is good.
  - `s4:258–265`: "Two earlier faults of this rule in our own implementation are now proved in Lean too". `s4:278–283`: "One implementation of ours declined to run the memo beside the old move". Both are project history. Reframe them as design requirements ("the rules must be applied in the order definite, subset, better, or a cycle of true links can lose a node; Beck 2025 makes the general point") and drop "our implementation".
  - "The old move" and "the memo" are central to Theorem 4.9 but get the least explanation. One sentence of intuition each would help ("a sibling that failed stays failed in this subtree" and "a state's solvability does not depend on how it was reached").
- **4.4 The repaired search is sound (`s4:285–333`).**
  - Proposition 4.8 and Theorem 4.9 are machinery for Theorem 4.10. Keep Theorem 4.10 in the main text, stated informally first, and move 4.8 and 4.9 with their proofs to the appendix.
  - `s4:319–333`, the validation paragraph, is important: it says what is proved (the model) and what is only tested (the code). Present it as a short list: "the Lean model; agreement of the code with the model on N checks; a certificate checker". Move the eight-digit counts to the supplement.
  - The last two sentences (58 lost nodes, "No whole instance ... is known") are the stakes. Repeat them at the start of Section 4.
- **4.5 The search in pathwidth language (`s4:335–446`).** Strong content, and the intellectual payoff of the paper.
  - `s4:369–372`: "Neither line cites the other ..." is the concrete instance of Section 2.4's finding. Say so explicitly: "This is the isolation measured in Section 2.4, at the level of one algorithm."
  - **"Prior reports" (`s4:434–446`)** is a due-diligence paragraph. Shorten it to two sentences and move the reading percentages to the supplement.
- **4.6 The revised algorithm in practice (`s4:448–526`).**
  - **There is no experimental setup.** IJOC requires hardware, implementation language, time limits, instance sources and the meaning of "one worker", "pairs" and "descents".
  - Jargon to remove: `s4:456–458`, "Since 1 October 2026 these are the default in both of our solvers"; `s4:473`, "the MOSP C engine"; `s4:477`, "our MOSP corpus" (never introduced, and its relation to Table 4.6 is unexplained); `s4:479`, "exact subset-lattice computation, a checked DRAT refutation" (both undefined); `s4:512`, `csearch` (undefined; it is a configuration name).
  - Certificates (`s4:499–516`): the 55-word sentence at `s4:503–508` should be a bulleted list of what the checker verifies.
- **4.7 Dataset (`s4:528–584`).** Make this its own section.
  - Define provenance in plain words. *Refutation* means proved optimal by exhaustive search. *Bound* means proved optimal because a lower bound meets the witness. *Upper bound* means witnessed but not proved.
  - "minor certificate that replays" (`s4:542`) and "nauty certificates" (Table 4.6 caption) need a gloss.
  - The "caution about MOSP benchmark files" (`s4:572–576`) is useful to practitioners. Keep it.
  - The pricing paragraph (`s4:578–584`) belongs in the closing section's open problems.

### Section 5, Closing (`s5`, placeholder)

What it must do, in this order, and in at most a page and a half:

1. **Answer the central question** in one paragraph:
   - which of the twelve are pathwidth (exact, band, false);
   - what moving between them exposed (a false theorem, already corrected in another literature);
   - what it made possible (one dataset for nine problems).
2. **Say what an OR reader should do differently:**
   - cite the corrected table (Table 3.1), not the 2002 one;
   - look for MOSP and gate matrix results under "pathwidth";
   - implementations of Chu and Stuckey's rules (including the code used by Frinhani et al. 2018 and reused by Martin, Yanasse and Pinto 2022) should adopt the matching test. Their values are not known to be wrong, but their refutations are not proved.
3. **State the limits honestly, in one list:**
   - the Lean model and the code are linked by testing and certificates, not by proof;
   - the certificate's acceptance condition is argued on paper;
   - LaPaugh's es = pes is stated but not formalised;
   - one reference of the table is not held;
   - three re-certifications are still running (resolve these before submission if at all possible: "in flight" will not survive refereeing).
4. **Open problems.** The placeholder (`s5:9–10`) lists "the gap between pathwidth and treewidth on trees of cliques, where no degree or clique bound can close it". **This topic appears nowhere in the body.** Either introduce it in the body (a paragraph in the dataset section on why some classes stay open would do) or leave it out. A closing section must not introduce new material.

---

## 4. Figures and tables, one by one

### Table 1.1, the reproduced 2002 table (p. 2, `s1:59–85`)

- **What it shows:** the twelve problems, their disciplines and references, as printed in 2002.
- **What to conclude:** twelve problems from three fields were claimed equivalent, with references but no stated relations.
- **Does the text or caption say it?** The caption reproduces the original's wording ("studied independently on the literature"). The "on" is the original's error and reads as the authors' own; mark it as a quotation. The conclusion is stated in prose (`s1:50–51`), not in the caption.
- **Necessary?** Yes; it is the object of the paper.
- **Recommendation:** add a fifth column, visually separated (shaded or after a double rule), headed "This paper", with entries such as *exact, = pw+1*, *band*, *false*. This puts the punchline on p. 2 and lets Table 3.1 be the detailed version. Use the same row order in both.

### Table 2.1, works and citations per name (p. 4, `s2:72–81`)

- **What it shows:** relevant works, raw hits and citations per name.
- **What to conclude:** pathwidth is used more than all other names together, three times over; three names are unused.
- **Does the caption say it?** No. It defines the columns only.
- **Necessary?** It duplicates Figure 2.1's main column. **Keep one.** For IJOC I would keep the table in the supplement and the figure in the text, or drop the figure and keep a three-column table (Problem, Relevant, Hits).
- The 1,212/1,213 duplicate-record note appears **four times**: footnote `s2:47`, this caption, the Figure 2.1 caption and the Figure 2.2 caption. Say it once.

### Figure 2.1, bar chart of name usage (p. 5)

- **What it shows:** relevant works per name, coloured by discipline.
- **What to conclude:** "pathwidth" has absorbed the family.
- **Does the caption say it?** No. It describes the data source and colours. Add: "Pathwidth accounts for more relevant works than the other eleven names together, three times over."
- **Necessary?** Yes, if Table 2.1 moves out.
- The label is "graph path-width" here and "Path-width" in Table 2.1. Use one.

### Figure 2.2, heat map over time (p. 6)

- **What it shows:** each name's usage rate per five-year period, scaled to its own peak.
- **What to conclude:** the VLSI names belong to the 1980s, the search games to 1990–2010 and MOSP to 2005–14; only pathwidth is still rising.
- **Does the caption say it?** No. The caption explains the encoding, and the text spends four sentences on the encoding too (`s2:132–135`).
- **Consistency:** the row totals for MOSP (57) and vertex separation (53) differ from Table 2.1 (58, 55). The caption explains the discrepancy only for pathwidth.
- **Necessary?** Marginal. It supports a point the argument does not need. Move it to the supplement and keep one sentence in the text.

### Figure 2.3, citation network (p. 7)

- **What it shows:** the Table 1 papers on a circle, with 844 citing works.
- **What to conclude:** the operations-research side is an island; only six works connect MOSP to graph theory.
- **Does the caption say it?** No, and **the figure does not show it either.** The eye sees a dense web. The six bridging works are not marked, and the two MOSP papers sit next to the VLSI papers.
- **Necessary?** The point is necessary; this rendering is not.
- **Recommendation:** replace it with a 3×3 table or heat map, "citing works by pair of disciplines cited" (OR–OR, OR–VLSI, OR–GT, VLSI–GT, and so on). Alternatively, keep the network and highlight the six OR–graph theory bridging works in a contrasting colour, with the caption saying "Only six works (highlighted) cite both an OR paper and a graph-theory paper."
- Move the figure to the same page as Section 2.4. It currently floats two pages away from its text.

### Table 3.1, the table settled (p. 9, `s3:85–113`)

- **What it shows:** for each row, the true relation to pathwidth, the sources and a status.
- **What to conclude:** eight rows are exact, two are bands, two are false; every relation goes through pathwidth.
- **Does the caption say it?** No. It defines the status labels only. Add the conclusion.
- The column "**Proved in**" lists *published* sources, while the caption says the relations are "proved in Lean". A reader will read "Proved in: Möhring (1990)" as "the Lean proof is in Möhring". Rename the column "**Published source**".
- The Edge separation row packs two findings into one cell ("false; VSG exact"). Its misattribution (`s3:254–256`) deserves a footnote here.
- **Necessary?** Yes. With the extended Table 1.1, it becomes the reference version.

### Figure 3.1, the equivalence graph (p. 10)

- **What it shows:** sixteen quantities around pathwidth, with exact, band, false and unproved edges.
- **What to conclude:** pathwidth is the hub. Every exact relation is one or two steps from it, and the two false claims are the only red nodes.
- **Does the caption say it?** No. It explains the edge styles, the hypotheses and what is not drawn. Lead with the conclusion.
- The figure has sixteen nodes where the reader expects twelve. It adds multiple folding, VSG, pes, mns and mpb, and mpb is defined only in Section 3.4. If 3.4 moves to the appendix, drop mpb.
- **Necessary?** Yes; it is the best single picture of the result. Consider moving it into the introduction (after Table 1.1) as a preview of the answer.

### Figure 4.1, the counterexample graph (p. 15)

- **What it shows:** the 14-vertex graph at the state where the definite move fails.
- **What to conclude:** closing 0 looks safe (open = close = 3), but 3 and 4 share the single new stack 0, so closing them first is cheaper, and no solution starts with 0.
- **Does the caption say it?** **Yes. This is the best caption in the paper**, and a model for the others.
- **Necessary?** Yes.
- **Fixes:**
  - Remove the title printed inside the image ("A counterexample to Chu & Stuckey's Theorem 1, at k = 6 ..."); it duplicates the caption, and journals do not print in-figure titles.
  - Remove the regeneration command from the caption (`s4:120–121`).
  - Consider a second panel showing the state $B=\{2,3,4\}$, where the repair's test fails ($b(B)=2<3=b(X)$). That one picture would explain both the failure and the repair.

### Table 4.1, the dictionary (p. 19, `s4:344–361`)

- **What it shows:** each notion of the customer search next to its exact-pathwidth name.
- **What to conclude:** the customer search is, ingredient by ingredient, a known kind of pathwidth algorithm.
- **Does the caption say it?** Partly ("in the vocabulary of exact pathwidth algorithms").
- **Necessary?** Yes, but **in Section 4.1**, not 4.5. Drop the Lean column from the main text and put it in the appendix table of formal names.

### Table 4.2, each rule against the literature (p. 20)

- **What it shows:** for each rule, its counterpart in the pathwidth literature and its status.
- **What to conclude:** the published definite and better moves are false. The free move and the repaired definite move are known pathwidth results. The matching test, the subset rule, the repaired better move and the old move have no published counterpart, and are proved here.
- **Does the caption say it?** No. Add the conclusion.
- The "Status" column mixes three kinds of entry (known, false, proved here). Order the rows by status, or shade the "new" rows.
- **Necessary?** Yes; it is the novelty statement in one table.

### Table 4.3, cost of the repair (p. 21)

- **What it shows:** search nodes under the published and repaired rules.
- **What to conclude:** the repair changes the search effort by at most about 2% and never changed an answer.
- **Does the caption say it?** No. Put "never changed an answer" in the caption.
- **Clarity problems:**
  - Several column headings are unexplained: "Pairs finished", "Worst pair" (the worst per-instance ratio?).
  - The last row ("Graph pathwidth, whole descents at 120 s") measures something different from the MOSP rows (whole descents versus single refutations) and uses a different budget.
  - "In one worker" is unexplained.
  - Split the table into a MOSP part and a graph part, or explain.
- **Necessary?** Yes.

### Table 4.4, the split re-certification (p. 21)

- **What it shows:** the seven hardest re-certifications, with tasks, nodes and core-hours.
- **What to conclude:** the hardest values re-certify unchanged, at 18–154 core-hours each.
- **Does the caption say it?** No.
- **Necessary?** It is a status report. Three rows say "in flight", which cannot go to referees. Finish the runs, then fold the result into one sentence ("all seven re-refuted, unchanged, at 18–154 core-hours each") and move the table to the supplement.
- The instance names (`Random-125-125-4-1_0`) need a one-line key: customers, products, density, seed.

### Table 4.5, certificates (p. 22)

- **What it shows:** certificate emission and checking by size band and configuration.
- **What to conclude:** every certificate emitted is accepted, none is rejected, and checking is fast (milliseconds to seconds).
- **Does the caption say it?** No.
- **Clarity problems:** there are eleven columns. "Definite", "Better" and "Matching edges" are counts of pruning steps of each kind and matching edges; this is never said. The configurations `csearch` and `default` are never defined in the paper.
- **Recommendation:** in the main text keep only Customers, Instances, Verified, Rejected, Unknown, Median size and Median check time, for one configuration. Move the rest to the supplement.

### Table 4.6, the dataset (p. 23)

- **What it shows:** instance files, isomorphism classes and provenance per collection.
- **What to conclude:** 16,087 of 17,714 classes have a certified pathwidth. The open classes concentrate in PACE, the VSPLIB grids, Carvalho and Soma, and the large Frinhani instances.
- **Does the caption say it?** No. Add the conclusion.
- **Clarity problems:**
  - "Owned" is an unusual term. "Counted here" or "first occurrence" would be clearer.
  - The row "Challenge 2005 (second copy)" with 0 owned puzzles the reader. Explain it in a footnote or drop it.
  - The Frinhani "large" row (610 classes, none witnessed) needs one sentence saying why it is included.
  - The provenance terms need the plain definitions given above.
- **Necessary?** Yes.

---

## 5. Theorems, lemmas and counterexamples

| Item | Role clear on arrival? | Motivated before stated? | Main text or appendix |
|---|---|---|---|
| Lemma 3.1 (Helly for intervals) | Yes, announced as a tool (`s3:131`). | Partly. | Fold it into the proof of Lemma 3.2; it is three lines. |
| Lemma 3.2 (cliques sit in a bag) | Yes. | Yes. | Main. |
| Theorem 3.3 (vs = pw) | Known result (Kinnersley). Say "known" in the heading. | Yes. | Main, as a one-line statement with citation; the proof sketch can go. |
| **Theorem 3.4 (MOSP = pw + 1)** | **The hub of the paper.** | Only by Section 1's history. | **Main, with proof.** The introduction's example should foreshadow it (the open sets of the good order *are* the bags). |
| Star remark (`s3:189–193`) | No: "the pattern graph" appears from nowhere. | No. | Motivate it in one clause, or make it a footnote. |
| Theorem 3.5 (the exact core) | A catalogue; clear. | Yes. | Main, with proofs and Lean names in the appendix. Say explicitly that the paper does not reprove these on paper. |
| Theorem 3.6 (bands) | Clear. | Yes. | Main. |
| Theorem 3.7 (two rows are false) | Clear and important. | Yes, by the table. | Main. Consider putting it right after Table 3.1: the false rows are the news. |
| Section 3.3 claims (edge cases, K–P gap) | Unclear why now. | No. | Appendix. |
| Section 3.4 (pebbling) | Unclear. | No. | Appendix. |
| Lemma 4.1 (free moves never hurt) | Clear. | Partly. The intuition comes after the statement; move it before. | Main. |
| Theorem 4.2 (search decides pathwidth) | Clear and essential: it is what makes the search a pathwidth algorithm. | Yes (`s4:16–19`). | Main. The phrase "Read backwards as a layout" confuses, given that the Lean proof "goes through narrowness ... which counts the forward order". Pick one direction for the reader. |
| Lemma 4.3 (what the premise says) | Clear and very helpful. | Yes. | Main. |
| **Counterexample 4.4** | Clear. | Yes. | Main. The edge list is unreadable as prose; keep it, but say "see Figure 4.1" first. |
| Lemma 4.5 (submodularity) | Not clear on arrival. | No. | Main, with "the proof of the repair needs one inequality". |
| Theorem 4.6 (repaired move sound) | Clear. | Yes, by the repair paragraph. | Main, with the proof in the appendix. |
| **Theorem 4.7 (matching test)** | **Under-sold.** It is the paper's main algorithmic contribution. | Weakly ("What we did not find ..."). | Main. Lead with it, and put the "In words" paragraph before it. |
| Proposition 4.8 (filter node-sound) | Technical. | Depends on the displaced paragraph `s4:78–89`. | Appendix. |
| Theorem 4.9 (runs are sound) | Technical. | Partly (`s4:278–283`). | Appendix. |
| **Theorem 4.10 (revised search sound)** | The main theorem of Section 4. | It should be announced at the start of Section 4. | Main, stated informally first. |
| Lemma 4.11 (endpoint vs commitment) | Clear; it makes the bridge to Tamaki exact. | Yes. | Main. |

The pattern is consistent. The *results* are well chosen; the *machinery* (3.1, 3.3, 3.4, 4.8, 4.9) and the *provenance* (Lean names, minimality searches, implementation history) should go to appendices.

---

## 6. Flow, signposting, jargon, notation

### 6.1 Turns in the argument without a stated reason

| Location | Turn | What is missing |
|---|---|---|
| End of Section 1 to Section 2 (p. 3) | From the table to name counting. | Why the name matters (`s2:99–100` gives the reason; move it up). |
| Section 2 to Section 3 (p. 8) | From bibliometrics to proofs. | Nothing connects them. Reordering solves this. |
| Section 3 to Section 4 (p. 13) | From a table of equivalences to one algorithm. | The reason is in `s2:174–178`. Repeat it in the first two sentences of Section 4: "If MOSP is pathwidth, the best MOSP algorithm is a pathwidth algorithm, and its rules can be checked against what the pathwidth literature knows." |
| 4.4 to 4.5 (p. 18) | From the soundness proof to vocabulary translation. | This is the wrong order. The translation should come first. |
| 4.6 to 4.7 (p. 22) | From the repair's cost to a dataset. | The reason is at `s4:531`; a new section heading would carry it. |

### 6.2 Jargon used before it is defined, or never defined

| Term | First use | Defined? |
|---|---|---|
| Tamaki's commitment lemma | abstract `main:99`; `s2:178` | `s4:374–377` (p. 19) |
| exact core | `s1:104`; `s2:179` | never formally (Theorem 3.5 heading; list at `s4:532`) |
| modified cutwidth | `s1:13` | `s3:77` |
| vertex-separation search | `s1:96` | no |
| certified pathwidth, witness layout, proof object | `s1:101`, `s1:100` | partly in 4.6–4.7 |
| old moves | `s4:79` | `s4:267` |
| `csearch`, `default` | `s4:512`; Table 4.5 | never |
| DRAT refutation, subset-lattice computation | `s4:479` | never |
| "our MOSP corpus" | `s4:477` | never |
| C engine | `s4:473` | never |
| descents | Table 4.3 caption | never |
| nauty certificates, minor certificate | Table 4.6 caption; `s4:542` | never |
| crusade argument | `s3:221` | never |
| `sorry`, Mathlib, `propext` etc. | `s3:21–26`; `s4:28`; `s4:213`; title footnote | never (Lean-specific) |
| progressive (strategies) | `s3:66` | never |
| left-edge algorithm | `s3:201` | no; cite it |
| "with a requirement" | `s4:63` | never; Section 3 says "has a 1" |
| S ++ [q], U′, R′ | `s4:96` | never |

### 6.3 Notation clashes

1. **C** means columns in the introduction (`s1:110`) and customers in Section 4 (`s4:34`).
2. **k** bounds the pathwidth in Section 3 (`s3:38`: $|X_i|\le k+1$) and the stacks in Section 4 (`s4:62`: $\Sol_k(\emptyset)\iff\pw+1\le k$).
3. **The border of a vertex set** has four notations: $b(T)$ (`s4:41`, as a count), $\partial S_i$ (`s4:67`), $N(T)$ and $d(T)$ (`s4:338–339`). $N(T)$ also clashes with the closed neighbourhood $N[c]$ (`s4:36`).
4. **Z** is the MOSP value (`s3:42`) and also a set in the proof of Theorem 4.6 (`s4:187`: "With $Z=T_i$").
5. **Φ versus Π** in the two quotations of the same sentence (`s1:25`, `s1:49`).
6. **"Table 1"** means the 2002 table throughout. But the paper's own tables are numbered Table 1.1, 2.1, 3.1, and Table 1.1 *is* Table 1. A reader seeing "Table 1" and "Table 1.1" on the same page (p. 2) will be confused. Name it "the Linhares–Yanasse table" or "the 2002 table" throughout, and refer to the reproduction as Table 1.1.
7. **Two numbering systems for theorems.** "Theorem 1", "Theorem 2" and "Theorem 3" refer to Chu and Stuckey's numbering. "Theorem 6.3.6" and "6.3.8" refer to Chu's thesis. "Thm 4" refers to Lengauer. The paper's own theorems are numbered 3.x and 4.x. Always attach the author: "Chu and Stuckey's Theorem 1 (the definite move)". Better, name the rules by their names (definite move, better move, old move) and give the original number only once.
8. **The one-dimensional logic graph** is called the "connection graph H" (`s3:51`) and the "net graph" (Table 3.1 caption, Figure 3.1 caption).

### 6.4 Sentences over about 40 words (split them)

- `s1:7–10` (MOSP definition, about 50 words).
- `s1:87–90` and `s1:96–101` (contribution bullets, 42 and 54 words).
- `s1:110–113` (notation, 45 words).
- `s2:110–113`, `s2:132–135`, `s2:174–178` (43–49 words).
- `s4:85–88` (node soundness, 43 words).
- `s4:229–234` (subset rule, 43 words).
- `s4:306–308` and `s4:310–316` (44–45 words).
- `s4:327–331` (published filter, 47 words).
- `s4:477–480` (re-certification, 41 words).
- `s4:503–508` (certificate checker, 55 words; make it a list).
- `s4:513–516`, `s4:536–539`, `s4:569–572`, `s4:572–576` (42–43 words).

### 6.5 Paragraphs with no topic sentence

- `s3:258–267`. It opens "Three of the published equalities fail on degenerate inputs" and then lists four items, the last of which is a different kind of failure ($t=\ns$ on [1]).
- `s4:142–151`. It opens with the refutation of both readings, then turns to minimality, discovery and Fink.
- `s4:258–265`. It opens "Two earlier faults of this rule in our own implementation", which is a history topic, not an argument topic.
- `s4:477–487` ("Re-certification"). The topic sentence is a count. The point, "no value changed", is in the fourth sentence.

### 6.6 Project-internal material to remove from the main text

- The title footnote (`main:78–81`): "assembled from the project's working documents (`paper1/`). Every number regenerates by the command named beside it in those documents".
- All `python -m ...` commands: `s2:65–68`, `s3:233`, the Figure 4.1 caption `s4:120`, `s4:325–327`, `s4:438`, `s4:485–487`, `s4:566–567`.
- File paths: `s4:27`, `s4:487` (`Search/Split.lean`), `s4:325–326` (`paper1/solver_fix.md`, items 01–05).
- Dates of internal events: `s4:456` ("Since 1 October 2026").
- The 53 `\lean{...}` footnotes, about 87% of all footnotes.

Replace all of these with:

- one **"Data, code and proofs"** statement after the abstract or before the references, pointing to the paper's repository (IJOC requires deposit anyway);
- **Appendix A**, a table mapping each numbered result to its Lean name.

---

## 7. The introduction specifically

### 7.1 Evaluation of the authors' plan

The plan is to open with (1) MOSP defined with a worked example, (2) a gate matrix drawing of the same instance, (3) the quantity to minimise, (4) Table 1.1, and (5) how the table came to be.

**Verdict: right in its first four steps, and it needs three additions.**

- **Strengths.** It shows the object before the history. It makes "equal up to one" concrete: the reader sees *one* instance read two ways with the *same* number. It turns the current p. 1 (history first) the right way round.
- **Missing 1: the graph view.** The paper's hub is pathwidth, and Theorem 3.4 is the one proof every reader should follow. A third panel showing the MOSP graph of the same instance, with the open sets of the good order drawn as bags, costs a quarter page. It makes "MOSP = pathwidth + 1" visible before it is stated.
- **Missing 2: the central question and the headline results.** After the history the reader must be told what the paper asks and what it finds, in plain words with numbers.
- **Missing 3: a roadmap**, plus one sentence on how the reader should treat the Lean proofs.
- **Keep the history short.** Step (5) is one paragraph. The thesis anecdote, the NP-hardness reduction and "the most important finding" can go or be compressed.

### 7.2 Recommended order of paragraphs and figures

| # | Paragraph or figure | What it must establish |
|---|---|---|
| P1 | **The problem.** MOSP in OR terms (customers, products, stacks; or piece types and patterns, but pick one vocabulary and say once that the other exists). Refer to Figure 1.1(a). | The order of production changes how many stacks are open at once, and that maximum is what we minimise. In the example, order A needs 3 stacks and order B needs 5; only 2 of the 24 orders achieve 3. |
| **Fig. 1.1** | Three panels (specification below). | |
| P2 | **The same instance in VLSI.** Figure 1.1(b–c): patterns are gates, customers are nets, and the number of open stacks is the number of tracks (the density). | Two disciplines compute the same number on the same matrix. This is the first row of the table, and the reader now *sees* it. |
| P3 | **The same instance as a graph.** Figure 1.1(d): customers as vertices, a clique per pattern; the open sets of order A are bags of a path decomposition of width 2. | Pathwidth plus one equals the optimum. This is the hub, made concrete (proved as Theorem 3.4). |
| P4 | **The claim.** Table 1.1 (with a "This paper" column; see Section 4 of this report): Linhares and Yanasse (2002) listed twelve such problems as "equal ... or closely related (plus or minus one)". The two readings of "±1" (literal versus fixed offset), in two sentences. **End with the central question.** | What exactly is being tested, and the question the paper asks. |
| P5 | **How the table came to be, and why its truth matters.** Collected during the first author's thesis from three literatures, references only, no proofs or graph. It is cited as an equivalence, for example to justify an algorithm in this journal (García de la Banda and Stuckey 2007). The communities rarely cite each other (one sentence and number from Section 2). | The claim was never checked and is relied upon, and nobody is positioned to notice an error. |
| P6 | **What we find**, as four short bullets with numbers: (i) eight rows exact, two bands, two false; (ii) the literature uses "pathwidth" three times as often as all the other names together; (iii) two dominance theorems of the best exact MOSP algorithm are false, the correct rule is a known pathwidth lemma testable by one bipartite matching, the repaired search is proved sound, costs ≤ about 2% in nodes and changed no benchmark value; (iv) a dataset of 17,714 graph classes, 16,087 with certified pathwidth, answering nine problems at once. | The answers, before the details. |
| P7 | **How to read the paper.** Roadmap. One sentence on the role of Lean: "Every theorem is machine-checked in Lean 4; the reader need not read Lean, and Appendix A maps results to formal names." One sentence pointing to the data and code statement. | Navigation and trust, with the proof assistant kept out of the way. |

The contributions list can replace P6 if it is rewritten as P6 describes. The notation paragraph moves to the start of Section 3.

### 7.3 Specification of Figure 1.1 (precise enough to draw)

**Instance:** 6 customers (rows) a–f and 4 products or patterns (columns) P1–P4.

|   | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| a | 1 | 0 | 0 | 0 |
| b | 1 | 1 | 0 | 0 |
| c | 0 | 1 | 1 | 0 |
| d | 0 | 1 | 1 | 0 |
| e | 0 | 0 | 1 | 1 |
| f | 0 | 0 | 0 | 1 |

That is: P1 = {a, b}, P2 = {b, c, d}, P3 = {c, d, e}, P4 = {e, f}.

**Two orders.** I checked these by enumerating all 24 orders. The maxima are 3 (2 orders), 4 (16 orders) and 5 (6 orders).

- **Order A = P1, P2, P3, P4** (optimal; only A and its reverse reach 3).

  | Position | 1 (P1) | 2 (P2) | 3 (P3) | 4 (P4) |
  |---|---|---|---|---|
  | Open stacks | {a, b} | {b, c, d} | {c, d, e} | {e, f} |
  | Count | 2 | 3 | 3 | 2 |

  The maximum is **3**.

- **Order B = P1, P3, P4, P2** (worst).

  | Position | 1 (P1) | 2 (P3) | 3 (P4) | 4 (P2) |
  |---|---|---|---|---|
  | Open stacks | {a, b} | {b, c, d, e} | {b, c, d, e, f} | {b, c, d} |
  | Count | 2 | 4 | 5 | 3 |

  The maximum is **5**. Customer b is served at P1 but cannot be closed until P2, which comes last. c and d stay open from P3 to P2.

**Panels:**

- **(a) Matrix and profiles.** The 6×4 matrix above, with columns in order A. Below it, two rows of numbers: "open stacks, order A: 2 3 3 2" and "order B (P1 P3 P4 P2): 2 4 5 3". Or show the matrix twice, with the 1s of each row joined by a horizontal bar from its first to its last 1 (the "consecutive ones" fill), so that the open stacks at a column are the bars crossing it.
- **(b) Gate matrix layout, order A.**
  - Four vertical lines (gates), labelled P1–P4 from left to right.
  - Six horizontal wire segments (nets) a–f, each spanning from its first to its last gate, with a filled dot where it meets a gate it uses.
  - Pack the nets onto **3 horizontal tracks**: track 1 holds a (P1), then c (P2–P3), then f (P4); track 2 holds b (P1–P2), then e (P3–P4); track 3 holds d (P2–P3).
  - Draw a dashed vertical cut at P2 or P3 that crosses 3 wires, labelled "density 3".
- **(c) Gate matrix layout, order B.**
  - Gates in the order P1, P3, P4, P2.
  - Spans: a = [P1]; b = [P1 … P2], i.e. all four positions; c and d = [P3 … P2], positions 2–4; e = [P3 … P4], positions 2–3; f = [P4], position 3.
  - **5 tracks** are needed: track 1 holds a, then e; track 2 b; track 3 c; track 4 d; track 5 f.
  - Draw the dashed cut at P4, crossing 5 wires, labelled "density 5".
  - Panels (b) and (c) side by side make the point of the paper's first page: the same wires, a different gate order, a different number of tracks.
- **(d) The MOSP graph and a path decomposition.**
  - Vertices a–f. Edges a–b (from P1); b–c, b–d, c–d (P2, a triangle); c–d, c–e, d–e (P3, a triangle); e–f (P4).
  - Below it, four bags in a row: {a, b} – {b, c, d} – {c, d, e} – {e, f}. These are exactly the open sets of order A.
  - Caption: "Each pattern is a clique; each clique lies in a bag; the largest bag has 3 = pathwidth + 1 vertices."

**Suggested caption:** "One instance, three readings. (a) Six customers and four patterns; order A keeps at most 3 stacks open, order B keeps 5; only 2 of the 24 orders achieve 3. (b, c) The same matrix as a gate matrix layout: the same orders need 3 and 5 tracks. (d) The same matrix as a graph, one clique per pattern: the open sets of order A form a path decomposition of width 2, so the optimum is pathwidth + 1 (Theorem 3.4)."

If space is tight, drop panel (c) and give order B's profile in panel (a) only. Do not drop panel (d).

---

## 8. Audience and venue fit

**What IJOC readers know:** MOSP or sequencing problems, branch and bound, dominance rules, SAT and MIP, computational experiments, reproducibility requirements.

**What they lack:**

- **Path decompositions, the Helly property, the interval property.** Fixed by Figure 1.1(d) and the Theorem 3.4 proof, which is short and should stay.
- **Graph search games with recontamination** (`s3:60–67`), split bandwidth, narrowness, pebbling. Give informal one-liners in the main text and formal definitions in an appendix.
- **Lean and Mathlib:** axioms, `sorry`, named theorems, "Lean statement goes through narrowness" (`s4:71–72`). None of this should be in the main text. Say once that everything is machine-checked, and put the details in an appendix.
- **Exact pathwidth algorithm vocabulary:** full sets, commitments, failure tables. Table 4.1 bridges this, but it is placed too late.
- **Bibliometric method detail.** OR readers will accept a short method and want robustness checks summarised, not narrated.

**What IJOC expects and the draft lacks:**

- **An experimental setup** for Section 4.6: hardware, language, time limits, instance sources, what "paired runs in one worker" means. This is a likely desk-review issue.
- **A data and code availability statement** pointing to the deposited repository.
- **A computational section that is identifiable as one.** At present it is subsections 4.6–4.7 of a theory section.

**Move to the appendix (in the paper):**

- Appendix A: formal (Lean) names of every result, the axioms, the one remaining conjecture.
- Appendix B: formal definitions of the twelve problems; the degenerate cases (Section 3.3); the Kirousis–Papadimitriou gap; Section 3.4.
- Appendix C: Proposition 4.8 and Theorem 4.9 with proofs; "why the published proof fails"; the minimality search for the counterexample; Fink's variant in full.

**Move to the online supplement or repository:**

- regenerate commands and file paths;
- relevance-labelling protocol and the 78% agreement analysis;
- Figure 2.2 and possibly Figure 2.3;
- Table 4.4 (once final) and the full Table 4.5;
- the prior-art reading log;
- validation counts (16,244,090 node checks and the like);
- the dataset format and the checker's description.

**Length:** the body is about 22 pages. With the moves above, the main text can lose 5–6 pages while gaining Figure 1.1 and Algorithm 1.

---

## 9. The ten changes that would most improve readability, by impact

1. **Rewrite the introduction around a worked example and the central question** (`sec1_intro.tex`, whole). Follow Section 7.2: example, then gate matrix, then graph (Figure 1.1), then the claim (Table 1.1), then history, then headline results, then roadmap. End P4 with the one-sentence central question.
2. **Put the answer on p. 2 and fix the "Table 1" naming** (`s1:59–85`, `s3:85–113`). Add a "This paper" verdict column to Table 1.1. Call the 2002 table "the Linhares–Yanasse table" everywhere. Rename Table 3.1's "Proved in" column to "Published source". Make the count (eight exact, two bands, two false) identical in the abstract, the introduction and `s3:292`.
3. **Remove the project from the page** (53 `\lean` footnotes; `main:78–81`; the paths and commands at `s2:65`, `s3:233`, `s4:120`, `s4:325`, `s4:438`, `s4:485`, `s4:566`; `csearch`/`default`; "our corpus"; "C engine"; "Since 1 October 2026"). Replace them with Appendix A (formal names) and one data, code and proofs statement.
4. **Restructure Section 4 so the reading as pathwidth comes first** (`s4:30–89`, `s4:335–361`). Open with the stakes (no wrong answer known, no value changed) and the main theorem informally. Add Algorithm 1 (pseudocode). Move Table 4.1 and the border notation into 4.1. Move "What a rule must satisfy" (`s4:78–89`) to 4.4.
5. **Lead Section 4.2 with intuition and the matching test** (`s4:91–220`). Explain why the rule looks safe, then give the counterexample, the repair and Theorem 4.7, with the "In words" paragraph (`s4:216–220`) before the theorem. Present the matching test as the algorithmic contribution, not as "What we did not find".
6. **Split computation and data out of Section 4** (`s4:448–584`). Create a new section, "Computational results and a dataset", with an experimental-setup paragraph (hardware, language, budgets, instances). Define corpus, provenance, configurations, DRAT and subset lattice, or remove them. Finish the three "in flight" runs.
7. **Reorder and shorten Section 2, and place it after Section 3** (`sec2_names.tex`). Keep one method paragraph, the usage result and the communities result. End with the bridge to Section 4. Move Figure 2.2, the citations-versus-usage point (`s2:110–115`) and the method detail (`s2:31–68`) to the supplement. Cut "The check changed ... two of the conclusions" (`s2:45`).
8. **Unify notation** (`s1:110`, `s3:38`, `s4:34`, `s4:41`, `s4:62–67`, `s4:187`, `s4:338`). Use one letter each for columns, customers and the border; flag or remove the off-by-one in $k$; do not reuse Z; use "has a 1" consistently; use one quotation with one symbol; give one name for the one-dimensional logic graph.
9. **Make every caption state its conclusion, and cut redundant displays** (Figure 2.1, Figure 2.2, Figure 2.3, Table 3.1, Figure 3.1, Tables 4.2–4.6). Keep one of Table 2.1 and Figure 2.1. Replace or annotate Figure 2.3 so the "island" is visible. Reduce Table 4.5 to seven columns. Remove the in-image title of Figure 4.1. Say the 1,212/1,213 note once.
10. **Move machinery to appendices and write Section 5 as the answer** (`s3:258–290`, Proposition 4.8 and Theorem 4.9, `s4:153–165`, `s4:142–151`; `sec5_closing.tex`). Sections 3.3, 3.4, the proof-failure analysis, the minimality search and Proposition 4.8/Theorem 4.9 go to appendices. Section 5 answers the central question, gives practical advice, lists the limits, and does not introduce the treewidth/pathwidth topic unless the body does.
