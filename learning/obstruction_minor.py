"""loop0013 item 04: family M (contraction minors) by search — the
contraction-sequence local search, its certificate, the greedy ladder as the
baseline, and the validation against brute force and the recorded certificates.

**The object.** For the MOSP graph `G` of an instance (customers as vertices,
a clique per pattern), a contraction sequence is a list of pairs `(v, u)` in
the instance's customer labels: contract `v` into `u` (`u` keeps its label and
inherits `v`'s neighbours), or `(v, -1)`: delete an isolated `v`. Every pair
must be an edge of the *current* graph (plan §0.5 (e); the rule of
`satisfiability.relaxation.minor_groups` and `pathwidth_solver`'s `replay`).
The result `H` is a contraction minor of `G`, so `pw(H) <= pw(G)` (Fellows &
Langston 1987, Lemma 4.2; Lean `pathwidth_minorOf_le` and
`pathwidth_gt_of_minorOf` in `lean/MOSPFormalization/Minor.lean`), and with
`mospValue_eq_pathwidth_add_one` a proved `pw(H) >= p` certifies
`MOSP(instance) >= p + 1`. The family's value on an instance is the best such
floor, in optimum units; its gap is `optimum - floor`.

**Direction.** Unlike family E, this family is a genuine maximisation: any
minor found by search, with a proved width, is a valid floor and a
certificate. What the search cannot say is that no better minor exists.

**Evaluation of a candidate minor** (`evaluate`): the certified witness's
opening layout lifted to the minor (every branch set at its first member's
position; the vertex separation of the lifted layout never exceeds the
original's, see `lifted_layout`) and a greedy layout are upper bounds on
`pw(H)`; a candidate whose upper bound cannot improve the best floor so far
is not sent to the C program. Otherwise one call,

    printf '%s\\n' "$g6" | nice -n 19 pathwidth_solver/cli/pathwidth -t CAP -l -v -m min_vertices=1000000

(graph6 by networkx from the quotient's edge list, labels `0..m-1` in
increasing order of the surviving representative), parsed for
`pathwidth <w> <status>` and stderr's `lower=`; the floor certified is `w`
when the status is `refutation` or `bound` (the C's own minor step is off,
so `minor` never occurs) and the printed `lower` when it is `upper` — both
valid; `source` records which.

**The search** (`search`): tabu local search over sequences; moves delete a
pair (the minor grows by one vertex), insert a pair (an edge of the current
minor), retarget a pair to another current neighbour of `v`, move a pair
earlier; an invalid pair after a move is repaired to `v`'s current neighbour
of least degree, or dropped (`repair`); tabu tenure 10 on the absorbed
vertex; restarts from `relaxation.minor_sequence` at 50, 60, 70, 80, 90 and
95% for both rules and from the incumbent; the objective is the certified
floor, ties by fewer vertices; plateau moves (equal floor) are accepted. The
baseline (`ladder`) is the greedy ladder, both rules at 50–85% in 5% steps
then 90 and 95%, through the same `evaluate` at the same cap. Both get the
same total seconds per instance. The ladder stops when its floor reaches the
optimum (its points come in increasing size, so the first is its smallest
certifying minor); the search runs its whole budget, minimising the
vertex count once the floor is at the optimum (the "minimal certifying
minor" the item asks about).

**Certificate** (`certificate`, JSON): instance name, `n`, the SHA-256 of
the rows and of `G`'s edge list, the sequence, `m`, the minor's edge hash,
the refuted width, the C program's output lines verbatim, its binary's
SHA-256, seconds, the floor and its source. `paper1/obstruction_check.py
check-minor` replays it with code that shares nothing with this module.

Stages:

    nice -n 19 python3 -m learning.obstruction_minor --stage validate
    nice -n 19 python3 -m learning.obstruction_minor --stage run --targets gap338 --max-n 60 --workers 8 --seconds 60,120
    nice -n 19 python3 -m learning.obstruction_minor --stage check --workers 8
    python3 -m learning.obstruction_minor --stage tables

Nothing here solves an instance: every optimum is read from item 01's ledger,
the witness from `solutions/<name>.json` (read only), and the C program runs
on minors only, under a cap, with its own minor step disabled.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from learning.obstruction_ledger import (LEDGER_CORPUS, TARGETS_JSON, BANDS,
                                         adjacency_from_matrix, corpus_instances)
from learning.obstruction_expansion import (solution_record, safe_name, witness_layouts,
                                            matrix_sha256, write_standard_instance, target_names, ledger)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "scratch" / "obstruction_search" / "04_minor"
SEARCH_CSV = OUT / "search.csv"
LADDER_CSV = OUT / "ladder.csv"
CERT_DIR = OUT / "certificates"
VALIDATION_LOG = OUT / "validation.log"
RUN_LOG = OUT / "run.log"
TABLES_MD = OUT / "tables.md"
CHECKER_CSV = OUT / "checker_verdicts.csv"
C_BINARY = ROOT / "pathwidth_solver" / "cli" / "pathwidth"

def set_out(item: str) -> Path:
    """Point every output path at `reports/scratch/obstruction_search/<item>/`
    (`04_minor` for item 04, `05_minor_scale` for item 05). Called before any
    worker pool is created, so forked workers see the same paths."""
    global OUT, SEARCH_CSV, LADDER_CSV, CERT_DIR, VALIDATION_LOG, RUN_LOG, TABLES_MD, CHECKER_CSV, RIDGE_CSV, RIDGE_DIR
    OUT = ROOT / "reports" / "scratch" / "obstruction_search" / item
    SEARCH_CSV = OUT / "search.csv"
    LADDER_CSV = OUT / "ladder.csv"
    CERT_DIR = OUT / "certificates"
    VALIDATION_LOG = OUT / "validation.log"
    RUN_LOG = OUT / "run.log"
    TABLES_MD = OUT / "tables.md"
    CHECKER_CSV = OUT / "checker_verdicts.csv"
    RIDGE_CSV = OUT / "ridge.csv"
    RIDGE_DIR = OUT / "ridge"
    return OUT


RIDGE_CSV = OUT / "ridge.csv"
RIDGE_DIR = OUT / "ridge"

# plan §0.5 (e): the C cap per call by the instance's size, and the item's
# per-instance budgets by band (item 04: 60 s at n <= 40, 120 s at 41-60;
# item 05: 180 s at 61-100, 300 s at 101-134)
CAP_BY_SIZE = ((60, 2.0), (100, 5.0), (134, 10.0))
BUDGET_BANDS = (40, 60, 100)


def cap_for(n: int) -> float:
    for hi, cap in CAP_BY_SIZE:
        if n <= hi:
            return cap
    return CAP_BY_SIZE[-1][1]


def budget_for(n: int, seconds: tuple[int, ...]) -> int:
    """`seconds` lists the budget per band (n <= 40, 41-60, 61-100, 101+);
    a shorter tuple repeats its last entry."""
    for i, hi in enumerate(BUDGET_BANDS):
        if n <= hi:
            return int(seconds[min(i, len(seconds) - 1)])
    return int(seconds[-1])


RULES = ("min-d", "least-c")
LADDER_FRACTIONS = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
RESTART_FRACTIONS = (0.50, 0.60, 0.70, 0.80, 0.90, 0.95)
TENURE = 10
MOVES_PER_RESTART = 25
C_CAP_SECONDS = 2.0      # per C call at n <= 60 (plan §0.5 (e))
MIN_MINOR = 3


def log(msg: str, path: Path | None = None) -> None:
    """Append to `RUN_LOG` (resolved at call time, so `set_out` redirects it)."""
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(path or RUN_LOG, "a") as fh:
        fh.write(line + "\n")


# ----------------------------------------------------------------------------
# graphs, sequences, replay
# ----------------------------------------------------------------------------


def bits(mask: int) -> list[int]:
    out = []
    while mask:
        b = mask & -mask
        out.append(b.bit_length() - 1)
        mask ^= b
    return out


def edge_list(adj: list[int]) -> list[tuple[int, int]]:
    return [(u, v) for u in range(len(adj)) for v in bits(adj[u]) if u < v]


def edges_sha256(m: int, edges: list[tuple[int, int]]) -> str:
    """The contract shared with the checker: SHA-256 of "m e\\n" then one
    "u v\\n" per edge, edges sorted, `u < v`."""
    edges = sorted((min(a, b), max(a, b)) for a, b in edges)
    text = f"{m} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges)
    return hashlib.sha256(text.encode()).hexdigest()


class InvalidPair(ValueError):
    pass


def replay(adj: list[int], seq: list[tuple[int, int]]) -> tuple[list[int], int, dict[int, int]]:
    """Replay a sequence on open-neighbourhood masks. Returns the contracted
    masks (over the original labels; dead vertices have mask 0), the alive
    mask, and the branch sets (representative -> member mask). Raises
    `InvalidPair` when a pair is not an edge of the current graph, when `v`
    is dead, or when `u == -1` and `v` is not isolated. Vertices with no
    edges at the start are isolated vertices of `G` and stay alive."""
    cur = list(adj)
    n = len(adj)
    alive = (1 << n) - 1
    branch = {v: 1 << v for v in range(n)}
    for step, (v, u) in enumerate(seq):
        if not 0 <= v < n or not (alive >> v) & 1:
            raise InvalidPair(f"step {step}: {v} is not in the current graph")
        if u == -1:
            if cur[v]:
                raise InvalidPair(f"step {step}: deleting {v}, which has a neighbour")
            alive &= ~(1 << v)
            branch.pop(v)
            continue
        if u == v or not 0 <= u < n or not (cur[v] >> u) & 1:
            raise InvalidPair(f"step {step}: ({v}, {u}) is not an edge of the current graph")
        merged = (cur[u] | cur[v]) & ~((1 << u) | (1 << v))
        for w in bits(cur[v]):
            cur[w] = (cur[w] | (1 << u)) & ~(1 << v)
        cur[u] = merged
        cur[v] = 0
        alive &= ~(1 << v)
        branch[u] |= branch.pop(v)
    return cur, alive, branch


def quotient_from_branch_sets(adj: list[int], branch: dict[int, int]) -> dict[int, set[int]]:
    """The quotient graph from the branch sets alone (the second route the
    checker takes): representatives adjacent iff some member edge crosses."""
    rep = {}
    for r, members in branch.items():
        for x in bits(members):
            rep[x] = r
    Q = {r: set() for r in branch}
    for a in range(len(adj)):
        if a not in rep:
            continue
        for b in bits(adj[a]):
            if b in rep and rep[a] != rep[b]:
                Q[rep[a]].add(rep[b])
    return Q


def minor_graph(cur: list[int], alive: int) -> tuple[list[int], list[tuple[int, int]]]:
    """Relabel the surviving representatives `0..m-1` in increasing label
    order; returns the labels and the relabelled edge list."""
    labels = bits(alive)
    index = {v: i for i, v in enumerate(labels)}
    edges = [(index[a], index[b]) for a in labels for b in bits(cur[a]) if a < b]
    return labels, sorted(edges)


def minor_masks(m: int, edges: list[tuple[int, int]]) -> list[int]:
    adj = [0] * m
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return adj


def graph6(m: int, edges: list[tuple[int, int]]) -> str:
    import networkx as nx

    G = nx.Graph()
    G.add_nodes_from(range(m))
    G.add_edges_from(edges)
    return nx.to_graph6_bytes(G, nodes=range(m), header=False).decode().strip()


def repair(adj: list[int], seq: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Replay, repairing every invalid pair: a dead or absent `v` drops the
    pair; a `u` that is no longer a neighbour is retargeted to `v`'s current
    neighbour of least degree (ties by label); a `v` with no neighbour and a
    `u != -1` becomes a deletion. The result replays without error."""
    cur = list(adj)
    n = len(adj)
    alive = (1 << n) - 1
    out: list[tuple[int, int]] = []
    for v, u in seq:
        if not 0 <= v < n or not (alive >> v) & 1:
            continue
        if u == -1 or u == v or not (cur[v] >> u) & 1:
            nb = bits(cur[v])
            if not nb:
                u = -1
            else:
                u = min(nb, key=lambda c: (cur[c].bit_count(), c))
        if u == -1:
            alive &= ~(1 << v)
            out.append((v, -1))
            continue
        merged = (cur[u] | cur[v]) & ~((1 << u) | (1 << v))
        for w in bits(cur[v]):
            cur[w] = (cur[w] | (1 << u)) & ~(1 << v)
        cur[u] = merged
        cur[v] = 0
        alive &= ~(1 << v)
        out.append((v, u))
    return out


