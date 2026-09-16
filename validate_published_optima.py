#!/usr/bin/env python3
"""Validate direct MOSP-to-SAT solver against all published optimal values.

Runs instances smallest to largest. Stops immediately if a non-optimal
result is found (for debugging). Prints per-k progress so the run can
be monitored mid-course with `tail -f` or `cat`.

Uses solution caching: solved instances are saved to solutions/ and
verified on re-run instead of re-solved.

Usage:
    python validate_published_optima.py
"""

import sys
import time
from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering
from satisfiability.mosp_solver import (
    _lower_bound, _upper_bound, _load_solution, _save_solution, SOLUTIONS_DIR,
)


# Published optimal values from Frinhani et al. (2018, Table 2),
# computed using Chu & Stuckey (2009) exact solver.
PUBLISHED_OPTIMA = {
    "GP1": 45,   # 50x50, high pathwidth
    "GP2": 40,   # 50x50
    "GP3": 40,   # 50x50
    "GP4": 30,   # 50x50, low pathwidth
    "GP5": 95,   # 100x100, high pathwidth
    "GP6": 75,   # 100x100
    "GP7": 75,   # 100x100
    "GP8": 60,   # 100x100, low pathwidth
    "SP2": 19,   # 50x50
    "SP3": 34,   # 75x75
    "SP4": 53,   # 100x100
}

CHALLENGE_DIR = Path("benchmarks/instances/MOSP_Instances/Challenge")


def solve_with_progress(instance, published):
    """Solve MOSP with binary search and per-k progress output.

    Checks cache first. If a cached solution exists and is valid, returns it.
    Otherwise solves with binary search and caches the result.
    """
    from pysat.solvers import Solver

    # Check cache first
    cached = _load_solution(instance, SOLUTIONS_DIR)
    if cached is not None:
        val, ordering = cached
        print(f"    Loaded from cache: MOSP={val}")
        sys.stdout.flush()
        return val, ordering

    m = instance.n_patterns

    if m == 0:
        return 0, []
    if m == 1:
        val = len(instance.pattern_customers(0))
        return max(val, 0), [0]

    # Compute bounds
    lb = _lower_bound(instance)
    print(f"    Lower bound: {lb}")
    sys.stdout.flush()

    t0 = time.time()
    ub_val, best_ordering = _upper_bound(instance)
    ub_time = time.time() - t0
    print(f"    Upper bound: {ub_val} (tabu search: {ub_time:.1f}s)")
    sys.stdout.flush()

    if lb >= ub_val:
        _save_solution(instance, ub_val, best_ordering, SOLUTIONS_DIR)
        return ub_val, best_ordering

    import math
    n_calls = math.ceil(math.log2(ub_val - lb + 1))
    print(f"    Binary search: k in [{lb}, {ub_val}] (~{n_calls} SAT calls)")
    sys.stdout.flush()

    # Binary search: find smallest k where MOSP <= k is SAT
    lo = lb
    hi = ub_val  # known SAT
    best_sat_ordering = best_ordering
    call_num = 0

    while lo < hi:
        mid = (lo + hi) // 2
        call_num += 1

        t0 = time.time()
        cnf, pool, m_enc = encode_mosp_decision(instance, mid)
        enc_time = time.time() - t0

        t0 = time.time()
        with Solver(name="cd195", bootstrap_with=cnf) as solver:
            sat = solver.solve()
            solve_time = time.time() - t0

            result_str = "SAT" if sat else "UNSAT"
            next_range = f"[{lo}, {mid}]" if sat else f"[{mid+1}, {hi}]"

            print(
                f"    #{call_num}: k={mid:>3} {result_str:>5}  "
                f"(encode={enc_time:.1f}s, solve={solve_time:.1f}s, "
                f"clauses={len(cnf.clauses)})  "
                f"-> {next_range}"
            )
            sys.stdout.flush()

            if sat:
                hi = mid
                model = solver.get_model()
                best_sat_ordering = extract_ordering(model, pool, m_enc)
            else:
                lo = mid + 1

    actual = max_open_stacks(instance, best_sat_ordering)

    # Cache the result
    _save_solution(instance, actual, best_sat_ordering, SOLUTIONS_DIR)

    return actual, best_sat_ordering


def main():
    print("=" * 78)
    print("MOSP Direct SAT Solver — Validation Against Published Optimal Values")
    print("=" * 78)
    print()
    sys.stdout.flush()

    # Load and sort instances
    instances = []
    for name in PUBLISHED_OPTIMA:
        path = CHALLENGE_DIR / f"{name}.txt"
        if not path.exists():
            print(f"  WARNING: {path} not found, skipping {name}")
            continue
        insts = MOSPInstance.from_benchmark_file(path)
        if insts:
            inst = insts[0]
            inst.name = name
            instances.append(inst)

    instances.sort(key=lambda inst: (inst.n_patterns, inst.n_customers))

    print(f"Loaded {len(instances)} instances")
    print()
    sys.stdout.flush()

    passed = 0
    failed = 0

    for i, inst in enumerate(instances, 1):
        published = PUBLISHED_OPTIMA[inst.name]
        size_str = f"{inst.n_customers}x{inst.n_patterns}"

        print(f"[{i}/{len(instances)}] {inst.name} ({size_str}), published optimal = {published}")
        sys.stdout.flush()

        total_start = time.time()
        val, ordering = solve_with_progress(inst, published)
        total_time = time.time() - total_start

        # Verify
        actual = max_open_stacks(inst, ordering)

        if actual != val:
            print(f"  INCONSISTENT: SAT={val}, simulation={actual}")
            print(f"  Ordering: {ordering}")
            sys.stdout.flush()
            sys.exit(1)

        if val == published:
            print(f"  RESULT: {val} == {published} (published)  OK  [{total_time:.1f}s total]")
            passed += 1
        else:
            print(f"  RESULT: {val} != {published} (published)  FAIL  [{total_time:.1f}s total]")
            print()
            print(f"STOP: Non-optimal result!")
            print(f"  SAT found: {val}, Published: {published}")
            print(f"  Ordering: {ordering}")
            sys.stdout.flush()
            sys.exit(1)

        print()
        sys.stdout.flush()

    print("=" * 78)
    print(f"SUMMARY: {passed}/{len(instances)} passed, {failed} failed")
    if passed == len(instances):
        print("ALL PUBLISHED OPTIMA MATCHED!")
    print("=" * 78)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
