"""The root split: one refutation spread over many cores (loop0007 item 10).

Item 07 left seven 125 x 125 refutations of `value - 1` censored after 10.1 h
on one core each (`paper2/data/solver_fix_recheck_long.csv`). The search keeps
no state across calls, so a longer single-core run starts again from zero. This
module splits the tree instead.

**What it runs.** The driver opens the top of the tree itself with
`native.split_expand`, which is `search` in `customer_search.c` up to its loop:
the free moves, the candidate set, the repaired dominance filter, and for each
child in loop order the old moves it inherits from the siblings before it.
Every child is a *task*: `native.split_decide` runs the unchanged `search` from
the child's state, with those inherited old moves and an empty memo. A task
that exceeds its node cap is expanded in turn and its children become tasks
(its nodes are counted as waste): breadth first into at least as many
pieces as there are workers, the cap doubling with depth to four times the
base. The configuration is item 07's `csearch` one
(repaired rules, Theorem 2 by `sparse_enough_for_better_move`, every earlier
survivor a dominator, memo and old move on).

**Why an all-unsat split is a refutation.** The driver's tree is the sequential
search's tree: same nodes, same filter, same children in the same order, same
inherited old moves. What differs is the memo, which the tasks do not share.
`lean/MOSPFormalization/Search/Split.lean` models exactly this run (`ExecSplit`:
`Exec` with a `task` leaf that runs from an empty memo and leaves the driver's
memo unchanged), proves that every such run lifts to an `Exec` run
(`ExecSplit.exec`), and draws `execSplit_repairedFullFilter_mospValue`: a split
run of the repaired filter answering `false` means `k < mospValue`. The old
moves a task inherits are refuted by its earlier siblings, which is why *all*
tasks must answer unsat before anything is claimed; the code never claims less.

**Counting.** Nodes are counted as the sequential search counts them: each
child of an expanded node is one node (the `s->nodes++` at the parent's loop),
plus every task's own count. With the memo off the split total equals the
sequential count exactly (`tests/test_solver_fix_split.py`); with the memo on
it is larger, because memo hits across tasks are lost. Waste (the nodes of
tasks that hit their cap and were split) is reported beside it.

**Resumable.** Every expansion and every task result is appended to
`paper2/data/solver_fix_split_tasks.csv` as it happens. The tree is rebuilt
from those rows on restart: an expanded key is re-expanded (deterministic, ms),
a finished key is done, everything else is pending. A run stopped by `--until`
loses only the work of the tasks in flight.

    python -m paper2.solver_fix_split --workers 24 --until 2026-10-02T23:30
    python -m paper2.solver_fix_split --summary
    python -m paper2.solver_fix_split --tables

Nothing here writes to `solutions/`.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import heapq
import multiprocessing as mp
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "paper2" / "data"
TASKS = DATA / "solver_fix_split_tasks.csv"
RESULTS = DATA / "solver_fix_split_results.csv"
LONG = DATA / "solver_fix_recheck_long.csv"

TASK_FIELDS = ["instance_name", "k", "key", "kind", "status", "nodes", "seconds",
               "children", "cap", "witness", "started", "finished"]
RESULT_FIELDS = ["instance_name", "n", "m", "value", "k", "status", "tasks", "expanded",
                 "edges", "task_nodes", "total_nodes", "waste_nodes", "core_seconds",
                 "wall_started", "wall_finished", "item07_censored_nodes"]


# ----------------------------------------------------------------------------
# the tree
# ----------------------------------------------------------------------------

def csearch_flags(instance) -> dict:
    """Item 07's `csearch` configuration, named in full."""
    from satisfiability.customer_search import sparse_enough_for_better_move
    return dict(subset_rule=True, definite_move=True, restrict=False,
                better_move=bool(sparse_enough_for_better_move(instance)),
                better_move_dominators=0, old_move=True, fan_order="index",
                repaired_rules=True)


class Node:
    """A state of the search, reached from the root by the branch choices `key`."""

    __slots__ = ("key", "closed", "opened", "seen", "prefix")

    def __init__(self, key, closed, opened, seen, prefix):
        self.key, self.closed, self.opened, self.seen, self.prefix = \
            key, closed, opened, seen, prefix

    @property
    def name(self) -> str:
        return ".".join(map(str, self.key))


