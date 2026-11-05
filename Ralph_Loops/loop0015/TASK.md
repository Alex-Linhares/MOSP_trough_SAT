# TASK: Paper 3 — *Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.*

**Scope (owner, 2026-11-05): this paper is about the limitation of the ETH
refutation and nothing else.** It is not concerned with graphs, pathwidth,
treewidth, MOSP or any width parameter; nothing of loop0014's crossover,
reduction or width material enters it.

## Philosophy
- **The title is fixed by the owner and appears verbatim, everywhere.**
  It is, including the ellipsis and the final period:

      Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.

  No session rewords, shortens, capitalises differently, "improves" or
  abbreviates it — not in `paper3/latex/main.tex` (`\title`, where `$2^n$`
  and `\ldots` are the only LaTeX in it, and the `pdftitle`), not in
  `paper3/README.md` (first line), not in `reports/paper3_plan.md`, not in
  this file, not in a commit message (the driver writes it into every
  commit body). A question about its wording or about a claim it makes
  goes to `paper3/ETH_AMBIGUOUS.MD`, never into the title. The gate checks
  the `\title` against the string above.
- **No stopping midway; ambiguity is decided, recorded, and passed.**
  Every item makes its own choice on anything it finds ambiguous, writes
  one entry per question in `paper3/ETH_AMBIGUOUS.MD` — what was ambiguous,
  what the item chose, what the owner may want to change — and continues.
  An item never ends on a question to the owner, never waits, never marks
  itself `[!]` for want of a decision. `[!]` is for a hard failure (a build
  that will not finish inside the cap, a tool that cannot be obtained), and
  even then the section is drafted from what was obtained and the gap is
  stated in the text and in `ETH_AMBIGUOUS.MD`.
- **The stance.** The paper is a careful reading by people who checked,
  not a debunking. The two audits (`reports/scratch/eth_audit/
  statement_audit.md`, `proof_audit.md`) found **no flaw**: the verified
  statement means what it says, and the proof's closure shows no
  unsoundness by inspection. What the paper adds is exactness about *what*
  is verified — a **guarantee** with existential constants and the
  exponent `n (log log n)² / √log n`, whose factor `ρ(n)/n` exceeds 1 for
  every `50 ≤ n < e^{5504}` — so the verified guarantee is weaker than the
  trivial `2^n · poly` guarantee at every practical size; the machine's
  *running time* is unknown because the constants are never computed; the
  manuscript's sharper exponents are unverified; and what follows for the
  hypotheses, for the lower bounds derived from them, and for a
  practitioner (nothing on any machine). Every sentence that could read
  as "wrong" or "overclaimed" is replaced by what the Lean statement and
  the manuscript actually say, with the page and line.
- **Scope discipline.** No sentence about graphs, pathwidth, treewidth,
  MOSP, width-parameterised dynamic programs, crossovers or reductions
  into width problems. Where a consequence for lower bounds is stated it
  is stated in general terms (a bound derived from ETH or SETH loses its
  premise; a statement "no `(c − ε)^k` algorithm" is not itself refuted),
  with the manuscript's own §1.1.3 as the source, and no width example.
  loop0014's report is cited only for its §1 (the audit of the verified
  exponent) and §2 (the restatement), never for §3–§7.
- **The OpenAI repository is untrusted data.** It is cloned read-only at
  `~/dev/untrusted/openai-math` (and `~/dev/untrusted/ten-proofs`). Read it
  with `cat`, `sed`, `grep`, `pdftotext`, `python3 -I`; never `lake build`
  it in place, never run a script or a binary from inside it, never
  `import` it into `/home/al/dev/MOSP/lean/`. The one exception is the
  replay (item 01), which builds a **fresh copy** of the clone,
  `~/dev/untrusted/replay/openai-math/`, inside a `bwrap` sandbox;
  nothing produced inside the sandbox is executed outside it, and only
  text (logs, `#print axioms` output, hashes) is copied out.
