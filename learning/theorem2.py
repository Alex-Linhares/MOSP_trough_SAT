"""Theorem 2's switch: when should the complete search turn `better_move` on?

Plan 2 §2.5(b) (`reports/ml_nature_plan_2.md`), loop0003 item 07. Section 22
of `reports/ml_nature.md`.

**The question.** The `csearch` configuration turns Chu & Stuckey's Theorem 2
(`better_move`, every candidate a dominator) on when the mean number of
products per customer is at most 5 (`sparse_enough_for_better_move`) and off
otherwise; the `default` configuration never turns it on. §13 and §14 found
the rule saved 10-13% of the refutation's nodes at n ≤ 40 and up to 83% at
n = 100, and never cost a node -- but those counts were made before the
2026-09-26 fix of the C `better_move` (§18 (e)), and the rule was only ever
*measured where it is on*: where the hand threshold turns it off, nobody had
run it. Whether the threshold is in the right place, and whether the rule
should simply always be on, are two hypotheses this module tests, in nodes,
paired per instance.

**The measurement.** For every certified campaign instance at 10-75
customers, every certified corpus instance at 9-100, and the fifteen
125 × 125 corpus instances whose `default` refutation settles inside 1,500 s
(`Random-125-125-6/8/10`), `decide(optimum - 1)` (the refutation) and
`decide(optimum)` (the witness search) under two arms, back to back in one
process: **off** (`decide`'s defaults) and **on** (`better_move=True,
better_move_dominators=0`, the fixed C). Both arms are byte-for-byte checks
of counts already on record: the off arm against item 06's
`nodes_lo_default_index`, the on arm against its `nodes_lo_csearch_index`
wherever the hand rule was on. The paired statistic is
`(nodes_on + 1) / (nodes_off + 1)`; a censored call is a lower bound and its
pair is counted but not pooled into ratio statistics.

**The rules compared**, each a function from an instance to on/off, scored
by the nodes it would have spent: *always off* (`default`), *always on*, the
*hand threshold* (`csearch`), the *oracle* (whichever arm was cheaper, the
floor), and a *learned boundary*: a depth-3 decision tree on size-free
features, fitted to the sign of the paired difference with the magnitude
`|log10 ratio|` as the sample weight, evaluated out of fold with folds
grouped by file ∪ MOSP-graph isomorphism class. **Kill** (plan 2 §2.5b): if
the learned boundary agrees with the hand threshold on more than 95% of
instances, the threshold stands.

Run:
    python -m learning.theorem2 --workers 16                 # the study, ~20 min
    python -m learning.theorem2 --stage tables               # tables from the CSV
    python -m learning.theorem2 --source campaign --limit 300 --workers 8

Writes `learning/data/ensemble/theorem2.csv.gz` (one wide row per instance,
committed), `learning/data/ensemble/theorem2_tree.txt` and
`reports/theorem2_tables.md`. Nothing is written to `solutions/`; no default
is changed. Every `on` count here is a post-fix count.
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.fan_order import (
    BAND_ORDER as _FAN_BAND_ORDER,
    RESULTS_CSV,
    RESULTS_UPWARD_CSV,
    SCALE_NODES_CSV,
    band as _fan_band,
    campaign_targets,
    corpus_targets,
    density_band,
)
from learning.fan_order import ROWS_CSV as FAN_ORDER_CSV
from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
INSTANCES_CSV = Path("learning/data/instances.csv")
CANONICAL_CSV = Path("learning/data/canonical.csv")
ROWS_CSV = ENSEMBLE_DIR / "theorem2.csv.gz"
PARTIAL_CSV = Path("learning/data/theorem2_partial.csv")
TREE_TXT = ENSEMBLE_DIR / "theorem2_tree.txt"
TABLES = Path("reports/theorem2_tables.md")

ARMS = {"off": {}, "on": {"better_move": True, "better_move_dominators": 0}}
SIDES = ("lo", "hi")
CAMPAIGN_MAX_N = 75
CORPUS_MAX_N = 125
CAMPAIGN_DEADLINE = 60.0
CORPUS_DEADLINE = 120.0
LARGE_DEADLINE = 2400.0          # the 125 × 125 dense classes: default takes up to 1,233 s
KILL_AGREEMENT = 0.95
HAND_THRESHOLD = 5.0             # `BETTER_MOVE_DENSITY`, mean products per customer
TREE_DEPTH = 3
FOLDS = 5

# Size-free features for the boundary. Each is a function of the feature frame;
# none grows with n. `row_mean` is the hand rule's own statistic.
SIZE_FREE = {
    "products_per_customer": lambda f: f["row_mean"],
    "customers_per_product": lambda f: f["col_mean"],
    "density": lambda f: f["density"],
    "log_m_over_n": lambda f: np.log10(f["m"] / f["n"]),
    "graph_density": lambda f: f["g_density"],
    "deg_mean_frac": lambda f: f["g_deg_mean"] / f["n"],
    "deg_cv": lambda f: f["g_deg_std"] / f["g_deg_mean"].replace(0, np.nan),
    "degeneracy_frac": lambda f: f["g_degeneracy"] / f["n"],
    "tw_frac": lambda f: f["tw_min_fill"] / f["n"],
    "opt_frac": lambda f: f["optimum"] / f["n"],
    "largest_component_frac": lambda f: f["g_largest_comp_frac"],
    "log_components": lambda f: np.log10(f["g_components"].astype(float)),
    "clustering": lambda f: f["g_clustering"],
    "dominated_col_frac": lambda f: f["dominated_col_frac"],
    "distinct_col_frac": lambda f: f["distinct_col_frac"],
    "row_cv": lambda f: f["row_std"] / f["row_mean"].replace(0, np.nan),
    "col_cv": lambda f: f["col_std"] / f["col_mean"].replace(0, np.nan),
}


def band(n: int, source: str) -> str:
    """Item 06's size bands plus one for the corpus above 100: the fifteen
    125 × 125 instances this study adds would otherwise fall into
    `fan_order`'s top band, which is named for 99–100."""
    if source == "corpus" and n > 100:
        return "corpus 101–125"
    return _fan_band(n, source)


