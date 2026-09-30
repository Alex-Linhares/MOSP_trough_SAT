"""Brute-force checker for the pathwidth complex (loop0005 item 02).

Every quantity of Table 1 of Linhares & Yanasse (2002) is computed here from
its *own* source definition, as quoted in `paper2/equivalences.md` (item 01),
and never through pathwidth. The relations item 01 recorded are then checked
exhaustively on small inputs:

- every graph on 1 to 7 vertices (the networkx atlas, 1,252 graphs);
- random graphs on 7 and 8 vertices;
- 0/1 matrices: all of them up to 4 x 4, random ones at 5 x 5.

    python -m paper2.complex_check            # full run, writes the JSON report
    python -m paper2.complex_check --quick    # atlas to 5 vertices, fewer samples
    python -m paper2.complex_check --pebbling # loop0006 item 02: pebbling (P.5)
    python -m paper2.complex_check --pebbling-strategy  # item 03: the Lean proof's constructions
    python -m paper2.complex_check --pebbling-gu  # item 04: Thm 2 and KP Thm 3.1 constructions

(interval thickness by explicit interval models only to 6 vertices; above
that by event words, which the atlas run checks against the model search).

Graphs are `(n, adj)` with vertices `0..n-1` and `adj[v]` the neighbour
bitmask of `v`. A minimum over all layouts is always a literal minimum over
`itertools.permutations` unless the function says otherwise; the three
functions that use a prefix-set DP instead (`vs_dp`, `cutwidth_dp`,
`modified_cutwidth_dp`) do so because their layout cost is a maximum of terms
that each depend only on the prefix set and the next vertex, and the tests
check each against the literal minimum.

Definitions and where they come from (page numbers as in equivalences.md):

- `pathwidth`            Kinnersley 1992 p. 346: sequences of bags with the
                         interval property; search over (introduced, bag).
- `vertex_separation`    Kinnersley 1992 p. 346: `V_L(i)`, prefix side.
- `vsg`                  Lengauer 1981 p. 467: the vertex separator game.
- `interval_thickness`   Kirousis & Papadimitriou 1985 p. 182, Mohring 1990
                         p. 31: least max-clique of an interval supergraph,
                         searched over interval models.
- `narrowness`           Kornai & Tuza 1992 sec. 2: the shack process.
- `node_search`          Kirousis & Papadimitriou 1985 p. 181: place / remove,
                         clearing, recontamination; `monotone=True` forbids
                         any recontamination.
- `edge_search`          Kirousis & Papadimitriou 1986 p. 208: place /
                         remove / slide; `monotone=True` as above.
- `interval_bandwidth`   Fomin 1998 sec. 3.1: surjective numberings, decided
                         by a finite automaton over per-vertex gap ages.
- `split_bandwidth_upto` Fomin 1998 sec. 3.2: bandwidth over splits, with at
                         most a given number of splittings (an upper bound).
- `mosp_value`           Linhares & Yanasse 2002 eqs. (1)-(2).
- `gate_matrix_tracks`   Mohring 1990 p. 18 (MPP): column permutation plus a
                         track assignment of the augmented rows, tracks
                         holding pairwise gate-disjoint nets.
- `pla_folding_tracks`   Mohring 1990 p. 25 (PLAMPP): as above with at most
                         two nets per track.
- `one_dim_logic_tracks` Ohtsuki et al. 1979 sec. II (and sec. IV with the
                         boundary gates fixed at the ends).
- `cutwidth`, `modified_cutwidth`   Lengauer 1981 p. 468 and Def. 6 p. 473.
- `progressive_bw_within` Lengauer 1981 pp. 466-467 (BWP with rule (iii'),
                         optional turning) and Kirousis & Papadimitriou 1986
                         pp. 205-206 (automatic turning); `progressive_black_within`,
                         `unrestricted_bw_within`, `unrestricted_black_within`
                         the other three games; `lengauer_u`, `lengauer_d`
                         Lengauer Def. 1 (pp. 468-469). Checked by
                         `run_pebbling` against equivalences.md P.5.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
import time
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

REPORT = Path(__file__).resolve().parent / "data" / "complex_check.json"
PEBBLING_REPORT = Path(__file__).resolve().parent / "data" / "pebbling_check.json"

# ----------------------------------------------------------------------------
# Graphs
# ----------------------------------------------------------------------------


def graph(n, edges):
    """`(n, adj)` from an edge list on vertices `0..n-1`."""
    adj = [0] * n
    for u, v in edges:
        if u == v:
            raise ValueError("loops are not graphs here")
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return n, tuple(adj)


def edges_of(g):
    n, adj = g
    return [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1]


def from_nx(h):
    nodes = sorted(h.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    return graph(len(nodes), [(idx[u], idx[v]) for u, v in h.edges()])


def path_graph(n):
    return graph(n, [(i, i + 1) for i in range(n - 1)])


def cycle_graph(n):
    return graph(n, [(i, (i + 1) % n) for i in range(n)])


def complete_graph(n):
    return graph(n, list(itertools.combinations(range(n), 2)))


def star_graph(leaves):
    return graph(leaves + 1, [(0, i) for i in range(1, leaves + 1)])


def complete_bipartite(a, b):
    return graph(a + b, [(i, a + j) for i in range(a) for j in range(b)])


def popcount(x):
    return bin(x).count("1")


def is_connected(g):
    n, adj = g
    if n == 0:
        return True
    seen, frontier = 1, 1
    while frontier:
        nxt = 0
        for v in range(n):
            if frontier >> v & 1:
                nxt |= adj[v]
        frontier = nxt & ~seen
        seen |= nxt
    return seen == (1 << n) - 1


def clique_number(g):
    n, adj = g
    best = 0

    def grow(cand, size):
        nonlocal best
        if size + popcount(cand) <= best:
            return
        if not cand:
            best = max(best, size)
            return
        v = cand.bit_length() - 1
        grow(cand & adj[v], size + 1)
        grow(cand & ~(1 << v), size)

    grow((1 << n) - 1, 0)
    return best


# ----------------------------------------------------------------------------
# Pathwidth: Kinnersley 1992 p. 346
# ----------------------------------------------------------------------------


def pathwidth(g):
    """Least `h` such that G has a path decomposition with bags of size <= h + 1.

    Searches bag sequences directly. The state is `(I, B)`: `I` the vertices
    introduced so far, `B` the current bag. The next bag `B'` may not contain a
    vertex that has already left (the interval property (c)); a vertex leaving
    (in `B` minus `B'`) must have all its neighbours already introduced, which
    is exactly what (b) needs given (c). Bags are nonempty. ℕ-valued, so the
    empty graph has pathwidth 0 as in `Pathwidth.lean`.
    """
    n, adj = g
    full = (1 << n) - 1
    if n == 0:
        return 0

    @lru_cache(maxsize=None)
    def best(intro, bag):
        # least max bag size over the rest of the sequence, `bag` already paid
        if intro == full:
            return 0
        avail = bag | (full & ~intro)
        res = n + 1
        sub = avail
        while sub:
            if sub != bag:
                leaving = bag & ~sub
                ok = True
                x = leaving
                while x:
                    v = (x & -x).bit_length() - 1
                    x &= x - 1
                    if adj[v] & ~intro:
                        ok = False
                        break
                if ok:
                    size = popcount(sub)
                    if size < res:
                        r = max(size, best(intro | sub, sub))
                        res = min(res, r)
            sub = (sub - 1) & avail
        return res

    return max(0, best(0, 0) - 1)


# ----------------------------------------------------------------------------
# Layout parameters
# ----------------------------------------------------------------------------


def _prefix_masks(order):
    masks, m = [], 0
    for v in order:
        m |= 1 << v
        masks.append(m)
    return masks


def vs_of_layout(g, order):
    """Kinnersley p. 346: `max_{1 <= i < |V|} |V_L(i)|`, `V_L(i)` the vertices
    at positions <= i with a neighbour at a position > i."""
    n, adj = g
    best = 0
    masks = _prefix_masks(order)
    for i in range(n - 1):
        pre = masks[i]
        cnt = sum(1 for v in order[: i + 1] if adj[v] & ~pre)
        best = max(best, cnt)
    return best


def vertex_separation(g):
    n, _ = g
    if n <= 1:
        return 0
    return min(vs_of_layout(g, p) for p in itertools.permutations(range(n)))


def vsg_of_strategy(g, order):
    """Lengauer p. 467: after the i-th pebbling move, the cut is the set of
    pebble-free vertices adjacent to a pebbled one; the value is the max cut."""
    n, adj = g
    best, peb = 0, 0
    for v in order:
        peb |= 1 << v
        nb = 0
        for u in range(n):
            if peb >> u & 1:
                nb |= adj[u]
        best = max(best, popcount(nb & ~peb))
    return best


def vsg(g):
    n, _ = g
    if n == 0:
        return 0
    return min(vsg_of_strategy(g, p) for p in itertools.permutations(range(n)))


def _layout_dp(n, cost):
    """min over orderings of max_i cost(prefix before i, i-th vertex)."""
    full = (1 << n) - 1
    INF = 10 ** 9
    f = [INF] * (1 << n)
    f[0] = 0
    for s in range(1 << n):
        if f[s] == INF:
            continue
        rest = full & ~s
        while rest:
            v = (rest & -rest).bit_length() - 1
            rest &= rest - 1
            c = max(f[s], cost(s, v))
            t = s | (1 << v)
            if c < f[t]:
                f[t] = c
    return f[full]


def vs_dp(g):
    """Vertex separation by DP over prefix sets. After placing `v` on top of
    prefix `s`, the separated set is the prefix vertices with a neighbour
    outside; its size depends only on `s | v`."""
    n, adj = g
    if n <= 1:
        return 0
    full = (1 << n) - 1

    def cost(s, v):
        t = s | (1 << v)
        if t == full:
            return 0
        return sum(1 for u in range(n) if t >> u & 1 and adj[u] & ~t)

    return _layout_dp(n, cost)


def cutwidth_of_layout(g, order):
    """Lengauer p. 468 (min-cut linear arrangement): edges crossing each gap."""
    n, adj = g
    best = 0
    for pre in _prefix_masks(order)[:-1]:
        c = sum(popcount(adj[u] & ~pre) for u in range(n) if pre >> u & 1)
        best = max(best, c)
    return best


def cutwidth(g):
    n, _ = g
    if n <= 1:
        return 0
    return min(cutwidth_of_layout(g, p) for p in itertools.permutations(range(n)))


def cutwidth_dp(g):
    n, adj = g
    if n <= 1:
        return 0
    full = (1 << n) - 1

    def cost(s, v):
        t = s | (1 << v)
        if t == full:
            return 0
        return sum(popcount(adj[u] & ~t) for u in range(n) if t >> u & 1)

    return _layout_dp(n, cost)


def modified_cutwidth_of_layout(g, order):
    """Lengauer Def. 6 p. 473: width(v_i) = edges {a, b} with
    lambda(a) < i < lambda(b), i.e. passing strictly over position i."""
    return _mcw_layout(len(order), edges_of(g), order)


def _mcw_layout(n, es, order):
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    spans = [(min(pos[a], pos[b]), max(pos[a], pos[b])) for a, b in es]
    return max((sum(1 for a, b in spans if a < i < b) for i in range(n)), default=0)


def modified_cutwidth(g):
    n, _ = g
    if n == 0:
        return 0
    es = edges_of(g)
    return min(_mcw_layout(n, es, p) for p in itertools.permutations(range(n)))


def modified_cutwidth_dp(g):
    n, adj = g
    if n == 0:
        return 0

    def cost(s, v):
        after = ((1 << n) - 1) & ~s & ~(1 << v)
        return sum(popcount(adj[u] & after) for u in range(n) if s >> u & 1)

    return _layout_dp(n, cost)


def bandwidth_of_layout(g, order):
    pos = {v: i for i, v in enumerate(order)}
    return max((abs(pos[u] - pos[v]) for u, v in edges_of(g)), default=0)


def bandwidth(g):
    """min over bijective layouts of the longest edge; backtracking with pruning."""
    n, adj = g
    if not edges_of(g):
        return 0
    for b in range(1, n):
        if _bandwidth_at_most(g, b):
            return b
    return n - 1


def _bandwidth_at_most(g, b):
    n, adj = g
    pos = [-1] * n

    def place(i, placed):
        if i == n:
            return True
        # every placed vertex with an unplaced neighbour must be within b of i
        for u in range(n):
            if pos[u] >= 0 and adj[u] & ~placed and i - pos[u] > b:
                return False
        for v in range(n):
            if pos[v] < 0:
                ok = True
                x = adj[v] & placed
                while x:
                    u = (x & -x).bit_length() - 1
                    x &= x - 1
                    if i - pos[u] > b:
                        ok = False
                        break
                if ok:
                    pos[v] = i
                    if place(i + 1, placed | (1 << v)):
                        return True
                    pos[v] = -1
        return False

    return place(0, 0)


# ----------------------------------------------------------------------------
# Narrowness: Kornai & Tuza 1992 sec. 2
# ----------------------------------------------------------------------------


def narrowness_of_sequence(g, seq):
    """The shack process of Kornai & Tuza: step i puts v_i from the input
    memory into the shack, then moves every v_j (j <= i) with no neighbour
    v_k, k > i, from the shack to the output memory. The value is the maximum
    shack size during the process (reached just after an insertion)."""
    n, adj = g
    shack, done_in, best = 0, 0, 0
    for v in seq:
        shack |= 1 << v
        done_in |= 1 << v
        best = max(best, popcount(shack))
        future = ((1 << n) - 1) & ~done_in
        x = shack
        while x:
            u = (x & -x).bit_length() - 1
            x &= x - 1
            if not adj[u] & future:
                shack &= ~(1 << u)
    return best


def narrowness(g):
    n, _ = g
    if n == 0:
        return 0
    return min(narrowness_of_sequence(g, p) for p in itertools.permutations(range(n)))


def out_narrowness(g):
    """Kornai & Tuza Prop. 2.1's out-sequence: v_i moves to the output memory
    once all its neighbours have entered; here computed as the reversal of
    the in-process, so the check is that reversal changes nothing."""
    n, _ = g
    if n == 0:
        return 0
    return min(narrowness_of_sequence(g, tuple(reversed(p)))
               for p in itertools.permutations(range(n)))


# ----------------------------------------------------------------------------
# Interval thickness: K&P 1985 p. 182, Mohring 1990 p. 31
# ----------------------------------------------------------------------------


def interval_thickness(g):
    """Least clique number of an interval supergraph of G on the same vertices.

    Searched over interval models: each vertex gets a closed interval
    `[l, r]` with integer endpoints in `0..n-1` (enough: an interval graph on
    n vertices has at most n maximal cliques, and a model on them as points);
    adjacent vertices must intersect; the clique number of an interval graph
    is its largest point load (intervals of a line have the Helly property).
    Returns 0 on the empty graph."""
    n, adj = g
    if n == 0:
        return 0
    order = sorted(range(n), key=lambda v: -popcount(adj[v]))
    k = max(1, clique_number(g))
    while not _interval_model_within(g, order, k):
        k += 1
    return k


def interval_thickness_events(g):
    """Interval thickness over interval models written as event words.

    An interval model up to equivalence is a word in which every vertex is
    opened once and later closed once; closed intervals u, v intersect iff
    each is opened before the other is closed. Adjacent vertices must
    intersect, so a vertex may close only once all its neighbours are open.
    The clique number is the largest number of open intervals. Minimised by
    DP over (opened, closed); used above 6 vertices, where the model search
    of `interval_thickness` is slow, and checked against it on the atlas."""
    n, adj = g
    if n == 0:
        return 0
    full = (1 << n) - 1

    @lru_cache(maxsize=None)
    def best(opened, closed):
        if closed == full:
            return 0
        res = n + 1
        live = opened & ~closed
        x = full & ~opened
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            load = popcount(live) + 1
            if load < res:
                res = min(res, max(load, best(opened | 1 << v, closed)))
        x = live
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            if not adj[v] & ~opened:
                res = min(res, best(opened, closed | 1 << v))
        return res

    return best(0, 0)


def _interval_model_within(g, order, k):
    n, adj = g
    load = [0] * n
    iv = [None] * n
    choices = [(l, r) for l in range(n) for r in range(l, n)]

    def go(i):
        if i == n:
            return True
        v = order[i]
        nbrs = [iv[u] for u in order[:i] if adj[v] >> u & 1]
        for l, r in choices:
            if any(r < a or b < l for a, b in nbrs):
                continue
            if any(load[p] >= k for p in range(l, r + 1)):
                continue
            for p in range(l, r + 1):
                load[p] += 1
            iv[v] = (l, r)
            if go(i + 1):
                return True
            for p in range(l, r + 1):
                load[p] -= 1
        iv[v] = None
        return False

    return go(0)


# ----------------------------------------------------------------------------
# Search games
# ----------------------------------------------------------------------------


def _edge_masks(g):
    n, adj = g
    es = edges_of(g)
    inc = [0] * n
    for i, (u, v) in enumerate(es):
        inc[u] |= 1 << i
        inc[v] |= 1 << i
    return es, inc


def _recontaminate(n, inc, guarded, cont):
    """Spread gas from contaminated edges through unguarded vertices: an
    unguarded vertex touching a contaminated edge contaminates all its edges
    (K&P 1985 p. 181, "a path that carries no searchers")."""
    while True:
        new = cont
        for w in range(n):
            if not guarded >> w & 1 and inc[w] & cont:
                new |= inc[w]
        if new == cont:
            return cont
        cont = new


def node_search(g, monotone=False):
    """Node search number (K&P 1985 p. 181): moves place a searcher on an
    unguarded node or remove one; an edge is cleared when both endpoints carry
    a searcher; clear edges recontaminate through searcher-free paths. The
    value is the least k such that some strategy never uses more than k
    searchers and clears every edge. With `monotone=True`, a move that
    recontaminates any edge is forbidden. 0 on edgeless graphs."""
    n, adj = g
    es, inc = _edge_masks(g)
    if not es:
        return 0
    allc = (1 << len(es)) - 1
    within = []  # edges with both ends in P, computed per P lazily
    cache = {}

    def inside(p):
        r = cache.get(p)
        if r is None:
            r = 0
            for i, (u, v) in enumerate(es):
                if p >> u & 1 and p >> v & 1:
                    r |= 1 << i
            cache[p] = r
        return r

    for k in range(1, n + 1):
        start = (0, allc)
        seen = {start}
        stack = [start]
        found = False
        while stack and not found:
            p, c = stack.pop()
            moves = []
            for v in range(n):
                if p >> v & 1:
                    moves.append(p & ~(1 << v))
                elif popcount(p) < k:
                    moves.append(p | (1 << v))
            for q in moves:
                c1 = c & ~inside(q)
                c2 = _recontaminate(n, inc, q, c1)
                if monotone and c2 & ~c:
                    continue
                if c2 == 0:
                    found = True
                    break
                s = (q, c2)
                if s not in seen:
                    seen.add(s)
                    stack.append(s)
        if found:
            return k
    raise AssertionError("n searchers always suffice")


def edge_search(g, monotone=False, kmax=None):
    """Edge search number (K&P 1986 p. 208, after Parsons): moves place a
    searcher on a vertex, remove one, or slide one along an edge. Sliding
    from u to v clears uv; clear edges recontaminate through unguarded paths
    (so a slide from an unguarded-after vertex with another contaminated edge
    is recontaminated at once, which is the source's "if all other edges
    incident on the first guarded vertex are clear" rule). Several searchers
    may share a vertex. 0 on edgeless graphs."""
    n, adj = g
    es, inc = _edge_masks(g)
    if not es:
        return 0
    allc = (1 << len(es)) - 1
    eidx = {}
    for i, (u, v) in enumerate(es):
        eidx[(u, v)] = eidx[(v, u)] = i
    kmax = kmax or len(es) + 1
    for k in range(1, kmax + 1):
        start = ((0,) * n, allc)
        seen = {start}
        stack = [start]
        found = False
        while stack and not found:
            cnt, c = stack.pop()
            total = sum(cnt)
            succ = []
            for v in range(n):
                if total < k:
                    t = list(cnt); t[v] += 1
                    succ.append((tuple(t), None))
                if cnt[v]:
                    t = list(cnt); t[v] -= 1
                    succ.append((tuple(t), None))
                    x = adj[v]
                    while x:
                        w = (x & -x).bit_length() - 1
                        x &= x - 1
                        t = list(cnt); t[v] -= 1; t[w] += 1
                        succ.append((tuple(t), eidx[(v, w)]))
            for t, e in succ:
                guarded = 0
                for v in range(n):
                    if t[v]:
                        guarded |= 1 << v
                c1 = c if e is None else c & ~(1 << e)
                c2 = _recontaminate(n, inc, guarded, c1)
                if monotone and c2 & ~c:
                    continue
                if c2 == 0:
                    found = True
                    break
                s = (t, c2)
                if s not in seen:
                    seen.add(s)
                    stack.append(s)
        if found:
            return k
    return None


def two_expansion(g):
    """EST 1994 Thm 2.2: every edge subdivided twice."""
    n, adj = g
    es = edges_of(g)
    new = []
    for i, (u, v) in enumerate(es):
        a, b = n + 2 * i, n + 2 * i + 1
        new += [(u, a), (a, b), (b, v)]
    return graph(n + 2 * len(es), new)


# ----------------------------------------------------------------------------
# Split and interval bandwidth: Fomin 1998 sec. 3
# ----------------------------------------------------------------------------


def interval_bandwidth(g, bmax=None):
    """Fomin sec. 3.1: a numbering is a surjection L: {1..N} -> V with N >= |V|
    free; g_L(u, v) is the longest open interval inside the span of
    L^-1(u) ∪ L^-1(v) that avoids it, i.e. the largest difference of
    consecutive elements of that set; ib(G, L) = max over u adjacent or equal
    to v; ib(G) = min over L.

    Decided exactly, with N unbounded, by a finite automaton read left to
    right. g_L <= b for every such pair iff (i) consecutive occurrences of a
    vertex are at most b apart and (ii) for adjacent u, v whose occurrence sets
    do not interleave, the last of one and the first of the other are at most
    b apart (any other consecutive pair of the union is bounded by (i)). Per
    vertex the state is: unseen, open (will occur again) with the age of its
    last occurrence, or closed with that age; closed vertices with no unseen
    neighbour are forgotten. A vertex is *pending* while open or while closed
    with an unseen neighbour, and a pending vertex's age must stay < b.
    """
    n, adj = g
    if n == 0:
        return 0
    bmax = bmax if bmax is not None else n
    for b in range(0, bmax + 1):
        if _ib_at_most(g, b):
            return b
    return None


def _ib_at_most(g, b):
    n, adj = g
    UNSEEN, DONE = -1, -2
    # state: tuple per vertex: UNSEEN, DONE (closed, no unseen nbr), or
    # (open_flag, age)
    start = (UNSEEN,) * n
    seen = {start}
    stack = [start]
    while stack:
        st = stack.pop()
        for x in range(n):
            sx = st[x]
            if sx == DONE or (isinstance(sx, tuple) and not sx[0]):
                continue  # closed vertices do not occur again
            for close in (False, True):
                new = list(st)
                new[x] = (not close, -1)  # age becomes 0 after the increment
                ok = True
                for u in range(n):
                    su = new[u]
                    if isinstance(su, tuple):
                        new[u] = (su[0], su[1] + 1)
                unseen = 0
                for u in range(n):
                    if new[u] == UNSEEN:
                        unseen |= 1 << u
                for u in range(n):
                    su = new[u]
                    if isinstance(su, tuple):
                        pending = su[0] or (adj[u] & unseen)
                        if not pending:
                            new[u] = DONE
                        elif su[1] >= b:
                            ok = False
                            break
                if not ok:
                    continue
                t = tuple(new)
                if all(s == DONE for s in t):
                    return True
                if t not in seen:
                    seen.add(t)
                    stack.append(t)
    return False


def node_splittings(g):
    """Fomin sec. 3.2: split v by partitioning N(v) into M and N (either may be
    empty): delete v, add u, w with the edge uw, u adjacent to M, w to N."""
    n, adj = g
    es = edges_of(g)
    for v in range(n):
        nb = [u for u in range(n) if adj[v] >> u & 1]
        for bits in range(1 << len(nb)):
            m_side = [nb[i] for i in range(len(nb)) if bits >> i & 1]
            n_side = [nb[i] for i in range(len(nb)) if not bits >> i & 1]
            # u keeps the index v, w is the new vertex n
            new = [(a, b) for a, b in es if v not in (a, b)]
            new += [(v, x) for x in m_side] + [(n, x) for x in n_side] + [(v, n)]
            yield graph(n + 1, new)


def _canon(g):
    import networkx as nx
    h = nx.Graph()
    h.add_nodes_from(range(g[0]))
    h.add_edges_from(edges_of(g))
    return nx.weisfeiler_lehman_graph_hash(h), h


def split_bandwidth_upto(g, splittings):
    """min bandwidth over G and every split with at most `splittings` node
    splittings: an upper bound on sb(G) that decreases in `splittings`."""
    import networkx as nx
    best = bandwidth(g)
    level = [g]
    seen = {}
    for _ in range(splittings):
        nxt = []
        for h in level:
            for s in node_splittings(h):
                key, hx = _canon(s)
                bucket = seen.setdefault(key, [])
                if any(nx.is_isomorphic(hx, o) for o in bucket):
                    continue
                bucket.append(hx)
                nxt.append(s)
                best = min(best, bandwidth(s))
        level = nxt
    return best


# ----------------------------------------------------------------------------
# Matrices: MOSP, gate matrix layout, PLA folding, one-dimensional logic
# ----------------------------------------------------------------------------
# A matrix is a tuple of rows; rows are piece types / customers / nets,
# columns are patterns / gates (L&Y 2002 and Mohring 1990 orientation).


def _spans(matrix, perm):
    """For a column order, each nonzero row's closed interval of positions."""
    out = []
    for row in matrix:
        pos = [i for i, c in enumerate(perm) if row[c]]
        if pos:
            out.append((pos[0], pos[-1]))
    return out


def mosp_value(matrix):
    """L&Y 2002 eqs. (1)-(2): q_ij = 1 iff piece i has patterns at or before
    and at or after position j; Z = min over orders of max_j sum_i q_ij."""
    if not matrix or not matrix[0]:
        return 0
    m = len(matrix[0])
    best = None
    for perm in itertools.permutations(range(m)):
        spans = _spans(matrix, perm)
        z = max((sum(1 for a, b in spans if a <= j <= b) for j in range(m)), default=0)
        best = z if best is None else min(best, z)
    return best


def _min_tracks(spans, cap=None):
    """Least number of tracks for the given closed intervals, each track
    holding pairwise disjoint intervals and at most `cap` of them."""
    k = len(spans)
    if k == 0:
        return 0
    order = sorted(range(k), key=lambda i: spans[i])
    best = k
    tracks = []

    def go(i):
        nonlocal best
        if len(tracks) >= best:
            return
        if i == k:
            best = len(tracks)
            return
        a, b = spans[order[i]]
        for t in tracks:
            if (cap is None or len(t) < cap) and all(bb < a or b < aa for aa, bb in t):
                t.append((a, b))
                go(i + 1)
                t.pop()
        tracks.append([(a, b)])
        go(i + 1)
        tracks.pop()

    go(0)
    return best


def gate_matrix_tracks(matrix, cap=None, fixed_ends=None):
    """Mohring's MPP (p. 18): over column permutations, assign the augmented
    rows (nets) to tracks, nets on a track sharing no gate; `cap=2` is
    PLAMPP (p. 25). `fixed_ends=(l, r)` pins two columns to the two ends
    (Ohtsuki et al. sec. IV)."""
    if not matrix or not matrix[0]:
        return 0
    m = len(matrix[0])
    cols = list(range(m))
    if fixed_ends is not None:
        l, r = fixed_ends
        inner = [c for c in cols if c not in (l, r)]
        perms = ((l, *p, r) for p in itertools.permutations(inner))
    else:
        perms = itertools.permutations(cols)
    return min(_min_tracks(_spans(matrix, p), cap) for p in perms)


def pla_folding_tracks(matrix):
    return gate_matrix_tracks(matrix, cap=2)


def one_dim_logic_tracks(matrix, boundary=None):
    """Ohtsuki et al. 1979 sec. II: nets are rows, gates columns, |V(t)| >= 1
    and |T(v)| >= 2 (eqs. 3-4); tracks = chromatic number of the interval
    graph of the placement, minimised over placements. `boundary=(l, r)`
    fixes the boundary gates at the ends (sec. IV, with V(t_l) ∩ V(t_r) = ∅)."""
    assert all(any(r[c] for r in matrix) for c in range(len(matrix[0]))), "|V(t)| >= 1"
    assert all(sum(r) >= 2 for r in matrix), "|T(v)| >= 2"
    return gate_matrix_tracks(matrix, fixed_ends=boundary)


def row_graph(matrix, columns=None):
    """The MOSP graph / net adjacency graph / connection graph: rows adjacent
    iff some column (among `columns`, default all) holds both."""
    k = len(matrix)
    cols = range(len(matrix[0])) if columns is None else columns
    es = [(i, j) for i in range(k) for j in range(i + 1, k)
          if any(matrix[i][c] and matrix[j][c] for c in cols)]
    return graph(k, es)


def boundary_family(k):
    """Item 01's family: nets a_i on t_l, b_i on t_r, inner gate {a_i, b_i}.
    Columns: 0 = t_l, 1..k inner, k+1 = t_r; rows a_1..a_k, b_1..b_k."""
    rows = []
    for i in range(k):
        r = [0] * (k + 2); r[0] = 1; r[1 + i] = 1; rows.append(tuple(r))
    for i in range(k):
        r = [0] * (k + 2); r[k + 1] = 1; r[1 + i] = 1; rows.append(tuple(r))
    return tuple(rows)


def boundary_path_instance():
    """Nets a, b, c, d, e (rows 0-4) with connection graph the path
    a-b-c-d-e; t_l = {c} (column 0), t_r = {a} (column 6), inner gates
    {a,b}, {b,c}, {c,d}, {d,e}, {e}. Pinning c's interval to the left end and
    a's to the right end forces three tracks against pw + 1 = 2."""
    cols = [{2}, {0, 1}, {1, 2}, {2, 3}, {3, 4}, {4}, {0}]
    return tuple(tuple(int(r in c) for c in cols) for r in range(5)), (0, 6)


def ohtsuki_boundary_row(matrix, lr):
    """Sec. IV: tracks with t_l, t_r pinned, against the free problem and the
    connection graph over all gates (eq. (6) ranges over all of T)."""
    tb = one_dim_logic_tracks(matrix, boundary=lr)
    h = row_graph(matrix)
    return dict(tracks_boundary=tb, tracks_free=one_dim_logic_tracks(matrix), pw1=pathwidth(h) + 1)


def _is_ohtsuki(matrix):
    return (all(any(row[c] for row in matrix) for c in range(len(matrix[0])))
            and all(sum(row) >= 2 for row in matrix))


def _boundary_task(args):
    matrix, lr = args
    r = ohtsuki_boundary_row(matrix, lr)
    r["matrix"], r["lr"] = matrix, lr
    return r


def identity_matrix(k):
    return tuple(tuple(int(i == j) for j in range(k)) for i in range(k))


def incidence_matrix(g):
    """Vertex-edge incidence: the MOSP instance whose MOSP graph is G."""
    n, _ = g
    es = edges_of(g)
    return tuple(tuple(int(v in e) for e in es) for v in range(n))


# ----------------------------------------------------------------------------
# Lengauer's constructions
# ----------------------------------------------------------------------------


def lengauer_du(g):
    """Thm 4: G_du adds, for every edge, a new vertex adjacent to both ends."""
    n, adj = g
    es = edges_of(g)
    new = list(es)
    for i, (u, v) in enumerate(es):
        new += [(u, n + i), (v, n + i)]
    return graph(n + len(es), new)


def lengauer_blowup(g):
    """Thm 7: v_i becomes the (N + 1)-clique {v_i(j) : 0 <= j <= N}, and each
    edge v_i v_j becomes the single edge v_i(j) v_j(i) (1-based i, j)."""
    n, _ = g
    N = n
    idx = lambda i, j: i * (N + 1) + j  # i 0-based, j in 0..N
    new = []
    for i in range(n):
        new += [(idx(i, a), idx(i, b)) for a, b in itertools.combinations(range(N + 1), 2)]
    for i, j in edges_of(g):
        new.append((idx(i, j + 1), idx(j, i + 1)))
    return graph(n * (N + 1), new)


# ----------------------------------------------------------------------------
# Pebbling (loop0006 item 02): equivalences.md, section "Pebbling", P.1-P.5
# ----------------------------------------------------------------------------
#
# Dags are `(n, pred)` with `pred[v]` the bitmask of immediate predecessors of
# `v` (Lengauer p. 466 footnote 1: v0 is an immediate predecessor of v1 when
# (v0, v1) is an edge). Every game is decided for a pebble budget `k` by an
# exhaustive search over the reachable positions that never hold more than `k`
# pebbles; the demand is the least `k` that reaches the final position. That
# positivity is monotone in `k` is immediate (a play within k is within k + 1),
# so the instance forms of the theorems are read off the demand.


def dag(n, arcs):
    """`(n, pred)` from arcs `(u, v)`: `u` an immediate predecessor of `v`."""
    pred = [0] * n
    for u, v in arcs:
        if u == v:
            raise ValueError("loops are not dags")
        pred[v] |= 1 << u
    d = (n, tuple(pred))
    if topological_order(d) is None:
        raise ValueError("not acyclic")
    return d


def arcs_of(d):
    n, pred = d
    return [(u, v) for v in range(n) for u in range(n) if pred[v] >> u & 1]


def topological_order(d):
    n, pred = d
    order, placed = [], 0
    while len(order) < n:
        ready = [v for v in range(n) if not placed >> v & 1 and pred[v] & ~placed == 0]
        if not ready:
            return None
        for v in ready:
            order.append(v)
            placed |= 1 << v
    return order


def underlying(d):
    return graph(d[0], arcs_of(d))


def lengauer_u(d):
    """Lengauer Def. 1a (p. 468): the arcs undirected, plus a clique on the
    immediate predecessors of every vertex."""
    n, pred = d
    es = set()
    for v in range(n):
        ps = [u for u in range(n) if pred[v] >> u & 1]
        es.update((min(u, v), max(u, v)) for u in ps)
        es.update(itertools.combinations(ps, 2))
    return graph(n, sorted(es))


def lengauer_d(g):
    """Lengauer Def. 1b (p. 469): `V_d = V u E`, arcs `v -> {v, w}` and
    `w -> {v, w}`. Vertex `n + i` is the i-th edge of `edges_of(g)`, the
    numbering `lengauer_du` uses, so `lengauer_u(lengauer_d(g)) ==
    lengauer_du(g)` literally."""
    n, _ = g
    es = edges_of(g)
    return (n + len(es), tuple([0] * n + [(1 << u) | (1 << v) for u, v in es]))


def orient(g, order):
    """The directive of `g` with every edge pointing to its later end in `order`."""
    n, adj = g
    pos = {v: i for i, v in enumerate(order)}
    return (n, tuple(sum(1 << u for u in range(n) if adj[v] >> u & 1 and pos[u] < pos[v])
                     for v in range(n)))


def acyclic_orientations(g):
    """Every directive of `g` (KP p. 213), each once: an acyclic orientation
    is induced by a topological order, so orient along every permutation."""
    return sorted({orient(g, p) for p in itertools.permutations(range(g[0]))})


def pebble_matrix(d):
    """The MOSP instance of P.2: a row per vertex, a column per vertex, row u
    of column v set iff u is in N^-[v] = {v} u pred(v)."""
    n, pred = d
    return tuple(tuple(int(u == v or bool(pred[v] >> u & 1)) for v in range(n)) for u in range(n))


def _search(start, moves, final):
    seen = {start}
    stack = [start]
    while stack:
        s = stack.pop()
        for t in moves(s):
            if t == final:
                return True
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return start == final


def progressive_bw_within(d, k, rules="lengauer"):
    """Can `d` be pebbled in the progressive black-white game with at most `k`
    pebbles at any instant?

    `rules="lengauer"`: Lengauer p. 466-467, rules (i), (ii), (iii'), (iv),
    (v), (vi): place a white pebble on a pebble-free vertex; remove a black
    pebble; a white pebble *may* be turned black when every immediate
    predecessor is pebbled; each vertex receives and loses a pebble exactly
    once. `rules="kp"`: Kirousis & Papadimitriou p. 205-206, where a white
    pebble turns black *at the moment* its predecessors are all pebbled (a
    black placement is a white one that turns at once). A position is
    `(white, black, done)`, `done` the vertices that have received and lost
    their one pebble."""
    n, pred = d
    full = (1 << n) - 1
    auto = rules == "kp"
    if rules not in ("lengauer", "kp"):
        raise ValueError(rules)

    def turn_all(w, b):
        peb = w | b
        x = w
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            if pred[v] & ~peb == 0:
                w &= ~(1 << v)
                b |= 1 << v
        return w, b

    def moves(s):
        w, b, done = s
        peb = w | b
        if popcount(peb) < k:
            x = full & ~(peb | done)
            while x:
                v = (x & -x).bit_length() - 1
                x &= x - 1
                w2 = w | 1 << v
                yield turn_all(w2, b) + (done,) if auto else (w2, b, done)
        if not auto:
            x = w
            while x:
                v = (x & -x).bit_length() - 1
                x &= x - 1
                if pred[v] & ~peb == 0:
                    yield (w & ~(1 << v), b | 1 << v, done)
        x = b
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            yield (w, b & ~(1 << v), done | 1 << v)

    return _search((0, 0, 0), moves, (0, 0, full))


def progressive_black_within(d, k):
    """KP p. 205-206, progressive: a pebble may be placed on a vertex only if
    all its immediate predecessors are pebbled, removed at any time, and each
    vertex is pebbled exactly once. Position `(pebbled, done)`."""
    n, pred = d
    full = (1 << n) - 1

    def moves(s):
        b, done = s
        if popcount(b) < k:
            x = full & ~(b | done)
            while x:
                v = (x & -x).bit_length() - 1
                x &= x - 1
                if pred[v] & ~b == 0:
                    yield (b | 1 << v, done)
        x = b
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            yield (b & ~(1 << v), done | 1 << v)

    return _search((0, 0), moves, (0, full))


def unrestricted_bw_within(d, k):
    """Lengauer's BWP (p. 466) with rule (iii), "at least once": a white pebble
    on any pebble-free vertex, including one pebbled before. Position
    `(white, black, received)`; the game ends pebble-free with every vertex
    received, and since it ends pebble-free every received pebble was lost."""
    n, pred = d
    full = (1 << n) - 1

    def moves(s):
        w, b, rec = s
        peb = w | b
        if popcount(peb) < k:
            x = full & ~peb
            while x:
                v = (x & -x).bit_length() - 1
                x &= x - 1
                yield (w | 1 << v, b, rec | 1 << v)
        x = w
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            if pred[v] & ~peb == 0:
                yield (w & ~(1 << v), b | 1 << v, rec)
        x = b
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            yield (w, b & ~(1 << v), rec)

    return _search((0, 0, 0), moves, (0, 0, full))


def unrestricted_black_within(d, k):
    """KP's black pebble game (p. 205), repebbling allowed."""
    n, pred = d
    full = (1 << n) - 1

    def moves(s):
        b, rec = s
        if popcount(b) < k:
            x = full & ~b
            while x:
                v = (x & -x).bit_length() - 1
                x &= x - 1
                if pred[v] & ~b == 0:
                    yield (b | 1 << v, rec | 1 << v)
        x = b
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            yield (b & ~(1 << v), rec)

    return _search((0, 0), moves, (0, full))


def _demand(d, within, lo=1):
    """Least `k >= lo` with `within(d, k)`; 0 on the empty dag (KP's demand;
    Lengauer's positive-K number is `max(1, .)`)."""
    n, _ = d
    if n == 0:
        return 0
    for k in range(lo, n + 1):
        if within(d, k):
            return k
    raise AssertionError("n pebbles always suffice")


def pbw(d, rules="kp", lo=1):
    return _demand(d, lambda d, k: progressive_bw_within(d, k, rules), lo)


def pb(d, lo=1):
    return _demand(d, progressive_black_within, lo)


def bw_unrestricted(d, lo=1):
    return _demand(d, unrestricted_bw_within, lo)


def black_unrestricted(d, lo=1):
    return _demand(d, unrestricted_black_within, lo)


def mpb_mpbw(g):
    """KP p. 213: the least progressive black and black-white demand over all
    directives of `g`."""
    ds = acyclic_orientations(g)
    return min(pb(d) for d in ds), min(pbw(d) for d in ds)


def is_chordal(g):
    """Every cycle of length >= 4 has a chord: repeatedly delete a simplicial
    vertex (its neighbourhood a clique)."""
    n, adj = g
    alive = (1 << n) - 1
    while alive:
        for v in range(n):
            if alive >> v & 1:
                nb = adj[v] & alive
                ok = True
                x = nb
                while x and ok:
                    u = (x & -x).bit_length() - 1
                    x &= x - 1
                    if nb & ~adj[u] & ~(1 << u):
                        ok = False
                if ok:
                    alive &= ~(1 << v)
                    break
        else:
            return False
    return True


def repebble_play_lemma(d):
    """KP's recontamination claim (P.3, 'On the proof'): in every position of
    a progressive black-white play (Lengauer's rules, no budget) from which
    the play can still be completed, a vertex that has lost its pebble has
    every neighbour (predecessor or successor) already pebbled or done.
    Returns the number of such positions checked, or raises on a violation."""
    n, pred = d
    full = (1 << n) - 1
    adj = underlying(d)[1]
    # forward: all reachable positions and arcs
    start = (0, 0, 0)
    succ = {}
    stack = [start]
    succ[start] = None
    order = []
    while stack:
        s = stack.pop()
        order.append(s)
        w, b, done = s
        peb = w | b
        out = []
        x = full & ~(peb | done)
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            out.append((w | 1 << v, b, done))
        x = w
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            if pred[v] & ~peb == 0:
                out.append((w & ~(1 << v), b | 1 << v, done))
        x = b
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            out.append((w, b & ~(1 << v), done | 1 << v))
        succ[s] = out
        for t in out:
            if t not in succ:
                succ[t] = None
                stack.append(t)
    rev = {}
    for s, out in succ.items():
        for t in out or ():
            rev.setdefault(t, []).append(s)
    final = (0, 0, full)
    live = {final}
    stack = [final]
    while stack:
        t = stack.pop()
        for s in rev.get(t, ()):
            if s not in live:
                live.add(s)
                stack.append(s)
    for w, b, done in live:
        rec = w | b | done
        x = done
        while x:
            v = (x & -x).bit_length() - 1
            x &= x - 1
            if adj[v] & ~rec:
                raise AssertionError(("lemma fails", d, (w, b, done)))
    return len(live)


def ternary_tree(h):
    """KP Prop. 3.2's complete ternary tree of height `h`, directed from the
    root (vertex 0) towards the leaves; vertex i's children are 3i+1..3i+3."""
    n = (3 ** (h + 1) - 1) // 2
    return dag(n, [((c - 1) // 3, c) for c in range(1, n)])


def rooted_trees(n):
    """Every tree on `n` vertices up to isomorphism, with every root, as
    `(in_tree, out_tree)` pairs: arcs towards and away from the root."""
    import networkx as nx
    out = []
    trees = [nx.empty_graph(1)] if n == 1 else list(nx.nonisomorphic_trees(n))
    for t in trees:
        for r in range(n):
            parent = dict(nx.bfs_predecessors(t, r))
            arcs = [(parent[c], c) for c in parent]
            out.append((dag(n, [(v, u) for u, v in arcs]), dag(n, arcs)))
    return out


def dag_row(d, rules_both=True, matrix=True):
    """Every pebbling quantity of P.5 statements 1-3 on one dag."""
    n, pred = d
    du = lengauer_u(d)
    r = dict(n=n, arcs=arcs_of(d), m=len(arcs_of(d)))
    r["pbw_kp"] = pbw(d, "kp")
    r["pbw_lengauer"] = pbw(d, "lengauer") if rules_both else None
    r["pb"] = pb(d)
    r["vs_du"] = vs_dp(du)
    r["vsg_du"] = vsg(du) if n <= 6 else None
    r["Z"] = mosp_value(pebble_matrix(d)) if matrix and n else None
    r["mosp_graph_is_du"] = row_graph(pebble_matrix(d)) == du if n else True
    return r


def dag_checks(r):
    out = []
    n, m = r["n"], r["m"]

    def chk(name, ok, applies=True):
        if applies:
            out.append((name, bool(ok)))

    chk("P1 Lengauer rules = KP rules (pbw)", r["pbw_kp"] == r["pbw_lengauer"],
        r["pbw_lengauer"] is not None)
    chk("P1 pbw <= pb", r["pbw_kp"] <= r["pb"])
    chk("P2 pbw(D) = vs(D_u) + 1 (nonempty)", r["pbw_kp"] == r["vs_du"] + 1, n >= 1)
    # instance forms, K = 1 .. n + 1: (D, K) positive iff pbw <= K
    if n >= 1:
        vs_form = all((r["pbw_kp"] <= K) == (r["vs_du"] <= K - 1) for K in range(1, n + 2))
        chk("P2 instance form with vs holds for every K >= 1", vs_form)
        if r["vsg_du"] is not None:
            fails = [K for K in range(1, n + 2)
                     if (r["pbw_kp"] <= K) != (K - 1 >= 1 and r["vsg_du"] <= K - 1)]
            chk("P2 instance form with VSG fails exactly at K = 1 on edgeless D",
                fails == ([1] if m == 0 else []))
            chk("P2 pbw = VSG(D_u) + 1 (D with an arc)", r["pbw_kp"] == r["vsg_du"] + 1, m > 0)
    chk("P3 pbw(D) = Z(M_D) (nonempty)", r["pbw_kp"] == r["Z"], n >= 1 and r["Z"] is not None)
    chk("P3 the MOSP graph of M_D is D_u", r["mosp_graph_is_du"])
    return out


def gd_row(g, exact_unrestricted=True):
    """P.5 statements 4 and 7 on one graph: pbw(G_d) against vs(G), and the
    unrestricted games on G_d."""
    n, _ = g
    gd = lengauer_d(g)
    m = len(edges_of(g))
    r = dict(n=n, m=m, edges=edges_of(g))
    r["vs"] = vs_dp(g)
    r["vsg"] = vsg(g) if n <= 7 else None
    r["pbw_gd"] = pbw(gd, "kp", lo=max(1, r["vs"] + 1))
    # the lo shortcut is only sound if pbw > vs + 1 - 1; check it explicitly
    r["pbw_gd_below"] = progressive_bw_within(gd, r["pbw_gd"] - 1, "kp") if r["pbw_gd"] > 1 else False
    r["du_is_triangle"] = lengauer_u(gd) == lengauer_du(g)
    r["bw_gd"] = bw_unrestricted(gd) if exact_unrestricted else None
    r["b_gd"] = black_unrestricted(gd) if exact_unrestricted else None
    return r


def gd_checks(r):
    out = []
    n, m = r["n"], r["m"]

    def chk(name, ok, applies=True):
        if applies:
            out.append((name, bool(ok)))

    chk("P4 pbw(G_d) is exact (not within one pebble less)", not r["pbw_gd_below"])
    chk("P4 (G_d)_u = G_du (Lengauer Thm 4's triangle graph)", r["du_is_triangle"])
    chk("P4 pbw(G_d) = vs(G) + 2 (G with an edge)", r["pbw_gd"] == r["vs"] + 2, m > 0)
    chk("P4 pbw(G_d) = 1 (G edgeless, nonempty)", r["pbw_gd"] == 1, m == 0 and n >= 1)
    chk("P4 vs(G) <= K iff pbw(G_d) <= K + 2, every K >= 0",
        all((r["vs"] <= K) == (r["pbw_gd"] <= K + 2) for K in range(0, n + m + 2)), n >= 1)
    if r["vsg"] is not None:
        chk("P4 Thm 3 as stated (VSG, K >= 1)",
            all((K >= max(1, r["vsg"])) == (r["pbw_gd"] <= K + 2) for K in range(1, n + m + 2)), n >= 1)
    if r["bw_gd"] is not None:
        chk("P7 unrestricted BWP on G_d <= 3", r["bw_gd"] <= 3, n >= 1)
        chk("P7 black pebble game on G_d <= 3", r["b_gd"] <= 3, n >= 1)
    return out


def directive_row(g):
    """P.5 statements 5 and 6 on one undirected graph."""
    n, _ = g
    ds = acyclic_orientations(g)
    r = dict(n=n, m=len(edges_of(g)), edges=edges_of(g), directives=len(ds))
    r["vs"] = vs_dp(g)
    r["ns"] = node_search(g) if n <= 6 else None
    r["mpb"] = min(pb(d) for d in ds)
    r["mpbw"] = min(pbw(d) for d in ds)
    r["chordal"] = is_chordal(g)
    r["is_some_du"] = any(lengauer_u(d) == g for d in ds)
    r["min_vs_du"] = min(vs_dp(lengauer_u(d)) for d in ds)
    best = min(itertools.permutations(range(n)), key=lambda p: vs_of_layout(g, p))
    lay = orient(g, best)
    r["vs_du_layout"] = vs_dp(lengauer_u(lay))
    r["pb_layout"] = pb(lay)
    return r


def directive_checks(r):
    out = []
    n, m = r["n"], r["m"]

    def chk(name, ok, applies=True):
        if applies:
            out.append((name, bool(ok)))

    chk("P5 mpb = vs + 1 (nonempty)", r["mpb"] == r["vs"] + 1, n >= 1)
    chk("P5 mpbw = vs + 1 (nonempty)", r["mpbw"] == r["vs"] + 1, n >= 1)
    if r["ns"] is not None:
        chk("P5 mpb = ns = mpbw (KP Thm 3.1; G with an edge)", r["mpb"] == r["ns"] == r["mpbw"], m > 0)
        chk("P5 ns = 0 != mpb = 1 (edgeless, nonempty)", r["ns"] == 0 and r["mpb"] == 1, m == 0 and n >= 1)
    chk("P5 the optimal-layout directive attains mpb", r["pb_layout"] == r["mpb"], n >= 1)
    chk("P6 G is some D_u iff G is chordal", r["is_some_du"] == r["chordal"])
    chk("P6 min over directives of vs(D_u) = vs(G)", r["min_vs_du"] == r["vs"])
    chk("P6 the optimal-layout directive attains vs(D_u) = vs(G)", r["vs_du_layout"] == r["vs"])
    return out


def tree_row(pair):
    """P.5 statement 8 on one rooted tree, in both directions."""
    tin, tout = pair
    r = dict(n=tin[0], arcs_in=arcs_of(tin))
    for name, d in (("in", tin), ("out", tout)):
        r[f"pbw_{name}"] = pbw(d, "kp")
        r[f"bw_{name}"] = bw_unrestricted(d)
        r[f"pb_{name}"] = pb(d)
        r[f"b_{name}"] = black_unrestricted(d)
    return r


def tree_checks(r):
    return [("P8 in-trees: BWP = PBWP (Lengauer p. 467)", r["bw_in"] == r["pbw_in"]),
            ("P8 in-trees: black game, repebbling = progressive", r["b_in"] == r["pb_in"])]


def _all_dags(n):
    """Every dag on `0..n-1` with arcs `i -> j` only for `i < j`: every dag on
    n vertices up to isomorphism, with repetition."""
    pairs = list(itertools.combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        pred = [0] * n
        for i, (u, v) in enumerate(pairs):
            if bits >> i & 1:
                pred[v] |= 1 << u
        yield (n, tuple(pred))


def _dag_task(d):
    return dag_row(d)


def _gd_task(g):
    return gd_row(g)


def run_pebbling(quick=False, workers=None, seed=20260930, out=PEBBLING_REPORT):
    """Every statement of P.5, exhaustively on small inputs."""
    from networkx.generators.atlas import graph_atlas_g

    t0 = time.time()
    summary, counterexamples, stats = {}, {}, {}

    def record(checks, witness):
        for name, ok in checks:
            s = summary.setdefault(name, [0, 0])
            s[0] += 1
            if not ok:
                s[1] += 1
                if len(counterexamples.setdefault(name, [])) < 5:
                    counterexamples[name].append(witness)

    dag_max = 5 if quick else 6
    dag_sample = (7, 200 if quick else 20000)  # random dags on 7 vertices
    gd_bound = 7 if quick else 14
    atlas_dir = 5 if quick else 7
    tree_max = 6 if quick else 11
    rng = random.Random(seed)
    with Pool(workers) as pool:
        # statements 1-3: every dag i -> j (i < j) on <= dag_max vertices
        t = time.time()
        dags = [d for n in range(0, dag_max + 1) for d in _all_dags(n)]
        stats["dags_exhaustive"] = len(dags)
        n7, count = dag_sample
        pairs7 = list(itertools.combinations(range(n7), 2))
        for _ in range(count):
            p = rng.choice([0.2, 0.35, 0.5, 0.65, 0.8])
            dags.append(dag(n7, [e for e in pairs7 if rng.random() < p]))
        for r in pool.imap_unordered(_dag_task, dags, chunksize=64):
            record(dag_checks(r), {"n": r["n"], "arcs": r["arcs"]})
        stats["dags"] = len(dags)
        stats["dag_seconds"] = round(time.time() - t, 1)
        # statements 4 and 7: G_d for every atlas graph with |V| + |E| <= gd_bound
        t = time.time()
        gs = [from_nx(h) for h in graph_atlas_g()
              if h.number_of_nodes() >= 1 and h.number_of_nodes() + h.number_of_edges() <= gd_bound]
        for r in pool.imap_unordered(_gd_task, gs, chunksize=1):
            record(gd_checks(r), {"n": r["n"], "edges": r["edges"]})
        stats["gd_graphs"] = len(gs)
        stats["gd_bound_V_plus_E"] = gd_bound
        stats["gd_seconds"] = round(time.time() - t, 1)
        # statements 5 and 6: every atlas graph on 1..atlas_dir vertices, all directives
        t = time.time()
        gs = [from_nx(h) for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= atlas_dir]
        chordal_mismatch = 0
        import networkx as nx
        for h, r in zip((h for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= atlas_dir),
                        pool.imap(directive_row, gs, chunksize=1)):
            record(directive_checks(r), {"n": r["n"], "edges": r["edges"]})
            chordal_mismatch += r["chordal"] != nx.is_chordal(h)
        stats["directive_graphs"] = len(gs)
        stats["is_chordal_vs_networkx_mismatches"] = chordal_mismatch
        stats["directive_seconds"] = round(time.time() - t, 1)
        # statement 8: every rooted tree on <= tree_max vertices, both directions
        t = time.time()
        pairs = [p for n in range(1, tree_max + 1) for p in rooted_trees(n)]
        out_gap = {}
        out_examples = []
        for r in pool.imap_unordered(tree_row, pairs, chunksize=4):
            record(tree_checks(r), {"n": r["n"], "arcs_in": r["arcs_in"]})
            gap = r["pbw_out"] - r["bw_out"]
            out_gap[gap] = out_gap.get(gap, 0) + 1
            if gap > 0 and len(out_examples) < 3:
                out_examples.append({k: r[k] for k in ("n", "arcs_in", "pbw_out", "bw_out", "pb_out", "b_out")})
        stats["rooted_trees"] = len(pairs)
        stats["tree_seconds"] = round(time.time() - t, 1)

    # the recontamination lemma of P.3, on every dag of <= 4 vertices (all plays)
    t = time.time()
    lemma_positions = 0
    lemma_max = 4 if quick else 5
    for n in range(1, lemma_max + 1):
        for d in _all_dags(n):
            lemma_positions += repebble_play_lemma(d)
    stats["lemma_dags_max_n"] = lemma_max
    stats["lemma_live_positions"] = lemma_positions
    stats["lemma_seconds"] = round(time.time() - t, 1)

    # named instances
    named = {}
    for name, g in (("K2", complete_graph(2)), ("K3", complete_graph(3)), ("K4", complete_graph(4)),
                    ("P4", path_graph(4)), ("C4", cycle_graph(4)), ("K1,3", star_graph(3))):
        if quick and g[0] + len(edges_of(g)) > 7:
            continue
        gd = lengauer_d(g)
        named[f"G_d of {name}"] = {"|V_d|": gd[0], "vs(G)": vs_dp(g), "pbw(G_d)": pbw(gd),
                                   "bw(G_d)": bw_unrestricted(gd), "b(G_d)": black_unrestricted(gd),
                                   "pb(G_d)": pb(gd)}
    heights = (1,) if quick else (1, 2)
    for h in heights:
        tt = ternary_tree(h)
        named[f"ternary out-tree, height {h}"] = {
            "n": tt[0], "pbw": pbw(tt), "pb": pb(tt), "bw": bw_unrestricted(tt),
            "b": black_unrestricted(tt), "pw(tree)": vs_dp(underlying(tt)) if tt[0] <= 13 else None}
        rev = dag(tt[0], [(v, u) for u, v in arcs_of(tt)])
        named[f"ternary in-tree, height {h}"] = {
            "n": rev[0], "pbw": pbw(rev), "pb": pb(rev), "bw": bw_unrestricted(rev),
            "b": black_unrestricted(rev)}
    star_in = dag(5, [(i, 0) for i in range(1, 5)])
    named["K1,4, every edge to the centre (KP p. 214)"] = {
        "pbw": pbw(star_in), "pb": pb(star_in), "bw": bw_unrestricted(star_in),
        "b": black_unrestricted(star_in), "mpb": mpb_mpbw(star_graph(4))[0]}

    report = {
        "stats": stats,
        "summary": {k: {"checked": v[0], "failed": v[1]} for k, v in sorted(summary.items())},
        "counterexamples": counterexamples,
        "out_trees_by_pbw_minus_bw": {str(k): v for k, v in sorted(out_gap.items())},
        "out_tree_examples": out_examples,
        "named": named,
        "seconds": round(time.time() - t0, 1), "quick": quick, "seed": seed,
    }
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, default=list))
    return report


# ----------------------------------------------------------------------------
# The checks
# ----------------------------------------------------------------------------


def graph_row(g, games=True, heavy=True):
    """Every graph quantity on one graph."""
    n, _ = g
    m = len(edges_of(g))
    r = dict(n=n, m=m, edges=edges_of(g), connected=is_connected(g))
    r["pw"] = pathwidth(g)
    r["vs"] = vertex_separation(g)
    r["vsg"] = vsg(g)
    r["nu"] = narrowness(g)
    r["nu_out"] = out_narrowness(g) if n <= 6 else None
    r["theta"] = interval_thickness(g) if n <= 6 else None
    r["theta_events"] = interval_thickness_events(g)
    r["cw"] = cutwidth(g)
    r["mcw"] = modified_cutwidth(g)
    r["bw"] = bandwidth(g)
    r["ib"] = interval_bandwidth(g) if r["connected"] and n >= 2 else None
    if games:
        r["ns"] = node_search(g)
        r["ns_mono"] = node_search(g, monotone=True)
        if m <= 20:
            r["es"] = edge_search(g)
            r["es_mono"] = edge_search(g, monotone=True)
        else:
            r["es"] = r["es_mono"] = None
    if n + 2 * m <= 18:
        r["vs_2exp"] = vs_dp(two_expansion(g))
    else:
        r["vs_2exp"] = None
    if m and n + m <= 16:
        r["vs_du"] = vs_dp(lengauer_du(g))
    else:
        r["vs_du"] = None
    return r


def _graph_row_task(args):
    g, games, heavy = args
    return graph_row(g, games, heavy)


def graph_checks(r):
    """Each item-01 statement on one graph row: a list of (statement, ok)."""
    out = []
    n, m, pw = r["n"], r["m"], r["pw"]

    def chk(name, ok, applies=True):
        if applies:
            out.append((name, bool(ok)))

    chk("S9 vs = pw", r["vs"] == pw)
    chk("S9 VSG = vs (graphs with an edge)", r["vsg"] == r["vs"], m > 0)
    chk("S4 theta = pw + 1 (>= 1 vertex; model search, n <= 6)", r["theta"] == pw + 1,
        n >= 1 and r["theta"] is not None)
    chk("S4 theta = pw + 1 (>= 1 vertex; event words)", r["theta_events"] == pw + 1, n >= 1)
    chk("S4 the two interval-thickness searches agree", r["theta"] == r["theta_events"],
        r["theta"] is not None)
    chk("S7 nu = pw + 1 (>= 1 vertex)", r["nu"] == pw + 1, n >= 1)
    chk("S7 in- and out-narrowness agree", r["nu"] == r["nu_out"], r["nu_out"] is not None)
    if "ns" in r:
        chk("S5 ns = vs + 1 (>= 1 edge)", r["ns"] == r["vs"] + 1, m > 0)
        chk("S5 ns = theta (>= 1 edge)", r["ns"] == r["theta_events"], m > 0)
        chk("S5 monotone ns = ns", r["ns_mono"] == r["ns"])
        chk("S5 ns = 0 on edgeless graphs", r["ns"] == 0, m == 0)
        if r.get("es") is not None:
            chk("S6 vs <= es <= vs + 2", r["vs"] <= r["es"] <= r["vs"] + 2)
            chk("S6 ns - 1 <= es <= ns + 1", r["ns"] - 1 <= r["es"] <= r["ns"] + 1)
            chk("S6 monotone es = es", r["es_mono"] == r["es"])
            chk("S6 es = vs(2-expansion)", r["es"] == r["vs_2exp"], r["vs_2exp"] is not None)
    if r["ib"] is not None:
        chk("S8 pw <= ib <= pw + 1 (connected, >= 2 vertices)", pw <= r["ib"] <= pw + 1)
        chk("S8 ib <= bandwidth", r["ib"] <= r["bw"])
    chk("S10 vs(G_du) = vs + 1 (>= 1 edge)", r["vs_du"] == r["vs"] + 1, r["vs_du"] is not None)
    chk("S11 vs <= cw", r["vs"] <= r["cw"])
    chk("S11 vs <= mcw + 1", r["vs"] <= r["mcw"] + 1)
    chk("S11 cw within 1 of pw + 1", abs(r["cw"] - (pw + 1)) <= 1, m > 0)
    chk("S11 mcw within 1 of pw + 1", abs(r["mcw"] - (pw + 1)) <= 1, m > 0)
    return out


def matrix_row(matrix):
    z = mosp_value(matrix)
    t = gate_matrix_tracks(matrix)
    pla = pla_folding_tracks(matrix)
    g = row_graph(matrix)
    pw = pathwidth(g)
    nets = sum(1 for r in matrix if any(r))
    return dict(matrix=matrix, Z=z, t=t, pla=pla, pw=pw, nets=nets,
                has_one=any(any(r) for r in matrix))


def matrix_checks(r):
    out = [("S1 Z = t (gate matrix layout)", r["Z"] == r["t"]),
           ("S3 multiple folding (= t) = pw + 1 when M has a 1", (not r["has_one"]) or r["t"] == r["pw"] + 1),
           ("S1 Z = pw(G_M) + 1 when M has a 1", (not r["has_one"]) or r["Z"] == r["pw"] + 1),
           ("S3 PLA >= max(pw + 1, ceil(nets / 2))",
            (not r["has_one"]) or r["pla"] >= max(r["pw"] + 1, -(-r["nets"] // 2))),
           ("S3 PLA within 1 of pw + 1", (not r["has_one"]) or abs(r["pla"] - (r["pw"] + 1)) <= 1)]
    return out


def ohtsuki_row(matrix):
    """One-dimensional logic on an Ohtsuki instance (every gate nonempty,
    every net on >= 2 gates); the connection graph is the row graph."""
    tracks = one_dim_logic_tracks(matrix)
    h = row_graph(matrix)
    return dict(tracks=tracks, pw=pathwidth(h), theta=interval_thickness(h))


def _matrix_task(matrix):
    r = matrix_row(matrix)
    ohtsuki = (all(any(row[c] for row in matrix) for c in range(len(matrix[0])))
               and all(sum(row) >= 2 for row in matrix))
    if ohtsuki:
        o = ohtsuki_row(matrix)
        r["ohtsuki"] = o
    return r


def _all_matrices(k, m):
    for bits in range(1 << (k * m)):
        yield tuple(tuple(bits >> (i * m + j) & 1 for j in range(m)) for i in range(k))


def _canonical_matrix(mx):
    """Canonical up to row and column permutations (small matrices only)."""
    k, m = len(mx), len(mx[0])
    best = None
    for cp in itertools.permutations(range(m)):
        rows = sorted(tuple(r[c] for c in cp) for r in mx)
        t = tuple(rows)
        if best is None or t < best:
            best = t
    return best


def _named_graphs():
    return {
        "P4": path_graph(4), "P6": path_graph(6), "C4": cycle_graph(4), "C6": cycle_graph(6),
        "K4": complete_graph(4), "K1,3": star_graph(3), "K3,3": complete_bipartite(3, 3),
        "K2": complete_graph(2),
    }


def run(quick=False, workers=None, seed=20260930, out=REPORT):
    import networkx as nx
    from networkx.generators.atlas import graph_atlas_g

    t0 = time.time()
    rng = random.Random(seed)
    atlas_max = 5 if quick else 7
    atlas = [from_nx(h) for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= atlas_max]
    rand = []
    for n, count in ((7, 10 if quick else 200), (8, 4 if quick else 200)):
        for _ in range(count):
            p = rng.choice([0.25, 0.4, 0.55, 0.7])
            es = [e for e in itertools.combinations(range(n), 2) if rng.random() < p]
            rand.append(graph(n, es))
    tasks = [(g, True, True) for g in atlas] + [(g, True, False) for g in rand]

    summary = {}
    counterexamples = {}

    def record(checks, witness):
        for name, ok in checks:
            s = summary.setdefault(name, [0, 0])
            s[0] += 1
            if not ok:
                s[1] += 1
                counterexamples.setdefault(name, [])
                if len(counterexamples[name]) < 5:
                    counterexamples[name].append(witness)

    stats = {"atlas_graphs": len(atlas), "random_graphs": len(rand)}
    value_sets = {}
    with Pool(workers) as pool:
        rows = pool.map(_graph_row_task, tasks, chunksize=4)
        for r in rows:
            record(graph_checks(r), {"n": r["n"], "edges": r["edges"]})
            if r["m"]:
                d = r.get("es")
                if d is not None:
                    value_sets.setdefault("es - vs", set()).add(d - r["vs"])
                if r["ib"] is not None:
                    value_sets.setdefault("ib - pw", set()).add(r["ib"] - r["pw"])
                value_sets.setdefault("cw - (pw+1)", set()).add(r["cw"] - r["pw"] - 1)
                value_sets.setdefault("mcw - (pw+1)", set()).add(r["mcw"] - r["pw"] - 1)
        stats["graph_seconds"] = round(time.time() - t0, 1)

        # matrices: all up to 4 x 4 up to row/column permutation, random 5 x 5
        t1 = time.time()
        mats = set()
        shapes = [(k, m) for k in range(1, 5) for m in range(1, 5)]
        if quick:
            shapes = [(k, m) for k in range(1, 4) for m in range(1, 4)]
        for k, m in shapes:
            for mx in _all_matrices(k, m):
                mats.add(_canonical_matrix(mx))
        n_exhaustive = len(mats)
        for _ in range(100 if quick else 1500):
            mats.add(tuple(tuple(int(rng.random() < 0.45) for _ in range(5)) for _ in range(5)))
        mats = sorted(mats)
        mrows = pool.map(_matrix_task, mats, chunksize=16)
        n_oht = 0
        for r in mrows:
            record(matrix_checks(r), {"matrix": r["matrix"]})
            if "ohtsuki" in r:
                n_oht += 1
                o = r["ohtsuki"]
                record([("S2 1-dim logic tracks = theta(H)", o["tracks"] == o["theta"]),
                        ("S2 1-dim logic tracks = pw(H) + 1", o["tracks"] == o["pw"] + 1)],
                       {"matrix": r["matrix"]})
            if r["has_one"]:
                value_sets.setdefault("PLA - (pw+1)", set()).add(r["pla"] - r["pw"] - 1)
        stats.update(matrices=len(mats), matrices_exhaustive_classes=n_exhaustive,
                     ohtsuki_instances=n_oht, matrix_seconds=round(time.time() - t1, 1))

    # named instances, hand-checkable
    named = {}
    for name, g in _named_graphs().items():
        r = graph_row(g, games=True, heavy=True)
        named[name] = {k: r[k] for k in ("pw", "vs", "vsg", "theta", "nu", "ns", "ns_mono",
                                         "es", "es_mono", "ib", "bw", "cw", "mcw", "vs_2exp", "vs_du")}
    for leaves in (7, 9):
        g = star_graph(leaves)
        named[f"K1,{leaves}"] = {"pw": pathwidth(g), "cw": cutwidth_dp(g),
                                 "mcw": modified_cutwidth_dp(g)}
    # split bandwidth by explicit splits (upper bound), against ib
    splits = {}
    for name, g in (("K2", complete_graph(2)), ("P3", path_graph(3)), ("K1,3", star_graph(3)),
                    ("C4", cycle_graph(4)), ("K3", complete_graph(3)), ("K4", complete_graph(4))):
        splits[name] = {"pw": pathwidth(g), "ib": interval_bandwidth(g), "bw": bandwidth(g),
                        "sb<=2 splittings": split_bandwidth_upto(g, 2),
                        "sb<=3 splittings": split_bandwidth_upto(g, 3)}
    # Lengauer Thm 7: vs(G') = mcw(G) + N
    thm7 = {}
    for name, g in (("K2", complete_graph(2)), ("P3", path_graph(3)), ("K3", complete_graph(3)),
                    ("K1,2+K1", graph(4, [(0, 1), (0, 2)])), ("P4", path_graph(4)),
                    ("K1,3", star_graph(3)), ("C4", cycle_graph(4))):
        bl = lengauer_blowup(g)
        thm7[name] = {"N": g[0], "mcw": modified_cutwidth(g), "vs(G')": vs_dp(bl),
                      "holds": vs_dp(bl) == modified_cutwidth(g) + g[0]}
    # Ohtsuki boundary family
    boundary = {}
    for k in range(1, 5):
        mx = boundary_family(k)
        tb = one_dim_logic_tracks(mx, boundary=(0, k + 1))
        tf = one_dim_logic_tracks(mx)
        h_all = row_graph(mx)
        h_inner = row_graph(mx, columns=range(1, k + 1))
        boundary[k] = {"tracks_boundary": tb, "tracks_free": tf,
                       "pw(H all gates)+1": pathwidth(h_all) + 1,
                       "pw(H inner gates)+1": pathwidth(h_inner) + 1}
    # Ohtsuki sec. IV: random instances with two disjoint boundary gates
    btasks = []
    for _ in range(400 if quick else 40000):
        nets, gates = rng.randint(3, 6), rng.randint(4, 7)
        mx = tuple(tuple(int(rng.random() < 0.35) for _ in range(gates)) for _ in range(nets))
        if not _is_ohtsuki(mx):
            continue
        l, r = 0, gates - 1
        if any(row[l] and row[r] for row in mx):
            continue
        btasks.append((mx, (l, r)))
    with Pool(workers) as pool:
        brows = pool.map(_boundary_task, btasks, chunksize=8)
    bgap = {}
    for r in brows:
        d = r["tracks_boundary"] - r["pw1"]
        bgap[d] = bgap.get(d, 0) + 1
        record([("S2b boundary tracks >= free tracks = pw(H) + 1",
                 r["tracks_boundary"] >= r["tracks_free"] == r["pw1"]),
                ("S2b boundary tracks within 1 of pw(H) + 1", abs(r["tracks_boundary"] - r["pw1"]) <= 1)],
               {"matrix": r["matrix"], "lr": r["lr"]})
    worst = max(brows, key=lambda r: r["tracks_boundary"] - r["pw1"], default=None)
    mx, lr = boundary_path_instance()
    boundary["path a-b-c-d-e"] = ohtsuki_boundary_row(mx, lr)
    boundary["random: instances by boundary - (pw+1)"] = {str(k): v for k, v in sorted(bgap.items())}
    if worst is not None:
        boundary["random: worst"] = {k: worst[k] for k in ("matrix", "lr", "tracks_boundary", "tracks_free", "pw1")}
    pla_named = {}
    for k in (3, 4, 5):
        mx = identity_matrix(k)
        pla_named[f"I{k}"] = {"pla": pla_folding_tracks(mx), "t": gate_matrix_tracks(mx),
                              "pw+1": pathwidth(row_graph(mx)) + 1}
    for n in (5, 6, 7):
        mx = incidence_matrix(path_graph(n))
        pla_named[f"P{n} incidence"] = {"pla": pla_folding_tracks(mx), "t": gate_matrix_tracks(mx),
                                        "pw+1": pathwidth(path_graph(n)) + 1}

    report = {
        "stats": stats,
        "summary": {k: {"checked": v[0], "failed": v[1]} for k, v in sorted(summary.items())},
        "counterexamples": counterexamples,
        "value_sets": {k: sorted(v) for k, v in value_sets.items()},
        "named": named, "split_bandwidth": splits, "lengauer_thm7": thm7,
        "ohtsuki_boundary": boundary, "pla": pla_named,
        "seconds": round(time.time() - t0, 1), "quick": quick, "seed": seed,
    }
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, default=list))
    return report


# ----------------------------------------------------------------------------
# Pebbling (loop0006 item 03): the two constructions of the Lean proof of
# Lengauer's Theorem 3, `lean/MOSPFormalization/Complex/Pebbling.lean`
# ----------------------------------------------------------------------------
#
# The Lean game is a four-phase machine per vertex (fresh, white, black, done)
# with three moves, place / turn / remove; `replay_progressive` is that game
# move by move. `gd_layout_strategy` is `pebblesWithin_of_layout` (⇐) and
# `removal_layout` is the layout of `vertexSeparation_le_of_pebblesWithin` (⇒).
# The Lean layout convention is the *outer* boundary (`activeSuffix`: later
# vertices with a neighbour at or before position i), `vs_outer_of_layout`;
# its minimum over layouts equals `vertex_separation` by reversal.

FRESH, WHITE, BLACK, DONE = range(4)


def replay_progressive(d, moves):
    """Play `moves` (pairs `("place" | "turn" | "remove", v)`) on the dag `d`
    under `PebbleMove.Legal` of Pebbling.lean and return the largest number of
    pebbles on the dag. Raises `ValueError` on an illegal move or if the play
    does not end with every vertex done."""
    n, pred = d
    ph = [FRESH] * n
    best = cur = 0
    for kind, v in moves:
        if kind == "place":
            if ph[v] != FRESH:
                raise ValueError(f"place {v} in phase {ph[v]}")
            ph[v] = WHITE
            cur += 1
        elif kind == "turn":
            if ph[v] != WHITE:
                raise ValueError(f"turn {v} in phase {ph[v]}")
            for u in range(n):
                if pred[v] >> u & 1 and ph[u] not in (WHITE, BLACK):
                    raise ValueError(f"turn {v} with predecessor {u} unpebbled")
            ph[v] = BLACK
        elif kind == "remove":
            if ph[v] != BLACK:
                raise ValueError(f"remove {v} in phase {ph[v]}")
            ph[v] = DONE
            cur -= 1
        else:
            raise ValueError(kind)
        best = max(best, cur)
    if any(p != DONE for p in ph):
        raise ValueError("play does not end with every vertex done")
    return best


def vs_outer_of_layout(g, order):
    """The Lean `vertexSepOfLayout`: `max_i |activeSuffix i|`, the vertices at
    positions > i with a neighbour at a position <= i."""
    n, adj = g
    best = 0
    for i, pre in enumerate(_prefix_masks(order)[:-1]):
        best = max(best, sum(1 for v in order[i + 1:] if adj[v] & pre))
    return best


def gd_layout_strategy(g, order):
    """The play of `pebblesWithin_of_layout` on `lengauer_d(g)`: for each `v` in
    `order`, blacken the pebble-free vertices of N[v] (place, turn), then place,
    turn and remove every edge vertex at `v` not yet cleared, then remove `v`."""
    n, adj = g
    es = edges_of(g)
    moves, done, black, cleared = [], 0, 0, set()
    for v in order:
        for w in [v] + [w for w in range(n) if adj[v] >> w & 1]:
            if not (done >> w & 1) and not (black >> w & 1):
                moves += [("place", w), ("turn", w)]
                black |= 1 << w
        for i, (a, b) in enumerate(es):
            if v in (a, b) and i not in cleared:
                moves += [("place", n + i), ("turn", n + i), ("remove", n + i)]
                cleared.add(i)
        moves.append(("remove", v))
        done |= 1 << v
    return moves


def removal_layout(n_g, moves):
    """The layout of `vertexSeparation_le_of_pebblesWithin`: the vertices of G
    (the first `n_g` vertices of G_d) in the order they lose their pebble."""
    return [v for kind, v in moves if kind == "remove" and v < n_g]


def strategy_row(g, max_layouts=None, seed=0):
    """Both constructions on every layout of `g` (or a sample of `max_layouts`)."""
    n, _ = g
    gd = lengauer_d(g)
    has_edge = bool(edges_of(g))
    perms = list(itertools.permutations(range(n)))
    if max_layouts is not None and len(perms) > max_layouts:
        perms = random.Random(seed).sample(perms, max_layouts)
    vs = vs_dp(g)
    fails = {"legal": 0, "bound": 0, "optimal": 0, "removal": 0, "three": 0}
    best_play = None
    for order in perms:
        moves = gd_layout_strategy(g, order)
        try:
            k = replay_progressive(gd, moves)
        except ValueError:
            fails["legal"] += 1
            continue
        lay = vs_outer_of_layout(g, order)
        # (⇐): at most the active suffix, the vertex cleared and one edge vertex
        fails["bound"] += k > (lay + 2 if has_edge else 1)
        # (⇒): the removal-order layout has vs <= pebbles - 2
        fails["removal"] += has_edge and vs_outer_of_layout(g, removal_layout(n, moves)) > k - 2
        # `three_le_of_pebblesWithin`
        fails["three"] += has_edge and k < 3
        best_play = k if best_play is None else min(best_play, k)
    # the minimum over layouts attains pbw(G_d) = vs + 2 (1 if edgeless)
    fails["optimal"] += best_play != (vs + 2 if has_edge else 1)
    return {"n": n, "edges": edges_of(g), "layouts": len(perms), "vs": vs,
            "best_play": best_play, "fails": fails}


def _strategy_task(args):
    g, cap = args
    return strategy_row(g, max_layouts=cap)


PEBBLING_STRATEGY_REPORT = Path(__file__).resolve().parent / "data" / "pebbling_strategy_check.json"


def run_pebbling_strategy(quick=False, workers=None, out=PEBBLING_STRATEGY_REPORT):
    """Replays both constructions of the Lean proof of Theorem 3 on every atlas
    graph on <= 7 vertices (<= 5 when quick), every layout of each."""
    from networkx.generators.atlas import graph_atlas_g

    t0 = time.time()
    nmax = 5 if quick else 7
    gs = [from_nx(h) for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= nmax]
    tasks = [(g, None) for g in gs]
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_strategy_task, tasks, chunksize=4))
    totals = {k: sum(r["fails"][k] for r in rows) for k in rows[0]["fails"]}
    report = {"graphs": len(rows), "max_vertices": nmax,
              "plays": sum(r["layouts"] for r in rows),
              "failures": totals,
              "counterexamples": [r for r in rows if any(r["fails"].values())][:5],
              "seconds": round(time.time() - t0, 1), "quick": quick}
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, default=list))
    return report


