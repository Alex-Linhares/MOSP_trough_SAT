"""Lemma D.5 (Tapered Hermite recovery), paper_flow.txt lines 4811-4951, tested
directly as the pure algebra/precision statement it is, over K = Q (e = 1),
ell = 1, with exact rational arithmetic.

For given (a, u, M): L = 2^a, S = {-L..L-1}, alpha = 2^{a+1}, h = ceil(3M/u),
q_t = h*max(0, u - v2(t)), D_t = L/2^{v2(t)}, p_t = p + 8 h D_t + 8 M (a+1).

Checks
 (1) identity (D.10): v2(E_t(0)) = D * sum_{j=1}^{a-i} (j/2^j)(q(i+j) - q(i)) >= -6 D h,
     for every node t, computed from the definition of E_t;
 (2) the exact Hermite identity (D.9) for random F satisfying the hypotheses
     (deg F <= M(2L-1), F(t + alpha z) 2-integral for all t in S);
 (3) the precision claim: replacing the first q_t coefficients of each
     F(t + alpha z) by arbitrary integer lifts of their residues mod 2^{p_t}
     (and discarding the rest) still returns F(0) mod 2^p;
 (4) the actual two-adic loss  -min_j v2(E_t(0) (-t/alpha)^j), j < q_t,
     against the budget 8 h D_t + 8 M (a+1).

Run: python3 -I lemma_d5_hermite.py [seed]
"""
from __future__ import annotations
import os, random, sys
from fractions import Fraction
from math import ceil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpoly import (v2, is_2integral, padd, pmul, pscale, peval, pshift, series_inverse,
                   trim, ppow, pdiv_linear)


def params(a, u, M, p):
    L = 1 << a
    S = list(range(-L, L))
    alpha = 1 << (a + 1)
    h = ceil(Fraction(3 * M, u))
    nodes = {}
    for t in S:
        if t == 0:
            continue
        i = int(v2(t))
        q = h * max(0, u - i)
        if q > 0:
            D = L >> i
            nodes[t] = dict(i=i, q=q, D=D, pt=p + 8 * h * D + 8 * M * (a + 1))
    return L, S, alpha, h, nodes


def C_poly(S):
    c = [Fraction(1)]
    for t in S:
        c = pmul(c, [Fraction(-t), Fraction(1)])
    return c


def Cprime0(S):
    # C'(0) = prod_{t in S, t != 0} (0 - t)
    r = Fraction(1)
    for t in S:
        if t != 0:
            r *= -t
    return r


def W_entry(S, x, y):
    """W_xy(T) = C(T) / (C'(0) (T - (y - x))) as a polynomial (D.7)."""
    c = C_poly(S)
    q = pdiv_linear(c, Fraction(y - x))
    return pscale(q, 1 / Cprime0(S))


def E_t(t, nodes, S):
    """E_t(T) = prod_{q in S minus {0,t}} ((T - q)/(t - q))^{q_q}, q_q = 0 for non-nodes."""
    e = [Fraction(1)]
    for q, info in nodes.items():
        if q == t:
            continue
        lin = [Fraction(-q, t - q), Fraction(1, t - q)]
        e = pmul(e, ppow(lin, info["q"]))
    return e


def random_F(a, u, M, S, L, rng):
    """Random F of degree <= M(2L-1) built from products of W entries and C(T)/C'(0)
    multiples with integer coefficients, plus an integer polynomial; verified later
    against the hypotheses of the lemma."""
    N = M * (2 * L - 1)
    F = [Fraction(rng.randint(-5, 5)) for _ in range(rng.randint(1, N + 1))]
    for _ in range(rng.randint(1, 4)):
        term = [Fraction(rng.randint(-3, 3))]
        for _ in range(rng.randint(1, M)):
            x, y = rng.randrange(L), rng.randrange(L)
            term = pmul(term, W_entry(S, x, y))
        F = padd(F, term)
    if rng.random() < 0.5:
        cc = pscale(C_poly(S), 1 / Cprime0(S))
        k = N - len(cc) + 1
        if k > 0:
            F = padd(F, pmul(cc, [Fraction(rng.randint(-4, 4)) for _ in range(k)]))
    assert len(F) - 1 <= N
    return F


