"""loop0010 item 06: the forest regime on paper -- the statements of
`reports/excess_phase_diagram.md` §6 and their brute-force checks.

Every statement §6 calls a theorem is checked here before it is called one
(`CLAUDE.md`, "Lessons that cost sessions": two earlier `sorry`s hid false
statements). The exact pathwidths come from the C program
`pathwidth_solver/cli/pathwidth` (through `learning.block_trees.run_pathwidth_one`)
and from item 03's CSVs; nothing goes through the Python pathwidth solver and
nothing writes to `solutions/`.

The statements (`G_M` the MOSP graph, `B` the customer-pattern incidence graph,
`omega` the largest pattern, `tb(N)` the least `k` with `N <= (5 * 3^k - 3) / 2`):

* **F1 (blow-up).** For *every* instance, forest or not,
  `pw(G_M) <= omega * (pw(B) + 1) - 1`  (`f1_bound`); when `B` is a forest,
  `pw(B) <= tb(n + m)` (`TreeBound.lean`), so
  `MOSP(M) <= omega * (tb(n + m) + 1)` (`f1_log_bound` is the pathwidth form).
* **Lemma P (two-sided pendant bound).** If a graph has a clique `R` and `q`
  cliques `Q_1..Q_q` with `|Q_i| >= t` and `Q_i ∩ R = {v_i}` for distinct `v_i`,
  then `pw >= t + ceil(q / 2) - 2`  (`pendant_lower_bound` is its best value
  over the patterns of an instance, floored at `omega - 1`).
* **F2 (depth one, exact).** `K_s` with pendant copies of `K_t` at `q` of its
  vertices (one or more per vertex, `1 <= q <= s`) has
  `pw = max(s - 1, t + ceil(q / 2) - 2)`  (`f2_value`; `clique_with_pendants`
  builds the instance). `CT(s, 1, b)` is the case `t = s`, `q = s`:
  `ceil(3s / 2) - 2`, item 03's measured value.
* **F3 (the branch lemma on `CT(s, h, 2)`).** For `s >= 3`:
  `pw(CT(s, h, 2)) >= ceil(3s / 2) - 2` for `h >= 1` and
  `>= s + ceil((s - 1) / 2) + h - 3` for `h >= 2`  (`branch_lower_bound_ct`).

Checks (`run`): item 03's record (clique trees, caterpillars, random block
trees, the forests on record) against F1, F1', F2 and F3; a fresh grid of
`clique_with_pendants(s, t, q, b)` against F2 and Lemma P; random small
instances that are *not* forests against F1 and Lemma P.

    python -m learning.excess --stage forest_check [--workers 8]
"""
from __future__ import annotations

import math
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from learning.block_trees import (
    clique_tree,
    graph6,
    incidence_graph,
    is_incidence_forest,
    largest_pattern,
    mosp_graph,
    run_pathwidth_one,
    tree_bound,
    vertex_separation,
)

ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = ROOT / "reports" / "scratch" / "forest_regime"
OUT_DIR = ROOT / "reports" / "scratch" / "forest_check"

Patterns = list[list[int]]


# ----------------------------------------------------------------------------
# the statements
# ----------------------------------------------------------------------------


def f1_bound(omega: int, pw_b: int) -> int:
    """F1: `omega * (pw(B) + 1) - 1`, an upper bound on `pw(G_M)` for every instance."""
    return omega * (pw_b + 1) - 1


def f1_log_bound(omega: int, n_plus_m: int) -> int:
    """F1': `omega * (tb(n + m) + 1) - 1`, an upper bound on `pw(G_M)` when `B` is a forest;
    `tb(N) = floor(log_3((6N + 3) / 5))` for `N >= 1`."""
    return omega * (tree_bound(n_plus_m) + 1) - 1


def log3_form(n_plus_m: int) -> int:
    """`floor(log_3((6N + 3) / 5))`, computed in integers: the largest `k` with `5 * 3^k <= 6N + 3`."""
    k = 0
    while 5 * 3 ** (k + 1) <= 6 * n_plus_m + 3:
        k += 1
    return k


