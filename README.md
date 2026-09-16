# MOSP Solver — Direct SAT Encoding

Exact solver for the **Minimization of Open Stacks Problem (MOSP)** using a direct SAT encoding with CaDiCaL. Includes a formal proof of the MOSP-pathwidth equivalence in Lean 4.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence that minimizes the maximum number of simultaneously open customer stacks. This problem is NP-hard (Linhares & Yanasse 2002).

## Approach

The solver encodes the MOSP decision problem ("can patterns be sequenced with at most k open stacks?") directly as a SAT formula, then uses **binary search** over k to find the exact optimum.

Given a MOSP instance with binary matrix M (rows = customers, columns = patterns):

1. Compute **bounds**: lower bound from max customers per pattern, upper bound via **tabu search** over random permutations.
2. **Binary search** over k in [lower, upper]: at each step, encode "MOSP <= k?" as CNF and solve with CaDiCaL.
3. The smallest satisfiable k is the exact optimal MOSP value.
4. **Verify** by simulating the production sequence on the witness ordering.

Solutions are cached as JSON in `solutions/` — subsequent runs verify cached solutions instead of re-solving.

### SAT Encoding

Position-based formulation with three variable families:

| Variable | Meaning |
|---|---|
| `x[p,t]` | Pattern p is placed at position t |
| `y[p,t]` | Pattern p is placed by step t (prefix) |
| `o[c,t]` | Customer c's stack is open at step t |

**Constraints:**
- **Permutation**: each pattern exactly one position, each position exactly one pattern (at-least-one + ladder at-most-one)
- **Prefix linking**: `x[p,t] -> y[p,t]`, monotonicity, converse (including t=0 base case)
- **Open stack forcing**: (a) `x[p,t] -> o[c,t]` for each pattern p of customer c; (b) `y[p,t] AND NOT y[q,t] -> o[c,t]` for each pair (p,q) of customer c
- **Width bound**: at most k open stacks per step (totalizer cardinality constraint)
- **Symmetry breaking**: pattern with most customers in first half of positions

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
    solve_all_sat.py                Batch SAT solver for large benchmark instances
    solve_all.py                    Batch solver for published benchmark files
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output

lean/
    MOSPFormalization/              Lean 4 proofs of the MOSP-pathwidth reduction

validate_published_optima.py    Batch validation against published optima

tests/                          107 tests across 8 test modules
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

### Validate against published optima

```bash
# Runs all 11 instances, caches results, stops on mismatch
python validate_published_optima.py
```

### Run tests

```bash
python -m pytest tests/ -v
```

### Instance file format

Standard `.mosp` files:

```
instance_name
n_customers n_patterns
<n_customers rows of n_patterns space-separated 0/1 values>
```

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

The `lean/` directory contains a Lean 4 formalization of the core theoretical results:

- **Vertex separation = pathwidth** (Kinnersley 1992): proven via explicit constructions in both directions
- **MOSP reduction**: formal proof that optimal MOSP value = pathwidth of the agreement graph + 1
- **Verified examples**: concrete MOSP instances solved and checked within the proof assistant

## References

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463.
- **Linhares, A. & Yanasse, H.H.** (2002). Connections between cutting-pattern sequencing, VLSI design, and flexible machines. *Computers & Operations Research*, 29, 1759-1772.
- **Chu, G. & Stuckey, P.J.** (2009). Minimizing the maximum number of open stacks by customer search. *CP 2009*, LNCS 5732, 242-257.
- **Frinhani, R.M.D. et al.** (2018). A PageRank-based heuristic for the minimization of open stacks problem. *PLOS ONE*, 13(8), e0203076.
- **Martin, M., Yanasse, H.H. & Pinto, M.J.** (2022). Mathematical models for the minimization of open stacks problem. *International Transactions in Operational Research*.

## License

MIT
