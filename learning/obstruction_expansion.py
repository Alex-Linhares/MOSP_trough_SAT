"""loop0013 item 02: family E (expansion) by search — the ceiling on every
target, the exact profile at `n <= 22`, the cap-12 floor by branch and bound.

**The object.** For the MOSP graph `G` of an instance (customers as vertices,
a clique per pattern), the vertex-isoperimetric profile is
`f(t) = min_{|C| = t} |N[C]|`. Harper's bound (Harper 1966; Lean
`exists_closedNbhd_card_le`) is `pw >= f(t) - t` for every `t`, so in optimum
units the family's bound is `max_t (f(t) - t) + 1`; the empty-pair bound
(`card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth`) is `n - 2 s* - 2 <= pw`
with `s* = max_t min(t - 1, n - f(t))`, a weakening of the same profile.

**Direction** (plan §0.2). Both are *universal* statements: the inner minimum
is over every `t`-set. A set `C` found by search proves `f(t) <= |N[C]|` and
nothing more, so the search's value `max_t (fhat(t) - t) + 1` with `fhat >= f`
is a **ceiling** on what the family can ever certify, never a bound; the
witness layout's prefixes give `fhat(t) <= t + pw` at every `t`, so with
those seeds the ceiling is at most the optimum. The **floor** is the valid
bound, from `f` proved exactly: `satisfiability.expansion_bound` (branch and
bound to cap 12) here; SAT with a DRAT proof per `(t, b)` is item 03.

**What this module does.** `search_profile` (tabu search on swaps per `t`,
restarted from the maximal cliques, the certified witness's prefix sets, BFS
balls of radius 1 and 2 around every vertex, and the best set at `t -/+ 1`;
the C helper `obstruction_expansion.c`); `exact_profile` (every subset at
`n <= 22`, same helper); `harper_floor`, the cap-12 branch-and-bound floor as
a `learning.bound_harness --extra` candidate; and the four stages:

    nice -n 19 python3 -m learning.obstruction_expansion --stage ceiling --targets all --workers 8
    nice -n 19 python3 -m learning.obstruction_expansion --stage exact --targets small --workers 8
    nice -n 19 python3 -m learning.obstruction_expansion --stage floor --targets gap338 --workers 8
    nice -n 19 python3 -m learning.obstruction_expansion --stage tables

Nothing here solves an instance: every optimum is read from the record
(`reports/scratch/obstruction_search/01_ledger/ledger_corpus.csv`), the
witness from `solutions/<name>.json` (read only), and the only new exact
computations are subset enumerations at `n <= 22` and the cap-12 branch and
bound on the 35 instances item 01 censored at 60 s.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from learning.obstruction_ledger import (LEDGER_CORPUS, TARGETS_JSON, SOLUTIONS_DIR,
                                         BANDS, adjacency_from_matrix, corpus_instances)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "scratch" / "obstruction_search" / "02_expansion"
CEILING_CSV = OUT / "ceiling.csv"
EXACT_CSV = OUT / "exact_small.csv"
FLOOR_CSV = OUT / "floor.csv"
SETS_DIR = OUT / "sets"
TABLES_MD = OUT / "tables.md"
RUN_LOG = OUT / "run.log"

_SOURCE = Path(__file__).with_name("obstruction_expansion.c")
_LIBRARY = Path(__file__).with_name("_obstruction_expansion.so")
_lock = threading.Lock()
_library: "ctypes.CDLL | None" = None

EXACT_MAX_N = 22
HARPER_CAP = 12
CLIQUE_SEEDS = 200
TENURE = 7
MAX_SWAPS = 2000
STALL_SWEEP = 40
STALL_FOCUS = 150
MAX_ROUNDS = 12
FLOOR_BUDGET_LOW_CAP = 600.0   # item 01's cap <= 10: room for several levels
FLOOR_BUDGET_HIGH_CAP = 300.0  # item 01's cap 11: only f(13) is missing


def log(msg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(RUN_LOG, "a") as handle:
        handle.write(line + "\n")


# ----------------------------------------------------------------------------
# the C helper
# ----------------------------------------------------------------------------


def _build() -> None:
    if _LIBRARY.exists() and _LIBRARY.stat().st_mtime >= _SOURCE.stat().st_mtime:
        return
    scratch = _LIBRARY.with_name(_LIBRARY.name + f".build-{os.getpid()}")
    subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(scratch), str(_SOURCE)],
                   check=True, capture_output=True, timeout=120)
    os.replace(scratch, _LIBRARY)


def _load() -> ctypes.CDLL:
    global _library
    with _lock:
        if _library is not None:
            return _library
        _build()
        lib = ctypes.CDLL(str(_LIBRARY))
        u64p, i32p, u32p, f64p = (ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_double))
        lib.exact_profile.restype = ctypes.c_int
        lib.exact_profile.argtypes = [ctypes.c_int, u32p, i32p, u32p]
        lib.search_profile.restype = ctypes.c_int
        lib.search_profile.argtypes = [ctypes.c_int, ctypes.c_int, u64p, ctypes.c_int, u64p,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                                       ctypes.c_double, ctypes.c_int, i32p, u64p, f64p, i32p, i32p]
        _library = lib
        return lib


# ----------------------------------------------------------------------------
# graphs, masks, witnesses
# ----------------------------------------------------------------------------


def closed_masks(adj: list[int]) -> list[int]:
    """Closed neighbourhoods `N[v]` from open ones."""
    return [a | (1 << v) for v, a in enumerate(adj)]


def closed_masks_from_matrix(matrix) -> list[int]:
    return closed_masks(adjacency_from_matrix(np.asarray(matrix, dtype=int)))


def _words(n: int) -> int:
    return max(1, (n + 63) // 64)


def _to_words(mask: int, W: int) -> list[int]:
    return [(mask >> (64 * i)) & ((1 << 64) - 1) for i in range(W)]


def _from_words(words, W: int) -> int:
    return sum(int(words[i]) << (64 * i) for i in range(W))


def mask_to_list(mask: int) -> list[int]:
    out = []
    while mask:
        bit = mask & -mask
        out.append(bit.bit_length() - 1)
        mask ^= bit
    return out


def neighbourhood_size(closed: list[int], C: int) -> int:
    """`|N[C]|` for a set given as a mask."""
    union = 0
    for v in mask_to_list(C):
        union |= closed[v]
    return union.bit_count()


def witness_layouts(matrix, ordering) -> tuple[list[int], list[int]]:
    """The two customer layouts a pattern ordering induces: by opening time
    (position of the first pattern a customer needs, ties by index) and by
    closing time (last pattern). The *opening* layout has vertex separation at
    most the ordering's open-stack count minus one (a placed vertex with a
    neighbour outside the prefix is open at the next opening position, and so
    is the vertex opening there), so its prefixes seed the search with sets
    witnessing `fhat(t) <= t + pw`. The closing layout carries no such
    guarantee under the prefix definition (the cost of a layout is not
    reversal-invariant; `vertex_separation_of` on it is recorded, not relied
    on) and its finished sets are seeds like any other."""
    matrix = np.asarray(matrix, dtype=int)
    n = matrix.shape[0]
    pos = {p: i for i, p in enumerate(ordering)}
    first, last = [], []
    for v in range(n):
        pats = [pos[p] for p in np.flatnonzero(matrix[v]) if p in pos]
        first.append(min(pats) if pats else 0)
        last.append(max(pats) if pats else 0)
    opening = sorted(range(n), key=lambda v: (first[v], v))
    closing = sorted(range(n), key=lambda v: (last[v], v))
    return opening, closing


def vertex_separation_of(adj: list[int], order: list[int]) -> int:
    """Max over prefixes of the placed vertices with a neighbour outside."""
    placed, best = 0, 0
    full = (1 << len(adj)) - 1
    for v in order:
        placed |= 1 << v
        rest = full & ~placed
        sep = sum(1 for u in mask_to_list(placed) if adj[u] & rest)
        best = max(best, sep)
    return best


def finished_sets(closed: list[int], order: list[int]) -> list[int]:
    """The distinct non-empty sets `C_i = {v in V_i : N[v] ⊆ V_i}` over the
    prefixes `V_i` of a layout; nested, one per new finished vertex. A
    `t`-subset of the first `C_i` with `|C_i| >= t` has `|N[C]| <= i <= t + vs`."""
    placed, out, seen = 0, [], set()
    for v in order:
        placed |= 1 << v
        C = 0
        for u in mask_to_list(placed):
            if closed[u] & ~placed == 0:
                C |= 1 << u
        if C and C not in seen:
            seen.add(C)
            out.append(C)
    return out


def maximal_clique_seeds(adj: list[int], cap: int = CLIQUE_SEEDS) -> list[int]:
    import itertools
    import networkx as nx

    n = len(adj)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for v in range(n):
        for u in mask_to_list(adj[v]):
            if u > v:
                g.add_edge(v, u)
    out = []
    for clique in itertools.islice(nx.find_cliques(g), cap):
        m = 0
        for v in clique:
            m |= 1 << v
        out.append(m)
    return out


def solution_record(name: str) -> dict | None:
    from satisfiability.mosp_solver import _solution_path
    from mosp.instance import MOSPInstance

    path = _solution_path(MOSPInstance.from_matrix([[1]], name=name), SOLUTIONS_DIR)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in (name or "unnamed"))


# ----------------------------------------------------------------------------
# the profile: exact and searched
# ----------------------------------------------------------------------------


@dataclass
class Profile:
    """`f[t]` (or `fhat[t]`) for `t = 0..n`, with one set per `t` as a mask."""

    n: int
    values: list[int]
    sets: list[int]
    exact: bool
    seconds: float = 0.0
    rounds: int = 0
    improved_rounds: int = 0
    level_seconds: list[float] = field(default_factory=list)

    def harper(self) -> tuple[int, int]:
        """`max_t (values[t] - t) + 1` in optimum units, and its smallest argmax `t*`."""
        best, arg = -1, 0
        for t in range(1, self.n + 1):
            if self.values[t] - t > best:
                best, arg = self.values[t] - t, t
        return best + 1, arg

    def s_hat(self) -> int:
        """`max_t min(t - 1, n - values[t])` (`s*` when exact, a lower estimate of it otherwise)."""
        return max(min(t - 1, self.n - self.values[t]) for t in range(1, self.n + 1))

    def empty_pair(self) -> int:
        """`n - 2 s - 2 + 1`: the empty-pair value in optimum units."""
        return self.n - 2 * self.s_hat() - 1


def exact_profile(closed: list[int]) -> Profile:
    """Every subset: `f(t)` and a minimiser per `t`, `n <= 22`."""
    n = len(closed)
    if n > EXACT_MAX_N:
        raise ValueError(f"exact_profile is for n <= {EXACT_MAX_N}, got {n}")
    if n == 0:
        return Profile(0, [0], [0], True)
    lib = _load()
    nbr = (ctypes.c_uint32 * n)(*closed)
    f = (ctypes.c_int * (n + 1))()
    sets = (ctypes.c_uint32 * (n + 1))()
    t0 = time.monotonic()
    rc = lib.exact_profile(n, nbr, f, sets)
    if rc:
        raise RuntimeError(f"exact_profile failed: {rc}")
    return Profile(n, list(f), [int(x) for x in sets], True, time.monotonic() - t0)


def exact_profile_reference(closed: list[int]) -> list[int]:
    """Pure-Python reference for the tests (tiny `n`)."""
    n = len(closed)
    f = [n + 1] * (n + 1)
    f[0] = 0
    for mask in range(1, 1 << n):
        f[mask.bit_count()] = min(f[mask.bit_count()], neighbourhood_size(closed, mask))
    return f


def search_profile(closed: list[int], seeds: list[int], time_budget: float, rng_seed: int = 1,
                   max_swaps: int = MAX_SWAPS, stall_sweep: int = STALL_SWEEP, stall_focus: int = STALL_FOCUS,
                   tenure: int = TENURE, max_rounds: int = MAX_ROUNDS) -> Profile:
    """Tabu search per level under a wall budget; `fhat(t) >= f(t)` with the
    set attaining it. `seeds` are masks of any size (cliques, witness prefix
    sets); the helper adds BFS balls and the neighbouring levels' sets."""
    n = len(closed)
    if n == 0:
        return Profile(0, [0], [0], False)
    W = _words(n)
    lib = _load()
    nbr = (ctypes.c_uint64 * (n * W))()
    for v in range(n):
        for i, w in enumerate(_to_words(closed[v], W)):
            nbr[v * W + i] = w
    seeds = [s for s in seeds if s] or [0]
    sd = (ctypes.c_uint64 * (len(seeds) * W))()
    for k, s in enumerate(seeds):
        for i, w in enumerate(_to_words(s, W)):
            sd[k * W + i] = w
    fhat = (ctypes.c_int * (n + 1))()
    sets = (ctypes.c_uint64 * ((n + 1) * W))()
    secs = (ctypes.c_double * (n + 1))()
    rounds, improved = ctypes.c_int(0), ctypes.c_int(0)
    t0 = time.monotonic()
    rc = lib.search_profile(n, W, nbr, len(seeds), sd, max_swaps, stall_sweep, stall_focus, tenure,
                            ctypes.c_uint64(rng_seed), float(time_budget), max_rounds, fhat, sets, secs,
                            ctypes.byref(rounds), ctypes.byref(improved))
    if rc:
        raise RuntimeError(f"search_profile failed: {rc}")
    values = list(fhat)
    masks = [_from_words(sets[t * W:(t + 1) * W], W) for t in range(n + 1)]
    # every incumbent is re-evaluated in Python: the value recorded is the set's, never the helper's word
    for t in range(1, n + 1):
        assert masks[t].bit_count() == t, (t, masks[t].bit_count())
        values[t] = neighbourhood_size(closed, masks[t])
    return Profile(n, values, masks, False, time.monotonic() - t0, rounds.value, improved.value, list(secs))


