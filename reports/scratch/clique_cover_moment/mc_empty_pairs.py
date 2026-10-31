"""Q2(a): is P(fixed pair (A, R) empty) <= prod_j q(s_j) under the real generator?
For each cell (n = m, d), generator and t: N instances; per instance P random disjoint pairs with |A| = t,
|R| = t - 1; the fraction of empty pairs against prod_j q(s_j) from the instance's realised sizes.
Ratio = mean(empty fraction) / mean(prod q), bootstrap CI over instances.  Also the conditional version:
ratio within the instances whose total ones is in the lower / upper half (does the direction depend on sizes?).
    nice -n 19 python3 mc_empty_pairs.py GEN1,GEN2,... [N] [P]
"""
import os, sys, math, time, csv
import numpy as np
from pathlib import Path
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gen_candidates import CANDIDATES
from bound_lib import lq

def uniform_given_sizes(n, m, d, rng, base):
    """control: an instance from `base`, every pattern redrawn as a uniform subset of its realised size."""
    M, t = CANDIDATES[base](n, m, d, rng)
    sizes = M.sum(axis=1)
    U = np.zeros_like(M)
    for i, s in enumerate(sizes):
        U[i, rng.choice(n, int(s), replace=False)] = True
    return U, t

def t_list(n, d, m):
    """t values at which prod q >= 1e-6 for patterns of size d (direct estimation feasible), plus t = 2."""
    out = []
    for t in range(2, n // 2 + 1):
        if m * lq(n, t, d) >= math.log(1e-6): out.append(t)
    return out

def job(args):
    cell, gen, N, P, seed = args
    n, m, d = cell
    rng = np.random.default_rng(seed)
    ts = t_list(n, d, m)
    emp = {t: [] for t in ts}; qs = {t: [] for t in ts}; ones = []
    t0 = time.time()
    for _ in range(N):
        if gen.startswith("uniform:"):
            M, _ = uniform_given_sizes(n, m, d, rng, gen.split(":", 1)[1])
        else:
            M, _ = CANDIDATES[gen](n, m, d, rng)
        if M is None: continue
        Mi = M.astype(np.float32)
        sizes = M.sum(axis=1); ones.append(int(sizes.sum()))
        for t in ts:
            # P random pairs: a random permutation per pair, A = first t, R = next t - 1
            perm = rng.random((P, n)).argsort(axis=1)
            A = np.zeros((n, P), np.float32); R = np.zeros((n, P), np.float32)
            cols = np.arange(P)
            for k in range(t): A[perm[:, k], cols] = 1
            for k in range(t, 2 * t - 1): R[perm[:, k], cols] = 1
            meetsA = (Mi @ A) > 0; meetsR = (Mi @ R) > 0
            empty = ~(meetsA & meetsR).any(axis=0)
            emp[t].append(empty.mean())
            qs[t].append(math.exp(sum(lq(n, t, int(s)) for s in sizes)))
    rows = []
    ones = np.array(ones); med = np.median(ones)
    for t in ts:
        e = np.array(emp[t]); q = np.array(qs[t])
        if e.mean() == 0: 
            rows.append(dict(n=n, m=m, d=d, gen=gen, t=t, N=len(e), P=P, p_emp=0.0, q_mean=q.mean(), ratio=0.0, lo=0.0, hi=0.0, ratio_lowones=math.nan, ratio_highones=math.nan, hits=0))
            continue
        bs = []
        for _ in range(1000):
            idx = rng.integers(0, len(e), len(e)); bs.append(e[idx].mean() / q[idx].mean())
        lo, hi = np.percentile(bs, [2.5, 97.5])
        low = ones <= med; high = ones > med
        rows.append(dict(n=n, m=m, d=d, gen=gen, t=t, N=len(e), P=P, p_emp=e.mean(), q_mean=q.mean(), ratio=e.mean() / q.mean(), lo=lo, hi=hi,
                         ratio_lowones=e[low].mean() / q[low].mean() if low.any() else math.nan,
                         ratio_highones=e[high].mean() / q[high].mean() if high.any() and q[high].mean() > 0 else math.nan,
                         hits=int(e.sum() * P)))
    return rows, time.time() - t0

if __name__ == "__main__":
    gens = sys.argv[1].split(",")
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    P = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    cells = [(n, n, d) for n in (30, 50) for d in (2, 4, 6)]
    jobs = [(c, g, N, P, abs(hash((c, g))) % 2**32) for c in cells for g in gens]
    allrows = []
    with Pool(int(os.environ.get("NPROC", "8"))) as pool:
        for rows, secs in pool.imap_unordered(job, jobs):
            allrows += rows
            for r in rows:
                print(f"({r['n']},{r['m']},{r['d']}) {r['gen']:28s} t={r['t']:2d} p_emp={r['p_emp']:.3e} prod_q={r['q_mean']:.3e} ratio={r['ratio']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}] low/high-ones {r['ratio_lowones']:.3f}/{r['ratio_highones']:.3f} hits={r['hits']}", flush=True)
            print(f"  ({secs:.0f} s)", flush=True)
    with open(HERE / "mc_empty_pairs.csv", "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys()))
        if f.tell() == 0: w.writeheader()
        w.writerows(allrows)
