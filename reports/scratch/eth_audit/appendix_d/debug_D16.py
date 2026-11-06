import itertools, sys, os
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_D16 as C
from check_lemma_D5 import v2
seed, t, zeta, P = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
packets, vertices, edges = C.build(seed)
i = v2(t); T = t + C.alpha * zeta; M = len(edges)
print("packets:", [(pk['syms'], pk['real']) for pk in packets])
print("vertices:", {k: (v['side'], v['label'], v['ports']) for k, v in vertices.items()})
rows = [v for v in vertices.values() if v['side'] == 'row']; cols = [v for v in vertices.values() if v['side'] == 'col']
def bit(x, c): return (x >> c) & 1
# three versions of the row form value for given X: exact, truncated-(D.12), and mode-expanded-then-dropped
def rowform_exact(e, X):
    Pk, x, _, _ = edges[e]
    return sum(C.Wval(T, x, y) * X[e2] for e2, (P2, y, _, _) in enumerate(edges) if P2 == Pk)
def rowform_trunc(e, X):
    Pk, x, _, _ = edges[e]; s = packets[Pk]['syms'][i]; tot = Fr(0)
    for e2, (P2, y, _, _) in enumerate(edges):
        if P2 != Pk: continue
        if s[0] == s[1] or bit(y, i) != bit(x, i): tot += C.Wval(T, x, y) * X[e2]
        else:
            y0 = y % 2 ** (i + 1); j = y // 2 ** (i + 1); base = C.Wval(T, x, y0)
            tot += sum(base * Fr(2 ** (i + 1) * j, T - y0 + x) ** b for b in range(P - 1)) * X[e2]
    return tot
def F_of(rowform):
    tot = Fr(0)
    for Y in itertools.product((0, 1), repeat=M):
        Ay = 1
        for v in rows: Ay *= C.tensor_val(v, dict(enumerate(Y)))
        if Ay == 0: continue
        for X in itertools.product((0, 1), repeat=M):
            Bx = 1
            for v in cols: Bx *= C.tensor_val(v, dict(enumerate(X)))
            if Bx == 0: continue
            prod = Fr(1)
            for e in range(M):
                w = rowform(e, X); prod *= (w if Y[e] else 1 - w)
            tot += Ay * Bx * prod
    return tot
Fa = F_of(rowform_exact); Fb = F_of(rowform_trunc)
print("v2(F_exact - F_trunc) =", v2(Fa - Fb) if Fa != Fb else 'inf', " (need >=", P, ")")
# crossing entries individually
for e, (Pk, x, _, _) in enumerate(edges):
    s = packets[Pk]['syms'][i]
    for e2, (P2, y, _, _) in enumerate(edges):
        if P2 != Pk or s[0] == s[1] or bit(y, i) != bit(x, i): continue
        y0 = y % 2 ** (i + 1); j = y // 2 ** (i + 1); base = C.Wval(T, x, y0)
        approx = sum(base * Fr(2 ** (i + 1) * j, T - y0 + x) ** b for b in range(P - 1))
        exact = C.Wval(T, x, y)
        print(f"  packet {Pk} x={x} y={y} (y0={y0}, j={j}): v2(W)={v2(exact) if exact else 'inf'}, "
              f"v2(W - trunc)={v2(exact-approx) if exact != approx else 'inf'}, v2(base)={v2(base)}, "
              f"v2(ratio)={v2(Fr(2**(i+1)*j, T-y0+x)) if j else 'n/a'}")

# (c): global mode expansion, drop sum w beta >= P, substitute L_Z
modes = []   # (packet, y0, b)
for Pk, pk in enumerate(packets):
    s = pk['syms'][i]
    if s[0] == s[1]: continue
    for y0 in range(2 ** (i + 1)):
        for b in range(P - 1): modes.append((Pk, y0, b))
nm = len(modes); widx = {m: n for n, m in enumerate(modes)}; W_ = [m[2] + 1 for m in modes]
def pmul(p, q):
    out = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = tuple(a + b for a, b in zip(e1, e2))
            if sum(w * k for w, k in zip(W_, e)) < P: out[e] = out.get(e, Fr(0)) + c1 * c2
    return out
