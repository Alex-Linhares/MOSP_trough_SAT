"""Brute-force check of the theorems of `reports/separator_moment.md` §8
(loop0011 item 08) before any is stated: Theorem S (the separator first moment
in finite form) with its factorisation step, Corollary S′ with Lemmas G
(Gilbert), F (first-vertex component) and P (the partition formula), Theorem Cl
(the closed-pair count), Lemma W (the weighted-count identity) with the flip
lemma as its first instance, and Lemma J (the joint binomial moments of the
flips on random covers).

Stage 1 — every labelled graph on n = 1..MAX_N vertices (2^C(n,2) of them), in
exact rationals at p = 1/2 and p = 1/3, for every k < n:

  S    Σ_{pw(G) ≤ k} w_p(G)  ≤  C(n, k) · P_N(E_bip)  ≤  C(n, k) · P_N(E_relax);
  fact for every k-set S (n ≤ 6): Σ_{G : E_bip(S)} w_p(G) = P_N(E_bip) exactly
       (the factorisation of the G(n, p) weight over G[V ∖ S]);
  P    P_N(E_bip) enumerated = the partition formula (`prob_bip_exact`);
  F    P_N(E_relax) enumerated = the first-vertex recursion (`prob_relax_exact`);
  G    P(connected) enumerated = Gilbert's recursion (`connected_probs_exact`);
  Cl   Σ_{pw ≤ k} w_p(G) ≤ E[X₃] and E[X₃] enumerated = Theorem Cl's formula
       (`closed_count_exact`); E[X₁] enumerated = C(n,t)C(n−t,N−t)(1−p)^{t(N−t)};
  Fl   (n ≤ 6) for every exact-size empty pair, every flip swap is an exact-size
       empty pair, the swaps are distinct, their number is C(I_A + I_R, I_A) ≤ X.
  The floating-point implementations of item 05–06 (`log_prob_bip`,
  `log_prob_rel`, `log_closed_count`) are pinned to the exact values.

Stage 2 — Lemma W on 1,000 random instances at n = 10 (600 G(10, p), 400
random clique covers), at k = pw and k = pw − 1, with Z = the move-class size
and Z = the flip count: Z ≤ X, Y = Σ 1/Z ≥ 1[X > 0], Y ≤ X, Y_move = X₄.

Stage 3 — the first instance's exact evaluation: Lemma J's joint binomial
moments against the enumeration of every cover at tiny sizes, and
E[Y], E[X] from `flip_log_bound` against 1,000 Monte Carlo covers at n = 10.

    nice -n 19 python3 reports/scratch/separator_moment/08_theorems/check.py --max-n 7 --workers 8
"""
from __future__ import annotations

import argparse
import math
import random
import sys
import time
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, "/home/al/dev/MOSP")

import numpy as np  # noqa: E402

from benchmarks.generator import generate_structured_instance  # noqa: E402
from learning.separator_moment import (  # noqa: E402
    closed_count_exact, closed_nbhd, components, connected_probs_exact, enumerate_empty_pairs,
    flip_count, flip_joint_pmf, flip_log_bound, flip_swaps, forced_sizes, is_empty_pair,
    log_closed_count, log_prob_bip, log_prob_rel, mosp_masks, move_classes, pair_count_exact,
    popcount, prob_bip_exact, prob_relax_exact, vertex_separation, weighted_count,
)

HERE = Path(__file__).resolve().parent
VIOL = 0


def viol(msg: str) -> None:
    global VIOL
    VIOL += 1
    print("VIOLATION " + msg, flush=True)


# ---------------------------------------------------------------- stage 1: enumeration

