# loop0014 progress

Plan: `reports/subexp_pathwidth_plan.md` — pathwidth after ETH: a
subexponential exact algorithm for pathwidth conditional on the formally
verified subexponential `#k`-SAT theorem (restated as a `Prop`, never
asserted), or a formalised linear reduction naming what such an algorithm
would refute, and a map of the post-ETH hypothesis landscape for width
parameters; items in `iterations.md`; rules in `TASK.md`. Gate:
`python3 Ralph_Loops/loop0014/gate.py`.

Current: 1/12 SOLVED

## Setup — 2026-11-04

- Driver, gate and knobs cloned from loop0013 (`sed s/loop0013/loop0014/`);
  `allowed_sorries.txt` empty; `max_iterations` 16, item cap 4 h, fix cap
  0.75 h, 3 fix attempts, one retry after a network error.
- The OpenAI collection is cloned read-only under `~/dev/untrusted/`
  (never built, never run from inside); nothing of it is imported into
  `lean/`.
- Tree clean at launch; the last commits are the checkpoint relaxation
  (`3161ff6b2`, `484ca6ff3`), the two-ended measurement (`6869dfba0`) and
  the plan (`bc5ca4cfd`).

---

## Iteration 1 — 2026-11-04 18:35

Item 01, the audit and the kill check. Report: `reports/subexp_pathwidth.md`
§1 (4,300 words; §0 is left for item 11). Scratch:
`reports/scratch/subexp_pathwidth/01_audit/` (README with regenerate
commands; the `pdftotext` extracts git-ignored; the subagent's second
reading committed).

### Completed

- The ETH paper read as the item specifies (Sections 1, 2, 3.5, Lemma 4.8,
  5, 6, Appendices C and D through D.4.2), extracted once to
  `01_audit/eth.txt`; nothing in the untrusted clone built or run. The
  formally verified comparator statement read with `cat`: **it carries the
  weaker exponent** `n (log log n)² / √log n` (Proposition 6.4's route); the
  sharper `n log log n / √log n` and the fixed-density `n / √log n` of
  Theorem 1.1 are paper-only (Appendix D, `lean/docs/378.md` says so).
  Item 02 must restate the verified form, not Theorem 1.1.
- §1.1 (a): the bases. Pathwidth `O(1.89ⁿ)` (Kitsunai et al. 2016, held)
  and `O*(1.9657ⁿ)` (Suchan & Villanger 2009, held); treewidth `1.7549`
  (Fomin & Villanger 2012, not held) and `1.7347` (as recalled, not held);
  cutwidth, OLA, FAS stuck at `O*(2ⁿ)` with no `c < 2` on record (Bentert
  et al. ITCS 2025, held, says so explicitly); bandwidth below 5 (Cygan &
  Pilipczuk 2010, not held, base from memory). **No `2^{o(n)}` exact
  algorithm for any of them is on record.**
- §1.2 (b): ETH/SETH-conditional bounds on *computing* the widths. One
  found, and it matters: **Bonnet (JACM 2025, arXiv 2406.11628; abstract on
  disk in `paper1/data/openalex_candidates.json`, paper not held) proves
  `2^{Ω(n)}` for exact treewidth under ETH by "a simple, self-contained
  reduction from 3-SAT"**, and says the earlier chains through cutwidth /
  pathwidth on bounded-degree graphs gave only `2^{Ω(√n)}`. No sentence of
  the form "no `2^{o(n)}` for pathwidth unless ETH fails" was found in any
  held paper or on-disk title; no SETH bound on computing any width. The
  Lampis primal-pathwidth SETH (SODA 2025) is on disk as a title, for item
  10.
- §1.3 (c): the two-page account. The method computes
  `Σ_x Π_f Φ_f(x|I_f)` over a Boolean cube; the exponent is in the cube's
  dimension (CNF form) or in the number of **wires = total
  variable–constraint incidence** (tensor form, Theorem D.1). Requirements
  R1–R6: bounded-degree factors, **linear total degree (so `O(n)`
  constraints)**, polylog incidence per variable after branching on
  `n/√log n` frequent ones, the separating design (supplied by the paper,
  not the problem), integer counts modulo `2^{n+1}`, and — tensor form —
  vertices of degree up to `s^{9/10}` with `2^{O(s^{9/10})}`-time entries, so
  **a wide threshold constraint costs its width in wires and nothing more**;
  what fixed `k` buys is sparsification (`B = (log n)^{Θ(k)}`) and the
  replacement-row degree. It counts, hence decides, finds witnesses by
  self-reduction, samples uniformly, and takes weights in any commutative
  `Q`-algebra or `(Z/2^P)[V]/(V^ℓ)`. **The budget for pathwidth** (§1.3.8):
  an encoding of "`vs ≤ k`" needs `N = o(n √log n / (log log n)²)` CNF
  variables (verified route) or `s = o(n √log n)` wires (paper route);
  the position and nested-chain encodings are `Θ(n²)`; a layout is
  `n log₂ n` bits, so a witness that determines the layout already exceeds
  the verified budget — the certificate must be another object. Cross-checked
  by one subagent's blind second reading: no disagreement.
- §1.4, the kill check: **not killed** on either criterion (no `2^{o(n)}`
  pathwidth algorithm on record; the method's failure on every NP-hard
  width problem is not demonstrated — nothing is demonstrated either way).
- §1.5 what this does not claim; §1.6 regenerate. `.gitignore` entry for
  the extracts.

### Blockers

None. Subagents used: 1 of 4.

### Next

Item 02 (the formal frame), restating the **verified** statement: for each
`k ≥ 2`, a machine and constants with time
`≤ C (L + 1)^d · 2^{A · n (log log(n+16))² / √log(n+16)}` on every
width-`≤ k` CNF on `n` variables; not Theorem 1.1's sharper exponents. Two
findings for the later items: item 03 should start from Bonnet's reduction
and ask whether its graphs have `pw = tw` (if so, the linear ETH bound
transfers to pathwidth at blow-up 1, and the only hypothesis a `2^{o(n)}`
pathwidth algorithm is known to refute is ETH itself, already refuted);
items 04/05 should look for a certificate of "`vs ≤ k`" with total
incidence `o(n √log n)` and constraints of any width, not for
bounded-width clauses. Missing papers for item 11's `MISSING.md`: listed at
the end of §1.2.
