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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    ce = sub.add_parser("check-expansion", help="check a family E certificate: CNF hash, DRAT proof, the bound")
    ce.add_argument("instance")
    ce.add_argument("certificate")
    ce.add_argument("--drat-trim", default=str(DEFAULT_DRAT_TRIM))
    ce.add_argument("--timeout", type=float, default=None)
    ce.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
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
