# The refuter pass (item 10, 2026-11-05)

One refuter subagent, the item's only one, read the built PDF
(`paper3/latex/main.pdf`, 62 pages, the 07:50 build after item 10's DOI
and Appendix A fixes) and checked every citable claim in it against the
primary sources: the clone at `4eaee875` (read with `cat`, `sed`, `grep`,
`python3 -I`; nothing run), the manuscript extract
`reports/scratch/eth_audit/paper.txt`, the two audits beside it, the
replay logs under `paper3/replay/`, the fetched texts under
`paper3/related/fetched/`, the companion Lean files and
`paper3/lean/*.log`, the measurement's `practitioner_raw.csv` and
`practitioner_meta.json`, and its own arithmetic. It was blind to the
LaTeX sources, the scripts and the loop's notes, and it edited nothing.
Its report, verbatim, is `REPORT.md` beside this file; the summary below
lists every finding, what was checked by item 10 before acting, and what
was done.

**Counts.** 21 findings: A (factual, wrong line or page or number) 6;
B (number without a stated source) 4; C (reads as an overclaim) 1;
D (out of scope) 0; E (title altered) 0; F (plain English, internal
consistency) 5; G (other) 5. **Fixed: 17. Recorded and not fixed: 4**
(R11 the title, 10b; R16 in part, 10c; R17 and R19, 10d). No finding
touches the paper's stance, its verdict on the proof, or any number of
the central argument (every value of `ρ(n)/n`, the peak, the crossing at
50, the 2,391 digits, every comparator line number, every replay and
nanoda number, every related-work quotation and all of Table 7.1 agreed).

## A — factual

| # | finding | checked | done |
|---|---|---|---|
| R1 | §3.5 said "ETH" and "SETH" occur in the collection's Lean only in two `ParityLifts` files; "ETH" also occurs in five files of this family (six comment lines) and in the theorem name `exact_count_eth` | `grep -rlw ETH` over `lean/OAI`: the five family files (`BooleanDifferences.lean` 7, 228; `Final.lean` 6; `NativeHashQueries.lean` 377; `NativeOuterBudgets.lean` 147; `NativeQueryTimeBounds.lean` 49), all comments; `SETH` nowhere | sentence rewritten (SETH nowhere; ETH in comments and one name inside the family, two files outside); the count added to `scripts/beyond_claims.py` as check 4b |
| R2 | §9.6 cited "practical" at page 4, line 153; the line is on page 3 | form feeds before line 153 at lines 53 and 104 only | "page 3"; the page added as a check to `scripts/related_work.py` |
| R3 | §4.2 / Table 4.1: 550,551 lines and 2,873 for the largest file are `split('\n')` counts, one more per file than `wc -l` (547,460 and 2,872) | arithmetic: 550,551 − 3,091 = 547,460 | the convention stated in §4.2 with both figures; the script's numbers unchanged |
| R4 | §5.1 "41 dependencies" against §4.6 and Table 4.1's 42 manifest packages | `lake-manifest.json`: 42 packages; replay copy `.lake/packages`: 42 directories | "42 dependencies (the packages of its manifest)"; `paper3/replay/README.md` corrected (it had 41) |
| R5 | §2.3 and B.2 cite `Final.lean` lines 98–101 for "80 one-bit registers and 1,220 tapes"; the 80 is at line 11 | `sed -n 11p; 98,101p` | "line 11; the machine is built from that program at lines 98–101" in both places |
| R6 | B.3 cites `GuardedCompiler.primitive_execution` at lines 158–162; it is declared at 160–162 | `sed -n 156,162p` | "lines 160–162" |

## B — numbers without a stated source

| # | finding | checked | done |
|---|---|---|---|
| R7 | §2.2 / B.1: the encoding lengths 1,006,223 and 47.9 M bits depend on the formula's literals, not on `(n, m, k)` alone; the formula was not named | `check_encoding.py` line 20: `random.seed(1)`, formulas drawn at random | "One random formula … with its random seed fixed at 1"; the dependence on the literals stated, "always under the bound" |
| R8 | §5.1 "the default target, which would build all 721 families": no source; 721 is not a family count | the collection's `README.md` line 16: "721 manuscripts organized into 373 families" | "the whole collection (its README, line 16, counts 721 manuscripts in 373 families)"; replay README corrected |
| R9 | §7.1 "counting those three patterns: 0, 0, 0": `def main` as a substring hits `def mainProgram` etc.; the pattern was not stated | `practitioner.py` line 277: `^\s*def\s+main\b`, a whole word | the patterns stated ("each as a whole word at the start of a line or before a type, so `def mainProgram` is not `def main`") |
| R10 | B.4 "14,034 lines with `decide`" is method-dependent (a different comment stripper gives 14,078) | the number is `closure.py`'s, comments stripped | "(as `closure.py` counts them, comments stripped)" |

