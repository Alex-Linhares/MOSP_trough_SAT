"""The repaired rules in the pathwidth solver (loop0007 item 03).

`pathwidth_solver/pathwidth/` is the MOSP customer search on graph masks. On
2026-10-01 it gained `repaired_rules` in all three implementations:

- `search.py`, the Python reference, which also gained a port of the better
  move (before, `better_move` was ignored on the Python path);
- `closing_search.c`, the 128-bit legacy C, again a byte copy of MOSP's
  `satisfiability/customer_search.c` (entry point `cs_decide_rules`);
- `closing_search_w.c`, the multiword C, built for 2, 4, 8 and 16 words
  (`csw_decide` gained the parameter).

This module runs the same decision through every one of them and through
MOSP's Python and C (the instance rebuilt from the masks by
`matrix_from_masks`), and requires equal status, node count and closing order
on every call, under both settings. Item 01 checked MOSP's Python against the
independent oracle at every node, and item 02 checked MOSP's C against MOSP's
Python, so equality here carries both checks over to the pathwidth solver.

Implementations compared on each call:

- `pw_py`: `pathwidth.search.decide(native=False)`;
- `pw_w2`, `pw_w4`, `pw_w8`, `pw_w16`: the multiword C at each word count,
  called directly, so every build runs on graphs that fit the smallest;
- `pw_legacy`: the 128-bit C (graphs of at most 128 vertices);
- `mosp_py`, `mosp_c`: MOSP's `customer_search.decide`, Python and C.

Configurations as in `paper2/solver_fix_c_check.py`: subset rule and definite
move on or off, better move off or on with dominator limit 0, 1 or 4, and old
move / memo in the three settings the C and the Python run identically; a
fan-order and a restricted-frontier setting besides. Families: the
`tests/test_native.py` random graphs (4-14 vertices), the pinned
counterexamples, gadgets at 14-17, random sparse and cover graphs at 10-24,
certified corpus instances at 9-125 (under node caps), and sparse random
graphs at 129-1000 vertices for the wide builds (C against the Python only).

    python -m paper2.solver_fix_pw_check --workers 20   # writes paper2/data/solver_fix_pw_check.json
    python -m paper2.solver_fix_pw_check --quick
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import random
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pathwidth_solver"))

import networkx as nx  # noqa: E402

from mosp.instance import MOSPInstance  # noqa: E402
from paper2.search_check import (  # noqa: E402
    BUG_A_CEX,
    BUG_B_CEX,
    DEFINITE_CEX,
    RUN_LOST_CEX,
    better_augment,
    matrix_from_masks,
    random_cover,
    random_sparse,
)
from paper2.solver_fix_c_check import BUG_B_10, FULL  # noqa: E402
from pathwidth import native as pw_native  # noqa: E402
from pathwidth.graph import masks_from_graph  # noqa: E402
from pathwidth.search import Decision, decide as pw_decide  # noqa: E402
from satisfiability.customer_search import decide as mosp_decide  # noqa: E402

REPORT = Path(__file__).resolve().parent / "data" / "solver_fix_pw_check.json"

CORPUS = [dict(subset_rule=True, definite_move=True, better_move=b,
               better_move_dominators=L, old_move=o, memo=m)
          for b, L in ((False, 4), (True, 0), (True, 4)) for o, m in ((True, False), (False, True))]
WIDE = [dict(subset_rule=True, definite_move=True, better_move=b,
             better_move_dominators=4, old_move=o, memo=m)
        for b in (False, True) for o, m in ((True, False), (False, True))]


def _word_build(masks, k, words, **flags) -> Decision | None:
    lib = pw_native._load(words)
    if lib is None or len(masks) > 64 * words:
        return None
    flags.setdefault("restrict", False)
    for name, default in (("subset_rule", True), ("definite_move", True), ("old_move", True),
                          ("memo", True), ("better_move", False), ("better_move_dominators", 4),
                          ("max_nodes", None), ("seconds", None), ("memo_limit", 4_000_000),
                          ("fan_order", "index"), ("repaired_rules", False)):
        flags.setdefault(name, default)
    if not any(masks):
        return Decision("sat", [], 0)
    return pw_native._call(lib.csw_decide, len(masks), k, pw_native._pack(masks, words), **flags)


def run_all(masks, k, cfg, repaired, max_nodes, instance=None, mosp=True):
    """Every implementation's (status, nodes, order over active vertices)."""
    active = {v for v, m in enumerate(masks) if m}

    def key(d):
        if d is None:
            return None
        order = None if d.order is None else [x for x in d.order if x in active]
        return (d.status, d.nodes, order)

    flags = dict(cfg, repaired_rules=repaired, max_nodes=max_nodes)
    out = {"pw_py": key(pw_decide(masks, k, native=False, **flags))}
    for w in pw_native.WORD_SIZES:
        if len(masks) <= 64 * w:
            out[f"pw_w{w}"] = key(_word_build(masks, k, w, **flags))
    if len(masks) <= 128:
        out["pw_legacy"] = key(pw_native.decide_native(masks, k, legacy=True, **flags))
    if mosp and instance is not None:
        out["mosp_py"] = key(mosp_decide(instance, k, native=False, **flags))
        out["mosp_c"] = key(mosp_decide(instance, k, native=True, **flags))
    return out


