"""Pooled size histograms, observed vs the best-fit candidate; across-file dispersion of ones; size correlation."""
import sys, glob, collections, csv, math
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_candidates import CANDIDATES, stats
ROOT = Path(__file__).resolve().parents[3]
CAND = sys.argv[1] if len(sys.argv) > 1 else "bern_padC1_padP2_conn"
obs = collections.defaultdict(list)
for f in sorted(glob.glob(str(ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-*.txt"))):
    L = [l for l in open(f).read().split("\n") if l.strip()]
    m, n = map(int, L[0].split())
    M = np.array([[int(x) for x in L[1 + i].split()] for i in range(m)], bool)
    obs[(n, m, int(Path(f).stem.split("-")[3]))].append(M)
rng = np.random.default_rng(7)
print("class | side | observed histogram (fraction at size 1,2,3,...) vs simulated | obs mean/var | sim mean/var | obs sd of ones across 5 files vs sim sd of ones per instance")
for key in sorted(obs):
    n, m, d = key
    if d not in (2, 4): continue
    sims = []
    while len(sims) < 200:
        M, _ = CANDIDATES[CAND](n, m, d, rng)
        if M is not None: sims.append(M)
    for side, ax in (("patterns", 1), ("customers", 0)):
        o = np.concatenate([M.sum(axis=ax) for M in obs[key]]); s = np.concatenate([M.sum(axis=ax) for M in sims])
        K = max(o.max(), s.max()) + 1
        ho = np.bincount(o, minlength=K) / len(o); hs = np.bincount(s, minlength=K) / len(s)
        print(f"{key} {side:9s} obs " + " ".join(f"{x:.3f}" for x in ho[1:12]) + f" | sim " + " ".join(f"{x:.3f}" for x in hs[1:12]) + f" | {o.mean():.2f}/{o.var():.2f} | {s.mean():.2f}/{s.var():.2f}")
    oo = np.array([M.sum() for M in obs[key]]); ss = np.array([M.sum() for M in sims])
    print(f"{key} ones: obs {oo.tolist()} sd {oo.std(ddof=1):.1f} | sim mean {ss.mean():.1f} sd {ss.std(ddof=1):.1f}")
print("\nrowcol_corr (correlation over incidences between the pattern's size and its customer's count): obs vs sim, from fit_generators.csv")
for r in csv.DictReader(open(Path(__file__).resolve().parent / "fit_generators.csv")):
    if r["cand"] == CAND:
        print(f"({r['n']},{r['m']},{r['d']}) obs {float(r['rowcol_corr_obs']):+.3f} sim {float(r['rowcol_corr_sim']):+.3f} z {float(r['rowcol_corr_z']):+.2f}")
