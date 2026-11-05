Exponential time hypothesis is false... but the verified algorithm is slower than trying all 2^n assignments at every practical size.

*(The title above is fixed by the owner and is used verbatim, including
the ellipsis and the final period, everywhere: here, in `latex/main.tex`,
in `reports/paper3_plan.md`, in `Ralph_Loops/loop0015/TASK.md` and in
every commit the loop makes. Questions about its wording go to
`ETH_AMBIGUOUS.MD`, never into the title.)*

**This paper is about the limitation of the ETH refutation and nothing
else.** It is not concerned with graphs, pathwidth, treewidth, MOSP or any
width parameter.

## What the paper is

A reading of OpenAI's family 378, *The Exponential Time Hypothesis is
False* (`github.com/openai/math`, 2026-10-25; cloned read-only under
`~/dev/untrusted/openai-math`, commit `4eaee875`), by people who checked:

- **what the Lean-verified statement says exactly** (`lean/ComparatorChallenges/SubexponentialSAT.lean`
  in the clone): for each `k ≥ 2` there *exist* a finite multitape machine
  and constants `C, A, S, d, e` such that on every width-`≤ k` CNF, in a
  canonical encoding of bit length `L`, the machine halts with the exact
  count within `C (L + 1)^d · 2^{A · ρ(n)}` steps,
  `ρ(n) = n (ln ln(n + 16))² / √ln(n + 16)`. A **guarantee**, not a
  running time; the constants are never computed; the exponent is `ρ(n)`
  only — the manuscript's sharper `n log log n / √log n` and `n / √log n`
  are not in the Lean library. The factor `ρ(n)/n` exceeds 1 for every
  `50 ≤ n < e^{5504}` (peak `16/e² ≈ 2.17` near `n ≈ 10^{23.7}`), so with
  `A = 1` the verified bound is above `2^n` at every practical size: the
  verified guarantee is weaker than the trivial `2^n · poly` guarantee of
  trying all assignments. The statement does refute ETH as stated.
- **an independent inspection and replay of the proof**: the closure of
  3,091 modules with no `axiom`, `sorry`, `native_decide`,
  `implemented_by`, `unsafe` or `partial`, 33 statement definitions
  identical to the comparator's, the compile lemmas concluding in the
  comparator's own `Trace`; and (item 01) a build of that closure in an
  isolated `bwrap` sandbox with `#print axioms` recorded, since the
  repository holds no recorded axiom audit, no CI and no second-kernel
  (nanoda) replay for this family.
