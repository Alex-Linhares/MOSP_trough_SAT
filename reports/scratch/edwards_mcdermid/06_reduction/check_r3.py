"""Item 06 of loop0012: the statements of `DegreeBound/SPReduction.lean`, checked by brute
force in the exact form Lean proves them, before they are stated.

Every graph on 1..max_n vertices from `nauty-geng` (288,266 at 9). For every step
`SPStep G v H` (degree of `v` 1 or 2; `sp_step` of `learning.edwards_mcdermid`):

  R1    the degree sum drops (the Lean measure `degSum`), and `H.deg v = 0 < G.deg v`
  R2    no degree rises; `f H ≤ f G`; a vertex isolated by the step costs `≥ g(deg)`
  R3    for every `w ≠ v`: `H − w = G − w`, or `SPStep (G − w) v (H − w)` with the
        *same* constructor kind that Lean's proof produces (pendant if `w ∈ N(v)`,
        the original kind otherwise)
  R3X   for random `X` with `v ∉ X`: `H − X = G − X`, or `SPStep (G − X) v (H − X)`
  R5    for `K` with support disjoint from `G`'s: `SPStep (G ⊔ K) v (H ⊔ K)`
  EX    a vertex of degree 1 or 2 admits a step (step existence)
and for a random maximal reduction `G →* H` of each graph:
  R4X   for random `X ⊆ supp H`: replaying the sequence on `G − X`, each step either
        vanishes (equal graphs) or is one step at the same vertex, and the replay ends
        at `H − X`; also every acted vertex is isolated in `H`.

Regenerate: nice -n 19 python3 reports/scratch/edwards_mcdermid/06_reduction/check_r3.py --max-n 9 --workers 8
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

from learning.edwards_mcdermid import (  # noqa: E402
    bits, degrees, f_potential, g, isolate, isolate_set, parse_g6, sp_step, step_vertices,
    support,
)


def deg_sum(adj):
    return sum(a.bit_count() for a in adj)


def step_kind(adj, v):
    d = adj[v].bit_count()
    if d == 1:
        return "pendant"
    nb = adj[v]
    x = (nb & -nb).bit_length() - 1
    y = (nb ^ (nb & -nb)).bit_length() - 1
    return "triangle" if (adj[x] >> y) & 1 else "suppress"


def one(args):
    n, line = args
    _, adj = parse_g6(line)
    rng = random.Random(hash(line) & 0xFFFFFFFF)
    cnt = Counter()
    bad = []
    deg = degrees(adj)
    f_G = f_potential(adj)
    S = deg_sum(adj)
    # EX: every vertex of degree 1 or 2 admits a step; none of degree 0 or >= 3 does
    for v in range(n):
        cnt["EX"] += 1
        if 1 <= deg[v] <= 2:
            try:
                sp_step(adj, v)
            except ValueError:
                bad.append(f"EX v={v}")
    for v in step_vertices(adj):
        H = sp_step(adj, v)
        kind = step_kind(adj, v)
        cnt["R1"] += 1
        d2 = degrees(H)
        if not (deg_sum(H) < S and d2[v] == 0 < deg[v]):
            bad.append(f"R1 {line} v={v}")
        cnt["R2"] += 1
        if any(d2[u] > deg[u] for u in range(n)) or f_potential(H) > f_G:
            bad.append(f"R2 {line} v={v}")
        for u in range(n):
            if d2[u] == 0 and deg[u] > 0 and not (f_G - f_potential(H) >= g(deg[u])):
                bad.append(f"R2iso {line} v={v} u={u}")
        # R3, with the constructor kind Lean's proof produces
        for w in range(n):
            if w == v:
                continue
            cnt["R3"] += 1
            Gw = isolate(adj, w)
            Hw = isolate(H, w)
            if Hw == Gw:
                cnt["R3_zero"] += 1
                # Lean's zero-step case: pendant with w its neighbour
                if not (kind == "pendant" and (adj[v] >> w) & 1):
                    bad.append(f"R3zero-kind {line} v={v} w={w} kind={kind}")
                continue
            if not (1 <= Gw[v].bit_count() <= 2 and sp_step(Gw, v) == Hw):
                bad.append(f"R3 {line} v={v} w={w}")
                continue
            cnt["R3_one"] += 1
            expected = "pendant" if (adj[v] >> w) & 1 else kind
            if step_kind(Gw, v) != expected:
                bad.append(f"R3kind {line} v={v} w={w} got={step_kind(Gw, v)} exp={expected}")
        # R3X: random X not containing v (3 draws)
        for _ in range(3):
            X = 0
            for u in range(n):
                if u != v and rng.random() < 0.4:
                    X |= 1 << u
            cnt["R3X"] += 1
            GX = isolate_set(adj, X)
            HX = isolate_set(H, X)
            if HX == GX:
                cnt["R3X_zero"] += 1
            elif 1 <= GX[v].bit_count() <= 2 and sp_step(GX, v) == HX:
                cnt["R3X_one"] += 1
            else:
                bad.append(f"R3X {line} v={v} X={X}")
        # R5: K a random graph on vertices outside supp G (plus edges among them only)
        s = support(adj)
        rest = [u for u in range(n) if not (s >> u) & 1]
        if rest:
            K = [0] * n
            for i, a in enumerate(rest):
                for b in rest[i + 1:]:
                    if rng.random() < 0.6:
                        K[a] |= 1 << b
                        K[b] |= 1 << a
            cnt["R5"] += 1
            GK = [a | k for a, k in zip(adj, K)]
            HK = [h | k for h, k in zip(H, K)]
            if not (1 <= GK[v].bit_count() <= 2 and sp_step(GK, v) == HK
                    and step_kind(GK, v) == kind):
                bad.append(f"R5 {line} v={v}")
    # R4X on a random maximal reduction
    seq = []
    cur = list(adj)
    while True:
        cands = step_vertices(cur)
        if not cands:
            break
        v = rng.choice(cands)
        seq.append(v)
        cur = sp_step(cur, v)
    Hfin = cur
    cnt["R4X_seq"] += 1
    for v in seq:
        if Hfin[v] != 0:
            bad.append(f"acted-not-isolated {line} v={v}")
    sH = support(Hfin)
    for _ in range(3):
        X = 0
        for u in bits(sH):
            if rng.random() < 0.5:
                X |= 1 << u
        cnt["R4X"] += 1
        g_cur = isolate_set(adj, X)
        for v in seq:
            if (X >> v) & 1:
                bad.append(f"R4X acted-in-X {line} v={v}")
                break
            if 1 <= g_cur[v].bit_count() <= 2:
                g_cur = sp_step(g_cur, v)
            # else: the step vanished (degree 0 at v), zero steps
        if g_cur != isolate_set(Hfin, X):
            bad.append(f"R4X {line} X={X}")
    return n, dict(cnt), bad


def geng(n):
    out = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True, check=True)
    return out.stdout.split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--log", default=f"{HERE}/check_r3.log")
    a = ap.parse_args()
    t0 = time.time()
    log = open(a.log, "w")

    def say(s=""):
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"# item 06 check, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, "
        f"max_n={a.max_n}, workers={a.workers}")
    total = Counter()
    per_n = {}
    nbad = 0
    with Pool(a.workers) as pool:
        for n in range(1, a.max_n + 1):
            lines = geng(n)
            cnt = Counter()
            for _, c, bad in pool.imap_unordered(one, [(n, l) for l in lines], chunksize=64):
                cnt.update(c)
                for b in bad:
                    nbad += 1
                    say(f"VIOLATION {b}")
            per_n[n] = {"graphs": len(lines), **cnt}
            total.update(cnt)
            say(f"n={n} graphs={len(lines)} " + " ".join(f"{k}={cnt[k]}" for k in sorted(cnt))
                + f" t={time.time() - t0:.0f}s")
    say(f"total " + " ".join(f"{k}={total[k]}" for k in sorted(total)))
    say(f"violations={nbad} elapsed={time.time() - t0:.0f}s")
    json.dump({"per_n": per_n, "total": dict(total), "violations": nbad,
               "elapsed_s": round(time.time() - t0)}, open(f"{HERE}/summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
