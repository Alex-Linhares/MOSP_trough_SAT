"""Does the rate keep falling? The ridge law refitted with the 100 cell (loop0004 item 08, `reports/ml_nature.md` §35).

Question. §11 fitted the nodes to refute `optimum − 1` on the `m = n` ridge
(three customers per product) as an exponential in `n` at 0.095 log10 per
customer; §16 found that rate drifting down by 0.002 per ten customers from
10 to 75 and, corrected for the drift, predicted the two `Random-125-125-2`
recertify counts to 0.04 decades; §34 then certified the 100 cell as far as
28 core-hours allow and found every one of its 25 counts *above* the drifting
law's band. This module refits the law with the 100 cell — one exact count
and twenty-four censored lower bounds, so the fit is a Tobit — predicts 125
with a band, and compares with the six 125 × 125 recertify counts on record
**like with like**: those counts are pre-fix `csearch` numbers, so the module
also measures the pre-fix `csearch` search on the 100 cell (item 04's `prefix`
variant, which reproduces the pre-fix counts to the node, §31) and fits the
pre-fix series 10 → 100 against them. It states whether the curve is
sub-exponential, whether the drift saturates, and what the day-long classes
cost under each reading.

Method. Instance-level `log10(1 + nodes)` per size; a censored call is a lower
bound and enters the likelihood as a survival term (`Φ`), never as a value;
three shapes — exponential `a + b n`, quadratic `a + b n + c n²` (§16's linear
drift), power law `a + b log10 n` — fitted by maximum likelihood with a
size-dependent scale `σ(n) = exp(s0 + s1 n)`, on 10–75 (what §16 saw) and on
10–100 (with the cell), compared by AIC; 90% bands on the 125 median by a
stratified bootstrap over instances within cells; the reading of the 100
cell varied (censored, as exact — the lower-bound reading — and dropped).
Nothing here is a bound, no solver default changes, nothing is written to
`solutions/`; the pre-fix run's witnesses, if any, go under
`learning/data/ensemble/solutions/` like §34's.

Usage:
    python -m learning.rate_drift --stage prefix-run --workers 16 --deadline 2400 --wall 4500
                                                    # pre-fix csearch at value − 1 on the 25 ridge-100 instances (resumable)
    python -m learning.rate_drift --stage tables --resamples 200 --workers 8   # reports/rate_drift_tables.md
    python -m pytest tests/test_rate_drift.py -q
"""
from __future__ import annotations

import argparse
import multiprocessing
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

from learning.ensemble import SOLUTIONS_DIR
from learning.ridge100 import CALLS_CSV, CELL, PRICE_CSV, generate, instance_states, load_calls, save_witness

ENSEMBLE_DIR = Path("learning/data/ensemble")
PREFIX_CSV = ENSEMBLE_DIR / "ridge100_prefix_calls.csv"
TABLES = Path("reports/rate_drift_tables.md")
RECERTIFY = Path("recertify/results.json")
SCALE_NODES = ENSEMBLE_DIR / "scale_nodes.csv"
PREFIX_COLUMNS = ["instance_name", "config", "k", "status", "nodes", "seconds", "deadline_seconds",
                  "achieved", "started", "finished"]
PREFIX_KW = {"old_close_count": True, "old_rule_order": True}   # item 04's `prefix` variant: the rule before 0eb33915
NODES_PER_SECOND = (1.4e6, 1.8e6)     # §16's measured rate on n ≥ 75 refutations, §34's on the 100 cell
SEED = 0


# ----------------------------------------------------------------------------
# the pre-fix csearch run on the 100 cell
# ----------------------------------------------------------------------------


def ridge100_values() -> dict[str, dict]:
    """Each ridge-100 instance's value (certified or verified upper bound) and index, from §34's calls."""
    calls = load_calls(CALLS_CSV)
    price = pd.read_csv(PRICE_CSV)
    ubs = dict(zip(price["instance_name"], price["ub_best"]))
    states = instance_states(calls, ubs)
    index = dict(zip(price["instance_name"], price["index"]))
    return {name: {"value": s["value"], "certified": s["certified"], "index": int(index[name])}
            for name, s in states.items()}


def _prefix_job(args) -> dict:
    """One `decide` at `k` under the pre-fix csearch rule (Theorem 2 on, old close count, old rule order)."""
    from mosp.verify import max_open_stacks
    from satisfiability.customer_search import decide, sparse_enough_for_better_move
    from satisfiability.heuristics import product_order_from_customers

    name, index, k, deadline_seconds = args
    inst = generate(CELL, index)
    assert inst.name == name
    started = time.time()
    t0 = time.monotonic()
    answer = decide(inst, k, deadline=t0 + deadline_seconds, better_move=bool(sparse_enough_for_better_move(inst)),
                    better_move_dominators=0, **PREFIX_KW)
    seconds = time.monotonic() - t0
    row = {"instance_name": name, "config": "csearch-prefix", "k": k, "status": answer.status,
           "nodes": answer.nodes, "seconds": round(seconds, 3), "deadline_seconds": deadline_seconds,
           "achieved": None, "started": round(started, 1), "finished": round(time.time(), 1)}
    if answer.status == "sat":
        ordering = product_order_from_customers(inst, answer.order)
        row["achieved"] = int(max_open_stacks(inst, ordering))
        row["ordering"] = ordering
    return row


