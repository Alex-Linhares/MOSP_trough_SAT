"""The relabelling portfolio: is label noise a free speed-up for the refutation?

Question (`reports/ml_nature_plan_2.md` §2.4, loop0003 item 04). The complete
customer search reads the neighbour masks of the MOSP graph and nothing else,
so relabelling the customers (rows permuted, columns too) cannot change the
answer of any decision call, and does change its node count -- by up to 8x
under `csearch` on the §13 bases, by 24-33% at the ninetieth percentile over
the whole campaign at n <= 40 (§15). The minimum over `k` independent
relabellings run side by side is a portfolio with no coordination cost. This
module measures whether it is worth the cores:

  1. **The spread.** For sampled campaign instances at n in {40, 50, 60, 75}
     (`learning/data/ensemble/results.csv`, `results_upward.csv`; `PER_CELL`
     per cell) and every certified corpus instance at 50-100 customers, the
     identity labelling and `RELABELLINGS` random relabellings
     (`learning.graph_story.relabel`, seeded from the name), each decided at
     `optimum - 1` (the refutation; expected `unsat`) and at `optimum` (the
     witness search; expected `sat`, the order simulated) under the `csearch`
     configuration (`learning.node_counts.refutation_kwargs`). Every node count
     is recorded; a call that hits the deadline is `unknown` and its count is a
     lower bound, never a missing value.
  2. **The expected speed-up of min-of-k**, k in {2, 4, 8, 16}, against the
     identity labelling and against the median labelling, exactly by order
     statistics: drawing `k` of the `N` relabellings without replacement, the
     `i`-th smallest count is the minimum with probability C(N-i, k-1)/C(N, k).
     Reported per size as the median and p90 over instances, and on the
     instances where the identity refutation costs at least 10^4 nodes, which
     are the only ones a portfolio could matter on. A portfolio's wall clock
     is the minimum; its core cost is `k` times the minimum when the losers
     are stopped, so the core-efficiency `identity / (k * min)` is beside it.
  3. **Growth with n**: the median min-of-16 speed-up per size, a log-linear
     fit, and what it says at 125.
  4. **Cheap statistics of a labelling** (`label_statistics`): the Spearman
     correlation of customer index with degree and with products per
     customer, of product index with customers per product, the degree of
     customer 0, the neighbourhood of the customer the root's cheapest-first
     fan order picks, and the witness search's own node count. Each is scored
     by its within-instance Spearman correlation with the refutation count and
     by the speed-up of choosing the labelling it prefers, against min-of-k.
     If one predicts, choose; if none does, race.
  5. **The race** (`--stage race`): the 16-way portfolio run for real on the
     `Random-100-100-2` instances §14 censored at 1,500 s -- sixteen
     labellings on sixteen cores, the losers terminated when the first
     refutation lands (`--no-early-stop` runs all sixteen to the deadline).
  6. **The projection**: the wall clock for the 125 x 125 ridge classes on 16
     cores, from the recertify counts (`recertify/results.json`, 0.55 us per
     node) and §16's revised predictions, divided by the measured speed-up.

Nothing here changes a solver default, touches `_lower_bound`, or writes to
`solutions/`; the driver that would use a portfolio is `benchmarks.recertify`,
and the recommendation is stated in `reports/ml_nature.md` §18 and not applied.

Run:
    python -m learning.relabel_portfolio --workers 16                 # the study, ~25 min
    python -m learning.relabel_portfolio --stage race --workers 16    # the four instances, <= 40 min
    python -m learning.relabel_portfolio --stage tables               # tables from the CSVs

Writes `learning/data/ensemble/portfolio.csv.gz` (one row per instance and
labelling; committed), `portfolio_race.csv`, and `reports/portfolio_tables.md`.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import time
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR
from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
RESULTS_CSV = ENSEMBLE_DIR / "results.csv"
RESULTS_UPWARD_CSV = ENSEMBLE_DIR / "results_upward.csv"
SCALE_NODES_CSV = ENSEMBLE_DIR / "scale_nodes.csv"
ROWS_CSV = ENSEMBLE_DIR / "portfolio.csv.gz"
PARTIAL_CSV = Path("learning/data/portfolio_partial.csv")
RACE_CSV = ENSEMBLE_DIR / "portfolio_race.csv"
RECERTIFY_JSON = Path("recertify/results.json")
TABLES = Path("reports/portfolio_tables.md")

CONFIG = "csearch"
RELABELLINGS = 16
CAMPAIGN_N = (40, 50, 60, 75)
PER_CELL = 8
CORPUS_RANGE = (50, 100)
# The study stage skips these two classes: every call would censor at any
# deadline the study can afford (identity 10^8.0-10^9.4 nodes, §14). The race
# stage covers the first; the second is priced in the report.
SKIP_CLASSES = ("Random-100-100-2-", "Random-100-100-4-")
RACE_INSTANCES = ("Random-100-100-2-1_0", "Random-100-100-2-3_0",
                  "Random-100-100-2-4_0", "Random-100-100-2-5_0")
KS = (2, 4, 8, 16)
HARD_NODES = 10_000          # "where a portfolio could matter": identity refutation >= this
KILL_MIN_N = 60
KILL_SPEEDUP = 1.5
RECERTIFY_US_PER_NODE = 0.55  # §14: seconds per node on the recertify 125s
RIDGE_PREDICTED_NODES = {"Random-125-125-2 (§16)": 1.5e11, "Random-125-125-4 (§16)": 4e10}


# ----------------------------------------------------------------------------
# labellings and their cheap statistics
# ----------------------------------------------------------------------------


def labellings(instance: MOSPInstance, relabellings: int = RELABELLINGS) -> list[tuple[str, MOSPInstance]]:
    """The identity and `relabellings` seeded relabellings (no re-covering)."""
    from learning.graph_story import relabel

    out = [("identity", instance)]
    for k in range(relabellings):
        out.append((f"relabel{k}", relabel(instance, k)[0]))
    return out


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return 0.0
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def label_statistics(instance: MOSPInstance) -> dict:
    """Statistics of a labelling that cost less than a handful of nodes.

    `rho_index_degree`: Spearman correlation of customer index with MOSP-graph
    degree (are low indices the well-connected customers?); `rho_index_rows`:
    with products per customer; `rho_col_index_sum`: product index with
    customers per product; `deg_first`: the degree of customer 0, who wins
    every index tie-break; `root_choice_nbr_deg`: the mean degree of the
    neighbours of the customer the root's cheapest-first fan order picks (the
    lowest index among the minimum-degree customers); `root_choice_index`:
    that customer's index.
    """
    m = np.asarray(instance.matrix, dtype=np.int64)
    n = m.shape[0]
    adj = (m @ m.T) > 0
    np.fill_diagonal(adj, False)
    degree = adj.sum(1)
    rows = m.sum(1)
    cols = m.sum(0)
    active = rows > 0
    idx = np.arange(n)
    if active.sum() >= 1:
        cand = np.where(active)[0]
        root = int(cand[np.argmin(degree[cand])])   # argmin takes the lowest index on ties
        nbrs = np.where(adj[root])[0]
        nbr_deg = float(degree[nbrs].mean()) if len(nbrs) else 0.0
    else:
        root, nbr_deg = 0, 0.0
    return {
        "rho_index_degree": _spearman(idx[active], degree[active]),
        "rho_index_rows": _spearman(idx[active], rows[active]),
        "rho_col_index_sum": _spearman(np.arange(m.shape[1]), cols),
        "deg_first": int(degree[0]),
        "root_choice_nbr_deg": nbr_deg,
        "root_choice_index": root,
    }


STATISTICS = ("rho_index_degree", "rho_index_rows", "rho_col_index_sum", "deg_first",
              "root_choice_nbr_deg", "root_choice_index", "nodes_hi")


# ----------------------------------------------------------------------------
# targets
# ----------------------------------------------------------------------------


def campaign_sample(per_cell: int = PER_CELL, sizes=CAMPAIGN_N, seed: int = 4,
                    results_csv: Path = RESULTS_CSV,
                    upward_csv: Path = RESULTS_UPWARD_CSV) -> list[dict]:
    """`per_cell` certified instances from every campaign cell at each size,
    drawn with a fixed seed, carrying the identity's `csearch` count for
    scheduling (largest first)."""
    frames = []
    for path in (results_csv, upward_csv):
        if path.exists():
            frames.append(pd.read_csv(path, low_memory=False))
    frame = pd.concat(frames, ignore_index=True)
    frame = frame[frame.certified.astype(bool) & frame.n.isin(sizes)]
    rng = np.random.default_rng(seed)
    jobs = []
    for cell, d in frame.groupby("cell", sort=True):
        take = d.sample(n=min(per_cell, len(d)), random_state=int(rng.integers(2**31)))
        for row in take.to_dict("records"):
            jobs.append({"source": "campaign", "instance_name": row["instance_name"],
                         "cell": cell, "generator": row["generator"], "n": int(row["n"]),
                         "m": int(row["m"]), "param": float(row["param"]), "index": int(row["index"]),
                         "optimum": int(row["optimum"]), "matrix_digest": row["matrix_digest"],
                         "identity_nodes": float(row.get("nodes_csearch", np.nan))})
    return jobs


def corpus_sample(lo: int = CORPUS_RANGE[0], hi: int = CORPUS_RANGE[1],
                  skip_classes=SKIP_CLASSES, instance_dir: Path = DEFAULT_INSTANCE_DIR,
                  solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
                  scale_nodes_csv: Path = SCALE_NODES_CSV) -> list[dict]:
    """Every certified corpus instance with `lo <= n <= hi` customers outside
    `skip_classes`, with the identity's `csearch` count where §14 recorded it."""
    from learning.node_counts import certified_targets

    known: dict[str, float] = {}
    if scale_nodes_csv.exists():
        s = pd.read_csv(scale_nodes_csv)
        s = s[s.config == CONFIG]
        known = dict(zip(s.instance_name, s.nodes.astype(float)))
    jobs = []
    for matrix, name, source_file, collection, optimum, _ in certified_targets(
            instance_dir, solutions_dir, hi):
        if len(matrix) < lo or any(name.startswith(c) for c in skip_classes):
            continue
        jobs.append({"source": "corpus", "instance_name": name, "matrix": matrix,
                     "source_file": source_file, "collection": collection, "cell": collection,
                     "n": len(matrix), "m": len(matrix[0]), "optimum": int(optimum),
                     "identity_nodes": known.get(name, np.nan)})
    return jobs


