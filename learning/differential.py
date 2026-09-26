"""The differential harness: is every refutation we hold sound under relabelling?

Question (`reports/ml_nature_plan_2.md` §2.1(a), loop0003 item 01). The
certified corpus and the generated campaign rest on the complete customer
search saying `unsat` at `optimum - 1`. Nothing outside the search checks that
answer above 15 customers (the lattice oracle) except a second configuration
of the same search (`learning.node_counts`), and the two false refutations of
`reports/better_move_bug.md` were invisible to every witness-based audit,
because a witness proves a value is *achievable* and a refutation one step too
strong leaves the witness intact. This module adds the check the plan asks
for: **differential testing over the symmetries the search must respect**.

The invariants, from `reports/ml_nature.md` §13. The search reads the
self-inclusive neighbour masks `N[c]` of the MOSP graph and nothing else, so

  * **relabelling** the customers (rows permuted, columns too) must leave the
    *status* of every decision call unchanged and is free to change the node
    count -- a dominance rule that fires on a tie broken by customer index is
    exactly the kind of rule a wrong implementation would get right on one
    labelling and wrong on another;
  * **re-covering** the same edge set with different products (a fresh greedy
    edge-clique cover) must leave both status and, under the default
    configuration, the node count *exactly* unchanged; under `csearch` the
    count may move when the cover crosses Theorem 2's density threshold.

For every instance the harness therefore runs the identity labelling, `k`
random relabellings and one re-covering, and on each of them `decide(optimum
- 1)` -- expected `unsat` -- and `decide(optimum)` -- expected `sat`, with the
returned closing order simulated on the instance -- under both configurations
(`learning.node_counts.CONFIGS`). Three things are reported, kept apart:

  1. a **disagreement**: two runs on the same instance and the same `k` that
     return `sat` and `unsat`. That is an unsound rule, whichever side is
     wrong, and the instance and labelling are drawn;
  2. a **contradiction**: every run agrees, but against the certificate (`sat`
     at `optimum - 1`, or `unsat` at `optimum`, or a witness that simulates
     above `optimum`). The existing audits would also see the first of these;
  3. an **oracle mismatch**: wherever the active customers number at most 15,
     `learning.degeneracy`'s subset-lattice minimum -- which shares no code
     with the search -- differs from the certified optimum, on the instance or
     on its re-covering.

A call that hits the deadline returns `unknown`, which is a censored
observation and never a disagreement; it is counted and its node count kept
as a lower bound. Every node count is recorded, because the spread of the
count over relabellings is the noise floor §2.3 needs and the portfolio §2.4
would exploit.

The planted-fault test (`tests/test_differential.py`) wraps `decide` in a
liar that answers `unsat` at `optimum` on one relabelling, and the harness
has to draw it.

Scope. The campaign (`learning/data/ensemble/results.csv`, 37,800 instances at
10-40 customers, regenerated from the manifest and checked by digest), the
certified corpus at `n <= 40` (6,135 instances, 9-40 customers, read from
`solutions/`), and the lattice oracle wherever the active customers number at
most 15. Nothing here touches `_lower_bound`, changes any default, or writes
to `solutions/`.

Run:
    python -m learning.differential --workers 16           # everything, ~15 min
    python -m learning.differential --source campaign --limit 500
    python -m learning.differential --stage tables         # tables from the CSVs
    python -m learning.differential --stage drawn          # re-certify the flagged instances, ~10 s
    python -m learning.differential --stage shrink         # minimal counterexamples, ~1 min

Writes `learning/data/ensemble/differential.csv.gz` (one row per instance,
labelling and configuration; committed, item 04 reads it),
`learning/data/ensemble/differential_summary.csv` (one row per instance with
its verdicts), `differential_drawn.csv` and `differential_drawn_rules.csv` (the
flagged instances re-certified, and which rule pairing each false answer
needs) and `reports/differential_tables.md`.
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR
from learning.node_counts import CONFIGS, certified_targets, refutation_kwargs
from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
RESULTS_CSV = ENSEMBLE_DIR / "results.csv"
ROWS_CSV = ENSEMBLE_DIR / "differential.csv.gz"
SUMMARY_CSV = ENSEMBLE_DIR / "differential_summary.csv"
PARTIAL_CSV = Path("learning/data/differential_partial.csv")
TABLES = Path("reports/differential_tables.md")

RELABELLINGS = 8
ORACLE_MAX_ACTIVE = 15
RECOVER_METHODS = ("greedy", "merge", "split")   # the first that applies
SIZE_BANDS = ((0, 10), (11, 15), (16, 20), (21, 25), (26, 30), (31, 35), (36, 40))

DecideFn = Callable[..., object]


# ----------------------------------------------------------------------------
# labellings
# ----------------------------------------------------------------------------


def labellings(instance: MOSPInstance, relabellings: int = RELABELLINGS,
               recovering: bool = True) -> list[tuple[str, MOSPInstance]]:
    """The identity, `relabellings` random relabellings, and one re-covering.

    The relabellings and the re-covering are seeded from the instance name
    through `learning.graph_story`, so a labelling regenerates from
    `(instance_name, labelling)` alone. The re-covering is the first of
    `RECOVER_METHODS` that applies; a re-covering that fails to keep the
    labelled graph (it never should) is dropped rather than tested.
    """
    from learning.graph_story import recover, relabel, same_labelled_graph

    out = [("identity", instance)]
    for k in range(relabellings):
        out.append((f"relabel{k}", relabel(instance, k)[0]))
    if recovering:
        for method in RECOVER_METHODS:
            cand = recover(instance, method, 0)
            if cand is not None and same_labelled_graph(instance, cand):
                out.append((f"{method}0", cand))
                break
    return out


# ----------------------------------------------------------------------------
# one instance
# ----------------------------------------------------------------------------


def _default_decide(instance: MOSPInstance, k: int, **kwargs):
    from satisfiability.customer_search import decide

    return decide(instance, k, **kwargs)


def _call(instance: MOSPInstance, k: int, config: str, deadline_seconds: float | None,
          decide_fn: DecideFn) -> tuple[str, int, float, list[int] | None]:
    kwargs = refutation_kwargs(instance, config)
    deadline = None if deadline_seconds is None else time.monotonic() + deadline_seconds
    started = time.monotonic()
    answer = decide_fn(instance, k, deadline=deadline, **kwargs)
    return answer.status, int(answer.nodes), round(time.monotonic() - started, 4), answer.order


def witness_value(instance: MOSPInstance, closing_order: list[int] | None) -> int | None:
    """The open-stack peak of the product order a closing order constructs."""
    if closing_order is None:
        return None
    from mosp.verify import max_open_stacks
    from satisfiability.heuristics import product_order_from_customers

    return int(max_open_stacks(instance, product_order_from_customers(instance, closing_order)))


def run_pair(instance: MOSPInstance, optimum: int, config: str,
             deadline_seconds: float | None = None,
             decide_fn: DecideFn | None = None) -> dict:
    """`decide(optimum - 1)` and `decide(optimum)` under one configuration.

    `status_lo` is expected `unsat`, `status_hi` expected `sat` with a closing
    order whose constructed product order simulates to at most `optimum`
    (`witness_ok`). An `optimum` of 1 has nothing below it to refute; the low
    call is then recorded as `trivial` with zero nodes.
    """
    decide_fn = decide_fn or _default_decide
    from satisfiability.customer_search import sparse_enough_for_better_move

    row = {"config": config,
           "better_move": bool(sparse_enough_for_better_move(instance)) if config == "csearch" else False}
    if optimum <= 1:
        row.update(status_lo="trivial", nodes_lo=0, seconds_lo=0.0)
    else:
        status, nodes, seconds, _ = _call(instance, optimum - 1, config, deadline_seconds, decide_fn)
        row.update(status_lo=status, nodes_lo=nodes, seconds_lo=seconds)
    status, nodes, seconds, order = _call(instance, optimum, config, deadline_seconds, decide_fn)
    value = witness_value(instance, order) if status == "sat" else None
    row.update(status_hi=status, nodes_hi=nodes, seconds_hi=seconds,
               witness_value=value,
               witness_ok=(value is not None and value <= optimum) if status == "sat" else None)
    return row


def oracle_minima(instance: MOSPInstance) -> dict | None:
    """The subset-lattice minima under both measures, or None above the cap."""
    from learning.degeneracy import Compact, closing_weights, lattice_minimum

    comp = Compact(instance)
    if comp.a == 0 or comp.a > ORACLE_MAX_ACTIVE:
        return None
    search, construction = closing_weights(comp)
    return {"oracle_search": lattice_minimum(search, comp.a),
            "oracle_construction": lattice_minimum(construction, comp.a)}


def differential(instance: MOSPInstance, optimum: int, relabellings: int = RELABELLINGS,
                 recovering: bool = True, configs: tuple[str, ...] = CONFIGS,
                 deadline_seconds: float | None = None, decide_fn: DecideFn | None = None,
                 oracle: bool = True) -> tuple[list[dict], dict]:
    """Every run on one instance, and the verdict over them.

    Returns `(rows, summary)`: one row per labelling and configuration with
    both calls' status, nodes and seconds, and the summary `verdict` builds.
    """
    rows = []
    for label, inst in labellings(instance, relabellings, recovering):
        for config in configs:
            row = {"base_name": instance.name, "labelling": label,
                   "instance_name": inst.name, "n": inst.n_customers,
                   "m": inst.n_patterns, "optimum": optimum}
            row.update(run_pair(inst, optimum, config, deadline_seconds, decide_fn))
            rows.append(row)
    summary = verdict(rows)
    summary.update(base_name=instance.name, n=instance.n_customers,
                   m=instance.n_patterns, optimum=optimum)
    if oracle:
        summary.update(oracle_on(instance, optimum, rows))
    return rows, summary


def oracle_on(instance: MOSPInstance, optimum: int, rows: list[dict]) -> dict:
    """Lattice minima on the instance and on its re-covering, against `optimum`."""
    out: dict = {"oracle_search": None, "oracle_construction": None, "oracle_ok": None,
                 "oracle_recover_search": None, "oracle_recover_ok": None}
    minima = oracle_minima(instance)
    if minima is None:
        return out
    out.update(minima)
    out["oracle_ok"] = (minima["oracle_search"] == optimum
                        and minima["oracle_construction"] == optimum)
    recovered = [r["labelling"] for r in rows if r["labelling"].rstrip("0123456789") in RECOVER_METHODS]
    if recovered:
        from learning.graph_story import recover

        method = recovered[0].rstrip("0123456789")
        cand = recover(instance, method, 0)
        if cand is not None:
            again = oracle_minima(cand)
            if again is not None:
                out["oracle_recover_search"] = again["oracle_search"]
                out["oracle_recover_ok"] = (again["oracle_search"] == optimum
                                            and again["oracle_construction"] == optimum)
    return out


def verdict(rows: list[dict]) -> dict:
    """Disagreements, contradictions and the labellings that carry them.

    A disagreement is two decided (non-`unknown`) statuses that differ at the
    same `k`; the minority side is named in `disagreeing`. A contradiction is a
    decided status, or a witness, against the certificate. Either is a
    finding; both are zero on a sound search with a correct certificate.
    """
    lo = [r for r in rows if r["status_lo"] in ("sat", "unsat")]
    hi = [r for r in rows if r["status_hi"] in ("sat", "unsat")]
    statuses_lo = {r["status_lo"] for r in lo}
    statuses_hi = {r["status_hi"] for r in hi}

    disagreeing: list[str] = []
    for calls, key in ((lo, "status_lo"), (hi, "status_hi")):
        found = {r[key] for r in calls}
        if len(found) > 1:
            counts = {s: sum(1 for r in calls if r[key] == s) for s in found}
            minority = min(found, key=lambda s: (counts[s], s))
            disagreeing += [f"{r['labelling']}/{r['config']}@{key[-2:]}"
                            for r in calls if r[key] == minority]

    contradiction = ("sat" in statuses_lo or "unsat" in statuses_hi
                     or any(r.get("witness_ok") is False for r in rows))
    return {
        "runs": len(rows),
        "labellings": len({r["labelling"] for r in rows}),
        "recovered": any(r["labelling"].rstrip("0123456789") in RECOVER_METHODS for r in rows),
        "unknown_lo": sum(1 for r in rows if r["status_lo"] == "unknown"),
        "unknown_hi": sum(1 for r in rows if r["status_hi"] == "unknown"),
        "disagreement": bool(disagreeing),
        "disagreeing": ";".join(disagreeing),
        "contradiction": bool(contradiction),
        "witness_failures": sum(1 for r in rows if r.get("witness_ok") is False),
        "nodes_lo_default_identity": next((r["nodes_lo"] for r in rows
                                           if r["labelling"] == "identity" and r["config"] == "default"), None),
    }


# ----------------------------------------------------------------------------
# the two sources
# ----------------------------------------------------------------------------


def campaign_targets(results_csv: Path = RESULTS_CSV, limit: int | None = None,
                     max_customers: int | None = None) -> list[dict]:
    """Every certified campaign instance, as the fields that regenerate it."""
    frame = pd.read_csv(results_csv)
    frame = frame[frame.certified.astype(bool)]
    if max_customers is not None:
        frame = frame[frame.n <= max_customers]
    cols = ["instance_name", "cell", "generator", "n", "m", "param", "index", "optimum",
            "matrix_digest"]
    jobs = [{"source": "campaign", **{c: row[c] for c in cols}}
            for row in frame[cols].to_dict("records")]
    return jobs[:limit] if limit is not None else jobs


def corpus_targets(instance_dir: Path = DEFAULT_INSTANCE_DIR,
                   solutions_dir: Path = DEFAULT_SOLUTIONS_DIR, max_customers: int = 40,
                   limit: int | None = None) -> list[dict]:
    """Every certified corpus instance at `n <= max_customers`."""
    jobs = []
    for matrix, name, source_file, collection, optimum, _ in certified_targets(
            instance_dir, solutions_dir, max_customers, limit):
        jobs.append({"source": "corpus", "instance_name": name, "matrix": matrix,
                     "source_file": source_file, "collection": collection,
                     "optimum": int(optimum), "cell": collection})
    return jobs


def _materialise(job: dict) -> MOSPInstance:
    if job["source"] == "campaign":
        from learning.canonical import matrix_digest
        from learning.ensemble import Cell, generate

        inst = generate(Cell(job["generator"], int(job["n"]), int(job["m"]), float(job["param"])),
                        int(job["index"]))
        if matrix_digest(inst) != job["matrix_digest"]:
            raise RuntimeError(f"{job['instance_name']}: regenerated digest differs from the manifest")
        return inst
    matrix = job["matrix"]
    return MOSPInstance(matrix=np.array(matrix, dtype=np.int8), n_customers=len(matrix),
                        n_patterns=len(matrix[0]), name=job["instance_name"])


def _job(args) -> tuple[list[dict], dict]:
    job, relabellings, deadline = args
    instance = _materialise(job)
    started = time.monotonic()
    rows, summary = differential(instance, int(job["optimum"]), relabellings,
                                 deadline_seconds=deadline)
    tags = {"source": job["source"], "cell": job.get("cell", "")}
    for row in rows:
        row.update(tags)
    summary.update(tags, source_file=job.get("source_file", ""),
                   seconds=round(time.monotonic() - started, 3))
    return rows, summary


def run(jobs: list[dict], workers: int = 16, relabellings: int = RELABELLINGS,
        deadline: float | None = 60.0, partial: Path = PARTIAL_CSV,
        rows_csv: Path = ROWS_CSV, summary_csv: Path = SUMMARY_CSV,
        progress_every: int = 2000) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run every job, flushing rows to `partial` as they arrive, then write
    the compressed row table and the per-instance summary."""
    args = [(job, relabellings, deadline) for job in jobs]
    partial.parent.mkdir(parents=True, exist_ok=True)
    if partial.exists():
        partial.unlink()
    summaries: list[dict] = []
    buffer: list[dict] = []
    started = time.time()
    header_written = False

    def _flush() -> None:
        nonlocal header_written
        if not buffer:
            return
        pd.DataFrame(buffer).to_csv(partial, mode="a", header=not header_written, index=False)
        header_written = True
        buffer.clear()

    def _consume(out) -> None:
        rows, summary = out
        buffer.extend(rows)
        summaries.append(summary)
        if len(summaries) % progress_every == 0:
            _flush()
            flagged = sum(s["disagreement"] or s["contradiction"] for s in summaries)
            print(f"  {len(summaries)}/{len(jobs)} instances, {time.time() - started:.0f} s, "
                  f"{flagged} flagged", flush=True)

    if workers <= 1:
        for a in args:
            _consume(_job(a))
    else:
        with multiprocessing.Pool(workers) as pool:
            for out in pool.imap_unordered(_job, args, chunksize=4):
                _consume(out)
    _flush()

    frame = pd.read_csv(partial) if partial.exists() else pd.DataFrame()
    summary = pd.DataFrame(summaries)
    rows_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(rows_csv, index=False, compression="gzip")
    summary.to_csv(summary_csv, index=False)
    return frame, summary


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _band(n: int) -> str:
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return f"{lo}-{hi}"
    return f">{SIZE_BANDS[-1][1]}"


