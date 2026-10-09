"""Brute-force soundness check of the customer search's pruning rules (loop0006 item 06).

`paper1/search_soundness.md` §1-2 (item 05) states Chu & Stuckey's customer
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

    python -m paper1.search_check            # full run, writes paper1/data/search_check.json
    python -m paper1.search_check --quick    # to 5 vertices, a few random instances
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
                      subset_after_better_move=config["variant"] == "bm_first",
                      # the published rules, which this port models; the
                      # repaired ones are the default since 2026-10-01
                      repaired_rules=False)
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


# ----------------------------------------------------------------------------
# item 07: the Lean model of `Search/Basic.lean`, checked before it was stated
# ----------------------------------------------------------------------------
#
# These functions transcribe the Lean definitions literally, on *arbitrary*
# sets of closed customers (not only free-closed states): `opened`, `cl`,
# `stepCost`, `orderCost` (the maximum step cost along a list), `Solvable`
# (some ordering of V \ T after T has cost <= k) and `SearchSol` (the
# inductive predicate: T = V, or a playable c whose child cl(T + c) satisfies
# it). Kornai & Tuza's out-sequence shack is transcribed from
# `Complex/Narrowness.lean` (`EnteredBy`, `outShackBeforeMove`), and the
# layout's vertex separation from `VertexSeparation.lean` (`activeSuffix`).


def m_opened(masks, T):
    o = 0
    for c in bits(T):
        o |= masks[c]
    return o


def m_cl(masks, T):
    o = m_opened(masks, T)
    return sum(1 << c for c in range(len(masks)) if masks[c] & ~o == 0)


def m_step_cost(masks, T, c):
    return (m_opened(masks, T | 1 << c) & ~T).bit_count()


def m_order_cost(masks, T, order):
    cost = 0
    for c in order:
        cost = max(cost, m_step_cost(masks, T, c))
        T |= 1 << c
    return cost


def m_solvable_table(masks, k):
    """`Solvable k T` for every T, by the recursion prepend/first-move (Lean
    `solvable_of_solvable_insert`, `exists_first_move`)."""
    n = len(masks)
    full = (1 << n) - 1
    P = [False] * (1 << n)
    for T in range(full, -1, -1):
        P[T] = T == full or any(P[T | 1 << c] for c in range(n)
                                if not T >> c & 1 and m_step_cost(masks, T, c) <= k)
    return P


def m_searchsol_table(masks, k):
    """`SearchSol k T` for every T: the inductive definition, whose children are cl(T + c)."""
    n = len(masks)
    full = (1 << n) - 1
    S = [False] * (1 << n)
    for T in range(full, -1, -1):   # cl(T + c) is a strict superset of T
        S[T] = T == full or any(S[m_cl(masks, T | 1 << c)] for c in range(n)
                                if not T >> c & 1 and m_step_cost(masks, T, c) <= k)
    return S


def m_out_narrowness(masks, tau):
    """`outNarrowness`: max over i of |{v : EnteredBy tau i v and i <= tau v}|; tau[v] is v's position."""
    n = len(masks)
    best = 0
    for i in range(n):
        shack = sum(1 for v in range(n)
                    if tau[v] >= i and any(tau[u] <= i for u in bits(masks[v])))
        best = max(best, shack)
    return best


def m_vs_of_layout(masks, tau):
    """`vertexSepOfLayout`: max over i < n of the suffix vertices (tau >= i) adjacent to the prefix."""
    n = len(masks)
    if n == 0:
        return 0
    return max(sum(1 for v in range(n) if tau[v] >= i
                   and any(tau[u] < i for u in bits(masks[v] & ~(1 << v))))
               for i in range(n))


def check_model_graph(masks, *, perms=None, pairs=True, seed=0):
    """Every statement of `Search/Basic.lean` on one graph; returns a tally of checks and failures."""
    n = len(masks)
    full = (1 << n) - 1
    t = Counter()
    rng = random.Random(seed)
    # a full closing order's cost = outNarrowness = vs + 1 (orderCost_ofFn_eq_*)
    all_perms = itertools.permutations(range(n)) if perms is None else (
        rng.sample(range(n), n) for _ in range(perms))
    costs = []
    for order in all_perms:
        tau = [0] * n
        for pos, v in enumerate(order):
            tau[v] = pos
        c = m_order_cost(masks, 0, order)
        costs.append(c)
        t["layouts"] += 1
        if c != m_out_narrowness(masks, tau):
            t["fail_outNarrowness"] += 1
        if n and c != m_vs_of_layout(masks, tau) + 1:
            t["fail_vs_plus_one"] += 1
    if m_cl(masks, 0) != 0:
        t["fail_cl_empty"] += 1
    opened = [m_opened(masks, T) for T in range(full + 1)]
    for T in range(full + 1):
        if m_opened(masks, m_cl(masks, T)) != opened[T] or T & ~m_cl(masks, T):
            t["fail_opened_cl"] += 1
    for k in range(n + 2):
        P = m_solvable_table(masks, k)
        S = m_searchsol_table(masks, k)
        if perms is None and P[0] != (min(costs) <= k):
            t["fail_root_min_cost"] += 1
        if P[0] != S[0]:
            t["fail_root"] += 1
        for T in range(full + 1):
            inv = (opened[T] & ~T).bit_count() <= k
            clT = m_cl(masks, T)
            t["lemma_f"] += 1
            if P[T] and not S[clT]:                  # searchSol_cl_of_solvable
                t["fail_lemma_f_forward"] += 1
            if inv and S[clT] != P[T]:               # solvable_iff_searchSol_cl
                t["fail_lemma_f"] += 1
            if not inv and S[clT] and not P[T]:
                t["lemma_f_needs_invariant"] += 1   # the hypothesis is not decorative
            if S[T] and inv and not P[T]:           # solvable_of_searchSol
                t["fail_solvable_of_searchSol"] += 1
            if P[T] and not P[clT]:                  # solvable_cl
                t["fail_solvable_cl"] += 1
            for c in range(n):
                if T >> c & 1 or masks[c] & ~opened[T]:
                    continue
                t["free_moves"] += 1                 # solvable_insert_of_free, _iff_of_free
                if P[T] and not P[T | 1 << c]:
                    t["fail_free_move"] += 1
                if inv and P[T | 1 << c] != P[T]:
                    t["fail_free_move_iff"] += 1
                if not inv and P[T | 1 << c] and not P[T]:
                    t["free_move_iff_needs_invariant"] += 1
            if pairs:                                # solvable_mono, over all T <= T'
                sub = full & ~T
                Tp = sub
                while True:
                    T2 = T | Tp
                    if opened[T2] & ~opened[T] == 0:
                        t["mono_pairs"] += 1
                        if P[T] and not P[T2]:
                            t["fail_mono"] += 1
                    if Tp == 0:
                        break
                    Tp = (Tp - 1) & sub
    return t


def _model_job(args):
    masks, perms, pairs = args
    return check_model_graph(masks, perms=perms, pairs=pairs)


def run_model(workers=None, out=None, quick=False):
    """Item 07's check: every labelled graph on 0-6 vertices and every atlas graph on 7, each
    with every layout and every monotonicity pair (`quick`: labelled graphs to 4 only)."""
    started = time.time()
    work = [(m, None, True) for n in range((4 if quick else 6) + 1) for m in labelled_graphs(n)]
    if not quick:
        work += [(m, None, True) for m in atlas_graphs(7)]
    total = Counter()
    with Pool(workers) as pool:
        for t in pool.imap_unordered(_model_job, work, chunksize=16):
            total.update(t)
    report = {"seconds": round(time.time() - started, 1), "graphs": len(work),
              "quick": quick, "tally": dict(total),
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))}
    out = out or REPORT.parent / "search_model_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report


# ----------------------------------------------------------------------------
# item 08: the definite move (Search/DefiniteMove.lean)
# ----------------------------------------------------------------------------
#
# Transcribes `Search/DefiniteMove.lean`: openStacks b(T) = |O(T) - T|, o(c, S),
# open/close counts as the code counts them, the code's premise, the repaired
# (hereditary) premise and its matching form. The conclusion checked is the
# rule's own: P_k(S) => P_k(cl(S + q)).

