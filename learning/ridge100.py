"""One certified ridge cell at n = 100 (loop0004 item 07, `reports/ml_nature.md` §34).

Question. §16 stopped the generated campaign at 75 customers because the
`m = n` ridge cell at 100 (`f_n100_m100_d3`, three customers per product) was
priced at 21.5 core-hours by the §11 law, and its 5-instance sample confirmed
the price: nine of ten descents ran out at 900 s and every refutation censored
at 1,500 s. Every 125 × 125 figure since is a 50-customer extrapolation from
75. This module certifies as much of that cell as a bounded run allows, records
the rest as censored lower bounds with their counts, and prices the run first
with §19's cost model so the price can be checked against what was paid.

Design.
* The cell is the campaign's own: `learning.ensemble.generate` with the CRC
  seeds, indices 0–24, so `i000`–`i004` are byte for byte §16's sample
  (digests checked against `manifest_upward.csv`).
* Each instance is *descended* with the complete customer search under the
  `csearch` configuration (Theorem 2 on: at three products per customer it is,
  and §16(d) measured it 1.8× faster in seconds than `default` on the
  satisfiable side here): heuristic upper bound (best of four registered
  strategies, witness re-simulated), then `decide(value − 1)` repeatedly. A
  `sat` answer is re-simulated and its witness saved (monotone, through
  `_save_solution`, under `learning/data/ensemble/solutions/`, never
  `solutions/`); an `unsat` certifies the value **and is the `csearch`
  refutation count**; `unknown` leaves the value a verified upper bound.
* Once an instance is certified, the `default` refutation at `optimum − 1` —
  the configuration §11/§16's laws are stated in — is queued behind every
  pending descent step. Cheapest predicted instance first throughout.
* Every call has a deadline and the run has a wall; a call that expires is a
  censored lower bound on its count, recorded with its status. The run is
  resumable: every finished call is appended to `ridge100_calls.csv` and the
  scheduler rebuilds each instance's state from that file.
* Nothing here touches `solutions/` or any solver default.

Run:
    python -m learning.ridge100 --stage price                 # instances, features, UBs, cost-model price (~2 min)
    python -m learning.ridge100 --stage run --workers 16 --wall 6000 --deadline 1800
    python -m learning.ridge100 --stage tables                # reports/ridge100_tables.md
    python -m pytest tests/test_ridge100.py -q
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.ensemble import (MANIFEST_COLUMNS, MANIFEST_UPWARD_CSV, SOLUTIONS_DIR, Cell, cell_seed,
                               generate, instance_name)
from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
CELL = Cell("fixed", 100, 100, 3.0)
PER_CELL = 25
MANIFEST_CSV = ENSEMBLE_DIR / "manifest_ridge100.csv"
PRICE_CSV = ENSEMBLE_DIR / "ridge100_price.csv"
CALLS_CSV = ENSEMBLE_DIR / "ridge100_calls.csv"
TABLES = Path("reports/ridge100_tables.md")
UPWARD_FINISH_CSV = ENSEMBLE_DIR / "results_upward_finish.csv"

UB_STRATEGIES = ("cs-dfs", "rule+cs-dfs", "mcnh", "mcn+tabu")
DESCENT_CONFIG = "csearch"        # the descent's configuration; its final `unsat` is the csearch refutation
REFUTE_CONFIG = "default"         # the extra call: the law's configuration
NODES_PER_SECOND = 1.8e6          # measured 2.29e6 on one core at load 4; 16 workers beside 8 run slower
CALL_COLUMNS = ["instance_name", "purpose", "config", "k", "status", "nodes", "seconds",
                "deadline_seconds", "achieved", "started", "finished"]


# ----------------------------------------------------------------------------
# the cell
# ----------------------------------------------------------------------------

def cell_instances(cell: Cell = CELL, per_cell: int = PER_CELL) -> list[MOSPInstance]:
    return [generate(cell, i) for i in range(per_cell)]


def manifest(cell: Cell = CELL, per_cell: int = PER_CELL) -> pd.DataFrame:
    from learning.canonical import matrix_digest
    rows = []
    for i in range(per_cell):
        inst = generate(cell, i)
        rows.append({"instance_name": inst.name, "cell": cell.id, "generator": cell.generator,
                     "n": cell.n, "m": cell.m, "param": cell.param, "index": i,
                     "seed": cell_seed(cell, i), "matrix_digest": matrix_digest(inst)})
    return pd.DataFrame(rows, columns=MANIFEST_COLUMNS)


def check_against_upward(frame: pd.DataFrame, upward_manifest: Path = MANIFEST_UPWARD_CSV) -> int:
    """How many of the cell's instances §16 already generated, and that every
    shared digest agrees (raises otherwise)."""
    if not upward_manifest.exists():
        return 0
    up = pd.read_csv(upward_manifest)
    up = up[up["cell"] == CELL.id].set_index("instance_name")
    shared = [n for n in frame["instance_name"] if n in up.index]
    for name in shared:
        mine = frame.loc[frame["instance_name"] == name, "matrix_digest"].iloc[0]
        if mine != up.loc[name, "matrix_digest"]:
            raise RuntimeError(f"{name}: digest {mine} differs from manifest_upward {up.loc[name, 'matrix_digest']}")
    return len(shared)


# ----------------------------------------------------------------------------
# pricing
# ----------------------------------------------------------------------------

def heuristic_upper_bounds(instance: MOSPInstance, strategies=UB_STRATEGIES) -> dict:
    """Every registered strategy's value, re-simulated, and the best witness."""
    from mosp.verify import max_open_stacks
    from satisfiability.heuristics import upper_bound
    out: dict = {}
    best = None
    for name in strategies:
        t0 = time.monotonic()
        val, ordering = upper_bound(instance, name)
        achieved = int(max_open_stacks(instance, list(ordering)))
        out[f"ub_{name}"] = achieved
        out[f"ub_seconds_{name}"] = round(time.monotonic() - t0, 3)
        if best is None or achieved < best[0]:
            best = (achieved, list(ordering), name)
    out["ub_best"], out["ub_best_strategy"] = best[0], best[2]
    return out, best[1]


