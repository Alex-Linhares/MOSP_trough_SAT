"""The bound harness and three branching-aware candidates (plan 3 §1 Q2, loop0004 item 11).

**Question.** §6 found that the solver's proved lower bound fails on *trees of
cliques with branching*; §24 that three of its four components are treewidth
bounds, that `tw + 1` is the honest reference, and that the one branching
lemma it tried (the cut-vertex rule seeded by treewidth, one level) sees the
wrong kind of branching — the gap instances branch at *separators*, not at
cut vertices. Plan 3 asks for the **harness, not the discovery**: a module
that takes any candidate lower bound as a Python function and

  (a) checks it on every certified instance (corpus 6,376 at 9–134 customers,
      campaign 37,800 at 10–40, upward 6,773 at 50–100) — a single value
      above the optimum is a counterexample, drawn and re-certified;
  (b) attacks it with `learning.extremal.local_search` at n = 8..15 with the
      exact solver as oracle, 10⁴ evaluations per candidate;
  (c) reports its tightness on the 338 corpus gap instances (`optimum −
      lb_best ≥ 2`) against the reference `max(lb_best, tw + 1)`;

and then three stated candidates run through it.

**Candidates** (all in optimum units, `pathwidth + 1`; every one is proved
valid, and the harness is what checks that the proofs were implemented):

- `cut-branch` — the plan's first: the pathwidth branch rule of Fellows &
  Langston (1987, Lemma 4.3; Kinnersley 1992, Corollary 4.2) applied
  *recursively* over cut vertices, seeded by the clique number. For a
  connected graph `H`: `b(H) = max(ω(H) − 1, max_v third-largest{b(B) : B a
  branch at v} + 1)` over cut vertices `v` with ≥ 3 branches (components of
  `H − v` containing a neighbour of `v`), memoised over vertex sets; for a
  disconnected `H` the maximum over components. Proof: three branches of
  pathwidth ≥ k at one vertex force pathwidth ≥ k + 1 (the layout argument
  in §38(a)), and `b(B) ≤ pw(B)` by induction.
- `sep-branch` — the session's first: the same rule with the cut vertex
  replaced by a **separator** `S`. *Lemma A*: if `H − S` has three components
  `B₁, B₂, B₃` with `pw(Bᵢ) ≥ k` and for every pair `Bᵢ, Bⱼ` some connected
  component of `H[S]` has a neighbour in both, then `pw(H) ≥ k + 1`. (Contract
  each component of `H[S]` to a vertex — a minor, so pathwidth does not
  rise — and run the cut-vertex argument with the contracted vertex adjacent
  to both branches of the pair that ends up outermost.) `S` ranges over the
  cut vertices, the pairwise intersections of the maximal cliques (the glue
  sets of a tree of cliques), the adhesions of a clique tree of the MCS-M
  chordal completion, and — on subgraphs of ≤ 40 vertices — every edge; the
  seed is `max(ω − 1, tw)` with treewidth exact by the subset DP on
  subgraphs of ≤ `TW_DP_SUB` vertices (≤ `TW_DP_TOP` at the top level),
  `tw ≤ pw` being a theorem. Dominates `cut-branch` pointwise.
- `contract-branch` — the session's second: `sep-branch` evaluated on every
  minor of the contraction-degeneracy sequence (contract the minimum-degree
  vertex into the neighbour it shares fewest neighbours with, the rule of
  `satisfiability.mosp_solver._contraction_degeneracy`), maximum over the
  sequence. Valid because pathwidth is minor-monotone. Contraction folds the
  fringe of single-product customers into the hubs, which is where §6's
  family hides its separators.

Each candidate carries a budget (deadline and a cap on memoised subproblems);
when it runs out the recursion returns its seed, which is still valid, and
the row is flagged `censored`.

**Reference and kill.** `lb_best` is the solver's bound as recorded, `tw` the
exact or interval treewidth of `learning.conjecture`'s invariants table
(`tw_lo`, always a valid lower bound). A candidate *beats the reference* on
an instance when it is strictly above `max(lb_best, tw_lo + 1)`. Kill (plan 3
§1 Q2): none beats the reference on more than 5% of the gap instances while
surviving (a) and (b).

**Nothing here is a bound the solver uses.** No candidate reaches
`satisfiability.mosp_solver._lower_bound` or any path that decides `k`.

Usage:
    python -m learning.bound_harness --stage validity --workers 16     # every certified instance, all candidates
    python -m learning.bound_harness --stage attack --workers 16       # 10⁴ oracle evaluations per candidate at n = 8..15
    python -m learning.bound_harness --stage tables                    # reports/bound_harness_tables.md
    python -m learning.bound_harness --stage one --key <matrix key>    # one instance, every candidate, verbose
    python -m pytest tests/test_bound_harness.py -q

A candidate of your own: `--extra mymodule:my_function`, a callable
`f(graph: networkx.Graph, matrix: numpy.ndarray, budget: Budget)` returning
a lower bound on the optimum (pathwidth + 1) as an `int`, or `(int, dict)`
with diagnostics the tables may show (`seed` is the one they use); see
`CANDIDATES`.
"""

from __future__ import annotations