def load_prefix(path: Path = PREFIX_CSV) -> pd.DataFrame:
    if path.exists() and path.stat().st_size:
        return pd.read_csv(path)
    return pd.DataFrame(columns=PREFIX_COLUMNS)


def _append(row: dict, path: Path) -> None:
    frame = pd.DataFrame([{c: row.get(c) for c in PREFIX_COLUMNS}])
    frame.to_csv(path, mode="a", header=not (path.exists() and path.stat().st_size), index=False)


def prefix_run(workers: int = 16, deadline: float = 2400.0, wall: float = 4500.0, min_call: float = 300.0,
               out: Path = PREFIX_CSV, verbose: bool = True) -> pd.DataFrame:
    """Pre-fix csearch at `value − 1` for every ridge-100 instance not yet recorded.

    One job per instance, dispatched to at most `workers` at a time; each
    call's deadline is capped by the wall so nothing is lost in flight; a call
    that expires is a censored lower bound. Resumable: instances with a row
    in `out` are skipped. A `sat` answer (the value was not optimal) is
    re-simulated and its witness saved monotonically under the ensemble's
    solutions directory, never `solutions/`.
    """
    values = ridge100_values()
    done = set(load_prefix(out)["instance_name"])
    jobs = [(name, v["index"], v["value"] - 1) for name, v in sorted(values.items()) if name not in done]
    if verbose:
        print(f"prefix-run: {len(jobs)} calls to make, {len(done)} recorded, {workers} workers, "
              f"deadline {deadline:.0f} s, wall {wall:.0f} s", flush=True)
    t_end = time.monotonic() + wall
    pending = list(jobs)
    running: dict = {}
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        while pending or running:
            remaining = t_end - time.monotonic()
            while pending and len(running) < workers and remaining > min_call:
                name, index, k = pending.pop(0)
                this = min(deadline, remaining - 10.0)
                running[name] = pool.apply_async(_prefix_job, ((name, index, k, this),))
            for name in list(running):
                r = running[name]
                if r.ready():
                    row = r.get()
                    del running[name]
                    _append(row, out)
                    if row["status"] == "sat":
                        save_witness(generate(CELL, values[name]["index"]), row["achieved"], row["ordering"], False)
                    if verbose:
                        print(f"  {name} k={row['k']} {row['status']} {row['nodes']:,} nodes {row['seconds']:.0f} s",
                              flush=True)
            if remaining <= min_call and pending:
                if verbose:
                    print(f"  wall: {len(pending)} calls not dispatched", flush=True)
                pending = []
            if not running and not pending:
                break
            time.sleep(2.0)
    return load_prefix(out)


# ----------------------------------------------------------------------------
# the series: instance-level log10(1 + nodes) per size, censoring kept
# ----------------------------------------------------------------------------

SERIES_COLUMNS = ["instance_name", "n", "d", "config", "log_nodes", "censored", "source", "value_certified"]


def campaign_series(config: str, d: float = 3.0, max_n: int = 75) -> pd.DataFrame:
    """§10's and §16's certified `m = n` fixed-`d` refutations at 10–`max_n`.

    Under `csearch` these are pre-fix counts (recorded before 2026-09-26 12:19);
    under `default` the fix does not apply. `config` may be `default`,
    `csearch` or `csearch-prefix` (the last two read the same recorded column).
    """
    from learning.upward import load_all

    col = "csearch" if config.startswith("csearch") else "default"
    f = load_all()
    s = f[(f["generator"] == "fixed") & (f["ratio"] == 1.0) & (f["param"] == d)
          & f["certified"].astype(bool) & (f["n"] <= max_n)]
    return pd.DataFrame({"instance_name": s["instance_name"].to_numpy(), "n": s["n"].astype(int).to_numpy(),
                         "d": d, "config": config, "log_nodes": s[f"ln_{col}"].to_numpy(float),
                         "censored": s[f"cens_{col}"].to_numpy(bool), "source": "campaign",
                         "value_certified": True})


def upward100_series(config: str, d: float = 4.0) -> pd.DataFrame:
    """§16(d)'s five-instance sample at 100 for a neighbour cell (`d = 4`):
    one certified count and four censored lower bounds at 1,500 s on values
    that are verified upper bounds. `sat` answers are excluded (they are not
    refutation counts). Under `csearch` these are pre-fix counts."""
    from learning.upward import load_all

    col = "csearch" if config.startswith("csearch") else "default"
    f = load_all()
    s = f[(f["generator"] == "fixed") & (f["ratio"] == 1.0) & (f["param"] == d) & (f["n"] == 100)]
    s = s[s[f"status_{col}"].isin(["unsat", "unknown"])]
    return pd.DataFrame({"instance_name": s["instance_name"].to_numpy(), "n": 100, "d": d, "config": config,
                         "log_nodes": s[f"ln_{col}"].to_numpy(float), "censored": s[f"cens_{col}"].to_numpy(bool),
                         "source": "upward-sample", "value_certified": s["certified"].astype(bool).to_numpy()})