def witness_profile(closed: list[int], layout_sets: list[int]) -> list[int]:
    """`fw(t)`: the best `|N[C]|` over `t`-subsets of the witness's finished
    sets (the first `C_i` with `|C_i| >= t`, its first `t` vertices), i.e.
    what the witness alone certifies at each `t`; `<= t + pw` by construction."""
    n = len(closed)
    fw = [n + 1] * (n + 1)
    fw[0] = 0
    for C in layout_sets:
        members = mask_to_list(C)
        union, sub = 0, 0
        for k, v in enumerate(members, 1):
            union |= closed[v]
            sub |= 1 << v
            if union.bit_count() < fw[k]:
                fw[k] = union.bit_count()
    # monotone closure downward: a t-subset of a larger finished set is also a candidate
    for t in range(n - 1, 0, -1):
        fw[t] = min(fw[t], fw[t + 1])
    fw[n] = min(fw[n], n)
    return fw


def ceiling_budget(n: int) -> float:
    """Seconds per instance for the search: `0.005 n²` clamped to `[2, 90]`."""
    return float(min(90.0, max(2.0, 0.005 * n * n)))


# ----------------------------------------------------------------------------
# the harness candidate: the cap-12 branch-and-bound floor
# ----------------------------------------------------------------------------


def harper_floor(graph, matrix, budget) -> tuple[int, dict]:
    """Family E's floor: Harper's bound with `f` proved exactly by branch and
    bound to cap 12 under the harness's budget (`satisfiability.expansion_bound`;
    a censored level is discarded, never used). Optimum units; valid by
    `exists_closedNbhd_card_le`."""
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound

    seconds = getattr(budget, "seconds", budget)
    inst = MOSPInstance.from_matrix(np.asarray(matrix, dtype=int), name="harness")
    b = expansion_bound(inst, max_t=HARPER_CAP, time_budget=float(seconds))
    return int(b.value), {"cap": int(b.cap), "complete": bool(b.complete)}


