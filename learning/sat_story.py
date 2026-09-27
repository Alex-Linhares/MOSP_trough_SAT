"""Does the graph story hold for the SAT path? (plan 3 §1 Q5, loop0004 item 03)

§13 of `reports/ml_nature.md` showed that the complete customer search reads
the labelled MOSP graph and nothing else: re-covering the same edge set with
different cliques leaves its node count *exactly* unchanged in 15,900 of
15,900 pairs. The direct SAT encoding (`satisfiability.mosp_encoding`) is not
like that on paper -- it has a position variable per *product*, so the clique
cover is written into the formula. This module asks whether it matters: on
§13's re-covering and relabelling pairs, `decide_mosp`'s reduction (component
decomposition, pattern dominance, `encode_mosp_decision`) is run through a
SAT solver at `optimum - 1` (the refutation) and at `optimum` (the witness),
conflicts and seconds recorded, and the paired ratios read off.

Two backends, for a reason that is itself a finding. `SAT_BACKEND` is
`kissat404`, and through pysat Kissat exposes no statistics, does not honour
`interrupt()` (the note in `benchmarks/ratchet.py`) and refuses incremental
calls, so it cannot be given a conflict budget either. Conflicts are therefore
measured on CaDiCaL 1.9.5 (`cadical195`), which does all three, with a wall
deadline enforced by conflict-budget chunks; a censored call is a lower bound
on conflicts, never a missing value. Kissat is timed in seconds inside a
forked child that is killed at the deadline, on the calls CaDiCaL settled
within `--kissat-cap` seconds, so the default backend is measured on the
same pairs at a bounded cost.

Every instance regenerates from the campaign manifest through
`learning.graph_story.recover` / `relabel`, and each re-covering is checked
to have its base's neighbour masks before it is encoded. Nothing is written
to `solutions/`; no solver default is touched.

Run:

    python -m learning.sat_story --workers 16 --per-n 40 --per-method 1 --relabellings 4 --deadline 120 --wall 3600
    python -m learning.sat_story --stage tables       # tables from the CSV only

Writes `learning/data/ensemble/sat_story.csv.gz` (one row per SAT call,
appended as calls finish; a rerun skips calls already present) and
`reports/sat_story_tables.md`.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import time
import zlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from learning.graph_story import (
    BASE_SIZES,
    RECOVER_CSV,
    RELABEL_CSV,
    RESULTS_CSV,
    _generate_base,
    _md,
    feature_sets,
    recover,
    relabel,
    same_labelled_graph,
)
from mosp.instance import MOSPInstance

ENSEMBLE_DIR = Path("learning/data/ensemble")
MANIFEST_CSV = ENSEMBLE_DIR / "manifest.csv"
SAT_CSV = ENSEMBLE_DIR / "sat_story.csv.gz"
TABLES = Path("reports/sat_story_tables.md")

CONFLICT_BACKEND = "cadical195"       # exposes conflicts, honours a conflict budget
CHUNK = 5_000                          # conflicts per `solve_limited` chunk
METHODS = ("split", "merge", "greedy")
KILL_TOLERANCE = 0.05                  # paired median re-covering ratio within ±5%


# ----------------------------------------------------------------------------
# one SAT decision, instrumented
# ----------------------------------------------------------------------------


def _reduce(instance: MOSPInstance):
    """`decide_mosp`'s reduction: components, then dominated patterns dropped."""
    from mosp.preprocess import components, remove_dominated_patterns

    parts, _free = components(instance)
    return [remove_dominated_patterns(part.instance).instance for part in parts]


def encode_reduced(instance: MOSPInstance, k: int) -> list:
    """The CNFs `decide_mosp` would hand the solver for `MOSP <= k?`, one per
    component, with dominated patterns removed. Returns `[(cnf, m_reduced)]`."""
    from satisfiability.mosp_encoding import encode_mosp_decision

    out = []
    for reduced in _reduce(instance):
        cnf, _pool, m = encode_mosp_decision(reduced, k)
        out.append((cnf, m))
    return out


