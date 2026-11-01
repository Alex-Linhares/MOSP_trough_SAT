"""Brute-force check of the deterministic lemmas L1, L1′, L2, L3 of
`reports/separator_moment.md` §2 (loop0011 item 02) before any is called a lemma.

For every graph on 1..MAX_N vertices from `nauty-geng`, for 20,000 random
`G(n, p)` graphs at n = 10–12 and for 2,000 random clique covers at <= 10
customers (`benchmarks.generator.generate_structured_instance`, the MOSP graph),
with k = pw(G) by the subset DP and N = n − k, t = ⌈N/2⌉:

  L1   an exact-size empty pair (|A| = t, |R| = N − t) exists        (X₁ > 0);
  L1′  a k-set S in E_bip exists (X₂ > 0), E_bip ⊆ E_relax per S (X₂ ≤ X₂′),
       and X₂ > 0 iff X₁ > 0;
  L2   from every exact-size pair (capped per graph) the alternating closure is
       monotone at every step, stops after one round, and lands on a closed
       pair (A* = V ∖ N[R*], R* = V ∖ N[A*], S* = N(A*) ∩ N(R*)) with no A*–R*
       edge, |A*| ≥ t, |R*| ≥ N − t, |S*| ≤ k; X₃ = all closed pairs with
       those sizes; X₃′ = distinct fixpoints reached (A closed first); the
       share of pairs whose A-first and R-first fixpoints differ;
  L3   on covers: a pair is empty iff no pattern meets both sides (sampled
       both ways), and every customer of S* shares a pattern with A* and with R*.

At k = pw − 1 the existence shares of L1 (= L2 = E_bip) and of E_relax are
recorded: the necessary condition's slack at these sizes. The first 6-vertex
graph with E_relax ⊋ E_bip is printed.

    nice -n 19 python3 reports/scratch/separator_moment/02_lemmas/check.py --max-n 9 --workers 8
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import random
import statistics
import subprocess
import sys
import time
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, "/home/al/dev/MOSP")

from learning.separator_moment import (  # noqa: E402
    close_pair, closed_pairs, closure_sequence, count_exact_pairs, count_separators,
    exact_pairs, forced_sizes, is_closed_pair, is_empty_pair, mosp_masks, open_nbhd,
    pattern_meets_both, popcount, separator_events, shares_pattern, vertex_separation,
)

HERE = Path(__file__).resolve().parent
CAP = 200  # closures checked per graph (all pairs when X₁ ≤ CAP)


def parse_g6(line: str) -> tuple[int, list[int]]:
    b = line.strip().encode()
    n = b[0] - 63
    bits = []
    for ch in b[1:]:
        v = ch - 63
        bits += [(v >> i) & 1 for i in range(5, -1, -1)]
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def check_graph(adj: list[int], matrix=None, rng_seed: int = 0) -> dict:
    """Every check on one graph; returns counts and violation flags."""
    n = len(adj)
    full = (1 << n) - 1
    pw = vertex_separation(adj)
    out = {"n": n, "pw": pw, "viol": []}
    k = pw
    N, t = forced_sizes(n, k)
    X1 = count_exact_pairs(adj, k)
    X2, X2r = count_separators(adj, k)
    out.update(X1=X1, X2=X2, X2r=X2r)
    if X1 == 0:
        out["viol"].append("L1")
    if X2 == 0:
        out["viol"].append("L1'")
    if X2 > X2r:
        out["viol"].append("bip_not_subset_relax")
    if (X1 > 0) != (X2 > 0):
        out["viol"].append("L1_iff_Ebip")
    # L2: the closure from exact-size pairs
    pairs = []
    for i, pr in enumerate(exact_pairs(adj, k)):
        if X1 <= CAP or i < CAP:
            pairs.append(pr)
        else:
            break
    fix_a = set()
    differ = 0
    for A, R in pairs:
        if not is_empty_pair(adj, A, R):
            out["viol"].append("exact_pair_not_empty")
        seq = closure_sequence(adj, A, R)
        for (a0, r0), (a1, r1) in zip(seq, seq[1:]):
            if a0 & ~a1 or r0 & ~r1:
                out["viol"].append("closure_not_monotone")
        if seq[4] != seq[2] or seq[3] != seq[2]:
            out["viol"].append("closure_not_one_round")
        As, Rs = seq[-1]
        Ss = full & ~(As | Rs)
        if not is_closed_pair(adj, As, Rs):
            out["viol"].append("fixpoint_not_closed")
        if not is_empty_pair(adj, As, Rs):
            out["viol"].append("fixpoint_not_empty")
        if popcount(As) < t or popcount(Rs) < N - t or popcount(Ss) > k:
            out["viol"].append("fixpoint_sizes")
        if Ss != (open_nbhd(adj, As) & open_nbhd(adj, Rs)):
            out["viol"].append("S_not_common_boundary")
        if (As, Rs) != close_pair(adj, A, R, "A"):
            out["viol"].append("close_pair_mismatch")
        fix_a.add((As, Rs))
        if close_pair(adj, A, R, "R") != (As, Rs):
            differ += 1
        if matrix is not None:
            if is_empty_pair(adj, A, R) == pattern_meets_both(matrix, A, R):
                out["viol"].append("L3_empty_iff_pattern")
            for s in range(n):
                if Ss >> s & 1 and not (shares_pattern(matrix, s, As) and shares_pattern(matrix, s, Rs)):
                    out["viol"].append("L3_S_pattern_reading")
    out["pairs_checked"] = len(pairs)
    out["closures_differ"] = differ
    out["X3prime"] = len(fix_a) if X1 <= CAP else -1
    X3 = closed_pairs(adj, k)
    out["X3"] = len(X3)
    if not fix_a <= set(X3):
        out["viol"].append("fixpoint_not_in_X3")
    for A, R in X3:
        if not is_empty_pair(adj, A, R) or (full & ~(A | R)) != (open_nbhd(adj, A) & open_nbhd(adj, R)):
            out["viol"].append("X3_member_bad")
            break
    if matrix is not None:
        rng = random.Random(rng_seed)
        for _ in range(20):
            verts = list(range(n))
            rng.shuffle(verts)
            a = rng.randint(1, max(1, n - 1))
            r = rng.randint(0, n - a)
            A = sum(1 << v for v in verts[:a])
            R = sum(1 << v for v in verts[a:a + r])
            if is_empty_pair(adj, A, R) == pattern_meets_both(matrix, A, R):
                out["viol"].append("L3_iff_random_pair")
    # k = pw − 1: the necessary condition's slack
    if pw >= 1:
        k1 = pw - 1
        Y1 = count_exact_pairs(adj, k1)
        Y2, Y2r = count_separators(adj, k1)
        out.update(Y1=Y1, Y2=Y2, Y2r=Y2r)
        if (Y1 > 0) != (Y2 > 0):
            out["viol"].append("L1_iff_Ebip_at_pw-1")
        if Y2 > Y2r:
            out["viol"].append("bip_not_subset_relax_at_pw-1")
    out["viol"] = sorted(set(out["viol"]))
    return out


def one_g6(line: str) -> dict:
    n, adj = parse_g6(line)
    return check_graph(adj)


def one_random(args) -> dict:
    n, p, seed = args
    rng = random.Random(seed)
    adj = [0] * n
    for u, v in combinations(range(n), 2):
        if rng.random() < p:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    out = check_graph(adj)
    out.update(p=p, seed=seed)
    return out


def one_cover(args) -> dict:
    n, m, cpp, seed = args
    from benchmarks.generator import generate_structured_instance
    inst = generate_structured_instance(n, m, cpp, seed=seed)
    M = inst.matrix
    adj = mosp_masks(M)
    out = check_graph(adj, matrix=M, rng_seed=seed)
    out.update(m=m, cpp=cpp, seed=seed)
    return out


def summarise(tag: str, res: list[dict]) -> dict:
    viol = collections.Counter()
    for r in res:
        for v in r["viol"]:
            viol[v] += 1
    def med(key):
        xs = [r[key] for r in res if key in r and r[key] >= 0]
        return (statistics.median(xs), max(xs)) if xs else (None, None)
    with_pw = [r for r in res if "Y1" in r]
    row = {
        "set": tag, "graphs": len(res), "violations": sum(viol.values()),
        "viol_kinds": dict(viol),
        "X1_med": med("X1")[0], "X1_max": med("X1")[1],
        "X2_med": med("X2")[0], "X2_max": med("X2")[1],
        "X2r_med": med("X2r")[0], "X2r_max": med("X2r")[1],
        "X3_med": med("X3")[0], "X3_max": med("X3")[1],
        "X3p_med": med("X3prime")[0], "X3p_max": med("X3prime")[1],
        "relax_gt_bip_share": sum(r["X2r"] > r["X2"] for r in res) / len(res),
        "pairs_checked": sum(r["pairs_checked"] for r in res),
        "closures_differ_share": (sum(r["closures_differ"] for r in res)
                                  / max(1, sum(r["pairs_checked"] for r in res))),
        "pw_ge_1": len(with_pw),
        "L1_at_pw-1_share": (sum(r["Y1"] > 0 for r in with_pw) / len(with_pw)) if with_pw else None,
        "Erelax_at_pw-1_share": (sum(r["Y2r"] > 0 for r in with_pw) / len(with_pw)) if with_pw else None,
    }
    return row


def relax_example(n: int = 6) -> str:
    """The first graph on `n` vertices (geng order) with a k-set S in E_relax ∖ E_bip."""
    lines = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines()
    for line in lines:
        nn, adj = parse_g6(line)
        for k in range(0, n):
            for combo in combinations(range(n), k):
                S = sum(1 << v for v in combo)
                b, r = separator_events(adj, S, k)
                if r and not b:
                    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1]
                    return (f"graph6 {line.strip()} edges {edges} k={k} S={sorted(combo)} "
                            f"pw={vertex_separation(adj)}: E_relax holds, E_bip fails")
    return "none"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--min-n", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--random", type=int, default=20000, help="random graphs at 10-12")
    ap.add_argument("--covers", type=int, default=2000, help="random covers at <= 10 customers")
    ap.add_argument("--out", default=str(HERE / "summary.csv"))
    a = ap.parse_args()
    t0 = time.time()
    rows = []
    print(f"E_relax ⊋ E_bip example: {relax_example(6)}", flush=True)
    with Pool(a.workers) as pool:
        for n in range(a.min_n, a.max_n + 1):
            lines = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True).stdout.splitlines()
            res = pool.map(one_g6, lines, chunksize=256)
            row = summarise(f"geng n={n}", res)
            rows.append(row)
            print(json.dumps(row), flush=True)
            for r in res:
                if r["viol"]:
                    print("VIOLATION", json.dumps(r), flush=True)
        if a.random:
            ps = [0.15, 0.3, 0.45, 0.6]
            jobs = [(10 + (i % 3), ps[(i // 3) % 4], i) for i in range(a.random)]
            res = pool.map(one_random, jobs, chunksize=64)
            for n in (10, 11, 12):
                row = summarise(f"random n={n}", [r for r in res if r["n"] == n])
                rows.append(row)
                print(json.dumps(row), flush=True)
            for r in res:
                if r["viol"]:
                    print("VIOLATION", json.dumps(r), flush=True)
        if a.covers:
            jobs = []
            i = 0
            while len(jobs) < a.covers:
                n = 4 + (i % 7)          # 4..10 customers
                m = n * (1 + (i // 7) % 2)  # m = n or 2n
                cpp = 2 + (i // 14) % 3   # 2, 3, 4 customers per pattern
                jobs.append((n, m, cpp, i))
                i += 1
            res = pool.map(one_cover, jobs, chunksize=32)
            row = summarise("covers n<=10", res)
            rows.append(row)
            print(json.dumps(row), flush=True)
            for r in res:
                if r["viol"]:
                    print("VIOLATION", json.dumps(r), flush=True)
    with open(a.out, "w", newline="") as fh:
        keys = [k for k in rows[0] if k != "viol_kinds"]
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)
    total_viol = sum(r["violations"] for r in rows)
    print(f"TOTAL graphs={sum(r['graphs'] for r in rows)} violations={total_viol} "
          f"wall={time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