def greedy_sequence(adj: list[int], size: int, rule: str) -> list[tuple[int, int]]:
    """`relaxation.minor_sequence`'s rule on masks (the same choices: the
    minimum-degree alive vertex, ties by label, into the neighbour of least
    degree (`min-d`) or fewest common neighbours (`least-c`), ties by label).
    Isolated vertices of `G` are deleted when chosen (degree 0 is minimal)."""
    cur = list(adj)
    n = len(adj)
    alive = (1 << n) - 1
    seq: list[tuple[int, int]] = []
    while alive.bit_count() > max(size, 0):
        v = min(bits(alive), key=lambda x: (cur[x].bit_count(), x))
        nb = cur[v]
        if not nb:
            seq.append((v, -1))
            alive &= ~(1 << v)
            continue
        if rule == "min-d":
            u = min(bits(nb), key=lambda c: (cur[c].bit_count(), c))
        else:
            u = min(bits(nb), key=lambda c: ((cur[c] & nb).bit_count(), c))
        seq.append((v, u))
        merged = (cur[u] | nb) & ~((1 << u) | (1 << v))
        for w in bits(nb):
            cur[w] = (cur[w] | (1 << u)) & ~(1 << v)
        cur[u] = merged
        cur[v] = 0
        alive &= ~(1 << v)
    return seq


# ----------------------------------------------------------------------------
# upper bounds on a minor's width (cheap), and the C program
# ----------------------------------------------------------------------------


def vertex_separation(adj: list[int], order: list[int]) -> int:
    placed, best = 0, 0
    full = (1 << len(adj)) - 1
    for v in order:
        placed |= 1 << v
        rest = full & ~placed
        best = max(best, sum(1 for u in bits(placed) if adj[u] & rest))
    return best


def lifted_layout(labels: list[int], branch: dict[int, int], position: list[int]) -> list[int]:
    """The minor's layout by the earliest member of each branch set. For a
    layout `L` of `G` with prefixes `P_i`, the lifted prefix `Q_i` is the set
    of branch sets meeting `P_i`; a branch set `B` in the boundary of `Q_i`
    (a neighbour branch set wholly outside `P_i`) is connected, meets `P_i`
    and has a member outside it, so some member of `B` inside `P_i` has a
    neighbour outside: an injection into `G`'s boundary. Hence
    `vs(lifted) <= vs(L)`."""
    index = {v: i for i, v in enumerate(labels)}
    first = {index[r]: min(position[x] for x in bits(branch[r])) for r in labels}
    return sorted(range(len(labels)), key=lambda i: (first[i], i))


def greedy_layout(adj: list[int]) -> list[int]:
    """Place next the vertex that keeps the boundary smallest (ties by label)."""
    m = len(adj)
    full = (1 << m) - 1
    placed, order = 0, []
    while placed != full:
        best, bv = None, -1
        for v in bits(full & ~placed):
            p = placed | (1 << v)
            rest = full & ~p
            cost = sum(1 for u in bits(p) if adj[u] & rest)
            if best is None or cost < best:
                best, bv = cost, v
        placed |= 1 << bv
        order.append(bv)
    return order


def binary_sha256(path: Path = C_BINARY) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_c(g6: str, cap: float, binary: Path = C_BINARY, nice: bool = True) -> dict:
    """One call of the C program on a graph6 line; `-m min_vertices=1000000`
    disables its own minor step so the certificate is ours."""
    cmd = ["nice", "-n", "19"] if nice else []
    cmd += [str(binary), "-t", f"{cap:g}", "-l", "-v", "-m", "min_vertices=1000000"]
    t0 = time.monotonic()
    proc = subprocess.run(cmd, input=g6 + "\n", capture_output=True, text=True, timeout=cap * 10 + 60)
    seconds = time.monotonic() - t0
    out = {"stdout": proc.stdout.strip().splitlines(), "stderr": proc.stderr.strip().splitlines(),
           "returncode": proc.returncode, "seconds": seconds, "width": None, "status": None, "lower": None,
           "layout": None, "nodes": None}
    for line in out["stdout"]:
        parts = line.split()
        if parts and parts[0] == "pathwidth" and len(parts) >= 3:
            out["width"], out["status"] = int(parts[1]), parts[2]
        elif parts and parts[0] == "layout":
            out["layout"] = [int(x) for x in parts[1:]]
    for line in out["stderr"]:
        for tok in line.split():
            if tok.startswith("lower="):
                out["lower"] = int(tok[6:])
            elif tok.startswith("nodes="):
                out["nodes"] = int(tok[6:])
    return out


def proved_pathwidth(c: dict) -> tuple[int | None, str]:
    """The pathwidth the C output proves for the graph it ran on, and why."""
    if c["status"] in ("refutation", "bound", "minor") and c["width"] is not None:
        return c["width"], "c_" + c["status"]
    if c["lower"] is not None:
        return c["lower"], "c_lower"
    return None, "none"


# ----------------------------------------------------------------------------
# the evaluator (shared by the ladder and the search)
# ----------------------------------------------------------------------------


@dataclass
class Evaluator:
    adj: list[int]
    optimum: int | None
    cap: float
    position: list[int] | None = None       # the certified witness's opening layout, as positions
    deadline: float = float("inf")
    calls: int = 0
    skipped: int = 0
    seconds_c: float = 0.0
    cache: dict = field(default_factory=dict)
    best_floor: int = 1                     # optimum units
    best_m: int = 10 ** 9
    best: dict | None = None
    proposals: list = field(default_factory=list)   # (masks, proved) for validation
    min_m: int = MIN_MINOR                  # item 07: minors outside [min_m, max_m] are never sent to the C program
    max_m: int = 10 ** 9
    greedy_upper_max_m: int = 10 ** 9       # the greedy layout (cubic) is computed only up to this size
    out_of_range: int = 0

    def time_left(self) -> float:
        return self.deadline - time.monotonic()

    def evaluate(self, seq: list[tuple[int, int]], record_proposals: bool = False) -> dict:
        """The floor the minor of `seq` certifies, in optimum units, with the
        C's output; a candidate that cannot improve the best is skipped."""
        cur, alive, branch = replay(self.adj, seq)
        labels, edges = minor_graph(cur, alive)
        m = len(labels)
        key = edges_sha256(m, edges)
        if key in self.cache:
            res = dict(self.cache[key])
            res["cached"] = True
            return res
        madj = minor_masks(m, edges)
        upper = m - 1 if m else 0
        if m and m <= self.greedy_upper_max_m:
            upper = min(upper, vertex_separation(madj, greedy_layout(madj)))
        if self.position is not None and m:
            upper = min(upper, vertex_separation(madj, lifted_layout(labels, branch, self.position)))
        res = {"m": m, "edges": edges, "labels": labels, "hash": key, "upper_pw": upper, "seq": list(seq),
               "floor": None, "source": "skipped", "c": None, "cached": False}
        if m < self.min_m or m > self.max_m:
            self.out_of_range += 1
            res["floor"], res["source"] = 1, "out_of_range"
            self.cache[key] = res
            return res
        # upper + 1 is an upper bound on the floor this minor could certify
        if m < MIN_MINOR or upper + 1 < self.best_floor or (upper + 1 == self.best_floor and m >= self.best_m):
            self.skipped += 1
            res["floor"] = 1
            self.cache[key] = res
            return res
        cap = min(self.cap, max(0.05, self.time_left()))
        res["cap"] = cap
        c = run_c(graph6(m, edges), cap)
        self.calls += 1
        self.seconds_c += c["seconds"]
        pw, source = proved_pathwidth(c)
        if pw is None:
            res.update({"floor": 1, "source": "none", "c": c})
        else:
            res.update({"floor": pw + 1, "source": source, "c": c})
        if record_proposals:
            self.proposals.append((madj, pw, source))
        self.cache[key] = res
        if res["floor"] > self.best_floor or (res["floor"] == self.best_floor and m < self.best_m):
            self.best_floor, self.best_m, self.best = res["floor"], m, res
        return res

    def at_optimum(self) -> bool:
        return self.optimum is not None and self.best_floor >= self.optimum

    def done(self) -> bool:
        return self.time_left() <= 0


def ladder(ev: Evaluator, fractions=LADDER_FRACTIONS, rules=RULES) -> list[dict]:
    """The greedy ladder, both rules, smallest minors first per rule."""
    n = len(ev.adj)
    rows = []
    for rule in rules:
        full = greedy_sequence(ev.adj, 0, rule)
        for frac in fractions:
            if ev.done() or ev.at_optimum():
                return rows
            size = max(MIN_MINOR, int(round(frac * n)))
            seq = full[:max(0, n - size)]
            res = ev.evaluate(seq)
            rows.append({"rule": rule, "fraction": frac, "size": size, "m": res["m"], "floor": res["floor"],
                         "source": res["source"], "cached": res["cached"]})
    return rows


# ----------------------------------------------------------------------------
# the search
# ----------------------------------------------------------------------------


def _moves(adj: list[int], seq: list[tuple[int, int]], rng: random.Random) -> tuple[str, int, list[tuple[int, int]]]:
    """One random neighbour of `seq`; returns (move, touched vertex, repaired sequence)."""
    kinds = ["insert", "retarget", "earlier"]
    if seq:
        kinds.append("delete")
    kind = rng.choice(kinds)
    new = list(seq)
    touched = -1
    if kind == "delete":
        i = rng.randrange(len(seq))
        touched = seq[i][0]
        del new[i]
    elif kind == "insert":
        cur, alive, _ = replay(adj, seq)
        cands = [v for v in bits(alive) if cur[v]]
        if not cands or alive.bit_count() <= MIN_MINOR:
            return kind, -1, list(seq)
        v = rng.choice(cands)
        u = rng.choice(bits(cur[v]))
        touched = v
        new.append((v, u))
    elif kind == "retarget":
        if not seq:
            return kind, -1, list(seq)
        i = rng.randrange(len(seq))
        cur, _, _ = replay(adj, seq[:i])
        v = seq[i][0]
        nb = [c for c in bits(cur[v]) if c != seq[i][1]]
        if not nb:
            return kind, -1, list(seq)
        touched = v
        new[i] = (v, rng.choice(nb))
    else:  # earlier
        if len(seq) < 2:
            return kind, -1, list(seq)
        i = rng.randrange(1, len(seq))
        j = rng.randrange(0, i)
        touched = seq[i][0]
        pair = new.pop(i)
        new.insert(j, pair)
    return kind, touched, repair(adj, new)


