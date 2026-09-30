"""Brute-force soundness check of the customer search's pruning rules (loop0006 item 06).

`paper2/search_soundness.md` §1-2 (item 05) states Chu & Stuckey's customer
search as a mathematical object and each of its pruning rules exactly as the
fixed code implements it. This module implements those statements -- *from the
document*, not by calling the solver -- and checks them against an exact
oracle on every instance small enough:

- `Sol_k(S)` (§1.3) is computed by memoised recursion over free-closed states;
  it shares no code with `satisfiability/`.
- **Node checks** (§2.0). At every free-closed state `S`, every `k`, and a
  family of old-move sets `Q` of genuinely refuted children, each filter
  configuration's output `L` must keep a child with a solution whenever any
  playable candidate had one (*node soundness*), every covering link `r -> c`
  it cites must satisfy `Sol_k(S.r) => Sol_k(S.c)` (*the rule's conclusion*),
  and every chain of links from a discarded candidate must end in `L` or `Q`
  (*the covering condition*, the certificate checker's step 5).
- **Tree checks** (§1.5, §2.6-§2.7). A port of the whole search -- free moves,
  memo, old move with inheritance, cost cut, the filter, the cost sort --
  is run at every `k` in every flag combination, and its answer compared with
  `Sol_k(root)`. Its node counts are compared with the C (`decide_native`),
  which is what shows that the port is the code and not a paraphrase.
- **Lemma F** (§1.4): `P_k(T) <=> Sol_k(cl T)` whenever `|O(T) - T| <= k`.

Instances are graphs given by self-inclusive neighbourhood masks (the search
reads nothing else, §1.1): every labelled graph on 1-6 vertices, every graph
on 7 vertices (networkx atlas) under the identity and random labellings, and
random sparse graphs at 8-16 vertices for the bad forms, which need more
customers (`reports/better_move_bug.md` §7).

The two known bad forms of `better_move` are variants of the filter:

- `old_close` -- Bug A, the close count also counts customers `r` finishes;
- `old_order` -- Bug B, better move first, then the subset rule citing every
  remaining customer, discarded ones included;
- `prefix`    -- both, the rule as it stood before 2026-09-26;
- `bm_first`  -- the measured-only candidate composition `BM_SUBSET_RESTRICTED`
  (better move first, then the subset rule excluding its discards); not claimed
  in §2.9, checked for information.

    python -m paper2.search_check            # full run, writes paper2/data/search_check.json
    python -m paper2.search_check --quick    # to 5 vertices, a few random instances
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

REPORT = Path(__file__).resolve().parent / "data" / "search_check.json"

VARIANTS = ("fixed", "old_close", "old_order", "prefix", "bm_first")
SOUND_VARIANTS = ("fixed",)          # the only one §2.9 claims


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


# ----------------------------------------------------------------------------
# instances
# ----------------------------------------------------------------------------


def masks_from_edges(n, edges):
    masks = [1 << v for v in range(n)]
    for u, v in edges:
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return masks


def masks_from_matrix(matrix):
    """Self-inclusive customer neighbourhoods of a 0/1 matrix; empty for a customer with no product."""
    n = len(matrix)
    masks = [0] * n
    for p in range(len(matrix[0]) if n else 0):
        holders = 0
        for c in range(n):
            if matrix[c][p]:
                holders |= 1 << c
        for c in bits(holders):
            masks[c] |= holders
    return masks


def matrix_from_masks(masks):
    """One product per edge, a private product for an isolated customer: same MOSP graph."""
    n = len(masks)
    cols = []
    for u in range(n):
        if masks[u] == 0:
            continue
        nb = masks[u] & ~(1 << u)
        if not nb:
            cols.append({u})
        for v in bits(nb):
            if v > u:
                cols.append({u, v})
    return [[1 if c in col else 0 for col in cols] for c in range(n)] if cols else [[0] for _ in range(n)]


def relabel(masks, perm):
    """`perm[v]` is the new label of `v`."""
    n = len(masks)
    out = [0] * n
    for v in range(n):
        m = 0
        for w in bits(masks[v]):
            m |= 1 << perm[w]
        out[perm[v]] = m
    return out


def labelled_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for code in range(1 << len(pairs)):
        yield masks_from_edges(n, [pairs[i] for i in range(len(pairs)) if code >> i & 1])


def atlas_graphs(n):
    import networkx as nx
    for g in nx.graph_atlas_g():
        if g.number_of_nodes() == n:
            yield masks_from_edges(n, list(g.edges()))


def random_sparse(n, rng):
    """A random graph at the sparse end, where the bad forms live: a few edges per vertex."""
    p = rng.choice((1.2, 1.5, 2.0, 2.5, 3.0)) / max(1, n - 1)
    edges = [(u, v) for u, v in itertools.combinations(range(n), 2) if rng.random() < p]
    return masks_from_edges(n, edges)


def random_cover(n, rng):
    """A random Chu & Stuckey-shaped matrix (products of 2-3 customers), as masks."""
    m = rng.randint(n // 2, 2 * n)
    matrix = [[0] * m for _ in range(n)]
    for p in range(m):
        for c in rng.sample(range(n), rng.choice((2, 2, 3))):
            matrix[c][p] = 1
    return masks_from_matrix(matrix)


# ----------------------------------------------------------------------------
# the model and the oracle (§1)
# ----------------------------------------------------------------------------


class Model:
    """`G` given by masks, and `k`. `Sol_k` and `P_k` are memoised and exact."""

    def __init__(self, masks, k):
        self.masks = masks
        self.n = len(masks)
        self.full = (1 << self.n) - 1
        self.k = k
        self._sol = {}
        self._plain = {}

    def opened(self, closed):
        o = 0
        for c in bits(closed):
            o |= self.masks[c]
        return o

    def cl(self, closed):
        """`fin(O(T))`, which contains `T`."""
        o = self.opened(closed)
        out = closed
        for c in bits(self.full & ~closed):
            if self.masks[c] & ~o == 0:
                out |= 1 << c
        return out

    def cost(self, closed, c):
        return (self.opened(closed | 1 << c) & ~closed).bit_count()

    def sol(self, state):
        """`Sol_k(S)` for a free-closed `S` (§1.3)."""
        hit = self._sol.get(state)
        if hit is not None:
            return hit
        if state == self.full:
            self._sol[state] = True
            return True
        o = self.opened(state)
        base = (o & ~state).bit_count()
        answer = False
        for c in bits(self.full & ~state):
            if base + (self.masks[c] & ~o).bit_count() <= self.k and self.sol(self.cl(state | 1 << c)):
                answer = True
                break
        self._sol[state] = answer
        return answer

    def plain(self, closed):
        """`P_k(T)`: some closing order from `T` of cost <= k, no free-closing."""
        hit = self._plain.get(closed)
        if hit is not None:
            return hit
        if closed == self.full:
            return True
        answer = any(self.cost(closed, c) <= self.k and self.plain(closed | 1 << c)
                     for c in bits(self.full & ~closed))
        self._plain[closed] = answer
        return answer

    def states(self):
        """Every free-closed set."""
        for s in range(self.full + 1):
            if self.cl(s) == s:
                yield s


# ----------------------------------------------------------------------------
# the filter, as §2.2-§2.5 state it
# ----------------------------------------------------------------------------


def definite_move(P, R, opens):
    """§2.2: the first q in index order with close(q, S) >= open(q, S), close counted over R(S)."""
    for _, q in P:
        own = opens[q]
        closed_by = sum(1 for d in R if opens[d] & ~own == 0)
        if closed_by >= own.bit_count():
            return q
    return None


def subset_pass(P, R, opens, exclude=0):
    """§2.3: r goes if some d in R(S) (not excluded), d != r, has o(d) ⊊ o(r), or o(d) = o(r) and d < r.

    Returns (kept, links); the fallback keeps P whole (and cites nothing) if everything would go."""
    kept, links = [], []
    for item in P:
        r = item[1]
        own = opens[r]
        cover = None
        for d in R:
            if d == r or exclude >> d & 1:
                continue
            other = opens[d]
            if other & ~own == 0 and (other != own or d < r):
                cover = d
                break
        if cover is None:
            kept.append(item)
        else:
            links.append((r, cover, "subset"))
    if not kept:
        return list(P), []
    return kept, links


def better_premise(masks, full, closed, opened, k, r, q, old_close=False):
    """§2.4 premises 3 and 4 (premise 2 is q in the input list)."""
    closed_r = closed | 1 << r
    opened_r = opened | masks[r]
    if ((opened_r | masks[q]) & ~closed_r).bit_count() > k:            # premise 3
        return False
    own = masks[q] & ~opened_r
    closed_by = 0
    for d in bits(full & ~closed_r):
        left = masks[d] & ~opened_r
        if (left or old_close) and left & ~own == 0:                   # premise 4
            closed_by += 1
    return closed_by >= own.bit_count()


def better_pass(P, masks, full, closed, opened, k, limit, old_close=False):
    """§2.4: over W = P in index order, r = w_i goes if some earlier w_j, j < L, meets the premise."""
    if len(P) <= 1:
        return list(P), []
    lim = len(P) if limit <= 0 or limit > len(P) else limit
    kept, links = [], []
    for ri, item in enumerate(P):
        r = item[1]
        cover = None
        for qi in range(min(lim, ri)):
            q = P[qi][1]
            if better_premise(masks, full, closed, opened, k, r, q, old_close):
                cover = q
                break
        if cover is None:
            kept.append(item)
        else:
            links.append((r, cover, "better"))
    return kept, links


def node_filter(masks, full, closed, Q, k, config):
    """One node of §1.5 steps 3-5: returns (P, L, links, R, opens).

    `config` has `definite`, `subset`, `better`, `limit`, `variant`, `old_move`."""
    opened = 0
    for c in bits(closed):
        opened |= masks[c]
    R = [c for c in bits(full & ~closed)]
    opens = {c: masks[c] & ~opened for c in R}
    open_now = (opened & ~closed).bit_count()
    K = [c for c in R if not (config["old_move"] and Q >> c & 1)]
    P = [(open_now + opens[c].bit_count(), c) for c in K if open_now + opens[c].bit_count() <= k]
    links = []
    if not P or not (config["definite"] or config["subset"] or config["better"]):
        return P, list(P), links, R, opens
    if config["definite"]:
        q = definite_move(P, R, opens)
        if q is not None:
            return P, [item for item in P if item[1] == q], [(r, q, "definite") for _, r in P if r != q], R, opens
    variant = config["variant"]
    old_close = variant in ("old_close", "prefix")
    L = list(P)
    if variant in ("old_order", "prefix"):
        if config["better"]:
            L, lk = better_pass(L, masks, full, closed, opened, k, config["limit"], old_close)
            links += lk
        if config["subset"]:
            L, lk = subset_pass(L, R, opens)
            links += lk
    elif variant == "bm_first":
        gone = 0
        if config["better"]:
            L, lk = better_pass(L, masks, full, closed, opened, k, config["limit"], old_close)
            links += lk
            for r, _, _ in lk:
                gone |= 1 << r
        if config["subset"]:
            L, lk = subset_pass(L, R, opens, exclude=gone)
            links += lk
    else:
        if config["subset"]:
            L, lk = subset_pass(L, R, opens)
            links += lk
        if config["better"]:
            L, lk = better_pass(L, masks, full, closed, opened, k, config["limit"], old_close)
            links += lk
    return P, L, links, R, opens


def chains_end_in(links, L, Q):
    """§2.0's covering condition: from every discarded candidate the cited links reach L or Q."""
    keep = {c for _, c in L}
    cover = {}
    for r, c, _ in links:
        cover.setdefault(r, c)        # a candidate discarded twice cites its first cover
    for start in cover:
        seen = set()
        x = start
        while x in cover and x not in keep:
            if x in seen:
                return False
            seen.add(x)
            x = cover[x]
        if not (x in keep or Q >> x & 1):
            return False
    return True


