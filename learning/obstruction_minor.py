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

RULES = ("min-d", "least-c")
LADDER_FRACTIONS = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
RESTART_FRACTIONS = (0.50, 0.60, 0.70, 0.80, 0.90, 0.95)
TENURE = 10
MOVES_PER_RESTART = 25
C_CAP_SECONDS = 2.0      # per C call at n <= 60 (plan §0.5 (e))
MIN_MINOR = 3


def log(msg: str, path: Path = RUN_LOG) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(path, "a") as fh:
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
           "layout": None}
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
        upper = vertex_separation(madj, greedy_layout(madj)) if m else 0
        if self.position is not None and m:
            upper = min(upper, vertex_separation(madj, lifted_layout(labels, branch, self.position)))
        res = {"m": m, "edges": edges, "labels": labels, "hash": key, "upper_pw": upper, "seq": list(seq),
               "floor": None, "source": "skipped", "c": None, "cached": False}
        # upper + 1 is an upper bound on the floor this minor could certify
        if m < MIN_MINOR or upper + 1 < self.best_floor or (upper + 1 == self.best_floor and m >= self.best_m):
            self.skipped += 1
            res["floor"] = 1
            self.cache[key] = res
            return res
        cap = min(self.cap, max(0.05, self.time_left()))
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
           moves_per_restart: int = MOVES_PER_RESTART) -> dict:
    """Tabu local search over contraction sequences; returns the trace."""
    rng = random.Random(rng_seed)
    n = len(ev.adj)
    starts = []
    for rule in RULES:
        full = greedy_sequence(ev.adj, 0, rule)
        for frac in restart_fractions:
            size = max(MIN_MINOR, int(round(frac * n)))
            starts.append((f"{rule}@{frac:.2f}", full[:max(0, n - size)]))
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
                optimum: int | None) -> dict:
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
        "c_command": f"printf '%s\\n' \"$g6\" | nice -n 19 pathwidth_solver/cli/pathwidth -t {C_CAP_SECONDS:g} -l -v -m min_vertices=1000000",
        "c_cap_seconds": C_CAP_SECONDS,
        "c_stdout": c["stdout"], "c_stderr": c["stderr"], "c_seconds": c["seconds"],
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
    name, matrix, ordering, optimum, seconds, rng_seed, write = args
    matrix = np.asarray(matrix, dtype=int)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    position = None
    if ordering is not None:
        opening, _ = witness_layouts(matrix, ordering)
        position = [0] * n
        for i, v in enumerate(opening):
            position[v] = i
    out = {"instance_name": name, "n": n, "optimum": optimum, "seconds_budget": seconds}
    # the ladder
    t0 = time.monotonic()
    ev_l = Evaluator(adj, optimum, C_CAP_SECONDS, position, deadline=t0 + seconds)
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
    ev_s = Evaluator(adj, optimum, C_CAP_SECONDS, position, deadline=t1 + seconds)
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
        cert = certificate(name, matrix, adj, ev_s.best, s_seconds, "search", optimum)
        (d / "search.json").write_text(json.dumps(cert, indent=1))
        if ev_l.best is not None:
            certl = certificate(name, matrix, adj, ev_l.best, lad_seconds, "ladder", optimum)
            (d / "ladder.json").write_text(json.dumps(certl, indent=1))
        (d / "ladder_points.json").write_text(json.dumps(rows, indent=1))
        out["certificate"] = str((d / "search.json").relative_to(ROOT))
    return out