def search(ev: Evaluator, rng_seed: int = 1, restart_fractions=RESTART_FRACTIONS,
           moves_per_restart: int = MOVES_PER_RESTART, starts: list | None = None) -> dict:
    """Tabu local search over contraction sequences; returns the trace.
    `starts` (label, sequence) overrides the greedy restart points (the
    ridge stage restarts from its own ladder points or a recorded certificate)."""
    rng = random.Random(rng_seed)
    n = len(ev.adj)
    if starts is None:
        starts = []
        for rule in RULES:
            full = greedy_sequence(ev.adj, 0, rule)
            for frac in restart_fractions:
                size = max(MIN_MINOR, int(round(frac * n)))
                starts.append((f"{rule}@{frac:.2f}", full[:max(0, n - size)]))
    starts = [(label, list(seq)) for label, seq in starts]
    trace = {"restarts": 0, "moves": 0, "improvements": 0, "accepted": 0, "move_kinds": {}}
    # evaluate every start first (the ladder's own points are among them)
    for label, seq in starts:
        if ev.done():
            return trace
        ev.evaluate(seq)
    k = 0
    while not ev.done():
        if k % 2 == 1 and ev.best is not None:
            label, seq = "incumbent", list(ev.best["seq"])
        else:
            label, seq = starts[(k // 2) % len(starts)]
        k += 1
        trace["restarts"] += 1
        cur = ev.evaluate(seq)
        cur_floor, cur_m = cur["floor"], cur["m"]
        tabu: dict[int, int] = {}
        for step in range(moves_per_restart):
            if ev.done():
                break
            kind, touched, new = _moves(ev.adj, seq, rng)
            trace["move_kinds"][kind] = trace["move_kinds"].get(kind, 0) + 1
            trace["moves"] += 1
            if touched < 0:
                continue
            res = ev.evaluate(new)
            better = res["floor"] > ev.best_floor or (res["floor"] == ev.best_floor and res["m"] < ev.best_m)
            if tabu.get(touched, -1) > step and not better:
                continue
            if res["floor"] > cur_floor or (res["floor"] == cur_floor and res["m"] <= cur_m + 1):
                if res["floor"] > cur_floor:
                    trace["improvements"] += 1
                seq, cur_floor, cur_m = new, res["floor"], res["m"]
                trace["accepted"] += 1
                tabu[touched] = step + TENURE
    return trace


# ----------------------------------------------------------------------------
# certificates
# ----------------------------------------------------------------------------


def certificate(name: str, matrix, adj: list[int], best: dict, seconds: float, method: str,
                optimum: int | None, cap: float = C_CAP_SECONDS) -> dict:
    c = best["c"]
    pw, source = proved_pathwidth(c)
    return {
        "format": "obstruction-minor-1",
        "instance_name": name,
        "n": len(adj),
        "matrix_sha256": matrix_sha256(matrix),
        "graph_sha256": edges_sha256(len(adj), edge_list(adj)),
        "graph_edges": len(edge_list(adj)),
        "sequence": [[int(v), int(u)] for v, u in best["seq"]],
        "sequence_note": "pairs [v, u] in the instance's customer labels (0-based rows): contract v into u, "
                         "u keeps its label; [v, -1] deletes an isolated v; every pair is an edge of the current graph",
        "m": best["m"],
        "minor_labels": best["labels"],
        "minor_edges": [[int(a), int(b)] for a, b in best["edges"]],
        "minor_sha256": best["hash"],
        "minor_sha256_note": 'SHA-256 of "m e\\n" then "a b\\n" per edge, sorted, a < b, labels 0..m-1 in increasing '
                             "order of the surviving representative",
        "c_width": c["width"], "c_status": c["status"], "c_lower": c["lower"],
        "pathwidth_proved": pw, "refuted_width": pw - 1 if pw is not None else None,
        "floor_source": source,
        "floor": best["floor"], "floor_units": "optimum units: pathwidth(minor) + 1 <= pathwidth(G) + 1 = MOSP",
        "optimum_on_record": optimum,
        "c_command": f"printf '%s\\n' \"$g6\" | nice -n 19 pathwidth_solver/cli/pathwidth -t {cap:g} -l -v -m min_vertices=1000000",
        "c_cap_seconds": cap,
        "c_stdout": c["stdout"], "c_stderr": c["stderr"], "c_seconds": c["seconds"], "c_nodes": c.get("nodes"),
        "c_binary_sha256": binary_sha256(),
        "method": method,
        "search_seconds": seconds,
        "theorems": "pathwidth_gt_of_minorOf / pathwidth_minorOf_le (lean/MOSPFormalization/Minor.lean); "
                    "mospValue_eq_pathwidth_add_one (lean/MOSPFormalization/MOSPGraph.lean); the C program's "
                    "refutation rests on the corrected search rules (lean/MOSPFormalization/Search/), its bound on "
                    "degeneracy_le_pathwidth / minDegreeIn_le_degeneracy (Sandwich.lean)",
    }


# ----------------------------------------------------------------------------
# stage: run
# ----------------------------------------------------------------------------


def _job(args) -> dict:
    name, matrix, ordering, optimum, seconds, rng_seed, write = args[:7]
    cap = float(args[7]) if len(args) > 7 else C_CAP_SECONDS
    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    position = None
    if ordering is not None:
        opening, _ = witness_layouts(matrix, ordering)
        position = [0] * n
        for i, v in enumerate(opening):
            position[v] = i
    out = {"instance_name": name, "n": n, "optimum": optimum, "seconds_budget": seconds, "c_cap": cap}
    # the ladder
    t0 = time.monotonic()
    ev_l = Evaluator(adj, optimum, cap, position, deadline=t0 + seconds)
    rows = ladder(ev_l)
    lad_seconds = time.monotonic() - t0
    out.update({"ladder_floor": ev_l.best_floor, "ladder_m": ev_l.best_m if ev_l.best else None,
                "ladder_source": ev_l.best["source"] if ev_l.best else "none",
                "ladder_rule": next((r["rule"] for r in rows if r["floor"] == ev_l.best_floor and r["m"] == ev_l.best_m), None),
                "ladder_calls": ev_l.calls, "ladder_skipped": ev_l.skipped, "ladder_seconds": lad_seconds,
                "ladder_c_seconds": ev_l.seconds_c, "ladder_points": len(rows),
                "ladder_reached_optimum": optimum is not None and ev_l.best_floor >= optimum})
    # the search
    t1 = time.monotonic()
    ev_s = Evaluator(adj, optimum, cap, position, deadline=t1 + seconds)
    trace = search(ev_s, rng_seed)
    s_seconds = time.monotonic() - t1
    out.update({"search_floor": ev_s.best_floor, "search_m": ev_s.best_m if ev_s.best else None,
                "search_source": ev_s.best["source"] if ev_s.best else "none",
                "search_calls": ev_s.calls, "search_skipped": ev_s.skipped, "search_seconds": s_seconds,
                "search_c_seconds": ev_s.seconds_c, "search_restarts": trace["restarts"],
                "search_moves": trace["moves"], "search_accepted": trace["accepted"],
                "search_improvements": trace["improvements"],
                "search_reached_optimum": optimum is not None and ev_s.best_floor >= optimum,
                "search_len": len(ev_s.best["seq"]) if ev_s.best else None})
    out["beats_ladder_floor"] = ev_s.best_floor > ev_l.best_floor
    out["beats_ladder_tie"] = ev_s.best_floor == ev_l.best_floor and ev_s.best is not None and ev_l.best is not None \
        and ev_s.best_m < ev_l.best_m
    out["below_ladder"] = ev_s.best_floor < ev_l.best_floor
    if write and ev_s.best is not None:
        d = CERT_DIR / safe_name(name)
        d.mkdir(parents=True, exist_ok=True)
        write_standard_instance(d / "instance.mosp", name, matrix)
        cert = certificate(name, matrix, adj, ev_s.best, s_seconds, "search", optimum, cap)
        (d / "search.json").write_text(json.dumps(cert, indent=1))
        if ev_l.best is not None:
            certl = certificate(name, matrix, adj, ev_l.best, lad_seconds, "ladder", optimum, cap)
            (d / "ladder.json").write_text(json.dumps(certl, indent=1))
        (d / "ladder_points.json").write_text(json.dumps(rows, indent=1))
        out["certificate"] = str((d / "search.json").relative_to(ROOT))
    return out


def run(which: str, max_n: int, workers: int, seconds: tuple[int, ...], rng_seed: int = 1,
        limit: int | None = None, wall: float | None = None, min_n: int = 0, core_hours: float | None = None,
        order: str = "large-first") -> pd.DataFrame:
    """The ladder and the search on every target with `min_n <= n <= max_n`
    not yet in `search.csv`; `which` is a comma-separated list of target
    sets (their union). At most `workers` instances run at once; a new one
    is started only while the core-hours spent (completed instances' ladder
    + search seconds, plus the budgets of the running ones) are below
    `core_hours`, and the instances not reached are listed in
    `not_reached.txt` (the item's hard stop)."""
    led = ledger().set_index("instance_name")
    names = []
    for w in which.split(","):
        for nm in target_names(w):
            if min_n <= int(led.loc[nm, "n"]) <= max_n and nm not in names:
                names.append(nm)
    if limit:
        names = names[:limit]
    inst = corpus_instances()
    done = set()
    if SEARCH_CSV.exists():
        done = set(pd.read_csv(SEARCH_CSV)["instance_name"])
    if (OUT / "carried_item04.csv").exists():
        done |= set(pd.read_csv(OUT / "carried_item04.csv")["instance_name"])
    jobs = []
    for nm in names:
        if nm in done:
            continue
        n = int(led.loc[nm, "n"])
        sol = solution_record(nm)
        budget = budget_for(n, seconds)
        jobs.append((nm, np.asarray(inst[nm][1].matrix, dtype=int), sol["ordering"] if sol else None,
                     int(led.loc[nm, "optimum"]), budget, rng_seed, True, cap_for(n)))
    jobs.sort(key=lambda j: (len(j[1]) if order == "small-first" else -len(j[1]), j[0]))
    log(f"run: {len(names)} targets ({which}, {min_n} <= n <= {max_n}), {len(jobs)} to do, {workers} workers, "
        f"seconds {seconds}, caps by size {CAP_BY_SIZE}, core-hours cap {core_hours}, order {order}, "
        f"binary {binary_sha256()[:16]}")
    t0 = time.monotonic()
    rows = []
    spent = 0.0            # seconds of completed instances (ladder + search)
    committed = 0.0        # budgets of the running instances (2 x budget each)
    cap_seconds = core_hours * 3600 if core_hours else float("inf")
    pending = list(jobs)
    running: dict = {}
    stopped_early = False
    with Pool(workers) as pool:
        while pending or running:
            while pending and len(running) < workers and not stopped_early:
                if spent + committed + 2 * pending[0][4] > cap_seconds:
                    stopped_early = True
                    break
                job = pending.pop(0)
                running[job[0]] = (pool.apply_async(_job, (job,)), 2 * job[4])
                committed += 2 * job[4]
            if wall and time.monotonic() - t0 > wall and not stopped_early:
                log("  wall budget reached; no more instances started")
                stopped_early = True
            if not running:
                break
            finished = [nm for nm, (res, _) in running.items() if res.ready()]
            if not finished:
                time.sleep(0.5)
                continue
            for nm in finished:
                res, budget2 = running.pop(nm)
                committed -= budget2
                row = res.get()
                rows.append(row)
                spent += float(row["ladder_seconds"]) + float(row["search_seconds"])
                pd.DataFrame([row]).to_csv(SEARCH_CSV, mode="a", header=not SEARCH_CSV.exists(), index=False)
                k = len(rows)
                if k % 10 == 0 or k == len(jobs) or row["n"] > 100:
                    log(f"  {k}/{len(jobs)} done, {time.monotonic() - t0:.0f} s wall, {spent / 3600:.2f} core-h spent; "
                        f"last {row['instance_name']!r} (n={row['n']}): ladder {row['ladder_floor']} search "
                        f"{row['search_floor']} opt {row['optimum']}")
        if stopped_early and pending:
            (OUT / "not_reached.txt").write_text("".join(j[0] + "\n" for j in pending))
            log(f"  core-hour cap {core_hours} reached at {spent / 3600:.2f} core-h: {len(pending)} instances not "
                f"reached (not_reached.txt)")
    frame = pd.read_csv(SEARCH_CSV) if SEARCH_CSV.exists() else pd.DataFrame(rows)
    write_ladder_csv()
    log(f"run done: {len(frame)} rows, {time.monotonic() - t0:.0f} s wall, {spent / 3600:.2f} core-h this run")
    return frame


def write_ladder_csv() -> None:
    lad = []
    for d in sorted(CERT_DIR.iterdir()) if CERT_DIR.exists() else []:
        p = d / "ladder_points.json"
        if p.exists():
            nm = (d / "instance.mosp").read_text().splitlines()[0].strip()
            for r in json.loads(p.read_text()):
                lad.append({"instance_name": nm, **r})
    pd.DataFrame(lad).to_csv(LADDER_CSV, index=False)


# ----------------------------------------------------------------------------
# stage: ridge (item 05: the two 125-customer ridge instances)
# ----------------------------------------------------------------------------

RIDGE_SIZES = (100, 102, 105, 108, 110)
RIDGE_LADDER_CAP = 120.0
RIDGE_SEARCH_CAP = 60.0
RECORDED_M70 = ROOT / "reports" / "scratch" / "minor_certificates" / "Random-125-125-2-3_0_m70.json"


def recorded_sequence(path: Path = RECORDED_M70) -> list[tuple[int, int]]:
    """`mc_graph.py`'s `[keep, absorbed]` pairs as this module's `(absorbed, keep)`."""
    rec = json.loads(Path(path).read_text())
    return [(int(b), int(a)) for a, b in rec["contraction_sequence"]]


def _ridge_job(args) -> dict:
    """One ridge instance: the two greedy rules at `RIDGE_SIZES` under the
    ladder cap, then the search from the best of them (or, with
    `from_recorded`, from the recorded 70-vertex certificate downward) under
    the search cap, within `seconds` in all. Every C call is a row."""
    name, matrix, ordering, optimum, seconds, rng_seed, from_recorded = args
    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    opening, _ = witness_layouts(matrix, ordering)
    position = [0] * n
    for i, v in enumerate(opening):
        position[v] = i
    t0 = time.monotonic()
    ev = Evaluator(adj, optimum, RIDGE_LADDER_CAP, position, deadline=t0 + seconds)
    rows = []

    def row(phase, label, res, m_target=None):
        c = res.get("c") or {}
        return {"instance_name": name, "n": n, "optimum": optimum, "phase": phase, "label": label,
                "size_target": m_target, "m": res["m"], "cap": ev.cap, "upper_pw": res["upper_pw"],
                "floor": res["floor"], "source": res["source"], "c_width": c.get("width"), "c_status": c.get("status"),
                "c_lower": c.get("lower"), "c_nodes": c.get("nodes"), "c_seconds": c.get("seconds"),
                "cached": res["cached"], "elapsed": time.monotonic() - t0, "best_floor": ev.best_floor, "best_m": ev.best_m}

    starts = []
    for size in RIDGE_SIZES:
        for rule in RULES:
            if ev.done():
                break
            seq = greedy_sequence(adj, size, rule)
            # the ladder points all go to the C program (no skip): the item asks for every size, rule, status
            saved = (ev.best_floor, ev.best_m)
            ev.best_floor, ev.best_m = 1, 10 ** 9
            res = ev.evaluate(seq)
            if res["floor"] < saved[0] or (res["floor"] == saved[0] and res["m"] >= saved[1]):
                ev.best_floor, ev.best_m = saved
            rows.append(row("ladder", f"{rule}@{size}", res, size))
            starts.append((f"{rule}@{size}", seq))
            log(f"ridge {name} ladder {rule}@{size}: m={res['m']} floor={res['floor']} ({res['source']}) "
                f"status={rows[-1]['c_status']} width={rows[-1]['c_width']} nodes={rows[-1]['c_nodes']} "
                f"{(rows[-1]['c_seconds'] or 0):.1f} s", RUN_LOG)
    ladder_best = (ev.best_floor, ev.best_m, ev.best["seq"] if ev.best else None)
    # the search
    ev.cap = RIDGE_SEARCH_CAP
    if from_recorded:
        rec = recorded_sequence()
        starts = [("recorded_m70", rec)]
        res = ev.evaluate(rec)
        rows.append(row("recorded", "least-c@70 (record)", res, 70))
        log(f"ridge {name} recorded m70: floor={res['floor']} ({res['source']}) status={rows[-1]['c_status']} "
            f"nodes={rows[-1]['c_nodes']} {(rows[-1]['c_seconds'] or 0):.1f} s", RUN_LOG)
    else:
        def start_key(ls):
            cur, alive, _ = replay(adj, ls[1])
            labels, edges = minor_graph(cur, alive)
            hit = ev.cache.get(edges_sha256(len(labels), edges), {})
            return (-(hit.get("floor") or 1), len(labels))
        starts.sort(key=start_key)   # best floor first, smaller minor first
    before = ev.calls
    calls_seen = {k for k in ev.cache}
    _orig = ev.evaluate

    def evaluate_logged(seq, record_proposals=False):
        res = _orig(seq, record_proposals)
        if not res["cached"] and res["source"] != "skipped":
            rows.append(row("search", "move", res))
            if res["floor"] >= ev.best_floor:
                log(f"ridge {name} search: m={res['m']} floor={res['floor']} ({res['source']}) best {ev.best_floor}@{ev.best_m}", RUN_LOG)
        return res

    ev.evaluate = evaluate_logged  # type: ignore[method-assign]
    trace = search(ev, rng_seed, starts=starts, moves_per_restart=10)
    ev.evaluate = _orig  # type: ignore[method-assign]
    total = time.monotonic() - t0
    out = {"instance_name": name, "n": n, "optimum": optimum, "seconds_budget": seconds, "seconds": total,
           "ladder_floor": ladder_best[0], "ladder_m": ladder_best[1] if ladder_best[2] is not None else None,
           "search_floor": ev.best_floor, "search_m": ev.best_m if ev.best else None,
           "search_source": ev.best["source"] if ev.best else "none", "calls": ev.calls, "search_calls": ev.calls - before,
           "skipped": ev.skipped, "c_seconds": ev.seconds_c, "restarts": trace["restarts"], "moves": trace["moves"],
           "reached_optimum": ev.best_floor >= optimum, "from_recorded": from_recorded}
    d = RIDGE_DIR / safe_name(name)
    d.mkdir(parents=True, exist_ok=True)
    write_standard_instance(d / "instance.mosp", name, matrix)
    if ev.best is not None and ev.best.get("c") is not None:
        cert = certificate(name, matrix, adj, ev.best, total, "ridge-search" if not from_recorded else "ridge-from-recorded",
                           optimum, ev.best.get("cap", RIDGE_SEARCH_CAP))
        (d / "search.json").write_text(json.dumps(cert, indent=1))
        out["certificate"] = str((d / "search.json").relative_to(ROOT))
    pd.DataFrame(rows).to_csv(d / "calls.csv", index=False)
    out["rows"] = rows
    return out


def ridge(names: list[str], core_hours: float, workers: int = 2, rng_seed: int = 1) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    inst = corpus_instances()
    per = core_hours * 3600 / max(1, len(names))
    jobs = []
    for nm in names:
        sol = solution_record(nm)
        jobs.append((nm, np.asarray(inst[nm][1].matrix, dtype=int), sol["ordering"], int(led.loc[nm, "optimum"]), per,
                     rng_seed, nm == "Random-125-125-2-3_0"))
    log(f"ridge: {names}, {per:.0f} s each, ladder cap {RIDGE_LADDER_CAP} s at sizes {RIDGE_SIZES}, search cap "
        f"{RIDGE_SEARCH_CAP} s, binary {binary_sha256()[:16]}")
    with Pool(min(workers, len(jobs))) as pool:
        outs = list(pool.imap_unordered(_ridge_job, jobs))
    calls = [r for o in outs for r in o.pop("rows")]
    pd.DataFrame(calls).to_csv(RIDGE_CSV, index=False)
    pd.DataFrame(outs).to_csv(OUT / "ridge_summary.csv", index=False)
    for o in outs:
        log(f"ridge done {o['instance_name']}: ladder {o['ladder_floor']}@{o['ladder_m']}, search {o['search_floor']}@"
            f"{o['search_m']} ({o['search_source']}), opt {o['optimum']}, {o['calls']} C calls, {o['seconds']:.0f} s")
    return pd.DataFrame(calls)


# ----------------------------------------------------------------------------
# stage: validate
# ----------------------------------------------------------------------------


def _validate_job(args) -> dict:
    name, matrix, ordering, optimum, seconds = args
    from learning.first_moment import vertex_separation_brute

    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    position = None
    if ordering is not None:
        opening, _ = witness_layouts(matrix, ordering)
        position = [0] * n
        for i, v in enumerate(opening):
            position[v] = i
    ev = Evaluator(adj, None, C_CAP_SECONDS, position, deadline=time.monotonic() + seconds)
    # force every candidate through the C program: no skip (best_floor stays 1 only if nothing proves more,
    # so record proposals by evaluating with the skip disabled)
    ev.best_floor, ev.best_m = 1, 10 ** 9
    checked, disagreements, proposals = 0, [], 0
    seen = set()

    def check_all():
        nonlocal checked, proposals
        for madj, pw, source in ev.proposals:
            key = tuple(madj)
            if key in seen:
                continue
            seen.add(key)
            proposals += 1
            if pw is None or len(madj) > 16:
                continue
            brute = vertex_separation_brute(madj)
            checked += 1
            if source in ("c_refutation", "c_bound") and pw != brute:
                disagreements.append({"m": len(madj), "c": pw, "brute": brute, "source": source})
            elif source == "c_lower" and pw > brute:
                disagreements.append({"m": len(madj), "c": pw, "brute": brute, "source": source})
        ev.proposals.clear()

    # every ladder point, with the skip disabled (best_floor reset before each evaluation)
    for rule in RULES:
        full = greedy_sequence(adj, 0, rule)
        for frac in LADDER_FRACTIONS:
            size = max(MIN_MINOR, int(round(frac * n)))
            ev.best_floor, ev.best_m = 1, 10 ** 9
            ev.evaluate(full[:max(0, n - size)], record_proposals=True)
    check_all()
    # the search's proposals (its own skip rule in force; the C runs on what the search sends)
    ev.best_floor, ev.best_m, ev.best = 1, 10 ** 9, None
    ev.optimum = None
    ev.deadline = time.monotonic() + seconds
    _orig = ev.evaluate

    def evaluate_recording(seq, record_proposals=True):
        return _orig(seq, record_proposals=True)

    ev.evaluate = evaluate_recording  # type: ignore[method-assign]
    search(ev, 3)
    check_all()
    return {"instance_name": name, "n": n, "optimum": optimum, "minors_checked": checked, "minors_proposed": proposals,
            "disagreements": len(disagreements), "detail": json.dumps(disagreements[:3]), "c_calls": ev.calls}


def validate_small(count: int = 50, workers: int = 8, seconds: float = 10.0, rng_seed: int = 0) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    pool_names = [nm for nm in target_names("small") if int(led.loc[nm, "n"]) <= 16]
    rng = np.random.default_rng(rng_seed)
    names = [pool_names[i] for i in sorted(rng.choice(len(pool_names), size=min(count, len(pool_names)), replace=False))]
    inst = corpus_instances()
    jobs = []
    for nm in names:
        sol = solution_record(nm)
        jobs.append((nm, np.asarray(inst[nm][1].matrix, dtype=int), sol["ordering"] if sol else None,
                     int(led.loc[nm, "optimum"]), seconds))
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_validate_job, jobs))
    frame = pd.DataFrame(rows).sort_values("instance_name")
    frame.to_csv(OUT / "validation_small.csv", index=False)
    return frame


