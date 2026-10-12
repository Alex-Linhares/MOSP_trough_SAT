# *The pathwidth complex*: to do

Started 2026-10-09. Check items off as they are done.

## Before posting on arXiv

- [ ] **Affiliations and emails** for both authors. They are boxed placeholders in
      `latex/main.tex`.
- [ ] **The paper's repository, at least a stub**, with the data and checkers.
      Then replace the URL placeholder in the "Data, code and proofs" statement
      (`latex/sec7_data.tex`), and retarget `\repofile` in `latex/main.tex` to
      the repository's layout (see `plan.md`, remaining work item 6).
- [ ] **Re-check the novelty claims.**
  - [ ] Read the 14 unread works that cite Chu & Stuckey 2009, listed in
        `literature/MISSING.md` (item 01 of loop0008). De Giovanni et al.
        (2013, *ITOR*) first.
  - [ ] Keep the wording "we found no prior report", never "first"
        (`prior_art_counterexample.md`).
- [ ] **Decide whether to write to Peter Stuckey** (and Geoffrey Chu) before
      the counterexample and the 34-customer wrong optimum become public.
- [ ] **arXiv endorsement.** Check whether we need one for cs.DS.
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

- [ ] **The solver claim: head-to-head against SageMath.** "Best" would hold
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

- [ ] **Rome graphs, a longer timeframe.** The Rome graphs (Di Battista et
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
- [ ] **Lean, the full table.** Extend the `WrongOptimum.lean` model with the
      better move as published, prove its runs are `Exec` runs with that
      filter, and check every row in the kernel (each run is 25-100 s of kernel
      time; the modelling is the work). Rows without the definite move already
      follow from the soundness theorem.
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
- [ ] **Independent checks before recording anything.** SAT (with DRAT) or a
      rule-free run on the minors of Random-125-125-2-1_0 and 2-3_0, and on
      the 110-vertex minor of myciel7. The 2-3_0 minor already holds rule-free;
      2-1_0 and myciel7 rest on our corrected rules so far.
- [ ] **myciel7.** Settle 71 against 72 (Coudert et al. 2016 leave it open at
      pw <= 72). If it is new, say so carefully, after the literature check.
- [ ] **Lean.** Pathwidth is minor-monotone: contracting an edge never increases
      pathwidth (Fellows & Langston 1987, Lemma 4.2, for layout cost; nothing
      on contraction or minors in `lean/MOSPFormalization/` yet). Prove it, and
      state the bound as a theorem: pathwidth of a contraction <= pathwidth.
      Then a minor certificate is a contraction sequence plus a refutation.
- [ ] **A checkable certificate.** The minor certificate is the contraction
      sequence (checkable by anyone) plus a refutation on the small graph (a
      DRAT proof, or our search certificate of Section 5). Ship both for every
      value certified this way.
- [ ] **Write it up.** A subsection of Section 5 ("A lower bound from minors"),
      the myciel6 passage rewritten (no longer a loss), the corpus values it
      re-certifies cheaply, the cost of 2-3_0 falling from 1,128 core-hours to
      seconds, and an honest line on what remains open (2-2_0: every contraction
      up to 95 vertices still admits 24).
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
- [ ] **The never-certified MOSP values.** `Random-125-125-2-3_0` = 21 was
      **certified on 2026-10-09** (k = 20 refuted, 9,665 tasks, 4.25 × 10¹²
      nodes, 1,128 core-hours). `solutions/Random-125-125-2-3_0.json` still says
      `solution`; upgrade its provenance to `certified:refutation` (owner).
      `Random-125-125-2-2_0` = 25 is still in flight, with the watcher continuing
      to 2026-10-29. When it closes, update Section 5, Table B.1 and the
      conclusion (`python -m paper1.solver_fix_split --tables`).
- [ ] **Open question: can the published rules fail with the better move
      on?** The 34-customer instance fails only with the better move off.
      Restart `false_refutation_hunt.py` with fitness on the better-move
      configurations if we want the answer.

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
