# The 34-customer instance with a wrong published optimum

Figure "The published rules report a wrong optimum" of paper 2 (Section 4,
`fig:wrong`).

| file | what it is |
|---|---|
| `instance34.mosp` | the instance, in the standard MOSP file format: 34 customers (rows) × 61 patterns (columns) |
| `solutions34.json` | both answers. For the **published rules** (Chu & Stuckey 2009, definite move + subset rule + old move + memo): the optimum they report (7, "proved by refutation"), their customer closing order and their pattern order. For the **repaired rules**: optimum 6 and an order achieving it. Also each search's answer at k = 5, 6 and 7. |
| `check.py` | a standalone checker (Python standard library only). It recomputes the peak of open stacks for both pattern orders from `instance34.mosp`. |
| `instance34.json` | the record from the search that found the instance: the graph as neighbourhood masks, the construction (two copies of a 17-customer near-miss joined by one edge), and the minimisation |

Check it with nothing but Python:

    python3 check.py

The expected output: the published order peaks at 7, the repaired order at 6,
and an order beats the published "optimum".

Reproduce both searches with the repository's solver:

    python -m pytest tests/test_false_refutation_instance.py
    python -m paper2.false_refutation_figure

Found 2026-10-09: `paper2/false_refutation_hunt.py` and
`paper2/near_miss_study.py`; write-up in `paper2/false_refutation.md`.
