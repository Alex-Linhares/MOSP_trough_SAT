"""Independent re-check of minor closures from graph_step.py: rebuild each
minor from its (size, rule) by replay, check the branch sets, and re-refute
`W - 1` on it with every dominance rule off (memo only, sound without any
dominance theorem) under a node budget; also with the published rules.

usage: verify_closed.py STEP.csv|RESULTS.csv OUT.csv [--budget N] [--procs 2]
"""
import argparse, csv, multiprocessing as mp, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
FIELDS = ["name", "width", "size", "rule", "replay_ok", "memo_only", "memo_only_nodes", "published",
          "published_nodes", "seconds"]


def one(args):
    name, width, size, rule, budget = args
    import networkx as nx
    from readers import HERE, read_any
    from pathwidth.graph import masks_from_graph
    from pathwidth.minor import check_branch_sets, contraction_sequence, replay
    from pathwidth.search import decide
    t = time.time()
    G = read_any(HERE / name)
    comp = max(nx.connected_components(G), key=len)
    masks, _ = masks_from_graph(G.subgraph(comp))
    minor, labels, br = replay(masks, contraction_sequence(masks, int(size), rule))
    check_branch_sets(masks, minor, labels, br)
    k = int(width)                                   # pw <= W-1 ?
    a = decide(minor, k, subset_rule=False, definite_move=False, old_move=False, memo=True,
               max_nodes=budget)
    b = decide(minor, k, repaired_rules=False, max_nodes=budget)
    return dict(name=name, width=width, size=size, rule=rule, replay_ok=True, memo_only=a.status,
                memo_only_nodes=a.nodes, published=b.status, published_nodes=b.nodes,
                seconds=round(time.time() - t, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step"); ap.add_argument("out")
    ap.add_argument("--budget", type=int, default=50_000_000); ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.step)))
    if "proof" in rows[0]:              # a bench/run.py result file (the descent)
        tasks = [(r["name"], r["width"], r["minor_size"], r["minor_rule"], a.budget)
                 for r in rows if r["proof"] == "minor"]
    else:                               # a graph_step.py file (the step alone)
        tasks = [(r["name"], r["width"], r["size"], r["rule"], a.budget)
                 for r in rows if r["closed"] == "True"]
    with open(a.out, "w", newline="") as fh, mp.get_context("spawn").Pool(a.procs) as pool:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for i, row in enumerate(pool.imap_unordered(one, tasks), 1):
            w.writerow(row); fh.flush()
            if row["memo_only"] == "sat" or row["published"] == "sat":
                print("DISAGREEMENT", row, flush=True)
    rows = list(csv.DictReader(open(a.out)))
    from collections import Counter
    print(len(rows), "checked; memo-only:", Counter(r["memo_only"] for r in rows),
          "published:", Counter(r["published"] for r in rows), flush=True)


if __name__ == "__main__":
    main()
