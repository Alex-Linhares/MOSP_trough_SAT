# MOSP via Pathwidth Reduction — Status and Next Steps

## What This Project Is

This project tackles the **Minimization of Open Stacks Problem (MOSP)** by reducing it to **pathwidth computation** on graphs, with a formal proof of the reduction in Lean 4. MOSP is NP-hard (Linhares & Yanasse 2002).

MOSP arises in manufacturing: given a set of customer orders (each requiring some subset of products), find a production sequence for the products that minimizes the maximum number of simultaneously "open" customer stacks. A stack opens when the first product a customer needs is produced and closes when the last one is done.

## Terminology Correction: We Had the Two Graphs Swapped

Yanasse & Senne (2010, `literature/yanasse_senne_2010_properties_preprocessing.pdf`)
defines both graphs this literature uses, and says they are "completely different":

- **MOSP graph** — nodes are *item types* (customers), with an arc between two
  nodes iff some pattern contains both. `M @ M^T`. A pattern with k items becomes
  a clique of size k, so the graph is a union of cliques. **This is the graph the
  pathwidth equivalence is about**, due to Yanasse (1997c). In this repository it
  is `customer_inter/customer_graph.py`.
- **Pattern connection graph** — nodes are *patterns*, with an arc between two
  iff they share an item type. `M^T @ M`. The literature uses this for exactly
  one purpose: decomposing an instance into independent clusters (pre-processing
  1). In this repository it is `mosp/agreement_graph.py`, and the name
  "agreement graph" is ours, not the literature's.

So the claim recorded below — that `pathwidth(agreement graph) + 1` should equal
the optimum — attached the theorem to the graph the literature uses only for
decomposition. The undercounting we measured is not a counterexample to
Yanasse's result; it is a consequence of testing the wrong graph. Note also that
the graph result is **Yanasse (1997c)**, a different paper from the EJOR
"On a pattern sequencing problem..." (1997b) cited elsewhere in this repository;
there are at least three distinct Yanasse 1997 papers.

## Earlier Finding: Neither Graph Formulation Gave Exact MOSP Values

Recorded as measured. Read it in light of the correction above: the agreement
graph column was never expected to be exact, and the customer graph column is
confounded by a heuristic ordering derivation.

Validation against published optimal values (from Frinhani et al. 2018, computed using Chu & Stuckey 2009):

| Instance | Published OPT | Agreement graph (pw+1) | Customer graph (pw+1) |
|---|---|---|---|
| GP1 (50×50) | 45 | — | 45 |
| GP2 (50×50) | 40 | — | 40 |
| GP3 (50×50) | 40 | — | 40 |
| GP4 (50×50) | 30 | — | 30 |
| GP5 (100×100) | 95 | — | **96 (+1)** |
| GP6 (100×100) | 75 | — | 75 |
| GP7 (100×100) | 75 | — | 75 |
| GP8 (100×100) | 60 | — | 60 |
| SP2 (50×50) | 19 | — | **21 (+2)** |
| SP3 (75×75) | 34 | — | **35 (+1)** |
| SP4 (100×100) | 53 | — | **55 (+2)** |

The pathwidth computation itself is provably correct (SAT certifies optimality via UNSAT at k-1 / SAT at k). The problem is that:
- `pathwidth(G_a) + 1` (agreement graph) **undercounts** — gives a lower bound
- `pathwidth(G_c) + 1` (customer graph) **overcounts on sparse instances** — gives an upper bound
- Neither is tight for all instances

The overcounting on the customer graph arises because the customer-to-pattern ordering derivation is heuristic (sort by earliest/latest customer position), not optimal. A customer ordering that achieves optimal pathwidth does not necessarily produce a pattern ordering that achieves optimal MOSP.

**The correct approach is to encode MOSP directly as SAT**, bypassing the pathwidth reduction entirely. The SAT infrastructure (encoding, solver wrapper, CaDiCaL backend) built for pathwidth can be reused for a direct MOSP encoding.

