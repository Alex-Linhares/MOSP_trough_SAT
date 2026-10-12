"""The statements of `lean/MOSPFormalization/Minor.lean`, checked on small graphs.

Lean models a contraction on a fixed vertex type: `contractEdge G u v` merges
`v` into `u` (u keeps its label, as in `pathwidth_solver/pathwidth/minor.py`)
and leaves `v` as an isolated vertex; a deletion step removes every edge at
`v`; the minor is the graph induced on the vertices never removed. Checked
here, with the subset DP as the oracle:

* that model, induced on the alive vertices, is exactly the code's `replay`;
* `pw(contractEdge G u v) <= pw(G)` for every edge `uv`, on the full vertex
  type with `v` isolated (the one-step Lean statement);
* `pw(minor) <= pw(G)` for random valid sequences, contractions and deletions
  mixed, not only the greedy ones `test_minor_bound.py` checks;
* a control: identifying two *non-adjacent* vertices can raise the pathwidth,
  so the edge hypothesis of the Lean theorem is not decorative.
"""

import random
import sys
from pathlib import Path

import networkx as nx

from fixed_parameter_algorithm.pathwidth import compute_pathwidth

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pathwidth_solver"))
from pathwidth.minor import replay  # noqa: E402


def pw(adj, vertices):
    G = nx.Graph()
    G.add_nodes_from(vertices)
    for x in vertices:
        for y in adj[x]:
            if y in vertices:
                G.add_edge(x, y)
    return compute_pathwidth(G)[0] if G.number_of_nodes() else 0


def contract_edge(adj, u, v):
    """Lean's `contractEdge G u v`: Adj x y iff x != y, x, y != v and
    (G.Adj x y or x = u and G.Adj v y or y = u and G.Adj v x)."""
    n = len(adj)
    out = [set() for _ in range(n)]
    for x in range(n):
        for y in range(n):
            if x != y and x != v and y != v and (
                    y in adj[x] or (x == u and y in adj[v]) or (y == u and x in adj[v])):
                out[x].add(y)
    return out


def delete_vertex(adj, v):
    """Lean's `isolate G v`: Adj x y iff G.Adj x y and x, y != v."""
    return [set() if x == v else {y for y in s if y != v} for x, s in enumerate(adj)]


def random_graph(rng, n):
    p = rng.uniform(0.15, 0.7)
    adj = [set() for _ in range(n)]
    for x in range(n):
        for y in range(x + 1, n):
            if rng.random() < p:
                adj[x].add(y)
                adj[y].add(x)
    return adj


def test_one_contraction_never_raises_pathwidth():
    rng = random.Random(2026)
    checked = 0
    for _ in range(80):
        n = rng.randint(3, 10)
        adj = random_graph(rng, n)
        base = pw(adj, range(n))
        for u in range(n):
            for v in adj[u]:
                assert pw(contract_edge(adj, u, v), range(n)) <= base
                checked += 1
    assert checked > 300


def test_random_sequences_match_replay_and_never_raise_pathwidth():
    rng = random.Random(7)
    checked = 0
    for _ in range(300):
        n = rng.randint(3, 11)
        adj = random_graph(rng, n)
        base = pw(adj, range(n))
        alive, cur, seq = set(range(n)), adj, []
        for _ in range(rng.randint(1, n - 1)):
            edges = [(v, u) for v in alive for u in cur[v]]
            isolated = [v for v in alive if not cur[v]]
            if isolated and (not edges or rng.random() < 0.2):
                v = rng.choice(isolated)
                seq.append((v, -1))
                cur = delete_vertex(cur, v)
            elif edges:
                v, u = rng.choice(edges)
                seq.append((v, u))
                cur = contract_edge(cur, u, v)
            else:
                break
            alive.discard(v)
        masks = [(1 << x) | sum(1 << y for y in adj[x]) for x in range(n)]
        minor, labels, _ = replay(masks, seq)
        assert set(labels) == alive
        for i, x in enumerate(labels):
            got = {labels[j] for j in range(len(labels)) if j != i and minor[i] >> j & 1}
            assert got == cur[x] & alive
        assert all(not cur[x] for x in set(range(n)) - alive)
        assert pw(cur, sorted(alive)) <= pw(cur, range(n)) <= base
        checked += 1
    assert checked == 300


def test_identifying_non_adjacent_vertices_can_raise_pathwidth():
    # The path 0-1-2-3-4-5 has pathwidth 1; identifying its non-adjacent ends
    # closes a 5-cycle, of pathwidth 2.
    n = 6
    adj = [set() for _ in range(n)]
    for x in range(n - 1):
        adj[x].add(x + 1)
        adj[x + 1].add(x)
    assert pw(adj, range(n)) == 1
    assert 5 not in adj[0]
    assert pw(contract_edge(adj, 0, 5), range(n)) == 2