def decide_conflicts(instance: MOSPInstance, k: int, deadline_seconds: float,
                     backend: str = CONFLICT_BACKEND, chunk: int = CHUNK) -> dict:
    """`decide_mosp(instance, k)` with the cost recorded.

    Solves each component's formula under `backend` in conflict-budget chunks
    until it answers or the wall deadline passes. `status` is `sat`, `unsat`
    or `unknown` (censored); `conflicts` is the total over the components
    tried and is a lower bound when censored.
    """
    from pysat.solvers import Solver

    started = time.monotonic()
    out = {"status": "sat", "conflicts": 0, "decisions": 0, "propagations": 0,
           "vars": 0, "clauses": 0, "m_reduced": 0, "components": 0, "seconds": 0.0}
    for cnf, m in encode_reduced(instance, k):
        out["components"] += 1
        out["m_reduced"] += m
        out["vars"] += int(cnf.nv)
        out["clauses"] += len(cnf.clauses)
        solver = Solver(name=backend, bootstrap_with=cnf.clauses)
        try:
            answer = None
            while answer is None and time.monotonic() - started < deadline_seconds:
                solver.conf_budget(chunk)
                answer = solver.solve_limited()
            stats = solver.accum_stats() or {}
        finally:
            solver.delete()
        for key in ("conflicts", "decisions", "propagations"):
            out[key] += int(stats.get(key, 0))
        if answer is None:
            out["status"] = "unknown"
            break
        if answer is False:
            out["status"] = "unsat"
            break
    out["seconds"] = round(time.monotonic() - started, 4)
    return out


def _kissat_solve(instance: MOSPInstance, k: int, backend: str) -> dict:
    from pysat.solvers import Solver

    started = time.monotonic()
    status = "sat"
    for cnf, _m in encode_reduced(instance, k):
        with Solver(name=backend, bootstrap_with=cnf.clauses) as solver:
            if not solver.solve():
                status = "unsat"
                break
    return {"status": status, "seconds": round(time.monotonic() - started, 4)}


def decide_seconds(instance: MOSPInstance, k: int, deadline_seconds: float,
                   backend: str = "kissat404") -> dict:
    """The same decision on a backend that exposes nothing: seconds only, in a
    forked child killed at the deadline (`status = "unknown"`, `seconds =
    deadline`: a lower bound). A raw `os.fork`, because pool workers are
    daemonic and may not start `multiprocessing` children."""
    import json
    import select
    import signal

    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:                                    # child
        os.close(read_fd)
        code = 0
        try:
            payload = json.dumps(_kissat_solve(instance, k, backend)).encode()
            os.write(write_fd, payload)
        except BaseException:                       # noqa: BLE001 - report as censored
            code = 1
        finally:
            os.close(write_fd)
            os._exit(code)
    os.close(write_fd)
    ready, _, _ = select.select([read_fd], [], [], deadline_seconds)
    if ready:
        chunks = []
        while True:
            chunk = os.read(read_fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        os.close(read_fd)
        os.waitpid(pid, 0)
        data = b"".join(chunks)
        if data:
            return json.loads(data)
        return {"status": "unknown", "seconds": float(deadline_seconds)}
    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)
    os.close(read_fd)
    return {"status": "unknown", "seconds": float(deadline_seconds)}


# ----------------------------------------------------------------------------
# the pairs: §13's bases, re-coverings and relabellings
# ----------------------------------------------------------------------------


def load_pairs(recover_csv: Path = RECOVER_CSV, relabel_csv: Path = RELABEL_CSV):
    rec = pd.read_csv(recover_csv)
    rec = rec[rec.applicable & rec.masks_equal & rec.same_optimum].copy()
    rel = pd.read_csv(relabel_csv)
    return rec, rel


def select_jobs(rec: pd.DataFrame, rel: pd.DataFrame, per_n: int, per_method: int,
                per_base: int, sizes=BASE_SIZES, seed: int = 0) -> pd.DataFrame:
    """One row per SAT call. `per_n` bases per size drawn uniformly from §13's
    200 (which were half uniform, half from the hardest decile by nodes), the
    first `per_method` applicable re-coverings per method and the first
    `per_base` relabellings of each, at `optimum - 1` and `optimum`."""
    rng = np.random.default_rng(seed)
    rows = []
    for n in sizes:
        d = rec[rec.n == n]
        bases = d.drop_duplicates("base_name")
        if bases.empty:
            continue
        chosen = bases.sample(min(per_n, len(bases)), random_state=int(rng.integers(1 << 31)))
        for b in chosen.itertuples():
            spec = {"base_name": b.base_name, "cell": b.cell, "n": int(n), "optimum": int(b.base_optimum),
                    "nodes_default_base": int(b.base_nodes_default)}
            rows.append({**spec, "kind": "base", "method": "base", "k": -1,
                         "instance_name": b.base_name, "nodes_default": int(b.base_nodes_default)})
            for method in METHODS:
                dm = d[(d.base_name == b.base_name) & (d.method == method)].sort_values("k").head(per_method)
                for r in dm.itertuples():
                    rows.append({**spec, "kind": "recover", "method": method, "k": int(r.k),
                                 "instance_name": r.instance_name, "nodes_default": int(r.nodes_default)})
            dl = rel[(rel.base_name == b.base_name) & (rel.k >= 0)].sort_values("k").head(per_base)
            for r in dl.itertuples():
                rows.append({**spec, "kind": "relabel", "method": "relabel", "k": int(r.k),
                             "instance_name": r.instance_name, "nodes_default": int(r.nodes_default)})
    specs = pd.DataFrame(rows)
    jobs = pd.concat([specs.assign(side="refute", kk=specs.optimum - 1),
                      specs.assign(side="witness", kk=specs.optimum)])
    # small sizes first, random within a size: a wall cutoff leaves a random sample
    jobs["_order"] = [zlib.crc32(f"{a}|{b}".encode()) for a, b in zip(jobs.instance_name, jobs.side)]
    return jobs.sort_values(["n", "_order"]).drop(columns="_order").reset_index(drop=True)


