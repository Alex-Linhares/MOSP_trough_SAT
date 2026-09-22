"""A lower bound on MOSP from neighbourhood expansion, not from degree.

Every lower bound this project had before this one is degree-based -- the
trivial bound, the clique bound, degeneracy, contraction degeneracy (= the arc
contraction bound of Yanasse, Becceneri & Soma 1999) -- and on the instances
that actually cost compute they all saturate near the *average degree* while the
optimum is roughly twice it. `Random-125-125-8-5_0`: average degree 43.2, our
bound 47, optimum 91. The strongest standard improvement in the treewidth
literature, the improved-graph technique LBN+ (Bodlaender, Koster & Wolle),
gains exactly zero on those instances. The family is out of room.

**The argument.** MOSP equals vertex separation plus one. Fix any ordering of
the customers and let `V_i` be its first `i`. The stacks open after `i` steps
are `i - |C_i|`, where `C_i = {v in V_i : N[v] subset of V_i}` is the customers
already *finished*. Since `N[C_i]` lies inside `V_i`,

    |N[C_i]| <= i.

So writing `f(t) = min over |C| = t of |N[C]|` -- which is non-decreasing in `t`,
because any `C` of size `t+1` contains one of size `t` with a smaller closed
neighbourhood -- no set of size `t` can sit inside a prefix of size `i` unless
`f(t) <= i`. Hence `|C_i| <= M(i) := max{t : f(t) <= i}` and

    vs(G) >= max over i of (i - M(i)),      MOSP(I) >= that + 1.

This measures how fast neighbourhoods *expand*, which is exactly the quantity
the degree-based bounds ignore and exactly where a dense graph is extreme.

**Where the care is needed.** `f` is only computed up to some cap `T`, so
`M(i) <= T` is proved only for `i < f(T+1)` -- and only if that `f(T+1)` is
**exact**. An overestimate would extend the usable prefix range too far and the
bound would exceed the optimum, which is not a slow bound but a wrong answer:
the search would start above the optimum and return a value whose witness
verifies. The first draft of this made exactly that mistake and returned 122
against an optimum of 91. So `f` is computed by exhaustive branch and bound, and
a level whose search is abandoned on budget is discarded entirely rather than
used.

Validated over all 6,376 certified optima at `max_t=4`: **zero violations**,
mean gap 0.98 -> 0.61, tight on 65.3% -> 75.3%. On the 200 Chu & Stuckey
`Random` instances, mean gap 12.76 -> 8.82 and tight on 1.5% -> 18.5%. Deeper
caps go much further on the hardest instances -- `Random-125-125-10-5_0` reaches
98 against an optimum of 99, from 59 -- at a cost that grows sharply with `t`.

**Prior art unsettled.** This is a vertex-isoperimetric argument over an interval
/ vertex-separation formulation, and something equivalent may well be known;
Ellis, Sudborough & Turner (1994) on vertex separation is the obvious place to
look. No novelty is claimed until `literature/MISSING.md` records an answer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from mosp.instance import MOSPInstance

# Levels beyond this are not attempted: `f(t)` is a search over t-subsets and
# the cost grows steeply, while the gain per level is already flattening.
MAX_LEVEL = 12


@dataclass
class ExpansionBound:
    """A bound, and the evidence behind it.

    `levels` is `f(1) .. f(t_max)`, each exact. `cap` is the deepest `T` for
    which `f(T+1)` was completed, so `max_i (i - M(i))` is proved for every
    prefix `i < f(T+1)`; `complete` says whether the search finished within
    budget or stopped early.
    """

    value: int
    cap: int
    levels: list[int] = field(default_factory=list)
    complete: bool = True
    seconds: float = 0.0


def _closed_masks(instance: MOSPInstance) -> tuple[list[int], int]:
    """Self-inclusive customer neighbourhoods of the MOSP graph, as bitmasks.

    Built straight from the matrix rather than through networkx: a product's
    holders form a clique, so OR-ing each holder set into each of its members
    gives `N[v]` in one pass over the products.
    """
    n = instance.n_customers
    masks = [1 << v for v in range(n)]
    for pattern in range(instance.n_patterns):
        holders = sorted(instance.pattern_customers(pattern))
        together = 0
        for customer in holders:
            together |= 1 << customer
        for customer in holders:
            masks[customer] |= together
    return masks, n


def _f_exact(masks: list[int], n: int, t: int, order: list[int],
             deadline: float | None) -> int | None:
    """`min |N[C]|` over every `C` of size `t`, or None if the budget ran out.

    Exhaustive with two cuts: a union already as large as the incumbent cannot
    improve it, and a suffix too short to reach size `t` is dead. Returning None
    rather than the incumbent matters -- the incumbent is an *over*estimate of
    the minimum, and using it as `f(T+1)` would extend the prefix range beyond
    what is proved.
    """
    best = n + 1
    checked = 0

    def dfs(start: int, chosen: int, union: int) -> bool:
        """False if the budget ran out."""
        nonlocal best, checked
        if union.bit_count() >= best:
            return True
        if chosen == t:
            best = union.bit_count()
            return True
        if n - start < t - chosen:
            return True
        for k in range(start, n):
            checked += 1
            if deadline is not None and not checked & 0x3FFF and time.monotonic() > deadline:
                return False
            if not dfs(k + 1, chosen + 1, union | masks[order[k]]):
                return False
        return True

    return best if dfs(0, 0, 0) else None


def expansion_bound(
    instance: MOSPInstance,
    max_t: int = 4,
    time_budget: float | None = 5.0,
) -> ExpansionBound:
    """Lower bound on MOSP from how fast closed neighbourhoods expand.

    Anytime in `max_t`: each level is usable the moment the *next* level's `f`
    is known exactly, so a budget that expires mid-level costs that level and
    keeps everything below it. The best bound over the completed caps is
    returned, since deeper is not guaranteed better -- a larger cap widens the
    usable prefix range but can also raise `M(i)`.

    Args:
        max_t: deepest cap to attempt, itself capped at `MAX_LEVEL`.
        time_budget: seconds, or None for no limit.

    Returns:
        An `ExpansionBound` whose `value` is a valid lower bound on `MOSP`.
    """
    started = time.monotonic()
    deadline = None if time_budget is None else started + time_budget

    masks, n = _closed_masks(instance)
    if n == 0:
        return ExpansionBound(0, 0, [], True, 0.0)

    order = sorted(range(n), key=lambda v: masks[v].bit_count())
    max_t = max(1, min(max_t, MAX_LEVEL, n - 1))

    levels: list[int] = []
    best_value, best_cap, complete = 0, 0, True

    for t in range(1, max_t + 2):
        value = _f_exact(masks, n, t, order, deadline)
        if value is None:
            complete = False
            break
        levels.append(value)

        # With f(1..t) exact, prefixes below f(t) admit no C of size >= t.
        cap = t - 1
        if cap >= 1:
            limit = min(n, levels[t - 1] - 1)
            for i in range(1, limit + 1):
                m = 0
                for s in range(cap, 0, -1):
                    if levels[s - 1] <= i:
                        m = s
                        break
                if i - m > best_value:
                    best_value, best_cap = i - m, cap

    return ExpansionBound(best_value + 1 if best_value else 0, best_cap, levels,
                          complete, time.monotonic() - started)


def mosp_lower_bound(instance: MOSPInstance, max_t: int = 4,
                     time_budget: float | None = 5.0) -> int:
    """The bound alone, for callers that do not want the evidence."""
    return expansion_bound(instance, max_t=max_t, time_budget=time_budget).value
