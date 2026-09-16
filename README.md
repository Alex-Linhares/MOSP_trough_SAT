# MOSP via SAT-based Pathwidth Reduction

Optimal solver for the **Minimization of Open Stacks Problem (MOSP)** by reduction to **pathwidth** on the customer intersection graph, solved via **SAT encoding** with CaDiCaL. Includes a formal proof of correctness in Lean 4.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence that minimizes the maximum number of simultaneously open customer stacks. A stack is "open" from the moment the first product a customer needs is produced until the last one is produced.

This problem is NP-hard (Linhares & Yanasse 2002). We reduce it to pathwidth computation on the customer intersection graph, then solve pathwidth optimally using a position-based SAT encoding.

## Approach

Given a MOSP instance with binary matrix M (rows = customers, columns = products):

1. Build the **customer intersection graph** G_c(M): vertices are customers, with an edge between two customers iff they share at least one common product (`M @ M^T`).
2. Encode the pathwidth decision problem ("is pathwidth(G_c) <= k?") as a **CNF formula** and solve with CaDiCaL.
3. Use **iterative deepening** over k to find the exact pathwidth.
4. Derive the optimal production sequence from the witness ordering; the optimal MOSP value equals `pathwidth(G_c) + 1`.

### SAT Encoding

Position-based formulation with three variable families:

| Variable | Meaning |
|---|---|
| `x[v,t]` | Vertex v is placed at position t |
| `y[v,t]` | Vertex v is placed by step t (prefix membership) |
| `s[v,t]` | Vertex v is separated at step t (not placed, but has a placed neighbor) |

**Constraints:**
- **Permutation**: each vertex gets exactly one position, each position gets exactly one vertex (at-least-one + ladder at-most-one)
- **Prefix linking**: `x[v,t] -> y[v,t]`, monotonicity `y[v,t] -> y[v,t+1]`, converse `y[v,t] -> y[v,t-1] OR x[v,t]`
- **Separation**: for each edge (u,v): `y[u,t] AND NOT y[v,t] -> s[v,t]`; also `y[v,t] -> NOT s[v,t]`
- **Width bound**: at most k vertices separated per step (totalizer cardinality constraint)
- **Symmetry breaking**: fix vertex 0 at position 0

The encoding produces O(n^2) variables and O(n^2 * degree) clauses. For n=100, this is roughly 100K variables and 500K clauses.

## Benchmark Results

Tested on 220 published benchmark instances that were previously unsolvable (both n_customers > 30 and n_patterns > 30), with a 300-second per-instance timeout:

| Instance Size | Solved | Avg Time | Notes |
|---|---|---|---|
| 40x40 | 35/35 (100%) | 5s | All Chu & Stuckey densities |
| 50x50 | 25/25 (100%) | 8s | All densities |
| 50x100 | 25/25 (100%) | 11s | Customer graph has 50 nodes |
| 75x75 | 27/27 (100%) | 37s | Including density 10 |
| 100x50 | 25/25 (100%) | 84s | Customer graph has 100 nodes |
| 100x100 | 23/25 (92%) | 140s | 2 timeout at density 8, 10 |
| 125x125 | 7/25 (28%) | 109s | Density 2 + two density 4 |
| Challenge/Wilson | 22/22 (100%) | 11s | Up to 100x100 |
| Faggioli/SCOOP | 23/23 (100%) | 5s | Real-world manufacturing |
| **Total** | **200/220 (91%)** | **44s** | **All provably optimal** |

All solved instances produce provably optimal results: the SAT solver certifies pathwidth = k by proving UNSAT at k-1 and SAT at k. Results are in `benchmarks/results/`.

## Project Structure

```
satisfiability/                 -> SAT-based pathwidth solver (primary)
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

fixed_parameter_algorithm/      -> Alternative pathwidth solvers (small instances)
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

### Solve a MOSP instance with SAT

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
print(f"Optimal open stacks: {actual_mosp}")
print(f"Production sequence: {solution.ordering}")
```

### Solve from a matrix directly

