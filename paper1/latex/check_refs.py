"""Check every DOI in paper1/latex/refs.bib against its registry (loop0008 item 08).

    python -m paper1.latex.check_refs            # uses the cache, fetches what is missing
    python -m paper1.latex.check_refs --refresh  # fetches everything again

For each entry with a `doi`, fetch the record from Crossref, or from DataCite
when Crossref does not know it (LIPIcs, arXiv), and compare the title, the
year and the first author's family name with the entry. The responses are
cached in `paper1/latex/data/doi_check.json` with the date of the fetch.
Prints one line per entry and exits non-zero if a title or first author
disagrees. A year that differs is reported, not failed: Crossref often gives
the online-first year where the bibliography gives the volume's.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIB = HERE / "refs.bib"
CACHE = HERE / "data" / "doi_check.json"
# Disagreements read by hand on 2026-10-03 and accepted, with the reason.
KNOWN = {
    "LY2002ref8": "Crossref puts the whole name, 'Omar Wing', in the family field",
    "LY2002ref9": "Crossref carries the publisher's typo 'Interval graphs and seatching'",
    "Kitsunai2016": "Crossref's title carries MathML residue; the words agree",
}
UA = {"User-Agent": "paper1-refcheck/0.1 (mailto:none@example.org)"}


def entries(text: str) -> list[dict]:
    out = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):
        body = m.group(3)
        fields = {k.lower(): re.sub(r"\s+", " ", v).strip()
                  for k, v in re.findall(r"(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", body)}
        fields["key"], fields["type"] = m.group(2).strip(), m.group(1).lower()
        out.append(fields)
    return out


def norm(s: str) -> str:
    s = re.sub(r"\\[a-zA-Z]+\s*|[{}$\\^]", "", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def fetch(doi: str) -> dict:
    try:
        req = urllib.request.Request(f"https://api.crossref.org/works/{doi}", headers=UA)
        m = json.load(urllib.request.urlopen(req, timeout=30))["message"]
        year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        return {"registry": "crossref", "title": (m.get("title") or [""])[0], "year": year,
                "first_author": (m.get("author") or [{}])[0].get("family", ""),
                "fetched": date.today().isoformat()}
    except Exception:  # noqa: BLE001 - fall through to DataCite
        req = urllib.request.Request(f"https://api.datacite.org/dois/{doi}", headers=UA)
        a = json.load(urllib.request.urlopen(req, timeout=30))["data"]["attributes"]
        return {"registry": "datacite", "title": a["titles"][0]["title"],
                "year": int(a["publicationYear"]),
                "first_author": a["creators"][0].get("familyName", ""),
                "fetched": date.today().isoformat()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    cache = {} if args.refresh or not CACHE.exists() else json.loads(CACHE.read_text())
    bad = 0
    es = entries(BIB.read_text())
    for e in es:
        doi = e.get("doi")
        if not doi:
            print(f"--   {e['key']:28s} no DOI (checked by hand, see its comment)")
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