FAN_BAND_ORDER = list(_FAN_BAND_ORDER) + ["corpus 101–125"]
fan_band = band

FEATURE_COLUMNS = ["row_mean", "col_mean", "density", "g_density", "g_deg_mean", "g_deg_std",
                   "g_degeneracy", "tw_min_fill", "g_largest_comp_frac", "g_components",
                   "g_clustering", "dominated_col_frac", "distinct_col_frac", "row_std", "col_std"]


# ----------------------------------------------------------------------------
# targets
# ----------------------------------------------------------------------------


def targets(campaign_max_n: int = CAMPAIGN_MAX_N, corpus_max_n: int = CORPUS_MAX_N,
            source: str = "both", limit: int | None = None) -> list[dict]:
    """Item 06's targets, plus the corpus above 100 where the `default`
    refutation is on record as settled (the dense 125 × 125 classes)."""
    jobs: list[dict] = []
    if source in ("both", "campaign"):
        jobs += campaign_targets(campaign_max_n, limit)
    if source in ("both", "corpus"):
        corp = corpus_targets(corpus_max_n, None)
        corp = [j for j in corp if j["n"] <= 100 or j["ref_status_default"] == "unsat"]
        jobs += corp[:limit] if limit is not None else corp
    return jobs


def deadline_for(job: dict) -> float:
    if job["source"] != "corpus" or job["n"] <= 40:
        return CAMPAIGN_DEADLINE
    return CORPUS_DEADLINE if job["n"] <= 100 else LARGE_DEADLINE


# ----------------------------------------------------------------------------
# one instance
# ----------------------------------------------------------------------------


def _call(instance: MOSPInstance, k: int, arm: str, deadline_seconds: float | None):
    from satisfiability.customer_search import decide

    deadline = None if deadline_seconds is None else time.monotonic() + deadline_seconds
    started = time.monotonic()
    answer = decide(instance, k, deadline=deadline, **ARMS[arm])
    return answer.status, int(answer.nodes), round(time.monotonic() - started, 4), answer.order


def measure(instance: MOSPInstance, optimum: int, deadline_seconds: float | None = None,
            arms: tuple[str, ...] = tuple(ARMS)) -> dict:
    """Both arms on one instance, as one wide row: `{status,nodes,seconds}_{lo,hi}_{arm}`
    plus `witness_{arm}` (the simulated value of the `hi` witness, at most
    `optimum` if the search is sound) and `hand_on` (the hand threshold)."""
    from learning.differential import witness_value
    from satisfiability.customer_search import sparse_enough_for_better_move

    row: dict = {"optimum": optimum,
                 "products_per_customer": float(instance.matrix.sum()) / max(instance.n_customers, 1),
                 "hand_on": bool(sparse_enough_for_better_move(instance))}
    for arm in arms:
        if optimum <= 1:
            row.update({f"status_lo_{arm}": "trivial", f"nodes_lo_{arm}": 0, f"seconds_lo_{arm}": 0.0})
        else:
            status, nodes, seconds, _ = _call(instance, optimum - 1, arm, deadline_seconds)
            row.update({f"status_lo_{arm}": status, f"nodes_lo_{arm}": nodes, f"seconds_lo_{arm}": seconds})
        status, nodes, seconds, order = _call(instance, optimum, arm, deadline_seconds)
        row.update({f"status_hi_{arm}": status, f"nodes_hi_{arm}": nodes, f"seconds_hi_{arm}": seconds,
                    f"witness_{arm}": witness_value(instance, order) if status == "sat" else None})
    return row


def _job(args) -> dict:
    from learning.fan_order import _materialise

    job, deadline = args
    instance = _materialise(job)
    started = time.monotonic()
    row = {k: job[k] for k in ("source", "instance_name", "cell", "n", "m", "optimum", "col_mean",
                               "graph_cert", "ref_nodes_default", "ref_status_default")}
    row["source_file"] = job.get("source_file", "")
    row["deadline"] = deadline
    row.update(measure(instance, int(job["optimum"]), deadline))
    row["seconds_total"] = round(time.monotonic() - started, 3)
    return row


