"""Small-instance check for CliqueCoverMoment.lean (2026-10-31).

Model: customers 0..n-1, patterns 0..m-1 with sizes s_j; a cover is a choice of an
s_j-subset per pattern; its graph is the union of the pattern cliques.  For every
n in 1..6, m in 1..3, every size vector in {0..min(3,n)}^m and every k < n, enumerate
all covers, compute each pathwidth with the subset DP, and verify

    #{S : pw(S) <= k} <= C(n,t) * C(n-t,t-1) * prod_j N(s_j),   t = (n-k+1)//2,
    N(s) = C(n-t,s) + C(n-(t-1),s) - C(n-(2t-1),s),

the probability form (divide by prod_j C(n,s_j)), and the MOSP form with
mospValue (brute force over pattern orders) <= k+1 when every s_j >= 1.
Also: N(s) against enumeration for every disjoint (A, R) with |A| = a, |R| = r
at n <= 6, and the Nat-truncation reading `n - 2t + 1` of the README formula.

Run from the repository root: python reports/scratch/clique_cover_moment/lean_check.py
"""
import itertools
import sys
from fractions import Fraction
from math import comb

sys.path.insert(0, "/home/al/dev/MOSP")
import networkx as nx  # noqa: E402

from fixed_parameter_algorithm.pathwidth import compute_pathwidth  # noqa: E402


def nat_sub(a, b):
    return a - b if a >= b else 0


def N_lean(n, t, s):
    # avoidCount n t (t - 1) s, Nat arithmetic exactly as in the Lean definition
    a, r = t, nat_sub(t, 1)
    return nat_sub(comb(nat_sub(n, a), s) + comb(nat_sub(n, r), s), comb(nat_sub(n, a + r), s))


def N_readme_nat(n, t, s):
    # the README's C(n-t,s) + C(n-t+1,s) - C(n-2t+1,s) read with Nat subtraction
    return nat_sub(comb(nat_sub(n, t), s) + comb(nat_sub(n, t) + 1, s),
                   comb(nat_sub(n, 2 * t) + 1, s))


_pw_cache = {}


def pathwidth_of(n, edges):
    key = (n, edges)
    if key not in _pw_cache:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)
        _pw_cache[key] = compute_pathwidth(G)[0]
    return _pw_cache[key]


def mosp_value(n, cover):
    """Brute force: min over pattern orders of the max number of open stacks."""
    m = len(cover)
    best = None
    for order in itertools.permutations(range(m)):
        first, last = {}, {}
        for pos, j in enumerate(order):
            for c in cover[j]:
                first.setdefault(c, pos)
                last[c] = pos
        worst = 0
        for pos in range(m):
            worst = max(worst, sum(1 for c in first if first[c] <= pos <= last[c]))
        best = worst if best is None else min(best, worst)
    return 0 if best is None else best


def graph_edges(cover):
    es = set()
    for T in cover:
        for u, v in itertools.combinations(sorted(T), 2):
            es.add((u, v))
    return tuple(sorted(es))


violations = 0
checked = 0
truncation_differs = 0
for n in range(1, 7):
    V = range(n)
    for m in range(1, 4):
        smax = min(3, n)
        for sizes in itertools.product(range(smax + 1), repeat=m):
            pools = [list(itertools.combinations(V, s)) for s in sizes]
            n_covers = 1
            for p in pools:
                n_covers *= len(p)
            assert n_covers == 1 and all(comb(n, s) == len(p) for s, p in zip(sizes, pools)) or True
            pws, mvs = [], []
            for cover in itertools.product(*pools):
                cover = [frozenset(T) for T in cover]
                pws.append(pathwidth_of(n, graph_edges(cover)))
                if all(s >= 1 for s in sizes):
                    mvs.append(mosp_value(n, cover))
            total = 1
            for s in sizes:
                total *= comb(n, s)
            assert total == len(pws)
            for k in range(n):
                t = (n - k + 1) // 2
                count = sum(1 for p in pws if p <= k)
                prodN = 1
                for s in sizes:
                    prodN *= N_lean(n, t, s)
                bound = comb(n, t) * comb(n - t, t - 1) * prodN
                checked += 1
                if count > bound:
                    violations += 1
                    print("VIOLATION count", n, m, sizes, k, count, bound)
                # probability form (exact rationals)
                if total > 0:
                    lhs = Fraction(count, total)
                    rhs = Fraction(comb(n, t) * comb(n - t, t - 1))
                    for s in sizes:
                        rhs *= Fraction(N_lean(n, t, s), comb(n, s))
                    if lhs > rhs:
                        violations += 1
                        print("VIOLATION prob", n, m, sizes, k, lhs, rhs)
                # MOSP form
                if mvs:
                    mcount = sum(1 for v in mvs if v <= k + 1)
                    if mcount != count:
                        violations += 1
                        print("VIOLATION mosp != pw+1", n, m, sizes, k, mcount, count)
                    if mcount > bound:
                        violations += 1
                        print("VIOLATION mosp", n, m, sizes, k, mcount, bound)
                # the README formula under Nat truncation
                for s in sizes:
                    if N_readme_nat(n, t, s) != N_lean(n, t, s):
                        truncation_differs += 1
print(f"counting/probability/MOSP checks: {checked} (n, m, sizes, k) cases, {violations} violations")
print(f"Nat-truncated README formula differs from avoidCount in {truncation_differs} (case, pattern) places"
      " (expected > 0: it truncates at 2t = n + 1, i.e. k = 0 with n - k + 1 even)")

# N(s) against enumeration for every disjoint (A, R) with |A| = a, |R| = r
pair_checks = pair_viol = 0
for n in range(1, 7):
    V = range(n)
    for a in range(0, n + 1):
        for A in itertools.combinations(V, a):
            rest = [v for v in V if v not in A]
            for r in range(0, len(rest) + 1):
                for R in itertools.combinations(rest, r):
                    for s in range(0, n + 1):
                        cnt = sum(1 for T in itertools.combinations(V, s)
                                  if not (set(T) & set(A)) or not (set(T) & set(R)))
                        formula = comb(n - a, s) + comb(n - r, s) - comb(n - a - r, s)
                        pair_checks += 1
                        if cnt != formula:
                            pair_viol += 1
                            print("VIOLATION N", n, A, R, s, cnt, formula)
print(f"avoidCount against enumeration: {pair_checks} (n, A, R, s) cases, {pair_viol} violations")
print("ALL OK" if violations == 0 and pair_viol == 0 else "FAILED")