# Two counterexamples to Chu & Stuckey's Theorem 1 in the code's form, each with
# (masks, S, q, k). The first is `cexGraph` of the Lean file (14 customers, found by
# random search at 10-16 customers and minimised by vertex/edge deletion); the
# second is the first one found (16 customers).
DEFINITE_CEX = [
    ([2201, 102, 30, 13, 21, 6690, 8514, 9857, 3904, 4000, 16256, 3873, 13344, 13504], 0b100, 0, 6),
    ([18459, 103, 286, 13, 21, 60578, 8770, 60320, 7044, 20416, 7712, 44961, 13568, 30944,
      58017, 51360], 0b100, 0, 7),
]


def d_opened_table(masks):
    n = len(masks)
    O = [0] * (1 << n)
    for T in range(1, 1 << n):
        low = T & -T
        O[T] = O[T ^ low] | masks[low.bit_length() - 1]
    return O


def d_solvable_table(masks, k, O):
    """`Solvable k T` for every T (as `m_solvable_table`, with the opened sets precomputed)."""
    n = len(masks)
    full = (1 << n) - 1
    P = [False] * (1 << n)
    P[full] = True
    for T in range(full - 1, -1, -1):
        rem = full & ~T
        while rem:
            low = rem & -rem
            rem ^= low
            if (O[T | low] & ~T).bit_count() <= k and P[T | low]:
                P[T] = True
                break
    return P


def d_open_stacks(O, T):
    return (O[T] & ~T).bit_count()


def d_counts(masks, O, S, q):
    """(open(q, S), close(q, S)) as the code counts them over the customers not in S."""
    n = len(masks)
    OS = O[S]
    own = masks[q] & ~OS
    close = sum(1 for d in range(n) if not S >> d & 1 and (masks[d] & ~OS) & ~own == 0)
    return own.bit_count(), close


def d_child(masks, O, S, q):
    U = O[S | 1 << q]
    return sum(1 << c for c in range(len(masks)) if masks[c] & ~U == 0)


def d_hereditary(masks, O, S, q):
    """`IsHereditarilyDefinite`: b(X) <= b(B) for S <= B <= X, q not in B."""
    X = d_child(masks, O, S, q)
    bX = d_open_stacks(O, X)
    D = X & ~S & ~(1 << q)
    E = D
    while True:
        if d_open_stacks(O, S | E) < bX:
            return False
        if E == 0:
            return True
        E = (E - 1) & D


def d_matching_size(masks, O, S, q):
    """Maximum matching of the customers X - S - {q} to distinct stacks y in o(d, S)."""
    X = d_child(masks, O, S, q)
    OS = O[S]
    match = {}

    def augment(d, seen):
        for y in bits(masks[d] & ~OS):
            if y in seen:
                continue
            seen.add(y)
            if y not in match or augment(match[y], seen):
                match[y] = d
                return True
        return False

    return sum(1 for d in bits(X & ~S & ~(1 << q)) if augment(d, set()))


def check_definite_graph(masks, ks=None, first_only=False):
    """Every statement of `Search/DefiniteMove.lean` on one graph, at every free-closed S with
    the node invariant, every k and every q not in S."""
    n = len(masks)
    full = (1 << n) - 1
    O = d_opened_table(masks)
    t = Counter()
    # submodularity of b over all pairs is quadratic in 2^n: all pairs to 5 customers, else a sample
    rng = random.Random(len(masks) * 7919 + sum(masks))
    pairs = ((A, B) for A in range(full + 1) for B in range(full + 1)) if n <= 5 else (
        (rng.randrange(full + 1), rng.randrange(full + 1)) for _ in range(2000))
    for A, B in pairs:
        t["submodular_pairs"] += 1
        if (d_open_stacks(O, A | B) + d_open_stacks(O, A & B)
                > d_open_stacks(O, A) + d_open_stacks(O, B)):
            t["fail_submodular"] += 1
    fc = [S for S in range(full) if sum(1 << c for c in range(n) if masks[c] & ~O[S] == 0) == S]
    for k in (range(1, n + 1) if ks is None else ks):
        P = d_solvable_table(masks, k, O)
        for S in fc:
            if d_open_stacks(O, S) > k:
                continue
            for q in range(n):
                if S >> q & 1:
                    continue
                X = d_child(masks, O, S, q)
                op, cl_ = d_counts(masks, O, S, q)
                code = op <= cl_
                # isDefinite_iff
                t["definite_iff"] += 1
                if code != (d_open_stacks(O, X) <= d_open_stacks(O, S)):
                    t["fail_definite_iff"] += 1
                if cl_ != (X & ~S).bit_count():
                    t["fail_closeCount_eq"] += 1
                her = d_hereditary(masks, O, S, q)
                mat = d_matching_size(masks, O, S, q) >= op - 1
                t["hereditary_vs_matching"] += 1
                if her != mat:                         # Hall with deficiency (not in Lean)
                    t["fail_matching_iff_hereditary"] += 1
                if her and not code:                   # IsHereditarilyDefinite.isDefinite
                    t["fail_hereditary_implies_code"] += 1
                if op <= 1 and not her:                # isHereditarilyDefinite_of_openCount_le_one
                    t["fail_open_le_one"] += 1
                if her:
                    t["hereditary_moves"] += 1         # solvable_cl_insert_of_hereditarilyDefinite
                    if P[S] and not P[X]:
                        t["fail_hereditary_sound"] += 1
                playable = (O[S | 1 << q] & ~S).bit_count() <= k
                if code and playable:
                    t["code_moves"] += 1               # the code's rule: the finding
                    if not her:
                        t["code_not_hereditary"] += 1
                    if P[S] and not P[X]:
                        t["code_loses_last_solution"] += 1
                    if first_only:
                        break
    return t


def definite_cex_report():
    """The pinned counterexamples, with what the port of the code keeps at the node."""
    out = []
    for masks, S, q, k in DEFINITE_CEX:
        n = len(masks)
        O = d_opened_table(masks)
        P = d_solvable_table(masks, k, O)
        X = d_child(masks, O, S, q)
        cfg = {"definite": True, "subset": True, "better": True, "limit": 0, "variant": "fixed",
               "old_move": False}
        _, L, _, _, _ = node_filter(masks, (1 << n) - 1, S, 0, k, cfg)
        opt = next(kk for kk in range(1, n + 1) if d_solvable_table(masks, kk, O)[0])
        op, cl_ = d_counts(masks, O, S, q)
        out.append({"n": n, "S": list(bits(S)), "q": q, "k": k, "open": op, "close": cl_,
                    "playable": (O[S | 1 << q] & ~S).bit_count() <= k,
                    "node_keeps": [c for _, c in L], "child": list(bits(X)),
                    "P_S": P[S], "P_child": P[X], "hereditary": d_hereditary(masks, O, S, q),
                    "optimum": opt, "decide_at_optimum": search_decide(masks, opt, dict(cfg, memo=True, old_move=True))[0]})
    return out


def _definite_job(args):
    masks, first_only = args
    return check_definite_graph(masks, first_only=first_only)


def run_definite(workers=None, out=None, quick=False, n_random=None):
    """Item 08's check: every labelled graph on 1-6 vertices and every atlas graph on 7, plus
    random graphs at 10-13 from `jobs_random`'s families, plus the pinned counterexamples."""
    started = time.time()
    work = [(m, False) for n in range(1, (4 if quick else 6) + 1) for m in labelled_graphs(n)]
    if not quick:
        work += [(m, False) for m in atlas_graphs(7)]
    rng = random.Random(8)
    count = (20 if quick else 2000) if n_random is None else n_random
    for _ in range(count):
        n = rng.randint(10, 11 if quick else 13)
        work.append(((random_sparse if rng.random() < 0.5 else random_cover)(n, rng), False))
    total = Counter()
    with Pool(workers) as pool:
        for t in pool.imap_unordered(_definite_job, work, chunksize=8):
            total.update(t)
    cex = definite_cex_report()
    cex_tallies = [dict(check_definite_graph(m, ks=[k])) for m, _, _, k in DEFINITE_CEX] if not quick else []
    report = {"seconds": round(time.time() - started, 1), "graphs": len(work), "quick": quick,
              "tally": dict(total), "pinned": cex, "pinned_tallies": cex_tallies,
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))}
    out = out or REPORT.parent / "search_definite_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report