def _materialise(job: dict) -> MOSPInstance:
    from learning.differential import _materialise

    return _materialise(job)


# ----------------------------------------------------------------------------
# the study
# ----------------------------------------------------------------------------


def _job(args) -> dict:
    """One (instance, labelling): both sides under `csearch`, with statistics."""
    job, label, deadline, with_hi = args
    from learning.differential import _call, witness_value
    from learning.graph_story import relabel

    base = _materialise(job)
    inst = base if label == "identity" else relabel(base, int(label[len("relabel"):]))[0]
    row = {"base_name": job["instance_name"], "labelling": label, "source": job["source"],
           "cell": job.get("cell", ""), "n": base.n_customers, "m": base.n_patterns,
           "optimum": int(job["optimum"]), "config": CONFIG, "deadline": deadline}
    row.update(label_statistics(inst))
    k = int(job["optimum"])
    if k <= 1:
        row.update(status_lo="trivial", nodes_lo=0, seconds_lo=0.0)
    else:
        status, nodes, seconds, _ = _call(inst, k - 1, CONFIG, deadline, _decide)
        row.update(status_lo=status, nodes_lo=nodes, seconds_lo=seconds)
    if with_hi:
        status, nodes, seconds, order = _call(inst, k, CONFIG, deadline, _decide)
        value = witness_value(inst, order) if status == "sat" else None
        row.update(status_hi=status, nodes_hi=nodes, seconds_hi=seconds, witness_value=value,
                   witness_ok=(value is not None and value <= k) if status == "sat" else None)
    return row