def f2_value(s: int, t: int, q: int) -> int:
    """F2: the pathwidth of `K_s` with pendant copies of `K_t` at `q` of its vertices
    (`1 <= q <= s`; for `q = 0` the clique alone, `s - 1`)."""
    if not (0 <= q <= s) or s < 1 or t < 1:
        raise ValueError("needs 1 <= s, 1 <= t, 0 <= q <= s")
    if q == 0:
        return s - 1
    return max(s - 1, t + math.ceil(q / 2) - 2)


def clique_with_pendants(s: int, t: int, q: int, b: int = 1) -> Patterns:
    """The instance of F2: pattern `0` is `K_s` on customers `0..s-1`; customers
    `0..q-1` each carry `b` pendant patterns of size `t` (the hub plus `t - 1` new
    customers). `s + q * b * (t - 1)` customers, `1 + q * b` patterns, a forest incidence."""
    if not (0 <= q <= s) or s < 1 or t < 1 or b < 0:
        raise ValueError("needs 1 <= s, 1 <= t, 0 <= q <= s, 0 <= b")
    patterns: Patterns = [list(range(s))]
    n = s
    for v in range(q):
        for _ in range(b):
            patterns.append([v] + list(range(n, n + t - 1)))
            n += t - 1
    return patterns


def pendant_lower_bound(patterns: Patterns) -> int:
    """Lemma P over an instance: for every pattern `R`, the patterns meeting `R` in
    exactly one customer, the largest one per customer, sorted by size; the best
    `t_q + ceil(q / 2) - 2` over the `q` largest (`t_q` the smallest of them);
    floored at `omega - 1`. A lower bound on `pw(G_M)` for every instance."""
    sets = [frozenset(p) for p in patterns]
    best = max((len(p) for p in patterns), default=1) - 1
    for i, R in enumerate(sets):
        per_customer: dict[int, int] = {}
        for j, Q in enumerate(sets):
            if j == i:
                continue
            meet = Q & R
            if len(meet) == 1:
                (v,) = meet
                per_customer[v] = max(per_customer.get(v, 0), len(Q))
        sizes = sorted(per_customer.values(), reverse=True)
        for q in range(1, len(sizes) + 1):
            best = max(best, sizes[q - 1] + math.ceil(q / 2) - 2)
    return best


def branch_lower_bound_ct(s: int, h: int) -> int:
    """F3: the lower bound on `pw(CT(s, h, 2))` from F2 at the root (`h >= 1`) and the
    branch lemma down the family `D(s, h)` (`h >= 2`, `s >= 3`); `s - 1` otherwise."""
    if s < 2 or h < 0:
        raise ValueError("needs s >= 2, h >= 0")
    best = s - 1
    if h >= 1:
        best = max(best, math.ceil(3 * s / 2) - 2)
    if h >= 2 and s >= 3:
        best = max(best, s + math.ceil((s - 1) / 2) + h - 3)
    return best


# ----------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------


def _exact(row, value_col: str, status_col: str) -> bool:
    """A row's value is exact unless the C program censored it (`upper`); item 03's
    `fit.py` resolution of one censored incidence tree by the ternary-subtree bound is
    re-applied here for the clique trees."""
    return str(row[status_col]) != "upper"


