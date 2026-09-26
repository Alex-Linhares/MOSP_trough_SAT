"""Generated ensembles G(n, m, p): the campaign infrastructure, and its pilot.

The question this module serves (`reports/ml_nature_plan.md` §3 phase 3, §2.4,
§2.5, §2.9): the certified corpus is a lattice of 74 `(n, m)` cells whose
density is confounded with the collection that generated it
(`reports/ml_nature.md` §2), so nothing in it can vary density at fixed size.
This module fills the space with ensembles it controls, so that the hardness
of the refutation and the value of the optimum can be measured as functions
of `(n, m, p)` -- or of `(n, m, d)` -- rather than of the benchmark author.

Two generators, both from `benchmarks.generator`:

- **bernoulli** -- `generate_random_instance`: each entry 1 with probability
  `p`, independently; empty rows and columns are given one entry. This is the
  random intersection graph `G(n, m, p)` of the plan's §0.
- **fixed** -- `generate_structured_instance`: every product has exactly `d`
  customers, which loop0001 §2 showed is what Chu & Stuckey's density class
  means (`col_mean` equals `d` to within rounding).

Every instance is a pure function of `(generator, n, m, param, index)`: the
seed is a CRC of the cell identifier and the index, so a cell regenerates byte
for byte from its parameters and nothing has to be stored to reproduce it
(`tests/test_ensemble.py` checks this). So the instance store is the
**manifest** `learning/data/ensemble/manifest.csv` -- one line per instance
with its parameters, seed and matrix digest, checked by `--verify-manifest` --
rather than 8,000 `.mosp` files (`--write-instances` writes them under
`learning/data/ensemble/instances/` when a file on disk is wanted). The
witnesses are stored under `learning/data/ensemble/solutions/` through
`solve_mosp_exact` with that directory as `solutions_dir` -- never `None`,
never the corpus directory.

For each instance one row of `learning/data/ensemble/results.csv` records:

- the generator parameters and the seed;
- `optimum`, how it was proved (`solve_proof`), the descent's node count and
  seconds, and whether the witness re-simulates to the value (`witness_ok`);
- nodes, seconds and status to refute `optimum - 1` under both configurations
  of `learning.node_counts` (`default`, `csearch`), as `nodes_default`,
  `nodes_csearch` and so on -- one row per instance, the configuration in the
  column name;
- all 49 features of `learning.features` (`lb_best`, `ub_cs_dfs`,
  `tw_min_fill`, `bw_rcm`, `g_degeneracy` and `g_components` among them);
- the isomorphism certificates of `learning.canonical` (`graph_cert` for the
  MOSP graph, `bipartite_cert` for the matrix), so that every downstream count
  can be deduplicated by class, and `complete_graph`.

Decomposable instances (`g_components > 1`) are kept and recorded, not
discarded: Chu & Stuckey discard them from their generator's output, which is
why the corpus has none at the hard sizes and why this campaign has to say how
many there are per cell.

The run is resumable -- rows already in the CSV are skipped -- and appends as
it goes, so an interrupted run keeps what it finished.

Usage:
    python -m learning.ensemble --pilot                 # the §9 pilot, 16 workers
    python -m learning.ensemble --pilot --extension     # plus m = 2n and lower densities
    python -m learning.ensemble --tables-only           # tables again from the CSV
    python -m learning.ensemble --tables-only --verify-manifest 0   # every instance regenerates
    python -m learning.ensemble --cells f:20:20:2 b:20:40:0.1 --per-cell 50
    python -m learning.ensemble --item02                # the §10 campaign: 252 cells x 150

Nothing here is a bound, nothing touches `_lower_bound` or any solver default,
and nothing is written to `solutions/`.
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks.generator import generate_random_instance, generate_structured_instance
from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
INSTANCE_DIR = ENSEMBLE_DIR / "instances"
SOLUTIONS_DIR = ENSEMBLE_DIR / "solutions"
RESULTS_CSV = ENSEMBLE_DIR / "results.csv"
DEFAULT_OUT = Path("reports/ensemble_tables.md")

GENERATORS = ("bernoulli", "fixed")
CONFIGS = ("default", "csearch")

# The pilot the item asked for: 10 per cell, m = n.
PILOT_N = (10, 20, 30, 40)
PILOT_D = (2, 3, 4, 6, 8)
PILOT_P = (0.05, 0.1, 0.2, 0.3)
PILOT_PER_CELL = 10

# The extension beyond the item's grid, so that item 02's budget covers m = 2n
# and the densities below Chu & Stuckey's 2 where §3 found nodes still rising.
EXTENSION_M_RATIOS = (2,)
EXTENSION_D = (2, 3, 4, 6, 8)
EXTENSION_P = (0.025, 0.05, 0.1, 0.2, 0.3)


# ----------------------------------------------------------------------------
# cells and generation
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Cell:
    """One point of the design: a generator, a size and a density parameter."""

    generator: str
    n: int
    m: int
    param: float

    def __post_init__(self) -> None:
        if self.generator not in GENERATORS:
            raise ValueError(f"generator must be one of {GENERATORS}, got {self.generator!r}")

    @property
    def id(self) -> str:
        tag = "p" if self.generator == "bernoulli" else "d"
        return f"{self.generator[0]}_n{self.n}_m{self.m}_{tag}{self.param:g}"

    @staticmethod
    def parse(text: str) -> "Cell":
        """`b:20:40:0.1` or `f:20:20:2`."""
        gen, n, m, param = text.split(":")
        generator = {"b": "bernoulli", "f": "fixed"}.get(gen, gen)
        return Cell(generator, int(n), int(m), float(param))


def cell_seed(cell: Cell, index: int) -> int:
    """The seed of the `index`-th instance of a cell: a CRC of its identity.

    Deterministic across machines and Python versions, and independent of the
    order in which cells are run, so that a cell can be regenerated alone.
    """
    return zlib.crc32(f"{cell.id}:{index}".encode()) & 0x7FFFFFFF


def instance_name(cell: Cell, index: int) -> str:
    return f"ens_{cell.id}_i{index:03d}"


def generate(cell: Cell, index: int) -> MOSPInstance:
    """The `index`-th instance of a cell, byte for byte the same every time."""
    seed = cell_seed(cell, index)
    name = instance_name(cell, index)
    if cell.generator == "bernoulli":
        return generate_random_instance(cell.n, cell.m, cell.param, seed=seed, name=name)
    return generate_structured_instance(cell.n, cell.m, int(cell.param), seed=seed, name=name)


def pilot_cells(sizes=PILOT_N, ds=PILOT_D, ps=PILOT_P, m_ratio: int = 1) -> list[Cell]:
    cells = []
    for n in sizes:
        m = m_ratio * n
        cells += [Cell("fixed", n, m, d) for d in ds if d <= n]
        cells += [Cell("bernoulli", n, m, p) for p in ps]
    return cells


def extension_cells(sizes=PILOT_N) -> list[Cell]:
    """m = 2n at every pilot density, and p = 0.025 at m = n: what the pilot
    grid does not cover but item 02's grid does."""
    cells = []
    for ratio in EXTENSION_M_RATIOS:
        cells += pilot_cells(sizes, EXTENSION_D, EXTENSION_P, m_ratio=ratio)
    cells += [Cell("bernoulli", n, n, p) for n in sizes for p in EXTENSION_P if p not in PILOT_P]
    return cells