def run(jobs: list[dict], workers: int = 16, partial: Path = PARTIAL_CSV,
        rows_csv: Path = ROWS_CSV, progress_every: int = 500) -> pd.DataFrame:
    """Every job on the pool, heaviest recorded refutation first, rows flushed to
    `partial` as they land; then the compressed wide table."""
    def _weight(job: dict) -> float:
        w = job.get("ref_nodes_default", np.nan)
        return -float(w) if w == w else -float(job["n"]) * 1e3

    order = sorted(jobs, key=_weight)
    args = [(job, deadline_for(job)) for job in order]
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
        if done % progress_every == 0 or done <= 50:
            _flush()
            if done % progress_every == 0 or done in (10, 50):
                print(f"  {done}/{len(args)} instances, {time.time() - started:.0f} s", flush=True)

    if workers <= 1:
        for a in args:
            _consume(_job(a))
    else:
        with multiprocessing.Pool(workers) as pool:
            for row in pool.imap_unordered(_job, args, chunksize=1):
                _consume(row)
    _flush()
    frame = pd.read_csv(partial, low_memory=False) if partial.exists() else pd.DataFrame()
    rows_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(rows_csv, index=False, compression="gzip")
    return frame


# ----------------------------------------------------------------------------
# features and groups
# ----------------------------------------------------------------------------


def feature_frame(results_csv: Path = RESULTS_CSV, upward_csv: Path = RESULTS_UPWARD_CSV,
                  instances_csv: Path = INSTANCES_CSV, canonical_csv: Path = CANONICAL_CSV) -> pd.DataFrame:
    """Matrix and graph features per instance from the campaign result files and
    `instances.csv`, keyed by (source, instance_name), with the grouping key."""
    parts = []
    for path in (results_csv, upward_csv):
        if path.exists():
            f = pd.read_csv(path, low_memory=False)
            cols = ["instance_name", "cell", "graph_cert"] + [c for c in FEATURE_COLUMNS if c in f.columns]
            f = f[cols].copy()
            f["source"] = "campaign"
            f["file_key"] = f["cell"]
            parts.append(f.drop(columns="cell"))
    if instances_csv.exists():
        f = pd.read_csv(instances_csv, low_memory=False)
        cols = ["instance_name", "source_file"] + [c for c in FEATURE_COLUMNS if c in f.columns]
        f = f[cols].copy()
        if canonical_csv.exists():
            can = pd.read_csv(canonical_csv)[["instance_name", "graph_cert"]]
            f = f.merge(can, on="instance_name", how="left")
        else:
            f["graph_cert"] = np.nan
        f["source"] = "corpus"
        f["file_key"] = f["source_file"]
        parts.append(f.drop(columns="source_file"))
    if not parts:
        return pd.DataFrame(columns=["source", "instance_name"])
    out = pd.concat(parts, ignore_index=True)
    return out.drop_duplicates(["source", "instance_name"])


def with_features(rows: pd.DataFrame, feats: pd.DataFrame | None = None) -> pd.DataFrame:
    """The run's rows joined with features and the file ∪ class group id."""
    from learning.fingerprint import union_groups

    feats = feature_frame() if feats is None else feats
    keep = [c for c in feats.columns
            if c not in rows.columns or c in ("source", "instance_name", "graph_cert")]
    f = rows.merge(feats[keep], on=["source", "instance_name"], how="left", suffixes=("", "_feat"))
    if "graph_cert_feat" in f.columns:
        # the run's rows carry the campaign certificate and "" for the corpus;
        # `canonical.csv` supplies the corpus one
        own = f["graph_cert"].where(f["graph_cert"].notna() & (f["graph_cert"].astype(str) != ""))
        f["graph_cert"] = own.fillna(f["graph_cert_feat"])
        f = f.drop(columns=["graph_cert_feat"])
    if "file_key" not in f.columns:
        f["file_key"] = f["cell"]
    f["file_key"] = f["file_key"].fillna(f["cell"])
    f["group"] = union_groups(f["file_key"].astype(str), f["graph_cert"])
    return f


def design(f: pd.DataFrame) -> pd.DataFrame:
    """The size-free feature matrix (NaN where a feature is unavailable)."""
    out = {}
    for name, fn in SIZE_FREE.items():
        try:
            out[name] = np.asarray(fn(f), dtype=float)
        except KeyError:
            out[name] = np.full(len(f), np.nan)
    return pd.DataFrame(out, index=f.index)


# ----------------------------------------------------------------------------
# paired statistics
# ----------------------------------------------------------------------------