def build_instance(base: MOSPInstance, kind: str, method: str, k: int) -> MOSPInstance:
    if kind == "base":
        return base
    if kind == "relabel":
        return relabel(base, k)[0]
    inst = recover(base, method, k)
    if inst is None or not same_labelled_graph(base, inst):
        raise AssertionError(f"{base.name} {method}{k}: re-covering does not reproduce §13's pair")
    return inst


def _job(args) -> dict:
    row, manifest_row, deadline, kissat_cap, kissat_backend = args
    row = SimpleNamespace(**row)
    base = _generate_base(SimpleNamespace(**manifest_row))
    assert base.name == row.base_name, (base.name, row.base_name)
    instance = build_instance(base, row.kind, row.method, int(row.k))
    assert instance.name == row.instance_name, (instance.name, row.instance_name)
    out = {**vars(row), "m": instance.n_patterns}
    conf = decide_conflicts(instance, int(row.kk), deadline)
    out.update({f"c_{key}": val for key, val in conf.items()})
    if kissat_cap is not None and conf["status"] != "unknown" and conf["seconds"] <= kissat_cap:
        kis = decide_seconds(instance, int(row.kk), deadline, kissat_backend)
        out["k_status"], out["k_seconds"] = kis["status"], kis["seconds"]
    else:
        out["k_status"], out["k_seconds"] = "skipped", np.nan
    expected = "unsat" if row.side == "refute" else "sat"
    for prefix in ("c", "k"):
        st = out[f"{prefix}_status"]
        out[f"{prefix}_agrees"] = bool(st == expected) if st not in ("unknown", "skipped") else None
    return out


def run(jobs: pd.DataFrame, workers: int, deadline: float, wall: float | None,
        kissat_cap: float | None = 30.0, kissat_backend: str = "kissat404",
        csv: Path = SAT_CSV, manifest_csv: Path = MANIFEST_CSV) -> pd.DataFrame:
    """Runs every job not already in `csv`, appending as calls finish; stops
    handing out work after `wall` seconds and returns everything on disk."""
    manifest = pd.read_csv(manifest_csv).set_index("instance_name")
    done = set()
    if csv.exists():
        prior = pd.read_csv(csv)
        done = set(zip(prior.instance_name, prior.side))
    todo = jobs[[(a, b) not in done for a, b in zip(jobs.instance_name, jobs.side)]]
    print(f"{len(jobs)} calls, {len(done)} on disk, {len(todo)} to run on {workers} workers, "
          f"deadline {deadline:.0f} s, wall {wall}", flush=True)
    args = [(r, manifest.loc[r["base_name"]].to_dict(), deadline, kissat_cap, kissat_backend)
            for r in todo.to_dict("records")]
    started = time.monotonic()
    rows: list[dict] = []
    header = not csv.exists()

    def _flush():
        nonlocal rows, header
        if rows:
            csv.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(csv, mode="a", header=header, index=False, float_format="%.6g")
            header = False
            rows = []

    if args:
        ctx = mp.get_context("fork")
        with ctx.Pool(workers) as pool:
            it = pool.imap_unordered(_job, args, chunksize=1)
            n_done = 0
            try:
                while True:
                    left = None if wall is None else max(1.0, wall - (time.monotonic() - started))
                    try:
                        rows.append(it.next(timeout=left))
                    except StopIteration:
                        break
                    except mp.TimeoutError:
                        print(f"wall {wall} s reached after {n_done} calls; stopping", flush=True)
                        break
                    n_done += 1
                    if n_done % 50 == 0:
                        _flush()
                        print(f"  {n_done} calls, {time.monotonic() - started:.0f} s", flush=True)
                    if wall is not None and time.monotonic() - started > wall:
                        print(f"wall {wall} s reached after {n_done} calls; stopping", flush=True)
                        break
            finally:
                _flush()
                pool.terminate()
    return pd.read_csv(csv)


