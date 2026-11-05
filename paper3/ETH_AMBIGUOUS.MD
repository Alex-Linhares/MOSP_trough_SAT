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

### 02a — three figures of one function (item 02, 2026-11-05)
- **Ambiguous**: the owner's commit of 2026-11-05 (`4ceb1699a`) gave the
  paper a central figure in two panels (`rho_over_n.pdf`, the whole
  range with the manuscript's two unverified exponents beneath;
  `rho_over_n_practical.pdf`, `n = 10…10⁶`) and told item 02 to use both
  as Figure 1; item 02's brief asks for its own `runtime_scale.pdf`
  (log-`n` axis to `10^2500`, the line, the level 1, the practical range
  shaded). Section 2 would then carry three drawings of `ρ(n)/n`.
- **Chosen**: both. Figure 2.1 (`fig:central`) is the owner's two panels
  in one float; Figure 2.2 (`fig:runtime-scale`) is the brief's figure,
  the verified curve alone with the three landmarks and the shaded range.
  The section text points at both. Section 1 (item 09) may re-use
  Figure 2.1 as its Figure 1 or refer to it.
- **Owner may change**: drop Figure 2.2 (the table carries its numbers),
  or move Figure 2.1 to the introduction.

### 02b — the central figure's peak label and formula (item 02, 2026-11-05)
- **Ambiguous**: `rho_over_n.py` found the peak on its grid of 4,000
  points over 3,000 decades (step 0.75 in `log₁₀ n`) and labelled it
  `n ≈ 10^23.5`; the maximum of `(ln y)²/√y` is at `ln y = 4`, i.e.
  `n ≈ 10^23.71`, which `check_encoding.py`, `TASK.md` and the plan all
  give as `10^23.7`. Its legend also wrote `ρ(n) = n(ln ln n)²/√ln n`,
  without the comparator's `+16`.
- **Chosen**: item 02 made the peak analytic in the script (`e⁴/ln 10`,
  value `16/e²`) and wrote the `+16` into the legend; the figure now
  reads `10^23.7` and the same formula as the comparator. Nothing else
  of the owner's figure was touched.
- **Owner may change**: the legend back to the shorter formula with the
  caption carrying the `+16`.

### 02c — a proof-side fact quoted in the statement section (item 02, 2026-11-05)
- **Ambiguous**: the brief says Section 2 makes "no statement about the
  proof", but the sentence "with the true `A` nothing is known" invites
  the question what the proof's own `A` is. The solution sets
  `A = 256 + A_t` with `1 ≤ A_t` (`SqrtLogSpace/NativeLargeEntry.lean`
  line 51; `NativeLeafContract.lean` lines 792–793), so the proof as
  written has `A ≥ 257`.
- **Chosen**: Section 2 quotes that one line for the value it assigns,
  says so explicitly in "what this does not claim" (a value the proof
  writes down, not a value the machine needs), and leaves the argument
  to Section 4. Item 04 should confirm the reading of lines 39–59 of
  `NativeLargeEntry.lean` (the `cutoff`, the leaf contract) in its own
  terms.
- **Owner may change**: remove the `A ≥ 257` sentence from Section 2 and
  keep it in Section 4 only.

### 02d — the Lean statement transcribed, not quoted verbatim (item 02, 2026-11-05)
- **Ambiguous**: the brief says "the statement in words and in Lean".
  The comparator's text uses `∃ ∧ → ℕ ℝ ≤`, which pdflatex with
  `inputenc` cannot typeset in a `verbatim` block, and the house build is
  pdflatex.
- **Chosen**: lines 194–217 are rendered as an aligned display in LaTeX
  math with each conjunct's line numbers beside it, and `runtimeScale`
  and `runtimeBound` as ASCII transcriptions with the casts omitted,
  each marked "transcribed"; the verbatim text is in the clone at the
  cited lines and in our `Frame.lean` (`SubexpCount`, Appendix A).
- **Owner may change**: a `listings` block with a Unicode-capable engine
  (`lualatex`/`xelatex`) if the verbatim Lean is wanted on the page.

