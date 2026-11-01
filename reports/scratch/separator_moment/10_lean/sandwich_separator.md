# The sandwich in Lean: tables

Regenerate: `python -m learning.sandwich`. Every table below is written by that command; `reports/ml_nature.md` §26 quotes them.

## `SeparatorMoment.lean` against `learning.separator_moment` (loop0011 item 10)

500 random `G(n, p)` graphs with exact pathwidth, 1000 `(graph, k)` rows at `k = pw` and `k = pw + 1`, 0.7 s. L1: an exact-size empty pair exists and its complement is a `k`-set; L1′: the complement is in `E_bip` and every component of `G − S` has at most `t` vertices; L2: the one-round closure `closeStep` (transcribed from Lean) is monotone, closed, idempotent, has separator `N(A*) ∩ N(R*)`, keeps the sizes, and equals item 03's `close_pair`; `sees both` is `isClosedPair_iff_sees_both` on random pairs. Each count is the number of rows where the statement holds.

|   n | k      |   rows |   pairs (median) |   L1 |   L1′ |   L2 |   sees both |
|----:|:-------|-------:|-----------------:|-----:|------:|-----:|------------:|
|   5 | pw + 1 |     76 |             10   |   76 |    76 |   76 |          76 |
|   5 | pw     |     76 |              6   |   76 |    76 |   76 |          76 |
|   6 | pw + 1 |     55 |             20   |   55 |    55 |   55 |          55 |
|   6 | pw     |     55 |              8   |   55 |    55 |   55 |          55 |
|   7 | pw + 1 |     70 |             26.5 |   70 |    70 |   70 |          70 |
|   7 | pw     |     70 |             11   |   70 |    70 |   70 |          70 |
|   8 | pw + 1 |     68 |             37   |   68 |    68 |   68 |          68 |
|   8 | pw     |     68 |             10   |   68 |    68 |   68 |          68 |
|   9 | pw + 1 |     64 |             58.5 |   64 |    64 |   64 |          64 |
|   9 | pw     |     64 |             14   |   64 |    64 |   64 |          64 |
|  10 | pw + 1 |     78 |             87.5 |   78 |    78 |   78 |          78 |
|  10 | pw     |     78 |             20   |   78 |    78 |   78 |          78 |
|  11 | pw + 1 |     89 |             92   |   89 |    89 |   89 |          89 |
|  11 | pw     |     89 |             16   |   89 |    89 |   89 |          89 |
