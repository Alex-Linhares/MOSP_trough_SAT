"""The chain count as an algebraic object (loop0014 item 05,
`reports/subexp_pathwidth.md` §5).

"`vs(G) ≤ k`" is reachability from `∅` to `V` by single additions inside the
lattice `L_k = {S ⊆ V : |N(S) ∖ S| ≤ k}` (`reports/checkpoint_relaxation.md`
§10, with the MOSP offset removed: outer boundary `≤ k` is vertex separation
`≤ k`, by the reversal bijection between prefix chains and suffix chains).
The **chain count** is

    C_k(G) = Σ_σ Π_{t=1}^{n−1} [S_t(σ) ∈ L_k]   = #{maximal chains ∅ ⊂ S_1 ⊂ … ⊂ V in L_k},

the number of layouts of vertex separation `≤ k`; the decision is `C_k > 0`.
This module computes it three independent ways and writes the objects §5
reasons about:

- `chain_count_dp` (layered path count over subsets, outer or inner
  boundary) and `chain_count_perm` (the literal sum over
  `itertools.permutations`, to 7 vertices): the count, cross-checked, and
  `C_k > 0 ⟺ vs(G) ≤ k` against the item-03 evaluators.
- `membership_polynomial`: the unique multilinear polynomial over `Q` (and
  its reduction mod 2) of the indicator `S ↦ [S ∈ L_k]` in the `n` set
  variables, by Möbius inversion on the subset lattice; its degree and its
  number of monomials — the "threshold constraint as a polynomial" the item
  asks for. `boundary_bit_polynomial` does the same for one vertex's
  boundary indicator `b_u(S) = [u ∉ S ∧ N(u) ∩ S ≠ ∅]` (degree `deg(u) + 1`,
  `2^{deg(u)+1} − 2` monomials), and `threshold_top_coefficient` checks the
  top coefficient `(−1)^{n−k} C(n−1, k)` of the bare threshold.
- `nested_chain_cnf`: the nested-chain / position encoding of the chain as a
  CNF whose auxiliary variables are all functionally determined (bidirectional
  OR and a bidirectional sequential counter), so that **its model count is
  `C_k(G)`** — the chain count *is* the number of solutions of a sparse
  system, in `Θ(n²)` variables. `count_models` enumerates the models with
  CaDiCaL and blocking clauses; `cnf_size` returns variables, clauses and
  incidence (total literal occurrences) and `cnf_size_formula` the closed
  forms at any `(n, m, k)`.
- `rank_formulation_count`: the same count from ranks (one integer per
  vertex, `n ⌈log₂ n⌉` bits) with the cut at `t` as an *interval* count
  (`v` active at `t` iff `pos(v) ≤ t < max_{w ∈ N[v]} pos(w)`), the
  interval-thickness form of the cut: `o(n²)` variables, `n` constraints of
  width `n ⌈log₂ n⌉`.
- `inclusion_exclusion_count`: `C_k = Σ_S (−1)^{n−|S|} W_k(S)`, `W_k(S)` the
  sequences in `S^n` (repetition allowed) whose prefix *supports* lie in
  `L_k`; checked, and the point is that `W_k(S)` is itself a sum over the
  lattice below `S` (its DP state is the support), unlike the walk count that
  makes the Hamiltonian-path sieve run over the `n`-cube.
- `split_rank`: for a vertex bipartition `A | B`, the rank over `Q` of the
  matrix `M[S_A, S_B] = [S_A ∪ S_B ∈ L_k]`; `log₂ rank` is a lower bound on
  the number of wires any tensor network computing the membership indicator
  must carry across a cut separating the `A` variables from the `B`
  variables; measured over every balanced split.
- `exact_count_table`: `log₂ n!` against `n` and against the verified
  budget `n (log log n)² / √log n` of §1.3.8 — the bits any 0/1 system whose
  solution count *equals* `C_k` needs on `K_n`.

    python -m learning.subexp_chain              # the full check, atlas to 7
    python -m learning.subexp_chain --nmax 5     # quick

Graphs are `(n, adj)` as in `paper1/complex_check.py`.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

from learning.subexp_reductions import atlas, vs
from paper1.complex_check import edges_of, vertex_separation

OUT = Path("reports/scratch/subexp_pathwidth/05_chain")


# ----------------------------------------------------------------------------
# the lattice and the chain count
# ----------------------------------------------------------------------------


def popcount(x: int) -> int:
    return bin(x).count("1")


def outer_boundary(adj, S: int) -> int:
    """`N(S) ∖ S` as a mask."""
    N = 0
    bits = S
    while bits:
        b = bits & -bits
        bits ^= b
        N |= adj[b.bit_length() - 1]
    return N & ~S


def inner_boundary(adj, S: int) -> int:
    """`{v ∈ S : N(v) ⊄ S}` as a mask (Kinnersley's cut)."""
    out = 0
    bits = S
    while bits:
        b = bits & -bits
        bits ^= b
        if adj[b.bit_length() - 1] & ~S:
            out |= b
    return out


def member(adj, S: int, k: int, inner: bool = False) -> bool:
    return popcount((inner_boundary if inner else outer_boundary)(adj, S)) <= k


def lattice(adj, k: int, inner: bool = False) -> list[int]:
    n = len(adj)
    return [S for S in range(1 << n) if member(adj, S, k, inner)]


def chain_count_dp(adj, k: int, inner: bool = False) -> int:
    """`C_k(G)`: the number of maximal chains `∅ ⊂ S_1 ⊂ … ⊂ V` in `L_k`, by
    a layered path count (every subset's chain count is the sum over its
    members' predecessors). `inner=True` uses Kinnersley's cut instead of
    the outer boundary; the two counts are equal (reversal)."""
    n = len(adj)
    full = (1 << n) - 1
    counts = {0: 1}
    for _ in range(n):
        nxt: dict[int, int] = {}
        for S, c in counts.items():
            bits = full & ~S
            while bits:
                b = bits & -bits
                bits ^= b
                S2 = S | b
                if S2 == full or member(adj, S2, k, inner):
                    nxt[S2] = nxt.get(S2, 0) + c
        counts = nxt
        if not counts:
            return 0
    return counts.get(full, 0)


def chain_count_perm(adj, k: int) -> int:
    """The literal sum over orderings of the product of prefix memberships."""
    n = len(adj)
    total = 0
    for p in itertools.permutations(range(n)):
        S = 0
        ok = True
        for t in range(n - 1):
            S |= 1 << p[t]
            if popcount(outer_boundary(adj, S)) > k:
                ok = False
                break
        total += ok
    return total


def layout_count_vs(adj, k: int) -> int:
    """Layouts of vertex separation `≤ k`, by Kinnersley's definition on each
    permutation (shares only `itertools` with the chain count)."""
    n = len(adj)
    g = (n, tuple(adj))
    from paper1.complex_check import vs_of_layout
    return sum(1 for p in itertools.permutations(range(n)) if vs_of_layout(g, p) <= k)


# ----------------------------------------------------------------------------
# the membership indicator as a polynomial
# ----------------------------------------------------------------------------


def moebius(values: np.ndarray, n: int) -> np.ndarray:
    """Coefficients of the multilinear polynomial with the given truth table:
    `c_T = Σ_{S ⊆ T} (−1)^{|T ∖ S|} f(S)` (the subset Möbius transform)."""
    c = values.astype(np.int64).copy()
    for i in range(n):
        bit = 1 << i
        idx = np.arange(1 << n)
        hi = idx[(idx & bit) != 0]
        c[hi] -= c[hi ^ bit]
    return c


def membership_polynomial(adj, k: int, inner: bool = False) -> dict:
    """Degree and monomial count over `Q` and over `GF(2)` of the indicator of
    `L_k` as a multilinear polynomial in the `n` set variables."""
    n = len(adj)
    f = np.fromiter((member(adj, S, k, inner) for S in range(1 << n)), dtype=np.int64, count=1 << n)
    c = moebius(f, n)
    pc = np.fromiter((popcount(T) for T in range(1 << n)), dtype=np.int64, count=1 << n)
    nz = c != 0
    nz2 = (c % 2) != 0
    idx = np.arange(1 << n)
    essential = sum(1 for v in range(n) if (f != f[idx ^ (1 << v)]).any())
    return {"degree_Q": int(pc[nz].max()) if nz.any() else -1,
            "monomials_Q": int(nz.sum()),
            "degree_GF2": int(pc[nz2].max()) if nz2.any() else -1,
            "monomials_GF2": int(nz2.sum()),
            "top_coefficient": int(c[(1 << n) - 1]),
            "essential": int(essential),
            "members": int(f.sum())}


def boundary_bit_polynomial(adj, u: int) -> dict:
    """The multilinear polynomial of `b_u(S) = [u ∉ S ∧ N(u) ∩ S ≠ ∅]`."""
    n = len(adj)
    f = np.fromiter((((S >> u) & 1) == 0 and (adj[u] & S) != 0 for S in range(1 << n)),
                    dtype=np.int64, count=1 << n)
    c = moebius(f, n)
    pc = np.fromiter((popcount(T) for T in range(1 << n)), dtype=np.int64, count=1 << n)
    nz = c != 0
    return {"degree": int(pc[nz].max()) if nz.any() else -1, "monomials": int(nz.sum()),
            "deg_u": popcount(adj[u])}


def threshold_top_coefficient(n: int, k: int) -> int:
    """The coefficient of `x_1 ⋯ x_n` in the multilinear polynomial of
    `[Σ x_i ≤ k]`: `Σ_{i ≤ k} (−1)^{n−i} C(n, i)`."""
    return sum((-1) ** (n - i) * math.comb(n, i) for i in range(0, k + 1))


# ----------------------------------------------------------------------------
# the nested-chain / position CNF with determined auxiliaries
# ----------------------------------------------------------------------------


class _Pool:
    def __init__(self):
        self.top = 0
        self.names: dict = {}

    def new(self, name=None) -> int:
        self.top += 1
        if name is not None:
            self.names[name] = self.top
        return self.top


def _seq_counter(pool: _Pool, clauses: list, xs: list[int], bound: int, tag) -> list[int]:
    """Bidirectional sequential counter: returns `s[j]`, `j = 1..bound+1`,
    with `s[j] ↔ (at least j of xs are true)` for `j ≤ bound + 1` — every
    auxiliary is a function of `xs`. `r[i][j]` = at least `j` among the first
    `i` inputs: `r[i][j] ↔ r[i−1][j] ∨ (x_i ∧ r[i−1][j−1])`."""
    J = bound + 1
    prev = [None] * (J + 1)       # prev[0] is "true"
    for i, x in enumerate(xs):
        cur = [None] * (J + 1)
        for j in range(1, J + 1):
            if j > i + 1:
                cur[j] = None     # cannot have j among i+1 inputs: false
                continue
            r = pool.new((tag, i, j))
            cur[j] = r
            a = prev[j]           # may be None (false)
            b = prev[j - 1]       # None means true when j-1 == 0
            # r ↔ a ∨ (x ∧ b)
            if j - 1 == 0:
                # r ↔ a ∨ x
                if a is None:
                    clauses += [[-r, x], [-x, r]]
                else:
                    clauses += [[-r, a, x], [-a, r], [-x, r]]
            else:
                if a is None and b is None:
                    clauses += [[-r]]
                elif a is None:
                    clauses += [[-r, x], [-r, b], [-x, -b, r]]
                elif b is None:
                    clauses += [[-r, a], [-a, r]]
                else:
                    clauses += [[-r, a, x], [-r, a, b], [-a, r], [-x, -b, r]]
        prev = cur
    return prev


def nested_chain_cnf(adj, k: int) -> tuple[list[list[int]], _Pool]:
    """The chain `∅ ⊂ S_1 ⊂ … ⊂ S_{n−1} ⊂ V` as a CNF: `y[v,t]` (`v ∈ S_t`,
    `1 ≤ t ≤ n−1`), nested, exactly one vertex new at each step (a pairwise
    exactly-one on `x[v,t] = y[v,t] ∧ ¬y[v,t−1]`), the boundary bit
    `b[u,t] ↔ ¬y[u,t] ∧ o[u,t]`, `o[u,t] ↔ ∨_{w ∈ N(u)} y[w,t]`, and
    `Σ_u b[u,t] ≤ k` by a bidirectional counter. Every variable other than the
    `y` is a function of the `y`, so the models are exactly the chains."""
    n = len(adj)
    pool = _Pool()
    cl: list[list[int]] = []
    y = [[None] * (n + 1) for _ in range(n)]
    for t in range(1, n):
        for v in range(n):
            y[v][t] = pool.new(("y", v, t))
    for t in range(1, n):
        prev_t = t - 1
        xs = []
        for v in range(n):
            x = pool.new(("x", v, t))
            xs.append(x)
            if prev_t == 0:
                cl += [[-x, y[v][t]], [-y[v][t], x]]
            else:
                # nested
                cl += [[-y[v][prev_t], y[v][t]]]
                # x ↔ y_t ∧ ¬y_{t−1}
                cl += [[-x, y[v][t]], [-x, -y[v][prev_t]], [-y[v][t], y[v][prev_t], x]]
        cl.append(list(xs))                              # at least one new
        for a, b in itertools.combinations(xs, 2):       # at most one new
            cl.append([-a, -b])
        bs = []
        for u in range(n):
            o = pool.new(("o", u, t))
            nb = [y[w][t] for w in range(n) if adj[u] >> w & 1]
            cl.append([-o] + nb)
            for w in nb:
                cl.append([-w, o])
            b = pool.new(("b", u, t))
            cl += [[-b, -y[u][t]], [-b, o], [y[u][t], -o, b]]
            bs.append(b)
        s = _seq_counter(pool, cl, bs, k, ("c", t))
        if s[k + 1] is not None:
            cl.append([-s[k + 1]])
    return cl, pool


def cnf_size(clauses) -> dict:
    nv = max((abs(l) for c in clauses for l in c), default=0)
    return {"variables": nv, "clauses": len(clauses), "incidence": sum(len(c) for c in clauses)}


def count_models(clauses, nvars: int | None = None, limit: int = 10 ** 6) -> int:
    """Model count by CaDiCaL with a blocking clause over *all* variables."""
    from pysat.solvers import Solver
    if nvars is None:
        nvars = max((abs(l) for c in clauses for l in c), default=0)
    cnt = 0
    with Solver(name="cadical195", bootstrap_with=clauses) as s:
        while s.solve():
            cnt += 1
            if cnt > limit:
                raise RuntimeError("model limit")
            m = s.get_model()
            s.add_clause([-l for l in m[:nvars]])
    return cnt


def cnf_size_formula(n: int, degrees: list[int], k: int) -> dict:
    """Closed forms for `nested_chain_cnf` at `(n, degrees, k)` — counted the
    same way `cnf_size` counts, checked against it on the atlas."""
    m2 = sum(degrees)                     # 2m
    T = n - 1
    # y: n(n−1); x: n(n−1); o, b: n(n−1) each; counter: per level Σ_i min(i+1, k+1)
    counter_vars = sum(min(i + 1, k + 1) for i in range(n))
    variables = 4 * n * T + T * counter_vars
    # clauses per level
    clauses = 0
    inc = 0
    for t in range(1, n):
        if t == 1:
            clauses += 2 * n; inc += 4 * n            # x ↔ y
        else:
            clauses += 4 * n; inc += n * (2 + 2 + 2 + 3)   # nested + x ↔ y ∧ ¬y'
        clauses += 1 + n * (n - 1) // 2; inc += n + n * (n - 1)
        # o ↔ OR: 1 + deg clauses, (1+deg) + 2 deg literals; b ↔: 3 clauses, 7 literals
        clauses += sum(1 + d + 3 for d in degrees); inc += sum((1 + d) + 2 * d + 7 for d in degrees)
    # counter: count clauses by replaying the structure
    pool = _Pool(); cl: list = []
    xs = [pool.new() for _ in range(n)]
    s = _seq_counter(pool, cl, xs, k, "c")
    if s[k + 1] is not None:
        cl.append([-s[k + 1]])
    clauses += T * len(cl); inc += T * sum(len(c) for c in cl)
    return {"variables": variables, "clauses": clauses, "incidence": inc}


# ----------------------------------------------------------------------------
# ranks, intervals, inclusion–exclusion
# ----------------------------------------------------------------------------


def rank_formulation_count(adj, k: int) -> int:
    """Count rank tuples `r ∈ {0..n−1}^n` that are permutations and whose
    every cut `t` has at most `k` active vertices, `v` active at `t` iff
    `r_v ≤ t < max_{w ∈ N[v]} r_w` (the interval form of the cut)."""
    n = len(adj)
    total = 0
    for r in itertools.product(range(n), repeat=n):
        if len(set(r)) != n:
            continue
        ok = True
        last = [max(r[w] for w in range(n) if (adj[v] >> w & 1) or w == v) for v in range(n)]
        for t in range(n - 1):
            if sum(1 for v in range(n) if r[v] <= t < last[v]) > k:
                ok = False
                break
        total += ok
    return total


def sequences_count(adj, k: int, S: int) -> int:
    """`W_k(S)`: sequences in `S^n` all of whose prefix supports lie in `L_k`
    (`V` itself counts as a member), by a DP whose state is the support."""
    n = len(adj)
    full = (1 << n) - 1
    counts = {0: 1}
    for _ in range(n):
        nxt: dict[int, int] = {}
        for T, c in counts.items():
            bits = S
            while bits:
                b = bits & -bits
                bits ^= b
                T2 = T | b
                if T2 == T:
                    nxt[T2] = nxt.get(T2, 0) + c
                elif T2 == full or member(adj, T2, k):
                    nxt[T2] = nxt.get(T2, 0) + c
        counts = nxt
    return sum(counts.values())


def inclusion_exclusion_count(adj, k: int) -> int:
    n = len(adj)
    return sum((-1) ** (n - popcount(S)) * sequences_count(adj, k, S) for S in range(1 << n))


def split_rank(adj, k: int, A: int) -> int:
    """Rank over `Q` of `M[S_A, S_B] = [S_A ∪ S_B ∈ L_k]`."""
    n = len(adj)
    full = (1 << n) - 1
    B = full & ~A
    As = [S for S in range(1 << n) if S & ~A == 0]
    Bs = [S for S in range(1 << n) if S & ~B == 0]
    M = np.array([[1 if member(adj, a | b, k) else 0 for b in Bs] for a in As], dtype=float)
    return int(np.linalg.matrix_rank(M))


def balanced_splits(n: int):
    """Every unordered bipartition `{A, B}` with `|A| = ⌊n/2⌋`, once: for even
    `n` the two sides have equal size and `0 ∈ A` picks one of the two
    namings; for odd `n` every `⌊n/2⌋`-subset is a different partition (the
    first version kept `0 ∈ A` for odd `n` too and skipped 15 of the 35
    splits at `n = 7`; found by the refuter agent, 2026-11-04)."""
    a = n // 2
    for comb in itertools.combinations(range(n), a):
        if n % 2 == 1 or 0 in comb or a == 0:
            yield sum(1 << v for v in comb)


def split_rank_profile(adj, k: int) -> dict:
    n = len(adj)
    ranks = [split_rank(adj, k, A) for A in balanced_splits(n)]
    return {"min_rank": min(ranks), "max_rank": max(ranks), "splits": len(ranks),
            "min_log2": math.log2(min(ranks)) if min(ranks) > 0 else float("-inf"),
            "trivial_log2": n // 2}


def exact_count_table(ns=(4, 5, 6, 7, 8, 10, 16, 32, 64, 125, 10 ** 3, 10 ** 6)) -> list[dict]:
    """`log₂ n!` (the bits a 0/1 system with solution count `n!` needs)
    against `n` and the verified budget `B_v = n √log n / (log log n)²` on the
    variable count (§1.3.8; natural logs, constant 1, as in §4.6)."""
    rows = []
    for n in ns:
        L = math.log(n)
        Bv = n * math.sqrt(L) / (math.log(L)) ** 2 if n > 2 else float("nan")
        lf = math.lgamma(n + 1) / math.log(2)
        rows.append({"n": n, "log2_factorial": lf, "log2_factorial_over_n": lf / n,
                     "Bv": Bv, "Bv_over_n": Bv / n, "ranks_bits": n * math.ceil(math.log2(n))})
    return rows


# ----------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------


def run_checks(nmax: int = 7, out_dir: Path = OUT, log=print, perm_nmax: int = 7,
               cnf_nmax: int = 6, cnf_sample7: int = 30, ie_nmax: int = 6, ie_sample7: int = 30,
               rank_nmax: int = 6, rank_sample7: int = 40, split_nmax: int = 7,
               seed: int = 0) -> dict:
    import random
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    graphs = atlas(nmax)
    res: dict = {"nmax": nmax, "graphs": len(graphs)}
    fails: dict[str, list] = {k: [] for k in
                              ["dp_vs_perm", "inner_vs_outer", "positive_iff_vs", "layouts_vs",
                               "boundary_bit", "threshold_top", "cnf_count", "cnf_size_formula",
                               "ranks_count", "inclusion_exclusion", "Kn_factorial"]}
    counts: Counter = Counter()
    poly_rows = []
    rank_rows = []
    smallest_full = None

    for g in graphs:
        n, adj = g
        v = vs(g)
        vperm = vertex_separation(g)
        if v != vperm:
            fails["dp_vs_perm"].append((g, v, vperm))
        m = len(edges_of(g))
        degs = [popcount(a) for a in adj]
        for k in range(0, n):
            c = chain_count_dp(adj, k)
            counts["chain_counts"] += 1
            if n <= perm_nmax:
                cp = chain_count_perm(adj, k)
                if cp != c:
                    fails["dp_vs_perm"].append((g, k, c, cp))
                lv = layout_count_vs(adj, k)
                if lv != c:
                    fails["layouts_vs"].append((g, k, c, lv))
            ci = chain_count_dp(adj, k, inner=True)
            if ci != c:
                fails["inner_vs_outer"].append((g, k, c, ci))
            if (c > 0) != (v <= k):
                fails["positive_iff_vs"].append((g, k, c, v))
            # the membership polynomial
            p = membership_polynomial(adj, k)
            poly_rows.append({"n": n, "m": m, "k": k, "vs": v, "edges": edges_of(g), **p})
            if (n >= 3 and p["degree_Q"] == n and p["monomials_Q"] >= (1 << (n - 1))
                    and p["essential"] == n and k == v - 1 and k >= 1
                    and smallest_full is None and _connected(adj)):
                smallest_full = {"n": n, "edges": edges_of(g), "k": k, "vs": v, **p}
        # boundary bits
        for u in range(n):
            b = boundary_bit_polynomial(adj, u)
            counts["boundary_bits"] += 1
            d = degs[u]
            exp_deg = d + 1 if d >= 1 else -1
            exp_mon = (1 << (d + 1)) - 2 if d >= 1 else 0
            if b["degree"] != exp_deg or b["monomials"] != exp_mon:
                fails["boundary_bit"].append((g, u, b))
        # the CNF: model count = chain count, size formula
        if n <= cnf_nmax or (n == 7 and rng.random() < cnf_sample7 / 1044):
            for k in range(0, n):
                cl, pool = nested_chain_cnf(adj, k)
                c = chain_count_dp(adj, k)
                counts["cnf_counts"] += 1
                try:
                    mc = count_models(cl, pool.top, limit=max(10, 2 * c + 10))
                except RuntimeError:
                    mc = -1
                if mc != c:
                    fails["cnf_count"].append((g, k, c, mc))
                sz = cnf_size(cl)
                sz["variables"] = pool.top
                if sz != cnf_size_formula(n, degs, k):
                    fails["cnf_size_formula"].append((g, k, sz, cnf_size_formula(n, degs, k)))
        # ranks / interval form
        if n <= rank_nmax or (n == 7 and rng.random() < rank_sample7 / 1044):
            for k in range(0, n):
                counts["rank_counts"] += 1
                rc = rank_formulation_count(adj, k)
                if rc != chain_count_dp(adj, k):
                    fails["ranks_count"].append((g, k, rc))
        # inclusion–exclusion
        if n <= ie_nmax or (n == 7 and rng.random() < ie_sample7 / 1044):
            for k in range(0, n):
                counts["ie_counts"] += 1
                if inclusion_exclusion_count(adj, k) != chain_count_dp(adj, k):
                    fails["inclusion_exclusion"].append((g, k))
        # split ranks at k = vs − 1 and k = vs, connected graphs with n ≥ 4
        if n >= 4 and n <= split_nmax and _connected(adj):
            for k in (v - 1, v):
                if k < 0:
                    continue
                pr = split_rank_profile(adj, k)
                rank_rows.append({"n": n, "m": m, "k": k, "vs": v, "level": "vs-1" if k == v - 1 else "vs",
                                  "edges": edges_of(g), **pr})
    # the bare threshold's top coefficient and K_n's count
    for n in range(1, nmax + 1):
        for k in range(0, n):
            counts["threshold_top"] += 1
            f = np.fromiter((popcount(S) <= k for S in range(1 << n)), dtype=np.int64, count=1 << n)
            c = moebius(f, n)
            top = int(c[(1 << n) - 1])
            expect = (-1) ** (n - k) * math.comb(n - 1, k)
            if top != threshold_top_coefficient(n, k) or top != expect:
                fails["threshold_top"].append((n, k, top, expect))
        adj = tuple(((1 << n) - 1) & ~(1 << v) for v in range(n))
        for k in range(0, n):
            c = chain_count_dp(adj, k)
            expect = math.factorial(n) if k >= n - 1 else 0
            counts["Kn"] += 1
            if c != expect:
                fails["Kn_factorial"].append((n, k, c, expect))

    # summaries
    import pandas as pd
    P = pd.DataFrame(poly_rows)
    P.to_csv(out_dir / "membership_polynomial.csv", index=False)
    R = pd.DataFrame(rank_rows)
    R.to_csv(out_dir / "split_rank.csv", index=False)
    summary = {}
    for lvl in ("all", "vs-1", "vs"):
        sub = P if lvl == "all" else P[P.k == (P.vs - (1 if lvl == "vs-1" else 0))]
        sub = sub[sub.k >= 0]
        if len(sub):
            summary[lvl] = {
                "rows": int(len(sub)),
                "full_degree_Q": float((sub.degree_Q == sub.n).mean()),
                "full_degree_GF2": float((sub.degree_GF2 == sub.n).mean()),
                "median_monomial_fraction_Q": float((sub.monomials_Q / 2 ** sub.n).median()),
                "median_monomial_fraction_GF2": float((sub.monomials_GF2 / 2 ** sub.n).median()),
                "min_monomial_fraction_Q_n7": float((sub[sub.n == 7].monomials_Q / 128).min()) if (sub.n == 7).any() else None,
                "mean_degree_Q_over_n": float((sub.degree_Q / sub.n).mean()),
                "all_essential_connected": float(sub[sub.apply(lambda r: _connected(_adj_of(r)), axis=1)]
                                                 .pipe(lambda d: (d.essential == d.n).mean())) if len(sub) else None,
            }
    by_n = {}
    for n_, grp in P[(P.k == P.vs - 1) & (P.k >= 0)].groupby("n"):
        by_n[int(n_)] = {"rows": int(len(grp)), "full_degree_Q": float((grp.degree_Q == grp.n).mean()),
                         "median_monomial_fraction_Q": float((grp.monomials_Q / 2 ** grp.n).median()),
                         "median_degree_GF2_over_n": float((grp.degree_GF2 / grp.n).median())}
    rank_summary = {}
    if len(R):
        for (n_, lvl), grp in R.groupby(["n", "level"]):
            rank_summary[f"{n_}:{lvl}"] = {
                "graphs": int(len(grp)), "trivial_log2": int(n_ // 2),
                "median_min_log2": float(grp.min_log2.median()),
                "max_min_log2": float(grp.min_log2.max()),
                "share_min_rank_full": float((grp.min_rank == 2 ** (n_ // 2)).mean()),
                "median_max_log2": float(np.log2(grp.max_rank).median()),
            }
    res.update(counts=dict(counts), failures={k: len(v) for k, v in fails.items()},
               failure_examples={k: [str(x) for x in v[:3]] for k, v in fails.items() if v},
               polynomial_summary=summary, polynomial_by_n=by_n, smallest_full=smallest_full,
               split_rank_summary=rank_summary,
               sizes_at_125=[dict(m=m, k=k, **cnf_size_formula(125, [2 * m // 125] * 125, k))
                             for m, k in ((250, 24), (500, 50), (1000, 75), (3875, 100))],
               exact_count_table=exact_count_table(), seconds=round(time.time() - t0, 1))
    for key in ("counts", "failures", "polynomial_summary", "polynomial_by_n", "smallest_full",
                "split_rank_summary", "sizes_at_125"):
        log(f"{key}: {json.dumps(res[key], default=str)}")
    for r in res["exact_count_table"]:
        log("exact_count: " + json.dumps(r))
    log(f"seconds: {res['seconds']}")
    (out_dir / "check.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def _adj_of(row) -> tuple:
    n = int(row["n"])
    adj = [0] * n
    for u, v in row["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return tuple(adj)


def _connected(adj) -> bool:
    n = len(adj)
    if n == 0:
        return True
    seen, stack = 1, [0]
    while stack:
        v = stack.pop()
        new = adj[v] & ~seen
        seen |= new
        while new:
            b = new & -new
            new ^= b
            stack.append(b.bit_length() - 1)
    return seen == (1 << n) - 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=7)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    res = run_checks(nmax=a.nmax, out_dir=a.out)
    sys.exit(0 if sum(res["failures"].values()) == 0 else 1)


if __name__ == "__main__":
    main()
