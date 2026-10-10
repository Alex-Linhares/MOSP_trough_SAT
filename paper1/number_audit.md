# The pathwidth complex paper: the number audit (2026-10-03, loop0008 item 07)

Every quantitative claim in the seven source documents of the pathwidth complex paper was checked
against its source. A claim here means a count, percentage, time, node count,
core-hour figure, size range, measurement date, a page, section or theorem
number in a citation, or a Lean theorem named as the source of a fact. The
documents are `revised_algorithm.md`, `equivalences.md`,
`problem_transformations.md`, `solver_fix.md`, `popularity.md`,
`prior_art_counterexample.md` and `plan.md`.

Each claim gets one row: line, value, source, the check done, and a status.
Repeated mentions of one number share a row. The tables, one per document,
are in `data/number_audit/<document>.md`. The shared rules the auditors
followed are in `data/number_audit/INSTRUCTIONS.md`. Line numbers there are
those **before** the fixes.

**Verdict.** No certified value, refutation, theorem claim or Lean name was
found to be wrong.
- **Drifts.** 24 claims drifted, all small, and all are fixed in the source
  documents (listed below). Most were citation counts from an older fetch,
  page numbers off by one, size ranges stated loosely, and one wrong
  attribution.
- **Stale.** 14 status lines were true when written and overtaken by the
  125 × 125 run. They are updated or carry a dated note.
- **The split run.** No `!!!` line is in `data/solver_fix_split.log`, and no
  task in `data/solver_fix_split_tasks.csv` answered SAT. This was checked at
  07:02 and again at the end of the audit.

## Status counts

| document | rows | reproduced | matches record | drift (fixed) | stale | unsourced | unchecked |
|---|---:|---:|---:|---:|---:|---:|---:|
| `revised_algorithm.md` | 94 | 23 | 64 | 2 + 1 | 4 | 0 | 1 |
| `equivalences.md` | 112 | 6 | 103 | 1 | 1 | 0 | 1 |
| `problem_transformations.md` | 44 | 18 | 23 | 4 | 0 | 1 | 0 |
| `solver_fix.md` | 146 | 70 | 58 | 6 | 4 | 3 | 5 |
| `popularity.md` | 58 | 44 | 3 | 7 | 1 | 3 | 0 |
| `prior_art_counterexample.md` | 51 | 32 | 15 | 2 + 1 | 0 | 1 | 1 |
| `plan.md` | 48 | 17 | 26 | 1 | 4 | 0 | 0 |
| **total** | **553** | **210** | **292** | **26** | **14** | **8** | **8** |

The meaning of each status:
- **Reproduced**: recomputed now from raw data or by rerunning a script.
- **Matches record**: equal to a recorded CSV, JSON, log or tables file, or
  to a Lean statement read in the source. Not rerun.
- **Drift**, **stale**, **unsourced** and **unchecked** are as in
  `INSTRUCTIONS.md`.

In `problem_transformations.md` two rows carry two statuses, one per source,
so its statuses sum to 46. The "+ 1" drifts were found while compiling this
report. They are the "verbatim" wording, recorded once for each of the two
documents it appears in.

**What was rerun.** All reruns were cheap, offline, read-only and on one core
per auditor:
- `python3 -m paper1.fink_check`;
- `python3 paper1/thesis_check.py`;
- `python3 -m paper1.section2_figures --numbers`;
- `python3 -m paper1.solver_fix_split --summary`;
- `python3 -m benchmarks.corpus`, which still reads 6,374 of 6,376 certified;
- the `solver_fix_cost_tables` code, written to `/tmp` and identical to the
  committed tables;
- `tests/test_section2_figures.py`;
- a scratch brute force that shares no code with the repository and checks
  every number in Counterexamples 4.5, 4.11 and 4.13.

Every other figure was checked against its recorded data.

**What was not rerun, and why.**
- `paper1.complex_check` rewrites its JSON. The equivalences auditor began a
  one-core rerun of the 4,394-tree pebbling check and stopped it after about
  4 CPU-minutes. The recorded run took 144 s on 32 cores, so a one-core rerun
  would take over an hour.
- `paper1.prior_art_sweep` rewrites `citers.csv` and may use the network. Its
  counts were recomputed from `citers.csv` and the cached index files instead.
- The solver re-solves behind `solver_fix.md` items 04 and 07 are far beyond
  4 cores × 1 hour. Their tables were checked against their CSVs.

Rerunning any of these is out of scope.

## The open re-certifications: in flight