# ----------------------------------------------------------------------------
# Pebbling (loop0006 item 04): the constructions of the Lean proofs of
# Lengauer's Theorem 2 and KP's Theorem 3.1, `Complex/PebblingGu.lean`
# ----------------------------------------------------------------------------
#
# `gu_layout_strategy` is `pebblesWithin_of_layout_lengauerU` (⇐ of Thm 2):
# for each `v` of a layout of G_u, whiten the pebble-free G_u-neighbours of `v`
# (and `v`), turn `v` and its successors that are not black, remove `v`
# (`reach_guPos_insert`). The (⇒) layout is the removal order. The Lean
# statement is for the game on *any* digraph, loops and cycles included, so
# `run_pebbling_gu` also checks `pbw(D) = vs(G_u) + 1` on every digraph with
# at most 4 vertices, loops allowed. `kp_black_strategy` is
# `blackPebblesWithin_layoutOrient` (KP Thm 3.1 ≤): orient along the layout,
# place in layout order, clear a vertex once all its neighbours are placed.


def digraph_pred(n, arcs):
    """`(n, pred)` from arcs `(u, v)` with no acyclicity or loop check."""
    pred = [0] * n
    for u, v in arcs:
        pred[v] |= 1 << u
    return (n, tuple(pred))


def lengauer_u_general(d):
    """`lengauerU` of PebblingGu.lean: `u ≠ w` and an arc either way or a common
    successor. Equals `lengauer_u` on loop-free digraphs."""
    n, pred = d
    es = set()
    for v in range(n):
        ps = [u for u in range(n) if pred[v] >> u & 1]
        es.update((min(u, v), max(u, v)) for u in ps if u != v)
        es.update((a, b) for a, b in itertools.combinations(ps, 2))
    return graph(n, sorted(es))


