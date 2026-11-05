# loop0015 — paper 3: items

The paper is *Exponential time hypothesis is false... but the verified
algorithm is slower than trying all 2^n assignments at every practical
size.* (title fixed by the owner, verbatim everywhere). **It is about the
limitation of the ETH refutation and nothing else**: not graphs, not
pathwidth, not any width parameter. The plan is `reports/paper3_plan.md`;
the rules are `TASK.md` (the title rule, the no-stopping /
`ETH_AMBIGUOUS.MD` protocol, the untrusted clone, the sandbox, four
subagents at most, "a measurement is not a theorem", "we found no prior
statement"). The paper lives in `paper3/latex/` (built by
`make -C paper3/latex check`); numbers come from `paper3/scripts/`; the
replay from `paper3/replay/`; the companion Lean from
`lean/MOSPFormalization/ETH/` with `paper3/lean/README.md` pointing at it.
Every item drafts its section in `paper3/latex/sec*.tex`, ends it with
"what this does not claim", and records every choice it had to make in
`paper3/ETH_AMBIGUOUS.MD`.

- [x] **01 The replay: the SubexponentialSAT closure built in the bwrap sandbox, the axioms recorded, nanoda attempted.** `[cap 8 h]`
  **The build is already running — do not start another.** The
  coordinator launched it on 2026-11-05 at 01:03 from
  `/home/al/dev/untrusted/replay/` (a fresh copy of the clone at
  `replay/openai-math/`; the pristine clone
  `/home/al/dev/untrusted/openai-math` is never touched). `run_sandbox.sh`
  there runs `bwrap` under `nice -n 19` with `/usr /lib /lib64 /bin /sbin
  /etc` read-only, a `tmpfs` `/home` with `/home/al` bound to
  `replay/home` (so `/home/al/dev/MOSP` is invisible), `replay/` bound at
  `/replay`, `--unshare-pid --unshare-ipc --unshare-uts
  --die-with-parent`, network on (the lakefile's clone hooks, the `elan`
  and Mathlib downloads), and executes `replay.sh` inside, which installs
  `elan` into the private home (`ELAN_HOME=/home/al/.elan` inside =
  `replay/home/.elan` outside; the pinned `leanprover/lean4:v4.34.1` is
  fetched from `lean-toolchain`), then in `/replay/openai-math/lean` runs
  `lake exe cache get`, then `lake build OAI.Algorithms.SubexponentialSAT.Main
  -j 8` (the 3,091-module closure only, never the default target that
  builds all 721 families), then `#print axioms
  OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat` via
  `lake env lean` on a file it writes to `/tmp`, logs `lean --version`
  and the Mathlib `rev`, and writes the exit code to `replay/logs/DONE`.
  Logs: `replay/logs/sandbox.out` (the timeline), `replay/logs/build_main.log`
  (the full build output, large — git-ignored; commit its SHA-256 and the
  filtered tail), `replay/logs/build_filtered.log` (errors, `sorry`
  warnings, completion lines), `replay/logs/axioms.log`. Expect hours;
  the item's cap is 8 h for this reason.
  **The job**: (a) read `run_sandbox.sh` and `replay.sh` and quote them
  verbatim in `paper3/replay/README.md`, with the start time from
  `sandbox.out`; (b) wait for `replay/logs/DONE` with **bounded polls in
  the foreground** (`timeout 600 bash -c 'until [ -f .../DONE ]; do sleep
  60; done'` repeated, reading `sandbox.out` and the module count in
  `build_main.log` between polls; never a bare background wait that ends
  the turn; find the build by PID if needed, never by command text); (c)
  when DONE exists, read the exit code; confirm **zero `error` lines and
  zero `sorry` warnings** in `build_main.log` (`grep -c`), record the
  module count built, the wall-clock from the timestamps; (d) record the
  axioms output (expected `[propext, Classical.choice, Quot.sound]`), the
  Lean version line and the Mathlib `rev` line from `sandbox.out`, plus
  `sha256sum` of `replay/openai-math/lean/ComparatorChallenges/SubexponentialSAT.lean`
  and of `OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean` and
  `git -C replay/openai-math rev-parse HEAD` (run from outside, read-only
  commands only); (e) copy the small logs (`sandbox.out`,
  `build_filtered.log`, `axioms.log`, `DONE`) and the SHA-256 and last
  200 lines of `build_main.log` into `paper3/replay/logs/`; (f) **if DONE
  shows a non-zero exit code or the log shows errors**: diagnose from the
  log (a toolchain download that failed, a hook failure, an
  out-of-memory, a cache miss that turned into a Mathlib build), fix the
  cause **inside `replay/` only** (never the pristine clone), relaunch
  `run_sandbox.sh` **once** (`nohup ... > replay/logs/sandbox.out 2>&1
  &` and then bounded polls again), and record what happened in the
  README and in `ETH_AMBIGUOUS.MD`; if the second run cannot finish in
  the cap, record the module count reached and mark `[!]`, leaving the
  sandbox in place for item 12; (g) **then the nanoda replay, if feasible
  within what is left of the cap (at most 2 h)**: `lean4export`
  (leanprover/lean4export at the `v4.34.1` toolchain) on the solution
  module to an export file, and nanoda (the independent Rust kernel the
  comparator README names; `cargo` is on the host, so build it **inside
  the same sandbox** in the private home, by a second script beside
  `replay.sh` run through `run_sandbox.sh`'s bwrap line) replaying that
  export; record repository, commit and command; if it cannot be
  obtained or built, record that in `ETH_AMBIGUOUS.MD` and leave it to
  item 12; (h) draft `paper3/latex/sec5_replay.tex`, "Independent
  replay": what was run, where, under what isolation, the axioms
  printed, the versions, the time, the hashes, and — in "what this does
  not claim" — that the replay trusts the `v4.34.1` kernel and upstream
  Mathlib, that it is not the comparator run (no statement-level match by
  `lean4export`; the textual match is item 04's), and whether a second
  kernel ran. One subagent at most, only if a build error needs a second
  reading. Nothing produced inside the sandbox is executed outside it;
  only text leaves it.

- [x] **02 The statement, read exactly.**
  From `reports/scratch/eth_audit/statement_audit.md`, re-verified line
  by line against the clone (`cat`, `sed -n`): the comparator's
  definitions one by one — `PrimitiveMachine` (finite: `tapeCount`,
  `stateCount`, the transition table on `3·stateCount` points into a
  five-value `Stmt`), `Cfg`, `step`, `Trace` (exactly `t` successful
  steps, `refl` only to itself), `LocatedCfg`/`monitor`/`visitedSpace`,
  the encoding (`encodeNat` unary, `frame`, `encodeList`, `literalCode`,
  `encodeCNF`, `formulaBitLength = O(k·n·m)`), `SAT.count` over all `2^n`
  assignments, `WidthAtMost`, `countWord`/`toNat`, `runtimeScale`,
  `runtimeBound` — then the quantifier order (`k` → machine and `C A S d
  e` → `∀ n F` → `∃ time final`), the encoding length, and the exponent.
  Write `paper3/scripts/runtime_scale.py` (from `check_encoding.py`,
  under `python3 -I`, no import from the clone) that prints the table of
  `ρ(n)/n` for `n = 1, 20, 49, 50, 100, 10³, 10⁶, 10¹², 10^{23.7}, …,
  e^{5504}`, the crossing points (above 1 from `n = 50`; below 1 again at
  `ln(n + 16) ≈ 5504`, `n ≈ 10^{2390}`), the peak (`16/e² ≈ 2.17` at
  `ln(n + 16) = e⁴`), and emits `paper3/latex/figures/runtime_scale.pdf`
  (log-`n` axis from 10 to 10^{2500}, the line `ρ(n)/n`, the level 1,
  the practical range 50–10⁶ shaded) and `paper3/latex/tables/
  runtime_scale.tex`. Draft `paper3/latex/sec2_statement.tex`: the
  statement in words and in Lean, the table and the figure, and the
  title's claim made precise — *a guarantee, not a running time; the
  constants `C, A, S, d, e` are existential and never computed; with
  `A = 1` the verified exponent exceeds `n` for every `50 ≤ n < e^{5504}`;
  with the true `A` nothing is known; so at every practical size the
  verified guarantee is weaker than the guarantee `2^n · poly` of trying
  all assignments.* Say what the statement does establish (a
  deterministic `2^{o(n)} · poly(n + m)` #k-SAT counter in the standard
  sense, hence the refutation of ETH as stated). Every definition quoted
  with its line in the comparator file; the manuscript's "log denotes
  the natural logarithm" with page and line. Ends with "what this does
  not claim" (no running time of any machine; no statement about the
  proof).

  **Owner's instruction (2026-11-05): the ratio ρ(n)/n is the paper's
  central figure — "it makes it so much more clear".** The coordinator has
  produced it: `paper3/scripts/rho_over_n.py` renders
  `latex/figures/rho_over_n.pdf` (the whole range, `log₁₀ n` from 1 to
  3000: the verified ratio peaking at 2.17 near `n ≈ 10^{23.5}`, above 1
  from `n = 50`, back below 1 only at `n ≈ e^{5504} ≈ 10^{2390}`, with the
  manuscript's two unverified exponents beneath) and
  `latex/figures/rho_over_n_practical.pdf` (`n = 10 … 10⁶` with the values
  at `n = 50, 125, 10³, 10⁴, 10⁶`), plus `latex/tables/rho_over_n.csv`.
  Use both in the statement section — the whole-range figure first, as
  Figure 1 of the paper — with captions that say what is verified and
  what is not, keep the script as the regenerate command, and improve the
  figures only if a check finds a number wrong (then fix the script, not
  the picture).

- [x] **03 What the manuscript claims beyond the verified statement.**
  From `paper.txt` (page = form feeds before the line + 1; cite page and
  line): Theorem 1.1's two sharper exponents (`n log log n / √log n`,
  and `n / √log n` for `m ≤ Dn`), Corollary 1.2 (its randomised
  reduction), Corollary 1.3 (the counting-preserving encodings), Corollary
  1.4 (the quantitative `c·n√log n` circuit bound, whose proof in Appendix
  C uses the fixed-density bound), Appendix C's consequences (C.1, C.2),
  Appendix D (tensor contraction, the sharper route), §1.1.1's list of
  hypotheses, §1.1.3's fine-grained remarks — each tagged **verified** (a
  consequence of the comparator statement, with the one-line reason) or
  **paper-only** (with the page where it is proved and the sentence of
  `lean/docs/378.md` that says the Lean carries the weaker bound). A
  table `claim → where stated → verified / paper-only → why`. Draft
  `paper3/latex/sec3_beyond.tex`. "What this does not claim": no
  judgement on the paper-only proofs (not read for correctness here);
  "paper-only" means not in the Lean library at commit `4eaee875`, not
  "wrong".