import argparse
import importlib
import itertools
import math
import sys
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from learning.treewidth import masks_from_graph, masks_from_matrix, treewidth_exact

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "learning" / "data"
ENSEMBLE = DATA / "ensemble"
SCRATCH_SOLUTIONS = DATA / "bound_harness" / "solutions"
VALUES_CSV = ENSEMBLE / "bound_harness_values.csv.gz"
ATTACK_CSV = ENSEMBLE / "bound_harness_attack.csv"
ATTACK_LARGE_CSV = ENSEMBLE / "bound_harness_attack_large.csv"
COUNTER_CSV = ENSEMBLE / "bound_harness_counterexamples.csv"
TABLES = ROOT / "reports" / "bound_harness_tables.md"

TW_DP_TOP = 22          # exact treewidth by the subset DP at the top level of a candidate
TW_DP_SUB = 16          # and inside the recursion (each subproblem pays it once)
PAIRS_MAX_N = 40        # every adjacent pair is a candidate separator on subgraphs this small
CLIQUE_PAIRS_MAX = 80   # pairwise intersections of the maximal cliques when there are at most this many
KILL_SHARE = 0.05
ATTACK_SIZES = tuple(range(8, 16))
ATTACK_KINDS = ("tree", "bern", "gap")
BANDS = ((9, 20), (21, 30), (31, 40), (41, 60), (61, 75), (76, 100), (101, 134))


# ----------------------------------------------------------------------------
# budget
# ----------------------------------------------------------------------------


@dataclass
class Budget:
    """A deadline and a cap on memoised subproblems; `exhausted` once either
    is hit, after which every recursion returns its seed (still valid)."""

    seconds: float = 10.0
    max_subproblems: int = 2000
    started: float = field(default_factory=time.monotonic)
    subproblems: int = 0
    exhausted: bool = False

    def charge(self) -> bool:
        """Account one subproblem; True while the budget holds."""
        self.subproblems += 1
        if self.subproblems > self.max_subproblems or time.monotonic() - self.started > self.seconds:
            self.exhausted = True
        return not self.exhausted

    def ok(self) -> bool:
        if not self.exhausted and time.monotonic() - self.started > self.seconds:
            self.exhausted = True
        return not self.exhausted


# ----------------------------------------------------------------------------
# graph helpers
# ----------------------------------------------------------------------------


def graph_from_matrix(matrix) -> "nx.Graph":
    """The MOSP graph: customers as vertices, a clique per product."""
    import networkx as nx

    matrix = np.asarray(matrix, dtype=int)
    g = nx.Graph()
    g.add_nodes_from(range(matrix.shape[0]))
    for j in range(matrix.shape[1]):
        rows = np.flatnonzero(matrix[:, j])
        g.add_edges_from(itertools.combinations(rows.tolist(), 2))
    return g


def clique_number(graph) -> int:
    import networkx as nx

    if graph.number_of_nodes() == 0:
        return 0
    if graph.number_of_edges() == 0:
        return 1
    return max(len(c) for c in nx.find_cliques(graph))


def seed_clique(graph, budget: Budget | None = None) -> int:
    """`ω − 1 ≤ tw ≤ pw`: the plan's seed for `cut-branch`."""
    return max(0, clique_number(graph) - 1)


def seed_clique_tw(graph, budget: Budget | None = None, dp_max: int = TW_DP_SUB) -> int:
    """`max(ω − 1, tw)`, treewidth exact by the subset DP when the graph is
    small enough; `tw ≤ pw` is a theorem, so this is a pathwidth lower bound."""
    best = seed_clique(graph)
    n = graph.number_of_nodes()
    if 2 <= n <= dp_max and graph.number_of_edges() > 0:
        import networkx as nx

        sub = nx.convert_node_labels_to_integers(graph)
        tw, _ = treewidth_exact(masks_from_graph(sub))
        best = max(best, int(tw))
    return best


def family_cut_vertices(graph) -> list[frozenset]:
    import networkx as nx

    return [frozenset([v]) for v in sorted(nx.articulation_points(graph))]


def family_separators(graph, pairs_max_n: int = PAIRS_MAX_N,
                      clique_pairs_max: int = CLIQUE_PAIRS_MAX, with_chordal: bool = True) -> list[frozenset]:
    """Cut vertices, pairwise intersections of maximal cliques, adhesions of
    a clique tree of the MCS-M chordal completion, and every vertex pair on
    small graphs. Deduplicated, smallest first, never the whole vertex set."""
    import networkx as nx

    n = graph.number_of_nodes()
    nodes = set(graph.nodes())
    found: set[frozenset] = set(family_cut_vertices(graph))
    if graph.number_of_edges() == 0:
        return sorted(found, key=lambda s: (len(s), sorted(s)))
    # never materialise every maximal clique: a dense 125-vertex graph can have millions
    cliques = [frozenset(c) for c in itertools.islice(nx.find_cliques(graph), clique_pairs_max + 1)]
    if len(cliques) <= clique_pairs_max:
        for a, b in itertools.combinations(cliques, 2):
            s = a & b
            if s and s != nodes:
                found.add(s)
    try:
        if not with_chordal:
            raise StopIteration
        chordal, _ = nx.complete_to_chordal_graph(graph)
        ccl = [frozenset(c) for c in nx.chordal_graph_cliques(chordal)]
        if 1 < len(ccl) <= 4 * clique_pairs_max:
            cg = nx.Graph()
            cg.add_nodes_from(range(len(ccl)))
            for i, j in itertools.combinations(range(len(ccl)), 2):
                w = len(ccl[i] & ccl[j])
                if w:
                    cg.add_edge(i, j, weight=w)
            tree = nx.maximum_spanning_tree(cg, weight="weight")
            for i, j in tree.edges():
                s = ccl[i] & ccl[j]
                if s and s != nodes:
                    found.add(s)
    except Exception:  # noqa: BLE001 - the completion is an optional source of separators
        pass
    if n <= pairs_max_n:
        for u, v in graph.edges():                 # adjacent pairs: the glue of two cliques sharing an edge
            found.add(frozenset((u, v)))
    return sorted(found, key=lambda s: (len(s), sorted(s)))


