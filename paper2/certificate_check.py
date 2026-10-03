"""Independent checker for customer-search certificates under the repaired rules.

A certificate (`learning/search_certificate.py`, format
`mosp-search-certificate-1`) is the tree a refutation of "MOSP(M) <= k?" leaves
behind, with every pruning step named by its rule and its witness. This file
checks one against the 0/1 matrix `M` and **imports nothing from this
repository** -- not the search, not the emitter, not `learning`'s own checker.
Everything below is recomputed from the matrix with the standard library.

The premises checked are the ones proved sound in
`lean/MOSPFormalization/Search/` (`paper2/revised_algorithm.md` §4.6.1):

- **free moves** -- the listed set equals the remaining customers `c` with
  `N[c] ⊆ O(S)`;
- **cost cut** -- recomputed: a candidate is playable iff
  `|O(S ∪ {c}) ∖ S| <= k`;
- **subset rule** `["subset", r, d]` -- `o(d,S) ⊆ o(r,S)`, `d != r`, with the
  index tie-break `d < r` on equality
  (`searchSol_cl_insert_of_newlyOpened_subset`);
- **repaired definite move** `["definite", q, M]` -- `q` playable and `M` a
  matching witnessing `HasDefiniteMatching G S q`: pairs `[d, s]` with the `d`
  distinct, the `s` distinct, each `d != q` a remaining customer that `q`
  frees (`o(d,S) ⊆ o(q,S)`), each `s ∈ o(d,S)`, and `|M| >= open(q,S) − 1`.
  By `isHereditarilyDefinite_iff_hasDefiniteMatching` this is
  `IsHereditarilyDefinite`, and `solvable_cl_insert_of_hereditarilyDefinite`
  makes `q` the only child needed;
- **repaired better move** `["better", r, q, M]` -- `r` and `q` playable,
  premise 3 `|(O(S ∪ {r}) ∪ N[q]) ∖ (S ∪ {r})| <= k`, and `M` a matching of
  the same kind at the child `T = cl(S ∪ {r})`: each `d ∉ T ∪ {q}` with
  `o(d,T) ⊆ o(q,T)`, `s ∈ o(d,T)`, `|M| >= open(q,T) − 1`. That is
  `IsRepairedBetter`, and `solvable_cl_insert_of_repairedBetter` moves any
  solution through `r` to one through `q`;
- **old move** (Theorem 3) -- nothing recorded; `Q(S)` is rebuilt from the
  path with the reinsertion test, as the search does it;
- **memo** -- a reference to an earlier completed refutation of the same
  closed set, accepted only with old move off.

and at every node: not a solution; every playable candidate is a child or is
covered, every chain of coverings ends at a child or (under old move) in
`Q(S)`, with no cycle; every child a playable candidate; every node reachable.

A published-rule step -- `["definite", q]` or `["better", r, q]` with no
matching -- is **rejected**: its premise is not sound (`DEFINITE_CEX`,
`paper2/certificates.md` §4).

What it trusts: the Lean theorems named above, and that the matrix given is the
instance meant (the certificate's SHA-256 of it is checked). Root `start`, when
present, makes the claim "no closing order extending `start` has cost <= k";
the claim `MOSP(M) > k` needs `start` empty, and `check` reports which.

    python paper2/certificate_check.py BUNDLE.json[.gz]

where a bundle is `{"matrix": [[0/1, ...], ...], "certificate": {...}}`.
Exit status 0 if the certificate verifies, 1 otherwise.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
import time


class Rejected(Exception):
    pass


def matrix_sha256(matrix: list[list[int]]) -> str:
    """SHA-256 of the int8 row-major bytes followed by the two dimensions as bytes."""
    n, m = len(matrix), len(matrix[0]) if matrix else 0
    raw = bytes(int(v) for row in matrix for v in row) + bytes([n, m])
    return hashlib.sha256(raw).hexdigest()


def closed_neighbourhoods(matrix: list[list[int]]) -> list[int]:
    """N[c] as bitmasks: c and every customer sharing a product with c."""
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    masks = [0] * n
    for p in range(m):
        holders = 0
        for c in range(n):
            if matrix[c][p]:
                holders |= 1 << c
        for c in range(n):
            if matrix[c][p]:
                masks[c] |= holders
    return masks


def members(mask: int) -> list[int]:
    out = []
    while mask:
        low = mask & -mask
        out.append(low.bit_length() - 1)
        mask ^= low
    return out


def popcount(mask: int) -> int:
    return bin(mask).count("1")


def verify_matching(pairs, freed: dict[int, int], need: int, where: str) -> None:
    """`pairs` matches distinct members of `freed` to distinct stacks in their sets."""
    if not isinstance(pairs, list):
        raise Rejected(f"{where}: matching is not a list")
    used_d, used_s = set(), set()
    for pair in pairs:
        if not (isinstance(pair, list) and len(pair) == 2):
            raise Rejected(f"{where}: malformed matching edge {pair!r}")
        d, s = int(pair[0]), int(pair[1])
        if d not in freed:
            raise Rejected(f"{where}: matched customer {d} is not one the move frees")
        if not (freed[d] >> s) & 1:
            raise Rejected(f"{where}: edge ({d}, {s}): stack {s} is not newly opened by {d}")
        if d in used_d:
            raise Rejected(f"{where}: customer {d} matched twice")
        if s in used_s:
            raise Rejected(f"{where}: stack {s} matched twice")
        used_d.add(d)
        used_s.add(s)
    if len(used_d) < need:
        raise Rejected(f"{where}: matching has {len(used_d)} edges, open - 1 = {need}")


def check(matrix: list[list[int]], cert: dict) -> dict:
    """Verify `cert` against `matrix`. Returns ok, reason, claim, nodes, steps, edges, seconds."""
    started = time.monotonic()
    counted = {"nodes": 0, "steps": 0, "edges": 0}
    claim = ""
    try:
        claim = _check(matrix, cert, counted)
        ok, reason = True, "refutation verified"
    except Rejected as why:
        ok, reason = False, str(why)
    except (KeyError, TypeError, ValueError, IndexError) as why:
        ok, reason = False, f"malformed certificate: {why!r}"
    return {"ok": ok, "reason": reason, "claim": claim if ok else "",
            "seconds": time.monotonic() - started, **counted}


def _check(matrix, cert: dict, counted: dict) -> str:
    if cert.get("format") != "mosp-search-certificate-1":
        raise Rejected("not a search certificate")
    if cert.get("status") != "unsat":
        raise Rejected(f"certificate status is {cert.get('status')!r}, not a refutation")
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    if (int(cert["n_customers"]), int(cert["n_patterns"])) != (n, m):
        raise Rejected("instance dimensions do not match")
    if cert["matrix_sha256"] != matrix_sha256(matrix):
        raise Rejected("matrix digest does not match the instance")
    config = cert.get("config", {})
    old_move = bool(config.get("old_move", False))
    memo = bool(config.get("memo", False))
    if memo and old_move:
        raise Rejected("memo references are not checkable under old move")
    k = int(cert["k"])
    N = closed_neighbourhoods(matrix)
    full = 0
    for c in range(n):
        if N[c]:
            full |= 1 << c
    records = cert["nodes"]
    nodes = {}
    for rec in records:
        nid = int(rec["id"])
        if nid in nodes:
            raise Rejected("duplicate node ids")
        nodes[nid] = rec
    if not records or records[0].get("parent") is not None:
        raise Rejected("no root")
    refuted_states: dict[int, int] = {}
    completed: set[int] = set()
    start = 0
    for c in cert.get("start", []):
        c = int(c)
        if not 0 <= c < n:
            raise Rejected(f"start customer {c} out of range")
        start |= 1 << c
    start &= full
    start_opened = 0
    for c in members(start):
        start_opened |= N[c]

    # an explicit stack instead of recursion: trees at 75 customers are deep enough
    # for Python's default limit to matter
    stack = [("enter", records[0], start, start_opened, 0)]
    while stack:
        item = stack.pop()
        if item[0] == "done":
            _, rec, closed = item
            completed.add(int(rec["id"]))
            if memo:
                refuted_states[closed] = int(rec["id"])
            continue
        if item[0] == "child":
            _, parent_frame, idx = item
            _descend(parent_frame, idx, stack, nodes, N, k, old_move)
            continue
        _, rec, closed, opened, seen = item
        frame = _visit(rec, closed, opened, seen, nodes, N, full, k, old_move, memo,
                       refuted_states, completed, counted)
        if frame is None:
            continue
        stack.append(("done", rec, frame["closed"]))
        for idx in range(len(frame["children"]) - 1, -1, -1):
            stack.append(("child", frame, idx))
    if counted["nodes"] != len(records):
        raise Rejected(f"{len(records) - counted['nodes']} nodes are not reachable from the root")
    if start:
        return f"no closing order extending {members(start)} has cost <= {k}"
    return f"MOSP > {k}"


def _descend(frame, idx, stack, nodes, N, k, old_move):
    """Push child `idx` of `frame`, with Q(S ++ [c]) by the reinsertion test; then
    mark it searched, so later siblings inherit it."""
    child_rec, c = frame["children"][idx]
    closed, opened, seen = frame["closed"], frame["opened"], frame["seen"]
    inherited = 0
    if old_move and seen:
        for q in members(seen):
            if popcount((opened | N[q] | N[c]) & ~(closed | (1 << q))) <= k:
                inherited |= 1 << q
    frame["seen"] = seen | (1 << c)
    stack.append(("enter", child_rec, closed | (1 << c), opened | N[c], inherited))


def _visit(rec, closed, opened, seen, nodes, N, full, k, old_move, memo,
           refuted_states, completed, counted):
    nid = int(rec["id"])
    counted["nodes"] += 1
    free = 0
    for c in members(full & ~closed):
        if N[c] & ~opened == 0:
            free |= 1 << c
    listed = 0
    for c in rec.get("free", []):
        listed |= 1 << int(c)
    if listed != free:
        raise Rejected(f"node {nid}: free moves {rec.get('free', [])} are not the customers "
                       f"whose neighbourhood is opened")
    closed |= free
    if closed == full:
        raise Rejected(f"node {nid}: every customer is closed -- the tree holds a solution")
    kind = rec.get("kind", "refuted")
    if kind == "memo":
        if not memo:
            raise Rejected(f"node {nid}: memo reference without memo enabled")
        cited = rec.get("memo_of")
        if cited is None or int(cited) not in completed:
            raise Rejected(f"node {nid}: memo cites {cited}, not a completed refutation")
        if refuted_states.get(closed) != int(cited):
            raise Rejected(f"node {nid}: memo cites {cited}, whose closed set differs")
        if rec.get("children") or rec.get("steps"):
            raise Rejected(f"node {nid}: a memo node carries children or steps")
        return None
    if kind != "refuted":
        raise Rejected(f"node {nid}: kind {kind!r} inside a refutation")

    remaining = full & ~closed
    seen &= remaining
    candidates = remaining & ~seen if old_move else remaining
    o = {c: N[c] & ~opened for c in members(remaining)}
    cost = {c: popcount((opened | N[c]) & ~closed) for c in members(candidates)}
    playable = {c for c, v in cost.items() if v <= k}

    children = []
    for cid in rec.get("children", []):
        child = nodes.get(int(cid))
        if child is None or child.get("parent") != nid or child.get("move") is None:
            raise Rejected(f"node {nid}: child id {cid} missing or mis-parented")
        c = int(child["move"])
        if c not in playable:
            raise Rejected(f"node {nid}: child {c} is not a playable candidate")
        children.append((child, c))
    child_set = {c for _, c in children}
    if len(child_set) != len(children):
        raise Rejected(f"node {nid}: repeated child")

    cover: dict[int, int] = {}
    definite = None
    for step in rec.get("steps", []):
        counted["steps"] += 1
        rule = step[0]
        if rule == "definite":
            q = int(step[1])
            where = f"node {nid}: definite move on {q}"
            if len(step) < 3:
                raise Rejected(f"{where}: no matching witness (a published-rule step)")
            if q not in playable:
                raise Rejected(f"{where}: {q} is not a playable candidate")
            own = o[q]
            freed = {d: o[d] for d in o if d != q and o[d] & ~own == 0}
            verify_matching(step[2], freed, popcount(own) - 1, where)
            counted["edges"] += len(step[2])
            if definite is not None:
                raise Rejected(f"node {nid}: two definite moves")
            definite = q
            for r in playable:
                if r != q:
                    cover.setdefault(r, q)
        elif rule == "subset":
            r, d = int(step[1]), int(step[2])
            if r not in playable or d not in o or d == r:
                raise Rejected(f"node {nid}: subset step ({r}, {d}) names a non-candidate")
            if not (o[d] & ~o[r] == 0 and (o[d] != o[r] or d < r)):
                raise Rejected(f"node {nid}: subset step ({r}, {d}): o({d}) is not a "
                               f"(tie-broken) subset of o({r})")
            if r in cover:
                raise Rejected(f"node {nid}: {r} discarded twice")
            cover[r] = d
        elif rule == "better":
            r, q = int(step[1]), int(step[2])
            where = f"node {nid}: better step ({r}, {q})"
            if len(step) < 4:
                raise Rejected(f"{where}: no matching witness (a published-rule step)")
            if r not in playable or q not in playable or q == r:
                raise Rejected(f"{where}: names a non-candidate")
            closed_r = closed | (1 << r)
            opened_r = opened | N[r]
            if popcount((opened_r | N[q]) & ~closed_r) > k:
                raise Rejected(f"{where}: S ++ [r, q] is not playable (premise 3)")
            own = N[q] & ~opened_r
            freed = {}
            for d in members(full & ~closed_r):
                left = N[d] & ~opened_r
                if d != q and left and left & ~own == 0:
                    freed[d] = left
            verify_matching(step[3], freed, popcount(own) - 1, where)
            counted["edges"] += len(step[3])
            if r in cover:
                raise Rejected(f"node {nid}: {r} discarded twice")
            cover[r] = q
        else:
            raise Rejected(f"node {nid}: unknown rule {rule!r}")

    for c in sorted(playable):
        here, trail = c, set()
        while here not in child_set:
            if old_move and (seen >> here) & 1:
                break
            if here in trail:
                raise Rejected(f"node {nid}: covering cycle through {sorted(trail)}")
            trail.add(here)
            if here not in cover:
                raise Rejected(f"node {nid}: candidate {here} (cost {cost.get(here)}) is "
                               f"neither explored nor covered")
            here = cover[here]
    return {"closed": closed, "opened": opened, "seen": seen, "children": children}


def load(path: str) -> dict:
    raw = open(path, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.split("\n\n")[0])
        print("usage: python paper2/certificate_check.py BUNDLE.json[.gz]")
        return 2
    bundle = load(argv[1])
    result = check(bundle["matrix"], bundle["certificate"])
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in result.items()}))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