def paired(rows: pd.DataFrame, side: str = "lo") -> pd.DataFrame:
    """Per-instance pair for one side: nodes under each arm, decided flag, ratio
    `(on + 1) / (off + 1)`, the oracle's choice and the hand rule's."""
    off = rows[f"nodes_{side}_off"].astype(float)
    on = rows[f"nodes_{side}_on"].astype(float)
    s_off = rows[f"status_{side}_off"].astype(str)
    s_on = rows[f"status_{side}_on"].astype(str)
    decided = s_off.isin(["sat", "unsat", "trivial"]) & s_on.isin(["sat", "unsat", "trivial"])
    out = rows[["source", "instance_name", "n", "m", "col_mean", "cell", "hand_on",
                "products_per_customer"]].copy()
    out["nodes_off"] = off
    out["nodes_on"] = on
    out["decided"] = decided
    out["ratio"] = (on + 1) / (off + 1)
    out["log_ratio"] = np.log10(out["ratio"])
    out["seconds_off"] = rows[f"seconds_{side}_off"].astype(float)
    out["seconds_on"] = rows[f"seconds_{side}_on"].astype(float)
    # oracle: +1 on cheaper, -1 off cheaper, 0 tie (undecided pairs are ties for scoring)
    sign = np.sign(off - on).astype(int)
    sign[~decided.to_numpy()] = 0
    out["oracle"] = sign
    out["band"] = [fan_band(n, s) for n, s in zip(out.n, out.source)]
    out["density_band"] = out["col_mean"].map(density_band)
    return out


def _summarise(g: pd.DataFrame) -> pd.Series:
    d = g[g.decided]
    r = d["ratio"]
    heavy = d[d.nodes_off >= 1e4]
    per_node = np.nan
    if len(heavy):
        per_node = float(((heavy.seconds_on / heavy.nodes_on.clip(lower=1)) /
                          (heavy.seconds_off / heavy.nodes_off.clip(lower=1))).median())
    return pd.Series({
        "instances": len(g),
        "paired": len(d),
        "censored": int((~g.decided).sum()),
        "saves": int((d.nodes_on < d.nodes_off).sum()),
        "ties": int((d.nodes_on == d.nodes_off).sum()),
        "costs": int((d.nodes_on > d.nodes_off).sum()),
        "median_ratio": float(r.median()) if len(d) else np.nan,
        "p10": float(r.quantile(0.1)) if len(d) else np.nan,
        "p90": float(r.quantile(0.9)) if len(d) else np.nan,
        "max": float(r.max()) if len(d) else np.nan,
        "geo_mean": float(10 ** d.log_ratio.mean()) if len(d) else np.nan,
        "total_ratio": float((d.nodes_on.sum() + 1) / (d.nodes_off.sum() + 1)) if len(d) else np.nan,
        "median_off": float(d.nodes_off.median()) if len(d) else np.nan,
        "sec_per_node_ratio": per_node,
        "heavy": len(heavy),
    })


def paired_table(rows: pd.DataFrame, side: str = "lo", by=("band", "hand_on"),
                 min_group: int = 1) -> pd.DataFrame:
    p = paired(rows, side)
    by = list(by) if not isinstance(by, str) else [by]
    t = p.groupby(by, sort=False).apply(_summarise, include_groups=False).reset_index()
    t = t[t.instances >= min_group]
    if "band" in by:
        t["_o"] = t["band"].map({b: i for i, b in enumerate(FAN_BAND_ORDER)})
        t = t.sort_values(["_o"] + [b for b in by if b != "band"]).drop(columns="_o")
    for c in ("instances", "paired", "censored", "saves", "ties", "costs", "heavy"):
        t[c] = t[c].astype(int)
    return t.reset_index(drop=True)


def density_table(rows: pd.DataFrame, side: str = "lo", min_n: int = 30) -> pd.DataFrame:
    p = paired(rows, side)
    p = p[p.n >= min_n]
    if not len(p):
        return pd.DataFrame()
    from learning.fan_order import DENSITY_BINS
    p["density_lo"] = [next((lo for lo, hi in DENSITY_BINS if lo <= cm < hi), -1) for cm in p.col_mean]
    t = (p.groupby(["band", "density_band", "density_lo"], sort=False)
         .apply(_summarise, include_groups=False).reset_index())
    t["_o"] = t["band"].map({b: i for i, b in enumerate(FAN_BAND_ORDER)})
    t = t.sort_values(["_o", "density_lo"]).drop(columns=["_o", "density_lo"])
    for c in ("instances", "paired", "censored", "saves", "ties", "costs", "heavy"):
        t[c] = t[c].astype(int)
    return t.reset_index(drop=True)


# ----------------------------------------------------------------------------
# rules
# ----------------------------------------------------------------------------


def rule_nodes(p: pd.DataFrame, choose_on: np.ndarray, metric: str = "nodes") -> np.ndarray:
    """What a rule would have spent: the on arm where it says on, else off.
    `metric` is `"nodes"` (the primary) or `"seconds"` (the two arms ran back to
    back in one process, so the pair shares the machine's load)."""
    choose_on = np.asarray(choose_on, dtype=bool)
    return np.where(choose_on, p[f"{metric}_on"].to_numpy(), p[f"{metric}_off"].to_numpy())


