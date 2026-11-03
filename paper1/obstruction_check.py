#!/usr/bin/env python3
"""Independent checker for the obstruction certificates of Ralph loop0013.

Imports nothing from `learning/`, `satisfiability/`, `pathwidth_solver/` or
`mosp/`: it has its own instance reader, its own graph construction, its own
CNF generator and (for later items) its own contraction replay and BFS. The
only thing it shares with the search is the *contract* below, copied by hand
from `learning/obstruction_expansion.py::ENCODING_SPEC` (the test
`tests/test_obstruction_expansion.py::test_checker_shares_only_the_spec`
pins the two texts equal).

    python3 paper1/obstruction_check.py check-expansion <instance.mosp> <certificate.json>
        [--drat-trim tools/drat-trim/drat-trim] [--timeout S] [--json]
    python3 paper1/obstruction_check.py check-minor <instance.mosp | edges.txt> <certificate.json>
        [--c-binary pathwidth_solver/cli/pathwidth] [--c-cap S] [--no-rulefree] [--rulefree-cap S] [--json]

`check-minor` (item 04, family M) reads the instance (or an edge list: "n e"
then one "u v" per line, 0-based), builds the MOSP graph, replays the
certificate's contraction sequence with its own code (every pair `[v, u]`
must be an edge of the current graph at its step; `u = -1` only for an
isolated `v`), rebuilds the quotient from the branch sets and compares its
edge hash with the certificate's (the contract: SHA-256 of "m e\n" then one
"a b\n" per edge, sorted, `a < b`, labels `0..m-1` in increasing order of the
surviving representative), writes the minor as graph6 with its own encoder,
re-runs the C program `pathwidth_solver/cli/pathwidth` on it with the cap
given (`-m min_vertices=1000000`: the C's own minor step off) and accepts
when the C proves at least the pathwidth the certificate claims
(`refutation`/`bound` status with width >= claim, or printed `lower` >=
claim); and, where `m <= 80` and `vsmemo.c` / `checkF.c` are present under
`reports/scratch/minor_certificates/`, compiles them into a temporary
directory and runs the rule-free refutation of `claim - 1` on the minor
(`vsmemo -o -w F`, under the cap and an 8 GB address-space limit) and
`checkF` on its family of sets, recording `verified`, `unknown` (budget),
`skipped` or `failed`. The verdict is `verified` when the replay, the hash
and the C check pass; the rule-free check is recorded beside it (it is the
check independent of the search rules, where it fits). What it certifies:
`pw(minor) >= p` with the minor a contraction minor of the MOSP graph, so
`pw(G) >= p` (`pathwidth_gt_of_minorOf`, `lean/MOSPFormalization/Minor.lean`)
and `MOSP >= p + 1` (`mospValue_eq_pathwidth_add_one`).

`check-expansion` reads the instance in the standard `.mosp` format (name,
"n m", `n` rows of `m` space-separated 0/1 values), builds the MOSP graph
(customers as vertices, a clique per pattern), regenerates the CNF of the
certificate's `(t, b)` from the contract, compares its SHA-256 with the
certificate's, decompresses the DRAT proof the certificate names, runs
`drat-trim` on the regenerated CNF, and prints the bound the certificate
proves with the theorem it rests on. Exit status 0 when every check passes
(`verdict: verified`), 1 otherwise. The certificate also carries the SHA-256
of the instance's 0/1 rows, which is compared with the file read.

What it certifies: an UNSAT CNF at `(t, b)` says no set `C` of at least `t`
customers has `|N[C]| <= b`, so `f(t) = min_{|C| = t} |N[C]| >= b + 1`; by
`exists_closedNbhd_card_le` (`lean/MOSPFormalization/EmptyPair.lean`: for
every `j` some `j`-set has `|N[A]| <= j + pathwidth`), `pathwidth >= b + 1 - t`
and, by `mospValue_eq_pathwidth_add_one`, `MOSP >= b + 2 - t`. The checker
trusts drat-trim and the two theorems, and nothing of ours.

The contract (expansion-cnf-1), verbatim:

expansion-cnf-1 — the decision "some C with |C| >= t has |N[C]| <= b".

Vertices 0..n-1 (customers in file order); N[u] is the closed neighbourhood in
the MOSP graph (a clique per pattern, plus u itself). Variables, 1-based:
  x_v = v + 1          (v in C)
  y_v = n + v + 1      (v in N[C])
  auxiliaries from 2n + 1 upward, in the order the totalizers allocate them.
Clauses:
  (1) for every u, for every v in N[u] (including v = u): [-x_u, y_v];
  (2) a full totalizer over [x_0, ..., x_{n-1}] (allocated first), with the unit
      clause [o_t] on its root outputs (o_1..o_n; 1 <= t <= n);
  (3) a full totalizer over [y_0, ..., y_{n-1}] (allocated second), with the unit
      clause [-o_{b+1}] on its root outputs (0 <= b <= n - 1).
The totalizer of a list L of literals: one literal is its own output (no
clauses, no variables); otherwise split A = L[:len(L)//2], B = L[len(L)//2:],
build A's totalizer, then B's, then allocate the node's outputs o_1..o_{p+q}
(p = |A|, q = |B|) as fresh consecutive variables; with a_0 = b_0 = true and
a_{p+1} = b_{q+1} = false (omitted literals), add for every i in 0..p and
j in 0..q:  [-a_i, -b_j, o_{i+j}] when i + j >= 1, and
            [a_{i+1}, b_{j+1}, -o_{i+j+1}] when i + j + 1 <= p + q.
Canonical form: literals within a clause sorted by integer value, duplicate
clauses removed, clauses sorted lexicographically; the DIMACS text is
"p cnf <nv> <m>" then one clause per line ending in " 0", "\\n" line ends; the
CNF's SHA-256 is of that text. UNSAT proves f(t) = min_{|C| = t} |N[C]| >= b + 1,
hence pathwidth >= b + 1 - t and MOSP >= b + 2 - t
(`exists_closedNbhd_card_le`, contrapositive).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DRAT_TRIM = ROOT / "tools" / "drat-trim" / "drat-trim"
THEOREMS = ("exists_closedNbhd_card_le (lean/MOSPFormalization/EmptyPair.lean), contrapositive; "
            "mospValue_eq_pathwidth_add_one (lean/MOSPFormalization/MOSPGraph.lean)")


# ----------------------------------------------------------------------------
# the instance and its graph (own code)
# ----------------------------------------------------------------------------


def read_mosp(path: Path) -> tuple[str, list[list[int]]]:
    """The standard format: name, "n m", n rows of m 0/1 values."""
    lines = [ln for ln in Path(path).read_text().splitlines()]
    name = lines[0].strip()
    n, m = (int(x) for x in lines[1].split()[:2])
    rows = []
    for i in range(n):
        row = [int(x) for x in lines[2 + i].split()]
        if len(row) != m or any(x not in (0, 1) for x in row):
            raise ValueError(f"row {i}: expected {m} values in 0/1")
        rows.append(row)
    return name, rows


def rows_sha256(rows: list[list[int]]) -> str:
    text = "".join(" ".join(str(v) for v in row) + "\n" for row in rows)
    return hashlib.sha256(text.encode()).hexdigest()


def closed_neighbourhoods(rows: list[list[int]]) -> list[set[int]]:
    """`N[u]` in the MOSP graph: the customers sharing a pattern with `u`, and `u`."""
    n = len(rows)
    m = len(rows[0]) if rows else 0
    closed = [{u} for u in range(n)]
    for j in range(m):
        holders = [u for u in range(n) if rows[u][j] == 1]
        for u in holders:
            closed[u].update(holders)
    return closed


# ----------------------------------------------------------------------------
# the CNF (own code, from the contract)
# ----------------------------------------------------------------------------


def totalizer(lits: list[int], next_var: int, clauses: list[list[int]]) -> tuple[list[int], int]:
    if len(lits) == 1:
        return [lits[0]], next_var
    half = len(lits) // 2
    a, next_var = totalizer(lits[:half], next_var, clauses)
    b, next_var = totalizer(lits[half:], next_var, clauses)
    p, q = len(a), len(b)
    outs = list(range(next_var, next_var + p + q))
    next_var += p + q
    for i in range(p + 1):
        for j in range(q + 1):
            if i + j >= 1:
                clause = []
                if i >= 1:
                    clause.append(-a[i - 1])
                if j >= 1:
                    clause.append(-b[j - 1])
                clause.append(outs[i + j - 1])
                clauses.append(clause)
            if i + j + 1 <= p + q:
                clause = []
                if i + 1 <= p:
                    clause.append(a[i])
                if j + 1 <= q:
                    clause.append(b[j])
                clause.append(-outs[i + j])
                clauses.append(clause)
    return outs, next_var


def expansion_cnf(closed: list[set[int]], t: int, b: int) -> tuple[list[list[int]], int]:
    n = len(closed)
    if not 1 <= t <= n or not 0 <= b <= n - 1:
        raise ValueError(f"need 1 <= t <= n and 0 <= b <= n - 1, got n={n}, t={t}, b={b}")
    x = [v + 1 for v in range(n)]
    y = [n + v + 1 for v in range(n)]
    clauses: list[list[int]] = []
    for u in range(n):
        for v in sorted(closed[u]):
            clauses.append([-x[u], y[v]])
    next_var = 2 * n + 1
    ox, next_var = totalizer(x, next_var, clauses)
    clauses.append([ox[t - 1]])
    oy, next_var = totalizer(y, next_var, clauses)
    clauses.append([-oy[b]])
    canon = sorted({tuple(sorted(cl)) for cl in clauses})
    return [list(cl) for cl in canon], next_var - 1


def dimacs(clauses: list[list[int]], nv: int) -> bytes:
    lines = [f"p cnf {nv} {len(clauses)}"]
    lines.extend(" ".join(map(str, cl)) + " 0" for cl in clauses)
    return ("\n".join(lines) + "\n").encode()


def cnf_sha256(clauses: list[list[int]], nv: int) -> str:
    return hashlib.sha256(dimacs(clauses, nv)).hexdigest()


# ----------------------------------------------------------------------------
# check-expansion
# ----------------------------------------------------------------------------


def run_drat_trim(cnf_bytes: bytes, proof_bytes: bytes, binary: Path, timeout: float | None) -> tuple[str, float, str]:
    with tempfile.TemporaryDirectory() as tmp:
        cnf_path, proof_path = Path(tmp) / "f.cnf", Path(tmp) / "p.drat"
        cnf_path.write_bytes(cnf_bytes)
        proof_path.write_bytes(proof_bytes)
        started = time.monotonic()
        try:
            out = subprocess.run([str(binary), str(cnf_path), str(proof_path)], capture_output=True,
                                 text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            return "check_timeout", round(time.monotonic() - started, 3), ""
        except OSError as exc:
            return "checker_error", round(time.monotonic() - started, 3), str(exc)
        seconds = round(time.monotonic() - started, 3)
        tail = "\n".join(out.stdout.strip().splitlines()[-3:])
        if "s VERIFIED" in out.stdout:
            return "verified", seconds, tail
        return "not_verified", seconds, tail or out.stderr.strip()[-300:]


def check_expansion(instance_path: Path, certificate_path: Path, drat_trim: Path = DEFAULT_DRAT_TRIM,
                    timeout: float | None = None) -> dict:
    """Every check, as a dict; `verdict` is `verified` only when all pass."""
    result: dict = {"instance": str(instance_path), "certificate": str(certificate_path), "checks": [], "verdict": ""}
    cert = json.loads(Path(certificate_path).read_text())
    name, rows = read_mosp(Path(instance_path))
    n = len(rows)
    t, b = int(cert["t"]), int(cert["b"])
    result.update({"instance_name": name, "n": n, "t": t, "b": b})

    def check(label: str, ok: bool, detail: str = "") -> bool:
        result["checks"].append({"check": label, "ok": bool(ok), "detail": detail})
        return bool(ok)

    ok = check("encoding is expansion-cnf-1", cert.get("encoding") == "expansion-cnf-1", str(cert.get("encoding")))
    ok &= check("instance size matches", n == int(cert["n"]), f"file n={n}, certificate n={cert['n']}")
    digest_rows = rows_sha256(rows)
    ok &= check("instance rows SHA-256 matches", digest_rows == cert.get("matrix_sha256"),
                f"{digest_rows[:16]}… vs {str(cert.get('matrix_sha256'))[:16]}…")
    ok &= check("(t, b) in range", 1 <= t <= n and 0 <= b <= n - 1, f"t={t}, b={b}, n={n}")
    if not ok:
        result["verdict"] = "rejected"
        return result
    closed = closed_neighbourhoods(rows)
    clauses, nv = expansion_cnf(closed, t, b)
    digest = cnf_sha256(clauses, nv)
    result.update({"cnf_variables": nv, "cnf_clauses": len(clauses), "cnf_sha256": digest})
    ok &= check("CNF SHA-256 matches the certificate", digest == cert.get("cnf_sha256"),
                f"{digest[:16]}… vs {str(cert.get('cnf_sha256'))[:16]}…")
    ok &= check("CNF size matches", nv == int(cert.get("cnf_variables", -1)) and len(clauses) == int(cert.get("cnf_clauses", -1)),
                f"{nv} variables, {len(clauses)} clauses")
    proof_file = cert.get("proof_file")
    if not proof_file:
        ok &= check("proof present", False, "the certificate names no proof file (hash only)")
        result["verdict"] = "rejected"
        return result
    proof_path = Path(certificate_path).parent / proof_file
    if not proof_path.exists():
        ok &= check("proof present", False, f"{proof_path} missing")
        result["verdict"] = "rejected"
        return result
    with gzip.open(proof_path, "rb") as fh:
        proof = fh.read()
    proof_digest = hashlib.sha256(proof).hexdigest()
    ok &= check("proof SHA-256 matches", proof_digest == cert.get("proof_sha256"),
                f"{proof_digest[:16]}… vs {str(cert.get('proof_sha256'))[:16]}…, {len(proof)} bytes")
    if not Path(drat_trim).exists():
        ok &= check("drat-trim available", False, str(drat_trim))
        result["verdict"] = "rejected"
        return result
    verdict, seconds, tail = run_drat_trim(dimacs(clauses, nv), proof, Path(drat_trim), timeout)
    result.update({"drat_trim": verdict, "check_seconds": seconds, "drat_trim_output": tail})
    ok &= check("drat-trim verifies the proof on the regenerated CNF", verdict == "verified", verdict)
    result["verdict"] = "verified" if ok else "rejected"
    if ok:
        result["proves"] = {"f_t_at_least": b + 1, "pathwidth_at_least": b + 1 - t, "mosp_at_least": b + 2 - t,
                            "statement": f"no set of {t} customers has a closed neighbourhood of at most {b} "
                                         f"customers, so pathwidth >= {b + 1 - t} and MOSP >= {b + 2 - t}",
                            "theorems": THEOREMS}
    return result


# ----------------------------------------------------------------------------
# family M: contraction minors (own replay, own graph6, the C program, rule-free)
# ----------------------------------------------------------------------------

DEFAULT_C_BINARY = ROOT / "pathwidth_solver" / "cli" / "pathwidth"
RULEFREE_DIR = ROOT / "reports" / "scratch" / "minor_certificates"
MINOR_THEOREMS = ("pathwidth_gt_of_minorOf / pathwidth_minorOf_le (lean/MOSPFormalization/Minor.lean); "
                  "mospValue_eq_pathwidth_add_one (lean/MOSPFormalization/MOSPGraph.lean)")


def read_edges(path: Path) -> tuple[str, int, list[tuple[int, int]]]:
    """An edge list: "n e" then e lines "u v", 0-based."""
    text = Path(path).read_text().split()
    n, e = int(text[0]), int(text[1])
    vals = [int(x) for x in text[2:2 + 2 * e]]
    if len(vals) != 2 * e:
        raise ValueError("edge list is short")
    return Path(path).stem, n, [(a, b) for a, b in zip(vals[0::2], vals[1::2])]


def graph_from_rows(rows: list[list[int]]) -> dict[int, set[int]]:
    closed = closed_neighbourhoods(rows)
    return {u: set(closed[u]) - {u} for u in range(len(rows))}


def graph_from_edges(n: int, edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    G = {u: set() for u in range(n)}
    for a, b in edges:
        if a != b:
            G[a].add(b)
            G[b].add(a)
    return G


def edges_sha256(m: int, edges) -> str:
    edges = sorted((min(a, b), max(a, b)) for a, b in edges)
    text = f"{m} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges)
    return hashlib.sha256(text.encode()).hexdigest()


def graph_edges(G: dict[int, set[int]]) -> list[tuple[int, int]]:
    return sorted((a, b) for a in G for b in G[a] if a < b)


def replay_minor(G: dict[int, set[int]], seq, deleted: set[int] | None = None) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """Replay `[v, u]` pairs (contract `v` into `u`; `[v, -1]` deletes an
    isolated `v`), raising ValueError at the first pair that is not an edge of
    the current graph. Returns the minor over the surviving labels and the
    branch sets; the branch sets of deleted vertices are added to `deleted`
    when given (an isolated representative may have absorbed a whole
    component before its deletion; deleting it deletes those vertices)."""
    H = {v: set(N) for v, N in G.items()}
    branch = {v: {v} for v in G}
    for step, pair in enumerate(seq):
        v, u = int(pair[0]), int(pair[1])
        if v not in H:
            raise ValueError(f"step {step}: {v} is not in the current graph")
        if u == -1:
            if H[v]:
                raise ValueError(f"step {step}: deleting {v}, which has {len(H[v])} neighbours")
            del H[v]
            gone = branch.pop(v)
            if deleted is not None:
                deleted |= gone       # the whole branch set leaves the graph (a vertex deletion in the minor)
            continue
        if u == v or u not in H or u not in H[v]:
            raise ValueError(f"step {step}: ({v}, {u}) is not an edge of the current graph")
        for w in H[v]:
            H[w].discard(v)
            if w != u:
                H[w].add(u)
                H[u].add(w)
        del H[v]
        H[u].discard(u)
        H[u].discard(v)
        branch[u] |= branch.pop(v)
    return H, branch


def quotient_by_branch_sets(G: dict[int, set[int]], branch: dict[int, set[int]],
                            deleted: set[int] = frozenset()) -> dict[int, set[int]]:
    """The quotient from the branch sets alone; the branch sets and the
    deleted (isolated) vertices must partition the vertex set."""
    rep = {x: r for r, B in branch.items() for x in B}
    if sorted(list(rep) + list(deleted)) != sorted(G) or set(rep) & set(deleted):
        raise ValueError("branch sets and deleted vertices do not partition the vertex set")
    Q = {r: set() for r in branch}
    for a in G:
        if a in deleted:
            continue
        for b in G[a]:
            if rep[a] != rep[b]:
                Q[rep[a]].add(rep[b])
    return Q


def relabel(H: dict[int, set[int]]) -> tuple[list[int], list[tuple[int, int]]]:
    labels = sorted(H)
    index = {r: i for i, r in enumerate(labels)}
    return labels, sorted((index[a], index[b]) for a in H for b in H[a] if a < b)


def graph6_encode(m: int, edges: list[tuple[int, int]]) -> str:
    """graph6 (McKay): N(m) then the upper triangle column by column, 6 bits
    per character, offset 63. Own code; `m < 63` uses the one-byte size."""
    if m <= 62:
        head = chr(m + 63)
    elif m <= 258047:
        head = "~" + "".join(chr(((m >> s) & 63) + 63) for s in (12, 6, 0))
    else:
        raise ValueError("too many vertices")
    adj = [set() for _ in range(m)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    bits_ = []
    for j in range(1, m):
        for i in range(j):
            bits_.append(1 if j in adj[i] else 0)
    while len(bits_) % 6:
        bits_.append(0)
    body = "".join(chr(int("".join(map(str, bits_[k:k + 6])), 2) + 63) for k in range(0, len(bits_), 6))
    return head + body


def run_pathwidth_c(g6: str, cap: float, binary: Path) -> dict:
    cmd = ["nice", "-n", "19", str(binary), "-t", f"{cap:g}", "-l", "-v", "-m", "min_vertices=1000000"]
    t0 = time.monotonic()
    proc = subprocess.run(cmd, input=g6 + "\n", capture_output=True, text=True, timeout=cap * 10 + 60)
    out = {"stdout": proc.stdout.strip().splitlines(), "stderr": proc.stderr.strip().splitlines(),
           "returncode": proc.returncode, "seconds": time.monotonic() - t0, "width": None, "status": None, "lower": None}
    for line in out["stdout"]:
        parts = line.split()
        if parts and parts[0] == "pathwidth" and len(parts) >= 3:
            out["width"], out["status"] = int(parts[1]), parts[2]
    for line in out["stderr"]:
        for tok in line.split():
            if tok.startswith("lower="):
                out["lower"] = int(tok[6:])
    return out


def _limit_memory(bytes_: int):
    def pre():
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (bytes_, bytes_))
        except Exception:
            pass
        try:
            os.nice(19)
        except Exception:
            pass
    return pre


def rulefree_refutation(m: int, edges: list[tuple[int, int]], w: int, cap: float, src_dir: Path = RULEFREE_DIR,
                        max_states: int = 100_000_000, memory_bytes: int = 8 << 30) -> dict:
    """`vsmemo -o -w F` refuting `pw <= w` on the minor, then `checkF`; both
    compiled from `src_dir` into a temporary directory. Returns the outcome:
    `verified`, `unknown` (vsmemo gave no answer in the budget), `sat`
    (vsmemo found a layout of width `w`: the claim is false), `failed`
    (checkF rejected the family) or `skipped`."""
    vs, cf = src_dir / "vsmemo.c", src_dir / "checkF.c"
    if not (vs.exists() and cf.exists()) or m > 192:
        return {"rulefree": "skipped", "reason": "sources missing or m > 192"}
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for src, exe in ((vs, "vsmemo"), (cf, "checkF")):
            r = subprocess.run(["gcc", "-O2", "-o", str(tmp / exe), str(src)], capture_output=True, text=True)
            if r.returncode != 0:
                return {"rulefree": "skipped", "reason": f"gcc failed on {src.name}: {r.stderr[-200:]}"}
        edge_file = tmp / "edges.txt"
        edge_file.write_text(f"{m} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges))
        fam = tmp / "F.bin"
        try:
            r = subprocess.run([str(tmp / "vsmemo"), str(edge_file), str(w), "-o", "-t", f"{cap:g}", "-m", str(max_states),
                                "-w", str(fam)], capture_output=True, text=True, timeout=cap + 120,
                               preexec_fn=_limit_memory(memory_bytes))
        except subprocess.TimeoutExpired:
            return {"rulefree": "unknown", "reason": "vsmemo timed out", "rulefree_seconds": time.monotonic() - t0}
        first = (r.stdout.strip().splitlines() or [""])[0]
        if r.returncode != 0 and not first.startswith("UNSAT"):
            return {"rulefree": "unknown", "reason": f"vsmemo exit {r.returncode}: {first[:80]} {r.stderr[-120:]}",
                    "rulefree_seconds": time.monotonic() - t0}
        if first.startswith("SAT"):
            return {"rulefree": "sat", "reason": first[:120], "rulefree_seconds": time.monotonic() - t0}
        if not first.startswith("UNSAT"):
            return {"rulefree": "unknown", "reason": first[:120], "rulefree_seconds": time.monotonic() - t0}
        if not fam.exists():
            return {"rulefree": "unknown", "reason": "no family written", "rulefree_seconds": time.monotonic() - t0}
        sets = fam.stat().st_size // ((m + 7) // 8)
        c = subprocess.run([str(tmp / "checkF"), str(edge_file), str(w), str(fam)], capture_output=True, text=True,
                           timeout=cap + 120)
        ok = c.stdout.strip().startswith("VERIFIED")
        return {"rulefree": "verified" if ok else "failed", "reason": c.stdout.strip()[:120], "rulefree_sets": sets,
                "rulefree_seconds": time.monotonic() - t0}


def check_minor(instance_path: Path, certificate_path: Path, c_cap: float = 10.0, c_binary: Path = DEFAULT_C_BINARY,
                rulefree: bool = True, rulefree_cap: float = 300.0, rulefree_max_m: int = 80) -> dict:
    """Every check, as a dict; `verdict` is `verified` when the replay, the
    hash and the C check pass. The rule-free outcome is recorded beside."""
    result: dict = {"instance": str(instance_path), "certificate": str(certificate_path), "checks": [], "verdict": "",
                    "replay_ok": False, "hash_ok": False, "c_ok": None, "rulefree": "skipped"}
    cert = json.loads(Path(certificate_path).read_text())

    def check(label: str, ok: bool, detail: str = "") -> bool:
        result["checks"].append({"check": label, "ok": bool(ok), "detail": detail})
        return bool(ok)

    instance_path = Path(instance_path)
    if instance_path.suffix == ".txt":
        name, n, edges = read_edges(instance_path)
        G = graph_from_edges(n, edges)
        ok = check("instance is an edge list", True, f"{n} vertices, {len(edges)} edges")
    else:
        name, rows = read_mosp(instance_path)
        n = len(rows)
        G = graph_from_rows(rows)
        digest_rows = rows_sha256(rows)
        ok = check("instance rows SHA-256 matches", cert.get("matrix_sha256") in (None, digest_rows),
                   f"{digest_rows[:16]}… vs {str(cert.get('matrix_sha256'))[:16]}…")
    result.update({"instance_name": name, "n": n})
    ok &= check("format is obstruction-minor-1", cert.get("format") == "obstruction-minor-1", str(cert.get("format")))
    ok &= check("instance size matches", n == int(cert["n"]), f"file n={n}, certificate n={cert['n']}")
    g_hash = edges_sha256(n, graph_edges(G))
    ok &= check("graph edge-list SHA-256 matches", cert.get("graph_sha256") in (None, g_hash),
                f"{g_hash[:16]}… vs {str(cert.get('graph_sha256'))[:16]}…")
    if not ok:
        result["verdict"] = "rejected"
        return result
    deleted: set[int] = set()
    try:
        H, branch = replay_minor(G, cert["sequence"], deleted)
        ok &= check("every pair is an edge of the current graph at its step", True,
                    f"{len(cert['sequence'])} steps, {len(deleted)} isolated deletions")
        result["replay_ok"] = True
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        ok &= check("every pair is an edge of the current graph at its step", False, str(exc))
        result["verdict"] = "rejected"
        return result
    try:
        Q = quotient_by_branch_sets(G, branch, deleted)
        ok &= check("quotient by branch sets equals the replayed minor", Q == H)
    except ValueError as exc:
        ok &= check("quotient by branch sets equals the replayed minor", False, str(exc))
        result["verdict"] = "rejected"
        return result
    labels, edges = relabel(H)
    m = len(labels)
    h = edges_sha256(m, edges)
    result.update({"m": m, "minor_edges": len(edges), "minor_sha256": h})
    ok &= check("minor size matches", m == int(cert["m"]), f"replayed m={m}, certificate m={cert['m']}")
    ok &= check("minor edge hash matches the certificate", h == cert.get("minor_sha256"),
                f"{h[:16]}… vs {str(cert.get('minor_sha256'))[:16]}…")
    result["hash_ok"] = h == cert.get("minor_sha256") and m == int(cert["m"])
    claim = cert.get("pathwidth_proved")
    result["floor_claimed"] = cert.get("floor")
    ok &= check("the claim is a pathwidth", claim is not None and int(claim) >= 0 and int(cert.get("floor", -1)) == int(claim) + 1,
                f"pathwidth >= {claim}, floor {cert.get('floor')}")
    if not ok:
        result["verdict"] = "rejected"
        return result
    claim = int(claim)
    if not Path(c_binary).exists():
        ok &= check("C program present", False, str(c_binary))
        result["verdict"] = "rejected"
        return result
    c = run_pathwidth_c(graph6_encode(m, edges), c_cap, Path(c_binary))
    result.update({"c_width": c["width"], "c_status": c["status"], "c_lower": c["lower"], "c_seconds": c["seconds"]})
    if c["status"] in ("refutation", "bound", "minor") and c["width"] is not None:
        proved = c["width"]
    else:
        proved = c["lower"] if c["lower"] is not None else -1
    c_ok = proved >= claim
    result["c_ok"] = c_ok
    ok &= check(f"the C program re-proves pathwidth(minor) >= {claim} within {c_cap:g} s", c_ok,
                f"width {c['width']} status {c['status']} lower {c['lower']} ({c['seconds']:.2f} s)")
    if c["status"] in ("refutation", "bound") and c["width"] is not None and c["width"] < claim:
        check("the C program's exact width contradicts the claim", False,
              f"exact {c['width']} < claim {claim}: the certificate is wrong")
        result["contradiction"] = True
    if rulefree and m <= rulefree_max_m:
        rf = rulefree_refutation(m, edges, claim - 1, rulefree_cap)
        result.update(rf)
        check(f"rule-free refutation of pathwidth <= {claim - 1} (vsmemo + checkF)", rf["rulefree"] in ("verified", "unknown", "skipped"),
              f"{rf['rulefree']}: {rf.get('reason', '')} ({rf.get('rulefree_seconds', 0):.1f} s)")
        if rf["rulefree"] in ("sat", "failed"):
            ok = False
            result["contradiction"] = True
    result["verdict"] = "verified" if ok else "rejected"
    if ok:
        result["proves"] = {"pathwidth_at_least": claim, "mosp_at_least": claim + 1,
                            "statement": f"the {m}-vertex contraction minor has pathwidth >= {claim}, so pathwidth(G) >= {claim} "
                                         f"and MOSP >= {claim + 1}", "theorems": MINOR_THEOREMS}
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    ce = sub.add_parser("check-expansion", help="check a family E certificate: CNF hash, DRAT proof, the bound")
    ce.add_argument("instance")
    ce.add_argument("certificate")
    ce.add_argument("--drat-trim", default=str(DEFAULT_DRAT_TRIM))
    ce.add_argument("--timeout", type=float, default=None)
    ce.add_argument("--json", action="store_true")
    cm = sub.add_parser("check-minor", help="check a family M certificate: replay, quotient hash, the C program, rule-free")
    cm.add_argument("instance")
    cm.add_argument("certificate")
    cm.add_argument("--c-binary", default=str(DEFAULT_C_BINARY))
    cm.add_argument("--c-cap", type=float, default=10.0)
    cm.add_argument("--no-rulefree", action="store_true")
    cm.add_argument("--rulefree-cap", type=float, default=300.0)
    cm.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.command == "check-minor":
        res = check_minor(Path(args.instance), Path(args.certificate), args.c_cap, Path(args.c_binary),
                          not args.no_rulefree, args.rulefree_cap)
        if args.json:
            print(json.dumps(res, indent=1))
        else:
            print(f"instance {res.get('instance_name')!r} (n = {res.get('n')}), minor m = {res.get('m')}, "
                  f"claimed floor {res.get('floor_claimed')}")
            for c in res["checks"]:
                print(f"  [{'ok' if c['ok'] else 'FAIL'}] {c['check']}: {c['detail']}")
            print(f"verdict: {res['verdict']} (rule-free: {res.get('rulefree')})")
            if res["verdict"] == "verified":
                print(f"proves: {res['proves']['statement']}")
                print(f"rests on: {res['proves']['theorems']}")
        return 0 if res["verdict"] == "verified" else 1
    if args.command == "check-expansion":
        res = check_expansion(Path(args.instance), Path(args.certificate), Path(args.drat_trim), args.timeout)
        if args.json:
            print(json.dumps(res, indent=1))
        else:
            print(f"instance {res.get('instance_name')!r} (n = {res.get('n')}), certificate (t, b) = ({res.get('t')}, {res.get('b')})")
            for c in res["checks"]:
                print(f"  [{'ok' if c['ok'] else 'FAIL'}] {c['check']}: {c['detail']}")
            print(f"verdict: {res['verdict']}")
            if res["verdict"] == "verified":
                p = res["proves"]
                print(f"proves: {p['statement']}")
                print(f"rests on: {p['theorems']}")
        return 0 if res["verdict"] == "verified" else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
