# Plan: from `customer_search.py` to a graph pathwidth solver

*Transferred on 2026-09-30 from `~/dev/pathwidth` into `pathwidth_solver/` of the MOSP repository; see `TRANSFER.md`.
`~/dev/MOSP/...` below is this repository; `src/`, `bench/` and the solver's own tests are under `pathwidth_solver/`.*

Written 2026-09-27. Source: `src/customer_search.py`, a verbatim copy of
`~/dev/MOSP/satisfiability/customer_search.py` (Chu & Stuckey 2009 customer search,
Python reference implementation). Target: a Python package that takes a
`networkx.Graph` and returns its exact pathwidth with an optimal layout.

## 0. Why the port is small

The search already runs on the customer graph alone. Its only inputs are the
self-inclusive neighbourhood bitmasks `masks[c] = N[c]` and `k`; products enter
nowhere else (Chu & Stuckey §2: "the products are essentially irrelevant").

Mapping, with `U = S ∪ {c}` the vertices closed after the move and
`d(U) = |N(U) \ U|` the vertex-separation boundary of the prefix `U`:

| customer search                                   | pathwidth                                          |
|---------------------------------------------------|----------------------------------------------------|
| customer                                          | vertex                                             |
| closing order `S`                                 | layout prefix `U` (reversed layout is a vs layout) |
| `O(S) = ∪ N[c]`                                   | `N[U]`                                             |
| cost `|O(S ∪ {c}) − S|`                           | `d(U) + 1`                                         |
| `MOSP ≤ k`                                        | `vs(G) = pw(G) ≤ k − 1`                            |
| free move (`N[c] ⊆ O(S)`)                         | fullset rule, Kitsunai et al. 2016 Prop. 3         |
| definite move (Thm 1)                             | depth-1 commitment (Tamaki 2011 Commitment Lemma)  |
| memo `prob[S]` / old move                         | subset DP state / Coudert et al. prefix table      |

So `decide_pathwidth(G, w)` is `decide(masks(G), k = w + 1)`, unchanged inside.
The optimum is `pw(G) = MOSP(customer graph) − 1`, proved in
`~/dev/MOSP/lean/MOSPFormalization/MOSPGraph.lean`.

What does *not* carry over: everything that touches products —
`MOSPInstance`, `customer_patterns`, `product_order_from_customers`,
`max_open_stacks`, `_closing_order`, the MOSP upper-bound strategies in
`satisfiability.heuristics`, and `sparse_enough_for_better_move` (uses
`matrix.sum()`). On a graph the closing-order cost *is* the vertex separation,
so the re-simulation step in `solve()` (which exists because the MOSP cost
over-charges unrealisable orders) becomes a plain `vertex_separation(G, layout)`
check with no possible disagreement.

## 1. Layout of the new package

```
pathwidth/                 (this repo)
  pyproject.toml           deps: networkx, numpy, pytest  (matches ~/dev/MOSP/requirements.txt)
  src/customer_search.py   pristine copy, never edited (reference for diffing)
  pathwidth/
    __init__.py            compute_pathwidth(G) -> (width, layout); decide(G, w) -> Decision
    graph.py               masks_from_graph, vertex_separation, layout helpers, readers
    search.py              decide() ported from customer_search.decide
    bounds.py              upper/lower bounds
    solve.py               descent ported from customer_search.solve
    preprocess.py          components, pendants, twins (phase 5)
    native/                C port (phase 6)
  tests/
  bench/
```

Libraries: `networkx` for graphs, generators, readers (`read_edgelist`,
`read_graph6`), max clique (`nx.max_weight_clique` / `nx.find_cliques`),
components, degeneracy (`nx.core_number`); `numpy` only for adjacency matrices
if needed; `pytest` with parametrised exhaustive tests as in `~/dev/MOSP/tests`.
Add a tiny reader for PACE `.gr` and DIMACS `.col` (TreewidthLIB, Rome, VSPLIB
come in those or edge-list forms).

## 2. Phases

### Phase 1 — graph adapter (`graph.py`) — DONE 2026-09-27
- `masks_from_graph(G) -> (masks, labels)`: relabel to `0..n-1`, `masks[v]` =
  closed neighbourhood as Python int; ignore self-loops; reject multigraphs.
- `vertex_separation(G, order) -> int`: `max_i d(V_{≤i})` (bitmask sweep, like
  `_cs_cost` in `satisfiability/heuristics.py` minus one).
- `closing_order_to_layout(order)` (identity/reverse; document the convention).
- Property test: `_cs_cost(masks, order) == vertex_separation(G, order) + 1`.