def gu_layout_strategy(d, order):
    """The play of `pebblesWithin_of_layout_lengauerU` on `d` along `order`
    (a layout of G_u), in the move vocabulary of `replay_progressive`."""
    n, pred = d
    _, uadj = lengauer_u_general(d)
    succ = [sum(1 << v for v in range(n) if pred[v] >> u & 1) for u in range(n)]
    ph = [FRESH] * n
    moves = []
    for v in order:
        for w in [v] + [w for w in range(n) if uadj[v] >> w & 1]:  # step 1: whiten X
            if ph[w] == FRESH:
                moves.append(("place", w))
                ph[w] = WHITE
        for z in [v] + [w for w in range(n) if succ[v] >> w & 1 and ph[w] != DONE]:  # Z
            if ph[z] == WHITE:
                moves.append(("turn", z))
                ph[z] = BLACK
        moves.append(("remove", v))
        ph[v] = DONE
    return moves


def replay_black(d, moves):
    """KP's progressive black game (`BlackMove.Legal`): `("place", v)` puts a
    black pebble on a never-pebbled `v` whose predecessors are all pebbled,
    `("remove", v)` clears it. Returns the largest pebble count."""
    n, pred = d
    ph = [FRESH] * n
    best = cur = 0
    for kind, v in moves:
        if kind == "place":
            if ph[v] != FRESH:
                raise ValueError(f"place {v} in phase {ph[v]}")
            for u in range(n):
                if pred[v] >> u & 1 and ph[u] != BLACK:
                    raise ValueError(f"place {v} with predecessor {u} unpebbled")
            ph[v] = BLACK
            cur += 1
        elif kind == "remove":
            if ph[v] != BLACK:
                raise ValueError(f"remove {v} in phase {ph[v]}")
            ph[v] = DONE
            cur -= 1
        else:
            raise ValueError(kind)
        best = max(best, cur)
    if any(p != DONE for p in ph):
        raise ValueError("play does not end with every vertex done")
    return best


