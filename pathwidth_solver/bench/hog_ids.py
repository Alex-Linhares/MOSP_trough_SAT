"""House of Graphs ids, names and invariant values, by search.

For each vertex range hog_download.py saved, page through the logged-in search
(`enquiry`) and write one JSON line per graph to instances/hog/graphs.jsonl:
graphId, graphName, canonicalForm (graph6, their canonical labelling), n, and
invariants {invariantId: [status, value]} (treewidth is 39; status 2 is
computed). Each range is checked complete: no search timeout, every candidate
handled, and as many results as graphs in the range's graph6 file. Resumable by
range; one request at a time, with a pause.

    python bench/hog_ids.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hog_download as hd  # noqa: E402

HOG = hd.OUT.parent
JSONL = HOG / "graphs.jsonl"
DONE = HOG / "graphs.ranges_done"
SIZE = 500


def page(s, lo, hi, p, elo=None, ehi=None):
    params = {"page": p, "size": SIZE, "sort": "graph_id", "sortDir": "asc", "offset": 0,
              "lastPageOffset": 0, "fullSearch": True, "timeout": 120}
    for attempt in range(3):
        r = s.post(hd.API + "enquiry", json=hd.conds(lo, hi, elo, ehi), params=params, timeout=300)
        if r.status_code == 401 and attempt == 0:
            hd.login(s); continue
        r.raise_for_status()
        time.sleep(hd.PAUSE)
        return r.json()
    raise RuntimeError(f"enquiry {lo}-{hi} page {p} failed")


def main():
    s = requests.Session(); hd.login(s)
    done = set(DONE.read_text().split()) if DONE.exists() else set()
    total = 0
    with open(JSONL, "a") as out, open(DONE, "a") as dn:
        for g6 in sorted(hd.OUT.glob("*.g6")):
            key = g6.stem
            want = hd.count_g6(g6.read_bytes())
            if key in done:
                total += want; continue
            nums = list(map(int, re.findall(r"\d+", key)))
            lo, hi = nums[:2]
            elo, ehi = (nums[2:4] if len(nums) == 4 else (None, None))
            rows, p = [], 0
            while True:
                d = page(s, lo, hi, p, elo, ehi)
                if d.get("timeout"):
                    sys.exit(f"{key}: search timed out on page {p}")
                rows += d.get("_embedded", {}).get("graphSearchModelList", [])
                if p + 1 >= d["page"]["totalPages"]:
                    break
                p += 1
            if len(rows) != want or len({r["graphId"] for r in rows}) != want:
                sys.exit(f"{key}: {len(rows)} results against {want} graphs in the download")
            g6set = {l.strip().decode() for l in g6.read_bytes().splitlines() if l.strip()}
            if {r["canonicalForm"] for r in rows} != g6set:
                print(f"WARNING {key}: search graph6 strings differ from the download's", flush=True)
            for r in rows:
                inv = {v["invariantId"]: [v["invariantStatus"], v["invariantValue"]] for v in r["invariantValues"]}
                out.write(json.dumps({"graphId": r["graphId"], "graphName": r["graphName"],
                                      "canonicalForm": r["canonicalForm"], "n": len(r["adjacencyList"]),
                                      "invariants": inv}) + "\n")
            out.flush(); dn.write(key + "\n"); dn.flush()
            total += want
            print(f"{key}: {want} graphs", flush=True)
    print(f"{total} graphs with ids", flush=True)


if __name__ == "__main__":
    main()
