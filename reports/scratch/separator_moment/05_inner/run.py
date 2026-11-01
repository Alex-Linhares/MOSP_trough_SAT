"""loop0011 item 05: the inner probability P_N(E_bip) of G(N, p), exactly.

Stages (all run by default; `--stage check|inner|rates|draw`):
  check  Gilbert's recursion against enumeration (j <= 6) and Monte Carlo (j = 20);
         the partition law sums to 1 (N <= 20); P_N(E_bip) against enumeration of
         every labelled graph (N <= 7) and Monte Carlo (N = 20, p = 0.1);
         P(E_bip) <= P(E_relax) <= 1 and P(E_bip) <= product bound on a grid.
  inner  at the pilot cells (n = 60, 120; c = 3, 4, 6, 8, 10), every k: the pair
         bound of finite_bound.py, the exact-size pair bound, the separator bound
         C(n, k) P_N(E_bip) and the relaxed bound C(n, k) P_N(E_relax); floors at
         < 1 and < 0.01; the pilot's observed minima / solver lower bounds.
  rates  -log P_N(E_bip)/N for N = 20..--max-N at c' in {2, 3, 4, 5, 6.6, 8, 10},
         -log P_N(E_relax)/N to N = 400; linear fits (intercept free, "fitted");
         the analytic bracket and the LDP rate I_{c'}(1/2) of item 01.
  draw   the figure of -log P/N against N with the bracket (PNG).

Usage: nice -n 19 python3 reports/scratch/separator_moment/05_inner/run.py --max-N 60
Outputs: inner.csv, floors.csv, rates.csv, rate_fits.csv, run.log, rates.png (here).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import os
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from learning.separator_moment import (  # noqa: E402
    log_connected, log_connected_enum, log_connected_mc, log_prob_bip, log_prob_bip_enum,
    log_prob_bip_mc, log_prob_partition, log_prob_rel, log_product_bound, partitions,
)
from learning.separator_moment import _lse  # noqa: E402

LOG = open(os.path.join(HERE, "run.log"), "a")
LN2 = math.log(2)


def log(msg: str = "") -> None:
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def ldp_rate_half(c: float) -> float:
    """`I_{c}^β(1/2)` from item 01's rate_check.py (O'Connell's rate as restated by Puhalskii)."""
    spec = importlib.util.spec_from_file_location("rate_check", os.path.join(HERE, "..", "rate_check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.I(c, 0.5)


def bracket(cp: float) -> tuple[float, float, float, float]:
    """(lower, upper, c'/4, thinning): the plan's analytic routes for the rate of E_bip."""
    lower = max(0.0, cp / 4 - LN2)
    quarter = cp / 4
    thinning = cp / 2 - LN2 + LN2 * math.log(2 * LN2 / cp) if cp > 2 * LN2 else 0.0
    return lower, min(quarter, thinning if cp > 2 * LN2 else quarter), quarter, thinning


# ---------------------------------------------------------------- check

def stage_check() -> None:
    log("== check ==")
    t0 = time.time()
    for p in (0.1, 0.3, 0.5):
        lc = log_connected(6, p)
        for j in range(1, 7):
            le = log_connected_enum(j, p)
            assert abs(lc[j] - le) < 1e-9, (j, p, lc[j], le)
    log(f"C_j (Gilbert, mpmath) = enumeration of all labelled graphs at j <= 6, p in {{0.1, 0.3, 0.5}}: ok "
        f"(counts at p = 1/2: {[round(math.exp(log_connected(6, 0.5)[j]) * 2 ** (j * (j - 1) // 2)) for j in range(1, 7)]})")
    for p in (0.15, 0.3):
        lc = log_connected(20, p)[20]
        mc, se = log_connected_mc(20, p, 20000, seed=5)
        z = (math.exp(lc) - math.exp(mc)) / se
        log(f"C_20({p}) = {math.exp(lc):.5f}; Monte Carlo 20,000 networkx graphs: {math.exp(mc):.5f} +- {se:.5f} (z = {z:+.2f})")
        assert abs(z) < 4
    for N in (1, 2, 5, 10, 15, 20):
        for p in (0.02, 0.1, 0.5):
            lc = log_connected(N, p)
            tot = _lse([log_prob_partition(l, N, p, lc) for l in partitions(N)])
            assert abs(tot) < 1e-9, (N, p, tot)
    log("sum over all partitions of P(component sizes = lambda) = 1 at N in {1, 2, 5, 10, 15, 20}, p in {0.02, 0.1, 0.5}: ok "
        f"(p(20) = {sum(1 for _ in partitions(20))} partitions)")
    for N in range(1, 8):
        for p in ((0.1, 0.3, 0.5) if N < 7 else (0.2,)):
            for t in (range(N + 1) if N < 7 else ((N + 1) // 2,)):
                a = log_prob_bip(N, p, t)
                b = log_prob_bip_enum(N, p, t)
                assert (a == b == -math.inf) or abs(a - b) < 1e-9, (N, p, t, a, b)
                r = log_prob_rel(N, p, max(t, N - t))
                assert a <= r + 1e-12
                assert a <= log_product_bound(N, p, t) + 1e-12
    log("P_N(E_bip) = enumeration of all labelled graphs, N <= 6 every t and p in {0.1, 0.3, 0.5}; N = 7, t = 4, p = 0.2 (2,097,152 graphs): ok; "
        "P(E_bip) <= P(E_relax) and <= C(N, t)(1 - p)^{t(N - t)} there: ok")
    N, p = 20, 0.1
    ex = log_prob_bip(N, p)
    mc, se = log_prob_bip_mc(N, p, samples=20000, seed=11)
    z = (math.exp(ex) - math.exp(mc)) / se
    log(f"P_20(E_bip) at p = 0.1, t = 10: exact {math.exp(ex):.5f}; Monte Carlo 20,000 graphs {math.exp(mc):.5f} +- {se:.5f} (z = {z:+.2f})")
    assert abs(z) < 4
    rel = log_prob_rel(N, p, 10)
    log(f"P_20(E_relax) at p = 0.1, M = 10: exact {math.exp(rel):.5f}; product bound {math.exp(log_product_bound(N, p)):.5f}")
    bad = 0
    for N in (10, 20, 30, 40, 60):
        for cp in (1, 2, 3, 5, 8, 12):
            if cp >= N:
                continue
            p = cp / N
            lc = log_connected(N, p)
            for t in range(0, N + 1, max(1, N // 5)):
                a = log_prob_bip(N, p, t, lc)
                r = log_prob_rel(N, p, max(t, N - t), lc)
                bad += not (a <= r + 1e-9 <= 1e-9 and a <= log_product_bound(N, p, t) + 1e-9)
    log(f"P(E_bip) <= P(E_relax) <= 1 and P(E_bip) <= product bound on N in {{10..60}}, c' in {{1..12}}, six t each: {bad} violations")
    assert bad == 0
    log(f"check: {time.time() - t0:.0f} s")


# ---------------------------------------------------------------- inner

def log_binom(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def logB_pair(n: int, k: int, p: float) -> float:
    """finite_bound.py: C(n,t) C(n-t,t-1) (1-p)^(t(t-1)), t = (n-k+1)//2 (the Lean convention)."""
    t = (n - k + 1) // 2
    return log_binom(n, t) + log_binom(n - t, t - 1) + t * (t - 1) * math.log1p(-p)


def cell_task(args):
    n, c = args
    p = c / n
    lc = log_connected(n, p)
    rows = []
    t0 = time.time()
    for k in range(0, n):
        N = n - k
        t = (N + 1) // 2
        lck = log_binom(n, k)
        lbip = log_prob_bip(N, p, t, lc)
        lrel = log_prob_rel(N, p, t, lc)
        rows.append(dict(n=n, c=c, k=k, N=N, t=t, p=p,
                         logB_pair=logB_pair(n, k, p),
                         logB_xpair=lck + log_product_bound(N, p, t),
                         logB_sep=lck + lbip, logB_rel=lck + lrel,
                         log_prob_bip=lbip, log_prob_rel=lrel, log_prod=log_product_bound(N, p, t)))
    return n, c, rows, time.time() - t0


def pilot_min(n: int, c: float):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "reports", "scratch", "gnp_pilot", "results.csv"))))
    rs = [r for r in rows if int(r["n"]) == n and float(r["c"]) == c]
    exact = [int(r["width"]) for r in rs if r["status"] != "upper"]
    lows = [int(r["lower"]) for r in rs if r["status"] == "upper"]
    return len(rs), len(exact), (min(exact) if exact else None), (min(lows) if lows else None)


def floors(rows, key, thresh):
    ks = [r["k"] for r in rows if r[key] < math.log(thresh)]
    return max(ks) if ks else -1


def beta_star(c: float) -> float:
    from learning.separator_moment import beta_star_gnp
    return beta_star_gnp(c)


def stage_inner(workers: int) -> None:
    log("== inner: the finite bounds at the pilot cells ==")
    cells = [(n, c) for n in (60, 120) for c in (3, 4, 6, 8, 10)]
    t0 = time.time()
    with Pool(workers) as pool:
        results = pool.map(cell_task, cells)
    allrows = []
    for n, c, rows, dt in results:
        allrows.extend(rows)
        log(f"  cell n={n} c={c}: {len(rows)} k in {dt:.0f} s")
    with open(os.path.join(HERE, "inner.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys()))
        w.writeheader()
        w.writerows(allrows)
    fl = []
    log(f"\n{'n':>4} {'c':>3} | {'pair<1':>6} {'pair<.01':>8} | {'xpair<1':>7} {'xpair<.01':>9} | {'sep<1':>5} {'sep<.01':>7} | {'rel<1':>5} {'rel<.01':>7} | {'beta*n':>6} | {'graphs':>6} {'exact':>5} {'min pw':>6} {'min LB':>6} | {'(lgBpair-lgBsep)/n @pair.01':>26} {'@sep.01':>8} {'(lgBxpair-lgBsep)/n @sep.01':>26}")
    for n, c, rows, _ in results:
        d = dict(n=n, c=c)
        for key, name in (("logB_pair", "pair"), ("logB_xpair", "xpair"), ("logB_sep", "sep"), ("logB_rel", "rel")):
            d[f"{name}_lt1"] = floors(rows, key, 1.0)
            d[f"{name}_lt001"] = floors(rows, key, 0.01)
        d["beta_star_n"] = beta_star(c) * n
        g, e, mn, ml = pilot_min(n, float(c))
        d.update(graphs=g, exact=e, min_pw_exact=mn, min_lb_unproved=ml)
        by_k = {r["k"]: r for r in rows}
        kp = d["pair_lt001"]
        ks = d["sep_lt001"]
        d["gain_pair_sep_per_n_at_pair001"] = (by_k[kp]["logB_pair"] - by_k[kp]["logB_sep"]) / n if kp >= 0 else float("nan")
        d["gain_pair_sep_per_n_at_sep001"] = (by_k[ks]["logB_pair"] - by_k[ks]["logB_sep"]) / n if ks >= 0 else float("nan")
        d["gain_xpair_sep_per_n_at_sep001"] = (by_k[ks]["logB_xpair"] - by_k[ks]["logB_sep"]) / n if ks >= 0 else float("nan")
        d["gain_rel_sep_per_n_at_sep001"] = (by_k[ks]["logB_rel"] - by_k[ks]["logB_sep"]) / n if ks >= 0 else float("nan")
        fl.append(d)
        log(f"{n:>4} {c:>3} | {d['pair_lt1']:>6} {d['pair_lt001']:>8} | {d['xpair_lt1']:>7} {d['xpair_lt001']:>9} | {d['sep_lt1']:>5} {d['sep_lt001']:>7} | {d['rel_lt1']:>5} {d['rel_lt001']:>7} | {d['beta_star_n']:>6.2f} | {g:>6} {e:>5} {str(mn):>6} {str(ml):>6} | {d['gain_pair_sep_per_n_at_pair001']:>26.4f} {d['gain_pair_sep_per_n_at_sep001']:>8.4f} {d['gain_xpair_sep_per_n_at_sep001']:>26.4f}")
    with open(os.path.join(HERE, "floors.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fl[0].keys()))
        w.writeheader()
        w.writerows(fl)
    log("\nn = 60 and 120, c = 10, around the floors (log10 of each bound):")
    for n, c, rows, _ in results:
        if c != 10:
            continue
        lo = max(0, floors(rows, "logB_sep", 0.01) - 6)
        for r in rows[lo:lo + 10]:
            log(f"  n={n} k={r['k']:>3} N={r['N']:>3} t={r['t']:>3}  log10: pair {r['logB_pair'] / math.log(10):>8.3f}  xpair {r['logB_xpair'] / math.log(10):>8.3f}  sep {r['logB_sep'] / math.log(10):>8.3f}  rel {r['logB_rel'] / math.log(10):>8.3f}   inner: prod {r['log_prod']:>9.3f} bip {r['log_prob_bip']:>9.3f} rel {r['log_prob_rel']:>9.3f}")
    log(f"inner: {time.time() - t0:.0f} s wall on {workers} workers")


# ---------------------------------------------------------------- rates

CPRIMES = (2.0, 3.0, 4.0, 5.0, 6.6, 8.0, 10.0)


def rate_task(args):
    N, cp, want_bip = args
    p = cp / N
    t0 = time.time()
    lc = log_connected(N, p)
    t = (N + 1) // 2
    lrel = log_prob_rel(N, p, t, lc)
    lprod = log_product_bound(N, p, t)
    lbip = log_prob_bip(N, p, t, lc) if want_bip else float("nan")
    return dict(N=N, cprime=cp, t=t, log_prob_bip=lbip, log_prob_rel=lrel, log_prod=lprod,
                rate_bip=(-lbip / N if want_bip else float("nan")), rate_rel=-lrel / N, rate_prod=-lprod / N,
                seconds=time.time() - t0)


def linfit(xs, ys):
    """slope, intercept, standard error of the slope (ordinary least squares)."""
    x = np.array(xs, float)
    y = np.array(ys, float)
    A = np.vstack([x, np.ones_like(x)]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    if len(x) > 2:
        resid = y - A @ coef
        s2 = (resid ** 2).sum() / (len(x) - 2)
        se = math.sqrt(s2 / ((x - x.mean()) ** 2).sum())
    else:
        se = float("nan")
    return coef[0], coef[1], se


def logfit(xs, ys):
    """`y = I N + b log N + a`: the slope I with the polynomial prefactor fitted."""
    x = np.array(xs, float)
    y = np.array(ys, float)
    A = np.vstack([x, np.log(x), np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef[0], coef[1], coef[2]


def stage_rates(max_N: int, workers: int) -> None:
    log("== rates ==")
    t0 = time.time()
    Ns_bip = list(range(20, max_N + 1, 10))
    Ns_rel = sorted(set(Ns_bip) | set(range(20, 401, 20)))
    tasks = [(N, cp, N in Ns_bip) for cp in CPRIMES for N in Ns_rel]
    tasks.sort(key=lambda a: -a[0])
    with Pool(workers) as pool:
        rows = pool.map(rate_task, tasks, chunksize=1)
    rows.sort(key=lambda r: (r["cprime"], r["N"]))
    with open(os.path.join(HERE, "rates.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log(f"  {len(rows)} (N, c') points in {time.time() - t0:.0f} s wall; the slowest point {max(r['seconds'] for r in rows):.0f} s")
    fits = []
    log(f"\n{'c prime':>7} | {'-logP_bip/N at N=20':>19} {'at 60':>7} {'at max':>7} | {'fit bip (N>=40)':>16} {'+-':>6} {'fit bip (N>=60)':>16} | {'-logP_rel/N at 400':>18} {'fit rel (N>=200)':>16} {'+-':>6} | {'pair c/4-ln2':>12} {'c/4':>6} {'thinning':>8} {'LDP I(1/2)':>10} | {'bip-rel at max':>14}")
    for cp in CPRIMES:
        rs = [r for r in rows if r["cprime"] == cp]
        rb = [r for r in rs if not math.isnan(r["rate_bip"])]
        s1, b1, e1 = linfit([r["N"] for r in rb if r["N"] >= 40], [-r["log_prob_bip"] for r in rb if r["N"] >= 40])
        s2, b2, e2 = linfit([r["N"] for r in rb if r["N"] >= 60], [-r["log_prob_bip"] for r in rb if r["N"] >= 60])
        s3, b3, e3 = linfit([r["N"] for r in rs if r["N"] >= 200], [-r["log_prob_rel"] for r in rs if r["N"] >= 200])
        s4, b4, e4 = linfit([r["N"] for r in rs if r["N"] >= 100], [-r["log_prob_rel"] for r in rs if r["N"] >= 100])
        lo, up, quarter, thin = bracket(cp)
        ldp = ldp_rate_half(cp)
        g1, gb1, _ = logfit([r["N"] for r in rb if r["N"] >= 40], [-r["log_prob_bip"] for r in rb if r["N"] >= 40])
        g3, gb3, _ = logfit([r["N"] for r in rs if r["N"] >= 100], [-r["log_prob_rel"] for r in rs if r["N"] >= 100])
        sp, _, _ = linfit([r["N"] for r in rb if r["N"] >= 40], [-r["log_prod"] for r in rb if r["N"] >= 40])
        gp, _, _ = logfit([r["N"] for r in rb if r["N"] >= 40], [-r["log_prod"] for r in rb if r["N"] >= 40])
        at = {r["N"]: r for r in rs}
        maxN = max(r["N"] for r in rb)
        d = dict(cprime=cp, rate_bip_N20=at[20]["rate_bip"], rate_bip_N60=at[60]["rate_bip"] if 60 in at else float("nan"),
                 rate_bip_Nmax=at[maxN]["rate_bip"], Nmax_bip=maxN,
                 fit_bip_slope_N40=s1, fit_bip_se_N40=e1, fit_bip_intercept_N40=b1,
                 fit_bip_slope_N60=s2, fit_bip_se_N60=e2, fit_bip_intercept_N60=b2,
                 rate_rel_N400=at[400]["rate_rel"], fit_rel_slope_N200=s3, fit_rel_se_N200=e3, fit_rel_intercept_N200=b3,
                 fit_rel_slope_N100=s4, fit_rel_se_N100=e4,
                 bracket_lower=lo, bracket_upper=up, quarter=quarter, thinning=thin, ldp_half=ldp,
                 bip_minus_rel_at_Nmax=at[maxN]["log_prob_bip"] - at[maxN]["log_prob_rel"],
                 prod_minus_bip_at_Nmax=at[maxN]["log_prod"] - at[maxN]["log_prob_bip"],
                 logfit_bip_slope_N40=g1, logfit_bip_logcoef_N40=gb1, logfit_rel_slope_N100=g3, logfit_rel_logcoef_N100=gb3,
                 fit_prod_slope_N40=sp, logfit_prod_slope_N40=gp,
                 in_bracket_linear=(lo <= s1 <= up), in_bracket_logfit=(lo <= g1 <= up),
                 above_finite_lower=(s1 >= sp))
        fits.append(d)
        log(f"{cp:>7.1f} | {d['rate_bip_N20']:>19.4f} {d['rate_bip_N60']:>7.4f} {d['rate_bip_Nmax']:>7.4f} | {s1:>16.4f} {e1:>6.4f} {s2:>16.4f} | {d['rate_rel_N400']:>18.4f} {s3:>16.4f} {e3:>6.4f} | {lo:>12.4f} {quarter:>6.3f} {thin:>8.3f} {ldp:>10.4f} | {d['bip_minus_rel_at_Nmax']:>14.5f}")
    log(f"\n{'c prime':>7} | {'logfit bip I (N>=40)':>20} {'logN coef':>9} | {'logfit rel I (N>=100)':>21} {'logN coef':>9} | {'linfit of product bound':>23} {'logfit of product bound':>23} | {'LDP I(1/2)':>10} | {'linear in bracket':>17} {'logfit in bracket':>17} {'bip fit >= prod fit':>19}")
    for d in fits:
        log(f"{d['cprime']:>7.1f} | {d['logfit_bip_slope_N40']:>20.4f} {d['logfit_bip_logcoef_N40']:>9.3f} | {d['logfit_rel_slope_N100']:>21.4f} {d['logfit_rel_logcoef_N100']:>9.3f} | {d['fit_prod_slope_N40']:>23.4f} {d['logfit_prod_slope_N40']:>23.4f} | {d['ldp_half']:>10.4f} | {str(d['in_bracket_linear']):>17} {str(d['in_bracket_logfit']):>17} {str(d['above_finite_lower']):>19}")
    with open(os.path.join(HERE, "rate_fits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fits[0].keys()))
        w.writeheader()
        w.writerows(fits)
    log("\nThe gap to the product bound, log[C(N,t)(1-p)^{t(N-t)}] - log P_N(E_bip), total nats and per vertex of N:")
    for cp in CPRIMES:
        rb = [r for r in rows if r["cprime"] == cp and not math.isnan(r["rate_bip"])]
        log(f"  c'={cp:>4}: " + "  ".join(f"N={r['N']}: {r['log_prod'] - r['log_prob_bip']:.2f} ({(r['log_prod'] - r['log_prob_bip']) / r['N']:.4f})" for r in rb if r["N"] in (20, 40, 60, 80, 100, 120)))
    log(f"rates: {time.time() - t0:.0f} s")


# ---------------------------------------------------------------- draw

def stage_draw() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(os.path.join(HERE, "rates.csv"))))
    fits = {float(r["cprime"]): r for r in csv.DictReader(open(os.path.join(HERE, "rate_fits.csv")))}
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.4), facecolor="#fcfcfb")
    axes = axes.ravel()
    for ax, cp in zip(axes, CPRIMES):
        rs = [r for r in rows if float(r["cprime"]) == cp]
        Nb = [int(r["N"]) for r in rs if r["rate_bip"] != "nan"]
        rb = [float(r["rate_bip"]) for r in rs if r["rate_bip"] != "nan"]
        Nr = [int(r["N"]) for r in rs]
        rr = [float(r["rate_rel"]) for r in rs]
        f = fits[cp]
        lo, up = float(f["bracket_lower"]), float(f["bracket_upper"])
        ax.set_facecolor("#fcfcfb")
        ax.axhspan(lo, up, color="#e6e5e1", zorder=0, label="analytic bracket for the rate of E_bip")
        ax.plot(Nr, rr, color="#eb6834", linewidth=2, label="E_relax, exact, to N = 400")
        ax.plot(Nb, rb, "o", color="#2a78d6", markersize=5, markeredgecolor="#fcfcfb", label="E_bip, exact")
        ax.axhline(float(f["ldp_half"]), color="#1baf7a", linewidth=2, linestyle="--", label="LDP rate I(1/2) of E_relax (item 01)")
        ax.axhline(float(f["fit_rel_slope_N200"]), color="#eb6834", linewidth=1, linestyle=":", label="fitted slope of E_relax (N >= 200)")
        ax.text(0.97, 0.95, f"c' = {cp:g}", transform=ax.transAxes, ha="right", va="top", fontsize=10, color="#0b0b0b")
        ax.set_xlabel("N", color="#52514e", fontsize=9)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#c3c2b7")
        ax.spines["bottom"].set_color("#c3c2b7")
        ax.tick_params(colors="#52514e", labelsize=8)
        ax.grid(axis="y", color="#e6e5e1", linewidth=0.6)
        ax.set_xlim(0, 410)
    axes[0].set_ylabel("−log P / N  (nats per vertex of N)", color="#52514e", fontsize=9)
    axes[4].set_ylabel("−log P / N  (nats per vertex of N)", color="#52514e", fontsize=9)
    axes[7].axis("off")
    h, l = axes[0].get_legend_handles_labels()
    axes[7].legend(h, l, loc="center", fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "rates.png"), dpi=150, facecolor="#fcfcfb")
    log("drew rates.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--max-N", type=int, default=60)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    load = os.getloadavg()[0]
    workers = min(a.workers, 4 if load > 24 else 8)
    log(f"\n# run at {time.strftime('%Y-%m-%d %H:%M')} stage={a.stage} max_N={a.max_N} workers={workers} load={load:.1f}")
    if a.stage in ("all", "check"):
        stage_check()
    if a.stage in ("all", "inner"):
        stage_inner(workers)
    if a.stage in ("all", "rates"):
        stage_rates(a.max_N, workers)
    if a.stage in ("all", "draw"):
        stage_draw()