# ----------------------------------------------------------------------------
# one instance
# ----------------------------------------------------------------------------


def analyse(instance: MOSPInstance, cell: Cell, index: int, solutions_dir: Path,
            deadline_seconds: float | None = 60.0,
            solve_budget: float | None = 600.0) -> dict:
    """Solve, verify, refute under both configurations, featurise, certify.

    `optimum` is a certified optimum when `certified` is true; when the solve
    budget ran out it is a verified upper bound and the refutation is skipped
    (`status_*` = `"uncertified"`). A refutation that returns `"sat"` would
    mean the solver's own optimum is wrong; that is recorded, never hidden.
    """
    from learning.canonical import canonical_record
    from learning.features import instance_features
    from learning.node_counts import refute
    from mosp.verify import max_open_stacks
    from satisfiability.mosp_solver import solve_mosp_exact

    started = time.monotonic()
    row: dict = {
        "instance_name": instance.name, "cell": cell.id,
        "generator": cell.generator, "n": cell.n, "m": cell.m,
        "param": cell.param, "index": index, "seed": cell_seed(cell, index),
    }

    stats: dict = {}
    t0 = time.monotonic()
    value, ordering = solve_mosp_exact(instance, solutions_dir=solutions_dir,
                                       time_budget=solve_budget, stats=stats)
    row["solve_seconds"] = round(time.monotonic() - t0, 4)
    row["optimum"] = int(value)
    row["solve_nodes"] = stats.get("nodes")
    row["solve_proof"] = stats.get("proof", "")
    row["certified"] = stats.get("proof") in ("refutation", "bound", "cached")
    row["witness_ok"] = int(max_open_stacks(instance, list(ordering))) == int(value)

    for config in CONFIGS:
        if not row["certified"]:
            result = {"status": "uncertified", "nodes": None, "seconds": None}
        elif value <= 1:
            result = {"status": "trivial", "nodes": 0, "seconds": 0.0}
        else:
            result = refute(instance, int(value), config, deadline_seconds)
        row[f"status_{config}"] = result["status"]
        row[f"nodes_{config}"] = result["nodes"]
        row[f"seconds_{config}"] = result["seconds"]

    t0 = time.monotonic()
    row.update(instance_features(instance))
    row["feature_seconds"] = round(time.monotonic() - t0, 4)

    canon = canonical_record(instance)
    for key in ("matrix_digest", "graph_cert", "bipartite_cert", "wl_hash", "aut_order"):
        row[key] = canon[key]
    row["complete_graph"] = canon["g_edges"] == cell.n * (cell.n - 1) // 2
    row["total_seconds"] = round(time.monotonic() - started, 4)
    return row