- [x] **04 The proof inspection, joined with the replay.**
  From `reports/scratch/eth_audit/proof_audit.md`, re-verified by
  re-running `closure.py` and `defdiff.py` (`python3 -I`, read-only on
  the clone) and quoting the numbers from the fresh run: the closure
  (3,091 modules, 550,551 lines, 50 Mathlib modules + `Lean.Elab.Tactic.Omega`,
  886 dead files), the zero counts (`axiom`, `sorry`, `admit`,
  `native_decide`, `ofReduceBool`, `implemented_by`, `extern`, `unsafe`,
  `partial`; the two `quotPrecheck false`; the nine bodied `opaque`s),
  the 33 statement definitions textually identical and the 1,124-character
  theorem statement identical, the compile lemmas concluding in the
  comparator's own `Trace`/`locatedStep` (the structural point: no
  internal cost model can leak into the statement), the unpatched Mathlib,
  the absence of a recorded axiom audit, of CI and of nanoda
  (`enable_nanoda: false`, as on 416 of 418 challenge JSONs), and the
  lakefile hooks. Then **join item 01's result**: which of the trust
  boundary's five items moved (kernel replay done by us; axioms printed;
  comparator run still not reproduced; nanoda done or not). Draft
  `paper3/latex/sec4_proof.tex`. "What this does not claim": the ~3,000
  files of arithmetic were not read; grep is necessary, not sufficient,
  and the build is what shows the closure type-checks.

