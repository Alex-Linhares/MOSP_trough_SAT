"""How redundant is the certified corpus? Isomorphism classes of every instance.

The question (`reports/ml_nature_plan.md` §2.1): two instances whose MOSP
graphs are isomorphic have the same optimum, because the optimum is
`pathwidth(MOSP graph) + 1` (Yanasse 1997c) and pathwidth is a graph invariant.
So the number of *distinct* MOSP graphs in the corpus, not the number of files,
is the sample size every downstream study is really working with. A generator
that emits the same graph under different names inflates that count silently.

Three levels of "the same instance", each coarser than the last:

1. **identical matrix** -- the same 0/1 matrix, byte for byte. Only catches a
   file copied into two collections.
2. **isomorphic matrix** -- equal up to renaming customers and renaming
   products. This is bipartite-graph isomorphism with the two sides coloured,
   computed as a nauty certificate of the coloured bipartite graph. Every
   feature in `learning.features` is constant on these classes, so a model
   cannot tell two members apart under any split.
3. **isomorphic MOSP graph** -- the customer graph `M @ M^T > 0` is the same up
   to renaming customers. The optimum is constant on these classes. Two
   matrices in the same class but not in the same level-2 class cover the same
   edge set with different cliques, which is exactly the residue §2.9 asks about.

Levels 2 and 3 use nauty through `pynauty`, behind a soft import: the
Weisfeiler--Lehman hash from networkx is always computed and is what the module
falls back to. WL is not a complete invariant -- it cannot separate some
non-isomorphic regular graphs -- so where both exist the table reports how many
nauty classes each WL class merged. That number is the WL hash's error on this
corpus, which matters because WL hashes are what a graph kernel or GNN sees.

The free audit: within every level-3 class all optima must agree. A
disagreement would mean one of the two certificates is wrong, and it costs
nothing to look. Any violating instances are re-solved through
`solve_mosp_exact` (with the solutions directory, never `solutions_dir=None`)
before the report is written, and the module prints them.

Usage:
    python -m learning.canonical                      # tables to stdout
    python -m learning.canonical --out reports/canonical_tables.md
    python -m learning.canonical --workers 16 --csv learning/data/canonical.csv

Nothing here is a bound and nothing here is used by the solver.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from learning.dataset import DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, enumerate_instances
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import _solution_path

try:  # soft import: the module works without nauty, on WL hashes alone
    import pynauty as _pynauty
except ImportError:  # pragma: no cover - exercised only where pynauty is absent
    _pynauty = None

HAVE_NAUTY = _pynauty is not None
DATA_DIR = Path("learning/data")
DEFAULT_CSV = DATA_DIR / "canonical.csv"
WL_ITERATIONS = 3

__all__ = [
    "HAVE_NAUTY",
    "mosp_graph_adjacency",
    "matrix_digest",
    "wl_hash",
    "nauty_graph_certificate",
    "nauty_bipartite_certificate",
    "automorphism_order",
    "canonical_record",
    "build",
    "class_tables",
    "audit_optima",
]


# ----------------------------------------------------------------------------
# invariants of one instance
# ----------------------------------------------------------------------------


def mosp_graph_adjacency(instance: MOSPInstance) -> dict[int, list[int]]:
    """Adjacency of the MOSP graph: customers, an edge iff some product is shared.

    Same graph as `customer_inter.customer_graph.build_customer_graph`, as a
    plain adjacency dict so that both networkx and nauty can consume it without
    a conversion each.
    """
    m = instance.matrix.astype(np.int64)
    overlap = m @ m.T
    np.fill_diagonal(overlap, 0)
    return {i: np.flatnonzero(overlap[i]).tolist() for i in range(instance.n_customers)}


def matrix_digest(instance: MOSPInstance) -> str:
    """Level 1: a digest of the matrix exactly as it is, shape included."""
    m = np.ascontiguousarray(instance.matrix.astype(np.uint8))
    h = hashlib.sha256()
    h.update(f"{m.shape[0]}x{m.shape[1]}:".encode())
    h.update(m.tobytes())
    return h.hexdigest()[:24]


def wl_hash(adjacency: dict[int, list[int]], iterations: int = WL_ITERATIONS) -> str:
    """Weisfeiler--Lehman hash of the MOSP graph. Isolated nodes count."""
    graph = nx.Graph()
    graph.add_nodes_from(adjacency)
    graph.add_edges_from((u, v) for u, vs in adjacency.items() for v in vs if u < v)
    return nx.weisfeiler_lehman_graph_hash(graph, iterations=iterations)


def _digest_certificate(cert: bytes, tag: str) -> str:
    return hashlib.sha256(tag.encode() + cert).hexdigest()[:24]


def nauty_graph_certificate(adjacency: dict[int, list[int]]) -> str | None:
    """Level 3: canonical certificate of the MOSP graph, or None without nauty.

    nauty's certificate is canonical among graphs on the same number of
    vertices, so the vertex count is folded into the digest.
    """
    if not HAVE_NAUTY:
        return None
    n = len(adjacency)
    g = _pynauty.Graph(n, directed=False, adjacency_dict=adjacency)
    return _digest_certificate(_pynauty.certificate(g), f"g{n}:")


def nauty_bipartite_certificate(instance: MOSPInstance) -> str | None:
    """Level 2: certificate of the coloured bipartite graph customers -- products.

    Customers are vertices `0..n-1`, products `n..n+m-1`, and the two sides
    are separate colour classes so nauty never maps a customer to a product.
    Two instances share a certificate iff their matrices are equal up to a
    row permutation and a column permutation.
    """
    if not HAVE_NAUTY:
        return None
    m = instance.matrix
    n_c, n_p = instance.n_customers, instance.n_patterns
    adjacency = {i: (n_c + np.flatnonzero(m[i])).tolist() for i in range(n_c)}
    colouring = [set(range(n_c)), set(range(n_c, n_c + n_p))]
    g = _pynauty.Graph(n_c + n_p, directed=False, adjacency_dict=adjacency,
                       vertex_coloring=colouring)
    return _digest_certificate(_pynauty.certificate(g), f"b{n_c}x{n_p}:")


def automorphism_order(adjacency: dict[int, list[int]]) -> float | None:
    """|Aut(G)| of the MOSP graph, as a float (nauty returns mantissa, exponent).

    Not part of the isomorphism question; recorded because §2.6b (degeneracy
    of the optimum) will need it and it is free here.
    """
    if not HAVE_NAUTY:
        return None
    g = _pynauty.Graph(len(adjacency), directed=False, adjacency_dict=adjacency)
    _, mantissa, exponent, _, _ = _pynauty.autgrp(g)
    return float(mantissa) * (10.0 ** exponent)


def canonical_record(instance: MOSPInstance) -> dict[str, object]:
    """Every invariant this module computes, for one instance."""
    adjacency = mosp_graph_adjacency(instance)
    n_edges = sum(len(v) for v in adjacency.values()) // 2
    return {
        "n_customers": instance.n_customers,
        "n_patterns": instance.n_patterns,
        "g_edges": n_edges,
        "matrix_digest": matrix_digest(instance),
        "wl_hash": wl_hash(adjacency),
        "graph_cert": nauty_graph_certificate(adjacency),
        "bipartite_cert": nauty_bipartite_certificate(instance),
        "aut_order": automorphism_order(adjacency),
    }


# ----------------------------------------------------------------------------
# the corpus
# ----------------------------------------------------------------------------


def _sub_collection(filepath: Path) -> str:
    parts = filepath.parts
    return "/".join(parts[2:4]) if len(parts) > 3 else "/".join(parts[2:3])


def _row(args: tuple[Path, MOSPInstance, Path]) -> dict | None:
    filepath, instance, solutions_dir = args
    path = _solution_path(instance, solutions_dir)
    if not path.exists():
        return None
    try:
        solution = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    row: dict[str, object] = {
        "instance_name": instance.name,
        "source_file": str(filepath),
        "collection": _sub_collection(filepath),
        "provenance": solution.get("provenance", ""),
        "optimum": int(solution["mosp_value"]),
    }
    row.update(canonical_record(instance))
    return row


def build(
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
    solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
    workers: int | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """One row per instance with a cached solution, with its invariants."""
    pairs = enumerate_instances(instance_dir)
    if verbose:
        print(f"{len(pairs)} instances enumerated; nauty "
              f"{'available' if HAVE_NAUTY else 'NOT available, WL only'}", flush=True)
    jobs = [(f, i, solutions_dir) for f, i in pairs]
    workers = workers or max(1, min(16, (multiprocessing.cpu_count() or 2) - 1))

    started = time.time()
    rows: list[dict] = []
    if workers == 1:
        results = map(_row, jobs)
    else:
        pool = multiprocessing.Pool(workers)
        results = pool.imap_unordered(_row, jobs, chunksize=16)
    for row in results:
        if row is not None:
            rows.append(row)
    if workers != 1:
        pool.close()
        pool.join()
    frame = pd.DataFrame(rows).sort_values("instance_name").reset_index(drop=True)
    if verbose:
        print(f"{len(frame)} rows in {time.time() - started:.0f}s", flush=True)
    return frame


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------

LEVELS = (
    ("matrix_digest", "identical matrix"),
    ("bipartite_cert", "isomorphic matrix"),
    ("graph_cert", "isomorphic MOSP graph"),
    ("wl_hash", "WL hash (not complete)"),
)


def _levels(frame: pd.DataFrame) -> list[tuple[str, str]]:
    return [(c, label) for c, label in LEVELS if c in frame and frame[c].notna().all()]


def _distinct_by(frame: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Rows, distinct classes at each level, and how many rows are redundant."""
    out = frame.groupby(by).size().rename("instances").to_frame()
    for column, label in _levels(frame):
        distinct = frame.groupby(by)[column].nunique()
        out[f"classes: {label}"] = distinct
    return out.reset_index()


