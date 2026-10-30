"""The sharp tree + cyclomatic upper bound against the data (survey §7(e), 2026-10-31).

  pw(G) ≤ max over components C of  tb(|C|) + (m_C − |C| + 1),
  tb(N) = least k with N ≤ (5·3^k − 3)/2  (= ⌊log₃((6N+3)/5)⌋ for N ≥ 2; 0 for N ≤ 1),

from `tree_pathwidth_le_treeBound` (TreeBound.lean) and pw ≤ pw(spanning forest) + cyclomatic
number. Part A: against the other upper bounds of the survey on the G(n, c/n) pilot graphs
(n = 30, 60; c ≤ 4). Part B: against every certified class of the pathwidth dataset.
    python3 compare_bound.py
"""
import csv, gzip, json, math, collections, statistics as st
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]


def treebound(N):
    if N <= 1: return 0
    k = 0
    while (5 * 3**k - 3) // 2 < N: k += 1
    return k


def oldtreebound(N): return math.floor(math.log(2 * N + 1, 3) + 1e-9) if N >= 2 else 0


def part_a():
    def bounds(G):
        n, m = G.number_of_nodes(), G.number_of_edges()
        comps = [G.subgraph(c) for c in nx.connected_components(G)]
        new = max(treebound(C.number_of_nodes()) + (C.number_of_edges() - C.number_of_nodes() + 1) for C in comps)
        old = max(oldtreebound(C.number_of_nodes()) + (C.number_of_edges() - C.number_of_nodes() + 1) for C in comps)
        H = G.copy(); I = 0
        while H.number_of_nodes():
            v = min(H.nodes, key=H.degree); I += 1
            H.remove_nodes_from(list(H.neighbors(v)) + [v])
        return new, old, m / 5.769, n - I
    src = ROOT / "reports/scratch/gnp_pilot/results.csv"
    cells = collections.defaultdict(list); viol = 0
    for r in csv.DictReader(open(src)):
        n, c = int(r["n"]), float(r["c"])
        if r["status"] == "upper" or n not in (30, 60) or c > 4: continue
        G = nx.gnp_random_graph(n, c / n, seed=int(r["seed"]))
        pw = int(r["width"]); b = bounds(G); viol += b[0] < pw
        cells[(n, c)].append((pw, *b))
    print("A. pilot graphs; violations:", viol)
    print("  n    c    pw | sharp tree+cyc  old tree+cyc  m/5.769  n−α_greedy | best  exact(sharp/old)")
    for (n, c) in sorted(cells):
        L = cells[(n, c)]; mean = lambda i: st.mean(x[i] - x[0] for x in L)
        best = sum(1 for x in L if x[1] <= min(x[2], x[3], x[4])) / len(L)
        ex = sum(x[1] == x[0] for x in L) / len(L); exo = sum(x[2] == x[0] for x in L) / len(L)
        print(f"{n:>3} {c:>4} {st.mean(x[0] for x in L):5.2f} | {mean(1):14.2f} {mean(2):13.2f} {mean(3):8.2f} {mean(4):11.2f} | {best:4.0%}  {ex:4.0%} / {exo:4.0%}")


def components(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges: adj[u].append(v); adj[v].append(u)
    seen = [False] * n; out = []
    for s in range(n):
        if seen[s]: continue
        seen[s] = True; stack = [s]; nodes = deg = 0
        while stack:
            x = stack.pop(); nodes += 1; deg += len(adj[x])
            for y in adj[x]:
                if not seen[y]: seen[y] = True; stack.append(y)
        out.append((nodes, deg // 2))
    return out


def part_b():
    D = ROOT / "paper1/data/dataset"
    owners = {r["id"]: r["owner"] for r in csv.DictReader(gzip.open(D / "classes.csv.gz", "rt"))}
    rows = []
    for line in gzip.open(D / "pathwidth_dataset.jsonl.gz", "rt"):
        d = json.loads(line)
        if not d["provenance"].startswith("certified"): continue
        comps = components(d["n"], d["edges"])
        if not comps: continue
        b = max(treebound(N) + (M - N + 1) for N, M in comps)
        rows.append((d["id"], owners.get(d["id"], "?"), d["n"], d["m"], d["width"], b, len(comps)))
    print(f"\nB. dataset: {len(rows)} certified classes; violations:", sum(r[5] < r[4] for r in rows))
    gap = [r[5] - r[4] for r in rows]
    print("  gap: exact", sum(g == 0 for g in gap), " 1:", sum(g == 1 for g in gap), " 2–5:", sum(2 <= g <= 5 for g in gap), " 6–20:", sum(6 <= g <= 20 for g in gap), " >20:", sum(g > 20 for g in gap))
    by = collections.defaultdict(list)
    for r in rows: by[r[1]].append(r)
    for k in sorted(by, key=lambda k: -len(by[k])):
        L = by[k]; g = [r[5] - r[4] for r in L]
        print(f"  {k[:40]:40} {len(L):6}  exact {sum(x==0 for x in g):5}  ≤2 {sum(x<=2 for x in g):5}  median gap {st.median(g):7.1f}  max n {max(r[2] for r in L)}")
    trees = [r for r in rows if r[3] == r[2] - r[6]]
    g = collections.Counter(r[5] - r[4] for r in trees)
    print("  trees/forests:", len(trees), "exact", g.get(0, 0), "gaps", dict(sorted(g.items())))


if __name__ == "__main__":
    part_a(); part_b()