- [x] **05 What follows, in general terms: the hypotheses, and what a derived lower bound loses.**
  Exactly which hypotheses the *verified* statement refutes and how: ETH
  (Impagliazzo & Paturi 2001; the deterministic `2^{o(n)}` 3-SAT decision
  is read off the answer tape), SETH (SETH ⇒ ETH; cite the standard
  implication with its source), Gap-ETH, #ETH, NSETH and the bounded-error
  randomised forms — each as the manuscript's §1.1.1 (page, line) lists
  it, with the one-line reason the comparator statement supports it (a
  deterministic counter decides, counts, and is a randomised algorithm
  too) and with the quantifier form stated (the single-machine
  `2^{O_k(ρ(n))}` form implies the `∀ ε ∃` negation of ETH). Then, **in
  general terms and with no example from any width parameter**: a lower
  bound proved as "ETH ⇒ no `2^{o(n)}` for X" or "SETH ⇒ no `(c − ε)^k`
  for Y" has a false premise if the theorem stands and derives nothing;
  its conclusion is not refuted by anything in the statement; and the
  manuscript's own §1.1.3 says such bounds also follow from the
  unrestricted-CNF-SAT hypothesis, which Theorem 1.1 does not touch
  because it is for fixed `k` — quote the sentence with page and line.
  Also the manuscript's own caveat that `2^{o(n)}` bounds do not transfer
  under general polynomial-time reductions (page, line). Draft
  `paper3/latex/sec6_consequences.tex`. "What this does not claim": no
  statement "no `(c − ε)^k` algorithm" is refuted; the unrestricted-width
  hypothesis is untouched; nothing about any specific problem's
  complexity beyond what §1.1.1 and §1.1.3 state.

