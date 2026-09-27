"""Is the two-key rule the literature's MCNh under another name? (loop0004
item 02, `reports/ml_nature_plan_3.md` Q6b; `reports/ml_nature.md` §29)

Question. Becceneri, Yanasse & Soma (2004) state the Minimal Cost Node
heuristic (MCNh) as an *arc traversal* of the MOSP graph; our `mcn` in
`satisfiability/heuristics.py` is a node-closing reading of Yanasse & Senne
(2010)'s one-sentence summary and never reproduced the published MCNh
numbers. Item 02 implements the 2004 pseudocode as `mcnh` (registered, the
default of nothing), checks it against the paper's worked example, compares
it with Frinhani et al. (2018)'s MCNh column on the Challenge instances and
their SCOOP figure, scores it against `mcn` and the two-key `rule` over the
whole corpus, and asks whether the rule and MCNh are the same heuristic: per
instance (same value, same closing order) and per step (is MCNh's closing
decision the one the rule's keys would take from the same state?).

Method. Every certified corpus instance (6,376 at 9–134 customers; optima
read from `solutions/`, never written) is run through `mcnh`, `mcnh-arcs`
(the same traversal with a pattern sequenced when its last own arc is
traversed rather than when all its pieces have been opened), `mcn` and
`rule`, in-process with `perf_counter` around each call. MCNh's closing order
is the one its pattern sequence induces (customers by last product). Per-step
agreement is measured along MCNh's own closing order: at each step with more
than one unclosed customer, whether MCNh's pick attains the rule's first key
(fewest newly opened stacks), both keys, and MCN's key (fewest unclosed
neighbours). No split is needed: nothing is fitted.

Not a bound, not a solver change. `_lower_bound` is untouched, no default
changes, nothing is written to `solutions/`.

Run:
    python -m learning.mcnh                    # all stages, ~2 min on 16 workers
    python -m learning.mcnh --stage paper      # the 2004 example, loop by loop
    python -m learning.mcnh --stage corpus     # the sweep -> learning/data/mcnh/corpus.csv
    python -m learning.mcnh --stage report     # tables from what is on disk
    python -m pytest tests/test_mcnh.py -q

Writes `learning/data/mcnh/corpus.csv` (git-ignored, regenerable) and
`reports/mcnh_tables.md` (committed).
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from learning.dataset import enumerate_instances
from mosp.instance import MOSPInstance
from mosp.verify import count_open_stacks
from satisfiability.mosp_solver import _solution_path

OUT_DIR = Path("learning/data/mcnh")
CORPUS_CSV = OUT_DIR / "corpus.csv"
TABLES = Path("reports/mcnh_tables.md")
SOLUTIONS = Path("solutions")

STRATEGIES = ("mcnh", "mcnh-arcs", "mcn", "rule")
BANDS = ((9, 30), (31, 60), (61, 134))

# Becceneri, Yanasse & Soma (2004), Table 1 (patterns × pieces) and what §4
# prints for it: the arc per loop, ARC, ξ, the pattern sequence, Fig. 2.
BYS2004_PATTERNS = [
    [1, 1, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1],
]
BYS2004 = MOSPInstance.from_matrix(
    np.array(BYS2004_PATTERNS).T.tolist(), name="becceneri-2004-table-1")
BYS2004_LOOP_ARCS = [(4, 8), (4, 6), (4, 1), (6, 5), (1, 3), (3, 2), (1, 7)]   # 1-based
BYS2004_ARC = [(4, 8), (4, 6), (6, 8), (1, 4), (1, 6), (1, 8), (6, 5), (1, 5),
               (1, 3), (3, 5), (3, 2), (1, 2), (2, 5), (1, 7), (2, 7), (5, 7)]
BYS2004_SEQUENCE = [11, 10, 14, 2, 4, 6, 12, 3, 9, 1, 7, 5, 8, 13]           # 1-based
BYS2004_FIG2 = [2, 3, 3, 4, 3, 3, 3, 2, 3, 4, 3, 4, 3, 2]
BYS2004_XI = 4
# after loops 1, 2, 3: (s, ξ, OPEN, SETV) as printed on pp. 2319–2320
BYS2004_STATES = [
    (1, 2, [4, 8], [4, 8, 3, 7, 2, 6, 5, 1]),
    (3, 3, [4, 6, 8], [4, 8, 6, 3, 7, 2, 5, 1]),
    (6, 4, [1, 6], [6, 3, 7, 1, 2, 5]),
]

# Frinhani et al. (2018), Table 2: the MCNh column (their code was Carvalho's
# reimplementation, not the 2004 authors'). Shaw is the mean over 25 files.
FRINHANI_MCNH = {
    "GP1": 45, "GP2": 40, "GP3": 40, "GP4": 30, "GP5": 96, "GP6": 75, "GP7": 75,
    "GP8": 60, "Miller": 13, "NWRS1": 3, "NWRS2": 4, "NWRS3": 7, "NWRS4": 7,
    "NWRS5": 12, "NWRS6": 12, "NWRS7": 10, "NWRS8": 16, "SP1": 9, "SP2": 23,
    "SP3": 37, "SP4": 57,
}
FRINHANI_SHAW_MEAN = 14.00
# Frinhani et al. (2018), Fig. 6 (SCOOP, 24 instances): MCNh optimal on 33%,
# no instance in 1–10%, 29% in 11–25%, 38% above 25%; total gap 25.27% over a
# total optimum of 186; the labelled gaps, read off the figure.
FRINHANI_SCOOP = {
    "optimal": 8, "gap_1_10": 0, "gap_11_25": 7, "gap_over_25": 9,
    "total_optimum": 186, "total_gap_pct": 25.27,
    "labelled_gaps": [60.00, 57.14, 47.06, 45.00, 44.44, 38.46, 36.36, 33.33,
                      33.33, 20.00, 18.18, 16.67, 16.67, 16.67, 16.67, 11.11],
}


# ----------------------------------------------------------------------------
# the paper's example
# ----------------------------------------------------------------------------

def paper_check(verbose: bool = True) -> dict:
    """Run `mcnh_trace` on Table 1 and compare with everything §4 prints."""
    from satisfiability.heuristics import mcnh_trace, patterns_from_arcs

    trace = mcnh_trace(BYS2004)
    loop_arcs = [(L["n1"] + 1, L["n2"] + 1) for L in trace["loops"]]
    arcs = [(a + 1, b + 1) for a, b in trace["arcs"]]   # the paper's orientation varies: (4,1) is printed (1,4), (6,5) as (6,5)
    states = [(L["s"], L["xi"], [c + 1 for c in L["open"]], [c + 1 for c in L["setv"]])
              for L in trace["loops"][:3]]
    result = {"loops": len(trace["loops"]), "xi": trace["xi"],
              "loop_arcs_match": loop_arcs == BYS2004_LOOP_ARCS,
              "arc_match": [frozenset(a) for a in arcs] == [frozenset(a) for a in BYS2004_ARC],
              "states_match": states == BYS2004_STATES}
    for rule in ("nodes", "arcs"):
        seq = [p + 1 for p in patterns_from_arcs(BYS2004, trace["arcs"], rule)]
        profile = count_open_stacks(BYS2004, [p - 1 for p in seq])
        result[f"sequence_match:{rule}"] = seq == BYS2004_SEQUENCE
        result[f"fig2_match:{rule}"] = profile == BYS2004_FIG2
        result[f"sequence:{rule}"] = seq
    if verbose:
        print("Becceneri, Yanasse & Soma (2004) §4, Table 1:")
        for i, L in enumerate(trace["loops"], start=1):
            print(f"  loop {i}: arc ({L['n1'] + 1},{L['n2'] + 1})  s={L['s']:2d}  "
                  f"xi={L['xi']}  OPEN={[c + 1 for c in L['open']]}  "
                  f"SETV={[c + 1 for c in L['setv']]}")
        print(f"  ARC = {arcs}")
        print(f"  sequence (nodes rule) = P{result['sequence:nodes']}")
        print(f"  profile = {count_open_stacks(BYS2004, [p - 1 for p in result['sequence:nodes']])}")
        print(f"  checks: {json.dumps({k: v for k, v in result.items() if not k.startswith('sequence:')})}")
    return result


# ----------------------------------------------------------------------------
# the corpus
# ----------------------------------------------------------------------------

def _rule_keys(masks, pmasks, opened, closed, produced, c):
    return ((masks[c] & ~opened).bit_count(),
            -((masks[c] & ~closed).bit_count() - 1),
            (pmasks[c] & ~produced).bit_count(), c)


def step_agreement(instance: MOSPInstance, closing_order: Sequence[int]) -> dict:
    """Along `closing_order`, at every step with more than one unclosed
    customer: does the pick attain the two-key rule's first key, both keys,
    and MCN's key (fewest unclosed neighbours)? Returns counts."""
    from satisfiability.heuristics import _neighbour_masks

    masks = _neighbour_masks(instance)
    n = instance.n_customers
    pmasks = [0] * n
    for c in range(n):
        for p in instance.customer_patterns(c):
            pmasks[c] |= 1 << p
    remaining = [c for c in range(n) if masks[c]]
    closed = opened = produced = 0
    steps = key1 = both = mcn_key = 0
    for pick in closing_order:
        if pick not in remaining:
            continue
        if len(remaining) > 1:
            keys = {c: _rule_keys(masks, pmasks, opened, closed, produced, c)
                    for c in remaining}
            min1 = min(k[0] for k in keys.values())
            min12 = min(k[:2] for k in keys.values())
            degrees = {c: (masks[c] & ~closed).bit_count() for c in remaining}
            mind = min(degrees.values())
            steps += 1
            key1 += keys[pick][0] == min1
            both += keys[pick][:2] == min12
            mcn_key += degrees[pick] == mind
        opened |= masks[pick]
        closed |= 1 << pick
        produced |= pmasks[pick]
        remaining.remove(pick)
    return {"steps": steps, "agree_key1": key1, "agree_both": both,
            "agree_mcn_key": mcn_key}


