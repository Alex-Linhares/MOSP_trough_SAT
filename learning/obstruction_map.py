"""loop0013 item 08: the duality-gap map.

Nothing here is computed afresh: the module reads the CSVs items 01-07 left
under `reports/scratch/obstruction_search/` and joins them into one row per
corpus instance (6,376) with every family's floor, family E's ceiling, the
best floor and the family attaining it, then the gap of each by size band,
collection, Chu & Stuckey class and excess decile, the share tight per
family per cell, the dominance table (for every pair of families, on how many
instances one is strictly above the other), the instances no family closes
(with the ten smallest drawn as matrices), the kill verdicts of plan §0.9
with the number that decides each, and the cost ledger regenerated from the
items' own files.

**Units.** Every bound is in optimum units (`pathwidth + 1`); "gap" is
`optimum - value`. Family E has two halves: the *floor* (Harper's bound over
proved levels: cap 12, the rerun, the exact enumeration at n <= 22, SAT with
a verified DRAT certificate) and the *ceiling* (the best searched sets: an
upper bound on what the family can ever prove, not a bound on the optimum).
A ceiling is never a floor anywhere in this module.

**The families and where each floor comes from** (`FAMILIES`):

- `C`  the clique number `omega` (item 01's ledger; `card_le_pathwidth_add_one_of_isClique`);
- `D`  the solver's `lb_best` = max(trivial, clique, contraction degeneracy + 1);
- `T`  `tw + 1`, exact or its proved lower end (`treewidth_le_pathwidth`);
- `P`  Lemma P, pendant cliques (loop0010 item 13);
- `E`  Harper's floor: `max(harper12, 02 floor rerun, 02 exact at n <= 22, 03 floor_after)`;
- `M`  the contraction-minor floor: `max(record minor, 04/05 ladder, 04/05 search, 05 ridge)`;
- `B`  item 06's `b_value` (the third-largest certified branch width + 1 at a
       separator; NaN where no linked triple exists).

`floor0` (item 01) is `max(D, T, harper12, P, record minor)`; `best` is the
maximum over the seven families; where no search ran (an instance outside
every target set) `best == floor0`, which the test pins.

**What this does not claim.** A bound (nothing here is one; every number is
a reading of the items' files); any solver change; that the uncovered
instances share one structure (the description is what the data say).

    python3 -m learning.obstruction_map --stage all        # map, tables, figure
    python3 -m learning.obstruction_map --stage map
    python3 -m learning.obstruction_map --stage tables
    python3 -m learning.obstruction_map --stage figure
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / "reports" / "scratch" / "obstruction_search"
OUT = SCRATCH / "08_map"
LEDGER_CSV = SCRATCH / "01_ledger" / "ledger_corpus.csv"
TARGETS_JSON = SCRATCH / "01_ledger" / "targets.json"
BOUND_GAP_CSV = ROOT / "learning" / "data" / "bound_gap.csv"   # git-ignored; §6's clusters

MAP_CSV = OUT / "map.csv"
UNCOVERED_CSV = OUT / "uncovered.csv"
DOMINANCE_CSV = OUT / "dominance.csv"
COST_CSV = OUT / "cost.csv"
VERDICTS_JSON = OUT / "verdicts.json"
TABLES_MD = OUT / "tables.md"
FIGURE_PNG = OUT / "families.png"
RUN_LOG = OUT / "run.log"

BANDS = ("9–20", "21–30", "31–40", "41–60", "61–75", "76–100", "101–134")
BAND_GROUPS = (("9–30", ("9–20", "21–30")), ("31–60", ("31–40", "41–60")),
               ("61–100", ("61–75", "76–100")), ("101–134", ("101–134",)))
FAMILIES = ("C", "D", "T", "P", "E", "M", "B")
FAMILY_COLUMNS = {"C": "omega", "D": "lb_best", "T": "tw1", "P": "lemmaP", "E": "e_floor", "M": "m_floor", "B": "b_value"}
FAMILY_NAMES = {"C": "clique (ω)", "D": "lb_best (trivial, clique, contraction degeneracy + 1)",
                "T": "treewidth + 1", "P": "Lemma P (pendant cliques)", "E": "expansion (Harper), floor",
                "M": "contraction minor", "B": "separator branches"}
# The palette of the dataviz skill (`references/palette.md`, light mode): slots 1-3 are the
# only ones that validate all-pairs on a scatter.
PALETTE = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a",
           "surface": "#fcfcfb", "text": "#0b0b0b", "text2": "#52514e", "grid": "#e4e3df"}


def log(msg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(RUN_LOG, "a") as handle:
        handle.write(line + "\n")


def _read(path: Path, **kw) -> pd.DataFrame | None:
    return pd.read_csv(path, **kw) if path.exists() else None


def _max_into(target: pd.Series, source: pd.Series) -> pd.Series:
    """`target[i] = max(target[i], source[i])` on the common index; NaN in the
    source leaves the target alone."""
    common = target.index.intersection(source.index)
    vals = pd.to_numeric(source.loc[common], errors="coerce")
    target.loc[common] = np.fmax(target.loc[common].values.astype(float), vals.values.astype(float))
    return target


# ----------------------------------------------------------------------------
# the map: one row per corpus instance
# ----------------------------------------------------------------------------


def targets() -> dict[str, list[str]]:
    t = json.loads(TARGETS_JSON.read_text())
    return {k: t[k] for k in ("gap338", "cs200", "rest500", "small") if isinstance(t.get(k), list)}


def family_e(led: pd.DataFrame) -> pd.DataFrame:
    """Family E per instance: the floor with its source, the ceiling with its
    source; NaN ceiling where the search did not run."""
    e = pd.DataFrame(index=led.index)
    e["e_floor"] = led["harper12"].astype(float)
    e["e_floor_source"] = "harper12"
    e["e_ceiling"] = np.nan
    e["e_ceiling_source"] = ""
    c2 = _read(SCRATCH / "02_expansion" / "ceiling.csv")
    if c2 is not None:
        c2 = c2.set_index("instance_name")
        common = e.index.intersection(c2.index)
        e.loc[common, "e_ceiling"] = c2.loc[common, "ceiling"].astype(float)
        e.loc[common, "e_ceiling_source"] = "02 search"
    for path, col, src in ((SCRATCH / "02_expansion" / "exact_small.csv", "exact_bound", "02 exact"),
                           (SCRATCH / "02_expansion" / "floor.csv", "floor", "02 rerun"),
                           (SCRATCH / "03_sat" / "instances.csv", "floor_after", "03 sat")):
        f = _read(path)
        if f is None:
            continue
        f = f.set_index("instance_name")
        common = e.index.intersection(f.index)
        better = f.loc[common, col].astype(float) > e.loc[common, "e_floor"]
        e.loc[common[better], "e_floor"] = f.loc[common[better], col].astype(float)
        e.loc[common[better], "e_floor_source"] = src
        if col == "exact_bound":      # exact enumeration: the ceiling is the exact value
            e.loc[common, "e_ceiling"] = f.loc[common, "exact_bound"].astype(float)
            e.loc[common, "e_ceiling_source"] = "02 exact"
    i3 = _read(SCRATCH / "03_sat" / "instances.csv")
    if i3 is not None:
        i3 = i3.set_index("instance_name")
        common = e.index.intersection(i3.index)
        lower = i3.loc[common, "ceiling_after"].astype(float) < e.loc[common, "e_ceiling"].fillna(np.inf)
        e.loc[common[lower], "e_ceiling"] = i3.loc[common[lower], "ceiling_after"].astype(float)
        e.loc[common[lower], "e_ceiling_source"] = "03 sat"
    e["e_ran"] = e["e_ceiling"].notna()
    return e


def family_m(led: pd.DataFrame) -> pd.DataFrame:
    """Family M per instance: the record's minor, the ladder's floor, the
    search's floor (items 04, 05 and the ridge stage), and their maximum."""
    m = pd.DataFrame(index=led.index)
    m["m_record"] = led["minor"].astype(float)
    m["m_ladder"] = np.nan
    m["m_search"] = np.nan
    m["m_source_item"] = ""
    for path, item in ((SCRATCH / "04_minor" / "search.csv", "04"), (SCRATCH / "05_minor_scale" / "search.csv", "05"),
                       (SCRATCH / "05_minor_scale" / "ridge_summary.csv", "05 ridge")):
        f = _read(path)
        if f is None:
            continue
        f = f.set_index("instance_name")
        for col in ("ladder_floor", "search_floor"):
            if col in f.columns:
                key = f"m_{col.split('_')[0]}"
                m[key] = _max_into(m[key].fillna(-np.inf), f[col]).replace(-np.inf, np.nan)
        common = m.index.intersection(f.index)
        m.loc[common, "m_source_item"] = [f"{s}|{item}" if s else item for s in m.loc[common, "m_source_item"]]
    m["m_ran"] = m["m_source_item"] != ""
    m["m_floor"] = m[["m_record", "m_ladder", "m_search"]].max(axis=1)
    return m


