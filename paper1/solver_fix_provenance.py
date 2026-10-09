"""Which certified values rest only on the customer search (loop0007 item 06).

Every corpus value marked `certified:refutation` or `certified:bound` has a
witness that re-simulates to it, so the upper bound is never in question. The
question is the other half: what proves that `value - 1` is infeasible? Until
loop0007 the customer search applied Chu & Stuckey's published definite and
better moves, which are false as stated (`Search/PublishedTheorems.lean`), so a
refutation from it alone is not covered by the soundness theorem. This script
reads the records and sorts every certified instance into the evidence it has
that does *not* go through the customer search:

    lattice   the subset-lattice optimum (`learning.degeneracy`, n <= 15)
              equals the value; shares no code with the search
    drat      a DRAT refutation of `value - 1` through the SAT encoding,
              checked by drat-trim (`learning/data/proofs*.csv`, n <= 40)
    sat       the direct SAT binary search reported the instance solved at
              this value, in a sweep that finished before the customer search
              or the ratchet existed (`benchmarks/results/sweep_*.csv`,
              `overnight_20260917_0033_round*.csv`); or a SAT refutation in a
              recorded race (`learning/data/race_*.json`)
    bound     `_lower_bound` equals the value (trivial, clique, contraction
              degeneracy): each comes with a checkable object, a clique or a
              contraction sequence (`learning/data/instances.csv`, recomputed
              here for every instance this is the only evidence for)

Two more bounds are recorded and reported, but not counted as independent,
because each rests on a search of its own with no proof object: `tw_lo + 1`
(a refutation by `learning.treewidth`'s decision search; a theorem via
tw <= pw) and the expansion bound (`f(t)` by branch and bound)
(`learning/data/ensemble/conjecture_invariants.csv.gz`).
    isomorph  none of the above directly, but an instance with the same MOSP
              graph (nauty certificate, `learning/data/canonical.csv`) has one
              at the same value; the optimum depends only on the graph
              (`MOSPGraph.lean`)

What is left is the list item 07 has to re-check. For each, the configuration
that certified it is read from the compute ledger (`csearch`) and
`recertify/results.json`; otherwise from the solution file's git history (the
commit that first recorded the current value as certified).

Reads only; never writes to `solutions/`.

    python -m paper1.solver_fix_provenance          # CSV + summary
"""

from __future__ import annotations

import collections
import csv
import gzip
import json
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "paper1/data/solver_fix_provenance.csv"
OUT_ALL = ROOT / "paper1/data/solver_fix_provenance_all.csv.gz"
OUT_MD = ROOT / "paper1/data/solver_fix_provenance_tables.md"

# Sweeps whose `solved` rows came from the direct SAT binary search. All four
# finished before the ratchet (859fa9299, 2026-09-17 16:24) and the customer
# search (3f5faa03b, 2026-09-18 19:33) existed, so a `solved` row -- including
# one served from the cache -- was certified by SAT or by the lower bound.
SAT_SWEEPS = [
    "benchmarks/results/sweep_full.csv",
    "benchmarks/results/sweep_long.csv",
    "benchmarks/results/overnight_20260917_0033_round1.csv",
    "benchmarks/results/overnight_20260917_0033_round2.csv",
]
# Overlaps the ratchet's first commit and a symmetry-breaking experiment
# (231f4db73) found unsound and disabled the same afternoon: counted separately.
SAT_SWEEP_LATE = "benchmarks/results/overnight_20260917_1442_round1.csv"

# Code history the configuration is read against (commit times).
THEOREM2_ADDED = "2026-09-19T01:37"    # 0bc1a12d5: csearch turns it on where sparse
BETTER_MOVE_FIX_1 = "2026-09-22T23:49"  # d3b060c8a: the first better_move fix
BETTER_MOVE_FIX_2 = "2026-09-26T11:45"  # 0eb33915a: the second (bugs A, B, C)


_CACHE: list = []


def _instances():
    from learning.dataset import enumerate_instances
    if not _CACHE:
        _CACHE.extend(enumerate_instances())
    return _CACHE


