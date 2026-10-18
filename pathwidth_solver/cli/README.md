# pathwidth: exact pathwidth for graph6 input

A standalone C program that computes the exact pathwidth of each graph it reads
and says how the value was proved. It was written for House of Graphs, which
runs invariant programs per graph under a time limit of about five minutes. It
needs only libc and libm.

It is a port of the Python solver in `../pathwidth/`. The port covers the descent
of `solve.py`, the bounds of `bounds.py` and the contraction-minor step of
`minor.py` with its default `MinorConfig`. It runs on the same C search engine
the Python loads through ctypes. `closing_search_w.c` is a byte-for-byte copy of
`../pathwidth/closing_search_w.c` (`make check-engine` confirms it). The engine
is compiled unmodified, once for each of 2, 4, 8 and 16 64-bit words, and the
smallest build that fits the graph is used, as `native.py` does. The search rules
are the engine's own: free moves, the subset rule, the corrected definite move,
old move and the memo, with the better move off, as in the solver's defaults.

## Build

    make                 # ./pathwidth, gcc -O2 -march=native, -Wall -Wextra -pedantic clean
    make ARCH=           # portable binary (no -march); about 1.8x slower, see Limits
    make test            # 45 unit cases (tests/unit.sh)
    make check-engine    # the engine is still the solver's, byte for byte

The code is C99 plus two GCC/Clang builtins (`__builtin_popcountll` and
`__builtin_ctzll`, which the engine already used), and it needs POSIX
`clock_gettime`.

## Usage

    ./pathwidth [-t seconds] [-n nodes] [-l] [-v] < graphs.g6

The input is graph6 strings, one per line. The program accepts the optional
`>>graph6<<` header, either on a line of its own or as a prefix. It accepts the
1-byte, 4-byte and 8-byte size forms, skips blank lines and ignores trailing
`\r` and whitespace. Graphs may have up to 32,768 vertices. A line it cannot
parse prints `error <reason>` in place of a result, so the output stays aligned
with the input, and the exit status becomes 1. sparse6 and digraph6 input are
rejected.

| option | meaning |
|---|---|
| `-t s` | time budget per graph for the descent, in seconds (default 300; `0` means none). This is the Python's `time_budget`, with the same semantics: it bounds the search, and the minor step stops at a quarter of it. The bounds computed before the search are not counted against it, but they take milliseconds. |
| `-n N` | node budget per search call, the Python's `max_nodes` (default none) |
| `-l` | after each result, print `layout v1 v2 ... vn`: a vertex order (0-based, in input order) whose vertex separation is the width |
| `-v` | on stderr: n, width, status, lower bound, starting upper bound, nodes, minor-step nodes, engine calls, seconds |

## Output

    pathwidth <w> <status>
    layout <v1> ... <vn>            (with -l)

`layout` is a layout in the textbook sense. For every position `i`, at most `w`
vertices at or before `i` have a neighbour after `i`. It is the solver's closing
order, reversed. The program does not trust it. Before printing, it checks two
things: the closing order's largest boundary on the whole graph, computed with
bitmasks, and the textbook vertex separation of the printed layout, computed from
the adjacency lists with no code shared with the search. Both must equal `w`, or
the program stops with an internal error. The empty graph (n = 0) prints
`pathwidth -1 bound`, as the Python does.

## The statuses, and why each is sound

The width `w` is always achieved by the printed layout, so `pathwidth <= w`
holds whatever the status. The status says how the matching lower bound
`pathwidth >= w` was established.

- **`refutation`**: the complete closing-order search refuted `pathwidth <= w - 1`.
  The search is Chu & Stuckey's customer search, ported to graphs. With the
  corrected definite and better moves, the whole search is proved sound in Lean
  (MOSP `lean/MOSPFormalization/Search/`, `exec_repairedFullFilter_mospValue`).
  The dominance rules only discard branches that a kept branch dominates, so
  exhausting the search is a proof.
