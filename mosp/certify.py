"""Tools for checking this project's optimality claims without trusting it.

An optimality claim has two halves and they are not equally checkable.

`MOSP(I) <= k` is witnessed by an ordering. Checking it means simulating that
ordering and counting open stacks, which is a few lines of code against the
instance file: no SAT solver, no encoding, nothing of ours need be trusted or
even read. `check_witness` does it, and is written to be re-implementable in any
language in an afternoon.

`MOSP(I) > k-1` is the harder half. It rests on a solver reporting the CNF
unsatisfiable, so re-running our code only reproduces our result -- including any
bug in the encoding. `export_cnf` writes the formula in DIMACS so it can be
refuted by *someone else's* solver, which narrows what has to be trusted from
"their whole pipeline" to "their encoding is faithful". Closing that last gap
needs either a proof log (see reports, shelved: the corpus would run to about a
terabyte) or the Lean formalization of the encoding.

Usage:
    python -m mosp.certify check SP2
    python -m mosp.certify export SP2 --k 18 --out sp2_k18.cnf
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Sequence

from mosp.instance import MOSPInstance


def count_open_stacks(matrix: Sequence[Sequence[int]],
                      ordering: Sequence[int]) -> int:
    """Maximum simultaneously open stacks for `ordering`, from first principles.

    Deliberately independent of the rest of this package: it takes a plain
    matrix and a plain list, and reimplements the count rather than calling
    `mosp.verify`. A checker that shares code with the solver checks less than
    it appears to.

    A customer's stack is open from the step its first required pattern is
    produced until the step its last one is, inclusive.
    """
    position = {pattern: index for index, pattern in enumerate(ordering)}

    # One pass to find each customer's opening and closing step, then a sweep
    # counting how many spans cover each step. Recomputing the span inside the
    # sweep would make this O(n*m^2) and take minutes over the whole corpus.
    opens_closes = []
    for row in matrix:
        steps = [position[p] for p, needed in enumerate(row)
                 if needed and p in position]
        if steps:
            opens_closes.append((min(steps), max(steps)))

    peak = 0
    for step in range(len(ordering)):
        open_now = sum(1 for first, last in opens_closes if first <= step <= last)
        peak = max(peak, open_now)
    return peak


def check_witness(
    instance: MOSPInstance,
    solution: dict,
) -> tuple[bool, str]:
    """Check a cached solution against its instance.

    Verifies that the ordering is a genuine permutation of the patterns and
    that simulating it yields the value claimed.

    Returns:
        (ok, message).
    """
    ordering = solution.get("ordering")
    claimed = solution.get("mosp_value")

    if ordering is None or claimed is None:
        return False, "solution is missing 'ordering' or 'mosp_value'"

    if sorted(ordering) != list(range(instance.n_patterns)):
        return False, (f"ordering is not a permutation of "
                       f"{instance.n_patterns} patterns")

    actual = count_open_stacks(instance.matrix.tolist(), ordering)
    if actual != claimed:
        return False, f"ordering achieves {actual}, but {claimed} was claimed"

    return True, f"verified: ordering achieves {actual} open stacks"


def export_cnf(
    instance: MOSPInstance,
    k: int,
    path: Path,
) -> tuple[int, int]:
    """Write the decision formula "MOSP(instance) <= k?" as DIMACS.

    The point is to let the refutation be reproduced by a solver other than
    ours. Feed the file at `k-1` to any SAT solver: UNSAT there, together with a
    witness at `k`, is the optimality claim.

    Returns:
        (n_variables, n_clauses).
    """
    from satisfiability.mosp_encoding import encode_mosp_decision

    cnf, _, _ = encode_mosp_decision(instance, k)
    path.parent.mkdir(parents=True, exist_ok=True)
    cnf.to_file(str(path))
    return cnf.nv, len(cnf.clauses)


def _load(name: str, solutions_dir: Path, instance_dir: Path):
    from mosp.visualize import load_cached_solution

    instance, ordering = load_cached_solution(name, solutions_dir, instance_dir)
    for candidate in sorted(solutions_dir.glob("*.json")):
        payload = json.loads(candidate.read_text())
        if payload["instance_name"] == instance.name:
            return instance, payload
    return instance, {"ordering": ordering, "mosp_value": None}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    p_check = sub.add_parser("check", help="verify a cached witness ordering")
    p_check.add_argument("name", nargs="?", default=None,
                         help="instance name; omit to check every solution")
    p_check.add_argument("--solutions-dir", type=Path, default=Path("solutions"))
    p_check.add_argument("--dir", type=Path, default=Path("benchmarks/instances"))

    p_export = sub.add_parser("export", help="write the decision CNF as DIMACS")
    p_export.add_argument("name")
    p_export.add_argument("--k", type=int, required=True)
    p_export.add_argument("--out", type=Path, required=True)
    p_export.add_argument("--solutions-dir", type=Path, default=Path("solutions"))
    p_export.add_argument("--dir", type=Path, default=Path("benchmarks/instances"))

    args = parser.parse_args()

    if args.mode == "export":
        instance, _ = _load(args.name, args.solutions_dir, args.dir)
        n_vars, n_clauses = export_cnf(instance, args.k, args.out)
        print(f"wrote {args.out}: {n_vars} variables, {n_clauses} clauses")
        print(f"refute with any SAT solver; UNSAT at k={args.k} plus a witness "
              f"at k={args.k + 1} proves the optimum is {args.k + 1}")
        return

    if args.name:
        instance, payload = _load(args.name, args.solutions_dir, args.dir)
        ok, message = check_witness(instance, payload)
        print(f"{instance.name}: {message}")
        raise SystemExit(0 if ok else 1)

    # Whole corpus.
    from benchmarks.solve_parallel import find_benchmark_files

    payloads = {}
    for candidate in sorted(args.solutions_dir.glob("*.json")):
        data = json.loads(candidate.read_text())
        payloads[data["instance_name"]] = data

    checked = failures = 0
    for filepath in find_benchmark_files(args.dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for instance in instances:
            payload = payloads.get(instance.name)
            if payload is None:
                continue
            ok, message = check_witness(instance, payload)
            checked += 1
            if not ok:
                failures += 1
                print(f"FAIL {instance.name}: {message}")

    print(f"checked {checked} witnesses, {failures} failed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
