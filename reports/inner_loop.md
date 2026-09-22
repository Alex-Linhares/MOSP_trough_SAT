# Profiling the C inner loop

*2026-09-22. `satisfiability/customer_search.c`. The hard refutations visit
274-627 million nodes at ~0.69 µs each, so after three failed attempts to reduce
the node **count** (`reports/expansion_bound.md` §6-7), this is the first look at
the node **cost**.*

## 1. Getting a profile at all

`perf` is unavailable here — `perf_event_paranoid` is 4, so no events can be
opened. `gprof` would not have helped either: the hot functions are `static` and
`-O3` inlines them into `search`, so function-level attribution collapses to one
symbol.

Two methods were used instead, and they disagree in an instructive way.

**Cycle counters.** A copy of the C with `__rdtsc()` around each section, in a
standalone harness. It reports 2,868 cycles per node against a real cost of
~0.69 µs ≈ 2,060 cycles, so the eight `rdtsc` pairs inflate the total by about
40%. Useful for *shape*, not for shares.

**The existing flags.** `cs_decide` already takes `subset_rule`,
`definite_move`, `old_move` and `use_memo` as parameters, so each can be turned
off and the change in µs/node measured with no instrumentation at all. This is
the trustworthy one.

## 2. What the node actually costs

All configurations below ran exactly 80,000,001 nodes on
`Random-125-125-6-3_0`, so µs/node compares cleanly:

| configuration | µs/node | implied cost of the rule |
|---|---|---|
| all on (default) | 0.688 | — |
| no `old_move` | 0.400 | **42%** |
| no `subset_rule` | 0.556 | 19% |
| no memo | 0.573 | 17% |
| no `definite_move` | 0.623 | 9% |
| cost cut only | 0.258 | the irreducible base |

**The dominance rules are the inner loop.** The base search — free moves,
candidate costs, the sort, the recursion — is 0.258 µs of 0.688. Everything else
is the four rules, and `old_move` alone is 42%.

That was not what the work in §3 assumed, and is the more useful finding.

## 3. One pass instead of three

The cycle profile showed three separate O(R) passes over 128-bit words —
building `opens[]`, computing candidate costs, and finding free moves —
together 57% of the instrumented total. They compute the same thing three times.

Since `closed` sits inside `opened`, the cost factors:

> `(opened | N[c]) & ~closed` = `(opened & ~closed) ⊎ (N[c] & ~opened)`

so `cost = open_now + |N[c] \ opened|`, and a free move is just
`|N[c] \ opened| == 0`. Both fall out of the pass that builds `opens[]`.
Verified against the direct form on 23,392 (state, candidate) pairs.

**The first attempt made it slower** — 0.93-1.03× — by storing `own_of[128]`
indexed by customer id on the stack at every node. That is scattered 128-bit
writes, and `dominance_filter` then copied them into its own compacted arrays:
arithmetic removed, memory traffic added. Rewritten to build one compacted,
in-order array that the rules read straight through:

| instance | k | nodes | identical | before | after | speedup |
|---|---|---|---|---|---|---|
| `Random-125-125-2-1_0` | 23 | 30,000,001 | yes | 53.40 s | 48.14 s | **1.11×** |
| `Random-125-125-4-2_0` | 56 | 30,000,001 | yes | 30.31 s | 29.12 s | 1.04× |
| `Random-125-125-6-3_0` | 79 | 30,000,001 | yes | 20.15 s | 20.02 s | 1.01× |
| `Random-125-125-8-5_0` | 90 | 17,120,616 | yes | 11.95 s | 12.02 s | 0.99× |
| **total** | | | | 140.1 s | 133.2 s | **1.05×** |

Node counts identical on every instance, which is the point: this is a pure
optimisation and any change in the counts would mean a change in behaviour.
1.05× overall, 1.11× where it matters most (the sparse instance). Also added:
both O(R²) rules now skip a pair on an integer size comparison before doing any
128-bit work, since a larger set cannot sit inside a smaller one.

Modest, and honest about why: the passes it merged are in the 0.258 µs base, not
in the 0.43 µs the rules consume.
