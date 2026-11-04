"""Join the checkpoint pilot with the refutation anatomy, one row per instance.

Reads `reports/scratch/checkpoint/pilot/pilot.csv` (floors per configuration)
and `reports/scratch/checkpoint/anatomy/anatomy.csv` (the search's state
census by prefix size) and prints the tables the report quotes.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from learning.checkpoint_bound import OUT


def load(pilot: Path = OUT / "pilot" / "pilot.csv", anatomy: Path = OUT / "anatomy" / "anatomy.csv"):
    d = pd.read_csv(pilot)
    d["kind"] = d.config.str.split(":").str[0]
    d["ok"] = d.status.astype(str).str.startswith("unsat")
    a = pd.read_csv(anatomy) if anatomy.exists() else None
    return d, a


def per_instance(d: pd.DataFrame) -> pd.DataFrame:
    base = d.groupby("instance_name").agg(n=("n", "first"), optimum=("optimum", "first"),
                                          harper=("harper_ref", "first")).reset_index()
    ok = d[d.ok]
    cols = {}
    for c in (2, 3, 4, 6, 8, 12, 16):
        s = ok[ok.config == f"even:{c}"].set_index("instance_name").mosp_floor
        cols[f"even{c}"] = s
    cols["pair_best"] = ok[ok.kind == "pair"].groupby("instance_name").mosp_floor.max()
    cols["single_best"] = ok[ok.kind == "single"].groupby("instance_name").mosp_floor.max()
    cols["full"] = ok[ok.config == "full"].set_index("instance_name").mosp_floor
    for k, s in cols.items():
        base[k] = base.instance_name.map(s)
    # the smallest even c that closes, and the smallest c reaching each floor
    evens = [2, 3, 4, 6, 8, 12, 16]

    def smallest_closing(row):
        for c in evens:
            v = row[f"even{c}"]
            if pd.notna(v) and v >= row.optimum:
                return c
        if pd.notna(row.full) and row.full >= row.optimum:
            return "full"
        return ""
    base["closes_at"] = base.apply(smallest_closing, axis=1)
    base["seconds_full"] = base.instance_name.map(d[d.config == "full"].set_index("instance_name").seconds)
    base["seconds_even8"] = base.instance_name.map(d[d.config == "even:8"].set_index("instance_name").seconds)
    return base.sort_values(["n", "instance_name"]).reset_index(drop=True)


def best_pair_sizes(d: pd.DataFrame) -> pd.DataFrame:
    ok = d[d.ok & (d.kind == "pair")].copy()
    idx = ok.groupby("instance_name").mosp_floor.idxmax()
    best = ok.loc[idx, ["instance_name", "n", "optimum", "harper_ref", "sizes", "mosp_floor"]].copy()
    best["sizes_frac"] = [" ".join(f"{int(s) / r.n:.2f}" for s in str(r.sizes).split()) for r in best.itertuples()]
    return best.sort_values(["n", "instance_name"]).reset_index(drop=True)


def join_anatomy(base: pd.DataFrame, a: pd.DataFrame, d: pd.DataFrame) -> pd.DataFrame:
    a = a[a.status == "unsat"][["instance_name", "nodes", "distinct_sets", "peak_p", "peak_nodes", "peak_distinct",
                                "half_window", "half_window_width", "profile_p"]]
    j = base.merge(a, on="instance_name", how="left")
    # does the best pair sit inside the half window?
    bp = best_pair_sizes(d).set_index("instance_name").sizes
    def inside(row):
        if pd.isna(row.half_window) or row.instance_name not in bp.index:
            return np.nan
        lo, hi = map(int, str(row.half_window).split("-"))
        sizes = list(map(int, bp[row.instance_name].split()))
        return sum(lo <= s <= hi for s in sizes)
    j["pair_sizes_in_half_window"] = j.apply(inside, axis=1)
    return j


def main() -> None:
    d, a = load()
    base = per_instance(d)
    pd.set_option("display.width", 250)
    print("per instance (optimum units; blank = censored or not run):")
    print(base.drop(columns=["seconds_full", "seconds_even8"]).to_string(index=False))
    print("\nclosures by family:")
    for k in ["single_best", "pair_best", "even2", "even3", "even4", "even6", "even8", "even12", "even16", "full"]:
        v = base[k]
        print(f"  {k:12} run {v.notna().sum():3}  closes {(v >= base.optimum).sum():3}  "
              f"mean gain over Harper {(v - base.harper).mean():.2f}  mean distance to optimum {(base.optimum - v).mean():.2f}")
    print("\nsmallest even grid that closes:", base.closes_at.replace("", "none").value_counts().to_dict())
    print("\nbest pair sizes (as fractions of n):")
    print(best_pair_sizes(d)[["instance_name", "n", "optimum", "harper_ref", "sizes", "sizes_frac", "mosp_floor"]].to_string(index=False))
    if a is not None:
        j = join_anatomy(base, a, d)
        print("\nanatomy: peak prefix size and half-window against the best pair:")
        print(j[["instance_name", "n", "optimum", "nodes", "distinct_sets", "peak_p", "peak_distinct", "half_window",
                 "half_window_width", "pair_best", "pair_sizes_in_half_window"]].to_string(index=False))
        jj = j.dropna(subset=["peak_p"])
        print(f"\npeak_p / n: median {np.median(jj.peak_p / jj.n):.2f}, IQR {np.percentile(jj.peak_p / jj.n, 25):.2f}-{np.percentile(jj.peak_p / jj.n, 75):.2f}")
        print(f"half-window width / n: median {np.median(jj.half_window_width / jj.n):.2f}")
        print(f"best-pair sizes inside the half window: {jj.pair_sizes_in_half_window.sum():.0f} of {2 * len(jj)}")


if __name__ == "__main__":
    main()
