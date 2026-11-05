"""Check every DOI in paper3/latex/refs.bib against Crossref (item 10, 2026-11-05).

    python3 paper3/scripts/check_refs.py            # uses the cache, fetches what is missing
    python3 paper3/scripts/check_refs.py --refresh  # fetches everything again
    python3 paper3/scripts/check_refs.py --lookup   # also searches Crossref for the DOI of
                                                    # every entry that has none, and prints
                                                    # the best match (adds nothing to the file)

Reuses `paper1.latex.check_refs` (entries, norm, fetch): for each entry with a
`doi`, the Crossref (or DataCite) record's title, year and first author's family
name are compared with the entry. Responses are cached in
`paper3/latex/data/doi_check.json` with the date of the fetch; the printed
lines are the log (`paper3/latex/doi_check.log` holds the run of record).
Exits non-zero if a title or first author disagrees. A year that differs is
reported, not failed. `@misc` entries that are repository READMEs or an arXiv
record carry no DOI and are listed as "no DOI".

Run from the repository root (it imports paper1.latex.check_refs).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from paper1.latex.check_refs import entries, fetch, norm  # noqa: E402

BIB = ROOT / "paper3" / "latex" / "refs.bib"
CACHE = ROOT / "paper3" / "latex" / "data" / "doi_check.json"
UA = {"User-Agent": "paper3-refcheck/0.1 (mailto:none@example.org)"}
# Disagreements read by hand and accepted, with the reason.
KNOWN: dict[str, str] = {
    "Mertens2006Threshold": "Crossref's title carries HTML italic tags around K; the words agree (year 2005 is the online-first year, the volume is 2006)",
}


def lookup(e: dict) -> dict | None:
    """Best Crossref match for an entry without a DOI, by bibliographic query."""
    first = e.get("author", "").split(" and ")[0]
    q = f"{e.get('title', '')} {first} {e.get('year', '')}"
    url = "https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers=UA)
    items = json.load(urllib.request.urlopen(req, timeout=30))["message"]["items"]
    for m in items:
        title = (m.get("title") or [""])[0]
        fam = (m.get("author") or [{}])[0].get("family", "")
        year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        t_ok = norm(title).startswith(norm(e["title"])[:40]) or norm(e["title"]).startswith(norm(title)[:40])
        f = first.split(",")[0] if "," in first else first.split()[-1]
        a_ok = norm(fam) == norm(f) or norm(f).endswith(norm(fam))
        if t_ok and a_ok:
            return {"doi": m["DOI"], "title": title, "year": year, "first_author": fam,
                    "container": (m.get("container-title") or [""])[0], "type": m.get("type")}
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--lookup", action="store_true")
    args = ap.parse_args()
    cache = {} if args.refresh or not CACHE.exists() else json.loads(CACHE.read_text())
    bad = 0
    es = entries(BIB.read_text())
    print(f"# {date.today().isoformat()} {BIB.relative_to(ROOT)}")
    for e in es:
        doi = e.get("doi")
        if not doi:
            if args.lookup and e["type"] != "misc":
                key = "lookup:" + e["key"]
                if key not in cache:
                    cache[key] = lookup(e) or {}
                    cache[key]["fetched"] = date.today().isoformat()
                r = cache[key]
                if r.get("doi"):
                    print(f"find {e['key']:28s} {r['doi']}  ({r['title']!r} / {r['first_author']} / {r['year']} / {r['container']})")
                else:
                    print(f"none {e['key']:28s} no Crossref match by title and first author")
            else:
                print(f"--   {e['key']:28s} no DOI ({e['type']}; see its comment)")
            continue
        if doi.lower() not in cache:
            cache[doi.lower()] = fetch(doi)
        r = cache[doi.lower()]
        t_ok = norm(r["title"]).startswith(norm(e["title"])[:40]) or \
            norm(e["title"]).startswith(norm(r["title"])[:40])
        first = e.get("author", "").split(" and ")[0].split(",")[0]
        a_ok = norm(r["first_author"]) == norm(first) or norm(first).endswith(norm(r["first_author"]))
        y_ok = str(r["year"]) == e.get("year")
        status = "ok" if t_ok and a_ok else ("known" if e["key"] in KNOWN else "BAD")
        bad += status == "BAD"
        note = "" if y_ok else f" (year: bib {e.get('year')}, {r['registry']} {r['year']})"
        print(f"{status:5s} {e['key']:28s} {r['registry']:8s} {doi}{note}")
        if status != "ok":
            print(f"     registry: {r['title']!r} / {r['first_author']}"
                  + (f"; accepted: {KNOWN[e['key']]}" if status == "known" else ""))
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n")
    print(f"{len(es)} entries, {sum(1 for e in es if e.get('doi'))} with a DOI, {bad} disagree")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
