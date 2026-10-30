"""One-CPU-hour by-product attempt on Q_7: Harper's simplicial layout (weight, then
lexicographic) as the seed (its vertex separation should be 43), proved floor 42
(the lower bound of the recurrence is not proved by us; -L 42 only directs the
descent: the C still refutes 42 itself, so soundness does not rest on it),
minor ladder disabled (hypercubes are near minor-critical: the ladder's minors lose width)."""
import iw, subprocess, os
G = iw.hypercube(7)
order = sorted(G.nodes(), key=lambda x: (bin(x).count("1"), -x))     # Harper simplicial order: layer, then descending
# verify its vertex separation = 43 in Python (no code shared with the C)
pos = {v: i for i, v in enumerate(order)}
vs = max(sum(1 for v in order[:i + 1] if any(pos[u] > i for u in G[v])) for i in range(len(order)))
print("Harper layout vertex separation on Q_7:", vs)
closing = list(reversed(order))     # the C's -u file: vertex closed first first = layout reversed
open("Q7_harper_closing.txt", "w").write(" ".join(map(str, closing)) + "\n")
open("Q7.g6", "w").write(iw.to_g6(G) + "\n")
