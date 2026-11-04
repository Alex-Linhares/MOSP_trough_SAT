"""Classes with `O(n)`-bit layouts? The structural claims of loop0014 item 04
(`reports/subexp_pathwidth.md` §4), each checked by brute force against
vertex separation on every graph of the networkx atlas (all graphs to 7
vertices) before it was stated.

    python -m learning.subexp_classes            # the full check, atlas to 7
    python -m learning.subexp_classes --nmax 5   # quick

Graphs are `(n, adj)` as in `paper1/complex_check.py`; `vs` is Kinnersley's
vertex separation (`= pw`), evaluated by the prefix-set DP of
`learning.subexp_reductions` (itself checked against the permutation minimum
on every atlas graph, §3.5) and, where the claim is about *layouts* rather
than values, by `itertools.permutations`.

The claims:

- **Cobipartite normal form** (§4.1). For `H` with cliques `A`, `B`, some
  optimal layout places one clique entirely first. With `X` first and `Y` the
  other side laid out by `τ`, the value is
  `max(|X| − 1, max_{0 ≤ t < |Y|} (t + |N_X(Y_{>t})|))`, so
  `vs(H) = min_{X ∈ {A, B}} max(|X| − 1, chain_X)`, where `chain_X` is the
  minimum over orderings of `Y` — a chain through the one-sided lattice
  `{S ⊆ Y : |N_X(S)| − |S| ≤ c}`. `cobipartite_normal_form` evaluates it.
- **Split dichotomy** (§4.2). For a split graph with partition `(K, I)`,
  `|K| = κ ≥ 1`: `vs ∈ {κ − 1, κ}`, and `vs = κ − 1` iff some `v ∈ K` has
  a `u ∈ K` adjacent to none of `v`'s independent neighbours.
  `split_formula` evaluates it.
- **Twin lemma / unit DP** (§4.5). Twins (`N(x) ∖ {y} = N(y) ∖ {x}`) can be
  laid out consecutively in some optimal layout, so `vs` is a DP over subsets
  of twin classes: `O*(2^u)`, `u` the number of classes. `twin_unit_dp`.
- **Orientations are not certificates** (§4.3): on subcubic graphs the
  acyclic orientation induced by a layout does not determine the value;
  `orientation_spread` measures how often its linear extensions disagree.
- **The gap lemma** (§4.6): the arithmetic of chain certificates at spacing
  `g` against the two budgets of §1.3.8, `gap_table`.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

from learning.subexp_reductions import atlas, vs
from paper1.complex_check import graph, vertex_separation, vs_of_layout

OUT = Path("reports/scratch/subexp_pathwidth/04_classes")
INF = 10 ** 9


def popcount(x: int) -> int:
    return bin(x).count("1")


def bits(x: int):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


# ----------------------------------------------------------------------------
# cobipartite graphs
# ----------------------------------------------------------------------------


def is_clique(g, mask: int) -> bool:
    n, adj = g
    return all((adj[v] | (1 << v)) & mask == mask for v in bits(mask))


def is_independent(g, mask: int) -> bool:
    n, adj = g
    return all(adj[v] & mask == 0 for v in bits(mask))


def cobipartitions(g):
    """Every `(A, B)` with `A ∪ B = V`, both cliques, `A` containing vertex 0
    (so each unordered partition once)."""
    n, adj = g
    full = (1 << n) - 1
    for A in range(1, 1 << n, 2):
        B = full & ~A
        if is_clique(g, A) and is_clique(g, B):
            yield A, B


def chain_value(g, X: int, Y: int) -> int:
    """`min_τ max_{0 ≤ t < |Y|} (t + |N_X(Y_{>t})|)` by a DP over suffix sets of
    `Y`: `f(S) = max(cost(S), min_{v ∈ S} f(S ∖ v))`, `cost(S) = |Y| − |S| +
    |N_X(S)|`, `f(∅) = 0`; the answer is `f(Y)`."""
    n, adj = g
    y = popcount(Y)
    if y == 0:
        return 0

    @lru_cache(maxsize=None)
    def f(S: int) -> int:
        if S == 0:
            return 0
        nx = 0
        for v in bits(S):
            nx |= adj[v]
        cost = y - popcount(S) + popcount(nx & X)
        return max(cost, min(f(S & ~(1 << v)) for v in bits(S)))

    return f(Y)


def cobipartite_normal_form(g, A: int, B: int) -> int:
    """`vs(H)` by the normal form: `min_X max(|X| − 1, chain_X)`."""
    vals = []
    for X, Y in ((A, B), (B, A)):
        if X == 0:
            continue
        vals.append(max(popcount(X) - 1, chain_value(g, X, Y)))
    return min(vals)


def cobipartite_decision(g, A: int, B: int, k: int) -> bool:
    """Corollary 4.2 as stated: `vs(H) ≤ k` iff for `X = A` or `X = B`,
    `|X| − 1 ≤ k` and some chain `∅ = S_0 ⊂ S_1 ⊂ … ⊂ S_|Y| = Y` has
    `|N_X(S_s)| − s ≤ k − |Y|` for every `1 ≤ s ≤ |Y|` (`S_0` unconstrained).
    Evaluated by a DP over subsets of `Y`."""
    n, adj = g
    for X, Y in ((A, B), (B, A)):
        if X == 0 or popcount(X) - 1 > k:
            continue
        c = k - popcount(Y)

        @lru_cache(maxsize=None)
        def ok(S: int) -> bool:
            if S == 0:
                return True
            nx = 0
            for v in bits(S):
                nx |= adj[v]
            if popcount(nx & X) - popcount(S) > c:
                return False
            return any(ok(S & ~(1 << v)) for v in bits(S))

        if ok(Y):
            return True
    return False


def one_side_first_layout_value(g, X: int, Y: int) -> int:
    """The literal minimum over layouts that place all of `X` before all of
    `Y` (every order of `X`, every order of `Y`): the normal form's claim
    about *layouts*, not just its formula."""
    xs, ys = list(bits(X)), list(bits(Y))
    best = INF
    for px in itertools.permutations(xs):
        for py in itertools.permutations(ys):
            best = min(best, vs_of_layout(g, list(px) + list(py)))
    return best


def bipartite_patterns(a: int, b: int):
    """Every cobipartite graph with cliques of sizes `a` and `b`: vertices
    `0..a-1` are `A`, `a..a+b-1` are `B`, one graph per `A × B` edge set."""
    n = a + b
    base = []
    for u in range(a):
        for v in range(u + 1, a):
            base.append((u, v))
    for u in range(a, n):
        for v in range(u + 1, n):
            base.append((u, v))
    cross = [(u, a + v) for u in range(a) for v in range(b)]
    A = (1 << a) - 1
    B = ((1 << n) - 1) & ~A
    for m in range(1 << len(cross)):
        es = base + [cross[i] for i in range(len(cross)) if m >> i & 1]
        yield graph(n, es), A, B


# ----------------------------------------------------------------------------
# split graphs
# ----------------------------------------------------------------------------


def split_partitions(g):
    """Every `(K, I)` with `K` a clique, `I = V ∖ K` independent, `K ≠ ∅`."""
    n, adj = g
    full = (1 << n) - 1
    for K in range(1, 1 << n):
        I = full & ~K
        if is_clique(g, K) and is_independent(g, I):
            yield K, I


def split_criterion(g, K: int, I: int) -> bool:
    """Some `v ∈ K` whose independent neighbours have a common non-neighbour
    `u ∈ K` (vacuous for a `v` with no independent neighbour)."""
    n, adj = g
    for v in bits(K):
        NI = adj[v] & I
        hit = 0
        for i in bits(NI):
            hit |= adj[i]
        if (K & ~hit) != 0:
            return True
    return False


def split_formula(g, K: int, I: int) -> int:
    kappa = popcount(K)
    return kappa - 1 if split_criterion(g, K, I) else kappa


def random_split_graph(n: int, rng: random.Random):
    kappa = rng.randint(1, n)
    K = (1 << kappa) - 1
    es = [(u, v) for u in range(kappa) for v in range(u + 1, kappa)]
    for i in range(kappa, n):
        for u in range(kappa):
            if rng.random() < rng.choice((0.2, 0.5, 0.8)):
                es.append((u, i))
    return graph(n, es), K, ((1 << n) - 1) & ~K


# ----------------------------------------------------------------------------
# twins and the unit DP
# ----------------------------------------------------------------------------


def twin_classes(g) -> list[int]:
    """Classes of the relation `x ~ y` iff `N(x) ∖ {y} = N(y) ∖ {x}` (true or
    false twins; it is an equivalence: each class is a clique or an
    independent set that is a module)."""
    n, adj = g
    classes: list[int] = []
    seen = 0
    for x in range(n):
        if seen >> x & 1:
            continue
        cls = 1 << x
        for y in range(x + 1, n):
            if seen >> y & 1:
                continue
            if adj[x] & ~(1 << y) == adj[y] & ~(1 << x):
                cls |= 1 << y
        seen |= cls
        classes.append(cls)
    return classes


def cut(g, placed: int) -> int:
    n, adj = g
    return sum(1 for v in bits(placed) if adj[v] & ~placed)


def block_cost(g, P: int, Q: int) -> int:
    """The largest cut while the class `Q` is placed consecutively after the
    prefix set `P` (any internal order: the members are twins)."""
    best, cur = 0, P
    for v in bits(Q):
        cur |= 1 << v
        best = max(best, cut(g, cur))
    return best


def twin_unit_dp(g) -> tuple[int, int]:
    """`(vs, u)`: vertex separation by a DP over subsets of twin classes, and
    the number of classes."""
    n, adj = g
    if n <= 1:
        return 0, n
    classes = twin_classes(g)
    u = len(classes)

    @lru_cache(maxsize=None)
    def f(S: int) -> int:        # S: subset of classes, as a mask over classes
        if S == 0:
            return 0
        best = INF
        for i in bits(S):
            rest = S & ~(1 << i)
            P = 0
            for j in bits(rest):
                P |= classes[j]
            best = min(best, max(f(rest), block_cost(g, P, classes[i])))
        return best

    return f((1 << u) - 1), u


def consecutive_twin_layout_value(g) -> int:
    """Minimum over layouts in which every twin class is consecutive — the
    literal form of the twin lemma."""
    n, adj = g
    classes = twin_classes(g)
    best = INF
    for order in itertools.permutations(range(len(classes))):
        lay = []
        for i in order:
            lay.extend(bits(classes[i]))
        best = min(best, vs_of_layout(g, lay))
    return best


# ----------------------------------------------------------------------------
# orientations on subcubic graphs
# ----------------------------------------------------------------------------


def orientation_spread(g) -> dict:
    """Group every layout by the acyclic orientation it induces (edge `uv`
    oriented from the earlier endpoint); per orientation the min and max
    layout value over its linear extensions."""
    n, adj = g
    es = [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1]
    lo: dict[int, int] = {}
    hi: dict[int, int] = {}
    for p in itertools.permutations(range(n)):
        pos = [0] * n
        for i, v in enumerate(p):
            pos[v] = i
        key = 0
        for i, (u, v) in enumerate(es):
            if pos[u] > pos[v]:
                key |= 1 << i
        val = vs_of_layout(g, p)
        lo[key] = min(lo.get(key, INF), val)
        hi[key] = max(hi.get(key, -1), val)
    v = min(lo.values())
    return {"orientations": len(lo),
            "disagreeing": sum(1 for k in lo if lo[k] != hi[k]),
            "optimal_orientations": sum(1 for k in lo if lo[k] == v),
            "optimal_but_not_forced": sum(1 for k in lo if lo[k] == v and hi[k] != v),
            "max_spread": max(hi[k] - lo[k] for k in lo)}


# ----------------------------------------------------------------------------
# the gap lemma's arithmetic
# ----------------------------------------------------------------------------


def gap_table(ns=(125, 10 ** 3, 10 ** 4, 10 ** 6, 10 ** 9, 10 ** 15, 10 ** 21, 10 ** 24)) -> list[dict]:
    """Lemma 4.6 against the two budgets of §1.3.8 (`log` natural in the
    budgets, bits in `log₂`). Verified route: bits `n log₂(n/(e g))` against
    `B_v = n √log n / (log log n)²`, and the smallest `g` that fits. Paper
    route: the same against `B_p = n √log n` (the wire count `s ≤ B_p`), and
    at that `g` the width `g log₂(n/g)` of one segment tensor against
    `s^{9/10} ≤ B_p^{9/10}`."""
    rows = []
    for n in ns:
        L = math.log(n)
        Bv = n * math.sqrt(L) / (math.log(L)) ** 2
        Bp = n * math.sqrt(L)
        gv = max(1.0, n / (math.e * 2 ** (Bv / n)))
        gp = max(1.0, n / (math.e * 2 ** (Bp / n)))
        width_p = gp * math.log2(n / gp) if gp < n else 0.0
        rows.append({"n": n, "Bv": Bv, "Bv_over_n": Bv / n, "gv_over_n": gv / n,
                     "Bp": Bp, "gp_over_n": gp / n, "segment_width_p": width_p,
                     "Bp_9_10": Bp ** 0.9, "ratio_p": width_p / Bp ** 0.9})
    return rows


# ----------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------


def run_checks(nmax: int = 7, out_dir: Path = OUT, log=print, patterns_max: int = 8,
               layout_nmax: int = 7, split_random: int = 300, split_random_n: int = 11,
               seed: int = 0) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    graphs = atlas(nmax)
    res: dict = {"nmax": nmax, "graphs": len(graphs)}
    fails: dict[str, list] = {k: [] for k in
                              ["cobipartite_formula_atlas", "cobipartite_layouts_atlas",
                               "cobipartite_formula_patterns", "cobipartite_decision",
                               "split_formula_atlas",
                               "split_formula_random", "split_dichotomy", "twin_dp",
                               "twin_layouts"]}
    counts: Counter = Counter()

    # cobipartite: every atlas graph, every cobipartition
    for g in graphs:
        v = vs(g)
        for A, B in cobipartitions(g):
            counts["cobipartite_pairs"] += 1
            if cobipartite_normal_form(g, A, B) != v:
                fails["cobipartite_formula_atlas"].append((g, A, B))
            for k in range(0, g[0] + 1):
                counts["cobipartite_decisions"] += 1
                if cobipartite_decision(g, A, B, k) != (v <= k):
                    fails["cobipartite_decision"].append((g, A, B, k))
            if g[0] <= layout_nmax:
                lay = min(one_side_first_layout_value(g, A, B),
                          one_side_first_layout_value(g, B, A))
                if lay != v:
                    fails["cobipartite_layouts_atlas"].append((g, A, B))
    counts["cobipartite_atlas_graphs"] = sum(1 for g in graphs if any(True for _ in cobipartitions(g)))
    log(f"cobipartite: {counts['cobipartite_atlas_graphs']} atlas graphs, "
        f"{counts['cobipartite_pairs']} (graph, partition) pairs; formula failures "
        f"{len(fails['cobipartite_formula_atlas'])}, layout failures "
        f"{len(fails['cobipartite_layouts_atlas'])}; Corollary 4.2 on "
        f"{counts['cobipartite_decisions']} (pair, k) decisions, failures "
        f"{len(fails['cobipartite_decision'])}  [{time.time() - t0:.1f}s]")

    # cobipartite: every A × B pattern with a + b <= patterns_max, a <= b
    for a in range(1, patterns_max):
        for b in range(a, patterns_max - a + 1):
            k = 0
            for g, A, B in bipartite_patterns(a, b):
                k += 1
                if cobipartite_normal_form(g, A, B) != vs(g):
                    fails["cobipartite_formula_patterns"].append((g, A, B))
            counts[f"patterns_{a}_{b}"] = k
            counts["patterns"] += k
    log(f"cobipartite patterns to {patterns_max} vertices: {counts['patterns']} graphs; "
        f"failures {len(fails['cobipartite_formula_patterns'])}  [{time.time() - t0:.1f}s]")

    # split: every atlas graph, every split partition
    for g in graphs:
        v = vs(g)
        parts = list(split_partitions(g))
        if parts:
            counts["split_atlas_graphs"] += 1
        for K, I in parts:
            counts["split_pairs"] += 1
            kappa = popcount(K)
            if v not in (kappa - 1, kappa):
                fails["split_dichotomy"].append((g, K))
            if split_formula(g, K, I) != v:
                fails["split_formula_atlas"].append((g, K))
            counts["split_value_kappa_minus_1" if v == kappa - 1 else "split_value_kappa"] += 1
    log(f"split: {counts['split_atlas_graphs']} atlas graphs, {counts['split_pairs']} "
        f"(graph, partition) pairs; dichotomy failures {len(fails['split_dichotomy'])}, "
        f"formula failures {len(fails['split_formula_atlas'])}  [{time.time() - t0:.1f}s]")
    rng = random.Random(seed)
    for _ in range(split_random):
        g, K, I = random_split_graph(split_random_n, rng)
        if split_formula(g, K, I) != vs(g):
            fails["split_formula_random"].append((g, K))
    log(f"split random: {split_random} graphs on {split_random_n} vertices; failures "
        f"{len(fails['split_formula_random'])}  [{time.time() - t0:.1f}s]")

    # twins: the unit DP and the consecutive-layout minimum
    units = Counter()
    for g in graphs:
        v = vs(g)
        d, u = twin_unit_dp(g)
        units[(g[0], u)] += 1
        if d != v:
            fails["twin_dp"].append(g)
        if g[0] <= layout_nmax and consecutive_twin_layout_value(g) != v:
            fails["twin_layouts"].append(g)
    counts["twin_graphs_with_fewer_units"] = sum(c for (n, u), c in units.items() if u < n)
    log(f"twins: unit DP failures {len(fails['twin_dp'])}, consecutive-layout failures "
        f"{len(fails['twin_layouts'])}; graphs with u < n: "
        f"{counts['twin_graphs_with_fewer_units']} of {len(graphs)}  [{time.time() - t0:.1f}s]")

    # orientations on subcubic graphs
    orient = Counter()
    spread_hist = Counter()
    for g in graphs:
        n, adj = g
        if n < 2 or max(popcount(a) for a in adj) > 3 or n > layout_nmax:
            continue
        r = orientation_spread(g)
        orient["graphs"] += 1
        orient["orientations"] += r["orientations"]
        orient["disagreeing"] += r["disagreeing"]
        orient["optimal_orientations"] += r["optimal_orientations"]
        orient["optimal_but_not_forced"] += r["optimal_but_not_forced"]
        orient["graphs_with_a_disagreeing_orientation"] += r["disagreeing"] > 0
        orient["graphs_with_an_unforced_optimal_orientation"] += r["optimal_but_not_forced"] > 0
        spread_hist[r["max_spread"]] += 1
    log(f"orientations (subcubic, ≤ {layout_nmax}): {orient['graphs']} graphs, "
        f"{orient['orientations']} acyclic orientations, {orient['disagreeing']} with "
        f"disagreeing linear extensions, {orient['optimal_but_not_forced']} of "
        f"{orient['optimal_orientations']} optimal ones not forced; max spread histogram "
        f"{dict(sorted(spread_hist.items()))}  [{time.time() - t0:.1f}s]")

    gap = gap_table()
    for r in gap:
        log(f"gap: n={r['n']:>7.0e}  verified B_v/n {r['Bv_over_n']:.3f} g/n {r['gv_over_n']:.3f} | "
            f"paper B_p/n {r['Bp'] / r['n']:.3f} g/n {r['gp_over_n']:.3f} "
            f"width {r['segment_width_p']:.3g} B_p^0.9 {r['Bp_9_10']:.3g} ratio {r['ratio_p']:.3g}")

    res["counts"] = dict(counts)
    res["units_by_n"] = {str(k): c for k, c in sorted(units.items())}
    res["orientations"] = dict(orient)
    res["orientation_spread_hist"] = {str(k): c for k, c in sorted(spread_hist.items())}
    res["gap_table"] = gap
    res["failures"] = {k: len(v) for k, v in fails.items()}
    res["failure_examples"] = {k: [str(x) for x in v[:3]] for k, v in fails.items() if v}
    res["seconds"] = time.time() - t0
    (out_dir / "check.json").write_text(json.dumps(res, indent=1))
    log(f"total failures: {sum(res['failures'].values())}  [{res['seconds']:.1f}s]")
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=7)
    ap.add_argument("--patterns-max", type=int, default=8)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    res = run_checks(nmax=a.nmax, out_dir=a.out, patterns_max=a.patterns_max)
    sys.exit(0 if sum(res["failures"].values()) == 0 else 1)


if __name__ == "__main__":
    main()
