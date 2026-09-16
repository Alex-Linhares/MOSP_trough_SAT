# MOSP via Pathwidth FPT Reduction

## What This Project Is

This project solves the **Minimization of Open Stacks Problem (MOSP)** optimally by reducing it to **pathwidth computation** on graphs, with a formal proof of correctness in Lean 4. MOSP is NP-hard, but pathwidth is fixed-parameter tractable (FPT) — meaning instances with small pathwidth can be solved efficiently regardless of input size. We exploit this structural property.

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence for the products that minimizes the maximum number of simultaneously "open" customer stacks. A stack opens when the first product a customer needs is produced and closes when the last one is done.

## Theoretical Foundation

The key equivalence chain (Kinnersley 1992, Yanasse 1997):

```
VS(G) = PW(G) = IT(G) = SN(G) - 1 = GML(G) + 1
```

For MOSP specifically, two graph formulations exist:
- **Agreement graph** G_a(M): nodes = patterns, edge iff two patterns share a customer. Built via `M^T @ M`.
- **Customer intersection graph** G_c(M): nodes = customers, edge iff two customers share a pattern. Built via `M @ M^T`.

Empirical testing against published optimal values shows that **MOSP(M) = pathwidth(G_c) + 1** (customer graph) gives correct results, while pathwidth(G_a) + 1 (agreement graph) gives a lower bound that can undercount. Both solvers are provided for comparison.

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
mosp/                           → Agreement graph approach (patterns as vertices)
    instance.py                     Parse/represent MOSP instances (binary matrix)
    agreement_graph.py              Build MOSP graph via M^T @ M overlap
    reduction.py                    Formal reduction: MOSP ↔ pathwidth
    solver.py                       End-to-end pipeline: parse → graph → pathwidth → ordering
    verify.py                       Simulate production sequence to count open stacks

customer_inter/                 → Customer intersection graph approach (customers as vertices)
    customer_graph.py               Build customer graph via M @ M^T overlap
    reduction.py                    MOSP ↔ customer-graph pathwidth reduction
    solver.py                       End-to-end pipeline using customer graph
    compare.py                      Side-by-side comparison of both approaches

fixed_parameter_algorithm/
    pathwidth.py                    Exact DP over vertex subsets (n ≤ 18)
    pathwidth_fpt.py                Branch-and-bound with iterative deepening (n ≤ 100+)
    path_decomposition.py           Extract path decomposition from ordering

satisfiability/                 → SAT-based pathwidth solver (n ≤ 125)
    encoding.py                     Position-based CNF encoding with cardinality constraints
    solver.py                       Solver wrapper: preprocessing, iterative deepening, CaDiCaL

benchmarks/
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output
    solve_all.py                    Batch solver for published benchmark files
    solve_all_sat.py                Batch SAT solver for large benchmark instances

lean/
    MOSPFormalization/              Lean 4 proofs of the MOSP-pathwidth reduction
        LinearLayout.lean               Linear vertex orderings
        VertexSeparation.lean           Vertex separation number
        PathDecomposition.lean          Path decomposition structure
        Pathwidth.lean                  Pathwidth definitions
        LayoutToDecomposition.lean      Layout → decomposition construction
        DecompositionToLayout.lean      Decomposition → layout construction
        VSEquivPW.lean                  VS = PW proof (Kinnersley 1992)
        MOSPInstance.lean               MOSP instance formalization
        OpenStacks.lean                 Open stacks counting
        Reduction.lean                  MOSP ↔ pathwidth reduction proof
        Examples.lean                   Verified example instances
        ForMathlib/                     Candidates for Mathlib contribution

