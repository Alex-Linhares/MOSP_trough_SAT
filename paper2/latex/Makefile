# Builds paper2/latex/main.pdf, the first full draft of paper 2.
#   make          latexmk -pdf (pdflatex + bibtex as often as needed)
#   make tables   regenerate tables/*.tex from the recorded CSVs
#   make refs     check every DOI in refs.bib against Crossref / DataCite (cached)
#   make check    fail on undefined references or citations in the last build
#   make clean    remove build products but the PDF
all: main.pdf

main.pdf: main.tex $(wildcard sec*.tex) refs.bib $(wildcard tables/*.tex) $(wildcard ../figures/*.pdf)
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

tables:
	cd ../.. && python3 -m paper2.latex.make_tables

refs:
	cd ../.. && python3 -m paper2.latex.check_refs

check: main.pdf
	@! grep -E "undefined|Citation .* undefined|Reference .* undefined" main.log
	@echo "no undefined references; $$(pdfinfo main.pdf | grep Pages)"

clean:
	latexmk -c
	rm -f *.bbl *.blg *.synctex.gz

distclean: clean
	rm -f main.pdf

.PHONY: all tables refs check clean distclean
