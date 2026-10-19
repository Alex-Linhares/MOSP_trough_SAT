"""Build the arXiv source bundle of *The pathwidth complex* and test-compile it.

    python -m paper1.latex.make_arxiv            # build arxiv/ and arxiv.tar.gz, then compile the bundle
    python -m paper1.latex.make_arxiv --no-test  # build only

What arXiv needs (info.arxiv.org/help/submit_tex.html): the sources, the
pre-generated main.bbl (arXiv runs BibTeX only from .bib files it is given;
shipping the .bbl pins the bibliography), every figure in PDF, and nothing
else: no .aux/.log/.pdf, no hidden files, no unused figures. Compilation runs
from the bundle's root, so the figures move from ../figures/ into figures/
and \graphicspath is rewritten to match. Everything else in main.tex is
standard TeX Live (mathpazo, microtype, natbib, hyperref without driver
options), which arXiv's TeX Live 2025 has.

The bundle is paper1/latex/arxiv/ (git-ignored) and paper1/latex/arxiv.tar.gz.
The test unpacks the tarball into a fresh temporary directory and runs
pdflatex three times with no BibTeX, as arXiv would with a .bbl present, then
fails on any undefined reference or citation and prints the page count.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent / "figures"
OUT = HERE / "arxiv"
TARBALL = HERE / "arxiv.tar.gz"
GRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")


def latexmk() -> None:
    """A fresh build, so main.bbl matches refs.bib and the sources."""
    subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                   cwd=HERE, check=True, capture_output=True)


def figure_files(sources: list[Path]) -> list[Path]:
    """Every figure the sources include, resolved to a PDF under ../figures/."""
    found: list[Path] = []
    for src in sources:
        for name in GRAPHICS.findall(src.read_text()):
            candidates = [FIGURES / name] + [FIGURES / f"{name}{ext}" for ext in (".pdf", ".png", ".jpg")]
            hit = next((c for c in candidates if c.is_file()), None)
            if hit is None:
                sys.exit(f"figure not found: {name}")
            if hit not in found:
                found.append(hit)
    return found


def build() -> Path:
    latexmk()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "tables").mkdir(parents=True)
    (OUT / "figures").mkdir()
    sources = [HERE / "main.tex"] + sorted(HERE.glob("sec*.tex"))
    for src in sources:
        text = src.read_text()
        if src.name == "main.tex":
            assert r"\graphicspath{{../figures/}}" in text
            text = text.replace(r"\graphicspath{{../figures/}}", r"\graphicspath{{figures/}}")
            assert r"\today" not in text
        (OUT / src.name).write_text(text)
    for tab in sorted((HERE / "tables").glob("*.tex")):
        shutil.copy(tab, OUT / "tables" / tab.name)
    bbl = HERE / "main.bbl"
    if not bbl.is_file():
        sys.exit("main.bbl missing: the build did not produce it")
    shutil.copy(bbl, OUT / "main.bbl")
    for fig in figure_files(sources):
        shutil.copy(fig, OUT / "figures" / fig.name)
    with tarfile.open(TARBALL, "w:gz") as tar:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                tar.add(p, arcname=str(p.relative_to(OUT)))
    files = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file())
    print(f"{TARBALL.name}: {len(files)} files, {TARBALL.stat().st_size / 1e6:.2f} MB")
    for f in files:
        print("  ", f)
    return TARBALL


def test(tarball: Path) -> None:
    """Compile the bundle as arXiv would: pdflatex only, from a clean directory."""
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(tarball) as tar:
            tar.extractall(tmp, filter="data")
        for _ in range(3):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                               cwd=tmp, capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stdout[-3000:])
                sys.exit("pdflatex failed on the bundle")
        log = Path(tmp, "main.log").read_text(errors="replace")
        bad = [l for l in log.splitlines()
               if "undefined" in l.lower() or "Citation" in l and "undefined" in l]
        if bad:
            print("\n".join(bad))
            sys.exit("undefined references or citations in the bundle")
        pages = subprocess.run(["pdfinfo", str(Path(tmp, "main.pdf"))], capture_output=True, text=True).stdout
        print("bundle compiles from scratch with pdflatex alone;",
              next(l for l in pages.splitlines() if l.startswith("Pages")))


if __name__ == "__main__":
    tb = build()
    if "--no-test" not in sys.argv:
        test(tb)