# ----------------------------------------------------------------------------
# targets and instances
# ----------------------------------------------------------------------------


def load_targets() -> dict:
    return json.loads(TARGETS_JSON.read_text())


def target_names(which: str, targets: dict | None = None) -> list[str]:
    targets = targets or load_targets()
    if which == "all":
        names: list[str] = []
        seen = set()
        for key in ("gap338", "cs200", "rest500", "small"):
            for nm in targets[key]:
                if nm not in seen:
                    seen.add(nm)
                    names.append(nm)
        return names
    if which not in targets or which == "open24":
        raise SystemExit(f"unknown or unsupported target set {which!r}")
    return list(targets[which])


def ledger() -> pd.DataFrame:
    return pd.read_csv(LEDGER_CORPUS)


# ----------------------------------------------------------------------------
# stage: ceiling
# ----------------------------------------------------------------------------


def _ceiling_job(args) -> dict:
    name, matrix, ordering, optimum, budget, rng_seed = args
    matrix = np.asarray(matrix, dtype=int)
    n = matrix.shape[0]
    adj = adjacency_from_matrix(matrix)
    closed = closed_masks(adj)
    t0 = time.monotonic()
    seeds, wsets, vs_open, vs_close = [], [], -1, -1
    if ordering is not None:
        opening, closing = witness_layouts(matrix, ordering)
        vs_open, vs_close = vertex_separation_of(adj, opening), vertex_separation_of(adj, closing)
        wsets = finished_sets(closed, opening) + finished_sets(closed, closing)
        seeds += wsets
    cliques = maximal_clique_seeds(adj)
    seeds += cliques
    fw = witness_profile(closed, wsets) if wsets else [n + 1] * (n + 1)
    prof = search_profile(closed, seeds, budget, rng_seed=rng_seed)
    ceiling, t_star = prof.harper()
    s_hat = prof.s_hat()
    wprof = Profile(n, fw, [0] * (n + 1), False)
    w_ceiling, _ = wprof.harper() if wsets else (n + 1, 0)
    below_witness = sum(1 for t in range(1, n) if prof.values[t] < fw[t])
    OUT.mkdir(parents=True, exist_ok=True)
    SETS_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"instance_name": name, "n": n, "optimum": int(optimum), "ceiling": int(ceiling), "t_star": int(t_star),
           "fhat": prof.values, "witness_profile": fw,
           "sets": {str(t): mask_to_list(prof.sets[t]) for t in range(1, n + 1)},
           "witness_vs_opening": vs_open, "witness_vs_closing": vs_close, "budget_seconds": budget,
           "rng_seed": rng_seed, "seeds": {"witness_sets": len(wsets), "cliques": len(cliques)},
           "note": "a set C of size t proves f(t) <= |N[C]| only; the ceiling is not a bound"}
    (SETS_DIR / f"{safe_name(name)}.json").write_text(json.dumps(rec))
    return {"instance_name": name, "n": n, "optimum": int(optimum), "ceiling": int(ceiling), "t_star": int(t_star),
            "s_hat": int(s_hat), "empty_ceiling": int(prof.empty_pair()), "witness_ceiling": int(w_ceiling),
            "witness_vs_opening": vs_open, "witness_vs_closing": vs_close,
            "levels_below_witness": below_witness, "rounds": prof.rounds, "improved_rounds": prof.improved_rounds,
            "budget_seconds": budget, "seconds": round(time.monotonic() - t0, 3),
            "n_witness_sets": len(wsets), "n_cliques": len(cliques)}


