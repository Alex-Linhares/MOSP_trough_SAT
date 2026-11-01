"""loop0011 item 07: the MOSP version — random clique covers.

Stages (`--stage check|slack|grid|giant|floors`, all by default):
  check   the exact closed-pair probability against the enumeration of every cover
          at n <= 8, m <= 3 (random sizes), the NA/tangent bound above it, the
          isolated-customer pmf and the joint (I_A, I_R, empty) pmf against
          enumeration, the pgf at z = 1, theta = 0 at branching factor <= 1.
  slack   log E[X3] exact (the (u, w) alternating sum, integers) against the
          NA/tangent bound at k = round(beta* n), n = 8..26, (d, mu) = (6, 1), (4, 1):
          the slack of the cancellation-free bound in nats per customer (fitted).
  grid    (d, mu) in {2,3,4,6,8,10} x {1/2, 1, 2} and the five Chu & Stuckey
          classes at 125 with their pooled sizes: beta*, beta_closed (NA and the
          independent-sites approximation), the gains in nats at beta*, the flip
          gain and beta_flip, the additive estimate, the slope at beta*, Edwards &
          McDermid on the cover degree law, the certified slope b, the kill.
  giant   theta(d, mu) against the measured largest-component fractions at
          n = 50..75 (learning/data/excess.csv, fixed generator); the half-giant
          line per mu beside e_g(r) and e = 1; the Chu & Stuckey classes.
  floors  the 200 Chu & Stuckey instances: old pair floor, exact-size floor, the
          closed-pair floor (NA bound) and the flip floor at < 1 and < 0.01 against
          the certified optima; violations; class means.

Usage: nice -n 19 python3 reports/scratch/separator_moment/07_cover/run.py --workers 4
Outputs here: check.log, slack.csv, grid.csv, giant.csv, half_giant.csv, floors_cs.csv, run.log.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import math
import os
import random
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import numpy as np  # noqa: E402

import learning.separator_moment as sm  # noqa: E402
from learning.first_moment import chu_stuckey_sizes, floors as pair_floors, log_bound  # noqa: E402

LOG = open(os.path.join(HERE, "run.log"), "a")
LN10 = math.log(10)

# certified slopes b (opt = a + b n on n >= 30) from reports/excess_phase_diagram.md §2.5,
# the `fixed` generator (repairing; realised mean size slightly above d at d <= 3) and the
# Chu & Stuckey classes at m = n.
B_FIXED = {
    (0.5, 2): 0.00516, (0.5, 3): 0.0483, (0.5, 4): 0.151, (0.5, 5): 0.232, (0.5, 6): 0.323,
    (0.5, 7): 0.400, (0.5, 8): 0.463, (0.5, 9): 0.517, (0.5, 10): 0.585,
    (1.0, 2): 0.0378, (1.0, 3): 0.200, (1.0, 4): 0.348, (1.0, 5): 0.479, (1.0, 6): 0.577,
    (1.0, 7): 0.651, (1.0, 8): 0.706, (1.0, 9): 0.752, (1.0, 10): 0.795,
    (2.0, 2): 0.167, (2.0, 3): 0.409, (2.0, 4): 0.568, (2.0, 5): 0.685, (2.0, 6): 0.755,
    (2.0, 7): 0.811, (2.0, 8): 0.847, (2.0, 9): 0.873, (2.0, 10): 0.894,
}
B_CS = {2: 0.146, 4: 0.396, 6: 0.599, 8: 0.722, 10: 0.804}
SE_CS = {2: 0.0117, 4: 0.0142, 6: 0.0112, 8: 0.00785, 10: 0.00818}


def log(msg: str = "") -> None:
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def all_covers(n, sizes):
    choices = [[sum(1 << c for c in cs) for cs in itertools.combinations(range(n), s)] for s in sizes]
    for masks in itertools.product(*choices):
        yield masks


# ------------------------------------------------------------------ check

def stage_check() -> None:
    out = open(os.path.join(HERE, "check.log"), "w")

    def both(msg):
        print(msg, flush=True)
        out.write(msg + "\n")
        out.flush()

    rng = random.Random(2026)
    t0 = time.time()
    both("== check: closed-pair probability against enumeration of every cover ==")
    worst = 0.0
    cases = 0
    na_gap = []
    for n in range(3, 9):
        for m in range(1, 4):
            for _ in range(4 if n <= 7 else 2):
                sizes = [rng.randint(1, min(4, n)) for _ in range(m)]
                if math.prod(math.comb(n, s) for s in sizes) > 400000:
                    continue
                a = rng.randint(1, n - 1)
                r = rng.randint(0, n - a)
                s = n - a - r
                A, R = (1 << a) - 1, ((1 << r) - 1) << a
                S = ((1 << n) - 1) & ~(A | R)
                tot = cnt = 0
                for masks in all_covers(n, sizes):
                    cnt += 1
                    if any(mk & A and mk & R for mk in masks):
                        continue
                    if all(any((mk >> v & 1) and (mk & A) for mk in masks) and any((mk >> v & 1) and (mk & R) for mk in masks)
                           for v in range(n) if S >> v & 1):
                        tot += 1
                pe = Fraction(tot, cnt)
                lp = sm.closed_cover_log_prob_exact(n, a, r, s, sizes)
                cases += 1
                if pe == 0:
                    assert lp == -math.inf, (n, sizes, a, r, s)
                else:
                    worst = max(worst, abs(lp - math.log(pe)))
                    assert worst < 1e-9, (n, sizes, a, r, s, pe, lp)
                if s > 0 and pe > 0:
                    lb = sm.closed_cover_log_prob_na(n, a, r, s, sizes)
                    assert lb >= lp - 1e-9, (n, sizes, a, r, s, lp, lb)
                    na_gap.append(lb - lp)
    both(f"  {cases} (n, sizes, A, R, S) cases at n = 3..8, m <= 3: max |log diff| = {worst:.2e}; "
         f"NA bound >= exact on all, gap {min(na_gap):.3f}..{max(na_gap):.3f} nats (mean {np.mean(na_gap):.3f})")
    both("== check: NA bound >= exact on 60 random (n, sizes, A, R, S) at n = 8..16 ==")
    gaps = []
    for _ in range(60):
        n = rng.randint(8, 16)
        sizes = [rng.randint(2, 6) for _ in range(rng.randint(2, n))]
        a = rng.randint(1, n - 2)
        r = rng.randint(1, n - a - 1)
        s = n - a - r
        lp = sm.closed_cover_log_prob_exact(n, a, r, s, sizes)
        lb = sm.closed_cover_log_prob_na(n, a, r, s, sizes)
        assert lb >= lp - 1e-9, (n, sizes, a, r, s, lp, lb)
        if lp > -math.inf:
            gaps.append(lb - lp)
    both(f"  zero violations; gap {min(gaps):.3f}..{max(gaps):.3f} nats on {len(gaps)} with positive probability")
    both("== check: isolated-customer pmf and the joint (I_A, I_R, empty) pmf against enumeration ==")
    c1 = c2 = 0
    for n in range(2, 8):
        for m in range(1, 4):
            for _ in range(2):
                sizes = [rng.randint(1, min(4, n)) for _ in range(m)]
                if math.prod(math.comb(n, s) for s in sizes) > 300000:
                    continue
                counts = [0] * (n + 1)
                tot = 0
                for masks in all_covers(n, sizes):
                    tot += 1
                    counts[sum(1 for v in range(n) if not any((mk >> v & 1) and sm.popcount(mk) >= 2 for mk in masks))] += 1
                assert sm.isolated_pmf(n, sizes) == [Fraction(c, tot) for c in counts], (n, sizes)
                assert abs(sm.isolated_pgf(n, sizes, 1.0) - 1) < 1e-12
                c1 += 1
                if n < 3:
                    continue
                a = rng.randint(1, n - 1)
                r = rng.randint(1, n - a)
                A, R = (1 << a) - 1, ((1 << r) - 1) << a
                joint = {}
                for masks in all_covers(n, sizes):
                    if any(mk & A and mk & R for mk in masks):
                        continue
                    iA = sum(1 for v in range(a) if not any((mk >> v & 1) and (mk & A & ~(1 << v)) for mk in masks))
                    iR = sum(1 for v in range(a, a + r) if not any((mk >> v & 1) and (mk & R & ~(1 << v)) for mk in masks))
                    joint[(iA, iR)] = joint.get((iA, iR), 0) + 1
                pmf = sm.flip_joint_pmf(n, a, r, sizes)
                assert all(pmf[i][ip] == Fraction(joint.get((i, ip), 0), tot) for i in range(a + 1) for ip in range(r + 1)), (n, sizes, a, r)
                fast = sm.flip_log_bound_fast(n, max(0, n - a - r), sizes)
                c2 += 1
    both(f"  {c1} pmf cases and {c2} joint cases at n = 2..7, m <= 3: exact agreement; pgf(1) = 1")
    both("== check: theta(d, mu) = 0 exactly at branching factor <= 1 ==")
    for mu, d in ((0.5, 2), (1 / 6, 3), (1 / 12, 4), (0.25, 2), (0.1, 3)):
        bf = sm.rig_branching_factor(mu, {d: 1})
        th = sm.rig_giant(mu, {d: 1})
        assert (th == 0.0) == (bf <= 1), (mu, d, bf, th)
        both(f"  mu = {mu:.4f}, d = {d}: branching factor {bf:.3f}, theta = {th:.4f}")
    both(f"check: {time.time() - t0:.0f} s")
    out.close()


# ------------------------------------------------------------------ slack

def slack_task(args):
    n, mu, d = args
    sizes = {d: round(mu * n)}
    bs = sm.beta_star_cover(mu, {d: 1})
    k = max(1, round(bs * n))
    exact = sm.closed_cover_log_count_exact(n, k, sizes)
    na = sm.closed_cover_log_bound(n, k, sizes, optimise=True)
    pair = sm.cover_log_pair_bound(n, k, sizes)
    return {"n": n, "mu": mu, "d": d, "k": k, "log_closed_exact": exact, "log_closed_na": na, "log_pair": pair}


def stage_slack(workers: int) -> None:
    log("== slack: exact closed count against the NA/tangent bound ==")
    t0 = time.time()
    tasks = [(n, mu, d) for (mu, d) in ((1.0, 6), (1.0, 4), (1.0, 10)) for n in range(8, 27, 2)]
    with Pool(workers) as pool:
        rows = pool.map(slack_task, tasks)
    with open(os.path.join(HERE, "slack.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for (mu, d) in ((1.0, 6), (1.0, 4), (1.0, 10)):
        sub = [r for r in rows if r["mu"] == mu and r["d"] == d]
        log(f"  (d, mu) = ({d}, {mu}): n  k  exact  NA  pair  (log10);  NA − exact (nats)")
        xs, ys, ys2 = [], [], []
        for r in sub:
            log(f"    {r['n']:3d} {r['k']:3d}  {r['log_closed_exact'] / LN10:+7.2f} {r['log_closed_na'] / LN10:+7.2f} {r['log_pair'] / LN10:+7.2f}   {r['log_closed_na'] - r['log_closed_exact']:+.3f}")
            xs.append(r["n"])
            ys.append(r["log_closed_na"] - r["log_closed_exact"])
            ys2.append(r["log_pair"] - r["log_closed_exact"])
        ok = [i for i in range(len(xs)) if math.isfinite(ys[i]) and math.isfinite(ys2[i])]
        xs, ys, ys2 = [xs[i] for i in ok], [ys[i] for i in ok], [ys2[i] for i in ok]
        sl = np.polyfit(xs, ys, 1)
        sl2 = np.polyfit(xs, ys2, 1)
        log(f"    fitted slope of (NA − exact): {sl[0]:+.4f} nats per customer (intercept {sl[1]:+.3f}); "
            f"of (pair − exact): {sl2[0]:+.4f} (intercept {sl2[1]:+.3f})")
    log(f"slack: {len(tasks)} tasks in {time.time() - t0:.0f} s")


# ------------------------------------------------------------------ grid

def grid_task(args):
    label, mu, sizes = args
    t0 = time.time()
    bs = sm.beta_star_cover(mu, sizes)
    row = {"cell": label, "mu": mu, "beta_star": bs}
    if bs > 0:
        a0 = (1 - bs) / 2
        row["slope_at_beta_star"] = sm.cover_exponent_slope_at(bs, mu, sizes)
        row["gain_closed_na_nats"] = -sm.closed_cover_exponent_na(a0, a0, bs, mu, sizes)
        row["gain_closed_ind_nats"] = -sm.closed_cover_exponent_ind(a0, a0, bs, mu, sizes)
        v, x, y = sm.flip_cover_exponent_na(a0, a0, bs, mu, sizes, grid=6)
        row["gain_flip_nats"] = -v
        row["flip_x_star"], row["flip_y_star"] = x, y
        lA, lR = sm.cover_lambda(a0, a0, bs, mu, sizes)
        row["lambda_A"] = lA
        row["beta_closed_na"] = sm.beta_closed_cover(mu, sizes, "na")
        row["beta_closed_ind"] = sm.beta_closed_cover(mu, sizes, "ind")
        row["beta_flip"] = sm.beta_flip_cover(mu, sizes)
        # the additive estimate: the beta at which pair exponent + both gains (held at beta*) vanishes
        row["beta_additive_estimate"] = sm._root_above(
            lambda b: sm.cover_pair_exponent_beta(b, mu, sizes) - row["gain_closed_na_nats"] - row["gain_flip_nats"], bs)
    else:
        for key in ("slope_at_beta_star", "gain_closed_na_nats", "gain_closed_ind_nats", "gain_flip_nats",
                    "flip_x_star", "flip_y_star", "lambda_A", "beta_closed_na", "beta_closed_ind", "beta_flip",
                    "beta_additive_estimate"):
            row[key] = 0.0
    row["em_upper"] = sm.edwards_mcdermid_cover(mu, sizes)
    row["theta_giant"] = sm.rig_giant(mu, sizes)
    row["seconds"] = time.time() - t0
    return row


def stage_grid(workers: int) -> None:
    log("== grid ==")
    t0 = time.time()
    tasks = []
    for mu in (0.5, 1.0, 2.0):
        for d in (2, 3, 4, 6, 8, 10):
            tasks.append((f"d={d} mu={mu}", mu, {d: 1}))
    cls = chu_stuckey_sizes()
    for d in (2, 4, 6, 8, 10):
        tasks.append((f"CS 125x125 d={d} (pooled sizes)", 1.0, dict(cls[(125, 125, d)]["sizes"])))
    with Pool(workers) as pool:
        rows = pool.map(grid_task, tasks)
    for row in rows:
        if row["cell"].startswith("d="):
            d = int(row["cell"].split()[0][2:])
            row["b_certified"] = B_FIXED.get((row["mu"], d), float("nan"))
        else:
            d = int(row["cell"].split("d=")[1].split()[0])
            row["b_certified"] = B_CS[d]
        row["gain_closed_beta"] = row["beta_closed_na"] - row["beta_star"]
        row["gain_flip_beta"] = row["beta_flip"] - row["beta_star"]
        row["kill_closed_lt_0.02"] = row["gain_closed_beta"] < 0.02
    with open(os.path.join(HERE, "grid.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log("cell                              beta*   b      EM    beta_cl(NA) +     beta_cl(ind) +   beta_flip +    additive  slope  gains(nats): closedNA closedInd flip   theta")
    for r in rows:
        log(f"{r['cell']:32s} {r['beta_star']:.4f} {r['b_certified']:.3f}  {r['em_upper']:.3f}  "
            f"{r['beta_closed_na']:.4f} {r['gain_closed_beta']:+.4f}  {r['beta_closed_ind']:.4f} {r['beta_closed_ind'] - r['beta_star']:+.4f}  "
            f"{r['beta_flip']:.4f} {r['gain_flip_beta']:+.4f}  {r['beta_additive_estimate']:.4f}  {r['slope_at_beta_star']:.2f}  "
            f"{r['gain_closed_na_nats']:.4f} {r['gain_closed_ind_nats']:.4f} {r['gain_flip_nats']:.4f}  {r['theta_giant']:.3f}  ({r['seconds']:.0f} s)")
    log(f"grid: {len(tasks)} cells in {time.time() - t0:.0f} s")


# ------------------------------------------------------------------ giant

def stage_grid_fix() -> None:
    """Recompute the cheap root columns of grid.csv with the corrected root finder
    (the first run's bisection on (0, 1) returned 1.0 where the exponent falls
    back to zero at beta -> 1); the expensive columns are kept."""
    log("== grid_fix ==")
    rows = list(csv.DictReader(open(os.path.join(HERE, "grid.csv"))))
    cls = chu_stuckey_sizes()
    for r in rows:
        mu = float(r["mu"])
        if r["cell"].startswith("d="):
            sizes = {int(r["cell"].split()[0][2:]): 1}
        else:
            sizes = dict(cls[(125, 125, int(r["cell"].split("d=")[1].split()[0]))]["sizes"])
        bs = float(r["beta_star"])
        if bs > 0:
            r["beta_closed_ind"] = sm.beta_closed_cover(mu, sizes, "ind")
            g = float(r["gain_closed_na_nats"]) + float(r["gain_flip_nats"])
            r["beta_additive_estimate"] = sm._root_above(lambda b: sm.cover_pair_exponent_beta(b, mu, sizes) - g, bs)
        log(f"  {r['cell']:32s} beta*={bs:.4f} closed_ind={float(r['beta_closed_ind']):.4f} additive={float(r['beta_additive_estimate']):.4f} "
            f"(closed_na={float(r['beta_closed_na']):.4f}, flip={float(r['beta_flip']):.4f})")
    with open(os.path.join(HERE, "grid.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def stage_giant() -> None:
    import pandas as pd
    log("== giant: theta(d, mu) against the measured largest-component fractions (n = 50..75, fixed generator) ==")
    f = pd.read_csv("learning/data/excess.csv", low_memory=False)
    g = f[(f.generator == "fixed") & (f.n >= 50) & (f.n <= 75)]
    rows = []
    for (rl, param), sub in g.groupby(["r_label", "param"]):
        mu = float(sub["r"].mean())
        d = int(param)
        mean_size = float(sub["c"].mean())
        rows.append({"r_label": rl, "mu": mu, "d": d, "e_realised": float(sub["e"].mean()), "n_instances": len(sub),
                     "mean_size_realised": mean_size,
                     "lcc_cust_frac_measured": float(sub["lcc_cust_frac"].mean()),
                     "lcc_cust_frac_se": float(sub["lcc_cust_frac"].std() / math.sqrt(len(sub))),
                     "theta_fixed_d": sm.rig_giant(mu, {d: 1}),
                     "theta_mean_size": sm.rig_giant(mu, {mean_size: 1}),
                     "branching_factor": sm.rig_branching_factor(mu, {d: 1})})
    rows.sort(key=lambda r: (r["mu"], r["d"]))
    with open(os.path.join(HERE, "giant.csv"), "w", newline="") as f2:
        w = csv.DictWriter(f2, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log("  mu     d   e_real  mean_sz  measured  (se)    theta(d)  theta(mean sz)  bf")
    for r in rows:
        log(f"  {r['mu']:.3f} {r['d']:3d}  {r['e_realised']:.3f}  {r['mean_size_realised']:.2f}   {r['lcc_cust_frac_measured']:.3f}  ({r['lcc_cust_frac_se']:.3f})  "
            f"{r['theta_fixed_d']:.3f}     {r['theta_mean_size']:.3f}       {r['branching_factor']:.2f}")
    log("== the half-giant line, per mu ==")
    hg = []
    for mu in (0.125, 0.25, 0.5, 1.0, 2.0):
        d = sm.half_giant_line(mu)
        e_g = (math.sqrt(mu * mu + 4 * mu) - mu) / 2
        hg.append({"mu": mu, "d_half": d, "e_half": mu * (d - 1), "e_g": e_g, "e_pair_threshold": 1.0,
                   "d_g": 1 + e_g / mu, "d_pair_threshold": 1 + 1 / mu})
        log(f"  mu = {mu:.3f}: theta = 1/2 at d = {d:.4f}, e = {mu * (d - 1):.4f}   (e_g = {e_g:.4f}, e = 1 at d = {1 + 1 / mu:.3f})")
    with open(os.path.join(HERE, "half_giant.csv"), "w", newline="") as f2:
        w = csv.DictWriter(f2, fieldnames=list(hg[0].keys()))
        w.writeheader()
        w.writerows(hg)
    log("== the Chu & Stuckey classes (pooled empirical sizes, mu = 1): theta, and measured ==")
    cls = chu_stuckey_sizes()
    cs = f[f.source_file.astype(str).str.contains("Chu_Stuckey")]
    for (n, m, d), c in sorted(cls.items()):
        sub = cs[cs.instance_name.str.startswith(f"Random-{n}-{m}-{d}-")]
        th = sm.rig_giant(m / n, dict(c["sizes"]))
        log(f"  ({n}, {m}, {d}): theta = {th:.3f}, measured lcc_cust_frac = {float(sub['lcc_cust_frac'].mean()):.3f}, e = {float(sub['e'].mean()):.2f}")


# ------------------------------------------------------------------ floors

def floor_of(vals: dict[int, float], thresh: float) -> int:
    best = -1
    for k in sorted(vals):
        if vals[k] < math.log(thresh):
            best = k
    return best


def floors_task(args):
    name, n, m, d, sizes, opt = args
    t0 = time.time()
    old1, old2 = pair_floors(n, sizes)
    xp = {k: sm.cover_log_pair_bound(n, k, sizes) for k in range(n)}
    x1, x2 = floor_of(xp, 1.0) + 2, floor_of(xp, 0.01) + 2
    # the closed and flip bounds around the exact-size floors only (valid at every k they are below)
    ks = [k for k in range(max(0, x2 - 4), min(n - 1, x1 + 6) + 1)]
    cl = {k: sm.closed_cover_log_bound(n, k, sizes, optimise=False) for k in ks}
    fl = {k: sm.flip_log_bound_fast(n, k, sizes)[0] for k in ks}
    c1, c2 = floor_of(cl, 1.0) + 2, floor_of(cl, 0.01) + 2
    f1, f2 = floor_of(fl, 1.0) + 2, floor_of(fl, 0.01) + 2
    return {"instance": name, "n": n, "m": m, "d": d, "optimum": opt,
            "old_lt1": old1, "old_lt001": old2, "xpair_lt1": x1, "xpair_lt001": x2,
            "closed_lt1": c1, "closed_lt001": c2, "flip_lt1": f1, "flip_lt001": f2,
            "k_scanned": f"{ks[0]}-{ks[-1]}", "seconds": round(time.time() - t0, 1),
            "log10_closed_at_xpair001": cl.get(x2 - 2, float("nan")) / LN10,
            "log10_xpair_at_xpair001": xp.get(x2 - 2, float("nan")) / LN10,
            "log10_flip_at_xpair001": fl.get(x2 - 2, float("nan")) / LN10}


def stage_floors(workers: int) -> None:
    import pandas as pd
    log("== floors on the 200 Chu & Stuckey instances ==")
    t0 = time.time()
    f = pd.read_csv("learning/data/excess.csv", low_memory=False)
    cs = f[f.source_file.astype(str).str.contains("Chu_Stuckey")]
    assert len(cs) == 200 and cs.certified.all()
    opt = dict(zip(cs.instance_name.str.replace(r"_0$", "", regex=True), cs.optimum))
    cls = chu_stuckey_sizes()
    tasks = []
    for (n, m, d), c in sorted(cls.items()):
        for name, sizes in c["instances"]:
            tasks.append((name, n, m, d, sizes, int(opt[name])))
    tasks.sort(key=lambda t: -(t[1] * t[3]))   # dense and large first
    with Pool(workers) as pool:
        rows = pool.map(floors_task, tasks, chunksize=1)
    rows.sort(key=lambda r: (r["n"], r["m"], r["d"], r["instance"]))
    with open(os.path.join(HERE, "floors_cs.csv"), "w", newline="") as f2:
        w = csv.DictWriter(f2, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log("floor               | violations (<1) | violations (<0.01) | mean floor <1 / <0.01 | mean gap <1 / <0.01")
    for key, lab in (("old", "old single pair"), ("xpair", "exact-size pair"), ("closed", "closed pair (NA)"), ("flip", "flip (weighted count)")):
        v1 = sum(1 for r in rows if r[f"{key}_lt1"] > r["optimum"])
        v2 = sum(1 for r in rows if r[f"{key}_lt001"] > r["optimum"])
        m1 = np.mean([r[f"{key}_lt1"] for r in rows])
        m2 = np.mean([r[f"{key}_lt001"] for r in rows])
        g1 = np.mean([r["optimum"] - r[f"{key}_lt1"] for r in rows])
        g2 = np.mean([r["optimum"] - r[f"{key}_lt001"] for r in rows])
        log(f"{lab:20s}| {v1:3d}             | {v2:3d}                | {m1:.2f} / {m2:.2f}         | {g1:.2f} / {g2:.2f}")
    for key in ("closed", "flip"):
        hi = sum(1 for r in rows if r[f"{key}_lt001"] > r["xpair_lt001"])
        eq = sum(1 for r in rows if r[f"{key}_lt001"] == r["xpair_lt001"])
        lo = sum(1 for r in rows if r[f"{key}_lt001"] < r["xpair_lt001"])
        log(f"  {key} < 0.01 floor against the exact-size pair floor: higher on {hi}, equal on {eq}, lower on {lo}")
    log("class          opt    old   xpair  closed  flip | old<.01 xpair<.01 closed<.01 flip<.01 | log10 at xpair<.01 k: xpair closed flip")
    for (n, m, d) in sorted({(r["n"], r["m"], r["d"]) for r in rows}):
        sub = [r for r in rows if (r["n"], r["m"], r["d"]) == (n, m, d)]
        mean = lambda key: np.mean([r[key] for r in sub])
        log(f"({n:3d},{m:3d},{d:2d})  {mean('optimum'):5.1f}  {mean('old_lt1'):5.1f} {mean('xpair_lt1'):5.1f} {mean('closed_lt1'):5.1f} {mean('flip_lt1'):5.1f} | "
            f"{mean('old_lt001'):5.1f} {mean('xpair_lt001'):5.1f} {mean('closed_lt001'):5.1f} {mean('flip_lt001'):5.1f} | "
            f"{mean('log10_xpair_at_xpair001'):+.2f} {mean('log10_closed_at_xpair001'):+.2f} {mean('log10_flip_at_xpair001'):+.2f}")
    log(f"floors: 200 instances in {time.time() - t0:.0f} s ({sum(r['seconds'] for r in rows) / 3600:.2f} core-hours)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    log(f"\n# run {time.strftime('%Y-%m-%d %H:%M:%S')} stage={a.stage} workers={a.workers}")
    if a.stage in ("all", "check"):
        stage_check()
    if a.stage in ("all", "slack"):
        stage_slack(a.workers)
    if a.stage in ("all", "grid"):
        stage_grid(a.workers)
    if a.stage == "grid_fix":
        stage_grid_fix()
    if a.stage in ("all", "giant"):
        stage_giant()
    if a.stage in ("all", "floors"):
        stage_floors(a.workers)


if __name__ == "__main__":
    main()
