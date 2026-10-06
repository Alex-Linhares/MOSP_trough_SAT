# loop0009 progress

Plan: revise paper 2's draft (`paper2/latex/`) for readability, following
`paper2/review_readability.md` and the owner's notes in `TASK.md`. Items are
in `iterations.md`. Gate: `python3 Ralph_Loops/loop0009/gate.py`. It includes
`make -C paper2/latex check`.

Current: 0/11 SOLVED

## Setup — 2026-10-06

- **The draft** has 26 pages and five sections. Section 1 was written today
  from the first author's thesis (`literature/linhares_2001_phd_thesis_industrial_pattern_sequencing.pdf`).
  Table 1.1 reproduces the Linhares–Yanasse table. Yanasse is now an
  author.
- **The review** (`paper2/review_readability.md`, 617 lines):
  - The paper is reconstructable, but nearly fails in four places: the hinge
    between the halves, inconsistent counts of exact rows, the buried
    dataset, and late stakes.
  - The top 10 changes map to items 01–09.
  - Its Figure 1.1 example was verified by brute force over all 24 orders.
- **In flight.** The split run on `Random-125-125-2-2_0` and `-2-3_0` is
  running, with a watcher continuing it to 2026-10-13. Do not touch it.

---