# ----------------------------------------------------------------------------
# item 09: the subset rule (Search/SubsetRule.lean)
# ----------------------------------------------------------------------------
#
# Transcribes `Search/SubsetRule.lean`: `Dominates S d r` (o(d, S) ⊆ o(r, S), d != r, and
# the inclusion strict or d < r), the subset filter over the playable candidates with its
# all-dominated fallback, and the composition `definite -> subset` for a premise D (the
# code's `open <= close`, or the repair). The conclusions checked are the Lean ones, on
# `SearchSol` computed by its inductive clauses.


# The subset rule without its index tie-break loses the last solution on this 7-customer
# graph (`noTieBreak_counterexample`, `tieGraph` of the Lean file): (masks, S, k); at S = {2}
# the twins 0 and 3 both go and only the refuted 5 is kept.
SUBSET_TIE_CEX = ([77, 82, 5, 73, 114, 48, 91], 0b100, 3)


def s_weak_dominated(masks, O, S, r):
    """Without the tie-break: some d outside S, d != r, with o(d, S) ⊆ o(r, S)."""
    b = masks[r] & ~O[S]
    return any(d != r and (masks[d] & ~O[S]) & ~b == 0 for d in range(len(masks)) if not S >> d & 1)


def s_paper_dominated(masks, O, S, r):
    """The paper's literal form (PDF p. 5): some d < r outside S with o(d, S) ⊆ o(r, S)."""
    b = masks[r] & ~O[S]
    return any((masks[d] & ~O[S]) & ~b == 0 for d in range(r) if not S >> d & 1)


def s_filter_by(pred, masks, O, S, P):
    kept = [r for r in P if not pred(masks, O, S, r)]
    return kept or list(P)


def s_tables(masks):
    n = len(masks)
    O = d_opened_table(masks)
    CL = [0] * (1 << n)
    for T in range(1 << n):
        o = O[T]
        CL[T] = sum(1 << c for c in range(n) if masks[c] & ~o == 0)
    return O, CL


def s_searchsol_table(masks, k, O, CL):
    """`SearchSol k T` for every T (as `m_searchsol_table`, with O and cl precomputed)."""
    n = len(masks)
    full = (1 << n) - 1
    S = [False] * (1 << n)
    for T in range(full, -1, -1):
        if T == full:
            S[T] = True
            continue
        rem = full & ~T
        while rem:
            low = rem & -rem
            rem ^= low
            if (O[T | low] & ~T).bit_count() <= k and S[CL[T | low]]:
                S[T] = True
                break
    return S


def s_dominates(masks, O, S, d, r):
    """`Dominates G S d r`."""
    a, b = masks[d] & ~O[S], masks[r] & ~O[S]
    return d != r and a & ~b == 0 and (a != b or d < r)


def s_dominated(masks, O, S, r):
    """`IsSubsetDominated G S r`: some d outside S dominates r."""
    return any(s_dominates(masks, O, S, d, r) for d in range(len(masks)) if not S >> d & 1)


def s_playable(masks, O, S, k, K):
    return [c for c in K if (O[S | 1 << c] & ~S).bit_count() <= k]


def s_subset_filter(masks, O, S, P):
    """`subsetFilter G S P`: the undominated members of P, or P itself if there are none."""
    kept = [r for r in P if not s_dominated(masks, O, S, r)]
    return kept or list(P)


def s_composed(masks, O, S, P, D):
    """`definiteThenSubset`: the least q in P meeting D alone, else the subset filter."""
    F = [q for q in P if D(q)]
    return [min(F)] if F else s_subset_filter(masks, O, S, P)


def check_subset_graph(masks, ks=None, all_sets=True, seed=0):
    """Every statement of `Search/SubsetRule.lean` on one graph. Pair and dominator statements
    at every set T (`all_sets`) or at the free-closed states with the invariant; node
    statements at every free-closed state with the invariant and a solution, over families
    of genuinely refuted old moves Q."""
    n = len(masks)
    full = (1 << n) - 1
    O, CL = s_tables(masks)
    t = Counter()
    rng = random.Random(seed * 7919 + sum(masks))
    fc = [S for S in range(full + 1) if CL[S] == S]
    for k in (range(0, n + 1) if ks is None else ks):
        SS = s_searchsol_table(masks, k, O, CL)
        sets = range(full + 1) if all_sets else [S for S in fc if (O[S] & ~S).bit_count() <= k]
        for T in sets:
            outside = [c for c in range(n) if not T >> c & 1]
            for r in range(n):
                nr = masks[r] & ~O[T]
                cost_r = (O[T | 1 << r] & ~T).bit_count()
                for d in range(n):
                    nd = masks[d] & ~O[T]
                    if nd & ~nr:
                        continue
                    t["subset_pairs"] += 1
                    if not CL[T | 1 << r] >> d & 1:                     # mem_cl_insert_of_...
                        t["fail_mem_cl_insert"] += 1
                    if CL[T | 1 << d] & ~CL[T | 1 << r]:               # cl_insert_subset_of_...
                        t["fail_cl_insert_subset"] += 1
                    if (O[T | 1 << d] & ~T).bit_count() > cost_r:     # stepCost_le_of_...
                        t["fail_stepCost_le"] += 1
                    if cost_r <= k and SS[CL[T | 1 << r]]:            # searchSol_cl_insert_of_...
                        t["covering_premises"] += 1
                        if not SS[CL[T | 1 << d]]:
                            t["fail_covering"] += 1
            if n <= 6 and all_sets:                                    # Dominates is a strict order
                for a in outside:
                    if s_dominates(masks, O, T, a, a):
                        t["fail_irrefl"] += 1
                    for b in outside:
                        if not s_dominates(masks, O, T, a, b):
                            continue
                        for c in outside:
                            t["trans_triples"] += 1
                            if s_dominates(masks, O, T, b, c) and not s_dominates(masks, O, T, a, c):
                                t["fail_trans"] += 1
            for r in outside:                                          # exists_undominated
                t["undominated_queries"] += 1
                nr = masks[r] & ~O[T]
                if not any(not s_dominated(masks, O, T, m) and (masks[m] & ~O[T]) & ~nr == 0
                           for m in outside):
                    t["fail_exists_undominated"] += 1
        for S in fc:
            if S == full or (O[S] & ~S).bit_count() > k:
                continue
            R = [c for c in range(n) if not S >> c & 1]
            # the Lean filter is the item 06 port of the code, at every Q = 0 node
            P0 = s_playable(masks, O, S, k, R)
            for cfg_def in (False, True):
                cfg = {"definite": cfg_def, "subset": True, "better": False, "limit": 0,
                       "variant": "fixed", "old_move": False}
                _, L, _, _, _ = node_filter(masks, full, S, 0, k, cfg)
                code = (lambda q: (lambda op_cl: op_cl[0] <= op_cl[1])(d_counts(masks, O, S, q)))
                mine = (s_composed(masks, O, S, P0, code) if cfg_def
                        else s_subset_filter(masks, O, S, P0))
                t["port_nodes"] += 1
                if sorted(c for _, c in L) != sorted(mine):
                    t["fail_port"] += 1
            if not SS[S]:
                continue
            refuted = sum(1 << c for c in R if not SS[CL[S | 1 << c]])
            her = {q: d_hereditary(masks, O, S, q) for q in R}
            code_def = {q: d_counts(masks, O, S, q)[0] <= d_counts(masks, O, S, q)[1] for q in R}
            for Q in q_family(refuted, rng):
                P = s_playable(masks, O, S, k, [c for c in R if not Q >> c & 1])
                t["nodes"] += 1
                kept = [r for r in P if not s_dominated(masks, O, S, r)]
                if not kept:                                           # subsetKept_nonempty
                    t["fail_kept_nonempty"] += 1
                L = s_subset_filter(masks, O, S, P)
                if not any(SS[CL[S | 1 << c]] for c in L):             # subsetFilter_sound
                    t["fail_subset_node"] += 1
                L = s_composed(masks, O, S, P, lambda q: her[q])
                if not any(SS[CL[S | 1 << c]] for c in L):             # repaired composition
                    t["fail_repaired_node"] += 1
                L = s_filter_by(s_paper_dominated, masks, O, S, P)
                if not any(SS[CL[S | 1 << c]] for c in L):             # the paper's own form
                    t["fail_paper_node"] += 1
                L = s_filter_by(s_weak_dominated, masks, O, S, P)
                if not any(SS[CL[S | 1 << c]] for c in L):             # no tie-break: unsound
                    t["weak_loses"] += 1
                L = s_composed(masks, O, S, P, lambda q: code_def[q])
                if not any(SS[CL[S | 1 << c]] for c in L):             # the code's composition
                    t["code_composition_loses"] += 1
    return t


