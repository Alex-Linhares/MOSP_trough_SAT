#!/usr/bin/env python3
"""Regression gate for loop0015 (paper 3).

Passes only if all five hold:
1. `lake build` in lean/ succeeds;
2. every `.lean` file under lean/MOSPFormalization/ (top level, Complex/ and
   Search/) is imported by lean/MOSPFormalization.lean, so the build really
   checks it;
3. the number of `sorry` in Lean *code* (comments and docstrings stripped) is
   at most the baseline (0: the development has none since Appendix E) plus
   the entries in allowed_sorries.txt, and no `axiom` declaration exists;
4. `python -m pytest tests/ -q -x` passes, and so does `pytest` in
   pathwidth_solver/;
5. the papers build with no undefined references (`make -C paper1/latex check`,
   and `make -C paper3/latex check` once paper3/latex/Makefile exists; skipped
   with a printed note until then);
6. nothing under solutions/ is modified, added or deleted (`git status`), and
   paper3/latex/main.tex still carries the owner's title verbatim.

    python3 Ralph_Loops/loop0015/gate.py
"""
from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LEAN = REPO / "lean"
BASELINE_SORRIES = 0
ALLOWED = HERE / "allowed_sorries.txt"
PAPER = REPO / "paper1" / "latex"
PAPER3 = REPO / "paper3" / "latex"
TITLE = ("Exponential time hypothesis is false... but the verified algorithm is slower "
         "than trying all 2^n assignments at every practical size.")


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


def _run(cmd: list[str], cwd: Path, timeout: float) -> subprocess.CompletedProcess:
    """`subprocess.run(cmd, capture_output=True, timeout=timeout)` with two
    differences, both from the loop0014 item 01 gate hang (2026-11-02): the
    command runs in its own session, so that on timeout its whole process group
    is killed (`subprocess.run` kills only the direct child, and the forked
    pytest worker that had hung outlived the gate by an hour), and the output
    produced before the timeout travels with the exception, so that `main` can
    print which test was running."""
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace", start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        raise subprocess.TimeoutExpired(cmd, timeout, output=out)
    return subprocess.CompletedProcess(cmd, proc.returncode, out, "")


# A test that runs this long has every thread's stack dumped to stderr (pytest's
# faulthandler plugin); the test goes on, and the dump names it if the gate
# then times out. The suite takes about 5 min in all.
FAULTHANDLER = "faulthandler_timeout=900"


def _main() -> int:
    ok = True
    b = subprocess.run(["lake", "build"], cwd=LEAN, capture_output=True, text=True, errors="replace")
    tail = "\n".join((b.stdout + b.stderr).splitlines()[-25:])
    if b.returncode != 0:
        print("GATE FAIL: lake build\n" + tail); return 1
    print("lake build: ok")

    root = (LEAN / "MOSPFormalization.lean").read_text()
    for f in sorted((LEAN / "MOSPFormalization").rglob("*.lean")):
        mod = "MOSPFormalization." + ".".join(f.relative_to(LEAN / "MOSPFormalization").with_suffix("").parts)
        if not re.search(rf"^import {re.escape(mod)}\s*$", root, re.M):
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

    t = _run([sys.executable, "-m", "pytest", "tests/", "-q", "-x", "-o", FAULTHANDLER], REPO, 2400)
    print("\n".join((t.stdout + t.stderr).splitlines()[-5:]))
    if t.returncode != 0:
        print("GATE FAIL: pytest"); ok = False
    w = _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", FAULTHANDLER],
             REPO / "pathwidth_solver", 2400)
    print("\n".join((w.stdout + w.stderr).splitlines()[-3:]))
    if w.returncode != 0:
        print("GATE FAIL: pathwidth_solver pytest"); ok = False
    # The paper must build cleanly: no undefined references or citations.
    m = subprocess.run(["make", "check"], cwd=PAPER, capture_output=True, text=True, errors="replace")
    print("\n".join((m.stdout + m.stderr).splitlines()[-3:]))
    if m.returncode != 0:
        print("GATE FAIL: paper1/latex make check"); ok = False
    # Paper 3 (loop0015): same check, once its Makefile exists.
    if (PAPER3 / "Makefile").exists():
        m3 = subprocess.run(["make", "check"], cwd=PAPER3, capture_output=True, text=True, errors="replace")
        print("\n".join((m3.stdout + m3.stderr).splitlines()[-3:]))
        if m3.returncode != 0:
            print("GATE FAIL: paper3/latex make check"); ok = False
        # The owner's title, verbatim: the source carries it as `\title{... $2^n$ ...}` and
        # as the pdftitle; `$` and `\ldots` are the only LaTeX in it (paper3/README.md).
        main_tex = (PAPER3 / "main.tex").read_text() if (PAPER3 / "main.tex").exists() else ""
        norm = re.sub(r"\s+", " ", main_tex.replace("$", "").replace("\\ldots{}", "...").replace("\\ldots", "..."))
        if TITLE not in norm:
            print("GATE FAIL: paper3/latex/main.tex does not carry the owner's title verbatim"); ok = False
    else:
        print("paper3/latex/Makefile not present yet: paper 3 check skipped")
    # Nothing under solutions/ is ever written by this loop.
    sol = subprocess.run(["git", "status", "--porcelain", "--", "solutions/"], cwd=REPO,
                         capture_output=True, text=True).stdout.strip()
    if sol:
        print("GATE FAIL: solutions/ changed:\n" + "\n".join(sol.splitlines()[:10])); ok = False
    print("GATE PASS" if ok else "GATE FAIL")
    return 0 if ok else 1




def main() -> int:  # added 2026-11-02: a hung pytest (libgomp fork deadlock) held loop0012's gate for 13 h
    try:
        return _main()
    except subprocess.TimeoutExpired as e:
        tail = "\n".join((e.output or "").splitlines()[-40:])
        print(f"GATE FAIL: timeout in {e.cmd}\n{tail}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
