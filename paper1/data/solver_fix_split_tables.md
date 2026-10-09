# Item 10: the root split (tables)

Regenerate: `python -m paper2.solver_fix_split --tables`.

| instance | value | `k` | state | tasks done / expanded nodes | nodes (split) | waste | core-hours | item 07 censored at |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| `Random-125-125-4-1_0` | 57 | 56 | **refuted** | 669 / 7 | 4.97e+10 | 1.5e+10 | 18.1 | 5.12e+10 |
| `Random-125-125-2-4_0` | 24 | 23 | partial | 1,683 / 39 | 4.72e+11 | 1.82e+11 | 148.3 | 6.28e+10 |
| `Random-125-125-4-5_0` | 46 | 45 | **refuted** | 616 / 9 | 7.96e+10 | 2.7e+10 | 26.1 | 5.52e+10 |
| `Random-125-125-4-2_0` | 57 | 56 | **refuted** | 842 / 9 | 7.64e+10 | 3.3e+10 | 30.2 | 4.99e+10 |
| `Random-125-125-2-1_0` | 24 | 23 | partial | 0 / 3 | 0 | 0 | 0.0 | 6.88e+10 |
| `Random-125-125-2-5_0` | 20 | 19 | partial | 0 / 3 | 0 | 0 | 0.0 | 6.78e+10 |
| `Random-125-125-4-4_0` | 51 | 50 | partial | 82 / 2 | 8.93e+09 | 3.57e+10 | 12.1 | 5.48e+10 |

For a partial instance the node count is the finished tasks' only: a lower bound on the split tree, not on the sequential one.
