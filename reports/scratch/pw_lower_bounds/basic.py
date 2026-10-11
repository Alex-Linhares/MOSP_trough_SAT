"""Basic invariants and cheap lower bounds on myciel5/6 (pw 20 / 38).
Scratch for reports/pathwidth_lower_bounds_survey.md. One core, seconds."""
import sys, time
from pathlib import Path
import numpy as np, networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
sys.path.insert(0, str(ROOT))
from readers import read_any, HERE
from pathwidth.graph import masks_from_graph
from pathwidth.bounds import degeneracy, contraction_degeneracy
from satisfiability.expansion_bound import _f_exact

def expansion(masks, n, max_t, budget):
    order = sorted(range(n), key=lambda v: masks[v].bit_count())
    dl = time.monotonic() + budget; levels = []; best = 0
    for t in range(1, max_t + 2):
        v = _f_exact(masks, n, t, order, dl)
        if v is None: break
        levels.append(v); cap = t - 1
        if cap >= 1:
            for i in range(1, min(n, levels[t-1]-1) + 1):
                m = max([s for s in range(1, cap+1) if levels[s-1] <= i], default=0)
                best = max(best, i - m)
    return best, levels

for name, pw in [("myciel5", 20), ("myciel6", 38)]:
    G = read_any(HERE / "coloring" / f"{name}.dgf")
    G = nx.convert_node_labels_to_integers(G)
    masks, _ = masks_from_graph(G)
    n, m = G.number_of_nodes(), G.number_of_edges()
    degs = sorted(d for _, d in G.degree())
    L = nx.laplacian_matrix(G).toarray().astype(float)
    ev = np.linalg.eigvalsh(L); l2, ln = ev[1], ev[-1]; D = max(degs)
    cs = 3*n*l2/(4*D+8*l2) - 1; gima = n*l2/(D+l2) - 1; gima2 = 2*n*l2/(3*ln-l2) - 1
    t0 = time.time(); exp, lev = expansion(masks, n, 10, 60); te = time.time() - t0
    print(f"{name}: n={n} m={m} deg min/med/max={degs[0]}/{degs[n//2]}/{D} avg={2*m/n:.2f} "
          f"omega={max(len(c) for c in nx.find_cliques(G))} girth-tri={sum(nx.triangles(G).values())//3}")
    print(f"  degeneracy={degeneracy(masks)} MMD+={contraction_degeneracy(masks)} pw={pw}")
    print(f"  lambda2={l2:.4f} lambda_n={ln:.3f}  C&S03={cs:.2f}  Gima24={gima:.2f}  Gima24(eq3)={gima2:.2f}")
    print(f"  expansion (Harper, exact f to t<={len(lev)}) = {exp}  f={lev}  {te:.1f}s")