def compare(masks, ks, configs, max_nodes, instance=None, mosp=True, name="") -> Counter:
    t = Counter()
    for k in ks:
        for cfg in configs:
            seen = {}
            for repaired in (False, True):
                tag = "repaired" if repaired else "old"
                got = run_all(masks, k, cfg, repaired, max_nodes, instance, mosp)
                ref = got["pw_py"]
                t[f"calls_{tag}"] += 1
                t[f"impl_calls_{tag}"] += len(got)
                t[f"nodes_{tag}"] += ref[1]
                t[f"{ref[0]}_{tag}"] += 1
                bad = [impl for impl, v in got.items() if v != ref]
                if bad:
                    t[f"mismatch_{tag}"] += 1
                    for impl in bad:
                        t[f"mismatch_{impl}"] += 1
                    if t["examples"] < 5:
                        t["examples"] += 1
                        print("MISMATCH", name, k, cfg, repaired, got, flush=True)
                seen[repaired] = ref
            old, rep = seen[False], seen[True]
            t["settings_nodes_differ"] += old[1] != rep[1]
            if "unknown" not in (old[0], rep[0]) and not cfg.get("restrict"):
                t["settings_answer_differ"] += old[0] != rep[0]
    return t


def _instance(masks, name):
    return MOSPInstance.from_matrix(matrix_from_masks(masks), name=name)


def _job(args):
    family, name, payload = args
    t = Counter()
    if family == "corpus":
        matrix, opt, cap = payload
        from satisfiability.heuristics import _neighbour_masks
        inst = MOSPInstance.from_matrix(matrix, name=name)
        masks = _neighbour_masks(inst)
        t.update(compare(masks, [opt - 1, opt], CORPUS, cap, inst, name=name))
        n = inst.n_customers
    elif family == "wide":
        masks, ks = payload
        t.update(compare(masks, ks, WIDE, 5_000, mosp=False, name=name))
        n = len(masks)
    else:
        masks = payload
        n = len(masks)
        t.update(compare(masks, range(0, n + 2), FULL, 200_000, _instance(masks, name), name=name))
    t["instances"] += 1
    t["max_n"] = n
    return family, t


def native_random(count, seed):
    """The generator of `pathwidth_solver/tests/test_native.py`."""
    rng = random.Random(seed)
    for i in range(count):
        n = rng.randint(4, 14)
        G = nx.gnp_random_graph(n, rng.uniform(0.15, 0.8), seed=rng.randint(0, 10**6))
        masks, _ = masks_from_graph(G)
        yield f"native_random_{i}", masks


def pinned():
    from satisfiability.heuristics import _neighbour_masks
    from tests.test_customer_search import MINIMAL_10x13, MINIMAL_17x9
    from tests.test_differential import DRAWN_10x20
    out = [(f"definite_cex_{i}", m) for i, (m, _, _, _) in enumerate(DEFINITE_CEX)]
    out += [("bug_a", BUG_A_CEX[0]), ("bug_b_8", BUG_B_CEX[0]), ("bug_b_10", BUG_B_10),
            ("run_lost", RUN_LOST_CEX[0])]
    for name, matrix in (("minimal_10x13", MINIMAL_10x13[0]), ("minimal_17x9", MINIMAL_17x9[0]),
                         ("drawn_10x20", DRAWN_10x20)):
        out.append((name, _neighbour_masks(MOSPInstance.from_matrix(matrix, name=name))))
    return out


def corpus(sample_small, sample_large, seed):
    from learning.differential import corpus_targets
    rng = random.Random(seed)
    jobs = corpus_targets(max_customers=130)
    small = [j for j in jobs if j["matrix"] and len(j["matrix"]) <= 40]
    large = [j for j in jobs if len(j["matrix"]) > 40]
    pick = rng.sample(small, min(sample_small, len(small))) + rng.sample(large, min(sample_large, len(large)))
    for j in pick:
        n = len(j["matrix"])
        yield j["instance_name"], (j["matrix"], j["optimum"], 30_000 if n <= 40 else 10_000)


def wide(count, seed):
    """Sparse random graphs sized for the 4-, 8- and 16-word builds."""
    rng = random.Random(seed)
    for i in range(count):
        words = (4, 8, 16)[i % 3]
        n = rng.randint(64 * words // 2 + 1, min(1000, 64 * words))
        G = nx.gnp_random_graph(n, rng.choice((1.5, 2.2, 3.0)) / n, seed=rng.randint(0, 10**6))
        masks, _ = masks_from_graph(G)
        k = max(2, int(n ** 0.5) // 2)
        yield f"wide_{words}_{i}", (masks, [k, k + 2, k + 6])


def jobs(quick):
    rng = random.Random(20261003)
    for name, masks in native_random(30 if quick else 400, 11):
        yield "native_random", name, masks
    for name, masks in pinned():
        yield "pinned", name, masks
    for i in range(10 if quick else 300):
        yield "gadget", f"gadget_{i}", better_augment(rng)
    for i in range(10 if quick else 300):
        n = rng.randint(10, 24)
        yield "random", f"random_{i}", random_sparse(n, rng) if i % 2 else random_cover(n, rng)
    for name, payload in corpus(10 if quick else 200, 5 if quick else 80, 8):
        yield "corpus", name, payload
    for name, payload in wide(3 if quick else 30, 9):
        yield "wide", name, payload


def run(quick=False, workers=16, out=REPORT):
    started = time.time()
    by = {}
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        for family, t in pool.imap_unordered(_job, list(jobs(quick)), chunksize=1):
            acc = by.setdefault(family, Counter())
            mx = max(acc.get("max_n", 0), t.pop("max_n", 0))
            acc.update(t)
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
