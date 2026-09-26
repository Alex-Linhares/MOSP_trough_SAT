"""Tests for learning.pwtw_exhaust (loop0003 item 14, the reserve item)."""

from __future__ import annotations

import shutil

import numpy as np
import pandas as pd
import pytest

from learning import pwtw_exhaust as px

nx = pytest.importorskip("networkx")


def _spider():
    return nx.Graph([(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6)])


def _section21_graph():
    from learning.extremal import matrix_from_key
    from learning.treewidth import masks_from_matrix

    masks = masks_from_matrix(matrix_from_key(px.SECTION21_KEY))
    g = nx.Graph()
    g.add_nodes_from(range(10))
    g.add_edges_from((i, j) for i in range(10) for j in range(i + 1, 10) if masks[i] >> j & 1)
    return g


# ----------------------------------------------------------------------------
# the C on hand-checkable graphs
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("graph, pw, tw", [
    (nx.path_graph(3), 1, 1), (nx.complete_graph(4), 3, 3), (nx.cycle_graph(5), 2, 2),
    (nx.empty_graph(5), 0, 0), (nx.empty_graph(1), 0, 0), (nx.star_graph(4), 1, 1),
    (nx.convert_node_labels_to_integers(nx.grid_2d_graph(3, 3)), 3, 3),
    (_spider(), 2, 1),                   # the 7-vertex spider: tw 1, pw 2
    (_section21_graph(), 5, 3),          # §21's record: pw 5, tw 3
])
def test_c_values_by_hand(graph, pw, tw):
    parsed = px.census_stream(px.graph6_of(graph), min_diff=0, level=2)
    assert len(parsed["found"]) == 1
    rec = parsed["found"][0]
    assert (rec["pw"], rec["tw"], rec["n"], rec["edges"]) == (pw, tw, graph.number_of_nodes(), graph.number_of_edges())
    assert parsed["hist"] == [{"n": graph.number_of_nodes(), "pw": pw, "tw": tw, "count": 1}]
    assert parsed["totals"][0]["graphs"] == 1


def test_graph6_round_trip_is_the_c_parser():
    """A graph6 string produced by networkx yields the right edge count in the C
    (the parser's bit order is the only thing that could go wrong)."""
    rng = np.random.default_rng(3)
    graphs = [nx.gnp_random_graph(int(rng.integers(2, 12)), 0.4, seed=int(s)) for s in rng.integers(0, 10**6, 20)]
    parsed = px.census_stream(b"".join(px.graph6_of(g) for g in graphs), min_diff=-100, level=2)
    assert [r["edges"] for r in parsed["found"]] == [g.number_of_edges() for g in graphs]
    assert [r["n"] for r in parsed["found"]] == [g.number_of_nodes() for g in graphs]


def test_c_against_python_references_on_the_atlas():
    """Every graph on ≤ 7 vertices (1,252) plus 40 random graphs on 8–11:
    exact pw and tw from the C equal the Python routes."""
    graphs = [g for g in nx.graph_atlas_g() if g.number_of_nodes() >= 1]
    rng = np.random.default_rng(1)
    for _ in range(40):
        graphs.append(nx.gnp_random_graph(int(rng.integers(8, 12)), float(rng.uniform(0.15, 0.7)),
                                          seed=int(rng.integers(1 << 30))))
    frame = px.check_against_references(graphs)
    assert len(frame) == len(graphs)
    assert frame["agree"].all(), frame[~frame["agree"]]


def test_levels_never_lose_a_graph():
    """The sound skip rules of levels 0 and 1 report exactly the graphs level 2
    reports, at k = 1 (where skips actually fire) and at k = 2."""
    graphs = [g for g in nx.graph_atlas_g() if g.number_of_nodes() >= 1]
    graphs += [_spider(), _section21_graph()]
    data = b"".join(px.graph6_of(g) for g in graphs)
    for k in (1, 2):
        full = px.census_stream(data, min_diff=k, level=2)
        for level in (0, 1):
            partial = px.census_stream(data, min_diff=k, level=level)
            assert [(r["graph6"], r["pw"], r["tw"]) for r in partial["found"]] == \
                   [(r["graph6"], r["pw"], r["tw"]) for r in full["found"]]
            assert sum(t["dp_runs"] for t in partial["totals"]) < sum(t["dp_runs"] for t in full["totals"])   # the skip fires
            assert sum(r["count"] for r in partial["hist"]) == sum(r["count"] for r in full["hist"])


