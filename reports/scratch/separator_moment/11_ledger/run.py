"""loop0011 item 11: the slack ledger — in stacks, what each count buys and what
is left, on certified instances (`reports/separator_moment.md` §11).

Every quantity is on the *pathwidth* scale (`pw = optimum − 1` on covers; the
proved width on the pilot graphs).  A floor at threshold `θ` is the largest `k`
with the count's bound on `P(pw ≤ k)` below `θ`, plus one (`learning.
separator_moment.floor_pw`; the record's `floors` is this plus one more, for
the optimum).  The ladder per instance is

    old pair → exact-size pair → {closed, flip | separator, closed} → Harper → pw,

where `Harper` is the vertex-isoperimetric bound under a level cap and a time
budget (a *lower* bound on the true Harper value, which is itself ≤ pw), so
`pw − Harper` is an *upper* bound on the necessary condition's slack and
`Harper − floor` a *lower* bound on the union bound's (§8.5 (b) of
`reports/excess_phase_diagram.md`).

Stages (`--stage covers|gnp|stats|draw`, all by default):
  covers  the 600 certified `(6, 1)` fixed-generator instances at `n = m = 30–75`
          whose Harper values are on record (`reports/scratch/structured_count/
          slack_6_1.csv`, read, never re-solved): sizes regenerated from the
          seeds (`learning.ensemble.generate`), the old pair floor, the
          exact-size pair floor, the closed-pair floor (NA bound, item 07) and the
          flip floor (item 07), at `< 1` and `< 0.01`.
  gnp     the pilot's `c = 10` cells at `n = 30, 40, 50, 60` (`reports/scratch/
          gnp_pilot/results.csv`, proved graphs only, regenerated from their
          seeds; the layout re-checked against the width): per cell the old and
          exact-size pair floors, the separator floor (item 05: `C(n, k)
          P_N(E_bip)`, exact) and the closed floor (item 06: `log_closed_count`);
          per graph Harper's bound (`harper_bound_graph`, `--max-t` levels,
          `--budget` seconds, censoring recorded).
  stats   per `n`, the quantiles of every consecutive difference of the ladder,
          the violation counts (a floor above `pw` at `< 0.01` is the stop
          condition of TASK.md), and where the slack sits.
  draw    the ladder figure (medians per `n`, gap to `pw`), PNG.

Outputs here: ledger_6_1.csv, ledger_gnp.csv, cells_gnp.csv, summary.csv,
ladder.png, run.log.

Regenerate: nice -n 19 python3 reports/scratch/separator_moment/11_ledger/run.py --workers 6
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from learning import separator_moment as sm  # noqa: E402
from learning.first_moment import floors as pair_floors, log_bound, lchoose  # noqa: E402

LN10 = math.log(10)
SLACK = "reports/scratch/structured_count/slack_6_1.csv"
PILOT = "reports/scratch/gnp_pilot/results.csv"
THRESH = {"lt1": 1.0, "lt001": 0.01}


def log(msg: str = "") -> None:
    print(msg, flush=True)
    with open(os.path.join(HERE, "run.log"), "a") as f:
        f.write(msg + "\n")


def write_csv(path: str, rows: list[dict]) -> None:
    fields = list(rows[0].keys())
    for r in rows[1:]:
        fields += [k for k in r if k not in fields]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def read_csv(path: str) -> list[dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ covers

def cover_task(args):
    frame, cell_text, index, name, rec = args
    from learning.ensemble import Cell, generate
    t0 = time.time()
    inst = generate(Cell(cell_text[0], cell_text[1], cell_text[2], cell_text[3]), index)
    assert inst.name == name, (inst.name, name)
    sizes = [int(s) for s in np.asarray(inst.matrix).sum(axis=0)]
    n = inst.n_customers
    assert n == int(rec["n"]) and inst.n_patterns == int(rec["m"])
    pw = int(rec["optimum"]) - 1
    old = {k: log_bound(n, sizes, k) for k in range(n)}
    xp = {k: sm.cover_log_pair_bound(n, k, sizes) for k in range(n)}
    o1, o2 = sm.floor_pw(old, 1.0), sm.floor_pw(old, 0.01)
    x1, x2 = sm.floor_pw(xp, 1.0), sm.floor_pw(xp, 0.01)
    # the record's floors (optimum scale) must be these plus one
    f_old = pair_floors(n, sizes)
    assert (o1 + 1, o2 + 1) == f_old == (int(rec["floor_old"]), int(rec["floor_old_001"])), (name, o1, o2, f_old, rec)
    assert (x1 + 1, x2 + 1) == (int(rec["floor_1"]), int(rec["floor_1_001"])), (name, x1, x2, rec)
    # closed and flip around the exact-size floors (each k is its own statement; the window holds the floors)
    ks = list(range(max(0, x2 - 5), min(n - 1, max(x1 + 7, pw + 1)) + 1))
    cl = {k: sm.closed_cover_log_bound(n, k, sizes, optimise=False) for k in ks}
    fl = {k: sm.flip_log_bound_fast(n, k, sizes)[0] for k in ks}
    c1, c2 = sm.floor_pw(cl, 1.0), sm.floor_pw(cl, 0.01)
    f1, f2 = sm.floor_pw(fl, 1.0), sm.floor_pw(fl, 0.01)
    harper = int(rec["harper"]) - 1          # the record's value is on the MOSP scale
    return {"frame": frame, "instance": name, "n": n, "m": inst.n_patterns, "pw": pw,
            "old_lt1": o1, "xpair_lt1": x1, "closed_lt1": c1, "flip_lt1": f1,
            "old_lt001": o2, "xpair_lt001": x2, "closed_lt001": c2, "flip_lt001": f2,
            "best_lt1": max(c1, f1, x1), "best_lt001": max(c2, f2, x2),
            "harper": harper, "harper_cap": int(rec["cap"]), "harper_complete": rec["complete"] == "True",
            "harper_secs": round(float(rec["secs"]), 1),
            "log10_old_at_pw": old[pw] / LN10, "log10_xpair_at_pw": xp[pw] / LN10,
            "log10_closed_at_pw": cl.get(pw, float("nan")) / LN10, "log10_flip_at_pw": fl.get(pw, float("nan")) / LN10,
            "k_scanned": f"{ks[0]}-{ks[-1]}", "seconds": round(time.time() - t0, 2)}


def stage_covers(workers: int) -> None:
    import pandas as pd
    log("== covers: the 600 certified (6, 1) instances with Harper on record ==")
    t0 = time.time()
    rec = {r["instance"]: r for r in read_csv(SLACK)}
    tasks = []
    for frame in ("results.csv", "results_upward.csv"):
        df = pd.read_csv(f"learning/data/ensemble/{frame}")
        sub = df[(df.generator == "fixed") & (df.param == 6) & (df.m == df.n) & (df.n >= 30)]
        assert sub.certified.all()
        for r in sub.itertuples():
            assert r.instance_name in rec and int(rec[r.instance_name]["optimum"]) == int(r.optimum)
            tasks.append((frame, (r.generator, int(r.n), int(r.m), float(r.param)), int(r.index), r.instance_name, rec[r.instance_name]))
    assert len(tasks) == len(rec) == 600, (len(tasks), len(rec))
    tasks.sort(key=lambda t: -t[1][1])
    with Pool(workers) as pool:
        rows = pool.map(cover_task, tasks, chunksize=2)
    rows.sort(key=lambda r: (r["n"], r["instance"]))
    write_csv(os.path.join(HERE, "ledger_6_1.csv"), rows)
    log(f"covers: {len(rows)} instances in {time.time() - t0:.0f} s wall ({sum(r['seconds'] for r in rows) / 3600:.2f} core-hours of bounds; Harper read from the record)")


# ------------------------------------------------------------------ gnp

def cell_task(args):
    n, c = args
    p = c / n
    t0 = time.time()
    lc = sm.log_connected(n, p)
    rows = []
    for k in range(n):
        N, t = sm.forced_sizes(n, k)
        lck = lchoose(n, k)
        rows.append({"n": n, "c": c, "k": k, "N": N, "t": t,
                     "logB_old": lchoose(n, t) + lchoose(n - t, t - 1) + t * (t - 1) * math.log1p(-p) if t >= 1 else math.inf,
                     "logB_xpair": lck + sm.log_product_bound(N, p, t),
                     "logB_sep": lck + sm.log_prob_bip(N, p, t, lc),
                     "logB_closed": sm.log_closed_count(n, k, p)})
    return n, c, rows, time.time() - t0


def harper_task(args):
    n, c, sample, seed, width, m, max_t, budget = args
    adj = sm.gnp_masks(n, c / n, seed)
    assert sum(popc(a) for a in adj) // 2 == m, (n, c, seed)
    hb = sm.harper_bound_graph(adj, max_t=max_t, time_budget=budget)
    return {"n": n, "c": c, "sample": sample, "seed": seed, "pw": width, "harper": hb.value, "harper_cap": hb.cap,
            "harper_levels": " ".join(map(str, hb.levels)), "harper_complete": hb.complete, "harper_secs": round(hb.seconds, 1)}


def popc(x: int) -> int:
    return bin(x).count("1")


def stage_gnp(workers: int, max_t: int, budget: float) -> None:
    log(f"== gnp: the pilot's c = 10 cells at n = 30–60, proved graphs; Harper with max_t {max_t}, budget {budget:.0f} s ==")
    t0 = time.time()
    pilot = [r for r in read_csv(PILOT) if float(r["c"]) == 10 and int(r["n"]) in (30, 40, 50, 60)]
    proved = [r for r in pilot if r["status"] != "upper"]
    # `status` is the proof type (bound / refutation / minor; `upper` = unproved), as item 05 read it
    log(f"  {len(pilot)} graphs in the four cells, {len(proved)} proved ({sum(1 for r in pilot if r['status'] == 'minor')} by a minor certificate)")
    # the layout on record has the width (both orientations tried: the C program's convention is not pinned here)
    bad = 0
    for r in proved:
        n = int(r["n"])
        adj = sm.gnp_masks(n, 10 / n, int(r["seed"]))
        lay = [int(x) for x in r["layout"].split()]
        vs = min(sm.layout_vertex_separation(adj, lay), sm.layout_vertex_separation(adj, lay[::-1]))
        if vs != int(r["width"]):
            bad += 1
    log(f"  layout check: {len(proved) - bad} of {len(proved)} layouts have the recorded width in one orientation, {bad} do not")
    with Pool(workers) as pool:
        cells = pool.map(cell_task, [(n, 10) for n in (30, 40, 50, 60)])
    cell_rows = []
    for n, c, rows, secs in cells:
        cell_rows.extend(rows)
    write_csv(os.path.join(HERE, "cells_gnp.csv"), cell_rows)
    log(f"  cell bounds: {len(cell_rows)} (n, k) rows in {sum(s for *_, s in cells):.0f} s")
    tasks = [(int(r["n"]), 10, int(r["sample"]), int(r["seed"]), int(r["width"]), int(r["m"]), max_t, budget) for r in proved]
    tasks.sort(key=lambda t: -t[0])
    with Pool(workers) as pool:
        rows = pool.map(harper_task, tasks, chunksize=1)
    by_cell = {}
    for r in cell_rows:
        by_cell.setdefault(int(r["n"]), {})[int(r["k"])] = r
    for r in rows:
        kb = by_cell[r["n"]]
        for key, lab in (("logB_old", "old"), ("logB_xpair", "xpair"), ("logB_sep", "sep"), ("logB_closed", "closed")):
            vals = {k: float(v[key]) for k, v in kb.items()}
            r[f"{lab}_lt1"] = sm.floor_pw(vals, 1.0)
            r[f"{lab}_lt001"] = sm.floor_pw(vals, 0.01)
            r[f"log10_{lab}_at_pw"] = vals[r["pw"]] / LN10
        r["best_lt1"] = max(r["sep_lt1"], r["closed_lt1"], r["xpair_lt1"])
        r["best_lt001"] = max(r["sep_lt001"], r["closed_lt001"], r["xpair_lt001"])
    rows.sort(key=lambda r: (r["n"], r["sample"]))
    write_csv(os.path.join(HERE, "ledger_gnp.csv"), rows)
    log(f"gnp: {len(rows)} graphs in {time.time() - t0:.0f} s wall ({sum(r['harper_secs'] for r in rows) / 3600:.2f} core-hours of Harper)")


# ------------------------------------------------------------------ stats

def q(vals, ps=(10, 50, 90)):
    return " / ".join(f"{np.percentile(vals, p):.0f}" for p in ps)


def ledger_stats(rows: list[dict], model: str, counts: list[tuple[str, str]], thr: str) -> list[dict]:
    """Per `n`: quantiles and means of the consecutive differences at threshold `thr`."""
    out = []
    ns = sorted({int(r["n"]) for r in rows})
    log(f"\n{model}, floors at < {THRESH[thr]} (pw scale; quantiles 10 / 50 / 90, mean in brackets)")
    header = "  n   N | " + " | ".join(f"{b}−{a}" for a, b in counts) + " | Harper−best | pw−Harper | pw−best | share union-bound | Harper≥best | Harper=pw | viol"
    log(header)
    for n in ns:
        g = [r for r in rows if int(r["n"]) == n]
        pw = np.array([int(r["pw"]) for r in g])
        best = np.array([int(r[f"best_{thr}"]) for r in g])
        harper = np.array([int(r["harper"]) for r in g])
        d = {"model": model, "thresh": THRESH[thr], "n": n, "N": len(g), "mean_pw": pw.mean(), "mean_harper": harper.mean()}
        cells = []
        for a, b in counts:
            diff = np.array([int(r[f"{b}_{thr}"]) - int(r[f"{a}_{thr}"]) for r in g])
            d[f"{b}_minus_{a}_mean"] = diff.mean()
            d[f"{b}_minus_{a}_q"] = q(diff)
            d[f"mean_{a}"] = np.mean([int(r[f"{a}_{thr}"]) for r in g])
            d[f"mean_{b}"] = np.mean([int(r[f"{b}_{thr}"]) for r in g])
            cells.append(f"{q(diff)} ({diff.mean():.2f})")
        hb, ph, pb = harper - best, pw - harper, pw - best
        share = hb.sum() / pb.sum() if pb.sum() else float("nan")
        d.update(harper_minus_best_mean=hb.mean(), harper_minus_best_q=q(hb), pw_minus_harper_mean=ph.mean(), pw_minus_harper_q=q(ph),
                 pw_minus_best_mean=pb.mean(), pw_minus_best_q=q(pb), share_union_bound=share,
                 harper_ge_best=int((hb >= 0).sum()), harper_eq_pw=int((ph == 0).sum()),
                 violations=int((best > pw).sum()), mean_best=best.mean(),
                 cap_min=min(int(r["harper_cap"]) for r in g), cap_median=float(np.median([int(r["harper_cap"]) for r in g])),
                 complete=sum(1 for r in g if str(r["harper_complete"]) == "True"),
                 harper_secs_mean=float(np.mean([float(r["harper_secs"]) for r in g])))
        log(f"{n:4d} {len(g):3d} | " + " | ".join(cells) + f" | {q(hb)} ({hb.mean():.2f}) | {q(ph)} ({ph.mean():.2f}) | {q(pb)} ({pb.mean():.2f}) | {share:.2f} | {d['harper_ge_best']} | {d['harper_eq_pw']} | {d['violations']}")
        out.append(d)
    return out


def stage_stats() -> None:
    log("\n== stats ==")
    cov = read_csv(os.path.join(HERE, "ledger_6_1.csv"))
    gnp = read_csv(os.path.join(HERE, "ledger_gnp.csv"))
    summary = []
    for thr in ("lt001", "lt1"):
        summary += ledger_stats(cov, "covers (6, 1), fixed generator, m = n", [("old", "xpair"), ("xpair", "closed"), ("xpair", "flip")], thr)
        summary += ledger_stats(gnp, "G(n, 10/n), pilot, proved", [("old", "xpair"), ("xpair", "sep"), ("xpair", "closed")], thr)
    write_csv(os.path.join(HERE, "summary.csv"), summary)
    # violations at both thresholds, every count
    log("\nviolations (floor > pw), by count and threshold:")
    for name, rows, keys in (("covers", cov, ("old", "xpair", "closed", "flip")), ("gnp", gnp, ("old", "xpair", "sep", "closed"))):
        for thr in ("lt1", "lt001"):
            v = {k: sum(1 for r in rows if int(r[f"{k}_{thr}"]) > int(r["pw"])) for k in keys}
            log(f"  {name} < {THRESH[thr]}: {v}")
    # Harper censoring
    log("\nHarper under the cap: covers (record, max_t 12, 60 s) and gnp (this item)")
    for name, rows in (("covers", cov), ("gnp", gnp)):
        for n in sorted({int(r["n"]) for r in rows}):
            g = [r for r in rows if int(r["n"]) == n]
            caps = [int(r["harper_cap"]) for r in g]
            t_forced = [math.ceil((int(r["n"]) - int(r["pw"])) / 2) for r in g]
            log(f"  {name} n={n}: cap min/median/max {min(caps)}/{np.median(caps):.0f}/{max(caps)}; forced t at pw: {min(t_forced)}–{max(t_forced)}; complete {sum(1 for r in g if str(r['harper_complete']) == 'True')}/{len(g)}; secs mean/max {np.mean([float(r['harper_secs']) for r in g]):.1f}/{max(float(r['harper_secs']) for r in g):.0f}")
    # per-cell floors on gnp (same for every graph in a cell) and the decades at pw
    log("\ngnp cells: floors (pw scale) at < 1 / < 0.01 and min/mean/max pw; log10 of each bound at k = min pw")
    cells = read_csv(os.path.join(HERE, "cells_gnp.csv"))
    for n in (30, 40, 50, 60):
        kb = {int(r["k"]): r for r in cells if int(r["n"]) == n}
        g = [int(r["pw"]) for r in gnp if int(r["n"]) == n]
        parts = []
        for key, lab in (("logB_old", "old"), ("logB_xpair", "xpair"), ("logB_sep", "sep"), ("logB_closed", "closed")):
            vals = {k: float(v[key]) for k, v in kb.items()}
            parts.append(f"{lab} {sm.floor_pw(vals, 1.0)}/{sm.floor_pw(vals, 0.01)} ({vals[min(g)] / LN10:+.2f})")
        log(f"  n={n}: " + "; ".join(parts) + f"; pw {min(g)}/{np.mean(g):.1f}/{max(g)}")
    # the decades at k = pw on covers (mean per n)
    log("\ncovers: mean log10 of each count's bound at k = pw (the instance's own pathwidth)")
    for n in sorted({int(r["n"]) for r in cov}):
        g = [r for r in cov if int(r["n"]) == n]
        log(f"  n={n}: old {np.mean([float(r['log10_old_at_pw']) for r in g]):+.2f}, xpair {np.mean([float(r['log10_xpair_at_pw']) for r in g]):+.2f}, "
            f"closed {np.nanmean([float(r['log10_closed_at_pw']) for r in g]):+.2f}, flip {np.nanmean([float(r['log10_flip_at_pw']) for r in g]):+.2f}")


# ------------------------------------------------------------------ draw

def stage_draw() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cov = read_csv(os.path.join(HERE, "ledger_6_1.csv"))
    gnp = read_csv(os.path.join(HERE, "ledger_gnp.csv"))
    # palette: reference categorical slots 1, 2, 3, 4, 7 (validated, see run.log)
    rungs_cov = [("old_lt001", "old pair floor", "#2a78d6"), ("xpair_lt001", "exact-size pair floor", "#eb6834"),
                 ("best_lt001", "best count (closed / flip)", "#1baf7a"), ("harper", "Harper (capped)", "#eda100"), ("pw", "pathwidth", "#6250d6")]
    rungs_gnp = [("old_lt001", "old pair floor", "#2a78d6"), ("xpair_lt001", "exact-size pair floor", "#eb6834"),
                 ("best_lt001", "best count (separator / closed)", "#1baf7a"), ("harper", "Harper (capped)", "#eda100"), ("pw", "pathwidth", "#6250d6")]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True)
    for ax, rows, rungs, title in ((axes[0], cov, rungs_cov, "random clique covers (6, 1), m = n, certified"),
                                   (axes[1], gnp, rungs_gnp, "G(n, 10/n), pilot graphs, proved")):
        ns = sorted({int(r["n"]) for r in rows})
        for i, n in enumerate(ns):
            g = [r for r in rows if int(r["n"]) == n]
            pw = np.array([int(r["pw"]) for r in g])
            meds = []
            for key, lab, col in rungs:
                gap = pw - np.array([int(r[key]) for r in g])
                meds.append(float(np.median(gap)))
            ax.plot([n, n], [max(meds), min(meds)], color="#c3c2b7", linewidth=1.5, zorder=1)
            offs = [-1.6, -0.8, 0.0, 0.8, 1.6]        # dodge: tied medians stay visible side by side
            for (key, lab, col), m, off in zip(rungs, meds, offs):
                ax.plot([n + off], [m], "o", color=col, markersize=8, markeredgecolor="#fcfcfb", markeredgewidth=1.2, zorder=3,
                        label=lab if i == 0 else None)
            if i == len(ns) - 1:
                # direct labels at the last n, pushed apart to at least 0.4 stacks
                order = sorted(range(len(rungs)), key=lambda j: meds[j])
                ys = [meds[j] for j in order]
                for a in range(1, len(ys)):
                    if ys[a] - ys[a - 1] < 0.4:
                        ys[a] = ys[a - 1] + 0.4
                for j, y in zip(order, ys):
                    ax.annotate(rungs[j][1], (n + 1.6, meds[j]), xytext=(n + 3.2, y), textcoords="data", fontsize=8,
                                color="#52514e", va="center", arrowprops=dict(arrowstyle="-", color="#c3c2b7", lw=0.6, shrinkA=0, shrinkB=3))
        ax.set_xlabel("n")
        ax.set_title(title, fontsize=9, color="#52514e", loc="left")
        ax.set_xticks(ns)
        ax.set_xlim(min(ns) - 3, max(ns) + 24)
        ax.grid(axis="y", color="#e8e7e3", linewidth=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#c3c2b7")
        ax.spines["bottom"].set_color("#c3c2b7")
    axes[0].set_ylabel("stacks below the pathwidth (median per n)")
    axes[0].invert_yaxis()
    axes[0].legend(loc="lower left", fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "ladder.png"), dpi=160)
    log("draw: ladder.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["all", "covers", "gnp", "stats", "draw"])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-t", type=int, default=16)
    ap.add_argument("--budget", type=float, default=60.0)
    a = ap.parse_args()
    if a.stage in ("all", "covers"):
        stage_covers(a.workers)
    if a.stage in ("all", "gnp"):
        stage_gnp(a.workers, a.max_t, a.budget)
    if a.stage in ("all", "stats"):
        stage_stats()
    if a.stage in ("all", "draw"):
        stage_draw()


if __name__ == "__main__":
    main()
