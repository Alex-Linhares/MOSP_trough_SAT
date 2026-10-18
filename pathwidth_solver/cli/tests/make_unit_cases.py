"""Build the unit cases and their expected values from the Python solver.

Each graph is solved by `pathwidth.solve` (the reference this program ports)
on the fly, and the case file records graph6, width, proof and a name:

    nice -n 19 python tests/make_unit_cases.py > tests/unit_cases.txt

`tests/unit.sh` then checks the C program against that file with no Python.
"""
import random
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pathwidth import solve  # noqa: E402


def cases():
    yield "empty-n0", nx.empty_graph(0)
    yield "K1", nx.empty_graph(1)
    yield "edgeless-5", nx.empty_graph(5)
    for n in (2, 3, 5, 10):
        yield f"P{n}", nx.path_graph(n)
    for n in (3, 4, 7, 10):
        yield f"C{n}", nx.cycle_graph(n)
    for n in (2, 4, 6, 8):
        yield f"K{n}", nx.complete_graph(n)
    for n in (3, 6, 20):
        yield f"star-K1,{n}", nx.star_graph(n)
    for h in (1, 2, 3):
        yield f"ternary-tree-h{h}", nx.balanced_tree(3, h)
    for k in (2, 3, 4, 5, 6):
        yield f"grid-{k}x{k}", nx.grid_2d_graph(k, k)
    yield "petersen", nx.petersen_graph()
    yield "K3,3", nx.complete_bipartite_graph(3, 3)
    yield "K4,6", nx.complete_bipartite_graph(4, 6)
    yield "hypercube-Q4", nx.hypercube_graph(4)
    yield "grotzsch", nx.mycielski_graph(4)
    yield "disjoint-K4+C5+P3+K1", nx.disjoint_union_all(
        [nx.complete_graph(4), nx.cycle_graph(5), nx.path_graph(3), nx.empty_graph(1)])
    yield "disjoint-P2+K5+K1+K1", nx.disjoint_union_all(
        [nx.path_graph(2), nx.complete_graph(5), nx.empty_graph(2)])
    yield "disjoint-tree-h3+grid4", nx.disjoint_union(nx.balanced_tree(3, 3), nx.grid_2d_graph(4, 4))
    # above 64 vertices: the multiword engine and the minor step (n >= 40)
    yield "P100", nx.path_graph(100)
    yield "C130", nx.cycle_graph(130)
    yield "grid-9x9", nx.grid_2d_graph(9, 9)
    yield "binary-tree-h7", nx.balanced_tree(2, 7)
    yield "ternary-tree-h4", nx.balanced_tree(3, 4)
    rng = random.Random(20261018)
    for n, m in ((45, 70), (70, 95), (120, 124)):
        yield f"gnm-{n}-{m}", nx.gnm_random_graph(n, m, seed=rng.randrange(1 << 30))
    yield "random-tree-300", nx.random_labeled_tree(300, seed=3) if hasattr(nx, "random_labeled_tree") \
        else nx.random_tree(300, seed=3)
    yield "random-tree-500", nx.random_labeled_tree(500, seed=7) if hasattr(nx, "random_labeled_tree") \
        else nx.random_tree(500, seed=7)
    yield "P1100", nx.path_graph(1100)       # above the engine's 1024 vertices


for name, G in cases():
    G = nx.convert_node_labels_to_integers(G)
    g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
    s = solve(G, time_budget=300)
    print(g6, s.width, s.proof or "upper", name, flush=True)
