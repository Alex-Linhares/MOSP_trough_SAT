"""The differential harness above 40 customers, under a budget (plan 3 §1 Q1c,
loop0004 item 06).

Question. Every refutation at n ≤ 40 is sound on twenty independent searches
(§15) and carries a checkable certificate (§32); above 40 the only checks on
record were two configurations agreeing on the identity labelling (§3, §14)
and the loop0003 relabelling portfolio (§18, sixteen labellings under one
configuration, asked about speed and not about soundness). This module runs
`learning.differential`'s check -- the identity and four random relabellings,
both search configurations (`default`, `csearch`), `decide(optimum − 1)`
expected `unsat` and `decide(optimum)` expected `sat` with the witness
simulated -- on the certified campaign at 50–75 (eight instances per cell,
the first eight by index) and the whole certified corpus at 50–100, at 300 s
per call, inside a budget of eight core-hours, **priced before it runs**.

Three verdicts, kept apart exactly as in `learning.differential`: a
*disagreement* (two settled statuses differ at the same `k`), a
*contradiction* (a settled status or a witness against the certificate), and
a *censored* call (`unknown` at the deadline), which is a lower bound on the
node count and never a disagreement.

Pricing. Every call's cost is predicted from a recorded identity run of the
same instance under the same configuration -- `results_upward.csv` and
`scale_nodes.csv` for `default`, `fix_cost_scale.csv` (today's rule) for
`csearch`, the loop0003 portfolio for the witness side -- inflated by 1.3 for
the relabelling spread and capped at the deadline; a recorded call that was
itself censored is priced at the full deadline. Witness calls are always
scheduled (they are cheap, and the satisfiable side is where an over-strong
rule shows, §15); refutation calls are scheduled cheapest instance first
until the budget is spent, and what is priced out is reported by size and
class. That cut is the deliverable "the first size at which the harness
stops being affordable".

The `variants` stage adds item 04's flag variants (`old-order`, `prefix`,
`bm-first`; `satisfiability.customer_search.decide` kwargs, all default off)
on the refutation side over the same five labellings, where Theorem 2 is on
and the identity refutation under today's rule settled within 2 s in §31's
scale table: the relabelling spread per variant, and the false answers of
the two unsound reverts above 40.

Run:
    python -m learning.differential_scale --stage price                 # tables only, nothing runs
    python -m learning.differential_scale --stage run --workers 16 --wall 3300
    python -m learning.differential_scale --stage variants --workers 16
    python -m learning.differential_scale --stage tables

Writes `learning/data/ensemble/differential_scale.csv` (one row per instance,
labelling and configuration; resumable), `differential_scale_price.csv`,
`differential_scale_variants.csv` and `reports/differential_scale_tables.md`.
Nothing here decides `k` for anything, changes a default, or writes to
`solutions/`.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.differential import (
    DEFAULT_INSTANCE_DIR,
    DEFAULT_SOLUTIONS_DIR,
    ENSEMBLE_DIR,
    RECOVER_METHODS,
    _call,
    _materialise,
    corpus_targets,
    labellings,
    verdict,
    witness_value,
)
from learning.node_counts import CONFIGS
from mosp.instance import MOSPInstance

UPWARD_CSV = ENSEMBLE_DIR / "results_upward.csv"
SCALE_NODES_CSV = ENSEMBLE_DIR / "scale_nodes.csv"
FIX_COST_SCALE_CSV = ENSEMBLE_DIR / "fix_cost_scale.csv"
PORTFOLIO_CSV = ENSEMBLE_DIR / "portfolio.csv.gz"

ROWS_CSV = ENSEMBLE_DIR / "differential_scale.csv"
PRICE_CSV = ENSEMBLE_DIR / "differential_scale_price.csv"
VARIANTS_CSV = ENSEMBLE_DIR / "differential_scale_variants.csv"
TABLES = Path("reports/differential_scale_tables.md")

RELABELLINGS = 4
DEADLINE = 300.0
BUDGET_CORE_HOURS = 8.0
PER_CELL = 8
MIN_N, CAMPAIGN_MAX_N, CORPUS_MAX_N = 50, 75, 100
SPREAD_INFLATION = 1.3          # §18: relabelling spread of a refutation is 1.00–1.05× in nodes; generous
WITNESS_FLOOR = 0.05            # seconds, where no witness run is on record
VARIANT_NAMES = ("old-order", "prefix", "bm-first")
VARIANT_CHEAP_SECONDS = 2.0
VARIANT_DEADLINE = 60.0
SIZE_BANDS = ((50, 50), (51, 60), (61, 75), (76, 99), (100, 100))


def band(n: int) -> str:
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return str(lo) if lo == hi else f"{lo}-{hi}"
    return f">{SIZE_BANDS[-1][1]}"


def instance_class(name: str, source: str, cell: str) -> str:
    """Campaign cell, Chu & Stuckey class (`Random-100-100-2`), or `other`."""
    if source == "campaign":
        return cell
    if name.startswith("Random-"):
        return name.rsplit("-", 1)[0]
    if name.startswith(("GP", "SP")):
        return "Challenge"
    return "SCOOP/other"


# ----------------------------------------------------------------------------
# targets
# ----------------------------------------------------------------------------


def sample_per_cell(frame: pd.DataFrame, per_cell: int = PER_CELL) -> pd.DataFrame:
    """The first `per_cell` certified instances of every cell by index."""
    frame = frame[frame.certified.astype(bool)]
    return frame.sort_values(["cell", "index"]).groupby("cell", sort=False).head(per_cell)


def campaign_targets_scale(upward_csv: Path = UPWARD_CSV, per_cell: int = PER_CELL,
                           min_n: int = MIN_N, max_n: int = CAMPAIGN_MAX_N) -> list[dict]:
    frame = pd.read_csv(upward_csv, low_memory=False)
    frame = frame[(frame.n >= min_n) & (frame.n <= max_n)]
    frame = sample_per_cell(frame, per_cell)
    cols = ["instance_name", "cell", "generator", "n", "m", "param", "index", "optimum",
            "matrix_digest", "seconds_default", "status_default"]
    return [{"source": "campaign", **{c: row[c] for c in cols}}
            for row in frame[cols].to_dict("records")]


def corpus_targets_scale(min_n: int = MIN_N, max_n: int = CORPUS_MAX_N,
                         instance_dir: Path = DEFAULT_INSTANCE_DIR,
                         solutions_dir: Path = DEFAULT_SOLUTIONS_DIR) -> list[dict]:
    jobs = []
    for job in corpus_targets(instance_dir, solutions_dir, max_n):
        n = len(job["matrix"])
        if n >= min_n:
            jobs.append(dict(job, n=n, m=len(job["matrix"][0])))
    return jobs


def targets(source: str = "all") -> list[dict]:
    jobs: list[dict] = []
    if source in ("all", "campaign"):
        jobs += campaign_targets_scale()
    if source in ("all", "corpus"):
        jobs += corpus_targets_scale()
    for job in jobs:
        job["class"] = instance_class(job["instance_name"], job["source"], job.get("cell", ""))
    return jobs


# ----------------------------------------------------------------------------
# pricing
# ----------------------------------------------------------------------------


def predicted_call_seconds(recorded_seconds: float | None, recorded_status: str | None,
                           deadline: float = DEADLINE, inflation: float = SPREAD_INFLATION,
                           floor: float = 0.01) -> float:
    """One call's price from a recorded identity run: inflated for the
    relabelling spread, capped at the deadline; a censored record (or none)
    is priced at the full deadline."""
    if recorded_seconds is None or not np.isfinite(recorded_seconds) \
            or recorded_status not in ("sat", "unsat"):
        return float(deadline)
    return float(min(max(recorded_seconds * inflation, floor), deadline))


def _recorded_tables() -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if SCALE_NODES_CSV.exists():
        sn = pd.read_csv(SCALE_NODES_CSV)
        out["scale_nodes"] = sn.set_index(["instance_name", "config"])
    if FIX_COST_SCALE_CSV.exists():
        fc = pd.read_csv(FIX_COST_SCALE_CSV)
        fc = fc[fc.variant == "fixed"].drop_duplicates("instance_name")
        out["fix_cost"] = fc.set_index("instance_name")
    if PORTFOLIO_CSV.exists():
        pf = pd.read_csv(PORTFOLIO_CSV, low_memory=False)
        pf = pf[pf.labelling == "identity"].drop_duplicates(["base_name", "config"])
        out["portfolio"] = pf.set_index(["base_name", "config"])
    return out


def _lookup(table: pd.DataFrame | None, key, col: str):
    if table is None:
        return None
    try:
        return table.loc[key, col]
    except KeyError:
        return None


def price(jobs: list[dict], deadline: float = DEADLINE, relabellings: int = RELABELLINGS,
          recorded: dict[str, pd.DataFrame] | None = None, probe_seconds: float | None = 10.0,
          workers: int = 16) -> pd.DataFrame:
    """One row per (instance, config): the recorded identity seconds for the
    refutation and the witness, and the predicted seconds for all labellings.
    Instances with no run on record are probed at `probe_seconds`."""
    from satisfiability.customer_search import sparse_enough_for_better_move

    recorded = _recorded_tables() if recorded is None else recorded
    sn, fc, pf = recorded.get("scale_nodes"), recorded.get("fix_cost"), recorded.get("portfolio")
    labels = 1 + relabellings
    rows = []
    for job in jobs:
        name = job["instance_name"]
        inst = _materialise(job) if job["source"] == "corpus" else None
        theorem2 = (bool(sparse_enough_for_better_move(inst)) if inst is not None
                    else np.nan)
        for config in CONFIGS:
            if config == "default":
                if job["source"] == "campaign":
                    sec, status = job.get("seconds_default"), job.get("status_default")
                else:
                    sec, status = _lookup(sn, (name, "default"), "seconds"), _lookup(sn, (name, "default"), "status")
            else:
                sec, status = _lookup(fc, name, "seconds"), _lookup(fc, name, "status")
                if sec is None and job["source"] == "corpus" and theorem2 is False:
                    sec, status = _lookup(sn, (name, "csearch"), "seconds"), _lookup(sn, (name, "csearch"), "status")
            hi_sec = _lookup(pf, (name, "csearch"), "seconds_hi")
            rows.append({"instance_name": name, "source": job["source"], "class": job["class"],
                         "n": int(job["n"]), "m": int(job["m"]), "optimum": int(job["optimum"]),
                         "config": config, "theorem2": theorem2,
                         "recorded_lo_seconds": sec, "recorded_lo_status": status,
                         "record": "none" if sec is None else "recorded",
                         "recorded_hi_seconds": hi_sec})
    frame = pd.DataFrame(rows)
    if probe_seconds and (frame.record == "none").any():
        frame = probe_unrecorded(frame, jobs, probe_seconds, workers)
    frame["predicted_lo_seconds"] = [
        predicted_call_seconds(s, st, deadline) * labels
        for s, st in zip(frame.recorded_lo_seconds, frame.recorded_lo_status)]
    frame["predicted_hi_seconds"] = [
        (predicted_call_seconds(h, "sat", deadline) if h is not None and np.isfinite(float(h))
         else WITNESS_FLOOR) * labels
        for h in frame.recorded_hi_seconds]
    frame["labellings"] = labels
    return frame


def _probe(args) -> tuple[str, str, str, int, float]:
    job, config, deadline = args
    inst = _materialise(job)
    status, nodes, seconds, _ = _call(inst, int(job["optimum"]) - 1, config, deadline, _decide)
    return job["instance_name"], config, status, nodes, seconds


def probe_unrecorded(frame: pd.DataFrame, jobs: list[dict], probe_seconds: float,
                     workers: int) -> pd.DataFrame:
    """An identity refutation at a short deadline for every (instance, config)
    with no run on record: a measurement, labelled `probe`; one that hits the
    probe deadline stays unrecorded and is priced at the full deadline."""
    by_name = {job["instance_name"]: job for job in jobs}
    todo = [(by_name[r.instance_name], r.config, probe_seconds)
            for r in frame[frame.record == "none"].itertuples()]
    with mp.Pool(min(workers, max(len(todo), 1))) as pool:
        results = pool.map(_probe, todo, chunksize=1)
    frame = frame.set_index(["instance_name", "config"])
    for name, config, status, nodes, seconds in results:
        frame.loc[(name, config), ["recorded_lo_seconds", "recorded_lo_status", "record"]] = [
            seconds, status, "probe"]
    return frame.reset_index()


def schedule(priced: pd.DataFrame, budget_core_hours: float = BUDGET_CORE_HOURS,
             reserve_seconds: float = 0.0) -> pd.DataFrame:
    """Which refutation calls fit: every witness call is scheduled; refutation
    calls are added cheapest instance first (both configurations of an
    instance together) until the budget, less `reserve_seconds`, is spent."""
    budget = budget_core_hours * 3600.0 - reserve_seconds
    priced = priced.copy()
    priced["run_hi"] = True
    spent = float(priced.predicted_hi_seconds.sum())
    per_instance = priced.groupby("instance_name").predicted_lo_seconds.sum().sort_values()
    run_lo: dict[str, bool] = {}
    for name, cost in per_instance.items():
        if spent + cost <= budget:
            run_lo[name] = True
            spent += cost
        else:
            run_lo[name] = False
    priced["run_lo"] = priced.instance_name.map(run_lo)
    priced["scheduled_seconds"] = priced.predicted_hi_seconds + np.where(
        priced.run_lo, priced.predicted_lo_seconds, 0.0)
    return priced


def price_tables(priced: pd.DataFrame) -> dict[str, pd.DataFrame]:
    p = priced.assign(band=priced.n.map(band))
    by_band = []
    for (source, b), d in p.groupby(["source", "band"], sort=False):
        inst = d.drop_duplicates("instance_name")
        by_band.append({
            "source": source, "band": b, "instances": len(inst),
            "refutation priced (core-h)": round(d.predicted_lo_seconds.sum() / 3600, 2),
            "witness priced (core-h)": round(d.predicted_hi_seconds.sum() / 3600, 3),
            "refutations scheduled": int(inst.run_lo.sum()),
            "refutations priced out": int((~inst.run_lo).sum()),
            "scheduled (core-h)": round(d.scheduled_seconds.sum() / 3600, 2),
            "records censored or none": int((~d.recorded_lo_status.isin(["sat", "unsat"])).sum()),
            "probed": int((d.record == "probe").sum()),
        })
    out_cls = []
    for cls, d in p[~p.run_lo].groupby("class"):
        inst = d.drop_duplicates("instance_name")
        out_cls.append({"class": cls, "n": int(d.n.iloc[0]), "instances priced out": len(inst),
                        "refutation would cost (core-h)": round(d.predicted_lo_seconds.sum() / 3600, 2),
                        "recorded identity seconds (default, median)": float(
                            d[d.config == "default"].recorded_lo_seconds.median()),
                        "recorded identity seconds (csearch, median)": float(
                            d[d.config == "csearch"].recorded_lo_seconds.median())})
    total = pd.DataFrame([{
        "instances": priced.instance_name.nunique(),
        "calls scheduled": int((priced.run_hi * priced.labellings).sum()
                               + (priced.run_lo * priced.labellings).sum()),
        "priced (core-h)": round(priced.scheduled_seconds.sum() / 3600, 2),
        "budget (core-h)": BUDGET_CORE_HOURS,
        "refutation calls priced out": int((~priced.run_lo * priced.labellings).sum()),
        "priced out would cost (core-h)": round(
            priced[~priced.run_lo].predicted_lo_seconds.sum() / 3600, 2),
    }])
    return {"by_band": pd.DataFrame(by_band), "priced_out": pd.DataFrame(out_cls), "total": total}


# ----------------------------------------------------------------------------
# the run
# ----------------------------------------------------------------------------


def run_sides(inst: MOSPInstance, optimum: int, config: str, sides: tuple[str, ...],
              deadline_seconds: float | None) -> dict:
    """`decide(optimum − 1)` and/or `decide(optimum)` under one configuration,
    with the same row schema as `learning.differential.run_pair`; a side not
    run is recorded as `skipped`."""
    from satisfiability.customer_search import sparse_enough_for_better_move

    row = {"config": config, "sides": "+".join(sides),
           "better_move": bool(sparse_enough_for_better_move(inst)) if config == "csearch" else False}
    if "lo" not in sides:
        row.update(status_lo="skipped", nodes_lo=np.nan, seconds_lo=np.nan)
    elif optimum <= 1:
        row.update(status_lo="trivial", nodes_lo=0, seconds_lo=0.0)
    else:
        status, nodes, seconds, _ = _call(inst, optimum - 1, config, deadline_seconds, _decide)
        row.update(status_lo=status, nodes_lo=nodes, seconds_lo=seconds)
    if "hi" not in sides:
        row.update(status_hi="skipped", nodes_hi=np.nan, seconds_hi=np.nan,
                   witness_value=None, witness_ok=None)
        return row
    status, nodes, seconds, order = _call(inst, optimum, config, deadline_seconds, _decide)
    value = witness_value(inst, order) if status == "sat" else None
    row.update(status_hi=status, nodes_hi=nodes, seconds_hi=seconds, witness_value=value,
               witness_ok=(value is not None and value <= optimum) if status == "sat" else None)
    return row


def _decide(instance: MOSPInstance, k: int, **kwargs):
    from satisfiability.customer_search import decide

    return decide(instance, k, **kwargs)


def _job(args) -> dict:
    job, label, config, sides, deadline = args
    base = _materialise(job)
    inst = dict(labellings(base, RELABELLINGS, recovering=False))[label]
    row = {"base_name": base.name, "labelling": label, "instance_name": inst.name,
           "source": job["source"], "cell": job.get("cell", ""), "class": job["class"],
           "n": inst.n_customers, "m": inst.n_patterns, "optimum": int(job["optimum"])}
    row.update(run_sides(inst, int(job["optimum"]), config, tuple(sides), deadline))
    return row


def build_jobs(jobs: list[dict], scheduled: pd.DataFrame, relabellings: int = RELABELLINGS,
               deadline: float = DEADLINE, done: dict | set | None = None) -> list[tuple]:
    """One job per (instance, labelling, configuration), the sides the
    schedule allows less those already recorded (`done` maps the triple to
    the sides on record), dearest first so the long calls start early."""
    plan = scheduled.set_index(["instance_name", "config"])
    labels = ["identity"] + [f"relabel{k}" for k in range(relabellings)]
    if isinstance(done, set):
        done = {key: {"lo", "hi"} for key in done}
    out = []
    for job in jobs:
        for config in CONFIGS:
            rec = plan.loc[(job["instance_name"], config)]
            sides = ("lo", "hi") if bool(rec.run_lo) else ("hi",)
            cost = float(rec.scheduled_seconds)
            for label in labels:
                recorded = done.get((job["instance_name"], label, config), set()) if done else set()
                todo = tuple(s for s in sides if s not in recorded)
                if not todo:
                    continue
                out.append((cost, (job, label, config, todo, deadline)))
    out.sort(key=lambda t: -t[0])
    return [t[1] for t in out]


def recorded_sides(frame: pd.DataFrame) -> dict[tuple, set]:
    """Which sides each (instance, labelling, configuration) already has."""
    done: dict[tuple, set] = {}
    for rec in frame.itertuples():
        key = (rec.base_name, rec.labelling, rec.config)
        done.setdefault(key, set()).update(str(rec.sides).split("+"))
    return done


def run(jobs: list[dict], scheduled: pd.DataFrame, workers: int = 16, deadline: float = DEADLINE,
        out: Path = ROWS_CSV, wall: float | None = None, progress_every: int = 200) -> pd.DataFrame:
    done: dict = {}
    if out.exists():
        done = recorded_sides(pd.read_csv(out, low_memory=False))
    args = build_jobs(jobs, scheduled, RELABELLINGS, deadline, done)
    print(f"run: {len(args)} jobs ({len(done)} already recorded), {workers} workers, "
          f"{deadline:.0f} s per call", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    buffer: list[dict] = []
    finished = 0

    def _flush() -> None:
        if buffer:
            pd.DataFrame(buffer).to_csv(out, mode="a", header=not out.exists(), index=False)
            buffer.clear()

    with mp.Pool(workers) as pool:
        for row in pool.imap_unordered(_job, args, chunksize=1):
            buffer.append(row)
            finished += 1
            if finished % progress_every == 0:
                _flush()
                print(f"  {finished}/{len(args)} jobs, {time.time() - started:.0f} s", flush=True)
            if wall is not None and time.time() - started > wall:
                print(f"  wall {wall:.0f} s reached after {finished} jobs; in-flight jobs dropped",
                      flush=True)
                pool.terminate()
                break
    _flush()
    frame = pd.read_csv(out, low_memory=False)
    print(f"run: {finished} jobs in {time.time() - started:.0f} s; {len(frame)} rows -> {out}")
    return frame


# ----------------------------------------------------------------------------
# item 04's variants on the cheap sparse instances
# ----------------------------------------------------------------------------


def variant_targets(jobs: list[dict], cheap_seconds: float = VARIANT_CHEAP_SECONDS,
                    recorded: dict[str, pd.DataFrame] | None = None) -> list[dict]:
    """Instances with Theorem 2 on whose identity refutation under today's
    rule settled within `cheap_seconds` in §31's scale table."""
    recorded = _recorded_tables() if recorded is None else recorded
    fc = recorded.get("fix_cost")
    if fc is None:
        return []
    out = []
    for job in jobs:
        sec = _lookup(fc, job["instance_name"], "seconds")
        status = _lookup(fc, job["instance_name"], "status")
        bm = _lookup(fc, job["instance_name"], "better_move")
        if sec is not None and status == "unsat" and bool(bm) and float(sec) <= cheap_seconds:
            out.append(dict(job, fixed_seconds=float(sec), fixed_nodes=int(_lookup(fc, job["instance_name"], "nodes"))))
    return out