def root() -> Node:
    return Node((), 0, 0, 0, [])


def expand(instance, k, node: Node, flags: dict, masks: list[int]):
    """The children of `node` in the sequential loop order, or the solution
    if the free moves at `node` close everything."""
    from satisfiability.native import split_expand
    after, free, kids = split_expand(instance, k, node.closed, node.opened, node.seen,
                                     **flags)
    if kids is None:
        return node.prefix + free, None
    children = [Node(node.key + (c,), after | (1 << c), node.opened | masks[c], inherited,
                     node.prefix + free + [c])
                for c, inherited in kids]
    return None, children


def run_task(instance, k, node: Node, flags: dict, *, memo: bool = True,
             max_nodes: int | None = None, seconds: float | None = None):
    from satisfiability.native import split_decide
    return split_decide(instance, k, node.closed, node.opened, node.seen, node.prefix,
                        memo=memo, max_nodes=max_nodes, seconds=seconds, **flags)


def split_refute(instance, k, *, flags: dict | None = None, target: int = 8,
                 cap: int | None = None, memo: bool = True) -> dict:
    """In-process split, for tests and small instances: expand breadth first to
    at least `target` tasks, run each (capped tasks are split further), and
    return the answer with the counts. `status` is "sat" with a witness,
    "unsat", or "unknown" never (caps split, they do not censor)."""
    from satisfiability.heuristics import _neighbour_masks
    flags = flags or csearch_flags(instance)
    masks = _neighbour_masks(instance)
    pending = [root()]
    edges = expanded = task_nodes = waste = tasks = 0
    # Breadth-first expansion to the target.
    while pending and len(pending) < target:
        node = pending.pop(0)
        witness, children = expand(instance, k, node, flags, masks)
        if children is None:
            return dict(status="sat", witness=witness, nodes=edges)
        expanded += 1
        edges += len(children)
        pending.extend(children)
    while pending:
        node = pending.pop(0)
        answer = run_task(instance, k, node, flags, memo=memo, max_nodes=cap)
        tasks += 1
        if answer.status == "sat":
            return dict(status="sat", witness=answer.order, nodes=edges + task_nodes)
        if answer.status == "unsat":
            task_nodes += answer.nodes
            continue
        waste += answer.nodes
        witness, children = expand(instance, k, node, flags, masks)
        if children is None:
            return dict(status="sat", witness=witness, nodes=edges + task_nodes)
        expanded += 1
        edges += len(children)
        pending[:0] = children
    return dict(status="unsat", witness=None, nodes=edges + task_nodes, edges=edges,
                task_nodes=task_nodes, waste=waste, tasks=tasks, expanded=expanded)


def cost_of(instance, order: list[int]) -> int:
    """Peak open stacks of a closing order (all active customers), simulated
    from the instance alone."""
    from satisfiability.heuristics import _neighbour_masks
    masks = _neighbour_masks(instance)
    opened = closed = 0
    peak = 0
    for c in order:
        opened |= masks[c]
        peak = max(peak, (opened & ~closed).bit_count())
        closed |= 1 << c
    active = sum(1 << c for c in range(instance.n_customers) if masks[c])
    if closed & active != active:
        raise ValueError("the order does not close every active customer")
    return peak


# ----------------------------------------------------------------------------
# the parallel driver
# ----------------------------------------------------------------------------

_WORKER: dict = {}


def _worker_init(matrices: dict) -> None:
    _WORKER["matrices"] = matrices
    _WORKER["instances"] = {}


def _worker_task(args):
    name, k, key, closed, opened, seen, prefix, flags, cap, seconds = args
    from paper2.solver_fix_recheck import _instance
    inst = _WORKER["instances"].get(name)
    if inst is None:
        inst = _WORKER["instances"][name] = _instance(name, _WORKER["matrices"][name])
    started = dt.datetime.now().isoformat(timespec="seconds")
    t0 = time.monotonic()
    answer = run_task(inst, k, Node(key, closed, opened, seen, prefix), flags,
                      max_nodes=cap, seconds=seconds)
    return dict(instance_name=name, key=key, status=answer.status, nodes=answer.nodes,
                seconds=round(time.monotonic() - t0, 3), witness=answer.order,
                started=started, finished=dt.datetime.now().isoformat(timespec="seconds"))


