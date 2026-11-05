#!/usr/bin/env python3
"""Section 8 of paper 3: the companion Lean, re-checked against the comparator file.

Three byte-level checks, read-only on the clone (open() only; nothing of the
clone is imported, built or run):

  1. The copy. `lean/MOSPFormalization/SubexpPathwidth/PrimitiveMachine.lean`
     says that everything after its header comment is a verbatim copy of lines
     1-190 and 220 of `lean/ComparatorChallenges/SubexponentialSAT.lean` in the
     OpenAI collection at commit 4eaee875. This script takes the lines of our
     file after the header (the first line that is `import Mathlib`) and
     compares them, byte for byte, with the clone's lines 1-190 followed by
     line 220. It also checks the clone file's SHA-256 against the hash the
     header records.
  2. The restatement. `SubexpCount k` in `Frame.lean` is said to be the body
     of the comparator theorem `exact_count_and_sat k` character for character.
     The script takes the body of our `def` (after `:=`, to the blank line) and
     the body of the clone's theorem (after the binders' `:`, to `:= by`), and
     compares them after whitespace normalisation (every run of whitespace,
     including line breaks, collapsed to one space) and, separately, line by
     line after stripping the indentation. The comparator's binders
     `(k : ℕ) (hk : 2 ≤ k)` are not part of the body: `k` is the argument of
     `SubexpCount` and `2 ≤ k` is the hypothesis of `ExactCountAndSat`.
  3. No `sorry`, no `axiom`. Neither of our two files contains the token
     `sorry` or an `axiom` declaration outside its header comment; the clone's
     comparator file contains exactly one `sorry`, at line 218, which is not
     copied.

Writes paper3/lean/rediff.log with the result of each check and the hashes.

Run:  python3 -I paper3/scripts/lean_rediff.py           (from the repository root)
      python3 -I paper3/scripts/lean_rediff.py --check   (verify only, write nothing)
Exit status is non-zero if any check fails.
"""
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CLONE = os.path.expanduser("~/dev/untrusted/openai-math")
CLONE_COMMIT = "4eaee87548250b2682affda7d05d947c05554bae"
COMPARATOR = os.path.join(CLONE, "lean", "ComparatorChallenges", "SubexponentialSAT.lean")
COMPARATOR_SHA256 = "4183b2057cff350d66848215ff7167196dfc20e1891b598fdddea59077a76685"
OURS_DIR = os.path.join(ROOT, "lean", "MOSPFormalization", "SubexpPathwidth")
MACHINE = os.path.join(OURS_DIR, "PrimitiveMachine.lean")
FRAME = os.path.join(OURS_DIR, "Frame.lean")
LOG = os.path.join(ROOT, "paper3", "lean", "rediff.log")

COPIED_RANGE = (1, 190)   # clone lines copied in full
COPIED_LAST = 220         # the closing `end` of the last namespace
SORRY_LINE = 218          # the comparator's one `sorry`, not copied


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def clone_commit():
    try:
        out = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=True).stdout.strip()
    except Exception as e:  # pragma: no cover
        return f"(git rev-parse failed: {e})"
    return out


def check_copy(lines_ours, lines_clone, log):
    """Check 1: byte-level diff of the copy against clone lines 1-190 + 220."""
    try:
        start = lines_ours.index(b"import Mathlib\n")
    except ValueError:
        log.append("CHECK 1 FAIL: `import Mathlib` not found in PrimitiveMachine.lean")
        return False
    ours = lines_ours[start:]
    a, b = COPIED_RANGE
    expected = lines_clone[a - 1:b] + [lines_clone[COPIED_LAST - 1]]
    log.append(f"check 1: our copy starts at PrimitiveMachine.lean line {start + 1} "
               f"({len(ours)} lines); expected = clone lines {a}-{b} + {COPIED_LAST} "
               f"({len(expected)} lines)")
    if ours == expected:
        log.append("check 1: byte-identical (diff empty)")
        return True
    log.append("CHECK 1 FAIL: the copy differs from the clone")
    n = max(len(ours), len(expected))
    shown = 0
    for i in range(n):
        o = ours[i] if i < len(ours) else None
        e = expected[i] if i < len(expected) else None
        if o != e:
            log.append(f"  ours line {start + 1 + i}: {o!r}")
            log.append(f"  clone     : {e!r}")
            shown += 1
            if shown >= 10:
                log.append("  ...")
                break
    return False


def body_of_def(lines, header_prefix):
    """Lines after the header line that starts with `header_prefix`, to the first blank line."""
    for i, line in enumerate(lines):
        if line.startswith(header_prefix):
            body = []
            for l in lines[i + 1:]:
                if l.strip() == "":
                    break
                body.append(l)
            return i + 1, body
    return None, None


def body_of_theorem(lines, header_prefix):
    """Lines after the theorem header to the line that ends in `:= by`, inclusive, with
    the `:= by` removed."""
    for i, line in enumerate(lines):
        if line.startswith(header_prefix):
            body = []
            for l in lines[i + 1:]:
                if l.rstrip().endswith(":= by"):
                    body.append(l.rstrip()[: -len(":= by")].rstrip() + "\n")
                    break
                body.append(l)
            return i + 1, body
    return None, None


def normalise(lines):
    return re.sub(r"\s+", " ", "".join(lines)).strip()


