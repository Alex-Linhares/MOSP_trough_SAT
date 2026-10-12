# The contraction-minor step in the exact solvers

*2026-10-12. Implements the recommendation of
`reports/pathwidth_lower_bounds_survey.md` §6 and the first item of
`paper1/todo.md`, "The contraction-minor lower bound". Scripts, raw output and
certificates are in `reports/scratch/minor_bound/`. Every run shared the machine
with other jobs (load average 40-60 on 32 cores), so seconds are noisy. Node
counts are not.*

**The step is on by default in both solvers. That was the owner's decision on
2026-10-12. Its settings are *proposed*, pending the owner's confirmation
(section 7).**

## 0. Summary

- **What it is.** Pathwidth is minor-monotone. So before the descent refutes
  `w = UB - 1` on the whole graph, it contracts the graph greedily: a
  minimum-degree vertex is merged into a neighbour. It then tries to refute
  `w` on contractions of growing size under a node budget. A refutation on a
  minor proves the width. The descent ends with proof `"minor"`, and a
  certificate that anyone can replay: the contraction sequence plus the
  refuted width. When no minor refutes `w`, a minor's exact pathwidth still
  raises the reported lower bound.
- **What it closes.**
  - **Graph solver.**
    - myciel6: pw = 38, in 0.2 s. It was open after 25 min and after a
      5 h 45 min unlimited run.
    - myciel7: the proved lower bound rises from 42 to **71**, so pw ∈ {71, 72}.
      It is not closed.
    - **Rome: 271 of the 340 graphs left open at 600 s are proved at 60 s
      each** (median 0.5 s; 262 under 10 s). The other 69 end with a lower
      bound one below their upper bound.
    - Also newly proved by our solver (open in its 600 s runs):
      - two colouring graphs, anna and myciel6;
      - one named graph, RingedTree_8;
      - four Harwell-Boeing graphs, bcsstk20, can__229, can__256 and
        lshp_265.

      All are proved within 60 s. (A random 300-graph Rome sample also gains
      17 graphs, but those are among the 340 above.)
    - The lower bound rises on most graphs that stay open, e.g. queen13_13
      from 47 to 94 and JohnsonGraph_10_4 from 35 to 72.
  - **MOSP.** Started from the recorded optimum, as a re-certification starts:
    - Random-125-125-2-3_0 (21) certified in **0.6 s of search**, against
      1,128 core-hours for the root-split refutation;
    - Random-125-125-2-1_0 (24) certified in **30 s with the large
      configuration**, against 1.6 × 10¹¹ nodes recorded. The default budget
      only reaches 23.
    - 6-1_0, 8-2_0 and SP4 are refuted on the full instance within a minute
      either way; the step adds a lower bound 1-3 below the optimum.
    - 4-1_0 stays open at 600 s. Its lower bound rises to 53 by default and
      56 with the large configuration; the optimum is 57.
- **Net effect on graphs proved with and without it.** Nodes are exactly
  paired against the 600 s baseline.

  | set | nodes |
  |---|---|
  | Rome sample | −99.1% |
  | grids | −93% |
  | Harwell-Boeing | −67% |
  | colouring | −55% |
  | named | +1.1% |
  | VSPLIB trees | **+20%** |

  The trees are the worst set: up to 1.5 M extra nodes, about 1.5 s per
  tree. On a 120-instance MOSP sample the cost is +4% of time. No proved
  width or value changed anywhere.
- **Soundness.** The closures checked were each re-refuted on the replayed
  minor, with zero disagreements:
  - under Chu & Stuckey's published rules: 292 of 292 (Rome, the step
    alone) and 3 of 3 (MOSP);
  - with every dominance rule off (memo only, sound with no dominance
    theorem): 261 of 292 and 2 of 3. The rest ran out of budget, which is
    not a disagreement.

  The independent checks of `reports/minor_bound_verification.md` (another
  session, code written from scratch) certify myciel6, myciel7 ≥ 71 and the
  four corpus optima rule-free.

## 1. What was built

### 1.1 Graph solver (`pathwidth_solver/`)

