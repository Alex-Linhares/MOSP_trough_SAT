#!/usr/bin/env python3
"""Regression gate for loop0007 (the pathwidth complex in Lean).

Passes only if all four hold:
1. `lake build` in lean/ succeeds;
2. every file under lean/MOSPFormalization/Complex/ and Search/ is imported by
   lean/MOSPFormalization.lean, so the build really checks it;
3. the number of `sorry` in Lean *code* (comments and docstrings stripped) is
   at most the baseline (1: the §24 conjecture in Sandwich.lean) plus the
   entries in allowed_sorries.txt, and no `axiom` declaration exists outside
   the baseline;
4. `python -m pytest tests/ -q -x` passes, and so does `pytest` in pathwidth_solver/.

    python3 Ralph_Loops/loop0007/gate.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LEAN = REPO / "lean"
BASELINE_SORRIES = 1
ALLOWED = HERE / "allowed_sorries.txt"


def strip_comments(src: str) -> str:
    out, i, depth = [], 0, 0
    while i < len(src):
        if src.startswith("/-", i):
            depth += 1; i += 2; continue
        if depth and src.startswith("-/", i):
            depth -= 1; i += 2; continue
        if depth:
            i += 1; continue
        if src.startswith("--", i):
            j = src.find("\n", i); i = len(src) if j < 0 else j; continue
        if src[i] == '"':
            j = i + 1
            while j < len(src) and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            i = j + 1; continue
        out.append(src[i]); i += 1
    return "".join(out)


def main() -> int:
    ok = True
    b = subprocess.run(["lake", "build"], cwd=LEAN, capture_output=True, text=True)
    tail = "\n".join((b.stdout + b.stderr).splitlines()[-25:])
    if b.returncode != 0:
        print("GATE FAIL: lake build\n" + tail); return 1
    print("lake build: ok")

    root = (LEAN / "MOSPFormalization.lean").read_text()
    for f in sorted(f for d in ("Complex", "Search") for f in (LEAN / "MOSPFormalization" / d).rglob("*.lean")):
        mod = "MOSPFormalization." + ".".join(f.relative_to(LEAN / "MOSPFormalization").with_suffix("").parts)
        if f"import {mod}" not in root:
            print(f"GATE FAIL: {mod} is not imported by MOSPFormalization.lean"); ok = False

    sorries, axioms = [], []
    for f in sorted((LEAN / "MOSPFormalization").rglob("*.lean")):
        code = strip_comments(f.read_text())
        for n, line in enumerate(code.splitlines(), 1):
            if re.search(r"\bsorry\b", line):
                sorries.append(f"{f.relative_to(LEAN)}:{n}")
            if re.match(r"\s*(private\s+)?axiom\b", line):
                axioms.append(f"{f.relative_to(LEAN)}:{n}")
    allowed = [l for l in ALLOWED.read_text().splitlines() if l.strip() and not l.startswith("#")] if ALLOWED.exists() else []
    limit = BASELINE_SORRIES + len(allowed)
    print(f"sorry in code: {len(sorries)} (limit {limit}): {sorries}")
    if len(sorries) > limit:
        print("GATE FAIL: more sorry than the baseline plus allowed_sorries.txt"); ok = False
    if axioms:
        print(f"GATE FAIL: axiom declarations: {axioms}"); ok = False

    t = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "-x"], cwd=REPO,
                       capture_output=True, text=True)
    print("\n".join((t.stdout + t.stderr).splitlines()[-5:]))
    if t.returncode != 0:
        print("GATE FAIL: pytest"); ok = False
    # The pathwidth solver is fixed by this loop too, so its own suite is part of the gate.
    w = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                       cwd=REPO / "pathwidth_solver", capture_output=True, text=True)
    print("\n".join((w.stdout + w.stderr).splitlines()[-3:]))
    if w.returncode != 0:
        print("GATE FAIL: pathwidth_solver pytest"); ok = False
    print("GATE PASS" if ok else "GATE FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