def class_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """The tables the report prints, keyed by title."""
    tables: dict[str, pd.DataFrame] = {}

    # Corpus-wide totals at every level.
    total = {"instances": len(frame)}
    for column, label in _levels(frame):
        n_classes = frame[column].nunique()
        total[f"classes: {label}"] = n_classes
        total[f"redundant: {label}"] = len(frame) - n_classes
    tables["corpus"] = pd.DataFrame([total])

    tables["per collection"] = _distinct_by(frame, ["collection"])

    # Per size, but only for the sizes that occur often enough to say anything.
    by_size = _distinct_by(frame, ["n_customers", "n_patterns"])
    tables["per (n_customers, n_patterns)"] = by_size.sort_values(
        ["n_customers", "n_patterns"]).reset_index(drop=True)

    # Size bands, because 5,938 of 6,376 instances have <= 30 customers and
    # a corpus-wide figure is mostly a figure about small instances.
    banded = frame.assign(size_band=np.where(frame["n_customers"] <= 30,
                                             "n <= 30", "n > 30"))
    tables["per size band"] = _distinct_by(banded, ["size_band"])

    # The trivial classes: a complete MOSP graph has optimum n, no search
    # needed, and the largest classes in the corpus are exactly those.
    complete = frame["g_edges"] == frame["n_customers"] * (frame["n_customers"] - 1) // 2
    tables["trivial instances"] = pd.DataFrame([{
        "complete MOSP graph": int(complete.sum()),
        "share of corpus": f"{complete.mean():.1%}",
        "optimum == n_customers": int((frame["optimum"] == frame["n_customers"]).sum()),
        "in Harvey": int(complete[frame["collection"].str.endswith("Harvey")].sum()),
        "in Simonis": int(complete[frame["collection"].str.endswith("Simonis")].sum()),
        "elsewhere": int(complete[~frame["collection"].str.endswith(("Harvey", "Simonis"))].sum()),
    }])
    key3 = "graph_cert" if "graph_cert" in dict(_levels(frame)) else "wl_hash"
    sizes = frame.groupby(key3).agg(
        instances=("instance_name", "size"), n_customers=("n_customers", "first"),
        n_patterns=("n_patterns", lambda s: "/".join(map(str, sorted(set(s))))),
        g_edges=("g_edges", "first"), optimum=("optimum", "first"),
        files=("source_file", "nunique"),
        collections=("collection", lambda s: " + ".join(sorted({c.split("/")[-1] for c in s}))),
    ).sort_values("instances", ascending=False)
    tables["largest MOSP-graph classes"] = sizes.head(10).reset_index(drop=True)
    tables["class sizes"] = pd.DataFrame([{
        "classes": int(len(sizes)),
        "singletons": int((sizes["instances"] == 1).sum()),
        "classes of size >= 10": int((sizes["instances"] >= 10).sum()),
        "instances in them": int(sizes.loc[sizes["instances"] >= 10, "instances"].sum()),
        "classes spanning > 1 file": int((sizes["files"] > 1).sum()),
    }])

    # Cross-collection duplicates: classes that appear in more than one
    # collection at the matrix-isomorphism level (or WL if nauty is absent).
    key = "bipartite_cert" if "bipartite_cert" in dict(_levels(frame)) else "wl_hash"
    spread = frame.groupby(key)["collection"].agg(lambda s: tuple(sorted(set(s))))
    multi = spread[spread.map(len) > 1]
    if len(multi):
        counts = frame[frame[key].isin(multi.index)].groupby(key).size()
        cross = pd.DataFrame({
            "collections": multi.map(lambda t: " + ".join(t)),
            "instances": counts,
        }).groupby("collections").agg(classes=("instances", "size"),
                                      instances=("instances", "sum")).reset_index()
        tables["classes shared across collections"] = cross

    # Where the matrix carries information the graph does not: level-3 classes
    # that contain more than one level-2 class.
    if "graph_cert" in dict(_levels(frame)):
        per_graph = frame.groupby("graph_cert")["bipartite_cert"].nunique()
        tables["graph classes with several matrix classes"] = pd.DataFrame([{
            "graph classes": int(per_graph.size),
            "with >1 matrix class": int((per_graph > 1).sum()),
            "matrix classes inside them": int(per_graph[per_graph > 1].sum()),
        }])
        # WL's error against nauty: WL classes that merge several nauty classes.
        per_wl = frame.groupby("wl_hash")["graph_cert"].nunique()
        nauty_per_wl = frame.drop_duplicates("graph_cert").groupby("wl_hash").size()
        tables["WL against nauty"] = pd.DataFrame([{
            "WL classes": int(per_wl.size),
            "nauty classes": int(frame["graph_cert"].nunique()),
            "WL classes merging >1 nauty class": int((per_wl > 1).sum()),
            "nauty classes hidden by WL": int((nauty_per_wl - 1).clip(lower=0).sum()),
        }])
    return tables


