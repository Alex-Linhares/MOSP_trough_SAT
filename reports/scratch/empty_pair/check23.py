"""Brute-force checks of the deterministic cores of survey §2 and §3 (todo "Lean the derived
random-graph bounds", items (2) and (3)):
  (2) every tree on N vertices has pw ≤ ⌊log₃(2N + 1)⌋ (trees to 16 vertices, geng -c n n-1);
      the complete ternary tree of height h has pw = h (h = 1..3; h = 3 has 40 vertices, C program);
  (3) pw ≤ n − α(G) for every graph on ≤ 9 vertices.
"""
import math, subprocess, collections, sys
from multiprocessing import Pool
sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/empty_pair")
from check import parse_g6, vs

def tree_one(line):
    n, adj = parse_g6(line); return n, vs(n, adj)

def alpha(n, adj):
    best = 0
    for S in range(1 << n):
        ok = True; T = S
        while T:
            low = T & -T; v = low.bit_length() - 1; T ^= low
            if adj[v] & S: ok = False; break
        if ok:
            c = bin(S).count("1")
            if c > best: best = c
    return best

def g_one(line):
    n, adj = parse_g6(line); return n, vs(n, adj), alpha(n, adj)

if __name__ == "__main__":
    print("(2) trees: pw <= floor(log3(2N+1))")
    for n in range(2, 17):
        lines = subprocess.run(["nauty-geng", "-c", "-q", str(n), f"{n-1}:{n-1}"], capture_output=True, text=True).stdout.splitlines()
        with Pool(8) as p: res = p.map(tree_one, lines, chunksize=64)
        bound = math.floor(math.log(2 * n + 1, 3) + 1e-9)
        mx = max(k for _, k in res); viol = sum(k > bound for _, k in res)
        print(f"  N={n:2} trees={len(res):6} max pw={mx} bound={bound} violations={viol} pw hist={dict(sorted(collections.Counter(k for _, k in res).items()))}", flush=True)
    print("(2) complete ternary trees: pw = h")
    import networkx as nx
    for h in range(1, 4):
        G = nx.balanced_tree(3, h); n = G.number_of_nodes()
        g6 = nx.to_graph6_bytes(G, header=False)
        out = subprocess.run(["/home/al/dev/MOSP/pathwidth_solver/cli/pathwidth", "-t", "60"], input=g6, capture_output=True).stdout.decode().split()
        print(f"  h={h} N={n}: C program says pathwidth {out[1]} ({out[2]})", flush=True)
    print("(3) pw <= n - alpha on every graph to 9 vertices")
    for n in range(1, 10):
        lines = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines()
        with Pool(8) as p: res = p.map(g_one, lines, chunksize=256)
        viol = sum(k > nn - a for nn, k, a in res); tight = sum(k == nn - a for nn, k, a in res)
        print(f"  n={n} graphs={len(res)} violations={viol} tight={tight}", flush=True)
