#!/usr/bin/env python3
"""Brute-force check of every statement of `lean/MOSPFormalization/DegreeBound/Potential.lean`
(loop0012 item 05; `reports/edwards_mcdermid.md` §5) in exact rationals, before it is
stated, on random graphs at n ≤ 12 with random isolated vertices (the Lean design keeps
removed vertices isolated, so every statement must hold with them present):

  D1   degree_isolate: deg_{G−w}(v) = 0 if v = w, deg(v) − 1 if v ~ w, deg(v) otherwise
  P1   potential_isolate: f(G − w) = f(G) − g(d(w)) − Σ_{v ∈ N(w)} g'(d(v))
  P2   potential_isolate_le_sub_one: degrees 0 or ≥ 3, d(w) = Δ ≥ 4 maximum, some
       neighbour of degree ≤ Δ − 1 ⇒ f(G − w) ≤ f(G) − 1
  P2n  potential_isolate_regular: d(w) = Δ ≥ 4 and EVERY NEIGHBOUR of w of degree Δ ⇒
       f(G − w) = f(G) − 1 + g'(Δ − 1) − g'(Δ)   (item 02 checked this for Δ-regular
       graphs only; the Lean statement needs only the neighbours, so it is re-checked)
  V1   potentialMinus_eq_sum_vertexTerm: f⁻(G) = Σ_v (g(d(v)) − g'(δ(C_v)) / |C_v|),
       C_v the component of v (singletons for isolated vertices)
  V2   potentialMinus_eq_sum_compPotential: f⁻(G) = Σ_C (Σ_{v ∈ C} g(d(v)) − g'(δ(C)));
       compPotential_nonneg: every summand ≥ 0
  M1   potentialMinus_le_potential: f⁻ ≤ f
  M2   potentialMinus_le_F: f⁻ ≤ F = f − g'(δ(G)), δ(G) the minimum over the support
  M3   potentialMinus_eq_F_of_connected: support connected (and non-empty) ⇒ f⁻ = F
  A1   potentialMinus_add: supports disjoint ⇒ f⁻(G₁ ⊔ G₂) = f⁻(G₁) + f⁻(G₂)
       (10,000 random disjoint unions; and the reachability characterisation behind it:
       reachable in G₁ ⊔ G₂ iff reachable in G₁ or in G₂)
  B1   potentialMinus_cubic: support connected, cubic on the support ⇒ f⁻ = N/6 − 1/6
  B2   potentialMinus_ge_five_sixths: support connected, degrees 0 or ≥ 3, some degree
       ≥ 4 ⇒ f⁻ ≥ 5/6

    nice -n 19 python3 reports/scratch/edwards_mcdermid/05_potential/check.py
"""
from __future__ import annotations

import collections
import json
import random
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/home/al/dev/MOSP")

from learning.edwards_mcdermid import (  # noqa: E402
    F_global, bits, components, degrees, f_potential, fminus, g, g_prime,
    global_min_degree, isolate, min_degree, support,
)

HERE = "/home/al/dev/MOSP/reports/scratch/edwards_mcdermid/05_potential"


def random_graph(rng, n, p, isolated=0):
    """A G(n, p) on the first n − isolated vertices; the rest isolated."""
    adj = [0] * n
    live = list(range(n))
    rng.shuffle(live)
    live = live[: n - isolated]
    for i, u in enumerate(live):
        for v in live[i + 1:]:
            if rng.random() < p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return adj


def random_cubic(rng, n_cubic, n_total):
    """A random connected cubic graph on n_cubic vertices (networkx), embedded in
    n_total vertices with the rest isolated; None if networkx fails to connect."""
    import networkx as nx
    H = nx.random_regular_graph(3, n_cubic, seed=rng.randrange(1 << 30))
    if not nx.is_connected(H):
        return None
    verts = list(range(n_total))
    rng.shuffle(verts)
    place = verts[:n_cubic]
    adj = [0] * n_total
    for a, b in H.edges():
        u, v = place[a], place[b]
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def reach_mask(adj, v):
    comp = 1 << v
    frontier = comp
    while frontier:
        nxt = 0
        for u in bits(frontier):
            nxt |= adj[u]
        nxt &= ~comp
        comp |= nxt
        frontier = nxt
    return comp


def vertex_term(adj, v):
    C = reach_mask(adj, v)
    return g(adj[v].bit_count()) - g_prime(min_degree(adj, C)) / C.bit_count()


def comp_potential(adj, C):
    return sum((g(adj[v].bit_count()) for v in bits(C)), Fraction(0)) - g_prime(min_degree(adj, C))


def support_connected(adj):
    s = support(adj)
    if s == 0:
        return False
    v = next(iter(bits(s)))
    return (reach_mask(adj, v) & s) == s and reach_mask(adj, v) == s


