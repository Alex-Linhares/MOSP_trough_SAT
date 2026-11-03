"""Item 02: the cap-12 floor through `learning.bound_harness`'s validity stage
on the corpus, written to this directory (the harness's own values file is
loop0004's artifact and is left alone). Equivalent to

    python -m learning.bound_harness --stage validity --workers 8 --sources corpus \
        --candidates "" --extra learning.obstruction_expansion:harper_floor

except for the output path. Run as
`nice -n 19 python3 reports/scratch/obstruction_search/02_expansion/run_harness.py --workers 8`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from learning import bound_harness as bh  # noqa: E402
from learning.obstruction_expansion import harper_floor  # noqa: E402

OUT_CSV = Path(__file__).with_name("harness_values.csv")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=None)
    args = ap.parse_args()
    bh.CANDIDATES["harper_floor"] = harper_floor
    frame = bh.run_validity(args.workers, ("harper_floor",), out_csv=OUT_CSV, sources=("corpus",), wall=args.wall)
    table = bh.validity_table(frame)
    print(table.to_string())
    Path(__file__).with_name("harness_table.md").write_text(table.to_markdown(index=False) + "\n")


if __name__ == "__main__":
    main()