def agreement_with_oracle(p: pd.DataFrame, choose_on: np.ndarray) -> float:
    """Fraction of instances on which a rule picks the cheaper arm (ties agree)."""
    choose_on = np.asarray(choose_on, dtype=bool)
    o = p.oracle.to_numpy()
    ok = (o == 0) | ((o > 0) & choose_on) | ((o < 0) & ~choose_on)
    return float(ok.mean()) if len(p) else np.nan


def fit_tree(X: pd.DataFrame, p: pd.DataFrame, depth: int = TREE_DEPTH, seed: int = 0,
             metric: str = "nodes"):
    """Depth-`depth` tree on the sign of the paired difference, decided
    non-tied pairs only, weighted by `|log10 ratio|` (in `metric`: nodes, the
    primary, or seconds). Returns the fitted tree (or None when one class is
    absent)."""
    from sklearn.tree import DecisionTreeClassifier

    if metric == "nodes":
        oracle, weight = p.oracle.to_numpy(), np.abs(p.log_ratio.to_numpy())
    else:
        oracle = np.sign(p.seconds_off.to_numpy() - p.seconds_on.to_numpy()).astype(int)
        oracle[~p.decided.to_numpy()] = 0
        with np.errstate(divide="ignore", invalid="ignore"):
            weight = np.abs(np.log10(p.seconds_on.to_numpy() / p.seconds_off.to_numpy()))
        weight = np.nan_to_num(weight, nan=0.0, posinf=0.0, neginf=0.0)
    mask = oracle != 0
    if mask.sum() < 2 or len(np.unique(oracle[mask])) < 2:
        return None
    tree = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=20, random_state=seed)
    tree.fit(X[mask], (oracle[mask] > 0).astype(int), sample_weight=weight[mask] + 1e-6)
    return tree


def learned_out_of_fold(X: pd.DataFrame, p: pd.DataFrame, groups: np.ndarray,
                        folds: int = FOLDS, depth: int = TREE_DEPTH, seed: int = 0,
                        metric: str = "nodes") -> np.ndarray:
    """Out-of-fold on/off predictions of the tree, folds grouped by `groups`."""
    from sklearn.model_selection import GroupKFold

    pred = np.zeros(len(p), dtype=bool)
    if len(np.unique(groups)) < folds:
        folds = max(2, len(np.unique(groups)))
    for train, test in GroupKFold(n_splits=folds).split(X, groups=groups):
        tree = fit_tree(X.iloc[train], p.iloc[train], depth, seed, metric)
        if tree is None:
            pred[test] = False
        else:
            pred[test] = tree.predict(X.iloc[test]).astype(bool)
    return pred


def tree_text(tree, names: list[str]) -> str:
    from sklearn.tree import export_text

    return export_text(tree, feature_names=list(names), decimals=3, show_weights=True)


def rules_table(p: pd.DataFrame, learned_on: np.ndarray, by: str = "band",
                metric: str = "nodes") -> pd.DataFrame:
    """Nodes (or seconds) spent under every rule, by group, decided pairs only;
    agreement with the node oracle; regret against the floor in `metric`.
    With `metric="seconds"` the oracle is still the node oracle, so its regret
    shows what choosing by nodes costs on the clock."""
    rules = {
        "always_off": np.zeros(len(p), dtype=bool),
        "always_on": np.ones(len(p), dtype=bool),
        "hand": p.hand_on.to_numpy().astype(bool),
        "learned": np.asarray(learned_on, dtype=bool),
        "oracle": (p.oracle > 0).to_numpy(),
    }
    out = []
    for key, g in p.groupby(by, sort=False):
        d = g[g.decided]
        idx = d.index
        rec: dict = {by: key, "instances": len(g), "paired": len(d)}
        floor = np.minimum(d[f"{metric}_on"], d[f"{metric}_off"]).sum()
        for name, choose in rules.items():
            c = choose[p.index.get_indexer(idx)]
            total = rule_nodes(d, c, metric).sum()
            rec[f"{name}_{metric}"] = float(total)
            rec[f"{name}_regret"] = float(total / floor) if floor > 0 else np.nan
            rec[f"{name}_agree"] = agreement_with_oracle(d, c)
        out.append(rec)
    t = pd.DataFrame(out)
    if by == "band":
        t["_o"] = t["band"].map({b: i for i, b in enumerate(FAN_BAND_ORDER)})
        t = t.sort_values("_o").drop(columns="_o")
    return t.reset_index(drop=True)


