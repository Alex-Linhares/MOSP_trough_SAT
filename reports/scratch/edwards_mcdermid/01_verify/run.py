#!/usr/bin/env python3
"""loop0012 item 01: Edwards & McDermid (2015) Corollary 5.2 and Theorem 5.3
evaluated on every graph with a pathwidth on record, the cubic base case
measured, the Poisson check on the pilot. Nothing here solves a pathwidth
except the subset DP on cubic graphs of at most 16 vertices (stage `cubic`).

    nice -n 19 python3 reports/scratch/edwards_mcdermid/01_verify/run.py --workers 8
    ... --stages pilot,dataset,ensemble,cubic,tables

Outputs beside this file: pilot.csv, dataset.csv, ensemble.csv, cubic.csv,
tables.md, poisson_n120.png, run.log.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

REPO = Path("/home/al/dev/MOSP")
sys.path.insert(0, str(REPO))
HERE = Path(__file__).resolve().parent
LOG = HERE / "run.log"

import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from learning.edwards_mcdermid import (  # noqa: E402
    evaluate, from_edges, from_networkx, fomin_hoie_budget, g, poisson_value, reduce,
    components, is_cubic, degrees,
)

PROVED = {"refutation", "bound", "minor"}


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------- pilot ---

def _pilot_job(row: dict) -> dict:
    n, c, seed = int(row["n"]), float(row["c"]), int(row["seed"])
    G = nx.gnp_random_graph(n, c / n, seed=seed)
    assert G.number_of_edges() == int(row["m"]), ("edge count mismatch", row)
    proved = row["status"] in PROVED
    pw = int(row["width"]) if proved else None
    adj = from_networkx(G)
    out = evaluate(adj, pw)
    out.update({"source": "pilot", "id": f"n{n}_c{c:g}_s{row['sample']}", "c": c,
                "status": row["status"], "proved": proved,
                "lower": int(row["lower"]), "seed": seed})
    if not proved:
        # the `lower` column is a proved lower bound on pw: a lower bound on the deficit
        out["deficit_lower"] = out["lower"] - out["main_term"]
    return out


def stage_pilot(workers: int) -> None:
    df = pd.read_csv(REPO / "reports/scratch/gnp_pilot/results.csv")
    rows = df.to_dict("records")
    log(f"pilot: {len(rows)} rows, {sum(r['status'] in PROVED for r in rows)} proved")
    with Pool(workers) as pool:
        out = pool.map(_pilot_job, rows, chunksize=64)
    pd.DataFrame(out).to_csv(HERE / "pilot.csv", index=False)
    log("pilot: written")


# -------------------------------------------------------------- dataset ---

def _dataset_job(rec: dict) -> dict:
    n = int(rec["n"])
    adj = from_edges(n, rec["edges"])
    proved = rec["provenance"].startswith("certified")
    pw = int(rec["width"]) if proved else None
    out = evaluate(adj, pw)
    members = rec.get("members") or []
    coll = members[0].get("collection", "") if members else ""
    out.update({"source": "dataset", "id": rec["id"], "provenance": rec["provenance"],
                "proved": proved, "collection": coll, "upper": int(rec["width"])})
    if not proved:
        out["deficit_upper"] = out["upper"] - out["main_term"]
    assert out["m"] == int(rec["m"]), ("edge count mismatch", rec["id"])
    return out


def stage_dataset(workers: int) -> None:
    with gzip.open(REPO / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt") as f:
        recs = [json.loads(l) for l in f]
    recs = [r for r in recs if r["n"] > 0]
    log(f"dataset: {len(recs)} classes, {sum(r['provenance'].startswith('certified') for r in recs)} certified")
    with Pool(workers) as pool:
        out = pool.map(_dataset_job, recs, chunksize=32)
    pd.DataFrame(out).to_csv(HERE / "dataset.csv", index=False)
    log("dataset: written")


# ------------------------------------------------------------- ensemble ---

def _ensemble_job(row: dict) -> dict:
    from learning.ensemble import Cell, generate
    from customer_inter.customer_graph import build_customer_graph
    cell = Cell(row["generator"], int(row["n"]), int(row["m"]), float(row["param"]))
    inst = generate(cell, int(row["index"]))
    assert inst.name == row["instance_name"], ("name mismatch", row["instance_name"], inst.name)
    G = build_customer_graph(inst)
    assert G.number_of_edges() == int(row["g_edges"]), ("edge mismatch", row["instance_name"])
    adj = from_networkx(G)
    pw = int(row["optimum"]) - 1
    out = evaluate(adj, pw)
    out.update({"source": "ensemble", "id": row["instance_name"], "cell": row["cell"],
                "frame": row["frame"], "proved": True, "graph_cert": row["graph_cert"],
                "dup": bool(row["dup"])})
    return out


def stage_ensemble(workers: int) -> None:
    frames = []
    for name in ("results", "results_height", "results_ratio", "results_upward"):
        d = pd.read_csv(REPO / f"learning/data/ensemble/{name}.csv")
        d = d[d["certified"] == True].copy()  # noqa: E712
        d["frame"] = name
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df["dup"] = df.duplicated(subset=["cell", "graph_cert"], keep="first")
    log(f"ensemble: {len(df)} certified rows across 4 frames, {int(df['dup'].sum())} isomorphic repeats within their cell")
    rows = df.to_dict("records")
    with Pool(workers) as pool:
        out = pool.map(_ensemble_job, rows, chunksize=64)
    pd.DataFrame(out).to_csv(HERE / "ensemble.csv", index=False)
    log("ensemble: written")


# ---------------------------------------------------------------- cubic ---

def _parse_g6(line: str):
    b = line.strip().encode(); n = b[0] - 63; bits = []
    for ch in b[1:]:
        v = ch - 63; bits += [(v >> i) & 1 for i in range(5, -1, -1)]
    adj = [0] * n; k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i] |= 1 << j; adj[j] |= 1 << i
            k += 1
    return n, adj


def _cubic_job(args) -> dict:
    from learning.first_moment import vertex_separation_brute
    N, line = args
    n, adj = _parse_g6(line)
    assert n == N and is_cubic(adj)
    pw = vertex_separation_brute(adj)
    return {"source": "geng", "N": N, "g6": line.strip(), "pw": pw, "connected": True,
            "excess": pw - (N / 6 - 1 / 6)}


def stage_cubic(workers: int) -> None:
    jobs = []
    counts = {}
    for N in range(4, 17, 2):
        lines = subprocess.run(["nauty-geng", "-q", "-c", "-d3", "-D3", str(N)],
                               capture_output=True, text=True, check=True).stdout.splitlines()
        counts[N] = len(lines)
        jobs += [(N, l) for l in lines]
    log(f"cubic: geng connected cubic counts {counts} ({len(jobs)} graphs), subset DP")
    with Pool(workers) as pool:
        out = pool.map(_cubic_job, jobs, chunksize=16)
    # the dataset's cubic graphs
    with gzip.open(REPO / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt") as f:
        for l in f:
            r = json.loads(l)
            if r["n"] == 0:
                continue
            adj = from_edges(r["n"], r["edges"])
            if not is_cubic(adj):
                continue
            comps = components(adj)
            proved = r["provenance"].startswith("certified")
            out.append({"source": "dataset", "N": r["n"], "g6": r["id"], "pw": int(r["width"]),
                        "connected": len(comps) == 1, "n_components": len(comps),
                        "largest_component": max(c.bit_count() for c in comps),
                        "proved": proved, "provenance": r["provenance"],
                        "excess": int(r["width"]) - (r["n"] / 6 - 1 / 6)})
    # consistency check, no new solve: the dataset's cubic graphs at N ≤ 16 are
    # among the geng graphs; find them by isomorphism and compare the pathwidths
    geng_by_N = {}
    for r in out:
        if r["source"] == "geng":
            G = nx.from_graph6_bytes(r["g6"].encode())
            geng_by_N.setdefault(r["N"], []).append((nx.weisfeiler_lehman_graph_hash(G), G, r["pw"]))
    with gzip.open(REPO / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt") as f:
        recs = {json.loads(l)["id"]: json.loads(l) for l in f}
    for r in out:
        if r["source"] == "dataset" and r["N"] <= 16 and r["connected"]:
            G = nx.Graph(recs[r["g6"]]["edges"])
            h = nx.weisfeiler_lehman_graph_hash(G)
            match = [pw for (hh, H, pw) in geng_by_N[r["N"]] if hh == h and nx.is_isomorphic(G, H)]
            r["geng_pw"] = match[0] if match else None
            r["geng_agrees"] = (match[0] == r["pw"]) if match else None
    pd.DataFrame(out).to_csv(HERE / "cubic.csv", index=False)
    log(f"cubic: written ({len(out)} rows)")


# --------------------------------------------------------------- tables ---

def _md(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for r in df.astype(object).itertuples(index=False):
        cells = []
        for v in r:
            if isinstance(v, (float, np.floating)):
                cells.append("—" if math.isnan(v) else format(float(v), floatfmt))
            elif isinstance(v, (bool, np.bool_)):
                cells.append("yes" if v else "no")
            elif isinstance(v, (int, np.integer)):
                cells.append(str(int(v)))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _band(n: int) -> str:
    for hi in (10, 20, 40, 60, 100, 200, 500, 1000, 3000):
        if n <= hi:
            return f"≤{hi}"
    return ">3000"


BANDS = ["≤10", "≤20", "≤40", "≤60", "≤100", "≤200", "≤500", "≤1000", "≤3000"]


def stage_tables() -> None:
    pilot = pd.read_csv(HERE / "pilot.csv")
    dataset = pd.read_csv(HERE / "dataset.csv")
    ens = pd.read_csv(HERE / "ensemble.csv")
    cubic = pd.read_csv(HERE / "cubic.csv")
    out = []
    P = out.append

    proved = pd.concat([
        pilot[pilot.proved].assign(src="pilot"),
        dataset[dataset.proved].assign(src="dataset"),
        ens[(~ens.dup)].assign(src="ensemble"),
    ], ignore_index=True)
    proved["band"] = proved["n"].map(_band)

    # kill checks
    viol = proved[proved.pw > proved.main_term + proved.n.map(fomin_hoie_budget)]
    gt = proved[proved.main_term > proved.histogram_term + 1e-9]
    P("## Kill checks\n")
    P(f"- proved graphs: {len(proved)} (pilot {int((proved.src=='pilot').sum())}, dataset {int((proved.src=='dataset').sum())}, ensemble distinct {int((proved.src=='ensemble').sum())}; ensemble rows including isomorphic repeats within a cell: {len(ens)})")
    P(f"- `pw > main_term + τ_FH(n)`: **{len(viol)}** graphs")
    P(f"- `main_term > histogram_term`: **{len(gt)}** graphs")
    P(f"- `reduce` raised a degree: checked inside the module's tests and by `n_reduced`/degree monotonicity in `evaluate` (every surviving degree ≥ 3; see tests)")
    P("")

    # (d) deficit per source and n-band
    P("## (d) The deficit `pw − main_term`, per source and size band\n")
    rows = []
    for src, grp in proved.groupby("src"):
        for band in BANDS:
            g_ = grp[grp.band == band]
            if len(g_) == 0:
                continue
            rows.append({"source": src, "n band": band, "graphs": len(g_),
                         "max": g_.deficit.max(), "p99": g_.deficit.quantile(0.99),
                         "median": g_.deficit.median(), "share deficit ≤ 0": (g_.deficit <= 0).mean(),
                         "max deficit_hist": g_.deficit_hist.max(),
                         "median main/pw": (g_.main_term / g_.pw.clip(lower=1)).median()})
    P(_md(pd.DataFrame(rows)))
    P("")
    P("Per source, all sizes:\n")
    rows = []
    for src, grp in proved.groupby("src"):
        rows.append({"source": src, "graphs": len(grp), "n range": f"{grp.n.min()}–{grp.n.max()}",
                     "max deficit": grp.deficit.max(), "p99": grp.deficit.quantile(0.99),
                     "median": grp.deficit.median(), "share ≤ 0": (grp.deficit <= 0).mean(),
                     "max deficit_hist": grp.deficit_hist.max(), "share deficit_hist ≤ 0": (grp.deficit_hist <= 0).mean(),
                     "mean (hist − main)": (grp.histogram_term - grp.main_term).mean(),
                     "max (hist − main)": (grp.histogram_term - grp.main_term).max()})
    P(_md(pd.DataFrame(rows)))
    P("")
    P("Split by whether the graph reduces to empty (`n_reduced = 0`: series-parallel, main term 0, the deficit *is* `pw`, the paper's `O(log n)` term) or not; and, among the rest, whether the reduced graph is cubic (where the deficit is the cubic base case's):\n")
    rows = []
    proved["kind"] = np.where(proved.n_reduced == 0, "reduces to empty", np.where(proved.reduced_is_cubic == True, "r(G) cubic", "r(G) non-cubic"))  # noqa: E712
    for (src, kind), grp in proved.groupby(["src", "kind"]):
        arg = grp.loc[grp.deficit.idxmax()]
        rows.append({"source": src, "kind": kind, "graphs": len(grp), "n range": f"{grp.n.min()}–{grp.n.max()}",
                     "max deficit": grp.deficit.max(), "at": f"{arg.id} (|V| = {int(arg.n)}, pw = {int(arg.pw)})",
                     "p99": grp.deficit.quantile(0.99), "median": grp.deficit.median(), "share ≤ 0": (grp.deficit <= 0).mean()})
    P(_md(pd.DataFrame(rows)))
    sp = proved[proved.n_reduced == 0]
    P(f"\nOn the {len(sp)} graphs that reduce to empty, `pw` against `log₃ n`: max of `pw − log₃ n` = {(sp.pw - np.log2(sp.n.clip(lower=1)) / np.log2(3)).max():.3f}, max `pw` = {int(sp.pw.max())} (at n = {int(sp.loc[sp.pw.idxmax()].n)}); this is the measured shape of the reduction lemma's term at these sizes, not its constant.\n")
    worst = proved.sort_values("deficit", ascending=False).head(12)[["src", "id", "n", "m", "pw", "main_term", "histogram_term", "deficit", "n_reduced", "components"]]
    P("The twelve largest deficits on record:\n")
    P(_md(worst))
    P("")

    # B(n) and τ_FH
    P("## (d) The budget the record needs, `B(n) = max{deficit : |V| ≤ n}`, beside Fomin–Høie's explicit `τ_FH(n)`\n")
    rows = []
    for n in (10, 20, 40, 60, 100, 200, 500, 1000, 2916):
        sub = proved[proved.n <= n]
        if len(sub) == 0:
            continue
        arg = sub.loc[sub.deficit.idxmax()]
        nz = sub[sub.n_reduced > 0]
        rows.append({"n": n, "graphs with |V| ≤ n": len(sub), "B(n)": sub.deficit.max(),
                     "attained by": f"{arg.src}:{arg.id} (|V| = {int(arg.n)}, pw = {int(arg.pw)})",
                     "B(n) over r(G) ≠ ∅": nz.deficit.max(),
                     "B(n)/n": sub.deficit.max() / n,
                     "τ_FH(n)": fomin_hoie_budget(n), "τ_FH(n)/n": fomin_hoie_budget(n) / n})
    P(_md(pd.DataFrame(rows)))
    P("")
    # unproved rows
    up = pilot[~pilot.proved]
    P(f"Unproved pilot rows (`status = upper`, {len(up)} graphs at n = {up.n.min()}–{up.n.max()}): the proved `lower` column gives `lower − main_term` with max {up.deficit_lower.max():.3f}, median {up.deficit_lower.median():.3f}; these are lower bounds on the deficit and are not in `B(n)`.")
    sol = dataset[~dataset.proved]
    P(f"Dataset `solution` rows ({len(sol)} classes, n = {sol.n.min()}–{sol.n.max()}): `upper − main_term` max {sol.deficit_upper.max():.3f}, median {sol.deficit_upper.median():.3f}; upper bounds only, not in `B(n)`.")
    P("")

    # (e) cubic
    P("## (e) The cubic base case measured: `pw − (N/6 − 1/6)`\n")
    geng = cubic[cubic.source == "geng"]
    rows = []
    for N, grp in geng.groupby("N"):
        rows.append({"N": N, "connected cubic graphs": len(grp), "pw min": grp.pw.min(), "pw max": grp.pw.max(),
                     "max excess": grp.excess.max(), "N/6 − 1/6": N / 6 - 1 / 6,
                     "graphs at max": int((grp.excess == grp.excess.max()).sum())})
    P(_md(pd.DataFrame(rows)))
    cmax = geng.excess.max()
    P(f"\nSmallest `c` with `pw ≤ N/6 − 1/6 + c` on every connected cubic graph to 16 vertices (exhaustive, {len(geng)} graphs): **c = {cmax:.4f}** = {cmax} (attained at N = {sorted(geng[geng.excess == cmax].N.unique().tolist())}).")
    dcub = cubic[cubic.source == "dataset"].copy()
    dcub["proved"] = dcub.proved == True  # noqa: E712
    dcub["connected"] = dcub.connected == True  # noqa: E712
    P(f"\nThe dataset's cubic graphs: {len(dcub)} classes ({int(dcub.proved.sum())} certified, {int((~dcub.proved).sum())} `solution`), N = {dcub.N.min()}–{dcub.N.max()}; connected: {int(dcub.connected.sum())}.\n")
    P(_md(dcub.sort_values("N")[["g6", "N", "pw", "n_components", "provenance", "excess", "geng_pw", "geng_agrees"]].astype({"n_components": int})))
    xc = dcub[dcub.N <= 16]
    P(f"\nConsistency check, no new solve: the {len(xc)} dataset cubic graphs at N ≤ 16 were matched by isomorphism to the exhaustive geng sweep; matched {int(xc.geng_pw.notna().sum())}, pathwidths agree on {int((xc.geng_agrees == True).sum())}, disagree on {int((xc.geng_agrees == False).sum())}.")
    dc = dcub[dcub.proved & dcub.connected]
    P(f"\nOn the {len(dc)} certified connected ones (N = {dc.N.min()}–{dc.N.max()}): max excess **{dc.excess.max():.4f}** (at {dc.loc[dc.excess.idxmax()].g6}, N = {int(dc.loc[dc.excess.idxmax()].N)}); so the smallest `c` is {max(cmax, dc.excess.max()):.4f}, measured to N = 16 exhaustively and on {len(dc)} certified connected cubic graphs to N = {dc.N.max()}.")
    P("")

    # (f) Poisson
    P("## (f) The Poisson evaluation on the pilot, `n = 60–120`, `c ∈ {3, 4, 6, 8, 10}` (all rows, proved or not)\n")
    rows = []
    for (n, c), grp in pilot[pilot.n.isin([60, 70, 80, 90, 100, 120]) & pilot.c.isin([3, 4, 6, 8, 10])].groupby(["n", "c"]):
        pr = grp[grp.proved]
        rows.append({"n": n, "c": c, "rows": len(grp), "proved": len(pr),
                     "poisson": poisson_value(c),
                     "hist/n mean": (grp.histogram_term / grp.n).mean(), "hist/n sd": (grp.histogram_term / grp.n).std(),
                     "main/n mean": (grp.main_term / grp.n).mean(), "main/n sd": (grp.main_term / grp.n).std(),
                     "gain (hist − main)/n": ((grp.histogram_term - grp.main_term) / grp.n).mean(),
                     "pw/n (proved)": (pr.pw / pr.n).mean() if len(pr) else float("nan"),
                     "pw/main (proved)": (pr.pw / pr.main_term).mean() if len(pr) else float("nan")})
    P(_md(pd.DataFrame(rows), ".4f"))
    P("")
    # the §7(e)-style table over the whole pilot
    P("The survey §7(e)-style column over every pilot cell (proved rows only; `main/n` over all rows):\n")
    rows = []
    for (n, c), grp in pilot.groupby(["n", "c"]):
        pr = grp[grp.proved]
        rows.append({"n": n, "c": c, "proved": len(pr), "pw/n": (pr.pw / pr.n).mean() if len(pr) else float("nan"),
                     "main/n": (grp.main_term / grp.n).mean(), "hist/n": (grp.histogram_term / grp.n).mean(),
                     "poisson": poisson_value(c),
                     "ratio pw/main": (pr.pw / pr.main_term.replace(0, np.nan)).mean() if len(pr) else float("nan"),
                     "max deficit": pr.deficit.max() if len(pr) else float("nan")})
    P(_md(pd.DataFrame(rows), ".3f"))
    P("")

    # (g) Theorem 5.3
    P("## (g) Theorem 5.3's average-degree form, where it applies (connected, or `d̄ ≥ 5`)\n")
    rows = []
    app = proved[proved.avg_applies]
    for src, grp in app.groupby("src"):
        rows.append({"source": src, "graphs where it applies": len(grp), "connected": int(grp.connected.sum()),
                     "d̄ ≥ 5": int((grp.avg_degree >= 5).sum()),
                     "max deficit_avg": grp.deficit_avg.max(), "median deficit_avg": grp.deficit_avg.median(),
                     "share deficit_avg ≤ 0": (grp.deficit_avg <= 0).mean(),
                     "main_term > g(d̄)n": int(grp.main_gt_avg.sum()),
                     "median (avg − main)": (grp.avg_term - grp.main_term).median()})
    P(_md(pd.DataFrame(rows)))
    bad = app[app.main_gt_avg]
    if len(bad):
        P(f"\nGraphs with `main_term > g(d̄) n` where the averaging lemma says none: {len(bad)}; the first ten:\n")
        P(_md(bad.head(10)[["src", "id", "n", "m", "pw", "avg_degree", "main_term", "avg_term", "connected"]]))
    # the averaging lemma where it does not apply
    nap = proved[~proved.avg_applies & proved.avg_term.notna()]
    P(f"\nWhere Theorem 5.3 does not apply (disconnected with `d̄ < 5`, `d̄ ≥ 2`; {len(nap)} graphs): `main_term > g(d̄) n` on {int(nap.main_gt_avg.sum())} of them.")
    P("")
    (HERE / "tables.md").write_text("\n".join(out) + "\n")
    log("tables: written tables.md")
    _figure(pilot)


def _figure(pilot: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sub = pilot[(pilot.n == 120)]
    cs = sorted(sub.c.unique())
    hist = [(sub[sub.c == c].histogram_term / 120).mean() for c in cs]
    hsd = [(sub[sub.c == c].histogram_term / 120).std() for c in cs]
    main = [(sub[sub.c == c].main_term / 120).mean() for c in cs]
    msd = [(sub[sub.c == c].main_term / 120).std() for c in cs]
    pois = [poisson_value(c) for c in cs]
    pr = sub[sub.proved]
    pwn = [(pr[pr.c == c].pw / 120).mean() if (pr.c == c).any() else np.nan for c in cs]
    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=160)
    ax.set_facecolor("#fcfcfb"); fig.patch.set_facecolor("#fcfcfb")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#d9d8d3"); ax.spines[sp].set_linewidth(1)
    ax.grid(True, color="#e8e7e2", linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    series = [("Σ_d g(d) n_d / n (unreduced, mean ± sd)", hist, hsd, "#2a78d6"),
              ("Σ_{r(G)} g / n (reduced, mean ± sd)", main, msd, "#eb6834"),
              ("Poisson(c) value", pois, None, "#1baf7a")]
    for label, ys, sd, col in series:
        ax.plot(cs, ys, color=col, linewidth=2, marker="o", markersize=5, solid_joinstyle="round", solid_capstyle="round", label=label, markeredgecolor="#fcfcfb", markeredgewidth=1)
        if sd is not None:
            ax.fill_between(cs, np.array(ys) - np.array(sd), np.array(ys) + np.array(sd), color=col, alpha=0.15, linewidth=0)
    ax.plot(cs, pwn, color="#52514e", linewidth=0, marker="s", markersize=5, label="pw / n (proved rows, mean)")
    ax.set_xlabel("c   (G(n, c/n), n = 120)", color="#52514e")
    ax.set_ylabel("per vertex", color="#52514e")
    ax.tick_params(colors="#52514e")
    ax.legend(frameon=False, fontsize=8, loc="upper left", labelcolor="#0b0b0b")
    fig.tight_layout()
    fig.savefig(HERE / "poisson_n120.png")
    log("tables: figure poisson_n120.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--stages", default="pilot,dataset,ensemble,cubic,tables")
    a = ap.parse_args()
    stages = a.stages.split(",")
    log(f"start: stages={stages} workers={a.workers} load={os.getloadavg()}")
    t0 = time.time()
    for s in stages:
        t = time.time()
        {"pilot": lambda: stage_pilot(a.workers), "dataset": lambda: stage_dataset(a.workers),
         "ensemble": lambda: stage_ensemble(a.workers), "cubic": lambda: stage_cubic(a.workers),
         "tables": stage_tables}[s]()
        log(f"stage {s}: {time.time() - t:.1f} s")
    log(f"done in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
