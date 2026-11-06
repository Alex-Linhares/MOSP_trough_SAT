"""End-to-end check of the recursion identity (D.16) and of F(0) = contraction, on a tiny
network already in packet form (Lemma D.3's output format), with e = 1 (O = Z_(2)), ell = 1,
r = 2 symbols, a = 2 coordinates (L = 4, S = {-4..3}, alpha = 8), u = 2 (nodes of valuation 0, 1).
For each node t, integer zeta, precision P: F(t + alpha*zeta) from (D.8) by brute force must be
congruent mod 2^P to sum_beta prod_g Z_{g,beta}, with the children built exactly as in D.4.6."""
import itertools, random, sys, os
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_lemma_D5 import v2

r = 2; a = 2; L = 2 ** a; alpha = 2 ** (a + 1); S = list(range(-L, L))
Cp0 = Fr(1)
for q in S:
    if q != 0: Cp0 *= Fr(-q)
def Wval(T, x, y):
    num = Fr(1)
    for q in S:
        if q != y - x: num *= (T - q)
    return num / Cp0
def bit(x, c): return (x >> c) & 1

def build(seed, npack=2, nreal=3):
    rng = random.Random(seed)
    packets = []
    for P in range(npack):
        syms = [(rng.randrange(r), rng.randrange(r)) for _ in range(a)]
        real = sorted(rng.sample(range(L), nreal))
        packets.append(dict(syms=syms, real=real))
    # vertices: for each (side, label) create up to 2 vertices; assign ports
    vertices = {}  # id -> dict(side, label, ports)
    def row_label(P, x):
        return tuple((syms[0] if bit(x, c) == 0 else syms[1]) for c, syms in enumerate(packets[P]['syms']))
    def col_label(P, x):
        return tuple((syms[1] if bit(x, c) == 0 else syms[0]) for c, syms in enumerate(packets[P]['syms']))
    def get_vertex(side, label):
        cands = [v for v, d in vertices.items() if d['side'] == side and d['label'] == label]
        if cands and rng.random() < 0.6: return rng.choice(cands)
        vid = len(vertices); vertices[vid] = dict(side=side, label=label, ports=[]); return vid
    edges = []
    for P, pk in enumerate(packets):
        for x in pk['real']:
            rv = get_vertex('row', row_label(P, x)); cv = get_vertex('col', col_label(P, x))
            eid = len(edges); edges.append((P, x, rv, cv))
            vertices[rv]['ports'].append(eid); vertices[cv]['ports'].append(eid)
    for v in vertices.values():
        v['tensor'] = {bits: rng.randrange(-5, 6) for bits in itertools.product((0, 1), repeat=len(v['ports']))}
    return packets, vertices, edges

def tensor_val(v, assign):   # assign: dict eid -> bit
    return v['tensor'][tuple(assign[e] for e in v['ports'])]

def contraction(vertices, edges):
    tot = 0
    for bits in itertools.product((0, 1), repeat=len(edges)):
        assign = dict(enumerate(bits)); prod = 1
        for v in vertices.values(): prod *= tensor_val(v, assign)
        tot += prod
    return tot

def F_direct(T, packets, vertices, edges):
    M = len(edges); tot = Fr(0)
    rows = [v for v in vertices.values() if v['side'] == 'row']; cols = [v for v in vertices.values() if v['side'] == 'col']
    for Y in itertools.product((0, 1), repeat=M):
        Ay = 1
        for v in rows: Ay *= tensor_val(v, dict(enumerate(Y)))
        if Ay == 0: continue
        for X in itertools.product((0, 1), repeat=M):
            Bx = 1
            for v in cols: Bx *= tensor_val(v, dict(enumerate(X)))
            if Bx == 0: continue
            prod = Fr(1)
            for e, (P, x, rv, cv) in enumerate(edges):
                wx = sum(Wval(T, x, y) * X[e2] for e2, (P2, y, _, _) in enumerate(edges) if P2 == P)
                prod *= (wx if Y[e] == 1 else 1 - wx)
                if prod == 0: break
            tot += Ay * Bx * prod
    return tot

# polynomials in modes: dict {exponent tuple (over mode index list): Fraction}
def pmul(p, q, modes, Pprec):
    out = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = tuple(x + y for x, y in zip(e1, e2))
            if sum(w * k for w, k in zip(modes['w'], e)) < Pprec:
                out[e] = out.get(e, Fr(0)) + c1 * c2
    return out

