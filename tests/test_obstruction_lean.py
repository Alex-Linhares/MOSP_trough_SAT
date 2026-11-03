"""loop0013 item 09: `lean/MOSPFormalization/ObstructionCertificate.lean` — a checked
certificate implies the bound. Three things are pinned here.

* The statements, re-checked in Python on small graphs with the subset-DP pathwidth as the
  oracle (the brute-force check `reports/scratch/obstruction_search/09_lean/check.py` runs the
  same functions on every graph to 8 vertices): Harper's contrapositive at every level, the
  min-degree minor bound on random legal sequences, the Bool checker against the Prop, and
  the Lean minor against the record's replay. Two statements the item's text gave are
  false without a hypothesis (`j <= n`; a nonempty minor) and are pinned false here.
* The concrete instances the Lean file decides: the 8-cycle with five contractions (min
  degree 2), `K_{3,4}` at level 1, and the record instance `Warwick 1729`, whose 22-step
  sequence in the Lean file is the record's 15 steps plus the extension in
  `warwick_extension.json`, legal, with an 8-vertex minor of minimum degree 7.
* The bookkeeping: the file is imported, has no `sorry`, every name in
  `learning.sandwich.OBSTRUCTION_PROVED` is declared in it and has a `#print axioms` line.
"""

import json
import random
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "reports" / "scratch" / "obstruction_search" / "09_lean"
LEAN = ROOT / "lean" / "MOSPFormalization" / "ObstructionCertificate.lean"
sys.path.insert(0, str(SCRATCH))
import check as ck  # noqa: E402

from learning import sandwich as sw  # noqa: E402


def _graph(n, edges):
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return adj


def _random_graph(rng, n):
    p = rng.uniform(0.2, 0.8)
    return _graph(n, [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < p])


def test_harper_contrapositive_at_every_level_and_false_above_n():
    rng = random.Random(1)
    for _ in range(60):
        n = rng.randint(1, 7)
        adj = _random_graph(rng, n)
        k = ck.vs(n, adj)
        f = ck.profile(n, adj)
        for j in range(n + 1):
            # (forall |A| = j, j + (f(j) - j - 1) < |N[A]|)  ->  f(j) - j <= pw
            assert f[j] - j <= k
        # without `j <= n`: no set has size n + 1, the premise is vacuous at every k, and
        # the conclusion k + 1 <= pw fails at k = pw
        assert not any(ck.popcount(A) == n + 1 for A in range(1 << n))


def test_min_degree_minor_bound_and_the_bool_checker():
    rng = random.Random(2)
    empty = 0
    for _ in range(80):
        n = rng.randint(1, 7)
        adj = _random_graph(rng, n)
        k = ck.vs(n, adj)
        seq = ck.random_legal_seq(rng, n, adj, rng.randint(0, n))
        assert ck.is_contraction_seq(adj, seq)
        assert ck.check_seq_bool(adj, seq)
        H = ck.apply_seq(adj, seq)
        S = ((1 << n) - 1) & ~ck.removed(seq)
        assert ck.min_degree_in(H, S) <= k
        assert ck.min_degree_in(H, rng.randrange(1 << n)) <= k
        # removed vertices are isolated, so the survivors' degrees are the minor's
        assert all(H[v] == 0 for v in range(n) if not S >> v & 1)
        # the Lean minor is the record's replay
        rec = ck.replay_record(n, adj, seq)
        assert rec is not None
        alive, cur = rec
        assert alive == S and all((cur[v] & S) == (H[v] & S) for v in range(n) if S >> v & 1)
        if S == 0:
            empty += 1
    # the item's phrasing without nonemptiness is vacuous on sequences that remove everything
    assert empty > 0


def test_an_illegal_step_is_refused_by_both_forms():
    adj = _graph(4, [(0, 1), (1, 2), (2, 3)])
    assert not ck.check_seq_bool(adj, [(3, 0)])            # 3 and 0 are not adjacent
    assert not ck.is_contraction_seq(adj, [(3, 0)])
    assert ck.check_seq_bool(adj, [(3, 2), (2, 1)])          # 3 into 2, then 2 into 1
    assert ck.check_seq_bool(adj, [(0, None), (0, 1)]) is False  # 0 isolated: no edge 0-1 left


