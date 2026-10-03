# loop0008 progress

Plan: strengthen paper 2, "The pathwidth complex", toward a first full draft.
Items are in `iterations.md`, rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0008/gate.py`.

Current: 3/9 SOLVED

**Correction (iteration 3, 2026-10-03).** Our notes said the definite move
"is" a depth-1 commitment, Tamaki's commitment lemma
(`pathwidth_solver/PLAN.md`, `CLUSTER_PAPER_PLAN.md`,
`literature/pathwidth_solvers_README.md`). That is wrong in two ways.
- A depth-1 commitment is a move with `open(q, S) ≤ 1` (`isCommittable_insert_iff`).
- The published Theorem 1 checks the commitment condition at the endpoints
  only, and it is false.
Only the *repaired* rule is the commitment lemma, at depth `close(q, S)`.
The three notes are corrected in place.

Also recorded in `prior_art_counterexample.md`: the repair's soundness theorem
is **known**. It is Kitsunai et al. (2016), Lemma 1, after Tamaki (WG 2011), and
our Theorem 4.7 proof is theirs. The paper must not claim it as new.

**Correction (iteration 2, 2026-10-03).** Item 01 recorded that Fink (2012)
restates CP Theorem 1 "with the CP premise". It does not. Fink's `f(α_j, S)`
counts only dominated customers `α_i ∉ S` with **`i < j`** (p. 27), so `q`
itself is not counted and the premise is strictly stronger. `cexGraph` does
not refute it under any labelling. A 15-customer variant (one more twin of 3
and 4) does: `fink_theorem1_false` in `Search/ChuThesis.lean`. Fixed in
`paper2/prior_art_counterexample.md`, in the header note, the citer table
row, the verdict and "For the paper". The iteration 1 text below is left as
written.

## Setup — 2026-10-03

- **Baseline.** loop0007 is complete:
  - both solvers apply the repaired rules by default;
  - 111 of the 115 values that rested only on the customer search are
    re-refuted, all unsat, so no certified value changed;
  - `Search/Split.lean` proves the root split sound.

  The one `sorry` in code is the §24 conjecture (`Sandwich.lean`).
- **In flight.** `paper2.solver_fix_split` has a five-day budget to
  2026-10-08, 20 workers, `--parallel`, on the four open 125 × 125 instances:
  `Random-125-125-2-4_0`, `-4-4_0`, `-2-1_0` and `-2-5_0`. Its PID is in
  `paper2/data/solver_fix_split.pid`. Do not touch it.
- **Novelty check so far.** `paper2/prior_art_counterexample.md`: no correction
  found. Chu's 2011 thesis restates Theorem 1 unchanged and states the better
  move with a different premise, and both are false on `cexGraph` by brute
  force. Item 01 widens this, and item 02 puts it in Lean.
- **Driver.** This loop's driver retries a session once, after 300 s, when it
  ends on an error without marking its item. loop0007's last session was lost
  to a network error.

---

## Iteration 1 — 2026-10-03 00:55

### Completed
- **Item 01, the prior-art sweep of every citer.** The table and verdict are
  in `paper2/prior_art_counterexample.md`, section "Every citer, swept". The
  regenerate command is `python3 -m paper2.prior_art_sweep` (new); it writes
  `paper2/data/prior_art/citers.csv`, `hits.txt` and the index caches.
  - **Sources.** OpenAlex, Semantic Scholar and OpenCitations, for the CP
    paper, the thesis and its IJCAI 2013 abstract. Crossref's cited-by list is
    open only to its members; its public count is 15.
  - **Coverage.** 144 distinct works. 38 cite the CP paper, after dropping the
    thesis itself, a proceedings-volume duplicate and one false link; 24 of
    them were read in full (63%). 103 cite only the thesis or its abstract;
    32 were read (31%).
  - **Verdict:** we found no prior report of the error.
    - **A third restatement turned up.** Fink (2012, ICMC-USP PhD thesis,
      pp. 27–28) restates CP Theorem 1 with the CP premise, as true. It is
      saved as `literature/fink_2012_phd_thesis_mosp_novas_contribuicoes.pdf`.
    - **Three works use an implementation of the rules**, and none reports a
      failure. Chu et al. (2010, 2012) use dominance-breaking constraints in a
      CP model. Frinhani et al. (2018) ran the original C code to get the
      optima that Martin, Yanasse & Pinto (2022) reuse.
    - **Related.** Beck, Kuroiwa, Lee, Stuckey & Zhong (CP 2025), Prop. 3 and
      Example 6: mutually dominating transitions can make a satisfiable
      instance unsatisfiable. That is the general form of the `better_move`
      cycle bug, not the premise flaw.
  - **Unread.** 14 CP citers, plus Gange, Chu & Stuckey (2019), are listed in
    `literature/MISSING.md`. The first to fetch is De Giovanni et al. (2013,
    *ITOR*), an exact method for gate matrix connection cost.
  - **Fetches.** Every PDF fetched by hand is recorded with its URL in `HELD`
    in the script, all fetched 2026-10-03. The downloads sit in
    `paper2/data/prior_art/fulltext/`, which is git-ignored (about 55 MB).
- **No published claim of ours was wrong.** The earlier table's Semantic
  Scholar–only row is superseded by the new section and left in place as the
  record of the first check.
- **The gate passes** (`python3 Ralph_Loops/loop0008/gate.py`): lake build is ok, one `sorry` (the §24 conjecture), MOSP pytest 1,361 passed, pathwidth_solver pytest 114 passed.
- **The split run is clean.** `paper2/data/solver_fix_split.log` has no `!!!`
  line, checked at 00:33 and 00:51.

### Blockers
- None for the item.
- Some author pages, Stuckey's site and Edinburgh's repository, refuse
  scripted fetches. WebFetch got four Stuckey PDFs before the site flagged it.

### Next
- **Item 02**: Chu (2011) Theorem 6.3.8 is false, in Lean.
- The paper can also cite Fink (2012) as a restatement refuted by the same
  graph. When item 02 updates `prior_art_counterexample.md`, mention Fink
  there.

---

## Iteration 2 — 2026-10-03 01:55

### Completed
- **Item 02: Chu (2011) Theorem 6.3.8 is false, in Lean.** The new file is
  `lean/MOSPFormalization/Search/ChuThesis.lean`. It is imported by
  `MOSPFormalization.lean` and listed in `paper2/axiom_check.lean`. There is
  no `sorry`, and the axioms are `propext`, `Classical.choice` and
  `Quot.sound` only. The thesis wording is quoted from the held PDF: §6.3,
  Definition 6.3.4 (p. 141), Theorem 6.3.6 (p. 142), Theorem 6.3.8 (p. 143),
  printed page numbers.
  - `chuThesis_theorem638_false` and `chuThesis_theorem638_false_literal`
    state 6.3.8 as published and refute it, in the form of
    `PublishedTheorems.lean`. The witness is S = {2}, r = 3, q = 0, k = 6,
    with close(0, S) = 3 ≥ 2 = open(0, S ∪ {3}). The "no extension" half is
    the CP counterexample's own `cex_not_solvable_child`.
  - The literal reading follows from the unclosed one, since its premise is
    weaker. `chuThesis_theorem638_literal_witness` also proves the brute
    force's literal-only witness, S = {1}, r = 6, q = 12. Its unclosed count
    is 1 < 2, and an invariant family of four states blocks it.
  - **Theorem 6.3.6** is recorded as `chuThesis_theorem636_false(_literal)`.
    These restate `chuStuckey_theorem1_false(_literal)` under the thesis's
    number, with a docstring saying it is CP Theorem 1 verbatim.
- **Fink (2012), added beyond the item because item 01's claim about it was
  wrong** (correction at the top of this file). Fink's Teorema 1 counts only
  dominated customers with index `i < j`, so its premise is strictly stronger
  than the CP premise, and `cexGraph` does not refute it under any labelling.
  - **A random search found nothing.** It covered about 41,700 graphs on
    6–12 vertices, on 3 cores for 300 s, at every k. The script was not kept.
  - **A hand-built gadget does refute it.** `finkGraph` is `cexGraph` plus a
    third twin of 3 and 4, with labels 0 and 14 swapped. At S = {2, 3},
    q = 14, k = 6, `f = {0, 4}` and open = 2, with a 12-state invariant
    family. The Lean theorem is `fink_theorem1_false`.
  - **An independent brute force checks it.** `python3 -m paper2.fink_check`
    (new, 0.3 s) finds 3 failing states on `finkGraph` and none on `cexGraph`.
    It is tested by `tests/test_fink_check.py` (3 tests).
- **Downstream text.**
  - `paper2/prior_art_counterexample.md` has a new section, "The thesis's
    theorems in Lean", with a theorem table. The old "has not been written"
    bullet is struck, and the Fink corrections are made.
  - `paper2/revised_algorithm.md` now has:
    - the header file list (nine files) and the thesis page convention;
    - §4.1, which says the thesis restates both rules;
    - §4.3.2, which adds the thesis citation for 6.3.6 and the Fink paragraph;
    - §4.3.4, with a new paragraph "The thesis's form", quoting 6.3.8 and
      giving its refutation.
- **The gate passes.** Lake build is ok, the one `sorry` is the §24
  conjecture, MOSP pytest gives 1,364 passed, and pathwidth_solver pytest
  gives 114 passed. `ChuThesis` takes 212 s to build, mostly the
  `decide +kernel` on the 15-vertex family.
- **The split run is clean.** No `!!!` line in
  `paper2/data/solver_fix_split*.log`, checked at 01:24 and 01:55.

### Blockers
- None.

### Next
- **Item 03**, section 4 in pathwidth language.
- The rule-by-rule text should note that each published restatement (CP,
  thesis and Fink) has a refuting graph. Fink's needs one more vertex.
- The open question whether a random search at 13–16 vertices finds Fink
  failures without the twin gadget is not important for the paper.

---

## Iteration 3 — 2026-10-03 02:30

### Completed
- **Item 03: section 4 in pathwidth language.** It is a new **§4.7** at the
  end of `paper2/revised_algorithm.md`, "The search in pathwidth language".
  - **Why at the end.** Inserting it after §4.2.3 would have renumbered every
    lemma that other documents cite. Pointers to it were added in §4.1, after
    Theorem 4.3, and after Theorem 4.7. Its results continue the numbering:
    Lemma 4.20 to Lemma 4.24.
  - **Contents.**
    - §4.7.1: the dictionary, as a table with Lean names. Open stacks are the
      border `d(T) = |N(T)|` of a forward prefix, the free closure is the full
      set of Suchan & Villanger, and `Sol_k(∅)` is `vs ≤ k − 1`.
    - §4.7.2: the skeleton is Kobayashi, Komuro & Tamaki's (SEA 2014)
      Algorithm 1, compared with Coudert, Mazauric & Nisse.
    - §4.7.3: each rule as a layout lemma with its Lean theorem and its
      published counterpart: the free move, the definite move (published,
      repaired, depth 1), the subset rule, the better move, the old move and
      the memo.
    - §4.7.4: a table of what is known and what is not.
- **The main finding: the repaired definite move is a known theorem.** It is
  Tamaki's commitment lemma, Kitsunai et al. (Algorithmica 2016) Lemma 1,
  p. 142, and our Theorem 4.7 proof is theirs. The published Theorem 1 checks
  the commitment condition at the endpoints only. By their Corollary 2
  (pp. 148–149), the published premise does guarantee a commitment, but to the
  least-border set W, not to the child. In the counterexample W = {2, 3, 4}.
  - A second repair that commits to W is **proposed, not built**.
  - What we found in no held paper:
    - the matching test for this target (Theorem 4.8), which is a special case
      of their minimum-separator method;
    - the subset rule, the better move and the old move;
    - the memo combined with the old move.
  - Every published pathwidth greedy rule of this kind lies in the region
    `open ≤ 1`. That covers Coudert et al.'s greedy step, Suchan & Villanger's
    Rule 1 and Kobayashi et al.'s depth-1 commitments. In that region the
    published definite move is right.
- **Lean: a new file, `lean/MOSPFormalization/Search/Layout.lean`.** It is
  imported by `MOSPFormalization.lean`, and its 13 theorems are listed in
  `paper2/axiom_check.lean` under "loop0008 item 03". All print `propext`,
  `Classical.choice` and `Quot.sound` only. The theorems are:
  - the dictionary: `opened_sdiff_eq_boundary`, `openStacks_eq_card_boundary`,
    `opened_eq_union_boundary`, `stepCost_eq_card_boundary_add_one` and
    `mem_cl_iff`;
  - the commitment lemma, `solvable_of_isCommittable`;
  - `isHereditarilyDefinite_iff_isCommittable`;
  - `solvable_cl_insert_of_hereditarilyDefinite'`;
  - `isDefinite_iff_endpoint`;
  - `isCommittable_insert_iff` (depth 1 means `open ≤ 1`);
  - `isGreedyStep_iff` (Coudert et al.'s greedy step means `open ≤ 1`);
  - `exists_isCommittable_of_isDefinite`;
  - `cex_isDefinite_not_isCommittable` and `cex_isCommittable_234`.

  No existing proof was edited. The file builds in seconds.
- **Downstream text.**
  - `prior_art_counterexample.md` has a dated note: the repair's soundness is
    known, and the paper may claim the counterexample, not the repair.
  - `plan.md` §4 marks the to-do as done.
  - The three wrong notes on depth-1 commitments are corrected (see the
    correction at the top of this file).
- **Sources.** Six held papers were read in full or in their relevant
  sections with `pdftotext` on 2026-10-03. Nothing was fetched.
  - Coudert, Mazauric & Nisse, SEA 2014 and JEA 2016;
  - Kobayashi, Komuro & Tamaki, SEA 2014;
  - Kitsunai et al. 2016;
  - Suchan & Villanger 2009;
  - Bodlaender et al. 2012.

  Tamaki (WG 2011) is not held. It is cited through Kitsunai et al., who
  restate it with proof.
- **Split run.** Clean: no `!!!` line, checked at 02:23.
- **The gate passes** (`python3 Ralph_Loops/loop0008/gate.py`): lake build is
  ok, the one `sorry` is the §24 conjecture, MOSP pytest gives 1,364 passed,
  and pathwidth_solver pytest gives 114 passed.

### Blockers
- None.

### Next
- **Item 04**, the dataset.
- §4.7 changes what section 4 can claim. Item 08 (LaTeX) should credit Tamaki
  and Kitsunai et al. for the repair's soundness, and present the counterexample
  as "Theorem 1 drops the interior condition of a commitment".
- Optional, not in any item: the retargeted repair (commit to W). A cheap first
  step is to measure, on the failing candidates of `solver_fix.md` items 04 and
  08, how many nodes committing to W would save. W always exists there, by
  Proposition 4.23.