def check_record(record_dir: Path = RECORD_DIR) -> tuple[pd.DataFrame, dict]:
    """Item 03's record against F1, F1', F2 and F3. Returns the per-row table and a
    summary. Censored exact values are reported apart: a censored `pw` is an interval
    `[lower, upper]`, consistent with an upper bound iff `lower <=` it; a censored `pw_B`
    is only an upper bound on `pw(B)` and the F1 check is skipped there."""
    frames = []
    for name, family in (("ct_values.csv", "clique tree (grid)"), ("ct_ext_values.csv", "clique tree (extension)"),
                         ("caterpillar_values.csv", "caterpillar of cliques"),
                         ("random_block_trees.csv", "random block tree"), ("record_forests.csv", "forest on record")):
        path = record_dir / name
        if not path.exists():
            continue
        f = pd.read_csv(path)
        f["family"] = family
        frames.append(f)
    rec = pd.concat(frames, ignore_index=True)
    if "status" not in rec:
        rec["status"] = "bound"
    rec["status"] = rec["status"].fillna("bound")  # record forests: certified optima
    if "lower" not in rec:
        rec["lower"] = np.nan
    # item 03 resolved one censored incidence tree by the ternary-subtree bound (fit.py): re-apply
    if "s" in rec:
        from learning.block_trees import ternary_subtree_height
        for i, r in rec[(rec.status_B == "upper") & rec["s"].notna()].iterrows():
            P, _ = clique_tree(int(r.s), int(r.h), int(r.b))
            if ternary_subtree_height(incidence_graph(P)) == int(r.pw_B):
                rec.loc[i, "status_B"] = "upper = ternary subtree lower bound"
    rec["N_B"] = rec["N_B"].astype(int)
    rec["pw_exact"] = rec["status"] != "upper"
    rec["pwB_exact"] = rec["status_B"] != "upper"
    rec["F1"] = [f1_bound(int(o), int(p)) for o, p in zip(rec.omega, rec.pw_B)]
    rec["F1_log"] = [f1_log_bound(int(o), int(N)) for o, N in zip(rec.omega, rec.N_B)]
    rec["tb"] = [tree_bound(int(N)) for N in rec.N_B]
    rec["log3_form"] = [log3_form(int(N)) for N in rec.N_B]
    # the pw value to test: exact -> pw; censored -> its proved lower bound (a bound is violated only if the
    # proved lower bound exceeds it)
    rec["pw_test"] = np.where(rec.pw_exact, rec.pw, rec["lower"].fillna(rec.pw))
    rec["F1_ok"] = np.where(rec.pwB_exact, rec.pw_test <= rec.F1, True)
    rec["F1_checked"] = rec.pwB_exact
    rec["F1_log_ok"] = rec.pw_test <= rec.F1_log
    rec["pwB_le_tb"] = np.where(rec.pwB_exact, rec.pw_B <= rec.tb, True)  # a censored pw(B) is an upper bound: not checked
    rec["tb_eq_log3"] = rec.tb == rec.log3_form
    rec["F1_slack"] = np.where(rec.pw_exact & rec.pwB_exact, rec.F1 - rec.pw, np.nan)
    # F2 on the depth-one clique trees and the caterpillars (every clique has q = s one-point neighbours)
    f2 = np.full(len(rec), np.nan)
    ct1 = rec["family"].str.startswith("clique tree") & (rec.get("h", pd.Series(np.nan, index=rec.index)) == 1)
    for i in rec.index[ct1]:
        f2[i] = f2_value(int(rec.loc[i, "s"]), int(rec.loc[i, "s"]), int(rec.loc[i, "s"]))
    cat = rec["family"] == "caterpillar of cliques"
    for i in rec.index[cat]:
        s = int(rec.loc[i, "s"])
        f2[i] = f2_value(s, s, s)
    rec["F2"] = f2
    rec["F2_ok"] = np.where(np.isnan(f2), True,
                            np.where(rec.pw_exact, rec.pw == f2, (rec["lower"].fillna(0) <= f2) & (f2 <= rec.pw)))
    # F3 on CT(s, h, 2)
    f3 = np.full(len(rec), np.nan)
    ct2 = rec["family"].str.startswith("clique tree") & (rec.get("b", pd.Series(np.nan, index=rec.index)) == 2)
    for i in rec.index[ct2]:
        f3[i] = branch_lower_bound_ct(int(rec.loc[i, "s"]), int(rec.loc[i, "h"]))
    rec["F3"] = f3
    rec["F3_ok"] = np.where(np.isnan(f3), True, f3 <= rec.pw)  # pw is exact or an upper bound: either way >= truth >= F3
    rec["F3_gap_to_F1"] = np.where(np.isnan(f3) | ~rec.pwB_exact, np.nan, rec.F1 - f3)

    summary = {}
    for fam, g in rec.groupby("family", sort=False):
        ex = g[g.pw_exact & g.pwB_exact]
        summary[fam] = {
            "rows": len(g), "pw exact": int(g.pw_exact.sum()), "pw(B) exact": int(g.pwB_exact.sum()),
            "F1 checked": int(g.F1_checked.sum()), "F1 violations": int((~g.F1_ok & g.F1_checked).sum()),
            "F1 exact": int((ex.F1 == ex.pw).sum()),
            "F1 slack min/mean/max": (float(ex.F1_slack.min()), float(ex.F1_slack.mean()), float(ex.F1_slack.max())) if len(ex) else None,
            "F1' violations": int((~g.F1_log_ok).sum()),
            "pw(B) <= tb(N_B) violations": int((~g.pwB_le_tb).sum()),
            "tb == log3 form on every row": bool(g.tb_eq_log3.all()),
            "F2 rows": int(g.F2.notna().sum()), "F2 violations": int((~g.F2_ok).sum()),
            "F3 rows": int(g.F3.notna().sum()), "F3 violations": int((~g.F3_ok).sum()),
        }
    return rec, summary


