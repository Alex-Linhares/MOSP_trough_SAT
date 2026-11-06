"""Audit of Lemma D.2 (Appendix D.3): a faithful small-scale implementation of the
incidence-monomial tensor-network encoding, checked against brute force.

Pieces checked:
  * Lemma 5.1: e_j from successive division of p_l by h = Y^2 - Y; p_l(y) = 1{y even} mod 2^l
  * Lemma 5.2: S_l(prod B_i mod V^l) = prod 1{y_i even} mod 2^l for random integers
  * the Moebius formula [z_S] bar B_i = sum_{T<=S} (-1)^{|S-T|} B_i(1_T, V), against direct
    symbolic multilinear expansion
  * the degree bound (D.1): coefficients of monomials of degree > K vanish in B (with small l)
  * array enumeration, lexicographic subset index (encode/decode by binomials), wire counts
    ceil(log2 C_gh) <= N_gh and (D.3)
  * the full identity: sum over branches of S_l(sum over arrays of contractions) = #common zeros
Run: python3 -I lemma_d2_encoding.py
"""
import itertools, math, random, sys
from functools import reduce

# ---------- integer polynomials in one variable (lists, low degree first) ----------
def padd(a, b):
    n = max(len(a), len(b)); return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]
def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): r[i + j] += x * y
    return r
def ppow(a, e):
    r = [1]
    for _ in range(e): r = pmul(r, a)
    return r
def peval(a, y): return sum(c * y ** i for i, c in enumerate(a))
def pdivmod_h(a):
    """divide by h = Y^2 - Y (monic): return quotient, remainder (deg < 2), exact over Z"""
    a = list(a); q = [0] * max(len(a) - 2, 0)
    for i in range(len(a) - 1, 1, -1):
        c = a[i]; q[i - 2] = c; a[i] -= c; a[i - 1] += c   # c*Y^i = c*Y^{i-2}*(Y^2 - Y) + c*Y^{i-1}
    return q, a[:2] + [0] * (2 - len(a[:2]))

def lemma51(l):
    p = pmul(ppow([1, -1], l), [math.comb(l + j - 1, j) for j in range(l)])
    assert len(p) <= 2 * l
    for y in range(-40, 41):
        assert peval(p, y) % 2 ** l == (1 if y % 2 == 0 else 0), (l, y)
    es = []; q = p
    for j in range(l):
        q, e = pdivmod_h(q); es.append(e)
    assert all(c == 0 for c in q), 'quotient should vanish after l divisions'
    # reconstruct
    rec = [0]
    for j, e in enumerate(es): rec = padd(rec, pmul(e, ppow([0, -1, 1], j)))
    assert [c for c in rec] + [0] * (len(p) - len(rec)) == p + [0] * (len(rec) - len(p))
    return es

# ---------- the ring B = (Z/2^p)[V]/(V^l) as tuples ----------
class Ring:
    def __init__(self, p, l): self.p, self.l, self.mod = p, l, 2 ** p
    def zero(self): return (0,) * self.l
    def one(self): return (1,) + (0,) * (self.l - 1)
    def scalar(self, c): return (c % self.mod,) + (0,) * (self.l - 1)
    def add(self, a, b): return tuple((x + y) % self.mod for x, y in zip(a, b))
    def neg(self, a): return tuple((-x) % self.mod for x in a)
    def mul(self, a, b):
        r = [0] * self.l
        for i, x in enumerate(a):
            if x:
                for j in range(self.l - i):
                    if b[j]: r[i + j] = (r[i + j] + x * b[j]) % self.mod
        return tuple(r)
    def S(self, a): return sum(a) % self.mod
    def Bfactor(self, y, es):
        """B(V) = sum_j e_j(y) h(y)^j V^j with coefficients mod 2^p"""
        h = y * (y - 1)
        return tuple((peval(es[j], y) * h ** j) % self.mod for j in range(self.l))

def lemma52_check(R, es, rng):
    for _ in range(200):
        m = rng.randint(0, 6)
        ys = [rng.randint(-30, 30) for _ in range(m)]
        prod = reduce(R.mul, (R.Bfactor(y, es) for y in ys), R.one())
        want = 1 if all(y % 2 == 0 for y in ys) else 0
        assert R.S(prod) % 2 ** R.l == want % 2 ** R.l, (ys, R.S(prod), want)

