"""Item 11: the combination's floors through `learning.bound_harness`'s
validity stage on the corpus, written to this directory. The candidate is a
*lookup*, as item 06's: the harness hands it a matrix, it finds the instance
by the SHA-256 of the rows among the scan's rows (`scan.csv`, joined to the
certificate directories' `instance.mosp`) and returns the best combination
floor over the minors scanned and the search (`search.csv`), in optimum
units; an instance outside the ten gets the trivial 1. So "above optimum"
being 0 checks every floor the item produced against the certified optimum,
on the harness's own reading of the corpus.

Run as `nice -n 19 python3 reports/scratch/obstruction_search/11_combo/run_harness.py --workers 8`.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from learning import bound_harness as bh  # noqa: E402

HERE = Path(__file__).parent
OUT_CSV = HERE / "harness_values.csv"
_LOOKUP: dict[str, tuple[str, int]] | None = None


def _rows_sha256(matrix) -> str:
    matrix = np.asarray(matrix, dtype=int)
    text = "".join(" ".join(str(int(v)) for v in row) + "\n" for row in matrix)
    return hashlib.sha256(text.encode()).hexdigest()


def _lookup() -> dict[str, tuple[str, int]]:
    global _LOOKUP
    if _LOOKUP is None:
        scan = pd.read_csv(HERE / "scan.csv")
        best = scan[scan["rule"] != "whole"].groupby("instance_name")["combo_floor"].max().to_dict()
        if (HERE / "search.csv").exists():
            se = pd.read_csv(HERE / "search.csv")
            for _, r in se.iterrows():
                if pd.notna(r["search_e_floor"]):
                    best[r["instance_name"]] = max(best.get(r["instance_name"], 1), int(r["search_e_floor"]))
        table: dict[str, tuple[str, int]] = {}
        for d in (HERE / "certificates").iterdir() if (HERE / "certificates").exists() else []:
            inst = d / "instance.mosp"
            if not inst.exists():
                continue
            lines = inst.read_text().splitlines()
            name = lines[0].strip()
            n = int(lines[1].split()[0])
            rows = [[int(x) for x in ln.split()] for ln in lines[2:2 + n]]
            if name in best:
                table[_rows_sha256(rows)] = (name, int(best[name]))
        _LOOKUP = table
    return _LOOKUP


def combo_floor(graph, matrix, budget) -> tuple[int, dict]:
    """The combination's best floor from the item 11 run, by lookup; 1 where the run has none."""
    hit = _lookup().get(_rows_sha256(matrix))
    if hit is None:
        return 1, {"source": "none"}
    return hit[1], {"source": "combo_run", "instance": hit[0]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=None)
    args = ap.parse_args()
    bh.CANDIDATES["combo_floor"] = combo_floor
    frame = bh.run_validity(args.workers, ("combo_floor",), out_csv=OUT_CSV, sources=("corpus",), wall=args.wall)
    table = bh.validity_table(frame)
    print(table.to_string())
    HERE.joinpath("harness_table.md").write_text(table.to_markdown(index=False) + "\n")


if __name__ == "__main__":
    main()
