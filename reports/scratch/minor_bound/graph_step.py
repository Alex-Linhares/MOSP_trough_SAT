"""The minor step alone on graphs whose width is recorded but unproved:
start the ladder at the recorded width W (an achieved upper bound) and ask
whether a minor refutes W - 1 (closes) or raises the lower bound.

usage: graph_step.py RESULTS.csv OUT.csv [--procs 2] [--config default|large] [--limit N]
Reads unproved rows (empty proof, no error) of a bench/results CSV.
"""
import argparse, csv, multiprocessing as mp, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))

CONFIGS = {"default": {}, "retry": dict(on_stall="retry"),
           "large": dict(first_nodes=1_000_000, total_nodes=500_000_000)}
FIELDS = ["name", "n", "m", "recorded_lower", "width", "config", "closed", "new_lower", "size", "rule",
          "step_nodes", "step_seconds", "calls", "error"]


def one(args):
    name, lower, width, config = args
    from readers import HERE, read_any
    import networkx as nx
    from pathwidth.graph import masks_from_graph
    from pathwidth.minor import MinorConfig, MinorLadder
    row = dict(name=name, recorded_lower=lower, width=width, config=config, error="")
    try:
        G = read_any(HERE / name)
        row.update(n=G.number_of_nodes(), m=G.number_of_edges())
        best_lower, closed, cert = int(lower), False, None
        ladder_nodes = ladder_seconds = calls = 0
        for comp in sorted(nx.connected_components(G), key=len, reverse=True):
            masks, _ = masks_from_graph(G.subgraph(comp))
            ladder = MinorLadder(masks, MinorConfig(**CONFIGS[config]))
            t0 = time.monotonic()
            c = ladder.try_refute(int(width) - 1)
            if c is not None:
                closed, cert = True, c
            else:
                c = ladder.raise_lower(best_lower)
                if c is not None and c.refuted + 1 > best_lower:
                    cert = c
            if cert is not None:
                best_lower = max(best_lower, cert.refuted + 1)
            ladder_nodes += ladder.nodes; ladder_seconds += time.monotonic() - t0; calls += ladder.calls
            break                                   # the widest component decides; graphs here are connected
        row.update(closed=closed, new_lower=best_lower, size=cert.size if cert else "",
                   rule=cert.rule if cert else "", step_nodes=ladder_nodes,
                   step_seconds=round(ladder_seconds, 3), calls=calls)
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"[:100]
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results"); ap.add_argument("out")
    ap.add_argument("--procs", type=int, default=2); ap.add_argument("--config", default="default")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(a.results)) if not r["proof"] and not r.get("error") and r["width"]]
    if a.limit:
        rows = rows[:a.limit]
    tasks = [(r["name"], r["lower"], r["width"], a.config) for r in rows]
    with open(a.out, "w", newline="") as fh, mp.get_context("spawn").Pool(a.procs) as pool:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for i, row in enumerate(pool.imap_unordered(one, tasks), 1):
            w.writerow(row); fh.flush()
            print(f"[{i}/{len(tasks)}] {row['name']} W={row['width']} lower {row['recorded_lower']}->{row.get('new_lower')} "
                  f"closed={row.get('closed')} {row.get('step_nodes')} nodes {row.get('step_seconds')}s {row['error']}", flush=True)


if __name__ == "__main__":
    main()
