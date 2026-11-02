#!/usr/bin/env python3
"""Brute-force checks for loop0012 item 11 (reserve; `reports/edwards_mcdermid.md`
§11). Three parts, each exhaustive where it says so and a stated slice elsewhere.

Part A — Fomin & Høie (2006) Lemma 4, exactly, on every graph of maximum degree
  at most 3 on 1–`--max-n-a` vertices (`nauty-geng -D3`, disconnected included).
  For a graph `G` and a vertex set `X`, `pwX(G, X)` is the least width of a path
  decomposition of `G` whose LAST bag is exactly `X`. It is computed exactly by
  the end-bag subset DP (derivation in the report, §11.2):

      E(V) = 0,  E(P) = max(|∂in P|, min_{v ∉ P} E(P ∪ {v}))  for P ⊊ V,
      pwX(G, X) = max(|X| − 1, E(X)),

  where `∂in P` is the set of vertices of `P` with a neighbour outside `P`.
  (Reverse the decomposition: a first bag `X`, then vertices start one at a time
  and finish as soon as their closed neighbourhood has started; `E(∅)` is the
  vertex separation, Kinnersley 1992.) Three bounds are checked for every
  `(G, X)`, with `n = |V|`:

      L4-printed : pwX ≤ max(|X|, n/3 + 1) + (2/3)·log₃ n + 1   (the lemma as printed)
      L4-proof   : pwX ≤ max(|X|, n/3 + 1) + log₃ n + 1          (what its proof gives:
                   |V(T)| ≤ 2n/3 and Theorem 3 give log₃(2n/3), not (2/3)·log₃ n)
      L4-lean    : pwX ≤ max(|X|, ⌊n/3⌋ + 1) + ⌊log₃(2n + 1)⌋ + 1  (the integer form a
                   Lean statement would take, with `tree_pathwidth_le_log`'s term)

  and the lower-order term the record needs, `max_{G,X} pwX − max(|X|, n/3 + 1)`,
  is recorded per `n` beside the three terms. Sanity: `E(∅)` equals
  `vertex_separation_brute` on every graph; for `n ≤ --sanity-n`, on every `X`,
  `max(pw(G), |X| − 1) ≤ pwX ≤ pw(G[V ∖ X]) + |X|`.

Part B — the Lean statements of `DegreeBound/StepBound.lean`, in the form proved,
  on every graph on 1–`--max-n-b` vertices (`nauty-geng`), every step vertex, and
  one random maximal reduction per graph:
      R6    SPStep G v H  ⇒  pw(G) ≤ pw(H) + 1;  v isolated in H;  supp H ⊂ supp G
      SUB   SPReduces G H ⇒  G − (supp G ∖ supp H) ≤ H   (as graphs)
      SEQ   SPReduces G H ⇒  pw(G) ≤ pw(H) + |supp G ∖ supp H|
                              and pw(G) + |supp H| ≤ pw(H) + |supp G|

Part C — the shape of (H3) at 10 vertices: `pw(G) − pw(r(G))` on the slices
  `nauty-geng 10 r/--mod` for `r` in `--res` (deterministic subtrees of geng's
  enumeration, spread over the residues; NOT a uniform sample), with the
  distribution and the maximum.

A violation prints the graph6 string and stops (unless --no-stop).

    nice -n 19 python3 reports/scratch/edwards_mcdermid/11_reserve/check.py --workers 8
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import random
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from learning.edwards_mcdermid import (  # noqa: E402
    isolate_set, parse_g6, pathwidth_induced, reduce, sp_step, step_vertices, support,
)
from learning.first_moment import vertex_separation_brute  # noqa: E402

HERE = Path(__file__).resolve().parent


# --- Part A: the end-bag DP ----------------------------------------------------


def endbag_dp(adj: list[int]) -> list[int]:
    """`E(P)` for every `P ⊆ V` (bit masks); `E(full) = 0`."""
    n = len(adj)
    full = (1 << n) - 1
    E = [0] * (1 << n)
    for P in range(full - 1, -1, -1):
        rest = full & ~P
        cost = 0
        T = P
        while T:
            v = T & -T
            T ^= v
            if adj[v.bit_length() - 1] & rest:
                cost += 1
        best = min(E[P | b] for b in (1 << v for v in range(n)) if not P & b)
        E[P] = max(cost, best)
    return E


def log3(x: float) -> float:
    return math.log(x) / math.log(3)


def part_a_graph(line: str, sanity_n: int) -> dict:
    n, adj = parse_g6(line)
    full = (1 << n) - 1
    E = endbag_dp(adj)
    pw = vertex_separation_brute(adj) if n > 0 else 0
    out = {"n": n, "pairs": 0, "viol": [], "need": -99.0, "need_arg": None,
           "need_int": -99, "sanity": 0, "e0_ok": E[0] == pw}
    l3 = log3(n) if n >= 1 else 0.0
    printed = (2.0 / 3.0) * l3 + 1.0
    proof = l3 + 1.0
    lean = int(math.floor(log3(2 * n + 1) + 1e-9)) + 1
    # exact integer log: largest k with 3^k ≤ 2n+1
    k = 0
    while 3 ** (k + 1) <= 2 * n + 1:
        k += 1
    lean = k + 1
    third = n / 3.0 + 1.0
    third_int = n // 3 + 1
    for X in range(1 << n):
        cx = bin(X).count("1")
        pwx = max(cx - 1, E[X])
        out["pairs"] += 1
        base = max(cx, third)
        need = pwx - base
        if need > out["need"]:
            out["need"] = need
            out["need_arg"] = (line.strip(), X, pwx)
        need_int = pwx - max(cx, third_int)
        if need_int > out["need_int"]:
            out["need_int"] = need_int
        if pwx > base + printed + 1e-9:
            out["viol"].append(("L4-printed", line.strip(), X, pwx))
        if pwx > base + proof + 1e-9:
            out["viol"].append(("L4-proof", line.strip(), X, pwx))
        if pwx > max(cx, third_int) + lean:
            out["viol"].append(("L4-lean", line.strip(), X, pwx))
        if n <= sanity_n:
            lo = max(pw, cx - 1)
            hi = (pathwidth_induced(adj, full & ~X) if X != full else 0) + cx
            out["sanity"] += 1
            if not (lo <= pwx <= hi):
                out["viol"].append(("sanity", line.strip(), X, pwx, lo, hi))
    if not out["e0_ok"]:
        out["viol"].append(("E0", line.strip(), 0, E[0], pw))
    return out


# --- Part B: the Lean statements of StepBound.lean -------------------------------


def le_graph(A: list[int], B: list[int]) -> bool:
    return all(a & ~b == 0 for a, b in zip(A, B))


def part_b_graph(line: str) -> dict:
    n, adj = parse_g6(line)
    rng = random.Random(hash(line) & 0xFFFFFFFF)
    out = {"n": n, "steps": 0, "seq": 0, "viol": []}
    pw = vs_cache(adj)
    sG = support(adj)
    for v in step_vertices(adj):
        H = sp_step(adj, v)
        out["steps"] += 1
        pwH = vs_cache(H)
        sH = support(H)
        if not (pw <= pwH + 1):
            out["viol"].append(("R6", line.strip(), v, pw, pwH))
        if H[v] != 0:
            out["viol"].append(("R6-isolated", line.strip(), v))
        if not (sH & ~sG == 0 and sH != sG):
            out["viol"].append(("R6-ssubset", line.strip(), v))
    # one random maximal reduction, every prefix checked
    cur = list(adj)
    while True:
        sv = step_vertices(cur)
        if not sv:
            break
        cur = sp_step(cur, rng.choice(sv))
        out["seq"] += 1
        sH = support(cur)
        removed = sG & ~sH
        if not le_graph(isolate_set(adj, removed), cur):
            out["viol"].append(("SUB", line.strip()))
        pwH = vs_cache(cur)
        if not (pw <= pwH + bin(removed).count("1")):
            out["viol"].append(("SEQ", line.strip(), pw, pwH, removed))
        if not (pw + bin(sH).count("1") <= pwH + bin(sG).count("1")):
            out["viol"].append(("SEQ2", line.strip(), pw, pwH))
    return out


_VS: dict[tuple[int, ...], int] = {}


def vs_cache(adj: list[int]) -> int:
    key = tuple(adj)
    if key not in _VS:
        if len(_VS) > 200000:
            _VS.clear()
        _VS[key] = vertex_separation_brute(adj) if adj else 0
    return _VS[key]


# --- Part C: pw(G) − pw(r(G)) at 10 ----------------------------------------------


def part_c_chunk(lines: list[str]) -> dict:
    hist: collections.Counter = collections.Counter()
    worst = (-1, None)
    reducible = 0
    for line in lines:
        n, adj = parse_g6(line)
        pw = vertex_separation_brute(adj)
        r, removed = reduce(adj)
        if removed:
            reducible += 1
        s = support(r)
        if s == 0:
            pwr = 0
        else:
            pwr = pathwidth_induced(r, s)
        gap = pw - pwr
        hist[gap] += 1
        if gap > worst[0]:
            worst = (gap, line.strip())
    return {"count": len(lines), "hist": dict(hist), "worst": worst, "reducible": reducible}


# --- driver --------------------------------------------------------------------


def geng(args: list[str]) -> list[str]:
    res = subprocess.run(["nauty-geng", "-q", *args], capture_output=True, text=True, check=True)
    return [ln for ln in res.stdout.splitlines() if ln.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n-a", type=int, default=12)
    ap.add_argument("--sanity-n", type=int, default=8)
    ap.add_argument("--max-n-b", type=int, default=8)
    ap.add_argument("--mod", type=int, default=120)
    ap.add_argument("--res", default="0,12,24,36,48,60,72,84,96,108")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-stop", action="store_true")
    ap.add_argument("--skip", default="", help="comma list of parts to skip: a,b,c")
    a = ap.parse_args()
    skip = set(a.skip.split(",")) if a.skip else set()
    log = open(HERE / "check.log", "w")
    summary: dict = {"parts": {}}

    def say(*s):
        msg = " ".join(str(x) for x in s)
        print(msg, flush=True)
        log.write(msg + "\n")
        log.flush()

    say(f"# item 11 brute force, {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    t0 = time.time()
    violations: list = []

    with Pool(a.workers) as pool:
        if "a" not in skip:
            say("## Part A: Fomin–Høie Lemma 4 on every graph of maximum degree ≤ 3")
            per_n = {}
            for n in range(1, a.max_n_a + 1):
                lines = geng(["-D3", str(n)])
                t = time.time()
                res = pool.starmap(part_a_graph, [(ln, a.sanity_n) for ln in lines], chunksize=64)
                need = max(r["need"] for r in res)
                arg = next(r["need_arg"] for r in res if r["need"] == need)
                need_int = max(r["need_int"] for r in res)
                viol = [v for r in res for v in r["viol"]]
                pairs = sum(r["pairs"] for r in res)
                sanity = sum(r["sanity"] for r in res)
                e0 = sum(1 for r in res if r["e0_ok"])
                l3 = log3(n)
                k = 0
                while 3 ** (k + 1) <= 2 * n + 1:
                    k += 1
                per_n[n] = {"graphs": len(lines), "pairs": pairs, "need": round(need, 4),
                            "need_arg": arg, "need_int": need_int,
                            "printed_term": round((2 / 3) * l3 + 1, 4),
                            "proof_term": round(l3 + 1, 4), "lean_term": k + 1,
                            "sanity_pairs": sanity, "e0_ok": e0,
                            "violations": len(viol), "seconds": round(time.time() - t, 1)}
                say(f"n={n:2d} graphs={len(lines):6d} (G,X)={pairs:9d} need={need:7.4f} "
                    f"(int {need_int}) printed={(2/3)*l3+1:6.3f} proof={l3+1:6.3f} lean={k+1} "
                    f"sanity={sanity} E0ok={e0}/{len(lines)} viol={len(viol)} "
                    f"[{time.time()-t:.1f}s] argmax={arg}")
                violations += viol
                if viol and not a.no_stop:
                    say("VIOLATION", viol[:5])
                    break
            summary["parts"]["A"] = per_n

        if "b" not in skip:
            say("## Part B: the StepBound.lean statements on every graph")
            per_n = {}
            for n in range(1, a.max_n_b + 1):
                lines = geng([str(n)])
                t = time.time()
                res = pool.map(part_b_graph, lines, chunksize=64)
                steps = sum(r["steps"] for r in res)
                seq = sum(r["seq"] for r in res)
                viol = [v for r in res for v in r["viol"]]
                per_n[n] = {"graphs": len(lines), "steps": steps, "sequence_prefixes": seq,
                            "violations": len(viol), "seconds": round(time.time() - t, 1)}
                say(f"n={n:2d} graphs={len(lines):6d} steps={steps:8d} prefixes={seq:8d} "
                    f"viol={len(viol)} [{time.time()-t:.1f}s]")
                violations += viol
                if viol and not a.no_stop:
                    say("VIOLATION", viol[:5])
                    break
            summary["parts"]["B"] = per_n

        if "c" not in skip:
            say(f"## Part C: pw(G) − pw(r(G)) on nauty-geng 10 r/{a.mod}, r in {a.res}")
            t = time.time()
            lines = []
            for r_ in a.res.split(","):
                lines += geng(["10", f"{int(r_)}/{a.mod}"])
            say(f"slices have {len(lines)} graphs")
            chunks = [lines[i:i + 2000] for i in range(0, len(lines), 2000)]
            hist: collections.Counter = collections.Counter()
            worst = (-1, None)
            count = 0
            reducible = 0
            for r in pool.imap_unordered(part_c_chunk, chunks):
                count += r["count"]
                reducible += r["reducible"]
                for k, v in r["hist"].items():
                    hist[int(k)] += v
                if r["worst"][0] > worst[0]:
                    worst = tuple(r["worst"])
            summary["parts"]["C"] = {"n": 10, "slice": f"{a.res} / {a.mod}", "graphs": count,
                                     "reducible": reducible,
                                     "hist": {str(k): hist[k] for k in sorted(hist)},
                                     "max_gap": worst[0], "max_arg": worst[1],
                                     "seconds": round(time.time() - t, 1)}
            say(f"graphs={count} reducible={reducible} hist={dict(sorted(hist.items()))} "
                f"max={worst} [{time.time()-t:.1f}s]")

    summary["violations"] = len(violations)
    summary["seconds"] = round(time.time() - t0, 1)
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    if violations:
        (HERE / "violations.txt").write_text("\n".join(map(str, violations)))
    say(f"# done: {len(violations)} violations, {time.time()-t0:.0f} s")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