def _subset_job(args):
    masks, all_sets = args
    return check_subset_graph(masks, all_sets=all_sets)


def _subset_gadget_job(args):
    seed, count, lo, hi = args
    rng = random.Random(seed)
    t = Counter()
    for _ in range(count):
        masks = subset_gadget(rng.randint(lo, hi), rng)
        O, CL = s_tables(masks)
        opt = next(k for k in range(len(masks) + 1) if s_searchsol_table(masks, k, O, CL)[0])
        t.update(check_subset_graph(masks, ks=[max(0, opt - 1), opt, opt + 1], all_sets=False,
                                    seed=seed))
    return t


def subset_gadget(n, rng):
    """The definite move's gadget (family 4 of `definite_hunt_gen.py`) with a twist for the
    subset rule: a closed s whose open neighbours d_i share one new stack y with r, so that
    closing r finishes them together, plus a random rest."""
    E = set()
    r_ = rng.randint(2, 3)
    t_ = rng.randint(1, r_)
    rest = n - (3 + r_ + t_)
    if rest < 1:
        return random_sparse(n, rng)
    s, q, y = 0, 1, 2
    ds = list(range(3, 3 + r_))
    zs = list(range(3 + r_, 3 + r_ + t_))
    R = list(range(3 + r_ + t_, n))
    E |= {(s, q)} | {(s, d) for d in ds} | {(d, y) for d in ds} | {(q, y)} | {(q, z) for z in zs}
    for z in zs:
        for w in rng.sample(R, rng.randint(1, len(R))):
            E.add((z, w))
    E.add((y, rng.choice(R)))
    p = rng.uniform(0.15, 0.5)
    E |= {(u, v) for u in R for v in R if u < v and rng.random() < p}
    perm = list(range(n))
    rng.shuffle(perm)                      # the index tie-break must not see the construction
    return masks_from_edges(n, [(perm[u], perm[v]) for u, v in E if u != v])


def run_subset(workers=None, out=None, quick=False, n_random=None):
    """Item 09's check: every labelled graph on 1-6 vertices at every set T, every atlas graph on
    7 at the search's states, random sparse and cover graphs at 10-13 and gadget graphs at
    12-16 at the search's states, and the pinned definite-move counterexamples."""
    started = time.time()
    work = [(m, True) for n in range(1, (4 if quick else 6) + 1) for m in labelled_graphs(n)]
    if not quick:
        work += [(m, False) for m in atlas_graphs(7)]
    rng = random.Random(9)
    count = (10 if quick else 1500) if n_random is None else n_random
    for _ in range(count):
        n = rng.randint(10, 11 if quick else 13)
        work.append(((random_sparse if rng.random() < 0.5 else random_cover)(n, rng), False))
    total = Counter()
    gadget = [] if quick else [(1000 + i, 5, 12, 16) for i in range(400)]
    with Pool(workers) as pool:
        for t in pool.imap_unordered(_subset_job, work, chunksize=8):
            total.update(t)
        for t in pool.imap_unordered(_subset_gadget_job, gadget):
            total.update(t)
    pinned = [dict(check_subset_graph(m, ks=[k], all_sets=False)) for m, _, _, k in DEFINITE_CEX]
    pinned.append(dict(check_subset_graph(SUBSET_TIE_CEX[0], ks=[SUBSET_TIE_CEX[2]], all_sets=False)))
    report = {"seconds": round(time.time() - started, 1), "graphs": len(work),
              "gadget_graphs": sum(c for _, c, _, _ in gadget), "quick": quick,
              "tally": dict(total), "pinned_tallies": pinned,
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))
              + sum(v for p in pinned for k, v in p.items() if k.startswith("fail_"))}
    out = out or REPORT.parent / "search_subset_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report


# ----------------------------------------------------------------------------
# item 10: Search/BetterMove.lean
# ----------------------------------------------------------------------------

# (masks, S, r, q, k) of `betterMove_counterexample`: `cexGraph` at the root, the code drops 2
# citing 0, and a solution exists after 2 but not after 0.
BETTER_CEX = (DEFINITE_CEX[0][0], 0, 2, 0, 6)
# `bugA_counterexample`: the old close count's premise holds, the corrected one does not.
BUG_A_CEX = ([3375, 1051, 1165, 15, 18, 289, 704, 1732, 3361, 704, 3463, 3329], 0, 6, 4, 4)
# `bugB_counterexample`: (masks, S, k); the old order keeps {6}, the fixed order {3, 6}.
BUG_B_CEX = ([139, 59, 12, 15, 178, 242, 224, 241], 0b100, 4)


def b_is_better(masks, O, S, k, r, q, old=False):
    """`IsBetter` (or `IsBetterOld`): premise 3 and open' <= close' after S + r."""
    Sr = S | 1 << r
    Or = O[Sr]
    if (O[Sr | 1 << q] & ~Sr).bit_count() > k:
        return False
    own = masks[q] & ~Or
    close = 0
    for d in range(len(masks)):
        if Sr >> d & 1:
            continue
        left = masks[d] & ~Or
        if (left or old) and left & ~own == 0:
            close += 1
    return own.bit_count() <= close


def b_is_repaired(masks, O, CL, S, k, r, q):
    """`IsRepairedBetter`: premise 3 and q hereditarily definite at cl(S + r)."""
    Sr = S | 1 << r
    return (O[Sr | 1 << q] & ~Sr).bit_count() <= k and d_hereditary(masks, O, CL[Sr], q)


def b_within(L, W, q):
    return L == 0 or sum(1 for w in W if w < q) < L


def b_better_filter(W, cite):
    """`betterFilterBy`: r goes if an earlier q in W is cited."""
    return [r for r in W if not any(q < r and cite(W, r, q) for q in W)]


def b_full(masks, O, S, P, D, cite):
    """`fullFilter`: definite -> subset -> better."""
    F = [q for q in P if D(q)]
    if F:
        return [min(F)]
    return b_better_filter(s_subset_filter(masks, O, S, P), cite)


def b_old_order(masks, O, S, P, D, cite):
    """`oldOrderFilter`: definite, else the better move over P, then the subset rule."""
    F = [q for q in P if D(q)]
    if F:
        return [min(F)]
    return s_subset_filter(masks, O, S, b_better_filter(P, cite))