def _decide(instance: MOSPInstance, k: int, **kwargs):
    from satisfiability.customer_search import decide

    return decide(instance, k, **kwargs)


def run(jobs: list[dict], workers: int = 16, relabellings: int = RELABELLINGS,
        deadline: float | None = 120.0, with_hi: bool = True, partial: Path = PARTIAL_CSV,
        rows_csv: Path = ROWS_CSV, progress_every: int = 500) -> pd.DataFrame:
    """Every (instance, labelling) pair on the pool, heaviest instances first,
    rows flushed to `partial` as they land; then the compressed row table."""
    labels = ["identity"] + [f"relabel{k}" for k in range(relabellings)]
    def _weight(job: dict) -> float:
        w = job.get("identity_nodes", np.nan)
        return -float(w) if w == w else 0.0

    order = sorted(jobs, key=_weight)
    args = [(job, label, deadline, with_hi) for job in order for label in labels]
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
        if done % progress_every == 0:
            _flush()
            print(f"  {done}/{len(args)} calls, {time.time() - started:.0f} s", flush=True)

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
# order statistics
# ----------------------------------------------------------------------------


def expected_min(values, k: int) -> float:
    """E[min of k drawn without replacement from `values`], exactly.

    Sorted ascending, the i-th value (1-indexed) is the minimum of the draw
    iff it is drawn and the other k-1 come from the N-i above it, so with
    probability C(N-i, k-1) / C(N, k).
    """
    xs = np.sort(np.asarray(values, dtype=float))
    n = len(xs)
    if k > n:
        raise ValueError(f"k={k} exceeds the {n} values")
    total = comb(n, k)
    return float(sum(x * comb(n - i, k - 1) / total for i, x in enumerate(xs, start=1)))