def clock_table(p: pd.DataFrame, min_nodes: float = 1e5, by: str = "ppc_band") -> pd.DataFrame:
    """The seconds side, on instances heavy enough to time (`nodes_off >= min_nodes`):
    per-node overhead of the on arm, node ratio, seconds ratio, and how often
    on wins on the clock. The break-even node ratio is 1 / overhead."""
    d = p[p.decided & (p.nodes_off >= min_nodes) & (p.seconds_off > 0)].copy()
    if not len(d):
        return pd.DataFrame()
    d["overhead"] = (d.seconds_on / d.nodes_on.clip(lower=1)) / (d.seconds_off / d.nodes_off.clip(lower=1))
    d["sec_ratio"] = d.seconds_on / d.seconds_off
    if by == "ppc_band" and "ppc_band" not in d.columns:
        d["ppc_band"] = pd.cut(d.products_per_customer, [0, 2, 3, 4, 5, 6, 8, 10, 15, 1e9],
                               labels=["≤2", "2–3", "3–4", "4–5", "5–6", "6–8", "8–10", "10–15", ">15"])
    def _s(g):
        return pd.Series({"instances": len(g),
                          "overhead_median": float(g.overhead.median()),
                          "overhead_p90": float(g.overhead.quantile(0.9)),
                          "node_ratio_median": float(g.ratio.median()),
                          "sec_ratio_median": float(g.sec_ratio.median()),
                          "sec_ratio_p90": float(g.sec_ratio.quantile(0.9)),
                          "on_faster": int((g.seconds_on < g.seconds_off).sum()),
                          "on_slower": int((g.seconds_on > g.seconds_off).sum()),
                          "total_sec_ratio": float(g.seconds_on.sum() / g.seconds_off.sum()),
                          "total_node_ratio": float(g.nodes_on.sum() / g.nodes_off.sum())})
    t = d.groupby(by, observed=True, sort=False).apply(_s, include_groups=False).reset_index()
    if by == "band":
        t["_o"] = t["band"].map({b: i for i, b in enumerate(FAN_BAND_ORDER)})
        t = t.sort_values("_o").drop(columns="_o")
    t["instances"] = t["instances"].astype(int)
    return t.reset_index(drop=True)


def kill_verdict(p: pd.DataFrame, learned_on: np.ndarray, threshold: float = KILL_AGREEMENT) -> dict:
    """Plan 2 §2.5b: met iff the learned boundary agrees with the hand threshold
    on more than `threshold` of instances."""
    hand = p.hand_on.to_numpy().astype(bool)
    learned = np.asarray(learned_on, dtype=bool)
    agree = float((hand == learned).mean()) if len(p) else np.nan
    return {"instances": int(len(p)), "agreement": agree, "threshold": threshold,
            "met": bool(agree > threshold) if len(p) else False,
            "hand_on_learned_off": int((hand & ~learned).sum()),
            "hand_off_learned_on": int((~hand & learned).sum())}


def hand_threshold_sweep(p: pd.DataFrame, thresholds=None, metric: str = "nodes") -> pd.DataFrame:
    """Cost of the one-statistic rule `products per customer ≤ t` for a range of
    `t`, decided pairs only: is 5 the right place for the threshold? `metric`
    is `"nodes"` (regret against the node oracle's spend) or `"seconds"`
    (regret against the seconds floor, the cheaper arm on the clock per pair;
    meaningful only on pairs heavy enough to time, see `clock_table`). The
    `agree` column is always agreement with the node oracle."""
    d = p[p.decided]
    thresholds = np.arange(0.0, 20.5, 0.5) if thresholds is None else thresholds
    if metric == "nodes":
        floor = rule_nodes(d, (d.oracle > 0).to_numpy()).sum()
    else:
        floor = np.minimum(d[f"{metric}_on"], d[f"{metric}_off"]).sum()
    out = []
    for t in thresholds:
        choose = (d.products_per_customer <= t).to_numpy()
        total = rule_nodes(d, choose, metric).sum()
        out.append({"threshold": float(t), "on_fraction": float(choose.mean()), metric: float(total),
                    "regret": float(total / floor) if floor else np.nan,
                    "agree": agreement_with_oracle(d, choose)})
    return pd.DataFrame(out)


