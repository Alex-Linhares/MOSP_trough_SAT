"""Fan order: does breaking cost ties by remaining degree change what the search costs?

Plan 2 §2.5(a) (`reports/ml_nature_plan_2.md`), loop0003 item 06. Section 20
of `reports/ml_nature.md`.

**The question.** Both the complete customer search (`customer_search.decide`,
Python and C) and Chu & Stuckey's restricted DFS (`heuristics.restricted_dfs`,
the `cs-dfs` upper bound) expand candidates cheapest first and break ties by
customer index -- an accident of labelling that §13 showed moves the node
count by up to 2.3× (`default`) and 8× (`csearch`). §7 found that the rule
*close the customer that opens the fewest new stacks; on ties, the one with
the most unclosed neighbours* is the best one-sentence greedy on record and
that its first key is already the DFS's fan order. The conjecture is that its
second key -- highest remaining degree first -- is the fan order the search
should use. This module measures it, in nodes, paired per instance.

**The flag.** `decide(..., fan_order="degree")` and
`restricted_dfs(..., fan_order="degree")` (registered as `cs-dfs+degree`).
Both default to `"index"`, today's behaviour; the C implements the same order
through a new entry point (`cs_decide_fan`) so a process that loaded the
library before the flag existed keeps calling what it always called. A fan
order changes which branches are visited first and never which are visited:
the cost cut, the memo and every dominance rule are properties of the state.
So the *status* of every decision must be identical under both orders, and
that is checked here on every call, item 01's harness protocol reused
(`decide(optimum - 1)` and `decide(optimum)`, both configurations, witness
simulated). The default arm is also compared, node for node, with the counts
recorded before the flag existed (`results.csv`, `results_upward.csv`,
`scale_nodes.csv`, `node_counts.csv`): a byte-for-byte check that the default
path is unchanged, over every instance in the study.

**The measurement.** For every certified campaign instance at 10-75 customers
(`results.csv`, `results_upward.csv`) and every certified corpus instance at
9-100, under both configurations (`default`; `csearch` = Theorem 2 on where
`sparse_enough_for_better_move`), `decide(optimum - 1)` (the refutation) and
`decide(optimum)` (the witness search) under each fan order, deadline per
call; and `restricted_dfs` under each fan order, with its default MCN seed and
200,000-node budget. The paired statistic is `(nodes_degree + 1) /
(nodes_index + 1)`; a censored call (`unknown`) is a lower bound and the pair
is reported but not pooled into medians. **Kill** (plan 2 §2.5a): if the paired
median is within ±5% at every size, the fan order does not matter.

Run:
    python -m learning.fan_order --workers 16                # the study, ~30 min
    python -m learning.fan_order --stage tables              # tables from the CSV
    python -m learning.fan_order --source campaign --limit 300 --workers 8

Writes `learning/data/ensemble/fan_order.csv.gz` (one wide row per instance:
status, nodes and seconds of all eight decision calls and both DFS values;
committed) and `reports/fan_order_tables.md`. Nothing is written to
`solutions/`; no default is changed.
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR
from learning.node_counts import CONFIGS, certified_targets, refutation_kwargs
from mosp.instance import MOSPInstance
from satisfiability.heuristics import FAN_ORDERS

ENSEMBLE_DIR = Path("learning/data/ensemble")
RESULTS_CSV = ENSEMBLE_DIR / "results.csv"
RESULTS_UPWARD_CSV = ENSEMBLE_DIR / "results_upward.csv"
SCALE_NODES_CSV = ENSEMBLE_DIR / "scale_nodes.csv"
NODE_COUNTS_CSV = Path("learning/data/node_counts.csv")
ROWS_CSV = ENSEMBLE_DIR / "fan_order.csv.gz"
PARTIAL_CSV = Path("learning/data/fan_order_partial.csv")
TABLES = Path("reports/fan_order_tables.md")

SIDES = ("lo", "hi")                       # decide(optimum - 1), decide(optimum)
CAMPAIGN_MAX_N = 75
CORPUS_MAX_N = 100
CAMPAIGN_DEADLINE = 60.0
CORPUS_DEADLINE = 120.0
KILL_PCT = 5.0
DENSITY_BINS = ((0, 2), (2, 3), (3, 4), (4, 6), (6, 10), (10, 1e9))
DFS_MAX_NODES = 200_000


# ----------------------------------------------------------------------------
# targets
# ----------------------------------------------------------------------------


def campaign_targets(max_n: int = CAMPAIGN_MAX_N, limit: int | None = None,
                     results_csv: Path = RESULTS_CSV,
                     upward_csv: Path = RESULTS_UPWARD_CSV) -> list[dict]:
    """Every certified campaign instance at `n <= max_n`, with the recorded
    `default` refutation count (the byte-for-byte reference) and `ub_cs_dfs`."""
    frames = [pd.read_csv(p, low_memory=False) for p in (results_csv, upward_csv) if p.exists()]
    if not frames:
        return []
    frame = pd.concat(frames, ignore_index=True)
    frame = frame[frame.certified.astype(bool) & (frame.n <= max_n)]
    cols = ["instance_name", "cell", "generator", "n", "m", "param", "index", "optimum",
            "matrix_digest"]
    jobs = []
    for row in frame.to_dict("records"):
        job = {"source": "campaign", **{c: row[c] for c in cols}}
        job.update(col_mean=float(row.get("col_mean", np.nan)),
                   graph_cert=row.get("graph_cert", ""),
                   ref_nodes_default=float(row.get("nodes_default", np.nan)),
                   ref_status_default=row.get("status_default", ""),
                   ref_ub_cs_dfs=float(row.get("ub_cs_dfs", np.nan)))
        jobs.append(job)
    return jobs[:limit] if limit is not None else jobs


def corpus_targets(max_n: int = CORPUS_MAX_N, limit: int | None = None,
                   instance_dir: Path = DEFAULT_INSTANCE_DIR,
                   solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
                   scale_nodes_csv: Path = SCALE_NODES_CSV,
                   node_counts_csv: Path = NODE_COUNTS_CSV) -> list[dict]:
    """Every certified corpus instance at `n <= max_n`, with the recorded
    `default` count where §3 (n ≤ 40) or §14 (50-125) recorded one."""
    known: dict[str, tuple[float, str]] = {}
    for path in (node_counts_csv, scale_nodes_csv):
        if path.exists():
            s = pd.read_csv(path)
            s = s[s.config == "default"]
            for name, nodes, status in zip(s.instance_name, s.nodes, s.status):
                known[name] = (float(nodes), str(status))
    jobs = []
    for matrix, name, source_file, collection, optimum, _ in certified_targets(
            instance_dir, solutions_dir, max_n):
        arr = np.asarray(matrix)
        ref = known.get(name, (np.nan, ""))
        jobs.append({"source": "corpus", "instance_name": name, "matrix": matrix,
                     "source_file": source_file, "collection": collection,
                     "cell": collection, "n": int(arr.shape[0]), "m": int(arr.shape[1]),
                     "optimum": int(optimum),
                     "col_mean": float(arr.sum() / max(arr.shape[1], 1)),
                     "graph_cert": "", "ref_nodes_default": ref[0],
                     "ref_status_default": ref[1], "ref_ub_cs_dfs": np.nan})
    return jobs[:limit] if limit is not None else jobs


def _materialise(job: dict) -> MOSPInstance:
    from learning.differential import _materialise

    return _materialise(job)


# ----------------------------------------------------------------------------
# one instance
# ----------------------------------------------------------------------------


def _call(instance: MOSPInstance, k: int, config: str, fan_order: str,
          deadline_seconds: float | None) -> tuple[str, int, float, list[int] | None]:
    from satisfiability.customer_search import decide

    kwargs = refutation_kwargs(instance, config)
    deadline = None if deadline_seconds is None else time.monotonic() + deadline_seconds
    started = time.monotonic()
    answer = decide(instance, k, deadline=deadline, fan_order=fan_order, **kwargs)
    return answer.status, int(answer.nodes), round(time.monotonic() - started, 4), answer.order


def measure(instance: MOSPInstance, optimum: int, deadline_seconds: float | None = None,
            configs: tuple[str, ...] = CONFIGS, fan_orders: tuple[str, ...] = FAN_ORDERS,
            dfs: bool = True, dfs_max_nodes: int = DFS_MAX_NODES) -> dict:
    """Every call on one instance, as one wide row.

    Columns `{status,nodes,seconds}_{lo,hi}_{config}_{fan}`, plus
    `witness_{config}_{fan}` (the simulated value of the `hi` witness; must be
    at most `optimum`) and `dfs_{fan}` (the `restricted_dfs` value under each
    fan order). An `optimum` of 1 has nothing to refute: `lo` is `trivial`.
    """
    from learning.differential import witness_value
    from satisfiability.customer_search import sparse_enough_for_better_move
    from satisfiability.heuristics import restricted_dfs

    row: dict = {"optimum": optimum,
                 "better_move": bool(sparse_enough_for_better_move(instance))}
    for config in configs:
        for fan in fan_orders:
            tag = f"{config}_{fan}"
            if optimum <= 1:
                row.update({f"status_lo_{tag}": "trivial", f"nodes_lo_{tag}": 0,
                            f"seconds_lo_{tag}": 0.0})
            else:
                status, nodes, seconds, _ = _call(instance, optimum - 1, config, fan, deadline_seconds)
                row.update({f"status_lo_{tag}": status, f"nodes_lo_{tag}": nodes,
                            f"seconds_lo_{tag}": seconds})
            status, nodes, seconds, order = _call(instance, optimum, config, fan, deadline_seconds)
            value = witness_value(instance, order) if status == "sat" else None
            row.update({f"status_hi_{tag}": status, f"nodes_hi_{tag}": nodes,
                        f"seconds_hi_{tag}": seconds, f"witness_{tag}": value})
    if dfs:
        for fan in fan_orders:
            started = time.monotonic()
            value, _ = restricted_dfs(instance, max_nodes=dfs_max_nodes, fan_order=fan)
            row[f"dfs_{fan}"] = int(value)
            row[f"dfs_seconds_{fan}"] = round(time.monotonic() - started, 4)
    return row


def _job(args) -> dict:
    job, deadline = args
    instance = _materialise(job)
    started = time.monotonic()
    row = {k: job[k] for k in ("source", "instance_name", "cell", "n", "m", "optimum",
                               "col_mean", "graph_cert", "ref_nodes_default",
                               "ref_status_default", "ref_ub_cs_dfs")}
    row["source_file"] = job.get("source_file", "")
    row["deadline"] = deadline
    row.update(measure(instance, int(job["optimum"]), deadline))
    row["seconds_total"] = round(time.monotonic() - started, 3)
    return row


def run(jobs: list[dict], workers: int = 16, partial: Path = PARTIAL_CSV,
        rows_csv: Path = ROWS_CSV, progress_every: int = 500) -> pd.DataFrame:
    """Every job on the pool, heaviest recorded refutation first, rows flushed
    to `partial` as they land; then the compressed wide table."""
    def _weight(job: dict) -> float:
        w = job.get("ref_nodes_default", np.nan)
        return -float(w) if w == w else -float(job["n"]) * 1e3

    order = sorted(jobs, key=_weight)
    args = [(job, CORPUS_DEADLINE if job["source"] == "corpus" and job["n"] > 40
             else CAMPAIGN_DEADLINE) for job in order]
    partial.parent.mkdir(parents=True, exist_ok=True)
    if partial.exists():
        partial.unlink()
    buffer: list[dict] = []
    done = 0
    started = time.time()
    header = [False]

    def _flush() -> None:
        if buffer:
            pd.DataFrame(buffer).to_csv(partial, mode="a", header=not header[0], index=False)
            header[0] = True
            buffer.clear()

    def _consume(row: dict) -> None:
        nonlocal done
        buffer.append(row)
        done += 1
        if done % progress_every == 0 or done <= 20:
            _flush()
            if done % progress_every == 0 or done == 20:
                print(f"  {done}/{len(args)} instances, {time.time() - started:.0f} s", flush=True)

    if workers <= 1:
        for a in args:
            _consume(_job(a))
    else:
        with multiprocessing.Pool(workers) as pool:
            for row in pool.imap_unordered(_job, args, chunksize=1):
                _consume(row)
    _flush()
    frame = pd.read_csv(partial) if partial.exists() else pd.DataFrame()
    rows_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(rows_csv, index=False, compression="gzip")
    return frame


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def band(n: int, source: str) -> str:
    if source == "campaign":
        return f"campaign {int(n)}"
    if n <= 20:
        return "corpus 9–20"
    if n <= 40:
        return "corpus 21–40"
    if n <= 60:
        return "corpus 41–60"
    if n <= 82:
        return "corpus 61–82"
    return "corpus 99–100"


BAND_ORDER = [f"campaign {n}" for n in (10, 15, 20, 25, 30, 35, 40, 50, 60, 75)] + [
    "corpus 9–20", "corpus 21–40", "corpus 41–60", "corpus 61–82", "corpus 99–100"]


def density_band(col_mean: float) -> str:
    for lo, hi in DENSITY_BINS:
        if lo <= col_mean < hi:
            return f"{lo}–{hi:g}" if hi < 1e8 else f"≥ {lo}"
    return "?"


def _paired(rows: pd.DataFrame, side: str, config: str) -> pd.DataFrame:
    """Per-instance ratio for one side and configuration, decided pairs only."""
    a = rows[f"nodes_{side}_{config}_index"].astype(float)
    b = rows[f"nodes_{side}_{config}_degree"].astype(float)
    sa = rows[f"status_{side}_{config}_index"]
    sb = rows[f"status_{side}_{config}_degree"]
    decided = sa.isin(["sat", "unsat"]) & sb.isin(["sat", "unsat"])
    out = rows[["source", "instance_name", "n", "col_mean", "cell"]].copy()
    out["nodes_index"] = a
    out["nodes_degree"] = b
    out["decided"] = decided
    out["ratio"] = (b + 1) / (a + 1)
    out["log_ratio"] = np.log10(out["ratio"])
    out["band"] = [band(n, s) for n, s in zip(out.n, out.source)]
    out["density_band"] = out["col_mean"].map(density_band)
    return out


def _summarise_group(g: pd.DataFrame) -> pd.Series:
    d = g[g.decided]
    r = d["ratio"]
    return pd.Series({
        "instances": len(g),
        "paired": len(d),
        "censored": int((~g.decided).sum()),
        "fewer": int((d.nodes_degree < d.nodes_index).sum()),
        "equal": int((d.nodes_degree == d.nodes_index).sum()),
        "more": int((d.nodes_degree > d.nodes_index).sum()),
        "median_ratio": float(r.median()) if len(d) else np.nan,
        "p10": float(r.quantile(0.1)) if len(d) else np.nan,
        "p90": float(r.quantile(0.9)) if len(d) else np.nan,
        "geo_mean": float(10 ** d.log_ratio.mean()) if len(d) else np.nan,
        "total_ratio": (float((d.nodes_degree.sum() + 1) / (d.nodes_index.sum() + 1))
                        if len(d) else np.nan),
        "median_index": float(d.nodes_index.median()) if len(d) else np.nan,
    })


def paired_table(rows: pd.DataFrame, side: str, config: str, by: str = "band",
                 min_group: int = 1) -> pd.DataFrame:
    """Paired node ratio `(degree + 1) / (index + 1)` grouped by `by`."""
    p = _paired(rows, side, config)
    table = (p.groupby(by, sort=False).apply(_summarise_group, include_groups=False)
             .reset_index())
    table = table[table.instances >= min_group]
    if by == "band":
        table["_o"] = table[by].map({b: i for i, b in enumerate(BAND_ORDER)})
        table = table.sort_values("_o").drop(columns="_o")
    for c in ("instances", "paired", "censored", "fewer", "equal", "more"):
        table[c] = table[c].astype(int)
    return table.reset_index(drop=True)


def density_table(rows: pd.DataFrame, side: str, config: str, min_n: int = 30) -> pd.DataFrame:
    """Paired ratio by size and realised density (`col_mean`) at `n >= min_n`."""
    p = _paired(rows, side, config)
    p = p[p.n >= min_n]
    if len(p) == 0:
        return pd.DataFrame()
    p["density_lo"] = [next((lo for lo, hi in DENSITY_BINS if lo <= cm < hi), -1)
                       for cm in p.col_mean]
    table = (p.groupby(["band", "density_band", "density_lo"], sort=False)
             .apply(_summarise_group, include_groups=False).reset_index())
    table["_o"] = table["band"].map({b: i for i, b in enumerate(BAND_ORDER)})
    table = table.sort_values(["_o", "density_lo"]).drop(columns=["_o", "density_lo"])
    for c in ("instances", "paired", "censored", "fewer", "equal", "more"):
        table[c] = table[c].astype(int)
    return table.reset_index(drop=True)


def kill_verdict(rows: pd.DataFrame, side: str = "lo", pct: float = KILL_PCT,
                 min_paired: int = 20) -> dict:
    """Plan 2 §2.5a: met iff the paired median is within ±`pct`% at every size,
    for each configuration. Bands with fewer than `min_paired` decided pairs
    are listed but do not decide the verdict."""
    out: dict = {"side": side, "pct": pct}
    for config in CONFIGS:
        t = paired_table(rows, side, config)
        t = t[t.paired >= min_paired]
        dev = (t.median_ratio - 1.0).abs() * 100
        out[f"{config}_max_abs_pct"] = float(dev.max()) if len(t) else np.nan
        out[f"{config}_bands_outside"] = ";".join(
            f"{b} ({r:.3f})" for b, r, d in zip(t.band, t.median_ratio, dev) if d > pct)
        out[f"{config}_met"] = bool(len(t)) and bool((dev <= pct).all())
    out["met"] = all(out[f"{c}_met"] for c in CONFIGS)
    return out


def audit_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Statuses under the two fan orders must agree at both k, and the default
    arm must reproduce the recorded counts node for node."""
    out = []
    for config in CONFIGS:
        rec: dict = {"config": config, "instances": len(rows)}
        for side in SIDES:
            sa = rows[f"status_{side}_{config}_index"]
            sb = rows[f"status_{side}_{config}_degree"]
            both = sa.isin(["sat", "unsat"]) & sb.isin(["sat", "unsat"])
            rec[f"{side}_both_decided"] = int(both.sum())
            rec[f"{side}_status_disagreements"] = int((both & (sa != sb)).sum())
            rec[f"{side}_censored_index"] = int((sa == "unknown").sum())
            rec[f"{side}_censored_degree"] = int((sb == "unknown").sum())
        rec["lo_sat_(contradiction)"] = int(sum(
            (rows[f"status_lo_{config}_{f}"] == "sat").sum() for f in FAN_ORDERS))
        rec["hi_unsat_(contradiction)"] = int(sum(
            (rows[f"status_hi_{config}_{f}"] == "unsat").sum() for f in FAN_ORDERS))
        rec["witness_above_optimum"] = int(sum(
            (rows[f"witness_{config}_{f}"].astype(float) > rows.optimum).sum() for f in FAN_ORDERS))
        if config == "default":
            # `results_upward.csv` wrote its counts with six significant
            # digits (123072000 for 123072316), so a recorded count is matched
            # at its own precision as well as exactly.
            ref = rows.ref_nodes_default.astype(float)
            mine = rows.nodes_lo_default_index.astype(float)
            have = ref.notna() & (rows.ref_status_default == "unsat") & \
                (rows.status_lo_default_index == "unsat")
            six = lambda s: s.map(lambda x: float(f"{x:.6g}") if x == x else x)  # noqa: E731
            rec["ref_counts_available"] = int(have.sum())
            rec["ref_counts_equal"] = int((have & (ref == mine)).sum())
            rec["ref_counts_equal_6sig"] = int((have & (six(ref) == six(mine))).sum())
            rec["ref_counts_differ"] = int((have & (six(ref) != six(mine))).sum())
            dref = rows.ref_ub_cs_dfs.astype(float)
            hd = dref.notna()
            rec["ref_dfs_available"] = int(hd.sum())
            rec["ref_dfs_equal"] = int((hd & (dref == rows.dfs_index.astype(float))).sum())
        out.append(rec)
    table = pd.DataFrame(out)
    for c in table.columns:
        if c != "config":
            table[c] = table[c].astype("Int64")
    return table


