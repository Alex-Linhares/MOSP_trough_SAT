"""Item 04: the search's minor floor through `learning.bound_harness`'s
validity stage on the corpus, written to this directory. The candidate is a
*lookup*: the harness hands it a matrix, it finds the instance by the SHA-256
of the rows among the run's certificate directories
(`certificates/<instance>/instance.mosp`) and returns that instance's
`floor` from `search.json`; an instance the run did not cover gets the
trivial 1. So "above optimum" being 0 checks every floor the item produced
against the certified optimum, on the harness's own reading of the corpus.

Run as `nice -n 19 python3 reports/scratch/obstruction_search/04_minor/run_harness.py --workers 8`.
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
            inst, cert = d / "instance.mosp", d / "search.json"
            if not (inst.exists() and cert.exists()):
                continue
            lines = inst.read_text().splitlines()
            n = int(lines[1].split()[0])
            rows = [[int(x) for x in ln.split()] for ln in lines[2:2 + n]]
            rec = json.loads(cert.read_text())
            table[_rows_sha256(rows)] = (lines[0].strip(), int(rec["floor"]))
        _LOOKUP = table
    return _LOOKUP


def minor_floor(graph, matrix, budget) -> tuple[int, dict]:
    """Family M's searched floor from the item 04 run, by lookup; 1 where the run has no record."""
    hit = _lookup().get(_rows_sha256(matrix))
    if hit is None:
        return 1, {"source": "none"}
    return hit[1], {"source": "minor_run", "instance": hit[0]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=None)
    args = ap.parse_args()
    bh.CANDIDATES["minor_floor"] = minor_floor
    frame = bh.run_validity(args.workers, ("minor_floor",), out_csv=OUT_CSV, sources=("corpus",), wall=args.wall)
    table = bh.validity_table(frame)
    print(table.to_string())
    HERE.joinpath("harness_table.md").write_text(table.to_markdown(index=False) + "\n")


if __name__ == "__main__":
    main()
