"""Check that every Lean name the draft cites is declared (loop0008 item 08).

    python -m paper1.latex.check_lean

Collects the names in `\\leannames{...}` (Appendix A) and `\\lean{...}`, and in `\\path{...}` cells of the section
files, and looks for a declaration of each (theorem, lemma, def, abbrev,
structure, inductive, instance, or a structure field) under
`lean/MOSPFormalization/`. A dotted name such as `NetGateMatrix.tracks_eq_mospValue`
is matched on its last component inside a file that mentions the prefix.
Exits non-zero if a name is not found. It checks existence, not that the
theorem states what the text says; that was checked by reading.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAN = HERE.parents[1] / "lean" / "MOSPFormalization"
DECL = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*"
                  r"(?:theorem|lemma|def|abbrev|structure|inductive|instance|class)\s+([^\s:({\[]+)",
                  re.M)
FIELD = re.compile(r"^\s{2,}(\w+)\s*:", re.M)


def cited() -> set[str]:
    names: set[str] = set()
    for f in sorted(HERE.glob("sec*.tex")):
        text = f.read_text()
        for arg in re.findall(r"\\lean(?:names)?\{([^}]*)\}", text):
            names.update(n.strip() for n in arg.split(","))
        for arg in re.findall(r"\\path\{([^}]*)\}", text):
            if re.fullmatch(r"[A-Za-z_.']+", arg) and not arg.endswith((".lean", "/")):
                names.add(arg)
    return {n for n in names if n}


def main() -> int:
    files = {p: p.read_text() for p in LEAN.rglob("*.lean")}
    declared: dict[str, list[Path]] = {}
    for p, text in files.items():
        for m in DECL.finditer(text):
            declared.setdefault(m.group(1).split(".")[-1], []).append(p)
        for m in FIELD.finditer(text):
            declared.setdefault(m.group(1), []).append(p)
    missing = []
    for name in sorted(cited()):
        last = name.split(".")[-1]
        prefix = name.split(".")[0] if "." in name else None
        hits = declared.get(last, [])
        if prefix:
            hits = [p for p in hits if prefix in files[p]]
        print(f"{'ok ' if hits else 'MISSING'} {name}"
              + (f"  ({hits[0].relative_to(LEAN)})" if hits else ""))
        if not hits:
            missing.append(name)
    print(f"{len(cited())} names cited, {len(missing)} not found")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