def ridge100_series(config: str, prefix_csv: Path = PREFIX_CSV, calls_csv: Path = CALLS_CSV,
                    price_csv: Path = PRICE_CSV) -> pd.DataFrame:
    """§34's 100 cell at `value − 1`: `default` (1 exact, 23 censored),
    `csearch` post-fix (1 exact, 24 censored) or `csearch-prefix` (this
    module's run). An instance whose value the pre-fix run shows not to be
    optimal (`sat` at `value − 1`) is excluded from every configuration: its
    censored counts bound a witness search, not the refutation."""
    calls = load_calls(calls_csv)
    price = pd.read_csv(price_csv)
    states = instance_states(calls, dict(zip(price["instance_name"], price["ub_best"])))
    prefix = load_prefix(prefix_csv)
    not_optimal = set(prefix[prefix["status"] == "sat"]["instance_name"])
    rows = []
    for name, st in sorted(states.items()):
        if name in not_optimal:
            continue
        k = st["value"] - 1
        if config == "csearch-prefix":
            at = prefix[(prefix["instance_name"] == name) & (prefix["k"] == k)]
        else:
            at = calls[(calls["instance_name"] == name) & (calls["k"] == k) & (calls["config"] == config)]
        at = at[at["status"].isin(["unsat", "unknown"])]
        if at.empty:
            continue
        r = at.iloc[0]
        rows.append({"instance_name": name, "n": 100, "d": 3.0, "config": config,
                     "log_nodes": float(np.log10(1.0 + float(r["nodes"]))), "censored": r["status"] == "unknown",
                     "source": "ridge100" if config != "csearch-prefix" else "prefix-run",
                     "value_certified": bool(st["certified"])})
    return pd.DataFrame(rows, columns=SERIES_COLUMNS)


def series(config: str, d: float = 3.0, with_100: bool = True) -> pd.DataFrame:
    """The whole series for one configuration and density: 10–75 from the
    campaign, 100 from §34 (`d = 3`) or §16(d) (`d = 4`)."""
    parts = [campaign_series(config, d)]
    if with_100:
        parts.append(ridge100_series(config) if d == 3.0 else upward100_series(config, d))
    return pd.concat(parts, ignore_index=True)


# ----------------------------------------------------------------------------
# censored maximum likelihood (Tobit) for three shapes of law
# ----------------------------------------------------------------------------

MODELS = {
    "exponential": 2,   # a + b n
    "quadratic": 3,     # a + b n + c n^2       (§16's linear drift: rate = b + 2 c n)
    "power": 2,         # a + b log10 n
    "saturating": 4,    # rate(n) = b_inf + (b0 - b_inf) exp(-n / tau)
}


def mean_of(model: str, theta: np.ndarray, n: np.ndarray) -> np.ndarray:
    n = np.asarray(n, dtype=float)
    if model == "exponential":
        return theta[0] + theta[1] * n
    if model == "quadratic":
        return theta[0] + theta[1] * n + theta[2] * n ** 2
    if model == "power":
        return theta[0] + theta[1] * np.log10(n)
    if model == "saturating":
        a, b_inf, b0, log_tau = theta
        tau = np.exp(log_tau)
        return a + b_inf * n - tau * (b0 - b_inf) * np.exp(-n / tau)
    raise ValueError(model)


def rate_of(model: str, theta: np.ndarray, n: np.ndarray) -> np.ndarray:
    """d mean / d n: the local rate in log10 per customer."""
    n = np.asarray(n, dtype=float)
    if model == "exponential":
        return np.full_like(n, theta[1])
    if model == "quadratic":
        return theta[1] + 2 * theta[2] * n
    if model == "power":
        return theta[1] / (n * np.log(10))
    if model == "saturating":
        a, b_inf, b0, log_tau = theta
        return b_inf + (b0 - b_inf) * np.exp(-n / np.exp(log_tau))
    raise ValueError(model)


def _negloglik(params: np.ndarray, model: str, n: np.ndarray, y: np.ndarray, cens: np.ndarray) -> float:
    k = MODELS[model]
    theta, s0, s1 = params[:k], params[k], params[k + 1]
    mu = mean_of(model, theta, n)
    sigma = np.exp(s0 + s1 * (n - 50.0) / 50.0)
    z = (y - mu) / sigma
    ll = np.where(cens, stats.norm.logsf(z), stats.norm.logpdf(z) - np.log(sigma))
    return -float(np.sum(ll))


def _start(model: str, n: np.ndarray, y: np.ndarray, cens: np.ndarray) -> np.ndarray:
    ex = ~cens
    nn, yy = n[ex], y[ex]
    if model == "exponential":
        b, a = np.polyfit(nn, yy, 1)
        theta = [a, b]
    elif model == "quadratic":
        c, b, a = np.polyfit(nn, yy, 2)
        theta = [a, b, c]
    elif model == "power":
        b, a = np.polyfit(np.log10(nn), yy, 1)
        theta = [a, b]
    else:
        b, a = np.polyfit(nn, yy, 1)
        theta = [a, b, b * 1.2, np.log(50.0)]
    resid = yy - mean_of(model, np.array(theta), nn)
    return np.array(list(theta) + [np.log(max(np.std(resid), 0.05)), 0.3])