def black_to_bw(moves):
    """`BlackStep.reflTransGen`: a black placement is a white one turned at once."""
    out = []
    for kind, v in moves:
        out += [("place", v), ("turn", v)] if kind == "place" else [(kind, v)]
    return out


def kp_black_strategy(g, order):
    """The play of `blackPebblesWithin_layoutOrient` on `orient(g, order)`."""
    n, adj = g
    pos = {v: i for i, v in enumerate(order)}
    moves, live = [], []
    for i, v in enumerate(order):
        moves.append(("place", v))
        live.append(v)
        keep = []
        for w in live:
            if all(pos[u] <= i for u in range(n) if adj[w] >> u & 1):
                moves.append(("remove", w))
            else:
                keep.append(w)
        live = keep
    return moves


def gu_row(d):
    """Both Thm 2 constructions on every layout of G_u, and the statement."""
    n, _ = d
    u = lengauer_u_general(d)
    vs = vs_dp(u)
    fails = {"legal": 0, "bound": 0, "removal": 0, "optimal": 0, "statement": 0}
    best = None
    for order in itertools.permutations(range(n)):
        moves = gu_layout_strategy(d, order)
        try:
            k = replay_progressive(d, moves)
        except ValueError:
            fails["legal"] += 1
            continue
        fails["bound"] += k > vs_outer_of_layout(u, order) + 1
        rem = [v for kind, v in moves if kind == "remove"]
        fails["removal"] += vs_outer_of_layout(u, rem) > max(k, 1) - 1
        best = k if best is None else min(best, k)
    if n:
        fails["optimal"] += best != vs + 1
        # the statement, by exact search: pbw(D) = vs(G_u) + 1
        fails["statement"] += not (progressive_bw_within(d, vs + 1)
                                   and not progressive_bw_within(d, vs))
    return {"n": n, "pred": d[1], "vs_u": vs, "fails": fails}


