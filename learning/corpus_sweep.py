"""Run an upper bound strategy over the whole corpus and score it against truth.

`benchmarks.reheuristic` exists to *improve* cached values, and against a closed
corpus it can improve nothing: every cached value is a proved optimum, and
`_save_solution` is monotone, so a sweep writes nothing. What it still does is
report, per instance, the cached value beside what the strategy achieved -- and
since the cached value is the optimum, that turns the sweep into an exact
scoring run over all 6,376 instances rather than a sample.

For a learned strategy one thing has to be arranged first. The policy trained on
the whole corpus has seen every instance here, so sweeping with it would measure
memorisation. `--folds` instead sweeps fold by fold, each with the model that
held that fold's files out (`learning.policy.train_folds`), so no instance is
ever scored by a model that saw its generator configuration.

Usage:
    python -m learning.corpus_sweep --strategy cs-dfs
    python -m learning.corpus_sweep --strategy learned+cs-dfs --folds
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from benchmarks.reheuristic import sweep
from learning.dataset import enumerate_instances
from learning.policy import MODEL_DIR
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import SOLUTIONS_DIR

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")
RESULTS_DIR = Path("learning/data")

# Scoring runs go in their own ledger. `benchmarks/results/compute_ledger.csv`
# answers "what did this corpus cost to prove", and a sweep that improves
# nothing -- which is every sweep against a closed corpus -- did not contribute
# to that. One scoring pass over 6,376 instances is an hour of core time, and
# quietly folding it into the headline figure would misattribute it.
SWEEP_LEDGER = RESULTS_DIR / "sweep_ledger.csv"


def _score(rows: list[tuple]) -> dict:
    """Aggregate sweep rows, whose `before` is the certified optimum."""
    scored = [(name, before, after) for name, before, after, _, note in rows
              if before is not None and after is not None]
    errors = [after - before for _, before, after in scored]
    below = [name for name, before, after in scored if after < before]
    failures = [(name, note) for name, _, after, _, note in rows
                if after is None and note not in (None, "closed")]

    return {
        "instances": len(scored),
        "mae": sum(errors) / len(errors) if errors else 0.0,
        "exact": sum(1 for e in errors if e == 0) / len(errors) if errors else 0.0,
        "worst": max(errors) if errors else 0,
        "total_overshoot": sum(errors),
        "below_optimum": below,
        "failures": failures,
    }


def run(
    strategy: str,
    use_folds: bool = False,
    workers: int = 12,
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
    solutions_dir: Path = SOLUTIONS_DIR,
    limit: int | None = None,
    ledger: Path = SWEEP_LEDGER,
    verbose: bool = True,
) -> tuple[dict, list[tuple]]:
    pairs = enumerate_instances(instance_dir)
    if limit:
        pairs = pairs[:limit]

    batches: list[tuple[str, list[MOSPInstance], dict]] = []
    if use_folds:
        manifest = json.loads((MODEL_DIR / "folds.json").read_text())
        assignment = manifest["assignment"]
        for fold in range(manifest["folds"]):
            members = [inst for path, inst in pairs
                       if assignment.get(str(path)) == fold]
            if members:
                batches.append((f"fold {fold}", members,
                                {"model_path": str(MODEL_DIR / f"fold{fold}.txt")}))
    else:
        batches.append(("all", [inst for _, inst in pairs], {}))

    rows: list[tuple] = []
    started = time.time()
    for label, members, kwargs in batches:
        if verbose:
            print(f"{label}: {len(members)} instances, strategy={strategy}",
                  flush=True)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        rows.extend(sweep(members, strategy, workers=workers,
                          solutions_dir=solutions_dir, ledger=ledger,
                          verbose=False, **kwargs))

    summary = _score(rows)
    summary["strategy"] = strategy
    summary["wall_clock"] = time.time() - started
    summary["folds"] = use_folds
    return summary, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--strategy", type=str, default="learned+cs-dfs")
    parser.add_argument("--folds", action="store_true",
                        help="sweep fold by fold with held-out models")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    summary, rows = run(args.strategy, use_folds=args.folds,
                        workers=args.workers, limit=args.limit)

    print(f"\n{summary['strategy']}"
          f"{' (held-out models)' if summary['folds'] else ''} "
          f"over {summary['instances']} instances "
          f"in {summary['wall_clock']:.0f}s")
    print(f"  mean overshoot   {summary['mae']:.3f}")
    print(f"  exact            {summary['exact']*100:.1f}%")
    print(f"  worst            +{summary['worst']}")
    print(f"  total overshoot  {summary['total_overshoot']}")
    if summary["below_optimum"]:
        print(f"  !! {len(summary['below_optimum'])} below a certified optimum: "
              f"{summary['below_optimum'][:5]}")
    if summary["failures"]:
        print(f"  !! {len(summary['failures'])} failed: {summary['failures'][:3]}")

    out = args.out or RESULTS_DIR / f"sweep_{args.strategy.replace('+', '_')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"summary": {k: v for k, v in summary.items() if k != "failures"},
         "rows": [{"instance": n, "optimum": b, "achieved": a, "seconds": s}
                  for n, b, a, s, _ in rows]}, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
