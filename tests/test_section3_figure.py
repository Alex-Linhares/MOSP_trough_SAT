"""Figure 3.1 (paper1/section3_figure.py) draws the master table and meets the print limits."""
import re

from paper1 import section3_figure as s3


def test_every_edge_joins_two_drawn_nodes():
    names = set(s3.NODES)
    assert all(a in names and b in names for a, b, *_ in s3.EDGES)
    # pathwidth is the hub: the reference every exact row is attached to
    assert {"Z", "TH", "VS", "NU", "SB", "CW"} <= {a for a, b, *_ in s3.EDGES if b == "PW"}
    # the two false rows of Table 1, and nothing else, are drawn as false
    assert {a for a, b, l, kind, *_ in s3.EDGES if kind == "false"} == {"PLA", "CW"}
    assert {n for n, v in s3.NODES.items() if v[3]} == {"PLA", "CW"}
    # mpb (the thirteenth member) lives in Appendix B, not in the figure
    assert "PB" not in names


def test_print_limits(tmp_path, monkeypatch):
    monkeypatch.setattr(s3, "FIGS", tmp_path)
    out = s3.draw()
    width = float(re.search(rb"/MediaBox \[\s*0 0 ([\d.]+)", out.read_bytes()).group(1))
    assert width <= 468          # 6.5 in text width
    src = open(s3.__file__).read()
    assert min(float(x) for x in re.findall(r"fontsize=([\d.]+)", src)) >= 7
