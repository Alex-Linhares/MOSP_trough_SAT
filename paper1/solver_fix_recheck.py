"""Re-check the values that rested on the customer search alone (loop0007 item 07).

Item 06 (`paper1/solver_fix_provenance.py`) listed 115 certified values (113
distinct graphs, 40-125 customers) whose refutation of `value - 1` came from the
customer search alone, under Chu & Stuckey's definite move as published (false
as stated) and, for 19 of them, an older `better_move`. This module re-checks
each of them three ways, cheapest first, and writes one CSV per way. Each row is
appended as it finishes, so a stopped run loses nothing, and every stage
continues where its CSV stops.

- `repaired`: refute `value - 1` with the repaired solver (`repaired_rules=True`,
  the default since item 03), in C, under the `csearch` configuration (Theorem 2
  by `sparse_enough_for_better_move`, every earlier survivor a dominator, memo
  and old move on). An `unsat` is covered by `exec_repairedFullFilter_mospValue`
  as far as the code matches the theorem (items 01-05). A call that hits its
  deadline is censored: its node count is a lower bound. `--retry-censored`
  re-runs censored rows with the new budget (a restart, not a resume: the search
  keeps no state across calls).
- `audit`: the *old* code's refutation (`repaired_rules=False`) in C, in the
  configuration that certified the value (Theorem 2 on or off as item 06 read
  it), with the audit counters of `cs_decide_rules(..., repaired_rules=2)`: at
  every expanded node, `CodeNodeRepaired` (`Search/Decide.lean`) is tested --
  the definite pick must pass the matching test (= hereditarily definite), and
  every better-move drop must have an earlier subset survivor meeting
  `IsRepairedBetter`. Zero failing nodes on an `unsat` run makes that old
  refutation sound by `codeExec_mospValue_of_repaired`.
- `cert`: the same check through the certificate (`learning/search_certificate.py`):
  emit the old Python run (`decide(native=False, repaired_rules=False)`'s search,
  old move, no memo), verify it with the independent checker, and test
  `CodeNodeRepaired` at every node of the certificate with this module's own
  matching (`node_repaired`), which shares no code with the solver. Capped in
  nodes, because the emitter is Python and keeps the tree in memory.
- `tables`: `paper1/data/solver_fix_recheck_tables.md`.

Prices, for the cheapest-first order: item 04's repaired node count where it
finished, else the larger of its censored count and the cost model's prediction
(`learning/data/ensemble/cost_model_predictions.csv`, `csearch`, pre-fix), else
the `recertify` count. Nodes are what is priced; seconds are beside them.

Nothing here writes to `solutions/`.

    python -m paper1.solver_fix_recheck --stage repaired --workers 21 --until 2026-10-02T05:40
    python -m paper1.solver_fix_recheck --stage audit --workers 3 --deadline 1800
    python -m paper1.solver_fix_recheck --stage cert --workers 3 --max-nodes 2000000
    python -m paper1.solver_fix_recheck --stage tables
    python -m paper1.solver_fix_recheck --stage price          # print the order and prices only
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import math
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "paper1" / "data"
PROVENANCE = DATA / "solver_fix_provenance.csv"
COST_CSVS = [DATA / "solver_fix_cost_cs.csv", DATA / "solver_fix_cost_cs125.csv",
             DATA / "solver_fix_cost_mosp40.csv"]
PREDICTIONS = ROOT / "learning" / "data" / "ensemble" / "cost_model_predictions.csv"
RECERTIFY = ROOT / "recertify" / "results.json"
LEDGER = ROOT / "benchmarks" / "results" / "compute_ledger.csv"
TABLES = DATA / "solver_fix_recheck_tables.md"
NODES_PER_SECOND = 1.1e6        # the C at 100-125 customers, item 04 (Table 3)

COUNTER_NAMES = (
    "filter_calls", "definite_prefilter", "definite_match_fail", "definite_fires",
    "definite_lost", "better_prefilter", "better_match_fail", "better_pruned",
    "audit_definite_fail", "audit_better_fail", "audit_nodes_fail",
)
BASE_FIELDS = ["instance_name", "n", "m", "value", "k", "config", "better_move", "setting",
               "status", "nodes", "seconds", "deadline", "max_nodes", "price_nodes",
               "price_source", "started", "finished"]
FIELDS = {
    "repaired": BASE_FIELDS + list(COUNTER_NAMES),
    "audit": BASE_FIELDS + list(COUNTER_NAMES),
    "cert": BASE_FIELDS + ["cert_nodes", "cert_steps", "gz_bytes", "emit_seconds",
                           "check_ok", "check_reason", "check_seconds",
                           "repaired_nodes_checked", "repaired_fail_nodes",
                           "repaired_fail_definite", "repaired_fail_better",
                           "repaired_seconds", "first_fail", "c_status", "c_nodes",
                           "c_audit_nodes_fail"],
}


def csv_path(stage: str) -> Path:
    return DATA / f"solver_fix_recheck_{stage}.csv"


# ----------------------------------------------------------------------------
# targets and prices
# ----------------------------------------------------------------------------


def listed() -> pd.DataFrame:
    return pd.read_csv(PROVENANCE)


def prices(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per listed instance: price in nodes and where it came from."""
    frame = listed() if frame is None else frame
    cost = pd.concat([pd.read_csv(p) for p in COST_CSVS if p.exists()], ignore_index=True)
    cost = cost[(cost.setting == "repaired") & (cost.config == "csearch")]
    by = cost.groupby("instance_name").agg(status=("status", "first"), nodes=("nodes", "max"))
    pred = pd.read_csv(PREDICTIONS)
    pred = pred[pred.config == "csearch"].groupby("instance_name")["pred"].max()
    rec = {}
    if RECERTIFY.exists():
        import json
        for entry in json.loads(RECERTIFY.read_text()):
            if entry.get("status") == "unsat" and entry.get("nodes"):
                rec[entry["name"]] = float(entry["nodes"])
    ledger = pd.read_csv(LEDGER)
    ledger = ledger[ledger.driver == "csearch"].groupby("instance")["seconds"].max()
    out = []
    for row in frame.itertuples():
        name = row.instance_name
        price, source = None, ""
        if name in by.index and by.loc[name, "status"] == "unsat":
            price, source = float(by.loc[name, "nodes"]), "item04"
        else:
            candidates = []
            if name in by.index:
                candidates.append((float(by.loc[name, "nodes"]), "item04-censored"))
            if name in pred.index:
                candidates.append((10 ** float(pred.loc[name]), "cost-model"))
            if name in rec:
                candidates.append((rec[name], "recertify"))
            if name in ledger.index:      # a whole pre-fix csearch descent, in seconds
                candidates.append((float(ledger.loc[name]) * NODES_PER_SECOND, "ledger-seconds"))
            if candidates:
                price, source = max(candidates)
        if price is None:
            price, source = 1e6, "none (n <= 40 or SP3; cheap)"
        out.append({"instance_name": name, "price_nodes": price, "price_source": source})
    return pd.DataFrame(out)


