"""loop0010 item 08: the structured count. Stages (each writes a CSV and a log
under this directory; nothing solved, `solutions/` not read):

    table    beta*_ell for ell = 1..4 at equal spacing on the 18 cells, plus the
             position-optimised ell = 2 exponent at beta* + 0.005 and the
             degenerate-limit sequence at (6, 1)
    floors   the finite floors on the 200 Chu & Stuckey instances: the old
             single pair, ell = 1 at the exact size, ell = 2 at equal spacing
             and with a +-3 position search, against the certified optima
    second   the second moment of the single-pair count X at (6, 1), n = 125,
             exact in the model, its asymptotic exponent, and the simulation
             check at n = 12, 14 (2,000 instances each)
    harper   the deterministic empty-pair (Harper) bound on the 25
             Random-125-125-6 instances, against the random floor and the optimum

    nice -n 19 python3 reports/scratch/structured_count/run.py <stage>
"""
import csv, math, os, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from learning.first_moment import (beta_star, beta_star_nested, chu_stuckey_sizes, empty_pair_count_brute, floors,
                                   log_bound, nested_floors, nested_log_bound, nested_rate_sup, rate,
                                   second_moment_exact, second_moment_rate, equal_positions, log_pairs)

HERE = Path(__file__).resolve().parent
CELLS = [(d, mu) for d in (2, 3, 4, 6, 8, 10) for mu in (0.5, 1, 2)]
NPROC = int(os.environ.get("NPROC", "8"))


def log(msg, f):
    print(msg, flush=True)
    f.write(msg + "\n"); f.flush()


# ---------------------------------------------------------------- table
def cell_job(cell):
    d, mu = cell
    t0 = time.time()
    row = {"d": d, "mu": mu, "e": mu * (d - 1), "beta_star": beta_star(mu, [d])}
    for ell in (1, 2, 3, 4):
        row[f"beta_{ell}"] = beta_star_nested(ell, mu, [d])
    # position-optimised ell = 2 at beta* + 0.005 (if beta* > 0): min exponent over a 31 x 31 grid
    bs = row["beta_star"]
    if bs > 0:
        beta = bs + 0.005
        grid = np.linspace(0.01, 1 - beta - 0.01, 31)
        best = (math.inf, None); neg = 0
        for i, p1 in enumerate(grid):
            for p2 in grid[i + 1:]:
                g = nested_rate_sup(2, beta, mu, [d], positions=[p1, p2], starts=3, cloud=20)[0]
                neg += g < 0
                if g < best[0]:
                    best = (g, (round(p1, 4), round(p2, 4)))
        row.update(beta_probe=beta, g2_min=best[0], g2_argmin=best[1], g2_negative=neg,
                   g1_at_probe=nested_rate_sup(1, beta, mu, [d])[0])
    row["secs"] = time.time() - t0
    return row


def stage_table():
    with open(HERE / "table.log", "w") as f:
        with Pool(NPROC) as pool:
            rows = pool.map(cell_job, CELLS)
        pd.DataFrame(rows).to_csv(HERE / "beta_ell.csv", index=False)
        log("d mu e | beta* | beta*_1 beta*_2 beta*_3 beta*_4 | beta*_2 - beta* | at beta*+0.005: min_pos g2, argmin, #neg of 465, g1", f)
        for r in rows:
            log(f"{r['d']:2d} {r['mu']:>3} {r['e']:4.1f} | {r['beta_star']:.4f} | {r['beta_1']:.4f} {r['beta_2']:.4f} {r['beta_3']:.4f} {r['beta_4']:.4f} | {r['beta_2']-r['beta_star']:+.4f} | "
                + (f"{r['g2_min']:+.4f} {r['g2_argmin']} {r['g2_negative']} {r['g1_at_probe']:+.4f}" if 'g2_min' in r else "(beta* = 0)") + f"  [{r['secs']:.0f} s]", f)
        # the degenerate limit at (6, 1): p_2 - p_1 = eps around the balanced point
        d, mu = 6, 1
        bs = beta_star(mu, [d])
        beta = bs - 0.005
        g1 = nested_rate_sup(1, beta, mu, [d])[0]
        log(f"\n(6, 1) at beta = beta* - 0.005 = {beta:.4f}: single pair exponent {g1:+.5f}; ell = 2 with p_1 = balanced, p_2 = balanced + eps:", f)
        for eps in (0.1, 0.03, 0.01, 0.003, 0.001, 0.0003, 0.0001):
            p1 = (1 - beta) / 2
            g = nested_rate_sup(2, beta, mu, [d], positions=[p1, p1 + eps], starts=3, cloud=20)[0]
            log(f"  eps = {eps:<7} exponent {g:+.5f}  excess over single pair {g - g1:+.5f}  (eps log(1/eps) = {eps*math.log(1/eps):.5f})", f)


