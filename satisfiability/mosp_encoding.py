"""SAT encoding for the direct MOSP decision problem.

Position-based formulation: given a MOSP instance and target k, encode
"can the patterns be sequenced so that at most k stacks are open at any step?"
as a CNF formula.

Variables (managed via pysat IDPool):
  x[p,t] — pattern p is placed at position t
  y[p,t] — pattern p is placed by step t (prefix membership)
  o[c,t] — customer c's stack is open at step t

Clauses:
  1. Permutation: each pattern gets exactly one position, each position exactly one pattern
  2. Prefix linking: x[p,t] -> y[p,t]; y[p,t] -> y[p,t+1]; y[p,t] -> y[p,t-1] OR x[p,t]
  3. Open stack forcing: if some pattern of customer c is placed by step t and some
     pattern of c is not placed before t, then o[c,t] must be true
  4. Width bound: at most k open stacks at each step (totalizer cardinality)
  5. Symmetry breaking: pattern with most customers in first half of positions
"""

from __future__ import annotations

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

from mosp.instance import MOSPInstance


def encode_mosp_decision(
    instance: MOSPInstance,
    k: int,
) -> tuple[CNF, IDPool, int]:
    """Encode the decision problem 'MOSP(instance) <= k?' as a CNF formula.

    Args:
        instance: A MOSP instance with n customers and m patterns.
        k: Target maximum number of open stacks.

    Returns:
        (cnf, pool, m) where:
          - cnf: the CNF formula
          - pool: the IDPool mapping variable names to SAT variable IDs
          - m: number of patterns (positions in the sequence)
    """
    n = instance.n_customers
    m = instance.n_patterns

    # Precompute customer-pattern relationships
    customer_pats: list[list[int]] = []
    for c in range(n):
        pats = sorted(instance.customer_patterns(c))
        customer_pats.append(pats)

    # Identify active customers (those requiring at least one pattern)
    active_customers = [c for c in range(n) if len(customer_pats[c]) > 0]

    pool = IDPool()
    cnf = CNF()

    # Track the next available variable ID for CardEnc auxiliary variables.
    # pool.occupy() does not update pool.top, so we must track this ourselves
    # to prevent different CardEnc calls from reusing the same auxiliary IDs.
    _next_var = [0]

    # Variable accessors
    def x(p: int, t: int) -> int:
        return pool.id(("x", p, t))

    def y(p: int, t: int) -> int:
        return pool.id(("y", p, t))

    def o(c: int, t: int) -> int:
        return pool.id(("o", c, t))

    def top() -> int:
        return max(pool.top, _next_var[0])

    def add_card(lits: list[int], bound: int, enc: int = EncType.ladder) -> None:
        """Add a cardinality constraint, properly tracking auxiliary variable IDs."""
        t = top()
        atmost = CardEnc.atmost(lits, bound=bound, top_id=t, encoding=enc)
        if atmost.nv > t:
            pool.occupy(t + 1, atmost.nv)
            _next_var[0] = atmost.nv
        cnf.extend(atmost)

    # -------------------------------------------------------
    # 1. Permutation constraints
    # -------------------------------------------------------
    # Each pattern is assigned to at least one position
    for p in range(m):
        cnf.append([x(p, t) for t in range(m)])

    # Each pattern is assigned to at most one position (ladder encoding)
    for p in range(m):
        add_card([x(p, t) for t in range(m)], bound=1)

    # Each position has at least one pattern
    for t in range(m):
        cnf.append([x(p, t) for p in range(m)])

    # Each position has at most one pattern (ladder encoding)
    for t in range(m):
        add_card([x(p, t) for p in range(m)], bound=1)

    # -------------------------------------------------------
    # 2. Prefix linking
    # -------------------------------------------------------
    for p in range(m):
        for t in range(m):
            # x[p,t] -> y[p,t]
            cnf.append([-x(p, t), y(p, t)])

            # y[p,t] -> y[p,t+1]  (monotonicity)
            if t < m - 1:
                cnf.append([-y(p, t), y(p, t + 1)])

            # y[p,t] -> y[p,t-1] OR x[p,t]
            # (if p is placed by step t, then either it was placed by step t-1
            #  or it was placed exactly at step t)
            if t > 0:
                cnf.append([-y(p, t), y(p, t - 1), x(p, t)])
            else:
                # t=0: if placed by step 0, must be at position 0
                cnf.append([-y(p, 0), x(p, 0)])

    # -------------------------------------------------------
    # 3. Open stack forcing
    # -------------------------------------------------------
    # Customer c's stack is open at step t if first_pos(c) <= t <= last_pos(c),
    # i.e., some pattern of c has been produced and some pattern of c is being
    # produced at this step or was produced at a later step.
    #
    # Two types of forcing clauses:
    #
    # (a) Placement forcing: when pattern p of customer c is placed at step t,
    #     the stack is open. x[p,t] -> o[c,t]
    #     This captures the first and last steps (which pair-wise misses).
    #
    # (b) Pair-wise forcing: when some pattern p is placed by step t but some
    #     pattern q is NOT placed by step t, the stack is open.
    #     y[p,t] AND NOT y[q,t] -> o[c,t]
    #     This captures intermediate steps between first and last.
    for c in active_customers:
        pats = customer_pats[c]
        # (a) Placement forcing: x[p,t] -> o[c,t] for all p in P_c
        for p in pats:
            for t in range(m):
                cnf.append([-x(p, t), o(c, t)])
        # (b) Pair-wise forcing (only needed for |P_c| >= 2)
        if len(pats) >= 2:
            for t in range(m):
                for p in pats:
                    for q in pats:
                        if p != q:
                            # y[p,t] AND NOT y[q,t] -> o[c,t]
                            cnf.append([-y(p, t), y(q, t), o(c, t)])

    # -------------------------------------------------------
    # 4. Width bound: at most k stacks open at each step
    # -------------------------------------------------------
    for t in range(m):
        open_lits = [o(c, t) for c in active_customers]
        if len(open_lits) > k:
            add_card(open_lits, bound=k, enc=EncType.totalizer)

    # -------------------------------------------------------
    # 5. Symmetry breaking: fix the pattern with the most customers
    #    to the first half of positions (reversal symmetry)
    # -------------------------------------------------------
    if m >= 2:
        # Find pattern with most customers
        max_cust_pattern = max(range(m), key=lambda p: len(instance.pattern_customers(p)))
        half = m // 2 + 1  # first floor(m/2)+1 positions
        # Pattern must be in one of positions 0..half-1
        cnf.append([x(max_cust_pattern, t) for t in range(half)])

    return cnf, pool, m


def extract_ordering(
    model: list[int],
    pool: IDPool,
    m: int,
) -> list[int]:
    """Extract the pattern ordering from a satisfying assignment.

    Args:
        model: List of literals (positive = true, negative = false).
        pool: The IDPool used during encoding.
        m: Number of patterns.

    Returns:
        A list of pattern indices in the order determined by the assignment.
    """
    true_vars = set(model)
    ordering = [None] * m

    for p in range(m):
        for t in range(m):
            var_id = pool.id(("x", p, t))
            if var_id in true_vars:
                ordering[t] = p
                break

    return ordering