- **`bound`**: `w` met a proved lower bound, so no search was needed. The lower
  bound is the maximum of the degeneracy and the contraction degeneracy (MMD+,
  least-c). Both are minimum degrees of minors, which bound treewidth and
  therefore pathwidth.
- **`minor`**: `pathwidth <= w - 1` was refuted on a minor reached by greedy edge
  contractions. Pathwidth is minor-monotone (Fellows & Langston 1987, Lemma 4.2;
  paper Theorem 4.11; Lean `pathwidth_gt_of_minorOf` in MOSP
  `lean/MOSPFormalization/Minor.lean`). A refutation on the minor therefore
  refutes the graph. Every contraction sequence is replayed and checked edge by
  edge before its minor is searched. The minor's search uses the same engine and
  rules as a `refutation`.
- **`upper`**: the budget ran out before a proof was found. `w` is an upper bound
  only.

A disconnected graph is solved one component at a time, widest first, each with
what is left of the budget. The width is the maximum over the components. The
status is that of the widest component, preferring `refutation`, then `minor`,
then `bound`, provided every component was proved; otherwise it is `upper`. This
is `solve()` in `solve.py`.

## Validation

**Unit tests** (`make test`, 45 cases): paths, cycles, complete graphs, stars,
complete ternary trees of height 1 to 4 (pathwidth equals height), k×k grids for
k = 2 to 6 and 9 (pathwidth k), Petersen (5), K3,3, K4,6, Q4 (7), the Grötzsch
graph, three disconnected graphs, n = 0, n = 1, an edgeless graph, and graphs
above 64 vertices: P100, C130, a binary tree of height 7, the 9×9 grid, random
G(n, m) at 45, 70 and 120 vertices, random trees on 300 and 500 vertices, and
P1100. The expected values were not taken from memory. The Python solver
computed each one on the fly (`tests/make_unit_cases.py`, which writes
`tests/unit_cases.txt`). All 45 match in both width and status. That includes
four `minor` proofs and P1100, which takes the path for components above 1024
vertices (see Limits).

**House of Graphs sample** (`tests/hog_sample.py`). The sample is 453 graphs
that the first pass (`bench/results/hog_pathwidth.csv`) had already proved in
under 5 s each. It was drawn with a fixed seed and stratified by proof type
(`refutation`, `bound`, `minor`) and by size band (1–19, 20–39, 40–64, 65–128
and 129–250 vertices), 36 graphs per stratum. Only 21 `minor` graphs existed in
the 40–64 band, so that stratum has 21. In total the sample holds 180
`refutation`, 180 `bound` and 93 `minor` graphs. 216 of them have more than 64
vertices and 38 are disconnected. All runs used `nice -n 19` and at most 4
processes.

| check | result |
|---|---|
| width equal to the first pass | **453 / 453** |
| status equal to the first pass | **453 / 453** |
| printed layout achieves the width (re-checked in Python from the edge list) | **453 / 453** |
| width and status equal to a fresh Python run on the same machine | 453 / 453 |
| node count identical to the fresh Python run | 444 / 453 |

All 9 node-count differences are on disconnected graphs whose components are
each smaller than half the graph. networkx's `G.subgraph` lists such a component
in the iteration order of a Python `set`, not in vertex order. The Python
therefore numbers those components differently, and the search breaks ties
differently. This program numbers every component in increasing vertex order.
Feeding the C each component in networkx's order reproduced the Python's node
counts exactly on all 4 graphs checked (57432, 57455, 57508, 57509). On every
connected graph, including all 93 `minor` graphs, the node counts are identical.

**Speed.** Summed solve time over the 453 graphs, both programs on the same
loaded machine, 4 processes each:

| n | graphs | C | Python | Python / C |
|---|---|---|---|---|
| 1–19 | 72 | 0.01 s | 0.03 s | 4.5× |
| 20–39 | 72 | 0.12 s | 0.15 s | 1.3× |
| 40–64 | 93 | 10.7 s | 12.3 s | 1.1× |
| 65–128 | 108 | 39.6 s | 42.9 s | 1.1× |
| 129–250 | 108 | 61.5 s | 66.0 s | 1.1× |
| all | 453 | 111.9 s | 121.4 s | 1.1× |