`paper1.solver_fix_split` is running under its five-day budget, to
2026-10-08T00:40, on 20 workers (PID 1465015). It is refuting `value − 1` on
the last of item 06's 115 values that rested on the customer search alone.
The figures below are from `python3 -m paper1.solver_fix_split --summary` and
`data/solver_fix_split_results.csv`, read at 07:05 on 2026-10-03.

| instance | value | `k` | state | tasks done | nodes (finished tasks) | core-hours |
|---|---:|---:|---|---:|---:|---:|
| `Random-125-125-4-1_0` | 57 | 56 | refuted 2026-10-02 16:19 | 669 | 4.97 × 10¹⁰ | 18.1 |
| `Random-125-125-4-5_0` | 46 | 45 | refuted 2026-10-02 20:34 | 616 | 7.96 × 10¹⁰ | 26.1 |
| `Random-125-125-4-2_0` | 57 | 56 | refuted 2026-10-02 23:51 | 842 | 7.64 × 10¹⁰ | 30.2 |
| `Random-125-125-2-4_0` | 24 | 23 | **refuted 2026-10-03 02:55** | 1,686 | 4.98 × 10¹¹ | 154.1 |
| `Random-125-125-2-1_0` | 24 | 23 | **in flight** | 196 | ≥ 7.55 × 10¹⁰ | 36.9 |
| `Random-125-125-2-5_0` | 20 | 19 | **in flight** | 82 | ≥ 3.21 × 10¹⁰ | 35.5 |
| `Random-125-125-4-4_0` | 51 | 50 | **in flight** | 331 | ≥ 8.96 × 10¹⁰ | 49.0 |

So **112 of the 115 are re-refuted, all unsat, and no value has changed.**
The three in flight keep their values as verified upper bounds. Their
optimality under the repaired rules is not yet re-established.

- **Not final.** For an instance in flight the node count covers finished
  tasks only, so it is a lower bound and not a final figure.
- **Do not quote the 2-4_0 count as a sequential one.** Its 4.98 × 10¹¹
  nodes is 7.9× the count at which item 07's one-core run was censored. It
  is not a sequential count: with the memo on, the split tree is larger than
  the sequential one.

**Two records are out of date and were not touched.**
- `data/solver_fix_split_tables.md` still shows `2-4_0` as partial, as of
  00:30. It is regenerated by `--tables`, which this audit was not allowed
  to run. The table is regenerated when the run is next summarised by its
  owner.
- `CLAUDE.md` says "6,374 of 6,376 certified, 2 open". That counts the
  corpus's own provenance, not the repaired-rule re-certification, so it is
  not contradicted.

## Fixes made in the source documents

Each fix is minimal and keeps the author's wording. Present-tense status
lines were updated, and history got a dated "*(2026-10-03, number audit: …)*"
note.

**`revised_algorithm.md`**
1. **The Search file count.** The header said "ten files" in `Search/`; it
   now says eleven. `Split.lean` was added on 2026-10-02. It has no `sorry`,
   but `axiom_check.lean` does not print its theorems yet, and the text now
   says so.
2. **The §4 status line.** It said "108 re-refuted, 7 need a longer run"; it
   now says 112 and 3, with a note.
3. **§4.3.6.** The nogood quote is on PDF p. 5 of Chu & Stuckey (2009), not
   p. 4.
4. **§4.6.3.**
   - "108 of 115 done, 7 left" is now "112 of 115 done, 3 left". A note
     names the four refuted by the split run, with their totals:
     7.04 × 10¹¹ nodes and 228.5 core-hours. `-2-4_0` alone took 154.1
     core-hours against a price of 47.5.
   - The note on the "faster route … proposed, not built" says it has since
     been built (`solver_fix.md` item 10, `Search/Split.lean`), and that its
     tasks do inherit old moves.
5. **§4.7.1.** The Kitsunai et al. (2016) citation is now pp. 141–142, not
   p. 141.
6. **The thesis wording** (found in compilation). The text said Chu's thesis
   restates Theorem 1 "verbatim" or "word for word"; it now says "with the
   same premise, reworded for `k` stacks". The held PDF's Theorem 6.3.6
   (p. 142) reads "S ++ [q] is k-playable … uses ≤ k stacks", where the CP
   paper reads "playable … is a solution". The premise and the proof's key
   line are the same. Fixed in §4.1 and §4.3.2.

**`equivalences.md`**
1. **Lines 508–510, a wrong attribution.** The text had Linhares & Yanasse
   (2002), Prop. 1, taking modified cutwidth "from Garey & Johnson". Page
   1761 cites it to "[3]", which is Downey & Fellows.
