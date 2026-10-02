# Item 10: the root split (tables)

Regenerate: `python -m paper2.solver_fix_split --tables`.

| instance | value | `k` | state | tasks done / expanded nodes | nodes (split) | waste | core-hours | item 07 censored at |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| `Random-125-125-4-1_0` | 57 | 56 | **refuted** | 669 / 7 | 4.97e+10 | 1.5e+10 | 18.1 | 5.12e+10 |
| `Random-125-125-2-4_0` | 24 | 23 | partial | 666 / 24 | 2.33e+11 | 6.3e+10 | 65.8 | 6.28e+10 |
| `Random-125-125-4-5_0` | 46 | 45 | partial | 134 / 3 | 1.42e+10 | 3e+09 | 4.0 | 5.52e+10 |
| `Random-125-125-4-2_0` | 57 | 56 | partial | 91 / 1 | 5.44e+09 | 0 | 1.5 | 4.99e+10 |
| `Random-125-125-2-1_0` | 24 | 23 | partial | 0 / 3 | 0 | 0 | 0.0 | 6.88e+10 |
| `Random-125-125-2-5_0` | 20 | 19 | partial | 0 / 3 | 0 | 0 | 0.0 | 6.78e+10 |
| `Random-125-125-4-4_0` | 51 | 50 | partial | 0 / 2 | 0 | 0 | 0.0 | 5.48e+10 |

For a partial instance the node count is the finished tasks' only: a lower bound on the split tree, not on the sequential one.