def audit_table(rows: pd.DataFrame, fan_csv: Path = FAN_ORDER_CSV,
                scale_csv: Path = SCALE_NODES_CSV) -> pd.DataFrame:
    """Statuses must agree between the arms at both k, witnesses must be within
    the optimum, and both arms must reproduce the counts on record."""
    rec: dict = {"instances": len(rows)}
    for side in SIDES:
        a, b = rows[f"status_{side}_off"].astype(str), rows[f"status_{side}_on"].astype(str)
        both = a.isin(["sat", "unsat"]) & b.isin(["sat", "unsat"])
        rec[f"{side}_both_decided"] = int(both.sum())
        rec[f"{side}_status_disagreements"] = int((both & (a != b)).sum())
        rec[f"{side}_censored_off"] = int((a == "unknown").sum())
        rec[f"{side}_censored_on"] = int((b == "unknown").sum())
    for arm in ARMS:
        w = rows[f"witness_{arm}"].astype(float)
        hi = rows[f"status_hi_{arm}"].astype(str) == "sat"
        rec[f"witness_{arm}_bad"] = int((hi & (w > rows.optimum.astype(float))).sum())
        rec[f"witness_{arm}_missing"] = int((hi & w.isna()).sum())
    # unsat at optimum − 1 under the off arm, sat at optimum under the on arm and vice versa
    rec["contradictions"] = int(((rows.status_lo_off == "sat") | (rows.status_lo_on == "sat")
                                 | (rows.status_hi_off == "unsat") | (rows.status_hi_on == "unsat")).sum())
    ref = rows.ref_nodes_default.astype(float)
    have = ref.notna() & (rows.status_lo_off == "unsat")
    rec["off_ref_available"] = int(have.sum())
    rec["off_ref_equal"] = int((have & np.isclose(ref, rows.nodes_lo_off.astype(float), rtol=1e-5)).sum())
    if fan_csv.exists():
        fan = pd.read_csv(fan_csv, low_memory=False)[
            ["source", "instance_name", "nodes_lo_default_index", "status_lo_default_index",
             "nodes_lo_csearch_index", "status_lo_csearch_index", "nodes_hi_default_index",
             "nodes_hi_csearch_index", "status_hi_default_index", "status_hi_csearch_index"]]
        m = rows.merge(fan, on=["source", "instance_name"], how="inner")
        d = (m.status_lo_off == "unsat") & (m.status_lo_default_index == "unsat")
        rec["fan06_off_pairs"] = int(d.sum())
        rec["fan06_off_equal"] = int((d & (m.nodes_lo_off == m.nodes_lo_default_index)).sum())
        d2 = d & m.hand_on.astype(bool) & (m.status_lo_csearch_index == "unsat")
        rec["fan06_on_pairs_hand_on"] = int(d2.sum())
        rec["fan06_on_equal_hand_on"] = int((d2 & (m.nodes_lo_on == m.nodes_lo_csearch_index)).sum())
        h = (m.status_hi_off == "sat") & (m.status_hi_default_index == "sat")
        rec["fan06_hi_off_pairs"] = int(h.sum())
        rec["fan06_hi_off_equal"] = int((h & (m.nodes_hi_off == m.nodes_hi_default_index)).sum())
    return pd.DataFrame([rec]).T.rename(columns={0: "value"})