def kp_row(g):
    """The KP black strategy on every layout of `g`."""
    n, _ = g
    vs = vs_dp(g)
    fails = {"legal": 0, "bound": 0, "bw_replay": 0, "optimal": 0}
    best = None
    for order in itertools.permutations(range(n)):
        d = orient(g, order)
        moves = kp_black_strategy(g, order)
        try:
            k = replay_black(d, moves)
        except ValueError:
            fails["legal"] += 1
            continue
        # the shack just after v_i is put in = vs(reversed layout) + 1
        fails["bound"] += k > vs_outer_of_layout(g, list(reversed(order))) + 1
        try:
            fails["bw_replay"] += replay_progressive(d, black_to_bw(moves)) != k
        except ValueError:
            fails["bw_replay"] += 1
        best = k if best is None else min(best, k)
    fails["optimal"] += best != vs + 1
    return {"n": n, "edges": edges_of(g), "vs": vs, "fails": fails}


def _all_digraphs(n, loops=True):
    pairs = [(u, v) for u in range(n) for v in range(n) if loops or u != v]
    for mask in range(1 << len(pairs)):
        yield digraph_pred(n, [pairs[i] for i in range(len(pairs)) if mask >> i & 1])


PEBBLING_GU_REPORT = Path(__file__).resolve().parent / "data" / "pebbling_gu_check.json"


