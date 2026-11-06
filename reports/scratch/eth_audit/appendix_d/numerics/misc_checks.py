"""Smaller numeric checks of Appendix D claims that are exact statements.

 (1) D.4.1: in O = Z_(2)[U]/(f), f monic of degree e irreducible mod 2, the 2^e
     binary-coordinate lifts have pairwise unit differences, and the Vandermonde
     matrix on any subset of them has unit determinant (so Lagrange interpolation
     is valid over A_p).  Tested for e = 3, 4, 5 with every such f.
 (2) D.4.1: v2(xy) = v2(x) + v2(y) for the coordinate-minimum valuation (random test).
 (3) Lemma D.3: E sum_gamma (X_gamma - M/D_arr)^2 <= 2 M Delta under independent
     uniform labels in [r]^a, computed EXACTLY by enumerating all labelings of tiny
     bipartite multigraphs, with D_arr = r^{2a} (the PDF) and, for contrast, r*2^a
     (what the text extraction reads).
 (4) Lemma D.4: v2(C'(t)) = v2(C'(0)) for all t in S and C(t + alpha z)/C'(0) is
     divisible by 2^{a+1} coefficientwise, a = 1..5.
 (5) (D.3): ceil(log2 C(N,d)) <= N and log2 C(N+K, K) <= K log2(e (N+K)/K).

Run: python3 -I misc_checks.py
"""
from __future__ import annotations
import os, random, sys
from fractions import Fraction
from itertools import product, combinations
from math import comb, log2, ceil, e as E_CONST
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpoly import v2, pmul, pshift, padd, pscale


