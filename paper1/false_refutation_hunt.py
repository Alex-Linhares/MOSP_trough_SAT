"""A hunt for a whole-instance false refutation by Chu & Stuckey's published rules.

Chu & Stuckey's definite move (Theorem 1) is false as published
(`paper1/revised_algorithm.md` Counterexample 4.5, `DEFINITE_CEX` in
`paper1/search_check.py`), and so is the better move's premise 4. Both can
discard the last solution *at a node*. What has never been seen is the
published search answering `unsat` where a solution exists, on a *whole
instance*: 600,000 random graphs, 90,000 gadgets and 17.4M searches in
loop0007 found none. This hunt is targeted rather than random, and it stops
at the first certified hit.

**The certificate** (the owner's design, 2026-10-08). Our repaired search is
the engine; no exact optimum is needed. For a graph given as closed
neighbourhood masks:

1. The repaired search descends from a greedy upper bound to its optimum k,
   the *repaired optimum*, returning a witness closing order at k. The
   witness is checked by `order_cost`, a few lines of arithmetic sharing no
   code with the search: its peak of open stacks must be <= k. That proves a
   solution of cost <= k exists, whoever found it.
2. The published search (`repaired_rules=0`) is asked at k under every
   configuration (definite / subset / better move with 4 or all dominators /
   old move / memo / fan order: 80), and at k + 1 under five. **A hit is any
   published `unsat` at a k where the witness simulates to <= k.** It is
   confirmed by the official `satisfiability.native.decide_native` (and by the
   Python reference `customer_search.decide` up to 24 customers), minimised by
   deleting vertices and edges while the certificate stays valid (the repaired
   descent and the witness check re-run after each deletion), written to
   `hits.jsonl` and `FOUND.md`, and the hunt exits.
3. If a repaired configuration answers `unsat` at k, or returns a witness that
   does not simulate to <= its k, that is a bug in the *repaired* search:
   written to `REPAIRED_BUG.jsonl`, and the hunt stops (and refuses to restart
   until the file is dealt with).

The exponential oracle (an exact subset DP, `fr_oracle`) is off the hot path:
it cross-checks the repaired optimum on a small sample of candidates with at
most 18 customers. A disagreement is a stop-and-report bug, like 3.

**Fitness**, for climbing toward a hit: the published search is replayed
(`false_refutation_hunt.c`, which includes `customer_search.c` verbatim) under
five configurations, with the repaired search as the judge of which states
have a solution, consulted only where the published search failed. It counts
falsely refuted nodes, node-level losses (a falsely refuted node where no kept
child had a solution but a discarded candidate did), memo hits on solvable
states, nodes whose only solvable moves were barred by old move, and the
fraction of the root's solvable kept branches that were falsely refuted (with
a bonus when exactly one is left standing; at all of them the answer is a
hit), plus the same fraction along the success path.

**Search**: simulated annealing with restarts, from `cexGraph` and the other
pinned graphs, the gadget family of `definite_hunt_gen.py`, the archive, and
(on resume) each worker's last frontier. Moves: relabelling (swaps, a vertex
to the front, steering the first loss state to the lowest labels, since the
published tie-breaks are by index), edge and vertex edits, twins, pendants,
splits, merges, rewiring, and bridging to a copy of part of the
counterexample. 15% of the budget is the plain baseline (random and gadget
graphs at 12-40 customers, relabelled). Candidates grow to 40 customers, each
restart under its own ceiling drawn from `SIZE_CAPS` so the sizes stay spread.

**Resuming**: `checkpoint.json` (counters, epoch, each worker's frontier) is
rewritten atomically every three minutes and at exit, `archive.jsonl` is
append-only with an hourly atomic compaction, and partial lines are skipped.
Each start is a new epoch with fresh seeds, so a restart does not replay.

    python -m paper1.false_refutation_hunt --workers 4          # until the first hit
    python -m paper1.false_refutation_hunt --workers 4 --until 2026-10-15T20:00
    python -m paper1.false_refutation_hunt --reproduce '[2201, 102, ...]'

Outputs in `paper1/data/false_refutation_hunt/`: `progress.log` (the restart
command on its first line), `checkpoint.json`, `archive.jsonl`, `hits.jsonl`,
`FOUND.md`, `hunt.pid`.
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import math
import os
import queue
import random
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
_SOURCE = HERE / "false_refutation_hunt.c"
_LIBRARY = HERE / "_false_refutation_hunt.so"
_DEPENDS = ROOT / "satisfiability" / "customer_search.c"
OUT = HERE / "data" / "false_refutation_hunt"
RESTART = ("cd /home/al/dev/MOSP && setsid nohup python -m paper1.false_refutation_hunt --workers 4"
           " >> paper1/data/false_refutation_hunt/nohup.out 2>&1 < /dev/null &")

MAX_N = 40          # candidates never exceed this
GROW_N = 36         # mutations stop adding single vertices here
MIN_N = 6
ORACLE_N = 18       # the cross-check's ceiling
ORACLE_RATE = 0.01  # the share of eligible candidates cross-checked
DECIDE_NODES = 2_000_000
WALK_NODES = 2_000_000
JUDGE_CALL = 200_000
JUDGE_TOTAL = 2_000_000
CHECKPOINT_SECONDS = 180
SIZE_CAPS = (14, 16, 18, 20, 22, 24, 28, 32, 40)   # per-restart size ceilings
W_NAMES = ("nodes", "expanded", "filter_loss", "def_loss", "seen_loss", "memo_poison",
           "false_ref", "loss_min_depth", "answer", "root_kept_solv", "root_refuted",
           "audit_fail", "judge_calls", "judge_aborts")
W_COUNT = len(W_NAMES)
SIZE_BINS = ((2, 12), (13, 16), (17, 20), (21, 24), (25, 28), (29, 32), (33, 36), (37, 40))


# ----------------------------------------------------------------------------
# configurations: (definite, subset, better, dominators, old, memo, fan)
# ----------------------------------------------------------------------------

def all_configs():
    out = []
    for definite in (1, 0):
        for subset in (1, 0):
            for better, dom in ((0, 4), (1, 4), (1, 0)):
                if not (definite or better):
                    continue                      # neither flawed rule: nothing to find
                for old in (1, 0):
                    for memo in (1, 0):
                        for fan in (0, 1):
                            out.append((definite, subset, better, dom, old, memo, fan))
    return out


CONFIGS = all_configs()
DEFAULT = (1, 1, 0, 4, 1, 1, 0)          # decide()'s defaults
CSEARCH = (1, 1, 1, 0, 1, 1, 0)          # benchmarks.csearch on sparse instances
WALKS = [DEFAULT, CSEARCH, (1, 1, 1, 4, 1, 1, 0), (1, 0, 0, 4, 1, 1, 0), (1, 1, 0, 4, 0, 0, 0)]


def config_name(c):
    d, s, b, dom, old, memo, fan = c
    rules = "+".join(r for r, on in (("definite", d), ("subset", s)) if on)
    if b:
        rules += ("+" if rules else "") + f"better/L{dom}"
    return rules + ("/old" if old else "") + ("/memo" if memo else "") + ("/degree" if fan else "")


def config_kwargs(c):
    d, s, b, dom, old, memo, fan = c
    return dict(definite_move=bool(d), subset_rule=bool(s), better_move=bool(b),
                better_move_dominators=dom, old_move=bool(old), memo=bool(memo),
                fan_order="degree" if fan else "index")


# ----------------------------------------------------------------------------
# the C helper
# ----------------------------------------------------------------------------

_lib = None


def _build():
    stale = (not _LIBRARY.exists()
             or _LIBRARY.stat().st_mtime < max(_SOURCE.stat().st_mtime, _DEPENDS.stat().st_mtime))
    if not stale:
        return
    scratch = _LIBRARY.with_name(_LIBRARY.name + f".build-{os.getpid()}")
    subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(scratch),
                    str(_SOURCE)], check=True, capture_output=True, timeout=120)
    os.replace(scratch, _LIBRARY)


def lib():
    global _lib
    if _lib is None:
        _build()
        L = ctypes.CDLL(str(_LIBRARY))
        u64p = ctypes.POINTER(ctypes.c_uint64)
        ip = ctypes.POINTER(ctypes.c_int)
        llp = ctypes.POINTER(ctypes.c_longlong)
        ll = ctypes.c_longlong
        L.fr_decide.argtypes = [ctypes.c_int, u64p, ctypes.c_int, ip, ctypes.c_int, ll, ip, llp, ip]
        L.fr_walk.argtypes = [ctypes.c_int, u64p, ctypes.c_int, ip, ll, ll, ll, llp,
                              ctypes.POINTER(ctypes.c_double), llp]
        L.fr_oracle.argtypes = [ctypes.c_int, u64p]
        L.fr_init()
        _lib = L
    return _lib


def _arr(masks):
    return (ctypes.c_uint64 * len(masks))(*masks)


def _cfg(c):
    return (ctypes.c_int * 7)(*c)


def c_decide(masks, k, cfg, repaired, max_nodes=DECIDE_NODES):
    """(status, closing order, nodes) through `cs_decide_rules`: 1 sat, 0 unsat, -1 budget."""
    if k < 0:
        return 0, [], 0
    path = (ctypes.c_int * 128)()
    nodes = ctypes.c_longlong(0)
    length = ctypes.c_int(0)
    st = lib().fr_decide(len(masks), _arr(masks), k, _cfg(cfg), int(repaired), max_nodes, path,
                         ctypes.byref(nodes), ctypes.byref(length))
    return st, [path[i] for i in range(length.value)], nodes.value


def walk(masks, k, cfg):
    out = (ctypes.c_longlong * W_COUNT)()
    score = ctypes.c_double(0)
    first = ctypes.c_longlong(0)
    lib().fr_walk(len(masks), _arr(masks), k, _cfg(cfg), WALK_NODES, JUDGE_CALL, JUDGE_TOTAL,
                  out, ctypes.byref(score), ctypes.byref(first))
    d = dict(zip(W_NAMES, out))
    d["path_score"] = score.value
    d["first_loss_state"] = first.value
    return d


def oracle(masks):
    """The exact optimum by subset DP (n <= 22): cross-checks only."""
    return lib().fr_oracle(len(masks), _arr(masks))


# ----------------------------------------------------------------------------
# graphs
# ----------------------------------------------------------------------------

def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def from_edges(n, edges):
    masks = [1 << v for v in range(n)]
    for u, v in edges:
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return masks


def edges_of(masks):
    return [(u, v) for u in range(len(masks)) for v in bits(masks[u] >> (u + 1) << (u + 1))]


def relabel(masks, perm):
    """`perm[v]` is the new label of v."""
    out = [0] * len(masks)
    for v, m in enumerate(masks):
        out[perm[v]] = sum(1 << perm[w] for w in bits(m))
    return out


def delete_vertex(masks, v):
    out = []
    for u, m in enumerate(masks):
        if u == v:
            continue
        out.append((m & ((1 << v) - 1)) | ((m >> (v + 1)) << v))
    return out


def order_cost(masks, order):
    """Peak open stacks of a closing order, from the definition: closing c with
    T closed costs |O(T + c) - T|, O the union of the closed neighbourhoods.
    None unless `order` closes every customer exactly once. Shares no code
    with the search: this is the witness check."""
    n = len(masks)
    if order is None or sorted(order) != list(range(n)):
        return None
    T = O = peak = 0
    for c in order:
        O |= masks[c]
        peak = max(peak, bin(O & ~T).count("1"))
        T |= 1 << c
    return peak


def greedy_order(masks):
    """Close the customer opening fewest new stacks, ties to the lowest index."""
    n = len(masks)
    T = O = 0
    order = []
    for _ in range(n):
        c = min((c for c in range(n) if not T >> c & 1),
                key=lambda c: (bin(masks[c] & ~O).count("1"), c))
        order.append(c)
        O |= masks[c]
        T |= 1 << c
    return order


def key(masks):
    return ",".join(map(str, masks))


def seeds():
    from paper1 import search_check as sc
    out = {"cex14": sc.DEFINITE_CEX[0][0], "cex16": sc.DEFINITE_CEX[1][0],
           "run_lost": sc.RUN_LOST_CEX[0], "bug_a": sc.BUG_A_CEX[0], "bug_b": sc.BUG_B_CEX[0],
           "subset_tie": sc.SUBSET_TIE_CEX[0]}
    return {k: list(v) for k, v in out.items()}


def gen_family(rng, n, fam):
    """`definite_hunt_gen.py`'s five families (4 is the gadget), thinned above 16."""
    E = set()
    if fam == 0:
        p = rng.uniform(0.08, 0.45) * min(1.0, 16 / n)
        E = {(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p}
    elif fam == 1:
        for v in range(1, n):
            E.add((rng.randrange(v), v))
        for _ in range(rng.randint(0, n // 2)):
            u, v = sorted(rng.sample(range(n), 2))
            E.add((u, v))
    elif fam == 2:
        deg = [0] * n
        D = rng.randint(2, 4)
        for _ in range(3 * n):
            u, v = sorted(rng.sample(range(n), 2))
            if deg[u] < D and deg[v] < D and (u, v) not in E:
                E.add((u, v))
                deg[u] += 1
                deg[v] += 1
    elif fam == 3:
        for _ in range(rng.randint(n // 2, n)):
            s = rng.sample(range(n), min(n, rng.choice([2, 2, 3, 3, 4])))
            E |= {(i, j) for i in s for j in s if i < j}
    else:
        r = rng.randint(2, 3)
        t = rng.randint(2, r)
        if n - (3 + r + t) < 2:
            n = 3 + r + t + 2
        s, q, y = 0, 1, 2
        ds = list(range(3, 3 + r))
        zs = list(range(3 + r, 3 + r + t))
        R = list(range(3 + r + t, n))
        E |= {(s, q)} | {(s, d) for d in ds} | {(min(d, y), max(d, y)) for d in ds}
        E |= {(q, y)} | {(q, z) for z in zs}
        for z in zs:
            for w in rng.sample(R, rng.randint(1, min(len(R), 6))):
                E.add((z, w))
        E.add((y, rng.choice(R)))
        p = rng.uniform(0.15, 0.5) * min(1.0, 10 / max(1, len(R)))
        E |= {(u, v) for u in R for v in R if u < v and rng.random() < p}
        for _ in range(rng.randint(0, 2)):
            E.add((s, rng.choice(R)))
    return from_edges(n, E)


def random_perm(rng, n):
    p = list(range(n))
    rng.shuffle(p)
    return p


# ----------------------------------------------------------------------------
# the certificate
# ----------------------------------------------------------------------------

def repaired_optimum(masks, dec=c_decide):
    """The repaired descent from a greedy bound. Returns (status, k, witness):
    'ok' with the repaired optimum and its closing order; 'repaired_unsat'
    with a greedy order the repaired search refuted (a repaired bug if that
    order simulates to <= k); 'aborted' when a budget ran out."""
    order = greedy_order(masks)
    k = order_cost(masks, order)
    lb = min(bin(m).count("1") for m in masks)
    st, path, _ = dec(masks, k, DEFAULT, 1)
    if st == 0:
        return "repaired_unsat", k, order
    if st != 1:
        return "aborted", k, None
    wit = path
    while k - 1 >= lb:
        st, path, _ = dec(masks, k - 1, DEFAULT, 1)
        if st == 1:
            k, wit = k - 1, path
        elif st == 0:
            break
        else:
            return "aborted", k, None
    return "ok", k, wit


def certify(masks, dec=c_decide):
    """The whole certificate for one graph.

    status 'ok': k is the repaired optimum and `witness` simulates to `peak` <= k;
    `hits` lists (configuration, k') where the published search said unsat at
    k' in {k, k + 1}: each is a certified false refutation. `repaired_bad`
    lists repaired configurations that said unsat at k, each a certified bug.
    status 'witness_invalid': the repaired search's witness does not simulate
    to <= k, so nothing is certified, and that itself is a repaired bug.
    """
    status, k, wit = repaired_optimum(masks, dec)
    peak = order_cost(masks, wit)
    res = {"status": status, "k": k, "witness": wit, "peak": peak, "hits": [],
           "repaired_bad": [], "aborted": 0}
    if status == "aborted":
        return res
    if peak is None or peak > k:
        res["status"] = "witness_invalid"
        return res
    if status == "repaired_unsat":
        res["repaired_bad"].append((DEFAULT, k))
        return res
    for c in CONFIGS:
        st = dec(masks, k, c, 0)[0]
        if st == 0:
            res["hits"].append((c, k))
        elif st < 0:
            res["aborted"] += 1
        st = dec(masks, k, c, 1)[0]
        if st == 0:
            res["repaired_bad"].append((c, k))
        elif st < 0:
            res["aborted"] += 1
    for c in WALKS:
        if dec(masks, k + 1, c, 0)[0] == 0:
            res["hits"].append((c, k + 1))
    return res


def any_hit(masks):
    """The certificate if it holds (some published unsat at a k the witness
    covers), else None. Minimisation keeps exactly this valid."""
    if len(masks) < 2:
        return None
    res = certify(masks)
    return res if res["status"] == "ok" and res["hits"] else None


def fitness(walks, res, n):
    fit = 0.0
    for w in walks:
        root = w["root_refuted"] / w["root_kept_solv"] if w["root_kept_solv"] else 0.0
        # one solvable root branch left standing is one step from a hit
        last = 3.0 if w["root_kept_solv"] >= 2 and w["root_kept_solv"] - w["root_refuted"] == 1 else 0.0
        # the counts are capped: a big lossy tree that leaves the root intact is not progress
        g = (10 * root + last + 3 * w["path_score"] + min(5.0, math.log2(1 + w["filter_loss"]))
             + min(5.0, math.log2(1 + w["false_ref"]))
             + 0.5 * min(5.0, math.log2(1 + w["memo_poison"] + w["seen_loss"]))
             + 0.3 * min(5.0, math.log2(1 + w["audit_fail"]))
             + (1.0 if w["filter_loss"] else 0.0)
             + (0.5 / (1 + w["loss_min_depth"]) if w["loss_min_depth"] < 99 else 0.0))
        if w["answer"] == 0:
            g += 100
        fit = max(fit, g)
    if res["hits"]:
        fit += 100
    return fit - 0.01 * n


def evaluate(masks, dec=c_decide):
    """The certificate, the walks and the fitness of one candidate."""
    n = len(masks)
    res = certify(masks, dec)
    ev = {"masks": list(masks), "n": n, "k": res["k"], "status": res["status"],
          "witness": res["witness"], "peak": res["peak"], "hits": res["hits"],
          "repaired_bad": res["repaired_bad"], "aborted": res["aborted"],
          "fitness": -1.0, "lossy": 0, "first_loss": -1}
    if res["status"] != "ok":
        return ev
    tot = dict(filter_loss=0, def_loss=0, false_ref=0, memo_poison=0, seen_loss=0, audit_fail=0,
               judge_aborts=0)
    walks = []
    for c in WALKS:
        w = walk(masks, res["k"], c)
        walks.append(w)
        for k_ in tot:
            tot[k_] += w[k_]
        if w["filter_loss"] and ev["first_loss"] < 0:
            ev["first_loss"] = w["first_loss_state"]
    ev.update(tot)
    ev["lossy"] = int(tot["filter_loss"] > 0)
    ev["root_best"] = max((w["root_refuted"] / w["root_kept_solv"] if w["root_kept_solv"] else 0.0)
                          for w in walks)
    ev["fitness"] = round(fitness(walks, res, n), 4)
    return ev


def confirm(masks, cfg, k):
    """The official confirmation of one hit: decide_native under the published and the
    repaired rules, and the Python reference to 24 customers."""
    from mosp.instance import MOSPInstance
    from paper1.search_check import matrix_from_masks
    from satisfiability.customer_search import decide
    from satisfiability.native import decide_native
    inst = MOSPInstance.from_matrix(matrix_from_masks(masks), name="false_refutation_hunt")
    kw = config_kwargs(cfg)
    pub = decide_native(inst, k, repaired_rules=False, **kw)
    rep = decide_native(inst, k, repaired_rules=True, **kw)
    py = None
    if len(masks) <= 24:
        try:
            py = decide(inst, k, native=False, repaired_rules=False, **kw).status
        except Exception as exc:                   # a flag the Python lacks
            py = f"n/a ({type(exc).__name__})"
    return {"config": config_name(cfg), "k": k, "native_published": pub.status if pub else None,
            "native_repaired": rep.status if rep else None, "python_published": py}


def minimise(masks, deadline=None):
    """Delete vertices, then edges, while the certificate (`any_hit`) still holds."""
    cur = list(masks)
    changed = True
    while changed:
        changed = False
        for v in range(len(cur) - 1, -1, -1):
            if deadline and time.time() > deadline:
                return cur
            cand = delete_vertex(cur, v)
            if len(cand) >= 2 and any_hit(cand):
                cur = cand
                changed = True
        for u, v in edges_of(cur):
            if deadline and time.time() > deadline:
                return cur
            cand = list(cur)
            cand[u] &= ~(1 << v)
            cand[v] &= ~(1 << u)
            if any_hit(cand):
                cur = cand
                changed = True
                break
    return cur


def reproduce_cmd(masks):
    return f"python -m paper1.false_refutation_hunt --reproduce '{json.dumps(list(masks))}'"


def reproduce(masks):
    res = certify(masks)
    print(f"n = {len(masks)}, repaired optimum k = {res['k']} ({res['status']}), "
          f"witness {res['witness']} simulates to peak {res['peak']}")
    if len(masks) <= ORACLE_N:
        print(f"oracle (subset DP) optimum: {oracle(masks)}")
    from mosp.instance import MOSPInstance
    from paper1.search_check import matrix_from_masks
    from satisfiability.native import decide_native
    inst = MOSPInstance.from_matrix(matrix_from_masks(masks), name="reproduce")
    for kk in (res["k"], res["k"] + 1):
        for c in CONFIGS:
            pub = decide_native(inst, kk, repaired_rules=False, **config_kwargs(c))
            rep = decide_native(inst, kk, repaired_rules=True, **config_kwargs(c))
            flag = "  <-- FALSE REFUTATION" if pub.status == "unsat" else ""
            flag += "  <-- REPAIRED BUG" if rep.status != "sat" else ""
            if kk == res["k"] or flag:
                print(f"k={kk} {config_name(c):40s} published {pub.status:6s} repaired {rep.status}{flag}")
    print(f"certified false refutations: {len(res['hits'])}; repaired failures: {len(res['repaired_bad'])}")


# ----------------------------------------------------------------------------
# moves
# ----------------------------------------------------------------------------

def mutate(masks, rng, info=None):
    """One move. `info` is the last evaluation, used to steer."""
    n = len(masks)
    m = list(masks)
    target = None
    if info:
        S = info.get("first_loss", -1)
        if S is not None and 0 < S < (1 << n):
            target = S
    r = rng.random()
    if r < 0.10:                                      # swap two labels
        p = list(range(n))
        i, j = rng.sample(range(n), 2)
        p[i], p[j] = p[j], p[i]
        return relabel(m, p), "swap"
    if r < 0.15:                                      # a vertex to the front
        v = rng.randrange(n)
        order = [v] + [u for u in range(n) if u != v]
        p = [0] * n
        for new, old in enumerate(order):
            p[old] = new
        return relabel(m, p), "front"
    if r < 0.20 and target:                           # steer the loss state to the lowest labels
        inside = list(bits(target))
        opened = 0
        for c in inside:
            opened |= m[c]
        mid = list(bits(opened & ~target))
        rest = [u for u in range(n) if u not in inside and u not in mid]
        rng.shuffle(rest)
        order = inside + mid + rest if rng.random() < 0.5 else inside + rest + mid
        p = [0] * n
        for new, old in enumerate(order):
            p[old] = new
        return relabel(m, p), "steer"
    if r < 0.22:
        return relabel(m, random_perm(rng, n)), "shuffle"
    if r < 0.40:                                      # add an edge, near the loss state if any
        if target and rng.random() < 0.5:
            opened = 0
            for c in bits(target):
                opened |= m[c]
            u = rng.choice(list(bits(opened)))
            v = rng.randrange(n)
            if u != v:
                m[u] |= 1 << v
                m[v] |= 1 << u
                return m, "edge+near"
        u, v = rng.sample(range(n), 2)
        m[u] |= 1 << v
        m[v] |= 1 << u
        return m, "edge+"
    if r < 0.55:                                      # remove an edge
        E = edges_of(m)
        if E:
            u, v = rng.choice(E)
            m[u] &= ~(1 << v)
            m[v] &= ~(1 << u)
            return m, "edge-"
        return m, "noop"
    if r < 0.63 and n < GROW_N:                       # add a customer
        k = rng.choice((1, 1, 2, 2, 3, 4))
        nb = rng.sample(range(n), min(k, n))
        new = 1 << n
        for u in nb:
            new |= 1 << u
            m[u] |= 1 << n
        m.append(new)
        if rng.random() < 0.5:
            return relabel(m, random_perm(rng, n + 1)), "vertex+"
        return m, "vertex+"
    if r < 0.70 and n > MIN_N:
        return delete_vertex(m, rng.randrange(n)), "vertex-"
    if r < 0.77 and n < GROW_N:                       # a twin: the counterexample's 3 and 4
        v = rng.randrange(n)
        true_twin = rng.random() < 0.3
        new = (m[v] & ~(1 << v)) | (1 << n) | ((1 << v) if true_twin else 0)
        for u in bits(new & ~(1 << n)):
            m[u] |= 1 << n
        m.append(new)
        return m, "twin"
    if r < 0.81 and n < GROW_N:                       # a pendant
        v = rng.randrange(n)
        m[v] |= 1 << n
        m.append((1 << n) | (1 << v))
        return m, "pendant"
    if r < 0.86 and n < GROW_N:                       # split v: some neighbours go to v'
        v = rng.randrange(n)
        nb = list(bits(m[v] & ~(1 << v)))
        if len(nb) >= 2:
            moved = rng.sample(nb, rng.randint(1, len(nb) - 1))
            for u in moved:
                m[u] &= ~(1 << v)
                m[v] &= ~(1 << u)
                m[u] |= 1 << n
            new = (1 << n) | sum(1 << u for u in moved)
            if rng.random() < 0.5:
                new |= 1 << v
                m[v] |= 1 << n
            m.append(new)
            return m, "split"
        return m, "noop"
    if r < 0.91 and n > MIN_N:                        # merge: contract an edge
        E = edges_of(m)
        if E:
            u, v = rng.choice(E)
            for w in bits(m[v] & ~(1 << v) & ~(1 << u)):
                m[u] |= 1 << w
                m[w] |= 1 << u
            return delete_vertex(m, v), "merge"
        return m, "noop"
    if r < 0.95:                                      # rewire one endpoint of an edge
        E = edges_of(m)
        if E:
            u, v = rng.choice(E)
            w = rng.randrange(n)
            if w not in (u, v) and not m[u] >> w & 1:
                m[u] &= ~(1 << v)
                m[v] &= ~(1 << u)
                m[u] |= 1 << w
                m[w] |= 1 << u
                return m, "rewire"
        return m, "noop"
    room = MAX_N - n                                  # bridge to a small graph
    if room >= 3:
        from paper1.search_check import DEFINITE_CEX
        if rng.random() < 0.5 and room >= 6:
            src = DEFINITE_CEX[0][0]
            keep = sorted(rng.sample(range(14), min(room, rng.randint(6, 14))))
            piece = [sum(1 << keep.index(w) for w in bits(src[v]) if w in keep) for v in keep]
        else:
            size = rng.randint(3, min(room, 8))
            piece = [x & ((1 << size) - 1) for x in gen_family(rng, size, rng.randrange(4))[:size]]
        s = len(piece)
        out = m + [x << n for x in piece]
        for _ in range(rng.randint(0, 2)):
            u = rng.randrange(n)
            v = n + rng.randrange(s)
            out[u] |= 1 << v
            out[v] |= 1 << u
        return out, "bridge"
    return m, "noop"


# ----------------------------------------------------------------------------
# workers
# ----------------------------------------------------------------------------

def read_jsonl(path):
    """Every complete JSON line; a partial last line (a crash) is skipped."""
    out = []
    try:
        with open(path) as fh:
            for line in fh:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return out


def read_archive(path, top=300):
    best = {}
    for e in read_jsonl(path):
        if not isinstance(e, dict) or "masks" not in e or "fitness" not in e:
            continue
        k_ = key(e["masks"])
        if k_ not in best or best[k_]["fitness"] < e["fitness"]:
            best[k_] = e
    return sorted(best.values(), key=lambda e: -e["fitness"])[:top]


def baseline_graph(rng):
    n = rng.randint(12, MAX_N if rng.random() < 0.3 else 24)
    r = rng.random()
    if r < 0.4:
        g = gen_family(rng, n, 4)
    elif r < 0.7:
        g = gen_family(rng, n, rng.randrange(4))
    else:
        from paper1.search_check import random_cover, random_sparse
        g = (random_sparse if rng.random() < 0.5 else random_cover)(n, rng)
        g = [m or 1 << v for v, m in enumerate(g)]   # a customer with no product: give it one
    return relabel(g, random_perm(rng, len(g)))


def start_graph(rng, archive, seed_graphs):
    r = rng.random()
    if r < 0.30 and archive:
        e = archive[min(int(rng.expovariate(1 / 20)), len(archive) - 1)]
        g, how = list(e["masks"]), "archive"
    elif r < 0.55:
        g, how = list(seed_graphs["cex14"]), "cex14"
    elif r < 0.65:
        name = rng.choice(sorted(seed_graphs))
        g, how = list(seed_graphs[name]), name
    else:
        g, how = gen_family(rng, rng.randint(12, 24), 4), "gadget"
    if rng.random() < 0.5:
        g = relabel(g, random_perm(rng, len(g)))
    return g, how


def size_bin(n):
    for lo, hi in SIZE_BINS:
        if lo <= n <= hi:
            return f"{lo}-{hi}"
    return "other"


def worker(wid, seed, until, outq, archive_path, frontier=None):
    try:
        os.nice(5)
    except OSError:
        pass
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    rng = random.Random(seed)
    lib()
    seed_graphs = seeds()
    stats = dict(tested=0, lossy=0, filter_loss=0, def_loss=0, false_ref=0, memo_poison=0,
                 seen_loss=0, aborted=0, oracle_checks=0, root_near=0, best=-1e9, restarts=0,
                 max_eval_seconds=0.0, sizes={})
    state = {"cur": None, "how": None}
    last_flush = time.time()

    def flush(force=False):
        nonlocal last_flush
        if force or time.time() - last_flush > 20:
            outq.put(("stats", wid, dict(stats, sizes=dict(stats["sizes"])),
                      {"cur": state["cur"], "how": state["how"]}))
            last_flush = time.time()

    def stop_report(kind, ev, extra):
        outq.put((kind, {"masks": ev["masks"], "n": ev["n"], "k": ev["k"],
                         "witness": ev["witness"], "peak": ev["peak"], **extra,
                         "reproduce": reproduce_cmd(ev["masks"])}))

    def consider(masks, how):
        t0 = time.time()
        ev = evaluate(masks)
        stats["max_eval_seconds"] = max(stats["max_eval_seconds"], round(time.time() - t0, 3))
        stats["tested"] += 1
        b = size_bin(len(masks))
        stats["sizes"][b] = stats["sizes"].get(b, 0) + 1
        if ev["status"] == "aborted" or ev["aborted"]:
            stats["aborted"] += 1
        if ev["status"] == "witness_invalid":
            stop_report("repaired_bug", ev, {"kind": "repaired witness does not simulate to <= k"})
            return ev
        if ev["repaired_bad"]:
            stop_report("repaired_bug", ev, {"kind": "repaired unsat at a k the witness covers",
                                             "configs": [(config_name(c), k) for c, k in ev["repaired_bad"]]})
            return ev
        if ev["status"] != "ok":
            return ev
        stats["lossy"] += ev["lossy"]
        for k_ in ("filter_loss", "def_loss", "false_ref", "memo_poison", "seen_loss"):
            stats[k_] += ev[k_]
        stats["root_near"] += ev.get("root_best", 0) >= 0.8
        stats["best"] = max(stats["best"], ev["fitness"])
        if len(masks) <= ORACLE_N and rng.random() < ORACLE_RATE:
            stats["oracle_checks"] += 1
            ko = oracle(masks)
            if ko != ev["k"]:
                stop_report("repaired_bug", ev, {"kind": "oracle disagrees with the repaired optimum",
                                                 "oracle": ko})
        if ev["hits"]:
            handle_hit(ev, how)
        return ev

    def handle_hit(ev, how):
        masks = ev["masks"]
        checks = [confirm(masks, c, k) for c, k in ev["hits"][:6]]
        if not any(x["native_published"] == "unsat" and x["native_repaired"] == "sat" for x in checks):
            outq.put(("mismatch", {"masks": masks, "k": ev["k"], "checks": checks,
                                   "reproduce": reproduce_cmd(masks)}))
            return
        outq.put(("log", f"worker {wid}: certified hit at n={len(masks)} k={ev['k']}, minimising"))
        small = minimise(masks, deadline=time.time() + 1800)
        sm = any_hit(small)
        entry = {"found": dt.datetime.now().isoformat(timespec="seconds"), "worker": wid, "how": how,
                 "masks": masks, "n": len(masks), "k": ev["k"], "witness": ev["witness"],
                 "peak": ev["peak"], "configs": [(config_name(c), k) for c, k in ev["hits"]],
                 "checks": checks, "reproduce": reproduce_cmd(masks)}
        if sm:
            entry["minimised"] = {
                "masks": small, "n": len(small), "edges": len(edges_of(small)), "k": sm["k"],
                "witness": sm["witness"], "peak": order_cost(small, sm["witness"]),
                "configs": [(config_name(c), k) for c, k in sm["hits"]],
                "checks": [confirm(small, c, k) for c, k in sm["hits"][:6]],
                "oracle": oracle(small) if len(small) <= ORACLE_N else None,
                "reproduce": reproduce_cmd(small)}
        outq.put(("hit", entry))

    archive = read_archive(archive_path)
    first = True
    while until is None or time.time() < until:
        stats["restarts"] += 1
        if stats["restarts"] % 20 == 0:
            archive = read_archive(archive_path)
        if not first and rng.random() < 0.15:          # the baseline
            g = baseline_graph(rng)
            for _ in range(3):
                consider(g, "baseline")
                g = relabel(g, random_perm(rng, len(g)))
            flush()
            continue
        if first and frontier and frontier.get("cur"):
            g, how = list(frontier["cur"]), (frontier.get("how") or "resume").split(":")[0] + ":resumed"
        else:
            g, how = start_graph(rng, archive, seed_graphs)
        first = False
        cur = consider(g, how)
        if cur["status"] != "ok":
            continue
        top = cur
        state["cur"], state["how"] = cur["masks"], how
        steps = rng.choice((150, 300, 600))
        # each restart its own ceiling, so the sizes stay spread instead of piling up at MAX_N
        cap = max(len(g), rng.choice(SIZE_CAPS))
        T0 = 1.5
        for step in range(steps):
            if until is not None and time.time() >= until:
                break
            T = T0 * (0.02 / T0) ** (step / steps)
            cand = cur["masks"]
            moves = []
            for _ in range(1 if rng.random() < 0.6 else rng.randint(2, 3)):
                cand, mv = mutate(cand, rng, cur)
                moves.append(mv)
            if not (2 <= len(cand) <= cap):
                continue
            ev = consider(cand, how + ":" + "+".join(moves))
            if ev["status"] != "ok":
                continue
            d = ev["fitness"] - cur["fitness"]
            if d >= 0 or rng.random() < math.exp(d / T):
                cur = ev
                state["cur"] = cur["masks"]
            if ev["fitness"] > top["fitness"]:
                top = ev
            flush()
        if top["fitness"] > 0:
            outq.put(("archive", {k_: top.get(k_) for k_ in
                                  ("masks", "n", "k", "fitness", "lossy", "root_best", "filter_loss",
                                   "def_loss", "false_ref", "memo_poison", "seen_loss", "audit_fail")}
                      | {"how": how, "worker": wid}))
    flush(force=True)
    outq.put(("done", wid))


# ----------------------------------------------------------------------------
# the main process
# ----------------------------------------------------------------------------

def atomic_write(path, text):
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


class Writer:
    def __init__(self, out):
        self.out = out
        out.mkdir(parents=True, exist_ok=True)
        self.log_path = out / "progress.log"
        if not self.log_path.exists():
            self.log_path.write_text(f"# restart after a reboot, from any directory:\n# {RESTART}\n")

    def append(self, name, obj):
        path = self.out / name
        lead = ""
        try:                                      # a crash may have left a partial last line
            with open(path, "rb") as fh:
                fh.seek(-1, os.SEEK_END)
                lead = "" if fh.read(1) == b"\n" else "\n"
        except OSError:
            pass
        with open(path, "a") as fh:
            fh.write(lead + json.dumps(obj) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def log(self, msg):
        line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
        with open(self.log_path, "a") as fh:
            fh.write(line + "\n")
        print(line, flush=True)


def found_md(e):
    lines = ["# A whole-instance false refutation by the published rules", "",
             f"Found {e['found']} by worker {e['worker']} ({e['how']}).", "",
             "The certificate: the repaired search finds a closing order whose simulated peak is at",
             "most k, and the published search, in the configuration below, answers unsat at k.", ""]
    for title, x in (("Minimised", e.get("minimised")), ("As found", e)):
        if not x:
            continue
        lines += [f"## {title}", "",
                  f"- customers: {x['n']}" + (f", edges: {x['edges']}" if "edges" in x else ""),
                  f"- masks (closed neighbourhoods): `{json.dumps(x['masks'])}`",
                  f"- repaired optimum k = {x['k']}" + (f"; subset-DP oracle: {x['oracle']}"
                                                         if x.get("oracle") is not None else ""),
                  f"- witness closing order: `{json.dumps(x['witness'])}`, simulated peak {x['peak']}",
                  "- published configurations answering unsat (configuration, k): "
                  + ", ".join(f"{c} at {k}" for c, k in x["configs"]),
                  f"- official confirmation (decide_native and the Python reference): "
                  f"`{json.dumps(x['checks'])}`",
                  f"- reproduce: `{x['reproduce']}`", ""]
    return "\n".join(lines)


def run(workers, until, out=OUT, archive_keep=500):
    import multiprocessing as mp
    out = Path(out)
    W = Writer(out)
    if (out / "FOUND.md").exists():
        W.log("FOUND.md exists: a hit is already recorded, nothing to do")
        return 0
    if (out / "REPAIRED_BUG.jsonl").exists():
        W.log("REPAIRED_BUG.jsonl exists: the repaired search has a reported bug; not restarting")
        return 2
    atomic_write(out / "hunt.pid", f"{os.getpid()}\n")
    lib()                                             # build once, before the workers
    ck_path = out / "checkpoint.json"
    try:
        ck = json.loads(ck_path.read_text())
    except (OSError, ValueError):
        ck = {}
    epoch = ck.get("epoch", 0) + 1
    base = ck.get("counters", {})
    base_sizes = ck.get("sizes", {})
    frontiers = ck.get("frontiers", {})
    archive = {key(e["masks"]): e for e in read_archive(out / "archive.jsonl", archive_keep)}
    if ck:
        W.log(f"resumed from checkpoint at {ck.get('saved')}, {base.get('tested', 0)} candidates so far"
              f" (epoch {epoch}, archive {len(archive)}, frontiers {len(frontiers)})")
    W.log(f"start pid {os.getpid()} workers {workers} until "
          f"{dt.datetime.fromtimestamp(until).isoformat() if until else 'the first hit'}")
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    stamp = time.time_ns() % (1 << 40)
    procs = [ctx.Process(target=worker, daemon=True,
                         args=(i, (epoch * 1_000_003 + i * 7919) ^ stamp, until, q,
                               str(out / "archive.jsonl"), frontiers.get(str(i))))
             for i in range(workers)]
    for p in procs:
        p.start()
    W.log("workers " + " ".join(str(p.pid) for p in procs))
    per, front = {}, dict(frontiers)
    started = time.time()
    last_log = time.time()
    last_compact = time.time()
    done = set()
    stop = {"why": None}

    def on_term(signum, frame):
        stop["why"] = "signal"

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)

    def totals():
        t = {k_: v for k_, v in base.items() if k_ not in ("best", "max_eval_seconds")}
        sizes = dict(base_sizes)
        for s in per.values():
            for k_, v in s.items():
                if k_ in ("best", "max_eval_seconds", "sizes"):
                    continue
                t[k_] = t.get(k_, 0) + v
            for b, v in s["sizes"].items():
                sizes[b] = sizes.get(b, 0) + v
        t["best"] = max([base.get("best", -1e9)] + [s["best"] for s in per.values()])
        t["max_eval_seconds"] = max([base.get("max_eval_seconds", 0)] +
                                    [s["max_eval_seconds"] for s in per.values()])
        return t, sizes

    def checkpoint():
        t, sizes = totals()
        atomic_write(ck_path, json.dumps({"saved": dt.datetime.now().isoformat(timespec="seconds"),
                                          "epoch": epoch, "counters": t, "sizes": sizes,
                                          "frontiers": front}, indent=1))

    def progress():
        t, sizes = totals()
        run_tested = sum(s["tested"] for s in per.values())
        rate = run_tested / max(1e-9, time.time() - started)
        hist = " ".join(f"{b}:{sizes[b]}" for b in sorted(
            sizes, key=lambda x: int(x.split("-")[0]) if x[0].isdigit() else 999))
        W.log(f"tested {t.get('tested', 0)} ({rate:.1f}/s) best_fitness {t['best']:.3f}"
              f" node_losses {t.get('filter_loss', 0)} (definite {t.get('def_loss', 0)})"
              f" lossy_graphs {t.get('lossy', 0)} false_ref_nodes {t.get('false_ref', 0)}"
              f" memo_poison {t.get('memo_poison', 0)} seen_loss {t.get('seen_loss', 0)}"
              f" root>=80% {t.get('root_near', 0)} aborted {t.get('aborted', 0)}"
              f" oracle_checks {t.get('oracle_checks', 0)} max_eval {t['max_eval_seconds']:.2f}s"
              f" sizes {hist} alive {sum(p.is_alive() for p in procs)}")
        checkpoint()

    while len(done) < workers and not stop["why"]:
        try:
            msg = q.get(timeout=5)
        except queue.Empty:
            msg = None
            if not any(p.is_alive() for p in procs):
                break
        if msg:
            kind = msg[0]
            if kind == "stats":
                per[msg[1]] = msg[2]
                if msg[3].get("cur"):
                    front[str(msg[1])] = msg[3]
            elif kind == "done":
                done.add(msg[1])
            elif kind == "log":
                W.log(msg[1])
            elif kind == "archive":
                e = msg[1]
                k_ = key(e["masks"])
                if k_ not in archive or archive[k_]["fitness"] < e["fitness"]:
                    floor = (sorted(x["fitness"] for x in archive.values())[-archive_keep]
                             if len(archive) >= archive_keep else -1e9)
                    if e["fitness"] > floor:
                        archive[k_] = e
                        W.append("archive.jsonl", e)
            elif kind == "mismatch":
                W.append("mismatch.jsonl", msg[1])
                W.log(f"a hit not confirmed by decide_native (helper mismatch): {msg[1]['reproduce']}")
            elif kind == "hit":
                e = msg[1]
                W.append("hits.jsonl", e)
                atomic_write(out / "FOUND.md", found_md(e))
                m = e.get("minimised") or e
                W.log(f"HIT FOUND n={e['n']} k={e['k']} minimised to n={m['n']} k={m['k']}"
                      f" configs={[c for c, _ in m['configs']][:3]} -- {m['reproduce']}")
                stop["why"] = "hit"
            elif kind == "repaired_bug":
                W.append("REPAIRED_BUG.jsonl", msg[1])
                W.log(f"!!!!!!!! BUG IN THE REPAIRED SEARCH ({msg[1]['kind']}): "
                      f"{msg[1]['reproduce']} -- stopping the hunt")
                stop["why"] = "repaired bug"
        if time.time() - last_log > CHECKPOINT_SECONDS:
            progress()
            last_log = time.time()
        if time.time() - last_compact > 3600:            # keep archive.jsonl small
            keep = sorted(archive.values(), key=lambda x: -x["fitness"])[:archive_keep]
            archive = {key(e["masks"]): e for e in keep}
            atomic_write(out / "archive.jsonl", "".join(json.dumps(e) + "\n" for e in keep))
            last_compact = time.time()
    for p in procs:
        if p.is_alive():
            p.terminate()
    for p in procs:
        p.join(timeout=10)
    try:
        while True:
            msg = q.get_nowait()
            if msg[0] == "stats":
                per[msg[1]] = msg[2]
    except (queue.Empty, OSError, EOFError, ValueError):
        pass
    progress()
    W.log(f"stopped ({stop['why'] or 'deadline'})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--until", default=None, help="ISO time to stop; default: run until the first hit")
    ap.add_argument("--minutes", type=float, default=None, help="or run this long")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--reproduce", default=None, help="a JSON list of masks")
    a = ap.parse_args(argv)
    if a.reproduce:
        reproduce(json.loads(a.reproduce))
        return 0
    if a.workers > 4:
        sys.exit("at most 4 workers: the other cores belong to another run")
    until = None
    if a.until:
        until = dt.datetime.fromisoformat(a.until).timestamp()
    elif a.minutes:
        until = time.time() + 60 * a.minutes
    return run(a.workers, until, Path(a.out))


if __name__ == "__main__":
    sys.exit(main())
