"""Tables for `paper2/solver_fix_cost.py` (loop0007 item 04).

    python -m paper2.solver_fix_cost --stage tables

Reads `paper2/data/solver_fix_cost_{mosp40,cs,cs125,pw}.csv`, whichever
exist, and writes `paper2/data/solver_fix_cost_tables.md`. Nodes are totals
over pairs where both settings finished; censored pairs are counted apart, and
there a node count is a lower bound.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / "data"
OUT = DATA / "solver_fix_cost_tables.md"
COUNTERS = ["filter_calls", "definite_prefilter", "definite_match_fail", "definite_fires",
            "definite_lost", "better_prefilter", "better_match_fail", "better_pruned"]
DONE = ("sat", "unsat")


def _md(frame: pd.DataFrame) -> str:
    return frame.to_markdown(index=False, floatfmt=".4g")


def _band(n: int) -> str:
    for hi in (10, 20, 30, 40, 50, 75, 100, 125):
        if n <= hi:
            return f"≤{hi}"
    return ">125"


def _wide(d: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    w = d.pivot_table(index=keys, columns="setting",
                      values=["status", "nodes", "seconds"], aggfunc="first")
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    return w.reset_index()


def cost_table(w: pd.DataFrame, group: str) -> pd.DataFrame:
    rows = []
    for g, x in w.groupby(group, sort=False):
        done = x.status_old.isin(DONE) & x.status_repaired.isin(DONE)
        f = x[done]
        ratio = (f.nodes_repaired.clip(lower=1) / f.nodes_old.clip(lower=1))
        rows.append({
            group: g, "pairs": len(x), "answers differ": int((done & (x.status_old != x.status_repaired)).sum()),
            "both finished": int(done.sum()),
            "censored (either)": int((~done).sum()),
            "nodes old": int(f.nodes_old.sum()), "nodes repaired": int(f.nodes_repaired.sum()),
            "total ratio": f.nodes_repaired.sum() / max(1, f.nodes_old.sum()),
            "pairs more": int((f.nodes_repaired > f.nodes_old).sum()),
            "pairs fewer": int((f.nodes_repaired < f.nodes_old).sum()),
            "max pair ratio": float(ratio.max()) if len(f) else np.nan,
            "min pair ratio": float(ratio.min()) if len(f) else np.nan,
            "s old": float(f.seconds_old.sum()), "s repaired": float(f.seconds_repaired.sum()),
        })
    return pd.DataFrame(rows)


def censored_table(w: pd.DataFrame) -> pd.DataFrame:
    c = w[~(w.status_old.isin(DONE) & w.status_repaired.isin(DONE))]
    if c.empty:
        return c
    out = c[["instance_name", "status_old", "nodes_old", "seconds_old",
             "status_repaired", "nodes_repaired", "seconds_repaired"]].copy()
    out["µs/node old"] = 1e6 * out.seconds_old / out.nodes_old.clip(lower=1)
    out["µs/node repaired"] = 1e6 * out.seconds_repaired / out.nodes_repaired.clip(lower=1)
    return out


def counter_table(d: pd.DataFrame, group: str) -> pd.DataFrame:
    rep = d[d.setting == "repaired"].copy()
    rep[COUNTERS] = rep[COUNTERS].apply(pd.to_numeric, errors="coerce")
    rows = []
    for g, x in rep.groupby(group, sort=False):
        s = x[COUNTERS].sum()
        rows.append({
            group: g, "instances": len(x), "filter calls": int(s.filter_calls),
            "definite: old test passes": int(s.definite_prefilter),
            "matching fails": int(s.definite_match_fail),
            "fail rate": s.definite_match_fail / max(1, s.definite_prefilter),
            "nodes where it no longer fires": int(s.definite_lost),
            "instances with a lost node": int((x.definite_lost > 0).sum()),
            "better: (r,q) premise 3+4": int(s.better_prefilter),
            "matching fails ": int(s.better_match_fail),
            "fail rate ": s.better_match_fail / max(1, s.better_prefilter),
        })
    return pd.DataFrame(rows)


def mosp_section(stage: str, title: str) -> list[str]:
    path = DATA / f"solver_fix_cost_{stage}.csv"
    if not path.exists():
        return []
    d = pd.read_csv(path)
    d["band"] = d.n.map(_band)
    d["class"] = d.instance_name.str.extract(r"^(Random-\d+-\d+-\d+)")[0].fillna(d.band)
    d = d.sort_values(["n", "m"])
    group = "band" if stage == "mosp40" else "class"
    lines = [f"## {title}", ""]
    for config, x in d.groupby("config", sort=False):
        w = _wide(x, ["instance_name", group])
        lines += [f"### Cost, configuration `{config}`", "", _md(cost_table(w, group)), ""]
        cens = censored_table(w)
        if len(cens):
            lines += [f"Censored pairs, `{config}` (node counts are lower bounds):", "", _md(cens), ""]
        lines += [f"### Rule counters, configuration `{config}`, repaired runs", "",
                  _md(counter_table(x, group)), ""]
    return lines


def pw_section() -> list[str]:
    path = DATA / "solver_fix_cost_pw.csv"
    if not path.exists():
        return []
    d = pd.read_csv(path)
    # A job writes its two rows together, and VSPLIB's tree set reuses file
    # stems across directories, so the pair is the row order, not the name.
    d["pair"] = np.arange(len(d)) // 2
    assert (d.groupby("pair").setting.nunique() == 2).all()
    w = d.pivot_table(index=["set", "name", "pair"], columns="setting",
                      values=["width", "proof", "nodes", "seconds"], aggfunc="first")
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    w = w.reset_index()
    rows = []
    for s, x in w.groupby("set", sort=False):
        proved = lambda p: p.isin(["refutation", "bound"])  # noqa: E731
        both = proved(x.proof_old) & proved(x.proof_repaired)
        f = x[both]
        rows.append({
            "set": s, "graphs": len(x), "both proved": int(both.sum()),
            "proved old only": int((proved(x.proof_old) & ~proved(x.proof_repaired)).sum()),
            "proved repaired only": int((~proved(x.proof_old) & proved(x.proof_repaired)).sum()),
            "proved widths differ": int((f.width_old != f.width_repaired).sum()),
            "nodes old": int(f.nodes_old.sum()), "nodes repaired": int(f.nodes_repaired.sum()),
            "total ratio": f.nodes_repaired.sum() / max(1, f.nodes_old.sum()),
            "pairs more": int((f.nodes_repaired > f.nodes_old).sum()),
            "pairs fewer": int((f.nodes_repaired < f.nodes_old).sum()),
            "s old": float(f.seconds_old.sum()), "s repaired": float(f.seconds_repaired.sum()),
            "unproved: width old>rep": int(((~both) & (x.width_old > x.width_repaired)).sum()),
            "unproved: width old<rep": int(((~both) & (x.width_old < x.width_repaired)).sum()),
        })
    lines = ["## The pathwidth solver: `solve(G, time_budget)`, both settings", "",
             _md(pd.DataFrame(rows)), ""]
    c = d.dropna(subset=["count_k"]).copy()
    if len(c):
        rows = []
        for s, x in c.groupby("set", sort=False):
            wc = x.pivot_table(index="pair", columns="setting", values=["count_nodes", "count_status"],
                               aggfunc="first")
            rep = x[x.setting == "repaired"]
            sm = rep[COUNTERS].sum()
            rows.append({
                "set": s, "graphs": len(rep),
                "answers differ": int((wc["count_status"]["old"] != wc["count_status"]["repaired"]).sum()),
                "nodes old": int(wc["count_nodes"]["old"].sum()),
                "nodes repaired": int(wc["count_nodes"]["repaired"].sum()),
                "definite: old test passes": int(sm.definite_prefilter),
                "matching fails": int(sm.definite_match_fail),
                "fail rate": sm.definite_match_fail / max(1, sm.definite_prefilter),
                "nodes where it no longer fires": int(sm.definite_lost),
                "graphs with a lost node": int((rep.definite_lost > 0).sum()),
            })
        lines += ["### Counter pass: refutation of the widest component's width − 1, as a MOSP "
                  "instance with one product per edge (components ≤ 128 vertices)", "",
                  _md(pd.DataFrame(rows)), ""]
    return lines


def overhead_section() -> list[str]:
    path = DATA / "solver_fix_cost_overhead.csv"
    if not path.exists():
        return []
    d = pd.read_csv(path)
    med = d.pivot_table(index="instance_name", columns="variant", values="us_per_node",
                        aggfunc="median")
    nodes = d.pivot_table(index="instance_name", columns="variant", values="nodes", aggfunc="first")
    out = pd.DataFrame({
        "instance": med.index,
        "nodes old": nodes["old"].astype(int).values,
        "nodes repaired": nodes["repaired"].astype(int).values,
        "µs/node old": med["old"].values,
        "µs/node repaired": med["repaired"].values,
        "µs/node pre-counter C": med["old, pre-counter C"].values,
        "repaired / old": (med["repaired"] / med["old"]).values,
        "old / pre-counter": (med["old"] / med["old, pre-counter C"]).values,
    })
    reps = int(d.rep.max()) + 1
    return ["## Per-node overhead under a fixed node cap", "",
            f"Median of {reps} repetitions, the three variants alternating; `csearch` "
            "configuration; refuting optimum − 1.", "", _md(out), ""]


def write_tables(out: Path = OUT) -> None:
    lines = ["# What the repair costs: tables (loop0007 item 04)", "",
             "Generated by `python -m paper2.solver_fix_cost --stage tables`. "
             "`old` = `repaired_rules=False`, `repaired` = `repaired_rules=True`. "
             "Nodes and seconds summed over pairs where both settings finished.", ""]
    lines += mosp_section("mosp40", "MOSP corpus at n ≤ 40, refuting optimum − 1")
    lines += mosp_section("cs", "Chu & Stuckey classes at 50–100, refuting optimum − 1")
    lines += mosp_section("cs125", "Chu & Stuckey 125 × 125, refuting optimum − 1 under a node cap")
    lines += overhead_section()
    lines += pw_section()
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    write_tables()
