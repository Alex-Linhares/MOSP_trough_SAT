"""What the corpus currently claims, counted from the files.

The certified share gets quoted in the README, in CLAUDE.md and in the paper
plan, and it moves every time a run closes something. Hand-carried figures in
those documents drifted four times in a single day, so they are regenerated from
here instead:

    python -m benchmarks.corpus            # the breakdown
    python -m benchmarks.corpus --quote    # the sentence the documents quote

"Distinct" is the number that matters for an open-problem count: SP4 is stored
under two names, so a file count overstates how many instances are unsettled.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from satisfiability.mosp_solver import CERTIFIED, SOLUTIONS_DIR


def survey(solutions_dir: Path = SOLUTIONS_DIR) -> dict:
    counts: collections.Counter = collections.Counter()
    open_names = []
    for path in sorted(solutions_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        provenance = data.get("provenance")
        counts[provenance] += 1
        if provenance not in CERTIFIED:
            open_names.append(data.get("instance_name", path.stem))

    files = sum(counts.values())
    certified = sum(counts[p] for p in CERTIFIED)
    distinct_open = {n.removesuffix("_0") for n in open_names}
    return {
        "files": files,
        "certified": certified,
        "refutation": counts["certified:refutation"],
        "bound": counts["certified:bound"],
        "open_files": files - certified,
        "open_distinct": len(distinct_open),
        "open_names": sorted(distinct_open),
        "share": certified / files if files else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--quote", action="store_true")
    parser.add_argument("--names", action="store_true",
                        help="list the instances whose optimality is open")
    args = parser.parse_args()

    s = survey(args.solutions_dir)
    if args.quote:
        print(f"{s['certified']:,} of {s['files']:,} certified optimal "
              f"({s['share']:.2%}); {s['open_distinct']} instances open")
        return

    print(f"  {s['refutation']:,} certified:refutation")
    print(f"  {s['bound']:,} certified:bound")
    print(f"  {s['open_files']:,} solution (optimality open)")
    print(f"  ----")
    print(f"  {s['certified']:,} of {s['files']:,} certified ({s['share']:.2%})")
    print(f"  {s['open_distinct']} distinct instances still open")
    if args.names:
        for name in s["open_names"]:
            print(f"     {name}")


if __name__ == "__main__":
    main()