def test_the_two_toy_instances_decided_in_lean():
    # the 8-cycle: five contractions into 0 leave a triangle, min degree 2 = pathwidth
    adj = _graph(8, [(i, (i + 1) % 8) for i in range(8)])
    seq = [(7, 0), (6, 0), (5, 0), (4, 0), (3, 0)]
    assert ck.check_seq_bool(adj, seq)
    H = ck.apply_seq(adj, seq)
    S = 0xFF & ~ck.removed(seq)
    assert S == 0b111 and ck.min_degree_in(H, S) == 2 and ck.vs(8, adj) == 2
    # K_{3,4} at level 1: every singleton has |N[A]| = 4 > 1 + 2, and pathwidth 3
    adj = _graph(7, [(a, b) for a in range(3) for b in range(3, 7)])
    f = ck.profile(7, adj)
    assert f[1] == 4 and ck.vs(7, adj) == 3
    assert max(f[j] - j for j in range(8)) == 3


def _lean_literal(name):
    text = LEAN.read_text()
    m = re.search(rf"def {name} : [^\n]*:=\n((?:  [^\n]*\n)+)", text)
    assert m, name
    return [tuple(int(x) for x in re.findall(r"\d+", pair))
            for pair in re.findall(r"\([^()]*\)", m.group(1))]


def test_warwick_record_certificate_matches_the_lean_literal():
    cert_dir = (ROOT / "reports/scratch/obstruction_search/04_minor/certificates"
                / "Warwick_1729__balanced_orders__3_orders_per_product")
    cert = json.loads((cert_dir / "ladder.json").read_text())
    ext = json.loads((SCRATCH / "warwick_extension.json").read_text())
    assert cert["c_status"] == "bound" and cert["c_lower"] == 7 and cert["floor"] == 8
    assert [list(p) for p in ext["sequence_record"]] == cert["sequence"]
    full = [tuple(p) for p in ext["full_sequence"]]
    assert full == [tuple(p) for p in ext["sequence_record"]] + [tuple(p) for p in ext["extension_least_c"]]
    assert _lean_literal("warwickSeq") == full
    # the instance's ones, row by row, are the Lean literal
    rows = [ln.split() for ln in (cert_dir / "instance.mosp").read_text().splitlines()[2:]]
    ones = [(i, j) for i in range(len(rows)) for j in range(len(rows[0])) if rows[i][j] == "1"]
    assert _lean_literal("warwickOnes") == ones
    # the MOSP graph, the sequence's legality, the 8-vertex K8 minor of minimum degree 7
    n = len(rows)
    adj = [0] * n
    for j in range(len(rows[0])):
        cs = [i for i in range(n) if rows[i][j] == "1"]
        for a in cs:
            for b in cs:
                if a != b:
                    adj[a] |= 1 << b
    assert sum(bin(x).count("1") for x in adj) // 2 == cert["graph_edges"]
    assert ck.check_seq_bool(adj, full)
    H = ck.apply_seq(adj, full)
    S = ((1 << n) - 1) & ~ck.removed(full)
    assert bin(S).count("1") == 8 and ck.min_degree_in(H, S) == 7
    # the record's own 15-vertex minor has minimum degree 5: the C's `lower = 7` is its
    # contraction degeneracy, which is why the extension is needed
    H15 = ck.apply_seq(adj, [tuple(p) for p in cert["sequence"]])
    S15 = ((1 << n) - 1) & ~ck.removed([tuple(p) for p in cert["sequence"]])
    assert bin(S15).count("1") == cert["m"] and ck.min_degree_in(H15, S15) == 5


def test_lean_bookkeeping():
    text = LEAN.read_text()
    root = (ROOT / "lean" / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.ObstructionCertificate" in root
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("--"))
    assert not re.search(r"\bsorry\b", code.split("-/", 1)[1])
    assert not re.search(r"^\s*axiom\b", code, re.M)
    axioms = (ROOT / "paper1" / "axiom_check.lean").read_text()
    for name in sw.OBSTRUCTION_PROVED:
        short = name.split(".")[-1]
        assert re.search(rf"^theorem {re.escape(short)}\b", text, re.M), name
        assert f"#print axioms MOSPFormalization.{name}\n" in axioms, name
    assert set(sw.OBSTRUCTION_PROVED) <= set(sw.ALL_PROVED)
    for name in ("eight_le_mospValue_warwick", "two_le_pathwidth_octGraph", "three_le_pathwidth_k34",
                 "pathwidth_ge_of_unsat", "pathwidth_ge_of_checkSeq"):
        assert name in sw.OBSTRUCTION_PROVED


@pytest.mark.skipif(not (SCRATCH / "run.log").exists(), reason="no check log")
def test_brute_force_log_reports_no_violation():
    log = (SCRATCH / "run.log").read_text()
    assert "TOTAL graphs=13598" in log and "violations={}" in log.splitlines()[-2]