def load_instances(names: set[str]) -> dict:
    """The listed instances, from the benchmark files, checked against the list."""
    from learning.node_counts import enumerate_instances

    found = {}
    for _, instance in enumerate_instances(ROOT / "benchmarks" / "instances"):
        if instance.name in names and instance.name not in found:
            found[instance.name] = instance.matrix.astype(np.int8).tolist()
    missing = names - set(found)
    if missing:
        raise RuntimeError(f"listed instances not found: {sorted(missing)}")
    return found


def _instance(name: str, matrix):
    from mosp.instance import MOSPInstance

    matrix = np.array(matrix, dtype=np.int8)
    return MOSPInstance(matrix=matrix, n_customers=matrix.shape[0],
                        n_patterns=matrix.shape[1], name=name)


def done_rows(stage: str) -> dict[str, dict]:
    path = csv_path(stage)
    if not path.exists():
        return {}
    rows = {}
    with path.open() as handle:
        for row in csv.DictReader(handle):
            rows[row["instance_name"]] = row       # the last row per instance wins
    return rows


# ----------------------------------------------------------------------------
# the C stages
# ----------------------------------------------------------------------------


def _c_job(args) -> dict:
    from satisfiability.customer_search import decide, sparse_enough_for_better_move
    from satisfiability.native import decide_native, last_rule_counts

    stage, name, matrix, value, theorem2, deadline, price, source = args
    instance = _instance(name, matrix)
    k = value - 1
    if stage == "repaired":
        better = bool(sparse_enough_for_better_move(instance))
        setting, config = "repaired", "csearch"
        rules = True
    else:
        better = theorem2 == "on"
        setting, config = "old+audit", "certifying"
        rules = False                           # published rules, audit counters on
    started = time.monotonic()
    when = dt.datetime.now().isoformat(timespec="seconds")
    if stage == "repaired":
        answer = decide(instance, k, repaired_rules=rules, better_move=better,
                        better_move_dominators=0,
                        deadline=None if deadline is None else started + deadline)
    else:
        answer = decide_native(instance, k, repaired_rules=False, audit_repaired=True,
                               better_move=better, better_move_dominators=0, seconds=deadline)
        if answer is None:
            raise RuntimeError("the audit needs the C library")
    seconds = time.monotonic() - started
    counts = last_rule_counts() or {}
    row = {"instance_name": name, "n": instance.n_customers, "m": instance.n_patterns,
           "value": value, "k": k, "config": config, "better_move": better,
           "setting": setting, "status": answer.status, "nodes": int(answer.nodes),
           "seconds": round(seconds, 3), "deadline": "" if deadline is None else round(deadline),
           "max_nodes": "", "price_nodes": f"{price:.3g}", "price_source": source,
           "started": when, "finished": dt.datetime.now().isoformat(timespec="seconds")}
    row.update({c: counts.get(c, "") for c in COUNTER_NAMES})
    return row


