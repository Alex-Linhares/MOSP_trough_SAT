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

for name, pw in [("myciel5", 20), ("myciel6", 38)]:
    G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / f"{name}.dgf"))
    n = G.number_of_nodes(); rng = random.Random(1); t0 = time.time()
    sys.path.insert(0, str(ROOT / "pathwidth_solver"))
    from pathwidth.graph import masks_from_graph
    from pathwidth.solve import initial_upper_bound
    masks, _ = masks_from_graph(G)
    seeds = [initial_upper_bound(masks)[1]]
    for r in range(200):   # BFS / min-degree greedy layouts from random roots
        root = rng.randrange(n); order = [root]; seen = {root}; inside = set([root])
        while len(order) < n:
            cand = [v for v in range(n) if v not in seen]
            # grow by the vertex adding fewest new boundary-ish neighbours, random ties
            cand.sort(key=lambda v: (sum(1 for u in G[v] if u not in seen) - sum(1 for u in G[v] if u in seen), rng.random()))
            v = cand[0]; order.append(v); seen.add(v)
        seeds.append(order)
    def bnd(S):
        return sum(1 for v in S if any(u not in S for u in G[v]))
    prof = []
    for i in range(1, n):
        best_seed = min((set(o[:i]) for o in seeds), key=bnd)
        b0 = bnd(best_seed)
        b1 = min(phi_search(G, i, 6000, rng, start=best_seed) for _ in range(2))
        prof.append(min(b0, b1))
    imax = max(range(len(prof)), key=lambda k: prof[k])
    print(f"{name} pw={pw}: max_i Phi_found(i) = {prof[imax]} at i={imax+1}  ({time.time()-t0:.0f}s)")
    print("  profile:", prof)
