"""The production filter with the repaired rules, against the oracle (loop0007 item 01).

`satisfiability/customer_search.py` gained `repaired_rules` on 2026-10-01: the
definite move fires only on a hereditarily definite candidate, tested by the
matching condition, and the better move cites only under `IsRepairedBetter`
(`paper2/revised_algorithm.md` §4.6.1). This module checks the production
Python against `paper2/search_check.py`, which shares no code with the solver:

- **Node checks.** At every free-closed state `S` with the invariant, every
  `k`, a family of old-move sets `Q` of genuinely refuted children, and every
  limit `L` in (0, 1, 2), the production filter (`_apply_dominance` with every
  rule on) must

  - with `repaired=True`, equal `k_repaired_filter`, the transcription of the
    Lean `repairedFullFilter`, as a set (`eq_repaired`), and keep a child with
    a solution whenever the state has one (`sound_repaired`, node soundness
    against the oracle `SearchSol` table);
  - with `repaired=False`, equal `k_code_filter`, the Lean `codeFullFilter`
    (`eq_code`): the port is the code the theorems were stated about;
  - and the matching test agrees with `d_hereditary` (`IsHereditarilyDefinite`
    by enumeration of every intermediate set) on every candidate that passes
    `close ≥ open` (`eq_matching`).

- **Whole-search checks.** `decide(..., native=False, repaired_rules=True)`
  answers `Sol_k(∅)` at every `k ≥ 1` under every combination of better move
  (off, `L` in 0, 1, 4), old move and memo, and every satisfiable witness
  simulates to at most `k`. With `repaired_rules=False` the same.

Families: every labelled graph on 1-6 vertices; every graph on 7 vertices
(networkx atlas) under the identity and four random labellings; random sparse
and Chu & Stuckey-shaped graphs at 8-13; the pinned counterexamples
(`DEFINITE_CEX`, both; Bug A; Bug B; `RUN_LOST_CEX`) at every `k`; and the
augmented definite-move gadgets of `better_augment` at 14-17 vertices, at
`opt − 1`, `opt` and `opt + 1`, with `Q = ∅`.

    python -m paper2.solver_fix_check            # full run, writes paper2/data/solver_fix_check.json
    python -m paper2.solver_fix_check --quick    # to 5 vertices, a few of each other family
"""
from __future__ import annotations

import argparse
import json
import random
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from paper2.search_check import (
    BUG_A_CEX,
    BUG_B_CEX,
    DEFINITE_CEX,
    RUN_LOST_CEX,
    atlas_graphs,
    better_augment,
    bits,
    d_counts,
    d_hereditary,
    k_code_filter,
    k_repaired_filter,
    labelled_graphs,
    matrix_from_masks,
    q_family,
    random_cover,
    random_sparse,
    relabel,
    s_searchsol_table,
    s_tables,
)
from satisfiability.customer_search import _apply_dominance, _has_definite_matching, decide
from satisfiability.heuristics import product_order_from_customers

REPORT = Path(__file__).resolve().parent / "data" / "solver_fix_check.json"
LIMITS = (0, 1, 2)
SEARCH_CONFIGS = [dict(better_move=b, better_move_dominators=L, old_move=o, memo=m)
                  for b, L in ((False, 4), (True, 0), (True, 1), (True, 4))
                  for o, m in ((False, False), (True, False), (False, True), (True, True))]


def production_filter(masks, S, Q, k, L, repaired):
    """The production node filter at `(S, Q)`: playable candidates in index order, then
    `_apply_dominance` with the definite move, the subset rule and the better move."""
    n = len(masks)
    full = (1 << n) - 1
    opened = 0
    for c in bits(S):
        opened |= masks[c]
    remaining = full & ~S
    opens = {c: masks[c] & ~opened for c in bits(remaining)}
    open_now = (opened & ~S).bit_count()
    playable = [(open_now + opens[c].bit_count(), c) for c in bits(remaining & ~Q)
                if open_now + opens[c].bit_count() <= k]
    if not playable:
        return []
    kept = _apply_dominance(playable, opens, True, True, better_move=True, dominators=L,
                            repaired=repaired, masks=masks, full=full, closed=S,
                            opened=opened, k=k)
    return sorted(c for _, c in kept)