def _append(stage: str, row: dict) -> None:
    path = csv_path(stage)
    new = not path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS[stage])
        if new:
            writer.writeheader()
        writer.writerow({f: row.get(f, "") for f in FIELDS[stage]})
        handle.flush()


def _order(stage: str, retry_censored: bool, only: list[str] | None) -> tuple[list, dict]:
    frame = listed()
    priced = frame.merge(prices(frame), on="instance_name").sort_values("price_nodes",
                                                                        kind="stable")
    if only:
        priced = priced[priced.instance_name.isin(only)]
    done = done_rows(stage)
    todo = []
    for row in priced.itertuples():
        prior = done.get(row.instance_name)
        if prior is not None and (prior["status"] in ("unsat", "sat") or not retry_censored):
            continue
        todo.append(row)
    return todo, done


def run_c(stage: str, workers: int, deadline: float | None, until: str | None,
          retry_censored: bool, only: list[str] | None) -> None:
    todo, done = _order(stage, retry_censored, only)
    if not todo:
        print(f"{stage}: nothing left ({len(done)} rows)")
        return
    matrices = load_instances({r.instance_name for r in todo})
    end = None if until is None else dt.datetime.fromisoformat(until).timestamp()

    def budget() -> float | None:
        if end is None:
            return deadline
        left = end - time.time()
        return max(1.0, left if deadline is None else min(deadline, left))

    print(f"{stage}: {len(todo)} to run on {workers} workers", flush=True)
    ctx = mp.get_context("spawn")
    # One task per instance, cheapest first, the budget fixed at submission: a
    # worker that picks up a job late gets what remains until `until`.
    with ctx.Pool(workers, maxtasksperchild=1) as pool:
        pending = []
        queue = list(todo)
        while queue or pending:
            while queue and len(pending) < workers:
                r = queue.pop(0)
                args = (stage, r.instance_name, matrices[r.instance_name], int(r.value),
                        r.theorem2, budget(), float(r.price_nodes), r.price_source)
                pending.append(pool.apply_async(_c_job, (args,)))
            time.sleep(0.5)
            still = []
            for res in pending:
                if res.ready():
                    row = res.get()
                    _append(stage, row)
                    print(f"{row['instance_name']}: {row['status']} {row['nodes']} nodes "
                          f"{row['seconds']} s audit_fail={row.get('audit_nodes_fail', '')}",
                          flush=True)
                else:
                    still.append(res)
            pending = still


# ----------------------------------------------------------------------------
# the certificate stage: CodeNodeRepaired at every node, our own matching
# ----------------------------------------------------------------------------