- `pathwidth/minor.py` (new):
  - `contraction_sequence(masks, size, rule)` is the greedy contraction,
    with rules `"min-d"` and `"least-c"`. A minimum-degree vertex (ties by
    index) is contracted into:
    - min-d: its least-degree neighbour;
    - least-c: the neighbour sharing fewest neighbours with it.

    `u` keeps its index, and `N(u) ∪ N(v) − {u, v}` becomes its
    neighbourhood. That is a genuine edge contraction: no self-loop, no
    multi-edge. An isolated vertex is deleted. The rules and tie-breaks are
    those of the survey's scratch code, which this reproduces exactly (21,108
    nodes on the 58-vertex myciel6 minor).
  - `replay(masks, sequence)` rebuilds the minor. It raises an error if a
    pair is not an edge of the current graph, so a sequence that replays is
    a minor.
  - `check_branch_sets` is an independent model check. The branch sets must
    partition the vertices, each must be connected, and minor adjacency must
    equal adjacency between branch sets.
  - `MinorLadder` is the step: `try_refute(w)` and `raise_lower(lower)`.
  - `MinorConfig` holds the settings (section 7).
- `pathwidth/solve.py`:
  - `solve_masks(..., minor=True)` and `solve(...)` run the step inside the
    descent. Before each refutation of `w` on the full graph, a 100,000-node
    probe of the full graph runs first. Only if the probe does not settle `w`
    does the ladder run: refute `w` on a minor, otherwise raise the lower
    bound from a minor's exact pathwidth, then the full refutation.
  - `Solution` gains `proof="minor"` and `minor`, the certificate: refuted
    width, size, rule and contraction sequence. `solve` translates the
    sequence to the graph's labels. It also gains `minor_nodes` and
    `minor_seconds`, which are already included in `nodes` and `seconds`.
  - `lower` includes what the minors proved, also when the descent ends
    unproved.
  - For a disconnected graph, the proof of the widest component is reported,
    in the order `refutation`, `minor`, `bound`.
- `bench/run.py` gains `--minor on|off` (default on) and the columns
  `minor_step`, `minor_nodes`, `minor_seconds`, `minor_size`, `minor_rule`
  and `minor_refuted`. `minor` counts as proved. `bench/summary.py` counts
  `minor` as proved.
- `minor=False` turns the step off, for measurements and tests only.

### 1.2 MOSP solver (`satisfiability/`)

- `relaxation.py` is extended rather than duplicated.
  - Merging two customers who share a product contracts that edge of the
    MOSP graph. So Chu & Stuckey's Lemma 1, which the module used to rest on
    as a measurement, now follows from minor monotonicity and
    `MOSPGraph.lean`.
  - New: `minor_sequence(instance, size, rule)`. It is the same contraction
    on the MOSP graph, and a test checks it is identical to the graph side's.
  - New: `minor_groups(instance, sequence)` replays the sequence as `Group`s.
    It raises an error if a merge joins customers who share no product, so a
    sequence that replays is a genuine contraction.
  - New: `MinorConfig`, `MinorCertificate` and `MinorLadder`, the same step
    in MOSP units, with refutations by `customer_search.decide`.
  - `prove` and `lower_bound`, the F(c)-ranked driver, are unchanged.
- `customer_search.solve(..., minor=True)` runs the same probe and ladder
  inside the descent. `Solution` gains `lower`, `minor`, `minor_nodes` and
  `minor_seconds`.
- `mosp_solver.py` adds the new provenance `certified:minor` and the lower
  bound source `minor`.
  - `solve_mosp_exact(..., minor=None)` falls back to `DEFAULT_MINOR = True`.
    A value proved by a minor is saved as `certified:minor`. A lower bound a
    minor proved is saved with source `minor`.
  - The save rules keep the guarantees of CLAUDE.md, "The provenance field".
    Saves are monotone in the value, and a certified value is never demoted
    to `solution`. **New:** at an equal value, an existing
    `certified:refutation` is never replaced by another certified kind, since
    a refutation on the instance itself rests on less than a minor or a
    bound. A minor certificate can be upgraded to a refutation, never the
    reverse.