def chunk(args):
    """All labelled graphs on n vertices with edge mask in [lo, hi): the counts."""
    n, lo, hi, per_S = args
    pairs = list(combinations(range(n), 2))
    Cn = len(pairs)
    full = (1 << n) - 1
    ks = range(n)
    sizes = {k: forced_sizes(n, k) for k in ks}
    pw_le = [[0] * (Cn + 1) for _ in ks]
    X1 = [[0] * (Cn + 1) for _ in ks]
    X3 = [[0] * (Cn + 1) for _ in ks]
    t_half = (n + 1) // 2
    bip = [0] * (Cn + 1)                      # E_bip at t = ⌈n/2⌉ on the n-vertex graph
    relax = [[0] * (Cn + 1) for _ in range(n + 1)]   # E_relax(M), M = 0..n
    conn = [0] * (Cn + 1)
    bipS = defaultdict(lambda: [0] * (Cn + 1))      # (k, S) -> counts of E_bip(S)
    flip_checked = 0
    flip_bad = 0
    for mask in range(lo, hi):
        adj = [0] * n
        e = 0
        for i, (u, v) in enumerate(pairs):
            if mask >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                e += 1
        pw = vertex_separation(adj)
        for k in range(pw, n):
            pw_le[k][e] += 1
        # one pass over all A: exact-size pairs and closed pairs at every k
        nbhd = [closed_nbhd(adj, A) for A in range(1 << n)]
        for A in range(1 << n):
            a = popcount(A)
            free = n - popcount(nbhd[A])
            R = full & ~nbhd[A]
            r = popcount(R)
            closed = (A == full & ~nbhd[R])
            for k in ks:
                N, t = sizes[k]
                if a == t and free >= N - t:
                    X1[k][e] += comb(free, N - t)
                if closed and a >= t and r >= N - t and n - a - r <= k:
                    X3[k][e] += 1
        # components of the whole graph: E_bip, E_relax(M), connectedness
        cs = [popcount(c) for c in components(adj, full)]
        reach = 1
        for s in cs:
            reach |= reach << s
        if reach >> t_half & 1:
            bip[e] += 1
        big = max(cs)
        for M in range(big, n + 1):
            relax[M][e] += 1
        if len(cs) == 1:
            conn[e] += 1
        if per_S:
            for k in ks:
                N, t = sizes[k]
                for combo in combinations(range(n), k):
                    S = sum(1 << v for v in combo)
                    sz = [popcount(c) for c in components(adj, full & ~S)]
                    rc = 1
                    for s in sz:
                        rc |= rc << s
                    if rc >> t & 1:
                        bipS[(k, S)][e] += 1
            # the flip lemma on every exact-size pair at every k
            for k in ks:
                N, t = sizes[k]
                ps = enumerate_empty_pairs(adj, k)
                X = len(ps)
                pset = set(ps)
                for (A, R) in ps:
                    sw = flip_swaps(adj, A, R)
                    ia, ir, Z = flip_count(adj, A, R)
                    flip_checked += 1
                    ok = (len(sw) == Z and len(set(sw)) == Z and Z <= X
                          and all(P in pset for P in sw) and sw[0] == (A, R))
                    if not ok:
                        flip_bad += 1
    return (n, pw_le, X1, X3, bip, relax, conn, dict(bipS), flip_checked, flip_bad)


def merge(acc, res):
    n, pw_le, X1, X3, bip, relax, conn, bipS, fc, fb = res
    a = acc.setdefault(n, None)
    if a is None:
        acc[n] = [pw_le, X1, X3, bip, relax, conn, defaultdict(lambda: [0] * len(bip)), 0, 0]
        a = acc[n]
    else:
        for k in range(n):
            for e in range(len(bip)):
                a[0][k][e] += pw_le[k][e]
                a[1][k][e] += X1[k][e]
                a[2][k][e] += X3[k][e]
        for e in range(len(bip)):
            a[3][e] += bip[e]
            a[5][e] += conn[e]
            for M in range(n + 1):
                a[4][M][e] += relax[M][e]
    for key, cnt in bipS.items():
        row = a[6][key]
        for e in range(len(bip)):
            row[e] += cnt[e]
    a[7] += fc
    a[8] += fb


def wsum(counts, p: Fraction, Cn: int) -> Fraction:
    q = 1 - p
    return sum(c * p ** e * q ** (Cn - e) for e, c in enumerate(counts) if c)