def _bits(mask: int):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def has_matching(sets: list[int], need: int) -> bool:
    """Whether `need` of `sets` (bitmasks) have distinct representatives (Kuhn)."""
    if need <= 0:
        return True
    if len(sets) < need:
        return False
    owner: dict[int, int] = {}

    def augment(i: int, visited: set[int]) -> bool:
        for e in _bits(sets[i]):
            if e in visited:
                continue
            visited.add(e)
            if e not in owner or augment(owner[e], visited):
                owner[e] = i
                return True
        return False

    matched = 0
    for i in range(len(sets)):
        if augment(i, set()):
            matched += 1
            if matched >= need:
                return True
    return False


def finished_by(masks: list[int], full: int, opened: int) -> int:
    """`cl` of a set whose opened stacks are `opened`: every customer with N[c] inside it."""
    out = 0
    for c in _bits(full):
        if masks[c] & ~opened == 0:
            out |= 1 << c
    return out


def hereditarily_definite(masks: list[int], full: int, S: int, opened: int, q: int) -> bool:
    """`HasDefiniteMatching G S q` (= `IsHereditarilyDefinite` by Theorem 4.8), at a
    free-closed `S` with `opened = O(S)`: the customers `d ∉ S ∪ {q}` with
    `o(d,S) ⊆ o(q,S)` have a system of distinct representatives in their `o(d,S)`
    of size at least `open(q,S) − 1`."""
    if (S >> q) & 1:
        return True                    # openCount = 0
    own = masks[q] & ~opened
    sets = []
    for d in _bits(full & ~S):
        if d == q:
            continue
        left = masks[d] & ~opened
        if left & ~own == 0:
            sets.append(left)
    return has_matching(sets, own.bit_count() - 1)


def repaired_better(masks: list[int], full: int, k: int, S: int, opened: int, r: int, q: int) -> bool:
    """`IsRepairedBetter G k S r q`: stepCost(insert r S, q) ≤ k and q hereditarily
    definite at cl(insert r S)."""
    S_r = S | (1 << r)
    opened_r = opened | masks[r]
    if ((opened_r | masks[q]) & ~S_r).bit_count() > k:
        return False
    T = S_r | finished_by(masks, full, opened_r)
    return hereditarily_definite(masks, full, T, opened_r, q)


def node_repaired(instance, cert, oracle: bool = False) -> dict:
    """Walk a verified certificate, re-deriving each node's state as the checker
    does, and test `CodeNodeRepaired` at every expanded (non-memo) node.

    With `oracle` (small graphs only: tables of size 2^n), the same check is also
    made with `paper1/search_check.py`'s `d_hereditary` (`IsHereditarilyDefinite`
    by enumerating every intermediate set) and `b_is_repaired`, and disagreements
    with this module's matching are counted in `oracle_disagree`."""
    from learning.search_certificate import neighbourhoods

    masks = neighbourhoods(instance)
    full = 0
    for c, mask in enumerate(masks):
        if mask:
            full |= 1 << c
    k = cert.k
    old_move = bool(cert.config.get("old_move", False))
    nodes = {node.id: node for node in cert.nodes}
    out = {"checked": 0, "fail_nodes": 0, "fail_definite": 0, "fail_better": 0, "first": "",
           "oracle_checked": 0, "oracle_disagree": 0}
    if oracle:
        from paper1.search_check import b_is_repaired, d_hereditary, s_tables

        O, CL = s_tables(masks)
    stack = [(cert.nodes[0], 0, 0, 0)]
    while stack:
        node, closed, opened, seen = stack.pop()
        closed |= finished_by(masks, full & ~closed, opened)
        if node.kind == "memo":
            continue
        out["checked"] += 1
        remaining = full & ~closed
        seen &= remaining
        candidates = remaining & ~seen if old_move else remaining
        open_now = (opened & ~closed).bit_count()
        playable = [c for c in _bits(candidates)
                    if open_now + (masks[c] & ~opened).bit_count() <= k]
        bad = False
        definite = [s for s in node.steps if s[0] == "definite"]
        if definite:
            q = int(definite[0][1])
            if not hereditarily_definite(masks, full, closed, opened, q):
                out["fail_definite"] += 1
                bad = True
        else:
            dropped = {int(s[1]) for s in node.steps if s[0] == "subset"}
            W = [c for c in playable if c not in dropped]
            for s in node.steps:
                if s[0] != "better":
                    continue
                r, q = int(s[1]), int(s[2])
                if repaired_better(masks, full, k, closed, opened, r, q):
                    continue
                if not any(repaired_better(masks, full, k, closed, opened, r, q2)
                           for q2 in W if q2 < r and q2 != q):
                    out["fail_better"] += 1
                    bad = True
                    break
        if oracle:
            if definite:
                bad_o = not d_hereditary(masks, O, closed, int(definite[0][1]))
            else:
                bad_o = False
                for s in node.steps:
                    if s[0] == "better" and not any(
                            b_is_repaired(masks, O, CL, closed, k, int(s[1]), q2)
                            for q2 in W if q2 < int(s[1])):
                        bad_o = True
                        break
            out["oracle_checked"] += 1
            out["oracle_disagree"] += bad_o != bad
        if bad:
            out["fail_nodes"] += 1
            if not out["first"]:
                out["first"] = f"node {node.id}"
        # children, Q inherited by the reinsertion test, in order
        cseen = seen
        kids = []
        for cid in node.children:
            child = nodes[int(cid)]
            c = int(child.move)
            inherited = 0
            if old_move and cseen:
                for q in _bits(cseen):
                    if ((opened | masks[q] | masks[c]) & ~(closed | (1 << q))).bit_count() <= k:
                        inherited |= 1 << q
            kids.append((child, closed | (1 << c), opened | masks[c], inherited))
            cseen |= 1 << c
        stack.extend(reversed(kids))
    return out