# ---------------------------------------------------------------- floors
def floor_job(args):
    key, name, sizes = args
    n, m, d = key
    t0 = time.time()
    old = floors(n, sizes)
    f1 = nested_floors(1, n, sizes)
    f2 = nested_floors(2, n, sizes)
    # position search at ell = 2: +-3 around equal spacing, at k = f2 floor (<1) and above
    k = f2[0] - 2
    best_k = k
    for kk in range(max(0, k), n):
        base = [int(round(p)) for p in equal_positions(2, n, kk)]
        found = False
        for a in range(-3, 4):
            for b in range(-3, 4):
                pos = [base[0] + a, base[1] + b]
                if pos[0] < 1 or pos[1] <= pos[0] or n - pos[1] - kk < 0:
                    continue
                if nested_log_bound(2, n, sizes, kk, pos) < 0:
                    found = True; break
            if found: break
        if found:
            best_k = kk
        else:
            break
    return dict(instance=name + "_0", n=n, m=m, d=d, floor_old=old[0], floor_old_001=old[1], floor_1=f1[0], floor_1_001=f1[1],
                floor_2=f2[0], floor_2_001=f2[1], floor_2_pos=best_k + 2, secs=time.time() - t0)


def stage_floors():
    classes = chu_stuckey_sizes()
    jobs = [(key, name, sizes) for key in sorted(classes) for name, sizes in classes[key]["instances"]]
    ex = pd.read_csv("learning/data/excess.csv", usecols=["instance_name", "optimum", "provenance", "source"])
    ex = ex[ex.instance_name.str.startswith("Random-")]
    opt = dict(zip(ex.instance_name, ex.optimum)); prov = dict(zip(ex.instance_name, ex.provenance))
    with open(HERE / "floors.log", "w") as f, Pool(NPROC) as pool:
        rows = pool.map(floor_job, jobs)
        for r in rows:
            r["optimum"] = opt[r["instance"]]; r["provenance"] = prov[r["instance"]]
        df = pd.DataFrame(rows)
        df.to_csv(HERE / "floors_cs.csv", index=False)
        assert (df.provenance.str.startswith("certified")).all()
        log(f"{len(df)} instances, {df.secs.sum():.0f} s of instance time", f)
        for col in ("floor_old", "floor_1", "floor_2", "floor_2_pos", "floor_old_001", "floor_1_001", "floor_2_001"):
            viol = int((df.optimum < df[col]).sum())
            log(f"{col:14s}: violations {viol}; mean {df[col].mean():.2f}; mean gap to optimum {(df.optimum - df[col]).mean():.2f}", f)
        log("\nfloor_2 vs floor_1 (same |R| convention): higher on %d, equal on %d, lower on %d" % (
            int((df.floor_2 > df.floor_1).sum()), int((df.floor_2 == df.floor_1).sum()), int((df.floor_2 < df.floor_1).sum())), f)
        log("floor_2_pos vs floor_1: higher on %d, equal on %d, lower on %d" % (
            int((df.floor_2_pos > df.floor_1).sum()), int((df.floor_2_pos == df.floor_1).sum()), int((df.floor_2_pos < df.floor_1).sum())), f)
        log("floor_1 vs floor_old: higher on %d, equal on %d, lower on %d" % (
            int((df.floor_1 > df.floor_old).sum()), int((df.floor_1 == df.floor_old).sum()), int((df.floor_1 < df.floor_old).sum())), f)
        log("\nclass means: (n, m, d) | opt | old | ell=1 | ell=2 | ell=2 pos | old<0.01 | ell=1<0.01 | ell=2<0.01", f)
        for key, g in df.groupby(["n", "m", "d"]):
            log(f"{key} | {g.optimum.mean():6.1f} | {g.floor_old.mean():6.1f} | {g.floor_1.mean():6.1f} | {g.floor_2.mean():6.1f} | {g.floor_2_pos.mean():6.1f} | "
                f"{g.floor_old_001.mean():6.1f} | {g.floor_1_001.mean():6.1f} | {g.floor_2_001.mean():6.1f}", f)