# ----------------------------------------------------------------------------
# the Python side
# ----------------------------------------------------------------------------


def test_clique_cover_matrix_reproduces_the_graph():
    from learning.treewidth import masks_from_graph, masks_from_matrix

    for g in (_spider(), _section21_graph(), nx.complete_graph(4), nx.empty_graph(3)):
        matrix = px.clique_cover_matrix(g)
        assert masks_from_matrix(matrix) == masks_from_graph(g)


def test_verify_graph_on_the_spider_without_recertify():
    out = px.verify_graph(px.graph6_of(_spider()).decode().strip(), recertify=False)
    assert (out["n"], out["edges"], out["pw_python"], out["tw_c"], out["tw_reference"],
            out["tw_order_width"], out["omega"]) == (7, 6, 2, 1, 1, 1, 2)
    assert out["is_section21_graph"] is False and out["contains_section21_graph"] is False


def test_verify_graph_recognises_section21():
    out = px.verify_graph(px.graph6_of(_section21_graph()).decode().strip(), recertify=False)
    assert out["is_section21_graph"] and out["contains_section21_graph"]
    assert (out["pw_python"], out["tw_c"], out["omega"]) == (5, 3, 4)


def test_vertex_minimality_of_the_gap():
    """§21's graph is vertex-minimal for pw − tw = 2 (every deletion has gap
    ≤ 1; it must be, since no 9-vertex graph has the gap); the same graph plus
    an isolated vertex is not (deleting the isolated vertex keeps the gap)."""
    g = _section21_graph()
    out = px.verify_graph(px.graph6_of(g).decode().strip(), recertify=False)
    assert out["vertex_minimal"] and out["deletions_keeping_gap"] == 0
    g11 = g.copy()
    g11.add_node(10)
    out11 = px.verify_graph(px.graph6_of(g11).decode().strip(), recertify=False)
    assert (out11["n"], out11["pw_python"], out11["tw_c"], out11["components"]) == (11, 5, 3, 2)
    assert not out11["vertex_minimal"] and out11["deletions_keeping_gap"] == 1
    assert out11["contains_section21_graph"] and out11["edges_added_to_section21"] is None
    summary = px.large_summary(pd.DataFrame([out11 | {"pw": 5, "tw": 3, "recertified": False, "agree": True}]))
    assert summary.iloc[0]["graphs"] == 1 and summary.iloc[0]["pw−tw=2"] == 1
    assert summary.iloc[0]["contain §21's graph"] == 1 and summary.iloc[0]["vertex-minimal"] == 0
    assert summary.iloc[0]["connected"] == 0


def test_parse_and_tables_on_a_toy(tmp_path, monkeypatch):
    text = "FOUND ItCXTbAvG 10 5 3 21\nHIST 10 5 3 1\nHIST 10 4 4 7\nHIST 9 3 -1 5\nTOTAL 10 8 8 1 1 2 1\nTOTAL 9 5 5 0 0 2 1\n"
    parsed = px.parse_output(text)
    assert parsed["found"][0]["edges"] == 21 and len(parsed["hist"]) == 3 and len(parsed["totals"]) == 2
    census = pd.DataFrame(parsed["hist"])
    diff = px.diff_table(census).set_index("n")
    assert diff.loc[10, "pw−tw=2"] == 1 and diff.loc[10, "pw−tw=0"] == 7 and diff.loc[10, "max pw−tw"] == 2
    assert diff.loc[9, "skipped (pw−tw<k proved)"] == 5 and np.isnan(diff.loc[9, "share pw>tw"])
    assert diff.loc[10, "share pw>tw"] == pytest.approx(1 / 8)
    joint = px.joint_table(census, 10)
    assert list(joint.columns) == ["", "tw=3", "tw=4"] and joint.iloc[1].tolist() == ["pw=5", 1, 0]
    totals = pd.DataFrame([{"n": 10, "graphs": 12005168, "level": 2, "seconds": 17.4, "workers": 16}])
    priced = px.price(totals)
    per_graph = 17.4 * 16 / 12005168
    assert priced["core-µs per graph"].iloc[0] == pytest.approx(per_graph * 1e6)
    assert priced["n=12 at this rate, core-hours"].iloc[0] == pytest.approx(
        px.GRAPH_COUNTS[12] * per_graph * (24 / 10) ** 2 / 3600)


