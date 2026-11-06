"""Appendix D.3 / Lemma D.2 (paper_flow.txt lines 4365-4560): counting common
zeros of a sparse polynomial system over F2 by contraction, tested at small
size with exact arithmetic in B = (Z/2^p)[V]/(V^ell), p = ell = n+1.

Tested claims
  (a) Lemma 5.1: p_ell(y) = 1{2|y} mod 2^ell, and the division of p_ell by
      h = Y^2 - Y into e_j of degree <= 1 (this is what D.3 imports);
  (b) (D.2): sum_x S_ell( prod_i Bbar_i(z = x, V) ) == #common zeros  (mod 2^p),
      with Bbar_i the multilinear representative of B_i;
  (c) the degree bounds: V^j-coefficient of Bbar_i has incidence degree
      <= k(1+2j) and every monomial of F has degree <= K = k(a + 2(ell-1));
  (d) the subset-sum inversion [z_{i,S}] Bbar_i = sum_{T<=S} (-1)^{|S|-|T|} B_i(1_T, V);
  (e) the indexing network: J = ceil(n^{1/4}) groups per side, arrays (d_gh),
      ceil(log2 C_gh) wires per pair indexing d_gh-subsets lexicographically,
      test-group entries = coefficient of the indicated monomial, variable-group
      entries = 2^{#{v: b_v = 0}}, unused strings -> 0; the sum of the
      contractions over all arrays equals the element of B inside S_ell in (D.2).

The high-incidence branching (fixing variables in > D* scopes) is a plain
substitution and is not exercised: all variables are kept free.

Run: python3 -I d3_sparse_system.py [seed] [trials]
"""
from __future__ import annotations
import os, random, sys
from itertools import product, combinations
from math import comb, ceil, log2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tn import Network


# ---------------------------------------------------------------------------
# the ring B = (Z/2^p)[V]/(V^ell)
# ---------------------------------------------------------------------------
class BRing:
    def __init__(self, p, ell):
        self.p, self.ell, self.mod = p, ell, 1 << p

    def elem(self, coeffs):
        c = [0] * self.ell
        for j, x in enumerate(coeffs[:self.ell]):
            c[j] = x % self.mod
        return BElem(self, tuple(c))

    def const(self, x):
        return self.elem([x])


class BElem:
    __slots__ = ("R", "c")

    def __init__(self, R, c):
        self.R, self.c = R, c

    def _coerce(self, o):
        if isinstance(o, BElem):
            return o
        return self.R.const(int(o))

    def __add__(self, o):
        o = self._coerce(o)
        return BElem(self.R, tuple((a + b) % self.R.mod for a, b in zip(self.c, o.c)))
    __radd__ = __add__

    def __neg__(self):
        return BElem(self.R, tuple((-a) % self.R.mod for a in self.c))

    def __sub__(self, o):
        return self + (-self._coerce(o))

    def __mul__(self, o):
        o = self._coerce(o)
        ell, mod = self.R.ell, self.R.mod
        out = [0] * ell
        for i, a in enumerate(self.c):
            if a == 0:
                continue
            for j, b in enumerate(o.c):
                if i + j >= ell:
                    break
                out[i + j] = (out[i + j] + a * b) % mod
        return BElem(self.R, tuple(out))
    __rmul__ = __mul__

    def __eq__(self, o):
        o = self._coerce(o)
        return self.c == o.c

    def __ne__(self, o):
        return not self.__eq__(o)

    def is_zero(self):
        return all(a == 0 for a in self.c)

    def S(self):
        """The coefficient-sum map S_ell, as a residue mod 2^p."""
        return sum(self.c) % self.R.mod

    def __repr__(self):
        return f"B{self.c}"


# ---------------------------------------------------------------------------
# Lemma 5.1: p_ell and the e_j
# ---------------------------------------------------------------------------
def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def p_ell(ell):
    s = [comb(ell + j - 1, j) for j in range(ell)]
    one_minus_Y = [1, -1]
    f = [1]
    for _ in range(ell):
        f = poly_mul(f, one_minus_Y)
    return poly_mul(f, s)


def divide_by_h(poly):
    """Successive division by h = Y^2 - Y: returns [e_0, e_1, ...] each of degree < 2 (as [c0, c1])."""
    es = []
    cur = list(poly)
    while len(cur) > 2 or (len(cur) == 2 and any(cur)) or (len(cur) <= 2 and not es):
        # cur = q*(Y^2 - Y) + r
        q = [0] * max(0, len(cur) - 2)
        r = list(cur)
        for d in range(len(cur) - 1, 1, -1):
            c = r[d]
            if c == 0:
                continue
            q[d - 2] += c
            r[d] -= c
            r[d - 1] += c
        rem = [r[0] if len(r) > 0 else 0, r[1] if len(r) > 1 else 0]
        es.append(rem)
        cur = q
        if not any(cur):
            break
    return es


