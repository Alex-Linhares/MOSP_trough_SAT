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

    @classmethod
    def from_benchmark_file(
        cls, path: str | Path, transpose: bool | None = None
    ) -> List["MOSPInstance"]:
        """Parse benchmark instance files, returning a list of instances.

        Handles two formats:
          - Format A (MOSP_Instances/): One instance per file, first line is
            "m n" (patterns x pieces), matrix needs transposing to get
            customers x patterns.
          - Format B (ChallengeInstances2005/): Multiple instances per file,
            optional text description lines before each "m n" line, matrix is
            already customers x patterns.

        Args:
            path: Path to a benchmark file.
            transpose: If True, transpose the matrix (Format A). If False,
                don't (Format B). If None, auto-detect: transpose if the path
                contains "MOSP_Instances".

        Returns:
            A list of MOSPInstance objects parsed from the file.
        """
        path = Path(path)
        if transpose is None:
            transpose = "MOSP_Instances" in str(path)

        text = path.read_text()
        lines = text.splitlines()

        instances: List[MOSPInstance] = []
        i = 0
        instance_idx = 0

        while i < len(lines):
            # Skip blank lines
            if not lines[i].strip():
                i += 1
                continue

            # Try to parse current line as "m n" dimensions
            name = ""
            parts = lines[i].split()
            try:
                dim1, dim2 = int(parts[0]), int(parts[1])
                if len(parts) != 2:
                    raise ValueError
            except (ValueError, IndexError):
                # This line is a text description — use it as the name
                name = lines[i].strip()
                i += 1
                # Skip blank lines after description
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i >= len(lines):
                    break
                parts = lines[i].split()
                dim1, dim2 = int(parts[0]), int(parts[1])

            i += 1  # advance past the dimension line

            # Read matrix rows: collect lines until we have dim1 complete rows
            # (some files wrap long rows across multiple lines)
            all_values: list[int] = []
            expected_total = dim1 * dim2
            while i < len(lines) and len(all_values) < expected_total:
                line = lines[i].strip()
                if not line:
                    # Blank line inside matrix — stop if we already have
                    # enough for at least one row, otherwise skip
                    if len(all_values) >= dim2:
                        break
                    i += 1
                    continue
                # Check if this line is a new dimension line or description
                # (meaning the matrix ended early)
                line_parts = line.split()
                if len(all_values) >= dim2:
                    # We have at least one row already
                    try:
                        # If this line has exactly 2 ints and they could be
                        # dimensions for a next instance, stop
                        if len(line_parts) == 2:
                            int(line_parts[0])
                            int(line_parts[1])
                            # Could be a new dimension line — check if we
                            # have a complete set of rows
                            if len(all_values) % dim2 == 0:
                                break
                    except ValueError:
                        # Text line — must be a description for next instance
                        break
                row_vals = list(map(int, line_parts))
                all_values.extend(row_vals)
                i += 1

            # Build matrix from collected values
            n_rows = len(all_values) // dim2
            if n_rows < dim1:
                # Truncated — use what we have if it makes complete rows
                if n_rows == 0:
                    continue
            else:
                n_rows = dim1

            matrix = np.array(
                all_values[: n_rows * dim2], dtype=np.int8
            ).reshape(n_rows, dim2)

            if transpose:
                matrix = matrix.T

            n_customers, n_patterns = matrix.shape

            if not name:
                name = f"{path.stem}_{instance_idx}"
            instance_idx += 1

            instances.append(
                cls(
                    matrix=matrix,
                    n_customers=n_customers,
                    n_patterns=n_patterns,
                    name=name,
                )
            )

        return instances