def _corpus() -> pd.DataFrame:
    from satisfiability.customer_search import sparse_enough_for_better_move
    from satisfiability.mosp_solver import _solution_path

    rows = []
    for path, inst in _instances():
        sol = _solution_path(inst, ROOT / "solutions")
        if not sol.exists():
            continue
        data = json.loads(sol.read_text())
        rows.append({
            "instance_name": inst.name,
            "solution_file": str(sol.relative_to(ROOT)),
            "source_file": str(path),
            "n_customers": inst.n_customers,
            "n_patterns": inst.n_patterns,
            "value": int(data["mosp_value"]),
            "provenance": data.get("provenance", ""),
            "theorem2_sparse": sparse_enough_for_better_move(inst),
        })
    return pd.DataFrame(rows)


def _sat_sweeps(names: set[str]) -> tuple[dict, dict]:
    strict: dict[str, set[int]] = collections.defaultdict(set)
    late: dict[str, set[int]] = collections.defaultdict(set)
    for target, files in ((strict, SAT_SWEEPS), (late, [SAT_SWEEP_LATE])):
        for f in files:
            d = pd.read_csv(ROOT / f)
            for name, v in d.loc[d.status == "solved", ["instance_name", "mosp_value"]].itertuples(index=False):
                target[name].add(int(v))
    return strict, late


def _races() -> dict[str, set[int]]:
    out: dict[str, set[int]] = collections.defaultdict(set)
    for f in ("race_corpus", "race_sweep", "race_dense", "race_sparse"):
        p = ROOT / f"learning/data/{f}.json"
        if not p.exists():
            continue
        for r in json.loads(p.read_text())["rows"]:
            if r.get("sat_proof") == "refutation":
                out[r["instance"]].add(int(r["sat_value"]))
    return out


def _drat() -> dict[str, set[int]]:
    """Instance -> the k values with a drat-trim-verified refutation."""
    out: dict[str, set[int]] = collections.defaultdict(set)
    for f in ("proofs.csv", "proofs_200k.csv"):
        d = pd.read_csv(ROOT / "learning/data" / f, usecols=["instance_name", "k", "status", "verdict"])
        ok = d[(d.status == "unsat") & (d.verdict == "verified")]
        for name, k in ok[["instance_name", "k"]].itertuples(index=False):
            out[name].add(int(k))
    return out


def _lattice() -> dict[str, int]:
    d = pd.read_csv(ROOT / "learning/data/degeneracy.csv",
                    usecols=["instance_name", "min_search", "min_construction"])
    d = d[d.min_search == d.min_construction]
    return dict(zip(d.instance_name, d.min_search.astype(int)))


def _bounds() -> pd.DataFrame:
    inst = pd.read_csv(ROOT / "learning/data/instances.csv", usecols=["instance_name", "lb_best"])
    with gzip.open(ROOT / "learning/data/ensemble/conjecture_invariants.csv.gz", "rt") as fh:
        inv = pd.read_csv(fh, usecols=["instance_name", "source", "tw_lo", "exp"])
    inv = inv[inv.source == "corpus"].drop(columns="source")
    return inst.merge(inv, on="instance_name", how="outer")


def _ledger() -> tuple[dict, dict]:
    led = pd.read_csv(ROOT / "benchmarks/results/compute_ledger.csv")
    cs = led[led.driver == "csearch"].sort_values("when")
    csearch = {}
    for r in cs.itertuples(index=False):
        csearch[r.instance] = (r.when, r.nodes)
    rec = {}
    p = ROOT / "recertify/results.json"
    if p.exists():
        for r in json.loads(p.read_text()):
            rec[r["name"]] = r
    return csearch, rec