def check_better_graph(masks, ks=None, all_sets=False, seed=0, limits=(0, 1, 2)):
    """Every statement of `Search/BetterMove.lean` on one graph: pair statements at every set
    (`all_sets`) or at the free-closed states with the invariant; node statements at the
    free-closed states with the invariant and a solution, over families of refuted old moves."""
    n = len(masks)
    full = (1 << n) - 1
    O, CL = s_tables(masks)
    t = Counter()
    rng = random.Random(seed * 104729 + sum(masks))
    fc = [S for S in range(full + 1) if CL[S] == S]
    for k in (range(0, n + 1) if ks is None else ks):
        SS = s_searchsol_table(masks, k, O, CL)
        sets = range(full + 1) if all_sets else [S for S in fc if (O[S] & ~S).bit_count() <= k]
        for T in sets:
            outside = [c for c in range(n) if not T >> c & 1]
            for r in outside:
                cost_r = (O[T | 1 << r] & ~T).bit_count()
                for q in outside:
                    if q == r:
                        continue
                    t["pairs"] += 1
                    code = b_is_better(masks, O, T, k, r, q)
                    p3 = (O[T | 1 << r | 1 << q] & ~(T | 1 << r)).bit_count() <= k
                    op, cl_ = d_counts(masks, O, CL[T | 1 << r], q)
                    if code != (p3 and op <= cl_):                    # isBetter_iff
                        t["fail_isBetter_iff"] += 1
                    rep = b_is_repaired(masks, O, CL, T, k, r, q)
                    if rep and not code:                              # IsRepairedBetter.isBetter
                        t["fail_repaired_implies_code"] += 1
                    if cost_r <= k and SS[CL[T | 1 << r]]:
                        if rep:                                       # the repaired rule is sound
                            t["repaired_applications"] += 1
                            if not SS[CL[T | 1 << q]]:
                                t["fail_repaired_sound"] += 1
                        if code:
                            t["code_applications"] += 1
                            if not SS[CL[T | 1 << q]]:
                                t["code_pair_false"] += 1
                        if b_is_better(masks, O, T, k, r, q, old=True) and not SS[CL[T | 1 << q]]:
                            t["bugA_pair_false"] += 1
        for S in fc:
            if S == full or (O[S] & ~S).bit_count() > k or not SS[S]:
                continue
            R = [c for c in range(n) if not S >> c & 1]
            refuted = sum(1 << c for c in R if not SS[CL[S | 1 << c]])
            her = {q: d_hereditary(masks, O, S, q) for q in R}
            code_def = {q: d_counts(masks, O, S, q)[0] <= d_counts(masks, O, S, q)[1] for q in R}
            for Q in q_family(refuted, rng):
                P = s_playable(masks, O, S, k, [c for c in R if not Q >> c & 1])
                for L in limits:
                    t["nodes"] += 1
                    code_cite = (lambda W, r, q, L=L: b_within(L, W, q)
                                 and b_is_better(masks, O, S, k, r, q))
                    rep_cite = (lambda W, r, q, L=L: b_within(L, W, q)
                                and b_is_repaired(masks, O, CL, S, k, r, q))
                    mine = b_full(masks, O, S, P, lambda q: code_def[q], code_cite)
                    old = b_old_order(masks, O, S, P, lambda q: code_def[q], code_cite)
                    for variant, lean in (("fixed", mine), ("old_order", old)):
                        cfg = {"definite": True, "subset": True, "better": True, "limit": L,
                               "variant": variant, "old_move": True}
                        _, Lp, _, _, _ = node_filter(masks, full, S, Q, k, cfg)
                        if sorted(c for _, c in Lp) != sorted(lean):  # Lean filter = item 06 port
                            t[f"fail_port_{variant}"] += 1
                    rep = b_full(masks, O, S, P, lambda q: her[q], rep_cite)
                    if not any(SS[CL[S | 1 << c]] for c in rep):      # repairedFullFilter_sound
                        t["fail_repaired_node"] += 1
                    if not any(SS[CL[S | 1 << c]] for c in mine):
                        definite = any(code_def[q] for q in P)
                        t["code_loses_definite" if definite else "code_loses_better"] += 1
                    if not any(SS[CL[S | 1 << c]] for c in old):
                        t["old_order_loses"] += 1
    return t


def better_augment(rng):
    """A definite-move counterexample graph, up to four extra vertices and two edge flips,
    relabelled: where the better move's false links live."""
    base = rng.choice([m for m, _, _, _ in DEFINITE_CEX])
    n0 = len(base)
    extra = rng.randint(0, 3 if n0 == 14 else 1)
    n = n0 + extra
    ms = list(base) + [1 << v for v in range(n0, n)]
    for v in range(n0, n):
        for u in rng.sample(range(v), rng.randint(1, 4)):
            ms[v] |= 1 << u
            ms[u] |= 1 << v
    for _ in range(rng.randint(0, 2)):
        u, v = rng.sample(range(n), 2)
        ms[u] ^= 1 << v
        ms[v] ^= 1 << u
    perm = list(range(n))
    rng.shuffle(perm)
    return relabel(ms, perm)


def _better_job(args):
    masks, all_sets = args
    return check_better_graph(masks, all_sets=all_sets)


def _better_aug_job(args):
    seed, count = args
    rng = random.Random(seed)
    t = Counter()
    for _ in range(count):
        masks = better_augment(rng)
        O, CL = s_tables(masks)
        opt = next(k for k in range(len(masks) + 1) if s_searchsol_table(masks, k, O, CL)[0])
        t.update(check_better_graph(masks, ks=[max(0, opt - 1), opt, opt + 1], seed=seed,
                                    limits=(0,)))
    return t


def run_better(workers=None, out=None, quick=False, n_random=None):
    """Item 10's check: every labelled graph on 1-5 vertices at every set, on 6 and the atlas
    on 7 at the search's states, random sparse and cover graphs at 10-13, augmented
    definite-move counterexamples at 14-17 at k in {opt-1, opt, opt+1}, and the three pinned
    Lean counterexamples."""
    started = time.time()
    small = [(m, n <= 5) for n in range(1, (4 if quick else 6) + 1) for m in labelled_graphs(n)]
    if not quick:
        small += [(m, False) for m in atlas_graphs(7)]
    rng = random.Random(10)
    count = (10 if quick else 1500) if n_random is None else n_random
    rand = []
    for _ in range(count):
        n = rng.randint(10, 11 if quick else 13)
        rand.append(((random_sparse if rng.random() < 0.5 else random_cover)(n, rng), False))
    work = small + rand
    aug = [] if quick else [(2000 + i, 5) for i in range(400)]
    by = {"small": Counter(), "random": Counter(), "augmented": Counter()}
    with Pool(workers) as pool:
        for t in pool.imap(_better_job, small, chunksize=8):
            by["small"].update(t)
        for t in pool.imap_unordered(_better_job, rand, chunksize=4):
            by["random"].update(t)
        for t in pool.imap_unordered(_better_aug_job, aug):
            by["augmented"].update(t)
    total = Counter()
    for t in by.values():
        total.update(t)
    pinned = {}
    for name, (m, S, r, q, k) in (("better_cex", BETTER_CEX), ("bug_a", BUG_A_CEX)):
        pinned[name] = dict(check_better_graph(m, ks=[k], limits=(0,)))
    pinned["bug_b"] = dict(check_better_graph(BUG_B_CEX[0], ks=[BUG_B_CEX[2]], limits=(0,)))
    report = {"seconds": round(time.time() - started, 1), "graphs": len(work),
              "augmented_graphs": sum(c for _, c in aug), "quick": quick,
              "tally": dict(total), "tally_by_family": {k: dict(v) for k, v in by.items()},
              "pinned_tallies": pinned,
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))
              + sum(v for p in pinned.values() for k, v in p.items() if k.startswith("fail_"))}
    out = out or REPORT.parent / "search_better_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report


# ----------------------------------------------------------------------------
# item 11: the memo and the old move (Search/Memo.lean)
# ----------------------------------------------------------------------------

# The configurations whose filter is node-sound on every graph item 06 checked (no bad
# variant); the Exec invariant is asserted for these and only reported for the rest.
MEMO_FILTERS = [c for c in FILTERS if c["variant"] == "fixed" and c["limit"] in (0, 1)]

# `reinsert_needs_test` in Memo.lean: the path 4-0-2-1-3, S = {}, q = 2, c = 3, k = 2, the
# smallest graph (exhaustive to 5 vertices) where reinsertion without the test fails.
REINSERT_CEX = ([21, 14, 7, 10, 17], 0, 2, 3, 2)
# the smallest graph (exhaustive to 6 vertices, every k, every filter of MEMO_FILTERS) where
# the search inheriting every `seen` entry, with no test, answers a false `unsat`: k = 2.
INHERIT_ALL_CEX = ([37, 22, 15, 12, 18, 33], 2)


def memo_run(masks, k, config, O, CL, SS, inherit_all=False):
    """The search of §1.5 with old move and the memo both on, instrumented with the invariant
    of `Memo.lean`'s `Exec.sound`: at every node entry each old move `q` outside `S` has
    `¬ Sol_k(S·q)`, every memo entry `T` has `¬ Sol_k(T)`, and every `false` answer is a
    state with `¬ Sol_k(S)`. `inherit_all` drops the inheritance test (a mutation).
    Returns (answer, violations Counter)."""
    n = len(masks)
    full = (1 << n) - 1
    memo = set()
    bad = Counter()

    def search(closed, seen):
        closed = CL[closed]                                        # free moves
        if closed == full:
            return True
        if closed in memo:
            return False
        seen &= full & ~closed
        for q in bits(seen):
            if SS[CL[closed | 1 << q]]:
                bad["q_not_refuted"] += 1
        opened = O[closed]
        _, L, _, _, _ = node_filter(masks, full, closed, seen, k, dict(config, old_move=True))
        for _, c in sorted(L):
            inh = seen if inherit_all else inherit(masks, seen, closed, opened, c, k)
            if search(closed | 1 << c, inh):
                return True
            seen |= 1 << c
        if SS[closed]:
            bad["false_refutation_recorded"] += 1
        memo.add(closed)
        return False

    return search(0, 0), bad