def _price_job(index: int) -> dict:
    from learning.canonical import canonical_record
    from learning.features import instance_features
    inst = generate(CELL, index)
    row = {"instance_name": inst.name, "cell": CELL.id, "generator": CELL.generator, "n": CELL.n,
           "m": CELL.m, "param": CELL.param, "index": index, "seed": cell_seed(CELL, index)}
    t0 = time.monotonic()
    row.update(instance_features(inst))          # brings its own `ub_best` = min(ub_mcn, ub_cs_dfs) ...
    row["feature_seconds"] = round(time.monotonic() - t0, 3)
    ubs, _ = heuristic_upper_bounds(inst)
    row.update(ubs)                              # ... which the four-strategy minimum replaces
    canon = canonical_record(inst)
    for key in ("matrix_digest", "graph_cert", "wl_hash", "aut_order"):
        row[key] = canon[key]
    return row


def fit_cost_models(configs=("default", "csearch")) -> dict:
    """§19's linear Tobit with drift, fitted on every count at 10–75 (csearch on pre-fix sources)."""
    from learning.cost_model import CostModel, assemble, training_mask
    frame = assemble()
    models = {}
    for cfg in configs:
        models[cfg] = CostModel(drift=True, gbm=False).fit(frame[training_mask(frame, cfg)], cfg)
    return models


def predict_cost(price: pd.DataFrame, models: dict, optimum_col: str = "ub_best") -> pd.DataFrame:
    """log10 nodes per configuration for each instance, the optimum taken from `optimum_col`
    (the heuristic upper bound before the run; the certified value after it)."""
    from learning.cost_model import prepare
    f = price.copy()
    f["optimum"] = f[optimum_col]
    f = prepare(f)
    out = price[["instance_name"]].copy()
    for cfg, model in models.items():
        out[f"pred_log_nodes_{cfg}"] = model.predict(f)
    return out


