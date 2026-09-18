"""Guards on the compute ledger.

The figure this produces gets quoted in the README and the paper plan, and a
quoted number nobody recomputes is one that drifts -- several did this week,
which is why it is computed rather than maintained. These tests pin that it
counts what it claims: core-seconds of solver work, from both record shapes.
"""

import csv

from benchmarks.compute import record, totals


def test_it_totals_both_record_shapes(tmp_path):
    """Old sweeps wrote `time_seconds` CSVs; the drivers now append a ledger."""
    legacy = tmp_path / "sweep.csv"
    with legacy.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["instance_name", "time_seconds", "status"])
        w.writerow(["a", "3600", "solved"])
        w.writerow(["b", "1800", "solved"])

    record("csearch", [("c", 7200.0), ("d", 900.0)],
           ledger=tmp_path / "compute_ledger.csv")

    rows = totals(tmp_path)
    assert sum(hours for _, hours, _ in rows) == (3600 + 1800 + 7200 + 900) / 3600
    assert sum(count for _, _, count in rows) == 4


def test_the_ledger_appends_rather_than_replaces(tmp_path):
    """A second sweep must add to the total, not overwrite the first."""
    ledger = tmp_path / "compute_ledger.csv"
    record("csearch", [("a", 60.0)], ledger=ledger)
    record("reheuristic", [("b", 120.0)], ledger=ledger)

    rows = list(csv.DictReader(ledger.open()))
    assert [r["driver"] for r in rows] == ["csearch", "reheuristic"]
    assert sum(float(r["seconds"]) for r in rows) == 180.0
    assert totals(tmp_path)[0][1] == 180 / 3600


def test_an_empty_sweep_writes_nothing(tmp_path):
    ledger = tmp_path / "compute_ledger.csv"
    assert record("csearch", [], ledger=ledger) == 0
    assert not ledger.exists()


def test_unreadable_and_timeless_files_are_skipped(tmp_path):
    """A CSV with no time column contributes nothing rather than crashing."""
    (tmp_path / "notes.csv").write_text("instance,value\na,3\n")
    (tmp_path / "broken.csv").write_bytes(b"\x00\x01binary")
    record("csearch", [("a", 3600.0)], ledger=tmp_path / "compute_ledger.csv")

    rows = totals(tmp_path)
    assert [name for name, _, _ in rows] == ["compute_ledger.csv"]
    assert rows[0][1] == 1.0
