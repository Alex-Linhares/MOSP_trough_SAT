"""Item 03: the exact floor (cap-12 branch and bound raised by every SAT-proved
level) through `learning.bound_harness`'s validity stage on the corpus, written
to this directory. The candidate is a *lookup*: the harness hands it a matrix,
it finds the instance by the SHA-256 of the rows among the run's certificate
directories (`certificates/<instance>/instance.mosp`, whose first line is the
name) and returns that instance's `floor_after` from `summary.json`; an
instance the run did not reach gets the trivial 1. So "above optimum" being
0 checks every floor the item produced against the certified optimum, on the
harness's own reading of the corpus. Equivalent to

    python -m learning.bound_harness --stage validity --workers 8 --sources corpus \
        --candidates "" --extra reports...run_harness:sat_floor

Run as `nice -n 19 python3 reports/scratch/obstruction_search/03_sat/run_harness.py --workers 8`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

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
        table: dict[str, tuple[str, int]] = {}
        for d in (HERE / "certificates").iterdir():
            inst, summ = d / "instance.mosp", d / "summary.json"
            if not (inst.exists() and summ.exists()):
                continue
            lines = inst.read_text().splitlines()
            n = int(lines[1].split()[0])
            rows = [[int(x) for x in ln.split()] for ln in lines[2:2 + n]]
            rec = json.loads(summ.read_text())
            table[_rows_sha256(rows)] = (lines[0].strip(), int(rec["floor_after"]))
        _LOOKUP = table
    return _LOOKUP


def sat_floor(graph, matrix, budget) -> tuple[int, dict]:
    """Family E's exact floor from the item 03 run, by lookup; 1 where the run has no record."""
    hit = _lookup().get(_rows_sha256(matrix))
    if hit is None:
        return 1, {"source": "none"}
    return hit[1], {"source": "sat_run", "instance": hit[0]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=None)
    args = ap.parse_args()
    bh.CANDIDATES["sat_floor"] = sat_floor
    frame = bh.run_validity(args.workers, ("sat_floor",), out_csv=OUT_CSV, sources=("corpus",), wall=args.wall)
    table = bh.validity_table(frame)
    print(table.to_string())
    HERE.joinpath("harness_table.md").write_text(table.to_markdown(index=False) + "\n")


if __name__ == "__main__":
    main()