# ----------------------------------------------------------------------------
# analysis
# ----------------------------------------------------------------------------


def _log_ratio(new: pd.Series, base: pd.Series) -> pd.Series:
    return np.log10(1.0 + new.astype(float)) - np.log10(1.0 + base.astype(float))


def paired(frame: pd.DataFrame, kind: str = "recover") -> pd.DataFrame:
    """Every (variant, base) pair with both calls on disk, one row per side."""
    bases = frame[frame.kind == "base"].set_index(["base_name", "side"])
    var = frame[frame.kind == kind].copy()
    idx = pd.MultiIndex.from_arrays([var.base_name, var.side])
    have = idx.isin(bases.index)
    var = var[have]
    b = bases.loc[pd.MultiIndex.from_arrays([var.base_name, var.side])]
    for col in ("c_status", "c_conflicts", "c_seconds", "c_clauses", "c_vars", "c_m_reduced",
                "k_status", "k_seconds", "nodes_default"):
        var[f"base_{col}"] = b[col].to_numpy()
    var["both_settled"] = (var.c_status != "unknown") & (var.base_c_status != "unknown")
    var["log_ratio_conflicts"] = _log_ratio(var.c_conflicts, var.base_c_conflicts)
    var["log_ratio_seconds"] = np.log10(var.c_seconds.clip(lower=1e-4) / var.base_c_seconds.clip(lower=1e-4))
    var["log_ratio_clauses"] = np.log10(var.c_clauses / var.base_c_clauses)
    var["log_ratio_nodes"] = _log_ratio(var.nodes_default, var.base_nodes_default)
    kis = (var.k_status != "unknown") & (var.k_status != "skipped") & \
          (var.base_k_status != "unknown") & (var.base_k_status != "skipped")
    var["kissat_settled"] = kis
    var["log_ratio_kissat"] = np.where(kis, np.log10(var.k_seconds.clip(lower=1e-4)
                                                     / var.base_k_seconds.clip(lower=1e-4)), np.nan)
    return var


def _q(s: pd.Series, q: float) -> float:
    return float(s.quantile(q)) if len(s) else float("nan")


def _wilcoxon(diff: pd.Series) -> float:
    from scipy.stats import wilcoxon

    d = diff[diff != 0]
    if len(d) < 10:
        return float("nan")
    return float(wilcoxon(d).pvalue)


def ratio_table(pairs: pd.DataFrame, by: tuple[str, ...] = ("side", "method"),
                column: str = "log_ratio_conflicts", settled: str = "both_settled") -> pd.DataFrame:
    """Paired ratios `variant / base` on the settled pairs: median, spread,
    share equal, share within ±5%, Wilcoxon on the non-zero differences.
    Censored pairs are counted, not dropped silently."""
    rows = []
    for key, d in pairs.groupby(list(by)):
        key = key if isinstance(key, tuple) else (key,)
        s = d[d[settled]]
        lr = s[column].dropna()
        rows.append({**dict(zip(by, key)), "pairs": len(d), "settled": len(s),
                     "variant censored": int((d.c_status == "unknown").sum()),
                     "base censored": int((d.base_c_status == "unknown").sum()),
                     "equal": int((lr == 0).sum()),
                     "within ±5%": float((lr.abs() <= np.log10(1.05)).mean()) if len(lr) else float("nan"),
                     "ratio median": 10 ** _q(lr, 0.5), "p10": 10 ** _q(lr, 0.1), "p90": 10 ** _q(lr, 0.9),
                     "min": 10 ** float(lr.min()) if len(lr) else float("nan"),
                     "max": 10 ** float(lr.max()) if len(lr) else float("nan"),
                     "MAD log10": float((lr - lr.median()).abs().median()) if len(lr) else float("nan"),
                     "Wilcoxon p": _wilcoxon(lr)})
    return pd.DataFrame(rows)


def by_n_table(pairs: pd.DataFrame, column: str = "log_ratio_conflicts") -> pd.DataFrame:
    return ratio_table(pairs, by=("side", "n"), column=column)