# ----------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def analyse(rows: pd.DataFrame, out: Path = TABLES, tree_txt: Path = TREE_TXT,
            seed: int = 0) -> dict:
    f = with_features(rows)
    p = paired(f, "lo")
    X = design(f)
    groups = f["group"].to_numpy()
    learned = learned_out_of_fold(X, p, groups, seed=seed)
    tree = fit_tree(X, p, seed=seed)
    verdict = kill_verdict(p, learned)
    verdict_decided = kill_verdict(p[p.decided], learned[p.decided.to_numpy()])
    # a tree that also sees n (robustness only)
    Xn = X.copy()
    Xn["n"] = f["n"].astype(float)
    learned_n = learned_out_of_fold(Xn, p, groups, seed=seed)
    verdict_n = kill_verdict(p, learned_n)

    lines = ["# Theorem 2's switch: tables", "",
             f"Regenerated by `python -m learning.theorem2 --stage tables` from `{ROWS_CSV}`. ",
             "`ratio` is `(nodes_on + 1) / (nodes_off + 1)` on the refutation `decide(optimum − 1)` "
             "unless the table says `hi` (the witness search `decide(optimum)`); censored calls are "
             "counted and excluded from ratio statistics. `hand_on` is `sparse_enough_for_better_move` "
             "(mean products per customer ≤ 5). `sec_per_node_ratio` is the median over instances with "
             "≥ 10⁴ off-nodes of (seconds/node on) / (seconds/node off).", ""]
    lines += ["## Audit", "", audit_table(rows).to_markdown(), ""]
    lines += ["## Refutation: paired ratio by size band and the hand switch", "",
              _md(paired_table(rows, "lo", ("band", "hand_on"))), ""]
    lines += ["## Refutation: by size band and realised density (n ≥ 30)", "",
              _md(density_table(rows, "lo")), ""]
    lines += ["## Refutation: by products per customer (the hand statistic), n ≥ 30", ""]
    q = p[(p.n >= 30)].copy()
    q["ppc_band"] = pd.cut(q.products_per_customer, [0, 2, 3, 4, 5, 6, 8, 10, 15, 1e9],
                           labels=["≤2", "2–3", "3–4", "4–5", "5–6", "6–8", "8–10", "10–15", ">15"])
    if len(q):
        t = q.groupby(["ppc_band"], observed=True).apply(_summarise, include_groups=False).reset_index()
        lines += [_md(t), ""]
    lines += ["## Rules: nodes spent, regret against the oracle, agreement with the oracle", "",
              _md(rules_table(p, learned)), ""]
    lines += ["## Rules by hand switch", "", _md(rules_table(p, learned, by="hand_on")), ""]
    lines += ["## The one-statistic threshold swept", "", _md(hand_threshold_sweep(p)), ""]
    lines += ["## The clock: per-node overhead and seconds ratio, refutations with ≥ 10⁵ off-nodes", "",
              "By products per customer:", "", _md(clock_table(p, by="ppc_band")), "",
              "By hand switch:", "", _md(clock_table(p, by="hand_on")), "",
              "By size band:", "", _md(clock_table(p, by="band")), ""]
    heavy = p[p.decided & (p.nodes_off >= 1e5)]
    lines += ["## The one-statistic threshold swept on the clock (refutations with ≥ 10⁵ off-nodes; "
              "`seconds` is what the rule would have spent, regret against the per-pair cheaper arm)", "",
              _md(hand_threshold_sweep(heavy, thresholds=np.arange(0.0, 12.5, 0.5), metric="seconds")), ""]
    lines += ["## Rules on the clock (seconds, same instances; regret against the seconds floor)", "",
              _md(rules_table(heavy, learned[heavy.index.get_indexer(heavy.index)] if False else
                              np.asarray(learned)[p.index.get_indexer(heavy.index)], by="hand_on",
                              metric="seconds")), "",
              _md(rules_table(heavy, np.asarray(learned)[p.index.get_indexer(heavy.index)], by="band",
                              metric="seconds")), ""]
    lines += ["## Kill: agreement of the learned boundary with the hand threshold", "",
              pd.DataFrame([{"variant": "size-free, all instances", **verdict},
                            {"variant": "size-free, decided pairs", **verdict_decided},
                            {"variant": "size-free + n, all instances", **verdict_n}]).to_markdown(index=False), ""]
    if tree is not None:
        txt = tree_text(tree, list(X.columns))
        tree_txt.parent.mkdir(parents=True, exist_ok=True)
        tree_txt.write_text(txt)
        lines += ["## The learned boundary (fitted on every decided non-tied pair)", "", "```",
                  txt.rstrip(), "```", ""]
    heavy_idx = p.index[p.decided & (p.nodes_off >= 1e5)]
    hp, hX, hg = p.loc[heavy_idx], X.loc[heavy_idx], f.loc[heavy_idx, "group"].to_numpy()
    verdict_clock = None
    if len(hp) >= 40:
        learned_clock = learned_out_of_fold(hX, hp, hg, seed=seed, metric="seconds")
        verdict_clock = kill_verdict(hp, learned_clock)
        clock_tree = fit_tree(hX, hp, seed=seed, metric="seconds")
        lines += ["## The boundary fitted to the clock (refutations with ≥ 10⁵ off-nodes, seconds sign)", "",
                  pd.DataFrame([{"variant": "size-free, heavy instances, seconds", **verdict_clock}])
                  .to_markdown(index=False), ""]
        if clock_tree is not None:
            lines += ["```", tree_text(clock_tree, list(hX.columns)).rstrip(), "```", ""]
    lines += ["## Where Theorem 2 costs most (refutation, decided pairs)", ""]
    worst = p[p.decided & (p.nodes_on > p.nodes_off)].sort_values("ratio", ascending=False).head(15)
    lines += [_md(worst[["source", "instance_name", "n", "m", "products_per_customer", "hand_on",
                         "nodes_off", "nodes_on", "ratio", "seconds_off", "seconds_on"]]), ""]
    lines += ["## Where Theorem 2 saves most (refutation, decided pairs, ≥ 10⁵ off-nodes)", ""]
    best = p[p.decided & (p.nodes_off >= 1e5)].sort_values("ratio").head(15)
    lines += [_md(best[["source", "instance_name", "n", "m", "products_per_customer", "hand_on",
                        "nodes_off", "nodes_on", "ratio", "seconds_off", "seconds_on"]]), ""]
    lines += ["## Corpus at 41–125 by class", ""]
    c = p[(p.source == "corpus") & (p.n > 40)].copy()
    c["cls"] = c.instance_name.str.rsplit("-", n=1).str[0].where(
        c.instance_name.str.startswith("Random"), c.cell)
    if len(c):
        lines += [_md(c.groupby("cls", sort=False).apply(_summarise, include_groups=False).reset_index()), ""]
    lines += ["## Witness search `decide(optimum)`: paired ratio by size band and the hand switch", "",
              _md(paired_table(rows, "hi", ("band", "hand_on"))), ""]
    ph = paired(f, "hi")
    lines += ["## Witness search: rules", "", _md(rules_table(ph, learned)), ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return {"verdict": verdict, "verdict_decided": verdict_decided, "verdict_n": verdict_n,
            "verdict_clock": verdict_clock,
            "paired": p, "learned": learned, "tree": tree, "features": list(X.columns)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=["run", "tables"], default="run")
    ap.add_argument("--source", choices=["both", "campaign", "corpus"], default="both")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--campaign-max-n", type=int, default=CAMPAIGN_MAX_N)
    ap.add_argument("--corpus-max-n", type=int, default=CORPUS_MAX_N)
    args = ap.parse_args()
    if args.stage == "run":
        jobs = targets(args.campaign_max_n, args.corpus_max_n, args.source, args.limit)
        print(f"{len(jobs)} instances", flush=True)
        rows = run(jobs, workers=args.workers)
    else:
        rows = pd.read_csv(ROWS_CSV, low_memory=False)
    res = analyse(rows)
    print(f"tables → {TABLES}")
    for k in ("verdict", "verdict_decided", "verdict_n", "verdict_clock"):
        print(k, res[k])


if __name__ == "__main__":
    main()