def linked_third(graph, S: frozenset, comps: list[set], values: list[int]) -> int | None:
    """Lemma A's triple: the largest `k` such that three components with
    `values ≥ k` are pairwise linked through a connected component of
    `H[S]`. `None` when no linked triple exists."""
    import networkx as nx

    sub_s = graph.subgraph(S)
    s_comp = {}
    for i, part in enumerate(nx.connected_components(sub_s)):
        for v in part:
            s_comp[v] = i
    touch = []
    for comp in comps:
        ids = set()
        for v in comp:
            for u in graph.neighbors(v):
                if u in s_comp:
                    ids.add(s_comp[u])
        touch.append(ids)
    order = sorted(range(len(comps)), key=lambda i: -values[i])
    if len(order) > 10:
        order = order[:10]
    best = None
    for i, j, k in itertools.combinations(order, 3):
        if (touch[i] & touch[j]) and (touch[i] & touch[k]) and (touch[j] & touch[k]):
            third = min(values[i], values[j], values[k])
            if best is None or third > best:
                best = third
    return best


def branch_bound(graph, family: Callable, seed: Callable, budget: Budget,
                 seed_top: Callable | None = None, restrict: bool = True,
                 info: dict | None = None) -> int:
    """The recursive branch rule in pathwidth units: for connected `H`,
    `max(seed(H), max_S third-largest-linked{b(B)} + 1)`; for disconnected
    `H` the maximum over components. Memoised over vertex sets.

    With `restrict` (the default) the separator family is computed once on
    the whole graph and a subproblem `H` uses its cut vertices, the top-level
    separators intersected with `H`, and — when `H` is small — its edges;
    Lemma A holds for any `S`, so this only chooses which `S` to try."""
    import networkx as nx

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10_000))
    memo: dict[frozenset, int] = {}
    top = frozenset(graph.nodes())
    top_family = family(graph) if restrict else None
    # the "seed" diagnostic is the seed of the whole graph: the maximum over
    # its components' seeds when it is disconnected
    top_parts = ({top} if nx.is_connected(graph) else {frozenset(c) for c in nx.connected_components(graph)}) \
        if graph.number_of_nodes() else set()

    def sub_family(sub, H):
        if not restrict or H == top:
            return top_family if restrict else family(sub)
        found = set(family_cut_vertices(sub))
        for S in top_family:
            r = S & H
            if r and len(r) < len(H):
                found.add(r)
        if len(H) <= PAIRS_MAX_N:
            found.update(frozenset(e) for e in sub.edges())
        return sorted(found, key=lambda x: (len(x), sorted(x)))

    def rec(H: frozenset) -> int:
        if H in memo:
            return memo[H]
        sub = graph.subgraph(H)
        if len(H) <= 1:
            memo[H] = 0
            return 0
        if not nx.is_connected(sub):
            value = max(rec(frozenset(c)) for c in nx.connected_components(sub))
            memo[H] = value
            return value
        value = (seed_top if (seed_top is not None and H in top_parts) else seed)(sub, budget)
        if info is not None and H in top_parts:
            info["seed_top"] = max(info.get("seed_top", 0), value)
        if len(H) >= 4 and budget.charge():
            for S in sub_family(sub, H):
                if not budget.ok():
                    break
                if len(S) > len(H) - 3:
                    continue
                rest = sub.subgraph(H - S)
                comps = [set(c) for c in nx.connected_components(rest)]
                if len(comps) < 3:
                    continue
                values = [rec(frozenset(c)) for c in comps]
                third = linked_third(sub, S, comps, values)
                if third is not None:
                    value = max(value, third + 1)
        memo[H] = value
        return value

    result = rec(top)
    if info is not None:
        info["value"] = result
        info["subproblems"] = len(memo)
    return result


def contraction_minors(graph):
    """The minors of the contraction-degeneracy sequence, the graph itself
    first: contract the minimum-degree vertex into the neighbour it shares
    fewest neighbours with (isolated vertices are dropped)."""
    import networkx as nx

    working = nx.Graph(graph)
    yield working
    while working.number_of_nodes() > 1:
        vertex = min(working.nodes, key=lambda x: (working.degree(x), x))
        if working.degree(vertex) == 0:
            working = nx.Graph(working)
            working.remove_node(vertex)
            yield working
            continue
        neighbours = set(working[vertex])
        target = min(neighbours, key=lambda x: (len(neighbours & set(working[x])), x))
        working = nx.contracted_nodes(working, target, vertex, self_loops=False)
        yield working


