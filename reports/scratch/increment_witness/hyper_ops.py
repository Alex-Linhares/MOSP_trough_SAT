"""Single minor operations on Q_d (vertex-transitive, edge-transitive: one test each)."""
import iw, json
from concurrent.futures import ThreadPoolExecutor
def ops(d):
    G = iw.hypercube(d); out = {}
    Gv = G.copy(); Gv.remove_node(0); out["delete vertex 0"] = Gv
    Ge = G.copy(); Ge.remove_edge(0, 1); out["delete edge 0-1"] = Ge
    Gc, _ = iw.apply_seq(G, [(1, 0)]); out["contract edge 1->0"] = Gc
    return [(d, name, H) for name, H in out.items()]
jobs = [j for d in range(3, 7) for j in ops(d)]
def run(j):
    d, name, H = j
    w, st, r = iw.proved_width(H, t=300)
    return dict(d=d, op=name, n=H.number_of_nodes(), m=H.number_of_edges(), width=w if w is not None else r["width"], status=st, seconds=round(r["seconds"], 2))
with ThreadPoolExecutor(max_workers=2) as ex:
    res = list(ex.map(run, jobs))
for r in res: print(r)
json.dump(res, open("hyper_ops.json", "w"), indent=1)