- [x] **06 For the practitioner: SAT solvers and model counters against the verified bound and `2^n`.**
  The comparison that matters on a machine is with CDCL and with exact
  model counters, not with `2^n`. A small measurement (`nice -n 19`,
  ≤ 8 workers, under an hour of wall clock, random 3-CNF generated by
  the script, **no MOSP or pathwidth instance**): first check what is
  available — no `sharpSAT`, `ganak`, `d4` or `approxmc` binary is on
  the host (checked 2026-11-05), `python-sat 1.9.dev15` is (CaDiCaL,
  Glucose, …), `pyapproxmc` is not installed; try `pip install
  pyapproxmc` (approximate counting) and, if a pip-installable exact
  counter exists, that; otherwise exact counting by blocking-clause
  enumeration at `n ≤ 30` only (a loop over a SAT solver is not a
  counter at larger `n`; say so). Measure (a) CaDiCaL decision time on
  random 3-CNF at clause ratio 4.26 for `n = 20, 30, …, 60` (and larger
  if seconds allow), 20 seeds each, median and max; (b) the counter's
  time on the same formulas where it finishes; and tabulate beside them
  `2^{ρ(n)}` and `2^n` (both at constant 1, both as *guarantees*, scaled
  to the `n = 20` measurement so the shapes compare). The point: the
  verified guarantee is never the binding one on any machine — it is
  above `2^n` for every `n ≥ 50`, and the solvers are many orders below
  `2^n`. `paper3/scripts/practitioner.py` with `--regenerate`; figure
  `paper3/latex/figures/practitioner.pdf`; table. Draft
  `paper3/latex/sec7_practitioner.tex`. "What this does not claim":
  timings on one machine, named versions, random instances only; nothing
  about the verified machine's actual running time (unknown); no
  implementation of the verified algorithm exists to run.

