"""A proof object for the customer search (plan 3 §1 Q1b, loop0004 item 05).

The complete customer search (`satisfiability/customer_search.py` and `.c`)
refutes "MOSP(I) ≤ k?" by exhausting a tree of closing orders pruned by Chu &
Stuckey's dominance rules, and until now left nothing behind that anyone could
check: two false refutations survived every audit because every audit only
confirmed that values are *achievable* (`reports/better_move_bug.md`). This
module defines a **search certificate** -- the tree a refutation leaves, with
every pruning decision named by its rule and its witness -- an **emitter** that
records one from an instrumented copy of the search, and an **independent
checker** that verifies every premise from the instance and the state and
confirms that the tree is exhaustive, without running any dominance rule of
its own.

**The certificate.** One record per search node, in the order the search
visited them. A node carries the customer whose closing reached it (`move`),
the free moves it closed (`free`), its kind (`refuted`, `memo` citing an earlier
node with the same closed set, `sat` or `aborted`, which are not refutations),
its pruning `steps` and its `children`. A step is one of

    ["definite", q]        Theorem 1: q keeps, every other candidate goes;
                           witness: q, checked as close(q,S) ≥ open(q,S)
    ["subset", r, d]       the subset rule: r goes, d dominates it;
                           witness: d, checked as o(d,S) ⊆ o(r,S) with the
                           index tie-break on equality
    ["better", r, q]       Theorem 2: r goes, q covers it; witness: q, checked
                           as S++[q] and S++[r,q] playable in the paper's
                           measure and close(q, S∪{r}) ≥ open(q, S∪{r}) with
                           the corrected count (`reports/better_move_bug.md` §7)

The cost cut and Theorem 3 (old move) record nothing: the checker recomputes
both -- the cost of every candidate from the state, and the set Q(S) of moves
an ancestor already searched from the *path*, with the reinsertion test the
search makes at each descent. The closed set of a node is likewise derived by
the checker from the path, so a certificate is the tree and the witnesses and
nothing else.

**What the checker verifies at each node**, given the state it derived:

1. the listed free moves are exactly the remaining customers whose
   neighbourhood is already opened;
2. the node is not a solution (closed ≠ full);
3. a `memo` node cites an earlier *refuted* node with the same closed set,
   and only when old move is off (see below);
4. every premise of every step holds, recomputed from the instance and the
   state;
5. every candidate with cost ≤ k is a child, or is covered by a step, and
   every chain of coverings ends at a child or -- under old move -- at a
   customer in Q(S), with no cycle;
6. the children, recursively, with Q inherited by the reinsertion test.

Step 5 is what the two historical bugs violate: the 2026-09-26 cross-rule
cycle has every step's premise true and no chain ending anywhere, and the
close-count bug has a `better` step whose premise the checker recomputes as
false. Both are rejected (`tests/test_search_certificate.py`).

**Which steps are locally checkable.** The subset rule, Theorem 1 and Theorem
2 are checkable from the instance and the state alone, step by step -- every
quantity in their premises is a function of `(N, S, O(S), k, r, q)`. What is
*not* a property of one step is its termination: a Theorem 2 step "r goes
because q covers it" is sound only if q is itself explored or covered by a
chain that ends in something explored, and that is a property of the whole
step set at the node (the checker's step 5). Theorem 3 is checkable from the
*path*, not the state: Q(S) is which siblings an ancestor searched, threaded
through the reinsertion tests. The memo is checkable from the state alone only
without old move: with it, a refuted state's subtree may rest on Q entries
inherited from ancestors above the cited node, so the refutation belongs to
the path and a second path reaching the same set has no right to it. The
emitter never combines the two, as the Python reference does not; the C does
(Chu & Stuckey run both), and a certificate of the C's run in that
configuration would need the checker to re-derive the cited subtree under the
new path's Q -- which is a replay, not a lookup. That is the precise form of
the kill criterion's answer, and it concerns Theorem 3 with the memo, not
Theorem 2.

**What the checker trusts.** The three theorems themselves, in the free-move
cost model this search uses (Theorem 2's hypotheses as re-derived in
`reports/better_move_bug.md` §7 and checked there by brute force over 124 M
applications), and the cost cut. It trusts neither the search nor the emitter:
a certificate that checks is a refutation whether or not the program that
produced it was correct. This is the same division as a DRAT proof, which
trusts resolution and not the solver.

**The emitter** is a copy of `decide(native=False)`'s search with the rule
witnesses recorded, extended by a Python port of the C's `better_move` (today's
rule: subset rule first over the remaining customers, Theorem 2 last over its
survivors, corrected close count) so that Theorem 2 steps can be certified at
all -- the Python reference never had the rule. Two measured reverts,
`old_close_count` and `old_rule_order`, reproduce the bugs for the tests. The
emitter agrees with `decide(native=False)` in status and node count on every
configuration it shares, and with the C under `csearch` (`better_move=True`,
`better_move_dominators=0`) -- `tests/test_search_certificate.py`. It certifies
the search under the rules **as Chu & Stuckey publish them**, i.e.
`decide(..., repaired_rules=False)`; the repaired rules became the default on
2026-10-01 (loop0007 item 03) and the emitter does not model them yet.

Run:

    python -m learning.search_certificate --stage run --max-customers 20 --workers 16
    python -m learning.search_certificate --stage run --max-customers 40 --min-customers 21 --workers 16 --deadline 60
    python -m learning.search_certificate --stage tables
    python -m learning.search_certificate --stage one --instance <name> --k <k>   # emit, check, print sizes

Writes `learning/data/ensemble/search_certificate.csv` (one row per instance ×
configuration: status, nodes, steps by rule, bytes raw and gzipped, emit and
check seconds, the checker's verdict, the DRAT verdict of §17 and the lattice
oracle's) and `reports/search_certificate_tables.md`. Nothing is written to
`solutions/`; no solver default is touched; nothing here decides `k` for
anything.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from mosp.instance import MOSPInstance

DATA_DIR = Path("learning/data/ensemble")
DEFAULT_CSV = DATA_DIR / "search_certificate.csv"
DEFAULT_OUT = Path("reports/search_certificate_tables.md")
PROOFS_CSV = Path("learning/data/proofs.csv")
DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")
DEFAULT_SOLUTIONS_DIR = Path("solutions")

CONFIGS = ("default", "csearch", "memo")
RULES = ("definite", "subset", "better")
SIZE_BANDS = ((0, 10), (11, 15), (16, 20), (21, 25), (26, 30), (31, 35), (36, 40),
              (41, 200))


# ----------------------------------------------------------------------------
# instance digest and masks -- the checker's own, sharing nothing with the search
# ----------------------------------------------------------------------------


def matrix_sha256(instance: MOSPInstance) -> str:
    matrix = np.asarray(instance.matrix, dtype=np.int8)
    return hashlib.sha256(matrix.tobytes() + bytes(matrix.shape)).hexdigest()


def neighbourhoods(instance: MOSPInstance) -> list[int]:
    """Self-inclusive neighbourhoods N[c] as bitmasks, from the matrix alone."""
    matrix = np.asarray(instance.matrix)
    n, m = matrix.shape
    masks = [0] * n
    for p in range(m):
        holders = np.flatnonzero(matrix[:, p])
        mask = 0
        for c in holders:
            mask |= 1 << int(c)
        for c in holders:
            masks[int(c)] |= mask
    return masks


def _bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


# ----------------------------------------------------------------------------
# the certificate
# ----------------------------------------------------------------------------


@dataclass
class Node:
    id: int
    parent: int | None
    move: int | None
    free: list[int] = field(default_factory=list)
    kind: str = "refuted"          # refuted | memo | sat | aborted
    memo_of: int | None = None
    steps: list[list[int | str]] = field(default_factory=list)
    children: list[int] = field(default_factory=list)

    def to_json(self) -> dict:
        out = {"id": self.id, "parent": self.parent, "move": self.move}
        if self.free:
            out["free"] = self.free
        if self.kind != "refuted":
            out["kind"] = self.kind
        if self.memo_of is not None:
            out["memo_of"] = self.memo_of
        if self.steps:
            out["steps"] = self.steps
        if self.children:
            out["children"] = self.children
        return out

    @staticmethod
    def from_json(data: dict) -> "Node":
        return Node(id=int(data["id"]), parent=data.get("parent"), move=data.get("move"),
                    free=list(data.get("free", [])), kind=data.get("kind", "refuted"),
                    memo_of=data.get("memo_of"), steps=list(data.get("steps", [])),
                    children=list(data.get("children", [])))


@dataclass
class Certificate:
    instance_name: str
    n_customers: int
    n_patterns: int
    matrix_sha256: str
    k: int
    config: dict
    status: str                    # unsat | sat | unknown
    nodes: list[Node]
    branches: int                  # the search's node count (branch decisions)
    order: list[int] | None = None
    emit_seconds: float = 0.0

    def to_json(self) -> dict:
        return {"format": "mosp-search-certificate-1",
                "instance_name": self.instance_name, "n_customers": self.n_customers,
                "n_patterns": self.n_patterns, "matrix_sha256": self.matrix_sha256,
                "k": self.k, "config": self.config, "status": self.status,
                "branches": self.branches, "order": self.order,
                "nodes": [node.to_json() for node in self.nodes]}

    def dumps(self) -> bytes:
        return json.dumps(self.to_json(), separators=(",", ":")).encode()

    @staticmethod
    def loads(data: bytes | str) -> "Certificate":
        obj = json.loads(data)
        if obj.get("format") != "mosp-search-certificate-1":
            raise ValueError("not a search certificate")
        return Certificate(instance_name=obj["instance_name"], n_customers=obj["n_customers"],
                           n_patterns=obj["n_patterns"], matrix_sha256=obj["matrix_sha256"],
                           k=int(obj["k"]), config=dict(obj["config"]), status=obj["status"],
                           nodes=[Node.from_json(d) for d in obj["nodes"]],
                           branches=int(obj["branches"]), order=obj.get("order"))

    def step_counts(self) -> dict[str, int]:
        counts = {rule: 0 for rule in RULES}
        for node in self.nodes:
            for step in node.steps:
                counts[str(step[0])] += 1
        counts["memo"] = sum(1 for node in self.nodes if node.kind == "memo")
        counts["free"] = sum(len(node.free) for node in self.nodes)
        return counts

    def sizes(self) -> dict[str, int]:
        raw = self.dumps()
        return {"nodes": len(self.nodes), "steps": sum(len(n.steps) for n in self.nodes),
                "bytes": len(raw), "gz_bytes": len(gzip.compress(raw, 9))}


# ----------------------------------------------------------------------------
# the emitter: decide(native=False) with witnesses, plus the C's better move
# ----------------------------------------------------------------------------


def emit(
    instance: MOSPInstance,
    k: int,
    *,
    subset_rule: bool = True,
    definite_move: bool = True,
    old_move: bool = True,
    memo: bool = False,
    better_move: bool = False,
    better_move_dominators: int = 0,
    old_close_count: bool = False,
    old_rule_order: bool = False,
    max_nodes: int | None = None,
    deadline: float | None = None,
) -> Certificate:
    """Search "MOSP(instance) ≤ k?" as `decide(native=False)` does, recording the tree.

    `memo` with `old_move` is refused, as the Python reference refuses it. With
    `better_move` the filter follows today's C: definite move, subset rule over
    the remaining customers, Theorem 2 over the subset survivors with only the
    first `better_move_dominators` (0: all) as dominators. `old_close_count`
    and `old_rule_order` are the two 2026-09-26 bugs, for the tests.
    """
    if old_move and memo:
        raise ValueError("memo cannot be combined with old_move in a certificate: "
                         "a refutation under old move belongs to its path")
    started = time.monotonic()
    masks = neighbourhoods(instance)
    active = [c for c in range(instance.n_customers) if masks[c]]
    full = 0
    for c in active:
        full |= 1 << c
    config = {"subset_rule": subset_rule, "definite_move": definite_move, "old_move": old_move,
              "memo": memo, "better_move": better_move,
              "better_move_dominators": better_move_dominators,
              "old_close_count": old_close_count, "old_rule_order": old_rule_order}

    nodes: list[Node] = []
    path: list[int] = []
    refuted: dict[int, int] = {}
    state = {"branches": 0, "aborted": False}

    def new_node(parent: int | None, move: int | None) -> Node:
        node = Node(id=len(nodes), parent=parent, move=move)
        nodes.append(node)
        return node

    if not active:
        root = new_node(None, None)
        root.kind = "sat"
        return Certificate(instance.name, instance.n_customers, instance.n_patterns,
                           matrix_sha256(instance), k, config, "sat", nodes, 0, [],
                           time.monotonic() - started)

    def search(node: Node, closed: int, opened: int, seen: int) -> bool:
        mark = len(path)
        free = 0
        for c in _bits(full & ~closed):
            if masks[c] & ~opened == 0:
                free |= 1 << c
        for c in _bits(free):
            path.append(c)
        node.free = list(_bits(free))
        closed |= free
        if closed == full:
            node.kind = "sat"
            return True
        if memo and closed in refuted:
            node.kind = "memo"
            node.memo_of = refuted[closed]
            del path[mark:]
            return False

        remaining = full & ~closed
        seen &= remaining
        candidates = remaining & ~seen if old_move else remaining
        opens = {c: masks[c] & ~opened for c in _bits(remaining)}
        playable = [(((opened | masks[c]) & ~closed).bit_count(), c) for c in _bits(candidates)]
        playable = [(cost, c) for cost, c in playable if cost <= k]

        if playable:
            playable = _filter(playable, opens, masks, closed, opened, k, node, config, full)
        playable.sort()

        for _, c in playable:
            state["branches"] += 1
            if max_nodes is not None and state["branches"] > max_nodes:
                state["aborted"] = True
            if (deadline is not None and state["branches"] % 256 == 0
                    and time.monotonic() > deadline):
                state["aborted"] = True
            if state["aborted"]:
                node.kind = "aborted"
                del path[mark:]
                return False
            here = len(path)
            path.append(c)
            inherited = 0
            if old_move and seen:
                for q in _bits(seen):
                    cost = ((opened | masks[q] | masks[c]) & ~(closed | (1 << q))).bit_count()
                    if cost <= k:
                        inherited |= 1 << q
            child = new_node(node.id, c)
            node.children.append(child.id)
            if search(child, closed | (1 << c), opened | masks[c], inherited):
                return True
            del path[here:]
            if state["aborted"]:
                node.kind = "aborted"
                del path[mark:]
                return False
            seen |= 1 << c

        if memo and not state["aborted"]:
            refuted[closed] = node.id
        del path[mark:]
        return False

    root = new_node(None, None)
    found = search(root, 0, 0, 0)
    if found:
        status, order = "sat", list(path)
    elif state["aborted"]:
        status, order = "unknown", None
    else:
        status, order = "unsat", None
    return Certificate(instance.name, instance.n_customers, instance.n_patterns,
                       matrix_sha256(instance), k, config, status, nodes, state["branches"],
                       order, time.monotonic() - started)


def _filter(playable, opens, masks, closed, opened, k, node, config, full):
    """The dominance filter with witnesses, in `decide`'s / the C's order."""
    if config["definite_move"]:
        for cost, q in playable:
            own = opens[q]
            if sum(1 for other in opens.values() if other & ~own == 0) >= own.bit_count():
                node.steps.append(["definite", q])
                return [(cost, q)]
    if not config["better_move"]:
        if config["subset_rule"]:
            playable = _subset_pass(playable, opens, node, exclude=0)
        return playable
    if config["old_rule_order"]:
        playable = _better_pass(playable, masks, closed, opened, k, node, config, full)
        if config["subset_rule"]:
            playable = _subset_pass(playable, opens, node, exclude=0)
    else:
        if config["subset_rule"]:
            playable = _subset_pass(playable, opens, node, exclude=0)
        playable = _better_pass(playable, masks, closed, opened, k, node, config, full)
    return playable


def _subset_pass(playable, opens, node, exclude):
    kept, steps = [], []
    for cost, c in playable:
        own = opens[c]
        dominator = None
        for d, other in opens.items():
            if d == c or (exclude >> d) & 1:
                continue
            if other & ~own == 0 and (other != own or d < c):
                dominator = d
                break
        if dominator is None:
            kept.append((cost, c))
        else:
            steps.append(["subset", c, dominator])
    if not kept:
        return playable
    node.steps.extend(steps)
    return kept


def _better_pass(playable, masks, closed, opened, k, node, config, full):
    """Theorem 2 as the C's `better_move_pass`: an earlier candidate may cover a later one."""
    if len(playable) <= 1:
        return playable
    limit = config["better_move_dominators"]
    limit = len(playable) if limit <= 0 or limit > len(playable) else limit
    survivors, steps = [], []
    for ri, (cost_r, r) in enumerate(playable):
        cover = None
        for qi in range(min(limit, ri)):
            q = playable[qi][1]
            if q == r:
                continue
            if _better_premise(masks, closed, opened, k, r, q, config["old_close_count"], full):
                cover = q
                break
        if cover is None:
            survivors.append((cost_r, r))
        else:
            steps.append(["better", r, cover])
    node.steps.extend(steps)
    return survivors


