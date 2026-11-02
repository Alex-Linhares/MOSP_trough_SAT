#!/usr/bin/env python3
"""Item 07 of loop0012: the step inequality, checked in the form `Step.lean` proves it.

For every connected graph of minimum degree 3 on `n ≤ 9` vertices (`nauty-geng -c -d3`)
that is not basic, for every `w` of the paper's two-key choice (maximum degree, then
the smallest lowest-neighbour degree), with `G' = G − w` and `G*` its canonical reduct
plus `R` random reducts, record which case of the Lean proof fires and check the
inequalities the proof combines in that case, in exact rationals:

  D4   Δ = deg w ≥ 4 (`four_le_degree_of_not_isBasic`); `G*` non-empty (`nonbasic_reduct_ne_bot`)
  SJ   1 + f(G') = f(G) + (Δ−1) g'(Δ) + g'(Δ−1) − S, S = Σ_{v∈N(w)} g'(deg v)
       (`one_add_potential_isolate`), and the j₁, j₂, j₃ form for a random ordered
       pair of neighbours (`j_identity`, no sorting)
  S0   j₄ ≥ g'(d) for every v with deg_{G'}(v) = d ≥ 3 (`j4_ge`), and j₄ ≥ 0
  SL   S ≥ g'(deg v₀) + (Δ−1) g'(Δ) for every neighbour v₀ (`sum_g'_neighbors_ge`)
  R    no neighbour of `w` below Δ ⇒ every support vertex has degree Δ
       (`degree_eq_of_reachable`), δ = Δ, S = Δ g'(Δ), j₄ ≥ g'(Δ−1)
  A    some v with 3 ≤ deg_{G'}(v) ≤ δ(G) ⇒ j₄ ≥ g'(δ(G))
  B    otherwise δ(G) = 3 and the minimum-degree vertex is adjacent to `w`;
  B1     a neighbour of degree ≥ 4 ⇒ j₄ ≥ g'(Δ−1);
  B2     all neighbours of degree 3 ⇒ S = Δ g'(3), a support vertex `u` of `G*` is not
         adjacent to `w`, deg_{G'}(u) = deg_G(u) ≥ 3, j₄ ≥ g'(Δ)
  S1   1 + F(G*) ≤ F(G) and 1 + f⁻(G*) ≤ f⁻(G) (the conclusion)

Usage: nice -n 19 python3 check.py --max-n 9 --workers 8
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import subprocess
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))

from learning.edwards_mcdermid import (  # noqa: E402
    F_global, bits, components, degrees, f_potential, fminus, g, g_prime, global_min_degree,
    is_basic, is_reduced, isolate, paper_choice, parse_g6, reduce, reduce_random,
)

RANDOM_REDUCTS = 3


def one(args: tuple[int, str]) -> dict:
    idx, line = args
    n, adj = parse_g6(line)
    rng = random.Random(idx * 7_919 + n)
    cnt: collections.Counter = collections.Counter()
    viol: list[str] = []

    def bad(stmt: str, detail: str) -> None:
        viol.append(f"{stmt}\t{line.strip()}\t{detail}")

    deg = degrees(adj)
    supp = [v for v in range(n) if adj[v]]
    assert len(components(adj)) == 1 and is_reduced(adj) and all(deg[v] >= 3 for v in supp)
    cnt["graphs"] += 1
    if is_basic(adj):
        cnt["basic"] += 1
        return {"cnt": cnt, "viol": viol}
    cnt["nonbasic"] += 1
    maxs, chosen, D = paper_choice(adj)
    if D < 4:
        bad("D4", f"Δ={D}")
    delta = global_min_degree(adj)
    fG = f_potential(adj)
    FG = F_global(adj)
    fmG = fminus(adj)
    for w in chosen:
        cnt["pairs"] += 1
        Gp = isolate(adj, w)
        dp = degrees(Gp)
        nbrs = list(bits(adj[w]))
        S = sum((g_prime(deg[v]) for v in nbrs), Fraction(0))
        fGp = f_potential(Gp)
        # SJ, unsorted
        if 1 + fGp != fG + (D - 1) * g_prime(D) + g_prime(D - 1) - S:
            bad("SJ", f"w={w}")
        cnt["SJ"] += 1
        # j-identity for a random ordered pair of distinct neighbours (no sorting)
        v1, v2 = rng.sample(nbrs, 2)
        rest = [v for v in nbrs if v not in (v1, v2)]
        j1 = g_prime(deg[v1]) - g_prime(D - 1)
        j2 = g_prime(deg[v2]) - g_prime(D)
        j3 = sum((g_prime(deg[v]) - g_prime(D) for v in rest), Fraction(0))
        if 1 + fGp != fG - j1 - j2 - j3:
            bad("SJpair", f"w={w} v1={v1} v2={v2}")
        cnt["SJpair"] += 1
        # SL for every neighbour
        for v0 in nbrs:
            cnt["SL"] += 1
            if not S >= g_prime(deg[v0]) + (D - 1) * g_prime(D):
                bad("SL", f"w={w} v0={v0}")
        reducts = [reduce(Gp)[0]]
        for _ in range(RANDOM_REDUCTS):
            r = reduce_random(Gp, rng)
            if r not in reducts:
                reducts.append(r)
        regular_nb = all(deg[v] == D for v in nbrs)
        for Gs in reducts:
            cnt["triples"] += 1
            if not any(Gs):
                bad("NE", f"w={w}: G* empty")
                continue
            ds = degrees(Gs)
            dstar = global_min_degree(Gs)
            fGs = f_potential(Gs)
            j4 = fGp - fGs + g_prime(dstar)
            if j4 < 0:
                bad("S0nn", f"w={w}")
            for v in range(n):
                if dp[v] >= 3:
                    cnt["S0"] += 1
                    if not j4 >= g_prime(dp[v]):
                        bad("S0", f"w={w} v={v}")
            # the conclusion
            cnt["S1"] += 1
            if not 1 + fGs - g_prime(dstar) <= FG:
                bad("S1", f"w={w} 1+F(G*)={1 + fGs - g_prime(dstar)} F(G)={FG}")
            if not 1 + fminus(Gs) <= fmG:
                bad("S1c", f"w={w}")
            # the case analysis, as the proof does it
            if regular_nb:
                cnt["case_R"] += 1
                if not all(deg[v] == D for v in supp):
                    bad("R_regular", f"w={w}: a neighbourhood of degree Δ but G not Δ-regular")
                if delta != D:
                    bad("R_delta", f"w={w}")
                if S != D * g_prime(D):
                    bad("R_S", f"w={w}")
                if not j4 >= g_prime(D - 1):
                    bad("R_j4", f"w={w}")
                continue
            low = [v for v in nbrs if deg[v] < D]
            assert low
            if any(3 <= dp[v] <= delta for v in range(n)):
                cnt["case_A"] += 1
                if not j4 >= g_prime(delta):
                    bad("A_j4", f"w={w}")
                continue
            cnt["case_B"] += 1
            if delta != 3:
                bad("B_delta3", f"w={w} δ={delta}")
            mins = [v for v in supp if deg[v] == delta]
            if not all((adj[w] >> v) & 1 for v in mins):
                bad("B_adj", f"w={w}: a degree-3 vertex not adjacent to w")
            if any(deg[v] >= 4 for v in nbrs):
                cnt["case_B1"] += 1
                if not j4 >= g_prime(D - 1):
                    bad("B1_j4", f"w={w}")
                continue
            cnt["case_B2"] += 1
            if S != D * g_prime(3):
                bad("B2_S", f"w={w}")
            us = [u for u in range(n) if ds[u] > 0]
            if not us:
                bad("B2_u", f"w={w}")
            for u in us:
                if (adj[w] >> u) & 1 or u == w:
                    bad("B2_adj", f"w={w} u={u}")
                if dp[u] != deg[u] or dp[u] < 3:
                    bad("B2_deg", f"w={w} u={u}")
            if not j4 >= g_prime(D):
                bad("B2_j4", f"w={w}")
    return {"cnt": cnt, "viol": viol}


def geng(n: int) -> list[str]:
    return subprocess.run(["nauty-geng", "-q", "-c", "-d3", str(n)], capture_output=True,
                          text=True, check=True).stdout.splitlines()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    log = open(f"{HERE}/check.log", "w")

    def say(s: str = "") -> None:
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"# item 07 brute-force check, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, "
        f"connected graphs of minimum degree 3, n = 4..{a.max_n}, {a.workers} workers, "
        f"{RANDOM_REDUCTS} random reducts beside the canonical one")
    total: collections.Counter = collections.Counter()
    per_n: dict[int, dict] = {}
    violations: list[str] = []
    t0 = time.time()
    with Pool(a.workers) as pool:
        for n in range(4, a.max_n + 1):
            lines = geng(n)
            cnt: collections.Counter = collections.Counter()
            for res in pool.imap_unordered(one, list(enumerate(lines)), chunksize=64):
                cnt.update(res["cnt"])
                violations += res["viol"]
            per_n[n] = dict(cnt)
            total.update(cnt)
            say(f"n={n}: {len(lines)} graphs, {cnt['nonbasic']} non-basic, {cnt['pairs']} (G, w) pairs, "
                f"{cnt['triples']} (G, w, G*) triples; cases R/A/B1/B2 = {cnt['case_R']}/{cnt['case_A']}/"
                f"{cnt['case_B1']}/{cnt['case_B2']}; S0 {cnt['S0']}, SL {cnt['SL']}; "
                f"violations so far {len(violations)}; {time.time() - t0:.0f} s")
    say(f"TOTAL: {dict(total)}")
    say(f"violations: {len(violations)}")
    for v in violations[:50]:
        say(v)
    with open(f"{HERE}/summary.json", "w") as fh:
        json.dump({"per_n": per_n, "total": dict(total), "violations": len(violations),
                   "random_reducts": RANDOM_REDUCTS, "seconds": round(time.time() - t0, 1)}, fh, indent=1)
    say("OK" if not violations else "VIOLATIONS")


if __name__ == "__main__":
    main()