def run_ceiling(which: str, workers: int, wall: float | None, rng_seed: int = 1,
                budget_scale: float = 1.0, limit: int | None = None) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    names = target_names(which)
    if limit:
        names = names[:limit]
    done = set(pd.read_csv(CEILING_CSV)["instance_name"]) if CEILING_CSV.exists() else set()
    todo = [nm for nm in names if nm not in done]
    inst = corpus_instances()
    jobs = []
    for nm in sorted(todo, key=lambda x: int(led.loc[x, "n"])):
        matrix = inst[nm][1].matrix.tolist()
        sol = solution_record(nm)
        ordering = sol.get("ordering") if sol else None
        n = int(led.loc[nm, "n"])
        jobs.append((nm, matrix, ordering, int(led.loc[nm, "optimum"]), ceiling_budget(n) * budget_scale, rng_seed))
    log(f"ceiling: targets {which}: {len(names)} names, {len(done)} on file, {len(jobs)} to run; "
        f"{workers} workers; budget 0.005 n² s in [2, 90] × {budget_scale}; rng seed {rng_seed}")
    t0 = time.monotonic()
    rows: list[dict] = []
    with Pool(workers) as pool:
        for k, row in enumerate(pool.imap_unordered(_ceiling_job, jobs, chunksize=1), 1):
            rows.append(row)
            if k % 250 == 0 or k == len(jobs):
                pd.DataFrame(rows).to_csv(CEILING_CSV, mode="a", header=not CEILING_CSV.exists(), index=False)
                rows = []
                log(f"ceiling: {k}/{len(jobs)} done, {time.monotonic() - t0:.0f} s wall")
            if wall is not None and time.monotonic() - t0 > wall:
                log("ceiling: wall reached; stopping (the rest is not in the file)")
                pool.terminate()
                break
    if rows:
        pd.DataFrame(rows).to_csv(CEILING_CSV, mode="a", header=not CEILING_CSV.exists(), index=False)
    out = pd.read_csv(CEILING_CSV).drop_duplicates("instance_name", keep="last")
    out.to_csv(CEILING_CSV, index=False)
    bad = out[out["ceiling"] > out["optimum"]]
    if not bad.empty:
        log(f"BUG: ceiling above the optimum on {len(bad)} instances: {bad['instance_name'].tolist()[:5]}")
    return out