def _one(task) -> dict:
    from satisfiability.heuristics import (
        _customer_order_from_products, two_key_closing_order, upper_bound)

    source_file, name, n, m, matrix, optimum = task
    inst = MOSPInstance(matrix=np.array(matrix, dtype=np.int8),
                        n_customers=n, n_patterns=m, name=name)
    parts = Path(source_file).parts
    row = {"instance": name, "source_file": source_file,
           "collection": "/".join(parts[2:4]), "stem": Path(source_file).stem,
           "n_customers": n, "n_patterns": m, "optimum": optimum}
    orderings = {}
    for strategy in STRATEGIES:
        started = time.perf_counter()
        value, ordering = upper_bound(inst, strategy)
        row[f"ms:{strategy}"] = 1000.0 * (time.perf_counter() - started)
        row[f"value:{strategy}"] = value
        orderings[strategy] = ordering
    row["same_sequence:mcnh,mcnh-arcs"] = orderings["mcnh"] == orderings["mcnh-arcs"]
    mcnh_closing = _customer_order_from_products(inst, orderings["mcnh"])
    rule_closing = two_key_closing_order(inst)
    row["same_closing:mcnh,rule"] = mcnh_closing == rule_closing
    row["same_sequence:mcnh,rule"] = orderings["mcnh"] == orderings["rule"]
    row["positional_agreement:mcnh,rule"] = (
        sum(a == b for a, b in zip(mcnh_closing, rule_closing)) / max(1, len(rule_closing)))
    row.update(step_agreement(inst, mcnh_closing))
    return row


