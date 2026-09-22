"""Does a better starting bound make the complete search certify faster?

`customer_search.solve` descends `k` from an upper bound until a refutation
lands. Every stack the starting bound saves is one whole `decide` call the
descent never makes. The calls it skips are the cheap ones at the top, so the
saving is not free money -- but it is also true that a descent starting two
stacks high pays for two extra satisfiable searches before reaching the
refutation that matters.

`learned+cs-dfs` starts lower than `cs-dfs` on 709 of the 6,376 corpus instances
(`reports/learning.md` §2.1). This re-certifies instances from scratch under
both and compares what it cost, which is the only currency left now that the
corpus is closed and there is nothing new to prove.

Both runs must arrive at the same value -- the certified optimum already on
disk. A disagreement is reported rather than averaged away.

Usage:
    python -m learning.descent_bench --instances 60
    python -m learning.descent_bench --match=Random- --instances 40 --budget 120
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path

from mosp.instance import MOSPInstance

STRATEGIES = ("cs-dfs", "learned+cs-dfs")


def _improved_instances() -> set[str]:
    """The instances where `learned+cs-dfs` starts below `cs-dfs`.

    Read from the corpus sweeps, so the selection is a measurement rather than
    a guess. These are the only instances where a different starting bound can
    possibly change the descent, and pooling them with the thousands where the
    two bounds agree would dilute the effect to nothing.
    """
    base = json.loads(Path("learning/data/sweep_cs-dfs.json").read_text())
    new = json.loads(Path("learning/data/sweep_learned_cs-dfs.json").read_text())
    achieved = {r["instance"]: r["achieved"] for r in base["rows"]}
    return {r["instance"] for r in new["rows"]
            if r["achieved"] is not None
            and achieved.get(r["instance"]) is not None
            and r["achieved"] < achieved[r["instance"]]}


def _corpus(count: int, seed: int, match: str | None,
            max_customers: int, improved_only: bool = False) -> list[tuple[MOSPInstance, int]]:
    from satisfiability.mosp_solver import _solution_path

    from learning.dataset import enumerate_instances

    pairs = enumerate_instances(Path("benchmarks/instances"))
    rng = random.Random(seed)
    rng.shuffle(pairs)

    improved = _improved_instances() if improved_only else None

    chosen = []
    for _, instance in pairs:
        if match and match not in instance.name:
            continue
        if improved is not None and instance.name not in improved:
            continue
        if instance.n_customers > max_customers:
            continue
        path = _solution_path(instance, Path("solutions"))
        if not path.exists():
            continue
        chosen.append((instance, json.loads(path.read_text())["mosp_value"]))
        if len(chosen) >= count:
            break
    return chosen


def run(
    instances: list[tuple[MOSPInstance, int]],
    budget: float = 60.0,
    verbose: bool = True,
) -> dict:
    from learning.policy import DEFAULT_MODEL, load
    from satisfiability.customer_search import solve

    # Load the booster before the clock starts on the first instance, or its
    # one-off 0.6s lands on whichever instance happens to be first.
    load(DEFAULT_MODEL)

    rows = []
    for instance, optimum in instances:
        record: dict[str, object] = {
            "instance": instance.name,
            "n_customers": instance.n_customers,
            "optimum": optimum,
        }
        for strategy in STRATEGIES:
            started = time.monotonic()
            answer = solve(instance, upper_strategy=strategy, time_budget=budget)
            record[f"{strategy}_seconds"] = time.monotonic() - started
            record[f"{strategy}_nodes"] = answer.nodes
            record[f"{strategy}_value"] = answer.value
            record[f"{strategy}_proof"] = answer.proof
            record[f"{strategy}_start"] = answer.value if not answer.proof else None
        rows.append(record)
        if verbose:
            a, b = (record[f"{s}_seconds"] for s in STRATEGIES)
            print(f"  {instance.name[:40]:40s} {a:7.2f}s -> {b:7.2f}s"
                  f"  {'FASTER' if b < a * 0.98 else ''}", flush=True)

    return {"rows": rows, "summary": _summarise(rows)}


def _summarise(rows: list[dict]) -> dict:
    base, new = STRATEGIES
    proved = [r for r in rows
              if r[f"{base}_proof"] and r[f"{new}_proof"]]
    wrong = [r["instance"] for r in rows
             for s in STRATEGIES
             if r[f"{s}_proof"] and r[f"{s}_value"] != r["optimum"]]
    only_new = [r["instance"] for r in rows
                if r[f"{new}_proof"] and not r[f"{base}_proof"]]
    only_base = [r["instance"] for r in rows
                 if r[f"{base}_proof"] and not r[f"{new}_proof"]]

    def total(key: str) -> float:
        return sum(r[key] for r in proved)

    speedups = [r[f"{base}_seconds"] / r[f"{new}_seconds"]
                for r in proved if r[f"{new}_seconds"] > 0]

    return {
        "instances": len(rows),
        "certified_by_both": len(proved),
        "base_seconds": total(f"{base}_seconds"),
        "new_seconds": total(f"{new}_seconds"),
        "base_nodes": int(total(f"{base}_nodes")),
        "new_nodes": int(total(f"{new}_nodes")),
        "median_speedup": statistics.median(speedups) if speedups else 0.0,
        "faster": sum(1 for r in proved
                      if r[f"{new}_seconds"] < r[f"{base}_seconds"] * 0.98),
        "slower": sum(1 for r in proved
                      if r[f"{new}_seconds"] > r[f"{base}_seconds"] * 1.02),
        "certified_only_by_learned": only_new,
        "certified_only_by_baseline": only_base,
        "value_disagreements": wrong,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instances", type=int, default=60)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--match", type=str, default=None)
    parser.add_argument("--max-customers", type=int, default=125)
    parser.add_argument("--budget", type=float, default=60.0)
    parser.add_argument("--improved", action="store_true",
                        help="only instances where the learned bound starts lower")
    parser.add_argument("--out", type=Path,
                        default=Path("learning/data/descent_bench.json"))
    args = parser.parse_args()

    instances = _corpus(args.instances, args.seed, args.match, args.max_customers,
                        improved_only=args.improved)
    print(f"{len(instances)} instances, {args.budget:.0f}s budget each\n")

    result = run(instances, budget=args.budget)
    s = result["summary"]
    base, new = STRATEGIES

    print(f"\ncertified by both: {s['certified_by_both']}/{s['instances']}")
    print(f"  {base:16s} {s['base_seconds']:9.1f}s  {s['base_nodes']:14,d} nodes")
    print(f"  {new:16s} {s['new_seconds']:9.1f}s  {s['new_nodes']:14,d} nodes")
    if s["base_seconds"]:
        print(f"  total time ratio {s['new_seconds']/s['base_seconds']:.3f}, "
              f"median speedup {s['median_speedup']:.2f}x")
    print(f"  faster on {s['faster']}, slower on {s['slower']}")
    for key in ("certified_only_by_learned", "certified_only_by_baseline",
                "value_disagreements"):
        if s[key]:
            print(f"  {key}: {len(s[key])} {s[key][:4]}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
