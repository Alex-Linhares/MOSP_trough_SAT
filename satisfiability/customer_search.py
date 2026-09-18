"""Complete search over customer closing orders (Chu & Stuckey 2009, §2-3).

An alternative to the SAT encoding for deciding "MOSP(I) <= k?". It searches the
space the plan's §0.1 established is the right one -- orders in which customers'
stacks *close* -- rather than the space of product sequences, and prunes it with
the dominance relations of their §3, none of which can be written as clauses
because every one conditions on the partial sequence already committed.

Why this exists alongside the SAT path: their Table 1 reports the complete
search closing 125-125-6, 125-125-8 and 125-125-10 in 9 s, 0.19 s and 0.02 s,
against our SAT refutations, which do not return on those instances at all.
The densities where their search is fastest are the ones holding most of our
open gap. It is also the reverse of the SAT path's profile -- their search is
slowest exactly where sparsity makes the branching factor explode, which is what
their relaxation technique (plan item 5) exists to repair.

**The measure.** A state is the set `S` of customers already closed. `O(S)` is
the set opened so far, the union of the neighbourhoods `N(c)` over `c ∈ S`, with
`N` self-inclusive. Closing `c` next costs `|O(S ∪ {c}) - S|`: the stacks opened
but not yet closed, counting `c` itself, which is still open at the moment it
closes. `min` over closing orders of the peak of this equals the true optimum --
measured 400/400 against exhaustive search, `reports/chu_stuckey_plan.md` §0.1.

**Free moves.** A remaining customer whose whole neighbourhood is already opened
costs nothing to close and is closed immediately. This is the `open = 0` case of
their Theorem 1 and it is what keeps the measure above honest: without it, a
customer whose products are all made would keep counting as an open stack, and
the "close" counts the dominance rules below are stated in terms of would be
wrong.

**The rules.** Each is a dominance: it discards branches that cannot beat the
branches kept, so a refutation still refutes.

- *subset* (their §2): if `o(cᵢ,S) ⊆ o(cⱼ,S)` then closing `cᵢ` first is never
  worse, since closing `cⱼ` opens everything `cᵢ` would have and closing `cᵢ`
  can only help `cⱼ` -- so `cⱼ` leaves the candidate set.
- *definite move* (their Theorem 1): if `close(q,S) ≥ open(q,S)` and `S ++ [q]`
  is playable, then every solution extending `S` has one extending `S ++ [q]`,
  so **all** other branches go.
- *old move* (their Theorem 3): if `q` was already searched at an ancestor and
  inserting `q` back there leaves the sequence playable, that subtree has been
  seen and `q` goes. Maintained as a set `Q(S)` in `O(|C|)` per node.

Theorem 2 ("better move") is not implemented: its condition ranges over pairs of
candidates and needs `close(q, S ∪ {r})` for each, which is `O(|R|³)` per node
where Theorem 1 -- its special case, where `q` beats every `r` at once -- is
`O(|R|²)`. See `reports/customer_search.md`.

**Old move and the memo do not compose.** A failure reached with old-move
pruning depends on which branches an *ancestor* had already searched, so it is a
property of the path, not of `S`, and recording it against `S` alone would
refute states that are not refuted. Chu & Stuckey report nogood recording worth
about 1.0x once old move is on, so the two are alternatives rather than a loss:
enabling `old_move` turns `memo` off, and `decide` raises if both are asked for.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import _neighbour_masks, product_order_from_customers


@dataclass
class Decision:
    """The answer to "MOSP(I) <= k?", and what it cost to get it.

    `status` is "sat" with a closing order, "unsat" -- a genuine refutation, the
    whole space having been searched -- or "unknown", which means the node
    budget ran out and nothing was proved either way. A restricted search never
    returns "unsat": the restriction discards branches it cannot justify, so
    exhausting what remains proves nothing.
    """

    status: str
    order: list[int] | None
    nodes: int


def decide(
    instance: MOSPInstance,
    k: int,
    *,
    restrict: bool = False,
    subset_rule: bool = True,
    definite_move: bool = True,
    old_move: bool = False,
    memo: bool = True,
    max_nodes: int | None = None,
    deadline: float | None = None,
    memo_limit: int = 4_000_000,
) -> Decision:
    """Decide "MOSP(instance) <= k?" by searching customer closing orders.

    Args:
        k: the budget on simultaneously open stacks.
        restrict: branch only on `R ∩ O(S)`, customers already open. This is
            their `ub_MOSP` (§3.4) and is **not sound** -- it answers "sat" or
            "unknown", never "unsat".
        subset_rule, definite_move, old_move: the dominance relations above. The
            flags exist so the exhaustive tests can vary one at a time.
            `old_move` cannot be combined with `memo`, for the reason above.
        memo: record states already refuted, their `prob[S]`. The state is
            `S` alone -- `O(S)` is a function of it -- so a failure at `S` is a
            failure by whatever path reached it.
        max_nodes: abort after this many branches and return "unknown".
        deadline: `time.monotonic()` value to stop at, checked every 4,096
            nodes. Same effect as `max_nodes`, in the unit a caller with a
            budget actually has.
        memo_limit: stop growing the memo past this many states. The table is
            what bounds memory here, and an unbounded one on a 125-customer
            refutation will take the machine down.

    Returns:
        A `Decision`. The "sat" order closes every customer with a non-empty
        product set; customers needing nothing are omitted, as they never open.
    """
    if old_move and memo:
        raise ValueError(
            "old_move and memo cannot both be on: an old-move failure depends "
            "on the path taken to the state, and the memo is keyed on the "
            "state alone")

    masks = _neighbour_masks(instance)
    active = [c for c in range(instance.n_customers) if instance.customer_patterns(c)]

    full = 0
    for customer in active:
        full |= 1 << customer

    if not active:
        return Decision("sat", [], 0)

    path: list[int] = []
    refuted: set[int] = set()
    state = {"nodes": 0, "aborted": False}

    def free_moves(closed: int, opened: int) -> int:
        """Customers whose neighbourhood is wholly opened: free to close now.

        Closing one opens nothing, so the peak cannot rise, and it can only
        release later steps. Closing them does not change `O`, so no further
        free moves appear and one pass suffices.
        """
        found = 0
        bits = full & ~closed
        while bits:
            bit = bits & -bits
            bits ^= bit
            if masks[bit.bit_length() - 1] & ~opened == 0:
                found |= bit
        return found

    def search(closed: int, opened: int, seen: int = 0) -> bool:
        """`seen` is Q(S): moves an ancestor already searched that could be
        played here instead, without making the sequence unplayable."""
        mark = len(path)

        free = free_moves(closed, opened)
        if free:
            bits = free
            while bits:
                bit = bits & -bits
                bits ^= bit
                path.append(bit.bit_length() - 1)
            closed |= free

        if closed == full:
            return True
        if memo and closed in refuted:
            del path[mark:]
            return False

        remaining = full & ~closed
        seen &= remaining
        candidates = remaining & ~seen if old_move else remaining
        if restrict:
            narrowed = remaining & opened
            # An empty frontier means a disconnected remainder, where some
            # stack has to be opened before anything can close.
            if narrowed:
                candidates = narrowed

        # o(c,S) = N(c) - O(S), the stacks closing c would newly open.
        opens: dict[int, int] = {}
        bits = remaining
        while bits:
            bit = bits & -bits
            bits ^= bit
            customer = bit.bit_length() - 1
            opens[customer] = masks[customer] & ~opened

        playable: list[tuple[int, int]] = []
        bits = candidates
        while bits:
            bit = bits & -bits
            bits ^= bit
            customer = bit.bit_length() - 1
            cost = ((opened | masks[customer]) & ~closed).bit_count()
            if cost <= k:
                playable.append((cost, customer))

        if playable and (subset_rule or definite_move):
            playable = _apply_dominance(
                playable, opens, subset_rule, definite_move)

        playable.sort()
        for _, customer in playable:
            state["nodes"] += 1
            if max_nodes is not None and state["nodes"] > max_nodes:
                state["aborted"] = True
                del path[mark:]
                return False
            if (deadline is not None and state["nodes"] % 4096 == 0
                    and time.monotonic() > deadline):
                state["aborted"] = True
                del path[mark:]
                return False

            here = len(path)
            path.append(customer)
            inherited = 0
            if old_move and seen:
                # Q(S ++ [c]) keeps those q whose reinsertion still leaves this
                # last move playable; everything earlier is playable already by
                # q being in Q(S). Auto-closures can only lower that cost, so
                # checking the move alone is conservative in the safe direction.
                bits = seen
                while bits:
                    bit = bits & -bits
                    bits ^= bit
                    other = bit.bit_length() - 1
                    cost = ((opened | masks[other] | masks[customer])
                            & ~(closed | bit)).bit_count()
                    if cost <= k:
                        inherited |= bit
            if search(closed | (1 << customer), opened | masks[customer],
                      inherited):
                return True
            del path[here:]
            if state["aborted"]:
                del path[mark:]
                return False
            # This branch is now searched, so a later sibling that could play it
            # instead would be repeating it.
            seen |= 1 << customer

        # Only a genuine exhaustion may be recorded: a budget abort has not
        # refuted anything, and memoising it would turn a timeout into a
        # permanent wrong answer.
        if memo and not state["aborted"] and len(refuted) < memo_limit:
            refuted.add(closed)
        del path[mark:]
        return False

    found = search(0, 0)
    if found:
        return Decision("sat", list(path), state["nodes"])
    if state["aborted"] or restrict:
        return Decision("unknown", None, state["nodes"])
    return Decision("unsat", None, state["nodes"])


def _apply_dominance(
    playable: list[tuple[int, int]],
    opens: dict[int, int],
    subset_rule: bool,
    definite_move: bool,
) -> list[tuple[int, int]]:
    """Cut the candidate list by the two dominance relations.

    `close(q,S) = |{d ∉ S : o(d,S) ⊆ o(q,S)}|` counts the stacks that closing
    `q` releases: `d` is finished once every stack it touches has been opened,
    which after `q` means `o(d,S) ⊆ o(q,S)`. Both `close` and the subset test
    fall out of the same pass over the remaining customers.
    """
    if definite_move:
        for cost, q in playable:
            own = opens[q]
            opened_by_q = own.bit_count()
            closed_by_q = sum(1 for other in opens.values() if other & ~own == 0)
            if closed_by_q >= opened_by_q:
                # q is at least as good as anything else here, so every other
                # branch can go.
                return [(cost, q)]

    if not subset_rule:
        return playable

    kept = []
    for cost, q in playable:
        own = opens[q]
        dominated = any(
            other & ~own == 0 and (other != own or d < q)
            for d, other in opens.items() if d != q
        )
        if not dominated:
            kept.append((cost, q))
    # Every candidate dominated by a non-candidate (possible only under the
    # frontier restriction) would empty the list; keep the original in that case.
    return kept or playable


@dataclass
class Solution:
    """What a descent established, and how -- which is not the same question.

    `proof` is "refutation" when the search exhausted `value - 1`, "bound" when
    `value` met a lower bound that needed no refutation, and empty when the
    descent ran out of budget. The last is still an upper bound worth keeping
    but is not an optimality claim, which is the distinction the `provenance`
    field in `solutions/` exists to preserve.

    `order` is empty when `solve` was given an `upper` it never improved on; the
    caller keeps whatever witness it already had in that case.
    """

    value: int
    order: list[int]
    proof: str
    nodes: int
    seconds: float

    @property
    def proved(self) -> bool:
        return bool(self.proof)


def solve(
    instance: MOSPInstance,
    *,
    upper: int | None = None,
    lower: int = 0,
    max_nodes: int | None = None,
    time_budget: float | None = None,
    **kwargs: object,
) -> Solution:
    """Descend `k` with the complete search until it refutes or runs out.

    Each satisfiable answer is re-simulated on the product order it induces
    rather than trusted at `k`: the search's own measure can over-charge an
    order no product sequence realises, so the witness is often worth more than
    the `k` it was found at, and the next step starts from what it actually
    achieves. That is also the point at which a wrong witness would be caught.

    Args:
        upper: where to start. Defaults to the `cs-dfs` heuristic bound.
        lower: a known lower bound. Reaching it ends the descent with a proof
            and no refutation, since nothing below it can be satisfiable.
        max_nodes, time_budget: per-`k` budgets. An exhausted budget stops the
            descent with `proved` false.

    Returns:
        A `Solution` whose `order` is a customer closing order; pass it through
        `product_order_from_customers` for a production sequence.
    """
    from satisfiability.heuristics import restricted_dfs

    started = time.monotonic()
    nodes = 0

    if upper is None:
        _, ordering = restricted_dfs(instance)
        order = _closing_order(instance, ordering)
        value = max_open_stacks(instance, ordering)
    else:
        value = upper
        order = []

    if value <= lower:
        return Solution(value, order, "bound", 0, time.monotonic() - started)

    k = value - 1
    while k >= lower:
        deadline = None if time_budget is None else started + time_budget
        answer = decide(instance, k, max_nodes=max_nodes, deadline=deadline, **kwargs)
        nodes += answer.nodes

        if answer.status == "unsat":
            # The refutation says the optimum is above k. Claiming it *is*
            # k + 1 needs a witness that achieves k + 1, and the witness in
            # hand is only trusted at the value it simulates to. The search
            # scores closing orders, not the product sequences they build, and
            # the two agree on every instance measured -- but a proof that
            # rests on "measured" rather than "checked here" is the kind this
            # project has had to retract before.
            if value == k + 1:
                return Solution(value, order, "refutation", nodes,
                                time.monotonic() - started)
            return Solution(value, order, "", nodes, time.monotonic() - started)
        if answer.status == "unknown":
            return Solution(value, order, "", nodes, time.monotonic() - started)

        found = answer.order
        achieved = max_open_stacks(
            instance, product_order_from_customers(instance, found))
        if achieved < value:
            value, order = achieved, found
        k = min(k, achieved) - 1

    # The descent walked down to the lower bound: nothing below it can be
    # satisfiable, so no refutation is needed.
    return Solution(value, order, "bound", nodes, time.monotonic() - started)


def _closing_order(instance: MOSPInstance, ordering: list[int]) -> list[int]:
    """The closing order a product sequence induces, customers by last product."""
    position = {pattern: i for i, pattern in enumerate(ordering)}
    active = [c for c in range(instance.n_customers) if instance.customer_patterns(c)]
    return sorted(
        active,
        key=lambda c: (max(position[p] for p in instance.customer_patterns(c)), c),
    )