def check_memo_graph(masks, ks=None, all_sets=True, tree=True):
    """Every statement of `Search/Memo.lean` on one graph."""
    n = len(masks)
    full = (1 << n) - 1
    O, CL = s_tables(masks)
    t = Counter()
    sets = range(full + 1)
    # cl_insert_cl_insert_comm: cl(q · cl(c · S)) = cl(c · cl(q · S)), every set, no k
    if all_sets:
        for S in sets:
            for q in range(n):
                for c in range(n):
                    t["comm_cases"] += 1
                    if CL[CL[S | 1 << c] | 1 << q] != CL[CL[S | 1 << q] | 1 << c]:
                        t["fail_comm"] += 1
    by_cl = {}
    for T in sets:
        by_cl.setdefault(CL[T], []).append(T)
    for k in (range(0, n + 1) if ks is None else ks):
        SS = s_searchsol_table(masks, k, O, CL)
        P = d_solvable_table(masks, k, O)
        # searchSol_reinsert: the one-step old-move lemma, at every set S
        for S in (sets if all_sets else [S for S in sets if CL[S] == S]):
            for q in range(n):
                back = SS[CL[S | 1 << q]]
                for c in range(n):
                    if (O[S | 1 << q | 1 << c] & ~(S | 1 << q)).bit_count() > k:
                        continue
                    t["reinsert_cases"] += 1
                    if SS[CL[CL[S | 1 << c] | 1 << q]] and not back:
                        t["fail_reinsert"] += 1
                    # the test is needed: without it the lemma fails
                if not back:
                    for c in range(n):
                        if (O[S | 1 << q | 1 << c] & ~(S | 1 << q)).bit_count() > k \
                                and SS[CL[CL[S | 1 << c] | 1 << q]]:
                            t["untested_reinsert_fails"] += 1
        # solvable_iff_of_cl_eq: the memo key, every pair with equal closure and the invariant
        for group in by_cl.values():
            inv = [T for T in group if (O[T] & ~T).bit_count() <= k]
            vals = {P[T] for T in inv}
            t["memo_key_groups"] += 1
            if len(vals) > 1:
                t["fail_memo_key"] += 1
        # Exec.sound in real runs, the instrumented search with old move and the memo
        if tree:
            root = SS[0]
            for cfg in MEMO_FILTERS:
                ans, bad = memo_run(masks, k, cfg, O, CL, SS)
                t["tree_runs"] += 1
                if ans != root:
                    t["fail_tree_answer"] += 1
                for key, v in bad.items():
                    t["fail_" + key] += v
            ans, bad = memo_run(masks, k, MEMO_FILTERS[0], O, CL, SS, inherit_all=True)
            t["mutation_runs"] += 1
            if ans != root:
                t["mutation_false_refutations"] += 1
    return t


def memo_path_check(masks, rng, paths=200):
    """`searchSol_reinsert_path` on random paths: from a state A, moves a_1..a_t each playable
    and each passing the inheritance test for q; then Sol(cl(q · A_t)) -> Sol(cl(q · A))."""
    n = len(masks)
    full = (1 << n) - 1
    O, CL = s_tables(masks)
    t = Counter()
    for k in range(1, n + 1):
        SS = s_searchsol_table(masks, k, O, CL)
        states = [S for S in range(full + 1) if CL[S] == S and S != full]
        for _ in range(paths // n + 1):
            A = rng.choice(states)
            q = rng.randrange(n)
            cur = A
            for _step in range(n):
                moves = [c for c in range(n) if not cur >> c & 1
                         and (O[cur | 1 << c] & ~cur).bit_count() <= k
                         and (O[cur | 1 << q | 1 << c] & ~(cur | 1 << q)).bit_count() <= k]
                if not moves:
                    break
                cur = CL[cur | 1 << rng.choice(moves)]
                t["path_cases"] += 1
                if SS[CL[cur | 1 << q]] and not SS[CL[A | 1 << q]]:
                    t["fail_path"] += 1
    return t


def _memo_job(args):
    masks, all_sets, seed = args
    t = check_memo_graph(masks, all_sets=all_sets)
    t.update(memo_path_check(masks, random.Random(seed)))
    return t


def run_memo(workers=None, out=None, quick=False, n_random=None):
    """Item 11's check: every labelled graph on 1-6 vertices (statements at every set), the
    atlas on 7 (at the free-closed states), random sparse and cover graphs at 8-11, and the
    pinned definite-move counterexamples for the Exec invariant under the code's filter."""
    started = time.time()
    small = [(m, True, i) for n in range(1, (4 if quick else 6) + 1)
             for i, m in enumerate(labelled_graphs(n))]
    if not quick:
        small += [(m, False, i) for i, m in enumerate(atlas_graphs(7))]
    rng = random.Random(11)
    count = (10 if quick else 400) if n_random is None else n_random
    rand = []
    for i in range(count):
        n = rng.randint(8, 9 if quick else 11)
        rand.append(((random_sparse if rng.random() < 0.5 else random_cover)(n, rng), False, i))
    by = {"small": Counter(), "random": Counter()}
    with Pool(workers) as pool:
        for tt in pool.imap(_memo_job, small, chunksize=16):
            by["small"].update(tt)
        for tt in pool.imap_unordered(_memo_job, rand, chunksize=2):
            by["random"].update(tt)
    total = Counter()
    for tt in by.values():
        total.update(tt)
    pinned = {}
    for i, (m, S, q, k) in enumerate(DEFINITE_CEX):
        O, CL = s_tables(m)
        SS = s_searchsol_table(m, k, O, CL)
        runs = {}
        for cfg in MEMO_FILTERS:
            ans, bad = memo_run(m, k, cfg, O, CL, SS)
            runs[config_name(dict(cfg, old_move=True, memo=True))] = {
                "answer": ans, "oracle": SS[0], "violations": dict(bad)}
        pinned[f"definite_cex_{i}"] = runs
    report = {"seconds": round(time.time() - started, 1), "graphs": len(small) + len(rand),
              "quick": quick, "filters": [config_name(c) for c in MEMO_FILTERS],
              "tally": dict(total), "tally_by_family": {k: dict(v) for k, v in by.items()},
              "pinned": pinned,
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))}
    out = out or REPORT.parent / "search_memo_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report


# ----------------------------------------------------------------------------
# item 12: the search assembled (Search/Decide.lean)
# ----------------------------------------------------------------------------

DECIDE_LIMITS = (0, 1)

# a 14-customer augmented definite-move counterexample (`run_decide`, seed family 3000) on which
# the code's own run at k = 6 expands the state {1}, where its filter loses the last solution,
# and still answers `true`, as the oracle does: a lost node inside a real run.
RUN_LOST_CEX = ([10357, 5378, 229, 13384, 10385, 8805, 621, 404, 898, 2912, 1034, 2577, 4106,
                 8249], 6, 0b10)


def k_parts(masks, O, S, Q, k):
    """The playable candidates `playable G k S ((univ \\ S) \\ Q)`, in index order."""
    n = len(masks)
    K = [c for c in range(n) if not S >> c & 1 and not Q >> c & 1]
    return s_playable(masks, O, S, k, K)


def k_code_filter(masks, O, S, Q, k, L):
    """`codeFullFilter G k L S Q`, transcribed through `b_full`."""
    P = k_parts(masks, O, S, Q, k)

    def D(q):
        o, c = d_counts(masks, O, S, q)
        return o <= c

    def cite(W, r, q):
        return b_within(L, W, q) and b_is_better(masks, O, S, k, r, q)

    return b_full(masks, O, S, P, D, cite)


def k_repaired_filter(masks, O, CL, S, Q, k, L):
    """`repairedFullFilter G k L S Q`."""
    P = k_parts(masks, O, S, Q, k)

    def cite(W, r, q):
        return b_within(L, W, q) and b_is_repaired(masks, O, CL, S, k, r, q)

    return b_full(masks, O, S, P, lambda q: d_hereditary(masks, O, S, q), cite)


def k_node_repaired(masks, O, CL, S, Q, k, L):
    """`CodeNodeRepaired G k L S Q`: the definite pick, if any, is hereditarily definite; if the
    definite move does not fire, every better-move drop has some earlier repaired citation."""
    P = k_parts(masks, O, S, Q, k)
    F = [q for q in P if (lambda oc: oc[0] <= oc[1])(d_counts(masks, O, S, q))]
    if F:
        return d_hereditary(masks, O, S, min(F))
    W = s_subset_filter(masks, O, S, P)
    for r in W:
        if any(q < r and b_within(L, W, q) and b_is_better(masks, O, S, k, r, q) for q in W):
            if not any(q < r and b_is_repaired(masks, O, CL, S, k, r, q) for q in W):
                return False
    return True


