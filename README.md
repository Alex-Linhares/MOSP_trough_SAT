# MOSP Solver — Pathwidth Reduction and SAT

Solver for the **Minimization of Open Stacks Problem (MOSP)** via reduction to pathwidth on the customer intersection graph, with pathwidth computed by SAT encoding (CaDiCaL). Includes a formal proof of the reduction in Lean 4.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence that minimizes the maximum number of simultaneously open customer stacks. This problem is NP-hard (Linhares & Yanasse 2002).

## Current Status

The pathwidth-based approach provides **provably correct pathwidth values** and **upper bounds on MOSP**. Validation against published optimal values (Frinhani et al. 2018, computed using Chu & Stuckey 2009) shows the reduction is not exact:

| Instance | Published OPT | Our result (pw+1) | Gap |
|---|---|---|---|
| GP1-4 (50×50) | 45, 40, 40, 30 | 45, 40, 40, 30 | exact |
| GP6-8 (100×100) | 75, 75, 60 | 75, 75, 60 | exact |
| GP5 (100×100) | 95 | 96 | +1 |
| SP2 (50×50) | 19 | 21 | +2 |
| SP3 (75×75) | 34 | 35 | +1 |
| SP4 (100×100) | 53 | 55 | +2 |

The pathwidth computation is provably optimal (SAT certifies via UNSAT at k-1 / SAT at k). The gap arises because the customer-to-pattern ordering derivation is heuristic — an optimal pathwidth ordering does not necessarily produce an optimal MOSP ordering on sparse instances.

**Next step: encode MOSP directly as SAT**, bypassing the pathwidth reduction. The SAT infrastructure (pysat, CaDiCaL, cardinality constraints, iterative deepening) can be reused.

## Approach

Given a MOSP instance with binary matrix M (rows = customers, columns = products):

1. Build the **customer intersection graph** G_c(M): vertices are customers, edges between customers sharing a product (`M @ M^T`).
2. Encode the pathwidth decision problem ("is pathwidth(G_c) <= k?") as a **CNF formula** and solve with CaDiCaL.
3. Use **iterative deepening** over k to find the exact pathwidth.
4. Derive a pattern ordering from the witness customer ordering.
5. The MOSP value `pathwidth(G_c) + 1` is an **upper bound** (exact on dense instances, may overcount by 1-2 on sparse instances).

### SAT Encoding for Pathwidth

Position-based formulation with three variable families:

| Variable | Meaning |
|---|---|
| `x[v,t]` | Vertex v is placed at position t |
| `y[v,t]` | Vertex v is placed by step t (prefix membership) |
| `s[v,t]` | Vertex v is separated at step t (not placed, but has a placed neighbor) |

**Constraints:**
- **Permutation**: each vertex exactly one position, each position exactly one vertex (at-least-one + ladder at-most-one)
- **Prefix linking**: `x[v,t] -> y[v,t]`, monotonicity `y[v,t] -> y[v,t+1]`, converse `y[v,t] -> y[v,t-1] OR x[v,t]`
- **Separation**: for each edge (u,v): `y[u,t] AND NOT y[v,t] -> s[v,t]`; also `y[v,t] -> NOT s[v,t]`
- **Width bound**: at most k vertices separated per step (totalizer cardinality constraint)
- **Symmetry breaking**: fix vertex 0 at position 0

The encoding produces O(n^2) variables and O(n^2 * degree) clauses.

## Pathwidth Benchmark Results

200 of 220 large instances solved (pathwidth provably optimal; MOSP values are upper bounds):

| Instance Size | Solved | Avg Time | Notes |
|---|---|---|---|
| 40×40 | 35/35 (100%) | 5s | All Chu & Stuckey densities |
| 50×50 | 25/25 (100%) | 8s | All densities |
| 50×100 | 25/25 (100%) | 11s | Customer graph has 50 nodes |
| 75×75 | 27/27 (100%) | 37s | Including density 10 |
| 100×50 | 25/25 (100%) | 84s | Customer graph has 100 nodes |
| 100×100 | 23/25 (92%) | 140s | 2 timeout at density 8, 10 |
| 125×125 | 7/25 (28%) | 109s | Density 2 + two density 4 |
| **Total** | **200/220 (91%)** | **44s** | |

Results are in `benchmarks/results/`.

## Project Structure