def _cert_job(args) -> dict:
    from learning.search_certificate import Certificate, check, config_kwargs, emit

    name, matrix, value, theorem2, max_nodes, deadline, price, source = args
    instance = _instance(name, matrix)
    k = value - 1
    config = "csearch" if theorem2 == "on" else "default"
    kwargs = config_kwargs(instance, config)
    if theorem2 == "on":
        kwargs["better_move"] = True          # the certifying run used Theorem 2
    when = dt.datetime.now().isoformat(timespec="seconds")
    started = time.monotonic()
    cert = emit(instance, k, max_nodes=max_nodes,
                deadline=None if deadline is None else started + deadline, **kwargs)
    row = {"instance_name": name, "n": instance.n_customers, "m": instance.n_patterns,
           "value": value, "k": k, "config": f"emitter-{config}",
           "better_move": bool(kwargs.get("better_move", False)), "setting": "old",
           "status": cert.status, "nodes": cert.branches, "seconds": round(cert.emit_seconds, 3),
           "deadline": "" if deadline is None else deadline, "max_nodes": max_nodes or "",
           "price_nodes": f"{price:.3g}", "price_source": source, "started": when,
           "emit_seconds": round(cert.emit_seconds, 3)}
    if cert.status == "unsat":
        sizes = cert.sizes()
        row.update(cert_nodes=sizes["nodes"], cert_steps=sizes["steps"],
                   gz_bytes=len(gzip.compress(cert.dumps(), 6)))
        result = check(instance, Certificate.loads(cert.dumps()))
        row.update(check_ok=result.ok, check_reason=result.reason,
                   check_seconds=round(result.seconds, 3))
        t0 = time.monotonic()
        rep = node_repaired(instance, cert)
        row.update(repaired_nodes_checked=rep["checked"], repaired_fail_nodes=rep["fail_nodes"],
                   repaired_fail_definite=rep["fail_definite"],
                   repaired_fail_better=rep["fail_better"],
                   repaired_seconds=round(time.monotonic() - t0, 3), first_fail=rep["first"])
    # The C audit on the emitter's own configuration (old move, no memo): the
    # same tree, so the failing-node counts must agree.
    from satisfiability.native import decide_native, last_rule_counts

    c = decide_native(instance, k, repaired_rules=False, audit_repaired=True, old_move=True,
                      memo=False, better_move=bool(kwargs.get("better_move", False)),
                      better_move_dominators=0, max_nodes=max_nodes)
    row.update(c_status=c.status, c_nodes=c.nodes,
               c_audit_nodes_fail=(last_rule_counts() or {}).get("audit_nodes_fail", ""))
    row["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    return row


def run_cert(workers: int, max_nodes: int, deadline: float | None, only: list[str] | None,
             retry_censored: bool) -> None:
    todo, done = _order("cert", retry_censored, only)
    if not todo:
        print(f"cert: nothing left ({len(done)} rows)")
        return
    matrices = load_instances({r.instance_name for r in todo})
    jobs = [(r.instance_name, matrices[r.instance_name], int(r.value), r.theorem2, max_nodes,
             deadline, float(r.price_nodes), r.price_source) for r in todo]
    print(f"cert: {len(jobs)} to run on {workers} workers", flush=True)
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers, maxtasksperchild=1) as pool:
        for row in pool.imap(_cert_job, jobs):
            _append("cert", row)
            print(f"{row['instance_name']}: {row['status']} {row['nodes']} nodes "
                  f"check={row.get('check_ok', '')} repaired_fail={row.get('repaired_fail_nodes', '')}",
                  flush=True)


