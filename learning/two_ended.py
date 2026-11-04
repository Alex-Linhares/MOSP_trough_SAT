"""Two-ended search: the state lattice of a refutation, forward and backward.

A closing order `c_1 … c_n` of the customers is feasible for "MOSP ≤ k"
exactly when every prefix `S_t = {c_1 … c_t}` satisfies `|N(S_t) ∖ S_t| ≤ k − 1`
(`satisfiability/customer_search.py`: closing `c` from `S` costs
`|N[S ∪ c] ∖ S| = |N(S ∪ c) ∖ (S ∪ c)| + 1`). So "MOSP ≤ k" is reachability
from `∅` to `V` inside the family `F_k = {S : |N(S) ∖ S| ≤ k − 1}` by single
additions. Reversing the production sequence maps closing orders to closing
orders of the same graph (the opening order reversed), so it gives the same
search; the genuinely different direction is building the order from its
**end**: states are suffixes `T = V ∖ S`, walked from `V` by single removals
under the same membership test, `|∂_in(T)| ≤ k − 1`.

This module enumerates both frontiers exactly and rule-free: `R_f(i)`, the
sets of size `i` reachable from `∅` inside `F_k`, and `R_b(i)`, those from
which `V` is reachable. A refutation at `k` is `R_f(i) = ∅` for some `i`
(the forward wall `i_f`), equivalently `R_b(i) = ∅` for some `i` (the
backward wall `i_b`), equivalently `R_f(i) ∩ R_b(i) = ∅` at every `i`. The
forward search's work is `Σ_{i < i_f} |R_f(i)|`, the backward's
`Σ_{i > i_b} |R_b(i)|`, and a meet at level `i` costs
`Σ_{j ≤ i} |R_f(j)| + Σ_{j ≥ i} |R_b(j)|`. The checkpoint anatomy
(`reports/checkpoint_relaxation.md` §5, §7) says the forward search's states
peak at `0.42 n` while the obstruction sits at `0.5–0.7 n`; this measures
whether the other end, or a meet, pays — in states, which is what a search
with a frontier store would hold.

Free moves (`N[v] ⊆ N[S]`) are a dominance the forward search applies; the
counts here are without any rule on either side, so the two directions are
compared like with like. `forward_closed(i)` counts the forward states with
no free move available, the ones the rule-based search can actually visit.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from learning.checkpoint_bound import OUT, pilot_population
from learning.obstruction_ledger import adjacency_from_matrix


def forward_layers(adj: list[int], k: int, cap: int) -> tuple[list[int], list[int], bool]:
    """`|R_f(i)|` for i = 0..n (stops at the first empty layer), the count of
    free-closed states per layer, and whether a layer exceeded `cap`."""
    n = len(adj)
    full = (1 << n) - 1
    bound = k - 1
    closed_nb = [adj[v] | (1 << v) for v in range(n)]
    layer: dict[int, int] = {0: 0}       # S -> N[S]
    sizes, closed_counts = [1], [1]
    for i in range(n):
        nxt: dict[int, int] = {}
        for S, NS in layer.items():
            bits = full & ~S
            while bits:
                bit = bits & -bits
                bits ^= bit
                v = bit.bit_length() - 1
                S2 = S | bit
                NS2 = NS | closed_nb[v]
                if (NS2 & ~S2).bit_count() <= bound and S2 not in nxt:
                    nxt[S2] = NS2
                    if len(nxt) > cap:
                        return sizes, closed_counts, True
        if not nxt:
            sizes.append(0)
            closed_counts.append(0)
            return sizes, closed_counts, False
        free_closed = 0
        for S, NS in nxt.items():
            ok = True
            bits = full & ~S
            while bits:
                bit = bits & -bits
                bits ^= bit
                if closed_nb[bit.bit_length() - 1] & ~NS == 0:
                    ok = False
                    break
            free_closed += ok
        sizes.append(len(nxt))
        closed_counts.append(free_closed)
        layer = nxt
    return sizes, closed_counts, False


def backward_layers(adj: list[int], k: int, cap: int) -> tuple[list[int], bool]:
    """`|R_b(i)|` for i = n down to the first empty layer (listed from n
    downward): sets `S` of size `i` from which `V` is reachable inside `F_k`.
    Walked from `S = V` by removing the customer closed last; the prefix that
    remains must satisfy `|N(S') ∖ S'| ≤ k − 1`. Membership needs, per vertex,
    how many of its neighbours are still in `S` (`cnt`), kept as a byte
    vector per state and updated for all candidates at once."""
    n = len(adj)
    full = (1 << n) - 1
    bound = k - 1
    A = np.zeros((n, n), dtype=np.int16)
    for v in range(n):
        for u in range(n):
            if adj[v] >> u & 1:
                A[v, u] = 1
    deg = A.sum(axis=1).astype(np.int16)
    layer: dict[int, np.ndarray] = {full: deg.copy()}     # S -> cnt[u] = |N(u) ∩ S|
    sizes = [1]
    idx = np.arange(n)
    for i in range(n, 0, -1):
        nxt: dict[int, np.ndarray] = {}
        for S, cnt in layer.items():
            members = np.array([v for v in range(n) if S >> v & 1], dtype=np.int64)
            # removing v: cnt' = cnt - A[v]; boundary = {u in S \ v : cnt'[u] > 0}
            C = cnt[None, :] - A[members]                       # (|S|, n)
            inS = np.zeros(n, dtype=bool)
            inS[members] = True
            pos = (C > 0) & ~inS[None, :]                       # outside S' and adjacent to it
            rows = np.arange(len(members))
            pos[rows, members] = C[rows, members] > 0          # v itself is outside S' now
            bsz = pos.sum(axis=1)
            for j, v in enumerate(members):
                if bsz[j] <= bound:
                    S2 = S & ~(1 << int(v))
                    if S2 not in nxt:
                        nxt[S2] = C[j]
                        if len(nxt) > cap:
                            return sizes, True
        if not nxt:
            sizes.append(0)
            return sizes, False
        sizes.append(len(nxt))
        layer = nxt
    return sizes, False


def profile(matrix, k: int, cap: int) -> dict:
    adj = adjacency_from_matrix(np.asarray(matrix, dtype=int))
    n = len(adj)
    t0 = time.monotonic()
    f, fc, f_cens = forward_layers(adj, k, cap)
    tf = time.monotonic() - t0
    t0 = time.monotonic()
    b, b_cens = backward_layers(adj, k, cap)
    tb = time.monotonic() - t0
    # align: R_f[i] for i = 0..len-1 ; R_b listed from n downward: R_b[n - j] = b[j]
    Rf = {i: v for i, v in enumerate(f)}
    Rb = {n - j: v for j, v in enumerate(b)}
    out = {"n": n, "k": k, "cap": cap, "forward_censored": f_cens, "backward_censored": b_cens,
           "forward_seconds": round(tf, 2), "backward_seconds": round(tb, 2),
           "Rf": json.dumps(f), "Rf_free_closed": json.dumps(fc), "Rb": json.dumps(b)}
    if not f_cens:
        out["i_f"] = len(f) - 1                       # first empty forward layer
        out["forward_work"] = sum(f)
        out["forward_work_closed"] = sum(fc)
        out["forward_peak"] = max(f)
        out["forward_peak_i"] = int(np.argmax(f))
    if not b_cens:
        out["i_b"] = n - (len(b) - 1)                 # first empty backward layer (from the top)
        out["backward_work"] = sum(b)
        out["backward_peak"] = max(b)
        out["backward_peak_i"] = n - int(np.argmax(b))
    if not f_cens and not b_cens:
        # a meet at level i: forward layers 0..i and backward layers n..i
        best = None
        for i in range(0, n + 1):
            wf = sum(v for j, v in Rf.items() if j <= i)
            wb = sum(v for j, v in Rb.items() if j >= i)
            if best is None or wf + wb < best[0]:
                best = (wf + wb, i)
        out["meet_work"], out["meet_i"] = best
    return out


def _init():
    os.nice(19)


def _job(args):
    name, matrix, optimum, cap = args
    try:
        r = profile(matrix, optimum - 1, cap)
    except Exception as exc:  # noqa: BLE001
        r = {"error": str(exc)}
    r.update(instance_name=name, optimum=optimum)
    return r


def run(workers: int, n_max: int, cap: int, out_dir: Path, names: list[str] | None = None) -> None:
    from learning.obstruction_ledger import corpus_instances

    out_dir.mkdir(parents=True, exist_ok=True)
    pop = pilot_population(n_max)
    if names:
        pop = pop[pop.instance_name.isin(names)]
    found = corpus_instances()
    jobs = [(r.instance_name, found[r.instance_name][1].matrix, int(r.optimum), cap) for r in pop.itertuples()]
    jobs.sort(key=lambda j: -j[1].shape[0])
    rows = []
    t0 = time.monotonic()
    print(f"{time.strftime('%F %T')} two-ended: {len(jobs)} instances, cap {cap}, {workers} workers", flush=True)
    with Pool(workers, initializer=_init) as pool:
        for r in pool.imap_unordered(_job, jobs):
            rows.append(r)
            print(f"{time.strftime('%T')} {len(rows)}/{len(jobs)} {r['instance_name'][:28]:28} n={r.get('n')} k={r.get('k')} "
                  f"fwd wall {r.get('i_f')} work {r.get('forward_work')} (closed {r.get('forward_work_closed')}) peak@{r.get('forward_peak_i')} "
                  f"| bwd wall {r.get('i_b')} work {r.get('backward_work')} peak@{r.get('backward_peak_i')} "
                  f"| meet {r.get('meet_work')}@{r.get('meet_i')} | cens f={r.get('forward_censored')} b={r.get('backward_censored')} "
                  f"{r.get('forward_seconds')}+{r.get('backward_seconds')}s {r.get('error', '')}", flush=True)
            pd.DataFrame(rows).to_csv(out_dir / "two_ended.csv", index=False)
    print(f"{time.strftime('%F %T')} two-ended done: {len(rows)} rows in {time.monotonic() - t0:.0f} s", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--n-max", type=int, default=50)
    ap.add_argument("--cap", type=int, default=3_000_000)
    ap.add_argument("--out", type=Path, default=OUT / "two_ended")
    ap.add_argument("--names", nargs="*", default=None)
    a = ap.parse_args()
    run(a.workers, a.n_max, a.cap, a.out, a.names)


if __name__ == "__main__":
    main()