def _variant_job(args) -> list[dict]:
    from learning.fix_cost import decide_variant

    job, deadline, variants = args
    base = _materialise(job)
    k = int(job["optimum"]) - 1
    rows = []
    for label, inst in labellings(base, RELABELLINGS, recovering=False):
        for variant in variants:
            answer, seconds, bm = decide_variant(inst, k, variant, deadline)
            rows.append({"base_name": base.name, "labelling": label, "source": job["source"],
                         "class": job["class"], "n": inst.n_customers, "m": inst.n_patterns,
                         "optimum": int(job["optimum"]), "variant": variant, "better_move": bm,
                         "status_lo": answer.status, "nodes_lo": int(answer.nodes),
                         "seconds_lo": seconds})
    return rows


def run_variants(jobs: list[dict], workers: int = 16, deadline: float = VARIANT_DEADLINE,
                 variants: tuple[str, ...] = ("fixed",) + VARIANT_NAMES,
                 out: Path = VARIANTS_CSV, wall: float | None = None) -> pd.DataFrame:
    done: set = set()
    if out.exists():
        done = set(pd.read_csv(out).base_name)
    args = [(job, deadline, variants) for job in jobs if job["instance_name"] not in done]
    print(f"variants: {len(args)} instances × {1 + RELABELLINGS} labellings × {len(variants)} variants",
          flush=True)
    started = time.time()
    buffer: list[dict] = []
    finished = 0
    with mp.Pool(workers) as pool:
        for rows in pool.imap_unordered(_variant_job, args, chunksize=1):
            buffer.extend(rows)
            finished += 1
            if finished % 50 == 0:
                pd.DataFrame(buffer).to_csv(out, mode="a", header=not out.exists(), index=False)
                buffer.clear()
                print(f"  {finished}/{len(args)} instances, {time.time() - started:.0f} s", flush=True)
            if wall is not None and time.time() - started > wall:
                print(f"  wall {wall:.0f} s reached after {finished} instances", flush=True)
                pool.terminate()
                break
    if buffer:
        pd.DataFrame(buffer).to_csv(out, mode="a", header=not out.exists(), index=False)
    frame = pd.read_csv(out)
    print(f"variants: {finished} instances in {time.time() - started:.0f} s; {len(frame)} rows -> {out}")
    return frame


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def summaries(rows: pd.DataFrame) -> pd.DataFrame:
    """`learning.differential.verdict` per instance over its rows."""
    out = []
    for base, d in rows.groupby("base_name"):
        recs = d.to_dict("records")
        for r in recs:
            r["witness_ok"] = None if pd.isna(r.get("witness_ok")) else bool(r["witness_ok"])
        v = verdict(recs)
        v.update(base_name=base, source=d.source.iloc[0], **{"class": d["class"].iloc[0]},
                 n=int(d.n.iloc[0]), m=int(d.m.iloc[0]), optimum=int(d.optimum.iloc[0]),
                 seconds=float(d.seconds_lo.fillna(0).sum() + d.seconds_hi.fillna(0).sum()),
                 refutation_run=bool((d.status_lo != "skipped").any()))
        out.append(v)
    return pd.DataFrame(out)


