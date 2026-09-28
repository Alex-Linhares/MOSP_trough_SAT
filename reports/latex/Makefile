# Builds reports/latex/main.pdf. `make` runs latexmk (pdflatex + bibtex as
# many times as needed); `make clean` removes every build product but the PDF.
all: main.pdf

main.pdf: main.tex references.bib $(wildcard figures/*.png)
	latexmk -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -c
	rm -f *.bbl *.blg *.synctex.gz

distclean: clean
	rm -f main.pdf

.PHONY: all clean distclean