def _better_premise(masks, closed, opened, k, r, q, old_close_count=False, full=None) -> bool:
    """close(q, S∪{r}) ≥ open(q, S∪{r}) with S++[r,q] playable in the paper's measure."""
    if full is None:
        full = 0
        for c, mask in enumerate(masks):
            if mask:
                full |= 1 << c
    closed_r = closed | (1 << r)
    opened_r = opened | masks[r]
    if ((opened_r | masks[q]) & ~closed_r).bit_count() > k:
        return False
    own = masks[q] & ~opened_r
    opened_by = own.bit_count()
    closed_by = 0
    for d in _bits(full & ~closed_r):
        left = masks[d] & ~opened_r
        if (left or old_close_count) and left & ~own == 0:
            closed_by += 1
    return closed_by >= opened_by


# ----------------------------------------------------------------------------
# the checker
# ----------------------------------------------------------------------------


@dataclass
class CheckResult:
    ok: bool
    reason: str
    nodes: int
    steps: int
    seconds: float


class Rejected(Exception):
    pass


def check(instance: MOSPInstance, cert: Certificate) -> CheckResult:
    """Verify that `cert` is a refutation of "MOSP(instance) ≤ k" (see the module docstring)."""
    started = time.monotonic()
    counted = {"nodes": 0, "steps": 0}
    try:
        _check(instance, cert, counted)
    except Rejected as why:
        return CheckResult(False, str(why), counted["nodes"], counted["steps"],
                           time.monotonic() - started)
    return CheckResult(True, "refutation verified", counted["nodes"], counted["steps"],
                       time.monotonic() - started)