def matching_test(masks, O, S, q):
    """The production matching test for `q` at `S`, built as `_apply_dominance` builds it."""
    own = masks[q] & ~O[S]
    freed = [masks[d] & ~O[S] for d in range(len(masks))
             if not S >> d & 1 and d != q and (masks[d] & ~O[S]) & ~own == 0]
    return _has_definite_matching(freed, own.bit_count() - 1)


def check_nodes(masks, ks=None, q_sets=True, limits=LIMITS, seed=0):
    n = len(masks)
    full = (1 << n) - 1
    O, CL = s_tables(masks)
    rng = random.Random(seed)
    t = Counter()
    states = [S for S in range(full) if CL[S] == S]
    for k in (range(0, n + 1) if ks is None else ks):
        SS = s_searchsol_table(masks, k, O, CL)
        for S in states:
            if (O[S] & ~S).bit_count() > k:
                continue
            for q in bits(full & ~S):
                o, c = d_counts(masks, O, S, q)
                if o <= c:
                    t["matching_checks"] += 1
                    m, h = matching_test(masks, O, S, q), d_hereditary(masks, O, S, q)
                    t["eq_matching"] += m == h
                    t["fail_matching"] += m != h
                    t["definite_premise_without_hereditary"] += not h
            refuted = sum(1 << q for q in bits(full & ~S)
                          if (O[S | 1 << q] & ~S).bit_count() <= k and not SS[CL[S | 1 << q]])
            for Q in (q_family(refuted, rng) if q_sets else [0]):
                for L in limits:
                    t["nodes"] += 1
                    rep = production_filter(masks, S, Q, k, L, True)
                    old = production_filter(masks, S, Q, k, L, False)
                    ok_rep = rep == sorted(k_repaired_filter(masks, O, CL, S, Q, k, L))
                    ok_old = old == sorted(k_code_filter(masks, O, S, Q, k, L))
                    t["eq_repaired"] += ok_rep
                    t["fail_eq_repaired"] += not ok_rep
                    t["eq_code"] += ok_old
                    t["fail_eq_code"] += not ok_old
                    t["filters_differ"] += rep != old
                    if SS[S]:
                        t["nodes_with_solution"] += 1
                        t["sound_repaired"] += any(SS[CL[S | 1 << c]] for c in rep)
                        t["fail_sound_repaired"] += not any(SS[CL[S | 1 << c]] for c in rep)
                        t["code_lost"] += not any(SS[CL[S | 1 << c]] for c in old)
    return t


def check_searches(masks, ks=None):
    n = len(masks)
    if n == 0:
        return Counter()
    O, CL = s_tables(masks)
    inst = MOSPInstance.from_matrix(matrix_from_masks(masks), name="solver_fix_check")
    t = Counter()
    for k in (range(1, n + 1) if ks is None else [k for k in ks if k >= 1]):
        truth = s_searchsol_table(masks, k, O, CL)[0]
        for cfg in SEARCH_CONFIGS:
            for repaired in (True, False):
                d = decide(inst, k, native=False, repaired_rules=repaired, **cfg)
                tag = "repaired" if repaired else "code"
                t[f"searches_{tag}"] += 1
                right = (d.status == "sat") == truth
                t[f"fail_answer_{tag}"] += not right
                if d.status == "sat":
                    value = max_open_stacks(inst, product_order_from_customers(inst, d.order))
                    t[f"fail_witness_{tag}"] += value > k
    return t


def _job(args):
    masks, opts = args
    t = check_nodes(masks, ks=opts.get("ks"), q_sets=opts.get("q_sets", True),
                    limits=opts.get("limits", LIMITS), seed=opts.get("seed", 0))
    if opts.get("searches", True):
        t.update(check_searches(masks, ks=opts.get("ks")))
    return opts["family"], t