# ----------------------------------------------------------------------------
# the candidates (optimum units = pathwidth + 1)
# ----------------------------------------------------------------------------


def cand_cut_branch(graph, matrix, budget: Budget):
    info: dict = {}
    value = branch_bound(graph, family_cut_vertices, seed_clique, budget, info=info) + 1
    return value, {"seed": info.get("seed_top", 0) + 1}


def _seed_top(graph, budget):
    return seed_clique_tw(graph, budget, dp_max=TW_DP_TOP)


def cand_sep_branch(graph, matrix, budget: Budget):
    info: dict = {}
    value = branch_bound(graph, family_separators, seed_clique_tw, budget, seed_top=_seed_top, info=info) + 1
    return value, {"seed": info.get("seed_top", 0) + 1}


def seed_minor(graph, budget: Budget | None = None, dense_edges: int = 1500) -> int:
    """The seed on a minor: its minimum degree (contraction degeneracy's
    term, `tw ≥ δ(minor)`), the clique number unless the minor is dense (then
    `find_cliques` is the cost), and the exact treewidth when small."""
    best = min((d for _, d in graph.degree()), default=0)
    if graph.number_of_edges() <= dense_edges:
        best = max(best, seed_clique_tw(graph, budget))
    elif graph.number_of_nodes() <= TW_DP_SUB:
        best = max(best, seed_clique_tw(graph, budget))
    return best


def _family_minor(graph):
    return family_separators(graph, with_chordal=False)