def recover(F_jets, nodes, S, alpha, p, lifts_rng=None):
    """(D.9) from the jets F_jets[t] (coefficient lists in z, first q_t entries).
    If lifts_rng is given, each coefficient is replaced by a random integer lift of
    its residue modulo 2^{p_t} before use."""
    total = Fraction(0)
    for t, info in nodes.items():
        q = info["q"]
        jet = list(F_jets[t][:q]) + [Fraction(0)] * (q - len(F_jets[t][:q]))
        if lifts_rng is not None:
            mod = 1 << info["pt"]
            lifted = []
            for c in jet:
                assert is_2integral(c)
                # residue of a 2-adic integer modulo 2^{pt}
                r = (c.numerator * pow(c.denominator, -1, mod)) % mod
                lifted.append(Fraction(r + mod * lifts_rng.randint(-3, 3)))
            jet = lifted
        Et = E_t(t, nodes, S)
        Et_shift = pshift(Et, t, alpha)
        inv = series_inverse(Et_shift, q)
        Q = pmul(jet, inv, trunc=q)
        total += peval(Et, 0) * peval(Q, Fraction(-t, alpha))
    return total


def check_D10(a, u, M, p):
    L, S, alpha, h, nodes = params(a, u, M, p)
    ok = True
    for t, info in nodes.items():
        i, D = info["i"], info["D"]
        lhs = v2(peval(E_t(t, nodes, S), 0))
        qf = lambda j: h * max(0, u - j)
        rhs = D * sum(Fraction(j, 1 << j) * (qf(i + j) - qf(i)) for j in range(1, a - i + 1))
        if Fraction(lhs) != rhs or rhs < -6 * D * h:
            ok = False
            print("  (D.10) FAILS at", (a, u, M, t), lhs, rhs)
    return ok


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rng = random.Random(seed)
    print("(D.10) identity v2(E_t(0)) = D sum_j (j/2^j)(q(i+j)-q(i)) >= -6Dh:")
    d10 = True
    for a in (1, 2, 3, 4):
        for u in range(1, a + 1):
            for M in (u, u + 1, 2 * u + 1):
                d10 &= check_D10(a, u, M, p=3)
    print("  holds on all tested (a<=4, u<=a, three M each):", d10)

    print("Recovery tests:")
    n_exact = n_prec = n_cases = 0
    worst_margin = None
    for (a, u, M) in [(1, 1, 1), (1, 1, 2), (2, 1, 1), (2, 1, 2), (2, 2, 2), (2, 2, 3), (3, 1, 1), (3, 2, 2), (3, 3, 3), (3, 2, 4)]:
        for p in (1, 2, 5):
            L, S, alpha, h, nodes = params(a, u, M, p)
            # actual loss vs budget
            for t, info in nodes.items():
                Et0 = peval(E_t(t, nodes, S), 0)
                loss = -min(v2(Et0 * Fraction(-t, alpha) ** j) for j in range(info["q"]))
                budget = 8 * h * info["D"] + 8 * M * (a + 1)
                margin = budget - loss
                if worst_margin is None or margin < worst_margin[0]:
                    worst_margin = (margin, (a, u, M, t), loss, budget)
                assert loss <= budget
            for trial in range(3):
                F = random_F(a, u, M, S, L, rng)
                jets = {}
                hyp = is_2integral(peval(F, 0))
                for t in S:
                    sh = pshift(F, t, alpha)
                    hyp &= all(is_2integral(c) for c in sh)
                    jets[t] = sh
                if not hyp:
                    continue  # generator produced something outside the hypotheses; skip
                n_cases += 1
                exact = recover(jets, nodes, S, alpha, p)
                if exact == peval(F, 0):
                    n_exact += 1
                else:
                    print("  EXACT (D.9) FAILS", (a, u, M, p))
                approx = recover(jets, nodes, S, alpha, p, lifts_rng=rng)
                diff = approx - peval(F, 0)
                if v2(diff) >= p:
                    n_prec += 1
                else:
                    print("  PRECISION CLAIM FAILS", (a, u, M, p), "v2(diff) =", v2(diff))
    print(f"  cases within hypotheses: {n_cases}; exact (D.9) holds: {n_exact}; "
          f"recovery mod 2^p from lifted residues mod 2^pt holds: {n_prec}")
    print("  smallest (budget - actual loss) over nodes:", worst_margin)


if __name__ == "__main__":
    main()
