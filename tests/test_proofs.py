"""Guards on the DRAT proof path (`learning.proofs`).

The item's acceptance tests are the first two: a four-customer instance's
refutation produces a proof drat-trim verifies, and a corrupted proof fails.
Beside them: a claim that is false (`optimum` one too high) yields `sat` and no
proof, the trace read back from CaDiCaL is complete (it ends with the empty
clause -- the thing pysat's own `get_proof` loses), the certificate carries
enough preprocessing to rebuild the CNF byte for byte on a decomposable
instance, and the lemma counter reads a hand-built binary proof.
"""

import gzip
import hashlib
import json
from pathlib import Path

import pytest

from learning.proofs import (
    DRAT_TRIM,
    check_proof,
    count_lemmas,
    drat_trim_available,
    rebuild_cnf,
    backfill,
    recheck,
    refute_with_proof,
    summarise,
)
from mosp.instance import MOSPInstance

pytestmark = pytest.mark.skipif(
    not drat_trim_available(),
    reason=f"{DRAT_TRIM} not built (cd tools/drat-trim && gcc drat-trim.c -std=gnu99 -O2 -o drat-trim)",
)

# Four customers on a cycle: each product is shared by two consecutive
# customers. The MOSP graph is C4, pathwidth 2, so the optimum is 3: no product
# order keeps two stacks open throughout, and 3 is trivially achievable.
CYCLE4 = [
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
    [1, 0, 0, 1],
]
OPTIMUM = 3


def test_four_customer_proof_checks(tmp_path):
    inst = MOSPInstance.from_matrix(CYCLE4, name="c4")
    cert = refute_with_proof(inst, OPTIMUM, "hand", deadline_seconds=60, proof_dir=tmp_path)
    assert cert.status == "unsat"
    assert cert.verdict == "verified"
    assert cert.k == 2
    assert cert.components == 1 and cert.refuted_component == 0
    assert cert.proof_lemmas > 0 and cert.proof_bytes > 0
    proof_path = tmp_path / f"{cert.proof_stem}.drat.gz"
    cert_path = tmp_path / f"{cert.proof_stem}.json"
    assert proof_path.exists() and cert_path.exists()
    with gzip.open(proof_path, "rb") as fh:
        proof = fh.read()
    assert hashlib.sha256(proof).hexdigest() == cert.proof_sha256
    # the trace is complete: CaDiCaL's last record is the empty clause `a 0`
    assert proof.endswith(b"a\x00")
    # and the stored certificate re-checks from the original instance alone
    verdict, _seconds, hash_ok = recheck(cert.proof_stem, inst, tmp_path)
    assert verdict == "verified" and hash_ok


