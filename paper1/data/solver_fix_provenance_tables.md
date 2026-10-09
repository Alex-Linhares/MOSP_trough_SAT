# Item 06: evidence for each certified value

Corpus files: 6,376; certified: 6,374; open: 2.

## First independent evidence, by size (certified instances)

| customers | lattice | drat | sat | bound | customer search only | all |
|---|---:|---:|---:|---:|---:|---:|
| 1-15 | 2,812 | 0 | 0 | 0 | 0 | 2,812 |
| 16-40 | 0 | 2,902 | 417 | 2 | 2 | 3,323 |
| 41-75 | 0 | 0 | 79 | 28 | 44 | 151 |
| 76-100 | 0 | 0 | 14 | 3 | 46 | 63 |
| 101-134 | 0 | 0 | 2 | 0 | 23 | 25 |
| all | 2,812 | 2,902 | 512 | 33 | 115 | 6,374 |

## Each kind of evidence on its own (certified instances, not exclusive)

| evidence | instances |
|---|---:|
| lattice | 2,812 |
| drat | 5,646 |
| sat | 6,226 |
| bound | 4,909 |
| treewidth | 5,653 |
| expansion | 3,996 |
| sat_late | 5,897 |
| csearch_ledger | 145 |
| recertify | 6 |

## Customer search only: 115 instances (113 distinct graphs)

| certifying run (definite move as published in every row) | instances |
|---|---:|
| benchmarks.csearch, 2026-09-18: solve() defaults; Theorem 2 off; better_move code: none | 8 |
| benchmarks.csearch, 2026-09-21: solve() defaults; Theorem 2 off; better_move code: none | 7 |
| benchmarks.csearch, 2026-09-21: solve() defaults + Theorem 2; Theorem 2 on; better_move code: original (bugs A, B); one of the 55 re-refuted with the first fix on 2026-09-23 | 7 |
| customer-search sweep, 2026-09-18: solve() defaults (definite, subset, memo), then re-refuted the same way; Theorem 2 off; better_move code: none | 81 |
| re-refutation after the first better_move fix, 2026-09-23; Theorem 2 on; better_move code: first fix (pre-0eb33915) | 1 |
| recertify: decide(value - 1, better_move=True, dominators=all, memo); Theorem 2 on; better_move code: first fix (pre-0eb33915) | 11 |

Already refuted at `value - 1` by the repaired solver in items 04-05 (covered by the theorem, not independent of the search): **94 of 115**; not yet: 21.

| size class (customers × products) | instances | values |
|---|---:|---|
| 40 × 40 | 2 | 29, 30 |
| 50 × 50 | 12 | 14, 22, 24, 25, 27, 33, 35, 35, 36, 42, 43, 45 |
| 50 × 100 | 10 | 19, 20, 21, 22, 24, 35, 35, 44, 47, 48 |
| 75 × 75 | 22 | 13, 16, 16, 17, 17, 32, 32, 34, 34, 35, 35, 37, 47, 49, 51, 51, 52, 58, 59, 60, 65, 66 |
| 100 × 50 | 20 | 24, 24, 26, 29, 29, 39, 43, 44, 46, 48, 55, 55, 55, 56, 60, 65, 67, 68, 68, 68 |
| 100 × 100 | 26 | 15, 19, 20, 23, 24, 42, 43, 44, 46, 50, 53, 53, 61, 63, 65, 66, 68, 75, 76, 76, 77, 79, 83, 84, 85, 87 |
| 125 × 125 | 23 | 20, 24, 24, 46, 51, 54, 57, 57, 74, 77, 80, 80, 81, 91, 93, 94, 95, 95, 99, 103, 104, 105, 105 |
