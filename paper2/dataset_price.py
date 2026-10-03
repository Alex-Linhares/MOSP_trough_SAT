"""Price of the full certification run for section 4's dataset (loop0008 item 04).

    python -m paper2.dataset price      # writes paper2/data/dataset/price.md
    python -m paper2.dataset tables     # writes paper2/data/dataset/tables.md (counts, dedupe, provenance)

Inputs, all on record: the dataset's class table (`classes.csv.gz`), the
index, the repaired-rules runs of `pathwidth_solver/bench/results/repaired/`
(seconds per graph), this item's run (`run.csv`), the split run's task file
(`paper2/data/solver_fix_split_tasks.csv`, read only), and the §19 cost model
(`learning/cost_model.py`) for the MOSP collections that were never certified.

Seconds are one core's wall time per instance, as `benchmarks.compute` counts
them; a core-hour is 3,600 of them. A censored call is a lower bound on its cost.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

from paper2.dataset import (CLASSES_CSV, COLLECTIONS, ENGINE_MAX, INDEX, IN_FLIGHT, OUT, PRIORITY,
                            REPAIRED, RESULT_SETS, ROOT, RUN_CSV, VALUES_CSV, classes, read_csv,
                            representative)

# solver_fix.md, item 07 table ("price (core-hours)"); the prices there are stated to be low.
ITEM07_PRICE = {"Random-125-125-2-1_0": "76.1", "Random-125-125-2-5_0": "116", "Random-125-125-4-4_0": "153"}
SPLIT_TASKS = ROOT / "paper2" / "data" / "solver_fix_split_tasks.csv"
SPLIT_RESULTS = ROOT / "paper2" / "data" / "solver_fix_split_results.csv"
PRICE_MD = OUT / "price.md"
TABLES_MD = OUT / "tables.md"
COST_PRED = OUT / "cost_model_mosp.csv"


def _f(x, nd=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, float):
        return f"{x:,.{nd}f}"
    return f"{x:,}"


def _md(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(header))) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Counts, deduplication and provenance
# ---------------------------------------------------------------------------

def tables() -> str:
    idx = read_csv(INDEX)
    cls_rows = read_csv(CLASSES_CSV)
    by_cls = {r["cls"]: r for r in cls_rows}
    by, vals = classes()
    lines = ["# Section 4's dataset: counts, deduplication, provenance", "",
             "Regenerate: `python -m paper2.dataset tables` (after `index`, `values`, `run`, `write`).", ""]
    # per collection before / after
    files = Counter(r["collection"] for r in idx)
    errors = Counter(r["collection"] for r in idx if r["error"])
    big = Counter(r["collection"] for r in idx if r["big"] == "1")
    distinct = defaultdict(set)
    for r in idx:
        if not r["error"]:
            distinct[r["collection"]].add(r["cls"])
    owned = Counter(by_cls[c]["owner"] for c in by_cls)
    rows = []
    for key, prob, _ in COLLECTIONS:
        sizes = [int(r["n"]) for r in idx if r["collection"] == key and r["n"]]
        rows.append([key, prob, _f(files[key]), _f(len(distinct[key])), _f(owned[key]),
                     f"{min(sizes)}–{max(sizes)}" if sizes else "—",
                     _f(big[key]) if big[key] else "", _f(errors[key]) if errors[key] else ""])
    rows.append(["**all**", "", _f(sum(files.values())), "", _f(len(by_cls)), "", _f(sum(big.values())),
                 _f(sum(errors.values()))])
    lines += ["## Instances per collection, before and after deduplication", "",
              "*files*: instances read; *distinct*: isomorphism classes within the collection; "
              "*new*: classes whose first member, in the order of this table, is in this collection "
              "(so the column sums to the dataset's class count); *n*: vertices of the graph "
              "(customers or nets for the matrix collections); *header only*: graphs above 5,000 "
              "vertices, deduplicated by exact file content, not by isomorphism.", "",
              _md(["collection", "problem", "files", "distinct", "new", "n", "header only", "unreadable"], rows), ""]
    # cross-collection overlap
    pairs = Counter()
    for c, members in by.items():
        colls = sorted({m["collection"] for m in members}, key=PRIORITY.get)
        if len(colls) > 1:
            pairs[" + ".join(colls)] += 1
    lines += ["## Classes shared between collections", "",
              _md(["collections", "classes"], [[k, v] for k, v in pairs.most_common()]) if pairs else "none", ""]
    # provenance by owner collection
    prov = defaultdict(Counter)
    for r in cls_rows:
        p = r["provenance"] or ("no value" if not r["width"] else "?")
        if r["width"] and not int(r["witness"]):
            p += " (no witness yet)"
        prov[r["owner"]][p] += 1
    kinds = ["certified:refutation", "certified:bound", "solution", "certified:refutation (no witness yet)",
             "certified:bound (no witness yet)", "solution (no witness yet)", "no value"]
    rows = [[k] + [_f(prov[k][p]) for p in kinds] for k, _, _ in COLLECTIONS]
    tot = Counter()
    for k in prov:
        tot.update(prov[k])
    rows.append(["**all**"] + [_f(tot[p]) for p in kinds])
    lines += ["## Provenance of each class, by the collection that owns it", "",
              "Classes, not files. A class's value is its best-established member's.", "",
              _md(["collection"] + kinds, rows), ""]
    lines += published_comparison()
    text = "\n".join(lines)
    TABLES_MD.write_text(text + "\n")
    return text


# Best known tracks of the VLSI circuits: Oliveira & Lorena (2002) Table I, as recorded
# in paper2/benchmarks/hunt_matrix.md (Gonçalves 2016 Table 9 gives the same values).
VLSI_BKS = dict(Wli=4, Wsn=8, v4000=5, v4050=5, v4090=10, V4470=9, X0=11, W1=4, W2=14, W3=18, W4=27)
MALLACH = ROOT / "literature" / "mallach_2018_linear_ordering_mip_vertex_separation_pathwidth.pdf"
CS_XLSX = ROOT / "paper2" / "benchmarks" / "raw" / "carvalho_soma2015" / \
    "PT-MOSP_reference_values_LARGER_AND_HARDER_RANDOM.xlsx"


def mallach_pw() -> dict[str, int]:
    """pw column of Mallach (2018), Tables 4-5 (pp. 165-166), via pdftotext."""
    import re
    import subprocess
    text = subprocess.run(["pdftotext", "-layout", str(MALLACH), "-"], capture_output=True, text=True).stdout
    out = {}
    for m in re.finditer(r"^\s*(p\d+_\d+_\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s", text, re.M):
        out[m.group(1)] = int(m.group(4))
    return out


def carvalho_soma_values() -> dict[str, int]:
    import openpyxl
    wb = openpyxl.load_workbook(CS_XLSX, read_only=True)
    out = {}
    for ws in wb:
        for row in list(ws.iter_rows(values_only=True))[1:]:
            if row and row[0] and isinstance(row[1], (int, float)):
                out.setdefault(str(row[0]), int(row[1]))
    return out


def published_comparison() -> list[str]:
    """Certified widths of this item's run against the values the sources publish."""
    by, vals = classes()
    cls_of = {(m["source"], m["name"]): c for c, ms in by.items() for m in ms}
    rows = {r["cls"]: r for r in read_csv(CLASSES_CSV)}
    def ours(m):
        r = rows[cls_of[(m["source"], m["name"])]]
        return (int(r["width"]) if r["width"] else None), r["provenance"]
    idx = [r for r in read_csv(INDEX) if not r["error"]]
    lines = ["## Against published values", ""]
    # VLSI
    t = []
    for m in sorted((r for r in idx if r["collection"] == "VLSI gate matrix circuits"), key=lambda r: r["name"]):
        w, p = ours(m)
        t.append([m["name"], m["n"], VLSI_BKS[m["name"]], "—" if w is None else w + 1, p or "—"])
    lines += ["VLSI circuits, tracks (= pathwidth + 1 of the net graph). Best known from Oliveira & "
              "Lorena (2002) Table I as recorded in `benchmarks/hunt_matrix.md`.", "",
              _md(["circuit", "nets", "best known", "here", "provenance"], t), ""]
    # Small
    pub = mallach_pw()
    agree = differ = proved = 0
    diffs = []
    for m in (r for r in idx if r["collection"].startswith("Small")):
        w, p = ours(m)
        if m["name"] in pub and w is not None:
            proved += p.startswith("certified")
            if w == pub[m["name"]]:
                agree += 1
            else:
                differ += 1
                diffs.append(f"{m['name']}: {w} vs {pub[m['name']]}")
    lines += [f"Small (Martí et al. 2008): {len(pub)} values read from Mallach (2018) Tables 4-5 "
              f"(pp. 165-166); compared {agree + differ}, agree {agree}, differ {differ}"
              f"{' (' + '; '.join(diffs) + ')' if diffs else ''}; certified here {proved}.", ""]
    # Carvalho & Soma
    cs = carvalho_soma_values()
    t = Counter()
    bad = []
    for m in (r for r in idx if r["collection"] == "MOSP: Carvalho & Soma 2015"):
        w, p = ours(m)
        if w is None or m["name"] not in cs:
            t["no value here"] += 1
            continue
        v = w + 1
        key = ("certified " if p.startswith("certified") else "upper bound ") + \
              ("=" if v == cs[m["name"]] else (">" if v > cs[m["name"]] else "<"))
        t[key] += 1
        if p.startswith("certified") and v != cs[m["name"]] or v < cs[m["name"]]:
            bad.append(f"{m['name']}: {v} ({p}) vs {cs[m['name']]}")
    lines += ["Carvalho & Soma (2015), open stacks against the PT-MOSP spreadsheet "
              "(`raw/carvalho_soma2015/PT-MOSP_reference_values_LARGER_AND_HARDER_RANDOM.xlsx`, "
              "sheet `best solutions larger random`, which is at or below the sheet `optimal solutions known` "
              "on all 150 and below it on 15; the latter's legend marks some values as not proved optimal). "
              "Read with rows as customers (see `paper2/dataset.md` on orientation): "
              + ", ".join(f"{k}: {v}" for k, v in sorted(t.items()))
              + (". Disagreements: " + "; ".join(bad[:10]) if bad else ". No certified value differs, and no "
                 "upper bound here is below a published value."), ""]
    return lines


