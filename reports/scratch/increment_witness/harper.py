"""Harper's vertex-isoperimetric profile of Q_d: Phi(i) = min_{|S|=i} |N[S]| - i.
Simplicial-order prefixes attain it (Harper 1966); brute force confirms at d = 3, 4."""
import itertools, iw
from math import comb
def profile_simplicial(d):
    G = iw.hypercube(d); n = 1 << d
    order = sorted(range(n), key=lambda x: (bin(x).count("1"), -x))   # Harper: within a layer, descending (the set holding min of the symmetric difference first)
    out = []
    S = set(); N = set()
    for i, v in enumerate(order, 1):
        S.add(v); N.add(v); N.update(G[v])
        out.append(len(N) - i)
    return out
def profile_brute(d):
    G = iw.hypercube(d); n = 1 << d
    best = [n] * (n + 1)
    for mask in range(1, 1 << n):
        S = [v for v in range(n) if mask >> v & 1]
        N = set(S)
        for v in S: N.update(G[v])
        i = len(S)
        if len(N) - i < best[i]: best[i] = len(N) - i
    return best[1:]
for d in (3, 4):
    s, b = profile_simplicial(d), profile_brute(d)
    print(f"Q_{d}: simplicial profile {s}\n     brute-force profile {b}\n     equal: {s == b}")
print()
for d in range(1, 9):
    p = profile_simplicial(d)
    mx = max(p); arg = [i + 1 for i, x in enumerate(p) if x == mx]
    formula = sum(comb(i, i // 2) for i in range(d))
    half = p[(1 << (d - 1)) - 1]
    print(f"Q_{d}: max Phi = {mx} at |S| in {arg}; formula {formula}; Phi(2^(d-1)) = {half}; C(d-1,floor((d-1)/2)) = {comb(d-1,(d-1)//2)}")