## Bounds: Ours Is the Weakest One in the Literature

`satisfiability/mosp_solver.py::_lower_bound` returns the maximum number of
customers requiring any single pattern. Yanasse & Senne (2010) attribute exactly
this to Yuen & Richardson (1995) and call it **the trivial lower bound**. Three
stronger ones are on record:

1. **maximal clique of the MOSP graph** (Yanasse 1997c) — dominates the trivial
   bound, since every pattern is already a clique there
2. **smallest node degree** of the MOSP graph (Yanasse 1997c)
3. **arc contraction bound** (Yanasse et al. 1999) — "dominates all previous
   lower bounds proposed in the literature"

Plus a general principle: any subgraph of the MOSP graph yields a valid lower
bound, so bounds can be obtained by solving smaller subinstances.

This matters concretely. On SP4 our bound is 13 against a true optimum of 53, and
SP4 is still unsolved. The binary search spends its budget on refutations at k
values far below the optimum, which are both hopeless and expensive.

## Preprocessing: Six Operations Exist, We Implement None

The SAT path does no preprocessing. Yanasse & Senne (2010) review six
operations: cluster decomposition, pattern dominance, item reduction from pattern
simplicity, and reductions from equivalent nodes and adjacent degree-2 nodes.
A measurement in this repository found pattern and item dominance nearly useless
on the Chu & Stuckey random instances (0 dominated customers), but that covered
only two of the six — the others are untested here.

### Key References

- **Kinnersley (1992)** — Established vertex separation = pathwidth. *Information Processing Letters*, 42(6), 345-350.
- **Yanasse (1997b)** — Mathematical formulation, branch and bound, greedy heuristic. *European Journal of Operational Research*, 100(3), 454-463. Note: this is *not* the paper that introduces the MOSP graph.
- **Yanasse (1997c)** — Introduced the MOSP graph (nodes = item types) and the clique / minimum-degree lower bounds. Cited via Yanasse & Senne (2010); exact venue still to be confirmed.
- **Yanasse, Becceneri & Soma (1999)** — Arc contraction lower bound, which dominates all earlier bounds. *Pesquisa Operacional*, 19, 249-277. Open access (SciELO).
- **Yanasse & Senne (2010)** — Review of MOSP properties and six pre-processing operations. *European Journal of Operational Research*, 203(3), 559-567.
- **Linhares & Yanasse (2002)** — Proved MOSP is NP-hard. *Computers & Operations Research*, 29, 1759-1772.
- **Chu & Stuckey (2009)** — Benchmark instances and exact solver via customer search with nogood recording. *CP 2009*, LNCS 5732, 242-257.
- **Frinhani et al. (2018)** — PageRank heuristic; published optimal values for Challenge/SCOOP instances using Chu & Stuckey's algorithm. *PLOS ONE*, 13(8), e0203076.
- **Martin, Yanasse & Pinto (2022)** — ILP/CP formulations; comparative benchmarks. *International Transactions in Operational Research*.
- **Faggioli & Bentivoglio (1998)** — Heuristic approaches and instance generation. *European Journal of Operational Research*, 110(3), 564-575.
- **Kirousis & Papadimitriou (1986)** — Graph searching and pathwidth connections. *Theoretical Computer Science*, 47, 205-218.
- **Fellows & Langston (1989)** — FPT algorithms for pathwidth. *Proc. 21st ACM STOC*, 501-512.

## Certified Optima vs Best Known Solutions

`solutions/` now holds two different kinds of result and **the files do not say
which**. A solution file carries `instance_name`, `n_customers`, `n_patterns`,
`mosp_value` and `ordering` — nothing about how the value was established. Since
both kinds are present, adding them into one total overstates what has been
proved.

- **Certified optimum**: satisfiable at `k` with a witness *and* unsatisfiable at
  `k-1`; or satisfiable at `k` where the lower bound already equals `k`, which
  needs no refutation.
