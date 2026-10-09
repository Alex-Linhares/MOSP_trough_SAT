"""Figure 1.1 (paper1/intro_figure.py): the introduction's worked example recomputes."""
import re

from paper1 import intro_figure as f1


def test_the_two_orders():
    assert f1.profile(f1.ORDER_A) == [2, 3, 3, 2]
    assert f1.profile(f1.ORDER_B) == [2, 4, 5, 3]


def test_all_24_orders():
    assert f1.peak_counts() == {3: 2, 4: 16, 5: 6}


def test_tracks_equal_open_stacks():
    for order in (f1.ORDER_A, f1.ORDER_B):
        track, sp = f1.left_edge(order), f1.spans(order)
        # nets on one track never overlap
        for c in f1.CUSTOMERS:
            for d in f1.CUSTOMERS:
                if c < d and track[c] == track[d]:
                    assert sp[c][1] < sp[d][0] or sp[d][1] < sp[c][0]
        assert max(track.values()) + 1 == max(f1.profile(order))


def test_pathwidth_plus_one_is_the_optimum():
    assert f1.vertex_separation() == 2 == min(f1.peak_counts()) - 1
    assert f1.is_path_decomposition(f1.open_sets(f1.ORDER_A))
    assert not f1.is_path_decomposition([{"a", "b"}, {"c", "d", "e"}, {"b", "c"}, {"e", "f"}])


def test_print_limits(tmp_path, monkeypatch):
    monkeypatch.setattr(f1, "FIGS", tmp_path)
    out = f1.draw()
    width = float(re.search(rb"/MediaBox \[\s*0 0 ([\d.]+)", out.read_bytes()).group(1))
    assert width <= 468          # 6.5 in text width
    src = open(f1.__file__).read()
    assert min(float(x) for x in re.findall(r"fontsize=([\d.]+)", src)) >= 7