# ----------------------------------------------------------------------------
# the whole search (§1.5), ported from the statement
# ----------------------------------------------------------------------------


def inherit(masks, seen, closed, opened, c, k):
    """§2.6: q stays if cost(S ∪ {q}, c) <= k."""
    kept = 0
    for q in bits(seen):
        if ((opened | masks[q] | masks[c]) & ~(closed | 1 << q)).bit_count() <= k:
            kept |= 1 << q
    return kept


def search_decide(masks, k, config):
    """The search of §1.5 with the rules of §2. Returns (answer, nodes)."""
    n = len(masks)
    full = (1 << n) - 1
    memo = set()
    nodes = 0

    def search(closed, seen):
        nonlocal nodes
        opened = 0
        for c in bits(closed):
            opened |= masks[c]
        for c in bits(full & ~closed):                 # step 1, free moves
            if masks[c] & ~opened == 0:
                closed |= 1 << c
        if closed == full:
            return True
        if config["memo"] and closed in memo:          # step 2
            return False
        seen &= full & ~closed                         # step 3
        P, L, _, _, _ = node_filter(masks, full, closed, seen, k, config)
        L = sorted(L)                                  # step 6, cost then index
        for _, c in L:                                 # step 7
            nodes += 1
            inherited = inherit(masks, seen, closed, opened, c, k) if config["old_move"] and seen else 0
            if search(closed | 1 << c, inherited):
                return True
            seen |= 1 << c
        if config["memo"]:                             # step 8
            memo.add(closed)
        return False

    return search(0, 0), nodes