2. **Line 1144.** It said the `K_{1,3}` gap in Kirousis & Papadimitriou's
   proof was "checked by hand, not in Lean". A dated note now says it was
   proved in Lean the same day, as `kirousisPapadimitriou_claim2_false`.

**`problem_transformations.md`** (the header promises that every statement is
proved in Lean, and these four were not marked)
1. **(B1).** `sb(K_{1,3}) = 2` is not in Lean. The upper bound comes from the
   brute-force check and the lower bound is a hand argument.
2. **(B2).** The `es`/`vs` values of `K_2`, `K_{1,3}` and `K_{3,3}` come from
   the brute-force check, not from Lean.
3. **(F1).** "For every matrix" now reads "for every matrix with at least one
   1", which is the Lean theorem's hypothesis.
4. **(F2).** Lean proves only the lower bounds on the cutwidth and modified
   cutwidth of stars. The equalities come from the brute-force check at
   n = 7 and 9.

**`solver_fix.md`**
1. **Lines 375 and 401.** The pathwidth check's corpus sample spans 10–125
   customers, not 9–125.
2. **Line 426.** Matching failures are 0.02–0.27% of definite candidates, not
   0.03–0.27%, and 0.02–0.06% of better pairs, not 0.02%.
3. **Line 584.** The ratio is 0.986, not 0.987 (0.98649, rounded twice in the
   tables file).
4. **Line 605.** The pathwidth graphs span 4–2,916 vertices, not
   "22–1,000+".
5. **Line 865.** There are six recertify refutations at 125 × 125 among the
   21, not five.
6. **Line 1550.** The "320 tasks still queued" was the whole queue across the
   four open instances, not `2-4_0`'s alone.
7. **Stale status.**
   - The status line at the top is updated to 112 of 115.
   - Dated notes are added in item 07 ("Needs a long run"), in item 09 (the
     proposed `CLAUDE.md` text), and in item 10 (after the results, and in
     "Still open").
   - The notes give `2-4_0`'s refutation and the three in flight.

**`popularity.md`**
1. **The citation column of the top table, and the prose.** These now quote
   the 2026-09-29 cache, and the column is dated:
   - Kinnersley 215 → 214;
   - Kirousis & Papadimitriou (1986) 294 → 293, three places;
   - Yanasse (1997) 74 → 75;
   - Ohtsuki et al. 107 → 108, two places;
   - works per Kinnersley citation 5.6 → 5.7.
2. **1,213 against 1,212.** The paper quotes 1,213 records, as the figure
   draws them. A footnote gives 1,212 distinct works (and 1,592 relevant and
   2,270 hits, distinct), in the top table, the Figure 2.1 caption and the
   method paragraph. The duplicate, `W4416062387`, is from 2026, so the
   heatmap's 1,014 is unaffected.
3. **"Almost all" multi-citing works stay in one discipline** is now "most
   (195 of 269)".
4. **"74 span two disciplines"** is now "two or more" (72 span two and 2 span
   three). The count excludes Linhares & Yanasse (2002); with it the figure
   is 81. Both were recomputed.
5. **A dated note.** Figure 2.2's PDF is 6.51 in wide, and Figure 2.3's
   legend is set at 6.8 pt, both against the stated print rules.
6. **The scatter.** A note says the scatter (not used in the paper) still
   draws the 2026-09-17 counts, carried by hand in `citation_graph.py`'s
   `SCATTER`. No point changes side of the diagonal.

**`prior_art_counterexample.md`**
1. **Line 8.** "144 citing works" is now "144 index entries (141 citing
   works)". Three entries are not citing works: the thesis itself, a
   proceedings volume and the ARCH-COMP report. Line 147's "144 distinct
   works" was already worded correctly.
2. **Lines 224–227, a factual slip.** The text said two of the 32
   thesis-only works read mention open stacks, and that Prestwich et al. "is
   in both lists". `citers.csv` has Prestwich et al. citing the CP paper
   only. Of the 32, one mentions open stacks, Medema et al. (2024). The two
   works in both lists are Leo et al. and Chu's IJCAI abstract.
3. **The thesis row and the Lean table** (found in compilation). "Word for
   word" and "verbatim" became "same premise and same proof, reworded for
   `k` stacks", as in `revised_algorithm.md`.
4. **Gange, Chu & Stuckey (2019).** A note says the author list is
   unverified. The only index entry, Semantic Scholar's `W081`, lists Gange
   and Stuckey. Settle it from the paper before citing.