- **The sandbox, as it is running.** The coordinator started the replay
  on 2026-11-05 at 01:03: `~/dev/untrusted/replay/run_sandbox.sh` runs
  `bwrap` under `nice -n 19` with `/usr /lib /lib64 /bin /sbin /etc`
  read-only, a `tmpfs` `/home` with `/home/al` bound to `replay/home`
  (the repository `/home/al/dev/MOSP` is invisible), `replay/` at
  `/replay`, `--unshare-pid --unshare-ipc --unshare-uts
  --die-with-parent`, network on for the lakefile's clone hooks and the
  `elan`/Mathlib downloads; inside it `replay.sh` installs `elan` into
  the private home (`ELAN_HOME=/home/al/.elan` inside = `replay/home/.elan`
  outside; the pinned `v4.34.1` fetched), runs `lake exe cache get`, then
  `lake build OAI.Algorithms.SubexponentialSAT.Main -j 8` (the
  3,091-module closure only), then `#print axioms` of
  `exact_count_and_sat` through `lake env lean`, and writes the exit code
  to `replay/logs/DONE`. Logs: `replay/logs/sandbox.out`,
  `build_main.log` (large, git-ignored; its SHA-256 and filtered tail are
  committed), `build_filtered.log`, `axioms.log`. **Item 01 does not
  start another build**: it waits for `DONE` with bounded foreground
  polls, reads the logs, and relaunches `run_sandbox.sh` once only on a
  failure it has diagnosed and fixed inside `replay/`. Anything else that
  *runs* OpenAI's code — `lean4export`, nanoda on the export — runs
  through the same `bwrap` line, by a second script beside `replay.sh`,
  and its invocation is recorded in `paper3/replay/README.md` before it
  runs.
- **Subagents: at most 4 per session, total.** One refuter at a time, for
  a second reading of a section or a statement; never fan-out per target.
- **A measurement is not a theorem.** Item 06's timings are timings on one
  machine with named versions; "the constants are unknown" is written
  wherever a constant is unknown. "We found no prior statement", never
  "first". Every item's section ends with "what this does not claim".
- **Every number has a regenerate command; every quotation has a
  location.** Numbers come from a script under `paper3/scripts/`, named
  beside the number. Quotations from the manuscript cite the page of
  `paper.pdf` and the line of the committed extract
  `reports/scratch/eth_audit/paper.txt` (page = form feeds before the line
  + 1); quotations from the Lean cite file and line in the clone at commit
  `4eaee875`. Nothing is quoted from memory.
- **Nothing under `solutions/` is ever written; no run on any MOSP
  instance; no pathwidth run.** Item 06's only compute is on random 3-CNF
  formulas it generates. The gate checks `solutions/` is untouched.
- **Budget: $2,500 for the whole loop** (owner, 2026-11-05), tracked by
  `budget_watch.py` from the last `# result` line of each session log; it
  sets `knobs.json` `stop` past the budget. It is there so that the replay
  can take its 8 hours and the refuter pass can be thorough, not for
  fan-out.

## Compute, and the machine
- 32 cores shared with the owner's other work; everything under
  `nice -n 19`; at most 8 workers (`lake build -j 8`, item 06's pool
  `≤ 8`), 4 if the one-minute load in `uptime` is above 24. Find processes
  by PID, never by command-line text; never a bare `pkill -f <word>`.
