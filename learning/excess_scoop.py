"""Industrial instances in the excess: the 24 SCOOP instances, with the 300
Faggioli-Bentivoglio instances as the structured-but-not-industrial comparison
(loop0010 item 04).

For every instance of the two collections, from what is already on record and
nothing else: `n`, `m`, `n_ones`, the excess `e = (n_ones - m) / n`, the
incidence graph's `kappa`, `gamma`, forest flag and (2, 2)-core share
(`learning/data/excess.csv`, item 01); the certified optimum with its
provenance read from the solution file (item 01's map); `lb_best` / `ub_best`
and the component bounds from `learning/data/instances.csv`; the two-key rule's
value (`learning/data/excess_rule.csv`, item 02); the finite first-moment floor
at bound < 1 and < 0.01 and the asymptotic constant `beta*` from the instance's
own pattern-size histogram (`learning/first_moment.py`); every certification
cost on record -- the three September sweeps of the SAT path
(`benchmarks/results/sweep_full.csv`, `sweep_long.csv`,
`overnight_20260917_0033_round1.csv`: seconds of the whole binary search), the
compute ledger (`compute_ledger.csv`: no row for either collection), the
refutation of `optimum - 1` in nodes and seconds under both search
configurations (`learning/data/node_counts.csv` at n <= 40, the identity
labelling of `learning/data/ensemble/differential_scale.csv` at 50-100,
`learning/data/ensemble/search_certificate.csv` at <= 75) and the DRAT proofs of
`learning/data/proofs.csv`; and the cost model's prediction
(`learning.cost_model`, the chosen `linear + drift + gbm [row]` variant per
configuration, refitted on its training rows at n <= 75).

Nothing is solved, nothing is re-run, and `solutions/` is not written. Where a
record has no row the column says so (`NaN`, and `nodes_source = not recorded`).

The one check the item states: every optimum must sit at or above its 0.01
floor. The floor is a statement about a *random* clique cover with the same
pattern sizes, so an instance below it is not a contradiction; it measures how
far the instance is from random (`below_floor_001`).

Usage:
    python -m learning.excess_scoop                  # build + tables (~10 s)
    python -m learning.excess_scoop --stage build    # -> learning/data/excess_scoop.csv
    python -m learning.excess_scoop --stage tables   # from the CSV
    python -m pytest tests/test_excess_scoop.py -q
"""
from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.excess import giant_threshold_excess, load, load_rule, sizes_from_text
from learning.first_moment import beta_star, floors

DATA_DIR = Path("learning/data")
OUT_CSV = DATA_DIR / "excess_scoop.csv"
INSTANCES_CSV = DATA_DIR / "instances.csv"
RESULTS_DIR = Path("benchmarks/results")
LEDGER_CSV = RESULTS_DIR / "compute_ledger.csv"
SWEEP_CSVS = ("sweep_full.csv", "sweep_long.csv", "overnight_20260917_0033_round1.csv")
NODE_COUNTS_CSV = DATA_DIR / "node_counts.csv"
DIFFERENTIAL_CSV = DATA_DIR / "ensemble" / "differential_scale.csv"
CERTIFICATE_CSV = DATA_DIR / "ensemble" / "search_certificate.csv"
PROOFS_CSV = DATA_DIR / "proofs.csv"
COLLECTIONS = ("SCOOP", "Faggioli-Bentivoglio")
CONFIGS = ("default", "csearch")
FB_NAME = re.compile(r"^p(\d{2})(\d{2})n\d+_\d+$")
SECONDS_PER_NODE = 0.65e-6   # CLAUDE.md, reports/inner_loop.md: hard refutations at 0.65 us per node, one core
RIDGE = (2.0, 2.4)
BOUND_COLUMNS = ["lb_trivial", "lb_contraction", "lb_best", "ub_mcn", "ub_cs_dfs", "ub_best", "tw_min_fill",
                 "g_degeneracy"]

# ----------------------------------------------------------------------------
# the regimes of the planner's statement
# ----------------------------------------------------------------------------