RECORDED = (
    # (label, instance name or edge-list file, certificate, pairs convention, expected proved pathwidth)
    ("Random-125-125-2-3_0_m70", "Random-125-125-2-3_0", "reports/scratch/minor_certificates/Random-125-125-2-3_0_m70.json", 20),
    ("Random-125-125-2-1_0_m87", "Random-125-125-2-1_0", "reports/scratch/minor_certificates/Random-125-125-2-1_0_m87.json", 23),
    ("Random-125-125-6-1_0_m120", "Random-125-125-6-1_0", "reports/scratch/minor_certificates/Random-125-125-6-1_0_m120.json", 80),
    ("SP4_m96", "SP4", "reports/scratch/minor_certificates/SP4_m96.json", 52),
    ("myciel6_m58", "reports/scratch/minor_certificates/myciel6_full_edges.txt", "reports/scratch/minor_certificates/myciel6_m58.json", 38),
    ("myciel7_m110", "reports/scratch/minor_certificates/myciel7_full_edges.txt", "reports/scratch/minor_certificates/myciel7_m110.json", 71),
)


def recorded_to_certificate(label: str, source: str, cert_path: Path, expected_pw: int, out_dir: Path) -> tuple[Path, Path]:
    """Convert one of `reports/minor_bound_verification.md`'s certificates
    (`[keep, absorbed]` pairs, by `mc_graph.py`) to this item's format
    (`[absorbed, keep]`) and write it with its instance beside it."""
    rec = json.loads(Path(cert_path).read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    if source.endswith(".txt"):
        inst_path = out_dir / f"{label}_graph.txt"
        inst_path.write_text(Path(source).read_text())
        text = Path(source).read_text().split()
        n, e = int(text[0]), int(text[1])
        adj = [0] * n
        vals = [int(x) for x in text[2:2 + 2 * e]]
        for a, b in zip(vals[0::2], vals[1::2]):
            adj[a] |= 1 << b
            adj[b] |= 1 << a
        matrix = None
    else:
        inst = corpus_instances()[source][1]
        matrix = np.asarray(inst.matrix, dtype=int)
        adj = adjacency_from_matrix(matrix)
        inst_path = out_dir / f"{label}_instance.mosp"
        write_standard_instance(inst_path, source, matrix)
    seq = [(int(b), int(a)) for a, b in rec["contraction_sequence"]]
    cur, alive, branch = replay(adj, seq)
    labels, edges = minor_graph(cur, alive)
    cert = {
        "format": "obstruction-minor-1", "instance_name": source if matrix is not None else label, "n": len(adj),
        "matrix_sha256": matrix_sha256(matrix) if matrix is not None else None,
        "graph_sha256": edges_sha256(len(adj), edge_list(adj)), "graph_edges": len(edge_list(adj)),
        "sequence": [[v, u] for v, u in seq], "m": len(labels), "minor_labels": labels,
        "minor_edges": [[a, b] for a, b in edges], "minor_sha256": edges_sha256(len(labels), edges),
        "recorded_minor_sha256_mc_graph": rec.get("minor_sha256"),
        "pathwidth_proved": expected_pw, "refuted_width": expected_pw - 1, "floor": expected_pw + 1,
        "floor_source": "recorded (rule-free search + checkF, reports/minor_bound_verification.md)",
        "c_status": None, "c_width": None, "c_lower": None, "c_cap_seconds": None,
        "source_certificate": str(cert_path), "method": "recorded",
    }
    cp = out_dir / f"{label}.json"
    cp.write_text(json.dumps(cert, indent=1))
    return inst_path, cp


def validate_recorded(cap: float = 60.0, with_rulefree: bool = False) -> pd.DataFrame:
    """The six recorded certificates through the checker (own replay) and the
    C program at `cap`; `expected` is the width the record refutes plus one."""
    sys.path.insert(0, str(ROOT / "paper1"))
    import obstruction_check as oc  # noqa: E402  (the independent checker; imported, not copied)

    out_dir = OUT / "validation_recorded"
    rows = []
    for label, source, cert_path, expected_pw in RECORDED:
        inst_path, cp = recorded_to_certificate(label, source, Path(cert_path), expected_pw, out_dir)
        t0 = time.monotonic()
        res = oc.check_minor(inst_path, cp, c_cap=cap, c_binary=C_BINARY, rulefree=with_rulefree)
        rows.append({"label": label, "m": res.get("m"), "expected_pw": expected_pw,
                     "replay": res.get("replay_ok"), "hash": res.get("hash_ok"),
                     "c_width": res.get("c_width"), "c_status": res.get("c_status"), "c_lower": res.get("c_lower"),
                     "c_reproduces": res.get("c_ok"), "rulefree": res.get("rulefree"),
                     "verdict": res.get("verdict"), "seconds": time.monotonic() - t0})
        log(f"recorded {label}: {rows[-1]}", VALIDATION_LOG)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "validation_recorded.csv", index=False)
    return frame


