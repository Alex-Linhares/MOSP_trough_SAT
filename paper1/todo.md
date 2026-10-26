# *The pathwidth complex*: to do

Started 2026-10-09. Check items off as they are done.

## Before posting on arXiv

Done 2026-10-19: the source bundle builds and compiles standalone
(`python -m paper1.latex.make_arxiv`, `latex/arxiv.tar.gz`); the metadata,
categories, licence choice and a 1,783-character abstract are in
`latex/arxiv_metadata.md`; the axiom audit, reference check and paper tests
pass (the hypercube and Mycielski theorems were missing from
`axiom_check.lean`); `pw(M_9) <= 138` and the date are current.


- [x] **Affiliations and emails** for both authors (2026-10-19; Yanasse's in
      English, the owner's choice).
- [x] **The paper's repository**: it is this repository, public at
      github.com/Alex-Linhares/MOSP_trough_SAT, which `latex/sec7_data.tex`
      names; the three `\repofile` paths exist in it, and the README's opening
      points at the paper (2026-10-19). A separate paper repository with its own
      DOI is the IJOC item below, not an arXiv one.
- [ ] **Re-check the novelty claims.**
  - [ ] Read the 14 unread works that cite Chu & Stuckey 2009, listed in
        `literature/MISSING.md` (item 01 of loop0008). De Giovanni et al.
        (2013, *ITOR*) first. *2026-10-19: eight obtained and read (Gange 2019, Visentin 2019,
        Stivala 2010, Chu & Stuckey 2012, Doulabi 2016, Arbib 2012 and 2016,
        De Giovanni 2010); none bears on the rules, and De Giovanni 2010 is a
        fourth work that ran their code without a failure, now cited in
        Appendix B. 2026-10-22: both De Giovanni 2013 papers received from the author
        and read; both ran Chu & Stuckey's code without a failure (six such
        works now). Four remain: Carvalho & Soma 2015, Lima & Carvalho 2017,
        Santos & Carvalho 2018, and the two mislinked ITOR papers. Counts in
        the paper: 66 of 141.*
  - [ ] Keep the wording "we found no prior report", never "first"
        (`prior_art_counterexample.md`).
- [ ] **Decide whether to write to Peter Stuckey** (and Geoffrey Chu) before
      the counterexample and the 34-customer wrong optimum become public.
- [ ] **arXiv endorsement.** The first author has arXiv papers in cs.AI
      (2604.17229, April 2026), so the account exists; endorsement is per
      category, and cs.DS is new to it. Start the submission: the form says at
      once whether cs.DS needs an endorser, and emails the request link. The
      abstract page of any recent cs.DS paper lists who can endorse.
  - Primary category: cs.DS.
  - Cross-lists: math.CO, math.OC, cs.DM, optionally cs.LO.
- [ ] **IJOC's preprint policy.** Confirm that posting on arXiv before or
      during review is allowed. INFORMS's author pages refused scripted access;
      check by hand.

## Before submitting to IJOC

- [ ] **The IJOC LaTeX class and formatting rules**, downloaded by hand from
      INFORMS. The draft uses `article` as a stand-in.
- [ ] **Length.** The draft is 45 pages, about 25 of them body. Decide between:
  - cutting Section 4, as `review_readability_2.md` suggests;
  - moving the appendices into an online supplement.
- [ ] **The repository in IJOC's form:** a code-and-data repository with its own
      DOI, following the template at `github.com/INFORMSJoC/2019.0000`
      (`ijoc_literature.md`).
- [ ] **Cite the relevant IJOC papers** from `ijoc_literature.md`, in particular
      Garcia de la Banda & Stuckey (2007), already held, and the 19 papers to
      obtain listed in `literature/MISSING.md`.

