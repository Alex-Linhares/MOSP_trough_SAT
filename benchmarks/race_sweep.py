"""Is racing the two decision procedures better than picking one?

`satisfiability.race` runs the SAT encoding and the complete customer search at
once and takes the first definitive answer. Whether that is worth two cores
instead of one depends on a thing nobody had measured: how often the *other*
procedure would have been the right choice.

Three configurations per instance, all through the same descent so the only
difference is who decides `k`:

- `csearch` alone — what `benchmarks.csearch` does today;
- `sat` alone — what `benchmarks.solve_parallel` does today;
- both, raced.

The race cannot beat the better of the two by more than measurement noise; what
it can do is never be the worse one. The number worth reading is how far the two
singles are apart, because that gap is what a wrong guess costs.

Usage:
    python -m benchmarks.race_sweep --match=Random- --instances 20 --budget 120
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

from mosp.instance import MOSPInstance

CONFIGS = {
    "csearch": ("csearch",),
    "sat": ("sat",),
    "race": ("csearch", "sat"),
}


def _corpus(count: int, seed: int, match: str | None,
            min_customers: int) -> list[tuple[MOSPInstance, int]]:
    from satisfiability.mosp_solver import _solution_path

    from learning.dataset import enumerate_instances

    pairs = enumerate_instances(Path("benchmarks/instances"))
    rng = random.Random(seed)
    rng.shuffle(pairs)

    chosen = []
    for _, instance in pairs:
        if match and match not in instance.name:
            continue
        if instance.n_customers < min_customers:
            continue
        path = _solution_path(instance, Path("solutions"))
        if not path.exists():
            continue
        chosen.append((instance, json.loads(path.read_text())["mosp_value"]))
        if len(chosen) >= count:
            break
    return chosen


def run(instances, budget: float, upper_strategy: str = "cs-dfs",
        verbose: bool = True) -> dict:
    from satisfiability.race import solve_race

    rows = []
    for instance, optimum in instances:
        record: dict[str, object] = {
            "instance": instance.name,
            "n_customers": instance.n_customers,
            "optimum": optimum,
        }
        for label, procedures in CONFIGS.items():
            started = time.monotonic()
            answer = solve_race(instance, time_budget=budget,
                                upper_strategy=upper_strategy,
                                procedures=procedures)
            record[f"{label}_seconds"] = time.monotonic() - started
            record[f"{label}_proof"] = answer.proof
            record[f"{label}_value"] = answer.value
            if label == "race":
                record["winners"] = answer.winners
        rows.append(record)
        if verbose:
            print(f"  {instance.name[:34]:34s} "
                  + "  ".join(
                      f"{label}={record[f'{label}_seconds']:6.1f}s"
                      f"{'*' if record[f'{label}_proof'] else ' '}"
                      for label in CONFIGS)
                  + f"  won: {record.get('winners')}", flush=True)

    return {"rows": rows, "summary": _summarise(rows)}


def _summarise(rows: list[dict]) -> dict:
    out: dict[str, object] = {"instances": len(rows)}
    for label in CONFIGS:
        proved = [r for r in rows if r[f"{label}_proof"]]
        out[label] = {
            "certified": len(proved),
            "seconds_on_certified": sum(r[f"{label}_seconds"] for r in proved),
        }

    # The comparison that matters: on instances everything certified, how does
    # the race compare with each single and with the oracle that always picks
    # the better one?
    common = [r for r in rows if all(r[f"{label}_proof"] for label in CONFIGS)]
    if common:
        out["common"] = {
            "instances": len(common),
            "csearch": sum(r["csearch_seconds"] for r in common),
            "sat": sum(r["sat_seconds"] for r in common),
            "race": sum(r["race_seconds"] for r in common),
            "oracle": sum(min(r["csearch_seconds"], r["sat_seconds"])
                          for r in common),
            "worst_choice": sum(max(r["csearch_seconds"], r["sat_seconds"])
                                for r in common),
        }

    wins: dict[str, int] = {}
    for row in rows:
        for procedure in (row.get("winners") or {}).values():
            wins[procedure] = wins.get(procedure, 0) + 1
    out["decision_calls_won"] = wins
    out["value_disagreements"] = [
        r["instance"] for r in rows
        for label in CONFIGS
        if r[f"{label}_proof"] and r[f"{label}_value"] != r["optimum"]]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instances", type=int, default=20)
    parser.add_argument("--seed", type=int, default=5)
    parser.add_argument("--match", type=str, default=None)
    parser.add_argument("--min-customers", type=int, default=40)
    parser.add_argument("--budget", type=float, default=120.0)
    parser.add_argument("--upper-strategy", type=str, default="cs-dfs")
    parser.add_argument("--out", type=Path,
                        default=Path("learning/data/race_sweep.json"))
    args = parser.parse_args()

    instances = _corpus(args.instances, args.seed, args.match, args.min_customers)
    print(f"{len(instances)} instances, {args.budget:.0f}s budget each, "
          f"upper bound from {args.upper_strategy}\n")

    result = run(instances, budget=args.budget, upper_strategy=args.upper_strategy)
    s = result["summary"]

    print(f"\n{'config':10s} {'certified':>10s} {'seconds':>10s}")
    for label in CONFIGS:
        print(f"{label:10s} {s[label]['certified']:10d} "
              f"{s[label]['seconds_on_certified']:10.1f}")
    if "common" in s:
        c = s["common"]
        print(f"\non the {c['instances']} all three certified:")
        for key in ("csearch", "sat", "race", "oracle", "worst_choice"):
            print(f"  {key:13s} {c[key]:9.1f}s")
    print(f"\ndecision calls won: {s['decision_calls_won']}")
    if s["value_disagreements"]:
        print(f"!! value disagreements: {s['value_disagreements']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