def cand_contract_branch(graph, matrix, budget: Budget):
    """Returns the value and, for the tables, the best *seed* over the minors
    (what contraction alone gives: clique number, minimum degree and small
    exact treewidth of a minor) so the branch rule's own contribution is
    `value − seed`."""
    best = 0
    best_seed = 0
    minors = 0
    per_minor = max(50, budget.max_subproblems // 8)
    for i, minor in enumerate(contraction_minors(graph)):
        if minor.number_of_nodes() < 2:
            break
        if not budget.ok():
            break
        minors += 1
        inner = Budget(seconds=max(0.0, budget.seconds - (time.monotonic() - budget.started)),
                       max_subproblems=per_minor)
        info: dict = {}
        if i == 0:
            value = branch_bound(minor, family_separators, seed_clique_tw, inner, seed_top=_seed_top, info=info)
        else:
            value = branch_bound(minor, _family_minor, seed_minor, inner, info=info)
        budget.subproblems += inner.subproblems
        best = max(best, value)
        best_seed = max(best_seed, info.get("seed_top", 0))
        if inner.exhausted:
            budget.exhausted = True          # censored: some minor did not finish its recursion
            if not budget.ok():
                break                        # out of time; out of subproblems only moves on to the next minor
    return best + 1, {"seed": best_seed + 1, "minors": minors}


CANDIDATES: dict[str, Callable] = {
    "cut-branch": cand_cut_branch,
    "sep-branch": cand_sep_branch,
    "contract-branch": cand_contract_branch,
}
BUDGET_SECONDS = {"cut-branch": 5.0, "sep-branch": 8.0, "contract-branch": 12.0}
BUDGET_SUBPROBLEMS = {"cut-branch": 4000, "sep-branch": 3000, "contract-branch": 4000}


def resolve_extra(spec: str) -> tuple[str, Callable]:
    module, _, func = spec.partition(":")
    return func, getattr(importlib.import_module(module), func)


def evaluate_candidates(matrix, candidates: dict[str, Callable] | None = None,
                        seconds: dict | None = None) -> dict:
    """Every candidate on one matrix: value, seed (ω and the top-level
    treewidth seed), seconds, subproblems, censored."""
    candidates = CANDIDATES if candidates is None else candidates
    matrix = np.asarray(matrix, dtype=int)
    graph = graph_from_matrix(matrix)
    import networkx as nx

    out = {"n": int(matrix.shape[0]), "m": int(matrix.shape[1]),
           "edges": graph.number_of_edges(), "omega": clique_number(graph),
           "components": nx.number_connected_components(graph) if matrix.shape[0] else 0}
    for name, fn in candidates.items():
        budget = Budget(seconds=(seconds or BUDGET_SECONDS).get(name, 10.0),
                        max_subproblems=BUDGET_SUBPROBLEMS.get(name, 2000))
        t0 = time.monotonic()
        info: dict = {}
        try:
            result = fn(graph, matrix, budget)
            if isinstance(result, tuple):
                result, info = result
            value = int(result)
            err = ""
        except Exception as exc:  # noqa: BLE001 - one candidate's failure is a row, not a crash
            value, err = -1, repr(exc)
        col = name.replace("-", "_")
        out[f"{col}"] = value
        for k, v in info.items():
            out[f"{col}_{k}"] = v
        out[f"{col}_seconds"] = round(time.monotonic() - t0, 3)
        out[f"{col}_subproblems"] = budget.subproblems
        out[f"{col}_censored"] = bool(budget.exhausted)
        if err:
            out[f"{col}_error"] = err
    return out


# ----------------------------------------------------------------------------
# (a) validity on every certified instance
# ----------------------------------------------------------------------------


def certified_rows() -> pd.DataFrame:
    """Every certified instance with optimum, `lb_best`, gap and the
    invariants table's treewidth interval (`learning.conjecture`)."""
    from learning.conjecture import all_rows, load_table

    rows = all_rows()
    inv = load_table()[["instance_name", "source", "tw_lo", "tw_hi", "tw_exact", "blt1", "hubs3", "art"]]
    rows = rows.merge(inv, on=["instance_name", "source"], how="left")
    rows["tw1"] = rows["tw_lo"] + 1
    rows["reference"] = np.maximum(rows["lb_best"].astype(float), rows["tw1"].astype(float))
    rows["is_gap"] = (rows["source"] == "corpus") & (rows["gap"] >= 2)
    return rows


def corpus_matrices(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    from learning.dataset import enumerate_instances

    wanted = {r.instance_name: str(r.source_file) for r in frame.itertuples() if r.source == "corpus"}
    found: dict[str, np.ndarray] = {}
    for path, inst in enumerate_instances():
        src = wanted.get(inst.name)
        if src is not None and str(path).endswith(src):
            found[inst.name] = np.asarray(inst.matrix, dtype=int)
    return found


def _validity_job(args) -> dict:
    name, source, key, names = args
    from learning.extremal import matrix_from_key

    matrix = matrix_from_key(key)
    cands = {k: CANDIDATES[k] for k in names}
    out = evaluate_candidates(matrix, cands)
    out.update(instance_name=name, source=source, key=key)
    return out


def run_validity(workers: int = 16, names: tuple[str, ...] = tuple(CANDIDATES),
                 out_csv: Path = VALUES_CSV, limit: int | None = None,
                 sources: tuple[str, ...] = ("corpus", "campaign", "upward"),
                 wall: float | None = None) -> pd.DataFrame:
    """Every candidate on every certified instance, resumable by
    `(instance_name, source)`, largest instances first."""
    from learning.conjecture import _generated_matrix
    from learning.extremal import matrix_key

    rows = certified_rows()
    rows = rows[rows["source"].isin(sources)]
    done: set[tuple[str, str]] = set()
    if out_csv.exists():
        prev = pd.read_csv(out_csv)
        done = set(zip(prev["instance_name"], prev["source"]))
    todo = rows[[(a, b) not in done for a, b in zip(rows["instance_name"], rows["source"])]]
    if limit is not None:
        todo = todo.sort_values("n_customers", ascending=False).head(limit)
    print(f"[harness] {len(rows)} certified rows, {len(done)} done, {len(todo)} to run", flush=True)
    matrices = corpus_matrices(todo) if (todo["source"] == "corpus").any() else {}
    jobs = []
    for r in todo.sort_values("n_customers", ascending=False).itertuples():
        if r.source == "corpus":
            mat = matrices.get(r.instance_name)
            if mat is None:
                continue
        else:
            mat = _generated_matrix(r)
        jobs.append((r.instance_name, r.source, matrix_key(mat), names))
    started = time.monotonic()
    part: list[dict] = []
    written = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_validity_job, j) for j in jobs]
        try:
            for i, fut in enumerate(as_completed(futures), start=1):
                part.append(fut.result())
                if len(part) >= 500 or i == len(futures):
                    _append(out_csv, pd.DataFrame(part))
                    written += len(part)
                    part = []
                    print(f"[harness] validity {i}/{len(futures)} in {time.monotonic() - started:.0f}s",
                          flush=True)
                if wall is not None and time.monotonic() - started > wall:
                    print("[harness] wall reached; cancelling the rest", flush=True)
                    for f in futures:
                        f.cancel()
                    break
        finally:
            if part:
                _append(out_csv, pd.DataFrame(part))
    return load_values(out_csv)


def _append(csv: Path, part: pd.DataFrame) -> None:
    csv.parent.mkdir(parents=True, exist_ok=True)
    if csv.exists():
        prev = pd.read_csv(csv)
        part = pd.concat([prev, part], ignore_index=True)
    part.to_csv(csv, index=False)


def load_values(csv: Path = VALUES_CSV) -> pd.DataFrame:
    """The recorded candidate values joined with the certified rows."""
    vals = pd.read_csv(csv)
    rows = certified_rows()
    return vals.merge(rows.drop(columns=[c for c in ("n",) if c in rows.columns]),
                      on=["instance_name", "source"], how="left")


def candidate_columns(frame: pd.DataFrame) -> list[str]:
    return [c.replace("_", "-") for c in frame.columns
            if f"{c}_seconds" in frame.columns and c not in ("n", "m")]