def per_instance(rows: pd.DataFrame, side: str = "lo", ks=KS) -> pd.DataFrame:
    """One row per instance: identity, median and min over the relabellings,
    E[min-of-k] for each k, the speed-ups, and whether any count is censored."""
    nodes_col, status_col = f"nodes_{side}", f"status_{side}"
    out = []
    for base, d in rows.groupby("base_name", sort=False):
        ident = d[d.labelling == "identity"]
        rel = d[d.labelling != "identity"]
        if ident.empty or rel.empty:
            continue
        x = 1.0 + rel[nodes_col].astype(float).to_numpy()
        x_id = 1.0 + float(ident[nodes_col].iloc[0])
        censored = (d[status_col] == "unknown")
        rec = {"base_name": base, "source": d.source.iloc[0], "cell": d.cell.iloc[0],
               "n": int(d.n.iloc[0]), "m": int(d.m.iloc[0]), "optimum": int(d.optimum.iloc[0]),
               "relabellings": len(rel), "identity": x_id - 1, "median": float(np.median(x)) - 1,
               "min": float(x.min()) - 1, "max": float(x.max()) - 1,
               "max_over_min": float(x.max() / x.min()),
               "identity_over_min": float(x_id / x.min()),
               "mad_log10": float(np.abs(np.log10(x) - np.median(np.log10(x))).mean()),
               "censored_identity": bool(censored[ident.index].any()),
               "censored_any": bool(censored.any()),
               "censored_min": bool(censored[rel.index][rel[nodes_col] == rel[nodes_col].min()].any()),
               "seconds_identity": float(ident[f"seconds_{side}"].iloc[0]),
               "seconds_min": float(rel[f"seconds_{side}"].min())}
        for k in ks:
            if k <= len(rel):
                e = expected_min(x, k)
                rec[f"emin_{k}"] = e - 1
                rec[f"speedup_identity_{k}"] = x_id / e
                rec[f"speedup_median_{k}"] = float(np.median(x)) / e
                rec[f"core_efficiency_{k}"] = x_id / (k * e)
        out.append(rec)
    return pd.DataFrame(out)


def _band(n: int, source: str) -> str:
    if source == "campaign":
        return f"campaign n={n}"
    if n <= 50:
        return "corpus 50"
    if n <= 82:
        return "corpus 60–82"
    return "corpus 99–100"


def speedup_table(inst: pd.DataFrame, ks=KS, hard_only: bool = False) -> pd.DataFrame:
    """Per size band: median and p90 speed-up of min-of-k against the identity
    and the median labelling, the share of instances saving >= 1.5x at k = 8,
    and the median core efficiency at k = 16."""
    d = inst if not hard_only else inst[inst.identity >= HARD_NODES]
    rows = []
    for band, g in d.assign(band=[_band(n, s) for n, s in zip(d.n, d.source)]).groupby("band", sort=False):
        rec = {"band": band, "instances": len(g), "identity nodes median": float(g.identity.median()),
               "censored": int(g.censored_any.sum()),
               "max/min median": float(g.max_over_min.median()),
               "max/min p90": float(g.max_over_min.quantile(0.9)),
               "MAD log10": float(g.mad_log10.mean())}
        for k in ks:
            col = f"speedup_identity_{k}"
            if col in g:
                rec[f"min-of-{k} vs identity median"] = float(g[col].median())
                rec[f"min-of-{k} vs identity p90"] = float(g[col].quantile(0.9))
        rec["min-of-8 vs median labelling median"] = float(g.get("speedup_median_8", pd.Series(dtype=float)).median())
        rec["min-of-8 saves >= 1.5x"] = f"{int((g.get('speedup_identity_8', pd.Series(dtype=float)) >= KILL_SPEEDUP).sum())} ({100 * (g.get('speedup_identity_8', pd.Series(dtype=float)) >= KILL_SPEEDUP).mean():.1f}%)"
        rec["core efficiency k=16 median"] = float(g.get("core_efficiency_16", pd.Series(dtype=float)).median())
        rows.append(rec)
    if not rows:
        return pd.DataFrame(columns=["band", "instances"])
    order = {b: i for i, b in enumerate([f"campaign n={n}" for n in CAMPAIGN_N] +
                                        ["corpus 50", "corpus 60–82", "corpus 99–100"])}
    return pd.DataFrame(rows).sort_values("band", key=lambda s: s.map(order)).reset_index(drop=True)


