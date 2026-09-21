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
`better_move` is Theorem 2, which exists only here: it is O(|R|^3) per node
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
import subprocess
import threading
from pathlib import Path

from mosp.instance import MOSPInstance
from satisfiability.customer_search import Decision
from satisfiability.heuristics import _neighbour_masks

_SOURCE = Path(__file__).with_name("customer_search.c")
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
    try:
        subprocess.run(
            ["gcc", "-O3", "-march=native", "-shared", "-fPIC",
             "-o", str(_LIBRARY), str(_SOURCE)],
            check=True, capture_output=True, timeout=120)
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        _build_error = f"{type(exc).__name__}: {exc}"
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
        lib.cs_decide.restype = ctypes.c_int
        lib.cs_decide.argtypes = [
            ctypes.c_int, ctypes.c_int,                 # n, k
            ctypes.POINTER(ctypes.c_uint64),            # neighbourhoods
            ctypes.c_longlong, ctypes.c_double,         # max_nodes, seconds
            ctypes.c_int, ctypes.c_int, ctypes.c_int,   # subset, definite, memo
            ctypes.c_int, ctypes.c_longlong,            # restrict, memo_limit
            ctypes.c_int, ctypes.c_int, ctypes.c_int,   # better, dominators, old
            ctypes.POINTER(ctypes.c_int),               # out_path
            ctypes.POINTER(ctypes.c_longlong),          # out_nodes
            ctypes.POINTER(ctypes.c_int),               # out_len
        ]
        _library = lib
        return lib


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
) -> Decision | None:
    """Decide "MOSP(instance) <= k?" in C, or return None if it cannot.

    None means "not applicable here" -- too many customers, no library, or a
    flag the C does not implement -- and the caller should use the Python. It
    never means "do not know"; that is `Decision("unknown", ...)`, as in the
    reference.
    """
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

    status = library.cs_decide(
        n, k, packed,
        -1 if max_nodes is None else int(max_nodes),
        0.0 if seconds is None else float(seconds),
        int(subset_rule), int(definite_move), int(memo),
        int(restrict), int(memo_limit),
        int(better_move), int(better_move_dominators), int(old_move),
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