def fit(frame: pd.DataFrame, model: str = "quadratic", n_min: int = 10, n_max: int = 100) -> dict:
    """Censored maximum likelihood of one law on the rows with `n_min ≤ n ≤ n_max`.

    Returns the parameters, the scale at 75 and 100, the log-likelihood, AIC,
    the fitted mean at 75 / 100 / 125 and the local rate at 40 / 75 / 100 /
    125, and how many exact and censored rows entered.
    """
    sub = frame[(frame["n"] >= n_min) & (frame["n"] <= n_max)]
    n = sub["n"].to_numpy(float)
    y = sub["log_nodes"].to_numpy(float)
    cens = sub["censored"].to_numpy(bool)
    x0 = _start(model, n, y, cens)
    best = None
    for method in ("Nelder-Mead", "BFGS"):
        try:
            res = optimize.minimize(_negloglik, x0 if best is None else best.x, args=(model, n, y, cens),
                                    method=method, options={"maxiter": 20000, "xatol": 1e-8, "fatol": 1e-10}
                                    if method == "Nelder-Mead" else {"maxiter": 2000})
        except Exception:
            continue
        if best is None or res.fun < best.fun:
            best = res
    k = MODELS[model]
    theta = best.x[:k]
    s0, s1 = best.x[k], best.x[k + 1]
    ll = -best.fun
    out = {"model": model, "n_min": n_min, "n_max": n_max, "exact": int((~cens).sum()), "censored": int(cens.sum()),
           "theta": theta.tolist(), "sigma_75": float(np.exp(s0 + s1 * 0.5)), "sigma_100": float(np.exp(s0 + s1 * 1.0)),
           "loglik": ll, "aic": 2 * (k + 2) - 2 * ll}
    for t in (75, 100, 125):
        out[f"mean_{t}"] = float(mean_of(model, theta, np.array([t]))[0])
    for t in (40, 75, 100, 125):
        out[f"rate_{t}"] = float(rate_of(model, theta, np.array([t]))[0])
    return out


def _boot_chunk(args) -> list[dict]:
    records, model, n_min, n_max, seeds, targets = args
    sub = pd.DataFrame.from_records(records)
    groups = [g.index.to_numpy() for _, g in sub.groupby("n")]
    out = []
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        idx = np.concatenate([rng.choice(g, size=len(g), replace=True) for g in groups])
        try:
            r = fit(sub.iloc[idx], model, n_min, n_max)
        except Exception:
            continue
        out.append({t: r[t] for t in targets})
    return out


def bootstrap_fit(frame: pd.DataFrame, model: str, n_min: int, n_max: int, resamples: int = 300,
                  seed: int = SEED, targets=("mean_125", "mean_100", "rate_100", "rate_75"),
                  workers: int = 1) -> dict:
    """Stratified bootstrap: resample instances within each size cell, refit,
    return 5th / 50th / 95th percentiles of the fitted quantities. With
    `workers > 1` the resamples are split over a spawned pool."""
    sub = frame[(frame["n"] >= n_min) & (frame["n"] <= n_max)].reset_index(drop=True)
    records = sub[["n", "log_nodes", "censored"]].to_dict("records")
    seeds = np.random.default_rng(seed).integers(0, 2 ** 31 - 1, size=resamples)
    chunks = [(records, model, n_min, n_max, seeds[i::max(workers, 1)], targets) for i in range(max(workers, 1))]
    if workers > 1:
        with multiprocessing.get_context("spawn").Pool(workers) as pool:
            parts = pool.map(_boot_chunk, chunks)
    else:
        parts = [_boot_chunk(c) for c in chunks]
    draws = [d for part in parts for d in part]
    out = {}
    for t in targets:
        v = np.asarray([d[t] for d in draws], dtype=float)
        if len(v):
            out[f"{t}_lo"], out[f"{t}_med"], out[f"{t}_hi"] = (float(np.percentile(v, 5)), float(np.percentile(v, 50)),
                                                              float(np.percentile(v, 95)))
    out["resamples"] = len(draws)
    return out