# ----------------------------------------------------------------------------
# validation: the C audit against the certificate walk, on small graphs
# ----------------------------------------------------------------------------

VALIDATE_JSON = DATA / "solver_fix_recheck_validate.json"


def _validate_one(masks: list[int], ks, better: bool) -> dict:
    """At each k: the C published run with and without the audit (same answer,
    nodes and witness), the emitter (same branches) and `node_repaired` on its
    tree (the same failing-node count as the C audit)."""
    from learning.search_certificate import emit
    from paper1.search_check import matrix_from_masks
    from satisfiability.native import decide_native, last_rule_counts

    instance = _instance("v", matrix_from_masks(masks))
    t = {"calls": 0, "same_search": 0, "same_branches": 0, "same_fail": 0, "fail_nodes": 0,
         "fail_runs": 0, "fail_unsat_runs": 0, "mismatch": []}
    for k in ks:
        flags = dict(old_move=True, memo=False, better_move=better, better_move_dominators=0)
        plain = decide_native(instance, k, repaired_rules=False, **flags)
        audit = decide_native(instance, k, repaired_rules=False, audit_repaired=True, **flags)
        counts = last_rule_counts()
        cert = emit(instance, k, better_move=better, better_move_dominators=0)
        rep = node_repaired(instance, cert, oracle=len(masks) <= 16)
        t["oracle_checked"] = t.get("oracle_checked", 0) + rep["oracle_checked"]
        t["oracle_disagree"] = t.get("oracle_disagree", 0) + rep["oracle_disagree"]
        t["calls"] += 1
        same = (plain.status, plain.nodes, plain.order) == (audit.status, audit.nodes, audit.order)
        t["same_search"] += same
        t["same_branches"] += cert.branches == audit.nodes and cert.status == audit.status
        t["same_fail"] += rep["fail_nodes"] == counts["audit_nodes_fail"]
        t["fail_nodes"] += rep["fail_nodes"]
        t["fail_runs"] += rep["fail_nodes"] > 0
        t["fail_unsat_runs"] += rep["fail_nodes"] > 0 and audit.status == "unsat"
        if not same or rep["fail_nodes"] != counts["audit_nodes_fail"] or cert.branches != audit.nodes:
            t["mismatch"].append({"masks": masks, "k": k, "better": better,
                                  "c_fail": counts["audit_nodes_fail"], "py_fail": rep["fail_nodes"],
                                  "c_nodes": audit.nodes, "py_nodes": cert.branches})
    return t


def _validate_job(args) -> dict:
    import random

    from paper1.search_check import (BUG_A_CEX, BUG_B_CEX, DEFINITE_CEX, RUN_LOST_CEX,
                                     better_augment, random_cover, random_sparse)
    from satisfiability.native import decide_native
    from paper1.search_check import matrix_from_masks

    family, seed, count = args
    rng = random.Random(seed)
    total: dict = {}

    def add(t):
        for key, v in t.items():
            total[key] = total.get(key, [] if key == "mismatch" else 0) + v

    graphs = []
    if family == "pinned":
        graphs = [m for m, *_ in DEFINITE_CEX] + [BUG_A_CEX[0], BUG_B_CEX[0], RUN_LOST_CEX[0]]
    for _ in range(count if family != "pinned" else 0):
        if family == "gadget":
            graphs.append(better_augment(rng))
        elif family == "sparse":
            graphs.append(random_sparse(rng.randint(8, 20), rng))
        else:
            graphs.append(random_cover(rng.randint(8, 20), rng))
    for masks in graphs:
        n = len(masks)
        inst = _instance("v", matrix_from_masks(masks))
        opt = next(k for k in range(1, n + 2)
                   if decide_native(inst, k, repaired_rules=True).status == "sat")
        ks = range(1, n + 1) if family == "pinned" else sorted({max(1, opt - 1), opt, opt + 1})
        for better in (False, True):
            add(_validate_one(masks, ks, better))
    total["graphs"] = len(graphs)
    return {family: total}


