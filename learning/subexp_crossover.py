"""Algorithms from the counting theorem for problems on graphs of linear
pathwidth: the encodings of loop0014 item 06 (`reports/subexp_pathwidth.md`
§6), each checked by brute force on every graph of the networkx atlas (all
graphs to 7 vertices) before it was stated, and the crossover table.

    python -m learning.subexp_crossover            # the full check, atlas to 7
    python -m learning.subexp_crossover --nmax 5   # quick
    python -m learning.subexp_crossover --table    # the crossover table only

Graphs are `(n, adj)` with `adj` a list of neighbour bitmasks, as in
`paper1/complex_check.py`. A CNF is a list of clauses, each a list of
non-zero ints (DIMACS literals); `count_models` is CaDiCaL with a blocking
clause over every variable (`learning.subexp_chain`), so it counts exactly.

The encodings, every one with one Boolean variable per vertex (or per edge)
and auxiliary variables that are *functions* of those, so that the model
count is the count of the combinatorial objects (count-preserving):

- `indep_cnf`: independent sets — `¬x_u ∨ ¬x_w` per edge; width 2, `n`
  variables, `m` clauses; `count = #independent sets` (ETH paper, Cor. 1.3).
- `indep_atleast_cnf(g, t)`: independent sets of size `≥ t` — the same plus
  `Σ x_v ≥ t` compiled through a binary adder tree (`popcount_circuit`) and a
  comparator against the constant `t` (`ge_const`), Tseitin-encoded, width
  3, `O(n)` auxiliary variables (`threshold_aux_ratio` measures the constant);
  satisfiable iff `α(G) ≥ t`, `count = #{S independent : |S| ≥ t}`.
- `coloring_cnf(g, q)`: proper `q`-colourings — `q n` variables, exactly one
  colour per vertex (one clause of width `q`, `C(q, 2)` of width 2), no
  equal colours across an edge (`q` clauses of width 2 per edge);
  `count = #proper q-colourings` (Cor. 1.3).
- `domset_cnf(g)`: dominating sets — `x_v ∨ ⋁_{u ∈ N(v)} x_u` per vertex,
  width `Δ + 1`; `domset_cnf(g, tseitin=True)` compiles each clause to width
  3 with `deg(v)` auxiliaries, so `n + 2m` variables; `domset_atmost_cnf`
  adds `Σ x_v ≤ t`; satisfiable iff `γ(G) ≤ t`.
- `maxcut_cnf(g, t)`: one side bit per vertex, one XOR auxiliary per edge,
  `Σ_e (x_u ⊕ x_w) ≥ t` through the adder tree; `n + O(m)` variables,
  width 3; satisfiable iff `maxcut(G) ≥ t`, `count = #{sides : cut ≥ t}`.
- `oct_cnf(g, t)`: odd cycle transversal `≤ t` — a deletion bit and a side
  bit per vertex, two clauses of width 4 per edge, `Σ d_v ≤ t`; decision only
  (the count is `Σ_D 2^{|D|} 2^{cc(G − D)}`: the deleted vertices' side bits are free).
- `hamcycle_cutcount_cnf(g)`: Cut & Count with the DP replaced by a count —
  one variable per edge, one side bit per vertex, exactly two chosen edges
  at every vertex (two thresholds), a chosen edge keeps both ends on one
  side, vertex 0 on side 0; `count = Σ_{2-factors X} 2^{cc(X) − 1}`, so
  `count ≡ #Hamiltonian cycles (mod 2)`. With the isolation lemma's random
  edge weights (the weighted count, paper form only) the decision follows;
  `hamcycle_weighted_decision` is that decision by enumeration.

`crossover_table` tabulates `n / (log₂ c · √ln n)` (the paper exponent with
constant 1) and `ρ(n) / log₂ c` (the verified exponent, constant 1) for
`c = 2, 3, 4`: the pathwidth above which `c^{pw}` exceeds the counting bound.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

from learning.subexp_chain import count_models as _count_models_mentioned
from learning.subexp_reductions import atlas

OUT = Path("reports/scratch/subexp_pathwidth/06_crossover")


def count_models(clauses, nvars: int, limit: int = 10 ** 6) -> int:
    """Exact model count over variables `1..nvars`: CaDiCaL with a blocking
    clause over every variable the clauses mention (`learning.subexp_chain`),
    times `2^(unmentioned)` for the variables above the highest one mentioned
    (an edgeless graph's independent-set formula has no clause at all)."""
    top = max((abs(l) for c in clauses for l in c), default=0)
    if any(len(c) == 0 for c in clauses):
        return 0
    base = _count_models_mentioned(clauses, top, limit) if top else 1
    return base * 2 ** (nvars - top)


def bits(x: int):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def popcount(x: int) -> int:
    return bin(x).count("1")


def edges_of(g):
    n, adj = g
    return [(u, w) for u in range(n) for w in bits(adj[u]) if u < w]


# ----------------------------------------------------------------------------
# a Tseitin circuit builder
# ----------------------------------------------------------------------------


class Builder:
    """Clauses over variables `1..nvars`; `fresh()` allocates. `TRUE` is a
    variable fixed by a unit clause, so constants are determined too and the
    count is preserved."""

    def __init__(self, nvars: int = 0):
        self.nvars = nvars
        self.clauses: list[list[int]] = []
        self._true = None

    def fresh(self) -> int:
        self.nvars += 1
        return self.nvars

    @property
    def TRUE(self) -> int:
        if self._true is None:
            self._true = self.fresh()
            self.clauses.append([self._true])
        return self._true

    @property
    def FALSE(self) -> int:
        return -self.TRUE

    def add(self, clause):
        self.clauses.append(list(clause))

    def xor(self, a: int, b: int) -> int:
        z = self.fresh()
        self.add([-a, -b, -z]); self.add([a, b, -z]); self.add([a, -b, z]); self.add([-a, b, z])
        return z

    def and_(self, a: int, b: int) -> int:
        z = self.fresh()
        self.add([-a, -b, z]); self.add([a, -z]); self.add([b, -z])
        return z

    def or_(self, a: int, b: int) -> int:
        z = self.fresh()
        self.add([a, b, -z]); self.add([-a, z]); self.add([-b, z])
        return z

    def or_many(self, lits) -> int:
        """OR of a list as a chain of binary ORs: `len − 1` auxiliaries."""
        lits = list(lits)
        if not lits:
            return self.FALSE
        acc = lits[0]
        for l in lits[1:]:
            acc = self.or_(acc, l)
        return acc

    def full_adder(self, a: int, b: int, c: int):
        t = self.xor(a, b)
        s = self.xor(t, c)
        carry = self.or_(self.and_(a, b), self.and_(t, c))
        return s, carry

    def add_numbers(self, A: list[int], B: list[int]) -> list[int]:
        """Ripple-carry sum of two little-endian bit lists."""
        L = max(len(A), len(B))
        out, carry = [], None
        for i in range(L):
            a = A[i] if i < len(A) else self.FALSE
            b = B[i] if i < len(B) else self.FALSE
            if carry is None:
                s = self.xor(a, b)
                carry = self.and_(a, b)
            else:
                s, carry = self.full_adder(a, b, carry)
            out.append(s)
        out.append(carry)
        return out

    def popcount_circuit(self, lits) -> list[int]:
        """The binary adder tree: the number of true literals as a
        little-endian bit list. Total size `O(len)`: level `j` has `len / 2^j`
        adders of `j + 1` bits."""
        nums = [[l] for l in lits]
        if not nums:
            return [self.FALSE]
        while len(nums) > 1:
            nxt = [self.add_numbers(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
            if len(nums) % 2:
                nxt.append(nums[-1])
            nums = nxt
        return nums[0]

    def ge_const(self, num: list[int], t: int) -> int:
        """A literal true iff the little-endian number `num` is `≥ t`."""
        L = max(len(num), t.bit_length())
        ge = self.TRUE
        for i in range(L):
            b = num[i] if i < len(num) else self.FALSE
            ge = self.and_(b, ge) if (t >> i) & 1 else self.or_(b, ge)
        return ge

    def at_least(self, lits, t: int) -> None:
        lits = list(lits)
        if t <= 0:
            return
        self.add([self.ge_const(self.popcount_circuit(lits), t)])

    def at_most(self, lits, t: int) -> None:
        lits = list(lits)
        self.at_least([-l for l in lits], len(lits) - t)


# ----------------------------------------------------------------------------
# the encodings
# ----------------------------------------------------------------------------


def indep_cnf(g):
    n, adj = g
    return [[-(u + 1), -(w + 1)] for u, w in edges_of(g)], n


def indep_atleast_cnf(g, t: int):
    n, adj = g
    b = Builder(n)
    for c, _ in [indep_cnf(g)]:
        for cl in c:
            b.add(cl)
    b.at_least(range(1, n + 1), t)
    return b.clauses, b.nvars


def coloring_cnf(g, q: int):
    n, adj = g

    def x(v, c):
        return v * q + c + 1

    clauses = []
    for v in range(n):
        clauses.append([x(v, c) for c in range(q)])
        for c1 in range(q):
            for c2 in range(c1 + 1, q):
                clauses.append([-x(v, c1), -x(v, c2)])
    for u, w in edges_of(g):
        for c in range(q):
            clauses.append([-x(u, c), -x(w, c)])
    return clauses, n * q


def domset_cnf(g, tseitin: bool = False):
    n, adj = g
    if not tseitin:
        return [[v + 1] + [u + 1 for u in bits(adj[v])] for v in range(n)], n
    b = Builder(n)
    for v in range(n):
        b.add([b.or_many([v + 1] + [u + 1 for u in bits(adj[v])])])
    return b.clauses, b.nvars


def domset_atmost_cnf(g, t: int):
    n, adj = g
    b = Builder(n)
    for v in range(n):
        b.add([b.or_many([v + 1] + [u + 1 for u in bits(adj[v])])])
    b.at_most(range(1, n + 1), t)
    return b.clauses, b.nvars


def maxcut_cnf(g, t: int):
    n, adj = g
    b = Builder(n)
    cut = [b.xor(u + 1, w + 1) for u, w in edges_of(g)]
    b.at_least(cut, t)
    return b.clauses, b.nvars


def oct_cnf(g, t: int):
    """Odd cycle transversal `≤ t`: a deletion bit `d_v` and a side bit `c_v`
    per vertex; per edge `uw` the two clauses `d_u ∨ d_w ∨ c_u ∨ c_w` and
    `d_u ∨ d_w ∨ ¬c_u ∨ ¬c_w` (width 4), and `Σ d_v ≤ t`. Satisfiable iff some
    `≤ t` vertices leave a bipartite graph; the count is `Σ_D 2^{|D|} 2^{cc(G − D)}`
    (the side bits of deleted vertices are free), not the number of
    transversals (decision only)."""
    n, adj = g
    b = Builder(2 * n)
    d = [v + 1 for v in range(n)]
    c = [n + v + 1 for v in range(n)]
    for u, w in edges_of(g):
        b.add([d[u], d[w], c[u], c[w]])
        b.add([d[u], d[w], -c[u], -c[w]])
    b.at_most(d, t)
    return b.clauses, b.nvars


def hamcycle_cutcount_cnf(g):
    """Variables `1..m` the edges (in `edges_of` order), `m+1..m+n` the sides."""
    n, adj = g
    E = edges_of(g)
    m = len(E)
    b = Builder(m + n)
    side = [m + v + 1 for v in range(n)]
    inc = {v: [] for v in range(n)}
    for i, (u, w) in enumerate(E):
        inc[u].append(i + 1)
        inc[w].append(i + 1)
    for v in range(n):
        b.at_least(inc[v], 2)
        b.at_most(inc[v], 2)
    for i, (u, w) in enumerate(E):
        e = i + 1
        b.add([-e, -side[u], side[w]])
        b.add([-e, side[u], -side[w]])
    if n:
        b.add([-side[0]])
    return b.clauses, b.nvars


# ----------------------------------------------------------------------------
# ground truth, by enumeration that shares nothing with the encodings
# ----------------------------------------------------------------------------


def independent_sets(g):
    n, adj = g
    return [S for S in range(1 << n) if all(adj[v] & S == 0 for v in bits(S))]


def dominating_sets(g):
    n, adj = g
    full = (1 << n) - 1
    out = []
    for S in range(1 << n):
        N = S
        for v in bits(S):
            N |= adj[v]
        if N == full:
            out.append(S)
    return out


def proper_colorings(g, q: int) -> int:
    n, adj = g
    E = edges_of(g)
    return sum(1 for col in itertools.product(range(q), repeat=n)
               if all(col[u] != col[w] for u, w in E))


def cut_sizes(g):
    n, adj = g
    E = edges_of(g)
    return [sum(1 for u, w in E if (S >> u) & 1 != (S >> w) & 1) for S in range(1 << n)]


def is_bipartite_after_deleting(g, D: int) -> bool:
    n, adj = g
    colour = {}
    for s in range(n):
        if (D >> s) & 1 or s in colour:
            continue
        colour[s] = 0
        stack = [s]
        while stack:
            a = stack.pop()
            for b_ in bits(adj[a] & ~D):
                if b_ not in colour:
                    colour[b_] = 1 - colour[a]
                    stack.append(b_)
                elif colour[b_] == colour[a]:
                    return False
    return True


def odd_cycle_transversal(g) -> int:
    n, adj = g
    return min(popcount(D) for D in range(1 << n) if is_bipartite_after_deleting(g, D))


def hamiltonian_cycles(g) -> int:
    """Hamiltonian cycles as edge sets: closed tours from vertex 0, divided
    by 2 (the two directions)."""
    n, adj = g
    if n < 3:
        return 0
    cnt = 0
    for perm in itertools.permutations(range(1, n)):
        tour = (0,) + perm
        if all((adj[tour[i]] >> tour[(i + 1) % n]) & 1 for i in range(n)):
            cnt += 1
    return cnt // 2


def two_factors(g):
    """Every 2-regular spanning subgraph as an edge subset, with its number
    of components. Enumerates edge subsets: for `m ≤ 16` only."""
    n, adj = g
    E = edges_of(g)
    m = len(E)
    out = []
    for X in range(1 << m):
        deg = [0] * n
        for i in bits(X):
            u, w = E[i]
            deg[u] += 1
            deg[w] += 1
        if any(d != 2 for d in deg):
            continue
        # components
        seen, cc = 0, 0
        nb = [0] * n
        for i in bits(X):
            u, w = E[i]
            nb[u] |= 1 << w
            nb[w] |= 1 << u
        for v in range(n):
            if (seen >> v) & 1:
                continue
            cc += 1
            stack = [v]
            seen |= 1 << v
            while stack:
                a = stack.pop()
                for c in bits(nb[a] & ~seen):
                    seen |= 1 << c
                    stack.append(c)
        out.append((X, cc))
    return out


def hamcycle_weighted_decision(g, weights: list[int], limit: int = 10 ** 6):
    """The Cut & Count decision with the given edge weights, by enumerating
    the models of `hamcycle_cutcount_cnf`: the coefficient of `y^w` in
    `Σ_X 2^{cc(X) − 1} y^{w(X)}` for each `w`; the answer is "yes" iff some
    coefficient is odd. Sound always; complete with probability `≥ 1/2` under
    the isolation lemma's weights (Cygan et al. 2011, Lemma 2.1 / Theorem 1).
    Returns `(decision, coefficients)`."""
    from pysat.solvers import Solver
    clauses, nvars = hamcycle_cutcount_cnf(g)
    m = len(edges_of(g))
    coef: dict[int, int] = {}
    cnt = 0
    with Solver(name="cadical195", bootstrap_with=clauses) as s:
        while s.solve():
            cnt += 1
            if cnt > limit:
                raise RuntimeError("model limit")
            model = s.get_model()
            X = [i for i in range(m) if model[i] > 0]
            w = sum(weights[i] for i in X)
            coef[w] = coef.get(w, 0) + 1
            s.add_clause([-l for l in model[:nvars]])
    return any(c % 2 for c in coef.values()), coef


# ----------------------------------------------------------------------------
# sizes and the crossover table
# ----------------------------------------------------------------------------


def cnf_size(clauses, nvars: int) -> dict:
    return {"variables": nvars, "clauses": len(clauses),
            "incidence": sum(len(c) for c in clauses),
            "width": max((len(c) for c in clauses), default=0)}


def threshold_aux_ratio(nmax: int = 200) -> dict:
    """Auxiliary variables of `Σ_{i ≤ n} x_i ≥ t` per input, over all `n ≤ nmax`
    and `t ∈ {1, ⌈n/2⌉, n}`: the constant in `O(n)`."""
    worst = 0.0
    rows = {}
    for n in range(1, nmax + 1):
        for t in {1, (n + 1) // 2, n}:
            b = Builder(n)
            b.at_least(range(1, n + 1), t)
            aux = b.nvars - n
            worst = max(worst, aux / n)
            if n in (1, 2, 4, 8, 16, 32, 64, 128, 200) and t == n:
                rows[n] = {"aux": aux, "clauses": len(b.clauses), "width": max(len(c) for c in b.clauses)}
    return {"max_aux_per_input": worst, "rows": rows}


def rho(n: float) -> float:
    """The verified runtime scale `n (log log(n + 16))² / √log(n + 16)`."""
    return n * math.log(math.log(n + 16)) ** 2 / math.sqrt(math.log(n + 16))


def crossover_table(cs=(2, 3, 4), exps=(2, 3, 4, 5, 6)) -> list[dict]:
    """For each `c` and `n = 10^e`: the pathwidth `pw*` with `c^{pw*} = 2^{E(n)}`,
    `E` the paper exponent `n / √ln n` and the verified `ρ(n)`, both with
    constant 1; `pw* = E(n) / log₂ c`; and `pw* / n`."""
    rows = []
    for c in cs:
        for e in exps:
            n = 10 ** e
            paper = n / math.sqrt(math.log(n))
            ver = rho(n)
            rows.append({"c": c, "n": n,
                         "paper_exponent": paper, "paper_pw_star": paper / math.log2(c),
                         "paper_ratio": paper / math.log2(c) / n,
                         "verified_exponent": ver, "verified_pw_star": ver / math.log2(c),
                         "verified_ratio": ver / math.log2(c) / n})
    return rows


def format_table(rows) -> str:
    lines = ["| c | n | paper: pw* = n/(log₂c √ln n) | pw*/n | verified: pw* = ρ(n)/log₂c | pw*/n |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['c']} | 10^{int(math.log10(r['n']))} | {r['paper_pw_star']:,.0f} | "
                     f"{r['paper_ratio']:.3f} | {r['verified_pw_star']:,.0f} | {r['verified_ratio']:.3f} |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------


def run_checks(nmax: int = 7, out_dir: Path = OUT, log=print, qs=(2, 3), q4_nmax: int = 6,
               twofactor_mmax: int = 15, seed: int = 0) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    t0 = time.time()
    graphs = atlas(nmax)
    log(f"atlas to {nmax} vertices: {len(graphs)} graphs")
    res = {"nmax": nmax, "graphs": len(graphs), "failures": [], "checks": {}}
    fails = res["failures"]
    C = {k: 0 for k in ["indep_count", "indep_width", "indep_size",
                        "indep_atleast_count", "indep_atleast_sat", "indep_atleast_width",
                        "coloring_count", "coloring_width", "coloring_size",
                        "domset_count", "domset_width", "domset_tseitin_count", "domset_tseitin_width",
                        "domset_atmost_sat", "maxcut_sat", "maxcut_count", "maxcut_width",
                        "oct_sat", "oct_width",
                        "ham_parity", "ham_count_2factors", "ham_weighted_sound", "ham_width",
                        "ham_size"]}
    sizes = {"indep": [], "indep_atleast": [], "coloring3": [], "domset_tseitin": [], "maxcut": [], "ham": []}
    ham_complete = [0, 0]
    for gi, g in enumerate(graphs):
        n, adj = g
        E = edges_of(g)
        m = len(E)

        # independent sets
        cl, nv = indep_cnf(g)
        IS = independent_sets(g)
        sz = cnf_size(cl, nv)
        if count_models(cl, nv) != len(IS):
            fails.append(("indep_count", gi))
        C["indep_count"] += 1
        if sz["width"] > 2:
            fails.append(("indep_width", gi))
        C["indep_width"] += 1
        if not (nv == n and sz["clauses"] == m):
            fails.append(("indep_size", gi))
        C["indep_size"] += 1
        sizes["indep"].append((n, m, nv, sz["clauses"]))
        alpha = max(popcount(S) for S in IS)
        for t in range(n + 2):
            cl, nv = indep_atleast_cnf(g, t)
            cnt = count_models(cl, nv)
            if cnt != sum(1 for S in IS if popcount(S) >= t):
                fails.append(("indep_atleast_count", gi, t))
            C["indep_atleast_count"] += 1
            if (cnt > 0) != (alpha >= t):
                fails.append(("indep_atleast_sat", gi, t))
            C["indep_atleast_sat"] += 1
            sz = cnf_size(cl, nv)
            if sz["width"] > 3:
                fails.append(("indep_atleast_width", gi, t))
            C["indep_atleast_width"] += 1
            if t == (n + 1) // 2:
                sizes["indep_atleast"].append((n, m, nv, sz["clauses"]))

        # colourings
        for q in list(qs) + ([4] if n <= q4_nmax else []):
            cl, nv = coloring_cnf(g, q)
            if count_models(cl, nv) != proper_colorings(g, q):
                fails.append(("coloring_count", gi, q))
            C["coloring_count"] += 1
            sz = cnf_size(cl, nv)
            if sz["width"] > max(q, 2):
                fails.append(("coloring_width", gi, q))
            C["coloring_width"] += 1
            if not (nv == n * q and sz["clauses"] == n + n * q * (q - 1) // 2 + q * m):
                fails.append(("coloring_size", gi, q))
            C["coloring_size"] += 1
            if q == 3:
                sizes["coloring3"].append((n, m, nv, sz["clauses"]))

        # dominating sets
        DS = dominating_sets(g)
        gamma = min(popcount(S) for S in DS)
        Delta = max((popcount(a) for a in adj), default=0)
        cl, nv = domset_cnf(g)
        if count_models(cl, nv) != len(DS):
            fails.append(("domset_count", gi))
        C["domset_count"] += 1
        if cnf_size(cl, nv)["width"] != Delta + 1:
            fails.append(("domset_width", gi))
        C["domset_width"] += 1
        cl, nv = domset_cnf(g, tseitin=True)
        if count_models(cl, nv) != len(DS):
            fails.append(("domset_tseitin_count", gi))
        C["domset_tseitin_count"] += 1
        sz = cnf_size(cl, nv)
        if sz["width"] > 3 or nv > n + 2 * m + 1:
            fails.append(("domset_tseitin_width", gi))
        C["domset_tseitin_width"] += 1
        sizes["domset_tseitin"].append((n, m, nv, sz["clauses"]))
        for t in range(n + 1):
            cl, nv = domset_atmost_cnf(g, t)
            if (count_models(cl, nv) > 0) != (gamma <= t):
                fails.append(("domset_atmost_sat", gi, t))
            C["domset_atmost_sat"] += 1

        # max cut
        cuts = cut_sizes(g)
        mc = max(cuts)
        for t in range(m + 2):
            cl, nv = maxcut_cnf(g, t)
            cnt = count_models(cl, nv)
            if (cnt > 0) != (mc >= t):
                fails.append(("maxcut_sat", gi, t))
            C["maxcut_sat"] += 1
            if cnt != sum(1 for c in cuts if c >= t):
                fails.append(("maxcut_count", gi, t))
            C["maxcut_count"] += 1
            sz = cnf_size(cl, nv)
            if sz["width"] > 3:
                fails.append(("maxcut_width", gi, t))
            C["maxcut_width"] += 1
            if t == (m + 1) // 2:
                sizes["maxcut"].append((n, m, nv, sz["clauses"]))

        # odd cycle transversal (decision only)
        oc = odd_cycle_transversal(g)
        for t in range(n + 1):
            cl, nv = oct_cnf(g, t)
            if (count_models(cl, nv) > 0) != (oc <= t):
                fails.append(("oct_sat", gi, t))
            C["oct_sat"] += 1
            if cnf_size(cl, nv)["width"] > 4:
                fails.append(("oct_width", gi, t))
            C["oct_width"] += 1

        # Hamiltonian cycles: Cut & Count as a count
        if n >= 3:
            cl, nv = hamcycle_cutcount_cnf(g)
            cnt = count_models(cl, nv)
            hc = hamiltonian_cycles(g)
            if cnt % 2 != hc % 2:
                fails.append(("ham_parity", gi))
            C["ham_parity"] += 1
            sz = cnf_size(cl, nv)
            if sz["width"] > 3:
                fails.append(("ham_width", gi))
            C["ham_width"] += 1
            if nv > 20 * (n + m) + 1:
                fails.append(("ham_size", gi))
            C["ham_size"] += 1
            sizes["ham"].append((n, m, nv, sz["clauses"]))
            if m <= twofactor_mmax:
                tf = two_factors(g)
                if cnt != sum(2 ** (cc - 1) for _, cc in tf):
                    fails.append(("ham_count_2factors", gi))
                C["ham_count_2factors"] += 1
            weights = [rng.randint(1, 2 * m) for _ in range(m)]
            dec, _ = hamcycle_weighted_decision(g, weights)
            if dec and hc == 0:
                fails.append(("ham_weighted_sound", gi))
            C["ham_weighted_sound"] += 1
            if hc > 0:
                ham_complete[1] += 1
                ham_complete[0] += int(dec)

        if (gi + 1) % 200 == 0:
            log(f"  {gi + 1}/{len(graphs)} graphs, {len(fails)} failures, {time.time() - t0:.1f} s")

    res["checks"] = C
    res["ham_weighted_complete"] = {"decided_yes": ham_complete[0], "with_cycle": ham_complete[1]}
    # linear size bounds, as measured constants
    lin = {}
    for key, rows in sizes.items():
        if rows:
            lin[key] = {"max_vars_over_n_plus_m": max(v / (n + m) for n, m, v, c in rows),
                        "max_clauses_over_n_plus_m": max(c / (n + m) for n, m, v, c in rows)}
    res["size_constants"] = lin
    res["threshold_aux"] = threshold_aux_ratio()
    res["crossover_table"] = crossover_table()
    res["seconds"] = time.time() - t0
    log(f"checks: {sum(C.values())} evaluations, {len(fails)} failures, {res['seconds']:.1f} s")
    for k, v in C.items():
        log(f"  {k}: {v}")
    log(f"Cut & Count weighted decision: yes on {ham_complete[0]} of {ham_complete[1]} graphs with a cycle"
        f" (sound on all: {C['ham_weighted_sound']} checked)")
    log("size constants: " + json.dumps(lin))
    log(f"threshold auxiliaries per input, n ≤ 200: ≤ {res['threshold_aux']['max_aux_per_input']:.2f}")
    log(format_table(res["crossover_table"]))
    if fails:
        log("FAILURES: " + str(fails[:20]))
    (out_dir / "check.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=7)
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    if a.table:
        print(format_table(crossover_table()))
        return
    res = run_checks(a.nmax, a.out)
    sys.exit(1 if res["failures"] else 0)


if __name__ == "__main__":
    main()