# ---------- polynomials over F2 as sets of monomials (frozensets of variables) ----------
def normalize(monos):
    """combine duplicates mod 2 (powers already collapsed by using sets)"""
    out = set()
    for M in monos:
        M = frozenset(M)
        if M in out: out.remove(M)
        else: out.add(M)
    return out

def eval_F2(monos, x): return sum(all(x[v] for v in M) for M in monos) % 2
def Ltilde(monos, z):  # integer lift at Boolean point z (dict var->bit)
    return sum(1 for M in monos if all(z[v] for v in M))

def brute_count(n, polys):
    c = 0
    for x in itertools.product((0, 1), repeat=n):
        if all(eval_F2(P, x) == 0 for P in polys): c += 1
    return c

# ---------- the Lemma D.2 encoding ----------
def lemma_d2_count(n, k, polys, R, es, J=None, Dstar_override=None, verbose=False, check_degree=False):
    lam = math.ceil(math.log2(n)); nu = math.ceil(math.log2(lam)) if lam > 1 else 1
    polys = [normalize(P) for P in polys]
    scopes = [set().union(*P) if P else set() for P in polys]
    N0 = sum(len(S) for S in scopes)
    Dstar = max(1, math.ceil(N0 / n)) * math.ceil(math.sqrt(lam)) if Dstar_override is None else Dstar_override
    occ = {v: sum(v in S for S in scopes) for v in range(n)}
    high = [v for v in range(n) if occ[v] > Dstar]
    assert len(high) <= n / math.sqrt(lam) or Dstar_override is not None, (len(high), n / math.sqrt(lam))
    if J is None: J = math.ceil(n ** 0.25)
    total = 0
    stats = {'branches': 2 ** len(high), 'arrays': 0, 'max_wires': 0, 'max_degree': 0, 'D3_ok': True, 'deg_bound_ok': True}
    for fixed in itertools.product((0, 1), repeat=len(high)):
        fx = dict(zip(high, fixed))
        # substitute and renormalize
        branch = []
        for P in polys:
            monos = []
            for M in P:
                if any(fx.get(v, 1) == 0 for v in M): continue
                monos.append(frozenset(v for v in M if v not in fx))
            branch.append(normalize(monos))
        free = [v for v in range(n) if v not in fx]
        if any(P == {frozenset()} for P in branch): continue          # constant-one equation
        branch = [P for P in branch if P]                              # discard constant-zero
        if not branch:
            total += 2 ** len(free); continue
        a = len(branch)
        I = [sorted(set().union(*P)) for P in branch]
        for Ii in I: assert len(Ii) <= k * lam ** 10  # the c-bound is vacuous here
        # coefficient tables of bar B_i via the paper's Moebius formula
        tables = []
        for i, P in enumerate(branch):
            Ii = I[i]; tab = {}
            evals = {}
            for T in itertools.product((0, 1), repeat=len(Ii)):
                z = dict(zip(Ii, T)); evals[T] = R.Bfactor(Ltilde(P, z), es)
            for Sb in itertools.product((0, 1), repeat=len(Ii)):
                acc = R.zero()
                for T in itertools.product((0, 1), repeat=len(Ii)):
                    if any(t and not s for t, s in zip(T, Sb)): continue
                    term = evals[T]
                    if (sum(Sb) - sum(T)) % 2: term = R.neg(term)
                    acc = R.add(acc, term)
                tab[frozenset(v for v, s in zip(Ii, Sb) if s)] = acc
            tables.append(tab)
            if check_degree:
                # cross-check against direct symbolic multilinear expansion of B_i
                direct = symbolic_Bbar(P, Ii, R, es)
                assert direct == tab, 'Moebius formula disagrees with direct expansion'
        # groups
        tests_g = [list(range(g, a, J)) for g in range(J)]
        vars_h = [free[h::J] for h in range(J)]
        var_group = {v: h for h, vs in enumerate(vars_h) for v in vs}
        inc = {(g, h): [] for g in range(J) for h in range(J)}
        for g in range(J):
            for i in tests_g[g]:
                for v in I[i]: inc[(g, var_group[v])].append((i, v))
        N = sum(len(x) for x in inc.values())
        K = k * (a + 2 * (R.l - 1))
        if check_degree:
            # every monomial of F of degree > K must have zero coefficient in B
            Fcoef = full_product_coeffs(tables, I, R)
            viol = [S for S, c in Fcoef.items() if len(S) > K and any(c)]
            if viol: stats['deg_bound_ok'] = False
            stats['maxdeg_nonzero'] = max((len(S) for S, c in Fcoef.items() if any(c)), default=0)
            stats['K'] = K
        pairs = sorted(inc)
        ranges = [range(0, min(len(inc[pr]), K) + 1) for pr in pairs]
        branch_sum = R.zero()
        for d in itertools.product(*ranges):
            if sum(d) > K: continue
            stats['arrays'] += 1
            wires = {pr: math.ceil(math.log2(math.comb(len(inc[pr]), dd))) for pr, dd in zip(pairs, d)}
            for pr, dd in zip(pairs, d): assert wires[pr] <= len(inc[pr])        # ceil(log2 C) <= N_gh
            M = sum(wires.values())
            stats['max_wires'] = max(stats['max_wires'], M)
            D3 = J * J + math.log2(math.comb(N + K, K))
            if M > D3 + 1e-9: stats['D3_ok'] = False
            degs = {}
            for (g, h), w in wires.items():
                degs[('T', g)] = degs.get(('T', g), 0) + w; degs[('X', h)] = degs.get(('X', h), 0) + w
            stats['max_degree'] = max(stats['max_degree'], max(degs.values()))
            # enumerate valid wire indices = subsets of each pair's incidences of the given size,
            # through the lexicographic index (encode/decode roundtrip checked)
            choices = []
            for pr, dd in zip(pairs, d):
                lst = inc[pr]; C = math.comb(len(lst), dd); subs = []
                for idx in range(C):
                    sub = decode_lex(lst, dd, idx); assert encode_lex(lst, dd, sub) == idx
                    subs.append(sub)
                # strings with idx >= C are the "unused bit strings" giving entry zero
                choices.append(subs)
            for combo in itertools.product(*choices):
                Ssel = {i: set() for i in range(a)}
                bcount = {v: 0 for v in free}
                for sub in combo:
                    for (i, v) in sub: Ssel[i].add(v); bcount[v] += 1
                entry = R.one()
                for g in range(J):                      # test-group entries
                    for i in tests_g[g]: entry = R.mul(entry, tables[i][frozenset(Ssel[i])])
                for h in range(J):                      # variable-group entries
                    zeros = sum(1 for v in vars_h[h] if bcount[v] == 0)
                    entry = R.mul(entry, R.scalar(2 ** zeros))
                branch_sum = R.add(branch_sum, entry)
        total += R.S(branch_sum)
    return total % R.mod, stats

