"""loop0007 item 07: re-checking the values that rested on the customer search alone.

Two things are tested. The audit of the published rules
(`decide_native(..., repaired_rules=False, audit_repaired=True)`) never changes
the search and counts exactly the nodes where `CodeNodeRepaired` fails, as an
independent walk of the certificate (`paper1.solver_fix_recheck.node_repaired`,
its own matching, cross-checked against `search_check.d_hereditary` by
enumeration) counts them. And the records of the re-check say what the item
reports: no listed value changed, and every listed instance is either
re-refuted or listed as censored with its node count.
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd
import pytest

from paper1 import solver_fix_recheck as recheck
from paper1.search_check import (BUG_A_CEX, BUG_B_CEX, DEFINITE_CEX, RUN_LOST_CEX,
                                 better_augment, matrix_from_masks)
from satisfiability.native import RULE_COUNT_NAMES, decide_native, last_rule_counts, native_available

ROOT = Path(__file__).resolve().parent.parent
needs_native = pytest.mark.skipif(not native_available(), reason="C library unavailable")

PINNED = [m for m, *_ in DEFINITE_CEX] + [BUG_A_CEX[0], BUG_B_CEX[0], RUN_LOST_CEX[0]]


def _graphs():
    rng = random.Random(20261001)
    return PINNED + [better_augment(rng) for _ in range(12)]


@needs_native
def test_the_counters_include_the_audit():
    inst = recheck._instance("cex", matrix_from_masks(DEFINITE_CEX[0][0]))
    decide_native(inst, 6, repaired_rules=False, audit_repaired=True)
    counts = last_rule_counts()
    assert tuple(counts) == RULE_COUNT_NAMES
    assert {"audit_definite_fail", "audit_better_fail", "audit_nodes_fail"} <= set(counts)


@needs_native
def test_the_audit_audits_the_published_rules_only():
    inst = recheck._instance("cex", matrix_from_masks(DEFINITE_CEX[0][0]))
    with pytest.raises(ValueError):
        decide_native(inst, 6, repaired_rules=True, audit_repaired=True)


@needs_native
def test_the_audit_never_changes_the_search():
    for masks in _graphs():
        inst = recheck._instance("g", matrix_from_masks(masks))
        for k in range(1, len(masks) + 1):
            for better in (False, True):
                for memo, old in ((True, True), (False, True), (True, False)):
                    flags = dict(better_move=better, better_move_dominators=0, memo=memo,
                                 old_move=old)
                    plain = decide_native(inst, k, repaired_rules=False, **flags)
                    counts_plain = last_rule_counts()
                    audit = decide_native(inst, k, repaired_rules=False, audit_repaired=True,
                                          **flags)
                    counts = last_rule_counts()
                    assert (plain.status, plain.nodes, plain.order) == \
                        (audit.status, audit.nodes, audit.order)
                    assert counts_plain["audit_nodes_fail"] == 0
                    assert counts["audit_nodes_fail"] <= counts["filter_calls"]
                    assert counts["audit_nodes_fail"] == \
                        counts["audit_definite_fail"] + counts["audit_better_fail"]


@needs_native
def test_the_c_audit_counts_what_the_certificate_walk_counts():
    """Node for node on the emitter's configuration, with the enumeration oracle
    behind the walk's matching; and the counterexamples do fail somewhere, so the
    check can tell the two rule sets apart."""
    failed = 0
    for masks in _graphs():
        t = recheck._validate_one(masks, range(1, len(masks) + 1), better=False)
        t2 = recheck._validate_one(masks, range(1, len(masks) + 1), better=True)
        for r in (t, t2):
            assert r["mismatch"] == []
            assert r["same_search"] == r["same_branches"] == r["same_fail"] == r["calls"]
            assert r["oracle_disagree"] == 0
            assert r["oracle_checked"] > 0 or len(masks) > 16
            failed += r["fail_nodes"]
    assert failed > 0


def test_the_walks_matching_is_hereditary_definiteness():
    """`hereditarily_definite` against `d_hereditary` at every state of a pinned graph."""
    from paper1.search_check import d_hereditary, s_tables

    for masks in PINNED[:2] + [BUG_B_CEX[0]]:
        n = len(masks)
        O, CL = s_tables(masks)
        full = (1 << n) - 1
        for S in range(1 << n):
            if CL[S] != S or S == full:
                continue
            for q in range(n):
                if (S >> q) & 1:
                    continue
                assert recheck.hereditarily_definite(masks, full, S, O[S], q) == \
                    d_hereditary(masks, O, S, q), (S, q)


# ---------------------------------------------------------------------------
# the records
# ---------------------------------------------------------------------------

REPAIRED = recheck.csv_path("repaired")


@pytest.mark.skipif(not REPAIRED.exists(), reason="run the repaired stage first")
def test_no_listed_value_changed_and_every_instance_is_accounted_for():
    listed = pd.read_csv(recheck.PROVENANCE)
    values = dict(zip(listed.instance_name, listed.value))
    for stage in ("repaired", "audit", "cert"):
        path = recheck.csv_path(stage)
        if not path.exists():
            continue
        rows = pd.read_csv(path)
        assert set(rows.instance_name) <= set(values)
        for r in rows.itertuples(index=False):
            assert r.value == values[r.instance_name] and r.k == r.value - 1
            # a refutation of value - 1 that came back satisfiable would be the
            # finding; none did
            assert r.status in ("unsat", "unknown"), (stage, r.instance_name, r.status)
    rows = pd.read_csv(REPAIRED).drop_duplicates("instance_name", keep="last")
    assert set(rows.instance_name) == set(values)
    for r in rows.itertuples(index=False):
        assert r.nodes > 0