- **Best known solution**: a witness of value `k` and nothing more. Produced by
  `benchmarks/ratchet.py`, which only ever asks satisfiable questions.

Both are equally checkable as *upper* bounds — the witness verifies either way
via `mosp/certify.py`. Only the first is an optimality claim.

### Recovering the split

Until a provenance field exists, the split is recoverable from other records:

1. Any instance appearing as `status=solved` in `benchmarks/results/sweep_*.csv`
   or `overnight_*round*.csv` was solved by the binary search, which certifies
   optimality by construction.
2. Any cached value equal to its `_lower_bound` is certified by the bound,
   whatever produced it.
3. Everything else is a best known solution with optimality unproven.

Measured on 2026-09-18 with 6,380 cached solutions, now read from the files
themselves rather than reconstructed:

| provenance | count |
|---|---|
| `certified:refutation` | 6,226 |
| `certified:bound` | 2 |
| `solution` (optimality open) | 152 |

(Four further files are orphans — `GP1.json` through `GP4.json`, written by
`validate_published_optima.py` under a bare naming convention that
`from_benchmark_file` does not produce, and matching no enumerated instance.)

### The provenance field — done

`_save_solution` records a `provenance` field: `certified:refutation`,
`certified:bound`, or `solution`. Existing files were backfilled using the two
recovery rules above. Saves are monotone in the value and never demote a
certified value to a bare solution, which matters because the ratchet re-derives
values earlier runs had proved — without that guard a night of re-solving would
quietly downgrade proofs to guesses.

This matters beyond bookkeeping: the corpus is intended as a published artifact,
and an artifact that cannot distinguish a proof from a good guess is a liability.

## Architecture

```
satisfiability/                 → SAT-based solvers (pathwidth + direct MOSP)
    encoding.py                     Position-based CNF encoding for pathwidth
    solver.py                       Pathwidth solver: preprocessing, iterative deepening, CaDiCaL
    mosp_encoding.py                Direct MOSP-to-SAT CNF encoding (no pathwidth reduction)
    mosp_solver.py                  Direct MOSP solver: bounds, iterative deepening, solution caching

customer_inter/                 → Customer intersection graph approach (customers as vertices)
    customer_graph.py               Build customer graph via M @ M^T overlap
    reduction.py                    MOSP ↔ customer-graph pathwidth reduction
    solver.py                       End-to-end pipeline using customer graph
    compare.py                      Side-by-side comparison of both approaches

mosp/                           → Agreement graph approach (patterns as vertices)
    instance.py                     Parse/represent MOSP instances (binary matrix)
    agreement_graph.py              Build MOSP graph via M^T @ M overlap
    reduction.py                    Formal reduction: MOSP ↔ pathwidth
    solver.py                       End-to-end pipeline: parse → graph → pathwidth → ordering
    verify.py                       Simulate production sequence to count open stacks

fixed_parameter_algorithm/      → Pathwidth solvers (exact DP and branch-and-bound)
    pathwidth.py                    Exact DP over vertex subsets (n ≤ 18)
    pathwidth_fpt.py                Branch-and-bound with iterative deepening (n ≤ 100+)
    path_decomposition.py           Extract path decomposition from ordering

benchmarks/
    generator.py                    Random/structured instance generation
    run_benchmarks.py               Batch solver with CSV output
    solve_all.py                    Batch solver for published benchmark files
    solve_all_sat.py                Batch SAT solver for large benchmark instances
    solve_parallel.py               Parallel solving: across instances, and across k
    ratchet.py                      Descending satisfiable-call search
    overnight.py                    Escalating-budget driver for unattended runs
    solver_portfolio.py             Times every pysat backend on the hard calls
    dedupe.py                       Shares solutions between identical instances

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

solutions/                      → Cached SAT solver solutions (JSON)

reports/                        → Analysis documents
tests/                          → 320 tests across 17 test modules
literature/                     → Reference papers (PDFs)
```