- [x] **07 The companion Lean: our restatement, axiom-audited.**
  The restatement `SubexpCount k` (the comparator statement character for
  character over the verbatim-copied machine model) is on record in
  `lean/MOSPFormalization/SubexpPathwidth/{PrimitiveMachine,Frame}.lean`.
  Move the ETH-only part under a neutral path (plan §0.4.7, decided at
  setup and recorded in `ETH_AMBIGUOUS.MD`): `git mv` `PrimitiveMachine.lean`
  to `lean/MOSPFormalization/ETH/PrimitiveMachine.lean` (header and
  attribution unchanged) and move `SubexpCount`, `ExactCountAndSat`,
  `SubexpCount.anti`, `ExactCountAndSat.subexpCount`, `runtimeBound_eq`,
  `tendsto_log_sq_div_sqrt`, `runtimeScale_isLittleO` and
  `isSubexpExponent_runtimeScale`'s dependency (`IsSubexpExponent` may
  stay in `Frame.lean` or move; keep the build green) into
  `lean/MOSPFormalization/ETH/Statement.lean`; `Frame.lean` imports
  `ETH.Statement` and keeps the pathwidth side untouched;
  `MOSPFormalization.lean` imports the new files; `lake build` clean; no
  `sorry`, no `axiom`. Then `paper3/lean/axiom_check.lean` in the
  `paper1/axiom_check.lean` pattern (`#print axioms` on every theorem of
  `ETH/`, run with `lake env lean ../paper3/lean/axiom_check.lean` from
  `lean/`), its output committed as `paper3/lean/axiom_check.log`, and a
  byte-level re-diff of `ETH/PrimitiveMachine.lean` against lines 1–190
  and 220 of the clone's comparator file (`diff` empty; log committed).
  `paper3/lean/README.md` pointing at the files, the names and the
  audit. Draft `paper3/latex/sec8_lean.tex` and the Appendix A rows
  (`\leanentry`). **No crossover theorem, no pathwidth statement is
  cited.** "What this does not claim": `SubexpCount k` is a `def` of a
  `Prop`, never proved here; the copy is definitions only; no `#eval`
  can evaluate the exponent.

  **Owner resolution (2026-11-05, ETH_AMBIGUOUS S3): do NOT move the
  Lean. Leave `PrimitiveMachine.lean` and `Frame.lean` under
  `lean/MOSPFormalization/SubexpPathwidth/` and cite that path; the paper's
  appendix names the declarations by their existing full names. The
  axiom audit, the README and everything else in this item stand.**

- [ ] **08 Related work and context.**
  The human-audit paper arXiv 2608.14673 (Sienicki & Sienicki, *A Human
  Audit of OpenAI's AI-Generated Mathematical Proofs*, v3 2026-09-09 —
  fetch the abstract page; it concerns the ten results of 1 August 2026,
  not family 378, so cite it for the method of review, quoting only what
  the fetched abstract says); the Impagliazzo–Paturi–Williams working
  group named in the collection's `history.md` (quote that sentence with
  its line; anything reported in the press is "reported" unless the text
  is on disk or fetched and quoted exactly); Impagliazzo & Paturi 2001
  and Impagliazzo, Paturi & Zane 2001 (the hypotheses; held? check
  `literature/`, else `MISSING.md`); the comparator mechanism's README
  (leanprover/comparator — fetch, quote the check it performs:
  statement-level match by exported declarations, permitted axioms,
  kernel replay, the `landrun` sandbox, `enable_nanoda`); nanoda (the
  Rust kernel; its repository README fetched and quoted); the
  collection's own `lean/docs/378.md` and `lean/ComparatorChallenges/README.md`.
  Draft `paper3/latex/sec9_related.tex`. `literature/MISSING.md` entries
  for every paper cited but not held. "We found no prior statement" of
  the title's observation, never "first" — and say what was searched
  (the collection's `history.md`, the human-audit paper's abstract, the
  comparator README).

