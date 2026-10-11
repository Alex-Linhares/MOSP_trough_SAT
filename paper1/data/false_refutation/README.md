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
    python -m paper1.false_refutation_figure

Found 2026-10-09: `paper1/false_refutation_hunt.py` and
`paper1/near_miss_study.py`; write-up in `paper1/false_refutation.md`.

## The DRAT refutation of k = 5 (`drat/`)

The SAT encoding of Appendix D (`satisfiability/mosp_encoding.py`) at k = 5:
31,598 variables, 109,923 clauses. CaDiCaL 1.9.5 refutes it in 53 s and logs
a DRAT proof of 1,403,159 lemmas (112 MB gzipped, not committed); drat-trim
verifies it in 44 s.

| file | what it is |
|---|---|
| `false_refutation_34__k5.json` | the certificate record: encoding parameters, CNF and proof SHA-256 |
| `false_refutation_34__k5.core.drat.xz` | the proof trimmed by drat-trim (`drat-trim f.cnf p.drat -l core.drat`) to the lemmas the refutation uses, 27 MB as xz |
| `false_refutation_34__k5.core.drat.xz.sha256` | its SHA-256 |
| `check_proof.sh` | rebuilds the CNF from the instance, checks its hash against the record, checks the proof |

From the repository root (about 35 s; needs `tools/drat-trim` built):

    bash paper1/data/false_refutation/drat/check_proof.sh

Expected: `s VERIFIED`. With k = 6 satisfiable (the repaired order above),
the optimum is 6, independently of both customer searches.