**`plan.md`**
1. **The `better_move` bugs.** The text said both bugs were found by the
   differential harness. Only the second was. The first was found by
   profiling the C inner loop (`reports/better_move_bug.md`).
2. **The certificate count.** "6,276 of 6,286" is the `default`
   configuration. It is 6,275 under `csearch`, with none rejected, as
   `data/certificates/tables.md` records.
3. **Stale items.** Dated notes are added to the definite-move decision and
   to remaining-work items 2, 3 and 5:
   - the fix has been the default since 2026-10-01;
   - 112 of 115 values are re-refuted, with 3 in flight;
   - the pathwidth benchmarks prove the same width on all 11,424 graphs;
   - section 2 is done;
   - of the dataset work, only the full run is left.

## Not fixed: drifts outside the seven documents

Reported, not edited, because they lie outside this item's documents or in
files it may not touch:
- **`CLAUDE.md`** (the owner's):
  - It says "the five 125×125 recertify counts"; the records hold six.
  - Its status for the 115 re-certifications, if quoted, should read 112
    re-refuted and 3 in flight.
- **`lean/MOSPFormalization/Search/ChuThesis.lean`**, line 71: the docstring
  says Theorem 6.3.6 is "Theorem 1 verbatim". It is the same premise,
  reworded. The file was not edited (no Lean edits in this item).
- **`paper1/axiom_check.lean`** does not list `Search/Split.lean`'s theorems.
  Adding them is a one-line change for item 08 or 09.
- **`paper1/citation_graph.py`**: `SCATTER` hard-codes the 2026-09-17
  citation counts.
- **`paper1/section2_figures.py`**:
  - Figure 2.3's legend is at 6.8 pt, below the 7 pt rule.
  - `numbers()` counts the phrase rule by distinct ids (1,214 for pathwidth)
    but relevant works by records (1,213); `popularity.md` quotes the
    phrase rule's record count, 1,215.
- **`data/solver_fix_split_tables.md`** is stale, as above.

## Still unsourced or unchecked

Sixteen claims (8 + 8), none load-bearing for a conclusion of the paper:
- **`popularity.md`**:
  - treewidth 6,222 hits and bandwidth minimization 306;
  - the four raw unrestricted counts (1,109,296, 1,755, 601 and 152);
  - "labels made in one session".

  The first two items are network counts of 2026-09-17 that were never
  cached. Re-fetch them, or drop them from the paper.
- **`prior_art_counterexample.md`**:
  - Crossref's public cited-by count of 15 has no cached response;
  - the Gange (2019) author list, as above;
  - "about 41,700 random graphs" (item 02) matches the session record only,
    because its script was not kept.
- **`problem_transformations.md`**: the Bienstock & Seymour (1991) and
  LaPaugh (1993) attributions point to papers not held. LaPaugh is reached
  through Kirousis & Papadimitriou (1986), ref. [3], Theorem 2.1, p. 208.
- **`revised_algorithm.md`**: Ore (1955), the source of the deficiency form
  of Hall's theorem, is not held.
- **`equivalences.md`**: the remark that pdftotext reads Lengauer's `≤` as `<`
  was not rechecked on the page image.
- **`solver_fix.md`**: the run details "12 workers", "stopped after 1.8 h",
  the worker loads in items 04 and 08 and the stage timings in item 04. These
  describe how runs were made, not results. Item 04's stage timings would
  need a re-solve to reproduce.

## For the LaTeX draft (item 08)

- **Quote the dated values.** Use the 2026-09-29 citation counts and 1,213
  relevant pathwidth works, with the footnote "1,212 distinct".
- **The re-certification status** to quote is "112 of 115 re-refuted, 3 at
  125 × 125 in flight". Check the split run again on the day the draft is
  built, with `python3 -m paper1.solver_fix_split --summary`.
- **The thesis.** Describe Theorem 6.3.6 as "the same theorem, reworded for
  k stacks", not "verbatim".
- **Before the bibliography is built**, cite Gange (2019) only after checking
  its authors, and check the OpenAlex citation, "Priem et al. 2022". The
  latter is from iteration 6's blockers and was not checked here.

## Regenerate

There is no single command; the audit is the per-document tables. The
commands used:

```
python3 -m paper1.solver_fix_split --summary          # in-flight status (read-only)
python3 -m paper1.section2_figures --numbers           # section 2 numbers, offline
python3 -m paper1.fink_check; python3 paper1/thesis_check.py
python3 -m benchmarks.corpus                           # corpus provenance counts
grep -n '^!!!' paper1/data/solver_fix_split.log        # must print nothing
```

Every other check is named in its row of `data/number_audit/<document>.md`.
