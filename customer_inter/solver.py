"""End-to-end MOSP solver via reduction to pathwidth of the customer graph.

Pipeline:
  1. Parse MOSP instance
  2. Build customer intersection graph
  3. Compute pathwidth (exact DP / FPT)
  4. Derive pattern ordering from customer ordering
  5. Simulate to get actual MOSP count
  6. Return solution
"""

from __future__ import annotations

from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from customer_inter.reduction import (
    mosp_to_pathwidth,
    pathwidth_to_mosp,
    CustomerMOSPSolution,
)
from fixed_parameter_algorithm.pathwidth_fpt import compute_pathwidth_fpt


def solve_mosp(instance: MOSPInstance) -> CustomerMOSPSolution:
    """Solve a MOSP instance via reduction to pathwidth of the customer graph.

    Args:
        instance: A MOSP instance.

    Returns:
        A CustomerMOSPSolution with the optimal ordering and objective value.
    """
    # Step 1: Reduce to pathwidth problem on customer graph
    pw_problem = mosp_to_pathwidth(instance)

    # Step 2: Solve pathwidth exactly
    pathwidth, customer_ordering = compute_pathwidth_fpt(pw_problem.graph)

    # Step 3: Convert customer ordering to pattern ordering and build solution
    solution = pathwidth_to_mosp(pw_problem, pathwidth, customer_ordering)

    # Step 4: Compute actual MOSP value by simulation
    actual_mosp = max_open_stacks(instance, solution.ordering)
    solution.max_open_stacks = actual_mosp

    return solution


def solve_mosp_from_file(path: str | Path) -> CustomerMOSPSolution:
    """Parse a MOSP instance file and solve it via the customer graph.

    Args:
        path: Path to a MOSP instance file.

    Returns:
        A CustomerMOSPSolution with the optimal ordering and objective value.
    """
    instance = MOSPInstance.from_file(path)
    return solve_mosp(instance)