def _job(args) -> dict:
    cell, index, instance_dir, solutions_dir, deadline, solve_budget = args
    instance = generate(cell, index)
    if instance_dir is not None:
        instance_dir.mkdir(parents=True, exist_ok=True)
        instance.to_file(instance_dir / f"{instance.name}.mosp")
    return analyse(instance, cell, index, solutions_dir, deadline, solve_budget)


# ----------------------------------------------------------------------------
# the run
# ----------------------------------------------------------------------------


MANIFEST_COLUMNS = ["instance_name", "cell", "generator", "n", "m", "param", "index",
                    "seed", "matrix_digest"]


def write_manifest(frame: pd.DataFrame, path: Path = ENSEMBLE_DIR / "manifest.csv") -> Path:
    """The table every instance regenerates from, byte for byte, through
    `generate(Cell(generator, n, m, param), index)`; `matrix_digest` is the
    check. Small enough to commit when the `.mosp` files are not."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame[MANIFEST_COLUMNS].sort_values("instance_name").to_csv(path, index=False)
    return path


def verify_manifest(path: Path = ENSEMBLE_DIR / "manifest.csv",
                    sample: int | None = None, seed: int = 0) -> dict[str, int]:
    """Regenerate every manifest row (or a sample) and compare matrix digests."""
    from learning.canonical import matrix_digest

    manifest = pd.read_csv(path)
    if sample is not None and sample < len(manifest):
        manifest = manifest.sample(sample, random_state=seed)
    mismatches = 0
    for row in manifest.itertuples(index=False):
        cell = Cell(row.generator, int(row.n), int(row.m), float(row.param))
        inst = generate(cell, int(row.index))
        if inst.name != row.instance_name or matrix_digest(inst) != row.matrix_digest:
            mismatches += 1
    return {"checked": len(manifest), "mismatches": mismatches}


def load_results(csv: Path = RESULTS_CSV) -> pd.DataFrame:
    if not csv.exists():
        return pd.DataFrame()
    return pd.read_csv(csv)


def run(cells: list[Cell], per_cell: int, workers: int = 16,
        csv: Path = RESULTS_CSV, instance_dir: Path | None = INSTANCE_DIR,
        solutions_dir: Path = SOLUTIONS_DIR, deadline: float | None = 60.0,
        solve_budget: float | None = 600.0, verbose: bool = True) -> pd.DataFrame:
    """Solve every `(cell, index)` not yet in the CSV; append as rows finish."""
    existing = load_results(csv)
    done = set(existing["instance_name"]) if len(existing) else set()
    cells = list(dict.fromkeys(cells))          # a cell named twice runs once
    jobs = [(cell, i, instance_dir, solutions_dir, deadline, solve_budget)
            for cell in cells for i in range(per_cell)
            if instance_name(cell, i) not in done]
    if verbose:
        print(f"{len(cells)} cells x {per_cell} = {len(cells) * per_cell} instances, "
              f"{len(done)} already in {csv}, {len(jobs)} to run on {workers} workers",
              flush=True)
    if not jobs:
        return existing
    solutions_dir.mkdir(parents=True, exist_ok=True)
    csv.parent.mkdir(parents=True, exist_ok=True)

    columns = list(existing.columns) if len(existing) else None
    started = time.time()
    finished = 0

    def _flush(rows: list[dict]) -> None:
        nonlocal columns
        frame = pd.DataFrame(rows)
        if columns is None:
            columns = list(frame.columns)
        frame = frame.reindex(columns=columns)
        frame.to_csv(csv, mode="a", header=not csv.exists() or csv.stat().st_size == 0,
                     index=False, float_format="%.6g")

    buffer: list[dict] = []
    if workers <= 1:
        results = map(_job, jobs)
        for row in results:
            buffer.append(row)
            finished += 1
            if len(buffer) >= 20:
                _flush(buffer)
                buffer = []
    else:
        with multiprocessing.Pool(workers) as pool:
            for row in pool.imap_unordered(_job, jobs, chunksize=1):
                buffer.append(row)
                finished += 1
                if len(buffer) >= 20:
                    _flush(buffer)
                    buffer = []
                    if verbose and finished % 100 == 0:
                        print(f"  {finished}/{len(jobs)} in {time.time() - started:.0f} s",
                              flush=True)
    if buffer:
        _flush(buffer)
    if verbose:
        print(f"  {finished} rows in {time.time() - started:.0f} s", flush=True)
    return load_results(csv)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def dedupe(frame: pd.DataFrame) -> pd.DataFrame:
    """One row per MOSP-graph isomorphism class within a cell (first seen)."""
    key = "graph_cert" if frame["graph_cert"].notna().all() else "wl_hash"
    return frame.drop_duplicates(subset=["cell", key], keep="first")


def _cell_order(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.sort_values(["generator", "n", "m", "param"], ascending=[False, True, True, True])


def cost_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per cell: how many, how many distinct graphs, complete, decomposable,
    certified, the optimum's spread, and the cost in seconds and nodes."""
    rows = []
    for cell, g in frame.groupby("cell", sort=False):
        first = g.iloc[0]
        nodes = g["nodes_default"].astype(float)
        rows.append({
            "cell": cell, "generator": first["generator"], "n": int(first["n"]),
            "m": int(first["m"]), "param": float(first["param"]),
            "instances": len(g),
            "classes": int(g["graph_cert"].nunique()),
            "complete": int(g["complete_graph"].sum()),
            "decomposable": int((g["g_components"] > 1).sum()),
            "certified": int(g["certified"].sum()),
            "refuted": int((g["status_default"] == "unsat").sum()),
            "opt_mean": round(float(g["optimum"].mean()), 2),
            "opt_std": round(float(g["optimum"].std(ddof=0)), 2),
            "sec_median": round(float(g["total_seconds"].median()), 3),
            "sec_max": round(float(g["total_seconds"].max()), 3),
            "sec_sum": round(float(g["total_seconds"].sum()), 2),
            "nodes_median": float(nodes.median()),
            "nodes_p90": float(nodes.quantile(0.9)),
            "nodes_max": float(nodes.max()),
        })
    return _cell_order(pd.DataFrame(rows))