def _solve(patterns: Patterns, timeout: float, n: int | None = None) -> tuple[dict, dict]:
    """Exact `pw(G_M)` and `pw(B)` by the C program, layouts re-checked."""
    n = 1 + max(v for p in patterns for v in p) if n is None else n
    G = mosp_graph(patterns, n)
    B = incidence_graph(patterns, n)
    rg = run_pathwidth_one(graph6(G), timeout)
    rb = run_pathwidth_one(graph6(B), timeout)
    if rg["layout"]:
        assert vertex_separation(G, rg["layout"]) == rg["width"]
    if rb["layout"]:
        assert vertex_separation(B, rb["layout"]) == rb["width"]
    return rg, rb


def f2_grid_jobs(s_max: int = 7, t_max: int = 7, bs: tuple[int, ...] = (1, 2, 3)) -> list[tuple[int, int, int, int]]:
    return [(s, t, q, b) for s in range(2, s_max + 1) for t in range(2, t_max + 1) for q in range(0, s + 1) for b in bs]


def _f2_job(args) -> dict:
    s, t, q, b, timeout = args
    P = clique_with_pendants(s, t, q, b)
    n = s + q * b * (t - 1)
    rg, rb = _solve(P, timeout)
    omega = largest_pattern(P)
    return {"s": s, "t": t, "q": q, "b": b, "n": n, "m": len(P), "omega": omega,
            "pw": rg["width"], "status": rg["status"], "lower": rg.get("lower", np.nan), "nodes": rg.get("nodes", np.nan),
            "seconds": rg.get("seconds", np.nan), "pw_B": rb["width"], "status_B": rb["status"],
            "F2": f2_value(s, t, q), "lemmaP": pendant_lower_bound(P), "F1": f1_bound(omega, rb["width"]),
            "F1_log": f1_log_bound(omega, n + len(P))}


def check_f2_grid(workers: int, timeout: float = 120.0, jobs=None) -> pd.DataFrame:
    """Fresh graphs of F2's family: `K_s` with `b` pendant `K_t` at `q` of its vertices,
    `s, t <= 6`, every `q <= s`, `b in {1, 2}`: `pw` by the C program against `f2_value`,
    Lemma P (must be `<= pw`) and F1 (must be `>= pw`)."""
    jobs = f2_grid_jobs() if jobs is None else jobs
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        rows = list(pool.map(_f2_job, [(s, t, q, b, timeout) for s, t, q, b in jobs]))
    f = pd.DataFrame(rows)
    f["exact"] = f.status != "upper"
    f["F2_ok"] = np.where(f.exact, f.pw == f.F2, (f["lower"] <= f.F2) & (f.F2 <= f.pw))
    f["lemmaP_ok"] = f.lemmaP <= f.pw  # pw exact or an upper bound of the truth: lemma P must sit below the truth,
    f.loc[~f.exact, "lemmaP_ok"] = f.loc[~f.exact, "lemmaP"] <= f.loc[~f.exact, "lower"]  # so test it against the proved floor
    f["F1_ok"] = np.where(f.exact, f.pw <= f.F1, f["lower"] <= f.F1)
    f["F1_log_ok"] = np.where(f.exact, f.pw <= f.F1_log, f["lower"] <= f.F1_log)
    return f


def random_instance(rng: np.random.Generator, n: int, m: int, kind: str, param: float) -> Patterns:
    """A small random instance: `kind = "bernoulli"` draws each entry with probability
    `param`; `kind = "fixed"` gives every pattern exactly `param` customers. Empty
    patterns are re-drawn to one customer; customers may be empty (isolated in both graphs)."""
    patterns: Patterns = []
    for _ in range(m):
        if kind == "fixed":
            size = int(param)
        else:
            size = int(rng.binomial(n, param))
        size = max(1, min(n, size))
        patterns.append(sorted(int(v) for v in rng.choice(n, size=size, replace=False)))
    return patterns


