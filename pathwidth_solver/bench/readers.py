"""Readers for the benchmark instance formats, all returning `networkx.Graph`
with integer labels, no self-loops, no parallel edges."""

from __future__ import annotations

from pathlib import Path

import networkx as nx


def _clean(G: nx.Graph) -> nx.Graph:
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def read_dgf(path: Path) -> nx.Graph:
    """DIMACS colouring / TreewidthLIB `.dgf`: `p edge n m`, `e u v`."""
    G = nx.Graph()
    for line in path.read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "p":
            G.add_nodes_from(range(1, int(parts[2]) + 1))
        elif parts[0] == "e":
            G.add_edge(int(parts[1]), int(parts[2]))
    return _clean(G)


def read_gr(path: Path) -> nx.Graph:
    """PACE `.gr`: `p tw n m`, then `u v` per edge, `c` comments."""
    G = nx.Graph()
    for line in path.read_text().splitlines():
        parts = line.split()
        if not parts or parts[0] == "c":
            continue
        if parts[0] == "p":
            G.add_nodes_from(range(1, int(parts[2]) + 1))
        else:
            G.add_edge(int(parts[0]), int(parts[1]))
    return _clean(G)


def read_vsplib(path: Path) -> nx.Graph:
    """VSPLIB `.mtx.rnd` and tree files: a name line, `n n m`, then `u v`."""
    G = nx.Graph()
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    start = 0
    if lines and not lines[0].split()[0].isdigit():
        start = 1
    header = lines[start].split()
    n = int(header[0])
    G.add_nodes_from(range(1, n + 1))
    for line in lines[start + 1:]:
        parts = line.split()
        if len(parts) >= 2:
            G.add_edge(int(parts[0]), int(parts[1]))
    return _clean(G)


def read_graphml(path: Path) -> nx.Graph:
    G = nx.Graph(nx.read_graphml(path))
    return _clean(nx.convert_node_labels_to_integers(G))


def read_any(path: Path) -> nx.Graph:
    s = path.suffix.lower()
    if s == ".dgf":
        return read_dgf(path)
    if s == ".gr":
        return read_gr(path)
    if s == ".graphml":
        return read_graphml(path)
    return read_vsplib(path)


HERE = Path(__file__).resolve().parent / "instances"

SETS = {
    "coloring": lambda: sorted(p for p in (HERE / "coloring").glob("*.dgf") if not p.name.endswith("-pp.dgf")),
    "named": lambda: sorted((HERE / "named" / "gr").glob("*.gr")),
    "vsplib-grids": lambda: sorted((HERE / "vsplib" / "grids").glob("*.rnd")),
    "vsplib-tree": lambda: sorted(p for p in (HERE / "vsplib" / "tree").rglob("*") if p.is_file() and "MACOSX" not in str(p)),
    "vsplib-hb": lambda: sorted((HERE / "vsplib" / "hb").glob("*.rnd")),
    "rome": lambda: sorted((HERE / "rome").rglob("*.graphml")),
}
