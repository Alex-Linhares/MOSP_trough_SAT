"""Soundness of the fixed solver (loop0007 item 05).

Since 2026-10-01 both solvers apply the repaired rules by default
(`repaired_rules=True`, `paper2/solver_fix.md`). Item 01 checked the production
*filter* against the Lean `repairedFullFilter` node by node; this module checks
the production *search*, end to end, in four stages:

- `port` -- **the whole search, repaired, against the oracle.** `search_decide`
  of `paper2/search_check.py` is the §1.5 search ported from the document (free
  moves, memo, old move with inheritance, cost cut, filter, cost sort), and its
  node counts equal the C's under the published rules. `repaired_decide` below
  is the same port with the two repairs stated from the theorems, using the
  oracle's own predicates and nothing from `satisfiability/`:

  * the definite move picks the first playable `q` (index order) with
    `close >= open` *and* `IsHereditarilyDefinite` (`d_hereditary`, by
    enumeration of every intermediate set, not by a matching);
  * the better move cites `q` for `r` only under premises 3 and 4 *and*
    `q` hereditarily definite at `cl(S + r)` (`IsRepairedBetter`).

  At every `k` and every search configuration (each rule subset, better-move
  limit `L` in 0, 1, 2, old move and memo on and off) it checks: the port's
  answer equals `Sol_k(root)` (`tree_fail`); at every expanded node with a
  solution whose old-move set is genuinely refuted, the kept list holds a child
  with a solution (`node_loss`, *node soundness*); the C under
  `repaired_rules=True` returns the port's (answer, nodes) (`native_mismatch`);
  and the production Python, `decide(native=False, repaired_rules=True)`,
  returns the same answer and, where it runs the same search (not old move and
  memo together, which it does not combine), the same node count
  (`python_mismatch`). Satisfiable witnesses from the C are simulated.
  `differs_from_published` counts the runs where the published port
  (`search_check.search_decide`) gives a different (answer, nodes): the runs
  on which the comparison with the C can tell the two rule sets apart.

  Families: every labelled graph on 1-6 vertices, every graph on 7 (atlas)
  under the identity and four labellings, random sparse and cover graphs at
  8-13, the pinned counterexamples (both `DEFINITE_CEX`, Bug A, Bug B,
  `RUN_LOST_CEX`) at every `k`.

- `gadget` -- the same checks on the gadget family of
  `paper2/definite_hunt_gen.py` (family 4, where the definite move's
  counterexamples live) at 12-17 vertices, at `opt - 1`, `opt`, `opt + 1`,
  every configuration with the definite move on.

- `diff40`, `diff75` -- `learning.differential`'s check with the solver's
  defaults (now repaired) on every certified instance at n <= 40 (the corpus
  and the campaign) and at 50-75 (the campaign sample of `differential_scale`
  and the corpus): identity, relabellings and a re-covering, both
  configurations, `optimum - 1` expected `unsat` and `optimum` expected `sat`
  with the witness simulated. Written to `paper2/data/`, never over the
  committed `learning/data/ensemble/differential*`.

    python -m paper2.solver_fix_soundness --stage port --workers 12
    python -m paper2.solver_fix_soundness --stage gadget --workers 12
    python -m paper2.solver_fix_soundness --stage diff40 --workers 12
    python -m paper2.solver_fix_soundness --stage diff75 --workers 12
    python -m paper2.solver_fix_soundness --stage tables

Nothing here writes to `solutions/` or changes a default.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

from paper2.search_check import (
    BUG_A_CEX,
    BUG_B_CEX,
    DEFINITE_CEX,
    RUN_LOST_CEX,
    atlas_graphs,
    better_premise,
    bits,
    config_name,
    d_hereditary,
    inherit,
    labelled_graphs,
    matrix_from_masks,
    random_cover,
    random_sparse,
    relabel,
    s_searchsol_table,
    s_tables,
    search_decide,
    subset_pass,
)

DATA = Path(__file__).resolve().parent / "data"
LIMITS = (0, 1, 2)


# ----------------------------------------------------------------------------
# the repaired search, from the theorems
# ----------------------------------------------------------------------------


def repaired_filter(masks, O, CL, full, closed, Q, k, cfg):
    """One node of the repaired search: (P, L) as item lists (cost, customer)."""
    opened = O[closed]
    R = list(bits(full & ~closed))
    opens = {c: masks[c] & ~opened for c in R}
    open_now = (opened & ~closed).bit_count()
    K = [c for c in R if not (cfg["old_move"] and Q >> c & 1)]
    P = [(open_now + opens[c].bit_count(), c) for c in K if open_now + opens[c].bit_count() <= k]
    if not P or not (cfg["definite"] or cfg["subset"] or cfg["better"]):
        return P, list(P)
    if cfg["definite"]:
        for item in P:
            q = item[1]
            own = opens[q]
            close = sum(1 for d in R if opens[d] & ~own == 0)
            if close >= own.bit_count() and d_hereditary(masks, O, closed, q):
                return P, [item]
    L = list(P)
    if cfg["subset"]:
        L, _ = subset_pass(L, R, opens)
    if cfg["better"] and len(L) > 1:
        lim = len(L) if cfg["limit"] <= 0 or cfg["limit"] > len(L) else cfg["limit"]
        kept = []
        for ri, item in enumerate(L):
            r = item[1]
            cited = False
            for qi in range(min(lim, ri)):
                q = L[qi][1]
                if (better_premise(masks, full, closed, opened, k, r, q)
                        and d_hereditary(masks, O, CL[closed | 1 << r], q)):
                    cited = True
                    break
            if not cited:
                kept.append(item)
        L = kept
    return P, L


def repaired_decide(masks, k, cfg, O, CL, SS, t):
    """`search_check.search_decide` with the repaired filter, checked node by node against
    `SS` (`SearchSol`). Returns (answer, nodes)."""
    n = len(masks)
    full = (1 << n) - 1
    memo = set()
    nodes = 0

    def search(closed, seen):
        nonlocal nodes
        opened = O[closed]
        closed = CL[closed]                            # step 1, free moves
        if closed == full:
            return True
        if cfg["memo"] and closed in memo:             # step 2
            return False
        seen &= full & ~closed                         # step 3
        P, L = repaired_filter(masks, O, CL, full, closed, seen, k, cfg)
        if P:
            t["nodes_checked"] += 1
            q_ok = not (cfg["old_move"] and any(SS[CL[closed | 1 << q]] for q in bits(seen)))
            if not q_ok:
                t["nodes_q_not_refuted"] += 1
            elif SS[closed] and not any(SS[CL[closed | 1 << c]] for _, c in L):
                t["node_loss"] += 1
        L = sorted(L)                                  # step 6, cost then index
        for _, c in L:                                 # step 7
            nodes += 1
            inherited = inherit(masks, seen, closed, opened, c, k) if cfg["old_move"] and seen else 0
            if search(closed | 1 << c, inherited):
                return True
            seen |= 1 << c
        if cfg["memo"]:
            memo.add(closed)
        return False

    return search(0, 0), nodes


def search_configs(definite_only=False):
    out = []
    for definite in (False, True):
        if definite_only and not definite:
            continue
        for subset in (False, True):
            for better, limit in ((False, 0),) + tuple((True, L) for L in LIMITS):
                for old_move in (False, True):
                    for memo in (False, True):
                        out.append(dict(definite=definite, subset=subset, better=better,
                                        limit=limit, variant="fixed", old_move=old_move, memo=memo))
    return out


# ----------------------------------------------------------------------------
# the implementations
# ----------------------------------------------------------------------------


def _instance(masks):
    from mosp.instance import MOSPInstance
    return MOSPInstance.from_matrix(matrix_from_masks(masks), name="solver_fix_soundness")


def _kwargs(cfg):
    return dict(subset_rule=cfg["subset"], definite_move=cfg["definite"], old_move=cfg["old_move"],
                memo=cfg["memo"], better_move=cfg["better"], better_move_dominators=cfg["limit"],
                repaired_rules=True)


def _witness_ok(inst, order, k):
    from mosp.verify import max_open_stacks
    from satisfiability.heuristics import product_order_from_customers
    return order is not None and max_open_stacks(inst, product_order_from_customers(inst, order)) <= k


def check(masks, ks=None, configs=None, python=True):
    """Every stage-`port` check on one graph. Returns a Counter."""
    from satisfiability.customer_search import decide
    from satisfiability.native import decide_native

    n = len(masks)
    O, CL = s_tables(masks)
    inst = _instance(masks)
    t = Counter()
    configs = configs or CONFIGS
    for k in (range(1, n + 1) if ks is None else ks):
        SS = s_searchsol_table(masks, k, O, CL)
        truth = SS[0]
        t["sat_k" if truth else "unsat_k"] += 1
        for cfg in configs:
            name = config_name(cfg)
            ans, nodes = repaired_decide(masks, k, cfg, O, CL, SS, t)
            t["port_runs"] += 1
            if search_decide(masks, k, cfg) != (ans, nodes):
                t["differs_from_published"] += 1       # where the check can discriminate
            if ans != truth:
                t["tree_fail"] += 1
                t[f"tree_fail:{name}"] += 1
            d = decide_native(inst, k, **_kwargs(cfg))
            if d is not None:
                t["native_runs"] += 1
                if (d.status == "sat", d.nodes) != (ans, nodes):
                    t["native_mismatch"] += 1
                    t[f"native_mismatch:{name}"] += 1
                if d.status == "sat" and not _witness_ok(inst, d.order, k):
                    t["witness_fail"] += 1
            if python:
                p = decide(inst, k, native=False, **_kwargs(cfg))
                t["python_runs"] += 1
                if (p.status == "sat") != ans:
                    t["python_answer_mismatch"] += 1
                if not (cfg["old_move"] and cfg["memo"]):
                    t["python_node_runs"] += 1
                    if p.nodes != nodes:
                        t["python_mismatch"] += 1
                        t[f"python_mismatch:{name}"] += 1
    return t


CONFIGS = search_configs()
DEFINITE_CONFIGS = search_configs(definite_only=True)


def _job(args):
    kind, masks, ks, definite_only = args
    if ks == "around":
        O, CL = s_tables(masks)
        opt = next(k for k in range(len(masks) + 1) if s_searchsol_table(masks, k, O, CL)[0])
        ks = [k for k in (opt - 1, opt, opt + 1) if 1 <= k <= len(masks)]
    t = check(masks, ks=ks, configs=DEFINITE_CONFIGS if definite_only else CONFIGS)
    t["graphs"] = 1
    if t["tree_fail"] or t["node_loss"] or t["native_mismatch"] or t["python_mismatch"] \
            or t["python_answer_mismatch"] or t["witness_fail"]:
        t["flagged"] = 1
        return kind, t, {"masks": list(masks), "ks": None if ks is None else list(ks)}
    return kind, t, None


def port_jobs(seed=5):
    rng = random.Random(seed)
    for n in range(1, 7):
        for masks in labelled_graphs(n):
            yield ("labelled", masks, None, False)
    for masks in atlas_graphs(7):
        for i in range(5):
            perm = list(range(7)) if i == 0 else rng.sample(range(7), 7)
            yield ("atlas7", relabel(masks, perm), None, False)
    for i in range(1500):
        n = rng.randint(8, 13)
        masks = random_sparse(n, rng) if i % 2 else random_cover(n, rng)
        yield ("random", masks, None, False)
    pinned = [m for m, _, _, _ in DEFINITE_CEX] + [BUG_A_CEX[0], BUG_B_CEX[0], RUN_LOST_CEX[0]]
    for masks in pinned:
        yield ("pinned", list(masks), None, False)


def gadget_graphs(seed, count, lo=12, hi=17):
    out = subprocess.run([sys.executable, str(Path(__file__).with_name("definite_hunt_gen.py")),
                          str(seed), str(count), str(lo), str(hi), "4"],
                         capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        xs = list(map(int, line.split()))
        yield xs[1:1 + xs[0]]


def gadget_jobs(count=3000, seed=7):
    """`ks = "around"`: the worker finds the optimum and checks opt - 1, opt, opt + 1."""
    for masks in gadget_graphs(seed, count):
        yield ("gadget", masks, "around", True)


def run_checks(jobs, workers, out):
    started = time.time()
    by = {}
    flagged = []
    jobs = list(jobs)
    with Pool(workers) as pool:
        for i, (kind, t, ex) in enumerate(pool.imap_unordered(_job, jobs, chunksize=4)):
            by.setdefault(kind, Counter()).update(t)
            if ex is not None:
                flagged.append(dict(ex, kind=kind, tally={k: v for k, v in t.items() if ":" in k}))
            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{len(jobs)} graphs, {time.time() - started:.0f} s", flush=True)
    total = Counter()
    for t in by.values():
        total.update(t)
    clean = {k: v for k, v in total.items() if ":" not in k}
    report = {"seconds": round(time.time() - started, 1), "configs": len(CONFIGS),
              "total": clean, "by_family": {k: {a: b for a, b in v.items() if ":" not in a}
                                            for k, v in by.items()},
              "failures": sum(clean.get(k, 0) for k in ("tree_fail", "node_loss", "native_mismatch",
                                                         "python_mismatch", "python_answer_mismatch",
                                                         "witness_fail")),
              "flagged": flagged[:50]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    return report


# ----------------------------------------------------------------------------
# the differential harness, with the repaired defaults
# ----------------------------------------------------------------------------


def run_diff(stage, workers):
    import learning.differential as D
    if stage == "diff40":
        jobs = D.campaign_targets(max_customers=40) + D.corpus_targets(max_customers=40)
    else:
        from learning.differential_scale import targets
        jobs = [j for j in targets("all") if 50 <= int(j["n"]) <= 75]
    tag = stage
    D.run(jobs, workers=workers, relabellings=D.RELABELLINGS if stage == "diff40" else 4,
          deadline=60.0 if stage == "diff40" else 300.0,
          partial=DATA / f"solver_fix_{tag}_partial.csv",
          rows_csv=DATA / f"solver_fix_{tag}.csv.gz",
          summary_csv=DATA / f"solver_fix_{tag}_summary.csv",
          progress_every=2000 if stage == "diff40" else 100)
    (DATA / f"solver_fix_{tag}_partial.csv").unlink(missing_ok=True)


def tables():
    import pandas as pd
    out = []
    for stage in ("port", "gadget"):
        p = DATA / f"solver_fix_soundness_{stage}.json"
        if p.exists():
            r = json.loads(p.read_text())
            out.append(f"### {stage} ({r['seconds']} s)\n")
            out.append("| family | graphs | k values | port runs | nodes checked | node losses | "
                       "answer fails | C runs | C mismatches | Python runs | Python node mismatches | "
                       "witness fails | runs differing from the published port |")
            out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            fams = dict(r["by_family"], total=r["total"])
            for fam, t in fams.items():
                out.append(f"| {fam} | {t.get('graphs', 0):,} | {t.get('sat_k', 0) + t.get('unsat_k', 0):,} | "
                           f"{t.get('port_runs', 0):,} | {t.get('nodes_checked', 0):,} | {t.get('node_loss', 0)} | "
                           f"{t.get('tree_fail', 0)} | {t.get('native_runs', 0):,} | "
                           f"{t.get('native_mismatch', 0)} | {t.get('python_runs', 0):,} | "
                           f"{t.get('python_mismatch', 0) + t.get('python_answer_mismatch', 0)} | "
                           f"{t.get('witness_fail', 0)} | {t.get('differs_from_published', 0):,} |")
            out.append("")
    for stage in ("diff40", "diff75"):
        s = DATA / f"solver_fix_{stage}_summary.csv"
        rows = DATA / f"solver_fix_{stage}.csv.gz"
        if not s.exists():
            continue
        summ = pd.read_csv(s, low_memory=False)
        r = pd.read_csv(rows, low_memory=False)
        out.append(f"### {stage}\n")
        out.append("| source | instances | n range | calls | censored | disagreements | contradictions | "
                   "witness fails | oracle checked | oracle mismatches |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        for src, g in list(summ.groupby("source")) + [("total", summ)]:
            rr = r[r.base_name.isin(g.base_name)] if src == "total" else r[r.source == src]
            calls = int((rr.status_lo != "trivial").sum() + len(rr))
            cens = int((rr.status_lo == "unknown").sum() + (rr.status_hi == "unknown").sum())
            orc = g.oracle_ok.notna().sum()
            bad = int((g.oracle_ok == False).sum() + (g.oracle_recover_ok == False).sum())  # noqa: E712
            out.append(f"| {src} | {len(g):,} | {int(g.n.min())}-{int(g.n.max())} | {calls:,} | {cens} | "
                       f"{int(g.disagreement.sum())} | {int(g.contradiction.sum())} | "
                       f"{int(g.witness_failures.sum())} | {int(orc):,} | {bad} |")
        out.append("")
    text = "\n".join(out)
    (DATA / "solver_fix_soundness_tables.md").write_text(text)
    print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=("port", "gadget", "diff40", "diff75", "tables"), required=True)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--count", type=int, default=3000, help="gadget graphs")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    if args.stage == "port":
        jobs = list(port_jobs())
        if args.quick:
            jobs = [j for j in jobs if j[0] != "random" and len(j[1]) <= 5] + \
                   [j for j in jobs if j[0] in ("random", "pinned")][:20]
        r = run_checks(jobs, args.workers, DATA / "solver_fix_soundness_port.json")
        print(json.dumps({k: r[k] for k in ("seconds", "total", "failures")}, indent=1))
    elif args.stage == "gadget":
        r = run_checks(gadget_jobs(args.count), args.workers, DATA / "solver_fix_soundness_gadget.json")
        print(json.dumps({k: r[k] for k in ("seconds", "total", "failures")}, indent=1))
    elif args.stage in ("diff40", "diff75"):
        run_diff(args.stage, args.workers)
    else:
        tables()


if __name__ == "__main__":
    main()