def growth_fit(inst: pd.DataFrame, k: int = 16, hard_only: bool = True) -> dict:
    """log10 of the median min-of-k speed-up against n over the campaign
    sizes, a straight line through it, and its value at 100 and 125."""
    d = inst[(inst.source == "campaign")]
    if hard_only:
        d = d[d.identity >= HARD_NODES]
    col = f"speedup_identity_{k}"
    if col not in d or d.empty:
        return {"points": {}, "slope_per_customer": np.nan, "at_100": np.nan, "at_125": np.nan}
    med = d.groupby("n")[col].median()
    med = med[med > 0]
    if len(med) < 2:
        return {"points": med.to_dict(), "slope_per_customer": np.nan, "at_100": np.nan, "at_125": np.nan}
    slope, intercept = np.polyfit(med.index.to_numpy(float), np.log10(med.to_numpy()), 1)
    return {"points": {int(n): float(v) for n, v in med.items()},
            "slope_per_customer": float(slope),
            "at_100": float(10 ** (intercept + slope * 100)),
            "at_125": float(10 ** (intercept + slope * 125))}


def kill_verdict(inst: pd.DataFrame) -> dict:
    """Median min-of-8 speed-up against the identity at n >= 60, refutation
    side, on every instance and on the hard ones; the kill fires under 1.5x."""
    d = inst[inst.n >= KILL_MIN_N] if "speedup_identity_8" in inst else inst.iloc[0:0]
    hard = d[d.identity >= HARD_NODES] if len(d) else d
    all_med = float(d.speedup_identity_8.median()) if len(d) else np.nan
    hard_med = float(hard.speedup_identity_8.median()) if len(hard) else np.nan
    return {"instances": len(d), "median_all": all_med, "hard_instances": len(hard),
            "median_hard": hard_med, "threshold": KILL_SPEEDUP,
            "kill_met_all": bool(all_med < KILL_SPEEDUP) if len(d) else None,
            "kill_met_hard": bool(hard_med < KILL_SPEEDUP) if len(hard) else None}


# ----------------------------------------------------------------------------
# does a cheap statistic predict the cost of a labelling?
# ----------------------------------------------------------------------------


def predictor_table(rows: pd.DataFrame, inst: pd.DataFrame, statistics=STATISTICS,
                    min_spread: float = 1.5) -> pd.DataFrame:
    """For each statistic, over the instances whose relabellings spread by at
    least `min_spread` (max/min): the mean within-instance Spearman correlation
    with the refutation count, and the speed-up (identity / chosen) when the
    labelling with the smallest (and the largest) value of the statistic is
    run alone, beside E[min-of-2] and the median labelling."""
    wide = inst.set_index("base_name")
    keep = set(wide[wide.max_over_min >= min_spread].index)
    d = rows[rows.base_name.isin(keep) & (rows.labelling != "identity")]
    out = []
    for stat in statistics:
        if stat not in d:
            continue
        rhos, low_ratio, high_ratio = [], [], []
        for base, g in d.groupby("base_name"):
            x = g[stat].astype(float).to_numpy()
            y = 1.0 + g.nodes_lo.astype(float).to_numpy()
            if np.ptp(x) == 0:
                continue
            rhos.append(_spearman(x, y))
            ident = 1.0 + wide.loc[base, "identity"]
            low_ratio.append(ident / y[np.argmin(x)])
            high_ratio.append(ident / y[np.argmax(x)])
        if not rhos:
            continue
        out.append({"statistic": stat, "instances": len(rhos),
                    "mean Spearman with nodes": float(np.mean(rhos)),
                    "|rho| >= 0.5": f"{100 * np.mean(np.abs(rhos) >= 0.5):.0f}%",
                    "choose smallest: median speed-up": float(np.median(low_ratio)),
                    "choose largest: median speed-up": float(np.median(high_ratio))})
    ref = wide.loc[list(keep)]
    out.append({"statistic": "(reference) one random relabelling", "instances": len(ref),
                "mean Spearman with nodes": np.nan, "|rho| >= 0.5": "",
                "choose smallest: median speed-up": float(((1 + ref.identity) / (1 + ref["median"])).median()),
                "choose largest: median speed-up": np.nan})
    for k in (2, 4):
        out.append({"statistic": f"(reference) min-of-{k}", "instances": len(ref),
                    "mean Spearman with nodes": np.nan, "|rho| >= 0.5": "",
                    "choose smallest: median speed-up": float(ref[f"speedup_identity_{k}"].median()),
                    "choose largest: median speed-up": np.nan})
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------
# the race
# ----------------------------------------------------------------------------


