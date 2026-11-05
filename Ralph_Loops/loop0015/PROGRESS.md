# loop0015 progress

Paper 3: *Exponential time hypothesis is false... but the verified
algorithm is slower than trying all 2^n assignments at every practical
size.* (title fixed by the owner, verbatim). Plan: `reports/paper3_plan.md`;
items in `iterations.md`; rules in `TASK.md`. The paper is about the
limitation of the ETH refutation and nothing else. Gate:
`python3 Ralph_Loops/loop0015/gate.py`. Open questions for the owner:
`paper3/ETH_AMBIGUOUS.MD`.

Current: 11/13 SOLVED (item 08x added to the list on 2026-11-05)

## Setup — 2026-11-05

- Driver, gate and budget watcher cloned from loop0014
  (`sed s/loop0014/loop0015/`); `allowed_sorries.txt` empty;
  `knobs.json`: `max_iterations` 24, item cap 4 h, fix cap 0.75 h, 3 fix
  attempts, one retry after a network error, `stop` false.
- `loop.py` extended with a **per-item cap**: an item whose first line
  carries `[cap N h]` runs under that wall-clock cap (`item_cap`); item 01
  carries `[cap 8 h]`, every other item uses the 4 h knob. Every commit
  body carries the paper's title verbatim (`PAPER_TITLE`); `paper3/` is
  kept on a code revert (`KEEP_ON_REVERT`); the iteration prompt tells the
  session not to reword the title and to use `ETH_AMBIGUOUS.MD`.
- `gate.py` extended: runs `make -C paper3/latex check` once the Makefile
  exists (it does; a printed note otherwise), checks that
  `paper3/latex/main.tex` carries the title verbatim (after stripping the
  `$` and `\ldots` that are its only LaTeX), and fails if `git status`
  shows any change under `solutions/`.
- `budget_watch.py`: `BUDGET = 2500.0` (owner, 2026-11-05).
- Scope narrowed by the owner during setup: no graphs, pathwidth,
  treewidth, MOSP or width parameters; items 05 and 07 rewritten
  accordingly; the LaTeX skeleton and `refs.bib` carry no width material.
- `paper3/` created: `README.md`, `ETH_AMBIGUOUS.MD` (protocol header and
  the setup entries), `.gitignore`, `latex/` (`main.tex` with the title
  verbatim, `Makefile` with `check`, `refs.bib`, ten section stubs,
  `figures/`, `tables/`); `make -C paper3/latex check` passes on the
  skeleton.
- The OpenAI collection is cloned read-only under `~/dev/untrusted/`
  (commit `4eaee875`); nothing in it built or run at setup; the replay
  copy is item 01's.
- Not launched; not committed (the owner launches).

---

## Iteration 1 — 2026-11-05 02:05 (item 01, the replay) `[x]`

### Completed
- **The coordinator's run 1 (01:03) had failed at 01:13 before this
  session started**: `lake build … -j 8` → `error: unknown short option
  '-j'` (Lake 5.0.0 / Lean v4.34.1 has no jobs option); `DONE` = 1;
  nothing of the family compiled. The toolchain download and the Mathlib
  cache (8,908 files) had succeeded. The run-1 logs and scripts are kept
  (`paper3/replay/logs/run1/`).
- **The one relaunch** (run 2, 01:16:17): `-j 8` dropped, the core cap
  moved to `taskset -c 0-7` on the `bwrap` line, the `mathlib rev` log
  line fixed (`grep -B3`); launched through a `setsid nohup bash -c`
  wrapper so that `--die-with-parent` keeps a live parent. Result:
  **exit 0 in 33 min 6 s** (01:16:25 → 01:49:31), **3,091 distinct
  modules built = the audit's closure exactly** (set difference empty
  both ways against `reports/scratch/eth_audit/closure_modules.json`),
  **0 `error` lines, 0 `sorry`**, 11 warnings all the lakefile's
  "has local changes" compatibility patches; `#print axioms
  exact_count_and_sat` = `[propext, Classical.choice, Quot.sound]`;
  Lean 4.34.1 (commit 5045d005), Lake 5.0.0-src+5045d00, Mathlib
  `d13f23b7`; replay copy HEAD = pristine HEAD = `4eaee875`; the
  comparator and solution files hash identically in both. The build log
  itself records 19 `depends on axioms` lines from the 17 closure files
  that carry `#print axioms` (Final.lean 197–201 among them), all three
  standard axioms.
- **nanoda ran and passed** (`run_sandbox_nanoda.sh` / `nanoda.sh`,
  recorded in `paper3/replay/README.md` before launch, 01:50:55):
  `lean4export` v4.34.0 built with the pinned v4.34.1 in 3 s; the
  selective export of `exact_count_and_sat` and its dependencies in
  68 s (2,355,666,449 bytes, 43,633,742 lines, format 3.1.0);
  `nanoda_lib` 0.4.31 (commit `8de7e0c4`) built in 10.7 s and
  **`Checked 95176 declarations with no errors`** in 110 s, exit 0,
  three axioms permitted, three `axiom` declarations in the export.
- Written: `paper3/replay/README.md` (isolation, timeline, both scripts
  verbatim in both versions, launch command, every count and hash, the
  nanoda scripts and result, file index); `paper3/replay/counts.sh`
  (regenerates every number; output `logs/run2/counts.txt`);
  `paper3/replay/logs/{run1,run2,nanoda}/` (small logs, SHA-256 and
  last 200 lines of the 297 KB build log, hashes, versions, the in-build
  axiom lines, the nanoda config and output); `paper3/latex/sec5_replay.tex`
  ("Independent replay", four subsections, ends with "what this does not
  claim"; `make -C paper3/latex check` passes, 6 pages); `paper3/README.md`
  "The replay" paragraph; `ETH_AMBIGUOUS.MD` entries 01a–01d.
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  built inside the sandbox executed outside it (the export and the
  build log are read with `grep`/`sha256sum` only).

### Blockers
- None. The trust boundary now reads: the Lean kernel *and* nanoda agree
  on the exported dependencies; `lean4export`'s faithfulness and the
  textual (not `lean4export`-level) statement match remain, as the
  section says.

### Next
- Item 02 (the statement, read exactly); its "replayed" sentence is the
  one in `sec5_replay.tex` §5.2's last paragraph. Item 04 joins the
  inspection with this result (the first three items of the trust
  boundary moved; which of the remaining two the second kernel touches
  is stated in §5.4). Item 12's nanoda reserve is not needed.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` passed at 02:10 (exit 0;
  the `lake build` of `lean/` was incremental and quick, pytest took the
  time).
- Note for the driver's `git add -A`: `paper3/scripts/rho_over_n.py`,
  `paper3/latex/figures/rho_over_n.{pdf,png}` and
  `paper3/latex/tables/rho_over_n.csv` appeared at 02:07 from another
  Claude session on this machine (not this one; item 02's script by its
  docstring). They will be swept into this iteration's commit; item 02
  should treat them as its own starting point, not as item 01's work.

---

## Iteration 2 — 2026-11-05 02:19 (item 02, the statement read exactly) `[x]`

### Completed
- **Re-verified the comparator file line by line** against the clone at
  `4eaee875` (`cat -n`, 220 lines): every line number of
  `statement_audit.md` holds (SAT 13–51, encoding 53–81, `Trace` 87–90,
  `PrimitiveMachine` 92–99, `Cfg` 103–105, `step` 107–119, `init`
  121–124, `runtimeScale` 132–134, `runtimeBound` 136–139, `countWord`
  147, `LocatedCfg`…`visitedSpace` 149–189, the theorem 194–217, `sorry`
  218); Mathlib's `Stmt` (PostTuringMachine.lean 118–120), `Dir`
  (Tape.lean 421–423), `Tape` (408–414), `mk₁` (494) re-located; the
  manuscript's "log denotes the natural logarithm" at p. 1 lines 48–49
  (and p. 7 lines 326–327), Theorem 1.1 at p. 2 lines 56–62, "the weaker
  exponent" at p. 2 line 63, Proposition 6.4 with `n ⩾ 20` at p. 43
  lines 2474–2476, Appendix D's base-2 convention at p. 57 lines
  3251–3252.
