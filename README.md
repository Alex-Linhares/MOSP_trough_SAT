# MOSP via Pathwidth Reduction

Optimal solver for the **Minimization of Open Stacks Problem (MOSP)** by reduction to **pathwidth** on the agreement graph, with a formal proof of correctness in Lean 4.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence that minimizes the maximum number of simultaneously open customer stacks. A stack is "open" from the moment the first product a customer needs is produced until the last one is produced.

This problem is NP-hard (Linhares & Yanasse 2002), but pathwidth is fixed-parameter tractable -- instances with small pathwidth can be solved efficiently regardless of total input size.

## Theoretical Foundation

The solver rests on a chain of equivalences established by Kinnersley (1992) and Yanasse (1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

where VS = vertex separation, PW = pathwidth, IT = interval thickness, SN = node search number, GML = gate matrix layout.

For a MOSP instance with binary matrix M (rows = customers, columns = products):

1. Build the **agreement graph** G(M): vertices are products, with an edge between two products iff they share at least one common customer.
2. Compute `pathwidth(G(M))` and the witness linear ordering.
3. The ordering gives the optimal production sequence; the optimal MOSP value equals `pathwidth(G(M)) + 1`.

The agreement graph is constructed via the overlap matrix M^T M -- entry (i,j) counts shared customers between products i and j, and an edge exists wherever this count is positive.

## Two Solvers

### Exact DP (n <= 25)

Held-Karp style dynamic programming over vertex subsets: O(2^n * n^2) time and O(2^n * n) space with bitmask adjacency. Guaranteed optimal for graphs up to 25 vertices.

### FPT Branch-and-Bound (n <= 100+)

For larger graphs with small pathwidth (k <= 5-8), a branch-and-bound algorithm with iterative deepening on target width k:

1. **Preprocessing**: iteratively remove degree-1 (pendant) vertices, decompose into connected components
2. **Bounds**: greedy heuristic upper bound, max-clique lower bound
3. **Search**: DFS building orderings left-to-right, pruning when vertex separation exceeds k
4. **Memoization**: bitmask-based cache for n <= 30; pruning-only for larger graphs
5. **Vertex selection**: prioritizes vertices already in the active suffix to reduce branching

The solver automatically delegates to exact DP for n <= 25 and uses the FPT algorithm for larger instances.

## Formal Verification in Lean 4

The `lean/` directory contains a Lean 4 formalization of the core theoretical results:

- **Vertex separation = pathwidth** (Kinnersley 1992): proven via explicit constructions in both directions (linear layout -> path decomposition and back)
- **MOSP reduction**: formal proof that optimal MOSP value = pathwidth of the agreement graph + 1
- **Verified examples**: concrete MOSP instances solved and checked within the proof assistant

The formalization includes candidates for contribution to Mathlib (`ForMathlib/` modules for path decomposition, vertex separation, and pathwidth).

## Project Structure

```
mosp/
    instance.py             MOSP instance representation (binary matrix)
    agreement_graph.py      Build agreement graph via M^T M
    reduction.py            Formal reduction: MOSP <-> pathwidth
    solver.py               End-to-end pipeline: parse -> graph -> pathwidth -> ordering
    verify.py               Simulate production sequence to count open stacks

fixed_parameter_algorithm/
    pathwidth.py             Exact DP over vertex subsets (n <= 25)
    pathwidth_fpt.py         FPT branch-and-bound with iterative deepening
    path_decomposition.py    Extract path decomposition from linear ordering

benchmarks/
    generator.py             Random/structured instance generation
    run_benchmarks.py        Batch solver with CSV output

lean/
    MOSPFormalization/       Lean 4 proofs (vertex separation, pathwidth, reduction)

tests/                       Comprehensive test suite (59 tests)
literature/                  Reference papers
```

## Usage

### Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9+ with `networkx`, `numpy`, `matplotlib`, and `pytest`.

### Solve a MOSP instance

```python
from mosp.solver import solve_mosp_from_file

solution = solve_mosp_from_file("path/to/instance.mosp")
print(f"Optimal open stacks: {solution.max_open_stacks}")
print(f"Production sequence: {solution.ordering}")
print(f"Pathwidth: {solution.pathwidth}")
```

### Solve from a matrix directly

```python
from mosp.instance import MOSPInstance
from mosp.solver import solve_mosp

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

### Instance file format

Standard `.mosp` files:

```
instance_name
n_customers n_patterns
<n_customers rows of n_patterns space-separated 0/1 values>
```

### Generate and run benchmarks

```bash
# Generate instances
python -c "
from benchmarks.generator import generate_benchmark_suite
generate_benchmark_suite('benchmarks/instances', sizes=[(10,10),(15,15)], densities=[0.3])
"

# Run benchmarks
python -m benchmarks.run_benchmarks benchmarks/instances benchmarks/results/output.csv
```

### Run tests

```bash
python -m pytest tests/ -v
```

## Design Decisions

**Verify by simulation, not formula alone.** The solver computes the ordering from pathwidth but determines the actual MOSP value by simulating the production sequence on the original instance. This handles the edge case where `pathwidth + 1` exceeds the number of customers.

**Two-tier solver.** The exact DP is faster for small instances (no overhead from heuristics or iterative deepening), so the FPT solver delegates to it for n <= 25. For larger instances, the preprocessing (pendant removal, component decomposition) and pruning of the FPT algorithm keep the search tractable when pathwidth is small.

**Bitmask adjacency.** Both solvers represent adjacency as integer bitmasks, making neighbor queries O(1) via bitwise AND.

## Known Limitations

- The exact DP is limited to n <= 25 vertices (exponential in n).
- The FPT solver's practical reach depends on pathwidth: it handles n = 100+ when k <= 5, but may be slow for moderate pathwidth (k >= 10) on large graphs.
- No heuristic fallback for instances beyond the exact/FPT solvers' reach.
- No implementation of the theoretical O(2^{O(k^2)} * n) algorithm (Bodlaender-Kloks), which has better worst-case guarantees but is extremely complex.

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
