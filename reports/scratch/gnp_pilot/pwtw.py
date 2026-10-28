"""pw − tw on the G(n, c/n) pilot graphs at n ≤ 60 (survey §7(b) item 4; 2026-10-28).

Reads results.csv (every graph regenerates from its seed; pw is the proved width),
computes the exact treewidth with learning/treewidth: the subset DP at n ≤ 26,
otherwise the decision search between the MMD floor and min(min-fill, pw) — pw is
a free upper bound on tw — under a deadline, so a censored graph carries an
interval [lo, hi] and pw − tw an interval too. Resumable by key. Run niced:
    nice -n 19 python3 reports/scratch/gnp_pilot/pwtw.py --procs 4
Output: pwtw.csv with n, c, sample, seed, m, pw, tw_lo, tw_hi, exact, method, nodes, seconds.
"""
import argparse, csv, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
OUT = HERE / "pwtw.csv"
FIELDS = ["n", "c", "sample", "seed", "m", "pw", "tw_lo", "tw_hi", "exact", "method", "nodes", "seconds"]


def one(args):
    n, c, s, seed, pw, deadline = args
    import networkx as nx
    from learning.treewidth import (masks_from_graph, treewidth_exact, treewidth_decide,
                                    min_fill_upper_bound, mmd_lower_bound, DP_MAX_N)
    G = nx.gnp_random_graph(n, c / n, seed=seed)
    masks = masks_from_graph(G)
    t0 = time.monotonic()
    row = dict(n=n, c=c, sample=s, seed=seed, m=G.number_of_edges(), pw=pw)
    if n <= DP_MAX_N:
        w, _ = treewidth_exact(masks)
        row.update(tw_lo=w, tw_hi=w, exact=True, method="dp", nodes=0)
    else:
        hi, _ = min_fill_upper_bound(masks)
        hi = min(hi, pw)
        lo = mmd_lower_bound(masks)
        nodes = 0; k = lo; censored = False
        while lo < hi:
            if time.monotonic() - t0 > deadline:
                censored = True; break
            st, _, nd = treewidth_decide(masks, k, budget=5_000_000)
            nodes += nd
            if st == "yes": hi = k
            elif st == "no": lo = k + 1; k += 1
            else: censored = True; break
        row.update(tw_lo=lo, tw_hi=hi, exact=(lo == hi), method="bb", nodes=nodes)
    row["seconds"] = round(time.monotonic() - t0, 3)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--max-n", type=int, default=60)
    ap.add_argument("--deadline", type=float, default=120.0)
    a = ap.parse_args()
    src = [r for r in csv.DictReader(open(HERE / "results.csv"))
           if int(r["n"]) <= a.max_n and r["status"] != "upper"]
    done = {(int(r["n"]), float(r["c"]), int(r["sample"])) for r in csv.DictReader(open(OUT))} if OUT.exists() else set()
    jobs = [(int(r["n"]), float(r["c"]), int(r["sample"]), int(r["seed"]), int(r["width"]), a.deadline)
            for r in src if (int(r["n"]), float(r["c"]), int(r["sample"])) not in done]
    jobs.sort(key=lambda j: (j[0], j[1]))
    new = not OUT.exists()
    print(f"{len(jobs)} graphs to do, {a.procs} procs", flush=True)
    with open(OUT, "a", newline="") as f, ProcessPoolExecutor(a.procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new: w.writeheader(); f.flush()
        k = 0
        for row in ex.map(one, jobs, chunksize=4):
            w.writerow(row); f.flush(); k += 1
            if k % 500 == 0: print(f"{k} done", flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