- [ ] **The solver claim: head-to-head against SageMath** (high priority; ready to run: `pathwidth_solver/bench/sage_headtohead.py`, SageMath 10.8 in the `sage` conda env; needs a quiet machine). "Best" would hold
      after a few hours of running SageMath's solver against ours on this
      machine, which is better done once the split run finishes. SageMath's
      `vertex_separation(algorithm="BAB")` is Coudert, Mazauric & Nisse's (2016)
      branch and bound, the one openly available exact competitor of known
      strength; run both on the same graphs (Rome sample, VSPLIB, TreewidthLIB
      colouring, Mycielski), same caps. Until then the abstract's closing
      sentence should read "strongest exact ... openly available", with the
      published comparison, the hardware caveat and the Mycielski loss
      (`myciel6` = M7, 95 vertices, pw 38: they prove it in about 10 minutes,
      we do not in 1,500 s) printed in Section 5
      (`abstract_nudge_review_2.md` §3).

- [x] **Rome graphs, a longer timeframe.** Done before 2026-10-19 (all 11,534 proved:
      292 by the minor step, 48 without a time limit, Section 5.3). The one Rome
      class proved without a stored witness, grafo10809.99 (width 9), got its
      layout on 2026-10-21 from the C program (`dataset_open/results_unlimited.csv`);
      the fold now carries a same-width witness onto a proved row that has none.
      *(The original item follows.)* The Rome graphs (Di Battista et
      al. 1997, a graph-drawing benchmark: 11,534 graphs of 10–110 vertices)
      were run in stages of 10, 120 and 600 s per graph; 11,194 are proved and
      340 are open, all at n ≥ 86. Rerun the 340 with a much longer cap (hours
      per graph, after the split run) and report the count at each cap.

## The 34-customer instance under every configuration (2026-10-12)