def family_b(led: pd.DataFrame) -> pd.DataFrame:
    b = pd.DataFrame(index=led.index)
    b["b_value"] = np.nan
    b["b_ran"] = False
    j6 = _read(SCRATCH / "06_branch" / "search.csv")
    if j6 is not None:
        j6 = j6.set_index("instance_name")
        common = b.index.intersection(j6.index)
        b.loc[common, "b_value"] = j6.loc[common, "b_value"].astype(float)
        b.loc[common, "b_ran"] = True
    return b


def clusters() -> pd.Series:
    """§6's two k-means clusters of the 338 (`learning/data/bound_gap.csv`,
    git-ignored): labelled `sparse` / `dense` by their mean matrix density."""
    g = _read(BOUND_GAP_CSV)
    if g is None or "cluster" not in g.columns:
        return pd.Series(dtype=object)
    means = g.groupby("cluster")["density"].mean().sort_values()
    names = {c: ("sparse" if i == 0 else "dense") for i, c in enumerate(means.index)}
    return g.set_index("instance_name")["cluster"].map(names)


def build_map() -> pd.DataFrame:
    led = pd.read_csv(LEDGER_CSV).set_index("instance_name")
    t = targets()
    cols = ["n", "m", "n_ones", "optimum", "collection", "cls", "band", "excess", "cs_n", "cs_m", "cs_d",
            "is_gap338", "is_cs200", "is_small", "lb_best", "lb_trivial", "lb_contraction", "omega", "tw1", "tw1_exact",
            "lemmaP", "minor", "harper12", "harper12_cap", "floor0", "floor0_source"]
    f = led[cols].copy()
    f["is_rest500"] = f.index.isin(t.get("rest500", []))
    f["in_targets"] = f["is_gap338"] | f["is_cs200"] | f["is_rest500"] | f["is_small"]
    f = f.join(family_e(led)).join(family_m(led)).join(family_b(led))
    f["cluster"] = clusters().reindex(f.index)
    for fam, col in FAMILY_COLUMNS.items():
        f[f"gap_{fam}"] = f["optimum"] - f[col]
    vals = f[[FAMILY_COLUMNS[k] for k in FAMILIES]].astype(float)
    f["best"] = vals.max(axis=1)
    f["best_family"] = ["|".join(k for k in FAMILIES if vals.at[i, FAMILY_COLUMNS[k]] == f.at[i, "best"]) for i in f.index]
    f["best"] = f["best"].astype(int)
    f["gap_best"] = f["optimum"] - f["best"]
    f["gap_floor0"] = f["optimum"] - f["floor0"]
    f["gap_e_ceiling"] = f["optimum"] - f["e_ceiling"]
    f["e_bracket"] = f["e_ceiling"] - f["e_floor"]
    f["searched"] = f["e_ran"] | f["m_ran"] | f["b_ran"]
    f["e_closed_out"] = f["e_ceiling"] < f["optimum"]      # the family can never close it
    f["gap_reference"] = f["optimum"] - f[["lb_best", "tw1"]].max(axis=1)
    f["excess_decile"] = pd.qcut(f["excess"], 10, labels=False, duplicates="drop") + 1
    return f.reset_index()