def _check(instance: MOSPInstance, cert: Certificate, counted: dict) -> None:
    if cert.status != "unsat":
        raise Rejected(f"certificate status is {cert.status!r}, not a refutation")
    if cert.matrix_sha256 != matrix_sha256(instance):
        raise Rejected("matrix digest does not match the instance")
    if (cert.n_customers, cert.n_patterns) != (instance.n_customers, instance.n_patterns):
        raise Rejected("instance dimensions do not match")
    config = cert.config
    old_move = bool(config.get("old_move", False))
    memo_allowed = bool(config.get("memo", False)) and not old_move
    if config.get("memo") and old_move:
        raise Rejected("memo references are not checkable under old move: "
                       "a refuted state's subtree may rest on Q inherited along its path")
    k = cert.k
    masks = neighbourhoods(instance)
    full = 0
    for c, mask in enumerate(masks):
        if mask:
            full |= 1 << c
    nodes = {node.id: node for node in cert.nodes}
    if len(nodes) != len(cert.nodes):
        raise Rejected("duplicate node ids")
    if not cert.nodes or cert.nodes[0].parent is not None:
        raise Rejected("no root")
    refuted_states: dict[int, int] = {}    # closed set -> node id, completed refutations
    completed: set[int] = set()

    def visit(node: Node, closed: int, opened: int, seen: int) -> None:
        counted["nodes"] += 1
        # 1. free moves: exactly the remaining customers whose N is opened
        computed_free = 0
        for c in _bits(full & ~closed):
            if masks[c] & ~opened == 0:
                computed_free |= 1 << c
        listed = 0
        for c in node.free:
            listed |= 1 << int(c)
        if listed != computed_free:
            raise Rejected(f"node {node.id}: free moves {node.free} are not the customers "
                           f"whose neighbourhood is opened")
        closed |= computed_free
        # 2. not a solution
        if closed == full:
            raise Rejected(f"node {node.id}: every customer is closed -- the tree holds a solution")
        if node.kind in ("sat", "aborted"):
            raise Rejected(f"node {node.id}: kind {node.kind!r} inside a refutation")
        # 3. memo
        if node.kind == "memo":
            if not memo_allowed:
                raise Rejected(f"node {node.id}: memo reference without memo enabled")
            cited = node.memo_of
            if cited is None or cited not in completed:
                raise Rejected(f"node {node.id}: memo cites node {cited}, not a completed refutation")
            if refuted_states.get(closed) != cited:
                raise Rejected(f"node {node.id}: memo cites node {cited}, whose closed set differs")
            if node.children or node.steps:
                raise Rejected(f"node {node.id}: a memo node carries children or steps")
            return
        if node.kind != "refuted":
            raise Rejected(f"node {node.id}: unknown kind {node.kind!r}")

        remaining = full & ~closed
        seen &= remaining
        candidates = remaining & ~seen if old_move else remaining
        opens = {c: masks[c] & ~opened for c in _bits(remaining)}
        cost = {c: ((opened | masks[c]) & ~closed).bit_count() for c in _bits(candidates)}
        playable = {c for c, v in cost.items() if v <= k}
        children = []
        for cid in node.children:
            child = nodes.get(int(cid))
            if child is None or child.parent != node.id or child.move is None:
                raise Rejected(f"node {node.id}: child id {cid} missing or mis-parented")
            children.append(int(child.move))
        child_set = set(children)
        if len(child_set) != len(children):
            raise Rejected(f"node {node.id}: repeated child")
        for c in children:
            if c not in playable:
                raise Rejected(f"node {node.id}: child {c} is not a playable candidate")

        # 4. premises, building the covering relation
        cover: dict[int, int] = {}
        definite: int | None = None
        for step in node.steps:
            counted["steps"] += 1
            rule = step[0]
            if rule == "definite":
                q = int(step[1])
                if q not in playable:
                    raise Rejected(f"node {node.id}: definite move keeps {q}, not a playable candidate")
                own = opens[q]
                closed_by = sum(1 for other in opens.values() if other & ~own == 0)
                if closed_by < own.bit_count():
                    raise Rejected(f"node {node.id}: definite move on {q}: close {closed_by} < open "
                                   f"{own.bit_count()}")
                if definite is not None:
                    raise Rejected(f"node {node.id}: two definite moves")
                definite = q
                for r in playable:
                    if r != q:
                        cover.setdefault(r, q)
            elif rule == "subset":
                r, d = int(step[1]), int(step[2])
                if r not in playable or d not in opens or d == r:
                    raise Rejected(f"node {node.id}: subset step ({r}, {d}) names a non-candidate")
                other, own = opens[d], opens[r]
                if not (other & ~own == 0 and (other != own or d < r)):
                    raise Rejected(f"node {node.id}: subset step ({r}, {d}): o({d}) is not a "
                                   f"(tie-broken) subset of o({r})")
                if r in cover:
                    raise Rejected(f"node {node.id}: {r} discarded twice")
                cover[r] = d
            elif rule == "better":
                r, q = int(step[1]), int(step[2])
                if r not in playable or q not in playable or q == r:
                    raise Rejected(f"node {node.id}: better step ({r}, {q}) names a non-candidate")
                if not _better_premise(masks, closed, opened, k, r, q, full=full):
                    raise Rejected(f"node {node.id}: better step ({r}, {q}): close(q, S∪{{r}}) < "
                                   f"open(q, S∪{{r}}) or S++[r,q] not playable")
                if r in cover:
                    raise Rejected(f"node {node.id}: {r} discarded twice")
                cover[r] = q
            else:
                raise Rejected(f"node {node.id}: unknown rule {rule!r}")

        # 5. exhaustiveness: every playable candidate ends at a child or in Q(S)
        for c in sorted(playable):
            if c in child_set:
                continue
            here, trail = c, set()
            while True:
                if here in child_set:
                    break
                if old_move and (seen >> here) & 1:
                    break                      # Theorem 3: searched at an ancestor
                if here in trail:
                    raise Rejected(f"node {node.id}: covering cycle through {sorted(trail)}")
                trail.add(here)
                if here not in cover:
                    raise Rejected(f"node {node.id}: candidate {here} (cost {cost.get(here)}) is "
                                   f"neither explored nor covered")
                here = cover[here]

        # 6. children in order, Q inherited by the reinsertion test
        for cid in node.children:
            child = nodes[int(cid)]
            c = int(child.move)
            inherited = 0
            if old_move and seen:
                for q in _bits(seen):
                    if ((opened | masks[q] | masks[c]) & ~(closed | (1 << q))).bit_count() <= k:
                        inherited |= 1 << q
            visit(child, closed | (1 << c), opened | masks[c], inherited)
            seen |= 1 << c
        completed.add(node.id)
        if memo_allowed:
            refuted_states[closed] = node.id

    visit(cert.nodes[0], 0, 0, 0)
    if counted["nodes"] != len(cert.nodes):
        raise Rejected(f"{len(cert.nodes) - counted['nodes']} nodes are not reachable from the root")