def decide_run(masks, k, filt, O, CL, SS, L=0, inspect=True, lost=None):
    """The search of `Exec` (memo on, old move on with the inheritance test, children in index
    order) with the filter `filt(S, Q)`. At every expanded node (`ExecOn`'s `N`) it records
    `NodeSoundAt` for the code's filter and `CodeNodeRepaired`; with `inspect=False` it only
    runs. Returns (answer, Counter)."""
    n = len(masks)
    full = (1 << n) - 1
    memo = set()
    t = Counter()

    def search(closed, seen):
        closed = CL[closed]
        if closed == full:
            return True
        if closed in memo:
            return False
        seen &= full & ~closed
        opened = O[closed]
        out = filt(closed, seen)
        if inspect:
            t["nodes"] += 1
            if (opened & ~closed).bit_count() > k:
                t["fail_invariant"] += 1
            # NodeSoundAt's hypothesis on Q; it can fail only downstream of a lost node,
            # whose refuted-but-solvable child then joins `seen` (asserted per run below)
            q_ok = not any(SS[CL[closed | 1 << q]] for q in bits(seen))
            if not q_ok:
                t["nodes_q_not_refuted"] += 1
            sound = not q_ok or not SS[closed] or any(SS[CL[closed | 1 << c]] for c in out)
            rep = k_node_repaired(masks, O, CL, closed, seen, k, L)
            t["nodes_sound"] += sound
            t["nodes_repaired"] += rep
            if rep and not sound:
                t["fail_repaired_not_sound"] += 1      # nodeSoundAt_codeFullFilter_of_repaired
            if not sound:
                t["nodes_unsound"] += 1
                if lost is not None:
                    lost.append(closed)
        for c in sorted(out):
            if search(closed | 1 << c, inherit(masks, seen, closed, opened, c, k)):
                return True
            seen |= 1 << c
        memo.add(closed)
        return False

    return search(0, 0), t


def check_decide_graph(masks, ks=None, pw=False, examples=None):
    """Item 12's statements on one graph, at every k (or `ks`)."""
    n = len(masks)
    O, CL = s_tables(masks)
    t = Counter()
    narrow = None
    if pw and n:
        narrow = min(m_vs_of_layout(masks, tau) for tau in itertools.permutations(range(n))) + 1
    for k in (range(0, n + 1) if ks is None else ks):
        SS = s_searchsol_table(masks, k, O, CL)
        root = SS[0]
        for L in DECIDE_LIMITS:
            # the repaired search: exec_repairedFullFilter_* (no instrumentation needed)
            ans, _ = decide_run(masks, k, lambda S, Q: k_repaired_filter(masks, O, CL, S, Q, k, L),
                                O, CL, SS, L, inspect=False)
            t["repaired_runs"] += 1
            if ans != root:
                t["fail_repaired_answer"] += 1
            if not ans and narrow is not None:
                t["pw_cases"] += 1
                if not k < narrow:                       # k < narrowness, i.e. k <= pw
                    t["fail_repaired_pw"] += 1
            # the code's search, instrumented with ExecOn's node predicates
            lost = []
            ans, tt = decide_run(masks, k, lambda S, Q: k_code_filter(masks, O, S, Q, k, L),
                                 O, CL, SS, L, lost=lost)
            if lost and examples is not None:
                examples.append({"masks": list(masks), "k": k, "limit": L, "lost_states": lost,
                                 "answer": ans, "oracle": root})
            t.update(tt)
            t["code_runs"] += 1
            if ans != root:
                t["code_wrong_answer"] += 1
            run_sound = tt["nodes_unsound"] == 0
            if run_sound and tt["nodes_q_not_refuted"]:
                t["fail_runsound_q_not_refuted"] += 1   # ExecOn.sound's invariant
            t["code_runs_q_not_refuted"] += tt["nodes_q_not_refuted"] > 0
            run_repaired = tt["nodes_repaired"] == tt["nodes"]
            t["code_runs_runsound"] += run_sound
            t["code_runs_all_repaired"] += run_repaired
            if not ans and run_sound and root:
                t["fail_runsound_answer"] += 1          # codeExec_sound_of_runSound
            if not ans and run_repaired and root:
                t["fail_allrepaired_answer"] += 1       # codeExec_sound_of_repaired
    return t


def _decide_job(args):
    masks, pw = args
    ex = []
    t = check_decide_graph(masks, pw=pw, examples=ex)
    return t, ex


def _decide_aug_job(args):
    seed, count = args
    rng = random.Random(seed)
    t = Counter()
    ex = []
    for _ in range(count):
        masks = better_augment(rng)
        O, CL = s_tables(masks)
        opt = next(k for k in range(len(masks) + 1) if s_searchsol_table(masks, k, O, CL)[0])
        t.update(check_decide_graph(masks, ks=[max(0, opt - 1), opt], examples=ex))
    return t, ex


def decide_pinned():
    """`codeFullFilter_cex` and `not_codeFilterSound_cexGraph` on the 14-customer graph, and
    whether the code's own run at k = 6 ever reaches the state {2}."""
    masks, S, q, k = DEFINITE_CEX[0]
    O, CL = s_tables(masks)
    SS = s_searchsol_table(masks, k, O, CL)
    out = {"filter_at_cex": {}, "runs": {}}
    for L in (0, 1, 2, 3):
        out["filter_at_cex"][L] = k_code_filter(masks, O, S, 0, k, L)
    for i, (m, S0, _, kk) in enumerate(DEFINITE_CEX):
        O2, CL2 = s_tables(m)
        for kq in (kk - 1, kk):
            SS2 = s_searchsol_table(m, kq, O2, CL2)
            for L in DECIDE_LIMITS:
                visited = []

                def filt(T, Q, m=m, O2=O2, kq=kq, L=L, visited=visited):
                    visited.append(T)
                    return k_code_filter(m, O2, T, Q, kq, L)

                ans, tt = decide_run(m, kq, filt, O2, CL2, SS2, L)
                out["runs"][f"definite_cex_{i}/k{kq}/L{L}"] = {
                    "answer": ans, "oracle": SS2[0], "visits_cex_state": S0 in visited,
                    "tally": dict(tt)}
    out["lean_claims_hold"] = (all(v == [0] for v in out["filter_at_cex"].values())
                               and SS[S] and not SS[CL[S | 1 << q]])
    return out


def run_decide(workers=None, out=None, quick=False, n_random=None, n_aug=800):
    """Item 12's check: every labelled graph on 1-6 vertices (pathwidth by layouts to 5), the
    atlas on 7, random sparse and cover graphs at 8-12, augmented definite-move
    counterexamples at 14-17 at k in {opt-1, opt}, and the pinned counterexample."""
    started = time.time()
    small = [(m, n <= 5) for n in range(1, (4 if quick else 6) + 1) for m in labelled_graphs(n)]
    if not quick:
        small += [(m, False) for m in atlas_graphs(7)]
    rng = random.Random(12)
    count = (10 if quick else 3000) if n_random is None else n_random
    rand = []
    for _ in range(count):
        n = rng.randint(8, 9 if quick else 12)
        rand.append(((random_sparse if rng.random() < 0.5 else random_cover)(n, rng), False))
    aug = [] if quick else [(3000 + i, 5) for i in range(n_aug)]
    by = {"small": Counter(), "random": Counter(), "augmented": Counter()}
    examples = []
    with Pool(workers) as pool:
        for t, ex in pool.imap(_decide_job, small, chunksize=16):
            by["small"].update(t)
            examples += ex
        for t, ex in pool.imap_unordered(_decide_job, rand, chunksize=2):
            by["random"].update(t)
            examples += ex
        for t, ex in pool.imap_unordered(_decide_aug_job, aug):
            by["augmented"].update(t)
            examples += ex
    total = Counter()
    for t in by.values():
        total.update(t)
    pinned = decide_pinned()
    report = {"seconds": round(time.time() - started, 1), "graphs": len(small) + len(rand),
              "augmented_graphs": sum(c for _, c in aug), "quick": quick,
              "limits": list(DECIDE_LIMITS),
              "tally": dict(total), "tally_by_family": {k: dict(v) for k, v in by.items()},
              "pinned": pinned, "lost_node_runs": examples,
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))
              + (0 if pinned["lean_claims_hold"] else 1)}
    out = out or REPORT.parent / "search_decide_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report


