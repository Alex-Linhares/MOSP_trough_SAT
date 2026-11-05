# loop0015 progress

Paper 3: *Exponential time hypothesis is false... but the verified
algorithm is slower than trying all 2^n assignments at every practical
size.* (title fixed by the owner, verbatim). Plan: `reports/paper3_plan.md`;
items in `iterations.md`; rules in `TASK.md`. The paper is about the
limitation of the ETH refutation and nothing else. Gate:
`python3 Ralph_Loops/loop0015/gate.py`. Open questions for the owner:
`paper3/ETH_AMBIGUOUS.MD`.

Current: 1/12 SOLVED

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
