"""Item 03: the C program against an independent exact method on small block graphs -- Chou, Ko, Ho &
Chen's Theorem 4 (learning/chou_block.py; exponential as implemented, so n <= 30 here): every clique tree
and caterpillar of cliques with at most 30 vertices, and 300 random block trees at n in {8, 12, 16, 20, 24},
d in {2, 3, 4, 6}, 15 per cell (seeds 9000 + 100 n + 10 d + i). A disagreement would mean one of the two is wrong.
    cd /home/al/dev/MOSP && nice -n 19 python3 reports/scratch/forest_regime/cross_check.py > reports/scratch/forest_regime/cross_check.log
"""
import csv, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from learning.block_trees import (caterpillar_of_cliques, clique_tree, graph6, mosp_graph, random_block_tree,
                                  run_pathwidth_one)
from learning.chou_block import is_block_graph, pathwidth_block_graph
t0 = time.time(); checked = dis = 0
for r in csv.DictReader(open(HERE / "ct_values.csv")):
    if int(r["n"]) > 30: continue
    P, _ = clique_tree(int(r["s"]), int(r["h"]), int(r["b"])); pw = pathwidth_block_graph(mosp_graph(P)); checked += 1
    ok = pw == int(r["pw"]); dis += not ok
    print(f"CT({r['s']},{r['h']},{r['b']}) n={r['n']} C={r['pw']} chou={pw} {'ok' if ok else 'DISAGREE'}")
for r in csv.DictReader(open(HERE / "caterpillar_values.csv")):
    if int(r["n"]) > 30: continue
    P = caterpillar_of_cliques(int(r["s"]), int(r["length"])); pw = pathwidth_block_graph(mosp_graph(P)); checked += 1
    ok = pw == int(r["pw"]); dis += not ok
    print(f"CAT(s={r['s']},L={r['length']}) n={r['n']} C={r['pw']} chou={pw} {'ok' if ok else 'DISAGREE'}")
cnt = 0
for n in (8, 12, 16, 20, 24):
    for d in (2, 3, 4, 6):
        for i in range(15):
            P = random_block_tree(n, d, 9000 + 100 * n + 10 * d + i); G = mosp_graph(P)
            assert is_block_graph(G)
            c = run_pathwidth_one(graph6(G), 120)["width"]; p = pathwidth_block_graph(G); checked += 1; cnt += 1
            if c != p: dis += 1; print(f"DISAGREE random n={n} d={d} i={i}: C={c} chou={p}")
print(f"random block trees: {cnt}; total checked {checked}; disagreements {dis}; {time.time()-t0:.0f}s")
