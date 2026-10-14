"""Independent checker for section 4's dataset (`paper1/dataset.md`).

It reads `paper1/data/dataset/pathwidth_dataset.jsonl.gz` and imports nothing
from this repository: not the builder (`paper1/dataset.py`), not a solver, not
a bound. Everything it checks is recomputed here from the record alone, with
the standard library.

For every record:

1. the graph is simple and well formed (`0 <= u < v < n`, no repeated edge,
   `m` equals the edge count);
2. the witness layout is a permutation of the vertices, and its width,
   `max_i |N(L[:i]) \\ L[:i]|`, **equals** the recorded width (an upper bound on
   the pathwidth, checked);
3. every problem value is the width plus that problem's offset
   (0 for pathwidth, vertex separation and Lengauer's game, 1 for the rest);
4. the provenance is one of `certified:refutation`, `certified:theorem`,
   `certified:minor`, `certified:bound`, `solution`;
5. for `certified:bound`, the width **equals** a lower bound computed here:
   the record's minor certificate is replayed (each contraction must be along
   an edge of the current graph) and the minor's minimum degree must reach the
   width, since `pw >= tw >= min degree of any minor`; independently of the
   certificate, the checker's own degeneracy and contraction-degeneracy
   (min-degree vertex into its least-common-neighbour neighbour) are computed
   and reported;
6. for `certified:minor` (a search refuted `width - 1` on a contracted minor),
   the record's contraction sequence, where it has one, is replayed: every
   contraction must be along an edge of the current graph, the minor must have
   the recorded size, and the refuted width must be `width - 1`. The refutation
   on the minor rests on a search, like `certified:refutation`, and is not
   checkable here; records without a sequence are counted;
7. for `certified:theorem`, the theorem must be one this checker knows and
   its hypothesis is recomputed from the graph: for the grid theorem
   (pw((h, w)-grid) = min(h, w), Ellis & Warren 2008, Theorem 4.1; Lean
   `pathwidth_grid`), the graph must be an h x w grid, which is checked by
   building the coordinates from two corners and testing every edge, and the
   width must be min(h, w). A flag in the record is never trusted;
8. every member's map to the representative is a permutation of the vertices;
   with `--sources`, the member's source file is re-read with this file's own
   readers and the map is checked to be an isomorphism onto the record's graph
   (collections in a format this checker does not read are counted as skipped).

A `certified:refutation` cannot be checked from the record: it rests on a
search (the repaired-rules customer search, `paper1/revised_algorithm.md`).
Nor can the refutation behind a `certified:minor`: the checker replays the
contraction sequence, which shows the minor is genuine, but the claim that the
minor has no layout of width `width - 1` rests on the same search. The checker
reports how many records rest on one.

    python paper1/dataset_check.py                    # every record
    python paper1/dataset_check.py --sources          # also re-read member sources
    python paper1/dataset_check.py --limit 500        # the first 500 records

Exit status 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import bz2
import gzip
import json
import lzma
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT = HERE / "data" / "dataset" / "pathwidth_dataset.jsonl.gz"

PROVENANCES = ("certified:refutation", "certified:theorem", "certified:minor", "certified:bound",
               "solution")
GRID_LEAN = "MOSPFormalization.pathwidth_grid"
OFFSETS = {
    "pathwidth": 0, "vertex separation": 0, "Lengauer's vertex separator game": 0,
    "MOSP": 1, "gate matrix layout (incl. multiple PLA folding)": 1,
    "one-dimensional logic": 1, "interval thickness": 1, "narrowness": 1,
    "node search number": 1,
}


# --------------------------------------------------------------------------
# Graph measures
# --------------------------------------------------------------------------

def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def width_of_layout(adj, layout):
    """Largest boundary of a prefix: vertices outside it with a neighbour in it."""
    inside = [False] * len(adj)
    boundary = set()
    best = 0
    for v in layout:
        inside[v] = True
        boundary.discard(v)
        for w in adj[v]:
            if not inside[w]:
                boundary.add(w)
        if len(boundary) > best:
            best = len(boundary)
    return best


def degeneracy(adj):
    adj = [set(a) for a in adj]
    alive = set(range(len(adj)))
    best = 0
    while alive:
        v = min(alive, key=lambda x: len(adj[x]))
        best = max(best, len(adj[v]))
        for w in adj[v]:
            adj[w].discard(v)
        alive.discard(v)
    return best


def contraction_degeneracy(adj, max_n=1500):
    if len(adj) > max_n:
        return None
    adj = [set(a) for a in adj]
    alive = set(range(len(adj)))
    best = 0
    while len(alive) > 1:
        v = min(alive, key=lambda x: (len(adj[x]), -x))
        best = max(best, len(adj[v]))
        if not adj[v]:
            alive.discard(v)
            continue
        u = min(adj[v], key=lambda c: (len(adj[c] & adj[v]), -c))
        for w in adj[v]:
            adj[w].discard(v)
            if w != u:
                adj[w].add(u)
                adj[u].add(w)
        adj[v] = set()
        alive.discard(v)
    return best


def replay_minor(adj, ops):
    """Apply deletions and edge contractions; return the minor's minimum degree,
    or raise ValueError if an operation is not valid on the current graph."""
    adj = [set(a) for a in adj]
    alive = set(range(len(adj)))
    for op in ops:
        if op[0] == "d":
            v = op[1]
            if v not in alive:
                raise ValueError(f"delete of a removed vertex {v}")
            for w in adj[v]:
                adj[w].discard(v)
            adj[v] = set()
            alive.discard(v)
        elif op[0] == "c":
            v, u = op[1], op[2]
            if v not in alive or u not in alive or u not in adj[v]:
                raise ValueError(f"contraction {v}->{u} is not along an edge")
            for w in adj[v]:
                adj[w].discard(v)
                if w != u:
                    adj[w].add(u)
                    adj[u].add(w)
            adj[v] = set()
            alive.discard(v)
        else:
            raise ValueError(f"unknown operation {op!r}")
    if not alive:
        return 0
    return min(len(adj[v]) for v in alive)


def replay_contractions(adj, contractions):
    """Apply a contraction sequence `[[v, u], ...]` (contract `v` into `u`; `u`
    null deletes `v`); return the minor's vertex count, or raise ValueError if
    a contraction is not along an edge of the current graph."""
    ops = [["d", v] if u is None else ["c", v, u] for v, u in contractions]
    adj = [set(a) for a in adj]
    alive = set(range(len(adj)))
    for op in ops:
        v = op[1]
        if not isinstance(v, int) or v not in alive:
            raise ValueError(f"step {op}: vertex {v} is not in the current graph")
        if op[0] == "c":
            u = op[2]
            if not isinstance(u, int) or u not in alive or u not in adj[v]:
                raise ValueError(f"contraction {v}->{u} is not along an edge")
            for w in adj[v]:
                adj[w].discard(v)
                if w != u:
                    adj[w].add(u)
                    adj[u].add(w)
        else:
            for w in adj[v]:
                adj[w].discard(v)
        adj[v] = set()
        alive.discard(v)
    return len(alive)


def _bfs(adj, s):
    dist = [-1] * len(adj)
    dist[s] = 0
    queue = [s]
    for x in queue:
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


def grid_shape(adj):
    """(h, w) with h <= w if the graph is an h x w grid (h, w >= 2), else None.

    A corner `a` (degree 2) and a nearest other corner `b` span one side, of
    length w - 1. Coordinates follow from the two distance maps,
    i = (d_a + d_b - (w - 1)) / 2 and j = (d_a - d_b + (w - 1)) / 2; the graph
    is the grid exactly when these are a bijection onto [0, h) x [0, w) and the
    edges are exactly the pairs at coordinate distance one."""
    n = len(adj)
    corners = [v for v in range(n) if len(adj[v]) == 2]
    if n < 4 or len(corners) != 4:
        return None
    a = corners[0]
    da = _bfs(adj, a)
    if min(da) < 0:
        return None
    b = min(corners[1:], key=lambda c: da[c])
    w = da[b] + 1
    if n % w:
        return None
    h = n // w
    db = _bfs(adj, b)
    coord = {}
    for v in range(n):
        i2, j2 = da[v] + db[v] - (w - 1), da[v] - db[v] + (w - 1)
        if i2 % 2 or j2 % 2:
            return None
        i, j = i2 // 2, j2 // 2
        if not (0 <= i < h and 0 <= j < w) or (i, j) in coord:
            return None
        coord[(i, j)] = v
    m = sum(len(x) for x in adj) // 2
    if m != h * (w - 1) + w * (h - 1):
        return None
    for (i, j), v in coord.items():
        want = {coord[p] for p in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)) if p in coord}
        if set(adj[v]) != want:
            return None
    return (min(h, w), max(h, w))


# --------------------------------------------------------------------------
# Readers for --sources (this file's own; formats as documented by each collection)
# --------------------------------------------------------------------------

def _simple(n, pairs):
    E = set()
    for u, v in pairs:
        if u != v:
            E.add((min(u, v), max(u, v)))
    return n, E


def _clique_graph(rows):
    """Customers x patterns rows -> (n, edge set): customers sharing a pattern."""
    pats = {}
    for c, r in enumerate(rows):
        for j, x in enumerate(r):
            if x:
                pats.setdefault(j, []).append(c)
    pairs = [(a, b) for cs in pats.values() for i, a in enumerate(cs) for b in cs[i + 1:]]
    return _simple(len(rows), pairs)


def read_challenge(path: Path, index):
    """Constraint Modelling Challenge 2005 files hold several instances, each an
    optional description line, a line `rows cols`, then rows x cols 0/1 values
    (customers x products, rows possibly wrapped). Read as a token stream; the
    instance at position `index` is returned."""
    if index is None:
        return None
    instances = []
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        p = lines[i].split()
        if len(p) == 2 and all(t.isdigit() for t in p) and int(p[0]) > 0 and int(p[1]) > 0:
            r, c = int(p[0]), int(p[1])
            vals = []
            i += 1
            while len(vals) < r * c and i < len(lines):
                q = lines[i].split()
                if q and all(t in ("0", "1") for t in q):
                    vals.extend(int(t) for t in q)
                    i += 1
                elif not q:
                    i += 1
                else:
                    break
            instances.append([vals[k * c:(k + 1) * c] for k in range(len(vals) // c)])
        else:
            i += 1
    if index >= len(instances):
        return None
    return _clique_graph(instances[index])


def read_source(path: Path, collection: str, name: str, index=None):
    """(n, edge set) of a member's own file, 0-based, or None if this checker
    does not read that collection's format."""
    fn = path.name
    if collection.startswith("MOSP: Challenge 2005") and "MOSP_Instances" not in str(path):
        return read_challenge(path, index)
    if collection.startswith("MOSP") or collection.startswith("VLSI"):
        rows = [list(map(int, l.split())) for l in path.read_text().splitlines() if l.strip()][1:]
        # MOSP_Instances (Chu & Stuckey format) and Frinhani: rows are patterns -> transpose.
        # VLSI (Lorena) and Carvalho & Soma: rows are nets / customers already.
        if not collection.startswith(("VLSI", "MOSP: Carvalho")):
            rows = [list(c) for c in zip(*rows)]
        n = len(rows)
        pats = {}
        for c, r in enumerate(rows):
            for j, x in enumerate(r):
                if x:
                    pats.setdefault(j, []).append(c)
        pairs = [(a, b) for cs in pats.values() for i, a in enumerate(cs) for b in cs[i + 1:]]
        return _simple(n, pairs)
    if fn.endswith(".graphml"):
        root = ET.parse(path).getroot()
        ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
        nodes = [nd.get("id") for nd in root.iter(ns + "node")]
        idx = {v: i for i, v in enumerate(nodes)}
        pairs = [(idx[e.get("source")], idx[e.get("target")]) for e in root.iter(ns + "edge")]
        return _simple(len(nodes), pairs)
    opener = lzma.open if fn.endswith(".xz") else bz2.open if fn.endswith(".bz2") else open
    with opener(path, "rt") as fh:
        lines = fh.read().splitlines()
    if ".gr" in fn or fn.endswith(".dgf"):
        n, pairs = 0, []
        for line in lines:
            p = line.split()
            if not p or p[0] in ("c", "n", "x"):
                continue
            if p[0] == "p":
                n = int(p[2])
            elif p[0] == "e":
                pairs.append((int(p[1]) - 1, int(p[2]) - 1))
            else:
                pairs.append((int(p[0]) - 1, int(p[1]) - 1))
        return _simple(n, pairs)
    body = [l.split() for l in lines if l.strip()]
    if not body[0][0].isdigit():
        body = body[1:]
    n = int(body[0][0])
    return _simple(n, [(int(p[0]) - 1, int(p[1]) - 1) for p in body[1:] if len(p) >= 2])