# ----------------------------------------------------------------------------
# the study: the corpus at n ≤ 20 (and beyond) against DRAT and the lattice
# ----------------------------------------------------------------------------


def config_kwargs(instance: MOSPInstance, config: str) -> dict:
    """The emitter's keyword arguments under a named configuration.

    `default`: the Python reference (subset rule, Theorem 1, Theorem 3, no memo).
    `csearch`: the same with Theorem 2 where `sparse_enough_for_better_move`
    says so, every candidate a dominator -- the configuration that certified
    the corpus. `memo`: the subset rule, Theorem 1 and the memo, no Theorem 3 --
    the one configuration whose memo references the checker accepts.
    """
    if config == "default":
        return {}
    if config == "csearch":
        from satisfiability.customer_search import sparse_enough_for_better_move

        return {"better_move": sparse_enough_for_better_move(instance),
                "better_move_dominators": 0}
    if config == "memo":
        return {"old_move": False, "memo": True}
    raise ValueError(f"unknown configuration {config!r}; one of {CONFIGS}")


def certify_refutation(instance: MOSPInstance, optimum: int, config: str,
                       deadline_seconds: float | None = None) -> dict:
    """Emit at `optimum − 1`, check, and describe the certificate in one row."""
    kwargs = config_kwargs(instance, config)
    deadline = None if deadline_seconds is None else time.monotonic() + deadline_seconds
    cert = emit(instance, optimum - 1, deadline=deadline, **kwargs)
    row = {"config": config, "k": optimum - 1, "status": cert.status, "branches": cert.branches,
           "better_move": bool(kwargs.get("better_move", False)),
           "emit_seconds": round(cert.emit_seconds, 5)}
    row.update({f"steps_{rule}": v for rule, v in cert.step_counts().items()})
    row.update(cert.sizes())
    if cert.status == "unsat":
        result = check(instance, Certificate.loads(cert.dumps()))
        row.update(check_ok=result.ok, check_reason=result.reason,
                   check_seconds=round(result.seconds, 5))
    else:
        row.update(check_ok=None, check_reason="", check_seconds=None)
    return row


