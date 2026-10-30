"""Brute-force check of the empty-pair lemma behind the derived first-moment bound
(reports/random_graph_pathwidth_survey.md §1.4; paper1/todo.md "Lean the derived random-graph
bounds", step one): for every graph on ≤ N vertices,

    pw(G) ≥ n − 2·s*(G) − 2,   s*(G) = max over A ⊆ V of min(|A| − 1, n − |N[A]|),

i.e. a layout of vertex separation k yields a set A with |A| ≥ s + 1 having at least s vertices
outside its closed neighbourhood, s = ⌈(n − k)/2⌉ − 1 (the suffix at the position after the last
one where the suffix-free prefix is no larger than the suffix).  Also the weaker rounding the
survey states, s'(G) = max_A min(|A|, n − |N[A]|) ≥ ⌈(n − k)/2⌉ − 1, i.e. pw ≥ n − 2s' − 2.
Pathwidth by the vertex-separation subset DP; graphs from nauty-geng.
    python3 check.py --max-n 9 --workers 16
"""
import argparse, subprocess, sys, collections
from multiprocessing import Pool
sys.path.insert(0, "/home/al/dev/MOSP")


def parse_g6(line):
    b = line.strip().encode(); n = b[0] - 63; bits = []
    for ch in b[1:]:
        v = ch - 63; bits += [(v >> i) & 1 for i in range(5, -1, -1)]
    adj = [0] * n; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: adj[i] |= 1 << j; adj[j] |= 1 << i
            k += 1
    return n, adj


def vs(n, adj):
    full = (1 << n) - 1
    # boundary b(S) = |N(S) \ S|; f(S) = min_{v in S} max(f(S - v), b(S))
    nb = [0] * (1 << n); f = [0] * (1 << n)
    for S in range(1, 1 << n):
        low = S & -S; v = low.bit_length() - 1
        nb[S] = nb[S ^ low] | adj[v]
        b = bin(nb[S] & ~S & full).count("1")
        best = n; T = S
        while T:
            low = T & -T; T ^= low
            c = f[S ^ low]
            if c < best: best = c
        f[S] = best if best > b else b
    return f[full]


def sstar(n, adj):
    # closed neighbourhoods: N[A] = union of adj[v] | {v}
    cl = [adj[v] | (1 << v) for v in range(n)]
    NA = [0] * (1 << n); s1 = s2 = 0
    for A in range(1, 1 << n):
        low = A & -A; v = low.bit_length() - 1
        NA[A] = NA[A ^ low] | cl[v]
        a = bin(A).count("1"); out = n - bin(NA[A]).count("1")
        t = min(a - 1, out); u = min(a, out)
        if t > s1: s1 = t
        if u > s2: s2 = u
    return s1, s2


def one(line):
    n, adj = parse_g6(line)
    k = vs(n, adj); s1, s2 = sstar(n, adj)
    return n, k, s1, s2


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max-n", type=int, default=9); ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest:
        import networkx as nx
        from fixed_parameter_algorithm.pathwidth import compute_pathwidth
        bad = 0; tot = 0
        for n in range(2, 8):
            for line in subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines():
                nn, adj = parse_g6(line); G = nx.from_graph6_bytes(line.encode())
                tot += 1
                if vs(nn, adj) != compute_pathwidth(G)[0]: bad += 1
        print(f"selftest: {tot} graphs to 7 vertices, {bad} pathwidth disagreements"); return
    for n in range(1, a.max_n + 1):
        lines = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines()
        with Pool(a.workers) as p: res = p.map(one, lines, chunksize=256)
        slack1 = collections.Counter(); slack2 = collections.Counter(); viol1 = viol2 = 0
        for (nn, k, s1, s2) in res:
            d1 = k - (nn - 2 * s1 - 2); d2 = k - (nn - 2 * s2 - 2)
            slack1[d1] += 1; slack2[d2] += 1
            if d1 < 0: viol1 += 1
            if d2 < 0: viol2 += 1
        print(f"n={n} graphs={len(res)} | sharp form: violations={viol1} slack {dict(sorted(slack1.items()))} | "
              f"survey rounding: violations={viol2} slack {dict(sorted(slack2.items()))}", flush=True)


if __name__ == "__main__":
    main()
