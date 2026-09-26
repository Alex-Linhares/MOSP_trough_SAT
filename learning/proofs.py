"""Can every certified optimum at n <= 40 carry a refutation a third party can check?

`reports/ml_nature_plan_2.md` §2.1(b), loop0003 item 03. The corpus's optima
are certified by refutations of `optimum - 1`, almost all of them from the
complete customer search, whose refutations rest on its dominance rules being
sound and leave no proof object behind (§15 found a false answer in exactly
such a rule). This module re-refutes `optimum - 1` through the direct SAT
encoding with proof logging on, checks every proof with an independent
checker, and keeps the proof.

For each certified corpus instance with at most `--max-customers` customers:

1. apply the two reductions `satisfiability.mosp_solver.decide_mosp` applies
   (component decomposition, then pattern dominance within each component),
   recording both in the certificate so the reduced instance -- and from it
   the CNF -- regenerates from the original file;
2. encode "MOSP <= optimum - 1?" with `encode_mosp_decision` and solve it with
   CaDiCaL 1.9.5 through pysat, `with_proof=True`, under a **conflict budget**
   (`--conflicts`, recorded in the certificate; conflicts, not seconds, so the
   censoring is reproducible) inside a child process the worker kills at a
   wall-clock deadline as a safety net -- pysat's `interrupt()` raises
   `NotImplementedError` for CaDiCaL, so a timer cannot stop it; the CNF is
   written in DIMACS and the proof, binary DRAT, is read back from the
   solver's trace file;
3. check the proof against the CNF with drat-trim (`tools/drat-trim/`, built
   from Marijn Heule's public source; `-std=gnu99` because the upstream
   Makefile's `-std=c99` hides `getc_unlocked`);
4. store the proof gzip-compressed under `learning/data/proofs/` (git-ignored)
   beside a JSON certificate, and append one row to the committed table
   `learning/data/proofs.csv`: instance, k, preprocessing, CNF size and hash,
   proof hash and size, solve and check seconds, the checker's verdict.

A refuted component refutes the whole instance (`decide_mosp`'s argument), so
one UNSAT component's proof is the instance's certificate; the component is
named. An instance whose every component is satisfiable at `optimum - 1`
would mean the stored optimum is wrong, and is recorded as `sat`, never
silently. A call that exhausts its conflict budget is `budget`, one the wall
deadline kills is `timeout`: both censored, neither missing.

**A pysat note that cost an hour.** `Solver.get_proof()` returns a truncated
proof for CaDiCaL: the trace is written through a C stdio buffer pysat never
flushes before reading, so the text proof ends mid-clause and drat-trim says
"no conflict" even on a 30-variable pigeonhole formula. Flushing every C
stream (`libc.fflush(NULL)`) before reading the trace file gives the complete
proof, which verifies. `_read_proof` does exactly that.

Nothing here touches `_lower_bound`, changes a solver default, or writes to
`solutions/`. The SAT path's answers are compared with the stored optimum and
with nothing else; a `sat` row is a finding, not a correction.

Usage:
    python -m learning.proofs run --max-customers 40 --workers 16 --conflicts 1000000 --deadline 180
    python -m learning.proofs tables --out reports/proof_tables.md
    python -m learning.proofs check <proof-stem>       # re-check one stored proof
    python -m pytest tests/test_proofs.py -q
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import json
import multiprocessing
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from learning.dataset import DATA_DIR, DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR
from mosp.instance import MOSPInstance

PROOF_DIR = DATA_DIR / "proofs"
"""Where the compressed proofs and their certificates live; git-ignored."""

DEFAULT_TABLE = DATA_DIR / "proofs.csv"
"""The committed table: one row per (instance, k), no proof bytes."""

DRAT_TRIM = Path("tools/drat-trim/drat-trim")
BACKEND = "cadical195"
SIZE_BANDS = ((0, 10), (11, 20), (21, 30), (31, 40), (41, 60), (61, 200))

TABLE_COLUMNS = [
    "instance_name", "source_file", "collection", "n_customers", "n_patterns",
    "optimum", "k", "status", "verdict",
    "components", "refuted_component", "component_customers",
    "component_patterns", "dominated_removed", "reduced_customers",
    "reduced_patterns", "cnf_variables", "cnf_clauses", "cnf_sha256",
    "proof_sha256", "proof_bytes", "proof_gz_bytes", "proof_lemmas",
    "solve_seconds", "check_seconds", "conflict_budget", "conflicts",
    "decisions", "deadline_seconds", "backend",
    "checker", "proof_stem",
]


# --------------------------------------------------------------------------- #
# The checker
# --------------------------------------------------------------------------- #

def drat_trim_available(binary: Path = DRAT_TRIM) -> bool:
    return binary.exists()


def check_proof(cnf_path: Path, proof_path: Path, binary: Path = DRAT_TRIM,
                timeout: float | None = None) -> tuple[str, float, str]:
    """Run drat-trim; return `(verdict, seconds, last lines of output)`.

    `verdict` is `verified`, `not_verified`, `check_timeout` or `checker_error`.
    drat-trim accepts text and binary DRAT and detects which; the proofs here
    are binary as CaDiCaL wrote them.
    """
    started = time.monotonic()
    try:
        out = subprocess.run(
            [str(binary), str(cnf_path), str(proof_path)],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return "check_timeout", round(time.monotonic() - started, 3), ""
    except OSError as exc:
        return "checker_error", round(time.monotonic() - started, 3), str(exc)
    seconds = round(time.monotonic() - started, 3)
    text = out.stdout + out.stderr
    if "s VERIFIED" in text:
        return "verified", seconds, text[-400:]
    if "s NOT VERIFIED" in text or "ERROR" in text:
        return "not_verified", seconds, text[-400:]
    return "checker_error", seconds, text[-400:]


# --------------------------------------------------------------------------- #
# One refutation with a proof
# --------------------------------------------------------------------------- #

@dataclass
class ProofCertificate:
    """Everything a third party needs to rebuild the CNF and check the proof."""

    instance_name: str
    source_file: str
    n_customers: int
    n_patterns: int
    optimum: int
    k: int
    status: str
    """`unsat` (proof stored), `sat` (stored optimum contradicted), `budget`
    (conflict budget exhausted), `timeout` (killed at the wall deadline)."""
    components: int
    refuted_component: int | None
    component_customers: list[int] = field(default_factory=list)
    """Original customer indices of the refuted component, in its row order."""
    component_patterns: list[int] = field(default_factory=list)
    """Original pattern indices of the refuted component, in its column order."""
    dominance_kept: list[int] = field(default_factory=list)
    """Component-local pattern indices surviving dominance, in reduced order."""
    dominance_dependents: dict[int, list[int]] = field(default_factory=dict)
    """Component-local survivor -> the dominated patterns dropped beside it."""
    cnf_variables: int = 0
    cnf_clauses: int = 0
    cnf_sha256: str = ""
    proof_sha256: str = ""
    proof_bytes: int = 0
    proof_gz_bytes: int = 0
    proof_lemmas: int = 0
    solve_seconds: float = 0.0
    check_seconds: float = 0.0
    verdict: str = ""
    conflict_budget: int | None = None
    conflicts: int = 0
    decisions: int = 0
    deadline_seconds: float | None = None
    backend: str = BACKEND
    checker: str = ""
    encoder: str = "satisfiability.mosp_encoding.encode_mosp_decision"
    python: str = platform.python_version()
    pysat: str = ""
    proof_stem: str = ""


def _fflush_all() -> None:
    """Flush every C stdio stream: CaDiCaL's trace buffer is one of them."""
    ctypes.CDLL(None).fflush(None)