def native_decide(masks, k, config):
    """The C on the same graph, or None if the library is unavailable."""
    from mosp.instance import MOSPInstance
    from satisfiability.native import decide_native
    inst = MOSPInstance.from_matrix(matrix_from_masks(masks), name="search_check")
    d = decide_native(inst, k, subset_rule=config["subset"], definite_move=config["definite"],
                      old_move=config["old_move"], memo=config["memo"], better_move=config["better"],
                      better_move_dominators=config["limit"],
                      old_close_count=config["variant"] in ("old_close", "prefix"),
                      old_rule_order=config["variant"] in ("old_order", "prefix"),
                      subset_after_better_move=config["variant"] == "bm_first")
    if d is None:
        return None
    return d.status == "sat", d.nodes


# ----------------------------------------------------------------------------
# configurations
# ----------------------------------------------------------------------------


def filter_configs():
    """Every rule subset; better move with L in {0, 1, 2}; each better-move variant."""
    out = []
    for definite, subset, better in itertools.product((False, True), repeat=3):
        if not better:
            out.append(dict(definite=definite, subset=subset, better=False, limit=0, variant="fixed"))
            continue
        for limit in (0, 1, 2):
            for variant in VARIANTS:
                if variant in ("old_order", "prefix", "bm_first") and not subset:
                    continue          # the order is moot without the subset rule
                out.append(dict(definite=definite, subset=subset, better=True, limit=limit, variant=variant))
    return out


