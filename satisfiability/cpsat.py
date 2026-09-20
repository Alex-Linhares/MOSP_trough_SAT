"""An independent oracle: CP-SAT, in its own interpreter.

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
) -> OracleAnswer:
    """Ask CP-SAT for the optimum, in a separate process.

    `upper` and `lower` narrow the objective's domain if they are known. They
    are an optimisation only: a wrong bound would make the model infeasible or
    cut off the optimum, so callers that are not certain should omit them.
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
    }
    try:
        finished = subprocess.run(
            [str(VENV_PYTHON), str(ORACLE)],
            input=json.dumps(request), capture_output=True, text=True,
            timeout=max_seconds + 60)
    except subprocess.SubprocessError as exc:
        return OracleAnswer("ERROR", None, None, None, 0.0, error=str(exc))

    if finished.returncode != 0:
        return OracleAnswer("ERROR", None, None, None, 0.0,
                            error=(finished.stderr or "").strip()[:200])
    try:
        answer = json.loads(finished.stdout)
    except json.JSONDecodeError:
        return OracleAnswer("ERROR", None, None, None, 0.0,
                            error=f"unparseable: {finished.stdout[:200]}")

    return OracleAnswer(
        status=answer.get("status", "ERROR"),
        value=answer.get("value"),
        ordering=answer.get("ordering"),
        best_bound=answer.get("best_bound"),
        seconds=answer.get("wall", 0.0),
        error=answer.get("error"),
    )