def check_lemma51(ell):
    pl = p_ell(ell)
    mod = 1 << ell
    ok = True
    for y in range(-40, 41):
        val = sum(c * y ** j for j, c in enumerate(pl))
        if (val - (1 if y % 2 == 0 else 0)) % mod:
            ok = False
    es = divide_by_h(pl)
    # reconstruct
    rec = [0]
    hpow = [1]
    for e in es:
        rec = [a + b for a, b in zip(rec + [0] * (len(hpow) + 1 - len(rec)), poly_mul(e, hpow) + [0] * (len(rec) - len(hpow) - 1))]
        hpow = poly_mul(hpow, [0, -1, 1])
    rec = rec[:len(pl)] + [0] * (len(pl) - len(rec))
    while len(rec) > len(pl):
        if rec[-1] != 0:
            ok = False
        rec.pop()
    ok &= (rec == pl)
    ok &= (len(es) <= ell)
    return ok, es


# ---------------------------------------------------------------------------
# multilinear polynomials over B in incidence indeterminates
# keys: (frozenset of indeterminates, ) -> BElem ; multilinear so z^2 = z
# ---------------------------------------------------------------------------
def ml_mul(P, Q, R):
    out = {}
    for s1, c1 in P.items():
        for s2, c2 in Q.items():
            key = s1 | s2
            v = c1 * c2
            if key in out:
                out[key] = out[key] + v
            else:
                out[key] = v
    return {k: v for k, v in out.items() if not v.is_zero()}


def ml_add(P, Q):
    out = dict(P)
    for k, v in Q.items():
        out[k] = out[k] + v if k in out else v
    return {k: v for k, v in out.items() if not v.is_zero()}


def ml_scale(P, c):
    return {k: v * c for k, v in P.items() if not (v * c).is_zero()}


def ml_eval(P, assignment):
    """Evaluate at a Boolean assignment dict indeterminate -> bit."""
    tot = None
    for s, c in P.items():
        if all(assignment[z] for z in s):
            tot = c if tot is None else tot + c
    return tot


def build_Bbar(i, monomials, k, R, es):
    """Bbar_i(z_i, V) for test i with the listed monomials (each a tuple of variables)."""
    ell = R.ell
    # Ltilde as a multilinear polynomial with integer coefficients 1 (in B as constants)
    Lt = {}
    for mono in monomials:
        key = frozenset((i, v) for v in mono)
        Lt[key] = Lt[key] + R.const(1) if key in Lt else R.const(1)
    # h(L) = L^2 - L
    L2 = ml_mul(Lt, Lt, R)
    hL = ml_add(L2, ml_scale(Lt, R.const(-1)))
    # B_i = sum_j e_j(L) h(L)^j V^j
    one = {frozenset(): R.const(1)}
    V = R.elem([0, 1])
    total = {}
    hpow = one
    for j in range(ell):
        if j >= len(es):
            break
        e0, e1 = es[j]
        ej = ml_add(ml_scale(one, R.const(e0)), ml_scale(Lt, R.const(e1)))
        term = ml_scale(ml_mul(ej, hpow, R), V ** 0 if False else R.elem([0] * j + [1]))
        total = ml_add(total, term)
        hpow = ml_mul(hpow, hL, R)
    return total, Lt


def B_i_direct(Lval, R, es):
    """B_i(V) for an integer value y = L~(x): sum_j e_j(y) h(y)^j V^j (Lemma 5.2's definition)."""
    coeffs = []
    hy = Lval * Lval - Lval
    for j in range(R.ell):
        if j >= len(es):
            coeffs.append(0); continue
        e0, e1 = es[j]
        coeffs.append((e0 + e1 * Lval) * hy ** j)
    return R.elem(coeffs)


