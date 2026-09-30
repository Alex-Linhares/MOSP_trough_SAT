"""Closing-order search: a complete search over vertex closing orders that
decides `pathwidth(G) <= w`.

The algorithm is Chu & Stuckey's (2009, §2-3) "customer search" for the
Minimization of Open Stacks Problem, ported from `src/customer_search.py` (the MOSP project's
Python reference implementation, kept verbatim in this repo for diffing). The
port changes the *input* and nothing else: the MOSP instance is replaced by the
self-inclusive neighbourhood masks of a graph (`graph.masks_from_graph`), and
"MOSP <= k" becomes "pathwidth <= k - 1". Given the same masks and `k`, this
search visits the same nodes in the same order as the MOSP one -- the node
counts are asserted identical in `tests/test_identity_mosp.py`.

**The measure.** A state is the set `S` of vertices already closed. `O(S)` is
the set opened so far, the union of `N[v]` over `v ∈ S`. Closing `v` next costs
`|O(S ∪ {v}) - S|` = boundary of `S ∪ {v}` plus one. The peak over a closing
order is the vertex separation of the order plus one, so `decide(masks, k)`
answers `pw(G) <= k - 1`; `decide_pathwidth(G, w)` does the shift.

**In commitment terms** (Tamaki 2011; Kitsunai et al. 2016 §3): free moves are
the *fullset* rule (Prop. 3) and the definite move is a depth-1 commitment
(Corollary 2 with a one-vertex extension). The subset rule, old move and the
memo are dominance / DP-state arguments, not commitments.

**The rules.** Each is a dominance: it discards branches that cannot beat the
branches kept, so a refutation still refutes.

- *free moves*: a remaining vertex whose whole closed neighbourhood is already
  opened costs nothing to close and is closed immediately.
- *subset* (their §2): if `o(u,S) ⊆ o(v,S)` then closing `u` first is never
  worse, so `v` leaves the candidate set.
- *definite move* (their Theorem 1): if `close(q,S) >= open(q,S)` and
  `S ++ [q]` is playable, every solution extending `S` has one extending
  `S ++ [q]`, so **all** other branches go.
- *old move* (their Theorem 3): if `q` was already searched at an ancestor and
  inserting `q` back there leaves the sequence playable, that subtree has been
  seen and `q` goes. Maintained as a set `Q(S)` in `O(n)` per node.
- *better move* (their Theorem 2) exists only in the MOSP project's C port and
  is not in this Python.

**Old move and the memo, together.** As in the reference: the Python refuses
the combination (a failure reached with old-move pruning is a property of the
path, not of `S` alone), and drops the memo when both are asked for.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import networkx as nx

from pathwidth.graph import FAN_ORDERS, fan_sort_key, masks_from_graph


@dataclass
class Decision:
    """The answer to "pathwidth <= w?" (or "MOSP <= k?"), and what it cost.

    `status` is "sat" with a closing order, "unsat" -- a genuine refutation, the
    whole space having been searched -- or "unknown", which means the node or
    time budget ran out and nothing was proved either way. A restricted search
    never returns "unsat": the restriction discards branches it cannot justify,
    so exhausting what remains proves nothing.

    `order` is over vertex indices `0..n-1` (mask positions). `decide_pathwidth`
    translates it back to the graph's labels.
    """

    status: str
    order: list[int] | None
    nodes: int


def decide(
    masks: Sequence[int],
    k: int,
    *,
    restrict: bool = False,
    subset_rule: bool = True,
    definite_move: bool = True,
    old_move: bool = True,
    memo: bool = True,
    max_nodes: int | None = None,
    deadline: float | None = None,
    memo_limit: int = 4_000_000,
    branch: "Callable[[int, int, list[tuple[int, int]]], list[tuple[int, int]]] | None" = None,
    expansion_prune: bool = False,
    fan_order: str = "index",
    native: bool = True,
    better_move: bool = False,
    better_move_dominators: int = 4,
) -> Decision:
    """Decide "max over closing orders of `|O(S ∪ {v}) − S|` <= k?" on `masks`.

    On a graph this is `pathwidth <= k − 1`; on a MOSP customer graph it is
    `MOSP <= k`. Vertices with an empty mask are inactive and never appear in
    a state (this is how the MOSP reference treats customers without products;
    `masks_from_graph` never produces one).

    Args:
        masks: self-inclusive neighbourhood bitmasks over vertices `0..n-1`.
        k: the budget.
        restrict: branch only on `R ∩ O(S)`, vertices already opened. This is
            Chu & Stuckey's `ub_MOSP` (§3.4) and is **not sound** -- it answers
            "sat" or "unknown", never "unsat".
        subset_rule, definite_move, old_move: the dominance relations above. The
            flags exist so the exhaustive tests can vary one at a time.
            `old_move` cannot be combined with `memo`, for the reason above.
        memo: record states already refuted, their `prob[S]`. The state is
            `S` alone -- `O(S)` is a function of it -- so a failure at `S` is a
            failure by whatever path reached it.
        max_nodes: abort after this many branches and return "unknown".
        deadline: `time.monotonic()` value to stop at, checked every 4,096
            nodes.
        memo_limit: stop growing the memo past this many states.
        expansion_prune: cut a whole node when even the best continuation must
            exceed `k`, by the neighbourhood-expansion argument applied to the
            vertices still remaining (MOSP `reports/expansion_bound.md`).
        branch: reorder the surviving candidates at each node. Called with
            `(closed, opened, playable)` where `playable` is the `(cost,
            vertex)` list the dominance rules left, and must return a
            permutation of it -- dropping a candidate would make a refutation
            unsound, and the caller is trusted not to. Default is cheapest first.
        fan_order: how equal-cost candidates are ordered; `"index"` (default)
            or `"degree"`. Changes which branches are visited first, never
            which are visited.
        native: use the C port (`pathwidth/native.py`) when it applies. It
            visits the same nodes in the same order, about 120x faster; up to
            1024 vertices. Set
            False to force the Python, which is the reference implementation.
            `branch` and `expansion_prune` force the Python: the C has neither.
        better_move, better_move_dominators: Chu & Stuckey's Theorem 2, which
            exists only in the C. Ignored on the Python path.

    Returns:
        A `Decision`. The "sat" order closes every active vertex.
    """
    if fan_order not in FAN_ORDERS:
        raise ValueError(f"fan_order must be one of {FAN_ORDERS}, not {fan_order!r}")

    if native and branch is None and not expansion_prune:
        from pathwidth.native import decide_native
        answer = decide_native(
            masks, k, restrict=restrict, subset_rule=subset_rule,
            definite_move=definite_move, old_move=old_move, memo=memo,
            better_move=better_move, better_move_dominators=better_move_dominators,
            max_nodes=max_nodes, memo_limit=memo_limit,
            seconds=None if deadline is None else max(0.0, deadline - time.monotonic()),
            fan_order=fan_order)
        if answer is not None:
            return answer

    if old_move and memo:
        # The reference keeps the stricter reading -- the memo is dropped rather
        # than combined -- so that the two implementations are not both resting
        # on the same assumption.
        memo = False

    n = len(masks)
    active = [v for v in range(n) if masks[v]]

    full = 0
    for vertex in active:
        full |= 1 << vertex

    if not active:
        return Decision("sat", [], 0)

    # The search recurses once per closed vertex, so its depth is the number of
    # active vertices; Python's default limit of 1000 is too low for the larger
    # VSPLIB and named graphs that fall through to this path.
    needed = 2 * len(active) + 1000
    if sys.getrecursionlimit() < needed:
        sys.setrecursionlimit(needed)

    path: list[int] = []
    refuted: set[int] = set()
    state = {"nodes": 0, "aborted": False}

    def free_moves(closed: int, opened: int) -> int:
        """Vertices whose neighbourhood is wholly opened: free to close now.

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
            # vertex has to be opened before anything can close.
            if narrowed:
                candidates = narrowed

        # o(v,S) = N[v] - O(S), the vertices closing v would newly open.
        opens: dict[int, int] = {}
        bits = remaining
        while bits:
            bit = bits & -bits
            bits ^= bit
            vertex = bit.bit_length() - 1
            opens[vertex] = masks[vertex] & ~opened

        # Expansion cut. Closing any `t` of the remaining vertices costs at
        # least `open_now + m_(t) - t + 1`, where `m_(t)` is the t-th smallest
        # number of vertices a single remaining vertex would newly open: any
        # `t` distinct vertices include one whose own count is at least that.
        # `t = 1` is the cost cut below; `t >= 2` is what this adds. The value
        # depends only on `closed` -- `opened` is a function of it -- so a state
        # refuted here is refuted by whatever path reached it, and the memo
        # stays sound.
        if expansion_prune and opens:
            open_now = (opened & ~closed).bit_count()
            sizes = sorted(mask.bit_count() for mask in opens.values())
            floor = 0
            for step, size in enumerate(sizes, start=1):
                need = size - step + 1
                if need > floor:
                    floor = need
            if open_now + floor > k:
                if memo and len(refuted) < memo_limit:
                    refuted.add(closed)
                del path[mark:]
                return False

        playable: list[tuple[int, int]] = []
        bits = candidates
        while bits:
            bit = bits & -bits
            bits ^= bit
            vertex = bit.bit_length() - 1
            cost = ((opened | masks[vertex]) & ~closed).bit_count()
            if cost <= k:
                playable.append((cost, vertex))

        if playable and (subset_rule or definite_move):
            playable = _apply_dominance(
                playable, opens, subset_rule, definite_move)

        if fan_order == "index":
            playable.sort()
        else:
            playable.sort(key=fan_sort_key(fan_order, masks, remaining))
        if branch is not None and len(playable) > 1:
            playable = branch(closed, opened, playable)
        for _, vertex in playable:
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
            path.append(vertex)
            inherited = 0
            if old_move and seen:
                # Q(S ++ [v]) keeps those q whose reinsertion still leaves this
                # last move playable; everything earlier is playable already by
                # q being in Q(S). Auto-closures can only lower that cost, so
                # checking the move alone is conservative in the safe direction.
                bits = seen
                while bits:
                    bit = bits & -bits
                    bits ^= bit
                    other = bit.bit_length() - 1
                    cost = ((opened | masks[other] | masks[vertex])
                            & ~(closed | bit)).bit_count()
                    if cost <= k:
                        inherited |= bit
            if search(closed | (1 << vertex), opened | masks[vertex],
                      inherited):
                return True
            del path[here:]
            if state["aborted"]:
                del path[mark:]
                return False
            # This branch is now searched, so a later sibling that could play it
            # instead would be repeating it.
            seen |= 1 << vertex

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

    `close(q,S) = |{d ∉ S : o(d,S) ⊆ o(q,S)}|` counts the vertices that closing
    `q` releases: `d` is finished once every vertex it touches has been opened,
    which after `q` means `o(d,S) ⊆ o(q,S)`. Both `close` and the subset test
    fall out of the same pass over the remaining vertices.
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
class GraphDecision:
    """`Decision` translated to graph labels: `order` is a closing order of
    `G.nodes`, and `width` is the vertex separation the search certified
    (`k - 1`) when `status == "sat"`."""

    status: str
    order: list | None
    nodes: int
    width: int | None


def decide_pathwidth(G: nx.Graph, width: int, **kwargs: object) -> GraphDecision:
    """Decide `pathwidth(G) <= width` by customer search on `G`'s masks.

    `width < 0` is unsatisfiable for any non-empty graph and is answered
    without searching. Keyword arguments are those of `decide`.
    """
    masks, labels = masks_from_graph(G)
    if not labels:
        return GraphDecision("sat", [], 0, -1 if width < 0 else width)
    if width < 0:
        return GraphDecision("unsat", None, 0, None)
    answer = decide(masks, width + 1, **kwargs)
    order = None if answer.order is None else [labels[i] for i in answer.order]
    return GraphDecision(answer.status, order, answer.nodes,
                         width if answer.status == "sat" else None)