def validate(workers: int, count: int, seconds: float, cap: float) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log(f"validate: {count} corpus instances at n <= 16, {seconds} s each; C binary {binary_sha256()[:16]}", VALIDATION_LOG)
    small = validate_small(count, workers, seconds)
    log(f"small: {len(small)} instances, {int(small.minors_checked.sum())} minors checked against "
        f"vertex_separation_brute, {int(small.minors_proposed.sum())} proposed, {int(small.c_calls.sum())} C calls, "
        f"disagreements {int(small.disagreements.sum())}", VALIDATION_LOG)
    if small.disagreements.sum():
        log("STOP: a C-proved width disagrees with brute force: " + small[small.disagreements > 0].to_string(), VALIDATION_LOG)
    rec = validate_recorded(cap)
    log(f"recorded: {len(rec)} certificates, replay ok {int(rec.replay.sum())}, hash ok {int(rec.hash.sum())}, "
        f"C reproduces {int(rec.c_reproduces.fillna(False).astype(bool).sum())}, verdicts {rec.verdict.value_counts().to_dict()}",
        VALIDATION_LOG)


# ----------------------------------------------------------------------------
# stage: check (the checker on every certificate of the run)
# ----------------------------------------------------------------------------


def _check_job(args) -> dict:
    d, cap, rulefree, rulefree_cap = args[:4]
    which = args[4] if len(args) > 4 else "search.json"
    sys.path.insert(0, str(ROOT / "paper1"))
    import obstruction_check as oc

    d = Path(d)
    t0 = time.monotonic()
    cert = json.loads((d / which).read_text())
    cap = float(cert.get("c_cap_seconds") or cap)
    res = oc.check_minor(d / "instance.mosp", d / which, c_cap=cap * 5, c_binary=C_BINARY,
                         rulefree=rulefree, rulefree_cap=rulefree_cap)
    return {"instance_name": res.get("instance_name"), "m": res.get("m"), "floor": res.get("floor_claimed"),
            "replay": res.get("replay_ok"), "hash": res.get("hash_ok"), "c": res.get("c_ok"),
            "c_status": res.get("c_status"), "c_width": res.get("c_width"),
            "rulefree": res.get("rulefree"), "rulefree_seconds": res.get("rulefree_seconds"),
            "verdict": res.get("verdict"), "seconds": time.monotonic() - t0, "certificate": str(d / which)}


def check_all(workers: int, rulefree: bool = True, rulefree_cap: float = 300.0) -> pd.DataFrame:
    """Every `search.json` under `certificates/`, every `ladder.json` whose
    floor is above its search's (the ladder is then the family's certificate
    on that instance), and every `ridge/<instance>/search.json`; the C cap is
    the certificate's own times five."""
    jobs = []
    for d in sorted(CERT_DIR.iterdir()) if CERT_DIR.exists() else []:
        if (d / "search.json").exists():
            jobs.append((str(d), C_CAP_SECONDS, rulefree, rulefree_cap, "search.json"))
            if (d / "ladder.json").exists():
                fs = json.loads((d / "search.json").read_text()).get("floor", 0)
                fl = json.loads((d / "ladder.json").read_text()).get("floor", 0)
                if fl > fs:
                    jobs.append((str(d), C_CAP_SECONDS, rulefree, rulefree_cap, "ladder.json"))
    for d in sorted(RIDGE_DIR.iterdir()) if RIDGE_DIR.exists() else []:
        if (d / "search.json").exists():
            jobs.append((str(d), C_CAP_SECONDS, rulefree, rulefree_cap, "search.json"))
    log(f"check: {len(jobs)} certificates, {workers} workers, rule-free {rulefree} (cap {rulefree_cap} s)")
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_check_job, jobs))
    frame = pd.DataFrame(rows).sort_values(["instance_name", "certificate"])
    frame.to_csv(CHECKER_CSV, index=False)
    log(f"check done: verdicts {frame.verdict.value_counts().to_dict()}, rule-free {frame.rulefree.value_counts().to_dict()}")
    return frame


# ----------------------------------------------------------------------------
# stage: tables
# ----------------------------------------------------------------------------


def _md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) + "\n"


def band_of(n: int) -> str:
    for lo, hi in BANDS:
        if lo <= n <= hi:
            return f"{lo}–{hi}"
    return "?"


def _joined(led: pd.DataFrame) -> pd.DataFrame:
    s = pd.read_csv(SEARCH_CSV)
    s["carried"] = False
    if (OUT / "carried_item04.csv").exists():   # item 05: the 22 Chu & Stuckey gap instances at n <= 60 run by item 04
        c = pd.read_csv(OUT / "carried_item04.csv")
        c["carried"] = True
        s = pd.concat([s, c[~c.instance_name.isin(s.instance_name)]], ignore_index=True)
    s["band"] = s["n"].map(band_of)
    s["gap_ladder"] = s["optimum"] - s["ladder_floor"]
    s["gap_search"] = s["optimum"] - s["search_floor"]
    for col in ("floor0", "lb_best", "tw1", "harper12", "excess", "m", "collection"):
        s[col] = s["instance_name"].map(led[col])
    s["gap_floor0"] = s["optimum"] - s["floor0"]
    s["best_floor"] = s[["floor0", "search_floor"]].max(axis=1)
    s["gap_best"] = s["optimum"] - s["best_floor"]
    s["m_over_n"] = s["search_m"] / s["n"]
    s["ladder_m_over_n"] = s["ladder_m"] / s["n"]
    s["beats_floor0"] = s["search_floor"] > s["floor0"]
    s["beats_ref"] = s["search_floor"] > s[["lb_best", "tw1"]].max(axis=1)
    return s


