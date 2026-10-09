"""Relevance filter for the Table 1 name searches (added 2026-09-29).

OpenAlex's `title_and_abstract.search` stems words and ignores punctuation,
so a quoted phrase is looser than it looks: "narrowness" matches "narrowing"
in term rewriting, "node searching" matches peer-to-peer networks, and "split
bandwidth" matches radar interferometry and photonic beam splitters. This
module fetches every candidate work with its abstract.

What decides relevance, and so the published counts, is `kept_works`: for the
eleven smaller names, a per-work label in `data/relevance_labels.json`; for
pathwidth, the rule `keep_pathwidth`. The phrase rule `relevant` (the
*literal* phrase, case-insensitive with hyphen and space interchangeable,
**and** a context term, and no exclusion term) is a mechanical first pass and
the sensitivity check, not the count; `python -m paper1.relevance` prints its
kept and dropped samples so they can be checked by eye.
(Docstring corrected 2026-10-03: it used to say the phrase rule was the whole
of the method. The two disagree on 157 of the 700 labelled works; see
`popularity.md`, "For the paper".)

Cache: `paper1/data/openalex_candidates.json` (every candidate, with text).
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "data" / "openalex_candidates.json"
MAILTO = "a@linhares.ltd"

GRAPH = ["graph", "pathwidth", "path-width", "treewidth", "vertex separation", "interval graph",
         "search number", "searcher", "fugitive", "pebbl", "layout", "cutwidth", "bandwidth of"]
# name -> (literal phrases, context terms: one must appear, exclusion terms: none may appear)
RULES = {
    "MOSP": (["minimization of open stacks", "open stacks problem", "number of open stacks",
              "minimization of the open stacks", "maximum number of open stacks"], [], []),
    "gate matrix layout": (["gate matrix layout"], [], []),
    "one-dimensional logic": (["one-dimensional logic array", "one-dimensional logic gate",
                               "logic gate assignment", "one-dimensional logic arrays"], [], []),
    "PLA folding": (["pla folding", "programmable logic array folding", "folding of programmable logic",
                     "folding of pla"], [], []),
    "interval thickness": (["interval thickness"], GRAPH, []),
    "node search game": (["node search number", "node searching", "node search game", "node-search"],
                         ["graph searching", "searcher", "fugitive", "search number", "pathwidth",
                          "vertex separation", "interval graph", "treewidth", "cops", "graph search"],
                         ["peer-to-peer", "p2p", "xml", "dht"]),
    "edge search game": (["edge search number", "edge searching", "edge search game", "edge-search"],
                         ["graph searching", "searcher", "fugitive", "search number", "pathwidth",
                          "vertex separation", "treewidth", "cops", "graph search", "contaminat"],
                         ["image", "segmentation", "robot", "music"]),
    "narrowness": (["narrowness"], ["pathwidth", "path-width", "interval", "graph parameter",
                                    "kornai", "linear layout", "vertex separation"], []),
    "split bandwidth": (["split bandwidth", "split-bandwidth"], ["graph", "pathwidth", "helicopter",
                                                                  "search"], ["radar", "interferometr",
                                                                              "photonic", "fiber", "sar "]),
    "graph path-width": (["pathwidth", "path-width", "path width of"], [], []),
    "edge separation": (["edge separation"], ["pebbl", "separation game", "vertex separation",
                                              "linear layout", "cutwidth", "pathwidth", "search number"], []),
    "vertex separation": (["vertex separation"], GRAPH, []),
}


def _norm(t: str) -> str:
    return re.sub(r"[\s\-‐‑–]+", " ", (t or "").lower())


def _text(w: dict) -> str:
    inv = w.get("abstract_inverted_index") or {}
    words = sorted(((p, k) for k, ps in inv.items() for p in ps))
    return (w.get("display_name") or "") + " . " + " ".join(k for _, k in words)


def relevant(name: str, text: str) -> bool:
    phrases, context, exclude = RULES[name]
    t = _norm(text)
    if not any(_norm(p) in t for p in phrases):
        return False
    if exclude and any(_norm(e) in t for e in exclude):
        return False
    return not context or any(_norm(c) in t for c in context)


def fetch(queries, fields: str) -> dict:
    out = {"fetched": time.strftime("%Y-%m-%d"), "names": {}}
    for name, q, *_ in queries:
        flt = f"title_and_abstract.search:{q},primary_topic.field.id:{fields}"
        cursor, works = "*", []
        while cursor:
            url = ("https://api.openalex.org/works?filter=" + urllib.parse.quote(flt, safe=':|,')
                   + f"&per-page=200&cursor={cursor}&select=id,display_name,publication_year,"
                   f"abstract_inverted_index&mailto={MAILTO}")
            for attempt in range(5):
                try:
                    d = json.load(urllib.request.urlopen(url, timeout=60)); break
                except Exception:
                    time.sleep(3 * (attempt + 1))
            for w in d["results"]:
                works.append({"id": w["id"].rsplit("/", 1)[1], "year": w.get("publication_year"),
                              "title": w.get("display_name"), "text": _text(w)})
            cursor = d["meta"].get("next_cursor")
        out["names"][name] = works
        print(f"{name:24} {len(works):>5} candidates", file=sys.stderr)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out))
    return out


PW_THEORY = {"Computational Theory and Mathematics", "Discrete Mathematics and Combinatorics",
             "Geometry and Topology", "Algebra and Number Theory", "Logic", "Theoretical Computer Science"}
PW_BAD = ["path planning", "datapath", "data path", "data-path", "trajectory", "steering", "vehicle",
          "road", "pedestrian"]
LABELS = HERE / "data" / "relevance_labels.json"


def keep_pathwidth(w: dict) -> bool:
    """Rule for "pathwidth" OR "path-width", whose search also matches physical path widths
    (roads, tool paths, vehicles) and datapath widths: keep the one-word spelling, anything
    in a theory subfield, or a work that talks about graphs or tree-width and not about paths
    in space. Checked by sampling both sides; errs by a few percent each way."""
    t = w["text"].lower()
    if "pathwidth" in t or w.get("subfield") in PW_THEORY:
        return True
    if any(b in t for b in PW_BAD):
        return False
    if any(k in t for k in ["graph", "treewidth", "tree-width", "minor"]):
        return True
    topic = (w.get("topic") or "").lower()
    return "path-width" in t and any(k in topic for k in ["graph", "complexity", "algorithm"])


def kept_works(name: str, data: dict | None = None) -> list[dict]:
    """The candidates for `name` judged relevant: by rule for pathwidth, and by the
    per-work labels in `relevance_labels.json` (judged from title, topic, venue and
    abstract) for the other eleven names."""
    data = data or json.loads(CACHE.read_text())
    works = data["names"][name]
    if name == "graph path-width":
        return [w for w in works if keep_pathwidth(w)]
    labels = json.loads(LABELS.read_text())[name]
    return [w for w in works if labels.get(w["id"])]


def relevant_counts() -> dict[str, int]:
    """Relevant works per name over all years: the corrected popularity counts."""
    data = json.loads(CACHE.read_text())
    return {name: len(kept_works(name, data)) for name in data["names"]}


if __name__ == "__main__":
    import random
    from paper1.trends import QUERIES, FIELDS
    data = json.loads(CACHE.read_text()) if CACHE.exists() and "--refresh" not in sys.argv else fetch(QUERIES, FIELDS)
    random.seed(2)
    for name, *_ in QUERIES:
        ws = data["names"][name]
        keep = [w for w in ws if relevant(name, w["text"])]
        drop = [w for w in ws if not relevant(name, w["text"])]
        print(f"\n== {name}: kept {len(keep)} of {len(ws)}")
        for tag, grp in (("KEEP", keep), ("DROP", drop)):
            for w in random.sample(grp, min(6, len(grp))):
                print(f"   {tag} {w['year']} {(w['title'] or '')[:92]}")