def LZ(n, X):
    Pk, y0, b = modes[n]
    return sum((j ** b if (j or b == 0) else 0) * X[e2] for e2, (P2, y, _, _) in enumerate(edges)
               if P2 == Pk and y % 2 ** (i + 1) == y0 for j in [y // 2 ** (i + 1)])
def rowpoly(e, X, Ye):
    Pk, x, _, _ = edges[e]; s = packets[Pk]['syms'][i]
    lin = {tuple([0] * nm): Fr(0)}
    for e2, (P2, y, _, _) in enumerate(edges):
        if P2 != Pk: continue
        if s[0] == s[1] or bit(y, i) != bit(x, i): lin[tuple([0] * nm)] += C.Wval(T, x, y) * X[e2]
    if s[0] != s[1]:
        for y0 in range(2 ** (i + 1)):
            if bit(y0, i) != bit(x, i): continue
            base = C.Wval(T, x, y0)
            for b in range(P - 1):
                ex = [0] * nm; ex[widx[(Pk, y0, b)]] = 1
                lin[tuple(ex)] = base * Fr(2 ** (i + 1), T - y0 + x) ** b
    if Ye == 0:
        lin = {k: -c for k, c in lin.items()}; lin[tuple([0] * nm)] += 1
    return lin
Fc = Fr(0); dropped_min_v2 = None
for Y in itertools.product((0, 1), repeat=M):
    Ay = 1
    for v in rows: Ay *= C.tensor_val(v, dict(enumerate(Y)))
    if Ay == 0: continue
    for X in itertools.product((0, 1), repeat=M):
        Bx = 1
        for v in cols: Bx *= C.tensor_val(v, dict(enumerate(X)))
        if Bx == 0: continue
        poly = {tuple([0] * nm): Fr(1)}
        for e in range(M): poly = pmul(poly, rowpoly(e, X, Y[e]))
        val = Fr(0)
        for ex, c in poly.items():
            term = c
            for n, k in enumerate(ex):
                if k: term *= Fr(LZ(n, X)) ** k
            val += term
        Fc += Ay * Bx * val
print("v2(F_trunc - F_modes) =", v2(Fb - Fc) if Fb != Fc else 'inf', " (need >=", P, ")")
print("v2(F_exact - F_modes) =", v2(Fa - Fc) if Fa != Fc else 'inf')

# per-beta comparison: (c) restricted to beta vs product of children (d)
def group_of_row(Pk, x): s = packets[Pk]['syms'][i]; return s[0] if bit(x, i) == 0 else s[1]
def group_of_col(Pk, y): s = packets[Pk]['syms'][i]; return s[1] if bit(y, i) == 0 else s[0]
src = [group_of_col(m[0], m[1]) for m in modes]; tgt = [1 - s for s in src]
allbeta = set()
def rec(n, budget, cur):
    if n == nm: allbeta.add(tuple(cur)); return
    for k in range(budget // W_[n] + 1):
        cur.append(k); rec(n + 1, budget - k * W_[n], cur); cur.pop()
rec(0, P - 1, [])
c_by_beta = {b: Fr(0) for b in allbeta}
for Y in itertools.product((0, 1), repeat=M):
    Ay = 1
    for v in rows: Ay *= C.tensor_val(v, dict(enumerate(Y)))
    if Ay == 0: continue
    for X in itertools.product((0, 1), repeat=M):
        Bx = 1
        for v in cols: Bx *= C.tensor_val(v, dict(enumerate(X)))
        if Bx == 0: continue
        poly = {tuple([0] * nm): Fr(1)}
        for e in range(M): poly = pmul(poly, rowpoly(e, X, Y[e]))
        for ex, c in poly.items():
            term = c
            for n, k in enumerate(ex):
                if k: term *= Fr(LZ(n, X)) ** k
            c_by_beta[ex] += Ay * Bx * term
def child(g, beta):
    gverts = [v for v in vertices.values() if v['label'][i] == g]
    gports = sorted({e for v in gverts for e in v['ports']})
    tot = Fr(0)
    for bits in itertools.product((0, 1), repeat=len(gports)):
        assign = dict(zip(gports, bits)); prod = Fr(1)
        for v in gverts: prod *= C.tensor_val(v, assign)
        if prod == 0: continue
        for Pk in range(len(packets)):
            poly = {tuple([0] * nm): Fr(1)}
            for e, (P2, x, _, _) in enumerate(edges):
                if P2 != Pk or group_of_row(Pk, x) != g: continue
                poly = pmul(poly, rowpoly(e, assign, assign[e]))
            want = tuple(beta[n] if (modes[n][0] == Pk and tgt[n] == g) else 0 for n in range(nm))
            coef = poly.get(want, Fr(0))
            for n in range(nm):
                if modes[n][0] == Pk and src[n] == g and beta[n] > 0: coef *= Fr(LZ(n, assign)) ** beta[n]
            prod *= coef
        tot += prod
    return tot
Fd = Fr(0); mism = 0
for beta in sorted(allbeta):
    d = child(0, beta) * child(1, beta); Fd += d
    if d != c_by_beta[beta]:
        mism += 1; print("  beta", beta, "global", c_by_beta[beta], "children", d)
print("mismatching betas:", mism, "; v2(F_modes - F_children) =", v2(Fc - Fd) if Fc != Fd else 'inf')
