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
    nice -n 19 python3 -m learning.obstruction_expansion --stage sat --targets gap338,cs200 --workers 8 --core-hours 6
    python3 -m learning.obstruction_expansion --stage sat-tables

**Item 03, the exact half above cap 12** (`exact_sat`, stage `sat`): the
decision "no `t`-set has `|N[C]| <= b`" as a CNF (`expansion_cnf`, the
contract in `ENCODING_SPEC`, shared with `paper1/obstruction_check.py` and
with nothing else), CaDiCaL 1.9.5 through pysat with proof logging under a
conflict budget and a wall deadline, drat-trim on every UNSAT; an UNSAT at
`(t, b)` proves `f(t) >= b + 1` (the contrapositive of
`exists_closedNbhd_card_le`) and a SAT answer is a set that lowers the
ceiling. The certificate per proved level is the CNF's SHA-256, `(t, b)`,
the gzipped DRAT proof and the checker's verdict, under
`reports/scratch/obstruction_search/03_sat/certificates/<instance>/`.

Nothing here solves an instance: every optimum is read from the record
(`reports/scratch/obstruction_search/01_ledger/ledger_corpus.csv`), the
witness from `solutions/<name>.json` (read only), and the only new exact
computations are subset enumerations at `n <= 22` and the cap-12 branch and
bound on the 35 instances item 01 censored at 60 s.
"""
from __future__ import annotations

import os

# The `sat` stage forks one child per SAT call from a pool worker (a deadline
# pysat cannot enforce); a fork from a process with BLAS thread pools is the
# hazard `tests/conftest.py` documents, so the limits are set before numpy loads.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import argparse
import ctypes
import gzip
import hashlib
import json
import signal
import sys
import tempfile
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
# item 03: the exact inner minimum by SAT with DRAT
# ----------------------------------------------------------------------------

ENCODING_SPEC = """expansion-cnf-1 — the decision "some C with |C| >= t has |N[C]| <= b".

Vertices 0..n-1 (customers in file order); N[u] is the closed neighbourhood in
the MOSP graph (a clique per pattern, plus u itself). Variables, 1-based:
  x_v = v + 1          (v in C)
  y_v = n + v + 1      (v in N[C])
  auxiliaries from 2n + 1 upward, in the order the totalizers allocate them.
Clauses:
  (1) for every u, for every v in N[u] (including v = u): [-x_u, y_v];
  (2) a full totalizer over [x_0, ..., x_{n-1}] (allocated first), with the unit
      clause [o_t] on its root outputs (o_1..o_n; 1 <= t <= n);
  (3) a full totalizer over [y_0, ..., y_{n-1}] (allocated second), with the unit
      clause [-o_{b+1}] on its root outputs (0 <= b <= n - 1).
