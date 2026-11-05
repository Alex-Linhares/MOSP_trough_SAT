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

*(Filled in by the items, section by section. Until then: the `ρ(n)/n`
numbers come from `python3 -I reports/scratch/eth_audit/check_encoding.py`;
the closure counts from `python3 -I reports/scratch/eth_audit/closure.py`
and `defdiff.py`, read-only on the clone.)*

## The replay

Started by the coordinator on 2026-11-05 at 01:03 from
`~/dev/untrusted/replay/` (`run_sandbox.sh`: bubblewrap with read-only
`/usr /lib /bin /etc`, a private `/home` with `/home/al` bound to
`replay/home`, the repository invisible, network on for the lakefile's
clone hooks and the `elan`/Mathlib downloads, `nice -n 19`; `replay.sh`
inside: `elan` into the private home, `lake exe cache get`, `lake build
OAI.Algorithms.SubexponentialSAT.Main -j 8`, `#print axioms` of
`exact_count_and_sat`, exit code to `replay/logs/DONE`). *(Item 01 writes
the rest here: the versions, the `#print axioms` output, the time, the
hashes of the logs, whether nanoda ran; `replay/README.md` quotes both
scripts.)*

## Open questions for the owner

See `ETH_AMBIGUOUS.MD`; item 11 lists the entries here by number.

## The CLAUDE.md paragraph

*(Item 11 drafts it here. Not applied to `CLAUDE.md`; the owner folds it.)*
