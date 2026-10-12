"""The descent with the minor step on myciel5/6/7 (default config), and the
step alone on myciel7 with the large config. usage: myciel.py [time_budget]"""
import sys, time, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
import networkx as nx
from readers import read_any, HERE
from pathwidth import solve
from pathwidth.graph import masks_from_graph
from pathwidth.minor import MinorConfig, MinorLadder, replay, check_branch_sets
from pathwidth.search import decide

budget = float(sys.argv[1]) if len(sys.argv) > 1 else 600
for name in ("myciel5", "myciel6", "myciel7"):
    G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / f"{name}.dgf"))
    t = time.time(); s = solve(G, time_budget=budget)
    print(f"{name}: width={s.width} proof={s.proof!r} lower={s.lower} upper_start={s.upper_start} "
          f"nodes={s.nodes} minor_nodes={s.minor_nodes} minor_s={s.minor_seconds:.1f} wall={time.time()-t:.1f}s "
          f"cert={s.minor and (s.minor['size'], s.minor['rule'], s.minor['refuted'])}", flush=True)
    if s.minor:
        masks, _ = masks_from_graph(G)
        minor, labels, br = replay(masks, [(v, -1 if u is None else u) for v, u in s.minor["contractions"]])
        check_branch_sets(masks, minor, labels, br)
        json.dump(s.minor, open(Path(__file__).with_name(f"{name}_certificate.json"), "w"))
        print(f"   certificate replays to {len(minor)} vertices, branch sets OK", flush=True)

# myciel7: the step alone, large config, from the known upper bound 72
G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / "myciel7.dgf"))
masks, _ = masks_from_graph(G)
ladder = MinorLadder(masks, MinorConfig(first_nodes=1_000_000, total_nodes=1_000_000_000))
t = time.time(); c = ladder.try_refute(71)
print(f"myciel7 large: refute 71 -> {c and (c.size, c.rule)} ({time.time()-t:.0f}s)", flush=True)
r = ladder.raise_lower(42)
print(f"myciel7 large: lower -> {r and (r.refuted + 1, r.size, r.rule)}; nodes={ladder.nodes} "
      f"seconds={ladder.seconds:.0f} calls={ladder.calls}", flush=True)
for row in ladder.log:
    print("   ", row, flush=True)
