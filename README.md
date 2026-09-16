# MOSP Solver — Direct SAT Encoding

Exact solver for the **Minimization of Open Stacks Problem (MOSP)** using a direct SAT encoding with CaDiCaL, with a quick tabu search supplying the upper bound. Includes an in-progress Lean 4 formalization of the underlying pathwidth theory.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence that minimizes the maximum number of simultaneously open customer stacks. This problem is NP-hard (Linhares & Yanasse 2002).

## Approach

The solver encodes the MOSP decision problem ("can patterns be sequenced with at most k open stacks?") directly as a SAT formula, then uses **binary search** over k to find the exact optimum.

Given a MOSP instance with binary matrix M (rows = customers, columns = patterns):

1. Compute **bounds**. Lower bound: the largest number of customers requiring any single pattern. Upper bound: a **quick tabu search** -- the best of identity, reverse, and 10 random permutations, improved by tabu search over swap moves (500 iterations, tenure 7, 200 sampled neighbours per step, with an aspiration criterion).
2. **Binary search** over k in [lower, upper]: at each step, encode "MOSP <= k?" as CNF and solve with CaDiCaL.
3. The smallest satisfiable k is the exact optimal MOSP value. If the bounds already meet (`lower >= upper`), the tabu ordering is optimal and no SAT call is made.
4. **Verify** by simulating the production sequence on the witness ordering.

Solutions are cached as JSON in `solutions/` — subsequent runs verify cached solutions instead of re-solving.

### SAT Encoding

Position-based formulation with three variable families:

| Variable | Meaning |
|---|---|
| `x[p,t]` | Pattern p is placed at position t |
| `y[p,t]` | Pattern p is placed by step t (prefix) |
| `o[c,t]` | Customer c's stack is open at step t |
| `any[c,t]`, `all[c,t]` | Auxiliaries for the open-stack condition |

**Constraints:**
- **Permutation**: each pattern exactly one position, each position exactly one pattern (at-least-one + ladder at-most-one)
- **Prefix linking**: `x[p,t] -> y[p,t]`, monotonicity, converse (including t=0 base case)
- **Open stack forcing**: (a) `x[p,t] -> o[c,t]` for each pattern p of customer c; (b) `y[p,t] -> any[c,t]`, `all[c,t] -> y[p,t]`, and `any[c,t] AND NOT all[c,t] -> o[c,t]`
- **Width bound**: at most k open stacks per step (totalizer cardinality constraint)
- **Symmetry breaking**: pattern with most customers in first half of positions

Constraint (b) costs `2|P_c| + 1` clauses per (customer, step). Writing it
directly over pairs of c's patterns instead -- `y[p,t] AND NOT y[q,t] -> o[c,t]`
-- costs `|P_c|(|P_c| - 1)`, which on dense instances dominates the entire
formula: GP5 (100x100, customers needing nearly every pattern) encoded to 76.7M
clauses and cost 10.3 GB and 60s to build, against 3.25M clauses, 461 MB and
2.3s now. Only the polarities above are needed; neither auxiliary is pinned to
its full definition, but `any` occurs negatively in the forcing clause so it
stays false unless some `y[p,t]` forces it true, and `all` occurs positively so
it goes true whenever every `y[p,t]` allows. So `o[c,t]` is forced exactly when
the customer is genuinely open, never spuriously -- which would over-tighten the
width bound. The pairwise form is retained behind `pairwise_open_stacks=True`
and both are tested against exhaustive search.

## Validation Against Published Optima

Validated against all published optimal values from Frinhani et al. (2018) / Chu & Stuckey (2009):

| Instance | Size | Published OPT | Our result | Status |
|---|---|---|---|---|
| GP1 | 50×50 | 45 | 45 | exact |
| GP2 | 50×50 | 40 | 40 | exact |
| GP3 | 50×50 | 40 | 40 | exact |
| GP4 | 50×50 | 30 | 30 | exact |
| SP2 | 50×50 | 19 | 19 | exact |
| GP5 | 100×100 | 95 | — | in progress |
| GP6 | 100×100 | 75 | — | in progress |
| GP7 | 100×100 | 75 | — | in progress |
| GP8 | 100×100 | 60 | — | in progress |
| SP3 | 75×75 | 34 | — | in progress |
| SP4 | 100×100 | 53 | — | in progress |

SP2 is notable: the earlier pathwidth-based approach gave 21 (+2 overcounting). The direct SAT encoding finds the exact optimal of 19.

