"""Does the two-key rule seed the DFS as well as the learned policy does, over
the whole corpus? (loop0004 item 01, `reports/ml_nature_plan_3.md` Q6a;
`reports/ml_nature.md` §28)

Question. `reports/learning.md` measured `learned+cs-dfs` -- Chu & Stuckey's
restricted DFS seeded with a LightGBM closing order -- as strictly better than
`cs-dfs` on 709 of 6,376 corpus instances and worse on 13, and left open
whether LightGBM belongs on the solver's critical path. `reports/ml_nature.md`
§7 then found that a two-key rule with no model -- close the customer that
opens the fewest new stacks, on ties the one with the most unclosed
neighbours -- seeds the DFS *better* than the ranker on 1,920 held-out
instances. This module runs the rule-seeded DFS (`rule+cs-dfs`, registered in
`satisfiability/heuristics.py` by this item) over all 6,376 beside `cs-dfs`
and `learned+cs-dfs`, and answers whether the dependency question still
exists.

Method. `learning.corpus_sweep` for every strategy, which is
`benchmarks.reheuristic.sweep` over a closed corpus: every cached value is a
certified optimum, so the sweep is an exact scoring run and writes nothing
(saves are monotone). The learned strategy is swept fold by fold with a model
that never saw the fold, and here the folds group by **file ∪ MOSP-graph
isomorphism class** (`learning.fingerprint.union_groups` over
`learning/data/canonical.csv`), not by file alone as `reports/learning.md`
did: 157 classes span more than one file, so a file split leaks isomorphic
copies (§1). The five union-fold models are trained by this module into
`learning/models/union/` with `learning.policy`'s own `_fit`. Seconds per
instance are measured separately, in-process, every strategy on every
instance in one worker, so that the sweep's process-spawn and import cost is
excluded; the in-process values are checked equal to the sweep's.

Strategies: `cs-dfs` (MCN seed, the baseline), `rule+cs-dfs`, `learned+cs-dfs`
(the three-way comparison the item asks for); `rule` alone and `cs-dfs+degree`
(the DFS whose fan is sorted by the rule's keys, no seed) as context rows.

Not a bound, not a solver change: no default changes, `_lower_bound` is not
touched, nothing is written to `solutions/`.

Run:
    python -m learning.rule_seed                  # all stages, ~12 min on 16 workers
    python -m learning.rule_seed --stage train    # the union-fold models only
    python -m learning.rule_seed --stage sweep    # the corpus sweeps
    python -m learning.rule_seed --stage time     # in-process seconds
    python -m learning.rule_seed --stage report   # tables from what is on disk
    python -m pytest tests/test_rule_seed.py -q

Writes `learning/data/rule_seed/` (sweep JSONs, `timing.csv`, `folds.json`)
and `reports/rule_seed_tables.md`. Sweep rows go to
`learning/data/sweep_ledger.csv`, the scoring ledger, never the compute ledger.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import random
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from learning.corpus_sweep import run as sweep_run
from learning.dataset import enumerate_instances
from learning.policy import MODEL_DIR, _corpus, _fit
from mosp.instance import MOSPInstance

OUT_DIR = Path("learning/data/rule_seed")
UNION_MODEL_DIR = MODEL_DIR / "union"
CANONICAL = Path("learning/data/canonical.csv")
TABLES = Path("reports/rule_seed_tables.md")

BASELINE = "cs-dfs"
STRATEGIES = ("cs-dfs", "rule+cs-dfs", "learned+cs-dfs", "rule", "cs-dfs+degree")
MODEL_STRATEGIES = {"learned+cs-dfs"}
HEAD_TO_HEAD = (
    ("rule+cs-dfs", "cs-dfs"),
    ("learned+cs-dfs", "cs-dfs"),
    ("rule+cs-dfs", "learned+cs-dfs"),
    ("rule", "cs-dfs"),
    ("cs-dfs+degree", "cs-dfs"),
    ("rule+cs-dfs", "cs-dfs+degree"),
)
SIZE_BANDS = ((1, 30), (31, 60), (61, 200))


# ----------------------------------------------------------------------------
# folds grouped by file ∪ isomorphism class
# ----------------------------------------------------------------------------

def union_fold_assignment(folds: int = 5, seed: int = 2,
                          canonical: Path = CANONICAL) -> dict[str, int]:
    """Which fold each benchmark file belongs to, with every file of a
    file ∪ class group in the same fold.

    Groups are the connected components of the file--class bipartite graph
    (`learning.fingerprint.union_groups`); the largest holds a quarter of the
    corpus, so groups are dealt largest-first to the fold with the fewest
    instances, ties by a seeded shuffle, rather than round-robin.
    """
    from learning.fingerprint import union_groups

    table = pd.read_csv(canonical)
    gid = union_groups(table["source_file"], table["graph_cert"])
    table = table.assign(group=gid)
    sizes = table.groupby("group").size()
    rng = random.Random(seed)
    groups = list(sizes.index)
    rng.shuffle(groups)
    groups.sort(key=lambda g: -sizes[g])          # stable: ties keep the shuffle
    load = [0] * folds
    fold_of_group: dict[int, int] = {}
    for g in groups:
        f = min(range(folds), key=lambda i: load[i])
        fold_of_group[g] = f
        load[f] += int(sizes[g])
    return {str(f): fold_of_group[g]
            for f, g in table.groupby("source_file")["group"].first().items()}


def train_union_folds(folds: int = 5, seed: int = 2,
                      out_dir: Path = UNION_MODEL_DIR, verbose: bool = True
                      ) -> Path:
    """`learning.policy.train_folds` with the union grouping; same manifest
    schema, so `learning.corpus_sweep --folds --model-dir` reads it."""
    corpus = _corpus()
    assignment = union_fold_assignment(folds=folds, seed=seed)
    missing = sorted({f for f, _, _ in corpus} - set(assignment))
    if missing:
        raise RuntimeError(f"{len(missing)} corpus files absent from "
                           f"{CANONICAL}: {missing[:3]}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for fold in range(folds):
        training = [row for row in corpus if assignment[row[0]] != fold]
        started = time.time()
        booster, n_rows = _fit(training)
        path = out_dir / f"fold{fold}.txt"
        booster.save_model(str(path))
        if verbose:
            held = sum(1 for row in corpus if assignment[row[0]] == fold)
            print(f"  fold {fold}: {len(training)} witnesses ({held} held out), "
                  f"{n_rows:,} rows, {time.time() - started:.0f}s -> {path}",
                  flush=True)
    manifest = out_dir / "folds.json"
    manifest.write_text(json.dumps(
        {"folds": folds, "seed": seed, "grouping": "file ∪ class",
         "assignment": assignment}, indent=2))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "folds.json").write_text(manifest.read_text())
    return manifest


# ----------------------------------------------------------------------------
# the sweeps
# ----------------------------------------------------------------------------

def _sweep_path(strategy: str) -> Path:
    return OUT_DIR / f"sweep_{strategy.replace('+', '_')}.json"


def run_sweeps(strategies: Sequence[str] = STRATEGIES, workers: int = 16,
               limit: int | None = None, force: bool = False) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for strategy in strategies:
        out = _sweep_path(strategy)
        if out.exists() and not force:
            print(f"{strategy}: {out} exists, skipping", flush=True)
            continue
        folds = strategy in MODEL_STRATEGIES
        summary, rows = sweep_run(strategy, use_folds=folds, workers=workers,
                                  limit=limit, model_dir=UNION_MODEL_DIR,
                                  verbose=True)
        if summary["below_optimum"]:
            raise RuntimeError(f"{strategy} beat a certified optimum on "
                               f"{summary['below_optimum'][:3]}")
        if summary["failures"]:
            raise RuntimeError(f"{strategy} failed on {summary['failures'][:3]}")
        out.write_text(json.dumps(
            {"summary": {k: v for k, v in summary.items() if k != "failures"},
             "rows": [{"instance": n, "optimum": b, "achieved": a, "seconds": s}
                      for n, b, a, s, _ in rows]}, indent=1))
        print(f"{strategy}: {summary['instances']} instances, "
              f"exact {summary['exact']*100:.1f}%, mean overshoot "
              f"{summary['mae']:.3f}, worst +{summary['worst']}, "
              f"{summary['wall_clock']:.0f}s wall -> {out}", flush=True)


# ----------------------------------------------------------------------------
# in-process seconds
# ----------------------------------------------------------------------------

_WORK: dict = {}


def _init_timing(strategies, fold_of_file, model_dir: str) -> None:
    from satisfiability.heuristics import _learned_model

    _WORK["strategies"] = tuple(strategies)
    _WORK["fold_of_file"] = fold_of_file
    _WORK["model_dir"] = Path(model_dir)
    if MODEL_STRATEGIES & set(strategies):
        for fold in sorted(set(fold_of_file.values())):
            _learned_model(_WORK["model_dir"] / f"fold{fold}.txt")   # warm the cache


def _time_one(task) -> dict:
    from satisfiability.heuristics import upper_bound

    source_file, name, n, m, matrix = task
    instance = MOSPInstance(matrix=np.array(matrix, dtype=np.int8),
                            n_customers=n, n_patterns=m, name=name)
    row = {"instance": name, "source_file": source_file, "n_customers": n}
    for strategy in _WORK["strategies"]:
        kwargs = {}
        if strategy in MODEL_STRATEGIES:
            fold = _WORK["fold_of_file"][source_file]
            kwargs["model_path"] = str(_WORK["model_dir"] / f"fold{fold}.txt")
        started = time.perf_counter()
        value, _ = upper_bound(instance, strategy, **kwargs)
        row[f"ms:{strategy}"] = 1000.0 * (time.perf_counter() - started)
        row[f"value:{strategy}"] = value
    return row


def run_timing(strategies: Sequence[str] = STRATEGIES, workers: int = 16,
               limit: int | None = None, out: Path = OUT_DIR / "timing.csv"
               ) -> pd.DataFrame:
    """Every strategy on every instance in one worker, `perf_counter` around
    the call. Spawned workers: LightGBM has run in this process by the time
    the sweep stage is over (CLAUDE.md method note)."""
    manifest = json.loads((UNION_MODEL_DIR / "folds.json").read_text())
    pairs = enumerate_instances()
    if limit:
        pairs = pairs[:limit]
    tasks = [(str(path), inst.name, inst.n_customers, inst.n_patterns,
              inst.matrix.tolist()) for path, inst in pairs]
    ctx = multiprocessing.get_context("spawn")
    started = time.time()
    with ctx.Pool(workers, initializer=_init_timing,
                  initargs=(tuple(strategies), manifest["assignment"],
                            str(UNION_MODEL_DIR))) as pool:
        rows = pool.map(_time_one, tasks, chunksize=8)
    frame = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    print(f"timed {len(frame)} instances × {len(strategies)} strategies in "
          f"{time.time() - started:.0f}s -> {out}", flush=True)
    return frame


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------

def load_frame(strategies: Sequence[str] = STRATEGIES) -> pd.DataFrame:
    """One row per instance: optimum, each strategy's sweep value, its
    in-process value and milliseconds, size and collection."""
    frame: pd.DataFrame | None = None
    for strategy in strategies:
        data = json.loads(_sweep_path(strategy).read_text())
        part = pd.DataFrame(data["rows"]).rename(
            columns={"achieved": f"sweep:{strategy}",
                     "seconds": f"sweep_s:{strategy}"})
        if frame is None:
            frame = part
        else:
            part = part.drop(columns=["optimum"])
            frame = frame.merge(part, on="instance", how="inner", validate="1:1")
    assert frame is not None
    timing = pd.read_csv(OUT_DIR / "timing.csv")
    frame = frame.merge(timing, on="instance", how="inner", validate="1:1")
    canon = pd.read_csv(CANONICAL)[["instance_name", "collection", "graph_cert"]]
    frame = frame.merge(canon.rename(columns={"instance_name": "instance"}),
                        on="instance", how="left")
    return frame


def check_consistency(frame: pd.DataFrame, strategies: Sequence[str] = STRATEGIES
                      ) -> dict[str, int]:
    """Sweep value against in-process value, per strategy: the strategies are
    deterministic, so any difference is a harness bug."""
    return {s: int((frame[f"sweep:{s}"] != frame[f"value:{s}"]).sum())
            for s in strategies}


def summary_table(frame: pd.DataFrame, strategies: Sequence[str] = STRATEGIES
                  ) -> pd.DataFrame:
    rows = []
    for s in strategies:
        err = frame[f"sweep:{s}"] - frame["optimum"]
        ms = frame[f"ms:{s}"]
        rows.append({
            "strategy": s,
            "exact": float((err == 0).mean()),
            "mean overshoot": float(err.mean()),
            "worst": int(err.max()),
            "total overshoot": int(err.sum()),
            "misses": int((err > 0).sum()),
            "ms/instance (mean)": float(ms.mean()),
            "ms/instance (median)": float(ms.median()),
            "ms/instance (p90)": float(ms.quantile(0.9)),
            "below optimum": int((err < 0).sum()),
        })
    return pd.DataFrame(rows)


def head_to_head(frame: pd.DataFrame, pairs: Sequence[tuple[str, str]] = HEAD_TO_HEAD
                 ) -> pd.DataFrame:
    rows = []
    for first, second in pairs:
        a, b = frame[f"sweep:{first}"], frame[f"sweep:{second}"]
        rows.append({
            "first": first, "second": second,
            "better": int((a < b).sum()), "equal": int((a == b).sum()),
            "worse": int((a > b).sum()),
            "stacks saved": int((b - a)[a < b].sum()),
            "stacks lost": int((a - b)[a > b].sum()),
            "first exact where second misses": int(((a == frame["optimum"]) & (b > frame["optimum"])).sum()),
            "both miss": int(((a > frame["optimum"]) & (b > frame["optimum"])).sum()),
        })
    return pd.DataFrame(rows)


def by_band(frame: pd.DataFrame, strategies: Sequence[str] = STRATEGIES,
            bands=SIZE_BANDS) -> pd.DataFrame:
    rows = []
    for lo, hi in bands:
        sub = frame[(frame["n_customers"] >= lo) & (frame["n_customers"] <= hi)]
        row = {"customers": f"{lo}–{hi if hi < 200 else int(sub['n_customers'].max())}",
               "instances": len(sub)}
        for s in strategies:
            err = sub[f"sweep:{s}"] - sub["optimum"]
            row[f"{s} mean"] = float(err.mean())
            row[f"{s} exact"] = float((err == 0).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def by_collection(frame: pd.DataFrame, strategies: Sequence[str] = STRATEGIES
                  ) -> pd.DataFrame:
    rows = []
    for coll, sub in frame.groupby("collection"):
        row = {"collection": coll, "instances": len(sub)}
        for s in strategies:
            row[f"{s} mean"] = float((sub[f"sweep:{s}"] - sub["optimum"]).mean())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("instances", ascending=False)


def largest_differences(frame: pd.DataFrame, first: str, second: str, top: int = 8
                        ) -> pd.DataFrame:
    d = (frame[f"sweep:{second}"] - frame[f"sweep:{first}"])
    cols = ["instance", "n_customers", "optimum", f"sweep:{first}", f"sweep:{second}"]
    return frame.assign(diff=d).sort_values("diff", ascending=False).head(top)[cols + ["diff"]]


def _md(table: pd.DataFrame, floats: int = 3) -> str:
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.{floats}f}"
        return str(v)
    head = "| " + " | ".join(table.columns) + " |"
    sep = "|" + "---|" * len(table.columns)
    body = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in table.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def write_report(frame: pd.DataFrame, out: Path = TABLES) -> None:
    lines = ["# The two-key rule as the DFS seed, over the whole corpus",
             "", f"*Generated by `python -m learning.rule_seed --stage report` on "
             f"{time.strftime('%Y-%m-%d %H:%M')}. {len(frame)} instances, "
             f"{int(frame['n_customers'].min())}–{int(frame['n_customers'].max())} customers.*", ""]
    cons = check_consistency(frame)
    lines += ["## Consistency: sweep value ≠ in-process value", "",
              _md(pd.DataFrame([cons])), ""]
    lines += ["## Summary", "", _md(summary_table(frame)), ""]
    lines += ["## Head to head (first below / equal / above second)", "",
              _md(head_to_head(frame)), ""]
    lines += ["## By size band (mean overshoot, exact)", "", _md(by_band(frame)), ""]
    lines += ["## By collection (mean overshoot)", "", _md(by_collection(frame)), ""]
    for first, second in (("rule+cs-dfs", "cs-dfs"), ("rule+cs-dfs", "learned+cs-dfs"),
                          ("learned+cs-dfs", "rule+cs-dfs")):
        lines += [f"## Largest gains of `{first}` over `{second}`", "",
                  _md(largest_differences(frame, first, second)), ""]
    manifest = json.loads((OUT_DIR / "folds.json").read_text())
    counts = pd.Series(manifest["assignment"]).value_counts().sort_index()
    inst_per_fold = frame.assign(fold=frame["source_file"].map(manifest["assignment"])) \
        .groupby("fold").size()
    lines += ["## Union folds", "",
              _md(pd.DataFrame({"fold": counts.index, "files": counts.values,
                                "instances": [int(inst_per_fold.get(f, 0)) for f in counts.index]})), ""]
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nwrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=("all", "train", "sweep", "time", "report"),
                        default="all")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="redo existing sweeps")
    args = parser.parse_args()

    if args.stage in ("all", "train"):
        if (UNION_MODEL_DIR / "folds.json").exists() and not args.force:
            print(f"{UNION_MODEL_DIR}/folds.json exists, skipping training")
        else:
            train_union_folds()
    if args.stage in ("all", "sweep"):
        run_sweeps(workers=args.workers, limit=args.limit, force=args.force)
    if args.stage in ("all", "time"):
        run_timing(workers=args.workers, limit=args.limit)
    if args.stage in ("all", "report"):
        write_report(load_frame())


if __name__ == "__main__":
    main()
