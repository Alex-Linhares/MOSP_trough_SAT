"""Learned branching inside the complete customer search.

`satisfiability.customer_search.decide` expands the surviving candidates
cheapest-first. Cheapest-first is a one-step-lookahead policy, and the corpus
contains 2.27M examples of what a *provably optimal* closing order does at the
same decision point -- so the obvious question is whether replacing it with the
trained policy visits fewer nodes.

Two calls are worth separating, because order does entirely different things to
them:

- **the sat call** (`k` = optimum): the search stops at the first order that
  works, so branching order decides how long it looks. A better order should
  win, and by a lot.
- **the refutation** (`k` = optimum - 1): every branch has to be refuted, so
  the node count is a property of the state space, not of the order it is
  walked in -- except through `old_move`, whose pruning depends on what an
  ancestor already searched, and through the memo. Any win here is that
  interaction, and it could as easily be a loss.

**This measures; it does not ship.** `decide` runs in C by default, about 120x
faster, and the C cannot call back into Python. A per-node model call costs more
than the nodes it saves unless the saving is large, so the experiment's job is
to say whether a C port of the ordering is worth writing. The `branch` hook
forces the Python reference path.

Usage:
    python -m learning.guided_search --instances 40
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np

from learning.policy import DEFAULT_MODEL, load, step_features
from mosp.instance import MOSPInstance
from satisfiability.heuristics import _neighbour_masks


def policy_branch(instance: MOSPInstance, model=None):
    """A `branch` callable for `decide` that orders candidates by the policy.

    Returns a permutation of what it is given -- never a subset. Dropping a
    candidate would turn an exhausted search into an unsound refutation, and
    `decide` trusts the callable not to.
    """
    model = model or load(DEFAULT_MODEL)
    masks = _neighbour_masks(instance)
    n = instance.n_customers

    def branch(closed: int, opened: int,
               playable: list[tuple[int, int]]) -> list[tuple[int, int]]:
        features = np.array(
            [step_features(masks, n, closed, opened, customer)
             for _, customer in playable],
            dtype=np.float32,
        )
        scores = model.predict(features, raw_score=True, num_threads=1)
        return [playable[i] for i in np.argsort(-scores)]

    return branch


def compare(
    instances: list[tuple[MOSPInstance, int]],
    max_nodes: int = 200_000,
    model=None,
    verbose: bool = True,
) -> dict:
    """Node counts with and without the policy, on the sat and unsat calls."""
    from satisfiability.customer_search import decide

    model = model or load(DEFAULT_MODEL)
    rows = []

    for instance, optimum in instances:
        record: dict[str, object] = {
            "instance": instance.name,
            "n_customers": instance.n_customers,
            "optimum": optimum,
        }
        branch = policy_branch(instance, model)

        for label, k in (("sat", optimum), ("unsat", optimum - 1)):
            if k < 1:
                continue
            for tag, kwargs in (("plain", {}), ("guided", {"branch": branch})):
                started = time.monotonic()
                answer = decide(instance, k, native=False, max_nodes=max_nodes,
                                **kwargs)
                record[f"{label}_{tag}_nodes"] = answer.nodes
                record[f"{label}_{tag}_seconds"] = time.monotonic() - started
                record[f"{label}_{tag}_status"] = answer.status

        rows.append(record)
        if verbose:
            print(f"  {instance.name[:44]:44s} "
                  f"sat {record.get('sat_plain_nodes')}->{record.get('sat_guided_nodes')}  "
                  f"unsat {record.get('unsat_plain_nodes')}->{record.get('unsat_guided_nodes')}",
                  flush=True)

    return {"rows": rows, "summary": _summarise(rows)}


def _summarise(rows: list[dict]) -> dict:
    out: dict[str, object] = {}
    for label in ("sat", "unsat"):
        # An "unknown" is a run that hit the node cap, so its count is the cap
        # rather than a measurement. Counting those would report a ratio of
        # exactly 1.000 for the hardest instances in the sample, which is the
        # one place the answer matters.
        pairs = [(r[f"{label}_plain_nodes"], r[f"{label}_guided_nodes"])
                 for r in rows
                 if r.get(f"{label}_plain_status") == r.get(f"{label}_guided_status")
                 and r.get(f"{label}_plain_status") != "unknown"
                 and f"{label}_plain_nodes" in r]
        if not pairs:
            continue
        plain = sum(p for p, _ in pairs)
        guided = sum(g for _, g in pairs)
        out[label] = {
            "instances": len(pairs),
            "plain_nodes": plain,
            "guided_nodes": guided,
            "ratio": guided / plain if plain else 0.0,
            "guided_wins": sum(1 for p, g in pairs if g < p),
            "guided_losses": sum(1 for p, g in pairs if g > p),
            "ties": sum(1 for p, g in pairs if g == p),
        }
    mismatch = [r["instance"] for r in rows
                for label in ("sat", "unsat")
                if r.get(f"{label}_plain_status") is not None
                and r.get(f"{label}_plain_status") != r.get(f"{label}_guided_status")]
    out["status_mismatches"] = mismatch
    return out


def _sample(count: int, seed: int, max_customers: int,
            match: str | None = None) -> list[tuple[MOSPInstance, int]]:
    """Instances small enough for the Python reference to finish on."""
    from satisfiability.mosp_solver import _solution_path

    from learning.dataset import enumerate_instances

    pairs = enumerate_instances(Path("benchmarks/instances"))
    rng = random.Random(seed)
    rng.shuffle(pairs)

    chosen: list[tuple[MOSPInstance, int]] = []
    for _, instance in pairs:
        if instance.n_customers > max_customers:
            continue
        if match and match not in instance.name:
            continue
        path = _solution_path(instance, Path("solutions"))
        if not path.exists():
            continue
        chosen.append((instance, json.loads(path.read_text())["mosp_value"]))
        if len(chosen) >= count:
            break
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instances", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-customers", type=int, default=30)
    parser.add_argument("--match", type=str, default=None,
                        help="only instances whose name contains this")
    parser.add_argument("--max-nodes", type=int, default=200_000)
    parser.add_argument("--out", type=Path,
                        default=Path("learning/data/guided_search.json"))
    args = parser.parse_args()

    instances = _sample(args.instances, args.seed, args.max_customers, args.match)
    print(f"{len(instances)} instances, up to {args.max_customers} customers\n")

    result = compare(instances, max_nodes=args.max_nodes)
    summary = result["summary"]

    print(f"\n{'call':8s} {'n':>4s} {'plain nodes':>12s} {'guided':>12s} "
          f"{'ratio':>7s} {'win':>5s} {'lose':>5s} {'tie':>5s}")
    for label in ("sat", "unsat"):
        s = summary.get(label)
        if s:
            print(f"{label:8s} {s['instances']:4d} {s['plain_nodes']:12,d} "
                  f"{s['guided_nodes']:12,d} {s['ratio']:7.3f} "
                  f"{s['guided_wins']:5d} {s['guided_losses']:5d} {s['ties']:5d}")
    if summary["status_mismatches"]:
        print(f"\n!! status disagreed on {len(summary['status_mismatches'])}: "
              f"{summary['status_mismatches'][:5]}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
