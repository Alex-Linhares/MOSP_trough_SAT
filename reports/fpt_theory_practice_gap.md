# The Pathwidth FPT Gap: Why Theoretical Tractability Fails in Practice

## 1. What FPT Promises

A problem is *fixed-parameter tractable* (FPT) in parameter k if it can be
solved in time f(k) * n^O(1), where n is the input size and f is some
computable function depending only on k. The key selling point: for fixed k,
the running time is *polynomial in n*. As k grows, f(k) may explode, but if
your instances have small k, FPT says you should be fine regardless of n.

Pathwidth is FPT in itself: given a graph G, we can decide whether
pathwidth(G) <= k in time f(k) * n for some function f. This is the
celebrated result of Bodlaender (1996), building on Bodlaender & Kloks (1996)
and the Robertson-Seymour graph minor machinery.

The question is: what is f(k)?

## 2. The Constants Are Catastrophic

### Bodlaender-Kloks (1996): 2^(32 * k^3) * n

The original algorithm for computing pathwidth exactly runs in time
2^(c * k^3) * n where c ~ 32 (as noted by Furer 2016). For concrete
pathwidth values encountered in our MOSP instances:

| k  | 2^(32 * k^3)         | Comparison                          |
|----|----------------------|-------------------------------------|
| 2  | 2^256                | More than atoms in the universe     |
| 3  | 2^864                | Incomprehensibly large              |
| 4  | 2^2048               | Larger than RSA-2048 key space      |
| 5  | 2^4000               | Completely absurd                   |
| 10 | 2^32000              | Theoretical fiction                 |

Our SCOOP benchmark instances have pathwidths of 3-9. Even k=2 requires
2^256 operations -- a number that exceeds the estimated number of atoms in
the observable universe (~2^266). The algorithm is "efficient" only in the
asymptotic sense that n appears linearly.

### Furer (2016): 2^O(k^2) * n

Furer improved the exponent from k^3 to k^2. This is a genuine theoretical
advance, but the practical impact is nil:

| k  | 2^(c * k^2), c=10    | Still feasible?                     |
|----|----------------------|-------------------------------------|
| 2  | 2^40                 | ~10^12, borderline feasible         |
| 3  | 2^90                 | ~10^27, no                          |
| 5  | 2^250                | No                                  |
| 10 | 2^1000               | No                                  |

Even with an optimistic constant c=10, only k=2 becomes remotely tractable.
The constant c in Furer's algorithm is not explicitly stated but inherits
complexity from the Bodlaender-Kloks framework.

### Why So Large?

The algorithms rely on a cascade of deep structural results:

1. **Robertson-Seymour Graph Minor Theory.** The FPT algorithm for treewidth
   (and hence pathwidth) ultimately depends on the Graph Minor Theorem, which
   guarantees that every minor-closed family has a finite obstruction set. The
   proof is *non-constructive*: it shows the obstruction set exists without
   telling you what it is. Fellows & Langston (1989) proved that computing
   the obstruction set is *undecidable in general* -- there is no algorithm
   that, given a description of a minor-closed class, outputs its obstruction
   set.

2. **Bounded-Width Structure Theorems.** The algorithm processes the graph by
   finding separators, building partial decompositions, and extending them.
   Each step involves case analysis over the structure of bags in the
   decomposition, leading to a number of cases exponential in the bag size
   (which is k+1). The case analysis compounds across levels.

3. **Typical Structure Enumeration.** The algorithm enumerates "typical
   sequences" of width-k path decompositions. The number of distinct typical
   sequences is bounded by a function of k alone, but that function involves
   iterated exponentials.

The Bodlaender-Kloks algorithm is what's called a **galactic algorithm**
(a term coined by Lipton and Regan): an algorithm with provably optimal
asymptotic complexity that will never be used on any dataset that exists on
Earth, because the constant factors are so enormous that the crossover point
where it outperforms naive methods lies beyond any practical input size.

## 3. What Actually Works: Branch-and-Bound

Every practical pathwidth solver -- our code, SageMath, and every
implementation described in experimental papers -- uses branch-and-bound:

```
for k = lower_bound to upper_bound:
    if DFS_backtracking_finds_ordering_with_vertex_separation <= k:
        return k, ordering
```

This approach has:

- **No FPT guarantee.** Worst case is still exponential in n, not just k.
  The search tree has n! leaves (all orderings), and pruning may not help
  for adversarial instances.