def count_zeros(n, tests):
    cnt = 0
    for x in product((0, 1), repeat=n):
        ok = True
        for monos in tests:
            val = sum(all(x[v] for v in m) for m in monos) % 2
            if val:
                ok = False; break
        cnt += ok
    return cnt


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    rng = random.Random(seed)
    print("Lemma 5.1 check (p_ell(y) = 1{2|y} mod 2^ell, e_j of degree <= 1 reconstruct p_ell):",
          all(check_lemma51(l)[0] for l in range(1, 9)))
    results = dict(D2=0, deg=0, inv=0, net=0, trials=0)
    for trial in range(trials):
        n = rng.randint(4, 6)
        k = rng.choice([2, 3])
        a = rng.randint(2, 4)
        tests = []
        for _ in range(a):
            monos = set()
            for _ in range(rng.randint(1, 2)):
                deg = rng.randint(1, k)
                monos.add(tuple(sorted(rng.sample(range(n), deg))))
            tests.append(sorted(monos))
        ell = p = n + 1
        R = BRing(p, ell)
        es = divide_by_h(p_ell(ell))
        ref = count_zeros(n, tests)
        # (b) the identity (D.2)
        Bbars, Lts, scopes = [], [], []
        for i, monos in enumerate(tests):
            Bb, Lt = build_Bbar(i, monos, k, R, es)
            Bbars.append(Bb); Lts.append(Lt)
            scopes.append(sorted({v for m in monos for v in m}))
        # (c) degree bounds
        deg_ok = True
        for i, Bb in enumerate(Bbars):
            for s, c in Bb.items():
                for j, cj in enumerate(c.c):
                    if cj and len(s) > k * (1 + 2 * j):
                        deg_ok = False
        Fpoly = {frozenset(): R.const(1)}
        for Bb in Bbars:
            Fpoly = ml_mul(Fpoly, Bb, R)
        K = k * (a + 2 * (ell - 1))
        if any(len(s) > K for s in Fpoly):
            deg_ok = False
        results["deg"] += deg_ok
        # sum over x of S_ell(F(z = x))
        total = 0
        Belem_total = R.const(0)
        for x in product((0, 1), repeat=n):
            assign = {(i, v): x[v] for i in range(a) for v in range(n)}
            val = ml_eval(Fpoly, assign)
            if val is not None:
                Belem_total = Belem_total + val
                # cross-check: product of the direct B_i(L~(x)) (Lemma 5.2's objects)
                direct = R.const(1)
                for i, monos in enumerate(tests):
                    Lval = sum(all(x[v] for v in m) for m in monos)
                    direct = direct * B_i_direct(Lval, R, es)
                assert direct == val
        d2_ok = (Belem_total.S() % (1 << p)) == ref
        results["D2"] += d2_ok
        # (d) subset-sum inversion
        inv_ok = True
        for i, monos in enumerate(tests):
            I = [(i, v) for v in scopes[i]]
            for r_ in range(len(I) + 1):
                for S in combinations(I, r_):
                    acc = R.const(0)
                    for r2 in range(len(S) + 1):
                        for T in combinations(S, r2):
                            Lval = sum(all((i, v) in T for v in m) for m in monos)
                            sign = (-1) ** (len(S) - len(T))
                            acc = acc + B_i_direct(Lval, R, es) * sign
                    coef = Bbars[i].get(frozenset(S), R.const(0))
                    if acc != coef:
                        inv_ok = False
        results["inv"] += inv_ok
        # (e) the indexing network, summed over arrays
        J = ceil(n ** 0.25)
        tgroups = [list(range(g, a, J)) for g in range(J)]
        xgroups = [list(range(h, n, J)) for h in range(J)]
        inc = {}   # (g,h) -> ordered list of incidences (i, v)
        for g in range(J):
            for h in range(J):
                inc[(g, h)] = [(i, v) for i in tgroups[g] for v in xgroups[h] if v in scopes[i]]
        Ngh = {gh: len(l) for gh, l in inc.items()}
        net_sum = R.const(0)
        n_arrays = 0
        ranges = [range(Ngh[gh] + 1) for gh in sorted(inc)]
        keys = sorted(inc)
        for darr in product(*ranges):
            d = dict(zip(keys, darr))
            if sum(darr) > K:
                continue
            n_arrays += 1
            net = Network()
            wires = {}
            for gh in keys:
                C = comb(Ngh[gh], d[gh])
                nw = ceil(log2(C)) if C > 1 else 0
                wires[gh] = [net.new_edge() for _ in range(nw)]
            # decode: bits -> subset (lexicographic index of d-subsets), or None if unused
            def decode(gh, bits):
                C = comb(Ngh[gh], d[gh])
                idx = int("".join(map(str, bits)), 2) if bits else 0
                if idx >= C:
                    return None
                subs = list(combinations(inc[gh], d[gh]))  # lexicographic
                return subs[idx]
            for g in range(J):
                ghs = [(g, h) for h in range(J)]
                es_ = [w for gh in ghs for w in wires[gh]]

                def tentry(bits, g=g, ghs=ghs):
                    pos = 0
                    chosen = []
                    for gh in ghs:
                        nw = len(wires[gh])
                        sub = decode(gh, bits[pos:pos + nw]); pos += nw
                        if sub is None:
                            return R.const(0)
                        chosen.extend(sub)
                    val = R.const(1)
                    for i in tgroups[g]:
                        Si = frozenset(z for z in chosen if z[0] == i)
                        val = val * Bbars[i].get(Si, R.const(0))
                    return val
                net.add_vertex(es_, tentry)
            for h in range(J):
                ghs = [(g, h) for g in range(J)]
                es_ = [w for gh in ghs for w in wires[gh]]

                def xentry(bits, h=h, ghs=ghs):
                    pos = 0
                    chosen = []
                    for gh in ghs:
                        nw = len(wires[gh])
                        sub = decode(gh, bits[pos:pos + nw]); pos += nw
                        if sub is None:
                            return R.const(0)
                        chosen.extend(sub)
                    bv = {v: 0 for v in xgroups[h]}
                    for (i, v) in chosen:
                        bv[v] += 1
                    return R.const(pow(2, sum(1 for v in bv if bv[v] == 0), R.mod))
                net.add_vertex(es_, xentry)
            net_sum = net_sum + net.contract()
        net_ok = (net_sum == Belem_total)
        results["net"] += net_ok
        results["trials"] += 1
        print(f"trial {trial}: n={n} k={k} a={a} tests={tests} #zeros={ref} | (D.2) ok={d2_ok} "
              f"deg ok={deg_ok} inversion ok={inv_ok} network-sum ok={net_ok} ({n_arrays} arrays, J={J})")
    print("summary:", results)


if __name__ == "__main__":
    main()
