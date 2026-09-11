# MOSP via Pathwidth FPT Reduction

## What This Project Is

This project solves the **Minimization of Open Stacks Problem (MOSP)** optimally by reducing it to **pathwidth computation** on graphs, with a formal proof of correctness in Lean 4. MOSP is NP-hard, but pathwidth is fixed-parameter tractable (FPT) — meaning instances with small pathwidth can be solved efficiently regardless of input size. We exploit this structural property.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence for the products that minimizes the maximum number of simultaneously "open" customer stacks. A stack opens when the first product a customer needs is produced and closes when the last one is done.

## Theoretical Foundation

The key equivalence chain (Kinnersley 1992, Yanasse 1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

For MOSP specifically:
- Build the **agreement graph** G(M): nodes = patterns (products), edge between two patterns iff they share at least one common customer
- **Optimal MOSP value** = pathwidth(G) + 1 (with the caveat that actual open stacks cannot exceed the number of customers)
- A linear vertex ordering achieving optimal pathwidth directly gives the optimal production sequence

### Key References

- **Kinnersley (1992)** — Established vertex separation = pathwidth. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse (1997)** — Formulated MOSP in terms of the agreement graph. *European Journal of Operational Research*, 100(3), 454-463.
- **Linhares & Yanasse (2002)** — Proved MOSP is NP-hard. *Computers & Operations Research*, 29, 1759-1772.
- **Chu & Stuckey (2009)** — Benchmark instances and constraint-based approaches. *CP 2009*, LNCS 5732, 242-257.
- **Faggioli & Bentivoglio (1998)** — Heuristic approaches and instance generation. *European Journal of Operational Research*, 110(3), 564-575.
- **Kirousis & Papadimitriou (1986)** — Graph searching and pathwidth connections. *Theoretical Computer Science*, 47, 205-218.
- **Fellows & Langston (1989)** — FPT algorithms for pathwidth. *Proc. 21st ACM STOC*, 501-512.

## Architecture

```
mosp/
    instance.py             → Parse/represent MOSP instances (binary matrix)
    agreement_graph.py      → Build MOSP graph via M^T @ M overlap
    reduction.py            → Formal reduction: MOSP ↔ pathwidth
    solver.py               → End-to-end pipeline: parse → graph → pathwidth → ordering
    verify.py               → Simulate production sequence to count open stacks

fixed_parameter_algorithm/
    pathwidth.py            → Exact DP over vertex subsets (n ≤ 25)
    pathwidth_fpt.py        → FPT branch-and-bound with iterative deepening (n ≤ 100+)
    path_decomposition.py   → Extract path decomposition from ordering

benchmarks/
    generator.py            → Random/structured instance generation
    run_benchmarks.py       → Batch solver with CSV output

lean/
    MOSPFormalization/      → Lean 4 proofs of the MOSP-pathwidth reduction
        LinearLayout.lean         Linear vertex orderings
        VertexSeparation.lean     Vertex separation number
        PathDecomposition.lean    Path decomposition structure
        Pathwidth.lean            Pathwidth definitions
        LayoutToDecomposition.lean   Layout → decomposition construction
        DecompositionToLayout.lean   Decomposition → layout construction
        VSEquivPW.lean            VS = PW proof (Kinnersley 1992)
        MOSPInstance.lean         MOSP instance formalization
        OpenStacks.lean           Open stacks counting
        Reduction.lean            MOSP ↔ pathwidth reduction proof
        Examples.lean             Verified example instances
        ForMathlib/               Candidates for Mathlib contribution

tests/                      → 59 tests across 6 test modules
literature/                 → Reference papers (PDFs)
```

## Two Solvers

### Exact DP (n ≤ 25)

O(2^n · n²) Held-Karp style subset DP with bitmask adjacency. Guaranteed optimal. Used automatically for small graphs.

### FPT Branch-and-Bound (n ≤ 100+)

For larger graphs with small pathwidth k. The algorithm:
1. **Preprocesses**: removes degree-1 (pendant) vertices iteratively, decomposes into connected components
2. **Bounds**: greedy heuristic upper bound, max-clique lower bound (pathwidth ≥ ω(G) - 1)
3. **Iterative deepening**: tests pathwidth ≤ k for k = lower..upper
4. **Decision procedure**: DFS backtracking building orderings left-to-right, pruning when vertex separation exceeds k
5. **Memoization**: bitmask cache for n ≤ 30; pruning-only for larger graphs
6. **Vertex selection**: prioritizes active suffix vertices (already "open") sorted by remaining neighbor count

The solver (`mosp/solver.py`) calls `compute_pathwidth_fpt()` which automatically delegates to exact DP for n ≤ 25.

## Design Decisions

**Two-tier solver.** Exact DP is faster for small instances (no heuristic/pruning overhead), so the FPT solver delegates to it for n ≤ 25. For larger instances, preprocessing and pruning keep the search tractable when pathwidth is small.

**Verify by simulation, not formula alone.** The solver computes the ordering from pathwidth but determines the actual MOSP value by simulating the production sequence on the original instance. This is necessary because `pathwidth + 1` can exceed the number of customers (the agreement graph encodes pattern relationships but not the customer count bound).

**Agreement graph via matrix multiplication.** `M^T @ M` gives the overlap matrix in one operation — entry (i,j) counts shared customers between patterns i and j. An edge exists wherever this count is positive. Simple and fast via numpy.

**Convention: rows = customers, columns = patterns.** The binary matrix M[i][j] = 1 means customer i requires pattern/product j. This matches the standard MOSP file format.

**Bitmask adjacency.** Both solvers represent graph adjacency as Python ints with bitwise operations, making neighbor queries O(1).

## File Format

Standard MOSP instance files (`.mosp`):
```
instance_name
n_customers n_patterns
<n_customers rows of n_patterns space-separated 0/1 values>
```

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Solve a single instance
python -c "
from mosp.solver import solve_mosp_from_file
sol = solve_mosp_from_file('path/to/instance.mosp')
print(f'Optimal: {sol.max_open_stacks}, Ordering: {sol.ordering}')
"

# Solve from a matrix
python -c "
from mosp.instance import MOSPInstance
from mosp.solver import solve_mosp
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
sol = solve_mosp(instance)
print(f'Optimal: {sol.max_open_stacks}, Ordering: {sol.ordering}')
"

# Generate benchmark instances and run them
python -c "
from benchmarks.generator import generate_benchmark_suite
generate_benchmark_suite('benchmarks/instances', sizes=[(10,10),(15,15)], densities=[0.3])
"
python -m benchmarks.run_benchmarks benchmarks/instances benchmarks/results/output.csv
```

## Known Limitations

- **Exact DP ceiling at n = 25**: The subset DP uses O(2^n) space/time. This is inherent to the algorithm, not a bug.
- **FPT solver depends on pathwidth**: Handles n = 100+ when k ≤ 5, but slows down for moderate pathwidth (k ≥ 10) on large graphs. No proven worst-case polynomial bound for fixed k — the theoretical O(2^{O(k²)} · n) algorithm (Bodlaender-Kloks) is not implemented due to extreme complexity.
- **No heuristic fallback**: For instances beyond both solvers' reach, there is currently no approximate/heuristic mode.

## Future Directions

- Integration with SageMath's pathwidth solvers as a reference oracle
- Heuristic mode for large instances (greedy, local search)
- Import published benchmark instances from Chu & Stuckey, Faggioli & Bentivoglio
- Comparison tables against published optimal values
- Bodlaender-Kloks FPT algorithm for proven worst-case guarantees
