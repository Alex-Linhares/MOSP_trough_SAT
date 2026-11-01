"""Lemma P scored on every certified corpus instance through `learning.bound_harness`
(loop0010 item 13; §14 item 3 of `reports/excess_phase_diagram.md`). Nothing is solved:
the harness reads certified optima and `lb_best` from the record and the exact or interval
treewidth from the invariants table; the candidate is `learning.forest_theorems.pendant_candidate`
(optimum units). Values to `harness_values.csv` beside this script; tables to stdout.

    nice -n 19 python reports/scratch/pendant_cliques/score.py --workers 8
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from learning import bound_harness as bh  # noqa: E402
from learning.forest_theorems import pendant_candidate  # noqa: E402

HERE = Path(__file__).resolve().parent
VALUES = HERE / "harness_values.csv"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--tables-only", action="store_true")
    args = ap.parse_args()
    bh.CANDIDATES["pendant"] = pendant_candidate
    bh.BUDGET_SECONDS["pendant"] = 10.0
    t0 = time.time()
    if not args.tables_only:
        bh.run_validity(args.workers, ("pendant",), out_csv=VALUES, sources=("corpus",), wall=args.wall)
    vals = pd.read_csv(VALUES)
    rows = bh.certified_rows()
    rows = rows[rows["source"] == "corpus"]
    f = rows.merge(vals[["instance_name", "source", "pendant", "pendant_censored_eval", "pendant_cliques",
                         "pendant_seconds", "omega"]], on=["instance_name", "source"], how="inner")
    parts = f["source_file"].astype(str).str.split("/")
    f["collection"] = parts.str[3].where(parts.str.len() > 3, parts.str[-1]).str.replace(r"\.(txt|mosp)$", "", regex=True)
    f.loc[parts.str[2] == "MOSP_Instances", "collection"] = "MOSP_Instances/" + parts.str[3]
    f["tw1"] = f["tw_lo"] + 1
    f["reference"] = np.maximum(f["lb_best"], f["tw1"])
    f["violation"] = f["pendant"] > f["optimum"]
    f["tight"] = f["pendant"] == f["optimum"]
    f["above_omega"] = f["pendant"] > f["omega"]
    f["above_lb"] = f["pendant"] > f["lb_best"]
    f["above_ref"] = f["pendant"] > f["reference"]
    f["gain_over_ref"] = f["pendant"] - f["reference"]
    print(f"rows scored: {len(f)} of {len(rows)} corpus rows; {time.time() - t0:.0f} s wall;"
          f" {f['pendant_seconds'].sum() / 3600:.2f} core-hours; censored evaluations:"
          f" {int(f['pendant_censored_eval'].astype(str).str.lower().eq('true').sum())}")
    print(f"violations (pendant > optimum): {int(f['violation'].sum())}")
    print(f"tight (pendant == optimum): {int(f['tight'].sum())} ({f['tight'].mean():.1%})")
    print(f"above the clique floor ω: {int(f['above_omega'].sum())}; above lb_best: {int(f['above_lb'].sum())};"
          f" above max(lb_best, tw + 1): {int(f['above_ref'].sum())}")
    g = f[f["is_gap"]]
    print(f"\nthe {len(g)} bound-gap instances (optimum − lb_best ≥ 2): above ω {int(g['above_omega'].sum())},"
          f" above lb_best {int(g['above_lb'].sum())}, above the reference {int(g['above_ref'].sum())},"
          f" tight {int(g['tight'].sum())}; max gain over the reference {int(g['gain_over_ref'].max())}")
    def table(frame, by):
        t = frame.groupby(by, observed=False).agg(instances=("pendant", "size"), tight=("tight", "sum"),
                                  above_omega=("above_omega", "sum"), above_lb=("above_lb", "sum"),
                                  above_ref=("above_ref", "sum"),
                                  mean_gap=("gap", "mean"),
                                  mean_pendant_gap=("optimum", lambda s: float((s - frame.loc[s.index, "pendant"]).mean())),
                                  censored=("pendant_censored_eval", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
                                  median_s=("pendant_seconds", "median"), max_s=("pendant_seconds", "max"))
        return t
    pd.set_option("display.width", 200)
    print("\nby collection, all corpus rows\n" + table(f, "collection").to_string())
    f["band"] = pd.cut(f["n_customers"], [0, 20, 30, 40, 50, 75, 100, 200], right=True)
    print("\nby size band, all corpus rows\n" + table(f, "band").to_string())
    if len(g):
        print("\nby collection, bound-gap instances\n" + table(g, "collection").to_string())
        best = g.sort_values("gain_over_ref", ascending=False).head(15)
        cols = ["instance_name", "n_customers", "optimum", "lb_best", "tw1", "reference", "pendant", "omega", "pendant_cliques"]
        print("\nbound-gap instances where Lemma P gains most over the reference\n" + best[cols].to_string(index=False))
    keep = ["instance_name", "source_file", "collection", "n_customers", "optimum", "lb_best", "gap", "tw_lo", "tw_hi",
            "tw1", "reference", "omega", "pendant", "pendant_cliques", "pendant_censored_eval", "pendant_seconds",
            "is_gap", "violation", "tight", "above_omega", "above_lb", "above_ref", "gain_over_ref"]
    f[keep].to_csv(HERE / "scored.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
