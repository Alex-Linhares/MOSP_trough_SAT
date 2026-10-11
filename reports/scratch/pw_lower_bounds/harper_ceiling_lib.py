"""Upper bound on Harper's vertex-isoperimetric value max_i Phi(i),
Phi(i) = min_{|S|=i} |{v in S : N(v) not inside S}|, by local search.
Any set found gives Phi(i) <= its boundary, so max_i (best found) caps what
the isoperimetric method (our expansion bound, at any depth) can ever prove."""
import sys, random, time
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
from readers import read_any, HERE

def phi_search(G, i, iters, rng, start=None):
    n = G.number_of_nodes(); nb = [list(G[v]) for v in range(n)]
    S = set(start) if start else set(rng.sample(range(n), i))
    out = [sum(1 for u in nb[v] if u not in S) for v in range(n)]  # neighbours outside S
    bnd = sum(1 for v in S if out[v] > 0)
    best = bnd; T = 1.0
    inS = list(S); outS = [v for v in range(n) if v not in S]
    pos_in = {v: k for k, v in enumerate(inS)}; pos_out = {v: k for k, v in enumerate(outS)}
    def move(a, b):  # a leaves S, b enters; return new boundary, apply
        nonlocal bnd
        S.remove(a); S.add(b)
        for u in nb[a]: out[u] += 1
        for u in nb[b]: out[u] -= 1
        return sum(1 for v in S if out[v] > 0)
    for it in range(iters):
        a = inS[rng.randrange(len(inS))] if inS else None
        b = outS[rng.randrange(len(outS))] if outS else None
        if a is None or b is None: break
        old = bnd
        new = move(a, b)
        if new <= old or rng.random() < pow(2.718, (old - new) / T):
            bnd = new
            ka, kb = pos_in.pop(a), pos_out.pop(b)
            inS[ka] = b; pos_in[b] = ka; outS[kb] = a; pos_out[a] = kb
            best = min(best, bnd)
        else:
            move(b, a)
        T = max(0.05, 1.0 * (1 - it / iters))
    return best

