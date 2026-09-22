"""Exact MOSP solvers: the complete customer search and the SAT encoding.

`solve_mosp_exact` is the entry point to reach for. It runs the complete
customer search by default; `procedure="sat"` selects the CNF encoding, which
is what to use when a checkable proof object matters, since a refutation from
the customer search is not a DRAT proof.
"""

from satisfiability.mosp_solver import solve_mosp_exact, solve_mosp_sat
from satisfiability.solver import compute_pathwidth_sat

__all__ = ["compute_pathwidth_sat", "solve_mosp_exact", "solve_mosp_sat"]
