"""Axiom audit of every theorem the draft cites (loop0008 item 09).

    python -m paper2.latex.check_axioms            # coverage, then run Lean
    python -m paper2.latex.check_axioms --no-lean  # coverage only (no build)

Two checks.

1. **Coverage.** Every theorem or lemma named in a `\\lean{...}` footnote or a
   `\\path{...}` cell of `sec*.tex` has a `#print axioms` line in
   `paper2/axiom_check.lean`. Definitions (`def`, `structure`, ...) are
   skipped: they carry no proof.
2. **Axioms.** `lake env lean ../paper2/axiom_check.lean` is run from `lean/`,
   and every line must report exactly `propext`, `Classical.choice` and
   `Quot.sound`, except the control `conjecture_sqrt_tw_f6`, which must show
   `sorryAx`. Needs a built `lean/` (`lake build`), takes a few seconds.

Exits non-zero on any failure.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from paper2.latex.check_lean import LEAN, cited

ROOT = Path(__file__).resolve().parents[2]
AXIOM_CHECK = ROOT / "paper2" / "axiom_check.lean"
CONTROL = "conjecture_sqrt_tw_f6"
EXPECTED = {"propext", "Classical.choice", "Quot.sound"}
THEOREM = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)*"
                     r"(?:theorem|lemma)\s+([^\s:({\[]+)", re.M)


def theorem_names() -> set[str]:
    """Last components of every theorem or lemma under lean/MOSPFormalization/."""
    names: set[str] = set()
    for p in LEAN.rglob("*.lean"):
        names.update(m.group(1).split(".")[-1] for m in THEOREM.finditer(p.read_text()))
    return names


def printed() -> set[str]:
    """Last components of the names `axiom_check.lean` prints."""
    return {line.split()[-1].split(".")[-1]
            for line in AXIOM_CHECK.read_text().splitlines()
            if line.startswith("#print axioms")}


def uncovered() -> list[str]:
    theorems, have = theorem_names(), printed()
    return sorted(n for n in cited()
                  if n.split(".")[-1] in theorems and n.split(".")[-1] not in have)


def run_lean() -> tuple[int, list[str]]:
    """Run the axiom check; return (lines checked, failures)."""
    out = subprocess.run(["lake", "env", "lean", str(AXIOM_CHECK)], cwd=ROOT / "lean",
                         capture_output=True, text=True, check=False)
    text = out.stdout + out.stderr
    failures = [] if out.returncode == 0 else [f"lean exited {out.returncode}"]
    records = re.findall(r"'(\S+)' depends on axioms: \[([^\]]*)\]", text)
    records += [(n, "") for n in re.findall(r"'(\S+)' does not depend on any axioms", text)]
    for name, axioms in records:
        found = {a.strip() for a in axioms.split(",") if a.strip()}
        if name.endswith(CONTROL):
            if "sorryAx" not in found:
                failures.append(f"control {name} does not show sorryAx")
        elif found != EXPECTED:
            failures.append(f"{name}: {sorted(found)}")
    expected = sum(line.startswith("#print axioms")
                   for line in AXIOM_CHECK.read_text().splitlines())
    if len(records) != expected:
        failures.append(f"{len(records)} axiom lines for {expected} #print lines")
    return len(records), failures


def main(argv: list[str]) -> int:
    missing = uncovered()
    for n in missing:
        print(f"NOT IN axiom_check.lean: {n}")
    print(f"{len(cited())} names cited, {len(missing)} theorems without an axiom line")
    if missing:
        return 1
    if "--no-lean" in argv:
        return 0
    n, failures = run_lean()
    for f in failures:
        print(f"FAIL {f}")
    print(f"{n} theorems checked, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