# ---------------------------------------------------------------------------
# Price
# ---------------------------------------------------------------------------

def spent_graph_runs() -> dict[str, float]:
    """Core-seconds of the repaired-rules runs (2026-10-02), by collection."""
    out = {}
    for coll, files in RESULT_SETS.items():
        out[coll] = sum(float(r["seconds"] or 0) for f in files for r in read_csv(REPAIRED / f))
    return out


def spent_this_run() -> dict[str, float]:
    out = Counter()
    if not RUN_CSV.exists():
        return out
    idx = {(r["source"], r["name"]): r["collection"] for r in read_csv(INDEX)}
    for r in read_csv(RUN_CSV):
        out[idx[(r["source"], r["name"])]] += float(r["seconds"] or 0)
    return out


def split_spent() -> dict[str, float]:
    out = Counter()
    if SPLIT_TASKS.exists():
        for r in read_csv(SPLIT_TASKS):
            try:
                out[r["instance_name"]] += float(r["seconds"] or 0)
            except ValueError:
                pass
    return out


def rome_survival() -> list[list]:
    """How many of the graphs still open at one budget each budget closed."""
    rows = []
    for f, cap in (("rome.csv", "10 s"), ("rome_120s.csv", "120 s"), ("rome_600s.csv", "600 s"),
                   ("rome_3600s.csv", "3,600 s")):
        d = read_csv(REPAIRED / f)
        proved = sum(1 for r in d if r["proof"] in ("refutation", "bound"))
        secs = sum(float(r["seconds"] or 0) for r in d)
        rows.append([f"`{f}`", cap, _f(len(d)), _f(proved), f"{proved / len(d):.0%}", _f(secs / 3600, 1)])
    return rows