### 03a — a third status, "supported", between verified and paper-only (item 03, 2026-11-05)
- **Ambiguous**: the brief tags every claim "verified (a consequence of
  the comparator statement)" or "paper-only (not in the Lean library)".
  Corollary 1.3 (a counting-preserving encoding into the verified
  counter, on paper) and Corollary 1.4 (a bound whose proof names the
  fixed-density exponent) are both "not in the library", and calling
  Corollary 1.3 "verified" would overstate what the kernel checked.
- **Chosen**: three statuses, defined in §3.1 — *verified* (the comparator
  statement, a conjunct, or a replayed theorem of `Final.lean`),
  *supported* (follows from the verified statement by an argument on paper
  only, inheriting `ρ(n)`), *paper-only* (rests on a bound the library
  lacks) — with the sentence that "supported" is a sub-case of the brief's
  "paper-only". Tagged supported: the self-reduction, Corollaries 1.2,
  1.3, C.1, C.2, the §1.1.1/§1.1.2 refutations, Set Splitting. Tagged
  paper-only: the two sharper exponents, "both bounds by tensor
  contraction", Corollary 1.4, Appendix D, the §1.1.3 remarks.
- **Owner may change**: collapse to the brief's two tags (then the
  "supported" rows read "paper-only, follows from the verified statement
  on paper"); or rename "supported".

### 03b — the manuscript has 67 pages, not 64 (item 03, 2026-11-05)
- **Ambiguous**: `TASK.md` (line 217) and `reports/paper3_plan.md` (line
  106) say "64 pages"; the table of contents puts References on p. 64 and
  the references run to p. 67. `pdfinfo` says 67 pages; the extract has 67
  form feeds, one per page, and the page convention (form feeds before the
  line + 1) matches the printed page headers everywhere it was checked
  (pp. 2–5, 43–45, 51–57, 64).
- **Chosen**: Section 3 says "67 pages"; `TASK.md` and the plan are left
  as they are (item 11 updates the plan).
- **Owner may change**: nothing, unless a different count is meant (64
  pages before the references).

### 03c — what the verified exponent would give through Corollary 1.4's argument (item 03, 2026-11-05)
- **Ambiguous**: Corollary 1.4's proof (p. 52, lines 2949–2967) chooses its
  threshold against the fixed-density rate `a(t) = √(log₂ t)`. Re-running
  the same argument with the verified rate would give some weaker
  quantitative bound. Stating what it gives is a judgement about a
  paper-only proof, which the brief excludes; leaving it out leaves a
  natural question unanswered.
