#!/usr/bin/env python3
"""Brute-force check of every intermediate statement of the Edwards–McDermid
chain (loop0012 item 02; `reports/edwards_mcdermid.md` §2; the plan is
`reports/edwards_mcdermid_plan.md` §0.3–0.5) on every graph on 1–9 vertices
from `nauty-geng`, pathwidth by the vertex-separation subset DP.

The statements, numbered as in the report's §2 (W = weights, C = cut lemma,
P = potential, R = reduction system, S = step inequality, T = Theorem 3.2,
A = assembly budgets, B = basic graphs, H = the shape of hypothesis (H3)):

  W1–W5  recurrence, g non-decreasing, g' non-increasing from 3, property 6,
         0 ≤ g < 1 and 0 ≤ g' ≤ 1/6, the closed form (exact rationals, to n = 40;
         main process)
  C1     pw(G) ≤ max(pw(G[V1]) + |∂1|, pw(G[V2]) + |∂2|, |∂1| + |∂2| − 1)
         (every partition of every graph); C1s the separator form
         pw(G) ≤ max(pw(G[V1]), pw(G[V2])) + min(|∂1|, |∂2|), and C1s ≤ C1
  C2     iterated form on a depth-2 bisection: pw(G) ≤ 2 Σ_i b_i + max_leaf pw;
         C2s the separator form Σ_i b_i + max_leaf pw (b_i the largest
         min(|∂1|, |∂2|) at level i); random trees
  R6     one step costs at most one: pw(H) ≤ pw(H') + 1 (every step)
  P1     f(G − w) = f(G) − g(d(w)) − Σ_{v ∈ N(w)} g'(d(v))        (every w)
  P2     degrees 0 or ≥ 3, w of maximum degree Δ ≥ 4 with a neighbour of degree
         ≤ Δ − 1 ⇒ f(G − w) ≤ f(G) − 1; Δ-regular, Δ ≥ 4 ⇒
         f(G − w) = f(G) − 1 + g'(Δ − 1) − g'(Δ)
  R1     every SPStep (at a vertex of degree 1 or 2) removes ≥ 1 edge
  R2     every SPStep lowers no degree-count: deg_{H'}(u) ≤ deg_H(u) for all u,
         hence f(H') ≤ f(H); a vertex of degree d isolated by the step loses g(d)
  R3     commutation: SPStep H H' at v, w ≠ v ⇒ H' − w = H − w, or
         H' − w = SPStep (H − w) at v (with v of degree 1 or 2 in H − w)
  R5     a step at v inside a component acts on that component only
  RU     (measured) every maximal reduction order reaches the same reduct
  S0     the hinge: G* a reduced reduct of G' = G − w, v with d_{G'}(v) = d ≥ 3
         ⇒ f(G') − f(G*) + g'(δ(G*)) ≥ g'(d)
  S1     the step inequality for the paper's choice of w; S1′ for every
         maximum-degree w (measured); both in the global-minimum form
         1 + f(G*) − g'(δ(G*)) ≤ f(G) − g'(δ(G)), which implies the
         per-component form 1 + f⁻(G*) ≤ f⁻(G)
  SJ     the j-identity (paper (2)–(4)): 1 + f(G') = f(G) − j1 − j2 − j3
  T1     Algorithm X: X, B with B non-empty, reduced, basic,
         |X| + f⁻(B) ≤ f⁻(G); and (measured) r(G − X) = B
  A1/A2  the budgets the record needs at n ≤ 9: max of pw − f⁻ over reduced
         graphs and of pw − main term over all graphs, per n
  B1     connected, every degree ≥ 3, not cubic ⇒ f⁻ ≥ 5/6; connected cubic ⇒
         f⁻ = N/6 − 1/6; f⁻(component) ≥ 0; additivity over components
  H3     pw(G) − pw(r(G)) per n (its maximum is the shape of (H3) at these sizes)

A violation prints the graph6 string and stops (unless --no-stop).

    nice -n 19 python3 reports/scratch/edwards_mcdermid/02_lemmas/check.py --max-n 9 --workers 8
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import subprocess
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

sys.path.insert(0, "/home/al/dev/MOSP")

from learning.edwards_mcdermid import (  # noqa: E402
    F_global, alternating_factorial, bits, components, degrees, edge_count, f_potential,
    fminus, g, g_closed_form, g_prime, global_min_degree, is_basic, is_basic_component,
    is_cubic, is_reduced, isolate, isolate_set, paper_choice, pathwidth_induced, reduce,
    reduce_random, restrict, sp_step, step_vertices, support,
)

HERE = "/home/al/dev/MOSP/reports/scratch/edwards_mcdermid/02_lemmas"

# No sampling: every partition of every graph to 9 vertices (the per-graph
# cost is that of pw(G[S]) for every S, about 3^n · n operations, 20 ms at
# n = 9 on the 9950X), 200 random reduction orders per graph, every step.
C2_TREES = 8            # random depth-2 bisection trees per graph
RANDOM_ORDERS = 200     # reduction orders per graph for RU
S1_RANDOM_REDUCTS = 5   # random reducts of G − w for S1 beside the canonical one


# ----------------------------------------------------------------------------
# graphs
# ----------------------------------------------------------------------------


def parse_g6(line: str) -> tuple[int, list[int]]:
    b = line.strip().encode()
    n = b[0] - 63
    bitlist: list[int] = []
    for ch in b[1:]:
        v = ch - 63
        bitlist += [(v >> i) & 1 for i in range(5, -1, -1)]
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bitlist[k]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def pw_induced(adj: list[int], S: int) -> int:
    return pathwidth_induced(adj, S)


def is_empty(adj: list[int]) -> bool:
    return not any(adj)


def connected_on_support(adj: list[int]) -> bool:
    return len(components(adj)) == 1


# ----------------------------------------------------------------------------
# the per-graph worker
# ----------------------------------------------------------------------------


def one(args: tuple[int, str]) -> dict:
    idx, line = args
    n, adj = parse_g6(line)
    rng = random.Random(idx * 1_000_003 + n)
    cnt: collections.Counter = collections.Counter()
    mx: dict[str, Fraction | int] = {}
    viol: list[str] = []

    def bump(key: str, value):
        if key not in mx or value > mx[key]:
            mx[key] = value

    def bad(stmt: str, detail: str):
        viol.append(f"{stmt}\t{line.strip()}\t{detail}")

    deg = degrees(adj)
    full = (1 << n) - 1
    supp = support(adj)
    heavy = True

    # pathwidth of G and of r(G)
    pw = pw_induced(adj, full)
    radj, removed = reduce(adj)
    pw_r = pw_induced(radj, support(radj))
    cnt["graphs"] += 1
    gap = pw - pw_r
    if gap < 0:
        bad("H3-minor", f"pw={pw} pw_r={pw_r}")
    bump("H3_gap", gap)
    cnt[f"H3_gap_{gap}"] += 1
    main_term = f_potential(radj)
    bump("A2_pw_minus_main", pw - main_term)
    reduced = is_reduced(adj)
    if reduced:
        cnt["reduced"] += 1
        bump("A1_pw_minus_fminus", pw - fminus(adj))
        if gap != 0:
            bad("H3-reduced", "a reduced graph is its own reduct")

    # ---- P1, P2: one deletion -------------------------------------------
    f_G = f_potential(adj)
    Delta = max(deg) if n else 0
    for w in range(n):
        Gw = isolate(adj, w)
        lhs = f_potential(Gw)
        rhs = f_G - g(deg[w]) - sum((g_prime(deg[v]) for v in bits(adj[w])), Fraction(0))
        cnt["P1"] += 1
        if lhs != rhs:
            bad("P1", f"w={w} lhs={lhs} rhs={rhs}")
        if reduced and deg[w] == Delta and Delta >= 4:
            if any(deg[v] <= Delta - 1 for v in bits(adj[w])):
                cnt["P2"] += 1
                if not lhs <= f_G - 1:
                    bad("P2", f"w={w} f(G-w)={lhs} f(G)={f_G}")
            if all(deg[v] == Delta for v in range(n) if adj[v]):
                cnt["P2reg"] += 1
                if lhs != f_G - 1 + g_prime(Delta - 1) - g_prime(Delta):
                    bad("P2reg", f"w={w} f(G-w)={lhs} f(G)={f_G} Delta={Delta}")

    # ---- R1, R2, R3, R5, R6: one step ----------------------------------
    steps = step_vertices(adj)
    comps = components(adj)
    comp_of = {}
    for C in comps:
        for v in bits(C):
            comp_of[v] = C
    m_G = edge_count(adj)
    for v in steps:
        H2 = sp_step(adj, v)
        cnt["R1"] += 1
        if not edge_count(H2) <= m_G - 1:
            bad("R1", f"v={v}")
        d2 = degrees(H2)
        cnt["R2"] += 1
        if any(d2[u] > deg[u] for u in range(n)):
            bad("R2", f"v={v} degree rose")
        if not f_potential(H2) <= f_G:
            bad("R2f", f"v={v}")
        if not f_G - f_potential(H2) >= g(deg[v]):
            bad("R2iso", f"v={v}")
        # R3
        for w in range(n):
            if w == v:
                continue
            cnt["R3"] += 1
            Hw = isolate(adj, w)
            H2w = isolate(H2, w)
            if H2w == Hw:
                cnt["R3_zero"] += 1
            elif 1 <= Hw[v].bit_count() <= 2 and sp_step(Hw, v) == H2w:
                cnt["R3_one"] += 1
            else:
                bad("R3", f"v={v} w={w}")
        # R5
        if len(comps) >= 2:
            C = comp_of[v]
            cnt["R5"] += 1
            inside = restrict(adj, C)
            outside = [adj[u] & ~C for u in range(n)]
            lifted = sp_step(inside, v)
            if [lifted[u] | outside[u] for u in range(n)] != H2:
                bad("R5", f"v={v}")
        # R6 (pathwidth-heavy, sampled at 9)
        if heavy:
            cnt["R6"] += 1
            pw2 = pw_induced(H2, support(H2))
            if not pw <= pw2 + 1:
                bad("R6", f"v={v} pw={pw} pw'={pw2}")
            bump("R6_drop", pw - pw2)

    # ---- RU: uniqueness of the reduct -----------------------------------
    if steps:
        k = RANDOM_ORDERS
        same = True
        for _ in range(k):
            if reduce_random(adj, rng) != radj:
                same = False
                break
        cnt["RU_graphs"] += 1
        cnt["RU_orders"] += k
        if not same:
            cnt["RU_nonunique"] += 1

    # ---- B1, additivity -------------------------------------------------
    fm = fminus(adj)
    tot = Fraction(0)
    for C in comps:
        sub = restrict(adj, C)
        fc = fminus(sub)
        tot += fc
        cnt["B1_nonneg"] += 1
        if fc < 0:
            bad("B1neg", f"component {C:b} fminus={fc}")
    cnt["B1_add"] += 1
    if tot != fm:
        bad("B1add", f"sum={tot} fminus={fm}")
    connected = len(comps) == 1
    min3 = bool(supp) and all(d == 0 or d >= 3 for d in deg)
    if connected and min3:
        if is_cubic(adj, supp):
            N = supp.bit_count()
            cnt["B1_cubic"] += 1
            if fm != Fraction(N, 6) - Fraction(1, 6):
                bad("B1cubic", f"fminus={fm} N={N}")
        else:
            cnt["B1_noncubic"] += 1
            if fm < Fraction(5, 6):
                bad("B1floor", f"fminus={fm}")

    # ---- S0, S1, S1′, SJ: the step ----------------------------------------
    if connected and min3:
        basic = is_basic(adj)
        cnt["S_conn_min3"] += 1
        if basic:
            cnt["S_basic"] += 1
        else:
            cnt["S_nonbasic"] += 1
            maxs, chosen, D = paper_choice(adj)
            assert D >= 4
            FG = F_global(adj)
            for w in maxs:
                Gp = isolate(adj, w)
                dp = degrees(Gp)
                reducts = [reduce(Gp)[0]]
                for _ in range(S1_RANDOM_REDUCTS):
                    r = reduce_random(Gp, rng)
                    if r not in reducts:
                        reducts.append(r)
                nbrs = sorted(bits(adj[w]), key=lambda v: deg[v])
                j1 = g_prime(deg[nbrs[0]]) - g_prime(D - 1)
                j2 = g_prime(deg[nbrs[1]]) - g_prime(D)
                j3 = sum((g_prime(deg[v]) - g_prime(D) for v in nbrs[2:]), Fraction(0))
                cnt["SJ"] += 1
                if 1 + f_potential(Gp) != f_G - j1 - j2 - j3:
                    bad("SJ", f"w={w}")
                for Gs in reducts:
                    if is_empty(Gs):
                        bad("S-empty", f"w={w}: G* empty though G is not basic")
                        continue
                    f_Gs = f_potential(Gs)
                    gd = g_prime(global_min_degree(Gs))
                    # S0 for every v of degree ≥ 3 in G'
                    for v in range(n):
                        if dp[v] >= 3:
                            cnt["S0"] += 1
                            if not f_potential(Gp) - f_Gs + gd >= g_prime(dp[v]):
                                bad("S0", f"w={w} v={v}")
                    ok = 1 + f_Gs - gd <= FG
                    okc = 1 + fminus(Gs) <= fm
                    if w in chosen:
                        cnt["S1"] += 1
                        if not ok:
                            bad("S1", f"w={w} 1+F(G*)={1 + f_Gs - gd} F(G)={FG}")
                        if not okc:
                            bad("S1c", f"w={w}")
                    cnt["S1p"] += 1
                    if not ok:
                        cnt["S1p_fail"] += 1
                        if cnt["S1p_fail"] == 1:
                            cnt["S1p_fail_graphs"] += 1
                            viol.append(f"S1p-MEASURED\t{line.strip()}\tw={w} chosen={chosen} "
                                        f"1+F(G*)={1 + f_Gs - gd} F(G)={FG}")
                    if not okc:
                        cnt["S1pc_fail"] += 1

    # ---- T1: Algorithm X -------------------------------------------------
    if reduced and supp:
        cnt["T1"] += 1
        X = 0
        cur = list(adj)
        while True:
            comps_cur = components(cur)
            nonbasic = [C for C in comps_cur if not is_basic_component(cur, C)]
            if not nonbasic:
                break
            C = nonbasic[0]
            _, chosen, _ = paper_choice(cur, C)
            w = rng.choice(chosen)
            X |= 1 << w
            cur, _ = reduce(isolate(cur, w))
        B = cur
        if is_empty(B):
            bad("T1empty", f"X={X:b}")
        if not is_reduced(B):
            bad("T1reduced", f"X={X:b}")
        if not is_basic(B):
            bad("T1basic", f"X={X:b}")
        if not X.bit_count() + fminus(B) <= fm:
            bad("T1", f"X={X:b} |X|+fminus(B)={X.bit_count() + fminus(B)} fminus(G)={fm}")
        if X & ~supp:
            bad("T1supp", f"X={X:b}")
        direct, _ = reduce(isolate_set(adj, X))
        cnt["T1_direct"] += 1
        if direct != B:
            cnt["T1_direct_differs"] += 1
        bump("T1_X", X.bit_count())

    # ---- C1, C2: the cut lemma --------------------------------------------
    if heavy:
        parts = range(0, 1 << (n - 1))         # V1 ∌ vertex n−1: each partition once
        pwcache: dict[int, int] = {full: pw, 0: 0}

        def pwS(S: int) -> int:
            if S not in pwcache:
                pwcache[S] = pw_induced(adj, S)
            return pwcache[S]

        for V1 in parts:
            V2 = full & ~V1
            b1 = sum(1 for v in bits(V1) if adj[v] & V2)
            b2 = sum(1 for v in bits(V2) if adj[v] & V1)
            bound = max(pwS(V1) + b1, pwS(V2) + b2, b1 + b2 - 1)
            cnt["C1"] += 1
            if not pw <= bound:
                bad("C1", f"V1={V1:b} pw={pw} bound={bound}")
            # C1s: the separator form, max(pw(G[V1]), pw(G[V2])) + min(|∂1|, |∂2|)
            bound_s = max(pwS(V1), pwS(V2)) + min(b1, b2)
            cnt["C1s"] += 1
            if not pw <= bound_s:
                bad("C1s", f"V1={V1:b} pw={pw} bound_s={bound_s}")
            if not bound_s <= bound:
                bad("C1s-le-C1", f"V1={V1:b}")
            bump("C1_slack", bound - pw)
            bump("C1s_slack", bound_s - pw)
            if bound_s == pw:
                cnt["C1s_tight"] += 1
        # C2: depth-2 bisection trees (random), budgets b_i = max boundary at level i
        if n >= 4:
            for _ in range(C2_TREES):
                V1 = rng.randrange(0, 1 << (n - 1))
                V2 = full & ~V1
                lvl1 = max(sum(1 for v in bits(V1) if adj[v] & V2),
                           sum(1 for v in bits(V2) if adj[v] & V1))
                lvl1s = min(sum(1 for v in bits(V1) if adj[v] & V2),
                            sum(1 for v in bits(V2) if adj[v] & V1))
                lvl2 = 0
                lvl2s = 0
                leaves = []
                for P in (V1, V2):
                    pb = list(bits(P))
                    sub = 0
                    for v in pb:
                        if rng.random() < 0.5:
                            sub |= 1 << v
                    Q1, Q2 = sub, P & ~sub
                    c1 = sum(1 for v in bits(Q1) if adj[v] & Q2)
                    c2 = sum(1 for v in bits(Q2) if adj[v] & Q1)
                    lvl2 = max(lvl2, c1, c2)
                    lvl2s = max(lvl2s, min(c1, c2))
                    leaves += [pwS(Q1), pwS(Q2)]
                bound = 2 * (lvl1 + lvl2) + max(leaves)
                cnt["C2"] += 1
                if not pw <= bound:
                    bad("C2", f"pw={pw} bound={bound}")
                # C2s: the separator form iterated, Σ_i b_i with b_i the largest
                # min(|∂1|, |∂2|) at level i
                bound_s = lvl1s + lvl2s + max(leaves)
                cnt["C2s"] += 1
                if not pw <= bound_s:
                    bad("C2s", f"pw={pw} bound_s={bound_s}")

    return {"n": n, "cnt": cnt, "mx": mx, "viol": viol}


# ----------------------------------------------------------------------------
# W1–W5 (main process)
# ----------------------------------------------------------------------------


def check_weights(N: int = 40) -> list[str]:
    out = []
    for d in range(4, N + 1):
        assert d * g(d) == (d - 2) * g(d - 1) + g(d - 2) + 1, d          # W1
    for d in range(0, N):
        assert g(d + 1) >= g(d), d                                       # W2 (Lemma 8.3)
    for d in range(3, N):
        assert g_prime(d + 1) <= g_prime(d), d                           # W3 (Lemma 8.4)
    for d in range(4, N + 1):
        assert 1 - g(d) == (d - 1) * g_prime(d) + g_prime(d - 1), d      # W4 (property 6)
    for d in range(0, N + 1):
        assert 0 <= g(d) < 1, d                                          # W5a
        assert 0 <= g_prime(d) <= Fraction(1, 6), d                      # W5b
    for d in range(2, N + 1):
        assert g_closed_form(d) == g(d), d                               # W5c (Lemma 8.1)
    for d in range(5, N):                                                # property 5 (not used)
        assert g(d + 1) / (d + 1) < g(d) / d, d
    for d in range(5, N + 1):                                            # the g' recurrence
        assert d * g_prime(d) == (d - 3) * g_prime(d - 1) + g_prime(d - 2), d
    for d in range(4, N + 1):                                            # the sandwich
        assert g_prime(d - 1) >= g_prime(d) >= g_prime(d - 1) / 3, d
    for d in range(3, N + 1):                                            # coupled invariant
        assert g(d - 1) <= g(d) <= (1 + g(d - 1)) / 2, d
    out.append(f"W1–W5 hold to n = {N} in exact rationals: recurrence (W1), g non-decreasing (W2), "
               f"g' non-increasing from 3 (W3), property 6 (W4), 0 ≤ g < 1 and 0 ≤ g' ≤ 1/6 (W5), "
               f"closed form (Lemma 8.1); also property 5, the g' recurrence n g'(n) = (n−3) g'(n−1) + g'(n−2) "
               f"for n ≥ 5, the sandwich g'(n−1) ≥ g'(n) ≥ g'(n−1)/3 (n ≥ 4) and the coupled invariant "
               f"g(n−1) ≤ g(n) ≤ (1 + g(n−1))/2 (n ≥ 3).")
    out.append("g(3..9) = " + ", ".join(str(g(d)) for d in range(3, 10)))
    out.append("g'(3..9) = " + ", ".join(str(g_prime(d)) for d in range(3, 10)))
    out.append(f"A(1..6) = {[alternating_factorial(k) for k in range(1, 7)]}")
    return out


# ----------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------


def geng(n: int) -> list[str]:
    return subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True,
                          check=True).stdout.splitlines()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--min-n", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-stop", action="store_true")
    ap.add_argument("--log", default=f"{HERE}/check.log")
    a = ap.parse_args()

    log = open(a.log, "w")

    def say(s: str = ""):
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"# item 02 brute-force check, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, "
        f"n = {a.min_n}..{a.max_n}, {a.workers} workers")
    for s in check_weights():
        say(s)

    violations: list[str] = []
    per_n: dict[int, dict] = {}
    t0 = time.time()
    stop = False
    with Pool(a.workers) as pool:
        for n in range(a.min_n, a.max_n + 1):
            lines = geng(n)
            tn = time.time()
            cnt: collections.Counter = collections.Counter()
            mx: dict = {}
            for res in pool.imap_unordered(one, list(enumerate(lines)), chunksize=64):
                cnt.update(res["cnt"])
                for k, v in res["mx"].items():
                    if k not in mx or v > mx[k]:
                        mx[k] = v
                if res["viol"]:
                    hard = [v for v in res["viol"] if not v.startswith("S1p-MEASURED")]
                    violations += res["viol"]
                    for v in res["viol"]:
                        if v.startswith("S1p"):
                            cnt["S1p_logged"] += 1
                            if cnt["S1p_logged"] <= 20:
                                say("MEASURED " + v)
                        else:
                            say("VIOLATION " + v)
                    if hard and not a.no_stop:
                        stop = True
                        break
            per_n[n] = {"cnt": dict(cnt), "mx": {k: str(v) for k, v in mx.items()},
                        "seconds": round(time.time() - tn, 1)}
            say(f"n={n}: {len(lines)} graphs in {time.time() - tn:.1f}s; "
                + "; ".join(f"{k}={v}" for k, v in sorted(cnt.items()))
                + "; maxima " + ", ".join(f"{k}={v}" for k, v in sorted(mx.items())))
            if stop:
                say("STOPPED on a violation")
                pool.terminate()
                break
    say(f"total {time.time() - t0:.1f}s; violations (hard): "
        f"{sum(1 for v in violations if not v.startswith('S1p'))}; "
        f"S1′ measured failures: {sum(1 for v in violations if v.startswith('S1p'))}")
    with open(f"{HERE}/violations.txt", "w") as fh:
        fh.write("# statement\tgraph6\tdetail  (S1p-MEASURED lines are the S1′ measurement, not violations)\n")
        for v in violations:
            fh.write(v + "\n")
    with open(f"{HERE}/summary.json", "w") as fh:
        json.dump(per_n, fh, indent=1)
    log.close()


if __name__ == "__main__":
    main()