def test_replace_rows_keeps_other_n(tmp_path):
    path = tmp_path / "x.csv"
    px._replace_rows(path, pd.DataFrame({"n": [9, 9], "pw": [1, 2], "tw": [1, 1], "count": [3, 4]}), 9)
    px._replace_rows(path, pd.DataFrame({"n": [10], "pw": [5], "tw": [3], "count": [1]}), 10)
    px._replace_rows(path, pd.DataFrame({"n": [9], "pw": [1], "tw": [1], "count": [99]}), 9)
    frame = pd.read_csv(path)
    assert frame["n"].tolist() == [9, 10] and frame["count"].tolist() == [99, 1]


@pytest.mark.skipif(px.geng_path() is None, reason="nauty-geng not installed")
def test_geng_census_at_n5_matches_the_atlas(tmp_path, monkeypatch):
    """The run stage on n = 5 (34 graphs) gives the same joint histogram as the
    C on the atlas's 34 five-vertex graphs, and the committed-CSV writers land
    in the redirected directory."""
    monkeypatch.setattr(px, "SCRATCH", tmp_path / "scratch")
    monkeypatch.setattr(px, "CENSUS_CSV", tmp_path / "census.csv")
    monkeypatch.setattr(px, "FOUND_CSV", tmp_path / "found.csv")
    monkeypatch.setattr(px, "TOTALS_CSV", tmp_path / "totals.csv")
    px.run(5, workers=1, min_n=5, log=lambda *a: None)
    census = pd.read_csv(tmp_path / "census.csv")
    totals = pd.read_csv(tmp_path / "totals.csv")
    assert totals["graphs"].iloc[0] == 34 and bool(totals["complete"].iloc[0])
    atlas5 = [g for g in nx.graph_atlas_g() if g.number_of_nodes() == 5]
    parsed = px.census_stream(b"".join(px.graph6_of(g) for g in atlas5), min_diff=2, level=2)
    expected = pd.DataFrame(parsed["hist"]).sort_values(["pw", "tw"]).reset_index(drop=True)
    got = census.sort_values(["pw", "tw"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(got[["n", "pw", "tw", "count"]], expected[["n", "pw", "tw", "count"]])
    assert pd.read_csv(tmp_path / "found.csv").empty


def test_committed_census_says_zero_below_ten_and_four_at_ten():
    """The committed result this section rests on: no graph on ≤ 9 vertices
    has pw − tw ≥ 2; exactly four on 10 vertices do, each containing §21's."""
    if not px.CENSUS_CSV.exists():
        pytest.skip("census not run")
    totals = pd.read_csv(px.TOTALS_CSV).set_index("n")
    assert all(totals.loc[n, "complete"] for n in range(1, 11))
    assert all(totals.loc[n, "found"] == 0 for n in range(1, 10))
    assert totals.loc[10, "found"] == 4
    found = pd.read_csv(px.FOUND_CSV)
    ten = found[found["n"] == 10]
    assert len(ten) == 4 and ten["is_section21_graph"].sum() == 1 and ten["contains_section21_graph"].all()
    assert ten["agree"].all() and ten["recertified"].all()
    if 11 in totals.index:
        assert totals.loc[11, "complete"] and totals.loc[11, "graphs"] == px.GRAPH_COUNTS[11]
        eleven = found[found["n"] == 11]
        assert len(eleven) == totals.loc[11, "found"] == 1034
        assert ((eleven["pw"] - eleven["tw"]) == 2).all()              # no pw − tw = 3 at 11
        assert eleven.groupby(["pw", "tw"]).size().to_dict() == {(4, 2): 12, (5, 3): 396, (6, 4): 626}
        census = pd.read_csv(px.CENSUS_CSV)
        assert (census.loc[census["n"] == 11, "tw"] >= 0).all()           # level 2: the joint histogram is complete
        assert int(census.loc[(census["n"] == 11) & (census["tw"] <= 1), "count"].sum()) == px.FOREST_COUNTS[11]
