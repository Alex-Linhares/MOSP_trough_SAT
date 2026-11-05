# Paper 3 — *Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.* — plan for Ralph loop0015

*Written 2026-11-05, after the two audits of OpenAI's family 378
(`reports/scratch/eth_audit/statement_audit.md`, `proof_audit.md`) and
after loop0014's items 01–02 fixed what the verified statement says and
restated it in Lean. The title is fixed by the owner and is used verbatim,
including the ellipsis and the final period, everywhere. The loop
directory is `Ralph_Loops/loop0015/` (`TASK.md`, `iterations.md`,
`PROGRESS.md`, `loop.py`, `gate.py`, `knobs.json`, `allowed_sorries.txt`,
`budget_watch.py`), cloned from loop0014's. Launched 2026-11-05 02:05; twelve
items done in twelve sessions by 2026-11-05 (§0.9 below, written by item 11,
records what was done, item by item, with the gaps).*

**This paper is about the limitation of the ETH refutation and nothing
else.** (Owner, 2026-11-05.) It is not concerned with graphs, pathwidth,
treewidth, MOSP or any width parameter.

## 0. The question and the stance

### 0.1 The question

On 2026-10-25 OpenAI's manuscript collection (`github.com/openai/math`,
Apache-2.0; cloned read-only under `~/dev/untrusted/openai-math` at commit
`4eaee875`) added family 378, *The Exponential Time Hypothesis is False*:
a deterministic algorithm that counts the satisfying assignments of any
`k`-CNF on `n` variables in time subexponential in `n`, with a Lean proof
checked by the collection's comparator mechanism against a 220-line
statement. The paper asks one question and answers it by reading, not by
opinion:

> **Q.** What exactly is verified, what is only in the manuscript, what
> follows from the verified part, and what does it change for anyone who
> solves or counts CNF formulas on a machine?

### 0.2 The stance, and the title's claim made precise

The two audits of 2026-11-05 found **no flaw**: the comparator statement
means what the manuscript's verified form says, and the proof's import
closure shows no unsoundness by inspection. The paper is therefore **a
careful reading by people who checked, not a debunking**, and every
sentence is to be written so that a reader who admires the result finds
nothing unfair in it. What the title asserts, made precise:

1. **What is verified is a bound, a guarantee**: for each `k ≥ 2` there
   *exist* a finite multitape machine and constants `C, A, S > 0`,
   `d, e ≥ 1` such that on every width-`≤ k` CNF the machine halts with
   the exact count within `C (L + 1)^d · 2^{A · ρ(n)}` steps, where `L`
   is the encoding's bit length and
   `ρ(n) = n (ln ln(n + 16))² / √ln(n + 16)`. The constants are
   existential: the proof constructs the machine from an explicit program
   but **no value of `C, A, S, d, e` or of the state count is computed**
   anywhere in the library.
2. **The exponent is `ρ(n)`, and only `ρ(n)`.** The manuscript's Theorem
   1.1 states the sharper `n log log n / √log n` and, at fixed clause
   density, `n / √log n`; the Lean library carries neither
   (`lean/docs/378.md` says so). Those exponents are **unverified**.
3. **The factor `ρ(n)/n` exceeds 1 for every `50 ≤ n < e^{5504}`**: it
   is 0.9994 at `n = 49`, 1.0027 at 50, 1.11 at 100, 1.42 at 10³, 1.85 at
   10⁶, peaks at `16/e² ≈ 2.17` near `n ≈ 10^{23.7}`, and falls below 1
   again only past `n ≈ 10^{2390}`. So even with `A = 1` the verified
   bound is above `2^n` at every practical size, and `A` is unknown.
   **The verified guarantee is weaker than the trivial guarantee
   `2^n · poly` of trying all assignments at every practical size.**
4. **The machine's actual running time is unknown.** A bound above `2^n`
   does not say the machine is slow; it says nothing about its speed
   below `e^{5504}` variables. No implementation exists to time.
5. **The verified statement does refute ETH** as stated — a deterministic
   `2^{o(n)} · poly(n + m)` #k-SAT counter in the standard sense — and
   with it SETH, Gap-ETH, #ETH and their randomised forms, as the
   manuscript's §1.1.1 lists. Lower bounds *derived* from those
   hypotheses lose their premise; the statements they concluded are not
   themselves refuted, as the manuscript's own §1.1.3 explains.

### 0.3 What is on record (nothing to redo)

