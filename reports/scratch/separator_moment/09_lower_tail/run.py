#!/usr/bin/env python3
"""Item 09 of Ralph loop0011: the weighted count's lower tail.

Stages (all by default; `--stage` selects one):

  check      the recombination lemma, brute force: every labelled graph on 4–6
             vertices at every width, every exact-size pair, every image pair
             empty, exact-size, distinct, not P₀, in the enumerated set, and the
             closed-form count equal to the explicit one (`check.log`);
  tail       on item 04's planted instances at `β*` (regenerated from their
             seeds; `X` read from `04_planted/planted.csv`): the recombination
             counts per (lobe, |U_A|, |U_R|) at `j ≤ 4`, `Z_4`, the flip count,
             `Ẑ₀`, `|L_A|`, `|L_R|` (`tail.csv`);
  stats      per cell: the quantiles of `log Z`, the shares with `Z = 1`, and the
             three slacks `−log E[1/X]`, `−log E[1/Z_4]`, `−log E[1/Ẑ₀]` per
             vertex and in `β` (`cells.csv`, `run.log`);
  laplace    the exact finite transform `log E[1/Ẑ₀ | planted]` at `n` up to
             3,200 against the variational exponent, and `β_W(c)` against
             `β_closed(c)` on the `c` table (`laplace.csv`, `beta_w.csv`);
  threshold  the (d) branch: `β_sep` at `c = 2.0, 2.2, …, 4.0` from the cited
             LDP rate and from a fitted rate on a finer `c′` grid, the finite
             separator floor at `n = 60` by the exact `P_N(E_bip)`
             (`threshold_fine.csv`, `floors_60.csv`).

Regenerate: `nice -n 19 python3 reports/scratch/separator_moment/09_lower_tail/run.py --workers 8`.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from fractions import Fraction
from itertools import combinations
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "..", "04_planted"))

import learning.separator_moment as sm  # noqa: E402
from learning.first_moment import beta_star, rate as cover_rate  # noqa: E402
from run import cells as planted_cells, planted_instance  # noqa: E402  (item 04's generator)

LOG = open(os.path.join(HERE, "run.log"), "a")
JMAX = 4
N_FIT = [100, 150, 200, 250, 300, 350, 400]
C_FINE = [round(2.0 + 0.2 * i, 1) for i in range(11)]          # 2.0 … 4.0
CP_FINE = [round(1.5 + 0.05 * i, 2) for i in range(51)]        # 1.50 … 4.00
SLOPES = {2.0: 0.040, 3.0: 0.099, 4.0: 0.158}                  # survey §7(d), fitted


def log(msg: str = "") -> None:
    print(msg)
    LOG.write(msg + "\n")
    LOG.flush()


# ---------------------------------------------------------------- check

def labelled_graphs(N):
    pairs = list(combinations(range(N), 2))
    for bits in range(1 << len(pairs)):
        adj = [0] * N
        for i, (u, v) in enumerate(pairs):
            if bits >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        yield adj


def check_task(args):
    n, lo, hi = args
    graphs = pairs = images = 0
    worst = 0
    pairs_list = list(combinations(range(n), 2))
    for bits in range(lo, hi):
        adj = [0] * n
        for i, (u, v) in enumerate(pairs_list):
            if bits >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        graphs += 1
        for k in range(0, n):
            N, t = sm.forced_sizes(n, k)
            r = N - t
            if min(t, r) < 2:
                continue
            ex = set(sm.enumerate_empty_pairs(adj, k))
            jm = min(JMAX, min(t, r) - 1)
            for (A, R) in ex:
                pairs += 1
                imgs = sm.recombination_pairs(adj, A, R, jm)
                cnt = sm.recombinations(adj, A, R, jm)
                total = sum(cnt.values())
                if len(imgs) != total or len(set(imgs)) != len(imgs):
                    raise AssertionError(f"count mismatch n={n} bits={bits} k={k} P=({A},{R}): explicit {len(imgs)}, distinct {len(set(imgs))}, closed form {total}")
                for (A2, R2) in imgs:
                    if (A2, R2) not in ex or (A2, R2) == (A, R):
                        raise AssertionError(f"bad image n={n} bits={bits} k={k} P=({A},{R}) -> ({A2},{R2})")
                    if sm.popcount(A2) != t or sm.popcount(R2) != r or A2 & R2:
                        raise AssertionError("sizes")
                images += total
                zh = sm.z_hat0(adj, A, R)
                la, lr = sm.side_avoiders(adj, A, R)
                zfull = 1 + sum(sm.recombinations(adj, A, R, min(max(jm, la, lr), min(t, r) - 1)).values())
                if not (1 <= zh <= zfull <= len(ex)):
                    raise AssertionError(f"Ẑ₀ ≤ Z ≤ X fails n={n} bits={bits} k={k}: {zh} {zfull} {len(ex)}")
                worst = max(worst, total)
    return n, graphs, pairs, images, worst


def stage_check(workers: int) -> None:
    log("== check ==")
    t0 = time.time()
    out = open(os.path.join(HERE, "check.log"), "w")
    tasks = []
    for n in (4, 5, 6):
        total = 1 << (n * (n - 1) // 2)
        chunk = max(1, total // (workers * 4))
        for lo in range(0, total, chunk):
            tasks.append((n, lo, min(total, lo + chunk)))
    with Pool(workers) as pool:
        res = pool.map(check_task, tasks)
    agg = {}
    for n, g, p, im, w in res:
        a = agg.setdefault(n, [0, 0, 0, 0])
        a[0] += g; a[1] += p; a[2] += im; a[3] = max(a[3], w)
    for n in sorted(agg):
        g, p, im, w = agg[n]
        line = (f"n={n}: {g} labelled graphs, {p} exact-size pairs at widths with min(t, r) >= 2, "
                f"{im} recombined pairs checked (empty, exact-size, distinct, not P0, in the enumeration; "
                f"closed form = explicit count), max per pair {w}; Ẑ₀ ≤ Z ≤ X on every pair")
        log(line); out.write(line + "\n")
    # the weighted-count identity with Z = Z_4 on random graphs at n = 10 (Lemma W, pointwise)
    import random
    rng = random.Random(9)
    viol = 0; tested = 0
    for i in range(300):
        n = 10
        p = rng.choice([0.3, 0.5, 0.7])
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    adj[u] |= 1 << v; adj[v] |= 1 << u
        for k in range(0, 7):
            N, t = sm.forced_sizes(n, k); r = N - t
            if min(t, r) < 2:
                continue
            ex = sm.enumerate_empty_pairs(adj, k)
            jm = min(JMAX, min(t, r) - 1)
            Y = sm.weighted_count(ex, lambda P: 1 + sum(sm.recombinations(adj, P[0], P[1], jm).values()))
            Yh = sm.weighted_count(ex, lambda P: sm.z_hat0(adj, P[0], P[1]))
            tested += 1
            if (len(ex) > 0 and (Y < 1 or Yh < Y)) or (len(ex) == 0 and Y != 0):
                viol += 1
    line = f"Lemma W with Z = Z_4 and Z = Ẑ₀ on 300 random G(10, p) at every width: {tested} (graph, k) pairs, Y ≥ 1[X > 0] and Y(Ẑ₀) ≥ Y(Z_4): {viol} violations"
    log(line); out.write(line + "\n")
    out.close()
    log(f"check: {time.time() - t0:.0f} s")


# ---------------------------------------------------------------- tail

FIELDS = ["source", "cell", "n", "c", "beta_label", "k", "beta", "N", "t", "r", "sample", "seed", "X",
          "Z4", "Z4_same", "Z4_rev", "Z1", "Z2", "Z3", "Zfl", "IA", "IR", "Zhat0", "LA", "LR", "Zall",
          "closed", "seconds"]


def tail_task(job):
    cell, i, X = job
    t0 = time.time()
    adj, (A, R), seed = planted_instance(cell, i)
    n, k = cell["n"], cell["k"]
    N, t = sm.forced_sizes(n, k)
    r = N - t
    jm = min(JMAX, min(t, r) - 1)
    cnt = sm.recombinations(adj, A, R, jm)
    by_j = {j: 1 + sum(v for (lobe, ja, jr), v in cnt.items() if max(ja, jr) <= j) for j in range(1, JMAX + 1)}
    same = sum(v for (lobe, ja, jr), v in cnt.items() if lobe == "same")
    rev = sum(v for (lobe, ja, jr), v in cnt.items() if lobe == "rev")
    ia, ir, zfl = sm.flip_count(adj, A, R)
    la, lr = sm.side_avoiders(adj, A, R)
    zh = sm.z_hat0(adj, A, R)
    # Z_all: recombinations (j ≤ max(4, L_A, L_R), so that Ẑ₀ ≤ Z) ∪ flips, the identity once
    jall = min(max(jm, la, lr), min(t, r) - 1)
    zall = (1 + sum(sm.recombinations(adj, A, R, jall).values()) if jall > jm else 1 + sum(cnt.values())) + zfl - 1
    row = dict(source=cell["source"], cell=cell["cell"], n=n, c=cell["c"], beta_label=cell["beta_label"], k=k,
               beta=round(k / n, 4), N=N, t=t, r=r, sample=i, seed=seed, X=X,
               Z4=1 + sum(cnt.values()), Z4_same=same, Z4_rev=rev, Z1=by_j[1], Z2=by_j[2], Z3=by_j[3],
               Zfl=zfl, IA=ia, IR=ir, Zhat0=zh, LA=la, LR=lr, Zall=zall,
               closed=int(la == 0 and lr == 0), seconds=round(time.time() - t0, 3))
    if not (zh <= zall and (X == "" or zall <= int(X))):
        row["note"] = "ORDER VIOLATION"
    return row


def stage_tail(workers: int) -> None:
    log("== tail ==")
    t0 = time.time()
    planted = {}
    for r in csv.DictReader(open(os.path.join(HERE, "..", "04_planted", "planted.csv"))):
        planted[(r["cell"], int(r["sample"]))] = r["X"]
    jobs = []
    for cell in planted_cells():
        if cell["beta_label"] != "star":
            continue
        for i in range(200):
            X = planted.get((cell["cell"], i), "")
            jobs.append((cell, i, "" if X.startswith(">") else X))
    with Pool(workers) as pool:
        rows = pool.map(tail_task, jobs, chunksize=4)
    viol = [r for r in rows if r.get("note")]
    with open(os.path.join(HERE, "tail.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + ["note"])
        w.writeheader()
        w.writerows(rows)
    log(f"tail: {len(rows)} planted instances in {time.time() - t0:.0f} s wall; {len(viol)} order violations (Ẑ₀ ≤ Z_all ≤ X)")


# ---------------------------------------------------------------- stats

def slack(vals, n):
    """(E[1/Z], se, −log E[1/Z], per vertex)"""
    inv = np.array([1.0 / v for v in vals])
    m = inv.mean(); se = inv.std(ddof=1) / math.sqrt(len(inv))
    return m, se, -math.log(m), -math.log(m) / n


def stage_stats() -> None:
    log("== stats ==")
    rows = list(csv.DictReader(open(os.path.join(HERE, "tail.csv"))))
    c04 = {r["cell"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "04_planted", "cells.csv")))}
    out = []
    log("cell                 n  k  |  Z4: med p10 p25 gm  share=1 | same/rev med | Zhat0: med share=1 | Zfl med | X med | "
        "slack per vertex (nats): X  Z4  Zall  Zhat0  Zfl  closed-share | in β")
    for cell in planted_cells():
        if cell["beta_label"] != "star":
            continue
        sub = [r for r in rows if r["cell"] == cell["cell"]]
        if not sub:
            continue
        n, k, c = cell["n"], cell["k"], cell["c"]
        Z4 = np.array([int(r["Z4"]) for r in sub]); Zh = np.array([int(r["Zhat0"]) for r in sub])
        Zall = np.array([int(r["Zall"]) for r in sub]); Zfl = np.array([int(r["Zfl"]) for r in sub])
        same = np.array([int(r["Z4_same"]) for r in sub]); rev = np.array([int(r["Z4_rev"]) for r in sub])
        Xs = [int(r["X"]) for r in sub if r["X"] != ""]
        closed = np.array([int(r["closed"]) for r in sub])
        if cell["source"] == "gnp":
            slope = sm.exponent_slope_at(float(c), k / n)
        else:
            sizes = {6: 1}
            slope = sm.cover_exponent_slope_at(k / n, 1.0, sizes)
        sX = slack(Xs, n); s4 = slack(Z4, n); sA = slack(Zall, n); sH = slack(Zh, n); sF = slack(Zfl, n)
        lz = np.log(Z4)
        d = dict(cell=cell["cell"], source=cell["source"], n=n, c=c, k=k, beta=round(k / n, 4), N=n - k, t=(n - k + 1) // 2,
                 instances=len(sub),
                 Z4_median=float(np.median(Z4)), Z4_p10=float(np.percentile(Z4, 10)), Z4_p25=float(np.percentile(Z4, 25)),
                 Z4_gm=float(math.exp(lz.mean())), Z4_share_one=float((Z4 == 1).mean()),
                 Z4_same_median=float(np.median(same)), Z4_rev_median=float(np.median(rev)),
                 Zhat0_median=float(np.median(Zh)), Zhat0_share_one=float((Zh == 1).mean()),
                 Zfl_median=float(np.median(Zfl)), Zfl_share_one=float((Zfl == 1).mean()),
                 Zall_median=float(np.median(Zall)), X_median=float(np.median(Xs)),
                 logZ4_over_logX_median=float(np.median([math.log(int(r["Z4"])) / math.log(int(r["X"])) for r in sub if r["X"] != "" and int(r["X"]) > 1])),
                 closed_share=float(closed.mean()),
                 Z4_one_given_closed=float((Z4[closed == 1] == 1).mean()) if closed.sum() else float("nan"),
                 inv_X=sX[0], inv_X_se=sX[1], inv_Z4=s4[0], inv_Z4_se=s4[1], inv_Zall=sA[0], inv_Zall_se=sA[1],
                 inv_Zhat0=sH[0], inv_Zhat0_se=sH[1], inv_Zfl=sF[0], inv_Zfl_se=sF[1],
                 slack_X=sX[2], slack_Z4=s4[2], slack_Zall=sA[2], slack_Zhat0=sH[2], slack_Zfl=sF[2],
                 slack_X_pv=sX[3], slack_Z4_pv=s4[3], slack_Zall_pv=sA[3], slack_Zhat0_pv=sH[3], slack_Zfl_pv=sF[3],
                 pair_slope=slope,
                 slack_X_beta=sX[3] / slope, slack_Z4_beta=s4[3] / slope, slack_Zall_beta=sA[3] / slope,
                 slack_Zhat0_beta=sH[3] / slope, slack_Zfl_beta=sF[3] / slope,
                 inv_X_item04=float(c04[cell["cell"]]["inv_X_mean"]) if cell["cell"] in c04 and "inv_X_mean" in c04[cell["cell"]] else float("nan"))
        out.append(d)
        log(f"{d['cell']:18s} {n:3d} {k:2d} | {d['Z4_median']:6.1f} {d['Z4_p10']:5.1f} {d['Z4_p25']:5.1f} {d['Z4_gm']:6.2f} {d['Z4_share_one']:.2f} | "
            f"{d['Z4_same_median']:5.1f}/{d['Z4_rev_median']:5.1f} | {d['Zhat0_median']:5.1f} {d['Zhat0_share_one']:.2f} | {d['Zfl_median']:4.1f} | {d['X_median']:7.1f} | "
            f"{d['slack_X_pv']:.3f} {d['slack_Z4_pv']:.3f} {d['slack_Zall_pv']:.3f} {d['slack_Zhat0_pv']:.3f} {d['slack_Zfl_pv']:.3f}  {d['closed_share']:.2f} | "
            f"{d['slack_X_beta']:.3f} {d['slack_Z4_beta']:.3f} {d['slack_Zall_beta']:.3f} {d['slack_Zhat0_beta']:.3f}")
    with open(os.path.join(HERE, "cells.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    # growth in n of the three slacks, per (source, c)
    log("slopes in n of −log E[1/·] (nats per vertex, OLS over the sizes): X / Z4 / Zall / Zhat0")
    for src, c in (("gnp", 6), ("gnp", 10), ("cover", 6)):
        sub = [d for d in out if d["source"] == src and d["c"] == c]
        ns = np.array([d["n"] for d in sub], float)
        line = f"  {src} c={c}: "
        for key in ("slack_X", "slack_Z4", "slack_Zall", "slack_Zhat0"):
            ys = np.array([d[key] for d in sub])
            A = np.vstack([ns, np.ones_like(ns)]).T
            coef, res, *_ = np.linalg.lstsq(A, ys, rcond=None)
            dof = len(ns) - 2
            se = math.sqrt(res[0] / dof / ((ns - ns.mean()) ** 2).sum()) if dof > 0 and len(res) else float("nan")
            line += f"{key[6:]} {coef[0]:+.3f} ± {se:.3f}   "
        log(line)
    # the mechanism of the lower tail: among Z4 = 1, how many are closed pairs; the Z4 = 1 share against the closed share
    log("lower tail: share Z4 = 1 / share Ẑ₀ = 1 (= P₀ closed) / share Z4 = 1 among closed / E[1/Z4] − P(Z4 = 1) (the rest of the transform)")
    for d in out:
        sub = [r for r in rows if r["cell"] == d["cell"]]
        inv = np.mean([1.0 / int(r["Z4"]) for r in sub])
        log(f"  {d['cell']:18s} {d['Z4_share_one']:.3f} / {d['Zhat0_share_one']:.3f} / {d['Z4_one_given_closed']:.3f} / {inv - d['Z4_share_one']:.3f}")


# ---------------------------------------------------------------- laplace

def stage_laplace() -> None:
    log("== laplace ==")
    rows = []
    for c in (6.0, 10.0):
        bs = sm.beta_star_gnp(c)
        expo, lamA, lamR = sm.z_hat_exponent(c, bs)
        a = (1 - bs) / 2
        corner = 2 * bs * math.log(-math.expm1(-c * a))
        log(f"c={c}: β*={bs:.4f}  exponent of E[1/Ẑ₀] = {expo:+.5f} at λ=({lamA:.5f}, {lamR:.5f}); 2β ln q(a) = {corner:+.5f}; "
            f"typical |L| per vertex = β e^{{−c a}} = {bs * math.exp(-c * a):.4f}")
        for n in (32, 64, 128, 256, 512, 1024, 2048, 3200):
            k = int(round(bs * n))
            lt = sm.z_hat_log_laplace(n, k, c / n)
            N, t = sm.forced_sizes(n, k)
            pi = (1 - c / n) ** t
            lower = 2 * k * math.log1p(-pi)          # log P(L_A = L_R = 0) at this n
            typ = sm.lchoose(int(round(k * pi)) + t, t)
            rows.append(dict(c=c, n=n, k=k, beta=k / n, log_laplace=lt, per_vertex=lt / n, log_P_closed=lower,
                             log_P_closed_pv=lower / n, asymptotic=expo, typical_log_Zhat0_pv=typ / n))
            log(f"   n={n:5d} k={k:4d}: log E[1/Ẑ₀] = {lt:9.3f} ({lt / n:+.5f} per vertex); log P(P₀ closed) = {lower:9.3f} ({lower / n:+.5f}); "
                f"typical log Ẑ₀ per vertex ≈ {typ / n:.4f}")
    with open(os.path.join(HERE, "laplace.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # β_W against β_closed, β_sep, β* on the c table
    const = {float(r["c"]): r for r in csv.DictReader(open(os.path.join(HERE, "..", "06_constants", "constants.csv")))}
    out = []
    log("c     β*      β_closed  β_W      β_W−β_closed  β_sep(fitted)  gain_W (β)  gain_W (nats)  λ at the minimiser")
    for c in (3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0):
        bs = sm.beta_star_gnp(c)
        bw = sm.beta_weighted(c)
        bc = float(const[c]["beta_closed"]) if c in const else sm.beta_closed(c)
        bsep = float(const[c]["beta_sep_fitted"]) if c in const else float("nan")
        expo, lamA, lamR = sm.z_hat_exponent(c, bs)
        slope = sm.exponent_slope_at(c, bs)
        out.append(dict(c=c, beta_star=bs, beta_closed=bc, beta_W=bw, diff_W_closed=bw - bc, beta_sep_fitted=bsep,
                        gain_W_beta=bw - bs, gain_W_nats=-expo, lamA=lamA, lamR=lamR, pair_slope=slope))
        log(f"{c:4.1f}  {bs:.4f}  {bc:.4f}    {bw:.4f}   {bw - bc:+.4f}       {bsep:.4f}         {bw - bs:+.4f}     {-expo:.4f}        ({lamA:.5f}, {lamR:.5f})")
    with open(os.path.join(HERE, "beta_w.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)


# ---------------------------------------------------------------- threshold (the (d) branch)

def logfit(xs, ys):
    x = np.array(xs, float); y = np.array(ys, float)
    A = np.vstack([x, np.log(x), np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef[0], coef[1], coef[2]


def fine_task(cp):
    vals = []
    for N in N_FIT:
        p = cp / N
        lc = sm.log_connected(N, p)
        vals.append(-sm.log_prob_rel_fast(N, p, N // 2, lc))
    I, b, a = logfit(N_FIT, vals)
    return dict(cprime=cp, fit_rel_half=I, fit_b=b, fit_a=a, ldp=sm.ldp_rate(cp, 0.5), rate_N400=vals[-1] / 400)


def floor60_task(c):
    n = 60
    p = c / n
    lc = sm.log_connected(n, p)
    rows = []
    for k in range(0, 16):
        N, t = sm.forced_sizes(n, k)
        lck = sm.lchoose(n, k)
        lbip = sm.log_prob_bip(N, p, t, lc)
        lrel = sm.log_prob_rel(N, p, t, lc)
        rows.append(dict(n=n, c=c, k=k, N=N, t=t, logB_pair=sm.log_pair_count(n, k, p), logB_sep=lck + lbip, logB_rel=lck + lrel,
                         logB_closed=sm.log_closed_count(n, k, p), log_prob_bip=lbip, log_prob_rel=lrel))
    return rows


def floors(vals: dict[int, float], thresh: float) -> int:
    best = -1
    for k in sorted(vals):
        if vals[k] < math.log(thresh):
            best = k
    return best


def stage_threshold(workers: int) -> None:
    log("== threshold (the (d) branch: finer c near the threshold) ==")
    t0 = time.time()
    with Pool(workers) as pool:
        fits = pool.map(fine_task, CP_FINE)
    with open(os.path.join(HERE, "rate_fits_fine.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fits[0].keys())); w.writeheader(); w.writerows(fits)
    cps = np.array([r["cprime"] for r in fits]); I = np.array([r["fit_rel_half"] for r in fits])

    def I_fit(cp):
        return max(0.0, float(np.interp(cp, cps, I)))

    log(f"fitted rates on {len(CP_FINE)} c′ points in {time.time() - t0:.0f} s; max |fit − LDP| = {max(abs(r['fit_rel_half'] - r['ldp']) for r in fits):.4f}")
    out = []
    log("c    β*      β_sep(cited)  β_sep(fitted)  β_closed  gain_sep(β)  gain_sep(nats)  dg/dβ   slope  share_of_gap  E–M")
    for c in C_FINE:
        bs = sm.beta_star_gnp(c)
        b_cited = sm.beta_sep(c, sm.ldp_rate)
        b_fit = sm.beta_sep(c, I_fit)
        bc = sm.beta_closed(c)
        slope = sm.exponent_slope_at(c, max(bs, 1e-3))
        nats = -sm.sep_exponent(c, bs, sm.ldp_rate) if bs > 0 else float("nan")  # gain at β*: −(sep exponent at β*), pair exponent is 0 there
        em = sm.edwards_mcdermid_poisson(c)
        sl = SLOPES.get(c, float("nan"))
        share = (b_fit - bs) / (sl - bs) if sl == sl else float("nan")
        out.append(dict(c=c, beta_star=bs, beta_sep_cited=b_cited, beta_sep_fitted=b_fit, beta_closed=bc, gain_sep_cited=b_cited - bs,
                        gain_sep_fitted=b_fit - bs, gain_sep_nats_at_beta_star=nats, pair_slope=slope, slope_fitted=sl, share_of_gap=share,
                        edwards_mcdermid=em, best=max(b_fit, bc)))
        log(f"{c:3.1f}  {bs:.4f}  {b_cited:.4f}        {b_fit:.4f}         {bc:.4f}    {b_fit - bs:+.4f}      {nats if nats == nats else float('nan'):.4f}          {slope:.2f}   {sl if sl == sl else float('nan'):.3f}  {share if share == share else float('nan'):.2f}         {em:.3f}")
    with open(os.path.join(HERE, "threshold_fine.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    # the finite floors at n = 60 by the exact P_N(E_bip)
    t1 = time.time()
    with Pool(workers) as pool:
        res = pool.map(floor60_task, C_FINE)
    rows = [r for rs in res for r in rs]
    with open(os.path.join(HERE, "floors_60_rows.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    pilot = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "reports", "scratch", "gnp_pilot", "results.csv"))):
        if int(r["n"]) == 60:
            pilot.setdefault(float(r["c"]), []).append(r)
    log("n = 60: c   pair<.01 pair<1 | sep<.01 sep<1 | rel<.01 | closed<.01 | β*·n  β_sep·n | pilot: graphs, min exact pw, min lower bound (unproved)")
    summ = []
    for c in C_FINE:
        sub = {r["k"]: r for r in rows if r["c"] == c}
        f = lambda key, thr: floors({k: r[key] for k, r in sub.items()}, thr)
        pr = pilot.get(c, [])
        exact = [int(r["width"]) for r in pr if r["status"] in ("refutation", "minor")]
        lbs = [int(r["lower"]) for r in pr if r["status"] not in ("refutation", "minor") and r["lower"] != ""]
        d = dict(n=60, c=c, pair_lt001=f("logB_pair", 0.01), pair_lt1=f("logB_pair", 1), sep_lt001=f("logB_sep", 0.01), sep_lt1=f("logB_sep", 1),
                 rel_lt001=f("logB_rel", 0.01), closed_lt001=f("logB_closed", 0.01), beta_star_n=sm.beta_star_gnp(c) * 60,
                 beta_sep_n=sm.beta_sep(c, sm.ldp_rate) * 60, pilot_graphs=len(pr), pilot_exact=len(exact),
                 pilot_min_pw=min(exact) if exact else "", pilot_min_lb=min(lbs) if lbs else "")
        summ.append(d)
        log(f"  {c:3.1f}   {d['pair_lt001']:3d}     {d['pair_lt1']:3d}   |  {d['sep_lt001']:3d}    {d['sep_lt1']:3d}  |   {d['rel_lt001']:3d}    |    {d['closed_lt001']:3d}     | "
            f"{d['beta_star_n']:5.2f}  {d['beta_sep_n']:5.2f}  | {d['pilot_graphs']:3d}, {d['pilot_min_pw']!s:>3}, {d['pilot_min_lb']!s:>3}")
    with open(os.path.join(HERE, "floors_60.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)
    log(f"floors at n = 60: {time.time() - t1:.0f} s; threshold stage {time.time() - t0:.0f} s")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    log(f"=== run {time.strftime('%Y-%m-%d %H:%M:%S')} stage={a.stage} workers={a.workers} load={os.getloadavg()[0]:.1f}")
    if a.stage in ("all", "check"):
        stage_check(a.workers)
    if a.stage in ("all", "tail"):
        stage_tail(a.workers)
    if a.stage in ("all", "stats"):
        stage_stats()
    if a.stage in ("all", "laplace"):
        stage_laplace()
    if a.stage in ("all", "threshold"):
        stage_threshold(a.workers)


if __name__ == "__main__":
    main()