LAW_75 = {  # §16(e), `reports/upward_tables.md`: the 75 median of the d = 3 cell, its 60 → 75 rate, the pooled drift slope
    "default": (6.78, 0.0951, -0.000217),
    "csearch": (6.662, 0.0924, -0.000174),
}


def law_prediction(n: int = 100, config: str = "default") -> dict:
    """§16(e)'s two figures for this cell at `n`: the 60 → 75 rate held constant and
    drifting at the pooled slope, from the 75-customer median; §11's 15–40 law beside them."""
    median75, rate, slope = LAW_75[config]
    dn = n - 75
    return {"constant": median75 + rate * dn,
            "drifting": median75 + rate * dn + 0.5 * slope * dn * dn,
            "sec11_law": -0.191 + 0.0951 * n}


def price(workers: int = 16, out: Path = PRICE_CSV, verbose: bool = True) -> pd.DataFrame:
    man = manifest()
    shared = check_against_upward(man)
    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    man.to_csv(MANIFEST_CSV, index=False)
    if verbose:
        print(f"{len(man)} instances in {CELL.id}; {shared} shared with manifest_upward, digests agree", flush=True)
    with multiprocessing.get_context("spawn").Pool(min(workers, PER_CELL)) as pool:
        rows = pool.map(_price_job, range(PER_CELL))
    frame = pd.DataFrame(rows)
    models = fit_cost_models()
    pred = predict_cost(frame, models)
    frame = frame.merge(pred, on="instance_name")
    for cfg in models:
        frame[f"pred_seconds_{cfg}"] = 10 ** frame[f"pred_log_nodes_{cfg}"] / NODES_PER_SECOND
    frame.to_csv(out, index=False)
    if verbose:
        print(price_summary(frame), flush=True)
    return frame


def price_summary(frame: pd.DataFrame) -> str:
    law = law_prediction()
    lines = [f"cost model (Tobit + drift, fit 10-75), optimum := ub_best ({frame['ub_best'].min()}-{frame['ub_best'].max()}):"]
    for cfg in ("default", "csearch"):
        col = f"pred_log_nodes_{cfg}"
        if col in frame:
            hours = frame[f"pred_seconds_{cfg}"].sum() / 3600
            lines.append(f"  {cfg}: median log10 nodes {frame[col].median():.2f} "
                         f"[{frame[col].min():.2f}, {frame[col].max():.2f}]; "
                         f"{PER_CELL} refutations = {hours:.1f} core-hours at {NODES_PER_SECOND:.2g} nodes/s")
    lines.append(f"  §16(e) law at 100 (default): constant {law['constant']:.2f}, drifting {law['drifting']:.2f}, "
                 f"§11 law {law['sec11_law']:.2f}")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# the run: one decision call per job, a priority scheduler in the parent
# ----------------------------------------------------------------------------

def _decide_job(args) -> dict:
    """One `decide` call in a worker. Returns the row for `ridge100_calls.csv`."""
    from learning.node_counts import refutation_kwargs
    from mosp.verify import max_open_stacks
    from satisfiability.customer_search import decide
    from satisfiability.heuristics import product_order_from_customers

    name, index, purpose, config, k, deadline_seconds = args
    inst = generate(CELL, index)
    assert inst.name == name
    started = time.time()
    t0 = time.monotonic()
    answer = decide(inst, k, deadline=t0 + deadline_seconds, **refutation_kwargs(inst, config))
    seconds = time.monotonic() - t0
    row = {"instance_name": name, "purpose": purpose, "config": config, "k": k,
           "status": answer.status, "nodes": answer.nodes, "seconds": round(seconds, 3),
           "deadline_seconds": deadline_seconds, "achieved": None,
           "started": round(started, 1), "finished": round(time.time(), 1)}
    if answer.status == "sat":
        ordering = product_order_from_customers(inst, answer.order)
        row["achieved"] = int(max_open_stacks(inst, ordering))
        row["ordering"] = ordering
    return row


def _ub_job(index: int) -> dict:
    inst = generate(CELL, index)
    ubs, ordering = heuristic_upper_bounds(inst)
    return {"instance_name": inst.name, "index": index, "value": ubs["ub_best"],
            "strategy": ubs["ub_best_strategy"], "ordering": ordering}


