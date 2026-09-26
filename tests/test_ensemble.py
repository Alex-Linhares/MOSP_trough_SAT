"""Guards on the generated-ensemble campaign (`learning.ensemble`).

Two properties the campaign rests on: an instance is a pure function of its
cell and index, so a cell regenerates byte for byte from parameters alone and
nothing stored can drift from it; and the results row carries the right
optimum and the search's own node count, so the CSV is what the report says
it is. The hand-checked instance: product 1 is required by customers 0 and 1,
so any production order has two stacks open when it is produced, and the
optimum is 2; refuting k = 1 branches twice in the customer search.
"""

from pathlib import Path

import numpy as np
import pytest

from learning.ensemble import (
    Cell,
    analyse,
    cell_seed,
    dedupe,
    generate,
    instance_name,
    load_results,
    run,
)
from mosp.instance import MOSPInstance

HAND = [[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]]


@pytest.mark.parametrize("cell", [Cell("fixed", 8, 8, 2), Cell("bernoulli", 8, 12, 0.2)])
def test_a_cell_regenerates_byte_for_byte(cell, tmp_path: Path):
    first = [generate(cell, i) for i in range(5)]
    again = [generate(cell, i) for i in range(5)]
    for a, b in zip(first, again):
        assert a.name == b.name
        assert np.array_equal(a.matrix, b.matrix)
    # through the .mosp file too
    path = tmp_path / f"{first[0].name}.mosp"
    first[0].to_file(path)
    back = MOSPInstance.from_file(path)
    assert back.name == first[0].name
    assert np.array_equal(back.matrix, first[0].matrix)
    # distinct indexes give distinct seeds, and the seed is a stable function
    seeds = {cell_seed(cell, i) for i in range(5)}
    assert len(seeds) == 5
    assert cell_seed(Cell("fixed", 8, 8, 2), 0) == cell_seed(Cell("fixed", 8, 8, 2), 0)
    assert instance_name(cell, 3).endswith("_i003")


def test_fixed_generator_gives_every_product_d_customers():
    cell = Cell("fixed", 12, 10, 3)
    inst = generate(cell, 0)
    assert inst.matrix.shape == (12, 10)
    sums = inst.matrix.sum(axis=0)
    # exactly d per product, except where an empty customer was repaired with
    # one extra entry -- the generator guarantees every customer needs something
    assert sums.min() == 3
    assert (inst.matrix.sum(axis=1) >= 1).all()
    assert (sums >= 3).all()


def test_results_row_for_a_hand_checked_instance(tmp_path: Path):
    inst = MOSPInstance.from_matrix(HAND, name="hand")
    cell = Cell("fixed", 4, 4, 2)
    row = analyse(inst, cell, 0, tmp_path / "solutions", deadline_seconds=30, solve_budget=60)
    assert row["optimum"] == 2
    assert row["certified"] and row["witness_ok"]
    assert row["status_default"] == "unsat" and row["status_csearch"] == "unsat"
    assert row["nodes_default"] > 0 and row["nodes_csearch"] > 0
    assert row["g_components"] == 3          # {0, 1}, {2}, {3}
    assert row["complete_graph"] is False or row["complete_graph"] == False  # noqa: E712
    assert row["lb_best"] <= 2 <= row["ub_cs_dfs"]
    assert row["graph_cert"] is not None or row["wl_hash"]
    assert (tmp_path / "solutions" / "hand.json").exists()


def test_run_is_resumable_and_dedupes(tmp_path: Path):
    cells = [Cell("fixed", 8, 8, 2), Cell("fixed", 8, 8, 2), Cell("bernoulli", 8, 8, 0.3)]
    csv = tmp_path / "results.csv"
    frame = run(cells, 3, workers=1, csv=csv, instance_dir=tmp_path / "inst",
                solutions_dir=tmp_path / "sol", verbose=False)
    assert len(frame) == 6                    # the duplicate cell ran once
    assert frame["instance_name"].is_unique
    again = run(cells, 3, workers=1, csv=csv, instance_dir=tmp_path / "inst",
                solutions_dir=tmp_path / "sol", verbose=False)
    assert len(again) == 6
    more = run(cells, 4, workers=1, csv=csv, instance_dir=tmp_path / "inst",
               solutions_dir=tmp_path / "sol", verbose=False)
    assert len(more) == 8                     # only the new index ran
    assert list(more.columns) == list(frame.columns)
    assert len(load_results(csv)) == 8
    assert len(dedupe(more)) <= 8
    assert len(list((tmp_path / "inst").glob("*.mosp"))) == 8
    assert (more["witness_ok"].astype(bool)).all()
    assert (more["status_default"] == "unsat").all()


def test_manifest_regenerates_every_instance(tmp_path: Path):
    from learning.ensemble import verify_manifest, write_manifest

    cells = [Cell("fixed", 8, 8, 2), Cell("bernoulli", 8, 16, 0.15)]
    frame = run(cells, 3, workers=1, csv=tmp_path / "results.csv", instance_dir=None,
                solutions_dir=tmp_path / "sol", verbose=False)
    path = write_manifest(frame, tmp_path / "manifest.csv")
    assert verify_manifest(path) == {"checked": 6, "mismatches": 0}
