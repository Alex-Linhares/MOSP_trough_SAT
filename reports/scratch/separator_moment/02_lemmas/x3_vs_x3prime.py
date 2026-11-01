"""Per-graph comparison of X₃ (all closed pairs of the forced sizes) with X₃′
(the image of the exact-size pairs under the A-first closure), §2.3 remark (iv):
on how many graphs is X₃′ < X₃?  Every graph at 7 and 8 vertices; 600 of the
random graphs at 10–12 (X₃′ is computed only when X₁ ≤ 200).
    python3 reports/scratch/separator_moment/02_lemmas/x3_vs_x3prime.py
"""
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/al/dev/MOSP")
from check import check_graph, one_random, parse_g6  # noqa: E402

for n in (7, 8):
    lines = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines()
    lt = eq = 0
    for line in lines:
        r = check_graph(parse_g6(line)[1])
        if r["X3prime"] >= 0:
            if r["X3prime"] < r["X3"]:
                lt += 1
            else:
                eq += 1
    print(f"geng n={n}: X3' < X3 on {lt} graphs, equal on {eq}")
lt = eq = skip = 0
for i in range(600):
    r = one_random((10 + (i % 3), [0.15, 0.3, 0.45, 0.6][(i // 3) % 4], i))
    if r["X3prime"] < 0:
        skip += 1
    elif r["X3prime"] < r["X3"]:
        lt += 1
    else:
        eq += 1
print(f"random n=10-12 (600 graphs): X3' < X3 on {lt}, equal on {eq}, X3' not computed (X1 > 200) on {skip}")
