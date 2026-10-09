#!/usr/bin/env python3
"""Check the 34-customer false-refutation instance with nothing but the standard library.

Reads instance34.mosp (the standard MOSP file: a name line, "rows columns", then
the 0/1 rows) and solutions34.json, and recomputes, for each pattern order, the
peak number of open stacks: a customer's stack is open from the first to the last
pattern it needs. Prints both peaks; exits non-zero if either disagrees with the
recorded value, or if the optimal order does not beat the published answer.

    python3 check.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_mosp(path):
    lines = [l.split() for l in path.read_text().splitlines() if l.strip()]
    rows, cols = int(lines[1][0]), int(lines[1][1])
    matrix = [[int(x) for x in line] for line in lines[2:2 + rows]]
    assert len(matrix) == rows and all(len(r) == cols for r in matrix)
    return matrix


def peak(matrix, order):
    assert sorted(order) == list(range(len(matrix[0]))), "not a permutation of the patterns"
    pos = {p: t for t, p in enumerate(order)}
    spans = []
    for row in matrix:
        ts = [pos[p] for p, x in enumerate(row) if x]
        if ts:
            spans.append((min(ts), max(ts)))
    return max(sum(1 for a, b in spans if a <= t <= b) for t in range(len(order)))


def main():
    m = read_mosp(HERE / "instance34.mosp")
    s = json.loads((HERE / "solutions34.json").read_text())
    ok = True
    for key in ("published_rules", "repaired_rules"):
        got = peak(m, s[key]["pattern_order"])
        rec = s[key]["peak_open_stacks"]
        print(f"{key:16s} reported optimum {s[key]['value']}, its order's peak {got} (recorded {rec})")
        ok &= got == rec
    better = peak(m, s["repaired_rules"]["pattern_order"]) < s["published_rules"]["value"]
    print("an order beats the published 'optimum':", better)
    sys.exit(0 if ok and better else 1)


if __name__ == "__main__":
    main()