def _repaired_refutations() -> dict[str, set[str]]:
    """Instance -> the loop0007 runs that refuted `value - 1` with
    `repaired_rules=True` (items 04 and 05). Not independent of the customer
    search, but covered by the soundness theorem: what item 07 can reuse."""
    out: dict[str, set[str]] = collections.defaultdict(set)
    data = ROOT / "paper1/data"
    for f, tag in (("solver_fix_cost_cs.csv", "item04-cs"), ("solver_fix_cost_cs125.csv", "item04-cs125"),
                   ("solver_fix_cost_mosp40.csv", "item04-mosp40")):
        if not (data / f).exists():
            continue
        d = pd.read_csv(data / f, usecols=["instance_name", "optimum", "k", "setting", "status"])
        ok = d[(d.setting == "repaired") & (d.status == "unsat") & (d.k == d.optimum - 1)]
        for name, opt in ok[["instance_name", "optimum"]].itertuples(index=False):
            out[name].add(f"{tag}@{int(opt)}")
    for f, tag in (("solver_fix_diff40.csv.gz", "item05-diff40"), ("solver_fix_diff75.csv.gz", "item05-diff75")):
        if not (data / f).exists():
            continue
        d = pd.read_csv(data / f, usecols=["instance_name", "base_name", "optimum", "status_lo", "source"])
        ok = d[(d.source == "corpus") & (d.status_lo == "unsat")]
        for name, opt in ok[["base_name", "optimum"]].drop_duplicates().itertuples(index=False):
            out[name].add(f"{tag}@{int(opt)}")
    return out