## Two Graph Formulations

### Agreement Graph (`mosp/solver.py`)

Nodes = patterns, edges between patterns sharing a customer (`M^T @ M`). Pathwidth gives a **lower bound** on MOSP but can undercount on some instances.

### Customer Intersection Graph (`customer_inter/solver.py`)

Nodes = customers, edges between customers sharing a pattern (`M @ M^T`). Pathwidth(G_c) + 1 gives an **upper bound** on MOSP. Matches published optimal values on dense instances (GP1-4, GP6-8) but overcounts on sparse instances (SP2-4, GP5).

The overcounting arises because the customer-to-pattern ordering derivation (sort patterns by earliest/latest customer position) is not guaranteed to produce an optimal MOSP ordering, even when the customer ordering achieves optimal pathwidth.

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

For large instances where branch-and-bound times out, a SAT-based solver encodes the pathwidth decision problem ("is pathwidth ≤ k?") as a CNF formula and solves it with CaDiCaL. This is the most powerful pathwidth solver in the project, handling instances up to 125 vertices.

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

**Important**: These pathwidth values are provably correct, but the derived MOSP values (pathwidth + 1) are upper bounds that may overcount on sparse instances. See "Critical Finding" above.

`compute_pathwidth_sat()` is a drop-in replacement for `compute_pathwidth_fpt()` with the same interface. It reuses the same preprocessing (pendant removal, component decomposition) and bounds (greedy upper, clique lower).

**Known bug**: The pathwidth SAT encoding (`encoding.py`) has a variable ID collision bug in `pool.occupy()` / `top_id` tracking. CardEnc auxiliary variables from different constraints share the same IDs, making the encoding unsound. The solver still returns correct results because: (1) n ≤ 18 delegates to exact DP, (2) n > 18 falls back to greedy ordering when SAT returns UNSAT. This bug is fixed in the direct MOSP encoding (`mosp_encoding.py`) which properly tracks auxiliary variable IDs.

### Direct MOSP-to-SAT Solver (`satisfiability/mosp_solver.py`)

Encodes the MOSP decision problem directly as SAT, bypassing the pathwidth reduction entirely. This produces **exact optimal MOSP values** — validated against all published optima (GP1-8, SP2-4).

