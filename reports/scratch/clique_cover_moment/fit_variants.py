"""Single-process fit of the intermediate variants on the d <= 4 classes (same statistics as fit_generators.py)."""
import sys, math
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_generators import observed, job, STATS
obs = observed()
for cand in sys.argv[1].split(","):
    zs = []
    for key in sorted(obs):
        if key[2] > 4: continue
        key, cand, sims, tries, secs = job((key, cand, 200, abs(hash((key, cand))) % 2**32))
        o = obs[key]; line = []
        for s in ("ones", "row_var", "col_var", "frac_row2", "frac_col1"):
            ov = np.mean([x[s] for x in o]); sv = np.array([x[s] for x in sims], float)
            z = (ov - sv.mean()) / (sv.std(ddof=1) / math.sqrt(5)) if sv.std() > 0 else 0.0
            zs.append(min(abs(z), 100)); line.append(f"{s} obs {ov:7.2f} sim {sv.mean():7.2f} z {z:+5.2f}")
        print(f"{key} {cand:30s} acc={len(sims)/tries:.3f} | " + " | ".join(line), flush=True)
    print(f"{cand}: mean z^2 over d<=4 classes and 5 statistics = {np.mean(np.array(zs)**2):.2f}, share |z|>3 = {np.mean(np.array(zs)>3):.3f}\n", flush=True)