- `benchmarks/csearch.py` and `benchmarks/corpus.py` know `minor` and
  `certified:minor`.
- Nothing was written to `solutions/`. The measurements used scratch
  solutions directories, or `customer_search.solve`, which does not save.

### 1.3 Tests

- `pathwidth_solver/tests/test_minor.py`, 9 tests:
  - the contraction against networkx's `contracted_nodes`, an independent
    implementation;
  - prefix consistency;
  - `replay` rejects non-minors;
  - pw(minor) ≤ pw(G) by brute force on 120 random graphs, at every size,
    both rules;
  - the descent with the step forced on at every size agrees with brute
    force on 150 graphs, and with the step off on 30 graphs of 20-40
    vertices. Every minor certificate replays and refutes, including with
    every dominance rule off;
  - a minor raises the lower bound;
  - labels are translated.
- `tests/test_minor_bound.py`, 16 tests:
  - pw(minor) ≤ pw(G) against the exact subset DP
    (`fixed_parameter_algorithm.pathwidth`), more than 300 minors per rule;
  - the MOSP contraction equals the graph contraction, both the sequence and
    the merged instance's MOSP graph;
  - `minor_groups` rejects non-contractions;
  - the descent with the step forced on agrees with the step off on 120
    random instances, and every certificate replays and refutes, memo-only
    included;
  - the default step on eight certified corpus instances (40-75 customers)
    returns the certified optimum;
  - `solve_mosp_exact` records `certified:minor` in a temporary directory,
    and the save rule never lets a minor certificate replace a refutation;
  - a contraction's exact optimum is never above the optimum.
- `pathwidth_solver/tests/test_solve.py::test_budget_exhaustion_is_reported_not_claimed`
  used myciel5 as an instance the budget cannot prove. With the step on, a
  34-vertex minor proves it in about 2,000 nodes. The test now runs that
  part with `minor=False`, and adds an assertion that the default proves it.

## 2. The Mycielski graphs

`reports/scratch/minor_bound/myciel.py`. The descent uses the default step and
a 600 s budget. The baseline is `bench/results/repaired/coloring.csv`, the same
solver without the step at 600 s.

| graph | n | pw | without the step (600 s) | with the step (default) | certificate |
|---|---|---|---|---|---|
| myciel5 | 47 | 20 | proved, 685,211 nodes, 0.37 s | **minor**, 102,185 nodes (2,184 in minors), 0.1 s | 34 vertices, min-d, refutes 19 |
| myciel6 | 95 | 38 | **open**: lower 25, width 38 (and 5 h 45 min unlimited: no answer) | **minor, 128,367 nodes, 0.2 s** | 58 vertices, min-d, refutes 37 |
| myciel7 | 191 | 71-72 | open: lower 42, width 72 | open: **lower 71**, width 72 | 106 vertices, min-d, refutes 70 |

- myciel5 and myciel6 each spend 100,000 of their nodes in the full-graph
  probe that runs before the ladder.
- On myciel7 the step spent 15 M nodes. That certificate is cheaper than the
  survey's: a 106-vertex minor in 685,684 nodes, against 110 vertices in
  2.28 M.
- Refuting 71 on minors of 136 vertices or more ran past 2.4 × 10⁸ nodes per
  call with the large configuration (750 M nodes over 703 s). That does not
  settle 71 against 72, which stays open (`paper1/todo.md`, "myciel7").

## 3. The graph benchmark sets

### 3.1 Method

- The new descent, with the step on at its defaults, ran at **60 s per
  graph**.
- It is compared with the recorded runs without the step,
  `pathwidth_solver/bench/results/repaired/*.csv`. Those had up to 600 s per
  graph; Rome ran in stages of 10, 120 and 600 s.
- With the step off, node counts are deterministic. They were checked equal
  to the baseline on every graph proved by both: 29 colouring, 123 named, 50
  tree and 39 Harwell-Boeing graphs. So the node comparison below is exactly
  paired. Seconds are not paired; the machine was loaded.
- Script: `vs_baseline.py`.

### 3.2 Results

