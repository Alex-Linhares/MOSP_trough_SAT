# ETH_AMBIGUOUS — questions the loop decided for itself, for the owner

**Protocol** (owner, 2026-11-05). Paper 3 is written by Ralph loop0015
with no stopping midway. Whenever an item finds something ambiguous — a
wording, a claim, a citation form, a choice between two sound ways of
doing a thing — it **decides**, writes **one entry here per question**,
and continues. Each entry has three parts: *what was ambiguous*, *what
the item chose*, *what the owner may want to change*. Entries are dated
and numbered (`S` for setup, then the item number and a letter: `01a`,
`01b`, …). Nothing here changes the title, which is fixed:

> Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.

Item 09 lists in the paper's conclusion the entries that affect the text;
item 11 lists all of them in `README.md`. The owner resolves an entry by
editing the paper and striking the entry (or by leaving it, which is also
an answer).

## Entries

### S1 — the author line (setup, 2026-11-05)
- **Ambiguous**: who the authors are. Paper 1 is Linhares and Yanasse;
  the brief for this paper names "Alexandre Linhares" and "the MOSP
  project" as a placeholder.
- **Chosen**: `\author{Alexandre Linhares \and the MOSP project}` in
  `latex/main.tex`, with a comment marking the second author as a
  placeholder; the acknowledgements will carry the AI-use disclosure in
  paper 1's form.
- **Owner may change**: the second author (Yanasse? none? a project
  name?), affiliations, ORCID.

### S2 — `2^n` in the typeset title (setup, 2026-11-05)
- **Ambiguous**: the title string carries the plain-text `2^n`; LaTeX
  cannot typeset `^` in text mode, and a typeset title would ordinarily
  show a superscript.
- **Chosen**: `\title{... all $2^n$ assignments ...}` (a superscript `n`
  in the PDF) with `\ldots` for the ellipsis; the PDF metadata
  (`pdftitle`) carries the plain string with the caret literal (`2\string^n`, since hyperref drops a bare `^` from PDF strings); the plain
  string also sits in a comment directly above `\title`. The gate strips
  `$` and `\ldots` before comparing. Nothing else in the title is
  touched.
- **Owner may change**: typeset the caret literally (`2\textasciicircum
  n`) if the plain form is wanted on the page.

### S3 — where the companion Lean lives (setup, 2026-11-05)
- **Ambiguous**: the restatement `SubexpCount` and the verbatim machine
  model are under `lean/MOSPFormalization/SubexpPathwidth/`, a path
  named for loop0014's pathwidth question, which this paper does not
  touch. Cite them there, or move them to a neutral path?
- **Chosen**: item 07 moves them — `PrimitiveMachine.lean` and the
  ETH-only declarations of `Frame.lean` (`SubexpCount`,
  `ExactCountAndSat`, `SubexpCount.anti`, `ExactCountAndSat.subexpCount`,
  `runtimeBound_eq`, `tendsto_log_sq_div_sqrt`, `runtimeScale_isLittleO`)
  — to `lean/MOSPFormalization/ETH/{PrimitiveMachine,Statement}.lean`;
  `SubexpPathwidth/Frame.lean` imports `ETH.Statement` and keeps its
  pathwidth side. loop0014's report will then name the old path for
  those declarations; a one-line note in `reports/subexp_pathwidth.md`
  §2.1 is the smallest fix and item 07 adds it.
- **Owner may change**: keep them in place and cite the old path; or a
  different directory name.