def validity_table(frame: pd.DataFrame) -> pd.DataFrame:
    """(a) and (c) in one table, per candidate and for the proved references:
    the "above optimum (must be 0)" column, tightness and the share above
    `lb_best` and above the reference, on all rows and on the gap instances."""
    gap = frame[frame["is_gap"]]
    rows = []
    specs = [("tw + 1 (tw_lo)", frame["tw1"]), ("lb_best", frame["lb_best"]),
             ("reference max(lb_best, tw + 1)", frame["reference"]),
             ("branch lemma + 1 (§24, one level, tw-seeded)", frame["blt1"])]
    for name in candidate_columns(frame):
        specs.append((name, frame[name.replace("-", "_")]))
    for name, values in specs:
        v = values.astype(float)
        ok = v >= 0
        above = (v > frame["optimum"]) & ok
        g = gap.index
        rows.append({
            "bound": name,
            "rows": int(ok.sum()),
            "above optimum (must be 0)": int(above.sum()),
            "tight, all": (v[ok] == frame.loc[ok, "optimum"]).mean(),
            "> lb_best, all": (v[ok] > frame.loc[ok, "lb_best"]).mean(),
            "> reference, all": (v[ok] > frame.loc[ok, "reference"]).mean(),
            "tight, gap": (v[g] == gap["optimum"]).mean() if len(g) else np.nan,
            "> lb_best, gap": (v[g] > gap["lb_best"]).mean() if len(g) else np.nan,
            "> reference, gap": (v[g] > gap["reference"]).mean() if len(g) else np.nan,
            "beats reference, gap (count)": int((v[g] > gap["reference"]).sum()) if len(g) else 0,
            "mean shortfall, gap": float((gap["optimum"] - v[g]).mean()) if len(g) else np.nan,
        })
    return pd.DataFrame(rows)


def band_of(n: pd.Series) -> pd.Series:
    labels = []
    for x in n:
        lab = "?"
        for lo, hi in BANDS:
            if lo <= x <= hi:
                lab = f"{lo}–{hi}"
                break
        labels.append(lab)
    return pd.Series(labels, index=n.index)