def search_configs():
    out = []
    for base in filter_configs():
        for old_move, memo in itertools.product((False, True), repeat=2):
            out.append(dict(base, old_move=old_move, memo=memo))
    return out


def config_name(c):
    rules = "+".join(r for r in ("definite", "subset", "better") if c[r]) or "none"
    name = rules
    if c["better"]:
        name += f"/L{c['limit']}/{c['variant']}"
    if "old_move" in c:
        name += "/old" if c["old_move"] else ""
        name += "/memo" if c["memo"] else ""
    return name


FILTERS = filter_configs()
SEARCHES = search_configs()


# ----------------------------------------------------------------------------
# the checks on one graph
# ----------------------------------------------------------------------------


def q_family(refuted, rng, cap=16):
    """Old-move sets to try: all subsets of the refuted children if few, else a sample."""
    xs = list(bits(refuted))
    if len(xs) <= 4:
        return [sum(1 << x for x in sub) for r in range(len(xs) + 1) for sub in itertools.combinations(xs, r)]
    fam = {0, refuted} | {1 << x for x in xs}
    while len(fam) < cap:
        fam.add(sum(1 << x for x in xs if rng.random() < 0.5))
    return sorted(fam)


def empty_tally():
    return {"node": Counter(), "node_fail": Counter(), "link": Counter(), "link_fail": Counter(), "pair": Counter(), "pair_fail": Counter(),
            "chain_fail": Counter(), "tree": Counter(), "tree_fail": Counter(),
            "native_mismatch": Counter(), "native": 0, "lemma_f": 0, "lemma_f_fail": 0,
            "states": 0, "examples": []}


