"""The pathwidth complex paper's LaTeX draft: its generated tables, its Lean names, its bibliography (loop0008 item 08)."""

import json
import re
from pathlib import Path

from paper1.latex import check_lean, check_refs, make_tables

HERE = Path(make_tables.__file__).resolve().parent


def test_every_cited_lean_name_is_declared():
    assert check_lean.main() == 0
    assert len(check_lean.cited()) > 50


def test_every_doi_is_in_the_checked_cache():
    """Offline: each DOI of refs.bib was fetched and compared by check_refs."""
    cache = json.loads(check_refs.CACHE.read_text())
    entries = check_refs.entries(check_refs.BIB.read_text())
    dois = [e["doi"].lower() for e in entries if e.get("doi")]
    assert len(dois) >= 30
    assert all(d in cache for d in dois)


def test_every_citation_key_is_in_the_bibliography():
    keys = {e["key"] for e in check_refs.entries(check_refs.BIB.read_text())}
    cited = set()
    for f in list(HERE.glob("sec*.tex")) + [HERE / "main.tex"]:
        for arg in re.findall(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}", f.read_text()):
            cited.update(k.strip() for k in arg.split(","))
    assert cited <= keys, cited - keys


def test_cost_table_reproduces_the_recorded_ratios():
    text = make_tables.cost_table()
    assert "1.00003" in text and "1.00004" in text      # MOSP corpus, revised_algorithm.md 4.6.2
    assert "118 of 125" in text and "1.00303" in text   # 50-100 customers
    assert "731 of 880" in text and "1.020" in text     # graph pathwidth, solver_fix.md table 4


def test_certificates_table_reproduces_the_recorded_totals():
    text = make_tables.certificates_table()
    assert "% total csearch: 6275 of 6286 verified, 0 rejected" in text
    assert "% total default: 6276 of 6286 verified, 0 rejected" in text


def test_every_cited_theorem_has_an_axiom_line():
    """Coverage half of check_axioms; the Lean half runs in the gate's build."""
    from paper1.latex import check_axioms
    assert check_axioms.uncovered() == []


# --- Appendix E, the excess phase diagram (loop0010 item 12) -----------------

def _phase_module():
    import importlib.util
    path = HERE / "figures" / "excess_phase_diagram.py"
    spec = importlib.util.spec_from_file_location("excess_phase_diagram", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _excess_of_files(directory: Path) -> dict[str, tuple[int, int, float]]:
    """(n, m, e) per instance name, read straight from the benchmark files."""
    import numpy as np
    from learning.excess import excess
    from mosp.instance import MOSPInstance
    out = {}
    for f in sorted(directory.glob("*.txt")):
        try:
            instances = MOSPInstance.from_benchmark_file(f)
        except Exception:  # noqa: BLE001 - the dataset description file
            continue
        for i, inst in enumerate(instances):
            matrix = np.asarray(inst.matrix)
            n, m = matrix.shape
            out[f"{f.stem}_{i}"] = (n, m, excess(n, m, int(matrix.sum())))   # the corpus names: file stem + index
    return out


def test_phase_diagram_csv_matches_its_sources():
    """The committed CSV behind Figure E.1 and Table E.3: the beta+ rows equal
    the tracked table of item 07; the SCOOP and Chu & Stuckey rows equal the
    excess recomputed from the benchmark files; the series rows equal
    `learning.excess.series_slopes` where its (git-ignored) input exists."""
    import pandas as pd
    mod = _phase_module()
    data = mod.load_data()
    assert set(data["kind"]) == {"collection", "scoop", "class", "series", "beta_plus"}

    plus = pd.read_csv(mod.BETA_PLUS_CSV)
    rows = data[data["kind"] == "beta_plus"].merge(plus, on=["mu", "d"], suffixes=("", "_src"))
    assert len(rows) == len(plus) == 18
    assert (rows["value"] - rows["beta_plus"]).abs().max() < 1e-5
    assert (rows["value2"] - rows["beta_star"]).abs().max() < 1e-5

    root = HERE.parents[1]
    scoop = _excess_of_files(root / "benchmarks" / "instances" / "MOSP_Instances" / "SCOOP")
    srows = data[data["kind"] == "scoop"]
    assert len(srows) == len(scoop) == 24
    for _, r in srows.iterrows():
        assert abs(scoop[r["label"]][2] - r["e"]) < 1e-5, r["label"]   # the CSV keeps six significant digits

    cs = _excess_of_files(root / "benchmarks" / "instances" / "MOSP_Instances" / "Chu_Stuckey")
    per_d: dict[int, list[float]] = {}
    for name, (n, m, e) in cs.items():
        n_cls, m_cls, d = (int(x) for x in mod._CS_CLASS.match(name).groups())
        if n_cls == m_cls:
            per_d.setdefault(d, []).append(e)
    crows = data[data["kind"] == "class"].set_index("d")
    assert sorted(crows.index) == sorted(per_d) == [2, 4, 6, 8, 10]
    for d, es in per_d.items():
        assert len(es) == crows.loc[d, "count"] == 30
        assert abs(pd.Series(es).median() - crows.loc[d, "e"]) < 1e-5

    from learning import excess as ex
    if ex.RULE_CSV.exists():
        slopes = ex.series_slopes(ex.load_rule())
        slopes = slopes[slopes["constant e"] & (slopes["generator"] == "fixed")]
        srs = data[data["kind"] == "series"]
        assert len(srs) == len(slopes)
        want = {(int(s["param"]), float(ex.RATIO_LABELS_INV[s["r"]])): (s["b"], s["se b"], s["beta* (sizes)"])
                for _, s in slopes.iterrows()}
        for _, r in srs.iterrows():
            b, se, bs = want[(int(r["d"]), float(r["mu"]))]
            assert abs(b - r["value"]) < 1e-5 and abs(se - r["value_se"]) < 1e-5 and abs(bs - r["value2"]) < 1e-5


def test_excess_table_comes_from_the_csv():
    text = make_tables.excess_table()
    data = _phase_module().load_data()
    series = data[(data["kind"] == "series") & (data["mu"] == 1.0)].set_index("d")
    plus = data[(data["kind"] == "beta_plus") & (data["mu"] == 1.0)].set_index("d")
    for d in (2, 3, 4, 6, 8, 10):
        line = next(l for l in text.splitlines() if l.startswith(f"{d} &"))
        cells = [c.strip() for c in line.rstrip(" \\").split("&")]
        assert cells[2] == f"{plus.loc[d, 'value2']:.3f}"
        assert cells[3].startswith(f"{series.loc[d, 'value']:.3f}")
        assert cells[4] == f"{plus.loc[d, 'value']:.3f}"
    assert (HERE.parent / "figures" / "excess_phase_diagram.pdf").exists()
