"""Brute-force check of Lemma P exactly as `PendantCliques.lean` states it, before it is stated.

For every random graph `G` on `n ≤ 8` vertices (exact pathwidth by the subset DP) and every
clique `R` of `G`: the cliques `Q` with `|Q ∩ R| = 1`, grouped by their meeting vertex `v`,
the largest per vertex; for each `q`, the `q` largest give `t` (the smallest of them) and
the statement `t + ⌈q/2⌉ ≤ pw(G) + 2`. Any choice of `q` pendant cliques at distinct vertices
is dominated by this one. Also the clique floor `|R| ≤ pw + 1` and F2's exact value on the
depth-one family, as `pathwidth_cliqueWithPendants` would state it.

    python reports/scratch/pendant_cliques/check.py > reports/scratch/pendant_cliques/check.log
"""
from __future__ import annotations

import itertools
import math
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from fixed_parameter_algorithm.pathwidth import compute_pathwidth  # noqa: E402


def lemma_p_best(g: nx.Graph, cliques: list[frozenset]) -> tuple[int, tuple]:
    best, arg = -1, ()
    for R in cliques:
        per_vertex: dict[int, int] = {}
        for Q in cliques:
            meet = Q & R
            if len(meet) == 1:
                (v,) = meet
                per_vertex[v] = max(per_vertex.get(v, 0), len(Q))
        sizes = sorted(per_vertex.values(), reverse=True)
        for q in range(1, len(sizes) + 1):
            t = sizes[q - 1]
            val = t + (q + 1) // 2 - 2
            if val > best:
                best, arg = val, (tuple(sorted(R)), q, t)
    return best, arg


def clique_with_pendants(s: int, t: int, q: int) -> nx.Graph:
    g = nx.complete_graph(s)
    nxt = s
    for v in range(q):
        block = [v] + list(range(nxt, nxt + t - 1))
        nxt += t - 1
        g.add_edges_from(itertools.combinations(block, 2))
    return g


def main() -> int:
    rng = np.random.default_rng(1301)
    t0 = time.time()
    checked = violations = tight = beats_clique = 0
    per_n: dict[int, list[int]] = {}
    for n in range(2, 9):
        for _ in range(300):
            p = float(rng.uniform(0.2, 0.9))
            g = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
            if g.number_of_edges() == 0:
                continue
            pw = compute_pathwidth(g)[0]
            cliques = [frozenset(c) for c in nx.enumerate_all_cliques(g)]
            omega = max(len(c) for c in cliques)
            best, arg = lemma_p_best(g, cliques)
            checked += 1
            if best > pw:
                violations += 1
                print(f"VIOLATION n={n} edges={sorted(g.edges())} pw={pw} bound={best} at {arg}")
            tight += best == pw
            beats_clique += best > omega - 1
            per_n.setdefault(n, [0, 0, 0])
            per_n[n][0] += 1
            per_n[n][1] += best == pw
            per_n[n][2] += best > omega - 1
    print(f"random graphs: {checked} checked, {violations} violations, tight on {tight}, "
          f"above the clique floor on {beats_clique}; {time.time() - t0:.1f} s")
    print("n | graphs | tight | above clique floor")
    for n, (c, ti, bc) in sorted(per_n.items()):
        print(f"{n} | {c} | {ti} | {bc}")
    # F2 exact on the depth-one family, n <= 15
    f2_checked = f2_bad = 0
    for s in range(2, 7):
        for t in range(2, 7):
            for q in range(1, s + 1):
                g = clique_with_pendants(s, t, q)
                if g.number_of_nodes() > 15:
                    continue
                pw = compute_pathwidth(g)[0]
                want = max(s - 1, t + (q + 1) // 2 - 2)
                f2_checked += 1
                if pw != want:
                    f2_bad += 1
                    print(f"F2 MISMATCH s={s} t={t} q={q} pw={pw} formula={want}")
    print(f"F2 family: {f2_checked} graphs (n ≤ 15), {f2_bad} mismatches; {time.time() - t0:.1f} s")
    return 1 if violations or f2_bad else 0


if __name__ == "__main__":
    sys.exit(main())
