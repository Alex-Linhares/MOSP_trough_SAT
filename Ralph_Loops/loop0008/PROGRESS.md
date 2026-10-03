# loop0008 progress

Plan: strengthen paper 2, "The pathwidth complex", toward a first full draft.
Items are in `iterations.md`, rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0008/gate.py`.

Current: 1/9 SOLVED

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