def random_jobs(count_per_cell: int = 25, seed0: int = 606000) -> list[tuple]:
    cells = [(n, m, kind, p) for n in (6, 8, 10, 12) for m in (4, 6, 8, 10, 12)
             for kind, p in (("bernoulli", 0.3), ("bernoulli", 0.5), ("fixed", 2), ("fixed", 3))]
    jobs = []
    for ci, (n, m, kind, p) in enumerate(cells):
        for i in range(count_per_cell):
            jobs.append((n, m, kind, p, seed0 + 100 * ci + i))
    return jobs


def _random_job(args) -> dict:
    n, m, kind, p, seed, timeout = args
    rng = np.random.default_rng(seed)
    P = random_instance(rng, n, m, kind, p)
    rg, rb = _solve(P, timeout, n)  # customers no pattern covers stay isolated in both graphs
    omega = largest_pattern(P)
    forest = is_incidence_forest(P, n)
    return {"n": n, "m": len(P), "kind": kind, "param": p, "seed": seed, "n_ones": sum(len(q) for q in P),
            "omega": omega, "forest": forest, "pw": rg["width"], "status": rg["status"], "pw_B": rb["width"],
            "status_B": rb["status"], "F1": f1_bound(omega, rb["width"]), "F1_log": f1_log_bound(omega, n + len(P)),
            "lemmaP": pendant_lower_bound(P)}


def check_random(workers: int, timeout: float = 60.0, jobs=None) -> pd.DataFrame:
    """Random small instances, most of them not forests: F1 (every instance), F1' (the
    forests only), Lemma P (every instance) against the C program's exact values."""
    jobs = random_jobs() if jobs is None else jobs
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        rows = list(pool.map(_random_job, [(*j, timeout) for j in jobs]))
    f = pd.DataFrame(rows)
    f["exact"] = (f.status != "upper") & (f.status_B != "upper")
    f["F1_ok"] = f.pw <= f.F1
    f["F1_log_ok"] = np.where(f.forest, f.pw <= f.F1_log, True)
    f["lemmaP_ok"] = f.lemmaP <= f.pw
    f["F1_slack"] = f.F1 - f.pw
    return f


def default_workers(cap: int = 8) -> int:
    load = os.getloadavg()[0]
    return min(cap, 4) if load > 24 else cap