def cost_model_mosp() -> list[dict]:
    """§19's model, fitted as `learning.cost_model` fits it (Tobit + drift, `default`
    configuration, trained at n <= 75), applied to the MOSP instances that were
    never certified (Carvalho & Soma 2015, Frinhani et al. 2018 large), with the
    best known upper bound standing in for the optimum. An extrapolation: the
    model was tested at 100-125 only."""
    import numpy as np
    import pandas as pd

    from learning import cost_model as cm
    from learning.features import instance_features
    from paper2.dataset import mosp_instance  # noqa: F401
    from mosp.instance import MOSPInstance

    if COST_PRED.exists():
        return read_csv(COST_PRED)
    frame = cm.assemble()
    model = cm.CostModel(drift=True, gbm=False).fit(frame[cm.training_mask(frame, "default")], "default")
    by, vals = classes()
    runs = {}
    if RUN_CSV.exists():
        for r in read_csv(RUN_CSV):
            runs[r["cls"]] = r
    rows = []
    for cls, members in by.items():
        rep = members[0]
        if not rep["collection"].startswith(("MOSP: Carvalho", "MOSP: Frinhani")):
            continue
        if rep["collection"].startswith("MOSP: Frinhani") and not (
                rep["name"].startswith("Random-400-400-") and rep["name"].endswith("-1")):
            continue      # a sample: features cost 5 s at 400 and 120 s at 1,000 vertices
        import numpy as _np
        from paper2.dataset import read_matrix_file
        M = read_matrix_file(ROOT / rep["source"], transpose=rep["kind"] == "matrix-T")
        inst = MOSPInstance.from_matrix(_np.asarray(M), name=rep["name"])
        feats = instance_features(inst, groups=("matrix", "graph", "invariants"))
        ub = runs.get(cls, {}).get("width")
        opt = int(ub) + 1 if ub not in (None, "") else None
        rows.append(dict(cls=cls, name=rep["name"], collection=rep["collection"], n=M.shape[0], m=M.shape[1],
                         optimum=opt, **{k: feats.get(k) for k in cm.FEATURES_NEEDED}))
    f = pd.DataFrame(rows)
    if f["optimum"].isna().any():   # no upper bound: fall back to the min-fill treewidth + 1 estimate (§4)
        f.loc[f["optimum"].isna(), "optimum"] = f.loc[f["optimum"].isna(), "tw_min_fill"] + 1
    f = cm.prepare(f)
    f["log10_nodes"] = model.predict(f)
    f["core_hours"] = 10 ** f["log10_nodes"] * cm.SECONDS_PER_NODE_125 / 3600
    keep = ["cls", "name", "collection", "n", "m", "optimum", "col_mean", "log10_nodes", "core_hours"]
    f[keep].to_csv(COST_PRED, index=False)
    return read_csv(COST_PRED)


