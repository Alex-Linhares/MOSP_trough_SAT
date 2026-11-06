"""Numeric consistency of the parameters Appendix D fixes (D.4.2, (D.4)-(D.6),
Lemma D.3's child size, (D.11), (D.15), D.4.7) and the degree hypothesis for the
D.2 network (item 4).  Exact integer arithmetic except where a quantity is a
real-valued bound (logs); every such line says so.

Run: python3 -I parameters.py
"""
from __future__ import annotations
import os, sys
from math import ceil, floor, log2, sqrt, pi, log, isqrt, comb
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

R = 64
EPS_INV = 128 * 1024          # eps = 1/131072 = 2^-17
LN2 = log(2)


def lam(s):
    return ceil(log2(s)) if s > 1 else 1


def params_at(log2s):
    """Parameters as functions of lambda = ceil(log2 s); we pass log2 s directly for huge s."""
    L_ = log2s
    u0 = (L_ // EPS_INV)                # floor(eps*lambda)
    a0 = 2 * u0
    return u0, a0


def section_thresholds():
    print("== Thresholds implied by the fixed constants (exact integer arithmetic) ==")
    lam_u1 = EPS_INV                   # smallest lambda with u_0 = floor(eps*lambda) >= 1
    print(f"  u_0 = floor(eps*lambda) >= 1 needs lambda >= {lam_u1} = 2^17, i.e. s > 2^{lam_u1 - 1}")
    # (D.5) u >= lambda^{4/5}:  eps*lambda >= lambda^{0.8}  <=> lambda^{0.2} >= 2^17 <=> lambda >= 2^85
    lam_d5 = EPS_INV ** 5
    print(f"  (D.5) u_0 >= lambda^(4/5) needs lambda >= eps^-5 = 2^85 = {lam_d5}, i.e. s > 2^(2^85 - 1)")
    # a <= 4 eps lambda always; L = 2^a, Darr = r^{2a} = 2^{12 a} <= s^{1/1000} <=> 12 a <= log2(s)/1000
    # with a <= 4 eps lambda: 48 eps lambda <= lambda/1000 <=> 48/131072 <= 1/1000 : 0.000366 <= 0.001  OK
    print(f"  (D.5) D_arr = r^(2a) = 2^(12a) <= s^(1/1000): with a <= 4 eps lambda the exponent ratio is "
          f"48/131072 = {48/EPS_INV:.6f} <= 1/1000: holds for all s once a <= 4 eps lambda (note r^(2a), not r*2^a)")
    # Depth bound d <= log2(lambda)/6 + O(1): from H < M <= C s 8^-d and H = ceil(s/floor(sqrt(lambda)))
    print("  depth: H < C s 8^-d  <=>  8^d < C floor(sqrt(lambda))  <=>  d < log2(lambda)/6 + log2(C)/3  (consistent)")
    # 6M/r = 3M/32 < M/8
    print(f"  Lemma D.3 child size: 6M/r with r = 64 is 6/64 = 3/32 = {3/32:.5f} < 1/8 = {1/8:.5f}: consistent")
    # (D.6) at the first s where the recursion is defined (lambda = 2^17, u0 = 1, a0 = 2):
    u0, a0 = params_at(EPS_INV)
    L = 2 ** a0
    Darr = R ** (2 * a0)
    print(f"  at lambda = 2^17: u_0 = {u0}, a_0 = {a0}, L = {L}, D_arr = {Darr} = 2^{int(log2(Darr))}, "
          f"2 D_arr^2 Delta = 2^{1 + 2 * int(log2(Darr))} * s^0.9; H ~ s/{floor(sqrt(EPS_INV))};"
          f" (D.6) M >= 2 D_arr^2 Delta needs s^0.1 >= 2^49 * 362, i.e. s >= 2^{ceil(10 * (49 + log2(362)))}: fine at s ~ 2^131072")


def child_count_bound(M, u, a, p, i=0):
    """The text's own count estimate for the number of exponent tuples at a node of valuation i
    (D.4.5, the display after (D.15)): exp(theta p_t + (6M/D) sum_j -ln(1-e^{-theta j})), in bits
    (real arithmetic, log-domain where D = 2^{a-i} is astronomically large).
    Returns (bits at the optimal theta = 2 pi sqrt(M p_t / D), bits numerically minimised,
    p_t (or None if it overflows a float), N = 6M/D, bits at the text's theta = sqrt(M/(D p_t)))."""
    from math import ldexp
    h = ceil(3 * M / u)
    ptD = 8 * h + ldexp(float(p + 8 * M * (a + 1)), -(a - i))     # p_t / D
    try:
        pt = ldexp(ptD, a - i)
    except OverflowError:
        pt = None
    N = ldexp(6.0 * M, -(a - i))
    theta = sqrt(M / ptD) / ldexp(1.0, a - i) if a - i < 1000 else 0.0   # text's theta = sqrt(M/(D p_t))
    bits_opt = 2 * pi * sqrt(ptD * M) / LN2
    bits_paper = (sqrt(M * ptD) * (1 + pi ** 2)) / LN2                 # = theta p_t + N (pi^2/6)/theta at the text's theta
    if pt is None or N < 1e-300:
        return bits_opt, bits_opt, pt, N, bits_paper

    def exact_series(th):
        """sum_{j>=1} -ln(1 - e^{-th j}), by the modular identity
        = pi^2/(6 th) + (1/2) ln(th/(2 pi)) - th/24 + sum_{j>=1} -ln(1 - e^{-4 pi^2 j / th})
        (the last sum is < 1e-12 for th < 1; for th >= 1 we sum directly)."""
        from math import expm1
        if th >= 1.0:
            s_, j = 0.0, 1
            while True:
                term = -log(-expm1(-th * j))
                s_ += term
                if term < 1e-18:
                    break
                j += 1
            return s_
        tail = 0.0
        j = 1
        while True:
            x = 4 * pi * pi * j / th
            if x > 700:
                break
            tail += -log(-expm1(-x))
            j += 1
        return pi ** 2 / (6 * th) + 0.5 * log(th / (2 * pi)) - th / 24 + tail

    # numeric minimisation over theta of theta*pt + N*exact_series(theta)
    best = None
    th = max(theta, 1e-300) / 8
    if th == 0:
        return bits_opt, bits_opt, pt, N, bits_paper
    for _ in range(200):
        val = th * pt + N * exact_series(th)
        if best is None or val < best[0]:
            best = (val, th)
        th *= 1.03
    return bits_opt, best[0] / LN2, pt, N, bits_paper


def weight_one_lower_bound_bits(N, pt):
    """log2 of the number of tuples using weight-1 modes only: C(N + pt - 1, N) (exact combinatorics,
    returned as a float of its log2)."""
    from math import lgamma
    N = int(N)
    return (lgamma(N + pt) - lgamma(N + 1) - lgamma(pt)) / LN2


def exact_tuple_count_bits(N, pt):
    """Exact number of tuples (beta_Z) over N variables of each weight w >= 1 with sum w beta < pt,
    via n p_n = N sum_{k=1}^n sigma(k) p_{n-k}; exact big integers; returns log2 of the count."""
    N = int(N)
    sigma = [0] * pt
    for d in range(1, pt):
        for m in range(d, pt, d):
            sigma[m] += d
    pcoef = [0] * pt
    pcoef[0] = 1
    for n in range(1, pt):
        acc = 0
        for k in range(1, n + 1):
            acc += sigma[k] * pcoef[n - k]
        assert (N * acc) % n == 0
        pcoef[n] = N * acc // n
    total = sum(pcoef)
    return log2(total), total


def section_mode_counts():
    print("== (D.15): number of exponent tuples at depth 0, with the parameters of (D.4) ==")
    print("  (M = number of wires at the root; p = root precision n+1; i = 0 node, D = L = 2^{a_0}; h = ceil(3M/u_0))")
    print("  Columns: lambda, u_0, a_0, p_t/M, N per weight = 6M/D, the text's estimate exp(theta p_t + (6M/D) sum_j -ln(1-e^{-theta j}))"
          " in bits per wire at its optimal theta (= 2 pi sqrt(M p_t/D)), at the text's theta = sqrt(M/(D p_t)), its numeric minimum,"
          " and a rigorous lower bound on the tuple count (weight-1 modes only, C(N+p_t-1, N)) in bits per wire")
    for log2lam in (17, 18, 20, 22, 24, 26, 28, 30, 32, 36, 40):
        lam_ = 2 ** log2lam
        u0, a0 = params_at(lam_)
        M = 10 ** 6  # the ratio bits/M is what matters; p = M/45+1 as for 3-CNF at density 4.26 (M ~ 45 n)
        p = M // 45 + 1
        bp, bn, pt, N, braw = child_count_bound(M, u0, a0, p)
        w1 = weight_one_lower_bound_bits(N, pt) if (N >= 1 and pt is not None) else 0.0
        ptM = f"{pt / M:10.3g}" if pt is not None else "  >1e308  "
        print(f"  lambda=2^{log2lam:<3d} u_0={u0:<8d} a_0={a0:<9d} p_t/M={ptM} N/M={N / M:10.3g} "
              f"bound(opt theta)={bp / M:8.3f} bits/wire (text's theta {braw / M:8.3f}; numeric min {bn / M:8.3f}); weight-1 lower bound={w1 / M:8.3f} bits/wire")
    print("  For comparison: direct summation of a call with M wires costs 2^M = 1.000 bits/wire; the trivial 2^n")
    print("  algorithm is 1/45 = 0.022 bits/wire for 3-CNF at density 4.26 (M ~ 45 n, computed in section_degree).")
    # where does the paper's bound drop below 1 bit/wire and below 1/45?
    c0 = 2 * pi * sqrt(24) / LN2     # large-M limit of the optimised estimate: bits/wire = c0 / sqrt(u_0)
    check = child_count_bound(10 ** 9, 100, 200, 10 ** 9 // 45 + 1)[0] / 10 ** 9 * sqrt(100)
    print(f"  large-M limit of the optimised estimate: {c0:.2f} / sqrt(u_0) bits per wire (check at M = 1e9, u = 100: {check:.2f})")
    for target, name in ((1.0, "2^M (direct summation of the same call)"), (1 / 45, "2^n (3-CNF, m = 4.26 n, M ~ 45 n)")):
        u = ceil((c0 / target) ** 2)
        print(f"  estimate < {name} needs u_0 > {u}, i.e. lambda >= {u * EPS_INV:.3g}, s >= 2^{u * EPS_INV:.3g}")
    # exact counts at a small M to show the slack of the bound
    print("  Exact tuple counts (big-integer, small M) against the paper's bound, u_0 = 1, a_0 = 2 (lambda = 2^17 parameters):")
    for M in (4, 8, 16):
        u0, a0 = 1, 2
        p = M // 45 + 1
        bp, bn, pt, N, braw = child_count_bound(M, u0, a0, p)
        bits, total = exact_tuple_count_bits(N, int(pt))
        print(f"    M={M:3d}: p_t={pt}, N={int(N)} modes per weight, exact #tuples = 2^{bits:.1f}  (paper's bound 2^{bp:.1f}; direct summation 2^{M})")


def section_exponent_sum():
    print("== D.4.7 exponent bookkeeping: sum over depth of the (D.15) bound, constants explicit ==")
    print("  (D.15) with p_t <= (24 + o(1)) M D/u gives bits <= 2 pi sqrt(24) / ln 2 * M/sqrt(u) = "
          f"{2 * pi * sqrt(24) / LN2:.2f} M/sqrt(u) per node; M_d <= C s 8^-d, u_d = floor(eps lambda / 2^d):")
    c0 = 2 * pi * sqrt(24) / LN2
    geo = sum(8 ** (-d) * sqrt(2 ** d) for d in range(60))
    print(f"  sum_d 8^-d sqrt(2^d) = {geo:.4f}, so total <= {c0:.2f} * {geo:.4f} / sqrt(eps) * C s / sqrt(lambda) = "
          f"{c0 * geo / sqrt(1 / EPS_INV):.0f} C s / sqrt(lambda) bits (plus H = s/sqrt(lambda) for the leaf and poly factors)")
    print("  i.e. the proved exponent is O(s/sqrt(log s)) with a constant of order 10^4 C (C >= 4k for the D.2 network),")
    for k, dens in ((3, 4.26), (3, 1.0), (2, 1.0)):
        C = 4 * k
        # s/sqrt(lambda) * const < n  with s = (1+dens) n  => sqrt(lambda) > const*(1+dens)
        const = c0 * geo / sqrt(1 / EPS_INV) * C
        lam_needed = (const * (1 + dens)) ** 2
        print(f"    k={k}, m={dens}n: bound < 2^n needs sqrt(lambda) > {const * (1 + dens):.3g}, lambda > {lam_needed:.3g}, s > 2^{lam_needed:.3g}")
    print("  (these use only the explicit constants; C and the 'sufficiently large s' thresholds make the true crossover larger)")


def section_degree():
    print("== Item 4: degree hypothesis for the D.2 network with one variable in every clause ==")
    from d2_cnf_network import build_d2_network
    # small n: build literally
    worst = 0
    for n in range(2, 13):
        for k in (2, 3, 4):
            if k > n:
                continue
            m = 3 * n
            import random
            rng = random.Random(n * 7 + k)
            cl = []
            for _ in range(m):
                others = rng.sample(range(2, n + 1), k - 1)
                cl.append([1] + [v if rng.random() < 0.5 else -v for v in others])
            net, unused, e0 = build_d2_network(n, cl)
            netpre, _, _ = build_d2_network(n, cl, subdivide=False)
            s = n + m
            worst = max(worst, netpre.max_degree())
            assert netpre.max_degree() <= max(k, 3)
            assert net.max_degree() <= max(k, 3)
            assert net.max_degree() <= ceil(s ** 0.9)
            assert net.n_edges <= 4 * k * s
    print(f"  n = 2..12, k = 2..4, m = 3n, x_1 in every clause: max degree before/after subdivision <= max(k,3) "
          f"(observed max {worst}); edges <= 4 k s; bipartite. The equality tree (d-2 trivalent vertices) is the splitting step.")
    # formula for large n: degree = max(k,3) always; ceil(s^0.9) >= 3 for s >= 3
    fails = [s for s in range(1, 200) if ceil(s ** 0.9) < 3]
    print(f"  ceil(s^0.9) < 3 only for s in {fails}; for n from 10 to 10^6 (s = n + m >= 10) the hypothesis holds with k = 3.")
    for k in (3, 5, 10, 20):
        smin = next(s for s in range(1, 10 ** 6) if ceil(s ** 0.9) >= max(k, 3))
        print(f"  k = {k}: max degree max(k,3) = {max(k, 3)} <= ceil(s^0.9) from s = {smin}")
    # exact edge count constant for 3-CNF at density 4.26 (all variables with d >= 3)
    n = 1000; m = 4260; k = 3
    ports = k * m
    # if all variable degrees >= 3: internal tree edges = sum(d_v - 3) = ports - 3n
    edges = 2 * (ports + ports - 3 * n)
    print(f"  3-CNF, m = 4.26 n, all variables with >= 3 occurrences: wires after subdivision = 2(2km - 3n) = {edges / n:.2f} n = {edges / (n + m):.2f} s")


if __name__ == "__main__":
    section_thresholds()
    section_mode_counts()
    section_exponent_sum()
    section_degree()
