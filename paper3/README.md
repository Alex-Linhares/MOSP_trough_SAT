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