The totalizer of a list L of literals: one literal is its own output (no
clauses, no variables); otherwise split A = L[:len(L)//2], B = L[len(L)//2:],
build A's totalizer, then B's, then allocate the node's outputs o_1..o_{p+q}
(p = |A|, q = |B|) as fresh consecutive variables; with a_0 = b_0 = true and
a_{p+1} = b_{q+1} = false (omitted literals), add for every i in 0..p and
j in 0..q:  [-a_i, -b_j, o_{i+j}] when i + j >= 1, and
            [a_{i+1}, b_{j+1}, -o_{i+j+1}] when i + j + 1 <= p + q.
Canonical form: literals within a clause sorted by integer value, duplicate
clauses removed, clauses sorted lexicographically; the DIMACS text is
"p cnf <nv> <m>" then one clause per line ending in " 0", "\\n" line ends; the
CNF's SHA-256 is of that text. UNSAT proves f(t) = min_{|C| = t} |N[C]| >= b + 1,
hence pathwidth >= b + 1 - t and MOSP >= b + 2 - t
(`exists_closedNbhd_card_le`, contrapositive).
"""

SAT_OUT = ROOT / "reports" / "scratch" / "obstruction_search" / "03_sat"
SAT_LEVELS_CSV = SAT_OUT / "levels.csv"
SAT_INSTANCES_CSV = SAT_OUT / "instances.csv"
SAT_BOUNDARY_CSV = SAT_OUT / "boundary.csv"
SAT_CERT_DIR = SAT_OUT / "certificates"
SAT_TABLES_MD = SAT_OUT / "tables.md"
SAT_RUN_LOG = SAT_OUT / "run.log"
SAT_CONFLICTS = 2_000_000
SAT_DEADLINE = 120.0
SAT_MAX_LEVELS = 8
SAT_INSTANCE_BUDGET = 240.0
PROOF_KEEP_BYTES = 50 * 2 ** 20
SAT_BACKEND = "cadical195"
ENCODING_NAME = "expansion-cnf-1"
THEOREM = "MOSPFormalization.EmptyPair.exists_closedNbhd_card_le (contrapositive)"


def slog(msg: str) -> None:
    SAT_OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(SAT_RUN_LOG, "a") as handle:
        handle.write(line + "\n")


def _totalizer(lits: list[int], next_var: int, clauses: list[list[int]]) -> tuple[list[int], int]:
    """Full totalizer (Bailleux & Boufkhad 2003) as `ENCODING_SPEC` fixes it;
    returns the root outputs `o_1..o_m` and the next free variable."""
    if len(lits) == 1:
        return [lits[0]], next_var
    half = len(lits) // 2
    a, next_var = _totalizer(lits[:half], next_var, clauses)
    b, next_var = _totalizer(lits[half:], next_var, clauses)
    p, q = len(a), len(b)
    out = list(range(next_var, next_var + p + q))
    next_var += p + q
    for i in range(p + 1):
        for j in range(q + 1):
            if i + j >= 1:
                cl = []
                if i >= 1:
                    cl.append(-a[i - 1])
                if j >= 1:
                    cl.append(-b[j - 1])
                cl.append(out[i + j - 1])
                clauses.append(cl)
            if i + j + 1 <= p + q:
                cl = []
                if i + 1 <= p:
                    cl.append(a[i])
                if j + 1 <= q:
                    cl.append(b[j])
                cl.append(-out[i + j])
                clauses.append(cl)
    return out, next_var


def expansion_cnf(closed: list[int], t: int, b: int) -> tuple[list[list[int]], int]:
    """The canonical CNF of `ENCODING_SPEC` for "some |C| >= t has |N[C]| <= b"."""
    n = len(closed)
    if not 1 <= t <= n or not 0 <= b <= n - 1:
        raise ValueError(f"need 1 <= t <= n and 0 <= b <= n - 1, got n={n}, t={t}, b={b}")
    x = [v + 1 for v in range(n)]
    y = [n + v + 1 for v in range(n)]
    clauses: list[list[int]] = []
    for u in range(n):
        for v in mask_to_list(closed[u]):
            clauses.append([-x[u], y[v]])
    next_var = 2 * n + 1
    ox, next_var = _totalizer(x, next_var, clauses)
    clauses.append([ox[t - 1]])
    oy, next_var = _totalizer(y, next_var, clauses)
    clauses.append([-oy[b]])
    canon = sorted({tuple(sorted(cl)) for cl in clauses})
    return [list(cl) for cl in canon], next_var - 1


def cnf_dimacs_bytes(clauses: list[list[int]], nv: int) -> bytes:
    lines = [f"p cnf {nv} {len(clauses)}"]
    lines.extend(" ".join(map(str, cl)) + " 0" for cl in clauses)
    return ("\n".join(lines) + "\n").encode()


def cnf_sha256(clauses: list[list[int]], nv: int) -> str:
    return hashlib.sha256(cnf_dimacs_bytes(clauses, nv)).hexdigest()


def matrix_sha256(matrix) -> str:
    """SHA-256 of the 0/1 rows as the standard `.mosp` format writes them."""
    matrix = np.asarray(matrix, dtype=int)
    text = "".join(" ".join(str(int(v)) for v in row) + "\n" for row in matrix)
    return hashlib.sha256(text.encode()).hexdigest()


def write_standard_instance(path: Path, name: str, matrix) -> None:
    matrix = np.asarray(matrix, dtype=int)
    lines = [name, f"{matrix.shape[0]} {matrix.shape[1]}"]
    lines += [" ".join(str(int(v)) for v in row) for row in matrix]
    path.write_text("\n".join(lines) + "\n")


def _drat_trim_path() -> Path:
    from learning.proofs import DRAT_TRIM
    return (ROOT / DRAT_TRIM) if not DRAT_TRIM.is_absolute() else DRAT_TRIM


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _solve_cnf(clauses: list[list[int]], conflicts: int | None, want_proof: bool) -> dict:
    """One CaDiCaL call in this process: answer, model, proof bytes, stats."""
    from pysat.solvers import Solver
    from learning.proofs import _read_proof

    solver = Solver(name=SAT_BACKEND, bootstrap_with=clauses, with_proof=want_proof)
    t0 = time.monotonic()
    try:
        if conflicts is not None:
            solver.conf_budget(int(conflicts))
            answer = solver.solve_limited()
        else:
            answer = solver.solve()
        seconds = time.monotonic() - t0
        stats = solver.accum_stats() or {}
        model = solver.get_model() if answer is True else None
        proof = _read_proof(solver) if (answer is False and want_proof) else b""
    finally:
        solver.delete()
    return {"answer": answer, "model": model, "proof": proof, "seconds": seconds,
            "conflicts": int(stats.get("conflicts", 0)), "decisions": int(stats.get("decisions", 0))}


def _sat_set_from_model(closed: list[int], model: list[int], t: int, b: int) -> tuple[list[int], int]:
    """The `t`-set a model gives: the first `t` vertices with `x_v` true (a
    subset of `C` has a closed neighbourhood inside `N[C]`); its `|N[·]|` is
    recomputed from the masks and never read from the `y` variables."""
    n = len(closed)
    C = [v for v in range(n) if model[v] > 0]
    if len(C) < t:
        raise RuntimeError(f"model has {len(C)} < t = {t} members: encoding bug")
    full = 0
    for v in C:
        full |= 1 << v
    if neighbourhood_size(closed, full) > b:
        raise RuntimeError("model's |N[C]| exceeds b: encoding bug")
    sub = 0
    for v in C[:t]:
        sub |= 1 << v
    return C[:t], neighbourhood_size(closed, sub)


def _exact_sat_inprocess(closed, t, b, proof_dir, conflicts, instance_name, matrix_sha, source_file) -> dict:
    clauses, nv = expansion_cnf(closed, t, b)
    digest = cnf_sha256(clauses, nv)
    res = _solve_cnf(clauses, conflicts, want_proof=proof_dir is not None)
    out = {"instance_name": instance_name, "n": len(closed), "t": t, "b": b, "cnf_variables": nv,
           "cnf_clauses": len(clauses), "cnf_sha256": digest, "solve_seconds": round(res["seconds"], 3),
           "conflicts": res["conflicts"], "decisions": res["decisions"], "conflict_budget": conflicts,
           "status": "budget" if res["answer"] is None else ("unsat" if res["answer"] is False else "sat"),
           "set": None, "nbhd": None, "proof_sha256": "", "proof_bytes": 0, "proof_gz_bytes": 0,
           "proof_kept": False, "proof_lemmas": 0, "verdict": "", "check_seconds": 0.0, "certificate": ""}
    if res["answer"] is True:
        out["set"], out["nbhd"] = _sat_set_from_model(closed, res["model"], t, b)
    elif res["answer"] is False and proof_dir is not None:
        from learning.proofs import check_proof, check_timeout_for, count_lemmas
        proof = res["proof"]
        proof_dir = Path(proof_dir)
        proof_dir.mkdir(parents=True, exist_ok=True)
        stem = f"t{t}_b{b}"
        out["proof_sha256"] = hashlib.sha256(proof).hexdigest()
        out["proof_bytes"] = len(proof)
        out["proof_lemmas"] = count_lemmas(proof)
        gz_path = proof_dir / f"{stem}.drat.gz"
        with gzip.open(gz_path, "wb", compresslevel=6) as fh:
            fh.write(proof)
        out["proof_gz_bytes"] = gz_path.stat().st_size
        with tempfile.TemporaryDirectory() as tmp:
            cnf_path, proof_path = Path(tmp) / "f.cnf", Path(tmp) / "p.drat"
            cnf_path.write_bytes(cnf_dimacs_bytes(clauses, nv))
            proof_path.write_bytes(proof)
            verdict, secs, _tail = check_proof(cnf_path, proof_path, _drat_trim_path(),
                                               check_timeout_for(res["seconds"]))
        out["verdict"], out["check_seconds"] = verdict, secs
        out["proof_kept"] = out["proof_gz_bytes"] <= PROOF_KEEP_BYTES
        if not out["proof_kept"]:
            gz_path.unlink(missing_ok=True)
        import pysat
        cert = {"format": "obstruction-expansion-certificate-1", "encoding": ENCODING_NAME,
                "instance_name": instance_name, "source_file": source_file, "n": len(closed),
                "matrix_sha256": matrix_sha, "instance_file": "instance.mosp", "t": t, "b": b,
                "claim": f"f({t}) = min over |C| = {t} of |N[C]| >= {b + 1}",
                "bound_pathwidth": b + 1 - t, "bound_mosp": b + 2 - t, "theorem": THEOREM,
                "cnf_variables": nv, "cnf_clauses": len(clauses), "cnf_sha256": digest,
                "proof_file": gz_path.name if out["proof_kept"] else None, "proof_sha256": out["proof_sha256"],
                "proof_bytes": len(proof), "proof_gz_bytes": out["proof_gz_bytes"], "proof_lemmas": out["proof_lemmas"],
                "solver": f"{SAT_BACKEND} via pysat {pysat.__version__}", "conflict_budget": conflicts,
                "conflicts": res["conflicts"], "solve_seconds": out["solve_seconds"],
                "checker": "drat-trim", "checker_sha256": _file_sha256(_drat_trim_path()),
                "verdict": verdict, "check_seconds": secs}
        cert_path = proof_dir / f"{stem}.json"
        cert_path.write_text(json.dumps(cert, indent=1, sort_keys=True))
        out["certificate"] = str(cert_path.relative_to(ROOT)) if cert_path.is_relative_to(ROOT) else str(cert_path)
    return out


def exact_sat(closed: list[int], t: int, b: int, proof_dir: Path | str | None = None,
              conflicts: int | None = SAT_CONFLICTS, deadline: float | None = SAT_DEADLINE,
              instance_name: str = "", matrix_sha: str = "", source_file: str = "") -> dict:
    """Decide "some |C| >= t has |N[C]| <= b" (plan §0.5 (d)).

    `closed` are closed-neighbourhood masks. Returns a dict with `status` in
    `unsat` (then `f(t) >= b + 1`; with `proof_dir` the DRAT proof is written,
    checked by drat-trim and a certificate JSON `t<t>_b<b>.json` is left
    there), `sat` (`set`: a `t`-set with `|N[set]| = nbhd <= b`), `budget`
    (the conflict budget ran out) or `timeout` (the wall deadline). pysat's
    CaDiCaL cannot be interrupted, so with a deadline the call runs in a
    forked child that is killed at the deadline; the child dies with its
    parent (`PR_SET_PDEATHSIG`) and has an alarm of its own."""
    if deadline is None:
        return _exact_sat_inprocess(closed, t, b, proof_dir, conflicts, instance_name, matrix_sha, source_file)
    with tempfile.TemporaryDirectory() as tmp:
        result_path = Path(tmp) / "result.json"
        sys.stdout.flush()
        sys.stderr.flush()
        pid = os.fork()
        if pid == 0:  # the child
            try:
                ctypes.CDLL(None).prctl(1, signal.SIGKILL)  # PR_SET_PDEATHSIG
                signal.alarm(int(deadline) + 10)
                out = _exact_sat_inprocess(closed, t, b, proof_dir, conflicts, instance_name, matrix_sha, source_file)
                result_path.write_text(json.dumps(out))
            except BaseException as exc:  # noqa: BLE001
                try:
                    result_path.write_text(json.dumps({"status": "error", "error": f"{type(exc).__name__}: {exc}"[:300]}))
                except Exception:  # noqa: BLE001
                    pass
            finally:
                os._exit(0)
        t0 = time.monotonic()
        killed = False
        while True:
            done, _ = os.waitpid(pid, os.WNOHANG)
            if done:
                break
            if time.monotonic() - t0 > deadline:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
                killed = True
                break
            time.sleep(0.02)
        seconds = time.monotonic() - t0
        if killed or not result_path.exists():
            if proof_dir is not None:
                for suffix in (".drat.gz", ".json"):
                    (Path(proof_dir) / f"t{t}_b{b}{suffix}").unlink(missing_ok=True)
            return {"instance_name": instance_name, "n": len(closed), "t": t, "b": b, "status": "timeout",
                    "solve_seconds": round(seconds, 3), "conflicts": 0, "conflict_budget": conflicts,
                    "set": None, "nbhd": None, "verdict": "", "certificate": "", "cnf_sha256": "",
                    "deadline": deadline}
        out = json.loads(result_path.read_text())
        out["deadline"] = deadline
        return out


def profile_floor(levels: list[int]) -> int:
    """`max_t (f(t) - t) + 1` over the proved levels `f(1..L)`, optimum units; 0 if none."""
    return max((f - t for t, f in enumerate(levels, 1)), default=-1) + 1


def mark_levels(n: int, fhat: list[int], proved: int, floor: int, t_star: int, visited: set[int],
                max_levels: int = SAT_MAX_LEVELS) -> list[int]:
    """The levels the ceiling marks relevant: `t > proved` (below is exact
    already), `t <= n - 1`, not yet visited, and `fhat(t) - t + 1 > floor` —
    a level at or below the floor can neither raise it nor move the bracket
    (the item's `>= floor - 1` in pathwidth units includes equality; equality
    is left out here, as it cannot change either half). Nearest `t*` first."""
    cand = [t for t in range(proved + 1, n) if t not in visited and fhat[t] - t + 1 > floor]
    cand.sort(key=lambda t: (abs(t - t_star), t))
    return cand[:max_levels]


def _sat_job(args) -> dict:
    (name, matrix, source_file, optimum, fhat, incumbents, levels, floor_record, t_star, ceiling_record,
     budget, conflicts, deadline, max_levels) = args
    matrix = np.asarray(matrix, dtype=int)
    n = matrix.shape[0]
    closed = closed_masks(adjacency_from_matrix(matrix))
    msha = matrix_sha256(matrix)
    cert_dir = SAT_CERT_DIR / safe_name(name)
    cert_dir.mkdir(parents=True, exist_ok=True)
    write_standard_instance(cert_dir / "instance.mosp", name, matrix)
    fhat = list(fhat)
    proved = len(levels)
    # the proved levels are exact: the incumbents there are f itself
    for t in range(1, proved + 1):
        fhat[t] = levels[t - 1]
    floor = max(profile_floor(levels), floor_record)
    floor0 = floor
    # f(t) >= b + 1 proved by SAT, per level (the largest b refuted)
    sat_lower: dict[int, int] = {}
    settled: list[int] = []
    partial: list[int] = []
    censored: list[int] = []
    calls: list[dict] = []
    new_sets: dict[str, list[int]] = {}
    t0 = time.monotonic()
    visited: set[int] = set()
    stop_reason = "levels exhausted"
    while True:
        if time.monotonic() - t0 > budget:
            stop_reason = "instance budget"
            break
        marks = mark_levels(n, fhat, proved, floor, t_star, visited, max_levels)
        if not marks or len(visited) >= max_levels:
            break
        t = marks[0]
        visited.add(t)
        lo = max(t, levels[-1] if levels else 1)   # f is monotone: f(t) >= f(L) for t > L
        hi = fhat[t]
        hic = hi
        first = True
        best_cert, best_b = "", -1
        while lo < hi and lo <= hic - 1:
            if time.monotonic() - t0 > budget:
                stop_reason = "instance budget"
                break
            b = hi - 1 if first else (lo + min(hi, hic) - 1) // 2
            first = False
            res = exact_sat(closed, t, b, cert_dir, conflicts, deadline, name, msha, source_file)
            res["instance_name"], res["n"], res["optimum"] = name, n, optimum
            res["lo_before"], res["hi_before"] = lo, hi
            calls.append(res)
            with open(cert_dir / "calls.jsonl", "a") as handle:
                handle.write(json.dumps(res) + "\n")
            if res["status"] == "unsat":
                if res.get("verdict") != "verified":
                    res["note"] = "drat-trim did not verify: the answer is not used"
                    hic = b   # treat as censored at this b
                    continue
                lo = b + 1
                sat_lower[t] = lo
                best_cert, best_b = res["certificate"], b
                floor = max(floor, lo - t + 1)
            elif res["status"] == "sat":
                v = int(res["nbhd"])
                assert v <= b, (name, t, b, v)
                hi = v
                hic = min(hic, hi)
                fhat[t] = v
                new_sets[str(t)] = res["set"]
            else:
                hic = b
        if lo >= hi:
            settled.append(t)
        elif t in sat_lower:
            partial.append(t)
        else:
            censored.append(t)
        if stop_reason == "instance budget":
            break
    seconds = time.monotonic() - t0
    # the ceiling after the run: proved levels are exact, incumbents elsewhere
    prof = Profile(n, fhat, [0] * (n + 1), False)
    ceiling, t_star_after = prof.harper()
    # the family's exact floor: proved levels, SAT-settled levels (f = fhat) and partial UNSATs
    floor_after = floor
    for t in settled:
        floor_after = max(floor_after, fhat[t] - t + 1)
    rec = {"instance_name": name, "n": n, "optimum": optimum, "floor_record": floor_record, "floor_before": floor0,
           "ceiling_record": ceiling_record, "ceiling_after": ceiling, "floor_after": floor_after,
           "bracket_before": ceiling_record - floor0, "bracket_after": ceiling - floor_after,
           "t_star_record": t_star, "t_star_after": t_star_after, "proved_levels_bb": proved,
           "levels_visited": len(visited), "levels_settled": len(settled), "levels_partial": len(partial),
           "levels_censored": len(censored), "settled": ",".join(map(str, sorted(settled))),
           "partial": ",".join(map(str, sorted(partial))), "censored": ",".join(map(str, sorted(censored))),
           "argmax_settled": (t_star_after <= proved) or (t_star_after in settled),
           "calls": len(calls), "calls_unsat": sum(1 for c in calls if c["status"] == "unsat"),
           "calls_sat": sum(1 for c in calls if c["status"] == "sat"),
           "calls_budget": sum(1 for c in calls if c["status"] == "budget"),
           "calls_timeout": sum(1 for c in calls if c["status"] == "timeout"),
           "calls_error": sum(1 for c in calls if c["status"] == "error"),
           "new_incumbents": len(new_sets), "seconds": round(seconds, 3), "budget": budget, "stop_reason": stop_reason}
    (cert_dir / "summary.json").write_text(json.dumps({**rec, "fhat_after": fhat, "sat_lower": sat_lower,
                                                       "new_sets": new_sets}, indent=1))
    return {"instance": rec, "calls": calls}


def _sat_inputs(name: str, led: pd.DataFrame, floors: pd.DataFrame | None) -> dict | None:
    path = SETS_DIR / f"{safe_name(name)}.json"
    if not path.exists():
        return None
    srec = json.loads(path.read_text())
    row = led.loc[name]
    levels_rec = [int(x) for x in str(row["harper12_levels"]).split(",") if x not in ("", "nan")]
    levels = levels_rec
    if floors is not None and name in floors.index:
        fl = [int(x) for x in str(floors.loc[name, "floor_levels"]).split(",") if x not in ("", "nan")]
        if len(fl) > len(levels):
            if fl[:len(levels)] != levels:
                raise RuntimeError(f"{name}: item 01's and item 02's proved levels disagree: {levels} vs {fl}")
            levels = fl
    harper_floor = int(row["harper12"])
    if floors is not None and name in floors.index:
        harper_floor = max(harper_floor, int(floors.loc[name, "floor"]))
    return {"fhat": srec["fhat"], "sets": srec["sets"], "levels": levels, "floor_record": harper_floor,
            "t_star": int(srec["t_star"]), "ceiling_record": int(srec["ceiling"])}


def run_sat(which: str, workers: int, core_hours: float, conflicts: int = SAT_CONFLICTS,
            deadline: float = SAT_DEADLINE, instance_budget: float = SAT_INSTANCE_BUDGET,
            max_levels: int = SAT_MAX_LEVELS, limit: int | None = None) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    floors = pd.read_csv(FLOOR_CSV).drop_duplicates("instance_name", keep="last").set_index("instance_name") \
        if FLOOR_CSV.exists() else None
    names: list[str] = []
    for key in which.split(","):
        for nm in sorted(target_names(key.strip()), key=lambda x: (int(led.loc[x, "n"]), x)):
            if nm not in names:
                names.append(nm)
    done = set(pd.read_csv(SAT_INSTANCES_CSV)["instance_name"]) if SAT_INSTANCES_CSV.exists() else set()
    inst = corpus_instances()
    jobs, skipped = [], []
    for nm in names:
        if nm in done:
            continue
        inp = _sat_inputs(nm, led, floors)
        if inp is None:
            skipped.append(nm)
            continue
        n = int(led.loc[nm, "n"])
        fhat = list(inp["fhat"])
        for t in range(1, len(inp["levels"]) + 1):
            fhat[t] = inp["levels"][t - 1]
        floor = max(profile_floor(inp["levels"]), inp["floor_record"])
        if not mark_levels(n, fhat, len(inp["levels"]), floor, inp["t_star"], set(), max_levels):
            skipped.append(nm)   # bracket 0: nothing a SAT call could change
            continue
        path, instance = inst[nm]
        jobs.append((nm, instance.matrix.tolist(), str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                     int(led.loc[nm, "optimum"]), fhat, inp["sets"], inp["levels"], inp["floor_record"],
                     inp["t_star"], inp["ceiling_record"], instance_budget, conflicts, deadline, max_levels))
    if limit:
        jobs = jobs[:limit]
    slog(f"sat: targets {which}: {len(names)} names, {len(done)} on file, {len(skipped)} with no level to ask "
         f"(bracket 0 or no item 02 record), {len(jobs)} to run; {workers} workers; {core_hours} core-hours; "
         f"conflicts {conflicts}, deadline {deadline} s, {instance_budget} s per instance, {max_levels} levels")
    SAT_CERT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    wall_cap = core_hours * 3600.0 / max(1, workers)
    k = 0
    with Pool(workers) as pool:
        for out in pool.imap_unordered(_sat_job, jobs, chunksize=1):
            k += 1
            rec, calls = out["instance"], out["calls"]
            pd.DataFrame([rec]).to_csv(SAT_INSTANCES_CSV, mode="a", header=not SAT_INSTANCES_CSV.exists(), index=False)
            if calls:
                cols = ["instance_name", "n", "optimum", "t", "b", "lo_before", "hi_before", "status", "nbhd",
                        "cnf_variables", "cnf_clauses", "cnf_sha256", "solve_seconds", "conflicts", "conflict_budget",
                        "deadline", "proof_bytes", "proof_gz_bytes", "proof_kept", "proof_lemmas", "verdict",
                        "check_seconds", "certificate"]
                df = pd.DataFrame(calls)
                for c in cols:
                    if c not in df.columns:
                        df[c] = None
                df[cols].to_csv(SAT_LEVELS_CSV, mode="a", header=not SAT_LEVELS_CSV.exists(), index=False)
            slog(f"sat: {k}/{len(jobs)} {rec['instance_name']} (n={rec['n']}): floor {rec['floor_before']} -> "
                 f"{rec['floor_after']}, ceiling {rec['ceiling_record']} -> {rec['ceiling_after']}, bracket "
                 f"{rec['bracket_before']} -> {rec['bracket_after']}, settled {rec['levels_settled']} partial "
                 f"{rec['levels_partial']} censored {rec['levels_censored']} of {rec['levels_visited']}, "
                 f"{rec['calls']} calls, {rec['seconds']:.0f} s [{rec['stop_reason']}] "
                 f"({time.monotonic() - t0:.0f} s wall)")
            if time.monotonic() - t0 > wall_cap:
                slog(f"sat: core-hour cap reached ({core_hours} core-hours = {wall_cap:.0f} s wall at {workers} workers); "
                     f"stopping with {len(jobs) - k} instances not reached")
                pool.terminate()
                break
    out = pd.read_csv(SAT_INSTANCES_CSV).drop_duplicates("instance_name", keep="last")
    out.to_csv(SAT_INSTANCES_CSV, index=False)
    bad = out[out["floor_after"] > out["optimum"]]
    if not bad.empty:
        slog(f"VIOLATION: SAT floor above the optimum on {len(bad)}: {bad['instance_name'].tolist()}")
    bad = out[out["floor_after"] > out["ceiling_after"]]
    if not bad.empty:
        slog(f"BUG: floor above the ceiling on {len(bad)}: {bad['instance_name'].tolist()}")
    return out


def write_sat_tables() -> str:
    inst = pd.read_csv(SAT_INSTANCES_CSV).drop_duplicates("instance_name", keep="last")
    calls = pd.read_csv(SAT_LEVELS_CSV) if SAT_LEVELS_CSV.exists() else pd.DataFrame()
    led = ledger()
    f = joined()  # item 02's per-instance view (ceiling, harper_floor, bracket, flags)
    tg = load_targets()
    inst = inst.rename(columns={"seconds": "sat_seconds"})
    keep = ["instance_name", "ceiling_after", "floor_after", "bracket_after", "levels_settled", "levels_partial",
            "levels_censored", "argmax_settled", "calls", "sat_seconds", "stop_reason", "new_incumbents"]
    m = f.merge(inst[keep], on="instance_name", how="left")
    m["reached"] = m["ceiling_after"].notna()
    m["floor_exact"] = np.where(m["reached"], m["floor_after"], m["harper_floor"]).astype(int)
    m["ceiling_exact"] = np.where(m["reached"], m["ceiling_after"], m["ceiling"]).astype(int)
    m["bracket_exact"] = m["ceiling_exact"] - m["floor_exact"]
    m["gap_floor_exact"] = m["optimum"] - m["floor_exact"]
    m["gap_ceiling_exact"] = m["optimum"] - m["ceiling_exact"]
    m["closed_by_floor"] = m["floor_exact"] == m["optimum"]
    m["ruled_out"] = m["ceiling_exact"] < m["optimum"]
    m["open_bracket"] = (~m["closed_by_floor"]) & (~m["ruled_out"])
    lines = ["# Item 03 tables (generated by `python3 -m learning.obstruction_expansion --stage sat-tables`)", "",
             "Units: optimum units; gap = optimum − value; the ceiling is not a bound; `floor_exact` = the "
             "cap-12 floor raised by every SAT-proved level; `bracket_exact` = ceiling − floor after the run.", ""]

    def summ(g):
        return {"instances": len(g), "had bracket": int((g["bracket"] > 0).sum()), "reached": int(g["reached"].sum()),
                "bracket closed": int(((g["bracket"] > 0) & (g["bracket_exact"] == 0)).sum()),
                "bracket open": int((g["bracket_exact"] > 0).sum()),
                "argmax settled (of had bracket)": int(((g["bracket"] > 0) & (g["argmax_settled"] == True)).sum()),  # noqa: E712
                "floor raised": int((g["floor_exact"] > g["harper_floor"]).sum()),
                "ceiling lowered": int((g["ceiling_exact"] < g["ceiling"]).sum()),
                "floor gap mean before": g["gap_floor"].mean(), "floor gap mean after": g["gap_floor_exact"].mean(),
                "bracket mean before": g["bracket"].mean(), "bracket mean after": g["bracket_exact"].mean(),
                "closed by floor": int(g["closed_by_floor"].sum()), "ruled out by ceiling": int(g["ruled_out"].sum()),
                "open with bracket": int(g["open_bracket"].sum()),
                "floor > lb_best": int((g["floor_exact"] > g["lb_best"]).sum()),
                "floor > max(lb_best, tw+1)": int((g["floor_exact"] > np.maximum(g["lb_best"], g["tw1"])).sum()),
                "seconds": g["sat_seconds"].fillna(0).sum()}
    rows = []
    for nm, msk in (("gap338", m["is_gap338"]), ("cs200", m["is_cs200"]), ("gap338 ∪ cs200", m["is_gap338"] | m["is_cs200"])):
        rows.append({"target": nm, **summ(m[msk])})
    lines += ["## (a) per target set", "", _md(pd.DataFrame(rows)), ""]
    g = m[m["is_gap338"]]
    rows = [{"band": f"{lo}–{hi}", **summ(g[(g["n"] >= lo) & (g["n"] <= hi)])} for lo, hi in BANDS
            if len(g[(g["n"] >= lo) & (g["n"] <= hi)])]
    lines += ["## (b) the 338 per band", "", _md(pd.DataFrame(rows)), ""]
    cs = m[m["is_cs200"]].copy()
    cs["class"] = [f"{int(a)}-{int(b)}-{int(c)}" for a, b, c in zip(cs["cs_n"], cs["cs_m"], cs["cs_d"])]
    rows = [{"class": cls, **summ(h)} for cls, h in cs.groupby("class", sort=False)]
    rows.sort(key=lambda r: (int(r["class"].split("-")[0]), int(r["class"].split("-")[2])))
    lines += ["## (c) the 200 Chu & Stuckey by class", "", _md(pd.DataFrame(rows)), ""]
    had = m[(m["bracket"] > 0) & (m["is_gap338"] | m["is_cs200"])]
    lines += [f"Of the {len(had)} targets with a bracket after item 02, {int(had['reached'].sum())} were reached, "
              f"the bracket closed on {int((had['bracket_exact'] == 0).sum())} (floor = ceiling: the family's duality "
              f"gap is exact there), the floor rose on {int((had['floor_exact'] > had['harper_floor']).sum())} and "
              f"the ceiling fell on {int((had['ceiling_exact'] < had['ceiling']).sum())}; on the 338 the argmax level "
              f"settled on {int(((m['is_gap338']) & (m['bracket'] > 0) & (m['argmax_settled'] == True)).sum())} of "  # noqa: E712
              f"{int(((m['is_gap338']) & (m['bracket'] > 0)).sum())} with a bracket, and the bracket is 0 on "
              f"{int((m['is_gap338'] & (m['bracket_exact'] == 0)).sum())} of 338 after the run "
              f"({int((m['is_gap338'] & (m['bracket'] == 0)).sum())} before).", ""]
    if len(calls):
        calls["n_band"] = pd.cut(calls["n"], [0, 30, 40, 60, 75, 100, 134], labels=["≤30", "31–40", "41–60", "61–75", "76–100", "101–134"])
        calls["t_band"] = pd.cut(calls["t"], [0, 15, 20, 25, 30, 40, 200], labels=["13–15", "16–20", "21–25", "26–30", "31–40", "41+"])
        rows = []
        for (nb, tb), h in calls.groupby(["n_band", "t_band"], observed=True):
            fin = h[h["status"].isin(["unsat", "sat"])]
            rows.append({"n": nb, "t": tb, "calls": len(h), "unsat": int((h["status"] == "unsat").sum()),
                         "sat": int((h["status"] == "sat").sum()), "budget": int((h["status"] == "budget").sum()),
                         "timeout": int((h["status"] == "timeout").sum()), "finished share": len(fin) / len(h),
                         "median s finished": fin["solve_seconds"].median() if len(fin) else np.nan,
                         "max s finished": fin["solve_seconds"].max() if len(fin) else np.nan,
                         "median clauses": h["cnf_clauses"].median(), "verified": int((h["verdict"] == "verified").sum()),
                         "median check s": h.loc[h["status"] == "unsat", "check_seconds"].median()})
        lines += ["## (d) calls by (n, t): finished against censored", "", _md(pd.DataFrame(rows)), ""]
        rows = []
        for n, h in calls.groupby("n"):
            fin = h[h["status"].isin(["unsat", "sat"])]
            cen = h[~h["status"].isin(["unsat", "sat"])]
            rows.append({"n": n, "instances": h["instance_name"].nunique(), "calls": len(h), "finished": len(fin),
                         "censored": len(cen), "max t finished": fin["t"].max() if len(fin) else np.nan,
                         "min t censored": cen["t"].min() if len(cen) else np.nan,
                         "max b finished (unsat)": fin.loc[fin["status"] == "unsat", "b"].max() if len(fin) else np.nan,
                         "median s finished": fin["solve_seconds"].median() if len(fin) else np.nan,
                         "max conflicts finished": fin["conflicts"].max() if len(fin) else np.nan})
        bd = pd.DataFrame(rows)
        bd.to_csv(SAT_BOUNDARY_CSV, index=False)
        lines += ["## (e) the boundary by n (`boundary.csv`)", "", _md(bd), ""]
        u = calls[calls["status"] == "unsat"]
        lines += [f"Calls: {len(calls)}; unsat {int((calls['status'] == 'unsat').sum())} (drat-trim verified "
                  f"{int((u['verdict'] == 'verified').sum())}, not verified {int((u['verdict'] != 'verified').sum())}), "
                  f"sat {int((calls['status'] == 'sat').sum())}, budget {int((calls['status'] == 'budget').sum())}, "
                  f"timeout {int((calls['status'] == 'timeout').sum())}, error {int((calls['status'] == 'error').sum())}; "
                  f"solve {calls['solve_seconds'].sum() / 3600:.2f} core-hours, check "
                  f"{calls['check_seconds'].fillna(0).sum() / 3600:.2f}; proofs kept "
                  f"{int(u['proof_kept'].fillna(False).astype(bool).sum())}, largest gz "
                  f"{u['proof_gz_bytes'].max() / 2 ** 20 if len(u) else 0:.1f} MB.", ""]
    cols = ["instance_name", "n", "optimum", "lb_best", "harper_floor", "ceiling", "floor_exact", "ceiling_exact",
            "bracket_exact", "levels_settled", "levels_partial", "levels_censored", "argmax_settled", "calls", "sat_seconds",
            "stop_reason"]
    lines += ["## (f) every target with a bracket after item 02", "",
              had.sort_values(["n", "instance_name"])[cols].to_markdown(index=False), ""]
    text = "\n".join(lines)
    SAT_TABLES_MD.write_text(text)
    m.to_csv(SAT_OUT / "joined.csv", index=False)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("ceiling", "exact", "floor", "tables", "sat", "sat-tables"), required=True)
    ap.add_argument("--targets", default="all")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--wall", type=float, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--budget-scale", type=float, default=1.0)
    ap.add_argument("--tag", default="", help="write ceiling_<tag>.csv and sets_<tag>/ (a second search pass)")
    ap.add_argument("--core-hours", type=float, default=6.0, help="sat: hard stop, workers × wall")
    ap.add_argument("--conflicts", type=int, default=SAT_CONFLICTS)
    ap.add_argument("--deadline", type=float, default=SAT_DEADLINE)
    ap.add_argument("--instance-budget", type=float, default=SAT_INSTANCE_BUDGET)
    ap.add_argument("--max-levels", type=int, default=SAT_MAX_LEVELS)
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
    elif args.stage == "sat":
        out = run_sat(args.targets, args.workers, args.core_hours, args.conflicts, args.deadline,
                      args.instance_budget, args.max_levels, args.limit)
        slog(f"sat: {len(out)} instances on file; bracket closed on {int((out['bracket_after'] == 0).sum())}; "
             f"floor raised on {int((out['floor_after'] > out['floor_before']).sum())}; "
             f"{out['seconds'].sum() / 3600:.2f} core-hours of instance time")
    elif args.stage == "sat-tables":
        print(write_sat_tables())
    else:
        print(write_tables())


if __name__ == "__main__":
    main()
