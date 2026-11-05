# Builds paper3/latex/main.pdf — paper 3 (title fixed by the owner, verbatim in main.tex).
#   make          latexmk -pdf (pdflatex + bibtex as often as needed)
#   make check    fail on undefined references or citations in the last build
#   make clean    remove build products but the PDF
# Figures are produced by the scripts under ../scripts/ into figures/;
# tables likewise into tables/ (item 02 and item 06 write them).
all: main.pdf

main.pdf: main.tex $(wildcard sec*.tex) refs.bib $(wildcard tables/*.tex) $(wildcard figures/*.pdf)
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

check: main.pdf
	@! grep -E "undefined|Citation .* undefined|Reference .* undefined" main.log
	@echo "no undefined references; $$(pdfinfo main.pdf | grep Pages)"

clean:
	latexmk -c
	rm -f *.bbl *.blg *.synctex.gz

distclean: clean
	rm -f main.pdf

.PHONY: all check clean distclean