def relabel_floor(pairs: pd.DataFrame) -> pd.DataFrame:
    """Within-base spread over relabellings: max/min ratio and MAD of log10
    conflicts, SAT beside the search (§13's floor recomputed on the same rows)."""
    rows = []
    for (side, n), d in pairs.groupby(["side", "n"]):
        s = d[d.both_settled]
        rec = []
        for base, g in s.groupby("base_name"):
            vals = np.log10(1.0 + np.append(g.c_conflicts.to_numpy(float), g.base_c_conflicts.iloc[0]))
            nodes = np.log10(1.0 + np.append(g.nodes_default.to_numpy(float), g.base_nodes_default.iloc[0]))
            rec.append({"spread": vals.max() - vals.min(), "mad": np.median(np.abs(vals - np.median(vals))),
                        "any_change": vals.max() > vals.min(),
                        "spread_nodes": nodes.max() - nodes.min(),
                        "mad_nodes": np.median(np.abs(nodes - np.median(nodes)))})
        r = pd.DataFrame(rec)
        if r.empty:
            continue
        rows.append({"side": side, "n": n, "bases": len(r), "relabellings per base": float(s.groupby("base_name").size().median()),
                     "SAT: bases with any change": int(r.any_change.sum()),
                     "SAT max/min median": 10 ** float(r.spread.median()), "SAT p90": 10 ** float(r.spread.quantile(0.9)),
                     "SAT max": 10 ** float(r.spread.max()), "SAT MAD log10": float(r.mad.mean()),
                     "search max/min median": 10 ** float(r.spread_nodes.median()),
                     "search p90": 10 ** float(r.spread_nodes.quantile(0.9)),
                     "search MAD log10": float(r.mad_nodes.mean())})
    return pd.DataFrame(rows)


def cover_vs_floor(rec_pairs: pd.DataFrame, rel_pairs: pd.DataFrame) -> pd.DataFrame:
    """Is the cover's effect larger than renaming the customers? Per side, the
    median |log10 ratio| over re-coverings against over relabellings, and the
    share of re-covering pairs whose |ratio| exceeds the relabelling p90."""
    rows = []
    for side in ("refute", "witness"):
        a = rec_pairs[(rec_pairs.side == side) & rec_pairs.both_settled].log_ratio_conflicts.abs()
        b = rel_pairs[(rel_pairs.side == side) & rel_pairs.both_settled].log_ratio_conflicts.abs()
        if a.empty or b.empty:
            continue
        p90 = float(b.quantile(0.9))
        rows.append({"side": side, "re-covering pairs": len(a), "relabelling pairs": len(b),
                     "re-covering |ratio| median": 10 ** float(a.median()),
                     "relabelling |ratio| median": 10 ** float(b.median()),
                     "re-covering p90": 10 ** float(a.quantile(0.9)), "relabelling p90": 10 ** p90,
                     "re-coverings beyond relabel p90": float((a > p90).mean())})
    return pd.DataFrame(rows)


def clause_channel(rec_pairs: pd.DataFrame) -> pd.DataFrame:
    """Does the cover reach the conflicts through the formula size? Spearman
    of log conflict ratio against log clause ratio and against the change in
    reduced products, per side and method, on settled pairs. `formula
    unchanged` compares clause *counts*, not clause sets: two covers with the
    same count can still hand the solver different clauses, or the same
    clauses in a different order, so equal counts need not mean equal
    conflicts."""
    from scipy.stats import spearmanr

    rows = []
    for (side, method), d in rec_pairs[rec_pairs.both_settled].groupby(["side", "method"]):
        d = d.dropna(subset=["log_ratio_conflicts", "log_ratio_clauses"])
        if len(d) < 10:
            continue
        dm = (d.c_m_reduced - d.base_c_m_reduced).astype(float)
        rows.append({"side": side, "method": method, "pairs": len(d),
                     "clauses ratio median": 10 ** float(d.log_ratio_clauses.median()),
                     "reduced products change median": float(dm.median()),
                     "formula unchanged": int((d.log_ratio_clauses == 0).sum()),
                     "conflicts equal when formula unchanged": int(((d.log_ratio_clauses == 0) & (d.log_ratio_conflicts == 0)).sum()),
                     "Spearman conflicts~clauses": float(spearmanr(d.log_ratio_conflicts, d.log_ratio_clauses).statistic)
                     if d.log_ratio_clauses.nunique() > 1 else float("nan"),
                     "Spearman conflicts~Δproducts": float(spearmanr(d.log_ratio_conflicts, dm).statistic)
                     if dm.nunique() > 1 else float("nan"),
                     "Spearman seconds~clauses": float(spearmanr(d.log_ratio_seconds, d.log_ratio_clauses).statistic)
                     if d.log_ratio_clauses.nunique() > 1 else float("nan")})
    return pd.DataFrame(rows)