# ----------------------------------------------------------------------------
# the tables
# ----------------------------------------------------------------------------


def _md(table: pd.DataFrame, floatfmt: str = ".2f") -> str:
    return table.to_markdown(index=False, floatfmt=floatfmt)


def family_cell(g: pd.DataFrame, fam: str) -> dict:
    col = FAMILY_COLUMNS[fam]
    ran = g[col].notna()
    gaps = g.loc[ran, f"gap_{fam}"]
    return {f"{fam} ran": int(ran.sum()), f"{fam} tight": int((gaps == 0).sum()),
            f"{fam} tight %": round(100 * (gaps == 0).mean(), 1) if ran.any() else np.nan,
            f"{fam} gap": round(gaps.mean(), 2) if ran.any() else np.nan}


def gap_by(f: pd.DataFrame, key: str, order=None, families=FAMILIES) -> pd.DataFrame:
    rows = []
    keys = order if order is not None else sorted(f[key].dropna().unique())
    for k in keys:
        g = f[f[key] == k]
        if g.empty:
            continue
        row = {key: k, "instances": len(g), "best tight": int((g.gap_best == 0).sum()),
               "best tight %": round(100 * (g.gap_best == 0).mean(), 1), "best gap": round(g.gap_best.mean(), 2),
               "best gap max": int(g.gap_best.max()),
               "floor0 tight": int((g.gap_floor0 == 0).sum()), "floor0 gap": round(g.gap_floor0.mean(), 2)}
        for fam in families:
            row.update(family_cell(g, fam))
        ec = g["e_ceiling"].notna()
        row.update({"E ceiling ran": int(ec.sum()), "E ceiling gap": round(g.loc[ec, "gap_e_ceiling"].mean(), 2) if ec.any() else np.nan,
                    "E closed out": int(g.loc[ec, "e_closed_out"].sum())})
        rows.append(row)
    return pd.DataFrame(rows)


def compact(table: pd.DataFrame, families=("E", "M", "B")) -> pd.DataFrame:
    """The by-cell table with the record families folded: `floor0`, `best`,
    and the three searched families."""
    keep = [c for c in table.columns if not any(c.startswith(f"{fam} ") for fam in FAMILIES if fam not in families)]
    return table[keep]


def dominance(f: pd.DataFrame, families=FAMILIES) -> pd.DataFrame:
    """For every ordered pair (A, B): the instances where both ran, where A
    is strictly above B, and where A is above B on a gap instance."""
    rows = []
    for a in families:
        for b in families:
            if a == b:
                continue
            both = f[FAMILY_COLUMNS[a]].notna() & f[FAMILY_COLUMNS[b]].notna()
            above = both & (f[FAMILY_COLUMNS[a]] > f[FAMILY_COLUMNS[b]])
            rows.append({"A": a, "B": b, "both ran": int(both.sum()), "A > B": int(above.sum()),
                         "A > B %": round(100 * above.sum() / both.sum(), 1) if both.any() else np.nan,
                         "A > B on gap338": int((above & f.is_gap338).sum()),
                         "A > B by ≥ 2": int((both & (f[FAMILY_COLUMNS[a]] - f[FAMILY_COLUMNS[b]] >= 2)).sum())})
    return pd.DataFrame(rows)


