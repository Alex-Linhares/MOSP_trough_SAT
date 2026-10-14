"""paper1/dataset_check.py: the independent checker accepts good records and
rejects each kind of bad one."""
import copy
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "paper1"))
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


def grid(h, w):
    """The h x w grid, vertex i * w + j at row i, column j."""
    E = [(i * w + j, i * w + j + 1) for i in range(h) for j in range(w - 1)]
    E += [(i * w + j, (i + 1) * w + j) for i in range(h - 1) for j in range(w)]
    return sorted((min(a, b), max(a, b)) for a, b in E)


def column_major(h, w):
    """Column by column: width h. Row by row (`range(h * w)`) has width w."""
    return [i * w + j for j in range(w) for i in range(h)]


def short_side(h, w):
    return column_major(h, w) if h <= w else list(range(h * w))


def theorem_record(h, w, edges=None, width=None, layout=None, claim=None):
    th = dict(family="grid", h=h, w=w, theorem="Ellis & Warren (2008), Theorem 4.1",
              lean="MOSPFormalization.pathwidth_grid (lean/MOSPFormalization/Grid.lean)")
    th.update(claim or {})
    return record(h * w, grid(h, w) if edges is None else edges, min(h, w) if width is None else width,
                  short_side(h, w) if layout is None else layout, provenance="certified:theorem", theorem=th)


def test_grid_shape_recognises_grids_under_any_labelling():
    rng = __import__("random").Random(5)
    for h, w in [(2, 2), (2, 5), (3, 3), (3, 7), (6, 4), (8, 8)]:
        perm = list(range(h * w))
        rng.shuffle(perm)
        edges = [(perm[a], perm[b]) for a, b in grid(h, w)]
        assert dc.grid_shape(dc.adjacency(h * w, edges)) == (min(h, w), max(h, w))
    assert dc.grid_shape(dc.adjacency(6, CYCLE6)) is None
    assert dc.grid_shape(dc.adjacency(4, K4)) is None


def test_theorem_records_pass_on_true_grids():
    for h, w in [(4, 4), (3, 5), (5, 3)]:
        rec = theorem_record(h, w)
        assert dc.width_of_layout(dc.adjacency(h * w, rec["edges"]), rec["layout"]) == min(h, w)
        fails, facts = dc.check_record(rec)
        assert fails == [] and facts["theorem_checked"], fails


def test_forged_grid_record_is_rejected():
    # one edge of the 4 x 4 grid moved to a diagonal: same n and m, not a grid
    edges = grid(4, 4)
    edges.remove((0, 1))
    edges.append((0, 5))
    adj = dc.adjacency(16, edges)
    layout = column_major(4, 4)
    rec = theorem_record(4, 4, edges=sorted(edges), width=dc.width_of_layout(adj, layout), layout=layout)
    fails, _ = dc.check_record(rec)
    assert any("not a grid" in f for f in fails), fails
    # a true grid with the wrong value: a layout of width 5 claimed as the theorem's value
    rec = theorem_record(4, 5, width=5, layout=list(range(20)))
    fails, _ = dc.check_record(rec)
    assert any("has pathwidth 4" in f for f in fails), fails
    # the record names another shape
    fails, _ = dc.check_record(theorem_record(3, 5, claim=dict(h=4)))
    assert any("names a" in f for f in fails), fails
    # a theorem this checker does not know, or no Lean proof named, is not trusted
    for bad in (dict(family="torus"), dict(lean="")):
        fails, _ = dc.check_record(theorem_record(4, 4, claim=bad))
        assert any("no theorem" in f for f in fails), fails


def minor_record(**cert):
    c = dict(refuted=1, size=3, rule="min-d", contractions=[[0, 1], [2, 3], [4, 5]])
    c.update(cert)
    return record(6, CYCLE6, 2, [0, 1, 5, 2, 4, 3], provenance="certified:minor", minor_certificate=c)


def test_minor_record_replays_its_contractions():
    fails, facts = dc.check_record(minor_record())
    assert fails == [] and facts["minor_by_certificate"], fails
    # a deletion (null target) is a minor operation too
    fails, facts = dc.check_record(minor_record(size=5, contractions=[[3, None]]))
    assert fails == [] and facts["minor_by_certificate"], fails
    # without a sequence the record passes, but is not counted as replayed
    rec = minor_record()
    del rec["minor_certificate"]
    fails, facts = dc.check_record(rec)
    assert fails == [] and not facts["minor_by_certificate"]


def test_forged_contraction_step_is_rejected():
    fails, _ = dc.check_record(minor_record(contractions=[[0, 1], [2, 4], [4, 5]]))   # 2, 4 not adjacent
    assert any("not along an edge" in f for f in fails), fails
    fails, _ = dc.check_record(minor_record(contractions=[[0, 1], [0, 2]]))           # 0 already gone
    assert any("not in the current graph" in f for f in fails), fails
    fails, _ = dc.check_record(minor_record(size=4))
    assert any("leaves 3 vertices" in f for f in fails), fails
    fails, _ = dc.check_record(minor_record(refuted=2))                               # must be width - 1
    assert any("refutes 2" in f for f in fails), fails


def test_checker_imports_nothing_from_the_repository():
    text = (Path(dc.__file__)).read_text()
    for forbidden in ("satisfiability", "pathwidth_solver", "from pathwidth", "paper1.dataset ",
                      "import dataset", "learning", "mosp."):
        assert forbidden not in text.split('"""', 2)[2], forbidden
