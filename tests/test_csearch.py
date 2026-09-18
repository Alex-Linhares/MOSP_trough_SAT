"""Guards on the parallel descent driver.

The interesting failure here is not a wrong answer but a hang: the pool used to
free worker slots by testing `is_alive()` on the processes, and a worker that has
posted its result is still alive for a moment afterwards. That loses one slot per
completion, so with more instances than workers the run could stop launching and
block forever on a queue nothing would ever write to. At `workers=1` it
deadlocked on the second instance every time.
"""

import json
import signal

import pytest

from benchmarks.csearch import sweep
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks


def _sweep_within(seconds, *args, **kwargs):
    """Run `sweep` under a wall-clock bound, failing rather than hanging.

    A regression here deadlocks instead of returning a wrong answer, and a test
    that hangs takes the whole suite with it. `SIGALRM` bounds it from the main
    thread; bounding it from a worker thread instead would mean forking the pool
    out of a multi-threaded process, which is the very thing CPython warns about.
    """
    def expired(signum, frame):
        raise AssertionError(
            f"sweep did not finish within {seconds}s -- the pool is deadlocked")

    previous = signal.signal(signal.SIGALRM, expired)
    signal.alarm(seconds)
    try:
        return sweep(*args, **kwargs)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _instances():
    return [
        MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]], name="a"),
        MOSPInstance.from_matrix([[1, 0, 1], [1, 1, 0], [0, 1, 1]], name="b"),
        MOSPInstance.from_matrix([[1, 1], [1, 0], [0, 1]], name="c"),
    ]


@pytest.mark.parametrize("workers", [1, 2, 5])
def test_the_pool_drains_with_fewer_workers_than_instances(workers, tmp_path):
    """Every instance must be launched and reported, at any pool size -- including
    one worker, where the slot-freeing bug deadlocked immediately."""
    instances = _instances()
    results = _sweep_within(120, instances, timeout=30, workers=workers,
                            solutions_dir=tmp_path,
                            ledger=tmp_path / "ledger.csv", verbose=False)

    assert len(results) == len(instances)
    assert {r[0] for r in results} == {i.name for i in instances}
    assert all(r[4] in ("refutation", "bound") for r in results), results


def test_it_writes_a_checkable_witness_with_its_provenance(tmp_path):
    """What lands on disk has to be the proof the driver claims it is."""
    instances = _instances()
    _sweep_within(120, instances, timeout=30, workers=2,
                  solutions_dir=tmp_path, ledger=tmp_path / 'ledger.csv',
                  verbose=False)

    for instance in instances:
        payload = json.loads((tmp_path / f"{instance.name}.json").read_text())
        assert payload["provenance"].startswith("certified:")
        assert max_open_stacks(instance, payload["ordering"]) == payload["mosp_value"]


# A descent that takes four steps rather than one, so "reported as it goes" is
# distinguishable from "reported at the end".
STEPWISE = [
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1], [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0],
]


def test_the_descent_reports_each_improvement_as_it_finds_it():
    """A multi-day descent must not hold its findings until it returns: an
    interruption would lose every bound it had ratcheted down. So `solve`
    reports each improvement as it happens, not only the final one."""
    from satisfiability.customer_search import solve

    instance = MOSPInstance.from_matrix(STEPWISE, name="stepwise")
    seen = []
    result = solve(instance, upper=instance.n_customers,
                   on_improve=lambda value, order: seen.append(value))

    assert len(seen) > 1, f"only the final value was reported: {seen}"
    assert seen == sorted(seen, reverse=True), f"values must fall: {seen}"
    assert seen[-1] == result.value


def test_the_worker_persists_a_checkpoint_even_when_nothing_is_proved(tmp_path):
    """The driver's callback re-verifies and writes, so an interrupted descent
    keeps what it found.

    `solve` is stubbed to report one improvement and then give up, and the
    worker's own final save is handed the stale cached value. Monotone saving
    means the file can only hold the better number if the checkpoint wrote it.
    """
    import multiprocessing

    import benchmarks.csearch as csearch
    from satisfiability.customer_search import Solution, solve as real_solve
    from satisfiability.mosp_solver import _save_solution

    instance = MOSPInstance.from_matrix(STEPWISE, name="stepwise")
    settled = real_solve(instance, upper=instance.n_customers)

    # Seed the cache with a deliberately poor value, as a stalled run would.
    stale = list(range(instance.n_patterns))
    _save_solution(instance, max_open_stacks(instance, stale), stale, tmp_path)

    def stub(inst, **kwargs):
        kwargs["on_improve"](settled.value, settled.order)
        return Solution(settled.value, [], "", 0, 0.0)   # no proof, no ordering

    original = csearch.solve if hasattr(csearch, "solve") else None
    import satisfiability.customer_search as cs
    cs.solve = stub
    try:
        queue: multiprocessing.Queue = multiprocessing.Queue()
        csearch._worker(instance.matrix.tolist(), instance.n_customers,
                        instance.n_patterns, instance.name, 30, None,
                        tmp_path, queue)
        queue.get()
    finally:
        cs.solve = real_solve

    payload = json.loads((tmp_path / "stepwise.json").read_text())
    assert payload["mosp_value"] == settled.value, "the checkpoint was not kept"
    assert payload["provenance"] == "solution", "an unproved value is not certified"
    assert max_open_stacks(instance, payload["ordering"]) == payload["mosp_value"]


def test_a_checkpoint_never_saves_a_witness_that_does_not_hold_up(monkeypatch,
                                                                  tmp_path):
    """The checkpoint re-simulates before writing, so a wrong witness from a
    future bug cannot reach the corpus between rounds."""
    import benchmarks.csearch as csearch

    instance = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]],
                                        name="liar")
    monkeypatch.setattr(csearch, "max_open_stacks", lambda *_: 999)
    _sweep_within(120, [instance], timeout=10, workers=1,
                  solutions_dir=tmp_path, ledger=tmp_path / 'ledger.csv',
                  verbose=False)
    assert not (tmp_path / "liar.json").exists()