def run(which: str, max_n: int, workers: int, seconds: tuple[int, int], rng_seed: int = 1,
        limit: int | None = None, wall: float | None = None) -> pd.DataFrame:
    led = ledger().set_index("instance_name")
    names = [nm for nm in target_names(which) if int(led.loc[nm, "n"]) <= max_n]
    if limit:
        names = names[:limit]
    inst = corpus_instances()
    done = set()
    if SEARCH_CSV.exists():
        done = set(pd.read_csv(SEARCH_CSV)["instance_name"])
    jobs = []
    for nm in names:
        if nm in done:
            continue
        n = int(led.loc[nm, "n"])
        sol = solution_record(nm)
        budget = seconds[0] if n <= 40 else seconds[1]
        jobs.append((nm, np.asarray(inst[nm][1].matrix, dtype=int), sol["ordering"] if sol else None,
                     int(led.loc[nm, "optimum"]), budget, rng_seed, True))
    jobs.sort(key=lambda j: -len(j[1]))
    log(f"run: {len(names)} targets ({which}, n <= {max_n}), {len(jobs)} to do, {workers} workers, "
        f"seconds {seconds}, binary {binary_sha256()[:16]}")
    t0 = time.monotonic()
    rows = []
    with Pool(workers) as pool:
        for k, row in enumerate(pool.imap_unordered(_job, jobs), 1):
            rows.append(row)
            part = pd.DataFrame([row])
            part.to_csv(SEARCH_CSV, mode="a", header=not SEARCH_CSV.exists(), index=False)
            if k % 10 == 0 or k == len(jobs):
                log(f"  {k}/{len(jobs)} done, {time.monotonic() - t0:.0f} s wall; last {row['instance_name']!r}: "
                    f"ladder {row['ladder_floor']} search {row['search_floor']} opt {row['optimum']}")
            if wall and time.monotonic() - t0 > wall:
                log("  wall budget reached; stopping")
                pool.terminate()
                break
    frame = pd.read_csv(SEARCH_CSV) if SEARCH_CSV.exists() else pd.DataFrame(rows)
    # the ladder's per-point table
    lad = []
    for d in sorted(CERT_DIR.iterdir()) if CERT_DIR.exists() else []:
        p = d / "ladder_points.json"
        if p.exists():
            nm = (d / "instance.mosp").read_text().splitlines()[0].strip()
            for r in json.loads(p.read_text()):
                lad.append({"instance_name": nm, **r})
    pd.DataFrame(lad).to_csv(LADDER_CSV, index=False)
    log(f"run done: {len(frame)} rows, {time.monotonic() - t0:.0f} s wall")
    return frame


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
    d, cap, rulefree, rulefree_cap = args
    sys.path.insert(0, str(ROOT / "paper1"))
    import obstruction_check as oc

    d = Path(d)
    t0 = time.monotonic()
    res = oc.check_minor(d / "instance.mosp", d / "search.json", c_cap=cap * 5, c_binary=C_BINARY,
                         rulefree=rulefree, rulefree_cap=rulefree_cap)
    return {"instance_name": res.get("instance_name"), "m": res.get("m"), "floor": res.get("floor_claimed"),
            "replay": res.get("replay_ok"), "hash": res.get("hash_ok"), "c": res.get("c_ok"),
            "c_status": res.get("c_status"), "c_width": res.get("c_width"),
            "rulefree": res.get("rulefree"), "rulefree_seconds": res.get("rulefree_seconds"),
            "verdict": res.get("verdict"), "seconds": time.monotonic() - t0, "certificate": str(d / "search.json")}


def check_all(workers: int, rulefree: bool = True, rulefree_cap: float = 300.0) -> pd.DataFrame:
    dirs = [d for d in sorted(CERT_DIR.iterdir()) if (d / "search.json").exists()]
    log(f"check: {len(dirs)} certificates, {workers} workers, rule-free {rulefree} (cap {rulefree_cap} s)")
    with Pool(workers) as pool:
        rows = list(pool.imap_unordered(_check_job, [(str(d), C_CAP_SECONDS, rulefree, rulefree_cap) for d in dirs]))
    frame = pd.DataFrame(rows).sort_values("instance_name")
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


def write_tables() -> str:
    led = ledger().set_index("instance_name")
    s = pd.read_csv(SEARCH_CSV)
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
    order = [f"{lo}–{hi}" for lo, hi in BANDS]
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


# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("validate", "run", "check", "tables"), required=True)
    ap.add_argument("--targets", default="gap338")
    ap.add_argument("--max-n", type=int, default=60)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seconds", default="60,120", help="per instance at n <= 40, at 41-60")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--wall", type=float, default=None)
    ap.add_argument("--count", type=int, default=50, help="validate: corpus instances at n <= 16")
    ap.add_argument("--validate-seconds", type=float, default=10.0)
    ap.add_argument("--cap", type=float, default=60.0, help="validate: C cap on the recorded minors")
    ap.add_argument("--no-rulefree", action="store_true")
    ap.add_argument("--rulefree-cap", type=float, default=300.0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "validate":
        validate(args.workers, args.count, args.validate_seconds, args.cap)
    elif args.stage == "run":
        seconds = tuple(int(x) for x in args.seconds.split(","))
        run(args.targets, args.max_n, args.workers, seconds, args.seed, args.limit, args.wall)
    elif args.stage == "check":
        check_all(args.workers, not args.no_rulefree, args.rulefree_cap)
    else:
        print(write_tables())


if __name__ == "__main__":
    main()
