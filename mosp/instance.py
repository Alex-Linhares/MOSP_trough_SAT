"""MOSP instance representation and parser.

Standard MOSP file format:
  Line 1: instance name (string)
  Line 2: n m  (n = number of customers/orders, m = number of products/patterns)
  Lines 3+: n×m binary matrix (n rows, m columns)

Convention: rows = customers, columns = patterns (products).
The binary matrix M[i][j] = 1 means customer i requires pattern/product j.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np


@dataclass
class MOSPInstance:
    """A Minimization of Open Stacks Problem instance.

    Attributes:
        matrix: Binary matrix of shape (n_customers, n_patterns).
                M[i][j] = 1 iff customer i requires pattern j.
        n_customers: Number of customers (rows).
        n_patterns: Number of patterns/products (columns).
        name: Optional instance name.
    """
    matrix: np.ndarray
    n_customers: int
    n_patterns: int
    name: str = ""

    @staticmethod
    def from_file(path: str | Path) -> MOSPInstance:
        """Parse a MOSP instance from a file in the standard format."""
        path = Path(path)
        lines = path.read_text().strip().splitlines()

        name = lines[0].strip()
        parts = lines[1].split()
        n_customers, n_patterns = int(parts[0]), int(parts[1])

        rows = []
        for i in range(2, 2 + n_customers):
            row = list(map(int, lines[i].split()))
            rows.append(row)

        matrix = np.array(rows, dtype=np.int8)
        assert matrix.shape == (n_customers, n_patterns), (
            f"Expected shape ({n_customers}, {n_patterns}), got {matrix.shape}"
        )

        return MOSPInstance(
            matrix=matrix,
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )

    @staticmethod
    def from_matrix(matrix: List[List[int]] | np.ndarray, name: str = "") -> MOSPInstance:
        """Create an instance from a binary matrix."""
        matrix = np.array(matrix, dtype=np.int8)
        n_customers, n_patterns = matrix.shape
        return MOSPInstance(
            matrix=matrix,
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )

    def to_file(self, path: str | Path) -> None:
        """Write the instance to a file in the standard format."""
        path = Path(path)
        lines = [self.name, f"{self.n_customers} {self.n_patterns}"]
        for row in self.matrix:
            lines.append(" ".join(map(str, row)))
        path.write_text("\n".join(lines) + "\n")

    def pattern_customers(self, pattern: int) -> set[int]:
        """Return the set of customers that require the given pattern."""
        return set(np.where(self.matrix[:, pattern] == 1)[0].tolist())

    def customer_patterns(self, customer: int) -> set[int]:
        """Return the set of patterns required by the given customer."""
        return set(np.where(self.matrix[customer, :] == 1)[0].tolist())