Our implementation (definite move on throughout; better move, old move, memo
switched): the reported optimum is wrong (7) only with the better move off and
the old move on, memo either way. All four configurations with the better move
on, including Chu & Stuckey's published one, report 6; so do the two without
the old move. (Their p. 6: "Our implementation of 'better move' subsumes
'definite move' so we will simply consider them as one improvement.")

- [ ] **Add the configuration table to Section 4**, beside Theorem 4.9, so the
      claim is exact and fair: which configurations fail, which do not, and
      that "answers correctly here" is not soundness (the published better move
      is false as a theorem too).
- [ ] **Hunt for instances that break their published configuration** (better
      move on, old move, memo: the one Chu & Stuckey actually run). Lean will
      not show a failure there unless one exists, so the question is empirical:
      search for small instances on which that configuration reports a wrong
      optimum, starting from the published better move's Lean counterexample
      (Section 4) the way `false_refutation_hunt.py` started from the definite
      move's, with the corrected search, SAT/DRAT and the lattice oracle
      (n <= 15) as referees. If one is found, check it in Lean as Theorem 4.9
      was; if none is, report the size of the search, so the paper can say how
      hard the open question is.
- [ ] **Who runs the definite move alone?** Check Chu (2011), Fink (2012) and
      the code behind Frinhani et al. (2018), reused by Martin, Yanasse & Pinto
      (2022). If any runs it without the better move, the counterexample bears
      on published work directly.

## The contraction-minor lower bound (found 2026-10-11)

The exact pathwidth of a contracted minor is a lower bound
(`reports/pathwidth_lower_bounds_survey.md`). It proves pw(myciel6) >= 38 on a
58-vertex minor in under a second, pw(myciel7) >= 71 (published: 52), and
closes Random-125-125-2-1_0, 2-3_0, 6-1_0 and SP4 in 1-80 s each. The idea is
known for treewidth (Bodlaender, Koster et al.), so the claim is the
measurement and that, for pathwidth, it is not capped by treewidth.

- [ ] **Into the solvers.** A budgeted step in the `pathwidth_solver` descent and in
      the MOSP descent: before refuting UB - 1 on the full graph, contract to
      about n/2 and upward and try to refute UB - 1 there; a refutation ends the
      descent with proof "bound" (or a new provenance, "certified:minor"). Measure
      on every benchmark set: what it closes, what it costs.
- [ ] **myciel7.** Settle 71 against 72 (Coudert et al. 2016 leave it open at
      pw <= 72). If it is new, say so carefully, after the literature check.
- [x] **Lean** (done 2026-10-12, `lean/MOSPFormalization/Minor.lean`, commit
      1c24e5d2f): contracting an edge never increases pathwidth
      (`pathwidth_contractEdge_le`), nor does deleting a vertex or an edge
      (`pathwidth_induce_le`, `pathwidth_mono`); along any legal contraction
      sequence (`pathwidth_minorOf_le`); the certificate theorem
      (`pathwidth_gt_of_minorOf`, and `pathwidth_gt_of_iso_minorOf` for a minor
      on its own labels); and the MOSP form `MOSPInstance.lt_mospValue_of_minorOf`.
      Axioms: the three standard ones. Statements checked first on small graphs
      (`tests/test_lean_minor_statement.py`). Still assumed: that the code's minor
      is isomorphic to `minorOf` for the recorded sequence (tested), and the
      soundness of the refutation on the minor. Proposed paper text, for the
      write-up: Section 5, "Every minor lower bound rests on minor monotonicity
      (Fellows & Langston 1987, Lemma 4.2): contracting an edge, or deleting a
      vertex or an edge, never increases pathwidth, so a refutation of
      pw(H) <= w on a minor H reached by a recorded contraction sequence proves
      pw(G) >= w + 1, and on the MOSP graph that every pattern order opens at
      least w + 2 stacks; both are proved in Lean." Appendix A entry `minor`,
      with \leannames{pathwidth_contractEdge_le, pathwidth_induce_le,
      pathwidth_mono, pathwidth_minorOf_le, pathwidth_gt_of_minorOf,
      MOSPInstance.lt_mospValue_of_minorOf}.
- [ ] **A checkable certificate.** The minor certificate is the contraction
      sequence (checkable by anyone) plus a refutation on the small graph (a
      DRAT proof, or our search certificate of Section 5). Ship both for every
      value certified this way.
- [ ] **Write it up.** A subsection of Section 5 ("A lower bound from minors"),
      the myciel6 passage rewritten (no longer a loss), the corpus values it
      re-certifies cheaply, the cost of 2-3_0 falling from 1,128 core-hours to
      seconds, and an honest line on what remains open (2-2_0: every contraction
      up to 95 vertices still admits 24).
- [ ] **Re-run the dataset's 860 upper-bound-only classes with the minor step.**
      *Running since 2026-10-21 02:50: `reports/scratch/dataset_open/run_unlimited.py`,
      415 classes (every non-certified class within the engine's limit, Frinhani
      excluded), the C program, no time limit, 24 workers at nice 19, cheapest
      first; results fold in from `results_unlimited.csv`. Rebuild with
      `python -m paper1.dataset values`, `write`, `tables` when it ends.*
      They were certified under short budgets (about 2.5 core-hours in all), so
      most are "ran out of time", not "proved hard": PACE 2016/2017 288, Rome
      326 (292 already closed by the minor step), Carvalho & Soma 139,
      Harwell-Boeing 33, colouring 27, named 23, grids 19. Run them with the
      minor step on (default once the solver agent commits), a few cores, a
      generous cap; then rebuild the dataset (`python -m paper1.dataset values`,
      `write`, `tables`) and update the counts in the abstract, Section 5 and
      the conclusion, whose "the graph sets will not close by budget alone" and
      "certified without search only when a lower bound meets its witness"
      need rewriting around the minor bound. Also try the ~150 classes above the 1,024-vertex limit:
      their minors may fall below it, but a minor gives only the lower bound,
      so a class is certified only where a witness layout of the full graph
      (from the dataset's runs, Python heuristics, annealing, or a known family
      layout such as row-by-row for grids) meets it; elsewhere record the
      narrowed interval (as myciel7's 71-72); the 610 large
      Frinhani MOSP instances stay out of reach.
- [ ] **Say it in the paper:** "Comparative pathwidth complex theory is richer than
      studying each problem in isolation." A thesis line for the introduction
      or the conclusion: the transfers in both directions (the corrected search
      from MOSP, the minor bound from pathwidth), the slips found only by
      setting the problems side by side (the false rows, Kirousis &
      Papadimitriou's edge cases), and one dataset for every problem.
- [ ] **A table: hard MOSP instances collapsing from core-days to seconds through
      the pathwidth lower bound.** One row per instance: its optimum, the cost
      of the full refutation that certified it, and the minor certificate
      (minor size, nodes, seconds). What we have now:
      - Random-125-125-2-3_0 = 21: 1,128 core-hours -> a 69-customer minor,
        666,153 nodes, under a second;
      - Random-125-125-2-1_0 = 24: 366.5 core-hours (Table B.1) -> an
        87-customer minor, 30 s (large budget);
      - measured 2026-10-13 at the owner's request (2 cores, 5 min each,
        reports/scratch/minor_table/): 2-5_0 = 20, 368.8 core-hours -> a
        63-customer minor, 0.4 s; 2-4_0 = 24, 154.1 -> 69 customers, 0.3 s;
        4-5_0 = 46, 26.1 -> 99 customers, 82 s; not settled in 5 min: 4-4_0
        (bound 50 of 51), 4-2_0 (55 of 57), 2-2_0 (24 of 25);
      - Random-125-125-6-1_0 = 81 and SP4 = 53: minor bound equals the optimum;
      - Random-125-125-2-2_0 = 25: 2,231 core-hours, not reached by any minor
        up to 95 customers (an honest last row).
      So 5 of Table B.1's 9 values settle in seconds or minutes.
- [ ] **Writing rule: no development history.** When writing about the solver,
      leave out the history of how our algorithm was developed (the bugs, the
      re-certifications, the configurations we tried, the order things were
      found). Focus on two transfers:
      - **MOSP -> pathwidth:** the correction of Chu & Stuckey's search, the
        best exact MOSP algorithm, which is also a pathwidth algorithm;
      - **pathwidth -> MOSP:** the new lower bound from contracted minors, which
        settles MOSP instances that the search needed core-days for.
- [ ] **A light touch, for the reader: Lean versus Kirousis & Papadimitriou.**
      Mention, with humour, that Lean caught two slips in Kirousis &
      Papadimitriou (1985, 1986): their equality ns = vs + 1 fails on graphs
      with no edges (no searcher is needed, so ns = 0 while vs + 1 = 1;
      `edgeless-ns`), and the proof of their Theorem 4.1 has a gap on the star
      K_{1,3} (`kirousisPapadimitriou_claim2_false`), repaired by their own
      Corollary 2.4; the theorem is true. Keep it accurate and affectionate:
      name both authors, call them slips, not "serious errors", and laugh at
      ourselves too, since our own 2002 table has the same edge-case flaw.
      Facts in Appendix B ("Edge cases and a gap in a published proof").
- [ ] **Say it in the paper:** "The complex gets an excellent lower bound from
      pathwidth, and an excellent algorithm from the MOSP side." The thesis of
      the transfer in one line: the minor bound comes from the pathwidth
      literature, the customer search from the open-stacks community, and the
      complex is where they meet. Candidate places: the abstract's close, the
      introduction's findings, and the conclusion's "What transfers".
- [ ] **Compare with Coudert et al. on the rest.** Their win on myciel6 came from
      prefix storage, not bounds (JEA 2016, Sec. 4.3); the remaining difference
      in raw search speed is unexplained. The SageMath head-to-head item above
      should include the solver with the minor step.
- [ ] **Fetch the papers** listed under "Pathwidth lower bounds (2026-10-11)" in
      `literature/MISSING.md` (Bodlaender & Koster 2011 journal version,
      Clautiaux et al., Lucena, Chandran & Subramanian, Mohar & Poljak,
      Fraire-Huacuja et al., Solano & Pioro).

## The introduction: MOSP's other guises (2026-10-17)

- [ ] **Name MOSP's other settings in the introduction**, after the cutting
      industry: among them the scheduling of scenes in film shooting. (The
      humorous opening was considered and dropped by the owner.)
      - **Film shooting / talent scheduling:** Cheng, Diamond & Lin (1993), JOTA
        79(3) 479-492, doi 10.1007/BF00940554; Garcia de la Banda, Stuckey & Chu
        (2011), INFORMS JoC 23(1) 120-137, doi 10.1287/ijoc.1090.0378. Both are
        listed for fetching in `literature/MISSING.md` (browser download).
        Talent scheduling minimizes a weighted *sum* of waiting days, not the
        *maximum* number on hold at once: present it as a close relative of
        MOSP, not the same problem.
      - Other settings: check Yanasse & Senne (2010) and Linhares & Yanasse
        (2002) for further applications; VLSI gate matrix layout is already in.

## Closed formulas for recursive families (high leverage, 2026-10-18)

- [ ] **Plan: `reports/closed_formula_families_plan.md`.** Exact pathwidth of
      small members, guess a formula, prove it by induction on the
      construction, Lean as for grids. First: Mycielski graphs and hypercubes
      (2026-10-18, after the G(n, c/n) pilot).

## Lean the derived random-graph bounds (high priority, 2026-10-17)

`reports/random_graph_pathwidth_survey.md` derives three bounds no paper states
(marked **[derived]** there, unrefereed). Check them, then prove them in Lean.
The deterministic cores are within reach of the existing development
(`VertexSeparation.lean`, `Sandwich.lean`); the probabilistic halves need a G(n, p)
model Mathlib does not have, so they come second, as finite first-moment
inequalities rather than asymptotics.

- [ ] **Brute-force check first** (lesson from the false branch lemma): each
      deterministic core against every graph to 9–10 vertices
      (`learning/pwtw_exhaust.py` has the census), before any Lean.
- [ ] **(1) Linear lower bound for average degree c > 4 ln 2 ≈ 2.77.**
      Deterministic core: if vs(G) ≤ k, there are disjoint A, R with
      |A| = |R| ≥ ⌈(n − k)/2⌉ − 1 and no A–R edge (survey §1.4). Then the
      first moment: the expected number of such empty pairs in G(n, c/n)
      vanishes below β*(c)·n, so whp pw ≥ β*(c)·n, beating Perarnau–Serra's
      treewidth bound at every c.
- [ ] **(2) Subcritical c < 1: pw = (1 + o(1)) log₃ log n.** Deterministic
      cores: a tree on N vertices has pw ≤ log₃(2N + 1); the complete ternary
      tree of height h has pw = h (classical, Scheffler; to cite, not claim).
      Probabilistic half: whp every component is a tree or unicyclic of size
      O(log n), and a ternary tree of size Θ(log n) occurs.
- [ ] **(3) Dense, constant p: n − pw = Θ(log n)**, between (2 − o(1)) log_b n
      and (4 + o(1)) log_b n, b = 1/(1 − p), against the published O(√(n/p)).
      Deterministic cores: pw ≤ n − α(G), and the empty-pair lemma of (1).
      Probabilistic half: the independence number and empty-pair first moments.
- [ ] **The large-n theorem first** (medium priority, owner 2026-10-18): the
      route to a real theorem about random graphs at every n is (1)'s
      first moment, "with high probability pw ≥ β*(c)·n", proved by counting,
      not enumeration; the G(n, c/n) measurements (`reports/scratch/gnp_pilot/`)
      test it but cannot prove it. *Pilot done 2026-10-18 and written up
      2026-10-26 in `reports/random_graph_pathwidth_survey.md` §7(d): 6,542
      exact pathwidths, no graph below `β*(c)·n`, fitted slopes 0.08–0.10
      above `β*` at every `c ≥ 3`; the full measurement is priced there.*
- [ ] **Exact E[pw] and Var[pw] of G(n, p) for n ≤ 11** (low priority,
      2026-10-18): exact polynomials in p with integer coefficients, from the
      census of every graph to 11 vertices (`learning/pwtw_exhaust.py`) and
      the count of labelled copies of each class. Computation, not proof.
      In Lean only for n ≤ 5-6, by brute force over the 1,024 / 32,768
      labelled graphs with kernel `decide` (avoid `native_decide`, which
      trusts the compiler), as a small fully verified example.
- [ ] Only after the checks and Lean: decide whether these go in a paper, and
      search once more that none is already published.

## Contributing to SageMath (after the arXiv preprint, 2026-10-16)

SageMath's `vertex_separation` (maintained by David Coudert, first author of the
branch and bound we compare against) is where exact pathwidth users already look.
The Sage hunt (`pathwidth_solver/bench/results/sage_hunt.csv`): of 381 benchmark
graphs, Sage's BAB settled 164 in 600 s; on the 217 it did not, ours proved 104
(loaded machine: to be confirmed by the quiet head-to-head).

- [ ] **Write to David Coudert first**, collegially: the results, the minor bound,
      and whether Sage would welcome the contributions below.
- [ ] **PR 1, small: the contraction-minor lower bound** as a self-contained
      function (Theorem 4.11, Lean: `pathwidth_gt_of_minorOf`), usable by Sage's
      existing BAB at once. Cython, doctests, Sage graph types.
- [ ] **PR 2: our corrected search as a new `algorithm=` option** of
      `vertex_separation`, beside "BAB", "MILP" and "exponential". Port the C engine
      (now called through ctypes) to Cython or a C extension Sage accepts; GPL is
      fine (our code is MIT).
- [ ] **Evidence for the reviewers:** the quiet-machine SageMath head-to-head
      (high-priority item above), and the arXiv preprint to cite.

## Contributing pathwidth to House of Graphs (2026-10-17)

House of Graphs (Coolsaet, D'hondt & Goedgebeur 2022, arXiv:2210.17253;
Devillez, D'hondt & Goedgebeur 2026, arXiv:2603.23070; both in `literature/`)
stores treewidth as an invariant, from a treewidth tester (their ref. [27]), but
**not pathwidth**. The 2026 paper puts treewidth as its second hardest
invariant, timing out on about 20% of graphs (~5,400). They say they prefer fast
compiled implementations.

How contributions work (2026 paper §4.1, §6.1; 2022 paper §6): **users do not
submit invariant values**; the server computes every invariant itself, under
a ~5-minute limit per graph, with invariant programs chosen and reviewed by
hand. They prefer compiled C/C++ with few dependencies and mature, tested
code. The 2022 paper invites "practical and well-tested programs to compute an
interesting graph invariant which is not on the House of Graphs yet".
Contact: Jan Goedgebeur (jan.goedgebeur@kuleuven.be); also Kris Coolsaet
(Ghent), Sven D'hondt, Gauvain Devillez (Mons).

Our evidence (first pass, 2026-10-18, `pathwidth_solver/bench/results/hog_pathwidth.csv`):
all 29,995 graphs at their 5-minute limit, pathwidth proved on 26,432, a
witness layout for every graph, zero conflicts with their treewidth, 1,948
proved where their treewidth timed out. Second pass on the 3,563 running.

- [ ] **A standalone pathwidth program in C** (high priority, today,
      2026-10-18): reads graph6 on stdin, one graph per line; prints the
      pathwidth, whether it is proved (refutation / bound / minor) or an upper
      bound, and a witness layout; a time limit; no Python, no networkx. Port
      the descent of `pathwidth/solve.py`, the bounds of `bounds.py` and the
      minor step of `minor.py` around the existing C engine
      (`closing_search.c`). Must reproduce the Python solver's widths.
- [ ] **Draft the email to Goedgebeur** (high priority, today): the program,
      the first-pass numbers above, the witness file, the paper. Send after
      the arXiv preprint, so they have something to cite.
- [ ] **Offer our values as a cross-check**, not a substitute: the server
      recomputes, and our witnesses let them verify every upper bound.
- [ ] Companion to the SageMath contributions above.

## W4: search for a width-26 layout (2026-10-15)

- [ ] **Try the finding side on W4** (VLSI, 202 nets, dataset class pwc-04432;
      26 <= pw <= 27, i.e. 27 or 28 tracks). The two running attempts
      (`reports/scratch/w4/`) both try to refute 26; after 2.5 days nothing
      found suggests 27 is optimal but proves nothing. A dedicated layout search
      for width 26 (simulated annealing as for myciel7,
      `reports/scratch/minor_certificates/vsanneal.c`, or restricted searches
      from varied orders), one core, an hour or two, when cores are free: a
      width-26 layout settles W4 at 26 (27 tracks); none adds evidence for 27.

## A parameterised bound for our search (high priority, 2026-10-14)

- [ ] **Can our corrected search be proved FPT, or at least XP, in the width k,
      and does it improve on what is known?** Empirically, on the Rome graphs,
      nodes ~ 10^(1.75 + 0.00705 n w) (Section 5, Figure 5.1): exponential in
      n*w, not fixed-parameter. Theory: Bodlaender & Kloks (1996) decide
      pathwidth <= k in linear time with a 2^O(k^3) constant
      (`reports/fpt_theory_practice_gap.md`); later improvements exist (Fuerer
      and others) and must be checked before any claim. Steps:
      1. survey the parameterised pathwidth literature for the current best
         bounds (FPT and XP), with what we hold and what to fetch;
      2. bound our search's state space: its states are vertex sets S with
         |N(S) \ S| <= k, each fixed by its boundary and a choice of the
         components of G - N[S] it contains, which suggests an n^O(k) (XP)
         bound; prove it, and check it on small graphs first;
      3. ask whether the corrected dominance rules (and the minor step) cut
         the state space to f(k) * poly(n), which would be FPT; a new idea
         would be needed, so scope it before investing;
      4. if a theorem results, formalise it in Lean beside Search/ and decide
         whether it belongs in this paper or in paper 2.

## The grid theorem in Lean (high priority, 2026-10-14)

- [x] **Done 2026-10-14** (`lean/MOSPFormalization/Grid.lean`, `pathwidth_grid`, commit cda02ac3b; 1x1 is the one exception, pathwidth 0; in the paper as Appendix A `grid`). **Prove in Lean that an (h, w)-grid has pathwidth min(h, w)** (Ellis &
      Warren 2008, Theorem 4.1, via node search: Lemma 4.1, the sweep, gives
      ns <= min(h, w) + 1; Lemma 4.2 the lower bound). 41 VSPLIB grids (sides
      14-54) are now settled by citing this theorem
      (`reports/scratch/grids_theorem/grids.csv`, each grid checked by
      isomorphism, each witness layout checked); with the Lean proof they rest
      on Lean like the rest of the paper. The upper bound is the row-by-row
      layout; the lower bound is the hard half (Ellis & Warren's search
      argument, or a separator / isoperimetric argument, or the grid minor
      structure). Check the statement on small grids first, as usual. Then give
      the dataset a provenance for it (e.g. `certified:theorem`, citing the Lean
      name) and update Table 5.2's grid row.

## From the owner's annotations (2026-10-13)

- [ ] **Lean: the certificate checker's acceptance condition** (medium priority). The checker
      (Section 5.4) accepts a refutation when every discarded move is justified
      by a checked step and the justifications are acyclic. That this makes the
      certificate a proof is argued on paper only (conclusion, Limits). Formalise
      it beside `lean/MOSPFormalization/Search/`.
- [ ] **Read every citer in full.** Of the 38 works citing the CP paper 24 were
      read in full, and of the 103 citing only the thesis, 32 (Appendix B,
      prior reports). Read the remaining 14 + 71: obtain the open ones, list the
      rest for fetching, and record any mention of the definite move's error.

## A replication notebook

- [ ] **"This entire paper can be read and replicated on a Python (with C calls)
      Jupyter notebook."** One notebook that follows the paper section by section:
  - the worked example of Figure 1.1;
  - the equivalences checked by brute force on small graphs (`complex_check.py`);
  - the census of names (from the cached OpenAlex data);
  - the counterexample and the repaired search (Python reference and the C
    through `native.py`);
  - the 34-customer wrong optimum with both searches, the SAT check and the DRAT
    check;
  - the cost tables, the re-certification records and the dataset checker.

  Every number and figure is regenerated from the recorded data, with the
  expensive runs (the split refutations, the full benchmarks) read from their
  CSVs rather than rerun. It ships in the paper's repository, and the paper
  says so in its "Data, code and proofs" statement.

## Data and proofs

- [x] **The trimmed DRAT proof for the 34-customer instance** (2026-10-11):
      `data/false_refutation/drat/false_refutation_34__k5.core.drat.xz`, 27 MB,
      with its SHA-256 and `check_proof.sh` (rebuilds the CNF, `s VERIFIED` in 35 s).
- [x] **The never-certified MOSP values** (closed 2026-10-12). `Random-125-125-2-3_0`
      = 21 certified 2026-10-09 (k = 20 refuted, 9,665 tasks, 1,128 core-hours);
      `Random-125-125-2-2_0` = 25 certified 2026-10-12 (k = 24 refuted, 17,001
      tasks, 7.38 × 10¹² nodes, 2,231 core-hours). Both provenances upgraded;
      the corpus is 6,376 of 6,376; dataset and paper updated.
- [ ] **Open question: can the published rules fail with the better move
      on?** The 34-customer instance fails only with the better move off.
      Restart `false_refutation_hunt.py` with fitness on the better-move
      configurations if we want the answer.

## Bug: legacy pathwidth_fpt on trees (found 2026-10-18)

- [ ] **`fixed_parameter_algorithm/pathwidth_fpt.compute_pathwidth_fpt` returns
      pathwidth 1 for every tree over 18 vertices** (e.g. `balanced_tree(3, 3)`,
      pathwidth 3). Found by the random-intersection report's agent, not yet
      reproduced or fixed. Below 19 vertices it delegates to the exact DP, so the
      fault is in the branch and bound or its pendant-removal preprocessing
      (removing degree-1 vertices does not preserve pathwidth on trees). Not
      used by `pathwidth_solver/` or any paper result; check what still calls it
      (`customer_inter/`, tests) and add a tree regression test.

## Repository housekeeping

- [ ] **Apply item 09's proposed `CLAUDE.md` blocks** (`solver_fix.md`, "For
      CLAUDE.md"), and record the wrong-optimum instance, Appendix D and the
      DRAT proof in `CLAUDE.md`.
- [ ] **Push** (`git status` before each push).
- [x] **Two new rows in Table 1.1** (2026-10-09): the vertex search of Bienstock,
      Robertson, Seymour & Thomas (1991) and the maximum wavefront of Kumfert &
      Pothen (1997, proved in Lean, `Complex/Wavefront.lean`); Figure 2.1 redrawn.

## Paper 2 (idea, 2026-10-09)

- [ ] **Read the four surveys** in `paper2/` (trees and sparse classes; products
      and grids; intersection and perfect classes; random and extremal results)
      when they arrive, and decide whether there is a paper in "the applied
      mathematics of pathwidth on special graph classes".
