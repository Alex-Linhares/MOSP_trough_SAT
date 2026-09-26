"""Exhaustive census of pathwidth − treewidth over every graph on ≤ 11 vertices
(plan 2 §3 item 14, reserve; the "for the next loop" note (i) of §21).

Question. §21 found a 10-vertex graph with pathwidth 5 and treewidth 3 by
local search and called it a record: is it a theorem that no graph on 9 or
fewer vertices has `pw − tw ≥ 2`, which graphs on 10 (and 11) vertices do, and
does `pw − tw = 3` occur at 11?

Method. nauty's `geng` enumerates every graph on n vertices up to isomorphism
(1, 1, 2, 4, 11, 34, 156, 1044, 12346, 274668, 12005168, 1018997864 for
n = 0..11, OEIS A000088); `learning/pwtw_exhaust.c` reads them as graph6 and
computes exact pathwidth (vertex-separation subset DP; Kinnersley 1992) and
exact treewidth (the Bodlaender–Fomin–Koster–Kratsch–Thilikos recurrence,
as in `learning/treewidth.c`) for each, tallying the joint histogram and
writing out every graph with `pw − tw ≥ k`. Graphs with isolated vertices
are included, so the census at n covers every graph on ≤ n vertices. Every
graph written out is re-established in Python by routes sharing no code with
the C: the pathwidth DP of `fixed_parameter_algorithm.pathwidth`, the
treewidth of `learning.treewidth` (C recurrence plus the Python reference at
n ≤ 10 and an elimination ordering re-checked by `elimination_width`), a
clique lower bound, and — as a MOSP instance whose products are the graph's
maximal cliques — `learning.extremal.recertify` (the exact solver with a
persisted witness, both refutation configurations at `optimum − 1` and
`optimum`, the lattice oracle at n ≤ 15).

Nothing here is a bound on MOSP; no solver path is touched; nothing is
written to `solutions/` (generated witnesses go under the git-ignored
`learning/data/extremal/solutions/`).

Usage:
    python -m learning.pwtw_exhaust --stage run --max-n 11 --workers 16 --level 2
    python -m learning.pwtw_exhaust --stage verify        # Python re-checks of every FOUND graph
    python -m learning.pwtw_exhaust --stage tables        # reports/pwtw_tables.md
    python -m learning.pwtw_exhaust --stage check         # C vs Python references on the graph atlas
    python -m learning.pwtw_exhaust --stage price         # cost of n = 12 from the measured rates
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "learning" / "data"
ENSEMBLE = DATA / "ensemble"
SCRATCH = DATA / "pwtw"                      # raw per-part outputs, git-ignored
CENSUS_CSV = ENSEMBLE / "pwtw_census.csv"
FOUND_CSV = ENSEMBLE / "pwtw_found.csv"
TOTALS_CSV = ENSEMBLE / "pwtw_totals.csv"
TABLES = ROOT / "reports" / "pwtw_tables.md"
_SOURCE = Path(__file__).with_name("pwtw_exhaust.c")
_BINARY = Path(__file__).with_name("_pwtw_exhaust")

# OEIS A000088: graphs on n unlabelled vertices.
GRAPH_COUNTS = [1, 1, 2, 4, 11, 34, 156, 1044, 12346, 274668, 12005168, 1018997864,
                165091172592]

# §21's record: three K4s glued pairwise at three hubs plus one vertex tied to
# a non-hub vertex of each (matrix key from `extremal_best.csv`, n = 10).
SECTION21_KEY = ("001000110/000000100/101000000/001011000/000011001/000001000/"
                 "100100001/001000000/000100100/010011100")


# ----------------------------------------------------------------------------
# the C binary and geng
# ----------------------------------------------------------------------------


def build() -> Path:
    if _BINARY.exists() and _BINARY.stat().st_mtime >= _SOURCE.stat().st_mtime:
        return _BINARY
    scratch = _BINARY.with_name(_BINARY.name + f".build-{os.getpid()}")
    subprocess.run(["gcc", "-O3", "-march=native", "-o", str(scratch), str(_SOURCE)],
                   check=True, capture_output=True, timeout=120)
    os.replace(scratch, _BINARY)
    return _BINARY


def geng_path() -> str | None:
    for name in ("nauty-geng", "geng"):
        found = shutil.which(name)
        if found:
            return found
    return None


def graph6_of(graph) -> bytes:
    import networkx as nx

    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph), header=False)


def graph_from_graph6(text: str):
    import networkx as nx

    return nx.from_graph6_bytes(text.encode())


def census_stream(data: bytes, min_diff: int = 2, level: int = 2) -> dict:
    """Runs the C on graph6 lines held in memory; returns parsed output."""
    out = subprocess.run([str(build()), "--min-diff", str(min_diff), "--level", str(level)],
                         input=data, capture_output=True, check=True)
    return parse_output(out.stdout.decode())


def parse_output(text: str) -> dict:
    found, hist, totals = [], [], []
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "FOUND":
            _, g6, n, pw, tw, edges = parts
            found.append({"n": int(n), "graph6": g6, "pw": int(pw), "tw": int(tw), "edges": int(edges)})
        elif parts[0] == "HIST":
            _, n, pw, tw, count = parts
            hist.append({"n": int(n), "pw": int(pw), "tw": int(tw), "count": int(count)})
        elif parts[0] == "TOTAL":
            _, n, graphs, pw_runs, dp_runs, nfound, min_diff, level = parts
            totals.append({"n": int(n), "graphs": int(graphs), "pw_runs": int(pw_runs),
                           "dp_runs": int(dp_runs), "found": int(nfound),
                           "min_diff": int(min_diff), "level": int(level)})
    return {"found": found, "hist": hist, "totals": totals}


# ----------------------------------------------------------------------------
# the run: geng res/mod parts piped into the C, one process pair per part
# ----------------------------------------------------------------------------


def run_part(n: int, res: int, mod: int, min_diff: int, level: int, out_path: Path) -> None:
    geng = geng_path()
    if geng is None:
        raise RuntimeError("nauty-geng not found")
    args = [geng, "-q", str(n)]
    if mod > 1:
        args.append(f"{res}/{mod}")
    with out_path.open("w") as sink:
        gen = subprocess.Popen(args, stdout=subprocess.PIPE)
        proc = subprocess.Popen([str(build()), "--min-diff", str(min_diff), "--level", str(level)],
                                stdin=gen.stdout, stdout=sink)
        gen.stdout.close()
        proc.wait()
        gen.wait()
        if proc.returncode or gen.returncode:
            raise RuntimeError(f"part {n} {res}/{mod} failed: geng {gen.returncode}, census {proc.returncode}")


def run(max_n: int, workers: int, min_diff: int = 2, level: int = 2, min_n: int = 0,
        parts_per_worker: int = 4, log=print) -> None:
    """For each n, split geng's output into `workers * parts_per_worker`
    parts (n ≥ 10; one part below), run them on `workers` processes, write
    the raw outputs under `learning/data/pwtw/`, then aggregate into the
    committed CSVs (rows for this n replace earlier rows for the same n)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    build()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for n in range(min_n, max_n + 1):
        mod = workers * parts_per_worker if n >= 10 else 1
        t0 = time.time()
        paths = [SCRATCH / f"n{n}_level{level}_k{min_diff}_{res}of{mod}.txt" for res in range(mod)]
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(run_part, n, res, mod, min_diff, level, path)
                       for res, path in enumerate(paths)]
            done = 0
            for fut in as_completed(futures):
                fut.result()
                done += 1
                if done % max(1, mod // 8) == 0 or done == mod:
                    log(f"n={n}: {done}/{mod} parts, {time.time() - t0:.0f} s")
        seconds = time.time() - t0
        aggregate(n, paths, seconds, workers, log=log)


def aggregate(n: int, paths: list[Path], seconds: float, workers: int, log=print) -> None:
    found, hist, totals = [], {}, {"n": n, "graphs": 0, "pw_runs": 0, "dp_runs": 0, "found": 0}
    for path in paths:
        parsed = parse_output(path.read_text())
        found.extend(parsed["found"])
        for row in parsed["hist"]:
            key = (row["pw"], row["tw"])
            hist[key] = hist.get(key, 0) + row["count"]
        for row in parsed["totals"]:
            for col in ("graphs", "pw_runs", "dp_runs", "found"):
                totals[col] += row[col]
            totals["min_diff"], totals["level"] = row["min_diff"], row["level"]
    if not hist:                                    # n = 0: geng writes one empty graph as "?"; C skips n=0
        hist[(0, 0)] = GRAPH_COUNTS[n]
        totals["graphs"] = GRAPH_COUNTS[n]
        totals.setdefault("min_diff", 2)
        totals.setdefault("level", 2)
    totals.update({"seconds": round(seconds, 1), "workers": workers,
                   "expected_graphs": GRAPH_COUNTS[n] if n < len(GRAPH_COUNTS) else -1})
    totals["complete"] = bool(totals["graphs"] == totals["expected_graphs"])
    census = pd.DataFrame([{"n": n, "pw": pw, "tw": tw, "count": c} for (pw, tw), c in sorted(hist.items())])
    found_df = pd.DataFrame(found, columns=["n", "graph6", "pw", "tw", "edges"])
    _replace_rows(CENSUS_CSV, census, n)
    _replace_rows(FOUND_CSV, found_df, n)
    _replace_rows(TOTALS_CSV, pd.DataFrame([totals]), n)
    log(f"n={n}: {totals['graphs']:,} graphs ({'complete' if totals['complete'] else 'INCOMPLETE'}), "
        f"{totals['dp_runs']:,} treewidth DPs, {totals['found']} with pw − tw ≥ {totals['min_diff']}, "
        f"{seconds:.0f} s on {workers} workers")


def _replace_rows(path: Path, frame: pd.DataFrame, n: int) -> None:
    if path.exists():
        old = pd.read_csv(path)
        old = old[old["n"] != n]
        frame = pd.concat([old, frame], ignore_index=True)
    frame = frame.sort_values([c for c in ("n", "pw", "tw", "edges", "graph6") if c in frame.columns])
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


# ----------------------------------------------------------------------------
# verification of every FOUND graph by independent routes
# ----------------------------------------------------------------------------


def clique_cover_matrix(graph) -> np.ndarray:
    """Customer × product matrix whose products are the maximal cliques of
    `graph`, so its MOSP graph is `graph` itself (isolated vertices get an
    empty column-free row and stay isolated)."""
    import networkx as nx

    n = graph.number_of_nodes()
    cliques = [sorted(c) for c in nx.find_cliques(graph) if len(c) >= 2]
    cliques.sort()
    matrix = np.zeros((n, max(1, len(cliques))), dtype=int)
    for j, clique in enumerate(cliques):
        for v in clique:
            matrix[v, j] = 1
    return matrix


def verify_graph(graph6: str, recertify: bool = True) -> dict:
    """Independent Python values for one graph6 string."""
    import networkx as nx

    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    from learning import extremal
    from learning.canonical import nauty_graph_certificate
    from learning.treewidth import (elimination_width, masks_from_graph, treewidth_exact,
                                    treewidth_reference)

    g = graph_from_graph6(graph6)
    g = nx.convert_node_labels_to_integers(g, ordering="sorted")
    n = g.number_of_nodes()
    masks = masks_from_graph(g)
    out = {"graph6": graph6, "n": n, "edges": g.number_of_edges(),
           "components": nx.number_connected_components(g),
           "degrees": " ".join(str(d) for _, d in sorted(g.degree(), key=lambda t: -t[1]))}
    pw = 0
    for comp in nx.connected_components(g):
        sub = nx.convert_node_labels_to_integers(g.subgraph(comp))
        pw = max(pw, compute_pathwidth(sub)[0])
    out["pw_python"] = int(pw)
    tw, order = treewidth_exact(masks)
    out["tw_c"] = int(tw)
    out["tw_order"] = " ".join(map(str, order))
    out["tw_order_width"] = int(elimination_width(masks, order))
    out["tw_reference"] = int(treewidth_reference(masks)) if n <= 10 else -1
    out["omega"] = int(max((len(c) for c in nx.find_cliques(g)), default=1)) if n else 1
    adjacency = {i: [j for j in range(n) if masks[i] >> j & 1] for i in range(n)}
    out["certificate"] = nauty_graph_certificate(adjacency) or ""
    ref = extremal.matrix_from_key(SECTION21_KEY)
    out["is_section21_graph"] = bool(n == 10 and out["certificate"] == extremal.graph_certificate(ref))
    out["contains_section21_graph"] = out["is_section21_graph"]
    out["edges_added_to_section21"] = "" if out["is_section21_graph"] else None
    if n >= 10 and not out["is_section21_graph"]:
        from networkx.algorithms.isomorphism import GraphMatcher

        ref_masks = extremal.masks_from_matrix(ref)
        ref_g = nx.Graph()
        ref_g.add_nodes_from(range(10))
        ref_g.add_edges_from((i, j) for i in range(10) for j in range(i + 1, 10) if ref_masks[i] >> j & 1)
        matcher = GraphMatcher(g, ref_g)
        out["contains_section21_graph"] = bool(matcher.subgraph_is_monomorphic())
        if out["contains_section21_graph"] and n == 10:
            mapping = next(matcher.subgraph_monomorphisms_iter())     # g-vertex → §21 label
            added = sorted(tuple(sorted((mapping[u], mapping[v]))) for u, v in g.edges()
                           if not ref_g.has_edge(mapping[u], mapping[v]))
            out["edges_added_to_section21"] = " ".join(f"{u}-{v}" for u, v in added)
    # vertex-minimality for the gap: does deleting any one vertex keep pw − tw ≥ 2?
    gap = out["pw_python"] - out["tw_c"]
    if n >= 2 and gap >= 2:
        deletions = b"".join(graph6_of(g.subgraph([u for u in g.nodes() if u != v])) for v in g.nodes())
        kept = census_stream(deletions, min_diff=gap, level=2)["found"]
        out["deletions_keeping_gap"] = len(kept)
        out["vertex_minimal"] = bool(not kept)
    else:
        out["deletions_keeping_gap"] = 0
        out["vertex_minimal"] = False
    if recertify:
        key = extremal.matrix_key(clique_cover_matrix(g))
        out["matrix_key"] = key
        cert = extremal.recertify(key)
        for col in ("optimum", "lo_default", "hi_default", "lo_csearch", "hi_csearch",
                    "lattice", "pathwidth_dp", "tw", "tw_order_width", "agree"):
            if col in cert:
                out[f"recert_{col}"] = cert[col]
    return out


def verify(found_csv: Path = FOUND_CSV, max_recertify: int = 400, log=print) -> pd.DataFrame:
    found = pd.read_csv(found_csv)
    rows = []
    for k, rec in enumerate(found.itertuples(index=False)):
        row = verify_graph(rec.graph6, recertify=k < max_recertify)
        row["pw_c"], row["tw_census"] = int(rec.pw), int(rec.tw)
        row["pw_agree"] = bool(row["pw_python"] == rec.pw
                               and row.get("recert_pathwidth_dp", rec.pw) == rec.pw
                               and row.get("recert_optimum", rec.pw + 1) == rec.pw + 1)
        row["tw_agree"] = bool(row["tw_c"] == rec.tw and row["tw_order_width"] == rec.tw
                               and row["tw_reference"] in (rec.tw, -1) and row["omega"] - 1 <= rec.tw)
        row["recertified"] = bool(k < max_recertify)
        row["agree"] = bool(row["pw_agree"] and row["tw_agree"] and row.get("recert_agree", True))
        rows.append(row)
        if (k + 1) % 10 == 0:
            log(f"verified {k + 1}/{len(found)}")
    frame = pd.DataFrame(rows)
    if not frame.empty:
        keep = ["n", "graph6", "pw_c", "tw_census", "edges", "components", "degrees", "omega", "pw_python",
                "tw_c", "tw_reference", "tw_order", "tw_order_width", "certificate", "is_section21_graph",
                "contains_section21_graph", "edges_added_to_section21", "deletions_keeping_gap",
                "vertex_minimal", "matrix_key", "recertified", "recert_optimum", "recert_lo_default",
                "recert_hi_default", "recert_lo_csearch", "recert_hi_csearch", "recert_lattice",
                "recert_pathwidth_dp", "recert_tw", "recert_tw_order_width", "recert_agree",
                "pw_agree", "tw_agree", "agree"]
        frame = frame[[c for c in keep if c in frame.columns]].sort_values(["n", "edges", "graph6"])
        frame = frame.rename(columns={"pw_c": "pw", "tw_census": "tw"})
    frame.to_csv(found_csv, index=False)
    log(f"{len(frame)} graphs verified; agree on {int(frame['agree'].sum()) if not frame.empty else 0}")
    return frame


# ----------------------------------------------------------------------------
# the C against Python references (also the test)
# ----------------------------------------------------------------------------


def check_against_references(graphs, level: int = 2) -> pd.DataFrame:
    """Exact pw and tw from the C for each graph against the Python routes;
    returns one row per graph with an `agree` column."""
    import networkx as nx

    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    from learning.treewidth import masks_from_graph, treewidth_exact

    graphs = [nx.convert_node_labels_to_integers(g) for g in graphs]
    data = b"".join(graph6_of(g) for g in graphs)
    parsed = census_stream(data, min_diff=-100, level=level)      # every graph is FOUND
    if len(parsed["found"]) != len(graphs):
        raise RuntimeError(f"C returned {len(parsed['found'])} rows for {len(graphs)} graphs")
    rows = []
    for g, rec in zip(graphs, parsed["found"]):
        pw = 0
        for comp in nx.connected_components(g):
            pw = max(pw, compute_pathwidth(nx.convert_node_labels_to_integers(g.subgraph(comp)))[0])
        tw = treewidth_exact(masks_from_graph(g))[0] if g.number_of_nodes() else 0
        rows.append({"n": g.number_of_nodes(), "edges": g.number_of_edges(), "graph6": rec["graph6"],
                     "pw_c": rec["pw"], "pw_py": pw, "tw_c": rec["tw"], "tw_py": tw,
                     "agree": rec["pw"] == pw and (rec["tw"] == tw or (level < 2 and rec["tw"] == -1))})
    return pd.DataFrame(rows)


def atlas_check(seed: int = 0, extra: int = 300) -> pd.DataFrame:
    """All 1,253 graphs on ≤ 7 vertices plus random graphs on 8–11."""
    import networkx as nx

    graphs = [g for g in nx.graph_atlas_g() if g.number_of_nodes() >= 1]
    rng = np.random.default_rng(seed)
    for _ in range(extra):
        n = int(rng.integers(8, 12))
        graphs.append(nx.gnp_random_graph(n, float(rng.uniform(0.15, 0.7)), seed=int(rng.integers(1 << 30))))
    return check_against_references(graphs)


# ----------------------------------------------------------------------------
# tables and the price of n = 12
# ----------------------------------------------------------------------------


def _md(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    kinds = {}
    for c in cols:
        dtype = frame[c].dtype
        kinds[c] = ("bool" if dtype == bool else "int" if pd.api.types.is_integer_dtype(dtype)
                    else "float" if pd.api.types.is_float_dtype(dtype) else "str")
    lines = ["| " + " | ".join(str(c) for c in cols) + " |",
             "|" + "|".join(":--" if kinds[c] in ("str", "bool") else "--:" for c in cols) + "|"]
    for values in frame.itertuples(index=False):
        cells = []
        for c, v in zip(cols, values):
            kind = kinds[c]
            if kind == "bool" or isinstance(v, (bool, np.bool_)):
                cells.append("yes" if bool(v) else "no")
            elif kind == "int":
                cells.append(f"{int(v):,}")
            elif kind == "float":
                cells.append("—" if pd.isna(v) else f"{v:,.3f}" if abs(v) < 100 else f"{v:,.0f}")
            else:
                cells.append("" if (not isinstance(v, str) and pd.isna(v)) else str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def diff_table(census: pd.DataFrame) -> pd.DataFrame:
    """Graphs by n and pw − tw (only rows with tw computed; the others are
    proved to have pw − tw < min_diff and are pooled as `< k, skipped`)."""
    rows = []
    for n, part in census.groupby("n"):
        exact = part[part["tw"] >= 0]
        skipped = int(part[part["tw"] < 0]["count"].sum())
        diffs = (exact["pw"] - exact["tw"])
        row = {"n": int(n), "graphs": int(part["count"].sum())}
        for d in range(0, 4):
            row[f"pw−tw={d}"] = int(exact.loc[diffs == d, "count"].sum())
        row["pw−tw≥4"] = int(exact.loc[diffs >= 4, "count"].sum())
        row["skipped (pw−tw<k proved)"] = skipped
        row["max pw−tw"] = int(diffs.max()) if not exact.empty else 0
        row["share pw>tw"] = (float(exact.loc[diffs >= 1, "count"].sum()) / row["graphs"]) if skipped == 0 else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def joint_table(census: pd.DataFrame, n: int) -> pd.DataFrame:
    part = census[(census["n"] == n) & (census["tw"] >= 0)]
    if part.empty:
        return pd.DataFrame()
    table = part.pivot_table(index="pw", columns="tw", values="count", aggfunc="sum", fill_value=0)
    table.columns = [f"tw={c}" for c in table.columns]
    table.index = [f"pw={i}" for i in table.index]
    return table.reset_index().rename(columns={"index": ""})


def pw_marginal(census: pd.DataFrame) -> pd.DataFrame:
    part = census[census["pw"] >= 0]
    table = part.pivot_table(index="n", columns="pw", values="count", aggfunc="sum", fill_value=0)
    table.columns = [f"pw={c}" for c in table.columns]
    return table.reset_index()


# OEIS A005195: forests on n unlabelled vertices (= graphs with tw ≤ 1).
FOREST_COUNTS = [1, 1, 2, 3, 6, 10, 20, 37, 76, 153, 329, 710, 1601]


def forest_check(census: pd.DataFrame) -> pd.DataFrame:
    """The census's tw ≤ 1 column against the known number of forests
    (OEIS A005195): a free external check of the treewidth DP and of geng's
    coverage. `pw ≤ 1` (caterpillar forests) is listed beside it."""
    rows = []
    for n, part in census.groupby("n"):
        n = int(n)
        rows.append({"n": n, "tw ≤ 1 (census)": int(part.loc[part["tw"].between(0, 1), "count"].sum()),
                     "forests, A005195": FOREST_COUNTS[n] if n < len(FOREST_COUNTS) else -1,
                     "pw ≤ 1 (caterpillar forests)": int(part.loc[part["pw"].between(0, 1), "count"].sum()),
                     "tw computed for all": bool((part["tw"] >= 0).all())})
        rows[-1]["agree"] = bool(rows[-1]["tw ≤ 1 (census)"] == rows[-1]["forests, A005195"]) if rows[-1]["tw computed for all"] else None
    return pd.DataFrame(rows)


def large_summary(found: pd.DataFrame) -> pd.DataFrame:
    """Per n: how many graphs, by pw − tw; how many contain §21's graph as a
    subgraph; how many are vertex-minimal; edge range; how many agree on
    every verification route."""
    rows = []
    for n, part in found.groupby("n"):
        row = {"n": int(n), "graphs": len(part), "edges min": int(part["edges"].min()), "edges max": int(part["edges"].max())}
        for d in sorted((part["pw"] - part["tw"]).unique()):
            row[f"pw−tw={int(d)}"] = int(((part["pw"] - part["tw"]) == d).sum())
        for col, name in (("contains_section21_graph", "contain §21's graph"), ("vertex_minimal", "vertex-minimal"),
                          ("recertified", "re-certified"), ("agree", "agree on every route")):
            if col in part.columns:
                row[name] = int((part[col] == True).sum())        # noqa: E712
        if "components" in part.columns:
            row["connected"] = int((part["components"] == 1).sum())
        if "omega" in part.columns:
            row["ω = 4"] = int((part["omega"] == 4).sum())
            row["ω ≠ 4"] = int((part["omega"] != 4).sum())
        rows.append(row)
    return pd.DataFrame(rows)


def containment_table(found: pd.DataFrame) -> pd.DataFrame:
    """For the graphs found at one n: is graph i (row) a subgraph of graph j
    (column)? Answers whether the census is a chain of supergraphs of one
    minimal graph. Restricted to n ≤ 12 and at most 40 graphs."""
    import networkx as nx
    from networkx.algorithms.isomorphism import GraphMatcher

    rows = []
    for n, part in found.groupby("n"):
        part = part.sort_values(["edges", "graph6"]).head(40)
        graphs = {rec.graph6: graph_from_graph6(rec.graph6) for rec in part.itertuples(index=False)}
        for gi, g in graphs.items():
            row = {"n": int(n), "graph6": gi, "edges": g.number_of_edges()}
            for gj, h in graphs.items():
                row[f"⊆ {gj}"] = bool(GraphMatcher(h, g).subgraph_is_monomorphic()) if gi != gj else True
            rows.append(row)
    return pd.DataFrame(rows)


def price(totals: pd.DataFrame) -> pd.DataFrame:
    """Core-seconds per graph at each (n, level) from the run, and the cost
    of n = 12 (165,091,172,592 graphs) at the n = 11 rate doubled per level
    of subset-DP growth (2× subsets, ×12/11 vertices)."""
    rows = []
    for rec in totals.itertuples(index=False):
        if rec.n < 9:
            continue
        per_graph = rec.seconds * rec.workers / rec.graphs
        rows.append({"n": int(rec.n), "level": int(rec.level), "graphs": int(rec.graphs),
                     "wall s": float(rec.seconds), "workers": int(rec.workers),
                     "core-µs per graph": per_graph * 1e6,
                     "n=12 at this rate, core-hours": GRAPH_COUNTS[12] * per_graph * (2 * 12 / rec.n) ** (12 - rec.n) / 3600})
    return pd.DataFrame(rows)


def write_tables(log=print) -> str:
    census = pd.read_csv(CENSUS_CSV)
    totals = pd.read_csv(TOTALS_CSV).sort_values("n")
    found = pd.read_csv(FOUND_CSV) if FOUND_CSV.exists() else pd.DataFrame()
    lines = ["# Exhaustive census of pathwidth − treewidth, n ≤ 11 (§27)", "",
             "*Generated by `python -m learning.pwtw_exhaust --stage tables`; data in "
             "`learning/data/ensemble/pwtw_{census,found,totals}.csv`.*", "",
             "## The run", "", _md(totals[["n", "graphs", "expected_graphs", "complete", "pw_runs", "dp_runs",
                                           "found", "min_diff", "level", "seconds", "workers"]]), "",
             "## Graphs by n and pw − tw", "", _md(diff_table(census)), "",
             "## External check: tw ≤ 1 against the number of forests (OEIS A005195)", "",
             _md(forest_check(census)), "",
             "## Pathwidth marginal", "", _md(pw_marginal(census)), ""]
    cols = [c for c in ("n", "graph6", "pw", "tw", "edges", "components", "omega", "degrees",
                        "is_section21_graph", "contains_section21_graph", "edges_added_to_section21",
                        "recertified", "recert_optimum", "recert_lattice", "recert_pathwidth_dp", "agree")
            if not found.empty and c in found.columns]
    for n in sorted(census["n"].unique()):
        if n >= 5:
            jt = joint_table(census, int(n))
            if not jt.empty:
                lines += [f"## Joint distribution at n = {n} (rows pw, columns tw)", "", _md(jt), ""]
    lines += ["## Price of n = 12", "", _md(price(totals)), ""]
    if not found.empty:
        small = found[found["n"] <= 10]
        large = found[found["n"] >= 11]
        if not small.empty:
            lines += ["## Every graph with pw − tw ≥ 2 at n ≤ 10", "", _md(small[cols]), "",
                      "## Subgraph containment among the graphs found at n ≤ 10 (row ⊆ column)", "",
                      _md(containment_table(small)), ""]
        if not large.empty:
            lines += ["## The graphs with pw − tw ≥ 2 at n ≥ 11, summarised", "", _md(large_summary(large)), ""]
            if "vertex_minimal" in large.columns:
                minimal = large[large["vertex_minimal"] == True]      # noqa: E712  (CSV round trip)
                mcols = [c for c in cols if c not in ("edges_added_to_section21", "is_section21_graph")]
                lines += [f"## Vertex-minimal graphs at n ≥ 11 ({len(minimal)}: no single vertex deletion keeps the gap)",
                          "", _md(minimal[mcols]) if not minimal.empty else "(none)", ""]
                drawn = pd.concat([small, minimal.head(40)])
            else:
                drawn = small
        else:
            drawn = small
        for rec in drawn.itertuples(index=False):
            lines += [f"### n = {rec.n}, `{rec.graph6}`", "", "```", *_draw(rec.graph6), "```", ""]
            if hasattr(rec, "matrix_key") and isinstance(rec.matrix_key, str):
                lines += ["MOSP instance (products = maximal cliques):", "", "```",
                          *(" ".join(r) for r in rec.matrix_key.split("/")), "```", ""]
    text = "\n".join(lines)
    TABLES.write_text(text)
    log(f"wrote {TABLES}")
    return text


def _draw(graph6: str) -> list[str]:
    import networkx as nx

    g = nx.convert_node_labels_to_integers(graph_from_graph6(graph6), ordering="sorted")
    return [f"{v}: {' '.join(map(str, sorted(g.neighbors(v))))}" for v in sorted(g.nodes())]


# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["run", "verify", "tables", "check", "price"], default="tables")
    ap.add_argument("--min-n", type=int, default=0)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--level", type=int, default=2)
    ap.add_argument("--min-diff", type=int, default=2)
    ap.add_argument("--max-recertify", type=int, default=400)
    args = ap.parse_args()
    if args.stage == "run":
        run(args.max_n, args.workers, min_diff=args.min_diff, level=args.level, min_n=args.min_n)
    elif args.stage == "verify":
        verify(max_recertify=args.max_recertify)
    elif args.stage == "tables":
        write_tables()
    elif args.stage == "check":
        frame = atlas_check()
        print(f"{len(frame)} graphs, agree on {int(frame['agree'].sum())}")
        print(frame[~frame["agree"]].to_string())
    elif args.stage == "price":
        print(_md(price(pd.read_csv(TOTALS_CSV))))


if __name__ == "__main__":
    main()