# --------------------------------------------------------------------------
# The check
# --------------------------------------------------------------------------

def check_record(rec, sources=False, root=REPO):
    """List of failure strings for one record (empty if it passes), and a dict
    of facts for the report."""
    fails = []
    facts = {}
    n, edges = rec["n"], rec["edges"]
    seen = set()
    for e in edges:
        u, v = e
        if not (0 <= u < v < n):
            fails.append(f"bad edge {e}")
            break
        if (u, v) in seen:
            fails.append(f"repeated edge {e}")
            break
        seen.add((u, v))
    if rec["m"] != len(edges):
        fails.append(f"m={rec['m']} but {len(edges)} edges")
    if fails:
        return fails, facts
    adj = adjacency(n, edges)
    layout = rec["layout"]
    if sorted(layout) != list(range(n)):
        fails.append("layout is not a permutation of the vertices")
    else:
        w = width_of_layout(adj, layout)
        facts["layout_width"] = w
        if w != rec["width"]:
            fails.append(f"layout width {w} != recorded width {rec['width']}")
    for p, k in OFFSETS.items():
        if rec["values"].get(p) != rec["width"] + k:
            fails.append(f"value of {p} is {rec['values'].get(p)}, expected {rec['width'] + k}")
    if rec["provenance"] not in PROVENANCES:
        fails.append(f"unknown provenance {rec['provenance']!r}")
    if rec["provenance"] == "certified:bound":
        own = degeneracy(adj)
        cd = contraction_degeneracy(adj)
        if cd is not None:
            own = max(own, cd)
        facts["own_bound"] = own
        cert = rec.get("lower_bound_certificate")
        cert_ok = False
        if cert is not None:
            try:
                md = replay_minor(adj, cert["ops"])
                facts["certificate_min_degree"] = md
                cert_ok = md >= rec["width"]
                if not cert_ok:
                    fails.append(f"minor certificate reaches {md} < width {rec['width']}")
            except ValueError as exc:
                fails.append(f"minor certificate invalid: {exc}")
        elif own < rec["width"]:
            fails.append(f"certified:bound with no certificate and own bound {own} < {rec['width']}")
        facts["bound_by_certificate"] = cert_ok
    if rec["provenance"] == "certified:minor":
        cert = rec.get("minor_certificate")
        facts["minor_by_certificate"] = False
        if cert is not None:
            try:
                size = replay_contractions(adj, cert["contractions"])
                if cert.get("refuted") != rec["width"] - 1:
                    fails.append(f"minor certificate refutes {cert.get('refuted')}, width is {rec['width']}")
                elif "size" in cert and size != cert["size"]:
                    fails.append(f"minor certificate leaves {size} vertices, not {cert['size']}")
                else:
                    facts["minor_by_certificate"] = True
            except (ValueError, TypeError, KeyError) as exc:
                fails.append(f"minor certificate invalid: {exc}")
    if rec["provenance"] == "certified:theorem":
        th = rec.get("theorem") or {}
        if th.get("family") != "grid" or not str(th.get("lean", "")).startswith(GRID_LEAN):
            fails.append(f"certified:theorem names no theorem this checker knows: {th!r}")
        else:
            shape = grid_shape(adj)
            if shape is None:
                fails.append("certified:theorem (grid), but the graph is not a grid")
            elif min(shape) != rec["width"]:
                fails.append(f"grid {shape[0]} x {shape[1]} has pathwidth {min(shape)}, record says {rec['width']}")
            elif sorted((th.get("h"), th.get("w"))) != list(shape):
                fails.append(f"record names a {th.get('h')} x {th.get('w')} grid, the graph is {shape[0]} x {shape[1]}")
            else:
                facts["theorem_checked"] = True
    for mem in rec["members"]:
        perm = mem.get("to_representative")
        if perm is not None and sorted(perm) != list(range(n)):
            fails.append(f"member {mem['source']}: map is not a permutation")
            continue
        if sources:
            path = root / mem["source"]
            if not path.exists():
                facts.setdefault("sources_missing", 0)
                facts["sources_missing"] += 1
                continue
            got = read_source(path, mem["collection"], mem["name"], mem.get("index_in_file"))
            if got is None:
                facts["sources_skipped"] = facts.get("sources_skipped", 0) + 1
                continue
            sn, sedges = got
            if sn != n:
                fails.append(f"member {mem['source']}: {sn} vertices, record has {n}")
                continue
            mapped = {(min(a, b), max(a, b)) for a, b in
                      ((perm[u], perm[v]) if perm else (u, v) for u, v in sedges)}
            if mapped != seen:
                fails.append(f"member {mem['source']}: map is not an isomorphism onto the record")
            else:
                facts["sources_checked"] = facts.get("sources_checked", 0) + 1
    return fails, facts