def cell_location(frame: pd.DataFrame, n: int, sigma: float) -> dict:
    """The censored-normal MLE of one cell's location with the scale held at
    `sigma` (taken from the last fully certified cell), and its 90% profile
    interval. With one exact count and twenty-four lower bounds this is what
    the cell says its median is, not what its censored median reads."""
    sub = frame[frame["n"] == n]
    y, cens = sub["log_nodes"].to_numpy(float), sub["censored"].to_numpy(bool)

    def nll(mu):
        z = (y - mu) / sigma
        return -float(np.sum(np.where(cens, stats.norm.logsf(z), stats.norm.logpdf(z) - np.log(sigma))))

    grid = np.linspace(y.min() - 1.0, y.max() + 3.0, 4001)
    vals = np.array([nll(m) for m in grid])
    i = int(np.argmin(vals))
    inside = grid[vals <= vals[i] + stats.chi2.ppf(0.90, 1) / 2]
    return {"n": n, "instances": len(y), "exact": int((~cens).sum()), "censored": int(cens.sum()),
            "sigma_used": sigma, "censored_median": float(np.median(y)),
            "location": float(grid[i]), "location_lo": float(inside.min()),
            "location_hi": float(inside.max()) if vals[-1] > vals[i] + stats.chi2.ppf(0.90, 1) / 2 else np.inf}


# ----------------------------------------------------------------------------
# what is on record at 100 and 125
# ----------------------------------------------------------------------------


def recertify_counts(path: Path = RECERTIFY) -> pd.DataFrame:
    """The six 125 × 125 counts: pre-fix `csearch` (workers forked 2026-09-24, fix 2026-09-26)."""
    from learning.upward import recertify_counts as _rc
    rec = _rc(path)
    rec["rule"] = "pre-fix csearch"
    return rec


def corpus100(path: Path = SCALE_NODES) -> pd.DataFrame:
    """§14's counts on Chu & Stuckey's `Random-100-100-2` and `-4` at 1,500 s:
    `default` and pre-fix `csearch`, censored ones as lower bounds."""
    s = pd.read_csv(path)
    s = s[s["instance_name"].str.match(r"Random-100-100-[24]-")].copy()
    s["d"] = s["instance_name"].str.split("-").str[3].astype(int)
    s["log_nodes"] = np.log10(1.0 + s["nodes"].astype(float)).round(2)
    s["censored"] = s["status"].eq("unknown")
    return s[["instance_name", "d", "optimum", "config", "status", "log_nodes", "censored", "seconds"]] \
        .sort_values(["d", "config", "instance_name"]).reset_index(drop=True)


def fix_cost_100(prefix_csv: Path = PREFIX_CSV, calls_csv: Path = CALLS_CSV, price_csv: Path = PRICE_CSV) -> pd.DataFrame:
    """Per ridge-100 instance: post-fix `csearch` count at `value − 1` (§34)
    against the pre-fix count (this run), both readings kept; the ratio is
    exact when both settled, a lower bound when only the post-fix call
    censored, and unreadable when the pre-fix call censored too."""
    post = ridge100_series("csearch", prefix_csv, calls_csv, price_csv).set_index("instance_name")
    pre = ridge100_series("csearch-prefix", prefix_csv, calls_csv, price_csv).set_index("instance_name")
    prefix = load_prefix(prefix_csv).set_index("instance_name")
    rows = []
    for name in sorted(set(post.index) | set(prefix.index)):
        row = {"instance_name": name, "value_certified": bool(post["value_certified"].get(name, False))}
        if name in post.index:
            row["post_log"], row["post_censored"] = float(post.loc[name, "log_nodes"]), bool(post.loc[name, "censored"])
        if name in prefix.index:
            r = prefix.loc[name]
            row["pre_status"] = r["status"]
            row["pre_log"] = float(np.log10(1.0 + float(r["nodes"])))
            row["pre_seconds"] = float(r["seconds"])
        if "post_log" in row and "pre_log" in row and row["pre_status"] != "sat":
            ratio = 10 ** (row["post_log"] - row["pre_log"])
            pre_c = row["pre_status"] == "unknown"
            row["ratio"] = ratio if not (pre_c and row["post_censored"]) else np.nan   # two lower bounds have no ratio
            row["ratio_reading"] = ("exact" if not row["post_censored"] and not pre_c else
                                    "lower bound" if row["post_censored"] and not pre_c else
                                    "upper bound" if pre_c and not row["post_censored"] else "both censored")
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# the readings of 125
# ----------------------------------------------------------------------------

SEC16 = {   # §16(e): from the 75 cell, the 60 → 75 rate constant / drifting at the pooled slope; log10 nodes, [90% band]
    ("default", 3.0): {"const_125": (11.54, 10.82, 12.23), "drift_125": (11.18, 10.39, 11.96),
                       "const_100": (9.16, 8.80, 9.51), "drift_100": (9.05, 8.67, 9.42)},
    ("csearch-prefix", 3.0): {"const_125": (11.28, 10.68, 11.63), "drift_125": (11.00, 10.33, 11.42),
                              "const_100": (8.97, 8.67, 9.14), "drift_100": (8.89, 8.56, 9.08)},
    ("default", 4.0): {"const_125": (10.98, 10.67, 11.33), "drift_125": (10.62, 10.25, 11.05),
                       "const_100": (8.80, 8.65, 8.98), "drift_100": (8.69, 8.52, 8.89)},
    ("csearch-prefix", 4.0): {"const_125": (10.89, 10.60, 11.28), "drift_125": (10.61, 10.25, 11.07),
                              "const_100": (8.73, 8.59, 8.93), "drift_100": (8.65, 8.48, 8.86)},
}
CLASS_OF = {3.0: "Random-125-125-2 (col_mean 2.76; generated 3.04)", 4.0: "Random-125-125-4 (col_mean 4.24; generated 4.01)"}


