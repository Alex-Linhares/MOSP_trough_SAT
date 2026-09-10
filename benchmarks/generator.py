"""Random MOSP instance generator.

Generates random binary matrices following the approach from the literature
(Chu & Stuckey 2009, Faggioli & Bentivoglio 1998).

Parameters:
  - n_patterns: number of products/patterns (columns)
  - n_customers: number of customers/orders (rows)
  - density: probability that a customer requires a pattern, or
  - customers_per_pattern: average number of customers per pattern
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mosp.instance import MOSPInstance


def generate_random_instance(
    n_customers: int,
    n_patterns: int,
    density: float = 0.3,
    seed: int | None = None,
    name: str | None = None,
) -> MOSPInstance:
    """Generate a random MOSP instance with given density.

    Each entry M[i][j] is 1 with probability `density`, independently.
    Rows/columns that are all-zero are given at least one random 1 to ensure
    every customer needs something and every pattern is needed by someone.

    Args:
        n_customers: Number of customers (rows).
        n_patterns: Number of patterns (columns).
        density: Probability each entry is 1.
        seed: Random seed for reproducibility.
        name: Instance name.

    Returns:
        A MOSPInstance with the generated binary matrix.
    """
    rng = np.random.RandomState(seed)

    if name is None:
        name = f"random_{n_customers}x{n_patterns}_d{density:.2f}_s{seed}"

    matrix = (rng.random((n_customers, n_patterns)) < density).astype(np.int8)

    # Ensure no all-zero rows (every customer needs at least one pattern)
    for i in range(n_customers):
        if matrix[i].sum() == 0:
            j = rng.randint(0, n_patterns)
            matrix[i, j] = 1

    # Ensure no all-zero columns (every pattern is needed by at least one customer)
    for j in range(n_patterns):
        if matrix[:, j].sum() == 0:
            i = rng.randint(0, n_customers)
            matrix[i, j] = 1

    return MOSPInstance.from_matrix(matrix, name=name)


def generate_structured_instance(
    n_customers: int,
    n_patterns: int,
    customers_per_pattern: int,
    seed: int | None = None,
    name: str | None = None,
) -> MOSPInstance:
    """Generate a MOSP instance where each pattern has a fixed number of customers.

    This follows the generation style from Chu & Stuckey (2009): for each
    pattern, exactly `customers_per_pattern` customers are randomly selected
    to require it.

    Args:
        n_customers: Number of customers (rows).
        n_patterns: Number of patterns (columns).
        customers_per_pattern: Exact number of customers requiring each pattern.
        seed: Random seed for reproducibility.
        name: Instance name.

    Returns:
        A MOSPInstance with the generated binary matrix.
    """
    rng = np.random.RandomState(seed)

    if name is None:
        name = f"struct_{n_customers}x{n_patterns}_cpp{customers_per_pattern}_s{seed}"

    cpp = min(customers_per_pattern, n_customers)
    matrix = np.zeros((n_customers, n_patterns), dtype=np.int8)

    for j in range(n_patterns):
        customers = rng.choice(n_customers, size=cpp, replace=False)
        matrix[customers, j] = 1

    # Ensure no all-zero rows
    for i in range(n_customers):
        if matrix[i].sum() == 0:
            j = rng.randint(0, n_patterns)
            matrix[i, j] = 1

    return MOSPInstance.from_matrix(matrix, name=name)


def generate_benchmark_suite(
    output_dir: str | Path,
    sizes: list[tuple[int, int]] | None = None,
    densities: list[float] | None = None,
    n_instances_per_config: int = 3,
    seed: int = 42,
) -> list[Path]:
    """Generate a suite of benchmark instances.

    Args:
        output_dir: Directory to write instance files.
        sizes: List of (n_customers, n_patterns) pairs.
        densities: List of density values.
        n_instances_per_config: Number of instances per (size, density) config.
        seed: Base random seed.

    Returns:
        List of paths to generated instance files.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if sizes is None:
        sizes = [
            (10, 10), (15, 10), (10, 15),
            (15, 15), (20, 15), (20, 20),
        ]
    if densities is None:
        densities = [0.2, 0.3, 0.5]

    paths = []
    idx = 0
    for n_cust, n_pat in sizes:
        for dens in densities:
            for rep in range(n_instances_per_config):
                instance = generate_random_instance(
                    n_customers=n_cust,
                    n_patterns=n_pat,
                    density=dens,
                    seed=seed + idx,
                    name=f"bench_{n_cust}x{n_pat}_d{dens:.1f}_r{rep}",
                )
                path = output_dir / f"{instance.name}.mosp"
                instance.to_file(path)
                paths.append(path)
                idx += 1

    return paths
