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
                            solutions_dir=tmp_path, verbose=False)

    assert len(results) == len(instances)
    assert {r[0] for r in results} == {i.name for i in instances}
    assert all(r[4] in ("refutation", "bound") for r in results), results


def test_it_writes_a_checkable_witness_with_its_provenance(tmp_path):
    """What lands on disk has to be the proof the driver claims it is."""
    instances = _instances()
    _sweep_within(120, instances, timeout=30, workers=2,
                  solutions_dir=tmp_path, verbose=False)

    for instance in instances:
        payload = json.loads((tmp_path / f"{instance.name}.json").read_text())
        assert payload["provenance"].startswith("certified:")
        assert max_open_stacks(instance, payload["ordering"]) == payload["mosp_value"]
