# Has anyone found the error in Chu & Stuckey's Theorems 1 and 2? (2026-10-02)

The question: before the paper calls the counterexample to Chu & Stuckey
(2009) Theorems 1 and 2 new, did the authors or anyone else find the error
and correct it? **No correction was found anywhere checked. The later restatement
by the same group repeats the error.**

## What was checked

| Source | What it says about the rules |
|---|---|
| Chu & Stuckey (2009), CP, LNCS 5732 (`literature/chu_stuckey_2009.pdf`) | Theorems 1 and 2 as published; false (`Search/PublishedTheorems.lean`). |
| **Chu (2011), PhD thesis, *Improving combinatorial optimization*, Univ. of Melbourne**, ch. 6 (`literature/chu_2011_phd_thesis_improving_combinatorial_optimization.pdf`, Minerva Access hdl:11343/36679) | The later and fuller statement. **Theorem 6.3.6 is Theorem 1 word for word, with the same proof** ("at most open(q, S) extra stacks open, but at least close(q, S) extra stacks closed"). **Theorem 6.3.8, the better move, has a different premise**: `close(q, S) ≥ open(q, S ∪ {r})`, not the CP paper's `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})`. Its proof goes through the definite move. Definition 6.3.4 counts `close(c, S) = |{d : o(d, S) ⊆ o(c, S)}|` with `d` unrestricted, which is the literal reading. **Both theorems are false on `cexGraph`** (below). The thesis says its implementation of the better move subsumes the definite move. |
| Chu, Garcia de la Banda & Stuckey (2012), *Constraints* 17, "Exploiting subproblem dominance" (held) | Uses MOSP as a benchmark for generic subproblem dominance (projection keys). Does not restate the definite or better move. |
| Chu & Stuckey (2015), *Constraints* 20, "Dominance breaking constraints" (author PDF `domjournal.pdf`) | Mentions the 2009 paper only in related work, among problem-specific methods whose implementations it calls "somewhat non-rigorous", meaning they prune in the search engine instead of propagating. It points to no error. |
| Beck, Kuroiwa, Lee, **Stuckey** & Zhong (2025), CP 2025, LIPIcs 340, paper 5, "Transition dominance in DIDP" | Cites the 2009 paper as the inspiration for a transition dominance on Graph-Clear (Proposition 14). Does not revisit MOSP or its rules. |
| The 37 citing works listed by Semantic Scholar (2010–2025), including Fink (2012), de Carvalho & Soma (2015), Gonçalves et al. (2016), Frinhani et al. (2018), Martin, Yanasse & Pinto (2022), Kuroiwa & Beck (2023/2026) | None titled or described as a correction. Every held paper in `literature/` was searched for criticism of the rules; there were no hits. |
| Web searches for an erratum, counterexample or "incorrect" with the paper's title | None found. |

The Semantic Scholar list is not the full citation set (Google Scholar counts
more), so this is "not found", not "does not exist". Before submission:

- run the same check on the Google Scholar citers;
- consider writing to the authors. Stuckey is active (Monash, CP 2025). Telling
  them before publication is courteous, and it is the surest guard against a
  false claim of priority.

## The thesis's versions are false too

`python3 paper2/thesis_check.py` is an independent brute force over all
2^14 closed sets of `cexGraph` at k = 6. It shares no code with the solver or
`search_check.py`. Failures are states where a solution exists, the
premises hold, and no solution follows the move. Two readings of `close`:
customers not yet closed, and the literal one that counts every `d`.

| Statement | Failures (unclosed / literal) | First example |
|---|---|---|
| CP Thm 1 = thesis Thm 6.3.6 | 6 / 19 | S = {2}, q = 0 |
| CP Thm 2 | 8 / 27 | S = ∅, r = 2, q = 0 |
| thesis Thm 6.3.8 | 13 / 22 | S = {2}, r = 3, q = 0, close 3 ≥ open 2 (unclosed); S = {1}, r = 6, q = 12 (literal) |

## What this means for the paper

- Cite the thesis next to the CP paper. Say the thesis restates Theorem 1
  unchanged and states the better move with the premise `close(q, S)`, and that
  both are refuted by the same graph.
- A Lean theorem for the thesis's Theorem 6.3.8 would make the claim complete.
  It is a finite `decide` on `cexGraph`, in the style of
  `chuStuckey_theorem2_false`. **It has not been written.** Add it after
  loop0007 ends, not while its sessions are building Lean.
- Word the claim as "we found no prior report", not "first".
