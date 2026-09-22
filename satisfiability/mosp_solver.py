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
import time
from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering

# SAT backend for the decision calls. Chosen by measurement, not default:
# across 6 hard instances x 19 pysat backends (benchmarks/solver_portfolio.py),
# Kissat404 was the only one to close all six refutations at k-1, against 2 for
# cd195 and 3 for cd153. Refutations dominate runtime -- the satisfiable call at
# k is comparatively cheap -- so the UNSAT column decides this. Kissat was also
# the fastest on the satisfiable calls it closed (13.6s against cd195's 19.1s),
# though it missed one of six there.
#
# Re-run benchmarks/solver_portfolio.py before changing this.
SAT_BACKEND = "kissat404"

# Default directory for cached solutions
SOLUTIONS_DIR = Path(__file__).parent.parent / "solutions"


def _lower_bound(
    instance: MOSPInstance,
    clique_budget: float = 5.0,
    expansion_t: int = 8,
    expansion_budget: float | None = None,
) -> int:
    """Compute a lower bound on MOSP from the largest clique found.

    In the MOSP graph (nodes are customers, an edge iff some pattern is
    required by both — Yanasse 1997c), any clique C forces |C| simultaneously
    open stacks:

        Let c be the customer of C that closes earliest. Every other c' in C
        shares some pattern p with c. Since c closes at step t, all of c's
        patterns including p are produced by t, so c' has opened by t; and c'
        closes after c. So every customer of C is open at step t.

    Hence MOSP >= omega(G). This argument is direct and does not rely on the
    MOSP = pathwidth + 1 equality.

    Each pattern is itself a clique, so the maximum patterns-per-customer count
    is the special case of this bound over single-pattern cliques — that is the
    trivial bound of Yuen & Richardson (1995), and the starting point here.
    Maximal cliques are then enumerated for at most `clique_budget` seconds and
    the largest kept; since any clique is valid, stopping early is sound.

    The arc contraction bound of Yanasse, Becceneri & Soma (1999) is the
    contraction degeneracy below; the 1999 paper settles that they are the same
    bound (`reports/lower_bounds.md` §3).

    `satisfiability.expansion_bound` is available here through
    `expansion_budget` and is **off by default, deliberately**. It is a real
    improvement to the bound -- over all 6,376 certified optima it lowers the
    mean gap from 0.98 to 0.44 with zero violations -- and it makes the solver
    *slower on every one of the 25 hardest instances*. A floor only shortens a
    descent when it **equals** the optimum, since otherwise the same `k` are
    visited either way; and where it is exactly tight, the refutation it saves
    costs 0.2s while computing it costs 28s. Measured head to head in
    `reports/expansion_bound.md` §6. Pass a budget to use it for analysis.

    **Trust classes differ and are recorded.** The clique bound above is proved
    directly from the MOSP semantics. Contraction degeneracy and the expansion
    bound both rest on Yanasse's `MOSP = pathwidth(MOSP graph) + 1`, so a
    closure resting on either inherits it.
    """
    m = instance.n_patterns
    if m == 0:
        return 0

    # Trivial bound: the largest pattern, which is a clique by construction.
    best = max(len(instance.pattern_customers(p)) for p in range(m))

    if instance.n_customers <= best:
        return best  # cannot do better than the number of customers

    try:
        import networkx as nx

        from customer_inter.customer_graph import build_customer_graph

        graph = build_customer_graph(instance)

        deadline = time.time() + clique_budget
        for clique in nx.find_cliques(graph):
            if len(clique) > best:
                best = len(clique)
            if time.time() > deadline:
                break

        best = max(best, _contraction_degeneracy(graph) + 1)
    except Exception:  # noqa: BLE001 - a bound is an optimisation, never required
        pass

    try:
        from satisfiability.expansion_bound import mosp_lower_bound

        best = max(best, mosp_lower_bound(instance, max_t=expansion_t,
                                          time_budget=expansion_budget))
    except Exception:  # noqa: BLE001 - as above
        pass

    return best


