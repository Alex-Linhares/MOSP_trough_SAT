"""Pass 1 over every open class of the pathwidth dataset (owner, 2026-11-03): ten minutes of
minor search each on 24 niced workers.  For a class with a recorded layout the target is its
width; for a class with none, the C program first runs 60 s on the whole graph to get a layout
(an upper bound; if it proves the width outright the class is closed there), then the search.
Minors at 40-90% of n, never above 1,000 vertices (the engine's limit).  A floor meeting the
target closes the class; nothing refutes a recorded width.  Rows: pass1.csv; certificates:
certificates/<id>/; evidence rows for closures: results_pass1.csv (run_unlimited.py's format).
    setsid nohup nice -n 19 python3 reports/scratch/obstruction_search/13_pass1/pass1.py > pass1.log 2>&1 &
"""
import csv, gzip, json, re, subprocess, sys, time, tempfile
from multiprocessing import Pool
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import learning.obstruction_minor as om
from learning.obstruction_ledger import adjacency_from_edges, _prefix_vs
from paper1.dataset import layout_width
HERE = Path(__file__).resolve().parent
CERT = HERE / "certificates"; CERT.mkdir(exist_ok=True)
CLI = ROOT / "pathwidth_solver" / "cli" / "pathwidth"
SEED, SEARCH_S, C_WHOLE_S, C_CAP = 11, 600.0, 60.0, 20.0
SKIP = {"pwc-15933", "pwc-17632", "pwc-17381"} | {r["id_at_launch"] for r in csv.DictReader(open(ROOT / "reports/scratch/dataset_open/unsolved_unlimited.csv"))}
FIELDS = ["id", "collections", "names", "n", "m", "recorded", "started_from_layout", "width", "proof",
          "lower", "nodes", "seconds", "finished", "status", "order", "minor"]

def graph6(n, edges):
    import networkx as nx
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    return nx.to_graph6_bytes(G, header=False).decode().strip()

def whole_graph_layout(n, edges, seconds):
    p = subprocess.run(["nice", "-n", "19", str(CLI), "-t", str(int(seconds)), "-l", "-v"], input=graph6(n, edges) + "\n",
                       capture_output=True, text=True)
    m = re.search(r"^pathwidth (-?\d+) (\w+)$", p.stdout, re.M)
    lay = re.search(r"^layout((?: \d+)+)$", p.stdout, re.M)
    if not m or not lay: return None
    return int(m.group(1)), m.group(2), [int(x) for x in lay.group(1).split()], dict(re.findall(r"(\w+)=([\d.]+)", p.stderr))