def _append(path: Path, fields: list[str], row: dict) -> None:
    new = not path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if new:
            writer.writeheader()
        writer.writerow({f: row.get(f, "") for f in fields})
        handle.flush()


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as handle:
        return list(csv.DictReader(handle))


def targets() -> list[dict]:
    """Item 07's censored seven, cheapest first by its price."""
    rows = _read_rows(LONG)
    rows.sort(key=lambda r: float(r["price (nodes)"]))
    return [dict(instance_name=r["instance"], value=int(r["value"]), k=int(r["k"]),
                 lower=float(r["lower bound (nodes)"])) for r in rows]


class Tree:
    """One instance's split, rebuilt from the task rows."""

    def __init__(self, rank, name, instance, k, masks, rows):
        self.rank, self.name, self.instance, self.k, self.masks = rank, name, instance, k, masks
        self.flags = csearch_flags(instance)
        self.expanded: dict[tuple, int] = {}
        self.done: dict[tuple, int] = {}
        self.waste = 0
        self.core_seconds = 0.0
        self.sat = None
        for row in rows:
            key = tuple(int(x) for x in row["key"].split(".")) if row["key"] else ()
            self.core_seconds += float(row["seconds"] or 0)
            if row["kind"] == "expand":
                self.expanded[key] = int(row["children"])
                self.waste += int(row["nodes"] or 0)
            elif row["kind"] == "task" and row["status"] == "unsat":
                self.done[key] = int(row["nodes"])
            elif row["kind"] == "task" and row["status"] == "sat":
                self.sat = row
            elif row["kind"] == "task" and row["status"] == "split":
                self.waste += int(row["nodes"] or 0)
            elif row["kind"] == "stopped":
                self.waste += int(row["nodes"] or 0)
        self.in_flight: set[tuple] = set()

    def pending(self, target: int) -> list[Node]:
        """Every node still to run, expanding as recorded (and, on a fresh
        tree, breadth first to `target`)."""
        if not self.expanded and not self.done:
            frontier = [root()]
            while frontier and len(frontier) < target:
                node = frontier.pop(0)
                self.record_expand(node, nodes=0, seconds=0.0)
                frontier.extend(self.children(node))
        out, stack = [], [root()]
        while stack:
            node = stack.pop()
            if node.key in self.expanded:
                stack.extend(reversed(self.children(node)))
            elif node.key not in self.done:
                out.append(node)
        return out

    def children(self, node: Node) -> list[Node]:
        witness, kids = expand(self.instance, self.k, node, self.flags, self.masks)
        if kids is None:
            raise RuntimeError(f"{self.name}: free moves close everything at "
                               f"{node.name}; the root would be sat: {witness}")
        if node.key in self.expanded and self.expanded[node.key] != len(kids):
            raise RuntimeError(f"{self.name}: {node.name} re-expanded to {len(kids)} "
                               f"children, recorded {self.expanded[node.key]}")
        return kids

    def record_expand(self, node: Node, nodes: int, seconds: float) -> list[Node]:
        kids = self.children(node)
        self.expanded[node.key] = len(kids)
        self.waste += nodes
        now = dt.datetime.now().isoformat(timespec="seconds")
        _append(TASKS, TASK_FIELDS, dict(instance_name=self.name, k=self.k, key=node.name,
                                         kind="expand", nodes=nodes, seconds=seconds,
                                         children=len(kids), finished=now))
        return kids

    def edges(self) -> int:
        return sum(self.expanded.values())

    def finished(self) -> bool:
        return not self.in_flight and not self.pending(0)