The "proved" columns count graphs proved by the baseline at up to 600 s and by
the new descent at 60 s.

| set | graphs | proved, baseline (≤ 600 s) | proved, new (60 s) | gained | lost (baseline needed > 60 s) | nodes on graphs both prove |
|---|---|---|---|---|---|---|
| Rome, the 340 open at 600 s | 340 | 0 | **271** | 271 | 0 | – |
| TreewidthLIB colouring | 58 | 31 | 32 | 2 (anna, myciel6) | 1 (queen12_12, 391 s) | 192.7 M → 86.9 M (−55%: games120 proved by a minor) |
| named | 150 | 125 | 125 | 1 (RingedTree_8) | 1 (M22Graph, 65 s) | 249.5 M → 252.3 M (+1.1%) |
| VSPLIB trees | 50 | 50 | 50 | 0 | 0 | 49.7 M → 59.6 M (**+19.9%**) |
| VSPLIB Harwell-Boeing | 73 | 39 | 43 | 4 (bcsstk20, can__229, can__256, lshp_265) | 0 | 18.8 M → 6.2 M (−67%) |
| VSPLIB grids (the first 12 in file order, 100-361 vertices) | 12 | 4 | 4 | 0 | 0 | 42.8 M → 3.1 M (−93%) |
| Rome, random sample of 300 with n ≥ 40 | 300 | 280 | 296 | 17 | 1 (grafo8800, 191 s) | 10.9 G → 97.6 M (**−99.1%**) |

The three "lost" graphs are a budget artefact. The baseline proved them in
391 s, 65 s and 191 s, above the new run's 60 s. The new run reaches the same
widths, with lower bounds 15, 13 and 1 short of them.

**Missing numbers.** The full VSPLIB grid set (50 graphs, up to 2,809 vertices)
was not run: only the first 12. Under the owner's rule of 2026-10-12, proved
graphs are not re-run, so the rest of the 11,534 Rome graphs were not either.

**Rome, the 340 graphs open at 600 s.**

- **End to end** (`rome_open_e2e.csv`): the descent from its own upper bound,
  60 s per graph.
  - It proves **271**: 189 in under 1 s, 262 in under 10 s, the slowest in
    56 s. Every one is proved by a minor, at the width recorded at 600 s.
  - The other 69 end one short: their lower bound is one below their upper
    bound. 22 of them did not find the recorded width within 60 s.
  - A first end-to-end pass (`old/v1/`) proved 269. Its code differs from the
    final code only in the pre-checks that save cost.

- **The step alone** (`graph_step.py`): the ladder only, started from each
  graph's recorded width.
  - It closes **292 of the 340**, in 259 s of search in total (median
    0.13 s, maximum 8 s).
  - The other 48 get a lower bound one below the recorded width. Each could
    therefore close if its upper bound came down by one.
  - Every one of the 292 replays and is refuted again under the published
    rules, and 261 also with every dominance rule off (`rome_step_verify.csv`).
- **Closing minor size.** 170 of the 271 end-to-end closures are at the first
  size, n/2. 24 need a minor above 0.75 n.
- **Rules.** min-d gives 264 of the 271 closures and least-c 7. In the first
  pass, which asked least-c even when it built the same minor as min-d,
  least-c was credited with 64.

**Lower bounds on graphs that stay open.** These rose on 7 colouring graphs:

| graph | lower bound | upper bound |
|---|---|---|
| fpsol2.i.2 | 31 → 35 | 43 |
| fpsol2.i.3 | 31 → 35 | 43 |
| myciel7 | 42 → 71 | 72 |
| queen12_12 | 43 → 88 | 103 |
| queen13_13 | 47 → 94 | 121 |
| school1 | 122 → 169 | 182 |
| school1_nsh | 106 → 148 | 156 |

They also rose on 17 named graphs, for example:

| graph | lower bound | upper bound |
|---|---|---|
| Balaban10Cage | 5 → 14 | 15 |
| HarriesGraph | 5 → 14 | 15 |
| SymplecticPolarGraph_4_4 | 24 → 50 | 64 |
| JohnsonGraph_10_4 | 35 → 72 | 109 |