def hours(log_nodes: float, nodes_per_second: float = NODES_PER_SECOND[0]) -> float:
    return 10 ** log_nodes / nodes_per_second / 3600.0


READINGS = (("exponential", 10, 100), ("quadratic", 10, 100), ("power", 10, 100), ("saturating", 10, 100),
            ("exponential", 40, 100), ("quadratic", 40, 100))


def readings_table(frame: pd.DataFrame, config: str, d: float, resamples: int = 300,
                   readings=READINGS, workers: int = 1) -> pd.DataFrame:
    """Every reading of 125 for one series: §16(e)'s two, and the Tobit refits
    per model and window with the cell read three ways (censored, as exact,
    dropped). Bands: §16's as published; the refits' by bootstrap."""
    rows = []
    for key, label in (("drift_125", "§16(e) drifting from 75"), ("const_125", "§16(e) constant from 75")):
        m, lo, hi = SEC16[(config, d)][key]
        m100, lo100, hi100 = SEC16[(config, d)][key.replace("125", "100")]
        rows.append({"reading": label, "cell_100": "not used", "mean_100": m100, "band_100": f"[{lo100:.2f}, {hi100:.2f}]",
                     "mean_125": m, "lo_125": lo, "hi_125": hi, "rate_100": np.nan, "curvature": np.nan, "aic": np.nan})
    variants = {"censored": frame,
                "as exact (lower-bound reading)": frame.assign(censored=False),
                "dropped": frame[frame["n"] < 100]}
    for (model, n_min, n_max) in readings:
        for how, fr in variants.items():
                if how != "censored" and (model != "quadratic" or n_min != 10):
                    continue          # the sensitivity is shown on §16's model and window only
                r = fit(fr, model, n_min, n_max)
                b = bootstrap_fit(fr, model, n_min, n_max, resamples=resamples, workers=workers)
                rows.append({"reading": f"Tobit {model} {n_min}–{n_max}", "cell_100": how,
                             "mean_100": r["mean_100"], "band_100": f"[{b.get('mean_100_lo', np.nan):.2f}, {b.get('mean_100_hi', np.nan):.2f}]",
                             "mean_125": r["mean_125"], "lo_125": b.get("mean_125_lo", np.nan), "hi_125": b.get("mean_125_hi", np.nan),
                             "rate_100": r["rate_100"], "rate_100_band": f"[{b.get('rate_100_lo', np.nan):.4f}, {b.get('rate_100_hi', np.nan):.4f}]",
                             "rate_75": r["rate_75"],
                             "curvature": r["theta"][2] if model == "quadratic" else np.nan,
                             "aic": r["aic"], "sigma_100": r["sigma_100"]})
    # the pointwise readings: §16(e)'s method one cell up — the 100 cell's location (censored-normal MLE,
    # σ from the 75 cell) plus a rate held constant over 100 → 125: the 75 → 100 rate the location implies,
    # and the 60 → 75 rate (the drift's last exact value, if the rise were the cell's and not the law's)
    med75 = float(frame[frame["n"] == 75]["log_nodes"].median())
    med60 = float(frame[frame["n"] == 60]["log_nodes"].median())
    loc = cell_location(frame, 100, float(frame[frame["n"] == 75]["log_nodes"].std()))
    r_75_100 = (loc["location"] - med75) / 25.0
    r_lo, r_hi = (loc["location_lo"] - med75) / 25.0, (loc["location_hi"] - med75) / 25.0
    r_60_75 = (med75 - med60) / 15.0
    rows.append({"reading": "100-cell location + 75→100 rate held", "cell_100": "censored (location MLE)",
                 "mean_100": loc["location"], "band_100": f"[{loc['location_lo']:.2f}, {loc['location_hi']:.2f}]",
                 "mean_125": loc["location"] + 25 * r_75_100, "lo_125": loc["location_lo"] + 25 * r_lo,
                 "hi_125": loc["location_hi"] + 25 * r_hi, "rate_100": r_75_100,
                 "rate_100_band": f"[{r_lo:.4f}, {r_hi:.4f}]", "rate_75": r_60_75, "curvature": np.nan, "aic": np.nan})
    rows.append({"reading": "100-cell location + 60→75 rate held", "cell_100": "censored (location MLE)",
                 "mean_100": loc["location"], "band_100": f"[{loc['location_lo']:.2f}, {loc['location_hi']:.2f}]",
                 "mean_125": loc["location"] + 25 * r_60_75, "lo_125": loc["location_lo"] + 25 * r_60_75,
                 "hi_125": loc["location_hi"] + 25 * r_60_75, "rate_100": r_60_75,
                 "rate_100_band": "", "rate_75": r_60_75, "curvature": np.nan, "aic": np.nan})
    out = pd.DataFrame(rows)
    out["hours_125_1core"] = out["mean_125"].map(lambda v: hours(v))
    return out