### S4 — Bonnet's venue year, and the width references dropped (setup, 2026-11-05)
- **Ambiguous**: the original brief listed Lokshtanov–Marx–Saurabh,
  Cygan et al. (Cut & Count), Lampis 2025 and Bonnet 2025 for `refs.bib`;
  the owner's scope change the same day removed every width-parameter
  consequence from the paper, so none of the four is cited. (For the
  record, Crossref on 2026-11-05 gives Bonnet as STOC 2025,
  `10.1145/3717823.3718117`, and *J. ACM* issued 2026-10-10,
  `10.1145/3833387`; loop0014's report says "*J. ACM* 2025".)
- **Chosen**: the four entries are not in `refs.bib`; `refs.bib` carries
  the OpenAI manuscript, Impagliazzo–Paturi 2001, Impagliazzo–Paturi–Zane
  2001, the human-audit paper arXiv 2608.14673, and `@misc` entries for
  the comparator and nanoda repositories (URLs; item 08 fills what it
  fetches).
- **Owner may change**: nothing unless a width reference is wanted back.

### S5 — per-item cap in the driver (setup, 2026-11-05)
- **Ambiguous**: the loop0014 driver has one global cap; the replay
  needs 8 h and every other item 4 h.
- **Chosen**: `loop.py` reads `[cap N h]` from an item's first line
  (`item_cap`); item 01 carries `[cap 8 h]`; the global knob stays 4.0.
- **Owner may change**: the global cap to 8.0 and the marker removed, if
  a modified driver is not wanted.

### S6 — no model counter on the host (setup, 2026-11-05)
- **Ambiguous**: item 06 asks for a public #SAT counter; none of
  `sharpSAT`, `ganak`, `d4`, `approxmc` is installed, `pyapproxmc` is not
  installed, `python-sat 1.9.dev15` is.
- **Chosen**: item 06 tries `pip install pyapproxmc` (and any
  pip-installable exact counter it finds), falls back to CaDiCaL decision
  times plus blocking-clause enumeration at `n ≤ 30`, and says in the
  text which it used.
- **Owner may change**: install a counter (`ganak`, `d4`, `sharpSAT-td`)
  on the host before item 06 runs, in which case item 06 uses it.

### S7 — the `50 ≤ n` boundary (setup, 2026-11-05)
- **Ambiguous**: `CLAUDE.md`'s Paper 3 paragraph says the factor exceeds
  1 "for every `n < e^{5504}`"; `check_encoding.py` says it crosses 1 at
  `n ≈ 49`; the brief says "for all `50 < n < e^{5504}`".
- **Chosen**: `ρ(49)/49 = 0.9994`, `ρ(50)/50 = 1.0027`
  (`python3 -I -c` from `check_encoding.py`'s `scale`), so the paper
  says **for every `50 ≤ n < e^{5504}`** and item 02's script prints both
  neighbours.
- **Owner may change**: the phrasing ("above 50", "from 50 on").

### S8 — the Lean toolchain for the replay (setup, 2026-11-05)
- **Ambiguous**: the clone pins `leanprover/lean4:v4.34.1`; the host has
  `v4.29.0` and `v4.34.0-rc2`. Build at the pinned version (a download
  inside the sandbox) or at the host's `rc2` (what loop0014 compiled the
  copied definitions with)?
- **Chosen**: the pinned `v4.34.1`, fetched by the sandbox's own `elan`
  into the private home — which is what the coordinator's `replay.sh`
  (started 01:03) does; the paper names the version it ran.
- **Owner may change**: nothing; the download has happened.

### 01a — the coordinator's `lake build … -j 8` was not accepted; the core cap is now `taskset` (item 01, 2026-11-05)
- **Ambiguous**: run 1 of the replay (01:03) failed at once with
  `error: unknown short option '-j'`: Lake `v4.34.1` has no `-j`/`--jobs`
  option (`lake --help`, `lake help build`), and Lake sizes its worker
  pool from the hardware concurrency (32) with no way to lower it. The
  owner's rule is "at most 8 workers (`lake build -j 8`)".
- **Chosen**: the one relaunch item 01 is allowed (run 2, 01:16:17):
  `-j 8` dropped from `replay.sh`, and `taskset -c 0-7` prefixed to the
  `bwrap` line in `run_sandbox.sh`, confining the whole sandbox to eight
  cores; `lake` then runs ~30 `lean` processes on those eight cores, so
  the one-minute load average sits above 24 while the CPU in use is
  eight cores. Not treated as the "load above 24 → 4 workers" case,
  since the load is our own confined processes. Also fixed in the same
  edit: the `mathlib rev` log line (`grep -B3`, since `"rev"` precedes
  `"name"` in the manifest). Both run-1 originals are kept under
  `paper3/replay/logs/run1/`; the README's timeline records the error.
- **Owner may change**: a stricter cap (`taskset -c 0-3`) on any future
  sandbox run; or accept `LEAN_NUM_THREADS`-style control if a later
  Lake offers one.

### 01b — which nanoda, which lean4export (item 01, 2026-11-05)
- **Ambiguous**: the brief says "the independent Rust kernel the
  comparator README names". The README of `github.com/leanprover/comparator`
  (fetched 2026-11-05) does name it ("check with the nanoda kernel in
  addition to the builtin one"; `cargo build --release` places
  `nanoda_bin` in `target/release`; `COMPARATOR_NANODA`,
  `enable_nanoda: true`), but gives no repository URL or commit; the
  clone at `4eaee875` itself mentions `nanoda` only in the JSON field
  `enable_nanoda` (`false` for family 378).
- **Chosen**: the second kernel used is `ammkrn/nanoda_lib` (the
  external Lean 4 checker of the "Type checking in Lean 4" book), at
  `master` commit `8de7e0c4ed3052745a7f8725164efd9e76d84c56`
  (2026-10-29), which consumes `lean4export`'s NDJSON format; the
  exporter is `leanprover/lean4export` at tag `v4.34.0` (commit
  `076e8e57…`), there being no `v4.34.1` tag, with its `lean-toolchain`
  overridden to `v4.34.1` inside the sandbox so that it is built with
  the Lean that produced the oleans. The paper cites the comparator
  README for the mechanism and the clone's JSON for the field's value.
- **Owner may change**: the checker (another external kernel) or the
  exact `lean4export` revision (`bump-to-v4.34.0-rc2` branch exists; no
  `v4.34.1` tag on 2026-11-05).

### 01c — the nanoda check permits the three axioms and ignores unused ones (item 01, 2026-11-05)
- **Ambiguous**: nanoda's config has `unpermitted_axiom_hard_error`;
  with `true` an axiom *declared* in the export but never used aborts
  the run. The export is selective (`-- exact_count_and_sat`), so only
  the theorem's transitive dependencies are exported, but a stray
  declaration would waste the one attempt.
- **Chosen**: `permitted_axioms = [propext, Classical.choice, Quot.sound]`,
  `unpermitted_axiom_hard_error = false` (an unlisted axiom is skipped
  and errors only if used, which is the same soundness guarantee for the
  checked theorem), `nat_extension` and `string_extension` on (the Lean
  kernel's own literal extensions), 8 threads, 1 GB stack per worker.
  The config is committed (`paper3/replay/logs/nanoda/nanoda_config.json`)
  with the output.
- **Owner may change**: rerun with `unpermitted_axiom_hard_error: true`
  if a stricter log is wanted.

### 01d — what "replayed" covers (item 01, 2026-11-05)
- **Ambiguous**: the comparator run itself (OpenAI's statement-level
  check through `lean4export`, `enable_nanoda: false`) is not
  reproduced; what the sandbox replays is the build of the solution's
  closure and `#print axioms` of the named theorem, plus, if it ran, an
  external-kernel check of that theorem's dependencies.
- **Chosen**: the paper's sentence is "replayed: the closure builds at
  the pinned toolchain with upstream Mathlib, the main theorem's axioms
  are the three standard ones, [and nanoda checked its export /
  single-kernel only]"; the textual match of the statement is item 04's,
  from `defdiff.py`, not a `lean4export`-level comparison.
- **Owner may change**: nothing unless the comparator's own tooling
  becomes available.

## Owner resolutions (2026-11-05, relayed by the coordinator)

- **S1 resolved**: author line is *Alex Linhares*, Argo Lab AGI, on leave
  from the Getulio Vargas Foundation, `alex@argolab.org`, ORCID
  0000-0002-4227-6879 (applied in `latex/main.tex`); the owner added
  "keep yours if possible", read as: keep the AI contribution disclosed in
  paper 1's form in the acknowledgements — if a co-author credit for the
  AI was meant instead, the owner says so and item 09 applies it.
- **S2**: no answer; the chosen typesetting stands.
- **S3 resolved**: **leave the Lean where it is** and cite the existing
  path `lean/MOSPFormalization/SubexpPathwidth/{PrimitiveMachine,Frame}.lean`;
  item 07 does not move anything (item 07's brief amended).
- **S4 resolved**: cite the OpenAI manuscript first; for our side nothing,
  unless a width reference is wanted back.
- **S5**: the owner asked for the question in plain words. It was only
  this: the driver originally gave every item the same time limit of
  four hours, and the replay needs eight; the agent changed the driver so
  one item can carry its own limit. Nothing for the owner to decide; the
  change stands.
- **S6 resolved**: `pyapproxmc` 4.4.0 (ApproxMC, an approximate counter
  with (ε, δ) guarantees) is installed on the host by the owner
  (2026-11-05); no exact counter is installed. Item 06 uses ApproxMC for
  counts and CaDiCaL (pysat) for decision times, and says so; an exact
  counter (ganak, sharpSAT-td) would need a source build.
- **S7 resolved**: the text says exactly "for every 50 ≤ n < e^5504".
- **S8 resolved**: ok.
- **Compute**: the owner allows as many `nice -n 19` cores as needed
  (TASK.md amended: no worker cap at nice 19).