def check(path=DEFAULT, sources=False, limit=None, out=sys.stdout):
    t0 = time.time()
    prov = Counter()
    prov_members = Counter()
    by_coll = Counter()
    failures = []
    totals = Counter()
    records = 0
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if limit is not None and records >= limit:
                break
            rec = json.loads(line)
            records += 1
            fails, facts = check_record(rec, sources=sources)
            prov[rec["provenance"]] += 1
            for m in rec["members"]:
                prov_members[rec["provenance"]] += 1
                by_coll[(m["collection"], rec["provenance"])] += 1
            for k in ("sources_checked", "sources_skipped", "sources_missing"):
                totals[k] += facts.get(k, 0)
            if rec["provenance"] == "certified:bound":
                totals["bound"] += 1
                totals["bound_by_certificate"] += facts.get("bound_by_certificate", False)
                totals["bound_by_own"] += facts.get("own_bound", -1) >= rec["width"]
            if rec["provenance"] == "certified:minor":
                totals["minor"] += 1
                totals["minor_by_certificate"] += facts.get("minor_by_certificate", False)
            if rec["provenance"] == "certified:theorem":
                totals["theorem"] += 1
                totals["theorem_checked"] += facts.get("theorem_checked", False)
            for f in fails:
                failures.append(f"{rec['id']}: {f}")
    print(f"records checked: {records} in {time.time() - t0:.1f} s", file=out)
    print("provenance (records, i.e. isomorphism classes):", file=out)
    for p in PROVENANCES:
        print(f"  {p:22s} {prov[p]:6d}   members {prov_members[p]:6d}", file=out)
    print(f"certified:bound re-established by the minor certificate: "
          f"{totals['bound_by_certificate']} / {totals['bound']}; "
          f"by the checker's own bounds alone: {totals['bound_by_own']} / {totals['bound']}", file=out)
    print(f"certified:refutation (rests on a search, not checkable here): {prov['certified:refutation']}",
          file=out)
    print(f"certified:minor contraction sequences replayed: {totals['minor_by_certificate']} / "
          f"{totals['minor']} (the refutation on the minor rests on a search, not checkable here)", file=out)
    print(f"certified:theorem hypotheses recomputed (grid recognised, width = min(h, w)): "
          f"{totals['theorem_checked']} / {totals['theorem']}", file=out)
    if sources:
        print(f"member sources re-read and matched: {totals['sources_checked']}, "
              f"skipped (format not read here): {totals['sources_skipped']}, "
              f"missing on disk: {totals['sources_missing']}", file=out)
    print("members by collection and provenance:", file=out)
    for coll in sorted({c for c, _ in by_coll}):
        cells = ", ".join(f"{p.split(':')[-1]} {by_coll[(coll, p)]}" for p in PROVENANCES if by_coll[(coll, p)])
        print(f"  {coll}: {cells}", file=out)
    print(f"FAILURES: {len(failures)}", file=out)
    for f in failures[:50]:
        print(f"  {f}", file=out)
    return failures, dict(records=records, provenance=dict(prov), totals=dict(totals))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Independent checker for the pathwidth dataset.")
    ap.add_argument("path", nargs="?", default=str(DEFAULT))
    ap.add_argument("--sources", action="store_true", help="re-read member source files")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    failures, _ = check(Path(a.path), sources=a.sources, limit=a.limit)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