- **what follows**: ETH, SETH, Gap-ETH, #ETH and their randomised forms
  refuted as the statement supports; lower bounds derived from them lose
  their premise while the statements they concluded are not themselves
  refuted (the manuscript's own §1.1.3).
- **what it changes for a practitioner**: nothing on any machine — a
  measurement of a SAT solver and a model counter on random 3-CNF against
  `2^{ρ(n)}` and `2^n`.

The two audits the paper rests on are `reports/scratch/eth_audit/
statement_audit.md` and `proof_audit.md` (2026-11-05). The plan is
`reports/paper3_plan.md`; the loop that writes the paper is
`Ralph_Loops/loop0015/`.

## Layout

| path | content |
|---|---|
| `latex/` | the paper: `main.tex` (title verbatim, abstract, section inputs), `sec*.tex`, `refs.bib`, `Makefile` (`make`, `make check`), `figures/`, `tables/` |
| `scripts/` | every number's regenerate script (`runtime_scale.py`, `practitioner.py`, …), written by the items |
| `replay/` | the sandboxed replay: `README.md` with the exact commands, `logs/` (full logs git-ignored, hashes committed) |
| `lean/` | `README.md` pointing at `lean/MOSPFormalization/ETH/` and `axiom_check.lean` with its log |
| `refuter/` | item 10's refuter report |
| `ETH_AMBIGUOUS.MD` | every question the loop could not settle, one entry each, for the owner |

## How to build

```bash
cd paper3/latex
make          # latexmk -pdf -> main.pdf
make check    # fails on any undefined reference or citation; prints the page count
make clean
```

The gate (`python3 Ralph_Loops/loop0015/gate.py`) runs `make check` here,
checks the title in `main.tex` verbatim, and fails if anything under
`solutions/` changed.

## How to regenerate every number

*(Filled in by the items, section by section. Until an item fills its
section: the closure counts come from `python3 -I
reports/scratch/eth_audit/closure.py` and `defdiff.py`, read-only on the
clone.)*

- **Section 2, the statement** (item 02): `python3 -I
  paper3/scripts/runtime_scale.py` prints the `ρ(n)/n` table (Table 2.1),
  the first integer above 1 (`n = 50`: `ρ(49)/49 = 0.9994`,
  `ρ(50)/50 = 1.0027`), the peak (`16/e² = 2.1654` at `ln(n+16) = e⁴`,
  `n ≈ 10^23.71`) and the return below 1 (`ln(n+16) = 5503.7`,
  `n ≈ e^5504 ≈ 10^2390`), and writes `latex/tables/runtime_scale.tex` and
  `latex/figures/runtime_scale.{pdf,png}` (Figure 2.2). `python3 -I
  paper3/scripts/rho_over_n.py` draws the central figure (Figure 2.1, two
  panels, with the manuscript's two unverified exponents beneath) and
  writes `latex/tables/rho_over_n.csv`. The encoding lengths quoted in
  §2.1 (`L = 1,006,223` at `n, m, k = 125, 500, 4`; `47.9 M` at
  `1000, 4000, 3`) come from `python3 -I
  reports/scratch/eth_audit/check_encoding.py`. Every comparator line
  number is at clone commit `4eaee875`; every manuscript quote gives the
  page of `paper.pdf` and the line of `reports/scratch/eth_audit/paper.txt`.
- **Section 3, what the manuscript claims beyond the statement** (item 03):
  `python3 -I paper3/scripts/beyond_claims.py` checks every page, line and
  quoted fragment of the section against the extract (page = form feeds
  before the line + 1; `paper.pdf` has 67 pages) and every Lean location
  against the read-only clone at `4eaee875` (`docs/378.md` lines 9 and 11,
  the five theorems of `SqrtLogSpace/Final.lean` at lines 10, 74, 104, 149,
  184 with their `#print axioms` at 197–201, the base-2 `rho` of
  `Asymptotics.lean` 10–11, `runtimeScale_le_four_rho` at 190–191, the
  sparsification parameters at 14–20, `MainTheorem` of
  `SqrtLog/StatementCanonical.lean` line 37), searches the family's 3,977
  `.lean` files for corollary and tensor-network identifiers (none), lists
  the files outside the family that mention ETH/SETH (two `ParityLifts`
  files, not in the closure), prints the three exponents of Theorem 1.1
  divided by `n` at constant 1 (the general one peaks at `2/e = 0.736` at
  `n = e^{e²} ≈ 1,618`; the fixed-density one is `0.578` at `n = 20` and
  falls), and writes `latex/tables/beyond_claims.tex` (Table 3.2) and
  `latex/tables/beyond_exponents.tex` (Table 3.1). Exit status non-zero if
  anything has moved; `--check` verifies without writing.
- **Section 4, the proof inspected** (item 04): `python3 -I
  paper3/scripts/proof_inspection.py` re-runs the two audit scripts
  `reports/scratch/eth_audit/closure.py` (the import closure of
  `OAI.Algorithms.SubexponentialSAT.Main`: 3,091 modules, 550,551 raw
  lines, 50 Mathlib modules + `Lean.Elab.Tactic.Omega`, the keyword
  counts with comments stripped) and `defdiff.py` (32 declarations
  `SAME`), both under `python3 -I` as subprocesses and read-only on the
  clone, and then checks what they do not: the four declarations the
  diff cannot match by itself (`countWord` identical, `runtimeScale` and
  `runtimeBound` identical up to `noncomputable def` / `noncomputable
  section`, the theorem statement identical, 1,124 characters normalised
  and 1,353 raw, challenge line 194 = `Final.lean` line 74), the 3,977
  family files and 886 outside the closure (no `sorry`/`axiom`/
  `native_decide`/`admit`, raw or stripped), the nine `opaque`s with
  bodies, the two `quotPrecheck false`, the `#print axioms` placement
  (8 closure files / 19 commands; 17 / 35 over the family directory;
  the replay's 19 in-build axiom lines all three axioms), the absence of
  any recorded `depends on axioms` output in the clone, the challenge
  JSONs (418; `enable_nanoda` false 413, true 2, absent 3), the single
  CI workflow, the toolchain, the Mathlib pin, the 42 manifest packages
  and 23 patches (none for Mathlib), the lakefile hooks, and about 60
  line citations of the proof's spine (`Final.lean`, `GuardedCompiler`,
  `CompileSpace`, `NativeOuter`, `NativeLargeEntry`, `NativeEntry`,
  `NativeOuterBudgets`, `NativeLeafContract`, `BitProgram`, the
  challenge file, `docs/378.md`, the preprint's date line, `history.md`).
  Writes `latex/tables/proof_inspection.tex` (Table 4.1) and
  `latex/tables/proof_inspection.json`; exit status non-zero if anything
  has moved; `--check` verifies without writing. Table 4.2 (the trust
  boundary) is prose from Sections 4 and 5, not generated.
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
  `4eaee875`, read with `open()` only), prints the clause-count bound
  `Σ_{j≤k} C(2n, j)` (2,604,376 at `n = 125`, `k = 3`) and `ρ(n)/n` at a
  few sizes, and writes `latex/tables/hypotheses.tex` (Table 6.1). Exit
  status non-zero if anything has moved; `--check` verifies without
  writing. No other number in Section 6 (the `A ≥ 257`, the `50 ≤ n <
  e^5504` range) is Section 6's own; each is Section 2's.
- **Section 7, for the practitioner** (item 06): `nice -n 19 python3 -I
  paper3/scripts/practitioner.py --regenerate` runs the measurement
  (about twenty minutes of wall clock on the machine of record, 1,172 s on
  2026-11-05): random 3-CNF at `m = round(4.26 n)`, `n = 20, 30, 40, 50,
  60, 80, 100, 150, 200, 250, 300, 400, 500`, twenty seeds per size,
  generated by the script from `(n, seed)`; CaDiCaL 1.9.5 through
  python-sat 1.9.dev15 (`cadical195`) for the decision bit, Ganak 2.8.0
  (pyganak, Arjun preprocessing included) for the exact count, ApproxMC
  4.4.0 (pyapproxmc, `ε = 0.8`, `δ = 0.2`, projection = all variables)
  for the approximate count, and blocking-clause enumeration over CaDiCaL
  at `n ≤ 30` as the independent check; each call in its own interpreter
  under `nice -n 19`, eight at a time, 60 s per call, censored above it; a
  tool that finishes fewer than ten of twenty at a size stops escalating.
  Writes `latex/tables/practitioner_raw.csv` (every call) and
  `latex/tables/practitioner_meta.json` (versions, CPU, load, date).
  `python3 -I paper3/scripts/practitioner.py` (seconds) rebuilds
  `latex/tables/practitioner.tex` (Table 7.1) and
  `latex/figures/practitioner.{pdf,png}` (Figure 7.1) from the CSV,
  prints every number Section 7 quotes (`t20 = 1.28e−4` s and the common
  factor `t20 / 2^20`; the 1 s crossings of the two scaled guarantees at
  `n = 33` and `35`; `2^(ρ(n) − n)` at 50, 100, 500; the decades between
  CaDiCaL's median and each guarantee at 60, 100, 200, 500), runs the
  checks (Ganak = enumeration on 40 instances at `n ≤ 30`; CaDiCaL's bit
  = `[count > 0]` everywhere both finished; ApproxMC within `1.8×` of
  Ganak on 178 of 206; the clone read with `open()` only: 3,977 family
  files, no `#eval`, no `def main`, no `IO` action, the comparator
  theorem existential in the machine at line 195) and exits non-zero if
  any fails; `--check` verifies without writing. No MOSP or pathwidth
  instance; nothing under `solutions/`. The two counters were installed
  from PyPI for this section (`pip install pyganak`; `pyapproxmc` was
  already present); no counter binary is on the host.

## The replay

Done (item 01, 2026-11-05): `replay/README.md` has the exact scripts,
the timeline, every count and hash. In one paragraph: a fresh copy of
the clone (commit `4eaee875`) was built inside a `bwrap` sandbox
(read-only system directories, a private home, the repository
invisible, PID/IPC/UTS namespaces, eight cores at `nice -n 19`, network
on for the lakefile's dependency clones and the Mathlib cache) at the
pinned `leanprover/lean4:v4.34.1` with upstream Mathlib
`d13f23b723b8a846827a245b89c10fc7d3f11612`: `lake build
OAI.Algorithms.SubexponentialSAT.Main` compiled **3,091 modules** (the
audit's closure exactly) in **33 min** with **0 `error` lines and 0
`sorry`** lines, and `#print axioms` of
`SqrtLogSpace.exact_count_and_sat` printed
`[propext, Classical.choice, Quot.sound]`. A first run (01:03) failed
at once on a `lake build -j 8` option this Lake does not have; the
second (01:16) is the one reported. Then a **second kernel**:
`lean4export` (tag `v4.34.0`, built with `v4.34.1`) exported the theorem
and its dependencies (2.36 GB, 43.6 M lines) and `nanoda_lib`
(commit `8de7e0c4`, v0.4.31) checked them: `Checked 95176 declarations
with no errors`, three axioms, exit 0, in 110 s. Regenerate the counts
with `bash paper3/replay/counts.sh`; the full build log and the export
stay in `~/dev/untrusted/replay/logs/` (hashes committed under
`replay/logs/run2/` and `replay/logs/nanoda/`).

## Open questions for the owner

See `ETH_AMBIGUOUS.MD`; item 11 lists the entries here by number.

## The CLAUDE.md paragraph

*(Item 11 drafts it here. Not applied to `CLAUDE.md`; the owner folds it.)*
