#!/usr/bin/env python3
"""Item 09 of loop0012: the pathwidth assembly of `DegreeBound/Pathwidth.lean`, checked
in the form the file proves it, before it is stated.

The hypotheses (H1), (H3) are named `Prop`s and cannot be checked; what is checked is every
*deterministic* statement the assembly rests on, on every graph on 1..8 vertices
(`nauty-geng`, 13,598 graphs; pathwidth by the subset DP of
`learning.edwards_mcdermid.pathwidth_induced`), and the numerical pin of the item on 500
random graphs at `n ≤ 12`:

  PB   pathwidth ⊥ = 0                                        (`pathwidth_bot`)
  IX   pw(G) ≤ pw(G − X) + |X| for every X ⊆ V                 (`pathwidth_le_pathwidth_isolateSet_add_card`)
  IXc  pw(G[Xᶜ]) ≤ pw(G − X)                                   (`pathwidth_induce_compl_le_isolateSet`)
  I1   pw(G) ≤ pw(G − v) + 1                                   (`pathwidth_le_pathwidth_isolate_add_one`)
  CR   pw(G[C₀]) ≤ pw(G|C₀) for every component C₀             (`pathwidth_induce_compFinset_le_restrict`)
  CM   C connected, v ∈ C ⇒ C ⊆ C₀(v) and pw(G[C]) ≤ pw(G[C₀])  (`subset_compFinset_of_connected`, `pathwidth_induce_mono`)
  CC   G[C₀] is connected for every component                   (`connected_induce_compFinset`)
  ID   v ∈ C₀ ⇒ deg_{G[C₀]}(v) = deg_G(v)                       (`degree_induce_compFinset`)
  EZ   every degree of C zero ⇒ G[C] = ⊥, pw = 0                 (`induce_eq_bot_of_forall_degree_eq_zero`)
  FC   pw(G) = max over connected C of pw(G[C]) (0 if none)      (`pathwidth_le_rat_of_forall_connected`)
  BC   for reduced basic B ≠ ⊥, each non-trivial component C₀: cubic ⇒ measure
       τ_need = pw(B[C₀]) − (|C₀|/6 − 1/6); second kind ⇒ some u ∈ C₀ has r(B|C₀ − u) = ∅
       and pw(B[C₀]) ≤ pw(B|C₀ − u) + 1 (measure ρ_need = pw(B|C₀ − u), the (H3) gap at ⊥);
       and compPotential(C₀) ≤ f⁻(B)                            (`pathwidth_component_le`)
  A1   reduced G ≠ ⊥, X from Algorithm X (item 02), B = r(G − X): pw(G) ≤ pw(G − X) + |X|,
       |X| + f⁻(B) ≤ f⁻(G); measure pw(G − X) − pw(B) (the (H3) gap) and pw(G) − f⁻(G)
       (what τ + 2ρ + 1 must reach)                             (`pathwidth_le_potentialMinus_of_hypotheses`)
  A2   every G, B = r(G): pw(G) − f(B) and pw(G) − f(G) measured, f(B) ≤ f(G)
                                                                 (`pathwidth_le_degreeSum_of_hypotheses`, `_histogram_`)
  PIN  500 random graphs, 1 ≤ n ≤ 12: pw(G) ≤ Σ_{r(G)} g + B(n), B = 3 (n ≤ 9), 10/3 (n = 10),
       4 (n ≤ 20), item 02 §2.5 and item 01 §1.3's measured budgets (a pipeline check,
       not a check of the theorem, whose budgets are abstract)

Usage: nice -n 19 python3 check.py --max-n 8 --workers 8
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
    algorithm_x, bits, components, f_potential, fminus, g, g_prime, is_basic, is_reduced,
    isolate, isolate_set, main_term, min_degree, parse_g6, pathwidth_induced, reduce, restrict,
    support,
)


def full(n: int) -> int:
    return (1 << n) - 1


def connected_mask(adj: list[int], C: int) -> bool:
    if C == 0:
        return False
    v = (C & -C).bit_length() - 1
    seen = 1 << v
    frontier = seen
    while frontier:
        nxt = 0
        for u in bits(frontier):
            nxt |= adj[u] & C
        nxt &= ~seen
        seen |= nxt
        frontier = nxt
    return seen == C


def comp_potential(adj: list[int], C: int) -> Fraction:
    return sum((g(adj[v].bit_count()) for v in bits(C)), Fraction(0)) - g_prime(min_degree(adj, C))


def check_graph(adj: list[int], rng: random.Random, exhaustive_X: bool) -> tuple[dict, list[str], dict]:
    """One graph: the counters, the violations, the maxima measured."""
    n = len(adj)
    cnt: collections.Counter = collections.Counter()
    viol: list[str] = []
    mx: dict[str, Fraction] = {}

    def bump(key, val):
        if key not in mx or val > mx[key]:
            mx[key] = val

    V = full(n)
    pw = {}

    def pw_of(adj_, S):
        return pathwidth_induced(adj_, S)

    pwG = pw_of(adj, V)
    cnt["graphs"] += 1
    # PB
    cnt["PB"] += 1
    if pw_of([0] * n, V) != 0:
        viol.append(f"PB n={n}")
    # IX, IXc: every X (exhaustive to 8), else 2n random X
    Xs = range(V + 1) if exhaustive_X else [rng.randrange(V + 1) for _ in range(2 * n)]
    for X in Xs:
        GX = isolate_set(adj, X)
        pwGX = pw_of(GX, V)
        cnt["IX"] += 1
        if pwG > pwGX + X.bit_count():
            viol.append(f"IX {adj} X={X}")
        cnt["IXc"] += 1
        if pw_of(adj, V & ~X) > pwGX:
            viol.append(f"IXc {adj} X={X}")
    # I1
    for v in range(n):
        cnt["I1"] += 1
        if pwG > pw_of(isolate(adj, v), V) + 1:
            viol.append(f"I1 {adj} v={v}")
    # components
    comps = components(adj, support_only=False)
    comp_pw = {}
    for C0 in comps:
        cnt["CC"] += 1
        if not connected_mask(adj, C0):
            viol.append(f"CC {adj} C0={C0}")
        p = pw_of(adj, C0)
        comp_pw[C0] = p
        cnt["CR"] += 1
        if p > pw_of(restrict(adj, C0), V):
            viol.append(f"CR {adj} C0={C0}")
        for v in bits(C0):
            cnt["ID"] += 1
            if (adj[v] & C0).bit_count() != adj[v].bit_count():
                viol.append(f"ID {adj} v={v}")
    # CM, EZ, FC over every connected subset (exhaustive to 8; sampled above)
    subsets = range(1, V + 1) if exhaustive_X else [rng.randrange(1, V + 1) for _ in range(4 * n)]
    best = 0
    for C in subsets:
        if not connected_mask(adj, C):
            continue
        p = pw_of(adj, C)
        best = max(best, p)
        v = (C & -C).bit_length() - 1
        C0 = next(c for c in comps if (c >> v) & 1)
        cnt["CM"] += 1
        if C & ~C0 or p > comp_pw[C0]:
            viol.append(f"CM {adj} C={C}")
        if all(adj[u] == 0 for u in bits(C)):
            cnt["EZ"] += 1
            if p != 0 or C.bit_count() != 1:
                viol.append(f"EZ {adj} C={C}")
    if exhaustive_X:
        cnt["FC"] += 1
        if pwG != best:
            viol.append(f"FC {adj} pw={pwG} max={best}")
    # BC: reduced basic non-empty
    if is_reduced(adj) and support(adj) and is_basic(adj):
        cnt["BC_graphs"] += 1
        fm = fminus(adj)
        for C0 in components(adj):
            cp = comp_potential(adj, C0)
            cnt["BC_components"] += 1
            if cp > fm:
                viol.append(f"BC_cp_le_fminus {adj} C0={C0}")
            p = comp_pw[C0]
            sub = restrict(adj, C0)
            if all(adj[v].bit_count() == 3 for v in bits(C0)):
                cnt["BC_cubic"] += 1
                if cp != Fraction(C0.bit_count(), 6) - Fraction(1, 6):
                    viol.append(f"BC_cubic_cp {adj} C0={C0}")
                bump("tau_need_cubic", Fraction(p) - (Fraction(C0.bit_count(), 6) - Fraction(1, 6)))
            else:
                us = [u for u in bits(C0) if not any(reduce(isolate(sub, u))[0])]
                cnt["BC_second"] += 1
                if not us:
                    viol.append(f"BC_second_no_u {adj} C0={C0}")
                    continue
                rho = [pw_of(isolate(sub, u), V) for u in us]
                if any(p > r + 1 for r in rho):
                    viol.append(f"BC_second_pw {adj} C0={C0}")
                bump("rho_need_second_min_u", Fraction(min(rho)))
                bump("rho_need_second_max_u", Fraction(max(rho)))
                bump("pw_minus_cp_second", Fraction(p) - cp)
    # A1
    if is_reduced(adj) and support(adj):
        cnt["A1"] += 1
        X, _ = algorithm_x(adj, rng)
        GX = isolate_set(adj, X)
        B, _ = reduce(GX)
        if not (is_reduced(B) and any(B) and is_basic(B)):
            viol.append(f"A1_B {adj} X={X}")
        pwGX = pw_of(GX, V)
        pwB = pw_of(B, V)
        if pwG > pwGX + X.bit_count():
            viol.append(f"A1_IX {adj} X={X}")
        if X.bit_count() + fminus(B) > fminus(adj):
            viol.append(f"A1_T1 {adj} X={X}")
        bump("rho_need_A1", Fraction(pwGX - pwB))
        bump("A1_pw_minus_fminus", Fraction(pwG) - fminus(adj))
        bump("A1_pwB_minus_fminusB", Fraction(pwB) - fminus(B))
    # A2
    cnt["A2"] += 1
    B, _ = reduce(adj)
    if f_potential(B) > f_potential(adj):
        viol.append(f"A2_f_le {adj}")
    bump("rho_need_A2", Fraction(pwG - pw_of(B, V)))
    bump("A2_pw_minus_fB", Fraction(pwG) - f_potential(B))
    bump("A2_pw_minus_fG", Fraction(pwG) - f_potential(adj))
    return dict(cnt), viol, {k: str(v) for k, v in mx.items()}


def one(job):
    i, line, exhaustive = job
    n, adj = parse_g6(line)
    rng = random.Random(1109 * 100003 + i)
    return check_graph(adj, rng, exhaustive)


def geng(n: int) -> list[str]:
    return subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True,
                          check=True).stdout.splitlines()


def budget(n: int) -> Fraction:
    if n <= 9:
        return Fraction(3)
    if n == 10:
        return Fraction(10, 3)
    return Fraction(4)


def pin_job(i):
    rng = random.Random(1109_000 + i)
    n = rng.randint(1, 12)
    p = rng.choice([0.2, 0.35, 0.5, 0.7, 0.9])
    adj = [0] * n
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    pw = pathwidth_induced(adj, full(n))
    mt = main_term(adj)
    ok = Fraction(pw) <= mt + budget(n)
    cnt, viol, mx = check_graph(adj, rng, exhaustive_X=False)
    return {"n": n, "pw": pw, "main": str(mt), "deficit": str(Fraction(pw) - mt), "ok": ok,
            "cnt": cnt, "viol": viol, "mx": mx}


def merge_mx(acc: dict, mx: dict) -> None:
    for k, v in mx.items():
        fv = Fraction(v)
        if k not in acc or fv > acc[k]:
            acc[k] = fv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=8)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--pin", type=int, default=500)
    a = ap.parse_args()
    log = open(f"{HERE}/check.log", "w")

    def say(s: str = "") -> None:
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"# item 09 brute-force check, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, "
        f"every graph on 1..{a.max_n} vertices (nauty-geng), {a.workers} workers; "
        f"{a.pin} random graphs at n ≤ 12 for the pin")
    total: collections.Counter = collections.Counter()
    per_n: dict[int, dict] = {}
    mx: dict[str, Fraction] = {}
    mx_per_n: dict[int, dict] = {}
    violations: list[str] = []
    t0 = time.time()
    with Pool(a.workers) as pool:
        for n in range(1, a.max_n + 1):
            lines = geng(n)
            cnt: collections.Counter = collections.Counter()
            mxn: dict[str, Fraction] = {}
            for res in pool.imap_unordered(one, [(i, l, True) for i, l in enumerate(lines)],
                                           chunksize=64):
                c, v, m = res
                cnt.update(c)
                violations += v
                merge_mx(mxn, m)
            per_n[n] = dict(cnt)
            mx_per_n[n] = {k: str(v) for k, v in mxn.items()}
            total.update(cnt)
            merge_mx(mx, {k: str(v) for k, v in mxn.items()})
            say(f"n={n}: {len(lines)} graphs; IX {cnt['IX']}, CM {cnt['CM']}, FC {cnt['FC']}, "
                f"BC components {cnt['BC_components']} (cubic {cnt['BC_cubic']}, second kind "
                f"{cnt['BC_second']}), A1 {cnt['A1']}; maxima {mx_per_n[n]}; "
                f"violations so far {len(violations)}; {time.time() - t0:.0f} s")
        pin_rows = list(pool.imap_unordered(pin_job, range(a.pin), chunksize=16))
    pin_ok = sum(1 for r in pin_rows if r["ok"])
    pin_cnt: collections.Counter = collections.Counter()
    pin_mx: dict[str, Fraction] = {}
    for r in pin_rows:
        pin_cnt.update(r["cnt"])
        violations += r["viol"]
        merge_mx(pin_mx, r["mx"])
    worst = max(pin_rows, key=lambda r: Fraction(r["deficit"]))
    say(f"pin: {pin_ok}/{len(pin_rows)} random graphs (n ≤ 12) have pw ≤ Σ_r(G) g + B(n); "
        f"largest deficit {worst['deficit']} at n={worst['n']} (pw {worst['pw']}, main {worst['main']}); "
        f"the deterministic checks on the same graphs: {dict(pin_cnt)}; maxima {{{', '.join(f'{k}: {v}' for k, v in pin_mx.items())}}}; "
        f"violations so far {len(violations)}")
    say(f"TOTAL: {dict(total)}")
    say(f"MAXIMA to n={a.max_n}: {{{', '.join(f'{k}: {v}' for k, v in mx.items())}}}")
    say(f"violations: {len(violations)}")
    for v in violations[:50]:
        say(v)
    with open(f"{HERE}/summary.json", "w") as fh:
        json.dump({"per_n": per_n, "total": dict(total), "mx": {k: str(v) for k, v in mx.items()},
                   "mx_per_n": mx_per_n,
                   "pin": {"graphs": len(pin_rows), "ok": pin_ok, "worst_deficit": worst["deficit"],
                           "worst_n": worst["n"], "cnt": dict(pin_cnt),
                           "mx": {k: str(v) for k, v in pin_mx.items()}},
                   "violations": len(violations), "seconds": round(time.time() - t0, 1)}, fh, indent=1)
    say("OK" if not violations else "VIOLATIONS")


if __name__ == "__main__":
    main()