def variance_split(frame: pd.DataFrame, side: str = "refute") -> pd.DataFrame:
    """How much of the variance in log conflicts across (base + re-coverings)
    is within a graph and how much between graphs, per size. If the cover
    barely moves the cost, the within share is small and SAT cannot 'fail on
    different instances' because of the cover."""
    rows = []
    d = frame[(frame.side == side) & frame.kind.isin(["base", "recover"]) & (frame.c_status != "unknown")]
    for n, g in d.groupby("n"):
        y = np.log10(1.0 + g.c_conflicts.astype(float))
        groups = g.base_name
        grand = y.var(ddof=0)
        within = y.groupby(groups).var(ddof=0).mul(groups.value_counts(sort=False).reindex(y.groupby(groups).var().index)).sum() / len(y)
        rows.append({"n": n, "instances": len(g), "graphs": groups.nunique(), "var log10 conflicts": float(grand),
                     "within-graph share": float(within / grand) if grand > 0 else float("nan"),
                     "between-graph share": float(1 - within / grand) if grand > 0 else float("nan")})
    return pd.DataFrame(rows)


def search_vs_sat(frame: pd.DataFrame) -> pd.DataFrame:
    """Do the two procedures find the same instances hard? Spearman between
    the search's nodes and SAT's conflicts on the refutation, over bases, by
    size and overall; censored SAT calls excluded and counted."""
    from scipy.stats import spearmanr

    d = frame[(frame.kind == "base") & (frame.side == "refute")]
    rows = []
    for label, g in [("all", d)] + [(str(n), gg) for n, gg in d.groupby("n")]:
        s = g[g.c_status != "unknown"]
        rows.append({"n": label, "bases": len(g), "SAT censored": int((g.c_status == "unknown").sum()),
                     "Spearman nodes~conflicts": float(spearmanr(np.log10(1 + s.nodes_default), np.log10(1 + s.c_conflicts)).statistic)
                     if len(s) > 5 and s.nodes_default.nunique() > 1 else float("nan"),
                     "Spearman nodes~seconds": float(spearmanr(np.log10(1 + s.nodes_default), np.log10(s.c_seconds.clip(lower=1e-4))).statistic)
                     if len(s) > 5 and s.nodes_default.nunique() > 1 else float("nan"),
                     "Spearman conflicts~clauses": float(spearmanr(np.log10(s.c_clauses), np.log10(1 + s.c_conflicts)).statistic)
                     if len(s) > 5 and s.c_clauses.nunique() > 1 else float("nan"),
                     "Spearman nodes~clauses": float(spearmanr(np.log10(s.c_clauses), np.log10(1 + s.nodes_default)).statistic)
                     if len(s) > 5 and s.c_clauses.nunique() > 1 else float("nan"),
                     "conflicts median": float(s.c_conflicts.median()) if len(s) else float("nan"),
                     "nodes median": float(s.nodes_default.median()) if len(s) else float("nan")})
    return pd.DataFrame(rows)


def kill_test(frame: pd.DataFrame, rec: pd.DataFrame, results: pd.DataFrame, side: str = "refute",
              folds: int = 5, seed: int = 0, extra_sets: bool = True) -> pd.DataFrame:
    """Predict `log10(1 + conflicts)` on the settled calls of one side from
    §13's three feature sets (graph-only, matrix-only, full), grouped by graph
    class; plus a `formula` set (products after dominance, variables, clauses)
    and `graph+formula`, to show which matrix quantity carries what the graph
    does not."""
    from sklearn.model_selection import GroupKFold

    from learning.graph_story import _model

    d = frame[(frame.side == side) & frame.kind.isin(["base", "recover"]) & (frame.c_status != "unknown")].copy()
    feats = pd.concat([results.set_index("instance_name"), rec.set_index("instance_name")])
    feats = feats[~feats.index.duplicated()]
    d = d.join(feats, on="instance_name", rsuffix="_f")
    d = d.dropna(subset=["graph_cert"])
    d = d.drop_duplicates("matrix_digest")
    sets = feature_sets(True)
    formula = ["c_m_reduced", "c_vars", "c_clauses", "c_components"]
    if extra_sets:
        sets["formula"] = formula + ["optimum", "n_customers"]
        sets["graph+formula"] = sets["graph-only"] + formula
    y = np.log10(1.0 + d.c_conflicts.astype(float)).to_numpy()
    groups = d.graph_cert.to_numpy()
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(d))
    pred = {name: np.zeros(len(d)) for name in sets}
    for train, test in GroupKFold(n_splits=folds).split(order, groups=groups[order]):
        tr, te = order[train], order[test]
        for name, cols in sets.items():
            model = _model()
            model.fit(d.iloc[tr][cols].to_numpy(dtype=float), y[tr])
            pred[name][te] = model.predict(d.iloc[te][cols].to_numpy(dtype=float))
    baseline = np.full(len(d), np.nan)
    for _, idx in d.groupby("n").indices.items():
        baseline[idx] = np.median(y[idx])
    rows = []
    for name in list(sets) + ["size-median baseline"]:
        p = baseline if name.startswith("size") else pred[name]
        err = p - y
        ss = np.sum((y - y.mean()) ** 2)
        rows.append({"features": name, "n_features": 0 if name.startswith("size") else len(sets[name]),
                     "rows": len(d), "MAE log10": float(np.abs(err).mean()),
                     "RMSE log10": float(np.sqrt((err ** 2).mean())),
                     "R2": float(1 - np.sum(err ** 2) / ss) if ss > 0 else float("nan"),
                     "within 2x": float((np.abs(err) <= np.log10(2)).mean())})
    return pd.DataFrame(rows)


