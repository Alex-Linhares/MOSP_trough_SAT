# TASK: Strengthen paper 2, "The pathwidth complex", toward a first full draft

## Philosophy
- **Read first, in full**:
  - `paper2/plan.md`: the paper, its sections, its decisions (INFORMS Journal
    on Computing first; the paper's own repository is the last step);
  - `paper2/revised_algorithm.md`: section 4;
  - `paper2/prior_art_counterexample.md`: what has been checked about the
    novelty of the Chu & Stuckey counterexample;
  - the `CLAUDE.md` blocks on Chu & Stuckey's Theorem 1 and on certified
    optima.
- **The goal is the paper, not more results.** Every item ends in text, a
  table, a figure or a theorem that the paper can use, written where the paper's
  sources live (`paper2/`), with the command that regenerates it.
- **Claims are only as strong as their checks.** Say "we found no prior
  report", never "first", unless a source settles it. Every number carries the
  size range it covers and its regenerate command. A citation gives what the
  source says, with page or section, from a copy held in `literature/` or one
  fetched and read in this session. Never cite from memory.
- **Lean**: new theorems go in new files under `lean/MOSPFormalization/`,
  imported by `lean/MOSPFormalization.lean`. Never add `sorry` or `axiom`.
  Never edit an existing proof. Adding a theorem to an existing file is
  allowed only where the item says so.

## A long computation shares the machine
- `paper2.solver_fix_split` is running in the background, started by the owner
  (2026-10-03, five-day budget, `--until 2026-10-08`). It refutes the four open
  125 × 125 re-certifications and writes `paper2/data/solver_fix_split_*.csv`
  and `.log`.
  - **Do not stop it, restart it, or edit `paper2/solver_fix_split.py` or those
    files.** Read them freely.
  - Find it by the PID recorded in `paper2/data/solver_fix_split.pid`, never by
    command-line text.
  - If its log shows a line beginning `!!!` (a SAT task, meaning a certified
    value is wrong), stop your item, record it at the top of PROGRESS.md and of
    `paper2/solver_fix.md`, and end the session. That is the most important
    possible finding.
- **Use at most 4 cores.** The split run has 20 of the 24 this machine gives
  this work. Check `uptime` before anything parallel. Another project's process
  may be running too; leave it alone.

## Current Focus
Items 01-02 secure the novelty claim. Items 03-06 are section content and data
(section 4's layout form and dataset, the certificate, section 2). Item 07
audits every number. Item 08 assembles the LaTeX draft. Item 09 is the reserve.

## Target Problems (in order)
See `iterations.md`. Work on exactly ONE unchecked item per iteration.

## Acceptance Criteria (per item)
- [ ] The item's output exists where the item says. It is self-contained,
      states its size range, and gives its regenerate command.
- [ ] `python3 Ralph_Loops/loop0008/gate.py` passes (lake build, imports, sorry
      and axiom count, MOSP pytest about 3 min, pathwidth_solver pytest about
      6 min).
- [ ] The item is marked `- [x]`, or `- [!]` with the reason in PROGRESS.md.

## Completion Conditions
An item is DONE when solved, or blocked with the obstacle documented. If an
item finds that a published claim of ours is wrong (a number, a theorem, a
citation), fix the source document and record the correction at the top of
PROGRESS.md.

## Context
- **The paper**: `paper2/plan.md`, `popularity.md` (section 2),
  `problem_transformations.md` and `equivalences.md` (section 3),
  `revised_algorithm.md`, `search_soundness.md` and `solver_fix.md`
  (section 4), `proof_reductions.md`, `prior_art_counterexample.md`,
  `table1.bib`, `figures/`, `benchmarks/README.md` (the benchmark hunt).
- **Lean**: `lean/MOSPFormalization/` (`Complex/`, `Search/`, `MOSPGraph.lean`),
  `paper2/axiom_check.lean`.
- **Solvers**: `satisfiability/customer_search.py` / `.c`, `native.py`;
  `pathwidth_solver/` (`TRANSFER.md`, `bench/`); certificates in
  `learning/search_certificate.py`; isomorphism classes in
  `learning/canonical.py`.
- **Literature**: `literature/` and `literature/MISSING.md`. Chu's 2011 thesis
  is `literature/chu_2011_phd_thesis_improving_combinatorial_optimization.pdf`.
- **Testing**: `python3 Ralph_Loops/loop0008/gate.py`.

## Important Notes
- Do NOT edit `CLAUDE.md`. Do NOT push. Commit nothing yourself; the driver
  commits.
- Do NOT write to `solutions/`. Do NOT run `benchmarks.csearch`,
  `benchmarks.recertify` or `benchmarks.overnight` in modes that write to it.
- Print mode: **ending your turn ends the session.** Never end on a background
  wait. Run long jobs in the foreground with bounded polls. Match processes by
  PID, never a bare `pkill -f <word>`.
- Network: web access is for fetching sources (OpenAlex, Crossref, publisher
  and author pages, arXiv). Send no personal data. Record every source fetched
  with its URL and date.