def job(rec):
    t0 = time.monotonic()
    n, edges = int(rec["n"]), [(int(a), int(b)) for a, b in rec["edges"]]
    adj = adjacency_from_edges(n, edges)
    out = dict(id=rec["id"], names=rec["names"], collections=rec["collections"], n=n, m=len(edges),
               recorded_width=rec.get("width"), had_layout=False, c_whole="", width=None, closed=False, proof="", order=None)
    width, layout = rec.get("width"), rec.get("layout") or []
    layout = [int(v) for v in layout] if sorted(int(v) for v in layout) == list(range(n)) else []
    if width is None or not layout:
        r = whole_graph_layout(n, edges, C_WHOLE_S)
        if r is None:
            out.update(status="error: no layout"); out["seconds"] = round(time.monotonic() - t0, 1); return out
        width, status, layout, vals = r
        out.update(c_whole=status, c_whole_lower=vals.get("lower", ""), c_whole_nodes=vals.get("nodes", ""))
        if status in ("refutation", "bound", "minor"):
            order = next((o for o in (layout[::-1], layout) if layout_width(n, edges, o) == width), None)
            out.update(width=width, closed=True, proof=status, order=order, status="ok", seconds=round(time.monotonic() - t0, 1))
            return out
    else:
        out["had_layout"] = True
    out["width"] = int(width)
    # prefix orientation for the evaluator's position
    position = None
    for cand in (layout[::-1], layout):
        if _prefix_vs(adj, cand) == int(width):
            position = [0] * n
            for i, v in enumerate(cand): position[v] = i
            break
    target = int(width) + 1
    lo_m, hi_m = int(round(0.40 * n)), min(int(0.90 * n), 1000)
    deadline = time.monotonic() + SEARCH_S
    ev = om.Evaluator(adj, target, C_CAP, position, deadline=deadline, min_m=lo_m, max_m=hi_m, greedy_upper_max_m=150)
    rows = om.ladder(ev, tuple(f for f in om.OPEN_LADDER_FRACTIONS if f <= 0.90) + (0.90,))
    lad_floor = ev.best_floor; lad_best = ev.best
    if not ev.done() and not ev.at_optimum():
        om.search(ev, SEED, (0.40, 0.50, 0.60, 0.70, 0.80, 0.90))
    out.update(ladder_floor=lad_floor, search_floor=ev.best_floor, search_m=ev.best_m if ev.best else None,
               calls=ev.calls, c_seconds=round(ev.seconds_c, 1), seconds=round(time.monotonic() - t0, 1),
               m_pathwidth=(ev.best_floor - 1) if ev.best else None, status="ok")
    if ev.best is not None:
        d = CERT / rec["id"]; d.mkdir(parents=True, exist_ok=True)
        (d / "instance.txt").write_text(f"{n} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges))
        cert = om.certificate(rec["id"], np.zeros((0, 0), dtype=int), adj, ev.best, out["seconds"],
                              "ladder" if ev.best is lad_best else "search", None, C_CAP)
        (d / "minor.json").write_text(json.dumps(cert))
        if ev.best_floor >= target:
            order = next((o for o in (layout[::-1], layout) if layout_width(n, edges, o) == int(width)), None)
            out.update(closed=True, proof="minor", order=order,
                       minor=json.dumps({"refuted": int(cert["refuted_width"]), "size": int(cert["m"]), "rule": "search",
                                         "contractions": [[v, None if u < 0 else u] for v, u in cert["sequence"]],
                                         "nodes": int(cert.get("c_nodes") or 0),
                                         "certificate": str((d / "minor.json").relative_to(ROOT))}))
    return out

def main():
    cls = {r["id"]: r for r in csv.DictReader(gzip.open(ROOT / "paper1/data/dataset/classes.csv.gz", "rt"))}
    recs = []
    for line in gzip.open(ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt"):
        d = json.loads(line)
        if str(d.get("provenance", "")).startswith("certified") or d["id"] in SKIP: continue
        c = cls[d["id"]]; mem = d.get("members") or [{}]; m0 = mem[0] if isinstance(mem[0], dict) else {"name": str(mem[0])}
        d["names"] = str(m0.get("name", d["id"])); d["collections"] = c["collections"]; recs.append(d)
    recs.sort(key=lambda d: int(d["n"]))
    done = set(pd.read_csv(HERE / "pass1.csv")["id"]) if (HERE / "pass1.csv").exists() else set()
    recs = [d for d in recs if d["id"] not in done]
    print(f"{time.strftime('%F %T')} pass 1: {len(recs)} open classes to run, 24 workers, {SEARCH_S:.0f} s search each "
          f"(+{C_WHOLE_S:.0f} s whole-graph layout where none is recorded), C cap {C_CAP} s, minors 40-90% of n and <= 1000", flush=True)
    k = closed = 0
    with Pool(24) as pool:
        for row in pool.imap_unordered(job, recs, chunksize=1):
            k += 1; closed += bool(row.get("closed"))
            pd.DataFrame([row]).to_csv(HERE / "pass1.csv", mode="a", header=not (HERE / "pass1.csv").exists(), index=False)
            if row.get("closed"):
                ev = {f: "" for f in FIELDS}
                ev.update(id=row["id"], collections=row["collections"].replace("; ", "|"), names=row["names"], n=row["n"], m=row["m"],
                          recorded=row["recorded_width"] if row["recorded_width"] is not None else row["width"],
                          started_from_layout=row["had_layout"], width=row["width"], proof=row["proof"],
                          lower=row["width"], nodes=row.get("c_whole_nodes", "") or 0, seconds=row["seconds"],
                          finished=time.strftime("%Y-%m-%dT%H:%M:%S"), status="ok", order=json.dumps(row["order"]),
                          minor=row.get("minor", ""))
                pd.DataFrame([ev], columns=FIELDS).to_csv(HERE / "results_pass1.csv", mode="a",
                                                          header=not (HERE / "results_pass1.csv").exists(), index=False)
            print(f"{time.strftime('%T')} {k}/{len(recs)} {row['id']} {str(row['names'])[:28]:28} n={row['n']:5} width {row.get('width')} "
                  f"{'[C whole: ' + row['c_whole'] + '] ' if row.get('c_whole') else ''}floor {row.get('m_pathwidth')} "
                  f"({row.get('search_m')} v) {'CLOSED ' + row['proof'] if row.get('closed') else ''} {row.get('seconds')}s  closed so far {closed}", flush=True)
    print(f"{time.strftime('%F %T')} pass 1 done: {k} classes, {closed} closed", flush=True)

if __name__ == "__main__":
    main()
