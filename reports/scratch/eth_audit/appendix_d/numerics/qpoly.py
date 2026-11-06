"""Exact univariate polynomials over Q (lists of Fractions, index = degree) and
2-adic valuations.  Shared by the Lemma D.5 and recursion-identity scripts."""
from __future__ import annotations
from fractions import Fraction


def v2(x) -> float:
    """Two-adic valuation of a rational (inf for zero)."""
    x = Fraction(x)
    if x == 0:
        return float("inf")
    n, d = x.numerator, x.denominator
    v = 0
    while n % 2 == 0:
        n //= 2; v += 1
    while d % 2 == 0:
        d //= 2; v -= 1
    return v


def is_2integral(x) -> bool:
    return Fraction(x).denominator % 2 == 1


def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def padd(p, q):
    n = max(len(p), len(q))
    return trim([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])


def pscale(p, c):
    return trim([c * x for x in p])


def pmul(p, q, trunc=None):
    if not p or not q:
        return []
    n = len(p) + len(q) - 1
    if trunc is not None:
        n = min(n, trunc)
    out = [Fraction(0)] * n
    for i, a in enumerate(p):
        if a == 0 or i >= n:
            continue
        for j, b in enumerate(q):
            if i + j >= n:
                break
            out[i + j] += a * b
    return trim(out)


def peval(p, x):
    r = Fraction(0)
    for c in reversed(p):
        r = r * x + c
    return r


def pshift(p, t, alpha):
    """Return the polynomial z -> p(t + alpha z)."""
    r = []
    lin = [Fraction(t), Fraction(alpha)]
    for c in reversed(p):
        r = padd(pmul(r, lin), [Fraction(c)])
    return r


def pdiv_linear(p, root):
    """Divide p(T) by (T - root) exactly; assumes root is a root."""
    n = len(p) - 1
    q = [Fraction(0)] * n
    carry = Fraction(0)
    for i in range(n, 0, -1):
        carry = p[i] + carry * root if i == n else p[i] + carry * root
        q[i - 1] = carry
    # remainder check
    rem = p[0] + carry * root
    assert rem == 0, "not a root"
    return q


def series_inverse(p, order):
    """Inverse of a power series with unit constant term, truncated at `order` terms."""
    assert p and p[0] != 0
    inv = [Fraction(0)] * order
    inv[0] = 1 / Fraction(p[0])
    for n in range(1, order):
        s = Fraction(0)
        for k in range(1, min(n, len(p) - 1) + 1):
            s += p[k] * inv[n - k]
        inv[n] = -s / p[0]
    return inv


def ppow(p, k, trunc=None):
    r = [Fraction(1)]
    for _ in range(k):
        r = pmul(r, p, trunc)
    return r


def lagrange_interpolate(points):
    """Exact Lagrange interpolation through (x_i, y_i) pairs; returns coefficient list."""
    n = len(points)
    result = []
    for i, (xi, yi) in enumerate(points):
        num = [Fraction(1)]
        den = Fraction(1)
        for j, (xj, _) in enumerate(points):
            if j != i:
                num = pmul(num, [Fraction(-xj), Fraction(1)])
                den *= (Fraction(xi) - Fraction(xj))
        result = padd(result, pscale(num, Fraction(yi) / den))
    return result