"Exact" means the binary search certified optimality: SAT at k with a witness ordering, UNSAT at k-1. The witness orderings are cached in `solutions/` and can be re-checked independently of the SAT solver by simulating them with `mosp.verify.max_open_stacks` -- all five reproduce the published value.

## Project Structure

```
satisfiability/                 -> SAT-based solvers
    mosp_encoding.py                Direct MOSP-to-SAT CNF encoding
    mosp_solver.py                  Solver: binary search, tabu bounds, solution caching
    encoding.py                     Pathwidth CNF encoding (legacy)
    solver.py                       Pathwidth solver (legacy)

mosp/                           -> MOSP instance handling
    instance.py                     Parse/represent MOSP instances (binary matrix)
    agreement_graph.py              Build agreement graph via M^T @ M overlap
    reduction.py                    Formal reduction: MOSP <-> pathwidth
    solver.py                       End-to-end pipeline (agreement graph approach)
    verify.py                       Simulate production sequence to count open stacks

customer_inter/                 -> Customer intersection graph approach (legacy)
    customer_graph.py               Build customer graph via M @ M^T overlap
    reduction.py                    MOSP <-> customer-graph pathwidth reduction
    solver.py                       End-to-end pipeline using customer graph
    compare.py                      Side-by-side comparison of graph formulations

fixed_parameter_algorithm/      -> Pathwidth solvers (used as subroutines)
    pathwidth.py                    Exact DP over vertex subsets (n <= 18)
    pathwidth_fpt.py                Branch-and-bound with iterative deepening (n <= 100+)
    path_decomposition.py           Extract path decomposition from ordering

solutions/                      Cached optimal solutions (JSON)

benchmarks/
    solve_parallel.py               Parallel solving: across instances, and across k
    solve_all_sat.py                Batch SAT solver for large benchmark instances
    solve_all.py                    Batch solver for published benchmark files
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output
    instances/                      Published MOSP benchmark collections
        ChallengeInstances2005/         2005 Constraint Modelling Challenge
            Harvey/ Miller/ Shaw/ Simonis/ Wilson/
        MOSP_Instances/                 SCOOP dataset collection
            Challenge/ Chu_Stuckey/ Faggioli_Bentivoglio/ SCOOP/
    results/                        Benchmark result CSVs (tracked for regression)

lean/
    MOSPFormalization/              Lean 4 proofs of the MOSP-pathwidth reduction

validate_published_optima.py    Batch validation against published optima

tests/                          147 tests across 9 test modules
literature/                     Reference papers
reports/                        Analysis documents
```

## Usage

### Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ with `networkx`, `numpy`, `python-sat`, `matplotlib`, and `pytest`.

### Solve a MOSP instance

```python
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import solve_mosp_sat

instance = MOSPInstance.from_benchmark_file("path/to/instance.txt")[0]
val, ordering = solve_mosp_sat(instance)
print(f"Optimal MOSP: {val}")
print(f"Ordering: {ordering}")
```

### Solve in parallel

Two axes of parallelism, both in `benchmarks/solve_parallel.py`:

```bash
# Fan out across instances (defaults to min(32, cores) workers)
python -m benchmarks.solve_parallel sweep --workers 30 --timeout 300 \
    --output benchmarks/results/sweep.csv

# Parallelise the binary search over k for one hard instance
python -m benchmarks.solve_parallel one GP5 --workers 28
```

`sweep` gives near-linear speedup: the benchmark tree holds 6,376 instances and
they are completely independent. Each instance still runs in its own process, so
a hung or memory-hungry solve is killed without taking the run down, and rows are
flushed to CSV as they complete.

`one` attacks a single instance. The sequential binary search issues `log2(gap)`
CaDiCaL calls strictly in order, and its hardest call is almost always the UNSAT
proof at the optimum minus one -- which it reaches *last*. Probing many k at once
starts that proof immediately. Since SAT at k implies SAT at k+1, every answer
shrinks the live interval, so each round cuts it by a factor of `workers + 1`
rather than 2, and probes whose result can no longer move either endpoint are
killed rather than awaited.

### Validate against published optima

```bash
# Runs all 11 instances, caches results, stops on mismatch
python validate_published_optima.py
```

### Run tests

```bash
python -m pytest tests/ -v
```

### Instance file formats

`MOSPInstance.from_file` reads this project's own single-instance `.mosp` format:

```
instance_name
n_customers n_patterns
<n_customers rows of n_patterns space-separated 0/1 values>
```

