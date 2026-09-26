"""Exact treewidth of small graphs (plan 2 §2.7, loop0003 item 08).

Two exact routines, both in `learning/treewidth.c` and reached through
ctypes, plus a pure-Python reference of the first for the tests:

- `treewidth_exact(adj)`: the O(2ⁿ · n · poly) subset recurrence
  `TW(S) = min_v max(TW(S − v), |Q(S − v, v)|)` (Bodlaender, Fomin, Koster,
  Kratsch & Thilikos 2012), one byte per subset, to n = 26; returns the
  treewidth and an elimination ordering of that width.
- `treewidth_decide(adj, k)`: "tw ≤ k?" by depth-first search over
  elimination prefixes with a failure memo and two safe reductions
  (simplicial and almost-simplicial vertices of degree ≤ k are eliminated at
  once; a simplicial vertex of degree > k refutes the node), for n to 64
  under a node budget. `treewidth_bounded(adj, deadline)` runs it upward
  from the MMD lower bound to the min-fill upper bound and returns exact
  bounds either way -- a censored run narrows the interval, never invents a
  value.

The elimination ordering returned is the checkable half of the answer:
`elimination_width(adj, order)` recomputes its width in Python with no shared
code. The lower half (no ordering does better) rests on the DP; for n ≤ 10
the Python reference DP recomputes it independently.

Nothing here is a bound on MOSP; nothing reaches the solver.

Usage:
    python -m learning.treewidth            # self-check on paths, cycles, grids
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Sequence

_SOURCE = Path(__file__).with_name("treewidth.c")
_LIBRARY = Path(__file__).with_name("_treewidth.so")
_lock = threading.Lock()
_library: "ctypes.CDLL | None" = None
_build_error: str | None = None
DP_MAX_N = 26


def _build() -> bool:
    global _build_error
    if _LIBRARY.exists() and _LIBRARY.stat().st_mtime >= _SOURCE.stat().st_mtime:
        return True
    scratch = _LIBRARY.with_name(_LIBRARY.name + f".build-{os.getpid()}")
    try:
        subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC",
                        "-o", str(scratch), str(_SOURCE)],
                       check=True, capture_output=True, timeout=120)
        os.replace(scratch, _LIBRARY)
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        _build_error = f"{type(exc).__name__}: {exc}"
        try:
            scratch.unlink()
        except OSError:
            pass
        return False


def _load() -> ctypes.CDLL:
    global _library, _build_error
    with _lock:
        if _library is not None:
            return _library
        if not _build():
            raise RuntimeError(f"cannot build {_SOURCE.name}: {_build_error}")
        lib = ctypes.CDLL(str(_LIBRARY))
        lib.tw_dp.restype = ctypes.c_int
        lib.tw_dp.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint64),
                              ctypes.POINTER(ctypes.c_int)]
        lib.tw_decide.restype = ctypes.c_int
        lib.tw_decide.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint64),
                                  ctypes.c_int, ctypes.c_longlong, ctypes.c_longlong,
                                  ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_longlong)]
        _library = lib
        return lib


# ----------------------------------------------------------------------------
# adjacency helpers
# ----------------------------------------------------------------------------


def masks_from_graph(graph) -> list[int]:
    """Neighbour bitmasks of a networkx graph whose nodes are 0..n−1 (self excluded)."""
    n = graph.number_of_nodes()
    masks = [0] * n
    for u, v in graph.edges():
        if u == v:
            continue
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return masks


def masks_from_matrix(matrix) -> list[int]:
    """Neighbour bitmasks of the MOSP graph of a customer × product 0/1 matrix."""
    import numpy as np

    m = np.asarray(matrix, dtype=np.int64)
    n = m.shape[0]
    masks = [0] * n
    for col in range(m.shape[1]):
        members = [int(i) for i in np.flatnonzero(m[:, col])]
        bits = 0
        for i in members:
            bits |= 1 << i
        for i in members:
            masks[i] |= bits & ~(1 << i)
    return masks


def masks_from_instance(instance) -> list[int]:
    return masks_from_matrix(instance.matrix)


def _c_masks(masks: Sequence[int]):
    arr = (ctypes.c_uint64 * max(1, len(masks)))()
    for i, m in enumerate(masks):
        arr[i] = m
    return arr


# ----------------------------------------------------------------------------
# the exact DP
# ----------------------------------------------------------------------------


def treewidth_exact(masks: Sequence[int]) -> tuple[int, list[int]]:
    """Exact treewidth and an elimination ordering of that width, n ≤ 26."""
    n = len(masks)
    if n == 0:
        return 0, []
    if n > DP_MAX_N:
        raise ValueError(f"the subset DP holds n ≤ {DP_MAX_N}; got {n}")
    lib = _load()
    order = (ctypes.c_int * n)()
    width = lib.tw_dp(n, _c_masks(masks), order)
    if width < 0:
        raise MemoryError(f"tw_dp failed with code {width}")
    return int(width), [int(order[i]) for i in range(n)]


def treewidth_reference(masks: Sequence[int]) -> int:
    """The same recurrence in Python, for the tests (n ≤ 12 or so)."""
    n = len(masks)
    if n == 0:
        return 0
    full = (1 << n) - 1
    tw = [0] * (1 << n)
    for S in range(1, full + 1):
        best = n
        rest = S
        while rest:
            v = (rest & -rest).bit_length() - 1
            rest &= rest - 1
            T = S & ~(1 << v)
            if tw[T] >= best:
                continue
            q = bin(q_set(masks, T, v)).count("1")
            best = min(best, max(tw[T], q))
        tw[S] = best
    return tw[full]


def q_set(masks: Sequence[int], S: int, v: int) -> int:
    """Neighbourhood of v in the graph with the vertex set S eliminated."""
    nb = masks[v]
    reach = nb & S
    seen = 0
    while reach != seen:
        fresh = reach & ~seen
        seen = reach
        while fresh:
            u = (fresh & -fresh).bit_length() - 1
            fresh &= fresh - 1
            nb |= masks[u]
        reach = nb & S
    return nb & ~S & ~(1 << v)


def elimination_width(masks: Sequence[int], order: Sequence[int]) -> int:
    """Width of an elimination ordering, recomputed from scratch: the largest
    degree a vertex has when it is eliminated. Checks the ordering is a
    permutation."""
    n = len(masks)
    if sorted(order) != list(range(n)):
        raise ValueError("order is not a permutation of the vertices")
    S = 0
    width = 0
    for v in order:
        width = max(width, bin(q_set(masks, S, v)).count("1"))
        S |= 1 << v
    return width


# ----------------------------------------------------------------------------
# the decision search
# ----------------------------------------------------------------------------


def treewidth_decide(masks: Sequence[int], k: int, budget: int = 10_000_000,
                     memo_capacity: int = 1 << 22) -> tuple[str, list[int] | None, int]:
    """Is tw ≤ k? Returns (`"yes"` | `"no"` | `"unknown"`, ordering or None, nodes)."""
    n = len(masks)
    if n == 0:
        return "yes", [], 0
    if n > 64:
        raise ValueError("tw_decide holds n ≤ 64")
    lib = _load()
    order = (ctypes.c_int * n)()
    nodes = ctypes.c_longlong(0)
    code = lib.tw_decide(n, _c_masks(masks), int(k), int(budget), int(memo_capacity),
                         order, ctypes.byref(nodes))
    if code == 1:
        return "yes", [int(order[i]) for i in range(n)], int(nodes.value)
    if code == 0:
        return "no", None, int(nodes.value)
    if code == 2:
        return "unknown", None, int(nodes.value)
    raise RuntimeError(f"tw_decide returned {code}")


def min_fill_upper_bound(masks: Sequence[int]) -> tuple[int, list[int]]:
    """Greedy min-fill elimination: an upper bound with its ordering."""
    n = len(masks)
    S = 0
    order: list[int] = []
    width = 0
    for _ in range(n):
        best_v, best_key = -1, None
        for v in range(n):
            if S >> v & 1:
                continue
            Q = q_set(masks, S, v)
            fill = 0
            rest = Q
            while rest:
                u = (rest & -rest).bit_length() - 1
                rest &= rest - 1
                fill += bin(Q & ~q_set(masks, S, u) & ~(1 << u)).count("1")
            key = (fill, bin(Q).count("1"), v)
            if best_key is None or key < best_key:
                best_key, best_v = key, v
        width = max(width, best_key[1])
        order.append(best_v)
        S |= 1 << best_v
    return width, order


def mmd_lower_bound(masks: Sequence[int]) -> int:
    """Maximum minimum degree over greedy vertex deletion: a treewidth lower bound."""
    n = len(masks)
    alive = (1 << n) - 1
    best = 0
    while alive:
        vmin, dmin = -1, n + 1
        rest = alive
        while rest:
            u = (rest & -rest).bit_length() - 1
            rest &= rest - 1
            d = bin(masks[u] & alive).count("1")
            if d < dmin:
                dmin, vmin = d, u
        best = max(best, dmin)
        alive &= ~(1 << vmin)
    return best


def treewidth_bounded(masks: Sequence[int], deadline_seconds: float = 60.0,
                      node_budget_per_call: int = 5_000_000) -> dict:
    """Exact treewidth by the decision search between MMD and min-fill.

    Returns `lo`, `hi` (exact bounds on the treewidth), `exact` (lo == hi),
    `order` (an elimination ordering of width `hi`), `nodes`, `seconds`, and
    `censored` when the deadline or budget stopped a call: then the interval
    is what was proved and nothing more.
    """
    started = time.monotonic()
    hi, order = min_fill_upper_bound(masks)
    lo = mmd_lower_bound(masks)
    nodes_total = 0
    censored = False
    k = lo
    while lo < hi:
        remaining = deadline_seconds - (time.monotonic() - started)
        if remaining <= 0:
            censored = True
            break
        status, found, nodes = treewidth_decide(masks, k, budget=node_budget_per_call)
        nodes_total += nodes
        if status == "yes":
            hi, order = k, found
        elif status == "no":
            lo = k + 1
            k += 1
        else:
            censored = True
            break
    return {"lo": int(lo), "hi": int(hi), "exact": bool(lo == hi), "order": order,
            "nodes": int(nodes_total), "seconds": round(time.monotonic() - started, 3),
            "censored": censored}


def treewidth(masks: Sequence[int], deadline_seconds: float = 60.0) -> dict:
    """The DP when it fits, the decision search otherwise; one result shape."""
    started = time.monotonic()
    if len(masks) <= DP_MAX_N:
        width, order = treewidth_exact(masks)
        return {"lo": width, "hi": width, "exact": True, "order": order, "nodes": 0,
                "seconds": round(time.monotonic() - started, 3), "censored": False,
                "method": "dp"}
    out = treewidth_bounded(masks, deadline_seconds)
    out["method"] = "bb"
    return out


# ----------------------------------------------------------------------------
# self-check
# ----------------------------------------------------------------------------


def _self_check() -> None:
    import networkx as nx

    cases = [
        ("P8", nx.path_graph(8), 1), ("C9", nx.cycle_graph(9), 2),
        ("K6", nx.complete_graph(6), 5), ("grid 3×4", nx.convert_node_labels_to_integers(nx.grid_2d_graph(3, 4)), 3),
        ("grid 4×5", nx.convert_node_labels_to_integers(nx.grid_2d_graph(4, 5)), 4),
        ("Petersen", nx.petersen_graph(), 4), ("K3,3", nx.complete_bipartite_graph(3, 3), 3),
        ("grid 5×5", nx.convert_node_labels_to_integers(nx.grid_2d_graph(5, 5)), 5),
    ]
    for name, g, expect in cases:
        masks = masks_from_graph(g)
        t = time.monotonic()
        width, order = treewidth_exact(masks)
        dt = time.monotonic() - t
        bb = treewidth_bounded(masks, 30)
        assert elimination_width(masks, order) == width
        print(f"{name:10s} dp {width} ({dt:.3f} s)  bb [{bb['lo']}, {bb['hi']}] "
              f"{bb['nodes']} nodes {bb['seconds']} s  expected {expect}")
        assert width == expect and bb["lo"] == bb["hi"] == expect
    print("ok")


if __name__ == "__main__":
    _self_check()