def check(seed, t, zeta, Pprec):
    packets, vertices, edges = build(seed)
    M = len(edges)
    Z0 = contraction(vertices, edges)
    assert F_direct(Fr(0), packets, vertices, edges) == Z0, "F(0) != contraction"
    i = v2(t); T = t + alpha * zeta
    # groups: symbol in coordinate i
    def group_of_row(P, x): s = packets[P]['syms'][i]; return s[0] if bit(x, i) == 0 else s[1]
    def group_of_col(P, y): s = packets[P]['syms'][i]; return s[1] if bit(y, i) == 0 else s[0]
    for e, (P, x, rv, cv) in enumerate(edges):
        assert vertices[rv]['label'][i] == group_of_row(P, x) and vertices[cv]['label'][i] == group_of_col(P, y=x)
    # modes: (packet, y0, b) for packets with unequal symbols in coord i
    modes = dict(key=[], w=[], src=[], tgt=[])
    for P, pk in enumerate(packets):
        s = pk['syms'][i]
        if s[0] == s[1]: continue
        for y0 in range(2 ** (i + 1)):
            for b in range(Pprec - 1):
                modes['key'].append((P, y0, b)); modes['w'].append(b + 1)
                src = group_of_col(P, y0); modes['src'].append(src); modes['tgt'].append(1 - src)
    nm = len(modes['key']); idx = {k: n for n, k in enumerate(modes['key'])}
    # row form for row port e as (local dict over column eids -> coeff, mode dict -> coeff)
    def row_form(e):
        P, x, rv, cv = edges[e]
        local = {}; modec = {}
        s = packets[P]['syms'][i]
        for e2, (P2, y, _, _) in enumerate(edges):
            if P2 != P: continue
            if s[0] == s[1] or bit(y, i) != bit(x, i): local[e2] = Wval(T, x, y)   # same group: local
        if s[0] != s[1]:
            for y0 in range(2 ** (i + 1)):
                if bit(y0, i) != bit(x, i): continue
                assert v2(t - y0 + x) <= i
                base = Wval(T, x, y0)
                for b in range(Pprec - 1):
                    c = base * Fr(2 ** (i + 1), T - y0 + x) ** b
                    assert v2(c) >= b + 1
                    modec[idx[(P, y0, b)]] = c
        return local, modec
    def L_Z(n, X):  # X: dict eid -> bit
        P, y0, b = modes['key'][n]; tot = 0
        for e2, (P2, y, _, _) in enumerate(edges):
            if P2 == P and y % (2 ** (i + 1)) == y0:
                j = y // (2 ** (i + 1)); tot += (j ** b if (j or b == 0) else 0) * X[e2]
        return tot
    # enumerate beta
    def betas():
        def rec(n, budget, cur):
            if n == nm: yield tuple(cur); return
            k = 0
            while k * modes['w'][n] < budget + 1 and k * modes['w'][n] <= budget:
                if k * modes['w'][n] < budget + 1:
                    cur.append(k); yield from rec(n + 1, budget - k * modes['w'][n], cur); cur.pop()
                k += 1
        yield from rec(0, Pprec - 1, [])
    total = Fr(0); nbeta = 0; max_child_edges = 0
    for beta in betas():
        if sum(w * k for w, k in zip(modes['w'], beta)) >= Pprec: continue
        nbeta += 1
        prod_g = Fr(1)
        for g in range(r):
            # child g: ports of group-g vertices
            gverts = [v for v in vertices.values() if v['label'][i] == g]
            # a child wire is a *port*: (edge, side).  Row ports carry Y bits, column ports X bits.
            gports = sorted({(e, v['side']) for v in gverts for e in v['ports']})
            max_child_edges = max(max_child_edges, len(gports))
            child = Fr(0)
            for bits in itertools.product((0, 1), repeat=len(gports)):
                pa = dict(zip(gports, bits)); prod = Fr(1)
                for v in gverts: prod *= tensor_val(v, {e: pa[(e, v['side'])] for e in v['ports']})
                if prod == 0: continue
                assign = {e: pa[(e, 'col')] for (e, sd) in gports if sd == 'col'}   # X bits of group g
                Yg = {e: pa[(e, 'row')] for (e, sd) in gports if sd == 'row'}       # Y bits of group g
                for P, pk in enumerate(packets):
                    # packet tensor for (P, g)
                    poly = {tuple([0] * nm): Fr(1)}
                    for e, (P2, x, rv, cv) in enumerate(edges):
                        if P2 != P or group_of_row(P, x) != g: continue
                        local, modec = row_form(e)
                        lin = {tuple([0] * nm): sum(c * assign[e2] for e2, c in local.items())}
                        for n, c in modec.items():
                            ex = [0] * nm; ex[n] = 1; lin[tuple(ex)] = c
                        if Yg[e] == 0:  # 1 - (.)
                            lin = {k: -c for k, c in lin.items()}; lin[tuple([0] * nm)] = lin.get(tuple([0] * nm), Fr(0)) + 1
                        poly = pmul(poly, lin, modes, Pprec)
                    # extract coefficient of beta restricted to modes targeted at g in P
                    want = tuple(beta[n] if (modes['key'][n][0] == P and modes['tgt'][n] == g) else 0 for n in range(nm))
                    coef = poly.get(want, Fr(0))
                    # must not depend on other modes: poly only involves modes targeted at g in P
                    for k in poly:
                        assert all(k[n] == 0 or (modes['key'][n][0] == P and modes['tgt'][n] == g) for n in range(nm))
                    for n in range(nm):
                        if modes['key'][n][0] == P and modes['src'][n] == g and beta[n] > 0:
                            coef *= Fr(L_Z(n, assign)) ** beta[n]
                    prod *= coef
                    if prod == 0: break
                child += prod
            prod_g *= child
        total += prod_g
    Fd = F_direct(Fr(T), packets, vertices, edges)
    diff = Fd - total
    ok = (diff == 0) or v2(diff) >= Pprec
    if not ok: print("   residual v2(F - sum) =", v2(diff), "needed", Pprec)
    return ok, M, nm, nbeta, max_child_edges, Z0

if __name__ == '__main__':
    for seed in [0, 1, 2, 3, 4, 5]:
        for t in [1, -3, 2, -2]:
            for zeta in [0, 1, -1, 2]:
                for Pprec in [3, 4]:
                    ok, M, nm, nb, mce, Z0 = check(seed, t, zeta, Pprec)
                    print(f"seed={seed} t={t:+d} (i={v2(t)}) zeta={zeta:+d} P={Pprec}: M={M} modes={nm} tuples={nb} "
                          f"max child edges={mce} (6M/r={6*M//r}) contraction={Z0}  (D.16) mod 2^P: {ok}")
                    if not ok: sys.exit("FAIL")
    print("all (D.16) identities hold")