def _job(args) -> list[dict]:
    matrix, name, source_file, collection, optimum, configs, deadline = args
    instance = MOSPInstance(matrix=np.array(matrix, dtype=np.int8), n_customers=len(matrix),
                            n_patterns=len(matrix[0]), name=name)
    base = {"instance_name": name, "source_file": source_file, "collection": collection,
            "n": instance.n_customers, "m": instance.n_patterns, "optimum": int(optimum)}
    oracle = None
    try:
        from learning.differential import oracle_minima
        minima = oracle_minima(instance)
        if minima is not None:
            oracle = int(minima["oracle_search"])
    except Exception:          # the oracle is a cross-check, never a blocker
        oracle = None
    rows = []
    for config in configs:
        row = dict(base)
        row.update(certify_refutation(instance, int(optimum), config, deadline))
        row["oracle_search"] = oracle
        rows.append(row)
    return rows


def targets(min_customers: int, max_customers: int, instance_dir: Path = DEFAULT_INSTANCE_DIR,
            solutions_dir: Path = DEFAULT_SOLUTIONS_DIR, limit: int | None = None) -> list[tuple]:
    from learning.node_counts import certified_targets

    jobs = [job for job in certified_targets(instance_dir, solutions_dir, max_customers, None)
            if len(job[0]) >= min_customers]
    return jobs[:limit] if limit is not None else jobs