# ----------------------------------------------------------------------------
# stage: exact at n <= 22
# ----------------------------------------------------------------------------


def _exact_job(args) -> dict:
    name, matrix, optimum = args
    closed = closed_masks_from_matrix(matrix)
    n = len(closed)
    prof = exact_profile(closed)
    exact_bound, t_star = prof.harper()
    rec = {"instance_name": name, "n": n, "optimum": int(optimum), "exact_bound": int(exact_bound),
           "exact_t_star": int(t_star), "s_star": int(prof.s_hat()), "empty_exact": int(prof.empty_pair()),
           "f": ",".join(str(x) for x in prof.values), "exact_seconds": round(prof.seconds, 4)}
    path = SETS_DIR / f"{safe_name(name)}.json"
    if path.exists():
        srec = json.loads(path.read_text())
        fhat = srec["fhat"]
        rec["ceiling"] = int(srec["ceiling"])
        rec["levels_total"] = n - 1
        rec["levels_mismatch"] = sum(1 for t in range(1, n) if fhat[t] != prof.values[t])
        rec["all_levels_match"] = rec["levels_mismatch"] == 0
        rec["max_level_excess"] = max((fhat[t] - prof.values[t] for t in range(1, n)), default=0)
        srec["f_exact"] = prof.values
        srec["exact_sets"] = {str(t): mask_to_list(prof.sets[t]) for t in range(1, n + 1)}
        path.write_text(json.dumps(srec))
    return rec


def run_exact(workers: int, limit: int | None = None) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    names = target_names("small")
    if limit:
        names = names[:limit]
    inst = corpus_instances()
    jobs = [(nm, inst[nm][1].matrix.tolist(), int(led.loc[nm, "optimum"])) for nm in names]
    log(f"exact: {len(jobs)} instances at n <= {EXACT_MAX_N}, {workers} workers")
    t0 = time.monotonic()
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_exact_job, jobs, chunksize=8))
    out = pd.DataFrame(rows).sort_values("instance_name")
    out["ceiling_eq_exact"] = out.get("ceiling", np.nan) == out["exact_bound"]
    out["exact_eq_optimum"] = out["exact_bound"] == out["optimum"]
    out["empty_eq_optimum"] = out["empty_exact"] == out["optimum"]
    out["harper12"] = led.loc[out["instance_name"], "harper12"].values
    out["lb_best"] = led.loc[out["instance_name"], "lb_best"].values
    out["floor0"] = led.loc[out["instance_name"], "floor0"].values
    out.to_csv(EXACT_CSV, index=False)
    log(f"exact: wrote {EXACT_CSV.relative_to(ROOT)} ({len(out)} rows) in {time.monotonic() - t0:.0f} s")
    bad = out[out["exact_bound"] > out["optimum"]]
    if not bad.empty:
        log(f"VIOLATION: exact Harper bound above the optimum on {len(bad)} instances: "
            f"{bad['instance_name'].tolist()[:5]}")
    return out


