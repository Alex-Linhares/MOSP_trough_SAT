"""Verify a MOSP solution by simulating the production sequence.

Given a pattern ordering and binary matrix, simulate processing patterns
in order and track which customer stacks are open at each step.

A customer's stack is open from the first pattern they require until the
last pattern they require has been processed.
"""

from __future__ import annotations

import numpy as np

from mosp.instance import MOSPInstance


def count_open_stacks(instance: MOSPInstance, ordering: list[int]) -> list[int]:
    """Count the number of open stacks at each step of the production sequence.

    A customer's stack opens when the first pattern they need is produced
    and closes after the last pattern they need is produced.

    Args:
        instance: A MOSP instance.
        ordering: A permutation of pattern indices (0..m-1).

    Returns:
        A list of length m where entry i is the number of open stacks
        after producing the (i+1)-th pattern in the ordering.
    """
    m = instance.n_patterns
    n = instance.n_customers

    assert len(ordering) == m, f"Ordering length {len(ordering)} != {m} patterns"
    assert set(ordering) == set(range(m)), "Ordering must be a permutation of 0..m-1"

    # For each customer, find the first and last position in the ordering
    # where one of their required patterns appears
    pos = {pattern: i for i, pattern in enumerate(ordering)}

    first_pos = [m] * n  # first position a customer's pattern appears
    last_pos = [-1] * n  # last position a customer's pattern appears

    for customer in range(n):
        patterns = instance.customer_patterns(customer)
        if not patterns:
            continue
        positions = [pos[p] for p in patterns]
        first_pos[customer] = min(positions)
        last_pos[customer] = max(positions)

    # Count open stacks at each step
    open_counts = []
    for step in range(m):
        count = 0
        for customer in range(n):
            if first_pos[customer] <= step <= last_pos[customer]:
                count += 1
        open_counts.append(count)

    return open_counts


def max_open_stacks(instance: MOSPInstance, ordering: list[int]) -> int:
    """Return the maximum number of simultaneously open stacks.

    This is the MOSP objective value for the given ordering.

    Args:
        instance: A MOSP instance.
        ordering: A permutation of pattern indices.

    Returns:
        The maximum number of open stacks at any point during production.
    """
    counts = count_open_stacks(instance, ordering)
    return max(counts) if counts else 0


def verify_solution(
    instance: MOSPInstance, ordering: list[int], claimed_value: int
) -> tuple[bool, int]:
    """Verify that a claimed MOSP solution is correct.

    Args:
        instance: A MOSP instance.
        ordering: The claimed optimal ordering.
        claimed_value: The claimed maximum open stacks.

    Returns:
        (is_correct, actual_value) where is_correct is True iff
        the actual max open stacks equals the claimed value.
    """
    actual = max_open_stacks(instance, ordering)
    return actual == claimed_value, actual
