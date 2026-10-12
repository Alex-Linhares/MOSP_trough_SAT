"""Independent minor-certificate tooling (2026-10-12), written from scratch.

Imports nothing from the project: no networkx, no pathwidth_solver, no mosp.
Graphs are dicts {vertex: set(neighbours)} over integer labels.

  read_dgf(path)               DIMACS .dgf, vertex id i -> label i-1
  read_mosp_customer_graph(path, fmt, index)
                               the MOSP graph: customers as vertices, a clique per
                               pattern. fmt "A" (Chu & Stuckey: first line
                               "patterns customers", one row per pattern) or "B"
                               (Challenge 2005: named blocks, rows = customers).
  heuristic_sequence(G, m, rule)
                               a contraction sequence [(keep, absorbed), ...] to m
                               vertices: repeatedly take the min-degree vertex v
                               (ties: smallest label) and contract it into a
                               neighbour u chosen by `rule` ("min-d": least degree;
                               "least-c": fewest common neighbours; ties smallest).
  sequence_from_branch_sets(G, sets)
                               a contraction sequence realising a partition into
                               connected branch sets (BFS tree inside each set).
  replay(G, seq)               replays a sequence, asserting every step contracts
                               an existing edge of the current graph; returns the
                               minor H (labels = surviving representatives) and the
                               branch set of every representative.
"""
import hashlib
import json


def read_dgf(path):
    G = {}
    for line in open(path):
        p = line.split()
        if not p:
            continue
        if p[0] == "p":
            for i in range(int(p[2])):
                G.setdefault(i, set())
        elif p[0] == "e":
            u, v = int(p[1]) - 1, int(p[2]) - 1
            if u != v:
                G.setdefault(u, set()).add(v)
                G.setdefault(v, set()).add(u)
    return G


def _blocks(path):
    rows = [l.split() for l in open(path)]
    i = 0
    out = []
    while i < len(rows):
        if not rows[i]:
            i += 1
            continue
        try:
            a, b = int(rows[i][0]), int(rows[i][1])
            assert len(rows[i]) == 2
        except (ValueError, AssertionError, IndexError):
            i += 1  # a name line
            continue
        mat = [list(map(int, r)) for r in rows[i + 1:i + 1 + a]]
        assert len(mat) == a and all(len(r) == b for r in mat), path
        out.append(mat)
        i += 1 + a
    return out


def read_mosp_customer_graph(path, fmt, index=0):
    mat = _blocks(path)[index]
    if fmt == "A":           # rows are patterns, columns customers
        n = len(mat[0])
        cliques = [[c for c, x in enumerate(r) if x] for r in mat]
    else:                    # rows are customers, columns patterns
        n = len(mat)
        cliques = [[c for c in range(n) if mat[c][p]] for p in range(len(mat[0]))]
    G = {c: set() for c in range(n)}
    for cl in cliques:
        for a in cl:
            for b in cl:
                if a != b:
                    G[a].add(b)
    return G


def copy(G):
    return {v: set(N) for v, N in G.items()}


def contract(G, u, v):
    """Contract edge uv in place, keeping u. Asserts the edge exists."""
    assert u in G and v in G and u != v, (u, v)
    assert v in G[u] and u in G[v], f"not an edge: {u}-{v}"
    for w in G[v]:
        G[w].discard(v)
        if w != u:
            G[w].add(u)
            G[u].add(w)
    del G[v]
    G[u].discard(u)
    G[u].discard(v)


def heuristic_sequence(G, m, rule):
    H = copy(G)
    seq = []
    while len(H) > m:
        v = min(H, key=lambda x: (len(H[x]), x))
        nb = H[v]
        assert nb, "isolated vertex: contraction alone cannot remove it"
        if rule == "least-c":
            u = min(nb, key=lambda c: (len(H[c] & nb), c))
        elif rule == "min-d":
            u = min(nb, key=lambda c: (len(H[c]), c))
        else:
            raise ValueError(rule)
        contract(H, u, v)
        seq.append((u, v))
    return seq


def sequence_from_branch_sets(G, sets):
    seq = []
    for S in sets:
        S = set(S)
        root = min(S)
        seen = {root}
        frontier = [root]
        while frontier:
            nxt = []
            for a in frontier:
                for b in sorted(G[a] & S):
                    if b not in seen:
                        seen.add(b)
                        nxt.append(b)
                        seq.append((root, b, a))   # b joins root's set via edge a-b
            frontier = nxt
        assert seen == S, f"branch set not connected: {sorted(S)}"
    return seq


def replay(G, seq):
    """Replay [(keep, absorbed), ...]; every step must contract a current edge."""
    H = copy(G)
    branch = {v: {v} for v in G}
    for step in seq:
        u, v = step[0], step[1]
        contract(H, u, v)
        branch[u] |= branch.pop(v)
    # independent re-derivation of the quotient graph from the branch sets
    rep = {x: r for r, B in branch.items() for x in B}
    assert sorted(rep) == sorted(G), "branch sets do not partition V(G)"
    Q = {r: set() for r in branch}
    for a in G:
        for b in G[a]:
            if rep[a] != rep[b]:
                Q[rep[a]].add(rep[b])
    assert Q == H, "replayed graph differs from the quotient by its branch sets"
    return H, branch


def edges(G):
    return sorted((a, b) for a in G for b in G[a] if a < b)


def relabel_sorted(H):
    """Relabel to 0..m-1 by increasing representative label."""
    idx = {r: i for i, r in enumerate(sorted(H))}
    return {idx[r]: {idx[x] for x in N} for r, N in H.items()}, idx


def graph_hash(H):
    return hashlib.sha256(json.dumps(edges(H)).encode()).hexdigest()