# ----------------------------------------------------------------------------
# stage: floor (the cap-12 branch and bound where item 01 censored it)
# ----------------------------------------------------------------------------


def _floor_job(args) -> dict:
    name, matrix, cap, budget = args
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound

    inst = MOSPInstance.from_matrix(np.asarray(matrix, dtype=int), name=name)
    t0 = time.monotonic()
    b = expansion_bound(inst, max_t=cap, time_budget=budget)
    return {"instance_name": name, "floor": int(b.value), "floor_cap": int(b.cap), "floor_complete": bool(b.complete),
            "floor_budget": budget, "floor_seconds": round(time.monotonic() - t0, 3),
            "floor_levels": ",".join(str(x) for x in b.levels)}


def run_floor(which: str, workers: int, wall: float | None) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    names = target_names(which)
    cens = [nm for nm in names if not bool(led.loc[nm, "harper12_complete"])]
    done = set(pd.read_csv(FLOOR_CSV)["instance_name"]) if FLOOR_CSV.exists() else set()
    todo = [nm for nm in cens if nm not in done]
    inst = corpus_instances()
    jobs = []
    for nm in sorted(todo, key=lambda x: int(led.loc[x, "harper12_cap"])):
        cap0 = int(led.loc[nm, "harper12_cap"])
        budget = FLOOR_BUDGET_LOW_CAP if cap0 <= HARPER_CAP - 2 else FLOOR_BUDGET_HIGH_CAP
        jobs.append((nm, inst[nm][1].matrix.tolist(), HARPER_CAP, budget))
    log(f"floor: targets {which}: {len(names)} names, {len(cens)} censored by item 01 at 60 s, {len(done)} on file, "
        f"{len(jobs)} to run; cap {HARPER_CAP}; budget {FLOOR_BUDGET_LOW_CAP:.0f} s where item 01's cap <= 10, "
        f"{FLOOR_BUDGET_HIGH_CAP:.0f} s at cap 11; {workers} workers")
    t0 = time.monotonic()
    rows: list[dict] = []
    with Pool(workers) as pool:
        for k, row in enumerate(pool.imap_unordered(_floor_job, jobs, chunksize=1), 1):
            rows.append(row)
            pd.DataFrame([row]).to_csv(FLOOR_CSV, mode="a", header=not FLOOR_CSV.exists(), index=False)
            log(f"floor: {k}/{len(jobs)} {row['instance_name']}: {row['floor']} cap {row['floor_cap']} "
                f"complete {row['floor_complete']} {row['floor_seconds']:.0f} s ({time.monotonic() - t0:.0f} s wall)")
            if wall is not None and time.monotonic() - t0 > wall:
                log("floor: wall reached; stopping")
                pool.terminate()
                break
    out = pd.read_csv(FLOOR_CSV).drop_duplicates("instance_name", keep="last")
    out = out.merge(led.reset_index()[["instance_name", "n", "optimum", "harper12", "harper12_cap", "floor0"]],
                    on="instance_name", how="left")
    if CEILING_CSV.exists():
        c = pd.read_csv(CEILING_CSV)[["instance_name", "ceiling"]]
        out = out.merge(c, on="instance_name", how="left")
    out.to_csv(FLOOR_CSV, index=False)
    bad = out[out["floor"] > out["optimum"]]
    if not bad.empty:
        log(f"VIOLATION: floor above the optimum on {len(bad)} instances: {bad['instance_name'].tolist()}")
    if "ceiling" in out:
        bad = out[out["floor"] > out["ceiling"]]
        if not bad.empty:
            log(f"BUG: floor above the ceiling on {len(bad)} instances: {bad['instance_name'].tolist()}")
    return out


# ----------------------------------------------------------------------------
# stage: tables
# ----------------------------------------------------------------------------


