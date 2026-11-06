"""One level of the Section D.4 recursion on a toy bipartite network, with
r groups and a label coordinates (the identity (D.16) does not depend on
r = 64; we use r = 2 or 3 and a = 2 so the children are contractible).

What is built literally from the text
  * Lemma D.3 packets: vertex labels in [r]^a, pair-label classes, padding to
    H_pad slots, packets of L = 2^a slots whose bit i gives the orientation in
    coordinate i (or the copy when the pair is equal); every edge occupies the
    same slot at both ends.                                    (lines 4705-4749)
  * (D.7) W_xy(T) = C(T) / (C'(0) (T - (y - x))) within a packet, zero across.
  * (D.8) F(T) = sum_{X,Y} A(Y) B(X) prod_x l_{Y_x}((W(T) X)_x).
  * Lemma D.4: W(t + alpha z) and F(t + alpha z) are 2-integral for all t in S.
  * D.4.5: at a node t with i = v2(t) < u, groups = symbol in coordinate i,
    local/crossing entries, tiles y = y0 + 2^{i+1} j, the expansion (D.12),
    modes Z = (packet, tile, b) of weight b+1 with L_Z(X) = sum j^b X_y,
    source/target groups, divisibility of the mode coefficients by 2^{w_Z}.
  * D.4.6 children: for each group g and exponent tuple beta, group-g vertices
    on one side, one vertex per packet on the other, with the packet tensor
    defined by coefficient extraction times prod L_Z(X)^{beta_Z}.
  * (D.16): F(t + alpha zeta) == sum_beta prod_g Z_{g,beta}  (mod 2^P), where
    the sum is over tuples with sum_Z w_Z beta_Z < P.
    (The text's precision p_t is replaced by a small P; the identity's proof is
    the same for any P, and the real p_t is tested in lemma_d5_hermite.py.)

Run:  python3 -I recursion_identity.py [seed] [r] [P] [neg]   (neg = also run the negative control)
"""
from __future__ import annotations
import os, random, sys
from fractions import Fraction
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpoly import v2, is_2integral, pmul, pscale, peval, pshift, pdiv_linear, lagrange_interpolate
from tn import Network


