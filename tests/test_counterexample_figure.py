"""Figure 4.1 of the pathwidth complex paper: the definite-move counterexample, two panels."""
import re

import pytest

from paper1 import counterexample_figure as cf


def test_facts():
    f = cf.facts()
    assert f["open_stacks"] == [1, 3, 4]
    assert f["q_new"] == [0, 7, 11] and f["close"] == [0, 3, 4]
    assert f["first_moves"] == [1, 3, 4, 6]
    assert f["solvable_S"] and not f["solvable_Sq"]
    # panel (b): b(B) = 2 < 3 = b(X), the hereditary test refuses
    assert f["border_B"] == [0, 1] and f["border_X"] == [1, 7, 11]


def test_print_limits(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    pytest.importorskip("networkx")
    monkeypatch.setattr(cf, "OUT", tmp_path)
    out = [p for p in cf.draw() if p.suffix == ".pdf"][0]
    width = float(re.search(rb"/MediaBox \[\s*0 0 ([\d.]+)", out.read_bytes()).group(1))
    assert width <= 468          # 6.5 in text width, drawn at printed size
    src = open(cf.__file__).read()
    assert "set_title" not in src and "suptitle" not in src   # no title inside the figure
    sizes = [float(x) for x in re.findall(r"fontsize=([\d.]+)", src)]
    assert cf.FONT >= 7 and all(s >= 7 for s in sizes)
