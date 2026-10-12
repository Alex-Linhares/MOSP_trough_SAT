"""Slowdown and gain of the minor step on a sample of certified corpus
instances with >= 40 customers: `customer_search.solve` with the step off
and on (default config), same floor, same budget. Nothing is saved.

usage: mosp_sample.py OUT.csv [--count 150] [--time 60] [--procs 2]
"""
import argparse, csv, json, multiprocessing as mp, random, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
FIELDS = ["instance", "n", "m", "optimum", "floor", "mode", "value", "proof", "nodes", "minor_nodes",
          "seconds", "lower"]
SKIP = ("Random-125-125-2-", "Random-125-125-4-")       # the day-long classes


def one(args):
    name, opt, budget = args
    from benchmarks.ratchet import find_instances
    from satisfiability.customer_search import solve
    from satisfiability.mosp_solver import _lower_bound
    from satisfiability.relaxation import MinorConfig
    inst = next(i for i in find_instances([name], ROOT / "benchmarks/instances") if i.name == name)
    floor = _lower_bound(inst)
    rows = []
    for mode, minor in (("off", False), ("on", MinorConfig())):
        t = time.monotonic()
        s = solve(inst, lower=floor, minor=minor, time_budget=budget)
        rows.append(dict(instance=name, n=inst.n_customers, m=inst.n_patterns, optimum=opt, floor=floor,
                         mode=mode, value=s.value, proof=s.proof, nodes=s.nodes, minor_nodes=s.minor_nodes,
                         seconds=round(time.monotonic() - t, 3), lower=s.lower))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--count", type=int, default=150)
    ap.add_argument("--time", type=float, default=60); ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    pool_names = []
    for p in sorted((ROOT / "solutions").glob("*.json")):
        d = json.loads(p.read_text())
        name = d["instance_name"]
        if d["n_customers"] >= 40 and d["provenance"].startswith("certified") and not name.startswith(SKIP):
            pool_names.append((name, d["mosp_value"]))
    random.seed(20261012)
    chosen = random.sample(pool_names, min(a.count, len(pool_names)))
    print(len(pool_names), "eligible;", len(chosen), "chosen", flush=True)
    with open(a.out, "w", newline="") as fh, mp.get_context("spawn").Pool(a.procs) as pool:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for i, rows in enumerate(pool.imap_unordered(one, [(n, o, a.time) for n, o in chosen]), 1):
            w.writerows(rows); fh.flush()
            off, on = rows
            print(f"[{i}/{len(chosen)}] {off['instance']} n={off['n']} off {off['proof'] or '-'} {off['nodes']} "
                  f"{off['seconds']}s | on {on['proof'] or '-'} {on['nodes']} ({on['minor_nodes']}) {on['seconds']}s",
                  flush=True)


if __name__ == "__main__":
    main()