def main():
    rng = random.Random(20261102)
    cnt = collections.Counter()
    bad = []
    t0 = time.time()
    log = open(f"{HERE}/check.log", "w")

    def say(msg):
        print(msg)
        log.write(msg + "\n")
        log.flush()

    def fail(tag, adj, msg):
        bad.append((tag, adj, msg))
        say(f"VIOLATION {tag}: adj={adj} {msg}")

    # ---- single graphs: D1, P1, P2, P2n, V1, V2, M1, M2, M3, B2 ------------
    graphs = []
    for _ in range(20000):
        n = rng.randint(1, 12)
        p = rng.choice([0.2, 0.4, 0.6, 0.8, 0.95])
        iso = rng.randint(0, min(3, n - 1)) if n > 1 else 0
        graphs.append(random_graph(rng, n, p, iso))
    for adj in graphs:
        n = len(adj)
        deg = degrees(adj)
        f_G = f_potential(adj)
        fm = fminus(adj)
        Delta = max(deg)
        for w in range(n):
            H = isolate(adj, w)
            dH = degrees(H)
            for v in range(n):
                cnt["D1"] += 1
                want = 0 if v == w else (deg[v] - 1 if (adj[w] >> v) & 1 else deg[v])
                if dH[v] != want:
                    fail("D1", adj, f"w={w} v={v}")
            cnt["P1"] += 1
            rhs = f_G - g(deg[w]) - sum((g_prime(deg[v]) for v in bits(adj[w])), Fraction(0))
            if f_potential(H) != rhs:
                fail("P1", adj, f"w={w}")
            reduced = all(d == 0 or d >= 3 for d in deg)
            if reduced and deg[w] == Delta and Delta >= 4:
                if any(deg[v] <= Delta - 1 for v in bits(adj[w])):
                    cnt["P2"] += 1
                    if not f_potential(H) <= f_G - 1:
                        fail("P2", adj, f"w={w}")
            if deg[w] == Delta and Delta >= 4 and all(deg[v] == Delta for v in bits(adj[w])):
                cnt["P2n"] += 1
                if f_potential(H) != f_G - 1 + g_prime(Delta - 1) - g_prime(Delta):
                    fail("P2n", adj, f"w={w} (neighbours-only regular identity)")
        cnt["V1"] += 1
        if fm != sum((vertex_term(adj, v) for v in range(n)), Fraction(0)):
            fail("V1", adj, "per-vertex form")
        comps = components(adj, support_only=False)
        cnt["V2"] += 1
        if fm != sum((comp_potential(adj, C) for C in comps), Fraction(0)):
            fail("V2", adj, "per-component form")
        for C in comps:
            cnt["V2nonneg"] += 1
            if comp_potential(adj, C) < 0:
                fail("V2nonneg", adj, f"C={C}")
        cnt["M1"] += 1
        if not fm <= f_G:
            fail("M1", adj, "")
        cnt["M2"] += 1
        if not fm <= F_global(adj):
            fail("M2", adj, "")
        if support_connected(adj):
            cnt["M3"] += 1
            if fm != F_global(adj):
                fail("M3", adj, "connected support")
            if all(d == 0 or d >= 3 for d in deg) and Delta >= 4:
                cnt["B2"] += 1
                if not fm >= Fraction(5, 6):
                    fail("B2", adj, f"fminus={fm}")

    # ---- disjoint unions: A1 ------------------------------------------------
    for _ in range(10000):
        n = rng.randint(2, 12)
        verts = list(range(n))
        rng.shuffle(verts)
        k = rng.randint(0, n)
        A, B = verts[:k], verts[k:]
        G1, G2 = [0] * n, [0] * n
        for part, G in ((A, G1), (B, G2)):
            p = rng.choice([0.3, 0.6, 0.9])
            for i, u in enumerate(part):
                for v in part[i + 1:]:
                    if rng.random() < p:
                        G[u] |= 1 << v
                        G[v] |= 1 << u
        assert support(G1) & support(G2) == 0
        G = [G1[v] | G2[v] for v in range(n)]
        cnt["A1"] += 1
        if fminus(G) != fminus(G1) + fminus(G2):
            fail("A1", (G1, G2), f"{fminus(G)} != {fminus(G1)} + {fminus(G2)}")
        for u in range(n):
            ru, r1, r2 = reach_mask(G, u), reach_mask(G1, u), reach_mask(G2, u)
            cnt["A1reach"] += 1
            if ru != (r1 | r2):
                fail("A1reach", (G1, G2), f"u={u}")

    # ---- cubic: B1 ----------------------------------------------------------
    for _ in range(2000):
        n_cubic = rng.choice([4, 6, 8, 10, 12])
        n_total = rng.randint(n_cubic, 14)
        adj = random_cubic(rng, n_cubic, n_total)
        if adj is None:
            continue
        cnt["B1"] += 1
        if fminus(adj) != Fraction(n_cubic, 6) - Fraction(1, 6):
            fail("B1", adj, f"fminus={fminus(adj)} N={n_cubic}")

    elapsed = time.time() - t0
    say(f"counts: {dict(cnt)}")
    say(f"violations: {len(bad)}")
    say(f"elapsed: {elapsed:.1f} s")
    json.dump({"counts": dict(cnt), "violations": len(bad), "elapsed_s": elapsed,
               "seed": 20261102, "n_max": 12, "graphs": 20000, "unions": 10000},
              open(f"{HERE}/summary.json", "w"), indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