# ---- arithmetic in Z[U]/(f) -------------------------------------------
def irreducible_mod2(f):
    """f: list of 0/1 coefficients low->high, monic. Irreducible over F2 by trial division."""
    e = len(f) - 1
    for d in range(1, e // 2 + 1):
        for g in product((0, 1), repeat=d):
            g = list(g) + [1]
            # divide f by g mod 2
            r = list(f)
            for i in range(len(r) - 1, d - 1, -1):
                if r[i] % 2:
                    for j in range(d + 1):
                        r[i - d + j] ^= g[j]
            if not any(x % 2 for x in r[:d]):
                return False
    return True


def omul(x, y, f):
    e = len(f) - 1
    out = [0] * (2 * e - 1)
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            out[i + j] += a * b
    for i in range(len(out) - 1, e - 1, -1):
        c = out[i]
        if c:
            for j in range(e + 1):
                out[i - e + j] -= c * f[j]
    return out[:e]


def osub(x, y):
    return [a - b for a, b in zip(x, y)]


def norm_is_odd(x, f):
    """x is a unit in O iff x mod 2 is nonzero in the field F_{2^e}."""
    return any(c % 2 for c in x)


def det_mod2_unit(mat, f):
    """Determinant over Z[U]/(f) by fraction-free elimination mod 2 suffices for unit-ness:
    reduce the matrix mod 2 and compute the determinant in F_{2^e}."""
    e = len(f) - 1
    n = len(mat)
    A = [[[c % 2 for c in x] for x in row] for row in mat]

    def mul2(x, y):
        return [c % 2 for c in omul(x, y, f)]

    def inv2(x):
        # brute force inverse in F_{2^e}
        for cand in product((0, 1), repeat=e):
            if mul2(x, list(cand)) == [1] + [0] * (e - 1):
                return list(cand)
        raise ZeroDivisionError

    det = [1] + [0] * (e - 1)
    for col in range(n):
        piv = next((r for r in range(col, n) if any(A[r][col])), None)
        if piv is None:
            return False
        A[col], A[piv] = A[piv], A[col]
        det = mul2(det, A[col][col])
        iv = inv2(A[col][col])
        for r in range(col + 1, n):
            if any(A[r][col]):
                fac = mul2(A[r][col], iv)
                for c in range(col, n):
                    A[r][c] = [(a - b) % 2 for a, b in zip(A[r][c], mul2(fac, A[col][c]))]
    return any(det)


def check_interpolation_points():
    ok = True
    for e in (3, 4, 5):
        fs = [list(g) + [1] for g in product((0, 1), repeat=e) if irreducible_mod2(list(g) + [1])]
        for f in fs:
            lifts = [list(c) for c in product((0, 1), repeat=e)]
            for x, y in combinations(lifts, 2):
                if not norm_is_odd(osub(x, y), f):
                    ok = False
            # Vandermonde on all 2^e points (and a random subset)
            n = len(lifts)
            V = [[[1] + [0] * (e - 1)] for _ in range(n)]
            for i, x in enumerate(lifts):
                row = [[1] + [0] * (e - 1)]
                for _ in range(n - 1):
                    row.append(omul(row[-1], x, f))
                V[i] = row
            if not det_mod2_unit(V, f):
                ok = False
        print(f"  e={e}: {len(fs)} irreducible f; pairwise unit differences and unit Vandermonde: {ok}")
    return ok


def check_valuation_multiplicative(trials=300):
    rng = random.Random(3)
    f = [1, 1, 0, 1]  # U^3 + U + 1
    e = 3

    def val(x):
        return min(v2(c) for c in x) if any(x) else float("inf")
    ok = True
    for _ in range(trials):
        x = [Fraction(rng.randint(-20, 20) * 2 ** rng.randint(0, 3), 2 * rng.randint(0, 5) + 1) for _ in range(e)]
        y = [Fraction(rng.randint(-20, 20) * 2 ** rng.randint(0, 3), 2 * rng.randint(0, 5) + 1) for _ in range(e)]
        if not any(x) or not any(y):
            continue
        if val(omul(x, y, f)) != val(x) + val(y):
            ok = False
    print(f"  v2(xy) = v2(x) + v2(y) in O (e=3, {trials} random pairs): {ok}")
    return ok


def check_lemma_d3_expectation():
    rng = random.Random(7)
    ok_pdf, ok_alt = True, True
    worst = None
    for trial in range(60):
        r = rng.choice([2, 3])
        a = rng.choice([1, 2])
        n_rows, n_cols = rng.randint(1, 2), rng.randint(1, 2)
        M = rng.randint(1, 5)
        edges = [(rng.randrange(n_rows), rng.randrange(n_cols)) for _ in range(M)]
        Delta = max(max(sum(1 for e in edges if e[0] == v) for v in range(n_rows)),
                    max(sum(1 for e in edges if e[1] == v) for v in range(n_cols)))
        labels = list(product(range(r), repeat=a))
        nv = n_rows + n_cols
        if len(labels) ** nv > 6000:
            continue
        for Darr, tag in ((r ** (2 * a), "r^(2a)"), (r * 2 ** a, "r*2^a")):
            total = Fraction(0)
            count = 0
            for lab in product(labels, repeat=nv):
                X = {}
                for (rv, cv) in edges:
                    key = (lab[rv], lab[n_rows + cv])
                    X[key] = X.get(key, 0) + 1
                # sum over all pair labels gamma (also empty classes)
                s = sum((Fraction(X.get(g, 0)) - Fraction(M, Darr)) ** 2 for g in product(labels, labels))
                total += s
                count += 1
            expect = total / count
            holds = expect <= 2 * M * Delta
            if tag == "r^(2a)":
                ok_pdf &= holds
                if worst is None or expect / (2 * M * Delta) > worst[0]:
                    worst = (expect / (2 * M * Delta), (r, a, M, Delta))
            else:
                ok_alt &= holds
    print(f"  E sum (X - M/D_arr)^2 <= 2 M Delta, exact over all labelings: with D_arr = r^(2a): {ok_pdf} "
          f"(largest ratio to the bound {float(worst[0]):.3f} at (r,a,M,Delta)={worst[1]}); with D_arr = r*2^a: {ok_alt}")
    return ok_pdf


def check_lemma_d4_C():
    ok = True
    for a in range(1, 6):
        L = 1 << a
        S = list(range(-L, L))
        alpha = 1 << (a + 1)
        C = [Fraction(1)]
        for t in S:
            C = pmul(C, [Fraction(-t), Fraction(1)])
        # derivative
        Cp = [C[i] * i for i in range(1, len(C))]
        v0 = v2(sum(Cp[i] * 0 ** i if i else Cp[0] for i in range(len(Cp))))
        for t in S:
            vt = v2(sum(c * Fraction(t) ** i for i, c in enumerate(Cp)))
            if vt != v0:
                ok = False
            sh = pshift(pscale(C, 1 / sum(c * 0 ** i if i else c for i, c in enumerate(Cp))), t, alpha)
            if any(v2(c) < a + 1 for c in sh if c != 0):
                ok = False
    print(f"  Lemma D.4: v2(C'(t)) = v2(C'(0)) for all t in S and C(t+alpha z)/C'(0) divisible by 2^(a+1), a=1..5: {ok}")
    return ok


def check_D3_inequalities():
    ok = True
    for N in range(1, 40):
        for d in range(0, N + 1):
            if comb(N, d) > 1 and ceil(log2(comb(N, d))) > N:
                ok = False
    for N in range(1, 200, 7):
        for K in range(1, 200, 5):
            if log2(comb(N + K, K)) > K * log2(E_CONST * (N + K) / K) + 1e-9:
                ok = False
    print(f"  (D.3): ceil(log2 C(N,d)) <= N and log2 C(N+K,K) <= K log2(e(N+K)/K) on the tested ranges: {ok}")
    return ok


if __name__ == "__main__":
    print("(1) interpolation points in O:")
    check_interpolation_points()
    print("(2) valuation:")
    check_valuation_multiplicative()
    print("(3) Lemma D.3 expectation bound:")
    check_lemma_d3_expectation()
    print("(4) Lemma D.4 C(T) facts:")
    check_lemma_d4_C()
    print("(5) (D.3) counting inequalities:")
    check_D3_inequalities()