def dfs_table(rows: pd.DataFrame) -> pd.DataFrame:
    """`restricted_dfs` over the optimum under each fan order, by band."""
    r = rows.copy()
    r["band"] = [band(n, s) for n, s in zip(r.n, r.source)]
    r["over_index"] = r.dfs_index - r.optimum
    r["over_degree"] = r.dfs_degree - r.optimum

    def _g(g: pd.DataFrame) -> pd.Series:
        return pd.Series({
            "instances": len(g),
            "exact_index": float((g.over_index == 0).mean()),
            "exact_degree": float((g.over_degree == 0).mean()),
            "mae_index": float(g.over_index.mean()),
            "mae_degree": float(g.over_degree.mean()),
            "worst_index": int(g.over_index.max()),
            "worst_degree": int(g.over_degree.max()),
            "degree_better": int((g.over_degree < g.over_index).sum()),
            "equal": int((g.over_degree == g.over_index).sum()),
            "degree_worse": int((g.over_degree > g.over_index).sum()),
            "ms_index": float(1e3 * g.dfs_seconds_index.mean()),
            "ms_degree": float(1e3 * g.dfs_seconds_degree.mean()),
        })

    table = r.groupby("band", sort=False).apply(_g, include_groups=False).reset_index()
    table["_o"] = table["band"].map({b: i for i, b in enumerate(BAND_ORDER)})
    table = table.sort_values("_o").drop(columns="_o")
    total = _g(r)
    total["band"] = "all"
    table = pd.concat([table, pd.DataFrame([total])], ignore_index=True)
    for c in ("instances", "worst_index", "worst_degree", "degree_better", "equal", "degree_worse"):
        table[c] = table[c].astype(int)
    return table