- **One fact added beyond the audit**: the proof's own exponent constant
  is `A = 256 + A_t` with `1 ≤ A_t` (`SqrtLogSpace/NativeLargeEntry.lean`
  line 51; `NativeLeafContract.lean` lines 792–793; `1 ≤ C ∧ 1 ≤ A` at
  `NativeLargeEntry.lean` line 12), so the proof as written has
  `A ≥ 257`; quoted for the value only, flagged for item 04
  (`ETH_AMBIGUOUS.MD` 02c).
- `paper3/scripts/runtime_scale.py` (python3 -I, computes in
  `y = ln(n+16)`, imports nothing from the clone): prints the `ρ(n)/n`
  table at `n = 1, 20, 49, 50, 100, 125, 10³, 10⁶, 10¹², 10^23.7, 10^100,
  10^1000, e^5504, 10^3000`; `n = 50` first above 1 (`0.9994 / 1.0027`);
  peak `16/e² = 2.1654` at `ln(n+16) = e⁴` (`n ≈ 10^23.71`); back below 1
  at `ln(n+16) = 5503.7` (`n ≈ e^5504 ≈ 10^2390`, bracketed: 1.000049 at
  5503, 0.999951 at 5505). Writes `latex/tables/runtime_scale.tex` and
  `latex/figures/runtime_scale.{pdf,png}` (log-`n` axis 10…10^2500, the
  line, the level 1, the three landmarks, `50 ≤ n ≤ 10⁶` shaded).
