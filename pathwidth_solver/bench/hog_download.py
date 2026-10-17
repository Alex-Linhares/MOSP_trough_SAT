"""Download every House of Graphs graph, with their invariant values.

House of Graphs (houseofgraphs.org; Coolsaet, D'hondt & Goedgebeur 2022) serves
at most 2,000 graphs per logged-in download, so this queries by number of
vertices (invariant 15) and splits any range that comes back full. Each range is
saved twice, as graph6 and as "Invariant values" (treewidth is invariant 39),
under bench/instances/hog/raw/. Resumable: ranges already saved are skipped.
Polite: one request at a time, a pause between them.

Credentials: ~/.config/houseofgraphs/credentials, two lines, email then
password, chmod 600. They are read here and sent only to houseofgraphs.org.

    python bench/hog_download.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

API = "https://houseofgraphs.org/api/"
OUT = Path(__file__).resolve().parent / "instances" / "hog" / "raw"
CRED = Path.home() / ".config" / "houseofgraphs" / "credentials"
CAP = 2000
PAUSE = 2.0
N_VERTICES = 15


N_EDGES = 14


def conds(lo, hi, elo=None, ehi=None):
    rng = [{"invariantId": N_VERTICES, "from": lo, "to": hi}]
    if elo is not None:
        rng.append({"invariantId": N_EDGES, "from": elo, "to": ehi})
    return {"invariantEnquiries": [], "interestingInvariantEnquiries": [],
            "invariantRangeEnquiries": rng,
            "graphClassEnquiries": [], "invariantParityEnquiries": [], "textEnquiries": [],
            "formulaEnquiries": [], "graphIdEnquiry": None, "canonicalFormEnquiry": None, "mostRecent": -1, "mostPopular": -1, "subgraphEnquiries": []}


def login(s):
    email, password = CRED.read_text().splitlines()[:2]
    r = s.post(API + "auth/login", json={"email": email.strip(), "password": password.strip()}, timeout=60)
    if r.status_code != 200 or not r.json().get("success"):
        sys.exit(f"login failed: {r.status_code} {r.text[:200]}")


def fetch(s, lo, hi, fmt, elo=None, ehi=None):
    body = {"graphId": -1, "format": fmt, "searchConditions": conds(lo, hi, elo, ehi)}
    for attempt in range(3):
        r = s.post(API + "download_graph", json=body, params={"timeout": 120}, timeout=300)
        if r.status_code == 401 and attempt == 0:
            login(s); continue
        r.raise_for_status()
        time.sleep(PAUSE)
        return r.content
    raise RuntimeError(f"download {lo}-{hi} {fmt} failed")


def count_g6(data: bytes) -> int:
    return sum(1 for l in data.splitlines() if l.strip() and not l.startswith(b">>"))


def ranges(lo, hi):
    """Yield saved (lo, hi) ranges, each under the cap, splitting full ones."""
    stack = [(lo, hi)]
    while stack:
        a, b = stack.pop()
        g6 = OUT / f"n{a:05d}-{b:05d}.g6"
        if g6.exists():
            continue
        data = fetch(S, a, b, "Graph6")
        k = count_g6(data)
        if k >= CAP and a < b:
            mid = (a + b) // 2
            stack += [(mid + 1, b), (a, mid)]
            print(f"n {a}-{b}: full ({k}), splitting", flush=True)
            continue
        if k >= CAP:
            print(f"n={a}: full ({k}), splitting by edges", flush=True)
            by_edges(a)
            continue
        (OUT / f"n{a:05d}-{b:05d}.inv.txt").write_bytes(fetch(S, a, b, "Invariant values"))
        g6.write_bytes(data)
        print(f"n {a}-{b}: {k} graphs", flush=True)


def by_edges(n):
    """One vertex count over the cap: split on the number of edges instead."""
    stack = [(0, n * (n - 1) // 2)]
    while stack:
        a, b = stack.pop()
        g6 = OUT / f"n{n:05d}-{n:05d}_e{a:06d}-{b:06d}.g6"
        if g6.exists():
            continue
        data = fetch(S, n, n, "Graph6", a, b)
        k = count_g6(data)
        if k >= CAP:
            if a == b:
                sys.exit(f"n={n} m={a}: {k} graphs, cannot split further")
            mid = (a + b) // 2
            stack += [(mid + 1, b), (a, mid)]
            continue
        (OUT / f"n{n:05d}-{n:05d}_e{a:06d}-{b:06d}.inv.txt").write_bytes(fetch(S, n, n, "Invariant values", a, b))
        g6.write_bytes(data)
        print(f"n {n} m {a}-{b}: {k} graphs", flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    S = requests.Session()
    login(S)
    print("total in database:", S.get(API + "graphs/total", timeout=60).json()["message"], flush=True)
    ranges(1, 100_000)
    got = sum(count_g6(p.read_bytes()) for p in OUT.glob("*.g6"))
    print(f"saved {got} graphs; a shortfall against the total means a range hit the server's timeout", flush=True)