- **Excellent practical performance when k is small.** When we test "is
  pathwidth <= k?" with small k, the pruning is aggressive: any partial
  ordering whose vertex separation exceeds k is immediately abandoned.
  For our 27-node SCOOP instance with pw=5, this solved in <0.1 seconds
  because most of the n! search space is pruned away.

- **Unpredictable failure modes.** The same algorithm that solves a 31-node
  graph with pw=5 in 0.0s times out on a 31-node graph with pw=6 after 120s,
  because one extra unit of pathwidth can exponentially increase the fraction
  of the search tree that survives pruning.

The irony: branch-and-bound exploits the *same structural property* as the
FPT algorithm (small pathwidth means aggressive pruning), but it does so
through simple backtracking rather than the elaborate graph minor machinery.
It gives up the theoretical guarantee in exchange for practical speed.

## 4. The Upper Bound Bottleneck

Our branch-and-bound uses iterative deepening: try k = lower, lower+1, ...,
upper. The upper bound comes from a greedy heuristic. This creates two
distinct ways a tighter upper bound helps:

### 4a. Fewer Iterations

If the true pathwidth is k* and our bounds are [lower, upper], we run the
decision procedure (upper - lower + 1) times. Each failing test (k < k*)
potentially explores a large portion of the search tree before concluding
infeasibility. A tighter upper bound eliminates wasted iterations at the
top.

But this is usually not the bottleneck. The expensive iteration is the
*successful* one at k = k*, and the failing iterations at k = k*-1, k*-2
are typically fast because the tight bound causes early pruning.

### 4b. Better Pruning at the Critical Level

More importantly: when we test "pathwidth <= k?" with a smaller k, the
pruning is *more aggressive*. Every vertex placement that would create
vertex separation > k is rejected. A smaller k means fewer surviving
branches at each node of the search tree.

Consider our failing cases:

| Instance         | n   | pw   | Status    | Issue                           |
|------------------|-----|------|-----------|---------------------------------|
| d_6              | 31  | >=4  | TIMEOUT   | FPT iterating through k values  |
| B_12F18_11       | 21  | 5    | 170s (DP) | DP is 2^21, slow but feasible   |
| B_GTM18A_139     | 24  | >=4  | TIMEOUT   | DP is 2^24, too slow            |
| FA+AA instances  | 68+ | ?    | TIMEOUT   | Way too large for either method |

For `d_6` (31 nodes), the FPT solver's greedy heuristic likely gives an
upper bound of 8-10. The solver then tests k=3, k=4, k=5, ... and at each
level where k < pw*, the search explores a massive tree before proving
infeasibility. If we knew upfront that pw >= 6, we'd skip those wasted
iterations.

### 4c. Approximation Algorithms as Upper Bounds

The state of the art for pathwidth approximation:

| Algorithm                          | Ratio                   | Time         |
|------------------------------------|-------------------------|--------------|
| Greedy (our current heuristic)     | No guarantee            | O(n^2)       |
| Bodlaender et al. (2016)           | O(k * sqrt(log k))      | 2^O(k) * n  |
| Feige-Hajiaghayi-Lee (2008)        | O(sqrt(log pw) * log n) | Polynomial   |
| Groenland-Joret-Nadara-Walczak     | O(tw * sqrt(log tw))    | Polynomial   |

The Bodlaender et al. 5-approximation for treewidth (which lower-bounds
pathwidth) runs in 2^O(k) * n time. Since pw >= tw, a treewidth
approximation gives pw <= 5*tw + 4. For tw=4, this gives pw <= 24 -- not
tight enough to help much.

The polynomial-time algorithms have logarithmic approximation ratios that
could give useful upper bounds for moderate-sized instances. If we could
determine that pw <= 6 for a 60-node graph in polynomial time, the
branch-and-bound would only need to test k=3,4,5,6 instead of k=3,...,15.

### 4d. What Would Actually Help

The instances that defeat our solver fall into three categories:

**Category 1: Moderate n (25-35), moderate pw (5-8).**
Examples: d_6 (31 nodes), B_GTM18A_139 (24 nodes, stuck in DP).
A tighter upper bound would directly help here. If we knew pw <= 6, the
pruning at k=6 would be tight enough to solve quickly. The problem is that
our greedy heuristic may return pw_upper = 10, forcing us to waste time on
k=7,8,9 before reaching the answer at k=6.

**Category 2: Large n (50-134), unknown pw.**
Examples: FA+AA instances (68-134 customers).
Even with a perfect upper bound, branch-and-bound on 100+ nodes is likely
hopeless unless the pathwidth is very small (k <= 3-4). The branching factor
at each step is too high. These instances would need fundamentally different
algorithms: SAT/ILP encodings, or the Bodlaender-Kloks algorithm if the
constants were practical.