- `reports/scratch/eth_audit/statement_audit.md` (2026-11-05): the
  comparator statement read field by field — `PrimitiveMachine` is
  finite, `Trace` counts exactly the steps, the encoding is `O(k·n·m)`
  bits and unary in `n`, the quantifier order puts the machine and the
  five constants after `k` and before `n` and `F`, `runtimeScale` is
  `ρ(n)` in natural logarithms, the output is the count in binary on a
  named tape and the decision in the halting state; verdict "not
  refuted", with the `ρ(n)/n` numbers and the companion-claims list
  (what the statement supports, what is paper-only). Scripts beside it:
  `check_encoding.py`, `VarCheck.lean`.
- `reports/scratch/eth_audit/proof_audit.md` (2026-11-05): the closure
  of the solution (3,091 modules, 550,551 lines; zero `axiom`, `sorry`,
  `admit`, `native_decide`, `ofReduceBool`, `implemented_by`, `extern`,
  `unsafe`, `partial`; nine bodied `opaque`s; two `quotPrecheck false`),
  the 33 statement definitions textually identical, the 1,124-character
  statement identical, the compile lemmas concluding in the comparator's
  own `Trace`, Mathlib `d13f23b7` unpatched, toolchain `v4.34.1`; and the
  evidential gap: no recorded `#print axioms`, no CI, `enable_nanoda:
  false`, the comparator run not reproduced. Scripts: `closure.py`,
  `defdiff.py`; data `closure_modules.json`, `hits.json`; the committed
  `pdftotext` extract `paper.txt`.