### Phase 2 — port `decide()` (`search.py`) — DONE 2026-09-27
- Signature `decide(masks, k, *, ...)` with the same flags (`restrict`,
  `subset_rule`, `definite_move`, `old_move`, `memo`, `max_nodes`, `deadline`,
  `memo_limit`, `branch`, `expansion_prune`, `fan_order`). Drop `native`
  until phase 6. Drop `active`/`customer_patterns`: every vertex is active
  (an isolated vertex costs 1 = d+1 with d=0).
- `sparse_enough_for_better_move` → average degree threshold; re-measure
  (`BETTER_MOVE_DENSITY` was products/customer, not degree).
- Copy `_neighbour_masks`, `FAN_ORDERS`, `fan_sort_key` from
  `satisfiability/heuristics.py` into `graph.py`/`search.py`.
- Keep the Python rule "old_move and memo not combined" and its comment.
- **Regression oracle:** on the 2005 challenge instances
  (`~/dev/MOSP/benchmarks/instances/ChallengeInstances2005`), build the
  customer graph with `customer_inter.customer_graph.build_customer_graph`,
  run both searches with identical flags and `k`, and assert identical
  `Decision.status`, `order` and **`nodes`**. Same masks ⇒ same trace, so node
  counts must match exactly. This is the test that proves the port is faithful.