def kill_verdict(rec_table: pd.DataFrame) -> dict:
    """The plan's kill: paired median re-covering ratio within ±5%, read per
    side over all methods."""
    out = {}
    for side in ("refute", "witness"):
        t = rec_table[(rec_table.side == side) & (rec_table.method == "all")]
        if t.empty:
            continue
        med = float(t["ratio median"].iloc[0])
        out[side] = {"median ratio": med, "within ±5%": abs(np.log10(med)) <= np.log10(1 + KILL_TOLERANCE),
                     "MAD log10": float(t["MAD log10"].iloc[0]), "settled": int(t.settled.iloc[0])}
    return out


def agreement(frame: pd.DataFrame) -> pd.DataFrame:
    """Every settled SAT answer against the certified value: `unsat` at
    `optimum - 1`, `sat` at `optimum`. Any disagreement is a soundness finding."""
    rows = []
    for (side, prefix), d in [((s, p), frame[frame.side == s]) for s in ("refute", "witness") for p in ("c", "k")]:
        st = d[f"{prefix}_status"]
        settled = d[~st.isin(["unknown", "skipped"])]
        rows.append({"side": side, "backend": CONFLICT_BACKEND if prefix == "c" else "kissat404",
                     "calls": len(d), "settled": len(settled), "censored": int((st == "unknown").sum()),
                     "skipped": int((st == "skipped").sum()),
                     "agree with certified value": int((settled[f"{prefix}_agrees"] == True).sum()),   # noqa: E712 - object column
                     "disagree": int((settled[f"{prefix}_agrees"] == False).sum())})                    # noqa: E712
    return pd.DataFrame(rows)