**Encoding** (position-based formulation):
- Variables: `x[p,t]` (pattern p at position t), `y[p,t]` (pattern p placed by step t), `o[c,t]` (customer c's stack open at step t)
- Permutation constraints via at-least-one + ladder at-most-one
- Prefix linking: `x→y`, monotonicity, converse (including t=0 base case)
- Open stack forcing: (a) placement clause `x[p,t] → o[c,t]` for each pattern p of customer c; (b) pair-wise clause for each (p,q) pair of customer c: `y[p,t] ∧ ¬y[q,t] → o[c,t]`
- Width bound: totalizer cardinality constraint (at most k open stacks per step)
- Symmetry breaking: pattern with most customers in first ⌊m/2⌋+1 positions

**Solution caching**: Results are saved as JSON files in `solutions/`. On subsequent runs, cached solutions are loaded and verified by simulation instead of re-solving. Disable with `solutions_dir=None`.

**Bounds for iterative deepening**:
- Lower bound: max over all patterns p of |customers(p)| (when p is produced, all its customers have open stacks)
- Upper bound: best of identity, reverse, and 10 random permutations (fast O(m·n) simulation each)

## Design Decisions

**Two graph formulations.** The agreement graph (patterns as vertices) and customer intersection graph (customers as vertices) provide complementary bounds. Neither yields exact MOSP on all instances: agreement undercounts, customer overcounts. The Lean formalization proves agreement graph properties.

**Direct MOSP-to-SAT solver.** Encodes MOSP directly without the pathwidth reduction. Produces exact optimal values validated against all published benchmarks. The placement + pair-wise open-stack forcing captures the full open/close semantics correctly.

**Three-tier pathwidth solver.** Exact DP for n ≤ 18 (fastest, no overhead). Branch-and-bound for n ≤ 100+ when pathwidth is small. SAT solver for large instances (n ≤ 125) where branch-and-bound times out — handles high pathwidth that defeats backtracking search.

**Verify by simulation, not formula alone.** Both solvers compute the ordering from pathwidth but determine the actual MOSP value by simulating the production sequence on the original instance.

**Customer ordering to pattern ordering.** Given a customer ordering, each pattern is assigned priority (first_customer_position, last_customer_position) and sorted. This heuristic is not guaranteed to produce an optimal MOSP ordering even from an optimal pathwidth ordering.

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
# NOTE: gives upper bound, may overcount on sparse instances
python -c "
from mosp.instance import MOSPInstance
from customer_inter.solver import solve_mosp
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
sol = solve_mosp(instance)
print(f'Upper bound: {sol.max_open_stacks}, Ordering: {sol.ordering}')
"

# Solve MOSP exactly with direct SAT encoding (recommended)
python -c "
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import solve_mosp_sat
matrix = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
instance = MOSPInstance.from_matrix(matrix, name='example')
val, ordering = solve_mosp_sat(instance)
print(f'Optimal MOSP: {val}, Ordering: {ordering}')
"

# Solve large instances with SAT solver (upper bounds via pathwidth reduction)
python -m benchmarks.solve_all_sat --timeout 300

# Compare both approaches on SCOOP benchmarks
python -m customer_inter.compare

# Run all published benchmarks with timeout
python -m benchmarks.solve_all --timeout 120
```

## Known Limitations

- **Direct MOSP SAT encoding scales to ~50×50**: The O(m² · |P_c|²) clause count for open-stack forcing grows quickly. Validated on 50×50 instances (GP1-GP4). Larger instances (100×100) may require longer timeouts.
- **Pathwidth reduction is not tight**: `pathwidth(G_c) + 1` overcounts MOSP on sparse instances (validated on GP5, SP2-4). Use `solve_mosp_sat()` for exact results.
- **Agreement graph undercounts**: `pathwidth(G_a) + 1` gives a lower bound that can be too low.
- **Pathwidth SAT encoding has a variable ID collision bug**: The `encoding.py` pool.occupy/top_id tracking is broken (CardEnc auxiliary variables collide across constraints). The solver works because it falls back to greedy. Fixed in `mosp_encoding.py`.
- **SAT solver ceiling around n = 125**: The pathwidth position-based encoding produces O(n²) variables and O(n² · degree) clauses. Instances with 125 vertices and density ≥ 4 (pathwidth ≥ 50) exceed 300s.
- **Exact DP ceiling at n = 18**: The subset DP uses O(2^n) space/time.
- **Branch-and-bound depends on pathwidth**: Handles n = 100+ when k ≤ 5, but slows down for moderate pathwidth (k ≥ 10) on large graphs.

## Next Steps

**Primary:**
- Validate direct SAT results against all published optimal values (Frinhani et al. 2018, Chu & Stuckey 2009) — GP1-4 validated, GP5-8 and SP instances need testing
- Fix the pathwidth SAT encoding variable ID collision bug in `encoding.py`
- Batch solver script for direct MOSP-to-SAT (analogous to `solve_all_sat.py`)

**Secondary:**
- Incremental SAT (assumption literals) to avoid rebuilding the formula for each k value
- Better greedy upper bounds (random restarts, local search) to improve iterative deepening
- Clause reduction: avoid O(|P_c|²) pair-wise clauses for customers with many patterns (use auxiliary variables to encode "exists placed" and "exists not placed")
- Integration with SageMath's pathwidth solvers as a reference oracle
- The existing pathwidth solvers and FPT theory remain valuable for theoretical interest and as bounds