def test_corrupted_proof_fails(tmp_path):
    inst = MOSPInstance.from_matrix(CYCLE4, name="c4")
    cert = refute_with_proof(inst, OPTIMUM, "hand", deadline_seconds=60, proof_dir=tmp_path)
    assert cert.verdict == "verified"
    with gzip.open(tmp_path / f"{cert.proof_stem}.drat.gz", "rb") as fh:
        proof = fh.read()
    dimacs = rebuild_cnf(json.loads((tmp_path / f"{cert.proof_stem}.json").read_text()), inst)
    cnf_path = tmp_path / "f.cnf"
    cnf_path.write_bytes(dimacs)

    # (a) truncated: the derivation never reaches the empty clause. Half the
    # bytes, not most of them: drat-trim verifies as soon as the lemmas so far
    # yield a conflict, and CaDiCaL's trace goes on with deletions after that
    # point (on this instance the conflict sits at about 60% of the bytes).
    truncated = tmp_path / "truncated.drat"
    truncated.write_bytes(proof[: len(proof) // 2])
    assert check_proof(cnf_path, truncated, timeout=60)[0] == "not_verified"
    empty = tmp_path / "empty.drat"
    empty.write_bytes(b"")
    assert check_proof(cnf_path, empty, timeout=60)[0] == "not_verified"

    # (d) one literal of the first lemma negated (bit 0 of a binary DRAT
    # literal is its sign): the lemma no longer follows
    flipped = bytearray(proof)
    assert flipped[0] == ord("a")
    flipped[1] ^= 1
    altered = tmp_path / "altered.drat"
    altered.write_bytes(bytes(flipped))
    assert check_proof(cnf_path, altered, timeout=60)[0] == "not_verified"

    # (b) a lemma that does not follow: the unit clause `1` prepended, which
    # fixes variable 1 without justification; drat-trim rejects it (or, if the
    # empty clause is then reached through it, rejects the proof as a whole)
    bogus = tmp_path / "bogus.drat"
    bogus.write_bytes(b"a" + bytes([2, 0]) + proof)
    assert check_proof(cnf_path, bogus, timeout=60)[0] == "not_verified"

    # (c) the wrong formula: the proof of k = 2 checked against k = 3's CNF,
    # which is satisfiable (3 is the optimum), so no sound checker can accept
    # any refutation of it. (Checking it against k = 1's CNF is *not* a
    # corruption test: a stricter formula may well admit the weaker proof.)
    from learning.proofs import cnf_dimacs
    from satisfiability.mosp_encoding import encode_mosp_decision

    sat_cnf, _pool, _m = encode_mosp_decision(inst, OPTIMUM)
    other_cnf = tmp_path / "k3.cnf"
    other_cnf.write_bytes(cnf_dimacs(sat_cnf))
    good = tmp_path / "good.drat"
    good.write_bytes(proof)
    assert check_proof(other_cnf, good, timeout=60)[0] == "not_verified"


def test_false_claim_is_sat_and_leaves_no_proof(tmp_path):
    inst = MOSPInstance.from_matrix(CYCLE4, name="c4")
    cert = refute_with_proof(inst, OPTIMUM + 1, "hand", deadline_seconds=60, proof_dir=tmp_path)
    assert cert.status == "sat"
    assert cert.verdict == ""
    assert list(tmp_path.iterdir()) == []


def test_decomposed_instance_records_the_refuted_component(tmp_path):
    # two disjoint copies of the 4-cycle, the second with a dominated extra
    # column (a product needed by customer 4 only, inside product 4's set)
    matrix = [row + [0] * 5 for row in CYCLE4] + [[0] * 4 + row + [row[0]] for row in CYCLE4]
    inst = MOSPInstance.from_matrix(matrix, name="two_cycles")
    cert = refute_with_proof(inst, OPTIMUM, "hand", deadline_seconds=60, proof_dir=tmp_path)
    assert cert.status == "unsat" and cert.verdict == "verified"
    assert cert.components == 2
    assert cert.refuted_component in (0, 1)
    assert len(cert.component_customers) == 4
    stored = json.loads((tmp_path / f"{cert.proof_stem}.json").read_text())
    if cert.refuted_component == 1:
        assert cert.dominance_dependents, "the dominated column should have been dropped"
        assert len(cert.dominance_kept) == 4
    assert hashlib.sha256(rebuild_cnf(stored, inst)).hexdigest() == cert.cnf_sha256
    verdict, _s, hash_ok = recheck(cert.proof_stem, inst, tmp_path)
    assert verdict == "verified" and hash_ok


def test_count_lemmas_reads_binary_drat():
    # `a 1 -2 0`, `d 1 -2 0`, `a 300 0` (300 -> 600, varint 0xD8 0x04), `a 0`
    proof = (b"a" + bytes([2, 5, 0])
             + b"d" + bytes([2, 5, 0])
             + b"a" + bytes([0xD8, 0x04, 0])
             + b"a" + bytes([0]))
    assert count_lemmas(proof) == 3


def test_summarise_counts_checked_and_censored():
    import pandas as pd

    frame = pd.DataFrame([
        {"instance_name": "a", "collection": "x", "n_customers": 8, "n_patterns": 5,
         "optimum": 3, "status": "unsat", "verdict": "verified", "components": 1,
         "dominated_removed": 0, "cnf_clauses": 10, "solve_seconds": 0.1,
         "check_seconds": 0.05, "proof_bytes": 100, "proof_gz_bytes": 50, "proof_lemmas": 4},
        {"instance_name": "b", "collection": "x", "n_customers": 35, "n_patterns": 5,
         "optimum": 3, "status": "timeout", "verdict": "", "components": 1,
         "dominated_removed": 0, "cnf_clauses": 10, "solve_seconds": 90.0,
         "check_seconds": 0.0, "proof_bytes": 0, "proof_gz_bytes": 0, "proof_lemmas": 0},
        {"instance_name": "c", "collection": "x", "n_customers": 35, "n_patterns": 5,
         "optimum": 3, "status": "unsat", "verdict": "not_verified", "components": 1,
         "dominated_removed": 2, "cnf_clauses": 10, "solve_seconds": 1.0,
         "check_seconds": 1.0, "proof_bytes": 10, "proof_gz_bytes": 5, "proof_lemmas": 1},
    ])
    tables = summarise(frame)
    totals = tables["totals"].iloc[0]
    assert totals["instances"] == 3 and totals["checked"] == 1
    assert totals["timeout"] == 1 and totals["not_verified"] == 1
    band = tables["by_band"]
    assert band.loc["≤10", "checked"] == 1
    assert band.loc["31–40", "checked"] == 0 and band.loc["31–40", "unsat_unchecked"] == 1


def test_backfill_restores_only_missing_rows(tmp_path):
    import pandas as pd

    cols = ["instance_name", "source_file", "status", "conflict_budget"]
    first = pd.DataFrame([["a", "f", "unsat", 200000], ["b", "f", "budget", 200000],
                          ["c", "f", "budget", 200000]], columns=cols)
    table = pd.DataFrame([["a", "f", "unsat", 200000], ["b", "f", "unsat", 1000000]], columns=cols)
    first.to_csv(tmp_path / "first.csv", index=False)
    table.to_csv(tmp_path / "table.csv", index=False)
    assert backfill(tmp_path / "table.csv", tmp_path / "first.csv") == 1
    out = pd.read_csv(tmp_path / "table.csv")
    assert len(out) == 3
    assert out.set_index("instance_name").loc["b", "conflict_budget"] == 1000000   # the retry's answer kept
    assert out.set_index("instance_name").loc["c", "status"] == "budget"           # the missing one restored
    assert backfill(tmp_path / "table.csv", tmp_path / "first.csv") == 0           # idempotent
