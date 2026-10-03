"""paper2/dataset_check.py: the independent checker accepts good records and
rejects each kind of bad one."""
import copy
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "paper2"))
import dataset_check as dc  # noqa: E402


def record(n, edges, width, layout, provenance="certified:refutation", **extra):
    rec = dict(id="pwc-t", n=n, m=len(edges), edges=[list(e) for e in edges], width=width,
               provenance=provenance, evidence="test", layout=layout,
               values={p: width + k for p, k in dc.OFFSETS.items()}, problems=["pathwidth"],
               members=[dict(collection="Rome graphs", problem="pathwidth", source="x", name="x",
                             to_representative=None)])
    rec.update(extra)
    return rec


PATH5 = [(0, 1), (1, 2), (2, 3), (3, 4)]
K4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
CYCLE6 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)]


def test_width_of_layout_matches_known_pathwidths():
    assert dc.width_of_layout(dc.adjacency(5, PATH5), [0, 1, 2, 3, 4]) == 1
    assert dc.width_of_layout(dc.adjacency(4, K4), [0, 1, 2, 3]) == 3
    assert dc.width_of_layout(dc.adjacency(6, CYCLE6), [0, 1, 5, 2, 4, 3]) == 2
    # a bad layout of the path has a larger width
    assert dc.width_of_layout(dc.adjacency(5, PATH5), [2, 0, 4, 1, 3]) == 2


def test_good_records_pass():
    good = [record(5, PATH5, 1, [0, 1, 2, 3, 4]),
            record(6, CYCLE6, 2, [0, 1, 5, 2, 4, 3], provenance="certified:bound",
                   lower_bound_certificate=dict(ops=[], min_degree=2)),
            record(4, K4, 3, [3, 2, 1, 0], provenance="solution")]
    for rec in good:
        fails, _ = dc.check_record(rec)
        assert fails == [], fails


def test_wrong_width_is_rejected():
    fails, _ = dc.check_record(record(5, PATH5, 2, [0, 1, 2, 3, 4]))
    assert any("layout width" in f for f in fails)


def test_layout_not_a_permutation_is_rejected():
    fails, _ = dc.check_record(record(5, PATH5, 1, [0, 1, 2, 3, 3]))
    assert any("permutation" in f for f in fails)


def test_bad_values_and_provenance_are_rejected():
    rec = record(5, PATH5, 1, [0, 1, 2, 3, 4], provenance="proved")
    rec["values"]["MOSP"] = 1
    fails, _ = dc.check_record(rec)
    assert any("value of MOSP" in f for f in fails)
    assert any("provenance" in f for f in fails)


def test_bound_needs_a_bound():
    # the path has pathwidth 1; claiming "bound" at width 1 is fine, at a cycle
    # layout width 3 it is not (the width is not a lower bound)
    bad = record(6, CYCLE6, 3, [0, 2, 4, 1, 3, 5], provenance="certified:bound")
    assert dc.width_of_layout(dc.adjacency(6, CYCLE6), bad["layout"]) == 3
    fails, _ = dc.check_record(bad)
    assert any("own bound" in f for f in fails)


def test_minor_certificate_is_replayed():
    # contracting the cycle 0-1-2-3-4-5 down to K3 keeps min degree 2
    ok = record(6, CYCLE6, 2, [0, 1, 5, 2, 4, 3], provenance="certified:bound",
                lower_bound_certificate=dict(ops=[["c", 0, 1], ["c", 2, 3], ["c", 4, 5]], min_degree=2))
    assert dc.check_record(ok)[0] == []
    bad = copy.deepcopy(ok)
    bad["lower_bound_certificate"]["ops"] = [["c", 0, 3]]      # 0 and 3 are not adjacent
    fails, _ = dc.check_record(bad)
    assert any("not along an edge" in f for f in fails)
    short = copy.deepcopy(ok)
    short["lower_bound_certificate"]["ops"] = [["d", 0]]      # the path left has min degree 1
    fails, _ = dc.check_record(short)
    assert any("reaches 1" in f for f in fails)


def test_member_map_must_be_an_isomorphism(tmp_path):
    src = tmp_path / "g.gr"
    # the path 0-1-2-3-4 relabelled: file vertex v (1-based) is record vertex perm[v-1]
    perm = [4, 3, 2, 1, 0]
    src.write_text("p tw 5 4\n1 2\n2 3\n3 4\n4 5\n")
    rec = record(5, PATH5, 1, [0, 1, 2, 3, 4])
    rec["members"] = [dict(collection="Rome graphs", problem="pathwidth", source="g.gr", name="g",
                           to_representative=perm)]
    fails, facts = dc.check_record(rec, sources=True, root=tmp_path)
    assert fails == [] and facts["sources_checked"] == 1
    src.write_text("p tw 5 4\n1 2\n2 3\n3 4\n1 5\n")             # a different path labelling
    rec["members"][0]["to_representative"] = [0, 1, 2, 3, 4]
    src.write_text("p tw 5 4\n1 3\n2 3\n3 4\n4 5\n")             # a spider, not a path
    fails, _ = dc.check_record(rec, sources=True, root=tmp_path)
    assert any("isomorphism" in f for f in fails)


def test_check_reads_a_file_and_counts_provenance(tmp_path, capsys):
    p = tmp_path / "d.jsonl.gz"
    with gzip.open(p, "wt") as fh:
        fh.write(json.dumps(record(5, PATH5, 1, [0, 1, 2, 3, 4])) + "\n")
        fh.write(json.dumps(record(4, K4, 3, [0, 1, 2, 3], provenance="solution")) + "\n")
    failures, summary = dc.check(p)
    assert failures == []
    assert summary["provenance"] == {"certified:refutation": 1, "solution": 1}
    assert dc.main([str(p)]) == 0


def test_checker_imports_nothing_from_the_repository():
    text = (Path(dc.__file__)).read_text()
    for forbidden in ("satisfiability", "pathwidth_solver", "from pathwidth", "paper2.dataset ",
                      "import dataset", "learning", "mosp."):
        assert forbidden not in text.split('"""', 2)[2], forbidden