def merge(a, b):
    for key, val in b.items():
        if isinstance(val, Counter):
            a[key].update(val)
        elif key == "examples":
            if len(a[key]) < 40:
                a[key].extend(val[:40 - len(a[key])])
        else:
            a[key] += val
    return a


def pair_checks(masks, full, S, k, model, child, t, example):
    """Each rule's premise => conclusion over *every* playable pair at S, not only the pairs cited.

    `definite`: Sol(S) => Sol(S.q) for every playable q meeting §2.2's premise.
    `subset`: Sol(S.r) => Sol(S.d) for every playable r and d in R(S) meeting §2.3's inclusion.
    `better/<form>`: Sol(S.r) => Sol(S.q) for every ordered playable pair meeting §2.4's
    premises 3-4 in the corrected form and in Bug A's (the measure of better_move_bug.md §7)."""
    opened = model.opened(S)
    R = list(bits(full & ~S))
    opens = {c: masks[c] & ~opened for c in R}
    open_now = (opened & ~S).bit_count()
    P = [c for c in R if open_now + opens[c].bit_count() <= k]
    here = model.sol(S)
    for q in P:
        own = opens[q]
        if sum(1 for d in R if opens[d] & ~own == 0) >= own.bit_count():
            t["pair"]["definite"] += 1
            if here and not child[q]:
                t["pair_fail"]["definite"] += 1
                example("pair", "definite", k=k, S=S, q=q)
    for r in P:
        own = opens[r]
        for d in R:
            if d != r and opens[d] & ~own == 0 and (opens[d] != own or d < r):
                t["pair"]["subset"] += 1
                if child[r] and not child[d]:
                    t["pair_fail"]["subset"] += 1
                    example("pair", "subset", k=k, S=S, r=r, d=d)
    for r in P:
        if not child[r]:
            continue                  # the conclusion holds vacuously; count applications only where it can fail
        for q in P:
            if q == r:
                continue
            for form, old in (("fixed", False), ("old_close", True)):
                if better_premise(masks, full, S, opened, k, r, q, old):
                    t["pair"][f"better/{form}"] += 1
                    if not child[q]:
                        t["pair_fail"][f"better/{form}"] += 1
                        example("pair", f"better/{form}", k=k, S=S, r=r, q=q)