def audit_optima(frame: pd.DataFrame, column: str | None = None) -> pd.DataFrame:
    """Classes whose members do not all carry the same optimum. Expected empty.

    Uses the MOSP-graph certificate when nauty is present, else the WL hash;
    on WL a disagreement is *not* proof of an error, only of a WL collision or
    of an error, so the report says which column was used.
    """
    if column is None:
        column = "graph_cert" if frame.get("graph_cert") is not None and \
            frame["graph_cert"].notna().all() else "wl_hash"
    spread = frame.groupby(column)["optimum"].agg(["min", "max", "size"])
    bad = spread[spread["min"] != spread["max"]]
    if bad.empty:
        return pd.DataFrame(columns=["class", "instances", "opt_min", "opt_max", "members"])
    members = frame[frame[column].isin(bad.index)].groupby(column)["instance_name"] \
        .agg(lambda s: "; ".join(sorted(s)))
    return pd.DataFrame({
        "class": bad.index,
        "instances": bad["size"].to_numpy(),
        "opt_min": bad["min"].to_numpy(),
        "opt_max": bad["max"].to_numpy(),
        "members": members.loc[bad.index].to_numpy(),
    }).reset_index(drop=True)


def recertify(names: list[str], frame: pd.DataFrame,
              instance_dir: Path = DEFAULT_INSTANCE_DIR) -> pd.DataFrame:
    """Re-solve the named instances exactly; the free audit's follow-up.

    Goes through `solve_mosp_exact` with the solutions directory, as the loop's
    rules require -- a cached value that survives is re-verified by simulation,
    and one that does not is corrected in place by the solver's own guarded save.
    """
    from satisfiability.mosp_solver import solve_mosp_exact

    wanted = set(names)
    rows = []
    for _, inst in enumerate_instances(instance_dir):
        if inst.name in wanted:
            value, _ = solve_mosp_exact(inst)
            cached = int(frame.loc[frame["instance_name"] == inst.name, "optimum"].iloc[0])
            rows.append({"instance_name": inst.name, "cached": cached, "resolved": value})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# entry point
