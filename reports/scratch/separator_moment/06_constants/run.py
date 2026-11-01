"""loop0011 item 06: beta_sep(c), beta_closed(c), beta_comb(c) against beta*(c)
and the fitted slopes on G(n, c/n).

Stages (all run by default; `--stage check|grid|constants|threshold|finite|draw`):
  check      the window/tilt recursions against the enumeration of every labelled
             graph at N <= 6; log_prob_rel_fast against log_prob_rel; the finite
             closed count against the enumeration of closed pairs at n <= 6 and
             Monte Carlo at n = 7, 8; the bracket's lower end reproduces beta*;
             Edwards-McDermid reproduces 0.183 / 0.458 / 0.656.
  grid       fitted rates in N (log-corrected fits over N = 100..400) of
             -log P_N(no component > uN) (untilted, u = 1/2: the separator
             count's rate) and of -log E[1[no component > uN] 2^kappa]
             (tilted, u = 0.5..0.8: the combined count's rate), on a grid of c'.
  constants  the table at c in {2, 2.5, 3, 4, 6, 8, 10, 12, 16, 20}: beta*,
             beta_closed, beta_sep (fitted / bracket / cited), beta_comb (fitted),
             the fitted slope where the pilot has one, Edwards-McDermid, the pair
             exponent's slope at beta* (nats per unit of beta), the kill.
  threshold  -log P_N(E_rel)/N at N <= 400 for c = 1.2, 1.386, 1.5, 2, 2.5
             against I_c(1/2): bounded away from 0 above 2 ln 2?
  finite     the finite form at n = 60, 120, c = 3..10: floors (< 1, < 0.01) of
             the pair, exact-size pair and separator bounds (item 05's inner.csv)
             beside the closed-pair and combined counts, in stacks.
  draw       beta against c (PNG).

Usage: nice -n 19 python3 reports/scratch/separator_moment/06_constants/run.py
Outputs here: rate_grid.csv, constants.csv, threshold.csv, finite.csv,
check.log, run.log, beta_vs_c.png.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import random
import sys
import time
from itertools import combinations
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

import learning.separator_moment as sm  # noqa: E402
from learning.separator_moment import LN2  # noqa: E402

LOG = open(os.path.join(HERE, "run.log"), "a")
C_TABLE = [2.0, 2.5, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0]
SLOPES = {2.0: 0.040, 3.0: 0.099, 4.0: 0.158, 6.0: 0.268, 8.0: 0.360, 10.0: 0.415}  # survey §7(d), fitted
N_FIT = [100, 150, 200, 250, 300, 350, 400]
U_GRID = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
CP_GRID = [round(1.0 + 0.25 * i, 2) for i in range(0, 77)]  # 1.00 .. 20.00


def log(msg: str = "") -> None:
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def logfit(xs, ys):
    x = np.array(xs, float)
    y = np.array(ys, float)
    A = np.vstack([x, np.log(x), np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef[0], coef[1], coef[2]


# ---------------------------------------------------------------- check

def labelled_graphs(N):
    pairs = list(combinations(range(N), 2))
    for mask in range(1 << len(pairs)):
        adj = [0] * N
        for i, (u, v) in enumerate(pairs):
            if mask >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        yield adj, bin(mask).count("1")


def enum_tilted_window(N, p, t_lo, t_hi, tilt):
    """E[1[some grouping of the components has a side of size in [t_lo, t_hi]] e^{tilt kappa}]."""
    full = (1 << N) - 1
    E = N * (N - 1) // 2
    tot = 0.0
    for adj, m in labelled_graphs(N):
        comps = sm.components(adj, full)
        sizes = [sm.popcount(cm) for cm in comps]
        reach = 1
        for s in sizes:
            reach |= reach << s
        ok = any(reach >> x & 1 for x in range(t_lo, t_hi + 1))
        if ok:
            tot += p ** m * (1 - p) ** (E - m) * math.exp(tilt * len(comps))
    return math.log(tot) if tot > 0 else -math.inf


def enum_closed_count(n, k, p):
    E = n * (n - 1) // 2
    tot = 0.0
    for adj, m in labelled_graphs(n):
        tot += p ** m * (1 - p) ** (E - m) * len(sm.closed_pairs(adj, k))
    return math.log(tot) if tot > 0 else -math.inf


def mc_closed_count(n, k, p, samples, seed):
    rng = random.Random(seed)
    xs = []
    for _ in range(samples):
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        xs.append(len(sm.closed_pairs(adj, k)))
    m = sum(xs) / samples
    se = (sum((x - m) ** 2 for x in xs) / (samples - 1) / samples) ** 0.5
    return m, se


def stage_check() -> None:
    log("== check ==")
    out = open(os.path.join(HERE, "check.log"), "w")
    def both(msg):
        log(msg)
        out.write(msg + "\n")
    t0 = time.time()
    worst = 0.0
    for N in range(1, 7):
        for p in (0.15, 0.4):
            lc = sm.log_connected(N, p)
            for t_lo in range(0, N + 1):
                for t_hi in range(t_lo, N + 1):
                    for tilt in (0.0, LN2):
                        a = sm.log_prob_bip(N, p, t_lo, lc, t_hi=t_hi, tilt=tilt)
                        b = enum_tilted_window(N, p, t_lo, t_hi, tilt)
                        d = abs(a - b) if math.isfinite(a) and math.isfinite(b) else (0.0 if a == b else math.inf)
                        worst = max(worst, d)
                        assert d < 1e-9, (N, p, t_lo, t_hi, tilt, a, b)
    both(f"window/tilt bipartition recursion = enumeration of every labelled graph at N <= 6 "
         f"(every window, tilt 0 and ln 2, p in {{0.15, 0.4}}): max |diff| {worst:.1e}  ok")
    worst = 0.0
    for N in range(1, 7):
        for p in (0.15, 0.4):
            lc = sm.log_connected(N, p)
            for M in range(1, N + 1):
                for tilt in (0.0, LN2):
                    a = sm.log_prob_rel(N, p, M, lc, tilt=tilt)
                    b = sm.log_prob_rel_fast(N, p, M, lc, tilt=tilt)
                    e = enum_tilted_window(N, p, 0, N, tilt) if M >= N else None
                    worst = max(worst, abs(a - b))
                    assert abs(a - b) < 1e-9, (N, p, M, tilt, a, b)
                    if e is not None:
                        assert abs(a - e) < 1e-9, (N, p, M, tilt, a, e)
    for N, cp in ((60, 3.0), (120, 5.0), (200, 8.0)):
        lc = sm.log_connected(N, cp / N)
        for M in (N // 3, N // 2, 2 * N // 3):
            for tilt in (0.0, LN2):
                a = sm.log_prob_rel(N, cp / N, M, lc, tilt=tilt)
                b = sm.log_prob_rel_fast(N, cp / N, M, lc, tilt=tilt)
                worst = max(worst, abs(a - b))
                assert abs(a - b) < 1e-7 * max(1.0, abs(a)), (N, cp, M, tilt, a, b)
    both(f"log_prob_rel_fast = log_prob_rel at N <= 6 (every M, both tilts) and at N = 60, 120, 200: "
         f"max |diff| {worst:.1e}  ok")
    worst = 0.0
    for n in range(2, 7):
        for p in (0.2, 0.5):
            for k in range(0, n):
                a = sm.log_closed_count(n, k, p)
                b = enum_closed_count(n, k, p)
                worst = max(worst, abs(a - b))
                assert abs(a - b) < 1e-9, (n, k, p, a, b)
    both(f"finite closed-pair count = enumeration of closed pairs over every labelled graph at n <= 6 "
         f"(every k, p in {{0.2, 0.5}}): max |diff| {worst:.1e}  ok")
    for n, k, p in ((7, 2, 0.3), (8, 3, 0.3), (8, 2, 0.5)):
        m, se = mc_closed_count(n, k, p, 20000, seed=n * 10 + k)
        a = math.exp(sm.log_closed_count(n, k, p))
        both(f"  Monte Carlo n={n} k={k} p={p}: E[X3] = {m:.4f} ± {se:.4f} (20,000 graphs) against the formula {a:.4f} "
             f"({abs(m - a) / se:.1f} s.e.)")
    for c in (2.0, 3.0, 4.0, 6.0, 10.0, 20.0):
        bs = sm.beta_star_gnp(c)
        bl = sm.beta_sep(c, lambda cp: sm.rate_bracket(cp)[0])
        assert abs(bs - bl) < 2e-6, (c, bs, bl)
    both("beta_sep with the bracket's lower end = beta* at c = 2, 3, 4, 6, 10, 20 (to 2e-6)  ok")
    em = [sm.edwards_mcdermid_poisson(c) for c in (3, 6, 10)]
    assert [round(x, 3) for x in em] == [0.183, 0.458, 0.656], em
    both(f"Edwards-McDermid Cor 5.2 on Poisson degrees: {[round(x, 3) for x in em]} at c = 3, 6, 10  ok")
    for c, b in ((6.0, 0.17), (10.0, 0.3), (3.0, 0.02)):
        a = (1 - b) / 2
        assert abs(sm.pair_exponent_beta(c, b) - sm.gnp_pair_rate(a, c)) < 1e-12
        assert abs(sm.closed_exponent(a, a, b, c, with_q=False) - sm.gnp_pair_rate(a, c)) < 1e-12
    both("pair_exponent_beta = gnp_pair_rate; closed exponent without the q terms at the corner = pair exponent  ok")
    both(f"check: {time.time() - t0:.0f} s")
    out.close()


# ---------------------------------------------------------------- grid

def grid_task(cp):
    rows = []
    for N in N_FIT:
        p = cp / N
        lc = sm.log_connected(N, p)
        row = {"cprime": cp, "N": N}
        row["rate_rel_half"] = -sm.log_prob_rel_fast(N, p, N // 2, lc) / N
        for u in U_GRID:
            M = int(round(u * N))
            row[f"tilted_u{u}"] = -sm.log_prob_rel_fast(N, p, M, lc, tilt=LN2) / N
        rows.append(row)
    return rows


def stage_grid(workers: int) -> None:
    log("== grid ==")
    t0 = time.time()
    with Pool(workers) as pool:
        results = pool.map(grid_task, CP_GRID)
    rows = [r for rs in results for r in rs]
    with open(os.path.join(HERE, "rate_grid.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    fits = []
    for cp in CP_GRID:
        sub = [r for r in rows if r["cprime"] == cp]
        Ns = [r["N"] for r in sub]
        fit = {"cprime": cp}
        I, b, a = logfit(Ns, [r["rate_rel_half"] * r["N"] for r in sub])
        fit["fit_rel_half"] = I
        fit["fit_rel_half_logcoef"] = b
        fit["rate_rel_half_N400"] = sub[-1]["rate_rel_half"]
        fit["ldp_half"] = sm.ldp_rate(cp, 0.5)
        for u in U_GRID:
            I, b, a = logfit(Ns, [r[f"tilted_u{u}"] * r["N"] for r in sub])
            fit[f"fit_tilted_u{u}"] = I
            fit[f"ldp_u{u}"] = sm.ldp_rate(cp, u)
        fits.append(fit)
    with open(os.path.join(HERE, "rate_fits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fits[0].keys()))
        w.writeheader()
        w.writerows(fits)
    log(f"grid: {len(CP_GRID)} c' x {len(N_FIT)} N x {1 + len(U_GRID)} events in {time.time() - t0:.0f} s on {workers} workers")
    log("c'    fit_rel(1/2)  LDP(1/2)  diff     item05_logfit  | tilted fit u=0.5  u=0.6  u=0.7  u=0.8   LDP u=0.6")
    item05 = {}
    p05 = os.path.join(HERE, "..", "05_inner", "rate_fits.csv")
    if os.path.exists(p05):
        for r in csv.DictReader(open(p05)):
            item05[float(r["cprime"])] = float(r["logfit_rel_slope_N100"])
    for fit in fits:
        cp = fit["cprime"]
        if cp in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0) or cp in item05:
            i5 = f"{item05[cp]:.4f}" if cp in item05 else "   -  "
            log(f"{cp:5.2f} {fit['fit_rel_half']:.4f}       {fit['ldp_half']:.4f}   {fit['fit_rel_half'] - fit['ldp_half']:+.4f}  {i5}         "
                f"| {fit['fit_tilted_u0.5']:.4f}  {fit['fit_tilted_u0.6']:.4f}  {fit['fit_tilted_u0.7']:.4f}  {fit['fit_tilted_u0.8']:.4f}   {fit['ldp_u0.6']:.4f}")


def load_fitted():
    """Interpolators: fitted untilted rate I_fit(c'), fitted tilted rate J_fit(c', u)."""
    fits = list(csv.DictReader(open(os.path.join(HERE, "rate_fits.csv"))))
    cps = np.array([float(r["cprime"]) for r in fits])
    I = np.array([float(r["fit_rel_half"]) for r in fits])
    J = np.array([[float(r[f"fit_tilted_u{u}"]) for u in U_GRID] for r in fits])
    from scipy.interpolate import RegularGridInterpolator
    Jint = RegularGridInterpolator((cps, np.array(U_GRID)), J, bounds_error=False, fill_value=None)

    def I_fit(cp):
        return max(0.0, float(np.interp(cp, cps, I)))

    def J_fit(cp, u):
        cp = min(max(cp, cps[0]), cps[-1])
        u = min(max(u, U_GRID[0]), U_GRID[-1])
        return float(Jint([[cp, u]])[0])

    return I_fit, J_fit


# ---------------------------------------------------------------- constants

def stage_constants() -> None:
    log("== constants ==")
    I_fit, J_fit = load_fitted()
    rows = []
    for c in C_TABLE:
        bs = sm.beta_star_gnp(c)
        b_cl = sm.beta_closed(c)
        b_sep_fit = sm.beta_sep(c, I_fit)
        b_sep_lo = sm.beta_sep(c, lambda cp: sm.rate_bracket(cp)[0])
        b_sep_hi = sm.beta_sep(c, lambda cp: sm.rate_bracket(cp)[1])
        b_sep_ldp = sm.beta_sep(c)
        b_comb = sm.beta_combined(c, J_fit)
        _, s_at = sm.combined_rate(c, b_comb, J_fit)
        bb = bs if bs > 0 else 1e-3
        slope = sm.exponent_slope_at(c, bb)
        cp = c * (1 - bs)
        row = {
            "c": c, "beta_star": bs, "beta_closed": b_cl,
            "beta_sep_fitted": b_sep_fit, "beta_sep_bracket_lo": b_sep_lo, "beta_sep_bracket_hi": b_sep_hi,
            "beta_sep_cited": b_sep_ldp, "beta_comb_fitted": b_comb, "comb_s_at_root": s_at,
            "slope_fitted": SLOPES.get(c, float("nan")), "edwards_mcdermid": sm.edwards_mcdermid_poisson(c),
            "pair_slope_at_beta_star": slope, "cprime_at_beta_star": cp,
            "I_fit_at_cp": I_fit(cp), "ldp_at_cp": sm.ldp_rate(cp, 0.5),
            "gain_sep_fitted": b_sep_fit - bs, "gain_sep_cited": b_sep_ldp - bs,
            "gain_closed": b_cl - bs, "gain_comb": b_comb - bs,
            "gain_sep_fitted_nats": (b_sep_fit - bs) * slope, "gain_closed_nats": (b_cl - bs) * slope,
            "gain_comb_nats": (b_comb - bs) * slope,
        }
        rows.append(row)
        log(f"c={c:5.1f}  beta*={bs:.4f}  closed={b_cl:.4f}  sep: fitted={b_sep_fit:.4f} bracket=[{b_sep_lo:.4f}, {b_sep_hi:.4f}] "
            f"cited={b_sep_ldp:.4f}  comb(fitted)={b_comb:.4f} (s'={s_at:.4f})  slope={row['slope_fitted']:.3f}  "
            f"E-M={row['edwards_mcdermid']:.3f}  dg/dbeta={slope:.2f}  c'={cp:.2f} I_fit={row['I_fit_at_cp']:.4f} LDP={row['ldp_at_cp']:.4f}")
    with open(os.path.join(HERE, "constants.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    g6 = [r for r in rows if r["c"] == 6.0][0]
    g10 = [r for r in rows if r["c"] == 10.0][0]
    log(f"KILL (brief): beta_sep(fitted) - beta* = {g6['gain_sep_fitted']:+.4f} at c=6, {g10['gain_sep_fitted']:+.4f} at c=10; "
        f"criterion < 0.02 at both: {'MET' if g6['gain_sep_fitted'] < 0.02 and g10['gain_sep_fitted'] < 0.02 else 'NOT MET'}")
    log(f"  closed: {g6['gain_closed']:+.4f} / {g10['gain_closed']:+.4f};  combined (fitted): {g6['gain_comb']:+.4f} / {g10['gain_comb']:+.4f}")
    # the combined exponent's profile in s' at the headline cells, for the report
    for c in (3.0, 6.0, 10.0):
        b = sm.beta_combined(c, J_fit)
        prof = [(s, sm.combined_exponent(c, b, s, J_fit)) for s in np.linspace(0, b, 11)]
        log(f"  combined exponent profile at c={c}, beta={b:.4f}: " + ", ".join(f"s'={s:.3f}:{v:+.4f}" for s, v in prof))


# ---------------------------------------------------------------- threshold

def thr_task(args):
    c, N = args
    p = c / N
    lc = sm.log_connected(N, p)
    rel = sm.log_prob_rel_fast(N, p, N // 2, lc)
    bip = sm.log_prob_bip(N, p, (N + 1) // 2, lc) if N <= 120 else float("nan")
    return {"c": c, "N": N, "log_prob_rel": rel, "rate_rel": -rel / N, "log_prob_bip": bip,
            "rate_bip": -bip / N if N <= 120 else float("nan")}


def stage_threshold(workers: int) -> None:
    log("== threshold ==")
    t0 = time.time()
    cs = [1.2, 2 * LN2, 1.5, 2.0, 2.5]
    Ns = [50, 100, 150, 200, 250, 300, 350, 400]
    with Pool(workers) as pool:
        rows = pool.map(thr_task, [(c, N) for c in cs for N in Ns])
    with open(os.path.join(HERE, "threshold.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log("c       I_c(1/2)   -log P_N(E_rel)/N at N = " + ", ".join(str(N) for N in Ns) + "   | log-fit N>=100 (I, b)   bip at 100")
    for c in cs:
        sub = [r for r in rows if r["c"] == c]
        I, b, a = logfit([r["N"] for r in sub if r["N"] >= 100], [-r["log_prob_rel"] for r in sub if r["N"] >= 100])
        bip100 = [r["rate_bip"] for r in sub if r["N"] == 100][0]
        log(f"{c:6.4f}  {sm.ldp_rate(c, 0.5):.5f}   " + "  ".join(f"{r['rate_rel']:.5f}" for r in sub)
            + f"   | {I:+.5f} ({b:+.2f})   {bip100:.5f}")
    log(f"threshold: {time.time() - t0:.0f} s")


# ---------------------------------------------------------------- finite

def finite_task(args):
    n, c, k = args
    p = c / n
    cache = {}
    closed = sm.log_closed_count(n, k, p)
    comb_rel = sm.log_combined_count(n, k, p, form="rel", logC_cache=cache)
    comb_bip = sm.log_combined_count(n, k, p, form="bip", logC_cache=cache) if n <= 60 else float("nan")
    return {"n": n, "c": c, "k": k, "logB_closed": closed, "logB_comb_rel": comb_rel, "logB_comb_bip": comb_bip}


def floors(vals: dict[int, float], thresh: float) -> int:
    """Largest k with log bound < log thresh (bounds increase with k); -1 if none."""
    best = -1
    for k in sorted(vals):
        if vals[k] < math.log(thresh):
            best = k
    return best


def stage_finite(workers: int) -> None:
    log("== finite ==")
    t0 = time.time()
    inner = list(csv.DictReader(open(os.path.join(HERE, "..", "05_inner", "inner.csv"))))
    tasks = []
    for n in (60, 120):
        for c in (3, 4, 6, 8, 10):
            ks = sorted({int(r["k"]) for r in inner if int(r["n"]) == n and float(r["c"]) == c})
            # around the floors only: pair floor - 2 .. sep floor + 6
            sep = {int(r["k"]): float(r["logB_sep"]) for r in inner if int(r["n"]) == n and float(r["c"]) == c}
            f_sep = floors(sep, 1.0)
            pair = {int(r["k"]): float(r["logB_pair"]) for r in inner if int(r["n"]) == n and float(r["c"]) == c}
            f_pair = floors(pair, 0.01)
            for k in ks:
                if max(0, f_pair - 2) <= k <= f_sep + 8:
                    tasks.append((n, c, k))
    with Pool(workers) as pool:
        rows = pool.map(finite_task, tasks)
    with open(os.path.join(HERE, "finite.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log("n    c   pair<1 pair<.01  xpair<1 xpair<.01  sep<1 sep<.01  closed<1 closed<.01  comb<1 comb<.01  comb_bip<1 comb_bip<.01   beta*n  minpw/LB")
    summary = []
    pilot = {(int(r["n"]), float(r["c"])): r for r in csv.DictReader(open(os.path.join(HERE, "..", "05_inner", "floors.csv")))}
    for n in (60, 120):
        for c in (3, 4, 6, 8, 10):
            sub = {int(r["k"]): r for r in rows if r["n"] == n and r["c"] == c}
            i5 = {int(r["k"]): r for r in inner if int(r["n"]) == n and float(r["c"]) == c}
            def fl(key, thr, src):
                return floors({k: float(r[key]) for k, r in src.items() if r[key] != "" and not (isinstance(r[key], float) and math.isnan(r[key]))}, thr)
            pr = pilot[(n, float(c))]
            row = {"n": n, "c": c,
                   "pair_lt1": fl("logB_pair", 1, i5), "pair_lt001": fl("logB_pair", 0.01, i5),
                   "xpair_lt1": fl("logB_xpair", 1, i5), "xpair_lt001": fl("logB_xpair", 0.01, i5),
                   "sep_lt1": fl("logB_sep", 1, i5), "sep_lt001": fl("logB_sep", 0.01, i5),
                   "closed_lt1": fl("logB_closed", 1, sub), "closed_lt001": fl("logB_closed", 0.01, sub),
                   "comb_lt1": fl("logB_comb_rel", 1, sub), "comb_lt001": fl("logB_comb_rel", 0.01, sub),
                   "comb_bip_lt1": fl("logB_comb_bip", 1, sub) if n <= 60 else -9,
                   "comb_bip_lt001": fl("logB_comb_bip", 0.01, sub) if n <= 60 else -9,
                   "beta_star_n": float(pr["beta_star_n"]), "min_pw_exact": pr["min_pw_exact"], "min_lb_unproved": pr["min_lb_unproved"]}
            summary.append(row)
            log(f"{n:4d} {c:3d}   {row['pair_lt1']:3d}   {row['pair_lt001']:3d}      {row['xpair_lt1']:3d}    {row['xpair_lt001']:3d}      "
                f"{row['sep_lt1']:3d}   {row['sep_lt001']:3d}      {row['closed_lt1']:3d}     {row['closed_lt001']:3d}       "
                f"{row['comb_lt1']:3d}   {row['comb_lt001']:3d}       {row['comb_bip_lt1']:3d}       {row['comb_bip_lt001']:3d}       "
                f"{row['beta_star_n']:5.1f}  {row['min_pw_exact']}/{row['min_lb_unproved']}")
    with open(os.path.join(HERE, "finite_floors.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    # the per-k decades at the two headline cells
    for n, c in ((60, 6), (60, 10), (120, 6), (120, 10)):
        sub = {int(r["k"]): r for r in rows if r["n"] == n and r["c"] == c}
        i5 = {int(r["k"]): r for r in inner if int(r["n"]) == n and float(r["c"]) == c}
        log(f"  n={n} c={c}: k: pair / xpair / sep / closed / comb (log10)")
        for k in sorted(sub):
            r = sub[k]; q = i5[k]
            cb = f"{r['logB_comb_bip'] / math.log(10):+.2f}" if n <= 60 else "  -  "
            log(f"    k={k:3d}: {float(q['logB_pair']) / math.log(10):+.2f} / {float(q['logB_xpair']) / math.log(10):+.2f} / "
                f"{float(q['logB_sep']) / math.log(10):+.2f} / {r['logB_closed'] / math.log(10):+.2f} / {r['logB_comb_rel'] / math.log(10):+.2f} (bip {cb})")
    log(f"finite: {len(tasks)} (n, c, k) in {time.time() - t0:.0f} s")


# ---------------------------------------------------------------- draw

def stage_draw() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(os.path.join(HERE, "constants.csv"))))
    cs = [float(r["c"]) for r in rows]
    col = {"star": "#2a78d6", "sep": "#eb6834", "closed": "#1baf7a", "comb": "#eda100", "slope": "#e87ba4", "em": "#6250d6"}
    text, muted, surface = "#0b0b0b", "#52514e", "#fcfcfb"
    f = lambda key: [float(r[key]) for r in rows]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.6), facecolor=surface, gridspec_kw={"width_ratios": [1.15, 1]})
    for a_ in (ax, bx):
        a_.set_facecolor(surface)
        for s in ("top", "right"):
            a_.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            a_.spines[s].set_color(muted)
        a_.tick_params(colors=muted)
        a_.grid(axis="y", color="#e6e5e1", lw=0.8)
        a_.set_axisbelow(True)
        a_.set_xlabel("c  (mean degree of G(n, c/n))", color=text)
    # left: the constants against c
    ax.fill_between(cs, f("beta_sep_bracket_lo"), f("beta_sep_bracket_hi"), color=col["sep"], alpha=0.12, lw=0,
                    label="bracket on β_sep (analytic ends)")
    ax.plot(cs, f("edwards_mcdermid"), color=col["em"], lw=2, ls=(0, (4, 2)), label="Edwards & McDermid 2015 (published upper line)")
    sc = [(float(r["c"]), float(r["slope_fitted"])) for r in rows if r["slope_fitted"] not in ("nan", "")]
    ax.plot([x for x, _ in sc], [y for _, y in sc], ls="none", marker="o", ms=7, mfc=col["slope"], mec=surface, mew=1.5,
            label="fitted slope of exact pathwidth (pilot)")
    ax.plot(cs, f("beta_closed"), color=col["closed"], lw=2, label="β_closed (closed pairs)")
    ax.plot(cs, f("beta_sep_cited"), color=col["sep"], lw=2, label="β_sep (separators; cited LDP rate)")
    ax.plot(cs, f("beta_star"), color=col["star"], lw=2, label="β* (pairs, on record)")
    for x, name in ((4 * LN2, "4 ln 2"), (2 * LN2, "2 ln 2")):
        ax.axvline(x, color=muted, lw=1, ls=":")
    ax.text(2 * LN2 - 0.1, 0.62, "2 ln 2", color=muted, fontsize=8, ha="right", rotation=90, va="bottom")
    ax.text(4 * LN2 + 0.1, 0.62, "4 ln 2", color=muted, fontsize=8, ha="left", rotation=90, va="bottom")
    ax.text(cs[-1] + 0.3, f("edwards_mcdermid")[-1], "E–M", color=text, fontsize=9, va="center")
    ax.text(cs[-1] + 0.3, f("beta_star")[-1], "β*, β_sep,\nβ_closed", color=text, fontsize=8, va="center")
    ax.set_xlim(1, 22.5)
    ax.set_ylim(0, 0.85)
    ax.set_ylabel("β  (pathwidth per vertex)", color=text)
    ax.legend(loc="lower right", fontsize=7.5, frameon=False)
    # right: the gains over β*
    gap = [(float(r["c"]), float(r["slope_fitted"]) - float(r["beta_star"])) for r in rows if r["slope_fitted"] not in ("nan", "")]
    bx.fill_between(cs, [0] * len(cs), [h - s for h, s in zip(f("beta_sep_bracket_hi"), f("beta_star"))],
                    color=col["sep"], alpha=0.12, lw=0, label="bracket on β_sep − β*")
    bx.plot([x for x, _ in gap], [y for _, y in gap], ls="none", marker="o", ms=7, mfc=col["slope"], mec=surface, mew=1.5,
            label="fitted slope − β* (the gap to the data)")
    bx.plot(cs, [v - s for v, s in zip(f("beta_comb_fitted"), f("beta_star"))], color=col["comb"], lw=2,
            label="β_comb − β* (combined; fitted tilted rate)")
    bx.plot(cs, [v - s for v, s in zip(f("beta_closed"), f("beta_star"))], color=col["closed"], lw=2, label="β_closed − β*")
    bx.plot(cs, [v - s for v, s in zip(f("beta_sep_cited"), f("beta_star"))], color=col["sep"], lw=2, label="β_sep − β* (cited LDP rate)")
    bx.plot(cs, [v - s for v, s in zip(f("beta_sep_fitted"), f("beta_star"))], color=col["sep"], lw=1, ls=(0, (2, 2)),
            label="β_sep − β* (fitted rate)")
    bx.axhline(0.02, color=muted, lw=1, ls=":")
    bx.text(21.3, 0.0215, "kill: 0.02", color=muted, fontsize=8, ha="right", va="bottom")
    bx.axhline(0, color=muted, lw=0.8)
    bx.set_xlim(1, 21.5)
    bx.set_ylim(-0.012, 0.11)
    bx.set_ylabel("gain over β*  (in β)", color=text)
    bx.legend(loc="center right", fontsize=7.5, frameon=False, bbox_to_anchor=(1.0, 0.42))
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "beta_vs_c.png"), dpi=160, facecolor=surface)
    log("drew beta_vs_c.png")


# ---------------------------------------------------------------- main

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    load1 = os.getloadavg()[0]
    workers = min(a.workers, 4 if load1 > 24 else 8)
    log(f"=== item 06 run {time.strftime('%Y-%m-%d %H:%M')} stage={a.stage} workers={workers} load={load1:.1f} ===")
    if a.stage in ("all", "check"):
        stage_check()
    if a.stage in ("all", "grid"):
        stage_grid(workers)
    if a.stage in ("all", "constants"):
        stage_constants()
    if a.stage in ("all", "threshold"):
        stage_threshold(workers)
    if a.stage in ("all", "finite"):
        stage_finite(workers)
    if a.stage in ("all", "draw"):
        stage_draw()