def _git_first_certified(solution_file: str, value: int) -> tuple[str, str, str]:
    """The oldest commit whose version of the file has the current value and a
    certified provenance, after the last commit where it had not."""
    log = subprocess.run(
        ["git", "log", "--format=%h %cI %s", "--", solution_file],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    first = ("", "", "")
    for line in log:  # newest first
        h, when, subject = line.split(" ", 2)
        try:
            blob = subprocess.run(["git", "show", f"{h}:{solution_file}"], cwd=ROOT,
                                  capture_output=True, text=True, check=True).stdout
            data = json.loads(blob)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            break
        prov = data.get("provenance")
        if int(data["mosp_value"]) != value or prov == "solution":
            break
        # Before the field existed (backfilled 2026-09-18) a file had no
        # provenance; it is marked so the reader can tell.
        first = (h, when, subject if prov else subject + " [pre-provenance]")
    return first


def _config(row, csearch, rec) -> tuple[str, str, str]:
    """(run, Theorem 2, better_move code) for the run that certified the value.

    Read from the commit that first recorded the current value as certified,
    the compute ledger and `recertify/results.json`. Every run below applied
    the definite move as Chu & Stuckey publish it: no run before loop0007 had
    the repaired premise.
    """
    name, when = row.instance_name, str(row.certified_when)[:16]
    subject = str(row.certified_commit_subject)
    if (name in rec and rec[name]["status"] == "unsat") or "ecertif" in subject:
        # recertify started 2026-09-24 and its processes kept the code they
        # loaded: every recertify count is pre-second-fix (CLAUDE.md, §5).
        return ("recertify: decide(value - 1, better_move=True, dominators=all, memo)",
                "on", "first fix (pre-0eb33915)")
    if subject.startswith("Correct the corpus"):
        return ("re-refutation after the first better_move fix, 2026-09-23",
                "on", "first fix (pre-0eb33915)")
    if subject.startswith("Close 111"):
        return ("customer-search sweep, 2026-09-18: solve() defaults "
                "(definite, subset, memo), then re-refuted the same way", "off", "none")
    # A commit lands after the run it records; a ledger row is written when
    # the run ends, so it dates the run better where one exists.
    if name in csearch and str(csearch[name][0])[:16] <= when:
        when = str(csearch[name][0])[:16]
    t2 = row.theorem2_sparse and when >= THEOREM2_ADDED
    if when >= BETTER_MOVE_FIX_2:
        code = "second fix"
    elif when >= BETTER_MOVE_FIX_1:
        code = "first fix (pre-0eb33915)"
    else:
        code = "original (bugs A, B)" + ("; one of the 55 re-refuted with the first fix on 2026-09-23" if t2 else "")
    run = f"benchmarks.csearch, {when[:10]}: solve() defaults" + (" + Theorem 2" if t2 else "")
    return (run, "on" if t2 else "off", code if t2 else "none")


def main() -> None:
    corpus = _corpus()
    names = set(corpus.instance_name)
    sat, sat_late = _sat_sweeps(names)
    races = _races()
    drat = _drat()
    lattice = _lattice()
    bounds = _bounds().set_index("instance_name")
    canon = pd.read_csv(ROOT / "learning/data/canonical.csv", usecols=["instance_name", "graph_cert"])
    cert_of = dict(zip(canon.instance_name, canon.graph_cert))
    csearch, rec = _ledger()

    def ev(r) -> dict:
        v, n = r.value, r.instance_name
        b = bounds.loc[n] if n in bounds.index else None
        lb = int(b.lb_best) if b is not None and pd.notna(b.lb_best) else 0
        tw1 = int(b.tw_lo) + 1 if b is not None and pd.notna(b.tw_lo) else 0
        exp = int(b.exp) if b is not None and pd.notna(b.exp) else 0
        return {
            "ev_lattice": lattice.get(n) == v,
            "ev_drat": (v - 1) in drat.get(n, ()),
            "ev_sat": v in sat.get(n, ()) or v in races.get(n, ()),
            "ev_sat_late": v in sat_late.get(n, ()),
            "ev_bound": lb == v,
            "ev_treewidth": tw1 == v,
            "ev_expansion": exp == v,
            "lb_best": lb, "tw1": tw1, "exp": exp,
            "bound_above_value": max(lb, tw1, exp) > v,
            "ev_csearch_ledger": n in csearch,
            "ev_recertify": n in rec and rec[n]["status"] == "unsat",
        }

    E = pd.DataFrame([ev(r) for r in corpus.itertuples(index=False)])
    df = pd.concat([corpus.reset_index(drop=True), E], axis=1)
    df["graph_cert"] = df.instance_name.map(cert_of)
    df["certified"] = df.provenance.isin(["certified:refutation", "certified:bound"])
    df["direct"] = df.ev_lattice | df.ev_drat | df.ev_sat | df.ev_bound
    # The bound is the only evidence for some instances: recompute it rather
    # than trust a recorded column.
    from satisfiability.mosp_solver import _lower_bound
    from mosp.instance import MOSPInstance
    sole = df.ev_bound & ~(df.ev_lattice | df.ev_drat | df.ev_sat)
    by_name = {inst.name: inst for _, inst in _instances()}
    for i in df.index[sole]:
        lb_now = _lower_bound(by_name[df.at[i, "instance_name"]])
        df.at[i, "lb_recomputed"] = lb_now
        if lb_now != df.at[i, "value"]:
            print("bound not reproduced:", df.at[i, "instance_name"], lb_now, df.at[i, "value"])
            df.at[i, "ev_bound"] = False
    df["direct"] = df.ev_lattice | df.ev_drat | df.ev_sat | df.ev_bound
    good = set(zip(df.loc[df.direct, "graph_cert"], df.loc[df.direct, "value"]))
    df["ev_isomorph"] = ~df.direct & df.apply(lambda r: (r.graph_cert, r.value) in good, axis=1)
    df["independent"] = df.direct | df.ev_isomorph

    def first_kind(r) -> str:
        for k in ("lattice", "drat", "sat", "bound", "isomorph"):
            if r[f"ev_{k}"]:
                return k
        return "customer search only"

    df["evidence"] = df.apply(first_kind, axis=1)
    if df.bound_above_value.any():
        print("WARNING: a proved bound above a stored value:",
              df.loc[df.bound_above_value, "instance_name"].tolist())

    only = df[df.certified & ~df.independent].copy()
    git = only.apply(lambda r: _git_first_certified(r.solution_file, r.value), axis=1)
    only["certified_commit"] = [g[0] for g in git]
    only["certified_when"] = [g[1] for g in git]
    only["certified_commit_subject"] = [g[2] for g in git]
    conf = only.apply(lambda r: _config(r, csearch, rec), axis=1)
    only["configuration"] = [c[0] for c in conf]
    only["theorem2"] = [c[1] for c in conf]
    only["better_move_code"] = [c[2] for c in conf]
    only["definite_move"] = "published (Chu & Stuckey Theorem 1, false as stated)"
    only["ledger_when"] = only.instance_name.map(lambda n: csearch.get(n, ("", ""))[0])
    only["ledger_nodes"] = only.instance_name.map(lambda n: csearch.get(n, ("", ""))[1])
    only["recertify_nodes"] = only.instance_name.map(lambda n: rec.get(n, {}).get("nodes", ""))
    rep = _repaired_refutations()
    only["repaired_refuted"] = [
        ";".join(sorted(t for t in rep.get(r.instance_name, ()) if t.endswith(f"@{r.value}")))
        for r in only.itertuples(index=False)]
    only["sat_late_solved"] = only.ev_sat_late
    only["secondary_evidence"] = [
        "+".join(k for k in ("treewidth", "expansion", "sat_late") if r[f"ev_{k}"]) or ""
        for _, r in only.iterrows()]
    only = only.sort_values(["n_customers", "n_patterns", "instance_name"])
    cols = ["instance_name", "value", "configuration", "theorem2", "better_move_code",
            "definite_move", "n_customers", "n_patterns",
            "provenance", "lb_best", "tw1", "exp", "secondary_evidence", "certified_commit", "certified_when",
            "certified_commit_subject", "ledger_when", "ledger_nodes", "recertify_nodes",
            "sat_late_solved", "repaired_refuted", "graph_cert", "source_file", "solution_file"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    only[cols].to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    df.drop(columns=[]).to_csv(OUT_ALL, index=False, compression="gzip")
    _tables(df, only)


BANDS = ((1, 15), (16, 40), (41, 75), (76, 100), (101, 134))


def _band(n: int) -> str:
    for lo, hi in BANDS:
        if lo <= n <= hi:
            return f"{lo}-{hi}"
    return "?"


def _tables(df: pd.DataFrame, only: pd.DataFrame) -> None:
    lines = ["# Item 06: evidence for each certified value", ""]
    lines.append(f"Corpus files: {len(df):,}; certified: {int(df.certified.sum()):,}; "
                 f"open: {int((~df.certified).sum())}.")
    lines.append("")
    lines.append("## First independent evidence, by size (certified instances)")
    lines.append("")
    c = df[df.certified].copy()
    c["band"] = c.n_customers.map(_band)
    t = pd.crosstab(c.band, c.evidence, margins=True, margins_name="all")
    t = t.reindex([f"{lo}-{hi}" for lo, hi in BANDS] + ["all"]).fillna(0)
    order = [k for k in ("lattice", "drat", "sat", "bound", "isomorph", "customer search only", "all") if k in t.columns]
    t = t[order]
    lines.append("| customers | " + " | ".join(order) + " |")
    lines.append("|---|" + "---:|" * len(order))
    for band, r in t.iterrows():
        lines.append(f"| {band} | " + " | ".join(f"{int(x):,}" for x in r) + " |")
    lines.append("")
    lines.append("## Each kind of evidence on its own (certified instances, not exclusive)")
    lines.append("")
    lines.append("| evidence | instances |")
    lines.append("|---|---:|")
    for k in ("lattice", "drat", "sat", "bound", "treewidth", "expansion", "sat_late",
              "csearch_ledger", "recertify"):
        lines.append(f"| {k} | {int(c[f'ev_{k}'].sum()):,} |")
    lines.append("")
    lines.append(f"## Customer search only: {len(only)} instances "
                 f"({only.graph_cert.nunique()} distinct graphs)")
    lines.append("")
    lines.append("| certifying run (definite move as published in every row) | instances |")
    lines.append("|---|---:|")
    for (k, t2, code), v in only.groupby(["configuration", "theorem2", "better_move_code"]).size().items():
        lines.append(f"| {k}; Theorem 2 {t2}; better_move code: {code} | {v} |")
    lines.append("")
    has = only.repaired_refuted.astype(bool)
    lines.append(f"Already refuted at `value - 1` by the repaired solver in items 04-05 "
                 f"(covered by the theorem, not independent of the search): "
                 f"**{int(has.sum())} of {len(only)}**; not yet: {int((~has).sum())}.")
    lines.append("")
    lines.append("| size class (customers × products) | instances | values |")
    lines.append("|---|---:|---|")
    g = only.groupby(["n_customers", "n_patterns"])
    for (n, m), grp in g:
        lines.append(f"| {n} × {m} | {len(grp)} | {', '.join(str(v) for v in sorted(grp.value))} |")
    OUT_MD.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
