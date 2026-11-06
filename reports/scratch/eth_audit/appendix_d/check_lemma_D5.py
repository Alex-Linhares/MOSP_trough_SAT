"""Numerical check of Lemma D.5 (tapered Hermite recovery) and identity (D.10).

Works over Q (i.e. e = 1, O = Z_(2), ell = 1).  For given a (L = 2^a), u <= a,
M >= u, p: builds h, q_t, D_t, p_t exactly as in the lemma, takes a polynomial
F in Q[T] of degree <= M(2L-1) with F(t + alpha z) in Z_(2)[z] for all t in S,
perturbs each jet coefficient by a random multiple of 2^{p_t}, applies (D.9),
and checks the result is congruent to F(0) modulo 2^p.  Also reports the
actual worst-case 2-adic loss against the lemma's budget 6 D_t h + 4 M (a+1).
"""
import random, sys
from fractions import Fraction as Fr
from math import comb

def v2(x):
    if x == 0: return float('inf')
    if isinstance(x, Fr):
        return v2(x.numerator) - v2(x.denominator)
    n = 0
    while x % 2 == 0:
        x //= 2; n += 1
    return n

def v2min(poly):  # list of Fractions
    return min((v2(c) for c in poly if c != 0), default=float('inf'))

def polymul(p, q, trunc=None):
    r = [Fr(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a == 0: continue
        for j, b in enumerate(q):
            r[i + j] += a * b
    return r[:trunc] if trunc else r

def polyshift(p, c):
    """p(T) -> p(T + c) as list in z where T = c + z ... actually returns p(c + z)."""
    # Horner in (c + z)
    r = [Fr(0)]
    for coef in reversed(p):
        r = polymul(r, [Fr(c), Fr(1)])
        r[0] += coef
    return r

def polyeval(p, x):
    r = Fr(0)
    for coef in reversed(p):
        r = r * x + coef
    return r

def series_inv(p, n):
    assert p[0] == 1
    inv = [Fr(0)] * n; inv[0] = Fr(1)
    for k in range(1, n):
        s = Fr(0)
        for j in range(1, min(k, len(p) - 1) + 1):
            s += p[j] * inv[k - j]
        inv[k] = -s
    return inv

def run(a, u, M, p, kind, seed):
    rng = random.Random(seed)
    L = 2 ** a; alpha = 2 ** (a + 1)
    S = list(range(-L, L))
    h = -(-3 * M // u)
    def q(i): return h * max(0, u - i)
    nodes = [t for t in S if t != 0 and v2(t) < u]
    degF = M * (2 * L - 1)
    # C(T) and C'(0)
    C = [Fr(1)]
    for t in S: C = polymul(C, [Fr(-t), Fr(1)])
    Cp0 = Fr(1)
    for t in S:
        if t != 0: Cp0 *= Fr(-t)
    def W(x, y):  # W_{xy}(T) as a polynomial in T
        num = [Fr(1)]
        for t in S:
            if t != (y - x): num = polymul(num, [Fr(-t), Fr(1)])
        return [c / Cp0 for c in num]
    if kind == 'int':
        F = [Fr(rng.randrange(-10**6, 10**6)) for _ in range(degF + 1)]
    else:  # product of M affine factors in W entries, like (D.8)
        F = [Fr(1)]
        for _ in range(M):
            x = rng.randrange(L); y = rng.randrange(L)
            fac = W(x, y); fac[0] += rng.choice([0, 1]); sg = rng.choice([1, -1]); fac = [sg * c for c in fac]
            F = polymul(F, fac)
    assert len(F) - 1 <= degF
    F0 = polyeval(F, 0)
    assert v2(F0) >= 0
    total_mult = sum(q(v2(t)) for t in nodes)
    assert total_mult > degF, (total_mult, degF)
    recon = Fr(0)
    worst = {}
    for t in nodes:
        i = v2(t); D = L // 2 ** i; qt = q(i); pt = p + 8 * h * D + 8 * M * (a + 1)
        jet = polyshift(F, t)              # F(t + z)
        jet = [c * Fr(alpha) ** k for k, c in enumerate(jet)]   # F(t + alpha z)
        assert v2min(jet) >= 0, "jet not integral"
        # E_t(t + alpha z) and E_t(0)
        Et_jet = [Fr(1)]; Et0 = Fr(1); vEt0 = 0
        for qq in S:
            if qq in (0, t) or q(v2(qq)) == 0: continue
            m = q(v2(qq))
            base = [Fr(1), Fr(alpha, t - qq)]
            for _ in range(m): Et_jet = polymul(Et_jet, base, trunc=qt)
            Et0 *= Fr(-qq, t - qq) ** m
            vEt0 += m * (v2(qq) - v2(t - qq))
        formula = D * sum(Fr(j, 2 ** j) * (q(i + j) - q(i)) for j in range(1, a - i + 1))
        assert vEt0 == formula, (t, vEt0, formula)   # (D.10) identity
        assert vEt0 >= -6 * D * h
        Q = polymul(jet[:qt], series_inv(Et_jet, qt), trunc=qt)
        assert v2min(Q) >= 0
        # perturb by multiples of 2^{pt} (any lift of the residue) and evaluate
        Qp = [c + rng.randrange(-3, 4) * 2 ** pt for c in Q]
        contrib = Et0 * polyeval(Qp, Fr(-t, alpha))
        # actual loss of this node: min over j of v2(Et0 * (-t/alpha)^j), j < qt
        loss = -min(vEt0 + j * v2(Fr(-t, alpha)) for j in range(qt))
        worst[t] = (loss, 6 * D * h + 4 * M * (a + 1), pt)
        recon += contrib
    diff = recon - F0
    ok = v2(diff) >= p if diff != 0 else True
    return ok, worst, len(nodes), total_mult, degF

if __name__ == '__main__':
    random.seed(1)
    for (a, u, M, p, kind) in [(2, 1, 2, 3, 'int'), (2, 2, 3, 4, 'int'), (3, 1, 3, 5, 'int'),
                               (3, 2, 4, 5, 'int'), (3, 3, 5, 6, 'int'), (4, 2, 4, 7, 'int'),
                               (3, 2, 4, 5, 'W'), (4, 3, 5, 6, 'W'), (4, 2, 6, 5, 'W')]:
        for seed in range(3):
            ok, worst, nn, tm, degF = run(a, u, M, p, kind, seed)
            mx = max(w[0] for w in worst.values()); bud = max(w[1] for w in worst.values())
            print(f"a={a} L={2**a} u={u} M={M} p={p} kind={kind} seed={seed}: nodes={nn} "
                  f"sum q_t={tm} > degF={degF}  recovery exact mod 2^p: {ok}  "
                  f"max actual loss={mx} (lemma budget 6Dh+4M(a+1) max={bud})")
            if not ok: sys.exit("FAIL")
    print("all recoveries exact")