def save_witness(inst: MOSPInstance, value: int, ordering: list[int], certified: bool,
                 solutions_dir: Path = SOLUTIONS_DIR) -> None:
    from satisfiability.mosp_solver import PROVENANCE_REFUTATION, PROVENANCE_SOLUTION, _save_solution
    _save_solution(inst, int(value), list(ordering), solutions_dir,
                   provenance=PROVENANCE_REFUTATION if certified else PROVENANCE_SOLUTION)


def load_calls(path: Path = CALLS_CSV) -> pd.DataFrame:
    if path.exists() and path.stat().st_size:
        return pd.read_csv(path)
    return pd.DataFrame(columns=CALL_COLUMNS)


def instance_states(calls: pd.DataFrame, ubs: dict[str, int]) -> dict[str, dict]:
    """Rebuild each instance's state from the recorded calls.

    value: the best verified value (UB, lowered by every `sat`); certified: an
    `unsat` at value − 1 under the descent configuration; descent_censored: an
    `unknown` at value − 1 under it; default_done: a `default` call at value − 1
    recorded (any status).
    """
    states = {}
    for name, ub in ubs.items():
        mine = calls[calls["instance_name"] == name]
        value = int(ub)
        sats = mine[mine["status"] == "sat"]
        if len(sats):
            value = min(value, int(sats["achieved"].min()))
        at = mine[mine["k"] == value - 1]
        desc = at[at["config"] == DESCENT_CONFIG]
        ref = at[at["config"] == REFUTE_CONFIG]
        states[name] = {
            "value": value,
            "certified": bool((desc["status"] == "unsat").any() or (ref["status"] == "unsat").any()),
            "descent_censored": bool((desc["status"] == "unknown").any()),
            "default_done": len(ref) > 0,
            "disagreement": any(((mine["k"] == kk) & (mine["status"] == "unsat")).any()
                                and ((mine["k"] == kk) & (mine["status"] == "sat")).any()
                                for kk in mine["k"].unique()),
        }
    return states


def next_jobs(states: dict[str, dict], order: list[str], running: set[tuple]) -> list[tuple]:
    """Pending jobs in priority order: every descent step first (cheapest instance
    first), then the `default` refutations of certified instances."""
    descents, refutes = [], []
    for name in order:
        s = states[name]
        if s["value"] <= 1:
            continue
        k = s["value"] - 1
        if not s["certified"] and not s["descent_censored"]:
            job = (name, "descent", DESCENT_CONFIG, k)
            if job not in running:
                descents.append(job)
        elif s["certified"] and not s["default_done"]:
            job = (name, "refute", REFUTE_CONFIG, k)
            if job not in running:
                refutes.append(job)
    return descents + refutes


def _append(row: dict, path: Path) -> None:
    keep = {c: row.get(c) for c in CALL_COLUMNS}
    pd.DataFrame([keep]).to_csv(path, mode="a", header=not path.exists() or path.stat().st_size == 0, index=False)