def _race_job(args) -> dict:
    job, label, deadline = args
    from learning.differential import _call
    from learning.graph_story import relabel

    base = _materialise(job)
    inst = base if label == "identity" else relabel(base, int(label[len("relabel"):]))[0]
    started = time.monotonic()
    status, nodes, seconds, _ = _call(inst, int(job["optimum"]) - 1, CONFIG, deadline, _decide)
    return {"base_name": job["instance_name"], "labelling": label, "n": base.n_customers,
            "m": base.n_patterns, "optimum": int(job["optimum"]), "k": int(job["optimum"]) - 1,
            "status": status, "nodes": nodes, "seconds": seconds, "deadline": deadline,
            "finished_at": round(time.monotonic() - started, 3)}


def race(jobs: list[dict], ways: int = 16, deadline: float = 600.0, early_stop: bool = True,
         out: Path = RACE_CSV, identity_reference: dict | None = None) -> pd.DataFrame:
    """The portfolio for real: `ways` labellings of each instance on `ways`
    cores, refuting `optimum - 1`; with `early_stop` the pool is terminated
    when the first `unsat` lands and the losers' counts are lost (they were
    running; that is the point). Appends one row per finished labelling plus
    a `portfolio` row per instance with the wall clock."""
    labels = ["identity"] + [f"relabel{k}" for k in range(ways - 1)]
    rows: list[dict] = []
    for job in jobs:
        name = job["instance_name"]
        started = time.monotonic()
        finished: list[dict] = []
        winner = None
        with multiprocessing.Pool(ways) as pool:
            for row in pool.imap_unordered(_race_job, [(job, lab, deadline) for lab in labels]):
                row["wall_at_return"] = round(time.monotonic() - started, 3)
                finished.append(row)
                print(f"  {name} {row['labelling']}: {row['status']} {row['nodes']} nodes "
                      f"{row['seconds']:.1f} s (wall {row['wall_at_return']:.1f} s)", flush=True)
                if row["status"] == "unsat" and winner is None:
                    winner = row
                    if early_stop:
                        break
            if early_stop:
                pool.terminate()
        wall = time.monotonic() - started
        rows.extend(finished)
        ref = (identity_reference or {}).get(name, {})
        rows.append({"base_name": name, "labelling": "portfolio", "n": finished[0]["n"],
                     "m": finished[0]["m"], "optimum": job["optimum"], "k": job["optimum"] - 1,
                     "status": winner["status"] if winner else "unknown",
                     "nodes": winner["nodes"] if winner else np.nan,
                     "seconds": round(wall, 3), "deadline": deadline,
                     "finished_at": round(wall, 3), "wall_at_return": round(wall, 3),
                     "winner": winner["labelling"] if winner else "",
                     "ways": ways, "early_stop": early_stop, "finished": len(finished),
                     "identity_reference_nodes": ref.get("nodes", np.nan),
                     "identity_reference_seconds": ref.get("seconds", np.nan),
                     "identity_reference_status": ref.get("status", "")})
    frame = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        frame = pd.concat([pd.read_csv(out), frame], ignore_index=True)
    frame.to_csv(out, index=False)
    return frame


def race_targets(names=RACE_INSTANCES, instance_dir: Path = DEFAULT_INSTANCE_DIR,
                 solutions_dir: Path = DEFAULT_SOLUTIONS_DIR) -> list[dict]:
    wanted = set(names)
    jobs = [j for j in corpus_sample(1, 200, skip_classes=(), instance_dir=instance_dir,
                                     solutions_dir=solutions_dir) if j["instance_name"] in wanted]
    return sorted(jobs, key=lambda j: names.index(j["instance_name"]))


def scale_reference(scale_nodes_csv: Path = SCALE_NODES_CSV) -> dict:
    """§14's identity `csearch` counts (censored at 1,500 s) for the race table."""
    if not scale_nodes_csv.exists():
        return {}
    s = pd.read_csv(scale_nodes_csv)
    s = s[s.config == CONFIG]
    return {r.instance_name: {"nodes": float(r.nodes), "seconds": float(r.seconds), "status": r.status}
            for r in s.itertuples()}