def check_graph(masks, *, seed=0, node_checks=True, tree_checks=True, native=False,
                q_sets=True, ks=None, filters=None, searches=None, pairs=True):
    """Every check on one graph at every k. Returns a tally."""
    rng = random.Random(seed)
    n = len(masks)
    full = (1 << n) - 1
    t = empty_tally()
    filters = FILTERS if filters is None else filters
    searches = SEARCHES if searches is None else searches

    def example(kind, name, **extra):
        if len(t["examples"]) < 40:
            t["examples"].append(dict(kind=kind, config=name, masks=list(masks), **extra))

    for k in (range(0, n + 1) if ks is None else ks):
        model = Model(masks, k)
        # Lemma F
        for T in range(full + 1):
            if (model.opened(T) & ~T).bit_count() <= k:
                t["lemma_f"] += 1
                if model.plain(T) != model.sol(model.cl(T)):
                    t["lemma_f_fail"] += 1
                    example("lemma_f", "-", k=k, T=T)
        if node_checks:
            for S in model.states():
                if S == full:
                    continue
                t["states"] += 1
                child = {c: model.sol(model.cl(S | 1 << c)) for c in bits(full & ~S)}
                refuted = sum(1 << c for c, ok in child.items() if not ok)
                qs = q_family(refuted, rng) if q_sets else [0]
                for Q in qs:
                    for cfg in filters:
                        for old_move in ((False, True) if Q else (False,)):
                            c = dict(cfg, old_move=old_move)
                            name = config_name(cfg) + ("/Q" if old_move else "")
                            P, L, links, _, _ = node_filter(masks, full, S, Q, k, c)
                            if not P:
                                continue
                            t["node"][name] += 1
                            any_ok = any(child[x] for _, x in P)
                            kept_ok = any(child[x] for _, x in L)
                            if any_ok and not kept_ok:
                                t["node_fail"][name] += 1
                                example("node", name, k=k, S=S, Q=Q, P=[x for _, x in P], L=[x for _, x in L],
                                        links=links)
                            for r, cov, rule in links:
                                key = f"{rule}/{cfg['variant']}" if rule == "better" else rule
                                t["link"][key] += 1
                                if child[r] and not child[cov]:
                                    t["link_fail"][key] += 1
                                    example("link", key, k=k, S=S, r=r, cover=cov)
                            if links and not chains_end_in(links, L, Q if old_move else 0):
                                t["chain_fail"][name] += 1
                if pairs:
                    pair_checks(masks, full, S, k, model, child, t, example)
        if tree_checks:
            truth = model.sol(model.cl(0))
            for cfg in searches:
                name = config_name(cfg)
                answer, nodes = search_decide(masks, k, cfg)
                t["tree"][name] += 1
                if answer != truth:
                    t["tree_fail"][name] += 1
                    example("tree", name, k=k, truth=truth)
                if native:
                    got = native_decide(masks, k, cfg)
                    if got is not None:
                        t["native"] += 1
                        if got != (answer, nodes):
                            t["native_mismatch"][name] += 1
                            example("native", name, k=k, port=[answer, nodes], c=list(got))
    return t


# ----------------------------------------------------------------------------
# the sweeps
# ----------------------------------------------------------------------------


def _job(args):
    kind, payload, seed, opts = args
    return kind, check_graph(payload, seed=seed, **opts)


def jobs_small(max_n, atlas7_labellings, seed=0):
    rng = random.Random(seed)
    for n in range(1, max_n + 1):
        if n <= 6:
            for masks in labelled_graphs(n):
                yield ("labelled", masks, rng.randrange(1 << 30), dict(native=n <= 5))
        else:
            for masks in atlas_graphs(n):
                perms = [list(range(n))] + [rng.sample(range(n), n) for _ in range(atlas7_labellings)]
                for perm in perms:
                    yield ("atlas7", relabel(masks, perm), rng.randrange(1 << 30),
                           dict(native=perm == list(range(n)), q_sets=perm == list(range(n))))


BUG_FILTERS = [c for c in FILTERS if c["better"] and c["limit"] == 0]
BUG_SEARCHES = [dict(c, old_move=o, memo=m) for c in BUG_FILTERS for o, m in ((True, True), (False, False))]