def movers_table(rows: pd.DataFrame, side: str, config: str, min_n: int = 50,
                 top: int = 12) -> pd.DataFrame:
    """Cells / classes with the largest and smallest median ratios at `n >= min_n`."""
    p = _paired(rows, side, config)
    p = p[(p.n >= min_n) & p.decided]
    if len(p) == 0:
        return pd.DataFrame()
    p["group"] = np.where(p.source == "campaign", p.cell,
                          p.instance_name.str.replace(r"-\d+_\d+$", "", regex=True))
    t = (p.groupby("group").apply(_summarise_group, include_groups=False).reset_index())
    t = t[t.paired >= 5].sort_values("median_ratio")
    for c in ("instances", "paired", "censored", "fewer", "equal", "more"):
        t[c] = t[c].astype(int)
    return pd.concat([t.head(top), t.tail(top)]).drop_duplicates("group").reset_index(drop=True)


def censored_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Every call censored under either fan order: both counts as lower bounds."""
    recs = []
    for config in CONFIGS:
        for side in SIDES:
            sa = rows[f"status_{side}_{config}_index"]
            sb = rows[f"status_{side}_{config}_degree"]
            mask = (sa == "unknown") | (sb == "unknown")
            for _, r in rows[mask].iterrows():
                recs.append({"instance": r.instance_name, "n": int(r.n), "config": config,
                             "side": side, "status_index": r[f"status_{side}_{config}_index"],
                             "nodes_index": int(r[f"nodes_{side}_{config}_index"]),
                             "status_degree": r[f"status_{side}_{config}_degree"],
                             "nodes_degree": int(r[f"nodes_{side}_{config}_degree"]),
                             "deadline_s": r.deadline})
    return pd.DataFrame(recs)


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    if frame is None or len(frame) == 0:
        return "*(empty)*\n"
    return frame.to_markdown(index=False, floatfmt=floatfmt) + "\n"


def write_tables(rows_csv: Path = ROWS_CSV, out: Path = TABLES) -> str:
    rows = pd.read_csv(rows_csv, low_memory=False)

    def _span(source: str) -> str:
        sub = rows[rows.source == source]
        if len(sub) == 0:
            return f"0 {source}"
        return f"{len(sub):,} {source} at {int(sub.n.min())}–{int(sub.n.max())}"

    parts = [f"# Fan order: paired node counts, index against remaining degree\n\n"
             f"*Regenerated {time.strftime('%Y-%m-%d %H:%M')} by "
             f"`python -m learning.fan_order --stage tables` from `{rows_csv}` "
             f"({len(rows):,} instances: {_span('campaign')}, {_span('corpus')}). "
             f"Ratio is `(nodes_degree + 1) / (nodes_index + 1)`, paired per instance; censored "
             f"pairs are counted and excluded from the ratio statistics. Wall clock "
             f"{rows.seconds_total.sum() / 3600:.2f} core-hours.*\n\n"]
    parts.append("## Audit: statuses agree under both fan orders; the default arm reproduces the recorded counts\n\n"
                 + _md(audit_table(rows)))
    verdict = kill_verdict(rows)
    parts.append("## Kill criterion (plan 2 §2.5a): paired median within ±5% at every size?\n\n"
                 + _md(pd.DataFrame([verdict])))
    for side, label in (("lo", "refutation, decide(optimum − 1)"), ("hi", "witness search, decide(optimum)")):
        for config in CONFIGS:
            parts.append(f"## {label}, `{config}`: by size\n\n" + _md(paired_table(rows, side, config)))
    for config in CONFIGS:
        parts.append(f"## Refutation, `{config}`: by size and realised density (customers per product), n ≥ 30\n\n"
                     + _md(density_table(rows, "lo", config)))
    for config in CONFIGS:
        parts.append(f"## Refutation, `{config}`: cells and classes at n ≥ 50 with the smallest and largest median ratios\n\n"
                     + _md(movers_table(rows, "lo", config)))
    parts.append("## `restricted_dfs` (cs-dfs, MCN seed, 200,000 nodes): value over the optimum under each fan order\n\n"
                 + _md(dfs_table(rows)))
    parts.append("## Censored calls (lower bounds under either order)\n\n" + _md(censored_table(rows)))
    text = "".join(parts)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=("run", "tables"), default="run")
    ap.add_argument("--source", choices=("both", "campaign", "corpus"), default="both")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--campaign-max-n", type=int, default=CAMPAIGN_MAX_N)
    ap.add_argument("--corpus-max-n", type=int, default=CORPUS_MAX_N)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--rows", type=Path, default=ROWS_CSV)
    ap.add_argument("--out", type=Path, default=TABLES)
    args = ap.parse_args()

    if args.stage == "run":
        jobs: list[dict] = []
        if args.source in ("both", "campaign"):
            jobs += campaign_targets(args.campaign_max_n, args.limit)
        if args.source in ("both", "corpus"):
            jobs += corpus_targets(args.corpus_max_n, args.limit)
        print(f"{len(jobs)} instances, {len(CONFIGS)} configs × {len(FAN_ORDERS)} fan orders × "
              f"2 sides + {len(FAN_ORDERS)} DFS values each, {args.workers} workers", flush=True)
        started = time.time()
        frame = run(jobs, args.workers, rows_csv=args.rows)
        print(f"wrote {args.rows} ({len(frame)} rows) in {time.time() - started:.0f} s")
    print(write_tables(args.rows, args.out))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
