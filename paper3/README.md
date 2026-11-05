Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.

*(The title above is fixed by the owner and is used verbatim, including
the ellipsis and the final period, everywhere: here, in `latex/main.tex`,
in `reports/paper3_plan.md`, in `Ralph_Loops/loop0015/TASK.md` and in
every commit the loop makes. Questions about its wording go to
`ETH_AMBIGUOUS.MD`, never into the title.)*

**This paper is about the limitation of the ETH refutation and nothing
else.** It is not concerned with graphs, pathwidth, treewidth, MOSP or any
width parameter.

Written by Ralph loop0015 on 2026-11-05 (twelve items, `Ralph_Loops/loop0015/`;
the plan is `reports/paper3_plan.md`, §0.9 records what was done); 64 pages,
`latex/main.pdf`.

## What the paper is

A reading of OpenAI's family 378, *The Exponential Time Hypothesis is
False* (`github.com/openai/math`, dated 2026-10-25, entered the collection
on 2026-10-26; cloned read-only under `~/dev/untrusted/openai-math`, commit
`4eaee875`), by people who checked. The two audits of 2026-11-05 and the
paper's own replay found **no flaw**; the paper is a careful reading, not a
debunking. What it adds is exactness about *what* is verified:

- **What the Lean-verified statement says exactly** (Section 2;
  `lean/ComparatorChallenges/SubexponentialSAT.lean` in the clone): for
  each `k ≥ 2` there *exist* a finite multitape machine and constants
  `C, A, S, d, e` such that on every width-`≤ k` CNF, in a canonical
  encoding of bit length `L`, the machine halts with the exact count
  within `C (L + 1)^d · 2^{A · ρ(n)}` steps,
  `ρ(n) = n (ln ln(n + 16))² / √ln(n + 16)`. A **guarantee**, not a
  running time; the constants are never computed (where the proof writes
  one down it is at least 257, and the exhibited theorem's at least 258
  with a leading constant of at least 28,701); the exponent is `ρ(n)`
  only. The factor `ρ(n)/n` exceeds 1 for every `50 ≤ n < e^{5504}` (peak
  `16/e² ≈ 2.17` near `n ≈ 10^{23.7}`; `e^{5504}` has 2,391 digits), so
  with `A = 1` the verified bound is above `2^n` at every practical size:
  the verified guarantee is weaker than the trivial `2^n · poly`
  guarantee of trying all assignments. The statement does refute ETH as
  stated.