- **Chosen**: not worked out; §3.7 says so in one bullet ("a reader can
  rerun Appendix C.1 with `a(t)` replaced by the verified rate; we did
  not").
- **Owner may change**: ask for the one-paragraph derivation (with the
  caveat that the argument is the manuscript's and unchecked here), or
  leave it out.

### 03d — Corollary 1.2 is stated with the verified exponent but tagged "supported" (item 03, 2026-11-05)
- **Ambiguous**: Corollary 1.2 (p. 2, lines 77–81) carries `2^{O_{k,ε}(ρ(n))}`,
  the verified exponent, so "verified exponent" would also be a fair tag;
  its proof is a randomised reduction (clause sampling, a threshold
  circuit to 3-CNF) on paper, not in the library.
- **Chosen**: "supported", with the text saying that the exponent matches
  the verified one and that the randomness is in the reduction, not the
  counter. Corollary C.2 (also stated with `ρ(n)`) is tagged the same way.
- **Owner may change**: a fourth tag ("verified exponent, paper
  reduction") for these two rows.


### 04a — the audit's "33 identical definitions" are 35 compared, 33 identical, 2 up to `noncomputable` (item 04, 2026-11-05)
- **Ambiguous**: `proof_audit.md` §4, `TASK.md` and item 01's §5.4 say
  "the 33 definitions". The fresh `defdiff.py` run reports 32 `SAME` and
  4 it cannot match by itself (`countWord`, whose library file it does
  not read; `runtimeScale` and `runtimeBound`, which differ only by
  `noncomputable def` against `noncomputable section`; and the theorem,
  whose block includes the proof). Checked by hand: `countWord` is
  identical (challenge 147 = `EncodingBounds.lean` 17), the two scale
  definitions are identical up to the keyword, the statement is
  identical. So 35 declarations are compared, 33 are identical character
  for character, 2 up to a keyword the kernel does not see.
- **Chosen**: Section 4 says "35 / 33 / 2" and Table 4.1 carries the
  three numbers; §5.4's "33 definitions" is changed to "35 … two of them
  up to the `noncomputable` keyword". `proof_audit.md` is left as it is
  (a dated scratch record).
- **Owner may change**: keep "33" everywhere with the two scale
  definitions counted separately in a footnote.

### 04b — `enable_nanoda: false` on 413 of 418 challenge JSONs, not 416 (item 04, 2026-11-05)
- **Ambiguous**: the item text says "as on 416 of 418 challenge JSONs".
  The fresh count (`proof_inspection.py`): 418 JSONs; 413 carry
  `"enable_nanoda": false`, 2 carry `true`
  (`ArtinParabolicIntersections`, `TraceIdealTransportSupport`), 3 have
  no `enable_nanoda` key at all (`KadisonRingrose`, `LocalSmoothing`,
  `UniversalTensorSquares`). The three without the key may use the
  newer `external_kernels` form or the comparator's default; not
  examined.
- **Chosen**: Section 4 states 413 / 2 / 3; the three keyless files are
  reported as "omit the key", with no claim about the comparator's
  default.
- **Owner may change**: nothing; or ask item 08 to say what the
  comparator does when the key is absent.

### 04c — the exponent constant the proof exhibits is `A + 1 = 257 + At ≥ 258`, sharpening 02c (item 04, 2026-11-05)
- **Ambiguous**: 02c recorded `A = 256 + At`, `1 ≤ At`, "so the proof as
  written has `A ≥ 257`". That is the constant of `NativeLargeEntry.run`
  (line 51); the comparator theorem's witness is `A + 1` after the
  fallback fold (`Final.lean` line 41: `C + 28700, A + 1, S + 5022741,
  d + 2, e + 2`), so the exhibited exponent constant is at least 258,
  the leading constant at least 28,701, and the polynomial degree is
  `db + (4 · (k − 2) + 2) + df + 2` with `db`, `df` uncomputed.
- **Chosen**: Section 4 states `A ≥ 258` and `C ≥ 28,701` as lower
  bounds on what this proof exhibits, with the line citations, and says
  in "what this does not claim" that they are not running-time
  statements. Section 2's 02c sentence (which quotes `256 + At` for the
  value only) is left as it is; the refuter (item 10) may align the two.
- **Owner may change**: drop the constants from the paper altogether
  (they are proof-side facts in a paper about the statement), or state
  only "at least 257" for `run`'s constant as 02c did.

### 04d — `#print axioms`: 8 closure files / 19 commands, not "seventeen files of the closure" (item 04, 2026-11-05)
- **Ambiguous**: §5.2 (item 01) said "Seventeen source files of the
  closure themselves carry `#print axioms` commands, so the build log
  records nineteen axiom lines". Seventeen is the count over the
  family's whole directory (35 commands); within the 3,091-module
  closure it is 8 files and 19 commands, which is why the build log has
  19 in-build axiom lines. The nine other files are among the 886 never
  built.
- **Chosen**: §5.2 corrected to "Eight source files of the closure …
  nineteen commands (seventeen files of the family's directory do, but
  nine of those are never built)"; Section 4 and Table 4.1 carry both
  counts.
- **Owner may change**: nothing.

### 04e — manifest package count 42, not 41; lakefile line numbers (item 04, 2026-11-05)
- **Ambiguous**: `proof_audit.md` §6 says "41 manifest packages" and
  cites `lakefile.lean:7-8` for `fixedToolchain` / `autoImplicit` and
  `:9` for the global option. `lake-manifest.json` has 42 entries in
  `packages` (Mathlib included); the lakefile lines are 8 and 9, and the
  default target is at 89 (as the audit says), the `run_cmd` hook at
  290 and `post_update` at 306 (as the audit says).
- **Chosen**: Section 4 states 42 and lines 8–9; the audit is left as a
  dated scratch record.
- **Owner may change**: nothing.

### 05a — the problem list elided from the quotation of §1.1.3 lines 233–235 (item 05, 2026-11-05)
- **Ambiguous**: the brief asks item 05 to quote, with page and line, the
  manuscript's sentence that some lower bounds also follow from the
  unrestricted-CNF-SAT hypothesis. That sentence (p. 5, lines 233–235)
  opens with a list of the problems it covers, one of which is a width
  parameter the owner's scope rule keeps out of the paper; the brief
  also says "no example from any width parameter".
- **Chosen**: Section 6 quotes lines 233–236 with the problem list
  replaced by "[…]" ("The lower bounds for […] also follow from the
  hypothesis that unrestricted CNF-SAT admits no …"), says so in the
  sentence that introduces the quote, and keeps the manuscript's bracket
  citations. The §1.1.3 opening list (lines 213–225) is referred to by
  its lines and not quoted, as Section 3 did. The script checks the full
  lines, elision or not.
- **Owner may change**: restore the full quotation (three problem names,
  one of them "the treewidth dependence of Independent Set and Dominating
  Set"), since it is the manuscript's sentence and not ours.

### 05b — SETH is refuted by reading the statement at each k; "SETH ⇒ ETH" is cited to Impagliazzo–Paturi–Zane (item 05, 2026-11-05)
- **Ambiguous**: the brief says "SETH (SETH ⇒ ETH; cite the standard
  implication with its source)". The verified statement holds for every
  fixed `k ≥ 2`, so it negates SETH's "for every ε there is a k" directly,
  without the implication; and the paper that states "SETH implies ETH"
  in those words (Calabro, Impagliazzo & Paturi 2009, where the name
  SETH is introduced) is not in the manuscript's bibliography and item 05
  fetched nothing (TASK.md's download list).
- **Chosen**: Section 6 refutes SETH directly (each `k` has a
  `2^{(1−ε)n}(n+m)^{O_k(1)}` algorithm for every `ε`) and then records the
  implication "for the record", with the two-line argument through the
  Sparsification Lemma and `\citet{ImpagliazzoPaturiZane2001}` as its
  source (that paper's SERF-completeness of `k`-SAT is the lemma the
  implication rests on).
- **Owner may change**: add Calabro–Impagliazzo–Paturi 2009 (IWPEC, LNCS
  5917) to `refs.bib` as the source that states the implication in words,
  or drop the implication sentence altogether since the refutation does
  not use it.

### 05c — the hypotheses' sources are copied from the manuscript's reference list and not re-read; no DOIs (item 05, 2026-11-05)
- **Ambiguous**: each hypothesis is to be stated "as the manuscript's
  §1.1.1 lists it" with its source. The sources (Dinur 2016, Manurangsi &
  Raghavendra 2017, Chalermsook et al. 2020, Carmosino et al. 2016, Dell
  et al. 2014, Cygan et al. 2016, Williams 2016) are not held under
  `literature/`, and `refs.bib`'s header says DOIs are Crossref-checked
  where given; item 05 may not download anything.
- **Chosen**: seven `refs.bib` entries copied from the manuscript's own
  reference list (extract lines 3686–3811, each entry's lines named in
  its `note` and checked by `consequences.py`), with no DOI and a note
  saying none was checked. Section 6 states every hypothesis in the
  manuscript's wording with the manuscript's bracket citation, and says
  in "what this does not claim" that the sources were not re-read.
- **Owner may change**: have item 08 (which may fetch) add the DOIs and
  check the entries against Crossref; or ask for the sources to be
  obtained and the definitions compared word for word (an afternoon).

### 05d — the "hardness as a classification" paragraph is ours (item 05, 2026-11-05)
- **Ambiguous**: the brief asks for the premise/conclusion distinction
  "in general terms" with the manuscript's §1.1.3 as the source. Section
  6.3 adds one paragraph the manuscript does not have: that "Y is
  SETH-hard" remains true as a statement about reductions and no longer
  conveys anything about Y's running time. It also adds the paragraph
  "What a transferred algorithm inherits" (the title's limitation read
  through a reduction), which is a consequence of Section 2 and not a
  manuscript sentence.
- **Chosen**: both paragraphs kept, in general terms, with no problem
  named; the first is marked as ours by its wording, the second cites
  Table 2.1 and Section 3's "supported" tag for the Set Splitting
  transfer. Section 6 also says `A ≥ 257` where it needs a constant,
  following Section 2 (02c), not Section 4's `A ≥ 258` (04c), which the
  refuter may align.
- **Owner may change**: cut either paragraph, or move the second to
  Section 7 (the practitioner).

### 06a — how the two guarantee curves are scaled beside the measurements (item 06, 2026-11-05)
- **Ambiguous**: the brief says to tabulate `2^ρ(n)` and `2^n` "both at
  constant 1, both as guarantees, scaled to the `n = 20` measurement so
  the shapes compare". Scaling *each* curve to the `n = 20` point makes
  them touch there and puts `2^ρ(n)` above `2^n` for every `n > 20`
  (because `ρ(20) − 20 = −2.79` is the minimum of `ρ(n) − n`), which
  hides the crossing at `n = 50` the statement actually has.
- **Chosen**: one common factor `t20 / 2^20` for both curves, where `t20`
  is CaDiCaL's median at `n = 20`: `2^n` passes through the `n = 20`
  measurement and `2^ρ(n)` crosses it at `n = 50`, so the ratio of the
  two drawn curves is the ratio of the guarantees themselves,
  `2^(ρ(n) − n)`. Section 7.4 says so and gives the per-curve alternative
  in one sentence.
- **Owner may change**: scale each curve to its own `n = 20` point as the
  brief literally says (one line in `practitioner.py`'s `write_table`
  and `write_figure`).

### 06b — pyapproxmc was already installed; pyganak installed from PyPI (item 06, 2026-11-05)
- **Ambiguous**: the brief says `pyapproxmc` "is not installed" and to try
  `pip install pyapproxmc`; on 2026-11-05 04:40 `pyapproxmc 4.4.0` was
  already importable (installed by someone or something between the
  brief's check and this session). The brief allows "a pip-installable
  exact counter … if one exists": `pyganak 2.8.0` (Ganak with Arjun
  preprocessing, Mate Soos) is on PyPI and was installed into the host's
  Anaconda Python for this item. `d4 0.1.10` on PyPI was not examined
  (its name may not be the d4 counter).
- **Chosen**: Ganak as the exact counter, ApproxMC as the approximate one,
  blocking-clause enumeration at `n ≤ 30` as the independent check of
  both (not as the counter). Versions recorded in
  `paper3/latex/tables/practitioner_meta.json` and in Section 7.2.
- **Owner may change**: uninstall `pyganak` after the paper (`pip
  uninstall pyganak`); or add a compiled `sharpSAT`/`d4` for a second
  exact counter (none is on the host).

### 06c — seven `refs.bib` entries for the tools and the threshold are from memory, no DOI (item 06, 2026-11-05)
- **Ambiguous**: Section 7 cites CaDiCaL (Biere et al., CAV 2024),
  PySAT (Ignatiev, Morgado & Marques-Silva, SAT 2018), Ganak (Sharma,
  Roy, Soos & Meel, IJCAI 2019), ApproxMC (Chakraborty, Meel & Vardi, CP
  2013; Soos & Meel, AAAI 2019), the 4.26 threshold (Selman, Mitchell &
  Levesque, AIJ 1996) and the cavity-method value 4.2667 (Mertens, Mézard
  & Zecchina, RSA 2006). Item 06 may download nothing but pip packages,
  so none of these was fetched or checked against Crossref; the package
  metadata (`pip show`) gives only the maintainers and the repository
  URLs.
- **Chosen**: the seven entries written with venue, volume and pages from
  memory, each with `note = {Venue from memory; no DOI checked}` and the
  package name and URL where there is one, under a header saying so.
- **Owner may change**: have item 08 check them against Crossref and add
  DOIs, or cut the venue details to the package URLs.

### 06d — the counters are reported at defaults, including a plateau that looks like a preprocessing budget (item 06, 2026-11-05)
- **Ambiguous**: Ganak's median through the pyganak binding is flat at
  about 6–8 s at `n = 100` and `n = 150` and lower at `n = 200` (2.4 s),
  while its maximum keeps rising; the shape is consistent with a fixed
  time budget inside Arjun's preprocessing rather than with counting
  difficulty, and the binding exposes no option to tune it. Tuning it,
  or calling the `ganak` binary directly, would be a different
  measurement.
- **Chosen**: reported as measured, at defaults, with the plateau named
  in Section 7.3 and the possible cause stated as a conjecture about the
  binding, not a finding; the point of the section (the measurement is
  orders below `2^n`) does not depend on it.
- **Owner may change**: rerun with the `ganak` binary and its options, or
  drop the exact counter's seconds above `n = 80` from the table.

### 07a — the brief says `git mv` to `ETH/`; the owner's resolution of S3 says leave the Lean in place (item 07, 2026-11-05)
- **Ambiguous**: `iterations.md` item 07, `TASK.md` (Context and
  Acceptance), `reports/paper3_plan.md` §0.4.7 and its item table, and
  the stubs of `sec8_lean.tex`, `secA_appendix_lean.tex` and `README.md`
  all say the companion Lean is moved to
  `lean/MOSPFormalization/ETH/{PrimitiveMachine,Statement}.lean`; the
  owner's resolution of S3 (relayed by the coordinator, above) says
  "leave the Lean where it is and cite the existing path … item 07 does
  not move anything (item 07's brief amended)", and the brief was not in
  fact amended.
- **Chosen**: the owner's word. Nothing is moved; the two files stay at
  `lean/MOSPFormalization/SubexpPathwidth/{PrimitiveMachine,Frame.lean}`
  with their namespace `MOSPFormalization.SubexpPathwidth`; the audit,
  the re-diff, Section 8, Appendix A and both READMEs cite that path.
  The paper says the directory is named for an earlier study of ours on
  a different question and that nothing from it is cited; the directory
  name is the one place the word in it appears in the paper (Section 8
  and Appendix A name the path, as they must). The one-line note S3
  planned for `reports/subexp_pathwidth.md` §2.1 is not needed and not
  added. `reports/paper3_plan.md` §0.4.7 and the item table still say
  `ETH/`; left for item 11, which updates the plan's §0.
- **Owner may change**: move the files after all (then the namespace in
  Appendix A's rows, `axiom_check.lean`'s `open`, `lean_rediff.py`'s
  paths and `paper3/lean/README.md` change with them; the loop0014
  crossover file, which uses these names, would need an `open` of the
  new namespace); or rename the directory.

### 07b — what the axiom audit prints, and "every line on the three axioms" (item 07, 2026-11-05)
- **Ambiguous**: the acceptance rule says the audit has "every line on
  `propext`, `Classical.choice`, `Quot.sound`". Two of the 21 lines print
  fewer: `Computation.Trace` (an inductive definition) depends on no
  axiom, and `SqrtLogSpace.countWord` on `[propext, Quot.sound]`. And
  `paper1/axiom_check.lean` ends with a control line that must show
  `sorryAx`, which this rule would forbid.
- **Chosen**: the rule is read as "nothing beyond the three on any line,
  `sorryAx` on none", which holds; the two lines are reported as printed,
  in Section 8, Appendix A ("or fewer") and `paper3/lean/README.md`. No
  `sorryAx` control line, so that the committed log has nothing a reader
  must explain away; the gate's library-wide `sorry`/`axiom` scan is the
  control instead. The ten copied definitions and the three `def`s are
  printed beside the lemmas to show that they elaborate; a `def` printed
  with axioms is not a claim.
- **Owner may change**: add paper 1's control line; print the lemmas
  only.

### 07c — the statement match in the re-diff goes beyond the brief (item 07, 2026-11-05)
- **Ambiguous**: the brief asks for a byte-level re-diff of
  `PrimitiveMachine.lean` against the comparator's lines 1–190 and 220
  only. Whether `SubexpCount`'s body is the theorem's "character for
  character" (Frame.lean's own claim, repeated in Section 2) had been
  checked only by reading.
- **Chosen**: `lean_rediff.py` also compares the body of `SubexpCount`
  (Frame.lean 85–107) with the body of `exact_count_and_sat` (clone
  195–217, the trailing `:= by` removed) after whitespace normalisation
  (identical, 1,073 characters) and line by line after stripping
  indentation (identical, 23 lines; every line of ours is two columns
  further left). "Character for character" in the paper is defined as
  exactly this normalised equality, and Section 8 says it is textual.
  The binders `(k : ℕ) (hk : 2 ≤ k)` are outside the body by
  construction (`k` is the def's argument, `2 ≤ k` is
  `ExactCountAndSat`'s hypothesis).
- **Owner may change**: drop the extra check; or require an
  indentation-exact match (which would mean restating the `def` with
  the theorem's indentation).