def cost_by_size(frame: pd.DataFrame) -> pd.DataFrame:
    """Per `(generator, n, m)`: seconds per instance, and the worst cell."""
    rows = []
    for (gen, n, m), g in frame.groupby(["generator", "n", "m"]):
        worst = g.groupby("cell")["total_seconds"].sum().idxmax()
        rows.append({
            "generator": gen, "n": int(n), "m": int(m), "instances": len(g),
            "sec_mean": round(float(g["total_seconds"].mean()), 3),
            "sec_p90": round(float(g["total_seconds"].quantile(0.9)), 3),
            "sec_max": round(float(g["total_seconds"].max()), 3),
            "nodes_median": float(g["nodes_default"].median()),
            "nodes_max": float(g["nodes_default"].max()),
            "worst_cell": worst,
        })
    return pd.DataFrame(rows).sort_values(["generator", "n", "m"], ascending=[False, True, True])


def config_ratio(frame: pd.DataFrame) -> pd.DataFrame:
    """The `csearch` configuration against `decide` defaults, per size."""
    rows = []
    both = frame.dropna(subset=["nodes_default", "nodes_csearch"])
    for n, g in both.groupby("n"):
        ratio = g["nodes_csearch"] / g["nodes_default"].clip(lower=1)
        rows.append({
            "n": int(n), "instances": len(g),
            "csearch_fewer": int((g["nodes_csearch"] < g["nodes_default"]).sum()),
            "equal": int((g["nodes_csearch"] == g["nodes_default"]).sum()),
            "csearch_more": int((g["nodes_csearch"] > g["nodes_default"]).sum()),
            "median_ratio": round(float(ratio.median()), 3),
        })
    return pd.DataFrame(rows)


