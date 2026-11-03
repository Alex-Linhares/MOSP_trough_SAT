"""Ten minutes of minor search each, new seed, wider minors (owner, 2026-11-03):
(a) the 11 dense-shoulder instances loop0013 left open (gap338 residual), through
    learning.obstruction_minor._job with 600 s for the ladder and 600 s for the search;
(b) the 22 open dataset classes whose floor is one below the recorded width, through
    run_open with 600 s each, minors at 40-90% of n, seed 7.
Nothing is refuted; a floor meeting the optimum / recorded width is a certificate.
    nice -n 19 python3 reports/scratch/obstruction_search/12_tenmin/run.py
"""
import sys, time, json
from multiprocessing import Pool
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import learning.obstruction_minor as om
HERE = Path(__file__).resolve().parent
SEED = 7
ELEVEN = ["Random-100-100-4-1_0", "Random-100-100-4-3_0", "Random-125-125-2-2_0", "Random-125-125-4-1_0",
          "Random-125-125-4-2_0", "Random-125-125-4-3_0", "Random-125-125-4-4_0", "Random-125-125-6-2_0",
          "Random-125-125-6-3_0", "Random-125-125-6-4_0", "Random-125-125-6-5_0"]
TWENTYTWO = "pwc-16471,pwc-17043,pwc-17257,pwc-17617,pwc-17286,pwc-17381,pwc-17342,pwc-04526,pwc-17359,pwc-17337,pwc-04517,pwc-17343,pwc-17317,pwc-17436,pwc-17321,pwc-17300,pwc-17306,pwc-17398,pwc-17357,pwc-17288,pwc-17427,pwc-17264".split(",")

def part_a():
    om.set_out("12_tenmin")
    led = om.ledger().set_index("instance_name"); inst = om.corpus_instances()
    jobs = []
    for nm in ELEVEN:
        sol = om.solution_record(nm); n = int(led.loc[nm, "n"])
        jobs.append((nm, np.asarray(inst[nm][1].matrix, dtype=int), sol["ordering"] if sol else None,
                     int(led.loc[nm, "optimum"]), 600.0, SEED, True, om.cap_for(n)))
    t0 = time.time(); rows = []
    with Pool(6) as pool:
        for r in pool.imap_unordered(om._job, jobs):
            rows.append(r); pd.DataFrame(rows).to_csv(HERE / "eleven.csv", index=False)
            print(f"[{time.time()-t0:6.0f}s] {r['instance_name']}: opt {r['optimum']} ladder {r['ladder_floor']}@{r['ladder_m']} "
                  f"search {r['search_floor']}@{r['search_m']} ({r['search_source']}) calls {r['ladder_calls']+r['search_calls']}", flush=True)

def part_b():
    om.OPEN_OUT = HERE / "open"; om.OPEN_MINOR_CSV = om.OPEN_OUT / "minor.csv"
    om.OPEN_LADDER_CSV = om.OPEN_OUT / "minor_ladder_points.csv"; om.OPEN_CERT_DIR = om.OPEN_OUT / "certificates"
    om.OPEN_FRACTIONS = (0.40, 0.90)
    om.OPEN_LADDER_FRACTIONS = (0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90)
    om.OPEN_RESTART_FRACTIONS = (0.40, 0.50, 0.60, 0.70, 0.80, 0.90)
    om.OPEN_OUT.mkdir(parents=True, exist_ok=True)
    frame = om.run_open(workers=6, seconds=600.0, cap=20.0, rng_seed=SEED, ids=TWENTYTWO)
    print(frame[["id", "names", "n", "width", "lower", "m_pathwidth", "search_m", "search_source"]].to_string(), flush=True)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "ab"
    if "a" in which: part_a()
    if "b" in which: part_b()