def joined() -> pd.DataFrame:
    """The ceiling rows joined with the ledger and the floor: per instance the
    family's floor (`harper_floor` = the floor rerun where it exists, else
    item 01's `harper12`), the ceiling, the gaps and the bracket."""
    led = ledger()
    c = pd.read_csv(CEILING_CSV).drop_duplicates("instance_name", keep="last")
    f = c.drop(columns=["n", "optimum"]).merge(led, on="instance_name", how="left")
    f["harper_floor"] = f["harper12"].astype(float)
    f["harper_floor_cap"] = f["harper12_cap"].astype(float)
    f["harper_floor_complete"] = f["harper12_complete"].astype(object)
    if FLOOR_CSV.exists():
        fl = pd.read_csv(FLOOR_CSV)[["instance_name", "floor", "floor_cap", "floor_complete", "floor_seconds"]]
        f = f.merge(fl, on="instance_name", how="left")
        m = f["floor"].notna()
        f.loc[m, "harper_floor"] = np.maximum(f.loc[m, "floor"], f.loc[m, "harper12"])
        f.loc[m, "harper_floor_cap"] = f.loc[m, "floor_cap"]
        f.loc[m, "harper_floor_complete"] = f.loc[m, "floor_complete"]
    f["harper_floor"] = f["harper_floor"].astype(int)
    f["gap_ceiling"] = f["optimum"] - f["ceiling"]
    f["gap_floor"] = f["optimum"] - f["harper_floor"]
    f["bracket"] = f["ceiling"] - f["harper_floor"]
    f["ceiling_at_optimum"] = f["gap_ceiling"] == 0
    f["ceiling_below_optimum"] = f["gap_ceiling"] > 0
    f["floor_tight"] = f["gap_floor"] == 0
    f["t_star_frac"] = f["t_star"] / f["n"]
    f["is_rest500"] = f["instance_name"].isin(set(load_targets()["rest500"]))
    return f


def _md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False, floatfmt=".2f")


def _summary(g: pd.DataFrame) -> dict:
    return {"instances": len(g), "mean n": g["n"].mean(), "mean optimum": g["optimum"].mean(),
            "ceiling gap mean": g["gap_ceiling"].mean(), "ceiling gap max": g["gap_ceiling"].max(),
            "ceiling at optimum": int(g["ceiling_at_optimum"].sum()),
            "ceiling below optimum": int(g["ceiling_below_optimum"].sum()),
            "floor gap mean": g["gap_floor"].mean(), "floor gap max": g["gap_floor"].max(),
            "floor tight": int(g["floor_tight"].sum()),
            "bracket mean": g["bracket"].mean(), "bracket 0": int((g["bracket"] == 0).sum()),
            "floor above lb_best": int((g["harper_floor"] > g["lb_best"]).sum()),
            "floor above floor0 ref": int((g["harper_floor"] > np.maximum(g["lb_best"], g["tw1"])).sum()),
            "t*/n median": g["t_star_frac"].median(), "ms median": 1000 * g["seconds"].median(),
            "ms max": 1000 * g["seconds"].max()}