def audit(frame: pd.DataFrame) -> dict[str, int]:
    """Every witness re-simulates; every certified optimum refutes at optimum - 1
    under both configurations; every complete graph has optimum n."""
    certified = frame[frame["certified"].astype(bool)]
    out = {
        "instances": len(frame),
        "witness_ok": int(frame["witness_ok"].astype(bool).sum()),
        "certified": len(certified),
    }
    for config in CONFIGS:
        col = certified[f"status_{config}"]
        out[f"unsat_{config}"] = int((col == "unsat").sum())
        out[f"trivial_{config}"] = int((col == "trivial").sum())
        out[f"sat_{config}"] = int((col == "sat").sum())
        out[f"unknown_{config}"] = int((col == "unknown").sum())
    complete = frame[frame["complete_graph"].astype(bool)]
    out["complete_graphs"] = len(complete)
    out["complete_with_optimum_n"] = int((complete["optimum"] == complete["n"]).sum())
    return out


def affordable(frame: pd.DataFrame, cells: list[Cell], hours: float = 2.5,
               workers: int = 16, efficiency: float = 0.7) -> pd.DataFrame:
    """What item 02's grid costs at the pilot's per-instance rate.

    Each planned cell is costed at the mean `total_seconds` of the nearest
    pilot cell with the same generator and `m / n` ratio (nearest in `n`, then
    in the density parameter); cells at a ratio the pilot never ran fall back
    to the same `n` at ratio 1, and are marked. The answer is the number of
    instances per cell that fits the budget, assuming the budget is shared
    equally across cells.
    """
    pilot = frame.groupby("cell").agg(
        generator=("generator", "first"), n=("n", "first"), m=("m", "first"),
        param=("param", "first"), sec=("total_seconds", "mean")).reset_index()
    pilot["ratio"] = pilot["m"] / pilot["n"]
    rows = []
    for cell in cells:
        same = pilot[(pilot["generator"] == cell.generator)]
        ratio_match = same[np.isclose(same["ratio"], cell.m / cell.n)]
        fallback = ratio_match.empty
        if fallback:
            ratio_match = same
        dn = (ratio_match["n"] - cell.n).abs()
        nearest_n = ratio_match[dn == dn.min()]
        dp = (nearest_n["param"] - cell.param).abs()
        pick = nearest_n[dp == dp.min()].iloc[0]
        rows.append({"cell": cell.id, "generator": cell.generator, "n": cell.n,
                     "m": cell.m, "param": cell.param, "sec_per_instance": pick["sec"],
                     "costed_from": pick["cell"], "ratio_fallback": fallback})
    plan = pd.DataFrame(rows)
    budget = hours * 3600 * workers * efficiency
    plan["per_cell_affordable"] = int(budget / plan["sec_per_instance"].sum())
    plan.attrs["budget_core_seconds"] = budget
    return plan


ITEM02_N = (10, 15, 20, 25, 30, 35, 40)
ITEM02_M_RATIOS = (1, 2)
ITEM02_D = tuple(range(2, 11))
ITEM02_P = (0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5)
ITEM02_PER_CELL = 150


