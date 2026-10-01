"""The C port of the search, and the rules for when to trust it.

`pathwidth/search.py` is the reference implementation and stays that way: it
is the one the exhaustive tests are written against, and where the two
disagree it is right. This module compiles `closing_search_w.c` (the multiword
generalisation of `closing_search.c`, which is a verbatim copy of the MOSP
project's `satisfiability/customer_search.c`) and calls it through `ctypes`, for the one reason that matters: it is about 120x faster,
and Mycielski M6 goes from 20 s to well under a second.

The C entry point takes only `n`, `k`, the neighbourhood masks and the flags --
it never saw products either -- so the port is this wrapper alone.

It declines rather than guesses. The Python is used instead when:
- the shared library will not build (no compiler, or a build error);
- the graph has more than 1024 vertices (16 x 64-bit words; the multiword
  `closing_search_w.c` is built for 2, 4, 8 and 16 words and the smallest
  that fits is used);
- a flag the C does not implement is asked for (`branch`, `expansion_prune`).

Two things worth knowing:
- `better_move` (Chu & Stuckey's Theorem 2) existed only here until
  2026-10-01, when the Python got a port of it (loop0007 item 03); the two
  now match node for node. It is O(|R|^3) per node against Theorem 1's
  O(|R|^2), which the MOSP project measured as the wrong trade in Python and
  worth it at C speed on sparse instances. `better_move_dominators` caps how many candidates are tried as
  the dominating `q`; a subset prunes less but never wrongly.
- With `old_move` and `memo` both on, the C runs both, as Chu & Stuckey do,
  while the Python drops the memo. The MOSP project's exhaustive tests found
  the two agree anyway (old move subsumes the memo), and
  `tests/test_native.py` re-checks that here.

The fallback is silent by design: a caller asking for a decision wants the
right answer, and both paths give the same one. `native_available()` reports
which is in use for the benchmarks that care.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import threading
from collections.abc import Sequence
from pathlib import Path

from pathwidth.graph import FAN_ORDERS
from pathwidth.search import Decision

_SOURCE = Path(__file__).with_name("closing_search_w.c")
_LEGACY_SOURCE = Path(__file__).with_name("closing_search.c")     # the 128-bit original, for tests
WORD_SIZES = (2, 4, 8, 16)                                          # 128, 256, 512, 1024 vertices
MAX_VERTICES = 64 * WORD_SIZES[-1]

_BM_TODAY = 0

_lock = threading.Lock()
_libraries: dict[int, "ctypes.CDLL"] = {}
_legacy: "ctypes.CDLL | None" = None
_build_error: str | None = None

_ARGTYPES = [
    ctypes.c_int, ctypes.c_int,                 # n, k
    ctypes.POINTER(ctypes.c_uint64),            # neighbourhoods
    ctypes.c_longlong, ctypes.c_double,         # max_nodes, seconds
    ctypes.c_int, ctypes.c_int, ctypes.c_int,   # subset, definite, memo
    ctypes.c_int, ctypes.c_longlong,            # restrict, memo_limit
    ctypes.c_int, ctypes.c_int, ctypes.c_int,   # better, dominators, old
    ctypes.c_int, ctypes.c_int,                 # fan_order, better_move_variant
    ctypes.c_int,                               # repaired_rules
    ctypes.POINTER(ctypes.c_int),               # out_path
    ctypes.POINTER(ctypes.c_longlong),          # out_nodes
    ctypes.POINTER(ctypes.c_int),               # out_len
]


def _build(source: Path, target: Path, defines: list[str]) -> bool:
    """Compile `source` to `target` unless `target` is newer. Returns whether
    the library is usable afterwards."""
    global _build_error
    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        return True
    scratch = target.with_name(target.name + f".build-{os.getpid()}")
    try:
        subprocess.run(
            ["gcc", "-O3", "-march=native", "-shared", "-fPIC", *defines,
             "-o", str(scratch), str(source)],
            check=True, capture_output=True, timeout=120)
        os.replace(scratch, target)
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        _build_error = f"{type(exc).__name__}: {exc}"
        try:
            scratch.unlink()
        except OSError:
            pass
        return False


def _load(words: int = 2) -> "ctypes.CDLL | None":
    """The multiword library for `words` x 64 bits, built on first use."""
    global _build_error
    with _lock:
        if words in _libraries:
            return _libraries[words]
        target = _SOURCE.with_name(f"_closing_search_w{words}.so")
        if not _SOURCE.exists() or not _build(_SOURCE, target, [f"-DWORDS={words}"]):
            return None
        try:
            lib = ctypes.CDLL(str(target))
        except OSError as exc:
            _build_error = str(exc)
            return None
        lib.csw_decide.restype = ctypes.c_int
        lib.csw_decide.argtypes = _ARGTYPES
        lib.csw_words.restype = ctypes.c_int
        assert lib.csw_words() == words
        _libraries[words] = lib
        return lib


def _load_legacy() -> "ctypes.CDLL | None":
    """The original 128-bit C (`closing_search.c`), kept for the tests that
    check the multiword build against it node for node."""
    global _legacy
    with _lock:
        if _legacy is not None:
            return _legacy
        target = _LEGACY_SOURCE.with_name("_closing_search_legacy.so")
        if not _LEGACY_SOURCE.exists() or not _build(_LEGACY_SOURCE, target, []):
            return None
        lib = ctypes.CDLL(str(target))
        lib.cs_decide_rules.restype = ctypes.c_int
        lib.cs_decide_rules.argtypes = _ARGTYPES
        _legacy = lib
        return lib


def words_for(n: int) -> int | None:
    """The smallest supported word count holding `n` vertices, or None."""
    for w in WORD_SIZES:
        if n <= 64 * w:
            return w
    return None


def native_available() -> bool:
    """Whether the C search can be used at all on this machine."""
    return _load(WORD_SIZES[0]) is not None


def build_error() -> str | None:
    """Why the C search is unavailable, if it is."""
    _load(WORD_SIZES[0])
    return _build_error


def _pack(masks: Sequence[int], words: int):
    n = len(masks)
    packed = (ctypes.c_uint64 * (words * n))()
    full = (1 << 64) - 1
    for index, mask in enumerate(masks):
        for w in range(words):
            packed[words * index + w] = (mask >> (64 * w)) & full
    return packed


def _call(fn, n: int, k: int, packed, *, restrict, subset_rule, definite_move, old_move, memo,
          better_move, better_move_dominators, max_nodes, seconds, memo_limit, fan_order,
          repaired_rules) -> Decision | None:
    path = (ctypes.c_int * n)()
    nodes = ctypes.c_longlong(0)
    length = ctypes.c_int(0)
    status = fn(
        n, k, packed,
        -1 if max_nodes is None else int(max_nodes),
        0.0 if seconds is None else float(seconds),
        int(subset_rule), int(definite_move), int(memo),
        int(restrict), int(memo_limit),
        int(better_move), int(better_move_dominators), int(old_move),
        FAN_ORDERS.index(fan_order), _BM_TODAY, int(repaired_rules),
        path, ctypes.byref(nodes), ctypes.byref(length))
    if status in (-2, -3):                 # allocation failure / too large for this build
        return None
    if status == 1:
        return Decision("sat", [path[i] for i in range(length.value)], nodes.value)
    if status == 0:
        return Decision("unknown" if restrict else "unsat", None, nodes.value)
    return Decision("unknown", None, nodes.value)


def decide_native(
    masks: Sequence[int],
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
    legacy: bool = False,
    repaired_rules: bool = True,
) -> Decision | None:
    """Decide the search question on `masks` in C, or return None if it cannot.

    None means "not applicable here" -- too many vertices, no library -- and
    the caller should use the Python. It never means "do not know"; that is
    `Decision("unknown", ...)`, as in the reference. `legacy=True` runs the
    original 128-bit C instead (tests only; None above 128 vertices).
    `repaired_rules` is the definite and better moves with the repaired
    premises proved sound in MOSP's `lean/MOSPFormalization/Search/`, as in
    `search.decide`; the default since 2026-10-01, `False` being the
    published rules.
    """
    if fan_order not in FAN_ORDERS:
        raise ValueError(f"fan_order must be one of {FAN_ORDERS}, not {fan_order!r}")
    n = len(masks)
    if not any(masks):
        return Decision("sat", [], 0)
    flags = dict(restrict=restrict, subset_rule=subset_rule, definite_move=definite_move,
                 old_move=old_move, memo=memo, better_move=better_move,
                 better_move_dominators=better_move_dominators, max_nodes=max_nodes,
                 seconds=seconds, memo_limit=memo_limit, fan_order=fan_order,
                 repaired_rules=repaired_rules)
    if legacy:
        lib = _load_legacy()
        if lib is None or n > 128:
            return None
        return _call(lib.cs_decide_rules, n, k, _pack(masks, 2), **flags)
    words = words_for(n)
    if words is None:
        return None
    lib = _load(words)
    if lib is None:
        return None
    return _call(lib.csw_decide, n, k, _pack(masks, words), **flags)
