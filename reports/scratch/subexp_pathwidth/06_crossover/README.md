# loop0014 item 06 — algorithms from the counting theorem at linear pathwidth (2026-11-04)

Report section: `reports/subexp_pathwidth.md` §6. Code:
`learning/subexp_crossover.py`, tests `tests/test_subexp_crossover.py` (10).
Lean: `lean/MOSPFormalization/SubexpPathwidth/Crossover.lean` (24 declarations).

Files:

- `check_atlas7.log`, `check.json` — the brute-force check of every encoding
  of §6 on every graph of the networkx atlas to 7 vertices (1,252 graphs,
  129,761 evaluations, zero failures, 119 s): independent-set count and width;
  the threshold formula `|S| ≥ t` for every `t` (count-preserving, decides
  `α ≥ t`, width 3); `q`-colouring counts for `q = 2, 3` (and 4 to 6
  vertices); dominating-set counts, direct and Tseitin, and `γ ≤ t`; Max-Cut
  `≥ t` counts and decisions; odd cycle transversal `≤ t` decisions; the Cut & Count formula's parity against the
  number of Hamiltonian cycles, its exact value `Σ_X 2^{cc(X) − 1}` against
  two-factor enumeration (`m ≤ 15`), the soundness of the weighted decision
  with one random weight vector per graph, and its completeness rate (435 of
  443 graphs with a cycle). Also the size constants (variables and clauses
  over `n + m`), the threshold circuit's auxiliaries per input to `n = 200`
  (`≤ 6.98`), and the crossover table. Committed.
- `axiom_check.lean`, `axiom_check.log` — the axiom audit of the Lean file:
  every declaration on `[propext, Classical.choice, Quot.sound]` or fewer.
- `gate.log` — the gate run.
- `refuter.md` — the refuter subagent's report (one subagent, the only one
  used).
- Nothing was downloaded, run on an instance, or written to `solutions/`.
  No pathwidth was computed; the item is about problems *parameterised by*
  pathwidth.

Regenerate:

    cd ~/dev/MOSP
    D=reports/scratch/subexp_pathwidth/06_crossover
    nice -n 19 python3 -m learning.subexp_crossover --nmax 7 --out $D > $D/check_atlas7.log
    python3 -m learning.subexp_crossover --table
    python3 -m pytest tests/test_subexp_crossover.py -q
    cd lean && lake build && lake env lean ../$D/axiom_check.lean | tee ../$D/axiom_check.log
