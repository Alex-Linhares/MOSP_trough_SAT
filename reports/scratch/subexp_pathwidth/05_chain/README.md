# loop0014 item 05 — the chain count as an algebraic object (2026-11-04)

Report section: `reports/subexp_pathwidth.md` §5. Code:
`learning/subexp_chain.py`, tests `tests/test_subexp_chain.py` (9).

Files:

- `check_atlas7.log`, `check.json` — the brute-force check of every
  statement of §5 on every graph of the atlas to 7 vertices (1,252):
  the chain count three ways (layered DP with outer boundary, with inner
  boundary, the literal sum over permutations, the count of layouts of
  `vs ≤ k`); `C_k > 0 ⟺ vs ≤ k`; `C_k(K_n) = n!`; the nested-chain CNF's
  model count (CaDiCaL, blocking over all variables) against `C_k` to 6
  vertices and a sample at 7, with its size formula; the boundary-bit and
  bare-threshold polynomial lemmas; the rank/interval count; the sieve
  over supports; the membership polynomial's degree, monomials and
  essential variables; the split ranks. §5.8 tabulates it. Zero
  failures. Committed.
- `membership_polynomial.csv` — one row per (atlas graph, `k`): degree
  and monomial count over `Q` and `GF(2)`, top coefficient, essential
  variables, `|L_k|`.
- `split_rank.csv` — one row per (connected atlas graph with `4 ≤ n ≤ 7`,
  level `vs − 1` / `vs`): min and max over balanced splits of
  `rank M_{A|B}`.
- Every encoding claimed (the nested-chain CNF, the rank formulation, the
  sieve) is checked by *counting* on small graphs, as TASK.md requires.
- Nothing was downloaded, run on an instance, or written to `solutions/`.

Regenerate:

    cd ~/dev/MOSP
    D=reports/scratch/subexp_pathwidth/05_chain
    nice -n 19 python3 -m learning.subexp_chain --nmax 7 > $D/check_atlas7.log
    python3 -m pytest tests/test_subexp_chain.py -q

`check_atlas7_attempt1_splitbug.log` is the first run, whose
`balanced_splits` skipped the odd-`n` partitions with vertex 0 on the
larger side (15 of 35 at `n = 7`); every other check in it is identical
to the corrected run. The refuter agent's own scripts lived under
`/tmp/ref/` and are not kept.
