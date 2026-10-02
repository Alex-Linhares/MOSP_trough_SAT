"""The benchmark runner's result format (loop0007 item 08, the two issues of
`TRANSFER.md`): the name is the path, and an unproved width has an empty proof."""

import csv
import subprocess
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1] / "bench"
sys.path.insert(0, str(BENCH))

import run  # noqa: E402
from readers import HERE, SETS  # noqa: E402

needs_instances = pytest.mark.skipif(not (HERE / "vsplib" / "tree").is_dir(),
                                     reason="bench/instances/ is git-ignored and not present")


@needs_instances
def test_the_tree_folders_get_distinct_keys():
    paths = SETS["vsplib-tree"]()
    keys = [run.key(p) for p in paths]
    assert len(set(keys)) == len(keys) == 50
    assert len({run.stem(k) for k in keys}) == 35        # what the old `name` column could tell apart
    assert all(k.startswith("vsplib/tree/") for k in keys)


@needs_instances
def test_a_proved_row_and_an_unproved_row():
    path = next(p for p in SETS["vsplib-tree"]() if "TREE_22_3" in p.name)
    row = run.one("vsplib-tree", path, 30.0, "repaired")
    assert row["proof"] in run.PROVED and row["width"] == 3 and row["error"] == ""
    grid = next(p for p in SETS["vsplib-grids"]() if p.name.startswith("grid_14."))
    row = run.one("vsplib-grids", grid, 0.5, "repaired")
    assert row["proof"] == "" and row["error"] == "" and row["width"] >= 14   # unproved: empty, not "budget"


@needs_instances
def test_both_rule_settings_prove_the_same_tree(tmp_path):
    path = next(p for p in SETS["vsplib-tree"]() if "TREE_67_4" in p.name)
    a = run.one("vsplib-tree", path, 30.0, "repaired")
    b = run.one("vsplib-tree", path, 30.0, "published")
    assert (a["rules"], b["rules"]) == ("repaired", "published")
    assert a["width"] == b["width"] == 4 and a["proof"] and b["proof"]


@needs_instances
def test_resume_skips_what_is_done_and_the_hard_cap_kills(tmp_path):
    out = tmp_path / "t.csv"
    names = tmp_path / "names.txt"
    names.write_text("TREE_22_3_rot1\nDorogovtsevGoltsevMendesGraph\n")
    cmd = [sys.executable, str(BENCH / "run.py"), "vsplib-tree", "--names", str(names), "--out", str(out),
           "--procs", "2", "--time", "10"]
    subprocess.run(cmd, check=True, capture_output=True)
    first = list(csv.DictReader(out.open()))
    assert len(first) == 3                                     # the stem matches all three rotation folders
    subprocess.run(cmd + ["--resume"], check=True, capture_output=True)
    assert list(csv.DictReader(out.open())) == first           # nothing re-run, nothing lost
    kill = [sys.executable, str(BENCH / "run.py"), "named", "--names", str(names), "--out", str(tmp_path / "k.csv"),
            "--time", "5", "--hard", "2"]
    subprocess.run(kill, check=True, capture_output=True)
    (row,) = csv.DictReader((tmp_path / "k.csv").open())
    assert row["proof"] == "" and row["error"].startswith("killed")
