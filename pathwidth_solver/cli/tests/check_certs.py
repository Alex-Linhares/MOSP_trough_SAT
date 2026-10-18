"""Replay every minor certificate the C program prints and re-check its claim.

For each input graph proved by 'minor': replay the contraction pairs with the
independent replay of pathwidth/minor.py (each pair must be an edge of the
current graph, each deletion an isolated vertex), then run the C program on the
resulting minor and check its width exceeds the refuted value, so the bound
pw(G) >= refuted + 1 follows from Theorem 4.11.
    python tests/check_certs.py < graphs.g6
"""
import subprocess, sys
from pathlib import Path
import networkx as nx
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from pathwidth.minor import replay  # the checker only; no solving in Python

BIN = str(HERE.parent / "pathwidth")
lines = [l.strip() for l in sys.stdin if l.strip()]
out = subprocess.run([BIN, "-l"], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout
recs, cur = [], None
for l in out.splitlines():
    if l.startswith("pathwidth "):
        cur = {"line": l}; recs.append(cur)
    elif l.startswith("minor "):
        cur["minor"] = l
ok = bad = 0
for g6, r in zip(lines, recs):
    if " minor" not in r["line"]:
        continue
    G = nx.from_graph6_bytes(g6.encode())
    masks = [0] * G.number_of_nodes()
    for v in G: masks[v] = 1 << v
    for u, v in G.edges(): masks[u] |= 1 << v; masks[v] |= 1 << u
    t = r["minor"].split()
    refuted = int(t[2]); pairs = [tuple(map(int, p.split(","))) for p in t[t.index("contractions") + 1:]]
    mm, labels, _ = replay(masks, pairs)
    H = nx.Graph(); H.add_nodes_from(range(len(mm)))
    for i, m in enumerate(mm):
        for j in range(len(mm)):
            if j != i and m >> j & 1: H.add_edge(i, j)
    w = int(subprocess.run([BIN, "-t", "600"], input=nx.to_graph6_bytes(H, header=False).decode(),
                           capture_output=True, text=True, check=True).stdout.split()[1])
    width = int(r["line"].split()[1])
    good = w >= refuted + 1 and width == refuted + 1
    ok += good; bad += not good
    print(("ok  " if good else "BAD ") + f"n={len(masks)} width={width} minor n={len(mm)} pw(minor)={w} refuted={refuted}")
print(f"{ok} certificates check, {bad} fail")
sys.exit(1 if bad else 0)