## 4. The MOSP corpus instances

`mosp_corpus.py`. The descent starts from the recorded optimum as its upper
bound, as a re-certification does from the stored witness. The floor is
`_lower_bound`, and the run is `customer_search.solve` with the step on.

- **default**: the default settings, with a 600 s budget.
- **large**: `first_nodes = 10⁶`, `total_nodes = 5 × 10⁸`,
  `time_fraction = 0.9`, with a 900 s budget.

| instance | n | optimum | floor | default | large | recorded cost without the step |
|---|---|---|---|---|---|---|
| Random-125-125-2-3_0 | 125 | 21 | 12 | **minor** at 69 (least-c), 0.6 s of search, 1.09 M nodes | **minor**, 0.4 s | 4.25 × 10¹² nodes, 1,128 core-hours |
| Random-125-125-2-1_0 | 125 | 24 | 13 | open at 600 s, lower **23** (63, min-d) | **minor** at 87 (min-d), **30.5 s**, 58.2 M nodes | 1.62 × 10¹¹ nodes |
| Random-125-125-6-1_0 | 125 | 81 | 63 | refutation, 51 s; lower 78 from a minor | same | 66 s (ledger, pre-fix rules) |
| Random-125-125-8-2_0 | 125 | 93 | 84 | refutation, 6 s; lower 87 | same | – |
| SP4 | 100 | 53 | 37 | refutation, 34 s; lower 52 (83, least-c) | same | 44 s (ledger) |
| Random-125-125-4-1_0 | 125 | 57 | 27 | open at 600 s, lower **53** | open at 900 s, lower **56** (105, least-c) | 26,447 s (ledger) |

- **2-3_0 and 2-1_0** are the two density-2 instances that cost the project
  the most, and the step certifies both. The large-configuration rows for
  4-1_0, 8-2_0 and SP4 are from the first pass (`old/v1/`), whose code
  differs only in cost-saving checks. The run of the final code was stopped
  to free cores.
- **6-1_0 and SP4.** The survey closed them on minors of 96-120 vertices,
  above the default's 0.85 n. They are refuted on the full instance in under
  a minute anyway, so the ladder is not extended for them.
- **End to end from the heuristic upper bound.** The first pass ran 2-1_0
  through `solve_mosp_exact` from the heuristic upper bound of 25 (`old/`).
  The descent could not find the satisfiable 24 within 600 s, so no target
  of 23 was ever reached. The step pays off on the corpus when the descent
  starts from the stored witness, which is how re-certification runs.
- **Re-checks of the corpus certificates** (`mosp_verify.py`). Each
  contraction replays.

  | instance | contraction | refuted | published rules | memo only | MOSP ≤ value on the contraction |
  |---|---|---|---|---|---|
  | 2-3_0 | 69 customers, least-c | MOSP ≤ 20 | 0.66 M nodes | 6.0 M nodes | satisfiable |
  | 2-3_0 | 75 customers, min-d | MOSP ≤ 20 | 1.9 M nodes | 21.3 M nodes | satisfiable |
  | 2-1_0 | 87 customers, min-d | MOSP ≤ 23 | 57.4 M nodes | budget out at 5 × 10⁸ | satisfiable |

  The memo-only refutation of 2-1_0 did not finish within its budget. The
  rule-free certificate of `minor_bound_verification.md` covers it (255 s,
  19.7 GB).

## 5. Cost on instances the step does not help

**MOSP**: `mosp_sample.py`, 120 random certified corpus instances with at least
40 customers, excluding the day-long 125-125-2/4 classes. Each ran at 60 s with
the step off and on, the same floor, on 2 cores.

- **No value differs from the certified optimum.**
- Proof kinds, as (off, on) pairs:
  - 62 (refutation, refutation);
  - 50 (bound, bound);
  - 2 (refutation, minor);
  - 2 (open, minor): Random-100-50-4-4_0 in 1.0 s and Random-100-100-2-1_0
    in 3.5 s, both open at 60 s without the step;
  - 4 (open, open), with lower bounds raised, e.g. SP4_0 from 37 to 52 and
    Random-125-125-6-5_0 from 49 to 71.