def gap_band_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Per size band on the gap instances: how often each candidate beats
    `lb_best`, the reference, and is tight; mean shortfall."""
    gap = frame[frame["is_gap"]].copy()
    gap["band"] = band_of(gap["n_customers"])
    rows = []
    for band, part in gap.groupby("band", sort=False):
        row = {"band": band, "gap instances": len(part),
               "tw exact": int(part["tw_exact"].astype(str).str.lower().eq("true").sum())}
        for name in candidate_columns(frame):
            col = name.replace("-", "_")
            row[f"{name} > lb_best"] = int((part[col] > part["lb_best"]).sum())
            row[f"{name} > ref"] = int((part[col] > part["reference"]).sum())
            row[f"{name} tight"] = int((part[col] == part["optimum"]).sum())
            row[f"{name} shortfall"] = float((part["optimum"] - part[col]).mean())
        rows.append(row)
    out = pd.DataFrame(rows)
    order = [f"{lo}–{hi}" for lo, hi in BANDS]
    out["_o"] = out["band"].map({b: i for i, b in enumerate(order)})
    return out.sort_values("_o").drop(columns="_o").reset_index(drop=True)


def gain_table(frame: pd.DataFrame) -> pd.DataFrame:
    """What the branching adds over its own seed: `cut-branch − ω`,
    `sep-branch − max(ω, tw + 1)`, `contract-branch − sep-branch`, on all
    rows and on the gap instances; censoring and time per candidate."""
    rows = []
    gap = frame["is_gap"]
    pairs = [("cut-branch", "cut_branch_seed", "ω (its seed)"),
             ("sep-branch", "sep_branch_seed", "max(ω, tw_DP) + 1 (its seed)"),
             ("contract-branch", "contract_branch_seed", "best seed over the minors"),
             ("contract-branch", "sep_branch", "sep-branch"),
             ("contract-branch", "reference", "reference (seed only)")]
    for name, base_col, base_name in pairs:
        col = name.replace("-", "_")
        if col not in frame.columns or base_col not in frame.columns:
            continue
        v = frame[col] if base_name != "reference (seed only)" else frame["contract_branch_seed"]
        d = v - frame[base_col]
        rows.append({
            "candidate": name if base_name != "reference (seed only)" else "contract-branch seed",
            "over": base_name,
            "gain > 0, all": float((d > 0).mean()), "gain > 0, gap": float((d[gap] > 0).mean()),
            "max gain": int(d.max()), "mean gain, gap": float(d[gap].mean()),
            "censored": int(frame[f"{col}_censored"].astype(str).str.lower().eq("true").sum()),
            "median s": float(frame[f"{col}_seconds"].median()),
            "max s": float(frame[f"{col}_seconds"].max()),
            "total core-h": float(frame[f"{col}_seconds"].sum() / 3600),
        })
    return pd.DataFrame(rows)


def counterexamples(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in candidate_columns(frame):
        col = name.replace("-", "_")
        bad = frame[(frame[col] > frame["optimum"]) & (frame[col] >= 0)]
        for r in bad.sort_values(["n_customers", "edges"]).itertuples():
            rows.append({"candidate": name, "instance_name": r.instance_name, "source": r.source,
                         "n": r.n_customers, "optimum": r.optimum, "value": getattr(r, col),
                         "key": r.key})
    return pd.DataFrame(rows, columns=["candidate", "instance_name", "source", "n", "optimum", "value", "key"])


# ----------------------------------------------------------------------------
# (b) the adversary
# ----------------------------------------------------------------------------


def make_evaluate(names: tuple[str, ...], solutions_dir: Path = SCRATCH_SOLUTIONS):
    """An `evaluate_fn` for `learning.extremal.local_search`: the optimum
    from the exact solver and `viol_<name>` = candidate − optimum."""
    from learning.extremal import instance_from_matrix, matrix_key
    from satisfiability.mosp_solver import solve_mosp_exact

    def evaluate(matrix, sol_dir=solutions_dir) -> dict:
        matrix = np.asarray(matrix, dtype=int)
        inst = instance_from_matrix(matrix, prefix="bh")
        sol_dir.mkdir(parents=True, exist_ok=True)
        optimum, ordering = solve_mosp_exact(inst, solutions_dir=sol_dir)
        vals = evaluate_candidates(matrix, {k: CANDIDATES[k] for k in names},
                                   seconds={k: 5.0 for k in names})
        rec = {"key": matrix_key(matrix), "n": int(matrix.shape[0]), "m": int(matrix.shape[1]),
               "optimum": int(optimum), "edges": int(vals["edges"]),
               "witness": " ".join(str(v) for v in ordering)}
        for k in names:
            rec[f"viol_{k}"] = int(vals[k.replace("-", "_")]) - int(optimum)
        return rec

    return evaluate


def _attack_job(args) -> dict:
    name, n, kind, restart, steps, solutions_dir = args
    from learning.extremal import bernoulli, gap_seed_matrices, local_search, subset_of, tree_of_cliques

    rng = np.random.default_rng([abs(hash(name)) % (2**31), n, ATTACK_KINDS.index(kind), restart])
    if kind == "tree":
        seed = tree_of_cliques(n, rng)
    elif kind == "bern":
        seed = bernoulli(n, rng)
    else:
        pool = [m for m in gap_seed_matrices() if m.shape[0] >= n]     # the gap seeds are 20–30 customers
        seed = subset_of(pool[rng.integers(len(pool))], n, rng) if pool else tree_of_cliques(n, rng)
    evaluate = make_evaluate((name,), Path(solutions_dir))
    res = local_search(seed, f"viol_{name}", steps, rng, solutions_dir=Path(solutions_dir),
                       evaluate_fn=evaluate)
    best = res["best"]
    return {"candidate": name, "n": n, "kind": kind, "restart": restart,
            "evaluations": res["evaluations"], "skipped": res["skipped"],
            "best_viol": int(best[f"viol_{name}"]), "best_key": best["key"],
            "best_optimum": int(best["optimum"]), "best_edges": int(best["edges"]),
            "max_trace": int(max(res["trace"]))}


def run_attack(names: tuple[str, ...] = tuple(CANDIDATES), workers: int = 16, steps: int = 210,
               sizes=ATTACK_SIZES, restarts: int = 2, kinds=ATTACK_KINDS,
               solutions_dir: Path = SCRATCH_SOLUTIONS, out_csv: Path = ATTACK_CSV) -> pd.DataFrame:
    """`steps × |sizes| × |kinds| × restarts` oracle evaluations per candidate
    (10,080 at the defaults), the search climbing `candidate − optimum`."""
    jobs = [(name, n, kind, r, steps, str(solutions_dir))
            for name in names for n in sizes for kind in kinds for r in range(restarts)]
    jobs.sort(key=lambda j: -j[1])
    rows = []
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_attack_job, j) for j in jobs]
        for i, fut in enumerate(as_completed(futures), start=1):
            rows.append(fut.result())
            if i % 16 == 0 or i == len(futures):
                print(f"[harness] attack {i}/{len(futures)} in {time.monotonic() - started:.0f}s", flush=True)
    out = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)
    return out


def attack_summary(attack: pd.DataFrame) -> pd.DataFrame:
    g = attack.groupby("candidate")
    out = g.agg(jobs=("n", "size"), evaluations=("evaluations", "sum"), skipped=("skipped", "sum"),
                max_viol=("best_viol", "max"), reached_optimum=("best_viol", lambda s: int((s >= 0).sum())),
                n_min=("n", "min"), n_max=("n", "max")).reset_index()
    keys = []
    for c, part in g:
        bad = part[part["best_viol"] >= 1]
        keys.append((c, int(bad.sort_values(["n", "best_edges"]).iloc[0]["n"]) if len(bad) else -1,
                     bad.sort_values(["n", "best_edges"]).iloc[0]["best_key"] if len(bad) else ""))
    out = out.merge(pd.DataFrame(keys, columns=["candidate", "counter_n", "counter_key"]), on="candidate")
    out["verdict"] = np.where(out["max_viol"] >= 1, "broken", "survived")
    return out


def recertify_counterexample(key: str, name: str, solutions_dir: Path = SCRATCH_SOLUTIONS) -> dict:
    from learning.extremal import matrix_from_key, recertify

    out = recertify(key, solutions_dir)
    vals = evaluate_candidates(matrix_from_key(key), {name: CANDIDATES[name]})
    out["candidate_value"] = int(vals[name.replace("-", "_")])
    out["violation"] = out["candidate_value"] - out["optimum"]
    return out


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _md(table: pd.DataFrame, floatfmt: str = ".3f") -> str:
    try:
        return table.to_markdown(index=False, floatfmt=floatfmt)
    except Exception:  # noqa: BLE001 - tabulate missing
        return table.to_string(index=False)


def kill_verdict(validity: pd.DataFrame, attack: pd.DataFrame | None) -> pd.DataFrame:
    rows = []
    summ = attack_summary(attack).set_index("candidate") if attack is not None and len(attack) else None
    for _, r in validity.iterrows():
        name = r["bound"]
        if name not in CANDIDATES:
            continue
        survived_a = int(r["above optimum (must be 0)"]) == 0
        attacked = summ is not None and name in summ.index
        survived_b = bool(attacked and summ.loc[name, "verdict"] == "survived")
        share = float(r["> reference, gap"])
        share = 0.0 if math.isnan(share) else share
        rows.append({"candidate": name, "valid on every certified instance": survived_a,
                     "survived the adversary": survived_b if attacked else "not attacked",
                     "beats reference on gap": f"{share:.1%}",
                     "beats > 5% while surviving": bool(survived_a and survived_b and share > KILL_SHARE)})
    return pd.DataFrame(rows)


def write_tables(values_csv: Path = VALUES_CSV, attack_csv: Path = ATTACK_CSV,
                 attack_large_csv: Path = ATTACK_LARGE_CSV, out: Path = TABLES) -> dict:
    frame = load_values(values_csv)
    attack = pd.read_csv(attack_csv) if attack_csv.exists() else None
    if attack_large_csv.exists():
        large = pd.read_csv(attack_large_csv)
        attack = pd.concat([attack, large], ignore_index=True) if attack is not None else large
    validity = validity_table(frame)
    bands = gap_band_table(frame)
    gains = gain_table(frame)
    counters = counterexamples(frame)
    verdict = kill_verdict(validity, attack)
    sizes = frame.groupby("source").agg(rows=("n_customers", "size"), n_min=("n_customers", "min"),
                                        n_max=("n_customers", "max")).reset_index()
    lines = ["# Bound harness tables (§38)", "",
             "*Regenerate: `python -m learning.bound_harness --stage tables`. Every candidate in "
             "optimum units (pathwidth + 1). Reference = `max(lb_best, tw_lo + 1)`. Gap instances = the "
             f"{int(frame['is_gap'].sum())} corpus instances with `optimum − lb_best ≥ 2`.*", "",
             "## Coverage", "", _md(sizes), "",
             "## (a) validity and (c) tightness", "", _md(validity), "",
             "## (c) by size band, gap instances", "", _md(bands), "",
             "## Gain over the seed, censoring and cost", "", _md(gains), "",
             "## Counterexamples from (a)", "",
             _md(counters) if len(counters) else "none — no candidate exceeds the optimum on any certified instance.", ""]
    if attack is not None and len(attack):
        lines += ["## (b) the adversary (plan's run at 8–15 and the supplementary run together)", "",
                  _md(attack_summary(attack)), ""]
        by_size = attack.groupby(["candidate", "n"]).agg(jobs=("kind", "size"), evaluations=("evaluations", "sum"),
                                                          max_viol=("best_viol", "max")).reset_index()
        lines += ["### by size", "", _md(by_size), ""]
        summ = attack_summary(attack)
        for r in summ[summ["verdict"] == "broken"].itertuples():
            from learning.extremal import draw

            cert = recertify_counterexample(r.counter_key, r.candidate)
            lines += [draw(r.counter_key, f"counterexample to {r.candidate}"), "",
                      f"re-certified: {cert}", ""]
    lines += ["## Kill verdict", "", _md(verdict), ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return {"validity": validity, "bands": bands, "gains": gains, "counters": counters,
            "verdict": verdict, "attack": attack, "frame": frame}


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=("validity", "attack", "tables", "one"), required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--candidates", default=",".join(CANDIDATES))
    ap.add_argument("--extra", action="append", default=[], help="module:function of your own candidate")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sources", default="corpus,campaign,upward")
    ap.add_argument("--wall", type=float, default=None, help="seconds; stop dispatching after this")
    ap.add_argument("--steps", type=int, default=210)
    ap.add_argument("--restarts", type=int, default=2)
    ap.add_argument("--key", default=None)
    ap.add_argument("--sizes", default=None, help="attack sizes, e.g. 18,20,22,25 (default 8..15)")
    ap.add_argument("--attack-csv", default=None, help="where the attack rows go (default the plan's file)")
    args = ap.parse_args()
    for spec in args.extra:
        name, fn = resolve_extra(spec)
        CANDIDATES[name] = fn
    names = tuple(c for c in args.candidates.split(",") if c) + tuple(resolve_extra(s)[0] for s in args.extra)
    if args.stage == "validity":
        frame = run_validity(args.workers, names, limit=args.limit,
                             sources=tuple(args.sources.split(",")), wall=args.wall)
        print(validity_table(frame).to_string())
    elif args.stage == "attack":
        sizes = tuple(int(x) for x in args.sizes.split(",")) if args.sizes else ATTACK_SIZES
        attack = run_attack(names, args.workers, steps=args.steps, restarts=args.restarts, sizes=sizes,
                            out_csv=Path(args.attack_csv) if args.attack_csv else ATTACK_CSV)
        print(attack_summary(attack).to_string())
    elif args.stage == "tables":
        res = write_tables()
        print(res["validity"].to_string())
        print(res["verdict"].to_string())
    else:
        from learning.extremal import matrix_from_key

        vals = evaluate_candidates(matrix_from_key(args.key), {k: CANDIDATES[k] for k in names})
        for k, v in vals.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
