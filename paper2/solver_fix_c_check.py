"""The repaired rules in the C, against the Python reference (loop0007 item 02).

`customer_search.c` gained `repaired_rules` on 2026-10-01, through the new
entry point `cs_decide_rules` (`cs_decide_variant` is it with the published
rules). The Python reference (`decide(..., native=False)`) carries the same
flag since item 01, where it was checked against the independent oracle of
`paper2/search_check.py` at every node (`paper2/solver_fix_check.py`). This
module checks that the C is the same search as the Python: equal status, node
count and closing order on every call, under both settings of
`repaired_rules`, so the oracle checks of item 01 carry over to the C.

Configurations: subset rule and definite move on or off, better move off or on
with dominator limit 0, 1 or 4, and old move / memo in the three settings the
two implementations run identically ((on, off), (off, on), (off, off)) -- with
both on the C runs both and the Python drops the memo, by design
(`tests/test_native.py`). A fan-order and a restricted-frontier setting are
added on the small families.

Families:

- `native_random`: the generator of `tests/test_native.py` (up to 8 customers),
  every `k` from 0 to `n + 1`;
- `pinned`: both `DEFINITE_CEX` graphs, Bug A, the 8-vertex Bug B node graph,
  the 10-vertex Bug B false refutation, `RUN_LOST_CEX`, and the 10 x 13,
  17 x 9 and 10 x 20 matrices of the better-move bug, every `k`;
- `gadget`: `better_augment` at 14-17 vertices, every `k`;
- `random`: `random_sparse` and `random_cover` at 10-24 vertices, every `k`;
- `corpus`: certified corpus instances at 9-125 customers, at `opt − 1` and
  `opt`, under a node cap (equal under a cap means equal up to it; the abort
  point is itself a node count).

    python -m paper2.solver_fix_c_check --workers 16       # writes paper2/data/solver_fix_c_check.json
    python -m paper2.solver_fix_c_check --quick
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import random
import time
from collections import Counter
from pathlib import Path

from mosp.instance import MOSPInstance
from paper2.search_check import (
    BUG_A_CEX,
    BUG_B_CEX,
    DEFINITE_CEX,
    RUN_LOST_CEX,
    better_augment,
    matrix_from_masks,
    random_cover,
    random_sparse,
)
from satisfiability.customer_search import decide

REPORT = Path(__file__).resolve().parent / "data" / "solver_fix_c_check.json"

# The 10-vertex false refutation by Bug B alone (paper2/search_soundness.md).
BUG_B_10 = [523, 519, 678, 73, 16, 548, 72, 388, 384, 551]

OLD_MEMO = ((True, False), (False, True), (False, False))
BETTER = ((False, 4), (True, 0), (True, 1), (True, 4))


def full_configs():
    out = []
    for s in (False, True):
        for d in (False, True):
            for b, L in BETTER:
                for o, m in OLD_MEMO:
                    out.append(dict(subset_rule=s, definite_move=d, better_move=b,
                                    better_move_dominators=L, old_move=o, memo=m))
    # the two remaining flags, on the production-like setting
    out.append(dict(subset_rule=True, definite_move=True, better_move=True,
                    better_move_dominators=0, old_move=True, memo=False, fan_order="degree"))
    out.append(dict(subset_rule=True, definite_move=True, better_move=True,
                    better_move_dominators=4, old_move=False, memo=True, restrict=True))
    return out


def corpus_configs():
    return [dict(subset_rule=True, definite_move=True, better_move=b,
                 better_move_dominators=L, old_move=o, memo=m)
            for b, L in ((False, 4), (True, 0), (True, 4)) for o, m in ((True, False), (False, True))]


FULL = full_configs()
CORPUS = corpus_configs()


def compare(instance: MOSPInstance, ks, configs, max_nodes=None) -> Counter:
    t = Counter()
    active = {c for c in range(instance.n_customers) if instance.customer_patterns(c)}
    for k in ks:
        for cfg in configs:
            seen = {}
            for repaired in (False, True):
                tag = "repaired" if repaired else "old"
                py = decide(instance, k, native=False, repaired_rules=repaired,
                            max_nodes=max_nodes, **cfg)
                c = decide(instance, k, native=True, repaired_rules=repaired,
                           max_nodes=max_nodes, **cfg)
                t[f"calls_{tag}"] += 1
                t[f"nodes_{tag}"] += c.nodes
                t[f"{c.status}_{tag}"] += 1
                # The C closes customers needing nothing as free moves at the
                # root and lists them; the Python omits them. Compare the rest.
                c_order = None if c.order is None else [x for x in c.order if x in active]
                if (py.status, py.nodes, py.order) != (c.status, c.nodes, c_order):
                    t[f"mismatch_{tag}"] += 1
                    if t["examples"] < 5:
                        t["examples"] += 1
                        print("MISMATCH", instance.name, k, cfg, repaired, py, c, flush=True)
                seen[repaired] = c
            # where the two settings part, on the C: a different answer is a
            # finding unless one side aborted on the node cap
            old, rep = seen[False], seen[True]
            t["settings_nodes_differ"] += old.nodes != rep.nodes
            if "unknown" not in (old.status, rep.status) and not cfg.get("restrict"):
                t["settings_answer_differ"] += old.status != rep.status
    return t


def _masks_instance(masks, name):
    return MOSPInstance.from_matrix(matrix_from_masks(masks), name=name)


def _job(args):
    family, payload = args
    t = Counter()
    if family in ("native_random", "pinned", "gadget", "random"):
        name, inst = payload
        n = inst.n_customers
        t.update(compare(inst, range(0, n + 2), FULL, max_nodes=200_000))
        t["instances"] += 1
        t[f"n_{n}"] += 1
    else:                                     # corpus
        name, matrix, opt, cap = payload
        inst = MOSPInstance.from_matrix(matrix, name=name)
        t.update(compare(inst, [opt - 1, opt], CORPUS, max_nodes=cap))
        t["instances"] += 1
        t["max_n"] = inst.n_customers
    return family, t


def native_random(count, seed):
    rng = random.Random(seed)
    for i in range(count):
        rows = [[1 if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8]) else 0
                 for _ in range(rng.randint(1, 7))]
                for _ in range(rng.randint(1, 8))]
        width = max(len(r) for r in rows)
        rows = [r + [0] * (width - len(r)) for r in rows]
        yield f"native_random_{i}", MOSPInstance.from_matrix(rows, name=f"nr{i}")


def pinned():
    from tests.test_customer_search import MINIMAL_10x13, MINIMAL_17x9
    from tests.test_differential import DRAWN_10x20
    out = [(f"definite_cex_{i}", _masks_instance(m, f"dc{i}")) for i, (m, _, _, _) in enumerate(DEFINITE_CEX)]
    out += [("bug_a", _masks_instance(BUG_A_CEX[0], "bug_a")),
            ("bug_b_8", _masks_instance(BUG_B_CEX[0], "bug_b_8")),
            ("bug_b_10", _masks_instance(BUG_B_10, "bug_b_10")),
            ("run_lost", _masks_instance(RUN_LOST_CEX[0], "run_lost")),
            ("minimal_10x13", MOSPInstance.from_matrix(MINIMAL_10x13[0], name="m10x13")),
            ("minimal_17x9", MOSPInstance.from_matrix(MINIMAL_17x9[0], name="m17x9")),
            ("drawn_10x20", MOSPInstance.from_matrix(DRAWN_10x20, name="d10x20"))]
    return out


def corpus(sample_small, sample_large, seed):
    """Certified corpus instances; every one at >= 41 customers is a 128-bit-word check."""
    from learning.differential import corpus_targets
    rng = random.Random(seed)
    jobs = corpus_targets(max_customers=130)
    small = [j for j in jobs if j["matrix"] and len(j["matrix"]) <= 40]
    large = [j for j in jobs if len(j["matrix"]) > 40]
    pick = rng.sample(small, min(sample_small, len(small))) + rng.sample(large, min(sample_large, len(large)))
    for j in pick:
        n = len(j["matrix"])
        cap = 30_000 if n <= 40 else 10_000
        yield j["instance_name"], j["matrix"], j["optimum"], cap


def jobs(quick):
    rng = random.Random(20261002)
    for item in native_random(30 if quick else 400, 90):
        yield "native_random", item
    for item in pinned():
        yield "pinned", item
    for i in range(10 if quick else 400):
        yield "gadget", (f"gadget_{i}", _masks_instance(better_augment(rng), f"g{i}"))
    for i in range(10 if quick else 300):
        n = rng.randint(10, 24)
        masks = random_sparse(n, rng) if i % 2 else random_cover(n, rng)
        yield "random", (f"random_{i}", _masks_instance(masks, f"r{i}"))
    for item in corpus(10 if quick else 300, 5 if quick else 120, 7):
        yield "corpus", item


def run(quick=False, workers=16, out=REPORT):
    started = time.time()
    by = {}
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        for family, t in pool.imap_unordered(_job, list(jobs(quick)), chunksize=1):
            acc = by.setdefault(family, Counter())
            mx = max(acc.get("max_n", 0), t.pop("max_n", 0))
            acc.update(t)
            if mx:
                acc["max_n"] = mx
    total = Counter()
    for t in by.values():
        total.update({k: v for k, v in t.items() if k != "max_n"})
    report = dict(quick=quick, seconds=round(time.time() - started, 1),
                  families={f: dict(sorted(t.items())) for f, t in sorted(by.items())},
                  total=dict(sorted(total.items())))
    if not quick:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    report = run(args.quick, args.workers)
    print(json.dumps(report["total"], indent=1))
    for f, t in report["families"].items():
        print(f, {k: v for k, v in t.items() if k.startswith(("calls", "mismatch", "instances", "max_n"))})
    print("seconds", report["seconds"])


if __name__ == "__main__":
    main()