# ----------------------------------------------------------------------------
# toy network and packets
# ----------------------------------------------------------------------------
class Toy:
    def __init__(self, r, a, n_rows, n_cols, edges, rng):
        self.r, self.a = r, a
        self.L = 1 << a
        self.S = list(range(-self.L, self.L))
        self.alpha = 1 << (a + 1)
        self.n_rows, self.n_cols = n_rows, n_cols
        self.edges = edges              # list of (row_vertex, col_vertex)
        self.M = len(edges)
        # random integer tensors: row vertex tensor on its ports (bits of its edges)
        self.row_ports = {v: [e for e, (rv, cv) in enumerate(edges) if rv == v] for v in range(n_rows)}
        self.col_ports = {v: [e for e, (rv, cv) in enumerate(edges) if cv == v] for v in range(n_cols)}
        self.row_tensor = {v: {bits: rng.randint(-3, 3) for bits in product((0, 1), repeat=len(self.row_ports[v]))}
                           for v in range(n_rows)}
        self.col_tensor = {v: {bits: rng.randint(-3, 3) for bits in product((0, 1), repeat=len(self.col_ports[v]))}
                           for v in range(n_cols)}
        # labels in [r]^a (1-based symbols)
        self.row_label = {v: tuple(rng.randint(1, r) for _ in range(a)) for v in range(n_rows)}
        self.col_label = {v: tuple(rng.randint(1, r) for _ in range(a)) for v in range(n_cols)}
        self._pack()
        # precompute C'(0)
        c = Fraction(1)
        for t in self.S:
            if t != 0:
                c *= -t
        self.Cp0 = c

    def _pack(self):
        """Lemma D.3 packets.  self.packets: list of dict(pairs=tuple of unordered pairs per
        coordinate, slots: dict slot -> edge or None).  self.slot_of[e] = (packet index, slot)."""
        L, a = self.L, self.a
        classes = {}
        for e, (rv, cv) in enumerate(self.edges):
            classes.setdefault((self.row_label[rv], self.col_label[cv]), []).append(e)
        max_load = max(len(v) for v in classes.values())
        Hpad = ((max_load + L - 1) // L) * L           # max load rounded up to a multiple of L
        # group classes by their packet type: the tuple of unordered pairs per coordinate
        types = {}
        for (rl, cl), es in classes.items():
            typ = tuple(tuple(sorted((rl[i], cl[i]))) for i in range(a))
            types.setdefault(typ, {})[(rl, cl)] = list(es)
        self.packets = []
        self.slot_of = {}
        for typ, members in types.items():
            unequal = [i for i in range(a) if typ[i][0] != typ[i][1]]
            # every compatible ordered class, padded to Hpad slots (also the absent ones)
            def cls_of_slot(s):
                rl, cl = [], []
                for i in range(a):
                    lo, hi = typ[i]
                    if lo == hi:
                        rl.append(lo); cl.append(lo)
                    else:
                        bit = (s >> i) & 1
                        rl.append(lo if bit == 0 else hi)
                        cl.append(hi if bit == 0 else lo)
                return (tuple(rl), tuple(cl))
            n_packets = Hpad * (1 << len(unequal)) // L
            queues = {c: list(es) for c, es in members.items()}
            for pk in range(n_packets):
                slots = {}
                for s in range(L):
                    c = cls_of_slot(s)
                    q = queues.get(c, [])
                    slots[s] = q.pop(0) if q else None
                if any(v is not None for v in slots.values()):
                    idx = len(self.packets)
                    self.packets.append(dict(pairs=typ, slots=slots))
                    for s, e in slots.items():
                        if e is not None:
                            self.slot_of[e] = (idx, s)
            assert all(not q for q in queues.values()), "slots exhausted before edges placed"
        assert len(self.slot_of) == self.M

    # ---- (D.7) ---------------------------------------------------------
    def W_poly(self, x, y):
        """W_xy(T) as an exact polynomial in T (x, y slots in one packet)."""
        c = [Fraction(1)]
        for s in self.S:
            if s != y - x:
                c = pmul(c, [Fraction(-s), Fraction(1)])
        return pscale(c, 1 / self.Cp0)

    def W_at(self, x, y, T):
        return peval(self.W_poly(x, y), Fraction(T))

    # ---- (D.8) ---------------------------------------------------------
    def A(self, Y):
        p = 1
        for v in range(self.n_rows):
            p *= self.row_tensor[v][tuple(Y[e] for e in self.row_ports[v])]
        return p

    def B(self, X):
        p = 1
        for v in range(self.n_cols):
            p *= self.col_tensor[v][tuple(X[e] for e in self.col_ports[v])]
        return p

    def row_form_at(self, e, X, T):
        """(W(T) X)_x for the row port of edge e, at numeric T."""
        pk, x = self.slot_of[e]
        s = Fraction(0)
        for y, e2 in self.packets[pk]["slots"].items():
            if e2 is not None and X[e2]:
                s += self.W_at(x, y, T)
        return s

    def F_at(self, T):
        total = Fraction(0)
        M = self.M
        for X in product((0, 1), repeat=M):
            b = self.B(X)
            if b == 0:
                continue
            forms = [self.row_form_at(e, X, T) for e in range(M)]
            for Y in product((0, 1), repeat=M):
                a = self.A(Y)
                if a == 0:
                    continue
                term = Fraction(a * b)
                for e in range(M):
                    term *= forms[e] if Y[e] else 1 - forms[e]
                    if term == 0:
                        break
                total += term
        return total

    def contraction(self):
        """Direct contraction of the original network (sum over edge bits)."""
        total = 0
        for X in product((0, 1), repeat=self.M):
            total += self.A(X) * self.B(X)
        return total

    # ---- Lemma D.4 ------------------------------------------------------
    def check_lemma_d4(self):
        ok = True
        for pk in self.packets:
            real = [s for s, e in pk["slots"].items() if e is not None]
            for x in real:
                for y in real:
                    Wp = self.W_poly(x, y)
                    for t in self.S:
                        if not all(is_2integral(c) for c in pshift(Wp, t, self.alpha)):
                            ok = False
        return ok

    # ---- D.4.5 / D.4.6 --------------------------------------------------
    def group_of_row(self, v, i):
        return self.row_label[v][i]

    def group_of_col(self, v, i):
        return self.col_label[v][i]

    def modes(self, t, P):
        """All modes at node t: list of dict(packet, y0, b, w, source, target)."""
        i = int(v2(t))
        out = []
        for pi, pk in enumerate(self.packets):
            lo, hi = pk["pairs"][i]
            if lo == hi:
                continue
            for y0 in range(1 << (i + 1)):
                bit = (y0 >> i) & 1
                col_sym = hi if bit == 0 else lo        # column symbol of slots with this bit
                row_sym = lo if bit == 0 else hi        # row symbol of slots with this bit (= target)
                for b in range(P - 1):                  # b + 1 < P
                    out.append(dict(packet=pi, y0=y0, b=b, w=b + 1, source=col_sym, target=row_sym))
        return out

    def mode_coeff(self, x, y0, b, T, i):
        """coefficient of Z_(packet, y0, b) in the row form of row slot x, at numeric T:
        C(T)/(C'(0)(T - y0 + x)) * (2^{i+1}/(T - y0 + x))^b."""
        first = self.W_at(x, y0, T)       # C(T)/(C'(0)(T - (y0 - x))) as a polynomial value
        den = Fraction(T) - y0 + x
        assert den != 0
        return first * (Fraction(1 << (i + 1)) / den) ** b

    def check_D12(self, t, zeta, P):
        """(D.12): W_xy(T) == sum_{b+1<P} coeff * j^b  (mod 2^P) for crossing pairs,
        and v2(coeff of weight-w mode) >= w."""
        i = int(v2(t))
        T = t + self.alpha * zeta
        ok_series, ok_div, n = True, True, 0
        for pk in self.packets:
            lo, hi = pk["pairs"][i]
            if lo == hi:
                continue
            real = [s for s, e in pk["slots"].items() if e is not None]
            for x in real:
                for y in real:
                    if ((x >> i) & 1) != ((y >> i) & 1):
                        continue                        # local
                    y0, j = y % (1 << (i + 1)), y >> (i + 1)
                    assert v2(t - y0 + x) <= i
                    s = Fraction(0)
                    for b in range(P - 1):
                        c = self.mode_coeff(x, y0, b, T, i)
                        if v2(c) < b + 1:
                            ok_div = False
                        s += c * (j ** b)
                    if v2(s - self.W_at(x, y, T)) < P:
                        ok_series = False
                    n += 1
        return ok_series, ok_div, n

    def child_contraction(self, g, beta, modes, t, zeta, P):
        """Contraction of the child network for group g and exponent tuple beta."""
        i = int(v2(t))
        T = t + self.alpha * zeta
        net = Network()
        # retained ports: ports of group-g vertices; one child edge per retained port
        edge_of_port = {}      # ('r'|'c', e) -> child edge id
        for v in range(self.n_rows):
            if self.group_of_row(v, i) == g:
                es = [net.new_edge() for _ in self.row_ports[v]]
                for e, ce in zip(self.row_ports[v], es):
                    edge_of_port[('r', e)] = ce
                tab = self.row_tensor[v]
                net.add_vertex(es, lambda bits, tab=tab: tab[bits])
        for v in range(self.n_cols):
            if self.group_of_col(v, i) == g:
                es = [net.new_edge() for _ in self.col_ports[v]]
                for e, ce in zip(self.col_ports[v], es):
                    edge_of_port[('c', e)] = ce
                tab = self.col_tensor[v]
                net.add_vertex(es, lambda bits, tab=tab: tab[bits])
        # one vertex per packet
        for pi, pk in enumerate(self.packets):
            rows_g = [(s, e) for s, e in pk["slots"].items() if e is not None and self.group_of_row(self.edges[e][0], i) == g]
            cols_g = [(s, e) for s, e in pk["slots"].items() if e is not None and self.group_of_col(self.edges[e][1], i) == g]
            tmodes = [m for m in modes if m["packet"] == pi and m["target"] == g and pk["pairs"][i][0] != pk["pairs"][i][1]]
            smodes = [m for m in modes if m["packet"] == pi and m["source"] == g and pk["pairs"][i][0] != pk["pairs"][i][1]]
            ports = [('r', e) for s, e in rows_g] + [('c', e) for s, e in cols_g]
            ces = [edge_of_port[pt] for pt in ports]
            if not ports:
                # packet vertex with no retained ports: scalar entry
                pass

            def entry(bits, rows_g=rows_g, cols_g=cols_g, tmodes=tmodes, smodes=smodes, pk=pk):
                Ybits = dict(zip([e for s, e in rows_g], bits[:len(rows_g)]))
                Xbits = dict(zip([e for s, e in cols_g], bits[len(rows_g):]))
                # product over group-g rows of l_{Y_x}(local + sum c_Z Z), as a polynomial in the
                # targeted modes, truncated at total weight >= P
                mkeys = [(m["y0"], m["b"]) for m in tmodes]
                widx = {k: m["w"] for k, m in zip(mkeys, tmodes)}
                poly = {tuple([0] * len(mkeys)): Fraction(1)}
                for x, e in rows_g:
                    # local part: columns of group g in this packet
                    loc = Fraction(0)
                    for y, e2 in cols_g:
                        if ((x >> i) & 1) != ((y >> i) & 1) or pk["pairs"][i][0] == pk["pairs"][i][1]:
                            if Xbits[e2]:
                                loc += self.W_at(x, y, T)
                    # crossing modes: tiles y0 with bit i equal to x's bit i
                    affine = {tuple([0] * len(mkeys)): loc}
                    if pk["pairs"][i][0] != pk["pairs"][i][1]:
                        for k, (y0, b) in enumerate(mkeys):
                            if ((y0 >> i) & 1) == ((x >> i) & 1):
                                ex = [0] * len(mkeys); ex[k] = 1
                                affine[tuple(ex)] = self.mode_coeff(x, y0, b, T, i)
                    if Ybits[e]:
                        fac = affine
                    else:
                        fac = {k: -v for k, v in affine.items()}
                        z = tuple([0] * len(mkeys))
                        fac[z] = fac.get(z, 0) + 1
                    new = {}
                    for ea, va in poly.items():
                        for eb, vb in fac.items():
                            ex = tuple(p + q for p, q in zip(ea, eb))
                            if sum(widx[mk] * n for mk, n in zip(mkeys, ex)) >= P:
                                continue
                            new[ex] = new.get(ex, 0) + va * vb
                    poly = new
                want = tuple(beta.get((pi, m["y0"], m["b"]), 0) for m in tmodes)
                val = poly.get(want, Fraction(0))
                if val == 0:
                    return Fraction(0)
                for m in smodes:
                    bz = beta.get((pi, m["y0"], m["b"]), 0)
                    if bz == 0:
                        continue
                    LZ = Fraction(0)
                    for y, e2 in cols_g:
                        if y % (1 << (i + 1)) == m["y0"] and Xbits[e2]:
                            LZ += (y >> (i + 1)) ** m["b"]
                    val *= LZ ** bz
                return val
            net.add_vertex(ces, entry)
        return net.contract()

    def check_D16(self, t, zeta, P, budget_shift=0):
        """(D.16) at node t, value zeta, precision P.  budget_shift>0 is a negative control:
        tuples are restricted to sum w beta < P - budget_shift while still checking mod 2^P."""
        i = int(v2(t))
        T = t + self.alpha * zeta
        modes = self.modes(t, P)
        # effective modes: tile has a real column (else L_Z = 0 forces beta_Z = 0) and
        # the target group has a real row in the packet (else coefficient 0 for beta_Z > 0)
        eff = []
        for m in modes:
            pk = self.packets[m["packet"]]
            has_col = any(e is not None and y % (1 << (i + 1)) == m["y0"] and self.group_of_col(self.edges[e][1], i) == m["source"]
                          for y, e in pk["slots"].items())
            has_row = any(e is not None and self.group_of_row(self.edges[e][0], i) == m["target"] and ((x >> i) & 1) == ((m["y0"] >> i) & 1)
                          for x, e in pk["slots"].items())
            if has_col and has_row:
                eff.append(m)
        # enumerate tuples beta over effective modes with sum w beta < P
        keys = [(m["packet"], m["y0"], m["b"]) for m in eff]
        ws = [m["w"] for m in eff]
        tuples = []

        def rec(k, budget, cur):
            if k == len(keys):
                tuples.append(dict(cur)); return
            for n in range(0, budget // ws[k] + 1):
                if n:
                    cur[keys[k]] = n
                rec(k + 1, budget - n * ws[k], cur)
                if n:
                    del cur[keys[k]]
        rec(0, P - 1 - budget_shift, {})
        groups = sorted(set([self.row_label[v][i] for v in range(self.n_rows)] + [self.col_label[v][i] for v in range(self.n_cols)]))
        rhs = Fraction(0)
        for beta in tuples:
            term = Fraction(1)
            for g in groups:
                term *= self.child_contraction(g, beta, modes, t, zeta, P)
                if term == 0:
                    break
            rhs += term
        lhs = self.F_at(T)
        return v2(lhs - rhs) >= P, len(tuples), len(eff), lhs, rhs, (lhs != rhs)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    r = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    P = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    rng = random.Random(seed)
    a = 2
    n_ok = n_tests = n_nontriv = n_neg = n_neg_fail = 0
    negative = len(sys.argv) > 4 and sys.argv[4] == 'neg'
    for trial in range(4):
        n_rows, n_cols = rng.randint(2, 3), rng.randint(2, 3)
        M = rng.randint(4, 6)
        edges = [(rng.randrange(n_rows), rng.randrange(n_cols)) for _ in range(M)]
        toy = Toy(r, a, n_rows, n_cols, edges, rng)
        print(f"trial {trial}: r={r} a={a} rows={n_rows} cols={n_cols} M={M} packets={len(toy.packets)} "
              f"labels rows={list(toy.row_label.values())} cols={list(toy.col_label.values())}")
        # F(0) is the contraction
        F0 = toy.F_at(0)
        assert F0 == toy.contraction(), (F0, toy.contraction())
        print("   F(0) = contraction:", F0)
        # Lemma D.4
        print("   Lemma D.4 integrality of W(t+alpha z) for all t in S:", toy.check_lemma_d4())
        # F as an exact polynomial (degree <= M(2L-1)) and Lemma D.4 for F(t + alpha z)
        degF = M * (2 * toy.L - 1)
        Fpoly = lagrange_interpolate([(T, toy.F_at(T)) for T in range(degF + 1)])
        assert len(Fpoly) - 1 <= degF
        Fint = all(all(is_2integral(c) for c in pshift(Fpoly, t, toy.alpha)) for t in toy.S)
        print(f"   deg F = {len(Fpoly)-1} <= M(2L-1) = {degF}; F(t+alpha z) 2-integral for all t in S: {Fint}")
        # nodes with i < u for u = a: t with v2(t) < a
        for t in toy.S:
            if t == 0 or v2(t) >= a:
                continue
            for zeta in (0, 1, 3):
                ok12, okdiv, npairs = toy.check_D12(t, zeta, P)
                ok16, ntuples, neff, lhs, rhs, nontriv = toy.check_D16(t, zeta, P)
                n_tests += 1
                n_ok += ok16
                n_nontriv += nontriv
                neg = ""
                if nontriv and negative:
                    # each mode coefficient has valuation >= w_Z + (a - i) (the text claims only >= w_Z),
                    # so the truncation is exact down to budget P - (a - i); the control cuts one more.
                    shift = a - int(v2(t)) + 1
                    okneg, _, _, _, _, _ = toy.check_D16(t, zeta, P, budget_shift=shift)
                    n_neg += 1
                    n_neg_fail += (not okneg)
                    neg = f"; control (budget P-{shift}) ok={okneg}"
                print(f"   t={t:2d} (i={int(v2(t))}) zeta={zeta}: (D.12) series ok={ok12} divisibility ok={okdiv} "
                      f"on {npairs} crossing pairs; (D.16) ok={ok16} with {ntuples} tuples over {neff} effective modes; "
                      f"lhs!=rhs exactly: {nontriv}{neg}")
    print(f"(D.16) held in {n_ok}/{n_tests} (node, zeta) tests at P={P}, r={r}; non-trivial (lhs != rhs exactly): {n_nontriv}; "
          f"negative controls run: {n_neg}, of which failed as they should: {n_neg_fail}")


if __name__ == "__main__":
    main()