- **On the 114 proved both ways**: 69.1 s → 72.0 s (+4%), and nodes +0.7%.
  The step ran on 10 of them, because the probe settled the rest.
- **Worst slowdown**: Random-100-50-8-5_0, 5.4 s → 6.7 s.

**Graph sets** (exactly paired nodes, section 3):

- **VSPLIB trees: the worst set, +20% of nodes.**
  - These trees are hard for the search: about 3 M nodes each.
  - Every minor admits width `pw − 1`, so the step cannot refute anything.
    But finding those layouts on minors of 121-171 vertices costs up to
    650 k nodes each. The restricted search does not find them, and neither
    do the lifted and greedy layouts.
  - Worst case: TREE_202_5_rot11, 3.38 M → 4.88 M nodes, 2.95 s → 4.67 s.
- **Named and colouring**: per-graph slowdowns of at most about 1 M nodes.
  Examples:
  - queen11_11: 33.9 M → 34.9 M nodes;
  - CubeGraph_6: 7.5 M → 7.9 M nodes;
  - BuckyBall: 0.24 M → 0.37 M nodes.

  Larger differences in seconds are machine load: queen11_11 also went
  37 s → 47 s for 3% more nodes.
- **Rome sample** (300 random Rome graphs with n ≥ 40). The step ran on 132
  of the 279 proved both ways, and it is a net gain there: 10.9 G → 97.6 M
  nodes. The worst slowdown is grafo9094.83, 2.30 M → 2.49 M nodes (+191 k).
- **No proved width changed on any set.**

## 6. Correctness

- **Minors.** The contraction is checked against networkx on random graphs
  at every size. Every recorded certificate replays through `replay` or
  `minor_groups`, which reject any step that is not an edge contraction, and
  through `check_branch_sets`.
- **Monotonicity.** pw(minor) ≤ pw(G) was checked against brute force and
  against the exact DP.
- **Answers.** The descent with the step forced on at every size agrees with
  the descent without it, and with brute force:
  - graph side: 150 graphs of 4-8 vertices and 30 of 20-40 vertices;
  - MOSP side: 120 instances, plus eight corpus instances against their
    certified optima.

  No proved width changed in the benchmark sets (section 3), and no MOSP
  value in the sample (section 5).
- **Refutations.**
  - Every refutation on a minor runs `decide` with the descent's rules. By
    default these are the repaired rules proved sound in
    `lean/MOSPFormalization/Search/`.
  - Rome closures were refuted again on their replayed minors: the 292 of
    the step alone and the 269 of the first end-to-end pass.
    - Under the published rules: all of them (292 and 269).
    - Memo only, with no dominance rule at all: 261 and 238. The rest ran
      out of a 5 × 10⁷-node budget. That is no answer, not a disagreement.
  - The 271 closures of the final end-to-end run were **not** re-verified,
    under the owner's rule that proved instances are not re-run. 264 of them
    are graphs the two verified runs already closed.
- **What the proof rests on.** A `"minor"` proof rests on minor monotonicity,
  which is classical (Fellows & Langston 1987, Lemma 4.2) but **not yet in
  Lean** (todo item "Lean"). On the MOSP side it also rests on `MOSPGraph.lean`.
  This is why it has its own provenance, `certified:minor`.
- **Full test suites, with the step on by default.**
  - `tests/`: 1,454 passed, 2 skipped, 1 xfailed.
  - `pathwidth_solver/tests/`: 123 passed.

  The one pre-existing test that changed is described in section 1.3.

## 7. Defaults (confirmed by the owner, 2026-10-12)

*Proposed by the measurements below and confirmed by the owner on 2026-10-12.
On the owner's question why the sizes climb rather than binary-search: along
one contraction sequence a smaller minor is a contraction of a larger one, so
"refutes w" is monotone in size and binary search would be correct; but the
cost of a refutation grows about 10x per 5 vertices, so the failed rungs below
the first success cost a fraction of it (a geometric series), while a binary
search's first probe sits in the expensive middle, and an over-budget probe
gives no direction. Closures cluster at the first rung (170 of 271 Rome
closures at n/2).*