**Category 3: DP range (n <= 25) but too slow.**
Examples: B_GTM18A_139 (24 nodes), B_12F18_11 (21 nodes).
These fall in the n <= 25 DP range but 2^24 = 16M subsets is too much.
The fix here isn't a better upper bound -- it's lowering the DP/FPT
threshold so that FPT branch-and-bound handles these instead. If B_GTM18A
has pw=4, FPT would solve it in seconds, but the code forces it into the
2^24 exact DP.

## 5. Concrete Recommendations

### Immediate: Lower the DP Threshold

Change the threshold in `compute_pathwidth_fpt` from n <= 25 to something
like n <= 18. For n=18, exact DP processes 2^18 = 262K subsets (fast). For
n=19-25, FPT branch-and-bound with pruning will be much faster than DP when
pathwidth is small. Our benchmarks show FPT solves n=27-31 in <1s when pw=5,
so it should handle n=19-25 easily.

This alone would fix B_GTM18A_139 (24 nodes) and B_12F18_11 (21 nodes),
which currently waste minutes in the DP when FPT would take milliseconds.

### Medium-term: Better Greedy Heuristic

The current greedy heuristic (`_greedy_ordering`) builds an ordering by
choosing at each step the vertex that minimizes vertex separation. This is
a single pass with no backtracking. Better heuristics:

- **Multiple random restarts.** Run the greedy heuristic 100 times with
  randomized tie-breaking, keep the best.
- **Local search.** Start from the greedy ordering, improve by swapping
  adjacent vertices.
- **Min-degree elimination.** Build the ordering by repeatedly removing
  the minimum-degree vertex from the remaining graph. This is the standard
  heuristic for treewidth and often gives good pathwidth bounds too.

A tighter upper bound from better heuristics directly translates to faster
iterative deepening: fewer k values to test, and tighter pruning at each
level.

### Longer-term: SAT/ILP Encoding

For Category 2 instances (n=50-134), neither DP nor branch-and-bound will
work. The state of the art for exact pathwidth on graphs of this size uses
Integer Linear Programming (ILP) or SAT encoding. Kammer & Trinks (2016)
describe an ILP formulation (IPPW) that outperforms SageMath's
branch-and-bound on instances with n up to ~80. This would require
integrating an ILP solver (e.g., Gurobi, CPLEX, or the open-source HiGHS).

## 6. Summary

The FPT classification of pathwidth is a *structural insight*, not a
*practical algorithm*. It tells us:

1. Pathwidth is not inherently harder for sparse, tree-like graphs than for
   arbitrary graphs (unlike, say, clique which is W[1]-hard).
2. The problem's difficulty is controlled by the parameter k, not the input
   size n.
3. There exist algorithms whose running time separates the contributions of
   k and n.

But the specific algorithms that achieve the FPT bound use constants so
large (2^(32k^3) for Bodlaender-Kloks) that they are galactic -- they will
never outperform brute force on any instance that fits in the observable
universe. The practical approach is branch-and-bound, which implicitly
exploits the same structure (small k = aggressive pruning) without the
theoretical guarantee.

The most impactful improvement for our solver is not implementing the FPT
algorithm -- it's lowering the DP/FPT threshold and improving the greedy
upper bound, so that branch-and-bound can exploit its pruning advantage on
the instances where it already works well.

## References

- Bodlaender, H.L. (1996). A linear-time algorithm for finding
  tree-decompositions of small treewidth. *SIAM J. Computing*, 25(6).
- Bodlaender, H.L. & Kloks, T. (1996). Efficient and constructive
  algorithms for the pathwidth and treewidth of graphs. *J. Algorithms*,
  21, 358-402.
- Furer, M. (2016). Faster computation of path-width. *SWAT 2016*, LNCS
  9644, 30:1-30:13. https://arxiv.org/abs/1606.06566
- Bodlaender, H.L. et al. (2016). A c^k n 5-approximation algorithm for
  treewidth. *SIAM J. Computing*, 45(2), 317-378.
- Bodlaender, H.L. (2024). Approximation algorithms for treewidth,
  pathwidth, and treedepth -- a short survey. *WG 2024*.
- Kammer, F. & Trinks, M. (2016). Integer linear programming formulation
  and exact algorithm for computing pathwidth. *ISCO 2016*, LNCS 9849.
- Lipton, R. & Regan, K. Galactic algorithms.
  https://en.wikipedia.org/wiki/Galactic_algorithm