def decode_lex(lst, dd, idx):
    """lexicographic index -> subset of size dd, by counting completions with binomials"""
    sub = []; need = dd
    for pos, item in enumerate(lst):
        if need == 0: break
        rem = len(lst) - pos - 1
        with_item = math.comb(rem, need - 1)   # completions if we take `item`
        if idx < with_item: sub.append(item); need -= 1
        else: idx -= with_item
    assert need == 0 and idx == 0
    return sub
def encode_lex(lst, dd, sub):
    idx = 0; need = dd; subset = set(sub)
    for pos, item in enumerate(lst):
        if need == 0: break
        rem = len(lst) - pos - 1
        if item in subset: need -= 1
        else: idx += math.comb(rem, need - 1)
    return idx

def symbolic_Bbar(P, Ii, R, es):
    """direct multilinear expansion of B_i(z,V) = sum_j e_j(L) h(L)^j V^j as a dict subset -> B"""
    # polynomials in z over Z as dict frozenset->int, multilinear (sets)
    def mmul(A, B):
        out = {}
        for s, c in A.items():
            for t, d in B.items():
                u = s | t; out[u] = out.get(u, 0) + c * d
        return out
    def madd(A, B, scale=1):
        out = dict(A)
        for t, d in B.items(): out[t] = out.get(t, 0) + scale * d
        return out
    L = {frozenset(M): 1 for M in P}
    one = {frozenset(): 1}
    h = madd(mmul(L, L), L, -1)            # L(L-1)
    coef = {}
    hj = dict(one)
    for j in range(R.l):
        ej = madd({frozenset(): es[j][0]}, L, es[j][1])    # e_j(L) = a_j + b_j L
        term = mmul(ej, hj)
        for s, c in term.items():
            vec = list(coef.get(s, R.zero())); vec[j] = (vec[j] + c) % R.mod; coef[s] = tuple(vec)
        hj = mmul(hj, h)
    out = {}
    for Sb in itertools.product((0, 1), repeat=len(Ii)):
        S = frozenset(v for v, s in zip(Ii, Sb) if s); out[S] = coef.get(S, R.zero())
    return out

