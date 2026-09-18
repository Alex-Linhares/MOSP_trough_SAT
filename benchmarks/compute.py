"""How much compute this corpus has cost, totalled from the records.

The figure gets quoted -- in the README, in the paper plan, in conversation --
and a quoted number that nobody recomputes is a number that drifts. Several did
drift this week. So it is computed here from two sources rather than maintained
by hand:

- **the result CSVs** in `benchmarks/results/`, which the older sweeps wrote,
  each row carrying the seconds that instance took;
- **the ledger**, `benchmarks/results/compute_ledger.csv`, which the parallel
  drivers append to as they finish, one row per instance.

Both measure the same thing: seconds of one core working on one instance.

Quote it in two parts, in this order: **roughly how many days it takes, with the
core count in brackets**, then the core-hours. The first is what a reader wants
-- it answers "how long would this take me" -- and is meaningless without the
cores beside it, since the same work is a day on 25 cores and a month on one.
The second is the invariant, and the one that can be compared between runs.

What it does not count: time spent on instances that were abandoned without a
row being written, the Lean build, and any run whose log was never parsed into
the ledger. So the total is a **lower bound on compute spent**, which is the
honest direction for a cost figure to err in.

    python -m benchmarks.compute            # the table and the total
    python -m benchmarks.compute --quote    # the one line the docs quote
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

RESULTS_DIR = Path("benchmarks/results")
LEDGER = RESULTS_DIR / "compute_ledger.csv"
LEDGER_FIELDS = ("when", "driver", "instance", "seconds")

# Columns that different generations of runner used for the same quantity.
TIME_COLUMNS = ("time_seconds", "seconds", "elapsed")


def record(driver: str, rows: list[tuple[str, float]], ledger: Path = LEDGER) -> int:
    """Append one row per instance to the ledger. Returns rows written.

    Called by the drivers once a sweep finishes rather than per instance, so
    that concurrent workers never write the same file.
    """
    if not rows:
        return 0
    ledger.parent.mkdir(parents=True, exist_ok=True)
    new = not ledger.exists()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    with ledger.open("a", newline="") as fh:
        writer = csv.writer(fh)
        if new:
            writer.writerow(LEDGER_FIELDS)
        for instance, seconds in rows:
            writer.writerow([stamp, driver, instance, f"{float(seconds):.1f}"])
    return len(rows)


def _seconds_in(path: Path) -> tuple[float, int]:
    total, count = 0.0, 0
    try:
        with path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                for column in TIME_COLUMNS:
                    if row.get(column):
                        try:
                            total += float(row[column])
                            count += 1
                        except ValueError:
                            pass
                        break
    except (OSError, csv.Error):
        return 0.0, 0
    return total, count


def totals(results_dir: Path = RESULTS_DIR) -> list[tuple[str, float, int]]:
    """(source, core-hours, rows) per file, largest first."""
    rows = []
    for path in sorted(results_dir.glob("*.csv")):
        seconds, count = _seconds_in(path)
        if seconds:
            rows.append((path.name, seconds / 3600, count))
    rows.sort(key=lambda r: -r[1])
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--quote", action="store_true",
                        help="print only the sentence the documents quote")
    parser.add_argument("--cores", type=int, default=25,
                        help="cores to express the wall-clock estimate against")
    args = parser.parse_args()

    rows = totals(args.results_dir)
    core_hours = sum(r[1] for r in rows)

    days = core_hours / args.cores / 24
    cores = f"{args.cores} core" + ("s" if args.cores != 1 else "")
    rough = (f"{days:.1f} days" if days >= 1.5
             else "about a day" if days >= 0.7
             else f"about {days * 24:.0f} hours")

    if args.quote:
        print(f"{rough} on {cores} "
              f"({core_hours:.0f} core-hours, {core_hours / 24:.1f} core-days) "
              f"of recorded solver time, as of {time.strftime('%Y-%m-%d')}")
        return

    print(f"{'core-hours':>12s} {'rows':>8s}  source")
    for name, hours, count in rows:
        print(f"{hours:12.1f} {count:8d}  {name}")
    print(f"{core_hours:12.1f} {sum(r[2] for r in rows):8d}  TOTAL")
    print(f"\n{rough} on {cores} "
          f"({core_hours:.0f} core-hours, {core_hours / 24:.1f} core-days).")
    print("Quote the days with the core count beside them, then the core-hours: "
          "the first says how long it takes, the second is what compares "
          "between runs.")


if __name__ == "__main__":
    main()