- `reports/subexp_pathwidth.md` §1.0 and §1.3.5–1.3.7 (the verified
  exponent named; the manuscript's caveats quoted with lines) and
  §2.1–2.2 (the machine model copied verbatim with attribution;
  `SubexpCount k` character for character; `runtimeScale_isLittleO`).
  Nothing else of that report is in scope.
- `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean` (the
  verbatim copy of the comparator's definitions, Apache-2.0 header) and
  `Frame.lean` lines 1–165 (`SubexpCount`, `ExactCountAndSat`,
  `SubexpCount.anti`, `runtimeBound_eq`, `runtimeScale_isLittleO`): no
  `sorry`, no `axiom`, axiom-audited in loop0014 item 02. Item 07 moves
  the ETH-only part to a neutral path (§0.4.7). *(Superseded 2026-11-05:
  the owner's resolution S3 left the Lean in place; item 07 moved nothing
  and cited the existing path, entry 07a.)*
- The collection itself: the manuscript (64 pages — **67**, item 03, `ETH_AMBIGUOUS.MD` 03b), the comparator file
  and JSON, the solution tree, `lean/docs/378.md`, `history.md` (the
  working-group sentence), `lean/lakefile.lean` with its configuration-time
  `run_cmd` (line ~290) and `post_update` hooks.
- `paper1/latex/`: the house LaTeX setup (`make check`, `plainnat`,
  Appendix A of Lean names, figures as PDFs beside their scripts).

### 0.4 Design decisions (fixed)

1. **The title is verbatim everywhere** — `\title` and `pdftitle` in
   `paper3/latex/main.tex` (`$2^n$` and `\ldots` its only LaTeX), the
   first line of `paper3/README.md`, this plan, `TASK.md`, every commit
   body (the driver writes it). The gate checks `main.tex`. No session
   rewords it; questions about it go to `paper3/ETH_AMBIGUOUS.MD`.
2. **The `ETH_AMBIGUOUS.MD` protocol.** No item stops on a question.
   Each ambiguity gets one dated entry — what was ambiguous, what the
   item chose, what the owner may want to change — and the item goes on
   with its choice. Item 09's conclusion lists the entries that affect
   the text; item 11's README lists them all.
3. **Every number has a regenerate command** under `paper3/scripts/` (or
   an existing audit script), named beside the number in the text and
   in `paper3/README.md`.
4. **Every quotation from the manuscript carries page and line** of the
   committed extract `reports/scratch/eth_audit/paper.txt` (page = form
   feeds before the line + 1); every quotation from the Lean carries
   file and line at commit `4eaee875`.
5. **The replay is sandboxed, and it is already running.** The clone is
   untrusted data, read only with `cat`/`sed`/`grep`/`pdftotext`/
   `python3 -I`, never built in place, never run from inside, never
   imported into our `lean/`. The one exception is the replay: a
   **fresh copy** at `~/dev/untrusted/replay/openai-math/`, built inside
   `/usr/bin/bwrap` by `~/dev/untrusted/replay/run_sandbox.sh` (read-only
   `/usr /lib /lib64 /bin /sbin /etc`, a `tmpfs` `/home` with `/home/al`
   bound to `replay/home` so that `/home/al/dev/MOSP` is invisible,
   `--unshare-pid --unshare-ipc --unshare-uts --die-with-parent`, network
   on for the lakefile's clone hooks and the `elan`/Mathlib downloads,
   `nice -n 19`), running `replay.sh` inside: `elan` into the private
   home (`v4.34.1` fetched), `lake exe cache get`, `lake build
   OAI.Algorithms.SubexponentialSAT.Main -j 8` (the 3,091-module closure
   only; *the `-j 8` was rejected by Lake 5.0.0 and the core cap became
   `taskset -c 0-7` on the `bwrap` line, entry 01a*), `#print axioms` of
   `exact_count_and_sat` through `lake env lean`,
   the exit code to `replay/logs/DONE`; logs `sandbox.out`,
   `build_main.log` (large, git-ignored, hash committed),
   `build_filtered.log`, `axioms.log`. **Started by the coordinator on
   2026-11-05 at 01:03**; budgeted at up to 8 hours. Item 01 does not
   start another: it waits with bounded polls, records, relaunches once
   on a diagnosed failure fixed inside `replay/`, and then attempts the
   nanoda replay of the exported environment in the same sandbox. Only
   text leaves the sandbox.
6. **The companion Lean is our restatement, audited** — `SubexpCount k`
   over the verbatim machine model, with `paper3/lean/axiom_check.lean`
   in the `paper1/axiom_check.lean` pattern; no `sorry`, no `axiom`; **no
   crossover or pathwidth theorem is cited**.
7. **The Lean lives under a neutral path.** Item 07 moves
   `PrimitiveMachine.lean` and the ETH-only declarations of `Frame.lean`
   to `lean/MOSPFormalization/ETH/{PrimitiveMachine,Statement}.lean`;
   `SubexpPathwidth/Frame.lean` imports `ETH.Statement` and keeps its
   pathwidth side untouched. Recorded in `ETH_AMBIGUOUS.MD` (setup
   entry S3). *(Superseded by the owner's resolution of S3 on 2026-11-05:
   the Lean stays under `SubexpPathwidth/` and the paper cites that path;
   nothing was moved, entry 07a.)*
8. **LaTeX in `paper3/latex/`**, built by `make check` like paper 1
   (article class, Palatino, `plainnat`, Appendix A rows for Lean names,
   figures in `paper3/latex/figures/` generated by `paper3/scripts/`).
9. **Scope discipline.** No sentence about graphs, pathwidth, treewidth,
   MOSP, width-parameterised dynamic programs, crossovers or reductions
   into width problems; consequences for lower bounds are stated in
   general terms with the manuscript's §1.1.3 as the source.
10. **Subagents: at most 4 per session**; one refuter at a time; no
    fan-out. **Compute**: 32 shared cores, everything under `nice -n 19`,
    ≤ 8 workers (*the owner lifted the worker cap at `nice -n 19` on
    2026-11-05; eight were used*); `solutions/` never written; no run on any MOSP or
    pathwidth instance; item 06's compute is on random 3-CNF it
    generates, under an hour.

### 0.5 Items, one line each, in order

| # | item | depends on | kind | cap |
|---|---|---|---|---|
| 01 | The replay: the SubexponentialSAT closure built in the bwrap sandbox from a fresh copy (already running since 2026-11-05 01:03; item 01 waits with bounded polls, never starts a second build); `#print axioms` of the main theorem; Lean and Mathlib versions; one relaunch on a diagnosed failure; nanoda attempted; `paper3/replay/README.md` quoting `run_sandbox.sh` and `replay.sh`; logs under `paper3/replay/logs/` (large ones git-ignored, hashes committed); "Independent replay" drafted | — | waiting on a sandboxed build, writing | **8 h** |
| 02 | The statement, read exactly: the comparator definitions one by one, re-verified against the clone; quantifier order; encoding length; the exponent; the `ρ(n)/n` table and figure with `paper3/scripts/runtime_scale.py`; the title's claim stated precisely | 01 (the "replayed" sentence only) | reading, writing, one script | 4 h |
| 03 | What the manuscript claims beyond the verified statement: Theorem 1.1's two sharper exponents, Corollary 1.4's quantitative circuit bound, Appendix C's consequences, Appendix D — each tagged verified / paper-only with page references | 02 | reading, writing | 4 h |
| 04 | The proof inspection, re-verified (closure, zero counts, 33 identical definitions, compile lemmas in the comparator's own `Trace`, unpatched Mathlib, no recorded audit / CI / nanoda) and joined with item 01's result | 01 | reading, scripts (read-only), writing | 4 h |
| 05 | What follows, in general terms: ETH, SETH, Gap-ETH, #ETH and the randomised forms refuted as the statement supports; a derived lower bound loses its premise, its conclusion is not refuted (the manuscript's §1.1.3) | 02 | writing | 4 h |
| 06 | For the practitioner: CDCL (python-sat/CaDiCaL) and a model counter if obtainable, on random 3-CNF at `n = 20…60`, against `2^{ρ(n)}` and `2^n`; under an hour; `paper3/scripts/practitioner.py` | 02 | measurement (minutes), writing | 4 h |
| 07 | The companion Lean: the restatement moved to `lean/MOSPFormalization/ETH/`, axiom-audited; `paper3/lean/README.md`; Appendix A rows | 02 | Lean | 4 h |
| 08 | Related work and context: arXiv 2608.14673, the working group (quoted from `history.md`), Impagliazzo–Paturi, Impagliazzo–Paturi–Zane, the comparator README, nanoda; `literature/MISSING.md` | — | reading, writing | 4 h |
| 09 | Abstract, introduction, conclusion; the title's sentence made precise in the first paragraph; `ETH_AMBIGUOUS.MD` reviewed, the entries affecting the text listed as open | 02–08 | writing | 4 h |
| 10 | Full build and refuter pass: `make check` clean; one refuter reads the PDF against the clone and the audits; every disagreement fixed or recorded | 09 | build, one subagent | 4 h |
| 11 | The write-up around the paper: `paper3/README.md` complete; the CLAUDE.md paragraph drafted there, not applied; this plan's §0 updated; the full gate | 10 | writing | 4 h |
| 12 | Reserve: the nanoda replay if item 01 could not do it, or whichever item ended short | 11 | — | 4 h |

Twelve items; the replay at its cap, the rest at loop0012–14's rate.
**Estimate 20–30 hours wall, $400–700**; the owner's budget is $4,000
(§0.6). *Actual (item 11, 2026-11-05): items 01–10 plus the added 08x in
eleven sessions, 02:05 to 08:37, about 6.5 h of wall clock and $133 by the
budget watcher's sum at 08:36; the replay's build itself took 33 min
because the coordinator had started it before launch.*

### 0.6 The budget rule

**$4,000 for the whole loop** (owner, 2026-11-05). `budget_watch.py`
(cloned from loop0014) sums, every five minutes, the **last** `# result`
line of every `session_*.log` — `total_cost_usd` is cumulative within a
session, so the last line is the session's cost and summing the lines
would overcount — writes `budget.txt`, and sets `knobs.json` `stop: true`
when the sum passes $4,000; the driver re-reads the knobs before every
session and finishes the current iteration before stopping. A session
that exceeds its wall-clock cap is killed by the driver and its item
marked `[!]`; a session that ends on an API error is retried once.

### 0.7 The risks

1. **The replay does not finish, or fails** (3,091 modules; the
   Mathlib cache may not match the pinned revision; a hook may fail
   inside the sandbox; the `v4.34.1` download; memory). Mitigation: the
   build was started before the loop (01:03) so the item's 8 h cap is
   mostly waiting; `replay.sh` writes the exit code to `DONE`; item 01
   relaunches once after fixing the cause inside `replay/`; the module
   count in the log is recorded at the cap; the sandbox stays in place
   for item 12; every later section reads "replayed to module N of
   3,091" rather than failing. Cost: the item's cap and no more.
2. **The sandbox leaks** (a bind too wide, a secret in the replay home,
   a hook writing outside `.lake`). Mitigation: the private home is
   created empty and inspected before the run; `/home/al/dev/MOSP` is not
   bound; only text is copied out; nothing produced inside is executed
   outside.
3. **The paper reads as a debunking.** Mitigation: the stance sentence in
   `TASK.md`; item 10's refuter is told to file every sentence that reads
   so; every "unverified" is paired with "not in the Lean library at
   commit `4eaee875`", never with "wrong".
4. **Scope creep back into width parameters** (the repository's whole
   context pulls that way). Mitigation: §0.4.9; the refuter files any
   graph, width or MOSP sentence; `refs.bib` carries no width reference.
5. **nanoda cannot be built or run** (toolchain mismatch of
   `lean4export`, the Rust crate's state). Mitigation: it is "if
   feasible" in item 01 and the reserve's first use; the paper says
   "single-kernel" honestly if it was not run.
6. **The title's `50 ≤ n` boundary is quoted differently in different
   documents** (the CLAUDE.md paragraph says "every `n < e^{5504}`",
   `check_encoding.py` says the crossing is at `n ≈ 49`). The number is
   regenerated by item 02's script: `ρ(50)/50 = 1.0027`, `ρ(49)/49 =
   0.9994`; the paper says `50 ≤ n`.

### 0.8 Gate

`Ralph_Loops/loop0015/gate.py`, cloned from loop0014 and extended:
`lake build` of `lean/`; every file under `lean/MOSPFormalization/`
imported by `MOSPFormalization.lean`; `sorry` count against an empty
`allowed_sorries.txt` and no `axiom`; pytest on `tests/` and
`pathwidth_solver/` with a 900 s per-test timeout; `make -C paper1/latex
check`; **`make -C paper3/latex check`** once `paper3/latex/Makefile`
exists (it does since setup; a printed note otherwise); **the title
verbatim in `paper3/latex/main.tex`** (after stripping its `$` and
`\ldots`); and **no change under `solutions/`** in `git status`. Axiom
audits of the companion Lean are item 07's (`paper3/lean/axiom_check.lean`),
run by hand and committed as a log, as paper 1's are.

### 0.9 What was done (item 11, 2026-11-05, in the past tense)

The loop ran twelve sessions on 2026-11-05 (items 01–11 and the added
item 08x; item 12, the reserve, was not needed for nanoda and remains the
place for a second plain-English pass, entry 10c). Every session ended
with the gate passing; nothing under `solutions/` was touched, no MOSP or
pathwidth instance was run, nothing of the clone was executed outside the
sandbox. The paper is `paper3/latex/main.pdf`, 64 pages, no overfull box,
title verbatim; `paper3/README.md` has the regenerate command beside every
number and every open entry by number.

- **01, the replay** — done, both kernels. The coordinator's run had failed
  at 01:13 on `lake build -j 8` (no such option in Lake 5.0.0); the one
  relaunch at 01:16 with `taskset -c 0-7` built the 3,091-module closure
  (the audit's set exactly) in 33 min 6 s, 0 errors, 0 `sorry`, `#print
  axioms` = the three standard axioms, Lean 4.34.1, Mathlib `d13f23b7`.
  Then `lean4export` (v4.34.0 tag, built with v4.34.1) and `nanoda_lib`
  0.4.31 (commit `8de7e0c4`): `Checked 95176 declarations with no errors`.
  `paper3/replay/README.md`, `logs/{run1,run2,nanoda}/`, `counts.sh`;
  Section 5. Gap: the comparator run itself is not reproduced (the
  statement match is textual); `lean4export`'s faithfulness is trusted.
- **02, the statement** — every comparator line re-verified; the proof's
  constant `A = 256 + A_t` found and quoted (02c); `runtime_scale.py`
  (the `ρ(n)/n` table, the crossing at 50, the peak `16/e²` at
  `ln(n+16) = e⁴`, the return below 1 at `ln(n+16) = 5503.7`); the owner's
  central figure kept with its peak made analytic (02b); Section 2.
- **03, beyond the statement** — every claim located by page and line
  (the manuscript has 67 pages, 03b) and tagged verified / supported (a
  third tag, 03a) / paper-only; `Final.lean`'s five theorems read;
  `beyond_claims.py`; Section 3. Gap: the paper-only proofs were located,
  not read for correctness.
- **04, the inspection joined with the replay** — both audit scripts
  re-run read-only with identical output; 35 definitions compared, 33
  identical, 2 up to `noncomputable` (04a); the exhibited constants
  `A + 1 ≥ 258`, `C + 28700 ≥ 28,701` (04c); 413 of 418 JSONs (04b); 8
  closure files / 19 `#print axioms` commands (04d); 42 packages (04e);
  the trust boundary's five items sorted into moved / moved in part / not
  moved (Table 4.2); `proof_inspection.py`, 141 checks; Section 4. Gap:
  the ~3,000 files of arithmetic were not read; grep is necessary, not
  sufficient.
- **05, what follows** — each hypothesis as the manuscript states it,
  refuted by a named conjunct of the statement with the quantifier form;
  what a derived lower bound loses, in general terms and with no example
  (05a–05d); `consequences.py`; Section 6.
- **06, the practitioner** — CaDiCaL 1.9.5, Ganak 2.8.0 (installed from
  PyPI, 06b) and ApproxMC 4.4.0 on random 3-CNF, 13 sizes 20–500, 20
  seeds, 1,172 s of wall clock; the two guarantees scaled by one common
  factor so that they cross at `n = 50` (06a); the absence of any entry
  point in the family proved by the script; `practitioner.py`; Section 7.
  Gap: one machine, random instances, the counters at their defaults
  (06d).
- **07, the companion Lean** — nothing moved (S3, 07a); the byte-level
  re-diff of the copy and the normalised match of the restatement's body
  (07c); the axiom audit of 21 declarations (07b); `paper3/lean/`;
  Section 8 and Appendix A. Gap: the match is textual, not a
  `lean4export`-level check; our library's toolchain is 4.34.0-rc2, not
  the clone's.
- **08, related work** — the three allowed pages fetched with their
  public records (08b), hashed and quoted by line; the working-group
  sentence of `history.md` quoted; `leanprover/comparator` found archived
  and merged into Lean core at v4.35.0; "no prior statement" bounded to
  six texts (08d); `literature/MISSING.md` extended; `related_work.py`;
  Section 9. Gap: the two JCSS hypothesis papers are cited unread.
- **08x, plain English** (added to the list by the owner's rule of 05:30)
  — Sections 2–8 rewritten sentence by sentence, the dense passages moved
  to a new Appendix B (08xa), 56 glosses after one blind reader; mean
  sentence length 30 → 18–28 words by section; 48 → 55 pages.
- **09, abstract, introduction, conclusion** — the abstract at 198 words
  with two numbers and no formula beyond `2^n` (09a, 09b); the glossary
  before the summary; the conclusion's §10.2 sorting of the 48 entries
  then written (09c); eight slips found by a blind reader, all fixed;
  62 pages.
- **10, full build and refuter** — DOIs: thirteen found on Crossref and
  DataCite and added (10a); one blind refuter, 21 findings, 17 fixed, 4
  recorded (10b the title's "is slower", 10c the unsplit 46–58-word
  sentences, 10d the placeholders and the audits' counts); zero overfull
  boxes; every check script re-run.
- **11, the write-up** — `paper3/README.md` completed (the replay's
  hashes, the Lean names, all 59 entries by number, the CLAUDE.md
  paragraph drafted and not applied); the data statement and the
  acknowledgements written (R17); the two audits annotated with their
  superseded counts (R19); this §0 annotated where it had been overtaken
  (the page count, the Lean's path, the `-j 8`, the worker cap, the
  estimate) and this subsection added; the gate run. The two new sections
  take the paper from 62 to 64 pages, still with no overfull box.
- **12, the reserve** — not needed for nanoda (item 01 ran it). Open for
  the owner: the second plain-English pass of 10c.

**Where §0.4 was found wrong**: 0.4.5's `-j 8` (Lake 5.0.0 has no jobs
option, 01a) and 0.4.7 (overtaken by the owner's S3). Everything else in
§0.4 held. The risks of §0.7: 1 did not occur beyond the first run's
option error; 2 did not occur (the private home was empty, only text left
the sandbox); 3 was tested by two blind readers, who found no debunking
sentence; 4 did not occur (the refuter found no width sentence); 5 did
not occur (nanoda built and ran in 110 s); 6 is settled by `runtime_scale.py`
and the owner's S7.

## 1. What this plan does not claim

It does not claim a flaw in the result, a running time of the verified
machine, or anything about the manuscript's paper-only proofs. It does
not assert the theorem either: our Lean restates it as a `Prop` and never
proves it. It claims, at the end, a paper that says exactly what is
verified, exactly what is not, what follows for the hypotheses, and what
it changes on a machine — with every number regenerable, every quotation
located, the proof replayed under isolation as far as the cap allowed,
and every question the loop could not settle written down for the owner.