"On by default" is decided. Everything below is proposed. The same values are
used on both sides (`pathwidth.minor.MinorConfig`,
`satisfiability.relaxation.MinorConfig`).

| setting | proposed | the measurement behind it | rejected alternative, and why |
|---|---|---|---|
| `min_vertices` / `min_customers` | 40 | Below 40 the full search is cheap: the hardest refutation in 37,800 generated MOSP instances at n ≤ 40 took 0.04 s (`ml_nature.md` §9). myciel5 (47) still benefits. | 0: Python overhead (contraction, replay) on thousands of tiny Rome graphs, for nothing. |
| `probe_nodes` | 100,000 | The step runs only when a 10⁵-node probe of the full graph does not settle the target. It ran on 11 of 30 colouring, 14 of 124 named and 10 of 114 MOSP graphs proved both ways. A step that closes pays the probe: 100 k nodes on myciel5 and 6. | No probe (the first pass): myciel5 and the trees paid the full step even when the search was cheap. |
| sizes | from ⌈n/2⌉ (at least w + 2) to ⌊0.85 n⌋ in steps of max(2, 0.05 n) | Rome closures cluster at n/2 (170 of 271 end to end); 24 of 271 need more than 0.75 n. The certificates for myciel6, myciel7, 2-1_0 and 2-3_0 sit at 0.61, 0.55, 0.70 and 0.55 n. | Up to 0.96 n, as in the survey for 6-1_0 and SP4: those instances refute on the full graph in under a minute, and large minors cost about as much as the graph. Up to 0.75 n: loses 24 of 271 Rome closures. |
| `rules` | min-d, then least-c, at each size; an identical minor is asked once | min-d gives 264 of the 271 end-to-end Rome closures, least-c 7, plus 2-3_0's cheapest certificate (69 customers; min-d needs 75). On trees the two rules build the same minor, and the duplicate check halves the cost there. | min-d only: cheaper on graphs where the minors differ. How many closures it would lose at a larger size was not measured. |
| `first_nodes`, `growth` | 10⁵, ×3 per size | The cost of a refutation grows about 10× per 5 vertices (survey §4.1). Rome closures need a median of about 2 × 10⁵ minor nodes. | Larger first budgets spend more on graphs not helped; smaller ones need more retries. Not tuned further. |
| `on_stall` | `"retry"`: a size where every minor asked runs out is retried with a 3× budget | Step alone on the 340 open Rome graphs: 246 closed with `"stop"`, **292 with `"retry"`**. | `"stop"`: 46 fewer Rome closures. |
| `share` | 0.5: one target may spend at most half of what remains | Without it, the first and too-high target (UB 76 against pw 72 on myciel7, UB 25 on 2-1_0) spent the whole budget in retries. myciel7's lower bound stayed at 42; with the share it reached 65, then 71 with the climbing `raise_lower`. | No share: the budget is lost at targets that cannot be refuted. |
| `total_nodes` | 2 × 10⁷ per descent | Bounds the step at about 10-25 s on this machine. That covers every Rome closure (maximum 14 M nodes for the step alone), myciel6, myciel7 ≥ 71 and 2-3_0, while the worst set (trees) pays +20%. | 5 × 10⁸ (the large configuration) closes 2-1_0 (58 M nodes) and lifts 4-1_0 to 56, but would let the step cost minutes on graphs it does not help. **Recommended for re-certification drivers, as an explicit `MinorConfig`.** |
| `time_fraction` | 0.25 of a descent time budget | The step never takes more than a quarter of a budgeted run. Not measured separately: whether it bound in any 60 s run was not checked. | – |
| `restrict_nodes` | 20,000 | Before a minor is searched, three layouts are tried; a minor that admits `w` cannot refute it, so finding one ends that minor's turn. The three are the descent's own layout lifted to the minor (closing each branch set at its last vertex never widens it), the greedy layout, and a restricted search. On TREE_202_5_rot6 this cut the step from 1.4 M to 15.6 k nodes. | No pre-check: the trees paid +38% in the first pass. |
| `raise_lower` | climbs minors smallest first, keeps the best, stops at the first budget overrun | myciel7: 69 when the first success was returned, 71 when it climbs. | First success only: weaker bounds. |