def write_tables(frame: pd.DataFrame, out: Path = TABLES, ml: bool = True, seconds: float | None = None) -> dict:
    rec, _rel = load_pairs()
    results = pd.read_csv(RESULTS_CSV)
    rec_pairs = paired(frame, "recover")
    rel_pairs = paired(frame, "relabel")
    summary: dict = {}
    summary["agreement"] = agreement(frame)
    summary["calls"] = frame.groupby(["n", "kind"]).size().unstack(fill_value=0).reset_index()
    t_all = ratio_table(rec_pairs.assign(method="all"))
    summary["recover"] = pd.concat([ratio_table(rec_pairs), t_all]).reset_index(drop=True)
    summary["recover_by_n"] = by_n_table(rec_pairs)
    summary["recover_method_by_n"] = ratio_table(rec_pairs[rec_pairs.side == "refute"], by=("method", "n"))
    summary["recover_seconds"] = pd.concat([ratio_table(rec_pairs, column="log_ratio_seconds"),
                                            ratio_table(rec_pairs.assign(method="all"), column="log_ratio_seconds")]).reset_index(drop=True)
    summary["recover_kissat"] = pd.concat([ratio_table(rec_pairs, column="log_ratio_kissat", settled="kissat_settled"),
                                           ratio_table(rec_pairs.assign(method="all"), column="log_ratio_kissat", settled="kissat_settled")]).reset_index(drop=True)
    summary["recover_nodes"] = ratio_table(rec_pairs.assign(method="all"), column="log_ratio_nodes")
    summary["relabel"] = pd.concat([ratio_table(rel_pairs), ratio_table(rel_pairs, column="log_ratio_kissat", settled="kissat_settled").assign(method="relabel (kissat s)")]).reset_index(drop=True)
    summary["relabel_floor"] = relabel_floor(rel_pairs)
    summary["cover_vs_floor"] = cover_vs_floor(rec_pairs, rel_pairs)
    summary["clause_channel"] = clause_channel(rec_pairs)
    summary["variance"] = variance_split(frame)
    summary["search_vs_sat"] = search_vs_sat(frame)
    summary["kill"] = kill_verdict(summary["recover"])
    if ml:
        try:
            summary["ml_refute"] = kill_test(frame, rec, results, side="refute")
            summary["ml_witness"] = kill_test(frame, rec, results, side="witness")
        except Exception as exc:  # pragma: no cover - reported, not fatal
            summary["ml_error"] = str(exc)

    lines = ["# SAT and the clique cover: tables (`learning.sat_story`)", "",
             f"*Generated {time.strftime('%Y-%m-%d %H:%M')} from `{SAT_CSV}`; {len(frame)} SAT calls"
             + (f"; {seconds:.0f} s.*" if seconds else ".*"), "",
             f"Conflicts on `{CONFLICT_BACKEND}` (conflict-budget chunks of {CHUNK} against the wall deadline); "
             "seconds on `kissat404` in a hard-killed child on the calls CaDiCaL settled within the cap. "
             "Ratios are variant / base on pairs where both calls settled; censored calls are counted in the tables.", ""]
    titles = {"agreement": "Answers against the certified value", "calls": "Calls on disk by size and kind",
              "recover": "Re-coverings: paired conflict ratios", "recover_by_n": "Re-coverings by size: paired conflict ratios",
              "recover_method_by_n": "Re-coverings by method and size: paired conflict ratios on the refutation",
              "recover_seconds": "Re-coverings: paired CaDiCaL seconds ratios",
              "recover_kissat": "Re-coverings: paired Kissat seconds ratios",
              "recover_nodes": "Re-coverings: the search's paired node ratio on the same pairs (§13)",
              "relabel": "Relabellings: paired ratios against the base", "relabel_floor": "Relabellings: the label floor, SAT beside the search",
              "cover_vs_floor": "Cover effect against the label floor", "clause_channel": "The channel: formula size",
              "variance": "Variance of log conflicts within and between graphs (refutation)",
              "search_vs_sat": "Do the search and SAT find the same bases hard?",
              "ml_refute": "Kill test: predicting refutation conflicts (grouped by graph class)",
              "ml_witness": "Kill test: predicting witness conflicts (grouped by graph class)"}
    for key, title in titles.items():
        if key in summary and isinstance(summary[key], pd.DataFrame) and not summary[key].empty:
            lines += [f"## {title}", "", _md(summary[key]), ""]
    lines += ["## Kill verdict", "", f"```\n{summary['kill']}\n```", ""]
    if "ml_error" in summary:
        lines += [f"ML step failed: {summary['ml_error']}", ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("all", "run", "tables"), default="all")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--per-n", type=int, default=40, help="bases per size, from §13's 200")
    ap.add_argument("--per-method", type=int, default=1)
    ap.add_argument("--relabellings", type=int, default=4)
    ap.add_argument("--sizes", type=int, nargs="*", default=list(BASE_SIZES))
    ap.add_argument("--deadline", type=float, default=120.0, help="wall seconds per SAT call")
    ap.add_argument("--wall", type=float, default=None, help="stop handing out calls after this many seconds")
    ap.add_argument("--kissat-cap", type=float, default=30.0,
                    help="time kissat only where CaDiCaL settled within this many seconds; negative to skip kissat")
    ap.add_argument("--csv", type=Path, default=SAT_CSV)
    ap.add_argument("--no-ml", action="store_true")
    ap.add_argument("--out", type=Path, default=TABLES)
    args = ap.parse_args()

    started = time.time()
    if args.stage in ("all", "run"):
        rec, rel = load_pairs()
        jobs = select_jobs(rec, rel, args.per_n, args.per_method, args.relabellings, tuple(args.sizes))
        frame = run(jobs, args.workers, args.deadline, args.wall,
                    kissat_cap=None if args.kissat_cap < 0 else args.kissat_cap, csv=args.csv)
    else:
        frame = pd.read_csv(args.csv)
    summary = write_tables(frame, args.out, ml=not args.no_ml, seconds=time.time() - started)
    for key in ("agreement", "recover", "recover_by_n", "relabel_floor", "cover_vs_floor", "clause_channel",
                "variance", "search_vs_sat", "ml_refute"):
        if key in summary and not summary[key].empty:
            print(f"\n## {key}\n{_md(summary[key])}")
    print("\nkill:", summary["kill"])
    print(f"\nwrote {args.out}; {time.time() - started:.0f} s total")


if __name__ == "__main__":
    main()