def audit_table(summary: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    """Per source: instances, runs, decision calls, and every kind of failure."""
    out = []
    for source, s in list(summary.groupby("source")) + [("TOTAL", summary)]:
        r = rows if source == "TOTAL" else rows[rows.source == source]
        oracle = s[s.oracle_ok.notna()] if "oracle_ok" in s else s.iloc[0:0]
        out.append({
            "source": source, "instances": len(s), "n range": f"{s.n.min()}-{s.n.max()}",
            "labellings per instance": f"{s.labellings.min()}-{s.labellings.max()}",
            "with a re-covering": int(s.recovered.sum()),
            "decision calls": int((r.status_lo != "trivial").sum() + len(r)),
            "unsat at opt-1": int((r.status_lo == "unsat").sum()),
            "sat at opt": int((r.status_hi == "sat").sum()),
            "unknown (censored)": int(s.unknown_lo.sum() + s.unknown_hi.sum()),
            "witness failures": int(s.witness_failures.sum()),
            "disagreements": int(s.disagreement.sum()),
            "contradictions": int(s.contradiction.sum()),
            "oracle instances (a <= 15)": len(oracle),
            "oracle mismatches": int((~oracle.oracle_ok.astype(bool)).sum()) if len(oracle) else 0,
            "oracle re-covering mismatches": int((oracle.oracle_recover_ok == False).sum()) if len(oracle) else 0,  # noqa: E712
            "seconds": round(float(s.seconds.sum()), 1),
        })
    return pd.DataFrame(out)


def spread_table(rows: pd.DataFrame, which: str = "lo") -> pd.DataFrame:
    """Relabelling spread of the node count by size band and configuration.

    Over the identity and the relabellings (the re-covering excluded), per
    base: max/min ratio of `1 + nodes`, the ratio of the identity to the
    minimum (what a portfolio would gain over today's labelling), and the
    within-base mean absolute deviation of `log10(1 + nodes)`.
    """
    col = f"nodes_{which}"
    status = f"status_{which}"
    r = rows[~rows.labelling.str.rstrip("0123456789").isin(RECOVER_METHODS)]
    r = r[r[status].isin(("sat", "unsat"))]
    out = []
    for (source, config), d in r.groupby(["source", "config"]):
        d = d.assign(band=d.n.map(_band), log=np.log10(1.0 + d[col].astype(float)))
        for band, b in d.groupby("band", sort=False):
            g = b.groupby("base_name")
            lo, hi = g[col].min(), g[col].max()
            ident = b[b.labelling == "identity"].set_index("base_name")[col]
            ident = ident.reindex(lo.index)
            ratio = (1.0 + hi) / (1.0 + lo)
            gain = (1.0 + ident) / (1.0 + lo)
            dev = (b.log - g.log.transform("median")).abs()
            out.append({
                "source": source, "config": config, "band": band, "bases": len(lo),
                "labellings": int(len(b) / max(len(lo), 1)),
                "identity nodes median": float(ident.median()),
                "bases with any change": int((hi != lo).sum()),
                "max/min median": round(float(ratio.median()), 3),
                "max/min p90": round(float(ratio.quantile(0.9)), 3),
                "max/min max": round(float(ratio.max()), 2),
                "identity/min median": round(float(gain.median()), 3),
                "identity/min p90": round(float(gain.quantile(0.9)), 3),
                "min-of-9 saves >= 1.5x": int((gain >= 1.5).sum()),
                "MAD log10": round(float(dev.mean()), 4),
            })
    frame = pd.DataFrame(out)
    order = [f"{lo}-{hi}" for lo, hi in SIZE_BANDS]
    frame["_o"] = frame.band.map({b: i for i, b in enumerate(order)})
    return frame.sort_values(["source", "config", "_o"]).drop(columns="_o").reset_index(drop=True)


def recover_table(rows: pd.DataFrame) -> pd.DataFrame:
    """The re-covering against the identity: status and node count, per config."""
    ident = rows[rows.labelling == "identity"].set_index(["base_name", "config"])
    rec = rows[rows.labelling.str.rstrip("0123456789").isin(RECOVER_METHODS)]
    rec = rec.set_index(["base_name", "config"])
    joined = rec.join(ident, rsuffix="_id", how="inner").reset_index()
    out = []
    for (source, config), d in joined.groupby(["source", "config"]):
        flipped = d.better_move != d.better_move_id
        out.append({
            "source": source, "config": config, "pairs": len(d),
            "status equal (opt-1)": int((d.status_lo == d.status_lo_id).sum()),
            "status equal (opt)": int((d.status_hi == d.status_hi_id).sum()),
            "nodes equal (opt-1)": int((d.nodes_lo == d.nodes_lo_id).sum()),
            "nodes equal (opt)": int((d.nodes_hi == d.nodes_hi_id).sum()),
            "better_move flipped": int(flipped.sum()),
            "nodes differ (opt-1) outside flips": int(((d.nodes_lo != d.nodes_lo_id) & ~flipped).sum()),
        })
    return pd.DataFrame(out)


def sat_vs_unsat_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Nodes to find a witness at `optimum` against nodes to refute `optimum - 1`."""
    r = rows[(rows.labelling == "identity") & (rows.status_lo == "unsat") & (rows.status_hi == "sat")]
    out = []
    for (source, config), d in r.groupby(["source", "config"]):
        d = d.assign(band=d.n.map(_band))
        for band, b in d.groupby("band", sort=False):
            out.append({
                "source": source, "config": config, "band": band, "instances": len(b),
                "refute median": float(b.nodes_lo.median()), "refute p90": float(b.nodes_lo.quantile(0.9)),
                "refute max": int(b.nodes_lo.max()),
                "witness median": float(b.nodes_hi.median()), "witness p90": float(b.nodes_hi.quantile(0.9)),
                "witness max": int(b.nodes_hi.max()),
                "witness > refute": int((b.nodes_hi > b.nodes_lo).sum()),
                "seconds total": round(float(b.seconds_lo.sum() + b.seconds_hi.sum()), 2),
            })
    frame = pd.DataFrame(out)
    order = [f"{lo}-{hi}" for lo, hi in SIZE_BANDS]
    frame["_o"] = frame.band.map({b: i for i, b in enumerate(order)})
    return frame.sort_values(["source", "config", "_o"]).drop(columns="_o").reset_index(drop=True)


def flagged_table(summary: pd.DataFrame) -> pd.DataFrame:
    cols = ["source", "base_name", "n", "m", "optimum", "disagreement", "disagreeing",
            "contradiction", "witness_failures", "oracle_ok", "oracle_recover_ok"]
    bad = summary[summary.disagreement | summary.contradiction
                  | (summary.oracle_ok == False) | (summary.oracle_recover_ok == False)]  # noqa: E712
    return bad[[c for c in cols if c in bad.columns]]


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    if frame is None or len(frame) == 0:
        return "*(empty)*\n\n"
    return frame.to_markdown(index=False, floatfmt=floatfmt) + "\n\n"


def write_tables(rows_csv: Path = ROWS_CSV, summary_csv: Path = SUMMARY_CSV,
                 out: Path = TABLES, command: str = "") -> str:
    rows = pd.read_csv(rows_csv)
    summary = pd.read_csv(summary_csv)
    text = (f"# The differential harness: tables\n\n*Regenerated "
            f"{time.strftime('%Y-%m-%d %H:%M')} by `{command or 'python -m learning.differential'}`; "
            f"{len(summary)} instances, {len(rows)} runs.*\n\n")
    text += "### Audit: every run, every verdict\n\n" + _md(audit_table(summary, rows))
    text += "### Flagged instances (empty means zero)\n\n" + _md(flagged_table(summary))
    text += ("### Relabelling spread of the refutation (opt-1), identity and 8 relabellings\n\n"
             + _md(spread_table(rows, "lo")))
    text += ("### Relabelling spread of the witness search (opt)\n\n"
             + _md(spread_table(rows, "hi")))
    text += "### The re-covering against the identity\n\n" + _md(recover_table(rows))
    text += "### Witness search against refutation, identity labelling\n\n" + _md(sat_vs_unsat_table(rows))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    return text


# ----------------------------------------------------------------------------
# the drawn instances: re-certification by independent routes, and which rule
# pairing each false answer needs
# ----------------------------------------------------------------------------

DRAWN_CSV = ENSEMBLE_DIR / "differential_drawn.csv"
DRAWN_RULES_CSV = ENSEMBLE_DIR / "differential_drawn_rules.csv"

RULE_PAIRS = {
    "better_move alone": {"definite_move": False, "subset_rule": False},
    "better_move + subset_rule": {"definite_move": False, "subset_rule": True},
    "better_move + definite_move": {"definite_move": True, "subset_rule": False},
    "better_move + both": {"definite_move": True, "subset_rule": True},
}


def _targets_by_name(results_csv: Path, instance_dir: Path, solutions_dir: Path,
                     max_customers: int) -> dict[str, dict]:
    jobs = campaign_targets(results_csv, None, max_customers)
    jobs += corpus_targets(instance_dir, solutions_dir, max_customers)
    return {job["instance_name"]: job for job in jobs}


def recertify_drawn(summary_csv: Path = SUMMARY_CSV, rows_csv: Path = ROWS_CSV,
                    results_csv: Path = RESULTS_CSV, instance_dir: Path = DEFAULT_INSTANCE_DIR,
                    solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
                    ensemble_solutions: Path = ENSEMBLE_DIR / "solutions",
                    max_customers: int = 40) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Every flagged instance re-certified by routes that share nothing with the
    rule under suspicion -- the cached independent solve, the Python reference
    search at `optimum - 1` and `optimum` with its witness simulated, the C
    default, and the lattice oracle where it reaches -- and every false answer
    re-run under the four pairings of `better_move` with the two other
    dominance rules, to say which composition produces it."""
    import json

    from satisfiability.mosp_solver import _solution_path, solve_mosp_exact

    summary = pd.read_csv(summary_csv)
    rows = pd.read_csv(rows_csv, low_memory=False)
    flagged = summary[summary.disagreement | summary.contradiction]
    targets = _targets_by_name(results_csv, instance_dir, solutions_dir, max_customers)

    certs = []
    for rec in flagged.itertuples():
        job = targets[rec.base_name]
        inst = _materialise(job)
        optimum = int(rec.optimum)
        out = {"source": rec.source, "base_name": rec.base_name, "n": inst.n_customers,
               "m": inst.n_patterns, "optimum": optimum, "disagreeing": rec.disagreeing}
        if rec.source == "campaign":
            stats: dict = {}
            value, _ = solve_mosp_exact(inst, solutions_dir=ensemble_solutions, stats=stats)
            out["stored_value"], out["stored_proof"] = int(value), stats.get("proof")
        else:
            data = json.loads(_solution_path(inst, solutions_dir).read_text())
            out["stored_value"], out["stored_proof"] = int(data["mosp_value"]), data.get("provenance")
        py_lo, py_hi = _default_decide(inst, optimum - 1, native=False), _default_decide(inst, optimum, native=False)
        out.update(python_lo=py_lo.status, python_hi=py_hi.status,
                   python_witness=witness_value(inst, py_hi.order))
        out.update(c_default_lo=_default_decide(inst, optimum - 1).status,
                   c_default_hi=_default_decide(inst, optimum).status)
        minima = oracle_minima(inst)
        out.update(oracle_search=None if minima is None else minima["oracle_search"],
                   oracle_construction=None if minima is None else minima["oracle_construction"])
        out["independently_certified"] = bool(
            out["stored_value"] == optimum and py_lo.status == "unsat" and py_hi.status == "sat"
            and out["python_witness"] == optimum and out["c_default_lo"] == "unsat"
            and out["c_default_hi"] == "sat"
            and (minima is None or (minima["oracle_search"] == optimum
                                    and minima["oracle_construction"] == optimum)))
        certs.append(out)

    lying = rows[(rows.status_hi == "unsat") | (rows.status_lo == "sat")]
    verdicts = []
    for rec in lying.itertuples():
        base = _materialise(targets[rec.base_name])
        inst = dict(labellings(base))[rec.labelling]
        k = int(rec.optimum) if rec.status_hi == "unsat" else int(rec.optimum) - 1
        out = {"base_name": rec.base_name, "labelling": rec.labelling, "k": k,
               "expected": "sat" if rec.status_hi == "unsat" else "unsat"}
        for name, kw in RULE_PAIRS.items():
            out[name] = _default_decide(inst, k, better_move=True, better_move_dominators=0, **kw).status
        verdicts.append(out)
    return pd.DataFrame(certs), pd.DataFrame(verdicts)


def drawn_tables(certs: pd.DataFrame, verdicts: pd.DataFrame) -> str:
    text = "### The drawn instances, re-certified by routes independent of the C better_move\n\n"
    if len(certs):
        head = pd.DataFrame([{
            "flagged instances": len(certs),
            "stored value = optimum": int((certs.stored_value == certs.optimum).sum()),
            "Python reference: unsat at opt-1": int((certs.python_lo == "unsat").sum()),
            "Python reference: sat at opt, witness = opt": int(((certs.python_hi == "sat") & (certs.python_witness == certs.optimum)).sum()),
            "C default: unsat / sat": int(((certs.c_default_lo == "unsat") & (certs.c_default_hi == "sat")).sum()),
            "lattice oracle reaches": int(certs.oracle_search.notna().sum()),
            "lattice oracle = optimum": int(((certs.oracle_search == certs.optimum) & (certs.oracle_construction == certs.optimum)).sum()),
            "independently certified": int(certs.independently_certified.sum()),
        }])
        text += _md(head)
        text += _md(certs.drop(columns=["disagreeing"]))
    else:
        text += "*(no flagged instances)*\n\n"
    text += "### Which rule pairing produces each false answer\n\n"
    if len(verdicts):
        counts = {name: int((verdicts[name] != verdicts.expected).sum()) for name in RULE_PAIRS}
        text += _md(pd.DataFrame([{"false answers": len(verdicts), **counts}]))
    else:
        text += "*(none)*\n\n"
    return text


# ----------------------------------------------------------------------------
# shrinking a drawn instance to a hand-checkable counterexample
# ----------------------------------------------------------------------------

SHRINK_TARGETS = (
    # (campaign instance, the rule pairing to keep, tag)
    ("ens_f_n10_m20_d2_i070", {"definite_move": False, "subset_rule": True}, "better_move + subset_rule"),
    ("ens_b_n25_m25_p0.075_i040", {"definite_move": True, "subset_rule": False}, "better_move + definite_move"),
)


def failing_k(matrix: np.ndarray, pairing: dict) -> int | None:
    """The optimum of `matrix` (by the C default, cross-checked with the Python
    reference) if the C with `better_move` under `pairing` refutes it, else None."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 1 or not matrix.any():
        return None
    inst = MOSPInstance.from_matrix(matrix.tolist(), name="shrink")
    optimum = next((k for k in range(1, inst.n_customers + 1)
                    if _default_decide(inst, k).status == "sat"), None)
    if optimum is None or optimum < 2:
        return None
    if _default_decide(inst, optimum, native=False).status != "sat":
        return None
    bad = _default_decide(inst, optimum, better_move=True, better_move_dominators=0, **pairing)
    return optimum if bad.status == "unsat" else None


def shrink(matrix: np.ndarray, pairing: dict) -> np.ndarray:
    """Greedy delta-debugging: drop customers, then products, then single
    ones, while the false refutation persists. A local minimum, not the
    smallest counterexample."""
    matrix = np.asarray(matrix).copy()
    changed = True
    while changed:
        changed = False
        for i in range(matrix.shape[0]):
            trial = np.delete(matrix, i, axis=0)
            if failing_k(trial, pairing) is not None:
                matrix, changed = trial, True
                break
        if changed:
            continue
        for j in range(matrix.shape[1]):
            trial = np.delete(matrix, j, axis=1)
            if failing_k(trial, pairing) is not None:
                matrix, changed = trial, True
                break
        if changed:
            continue
        for i, j in zip(*np.nonzero(matrix)):
            trial = matrix.copy()
            trial[i, j] = 0
            if failing_k(trial, pairing) is not None:
                matrix, changed = trial, True
                break
    return matrix[matrix.sum(1) > 0][:, matrix.sum(0) > 0]


def shrink_report(results_csv: Path = RESULTS_CSV) -> str:
    from satisfiability.heuristics import _neighbour_masks

    targets = {job["instance_name"]: job for job in campaign_targets(results_csv)}
    text = "### Minimal counterexamples by delta-debugging (`--stage shrink`)\n\n"
    for name, pairing, tag in SHRINK_TARGETS:
        base = np.asarray(_materialise(targets[name]).matrix)
        small = shrink(base, pairing)
        k = failing_k(small, pairing)
        inst = MOSPInstance.from_matrix(small.tolist(), name="shrink")
        masks = _neighbour_masks(inst)
        neigh = {c: [d for d in range(inst.n_customers) if masks[c] >> d & 1]
                 for c in range(inst.n_customers)}
        oracle = oracle_minima(inst)
        limits = {dom: _default_decide(inst, k, better_move=True, better_move_dominators=dom,
                                       **pairing).status for dom in (0, 1, 2, 4)}
        text += (f"**{tag}**, from `{name}` {base.shape[0]} × {base.shape[1]} to "
                 f"{small.shape[0]} × {small.shape[1]}, optimum {k} "
                 f"(C default `sat`, Python `sat`, lattice oracle {oracle}); the C with "
                 f"{tag} says `unsat` at {k}; by dominator limit {limits}.\n\n"
                 f"```\nmatrix = {small.tolist()}\nN[c] = {neigh}\n```\n\n")
    return text


# ----------------------------------------------------------------------------
# entry point
# ----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=("run", "tables", "drawn", "shrink"), default="run")
    parser.add_argument("--source", choices=("all", "campaign", "corpus"), default="all")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--relabellings", type=int, default=RELABELLINGS)
    parser.add_argument("--deadline", type=float, default=60.0,
                        help="seconds per decision call before 'unknown'")
    parser.add_argument("--limit", type=int, default=None, help="first N instances per source")
    parser.add_argument("--max-customers", type=int, default=40)
    parser.add_argument("--results", type=Path, default=RESULTS_CSV)
    parser.add_argument("--instance-dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=DEFAULT_SOLUTIONS_DIR)
    parser.add_argument("--rows-csv", type=Path, default=ROWS_CSV)
    parser.add_argument("--summary-csv", type=Path, default=SUMMARY_CSV)
    parser.add_argument("--out", type=Path, default=TABLES)
    args = parser.parse_args()

    if args.stage == "run":
        jobs: list[dict] = []
        if args.source in ("all", "campaign"):
            jobs += campaign_targets(args.results, args.limit, args.max_customers)
        if args.source in ("all", "corpus"):
            jobs += corpus_targets(args.instance_dir, args.solutions_dir, args.max_customers, args.limit)
        print(f"{len(jobs)} instances, {args.relabellings} relabellings + identity + one "
              f"re-covering, {len(CONFIGS)} configurations, 2 calls each, {args.workers} workers",
              flush=True)
        started = time.time()
        rows, summary = run(jobs, args.workers, args.relabellings, args.deadline,
                            rows_csv=args.rows_csv, summary_csv=args.summary_csv)
        print(f"{len(rows)} runs on {len(summary)} instances in {time.time() - started:.0f} s; "
              f"disagreements {int(summary.disagreement.sum())}, "
              f"contradictions {int(summary.contradiction.sum())}", flush=True)
    if args.stage == "shrink":
        text = shrink_report(args.results)
        print(text)
        with args.out.open("a") as fh:
            fh.write(text)
        return
    if args.stage == "drawn":
        certs, verdicts = recertify_drawn(args.summary_csv, args.rows_csv, args.results,
                                          args.instance_dir, args.solutions_dir,
                                          max_customers=args.max_customers)
        certs.to_csv(DRAWN_CSV, index=False)
        verdicts.to_csv(DRAWN_RULES_CSV, index=False)
        text = drawn_tables(certs, verdicts)
        print(text)
        with args.out.open("a") as fh:
            fh.write(text)
        print(f"wrote {DRAWN_CSV} ({len(certs)} rows), {DRAWN_RULES_CSV} ({len(verdicts)} rows)")
        return
    command = "python -m learning.differential " + " ".join(
        a for a in __import__("sys").argv[1:] if not a.startswith("--stage"))
    print(write_tables(args.rows_csv, args.summary_csv, args.out, command.strip()))


if __name__ == "__main__":
    main()