def run_corpus(workers: int = 16, limit: int | None = None,
               out: Path = CORPUS_CSV) -> pd.DataFrame:
    tasks = []
    for path, inst in enumerate_instances():
        solution = _solution_path(inst, SOLUTIONS)
        if not solution.exists():
            continue
        optimum = int(json.loads(solution.read_text())["mosp_value"])
        tasks.append((str(path), inst.name, inst.n_customers, inst.n_patterns,
                      inst.matrix.tolist(), optimum))
    if limit:
        tasks = tasks[:limit]
    started = time.time()
    with multiprocessing.Pool(workers) as pool:
        rows = pool.map(_one, tasks, chunksize=8)
    frame = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    print(f"{len(frame)} instances × {len(STRATEGIES)} strategies in "
          f"{time.time() - started:.0f}s -> {out}", flush=True)
    return frame


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------

def _score(frame: pd.DataFrame, strategy: str) -> dict:
    over = frame[f"value:{strategy}"] - frame["optimum"]
    return {"strategy": strategy, "instances": len(frame),
            "MAE": over.mean(), "exact": (over == 0).mean(),
            "worst": int(over.max()), "total over": int(over.sum()),
            "ms": frame[f"ms:{strategy}"].mean()}


def _md(frame: pd.DataFrame, floats: dict[str, str] | None = None) -> str:
    floats = floats or {}
    cols = list(frame.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in frame.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in floats:
                cells.append(format(v, floats[c]))
            elif isinstance(v, float):
                cells.append(f"{v:,.3f}")
            elif isinstance(v, (int, np.integer)):
                cells.append(f"{v:,}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


FMT = {"MAE": ".3f", "exact": ".1%", "ms": ".2f"}


def _head_to_head(frame: pd.DataFrame, pairs) -> pd.DataFrame:
    rows = []
    for a, b in pairs:
        d = frame[f"value:{a}"] - frame[f"value:{b}"]
        rows.append({"first": a, "second": b, "better": int((d < 0).sum()),
                     "equal": int((d == 0).sum()), "worse": int((d > 0).sum())})
    return pd.DataFrame(rows)


def build_tables(frame: pd.DataFrame, paper: dict) -> str:
    out = ["# MCNh (2004) against `mcn` and the two-key rule: tables\n",
           "*Written by `python -m learning.mcnh --stage report`; every table "
           "of `reports/ml_nature.md` §29 in full. Over the optimum, "
           f"{len(frame):,} certified instances at "
           f"{frame.n_customers.min()}–{frame.n_customers.max()} customers.*\n"]

    out.append("## The paper's example\n")
    out.append("```\n" + json.dumps(paper, indent=1) + "\n```\n")

    out.append("## Over the optimum, whole corpus\n")
    out.append(_md(pd.DataFrame([_score(frame, s) for s in STRATEGIES]), FMT) + "\n")

    out.append("## By size band\n")
    rows = []
    for lo, hi in BANDS:
        part = frame[(frame.n_customers >= lo) & (frame.n_customers <= hi)]
        r = {"customers": f"{lo}–{hi}", "instances": len(part)}
        for s in STRATEGIES:
            over = part[f"value:{s}"] - part.optimum
            r[f"MAE {s}"] = over.mean()
            r[f"exact {s}"] = (over == 0).mean()
        rows.append(r)
    fmt = {**{f"MAE {s}": ".3f" for s in STRATEGIES},
           **{f"exact {s}": ".1%" for s in STRATEGIES}}
    out.append(_md(pd.DataFrame(rows), fmt) + "\n")

    out.append("## By collection\n")
    rows = []
    for coll, part in frame.groupby("collection"):
        r = {"collection": coll, "instances": len(part)}
        for s in STRATEGIES:
            r[f"MAE {s}"] = (part[f"value:{s}"] - part.optimum).mean()
        rows.append(r)
    out.append(_md(pd.DataFrame(rows), {f"MAE {s}": ".3f" for s in STRATEGIES}) + "\n")

    out.append("## Head to head (instances where the first is below / equal / above the second)\n")
    out.append(_md(_head_to_head(frame, [("mcnh", "mcn"), ("mcnh", "rule"),
                                         ("mcnh", "mcnh-arcs"), ("rule", "mcn")])) + "\n")

    out.append("## Is the rule MCNh under another name?\n")
    agree = {
        "instances": len(frame),
        "same value (mcnh = rule)": int((frame["value:mcnh"] == frame["value:rule"]).sum()),
        "same closing order": int(frame["same_closing:mcnh,rule"].sum()),
        "same pattern sequence": int(frame["same_sequence:mcnh,rule"].sum()),
        "mean positional agreement of closing orders": frame["positional_agreement:mcnh,rule"].mean(),
        "steps with a choice": int(frame.steps.sum()),
        "MCNh pick attains rule key 1": frame.agree_key1.sum() / frame.steps.sum(),
        "MCNh pick attains rule keys 1+2": frame.agree_both.sum() / frame.steps.sum(),
        "MCNh pick attains MCN key (min degree)": frame.agree_mcn_key.sum() / frame.steps.sum(),
        "mcnh = mcnh-arcs sequence": int(frame["same_sequence:mcnh,mcnh-arcs"].sum()),
        "mcnh = mcnh-arcs value": int((frame["value:mcnh"] == frame["value:mcnh-arcs"]).sum()),
    }
    out.append(_md(pd.DataFrame([{"quantity": k, "value": v} for k, v in agree.items()])) + "\n")
    rows = []
    for lo, hi in BANDS:
        part = frame[(frame.n_customers >= lo) & (frame.n_customers <= hi)]
        rows.append({"customers": f"{lo}–{hi}", "instances": len(part),
                     "steps": int(part.steps.sum()),
                     "key 1": part.agree_key1.sum() / max(1, part.steps.sum()),
                     "keys 1+2": part.agree_both.sum() / max(1, part.steps.sum()),
                     "MCN key": part.agree_mcn_key.sum() / max(1, part.steps.sum()),
                     "same closing order": part["same_closing:mcnh,rule"].mean()})
    out.append(_md(pd.DataFrame(rows), {"key 1": ".1%", "keys 1+2": ".1%",
                                        "MCN key": ".1%", "same closing order": ".1%"}) + "\n")

    out.append("## Frinhani et al. (2018) Table 2, MCNh column, against `mcnh` (MOSP_Instances/Challenge)\n")
    chal = frame[frame.collection == "MOSP_Instances/Challenge"].copy()
    rows = []
    for stem, published in FRINHANI_MCNH.items():
        r = chal[chal.stem == stem]
        if len(r) != 1:
            continue
        r = r.iloc[0]
        rows.append({"instance": stem, "OPT": int(r.optimum), "Frinhani MCNh": published,
                     "mcnh": int(r["value:mcnh"]), "mcnh-arcs": int(r["value:mcnh-arcs"]),
                     "mcn": int(r["value:mcn"]), "rule": int(r["value:rule"])})
    shaw = chal[chal.stem.str.startswith("Shaw")]
    rows.append({"instance": f"Shaw (mean of {len(shaw)})", "OPT": round(shaw.optimum.mean(), 2),
                 "Frinhani MCNh": FRINHANI_SHAW_MEAN,
                 "mcnh": round(shaw["value:mcnh"].mean(), 2),
                 "mcnh-arcs": round(shaw["value:mcnh-arcs"].mean(), 2),
                 "mcn": round(shaw["value:mcn"].mean(), 2),
                 "rule": round(shaw["value:rule"].mean(), 2)})
    table = pd.DataFrame(rows)
    out.append(_md(table) + "\n")
    named = table[~table.instance.str.startswith("Shaw")]
    out.append(f"Named rows: `mcnh` equals Frinhani's MCNh on "
               f"{int((named.mcnh == named['Frinhani MCNh']).sum())} of {len(named)}, "
               f"below it on {int((named.mcnh < named['Frinhani MCNh']).sum())}, "
               f"above it on {int((named.mcnh > named['Frinhani MCNh']).sum())}; "
               f"sums {int(named.mcnh.sum())} against {int(named['Frinhani MCNh'].sum())} "
               f"(OPT {int(named.OPT.sum())}).\n")

    out.append("## Frinhani et al. (2018) Fig. 6, SCOOP: MCNh gap buckets\n")
    scoop = frame[frame.collection == "MOSP_Instances/SCOOP"].copy()
    if scoop.empty:
        scoop = frame.head(1).copy()   # a --limit run: keep the table well defined
    rows = []
    for s in ("mcnh", "mcnh-arcs", "mcn", "rule"):
        gap = 100.0 * (scoop[f"value:{s}"] - scoop.optimum) / scoop.optimum
        rows.append({"method": s, "instances": len(scoop),
                     "optimal": int((gap == 0).sum()),
                     "1–10%": int(((gap > 0) & (gap <= 10)).sum()),
                     "11–25%": int(((gap > 10) & (gap <= 25)).sum()),
                     ">25%": int((gap > 25).sum()),
                     "total value": int(scoop[f"value:{s}"].sum()),
                     "total gap %": 100.0 * (scoop[f"value:{s}"].sum() - scoop.optimum.sum()) / scoop.optimum.sum(),
                     "largest gap %": gap.max()})
    f = FRINHANI_SCOOP
    rows.append({"method": "Frinhani MCNh (Fig. 6)", "instances": 24, "optimal": f["optimal"],
                 "1–10%": f["gap_1_10"], "11–25%": f["gap_11_25"], ">25%": f["gap_over_25"],
                 "total value": round(f["total_optimum"] * (1 + f["total_gap_pct"] / 100)),
                 "total gap %": f["total_gap_pct"], "largest gap %": max(f["labelled_gaps"])})
    out.append(_md(pd.DataFrame(rows), {"total gap %": ".2f", "largest gap %": ".2f"}) + "\n")
    out.append(f"SCOOP total optimum here: {int(scoop.optimum.sum())} (Frinhani: {f['total_optimum']}).\n")
    gaps = sorted((100.0 * (scoop["value:mcnh"] - scoop.optimum) / scoop.optimum).round(2), reverse=True)
    out.append(f"`mcnh` gaps, sorted: {gaps}\n\nFrinhani's labelled MCNh gaps: "
               f"{sorted(f['labelled_gaps'], reverse=True)} plus {f['optimal']} zeros.\n")

    out.append("## Where `mcnh` and the rule differ most (over the optimum)\n")
    diff = frame.assign(d=frame["value:mcnh"] - frame["value:rule"])
    worst = pd.concat([diff.nlargest(8, "d"), diff.nsmallest(4, "d")])
    out.append(_md(worst[["instance", "n_customers", "optimum", "value:mcnh",
                          "value:mcn", "value:rule", "d"]]) + "\n")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=("paper", "corpus", "report", "all"), default="all")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    paper = None
    if args.stage in ("paper", "all", "report"):
        paper = paper_check(verbose=args.stage != "report")
    if args.stage in ("corpus", "all"):
        run_corpus(workers=args.workers, limit=args.limit)
    if args.stage in ("report", "all"):
        frame = pd.read_csv(CORPUS_CSV)
        text = build_tables(frame, paper)
        TABLES.write_text(text)
        print(text)
        print(f"-> {TABLES}")


if __name__ == "__main__":
    main()