def _contraction_degeneracy(graph, max_nodes: int = 400) -> int:
    """Contraction degeneracy (MMD+, least-c) of the MOSP graph.

    Repeatedly records the minimum degree, then contracts that vertex into the
    neighbour it shares fewest neighbours with. The largest minimum degree seen
    over the sequence is a lower bound on treewidth, hence on pathwidth.

    **This bound rests on Yanasse's MOSP = pathwidth(MOSP graph) + 1**, unlike
    the clique bound above, which is provable directly. A lower bound that is
    too high does not merely slow the search -- it makes the binary search start
    above the true optimum and return a wrong answer, which simulating the
    witness would not catch, because the witness does achieve the value
    reported. So this is a correctness dependency, not a tuning knob.

    It is checked against every known optimum in the corpus by
    tests/test_lower_bounds.py, which fails on any instance where the bound
    exceeds the optimum.
    """
    import networkx as nx

    if graph.number_of_nodes() > max_nodes:
        return 0  # contraction is O(n^3)-ish; skip rather than stall a solve

    working = nx.Graph(graph)
    best = 0
    while working.number_of_nodes() > 1:
        vertex = min(working.nodes, key=lambda x: working.degree(x))
        degree = working.degree(vertex)
        if degree == 0:
            working.remove_node(vertex)
            continue
        best = max(best, degree)
        neighbours = set(working[vertex])
        target = min(neighbours,
                     key=lambda x: len(neighbours & set(working[x])))
        working = nx.contracted_nodes(working, target, vertex, self_loops=False)
    return best


