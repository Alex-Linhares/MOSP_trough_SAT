# MOSP via Pathwidth FPT Reduction

## What This Project Is

This project solves the **Minimization of Open Stacks Problem (MOSP)** optimally by reducing it to **pathwidth computation** on graphs. MOSP is NP-hard, but pathwidth is fixed-parameter tractable (FPT) — meaning instances with small pathwidth can be solved efficiently regardless of input size. We exploit this structural property.

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

- **Kinnersley (1992)** — Established vertex separation = pathwidth
- **Yanasse (1997)** — Formulated MOSP in terms of the agreement graph
- **Linhares & Yanasse (2002)** — Proved MOSP is NP-hard
- **Chu & Stuckey (2009)** — Benchmark instances and constraint-based approaches
- **Faggioli & Bentivoglio (1998)** — Heuristic approaches and instance generation
- **Kirousis & Papadimitriou** — Graph searching and pathwidth connections
- **Fellows & Langston** — FPT algorithms for pathwidth

## Architecture

```
mosp/instance.py          → Parse/represent MOSP instances (binary matrix)
mosp/agreement_graph.py   → Build MOSP graph via M^T @ M overlap
mosp/reduction.py         → Formal reduction: MOSP ↔ pathwidth
mosp/solver.py            → End-to-end pipeline: parse → graph → pathwidth → ordering
mosp/verify.py            → Simulate production sequence to count open stacks

fixed_parameter_algorithm/pathwidth.py           → Exact DP over vertex subsets
fixed_parameter_algorithm/path_decomposition.py  → Extract path decomposition from ordering

benchmarks/generator.py       → Random/structured instance generation
benchmarks/run_benchmarks.py  → Batch solver with CSV output
```

## Design Decisions

**Exact DP over vertex subsets (Held-Karp style).** We chose O(2^n · n²) subset DP with bitmask adjacency representation. This is the simplest correct exact algorithm and handles up to ~25 patterns (vertices in the agreement graph). The bitmask representation makes neighbor queries O(1) via bitwise AND.

**Verify by simulation, not formula alone.** The solver computes the ordering from pathwidth but determines the actual MOSP value by simulating the production sequence on the original instance. This is necessary because `pathwidth + 1` can exceed the number of customers (the agreement graph encodes pattern relationships but not the customer count bound).

**Agreement graph via matrix multiplication.** `M^T @ M` gives the overlap matrix in one operation — entry (i,j) counts shared customers between patterns i and j. An edge exists wherever this count is positive. Simple and fast via numpy.

**Convention: rows = customers, columns = patterns.** The binary matrix M[i][j] = 1 means customer i requires pattern/product j. This matches the standard MOSP file format.

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

# Generate benchmark instances and run them
python -c "
from benchmarks.generator import generate_benchmark_suite
generate_benchmark_suite('benchmarks/instances', sizes=[(10,10),(15,15)], densities=[0.3])
"
python -m benchmarks.run_benchmarks benchmarks/instances benchmarks/results/output.csv
```

## Known Limitations

- **25-vertex ceiling**: The exact subset DP uses O(2^n) space/time, limiting us to ~25 patterns. This is inherent to the algorithm, not a bug.
- **No FPT algorithm yet**: An O(2^O(k²) · n) algorithm parameterized by pathwidth k would handle larger graphs when pathwidth is small. This is significantly more complex to implement and is a stretch goal.
- **No heuristic fallback**: For instances beyond the exact solver's reach, there is currently no approximate/heuristic mode.

## Future Directions

- FPT pathwidth algorithm parameterized by k (for large graphs with small pathwidth)
- Integration with SageMath's pathwidth solvers as a reference oracle
- Heuristic mode for large instances (greedy, local search)
- Import published benchmark instances from Chu & Stuckey, Faggioli & Bentivoglio
- Comparison tables against published optimal values
