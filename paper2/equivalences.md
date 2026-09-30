# The pathwidth complex: the equivalences of Table 1

Section 3 of *The pathwidth complex* (`plan.md`), built by Ralph loop0005.
Every row states what the source proves, not what Table 1 asserts, and where
it is checked (brute force, `complex_check.py`) and proved (Lean,
`../lean/MOSPFormalization/Complex/`).

## Master table

| # | Problem | Source | Defined on | Relation to pathwidth | Checked | Lean | Status |
|---|---|---|---|---|---|---|---|
| 1 | MOSP | [1] Yanasse 1997a; [4] | 0/1 matrix → MOSP graph | `= pw + 1` | corpus | `mospValue_eq_pathwidth_add_one` | proved |
| 2 | Vertex separation | [13] Kinnersley 1992 | graph | `= pw` | — | `VSEquivPW.lean` | proved |
| 3 | Graph path-width | [13] | graph | — | — | `Pathwidth.lean` | definition |

The other nine rows are item 01's.
