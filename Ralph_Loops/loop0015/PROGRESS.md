# loop0015 progress

Paper 3: *Exponential time hypothesis is false... but the verified
algorithm is slower than trying all 2^n assignments at every practical
size.* (title fixed by the owner, verbatim). Plan: `reports/paper3_plan.md`;
items in `iterations.md`; rules in `TASK.md`. The paper is about the
limitation of the ETH refutation and nothing else. Gate:
`python3 Ralph_Loops/loop0015/gate.py`. Open questions for the owner:
`paper3/ETH_AMBIGUOUS.MD`.

Current: 0/12 SOLVED

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