def run(workers: int = 16, wall: float = 6000.0, deadline: float = 1800.0, min_call: float = 120.0,
        calls_csv: Path = CALLS_CSV, price_csv: Path = PRICE_CSV, verbose: bool = True) -> pd.DataFrame:
    """The scheduler. `wall` seconds after the start no job is dispatched and every
    running call's deadline is inside the wall; `deadline` caps each call;
    `min_call` is the least a dispatched call may be given."""
    t_start = time.time()
    price_frame = pd.read_csv(price_csv) if price_csv.exists() else None
    indices = {instance_name(CELL, i): i for i in range(PER_CELL)}
    if price_frame is not None and "pred_log_nodes_default" in price_frame:
        order = list(price_frame.sort_values("pred_log_nodes_default")["instance_name"])
    else:
        order = list(indices)
    instances = {name: generate(CELL, indices[name]) for name in order}

    ctx = multiprocessing.get_context("fork")
    with ctx.Pool(workers) as pool:
        # heuristic upper bounds, witnesses saved (a `solution`, never demoting anything)
        ubs: dict[str, int] = {}
        for res in pool.imap_unordered(_ub_job, [indices[n] for n in order]):
            ubs[res["instance_name"]] = int(res["value"])
            save_witness(instances[res["instance_name"]], res["value"], res["ordering"], certified=False)
        if verbose:
            print(f"UB by heuristics: {sorted(ubs.values())}", flush=True)

        calls = load_calls(calls_csv)
        states = instance_states(calls, ubs)
        running: dict = {}          # AsyncResult -> job tuple
        while True:
            remaining = wall - (time.time() - t_start)
            pending = next_jobs(states, order, set(running.values()))
            while pending and len(running) < workers and remaining > min_call:
                name, purpose, config, k = pending.pop(0)
                dl = float(min(deadline, remaining - 5.0))
                job = (name, purpose, config, k)
                running[pool.apply_async(_decide_job, ((name, indices[name], purpose, config, k, dl),))] = job
                if verbose:
                    print(f"[{time.time() - t_start:7.0f}s] -> {name} {purpose} {config} k={k} ({dl:.0f} s)", flush=True)
            if not running:
                break
            done = [r for r in running if r.ready()]
            if not done:
                time.sleep(1.0)
                continue
            for r in done:
                job = running.pop(r)
                row = r.get()
                _append(row, calls_csv)
                name = row["instance_name"]
                if row["status"] == "sat":
                    save_witness(instances[name], row["achieved"], row["ordering"], certified=False)
                elif row["status"] == "unsat" and row["purpose"] == "descent":
                    # the value stands certified: re-save the witness with its provenance
                    sol = json.loads((SOLUTIONS_DIR / f"{name}.json").read_text())
                    if int(sol["mosp_value"]) == states[name]["value"]:
                        save_witness(instances[name], sol["mosp_value"], sol["ordering"], certified=True)
                calls = pd.concat([calls, pd.DataFrame([{c: row.get(c) for c in CALL_COLUMNS}])], ignore_index=True)
                states = instance_states(calls, ubs)
                if verbose:
                    print(f"[{time.time() - t_start:7.0f}s] <- {name} {row['purpose']} {row['config']} k={row['k']}: "
                          f"{row['status']} {row['nodes']:,} nodes {row['seconds']:.0f} s"
                          + ("" if row["achieved"] is None else f" achieved {row['achieved']}"), flush=True)
    return load_calls(calls_csv)


def refute_censored(workers: int = 7, deadline: float = 1800.0, calls_csv: Path = CALLS_CSV,
                    price_csv: Path = PRICE_CSV, config: str = REFUTE_CONFIG, verbose: bool = True,
                    exclude: tuple[str, ...] = ()) -> pd.DataFrame:
    """For every instance whose descent censored (value a verified upper bound, no
    refutation), one `config` call at `value − 1` under `deadline`: a censored
    lower bound in the law's configuration, as §16(d) recorded for its sample.
    Appends to `ridge100_calls.csv`; safe beside a running `run` (append-only,
    disjoint jobs). A `sat` answer is a better witness and is saved."""
    price = pd.read_csv(price_csv)
    indices = dict(zip(price["instance_name"], price["index"].astype(int)))
    ubs = dict(zip(price["instance_name"], price["ub_best"].astype(int)))
    states = instance_states(load_calls(calls_csv), ubs)
    order = list(price.sort_values("pred_log_nodes_default")["instance_name"])
    todo = [n for n in order if states[n]["descent_censored"] and not states[n]["certified"] and n not in exclude
            and not any((r["config"] == config) for _, r in load_calls(calls_csv).iterrows()
                        if r["instance_name"] == n and r["k"] == states[n]["value"] - 1)]
    jobs = [(n, indices[n], "refute", config, states[n]["value"] - 1, float(deadline)) for n in todo]
    if verbose:
        print(f"{len(jobs)} censored instances -> {config} at value - 1, {deadline:g} s each on {workers} workers", flush=True)
    if not jobs:
        return load_calls(calls_csv)
    t0 = time.time()
    with multiprocessing.get_context("fork").Pool(min(workers, len(jobs))) as pool:
        for row in pool.imap_unordered(_decide_job, jobs):
            _append(row, calls_csv)
            if row["status"] == "sat":
                save_witness(generate(CELL, indices[row["instance_name"]]), row["achieved"], row["ordering"], certified=False)
            if verbose:
                print(f"[{time.time() - t0:7.0f}s] {row['instance_name']} {config} k={row['k']}: {row['status']} "
                      f"{row['nodes']:,} nodes {row['seconds']:.0f} s", flush=True)
    return load_calls(calls_csv)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------