`MOSPInstance.from_benchmark_file` reads the published collections in
`benchmarks/instances/` and returns a **list** of instances, since many of those
files concatenate several instances (`Harvey/wbp_10_10.txt` holds 40). It handles
both layouts found there:

- **Format A** (`MOSP_Instances/`) -- one instance per file, leading `m n` line,
  matrix transposed to customers x patterns.
- **Format B** (`ChallengeInstances2005/`) -- multiple instances per file, optional
  description lines before each `m n` line, matrix already customers x patterns.

The format is auto-detected from the path; pass `transpose=` to override.

## Theoretical Foundation

The MOSP-pathwidth connection (Kinnersley 1992, Yanasse 1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

Two graph formulations provide bounds on MOSP:
- **Agreement graph** G_a(M): `pathwidth(G_a) + 1` gives a lower bound
- **Customer intersection graph** G_c(M): `pathwidth(G_c) + 1` gives an upper bound

Neither is exact on all instances. The direct SAT encoding bypasses these reductions entirely, encoding MOSP as a self-contained decision problem.

### Formal Verification in Lean 4

The `lean/` directory contains a Lean 4 formalization of the pathwidth theory. It is a work in progress, and it formalizes the *pathwidth* side of the story -- not the direct SAT encoding, and not an exact-MOSP claim.

**Complete (no `sorry`):**

- **Vertex separation = pathwidth** (Kinnersley 1992), in `VSEquivPW.lean`: proven in both directions via explicit constructions (`LayoutToDecomposition.lean` and `DecompositionToLayout.lean`).
- Supporting definitions and lemmas: linear layouts, vertex separation, path decompositions, pathwidth, MOSP instances, open-stack counting.
- `Examples.lean`: small concrete instances checking that the agreement-graph and open-stack *definitions* behave as intended. No instance is solved inside the proof assistant -- pathwidth is defined via `sInf` and is noncomputable.

**Incomplete (2 `sorry`s, both in `Reduction.lean`):**

- `openStacksAt_le_bag_card` (line 61) -- the core injection step, which needs Hall's marriage theorem under the `IsReduced` hypothesis.
- `exists_instance_achieving_equality` (line 111) -- the tightness direction.

What is stated in Lean is the one-sided bound `mospValue <= pathwidth + 1` (`mosp_le_pathwidth_add_one`, for `IsReduced` instances), and it currently rests on the first `sorry`. **Equality is not proven, and is not expected to hold in general** -- the empirical results above show `pathwidth(G_a) + 1` undercounting and `pathwidth(G_c) + 1` overcounting on real instances. Closing the tightness `sorry` would require the reduced-instance hypothesis to do real work.

The formalization includes candidates for contribution to Mathlib (`ForMathlib/`).

Building requires `elan`/`lake` with the toolchain pinned in `lean/lean-toolchain`:

```bash
cd lean && lake build
```

## Known Limitations

- **Six of the eleven published instances are still unsolved** (GP5-GP8, SP3, SP4 -- the 100x100 and 75x75 cases). These now encode in 0.4-3.3M clauses rather than tens of millions, so the obstacle is no longer building the formula but the UNSAT proof at k-1 that certifies optimality.
- **The Lean formalization is incomplete** (2 `sorry`s) and covers the pathwidth reduction, which the SAT solver no longer relies on. Only VS = PW is fully proven.
- **The pathwidth code paths are legacy.** `mosp/solver.py`, `customer_inter/`, `fixed_parameter_algorithm/`, and `satisfiability/solver.py` are retained for comparison and for the analysis in `reports/`, but neither graph formulation yields exact MOSP values on all instances.
- **`matplotlib` is listed as a dependency but imported nowhere** in the codebase.
- **There is no `LICENSE` file**, although this README states MIT and the Lean sources carry Apache 2.0 headers.

## References

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463.
- **Linhares, A. & Yanasse, H.H.** (2002). Connections between cutting-pattern sequencing, VLSI design, and flexible machines. *Computers & Operations Research*, 29, 1759-1772.
- **Chu, G. & Stuckey, P.J.** (2009). Minimizing the maximum number of open stacks by customer search. *CP 2009*, LNCS 5732, 242-257.
- **Frinhani, R.M.D. et al.** (2018). A PageRank-based heuristic for the minimization of open stacks problem. *PLOS ONE*, 13(8), e0203076.
- **Martin, M., Yanasse, H.H. & Pinto, M.J.** (2022). Mathematical models for the minimization of open stacks problem. *International Transactions in Operational Research*.

## License

MIT