def compare_with_record(readings: pd.DataFrame, rec: pd.DataFrame, d: float) -> pd.DataFrame:
    """For each reading: how many of the on-record 125 counts of the analogue
    class fall inside its band, and the signed distance of the class median."""
    cls = 2 if d == 3.0 else 4
    counts = rec[rec["d"] == cls]["log_nodes"].to_numpy(float)
    out = readings.copy()
    out["record_counts"] = ", ".join(f"{c:.2f}" for c in counts)
    out["record_inside_band"] = [int(np.sum((counts >= lo) & (counts <= hi))) if np.isfinite(lo) and np.isfinite(hi) else -1
                                 for lo, hi in zip(out["lo_125"], out["hi_125"])]
    out["record_median_minus_mean"] = float(np.median(counts)) - out["mean_125"]
    return out


def fix_ratio_summary(fc: pd.DataFrame) -> dict:
    """The post-fix / pre-fix csearch ratio on the 100 cell: exact where both
    settled, a lower bound where only the post-fix call censored; the summary
    is the median over both kinds (a lower bound whenever any censored pair
    enters) and the exact values listed."""
    if "ratio" not in fc.columns:
        return {"pairs": 0}
    readable = fc[fc["ratio_reading"].isin(["exact", "lower bound"])]
    exact = fc[fc["ratio_reading"] == "exact"]["ratio"]
    return {"pairs": int(len(readable)), "exact_pairs": int(len(exact)),
            "exact_ratios": ", ".join(f"{v:.2f}" for v in exact),
            "median_ratio": float(readable["ratio"].median()) if len(readable) else np.nan,
            "median_is_lower_bound": bool((readable["ratio_reading"] == "lower bound").any()),
            "min_ratio": float(readable["ratio"].min()) if len(readable) else np.nan,
            "max_ratio": float(readable["ratio"].max()) if len(readable) else np.nan}