def race_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per raced instance: the identity's §14 count, the winner, the wall, the
    speed-up in wall clock (a lower bound when the identity was censored) and
    the core cost of the portfolio against the identity's seconds."""
    rows = []
    for base, d in frame.groupby("base_name", sort=False):
        p = d[d.labelling == "portfolio"]
        if p.empty:
            continue
        p = p.iloc[-1]
        fin = d[(d.labelling != "portfolio") & (d.status == "unsat")]
        ref_s, ref_n = p.identity_reference_seconds, p.identity_reference_nodes
        censored_ref = p.identity_reference_status == "unknown"
        rec = {"instance": base, "k": int(p.k), "identity §14": f"{'≥ ' if censored_ref else ''}{ref_n:.3g} nodes, {'≥ ' if censored_ref else ''}{ref_s:.0f} s",
               "ways": int(p.ways), "early stop": bool(p.early_stop),
               "winner": p.winner or "none", "winner nodes": p.nodes,
               "wall (s)": p.seconds, "labellings finished": int(p.finished),
               "finished unsat": len(fin),
               "wall speed-up vs identity": (f"{'≥ ' if censored_ref else ''}{ref_s / p.seconds:.2f}×"
                                             if p.status == "unsat" and ref_s == ref_s else "—"),
               "core cost (ways × wall) / identity s": (f"{'≤ ' if censored_ref else ''}{p.ways * p.seconds / ref_s:.2f}"
                                                        if p.status == "unsat" and ref_s == ref_s else "—")}
        if len(fin) >= 2:
            rec["finished max/min nodes"] = float(fin.nodes.max() / fin.nodes.min())
        rows.append(rec)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# the projection
# ----------------------------------------------------------------------------


def projection(speedups: dict[str, float], recertify_json: Path = RECERTIFY_JSON,
               predicted=RIDGE_PREDICTED_NODES, us_per_node: float = RECERTIFY_US_PER_NODE,
               cores: int = 16) -> pd.DataFrame:
    """Wall clock for the 125 x 125 ridge on `cores` cores: the identity's
    seconds (recertify's, or predicted nodes x us/node) divided by each named
    speed-up, beside the plain alternative of `cores` instances side by side."""
    items = []
    if recertify_json.exists():
        for r in json.loads(recertify_json.read_text()):
            if r.get("status") == "unsat" and r.get("nodes"):
                items.append((r["name"] + " (recertify)", float(r["nodes"]), float(r["seconds"])))
    for name, nodes in predicted.items():
        items.append((name, nodes, nodes * us_per_node * 1e-6))
    rows = []
    for name, nodes, seconds in items:
        rec = {"instance / class": name, "nodes": nodes, "identity hours (1 core)": seconds / 3600}
        for label, s in speedups.items():
            rec[f"portfolio hours, {label}"] = seconds / s / 3600 if s and s == s else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt) if len(frame) else "_(empty)_"