- **What the manuscript claims beyond it** (Section 3): Theorem 1.1's two
  sharper exponents, Corollary 1.4's quantitative circuit bound and
  Appendix D are **paper-only** (not in the Lean library at `4eaee875`,
  which the collection's own `lean/docs/378.md` says); the corollaries
  that follow from the statement by a reduction are **supported**; the
  comparator statement, the space bound and the sparsification parameters
  are **verified**.
- **An independent inspection and replay of the proof** (Sections 4 and
  5): the closure of 3,091 modules with no `axiom`, `sorry`,
  `native_decide`, `implemented_by`, `unsafe` or `partial`; 35 statement
  definitions compared, 33 identical and 2 identical up to the
  `noncomputable` keyword; the compile lemmas concluding in the
  comparator's own `Trace`; the repository holding no recorded axiom
  audit, no CI and no second-kernel run for this family. Then our own
  build of that closure in an isolated `bwrap` sandbox at the pinned
  toolchain (3,091 modules, 33 minutes, `#print axioms` =
  `[propext, Classical.choice, Quot.sound]`) and a second, independent
  checker (`nanoda_lib`: 95,176 declarations, no errors).
- **What follows** (Section 6): ETH, SETH, Gap-ETH, NSETH, #ETH, and the
  randomised forms of ETH, SETH and Gap-ETH, each refuted by a named
  conjunct of the statement; lower bounds derived from them lose their
  premise while the statements they concluded are not themselves refuted
  (the manuscript's own §1.1.3), in general terms and with no example.
- **What it changes for a practitioner** (Section 7): nothing on any
  machine — a measurement of CaDiCaL, Ganak and ApproxMC on random 3-CNF
  up to 500 variables against `2^{ρ(n)}` and `2^n` at constant 1, which
  cross at `n = 50`.
- **Our own Lean** (Section 8, Appendix A): the comparator's machine model
  copied byte for byte and its theorem restated as a `Prop` character for
  character, with the limit `ρ(n) = o(n)` proved and every declaration
  axiom-audited; never proved, never an axiom.
- **Related work** (Section 9): the collection's own texts, the human
  audit of the August 2026 results, the comparator and nanoda READMEs;
  "we found no prior statement" of the title's observation, bounded to
  the six texts searched.

The two audits the paper rests on are `reports/scratch/eth_audit/
statement_audit.md` and `proof_audit.md` (2026-11-05; each now carries a
one-line note of the counts the paper has since corrected). The plan is
`reports/paper3_plan.md`; the loop that wrote the paper is
`Ralph_Loops/loop0015/` (`PROGRESS.md` has one section per iteration).

## Layout

| path | content |
|---|---|
| `latex/` | the paper: `main.tex` (title verbatim, abstract, section inputs), `sec1_intro.tex` … `sec12_ack.tex`, `secA_appendix_lean.tex` (the Lean names), `secB_appendix_technical.tex` (the dense passages Sections 2–7 cite, with every line number and formula), `refs.bib` (24 entries, DOIs checked), `Makefile` (`make`, `make check`), `figures/` (PDF and PNG, each with its script under `scripts/`), `tables/` (generated `.tex`, the measurement's raw CSV and metadata), `data/doi_check.json` (the registry cache), `doi_check.log` (the run of record), `main.pdf` (committed) |
| `scripts/` | every number's regenerate script, one per section (below); each runs under `python3 -I`, reads the clone and the extract with `open()` only, and has a `--check` mode; plus `sentence_lengths.py`, the plain-English bookkeeping measure (item 12), which reads only this directory |
| `replay/` | the sandboxed replay: `README.md` (isolation, timeline, both scripts verbatim in both versions, every count and hash), `run_sandbox.sh`, `replay.sh`, `run_sandbox_nanoda.sh`, `nanoda.sh`, `counts.sh`, `logs/{run1,run2,nanoda}/` (the short logs and hashes; the full build log and the export are git-ignored and identified by SHA-256) |
| `lean/` | `README.md` pointing at the companion Lean (`lean/MOSPFormalization/SubexpPathwidth/{PrimitiveMachine,Frame}.lean`, left in place by the owner's decision S3), `axiom_check.lean` with its committed `axiom_check.log`, and `rediff.log` (the byte-level re-diff of the copy, written by `scripts/lean_rediff.py`) |
| `related/` | the four texts Section 9 quotes, fetched on 2026-11-05 (`fetched/`, with their API records and hashes), and a `README.md` of files, URLs and what was not fetched |
| `refuter/` | item 10's refuter pass: `REPORT.md` (the blind reader's report verbatim) and `README.md` (every finding, what was checked, what was done) |
| `ETH_AMBIGUOUS.MD` | every question the loop decided for itself, one entry each, for the owner; listed by number below |

## How to build

```bash
cd paper3/latex
make          # latexmk -pdf -> main.pdf
make check    # fails on any undefined reference or citation; prints the page count
make clean
```

The gate (`python3 Ralph_Loops/loop0015/gate.py`) runs `make check` here,
checks the title in `main.tex` verbatim, and fails if anything under
`solutions/` changed. The paper builds to 64 pages with no overfull box
(2026-11-05, item 11).

## How to regenerate every number

All scripts run from the repository root under `python3 -I` and read the
clone (`~/dev/untrusted/openai-math`, commit `4eaee875`) and the committed
extract `reports/scratch/eth_audit/paper.txt` with `open()` only; nothing of
the clone is executed. Every `--check` run exits non-zero if a cited page,
line, fragment or count has moved. To re-check the whole paper at once:

```bash
for s in beyond_claims proof_inspection consequences lean_rediff related_work practitioner; do
  python3 -I paper3/scripts/$s.py --check || echo "FAILED: $s"; done
python3 -I paper3/scripts/runtime_scale.py        # Section 2 (prints and rewrites its table and figure)
python3 -I paper3/scripts/rho_over_n.py           # Figure 2.1
bash paper3/replay/counts.sh                      # Section 5, from the full build log if present
python3 paper3/scripts/check_refs.py              # the bibliography's DOIs (network)
```

- **Section 2, the statement** (item 02): `python3 -I
  paper3/scripts/runtime_scale.py` prints the `ρ(n)/n` table (Table 2.1),
  the first integer above 1 (`n = 50`: `ρ(49)/49 = 0.9994`,
  `ρ(50)/50 = 1.0027`), the peak (`16/e² = 2.1654` at `ln(n+16) = e⁴`,
  `n ≈ 10^23.71`) and the return below 1 (`ln(n+16) = 5503.7`,
  `n ≈ e^5504 ≈ 10^2390`, a number of 2,391 digits), and writes
  `latex/tables/runtime_scale.tex` and `latex/figures/runtime_scale.{pdf,png}`
  (Figure 2.2). `python3 -I paper3/scripts/rho_over_n.py` draws the central
  figure (Figure 2.1, two panels, with the manuscript's two unverified
  exponents beneath) and writes `latex/tables/rho_over_n.csv`. The encoding
  lengths quoted in §2.2 and B.1 (`L = 1,006,223` at `n, m, k = 125, 500,
  4`; `47.9 M` at `1000, 4000, 3`; one seed-1 random formula each) come
  from `python3 -I reports/scratch/eth_audit/check_encoding.py`. The
  proof's constants (`A = 256 + A_t`, `1 ≤ A_t`, so at least 257;
  the comparator witnesses `C + 28700, A + 1, …`, so at least 258 and
  28,701) are read at `SqrtLogSpace/NativeLargeEntry.lean` 51,
  `NativeLeafContract.lean` 793 and `Final.lean` 41, checked by
  `proof_inspection.py`. Every comparator line number is at clone commit
  `4eaee875`; every manuscript quote gives the page of `paper.pdf` and the
  line of `reports/scratch/eth_audit/paper.txt` (page = form feeds before
  the line + 1).
- **Section 3, what the manuscript claims beyond the statement** (item 03):
  `python3 -I paper3/scripts/beyond_claims.py` checks every page, line and
  quoted fragment of the section against the extract (`paper.pdf` has 67
  pages) and every Lean location against the read-only clone at `4eaee875`
  (`docs/378.md` lines 9 and 11, the five theorems of
  `SqrtLogSpace/Final.lean` at lines 10, 74, 104, 149, 184 with their
  `#print axioms` at 197–201, the base-2 `rho` of `Asymptotics.lean` 10–11,
  `runtimeScale_le_four_rho` at 190–191, the sparsification parameters at
  14–20, `MainTheorem` of `SqrtLog/StatementCanonical.lean` line 37),
  searches the family's 3,977 `.lean` files for corollary and
  tensor-network identifiers (none), counts the files that mention ETH or
  SETH (inside the family: "ETH" in six comment lines of five files and in
  the name `exact_count_eth`, "SETH" nowhere; outside it: two `ParityLifts`
  files, not in the closure), prints the three exponents of Theorem 1.1
  divided by `n` at constant 1 (the general one peaks at `2/e = 0.736` at
  `n = e^{e²} ≈ 1,618`; the fixed-density one is `0.578` at `n = 20` and
  falls), and writes `latex/tables/beyond_claims.tex` (Table 3.2) and
  `latex/tables/beyond_exponents.tex` (Table 3.1).
- **Section 4, the proof inspected** (item 04): `python3 -I
  paper3/scripts/proof_inspection.py` re-runs the two audit scripts
  `reports/scratch/eth_audit/closure.py` (the import closure of
  `OAI.Algorithms.SubexponentialSAT.Main`: 3,091 modules, 550,551 lines
  counted by `split('\n')`, 547,460 by `wc -l`; 50 Mathlib modules +
  `Lean.Elab.Tactic.Omega`; the keyword counts with comments stripped) and
  `defdiff.py` (32 declarations `SAME`), both under `python3 -I` as
  subprocesses and read-only on the clone, and then checks what they do
  not: the four declarations the diff cannot match by itself (`countWord`
  identical, `runtimeScale` and `runtimeBound` identical up to
  `noncomputable def` / `noncomputable section`, the theorem statement
  identical, 1,124 characters normalised and 1,353 raw, challenge line 194
  = `Final.lean` line 74; so 35 compared, 33 identical, 2 up to the
  keyword), the 3,977 family files and 886 outside the closure (no
  `sorry`/`axiom`/`native_decide`/`admit`, raw or stripped), the nine
  `opaque`s with bodies, the two `quotPrecheck false`, the `#print axioms`
  placement (8 closure files / 19 commands; 17 / 35 over the family
  directory; the replay's 19 in-build axiom lines all three axioms), the
  absence of any recorded `depends on axioms` output in the clone, the
  challenge JSONs (418; `enable_nanoda` false 413, true 2, absent 3), the
  single CI workflow, the toolchain, the Mathlib pin, the 42 manifest
  packages and 23 patches (none for Mathlib), the lakefile hooks, and
  about 60 line citations of the proof's spine (`Final.lean`,
  `GuardedCompiler`, `CompileSpace`, `NativeOuter`, `NativeLargeEntry`,
  `NativeEntry`, `NativeOuterBudgets`, `NativeLeafContract`, `BitProgram`,
  the challenge file, `docs/378.md`, the preprint's date line,
  `history.md`). Writes `latex/tables/proof_inspection.tex` (Table 4.1)
  and `latex/tables/proof_inspection.json`. Table 4.2 (the trust boundary)
  is prose from Sections 4 and 5, not generated.
- **Section 5, the replay** (item 01): `bash paper3/replay/counts.sh`
  recomputes every count of the section from the full build log
  (`~/dev/untrusted/replay/logs/build_main.log`, git-ignored; its SHA-256
  is committed, below) and writes `replay/logs/run2/counts.txt`: 3,083
  `Built OAI…` lines, 3,091 distinct modules (= the audit's closure, set
  difference empty both ways against
  `reports/scratch/eth_audit/closure_modules.json`), `Build completed
  successfully (12014 jobs)`, 0 `error` lines, 0 `sorry` warnings, 11
  warnings all `has local changes`, start 01:16:25 and end 01:49:31 on
  2026-11-05 (33 min 6 s), exit 0, the axioms line, the Lean and Mathlib
  version lines. The nanoda numbers (2,355,666,449 bytes and 43,633,742
  lines of export in 68 s; `Checked 95176 declarations with no errors` in
  110 s) are in `replay/logs/nanoda/` as the tools printed them. The
  scripts are quoted verbatim in `replay/README.md`; re-running the replay
  means re-running `run_sandbox.sh` and `run_sandbox_nanoda.sh` from
  `~/dev/untrusted/replay/` (about an hour of eight cores, network on).
- **Section 6, what follows in general terms** (item 05): `python3 -I
  paper3/scripts/consequences.py` checks every page, line and quoted
  fragment of the section against the extract (the hypotheses as the
  manuscript states them: ETH p. 4 lines 165–166, SETH 166–169, Gap-ETH
  172–174 and its randomised form 175–176, NSETH 181–183, the randomised
  ETH and SETH by citation at 190–191, #ETH 204–205; the refutation
  paragraph 187–191 and its two context sentences 191–194; the #ETH
  sentence p. 5 211–212; §1.1.3's "removes one basis" 226–227, OVC
  229–232, the unrestricted-width hypothesis 233–236, "a reduction in the
  other direction" 237–238, Set Splitting 239–243; the transfer caveat
  p. 2 95–99), the manuscript's bibliography entries that `refs.bib`
  copies for the hypotheses' sources (extract lines 3686–3811), the
  comparator lines Section 6 relies on (38, 47, 132, 147, 194, 203–211 at
  `4eaee875`), prints the clause-count bound `Σ_{j≤k} C(2n, j)` (2,604,376
  at `n = 125`, `k = 3`) and `ρ(n)/n` at a few sizes, and writes
  `latex/tables/hypotheses.tex` (Table 6.1). No other number in Section 6
  is its own; each is Section 2's.
- **Section 7, for the practitioner** (item 06): `nice -n 19 python3 -I
  paper3/scripts/practitioner.py --regenerate` runs the measurement
  (1,172 s of wall clock on the machine of record, 2026-11-05): random
  3-CNF at `m = round(4.26 n)`, `n = 20, 30, 40, 50, 60, 80, 100, 150, 200,
  250, 300, 400, 500`, twenty seeds per size, generated by the script from
  `(n, seed)`; CaDiCaL 1.9.5 through python-sat 1.9.dev15 (`cadical195`)
  for the decision bit, Ganak 2.8.0 (pyganak, Arjun preprocessing included)
  for the exact count, ApproxMC 4.4.0 (pyapproxmc, `ε = 0.8`, `δ = 0.2`,
  projection = all variables) for the approximate count, and
  blocking-clause enumeration over CaDiCaL at `n ≤ 30` as the independent
  check; each call in its own interpreter under `nice -n 19`, eight at a
  time, 60 s per call, censored above it; a tool that finishes fewer than
  ten of twenty at a size stops escalating. Writes
  `latex/tables/practitioner_raw.csv` (every call) and
  `latex/tables/practitioner_meta.json` (versions, CPU, load, date).
  `python3 -I paper3/scripts/practitioner.py` (seconds) rebuilds
  `latex/tables/practitioner.tex` (Table 7.1) and
  `latex/figures/practitioner.{pdf,png}` (Figure 7.1) from the CSV, prints
  every number Section 7 quotes (`t20 = 1.28e−4` s and the common factor
  `t20 / 2^20`; the 1 s crossings of the two scaled guarantees at `n = 33`
  and `35`; `2^(ρ(n) − n)` at 50, 100, 500; the decades between CaDiCaL's
  median and each guarantee at 60, 100, 200, 500), runs the checks (Ganak =
  enumeration on 40 instances at `n ≤ 30`; CaDiCaL's bit = `[count > 0]`
  everywhere both finished; ApproxMC within `1.8×` of Ganak on 178 of 206;
  the clone read with `open()` only: 3,977 family files, no `#eval`, no
  `def main`, no `IO` action, the comparator theorem existential in the
  machine at line 195) and exits non-zero if any fails. No MOSP or
  pathwidth instance; nothing under `solutions/`. The two counters were
  installed from PyPI for this section (`pip install pyganak`;
  `pyapproxmc` was already present); no counter binary is on the host.
- **Section 8, the statement in our Lean** (item 07): `python3 -I
  paper3/scripts/lean_rediff.py` re-diffs the copy — our
  `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean` lines
  31–221 against the clone's comparator file lines 1–190 followed by 220,
  byte for byte (identical, 191 lines each side), with the clone's SHA-256
  (`4183b205…`) and commit (`4eaee875`) — and the restatement — the body of
  `SubexpCount` (Frame.lean 85–107) against the comparator theorem's body
  (clone 195–217): identical after whitespace normalisation (1,073
  characters) and line by line after stripping indentation (23 lines) —
  and counts `sorry` and `axiom` declarations in our two files (zero and
  zero; the clone's one `sorry` at line 218 is outside the copied range);
  log `paper3/lean/rediff.log`. The axiom audit is `cd lean && lake env
  lean ../paper3/lean/axiom_check.lean > ../paper3/lean/axiom_check.log`
  (21 declarations: 19 on exactly `[propext, Classical.choice,
  Quot.sound]`, `Trace` on none, `countWord` on two of the three, `sorryAx`
  on none; Lean 4.34.0-rc2, Mathlib `1192d624`, our library's toolchain).
  The names are listed below and in `paper3/lean/README.md`.
- **Section 9, related work and context** (item 08): `python3 -I
  paper3/scripts/related_work.py` locates every quotation of the section —
  in the four texts fetched on 2026-11-05 into `paper3/related/fetched/`
  (the arXiv API record and abstract page of 2608.14673; the `master`
  READMEs of `leanprover/comparator`, commit `865edc14`, archived and
  merged into Lean core as `lake comparator` at v4.35.0, and
  `ammkrn/nanoda_lib`, commit `8de7e0c4`, with both repositories' API
  records), in the clone at `4eaee875` (`history.md` line 18,
  `lean/docs/378.md`, `lean/ComparatorChallenges/README.md` and
  `SubexponentialSAT.json`) and in the manuscript extract (lines 153 on
  page 3, 170–171, 3733–3736) — checks that `literature/` holds none of
  the cited papers (`literature/MISSING.md` lists them), that the replay's
  nanoda commit equals the repository's latest, runs the prior-statement
  word search over the six texts (none outside the manuscript; in it,
  "practical" once and "exhaustive" eleven times), prints the SHA-256 of
  every fetched file and writes `latex/tables/related_sources.tex`
  (Table 9.1). `paper3/related/README.md` lists the files and URLs.
- **Sections 1 and 10, the abstract, introduction and conclusion** (item
  09): no number of their own. The abstract's two numbers (the crossing at
  50 variables; the 2,391 digits of `e^5504`) and the introduction's (257,
  2.17 near a 24-digit `n`, 3,091 files, 33 minutes, 95,176 declarations,
  500 variables) are Sections 2, 4, 5 and 7's, each cited with its
  section; the abstract is 198 words (`\emph` stripped, `$2^n$` one word).
  The conclusion's §10.2 sorts every `ETH_AMBIGUOUS.MD` entry (61 as of
  item 12, through 12b): 7 resolved by the owner, 15 procedural or
  already carried by the text, 39 open and affecting the text, by entry
  number (item 09 wrote it for the first 48 as 7 / 8 / 33; item 12
  extended and re-counted it, 12b). The same sorting is below.
- **The data statement and the acknowledgements** (item 11): no number
  of their own; the data statement names the paths above, the
  acknowledgements the versions Sections 5, 7 and 8 record.
- **The bibliography** (item 10, two entries added by item 11): `python3
  paper3/scripts/check_refs.py` (it imports paper 1's checker) fetches
  the Crossref or DataCite record of every `refs.bib` entry that carries a
  DOI and compares title, year and first author; `--lookup` also searches
  Crossref for the entries that have none; `--refresh` ignores the cache
  `paper3/latex/data/doi_check.json`. The run of record is
  `paper3/latex/doi_check.log` (tracked since item 11; the `latex/*.log`
  ignore rule had hidden it). Thirteen DOIs were found and added by item
  10 (`ETH_AMBIGUOUS.MD` 10a); the Lean 4 and Mathlib entries were copied
  from `paper1/latex/refs.bib` by item 11 (11g); Dinur 2016 is an ECCC
  report with none; the manuscript, the arXiv record and the four
  repository READMEs carry none by nature.
- **The refuter pass** (item 10): no number of its own.
  `paper3/refuter/README.md` is the account of the one blind refuter
  subagent (21 findings, 17 fixed, 4 recorded as 10a–10d); the family-side
  "ETH" count it prompted is now a check in `beyond_claims.py` and the page
  of extract line 153 a check in `related_work.py`.
- **The second plain-English pass** (item 12, the reserve): no number in
  the paper. `python3 -I paper3/scripts/sentence_lengths.py` (from the
  repository root; `--ref <commit>` for a committed version, `--list N`
  to list the pieces over N words) is the crude measure behind
  `ETH_AMBIGUOUS.MD` 12a: pieces over 45 words 95 → 26 and over 58 words
  32 → 18 across every `sec*.tex`, mean 22.4 → 20.0 words, between commit
  `66a755ac2` and the working tree of 2026-11-05; the 26 left are tables,
  displays, list sentences, verbatim quotations and splitter artefacts.

## The replay: status and hashes

**Done, both kernels** (item 01, 2026-11-05; `replay/README.md` has the
exact scripts, the timeline, every count and hash). A fresh copy of the
clone (commit `4eaee875`) was built inside a `bwrap` sandbox (read-only
system directories, a private home, this repository invisible, PID/IPC/UTS
namespaces, eight cores by `taskset` at `nice -n 19`, network on for the
lakefile's dependency clones and the Mathlib cache) at the pinned
`leanprover/lean4:v4.34.1` (commit `5045d005`, Lake 5.0.0) with upstream
Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`: `lake build
OAI.Algorithms.SubexponentialSAT.Main` compiled **3,091 modules** (the
audit's closure exactly) in **33 min 6 s** (01:16:25 → 01:49:31) with **0
`error` lines and 0 `sorry`** lines, and `#print axioms` of
`SqrtLogSpace.exact_count_and_sat` printed `[propext, Classical.choice,
Quot.sound]`. A first run (01:03) failed at once on a `lake build -j 8`
option this Lake does not have (01a); the second (01:16) is the one
reported. Then a **second kernel**: `lean4export` (tag `v4.34.0`, built
with `v4.34.1` in 3 s) exported the theorem and its dependencies in 68 s,
and `nanoda_lib` (commit `8de7e0c4`, v0.4.31, built in 10.7 s) checked
them: `Checked 95176 declarations with no errors`, three axioms permitted
and three `axiom` declarations in the export, exit 0, 110 s. What the
replay does not cover: the comparator run itself (the statement match is
textual, item 04's) and the faithfulness of `lean4export`; the Lean kernel
of `v4.34.1` and upstream Mathlib are trusted, the former now beside
nanoda (Section 5.4, Table 4.2).

The hashes (`replay/logs/run2/hashes.txt`, `build_main_sha256.txt`,
`replay/logs/nanoda/export_sha256.txt`; SHA-256; the same values in the
replay copy and in the pristine clone):

| file | SHA-256 |
|---|---|
| `lean/ComparatorChallenges/SubexponentialSAT.lean` (the statement, 220 lines) | `4183b2057cff350d66848215ff7167196dfc20e1891b598fdddea59077a76685` |
| `lean/ComparatorChallenges/SubexponentialSAT.json` | `debbfdc9c01104d2369be80da5180978275106df8b685f693fba7ce7da7c5b19` |
| `lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean` | `040360a8465957622d934e5f1bb4f2cce8dab950e78f52033fbf70da493184f5` |
| `lean/OAI/Algorithms/SubexponentialSAT/Main.lean` | `cbd4cebf71f1d3239c21241f946d05e8de802dbb9c138713f8e7182d868b2d1c` |
| `lean/lean-toolchain` | `d5edba4e4b8faad9c1baeadb265716d20d03be4d1a2647dc5e35b0c0325bea7b` |
| `lean/lake-manifest.json` | `cf6105a25d9dca2f166b241d9191bd12c7e13305890dc9c4d0952351cccc0794` |
| `logs/build_main.log` (the full build log, 3,160 lines, git-ignored) | `d313f594daa3cd3713f872bde8b4d33138820eeec5a335a21a276846aa54e21e` |
| `logs/export.ndjson` (the `lean4export` output, 2,355,666,449 bytes, 43,633,742 lines, git-ignored) | `bdbc9afe336fea99b01bc4eced6e4232153afdefe13a1095cdc5ca9499e3f573` |

Replay copy HEAD = pristine clone HEAD = `4eaee87548250b2682affda7d05d947c05554bae`;
`git status --short` of the replay copy's tracked files is empty. The
fetched texts of Section 9 are hashed in `related/README.md` and by
`scripts/related_work.py`.

## The Lean names

The companion Lean is two files of our library, left where loop0014 wrote
them (owner's decision S3): `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean`
(the verbatim copy of the comparator's definitions, lines 31–221, after a
30-line attribution header) and `Frame.lean` lines 1–191 (the
restatement; lines 192–268 belong to another study and are not cited).
Namespace `MOSPFormalization.SubexpPathwidth`, except the copy, whose
namespaces are the source's (`OAI.Algorithms.SubexponentialSAT.…`).
Appendix A of the paper has eight rows; `paper3/lean/README.md` gives the
line of each name. The 21 declarations the audit prints
(`paper3/lean/axiom_check.log`):

| group | names |
|---|---|
| the copied vocabulary (ten, under `OAI.Algorithms.SubexponentialSAT.`) | `SqrtLog.Statement.runtimeScale`, `SqrtLog.Statement.runtimeBound`, `SAT.count`, `Encoding.encodeCNF`, `Encoding.formulaBitLength`, `Computation.PrimitiveMachine.step`, `Computation.Trace`, `SqrtLogSpace.countWord`, `SqrtLogSpace.locatedStep`, `SqrtLogSpace.visitedSpace` |
| the restatement | `SubexpCount` (a `def` of a `Prop`, the theorem's body character for character), `ExactCountAndSat` (`∀ k, 2 ≤ k → SubexpCount k`) |
| the lemmas and helpers | `SubexpCount.anti`, `ExactCountAndSat.subexpCount`, `IsSubexpExponent`, `runtimeBound_eq`, `tendsto_log_sq_div_sqrt`, `runtimeScale_isLittleO`, `isSubexpExponent_runtimeScale`, `LocatedCfg.monitor_config`, `Trace.config_of_locatedStep` |

Audit result: 19 on exactly `[propext, Classical.choice, Quot.sound]`,
`Computation.Trace` on none (an inductive), `SqrtLogSpace.countWord` on
`[propext, Quot.sound]`, `sorryAx` on none; no `sorry`, no `axiom`
declaration in either file; both imported by `lean/MOSPFormalization.lean`
and built by the gate. Nothing is proved about the theorem itself; nothing
of the proof's 3,091 modules is copied.

## Open questions for the owner, by entry

Every entry of `ETH_AMBIGUOUS.MD` (61 on 2026-11-05: S1–S8 from the setup,
01a–10d from the items, 11a–11g from this write-up, 12a–12b from the
reserve item), one clause each. The paper's §10.2 sorts all 61 the same
way (since item 12; item 11 had listed the entries after 09d here only).
The owner resolves an entry by editing the paper and striking it, or by
leaving it.

**Resolved by the owner in writing (7).** S1 the author line; S3 the Lean
left in place (07a follows it); S4 cite the manuscript first, no width
references; S6 the counters; S7 the phrase "for every 50 ≤ n < e^5504";
S8 the replay's toolchain.

**Procedural, or corrections the text already carries (15).** S5 the
per-item cap of the driver; 01a the sandbox's core cap (`-j 8` → `taskset`);
03b the manuscript has 67 pages, not 64; 04b `enable_nanoda: false` on 413
of 418, not 416; 04d `#print axioms` in 8 closure files / 19 commands; 04e
42 manifest packages, not 41; 06b `pyapproxmc` was already installed,
`pyganak` installed; 08xb Section 9 and Appendix A not rewritten by the
plain-English item (drafted plain); 10c the sentences over 45 words the
refuter left, split by item 12 (12a); 11c the two audits annotated, not
edited, and the budget comment fixed; 11d the entries after 09d listed
here, and since item 12 in §10.2 too; 11e the CLAUDE.md paragraph drafted
below and not applied; 11f the plan's §0 updated by annotation and a new
§0.9; 12a the scope of the second plain-English pass (quotations, tables,
lists and captions left); 12b §10.2 extended to all entries and
re-counted, and this section's open count corrected (it said 36 and
listed 40).

**Open and affecting the text (39).**
- *The title and its figures*: S2 `2^n` typeset with a superscript; 02a
  three drawings of one function; 02b the central figure's peak and `+16`;
  10b the title's "is slower" against the paper's non-claim of any running
  time, reconciled by §2.5 and §7.4 and by nothing in the title.
- *Section 2*: 02c a proof-side constant quoted in the statement section;
  02d the Lean theorem transcribed, not verbatim; 08xd the `A ≥ 257` /
  `A ≥ 258` readings both kept.
- *Section 3*: 03a the third tag "supported"; 03c Corollary 1.4's argument
  not worked out with the verified exponent; 03d Corollary 1.2 stated with
  the verified exponent and tagged supported.
- *Sections 4 and 5*: 01b which nanoda and which `lean4export`; 01c the
  three axioms permitted and unused ones ignored; 01d what "replayed"
  covers; 04a 35 compared / 33 identical / 2 up to a keyword; 04c the
  exhibited constants `A ≥ 258`, `C ≥ 28,701`.
- *Section 6*: 05a the problem list elided from one quotation; 05b SETH
  refuted at each `k`, "SETH ⇒ ETH" cited for the record; 05c the
  hypotheses' sources copied from the manuscript, not re-read; 05d two
  paragraphs are ours.
- *Section 7*: 06a one scale factor for both guarantee curves; 06c seven
  references typed from memory (DOIs since checked, 10a); 06d the counters
  at their defaults, with a plateau that looks like a preprocessing budget.
- *Section 8*: 07b "every line on the three axioms" read as "nothing beyond
  the three"; 07c the re-diff matches the restatement's body too.
- *Section 9*: 08a the audit paper's title spelt with an apostrophe the
  arXiv record lacks; 08b four public records fetched beside the three
  allowed pages; 08c DOIs unchecked at the time (since checked, 10a); 08d
  "no prior statement" bounded to six texts.
- *Plain English, Sections 1 and 10*: 08xa dense passages moved to Appendix
  B, not cut; 08xc glosses repeated per section and in the introduction;
  09a the third clause in words, no formula beyond `2^n`; 09b which numbers
  the abstract carries; 09c the sorting of the entries is the owner's to
  redo; 09d "people who checked" is the author and the assistant the
  acknowledgements disclose.
- *The write-up*: 10a thirteen DOIs added from Crossref, which the download
  list did not name; 10d the refuter's recorded findings (the placeholders,
  now written; the audits, now annotated); 11a the data statement's
  repository URL and licence taken from paper 1; 11b the acknowledgements'
  AI-use disclosure names the refuter as a second session of the same
  assistant; 11g the Lean 4 and Mathlib references copied from paper 1's
  bibliography.

Fourteen of the 39 are bibliographic or typographic (S2, 02a, 02b, 02d,
03a, 03d, 04a, 05c, 06c, 08a, 08b, 08c, 08xa, 11g); the rest are choices
about what the text says, each a sentence that can be struck without
touching any number.

## The CLAUDE.md paragraph

*(Drafted by item 11, 2026-11-05. **Not applied** to `CLAUDE.md`; the owner
folds it in, replacing the paragraph "Paper 3, title fixed by the owner
(2026-11-05, no deviations)" in the Next Steps section. The title stays
verbatim.)*

**Paper 3, written (loop0015, 2026-11-05; title fixed by the owner, verbatim):**
*"Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size."*
— **about the limitation of the ETH refutation and nothing else** (owner:
no graphs, no pathwidth, no MOSP in it). `paper3/latex/main.pdf`, 64
pages, plain English by the owner's rule (every symbol glossed, no formula
beyond `2^n` in the abstract and introduction, the dense passages in
Appendix B); `paper3/README.md` has the regenerate command beside every
number, the replay's hashes, the Lean names and every open question by
entry. The object is OpenAI's family 378 (`github.com/openai/math`, commit
`4eaee875`, cloned read-only under `~/dev/untrusted/`, read with `open()`,
`sed` and `grep` only, built once in a `bwrap` sandbox from a fresh copy).
**What is verified** (Section 2): for each `k` a finite multitape machine
and constants `C, A, S, d, e` *exist* with the exact count within
`C (L+1)^d · 2^{A ρ(n)}` steps, `ρ(n) = n (ln ln(n+16))² / √ln(n+16)`; the
constants are never computed (at least 257 where the proof writes one
down, the exhibited theorem's at least 258 with `C ≥ 28,701`); `ρ(n)/n`
exceeds 1 for every `50 ≤ n < e^{5504}` (peak `16/e² ≈ 2.17` near
`10^{23.7}`; `e^{5504}` has 2,391 digits), so the verified guarantee is
above `2^n` at every practical size while the machine's running time is
unknown; the manuscript's sharper exponents and Corollary 1.4's circuit
bound are **paper-only** (Section 3, each claim tagged verified /
supported / paper-only with page and line). **The inspection** (Section
4): closure 3,091 modules, zero `axiom` / `sorry` / `native_decide` /
`implemented_by` / `unsafe` / `partial`, 35 statement definitions compared
(33 identical, 2 up to `noncomputable`), the compile lemmas ending in the
comparator's own `Trace`, no recorded axiom audit, no CI,
`enable_nanoda: false` on 413 of 418 challenge JSONs. **The replay**
(Section 5): the closure built at the pinned `v4.34.1` and upstream
Mathlib `d13f23b7` in 33 min, 0 errors, `#print axioms` = the three
standard axioms; `lean4export` + `nanoda_lib` (`8de7e0c4`) checked 95,176
declarations with no errors — the trust boundary now excludes the build,
the axiom output and the single kernel, and still includes the comparator
run (textual match only) and `lean4export`'s faithfulness. **What
follows** (Section 6): ETH, SETH, Gap-ETH, NSETH, #ETH and the randomised
forms of the first three refuted by named conjuncts; a derived lower bound
loses its premise and nothing more (the manuscript's §1.1.3). **The
practitioner** (Section 7): CaDiCaL, Ganak and ApproxMC on random 3-CNF to
500 variables sit tens of decades below `2^n`, which the verified
guarantee crosses at `n = 50`; no implementation of the verified machine
exists (`practitioner.py --check` proves the absence of any entry point).
**Our Lean** (Section 8): the comparator's model copied byte for byte and
the theorem restated as `SubexpCount k : Prop`, left under
`lean/MOSPFormalization/SubexpPathwidth/` by the owner's decision S3, 21
declarations axiom-audited (`paper3/lean/`), never proved, never an axiom.
**Related work** (Section 9): `leanprover/comparator` is archived and
merged into Lean core as `lake comparator` at v4.35.0; the human audit
paper (arXiv 2608.14673) concerns the August results, not 378; "we found
no prior statement" of the title's observation, bounded to six texts.
**The stance**: no flaw found, none asserted; a careful reading by people
who checked. **Gaps**: the comparator run not reproduced; the two JCSS
hypothesis papers cited unread (`literature/MISSING.md`); the title's
"is slower" rests on §2.5 and §7.4 (10b); 61 entries in
`paper3/ETH_AMBIGUOUS.MD`, 39 open and affecting the text, sorted in
Section 10.2 and in the README. Cost: thirteen sessions and about 7.5 h
of wall clock for items 01–12 (the replay's 33 min inside), under $160
of the $4,000 budget. Nothing under `solutions/` touched;
no MOSP or pathwidth run; the only compute on random 3-CNF the script
generates and the sandboxed build.
