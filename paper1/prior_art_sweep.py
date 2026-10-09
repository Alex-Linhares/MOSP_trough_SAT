"""Prior-art sweep of every work citing Chu & Stuckey (2009) or Chu (2011).

loop0008 item 01 (2026-10-03). The question is whether anyone has restated,
implemented, tested or corrected the definite move or the better move: CP 2009
Theorems 1 and 2, thesis Theorems 6.3.6 and 6.3.8.

Steps, each cached under `paper1/data/prior_art/`:

1. **Citers.** OpenAlex `cites:` on the CP paper (W1493287964), the thesis
   (W2278850436) and its IJCAI extended abstract (W2295506942); Semantic
   Scholar's citation lists for the same three; OpenCitations (the open
   Crossref-derived index; Crossref's own cited-by service is members-only)
   for the CP DOI. Merged by DOI, else by normalised title.
2. **Full texts.** Every open-access PDF URL any index gives, plus arXiv,
   downloaded to `fulltext/` (git-ignored) and converted by `pdftotext`.
   Works held in `literature/`, or fetched by hand, are read from there
   (`HELD` below).
3. **Search.** Each text is searched for the rules (`PATTERNS`); hits are
   written with context to `hits.txt` so they can be read by eye.

Outputs: `citers.csv` (one row per work), `hits.txt`. The verdict per work is
written by hand into `paper1/prior_art_counterexample.md`, from `hits.txt`.

    python3 -m paper1.prior_art_sweep            # uses the caches
    python3 -m paper1.prior_art_sweep --refresh  # re-queries the indexes
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = HERE / "data" / "prior_art"
FULL = DATA / "fulltext"
MAILTO = "a@linhares.ltd"
UA = "Mozilla/5.0 (X11; Linux x86_64) prior-art-sweep (mailto:%s)" % MAILTO

CP_DOI = "10.1007/978-3-642-04244-7_21"
TARGETS = {  # label -> (OpenAlex id, Semantic Scholar id)
    "cp2009": ("W1493287964", "DOI:" + CP_DOI),
    "thesis2011": ("W2278850436", "a15e7cf954a097fee86d4f82f1c250a63f530198"),
    "ijcai2013": ("W2295506942", "2f4c86dcb0e13c030ee89b70bd711e1a4f95e402"),
}

# Full texts not reachable through the indexes, by work key (DOI, or "t:" + the
# normalised title) -> (path under the repository, where it came from, date).
# `literature/...` are held copies; `fulltext/manual/...` were fetched by hand on
# 2026-10-03 (author pages, institutional repositories; git-ignored).
M = "paper1/data/prior_art/fulltext/manual/"
HELD = {
    "10.1007/s10601-011-9112-9": (
        "literature/2012-Chu-Garcia-de-la-Banda-Stuckey-Exploiting-Subproblem-Dominance-Constraint-Programming-Constraints.pdf",
        "held"),
    "10.1111/itor.12109": ("literature/goncalves_2016_brkga_mosp.pdf", "held"),
    "10.1371/journal.pone.0203076": ("literature/plosone_2018_pagerank_mosp.pdf", "held"),
    "10.1111/itor.13053": ("literature/martin_yanasse_pinto_2022_math_models_mosp.pdf", "held"),
    "t:improvingcombinatorialoptimization": (
        "literature/chu_2011_phd_thesis_improving_combinatorial_optimization.pdf", "held, hdl:11343/36679"),
    "t:adeltaevaluationfunctionforcolumnpermutationproblems": (
        "literature/2024-Lima-Santos-Carvalho-Delta-Evaluation-Function-Column-Permutation-Problems-arXiv.pdf", "held"),
    "10.11606/t.55.2012.tde-19022013-084858": ("literature/fink_2012_phd_thesis_mosp_novas_contribuicoes.pdf", "held"),
    "10.4230/lipics.cp.2025.7": (
        M + "chastenay_2025_cp.pdf",
        "https://drops.dagstuhl.de/storage/00lipics/lipics-vol340-cp2025/LIPIcs.CP.2025.7/LIPIcs.CP.2025.7.pdf"),
    "10.1007/978-3-642-13520-0_10": (M + "chu_garcia_stuckey_2010_equivalence.pdf",
                                     "https://ndownloader.figshare.com/files/36404310"),
    "10.1287/ijoc.1090.0378": (M + "garcia_stuckey_chu_2011_talent.pdf",
                               "https://people.eng.unimelb.edu.au/pstuckey/papers/rehearsal.pdf"),
    "t:trcsseriescuttingstockwithboundedopenstacksanewintegerlinear": (
        M + "arbib_2010_trcs.pdf", "https://optimization-online.org/wp-content/uploads/2010/07/2671.pdf"),
    "t:patternsequencingmodelsincuttingstockproblems": (
        M + "lopes_2011_thesis.pdf",
        "https://repositorium.uminho.pt/bitstreams/514de5ee-875b-49e8-8e27-13d0a5c6b847/download"),
    "10.1007/978-3-642-33558-7_4": (M + "chu_stuckey_2012_dominance.pdf",
                                    "https://people.eng.unimelb.edu.au/pstuckey/papers/dominance.pdf"),
    "t:interproblemnogoodlearninginconstraintprogramming": (
        M + "chu_stuckey_2012_interprob.pdf", "https://people.eng.unimelb.edu.au/pstuckey/interprob/interprob.pdf"),
    "10.1016/j.artint.2021.103599": (M + "leo_2013_cp.pdf",
                                     "https://researchmgt.monash.edu/ws/files/444967109/352525004_oa.pdf"),
    "t:improvingcombinatorialoptimizationextendedabstract": (
        M + "chu_2013_ijcai.pdf", "https://www.ijcai.org/Proceedings/13/Papers/468.pdf"),
    "10.1007/978-3-319-18008-3_8": (M + "chu_stuckey_2015_value.pdf",
                                    "https://people.eng.unimelb.edu.au/pstuckey/papers/autopt.pdf"),
    "10.4230/lipics.cp.2025.5": (
        M + "beck_2025_cp.pdf",
        "https://drops.dagstuhl.de/storage/00lipics/lipics-vol340-cp2025/LIPIcs.CP.2025.5/LIPIcs.CP.2025.5.pdf"),
}

PATTERNS = {
    "definite": r"definite[\s-]+move",
    "better": r"better[\s-]+move",
    "old_move": r"old[\s-]+move",
    "open_stack": r"open[\s-]+stacks?",
    "chu_stuckey": r"Chu\s*(?:and|&)\s*Stuckey|Chu,?\s+G\.?,?\s+(?:and|&)?\s*Stuckey",
    "customer_search": r"customer[\s-]+search",
    "thm636": r"6\.3\.[68]",
    "counterex": r"counter-?\s?example|incorrect|erratum|does not hold|is false|unsound",
}
READ_IN_CONTEXT = ("definite", "better", "customer_search", "thm636")


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _json(url: str) -> dict:
    for attempt in range(4):
        try:
            return json.loads(_get(url))
        except Exception as e:  # rate limits on Semantic Scholar
            print(f"  retry {attempt}: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(url)


def fetch_indexes(refresh: bool) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    sel = "id,doi,title,publication_year,authorships,primary_location,open_access,best_oa_location,locations,type,ids"
    for label, (oa, s2) in TARGETS.items():
        f = DATA / f"openalex_cites_{label}.json"
        if refresh or not f.exists():
            url = (f"https://api.openalex.org/works?filter=cites:{oa}&per-page=200&select={sel}"
                   f"&mailto={MAILTO}")
            f.write_text(json.dumps(_json(url), indent=1))
        f = DATA / f"s2_cites_{label}.json"
        if refresh or not f.exists():
            url = (f"https://api.semanticscholar.org/graph/v1/paper/{s2}/citations?"
                   "fields=title,year,authors,venue,externalIds,openAccessPdf&limit=1000")
            f.write_text(json.dumps(_json(url), indent=1))
            time.sleep(3)
    f = DATA / "opencitations_cites_cp2009.json"
    if refresh or not f.exists():
        f.write_text(json.dumps(_json(f"https://api.opencitations.net/index/v2/citations/doi:{CP_DOI}"),
                                indent=1))


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:60]


def _doi(d: str | None) -> str | None:
    if not d:
        return None
    return d.lower().replace("https://doi.org/", "").strip()


def merge() -> list[dict]:
    works: dict[str, dict] = {}
    by_title: dict[str, str] = {}

    def add(label, src, doi, title, year, authors, venue, urls):
        doi = _doi(doi)
        key = doi or by_title.get(_norm(title)) or "t:" + _norm(title)
        if not doi and _norm(title) in by_title:
            key = by_title[_norm(title)]
        if doi and _norm(title) in by_title and by_title[_norm(title)] != key:
            # same title already under another key (S2 without DOI, or a second DOI)
            old = by_title[_norm(title)]
            if old.startswith("t:"):
                works[key] = works.pop(old)
                works[key]["doi"] = doi
            else:
                key = old
        w = works.setdefault(key, {"doi": doi, "title": title, "year": year, "authors": authors,
                                   "venue": venue, "cites": set(), "sources": set(), "urls": []})
        by_title[_norm(title)] = key
        w["cites"].add(label)
        w["sources"].add(src)
        if not w["venue"] and venue:
            w["venue"] = venue
        if (not w["year"]) or (year and year < w["year"]):
            w["year"] = year or w["year"]
        for u in urls:
            if u and u not in w["urls"]:
                w["urls"].append(u)

    for label in TARGETS:
        d = json.loads((DATA / f"openalex_cites_{label}.json").read_text())
        for w in d["results"]:
            urls = []
            for loc in [w.get("best_oa_location")] + (w.get("locations") or []):
                if loc and loc.get("is_oa"):
                    urls += [loc.get("pdf_url"), loc.get("landing_page_url")]
            urls.append((w.get("open_access") or {}).get("oa_url"))
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
            add(label, "openalex", w.get("doi"), w["title"], w["publication_year"],
                "; ".join(a["author"]["display_name"] for a in w["authorships"]), src, urls)
        d = json.loads((DATA / f"s2_cites_{label}.json").read_text())
        for x in d["data"]:
            p = x["citingPaper"]
            if not p.get("title"):
                continue
            ext = p.get("externalIds") or {}
            urls = [(p.get("openAccessPdf") or {}).get("url")]
            if ext.get("ArXiv"):
                urls.append(f"https://arxiv.org/pdf/{ext['ArXiv']}")
            add(label, "s2", ext.get("DOI"), p["title"], p.get("year"),
                "; ".join(a["name"] for a in p.get("authors") or []), p.get("venue"), urls)
    oc = json.loads((DATA / "opencitations_cites_cp2009.json").read_text())
    for c in oc:
        m = re.search(r"doi:(\S+)", c["citing"])
        if m and _doi(m.group(1)) in works:
            works[_doi(m.group(1))]["sources"].add("opencitations")
        elif m:
            add("cp2009", "opencitations", m.group(1), "(doi only) " + m.group(1), None, "", "", [])
    out = sorted(works.values(), key=lambda w: (w["year"] or 0, w["title"]))
    for i, w in enumerate(out):
        w["id"] = f"W{i:03d}"
    return out


def _pdf_text(w: dict) -> tuple[str, str]:
    """Return (where, text) of the first readable full text, or ("", "")."""
    FULL.mkdir(parents=True, exist_ok=True)
    (FULL / ".gitignore").write_text("*\n")
    key = w["doi"] or "t:" + _norm(w["title"])
    if key in HELD and (ROOT / HELD[key][0]).exists():
        path, origin = HELD[key]
        where = path if origin == "held" else f"{origin} ({path})"
        return where, subprocess.run(["pdftotext", str(ROOT / path), "-"],
                                     capture_output=True, text=True).stdout
    pdf = FULL / f"{w['id']}.pdf"
    if pdf.exists() and pdf.stat().st_size > 0:
        where = (FULL / f"{w['id']}.url").read_text().strip()
        return where, subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    for u in w["urls"]:
        try:
            b = _get(u)
        except Exception:
            continue
        if not b.startswith(b"%PDF"):
            # landing page: look for a citation_pdf_url meta tag
            m = re.search(rb'citation_pdf_url"\s+content="([^"]+)"', b)
            if not m:
                continue
            try:
                b = _get(urllib.parse.urljoin(u, m.group(1).decode()))
            except Exception:
                continue
            if not b.startswith(b"%PDF"):
                continue
        pdf.write_bytes(b)
        (FULL / f"{w['id']}.url").write_text(u)
        return u, subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    return "", ""


def main(argv: list[str]) -> None:
    fetch_indexes("--refresh" in argv)
    works = merge()
    rows, hits = [], []
    for w in works:
        where, text = _pdf_text(w)
        flat = re.sub(r"\s+", " ", text)
        counts = {k: len(re.findall(p, flat, flags=re.I if k != "chu_stuckey" else 0))
                  for k, p in PATTERNS.items()}
        rows.append({"id": w["id"], "year": w["year"], "authors": w["authors"], "title": w["title"],
                     "venue": w["venue"] or "", "doi": w["doi"] or "",
                     "cites": "+".join(sorted(w["cites"])), "sources": "+".join(sorted(w["sources"])),
                     "fulltext": where, "chars": len(flat), **counts})
        if any(counts[k] for k in READ_IN_CONTEXT) or (counts["open_stack"] and counts["chu_stuckey"]):
            hits.append(f"==== {w['id']} {w['year']} {w['authors'][:80]} | {w['title']}")
            for k in READ_IN_CONTEXT + ("chu_stuckey",):
                for m in re.finditer(PATTERNS[k], flat, flags=re.I if k != "chu_stuckey" else 0):
                    hits.append(f"-- [{k}] ...{flat[max(0, m.start() - 300):m.end() + 300]}...")
        print(f"{w['id']} {w['year']} {'T' if where else '-'} {w['title'][:70]}", file=sys.stderr)
    with open(DATA / "citers.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    (DATA / "hits.txt").write_text("\n".join(hits) + "\n")
    n = len(rows)
    read = sum(1 for r in rows if r["fulltext"])
    print(f"{n} distinct citing works; full text read for {read}; "
          f"{sum(1 for r in rows if 'cp2009' in r['cites'])} cite the CP paper")


if __name__ == "__main__":
    main(sys.argv[1:])