## C — overclaim

| # | finding | done |
|---|---|---|
| R11 | The title's "is slower" read literally is a running-time claim that §1.3, §7.1 and §10 disown; the reconciliation rests on §2.5 and §7.4 | **not fixed**: the title is the owner's; recorded as `ETH_AMBIGUOUS.MD` 10b with the passages that carry the reconciliation |

## D, E — scope and title

None found. The only graph words are the manuscript's own corollary objects and the `SubexpPathwidth` directory name; the title is verbatim on page 1, in the PDF metadata and in `paper3/lean/README.md`, with no running headers.

## F — plain English and consistency

| # | finding | done |
|---|---|---|
| R12 | B.6 "equal to 1 at n = 50 up to the rounding of ρ(50) = 50.13" against Table 2.1's 50.14; the ratio is 1.10 | "just above 1 at n = 50 (ρ(50) = 50.14, ratio 1.10)" |
| R13 | Table 7.1's "sat" caption ("among those CaDiCaL finished") against cells 10/20 and 8/20 at n = 400, 500 | caption: "how many of the twenty instances CaDiCaL found satisfiable (at n = 400 and 500 only 10 and 8 finished, every one of them satisfiable)"; cells unchanged |
| R14 | §8.1 "no `sorry` and no axiom declaration anywhere" while the words occur in comments (`PrimitiveMachine.lean` 10; `Frame.lean` 13, 83) | "outside its comments", with the three lines named |
| R15 | `lean4export` and `nanoda_lib` used in Table 4.2 before their gloss; `tmpfs` and SHA-256 never glossed; `m = ⌊4.26 n⌉` unexplained | `lean4export` glossed at its first use in Table 4.2 (nanoda was already glossed in §4.7, before the table); `tmpfs` and SHA-256 glossed at first use in §5; "(4.26 n rounded to the nearest whole number)" |
| R16 | 21 sentences of 59–151 words named, about forty more of 46–58 | the 21 named split, one idea per sentence, quotations intact; the rest recorded as 10c with a before/after count |

## G — other

| # | finding | done |
|---|---|---|
| R17 | "Placeholder" boxes for the data statement and the acknowledgements | item 11's by the brief; **not fixed** (10d) |
| R18 | §3.2 "the manuscript's exponents are undefined below n = e": `ln ln n` is undefined at n ≤ 1 and negative for 1 < n < e | "negative below n = e (and undefined at n ≤ 1)" |
| R19 | the audits and the replay README carry counts the paper corrected (41/42, 33/35, line 181/194, 416/413, 17 files/8) | replay README corrected (three cells); the two audits left as dated scratch records for item 11's note, **recorded** (10d) |
| R20 | Figure 7.1's caption "The same data" has no antecedent | "Table 7.1's data" |
| R21 | the quotation at §2.2 cited to line 44 spans lines 44–45 | "lines 44–45" |

## Also done by item 10, outside the refuter's list

- `paper3/latex/sec7_practitioner.tex`: the sentence pairing `A ≥ 257`
  with `C ≥ 28,701` (item 09's reader had flagged the pairing in the
  conclusion; this one was left) now gives both readings with their
  sections.
- Appendix A's two overfull boxes (the `\leangroup` rows, a
  non-wrapping `l` cell) fixed by a wrapping `p{}` cell in `main.tex`;
  the paper builds with zero overfull boxes.
- The bibliography: `paper3/scripts/check_refs.py`, every DOI checked
  (`paper3/latex/doi_check.log`: 22 entries, 15 with a DOI, 0 disagree),
  thirteen DOIs found and added (10a).

## After the fixes

`make -C paper3/latex check` passes (62 pages, 0 overfull boxes, no
undefined reference or citation); every section's check script passes
(`beyond_claims.py --check`, `proof_inspection.py --check`,
`consequences.py --check`, `lean_rediff.py --check`,
`related_work.py --check`, `practitioner.py --check`, `runtime_scale.py`,
`check_refs.py`). The refuter was not re-run on the fixed PDF (one
subagent per item); the fixes are each a few words at a located place
and were re-read by item 10.

## What this does not claim

The refuter read one build of one PDF on one day; a finding it did not
file is not a claim that none exists. Its checks of the clone were by
`grep`, `sed` and its own small scripts, never by building anything.
"Agreed" means the quoted text or number matched the source at the cited
place; it does not mean the source is right.
