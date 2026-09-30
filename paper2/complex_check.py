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
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
import time
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

REPORT = Path(__file__).resolve().parent / "data" / "complex_check.json"

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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--out", type=Path, default=REPORT)
    a = ap.parse_args(argv)
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