def price() -> str:
    cls_rows = read_csv(CLASSES_CSV)
    spent = spent_graph_runs()
    mine = spent_this_run()
    split = split_spent()
    lines = ["# Section 4's dataset: the price of the full certification run", "",
             "Regenerate: `python -m paper2.dataset price`. Core-hours are one core's wall time; "
             "a censored call counts what it ran, so every spent figure is a lower bound on the "
             "price of what it attempted.", ""]
    # open work per owner collection
    open_by = defaultdict(list)
    for r in cls_rows:
        if r["provenance"] not in ("certified:refutation", "certified:bound"):
            open_by[r["owner"]].append(r)
    rows = []
    for key, _, _ in COLLECTIONS:
        own = [r for r in cls_rows if r["owner"] == key]
        if not own:
            continue
        certified = sum(1 for r in own if r["provenance"] in ("certified:refutation", "certified:bound"))
        op = open_by[key]
        beyond = sum(1 for r in op if not r["max_component"] or int(r["max_component"]) > ENGINE_MAX)
        sp = spent.get(key, 0.0) / 3600
        rows.append([key, _f(len(own)), _f(certified), _f(len(op) - beyond), _f(beyond),
                     _f(sp, 1) if key in spent else "", _f(mine.get(key, 0.0) / 3600, 2)])
    lines += ["## Where the work stands, by collection (classes)", "",
              "*open, engine*: classes without a certified value whose largest component fits the C engine "
              f"(≤ {ENGINE_MAX} vertices); *open, beyond*: larger, or read by header only. "
              "*spent 10-02*: the repaired-rules runs of 2026-10-02 (`solver_fix.md` item 08); "
              "*spent here*: this item's run (witnesses and first runs).", "",
              _md(["collection", "classes", "certified", "open, engine", "open, beyond", "spent 10-02 (core-h)",
                   "spent here (core-h)"], rows), ""]
    # the next step for the graph collections: one budget step up from what each graph has had
    rows = []
    tot = 0.0
    for key, _, fam in COLLECTIONS:
        if fam != "graph" and key != "VLSI gate matrix circuits" and not key.startswith("MOSP: Carvalho"):
            continue
        op = [r for r in open_by[key] if r["max_component"] and int(r["max_component"]) <= ENGINE_MAX]
        if not op:
            continue
        budget = 3600 if key in RESULT_SETS else 600
        ch = len(op) * budget / 3600
        tot += ch
        rows.append([key, _f(len(op)), "3,600 s (had 600 s)" if key in RESULT_SETS else "600 s (had 30 s)",
                     _f(ch, 0)])
    rows.append(["**all**", "", "", _f(tot, 0)])
    lines += ["## The next step for the graph collections, priced", "",
              "Each open class within the engine, run once more at the next budget. The Rome graphs show "
              "what to expect: of the graphs still open at one budget, the next (×5–×12) closed 39–45% "
              "(table below), so a step closes a share, not the set. Each step's cost is bounded by "
              "classes × budget.", "",
              _md(["collection", "open classes (engine)", "next budget", "core-hours at most"], rows), ""]
    lines += ["## The Rome graphs: what each budget closed (repaired rules, 2026-10-02)", "",
              _md(["file", "cap per graph", "attempted", "proved", "share", "core-hours"], rome_survival()), ""]
    # MOSP open
    lines += ["## MOSP corpus: the values still open or in flight", ""]
    rows = []
    for name in sorted(IN_FLIGHT | {"Random-125-125-2-2_0", "Random-125-125-2-3_0"}):
        rows.append([f"`{name}`", "re-certification in flight (`paper2.solver_fix_split`)" if name in IN_FLIGHT
                     else "optimality open (`solution`)",
                     _f(split.get(name, 0.0) / 3600, 1) if name in IN_FLIGHT else "—",
                     ITEM07_PRICE.get(name, "—")])
    measured = sum(split.get(n, 0.0) for n in ("Random-125-125-2-4_0",)) / 3600
    lines += ["The in-flight values are `certified:refutation` in `solutions/` (certified before the repair) "
              "and carry a note in the dataset; the two open ones are `solution`. *Item 07 price*: "
              "`solver_fix.md` item 07, which says those prices are low. The one density-2 125 × 125 "
              f"re-certification completed so far, `Random-125-125-2-4_0`, took {measured:.1f} core-hours "
              "(split run, refuted 2026-10-03 02:55) against an item 07 price of 47.5.", "",
              _md(["instance", "state", "split run so far (core-h)", "item 07 price (core-h)"], rows), ""]
    # cost model on never-certified MOSP collections
    try:
        cm_rows = cost_model_mosp()
    except Exception as exc:  # recorded in the report
        cm_rows = []
        lines += [f"Cost model not applied: {type(exc).__name__}: {exc}", ""]
    if cm_rows:
        lines += ["## Never-certified MOSP collections: the §19 cost model, extrapolated", ""]
        groups = defaultdict(list)
        for r in cm_rows:
            groups[(r["collection"], int(r["n"]))].append(r)
        rows = []
        for (coll, n), rs in sorted(groups.items()):
            ln = sorted(float(r["log10_nodes"]) for r in rs)
            ch = sorted(float(r["core_hours"]) for r in rs)
            cheap = [c for c in ch if c <= 100]
            rows.append([coll, n, len(rs), f"{ln[len(ln) // 2]:.1f}", f"{ln[0]:.1f}–{ln[-1]:.1f}",
                         f"{ch[len(ch) // 2]:.3g}", sum(1 for c in ch if c <= 1), len(cheap),
                         f"{sum(cheap):.3g}"])
        lines += ["Predicted nodes to refute `optimum − 1` under the `default` configuration "
                  "(Tobit + drift, trained at n ≤ 75, tested at 100–125: §19's model), converted at "
                  "0.55 µs per node (`learning.cost_model.SECONDS_PER_NODE_125`). The best upper bound found "
                  "here stands in for the optimum. **Extrapolation**: 150–200 lies beyond every size the model "
                  "was tested at, its per-instance spread is a decade at 100–125, and the post-fix rules cost "
                  "more on the ridge (`solver_fix.md` item 09). Frinhani is a sample, one instance per density "
                  "at 400. Instances already certified here are included, which shows how far off the "
                  "low end is.", "",
                  _md(["collection", "n", "instances", "median log10 nodes", "range", "median core-h",
                       "≤ 1 core-h", "≤ 100 core-h", "core-h of those ≤ 100"], rows), ""]
    text = "\n".join(lines)
    PRICE_MD.write_text(text + "\n")
    return text


def main(stage: str) -> None:
    if stage == "tables":
        print(tables())
    else:
        print(price())
