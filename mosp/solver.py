"""End-to-end MOSP solver via reduction to pathwidth.

Pipeline:
  1. Parse MOSP instance
  2. Build agreement graph
  3. Compute pathwidth (exact DP)
  4. Extract pattern ordering
  5. Return MOSP solution with optimal value = pathwidth + 1
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance
from mosp.reduction import mosp_to_pathwidth, pathwidth_to_mosp, MOSPSolution
from mosp.verify import max_open_stacks
from fixed_parameter_algorithm.pathwidth_fpt import compute_pathwidth_fpt


def solve_mosp(instance: MOSPInstance) -> MOSPSolution:
    """Solve a MOSP instance optimally via reduction to pathwidth.

    The pathwidth of the agreement graph gives the optimal ordering, but the
    actual MOSP value (max open stacks) is computed by simulating the ordering
    on the original instance. This handles edge cases where the number of
    customers is smaller than pathwidth + 1.

    Args:
        instance: A MOSP instance.

    Returns:
        A MOSPSolution with the optimal ordering and objective value.

    Raises:
        ValueError: If the instance has too many patterns for exact solving.
    """
    # Step 1: Reduce to pathwidth problem
    pw_problem = mosp_to_pathwidth(instance)

    # Step 2: Solve pathwidth exactly
    pathwidth, ordering = compute_pathwidth_fpt(pw_problem.graph)

    # Step 3: Compute actual MOSP value by simulation
    actual_mosp = max_open_stacks(instance, ordering)

    # Step 4: Build solution
    solution = pathwidth_to_mosp(pw_problem, pathwidth, ordering)
    solution.max_open_stacks = actual_mosp

    return solution


def solve_mosp_from_file(path: str | Path) -> MOSPSolution:
    """Parse a MOSP instance file and solve it.

    Args:
        path: Path to a MOSP instance file.

    Returns:
        A MOSPSolution with the optimal ordering and objective value.
    """
    instance = MOSPInstance.from_file(path)
    return solve_mosp(instance)