def dominance_matrix(d: pd.DataFrame, families=FAMILIES, col: str = "A > B") -> pd.DataFrame:
    m = pd.DataFrame(index=list(families), columns=list(families), dtype=object)
    for _, r in d.iterrows():
        m.at[r.A, r.B] = int(r[col])
    for fam in families:
        m.at[fam, fam] = "—"
    m.index.name = "A ∖ B"
    return m.reset_index()


def uncovered(f: pd.DataFrame) -> pd.DataFrame:
    u = f[f.gap_best > 0].copy()
    cols = ["instance_name", "n", "m", "n_ones", "excess", "collection", "cls", "band", "cluster", "is_gap338", "is_cs200",
            "is_rest500", "is_small", "optimum", "lb_best", "tw1", "omega", "lemmaP", "floor0", "e_floor", "e_ceiling",
            "e_closed_out", "e_bracket", "m_floor", "m_record", "m_ladder", "m_search", "m_ran", "b_value", "b_ran",
            "best", "best_family", "gap_best", "searched"]
    return u[cols].sort_values(["gap_best", "n", "instance_name"], ascending=[False, True, True])


def draw_smallest(u: pd.DataFrame, k: int = 10) -> str:
    """The k smallest uncovered instances (by n, m, name) as matrices, through
    `learning.extremal.draw` (the same renderer §6 used)."""
    from learning.extremal import draw, matrix_key
    from learning.obstruction_ledger import corpus_instances

    inst = corpus_instances()
    rows = u.sort_values(["n", "m", "instance_name"]).head(k)
    blocks = []
    for _, r in rows.iterrows():
        matrix = np.asarray(inst[r.instance_name][1].matrix, dtype=int)
        title = (f"`{r.instance_name}` ({r.collection}): optimum {int(r.optimum)}, best floor {int(r.best)} ({r.best_family}), "
                 f"E ceiling {'—' if pd.isna(r.e_ceiling) else int(r.e_ceiling)}, excess {r.excess:.2f}"
                 + (f", §6 cluster {r.cluster}" if isinstance(r.cluster, str) else ""))
        blocks.append(draw(matrix_key(matrix), title))
    return "\n\n".join(blocks)


# ----------------------------------------------------------------------------
# kill verdicts and the cost ledger
# ----------------------------------------------------------------------------


def kill_verdicts(f: pd.DataFrame) -> list[dict]:
    """Plan §0.9's five verdicts, each with the number from the item's own
    file that decides it, recomputed here from those files."""
    out = []
    ex = _read(SCRATCH / "02_expansion" / "exact_small.csv")
    if ex is not None:
        share = ex["all_levels_match"].astype(bool).mean()
        out.append({"family": "E, the search", "criterion": "searched f̂(t) = exact f(t) at every t on < 90% of instances at n ≤ 22",
                    "number": f"{int(ex['all_levels_match'].astype(bool).sum())} of {len(ex)} ({100 * share:.1f}%)",
                    "verdict": "met" if share < 0.9 else "not met", "source": "02_expansion/exact_small.csv"})
    i3 = _read(SCRATCH / "03_sat" / "instances.csv")
    c2 = _read(SCRATCH / "02_expansion" / "ceiling.csv")
    if i3 is not None and c2 is not None:
        g338 = f[f.is_gap338].set_index("instance_name")
        n338 = len(g338)
        # the bracket before item 03: item 02's ceiling against the floor on record then
        # (cap 12, the rerun, the exact enumeration)
        e_before = g338["harper12"].astype(float).copy()
        for path, col in ((SCRATCH / "02_expansion" / "floor.csv", "floor"), (SCRATCH / "02_expansion" / "exact_small.csv", "exact_bound")):
            x = _read(path)
            if x is not None:
                e_before = _max_into(e_before, x.set_index("instance_name")[col])
        bracket = int((c2.set_index("instance_name")["ceiling"].reindex(g338.index) - e_before > 0).sum())
        g = i3[i3.instance_name.isin(g338.index)]
        settled = int(g["argmax_settled"].astype(bool).sum())
        out.append({"family": "E, the exact half", "criterion": "SAT settles the argmax level on < 50% of the 338 within budget",
                    "number": f"{settled} of {n338} ({100 * settled / n338:.1f}%); {settled} of the {bracket} with a bracket "
                              f"({100 * settled / max(bracket, 1):.1f}%), {len(g)} of them reached",
                    "verdict": "met" if settled / n338 < 0.5 else "not met", "source": "03_sat/instances.csv, 02_expansion/ceiling.csv"})
    beats = 0
    ran = 0
    for path in (SCRATCH / "04_minor" / "search.csv", SCRATCH / "05_minor_scale" / "search.csv"):
        s = _read(path)
        if s is None:
            continue
        s = s[s.instance_name.isin(f.loc[f.is_gap338, "instance_name"])]
        beats += int(s["beats_ladder_floor"].astype(bool).sum())
        ran += len(s)
    n338 = int(f.is_gap338.sum())
    out.append({"family": "M", "criterion": "the search beats the greedy ladder on < 10% of the 338",
                "number": f"{beats} of {n338} ({100 * beats / n338:.1f}%); {ran} of the 338 run",
                "verdict": "met" if beats / n338 < 0.1 else "not met", "source": "04_minor/search.csv, 05_minor_scale/search.csv"})
    res = f[f.is_gap338 & (f[["lb_best", "tw1", "m_floor", "e_floor", "floor0"]].max(axis=1) < f.optimum)]
    ref = f[["lb_best", "tw1", "m_floor"]].max(axis=1)
    exceeds_res = int((f.b_value > ref)[res.index].sum())
    exceeds_338 = int(((f.b_value > ref) & f.is_gap338).sum())
    out.append({"family": "B", "criterion": "no B certificate exceeds max(lb_best, tw + 1, M's floor) on any residual gap instance",
                "number": f"{exceeds_res} of {len(res)} residual instances; {exceeds_338} of the 338",
                "verdict": "met" if exceeds_res == 0 else "not met", "source": "06_branch/search.csv"})
    j7 = _read(SCRATCH / "07_open" / "joined.csv")
    if j7 is not None:
        tree = j7["best_family"].eq("theorem")
        above = j7.loc[~tree, "above_record"].astype(bool)
        closed = j7["closed"].astype(bool)
        out.append({"family": "open classes", "criterion": "zero floors above the recorded ones (the tree aside) is a verdict, not a failure",
                    "number": f"{int(above.sum())} of {int((~tree).sum())} floors above the record (tree aside); {int(closed.sum())} of {len(j7)} classes closed",
                    "verdict": "not met (floors rose; two classes closed)" if above.any() else "met", "source": "07_open/joined.csv"})
    return out


