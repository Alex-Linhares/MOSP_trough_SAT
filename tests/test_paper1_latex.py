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
