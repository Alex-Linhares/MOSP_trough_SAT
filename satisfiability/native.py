"""The C port of the customer search, and the rules for when to trust it.

`satisfiability/customer_search.py` is the reference implementation and stays
that way: it is the one the exhaustive tests are written against, and where the
two disagree it is right. This module compiles `customer_search.c` and calls it
through `ctypes`, for the one reason that matters -- Chu & Stuckey close
125-125-2 in about 19 minutes with this algorithm in C++, and the Python does
not close it at all. Most of that gap is the language.

It declines rather than guesses. The Python is used instead when:

- the shared library will not build (no compiler, or a build error);
- the instance has more than 128 active customers, which is what fits in the
  `__int128` the C uses for a customer set.

All four dominance rules are now in the C, which is what Chu & Stuckey run:
they report "better move", "old move" and nogood recording on together. Old
move lived only in the Python until 2026-09-21, which meant asking for it
silently gave up the C's 120x -- so nothing used it.
`better_move` is Theorem 2, which existed only here until 2026-10-01: it is O(|R|^3) per node
against Theorem 1's O(|R|^2), which was the wrong trade in Python and may be
the right one at two million nodes a second. `better_move_dominators` caps how
many candidates are tried as the dominating `q`; a subset prunes less but never
wrongly, since the theorem justifies each pruning on its own.

The fallback is silent by design: a caller asking for a decision wants the
right answer, and both paths give the same one. `native_available()` reports
which is in use for the benchmarks that care.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import threading
from pathlib import Path

from mosp.instance import MOSPInstance
from satisfiability.customer_search import FAN_ORDERS, Decision
from satisfiability.heuristics import _neighbour_masks

_SOURCE = Path(__file__).with_name("customer_search.c")

# Bits of the C's `better_move_variant`; must match customer_search.c.
BM_OLD_CLOSE_COUNT = 1
BM_OLD_RULE_ORDER = 2
BM_SUBSET_RESTRICTED = 4
_LIBRARY = Path(__file__).with_name("_customer_search.so")
_MAX_CUSTOMERS = 128

_lock = threading.Lock()
_library: "ctypes.CDLL | None" = None
_build_error: str | None = None


def _build() -> bool:
    """Compile the shared library. Returns whether it is usable afterwards."""
    global _build_error
    if _LIBRARY.exists() and _LIBRARY.stat().st_mtime >= _SOURCE.stat().st_mtime:
        return True
    # Compiled beside the target and renamed into place: a process that has
    # the old library mapped keeps its inode, and no process ever opens a
    # half-written file. A multi-day `benchmarks.recertify` run is the process
    # this protects.
    scratch = _LIBRARY.with_name(_LIBRARY.name + f".build-{os.getpid()}")
    try:
        subprocess.run(
            ["gcc", "-O3", "-march=native", "-shared", "-fPIC",
             "-o", str(scratch), str(_SOURCE)],
            check=True, capture_output=True, timeout=120)
        os.replace(scratch, _LIBRARY)
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        _build_error = f"{type(exc).__name__}: {exc}"
        try:
            scratch.unlink()
        except OSError:
            pass
        return False


def _load() -> "ctypes.CDLL | None":
    global _library
    with _lock:
        if _library is not None:
            return _library
        if not _SOURCE.exists() or not _build():
            return None
        try:
            lib = ctypes.CDLL(str(_LIBRARY))
        except OSError as exc:            # built for another machine, say
            global _build_error
            _build_error = str(exc)
            return None
        # `cs_decide_fan` is `cs_decide` plus the fan-order flag; the C keeps
        # the old entry point for processes that loaded the library before
        # the flag existed.
        # `cs_decide_variant` adds the better-move variant bits (item 04 of
        # loop0004, reports/ml_nature.md §31); `cs_decide_fan` and `cs_decide`
        # stay as they were for processes that loaded the library before.
        # `cs_decide_rules` adds `repaired_rules` (loop0007 item 02), and
        # `cs_decide_variant` is it with the published rules.
        lib.cs_decide_variant.restype = ctypes.c_int
        lib.cs_decide_variant.argtypes = [
            ctypes.c_int, ctypes.c_int,                 # n, k
            ctypes.POINTER(ctypes.c_uint64),            # neighbourhoods
            ctypes.c_longlong, ctypes.c_double,         # max_nodes, seconds
            ctypes.c_int, ctypes.c_int, ctypes.c_int,   # subset, definite, memo
            ctypes.c_int, ctypes.c_longlong,            # restrict, memo_limit
            ctypes.c_int, ctypes.c_int, ctypes.c_int,   # better, dominators, old
            ctypes.c_int, ctypes.c_int,                 # fan_order, better_move_variant
            ctypes.POINTER(ctypes.c_int),               # out_path
            ctypes.POINTER(ctypes.c_longlong),          # out_nodes
            ctypes.POINTER(ctypes.c_int),               # out_len
        ]
        lib.cs_decide_rules.restype = ctypes.c_int
        lib.cs_decide_rules.argtypes = (lib.cs_decide_variant.argtypes[:15]
                                        + [ctypes.c_int]   # repaired_rules
                                        + lib.cs_decide_variant.argtypes[15:])
        # Rule counters of the last call on this thread (loop0007 item 04).
        lib.cs_last_rule_counts.restype = ctypes.c_int
        lib.cs_last_rule_counts.argtypes = [ctypes.POINTER(ctypes.c_longlong)]
        _library = lib
        return lib


# The counters `cs_last_rule_counts` returns, in the order of customer_search.c's
# RC_* enum.
RULE_COUNT_NAMES = (
    "filter_calls",       # dominance_filter calls with a candidate left
    "definite_prefilter", # candidates passing close >= open
    "definite_match_fail",  # ... of which the matching test fails (repaired only)
    "definite_fires",     # nodes where the definite move fires
    "definite_lost",      # nodes with a prefilter pass where none fires
    "better_prefilter",   # (r, q) pairs passing premises 3 and 4
    "better_match_fail",  # ... of which the matching test fails (repaired only)
    "better_pruned",      # candidates the better move drops
    # The audit of the published rules (`audit_repaired`, loop0007 item 07):
    "audit_definite_fail",  # nodes whose definite pick is not hereditarily definite
    "audit_better_fail",  # nodes with a better-move drop no repaired citation covers
    "audit_nodes_fail",   # nodes failing CodeNodeRepaired, either way
)


def last_rule_counts() -> dict[str, int] | None:
    """How often each rule's prefilter and its repaired test passed in the
    last `decide_native` call made *on this thread*, or None without the
    library. Counting never changes the search; it is there to measure what
    the repair costs (loop0007 item 04, `paper2/solver_fix_cost.py`)."""
    library = _load()
    if library is None:
        return None
    out = (ctypes.c_longlong * len(RULE_COUNT_NAMES))()
    library.cs_last_rule_counts(out)
    return dict(zip(RULE_COUNT_NAMES, (int(v) for v in out)))


def native_available() -> bool:
    """Whether the C search can be used at all on this machine."""
    return _load() is not None


def build_error() -> str | None:
    """Why the C search is unavailable, if it is."""
    _load()
    return _build_error


def decide_native(
    instance: MOSPInstance,
    k: int,
    *,
    restrict: bool = False,
    subset_rule: bool = True,
    definite_move: bool = True,
    old_move: bool = True,
    memo: bool = True,
    better_move: bool = False,
    better_move_dominators: int = 4,
    max_nodes: int | None = None,
    seconds: float | None = None,
    memo_limit: int = 4_000_000,
    fan_order: str = "index",
    old_close_count: bool = False,
    old_rule_order: bool = False,
    subset_after_better_move: bool = False,
    repaired_rules: bool = True,
    audit_repaired: bool = False,
) -> Decision | None:
    """Decide "MOSP(instance) <= k?" in C, or return None if it cannot.

    `old_close_count` and `old_rule_order` each *revert* one of the two
    changes of the 2026-09-26 `better_move` fix (`reports/better_move_bug.md`
    §7): the corrected close count, and the subset rule running before better
    move. Both defaults are today's rule; either flag on is an unsound search
    kept only to measure what the fix costs (`learning.fix_cost`,
    `reports/ml_nature.md` §31). They do nothing unless `better_move` is on.
    `subset_after_better_move` is not a revert but a candidate composition
    (better move first, then the subset rule citing nothing better move
    discarded), measured in the same study and, like the rest, the default of
    nothing.

    `repaired_rules` is the definite and better moves with the repaired
    premises proved sound in `lean/MOSPFormalization/Search/`, as in
    `customer_search.decide`; it matches the Python node for node
    (`tests/test_repaired_rules.py`). The default since 2026-10-01
    (loop0007 item 03); `False` is the rules as Chu & Stuckey publish them.

    `audit_repaired` (with `repaired_rules=False` only) runs the published
    rules and counts, at every node the search expands, whether the check
    `CodeNodeRepaired` of `lean/MOSPFormalization/Search/Decide.lean` fails:
    the definite pick not hereditarily definite, or a better-move drop with no
    earlier survivor meeting `IsRepairedBetter`. Read the counts with
    `last_rule_counts()`. An `unsat` with `audit_nodes_fail == 0` is a sound
    refutation by `codeExec_mospValue_of_repaired` (loop0007 item 07). The
    audit never changes the search: nodes, answer and witness are the
    published rules' own.

    None means "not applicable here" -- too many customers, no library, or a
    flag the C does not implement -- and the caller should use the Python. It
    never means "do not know"; that is `Decision("unknown", ...)`, as in the
    reference.
    """
    if fan_order not in FAN_ORDERS:
        raise ValueError(f"fan_order must be one of {FAN_ORDERS}, not {fan_order!r}")
    if audit_repaired and repaired_rules:
        raise ValueError("audit_repaired audits the published rules: pass repaired_rules=False")
    library = _load()
    if library is None:
        return None

    active = [c for c in range(instance.n_customers)
              if instance.customer_patterns(c)]
    if not active or instance.n_patterns == 0:
        return Decision("sat", [], 0)
    if instance.n_customers > _MAX_CUSTOMERS:
        return None

    masks = _neighbour_masks(instance)
    n = instance.n_customers
    packed = (ctypes.c_uint64 * (2 * n))()
    for index, mask in enumerate(masks):
        packed[2 * index] = mask & ((1 << 64) - 1)
        packed[2 * index + 1] = (mask >> 64) & ((1 << 64) - 1)

    path = (ctypes.c_int * n)()
    nodes = ctypes.c_longlong(0)
    length = ctypes.c_int(0)

    variant = (BM_OLD_CLOSE_COUNT if old_close_count else 0) | \
              (BM_OLD_RULE_ORDER if old_rule_order else 0) | \
              (BM_SUBSET_RESTRICTED if subset_after_better_move else 0)
    status = library.cs_decide_rules(
        n, k, packed,
        -1 if max_nodes is None else int(max_nodes),
        0.0 if seconds is None else float(seconds),
        int(subset_rule), int(definite_move), int(memo),
        int(restrict), int(memo_limit),
        int(better_move), int(better_move_dominators), int(old_move),
        FAN_ORDERS.index(fan_order), variant,
        2 if audit_repaired else int(repaired_rules),
        path, ctypes.byref(nodes), ctypes.byref(length))

    if status == -2:                       # the memo could not be allocated
        return None
    if status == 1:
        return Decision("sat", [path[i] for i in range(length.value)], nodes.value)
    if status == 0:
        # A restricted search discards branches it cannot justify, so
        # exhausting what remains proves nothing -- same rule as the reference.
        return Decision("unknown" if restrict else "unsat", None, nodes.value)
    return Decision("unknown", None, nodes.value)