def per_instance(calls: pd.DataFrame, price: pd.DataFrame) -> pd.DataFrame:
    """One row per instance: value, how it was established, both refutation counts
    (censored ones marked `≥`), descent calls and seconds, predictions."""
    ubs = dict(zip(price["instance_name"], price["ub_best"]))
    states = instance_states(calls, ubs)
    rows = []
    for name in price.sort_values("index")["instance_name"]:
        s = states[name]
        mine = calls[calls["instance_name"] == name]
        k = s["value"] - 1
        row = {"instance": name.rsplit("_", 1)[1], "ub_best": ubs[name], "value": s["value"],
               "status": ("certified" if s["certified"] else
                          "upper bound (descent censored)" if s["descent_censored"] else
                          "upper bound (not reached)"),
               "descent_calls": int((mine["purpose"] == "descent").sum()),
               "descent_seconds": round(mine.loc[mine["purpose"] == "descent", "seconds"].sum()),
               "descent_nodes": int(mine.loc[mine["purpose"] == "descent", "nodes"].sum()),
               }
        for cfg in (DESCENT_CONFIG, REFUTE_CONFIG):
            at = mine[(mine["k"] == k) & (mine["config"] == cfg)]
            if len(at):
                settled = at[at["status"] != "unknown"]
                r = settled.iloc[-1] if len(settled) else at.loc[at["nodes"].astype(float).idxmax()]
                row[f"log_nodes_{cfg}"] = round(float(np.log10(1 + r["nodes"])), 2)
                row[f"censored_{cfg}"] = r["status"] == "unknown"
                row[f"seconds_{cfg}"] = round(float(r["seconds"]))
            else:
                row[f"log_nodes_{cfg}"] = np.nan
                row[f"censored_{cfg}"] = np.nan
                row[f"seconds_{cfg}"] = np.nan
        p = price[price["instance_name"] == name].iloc[0]
        row["pred_default_ub"] = round(float(p["pred_log_nodes_default"]), 2)
        rows.append(row)
    return pd.DataFrame(rows)


def cell_summary(table: pd.DataFrame, config: str = REFUTE_CONFIG) -> dict:
    """Censored median of log10 nodes (§16's `censored_median`) and the counts."""
    from learning.upward import censored_median
    col, cens = f"log_nodes_{config}", f"censored_{config}"
    have = table[np.isfinite(table[col].astype(float))]
    if not len(have):
        return {"config": config, "n_counts": 0}
    med, lower = censored_median(have[col].to_numpy(float), have[cens].astype(bool).to_numpy())
    settled = have[~have[cens].astype(bool)]
    return {"config": config, "n_counts": len(have), "settled": len(settled), "censored": int(have[cens].astype(bool).sum()),
            "median_log_nodes": round(med, 2), "median_is_lower_bound": lower,
            "min_settled": round(float(settled[col].min()), 2) if len(settled) else np.nan,
            "max_settled": round(float(settled[col].max()), 2) if len(settled) else np.nan,
            "max_censored": round(float(have.loc[have[cens].astype(bool), col].max()), 2) if have[cens].astype(bool).any() else np.nan}


