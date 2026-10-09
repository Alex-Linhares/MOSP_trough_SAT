"""Why the last root branch survives: anatomy of the false-refutation hunt's near-misses.

The hunt (`paper1/false_refutation_hunt.py`) finds graphs on which Chu &
Stuckey's published rules falsely refute all but one of the root's solvable
branches. This module re-runs a near-miss under the published search, ported
node for node from `satisfiability/customer_search.c` (the port is checked
against the C's node count and answer, through the hunt's own `c_decide`, on
every graph it studies), with an exact judge of `Sol_k(S)` beside it, and
reports for each root branch where its solution was lost.

    python -m paper1.near_miss_study anatomy  [--top 6]   # study archive near-misses
    python -m paper1.near_miss_study kill     [...]        # targeted edits

Reads the hunt's archive (read only). Writes `paper1/data/near_miss_study/`.
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

sys.setrecursionlimit(100000)

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "data" / "false_refutation_hunt" / "archive.jsonl"
OUT = HERE / "data" / "near_miss_study"


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def pc(x):
    return x.bit_count()


# ----------------------------------------------------------------------------
# configurations (definite, subset, better, dominators, old, memo, fan): as the hunt
# ----------------------------------------------------------------------------

DEFAULT = (1, 1, 0, 4, 1, 1, 0)
CSEARCH = (1, 1, 1, 0, 1, 1, 0)
WALKS = [DEFAULT, CSEARCH, (1, 1, 1, 4, 1, 1, 0), (1, 0, 0, 4, 1, 1, 0), (1, 1, 0, 4, 0, 0, 0)]


def cname(c):
    d, s, b, dom, old, memo, fan = c
    rules = "+".join(r for r, on in (("definite", d), ("subset", s)) if on)
    if b:
        rules += ("+" if rules else "") + f"better/L{dom}"
    return rules + ("/old" if old else "") + ("/memo" if memo else "") + ("/degree" if fan else "")


# ----------------------------------------------------------------------------
# the exact judge: Sol_k(S) for free-closed S
# ----------------------------------------------------------------------------

class Judge:
    def __init__(self, masks, k):
        self.m = masks
        self.k = k
        self.n = len(masks)
        self.full = (1 << self.n) - 1
        self.memo = {}

    def opened(self, closed):
        o = 0
        for c in bits(closed):
            o |= self.m[c]
        return o

    def close_free(self, closed, opened):
        for c in bits(self.full & ~closed):
            if self.m[c] & ~opened == 0:
                closed |= 1 << c
        return closed

    def sol(self, closed, opened=None):
        """Does some closing order from `closed` keep every step at <= k open stacks?"""
        if opened is None:
            opened = self.opened(closed)
        closed = self.close_free(closed, opened)
        if closed == self.full:
            return True
        r = self.memo.get(closed)
        if r is not None:
            return r
        open_now = pc(opened & ~closed)
        R = list(bits(self.full & ~closed))
        opens = {c: self.m[c] & ~opened for c in R}
        cand = [c for c in R if open_now + pc(opens[c]) <= self.k]
        # the subset rule with index tie-break: sound (strict partial order on R)
        kept = []
        for c in cand:
            dom = False
            for d in R:
                if d != c and opens[d] & ~opens[c] == 0 and (opens[d] != opens[c] or d < c):
                    dom = True
                    break
            if not dom:
                kept.append(c)
        if not kept:
            kept = cand
        kept.sort(key=lambda c: pc(opens[c]))
        res = False
        for c in kept:
            if self.sol(closed | 1 << c, opened | self.m[c]):
                res = True
                break
        self.memo[closed] = res
        return res

    def witness(self, closed=0, opened=None):
        """A closing order from `closed` of cost <= k, or None."""
        if opened is None:
            opened = self.opened(closed)
        order = []
        while True:
            c2 = self.close_free(closed, opened)
            order += list(bits(c2 & ~closed))
            closed = c2
            if closed == self.full:
                return order
            nxt = None
            open_now = pc(opened & ~closed)
            for c in bits(self.full & ~closed):
                if open_now + pc(self.m[c] & ~opened) <= self.k and \
                        self.sol(closed | 1 << c, opened | self.m[c]):
                    nxt = c
                    break
            if nxt is None:
                return None
            order.append(nxt)
            closed |= 1 << nxt
            opened |= self.m[nxt]


def b_of(masks, T):
    o = 0
    for c in bits(T):
        o |= masks[c]
    return pc(o & ~T)


def order_cost(masks, order):
    n = len(masks)
    if order is None or sorted(order) != list(range(n)):
        return None
    T = O = peak = 0
    for c in order:
        O |= masks[c]
        peak = max(peak, pc(O & ~T))
        T |= 1 << c
    return peak


def hereditary(masks, closed, q):
    """Is q hereditarily definite at closed: b(X) <= b(B) for all S <= B <= X, q not in B
    (brute force over the freed customers). Returns (ok, worst B)."""
    opened = 0
    for c in bits(closed):
        opened |= masks[c]
    own = masks[q] & ~opened
    n = len(masks)
    full = (1 << n) - 1
    X = closed | 1 << q
    for d in bits(full & ~closed):
        if masks[d] & ~(opened | masks[q]) == 0:
            X |= 1 << d
    bX = b_of(masks, X)
    Y = [d for d in bits(X & ~closed) if d != q]
    best = None
    for sub in range(1 << len(Y)):
        B = closed
        for i, d in enumerate(Y):
            if sub >> i & 1:
                B |= 1 << d
        bb = b_of(masks, B)
        if bb < bX and (best is None or bb < best[1]):
            best = (B, bb)
    return best is None, best, X, bX


# ----------------------------------------------------------------------------
# the published search, instrumented (a port of customer_search.c `search`)
# ----------------------------------------------------------------------------

class Published:
    """The C's `search` with `repaired_rules = 0`, node for node.

    Records, per expanded node: closed (after free moves), seen, candidates P,
    kept L, the rule that fired and its citations, children results."""

    def __init__(self, masks, k, cfg, max_nodes=3_000_000):
        self.m = masks
        self.k = k
        self.n = len(masks)
        self.full = (1 << self.n) - 1
        (self.definite, self.subset, self.better, self.dom, self.old, self.use_memo,
         self.fan) = cfg
        self.memo = set()
        self.nodes = 0
        self.max_nodes = max_nodes
        self.aborted = False
        self.records = {}       # closed -> record of the (first) expansion
        self.memo_hits = []     # (closed, parent closed) where a memo hit cut a child

    def filter(self, closed, opened, candidates, R, opens, open_now):
        P = [c for c in R if candidates >> c & 1 and open_now + pc(opens[c]) <= self.k]
        info = {"rule": None, "links": []}
        if not P or not (self.subset or self.definite or self.better):
            return P, info
        if self.definite:
            for c in P:
                own = opens[c]
                ob = pc(own)
                cb = sum(1 for d in R if pc(opens[d]) <= ob and opens[d] & ~own == 0)
                if cb >= ob:
                    info["rule"] = "definite"
                    info["q"] = c
                    info["links"] = [(r, c, "definite") for r in P if r != c]
                    return [c], info
        L = list(P)
        if self.subset:
            kept = []
            for c in L:
                own = opens[c]
                cover = None
                for d in R:
                    if pc(opens[d]) > pc(own) or d == c:
                        continue
                    if opens[d] & ~own == 0 and (opens[d] != own or d < c):
                        cover = d
                        break
                if cover is None:
                    kept.append(c)
                else:
                    info["links"].append((c, cover, "subset"))
            if kept:
                L = kept
            else:
                info["links"] = [x for x in info["links"] if x[2] != "subset"]
        if self.better and len(L) > 1:
            lim = self.dom if 0 < self.dom < len(L) else len(L)
            kept = []
            for ri, r in enumerate(L):
                closed_r = closed | 1 << r
                opened_r = opened | self.m[r]
                cover = None
                for qi in range(min(lim, ri)):
                    q = L[qi]
                    if pc((opened_r | self.m[q]) & ~closed_r) > self.k:
                        continue
                    own = self.m[q] & ~opened_r
                    cb = 0
                    for d in bits(self.full & ~closed_r):
                        left = self.m[d] & ~opened_r
                        if left and left & ~own == 0:
                            cb += 1
                    if cb >= pc(own):
                        cover = q
                        break
                if cover is None:
                    kept.append(r)
                else:
                    info["links"].append((r, cover, "better"))
            if kept:
                L = kept
        return L, info

    def sort(self, L, opens, open_now, closed):
        if self.fan:
            rem = self.full & ~closed
            return sorted(L, key=lambda c: (open_now + pc(opens[c]),
                                            -(pc(self.m[c] & rem) - 1), c))
        return sorted(L, key=lambda c: (open_now + pc(opens[c]), c))

    def search(self, closed, opened, seen, depth=0, parent=None):
        R0 = list(bits(self.full & ~closed))
        free = 0
        for c in R0:
            if self.m[c] & ~opened == 0:
                free |= 1 << c
        closed |= free
        if closed == self.full:
            return True
        if self.use_memo and closed in self.memo:
            self.memo_hits.append((closed, parent))
            return False
        rem = self.full & ~closed
        seen &= rem
        candidates = rem & ~seen if self.old else rem
        R = list(bits(rem))
        opens = {c: self.m[c] & ~opened for c in R}
        open_now = pc(opened & ~closed)
        L, info = self.filter(closed, opened, candidates, R, opens, open_now)
        L = self.sort(L, opens, open_now, closed)
        rec = {"closed": closed, "seen": seen, "depth": depth, "L": L, "info": info,
               "P": [c for c in R if candidates >> c & 1 and open_now + pc(opens[c]) <= self.k],
               "children": [], "parent": parent}
        if closed not in self.records:
            self.records[closed] = rec
        for c in L:
            self.nodes += 1
            if self.nodes > self.max_nodes:
                self.aborted = True
                return False
            inherited = 0
            if self.old and seen:
                for q in bits(seen):
                    if pc((opened | self.m[q] | self.m[c]) & ~(closed | 1 << q)) <= self.k:
                        inherited |= 1 << q
            child_closed = closed | 1 << c
            r = self.search(child_closed, opened | self.m[c], inherited, depth + 1, closed)
            rec["children"].append((c, r, inherited))
            if r:
                rec["result"] = True
                return True
            if self.aborted:
                return False
            seen |= 1 << c
        rec["result"] = False
        if self.use_memo:
            self.memo.add(closed)
        return False


# ----------------------------------------------------------------------------
# anatomy
# ----------------------------------------------------------------------------

def fmt(mask):
    return "{" + ",".join(map(str, bits(mask))) + "}"


def trace_loss(pub, judge, closed, opened_of):
    """Descend from a falsely refuted node along falsely refuted kept children to the
    node where the solution was lost. Returns a description."""
    path = []
    cur = closed
    for _ in range(200):
        rec = pub.records.get(cur)
        if rec is None:
            return {"kind": "memo", "state": cur, "path": path}
        sol_children = []
        for c, r, inh in rec["children"]:
            cc = judge.close_free(cur | 1 << c, judge.opened(cur | 1 << c))
            if judge.sol(cc):
                sol_children.append((c, cc, inh))
        if sol_children:
            c, cc, inh = sol_children[0]
            path.append(c)
            # the child might have been cut by memo (record belongs to another visit)
            crec = pub.records.get(cc)
            if crec is None or crec.get("parent") != cur and cc in pub.memo:
                if crec is None:
                    return {"kind": "memo", "state": cc, "path": path}
            cur = cc
            continue
        # no kept child is solvable: the loss is here
        opened = judge.opened(cur)
        open_now = pc(opened & ~cur)
        lost = [c for c in bits(pub.full & ~cur)
                if open_now + pc(pub.m[c] & ~opened) <= pub.k and judge.sol(cur | 1 << c)]
        info = rec["info"]
        why = {}
        for c in lost:
            if rec["seen"] >> c & 1:
                why[c] = "old move (seen)"
            else:
                cites = [l for l in info["links"] if l[0] == c]
                why[c] = cites[0][2] + f"->{cites[0][1]}" if cites else "?"
        out = {"kind": "filter", "state": cur, "path": path, "rule": info["rule"],
               "kept": rec["L"], "lost_solvable": lost, "why": why, "seen": rec["seen"]}
        if info["rule"] == "definite":
            ok, worst, X, bX = hereditary(pub.m, cur, info["q"])
            out["q"] = info["q"]
            out["hereditary"] = ok
            out["X"] = X
            out["bX"] = bX
            out["b_state"] = b_of(pub.m, cur)
            if worst:
                out["better_B"] = worst
        return out
    return {"kind": "deep", "state": cur, "path": path}


def anatomy(masks, k, cfg, verbose=True):
    judge = Judge(masks, k)
    pub = Published(masks, k, cfg)
    ans = pub.search(0, 0, 0)
    root = pub.records.get(0) or pub.records.get(judge.close_free(0, 0))
    rootc = judge.close_free(0, 0)
    root = pub.records[rootc]
    rows = []
    for c in bits(pub.full & ~rootc):
        cost = pc(masks[c])
        kept = c in root["L"]
        s = judge.sol(rootc | 1 << c)
        res = None
        for cc, r, _ in root["children"]:
            if cc == c:
                res = r
        row = {"c": c, "cost": cost, "deg": pc(masks[c]) - 1, "kept": kept, "solvable": s,
               "published": res}
        if kept and s and res is False:
            row["loss"] = trace_loss(pub, judge, judge.close_free(rootc | 1 << c, masks[c]), None)
        rows.append(row)
    return {"answer": ans, "nodes": pub.nodes, "aborted": pub.aborted, "root_rule": root["info"]["rule"],
            "root_L": root["L"], "rows": rows, "pub": pub, "judge": judge}


def load_archive():
    out = []
    for line in open(ARCHIVE):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    best = {}
    for e in out:
        key = tuple(e["masks"])
        if key not in best or best[key]["fitness"] < e["fitness"]:
            best[key] = e
    return list(best.values())


# ----------------------------------------------------------------------------
# statistics over many near-misses
# ----------------------------------------------------------------------------

def survivor_profile(masks, k, cfg):
    """Per near-miss under one configuration: who survives and why it could."""
    A = anatomy(masks, k, cfg)
    pub, J = A["pub"], A["judge"]
    rootc = J.close_free(0, 0)
    root = pub.records[rootc]
    rs = [r for r in A["rows"] if r["kept"] and r["solvable"]]
    if not rs:
        return None
    surv = [r["c"] for r in rs if r["published"]]
    ref = [r["c"] for r in rs if r["published"] is False]
    order = root["L"]
    out = {"n": len(masks), "k": k, "config": cname(cfg), "kept_solvable": len(rs),
           "refuted": len(ref), "answer": A["answer"], "survivors": surv}
    if len(surv) != 1:
        return out
    s = surv[0]
    costs = {r["c"]: r["cost"] for r in rs}
    deg = [pc(m) - 1 for m in masks]
    out["surv_cost"] = costs[s]
    out["surv_cost_is_k"] = costs[s] == k
    out["surv_cost_rank"] = sorted(costs.values(), reverse=True).index(costs[s])   # 0 = most expensive
    out["surv_max_cost"] = costs[s] == max(costs.values())
    pos = [c for c in order if c in costs]
    out["surv_position_from_end"] = len(pos) - 1 - pos.index(s)   # 0 = last solvable explored
    out["surv_deg"] = deg[s]
    out["surv_deg_rank"] = sorted(deg, reverse=True).index(deg[s])
    out["surv_label_rank"] = sorted(costs).index(s) / max(1, len(costs) - 1)
    # what the survivor child inherited under old move
    for c, r, inh in root["children"]:
        if c == s:
            out["surv_inherited"] = pc(inh)
    # intrinsic deaths: each solvable branch searched alone, fresh memo, no seen
    intr = {}
    for c in costs:
        P = Published(masks, k, cfg)
        intr[c] = P.search(1 << c, masks[c], 0, 1, 0)
    out["intrinsically_dead"] = sum(1 for c in ref if not intr[c])
    out["poison_killed"] = sum(1 for c in ref if intr[c])
    # falsely refuted states in the memo / records: do any contain the survivor?
    false_states = [st for st, rec in pub.records.items()
                    if rec.get("result") is False and J.sol(st)]
    out["false_states"] = len(false_states)
    out["false_states_with_surv"] = sum(1 for st in false_states if st >> s & 1)
    # survivor's success path: is it ever reached by a state some refuted branch visited?
    path_states, cur = [], rootc
    while cur in pub.records:
        rec = pub.records[cur]
        succ = [c for c, r, _ in rec["children"] if r]
        path_states.append(cur)
        if not succ:
            break
        c = succ[0]
        cur = J.close_free(cur | 1 << c, J.opened(cur | 1 << c))
    out["surv_path_max_seen"] = max(pc(pub.records[p]["seen"]) for p in path_states[1:]) if len(path_states) > 1 else 0
    # loss states of the definite move (the traps) and their q
    traps = {}
    for st in false_states:
        rec = pub.records[st]
        if rec["info"]["rule"] == "definite":
            ok, worst, X, bX = hereditary(masks, st, rec["info"]["q"])
            if not ok:
                traps.setdefault(rec["info"]["q"], 0)
                traps[rec["info"]["q"]] += 1
    out["trap_qs"] = traps
    # when the survivor's path closes each trap q: fraction of N(q) already opened (or closed)
    fr = {}
    for q in traps:
        for i, st in enumerate(path_states):
            if st >> q & 1:
                prev = path_states[i - 1] if i else 0
                op = J.opened(prev)
                nb = masks[q] & ~(1 << q)
                fr[q] = round(pc(nb & op) / max(1, pc(nb)), 2)
                break
    out["surv_trap_nbr_opened"] = fr
    # and at the losses (first loss state per trap)
    fl = {}
    for st in false_states:
        rec = pub.records[st]
        q = rec["info"].get("q")
        if rec["info"]["rule"] == "definite" and q in traps and q not in fl:
            op = J.opened(st)
            nb = masks[q] & ~(1 << q)
            fl[q] = round(pc(nb & op) / max(1, pc(nb)), 2)
    out["loss_trap_nbr_opened"] = fl
    return out


def best_config(masks, k):
    best = None
    for cfg in WALKS:
        A = anatomy(masks, k, cfg)
        rs = [r for r in A["rows"] if r["kept"] and r["solvable"]]
        if not rs:
            continue
        f = sum(1 for r in rs if r["published"] is False) / len(rs)
        if best is None or f > best[0]:
            best = (f, cfg)
    return best


# ----------------------------------------------------------------------------
# the kill: glue two near-misses core to core
# ----------------------------------------------------------------------------

def glue(A, B, x, y):
    """Disjoint union of A (labels first) and B (labels after), plus the edge x-y (x in A, y in B)."""
    n = len(A)
    g = list(A) + [m << n for m in B]
    g[x] |= 1 << (n + y)
    g[n + y] |= 1 << x
    return g


def certified_hit(g):
    """The hunt's certificate (repaired witness <= k, published unsat at k), or None."""
    from paper1 import false_refutation_hunt as H
    res = H.certify(g)
    if res["status"] == "ok" and res["hits"] and order_cost(g, res["witness"]) <= res["k"]:
        return res
    return None
