"""An independent oracle: the CP model of Martin, Yanasse & Pinto (2022), solved
by OR-Tools CP-SAT, in its own interpreter.

"CP-SAT" is Google's name for that solver, not a SAT encoding of ours -- see the
note at the top of `cpsat_oracle.py`. Elsewhere this is called "the CP oracle",
because "SAT" in this project means `satisfiability/mosp_encoding.py`.

Every certified optimum in this corpus currently rests on two solvers written
here -- the SAT encoding and the customer search -- which agree with each other
on the instances where both were run. Agreement between two implementations by
the same author is weaker evidence than it looks, and the customer search's
refutations carry no proof object at all, so a third opinion from a mature
outside solver is the strongest validation available short of a proof checker.

This is the bridge. The model itself lives in `cpsat_oracle.py` and runs under
`.venv-cpsat/bin/python`, which shares no code and no interpreter with this
project; instances go across as JSON and answers come back the same way. The
separation began as a workaround -- `ortools` needs numpy >= 2 and collides with
anaconda's native libprotobuf -- and is worth keeping on its own merits.

What to expect of it, from the authors of the model:

    our mathematical models perform best for scenarios characterised by a
    small/moderate number of patterns or for scenarios that lead to a dense
    MOSP graph, but are not competitive with the best algorithms of the
    literature (Chu & Stuckey, 2009; Goncalves et al., 2016)

So this is built to check the corpus, not to close the instances that remain
open -- those are large and sparse, the case its authors call weakest.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from mosp.instance import MOSPInstance

VENV_PYTHON = Path(__file__).parent.parent / ".venv-cpsat" / "bin" / "python"
ORACLE = Path(__file__).with_name("cpsat_oracle.py")


@dataclass
class OracleAnswer:
    """What CP-SAT said, and how far it got.

    `status` is CP-SAT's own: OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN, or
    ERROR/UNAVAILABLE from this side. Only OPTIMAL is an optimality claim;
    FEASIBLE means it found `value` and ran out of time proving it minimal,
    with `best_bound` saying how far it got.
    """

    status: str
    value: int | None
    ordering: list[int] | None
    best_bound: int | None
    seconds: float
    error: str | None = None

    @property
    def proved(self) -> bool:
        return self.status == "OPTIMAL"


def available() -> bool:
    """Whether the isolated interpreter and the model are both present."""
    return VENV_PYTHON.exists() and ORACLE.exists()


def solve_cpsat(
    instance: MOSPInstance,
    max_seconds: float = 60.0,
    workers: int = 1,
    upper: int | None = None,
    lower: int = 0,
    hint: list[int] | None = None,
    on_improve: "Callable[[int, list[int]], None] | None" = None,
) -> OracleAnswer:
    """Ask CP-SAT for the optimum, in a separate process.

    `upper` and `hint` pass on what is already known: a verified witness cannot
    cut off the optimum, since the optimum is at or below it, and the hint saves
    CP-SAT from spending its budget rediscovering a worse sequence.

    `lower` is different and should usually be left alone. Feeding in this
    project's relaxation bounds would make CP-SAT's own `best_bound` rest on
    Chu & Stuckey's Lemma 1, which is measured here and not proved — and an
    independent bound is the one thing this solver offers that the others do
    not. Pass it only when the caller wants speed rather than an opinion.
    """
    if not available():
        return OracleAnswer("UNAVAILABLE", None, None, None, 0.0,
                            error=f"no interpreter at {VENV_PYTHON}")

    request = {
        "matrix": instance.matrix.astype(int).tolist(),
        "n_customers": instance.n_customers,
        "n_patterns": instance.n_patterns,
        "max_seconds": max_seconds,
        "workers": workers,
        "upper": upper,
        "lower": lower,
        "hint": hint,
    }

    # Read the child line by line rather than waiting for it. A long solve
    # reports improvements as it finds them, and a caller that only sees the
    # final line holds every one of them in the child's memory until it exits,
    # losing all of them if anything interrupts it.
    answer = {"status": "ERROR", "error": "no output"}
    try:
        child = subprocess.Popen(
            [str(VENV_PYTHON), str(ORACLE)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
    except OSError as exc:
        return OracleAnswer("ERROR", None, None, None, 0.0, error=str(exc))

    try:
        child.stdin.write(json.dumps(request))
        child.stdin.close()
        for line in child.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("type") == "improvement":
                if on_improve is not None:
                    on_improve(record["value"], record["ordering"])
            else:
                answer = record
        child.wait(timeout=60)
    except subprocess.SubprocessError as exc:
        child.kill()
        return OracleAnswer("ERROR", None, None, None, 0.0, error=str(exc))
    finally:
        if child.poll() is None:
            child.kill()

    if child.returncode not in (0, None):
        stderr = (child.stderr.read() or "").strip()[:200]
        return OracleAnswer("ERROR", None, None, None, 0.0, error=stderr)

    return OracleAnswer(
        status=answer.get("status", "ERROR"),
        value=answer.get("value"),
        ordering=answer.get("ordering"),
        best_bound=answer.get("best_bound"),
        seconds=answer.get("wall", 0.0),
        error=answer.get("error"),
    )