### Phase 3 — bounds and descent (`bounds.py`, `solve.py`) — DONE 2026-09-27
- Upper bounds (replace `satisfiability.heuristics.upper_bound`): reuse
  `_greedy_upper_bound` / `_greedy_ordering` from
  `~/dev/MOSP/fixed_parameter_algorithm/pathwidth_fpt.py` (min-boundary greedy,
  = Coudert et al.'s greedy step), plus a port of `restricted_dfs`
  (`cs-dfs`) which needs only masks.
- Lower bounds: max clique − 1 (`_clique_lower_bound` in `pathwidth_fpt.py`),
  degeneracy (`nx.core_number`), contraction degeneracy
  (`_contraction_degeneracy` in `satisfiability/mosp_solver.py`, = LB5 of
  Yanasse–Becceneri–Soma 1999); all shifted by −1 for pathwidth.
- `solve(G, *, upper, lower, budgets, on_improve)`: same descent as
  `customer_search.solve`, but the witness check is
  `vertex_separation(G, order)` and `proof` semantics are kept
  (`refutation` / `bound` / `""`).
- `compute_pathwidth(G)`: components solved independently, `pw = max`.

### Phase 4 — tests
- Exhaustive: all graphs on ≤ 7 vertices (`nx.graph_atlas_g()`) against a
  brute-force `min over permutations of vertex_separation`.
- Cross-check against `fixed_parameter_algorithm.compute_pathwidth` (subset
  DP, n ≤ 18) on random `nx.gnp_random_graph` instances.
- Known values: `path_graph` 1, `cycle_graph` 2, `complete_graph(n)` n−1,
  `grid_2d_graph(n,n)` n, `petersen_graph` 5, `mycielski_graph(5)` 10,
  `mycielski_graph(6)` 20 (Coudert et al. Table 1), Lodha et al. Table 1 named
  graphs (Grötzsch 5, Chvátal 6, Clebsch 9, Hoffman 7, Pappus 7, Desargues 6).
- Flag-by-flag soundness as in `tests/test_theorem2.py`, `tests/test_fan_order.py`:
  every flag combination gives the same width; node counts recorded as a
  regression table like `tests/test_node_counts.py`.
- The phase-2 node-count identity test against the MOSP solver.

### Phase 5 — preprocessing (`preprocess.py`)
From Coudert et al. 2016 §2.2 and `pathwidth_fpt._preprocess`: connected
components; pendant/degree-1 removal with reinsertion (`_reinsert_pendants`);
twin merging; the arc-contraction rules. Each rule gets a brute-force test.
The Yanasse–Senne 2010 rules in `~/dev/MOSP/mosp/preprocess.py` are the same
rules in MOSP language; check which are already covered.

### Phase 6 — native C — DONE 2026-09-27 (pulled forward; benchmarks need it)
`~/dev/MOSP/satisfiability/customer_search.c` + `native.py` (ctypes, `__int128`
sets, ≤128 vertices). Check what `native.py` passes in; if it is already masks,
the wrapper just changes its argument builder. Keep the Python as reference,
as the MOSP repo does. Later: 256-bit sets or `n`-word bitsets to pass 128.

### Phase 7 — beyond Chu & Stuckey (from the literature review)
In order of expected value:
1. **Lower bound by certified minors** (Tamaki 2022 `Lift`): search
   contractions of `G` for a small minor whose exact pathwidth (this solver)
   is high; replaces the heuristic relaxation of Chu & Stuckey §3.5 and
   attacks the optimality-proof bottleneck.
2. **Component push** (Kitsunai et al. Lemma 2): if a connected component `C`
   of `G − N[U]` has `|C| ≤ k + 1 − |open|`, close all of `C` at once.
3. **Separator-based commitment extraction** (Kitsunai Cor. 2, O(km) min
   s–t separator) — general-depth commitments; SEA 2014 suggests small gain.
4. Vertex relabelling / tie-breaking experiments (Coudert et al. §5).

## Status log
- 2026-09-27: Phases 1–2 implemented (`pathwidth/graph.py`, `pathwidth/search.py`,
  `pathwidth/__init__.py` with a placeholder ascending `compute_pathwidth`). Tests in
  `tests/test_graph.py`, `tests/test_search.py`, `tests/test_identity_mosp.py`: brute-force agreement
  on every graph with ≤ 6 vertices, known pathwidths, all flag combinations agree, and the node-count
  identity against the MOSP Python reference on 2005 challenge customer graphs (five sources, 8–26
  customers, k = ub−1..ub−4, seven flag sets).
- 2026-09-27: Phase 6 done. `pathwidth/customer_search.c` is a verbatim copy of the MOSP C;
  `pathwidth/native.py` is the masks-based ctypes wrapper; `decide(..., native=True)` is the default
  and falls back to Python above 128 vertices or for `branch`/`expansion_prune`. `tests/test_native.py`
  (C = Python node-for-node under seven flag sets; better_move sound; atlas brute force) and a C-to-C
  identity against MOSP's `decide_native`. 81 tests pass. First numbers (C, default flags): M6 pw≤19
  refuted in 685k nodes / 0.4 s (Coudert et al.: 496k nodes / 0.77 s); grid 9×9 refuted in 24k nodes;
  queen8×8 pw 45 confirmed in 289 nodes; M7 pw≤37 *not* refuted within 20M nodes / 9.7 s (Coudert et al.
  needed 10–14 min and 10M stored prefixes).
- 2026-09-27: Phase 3 done. `pathwidth/bounds.py` (greedy order; degeneracy; contraction degeneracy
  MMD+ least-c), `pathwidth/solve.py` (`solve_masks` descent ported from the reference `solve()`,
  witness re-measured by vertex separation, start = greedy + restricted-search descent, stop at the
  lower bound with proof "bound"; `solve(G)` per connected component). `compute_pathwidth` is now the
  real thing and raises on an exhausted budget. C port renamed `closing_search.c` / `_closing_search.so`
  (code untouched). `tests/test_solve.py`: bounds bracket brute force on 120 random graphs, proofs
  labelled, components, budgets, callbacks. 90 tests pass. Next: the Table 3–5 benchmark run (`bench/`).

## 3. Benchmarks (`bench/`) — first sweep run 2026-09-27
`bench/readers.py` (dgf / gr / graphml / VSPLIB), `bench/run.py` (parallel, CSV per set, `--names` filter),
`bench/summary.py` (vs `bench/reference.py` = Coudert et al. Table 4 / §4.6 / §4.4). Instances in
`bench/instances/`: TreewidthLIB `coloring.zip` (58 non-pp graphs; the TSP/Bayesian-net part of TreewidthLIB
is no longer online), freetdi named graphs (150), VSPLIB 2012 (grids/trees/hb), Rome (11,534). Results in
`bench/results/*.csv`. Findings, default flags, C engine ≤ 128 vertices:
- coloring, 600 s: all 14 Table-4 graphs we hold match Coudert et al.'s pathwidth; faster on most (david 0.5 s
  vs 99 s, miles750 0.08 s vs 51 s, queen10_10 3.5 s vs 26 s, games120 118 s vs 148 s). Also proved
  queen11_11 = 87. Only C-engine miss: myciel6 (n=95, pw 38; they needed 10–14 min + 10M prefixes; we did
  not close pw ≤ 37 in 600 s, nor in 25 min with better_move, 1.7G nodes). All other 30 misses have n > 128.
- named, 120 s: 124/150 proved. 16 misses within 128 vertices (cages, polar graphs: lb far below ub).
- VSPLIB, 600 s: hb 26/73 proved (= their 26); grids sides 5–11 proved (they: ≤ 13; 12×12 = 144 > 128);
  trees n = 22, 67 all proved (= them), n = 202 (> 128) not.
