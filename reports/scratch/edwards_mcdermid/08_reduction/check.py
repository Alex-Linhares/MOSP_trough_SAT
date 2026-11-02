#!/usr/bin/env python3
"""Item 08 of loop0012: Theorem 3.2 (the reduction theorem), checked in the form
`ReductionTheorem.lean` proves it, on every graph on 1..9 vertices (`nauty-geng`).

Item 02 checked T1 through Algorithm X (89,972 reduced non-empty graphs to 9). This
script replays the **Lean induction** instead — the recursion on the support size with
its three cases — and checks every lemma the file states that no earlier item checked:

  T1   for every reduced non-empty G: X ⊆ supp G, SPReduces (G − X) B (decided by a
       search over step sequences), B ≠ ⊥, IsSPReduced B, IsBasic B,
       |X| + f⁻(B) ≤ f⁻(G); the recursion as the proof does it:
         basic        → X = ∅, B = G;
         disconnected → C the component of a random support vertex u, G₁ = G|C,
                        G₂ = G|Cᶜ (both reduced, non-empty, smaller support), the
                        recursion on both, X = X₁ ∪ X₂, B = B₁ ⊔ B₂;
         connected    → w the two-key choice (random among ties), G* a random reduct
                        of G − w (non-empty, reduced, smaller support, w ∉ supp G*),
                        1 + f⁻(G*) ≤ f⁻(G) (S1), the recursion on G*, X = {w} ∪ X*,
                        (G − w) − X* →* G* − X* (R4, by search), transitivity.
  RS   restrict: ndeg (G|S) x = ndeg G x for x ∈ S, 0 otherwise, when no edge crosses
       S (`ndeg_restrict_of_mem`, `_of_not_mem`); IsSPReduced (G|S) (`IsSPReduced.restrict`);
       G|C ⊔ G|Cᶜ = G (`restrict_sup_restrict_compl`, item 06)
  IS   isolateSet (G₁ ⊔ G₂) X = isolateSet G₁ X ⊔ isolateSet G₂ X (`isolateSet_sup`);
       isolateSet G (X ∪ Y) = isolateSet G X when Y has no G-edges
       (`isolateSet_union_of_forall_not_adj`)
  SUP  for graphs with disjoint supports: IsSPReduced and IsBasic pass to the union
       (`IsSPReduced.sup`, `IsBasic.sup`), f⁻ is additive (item 05), a component of
       the union containing a G₁-vertex is a G₁-component (`supp_eq_of_agree`)
  CP   per component C with a positive-degree vertex: cubic ⇒ compPotential = |C|/6 − 1/6
       (`compPotential_cubic`); reduced and some degree ≥ 4 ⇒ 5/6 ≤ compPotential and
       |C| ≥ 5 (`compPotential_ge_five_sixths`, `five_le_card_compFinset`); reduced ⇒
       one of the two (`compPotential_cubic_or_ge_five_sixths`)

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
    bits, components, degrees, f_potential, fminus, g, g_prime, is_basic, is_cubic,
    is_reduced, isolate, isolate_set, min_degree, paper_choice, parse_g6, reduce_random,
    restrict, sp_step, step_vertices, support,
)


def sup(a: list[int], b: list[int]) -> list[int]:
    return [x | y for x, y in zip(a, b)]


def sp_reaches(G: list[int], H: list[int], limit: int = 200_000) -> bool:
    """`SPReduces G H`: is `H` reachable from `G` by series-parallel steps? Depth-first
    search over the step relation with a visited set (every step empties a vertex, so
    the depth is at most the support size)."""
    target = tuple(H)
    seen = {tuple(G)}
    stack = [G]
    while stack:
        cur = stack.pop()
        if tuple(cur) == target:
            return True
        if len(seen) > limit:
            raise RuntimeError("sp_reaches: state limit")
        for v in step_vertices(cur):
            nxt = sp_step(cur, v)
            t = tuple(nxt)
            if t not in seen:
                seen.add(t)
                stack.append(nxt)
    return False


def comp_potential(adj: list[int], C: int) -> Fraction:
    return sum((g(adj[v].bit_count()) for v in bits(C)), Fraction(0)) - g_prime(min_degree(adj, C))


class Checker:
    def __init__(self, line: str, rng: random.Random) -> None:
        self.line = line.strip()
        self.rng = rng
        self.cnt: collections.Counter = collections.Counter()
        self.viol: list[str] = []

    def bad(self, stmt: str, detail: str) -> None:
        self.viol.append(f"{stmt}\t{self.line}\t{detail}")

    # the Lean induction, replayed
    def recursion(self, adj: list[int], depth: int = 0) -> tuple[int, list[int]]:
        n = len(adj)
        full = (1 << n) - 1
        supp = support(adj)
        assert is_reduced(adj) and supp
        self.cnt["rec_calls"] += 1
        if is_basic(adj):
            self.cnt["case_basic"] += 1
            return 0, adj
        comps = components(adj)
        if len(comps) >= 2:
            self.cnt["case_disconnected"] += 1
            u = self.rng.choice(list(bits(supp)))
            C = next(c for c in comps if (c >> u) & 1)
            Cc = full & ~C
            G1, G2 = restrict(adj, C), restrict(adj, Cc)
            # RS: degrees and reducedness of the halves; the union identity
            d = degrees(adj)
            for x in range(n):
                if (C >> x) & 1:
                    if G1[x].bit_count() != d[x] or G2[x].bit_count() != 0:
                        self.bad("RS_deg", f"x={x} C={C:b}")
                else:
                    if G1[x].bit_count() != 0 or G2[x].bit_count() != d[x]:
                        self.bad("RS_deg", f"x={x} C={C:b}")
            self.cnt["RS_deg"] += n
            if not (is_reduced(G1) and is_reduced(G2)):
                self.bad("RS_reduced", f"C={C:b}")
            if sup(G1, G2) != adj:
                self.bad("RS_sup", f"C={C:b}")
            if not (any(G1) and any(G2)):
                self.bad("RS_nonempty", f"C={C:b}")
            if not (support(G1) < supp and support(G2) < supp and support(G1) != supp and support(G2) != supp):
                self.bad("RS_smaller", f"C={C:b}")
            self.cnt["RS"] += 1
            X1, B1 = self.recursion(G1, depth + 1)
            X2, B2 = self.recursion(G2, depth + 1)
            # the sides stay inside their halves
            if X1 & ~C or X2 & C:
                self.bad("D_sides", f"X1={X1:b} X2={X2:b} C={C:b}")
            if support(B1) & ~C or support(B2) & C:
                self.bad("D_Bsides", f"C={C:b}")
            # IS: the isolateSet identities
            lhs = isolate_set(adj, X1 | X2)
            rhs = sup(isolate_set(G1, X1), isolate_set(G2, X2))
            if lhs != rhs:
                self.bad("IS", f"X1={X1:b} X2={X2:b}")
            if isolate_set(sup(G1, G2), X1 | X2) != sup(isolate_set(G1, X1 | X2), isolate_set(G2, X1 | X2)):
                self.bad("IS_sup", f"X1={X1:b} X2={X2:b}")
            if isolate_set(G1, X1 | X2) != isolate_set(G1, X1) or isolate_set(G2, X1 | X2) != isolate_set(G2, X2):
                self.bad("IS_union", f"X1={X1:b} X2={X2:b}")
            self.cnt["IS"] += 1
            # SUP: the union of the two basic reducts
            B = sup(B1, B2)
            if support(B1) & support(B2):
                self.bad("SUP_disjoint", "")
            if not is_reduced(B):
                self.bad("SUP_reduced", "")
            if not is_basic(B):
                self.bad("SUP_basic", "")
            if fminus(B) != fminus(B1) + fminus(B2):
                self.bad("SUP_fminus", "")
            if fminus(adj) != fminus(G1) + fminus(G2):
                self.bad("SUP_fminusG", f"C={C:b}")
            # a component of B containing a B1-vertex is a B1-component
            for K in components(B):
                v = next(iter(bits(K)))
                side = B1 if B1[v] else B2
                KK = next(c for c in components(side) if (c >> v) & 1)
                if KK != K:
                    self.bad("SUP_comp", f"K={K:b}")
                self.cnt["SUP_comp"] += 1
            self.cnt["SUP"] += 1
            # the lifted reductions (R5), by search
            if not sp_reaches(sup(isolate_set(G1, X1), isolate_set(G2, X2)), sup(B1, isolate_set(G2, X2))):
                self.bad("D_R5a", f"X1={X1:b}")
            if not sp_reaches(sup(isolate_set(G2, X2), B1), sup(B2, B1)):
                self.bad("D_R5b", f"X2={X2:b}")
            self.cnt["R5"] += 2
            return X1 | X2, B
        # connected, not basic
        self.cnt["case_connected"] += 1
        _, chosen, D = paper_choice(adj)
        w = self.rng.choice(chosen)
        Gp = isolate(adj, w)
        Gs = reduce_random(Gp, self.rng)
        if D < 4:
            self.bad("C_delta", f"w={w} Δ={D}")
        if not any(Gs):
            self.bad("C_nonempty", f"w={w}")
        if not is_reduced(Gs):
            self.bad("C_reduced", f"w={w}")
        ss = support(Gs)
        if not (ss & ~supp == 0 and ss != supp and not (ss >> w) & 1):
            self.bad("C_smaller", f"w={w}")
        if not 1 + fminus(Gs) <= fminus(adj):
            self.bad("C_S1", f"w={w}")
        self.cnt["C"] += 1
        Xs, B = self.recursion(Gs, depth + 1)
        if (Xs >> w) & 1:
            self.bad("C_wX", f"w={w} Xs={Xs:b}")
        if Xs & ~ss:
            self.bad("C_Xsupp", f"w={w} Xs={Xs:b}")
        X = Xs | (1 << w)
        if isolate_set(adj, X) != isolate_set(Gp, Xs):
            self.bad("C_insert", f"w={w} Xs={Xs:b}")
        # R4 by search: (G − w) − X* →* G* − X*
        if not sp_reaches(isolate_set(Gp, Xs), isolate_set(Gs, Xs)):
            self.bad("C_R4", f"w={w} Xs={Xs:b}")
        self.cnt["R4"] += 1
        if not Xs.bit_count() + 1 + fminus(B) <= fminus(adj):
            self.bad("C_ineq", f"w={w}")
        return X, B

    def run(self, adj: list[int]) -> None:
        n = len(adj)
        self.cnt["graphs"] += 1
        d = degrees(adj)
        supp = support(adj)
        # CP: the per-component statements, on every graph
        for C in components(adj):
            self.cnt["CP_components"] += 1
            cp = comp_potential(adj, C)
            N = C.bit_count()
            if is_cubic(adj, C):
                self.cnt["CP_cubic"] += 1
                if cp != Fraction(N, 6) - Fraction(1, 6):
                    self.bad("CP_cubic", f"C={C:b} cp={cp}")
            if all(d[v] >= 3 for v in bits(C)):
                self.cnt["CP_reduced"] += 1
                if any(d[v] >= 4 for v in bits(C)):
                    self.cnt["CP_noncubic"] += 1
                    if not cp >= Fraction(5, 6):
                        self.bad("CP_floor", f"C={C:b} cp={cp}")
                    if N < 5:
                        self.bad("CP_five", f"C={C:b} N={N}")
                if not (cp == Fraction(N, 6) - Fraction(1, 6) or cp >= Fraction(5, 6)):
                    self.bad("CP_dichotomy", f"C={C:b} cp={cp}")
            if cp < 0:
                self.bad("CP_nonneg", f"C={C:b}")
        # RS on the component of the lowest support vertex (any graph)
        if supp:
            u = (supp & -supp).bit_length() - 1
            C = next(c for c in components(adj) if (c >> u) & 1)
            G1 = restrict(adj, C)
            for x in range(n):
                want = d[x] if (C >> x) & 1 else 0
                if G1[x].bit_count() != want:
                    self.bad("RS_deg_any", f"x={x} C={C:b}")
            if is_reduced(adj) and not is_reduced(G1):
                self.bad("RS_reduced_any", f"C={C:b}")
            self.cnt["RS_any"] += 1
        # IS on random X, Y with Y off the support
        full = (1 << n) - 1
        X = self.rng.randrange(1 << n)
        off = full & ~supp
        Y = self.rng.randrange(1 << n) & off
        if isolate_set(adj, X | Y) != isolate_set(adj, X):
            self.bad("IS_union_any", f"X={X:b} Y={Y:b}")
        self.cnt["IS_any"] += 1
        # T1 as the proof does it
        if is_reduced(adj) and supp:
            self.cnt["T1"] += 1
            X, B = self.recursion(adj)
            if X & ~supp:
                self.bad("T1_supp", f"X={X:b}")
            if not any(B):
                self.bad("T1_empty", f"X={X:b}")
            if not is_reduced(B):
                self.bad("T1_reduced", f"X={X:b}")
            if not is_basic(B):
                self.bad("T1_basic", f"X={X:b}")
            if not X.bit_count() + fminus(B) <= fminus(adj):
                self.bad("T1_ineq", f"X={X:b} |X|+f⁻(B)={X.bit_count() + fminus(B)} f⁻(G)={fminus(adj)}")
            if not sp_reaches(isolate_set(adj, X), B):
                self.bad("T1_reduces", f"X={X:b}")
            self.cnt[f"T1_X_{X.bit_count()}"] += 1


def one(args: tuple[int, str]) -> dict:
    idx, line = args
    n, adj = parse_g6(line)
    ck = Checker(line, random.Random(idx * 7_919 + n))
    ck.run(adj)
    return {"cnt": ck.cnt, "viol": ck.viol}


def pair(args: tuple[int, str, str]) -> dict:
    """SUP on two random graphs embedded on disjoint vertex sets."""
    idx, l1, l2 = args
    n1, a1 = parse_g6(l1)
    n2, a2 = parse_g6(l2)
    n = n1 + n2
    G1 = a1 + [0] * n2
    G2 = [0] * n1 + [a << n1 for a in a2]
    G = sup(G1, G2)
    cnt: collections.Counter = collections.Counter()
    viol: list[str] = []
    cnt["pairs"] += 1
    r1, r2, r = is_reduced(G1), is_reduced(G2), is_reduced(G)
    b1, b2, b = is_basic(G1), is_basic(G2), is_basic(G)
    if r1 and r2 and not r:
        viol.append(f"SUP_reduced_pair\t{l1.strip()} {l2.strip()}")
    if b1 and b2 and not b:
        viol.append(f"SUP_basic_pair\t{l1.strip()} {l2.strip()}")
    if r != (r1 and r2):
        cnt["reduced_converse_fails"] += 1
    if b != (b1 and b2):
        cnt["basic_converse_fails"] += 1
    if fminus(G) != fminus(G1) + fminus(G2):
        viol.append(f"SUP_fminus_pair\t{l1.strip()} {l2.strip()}")
    cnt["both_reduced"] += int(r1 and r2)
    cnt["both_basic"] += int(b1 and b2)
    # the recursion on the union (its disconnected case, which single graphs below 9
    # vertices barely reach): both halves reduced and non-empty
    if r1 and r2 and any(G1) and any(G2):
        ck = Checker(f"{l1.strip()} {l2.strip()}", random.Random(idx))
        ck.run(G)
        cnt.update({f"union_{k}": v for k, v in ck.cnt.items()})
        viol += ck.viol
    return {"cnt": cnt, "viol": viol}


def geng(n: int) -> list[str]:
    return subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True,
                          check=True).stdout.splitlines()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--pairs", type=int, default=20000)
    a = ap.parse_args()
    log = open(f"{HERE}/check.log", "w")

    def say(s: str = "") -> None:
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    say(f"# item 08 brute-force check, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, "
        f"every graph on 1..{a.max_n} vertices (nauty-geng), {a.workers} workers; "
        f"{a.pairs} random disjoint pairs")
    total: collections.Counter = collections.Counter()
    per_n: dict[int, dict] = {}
    violations: list[str] = []
    t0 = time.time()
    rng = random.Random(2026_11_02)
    pool_lines: list[str] = []
    with Pool(a.workers) as pool:
        for n in range(1, a.max_n + 1):
            lines = geng(n)
            if n <= 5:
                pool_lines += lines
                # reduced graphs are rare in the general pool: add the min-degree-3 ones
                # of 4 and 5 vertices twenty times over, so that most pairs are reduced
                if n >= 4:
                    pool_lines += 20 * subprocess.run(["nauty-geng", "-q", "-d3", str(n)],
                                                      capture_output=True, text=True,
                                                      check=True).stdout.splitlines()
            cnt: collections.Counter = collections.Counter()
            for res in pool.imap_unordered(one, list(enumerate(lines)), chunksize=64):
                cnt.update(res["cnt"])
                violations += res["viol"]
            per_n[n] = dict(cnt)
            total.update(cnt)
            say(f"n={n}: {len(lines)} graphs, T1 on {cnt['T1']} reduced non-empty; recursion calls "
                f"{cnt['rec_calls']} (basic/disconnected/connected = {cnt['case_basic']}/"
                f"{cnt['case_disconnected']}/{cnt['case_connected']}); components {cnt['CP_components']} "
                f"(cubic {cnt['CP_cubic']}, reduced non-cubic {cnt['CP_noncubic']}); "
                f"violations so far {len(violations)}; {time.time() - t0:.0f} s")
        # random disjoint pairs from graphs on ≤ 5 vertices (so the union has ≤ 10)
        jobs = [(i, rng.choice(pool_lines), rng.choice(pool_lines)) for i in range(a.pairs)]
        pcnt: collections.Counter = collections.Counter()
        for res in pool.imap_unordered(pair, jobs, chunksize=64):
            pcnt.update(res["cnt"])
            violations += res["viol"]
        total.update(pcnt)
        say(f"pairs: {dict(pcnt)}; violations so far {len(violations)}; {time.time() - t0:.0f} s")
    say(f"TOTAL: {dict(total)}")
    say(f"violations: {len(violations)}")
    for v in violations[:50]:
        say(v)
    with open(f"{HERE}/summary.json", "w") as fh:
        json.dump({"per_n": per_n, "total": dict(total), "pairs": dict(pcnt),
                   "violations": len(violations), "seconds": round(time.time() - t0, 1)}, fh, indent=1)
    say("OK" if not violations else "VIOLATIONS")


if __name__ == "__main__":
    main()