def check_statement(lines_frame, lines_clone, log):
    """Check 2: SubexpCount's body against the comparator theorem's body."""
    i_ours, ours = body_of_def(lines_frame, "def SubexpCount (k : ℕ) : Prop :=")
    i_clone, clone = body_of_theorem(lines_clone, "theorem exact_count_and_sat (k : ℕ) (hk : 2 ≤ k) :")
    if ours is None or clone is None:
        log.append("CHECK 2 FAIL: a header line was not found")
        return False
    log.append(f"check 2: SubexpCount body = Frame.lean lines {i_ours + 1}-{i_ours + len(ours)} "
               f"({len(ours)} lines); exact_count_and_sat body = clone lines "
               f"{i_clone + 1}-{i_clone + len(clone)} ({len(clone)} lines, `:= by` removed)")
    ok = True
    if normalise(ours) == normalise(clone):
        log.append(f"check 2: identical after whitespace normalisation "
                   f"({len(normalise(ours))} characters)")
    else:
        log.append("CHECK 2 FAIL: the bodies differ after whitespace normalisation")
        ok = False
    stripped_ours = [l.strip() for l in ours]
    stripped_clone = [l.strip() for l in clone]
    if stripped_ours == stripped_clone:
        log.append(f"check 2: identical line by line after stripping indentation "
                   f"({len(ours)} lines); the indentation differs by two spaces "
                   f"(a `def` body against a `theorem` type)")
    else:
        log.append("CHECK 2 FAIL: the bodies differ line by line")
        for a, b in zip(stripped_ours, stripped_clone):
            if a != b:
                log.append(f"  ours : {a}")
                log.append(f"  clone: {b}")
        ok = False
    # The indentation: every body line of ours is the clone's with two fewer leading spaces.
    indent = [len(o) - len(o.lstrip(" ")) - (len(c) - len(c.lstrip(" "))) for o, c in zip(ours, clone)]
    log.append(f"check 2: indentation offset (ours minus clone) per line: {sorted(set(indent))}")
    return ok


def check_no_sorry(lines_machine, lines_frame, lines_clone, log):
    """Check 3: no `sorry`, no `axiom` declaration in our two files outside their header
    comments; exactly one `sorry` in the clone, at line 218."""
    ok = True
    for name, lines in (("PrimitiveMachine.lean", lines_machine), ("Frame.lean", lines_frame)):
        # The header comment is the first `/- ... -/` block.
        text = b"".join(lines).decode("utf-8")
        end = text.find("-/")
        body = text[end + 2:] if text.startswith("/-") and end >= 0 else text
        sorries = [m.start() for m in re.finditer(r"\bsorry\b", body)]
        axioms = [m.start() for m in re.finditer(r"^\s*(private\s+)?axiom\b", body, re.M)]
        log.append(f"check 3: {name}: {len(sorries)} `sorry`, {len(axioms)} `axiom` declaration(s) "
                   f"outside the header comment")
        if sorries or axioms:
            ok = False
    clone_sorries = [i + 1 for i, l in enumerate(lines_clone) if re.search(rb"\bsorry\b", l)]
    log.append(f"check 3: the clone's comparator file has `sorry` at line(s) {clone_sorries}")
    if clone_sorries != [SORRY_LINE]:
        log.append(f"CHECK 3 FAIL: expected exactly one `sorry` at line {SORRY_LINE}")
        ok = False
    copied_has_sorry = any(SORRY_LINE in range(a, b + 1) for a, b in [COPIED_RANGE]) or SORRY_LINE == COPIED_LAST
    log.append(f"check 3: the `sorry` line is inside the copied range: {copied_has_sorry}")
    if copied_has_sorry:
        ok = False
    if not ok:
        log.append("CHECK 3 FAIL")
    return ok


def main(argv):
    check_only = "--check" in argv
    log = []
    log.append(f"paper3/scripts/lean_rediff.py -- {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    log.append(f"clone: {CLONE} at commit {clone_commit()} (expected {CLONE_COMMIT})")
    data_clone = read_bytes(COMPARATOR)
    data_machine = read_bytes(MACHINE)
    data_frame = read_bytes(FRAME)
    log.append(f"sha256 comparator (clone) : {sha256(data_clone)} (expected {COMPARATOR_SHA256})")
    log.append(f"sha256 PrimitiveMachine.lean: {sha256(data_machine)}")
    log.append(f"sha256 Frame.lean           : {sha256(data_frame)}")
    ok = True
    if clone_commit() != CLONE_COMMIT:
        log.append("FAIL: the clone is not at the expected commit")
        ok = False
    if sha256(data_clone) != COMPARATOR_SHA256:
        log.append("FAIL: the comparator file's hash is not the one the header records")
        ok = False
    lines_clone = data_clone.splitlines(keepends=True)
    lines_machine = data_machine.splitlines(keepends=True)
    lines_frame = data_frame.splitlines(keepends=True)
    log.append(f"comparator file: {len(lines_clone)} lines; PrimitiveMachine.lean: "
               f"{len(lines_machine)} lines; Frame.lean: {len(lines_frame)} lines")
    ok &= check_copy(lines_machine, lines_clone, log)
    ok &= check_statement([l.decode("utf-8") for l in lines_frame],
                          [l.decode("utf-8") for l in lines_clone], log)
    ok &= check_no_sorry(lines_machine, lines_frame, lines_clone, log)
    log.append("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED")
    text = "\n".join(log) + "\n"
    print(text, end="")
    if not check_only:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "w") as f:
            f.write(text)
        print(f"wrote {os.path.relpath(LOG, ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