def regime_of(e: float, r: float, forest: bool = False) -> str:
    """Where an order book with excess `e` and product ratio `r = m / n` sits.

    `forest`: the incidence graph has no cycle (`gamma = 0`), a deterministic
    hypothesis under which item 03/06's bound applies whatever `e` is;
    `below e_g`: `e < e_g(r)`, the random model's forest regime (mostly forests,
    item 01 finding 5), but this instance has a cycle; `[e_g, 1)`: the first
    moment says nothing and the deterministic bounds are what there is;
    `[1, 2)`, `ridge [2, 2.4]`, `> 2.4`: the floor is positive.
    """
    if forest:
        return "forest"
    if e < giant_threshold_excess(r):
        return "below e_g"
    if e < 1.0:
        return "[e_g, 1)"
    if e < RIDGE[0]:
        return "[1, 2)"
    if e <= RIDGE[1]:
        return "ridge [2, 2.4]"
    return "> 2.4"


REGIME_ORDER = ["forest", "below e_g", "[e_g, 1)", "[1, 2)", "ridge [2, 2.4]", "> 2.4"]


def fb_cell(name: str) -> tuple[int, int] | None:
    """`(m, n)` nominal of a Faggioli-Bentivoglio file name `pMMNNnK_0` (the
    README: `m` patterns, `n` pieces; empty rows and columns were removed, so
    the realised `n` can be smaller)."""
    match = FB_NAME.match(name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


# ----------------------------------------------------------------------------
# the floor from the instance's own pattern sizes
# ----------------------------------------------------------------------------


def floor_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """`floor_lt1`, `floor_lt001` (the optimum is at least this for a random
    cover of the same size law, with probability > 0 / > 0.99), `beta_star`,
    `beta_star_n`, and the two flags `below_floor_1`, `below_floor_001`."""
    out = frame.copy()
    f1, f01, bs = [], [], []
    for n, m, sizes in zip(out["n"], out["m"], out["sizes"]):
        hist = sizes_from_text(sizes)
        a, b = floors(int(n), hist)
        f1.append(a)
        f01.append(b)
        bs.append(beta_star(m / n, hist))
    out["floor_lt1"] = f1
    out["floor_lt001"] = f01
    out["beta_star"] = bs
    out["beta_star_n"] = out["beta_star"] * out["n"]
    out["below_floor_1"] = out["optimum"] < out["floor_lt1"]
    out["below_floor_001"] = out["optimum"] < out["floor_lt001"]
    return out


# ----------------------------------------------------------------------------
# every certification cost on record
# ----------------------------------------------------------------------------


def sweep_records(names: list[str], results_dir: Path = RESULTS_DIR, files: tuple[str, ...] = SWEEP_CSVS) -> pd.DataFrame:
    """Per instance, the seconds and status in each sweep CSV (the SAT path's
    binary search, 2026-09-16/17, before the customer search became the
    default), and `certified_by` / `certified_seconds`: the first file whose
    row says `solved`."""
    out = pd.DataFrame({"instance_name": names})
    out["certified_by"] = ""
    out["certified_seconds"] = np.nan
    for file in files:
        path = results_dir / file
        stem = Path(file).stem
        if not path.exists():
            out[f"{stem}_seconds"] = np.nan
            out[f"{stem}_status"] = ""
            continue
        f = pd.read_csv(path).drop_duplicates("instance_name", keep="last").set_index("instance_name")
        sec = out["instance_name"].map(f["time_seconds"])
        status = out["instance_name"].map(f["status"]).fillna("")
        out[f"{stem}_seconds"] = sec
        out[f"{stem}_status"] = status
        first = (out["certified_by"] == "") & status.eq("solved")
        out.loc[first, "certified_by"] = stem
        out.loc[first, "certified_seconds"] = sec[first]
    return out


def ledger_records(names: list[str], ledger: Path = LEDGER_CSV) -> pd.DataFrame:
    """Rows of the compute ledger for these instances: `ledger_rows`,
    `ledger_seconds` (sum), `ledger_nodes` (last non-empty)."""
    out = pd.DataFrame({"instance_name": names, "ledger_rows": 0, "ledger_seconds": np.nan, "ledger_nodes": np.nan})
    if not ledger.exists():
        return out
    f = pd.read_csv(ledger)
    f = f[f["instance"].isin(names)]
    if len(f):
        g = f.groupby("instance").agg(rows=("seconds", "size"), seconds=("seconds", "sum"), nodes=("nodes", "last"))
        out["ledger_rows"] = out["instance_name"].map(g["rows"]).fillna(0).astype(int)
        out["ledger_seconds"] = out["instance_name"].map(g["seconds"])
        out["ledger_nodes"] = out["instance_name"].map(g["nodes"])
    return out


def node_count_records(names: list[str], node_counts: Path = NODE_COUNTS_CSV,
                       differential: Path = DIFFERENTIAL_CSV) -> pd.DataFrame:
    """Per configuration: nodes and seconds to refute `optimum - 1`, from
    `node_counts.csv` (n <= 40) where present, else from the identity labelling
    of `differential_scale.csv` (50-100), with the min and max over its five
    labellings; `nodes_source_<cfg>` names the file or says `not recorded`. A
    censored count (`status != unsat`) is kept and flagged in `status_<cfg>`."""
    out = pd.DataFrame({"instance_name": names})
    for cfg in CONFIGS:
        out[f"nodes_{cfg}"] = np.nan
        out[f"seconds_{cfg}"] = np.nan
        out[f"status_{cfg}"] = ""
        out[f"nodes_source_{cfg}"] = "not recorded"
        out[f"nodes_{cfg}_labelling_min"] = np.nan
        out[f"nodes_{cfg}_labelling_max"] = np.nan
    if differential.exists():
        d = pd.read_csv(differential)
        d = d[d["base_name"].isin(names)]
        for cfg in CONFIGS:
            dc = d[d["config"] == cfg]
            ident = dc[dc["labelling"] == "identity"].drop_duplicates("base_name").set_index("base_name")
            g = dc.groupby("base_name")["nodes_lo"].agg(["min", "max"])
            has = out["instance_name"].isin(ident.index)
            out.loc[has, f"nodes_{cfg}"] = out.loc[has, "instance_name"].map(ident["nodes_lo"])
            out.loc[has, f"seconds_{cfg}"] = out.loc[has, "instance_name"].map(ident["seconds_lo"])
            out.loc[has, f"status_{cfg}"] = out.loc[has, "instance_name"].map(ident["status_lo"])
            out.loc[has, f"nodes_source_{cfg}"] = "differential_scale (identity)"
            out.loc[has, f"nodes_{cfg}_labelling_min"] = out.loc[has, "instance_name"].map(g["min"])
            out.loc[has, f"nodes_{cfg}_labelling_max"] = out.loc[has, "instance_name"].map(g["max"])
    if node_counts.exists():
        nc = pd.read_csv(node_counts)
        nc = nc[nc["instance_name"].isin(names)]
        for cfg in CONFIGS:
            c = nc[nc["config"] == cfg].drop_duplicates("instance_name", keep="last").set_index("instance_name")
            has = out["instance_name"].isin(c.index)
            out.loc[has, f"nodes_{cfg}"] = out.loc[has, "instance_name"].map(c["nodes"])
            out.loc[has, f"seconds_{cfg}"] = out.loc[has, "instance_name"].map(c["seconds"])
            out.loc[has, f"status_{cfg}"] = out.loc[has, "instance_name"].map(c["status"])
            out.loc[has, f"nodes_source_{cfg}"] = "node_counts"
    return out


def certificate_records(names: list[str], certificate: Path = CERTIFICATE_CSV) -> pd.DataFrame:
    """The search certificate's node count and checker verdict per configuration (<= 75 customers)."""
    out = pd.DataFrame({"instance_name": names})
    for cfg in CONFIGS:
        out[f"cert_nodes_{cfg}"] = np.nan
        out[f"cert_ok_{cfg}"] = ""
    if not certificate.exists():
        return out
    c = pd.read_csv(certificate)
    c = c[c["instance_name"].isin(names)]
    for cfg in CONFIGS:
        cc = c[c["config"] == cfg].drop_duplicates("instance_name", keep="last").set_index("instance_name")
        out[f"cert_nodes_{cfg}"] = out["instance_name"].map(cc["nodes"])
        out[f"cert_ok_{cfg}"] = out["instance_name"].map(cc["check_ok"]).map({True: "ok", False: "FAIL"}).fillna("")
    return out


def proof_records(names: list[str], proofs: Path = PROOFS_CSV) -> pd.DataFrame:
    """The DRAT refutation of `optimum - 1` through the SAT path (n <= 40):
    verdict, solve seconds, conflicts."""
    out = pd.DataFrame({"instance_name": names, "drat_verdict": "", "drat_solve_seconds": np.nan,
                        "drat_conflicts": np.nan})
    if not proofs.exists():
        return out
    p = pd.read_csv(proofs)
    p = p[p["instance_name"].isin(names)].drop_duplicates("instance_name", keep="last").set_index("instance_name")
    out["drat_verdict"] = out["instance_name"].map(p["verdict"]).fillna("")
    out["drat_solve_seconds"] = out["instance_name"].map(p["solve_seconds"])
    out["drat_conflicts"] = out["instance_name"].map(p["conflicts"])
    return out


def join_records(names: list[str], **paths) -> pd.DataFrame:
    """Every record above on one row per instance."""
    parts = [sweep_records(names, **{k: v for k, v in paths.items() if k in ("results_dir", "files")}),
             ledger_records(names, **{k: v for k, v in paths.items() if k in ("ledger",)}),
             node_count_records(names, **{k: v for k, v in paths.items() if k in ("node_counts", "differential")}),
             certificate_records(names, **{k: v for k, v in paths.items() if k in ("certificate",)}),
             proof_records(names, **{k: v for k, v in paths.items() if k in ("proofs",)})]
    out = parts[0]
    for p in parts[1:]:
        out = out.merge(p, on="instance_name", how="left")
    return out


# ----------------------------------------------------------------------------
# the cost model's prediction
# ----------------------------------------------------------------------------


def cost_predictions(names: list[str]) -> pd.DataFrame:
    """`pred_log10_nodes_<cfg>` from `learning.cost_model`'s chosen variant
    (`linear + drift + gbm [row]`, refitted here on its training rows at
    n <= 75 for each configuration), `pred_seconds_<cfg>` at 0.65 us per node,
    and `in_training_<cfg>`: whether the instance's own count was among the
    rows the model was fitted on (true for the corpus instances at n <= 40 with
    a `node_counts` row), in which case the prediction is in-sample."""
    from learning.cost_model import CostModel, assemble, training_mask
    frame = assemble()
    sel = frame[frame["instance_name"].isin(names)].drop_duplicates("instance_name").set_index("instance_name")
    out = pd.DataFrame({"instance_name": names})
    for cfg in CONFIGS:
        mask = training_mask(frame, cfg)
        model = CostModel(drift=True, gbm=True, weighting="row").fit(frame[mask], cfg)
        pred = pd.Series(model.predict(sel.reset_index()), index=sel.index)
        trained = set(frame.loc[mask, "instance_name"])
        out[f"pred_log10_nodes_{cfg}"] = out["instance_name"].map(pred)
        out[f"pred_seconds_{cfg}"] = (10 ** out[f"pred_log10_nodes_{cfg}"] - 1.0) * SECONDS_PER_NODE
        out[f"in_training_{cfg}"] = out["instance_name"].isin(trained)
        out[f"cost_model_{cfg}"] = model.name
    return out


# ----------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------


def build(out: Path = OUT_CSV, with_cost_model: bool = True) -> pd.DataFrame:
    started = time.time()
    m = load()
    m = m[m["collection"].isin(COLLECTIONS)].copy()
    keep = ["instance_name", "source_file", "collection", "n", "m", "n_ones", "e", "r", "c", "e_g", "kappa", "gamma",
            "gamma_n", "forest", "lcc_cust_frac", "core2_cust_frac", "core2_prod_frac", "optimum", "provenance",
            "certified", "bound_gap"]
    m = m[keep]
    rule = load_rule()
    rule = rule[rule["instance_name"].isin(m["instance_name"])][["instance_name", "rule", "rule_seconds", "sizes"]]
    f = m.merge(rule, on="instance_name", how="left")
    inst = pd.read_csv(INSTANCES_CSV, usecols=["instance_name"] + BOUND_COLUMNS)
    f = f.merge(inst, on="instance_name", how="left")
    f["rule_gap"] = f["rule"] - f["optimum"]
    f["lb_gap"] = f["optimum"] - f["lb_best"]
    f["ub_gap"] = f["ub_best"] - f["optimum"]
    f["regime"] = [regime_of(e, r, bool(fo)) for e, r, fo in zip(f["e"], f["r"], f["forest"])]
    cells = [fb_cell(name) for name in f["instance_name"]]
    f["fb_m_nominal"] = [c[0] if c else np.nan for c in cells]
    f["fb_n_nominal"] = [c[1] if c else np.nan for c in cells]
    f = floor_columns(f)
    names = list(f["instance_name"])
    f = f.merge(join_records(names), on="instance_name", how="left")
    if with_cost_model:
        f = f.merge(cost_predictions(names), on="instance_name", how="left")
    f = f.sort_values(["collection", "n", "instance_name"]).reset_index(drop=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    f.to_csv(out, index=False)
    print(f"{len(f)} rows -> {out} in {time.time() - started:.0f}s", flush=True)
    return f


def load_scoop(path: Path = OUT_CSV) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist; run `python -m learning.excess_scoop --stage build` first")
    return pd.read_csv(path, low_memory=False)


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def _fmt_nodes(x) -> str:
    return "not recorded" if pd.isna(x) else f"{int(x):,}"


def scoop_table(f: pd.DataFrame) -> pd.DataFrame:
    """The per-instance table for the report, one row per SCOOP instance."""
    s = f[f["collection"] == "SCOOP"].sort_values("n")
    rows = []
    for r in s.itertuples():
        rows.append({
            "instance": r.instance_name.replace("scoop-", "").replace("_0", "", 1) if r.instance_name.endswith("_0") else r.instance_name,
            "n": r.n, "m": r.m, "ones": r.n_ones, "e": round(r.e, 2), "e_g(r)": round(r.e_g, 2),
            "κ": r.kappa, "γ": r.gamma, "2-core": f"{r.core2_cust_frac:.2f}", "regime": r.regime,
            "opt": int(r.optimum), "lb": int(r.lb_best), "ub": int(r.ub_best), "rule": int(r.rule),
            "floor<1": r.floor_lt1, "floor<.01": r.floor_lt001, "β*n": round(r.beta_star_n, 1),
            "nodes (default)": _fmt_nodes(r.nodes_default), "nodes (csearch)": _fmt_nodes(r.nodes_csearch),
            "nodes from": r.nodes_source_default.replace(" (identity)", ""),
            "SAT sweep s": f"{r.certified_seconds:.2f}" if pd.notna(r.certified_seconds) else "",
            "DRAT": r.drat_verdict or "",
            "pred log₁₀ nodes": f"{r.pred_log10_nodes_default:.1f}" if pd.notna(r.pred_log10_nodes_default) else "",
            "in-sample": "yes" if r.in_training_default else "no",
        })
    return pd.DataFrame(rows)


def regime_table(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for coll in COLLECTIONS:
        c = f[f["collection"] == coll]
        for regime in REGIME_ORDER:
            g = c[c["regime"] == regime]
            if not len(g):
                continue
            rows.append({"collection": coll, "regime": regime, "instances": len(g),
                         "n range": f"{g['n'].min()}-{g['n'].max()}",
                         "e range": f"{g['e'].min():.2f}-{g['e'].max():.2f}",
                         "rule exact": f"{(g['rule_gap'] == 0).mean():.2f}", "rule gap mean": g["rule_gap"].mean(),
                         "rule gap max": g["rule_gap"].max(), "lb tight": f"{(g['lb_gap'] == 0).mean():.2f}",
                         "lb gap max": g["lb_gap"].max(), "ub_best tight": f"{(g['ub_gap'] == 0).mean():.2f}",
                         "below floor<1": int(g["below_floor_1"].sum()),
                         "below floor<.01": int(g["below_floor_001"].sum()),
                         "floor<.01 = opt": int((g["floor_lt001"] == g["optimum"]).sum())})
    return pd.DataFrame(rows)


def fb_cell_table(f: pd.DataFrame) -> pd.DataFrame:
    c = f[f["collection"] == "Faggioli-Bentivoglio"]
    g = c.groupby(["fb_m_nominal", "fb_n_nominal"])
    t = g.agg(instances=("n", "size"), n=("n", "median"), m=("m", "median"), e_min=("e", "min"),
              e_med=("e", "median"), e_max=("e", "max"), forests=("forest", "sum"),
              decompose=("kappa", lambda s: int((s > 1).sum())), opt_med=("optimum", "median"),
              rule_exact=("rule_gap", lambda s: float((s == 0).mean())), rule_gap_max=("rule_gap", "max"),
              lb_tight=("lb_gap", lambda s: float((s == 0).mean())),
              below_floor_1=("below_floor_1", "sum"), below_floor_001=("below_floor_001", "sum"),
              nodes_default_med=("nodes_default", "median"), nodes_default_max=("nodes_default", "max"),
              pred_log10_med=("pred_log10_nodes_default", "median")).reset_index()
    t = t.rename(columns={"fb_m_nominal": "m nominal", "fb_n_nominal": "n nominal"})
    t["regimes"] = [", ".join(sorted(set(c[(c["fb_m_nominal"] == a) & (c["fb_n_nominal"] == b)]["regime"]),
                                     key=REGIME_ORDER.index)) for a, b in zip(t["m nominal"], t["n nominal"])]
    return t


def cost_table(f: pd.DataFrame) -> pd.DataFrame:
    """The cost model against every recorded count, per collection, in and out of sample."""
    rows = []
    for coll in COLLECTIONS:
        c = f[f["collection"] == coll]
        for cfg in CONFIGS:
            have = c[np.isfinite(c[f"nodes_{cfg}"]) & np.isfinite(c[f"pred_log10_nodes_{cfg}"])]
            for ins, label in ((True, "in-sample"), (False, "out-of-sample")):
                h = have[have[f"in_training_{cfg}"] == ins]
                if not len(h):
                    continue
                err = h[f"pred_log10_nodes_{cfg}"] - np.log10(1.0 + h[f"nodes_{cfg}"])
                rows.append({"collection": coll, "config": cfg, "rows": label, "counts": len(h),
                             "n range": f"{h['n'].min()}-{h['n'].max()}",
                             "MAE (decades)": err.abs().mean(), "bias": err.mean(), "max |err|": err.abs().max(),
                             "within a decade": (err.abs() <= 1.0).mean()})
    return pd.DataFrame(rows)


def corpus_floor_table(rule: pd.DataFrame | None = None) -> pd.DataFrame:
    """The same floor check over every certified corpus instance, per
    collection (Chu & Stuckey pooled; Harvey's files pooled), from
    `learning/data/excess_rule.csv`: how many optima sit below the floor at
    bound < 1 and at bound < 0.01, and the largest shortfall. Context for the
    SCOOP check: the floor is a random-model statement, and the structured
    Challenge instances sit far below it."""
    r = load_rule() if rule is None else rule
    c = r[(r["source"] == "corpus") & r["certified"]].copy()
    fl = [floors(int(n), sizes_from_text(sz)) for n, sz in zip(c["n"], c["sizes"])]
    c["floor_lt1"] = [a for a, _ in fl]
    c["floor_lt001"] = [b for _, b in fl]
    c["collection"] = np.where(c["generator"].eq("chu_stuckey"), "Chu & Stuckey",
                               np.where(c["cell"].str.startswith("wb"), "Harvey", c["cell"]))
    c["short_001"] = c["floor_lt001"] - c["optimum"]
    g = c.groupby("collection").agg(instances=("n", "size"), n_min=("n", "min"), n_max=("n", "max"),
                                   below_floor_1=("floor_lt1", lambda s: int((c.loc[s.index, "optimum"] < s).sum())),
                                   below_floor_001=("short_001", lambda s: int((s > 0).sum())),
                                   largest_shortfall_001=("short_001", lambda s: int(max(s.max(), 0)))).reset_index()
    return g.sort_values("instances", ascending=False)


def floor_violations(f: pd.DataFrame) -> pd.DataFrame:
    v = f[f["below_floor_001"] | f["below_floor_1"]]
    return v[["collection", "instance_name", "n", "m", "e", "kappa", "optimum", "floor_lt1", "floor_lt001",
              "beta_star_n", "below_floor_1", "below_floor_001"]].sort_values(["collection", "n"])


def tables(f: pd.DataFrame) -> str:
    s = f[f["collection"] == "SCOOP"]
    parts = ["## SCOOP, per instance\n", _md(scoop_table(f)), "",
             "## Per regime and collection\n", _md(regime_table(f)), "",
             "## Faggioli-Bentivoglio, per nominal cell (m patterns x n pieces)\n", _md(fb_cell_table(f)), "",
             "## The floor check (bound < 1 and < 0.01)\n", _md(floor_violations(f)), "",
             "## The floor check over every certified corpus instance, per collection\n", _md(corpus_floor_table()), "",
             "## The cost model against the counts on record\n", _md(cost_table(f)), ""]
    parts.append("## SCOOP summary\n")
    parts.append(f"- instances: {len(s)}, n {s['n'].min()}-{s['n'].max()}, m {s['m'].min()}-{s['m'].max()}, "
                 f"e {s['e'].min():.2f}-{s['e'].max():.2f} (median {s['e'].median():.2f})")
    parts.append(f"- regimes: {s['regime'].value_counts().reindex(REGIME_ORDER).dropna().astype(int).to_dict()}")
    parts.append(f"- decompose (κ > 1): {int((s['kappa'] > 1).sum())}; forests: {int(s['forest'].sum())}; "
                 f"median γ/n {s['gamma_n'].median():.2f}; median 2-core share of customers {s['core2_cust_frac'].median():.2f}")
    parts.append(f"- optimum: {int(s['optimum'].min())}-{int(s['optimum'].max())}; opt/n median {(s['optimum'] / s['n']).median():.3f}")
    parts.append(f"- lb_best tight on {int((s['lb_gap'] == 0).sum())}, gap max {int(s['lb_gap'].max())}; "
                 f"ub_best tight on {int((s['ub_gap'] == 0).sum())}, gap max {int(s['ub_gap'].max())}")
    parts.append(f"- the two-key rule: exact on {int((s['rule_gap'] == 0).sum())}, gap mean {s['rule_gap'].mean():.2f}, "
                 f"max {int(s['rule_gap'].max())}, gap/n max {(s['rule_gap'] / s['n']).max():.3f}; "
                 f"rule ≤ ub_best on {int((s['rule'] <= s['ub_best']).sum())}")
    parts.append(f"- floor < 0.01: tight (= opt) on {int((s['floor_lt001'] == s['optimum']).sum())}, "
                 f"below the optimum by a median of {(s['optimum'] - s['floor_lt001']).median():.0f}; "
                 f"instances below it: {int(s['below_floor_001'].sum())}; below the floor < 1: {int(s['below_floor_1'].sum())}")
    parts.append(f"- refutation counts on record: default {int(np.isfinite(s['nodes_default']).sum())}, "
                 f"csearch {int(np.isfinite(s['nodes_csearch']).sum())}; max nodes "
                 f"{_fmt_nodes(s['nodes_default'].max())} (default), {_fmt_nodes(s['nodes_csearch'].max())} (csearch); "
                 f"compute ledger rows: {int(s['ledger_rows'].sum())}; DRAT verified: {int((s['drat_verdict'] == 'verified').sum())}")
    parts.append(f"- SAT sweep seconds (whole binary search): median {s['certified_seconds'].median():.2f}, "
                 f"max {s['certified_seconds'].max():.0f} ({s.loc[s['certified_seconds'].idxmax(), 'instance_name']})")
    parts.append(f"- cost model (default), the two instances with no count: "
                 + "; ".join(f"{r.instance_name}: 10^{r.pred_log10_nodes_default:.1f} nodes, {r.pred_seconds_default:.1f} s at 0.65 µs"
                             for r in s[~np.isfinite(s['nodes_default'])].itertuples()))
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("build", "tables", "all"), default="all")
    ap.add_argument("--no-cost-model", action="store_true")
    ap.add_argument("--out", type=Path, default=OUT_CSV)
    args = ap.parse_args()
    if args.stage in ("build", "all"):
        f = build(args.out, with_cost_model=not args.no_cost_model)
    else:
        f = load_scoop(args.out)
    if args.stage in ("tables", "all"):
        print(tables(f))


if __name__ == "__main__":
    main()
