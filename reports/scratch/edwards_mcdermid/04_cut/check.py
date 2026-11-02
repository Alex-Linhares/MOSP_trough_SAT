#!/usr/bin/env python3
"""Brute-force check of every statement `DegreeBound/CutLemma.lean` makes
(loop0012 item 04; `reports/edwards_mcdermid.md` §4), before it is stated.

Part A — every graph on 1–7 vertices from `nauty-geng`, every ordered pair of
disjoint vertex sets `(S1, S2)` (3^n per graph; pathwidth of every `G[S]` by
the subset DP, memoised per graph):

  M    monotonicity           T ⊆ U ⇒ pw(G[T]) ≤ pw(G[U])
  L1r  relative deletion      T ⊆ U ⇒ pw(G[U]) ≤ pw(G[T]) + |U ∖ T|
  L1g  the same for every pair (T, U), no inclusion (the form Lean proves:
       the unused hypothesis was noticed by the linter after the first run)
  C1r1 one-sided separator    pw(G[S1 ∪ S2]) ≤ max(pw G[S1], pw G[S2]) + |∂(S1→S2)|
  C1r  relative C1s           pw(G[S1 ∪ S2]) ≤ max(pw G[S1], pw G[S2]) + min(|∂(S1→S2)|, |∂(S2→S1)|)
  and, on the partitions (S1 ∪ S2 = V, each once):
  C1s  the global form        pw(G) ≤ max(pw G[S], pw G[Sᶜ]) + min(|∂S|, |∂Sᶜ|)
  C1   the item's form        pw(G) ≤ max(pw G[S] + |∂S|, pw G[Sᶜ] + |∂Sᶜ|, |∂S| + |∂Sᶜ| − 1)
  C1s ≤ C1, and the tightness count of C1s.

Part B — 2,000 random graphs `G(n, p)` at `n = 10, 11, 12` (`p` uniform in
[0.15, 0.85]), each with 4 random balanced bisection trees of depth 2 (and one
of depth 3), checked exactly in the form the Lean theorems state:

  C2s  BisectionTree (min budgets per level)   pw(G) ≤ k + Σ_i b_i
  C2m  BisectionTreeMax (max budgets)          pw(G) ≤ k + Σ_i b_i
  C2   the item's factor-2 form                pw(G) ≤ k + 2 Σ_i b_i

A violation prints the graph (graph6 or edge list) and stops.

    nice -n 19 python3 reports/scratch/edwards_mcdermid/04_cut/check.py --max-n 7 --workers 8
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import subprocess
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, "/home/al/dev/MOSP")

from learning.edwards_mcdermid import (  # noqa: E402
    bisection_bound, bits, boundary_to, parse_g6, pathwidth_induced, separator_cut_bound,
)
from learning.first_moment import vertex_separation_brute  # noqa: E402

HERE = "/home/al/dev/MOSP/reports/scratch/edwards_mcdermid/04_cut"
RANDOM_GRAPHS = 2000
TREES_PER_GRAPH = 4


def submasks(S: int):
    T = S
    while True:
        yield T
        if T == 0:
            break
        T = (T - 1) & S


def one(arg: tuple[int, str]) -> dict:
    idx, line = arg
    n, adj = parse_g6(line)
    full = (1 << n) - 1
    cnt: collections.Counter = collections.Counter()
    slack: collections.Counter = collections.Counter()
    viol: list[str] = []
    pwc = {S: pathwidth_induced(adj, S) for S in range(1 << n)}
    pw_of = pwc.__getitem__

    def bad(tag: str, what: str) -> None:
        viol.append(f"{tag} n={n} g6={line.strip()} {what}")

    for U in range(1 << n):
        for T in range(1 << n):
            cnt["L1g"] += 1
            if not pw_of(U) <= pw_of(T) + (U & ~T).bit_count():
                bad("L1g", f"T={T:b} U={U:b}")
        for T in submasks(U):
            # M and L1r on every T ⊆ U
            cnt["M"] += 1
            if not pw_of(T) <= pw_of(U):
                bad("M", f"T={T:b} U={U:b}")
            cnt["L1r"] += 1
            if not pw_of(U) <= pw_of(T) + (U & ~T).bit_count():
                bad("L1r", f"T={T:b} U={U:b}")
            # the pair (S1, S2) = (T, U \ T) is disjoint with union U
            S1, S2 = T, U & ~T
            b12 = boundary_to(adj, S1, S2).bit_count()
            b21 = boundary_to(adj, S2, S1).bit_count()
            m = max(pw_of(S1), pw_of(S2))
            cnt["C1r1"] += 1
            if not pw_of(U) <= m + b12:
                bad("C1r1", f"S1={S1:b} S2={S2:b}")
            bound_r = separator_cut_bound(adj, S1, S2, pw_of)
            cnt["C1r"] += 1
            if not pw_of(U) <= bound_r:
                bad("C1r", f"S1={S1:b} S2={S2:b} pw={pw_of(U)} bound={bound_r}")
            if U == full and not (S1 >> (n - 1)) & 1:
                # each partition once (S1 avoids the last vertex)
                cnt["C1s"] += 1
                if not pw_of(full) <= bound_r:
                    bad("C1s", f"S={S1:b}")
                bound = max(pw_of(S1) + b12, pw_of(S2) + b21, b12 + b21 - 1)
                cnt["C1"] += 1
                if not pw_of(full) <= bound:
                    bad("C1", f"S={S1:b}")
                if not bound_r <= bound:
                    bad("C1s-le-C1", f"S={S1:b}")
                slack[bound_r - pw_of(full)] += 1
                if bound_r == pw_of(full):
                    cnt["C1s_tight"] += 1
    return {"n": n, "cnt": cnt, "slack": slack, "viol": viol}


def random_tree(rng: random.Random, verts: list[int], depth: int):
    if depth == 0 or len(verts) <= 1:
        m = 0
        for v in verts:
            m |= 1 << v
        return m
    vs = list(verts)
    rng.shuffle(vs)
    h = len(vs) // 2
    return (random_tree(rng, vs[:h], depth - 1), random_tree(rng, vs[h:], depth - 1))


def part_b(seed: int, say) -> tuple[collections.Counter, list[str]]:
    rng = random.Random(seed)
    cnt: collections.Counter = collections.Counter()
    viol: list[str] = []
    slack_s: collections.Counter = collections.Counter()
    for i in range(RANDOM_GRAPHS):
        n = 10 + i % 3
        p = rng.uniform(0.15, 0.85)
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        pw = vertex_separation_brute(adj)
        cache: dict[int, int] = {}

        def pw_of(S: int) -> int:
            if S not in cache:
                cache[S] = pathwidth_induced(adj, S)
            return cache[S]

        edges = [(u, v) for u in range(n) for v in bits(adj[u]) if u < v]
        trees = [random_tree(rng, list(range(n)), 2) for _ in range(TREES_PER_GRAPH)]
        trees.append(random_tree(rng, list(range(n)), 3))
        for t in trees:
            k, bs = bisection_bound(adj, t, pw_of)
            cnt["C2s"] += 1
            if not pw <= k + sum(bs):
                viol.append(f"C2s n={n} edges={edges} tree={t} pw={pw} k={k} bs={bs}")
            slack_s[k + sum(bs) - pw] += 1
            km, bsm = bisection_bound(adj, t, pw_of, use_max=True)
            cnt["C2m"] += 1
            if not pw <= km + sum(bsm):
                viol.append(f"C2m n={n} edges={edges} tree={t} pw={pw} k={km} bs={bsm}")
            cnt["C2"] += 1
            if not pw <= km + 2 * sum(bsm):
                viol.append(f"C2 n={n} edges={edges} tree={t} pw={pw} k={km} bs={bsm}")
            if not (k + sum(bs) <= km + sum(bsm) <= km + 2 * sum(bsm)):
                viol.append(f"C2-order n={n} edges={edges} tree={t}")
        if viol:
            break
    say("part B slack of C2s (k + Σ b − pw): "
        + ", ".join(f"{s}:{c}" for s, c in sorted(slack_s.items())))
    return cnt, viol


def geng(n: int) -> list[str]:
    return subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True,
                          check=True).stdout.splitlines()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=7)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=4)
    ap.add_argument("--log", default=f"{HERE}/check.log")
    a = ap.parse_args()
    log = open(a.log, "w")

    def say(s: str = "") -> None:
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"# item 04 brute-force check, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, "
        f"n = 1..{a.max_n}, {a.workers} workers, part B seed {a.seed}")
    summary: dict = {"per_n": {}, "part_b": {}}
    violations: list[str] = []
    t0 = time.time()
    with Pool(a.workers) as pool:
        for n in range(1, a.max_n + 1):
            lines = geng(n)
            tn = time.time()
            cnt: collections.Counter = collections.Counter()
            slack: collections.Counter = collections.Counter()
            stop = False
            for res in pool.imap_unordered(one, list(enumerate(lines)), chunksize=16):
                cnt.update(res["cnt"])
                slack.update(res["slack"])
                if res["viol"]:
                    violations += res["viol"]
                    for v in res["viol"]:
                        say("VIOLATION " + v)
                    stop = True
                    break
            summary["per_n"][n] = {"graphs": len(lines), "cnt": dict(cnt),
                                   "C1s_slack": {str(k): v for k, v in sorted(slack.items())},
                                   "seconds": round(time.time() - tn, 1)}
            say(f"n={n}: {len(lines)} graphs in {time.time() - tn:.1f}s; "
                + "; ".join(f"{k}={v}" for k, v in sorted(cnt.items()))
                + "; C1s slack " + ", ".join(f"{k}:{v}" for k, v in sorted(slack.items())))
            if stop:
                say("STOPPED on a violation")
                break
    if not violations:
        tb = time.time()
        cnt_b, viol_b = part_b(a.seed, say)
        violations += viol_b
        for v in viol_b:
            say("VIOLATION " + v)
        summary["part_b"] = {"graphs": RANDOM_GRAPHS, "cnt": dict(cnt_b),
                             "seconds": round(time.time() - tb, 1)}
        say(f"part B: {RANDOM_GRAPHS} random graphs at n = 10, 11, 12 in {time.time() - tb:.1f}s; "
            + "; ".join(f"{k}={v}" for k, v in sorted(cnt_b.items())))
    summary["violations"] = violations
    summary["seconds"] = round(time.time() - t0, 1)
    with open(f"{HERE}/summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    say(f"done in {time.time() - t0:.1f}s; violations: {len(violations)}")


if __name__ == "__main__":
    main()
