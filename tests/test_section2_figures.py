"""Section 2's caption numbers reproduce from the cached OpenAlex data."""
import pytest

from paper2 import section2_figures as s2

PUBLISHED = {"graph path-width": 1213, "gate matrix layout": 110, "PLA folding": 68, "MOSP": 58,
             "vertex separation": 55, "edge search game": 38, "node search game": 34,
             "one-dimensional logic": 11, "interval thickness": 6, "narrowness": 0,
             "split bandwidth": 0, "edge separation": 0}


@pytest.fixture(scope="module")
def nums():
    return s2.numbers()


def test_relevant_counts_match_popularity_table(nums):
    assert {k: v["relevant"] for k, v in nums["names"].items()} == PUBLISHED


def test_method_paragraph_numbers(nums):
    assert nums["labelled"] == 700 and nums["labelled_relevant"] == 380
    assert nums["pathwidth_hits"] == 1571 and nums["hits_total"] == 2271
    assert nums["names"]["graph path-width"]["distinct"] == 1212
    assert nums["mosp_rank_labels"] == 4 and nums["mosp_rank_phrase_rule"] == 5
    assert nums["pathwidth_2020_24"] == 311 and nums["pathwidth_1970_2024"] == 1014


def test_network_numbers(nums):
    assert nums["citing_works"] == 844 and nums["citing_two_or_more"] == 269
    assert nums["span_two_or_more_disciplines"] == 74 and nums["span_gt_vlsi_only"] == 63
    assert nums["mosp_and_graph_theory"] == 6


def test_figures_meet_the_print_limits(tmp_path, monkeypatch):
    """No text below 7 pt, nothing wider than the 6.5 in text width (item 09)."""
    import paper2.section2_figures as s2

    seen = {}

    def capture(fig, stem):
        from matplotlib.text import Text
        sizes = [t.get_fontsize() for t in fig.findobj(Text) if t.get_text().strip()]
        out = tmp_path / f"{stem}.pdf"
        fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
        import re
        box = re.search(rb"/MediaBox \[\s*0 0 ([\d.]+)", out.read_bytes())
        seen[stem] = (min(sizes), float(box.group(1)) / 72)
        return out

    monkeypatch.setattr(s2, "_save", capture)
    nums = s2.numbers()
    s2.fig_name_usage(nums["names"])
    s2.fig_timeline()
    s2.fig_network()
    assert len(seen) == 3
    for stem, (smallest, width) in seen.items():
        assert smallest >= 7, (stem, smallest)
        assert width <= 6.5, (stem, width)