def write_tables() -> str:
    f = joined()
    lines = ["# Item 02 tables (generated by `python3 -m learning.obstruction_expansion --stage tables`)", ""]
    lines += ["Units: optimum units (`pathwidth + 1`); gap = optimum − value; the ceiling is not a bound.", ""]
    sets = [("gap338", f["is_gap338"]), ("cs200", f["is_cs200"]), ("rest500", f["is_rest500"]), ("small", f["is_small"]),
            ("all targets", f["instance_name"].notna())]
    rows = []
    for nm, m in sets:
        d = _summary(f[m])
        d = {"target": nm, **d}
        rows.append(d)
    lines += ["## (a) per target set", "", _md(pd.DataFrame(rows)), ""]
    rows = []
    for lo, hi in BANDS:
        g = f[(f["n"] >= lo) & (f["n"] <= hi)]
        if len(g):
            rows.append({"band": f"{lo}–{hi}", **_summary(g)})
    lines += ["## (b) per size band, all targets", "", _md(pd.DataFrame(rows)), ""]
    g = f[f["is_gap338"]]
    rows = []
    for lo, hi in BANDS:
        h = g[(g["n"] >= lo) & (g["n"] <= hi)]
        if len(h):
            rows.append({"band": f"{lo}–{hi}", **_summary(h)})
    lines += ["## (c) the 338 per band", "", _md(pd.DataFrame(rows)), ""]
    closed_by_floor = int(g["floor_tight"].sum())
    ruled_out = int(g["ceiling_below_optimum"].sum())
    lines += [f"On the 338: the floor closes {closed_by_floor}; the ceiling rules out {ruled_out} "
              f"(the family can never close these); {int(((~g['floor_tight']) & (~g['ceiling_below_optimum'])).sum())} "
              f"are open between floor and ceiling; the floor is above `lb_best` on "
              f"{int((g['harper_floor'] > g['lb_best']).sum())} and above `max(lb_best, tw + 1)` on "
              f"{int((g['harper_floor'] > np.maximum(g['lb_best'], g['tw1'])).sum())}.", ""]
    cs = f[f["is_cs200"]].copy()
    cs["class"] = [f"{int(a)}-{int(b)}-{int(c)}" for a, b, c in zip(cs["cs_n"], cs["cs_m"], cs["cs_d"])]
    rows = []
    for cls, h in cs.groupby("class", sort=False):
        rows.append({"class": cls, **_summary(h)})
    rows.sort(key=lambda r: (int(r["class"].split("-")[0]), int(r["class"].split("-")[2])))
    lines += ["## (d) the 200 Chu & Stuckey by class", "", _md(pd.DataFrame(rows)), ""]
    for path in sorted(OUT.glob("ceiling_*.csv")):
        tag = path.stem[len("ceiling_"):]
        c2 = pd.read_csv(path).drop_duplicates("instance_name", keep="last")[["instance_name", "ceiling", "seconds", "budget_seconds"]]
        c2 = c2.rename(columns={"ceiling": "ceiling2", "seconds": "seconds2", "budget_seconds": "budget2"})
        j = f.merge(c2, on="instance_name", how="inner")
        rows = []
        for lo, hi in BANDS:
            h = j[(j["n"] >= lo) & (j["n"] <= hi)]
            if len(h):
                rows.append({"band": f"{lo}–{hi}", "instances": len(h), "second pass lower": int((h["ceiling2"] < h["ceiling"]).sum()),
                             "second pass higher": int((h["ceiling2"] > h["ceiling"]).sum()),
                             "max drop": int((h["ceiling"] - h["ceiling2"]).max()),
                             "min(ceilings) below optimum": int((np.minimum(h["ceiling"], h["ceiling2"]) < h["optimum"]).sum()),
                             "seconds median pass 1": h["seconds"].median(), "seconds median pass 2": h["seconds2"].median(),
                             "budget pass 2": h["budget2"].median()})
        lines += [f"## (g) the second search pass `{tag}` against the first, on the instances it covers", "",
                  _md(pd.DataFrame(rows)), ""]
    if FLOOR_CSV.exists():
        fl = pd.read_csv(FLOOR_CSV)
        cols = [c for c in ("instance_name", "n", "optimum", "harper12", "harper12_cap", "floor", "floor_cap",
                            "floor_complete", "floor_seconds", "ceiling", "floor0") if c in fl.columns]
        lines += ["## (e) the floor rerun on the instances item 01 censored", "", fl[cols].to_markdown(index=False), ""]
    if EXACT_CSV.exists():
        e = pd.read_csv(EXACT_CSV)
        d = {"instances": len(e), "search = exact at every t": int(e["all_levels_match"].sum()),
             "share": e["all_levels_match"].mean(), "ceiling = exact bound": int(e["ceiling_eq_exact"].sum()),
             "exact bound = optimum": int(e["exact_eq_optimum"].sum()), "share tight": e["exact_eq_optimum"].mean(),
             "empty-pair = optimum": int(e["empty_eq_optimum"].sum()),
             "exact > harper12 (record)": int((e["exact_bound"] > e["harper12"]).sum()),
             "exact > lb_best": int((e["exact_bound"] > e["lb_best"]).sum()),
             "exact > floor0": int((e["exact_bound"] > e["floor0"]).sum()),
             "max level excess": int(e["max_level_excess"].max()), "exact ms median": 1000 * e["exact_seconds"].median()}
        lines += ["## (f) exact at n <= 22 (targets.small)", "", _md(pd.DataFrame([d])), ""]
        rows = []
        for n, h in e.groupby("n"):
            rows.append({"n": n, "instances": len(h), "search exact at every t": h["all_levels_match"].mean(),
                         "Harper tight": h["exact_eq_optimum"].mean(), "empty-pair tight": h["empty_eq_optimum"].mean(),
                         "mean gap exact": (h["optimum"] - h["exact_bound"]).mean(),
                         "mean gap lb_best": (h["optimum"] - h["lb_best"]).mean()})
        lines += ["### (f2) by n", "", _md(pd.DataFrame(rows)), ""]
    text = "\n".join(lines)
    TABLES_MD.write_text(text)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("ceiling", "exact", "floor", "tables"), required=True)
    ap.add_argument("--targets", default="all")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--budget-scale", type=float, default=1.0)
    ap.add_argument("--tag", default="", help="write ceiling_<tag>.csv and sets_<tag>/ (a second search pass)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.tag:
        global CEILING_CSV, SETS_DIR
        CEILING_CSV = OUT / f"ceiling_{args.tag}.csv"
        SETS_DIR = OUT / f"sets_{args.tag}"
    if args.stage == "ceiling":
        out = run_ceiling(args.targets, args.workers, args.wall, args.seed, args.budget_scale, args.limit)
        log(f"ceiling: {len(out)} rows on file; ceiling = optimum on {int((out['ceiling'] == out['optimum']).sum())}, "
            f"below on {int((out['ceiling'] < out['optimum']).sum())}, above (BUG) on "
            f"{int((out['ceiling'] > out['optimum']).sum())}; {out['seconds'].sum() / 3600:.2f} core-hours")
    elif args.stage == "exact":
        out = run_exact(args.workers, args.limit)
        log(f"exact: search attains f at every t on {int(out['all_levels_match'].sum())}/{len(out)}; "
            f"Harper exact = optimum on {int(out['exact_eq_optimum'].sum())}")
    elif args.stage == "floor":
        out = run_floor(args.targets, args.workers, args.wall)
        log(f"floor: {len(out)} rows; {out['floor_seconds'].sum() / 3600:.2f} core-hours")
    else:
        print(write_tables())


if __name__ == "__main__":
    main()