def write_tables(item: str = "04") -> str:
    led = ledger().set_index("instance_name")
    s = _joined(led)
    order = [f"{lo}–{hi}" for lo, hi in BANDS]
    if item == "05":
        return write_tables_scale(s, led, order)
    parts = [f"# Family M by search: tables (item 04)\n\n*Generated by `python3 -m learning.obstruction_minor --stage tables` "
             f"on {time.strftime('%Y-%m-%d %H:%M')}; {len(s)} instances of `gap338` at n ≤ {int(s.n.max())}.*\n"]

    def band_table(g: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for band in order:
            b = g[g.band == band]
            if not len(b):
                continue
            rows.append({"band": band, "instances": len(b),
                         "ladder gap mean": round(b.gap_ladder.mean(), 2), "ladder tight": int((b.gap_ladder == 0).sum()),
                         "search gap mean": round(b.gap_search.mean(), 2), "search tight": int((b.gap_search == 0).sum()),
                         "search > ladder": int(b.beats_ladder_floor.sum()),
                         "tie, fewer vertices": int(b.beats_ladder_tie.sum()),
                         "search < ladder": int(b.below_ladder.sum()),
                         "floor0 gap mean": round(b.gap_floor0.mean(), 2),
                         "search > floor0": int(b.beats_floor0.sum()),
                         "best gap mean": round(b.gap_best.mean(), 2), "best tight": int((b.gap_best == 0).sum())})
        tot = {"band": "all", "instances": len(g),
               "ladder gap mean": round(g.gap_ladder.mean(), 2), "ladder tight": int((g.gap_ladder == 0).sum()),
               "search gap mean": round(g.gap_search.mean(), 2), "search tight": int((g.gap_search == 0).sum()),
               "search > ladder": int(g.beats_ladder_floor.sum()), "tie, fewer vertices": int(g.beats_ladder_tie.sum()),
               "search < ladder": int(g.below_ladder.sum()), "floor0 gap mean": round(g.gap_floor0.mean(), 2),
               "search > floor0": int(g.beats_floor0.sum()),
               "best gap mean": round(g.gap_best.mean(), 2), "best tight": int((g.gap_best == 0).sum())}
        return pd.DataFrame(rows + [tot])

    parts.append("## (a) Per band: the ladder's floor gap and the search's (optimum units)\n\n" + _md(band_table(s)))
    beat = s[s.beats_ladder_floor]
    parts.append("## (b) Where the search beats the ladder's floor\n\n")
    if len(beat):
        b = beat.copy()
        b["by"] = b.search_floor - b.ladder_floor
        parts.append(_md(b[["instance_name", "n", "optimum", "ladder_floor", "ladder_m", "search_floor", "search_m",
                            "search_source", "by", "search_calls", "search_seconds"]].sort_values(["by", "n"], ascending=[False, True])))
        parts.append(f"\nBy how much: {b.by.value_counts().sort_index().to_dict()}; reaching the optimum: "
                     f"{int(b.search_reached_optimum.sum())} of {len(b)}.\n\n")
    else:
        parts.append("None.\n\n")
    parts.append("## (c) Reaching the optimum\n\n" + _md(pd.DataFrame([{
        "ladder reaches optimum": int(s.ladder_reached_optimum.sum()), "search reaches optimum": int(s.search_reached_optimum.sum()),
        "either": int((s.ladder_reached_optimum | s.search_reached_optimum).sum()),
        "search beats floor0": int(s.beats_floor0.sum()), "search beats max(lb_best, tw+1)": int(s.beats_ref.sum()),
        "best floor tight (floor0 or search)": int((s.gap_best == 0).sum()), "instances": len(s)}])))
    parts.append("## (d) The minimal certifying minor: `m / n` by band and by the ladder's rule\n\n")
    rows = []
    for band in order:
        b = s[s.band == band]
        if not len(b):
            continue
        rows.append({"band": band, "instances": len(b), "search m/n median": round(b.m_over_n.median(), 3),
                     "search m/n IQR": f"{b.m_over_n.quantile(0.25):.2f}–{b.m_over_n.quantile(0.75):.2f}",
                     "ladder m/n median": round(b.ladder_m_over_n.median(), 3),
                     "excess median": round(b.excess.median(), 2),
                     "corr(m/n, excess)": round(b[["m_over_n", "excess"]].corr().iloc[0, 1], 3) if len(b) > 3 else None,
                     "source refutation": int((b.search_source == "c_refutation").sum()),
                     "source bound": int((b.search_source == "c_bound").sum()),
                     "source lower": int((b.search_source == "c_lower").sum())})
    parts.append(_md(pd.DataFrame(rows)))
    parts.append(f"\nLadder rule of the best ladder point: {s.ladder_rule.value_counts(dropna=False).to_dict()}.\n\n")
    parts.append("## (e) Checker verdicts\n\n")
    if CHECKER_CSV.exists():
        c = pd.read_csv(CHECKER_CSV)
        c["checks"] = c.apply(lambda r: "replay+C+rule-free" if r.replay and r.hash and r.c and r.rulefree == "verified"
                              else ("replay+C" if r.replay and r.hash and r.c else ("replay only" if r.replay and r.hash else "rejected")), axis=1)
        parts.append(_md(c.groupby(["verdict", "checks"]).size().reset_index(name="certificates")))
        parts.append(f"\nRule-free outcomes: {c.rulefree.value_counts(dropna=False).to_dict()}; rule-free seconds median "
                     f"{c.rulefree_seconds.median():.2f}, max {c.rulefree_seconds.max():.1f}; checker seconds median {c.seconds.median():.1f}.\n\n")
    else:
        parts.append("(not run)\n\n")
    parts.append("## (f) C calls per instance and seconds\n\n")
    rows = []
    for band in order:
        b = s[s.band == band]
        if not len(b):
            continue
        rows.append({"band": band, "instances": len(b), "budget s": int(b.seconds_budget.iloc[0]),
                     "ladder calls median": b.ladder_calls.median(), "ladder skipped median": b.ladder_skipped.median(),
                     "ladder seconds median": round(b.ladder_seconds.median(), 1),
                     "search calls median": b.search_calls.median(), "search skipped median": b.search_skipped.median(),
                     "search seconds median": round(b.search_seconds.median(), 1),
                     "search moves median": b.search_moves.median(), "search restarts median": b.search_restarts.median(),
                     "ladder core-h": round(b.ladder_seconds.sum() / 3600, 2), "search core-h": round(b.search_seconds.sum() / 3600, 2)})
    parts.append(_md(pd.DataFrame(rows)))
    parts.append(f"\nTotal: ladder {s.ladder_seconds.sum() / 3600:.2f} core-hours, search {s.search_seconds.sum() / 3600:.2f}; "
                 f"C calls {int(s.ladder_calls.sum())} and {int(s.search_calls.sum())}.\n\n")
    parts.append("## (g) By collection\n\n")
    rows = []
    for coll, b in s.groupby("collection"):
        rows.append({"collection": coll, "instances": len(b), "ladder gap mean": round(b.gap_ladder.mean(), 2),
                     "search gap mean": round(b.gap_search.mean(), 2), "search > ladder": int(b.beats_ladder_floor.sum()),
                     "search tight": int((b.gap_search == 0).sum()), "floor0 gap mean": round(b.gap_floor0.mean(), 2),
                     "search > floor0": int(b.beats_floor0.sum())})
    parts.append(_md(pd.DataFrame(rows)))
    s.to_csv(OUT / "joined.csv", index=False)
    text = "".join(parts)
    TABLES_MD.write_text(text)
    return text


def family_e_floor(led: pd.DataFrame) -> pd.Series:
    """Family E's floor on record per instance, in optimum units: the best of
    item 01's Harper at cap 12, item 02's rerun floor and item 03's exact
    floor where a verified certificate proves it."""
    e = led["harper12"].astype(float).copy()
    base = ROOT / "reports" / "scratch" / "obstruction_search"
    for path, col in ((base / "02_expansion" / "floor.csv", "floor"), (base / "03_sat" / "instances.csv", "floor_after")):
        if path.exists():
            f = pd.read_csv(path).set_index("instance_name")[col]
            common = e.index.intersection(f.index)
            e.loc[common] = np.maximum(e.loc[common].values, f.loc[common].astype(float).values)
    return e


RECORD_SEVEN = (   # reports/pathwidth_lower_bounds_survey.md §5: instance, the survey's minor bound (optimum units), at m (rule)
    ("Random-125-125-2-1_0", 24, "87 (min-d)"), ("Random-125-125-2-3_0", 21, "70 (least-c)"),
    ("Random-125-125-2-2_0", None, "none ≤ 95; 100–105 out of budget"), ("Random-125-125-4-1_0", 54, "100 (min-d)"),
    ("Random-125-125-6-1_0", 81, "120 (both)"), ("Random-125-125-8-2_0", 92, "115–120"), ("SP4", 53, "96 (both)"))


def write_tables_scale(s: pd.DataFrame, led: pd.DataFrame, order: list[str]) -> str:
    """Item 05's tables: by Chu & Stuckey class, by band on the gap instances,
    the search against the ladder, the record's seven and family E, the
    minimal certifying minor, the ridge instances, calls, the checker."""
    s["e_floor"] = s["instance_name"].map(family_e_floor(led))
    s["gap_e"] = s["optimum"] - s["e_floor"]
    s["m_tighter"] = np.where(s.search_floor > s.e_floor, "M", np.where(s.search_floor < s.e_floor, "E", "tie"))
    s["is_gap338"] = s["instance_name"].map(led["is_gap338"]).astype(bool)
    s["is_cs200"] = s["instance_name"].map(led["is_cs200"]).astype(bool)
    for col in ("cs_n", "cs_m", "cs_d", "cls"):
        s[col] = s["instance_name"].map(led[col])
    parts = [f"# Family M at scale: tables (item 05)\n\n*Generated by `python3 -m learning.obstruction_minor --stage tables "
             f"--out 05_minor_scale` on {time.strftime('%Y-%m-%d %H:%M')}; {len(s)} instances "
             f"(`cs200` ∪ `gap338` at n > 60; n = {int(s.n.min())}–{int(s.n.max())}).*\n"]

    def agg(g: pd.DataFrame, key: str, val) -> dict:
        return {key: val, "instances": len(g),
                "ladder gap mean": round(g.gap_ladder.mean(), 2), "ladder tight": int((g.gap_ladder == 0).sum()),
                "search gap mean": round(g.gap_search.mean(), 2), "search tight": int((g.gap_search == 0).sum()),
                "search > ladder": int(g.beats_ladder_floor.sum()), "search < ladder": int(g.below_ladder.sum()),
                "floor0 gap mean": round(g.gap_floor0.mean(), 2), "search > floor0": int(g.beats_floor0.sum()),
                "E gap mean": round(g.gap_e.mean(), 2), "M tighter": int((g.m_tighter == "M").sum()),
                "E tighter": int((g.m_tighter == "E").sum()),
                "best gap mean": round((g.optimum - g[["floor0", "search_floor", "e_floor"]].max(axis=1)).mean(), 2),
                "best tight": int((g.optimum == g[["floor0", "search_floor", "e_floor"]].max(axis=1)).sum())}

    cs = s[s.is_cs200].copy()
    rows = [agg(g, "class", cls) for cls, g in cs.groupby("cls", sort=False)]
    rows.sort(key=lambda r: (int(r["class"].split("-")[1]), int(r["class"].split("-")[2]), int(r["class"].split("-")[3])))
    rows.append(agg(cs, "class", "all Chu & Stuckey"))
    parts.append("## (a) By Chu & Stuckey class `(n, m, d)` (the instances this item ran; item 04 covered the 22 "
                 "gap instances at n ≤ 60 separately)\n\n" + _md(pd.DataFrame(rows)))
    gp = s[s.is_gap338]
    rows = [agg(gp[gp.band == b], "band", b) for b in order if len(gp[gp.band == b])] + [agg(gp, "band", "all")]
    parts.append("## (b) The gap instances (`gap338` at n > 60) by band\n\n" + _md(pd.DataFrame(rows)))
    beat = s[s.beats_ladder_floor].copy()
    parts.append("## (c) Where the search beats the ladder's floor\n\n")
    if len(beat):
        beat["by"] = beat.search_floor - beat.ladder_floor
        parts.append(_md(beat[["instance_name", "n", "optimum", "ladder_floor", "ladder_m", "search_floor", "search_m",
                               "search_source", "by", "search_calls", "search_seconds"]].sort_values(["by", "n"], ascending=[False, True])))
        parts.append(f"\nBy how much: {beat.by.value_counts().sort_index().to_dict()}; reaching the optimum: "
                     f"{int(beat.search_reached_optimum.sum())} of {len(beat)}; below the ladder: {int(s.below_ladder.sum())}.\n\n")
    else:
        parts.append("None.\n\n")
    parts.append("## (d) Against the record's seven (survey §5) and the file-backed minors of item 01\n\n")
    rows = []
    rs = pd.read_csv(OUT / "ridge_summary.csv").set_index("instance_name") if (OUT / "ridge_summary.csv").exists() else None
    for nm, survey, at in RECORD_SEVEN:
        r = s[s.instance_name == nm]
        ridge_txt = (f"{int(rs.loc[nm, 'search_floor'])} @ {int(rs.loc[nm, 'search_m'])}" if rs is not None and nm in rs.index
                     and pd.notna(rs.loc[nm, "search_m"]) else None)
        rows.append({"instance": nm, "optimum": int(led.loc[nm, "optimum"]), "survey minor": survey, "at m (rule)": at,
                     "ridge stage": ridge_txt,
                     "file-backed (item 01)": led.loc[nm, "minor"], "ladder": int(r.ladder_floor.iloc[0]) if len(r) else None,
                     "ladder m": int(r.ladder_m.iloc[0]) if len(r) and pd.notna(r.ladder_m.iloc[0]) else None,
                     "search": int(r.search_floor.iloc[0]) if len(r) else None,
                     "search m": int(r.search_m.iloc[0]) if len(r) and pd.notna(r.search_m.iloc[0]) else None,
                     "E floor": r.e_floor.iloc[0] if len(r) else None})
    parts.append(_md(pd.DataFrame(rows)))
    parts.append("## (e) Family M against family E, by class and band: which is tighter where\n\n")
    rows = []
    for cls, g in cs.groupby("cls", sort=False):
        rows.append({"class": cls, "instances": len(g), "M floor gap mean": round(g.gap_search.mean(), 2),
                     "E floor gap mean": round(g.gap_e.mean(), 2), "M tighter": int((g.m_tighter == "M").sum()),
                     "E tighter": int((g.m_tighter == "E").sum()), "tie": int((g.m_tighter == "tie").sum()),
                     "excess median": round(g.excess.median(), 2)})
    rows.sort(key=lambda r: (int(r["class"].split("-")[1]), int(r["class"].split("-")[2]), int(r["class"].split("-")[3])))
    parts.append(_md(pd.DataFrame(rows)))
    rows = []
    for b in order:
        g = s[s.band == b]
        if len(g):
            rows.append({"band": b, "instances": len(g), "M floor gap mean": round(g.gap_search.mean(), 2),
                         "E floor gap mean": round(g.gap_e.mean(), 2), "M tighter": int((g.m_tighter == "M").sum()),
                         "E tighter": int((g.m_tighter == "E").sum()), "tie": int((g.m_tighter == "tie").sum())})
    parts.append("\n" + _md(pd.DataFrame(rows)))
    parts.append("## (f) The minimal certifying minor: `m / n` where the search reaches the optimum\n\n")
    rows = []
    for b in order:
        g = s[(s.band == b) & s.search_reached_optimum]
        if len(g):
            rows.append({"band": b, "at optimum": len(g), "search m/n median": round(g.m_over_n.median(), 3),
                         "search m/n IQR": f"{g.m_over_n.quantile(0.25):.2f}–{g.m_over_n.quantile(0.75):.2f}",
                         "ladder m/n median": round(g[g.ladder_reached_optimum].ladder_m_over_n.median(), 3) if g.ladder_reached_optimum.any() else None,
                         "excess median": round(g.excess.median(), 2)})
    parts.append(_md(pd.DataFrame(rows)))
    parts.append(f"\nSources of the search's floor: {s.search_source.value_counts().to_dict()}; of the ladder's: "
                 f"{s.ladder_source.value_counts().to_dict()}; ladder rule: {s.ladder_rule.value_counts(dropna=False).to_dict()}.\n\n")
    parts.append("## (g) The two ridge instances: every C call of the ridge stage\n\n")
    if RIDGE_CSV.exists():
        r = pd.read_csv(RIDGE_CSV)
        cols = ["instance_name", "phase", "label", "m", "cap", "upper_pw", "floor", "source", "c_width", "c_status", "c_lower",
                "c_nodes", "c_seconds", "cached"]
        parts.append("The ladder points and the recorded certificate (every call; the search's calls are summarised "
                     "below and listed in full in `ridge.csv` and `ridge/<instance>/calls.csv`):\n\n")
        parts.append(_md(r[r.phase != "search"][cols]))
        rows = []
        for nm, g in r[r.phase == "search"].groupby("instance_name"):
            rows.append({"instance": nm, "search calls": len(g), "m range": f"{int(g.m.min())}–{int(g.m.max())}",
                         "cap s": g.cap.iloc[0], "refutations": int((g.c_status == "refutation").sum()),
                         "upper (undecided)": int((g.c_status == "upper").sum()),
                         "widths found (status upper)": g[g.c_status == "upper"].c_width.value_counts().sort_index().to_dict(),
                         "best floor": int(g.floor.max()), "smallest m at best floor": int(g[g.floor == g.floor.max()].m.min()),
                         "nodes median": int(g.c_nodes.median()) if g.c_nodes.notna().any() else None,
                         "C seconds": round(g.c_seconds.sum(), 1)})
        parts.append("\n" + _md(pd.DataFrame(rows)))
        if (OUT / "ridge_summary.csv").exists():
            rs = pd.read_csv(OUT / "ridge_summary.csv").drop(columns=["certificate"], errors="ignore")
            parts.append("\n" + _md(rs))
    else:
        parts.append("(not run)\n\n")
    parts.append("## (h) Checker verdicts\n\n")
    if CHECKER_CSV.exists():
        c = pd.read_csv(CHECKER_CSV)
        c["checks"] = c.apply(lambda r: "replay+C+rule-free" if r.replay and r.hash and r.c and r.rulefree == "verified"
                              else ("replay+C" if r.replay and r.hash and r.c else ("replay only" if r.replay and r.hash else "rejected")), axis=1)
        parts.append(_md(c.groupby(["verdict", "checks"]).size().reset_index(name="certificates")))
        parts.append(f"\nRule-free outcomes: {c.rulefree.value_counts(dropna=False).to_dict()}; rule-free seconds median "
                     f"{c.rulefree_seconds.median():.2f}, max {c.rulefree_seconds.max():.1f}; checker seconds median {c.seconds.median():.1f}, "
                     f"max {c.seconds.max():.1f}; minors m = {int(c.m.min())}–{int(c.m.max())}.\n\n")
    else:
        parts.append("(not run)\n\n")
    parts.append("## (i) C calls per instance and seconds\n\n")
    rows = []
    for b in order:
        g = s[s.band == b]
        if len(g):
            rows.append({"band": b, "instances": len(g), "budget s": int(g.seconds_budget.iloc[0]), "C cap s": g.c_cap.iloc[0],
                         "ladder calls median": g.ladder_calls.median(), "ladder seconds median": round(g.ladder_seconds.median(), 1),
                         "search calls median": g.search_calls.median(), "search skipped median": g.search_skipped.median(),
                         "search seconds median": round(g.search_seconds.median(), 1), "search moves median": g.search_moves.median(),
                         "ladder core-h": round(g.ladder_seconds.sum() / 3600, 2), "search core-h": round(g.search_seconds.sum() / 3600, 2)})
    parts.append(_md(pd.DataFrame(rows)))
    parts.append(f"\nTotal: ladder {s.ladder_seconds.sum() / 3600:.2f} core-hours, search {s.search_seconds.sum() / 3600:.2f}; "
                 f"C calls {int(s.ladder_calls.sum())} and {int(s.search_calls.sum())}; C seconds {s.ladder_c_seconds.sum() / 3600:.2f} "
                 f"and {s.search_c_seconds.sum() / 3600:.2f} core-hours.\n\n")
    nr = OUT / "not_reached.txt"
    parts.append(f"Not reached under the core-hour cap: {nr.read_text().split() if nr.exists() else 'none'}.\n\n")
    s.to_csv(OUT / "joined.csv", index=False)
    text = "".join(parts)
    TABLES_MD.write_text(text)
    return text


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# item 07: the 24 open classes (a lower-bound search only)
# ----------------------------------------------------------------------------

OPEN_OUT = ROOT / "reports" / "scratch" / "obstruction_search" / "07_open"
OPEN_MINOR_CSV = OPEN_OUT / "minor.csv"
OPEN_LADDER_CSV = OPEN_OUT / "minor_ladder_points.csv"
OPEN_CERT_DIR = OPEN_OUT / "certificates"
OPEN_C_CAP = 20.0
OPEN_SECONDS = 900.0
OPEN_FRACTIONS = (0.30, 0.85)          # minors at 30-85% of n only (the item's rule; never above 90%)
OPEN_LADDER_FRACTIONS = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85)
OPEN_RESTART_FRACTIONS = (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85)