def class_cost_table(readings_by_d: dict[float, pd.DataFrame], fix: dict,
                     chosen=("§16(e) drifting from 75", "Tobit exponential 10–100", "Tobit quadratic 40–100",
                             "100-cell location + 75→100 rate held")) -> pd.DataFrame:
    """What the two day-long classes cost under each reading: log10 nodes and
    hours per refutation on one core at 1.4 × 10⁶ nodes/s, pre-fix csearch
    (what the record was made with) and post-fix (× the 100-cell fix ratio),
    with the record's own hours beside them."""
    rec = recertify_counts()
    rows = []
    ratio = fix.get("median_ratio", np.nan)
    for d, rd in readings_by_d.items():
        cls = 2 if d == 3.0 else 4
        on_record = rec[rec["d"] == cls]
        for name in chosen:
            r = rd[(rd["reading"] == name) & (rd["cell_100"] != "dropped") & (rd["cell_100"].str.startswith(("censored", "not")))]
            if r.empty:
                continue
            r = r.iloc[0]
            rows.append({"class": CLASS_OF[d], "reading": name, "log10_nodes_125": r["mean_125"],
                         "band": f"[{r['lo_125']:.2f}, {r['hi_125']:.2f}]",
                         "hours_prefix_csearch": hours(r["mean_125"]),
                         "hours_postfix_csearch": hours(r["mean_125"]) * ratio if np.isfinite(ratio) else np.nan,
                         "postfix_reading": ("≥ " if fix.get("median_is_lower_bound") else "") + f"× {ratio:.2f}" if np.isfinite(ratio) else "",
                         "record_log10": ", ".join(f"{v:.2f}" for v in on_record["log_nodes"]),
                         "record_hours": ", ".join(f"{v:.0f}" for v in on_record["hours"])})
    return pd.DataFrame(rows)


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def tables(out: Path = TABLES, resamples: int = 300, verbose: bool = True, workers: int = 8) -> dict:
    """Every table of §35, written to `reports/rate_drift_tables.md`."""
    t0 = time.monotonic()
    parts = [f"# Rate drift refit with the 100 cell (§35)\n\n*Generated by `python -m learning.rate_drift --stage tables "
             f"--resamples {resamples}` on {time.strftime('%Y-%m-%d %H:%M')}.*\n"]
    result: dict = {}

    prefix = load_prefix()
    parts.append("## The pre-fix csearch run on the 100 cell (`ridge100_prefix_calls.csv`)\n")
    if len(prefix):
        pf = prefix.copy()
        pf["log_nodes"] = np.log10(1.0 + pf["nodes"].astype(float)).map(lambda v: f"{v:.3f}")
        pf["achieved"] = pf["achieved"].map(lambda v: "" if pd.isna(v) else f"{int(v)}")
        pf["nodes"] = pf["nodes"].map(lambda v: f"{int(v):,}")
        pf["seconds"] = pf["seconds"].map(lambda v: f"{v:,.0f}")
        parts.append(pf[["instance_name", "k", "status", "nodes", "log_nodes", "seconds", "deadline_seconds", "achieved"]]
                     .to_markdown(index=False, disable_numparse=True))
        result["prefix_status"] = pf["status"].value_counts().to_dict()
    else:
        parts.append("*(not run)*")

    fc = fix_cost_100()
    parts.append("\n## Fix cost on the 100 cell: post-fix csearch (§34) against pre-fix csearch (this run), at `value − 1`\n")
    parts.append(_md(fc, ".3g"))
    result["fix_cost"] = fc

    rec = recertify_counts()
    parts.append("\n## On record at 125 × 125 (`recertify/results.json`; pre-fix csearch)\n")
    parts.append(_md(rec))
    c100 = corpus100()
    parts.append("\n## On record at 100 (Chu & Stuckey `Random-100-100-2/4`, §14, 1,500 s; csearch rows pre-fix)\n")
    parts.append(_md(c100))
    result["recertify"] = rec

    for config in ("default", "csearch-prefix", "csearch"):
        for d in (3.0, 4.0):
            if config == "csearch" and d == 4.0:
                continue
            fr = series(config, d)
            if fr[fr["n"] == 100].empty:
                continue
            label = f"{config}, d = {d:g}"
            cells = fr.groupby("n").agg(instances=("log_nodes", "size"), censored=("censored", "sum"),
                                        median=("log_nodes", "median"), sd=("log_nodes", "std"),
                                        min=("log_nodes", "min"), max=("log_nodes", "max")).reset_index()
            parts.append(f"\n## Series `{label}`: cells (median of log10(1 + nodes); a cell with censored rows reads as a lower bound)\n")
            parts.append(_md(cells, ".3f"))
            sigma75 = float(fr[fr["n"] == 75]["log_nodes"].std())
            loc = cell_location(fr, 100, sigma75)
            med75 = float(fr[fr["n"] == 75]["log_nodes"].median())
            med60 = float(fr[fr["n"] == 60]["log_nodes"].median())
            loc.update(rate_60_75=(med75 - med60) / 15.0,
                       rate_75_100_from_censored_median=(loc["censored_median"] - med75) / 25.0,
                       rate_75_100_from_location=(loc["location"] - med75) / 25.0,
                       rate_75_100_lo=(loc["location_lo"] - med75) / 25.0,
                       rate_75_100_hi=(loc["location_hi"] - med75) / 25.0)
            sigma_fit = fit(fr, "exponential", 10, 75)["sigma_100"]     # the scale the 10–75 fit extrapolates to 100
            loc2 = cell_location(fr, 100, sigma_fit)
            loc2.update(rate_75_100_from_location=(loc2["location"] - med75) / 25.0,
                        rate_75_100_lo=(loc2["location_lo"] - med75) / 25.0,
                        rate_75_100_hi=(loc2["location_hi"] - med75) / 25.0)
            parts.append(f"\n### `{label}`: the 100 cell's location (censored-normal MLE; σ held at the 75 cell's "
                         f"{sigma75:.3f}, then at the 10–75 fit's extrapolated {sigma_fit:.3f})\n")
            parts.append(_md(pd.DataFrame([loc, loc2]), ".3f"))
            result[f"location_{label}"] = loc
            result[f"location_fitsigma_{label}"] = loc2
            if config == "csearch" and d == 3.0:
                # post-fix has no series below 100 (10–75 csearch counts are pre-fix): the cell alone
                continue
            rd = readings_table(fr, config, d, resamples=resamples, workers=workers)
            rd = compare_with_record(rd, rec, d)
            parts.append(f"\n### `{label}`: every reading of 125 (log10 nodes; band 90%; hours at 1.4 × 10⁶ nodes/s on one core)\n")
            parts.append(_md(rd, ".3g"))
            result[f"readings_{label}"] = rd
            if verbose:
                print(f"{label}: {len(rd)} readings in {time.monotonic() - t0:.0f} s", flush=True)

    fix = fix_ratio_summary(fc)
    parts.append("\n## Fix ratio on the 100 cell (post-fix / pre-fix csearch at `value − 1`)\n")
    parts.append(_md(pd.DataFrame([fix]), ".3g"))
    result["fix_ratio"] = fix
    by_d = {d: result[f"readings_csearch-prefix, d = {d:g}"] for d in (3.0, 4.0)
            if f"readings_csearch-prefix, d = {d:g}" in result}
    if by_d:
        cost = class_cost_table(by_d, fix)
        parts.append("\n## What the day-long classes cost under each reading (pre-fix csearch series; one core at 1.4 × 10⁶ nodes/s)\n")
        parts.append(_md(cost, ".3g"))
        result["class_cost"] = cost
    out.write_text("\n".join(parts) + "\n")
    if verbose:
        print(f"wrote {out} in {time.monotonic() - t0:.0f} s")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("prefix-run", "tables"), default="tables")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--deadline", type=float, default=2400.0)
    ap.add_argument("--wall", type=float, default=4500.0)
    ap.add_argument("--resamples", type=int, default=300)
    args = ap.parse_args()
    if args.stage == "prefix-run":
        prefix_run(workers=args.workers, deadline=args.deadline, wall=args.wall)
    else:
        tables(resamples=args.resamples, workers=args.workers)


if __name__ == "__main__":
    main()