def write_tables(rows_csv: Path = ROWS_CSV, race_csv: Path = RACE_CSV, out: Path = TABLES) -> str:
    rows = pd.read_csv(rows_csv, low_memory=False)
    parts = [f"# Relabelling portfolio tables (`python -m learning.relabel_portfolio --stage tables`)\n",
             f"Rows: {len(rows):,} calls on {rows.base_name.nunique():,} instances, "
             f"{rows.labelling.nunique()} labellings each, configuration `{CONFIG}`.\n"]
    audit = rows.groupby(["source", "status_lo"]).size().unstack(fill_value=0)
    parts.append("## Audit: status at optimum − 1 by source\n\n" + _md(audit.reset_index()))
    if "status_hi" in rows:
        audit_hi = rows.groupby(["source", "status_hi"]).size().unstack(fill_value=0)
        bad = rows[(rows.status_hi == "sat") & (rows.witness_ok == False)]  # noqa: E712
        parts.append("## Audit: status at the optimum by source\n\n" + _md(audit_hi.reset_index())
                     + f"\n\nWitnesses simulating above the optimum: {len(bad)}.")
    inst_lo = per_instance(rows, "lo")
    parts.append("## Refutation (optimum − 1): speed-up of min-of-k, every instance\n\n" + _md(speedup_table(inst_lo)))
    parts.append(f"## Refutation: instances whose identity refutation costs ≥ {HARD_NODES:,} nodes\n\n"
                 + _md(speedup_table(inst_lo, hard_only=True)))
    if "nodes_hi" in rows:
        inst_hi = per_instance(rows, "hi")
        parts.append("## Witness search (optimum): speed-up of min-of-k, every instance\n\n" + _md(speedup_table(inst_hi)))
        parts.append(f"## Witness search: identity ≥ {HARD_NODES:,} nodes\n\n" + _md(speedup_table(inst_hi, hard_only=True)))
    g_all = growth_fit(inst_lo, hard_only=False)
    g_hard = growth_fit(inst_lo, hard_only=True)
    parts.append("## Growth of the median min-of-16 refutation speed-up with n (campaign)\n\n"
                 f"- every instance: {g_all['points']}, slope {g_all['slope_per_customer']:.4f} log10 per customer, "
                 f"at 100: {g_all['at_100']:.2f}×, at 125: {g_all['at_125']:.2f}×\n"
                 f"- identity ≥ {HARD_NODES:,} nodes: {g_hard['points']}, slope {g_hard['slope_per_customer']:.4f}, "
                 f"at 100: {g_hard['at_100']:.2f}×, at 125: {g_hard['at_125']:.2f}×")
    kv = kill_verdict(inst_lo)
    parts.append("## Kill criterion (median min-of-8 refutation speed-up at n ≥ 60 under 1.5×)\n\n"
                 + "\n".join(f"- {k}: {v}" for k, v in kv.items()))
    parts.append("## Does a cheap statistic of a labelling predict its refutation cost? (instances with max/min ≥ 1.5)\n\n"
                 + _md(predictor_table(rows, inst_lo)))
    ext = inst_lo.sort_values("max_over_min", ascending=False).head(15)
    parts.append("## The fifteen widest spreads (refutation)\n\n"
                 + _md(ext[["base_name", "n", "m", "optimum", "identity", "min", "max", "max_over_min",
                            "identity_over_min", "speedup_identity_8", "censored_any"]]))
    speedups = {"min-of-16 at n=75 (hard, measured)": g_hard["points"].get(75, np.nan),
                "min-of-16 extrapolated to 125": g_hard["at_125"]}
    if race_csv.exists():
        rf = pd.read_csv(race_csv)
        rt = race_table(rf)
        parts.append("## The race: the 16-way portfolio on the censored `Random-100-100-2` instances\n\n" + _md(rt))
        fin = rf[(rf.labelling != "portfolio")]
        parts.append("### Every labelling that returned\n\n"
                     + _md(fin[["base_name", "labelling", "status", "nodes", "seconds", "wall_at_return"]]))
        won = rt[rt["wall speed-up vs identity"].astype(str).str.contains("×")]
        if len(won):
            vals = won["wall speed-up vs identity"].str.replace("≥ ", "").str.rstrip("×").astype(float)
            speedups["race wall speed-up at n=100 (median, ≥ where censored)"] = float(vals.median())
    parts.append("## Projection: the 125 × 125 ridge on 16 cores\n\n" + _md(projection(speedups), floatfmt=".3g"))
    text = "\n\n".join(parts) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("run", "race", "tables"), default="run")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--relabellings", type=int, default=RELABELLINGS)
    ap.add_argument("--per-cell", type=int, default=PER_CELL)
    ap.add_argument("--deadline", type=float, default=120.0, help="per call, seconds")
    ap.add_argument("--source", choices=("both", "campaign", "corpus"), default="both")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-hi", action="store_true", help="skip the witness-search side")
    ap.add_argument("--ways", type=int, default=16)
    ap.add_argument("--race-deadline", type=float, default=600.0)
    ap.add_argument("--race-instances", nargs="*", default=list(RACE_INSTANCES))
    ap.add_argument("--no-early-stop", action="store_true")
    args = ap.parse_args()

    if args.stage == "run":
        jobs = []
        if args.source in ("both", "campaign"):
            jobs += campaign_sample(args.per_cell)
        if args.source in ("both", "corpus"):
            jobs += corpus_sample()
        if args.limit:
            jobs = jobs[:args.limit]
        print(f"{len(jobs)} instances x {1 + args.relabellings} labellings, deadline {args.deadline} s, "
              f"{args.workers} workers", flush=True)
        frame = run(jobs, args.workers, args.relabellings, args.deadline, not args.no_hi)
        print(f"{len(frame)} rows -> {ROWS_CSV}")
        print(write_tables())
    elif args.stage == "race":
        jobs = race_targets(tuple(args.race_instances))
        print(f"racing {[j['instance_name'] for j in jobs]} {args.ways}-way, deadline {args.race_deadline} s")
        frame = race(jobs, args.ways, args.race_deadline, not args.no_early_stop,
                     identity_reference=scale_reference())
        print(_md(race_table(frame)))
    else:
        print(write_tables())


if __name__ == "__main__":
    main()
