# loop0008 progress

Plan: strengthen paper 2, "The pathwidth complex", toward a first full draft.
Items are in `iterations.md`, rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0008/gate.py`.

Current: 6/9 SOLVED

**Correction (iteration 6, 2026-10-03).** Three small faults in section 2's
record; none changes a conclusion.
- `paper2/relevance.py`'s docstring said the phrase rule was "the whole of
  the method". The published counts come from the per-work labels and
  `keep_pathwidth`. The two readings disagree on 157 of the 700 labelled works.
  The docstring is corrected.
- Pathwidth's 1,213 counts one OpenAlex record twice (`W4416062387`), so it is
  1,212 distinct works.
- `popularity.md`'s citation column is from 2026-09-17, and the network is
  from 2026-09-29. Four counts differ by one.

The last two are recorded in `popularity.md`, "Notes for the number audit",
for item 07. The claim "MOSP ranks fourth" depends on the labels: under the
phrase rule it is fifth. A dated note is added beside the claim.

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

---

## Iteration 4 — 2026-10-03 05:05

### Completed
- **Item 04: section 4's dataset, defined and priced.** It is written up in
  `paper2/dataset.md`.
  - **Code.** The builder is `paper2/dataset.py`, with stages `index`,
    `values`, `run`, `write`, `tables` and `price`. The independent checker is
    `paper2/dataset_check.py` (standard library only, nothing imported from
    the repository). The price is `paper2/dataset_price.py`. Tests are
    `tests/test_dataset.py` (5) and `tests/test_dataset_check.py` (10).
  - **Data.** Everything is under `paper2/data/dataset/`, about 21 MB. The
    dataset itself is `pathwidth_dataset.jsonl.gz`.
- **Scope.** Every collection in `benchmarks/README.md` §1 plus the MOSP
  corpus: 21,754 instance files in 20 collections.
- **Deduplication.** nauty certificates, across collections and across
  problems, give **17,714 classes**.
  - The MOSP corpus is 3,667 classes, matching `ml_nature.md` §1.
  - Rome: 11,534 files, 11,199 classes. VSPLIB trees: 50 files, 28 classes.
    Control-flow graphs: 1,817 files, 1,070 classes.
  - 78 PACE graphs over 5,000 vertices are deduplicated by file content only.
- **Format.** One JSON line per class: graph, width, provenance, evidence,
  witness layout, the value under each of the nine exact problems, members
  with their isomorphism map to the representative, and, for
  `certified:bound`, a minor certificate.
- **The check.** `python paper2/dataset_check.py --sources` reports **0
  failures on 16,949 records**.
  - Provenance: 12,552 `certified:refutation`, 3,535 `certified:bound`, 862
    `solution`.
  - Every bound certificate replays.
  - All 20,987 member source files are re-read by the checker's own readers
    and mapped onto their record by isomorphism.
- **Published values.**
  - All 84 Small graphs agree with Mallach (2018) Tables 4–5.
  - **10 of 11 VLSI circuits certify at their published best-known tracks.**
    W4 is open at 28 against 27.
  - All 11 certified Carvalho & Soma values agree with the PT-MOSP sheet.
    The Random-150-150-10 class mean is 123.9, the same as S1's OPT.
  - One upper bound beats the published best: Random-200-200-6-7 at 119
    against 120.
- **Finding: Carvalho & Soma's files are customers × patterns.** The
  Chu & Stuckey files beside them in PT-MOSP are patterns × customers.
  - The evidence is S1 Table's MOSP-graph density `D` and the per-instance
    values: transposed, Random-150-150-10-2 certifies at 127 against a
    published 124.
  - The first pass read them transposed; the published-values comparison
    caught it and the 150 were rerun.
  - Our Chu & Stuckey reading is confirmed against all 40 S1 class means.
  - **Frinhani large's orientation is unsettled**: `D` points both ways. It is
    read as its description says, and none of its values is certified.
- **Run.** 5.7 core-hours on 4 workers, 03:15–04:55, of which 1.2 went on the
  wrongly oriented first pass.
  - 11,527 witnesses were regenerated at the recorded width (satisfiable side
    only).
  - First full runs of 1,756 classes at 30 s each: Small, VLSI, control-flow
    graphs, PACE within the engine, Carvalho & Soma.
- **Price**, by collection, in `dataset.md` §6.
  - One more budget step for every open graph class within the engine costs
    at most 500 core-hours. On the Rome record, each step closes about 40% of
    what it attempts.
  - The MOSP corpus's last five are each priced in the hundreds of
    core-hours.
  - Carvalho & Soma beyond density 10, Frinhani, and the 154 classes above
    1,024 vertices are out of reach. The cost model is extrapolated past
    125 and is labelled so.
- **Found while pricing: `Random-125-125-2-4_0` is re-certified.** The split
  run refuted k = 23 at 02:55 today, 154.1 core-hours over 1,686 tasks, and
  the value is unchanged. `paper2/solver_fix.md` item 09 still says
  "partial". This is not a wrong claim, only an out-of-date one; item 07 (the
  number audit) should update it. Three instances remain in flight.
- **Pointers added**: `plan.md` §4 and `benchmarks/README.md` "Next".
- **The gate passes** (`python3 Ralph_Loops/loop0008/gate.py`): lake build is
  ok, the one `sorry` is the §24 conjecture, MOSP pytest gives 1,379 passed,
  and pathwidth_solver pytest gives 114 passed.
- **Split run.** Clean: no `!!!` line, checked at 03:20, 04:08 and 05:01.

### Blockers
- None for the item. Left beyond its budget:
  - the next budget steps (about 500 core-hours for the graph sets);
  - the in-flight and open MOSP values;
  - licences and the four requests (`benchmarks/README.md` §2);
  - one Rome witness (`pwc-05529`, certified 9) that did not come back in
    120 s.

### Next
- **Item 05**, certificates for the repaired rules. Its proof object is what
  the dataset's 12,552 `certified:refutation` records lack.
- **Item 07** should take `Random-125-125-2-4_0`'s re-certification into
  `solver_fix.md`, and can use `paper2/data/dataset/tables.md` and `price.md`
  as the sources for the dataset numbers.
- **Item 08** (LaTeX) can take section 4's dataset paragraph from
  `dataset.md` §7.

---

## Iteration 5 — 2026-10-03 06:10

### Completed
- **Item 05: certificates for the repaired rules.** It is written up in
  `paper2/certificates.md`.
  - **The emitter.** `learning/search_certificate.py` gains `emit(...,
    repaired_rules=True)`. Each definite step is now `["definite", q, M]` and
    each better step `["better", r, q, M]`, where `M` is the
    `HasDefiniteMatching` witness: pairs `[d, s]` matching freed customers to
    new stacks. The better move's matching is taken at `cl(S ∪ {r})`.
  - **`start`.** A new option roots the tree at a closed set. The certificate
    then claims "no solution extends S".
  - **Defaults.** The emitter's defaults are unchanged, so §32's numbers and
    tests stand. §32's checker `check` now honours `start`. It still checks
    published premises only, and its docstring says so.
  - **Fidelity.** Status and branch count equal
    `decide(native=False, repaired_rules=True)` at every `k`: 2,463
    refutations on 300 random instances, three configurations. They equal the
    C (memo off) on 968 decisions.
- **The checker**, `paper2/certificate_check.py`, uses the standard library
  only, and a test parses its imports.
  - It recomputes `N[c]` and the SHA-256 from the matrix, and walks the tree
    with an explicit stack.
  - It verifies each matching: distinct `d`, distinct `s`, `d` freed,
    `s ∈ o(d)`, and at least `open − 1` edges.
  - It checks premise 3, the subset rule, free moves, `Q(S)`, memo, and
    acyclic cover chains.
  - It rejects any definite or better step without a matching.
  - CLI: `python paper2/certificate_check.py BUNDLE.json.gz`.
- **Results** (`paper2/data/certificates/tables.md`), with a 60 s emission
  budget on 4 workers.
  - **41–75 customers.** 141 of 151 verify under `default` and 140 under
    `csearch`; 0 are rejected. The 141 are the same set §32 verified under the
    published rules. The `csearch` gap is `Random-75-75-4-1_0`, which crossed
    60 s; `default` verified it in 46 s. The ten unknown are `SP3`, `SP3_0`,
    `Random-75-75-2-{1..5}_0` and `Random-75-75-4-{3,4,5}_0`.
  - **9–40 customers.** All 6,135 verify under both configurations.
  - **Size and time, `csearch`, all 6,275 verified.** 35.5 MB gzipped,
    checked in 147 s, 44 µs per node. The largest certificate is 11.6 MB
    gzipped and the slowest check takes 68 s.
  - **Matchings.** 215,258 edges in all. Most definite steps carry an empty
    matching, because `open ≤ 1` there.
- **Hand-built failures** (`failures.json`, `bundles/`).
  - **`DEFINITE_CEX`.** On both graphs, from `start = {2}`, the published
    rules emit an exhaustive `unsat` tree, which is a false claim.
    - §32's published-premise checker **accepts** it.
    - The new checker rejects it: "no matching witness".
    - With a largest matching attached it still rejects: "matching has 1
      edges, open − 1 = 2".
    - The repaired emitter from {2} finds a solution of cost ≤ k.
  - **Corrupted matchings.** Seven single corruptions of Warwick 877's
    repaired certificate are all rejected, as are five tree corruptions.
  - **Bug B.** The rule-order cycle, emitted under the repaired premises, is
    still caught as a covering cycle.
- **C emitter: proposed, not built** (`certificates.md` §5).
  - A binary stream of about 10 bytes a node, with the matching copied from
    `has_definite_matching`'s `owner[]`.
  - It must run with the memo off.
  - Per-task certificates would come via `start` and the root split.
  - The 125 × 125 refutations would be about 250 GB: possible, not shippable.
- **Downstream text.** `revised_algorithm.md` §4.6.3 now says "the
  certificate route: done", and `plan.md` has a pointer.
- **Tests.** `tests/test_certificate_check.py` has 20.
- **The gate passes** (`python3 Ralph_Loops/loop0008/gate.py`): lake build is
  ok, the one `sorry` is the §24 conjecture, MOSP pytest gives 1,399 passed,
  and pathwidth_solver pytest gives 114 passed.
- **Split run.** Clean: no `!!!` line, checked at 05:33, 05:48 and 06:10.

### Blockers
- None for the item.
- Left beyond it:
  - the ten 75-customer instances, which need the C emitter;
  - checking the graph records of the dataset, which needs an edge-list reader
    in the checker;
  - a Lean statement of the checker's acceptance condition, which is argued
    on paper in `certificates.md` §2.

### Next
- **Item 06**, section 2: three figures and the method paragraph.
- Item 08 (LaTeX) can take section 4's proof-object paragraph from
  `certificates.md` §1–§4.
- Item 07 should check the numbers here against `tables.md`.

---

## Iteration 6 — 2026-10-03 06:47

### Completed
- **Item 06: section 2's three figures and the method paragraph.** Both are in
  `paper2/popularity.md`, under a new heading "For the paper".
- **The three figures.** These are the name-usage bars, the rate heatmap and
  the citation network, as `plan.md` suggested. Each has a paragraph saying
  why it was chosen and why the alternative was not:
  - the scatter is secondary, mixes fetch dates and lacks one point;
  - the small multiples take three times the space and hide the order in time;
  - the citers by decade repeat Figure 2.2.

  Draft captions are included.
- **Print versions.** A new script, `paper2/section2_figures.py`, redraws all
  three from the 2026-09-29 caches with no network access, as
  `paper2/figures/sec2_fig{1_name_usage,2_timeline,3_citation_network}.pdf`,
  with PNG previews. They are:
  - vector, with TrueType fonts embedded;
  - at most 6.5 in wide (468.8, 456.8 and 443.6 pt);
  - no text below 7 pt;
  - without titles, which go in the captions.

  The heatmap now uses a single-hue scale that prints in grey. Discipline is
  shown as a coloured tab, with black label text. The network labels point
  outward and no longer collide. Each figure was looked at after rendering.
  The palette passed the dataviz validator; orange's low contrast is relieved
  by the direct labels.
- **Caption numbers.** The same script's `numbers()` recomputes every number
  the paragraph and captions quote. `tests/test_section2_figures.py` pins
  them in 3 tests, against the published table: 2,271 hits, 700 labelled,
  1,593 relevant, 844 / 269 / 74 / 63 / 6, and 1,014 / 311.
- **The method paragraph** is drafted as quoted prose. It covers:
  - the OpenAlex queries and the four-field restriction;
  - stem matching, with examples;
  - fetching every hit, the 700 per-work labels and the pathwidth rule;
  - the corrected counts and the two changed conclusions;
  - the limits.
- **Sensitivity.** The labels were judged by one model-assisted session with
  no second labeller, and the text says so. The mechanical phrase rule
  (`relevance.relevant`) is used as a second reading:
  - it agrees with the labels on 543 of 700 works (78%);
  - pathwidth is more than 3 times the other eleven names under both
    readings (3.2 and 3.6);
  - the three empty names stay empty, apart from one 5G false positive;
  - MOSP's rank moves from 4th to 5th, so the paper should say "one of the
    better-used names".
- **Pathwidth rule.** It keeps 266 works whose cached text lacks the word.
  261 of them have no abstract in OpenAlex's response and are kept by their
  theory subfield. The rule also misses at least two real 1991 papers.
- **Corrections** (top of this file): the `relevance.py` docstring is fixed,
  and two number drifts are handed to item 07.
- **`plan.md` §2.** The to-do is marked done, with a pointer.
- **The gate passes** (`python3 Ralph_Loops/loop0008/gate.py`): lake build is
  ok, the one `sorry` is the §24 conjecture, MOSP pytest gives 1,402 passed,
  and pathwidth_solver pytest gives 114 passed.
- **Split run.** Clean: no `!!!` line, checked at 06:32 and 06:47. PID 1465015
  is alive.

### Blockers
- None. One thing is left for item 08: the method paragraph cites OpenAlex as
  "Priem et al. (2022)". That citation was **not** fetched in this session and
  must be checked before it goes into `refs.bib`.

### Next
- **Item 07**, the number audit. Start from `popularity.md`, "Notes for the
  number audit":
  - 1,213 against 1,212 distinct;
  - the two citation-count dates;
  - the definition behind 74 against 81.

  Also `Random-125-125-2-4_0`'s re-certification in `solver_fix.md`.
- **Item 08** takes the figure PDFs and captions as they are.