def drive(workers: int, until: dt.datetime | None, target: int, cap: int,
          only: list[str] | None) -> None:
    from paper2.solver_fix_recheck import _instance, load_instances
    from satisfiability.heuristics import _neighbour_masks

    chosen = [t for t in targets() if not only or t["instance_name"] in only]
    if only:
        # `--only` also gives the priority order.
        chosen.sort(key=lambda t: only.index(t["instance_name"]))
    matrices = load_instances({t["instance_name"] for t in chosen})
    rows = _read_rows(TASKS)
    results = {r["instance_name"] for r in _read_rows(RESULTS)}
    trees: dict[str, Tree] = {}
    for rank, t in enumerate(chosen):
        name = t["instance_name"]
        if name in results:
            continue
        inst = _instance(name, matrices[name])
        tree = Tree(rank, name, inst, t["k"], _neighbour_masks(inst),
                    [r for r in rows if r["instance_name"] == name and int(r["k"]) == t["k"]])
        tree.value, tree.lower, tree.started = t["value"], t["lower"], dt.datetime.now()
        if tree.sat is not None:
            print(f"!!! {name}: a recorded task is SAT at k = {tree.k}; stop and report",
                  flush=True)
            return
        trees[name] = tree

    heap: list = []
    seq = 0
    for tree in trees.values():
        for node in tree.pending(target):
            heapq.heappush(heap, (tree.rank, seq, tree.name, node))
            seq += 1
    print(f"{len(trees)} instances, {len(heap)} tasks pending", flush=True)

    ctx = mp.get_context("fork")
    with cf.ProcessPoolExecutor(workers, mp_context=ctx, initializer=_worker_init,
                                initargs=(matrices,)) as pool:
        flying: dict = {}

        def cap_at(node: Node) -> int:
            # Doubling with depth, to four times the base: the waste along a
            # chain of splits is then geometric, not linear, in its length.
            return cap * min(4, 2 ** max(0, len(node.key) - 1))

        def submit():
            nonlocal seq
            while heap and len(flying) < workers:
                left = None
                if until is not None:
                    left = (until - dt.datetime.now()).total_seconds()
                    if left < 60:
                        return
                _, _, name, node = heapq.heappop(heap)
                tree = trees[name]
                fut = pool.submit(_worker_task, (name, tree.k, node.key, node.closed,
                                                 node.opened, node.seen, node.prefix,
                                                 tree.flags, cap_at(node), left))
                flying[fut] = (name, node)
                tree.in_flight.add(node.key)

        submit()
        while flying:
            done, _ = cf.wait(list(flying), timeout=600, return_when=cf.FIRST_COMPLETED)
            for fut in done:
                name, node = flying.pop(fut)
                tree = trees[name]
                tree.in_flight.discard(node.key)
                out = fut.result()
                tree.core_seconds += out["seconds"]
                base = dict(instance_name=name, k=tree.k, key=node.name, cap=cap_at(node),
                            status=out["status"], nodes=out["nodes"], seconds=out["seconds"],
                            started=out["started"], finished=out["finished"])
                if out["status"] == "unsat":
                    tree.done[node.key] = out["nodes"]
                    _append(TASKS, TASK_FIELDS, dict(base, kind="task"))
                elif out["status"] == "sat":
                    witness = out["witness"]
                    _append(TASKS, TASK_FIELDS, dict(base, kind="task",
                                                     witness=" ".join(map(str, witness))))
                    peak = cost_of(tree.instance, witness)
                    print(f"!!! {name}: SAT at k = {tree.k}, witness peak {peak}. "
                          f"A certified value is wrong: stop and report.", flush=True)
                    for f in flying:
                        f.cancel()
                    return
                elif out["nodes"] >= cap_at(node):
                    # Over its cap: split it breadth first into at least
                    # `workers` pieces (expanding is free), so that a heavy
                    # subtree is spread at once rather than one level per cap.
                    _append(TASKS, TASK_FIELDS, dict(base, kind="task", status="split",
                                                     cap=cap_at(node)))
                    tree.waste += out["nodes"]
                    pieces = [node]
                    while pieces and len(pieces) < workers:
                        pieces.extend(tree.record_expand(pieces.pop(0), nodes=0, seconds=0.0))
                    for child in pieces:
                        heapq.heappush(heap, (tree.rank, seq, name, child))
                        seq += 1
                else:
                    # Stopped by --until: pending again on resume.
                    _append(TASKS, TASK_FIELDS, dict(base, kind="stopped"))
                    tree.waste += out["nodes"]
                if out["status"] == "unsat" and tree.finished():
                    _finish(tree)
                print(f"{out['finished']} {name} {node.name or 'root'} {out['status']} "
                      f"{out['nodes']:.3g} nodes {out['seconds']:.0f} s; "
                      f"{len(heap)} queued", flush=True)
            submit()