def run(jobs: list[tuple], configs: tuple[str, ...], workers: int, deadline: float | None,
        table: Path = DEFAULT_CSV) -> pd.DataFrame:
    table.parent.mkdir(parents=True, exist_ok=True)
    done: set[tuple[str, str, str]] = set()
    if table.exists():
        old = pd.read_csv(table)
        done = set(zip(old.instance_name, old.source_file, old.config))
    todo = [(m, name, src, coll, opt, tuple(c for c in configs if (name, src, c) not in done), deadline)
            for m, name, src, coll, opt, _ in jobs]
    todo = [job for job in todo if job[5]]
    print(f"{len(todo)} instances to certify under {configs} on {workers} workers", flush=True)
    header = not table.exists()
    started = time.monotonic()
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        with table.open("a") as handle:
            for i, rows in enumerate(pool.imap_unordered(_job, todo, chunksize=1), 1):
                frame = pd.DataFrame(rows)
                frame.to_csv(handle, header=header, index=False)
                header = False
                if i % 500 == 0:
                    print(f"  {i}/{len(todo)} in {time.monotonic() - started:.0f} s", flush=True)
    return pd.read_csv(table)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _band(n: int) -> str:
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return f"{lo}–{hi}" if hi < 200 else f"{lo}+"
    return "?"


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def join_verdicts(frame: pd.DataFrame, proofs_csv: Path = PROOFS_CSV) -> pd.DataFrame:
    """Beside each row, §17's DRAT verdict and the lattice oracle's agreement."""
    out = frame.copy()
    if proofs_csv.exists():
        proofs = pd.read_csv(proofs_csv)[["instance_name", "source_file", "verdict", "status"]]
        proofs = proofs.rename(columns={"verdict": "drat_verdict", "status": "drat_status"})
        out = out.merge(proofs, on=["instance_name", "source_file"], how="left")
    else:
        out["drat_verdict"] = None
        out["drat_status"] = None
    out["oracle_agrees"] = out.oracle_search.notna() & (out.oracle_search == out.optimum)
    out["oracle_disagrees"] = out.oracle_search.notna() & (out.oracle_search != out.optimum)
    return out