def audit_table(rows: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    r = rows.assign(band=rows.n.map(band))
    s = summary.assign(band=summary.n.map(band))
    out = []
    groups = list(s.groupby(["source", "band"], sort=False)) + [(("TOTAL", ""), s)]
    for (source, b), d in groups:
        rr = r if source == "TOTAL" else r[(r.source == source) & (r.band == b)]
        out.append({
            "source": source, "band": b, "instances": len(d),
            "with refutation": int(d.refutation_run.sum()),
            "labellings": int(rr.labelling.nunique()),
            "decision calls": int((rr.status_lo.isin(["sat", "unsat", "unknown"])).sum()
                                  + (rr.status_hi.isin(["sat", "unsat", "unknown"])).sum()),
            "unsat at opt-1": int((rr.status_lo == "unsat").sum()),
            "sat at opt": int((rr.status_hi == "sat").sum()),
            "censored opt-1": int((rr.status_lo == "unknown").sum()),
            "censored opt": int((rr.status_hi == "unknown").sum()),
            "witness failures": int(d.witness_failures.sum()),
            "disagreements": int(d.disagreement.sum()),
            "contradictions": int(d.contradiction.sum()),
            "core-hours": round(float(d.seconds.sum()) / 3600, 2),
        })
    return pd.DataFrame(out)


def censoring_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Per class and configuration: how many refutation calls settled, the
    censored lower bounds, and whether every labelling agreed."""
    r = rows[rows.status_lo.isin(["sat", "unsat", "unknown"])]
    out = []
    for (cls, config), d in r.groupby(["class", "config"]):
        if (d.status_lo == "unknown").sum() == 0:
            continue
        out.append({
            "class": cls, "n": int(d.n.iloc[0]), "config": config, "calls": len(d),
            "instances": d.base_name.nunique(),
            "settled": int((d.status_lo == "unsat").sum()),
            "censored": int((d.status_lo == "unknown").sum()),
            "instances censored on every labelling": int(
                (d.groupby("base_name").status_lo.apply(lambda s: (s == "unknown").all())).sum()),
            "instances settled on some, censored on others": int(
                (d.groupby("base_name").status_lo.apply(lambda s: (s == "unknown").any() and (s == "unsat").any())).sum()),
            "censored nodes min (lower bound)": int(d[d.status_lo == "unknown"].nodes_lo.min()),
            "settled nodes median": float(d[d.status_lo == "unsat"].nodes_lo.median()) if (d.status_lo == "unsat").any() else np.nan,
        })
    return pd.DataFrame(out)


def spread_table(rows: pd.DataFrame, which: str = "lo", by: str = "band",
                 value: str = "nodes", label_col: str = "config") -> pd.DataFrame:
    """Relabelling spread of the node count per size band (or class) and
    configuration (or variant): max/min ratio of `1 + nodes` over labellings
    that settled, identity over the minimum, MAD of log10, and how many
    bases had a censored labelling (excluded from the ratios, counted)."""
    col, status = f"{value}_{which}", f"status_{which}"
    r = rows[~rows.labelling.str.rstrip("0123456789").isin(RECOVER_METHODS)].copy()
    r["band"] = r.n.map(band)
    out = []
    for (source, lab), d in r.groupby(["source", label_col]):
        for key, b in d.groupby(by, sort=False):
            b = b[b[status] != "skipped"]          # a side recorded in its own row
            if b.empty:
                continue
            censored_bases = b[b[status] == "unknown"].base_name.unique()
            settled = b[b[status].isin(["sat", "unsat"])]
            g = settled.groupby("base_name")
            full = g.size()
            full = full[full == b.groupby("base_name").size().reindex(full.index)]
            settled = settled[settled.base_name.isin(full.index)]
            if settled.empty:
                out.append({"source": source, label_col: lab, by: key, "bases": 0,
                            "bases with a censored labelling": len(censored_bases)})
                continue
            g = settled.groupby("base_name")
            lo, hi = g[col].min(), g[col].max()
            ident = settled[settled.labelling == "identity"].set_index("base_name")[col].reindex(lo.index)
            ratio = (1.0 + hi) / (1.0 + lo)
            gain = (1.0 + ident) / (1.0 + lo)
            logs = np.log10(1.0 + settled[col].astype(float))
            dev = (logs - logs.groupby(settled.base_name).transform("median")).abs()
            out.append({
                "source": source, label_col: lab, by: key, "bases": len(lo),
                "bases with a censored labelling": len(censored_bases),
                "identity median": float(ident.median()),
                "bases with any change": int((hi != lo).sum()),
                "max/min median": round(float(ratio.median()), 3),
                "max/min p90": round(float(ratio.quantile(0.9)), 3),
                "max/min max": round(float(ratio.max()), 2),
                "identity/min median": round(float(gain.median()), 3),
                "identity/min p90": round(float(gain.quantile(0.9)), 3),
                "MAD log10": round(float(dev.mean()), 4),
            })
    return pd.DataFrame(out)


def config_agreement_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Per band: pairs of configurations on the same labelling, both settled,
    and whether they agree; plus the csearch / default node ratio."""
    r = rows[rows.status_lo.isin(["sat", "unsat"])]
    wide = r.pivot_table(index=["base_name", "labelling", "n"], columns="config",
                         values="nodes_lo", aggfunc="first").dropna().reset_index()
    if wide.empty or not set(CONFIGS) <= set(wide.columns):
        return pd.DataFrame()
    wide["band"] = wide.n.map(band)
    wide["ratio"] = (1 + wide["csearch"]) / (1 + wide["default"])
    out = []
    for b, d in wide.groupby("band", sort=False):
        out.append({"band": b, "pairs both settled": len(d), "bases": d.base_name.nunique(),
                    "csearch/default median": round(float(d.ratio.median()), 3),
                    "p10": round(float(d.ratio.quantile(0.1)), 3),
                    "p90": round(float(d.ratio.quantile(0.9)), 3),
                    "equal": int((d["csearch"] == d["default"]).sum())})
    return pd.DataFrame(out)


def variant_tables(vrows: pd.DataFrame) -> dict[str, pd.DataFrame]:
    v = vrows.copy()
    v["band"] = v.n.map(band)
    false = []
    for (variant, b), d in v.groupby(["variant", "band"], sort=False):
        false.append({"variant": variant, "band": b, "instances": d.base_name.nunique(),
                      "calls": len(d), "unsat": int((d.status_lo == "unsat").sum()),
                      "false sat at opt-1": int((d.status_lo == "sat").sum()),
                      "instances with a false answer": int(d[d.status_lo == "sat"].base_name.nunique()),
                      "censored": int((d.status_lo == "unknown").sum()),
                      "seconds": round(float(d.seconds_lo.sum()), 1)})
    spread = spread_table(v.assign(config=v.variant), "lo", label_col="config")
    spread = spread.rename(columns={"config": "variant"})
    # paired against fixed on the identity
    ident = v[(v.labelling == "identity") & (v.status_lo == "unsat")]
    wide = ident.pivot_table(index=["base_name", "n"], columns="variant", values="nodes_lo",
                             aggfunc="first").reset_index()
    paired = []
    if "fixed" in wide.columns:
        wide["band"] = wide.n.map(band)
        for variant in VARIANT_NAMES:
            if variant not in wide.columns:
                continue
            for b, d in wide.dropna(subset=[variant, "fixed"]).groupby("band", sort=False):
                ratio = (1 + d[variant]) / (1 + d["fixed"])
                paired.append({"variant": variant, "band": b, "instances": len(d),
                               "nodes vs fixed median": round(float(ratio.median()), 3),
                               "p10": round(float(ratio.quantile(0.1)), 3),
                               "p90": round(float(ratio.quantile(0.9)), 3),
                               "total ratio": round(float((1 + d[variant]).sum() / (1 + d["fixed"]).sum()), 3)})
    return {"false": pd.DataFrame(false), "spread": spread, "paired": pd.DataFrame(paired)}


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    if frame is None or len(frame) == 0:
        return "*(empty)*\n\n"
    return frame.to_markdown(index=False, floatfmt=floatfmt) + "\n\n"


def write_tables(rows_csv: Path = ROWS_CSV, price_csv: Path = PRICE_CSV,
                 variants_csv: Path = VARIANTS_CSV, out: Path = TABLES) -> str:
    text = (f"# The differential harness above 40: tables\n\n*Regenerated "
            f"{time.strftime('%Y-%m-%d %H:%M')} by `python -m learning.differential_scale --stage tables`.*\n\n")
    if price_csv.exists():
        priced = pd.read_csv(price_csv)
        pt = price_tables(priced)
        text += "### Price, before the run\n\n" + _md(pt["total"]) + _md(pt["by_band"])
        text += "### Priced out: refutations not scheduled\n\n" + _md(pt["priced_out"])
    if rows_csv.exists():
        rows = pd.read_csv(rows_csv, low_memory=False)
        summary = summaries(rows)
        text += "### Audit: every run, every verdict\n\n" + _md(audit_table(rows, summary))
        flagged = summary[summary.disagreement | summary.contradiction]
        text += "### Flagged instances (empty means zero)\n\n" + _md(
            flagged[["source", "base_name", "n", "m", "optimum", "disagreeing", "contradiction", "witness_failures"]])
        text += "### Censored refutations, by class and configuration\n\n" + _md(censoring_table(rows))
        text += ("### Relabelling spread of the refutation (opt-1), identity and 4 relabellings, by size\n\n"
                 + _md(spread_table(rows, "lo")))
        text += ("### Relabelling spread of the refutation, by class (75 and 100 customers)\n\n"
                 + _md(spread_table(rows[rows.n >= 75], "lo", by="class")))
        text += ("### Relabelling spread of the witness search (opt), by size\n\n"
                 + _md(spread_table(rows, "hi")))
        text += "### The two configurations on the same labelling\n\n" + _md(config_agreement_table(rows))
        secs = rows.assign(band=rows.n.map(band)).groupby(["source", "band"], sort=False).agg(
            seconds=("seconds_lo", lambda s: float(s.fillna(0).sum())),
            seconds_hi=("seconds_hi", lambda s: float(s.fillna(0).sum())))
        secs["core-hours"] = ((secs.seconds + secs.seconds_hi) / 3600).round(2)
        text += "### Actual cost\n\n" + _md(secs.reset_index())
    if variants_csv.exists():
        vt = variant_tables(pd.read_csv(variants_csv))
        text += "### Item 04's variants above 40: false answers of the reverts\n\n" + _md(vt["false"])
        text += "### Item 04's variants: relabelling spread of the refutation\n\n" + _md(vt["spread"])
        text += "### Item 04's variants: nodes against today's rule, identity labelling\n\n" + _md(vt["paired"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return text


# ----------------------------------------------------------------------------
# entry point
# ----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=("price", "run", "variants", "tables"), default="price")
    parser.add_argument("--source", choices=("all", "campaign", "corpus"), default="all")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--deadline", type=float, default=DEADLINE)
    parser.add_argument("--budget", type=float, default=BUDGET_CORE_HOURS, help="core-hours")
    parser.add_argument("--reserve", type=float, default=0.0,
                        help="seconds of the budget held back (for the variants stage)")
    parser.add_argument("--wall", type=float, default=None, help="wall-clock seconds for the stage")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if args.stage == "tables":
        print(write_tables())
        return
    jobs = targets(args.source)
    if args.limit:
        jobs = jobs[:args.limit]
    if args.stage == "variants":
        vjobs = variant_targets(jobs)
        print(f"{len(vjobs)} of {len(jobs)} instances are cheap sparse targets for the variants")
        run_variants(vjobs, args.workers, wall=args.wall)
        return
    priced = schedule(price(jobs, args.deadline, workers=args.workers), args.budget, args.reserve)
    PRICE_CSV.parent.mkdir(parents=True, exist_ok=True)
    priced.to_csv(PRICE_CSV, index=False)
    for name, table in price_tables(priced).items():
        print(f"--- {name}\n{table.to_string()}\n")
    if args.stage == "run":
        run(jobs, priced, args.workers, args.deadline, wall=args.wall)


if __name__ == "__main__":
    main()