- Rome, 10 s cap: 10,502/11,534 = 91.1 % proved in 7 min wall (they: 95.6 % at 600 s). All misses n ≥ 75.
  Rerun of the 1,032 capped graphs at 120 s (`rome_capped_120s.csv`): +386 → 10,888/11,534 = 94.4 %; the
  646 still capped have the same n-profile as their 502 unsolved (all n ≥ 79). Like-for-like 600 s rerun of
  those 646 (`rome_capped_600s.csv`, 2026-09-28): +295 → **11,183/11,534 = 97.0 % proved, vs their 95.6 %**;
  351 still open (theirs 502), all n ≥ 86, ub−lb gaps 2–6. The 600 s pass proved its graphs at a median
  of 279 s, so the curve is still rising at the cap.
**Conclusion:** at ≤ 128 vertices the untuned closing-order search matches or beats the published solver;
every systematic miss is the 128-vertex C limit. Next: multiword bitsets in the C (phase 6b), then the
lower-bound work of phase 7 (myciel6, cages).

### Reference points from Kobayashi–Komuro–Tamaki (SEA 2014), obtained 2026-09-28
Their search = our search minus the subset / old / better-move rules, in Java with no vertex limit, 30-min cap.
Table 6 vs ours: queen9_9 94 s → 0.45 s; anna (n=138) they TLE at ub 14, we budget at ub 15 (Python path);
fpsol2.i.1 (n=496) they prove pw 67 in 323 s, we fail (Python path, lb 66 ub 68). Table 5: 145/162 TreewidthLIB
instances with ≤ 300 vertices proved. Beating Table 5 needs phase 6b; the TSP/Bayesian-net TreewidthLIB files are
not online (the SEA 2014 volume in `~/Downloads` also holds Coudert et al.'s conference version, pp. 46–58).

### Phase 6b — lift the 128-vertex limit in the C — DONE 2026-09-28
Replace `unsigned __int128 mask_t` by fixed-width multiword sets (e.g. 4×64 = 256 bits, or a compile-time
`WORDS`), keep the Python wrapper's packing generic. Covers queen12–16, anna, zeroin, fpsol2, grids ≤ 16×16,
the 202-node trees, most hb graphs.
Done as `pathwidth/closing_search_w.c`: `set_t { uint64_t w[WORDS]; }` with compile-time WORDS ∈ {2,4,8,16}
(128…1024 vertices), per-depth scratch frames on the heap, memo capped at ~512 MB. The wrapper builds
`_closing_search_w{W}.so` lazily and picks the smallest W that fits; `closing_search.c` (the 128-bit original)
stays as the reference the tests compare against (`legacy=True`). Tests: multiword = legacy node for node with
better move on/off; W=4/8/16 = Python node for node above 128 vertices; 95 tests pass. Speed at W=2 equals the
original (M6 0.27 s both; queen10 2.1 s vs 2.6 s). Rerun of every benchmark graph that had fallen to the Python
path: `bench/results/*_w.csv`. **Result (600 s, 2026-09-28):** coloring 27→31/58 (+queen12_12 = 103 in
464 s, fpsol2.i.1 = 67 in 5 s, zeroin.i.2/i.3 = 32); VSPLIB grids 7→9/50 (sides 12, 13 now proved; Coudert
et al. also stopped at 13); VSPLIB trees 30→**50/50** (all twenty 202-node trees in ~3 s each; they proved none);
VSPLIB hb 26→**39/73** (they: 26), new: can__161, dwt__162/193/209/221/310/361/492/512, can__268, ash292,
plat362, bcsstk19 (n=817, pw 11); named 124→125/150. Remaining misses are large sparse graphs where the
degeneracy lower bound is far from the width (le450, school, inithx, homer, anna, myciel6/7, queen13–16, cages).

TreewidthLIB, Rome graphs, VSPLIB (grids γ ≤ 13, trees, hb), Mycielski M6/M7,
queen graphs, Delaunay TSP graphs — with Coudert et al. 2016 Tables 3–5 as the
comparison targets; the 2005 challenge customer graphs as the MOSP link.

## 4. Risks / open points
- Python `int` bitsets are fine for correctness but ~120× slower than the C.
- `old_move` + `memo` soundness question is inherited unchanged.
- Node counts depend on vertex numbering (tie-breaks); tests fix a labelling.
- `restrict=True` remains a heuristic (`ub_MOSP`), never returns `unsat`.