- [ ] **08x The plain-English rewrite of every section drafted so far.**
  Owner's rule of 2026-11-05 (TASK.md, "The paper is written in plain
  English"). Rewrite `sec2` … `sec8` (whatever exists under
  `paper3/latex/`) sentence by sentence to that rule: short sentences,
  one idea each; every symbol defined in words on first use and
  paraphrased where it carries the argument; every term of art glossed on
  first use; the figures' captions readable by a layperson; nothing lost
  in precision ("the verified guarantee", not "the algorithm", where that
  is the fact; "verified" and "not verified" kept on every claim). Keep
  every number, citation, regenerate command and Lean name; move dense
  technical passages into the appendix and cite them from the plain text.
  Check: read each rewritten section aloud in your head as a reader with
  no background; `make -C paper3/latex check` clean; page count recorded
  before and after. One subagent at most, as a blind reader who lists
  every sentence it could not follow. Entry in ETH_AMBIGUOUS.MD for any
  passage where plainness and precision pulled apart. Ends with "what this
  does not claim".

- [ ] **09 The abstract, introduction and conclusion.**
  The title's sentence made precise in the first paragraph of the
  introduction (the four clauses: a guarantee, not a running time;
  existential constants never computed; `ρ(n) > n` for every `50 ≤ n <
  e^{5504}`; the sharper exponents unverified); the paper's one-paragraph
  summary (what the Lean statement says, what we replayed, what we
  inspected, what follows, what it changes for a practitioner); what is
  claimed and what is not, as a list; the stance sentence (a careful
  reading by people who checked; no flaw found). The conclusion reviews
  **every** `ETH_AMBIGUOUS.MD` entry to date and lists the ones that
  affect the text as open, by entry number. `paper3/latex/sec1_intro.tex`,
  `sec10_conclusion.tex`, the abstract in `main.tex`. Abstract under 200
  words; no number in it without a section that regenerates it.

- [ ] **10 Full build and refuter pass.**
  `make -C paper3/latex check` clean (no undefined reference or citation;
  `python3 -m paper1.latex.check_refs`-style DOI check adapted or run on
  `paper3/latex/refs.bib` if the script generalises; else every DOI
  checked by hand against Crossref and the check logged). Then **one**
  refuter subagent, blind to the sections' sources, reads the whole PDF
  against the clone (`cat`/`sed`, read-only), `paper.txt`, the two
  audits and `paper3/replay/logs/`, and files every disagreement (a
  wrong line number, a quote that differs, a number without a
  regenerate command, a sentence that reads as a debunking, a sentence
  out of scope — any graph, width or MOSP content — a claim the Lean
  statement does not support, the title altered anywhere). Each finding
  is fixed or recorded in `ETH_AMBIGUOUS.MD` with the reason it was not
  fixed. The refuter's report goes to `paper3/refuter/README.md` and the
  fixes are listed in PROGRESS.md.

- [ ] **11 The write-up around the paper.**
  `paper3/README.md` complete (title verbatim first; what the paper is;
  how to build; how to regenerate every number, section by section; the
  replay's status and its logs' hashes; the Lean names; the open entries
  of `ETH_AMBIGUOUS.MD` by number); the CLAUDE.md paragraph drafted into
  `paper3/README.md`'s last section, **not applied** to CLAUDE.md (the
  owner folds it); `reports/paper3_plan.md` §0 updated with what was
  done, item by item, in the past tense, with the gaps; the full gate
  (`python3 Ralph_Loops/loop0015/gate.py`) run and its tail recorded in
  PROGRESS.md.

- [ ] **12 Reserve.** The nanoda replay if item 01 could not do it (the
  sandbox left in place; `lean4export` at the matching toolchain on the
  solution module; nanoda built inside the sandbox; the result into
  `paper3/replay/` and `sec5_replay.tex` updated), or whichever of 02–10
  ended short (PROGRESS.md says which), one session with its own cap.
