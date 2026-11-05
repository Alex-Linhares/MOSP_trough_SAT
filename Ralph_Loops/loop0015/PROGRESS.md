# loop0015 progress

Paper 3: *Exponential time hypothesis is false... but the verified
algorithm is slower than trying all 2^n assignments at every practical
size.* (title fixed by the owner, verbatim). Plan: `reports/paper3_plan.md`;
items in `iterations.md`; rules in `TASK.md`. The paper is about the
limitation of the ETH refutation and nothing else. Gate:
`python3 Ralph_Loops/loop0015/gate.py`. Open questions for the owner:
`paper3/ETH_AMBIGUOUS.MD`.

Current: 2/12 SOLVED

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