def run_validate(workers: int, count: int) -> dict:
    import json

    jobs = [("pinned", 0, 0)]
    for family in ("gadget", "sparse", "cover"):
        offset = {"gadget": 1, "sparse": 2, "cover": 3}[family]
        jobs += [(family, 1000 * i + offset, count) for i in range(workers)]
    ctx = mp.get_context("spawn")
    out: dict = {}
    with ctx.Pool(workers) as pool:
        for res in pool.imap_unordered(_validate_job, jobs):
            for family, t in res.items():
                agg = out.setdefault(family, {})
                for key, v in t.items():
                    agg[key] = agg.get(key, [] if key == "mismatch" else 0) + v
    for agg in out.values():
        agg["mismatch"] = agg["mismatch"][:20]
    VALIDATE_JSON.write_text(json.dumps(out, indent=1))
    print(json.dumps({f: {k: v for k, v in a.items() if k != "mismatch"} | {"mismatches": len(a["mismatch"])}
                      for f, a in out.items()}, indent=1))
    return out


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _read(stage: str) -> pd.DataFrame:
    path = csv_path(stage)
    if not path.exists():
        return pd.DataFrame(columns=FIELDS[stage])
    frame = pd.read_csv(path)
    return frame.drop_duplicates("instance_name", keep="last")


def summary() -> pd.DataFrame:
    frame = listed()[["instance_name", "value", "n_customers", "n_patterns", "theorem2"]]
    frame = frame.merge(prices(), on="instance_name")
    rep, aud, cer = _read("repaired"), _read("audit"), _read("cert")
    frame = frame.merge(rep[["instance_name", "status", "nodes", "seconds"]].rename(
        columns={"status": "repaired_status", "nodes": "repaired_nodes",
                 "seconds": "repaired_seconds"}), on="instance_name", how="left")
    frame = frame.merge(aud[["instance_name", "status", "nodes", "seconds",
                             "audit_nodes_fail"]].rename(
        columns={"status": "audit_status", "nodes": "audit_nodes_run",
                 "seconds": "audit_seconds"}), on="instance_name", how="left")
    frame = frame.merge(cer[["instance_name", "status", "nodes", "check_ok",
                             "repaired_nodes_checked", "repaired_fail_nodes"]].rename(
        columns={"status": "cert_status", "nodes": "cert_branches",
                 "repaired_fail_nodes": "cert_fail_nodes"}), on="instance_name", how="left")

    def verdict(r) -> str:
        audit_ok = r.audit_status == "unsat" and r.audit_nodes_fail == 0
        cert_ok = (r.cert_status == "unsat" and r.check_ok in (True, "True")
                   and r.cert_fail_nodes == 0)
        if r.repaired_status == "sat" or r.audit_status == "sat" or r.cert_status == "sat":
            return "VALUE CHANGED"
        if r.repaired_status == "unsat" or audit_ok or cert_ok:
            return "re-checked"
        return "censored"

    frame["verdict"] = frame.apply(verdict, axis=1)
    return frame


def needs_long_run(frame: pd.DataFrame) -> pd.DataFrame:
    """The censored instances with their prices (one row each)."""
    import json

    rep = _read("repaired").set_index("instance_name")
    pred = pd.read_csv(PREDICTIONS)
    pred = pred[pred.config == "csearch"].groupby("instance_name")["pred"].max()
    rec = {e["name"]: float(e["nodes"]) for e in json.loads(RECERTIFY.read_text())
           if e.get("status") == "unsat" and e.get("nodes")} if RECERTIFY.exists() else {}
    rows = []
    for r in frame[frame.verdict == "censored"].itertuples():
        lower = float(rep.loc[r.instance_name, "nodes"]) if r.instance_name in rep.index else 0.0
        seconds = float(rep.loc[r.instance_name, "seconds"]) if r.instance_name in rep.index else 0.0
        model = 10 ** float(pred[r.instance_name]) if r.instance_name in pred.index else float("nan")
        recert = rec.get(r.instance_name, float("nan"))
        price = max(v for v in (lower, model, recert, float(r.price_nodes)) if v == v)
        rows.append({"instance": r.instance_name, "value": r.value, "k": r.value - 1,
                     "lower bound (nodes)": lower, "censored after (s)": seconds,
                     "cost model (nodes)": model, "recertify (nodes)": recert,
                     "order price": f"{float(r.price_nodes):.3g} ({r.price_source})",
                     "price (nodes)": price, "price (core-hours)": price / NODES_PER_SECOND / 3600})
    return pd.DataFrame(rows).sort_values("price (nodes)") if rows else pd.DataFrame()


