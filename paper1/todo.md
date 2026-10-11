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