# ----------------------------------------------------------------------------
# item 13: Hall's converse (Search/DefiniteMatching.lean)
# ----------------------------------------------------------------------------
#
# Transcribes `Search/DefiniteMatching.lean`: for every set S (not only free-closed ones)
# and every q, with Y = cl(S + q) - S - {q}, the repair `IsHereditarilyDefinite`, its
# deficiency form `open(q, S) + |D| <= |o(D)| + |Y| + 1` for all D <= Y, the matching form
# (a maximum matching of Y into the new stacks reaches open(q, S) - 1), and the Lean proof's
# own construction: delta = |Y| + 1 - open dummy stacks shared by every d, Hall's condition
# on the augmented sets, a Y-saturating matching of them, and at least open - 1 customers
# matched to real stacks. Also `card_opened_union_eq` and `openCount_eq_zero_of_mem`.


def h_hereditary_any(masks, O, S, q):
    """`IsHereditarilyDefinite` at any S (B ranges over S <= B <= X, q not in B)."""
    X = d_child(masks, O, S, q)
    bX = d_open_stacks(O, X)
    if S >> q & 1:
        return True
    D = X & ~S & ~(1 << q)
    E = D
    while True:
        if d_open_stacks(O, S | E) < bX:
            return False
        if E == 0:
            return True
        E = (E - 1) & D


def h_new_union(masks, OS, D):
    u = 0
    for d in bits(D):
        u |= masks[d] & ~OS
    return u


def h_augmented_matching(masks, OS, Y, delta):
    """Maximum matching of Y into o(d, S) plus `delta` dummies shared by all; returns
    (size, number matched to real stacks)."""
    match = {}

    def augment(d, seen):
        for y in list(bits(masks[d] & ~OS)) + [("dummy", i) for i in range(delta)]:
            if y in seen:
                continue
            seen.add(y)
            if y not in match or augment(match[y], seen):
                match[y] = d
                return True
        return False

    size = sum(1 for d in bits(Y) if augment(d, set()))
    real = sum(1 for y in match if not isinstance(y, tuple))
    return size, real


def check_hall_graph(masks, all_sets=True, mutate=False):
    n = len(masks)
    full = (1 << n) - 1
    O = d_opened_table(masks)
    t = Counter()
    sets = range(full + 1) if all_sets else [
        S for S in range(full) if sum(1 << c for c in range(n) if masks[c] & ~O[S] == 0) == S]
    for S in sets:
        OS = O[S]
        for q in range(n):
            op, _ = d_counts(masks, O, S, q)
            if S >> q & 1:
                t["q_in_S"] += 1
                if op != 0:
                    t["fail_openCount_eq_zero_of_mem"] += 1
            X = d_child(masks, O, S, q)
            Y = X & ~S & ~(1 << q)
            ny = Y.bit_count()
            her = h_hereditary_any(masks, O, S, q)
            mat = d_matching_size(masks, O, S, q) >= op - 1
            # deficiency form, over every D <= Y (only claimed for q not in S)
            slack = 0 if mutate else 1
            defi = True
            E = Y
            while True:
                t["deficiency_cases"] += 1
                # card_opened_union_eq
                if O[S | E].bit_count() != OS.bit_count() + h_new_union(masks, OS, E).bit_count():
                    t["fail_card_opened_union_eq"] += 1
                if op + E.bit_count() > h_new_union(masks, OS, E).bit_count() + ny + slack:
                    defi = False
                if E == 0:
                    break
                E = (E - 1) & Y
            t["pairs"] += 1
            if her != mat:
                t["fail_iff_matching"] += 1      # isHereditarilyDefinite_iff_hasDefiniteMatching
            if not S >> q & 1:
                if her and not defi:
                    t["fail_hall_of_hereditary"] += 1   # hall_of_isHereditarilyDefinite
                if defi != her:
                    t["deficiency_ne_hereditary"] += 1  # the converse, not claimed in Lean
                if her:
                    t["hereditary_pairs"] += 1
                    if op > ny + 1:
                        t["fail_delta_truncation"] += 1  # hY: D = empty
                    delta = ny + 1 - op
                    size, real = h_augmented_matching(masks, OS, Y, delta)
                    if size != ny:
                        t["fail_hall_augmented_saturates"] += 1
                    if real + 1 < op:
                        t["fail_real_matched"] += 1      # exists_matching_of_isHereditarilyDefinite
    return t


def _hall_job(args):
    masks, all_sets = args
    return check_hall_graph(masks, all_sets=all_sets)


def run_hall(workers=None, out=None, quick=False, n_random=None):
    """Item 13's check: every labelled graph on 1-5 (6 unless quick) at every set S, every
    atlas graph on 7 at every S, random graphs at 10-12 and the pinned counterexamples at
    their free-closed states."""
    started = time.time()
    work = [(m, True) for n in range(1, (4 if quick else 6) + 1) for m in labelled_graphs(n)]
    if not quick:
        work += [(m, True) for m in atlas_graphs(7)]
    rng = random.Random(13)
    count = (20 if quick else 1000) if n_random is None else n_random
    for _ in range(count):
        n = rng.randint(10, 11 if quick else 12)
        work.append(((random_sparse if rng.random() < 0.5 else random_cover)(n, rng), False))
    if not quick:
        work += [(m, False) for m, _, _, _ in DEFINITE_CEX]
    total = Counter()
    with Pool(workers) as pool:
        for t in pool.imap_unordered(_hall_job, work, chunksize=8):
            total.update(t)
    m0 = DEFINITE_CEX[0][0]
    O = d_opened_table(m0)
    S, q = DEFINITE_CEX[0][1], DEFINITE_CEX[0][2]
    op, _ = d_counts(m0, O, S, q)
    pinned = {"open": op, "max_matching": d_matching_size(m0, O, S, q),
              "hereditary": h_hereditary_any(m0, O, S, q)}
    report = {"seconds": round(time.time() - started, 1), "graphs": len(work), "quick": quick,
              "tally": dict(total), "cexGraph_at_S2_q0": pinned,
              "failures": sum(v for k, v in total.items() if k.startswith("fail_"))}
    out = out or REPORT.parent / "search_hall_check.json"
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--random", type=int, default=None, help="random instances at 8-16 vertices")
    ap.add_argument("--model", action="store_true",
                    help="item 07: check the Lean model of Search/Basic.lean")
    ap.add_argument("--definite", action="store_true",
                    help="item 08: check Search/DefiniteMove.lean and the counterexamples")
    ap.add_argument("--subset", action="store_true",
                    help="item 09: check Search/SubsetRule.lean")
    ap.add_argument("--better", action="store_true",
                    help="item 10: check Search/BetterMove.lean")
    ap.add_argument("--memo", action="store_true",
                    help="item 11: check Search/Memo.lean")
    ap.add_argument("--decide", action="store_true",
                    help="item 12: check Search/Decide.lean")
    ap.add_argument("--hall", action="store_true",
                    help="item 13: check Search/DefiniteMatching.lean")
    args = ap.parse_args()
    if args.hall:
        print(json.dumps(run_hall(workers=args.workers, quick=args.quick,
                                  n_random=args.random), indent=1))
        return
    if args.decide:
        print(json.dumps(run_decide(workers=args.workers, quick=args.quick,
                                    n_random=args.random), indent=1))
        return
    if args.memo:
        print(json.dumps(run_memo(workers=args.workers, quick=args.quick,
                                  n_random=args.random), indent=1))
        return
    if args.better:
        print(json.dumps(run_better(workers=args.workers, quick=args.quick,
                                    n_random=args.random), indent=1))
        return
    if args.subset:
        print(json.dumps(run_subset(workers=args.workers, quick=args.quick,
                                    n_random=args.random), indent=1))
        return
    if args.definite:
        print(json.dumps(run_definite(workers=args.workers, quick=args.quick,
                                      n_random=args.random), indent=1))
        return
    if args.model:
        print(json.dumps(run_model(workers=args.workers, quick=args.quick), indent=1))
        return
    report = run(quick=args.quick, workers=args.workers, n_random=args.random)
    print(json.dumps({"seconds": report["seconds"], "graphs": report["graphs"],
                      "summary": report["summary"],
                      "pinned": {k: {c: r for c, r in v["runs"].items()}
                                 for k, v in report["pinned"].items()}}, indent=1))


if __name__ == "__main__":
    main()
