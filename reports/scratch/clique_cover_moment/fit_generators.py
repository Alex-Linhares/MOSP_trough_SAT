"""Fit the candidate generators to the 200 files: per class (n, m, d), simulate N accepted instances per
candidate, compare the class's 5-file mean of each statistic with the simulated distribution of a 5-file mean.
    nice -n 19 python3 fit_generators.py [N]
Writes fit_generators.csv (every class x candidate x statistic) and prints a summary."""
import sys, glob, collections, json, math, time
import numpy as np
from pathlib import Path
from multiprocessing import Pool
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_candidates import CANDIDATES, stats
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 200
STATS = ["ones", "row_var", "row_max", "col_var", "col_min", "col_max", "frac_row2", "frac_row3", "frac_col1", "frac_col2", "rowcol_corr"]

def observed():
    by = collections.defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-*.txt"))):
        L = [l for l in open(f).read().split("\n") if l.strip()]
        m, n = map(int, L[0].split())
        M = np.array([[int(x) for x in L[1 + i].split()] for i in range(m)], bool)
        d = int(Path(f).stem.split("-")[3])
        by[(n, m, d)].append(stats(M))
    return by

def job(args):
    key, cand, N, seed = args
    n, m, d = key
    rng = np.random.default_rng(seed)
    g = CANDIDATES[cand]
    out = []; tries = 0; t0 = time.time()
    for _ in range(N):
        M, t = g(n, m, d, rng); tries += t
        if M is None: break
        out.append(stats(M))
    return key, cand, out, tries, time.time() - t0

if __name__ == "__main__":
    obs = observed()
    keys = sorted(obs)
    jobs = [(k, c, N, abs(hash((k, c))) % 2**32) for k in keys for c in CANDIDATES]
    rows = []
    with Pool(8) as pool:
        for key, cand, sims, tries, secs in pool.imap_unordered(job, jobs):
            n, m, d = key
            o = obs[key]
            rec = dict(n=n, m=m, d=d, cand=cand, n_sim=len(sims), acc=len(sims) / tries if tries else 0.0, secs=secs)
            for s in STATS:
                ov = np.mean([x[s] for x in o])
                if sims:
                    sv = np.array([x[s] for x in sims], float)
                    mu, sd = sv.mean(), sv.std(ddof=1) if len(sv) > 1 else 0.0
                    z = (ov - mu) / (sd / math.sqrt(5)) if sd > 0 else (0.0 if abs(ov - mu) < 1e-12 else math.inf)
                else:
                    mu, z = math.nan, math.nan
                rec[s + "_obs"] = ov; rec[s + "_sim"] = mu; rec[s + "_z"] = z
            rows.append(rec)
            print(f"{key} {cand:24s} n_sim={len(sims):3d} acc={rec['acc']:.4f} ones obs {rec['ones_obs']:7.1f} sim {rec['ones_sim']:7.1f} z={rec['ones_z']:6.2f} | row_var z={rec['row_var_z']:6.2f} col_var z={rec['col_var_z']:6.2f} col_min z={rec['col_min_z']:6.2f} frac_row2 z={rec['frac_row2_z']:6.2f}", flush=True)
    import csv
    with open(HERE / "fit_generators.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # summary: mean z^2 per candidate over classes and statistics (inf -> 100)
    print("\ncandidate | classes simulated | mean z^2 over (class, statistic) | share |z| > 3 | min acceptance")
    for c in CANDIDATES:
        R = [r for r in rows if r["cand"] == c and r["n_sim"] > 0]
        zs = np.array([min(abs(r[s + "_z"]), 100) for r in R for s in STATS if not math.isnan(r[s + "_z"])])
        print(f"{c:24s} | {len(R):2d} | {np.mean(zs**2):8.2f} | {np.mean(zs > 3):.3f} | {min(r['acc'] for r in R):.4f}")