# ---------------------------------------------------------------- second moment
def sim_job(args):
    n, m, d, t, N, seed = args
    rng = np.random.default_rng(seed)
    xs = []
    for _ in range(N):
        masks = [int(sum(1 << int(v) for v in rng.choice(n, size=d, replace=False))) for _ in range(m)]
        xs.append(empty_pair_count_brute(masks, n, t))
    return n, m, d, t, np.array(xs, dtype=float)


def stage_second():
    with open(HERE / "second_moment.log", "w") as f:
        d, mu, n = 6, 1, 125
        sizes = [d] * n
        bs = beta_star(mu, [d])
        log(f"(6, 1): beta* = {bs:.4f}; fixed size 6, m = n = 125 (the uniform model)", f)
        log("\nexact second moment at n = 125: k | t | log10 E[X] | log10 E[X^2] | E[X^2]/E[X]^2 | log10 P(fixed pair empty)", f)
        rows = []
        for k in range(50, 86, 3):
            t = (n - k + 1) // 2
            t0 = time.time()
            lEX, lEX2, ratio = second_moment_exact(n, t, sizes)
            lp = lEX - log_pairs(n, t)
            rows.append(dict(k=k, t=t, log10_EX=lEX / math.log(10), log10_EX2=lEX2 / math.log(10), ratio=ratio, log10_pair=lp / math.log(10), secs=time.time() - t0))
            log(f"{k:3d} | {t:2d} | {lEX/math.log(10):8.2f} | {lEX2/math.log(10):8.2f} | {ratio:.4g} | {lp/math.log(10):8.2f}  [{time.time()-t0:.0f} s]", f)
        pd.DataFrame(rows).to_csv(HERE / "second_moment_125.csv", index=False)
        log("\nasymptotic: a = (1 - beta)/2 | beta | g(a) | sup table exponent | 2 g(a) | ratio exponent (sup - 2g) | table (AA' AR' AO' RA' RR' RO' OA' OR' OO') | product table?", f)
        arows = []
        for beta in (bs - 0.1, bs - 0.05, bs - 0.02, bs, bs + 0.02, bs + 0.05):
            a = (1 - beta) / 2
            sup, twice, table = second_moment_rate(a, mu, [d])
            prod = np.outer([a, a, 1 - 2 * a], [a, a, 1 - 2 * a]).ravel()
            dev = float(np.abs(table - prod).max())
            arows.append(dict(beta=beta, a=a, g=rate(a, mu, [d]), sup=sup, twice=twice, excess=sup - twice, max_dev_from_product=dev))
            log(f"{a:.4f} | {beta:.4f} | {rate(a, mu, [d]):+.5f} | {sup:+.5f} | {twice:+.5f} | {sup-twice:+.5f} | {np.round(table, 4)} | max |table - product| = {dev:.2e}", f)
        pd.DataFrame(arows).to_csv(HERE / "second_moment_rate.csv", index=False)
        log("\nsimulation check (2,000 instances per cell, X enumerated): n m d t | mean X | E[X] exact | mean X^2 | E[X^2] exact | ratio sim | ratio exact | P(X > 0) sim", f)
        jobs = [(12, 12, 6, 3, 250, s) for s in range(8)] + [(14, 14, 6, 3, 250, 8 + s) for s in range(8)] + [(14, 14, 6, 4, 250, 16 + s) for s in range(8)]
        with Pool(NPROC) as pool:
            res = pool.map(sim_job, jobs)
        srows = []
        for key in sorted(set(r[:4] for r in res)):
            xs = np.concatenate([r[4] for r in res if r[:4] == key])
            n_, m_, d_, t_ = key
            lEX, lEX2, ratio = second_moment_exact(n_, t_, [d_] * m_)
            se1 = xs.std() / math.sqrt(len(xs)); se2 = (xs ** 2).std() / math.sqrt(len(xs))
            srows.append(dict(n=n_, m=m_, d=d_, t=t_, N=len(xs), mean_X=xs.mean(), EX=math.exp(lEX), se_X=se1, mean_X2=(xs ** 2).mean(), EX2=math.exp(lEX2), se_X2=se2,
                              ratio_sim=(xs ** 2).mean() / xs.mean() ** 2 if xs.mean() > 0 else math.nan, ratio_exact=ratio, p_positive=(xs > 0).mean()))
            log(f"{n_} {m_} {d_} {t_} | {xs.mean():.3f} ± {se1:.3f} | {math.exp(lEX):.3f} | {(xs**2).mean():.2f} ± {se2:.2f} | {math.exp(lEX2):.2f} | {srows[-1]['ratio_sim']:.3f} | {ratio:.3f} | {(xs > 0).mean():.3f}", f)
        pd.DataFrame(srows).to_csv(HERE / "second_moment_sim.csv", index=False)


