"""Numeric check behind the proof of conjecture_sqrt_tw_f6 (2026-10-31).

Claim 4 of the proof: 0.9428 * sqrt(p (p + 6)) < p + 2 for every real p >= 0,
with p = pathwidth. Also the tight case K_{6,6}: tw = pw = 6, f(6) = 12.
"""
import itertools, math, sys
import networkx as nx
sys.path.insert(0, "/home/al/dev/MOSP")
from fixed_parameter_algorithm.pathwidth import compute_pathwidth

c = 0.9428
c2 = c * c
print(f"c^2 = {c2!r}")
# quadratic (1 - c^2) p^2 + (4 - 6 c^2) p + 4 > 0 for all p : discriminant < 0
a, b, d = 1 - c2, 4 - 6 * c2, 4
disc = b * b - 4 * a * d
print(f"quadratic {a:.8f} p^2 + {b:.8f} p + {d} ; discriminant {disc:.9f}")
print(f"with 2*sqrt(2)/3 = {2*math.sqrt(2)/3!r}: discriminant "
      f"{(4-6*8/9)**2 - 4*(1-8/9)*4:.3e} (zero), root p = {-(4-6*8/9)/(2*(1-8/9))}")
worst = max(range(0, 41), key=lambda p: c * math.sqrt(p * (p + 6)) - (p + 2))
for p in range(0, 41):
    lhs = c * math.sqrt(p * (p + 6)); rhs = p + 2
    assert lhs < rhs, p
    if p <= 12 or p == 40:
        print(f"p={p:2d}  0.9428*sqrt(p(p+6)) = {lhs:.6f}  <  p+2 = {rhs}  "
              f"floor = {math.floor(lhs)} <= p+1 = {p+1}")
print(f"largest lhs - rhs over p = 0..40 at p = {worst}: "
      f"{c*math.sqrt(worst*(worst+6)) - (worst+2):.6f}")

# K_{6,6}
K = nx.complete_bipartite_graph(6, 6)
pw, order = compute_pathwidth(K)
tw, _ = nx.algorithms.approximation.treewidth_min_degree(K)  # upper bound
# exact tw of K_{m,n} is min(m,n); check with the lower bound: K_{6,6} contains
# no K_8 but tw >= degeneracy = 6
f6 = min(len(set(S) | set().union(*(set(K[v]) for v in S)))
         for S in itertools.combinations(K.nodes, 6))
print(f"K_6,6: pw = {pw} (witness {order}), tw <= {tw} (min-degree), "
      f"degeneracy = {max(nx.core_number(K).values())} so tw = 6 exactly, f(6) = {f6}")
x = c * math.sqrt(6 * f6)
print(f"K_6,6: 0.9428*sqrt(tw*f6) = {x:.6f}, floor = {math.floor(x)}, pw+1 = {pw+1}; "
      f"exact constant would give 2sqrt2/3*sqrt(72) = {2*math.sqrt(2)/3*math.sqrt(72):.6f} = 8 = pw + 2")
