# `ub_MOSP`: Chu & Stuckey's Restricted DFS as an Upper Bound

**Status:** implemented and measured, 2026-09-18. `satisfiability/heuristics.py`,
strategy `cs-dfs`. Item 1 of `reports/chu_stuckey_plan.md` §7.

---

## 1. Summary

Chu & Stuckey (2009) §3.4 obtain an upper bound by running their complete
customer search with one line changed: branch on `R ∩ O(S)`, the remaining
customers whose stack is already **open**, instead of on all of `R`. The
restriction makes the search incomplete — it can exclude every optimal order —
and they report it finding the optimum almost always, 104× and 3010× faster on
100-100-2 and 125-125-2.

It reproduces here, and the margin is larger than expected:

| | improved | stacks saved | wall clock |
|---|---|---|---|
| two `customer-tabu` sweeps (3 seeds, then 12) | 54 / 148 | 113 | ≈ 2 h |
| `cs-dfs`, one run, no seeds | **25 / 148** | **38** | **3 s** |

The 25 are improvements *on top of* the 54: they are instances where fifteen
seeded tabu runs over two hours had already taken everything they could find,
and a 0.1-second search found more. The largest single gain was
`Random-125-125-6-2_0`, 82 → 77.

Nothing closed. Every improvement stayed above its lower bound, which is the
finding `chu_stuckey_plan.md` §2 predicted: the gap on these instances is a
lower-bound problem, and no upper bound will close it.

---

## 2. Why the restriction is not just a cheaper search

Closing a customer nobody has opened yet forces its entire neighbourhood open in
one step. The restriction forbids exactly that move, and what makes it cheap is
not the smaller branching factor on its own but what it does to pruning:

- the cost of a prefix never falls as the prefix grows, so a branch whose
  running peak has reached the incumbent cannot beat it;
- candidates are expanded cheapest-first, so the cut fires on the whole
  remaining fan at once rather than one child at a time.

Together these exhaust the restricted space in well under a second on 125
customers. The node budget (`max_nodes`, default 200,000) was never reached on
any instance measured: the search **finishes**, having proved that no order in
the restricted space beats what it returned.

That is why extra effort buys nothing. Seeding with five random closing orders
instead of MCN's — a deliberately worse incumbent, so a wider search — returned
an identical value on all six instances tried, for five times the time:

| instance | MCN seed | 5× random seed |
|---|---|---|
| SP3 | 36 (0.6 s) | 36 (3.1 s) |
| SP4 | 57 (0.7 s) | 57 (3.2 s) |
| Random-100-100-8-5_0 | 77 (0.6 s) | 77 (3.2 s) |
| Random-125-125-2-4_0 | 29 (0.6 s) | 29 (3.2 s) |
| Random-125-125-6-2_0 | 77 (0.7 s) | 77 (3.4 s) |
| Random-125-125-10-3_0 | 104 (0.7 s) | 104 (3.3 s) |

The restricted space is small enough to be searched out, so the quality of the
bound is set by the restriction, not by the budget. Spending more time on this
heuristic is not an available option — a different restriction would be.

---

## 3. Head to head with `customer-tabu`

Twelve instances sampled evenly from the 148 unproven, each strategy run once.
`cache` is the best value known before either run, after both tabu sweeps.

| instance | cache | lb | `customer-tabu` | s | `cs-dfs` | s |
|---|---|---|---|---|---|---|
| Random-100-100-10-1_0 | 88 | 59 | 88 | 50.8 | **87** | 0.1 |
| Random-100-100-4-3_0 | 47 | 23 | 50 | 44.7 | 48 | 0.1 |
| Random-100-100-8-5_0 | 78 | 46 | 79 | 48.5 | **77** | 0.1 |
| Random-100-50-6-2_0 | 44 | 24 | 44 | 34.5 | 45 | 0.1 |
| Random-125-125-10-4_0 | 108 | 67 | 109 | 68.0 | **107** | 0.1 |
| Random-125-125-6-1_0 | 84 | 40 | 89 | 65.7 | 84 | 0.1 |
| Random-40-40-6-4_0 | 29 | 21 | 30 | 14.6 | 30 | 0.1 |
| Random-50-100-4-1_0 | 36 | 24 | 38 | 24.1 | 38 | 0.1 |
| Random-50-100-8-3_0 | 46 | 43 | 46 | 26.4 | 46 | 0.1 |
| Random-50-50-4-5_0 | 22 | 18 | 24 | 18.1 | 25 | 0.1 |
| Random-75-75-10-2_0 | 66 | 50 | 67 | 34.6 | 67 | 0.1 |
| Random-75-75-4-4_0 | 34 | 19 | 35 | 30.3 | **34** | 0.1 |

Seven wins, two draws, three losses, at 300-600× the speed. The losses matter:
`cs-dfs` does not dominate, and on SP3 it returns 36 against the 35 tabu found.
Both strategies stay registered and `benchmarks/reheuristic.py` saves
monotonically, so running both keeps the better of the two per instance;
`customer-tabu+cs-dfs` does that in one call, tabu first and the DFS pruning
against its result.

---

## 4. What it is for

The bound is not the point. `chu_stuckey_plan.md` §2's relaxation driver calls
an upper bound in its inner loop, once per candidate unmerge, to decide whether
it has relaxed too far. At 50 seconds a call that loop is not affordable; at 0.1
seconds it is free. Item 1 existed to unblock item 5, and it does.

---

## 5. Validation

`tests/test_heuristics.py`. The parametrised suites over `STRATEGIES` already
require every strategy to return a real permutation whose simulated value equals
its claim, and to be a genuine upper bound against brute force. Four tests are
specific to this one:

- `_cs_cost` agrees with the set-theoretic definition `max_i |O(S_i) - S_{i-1}|`
  computed independently with Python sets, on 60 random instances.
- the search is optimal on ≥ 90% of exhaustively-solved random instances (599 of
  600 in a wider run, with no value ever below the optimum).
- a seeded run never returns worse than its seed.
- `max_nodes=0` still returns the seed's ordering, so the anytime contract holds.
- a disconnected instance is ordered rather than abandoned, which is the branch
  where `R ∩ O(S)` is empty and every remaining customer becomes a candidate.

The value returned is always the *simulated* count of the ordering built, never
the search's own score. `_cs_cost` over-charges orders that no product sequence
realises (313/400 agreement per order, `chu_stuckey_plan.md` §0.1), so scoring
by it would report bounds that are true but needlessly weak.
