# The sandwich in Lean: tables

Regenerate: `python -m learning.sandwich`. Every table below is written by that command; `reports/ml_nature.md` §26 quotes them.

## `ForestCover.lean` against item 03's record (`reports/scratch/forest_check/record_check.csv`)

(L2) `pw(G_M) + 1 ≤ (pw(B) + 1) ω` on the rows where both pathwidths are exact; (L4) `pw(G_M) + 1 ≤ ω (tb(n + m) + 1)` on every row with `pw(G_M)` exact (every record row's incidence graph is a forest); `tb` is `treeBoundInv` as Lean defines it, equal to the least `k` with `N ≤ treeBound k` for every `N < 3001` (checked).

| family                  |   rows |   both exact (L2) |   L2 violations |   L2 slack min |   pw exact (L4) |   L4 violations |   L4 slack min |   tb(n+m) max |
|:------------------------|-------:|------------------:|----------------:|---------------:|----------------:|----------------:|---------------:|--------------:|
| caterpillar of cliques  |     24 |                24 |               0 |              2 |              24 |               0 |              4 |             5 |
| clique tree (extension) |     18 |                11 |               0 |             10 |              11 |               0 |             16 |             5 |
| clique tree (grid)      |     29 |                29 |               0 |              2 |              29 |               0 |              4 |             5 |
| forest on record        |   3448 |              3448 |               0 |              1 |            3448 |               0 |              3 |             4 |
| random block tree       |    900 |               898 |               0 |              5 |             898 |               0 |              9 |             5 |
| all                     |   4419 |              4410 |               0 |              1 |            4410 |               0 |              3 |             5 |