def audit(calls: pd.DataFrame, price: pd.DataFrame, solutions_dir: Path = SOLUTIONS_DIR) -> dict:
    """Every saved witness re-simulates to its value; no k has both `sat` and
    `unsat`; certified values are never below `lb_best`; distinct graphs."""
    from mosp.verify import max_open_stacks
    ubs = dict(zip(price["instance_name"], price["ub_best"]))
    states = instance_states(calls, ubs)
    out = {"instances": len(price), "certified": sum(s["certified"] for s in states.values()),
           "descent_censored": sum(s["descent_censored"] for s in states.values()),
           "not_reached": sum((not s["certified"]) and (not s["descent_censored"]) for s in states.values()),
           "disagreements": sum(s["disagreement"] for s in states.values()),
           "default_counts": int(((calls["config"] == REFUTE_CONFIG)).sum()),
           "default_unsat": int(((calls["config"] == REFUTE_CONFIG) & (calls["status"] == "unsat")).sum()),
           "default_censored": int(((calls["config"] == REFUTE_CONFIG) & (calls["status"] == "unknown")).sum()),
           "default_sat": int(((calls["config"] == REFUTE_CONFIG) & (calls["status"] == "sat")).sum()),
           "witness_ok": 0, "witness_bad": 0, "below_lb": 0, "certified_provenance": 0,
           "distinct_graphs": int(price["graph_cert"].nunique()) if "graph_cert" in price else None,
           "decomposable": int((price["g_components"] > 1).sum()) if "g_components" in price else None}
    for name, s in states.items():
        path = solutions_dir / f"{name}.json"
        if not path.exists():
            continue
        sol = json.loads(path.read_text())
        inst = generate(CELL, int(price.loc[price["instance_name"] == name, "index"].iloc[0]))
        ok = int(max_open_stacks(inst, list(sol["ordering"]))) == int(sol["mosp_value"]) == s["value"]
        out["witness_ok" if ok else "witness_bad"] += 1
        if s["certified"] and sol.get("provenance", "").startswith("certified"):
            out["certified_provenance"] += 1
        lb = price.loc[price["instance_name"] == name, "lb_best"]
        if len(lb) and s["value"] < int(lb.iloc[0]):
            out["below_lb"] += 1
    return out


def prior_sample(finish_csv: Path = UPWARD_FINISH_CSV) -> pd.DataFrame:
    """§16(d)'s answers on `i000`–`i004` at 1,500 s, for the comparison."""
    if not finish_csv.exists():
        return pd.DataFrame()
    f = pd.read_csv(finish_csv)
    f = f[f["instance_name"].str.startswith(f"ens_{CELL.id}")].copy()
    f["log_nodes"] = np.log10(1 + f["nodes"].astype(float)).round(2)
    return f[["instance_name", "config", "value", "status", "log_nodes", "seconds"]]


def price_vs_paid(calls: pd.DataFrame, price: pd.DataFrame, table: pd.DataFrame, wall: float | None = None,
                  workers: int = 16) -> pd.DataFrame:
    """Core-hours predicted (cost model on the UB, then on the certified value where
    there is one) against core-hours actually spent, per purpose."""
    rows = []
    spent = calls.groupby(["purpose", "config"])["seconds"].sum() / 3600
    for (purpose, cfg), h in spent.items():
        rows.append({"item": f"paid: {purpose} ({cfg})", "core_hours": round(float(h), 2),
                     "calls": int(((calls["purpose"] == purpose) & (calls["config"] == cfg)).sum())})
    rows.append({"item": "paid: total", "core_hours": round(float(calls["seconds"].sum() / 3600), 2), "calls": len(calls)})
    for cfg in ("default", "csearch"):
        col = f"pred_seconds_{cfg}"
        if col in price:
            rows.append({"item": f"priced: 25 refutations ({cfg}), optimum := ub_best", "core_hours": round(float(price[col].sum() / 3600), 2),
                         "calls": PER_CELL})
    if wall is not None:
        rows.append({"item": f"available: {workers} workers × wall", "core_hours": round(workers * wall / 3600, 2), "calls": None})
    return pd.DataFrame(rows)