- The owner's central figure (`rho_over_n.py`, from another session at
  02:07) kept as Figure 2.1, with two fixes: the peak made analytic
  (`10^23.7`, was the grid's `10^23.5`) and the `+16` written into the
  legend (02b).
- `paper3/latex/sec2_statement.tex` drafted (6 subsections, 7 pages:
  definitions one by one with lines; the theorem as an aligned display
  with each conjunct's lines; the quantifier order, no `n ≥ 20`, the
  existential constants; the numbers, Table 2.1, Figures 2.1–2.2; the
  title's claim in four numbered points; what the statement does
  establish, with the `O(n^k)` clause cap and the ETH citation; "what
  this does not claim"). `make -C paper3/latex check` passes, 13 pages,
  no overfull box from this section.
- `paper3/README.md` "How to regenerate every number" gets the Section 2
  paragraph; `ETH_AMBIGUOUS.MD` entries 02a–02d.
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone executed (read with `sed -n`/`grep` only).

### Blockers
- None.

### Next
- Item 03 (what the manuscript claims beyond the statement): Section 2
  already points at `sec:beyond` for the two sharper exponents and the
  base-2 `rho` of `Asymptotics.lean` lines 10–11 / 189–190.
- Item 04 should confirm the `A = 256 + A_t` reading (02c) and the
  `cutoff = max 20 (max Nleaf Ns)` at `NativeLargeEntry.lean` line 50.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 02:38
  (exit 0; pytest 1,978 + 123 passed, both papers build, title verbatim,
  `solutions/` untouched).

---

## Iteration 3 — 2026-11-05 02:45 (item 03, what the manuscript claims beyond the verified statement) `[x]`

### Completed
- **Read the manuscript's claims against the extract and the clone**,
  every one with page and line (page = form feeds before the line + 1;
  `paper.pdf` has 67 pages, not the 64 `TASK.md` says — 03b): Theorem 1.1's
  two bounds (p. 2, 56–62), the "weaker exponent" sentence (63–67),
  Proposition 6.4 (p. 43, 2474–2476) and its parameters (2480–2486), the
  self-reduction (68–71), Corollary 1.2 (77–94), the transfer caveat
  (95–99), Corollary 1.3 (100–120), Corollary 1.4 (p. 3, 123–127; proof
  pp. 51–52, 2925–2967, which names "the constant-density part of
  Theorem 1.1" at 2949), §1.1.1 (p. 4, 187–194), §1.1.2 (p. 5, 211–212),
  §1.1.3 (213–243), Corollaries C.1 (p. 51, 2912–2916) and C.2 (p. 52,
  2974–2977), Appendix D (p. 53, 3001–3028; proofs p. 54, 3045–3064 and
  p. 57, 3222–3250; the base-2 convention 3251–3252).
- **Tagged each** verified / supported / paper-only (the middle tag is
  new, 03a). Verified: the comparator statement, the space bound, the
  weaker exponent, Prop. 6.4's parameters (`Asymptotics.lean` 14–20
  define `sparsifyLambda`, `sparsifyNu`, `sparsifySchedule` exactly as
  the proof selects λ_n, ν_n, s), and the abstract's `2^{n/(log n)^{1/2+o(1)}}`
  as a form. Supported: self-reduction, Cor. 1.2 (stated with ρ(n) itself,
  03d), Cor. 1.3, Cor. C.1, Cor. C.2, the §1.1.1/§1.1.2 refutations, Set
  Splitting. Paper-only: both sharper exponents (`docs/378.md` line 11),
  Cor. 1.4, Appendix D, the §1.1.3 remarks.
- **What the library carries beyond the comparator theorem**, from
  `Final.lean` (201 lines, five theorems, `#print axioms` at 197–201, all
  five with the three axioms in the replay's build log): `exact_count_eth`
  (104–147) is Prop. 6.4's `(n+|F|+1)^d` form with `A·rho n` in base 2
  and `20 ≤ n` (its proof takes `2d`, `2e`, `4A` from the comparator's
  constants); `sat_polynomial_space` (149–183, `answer = true ↔
  Satisfiable`); `original_sat_main` (184) inhabits
  `SqrtLog.Statement.MainTheorem` (`StatementCanonical.lean` 37). An
  identifier search over the family's 3,977 files finds no corollary,
  hypothesis or tensor-network identifier; the strings ETH/SETH occur
  outside the family only in two `ParityLifts` files of another family,
  not in the closure.
- **The three exponents in numbers**: at constant 1 the general paper-only
  ratio `ln ln n/√ln n` peaks at `2/e = 0.736` (`n = e^{e²} ≈ 1,618`) and
  the fixed-density `1/√ln n` falls from 0.578 at n = 20; both are below
  1 at every size while the verified ratio is above 1 from 50 (Table 3.1).
- `paper3/scripts/beyond_claims.py` (python3 -I; reads the extract and
  the clone with `open()` only; checks 19 manuscript locations with
  fragments and pages, 16 Lean locations with fragments, the identifier
  absence, the ETH-string files against `closure_modules.json`, the
  exponent facts; writes `tables/beyond_claims.tex` and
  `tables/beyond_exponents.tex`; `ALL CHECKS PASSED`).
- `paper3/latex/sec3_beyond.tex` drafted (8 subsections, 7 pages: the
  scope note quoted in full, the three statuses, the sharper exponents,
  the corollaries one by one, Appendix D, the hypotheses and fine-grained
  remarks, what the library carries beyond the statement, the table,
  "what this does not claim"). `make -C paper3/latex check` passes, 20
  pages, no overfull box left in this section.
- `paper3/README.md` Section 3 regenerate paragraph; `ETH_AMBIGUOUS.MD`
  entries 03a–03d.
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing of
  the clone executed (read with `sed -n`, `grep`, `cat -n`, `pdfinfo` and
  the script's `open()` only).

### Blockers
- None.

### Next
- Item 04 (the proof inspection joined with the replay). Two line
  citations for it to carry: `runtimeScale_le_four_rho` is at
  `Asymptotics.lean` **190–191** (Section 2's text says 189–190; a
  one-number fix, left for item 04 or the refuter); the five `Final.lean`
  theorems and their `#print axioms` lines are listed above.
- Item 05 inherits from Section 3 the quotes it needs (§1.1.1 187–191,
  §1.1.3 226–236, the transfer caveat 95–99) with their pages.
- Item 11: `reports/paper3_plan.md` line 106 says "64 pages"; it is 67
  (03b).
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 03:15
  (exit 0; `lake build` ok; pytest 1,978 passed, 2 skipped, 1 xfailed in
  4:38, pathwidth_solver 123 passed in 6:34; paper 1 builds at 78 pages,
  paper 3 at 20; title verbatim; `solutions/` untouched).


---

## Iteration 4 — 2026-11-05 03:25 (item 04, the proof inspection joined with the replay) `[x]`

### Completed
- **Re-ran both audit scripts** read-only on the clone at `4eaee875`
  (`python3 -I reports/scratch/eth_audit/closure.py …`, 14 s;
  `defdiff.py`): the fresh run reproduces the audit's numbers exactly and
  leaves the committed `closure_modules.json` / `hits.json` byte-identical
  (`git status` clean there). Closure 3,091 modules / 550,551 raw lines /
  50 Mathlib modules + `Lean.Elab.Tactic.Omega` (imported at
  `FiniteFallback.lean:14`, `SparseCharging.lean:5`); 3,977 family files,
  886 outside the closure (no `sorry`/`axiom`/`native_decide`/`admit`,
  raw or stripped; `OAI.lean:49` the only family import; default target
  `lakefile.lean:89`); zero `axiom`, `sorry`, `admit`, `native_decide`,
  `ofReduceBool`, `implemented_by`, `extern`, `unsafe`, `partial`,
  `elab`, `macro`, `syntax`, `simproc`; two `set_option quotPrecheck
  false` (lines 15 / 14 of the two recovery files); nine `opaque`s all
  with bodies; 1,048 `noncomputable`; 4 / 4 / 8 explicit
  `Classical.choice` / `propext` / `open Classical`; 148 / 40 instances;
  9 / 5 termination clauses.
- **Statement match, counted afresh**: `defdiff.py` prints 32 `SAME` and
  4 it cannot match by itself; by hand, `countWord` is identical
  (challenge 147 = `EncodingBounds.lean` 17), `runtimeScale` /
  `runtimeBound` identical up to `noncomputable def` vs `noncomputable
  section` (`StatementScale.lean:15`), the theorem statement identical
  raw and normalised (1,353 / 1,124 characters; challenge line 194 =
  `Final.lean` 74; the challenge's `sorry` at 218). So **35 compared, 33
  identical, 2 up to the keyword** — the audit's "33" is explained (04a).
- **The spine, every line re-cited** (about 60 citations, each checked by
  the script): the machine (`Final.lean` 100, 40, 11; `BitProgram.lean`
  10–26; `GuardedCompiler.lean` 131–132, 14–17, 30–47), the time bound
  and constants (`NativeLargeEntry.lean` 11–33, 12, 27, 39, 46, 48, 50,
  51; `NativeLeafContract.lean` 793; `NativeOuter.lean` 53–56;
  `NativeEntry.lean` 81–100, 92; `NativeOuterBudgets.lean` 297, 317;
  `Final.lean` 41), the compile lemmas concluding in the comparator's own
  `Trace`/`locatedStep`/`visitedSpace` (`GuardedCompiler.lean` 158–162,
  152–153, 600; `CompileSpace.lean` 125–143; challenge 87–90, 149–189,
  201), the count (`NativeOuter.lean` 50–51, 73). **02c confirmed and
  sharpened** (04c): the comparator theorem's witnesses are
  `C + 28700, A + 1, S + 5022741, d + 2, e + 2` (`Final.lean:41`) with
  `A = 256 + At`, `1 ≤ At`, so the exhibited exponent constant is ≥ 258
  and the leading constant ≥ 28,701; `cutoff = max 20 (max Nleaf Ns)`
  confirmed at line 50.
- **What the repository does not record**: `#print axioms` in **8
  closure files / 19 commands** (17 files / 35 commands over the family
  directory, 9 of them dead) with no recorded output anywhere in the
  clone (`grep -rIl 'depends on axioms'` empty); CI = `lock-prs.yml`
  only; `enable_nanoda: false` on **413 of 418** challenge JSONs, `true`
  on 2, key absent on 3 (the item text's "416 of 418" corrected, 04b);
  manifest 42 packages (audit said 41, 04e), 23 patches none for
  Mathlib, toolchain `v4.34.1`, Mathlib `d13f23b7` upstream; the
  `run_cmd` (290–304) and `post_update` (306–) hooks.
- **Joined with item 01**: Table 4.2 — (i) the build **moved**, (ii) the
  axiom output **moved**, (iii) kernel + Mathlib **moved in part**
  (Mathlib observed upstream and unpatched; the kernel still trusted,
  now beside nanoda), (iv) the comparator run **not moved** (the match
  is textual), (v) the second kernel **moved** (95,176 declarations).
- Written: `paper3/scripts/proof_inspection.py` (python3 -I; re-runs
  the two audit scripts as subprocesses, 141 checks, writes
  `tables/proof_inspection.{tex,json}`, `--check`; `ALL CHECKS PASSED`);
  `paper3/latex/sec4_proof.tex` (9 subsections, pages 16–21: method,
  closure, keyword sweep with Table 4.1, the statement match, the spine
  in four paragraphs, toolchain and hooks, what the repository does not
  record, the trust boundary with Table 4.2, "what this does not claim");
  `make -C paper3/latex check` passes, 26 pages, **no overfull box in
  this section** (the long identifiers made breakable with `\path`, the
  section under `\sloppy`); `paper3/README.md` Section 4 regenerate
  paragraph; `ETH_AMBIGUOUS.MD` entries 04a–04e.
- **Two one-number fixes left by earlier items**: Section 2's
  `runtimeScale_le_four_rho` citation "189–190" → "190–191"
  (`sec2_statement.tex:329`); Section 5's "Seventeen source files of the
  closure" → "Eight … nineteen commands (seventeen files of the family's
  directory, nine never built)" and "the 33 definitions" → "the 35 …,
  two of them up to the `noncomputable` keyword" (04d, 04a).
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone executed (read with `open()`, `sed -n`, `grep`, `wc`,
  `git rev-parse` only; the two audit scripts read it the same way).

### Blockers
- None.

### Next
- Item 05 (the hypotheses and what a derived lower bound loses):
  Section 3 holds the quotes it needs (§1.1.1 187–191, §1.1.3 226–236,
  the transfer caveat 95–99, with pages).
- Item 08 (related work) should fetch and quote the comparator README
  and the nanoda README; Section 4 cites `\citep{LeanComparator}` and
  `\citep{Nanoda}` and says "Section 9 records the versions" — the
  `refs.bib` notes still say "recorded by item 08".
- Item 10 (refuter) may align Section 2's 02c sentence (`A ≥ 257`, the
  `run` constant) with Section 4's `A ≥ 258` (the comparator witness).
- Item 11: `TASK.md` line ~"416 of 418" and `proof_audit.md`'s 33 / 41
  are superseded by 04a / 04b / 04e; the audit is left as a dated
  scratch record.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 03:50
  (exit 0; `lake build` ok; pytest 1,978 passed, 2 skipped, 1 xfailed;
  pathwidth_solver 123 passed in 6:32; paper 1 builds at 78 pages,
  paper 3 at 26; title verbatim; `solutions/` untouched).


---

## Iteration 5 — 2026-11-05 (item 05, what follows in general terms) `[x]`

### Completed
- **Each hypothesis read in the form the manuscript states it**, with page
  and line of the extract and the manuscript's own source: ETH (p. 4,
  165–166, [IP01, Theorem 1]), SETH (166–169, [IP01, Open Problems, item
  2]), Gap-ETH (172–174, [Din16, MR17]) and its randomised form (175–176,
  [CCK+20, Conjecture 2.5]), NSETH (181–183, [CGI+16]), the randomised ETH
  and SETH by citation (190–191, [DHM+14, Section 1], [CDL+16, Definition
  2.1]), #ETH (204–205, [DHM+14, Section 1]); the refutation paragraph
  (187–191) and the #ETH sentence (p. 5, 211–212) quoted in full.
- **Each refuted from the comparator statement alone**, by one of its
  conjuncts (lines 194–217 at `4eaee875`): the answer bit
  `[0 < count F]` (205–207) for ETH, SETH, Gap-ETH and NSETH, the count
  tape (203–204) for #ETH; with the quantifier form stated each time —
  the single-machine `2^{O_k(ρ(n))}` form gives the uniform negation (one
  algorithm `O_δ(2^{δn})` for every `δ`), stronger than the `∀δ ∃` ETH
  negation; SETH negated directly at every `k` and every `ε` (the
  `(n+m)^{O_k(1)}` degree is what "for a fixed k" permits), with
  "SETH ⇒ ETH" recorded for the record through the Sparsification Lemma
  (`\citet{ImpagliazzoPaturiZane2001}`); the randomised and
  nondeterministic forms by "a deterministic machine is both"; the
  `2^{o(n)}`-in-`n`-alone step made explicit (`m ≤ Σ_{j≤k} C(2n,j)`, so
  `L = O(n^{k+1})`); no `n ≥ 20` proviso; the multitape model as the
  conservative one.
- **What a derived lower bound loses, in general terms** with no problem
  named: shapes (E) `ETH ⇒ no 2^{o(n)} for X` and (S) `SETH ⇒ no (c−ε)^k
  for Y`; the theorem stands, the premise is false, nothing is derived
  (the manuscript's "removes one basis", p. 5, 226–227, quoted); the
  conclusion is not refuted (the "reduction in the other direction",
  237–238, and the transfer caveat, p. 2, 95–99, quoted); hardness as a
  classification (ours, 05d); OVC and the unrestricted-width hypothesis
  untouched (229–236 quoted, the problem list elided for scope, 05a),
  with the quantifier reason (constants chosen after `k`, nothing bounds
  their growth); what a transferred algorithm inherits (Set Splitting,
  239–243: the title's limitation read through a reduction).
- `paper3/scripts/consequences.py` (python3 -I; reads the extract and
  the clone with `open()` only): 8 hypothesis locations, 14 quoted
  sentences, 9 bibliography entries, 12 comparator lines, the arithmetic;
  writes `tables/hypotheses.tex` (Table 6.1); `ALL CHECKS PASSED`;
  `--check` verifies without writing.
- `paper3/latex/sec6_consequences.tex` drafted (4 subsections, pages
  25–30: the one property every refutation uses, the hypotheses one by
  one with Table 6.1 and the two context sentences, what a derived lower
  bound loses in five paragraphs, "what this does not claim" in seven
  points). `make -C paper3/latex check` passes, 33 pages; no overfull
  box in the section (the (E)/(S) display split, an `\allowbreak` in the
  NSETH quotation's formula). No word of graphs, pathwidth, treewidth or
  MOSP in the section (grep).
- `refs.bib`: seven entries for the hypotheses' sources (Dinur 2016,
  Manurangsi & Raghavendra 2017, Chalermsook et al. 2020, Carmosino et
  al. 2016, Dell et al. 2014, Cygan et al. 2016, Williams 2016), each
  copied from the manuscript's reference list with its extract lines in
  the `note`, no DOI (nothing fetched; 05c).
- `paper3/README.md` Section 6 regenerate paragraph; `ETH_AMBIGUOUS.MD`
  entries 05a–05d.
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone executed (read with `sed -n`, `cat -n` and the script's
  `open()` only); no subagent used.

### Blockers
- None.

### Next
- Item 06 (the practitioner): Section 6's last paragraph ("what a
  transferred algorithm inherits") is the bridge to it; 05d offers to
  move that paragraph there.
- Item 08 may add the DOIs to the seven new `refs.bib` entries (05c) and
  Calabro–Impagliazzo–Paturi 2009 for "SETH ⇒ ETH" in words (05b).
- Item 10 (refuter): the `A ≥ 257` of Sections 2 and 6 against Section
  4's `A ≥ 258` (04c, 05d); the elided problem list in the §1.1.3
  quotation (05a) is the owner's call.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 04:23
  (exit 0; `lake build` ok, 0 sorry; pytest 1,978 passed, 2 skipped,
  1 xfailed in 4:37; pathwidth_solver 123 passed in 6:35; paper 1 builds
  at 78 pages, paper 3 at 33; title verbatim; `solutions/` untouched).


---

## Iteration 6 — 2026-11-05 04:35 (item 06, for the practitioner) `[x]`

### Completed
- **Tools found and installed**: no `sharpSAT`/`ganak`/`d4`/`approxmc`
  binary on the host; `python-sat 1.9.dev15` (CaDiCaL 1.9.5 as
  `cadical195`) present; `pyapproxmc 4.4.0` was *already* importable
  (the brief said not installed; 06b); `pyganak 2.8.0` (Ganak with Arjun
  preprocessing, Mate Soos) is on PyPI and was installed for the item —
  an exact counter, so enumeration is used only as the check at
  `n ≤ 30`. ApproxMC needs the projection set passed explicitly
  (`count(list(range(1, n+1)))`; with the default it returns 1).
- **The measurement** (`paper3/scripts/practitioner.py --regenerate`,
  1,172 s wall, 04:40–05:00, load 0.3 at start): random 3-CNF at
  `m = round(4.26 n)`, 13 sizes 20–500, 20 seeds each, each call in its
  own `python3 -I` under `nice -n 19`, 8 at a time, 60 s per call,
  censored above; a tool finishing fewer than 10 of 20 stops escalating.
  CaDiCaL: median < 1 ms to n = 80, 2.5 ms at 100, 58 ms at 200, 1.5 s
  at 250, 3.7 s at 300 (max 20.5 s), 10/20 within 60 s at 400, 8/20 at
  500 (every finished one satisfiable). Ganak: all 20 to n = 250
  (median 17.6 s there), 10/20 at 300, 0 at 400; a flat median of
  8.3 / 6.2 s at n = 100 / 150 that looks like a preprocessing budget
  in the binding (06d, reported as measured). ApproxMC: all 20 to 200
  (median 0.51 s), 18 at 250, 11 at 300, 0 at 400. Checks: Ganak =
  enumeration on all 40 instances at n ≤ 30; CaDiCaL's bit = `[count >
  0]` everywhere; ApproxMC within 1.8× of Ganak on 178/206 (it promises
  80%); the clone read with `open()` only has no `#eval`, no `def
  main`, no `IO` action in 3,977 family files and the comparator theorem
  is `∃ (machine : …)` at line 195 — so "no implementation exists to
  run" has a regenerate command. `ALL CHECKS PASSED`.
- **The guarantees beside them**: `2^n` and `2^ρ(n)` at constant 1 with
  one common factor `t20 / 2^20` (`t20 = 1.28e−4` s), so `2^n` passes
  through the n = 20 measurement and `2^ρ(n)` crosses it at n = 50
  (06a; the brief's per-curve scaling would hide the crossing). The
  scaled guarantees reach 1 s at n = 33 and 35; at n = 60 CaDiCaL's
  median is 11.6 and 12.2 decades below them, at n = 200 51.5 and 64.8,
  at n = 500 (censored) 138.8 and 190.4. `2^(ρ(n) − n)` = 1.10, 2.8 ×
  10³, 4.0 × 10⁵¹ at n = 50, 100, 500.
- Written: `paper3/scripts/practitioner.py` (`--regenerate`, default
  rebuild from CSV, `--check`, `--task` for the child); the raw CSV and
  `practitioner_meta.json` (versions, CPU, load, date, where each tool
  stopped) under `latex/tables/`; `latex/tables/practitioner.tex`
  (Table 7.1); `latex/figures/practitioner.{pdf,png}` (Figure 7.1, two
  panels: the measured seconds with the guarantees leaving the panel,
  and the same on the guarantees' scale; dataviz palette);
  `paper3/latex/sec7_practitioner.tex` (5 subsections, pages 31–35: why
  guarantees against measurements, what was run, what came out with the
  checks, the two guarantees beside them, "what this does not claim" in
  six points); seven `refs.bib` entries for the tools and the threshold
  (from memory, no DOI, flagged — 06c); `paper3/README.md` Section 7
  regenerate paragraph; `ETH_AMBIGUOUS.MD` entries 06a–06d. `make -C
  paper3/latex check` passes, 38 pages, no overfull box in the section
  (`\repofile` cannot sit in a caption: `\texttt` there).
- Nothing under `solutions/` touched; no MOSP or pathwidth run; the only
  compute is on the script's own random 3-CNF; nothing of the clone
  executed; no subagent used.

### Blockers
- None.

### Next
- Item 07 (the companion Lean) is independent of this section.
- Item 08 (related work) may add DOIs to the seven tool/threshold
  `refs.bib` entries (06c) and to item 05's seven (05c).
- Item 09/10: Section 6's last paragraph ("what a transferred algorithm
  inherits") and Section 7.1 say the same thing from two sides; 05d
  offered to move the former to Section 7, left in place here.
- Item 11: `pip uninstall pyganak` is the owner's call (06b).
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 05:24
  (exit 0; `lake build` ok; pytest 1,978 passed, 2 skipped, 1 xfailed;
  pathwidth_solver 123 passed in 6:32; paper 1 builds at 78 pages, paper
  3 at 38; title verbatim; `solutions/` untouched).


---

## Iteration 7 — 2026-11-05 05:25 (item 07, the companion Lean, axiom-audited) `[x]`

### Completed
- **Nothing moved.** The brief says `git mv` to `lean/MOSPFormalization/ETH/`;
  the owner's resolution of S3 (`ETH_AMBIGUOUS.MD`, "Owner resolutions")
  says "leave the Lean where it is … item 07 does not move anything", and
  the brief had not been amended. The owner's word was followed: the
  companion Lean stays at
  `lean/MOSPFormalization/SubexpPathwidth/{PrimitiveMachine,Frame}.lean`,
  namespace `MOSPFormalization.SubexpPathwidth`; `MOSPFormalization.lean`
  and the loop0014 crossover file are untouched; the S3 note planned for
  `reports/subexp_pathwidth.md` §2.1 is not needed (07a).
- **The byte-level re-diff** (`paper3/scripts/lean_rediff.py`, python3 -I,
  reads the clone with `open()` only; `--check`; log
  `paper3/lean/rediff.log`): our `PrimitiveMachine.lean` lines 31–221
  against the clone's comparator file lines 1–190 followed by 220 —
  **byte-identical, 191 lines each side, diff empty**; the clone's SHA-256
  `4183b205…` and commit `4eaee875` as the header records. Beyond the
  brief (07c): the body of `SubexpCount` (Frame.lean 85–107) against the
  body of `exact_count_and_sat` (clone 195–217, `:= by` removed) —
  **identical after whitespace normalisation (1,073 characters) and line
  by line after stripping indentation (23 lines; ours two columns further
  left)**, so "character for character" now has a regenerate command.
  Zero `sorry`, zero `axiom` declarations in our two files; the clone's
  one `sorry` at 218 is outside the copied range. `ALL CHECKS PASSED`.
- **The axiom audit** (`paper3/lean/axiom_check.lean`, paper 1's pattern
  without its `sorryAx` control line, 07b; run `cd lean && lake env lean
  ../paper3/lean/axiom_check.lean > ../paper3/lean/axiom_check.log`
  after an incremental `lake build`, 2 s, "Build completed successfully
  (8988 jobs)"): 21 declarations — the ten copied definitions the
  statement rests on, `SubexpCount`, `ExactCountAndSat`, and the nine
  lemmas and helper defs — **19 on exactly `[propext, Classical.choice,
  Quot.sound]`, `Computation.Trace` on none (inductive), `countWord` on
  `[propext, Quot.sound]`, `sorryAx` on none**. Lean 4.34.0-rc2 (commit
  `6a10ac8c`), Lake 5.0.0, Mathlib `1192d6246b46` (our library's toolchain,
  not the clone's `v4.34.1` / `d13f23b7`; the copied model elaborates on
  both, which the section calls small evidence and no more).
- Written: `paper3/lean/README.md` (the files with the line of every
  cited name, the eight Appendix rows, the audit command and result with
  versions, the three re-diff checks, what this does not claim);
  `paper3/latex/sec8_lean.tex` (pages 35–38, five subsections in plain
  English: the copy, the restatement, what is proved and what it means
  in words, the axiom audit, "what this does not claim" in six points; a
  Prop / def / theorem / axiom gloss up front; no crossover or pathwidth
  statement cited — the directory name is the only occurrence of the
  word, 07a); `paper3/latex/secA_appendix_lean.tex` (eight `\leanentry`
  rows in three groups, the placeholder removed, the `ETH/` preamble
  rewritten); `paper3/README.md` (the `lean/` layout row and the Section
  8 regenerate paragraph); `ETH_AMBIGUOUS.MD` entries 07a–07c.
- **One paper-wide typesetting fix**: `\_` inside `\repofile{}`,
  `\clonefile{}` and `\leannames{}` (verbatim-style `\path`) printed a
  literal backslash — 11 places on pages 5, 8, 13, 14, 38, 39 of
  Sections 2, 3, 10, 12 and in my own two files. Replaced by a plain `_`
  inside those three macros only (`\texttt{…\_…}` untouched); the PDF
  now has zero literal `\_`. Also a Unicode `ℕ` in Section 8's text
  (`inputenc` cannot typeset it) became `$\mathbb{N}$`. `make -C
  paper3/latex check` passes, 42 pages, no overfull box in Section 8 or
  Appendix A (both under `\sloppy`, as item 04's section is).
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone executed (read with `open()`, `sed -n`, `sha256sum`,
  `git rev-parse` only); the only Lean run is on our library; no
  subagent used.

### Blockers
- None.

### Next
- Item 08 (related work): `refs.bib` notes still say "recorded by item
  08" for `LeanComparator` and `Nanoda`; Section 8 cites neither.
- Item 10 (refuter): Section 8's "character for character" is defined
  as the normalised equality of 07c — Section 2 line ~352 and
  Frame.lean's docstring use the phrase without that definition; align
  if wanted. The two acceptance readings of 07b (lines with fewer than
  three axioms) are the owner's call.
- Item 11: `reports/paper3_plan.md` §0.4.7 and the item table still say
  the Lean is moved to `ETH/`; `TASK.md` Context and Acceptance likewise;
  superseded by the owner's S3 resolution and 07a. `paper3/lean/README.md`
  records the audit's repository commit as `95eb564a0` (the HEAD when it
  ran; the driver's commit of this iteration will be the one that holds
  the files).
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 05:46
  (exit 0; `lake build` ok; 1978 passed, 2 skipped, 1 xfailed, 180 warnings in 277.76s; 123 passed in 393.59s; paper 1 builds at 78 pages, paper 3 at 42; title verbatim;
  `solutions/` untouched).


---

## Iteration 8 — 2026-11-05 05:55 (item 08, related work and context) `[x]`

### Completed
- **Fetched, exactly the three pages the brief allows plus their public
  metadata records** (05:59 UTC, `curl`, into `paper3/related/fetched/`,
  eight files, each hashed; `paper3/related/README.md` lists file, URL and
  what was *not* fetched; 08b): the arXiv API record and abstract page of
  2608.14673 (v1 3 Aug, v2 25 Aug, v3 9 Sep 2026; "13 pages, 27
  references"; cs.AI; the record spells the title `OpenAIs`, 08a); the
  `master` README of `leanprover/comparator` (208 lines; latest commit
  `865edc14` of 2026-10-14 "doc: migration notice"; **archived**, its line
  3 says the tool "has been merged into core as of Lean release v4.35.0 in
  the form of `lake comparator`"; neither repository has a `main` branch);
  the `master` README of `ammkrn/nanoda_lib` (85 lines; latest commit
  `8de7e0c4` of 2026-10-29 = **the commit the replay built**, checked
  against `replay/logs/nanoda/nanoda_sandbox.txt`; Apache-2.0).
- **Read in the clone at `4eaee875`** (`cat -n`/`sed -n`/`open()` only):
  `history.md` line 18 under "October 26, 2026" (line 11), quoted in full
  — the working-group sentence ("will examine and explain the proof"; the
  log has no word "audit" or "review", and its one "verif" is another
  family's Python checker, line 27); `lean/docs/378.md` (already quoted
  in full by Section 3; here as the collection's own record of the weaker
  exponent, which does not say what it means at any size);
  `lean/ComparatorChallenges/README.md` (10 lines, line 3 and the three
  commands) and `SubexponentialSAT.json` (six fields, `enable_nanoda:
  false`, no `external_kernels`). The manuscript's own `[IP01]`/`[IPZ01]`
  entries at extract lines 3733–3736 (page 66) and the "over exhaustive
  search diminish as k grows" sentence at 170–171 (page 4).
- **Holdings**: `literature/` has neither Impagliazzo–Paturi 2001 nor
  Impagliazzo–Paturi–Zane 2001 nor the audit paper; a "Paper 3, related
  work" section is appended to `literature/MISSING.md` with the three
  (DOIs from the setup's Crossref check for the two JCSS papers) and a
  pointer to the fourteen unchecked-DOI entries of items 05 and 06 (08c:
  not fetched, Crossref is outside the download list).
- `paper3/scripts/related_work.py` (python3 -I; `--check`): hashes the
  eight fetched files; checks 60-odd quoted fragments at their lines (the
  arXiv record's title, authors, dates, class, comment and five abstract
  sentences, and that the abstract names neither 378 nor ETH; 33
  comparator README lines; 7 nanoda README lines; both API records and
  commits; the clone's four texts and the JSON's six fields; the clone's
  commit read from `.git` without running git; the extract's six lines
  with their pages); the holdings; the replay's nanoda commit; and runs
  the **prior-statement word search** over the six texts ("practical",
  "brute", "trying all", "exhaustive", "2^n", "constants are",
  "concrete"): none outside the manuscript; in it "practical" once (line
  153, the practical value of SAT solvers) and "exhaustive" eleven times
  (170 the SETH motivation, 2480/2487 the proof's small-case fallback).
  Writes `tables/related_sources.tex` (Table 9.1). `ALL CHECKS PASSED`.
- `paper3/latex/sec9_related.tex` drafted in plain English (pages 38–43 of
  48, seven subsections: what the collection says about itself; the two
  hypothesis papers, cited through the manuscript and not read; the human
  audit of the 1 August results — four abstract sentences quoted, the
  "overbar lost during PDF extraction" taken as a warning and tied to our
  page-plus-line and read-the-Lean-from-source rules; the comparator —
  its three guarantees as a three-line quote, the six assumptions with
  the kernel one quoted, Internals steps 4–6, `landrun`, external kernels
  and `enable_nanoda`, the Lean FRO / AIMO acknowledgement, and family
  378's JSON read against them: the configured check is the Lean kernel
  alone, Section 5 is the weakened fifth assumption supplied by us; nanoda
  — four README lines, the commit identity with the replay; **"we found
  no prior statement" bounded to the six texts** with the two nearest
  earlier statements named (the manuscript's "weaker exponent" sentence,
  the scope note), 08d; "what this does not claim" in six points).
  `make -C paper3/latex check` passes, 48 pages, **zero overfull boxes in
  the section** (the sources table made breakable with `\path` and
  ragged-right columns; `\repofile` cannot sit in a caption, as item 06
  found).
- `refs.bib`: `LeanComparator` and `Nanoda` completed with commit, date,
  branch, licence and the archived/merged status; `SienickiSienicki2026`
  with the three version dates and the record's spelling; two `@misc`
  entries added for `lean4export` and `landrun` by the URLs the comparator
  README gives (lines 10–11, "page not fetched"); the header's "item 08
  completes" sentence resolved. `paper3/README.md`: Section 9 regenerate
  paragraph and a `related/` layout row. `ETH_AMBIGUOUS.MD` entries
  08a–08d.
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing of
  the clone executed; the fetched files never executed, imported or
  rendered; no subagent used.

### Blockers
- None.

### Next
- Item 09 (abstract, introduction, conclusion): Section 9.1 quotes the
  working-group sentence and 9.6 bounds "no prior statement"; the
  introduction may reuse the former and must not widen the latter.
- Item 10 (refuter): Section 9's quotations are all located by the
  script; the two JCSS papers are cited unread (9.2 says so) — the owner
  may want them obtained (MISSING.md) before submission.
- Item 11: `paper3/README.md`'s Section 9 paragraph is written; the
  CLAUDE.md paragraph may mention that `leanprover/comparator` is
  archived and merged into Lean core at v4.35.0 (one release above the
  clone's pin).
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 06:22
  (exit 0; `lake build` ok; pytest 1,978 passed, 2 skipped, 1 xfailed in
  4:36; pathwidth_solver 123 passed in 6:35; paper 1 builds at 78 pages,
  paper 3 at 48; title verbatim; `solutions/` untouched).


---

## Iteration 9 — 2026-11-05 06:30 (item 08x, the plain-English rewrite of every section drafted so far) `[x]`

### Completed
- **Sections 2–8 rewritten sentence by sentence** to the owner's rule
  of 2026-11-05 05:30 (`paper3/latex/sec2_statement.tex` …
  `sec8_lean.tex`): short sentences, one idea each; every symbol
  defined in words on first use and paraphrased where it carries the
  argument (`ρ(n)` as "the exponent", `C(L+1)^d 2^{Aρ(n)}` as "the
  bound", `2^n` as "trying every assignment", `o(n)` as "grows more
  slowly than n", `O_k(1)` as "a constant that depends only on k");
  every term of art glossed in one clause on first use in its section
  (Lean, kernel, formula, k-CNF, satisfying assignment, comparator,
  axiom, lemma, Turing machine, configuration, polynomial in Section 2;
  closure, type-checks, typeclass instance, non-constructive, manifest,
  hook, environment in Section 4; namespaces in Section 5; hypothesis,
  ETH, SETH, derived lower bound, Sparsification Lemma, DNF/tautology,
  regular resolution, Merlin–Arthur, Set Splitting in Section 6; SAT
  solver, CDCL, model counter, censored, projection set in Section 7;
  Prop/def/theorem/axiom, namespace, located step in Section 8); every
  figure and table caption rewritten so that a layperson can read the
  columns and the curves ("a curve above the line is a guarantee worse
  than trying every assignment"; "each grid line is ten times the one
  below"). Section 9 (drafted after the rule, already plain) and
  Appendix A (a table of names) untouched (08xb).
- **Nothing lost in precision**: "the verified guarantee" where that is
  the fact, "verified" / "supported" / "paper-only" / "not verified" on
  every claim, every "what this does not claim" list kept. A script
  compared each old section (git `521b617e0`) with its rewrite: **every
  citation key, every `\ref`/`\leanref`, every `\label`, every file
  path and every number of the old text is present in the new text or
  in Appendix B**; the handful of literal identifiers the rewording
  dropped (`SqrtLog.ExecutionNativeFinal`, `SqrtLogSpace.Final`,
  `@[default_target] lean_lib OAI`, `definition_names`, `tmpfs`,
  `lakefile`, the `Nat`/`String` literal extensions, `IO`,
  `perf_counter`) were restored by hand.
- **Dense passages moved, not cut, into a new Appendix B** "Technical
  detail behind the plain text" (`paper3/latex/secB_appendix_technical.tex`,
  `\input` after Appendix A in `main.tex`; labels `app:tech`,
  `app:tech-definitions`, `-theorem`, `-spine`, `-keywords`,
  `-hypotheses`, `-scaling`): the comparator definitions line by line,
  the theorem with its quantifiers and the proof's constants, the spine
  of the proof with every name and line and the 35/33/2 statement
  match, the keyword sweep item by item with the lakefile hooks, the
  hypotheses in quantifier form with their negations and the shape-(S)
  arithmetic, and the scaling of the two guarantee curves. The body
  cites each subsection where it states the fact in words (08xa).
- **Readability measured** (sentences from the `.tex` with LaTeX
  stripped, old → new): mean words per sentence 30.2 → 17.9 (Section
  2), 29.6 → 25.6 (3), 29.3 → 22.6 (4), 33.8 → 24.8 (5), 32.0 → 28.3
  (6), 34.5 → 27.9 (7), 22.5 → 21.4 (8); share of sentences over 35
  words 25% → 4%, 33% → 21%, 30% → 16%, 40% → 18%, 30% → 22%, 42% → 26%,
  15% → 16%. Sections 3 and 6 stay longest because their quotations
  from the manuscript are kept verbatim.
- **One blind-reader subagent** (the item's one; read Sections 2–8 of
  the built PDF as a layperson, edited nothing): **no overclaim found**
  ("every section's 'what this does not claim' keeps to the guarantee");
  about fifty stalls listed, almost all a term used before its gloss.
  **All addressed** by 56 one-clause glosses or re-orderings in the
  places it named (axiom, lemma, Turing machine, configuration,
  polynomial, `O(knm)`, `o(n)`; the corollaries' objects — circuit,
  independent set, proper colouring, perfect matching, circuit lower
  bound, `E^NP`, constant-locality, one-way function, tensor network;
  closure, Prop, "inhabitant"; type-checks, typeclass instances, choice
  principle, "eventually", "it elaborates" → "Lean accepts it",
  manifest, hooks, environment; namespaces; uniform denial, models of
  computation, `s_k`, Sparsification Lemma, DNF/tautology, regular
  resolution, Merlin–Arthur, Set Splitting; cavity method, Arjun,
  projection set; namespace, located step, "countWord on two of the
  three"); its two borderline phrasings in Section 7 reworded ("not the
  one that matters" → "not the binding one"). Its three "clearest"
  passages (the Section 2 glossary, the four numbered points of 2.5,
  the "theorem stands; premise false; derives nothing" paragraphs of
  6.3) are the model the rest was pulled toward.
- **Pages before / after: 48 / 55** (`make -C paper3/latex check`
  passes; the 7 extra pages are Appendix B and the glosses). Overfull
  boxes: the baseline build of `521b617e0` had 8 (one in Section 2,
  five in Section 5, two in Appendix A's `longtable`); after this item
  2, both the pre-existing Appendix A ones (item 07's file, not
  rewritten here; left for item 10, 08xb).
- Scope check: no word of graphs, pathwidth, treewidth or MOSP added;
  the only occurrences in Sections 2–8 and Appendix B are the
  `SubexpPathwidth` directory name (07a), the manuscript's own
  Corollary 1.3 objects ("a graph on v vertices", item 03's text) and
  the `SimpleGraph` identifier in the absence search.
- `paper3/README.md` layout row notes the rewrite and Appendix B;
  `ETH_AMBIGUOUS.MD` entries 08xa–08xd (plainness vs precision and the
  new appendix; Section 9 / Appendix A untouched; per-section glosses
  pending item 09's introduction; the `A ≥ 257` / `A ≥ 258` readings
  reconciled in Section 2's text).
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone executed; no script re-run (no number changed); one
  subagent used.

### Blockers
- None.

### Next
- Item 09 (abstract, introduction, conclusion): the introduction's
  first-use glosses may make the per-section ones redundant (08xc); the
  abstract and introduction carry no formula beyond `2^n` by the rule.
- Item 10 (refuter): read the whole paper for readability once more
  (Section 9 and the appendices were not re-read here); the two
  Appendix A overfull boxes; the "character for character" phrase is
  now defined in Section 8 and used in Sections 2, 4 and 5.
- Item 11: `paper3/README.md`'s regenerate paragraphs are unchanged
  (no number moved); Appendix B's cited line numbers are the same ones
  the Section 2–7 scripts check.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 06:57
  (exit 0; `lake build` ok; pytest 1,978 passed, 2 skipped, 1 xfailed in
  4:36; pathwidth_solver 123 passed in 6:33; paper 1 builds at 78 pages,
  paper 3 at 55; title verbatim; `solutions/` untouched).


---

## Iteration 10 — 2026-11-05 07:05 (item 09, the abstract, introduction and conclusion) `[x]`

### Completed
- **The abstract** (`paper3/latex/main.tex`): 198 words (counted with
  `\emph` stripped and `$2^n$` as one word), no formula beyond `2^n`,
  two numbers only — the crossing at 50 variables and the 2,391 digits
  of `e^5504`, both Section 2's (`paper3/scripts/runtime_scale.py`);
  the result's month, "the 2001 conjecture", the no-flaw sentence, the
  four clauses in words, and "nothing changes on any machine".
- **The introduction** (`sec1_intro.tex`, five subsections): the
  title's four clauses made precise in the first paragraph (a
  guarantee, not a running time; constants that exist and are never
  computed, at least 257 where the proof writes one down; the exponent
  above the number of variables from 50 variables to a number with
  2,391 digits, so the verified bound is above `2^n` there; the sharper
  exponents not in the library), every number with its section; the
  stance paragraph ("a careful reading by people who checked, not a
  debunking … found no flaw"); a glossary of the words the whole paper
  needs (formula, satisfies, k-CNF, clause width, trying all `2^n`
  assignments, ETH, SETH, guarantee vs running time, Lean, kernel,
  Mathlib, comparator, challenge file, solution, nanoda, replay,
  sandbox, pinned, SAT solver, model counter), placed before the
  summary so that nothing is used before its gloss; the one-paragraph
  summary (statement, beyond, inspection, replay, consequences,
  practitioner, our Lean, related work) with its numbers (257; 2.17
  near a 24-digit `n`; 3,091 files; 33 minutes; 95,176 declarations;
  500 variables) each cited to its section; "what is claimed" (six
  points) and "not claimed" (six points) as lists; the organisation
  paragraph; "what this does not claim".
- **The conclusion** (`sec10_conclusion.tex`, three subsections): the
  paper's findings in one paragraph with the two facts that are true
  at once (the limit theorem in our Lean; the practical range); the
  claims and non-claims in one sentence each; and **the review of every
  `ETH_AMBIGUOUS.MD` entry to date** — 48 (S1–S8, 01a–08xd, and this
  item's 09a–09d) — sorted into resolved by the owner in writing (7:
  S1, S3 with 07a, S4, S6, S7, S8), procedural or corrections already
  carried by the text (8: S5, 01a, 03b, 04b, 04d, 04e, 06b, 08xb), and
  **open and affecting the text (33)**, listed by entry number in
  groups by the section each touches with one clause each, and a
  closing count of the thirteen that are bibliographic or typographic;
  "what this does not claim" (entries added by the refuter are not in
  it).
- **One blind-reader subagent** (the item's one) read the abstract,
  Section 1 and Section 10 against Sections 2–9 and the ledger. Its
  arithmetic check of §10.2 passed (7 + 8 + 33 = 48, every entry once,
  the thirteen correct). It found eight slips, **all fixed**: "the
  forty-year-old conjecture" (ETH is from 2001 → "the 2001 conjecture";
  the same phrase in Section 4's "a verified refutation of a
  forty-year-old hypothesis" → "twenty-five-year-old", one word in item
  04's text); "On 25 October 2026 … added" (Section 9: entered the
  collection on 26 October → "In late October 2026 … a result dated 25
  October 2026"); Section 2's own "a number with 2,390 digits" at one
  place against its "2,391 digits" elsewhere (→ 2,391, one number in
  item 02's text; `e^5504 ≈ 10^2390.3` has 2,391 digits); the
  conclusion's pairing "257 … 28,701" (Section 4 pairs 258 with 28,701
  → both readings stated, 08xd); "the one place the proof writes a value
  down" (three lines are cited → "where the proof does write a value
  down"); "ETH, SETH, Gap-ETH, NSETH, #ETH and their randomised forms"
  (Section 6 states randomised forms for ETH, SETH and Gap-ETH only →
  so worded, in the summary and in claim 5); nanoda "shares no code
  with Lean" (→ "with Lean's own [checker]"); "95,176 exported
  dependencies" (→ "95,176 declarations, the theorem and everything it
  depends on"). Its readability stalls (the glossary after its first
  uses; sentences of 40–73 words; "sandbox", "pinned", "circuit lower
  bound", "tensor contraction", "nondeterministic", "Mathlib", "clause
  width" unglossed) were addressed by moving the glossary ahead of the
  summary, adding the seven glosses, and splitting every sentence it
  named. No debunking sentence, no out-of-scope word (its items 4 and
  5: none).
- `make -C paper3/latex check` passes, **62 pages** (55 before; the
  introduction is 4 pages, the conclusion 3); the only overfull boxes
  are the two pre-existing ones in Appendix A's `longtable` (08xb, item
  10's). Page 1 rendered and looked at: title verbatim with `2^n`
  typeset, author line, abstract.
- `paper3/README.md`: a "Sections 1 and 10" regenerate paragraph (no
  number of their own; which sections each number belongs to; the
  abstract's word count; what §10.2 sorts) and the "Open questions"
  section pointing at §10.2; `ETH_AMBIGUOUS.MD` entries 09a–09d (the
  third clause in words, by the plain-English rule over the brief;
  which numbers the abstract carries; how the conclusion sorts the
  entries; "people who checked" with one author line and no co-author
  credit applied).
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone read or executed (every fact is from Sections 2–9 and
  the ledger); one subagent used.

### Blockers
- None.

### Next
- Item 10 (refuter): Section 4's "twenty-five-year-old hypothesis" and
  Section 2's "2,391 digits" are the two one-word edits outside this
  item's files, made for consistency and listed here; the two Appendix
  A overfull boxes; the per-section glosses now duplicated by §1.1
  (08xc, the owner's call); the README's older "ETH, SETH, Gap-ETH,
  #ETH and their randomised forms" sentence (item 11's text) could be
  aligned with claim 5's wording.
- Item 11: §10.2's sorting is the list the README's "Open questions"
  section needs, plus the refuter's entries; `paper3/README.md`
  already points at it.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 07:38
  (exit 0; `lake build` ok; pytest 1,978 passed, 2 skipped, 1 xfailed
  in 4:36; pathwidth_solver 123 passed in 6:32; paper 1 builds at 78
  pages, paper 3 at 62; title verbatim; `solutions/` untouched). A
  first gate run was started before the reader's fixes and stopped by
  PID; its python child survived the shell for eight minutes beside
  the second run (two `lake build`s of `lean/` briefly overlapped) and
  was killed by PID; the pass above is a third, clean run on the final
  files.


---

## Iteration 11 — 2026-11-05 07:46 (item 10, full build and refuter pass) `[x]`

### Completed
- **Full build**: `make -C paper3/latex check` clean at the start (62
  pages; no undefined reference or citation; the two overfull boxes of
  Appendix A, 08xb) and at the end (62 pages, **zero overfull boxes**:
  `\leangroup`'s non-wrapping `l` cell replaced by a wrapping `p{}` cell
  in `main.tex`).
- **The DOI check**: `paper3/scripts/check_refs.py` (reuses paper 1's
  checker; `--lookup` searches Crossref for entries without a DOI;
  cache `paper3/latex/data/doi_check.json`; run of record
  `paper3/latex/doi_check.log`). The two DOIs on file agree; **thirteen
  DOIs found and added** for the entries items 05, 06 and 08 had left
  "no DOI checked" (two LIPIcs ones through DataCite); Dinur 2016 is an
  ECCC report with none; Mertens 2006 accepted as `known` (HTML italic
  tags in Crossref's title; year 2005 online-first vs 2006 volume). 22
  entries, 15 with a DOI, 0 disagree. The item names Crossref, so it was
  queried although the download list does not list it (10a).
- **One refuter subagent**, blind to the LaTeX, the scripts and the
  loop's notes, read the whole 62-page PDF against the clone (read-only),
  the extract, the two audits, the replay logs, the fetched texts, the
  companion Lean and the measurement's data files, and its own
  arithmetic (49 tool calls, 16.5 min). Report verbatim in
  `paper3/refuter/REPORT.md`; the item's account, every finding with
  what was checked and done, in `paper3/refuter/README.md`. **21
  findings: A 6, B 4, C 1, D 0, E 0, F 5, G 5; 17 fixed, 4 recorded.**
  Every central number agreed (every `ρ(n)/n`, the peak, the crossing,
  the 2,391 digits, every comparator line number, every replay and
  nanoda number, every related-work quotation, all of Table 7.1); no
  scope or title finding.
- **Fixed, each verified against the source first** (sections in
  `paper3/latex/`): R1 §3.5's "ETH/SETH occur only in two ParityLifts
  files" was false — "ETH" also occurs in six comment lines of five
  family files and in the name `exact_count_eth` (rewritten; the count
  is now check 4b of `beyond_claims.py`); R2 "practical" at line 153 is
  on page 3, not 4 (fixed; the page is now a check in
  `related_work.py`); R3 the line counts 550,551 / 2,873 are
  `split('\n')` counts, one more per file than `wc -l` (547,460 /
  2,872) — convention stated with both figures; R4 §5.1's "41
  dependencies" → 42 (manifest and `.lake/packages` both 42; replay
  README corrected); R5 `Final.lean` lines 98–101 do not hold the "80
  registers", line 11 does (both places); R6 `primitive_execution` is at
  160–162, not 158–162; R7 the encoding lengths are one seed-1 random
  formula's (`check_encoding.py` line 20), said so in §2.2 and B.1; R8
  "721 families" → "721 manuscripts in 373 families" (the collection's
  README line 16; replay README corrected); R9 the three no-entry-point
  patterns stated as whole words; R10 "14,034 lines with decide"
  attributed to `closure.py`'s stripping; R12 B.6's ρ(50) = 50.13 →
  50.14, "equal to 1 up to rounding" → "just above 1, ratio 1.10"; R13
  Table 7.1's "sat" caption matched to its cells; R14 §8.1's "no sorry
  and no axiom anywhere" → "outside its comments", the three comment
  lines named; R15 `lean4export`, `tmpfs`, SHA-256 and `⌊4.26 n⌉`
  glossed at first use; R16 the 21 named long sentences (59–151 words)
  split one idea per sentence, quotations intact (crude whole-PDF count
  of pieces over 59 words 90 → 71, mean 28.9 → 27.6); R18 "undefined
  below n = e" → "negative below n = e (undefined at n ≤ 1)"; R20
  Figure 7.1's "The same data" → "Table 7.1's data"; R21 "line 44" →
  "lines 44–45". Also, outside the list: Section 7's sentence pairing
  `A ≥ 257` with `C ≥ 28,701` now gives both readings with their
  sections (item 09's reader had flagged the same pairing elsewhere).
- **Recorded, not fixed**: R11 the title's "is slower" read literally
  against the paper's own non-claim of any running time — the title is
  the owner's; the reconciliation rests on §2.5 and §7.4 (10b); R16's
  remaining ~40 sentences of 46–58 words (10c); R17 item 11's
  placeholders and R19 the audits' superseded counts, left as dated
  scratch records for item 11's note, the loop's own replay README
  corrected in three cells (10d).
- **Every check script re-run and passing** on the final text:
  `beyond_claims.py --check` (with the new 4b), `proof_inspection.py
  --check`, `consequences.py --check`, `lean_rediff.py --check`,
  `related_work.py --check` (with the new page check),
  `practitioner.py --check`, `runtime_scale.py`, `check_refs.py`.
  `paper3/README.md`: a bibliography paragraph and an item-10 paragraph
  under "How to regenerate", the `refuter/` layout row; `ETH_AMBIGUOUS.MD`
  entries 10a–10d.
- Nothing under `solutions/` touched; no MOSP or pathwidth run; nothing
  of the clone executed (read with `grep`, `sed`, `ls`, `python3 -I`
  and the scripts' `open()` only); the only network access was
  Crossref/DataCite metadata for the DOI check; one subagent used.

### Blockers
- None.

### Next
- Item 11 (the write-up around the paper): the placeholders of the data
  statement and the acknowledgements (R17); the one-line "superseded
  counts" note at the top of each audit (R19, 10d; 04a / 04b / 04e);
  `paper3/README.md`'s "Open questions" section listing every entry,
  now 52 (S1–S8, 01a–09d, 10a–10d); the CLAUDE.md paragraph; the plan's
  §0 (67 pages, 03b; the Lean left in place, 07a; Crossref queried,
  10a). The conclusion's §10.2 sorts 48 entries and says the refuter's
  are not in it; item 11 may add 10a–10d to the README list only, or
  to §10.2 as four more open entries (10a bibliographic, 10b–10d
  affecting the text).
- Item 12 (reserve): a second plain-English pass over the sections 10c
  names, if the owner wants the 46–58-word sentences split too.
- Gate: `python3 Ralph_Loops/loop0015/gate.py` **GATE PASS** at 08:24
  (exit 0; `lake build` ok, 0 sorry; pytest 1,978 passed, 2 skipped,
  1 xfailed in 4:36; pathwidth_solver 123 passed in 6:33; paper 1 builds
  at 78 pages, paper 3 at 62; title verbatim; `solutions/` untouched).