def full_product_coeffs(tables, I, R):
    """F = prod_i bar B_i over disjoint incidence variables; coefficient dict incidence-set -> B"""
    F = {frozenset(): R.one()}
    for i, tab in enumerate(tables):
        new = {}
        for s, c in F.items():
            for S, d in tab.items():
                key = s | frozenset((i, v) for v in S)
                val = R.mul(c, d)
                if any(val): new[key] = R.add(new.get(key, R.zero()), val)
        F = {kk: vv for kk, vv in new.items() if any(vv)}
    return F

def random_system(n, a, k, maxmono, rng):
    polys = []
    for _ in range(a):
        monos = []
        for _ in range(rng.randint(1, maxmono)):
            deg = rng.randint(0, k)
            monos.append(frozenset(rng.sample(range(n), deg)))
        polys.append(monos)
    return polys

if __name__ == '__main__':
    rng = random.Random(7)
    for l in (1, 2, 3, 5, 7, 9):
        es = lemma51(l); R = Ring(l, l); lemma52_check(R, es, rng)
    print('Lemma 5.1 construction and Lemma 5.2 identity: OK for l in 1..9')

    # (a) full-precision runs, p = l = n+1, random systems; compare with brute force
    bad = 0; runs = 0
    for trial in range(40):
        n = rng.choice([4, 5, 5, 6]); k = rng.choice([1, 2, 3]); a = rng.randint(1, 4)
        polys = random_system(n, a, k, 3, rng)
        R = Ring(n + 1, n + 1); es = lemma51(n + 1)
        got, st = lemma_d2_count(n, k, polys, R, es)
        want = brute_count(n, polys)
        runs += 1
        if got != want: bad += 1; print('MISMATCH', n, k, polys, got, want)
        assert st['D3_ok'], 'wire bound (D.3) violated'
    print(f'(a) p = l = n+1: {runs} random systems, {bad} mismatches; (D.3) held on every array')

    # (b) small l = p so that the degree bound K bites; check (D.1) and the identity mod 2^l
    bad = 0; runs = 0; bites = 0
    for trial in range(40):
        n = rng.choice([4, 5, 6]); k = rng.choice([1, 2]); a = rng.randint(2, 4); l = rng.choice([1, 2, 3])
        polys = random_system(n, a, k, 3, rng)
        R = Ring(l, l); es = lemma51(l)
        got, st = lemma_d2_count(n, k, polys, R, es, check_degree=True)
        want = brute_count(n, polys) % 2 ** l
        runs += 1
        if got != want: bad += 1; print('MISMATCH-smalll', n, k, l, polys, got, want)
        assert st['deg_bound_ok'], ('coefficient of degree > K nonzero', st)
        if st.get('maxdeg_nonzero', 0) > 0 and st['K'] < sum(len(set().union(*normalize(P))) for P in polys): bites += 1
    print(f'(b) l = p in 1..3: {runs} systems, {bad} mismatches; (D.1) degree bound never violated; '
          f'Moebius = direct expansion on every test; K below total incidence count on {bites} systems')

    # (c) force the high-incidence branching with an artificially small D*
    bad = 0
    for trial in range(15):
        n = 5; k = 2; a = rng.randint(2, 4)
        polys = random_system(n, a, k, 3, rng)
        R = Ring(n + 1, n + 1); es = lemma51(n + 1)
        got, st = lemma_d2_count(n, k, polys, R, es, Dstar_override=1)
        want = brute_count(n, polys)
        if got != want: bad += 1; print('MISMATCH-branch', polys, got, want)
    print(f'(c) forced branching (D* = 1): 15 systems, {bad} mismatches')