def summarise(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    frame = join_verdicts(frame)
    frame["band"] = frame.n.map(_band)
    frame["band_lo"] = frame.n.map(lambda n: next(lo for lo, hi in SIZE_BANDS if lo <= n <= hi))
    tables: dict[str, pd.DataFrame] = {}

    # verdicts per configuration
    rows = []
    for config, part in frame.groupby("config"):
        unsat = part[part.status == "unsat"]
        drat = part[part.drat_verdict == "verified"]
        oracle = part[part.oracle_search.notna()]
        rows.append({"config": config, "instances": len(part),
                     "refuted (unsat)": len(unsat), "unknown (deadline)": int((part.status == "unknown").sum()),
                     "sat below optimum": int((part.status == "sat").sum()),
                     "certificates verified": int(unsat.check_ok.fillna(False).astype(bool).sum()),
                     "certificates rejected": int((~unsat.check_ok.fillna(True).astype(bool)).sum()),
                     "DRAT verified (§17)": len(drat),
                     "both certificate and DRAT": int(((unsat.check_ok == True) & (unsat.drat_verdict == "verified")).sum()),
                     "certificate where DRAT censored": int(((unsat.check_ok == True) & (unsat.drat_verdict != "verified")).sum()),
                     "lattice oracle available": len(oracle),
                     "oracle agrees": int(oracle.oracle_agrees.sum()),
                     "oracle disagrees": int(oracle.oracle_disagrees.sum())})
    tables["verdicts"] = pd.DataFrame(rows)

    # size and time by band, per config
    rows = []
    for (config, lo, band), part in frame.groupby(["config", "band_lo", "band"]):
        unsat = part[(part.status == "unsat")]
        if unsat.empty:
            continue
        rows.append({"config": config, "band": band, "instances": len(unsat),
                     "nodes median": unsat.nodes.median(), "nodes p90": unsat.nodes.quantile(0.9),
                     "nodes max": unsat.nodes.max(),
                     "steps median": unsat.steps.median(), "steps max": unsat.steps.max(),
                     "bytes median": unsat.bytes.median(), "bytes max": unsat.bytes.max(),
                     "gz bytes median": unsat.gz_bytes.median(), "gz bytes max": unsat.gz_bytes.max(),
                     "emit ms median": 1000 * unsat.emit_seconds.median(),
                     "check ms median": 1000 * unsat.check_seconds.median(),
                     "check ms p90": 1000 * unsat.check_seconds.quantile(0.9),
                     "check ms max": 1000 * unsat.check_seconds.max(),
                     "bytes / branch": (unsat.bytes.sum() / max(1, unsat.branches.sum()))})
    tables["by_band"] = pd.DataFrame(rows).sort_values(["config", "band"], key=lambda s: s if s.name == "config" else s.map(lambda b: int(str(b).split("–")[0].rstrip("+"))))

    # steps by rule per config
    rows = []
    for config, part in frame.groupby("config"):
        unsat = part[part.status == "unsat"]
        total_steps = max(1, unsat.steps.sum())
        row = {"config": config, "refutations": len(unsat), "branches": int(unsat.branches.sum()),
               "nodes": int(unsat.nodes.sum()), "steps": int(unsat.steps.sum())}
        for rule in ("definite", "subset", "better", "memo", "free"):
            col = f"steps_{rule}"
            row[rule] = int(unsat[col].sum()) if col in unsat else 0
        row["zero-step refutations"] = int((unsat.steps == 0).sum())
        row["zero-branch refutations"] = int((unsat.branches == 0).sum())
        row["steps / branch"] = unsat.steps.sum() / max(1, unsat.branches.sum())
        rows.append(row)
    tables["rules"] = pd.DataFrame(rows)

    # check time against size: seconds per node, per step
    rows = []
    for config, part in frame.groupby("config"):
        unsat = part[(part.status == "unsat") & part.check_seconds.notna()]
        if unsat.empty:
            continue
        rows.append({"config": config, "refutations": len(unsat),
                     "check s total": unsat.check_seconds.sum(),
                     "emit s total": unsat.emit_seconds.sum(),
                     "check / emit": unsat.check_seconds.sum() / max(1e-9, unsat.emit_seconds.sum()),
                     "µs per node": 1e6 * unsat.check_seconds.sum() / max(1, unsat.nodes.sum()),
                     "µs per step": 1e6 * unsat.check_seconds.sum() / max(1, unsat.steps.sum()),
                     "bytes total": int(unsat.bytes.sum()), "gz bytes total": int(unsat.gz_bytes.sum())})
    tables["cost"] = pd.DataFrame(rows)

    # against the DRAT proofs of §17: the same instances, size and check time
    rows = []
    proofs = pd.read_csv(PROOFS_CSV) if PROOFS_CSV.exists() else None
    if proofs is not None:
        cs = frame[(frame.config == "csearch") & (frame.status == "unsat") & (frame.check_ok == True)]
        both = cs.merge(proofs[proofs.verdict == "verified"][
            ["instance_name", "source_file", "proof_gz_bytes", "proof_bytes", "proof_lemmas",
             "check_seconds", "solve_seconds", "conflicts"]].rename(
                columns={"check_seconds": "drat_check_seconds", "solve_seconds": "drat_solve_seconds"}),
            on=["instance_name", "source_file"], how="inner")
        for (lo, band), part in both.groupby(["band_lo", "band"]):
            rows.append({"band": band, "instances (both proofs)": len(part),
                         "certificate gz bytes median": part.gz_bytes.median(),
                         "DRAT gz bytes median": part.proof_gz_bytes.median(),
                         "gz ratio DRAT / certificate (median of ratios)": (part.proof_gz_bytes / part.gz_bytes).median(),
                         "certificate check ms median": 1000 * part.check_seconds.median(),
                         "DRAT check ms median": 1000 * part.drat_check_seconds.median(),
                         "check ratio DRAT / certificate (median)": (part.drat_check_seconds / part.check_seconds.clip(lower=1e-6)).median(),
                         "certificate gz total MB": part.gz_bytes.sum() / 1e6,
                         "DRAT gz total MB": part.proof_gz_bytes.sum() / 1e6,
                         "certificate check s total": part.check_seconds.sum(),
                         "DRAT check s total": part.drat_check_seconds.sum(),
                         "emit s total": part.emit_seconds.sum(),
                         "DRAT solve s total": part.drat_solve_seconds.sum()})
    tables["against_drat"] = pd.DataFrame(rows)

    # rejected or disagreeing rows, if any
    bad = frame[((frame.status == "unsat") & (frame.check_ok == False))
                | (frame.status == "sat") | frame.oracle_disagrees]
    tables["flagged"] = bad[["instance_name", "config", "n", "m", "optimum", "status", "check_ok",
                             "check_reason", "oracle_search", "drat_verdict"]].head(50)
    return tables


def write_tables(frame: pd.DataFrame, out: Path = DEFAULT_OUT) -> None:
    tables = summarise(frame)
    parts = ["# Search certificates: tables (loop0004 item 05)", "",
             f"*Generated by `python -m learning.search_certificate --stage tables` from "
             f"`{DEFAULT_CSV}`: {len(frame)} rows, {frame.instance_name.nunique()} instances at "
             f"{frame.n.min()}–{frame.n.max()} customers.*", ""]
    titles = {"verdicts": "Verdicts per configuration, against §17's DRAT proofs and the lattice oracle (n_active ≤ 15)",
              "by_band": "Certificate size and check time by size band (refutations only)",
              "rules": "Steps by rule",
              "cost": "Check cost against emit cost and size",
              "against_drat": "Against §17's DRAT proofs on the instances that have both (csearch configuration)",
              "flagged": "Rejected certificates, satisfiable calls below the optimum, oracle disagreements"}
    for key, title in titles.items():
        parts += [f"## {title}", "", _md(tables[key]) if not tables[key].empty else "*(none)*", ""]
    out.write_text("\n".join(parts))
    print(f"wrote {out}")


# ----------------------------------------------------------------------------
# entry point
# ----------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", choices=("run", "tables", "one"), default="tables")
    parser.add_argument("--configs", default=",".join(CONFIGS))
    parser.add_argument("--min-customers", type=int, default=0)
    parser.add_argument("--max-customers", type=int, default=20)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--deadline", type=float, default=None, help="seconds per emit call")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--table", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--instance", type=str, default=None)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--save", type=Path, default=None, help="write the certificate (gzip JSON)")
    args = parser.parse_args()
    configs = tuple(c for c in args.configs.split(",") if c)

    if args.stage == "run":
        jobs = targets(args.min_customers, args.max_customers, limit=args.limit)
        frame = run(jobs, configs, args.workers, args.deadline, args.table)
        write_tables(frame, args.out)
    elif args.stage == "tables":
        write_tables(pd.read_csv(args.table), args.out)
    else:
        from learning.dataset import enumerate_instances

        found = None
        for _, inst in enumerate_instances(Path(DEFAULT_INSTANCE_DIR)):
            if inst.name == args.instance:
                found = inst
                break
        if found is None:
            raise SystemExit(f"no instance named {args.instance!r}")
        for config in configs:
            cert = emit(found, args.k, **config_kwargs(found, config))
            result = check(found, cert) if cert.status == "unsat" else None
            print(config, cert.status, "branches", cert.branches, cert.sizes(), cert.step_counts(),
                  result)
            if args.save is not None:
                args.save.write_bytes(gzip.compress(cert.dumps()))


if __name__ == "__main__":
    main()
