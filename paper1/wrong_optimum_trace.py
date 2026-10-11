"""Write the Lean data for `Search/WrongOptimum.lean` from the Python reference.

The 34-customer instance of `paper1/data/false_refutation/` is the one on which
the previous algorithm (Chu & Stuckey 2009: definite move as published, subset
rule, old move, memo; better move off) refutes k = 6 although 6 stacks suffice.
`lean/MOSPFormalization/Search/WrongOptimum.lean` proves this in Lean by
running a bitmask model of that search inside the kernel. This script writes
the data that model is checked against, to
`lean/MOSPFormalization/Search/WrongOptimumData.lean`:

* the instance, as its 61 patterns (each pattern is one edge of the MOSP graph,
  `solutions34.json`'s `patterns_as_edges`), checked against `instance34.mosp`;
* the closing order of 6 open stacks (`solutions34.json`, `repaired_rules`);
* **the trace of the Python reference** at k = 6: every call of the inner
  `search(closed, opened, seen)` of `satisfiability.customer_search.decide`,
  in the order the calls are made, as the pair `(closed, seen)` of bitmasks
  with which it was entered, captured with `sys.setprofile` from the running
  reference (`native=False`, `repaired_rules=False`, definite move, subset
  rule, old move, better move off). The reference drops the memo under old
  move, so this is the memo-off run (839 nodes). The C's memo-on run (526
  nodes) is checked against the Lean model by its node count, which this
  script records too.

The Lean model recomputes the run itself; the trace is not an input to the
proof that the run refutes 6. It is what the model is *tested* against: the
Lean theorem `trace_eq_python` says the model enters exactly these calls in
exactly this order, and the mutation tests below show the comparison is not
vacuous: with `--mutate N` the script asks Lean to check the captured trace
(which must pass) and N mutants of it, each with one bit of one call flipped,
one call deleted or two calls swapped (each must fail).

    python -m paper1.wrong_optimum_trace            # write the data file
    python -m paper1.wrong_optimum_trace --mutate 8 # and 8 mutation tests in Lean
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

from mosp.instance import MOSPInstance
from satisfiability import customer_search
from satisfiability.customer_search import decide
from satisfiability.heuristics import _neighbour_masks

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "paper1" / "data" / "false_refutation"
LEAN = ROOT / "lean"
OUT = LEAN / "MOSPFormalization" / "Search" / "WrongOptimumData.lean"

CONFIG = dict(repaired_rules=False, definite_move=True, subset_rule=True,
              old_move=True, better_move=False)


def python_trace(instance: MOSPInstance, k: int) -> tuple[list[tuple[int, int]], str, int]:
    """Every call of the reference's inner `search`, as `(closed, seen)` on entry."""
    calls: list[tuple[int, int]] = []
    code = None

    def profile(frame, event, arg):
        nonlocal code
        if event != "call" or frame.f_code.co_name != "search":
            return
        if frame.f_code.co_filename != customer_search.__file__:
            return
        loc = frame.f_locals
        calls.append((loc["closed"], loc["seen"]))

    sys.setprofile(profile)
    try:
        answer = decide(instance, k, native=False, memo=False, **CONFIG)
    finally:
        sys.setprofile(None)
    return calls, answer.status, answer.nodes


def lean_list(items, per_line=6) -> str:
    rows = [", ".join(items[i:i + per_line]) for i in range(0, len(items), per_line)]
    return "[" + ",\n  ".join(rows) + "]"


def render(edges, masks, order, trace, c_nodes, py_nodes) -> str:
    edge_s = lean_list([f"({a}, {b})" for a, b in edges], 8)
    mask_s = lean_list([str(m) for m in masks], 6)
    order_s = lean_list([str(c) for c in order], 17)
    trace_s = lean_list([f"({c}, {s})" for c, s in trace], 4)
    return f'''/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# Data for `WrongOptimum.lean` (generated, do not edit)

Written by `python -m paper1.wrong_optimum_trace` from
`paper1/data/false_refutation/` and from a run of the Python reference
`satisfiability.customer_search.decide` (published rules, old move, better
move off, `native=False`) at `k = 6`.
-/

namespace MOSPFormalization

namespace Search

namespace WrongOptimum

/-- The 61 patterns of `instance34.mosp`, each the pair of customers needing it
(`solutions34.json`, `patterns_as_edges`). -/
def patternEdges : List (Nat × Nat) :=
  {edge_s}

/-- `N[c]` as a bitmask, for each customer `c` (the reference's `_neighbour_masks`). -/
def nbList : List Nat :=
  {mask_s}

/-- A closing order of cost 6 (`solutions34.json`, `repaired_rules`). -/
def witnessOrder : List Nat :=
  {order_s}

/-- Every call of the Python reference's inner `search` at `k = 6`, in call order, as the
bitmasks `(closed, seen)` it was entered with ({len(trace)} calls, {py_nodes} nodes). -/
def pythonTrace : List (Nat × Nat) :=
  {trace_s}

/-- Nodes of the Python reference (memo off) and of the C (memo on) at `k = 6`. -/
def pythonNodes : Nat := {py_nodes}
def cNodes : Nat := {c_nodes}

end WrongOptimum

end Search

end MOSPFormalization
'''