# ---------------------------------------------------------------- harper
def harper_job(args):
    path, name, max_t, budget = args
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound
    inst = MOSPInstance.from_benchmark_file(path)[0]
    eb = expansion_bound(inst, max_t=max_t, time_budget=budget)
    return dict(instance=name + "_0", n=inst.n_customers, harper=eb.value, cap=eb.cap, levels=str(eb.levels), complete=eb.complete, secs=eb.seconds)


def stage_harper():
    from learning.first_moment import CS_DIR
    classes = chu_stuckey_sizes()
    ex = pd.read_csv("learning/data/excess.csv", usecols=["instance_name", "optimum"])
    opt = dict(zip(ex.instance_name, ex.optimum))
    budget = float(os.environ.get("HARPER_BUDGET", "240"))
    jobs = [(CS_DIR / f"{name}.txt", name, 12, budget) for name, _ in classes[(125, 125, 6)]["instances"]]
    with open(HERE / "harper.log", "w") as f, Pool(NPROC) as pool:
        rows = pool.map(harper_job, jobs)
        for r, (name, sizes) in zip(rows, classes[(125, 125, 6)]["instances"]):
            r["optimum"] = opt[r["instance"]]
            r["floor_old"], r["floor_old_001"] = floors(125, sizes)
            r["floor_1"], _ = nested_floors(1, 125, sizes)
        df = pd.DataFrame(rows)
        df.to_csv(HERE / "harper_125_6.csv", index=False)
        log(f"Random-125-125-6, budget {budget:.0f} s per instance, max_t 12: instance | optimum | Harper bound (cap reached, complete) | random floor <1 (old / exact size) | levels f(1..) | s", f)
        for r in rows:
            log(f"{r['instance']} | {r['optimum']} | {r['harper']} (cap {r['cap']}, {'complete' if r['complete'] else 'budget'}) | {r['floor_old']} / {r['floor_1']} | {r['levels']} | {r['secs']:.0f}", f)
        log(f"\nmeans: optimum {df.optimum.mean():.2f}, Harper {df.harper.mean():.2f}, floor old {df.floor_old.mean():.2f}, floor exact-size {df.floor_1.mean():.2f}; "
            f"Harper - floor_1 {(df.harper - df.floor_1).mean():.2f}; optimum - Harper {(df.optimum - df.harper).mean():.2f}; Harper >= floor_1 on {(df.harper >= df.floor_1).sum()} of {len(df)}", f)




