"""`paper2/search_soundness.md` quotes the search's code; the quotes must still be there.

§2 of the document states each pruning rule "as the fixed code implements it"
and quotes the lines. A quote that has drifted from the source would make the
statement a statement about code that no longer exists, so every fenced block
tagged `# Py:` or `/* C:` is checked line by line against the file it cites,
up to indentation, `...` elisions and the trailing `/* ... */` annotations the
document adds.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "paper2" / "search_soundness.md"
SOURCES = {
    "Py": ROOT / "satisfiability" / "customer_search.py",
    "C": ROOT / "satisfiability" / "customer_search.c",
}


def _blocks() -> list[tuple[str, list[str]]]:
    text = DOC.read_text()
    out = []
    for body in re.findall(r"```(?:python|c)\n(.*?)```", text, flags=re.S):
        lines = body.splitlines()
        head = re.match(r"\s*(?:#|/\*)\s*(Py|C):", lines[0])
        if head:
            out.append((head.group(1), lines[1:]))
    return out


def _normalise(line: str) -> str:
    line = re.sub(r"/\*.*?\*/\s*$", "", line)
    return " ".join(line.split())


def test_the_document_quotes_both_implementations():
    tags = {tag for tag, _ in _blocks()}
    assert tags == {"Py", "C"}
    assert len(_blocks()) >= 6


def test_every_quoted_line_is_in_the_cited_source():
    sources = {tag: {_normalise(line) for line in path.read_text().splitlines()}
               for tag, path in SOURCES.items()}
    missing = []
    for tag, lines in _blocks():
        for line in lines:
            norm = _normalise(line)
            if not norm or norm == "...":
                continue
            if norm not in sources[tag]:
                missing.append((tag, line))
    assert not missing, missing


def test_the_rule_order_quoted_is_the_one_the_c_runs():
    c = SOURCES["C"].read_text()
    default = c[c.index("} else {\n        if (s->subset_rule)"):]
    assert default.index("subset_pass") < default.index("better_move_pass")