def _aug_job(args):
    seed, count = args
    rng = random.Random(seed)
    t = Counter()
    for _ in range(count):
        masks = better_augment(rng)
        O, CL = s_tables(masks)
        opt = next(k for k in range(len(masks) + 1) if s_searchsol_table(masks, k, O, CL)[0])
        ks = [max(1, opt - 1), opt, opt + 1]
        t.update(check_nodes(masks, ks=ks, q_sets=False, limits=(0, 1)))
        t.update(check_searches(masks, ks=ks))
        t["graphs"] += 1
    return "gadget", t


def jobs(quick):
    rng = random.Random(20261001)
    top = 5 if quick else 6
    for n in range(1, top + 1):
        for masks in labelled_graphs(n):
            yield masks, dict(family="labelled", seed=rng.randrange(1 << 30))
    if not quick:
        for masks in atlas_graphs(7):
            for p in range(5):
                perm = list(range(7)) if p == 0 else rng.sample(range(7), 7)
                yield relabel(masks, perm), dict(family="atlas7", seed=rng.randrange(1 << 30))
    for i in range(20 if quick else 600):
        n = rng.randint(8, 13)
        masks = random_sparse(n, rng) if i % 2 else random_cover(n, rng)
        yield masks, dict(family="random", q_sets=False, seed=rng.randrange(1 << 30))
    pinned = [m for m, _, _, _ in DEFINITE_CEX] + [BUG_A_CEX[0], BUG_B_CEX[0], RUN_LOST_CEX[0]]
    for masks in pinned:
        yield masks, dict(family="pinned", q_sets=False, limits=(0, 1))


def definite_cex_filter():
    """On `DEFINITE_CEX` at S = {2}, k = 6: the old filter keeps 0 alone, the repaired does not."""
    masks, S, q, k = DEFINITE_CEX[0]
    O, CL = s_tables(masks)
    SS = s_searchsol_table(masks, k, O, CL)
    out = {}
    for L in LIMITS:
        old = production_filter(masks, S, 0, k, L, False)
        rep = production_filter(masks, S, 0, k, L, True)
        out[L] = {"code": old, "repaired": rep,
                  "repaired_keeps_solution": any(SS[CL[S | 1 << c]] for c in rep)}
    return out


def summarise(by_family):
    total = Counter()
    for t in by_family.values():
        total.update(t)
    fails = {key: v for key, v in total.items() if key.startswith("fail") and v}
    return total, fails


def run(quick=False, workers=None, out=REPORT, n_aug=None):
    started = time.time()
    by_family: dict[str, Counter] = {}
    n_aug = (8 if quick else 200) if n_aug is None else n_aug
    with Pool(workers) as pool:
        for family, t in pool.imap_unordered(_job, jobs(quick), chunksize=64):
            by_family.setdefault(family, Counter()).update(t)
        per = 4
        for family, t in pool.imap_unordered(_aug_job, [(9000 + i, per) for i in range(n_aug // per)]):
            by_family.setdefault(family, Counter()).update(t)
    total, fails = summarise(by_family)
    report = {
        "quick": quick,
        "seconds": round(time.time() - started, 1),
        "definite_cex_filter": definite_cex_filter(),
        "by_family": {f: dict(sorted(t.items())) for f, t in sorted(by_family.items())},
        "total": dict(sorted(total.items())),
        "failures": fails,
    }
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1, default=str) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--aug", type=int, default=None, help="augmented gadget graphs")
    ap.add_argument("--out", type=Path, default=REPORT)
    args = ap.parse_args()
    report = run(quick=args.quick, workers=args.workers, out=args.out, n_aug=args.aug)
    print(json.dumps({k: report[k] for k in ("seconds", "total", "failures",
                                             "definite_cex_filter")}, indent=1))


if __name__ == "__main__":
    main()