def stage1(max_n: int, workers: int, ps):
    acc = {}
    t0 = time.time()
    for n in range(1, max_n + 1):
        Cn = n * (n - 1) // 2
        total = 1 << Cn
        per_S = n <= 6
        step = max(1, min(1 << 14, total // (4 * workers) or 1))
        jobs = [(n, lo, min(lo + step, total), per_S) for lo in range(0, total, step)]
        if workers > 1 and len(jobs) > 1:
            with Pool(workers) as pool:
                for res in pool.imap_unordered(chunk, jobs):
                    merge(acc, res)
        else:
            for job in jobs:
                merge(acc, chunk(job))
        print(f"n={n}: {total} labelled graphs enumerated in {time.time() - t0:.0f} s"
              f" ({len(jobs)} chunks, per-S factorisation {'on' if per_S else 'off'})", flush=True)
    # the inner tables per N: P_N(E_bip), P_N(E_relax(M)), connectedness
    print("\n== Lemmas G, F, P: the inner probabilities, enumerated against the formulas ==")
    for N in range(1, max_n + 1):
        Cn = N * (N - 1) // 2
        _, _, _, bip, relax, conn, _, _, _ = acc[N]
        for p in ps:
            C = connected_probs_exact(N, p)
            pc = wsum(conn, p, Cn)
            if pc != C[N]:
                viol(f"Lemma G N={N} p={p}: enumerated {pc} != Gilbert {C[N]}")
            pb = wsum(bip, p, Cn)
            pb_f = prob_bip_exact(N, p, None, C)
            if pb != pb_f:
                viol(f"Lemma P N={N} p={p}: enumerated {pb} != partition formula {pb_f}")
            lf = log_prob_bip(N, float(p))
            if abs(lf - math.log(pb)) > 1e-9:
                viol(f"log_prob_bip N={N} p={p}: {lf} vs exact {math.log(pb)}")
            for M in range(1, N + 1):
                pr = wsum(relax[M], p, Cn)
                pr_f = prob_relax_exact(N, p, M, C)
                if pr != pr_f:
                    viol(f"Lemma F N={N} p={p} M={M}: enumerated {pr} != recursion {pr_f}")
                lf = log_prob_rel(N, float(p), M)
                if abs(lf - math.log(pr)) > 1e-9:
                    viol(f"log_prob_rel N={N} p={p} M={M}: {lf} vs exact {math.log(pr)}")
            t = (N + 1) // 2
            print(f"  N={N} p={p}: P(conn)={float(pc):.6f} = C_N (Gilbert) OK;"
                  f" P_N(E_bip)={float(pb):.6f} = partition formula OK;"
                  f" P_N(E_relax(t={t}))={float(wsum(relax[t], p, Cn)):.6f} = recursion OK (all M)")
    print("\n== Theorems S and Cl at every (n, k, p): the weighted count of {pw <= k} against the bounds ==")
    print("  columns: P(pw<=k) | C(n,k)·P_N(E_bip) | C(n,k)·P_N(E_relax) | E[X3] (Cl) | E[X1] (pairs) | E[X3]/E[X1]")
    for n in range(1, max_n + 1):
        Cn = n * (n - 1) // 2
        pw_le, X1, X3, _, _, _, bipS, fc, fb = acc[n]
        for p in ps:
            for k in range(n):
                N, t = forced_sizes(n, k)
                lhs = wsum(pw_le[k], p, Cn)
                _, _, _, bipN, relaxN, _, _, _, _ = acc[N]
                CN = N * (N - 1) // 2
                inner_bip = wsum(bipN, p, CN)
                inner_rel = wsum(relaxN[t], p, CN)
                S_bound = comb(n, k) * inner_bip
                R_bound = comb(n, k) * inner_rel
                ex1 = wsum(X1[k], p, Cn)
                ex3 = wsum(X3[k], p, Cn)
                if not lhs <= S_bound:
                    viol(f"Theorem S n={n} k={k} p={p}: {lhs} > {S_bound}")
                if not S_bound <= R_bound:
                    viol(f"Corollary S' n={n} k={k} p={p}: E_bip bound {S_bound} > E_relax bound {R_bound}")
                if not lhs <= ex3:
                    viol(f"Theorem Cl n={n} k={k} p={p}: {lhs} > E[X3] {ex3}")
                if not lhs <= ex1:
                    viol(f"pair count n={n} k={k} p={p}: {lhs} > E[X1] {ex1}")
                f1 = pair_count_exact(n, k, p)
                if ex1 != f1:
                    viol(f"E[X1] n={n} k={k} p={p}: enumerated {ex1} != formula {f1}")
                f3 = closed_count_exact(n, k, p)
                if ex3 != f3:
                    viol(f"E[X3] n={n} k={k} p={p}: enumerated {ex3} != Theorem Cl formula {f3}")
                lc = log_closed_count(n, k, float(p))
                if abs(lc - math.log(ex3)) > 1e-9:
                    viol(f"log_closed_count n={n} k={k} p={p}: {lc} vs exact {math.log(ex3)}")
                # the factorisation per S
                nS = 0
                for combo in combinations(range(n), k):
                    S = sum(1 << v for v in combo)
                    if (k, S) in bipS:
                        v = wsum(bipS[(k, S)], p, Cn)
                        nS += 1
                        if v != inner_bip:
                            viol(f"factorisation n={n} k={k} S={combo} p={p}: {v} != P_N(E_bip) {inner_bip}")
                print(f"  n={n} k={k} N={N} t={t} p={p}: {float(lhs):.6f} <= {float(S_bound):.6f} <= {float(R_bound):.6f} OK;"
                      f" Cl {float(ex3):.6f} OK; pairs {float(ex1):.6f} OK; X3/X1 {float(ex3 / ex1):.3f}"
                      + (f"; factorisation identity on {nS} sets S OK" if nS else ""))
        if fc:
            print(f"  n={n}: flip lemma on {fc} exact-size pairs, {fb} violations")
            if fb:
                viol(f"flip lemma n={n}: {fb} of {fc} pairs")


# ---------------------------------------------------------------- stage 2: Lemma W at n = 10

def random_adj(n, p, seed):
    rng = random.Random(seed)
    adj = [0] * n
    for u, v in combinations(range(n), 2):
        if rng.random() < p:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    return adj


def lemma_w_instance(args):
    kind, n, seed = args
    if kind == "gnp":
        p = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7)[seed % 6]
        adj = random_adj(n, p, seed)
        label = f"G({n},{p})"
    else:
        m = (n, 2 * n)[seed % 2]
        cpp = (2, 3, 4)[seed % 3]
        inst = generate_structured_instance(n, m, cpp, seed=seed)
        adj = mosp_masks(np.asarray(inst.matrix))
        label = f"cover({n},{m},{cpp})"
    pw = vertex_separation(adj)
    rows = []
    for k in (pw, pw - 1):
        if k < 0:
            continue
        ps = enumerate_empty_pairs(adj, k)
        X = len(ps)
        pset = set(ps)
        bad = 0
        if X:
            cls = move_classes(ps, n)
            size = defaultdict(int)
            for c in cls:
                size[c] += 1
            Zm = {P: size[c] for P, c in zip(ps, cls)}
            X4 = len(size)
            Zf = {}
            for (A, R) in ps:
                sw = flip_swaps(adj, A, R)
                ia, ir, Z = flip_count(adj, A, R)
                if not (len(sw) == Z == len(set(sw)) and all(Q in pset for Q in sw) and Z <= X):
                    bad += 1
                Zf[(A, R)] = Z
                if Zm[(A, R)] > X:
                    bad += 1
            Ym = weighted_count(ps, lambda P: Zm[P])
            Yf = weighted_count(ps, lambda P: Zf[P])
            if Ym != X4:
                bad += 1
            if not (1 <= Yf <= X and 1 <= Ym <= X):
                bad += 1
        else:
            X4, Ym, Yf = 0, Fraction(0), Fraction(0)
        rows.append((label, seed, pw, k, X, X4, float(Ym), float(Yf), bad))
    return rows


def stage2(workers: int):
    print("\n== Lemma W on 1,000 random instances at n = 10 (600 G(n, p), 400 random covers) ==")
    jobs = [("gnp", 10, i) for i in range(600)] + [("cover", 10, i) for i in range(400)]
    rows = []
    with Pool(workers) as pool:
        for r in pool.imap_unordered(lemma_w_instance, jobs, chunksize=8):
            rows += r
    bad = sum(r[8] for r in rows)
    if bad:
        viol(f"Lemma W / flip lemma at n = 10: {bad} violations")
    import csv
    with open(HERE / "lemma_w_n10.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instance", "seed", "pw", "k", "X", "X4", "Y_move", "Y_flip", "violations"])
        w.writerows(rows)
    for kind in ("G(", "cover"):
        for at in ("pw", "pw-1"):
            sel = [r for r in rows if r[0].startswith(kind) and ((r[3] == r[2]) == (at == "pw"))]
            if not sel:
                continue
            Xs = sorted(r[4] for r in sel)
            X4s = sorted(r[5] for r in sel)
            Yf = sorted(r[7] for r in sel)
            zero = sum(1 for r in sel if r[4] == 0)
            med = lambda v: v[len(v) // 2]
            print(f"  {kind:6s} k={at:4s}: {len(sel)} instances, X=0 on {zero}; median X {med(Xs)},"
                  f" X4 {med(X4s)}, Y_flip {med(Yf):.3f}; max X {Xs[-1]}, Y_flip range [{Yf[0]:.3f}, {Yf[-1]:.3f}];"
                  f" Y >= 1[X>0] on all; violations {sum(r[8] for r in sel)}")


# ---------------------------------------------------------------- stage 3: the first instance, exactly

def all_covers(n, sizes):
    pools = [[sum(1 << v for v in c) for c in combinations(range(n), s)] for s in sizes]
    from itertools import product
    return product(*pools)


def stage3(samples: int, seed: int = 0):
    print("\n== Lemma J: the joint binomial moments of the flips against every cover at tiny sizes ==")
    rng = random.Random(seed)
    cases = 0
    for n in range(3, 7):
        for m in (1, 2, 3):
            for _ in range(2):
                sizes = [rng.randint(2, min(3, n)) for _ in range(m)]
                a = rng.randint(1, n - 1)
                r = rng.randint(1, n - a)
                A, R = (1 << a) - 1, ((1 << r) - 1) << a
                counts = defaultdict(int)
                tot = 0
                for masks in all_covers(n, sizes):
                    tot += 1
                    if any(mk & A and mk & R for mk in masks):
                        continue
                    adj = [0] * n
                    for mk in masks:
                        vs = [v for v in range(n) if mk >> v & 1]
                        for u in vs:
                            for v in vs:
                                if u != v:
                                    adj[u] |= 1 << v
                    ia, ir, _ = flip_count(adj, A, R)
                    counts[(ia, ir)] += 1
                pmf = flip_joint_pmf(n, a, r, sizes)
                ok = all(pmf[i][ip] == Fraction(counts.get((i, ip), 0), tot) for i in range(a + 1) for ip in range(r + 1))
                cases += 1
                if not ok:
                    viol(f"Lemma J n={n} sizes={sizes} a={a} r={r}")
    print(f"  {cases} cases (n = 3–6, m ≤ 3, sizes 2–3): the inverted moments equal the enumerated joint law on all")
    print(f"\n== E[Y] and E[X] from the generating function against {samples} Monte Carlo covers at n = 10, m = 10, d = 3 ==")
    n, m, d = 10, 10, 3
    sizes = [d] * m
    rs = np.random.default_rng(seed)
    for k in (3, 4, 5, 6):
        N, t = forced_sizes(n, k)
        lY, lX = flip_log_bound(n, k, sizes)
        EY, EX = math.exp(lY), math.exp(lX)
        ys, xs, pos = [], [], 0
        for _ in range(samples):
            adj = [0] * n
            for _j in range(m):
                vs = [int(v) for v in rs.choice(n, d, replace=False)]
                for u in vs:
                    for v in vs:
                        if u != v:
                            adj[u] |= 1 << v
            ps = enumerate_empty_pairs(adj, k)
            X = len(ps)
            Y = float(weighted_count(ps, lambda P: flip_count(adj, P[0], P[1])[2])) if X else 0.0
            ys.append(Y)
            xs.append(X)
            pos += X > 0
        ys, xs = np.array(ys), np.array(xs)
        seY, seX = ys.std(ddof=1) / math.sqrt(samples), xs.std(ddof=1) / math.sqrt(samples)
        zY, zX = (ys.mean() - EY) / seY if seY else 0.0, (xs.mean() - EX) / seX if seX else 0.0
        flag = "" if abs(zY) < 4 and abs(zX) < 4 else "  <-- more than 4 s.e."
        if abs(zY) >= 4 or abs(zX) >= 4:
            viol(f"Monte Carlo n={n} k={k}: E[Y] {EY:.4f} vs {ys.mean():.4f} ({zY:+.1f} s.e.); E[X] {EX:.4f} vs {xs.mean():.4f} ({zX:+.1f} s.e.)")
        print(f"  k={k} (N={N}, t={t}): exact E[Y]={EY:.4f}, sample {ys.mean():.4f} ± {seY:.4f} ({zY:+.1f} s.e.);"
              f" exact E[X]={EX:.4f}, sample {xs.mean():.4f} ± {seX:.4f} ({zX:+.1f} s.e.);"
              f" P(X>0) sample {pos / samples:.4f} <= E[Y]{flag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=7)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--stages", default="1,2,3")
    args = ap.parse_args()
    t0 = time.time()
    ps = (Fraction(1, 2), Fraction(1, 3))
    stages = set(args.stages.split(","))
    if "1" in stages:
        stage1(args.max_n, args.workers, ps)
    if "2" in stages:
        stage2(args.workers)
    if "3" in stages:
        stage3(args.samples)
    print(f"\nviolations: {VIOL}; wall {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
