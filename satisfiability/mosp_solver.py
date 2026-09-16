"""Direct MOSP-to-SAT solver with iterative deepening.

Encodes the MOSP decision problem directly as SAT, bypassing the lossy
pathwidth reduction. Uses iterative deepening over the target number of
open stacks k, with greedy upper bounds and a max-customer lower bound.

The SAT infrastructure (pysat, CaDiCaL, cardinality constraints) is
shared with the pathwidth SAT solver.

Solutions can be cached to JSON files in a solutions/ directory. On
subsequent runs, the solver checks for an existing solution file and
verifies it instead of re-solving.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering

# Default directory for cached solutions
SOLUTIONS_DIR = Path(__file__).parent.parent / "solutions"


def _lower_bound(instance: MOSPInstance) -> int:
    """Compute a lower bound on MOSP.

    For any pattern p, when p is produced, all customers requiring p have
    their stacks open (their first pattern has been produced — possibly p
    itself — and their last pattern hasn't been produced yet — possibly p
    itself). So at minimum, len(pattern_customers(p)) stacks are open.

    Actually, this counts customers whose *only* pattern is p as having
    open stacks too (they open and close at the same step). The true
    lower bound is max over all patterns of |customers(p)|.
    """
    m = instance.n_patterns
    if m == 0:
        return 0
    return max(len(instance.pattern_customers(p)) for p in range(m))


def _upper_bound(instance: MOSPInstance, n_random: int = 10, seed: int = 42) -> tuple[int, list[int]]:
    """Compute an upper bound on MOSP via greedy orderings.

    Tries identity, reverse, and random permutations, returning the best
    (lowest max open stacks) ordering found.

    Returns:
        (upper_bound_value, best_ordering)
    """
    m = instance.n_patterns
    if m == 0:
        return 0, []

    best_val = float("inf")
    best_ord = list(range(m))

    candidates = [list(range(m)), list(range(m - 1, -1, -1))]

    rng = random.Random(seed)
    for _ in range(n_random):
        perm = list(range(m))
        rng.shuffle(perm)
        candidates.append(perm)

    for perm in candidates:
        val = max_open_stacks(instance, perm)
        if val < best_val:
            best_val = val
            best_ord = perm

    return best_val, best_ord


def _solution_path(instance: MOSPInstance, solutions_dir: Path) -> Path:
    """Return the path for a cached solution file."""
    # Sanitize instance name for use as a filename
    name = instance.name or "unnamed"
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
    return solutions_dir / f"{safe_name}.json"


def _save_solution(
    instance: MOSPInstance,
    val: int,
    ordering: list[int],
    solutions_dir: Path,
) -> Path:
    """Save a solution to a JSON file."""
    solutions_dir.mkdir(parents=True, exist_ok=True)
    path = _solution_path(instance, solutions_dir)
    data = {
        "instance_name": instance.name,
        "n_customers": instance.n_customers,
        "n_patterns": instance.n_patterns,
        "mosp_value": val,
        "ordering": ordering,
    }
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def _load_solution(
    instance: MOSPInstance,
    solutions_dir: Path,
) -> tuple[int, list[int]] | None:
    """Load and verify a cached solution. Returns None if invalid or missing."""
    path = _solution_path(instance, solutions_dir)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text())
        ordering = data["ordering"]
        claimed_val = data["mosp_value"]

        # Basic validation
        m = instance.n_patterns
        if len(ordering) != m or set(ordering) != set(range(m)):
            return None

        # Verify by simulation
        actual = max_open_stacks(instance, ordering)
        if actual != claimed_val:
            return None

        return claimed_val, ordering
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def solve_mosp_sat(
    instance: MOSPInstance,
    max_stacks: int | None = None,
    solutions_dir: Path | str | None = SOLUTIONS_DIR,
) -> tuple[int, list[int]]:
    """Solve MOSP exactly using direct SAT encoding.

    Encodes the MOSP decision problem directly, sequencing patterns and
    counting open stacks. This avoids the lossy pathwidth reduction that
    overcounts on sparse instances.

    If solutions_dir is set, checks for a cached solution file first and
    verifies it. If valid, returns the cached result. Otherwise solves
    and saves the result.

    Args:
        instance: A MOSP instance.
        max_stacks: Optional upper bound on open stacks to search.
            If None, computed via greedy heuristics.
        solutions_dir: Directory for cached solutions. Set to None to
            disable caching.

    Returns:
        (optimal_mosp_value, pattern_ordering) where the ordering is a
        permutation of pattern indices 0..m-1 that achieves the optimum.
    """
    # Check for cached solution
    if solutions_dir is not None:
        solutions_dir = Path(solutions_dir)
        cached = _load_solution(instance, solutions_dir)
        if cached is not None:
            return cached

    m = instance.n_patterns
    n = instance.n_customers

    if m == 0:
        return 0, []
    if m == 1:
        # Single pattern: open stacks = number of customers needing it
        val = len(instance.pattern_customers(0))
        return max(val, 0), [0]

    # Compute bounds
    k_lower = _lower_bound(instance)
    k_upper_val, best_ordering = _upper_bound(instance)

    if max_stacks is not None:
        k_upper_val = min(k_upper_val, max_stacks)

    # If bounds are tight, return the greedy solution
    if k_lower >= k_upper_val:
        val, ordering = k_upper_val, best_ordering
    else:
        val, ordering = None, None
        # Iterative deepening with SAT
        for k in range(k_lower, k_upper_val):
            result = _sat_decision(instance, k)
            if result is not None:
                # Verify by simulation
                actual = max_open_stacks(instance, result)
                val, ordering = actual, result
                break

        if val is None:
            # Fallback: the greedy ordering achieves k_upper_val
            val, ordering = k_upper_val, best_ordering

    # Save solution
    if solutions_dir is not None and instance.name:
        _save_solution(instance, val, ordering, solutions_dir)

    return val, ordering


def _sat_decision(
    instance: MOSPInstance,
    k: int,
) -> list[int] | None:
    """Test if MOSP(instance) <= k using SAT encoding.

    Returns a witness ordering if satisfiable, None otherwise.
    """
    from pysat.solvers import Solver

    cnf, pool, m = encode_mosp_decision(instance, k)

    with Solver(name="cd195", bootstrap_with=cnf) as solver:
        if solver.solve():
            model = solver.get_model()
            return extract_ordering(model, pool, m)

    return None