def jobs_random(count, lo, hi, seed=1):
    rng = random.Random(seed)
    for i in range(count):
        n = rng.randint(lo, hi)
        masks = random_sparse(n, rng) if i % 2 else random_cover(n, rng)
        yield ("random", masks, rng.randrange(1 << 30),
               dict(q_sets=False, native=True, filters=BUG_FILTERS, searches=BUG_SEARCHES,
                    ks=range(max(1, n // 5), n)))


def pinned_instances():
    """The three counterexamples of `reports/better_move_bug.md` / `tests/test_differential.py`."""
    from tests.test_customer_search import MINIMAL_10x13, MINIMAL_17x9
    from tests.test_differential import DRAWN_10x20, DRAWN_OPTIMUM
    return {"minimal_10x13": (MINIMAL_10x13[0], MINIMAL_10x13[1]),
            "minimal_17x9": (MINIMAL_17x9[0], MINIMAL_17x9[1]),
            "drawn_10x20": (DRAWN_10x20, DRAWN_OPTIMUM)}


def check_pinned():
    """Every variant's answer at the optimum, port and C, on the pinned instances."""
    out = {}
    for name, (matrix, opt) in pinned_instances().items():
        masks = masks_from_matrix(matrix)
        truth = Model(masks, opt).sol(Model(masks, opt).cl(0))
        rows = {}
        for variant in VARIANTS:
            for definite, subset in ((True, True), (True, False), (False, True)):
                cfg = dict(definite=definite, subset=subset, better=True, limit=0, variant=variant,
                           old_move=True, memo=True)
                ans, nodes = search_decide(masks, opt, cfg)
                c = native_decide(masks, opt, cfg)
                rows[config_name(cfg)] = dict(port="sat" if ans else "unsat", nodes=nodes,
                                              c=None if c is None else ("sat" if c[0] else "unsat"),
                                              c_nodes=None if c is None else c[1])
        out[name] = dict(n=len(masks), optimum=opt, truth_at_optimum=truth, runs=rows)
    return out


def summarise(tallies):
    s = {}
    for kind, t in tallies.items():
        sound_node_fail = {k: v for k, v in t["node_fail"].items() if "/old_" not in k and "/prefix" not in k
                           and "/bm_first" not in k}
        s[kind] = {
            "states": t["states"], "node_checks": sum(t["node"].values()),
            "link_checks": sum(t["link"].values()), "tree_runs": sum(t["tree"].values()),
            "lemma_f": t["lemma_f"], "lemma_f_fail": t["lemma_f_fail"],
            "native_runs": t["native"], "native_mismatch": sum(t["native_mismatch"].values()),
            "node_fail": dict(t["node_fail"]), "link_fail": dict(t["link_fail"]),
            "link_by_rule": dict(t["link"]), "chain_fail": dict(t["chain_fail"]),
            "tree_fail": dict(t["tree_fail"]),
            "pair_by_rule": dict(t["pair"]), "pair_fail": dict(t["pair_fail"]),
            "fixed_rules_failures": sum(sound_node_fail.values())
            + sum(v for k, v in t["link_fail"].items() if k in ("definite", "subset", "better/fixed"))
            + sum(v for k, v in t["pair_fail"].items() if k in ("definite", "subset", "better/fixed"))
            + sum(v for k, v in t["tree_fail"].items() if "/old_" not in k and "/prefix" not in k
                  and "/bm_first" not in k),
        }
    return s


def run(quick=False, workers=None, out=REPORT, n_random=None):
    started = time.time()
    max_n = 5 if quick else 7
    atlas7 = 0 if quick else 24
    n_random = (40 if quick else 6000) if n_random is None else n_random
    tallies = {}
    work = list(jobs_small(max_n, atlas7)) + list(jobs_random(n_random, 8, 11 if quick else 16))
    work += [("pinned", masks_from_matrix(matrix), 0,
              dict(q_sets=False, native=True, filters=BUG_FILTERS, searches=BUG_SEARCHES))
             for matrix, _ in pinned_instances().values()]
    with Pool(workers) as pool:
        for kind, t in pool.imap_unordered(_job, work, chunksize=8):
            if kind not in tallies:
                tallies[kind] = empty_tally()
            merge(tallies[kind], t)
    report = {
        "seconds": round(time.time() - started, 1),
        "quick": quick,
        "graphs": dict(Counter(kind for kind, *_ in work)),
        "summary": summarise(tallies),
        "pinned": check_pinned(),
        "examples": {kind: t["examples"][:20] for kind, t in tallies.items()},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, default=str))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--random", type=int, default=None, help="random instances at 8-16 vertices")
    args = ap.parse_args()
    report = run(quick=args.quick, workers=args.workers, n_random=args.random)
    print(json.dumps({"seconds": report["seconds"], "graphs": report["graphs"],
                      "summary": report["summary"],
                      "pinned": {k: {c: r for c, r in v["runs"].items()}
                                 for k, v in report["pinned"].items()}}, indent=1))


if __name__ == "__main__":
    main()