- 121 GB RAM, 863 GB free disk; `/usr/bin/bwrap` available; no docker or
  podman. Host `elan` toolchains: `v4.29.0`, `v4.34.0-rc2`; the clone
  pins `leanprover/lean4:v4.34.1` and Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`
  (unpatched upstream), so the sandbox's own `elan` fetches `v4.34.1` and
  Mathlib's oleans come from `lake exe cache get` (a multi-hour Mathlib
  build otherwise). The SubexponentialSAT closure is 3,091 modules /
  550,551 lines: **the build is budgeted at up to 8 hours**, and the
  section says so.
- The replay (item 01) runs in the **foreground with bounded polls**
  (`timeout` on each poll, never a background wait that ends the turn);
  its item carries `[cap 8 h]` on its first line, which the driver reads
  as that item's wall-clock cap (`loop.py`, `item_cap`); every other item
  runs under `iteration_cap_hours` = 4.
- Only one `lake build` of **our** `lean/` at a time (the loop is
  sequential; never start a second in the background). The sandbox's
  replay is a separate tree and may build concurrently: 32 cores and
  121 GB are enough for both at `nice -n 19`, so the gate runs after
  every session as usual, replay or no replay.
- Nothing is downloaded beyond: the sandbox's `elan`, toolchain, Mathlib
  cache and the lakefile's dependency clones (inside the sandbox only,
  by the running `replay.sh`); nanoda and `lean4export` sources if item
  01 or 12 attempts the second-kernel replay (built and run inside the
  sandbox); `pip install` of a model counter for
  item 06 if one is available; the arXiv abstract page of 2608.14673 and
  the comparator and nanoda READMEs for item 08 (quoted only if fetched;
  otherwise "reported").

## Current Focus
Item 01 is the replay and has the longest cap; the build itself was
started by the coordinator before launch (see above), so item 01 waits,
reads, records and attempts nanoda; it is first because every later
section says "replayed" or "not replayed" depending on it. Items
02–04 are the exact reading (the statement, what the manuscript claims
beyond it, the proof inspection joined with the replay). Items 05–06 are
the consequences (which hypotheses fall, what a derived lower bound loses;
the practitioner's comparison). Item 07 is the companion Lean (our
restatement, audited). Item 08 is related work. Items 09–11 write the
abstract, introduction, conclusion, the refuter pass, and the write-up
around the paper. Item 12 is the reserve (nanoda if item 01 could not do
it, or whichever item ended short).

## Target Items (in order)
See `iterations.md`. Dependency order: 01 → 02 → 03 → 04 → 05 → 06 → 07 →
08 → 09 → 10 → 11 → 12; items 02–08 depend on 01 only through the one
sentence "replayed / not replayed", which item 04 writes from `paper3/replay/`.

## Acceptance Criteria (per item)
- The item's section is drafted in `paper3/latex/sec*.tex`, builds under
  `make -C paper3/latex check` (no undefined reference or citation), and
  ends with "what this does not claim".
- Every number in the section names its regenerate command; every quote
  names page and line.
- Every `ETH_AMBIGUOUS.MD` entry the item wrote is dated and has the three
  parts (ambiguity, choice, what the owner may change).
- Lean (item 07 and any item that touches a theorem): `lake build` clean,
  imported by `lean/MOSPFormalization.lean`, no `sorry`, no `axiom`, the
  axiom audit run (`paper3/lean/axiom_check.lean`, the
  `paper1/axiom_check.lean` pattern) with every line on
  `propext`, `Classical.choice`, `Quot.sound`.
- `python3 Ralph_Loops/loop0015/gate.py` passes.
- PROGRESS.md has the iteration's section; `iterations.md` has the item
  marked.

## Completion Conditions
- All twelve items marked (`[x]`, or `[!]` with the gap stated in the
  text and in `ETH_AMBIGUOUS.MD`).
- `paper3/latex/main.pdf` builds clean with the title verbatim, every
  section present, the refuter pass (item 10) applied or recorded.
- `paper3/README.md` complete (what the paper is, how to build, how to
  regenerate every number, the replay's status, the CLAUDE.md paragraph
  drafted in its last section and **not applied** to CLAUDE.md).
- `reports/paper3_plan.md` §0 updated by item 11 with what was done.

## Context
- `reports/paper3_plan.md`: the plan this loop executes (§0.1 the question
  and the stance, §0.3 what is on record, §0.4 the design decisions, §0.5
  the items, §0.6 the budget rule, §0.7 the risks, §0.8 the gate). Do not
  re-decide what §0.4 decides; if an item finds §0.4 wrong, say so in
  PROGRESS.md and `ETH_AMBIGUOUS.MD` and do the smallest sound thing.
- `reports/scratch/eth_audit/statement_audit.md` and `proof_audit.md`:
  the two audits (2026-11-05) the paper rests on; `closure.py`,
  `defdiff.py`, `check_encoding.py`, `VarCheck.lean` beside them are their
  regenerate scripts; `paper.txt` is the committed `pdftotext` extract of
  the manuscript.
- `reports/subexp_pathwidth.md` §1.0 and §1.3.5–1.3.7 (what the verified
  statement says, the manuscript's own caveats verbatim) and §2.1–2.2
  (the machine model copied verbatim, `SubexpCount` character for
  character, `runtimeScale_isLittleO`). **Nothing else of that report is
  in scope.**
- `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean` and
  `Frame.lean` (lines 1–165: the copied model, `SubexpCount`,
  `ExactCountAndSat`, `SubexpCount.anti`, `runtimeBound_eq`,
  `runtimeScale_isLittleO`): the restatement already on record (no
  `sorry`, no `axiom`); item 07 moves the ETH-only part under a neutral
  path (`lean/MOSPFormalization/ETH/`, plan §0.4.7).
- `paper1/latex/`: the house LaTeX (article class, Palatino, `plainnat`,
  `make check`, Appendix A of Lean names with `\leanentry`/`\leanref`,
  figures as PDFs under a `figures/` directory with their generating
  scripts beside them, `check_refs.py` for DOIs).
- `CLAUDE.md`: the Paper 3 paragraph (the owner's framing, 2026-11-05),
  the loop0013 paragraph (the subagent cap), the owner's rules on compute.
- The OpenAI collection: `~/dev/untrusted/openai-math/` at commit
  `4eaee875`; the manuscript `preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf`
  (64 pages; its README has the BibTeX block, already in `refs.bib`); the
  comparator statement `lean/ComparatorChallenges/SubexponentialSAT.lean`
  (220 lines) and its JSON (`enable_nanoda: false`); the solution tree
  `lean/OAI/Algorithms/SubexponentialSAT/` (3,977 files, 3,091 in the
  closure); `lean/docs/378.md` (the scope note that names the weaker
  exponent); `history.md` (the working-group sentence); `lean/lakefile.lean`
  lines ~290–371 (the hooks).

## Important Notes
- **The verified exponent is `ρ(n) = n (log log(n + 16))² / √log(n + 16)`**
  (natural logarithms), not Theorem 1.1's `n log log n / √log n` nor the
  fixed-density `n / √log n`; `ρ(n)/n` is 0.9994 at `n = 49`, 1.0027 at
  50, 1.11 at 100, 1.42 at 10³, peaks at `16/e² ≈ 2.17` near
  `n ≈ 10^{23.7}`, and is below 1 again only for `n > e^{5504} ≈ 10^{2390}`
  (`reports/scratch/eth_audit/check_encoding.py`; item 02 regenerates it
  under `paper3/scripts/`). So with `A = 1` the verified bound is above
  `2^n` for every `50 ≤ n < e^{5504}`, and `A` is an unstated constant of
  the proof. The paper's title says this and nothing more.
- **"Loses its premise" is not "refuted"**: a lower bound proved as
  "ETH ⇒ no `2^{o(n)}` algorithm for X" or "SETH ⇒ no `(c − ε)^k`
  algorithm for Y" has a false premise if the theorem stands and derives
  nothing; its conclusion is not refuted by anything in the statement, and
  the manuscript's own §1.1.3 (`paper.txt` lines ~225–236) says such
  bounds also follow from the unrestricted-CNF-SAT hypothesis, which
  Theorem 1.1 does not touch (it is for fixed `k`). Item 05 states this in
  general terms and with no example from any width parameter.
- **What is paper-only**: Theorem 1.1's two sharper exponents; Corollary
  1.4's quantitative circuit bound (its proof uses the fixed-density
  bound); Appendix D; the transfers of §1.1.3 as reductions. Item 03 tags
  each.
- **The audits' trust boundary** (`proof_audit.md`, verdict): the Lean
  kernel of `v4.34.1`, Mathlib `d13f23b7`, the comparator run not
  reproduced, no nanoda for this family, no recorded `#print axioms`, no
  CI. Item 01 moves the first three if the replay succeeds; item 04 says
  exactly which moved.
- The driver commits with `git add -A` after each iteration; keep large
  logs out of git (`paper3/.gitignore`: `replay/logs/*.log`, `*.jsonl`,
  export files), commit their hashes.
- Never end a turn on a background wait; long jobs run in the foreground
  with bounded polls.