def write_tables(out: Path = TABLES) -> None:
    frame = summary()
    frame.to_csv(DATA / "solver_fix_recheck.csv", index=False)
    lines = ["# Item 07: re-checking the 115 values (tables)", "",
             "Regenerate: `python -m paper1.solver_fix_recheck --stage tables`.", ""]
    frame["size"] = frame.n_customers.astype(str) + " × " + frame.n_patterns.astype(str)
    g = frame.groupby("size", sort=False).agg(
        listed=("instance_name", "size"),
        repaired_unsat=("repaired_status", lambda s: int((s == "unsat").sum())),
        audit_pass=("audit_nodes_fail", lambda s: int((s == 0).sum())),
        cert_pass=("cert_fail_nodes", lambda s: int((s == 0).sum())),
        rechecked=("verdict", lambda s: int((s == "re-checked").sum())),
        censored=("verdict", lambda s: int((s == "censored").sum())),
        changed=("verdict", lambda s: int((s == "VALUE CHANGED").sum())))
    lines += ["## By size", "", g.reset_index().to_markdown(index=False), ""]
    cols = ["instance_name", "value", "theorem2", "price_nodes", "price_source",
            "repaired_status", "repaired_nodes", "repaired_seconds", "audit_status",
            "audit_nodes_run", "audit_nodes_fail", "cert_status", "cert_branches",
            "cert_fail_nodes", "verdict"]
    lines += ["## Every instance, cheapest first", "",
              frame.sort_values("price_nodes")[cols].to_markdown(index=False, floatfmt=".3g"), ""]
    long = needs_long_run(frame)
    if len(long):
        lines += ["## Needs a long run", "",
                  "Censored under the repaired solver. `lower bound` is the node count the "
                  "censored call reached, a lower bound on its tree. `price` is the largest of "
                  "that, the price used for the order (item 04, a pre-fix `csearch` ledger time "
                  "or the like), the cost model's `csearch` prediction (trained on pre-2026-09-26 "
                  "counts) and the `recertify` count (first-fix code); the 2026-09-26 fix "
                  "made ridge refutations 2-20x larger, so the price is itself low. Hours "
                  f"at {NODES_PER_SECOND:.2g} nodes/s on one core.", "",
                  long.to_markdown(index=False, floatfmt=".3g"), ""]
        long.to_csv(DATA / "solver_fix_recheck_long.csv", index=False)
    out.write_text("\n".join(lines) + "\n")
    print(g.to_string())
    print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", required=True,
                        choices=("repaired", "audit", "cert", "tables", "price", "validate"))
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--deadline", type=float, default=None, help="seconds per call")
    parser.add_argument("--until", default=None, help="ISO time; no call runs past it")
    parser.add_argument("--max-nodes", type=int, default=2_000_000)
    parser.add_argument("--retry-censored", action="store_true")
    parser.add_argument("--only", nargs="*", default=None)
    parser.add_argument("--count", type=int, default=200, help="validate: graphs per worker")
    args = parser.parse_args()
    if args.stage in ("repaired", "audit"):
        run_c(args.stage, args.workers, args.deadline, args.until, args.retry_censored, args.only)
    elif args.stage == "cert":
        run_cert(args.workers, args.max_nodes, args.deadline, args.only, args.retry_censored)
    elif args.stage == "validate":
        run_validate(args.workers, args.count)
    elif args.stage == "price":
        frame = listed().merge(prices(), on="instance_name").sort_values("price_nodes")
        frame["price_hours"] = frame.price_nodes / NODES_PER_SECOND / 3600
        print(frame[["instance_name", "value", "theorem2", "price_nodes", "price_source",
                     "price_hours"]].to_string())
    else:
        write_tables()


if __name__ == "__main__":
    main()
