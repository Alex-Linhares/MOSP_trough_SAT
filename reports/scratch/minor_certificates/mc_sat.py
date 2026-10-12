"""Independent CNF for "vertex separation (= pathwidth, Kinnersley 1992) <= k",
written from scratch on 2026-10-12 (no pysat, no project code).

Steps t = 0..n-1; exactly one vertex is placed at each step.
  y[v,t]  v is placed at a step <= t           (monotone in t)
  d[v,t]  v is placed exactly at step t        (d <-> y[v,t] & ~y[v,t-1])
  s[v,t]  v is placed by t and has an unplaced neighbour after step t
          (forced: y[v,t] & ~y[u,t] -> s[v,t] for every edge uv)
  per step: at least one and at most one d[.,t] (sequential AMO);
  per step t < n-1: at most k of s[.,t] (Sinz sequential counter).
s may be true spuriously, which only makes the bound harder, so the formula
is satisfiable iff some layout has vertex separation <= k. No symmetry is broken.

  python mc_sat.py encode EDGES.json K OUT.cnf     (EDGES: [[u,v],...], vertices 0..m-1)
  python mc_sat.py selftest                        (brute force on small graphs)
"""
import json
import sys


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, c):
        self.cl.append(c)

    def amo_seq(self, xs):
        n = len(xs)
        if n <= 1:
            return
        r = [self.new() for _ in range(n - 1)]
        self.add([-xs[0], r[0]])
        for i in range(1, n - 1):
            self.add([-xs[i], r[i]])
            self.add([-r[i - 1], r[i]])
            self.add([-xs[i], -r[i - 1]])
        self.add([-xs[n - 1], -r[n - 2]])

    def atmost_seq(self, xs, k):
        n = len(xs)
        if k >= n:
            return
        if k == 0:
            for x in xs:
                self.add([-x])
            return
        R = [[self.new() for _ in range(k)] for _ in range(n - 1)]
        self.add([-xs[0], R[0][0]])
        for j in range(1, k):
            self.add([-R[0][j]])
        for i in range(1, n - 1):
            self.add([-xs[i], R[i][0]])
            for j in range(k):
                self.add([-R[i - 1][j], R[i][j]])
            for j in range(1, k):
                self.add([-xs[i], -R[i - 1][j - 1], R[i][j]])
            self.add([-xs[i], -R[i - 1][k - 1]])
        self.add([-xs[n - 1], -R[n - 2][k - 1]])

    def dimacs(self, path, comment=""):
        with open(path, "w") as f:
            for line in comment.splitlines():
                f.write(f"c {line}\n")
            f.write(f"p cnf {self.nv} {len(self.cl)}\n")
            for c in self.cl:
                f.write(" ".join(map(str, c)) + " 0\n")


def encode(n, edge_list, k):
    F = CNF()
    y = [[F.new() for _ in range(n)] for _ in range(n)]   # y[v][t]
    d = [[F.new() for _ in range(n)] for _ in range(n)]
    for v in range(n):
        for t in range(n):
            if t:
                F.add([-y[v][t - 1], y[v][t]])                   # monotone
                F.add([-d[v][t], y[v][t]])
                F.add([-d[v][t], -y[v][t - 1]])
                F.add([-y[v][t], y[v][t - 1], d[v][t]])
            else:
                F.add([-d[v][0], y[v][0]])
                F.add([-y[v][0], d[v][0]])
    for t in range(n):
        F.add([d[v][t] for v in range(n)])
        F.amo_seq([d[v][t] for v in range(n)])
    for t in range(n - 1):
        s = [F.new() for _ in range(n)]
        for u, v in edge_list:
            F.add([-y[v][t], y[u][t], s[v]])
            F.add([-y[u][t], y[v][t], s[u]])
        F.atmost_seq(s, k)
    return F, y


def vs_brute(n, adj):
    """Exact vertex separation by DP over subsets (n <= 16)."""
    full = (1 << n) - 1
    nb = [sum(1 << u for u in adj[v]) for v in range(n)]
    INF = 10 ** 9
    f = [INF] * (1 << n)
    f[0] = 0
    for S in range(1, 1 << n):
        bd = sum(1 for v in range(n) if S >> v & 1 and nb[v] & ~S & full)
        best = INF
        T = S
        while T:
            v = (T & -T).bit_length() - 1
            T &= T - 1
            best = min(best, f[S & ~(1 << v)])
        f[S] = max(bd, best)
    return f[full]


def selftest(trials=300, seed=1):
    import random
    import subprocess
    import tempfile
    import os
    rng = random.Random(seed)
    cad = os.environ.get("CADICAL", "/home/al/.elan/toolchains/leanprover--lean4---v4.29.0/bin/cadical")
    for t in range(trials):
        n = rng.randint(2, 10)
        p = rng.choice([0.2, 0.35, 0.5, 0.7])
        E = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < p]
        adj = {v: set() for v in range(n)}
        for a, b in E:
            adj[a].add(b); adj[b].add(a)
        pw = vs_brute(n, adj)
        for k in range(max(0, pw - 1), pw + 1):
            F, _ = encode(n, E, k)
            with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as fh:
                path = fh.name
            F.dimacs(path)
            r = subprocess.run([cad, "-q", path], capture_output=True, text=True).returncode
            os.unlink(path)
            want = 10 if k >= pw else 20
            assert r == want, (n, E, k, pw, r)
    print(f"selftest: {trials} random graphs, encoding agrees with brute force at pw-1 and pw")


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        selftest()
    else:
        E = [tuple(e) for e in json.load(open(sys.argv[2]))]
        k = int(sys.argv[3])
        n = 1 + max(max(e) for e in E)
        F, _ = encode(n, E, k)
        F.dimacs(sys.argv[4], comment=f"vertex separation <= {k}? n={n} edges={len(E)} (mc_sat.py)")
        print(f"{sys.argv[4]}: {F.nv} vars, {len(F.cl)} clauses")