reports/                        → Analysis documents
tests/                          → 85 tests across 7 test modules
literature/                     → Reference papers (PDFs)
```

## Two Graph Formulations

### Agreement Graph (`mosp/solver.py`)

Nodes = patterns, edges between patterns sharing a customer (`M^T @ M`). This was the original approach. Pathwidth gives a lower bound on MOSP but can undercount on some instances.

### Customer Intersection Graph (`customer_inter/solver.py`)

Nodes = customers, edges between customers sharing a pattern (`M @ M^T`). Pathwidth(G_c) + 1 matches published optimal values. The pattern ordering is derived from the customer ordering by assigning each pattern the position of its earliest customer.

Both solvers share the same pathwidth backend. The customer graph often has more nodes (customers > patterns), but SCOOP benchmarks show it solves faster via branch-and-bound due to lower pathwidth.

## Pathwidth Computation

### Exact DP (n ≤ 18)

O(2^n · n²) Held-Karp style subset DP with bitmask adjacency. Guaranteed optimal. Used automatically for small graphs.

### Branch-and-Bound (n ≤ 100+)

For larger graphs with small pathwidth k. The algorithm:
1. **Preprocesses**: removes degree-1 (pendant) vertices iteratively, decomposes into connected components
2. **Bounds**: greedy heuristic upper bound, max-clique lower bound (pathwidth ≥ ω(G) - 1)
3. **Iterative deepening**: tests pathwidth ≤ k for k = lower..upper
4. **Decision procedure**: DFS backtracking building orderings left-to-right, pruning when vertex separation exceeds k
5. **Memoization**: bitmask cache for n ≤ 30; pruning-only for larger graphs
6. **Vertex selection**: prioritizes active suffix vertices (already "open") sorted by remaining neighbor count

Note: despite the filename `pathwidth_fpt.py`, this is not a true FPT algorithm. It is branch-and-bound that works well when pathwidth is small, but has no proven f(k) · poly(n) guarantee. The theoretical FPT algorithm (Bodlaender-Kloks, 2^(32k³) · n) has constants too large for practical use. See `reports/fpt_theory_practice_gap.md`.

`compute_pathwidth_fpt()` delegates to exact DP for n ≤ 18. The threshold was lowered from 25 to 18 because branch-and-bound is faster than DP for n=19-25 when pathwidth is small (test suite: 114s → 5s).

### SAT Solver (n ≤ 125)

For large instances where branch-and-bound times out, a SAT-based solver encodes the pathwidth decision problem ("is pathwidth ≤ k?") as a CNF formula and solves it with CaDiCaL. This is the most powerful solver in the project, handling instances up to 125 vertices.

**Encoding** (position-based formulation):
- Variables: `x[v,t]` (vertex v at position t), `y[v,t]` (vertex v placed by step t), `s[v,t]` (vertex v separated at step t)
- Permutation constraints via at-least-one + ladder at-most-one
- Prefix linking: `x→y`, monotonicity, converse
- Separation: if a neighbor is placed but v is not, v is separated
- Width bound: totalizer cardinality constraint (at most k separated per step)
- Symmetry breaking: fix vertex 0 at position 0

**Performance** (with 300s timeout, customer intersection graph):
- 40×40: 100% solved, avg 5s
- 50×50: 100% solved, avg 8s
- 75×75: 100% solved, avg 37s
- 100×100: 92% solved, avg 140s (2 of 25 Chu & Stuckey timeout)
- 100×50: 100% solved, avg 84s
- 50×100: 100% solved, avg 11s
- 125×125: 28% solved (only density-2 and 2 density-4; density ≥ 4 mostly timeout)
- **Overall: 200 of 220 instances solved that were previously out of reach for the branch-and-bound solver (91%)**

`compute_pathwidth_sat()` is a drop-in replacement for `compute_pathwidth_fpt()` with the same interface. It reuses the same preprocessing (pendant removal, component decomposition) and bounds (greedy upper, clique lower).

## Design Decisions

**Two graph formulations.** The agreement graph (patterns as vertices) and customer intersection graph (customers as vertices) provide complementary approaches. The customer graph matches published optimal values; the agreement graph is retained for comparison and because the Lean formalization proves its properties.

**Three-tier pathwidth solver.** Exact DP for n ≤ 18 (fastest, no overhead). Branch-and-bound for n ≤ 100+ when pathwidth is small. SAT solver for large instances (n ≤ 125) where branch-and-bound times out — handles high pathwidth that defeats backtracking search.

**Verify by simulation, not formula alone.** Both solvers compute the ordering from pathwidth but determine the actual MOSP value by simulating the production sequence on the original instance.

**Customer ordering to pattern ordering.** Given a customer ordering, each pattern is assigned priority (first_customer_position, last_customer_position) and sorted. This produces the pattern sequence that processes patterns as their earliest customer arrives.

**Convention: rows = customers, columns = patterns.** The binary matrix M[i][j] = 1 means customer i requires pattern/product j. This matches the standard MOSP file format.

**Bitmask adjacency.** Both pathwidth solvers represent graph adjacency as Python ints with bitwise operations, making neighbor queries O(1).

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

# Solve via customer intersection graph + branch-and-bound (small/medium instances)
python -c "
from mosp.instance import MOSPInstance
from customer_inter.solver import solve_mosp
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
sol = solve_mosp(instance)
print(f'Optimal: {sol.max_open_stacks}, Ordering: {sol.ordering}')
"

# Solve large instances with SAT solver (recommended for n > 30)
python -m benchmarks.solve_all_sat --timeout 300

# Compare both approaches on SCOOP benchmarks
python -m customer_inter.compare

# Run all published benchmarks with timeout
python -m benchmarks.solve_all --timeout 120
```

## Known Limitations

- **Exact DP ceiling at n = 18**: The subset DP uses O(2^n) space/time. This is inherent to the algorithm, not a bug.
- **Branch-and-bound depends on pathwidth**: Handles n = 100+ when k ≤ 5, but slows down for moderate pathwidth (k ≥ 10) on large graphs. Not a true FPT algorithm — no proven f(k) · poly(n) guarantee.
- **SAT solver ceiling around n = 125**: The position-based encoding produces O(n²) variables and O(n² · degree) clauses. Instances with 125 vertices and density ≥ 4 (pathwidth ≥ 50) exceed 300s. The 20 remaining unsolved benchmark instances are all 125×125 Chu & Stuckey with density 4-10.
- **No heuristic fallback**: For instances beyond all three solvers' reach, there is currently no approximate/heuristic mode.

## Future Directions

- Incremental SAT (assumption literals) to avoid rebuilding the formula for each k value
- Better greedy upper bounds (random restarts, local search) to improve both branch-and-bound and SAT iterative deepening
- Integration with SageMath's pathwidth solvers as a reference oracle
- Comparison tables against published optimal values across all datasets
- Populate `KNOWN_OPTIMA` in compare.py with published results from Chu & Stuckey
- Solve the remaining 20 instances (125×125 density ≥ 4) with longer timeouts or ILP encoding
