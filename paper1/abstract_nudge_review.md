# Nudging *The pathwidth complex* towards the proposed abstract: a review

Reviewed 2026-10-11 against the LaTeX in `paper1/latex/` (draft of 6 October
2026), the notes in `paper1/`, `pathwidth_solver/`, the Lean development and
the held literature. No file other than this one was changed. Line numbers are
per file (`sec1_intro.tex:140` is line 140 of that file).

The proposed abstract, for reference:

> Following our previous work from 2001/2002, we show that there exists a
> *graph pathwidth complex*: a set of problems, studied independently,
> sometimes by different communities, that are, mathematically, graph
> pathwidth. We make corrections from the previously-published table of these
> problems, we include new problems to the list, providing proofs of the
> reductions, formalized in Lean. We claim this cluster should be called the
> *pathwidth* complex (and not, say, the pebbling complex) because pathwidth
> overwhelms all other communities in the published literature. Because we
> come from the 2nd most active community (MOSP: Minimization of Open Stacks
> Problem) and we had a competition of exact solvers, we struck luck: Chu &
> Stuckey won that competition, and we provide an exact algorithm for graph
> pathwidth, testing it on tens of thousands of instances. This algorithm is a
> variation of our competition's winner, which we prove formally in Lean to be
> incorrect, and we prove our corrected version to always achieve optimality.
> All of our results are open-source and can readily be confirmed by readers.

---

## 1. Where the paper stands now versus this abstract

**The current abstract** (`main.tex:103-130`) is question-driven. It opens
with MOSP, states that Linhares & Yanasse (2002) listed twelve problems as
equal "plus or minus one" without proofs, asks which equalities are true and
what moves between them through pathwidth, and then gives four findings: the
table settled (8 exact, 2 bands, 2 false, 3 new members, all in Lean); the
name (pathwidth more than three times the other eleven together, communities
rarely cite one another); the search (Chu & Stuckey is a pathwidth algorithm,
two theorems false, a 34-customer wrong optimum, repair by matching, proved
sound, at most 2% more nodes, 115 optima re-proved with none changed); and the
dataset (17,714 graphs, 16,087 certified).

**The proposed abstract** keeps three of those four findings and changes the
emphasis in four ways:

| | Current | Proposed |
|---|---|---|
| Frame | A question about a published table | A thesis: "there exists a pathwidth complex", and it is *our* table |
| Lead | MOSP, then the table | The complex, then the corrections |
| Naming | A finding of Section 3, reported as a count | The argument for the name, contrasted with "pebbling" |
| Search | Section 4's results, balanced (theorems false; values unchanged) | A story: our community, a competition, luck, a winner proved incorrect |
| Solver | Not in the abstract; one paragraph in Section 3 (`sec3_names.tex:120-127`) | "an exact algorithm for graph pathwidth, tested on tens of thousands of instances" |
| Reproducibility | Not in the abstract | "open-source and can readily be confirmed" |
| Omitted | | the 2% cost, the 115 unchanged optima, the bands, the dataset, the community isolation |