```
satisfiability/                 -> SAT-based pathwidth solver
    encoding.py                     Position-based CNF encoding with cardinality constraints
    solver.py                       Solver wrapper: preprocessing, iterative deepening, CaDiCaL

customer_inter/                 -> Customer intersection graph reduction
    customer_graph.py               Build customer graph via M @ M^T overlap
    reduction.py                    MOSP <-> customer-graph pathwidth reduction
    solver.py                       End-to-end pipeline using customer graph
    compare.py                      Side-by-side comparison of graph formulations

mosp/                           -> MOSP instance handling and agreement graph
    instance.py                     Parse/represent MOSP instances (binary matrix)
    agreement_graph.py              Build agreement graph via M^T @ M overlap
    reduction.py                    Formal reduction: MOSP <-> pathwidth
    solver.py                       End-to-end pipeline (agreement graph approach)
    verify.py                       Simulate production sequence to count open stacks

fixed_parameter_algorithm/      -> Alternative pathwidth solvers
    pathwidth.py                    Exact DP over vertex subsets (n <= 18)
    pathwidth_fpt.py                Branch-and-bound with iterative deepening (n <= 100+)
    path_decomposition.py           Extract path decomposition from ordering

benchmarks/
    solve_all_sat.py                Batch SAT solver for large benchmark instances
    solve_all.py                    Batch solver for published benchmark files
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output

lean/
    MOSPFormalization/              Lean 4 proofs of the MOSP-pathwidth reduction

tests/                          85 tests across 7 test modules
literature/                     Reference papers
reports/                        Analysis documents
```

## Usage

### Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ with `networkx`, `numpy`, `python-sat`, `matplotlib`, and `pytest`.

### Solve a MOSP instance (upper bound via pathwidth)

```python
from mosp.instance import MOSPInstance
from customer_inter.reduction import mosp_to_pathwidth, pathwidth_to_mosp
from satisfiability.solver import compute_pathwidth_sat
from mosp.verify import max_open_stacks

instance = MOSPInstance.from_benchmark_file("path/to/instance.txt")[0]
pw_problem = mosp_to_pathwidth(instance)
pathwidth, customer_ordering = compute_pathwidth_sat(pw_problem.graph)
solution = pathwidth_to_mosp(pw_problem, pathwidth, customer_ordering)
actual_mosp = max_open_stacks(instance, solution.ordering)
print(f"MOSP upper bound: {actual_mosp}")
print(f"Pathwidth (exact): {pathwidth}")
```

### Run benchmarks

```bash
# Solve large instances with SAT-based pathwidth solver
python -m benchmarks.solve_all_sat --timeout 300

# Run tests
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

The solver rests on a chain of equivalences (Kinnersley 1992, Yanasse 1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

Two graph formulations exist for MOSP:
- **Customer intersection graph** G_c(M): `pathwidth(G_c) + 1` gives an upper bound on MOSP. Exact on dense instances, may overcount by 1-2 on sparse ones.
- **Agreement graph** G_a(M): `pathwidth(G_a) + 1` gives a lower bound on MOSP. May undercount.

Neither formulation yields exact MOSP on all instances. The gap arises because the customer-to-pattern ordering derivation is lossy.

### Formal Verification in Lean 4

The `lean/` directory contains a Lean 4 formalization of the core theoretical results:

- **Vertex separation = pathwidth** (Kinnersley 1992): proven via explicit constructions in both directions
- **MOSP reduction**: formal proof that optimal MOSP value = pathwidth of the agreement graph + 1
- **Verified examples**: concrete MOSP instances solved and checked within the proof assistant

### Pathwidth Solvers

Three pathwidth solvers, each optimal for different regimes:

| Solver | File | Range | Method |
|---|---|---|---|
| Exact DP | `pathwidth.py` | n <= 18 | Held-Karp subset DP, O(2^n * n^2) |
| Branch-and-bound | `pathwidth_fpt.py` | n <= 100+ (small k) | Iterative deepening with DFS/backtracking |
| **SAT** | `satisfiability/` | **n <= 125** | **Position-based CNF + CaDiCaL** |

## Known Limitations

- **Pathwidth reduction is not tight**: `pathwidth(G_c) + 1` overcounts MOSP on sparse instances. A direct MOSP-to-SAT encoding is needed for exact results.
- **Agreement graph undercounts**: `pathwidth(G_a) + 1` gives a lower bound that can be too low.
- **SAT solver ceiling around n = 125**: Instances with 125 vertices and density >= 4 exceed 300s.

## References

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463.
- **Linhares, A. & Yanasse, H.H.** (2002). Connections between cutting-pattern sequencing, VLSI design, and flexible machines. *Computers & Operations Research*, 29, 1759-1772.
- **Chu, G. & Stuckey, P.J.** (2009). Minimizing the maximum number of open stacks by customer search. *CP 2009*, LNCS 5732, 242-257.
- **Frinhani, R.M.D. et al.** (2018). A PageRank-based heuristic for the minimization of open stacks problem. *PLOS ONE*, 13(8), e0203076.
- **Martin, M., Yanasse, H.H. & Pinto, M.J.** (2022). Mathematical models for the minimization of open stacks problem. *International Transactions in Operational Research*.
- **Faggioli, E. & Bentivoglio, C.A.** (1998). Heuristic and exact methods for the cutting sequencing problem. *European Journal of Operational Research*, 110(3), 564-575.

## License

MIT