def run(workers: int | None = None, out_dir: Path = OUT_DIR, record_dir: Path = RECORD_DIR,
        f2_timeout: float = 120.0, random_timeout: float = 60.0) -> str:
    """All three checks; CSVs and the log under `out_dir`; returns the markdown summary."""
    workers = default_workers() if workers is None else workers
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# forest_check -- {time.strftime('%Y-%m-%d %H:%M')} -- workers {workers}, load {os.getloadavg()[0]:.1f}", ""]
    t0 = time.time()
    rec, summary = check_record(record_dir)
    rec.to_csv(out_dir / "record_check.csv", index=False)
    lines.append("## Item 03's record against F1, F1', F2, F3\n")
    lines.append("| family | rows | pw exact | pw(B) exact | F1 checked | F1 violations | F1 exact | F1 slack min / mean / max "
                 "| F1' violations | pw(B) <= tb violations | tb = log3 form | F2 rows | F2 violations | F3 rows | F3 violations |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for fam, s in summary.items():
        sl = s["F1 slack min/mean/max"]
        sl_txt = f"{sl[0]:.0f} / {sl[1]:.1f} / {sl[2]:.0f}" if sl else "-"
        v_log = s["F1' violations"]
        lines.append(f"| {fam} | {s['rows']} | {s['pw exact']} | {s['pw(B) exact']} | {s['F1 checked']} | {s['F1 violations']} "
                     f"| {s['F1 exact']} | {sl_txt} | {v_log} | {s['pw(B) <= tb(N_B) violations']} "
                     f"| {'yes' if s['tb == log3 form on every row'] else 'NO'} | {s['F2 rows']} | {s['F2 violations']} "
                     f"| {s['F3 rows']} | {s['F3 violations']} |")
    lines.append("")
    # the F3 table on CT(s, h, 2)
    ct2 = rec[rec.F3.notna()].sort_values(["s", "h"])
    if len(ct2):
        lines.append("### F3 on CT(s, h, 2): the branch-lemma floor, the value, the blow-up bound\n")
        lines.append("| s | h | n | F3 (lower bound) | pw (C program) | status | F1 = omega (pw(B) + 1) - 1 | pw(B) | F1' |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for r in ct2.itertuples():
            pw_txt = f"{int(r.pw)}" if r.pw_exact else f"[{int(r.lower)}, {int(r.pw)}]"
            f1_txt = f"{int(r.F1)}" if r.pwB_exact else f"<= {int(r.F1)} (pw(B) censored)"
            lines.append(f"| {int(r.s)} | {int(r.h)} | {int(r.n)} | {int(r.F3)} | {pw_txt} | {r.status} | {f1_txt} | {int(r.pw_B)} | {int(r.F1_log)} |")
        lines.append("")
    # the F2 rows of the record
    f2rows = rec[rec.F2.notna()]
    lines.append(f"### F2 on the record: {len(f2rows)} rows (CT(s, 1, b) and every caterpillar), "
                 f"{int((~f2rows.F2_ok).sum())} disagreements\n")
    t1 = time.time()
    lines.append(f"(record read and scored in {t1 - t0:.1f} s)\n")

    grid = check_f2_grid(workers, f2_timeout)
    grid.to_csv(out_dir / "f2_grid.csv", index=False)
    t2 = time.time()
    ex = grid[grid.exact]
    lines.append("## F2's family by the C program: K_s with b pendant K_t at q vertices\n")
    lines.append(f"{len(grid)} graphs (s, t = 2..{int(grid.s.max())}, q = 0..s, b = {', '.join(str(b) for b in sorted(grid.b.unique()))}; "
                 f"n <= {int(grid.n.max())}), {int(grid.exact.sum())} exact, "
                 f"{int((~grid.exact).sum())} censored at {f2_timeout:.0f} s; {t2 - t1:.0f} s wall on {workers} workers; "
                 f"{grid.seconds.sum() / 3600:.3f} core-hours in the MOSP-graph solves.\n")
    lines.append(f"- F2 = pw on {int((ex.pw == ex.F2).sum())} of {len(ex)} exact graphs; disagreements {int((~grid.F2_ok).sum())} "
                 f"(censored rows count as consistent iff lower <= F2 <= upper).")
    lines.append(f"- Lemma P <= pw: violations {int((~grid.lemmaP_ok).sum())}; Lemma P = pw on {int((ex.lemmaP == ex.pw).sum())} of {len(ex)}.")
    lines.append(f"- F1 >= pw: violations {int((~grid.F1_ok).sum())}; F1' >= pw: violations {int((~grid.F1_log_ok).sum())}.")
    worst = grid[~grid.F2_ok]
    if len(worst):
        lines.append("\n**F2 DISAGREEMENTS**\n")
        lines.append(worst.to_markdown(index=False))
    lines.append("")
    lines.append("### F2's grid, exact values (rows s, columns q; cells `pw` for t = s, b = 1)\n")
    lines.append("")
    piv = ex[(ex.t == ex.s) & (ex.b == 1)].pivot(index="s", columns="q", values="pw")
    lines.append(piv.to_markdown())
    lines.append("")

    rnd = check_random(workers, random_timeout)
    rnd.to_csv(out_dir / "random_check.csv", index=False)
    t3 = time.time()
    lines.append("## Random small instances (not forests, mostly): F1, F1' and Lemma P\n")
    lines.append(f"{len(rnd)} instances, n = {int(rnd.n.min())}..{int(rnd.n.max())}, m = 4..12, Bernoulli p = 0.3 / 0.5 and fixed size 2 / 3, 25 per cell "
                 f"(seeds in `random_check.csv`); {int(rnd.forest.sum())} forests; {int(rnd.exact.sum())} with both pathwidths exact; "
                 f"{t3 - t2:.0f} s wall.\n")
    lines.append(f"- F1 >= pw: violations {int((~rnd.F1_ok).sum())}; F1 = pw on {int((rnd.F1 == rnd.pw).sum())}; "
                 f"slack min / median / max {int(rnd.F1_slack.min())} / {float(rnd.F1_slack.median()):.1f} / {int(rnd.F1_slack.max())}.")
    lines.append(f"- F1' >= pw on the {int(rnd.forest.sum())} forests: violations {int((~rnd.F1_log_ok).sum())}.")
    lines.append(f"- Lemma P <= pw: violations {int((~rnd.lemmaP_ok).sum())}; Lemma P = pw on {int((rnd.lemmaP == rnd.pw).sum())} "
                 f"of {len(rnd)} (the floor omega - 1 alone is exact on {int((rnd.omega - 1 == rnd.pw).sum())}).")
    lines.append("")
    total_viol = (sum(s["F1 violations"] + s["F1' violations"] + s["pw(B) <= tb(N_B) violations"] + s["F2 violations"]
                      + s["F3 violations"] for s in summary.values())
                  + int((~grid.F2_ok).sum()) + int((~grid.lemmaP_ok).sum()) + int((~grid.F1_ok).sum()) + int((~grid.F1_log_ok).sum())
                  + int((~rnd.F1_ok).sum()) + int((~rnd.F1_log_ok).sum()) + int((~rnd.lemmaP_ok).sum()))
    lines.append(f"## Verdict: {total_viol} violations in all. {'No statement is withdrawn.' if total_viol == 0 else 'A STATEMENT IS FALSE: see above.'}")
    lines.append(f"\n(total {t3 - t0:.0f} s wall)")
    text = "\n".join(lines)
    (out_dir / "forest_check.log").write_text(text + "\n")
    return text


# ----------------------------------------------------------------------------
# Lemma P on a graph (loop0010 item 13): the evaluation `PendantCliques.lean` licenses
# ----------------------------------------------------------------------------

def pendant_graph_bound(graph, max_r: int = 500, max_q: int = 5000, max_cliques: int = 50000,
                        deadline: float | None = None) -> tuple[int, dict]:
    """Lemma P evaluated on a graph: `R` over the largest maximal cliques (at most
    `max_r`), the pendant cliques over the largest maximal cliques `Q'` (at most
    `max_q`), each cut down to `Q' \\ (R \\ {v})` for every `v ∈ Q' ∩ R` — the largest
    sub-clique of `Q'` meeting `R` exactly in `v` — the largest such per `v`, sorted;
    the best `t_q + ceil(q / 2) - 2` over the `q` largest. Returns the bound in
    **pathwidth units** (`optimum - 1`), floored at `ω - 1`, with a dict saying
    whether any cap was hit (`censored`: the evaluation is then over a subset of the
    cliques, still a valid bound by `pathwidth_ge_of_pendant_cliques`). No part of
    this is used by the solver."""
    import itertools
    import time

    import networkx as nx

    nodes = list(graph.nodes())
    index = {v: i for i, v in enumerate(nodes)}
    cliques: list[int] = []
    censored = False
    for clique in itertools.islice(nx.find_cliques(graph), max_cliques + 1):
        if len(cliques) >= max_cliques:
            censored = True
            break
        mask = 0
        for v in clique:
            mask |= 1 << index[v]
        cliques.append(mask)
        if deadline is not None and time.monotonic() > deadline:
            censored = True
            break
    cliques.sort(key=lambda m: -bin(m).count("1"))
    sizes = {m: bin(m).count("1") for m in cliques}
    omega = max(sizes.values(), default=1)
    best = omega - 1
    rs = cliques[:max_r]
    qs = cliques[:max_q]
    censored = censored or len(rs) < len(cliques) or len(qs) < len(cliques)
    for R in rs:
        per_vertex: dict[int, int] = {}
        for Q in qs:
            meet = Q & R
            if meet == 0 or Q == R:
                continue
            size = sizes[Q] - bin(meet).count("1") + 1
            if size < 2:
                continue
            while meet:
                low = meet & -meet
                if per_vertex.get(low, 0) < size:
                    per_vertex[low] = size
                meet ^= low
        if not per_vertex:
            continue
        ordered = sorted(per_vertex.values(), reverse=True)
        for q, t in enumerate(ordered, start=1):
            val = t + (q + 1) // 2 - 2
            if val > best:
                best = val
        if deadline is not None and time.monotonic() > deadline:
            censored = True
            break
    return best, {"censored": censored, "cliques": len(cliques), "omega": omega}


def pendant_candidate(graph, matrix, budget):
    """`learning.bound_harness` candidate: Lemma P in optimum units (`pathwidth + 1`)."""
    import time

    value, info = pendant_graph_bound(graph, deadline=time.monotonic() + budget.seconds)
    if info["censored"]:
        budget.exhausted = True
    return value + 1, {"censored_eval": info["censored"], "cliques": info["cliques"]}