# ---------------------------------------------------------------- slack: the necessary condition at sizes where Harper is exact
def slack_job(args):
    frame, cell_text, index, name, optimum, budget = args
    from learning.ensemble import Cell, generate
    from satisfiability.expansion_bound import expansion_bound
    cell = Cell(cell_text[0], cell_text[1], cell_text[2], cell_text[3])
    inst = generate(cell, index)
    assert inst.name == name, (inst.name, name)
    sizes = [int(s) for s in np.asarray(inst.matrix).sum(axis=0)]
    n = inst.n_customers
    eb = expansion_bound(inst, max_t=12, time_budget=budget)
    old = floors(n, sizes)
    f1 = nested_floors(1, n, sizes)
    return dict(frame=frame, instance=name, n=n, m=inst.n_patterns, optimum=optimum, harper=eb.value, cap=eb.cap, complete=eb.complete,
                levels=str(eb.levels), secs=eb.seconds, floor_old=old[0], floor_old_001=old[1], floor_1=f1[0], floor_1_001=f1[1])


def stage_slack():
    budget = float(os.environ.get("SLACK_BUDGET", "60"))
    jobs = []
    for frame in ("results.csv", "results_upward.csv"):
        df = pd.read_csv(f"learning/data/ensemble/{frame}")
        sub = df[(df.generator == "fixed") & (df.param == 6) & (df.m == df.n) & (df.n >= 30)]
        assert sub.certified.all()
        for r in sub.itertuples():
            jobs.append((frame, (r.generator, int(r.n), int(r.m), float(r.param)), int(r.index), r.instance_name, int(r.optimum), budget))
    with open(HERE / "slack.log", "w") as f, Pool(NPROC) as pool:
        rows = pool.map(slack_job, jobs)
        df = pd.DataFrame(rows)
        df.to_csv(HERE / "slack_6_1.csv", index=False)
        df["pw"] = df.optimum - 1
        df["ep"] = df.harper - 1            # Harper's bound on vs = pw, i.e. the empty-pair necessary condition on the instance
        df["fl"] = df.floor_1 - 1
        log(f"(6, 1) record instances, fixed generator, m = n, certified optima read from the frames; Harper's bound with max_t 12 and {budget:.0f} s budget", f)
        log("n | N | complete | cap (min/median) | mean pw | mean Harper(pw) | mean floor_1(pw) | pw - Harper | Harper - floor | Harper >= floor on | Harper = pw on | seconds (mean/max)", f)
        for n, g in df.groupby("n"):
            log(f"{n:3d} | {len(g)} | {int(g.complete.sum())} | {g.cap.min()}/{g.cap.median():.0f} | {g.pw.mean():.2f} | {g.ep.mean():.2f} | {g.fl.mean():.2f} | "
                f"{(g.pw - g.ep).mean():.2f} | {(g.ep - g.fl).mean():.2f} | {(g.ep >= g.fl).sum()} | {(g.ep == g.pw).sum()} | {g.secs.mean():.1f}/{g.secs.max():.0f}", f)
        log("\nper-size distribution of pw - Harper (the slack of the necessary condition on the instance) and Harper - floor (the slack of the union bound):", f)
        for n, g in df.groupby("n"):
            log(f"{n:3d}: pw - Harper quantiles 10/50/90 = {np.percentile(g.pw - g.ep, [10, 50, 90])}; Harper - floor = {np.percentile(g.ep - g.fl, [10, 50, 90])}; floor_1 violations {(g.optimum < g.floor_1).sum()} (< 1), {(g.optimum < g.floor_1_001).sum()} (< 0.01)", f)


if __name__ == "__main__":
    {"table": stage_table, "floors": stage_floors, "second": stage_second, "harper": stage_harper, "slack": stage_slack}[sys.argv[1]]()