The move to a first-person, thesis-first frame is good for IJOC: the thesis
and the 2002 table are the authors' own, and "we correct our own table" is
both true and disarming. The graph-solver emphasis is also good, but the paper
does not yet carry it: the graph results are one paragraph in Section 3 with no
table in Section 5 (see §4). The narrative sentences ("we had a competition",
"Chu & Stuckey won", "struck luck", "prove ... to be incorrect", "always
achieve optimality", "readily be confirmed") are where the overclaims are
(§6). Dropping "115 values re-proved, none changed" removes the balance that
stops "incorrect" from being read as "its published results are wrong".

---

## 2. Changes to the introduction (`sec1_intro.tex`)

A nudge, paragraph by paragraph. Paragraphs not listed need no change.

**Opening example, lines 12-25; gate matrix, 41-51; graph, 53-63; wavefront,
65-71.** No change. The four readings of one matrix illustrate "studied
independently, sometimes by different communities, mathematically pathwidth"
better than any sentence could. One optional touch at line 24-25: "MOSP is
NP-hard \citep{Linhares2001,LY2002}" could read "MOSP is NP-hard, as the first
author's thesis showed \citep{Linhares2001,LY2002}", which sets up "our previous
work" early.

**Table 1.1 caption, lines 75-84.** "Twelve problems from three fields,
published as one family" is fine. To match the new frame, add after "as
printed": "This is our own table; the shaded column corrects it."

**The question and the name, lines 130-146.** This is where the new abstract's
central claim lives. Current, lines 140-143:

> We call the twelve \emph{the pathwidth complex}, because pathwidth is both
> the name the literature uses most (Section~\ref{sec:names}) and the quantity
> through which every true relation in the table is proved
> (Section~\ref{sec:equiv}).

Two problems. "The twelve" includes the two false rows, which are not
pathwidth, so the name is attached to a set the paper then shows is not
entirely pathwidth. And the new abstract wants the name argued against an
alternative. Proposed:

> We call the problems that are, on every input, pathwidth or pathwidth plus
> one the \emph{pathwidth complex}: most of the table, and three problems it
> missed. The name is not ours to choose freely. Pathwidth is the quantity
> through which every true relation in the table is proved
> (Section~\ref{sec:equiv}), and it is the name the literature uses, more than
> three times as often as the other eleven names of the table together
> (Section~\ref{sec:names}); a reader who searches under ``open stacks'' or
> ``gate matrix layout'' misses most of what is known.

Do not use "pebbling" as the foil (see §6, item 4).

**The history, lines 148-167.** This paragraph already carries "our previous
work". Two nudges.

1. Line 148-150, "The table has a history ... first printed in the first
   author's doctoral thesis": make "previous work" explicit and dated. Proposed
   first sentence: "The table is ours. It was first printed in the first
   author's doctoral thesis in 2001 \citep[Table~2.1, p.~13]{Linhares2001}
   ... and again, row for row, as Table~1 of \citet{LY2002}."
2. After line 159 (the García de la Banda & Stuckey quotation), add the
   challenge link, which is the honest version of "we had a competition":

   > When MOSP was chosen for the first Constraint Modelling Challenge in 2005,
   > the organisers' report pointed to the table for the problems equivalent to
   > it, graph path-width among them, and credited the second author with the
   > idea of searching over customers rather than patterns
   > \citep{SmithGent2005,Yanasse1997b}, on which the best exact algorithm,
   > Section~\ref{sec:search}, is built.

   This is supported: the report (`literature/2005-Smith-Gent-...-Proceedings-and-Report.pdf`,
   §1 and §5.3) says "Linhares and Yanasse [8] list several equivalent problems,
   including graph path-width" and "This idea was previously proposed by
   Yanasse [18]" (the EJOR 1997 paper). Check that Chu & Stuckey's customer
   search is fairly described as built on that idea before using the last
   clause; the report says it of Wilson & Petrie's entry.

Keep lines 162-164 ("Looking back, the table was the thesis's most important
finding, and this article does what the thesis did not"): it is the authors'
voice and is exactly the new abstract's intent.

**Three more members, lines 169-191.** No change in substance. Line 185-189
already separates what is new: "For pebbling and the vertex search, what is new
is the membership ... For the wavefront the equality itself is ours." Keep this
precision; it protects the abstract's "we include new problems".

**What we find, lines 193-226.** Four bullets. Changes:

- *The table, settled* (195-203): no change. Optionally lead with "Our table,
  corrected."
- *One name* (204-209): current "Besides pathwidth, the most active community
  over 2005--2024 is the open-stacks one, and the exact search of
  Section~\ref{sec:search} came from it". Keep the period qualifier; it is the
  only reading under which MOSP is second (§6, item 5). Proposed: "Since 2005,
  after pathwidth, the most active name of the twelve is MOSP, and the best
  exact search for the whole family came from that community, through the
  2005 Constraint Modelling Challenge (Section~\ref{sec:names})."
- *A repaired search* (210-219): reorder so that the Lean result and the
  computational result are told apart, and add the graph solver, which the new
  abstract puts in front and the intro never mentions. Proposed:

  > \emph{A repaired search, and a pathwidth solver.} The best exact algorithm
  > for MOSP, the customer search of \citet{ChuStuckey2009}, is also a
  > pathwidth algorithm. We prove in Lean that two of its published dominance
  > theorems are false, as are their later restatements
  > \citep{Chu2011,Fink2012}: each can discard the last solution at a node. On
  > every benchmark the previous algorithm happens to answer correctly, but on a
  > 34-customer instance it reports an optimum of 7 where the optimum is 6, a
  > fact backed by a SAT solver and a DRAT proof checked by drat-trim. The
  > correct rule was already known in the exact pathwidth literature; we show
  > that it is tested by one bipartite matching per candidate and prove the
  > repaired search sound. Ported to graphs, it proves the pathwidth of 11,194
  > of the 11,534 Rome graphs within 600\,s, all 50 VSPLIB trees and 39 of the
  > 73 Harwell--Boeing graphs (Sections~\ref{sec:search}, \ref{sec:names},
  > \ref{sec:results}).

- *Benchmarks re-certified, and a dataset* (220-225): no change; this keeps
  "115 re-proved, none changed", which the new abstract should not lose.

**How to read the paper, lines 228-239.** Line 234, "Every theorem we state is
machine-checked in the Lean~4 proof assistant", is accurate (computed facts are
labelled as such in `sec9a_appendix_lean.tex:23-36`). Add at the end, to carry
the abstract's last sentence honestly: "The Lean development, both solvers, the
dataset and an independent checker for each will be public with the paper."

---

## 3. Changes to the conclusion (`sec6_conclusion.tex`)

**Opening, lines 10-23.** Fine as it is. One sentence would tie it to the new
abstract's thesis, after line 16: "This is the sense in which the family is a
pathwidth complex: its exact members are one quantity, and the literature names
that quantity pathwidth."

**What transfers, lines 25-36.** No change. Lines 33-36 ("the communities
rarely read one another, and most of what is known about the family is
published under ``pathwidth''") already state the naming argument in its
defensible form, as a statement about names and citations.

**What the search teaches, lines 38-53.** Keep. One precision at lines 42-44,
"It took a search built for the purpose to find a whole instance with a wrong
optimum, 34 customers and one stack too many": add "in our implementation of the previous
algorithm, with its definite move, the subset rule and the old move and with the better move off; the optimum
of 6 is backed by a SAT solver and a DRAT proof checked by drat-trim". The
configuration matters, because Chu (2011, §6.3.2) says their own
implementation's better move subsumes the definite move, and with the better
move on the instance is answered correctly (`paper1/false_refutation.md:22-36`).

**What a reader can do differently, lines 55-62.** Add a third use that the new
abstract implies: "Use the repaired search as an exact pathwidth solver: on the
benchmarks with published exact pathwidth results it proves more graphs than
reported (Section~\ref{sec:names})." Keep lines 61-62 ("The values those
implementations report are not known to be wrong, but their refutations are not
proved"); it is the right register, and it covers Martin, Yanasse & Pinto (2022),
whose second author is ours.

**Limits, lines 64-78.** Add two items that the new abstract makes relevant:

- "The comparisons of the graph solver are with published numbers obtained on
  other hardware, not head-to-head runs, and only against
  \citet{CoudertMazauricNisse2016}" (this is already said at
  `sec3_names.tex:126-127`; the limits list should repeat it once the abstract
  advertises the solver).
- "The census of names covers the twelve names of the table; the three members
  we add, and the wider treewidth and pebbling literatures, are not counted."

**Open problems, lines 80-93.** No change; keep the two in-flight values here
until `Random-125-125-2-2_0` closes or is frozen.

---

## 4. Smaller ripples elsewhere

**Title** (`main.tex:94`). "The pathwidth complex" fits the new abstract better
than the old one, but it says nothing to an IJOC reader who does not know the
term (`review_readability_2.md:105-108` makes the same point). Options:
"The pathwidth complex: open stacks, gate matrices, search games, and a
repaired exact search"; or "The pathwidth complex: twelve problems, one
quantity, and a repaired exact solver". Avoid "graph pathwidth complex" (the
abstract's phrase) only if the body never uses it; at present it does not.

**Section 3, the names** (`sec3_names.tex`).
- Lines 104-118 already tell the challenge story correctly ("It is not a
  coincidence that the best exact algorithm for MOSP came from the open-stacks
  community"). This contradicts "we struck luck" in the proposed abstract; the
  paper's version is the better one, and the abstract should follow it.
- Lines 104-118: add the one-sentence link to the authors (the challenge report
  citing LY2002 and Yanasse 1997b), as proposed for the introduction, here or
  there but not both.
- Lines 109-110: "The winning entry". Both García de la Banda & Stuckey (2007,
  p. 1) and Chu & Stuckey (2009, §1) call it that, so the wording is
  defensible. Be aware that the organisers wrote that it was "a challenge, not a
  competition or evaluation", that "winners [cannot] be determined purely by cpu
  time", and that the prize was for best paper (Smith & Gent 2005, §11). A
  referee who knows the challenge may object to "competition"; "the entry
  judged best" or "the fastest entry" are safe alternatives.
- Lines 120-127: the graph-solver results are here, in the names section, as a
  three-sentence paragraph. If the abstract leads with the solver, give them a
  home in Section 5 (next item) and leave a pointer here.
- Section title "The names and the communities" could become "Why
  \emph{pathwidth}: the names and the communities", which signals that this
  section is the argument for the name.

**Section 4, the search** (`sec4_search.tex`). Lines 12-23 say the search
"decides pathwidth for every graph" (line 23) but never say it was ported and
run as a graph solver; one sentence at line 23, "and ported to graphs it is an
exact pathwidth solver (Sections~\ref{sec:names} and~\ref{sec:results})",
connects it to the abstract. Lines 464-475 ("What is proved and what is
tested") are exactly the qualification the abstract's "always achieve
optimality" lacks; keep them prominent. Lines 483-503 (the wrong optimum)
already give the configuration and the SAT/DRAT backing; no change.

**Section 5, results** (`sec5_results.tex`). The abstract's "tested on tens of
thousands of instances" needs a table of what the graph solver proved, and
Section 5 has none: Table 5.1 (`tables/cost.tex`) reports only node ratios on
731 of 880 graph pairs, and Table 5.3 (`tables/dataset.tex`) reports certified
classes by any method. `paper1/solver_fix.md:1235-1254` (item 08, Table 1) has
the right table: 11,915 graph benchmarks (Rome, VSPLIB grids, trees and HB,
TreewidthLIB colouring, freetdi named), 11,448 proved under the repaired rules,
0 width differences against the run of the previous algorithm. A small "Graph
benchmarks" table in §5.2 with the Coudert, Mazauric & Nisse (2016) column
beside it would carry the claim. Line 104, "Single pairs differ by at most
4\%", is true of the open-stacks rows only; on Rome one pair costs 1.64×
(`solver_fix.md`, item 08, Table 3, `grafo6585.97`). Say "single open-stacks
pairs".

**Data, code and proofs** (`sec7_data.tex:24-25`). "Everything this paper
reports can be checked from its repository, \fbox{URL to be added on release}".
Qualify "everything" (§6, item 12): witnesses and minor certificates are
checked by the independent checker; refutations are checkable by certificate
up to about 75 customers (`sec5_results.tex:178-187`); the largest refutations
can be re-run but cost over 1,000 core-hours each
(`sec5_results.tex:130-142`); and "a value certified by search cannot be
checked from its record" (`sec5_results.tex:246`).

**Figure and table captions.**
- Figure 3.1 (`sec3_names.tex:43-49`): "Pathwidth has more relevant works than
  the other eleven names together, three times over". Good; keep "names", not
  "communities".
- Table 3.1 (`sec3_names.tex:67-71`): "Besides pathwidth, the most active name
  over 2005--2024 is MOSP". Good; this is the abstract's "2nd most active" in
  its true form.
- Figure 4.2 (`sec4_search.tex:508-514`): "The published rules
  \citep{ChuStuckey2009} report a wrong optimum ... The layout the search with
  the published rules returns and certifies as optimal: 7 tracks." Change to
  "The previous algorithm \citep{ChuStuckey2009} reports a wrong optimum ...
  The layout the previous algorithm returns and certifies as optimal" (see
  §4a), and add "(our implementation, better move off)" and "(b) ... confirmed by a SAT solver and
  a DRAT proof checked by drat-trim". Without that, the caption reads as a
  claim about Chu & Stuckey's own code, which was not run.
- Table 1.1 caption: see §2.

---

## 4a. Terminology: "the previous algorithm", not "the published rules"

Author's instruction (2026-10-11): the paper should not say "the published
rules"; it should say **"the previous algorithm"**, meaning Chu & Stuckey's
customer search, cited on first use in each section (\citet{ChuStuckey2009}).
All proposed wording in this report, and the revised abstract in §7, already
follow it.

Two cautions in applying it. First, keep "published" where the object is a
*theorem* or a *premise* as printed ("two of its published dominance theorems
are false" is correct and should stay: the theorems are what Lean refutes).
Second, the wrong optimum is for one configuration of the previous algorithm
(definite move, subset rule and old move, better move off), run in *our*
implementations; Chu & Stuckey's own code was not run. Where the paper names
the failing run, say "our implementation of the previous algorithm, with the
better move off" at least once.

Locations to change (from `grep` over `paper1/latex/*.tex` and `tables/`):

| file:line | current | proposed |
|---|---|---|
| `main.tex:122` | "the published rules report a wrong optimum" | "the previous algorithm reports a wrong optimum" |
| `main.tex:127` | "optima that rested on the published rules" | "optima that rested on the previous algorithm" |
| `sec1_intro.tex:217` | "every benchmark the published rules happen to answer correctly" | "every benchmark the previous algorithm happens to answer correctly" |
| `sec1_intro.tex:221` | "rested on the published rules" | "rested on the previous algorithm" |
| `sec4_search.tex:29` | "the published search answers correctly" | "the previous algorithm answers correctly" |
| `sec4_search.tex:356` | "so the published rule is right there" | "so the previous algorithm's definite move is right there" |
| `sec4_search.tex:477` | "\paragraph{The published rules.} Under the published rules the filter is not node-sound" | "\paragraph{The previous algorithm.} Under the previous algorithm's rules the filter is not node-sound" |
| `sec4_search.tex:484` | "which the published rules \citep{ChuStuckey2009} give a wrong answer" | "which the previous algorithm \citep{ChuStuckey2009} gives a wrong answer" |
| `sec4_search.tex:488` | "the search with the published definite move, the subset rule and the old move" | "our implementation of the previous algorithm, with its definite move, the subset rule and the old move" |
| `sec4_search.tex:499-500` | "the published search answers this instance correctly; whether the published rules can also fail" | "the previous algorithm answers this instance correctly; whether it can also fail" |
| `sec4_search.tex:508` | caption "The published rules \citep{ChuStuckey2009} report a wrong optimum" | "The previous algorithm \citep{ChuStuckey2009} reports a wrong optimum" |
| `sec4_search.tex:510` | "The layout the search with the published rules returns" | "The layout the previous algorithm returns" |
| `sec4_search.tex:512` | "the published order reaches 7" | "the order of the previous algorithm reaches 7" |
| `sec4_search.tex:537` | "the published definite move is a commitment whose interior condition was dropped" | "the previous algorithm's definite move is ..." (judgement call; "published" here qualifies a stated rule) |
| `sec4_search.tex:562` | "The published definite and better moves are false" | keep, or "The definite and better moves of the previous algorithm, as published, are false" |
| `sec4_search.tex:572` | caption "Two published rules are false" | "Two rules of the previous algorithm are false" |
| `sec4_search.tex:581-582` | table rows "definite move, published", "better move, published" | "definite move, previous algorithm"; "better move, previous algorithm" |
| `sec4_search.tex:298, 530, 540` | "the published premise" | keep (a premise as printed), or "the premise of the previous algorithm" |
| `sec5_results.tex:14` | "All 115 that rested on the published rules" | "All 115 that rested on the previous algorithm" |
| `sec5_results.tex:31` | "the published tests remain available as an option" | "the tests of the previous algorithm remain available as an option" |
| `sec5_results.tex:41` | "once under the published rules and once under the repaired rules" | "once under the previous algorithm and once under the repaired one" |
| `sec5_results.tex:90` | caption "under the published and the repaired rules" | "under the previous algorithm and the repaired one" |
| `sec5_results.tex:103` | "the repaired and the published rules gave the same answer" | "the repaired and the previous algorithm gave the same answer" |
| `sec5_results.tex:123` | "rested on the customer search under the published rules" | "rested on the previous algorithm" |
| `sec5_results.tex:183` | "the published rules emit a complete tree" | "the previous algorithm emits a complete tree" |
| `sec6_conclusion.tex:41` | "where the published rules lost the last solution at a node" | "where the previous algorithm lost the last solution at a node" |
| `sec6_conclusion.tex:50` | "a checker of the published premises accepts" | keep, or "a checker of the previous algorithm's premises accepts" |
| `sec6_conclusion.tex:60` | "replace the published definite and better moves" | "replace the definite and better moves of the previous algorithm" |
| `sec7_data.tex:30` | "with the published and the repaired rules" | "with the previous algorithm and the repaired one" |
| `sec7_data.tex:35` | "the optimum the published rules report" | "the optimum the previous algorithm reports" |
| `sec9a_appendix_lean.tex:85` | "The published definite move is right when ..." | "The previous algorithm's definite move is right when ..." |
| `sec9a_appendix_lean.tex:99` | "Under the published rules the filter is not node-sound" | "Under the previous algorithm the filter is not node-sound" |
| `sec9a_appendix_lean.tex:102` | "The published premise gives a commitment" | keep, or "The previous algorithm's premise gives ..." |
| `tables/cost.tex:5` (generated by `make_tables.py:211`) | column "Nodes, published" | "Nodes, previous"; change it in `make_tables.py`, not the generated file |

Rows marked "keep" are about a printed theorem or premise, where "published"
is the precise word; the author may still prefer uniformity. Comment lines
(`%`) were not listed.

---

## 5. What to emphasize, and what to de-emphasize

**Emphasize**

1. *We correct our own table.* The thesis (2001) and LY2002 printed the table;
   this paper proves eight rows exact, two bands, two false, and adds three.
   Self-correction is the paper's strongest credential for a claim against
   someone else's theorems, and the new abstract's opening is right to lead with
   it. Name the two false rows (simple PLA folding; edge separation as cutwidth)
   and the bands (split bandwidth; edge search), since "corrections" alone is
   vague.
2. *Why "pathwidth"*: the name argument as the paper measures it, names and
   citations, not communities. 1,213 relevant works against 380 for the other
   eleven together; 6 of the 135 works citing an open-stacks paper also cite a
   graph-theory paper (`sec3_names.tex:53-57, 82-98`). The isolation number is
   the best evidence that the transfer matters, and the proposed abstract drops
   it.
3. *The MOSP-to-pathwidth transfer paid*: the best exact MOSP search, read as a
   pathwidth algorithm, put the previous algorithm's definite move next to the known correct one
   (Tamaki's commitment lemma), and the matching test is the algorithmic
   contribution (`sec4_search.tex:332-357`). This is the IJOC-shaped result.
4. *The graph solver, with honest numbers*: 11,194 of 11,534 Rome graphs within
   600 s (97.1% against 95.6% published), all 50 VSPLIB trees (against 30), 39
   of 73 Harwell–Boeing (against 26), as comparisons with published numbers.
5. *Balance on the error*: two theorems false in Lean; one wrong optimum backed
   by SAT and a checked DRAT proof; 115 benchmark optima re-proved, none changed;
   repair costs at most 2% nodes per benchmark set. All four belong together.
6. *The legitimate link to the challenge*: the 2005 challenge report cites LY2002
   for the equivalent problems, path-width among them, and credits Yanasse
   (1997b) with the customer-ordering idea; García de la Banda & Stuckey (2007),
   the challenge's best entry, published in IJOC itself, credit their speed to
   LY2002's FPT remark (`sec1_intro.tex:157-159`).

**De-emphasize**

1. "Competition", "won", "struck luck", "our competition's winner". Wrong in
   fact or wrong in register (§6, items 6-7), and "luck" contradicts the paper's
   own "It is not a coincidence" (`sec3_names.tex:104`).
2. "Prove ... to be incorrect" as a verdict on the algorithm. Prove the
   theorems false; report the wrong optimum with its configuration. The authors
   are about to make a public claim against named colleagues (`todo.md:19-20`
   still lists "Decide whether to write to Peter Stuckey"); precision is
   courtesy and protection at once. Note also that the false restatement of
   Fink (2012) is a thesis supervised by the second author, and that Martin,
   Yanasse & Pinto (2022) reuse optima from the unrepaired code: saying so is
   the strongest evidence of good faith.
3. "Always achieve optimality". Soundness of refutations is what Lean proves,
   about the search as specified (§6, item 10).
4. "Overwhelms all other communities". It is names, not communities, and the
   census covers only the table's twelve names.
5. The pebbling foil. Pebbling was not counted (§6, item 4).
6. "Readily be confirmed". Not until the repository is public, and not for the
   largest refutations (§6, item 12).

---

## 6. Overclaims and factual risks, claim by claim

Verdicts: **supported**, **qualify**, or **wrong**.

**1. "Following our previous work from 2001/2002".** *Supported; name it.* The
previous work is Linhares (2001), doctoral thesis, INPE, advisor H. H. Yanasse
(`refs.bib:225-233`), whose Table 2.1 (p. 13) first printed the table and which
proved MOSP NP-hard and equal to gate matrix layout (`sec1_intro.tex:148-151`);
and Linhares & Yanasse (2002), *Computers & Operations Research* 29(14),
1759–1772 (`refs.bib:14-21`), Table 1, p. 1764. The 2002 paper gave no proofs of
the rows (`sec1_intro.tex:134-135`). Say so in the abstract: "listed ... without
proofs" is what makes the present paper necessary.

**2. "there exists a graph pathwidth complex: a set of problems ... that are,
mathematically, graph pathwidth".** *Qualify.* True of the exact core only:
eight of the twelve rows (counting pathwidth itself), the two exact variants
(multiple folding, Lengauer's vertex separator game) and three added members
(`sec2_equivalences.tex:279-285, 379-390`). Split bandwidth and edge search are
bands, `pw ≤ sb ≤ pw+1` and `vs ≤ es ≤ vs+2`, with both ends occurring; simple
PLA folding and edge separation (as cutwidth) are not within any constant of
pathwidth (`sec2_equivalences.tex:329-372`). Also, several exact rows need
nondegeneracy (an edge, a nonempty graph, a 1 in the matrix;
`sec9b_appendix_machinery.tex:59-68`). "Most of them are" or "their exact
members are" is the honest form.

**3. "We make corrections from the previously-published table ... we include
new problems ... providing proofs of the reductions, formalized in Lean."**
*Supported, with four qualifications.*
- What was corrected: two rows false as stated (simple PLA folding:
  `max(pw+1, ⌈|C|/2⌉) ≤ pla`, gap unbounded; edge separation read as cutwidth:
  unbounded on stars), each with an exact variant; two rows only within a band;
  the "plus or minus one" made precise by the fixed-offset versus literal
  reading (`sec1_intro.tex:135-140`); nondegeneracy hypotheses added; the edge
  separation reference misattributed, since what Lengauer proves exactly is the
  vertex separator game (`sec2_equivalences.tex:181-183`); and a gap in the
  Kirousis–Papadimitriou proof of `vs ≤ ns − 1` repaired
  (`sec9b_appendix_machinery.tex:70-77`).
- Every *relation* in Table 2.3 is proved in Lean (`sec9a_appendix_lean.tex`,
  entries A.1-A.14 and A.47-A.49), axioms `propext`, `Classical.choice`,
  `Quot.sound` only. But: (a) that both ends of each band occur, which is what
  makes those rows bands rather than exact, is computed by brute force on
  `K_2`, `K_{1,3}`, `K_{3,3}` (`complex_check.py`), not proved in Lean
  (`sec2_equivalences.tex:337-341`; `sec9a_appendix_lean.tex:32-35`);
  (b) LaPaugh's `es = pes` is the named, unasserted gap `EdgeSearchMonotonicity`
  (`lean/MOSPFormalization/Complex/EdgeSearch.lean:95-98, 195-197`); no row
  needs it, because `Complex/EdgeSearchFull.lean` proves the band for the full
  game without it; (c) one reference, Kashiwabara & Fujisawa (1979), is not
  held, and interval thickness is proved from two other references of the table
  (`sec2_equivalences.tex:391-392`); (d) the Lean definitions are our
  formalisations of the published definitions, matched by reading
  (Appendix B), which is inherent and worth one clause in the paper, not in the
  abstract.
- "Providing proofs": on paper the paper proves the hub (Lemma 2.1, Theorem 2.3)
  and *cites* the published proofs of the other exact rows ("We do not reprove
  them on paper", `sec2_equivalences.tex:280-282`). "Every relation is proved,
  and machine-checked in Lean", the current abstract's wording, is accurate.
- "New problems": three. For progressive pebbling and the vertex search the
  equalities were published and what is new is membership; for the maximum
  wavefront the (elementary) equality is ours (`sec1_intro.tex:185-191`).

**4. "called the pathwidth complex (and not, say, the pebbling complex) because
pathwidth overwhelms all other communities in the published literature".**
*Qualify; the foil is wrong.* What `popularity.md` shows is name usage:
pathwidth 1,213 relevant works (1,212 distinct) against 380 for the other
eleven names together, 3.2× (3.6× under the mechanical phrase rule), and 21×
MOSP (`popularity.md:28-41, 52-55, 386-416`). "Overwhelms" is fair for names.
But:
- It measures names, not communities. Graph theory as a community includes
  pathwidth, vertex separation and the search games; the paper's community
  measurement is the citation one (Table 3.2), which is a different claim.
- **Pebbling was not counted.** The census covers only the table's twelve names;
  "the three members we add ... are not counted" (`sec3_names.tex:35-38`).
  Pebbling also has a large literature in other senses (proof complexity,
  register allocation, space–time trade-offs), so a referee could fairly ask
  whether "pebbling" outnumbers "pathwidth" in a naive count. The paper has no
  number to answer with. Use a counted name as the foil: "and not the
  open-stacks or gate-matrix complex".
- The counts are lower bounds and OpenAlex has thin abstracts before 1990, which
  undercounts the VLSI names (`popularity.md:105-111`).

**5. "we come from the 2nd most active community (MOSP)".** *Qualify: true only
for 2005–2024, and only by name.* Over all years MOSP has 58 relevant works and
ranks fourth of twelve, behind pathwidth (1,213), gate matrix layout (110) and
PLA folding (68) (`popularity.md:28-41, 65-71`); under the phrase rule it is
fifth, behind vertex separation (65) (`popularity.md:393`), and the note
concludes "the paper should say 'one of the better-used names', not 'fourth'"
(`popularity.md:414-416`). Over 2005–2024 MOSP is second with 51, ahead of
vertex separation (32) and edge search (28) (`tables/periods.tex`;
`sec3_names.tex:76-80`). Counted as communities rather than names, VLSI (gate
matrix layout + PLA folding + one-dimensional logic) and graph searching (node
+ edge search + vertex separation + interval thickness, 133) each exceed MOSP's
58 over all years. Correct form: "since 2005, the most active name after
pathwidth is MOSP".

**6. "we had a competition of exact solvers ... Chu & Stuckey won that
competition".** *Wrong on three counts.*
- *Not ours.* The first Constraint Modelling Challenge (May 2005) was posed and
  organised by Barbara Smith and Ian Gent, proposed by Patrick Prosser, at the
  IJCAI 2005 Workshop on Modelling and Solving Problems with Constraints
  (`refs.bib:367-373`; report p. 1 and §11). Linhares and Yanasse were neither
  organisers nor entrants: the 13 entries listed are by Baptiste, Beldiceanu &
  Carlsson, García de la Banda & Stuckey, Hebrard et al., Hnich et al., Miller,
  Miller et al., Pesant, Prestwich, Shaw & Laborie, Simonis, Szymanek &
  Hennessy, Truchet et al. and Wilson & Petrie. The honest connection is that
  the report cites Linhares & Yanasse (2002) as listing "several equivalent
  problems, including graph path-width", and credits Yanasse (1997b) with the
  idea of permuting customers rather than products (report §1 and §5.3).
- *Not a competition of exact solvers.* The organisers wrote: "It was also his
  idea that it be a challenge, not a competition or evaluation ... we do not feel
  that constraint programming is at a point where winners can be determined
  purely by cpu time", and the prize was for best paper (report §11). Entries
  included local search (Prestwich).
- *Chu & Stuckey did not win it.* The entry the literature calls the winner is
  García de la Banda & Stuckey, published as García de la Banda & Stuckey
  (2007), *INFORMS Journal on Computing* 19(4), 607–617 — this journal
  (`refs.bib:237-243`; `sec3_names.tex:106-112`). Chu & Stuckey (2009), CP 2009,
  came four years later, built on it and was five to six orders of magnitude
  faster on hard instances (`sec3_names.tex:112-117`). The paper's own Section 3
  has this right; the abstract would contradict it.

**7. "we struck luck".** *Register.* Not IJOC prose, and it contradicts the
paper ("It is not a coincidence", `sec3_names.tex:104`), whose explanation
(the challenge drew constraint programmers to MOSP; their search reads only the
MOSP graph; therefore it decides pathwidth) is better than luck. Use the paper's
version.

**8. "we provide an exact algorithm for graph pathwidth, testing it on tens of
thousands of instances".** *Qualify the count and the novelty.*
- *The algorithm* is Chu & Stuckey's customer search, ported to graphs
  (`pathwidth_solver/`, `TRANSFER.md`), with the definite and better moves
  repaired. "We provide" is fair for the repaired, ported solver; "our
  algorithm" is not.
- *Graph benchmarks run by the graph solver, repaired rules*: 11,915 graphs
  (Rome 11,534, VSPLIB trees 50, grids 50, Harwell–Boeing 73, TreewidthLIB
  colouring 58, freetdi named 150), 11,448 proved, 0 width differences against
  the run of the previous algorithm (`solver_fix.md:1235-1254`). Rome: 11,194 of 11,534
  within 600 s (97.05%; the older figure, under the previous algorithm, in
  `pathwidth_solver/TRANSFER.md:47-48, 75` and in `CLAUDE.md` is 11,183,
  97.0%). The dataset adds freetdi control-flow (1,817 files), PACE 2016/2017
  (791 files) and the small graphs of Martí et al. (84), so the graph solver has
  been pointed at roughly 14,600 graph files.
- *MOSP instances*: the corpus is 6,376 files, 3,667 distinct MOSP graphs; the
  repaired customer search re-proved the 115 values that rested on the
  previous algorithm, and ran 6,135 + 125 + 23 cost pairs (`tables/cost.tex`).
  6,259 corpus values do not depend on the customer search at all
  (`sec5_results.tex:110-124`).
- *Small-graph soundness checks*: 17,431,232 runs over 52,592 graphs on 1 to
  17 vertices (`sec4_search.tex:471-472`). These are tests, not benchmarks.
- *Generated MOSP ensembles* (37,800 at n ≤ 40, 6,747 at 50–75; `CLAUDE.md`)
  were solved under the pre-repair rules and are not in this paper.
- *Dataset*: 21,754 files, 17,714 isomorphism classes, 16,087 with certified
  pathwidth, but "certified" includes values certified by bound (3,535) and
  MOSP values certified by DP or SAT, not by this solver (`tables/dataset.tex`).

  "Tens of thousands" is true only by adding these unlike things. Safer:
  "on more than 11,000 benchmark graphs" or the Rome sentence itself, and
  "17,714 distinct benchmark graphs" for the dataset. Also note the comparison
  is with published numbers on other hardware, against one exact solver
  (Coudert, Mazauric & Nisse 2016; `sec3_names.tex:120-127`).

**9. "a variation of our competition's winner, which we prove formally in Lean
to be incorrect".** *Wrong as phrased; here is what is proved where.*
- *Proved in Lean* (`sec9a_appendix_lean.tex`, entries `thm1false`, `fink`,
  `bettercex`, `thm638`, `notsound`; `lean/MOSPFormalization/Search/`):
  Chu & Stuckey's Theorem 1 (definite move) is false under both readings of
  `close`; their Theorem 2 (better move) is false; Chu's thesis Theorems 6.3.6
  and 6.3.8 are false; Fink's (2012) restatement is false on a 15-customer
  graph; and under the previous algorithm's rules the filter is not node-sound — it can
  discard the last solution at one step of the search
  (`not_codeFilterSound_cexGraph`). That is a statement about a node, not about
  a whole instance.
- *Not a Lean theorem, but independent of both customer searches*: on a
  34-customer instance, our C and Python implementations of the previous
  algorithm (definite move, subset rule and old move; better move off) refute 6 and
  report an optimum of 7, while the optimum is 6. That 6 suffices is shown by
  an order that simulates to 6; that 5 does not is shown by Kissat
  independently and by a CaDiCaL DRAT proof verified by drat-trim
  (`sec9d_appendix_sat.tex:53-63`; `sec4_search.tex:483-503`). This should be
  described as *backed by a SAT solver and a checked DRAT proof*, not as merely
  computational. The residual trust is in the encoder emitting the clauses the
  Lean model of the encoding describes, which is "a reading of its source, not
  a proof" (`sec9d_appendix_sat.tex:46-51`), and in drat-trim.
- *Scope*: the failing configuration has the better move off; with it on the
  instance is answered correctly, and whether a better-move configuration can
  fail is open (`false_refutation.md:22-36`; `todo.md:72-75`). Chu (2011,
  §6.3.2) says their implementation's better move subsumes the definite move.
  Chu & Stuckey's original code was not run; Frinhani et al. (2018) ran it
  (`sec9b_appendix_machinery.tex:166-172`). On every benchmark the previous
  algorithm answers correctly, and all 115 values that rested on it stand.
- *Not "our competition's winner"*: see item 6.

  Honest form: "two of its published dominance theorems are false (proved in
  Lean), and on a 34-customer instance the previous algorithm reports a wrong
  optimum (backed by a SAT solver and a checked DRAT proof)".

**10. "we prove our corrected version to always achieve optimality".**
*Qualify.* Lean proves soundness of refutations for the search *as specified*
(an `Exec` relation modelling Algorithm 4.1 with the repaired filter):
if the repaired search refutes `k` from the root then no closing order fits in
`k` stacks, `pw(G) ≥ k`, and on a MOSP graph `Z(M) > k`
(`Search/Memo.lean:372-374`, `Search/Decide.lean:280-305`; Theorem 4.9,
`sec4_search.tex:450-457`). Together with the fact that a "yes" comes with a
witness that is checked by simulation, this makes the decision procedure
correct in both directions. It is not a theorem about termination within a
budget, and it is not about the code: "that our C and Python implementations
run it is checked, not proved" (`sec4_search.tex:464-475`; limits,
`sec6_conclusion.tex:66-71`), by 16.2 M node checks, 36.9 M matching checks,
17.4 M runs on small graphs, and per-run certificates (6,275 of 6,286 verified
at 9–75 customers, none rejected; `sec5_results.tex:178-187`), whose checker's
acceptance condition is itself a paper argument (`sec6_conclusion.tex:69-71`).
Honest form: "we prove in Lean that the repaired search is sound: when it
reports that `k` stacks do not suffice, they do not".

**11. "This algorithm is a variation of ..."; "we provide an exact algorithm".**
*Qualify novelty.* The repaired definite move is Tamaki's commitment lemma
(Kitsunai et al. 2016, Lemma 1) and is "not new" (`sec4_search.tex:327-330`);
what is new is the matching test, the repaired better move, the subset and old
move proofs, and the soundness of their combination (Table 4.2,
`sec4_search.tex:570-594`). The paper says "none found" is "not a claim of
priority" (line 568) and `todo.md:17-18` says "never 'first'". The abstract
should keep that discipline.

**12. "All of our results are open-source and can readily be confirmed by
readers."** *Not yet true; qualify after release.* The repository does not
exist publicly: `sec7_data.tex:24-25` carries "URL to be added on release", and
`todo.md:9-12, 35-37` lists the repository stub and the IJOC code-and-data
repository with a DOI as open items. Even after release, "readily" holds for
the Lean (one build and the axiom check), the witnesses and minor certificates
(independent checker), the 34-customer instance (a standard-library Python
checker and a 35 s DRAT check, `todo.md:62-64`), and refutations up to about
75 customers (certificates). It does not hold for the largest refutations, which
cost 18–369 core-hours each for seven instances and 1,128 core-hours for
`Random-125-125-2-3_0` (`sec5_results.tex:126-142`), nor for any value
certified by search without a certificate ("cannot be checked from its record",
`sec5_results.tex:246-248`). One corpus value, `Random-125-125-2-2_0`, is still
uncertified (`sec6_conclusion.tex:80-84`). Honest form: "the Lean proofs, both
solvers, the data and independent checkers are released with the paper".

**13. Omissions that change the reading.** Not overclaims in themselves, but
the proposed abstract drops: the bands (so "mathematically pathwidth" reads as
universal); "115 optima re-proved, none changed" and "at most 2% more nodes"
(so "incorrect" reads as "its results were wrong"); and the citation isolation
(the best evidence that cross-community transfer matters).

---

## 7. A proposed revised abstract

About the same length as the proposal (≈ 235 words against ≈ 205), in the
authors' first-person frame, with every claim above in its supported form.

> In 2001 and 2002 we listed twelve problems from operations research, VLSI
> design and graph theory, the minimization of open stacks problem (MOSP) among
> them, as equal "plus or minus one", without proofs. We show that most of them
> form a *pathwidth complex*: problems studied independently, by communities
> that rarely cite one another, that are mathematically pathwidth. We correct
> our table. Eight rows are exactly pathwidth or pathwidth plus one, two lie in
> bands one and two wide, and two are false as stated; we add three members it
> missed, among them the maximum wavefront of sparse matrix elimination, and
> every relation is machine-checked in Lean. We call the cluster the
> *pathwidth* complex because the literature uses that name more than three
> times as often as the other eleven together; since 2005 the next most active
> name is MOSP. That community produced, through the 2005 Constraint Modelling
> Challenge, the best exact MOSP algorithm, the customer search of Chu and
> Stuckey (2009), which is also a pathwidth algorithm. We prove in Lean that two
> of its published dominance theorems are false, and on a 34-customer instance
> the previous algorithm reports a wrong optimum, which a SAT solver and a checked
> DRAT proof confirm. The correct rule was known for pathwidth; we test it with
> one bipartite matching and prove the repaired search sound. It re-proves all
> 115 benchmark optima that rested on the previous algorithm, changing none, and
> ported to graphs it proves the pathwidth of 11,194 of the 11,534 Rome graphs.
> We release the proofs, both solvers and 17,714 benchmark graphs, 16,087 with
> certified pathwidth, with independent checkers.

If the length must come down, the sentence on the wavefront and the Rome clause
are the first to go; the bands and "changing none" should stay.

---

## Summary

**Top three overclaims**

1. *"We had a competition ... Chu & Stuckey won"*: wrong. Smith & Gent
   organised the 2005 challenge, which its organisers said was "not a
   competition"; the best entry was García de la Banda & Stuckey (2007, IJOC);
   Chu & Stuckey (2009) came later. The authors' real link is that the
   challenge report cites their 2002 table and Yanasse's customer-ordering idea.
2. *"prove formally in Lean to be incorrect" / "prove our corrected version to
   always achieve optimality"*: Lean proves two published theorems false and that
   the previous algorithm can discard the last solution at a node; the wrong
   optimum on the 34-customer instance is backed by a SAT solver and a checked
   DRAT proof, in one configuration (better move off), not on Chu & Stuckey's
   code. Lean proves the repaired search *sound as specified*; the C and Python
   are linked by testing and certificates.
3. *"open-source and readily confirmed"*, *"tens of thousands of instances"*,
   *"2nd most active community"*: the repository is not public yet and the
   largest refutations cost over 1,000 core-hours; the instance count only
   reaches tens of thousands by adding unlike sets (about 11,900 graph
   benchmarks proved at the core); MOSP is second only by name and only over
   2005–2024, and the pebbling foil was never counted.

**Top three emphasis changes**

1. Lead with "we correct our own table" and name the corrections (two false
   rows, two bands, three new members), with "every relation machine-checked in
   Lean".
2. Make the name argument the paper's measured one, names and citations
   (1,213 against 380; 6 of 135 cross-citations), with a counted foil.
3. Give the graph solver a table in Section 5 and a sentence in the
   introduction, and keep the balance on the error: theorems false, one wrong
   optimum, 115 values unchanged, at most 2% more nodes.