def _read_proof(solver) -> bytes:
    """The complete binary DRAT trace of a pysat CaDiCaL solver.

    Reads the trace file pysat handed CaDiCaL after flushing the C side; see
    the module docstring for why `get_proof()` is not used.
    """
    _fflush_all()
    inner = solver.solver
    inner.prfile.seek(0)
    return inner.prfile.read()


def count_lemmas(proof: bytes) -> int:
    """Number of addition records (`a`) in a binary DRAT proof."""
    count = 0
    i = 0
    length = len(proof)
    while i < length:
        tag = proof[i]
        i += 1
        if tag == 0x61:          # 'a'
            count += 1
        # skip the varint literals up to and including the 0 terminator
        while i < length:
            byte = proof[i]
            i += 1
            if byte == 0:
                break
            while byte & 0x80 and i < length:
                byte = proof[i]
                i += 1
    return count


def cnf_dimacs(cnf) -> bytes:
    """A DIMACS rendering of a pysat CNF, deterministic in the clause order."""
    lines = [f"p cnf {cnf.nv} {len(cnf.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in cnf.clauses)
    return ("\n".join(lines) + "\n").encode()


def _stem(name: str, k: int) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")
    return f"{safe}__k{k}"


def solve_with_proof(
    instance: MOSPInstance,
    optimum: int,
    source_file: str = "",
    conflicts: int | None = None,
    proof_dir: Path = PROOF_DIR,
    backend: str = BACKEND,
) -> ProofCertificate:
    """Refute `optimum - 1` through the SAT path, writing the proof but not checking it.

    Mirrors `decide_mosp`: decompose, then drop dominated patterns within each
    component, encode, solve. Stops at the first component that is UNSAT, whose
    proof refutes the instance. Writes `<stem>.drat.gz`, `<stem>.cnf.gz` and
    `<stem>.json` under `proof_dir` when a proof exists; `check_certificate`
    fills in the verdict and removes the CNF.
    """
    import pysat
    from pysat.solvers import Solver

    from mosp.preprocess import components, remove_dominated_patterns
    from satisfiability.mosp_encoding import encode_mosp_decision

    k = optimum - 1
    cert = ProofCertificate(
        instance_name=instance.name, source_file=source_file,
        n_customers=instance.n_customers, n_patterns=instance.n_patterns,
        optimum=optimum, k=k, status="sat", components=0,
        refuted_component=None, conflict_budget=conflicts,
        backend=backend, pysat=pysat.__version__,
        proof_stem=_stem(instance.name, k),
    )
    parts, _free = components(instance)
    cert.components = len(parts)
    if not parts:
        return cert         # an empty instance is satisfiable at any k

    proof_dir.mkdir(parents=True, exist_ok=True)
    budget_left = conflicts

    for index, part in enumerate(parts):
        reduction = remove_dominated_patterns(part.instance)
        reduced = reduction.instance
        cnf, _pool, _m = encode_mosp_decision(reduced, k)
        dimacs = cnf_dimacs(cnf)

        solver = Solver(name=backend, bootstrap_with=cnf.clauses, with_proof=True)
        started = time.monotonic()
        try:
            if budget_left is not None:
                solver.conf_budget(budget_left)
                answer = solver.solve_limited()
            else:
                answer = solver.solve()
            solve_seconds = round(time.monotonic() - started, 3)
            stats = solver.accum_stats() or {}
            proof = _read_proof(solver) if answer is False else b""
        finally:
            solver.delete()

        cert.solve_seconds = round(cert.solve_seconds + solve_seconds, 3)
        cert.conflicts += int(stats.get("conflicts", 0))
        cert.decisions += int(stats.get("decisions", 0))
        if budget_left is not None:
            budget_left = max(0, budget_left - int(stats.get("conflicts", 0)))
        if answer is None:
            cert.status = "budget"
            return cert
        if answer is True:
            continue        # this component fits in k; the next may not

        # UNSAT: this component's proof is the instance's certificate.
        cert.status = "unsat"
        cert.refuted_component = index
        cert.component_customers = list(part.customers)
        cert.component_patterns = list(part.patterns)
        cert.dominance_kept = list(reduction.kept)
        cert.dominance_dependents = {int(a): list(b) for a, b in reduction.dependents.items()}
        cert.cnf_variables = cnf.nv
        cert.cnf_clauses = len(cnf.clauses)
        cert.cnf_sha256 = hashlib.sha256(dimacs).hexdigest()
        cert.proof_sha256 = hashlib.sha256(proof).hexdigest()
        cert.proof_bytes = len(proof)
        cert.proof_lemmas = count_lemmas(proof)

        gz_path = proof_dir / f"{cert.proof_stem}.drat.gz"
        with gzip.open(gz_path, "wb", compresslevel=6) as fh:
            fh.write(proof)
        cert.proof_gz_bytes = gz_path.stat().st_size
        with gzip.open(proof_dir / f"{cert.proof_stem}.cnf.gz", "wb", compresslevel=6) as fh:
            fh.write(dimacs)
        _write_certificate(cert, proof_dir)
        return cert

    return cert         # every component satisfiable: the stored optimum is contradicted


def _write_certificate(cert: ProofCertificate, proof_dir: Path) -> None:
    (proof_dir / f"{cert.proof_stem}.json").write_text(
        json.dumps(asdict(cert), indent=1, sort_keys=True))


def check_certificate(cert: ProofCertificate, proof_dir: Path = PROOF_DIR,
                      checker: Path = DRAT_TRIM, timeout: float | None = None,
                      keep_cnf: bool = False) -> ProofCertificate:
    """Run drat-trim on a stored proof; record verdict and seconds in the certificate.

    The CNF written by `solve_with_proof` is removed afterwards unless
    `keep_cnf`: it regenerates from the certificate (`rebuild_cnf`).
    """
    if cert.status != "unsat":
        return cert
    cert.checker = str(checker)
    cnf_gz = proof_dir / f"{cert.proof_stem}.cnf.gz"
    with tempfile.TemporaryDirectory() as tmp:
        cnf_path = Path(tmp) / "formula.cnf"
        proof_path = Path(tmp) / "proof.drat"
        with gzip.open(cnf_gz, "rb") as fh:
            cnf_path.write_bytes(fh.read())
        with gzip.open(proof_dir / f"{cert.proof_stem}.drat.gz", "rb") as fh:
            proof_path.write_bytes(fh.read())
        verdict, seconds, _tail = check_proof(cnf_path, proof_path, checker, timeout)
    cert.verdict = verdict
    cert.check_seconds = seconds
    if not keep_cnf:
        cnf_gz.unlink(missing_ok=True)
    _write_certificate(cert, proof_dir)
    return cert


def check_timeout_for(solve_seconds: float, floor: float = 30.0, factor: float = 3.0) -> float:
    """The checker's wall budget: backward checking is usually cheaper than
    solving but not by a guaranteed factor; measured 0.3-3x on this corpus."""
    return max(floor, factor * solve_seconds)


def refute_with_proof(
    instance: MOSPInstance,
    optimum: int,
    source_file: str = "",
    deadline_seconds: float | None = None,
    proof_dir: Path = PROOF_DIR,
    backend: str = BACKEND,
    checker: Path = DRAT_TRIM,
    keep_cnf: bool = False,
    conflicts: int | None = None,
) -> ProofCertificate:
    """Solve and check in-process: `solve_with_proof` then `check_certificate`.

    `deadline_seconds` bounds only the checker here (CaDiCaL cannot be
    interrupted through pysat); the batch enforces its wall deadline by
    running `solve_with_proof` in a child it can kill (`_job`).
    """
    cert = solve_with_proof(instance, optimum, source_file, conflicts, proof_dir, backend)
    cert.deadline_seconds = deadline_seconds
    return check_certificate(cert, proof_dir, checker, deadline_seconds, keep_cnf)


def rebuild_cnf(certificate: dict, instance: MOSPInstance) -> bytes:
    """Regenerate the DIMACS of a certificate from the original instance.

    A third party who distrusts the stored CNF hash can compare this against
    `cnf_sha256`; the preprocessing is replayed from the recorded indices, not
    recomputed, so the check does not depend on `mosp.preprocess`.
    """
    from satisfiability.mosp_encoding import encode_mosp_decision

    rows = certificate["component_customers"]
    cols = certificate["component_patterns"]
    sub = instance.matrix[np.ix_(rows, cols)]
    kept = certificate["dominance_kept"]
    reduced = MOSPInstance.from_matrix(sub[:, kept], name=certificate["instance_name"])
    cnf, _pool, _m = encode_mosp_decision(reduced, int(certificate["k"]))
    return cnf_dimacs(cnf)


def recheck(stem: str, instance: MOSPInstance, proof_dir: Path = PROOF_DIR,
            checker: Path = DRAT_TRIM, timeout: float | None = None) -> tuple[str, float, bool]:
    """Re-check a stored proof from scratch: rebuild the CNF, decompress, run drat-trim.

    Returns `(verdict, check seconds, cnf hash matches certificate)`.
    """
    cert = json.loads((proof_dir / f"{stem}.json").read_text())
    dimacs = rebuild_cnf(cert, instance)
    hash_ok = hashlib.sha256(dimacs).hexdigest() == cert["cnf_sha256"]
    with gzip.open(proof_dir / f"{stem}.drat.gz", "rb") as fh:
        proof = fh.read()
    with tempfile.TemporaryDirectory() as tmp:
        cnf_path = Path(tmp) / "formula.cnf"
        proof_path = Path(tmp) / "proof.drat"
        cnf_path.write_bytes(dimacs)
        proof_path.write_bytes(proof)
        verdict, seconds, _ = check_proof(cnf_path, proof_path, checker, timeout)
    return verdict, seconds, hash_ok


# --------------------------------------------------------------------------- #
# The batch
# --------------------------------------------------------------------------- #

def _row(cert: ProofCertificate, collection: str) -> dict:
    return {
        "instance_name": cert.instance_name, "source_file": cert.source_file,
        "collection": collection, "n_customers": cert.n_customers,
        "n_patterns": cert.n_patterns, "optimum": cert.optimum, "k": cert.k,
        "status": cert.status, "verdict": cert.verdict,
        "components": cert.components, "refuted_component": cert.refuted_component,
        "component_customers": len(cert.component_customers),
        "component_patterns": len(cert.component_patterns),
        "dominated_removed": sum(len(v) for v in cert.dominance_dependents.values()),
        "reduced_customers": len(cert.component_customers),
        "reduced_patterns": len(cert.dominance_kept),
        "cnf_variables": cert.cnf_variables, "cnf_clauses": cert.cnf_clauses,
        "cnf_sha256": cert.cnf_sha256, "proof_sha256": cert.proof_sha256,
        "proof_bytes": cert.proof_bytes, "proof_gz_bytes": cert.proof_gz_bytes,
        "proof_lemmas": cert.proof_lemmas, "solve_seconds": cert.solve_seconds,
        "check_seconds": cert.check_seconds, "conflict_budget": cert.conflict_budget,
        "conflicts": cert.conflicts, "decisions": cert.decisions,
        "deadline_seconds": cert.deadline_seconds,
        "backend": cert.backend, "checker": cert.checker, "proof_stem": cert.proof_stem,
    }


def _child_solve(job: dict) -> ProofCertificate:
    """Entry point of the solve child (`python -m learning.proofs one`), reading a job from stdin."""
    instance = MOSPInstance(matrix=np.array(job["matrix"], dtype=np.int8),
                            n_customers=len(job["matrix"]), n_patterns=len(job["matrix"][0]),
                            name=job["name"])
    return solve_with_proof(instance, job["optimum"], job["source_file"],
                            job["conflicts"], Path(job["proof_dir"]))


def _job(args) -> dict:
    matrix, name, source_file, collection, optimum, deadline, proof_dir, conflicts = args
    job = {"matrix": matrix, "name": name, "source_file": source_file,
           "optimum": optimum, "conflicts": conflicts, "proof_dir": proof_dir}
    base = ProofCertificate(instance_name=name, source_file=source_file,
                            n_customers=len(matrix), n_patterns=len(matrix[0]),
                            optimum=optimum, k=optimum - 1, status="error",
                            components=0, refuted_component=None,
                            conflict_budget=conflicts, deadline_seconds=deadline,
                            proof_stem=_stem(name, optimum - 1))
    started = time.monotonic()
    try:
        out = subprocess.run(
            [sys.executable, "-m", "learning.proofs", "one"],
            input=json.dumps(job), capture_output=True, text=True,
            timeout=deadline, check=False, cwd=str(Path(__file__).resolve().parent.parent),
        )
    except subprocess.TimeoutExpired:
        base.status = "timeout"
        base.solve_seconds = round(time.monotonic() - started, 3)
        # a killed child may have left a partial trace; nothing of it is kept
        for suffix in (".drat.gz", ".cnf.gz", ".json"):
            (Path(proof_dir) / f"{base.proof_stem}{suffix}").unlink(missing_ok=True)
        return _row(base, collection)
    if out.returncode != 0 or not out.stdout.strip():
        base.verdict = ("child failed: " + (out.stderr.strip().splitlines() or ["no output"])[-1])[:200]
        return _row(base, collection)
    cert = ProofCertificate(**json.loads(out.stdout.strip().splitlines()[-1]))
    cert.deadline_seconds = deadline
    try:
        cert = check_certificate(cert, Path(proof_dir), DRAT_TRIM,
                                 check_timeout_for(cert.solve_seconds))
    except Exception as exc:  # noqa: BLE001 - one bad instance must not kill the batch
        cert.verdict = "checker_error: " + f"{type(exc).__name__}: {exc}"[:180]
    return _row(cert, collection)


def targets(max_customers: int, instance_dir: Path = DEFAULT_INSTANCE_DIR,
            solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
            limit: int | None = None) -> list[tuple]:
    """Every certified corpus instance at or below `max_customers`, as job tuples."""
    from learning.node_counts import certified_targets

    return certified_targets(instance_dir, solutions_dir, max_customers, limit)


def _done_keys(table: Path) -> set[tuple[str, str]]:
    if not table.exists():
        return set()
    frame = pd.read_csv(table, usecols=["instance_name", "source_file", "status"])
    # a timeout is re-run only when asked (see --retry-timeouts); everything
    # else is final
    return set(zip(frame["instance_name"].astype(str), frame["source_file"].astype(str)))


def run(jobs: list[tuple], deadline: float, workers: int, table: Path = DEFAULT_TABLE,
        proof_dir: Path = PROOF_DIR, retry_timeouts: bool = False,
        wall_seconds: float | None = None, conflicts: int | None = 1_000_000,
        log=print) -> pd.DataFrame:
    """Resumable batch: rows already in `table` are skipped, new rows appended as they finish.

    `wall_seconds` stops dispatching new work after that much wall clock; rows
    in flight finish. The table is the resume point, so a stopped run is
    picked up by running the same command again.
    """
    table.parent.mkdir(parents=True, exist_ok=True)
    done = _done_keys(table)
    if retry_timeouts and table.exists():
        frame = pd.read_csv(table)
        keep = frame[~frame["status"].isin(["timeout", "budget"])]
        keep.to_csv(table, index=False)
        done = set(zip(keep["instance_name"].astype(str), keep["source_file"].astype(str)))
    todo = [job[:5] + (deadline, str(proof_dir), conflicts) for job in jobs
            if (job[1], job[2]) not in done]
    # largest first so the slow tail is not left to the end of the pool
    todo.sort(key=lambda j: (-len(j[0]), -len(j[0][0])))
    log(f"proofs: {len(jobs)} targets, {len(done)} already in table, {len(todo)} to run "
        f"on {workers} workers, conflict budget {conflicts}, wall deadline {deadline}s")
    if not todo:
        return pd.read_csv(table) if table.exists() else pd.DataFrame(columns=TABLE_COLUMNS)

    write_header = not table.exists() or table.stat().st_size == 0
    started = time.monotonic()
    written = 0
    with table.open("a", newline="") as fh:
        def emit(row: dict) -> None:
            nonlocal write_header, written
            pd.DataFrame([row], columns=TABLE_COLUMNS).to_csv(fh, header=write_header, index=False)
            fh.flush()
            write_header = False
            written += 1
            if written % 200 == 0:
                log(f"  {written}/{len(todo)} rows, {time.monotonic() - started:.0f}s")

        if workers <= 1:
            for job in todo:
                emit(_job(job))
                if wall_seconds is not None and time.monotonic() - started > wall_seconds:
                    log("  wall budget reached; stopping (resume with the same command)")
                    break
        else:
            ctx = multiprocessing.get_context("spawn")
            with ctx.Pool(workers) as pool:
                pending = iter(todo)
                in_flight = {}
                for job in pending:
                    in_flight[pool.apply_async(_job, (job,))] = job
                    if len(in_flight) >= workers * 2:
                        break
                while in_flight:
                    ready = [r for r in in_flight if r.ready()]
                    if not ready:
                        time.sleep(0.05)
                        continue
                    for r in ready:
                        in_flight.pop(r)
                        emit(r.get())
                        stop = wall_seconds is not None and time.monotonic() - started > wall_seconds
                        if not stop:
                            nxt = next(pending, None)
                            if nxt is not None:
                                in_flight[pool.apply_async(_job, (nxt,))] = nxt
                if wall_seconds is not None and time.monotonic() - started > wall_seconds:
                    log("  wall budget reached; stopping (resume with the same command)")
    log(f"proofs: wrote {written} rows in {time.monotonic() - started:.0f}s")
    return pd.read_csv(table)


def backfill(table: Path, source: Path) -> int:
    """Append to `table` the rows of `source` whose instance it lacks; return how many.

    The second pass (`--retry-timeouts`) drops the censored rows before it
    re-runs them, and a wall cap can stop it before every one has run; this
    restores the first pass's censored row for any instance left without one,
    so the table has exactly one row per target, each stating its budget.
    """
    have = pd.read_csv(table)
    src = pd.read_csv(source)
    keys = set(zip(have["instance_name"].astype(str), have["source_file"].astype(str)))
    missing = src[[(a, b) not in keys for a, b in zip(src["instance_name"].astype(str),
                                                       src["source_file"].astype(str))]]
    if not missing.empty:
        pd.concat([have, missing[have.columns]], ignore_index=True).to_csv(table, index=False)
    return len(missing)


# --------------------------------------------------------------------------- #
# Tables
# --------------------------------------------------------------------------- #

def _band(n: int) -> str:
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return f"{lo}–{hi}" if lo else f"≤{hi}"
    return f">{SIZE_BANDS[-1][1]}"


def summarise(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """The tables §17 prints: certification by band, cost by n, the tail."""
    frame = frame.copy()
    frame["band"] = frame["n_customers"].map(_band)
    frame["checked"] = (frame["status"] == "unsat") & (frame["verdict"] == "verified")
    frame["unsat_unchecked"] = ((frame["status"] == "unsat") & ~frame["checked"]).astype(int)
    order = [f"{lo}–{hi}" if lo else f"≤{hi}" for lo, hi in SIZE_BANDS]

    def by(group_col):
        g = frame.groupby(group_col, observed=True)
        out = pd.DataFrame({
            "instances": g.size(),
            "checked": g["checked"].sum(),
            "unsat_unchecked": g["unsat_unchecked"].sum(),
            "censored": g["status"].apply(lambda s: int(s.isin(["timeout", "budget"]).sum())),
            "sat": g["status"].apply(lambda s: int((s == "sat").sum())),
            "error": g["status"].apply(lambda s: int((s == "error").sum())),
        })
        out["checked_%"] = (100 * out["checked"] / out["instances"]).round(1)
        ok = frame[frame["checked"]].groupby(group_col, observed=True)
        out["solve_s_med"] = ok["solve_seconds"].median().round(3)
        out["solve_s_p90"] = ok["solve_seconds"].quantile(0.9).round(2)
        out["solve_s_max"] = ok["solve_seconds"].max().round(2)
        out["check_s_med"] = ok["check_seconds"].median().round(3)
        out["check_s_max"] = ok["check_seconds"].max().round(2)
        out["proof_MB_med"] = (ok["proof_bytes"].median() / 1e6).round(3)
        out["proof_MB_max"] = (ok["proof_bytes"].max() / 1e6).round(2)
        out["proof_gz_MB_sum"] = (ok["proof_gz_bytes"].sum() / 1e6).round(1)
        out["lemmas_med"] = ok["proof_lemmas"].median()
        out["core_hours"] = ((frame.groupby(group_col, observed=True)["solve_seconds"].sum()
                              + frame.groupby(group_col, observed=True)["check_seconds"].sum()) / 3600).round(2)
        return out

    by_band = by("band").reindex([b for b in order if b in set(frame["band"])])
    by_n = by("n_customers")
    by_collection = by("collection")
    by_n_afford = by_n[["instances", "checked", "censored", "checked_%", "solve_s_med",
                        "solve_s_p90", "solve_s_max", "check_s_med", "proof_MB_med",
                        "proof_MB_max", "core_hours"]]

    # the pre-processing: how often each reduction fired among the checked proofs
    ok = frame[frame["checked"]]
    prep = pd.DataFrame({
        "checked": [len(ok)],
        "decomposed (components > 1)": [int((ok["components"] > 1).sum())],
        "dominance fired": [int((ok["dominated_removed"] > 0).sum())],
        "columns removed": [int(ok["dominated_removed"].sum())],
        "cnf_clauses_med": [ok["cnf_clauses"].median()],
        "cnf_clauses_max": [ok["cnf_clauses"].max()],
    })

    # affordability: median solve seconds and proof bytes against n, with a
    # least-squares exponential fit over the n with at least ten checked
    # proofs, and the n at which the fitted median crosses one hour and one GB
    medians = ok.groupby("n_customers").agg(
        checked=("solve_seconds", "size"),
        solve_s_med=("solve_seconds", "median"),
        proof_MB_med=("proof_bytes", lambda s: s.median() / 1e6),
    )
    fitted = medians[(medians["checked"] >= 10) & (medians["solve_s_med"] > 0)]
    fit_rows = {}
    if len(fitted) >= 3:
        x = fitted.index.to_numpy(dtype=float)
        for col, unit, target, label in (
            ("solve_s_med", "seconds", 3600.0, "one hour"),
            ("proof_MB_med", "MB", 1000.0, "one GB"),
        ):
            y = np.log10(fitted[col].to_numpy(dtype=float).clip(min=1e-4))
            slope, intercept = np.polyfit(x, y, 1)
            cross = (np.log10(target) - intercept) / slope if slope > 0 else float("nan")
            fit_rows[col] = {
                "quantity": f"median {col.split('_')[0]} ({unit})",
                "n_fitted": f"{int(x.min())}–{int(x.max())}",
                "log10 per customer": round(slope, 4),
                "doubling every (customers)": round(np.log10(2) / slope, 2) if slope > 0 else float("nan"),
                f"n at {label}": round(cross, 1),
            }
    afford = pd.DataFrame(fit_rows).T if fit_rows else pd.DataFrame()

    worst = frame.sort_values("solve_seconds", ascending=False).head(15)[
        ["instance_name", "collection", "n_customers", "n_patterns", "optimum",
         "status", "verdict", "solve_seconds", "check_seconds", "proof_bytes", "proof_lemmas"]]
    totals = pd.DataFrame({
        "instances": [len(frame)], "checked": [int(frame["checked"].sum())],
        "checked_%": [round(100 * frame["checked"].mean(), 2)],
        "budget": [int((frame["status"] == "budget").sum())],
        "timeout": [int((frame["status"] == "timeout").sum())],
        "sat": [int((frame["status"] == "sat").sum())],
        "not_verified": [int((frame["verdict"] == "not_verified").sum())],
        "check_timeout": [int((frame["verdict"] == "check_timeout").sum())],
        "error": [int((frame["status"] == "error").sum())],
        "solve_core_hours": [round(frame["solve_seconds"].sum() / 3600, 2)],
        "check_core_hours": [round(frame["check_seconds"].sum() / 3600, 2)],
        "proof_GB": [round(frame["proof_bytes"].sum() / 1e9, 3)],
        "proof_gz_GB": [round(frame["proof_gz_bytes"].sum() / 1e9, 3)],
    })
    # affordability is a matter of the width k as much as of n: the same
    # cardinality constraint is harder to refute the closer k sits to m / 2
    if "k" not in frame.columns:
        frame["k"] = frame["optimum"] - 1
    frame["k_band"] = pd.cut(frame["k"], [0, 5, 10, 15, 20, 30, 200],
                             labels=["1–5", "6–10", "11–15", "16–20", "21–30", ">30"])
    by_k = by("k_band")[["instances", "checked", "censored", "checked_%", "solve_s_med",
                          "solve_s_p90", "check_s_med", "proof_MB_med", "core_hours"]]
    grid = frame.pivot_table(index="band", columns="k_band", values="checked",
                             aggfunc=lambda s: f"{int(s.sum())}/{len(s)}", observed=True)
    grid = grid.reindex([b for b in order if b in set(frame["band"])])

    # and of the number of patterns: the encoding has m² position variables
    # and a k-bounded cardinality constraint at each of m steps, so m² · k is
    # the natural size of the formula; censoring is a function of it
    frame["m_band"] = pd.cut(frame["n_patterns"], [0, 10, 20, 30, 40, 60, 10**6],
                             labels=["≤10", "11–20", "21–30", "31–40", "41–60", ">60"])
    frame["censored"] = frame["status"].isin(["budget", "timeout"])
    grid_m = frame.pivot_table(index="m_band", columns="k_band", values="censored",
                               aggfunc=lambda s: f"{int(s.sum())}/{len(s)}", observed=True)
    frame["m2k"] = frame["n_patterns"] ** 2 * frame["k"]
    edges = [0, 500, 2000, 5000, 10000, 20000, 50000, 10**9]
    labels = ["<500", "500–2k", "2k–5k", "5k–10k", "10k–20k", "20k–50k", "≥50k"]
    frame["m2k_band"] = pd.cut(frame["m2k"], edges, labels=labels)
    gsz = frame.groupby("m2k_band", observed=True)
    by_size = pd.DataFrame({
        "instances": gsz.size(),
        "checked": gsz["checked"].sum(),
        "censored": gsz["censored"].sum(),
    })
    by_size["censored_%"] = (100 * by_size["censored"] / by_size["instances"]).round(1)
    oksz = frame[frame["checked"]].groupby("m2k_band", observed=True)
    by_size["solve_s_med"] = oksz["solve_seconds"].median().round(3)
    by_size["proof_MB_med"] = (oksz["proof_bytes"].median() / 1e6).round(2)
    by_size["n_range"] = gsz["n_customers"].agg(lambda s: f"{s.min()}–{s.max()}")
    by_size["m_range"] = gsz["n_patterns"].agg(lambda s: f"{s.min()}–{s.max()}")

    tables = {"totals": totals, "by_band": by_band, "by_n": by_n_afford,
              "censored_grid_m_by_k": grid_m, "by_formula_size": by_size,
              "by_k": by_k, "checked_grid_n_by_k": grid,
              "affordability_fit": afford, "by_collection": by_collection,
              "preprocessing": prep, "slowest": worst}
    comparison = against_customer_search(frame)
    if comparison is not None:
        tables["vs_customer_search"] = comparison
    return tables


def against_customer_search(frame: pd.DataFrame,
                            node_counts: Path = DATA_DIR / "node_counts.csv") -> pd.DataFrame | None:
    """The same refutations by the complete customer search (`learning.node_counts`, `default`).

    Seconds against seconds by size band, on the instances both tables hold; a
    proof-carrying refutation is measured against the proof-free one it would
    replace. Returns None when `node_counts.csv` is absent (it is git-ignored
    and regenerates with `python -m learning.node_counts --max-customers 40`).
    """
    if not node_counts.exists() or not {"instance_name", "source_file"} <= set(frame.columns):
        return None
    cs = pd.read_csv(node_counts)
    cs = cs[cs["config"] == "default"][["instance_name", "source_file", "status", "nodes", "seconds"]]
    cs = cs.rename(columns={"status": "cs_status", "nodes": "cs_nodes", "seconds": "cs_seconds"})
    both = frame.merge(cs, on=["instance_name", "source_file"], how="inner")
    if both.empty:
        return None
    both["band"] = both["n_customers"].map(_band)
    both["sat_total_s"] = both["solve_seconds"].fillna(0) + both["check_seconds"].fillna(0)
    both["checked"] = (both["status"] == "unsat") & (both["verdict"] == "verified")
    order = [f"{lo}–{hi}" if lo else f"≤{hi}" for lo, hi in SIZE_BANDS]
    g = both.groupby("band", observed=True)
    out = pd.DataFrame({
        "instances": g.size(),
        "cs_unsat": g["cs_status"].apply(lambda s: int((s == "unsat").sum())),
        "sat_checked": g["checked"].sum(),
        "cs_s_med": g["cs_seconds"].median().round(4),
        "cs_s_max": g["cs_seconds"].max().round(3),
        "cs_nodes_med": g["cs_nodes"].median(),
        "sat_solve_s_med": g["solve_seconds"].median().round(3),
        "sat_solve+check_s_med": g["sat_total_s"].median().round(3),
        "sat_solve+check_s_sum": g["sat_total_s"].sum().round(1),
        "cs_s_sum": g["cs_seconds"].sum().round(2),
    })
    out["ratio_of_sums"] = (out["sat_solve+check_s_sum"] / out["cs_s_sum"]).round(0)
    return out.reindex([b for b in order if b in set(both["band"])])


def _markdown(title: str, table: pd.DataFrame) -> str:
    return f"### {title}\n\n{table.to_markdown()}\n\n"


def write_tables(frame: pd.DataFrame, out: Path) -> None:
    tables = summarise(frame)
    text = "# DRAT proofs at n ≤ 40 (`python -m learning.proofs tables`)\n\n"
    text += _markdown("Totals", tables["totals"])
    text += _markdown("By size band", tables["by_band"])
    text += _markdown("By n (affordability)", tables["by_n"])
    text += _markdown("By the width k = optimum − 1", tables["by_k"])
    text += _markdown("Checked / instances, size band by k band", tables["checked_grid_n_by_k"])
    text += _markdown("Censored / instances, patterns band by k band", tables["censored_grid_m_by_k"])
    text += _markdown("By formula size m² · k", tables["by_formula_size"])
    if not tables["affordability_fit"].empty:
        text += _markdown("Exponential fit of the medians against n", tables["affordability_fit"])
    if "vs_customer_search" in tables:
        text += _markdown("Against the complete customer search (`learning.node_counts`, default configuration)",
                          tables["vs_customer_search"])
    text += _markdown("By collection", tables["by_collection"])
    text += _markdown("Preprocessing among checked proofs", tables["preprocessing"])
    text += _markdown("Slowest fifteen", tables["slowest"])
    out.write_text(text)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="stage", required=True)

    p_run = sub.add_parser("run", help="re-refute with proofs; resumable")
    p_run.add_argument("--max-customers", type=int, default=40)
    p_run.add_argument("--workers", type=int, default=16)
    p_run.add_argument("--conflicts", type=int, default=1_000_000,
                       help="CaDiCaL conflict budget per instance (0 = unlimited); the reproducible censoring")
    p_run.add_argument("--deadline", type=float, default=180.0,
                       help="wall-clock seconds after which the solve child is killed (safety net)")
    p_run.add_argument("--limit", type=int, default=None)
    p_run.add_argument("--wall", type=float, default=None,
                       help="stop dispatching after this many seconds; resume with the same command")
    p_run.add_argument("--retry-timeouts", action="store_true")
    p_run.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    p_run.add_argument("--proof-dir", type=Path, default=PROOF_DIR)

    p_tab = sub.add_parser("tables", help="the §17 tables from the committed table")
    p_tab.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    p_tab.add_argument("--out", type=Path, default=Path("reports/proof_tables.md"))

    p_chk = sub.add_parser("check", help="re-check one stored proof from the original instance")
    p_chk.add_argument("stem")
    p_chk.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    p_chk.add_argument("--proof-dir", type=Path, default=PROOF_DIR)

    sub.add_parser("one", help="solve one job read as JSON from stdin (the batch's child process)")

    p_bf = sub.add_parser("backfill", help="restore rows a stopped retry pass left out, from an earlier pass's table")
    p_bf.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    p_bf.add_argument("--source", type=Path, default=DATA_DIR / "proofs_200k.csv")

    args = parser.parse_args()
    if args.stage == "one":
        cert = _child_solve(json.load(sys.stdin))
        print(json.dumps(asdict(cert)))
        return
    if args.stage == "run":
        if not drat_trim_available():
            raise SystemExit(f"{DRAT_TRIM} not found; build it: cd tools/drat-trim && "
                             "gcc drat-trim.c -std=gnu99 -O2 -o drat-trim")
        jobs = targets(args.max_customers, limit=args.limit)
        run(jobs, args.deadline, args.workers, args.table, args.proof_dir,
            args.retry_timeouts, args.wall, args.conflicts or None)
    elif args.stage == "tables":
        frame = pd.read_csv(args.table)
        write_tables(frame, args.out)
        for title, table in summarise(frame).items():
            print(f"\n## {title}\n{table.to_string()}")
        print(f"\nwrote {args.out}")
    elif args.stage == "backfill":
        added = backfill(args.table, args.source)
        print(f"backfilled {added} rows from {args.source} into {args.table}")
    elif args.stage == "check":
        frame = pd.read_csv(args.table)
        row = frame[frame["proof_stem"] == args.stem]
        if row.empty:
            raise SystemExit(f"no row with proof_stem {args.stem!r}")
        row = row.iloc[0]
        instances = MOSPInstance.from_benchmark_file(Path(row["source_file"]))
        instance = next(i for i in instances if i.name == row["instance_name"])
        verdict, seconds, hash_ok = recheck(args.stem, instance, args.proof_dir)
        print(f"{args.stem}: cnf hash {'matches' if hash_ok else 'DIFFERS'}, "
              f"drat-trim {verdict} in {seconds}s")


if __name__ == "__main__":
    main()