def cost_ledger() -> pd.DataFrame:
    """Core-hours per item, summed from the seconds columns of the items' own
    CSVs (instance time only: the C program's seconds are inside the search's;
    the checker's seconds where its verdict file has them). What the files do
    not carry is listed in `not counted`; the run logs' own `core-hours` lines
    are quoted beside."""
    def secs(path, cols):
        f = _read(path)
        if f is None:
            return 0.0
        return float(sum(pd.to_numeric(f[c], errors="coerce").fillna(0).sum() for c in cols if c in f.columns))

    def log_lines(item):
        p = SCRATCH / item / "run.log"
        if not p.exists():
            return ""
        nums = []
        for ln in p.read_text().splitlines():
            if "this run" in ln or "instance time" in ln or re.search(r"core-hours?$", ln.strip()):
                nums += re.findall(r"([0-9]+\.[0-9]+) core-h", ln)
        return "; ".join(nums)

    rows = [
        ("01", "Harper at cap 12 on every corpus instance", secs(SCRATCH / "01_ledger" / "harper12.csv", ["harper12_seconds"]), 0.0,
         "the dataset's cheap floors (no seconds column)"),
        ("02", "E ceiling (two passes), exact at n ≤ 22, floor rerun",
         secs(SCRATCH / "02_expansion" / "ceiling.csv", ["seconds"]) + secs(SCRATCH / "02_expansion" / "ceiling_s2x3.csv", ["seconds"])
         + secs(SCRATCH / "02_expansion" / "exact_small.csv", ["exact_seconds"]) + secs(SCRATCH / "02_expansion" / "floor.csv", ["floor_seconds"]),
         0.0, "the harness run (0.32 core-hours by its log)"),
        ("03", "E exact by SAT with DRAT", secs(SCRATCH / "03_sat" / "instances.csv", ["seconds"]),
         secs(SCRATCH / "03_sat" / "checker_verdicts.csv", ["check_seconds"]), "the three instances not reached (partial certificates)"),
        ("04", "M search and ladder at n ≤ 60", secs(SCRATCH / "04_minor" / "search.csv", ["ladder_seconds", "search_seconds"]),
         secs(SCRATCH / "04_minor" / "checker_verdicts.csv", ["seconds"]), "the validation runs (0.3 core-hours by the log), the two restarts' redone work"),
        ("05", "M at scale, the ridge pair", secs(SCRATCH / "05_minor_scale" / "search.csv", ["ladder_seconds", "search_seconds"])
         + secs(SCRATCH / "05_minor_scale" / "ridge_summary.csv", ["seconds"]),
         secs(SCRATCH / "05_minor_scale" / "checker_verdicts.csv", ["seconds"]), "the 22 carried rows are counted under 04"),
        ("06", "B separators with certified branches", secs(SCRATCH / "06_branch" / "search.csv", ["seconds"]),
         secs(SCRATCH / "06_branch" / "checker_verdicts.csv", ["seconds"]), "pass 1 (0.48 core-hours by the log), connectivity"),
        ("07", "the 24 open classes (E, M, B)", secs(SCRATCH / "07_open" / "ceiling.csv", ["seconds"]) + secs(SCRATCH / "07_open" / "minor.csv", ["seconds"])
         + secs(SCRATCH / "07_open" / "branch.csv", ["seconds"]), secs(SCRATCH / "07_open" / "checker_verdicts.csv", ["seconds"]),
         "the rule-free check of NY_13 (1.9 s)"),
        ("08", "this map (reads files)", 0.0, 0.0, "—"),
    ]
    out = pd.DataFrame(rows, columns=["item", "what", "instance core-hours", "checker core-hours", "not counted"])
    out["instance core-hours"] = (out["instance core-hours"] / 3600).round(2)
    out["checker core-hours"] = (out["checker core-hours"] / 3600).round(2)
    dirs = {"01": "01_ledger", "02": "02_expansion", "03": "03_sat", "04": "04_minor", "05": "05_minor_scale",
            "06": "06_branch", "07": "07_open", "08": "08_map"}
    out["run.log says (core-hours)"] = [log_lines(dirs[i]) for i in out["item"]]
    total = pd.DataFrame([{"item": "total", "what": "", "instance core-hours": out["instance core-hours"].sum().round(2),
                           "checker core-hours": out["checker core-hours"].sum().round(2), "not counted": "", "run.log says (core-hours)": ""}])
    return pd.concat([out, total], ignore_index=True)