def item02_cells(sizes=ITEM02_N, ratios=ITEM02_M_RATIOS, ds=ITEM02_D, ps=ITEM02_P) -> list[Cell]:
    """The grid §9 chose for item 02: n in {10, 15, ..., 40}, m in {n, 2n},
    d 2..10 (only d <= n: d = n is already the complete graph in one class),
    p 0.025..0.5 -- below Chu & Stuckey's d = 2 and above the range where the
    graph is complete, so the campaign sees both edges. The pilot's 80 cells
    are a subset with the same seeds, so its 8,000 instances are reused."""
    cells = []
    for n in sizes:
        for ratio in ratios:
            m = ratio * n
            cells += [Cell("fixed", n, m, d) for d in ds if d <= n]
            cells += [Cell("bernoulli", n, m, p) for p in ps]
    return cells


# ----------------------------------------------------------------------------
# the campaign's descriptive tables (§10)
# ----------------------------------------------------------------------------


def campaign_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Per `(generator, n, m)`: cells, instances raw and per class, complete
    graphs, decomposable instances, certified, refuted, core-seconds."""
    rows = []
    for (gen, n, m), g in frame.groupby(["generator", "n", "m"]):
        classes = g.groupby("cell")["graph_cert"].nunique().sum()
        rows.append({
            "generator": gen, "n": int(n), "m": int(m),
            "cells": int(g["cell"].nunique()),
            "instances": len(g),
            "classes": int(classes),
            "complete": int(g["complete_graph"].astype(bool).sum()),
            "decomposable": int((g["g_components"] > 1).sum()),
            "certified": int(g["certified"].astype(bool).sum()),
            "refuted_both": int(((g["status_default"] == "unsat") | (g["status_default"] == "trivial")).sum()
                                if "status_default" in g else 0),
            "core_seconds": round(float(g["total_seconds"].sum()), 1),
        })
    return pd.DataFrame(rows).sort_values(["generator", "n", "m"], ascending=[False, True, True])


def density_matrix(frame: pd.DataFrame, generator: str, ratio: int,
                   quantity: str = "classes") -> pd.DataFrame:
    """Rows = density parameter, columns = n, for one generator and `m / n`.

    `quantity`: `classes` (distinct MOSP graphs / instances), `complete`
    (share of complete graphs), `decomposable` (share with more than one
    component), `optimum` (mean), `nodes` (median `nodes_default`).
    """
    sub = frame[(frame["generator"] == generator) & (frame["m"] == ratio * frame["n"])]
    table: dict[float, dict[int, str]] = {}
    for (param, n), g in sub.groupby(["param", "n"]):
        if quantity == "classes":
            value = f"{g['graph_cert'].nunique()}/{len(g)}"
        elif quantity == "complete":
            value = f"{100 * g['complete_graph'].astype(bool).mean():.0f}%"
        elif quantity == "decomposable":
            value = f"{100 * (g['g_components'] > 1).mean():.0f}%"
        elif quantity == "optimum":
            value = f"{g['optimum'].mean():.1f}"
        elif quantity == "nodes":
            value = f"{g['nodes_default'].median():.0f}"
        else:
            raise ValueError(quantity)
        table.setdefault(float(param), {})[int(n)] = value
    out = pd.DataFrame(table).T.sort_index()
    out = out.reindex(sorted(out.columns), axis=1)
    out.index.name = "p" if generator == "bernoulli" else "d"
    return out.fillna("·").reset_index()


def campaign_tables(frame: pd.DataFrame) -> str:
    dd = dedupe(frame)
    text = "### Campaign summary by size\n\n" + _md(campaign_summary(frame))
    text += (f"{len(frame)} instances in {frame['cell'].nunique()} cells; {len(dd)} distinct "
             f"MOSP graphs within their cells ({len(frame) - len(dd)} isomorphic repeats); "
             f"{frame['total_seconds'].sum() / 3600:.2f} core-hours.\n\n")
    for quantity, title in (("classes", "distinct MOSP graphs / instances"),
                            ("complete", "share of complete graphs"),
                            ("decomposable", "share with more than one component")):
        for generator in GENERATORS:
            for ratio in sorted({int(round(m / n)) for n, m in
                                 frame[frame["generator"] == generator][["n", "m"]].itertuples(index=False)}):
                text += f"### {title}: {generator}, m = {ratio}n\n\n"
                text += _md(density_matrix(frame, generator, ratio, quantity))
    return text


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt) + "\n\n"


def tables(frame: pd.DataFrame, hours: float = 2.5, workers: int = 16) -> str:
    text = ""
    a = audit(frame)
    text += "### Audit\n\n" + _md(pd.DataFrame({"check": list(a), "count": [str(v) for v in a.values()]}))
    text += "### Cost per cell (seconds are solve + both refutations + features)\n\n"
    text += _md(cost_table(frame))
    dd = dedupe(frame)
    text += (f"### Per class\n\n{len(frame)} instances, {len(dd)} distinct MOSP graphs "
             f"within their cells ({len(frame) - len(dd)} isomorphic repeats).\n\n")
    text += campaign_tables(frame)
    text += "### Cost by size\n\n" + _md(cost_by_size(frame))
    text += "### The two configurations\n\n" + _md(config_ratio(frame))
    plan = affordable(frame, item02_cells(), hours, workers)
    by_size = plan.groupby(["generator", "n", "m"]).agg(
        cells=("cell", "count"), sec_per_instance_sum=("sec_per_instance", "sum"),
        ratio_fallback=("ratio_fallback", "any")).reset_index()
    text += (f"### Item 02 grid costed at the pilot's rates\n\n{len(plan)} cells; "
             f"budget {plan.attrs['budget_core_seconds']:.0f} core-seconds "
             f"({hours} h x {workers} workers x 0.7); "
             f"sum of per-instance seconds over cells "
             f"{plan['sec_per_instance'].sum():.2f} s; "
             f"**affordable per cell: {int(plan['per_cell_affordable'].iloc[0])}**.\n\n")
    text += _md(by_size)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pilot", action="store_true", help="run the §9 pilot cells")
    parser.add_argument("--extension", action="store_true",
                        help="also m = 2n and p = 0.025 cells")
    parser.add_argument("--item02", action="store_true",
                        help="the §10 campaign grid: 252 cells, 150 per cell unless --per-cell")
    parser.add_argument("--cells", nargs="*", default=[],
                        help="cells as gen:n:m:param, e.g. f:20:20:2 b:20:40:0.1")
    parser.add_argument("--per-cell", type=int, default=PILOT_PER_CELL)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--deadline", type=float, default=60.0,
                        help="seconds per refutation before 'unknown'")
    parser.add_argument("--solve-budget", type=float, default=600.0,
                        help="seconds for the descent before the value is an upper bound")
    parser.add_argument("--csv", type=Path, default=RESULTS_CSV)
    parser.add_argument("--write-instances", action="store_true",
                        help="also write .mosp files; by default the manifest is the "
                             "instance store, since every instance regenerates from it")
    parser.add_argument("--verify-manifest", type=int, default=None, metavar="N",
                        help="regenerate N manifest rows (0 = all) and check their digests")
    parser.add_argument("--tables-only", action="store_true")
    parser.add_argument("--hours", type=float, default=2.5)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    started = time.time()
    cells: list[Cell] = []
    if args.pilot:
        cells += pilot_cells()
    if args.extension:
        cells += extension_cells()
    if args.item02:
        cells += item02_cells()
        if args.per_cell == PILOT_PER_CELL:
            args.per_cell = ITEM02_PER_CELL
    cells += [Cell.parse(c) for c in args.cells]

    if args.tables_only or not cells:
        frame = load_results(args.csv)
    else:
        frame = run(cells, args.per_cell, args.workers, args.csv,
                    instance_dir=INSTANCE_DIR if args.write_instances else None,
                    deadline=args.deadline, solve_budget=args.solve_budget)
        write_manifest(frame)
    if frame.empty:
        print("no results")
        return
    if args.verify_manifest is not None:
        check = verify_manifest(sample=args.verify_manifest or None)
        print(f"manifest: {check['checked']} regenerated, {check['mismatches']} mismatches")

    text = (f"# Generated ensembles: campaign tables\n\n"
            f"*Regenerated {time.strftime('%Y-%m-%d %H:%M')} by "
            f"`python -m learning.ensemble{' --pilot' if args.pilot else ''}"
            f"{' --extension' if args.extension else ''}"
            f"{' --item02' if args.item02 else ''}"
            f"{' --tables-only' if args.tables_only else ''}`; "
            f"{len(frame)} rows in {args.csv}, {time.time() - started:.0f} s.*\n\n")
    text += tables(frame, args.hours, args.workers)
    print(text)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
