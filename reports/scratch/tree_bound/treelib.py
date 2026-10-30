"""Helpers: parent arrays (gentreeg -p, 1-indexed, 0 = root) <-> networkx <-> graph6; the C filter
treepw and the C solver pathwidth_solver/cli/pathwidth as subprocesses."""
import subprocess, networkx as nx, itertools, random, sys
HERE = "/home/al/dev/MOSP/reports/scratch/tree_bound"
SOLVER = "/home/al/dev/MOSP/pathwidth_solver/cli/pathwidth"

def parents_to_nx(par):
    G = nx.Graph(); G.add_nodes_from(range(len(par)))
    for v, p in enumerate(par):
        if p > 0: G.add_edge(v, p - 1)
    return G

def nx_to_parents(G, root=None):
    nodes = list(G.nodes()); root = nodes[0] if root is None else root
    order = list(nx.dfs_preorder_nodes(G, root)); idx = {v: i for i, v in enumerate(order)}
    par = [0] * len(order)
    for v in order:
        if v != root:
            p = next(iter(nx.dfs_predecessors(G, root).get(v, None),)) if False else None
    pred = nx.dfs_predecessors(G, root)
    for v in order:
        if v != root: par[idx[v]] = idx[pred[v]] + 1
    return par

def g6(G):
    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G), header=False).decode().strip()

def treepw_many(pars):
    """exact pw by the C ternary-lemma filter, list of parent arrays -> list of ints"""
    inp = "\n".join(" ".join(map(str, p)) for p in pars) + "\n"
    out = subprocess.run([HERE + "/treepw", "-v"], input=inp, capture_output=True, text=True).stdout.splitlines()
    return [int(l) for l in out if not l.startswith("hist")]

def solver_pw(G, t=600):
    """C solver: (width, status)"""
    out = subprocess.run(["nice", "-n", "19", SOLVER, "-t", str(t)], input=(g6(G) + "\n").encode(), capture_output=True).stdout.decode().split()
    return int(out[1]), out[2]

def join_at_root(trees_with_attach):
    """new root r joined by an edge to vertex a_i of tree T_i, for (T_i, a_i) pairs"""
    G = nx.Graph(); G.add_node("r"); 
    for i, (T, a) in enumerate(trees_with_attach):
        H = nx.relabel_nodes(T, {v: (i, v) for v in T.nodes()}); G = nx.union(G, H); G.add_edge("r", (i, a))
    return nx.convert_node_labels_to_integers(G)

def spider(legs):
    G = nx.Graph(); G.add_node(0); nxt = 1
    for L in legs:
        prev = 0
        for _ in range(L): G.add_edge(prev, nxt); prev = nxt; nxt += 1
    return G

def random_tree(n, rng):
    """random labelled tree by Prüfer"""
    return nx.from_prufer_sequence([rng.randrange(n) for _ in range(n - 2)]) if n > 2 else nx.path_graph(n)
