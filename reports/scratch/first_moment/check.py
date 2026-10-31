"""Small-instance check for FirstMoment.lean (2026-10-31).

For every n in 1..6 and every k < n, enumerate all 2^C(n,2) labelled graphs on
Fin n, compute each pathwidth with the subset DP, and verify

    #{G : pw(G) <= k} <= C(n,t) * C(n-t,t-1) * 2^(C(n,2) - t(t-1)),  t = (n-k+1)//2,

plus the two corollaries (the multiplied-through form and, at p = 0.3, the
weighted form), plus card_graphs_avoiding for every disjoint (A, R) at n <= 5.

Run from the repository root: python reports/scratch/first_moment/check.py
"""
import itertools
import sys
from fractions import Fraction
from math import comb

sys.path.insert(0, "/home/al/dev/MOSP")
import networkx as nx  # noqa: E402

from fixed_parameter_algorithm.pathwidth import compute_pathwidth  # noqa: E402


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main():
    violations = 0
    for n in range(1, 7):
        C = comb(n, 2)
        pw = []
        edge_sets = []
        for edges in all_graphs(n):
            G = nx.Graph()
            G.add_nodes_from(range(n))
            G.add_edges_from(edges)
            pw.append(compute_pathwidth(G)[0] if n > 0 else 0)
            edge_sets.append(edges)
        total = len(pw)
        assert total == 2 ** C
        print(f"n={n}: {total} graphs = 2^{C}; pathwidth histogram "
              f"{ {w: pw.count(w) for w in sorted(set(pw))} }")
        p = Fraction(3, 10)
        for k in range(n):
            t = (n - k + 1) // 2
            lhs = sum(1 for w in pw if w <= k)
            rhs = comb(n, t) * comb(n - t, t - 1) * 2 ** (C - t * (t - 1))
            ok = lhs <= rhs
            # corollary 1 (multiplied through)
            ok1 = lhs * 2 ** (t * (t - 1)) <= comb(n, t) * comb(n - t, t - 1) * 2 ** C
            # weighted corollary at p = 3/10
            wsum = sum(p ** len(e) * (1 - p) ** (C - len(e))
                       for w, e in zip(pw, edge_sets) if w <= k)
            wrhs = comb(n, t) * comb(n - t, t - 1) * (1 - p) ** (t * (t - 1))
            ok2 = wsum <= wrhs
            if not (ok and ok1 and ok2):
                violations += 1
            print(f"  k={k} t={t}: #{{pw<=k}}={lhs} <= C({n},{t})*C({n-t},{t-1})"
                  f"*2^({C}-{t*(t-1)})={rhs} {'OK' if ok else 'VIOLATION'};"
                  f" mult {'OK' if ok1 else 'VIOLATION'};"
                  f" weighted(p=0.3) {float(wsum):.6f} <= {float(wrhs):.6f}"
                  f" {'OK' if ok2 else 'VIOLATION'}")
        # card_graphs_avoiding: for every disjoint (A, R), count graphs with no A-R edge
        if n <= 5:
            checked = 0
            for A in itertools.chain.from_iterable(
                    itertools.combinations(range(n), a) for a in range(n + 1)):
                rest = [v for v in range(n) if v not in A]
                for R in itertools.chain.from_iterable(
                        itertools.combinations(rest, r) for r in range(len(rest) + 1)):
                    cnt = sum(1 for e in edge_sets
                              if not any((a, r) in e or (r, a) in e
                                         for a in A for r in R))
                    expect = 2 ** (C - len(A) * len(R))
                    if cnt != expect:
                        violations += 1
                        print(f"  AVOID VIOLATION A={A} R={R}: {cnt} != {expect}")
                    checked += 1
            print(f"  card_graphs_avoiding: {checked} disjoint (A, R) pairs checked, "
                  f"all equal to 2^(C(n,2) - |A||R|)")
    print(f"violations: {violations}")


if __name__ == "__main__":
    main()