PROBE = """import MOSPFormalization.Search.WrongOptimum
open MOSPFormalization.Search MOSPFormalization.Search.BitSearch
open MOSPFormalization.Search.WrongOptimum
set_option maxHeartbeats 0 in
example : summaryTrace (run (published 6 false) 40) =
    (.unsat, {nodes}, {trace}) := by
  decide +kernel
"""


def probe(trace, nodes: int, path: Path) -> bool:
    """Whether Lean accepts `trace` as the model's calls (a standalone file, so the
    built data module is not involved)."""
    path.write_text(PROBE.format(nodes=nodes,
                                 trace=lean_list([f"({c}, {s})" for c, s in trace], 4)))
    result = subprocess.run(["lake", "env", "lean", str(path)], cwd=LEAN,
                            capture_output=True, text=True)
    return result.returncode == 0


def mutate(trace, i: int, rng: random.Random):
    mutated = list(trace)
    kind = ["closed bit", "seen bit", "deleted call", "swapped calls"][i % 4]
    j = rng.randrange(1, len(mutated))
    closed, seen = mutated[j]
    if kind == "closed bit":
        mutated[j] = (closed ^ (1 << rng.randrange(34)), seen)
    elif kind == "seen bit":
        mutated[j] = (closed, seen ^ (1 << rng.randrange(34)))
    elif kind == "deleted call":
        del mutated[j]
    else:
        j2 = rng.randrange(1, len(mutated))
        while mutated[j2] == mutated[j]:
            j2 = rng.randrange(1, len(mutated))
        mutated[j], mutated[j2] = mutated[j2], mutated[j]
    return kind, j, mutated


def mutation_tests(trace, py_nodes: int, count: int) -> None:
    """The control (the trace as captured) must be accepted, and every mutant (one
    bit of one call flipped, one call deleted, two calls swapped) rejected. Each
    probe re-runs the search in the kernel, about two minutes, four at a time."""
    from concurrent.futures import ThreadPoolExecutor

    rng = random.Random(0)
    scratch = LEAN / ".lake" / "wrong_optimum_probes"
    scratch.mkdir(parents=True, exist_ok=True)
    jobs = [("control", 0, trace)] + [mutate(trace, i, rng) for i in range(count)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        verdicts = list(pool.map(
            lambda ij: probe(ij[1][2], py_nodes, scratch / f"probe{ij[0]}.lean"),
            enumerate(jobs)))
    bad = 0
    for (kind, j, _), accepted in zip(jobs, verdicts):
        expected = kind == "control"
        print(f"{kind:14s} at call {j:4d}: {'accepted' if accepted else 'rejected'}"
              f"{'' if accepted == expected else '   <-- WRONG'}")
        bad += accepted != expected
    if bad:
        raise SystemExit(f"{bad} probes gave the wrong verdict")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mutate", type=int, default=0, metavar="N",
                        help="run N mutation tests in Lean after writing")
    args = parser.parse_args()

    instance = MOSPInstance.from_file(DATA / "instance34.mosp")
    record = json.loads((DATA / "solutions34.json").read_text())
    edges = [tuple(e) for e in record["patterns_as_edges"]]
    order = record["repaired_rules"]["customer_closing_order"]

    # The edges are the instance: pattern j needs exactly customers edges[j].
    assert instance.n_customers == 34 and instance.n_patterns == len(edges) == 61
    for j, (a, b) in enumerate(edges):
        column = {c for c in range(34) if instance.matrix[c][j]}
        assert column == {a, b}, (j, column)
    masks = _neighbour_masks(instance)
    for c in range(34):
        expect = 1 << c
        for a, b in edges:
            if c in (a, b):
                expect |= (1 << a) | (1 << b)
        assert masks[c] == expect

    trace, status, py_nodes = python_trace(instance, 6)
    assert status == "unsat" and py_nodes == 839, (status, py_nodes)
    assert len(trace) == py_nodes + 1
    native = decide(instance, 6, native=True, memo=True, **CONFIG)
    assert native.status == "unsat", native
    c_nodes = native.nodes

    OUT.write_text(render(edges, masks, order, trace, c_nodes, py_nodes))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(trace)} calls, "
          f"Python {py_nodes} nodes (memo off), C {c_nodes} nodes (memo on)")

    if args.mutate:
        mutation_tests(trace, py_nodes, args.mutate)


if __name__ == "__main__":
    main()