The two take the same time because both spend it in the same C engine; the
Python is only the driver. The Python times above exclude interpreter start-up
and the networkx import, about 0.3 to 0.5 s per process, which a per-graph
process pays and this program does not. With `make ARCH=` (no hardware
popcount) the engine is about 1.8× slower: 11.0 s against 6.2 s on a 500-vertex
tree.

## Deviations from the Python, all deliberate

1. **Component numbering**: increasing vertex order, not networkx's set order
   (see above). This changes tie-breaks only, never a width. A status could in
   principle differ on a disconnected graph near the budget; none did on the
   sample.
2. **A deadline that has already passed.** The Python passes the engine
   `max(0, deadline - now)` seconds, and the engine reads 0 as "no deadline". A
   search call that starts after the budget has expired, for example on a later
   component, therefore runs without a time limit in the Python. Here it gets
   1e-9 s, so it stops at the engine's first clock check, which comes every
   4,096 nodes. In the first House of Graphs pass the worst overrun was 4.5 s
   (76 of 29,995 graphs ran past 301 s).
3. **Components above 1024 vertices** (the largest engine build). The Python
   falls back to its pure-Python search for these. This program reports the
   greedy layout's width instead, with status `bound` if it meets the lower
   bound and `upper` otherwise. That is sound, but it is not the full descent.
   The largest House of Graphs graph today has 250 vertices.

## Limits

- **Memory.** Each search call allocates the engine's memo table, as the Python
  does. Peak resident memory was 67 MB on the 9×9 grid, 268 MB on a 255-vertex
  tree and 544 MB on a 500-vertex tree.
- **`-n`.** It is the Python's per-call `max_nodes`, and that interacts badly
  with the minor step. When every minor stalls at a size, the step retries
  until half of its 2 × 10^7-node allowance is spent. A small `-n` therefore
  means thousands of short calls: on the 9×9 grid, `-n 1000` makes 10,005 calls
  in 15.5 s and ends `upper`. Prefer `-t`.
- **Time.** `-t` bounds the descent, which is checked every 4,096 nodes. The
  bounds and the restricted-search upper bound beforehand are not counted, but
  they take milliseconds. Under a hard 300 s kill, `-t 290` leaves a margin.

## Files

| file | |
|---|---|
| `pathwidth.c` | graph6 reader, bounds, minor step, descent, checks, main |
| `engine.c`, `engine.h` | compile `closing_search_w.c` once per word count |
| `closing_search_w.c` | the search engine, a verbatim copy of `../pathwidth/closing_search_w.c` |
| `Makefile` | build, `test`, `check-engine` |
| `tests/unit.sh`, `tests/unit_cases.txt`, `tests/make_unit_cases.py` | unit tests and their generator |
| `tests/hog_sample.py`, `tests/hog_sample.txt`, `tests/hog_sample_c.jsonl`, `tests/hog_sample_python.jsonl` | the House of Graphs sample, both runs |

MIT licence, as the repository; the header is in `pathwidth.c`.

## Restarting long runs (added 2026-10-18)

- `-u file`: start from a closing order (0-based vertex numbers, the vertex
  closed first first); its width is recomputed and becomes the starting upper
  bound. Connected graphs only.
- `-L k`: a proved lower bound to start from, so the descent goes straight to
  refuting `k` when the starting width is `k + 1`.
- `-m key=value`: one `MinorConfig` field (`first_nodes`, `total_nodes`,
  `share`, `start_fraction`, `step_fraction`, `max_fraction`, `growth`,
  `min_vertices`, `probe_nodes`, `time_fraction`), repeatable. Defaults are
  unchanged.

The unit tests still pass 45 of 45 with these options added. Used by
`reports/scratch/c_long/run.sh` (myciel7, W4).