```python
from mosp.instance import MOSPInstance
from customer_inter.solver import solve_mosp

# Rows = customers, columns = products
# M[i][j] = 1 means customer i needs product j
matrix = [
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]
instance = MOSPInstance.from_matrix(matrix, name="example")
solution = solve_mosp(instance)
print(f"Optimal: {solution.max_open_stacks}, Ordering: {solution.ordering}")
```

### Run benchmarks

```bash
# Solve large instances with SAT solver
python -m benchmarks.solve_all_sat --timeout 300

# Solve all published benchmarks (agreement graph, branch-and-bound)
python -m benchmarks.solve_all --timeout 120

# Compare agreement vs customer graph approaches
python -m customer_inter.compare
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

The solver rests on a chain of equivalences (Kinnersley 1992, Yanasse 1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

Two graph formulations exist for MOSP:
- **Customer intersection graph** G_c(M): nodes = customers, edge iff two customers share a product. `MOSP(M) = pathwidth(G_c) + 1`. This is the formulation used by the SAT solver.
- **Agreement graph** G_a(M): nodes = products, edge iff two products share a customer. Pathwidth gives a lower bound but can undercount on some instances.

### Formal Verification in Lean 4

The `lean/` directory contains a Lean 4 formalization of the core theoretical results:

- **Vertex separation = pathwidth** (Kinnersley 1992): proven via explicit constructions in both directions
- **MOSP reduction**: formal proof that optimal MOSP value = pathwidth of the agreement graph + 1
- **Verified examples**: concrete MOSP instances solved and checked within the proof assistant

Includes candidates for contribution to Mathlib (`ForMathlib/` modules).

## Pathwidth Solvers

The project includes three pathwidth solvers, each optimal for different regimes:

| Solver | File | Range | Method |
|---|---|---|---|
| Exact DP | `pathwidth.py` | n <= 18 | Held-Karp subset DP, O(2^n * n^2) |
| Branch-and-bound | `pathwidth_fpt.py` | n <= 100+ (small k) | Iterative deepening with DFS/backtracking |
| **SAT** | `satisfiability/` | **n <= 125** | **Position-based CNF + CaDiCaL** |

The SAT solver (`compute_pathwidth_sat()`) is a drop-in replacement for `compute_pathwidth_fpt()` — same interface, same preprocessing (pendant removal, component decomposition), same bounds (greedy upper, clique lower). It delegates to exact DP for n <= 18 automatically.

## Known Limitations

- **SAT solver ceiling around n = 125**: The position-based encoding produces O(n^2) variables and O(n^2 * degree) clauses. Instances with 125 vertices and density >= 4 (pathwidth >= 50) exceed 300s. The 20 remaining unsolved benchmark instances are all 125x125 Chu & Stuckey with density 4-10.
- **Exact DP ceiling at n = 18**: The subset DP uses O(2^n) space/time.
- **Branch-and-bound depends on pathwidth**: Handles n = 100+ when k <= 5, but slows down for moderate pathwidth (k >= 10) on large graphs.
- **No heuristic fallback**: For instances beyond all three solvers' reach, there is currently no approximate/heuristic mode.

## References

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463.
- **Linhares, A. & Yanasse, H.H.** (2002). Connections between cutting-pattern sequencing, VLSI design, and flexible machines. *Computers & Operations Research*, 29, 1759-1772.
- **Chu, G. & Stuckey, P.J.** (2009). Minimizing the maximum number of open stacks by customer search. *CP 2009*, LNCS 5732, 242-257.
- **Faggioli, E. & Bentivoglio, C.A.** (1998). Heuristic and exact methods for the cutting sequencing problem. *European Journal of Operational Research*, 110(3), 564-575.
- **Kirousis, L.M. & Papadimitriou, C.H.** (1986). Searching and pebbling. *Theoretical Computer Science*, 47, 205-218.
- **Fellows, M.R. & Langston, M.A.** (1989). On search, decision, and the efficiency of polynomial-time algorithms. *Proc. 21st ACM STOC*, 501-512.

## License

MIT