def _random_restarts(
    instance: MOSPInstance, n_random: int = 10, seed: int = 42
) -> tuple[int, list[int]]:
    """Best of identity, reverse, and `n_random` random permutations.

    Split out from `_upper_bound` so that the strategies in
    `satisfiability.heuristics` can share it — MCN, for instance, uses these
    restarts as a fallback start when its own construction happens to be worse.
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
            best_ord = list(perm)

    return best_val, best_ord


def _upper_bound(
    instance: MOSPInstance,
    n_random: int = 10,
    seed: int = 42,
    strategy: str | None = None,
) -> tuple[int, list[int]]:
    """Compute an upper bound on MOSP.

    Delegates to a named strategy from `satisfiability.heuristics`; the default
    constructs with least cost node and improves with tabu search. Pass
    `strategy="tabu"` for the original behaviour, which is retained unchanged.

    Returns:
        (upper_bound_value, best_ordering)
    """
    m = instance.n_patterns
    if m == 0:
        return 0, []

    from satisfiability.heuristics import upper_bound as _strategy_upper_bound

    return _strategy_upper_bound(instance, strategy=strategy, seed=seed)


def _tabu_search(
    instance: MOSPInstance,
    init_ordering: list[int],
    init_val: int,
    seed: int = 42,
    max_iterations: int = 500,
    tabu_tenure: int = 7,
    n_neighbors: int = 200,
) -> tuple[int, list[int]]:
    """Tabu search over pattern orderings using swap moves.

    Neighborhood: swap patterns at positions i and j.
    Tabu list: recently swapped positions (can't be swapped again for tabu_tenure steps).
    Uses sampled neighborhood for scalability on large instances.
    """
    m = len(init_ordering)
    if m <= 2:
        return init_val, init_ordering

    rng = random.Random(seed + 1)

    current = list(init_ordering)
    current_val = init_val
    best = list(init_ordering)
    best_val = init_val

    # Tabu list: position -> iteration when it becomes non-tabu
    tabu = {}

    stale = 0  # iterations without improvement

    for iteration in range(max_iterations):
        best_move_val = float("inf")
        best_move_i = -1
        best_move_j = -1

        # Sample neighborhood: random swaps
        for _ in range(min(n_neighbors, m * (m - 1) // 2)):
            i = rng.randint(0, m - 1)
            j = rng.randint(0, m - 2)
            if j >= i:
                j += 1

            i_tabu = tabu.get(i, 0) > iteration
            j_tabu = tabu.get(j, 0) > iteration

            # Apply swap
            current[i], current[j] = current[j], current[i]
            val = max_open_stacks(instance, current)
            current[i], current[j] = current[j], current[i]

            # Aspiration: accept tabu moves if they improve global best
            if (i_tabu or j_tabu) and val >= best_val:
                continue

            if val < best_move_val:
                best_move_val = val
                best_move_i = i
                best_move_j = j

        if best_move_i < 0:
            break

        # Apply the best move
        current[best_move_i], current[best_move_j] = current[best_move_j], current[best_move_i]
        current_val = best_move_val
        tabu[best_move_i] = iteration + tabu_tenure
        tabu[best_move_j] = iteration + tabu_tenure

        if current_val < best_val:
            best_val = current_val
            best = list(current)
            stale = 0
        else:
            stale += 1
            if stale > 100:
                break  # Early termination if stuck

    return best_val, best


def _solution_path(instance: MOSPInstance, solutions_dir: Path) -> Path:
    """Return the path for a cached solution file."""
    # Sanitize instance name for use as a filename
    name = instance.name or "unnamed"
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
    return solutions_dir / f"{safe_name}.json"


# How a cached value was established. A corpus that cannot tell a proof from a
# good guess is a liability, and both kinds are now present.
PROVENANCE_REFUTATION = "certified:refutation"  # SAT at k, UNSAT at k-1
PROVENANCE_BOUND = "certified:bound"            # SAT at k, and lower bound = k
PROVENANCE_RELAXATION = "certified:relaxation"  # as above, but the bound came
                                                # from a contraction, so the
                                                # claim also rests on Lemma 1
PROVENANCE_SOLUTION = "solution"                # witness only; optimality open

CERTIFIED = frozenset({PROVENANCE_REFUTATION, PROVENANCE_BOUND,
                       PROVENANCE_RELAXATION})

# Lower bounds are recorded with where they came from, because they do not all
# rest on the same thing. `clique` is proved directly here. `degeneracy` rests
# on MOSP = pathwidth + 1. `relaxation` rests additionally on Chu & Stuckey's
# Lemma 1 -- that contracting an edge relaxes the instance -- which this project
# has measured on 3,167 contractions and not proved, from a paper it does not
# hold. An optimality claim closed by a relaxation bound inherits that, which is
# why it gets its own provenance rather than being folded into certified:bound.
BOUND_SOURCES = ("clique", "degeneracy", "expansion", "relaxation")


def _save_solution(
    instance: MOSPInstance,
    val: int,
    ordering: list[int],
    solutions_dir: Path,
    provenance: str = PROVENANCE_SOLUTION,
    lower_bound: int | None = None,
    lower_bound_source: str | None = None,
) -> Path:
    """Save a solution, refusing to replace a better one already on disk.

    Saves are monotone in the value. Several things write here at once — the
    parallel runners, the ratchet, and any deduplication across instances that
    share a matrix — and without this a later worker could overwrite a better
    result with its own, silently losing the best value found. A cached solution
    is only ever replaced by one at least as good.
    """
    solutions_dir.mkdir(parents=True, exist_ok=True)
    path = _solution_path(instance, solutions_dir)

    kept_bound, kept_source = lower_bound, lower_bound_source
    if path.exists():
        try:
            existing = json.loads(path.read_text())
            # Lower bounds are monotone upwards, independently of the value:
            # a run that improves the witness must not discard a bound an
            # earlier run proved, and vice versa.
            previous = existing.get("lower_bound")
            if previous is not None and (kept_bound is None or previous > kept_bound):
                kept_bound, kept_source = previous, existing.get("lower_bound_source")

            if existing.get("mosp_value") is not None:
                if existing["mosp_value"] < val:
                    if kept_bound != previous:      # still worth recording
                        _rewrite_bound(path, existing, kept_bound, kept_source)
                    return path
                # An equal value that is already certified must not be demoted
                # to a bare solution by a later run that merely re-found it.
                if (existing["mosp_value"] == val
                        and existing.get("provenance") in CERTIFIED
                        and provenance not in CERTIFIED):
                    if kept_bound != previous:
                        _rewrite_bound(path, existing, kept_bound, kept_source)
                    return path
        except (json.JSONDecodeError, OSError):
            pass  # unreadable or truncated: overwrite it

    if kept_bound is not None and kept_bound > val:
        raise ValueError(
            f"{instance.name}: lower bound {kept_bound} exceeds the value {val}; "
            "one of them is wrong and the corpus must not record both")

    data = {
        "instance_name": instance.name,
        "n_customers": instance.n_customers,
        "n_patterns": instance.n_patterns,
        "mosp_value": val,
        "ordering": ordering,
        "provenance": provenance,
    }
    if kept_bound is not None:
        data["lower_bound"] = kept_bound
        if kept_source:
            data["lower_bound_source"] = kept_source
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def _rewrite_bound(path: Path, existing: dict, bound: int | None,
                   source: str | None) -> None:
    """Record a better lower bound on a solution whose value is not changing."""
    if bound is None:
        return
    existing["lower_bound"] = bound
    if source:
        existing["lower_bound_source"] = source
    path.write_text(json.dumps(existing, indent=2) + "\n")


def load_lower_bound(instance: MOSPInstance,
                     solutions_dir: Path = SOLUTIONS_DIR) -> tuple[int, str] | None:
    """The best lower bound recorded for this instance, and where it came from."""
    path = _solution_path(instance, solutions_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    bound = data.get("lower_bound")
    if bound is None:
        return None
    return int(bound), data.get("lower_bound_source", "")


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
        # Binary search: find the smallest k where MOSP <= k is SAT.
        # Invariant: UNSAT at lo-1, SAT at hi. We want the smallest SAT k.
        lo = k_lower
        hi = k_upper_val  # known SAT (greedy achieves this)
        best_sat_ordering = best_ordering

        while lo < hi:
            mid = (lo + hi) // 2
            result = _sat_decision(instance, mid)
            if result is not None:
                hi = mid
                best_sat_ordering = result
            else:
                lo = mid + 1

        # lo == hi == optimal k
        actual = max_open_stacks(instance, best_sat_ordering)
        val, ordering = actual, best_sat_ordering

    # Save solution. The binary search returns only once the interval has
    # closed, which means k-1 was refuted, so this is a certified optimum.
    if solutions_dir is not None and instance.name:
        _save_solution(instance, val, ordering, solutions_dir,
                       provenance=PROVENANCE_REFUTATION)

    return val, ordering


# Which complete decision procedure solves an instance unless told otherwise.
#
# It was the SAT encoding until 2026-09-22, when the two were finally raced
# against each other: over 20 hard `Random` instances at densities 2 and 8, with
# SAT on kissat404 -- the backend measured at 6/6 on hard refutations -- the
# customer search won **63 of 63** decision calls and the SAT path certified
# none inside a minute. On a broad corpus sample it wins too, by an order of
# magnitude on instances both settle in under a second.
#
# The reason nobody noticed is in the records: the direct SAT path has a solved
# row for 6,226 instances and `csearch` has a ledger row for 147, and the
# overlap is **zero**. `csearch` was only ever pointed at what SAT had already
# failed, so the two had no head-to-head history and the belief that they fail
# on disjoint instance sets was inherited rather than measured
# (`reports/learned_search.md` §3).
DEFAULT_PROCEDURE = "csearch"
PROCEDURES = ("csearch", "sat")


def solve_mosp_exact(
    instance: MOSPInstance,
    *,
    procedure: str = DEFAULT_PROCEDURE,
    solutions_dir: Path | str | None = SOLUTIONS_DIR,
    upper_strategy: str = "cs-dfs",
    time_budget: float | None = None,
    max_nodes: int | None = None,
) -> tuple[int, list[int]]:
    """Solve MOSP to optimality with the project's default decision procedure.

    This is the entry point to reach for. `solve_mosp_sat` remains what its name
    says -- the SAT encoding, reachable here as `procedure="sat"` -- and is worth
    running when a checkable proof object matters, since a refutation from the
    customer search is not a DRAT proof (`CLAUDE.md`, item 7).

    The value returned is `max_open_stacks` of the ordering, re-simulated on the
    original instance rather than taken from the search's own accounting: the
    closing-order measure can over-charge, and a witness that does not simulate
    to its claimed value is a bug that must not reach the corpus.

    Args:
        procedure: "csearch" (default) or "sat".
        upper_strategy: the named heuristic supplying the starting upper bound.
        time_budget: seconds for the descent. Without one the search runs to a
            refutation, which on the hardest instances is hours.
        max_nodes: node cap for a single decision call.

    Returns:
        `(value, pattern_ordering)`. The value is optimal when the descent
        refuted `value - 1` or met the lower bound; when a budget ran out it is
        an upper bound, and the provenance recorded on disk says which.
    """
    if procedure not in PROCEDURES:
        raise ValueError(
            f"unknown procedure {procedure!r}; available: {', '.join(PROCEDURES)}")
    if procedure == "sat":
        return solve_mosp_sat(instance, solutions_dir=solutions_dir)

    from satisfiability.customer_search import solve as csearch_solve
    from satisfiability.heuristics import product_order_from_customers

    if solutions_dir is not None:
        solutions_dir = Path(solutions_dir)
        cached = _load_solution(instance, solutions_dir)
        if cached is not None:
            return cached

    if instance.n_patterns == 0:
        return 0, []
    if instance.n_patterns == 1:
        return max(len(instance.pattern_customers(0)), 0), [0]

    # The recorded bound can exceed a freshly computed one -- a relaxation may
    # have proved something this call would not -- and the descent ends the
    # moment its value reaches the floor, with no refutation needed.
    cheap = _lower_bound(instance)
    floor, source = cheap, "degeneracy"
    if solutions_dir is not None:
        recorded = load_lower_bound(instance, solutions_dir)
        if recorded and recorded[0] > cheap:
            floor, source = recorded

    result = csearch_solve(instance, lower=floor, upper_strategy=upper_strategy,
                           time_budget=time_budget, max_nodes=max_nodes)
    if not result.order:
        # No closing order means the descent never improved on its start, which
        # only happens when it was handed one; it is not handed one here.
        _, ordering = upper_bound_ordering(instance, upper_strategy)
    else:
        ordering = product_order_from_customers(instance, result.order)

    achieved = max_open_stacks(instance, ordering)
    if result.order and achieved != result.value:
        raise AssertionError(
            f"{instance.name}: search claimed {result.value}, "
            f"ordering achieves {achieved}")

    if solutions_dir is not None and instance.name:
        provenance = {"refutation": PROVENANCE_REFUTATION,
                      "bound": PROVENANCE_BOUND,
                      "": PROVENANCE_SOLUTION}[result.proof]
        if result.proof == "bound" and source == "relaxation":
            provenance = PROVENANCE_RELAXATION
        _save_solution(instance, achieved, ordering, solutions_dir,
                       provenance=provenance, lower_bound=floor,
                       lower_bound_source=source)

    return achieved, ordering


def upper_bound_ordering(instance: MOSPInstance, strategy: str):
    """`(value, ordering)` from a named heuristic, without importing at module scope."""
    from satisfiability.heuristics import upper_bound

    return upper_bound(instance, strategy)


def decide_mosp(
    instance: MOSPInstance,
    k: int,
    backend: str = SAT_BACKEND,
) -> list[int] | None:
    """Decide "MOSP(instance) <= k?", reducing the instance before encoding.

    Two reductions from `mosp.preprocess` apply, in this order:

    - **Decomposition.** The components of the MOSP graph share no customer and
      no product, so `MOSP(I) <= k` exactly when every component satisfies it,
      and a refutation on any one component refutes the whole instance. Each
      component is encoded separately, which is what makes this worth doing at
      all: the formula is superlinear in the instance, so two halves cost far
      less than the whole.
    - **Pattern dominance.** Within a component, a product whose customers are a
      subset of another product's is dropped and reinserted next to its
      dominator afterwards, at no cost to the count.

    Both preserve the optimum, so an UNSAT here refutes the original instance
    and is safe to record as a certified bound. Measured firing rates on the
    6,376-instance corpus: dominance on 3,409 of them, removing 17,699 columns;
    decomposition on 154. On the 148 unproven Random instances the rates are 93
    and **zero** -- Chu & Stuckey (2009) deliberately discard decomposable
    instances from that generator's output, so its absence there is by design.

    Returns a witness ordering of the *original* instance if satisfiable, None
    otherwise.
    """
    from pysat.solvers import Solver

    from mosp.preprocess import (
        components, lift_component_orderings, remove_dominated_patterns)

    parts, free = components(instance)
    if not parts:
        return list(range(instance.n_patterns))

    orderings: list[list[int]] = []
    for part in parts:
        reduction = remove_dominated_patterns(part.instance)
        cnf, pool, m = encode_mosp_decision(reduction.instance, k)
        with Solver(name=backend, bootstrap_with=cnf.clauses) as solver:
            if not solver.solve():
                return None
            order = extract_ordering(solver.get_model(), pool, m)
        orderings.append(reduction.lift(order))

    return lift_component_orderings(parts, orderings, free)


def _sat_decision(
    instance: MOSPInstance,
    k: int,
) -> list[int] | None:
    """Test if MOSP(instance) <= k using SAT encoding.

    Returns a witness ordering if satisfiable, None otherwise.
    """
    return decide_mosp(instance, k)
