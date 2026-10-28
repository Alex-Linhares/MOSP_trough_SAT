"""Check a PACE .td against a .gr: every vertex in a bag, every edge in a bag, the bags of
each vertex connected in the tree; print the width.  python3 check_td.py g.gr g.td"""
import sys
from collections import defaultdict
gr, td = sys.argv[1], sys.argv[2]
n = m = 0; edges = []
for line in open(gr):
    if line.startswith("c"): continue
    if line.startswith("p"): _, _, n, m = line.split(); n, m = int(n), int(m); continue
    u, v = map(int, line.split()); edges.append((u, v))
bags = {}; tree = defaultdict(list); nb = width = 0
for line in open(td):
    if line.startswith("c"): continue
    p = line.split()
    if not p: continue
    if p[0] == "s": nb, width, nv = int(p[2]), int(p[3]) - 1, int(p[4]); assert nv == n
    elif p[0] == "b": bags[int(p[1])] = set(map(int, p[2:]))
    else: a, b = map(int, p); tree[a].append(b); tree[b].append(a)
assert len(bags) == nb, (len(bags), nb)
assert max(len(b) for b in bags.values()) - 1 == width
cover = set().union(*bags.values()); assert cover == set(range(1, n + 1)), "vertex not covered"
for u, v in edges:
    assert any(u in b and v in b for b in bags.values()), f"edge {u},{v} in no bag"
for v in range(1, n + 1):
    ids = [i for i, b in bags.items() if v in b]
    seen = {ids[0]}; st = [ids[0]]
    while st:
        for w in tree[st.pop()]:
            if w in bags and v in bags[w] and w not in seen: seen.add(w); st.append(w)
    assert seen == set(ids), f"bags of {v} disconnected"
# tree: nb-1 edges, connected
ne = sum(len(x) for x in tree.values()) // 2; assert ne == nb - 1 or nb == 1, (ne, nb)
print(f"valid tree decomposition, width {width}, {nb} bags")