def _finish(tree: Tree) -> None:
    task_nodes = sum(tree.done.values())
    edges = tree.edges()
    row = dict(instance_name=tree.name, n=tree.instance.n_customers,
               m=tree.instance.n_patterns, value=tree.value, k=tree.k, status="unsat",
               tasks=len(tree.done), expanded=len(tree.expanded), edges=edges,
               task_nodes=task_nodes, total_nodes=task_nodes + edges, waste_nodes=tree.waste,
               core_seconds=round(tree.core_seconds, 1),
               wall_started=tree.started.isoformat(timespec="seconds"),
               wall_finished=dt.datetime.now().isoformat(timespec="seconds"),
               item07_censored_nodes=f"{tree.lower:.6g}")
    _append(RESULTS, RESULT_FIELDS, row)
    print(f"=== {tree.name}: k = {tree.k} refuted, {row['total_nodes']:.4g} nodes over "
          f"{row['tasks']} tasks, {row['core_seconds'] / 3600:.1f} core-h", flush=True)


def summary() -> None:
    """Per instance: finished, or how far the split has got."""
    rows = _read_rows(TASKS)
    finished = {r["instance_name"]: r for r in _read_rows(RESULTS)}
    for t in targets():
        name = t["instance_name"]
        mine = [r for r in rows if r["instance_name"] == name]
        done = [r for r in mine if r["kind"] == "task" and r["status"] == "unsat"]
        nodes = sum(int(r["nodes"]) for r in done)
        secs = sum(float(r["seconds"] or 0) for r in mine)
        state = "REFUTED" if name in finished else ("not started" if not mine else "partial")
        print(f"{name:24s} k={t['k']:3d} {state:11s} tasks done {len(done):5d} "
              f"nodes {nodes:.3g} core-h {secs / 3600:.1f}")


def tables() -> str:
    """`paper2/data/solver_fix_split_tables.md`: one row per instance."""
    rows = _read_rows(TASKS)
    finished = {r["instance_name"]: r for r in _read_rows(RESULTS)}
    lines = ["# Item 10: the root split (tables)", "",
             "Regenerate: `python -m paper2.solver_fix_split --tables`.", "",
             "| instance | value | `k` | state | tasks done / expanded nodes | nodes (split) "
             "| waste | core-hours | item 07 censored at |",
             "|---|---:|---:|---|---:|---:|---:|---:|---:|"]
    for t in targets():
        name = t["instance_name"]
        mine = [r for r in rows if r["instance_name"] == name and int(r["k"]) == t["k"]]
        done = [r for r in mine if r["kind"] == "task" and r["status"] == "unsat"]
        expanded = [r for r in mine if r["kind"] == "expand"]
        waste = sum(int(r["nodes"] or 0) for r in mine
                    if r["kind"] == "stopped" or (r["kind"] == "task" and r["status"] == "split"))
        secs = sum(float(r["seconds"] or 0) for r in mine)
        if name in finished:
            state, nodes = "**refuted**", int(finished[name]["total_nodes"])
        else:
            state = "partial" if mine else "not started"
            nodes = sum(int(r["nodes"]) for r in done)
        lines.append(f"| `{name}` | {t['value']} | {t['k']} | {state} | {len(done):,} / "
                     f"{len(expanded):,} | {nodes:.3g} | {waste:.3g} | {secs / 3600:.1f} | "
                     f"{t['lower']:.3g} |")
    lines += ["", "For a partial instance the node count is the finished tasks' only: a lower "
              "bound on the split tree, not on the sequential one."]
    text = "\n".join(lines) + "\n"
    (DATA / "solver_fix_split_tables.md").write_text(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--until", help="ISO time: submit nothing that cannot run a minute")
    parser.add_argument("--target", type=int, default=96,
                        help="initial tasks per instance (breadth-first expansion)")
    parser.add_argument("--cap", type=float, default=3e9, help="nodes before a task is split")
    parser.add_argument("--only", nargs="*", help="these instances, in this priority order")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--tables", action="store_true")
    args = parser.parse_args()
    if args.tables:
        print(tables())
        return
    if args.summary:
        summary()
        return
    until = dt.datetime.fromisoformat(args.until) if args.until else None
    drive(args.workers, until, args.target, int(args.cap), args.only)


if __name__ == "__main__":
    main()