def run_pebbling_gu(quick=False, workers=None, out=PEBBLING_GU_REPORT):
    """Thm 2's constructions on every digraph with <= 4 vertices, loops
    allowed (<= 3 when quick), and on every dag with 5 vertices; KP's black
    strategy on every atlas graph with <= 7 vertices (<= 5 when quick)."""
    from networkx.generators.atlas import graph_atlas_g

    t0 = time.time()
    dmax = 3 if quick else 4
    ds = [d for n in range(0, dmax + 1) for d in _all_digraphs(n)]
    dags5 = [] if quick else list(_all_dags(5))
    gmax = 5 if quick else 7
    gs = [from_nx(h) for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= gmax]
    with Pool(workers) as pool:
        drows = list(pool.imap_unordered(gu_row, ds + dags5, chunksize=64))
        grows = list(pool.imap_unordered(kp_row, gs, chunksize=4))

    def tot(rows):
        return {k: sum(r["fails"][k] for r in rows) for k in rows[0]["fails"]}

    report = {"digraphs": len(ds), "digraph_max_vertices": dmax, "dags_5": len(dags5),
              "gu_failures": tot(drows),
              "graphs": len(gs), "graph_max_vertices": gmax,
              "kp_plays": sum(math.factorial(r["n"]) for r in grows),
              "kp_failures": tot(grows),
              "counterexamples": ([r for r in drows if any(r["fails"].values())][:5]
                                  + [r for r in grows if any(r["fails"].values())][:5]),
              "seconds": round(time.time() - t0, 1), "quick": quick}
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, default=list))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--pebbling", action="store_true",
                    help="run only the loop0006 pebbling checks (P.5), writing pebbling_check.json")
    ap.add_argument("--pebbling-strategy", action="store_true",
                    help="replay the two constructions of the Lean proof of Lengauer Thm 3 (item 03)")
    ap.add_argument("--pebbling-gu", action="store_true",
                    help="replay the constructions of the Lean proofs of Lengauer Thm 2 and KP Thm 3.1 (item 04)")
    a = ap.parse_args(argv)
    if a.pebbling_gu:
        rep = run_pebbling_gu(quick=a.quick, workers=a.workers, out=a.out or PEBBLING_GU_REPORT)
        print(json.dumps(rep, indent=1, default=list))
        return 0
    if a.pebbling_strategy:
        rep = run_pebbling_strategy(quick=a.quick, workers=a.workers,
                                    out=a.out or PEBBLING_STRATEGY_REPORT)
        print(json.dumps(rep, indent=1, default=list))
        return 0
    if a.pebbling:
        rep = run_pebbling(quick=a.quick, workers=a.workers, out=a.out or PEBBLING_REPORT)
        print(json.dumps(rep["stats"], indent=1))
        width = max(len(k) for k in rep["summary"])
        for k, v in rep["summary"].items():
            print(f"{k:<{width}}  checked {v['checked']:>6}  failed {v['failed']:>6}")
        for key in ("out_trees_by_pbw_minus_bw", "named", "counterexamples"):
            print(key, json.dumps(rep[key]))
        print(f"{rep['seconds']} s")
        return 0
    a.out = a.out or REPORT
    rep = run(quick=a.quick, workers=a.workers, out=a.out)
    print(json.dumps(rep["stats"], indent=1))
    width = max(len(k) for k in rep["summary"])
    for k, v in rep["summary"].items():
        print(f"{k:<{width}}  checked {v['checked']:>6}  failed {v['failed']:>6}")
    print("value sets:", json.dumps(rep["value_sets"]))
    for key in ("named", "split_bandwidth", "lengauer_thm7", "ohtsuki_boundary", "pla"):
        print(key, json.dumps(rep[key], indent=None))
    print("counterexamples:", json.dumps(rep["counterexamples"])[:3000])
    print(f"{rep['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