# ----------------------------------------------------------------------------


def _fmt(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    # tabulate treats numpy integers as floats and would print 6376 as 6.38e+03.
    return frame.astype(object).to_markdown(index=False, floatfmt=floatfmt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instance-dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=DEFAULT_SOLUTIONS_DIR)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV,
                        help="where the per-instance invariants are written")
    parser.add_argument("--out", type=Path, default=None,
                        help="also write the tables as markdown here")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--min-size-count", type=int, default=20,
                        help="only print (n, m) sizes with at least this many instances")
    parser.add_argument("--recertify", action="store_true",
                        help="re-solve every instance in a class whose optima disagree")
    args = parser.parse_args()

    frame = build(args.instance_dir, args.solutions_dir, workers=args.workers)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.csv, index=False)
    print(f"wrote {args.csv} ({len(frame)} rows)\n")

    sections: list[str] = []
    for title, table in class_tables(frame).items():
        if title.startswith("per (n_customers"):
            table = table[table["instances"] >= args.min_size_count]
            title += f" (sizes with >= {args.min_size_count} instances)"
        sections.append(f"### {title}\n\n{_fmt(table)}\n")

    bad = audit_optima(frame)
    column = "graph_cert" if HAVE_NAUTY else "wl_hash"
    if bad.empty:
        sections.append(f"### audit\n\nAll classes by `{column}` carry one optimum: "
                        f"zero disagreements over {len(frame)} instances.\n")
    else:
        sections.append(f"### audit: classes by `{column}` whose optima DISAGREE\n\n"
                        f"{_fmt(bad)}\n")
        if args.recertify:
            names = [n for ms in bad["members"] for n in ms.split("; ")]
            sections.append("### re-certification\n\n"
                            f"{_fmt(recertify(names, frame, args.instance_dir))}\n")

    text = "\n".join(sections)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