# ----------------------------------------------------------------------------
# the figure
# ----------------------------------------------------------------------------


def figure(f: pd.DataFrame, path: Path = FIGURE_PNG) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": PALETTE["grid"], "axes.labelcolor": PALETTE["text2"],
                         "xtick.color": PALETTE["text2"], "ytick.color": PALETTE["text2"], "axes.titlecolor": PALETTE["text"],
                         "figure.facecolor": PALETTE["surface"], "axes.facecolor": PALETTE["surface"], "savefig.facecolor": PALETTE["surface"]})
    s = f[f.e_ceiling.notna()].copy()         # the 4,697 targets: where both a floor and a ceiling exist
    fig = plt.figure(figsize=(11, 7.6))
    gs = fig.add_gridspec(2, 4, height_ratios=(1, 1.15), hspace=0.55, wspace=0.28)
    rng = np.random.default_rng(0)
    ymax = int(max(s.gap_best.max(), s.gap_e_ceiling.max())) + 1
    XMAX = 20.0
    bins = np.arange(0, XMAX + 1.0, 0.5)
    for col, (label, bands) in enumerate(BAND_GROUPS):
        ax = fig.add_subplot(gs[0, col])
        g = s[s.band.isin(bands)]
        jit = lambda v: v + rng.uniform(-0.22, 0.22, len(v))  # noqa: E731
        ax.scatter(g.excess, jit(g.gap_e_ceiling.values), s=16, facecolors="none", edgecolors=PALETTE["orange"], alpha=0.75,
                   linewidths=0.8, label="E ceiling", zorder=2)
        ax.scatter(g.excess, jit(g.gap_best.values), s=14, color=PALETTE["blue"], alpha=0.45, linewidths=0, label="best floor", zorder=3)
        for name, color, z in (("gap_e_ceiling", PALETTE["orange"], 4), ("gap_best", PALETTE["blue"], 5)):
            grp = g.groupby(pd.cut(g.excess, bins), observed=True)[name].agg(["mean", "size"])
            grp = grp[grp["size"] >= 5]
            ax.plot([iv.mid for iv in grp.index], grp["mean"], color=color, linewidth=2, zorder=z)
        off = int((g.excess > XMAX).sum())
        ax.set_title(f"{label} customers\n{len(g):,} instances" + (f", {off} beyond e = {XMAX:.0f}" if off else ""),
                     loc="left", fontsize=9)
        ax.set_xlim(0, XMAX + 0.5)
        ax.set_xlabel("excess e = (ones − m) / n")
        if col == 0:
            ax.set_ylabel("gap = optimum − value")
            ax.legend(frameon=False, loc="upper left", fontsize=8.5)
        ax.set_ylim(-0.6, ymax)
        ax.grid(True, color=PALETTE["grid"], linewidth=0.6)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    # panel B: the 200 Chu & Stuckey by class
    ax = fig.add_subplot(gs[1, :])
    cs = f[f.is_cs200].copy()
    keys = sorted(set(zip(cs.cs_n.astype(int), cs.cs_m.astype(int), cs.cs_d.astype(int))))
    label_of = {k: f"{k[0]}-{k[1]}-{k[2]}" for k in keys}
    cs["cls_key"] = [label_of[k] for k in zip(cs.cs_n.astype(int), cs.cs_m.astype(int), cs.cs_d.astype(int))]
    order = [label_of[k] for k in keys]
    pos = {k: i for i, k in enumerate(order)}
    x = cs.cls_key.map(pos).values.astype(float)
    ax.scatter(x + rng.uniform(-0.18, 0.18, len(x)), cs.gap_e_ceiling, s=20, facecolors="none", edgecolors=PALETTE["orange"], alpha=0.8,
               linewidths=0.9, label="E ceiling", zorder=2)
    ax.scatter(x + rng.uniform(-0.18, 0.18, len(x)), cs.gap_best, s=18, color=PALETTE["blue"], alpha=0.55, linewidths=0, label="best floor",
               zorder=3)
    means = cs.groupby("cls_key")[["gap_best", "gap_e_ceiling"]].mean()
    ax.plot([pos[k] for k in order], [means.loc[k, "gap_e_ceiling"] for k in order], color=PALETTE["orange"], linewidth=2, zorder=4)
    ax.plot([pos[k] for k in order], [means.loc[k, "gap_best"] for k in order], color=PALETTE["blue"], linewidth=2, zorder=5)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=90, fontsize=7.5)
    ax.set_xlabel("Chu & Stuckey class (customers-products-density), 5 instances each")
    ax.set_ylabel("gap = optimum − value")
    ax.grid(True, axis="y", color=PALETTE["grid"], linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    worst = means["gap_best"].sort_values(ascending=False).head(2)
    for k, v in worst.items():
        ax.annotate(f"mean {v:.1f}", (pos[k], v), textcoords="offset points", xytext=(6, 4), fontsize=8, color=PALETTE["text2"])
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------
# tables.md
# ----------------------------------------------------------------------------


def headline(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, g in (("all 6,376", f), ("searched targets", f[f.in_targets]), ("gap338", f[f.is_gap338]),
                     ("cs200", f[f.is_cs200]), ("rest500", f[f.is_rest500]), ("small (n ≤ 22)", f[f.is_small])):
        rows.append({"set": label, "instances": len(g), "floor0 tight": int((g.gap_floor0 == 0).sum()),
                     "reference tight": int((g.gap_reference == 0).sum()),
                     "best tight": int((g.gap_best == 0).sum()), "best tight %": round(100 * (g.gap_best == 0).mean(), 1),
                     "best gap mean": round(g.gap_best.mean(), 2), "best gap max": int(g.gap_best.max()),
                     "gap ≥ 2": int((g.gap_best >= 2).sum()), "best > floor0": int((g.best > g.floor0).sum()),
                     "E closed out": int(g.e_closed_out.sum()), "E bracket 0": int((g.e_bracket == 0).sum())})
    return pd.DataFrame(rows)


def excess_table(f: pd.DataFrame, mask=None) -> pd.DataFrame:
    g = f if mask is None else f[mask]
    bounds = f.groupby("excess_decile")["excess"].agg(["min", "max"])
    t = gap_by(g, "excess_decile", sorted(f.excess_decile.dropna().unique()))
    t.insert(1, "excess range", [f"{bounds.loc[d, 'min']:.2f}–{bounds.loc[d, 'max']:.2f}" for d in t["excess_decile"]])
    return t


def best_family_table(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fam in FAMILIES:
        hit = f.best_family.str.split("|").map(lambda s: fam in s)
        alone = f.best_family == fam
        rows.append({"family": fam, "what": FAMILY_NAMES[fam], "ran": int(f[FAMILY_COLUMNS[fam]].notna().sum()),
                     "attains best": int(hit.sum()), "attains alone": int(alone.sum()),
                     "attains alone and tight": int((alone & (f.gap_best == 0)).sum()),
                     "on the 338: attains best": int((hit & f.is_gap338).sum()),
                     "on the 338: alone and tight": int((alone & f.is_gap338 & (f.gap_best == 0)).sum()),
                     "on cs200: alone and tight": int((alone & f.is_cs200 & (f.gap_best == 0)).sum())})
    return pd.DataFrame(rows)


def uncovered_summary(f: pd.DataFrame, u: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, g, ug in (("all 6,376", f, u), ("searched targets", f[f.in_targets], u[u.searched]),
                         ("gap338", f[f.is_gap338], u[u.is_gap338]), ("cs200", f[f.is_cs200], u[u.is_cs200])):
        rows.append({"set": label, "instances": len(g), "uncovered": len(ug), "uncovered %": round(100 * len(ug) / max(len(g), 1), 1),
                     "gap 1": int((ug.gap_best == 1).sum()), "gap ≥ 2": int((ug.gap_best >= 2).sum()),
                     "n range": f"{int(ug.n.min())}–{int(ug.n.max())}" if len(ug) else "—",
                     "excess mean": round(ug.excess.mean(), 2) if len(ug) else np.nan,
                     "E closed out": int(ug.e_closed_out.sum()), "E bracket open": int((ug.e_bracket > 0).sum()),
                     "M ran": int(ug.m_ran.sum()), "B ran": int(ug.b_ran.sum()), "not searched": int((~ug.searched).sum())})
    return pd.DataFrame(rows)


def uncovered_by(u: pd.DataFrame) -> pd.DataFrame:
    g = u.copy()
    g["cluster"] = g["cluster"].fillna("(not in the 338)")
    t = g.groupby(["collection", "cluster"]).agg(instances=("instance_name", "size"), n_min=("n", "min"), n_max=("n", "max"),
                                                  excess_mean=("excess", "mean"), gap_mean=("gap_best", "mean"), gap_max=("gap_best", "max"),
                                                  e_closed_out=("e_closed_out", "sum"), m_ran=("m_ran", "sum")).reset_index()
    return t.sort_values("instances", ascending=False)


def open_table() -> pd.DataFrame:
    j7 = _read(SCRATCH / "07_open" / "joined.csv")
    if j7 is None:
        return pd.DataFrame()
    cols = ["id", "names", "n", "width", "lower", "e_ceiling_pw", "m_floor_pw", "b_floor_pw", "theorem_pw", "best_new_floor_pw",
            "best_family", "above_record", "closed", "e_ceiling_below_width"]
    t = j7[[c for c in cols if c in j7.columns]].copy()
    t["names"] = t["names"].astype(str).str.slice(0, 28)
    return t


def write_tables(f: pd.DataFrame) -> str:
    n_targets = int(f.in_targets.sum())
    parts = [f"# The duality-gap map: tables (item 08)\n\n*Generated by `python3 -m learning.obstruction_map --stage tables` on "
             f"{time.strftime('%Y-%m-%d %H:%M')}; {len(f)} corpus instances (9–134 customers); the searched families ran on "
             f"{n_targets} targets (E ceiling on {int(f.e_ran.sum())}, M on {int(f.m_ran.sum())}, B on {int(f.b_ran.sum())}); "
             f"C, D, T, P and Harper at cap 12 are on record for all {len(f)}. Every value in optimum units; gap = optimum − value; "
             f"\"ran\" counts the instances where the family has a value; a family's \"tight %\" is over those.*\n"]
    parts += ["## (a) Headline: who closes what", "", _md(headline(f)), ""]
    by_band = gap_by(f, "band", list(BANDS))
    parts += ["## (b) By size band (all 6,376; the searched families over the instances they ran on)", "", _md(compact(by_band)), ""]
    parts += ["## (b2) By size band, the record families", "",
              _md(by_band[["band", "instances"] + [c for c in by_band.columns if c.split(" ")[0] in ("C", "D", "T", "P")]]), ""]
    parts += ["## (c) The 338 gap instances by band", "", _md(compact(gap_by(f[f.is_gap338], "band", list(BANDS)))), ""]
    parts += ["## (d) By collection", "", _md(compact(gap_by(f, "collection"))), ""]
    cs = f[f.is_cs200].copy()
    cs["class"] = [f"{int(a)}-{int(b)}-{int(c)}" for a, b, c in zip(cs.cs_n, cs.cs_m, cs.cs_d)]
    order = [f"{int(a)}-{int(b)}-{int(c)}" for a, b, c in sorted(set(zip(cs.cs_n, cs.cs_m, cs.cs_d)))]
    parts += ["## (e) The 200 Chu & Stuckey by class", "", _md(compact(gap_by(cs, "class", order))), ""]
    parts += ["## (f) By excess decile (deciles over all 6,376; the boundaries in the second column)", "", _md(compact(excess_table(f))), ""]
    parts += ["## (f2) The 338 by excess decile (the same boundaries)", "", _md(compact(excess_table(f, f.is_gap338))), ""]
    d = dominance(f)
    parts += ["## (g) Dominance: instances where the row family is strictly above the column family (both ran)", "",
              _md(dominance_matrix(d), ".0f"), "", "Both ran (denominator):", "", _md(dominance_matrix(d, col="both ran"), ".0f"), "",
              "On the 338:", "", _md(dominance_matrix(d, col="A > B on gap338"), ".0f"), ""]
    parts += ["## (h) Best family: which family attains the best floor (ties counted for each)", "", _md(best_family_table(f)), ""]
    u = uncovered(f)
    parts += ["## (i) Uncovered: the instances no family closes", "", _md(uncovered_summary(f, u)), "",
              "By collection and §6 cluster (only the 338 carry a cluster):", "", _md(uncovered_by(u)), "",
              "The uncovered instances of the 338, in full (`uncovered.csv` has every one):", "",
              _md(u[u.is_gap338][["instance_name", "n", "m", "excess", "cluster", "optimum", "floor0", "e_floor", "e_ceiling",
                                  "m_floor", "b_value", "best", "best_family", "gap_best"]], ".2f"), ""]
    parts += ["## (j) The ten smallest uncovered instances, drawn", "", draw_smallest(u), ""]
    parts += ["## (k) Kill verdicts (plan §0.9), each with the number that decides it", "", _md(pd.DataFrame(kill_verdicts(f))), ""]
    parts += ["## (l) Cost ledger: core-hours per item, from the items' files", "", _md(cost_ledger()), ""]
    parts += ["## (m) The 24 open classes (pathwidth units; item 07's `joined.csv`)", "", _md(open_table()), ""]
    text = "\n".join(parts)
    TABLES_MD.write_text(text)
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", default="all", choices=("all", "map", "tables", "figure"))
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage in ("all", "map"):
        f = build_map()
        f.to_csv(MAP_CSV, index=False)
        u = uncovered(f)
        u.to_csv(UNCOVERED_CSV, index=False)
        dominance(f).to_csv(DOMINANCE_CSV, index=False)
        cost_ledger().to_csv(COST_CSV, index=False)
        VERDICTS_JSON.write_text(json.dumps(kill_verdicts(f), indent=2, ensure_ascii=False))
        log(f"map: {len(f)} instances; best tight on {int((f.gap_best == 0).sum())}; floor0 tight on {int((f.gap_floor0 == 0).sum())}; "
            f"uncovered {len(u)} ({int(u.is_gap338.sum())} of the 338, {int(u.is_cs200.sum())} of cs200); "
            f"best above optimum on {int((f.best > f.optimum).sum())} (must be 0); wrote {MAP_CSV.name}, {UNCOVERED_CSV.name}, "
            f"{DOMINANCE_CSV.name}, {COST_CSV.name}, {VERDICTS_JSON.name}")
    if args.stage in ("all", "tables"):
        f = pd.read_csv(MAP_CSV)
        write_tables(f)
        log(f"tables: wrote {TABLES_MD}")
    if args.stage in ("all", "figure"):
        f = pd.read_csv(MAP_CSV)
        figure(f)
        log(f"figure: wrote {FIGURE_PNG}")


if __name__ == "__main__":
    main()
