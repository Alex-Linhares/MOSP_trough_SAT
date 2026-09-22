"""A closing-order policy learned by imitating the certified witnesses.

Every construction heuristic in `satisfiability.heuristics` answers one
question repeatedly: given the customers already closed, which one closes next?
MCN answers it with minimum remaining degree, Chu & Stuckey's DFS answers it by
searching. The corpus answers it 100,000 times over -- each certified witness is
a product order, which induces a closing order, which is a sequence of decisions
made by something that provably reached the optimum.

So the policy here is trained by imitation: replay each witness, and at every
step label the customer it actually closed against all the others available.
The learned scorer is then used greedily, and the order it produces is
*simulated* like any other -- nothing is trusted because a model proposed it,
which is what makes learning safe to use here at all. The same order is also
handed to `restricted_dfs` as its incumbent, where it is worth more than extra
nodes (see that function's docstring).

Measured by five-fold cross-validation grouped by source file
(`reports/learning.md`):

    MCN                      MAE 1.63 over the optimum, exact on 51.0%
    learned greedy           MAE 0.46                   exact on 75.0%
    cs-dfs                   MAE 0.30                   exact on 82.0%
    cs-dfs, learned seed     MAE 0.14                   exact on 92.0%

The greedy is better than MCN on average and worse than `cs-dfs` in the tail --
it overshoots by 34 on one held-out instance against the DFS's worst of 10 --
which is the shape of a construction with no search behind it. Its value is as
the DFS's incumbent, where it cuts the worst case to 6.

Usage:
    python -m learning.policy train           # writes learning/models/policy.txt
    python -m learning.policy evaluate        # grouped cross-validation
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import (
    _customer_order_from_products,
    _neighbour_masks,
    product_order_from_customers,
)

MODEL_DIR = Path("learning/models")
DEFAULT_MODEL = MODEL_DIR / "policy.txt"

# Names in the order `step_features` emits them; used for importances and to
# make a saved model self-describing.
STEP_FEATURE_NAMES = [
    "remaining_degree",   # neighbours not yet closed -- MCN's own criterion
    "newly_opened",       # customers this closing would open for the first time
    "already_open",       # 1 if some product of this customer is already produced
    "open_after",         # open stacks immediately after closing it (the cs cost)
    "open_now",           # open stacks before the decision
    "progress",           # fraction of customers already closed
    "total_degree",       # degree in the MOSP graph
    "n_customers",        # instance scale, so one model covers every size
]


def step_features(
    masks: Sequence[int], n: int, closed: int, opened: int, candidate: int
) -> list[float]:
    """Features of "close `candidate` next", given the state of the sweep.

    `closed` and `opened` are bitmasks over customers: closed ones are done,
    opened ones have had at least one of their products produced. Everything is
    computed from the self-inclusive neighbourhood masks of the MOSP graph, so a
    decision costs a handful of popcounts.

    Deliberately local. A policy that needed a global view of the instance could
    not be evaluated in the inner loop of a search, which is where this one is
    meant to end up.
    """
    nb = masks[candidate]
    after_closed = closed | (1 << candidate)
    after_open = opened | nb
    return [
        float((nb & ~closed).bit_count() - 1),
        float((nb & ~opened).bit_count()),
        1.0 if (opened >> candidate) & 1 else 0.0,
        float((after_open & ~after_closed).bit_count()),
        float((opened & ~closed).bit_count()),
        float(closed.bit_count() / n) if n else 0.0,
        float(nb.bit_count() - 1),
        float(n),
    ]


def training_rows(
    instance: MOSPInstance, closing_order: Sequence[int]
) -> tuple[list[list[float]], list[int]]:
    """Replay one witness into (features, chosen?) rows, one per candidate.

    Steps with a single candidate are skipped: there is no decision to imitate
    and they would only dilute the positive rate.
    """
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    closed = opened = 0
    X: list[list[float]] = []
    y: list[int] = []

    for chosen in closing_order:
        candidates = [c for c in range(n) if masks[c] and not (closed >> c) & 1]
        if len(candidates) > 1:
            for candidate in candidates:
                X.append(step_features(masks, n, closed, opened, candidate))
                y.append(int(candidate == chosen))
        opened |= masks[chosen]
        closed |= 1 << chosen

    return X, y


def witness_closing_order(
    instance: MOSPInstance, ordering: Sequence[int]
) -> list[int]:
    """The closing order a certified witness induces."""
    return _customer_order_from_products(instance, ordering)


def learned_closing_order(instance: MOSPInstance, model) -> list[int]:
    """Greedy closing order under the learned scorer."""
    masks = _neighbour_masks(instance)
    n = instance.n_customers
    closed = opened = 0
    remaining = {c for c in range(n) if masks[c]}
    order: list[int] = []

    while remaining:
        candidates = sorted(remaining)
        X = np.array(
            [step_features(masks, n, closed, opened, c) for c in candidates],
            dtype=np.float32,
        )
        # Single-threaded on purpose: the matrix is one row per candidate, so
        # LightGBM's thread pool costs more than it saves, and the sweeps in
        # `benchmarks` already fan out one process per instance.
        scores = model.predict(X, raw_score=True, num_threads=1)
        pick = candidates[int(np.argmax(scores))]
        order.append(pick)
        opened |= masks[pick]
        closed |= 1 << pick
        remaining.discard(pick)

    return order


def learned_upper_bound(
    instance: MOSPInstance, model=None, dfs_nodes: int = 0
) -> tuple[int, list[int]]:
    """An upper bound from the learned policy, counted by simulation.

    With `dfs_nodes > 0` the learned order becomes the incumbent of Chu &
    Stuckey's restricted DFS instead of the answer, which is where it is worth
    most. Either way the number returned comes from `max_open_stacks` on the
    original instance, so a bad model costs quality and never correctness.
    """
    model = model or load(DEFAULT_MODEL)
    order = learned_closing_order(instance, model)

    if dfs_nodes:
        from satisfiability.heuristics import restricted_dfs

        return restricted_dfs(instance, max_nodes=dfs_nodes, seed_order=order)

    ordering = product_order_from_customers(instance, order)
    return max_open_stacks(instance, ordering), ordering


# -------------------------------------------------------
# Training
# -------------------------------------------------------


def _corpus(
    instance_dir: Path = Path("benchmarks/instances"),
    solutions_dir: Path = Path("solutions"),
    certified_only: bool = True,
) -> list[tuple[str, MOSPInstance, dict]]:
    """Instances paired with their solution file, keyed by source file."""
    from learning.dataset import enumerate_instances
    from satisfiability.mosp_solver import CERTIFIED, _solution_path

    out = []
    for filepath, instance in enumerate_instances(instance_dir):
        path = _solution_path(instance, solutions_dir)
        if not path.exists():
            continue
        try:
            solution = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if certified_only and solution.get("provenance") not in CERTIFIED:
            continue
        out.append((str(filepath), instance, solution))
    return out


def _fit(corpus, n_estimators: int = 300, learning_rate: float = 0.08):
    import lightgbm as lgb

    X: list[list[float]] = []
    y: list[int] = []
    for _, instance, solution in corpus:
        order = witness_closing_order(instance, solution["ordering"])
        rows, labels = training_rows(instance, order)
        X.extend(rows)
        y.extend(labels)

    model = lgb.LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=63,
        verbose=-1,
    )
    model.fit(np.array(X, dtype=np.float32), np.array(y),
              feature_name=STEP_FEATURE_NAMES)
    return model.booster_, len(y)


def fold_assignment(folds: int = 5, seed: int = 2) -> dict[str, int]:
    """Which cross-validation fold each benchmark file belongs to.

    Shared by `evaluate` and `train_folds` so that a model is never asked about
    an instance from a file it trained on -- the whole point of holding out by
    file rather than by instance.
    """
    corpus = _corpus()
    files = sorted({f for f, _, _ in corpus})
    rng = random.Random(seed)
    rng.shuffle(files)
    return {name: index % folds for index, name in enumerate(files)}


def train_folds(
    folds: int = 5, seed: int = 2, out_dir: Path = MODEL_DIR, verbose: bool = True
) -> dict[int, Path]:
    """Fit one model per fold, each blind to its own fold's files.

    What this buys: a sweep over the *whole* corpus where every instance is
    scored by a model that never saw its generator configuration. Running the
    all-data model over the corpus it was fitted on would measure memorisation.
    """
    corpus = _corpus()
    assignment = fold_assignment(folds=folds, seed=seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[int, Path] = {}
    for fold in range(folds):
        training = [row for row in corpus if assignment[row[0]] != fold]
        booster, n_rows = _fit(training)
        path = out_dir / f"fold{fold}.txt"
        booster.save_model(str(path))
        paths[fold] = path
        if verbose:
            print(f"  fold {fold}: {len(training)} witnesses, "
                  f"{n_rows:,} rows -> {path}", flush=True)

    manifest = out_dir / "folds.json"
    manifest.write_text(json.dumps(
        {"folds": folds, "seed": seed, "assignment": assignment}, indent=2))
    if verbose:
        print(f"wrote {manifest}")
    return paths


def load(path: Path = DEFAULT_MODEL):
    import lightgbm as lgb

    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist; run `python -m learning.policy train` first"
        )
    return lgb.Booster(model_file=str(path))


def train(out: Path = DEFAULT_MODEL, verbose: bool = True) -> Path:
    """Fit on every certified witness and save the booster."""
    started = time.time()
    corpus = _corpus()
    booster, n_rows = _fit(corpus)
    out.parent.mkdir(parents=True, exist_ok=True)
    booster.save_model(str(out))
    if verbose:
        print(f"{len(corpus)} witnesses -> {n_rows:,} decision rows, "
              f"fitted in {time.time() - started:.0f}s")
        print(f"wrote {out}")
        for name, gain in sorted(
            zip(STEP_FEATURE_NAMES, booster.feature_importance("gain")),
            key=lambda t: -t[1],
        ):
            print(f"  {name:18s} {gain:12,.0f}")
    return out


# -------------------------------------------------------
# Evaluation
# -------------------------------------------------------


def evaluate(
    folds: int = 5,
    per_fold: int = 400,
    dfs_nodes: int = 200_000,
    seed: int = 2,
    verbose: bool = True,
) -> dict[str, dict[str, float]]:
    """Cross-validate the policy, grouping by source file.

    Grouping matters more than usual: instances in one benchmark file came from
    one generator configuration, so a random split would train on a row's own
    siblings. `per_fold` caps how many held-out instances are actually run,
    because the comparison runs four constructions per instance.
    """
    from satisfiability.heuristics import restricted_dfs, upper_bound

    corpus = _corpus()
    files = sorted({f for f, _, _ in corpus})
    rng = random.Random(seed)
    rng.shuffle(files)
    blocks = [set(files[i::folds]) for i in range(folds)]

    results: dict[str, list[int]] = {k: [] for k in
                                     ("mcn", "learned", "cs-dfs", "cs-dfs+learned")}
    optima: list[int] = []

    for fold, held in enumerate(blocks, start=1):
        train_set = [row for row in corpus if row[0] not in held]
        test_set = [row for row in corpus if row[0] in held]
        rng.shuffle(test_set)
        test_set = test_set[:per_fold]

        booster, _ = _fit(train_set)
        started = time.time()
        for _, instance, solution in test_set:
            order = learned_closing_order(instance, booster)
            ordering = product_order_from_customers(instance, order)
            results["learned"].append(max_open_stacks(instance, ordering))
            results["mcn"].append(upper_bound(instance, "mcn")[0])
            results["cs-dfs"].append(restricted_dfs(instance, max_nodes=dfs_nodes)[0])
            results["cs-dfs+learned"].append(
                restricted_dfs(instance, max_nodes=dfs_nodes, seed_order=order)[0]
            )
            optima.append(int(solution["mosp_value"]))
        if verbose:
            print(f"  fold {fold}/{folds}: {len(test_set)} held-out instances "
                  f"in {time.time() - started:.0f}s", flush=True)

    truth = np.array(optima)
    summary = {}
    for name, values in results.items():
        err = np.array(values) - truth
        summary[name] = {
            "mae": float(np.abs(err).mean()),
            "exact": float((err == 0).mean()),
            "worst": int(err.max()),
        }
    if verbose:
        print(f"\n{len(truth)} held-out instances")
        print(f"{'strategy':18s} {'MAE':>7s} {'exact':>8s} {'worst':>6s}")
        for name, s in summary.items():
            print(f"{name:18s} {s['mae']:7.3f} {s['exact']*100:7.1f}% {s['worst']:6d}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    fit = sub.add_parser("train", help="fit on every certified witness")
    fit.add_argument("--out", type=Path, default=DEFAULT_MODEL)

    folds = sub.add_parser("train-folds",
                           help="one model per cross-validation fold")
    folds.add_argument("--folds", type=int, default=5)
    folds.add_argument("--seed", type=int, default=2)

    ev = sub.add_parser("evaluate", help="grouped cross-validation")
    ev.add_argument("--folds", type=int, default=5)
    ev.add_argument("--per-fold", type=int, default=400)
    ev.add_argument("--dfs-nodes", type=int, default=200_000)

    args = parser.parse_args()
    if args.command == "train":
        train(args.out)
    elif args.command == "train-folds":
        train_folds(folds=args.folds, seed=args.seed)
    else:
        evaluate(folds=args.folds, per_fold=args.per_fold, dfs_nodes=args.dfs_nodes)


if __name__ == "__main__":
    main()
