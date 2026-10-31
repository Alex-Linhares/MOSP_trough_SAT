"""Q2(b): generate instances from a candidate generator at n = m in {30, 40}, d in {2,4,6,8,10}, solve each exactly
and count how often the certified optimum falls below the floor the first-moment bound gives at < 0.01 and at < 1.
Solutions are persisted under sim_solutions/ (owner's rule: never solutions_dir=None).
    nice -n 19 python3 floor_violation.py GEN N
"""
import os, sys, time, csv, math
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from pathlib import Path
from multiprocessing import Pool
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))
from gen_candidates import CANDIDATES
from bound_lib import floors

def job(args):
    gen, n, m, d, seed = args
    from mosp.instance import MOSPInstance
    from satisfiability import solve_mosp_exact
    rng = np.random.default_rng(seed)
    M, tries = CANDIDATES[gen](n, m, d, rng)
    if M is None: return None
    sizes = [int(s) for s in M.sum(axis=1)]
    f1, f2 = floors(n, sizes)
    inst = MOSPInstance.from_matrix(M.T.astype(np.int8), name=f"sim-{gen}-{n}-{m}-{d}-{seed}")
    t0 = time.time()
    stats = {}
    val, order = solve_mosp_exact(inst, solutions_dir=HERE / "sim_solutions", stats=stats)
    return dict(gen=gen, n=n, m=m, d=d, seed=seed, ones=sum(sizes), opt=int(val), floor1=f1, floor2=f2, secs=time.time() - t0, nodes=stats.get("nodes"))

if __name__ == "__main__":
    gen = sys.argv[1]; N = int(sys.argv[2])
    ds = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [2, 4, 6, 8, 10]
    ns = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [30, 40]
    jobs = [(gen, n, n, d, 10_000_000 + n * 10000 + d * 1000 + i) for n in ns for d in ds for i in range(N)]
    out = HERE / "floor_violation.csv"
    rows = []
    t0 = time.time()
    with Pool(int(os.environ.get("NPROC", "8"))) as pool:
        for i, r in enumerate(pool.imap_unordered(job, jobs, chunksize=4)):
            if r: rows.append(r)
            if (i + 1) % 200 == 0: print(f"{i+1}/{len(jobs)} done, {time.time()-t0:.0f} s", flush=True)
    with open(out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if f.tell() == 0: w.writeheader()
        w.writerows(rows)
    print("\nclass | N | mean opt | mean floor<1 | mean floor<0.01 | P(opt < floor<1) | P(opt < floor<0.01) | P(opt == floor<0.01) | total solve s")
    for n in ns:
        for d in ds:
            R = [r for r in rows if r["n"] == n and r["d"] == d]
            if not R: continue
            v1 = np.mean([r["opt"] < r["floor1"] for r in R]); v2 = np.mean([r["opt"] < r["floor2"] for r in R]); e2 = np.mean([r["opt"] == r["floor2"] for r in R])
            print(f"({n},{n},{d}) | {len(R)} | {np.mean([r['opt'] for r in R]):.2f} | {np.mean([r['floor1'] for r in R]):.2f} | {np.mean([r['floor2'] for r in R]):.2f} | {v1:.4f} | {v2:.4f} | {e2:.4f} | {sum(r['secs'] for r in R):.0f}")