def _open_job(args) -> dict:
    rec, seconds, cap, rng_seed = args
    adj = rec["adj"]
    n = len(adj)
    position = None
    if rec.get("layout"):
        position = [0] * n
        for i, v in enumerate(rec["layout"]):
            position[v] = i
    target = int(rec["width"]) + 1              # optimum units: a floor meeting it closes the class
    lo_m, hi_m = int(round(OPEN_FRACTIONS[0] * n)), int(OPEN_FRACTIONS[1] * n)
    out = {"id": rec["id"], "names": rec["names"], "n": n, "m_edges": rec["m"], "width": rec["width"],
           "lower": rec["lower"], "target": target, "min_m": lo_m, "max_m": hi_m, "seconds_budget": seconds, "c_cap": cap}
    t0 = time.monotonic()
    deadline = t0 + seconds
    ev = Evaluator(adj, target, cap, position, deadline=deadline, min_m=lo_m, max_m=hi_m, greedy_upper_max_m=150)
    rows = ladder(ev, OPEN_LADDER_FRACTIONS)
    lad_seconds = time.monotonic() - t0
    lad_floor, lad_m, lad_best = ev.best_floor, ev.best_m if ev.best else None, ev.best
    out.update({"ladder_floor": lad_floor, "ladder_m": lad_m, "ladder_source": lad_best["source"] if lad_best else "none",
                "ladder_calls": ev.calls, "ladder_skipped": ev.skipped, "ladder_seconds": round(lad_seconds, 1),
                "ladder_c_seconds": round(ev.seconds_c, 1), "ladder_points": len(rows)})
    # the search continues from the ladder's evaluator (same cache, same best) for the rest of the budget
    t1 = time.monotonic()
    calls0, skipped0, c0 = ev.calls, ev.skipped, ev.seconds_c
    trace = search(ev, rng_seed, OPEN_RESTART_FRACTIONS) if not ev.done() and not ev.at_optimum() else \
        {"restarts": 0, "moves": 0, "improvements": 0, "accepted": 0, "move_kinds": {}}
    out.update({"search_floor": ev.best_floor, "search_m": ev.best_m if ev.best else None,
                "search_source": ev.best["source"] if ev.best else "none",
                "search_calls": ev.calls - calls0, "search_skipped": ev.skipped - skipped0,
                "search_seconds": round(time.monotonic() - t1, 1), "search_c_seconds": round(ev.seconds_c - c0, 1),
                "search_restarts": trace["restarts"], "search_moves": trace["moves"],
                "search_accepted": trace["accepted"], "search_improvements": trace["improvements"],
                "out_of_range": ev.out_of_range, "seconds": round(time.monotonic() - t0, 1)})
    out["m_pathwidth"] = ev.best_floor - 1 if ev.best else None      # pathwidth units: the proved width of the minor
    out["meets_width"] = ev.best is not None and ev.best_floor >= target
    out["above_width"] = ev.best is not None and ev.best_floor > target
    out["above_floor"] = ev.best is not None and rec["lower"] is not None and ev.best_floor - 1 > int(rec["lower"])
    if ev.best is not None:
        d = OPEN_CERT_DIR / rec["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "instance.txt").write_text(f"{n} {rec['m']}\n" + "".join(f"{a} {b}\n" for a, b in rec["edges"]))
        cert = certificate(rec["id"], np.zeros((0, 0), dtype=int), adj, ev.best, out["seconds"],
                           "ladder" if ev.best is lad_best else "search", None, cap)
        cert.pop("matrix_sha256", None)
        cert.update({"names": rec["names"], "recorded_width": rec["width"], "recorded_floor": rec["lower"],
                     "minor_fraction_window": list(OPEN_FRACTIONS),
                     "units_note": "a dataset class: pathwidth_proved is the minor's proved pathwidth, a lower bound "
                                   "on the class's pathwidth; floor = pathwidth_proved + 1 is in optimum units"})
        (d / "minor.json").write_text(json.dumps(cert, indent=1))
        (d / "ladder_points.json").write_text(json.dumps(rows, indent=1))
        out["certificate"] = str((d / "minor.json").relative_to(ROOT))
    return out


def run_open(workers: int, seconds: float = OPEN_SECONDS, cap: float = OPEN_C_CAP, rng_seed: int = 1,
             ids: list[str] | None = None, core_hours: float | None = None) -> pd.DataFrame:
    """Family M on the 24 open classes (the tree aside): the greedy ladder at
    30-85% then the tabu search for the rest of `seconds`, every minor in
    the 30-85% window, C cap `cap` per call; a floor meeting the recorded
    width closes the class, nothing refutes anything. Instances are not
    started once the budgets committed exceed `core_hours`."""
    from learning.obstruction_ledger import open_class_graphs

    OPEN_OUT.mkdir(parents=True, exist_ok=True)
    recs = open_class_graphs(ids, check_representative=False)
    done = set(pd.read_csv(OPEN_MINOR_CSV)["id"]) if OPEN_MINOR_CSV.exists() else set()
    jobs = [(r, seconds, cap, rng_seed) for r in recs if r["id"] not in done and r["names"] != "BalancedTree_3_5"]
    jobs.sort(key=lambda j: -j[0]["n"])
    if core_hours is not None:
        keep = int(core_hours * 3600 // seconds)
        if keep < len(jobs):
            (OPEN_OUT / "minor_not_reached.txt").write_text("".join(j[0]["id"] + "\n" for j in jobs[keep:]))
            jobs = jobs[:keep]
    log(f"open: {len(recs)} classes, {len(jobs)} to run, {workers} workers, {seconds:g} s each (ladder then search), "
        f"C cap {cap:g} s, minors at {OPEN_FRACTIONS[0]:.0%}-{OPEN_FRACTIONS[1]:.0%} of n, core-hours cap {core_hours}, "
        f"binary {binary_sha256()[:16]}", OPEN_OUT / "run.log")
    t0 = time.monotonic()
    with Pool(workers) as pool:
        for k, row in enumerate(pool.imap_unordered(_open_job, jobs, chunksize=1), 1):
            pd.DataFrame([row]).to_csv(OPEN_MINOR_CSV, mode="a", header=not OPEN_MINOR_CSV.exists(), index=False)
            log(f"  {k}/{len(jobs)} {row['id']} n={row['n']} width {row['width']} floor {row['lower']}: ladder "
                f"{row['ladder_floor'] - 1} search {row['m_pathwidth']} (m {row['search_m']}, {row['search_source']}), "
                f"{row['ladder_calls'] + row['search_calls']} C calls, {row['seconds']} s", OPEN_OUT / "run.log")
    frame = pd.read_csv(OPEN_MINOR_CSV).drop_duplicates("id", keep="last")
    frame.to_csv(OPEN_MINOR_CSV, index=False)
    log(f"open done: {len(frame)} rows, {time.monotonic() - t0:.0f} s wall", OPEN_OUT / "run.log")
    return frame


OPEN_FIELDS = ["id", "collections", "names", "n", "m", "recorded", "started_from_layout", "width", "proof",
               "lower", "nodes", "seconds", "finished", "status", "order", "minor"]   # run_unlimited.py's FIELDS


def open_joined() -> pd.DataFrame:
    """One row per open class: the record, E's ceiling, M's floor, B's floor,
    the tree's theorem, the best new floor (pathwidth units throughout; the
    `*_floor` columns of the run files are optimum units and are converted)."""
    from learning.obstruction_ledger import open_class_graphs

    recs = open_class_graphs(check_representative=True)
    base = pd.DataFrame([{"id": r["id"], "names": r["names"], "collections": r["collections"], "n": r["n"], "m": r["m"],
                          "width": r["width"], "lower": r["lower"], "layout_vs": r["layout_vs"],
                          "representative_matches_record": r["representative_matches_record"]} for r in recs])
    ceil = OPEN_OUT / "ceiling.csv"
    if ceil.exists():
        c = pd.read_csv(ceil).rename(columns={"instance_name": "id"})
        c["e_ceiling_pw"] = c["ceiling"] - 1
        base = base.merge(c[["id", "e_ceiling_pw", "t_star", "levels_below_witness", "seconds"]].rename(
            columns={"seconds": "e_seconds"}), on="id", how="left")
    else:
        base["e_ceiling_pw"] = np.nan
    if OPEN_MINOR_CSV.exists():
        m = pd.read_csv(OPEN_MINOR_CSV)
        m["m_ladder_pw"] = m["ladder_floor"] - 1
        base = base.merge(m[["id", "m_pathwidth", "m_ladder_pw", "search_m", "search_source", "ladder_calls",
                             "search_calls", "seconds", "certificate"]].rename(
            columns={"m_pathwidth": "m_floor_pw", "search_m": "m_minor_vertices", "search_source": "m_source",
                     "seconds": "m_seconds", "certificate": "m_certificate"}), on="id", how="left")
    else:
        base["m_floor_pw"] = np.nan
    bcsv = OPEN_OUT / "branch.csv"
    if bcsv.exists():
        b = pd.read_csv(bcsv)
        base = base.merge(b[["id", "b_pathwidth", "b_potential", "S", "branch_sizes", "c_calls", "seconds", "certificate"]]
                          .rename(columns={"b_pathwidth": "b_floor_pw", "S": "b_S", "c_calls": "b_c_calls",
                                           "seconds": "b_seconds", "certificate": "b_certificate"}), on="id", how="left")
    else:
        base["b_floor_pw"] = np.nan
    tree = OPEN_OUT / "tree_certificate.json"
    base["theorem_pw"] = np.nan
    if tree.exists():
        t = json.loads(tree.read_text())
        base.loc[base["id"] == t.get("id"), "theorem_pw"] = int(t["pathwidth_proved"])
    for col in ("m_floor_pw", "b_floor_pw", "theorem_pw", "e_ceiling_pw"):
        base[col] = pd.to_numeric(base[col], errors="coerce")
    base["best_new_floor_pw"] = base[["m_floor_pw", "b_floor_pw", "theorem_pw"]].max(axis=1)
    base["best_family"] = base.apply(lambda r: "theorem" if r["theorem_pw"] == r["best_new_floor_pw"] and pd.notna(r["theorem_pw"])
                                     else ("M" if r["m_floor_pw"] == r["best_new_floor_pw"] and pd.notna(r["m_floor_pw"])
                                           else ("B" if pd.notna(r["b_floor_pw"]) and r["b_floor_pw"] == r["best_new_floor_pw"] else "none")), axis=1)
    base["above_record"] = base["best_new_floor_pw"] > base["lower"]
    base["closed"] = base["best_new_floor_pw"] >= base["width"]
    base["above_width"] = base["best_new_floor_pw"] > base["width"]
    base["e_ceiling_below_width"] = base["e_ceiling_pw"] < base["width"]
    return base


def write_open_rows(joined: pd.DataFrame, checker: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(c) of the item: `results_obstruction.csv` in `run_unlimited.py`'s
    format, one row per class whose new floor meets the recorded width
    (`proof=minor` with the obstruction-minor-1 certificate JSON in `minor`,
    or `proof=theorem` with the B certificate, which `fold` does not read),
    the `order` the stored witness in the representative's labels in the
    dataset's orientation (reversed from the prefix orientation the loop
    uses); and `lower_bounds.csv` for every class with a new floor that does
    not close it. A floor above the recorded width stops the item."""
    from learning.obstruction_ledger import open_class_graphs

    recs = {r["id"]: r for r in open_class_graphs(check_representative=True)}
    verdict = {}
    if checker is not None and not checker.empty:
        verdict = dict(zip(checker["id"], checker["verdict"]))
    rows, lows = [], []
    for _, r in joined.iterrows():
        rec = recs[r["id"]]
        assert rec["representative_matches_record"], r["id"]
        if r["above_width"]:
            raise SystemExit(f"STOP: {r['id']} floor {r['best_new_floor_pw']} above the recorded width {r['width']}")
        if r["closed"]:
            fam = r["best_family"]
            if fam == "theorem":
                proof, cert_path = "theorem", OPEN_OUT / "tree_certificate.json"
                cert = json.loads(cert_path.read_text())
                minor = json.dumps({"format": cert["format"], "theorem": "branch_lemma_separator (Sandwich.lean)",
                                    "pathwidth_proved": cert["pathwidth_proved"], "certificate": str(cert_path.relative_to(ROOT)),
                                    "note": "a family B certificate; paper1.dataset.fold reads proof=minor only"})
                nodes, secs = 0, 0.0
            else:
                cert_path = ROOT / str(r["m_certificate"] if fam == "M" else r["b_certificate"])
                cert = json.loads(cert_path.read_text())
                if fam == "M":
                    proof = "minor"
                    minor = json.dumps({"refuted": int(cert["refuted_width"]), "size": int(cert["m"]),
                                        "rule": "search" if cert["method"] == "search" else "ladder",
                                        "contractions": [[v, None if u < 0 else u] for v, u in cert["sequence"]],
                                        "nodes": int(cert.get("c_nodes") or 0), "certificate": str(cert_path.relative_to(ROOT))})
                    nodes, secs = int(cert.get("c_nodes") or 0), float(cert.get("c_seconds") or 0)
                else:
                    proof = "theorem"
                    minor = json.dumps({"format": cert["format"], "theorem": "branch_lemma_separator (Sandwich.lean)",
                                        "pathwidth_proved": cert["pathwidth_proved"], "certificate": str(cert_path.relative_to(ROOT)),
                                        "note": "a family B certificate; paper1.dataset.fold reads proof=minor only"})
                    nodes, secs = 0, float(cert.get("seconds") or 0)
            order = rec["layout"][::-1]      # the dataset's orientation: prefix boundary |N(T) \ T|
            rows.append({"id": r["id"], "collections": r["collections"].replace("; ", "|"), "names": r["names"],
                         "n": r["n"], "m": r["m"], "recorded": r["width"], "started_from_layout": False,
                         "width": int(r["width"]), "proof": proof, "lower": int(r["best_new_floor_pw"]), "nodes": nodes,
                         "seconds": secs, "finished": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": "ok",
                         "order": json.dumps(order), "minor": minor})
        elif r["above_record"]:
            fam = r["best_family"]
            cert_rel = r["m_certificate"] if fam == "M" else (r["b_certificate"] if fam == "B" else "")
            lows.append({"id": r["id"], "names": r["names"], "n": r["n"], "m": r["m"], "recorded_width": r["width"],
                         "recorded_floor": r["lower"], "new_floor": int(r["best_new_floor_pw"]), "family": fam,
                         "certificate": cert_rel, "checker_verdict": verdict.get(r["id"], "not checked")})
    out = pd.DataFrame(rows, columns=OPEN_FIELDS)
    out.to_csv(OPEN_OUT / "results_obstruction.csv", index=False)
    low = pd.DataFrame(lows, columns=["id", "names", "n", "m", "recorded_width", "recorded_floor", "new_floor", "family",
                                      "certificate", "checker_verdict"])
    low.to_csv(OPEN_OUT / "lower_bounds.csv", index=False)
    return out, low


def _open_check_job(args) -> dict:
    cid, inst, cert, kind = args
    sys.path.insert(0, str(ROOT / "paper1"))
    import obstruction_check as oc

    t0 = time.monotonic()
    if kind == "minor":
        res = oc.check_minor(Path(inst), Path(cert), c_cap=OPEN_C_CAP * 5, rulefree=True, rulefree_cap=120.0)
    else:
        res = oc.check_branch(Path(inst), Path(cert), c_cap=OPEN_C_CAP * 5)
    bad = [c["check"] for c in res["checks"] if not c["ok"]]
    return {"id": cid, "kind": kind, "certificate": str(Path(cert).relative_to(ROOT)), "verdict": res["verdict"],
            "pathwidth_proved": (res.get("proves") or {}).get("pathwidth_at_least"),
            "c_status": res.get("c_status"), "c_width": res.get("c_width"), "rulefree": res.get("rulefree"),
            "nodes_checked": res.get("nodes_checked"), "c_reruns": res.get("c_reruns"),
            "contradiction": bool(res.get("contradiction")), "failed_checks": "; ".join(bad),
            "seconds": round(time.monotonic() - t0, 1)}


def open_check_all(workers: int = 4) -> pd.DataFrame:
    """Every certificate of the item through the independent checker: the
    tree (`check-branch`, no C), every M certificate (`check-minor`, the C
    re-proof at cap x5, rule-free where the minor has at most 80 vertices)
    and every B certificate with a value (`check-branch`)."""
    jobs = []
    tree = OPEN_OUT / "tree_certificate.json"
    if tree.exists():
        jobs.append(("pwc-15933", OPEN_OUT / "tree_instance.txt", tree, "branch"))
    for d in sorted(OPEN_CERT_DIR.glob("pwc-*")):
        if (d / "minor.json").exists():
            jobs.append((d.name, d / "instance.txt", d / "minor.json", "minor"))
        if (d / "branch.json").exists():
            jobs.append((d.name, d / "instance.txt", d / "branch.json", "branch"))
    log(f"open check: {len(jobs)} certificates, {workers} workers", OPEN_OUT / "run.log")
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_open_check_job, jobs))
    frame = pd.DataFrame(rows).sort_values(["id", "kind"])
    frame.to_csv(OPEN_OUT / "checker_verdicts.csv", index=False)
    log(f"open check: {int((frame['verdict'] == 'verified').sum())} of {len(frame)} verified", OPEN_OUT / "run.log")
    return frame


def write_open_tables() -> str:
    j = open_joined()
    checker = pd.read_csv(OPEN_OUT / "checker_verdicts.csv") if (OPEN_OUT / "checker_verdicts.csv").exists() else None
    if checker is not None:
        cv = checker[checker["kind"] == "minor"].set_index("id")["verdict"] if "kind" in checker else pd.Series(dtype=str)
        j["m_checker"] = j["id"].map(cv)
        bv = checker[checker["kind"] == "branch"].set_index("id")["verdict"]
        j["b_checker"] = j["id"].map(bv)
    j.to_csv(OPEN_OUT / "joined.csv", index=False)
    rows, low = write_open_rows(j, checker)
    cols = ["id", "names", "n", "m", "width", "lower", "e_ceiling_pw", "m_floor_pw", "m_ladder_pw", "m_minor_vertices",
            "b_floor_pw", "b_potential", "theorem_pw", "best_new_floor_pw", "best_family", "above_record", "closed"]
    cols = [c for c in cols if c in j.columns]
    tab = j[cols].copy()
    for c in ("e_ceiling_pw", "m_floor_pw", "m_ladder_pw", "b_floor_pw", "b_potential", "theorem_pw", "best_new_floor_pw",
              "m_minor_vertices"):
        if c in tab:
            tab[c] = tab[c].map(lambda x: "" if pd.isna(x) else str(int(x)))
    md = ["## Item 07 tables (pathwidth units: a dataset class's width is a pathwidth)", "",
          "### (a) The 24 open classes: record, E ceiling, M floor, B floor, theorem, best new floor", "",
          _md(tab), "",
          "### (b) Counts", "",
          f"- classes: {len(j)}; closed by this item: {int(j['closed'].sum())} ({', '.join(j.loc[j['closed'], 'id'])})",
          f"- new floor above the recorded floor: {int(j['above_record'].sum())}; above the recorded width: {int(j['above_width'].sum())} (must be 0)",
          f"- E ceiling below the recorded width (Harper cannot close the class under any computation): "
          f"{int(j['e_ceiling_below_width'].sum())} of {int(j['e_ceiling_pw'].notna().sum())} with a ceiling",
          f"- M floor = width − 1: {int((j['m_floor_pw'] == j['width'] - 1).sum())}; M floor above the recorded floor: "
          f"{int((j['m_floor_pw'] > j['lower']).sum())}; search above the ladder: {int((j['m_floor_pw'] > j['m_ladder_pw']).sum())}",
          f"- B with a linked triple: {int(j['b_floor_pw'].notna().sum())}; B above the recorded floor: "
          f"{int((j['b_floor_pw'] > j['lower']).sum())}",
          f"- evidence rows written: {len(rows)} (results_obstruction.csv); non-closing floors: {len(low)} (lower_bounds.csv)", ""]
    if checker is not None:
        md += ["### (c) Checker", "", _md(checker[["id", "kind", "verdict", "pathwidth_proved", "c_status", "rulefree",
                                                   "nodes_checked", "c_reruns", "seconds"]]), ""]
    (OPEN_OUT / "tables.md").write_text("\n".join(md))
    return "\n".join(md)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("validate", "run", "ridge", "check", "tables", "open", "open-check", "open-tables"), required=True)
    ap.add_argument("--out", default="04_minor", help="output directory under reports/scratch/obstruction_search/")
    ap.add_argument("--targets", default="gap338", help="comma-separated target sets (their union)")
    ap.add_argument("--max-n", type=int, default=60)
    ap.add_argument("--min-n", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seconds", default="60,120", help="per instance at n <= 40, 41-60, 61-100, 101+ (last repeats)")
    ap.add_argument("--core-hours", type=float, default=None, help="run: stop starting instances at this many core-hours")
    ap.add_argument("--order", choices=("large-first", "small-first"), default="large-first")
    ap.add_argument("--instances", default="Random-125-125-2-2_0,Random-125-125-2-3_0", help="ridge: instance names")
    ap.add_argument("--item", default=None, help="tables: 04 or 05 (default from --out)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--wall", type=float, default=None)
    ap.add_argument("--count", type=int, default=50, help="validate: corpus instances at n <= 16")
    ap.add_argument("--validate-seconds", type=float, default=10.0)
    ap.add_argument("--cap", type=float, default=60.0, help="validate: C cap on the recorded minors")
    ap.add_argument("--no-rulefree", action="store_true")
    ap.add_argument("--rulefree-cap", type=float, default=300.0)
    ap.add_argument("--ids", default=None, help="open: comma-separated class ids (default all 24)")
    ap.add_argument("--open-seconds", type=float, default=OPEN_SECONDS, help="open: seconds per class")
    args = ap.parse_args()
    set_out(args.out)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "open":
        run_open(args.workers, args.open_seconds, args.cap if args.cap != 60.0 else OPEN_C_CAP, args.seed,
                 args.ids.split(",") if args.ids else None, args.core_hours)
        return
    if args.stage == "open-check":
        print(open_check_all(args.workers).to_string())
        return
    if args.stage == "open-tables":
        print(write_open_tables())
        return
    if args.stage == "validate":
        validate(args.workers, args.count, args.validate_seconds, args.cap)
    elif args.stage == "run":
        seconds = tuple(int(x) for x in args.seconds.split(","))
        run(args.targets, args.max_n, args.workers, seconds, args.seed, args.limit, args.wall, args.min_n,
            args.core_hours, args.order)
    elif args.stage == "ridge":
        ridge([x for x in args.instances.split(",") if x], args.core_hours or 2.0, args.workers, args.seed)
    elif args.stage == "check":
        check_all(args.workers, not args.no_rulefree, args.rulefree_cap)
    else:
        print(write_tables(args.item or args.out.split("_")[0]))


if __name__ == "__main__":
    main()