def repriced(price: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    """The cost model's prediction with the certified value in place of the UB,
    beside the observed default count, for the certified instances."""
    models = fit_cost_models()
    cert = table[table["status"] == "certified"]
    if not len(cert):
        return pd.DataFrame()
    f = price.copy()
    f["value"] = f["instance_name"].map(dict(zip("ens_" + CELL.id + "_" + cert["instance"], cert["value"])))
    f = f[np.isfinite(f["value"].astype(float))]
    pred = predict_cost(f, models, optimum_col="value")
    out = pred.copy()
    out["instance"] = out["instance_name"].str.rsplit("_", n=1).str[1]
    out = out.merge(cert[["instance", "value", "log_nodes_default", "censored_default", "log_nodes_csearch", "censored_csearch"]], on="instance")
    out["pred_ub_default"] = out["instance"].map(dict(zip(table["instance"], table["pred_default_ub"])))
    return out.drop(columns=["instance_name"])


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def tables(out: Path = TABLES, calls_csv: Path = CALLS_CSV, price_csv: Path = PRICE_CSV,
           wall: float | None = None, workers: int = 16) -> dict:
    calls, price = load_calls(calls_csv), pd.read_csv(price_csv)
    table = per_instance(calls, price)
    summary = pd.DataFrame([cell_summary(table, cfg) for cfg in (REFUTE_CONFIG, DESCENT_CONFIG)])
    aud = audit(calls, price)
    paid = price_vs_paid(calls, price, table, wall, workers)
    rep = repriced(price, table)
    prior = prior_sample()
    law = law_prediction()
    law_cs = law_prediction(config="csearch")
    md = [f"# One certified ridge cell at 100 (§34)\n\n*Generated {time.strftime('%Y-%m-%d %H:%M')} by "
          f"`python -m learning.ridge100 --stage tables`. Cell `{CELL.id}`, {PER_CELL} instances; log = log10(1 + nodes); "
          f"a censored count is a lower bound.*\n",
          "## Per instance\n\n" + _md(table) + "\n",
          "## Cell summary (censored median as in §16)\n\n" + _md(summary) + "\n",
          f"## §16(e) law at 100 — default: constant {law['constant']:.2f}, drifting {law['drifting']:.2f}; "
          f"csearch: constant {law_cs['constant']:.2f}, drifting {law_cs['drifting']:.2f}; §11 law {law['sec11_law']:.2f}\n",
          "## Audit\n\n" + _md(pd.DataFrame([aud])) + "\n",
          "## Price against paid\n\n" + _md(paid) + "\n",
          "## Cost model re-priced on the certified value\n\n" + (_md(rep) if len(rep) else "*no certified instance*") + "\n",
          "## §16(d)'s prior answers on i000–i004 (1,500 s)\n\n" + (_md(prior) if len(prior) else "*none*") + "\n",
          "## Heuristic upper bounds\n\n" + _md(price[["instance_name", "ub_cs-dfs", "ub_rule+cs-dfs", "ub_mcnh", "ub_mcn+tabu", "ub_best",
                                                        "ub_best_strategy", "lb_best", "col_mean", "g_components", "pred_log_nodes_default",
                                                        "pred_log_nodes_csearch"]]) + "\n"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md))
    return {"table": table, "summary": summary, "audit": aud, "paid": paid, "repriced": rep, "prior": prior}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("price", "run", "refute-censored", "tables"), required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--wall", type=float, default=6000.0, help="seconds after which nothing is dispatched")
    ap.add_argument("--deadline", type=float, default=1800.0, help="seconds per decision call")
    ap.add_argument("--out", type=Path, default=TABLES)
    ap.add_argument("--exclude", default="", help="refute-censored: instance names already in flight elsewhere")
    args = ap.parse_args()
    if args.stage == "price":
        price(args.workers)
    elif args.stage == "run":
        run(args.workers, args.wall, args.deadline)
    elif args.stage == "refute-censored":
        refute_censored(args.workers, args.deadline, exclude=tuple(x for x in args.exclude.split(",") if x))
    else:
        res = tables(args.out, wall=args.wall, workers=args.workers)
        print(_md(res["summary"]))
        print(res["audit"])
        print(_md(res["paid"]))
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
