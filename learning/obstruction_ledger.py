"""loop0013 item 01: the baseline ledger and the frozen targets.

Every lower bound already on record against the certified optimum, for every
corpus instance, and the cheap floors against the proved width for every
certified class of the pathwidth dataset; then the target sets every later
item of the loop reads (`targets.json`), frozen once. Nothing here solves an
instance: the only new computation is Harper's expansion bound at cap 12
under a 60 s budget per instance (`satisfiability.expansion_bound`), which is
family E's floor on record, and the cheap floors (degeneracy, MMD+ under both
rules, the largest clique found in 2 s) on the dataset classes.

**Units.** Corpus bounds are in optimum units (`pathwidth + 1`); "gap" is
`optimum - bound`. The dataset's `width` is a pathwidth and its floors are in
pathwidth units (`degeneracy <= pw`, `MMD+ <= tw <= pw`, `omega - 1 <= pw`); a
gap is the same number in either unit.

**What is read** (all on record; see `reports/obstruction_search_plan.md` §0.3):
`learning/data/instances.csv` (`optimum`, `lb_trivial`, `lb_contraction`,
`lb_best`, `tw_min_fill`, `ub_best`, sizes), the invariants table
`learning/data/ensemble/conjecture_invariants.csv.gz` (`omega`, `contraction`,
`exp`, `exp_cap`, `tw_lo`, `tw_hi`, `tw_exact`), Lemma P from loop0010 item 13
(`reports/scratch/pendant_cliques/harness_values.csv`, column `pendant`), the
contraction-minor certificates on record (`reports/scratch/minor_certificates/*.json`,
claims in pathwidth units; `reports/scratch/minor_bound/*_recorded_certificate.json`,
`refuted` in MOSP units), the provenance of every `solutions/` file (read
only), the dataset `paper1/data/dataset/pathwidth_dataset.jsonl.gz`, and the
open classes of `reports/scratch/dataset_open/`.

**The guard.** A bound on record above a certified optimum, or a dataset floor
above a certified width, is the most important finding the loop could make:
`build_corpus` / `build_dataset` write `VIOLATION.md` beside the ledger and
raise, and `tests/test_obstruction_ledger.py` asserts the same on the files.

    nice -n 19 python3 -m learning.obstruction_ledger --stage corpus --workers 8
    nice -n 19 python3 -m learning.obstruction_ledger --stage dataset --workers 8
    nice -n 19 python3 -m learning.obstruction_ledger --stage targets
    nice -n 19 python3 -m learning.obstruction_ledger --stage tables
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "scratch" / "obstruction_search" / "01_ledger"
INSTANCES_CSV = ROOT / "learning" / "data" / "instances.csv"
INVARIANTS_CSV = ROOT / "learning" / "data" / "ensemble" / "conjecture_invariants.csv.gz"
PENDANT_CSV = ROOT / "reports" / "scratch" / "pendant_cliques" / "harness_values.csv"
MINOR_CERT_DIR = ROOT / "reports" / "scratch" / "minor_certificates"
MINOR_BOUND_DIR = ROOT / "reports" / "scratch" / "minor_bound"
SOLUTIONS_DIR = ROOT / "solutions"
DATASET = ROOT / "paper1" / "data" / "dataset" / "pathwidth_dataset.jsonl.gz"
OPEN_CSV = ROOT / "reports" / "scratch" / "dataset_open" / "unsolved_unlimited.csv"
OPEN_FLOOR_CSVS = (ROOT / "reports" / "scratch" / "dataset_open" / "results_quick.csv",
                   ROOT / "reports" / "scratch" / "dataset_open" / "results_quick_rescued.csv",
                   ROOT / "reports" / "scratch" / "dataset_open" / "results.csv")

LEDGER_CORPUS = OUT / "ledger_corpus.csv"
HARPER_CSV = OUT / "harper12.csv"
LEDGER_DATASET = OUT / "ledger_dataset.csv.gz"
TARGETS_JSON = OUT / "targets.json"
TABLES_MD = OUT / "tables.md"
RUN_LOG = OUT / "run.log"
VIOLATION_MD = OUT / "VIOLATION.md"

# The harness's seven size bands (`learning.bound_harness.BANDS`), copied so that
# this module does not import networkx at load; the test pins the two equal.
BANDS = ((9, 20), (21, 30), (31, 40), (41, 60), (61, 75), (76, 100), (101, 134))
HARPER_CAP = 12
HARPER_BUDGET = 60.0
SMALL_N = 22
REST_SIZE = 500
REST_SEED = 0
DATASET_MAX_COMPONENT = 1024
CLIQUE_BUDGET = 2.0
CLIQUE_CAP = 200_000

# The two values the survey's §5 table reports with no certificate file on record
# (`reports/pathwidth_lower_bounds_survey.md` §5; logged in
# `reports/scratch/pw_lower_bounds/corpus_minor.out` and `corpus_minor_hi.out`).
# Optimum units. Listed beside `floor0`, never inside it.
MINOR_SURVEY_ONLY = {"Random-125-125-4-1_0": 54, "Random-125-125-8-2_0": 92}

# Every bound column of the corpus ledger, in optimum units, with the theorem or
# record it rests on (for the report).
CORPUS_BOUNDS = (
    ("lb_trivial", "max customers on one pattern (a clique): card_le_pathwidth_add_one_of_isClique"),
    ("lb_contraction", "contraction degeneracy + 1 (MMD+, least-c): minDegreeIn_le_degeneracy, degeneracy_le_pathwidth"),
    ("lb_best", "the solver's floor: best of trivial, clique, contraction degeneracy + 1"),
    ("omega", "clique number: card_le_pathwidth_add_one_of_isClique"),
    ("exp_rec", "Harper at the recorded cap (invariants table): exists_closedNbhd_card_le"),
    ("harper12", "Harper at cap 12, 60 s (this item): exists_closedNbhd_card_le"),
    ("tw1", "treewidth + 1 (exact or its proved lower end): treewidth_le_pathwidth"),
    ("lemmaP", "Lemma P, pendant cliques (loop0010 item 13): pathwidth_ge_of_pendant_cliques"),
    ("minor", "contraction-minor certificate on record: pathwidth_gt_of_minorOf, lt_mospValue_of_minorOf"),
)
FLOOR0_PARTS = ("lb_best", "tw1", "harper12", "lemmaP", "minor")

_CS_NAME = re.compile(r"^Random-(\d+)-(\d+)-(\d+)-(\d+)_0$")


def log(msg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(RUN_LOG, "a") as handle:
        handle.write(line + "\n")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------
# graphs as bit masks
# ----------------------------------------------------------------------------


def adjacency_from_edges(n: int, edges) -> list[int]:
    """Open neighbourhoods as bit masks (loops and repeats ignored)."""
    adj = [0] * n
    for u, v in edges:
        if u == v:
            continue
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def adjacency_from_matrix(matrix: np.ndarray) -> list[int]:
    """The MOSP graph of a 0/1 matrix (rows customers): a clique per pattern."""
    matrix = np.asarray(matrix)
    n = matrix.shape[0]
    adj = [0] * n
    for col in range(matrix.shape[1]):
        holders = np.flatnonzero(matrix[:, col])
        together = 0
        for c in holders:
            together |= 1 << int(c)
        for c in holders:
            adj[int(c)] |= together & ~(1 << int(c))
    return adj


def components(adj: list[int], alive: int | None = None) -> list[int]:
    """Connected components of the vertices in `alive` (default all), as masks."""
    n = len(adj)
    if alive is None:
        alive = (1 << n) - 1
    out = []
    while alive:
        start = alive & -alive
        comp, frontier = start, start
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            nb = adj[bit.bit_length() - 1] & alive & ~comp
            comp |= nb
            frontier |= nb
        out.append(comp)
        alive &= ~comp
    return out


def degeneracy(adj: list[int], alive: int | None = None) -> int:
    """`max_H delta(H)`: repeatedly delete a minimum-degree vertex."""
    n = len(adj)
    if alive is None:
        alive = (1 << n) - 1
    best = 0
    while alive:
        best_v, best_d = -1, n + 1
        bits = alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            d = (adj[bit.bit_length() - 1] & alive).bit_count()
            if d < best_d:
                best_d, best_v = d, bit.bit_length() - 1
        if best_d > best:
            best = best_d
        alive &= ~(1 << best_v)
    return best


def mmd_plus(adj: list[int], rule: str, alive: int | None = None) -> int:
    """Contraction degeneracy (MMD+): record the minimum degree, contract that
    vertex into a neighbour chosen by `rule` -- `least-c`, the neighbour
    sharing fewest neighbours with it (ties by index), or `min-d`, the
    neighbour of least degree (ties by index) -- and repeat. The largest
    minimum degree seen is a lower bound on treewidth, hence on pathwidth."""
    if rule not in ("least-c", "min-d"):
        raise ValueError(rule)
    n = len(adj)
    adj = list(adj)
    if alive is None:
        alive = (1 << n) - 1
    best = 0
    while alive.bit_count() > 1:
        best_v, best_d = -1, n + 1
        bits = alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            v = bit.bit_length() - 1
            d = (adj[v] & alive).bit_count()
            if d < best_d:
                best_d, best_v = d, v
        if best_d > best:
            best = best_d
        v = best_v
        nbrs = adj[v] & alive
        if not nbrs:
            alive &= ~(1 << v)
            continue
        u, score = -1, n + 1
        bits = nbrs
        while bits:
            bit = bits & -bits
            bits ^= bit
            c = bit.bit_length() - 1
            s = (adj[c] & nbrs).bit_count() if rule == "least-c" else (adj[c] & alive).bit_count()
            if s < score:
                score, u = s, c
        merged = (adj[u] | adj[v]) & ~((1 << u) | (1 << v))
        adj[u] = merged
        bits = merged & alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            w = bit.bit_length() - 1
            adj[w] = (adj[w] | (1 << u)) & ~(1 << v)
        alive &= ~(1 << v)
    return best


def clique_number_budget(adj: list[int], seconds: float = CLIQUE_BUDGET,
                         cap: int = CLIQUE_CAP) -> tuple[int, bool]:
    """The largest maximal clique `networkx.find_cliques` enumerates within
    `seconds` and `cap` cliques: `(size, censored)`. Censored means a subset of
    the maximal cliques was seen, so the size is a floor on omega (still a
    valid lower bound on `pw + 1`), not omega itself."""
    import networkx as nx

    n = len(adj)
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for v in range(n):
        bits = adj[v]
        while bits:
            bit = bits & -bits
            bits ^= bit
            u = bit.bit_length() - 1
            if u > v:
                graph.add_edge(v, u)
    deadline = time.monotonic() + seconds
    best, seen, censored = 1 if n else 0, 0, False
    for clique in itertools.islice(nx.find_cliques(graph), cap + 1):
        seen += 1
        if seen > cap:
            censored = True
            break
        if len(clique) > best:
            best = len(clique)
        if not seen & 0x3FF and time.monotonic() > deadline:
            censored = True
            break
    return best, censored


def excess(n: float, m: float, n_ones: float) -> float:
    """`e = (n_ones - m) / n` (`learning.excess.excess`)."""
    return (n_ones - m) / n


def band_label(n: int) -> str:
    for lo, hi in BANDS:
        if lo <= n <= hi:
            return f"{lo}–{hi}"
    return "?"


# ----------------------------------------------------------------------------
# (a) corpus: the record
# ----------------------------------------------------------------------------


def chu_stuckey_class(name: str) -> tuple[int, int, int] | None:
    m = _CS_NAME.match(name)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def minor_floors_on_record(name: str) -> tuple[float, str]:
    """The best contraction-minor floor on record for a corpus instance, in
    optimum units, with the file it comes from. `reports/scratch/minor_certificates/<name>_m*.json`
    claims `pw(G) >= K` (pathwidth units, floor `K + 1`);
    `reports/scratch/minor_bound/<name>_*_recorded_certificate.json` records
    `refuted` in MOSP units (floor `refuted + 1`). `(nan, "")` where none."""
    best, source = float("nan"), ""
    for path in sorted(MINOR_CERT_DIR.glob(f"{name}_m*.json")):
        if path.name.endswith("_edges.json"):
            continue
        rec = json.loads(path.read_text())
        claim = rec.get("claim") or ""
        m = re.search(r"pw\(G\) >= (\d+)", claim)
        if not m:
            continue
        value = int(m.group(1)) + 1
        if not value <= best:
            best, source = value, str(path.relative_to(ROOT))
    for path in sorted(MINOR_BOUND_DIR.glob(f"{name}_*_recorded_certificate.json")):
        rec = json.loads(path.read_text())
        if "refuted" not in rec:
            continue
        value = int(rec["refuted"]) + 1
        if not value <= best:
            best, source = value, str(path.relative_to(ROOT))
    return best, source


def minor_certificate_files() -> dict[str, tuple[float, str]]:
    names = set()
    for path in MINOR_CERT_DIR.glob("*_m*.json"):
        names.add(re.sub(r"_m\d+.*$", "", path.name))
    for path in MINOR_BOUND_DIR.glob("*_recorded_certificate.json"):
        names.add(re.sub(r"_(default|large|off)_recorded_certificate\.json$", "", path.name))
    return {n: minor_floors_on_record(n) for n in sorted(names)}


def corpus_instances() -> dict[str, tuple[Path, object]]:
    from learning.dataset import enumerate_instances

    found: dict[str, tuple[Path, object]] = {}
    for path, inst in enumerate_instances():
        found.setdefault(inst.name, (path, inst))
    return found


def read_record() -> pd.DataFrame:
    """`instances.csv` joined with the invariants, Lemma P, the minor
    certificates and the provenance in `solutions/`; no computation."""
    from satisfiability.mosp_solver import _solution_path
    from learning.excess import collection_of

    if not INSTANCES_CSV.exists():
        raise SystemExit(f"{INSTANCES_CSV} is missing: python -m learning.dataset --workers 8")
    d = pd.read_csv(INSTANCES_CSV)
    inv = pd.read_csv(INVARIANTS_CSV)
    inv = inv[inv["source"] == "corpus"][["instance_name", "omega", "contraction", "exp", "exp_cap",
                                           "tw_lo", "tw_hi", "tw_exact", "tw_method", "edges"]]
    inv = inv.rename(columns={"exp": "exp_rec", "exp_cap": "exp_rec_cap", "edges": "g_edges_inv"})
    f = d.merge(inv, on="instance_name", how="left", validate="one_to_one")
    pend = pd.read_csv(PENDANT_CSV)
    pend = pend[pend["source"] == "corpus"][["instance_name", "pendant", "pendant_censored_eval"]]
    pend = pend.rename(columns={"pendant": "lemmaP", "pendant_censored_eval": "lemmaP_censored"})
    f = f.merge(pend, on="instance_name", how="left", validate="one_to_one")
    f = f.rename(columns={"n_customers": "n", "n_patterns": "m"})
    for c in ("n", "m", "n_ones", "optimum", "lb_trivial", "lb_contraction", "lb_best", "ub_best",
              "omega", "contraction", "exp_rec", "exp_rec_cap", "tw_lo", "tw_hi"):
        f[c] = f[c].astype(int)
    f["tw_exact"] = f["tw_exact"].astype(str).str.lower().eq("true")
    f["tw1"] = f["tw_lo"] + 1
    f["tw1_exact"] = np.where(f["tw_exact"], f["tw1"], np.nan)
    f["tw_min_fill1"] = f["tw_min_fill"].astype(int) + 1
    f["excess"] = excess(f["n"], f["m"], f["n_ones"])
    f["band"] = f["n"].map(band_label)
    coll = [collection_of(s, nm) for s, nm in zip(f["source_file"], f["instance_name"])]
    f["collection"] = [c for c, _ in coll]
    f["cls"] = [k for _, k in coll]
    cs = f["instance_name"].map(chu_stuckey_class)
    f["cs_n"] = [c[0] if c else np.nan for c in cs]
    f["cs_m"] = [c[1] if c else np.nan for c in cs]
    f["cs_d"] = [c[2] if c else np.nan for c in cs]
    # provenance and value from the solution files themselves (instances.csv lags them)
    inst = corpus_instances()
    prov, val = [], []
    for name in f["instance_name"]:
        path = _solution_path(inst[name][1], SOLUTIONS_DIR)
        rec = json.loads(path.read_text())
        prov.append(rec.get("provenance", ""))
        val.append(int(rec["mosp_value"]))
    f["provenance_file"] = prov
    f["optimum_file"] = val
    minors = minor_certificate_files()
    f["minor"] = [minors.get(nm, (np.nan, ""))[0] for nm in f["instance_name"]]
    f["minor_source"] = [minors.get(nm, (np.nan, ""))[1] for nm in f["instance_name"]]
    f["minor_survey"] = f["instance_name"].map(MINOR_SURVEY_ONLY)
    return f


# ----------------------------------------------------------------------------
# (a) corpus: Harper at cap 12
# ----------------------------------------------------------------------------


def _harper_job(args) -> dict:
    name, matrix, cap, budget = args
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound

    inst = MOSPInstance.from_matrix(np.asarray(matrix, dtype=int), name=name)
    t0 = time.monotonic()
    b = expansion_bound(inst, max_t=cap, time_budget=budget)
    return {"instance_name": name, "harper12": int(b.value), "harper12_cap": int(b.cap),
            "harper12_complete": bool(b.complete), "harper12_seconds": round(time.monotonic() - t0, 3),
            "harper12_levels": ",".join(str(x) for x in b.levels)}


def run_harper(frame: pd.DataFrame, workers: int, wall: float | None, cap: int = HARPER_CAP,
               budget: float = HARPER_BUDGET, out_csv: Path = HARPER_CSV) -> pd.DataFrame:
    """Harper's bound at cap `cap` under `budget` seconds per instance, every
    instance in `frame`, cheapest sizes first, appended to `out_csv` as they
    finish so a rerun resumes. `wall` seconds stops dispatching; the instances
    not reached are left out (the ledger says so)."""
    done = pd.read_csv(out_csv) if out_csv.exists() else pd.DataFrame(columns=["instance_name"])
    have = set(done["instance_name"])
    inst = corpus_instances()
    todo = frame[~frame["instance_name"].isin(have)].sort_values(["n", "m"])
    jobs = [(nm, inst[nm][1].matrix.tolist(), cap, budget) for nm in todo["instance_name"]]
    log(f"harper: {len(jobs)} instances to run, {len(have)} on file; cap {cap}, budget {budget} s, "
        f"{workers} workers, wall {wall}")
    t0 = time.monotonic()
    rows, stopped = [], False
    if jobs:
        with Pool(workers) as pool:
            it = pool.imap_unordered(_harper_job, jobs, chunksize=1)
            for k, row in enumerate(it, 1):
                rows.append(row)
                if k % 200 == 0 or k == len(jobs):
                    part = pd.DataFrame(rows)
                    part.to_csv(out_csv, mode="a", header=not out_csv.exists(), index=False)
                    rows = []
                    log(f"harper: {k}/{len(jobs)} done, {time.monotonic() - t0:.0f} s wall")
                if wall is not None and time.monotonic() - t0 > wall:
                    stopped = True
                    log("harper: wall reached; stopping (unfinished instances are not in the file)")
                    pool.terminate()
                    break
        if rows:
            pd.DataFrame(rows).to_csv(out_csv, mode="a", header=not out_csv.exists(), index=False)
    out = pd.read_csv(out_csv).drop_duplicates("instance_name", keep="last")
    out.attrs["stopped"] = stopped
    return out


def attach_floor0(f: pd.DataFrame) -> pd.DataFrame:
    """Gaps per bound and `floor0 = max(lb_best, tw1, harper12, lemmaP, minor)`
    with the bounds attaining it."""
    for col, _ in CORPUS_BOUNDS:
        f[f"gap_{col}"] = f["optimum"] - f[col]
    parts = f[list(FLOOR0_PARTS)].astype(float)
    f["floor0"] = parts.max(axis=1)
    f["floor0_source"] = ["|".join(c for c in FLOOR0_PARTS if row[c] == row["floor0"])
                          for _, row in f[list(FLOOR0_PARTS) + ["floor0"]].iterrows()]
    f["floor0"] = f["floor0"].astype(int)
    f["gap_floor0"] = f["optimum"] - f["floor0"]
    f["gap_lb_best"] = f["optimum"] - f["lb_best"]
    f["is_gap338"] = f["gap_lb_best"] >= 2
    f["is_cs200"] = f["collection"] == "Chu & Stuckey"
    f["is_small"] = f["n"] <= SMALL_N
    return f


def violations(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, _ in CORPUS_BOUNDS:
        bad = f[f[col].notna() & (f[col] > f["optimum"])]
        for _, r in bad.iterrows():
            rows.append({"instance_name": r["instance_name"], "bound": col, "value": r[col], "optimum": r["optimum"]})
    bad = f[f["optimum_file"] != f["optimum"]]
    for _, r in bad.iterrows():
        rows.append({"instance_name": r["instance_name"], "bound": "optimum(instances.csv) != solutions/",
                     "value": r["optimum"], "optimum": r["optimum_file"]})
    return pd.DataFrame(rows, columns=["instance_name", "bound", "value", "optimum"])


def _stop_on_violation(bad: pd.DataFrame, what: str) -> None:
    if bad.empty:
        return
    text = (f"# VIOLATION ({what})\n\nA bound on record sits above a certified value. Item 01 stopped here;"
            f" see TASK.md's kill guard.\n\n{bad.to_markdown(index=False)}\n")
    VIOLATION_MD.write_text(text)
    log(f"VIOLATION: {len(bad)} rows ({what}); written to {VIOLATION_MD}")
    raise SystemExit(2)


def build_corpus(workers: int, wall: float | None, harper: bool = True) -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    log(f"corpus stage: reading the record ({INSTANCES_CSV.relative_to(ROOT)}, invariants, Lemma P, minors, solutions/)")
    f = read_record()
    log(f"corpus stage: {len(f)} instances; provenance in solutions/: {f['provenance_file'].value_counts().to_dict()}")
    if harper:
        h = run_harper(f, workers, wall)
        f = f.merge(h, on="instance_name", how="left", validate="one_to_one")
    else:
        for c in ("harper12", "harper12_cap", "harper12_seconds"):
            f[c] = np.nan
        f["harper12_complete"] = np.nan
        f["harper12_levels"] = ""
    f = attach_floor0(f)
    bad = violations(f)
    f.to_csv(LEDGER_CORPUS, index=False)
    log(f"corpus stage: wrote {LEDGER_CORPUS.relative_to(ROOT)} ({len(f)} rows, sha256 {sha256_of(LEDGER_CORPUS)[:16]})")
    _stop_on_violation(bad, "corpus")
    log("corpus stage: guard passed: no bound on record above a certified optimum")
    return f


# ----------------------------------------------------------------------------
# (b) dataset
# ----------------------------------------------------------------------------


def dataset_records(certified_only: bool = True):
    with gzip.open(DATASET, "rt") as handle:
        for line in handle:
            rec = json.loads(line)
            if certified_only and not str(rec.get("provenance", "")).startswith("certified"):
                continue
            yield rec


def dataset_floors(n: int, edges, max_component: int = DATASET_MAX_COMPONENT,
                   clique_seconds: float = CLIQUE_BUDGET) -> dict:
    """Degeneracy, MMD+ (both rules) and the largest clique found, per
    component, maxed over the components at most `max_component` vertices;
    `skipped_components` counts the larger ones (their floors are not
    computed, so the row's floors are over a subgraph: still valid)."""
    adj = adjacency_from_edges(n, edges)
    comps = components(adj)
    out = {"n_components": len(comps), "largest_component": max((c.bit_count() for c in comps), default=0),
           "skipped_components": 0, "degeneracy": 0, "mmd_leastc": 0, "mmd_mind": 0, "omega": 1 if n else 0,
           "omega_censored": False}
    t0 = time.monotonic()
    for comp in comps:
        size = comp.bit_count()
        if size > max_component:
            out["skipped_components"] += 1
            continue
        if size == 1:
            continue
        out["degeneracy"] = max(out["degeneracy"], degeneracy(adj, comp))
        out["mmd_leastc"] = max(out["mmd_leastc"], mmd_plus(adj, "least-c", comp))
        out["mmd_mind"] = max(out["mmd_mind"], mmd_plus(adj, "min-d", comp))
    if n and out["skipped_components"] == 0 and n <= max_component:
        omega, censored = clique_number_budget(adj, clique_seconds)
        out["omega"], out["omega_censored"] = omega, censored
    elif n:
        # per component, under the same total budget
        deadline = time.monotonic() + clique_seconds
        for comp in comps:
            if comp.bit_count() > max_component or comp.bit_count() < 2:
                continue
            verts = [v for v in range(n) if comp >> v & 1]
            index = {v: i for i, v in enumerate(verts)}
            sub = [[index[u], index[v]] for u, v in edges if comp >> u & 1 and comp >> v & 1]
            omega, censored = clique_number_budget(adjacency_from_edges(len(verts), sub),
                                                   max(0.05, deadline - time.monotonic()))
            out["omega"] = max(out["omega"], omega)
            out["omega_censored"] = out["omega_censored"] or censored
    out["seconds"] = round(time.monotonic() - t0, 3)
    return out


def _dataset_job(rec: dict) -> dict:
    n, edges, width = int(rec["n"]), rec["edges"], int(rec["width"])
    row = {"id": rec["id"], "n": n, "m": int(rec["m"]), "width": width, "provenance": rec["provenance"],
           "collection": (rec.get("members") or [{}])[0].get("collection", ""),
           "edges_present": len(edges) > 0}
    row.update(dataset_floors(n, edges))
    cert = rec.get("minor_certificate")
    if rec["provenance"] == "certified:minor":
        row["minor_certificate_present"] = cert is not None
        if cert:
            row["minor_size"] = int(cert.get("size", 0))
            row["minor_rule"] = cert.get("rule", "")
            row["minor_refuted"] = int(cert.get("refuted", -1))
            row["minor_ratio"] = round(int(cert.get("size", 0)) / n, 4) if n else np.nan
    row["omega1"] = row["omega"] - 1
    for col in ("degeneracy", "mmd_leastc", "mmd_mind", "omega1"):
        row[f"gap_{col}"] = width - row[col]
    row["floor_cheap"] = max(row["degeneracy"], row["mmd_leastc"], row["mmd_mind"], row["omega1"])
    row["gap_floor_cheap"] = width - row["floor_cheap"]
    return row


def build_dataset(workers: int) -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    recs = list(dataset_records())
    log(f"dataset stage: {len(recs)} certified classes from {DATASET.relative_to(ROOT)}; {workers} workers")
    t0 = time.monotonic()
    recs.sort(key=lambda r: -int(r["n"]))     # big ones first so the pool tail is short
    rows = []
    with Pool(workers) as pool:
        for k, row in enumerate(pool.imap_unordered(_dataset_job, recs, chunksize=4), 1):
            rows.append(row)
            if k % 2000 == 0:
                log(f"dataset: {k}/{len(recs)}, {time.monotonic() - t0:.0f} s")
    f = pd.DataFrame(rows).sort_values("id").reset_index(drop=True)
    f.to_csv(LEDGER_DATASET, index=False, compression="gzip")
    log(f"dataset stage: wrote {LEDGER_DATASET.relative_to(ROOT)} ({len(f)} rows) in {time.monotonic() - t0:.0f} s; "
        f"skipped components > {DATASET_MAX_COMPONENT}: {int((f['skipped_components'] > 0).sum())} rows; "
        f"omega censored: {int(f['omega_censored'].sum())}")
    bad = f[f["gap_floor_cheap"] < 0]
    _stop_on_violation(bad[["id", "n", "width", "degeneracy", "mmd_leastc", "mmd_mind", "omega1"]], "dataset")
    log("dataset stage: guard passed: no cheap floor above a certified width")
    return f


# ----------------------------------------------------------------------------
# (c) targets
# ----------------------------------------------------------------------------


def stratified_sample(pool: pd.DataFrame, size: int, seed: int) -> list[str]:
    """`size` instance names from `pool`, stratified by `band` in proportion to
    the band's share of the pool (largest remainders), drawn without
    replacement by `numpy.random.default_rng(seed)`, in band order."""
    rng = np.random.default_rng(seed)
    counts = pool["band"].value_counts()
    order = [f"{lo}–{hi}" for lo, hi in BANDS]
    shares = {b: size * counts.get(b, 0) / len(pool) for b in order}
    quota = {b: int(np.floor(shares[b])) for b in order}
    short = size - sum(quota.values())
    for b in sorted(order, key=lambda b: shares[b] - quota[b], reverse=True)[:short]:
        quota[b] += 1
    chosen = []
    for b in order:
        names = sorted(pool.loc[pool["band"] == b, "instance_name"])
        k = min(quota[b], len(names))
        if k:
            chosen.extend(sorted(rng.choice(names, size=k, replace=False).tolist()))
    return chosen


def open_floors() -> dict[str, float]:
    floors: dict[str, float] = {}
    for path in OPEN_FLOOR_CSVS:
        if not path.exists() or path.stat().st_size == 0:
            continue
        r = pd.read_csv(path)
        if "lower" not in r.columns:
            continue
        for _, row in r.iterrows():
            if pd.notna(row.get("lower")):
                floors[row["id"]] = max(floors.get(row["id"], -1), float(row["lower"]))
    return floors


def open_class_graphs(ids: list[str] | None = None, check_representative: bool = True) -> list[dict]:
    """Item 07: the 24 open dataset classes of `targets.json` as graphs. Each
    record carries the jsonl's `edges` (the representative's labels), its
    recorded `width` (an upper bound: the stored layout achieves it) and
    `layout` (the stored witness, in the orientation whose *prefix* vertex
    separation — placed vertices with a neighbour outside — equals the
    width; the dataset's own convention is the reversal), the recorded
    floor `lower` from `targets.json`, and, when `check_representative`, the
    representative member computed as `paper1.dataset.fold` does (from the
    values on record before the fold, as `run_unlimited.py` does) with the
    check that its graph is the record's graph edge for edge. Nothing here
    runs a solver."""
    targets = json.loads(TARGETS_JSON.read_text())
    wanted = {r["id"]: r for r in targets["open24"]}
    if ids is not None:
        wanted = {k: v for k, v in wanted.items() if k in set(ids)}
    recs = {}
    for rec in dataset_records(certified_only=False):
        if rec["id"] in wanted:
            recs[rec["id"]] = rec
    rep_of = {}
    if check_representative:
        sys.path.insert(0, str(ROOT))
        from collections import defaultdict
        from paper1.dataset import INDEX, VALUES_CSV, PRIORITY, class_order, representative, load, read_csv
        idx = [r for r in read_csv(INDEX) if not r["error"]]
        by = defaultdict(list)
        for r in idx:
            by[r["cls"]].append(r)
        for members in by.values():
            members.sort(key=lambda r: (PRIORITY[r["collection"]], r["source"], r["name"]))
        cls_of_id = {f"pwc-{i + 1:05d}": c for i, c in enumerate(class_order(by))}
        base = {(v["source"], v["name"]): v for v in read_csv(VALUES_CSV)
                if not v["evidence"].startswith("reports/scratch/")}
        for cid in wanted:
            rep, _ = representative(by[cls_of_id[cid]], base)
            n_rep, e_rep = load(rep)
            rep_of[cid] = (rep, n_rep, {(min(a, b), max(a, b)) for a, b in e_rep})
    out = []
    for cid, t in wanted.items():
        rec = recs[cid]
        n = int(rec["n"])
        edges = [(int(a), int(b)) for a, b in rec["edges"]]
        adj = adjacency_from_edges(n, edges)
        lay = [int(v) for v in (rec.get("layout") or [])]
        layout, vs = None, None
        if sorted(lay) == list(range(n)):
            for cand in (lay[::-1], lay):
                v = _prefix_vs(adj, cand)
                if v == int(rec["width"]):
                    layout, vs = cand, v
                    break
        row = {"id": cid, "names": t["names"], "collections": t["collections"], "n": n, "m": len(edges),
               "width": int(rec["width"]), "lower": t.get("lower"), "lower_source": t.get("lower_source"),
               "provenance": rec.get("provenance"), "edges": edges, "adj": adj, "layout": layout,
               "layout_vs": vs, "record_layout_len": len(lay)}
        if check_representative:
            rep, n_rep, e_rep = rep_of[cid]
            row["representative"] = {"collection": rep["collection"], "source": rep["source"], "name": rep["name"]}
            row["representative_matches_record"] = (n_rep == n and e_rep == {(min(a, b), max(a, b)) for a, b in edges})
        out.append(row)
    return out


def _prefix_vs(adj: list[int], order: list[int]) -> int:
    """Vertex separation under the prefix definition: the largest number of
    placed vertices with a neighbour outside the prefix."""
    placed, best = 0, 0
    full = (1 << len(adj)) - 1
    for v in order:
        placed |= 1 << v
        rest = full & ~placed
        best = max(best, sum(1 for u in range(len(adj)) if (placed >> u) & 1 and adj[u] & rest))
    return best


def build_targets() -> dict:
    f = pd.read_csv(LEDGER_CORPUS)
    gap338 = sorted(f.loc[f["is_gap338"], "instance_name"])
    cs200 = sorted(f.loc[f["is_cs200"], "instance_name"])
    small = sorted(f.loc[f["is_small"], "instance_name"])
    pool = f[~f["is_gap338"] & ~f["is_cs200"]]
    rest500 = stratified_sample(pool, REST_SIZE, REST_SEED)
    u = pd.read_csv(OPEN_CSV)
    floors = open_floors()
    ds = pd.read_csv(LEDGER_DATASET) if LEDGER_DATASET.exists() else None
    open24 = []
    for _, row in u.iterrows():
        cid = row["id_now"]
        rec = {"id": cid, "names": row["names"], "collections": row["collections"], "n": int(row["n"]),
               "m": int(row["m"]), "width": int(row["recorded_width"])}
        if cid in floors:
            rec["lower"], rec["lower_source"] = int(floors[cid]), "reports/scratch/dataset_open/results_quick*.csv `lower`"
        elif ds is not None and cid in set(ds["id"]):
            rec["lower"] = int(ds.loc[ds["id"] == cid, "floor_cheap"].iloc[0])
            rec["lower_source"] = "ledger_dataset.csv.gz floor_cheap"
        else:
            rec["lower"], rec["lower_source"] = None, "none on record"
        open24.append(rec)
    bands = {b: int((pool["band"] == b).sum()) for b in [f"{lo}–{hi}" for lo, hi in BANDS]}
    rest_bands = pd.Series([band_label(int(f.loc[f["instance_name"] == nm, "n"].iloc[0])) for nm in rest500]).value_counts().to_dict()
    targets = {
        "written": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ledger_corpus_sha256": sha256_of(LEDGER_CORPUS),
        "rules": {"gap338": "optimum - lb_best >= 2 in ledger_corpus.csv",
                  "cs200": "collection == 'Chu & Stuckey'",
                  "open24": f"{OPEN_CSV.relative_to(ROOT)}; floors from results_quick*.csv `lower`",
                  "rest500": f"stratified by the harness's seven size bands from the corpus minus gap338 ∪ cs200; "
                             f"numpy.random.default_rng({REST_SEED}); largest-remainder quotas",
                  "small": f"n <= {SMALL_N}"},
        "seed": REST_SEED,
        "counts": {"gap338": len(gap338), "cs200": len(cs200), "open24": len(open24), "rest500": len(rest500),
                   "small": len(small), "pool_for_rest500": int(len(pool)), "pool_by_band": bands,
                   "rest500_by_band": rest_bands,
                   "gap338_and_cs200": int(len(set(gap338) & set(cs200))),
                   "small_and_gap338": int(len(set(small) & set(gap338)))},
        "gap338": gap338, "cs200": cs200, "open24": open24, "rest500": rest500, "small": small,
    }
    TARGETS_JSON.write_text(json.dumps(targets, indent=1))
    log(f"targets: {targets['counts']}")
    return targets


# ----------------------------------------------------------------------------
# (d) tables
# ----------------------------------------------------------------------------


def _md(table: pd.DataFrame, floatfmt: str = ".2f") -> str:
    # object dtype: an all-numeric frame would be upcast to float on the way into tabulate
    return table.astype(object).to_markdown(index=False, floatfmt=floatfmt)


def per_bound_table(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, rests_on in CORPUS_BOUNDS:
        g = f[f"gap_{col}"]
        have = g.notna()
        rows.append({"bound": col, "instances": int(have.sum()), "tight": int((g == 0).sum()),
                     "gap 1": int((g == 1).sum()), "gap ≥ 2": int((g >= 2).sum()),
                     "mean gap": float(g[have].mean()) if have.any() else np.nan,
                     "max gap": int(g[have].max()) if have.any() else np.nan,
                     "above optimum": int((g < 0).sum())})
    g = f["gap_floor0"]
    rows.append({"bound": "floor0", "instances": len(f), "tight": int((g == 0).sum()), "gap 1": int((g == 1).sum()),
                 "gap ≥ 2": int((g >= 2).sum()), "mean gap": float(g.mean()), "max gap": int(g.max()),
                 "above optimum": int((g < 0).sum())})
    return pd.DataFrame(rows)


def gap_by(f: pd.DataFrame, key: str, order=None) -> pd.DataFrame:
    rows = []
    groups = f.groupby(key)
    keys = order if order is not None else sorted(groups.groups)
    for k in keys:
        if k not in groups.groups:
            continue
        g = groups.get_group(k)
        rows.append({key: k, "instances": len(g),
                     "lb_best tight": int((g["gap_lb_best"] == 0).sum()), "lb_best mean gap": g["gap_lb_best"].mean(),
                     "floor0 tight": int((g["gap_floor0"] == 0).sum()), "floor0 gap 1": int((g["gap_floor0"] == 1).sum()),
                     "floor0 gap ≥ 2": int((g["gap_floor0"] >= 2).sum()), "floor0 mean gap": g["gap_floor0"].mean(),
                     "floor0 max gap": int(g["gap_floor0"].max())})
    return pd.DataFrame(rows)


def floor0_source_table(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in FLOOR0_PARTS:
        attains = f["floor0_source"].str.split("|").map(lambda s: col in s)
        alone = f["floor0_source"] == col
        rows.append({"part": col, "attains floor0": int(attains.sum()), "attains alone": int(alone.sum()),
                     "attains alone and tight": int((alone & (f["gap_floor0"] == 0)).sum()),
                     "on the 338: attains alone": int((alone & f["is_gap338"]).sum()),
                     "on the 338: closes alone": int((alone & f["is_gap338"] & (f["gap_floor0"] == 0)).sum())})
    return pd.DataFrame(rows)


def gap338_table(f: pd.DataFrame) -> pd.DataFrame:
    g = f[f["is_gap338"]]
    rows = []
    for col in ("lb_best", "tw1", "harper12", "lemmaP", "minor", "floor0"):
        gap = g[f"gap_{col}"]
        have = gap.notna()
        rows.append({"bound": col, "with a value": int(have.sum()), "closes (gap 0)": int((gap == 0).sum()),
                     "gap 1": int((gap == 1).sum()), "gap ≥ 2": int((gap >= 2).sum()),
                     "mean gap": gap[have].mean(), "max gap": int(gap[have].max()) if have.any() else np.nan,
                     "beats lb_best": int((g[col] > g["lb_best"]).sum())})
    return pd.DataFrame(rows)


def cs_class_table(f: pd.DataFrame) -> pd.DataFrame:
    g = f[f["is_cs200"]].copy()
    rows = []
    for (n, m, d), grp in g.groupby(["cs_n", "cs_m", "cs_d"]):
        rows.append({"n": int(n), "m": int(m), "d": int(d), "instances": len(grp),
                     "mean opt": grp["optimum"].mean(),
                     "lb_best gap": grp["gap_lb_best"].mean(), "harper12 gap": grp["gap_harper12"].mean(),
                     "tw1 gap": grp["gap_tw1"].mean(), "lemmaP gap": grp["gap_lemmaP"].mean(),
                     "floor0 gap": grp["gap_floor0"].mean(), "floor0 tight": int((grp["gap_floor0"] == 0).sum()),
                     "harper12 complete": int(grp["harper12_complete"].astype(str).str.lower().eq("true").sum()),
                     "harper12 s": grp["harper12_seconds"].mean()})
    t = pd.DataFrame(rows).sort_values(["n", "m", "d"])
    for c in ("n", "m", "d", "instances", "floor0 tight", "harper12 complete"):
        t[c] = t[c].astype(int)
    return t


def harper_table(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    order = [f"{lo}–{hi}" for lo, hi in BANDS]
    for b in order:
        g = f[f["band"] == b]
        if g.empty:
            continue
        comp = g["harper12_complete"].astype(str).str.lower().eq("true")
        rows.append({"band": b, "instances": len(g), "run": int(g["harper12"].notna().sum()),
                     "complete to cap 12": int(comp.sum()), "censored at 60 s": int((g["harper12"].notna() & ~comp).sum()),
                     "mean cap reached": g["harper12_cap"].mean(), "core-seconds": g["harper12_seconds"].sum(),
                     "harper12 > exp_rec": int((g["harper12"] > g["exp_rec"]).sum()),
                     "harper12 > lb_best": int((g["harper12"] > g["lb_best"]).sum()),
                     "harper12 tight": int((g["gap_harper12"] == 0).sum())})
    return pd.DataFrame(rows)


def dataset_tables(ds: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rows = []
    for col in ("degeneracy", "mmd_leastc", "mmd_mind", "omega1", "floor_cheap"):
        g = ds[f"gap_{col}"]
        rows.append({"floor (pw units)": col, "classes": len(ds), "tight": int((g == 0).sum()), "gap 1": int((g == 1).sum()),
                     "gap ≥ 2": int((g >= 2).sum()), "mean gap": g.mean(), "max gap": int(g.max()),
                     "above width": int((g < 0).sum())})
    per = pd.DataFrame(rows)
    rows = []
    for coll, g in ds.groupby("collection"):
        rows.append({"collection": coll, "classes": len(g), "mean n": g["n"].mean(), "mean width": g["width"].mean(),
                     "floor_cheap tight": int((g["gap_floor_cheap"] == 0).sum()),
                     "gap ≥ 2": int((g["gap_floor_cheap"] >= 2).sum()), "mean gap": g["gap_floor_cheap"].mean(),
                     "max gap": int(g["gap_floor_cheap"].max()),
                     "skipped": int((g["skipped_components"] > 0).sum())})
    bycoll = pd.DataFrame(rows).sort_values("classes", ascending=False)
    m = ds[ds["provenance"] == "certified:minor"].copy()
    rows = []
    if "minor_ratio" in m.columns:
        have = m[m["minor_ratio"].notna()]
        rows.append({"certified:minor classes": len(m), "with certificate": len(have),
                     "mean size/n": have["minor_ratio"].mean(), "median size/n": have["minor_ratio"].median(),
                     "min size/n": have["minor_ratio"].min(), "max size/n": have["minor_ratio"].max(),
                     "least-c": int((have["minor_rule"] == "least-c").sum()), "min-d": int((have["minor_rule"] == "min-d").sum()),
                     "refuted = width − 1": int((have["minor_refuted"] == have["width"] - 1).sum()),
                     "floor_cheap tight": int((m["gap_floor_cheap"] == 0).sum())})
    minors = pd.DataFrame(rows)
    return {"per_floor": per, "by_collection": bycoll, "minors": minors}


def write_tables() -> str:
    f = pd.read_csv(LEDGER_CORPUS)
    parts = ["# Item 01 tables (generated by `learning.obstruction_ledger --stage tables`)", "",
             f"Corpus rows: {len(f)}; ledger sha256 {sha256_of(LEDGER_CORPUS)[:16]}…", "",
             "## (a1) every bound on record, corpus, optimum units", "", _md(per_bound_table(f)), "",
             "## (a2) floor0 by collection", "", _md(gap_by(f, "collection")), "",
             "## (a3) floor0 by size band", "", _md(gap_by(f, "band", [f"{lo}–{hi}" for lo, hi in BANDS])), "",
             "## (a4) which part attains floor0", "", _md(floor0_source_table(f)), "",
             "## (a5) the 338 against the record", "", _md(gap338_table(f)), "",
             "## (a6) the 200 Chu & Stuckey by class", "", _md(cs_class_table(f)), "",
             "## (a7) Harper at cap 12 by band", "", _md(harper_table(f)), ""]
    stopped = f["harper12"].isna().sum()
    parts.append(f"Harper rows without a value (not reached under the wall): {int(stopped)}.")
    parts.append("")
    hs = f[f["minor"].notna()][["instance_name", "optimum", "lb_best", "harper12", "tw1", "lemmaP", "minor", "minor_source", "minor_survey", "floor0"]]
    parts += ["## (a8) the instances with a minor certificate on record", "", _md(hs, ".0f"), ""]
    if LEDGER_DATASET.exists():
        ds = pd.read_csv(LEDGER_DATASET)
        t = dataset_tables(ds)
        parts += [f"## (b1) dataset: {len(ds)} certified classes, cheap floors against the width (pathwidth units)", "",
                  _md(t["per_floor"]), "",
                  f"Rows with a component above {DATASET_MAX_COMPONENT} vertices (floors over the rest): "
                  f"{int((ds['skipped_components'] > 0).sum())}; omega censored (2 s / {CLIQUE_CAP} cliques): "
                  f"{int(ds['omega_censored'].sum())}; edgeless classes: {int((~ds['edges_present']).sum())}; "
                  f"seconds total: {ds['seconds'].sum():.0f}.", "",
                  "## (b2) by collection", "", _md(t["by_collection"]), "",
                  "## (b3) the certified:minor classes", "", _md(t["minors"], ".3f"), ""]
    if TARGETS_JSON.exists():
        tg = json.loads(TARGETS_JSON.read_text())
        parts += ["## (c) targets", "", "```", json.dumps(tg["counts"], indent=1), "```", ""]
    text = "\n".join(parts)
    TABLES_MD.write_text(text)
    log(f"tables: wrote {TABLES_MD.relative_to(ROOT)}")
    return text


# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("corpus", "dataset", "targets", "tables"), required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=4800.0, help="seconds; the Harper run stops dispatching after this")
    ap.add_argument("--no-harper", action="store_true", help="corpus stage without the Harper run (record only)")
    args = ap.parse_args()
    os.nice(19) if hasattr(os, "nice") and os.nice(0) < 19 else None
    if args.stage == "corpus":
        build_corpus(args.workers, args.wall, harper=not args.no_harper)
    elif args.stage == "dataset":
        build_dataset(args.workers)
    elif args.stage == "targets":
        build_targets()
    else:
        write_tables()


if __name__ == "__main__":
    main()