**The owner's answers (2026-10-12).** (1) Long runs on unsolved problems use
the large configuration (`MinorConfig(first_nodes=1_000_000,
total_nodes=500_000_000, time_fraction=0.9)`); the default stays for ordinary
runs. (2) `certified:minor` stays a separate label after the Lean proof
(`lean/MOSPFormalization/Minor.lean`): it records how a value was proved.

**Open questions for the owner** (answered above).

1. Should the re-certification drivers (`benchmarks.csearch`,
   `benchmarks.recertify`) pass the large configuration? They now run the
   default step, because `customer_search.solve` has it on. The large
   configuration is what certifies 2-1_0. It is not the default because of
   its cost on instances it does not help.
2. Whether to keep `certified:minor` separate from `certified:refutation`
   once minor monotonicity is proved in Lean.

## 8. What worried me

- **Proofs now rest on one more theorem.** Minor monotonicity is not
  formalised here. Every `"minor"` proof and every `certified:minor` rests on
  it. The Lean item in `paper1/todo.md` is now on the critical path for the
  paper's claims.
- **Nothing on the corpus is re-certified yet.** The step only proves a value
  when the descent starts at it. Its biggest corpus wins, 2-1_0 and 2-3_0,
  come from starting at the stored witness, and 2-1_0 needs the large
  configuration. Nothing was written to `solutions/`, so neither instance has
  been re-certified by this work.
- **Recorded node counts are now pre-minor.**
  - A future `bench/run.py` run, and any `solve`, `customer_search.solve` or
    `solve_mosp_exact` call, includes the step's nodes.
  - Scripts that compare against recorded counts will see different numbers,
    for example `paper1/solver_fix_cost.py`, the `learning/` node-count
    studies and the ledger.
  - `paper1/dataset.py` maps unknown proofs to `"solution"`. A rebuild would
    therefore label minor-proved widths as uncertified. That is
    conservative, but wrong.
  - Pass `minor=False` (`--minor off`) to reproduce old counts.
- **Lower bounds in `Solution.lower` now come from searches.** A wrong minor
  refutation would show up as a lower bound above an achieved width. The
  descent would then stop early with proof `"minor"`, and no witness would
  contradict it. This is the same exposure the existing `lower` argument
  always had, and the reason for the replay and rule-free re-checks above.
- **Seconds are noisy.** The machine ran 20-40 other jobs. The paired node
  counts are the reliable comparison. The seconds in section 3 should not be
  quoted as speed-ups.

## 9. Reproduction

All scripts are in `reports/scratch/minor_bound/`. They write only there, or to
a temporary solutions directory, never to `solutions/`. Superseded first-pass
outputs are in `old/`.

| what | how to run it | output |
|---|---|---|
| Mycielski graphs | `myciel.py 600` | `myciel.out`, `myciel{5,6,7}_certificate.json` |
| the step alone on graphs open in a result file | `graph_step.py RESULTS.csv OUT.csv [--config default\|retry\|large]` | – |
| re-refuting closures on the replayed minor | `verify_closed.py STEP_OR_RESULTS.csv OUT.csv` (published rules, and memo only) | – |
| benchmark sets with the step on or off | `bench_sets.sh on\|off PROCS SET...` (calls `bench/run.py --minor`) | – |
| comparison with the 600 s baseline | `vs_baseline.py SET[=file]` | – |
| comparison with the step off | `compare_sets.py SET` | – |
| MOSP corpus | `mosp_corpus.py default@recorded 600`, `mosp_corpus.py large@recorded 900` | – |
| re-checking MOSP certificates | `mosp_verify.py CERT.json...` | – |
| MOSP sample, step off against on | `mosp_sample.py OUT.csv --count 120 --time 60` | – |

`bench/run.py SET --minor off` reproduces the old node counts exactly.
