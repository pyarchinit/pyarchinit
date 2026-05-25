PANDOC ?= pandoc
SRC := PyArchInit_SRS_StratiGraph_v3.md
HTML := PyArchInit_SRS_StratiGraph_v3.html
PDF  := PyArchInit_SRS_StratiGraph_v3.pdf
CSS  := style.css

.PHONY: all html pdf clean

all: html pdf

html: $(HTML)

$(HTML): $(SRC) $(CSS)
	$(PANDOC) $(SRC) \
	  --from markdown \
	  --to html5 \
	  --standalone \
	  --self-contained \
	  --toc --toc-depth=2 \
	  --metadata title="PyArchInit SRS - StratiGraph (v3)" \
	  --css $(CSS) \
	  -o $@

pdf: $(PDF)

$(PDF): $(SRC)
	$(PANDOC) $(SRC) \
	  --from markdown \
	  --to pdf \
	  --pdf-engine=xelatex \
	  --toc --toc-depth=2 \
	  -V geometry:margin=2cm \
	  -V mainfont="Helvetica Neue" \
	  -V monofont="Menlo" \
	  -V colorlinks=true \
	  -V linkcolor=NavyBlue \
	  -V documentclass=article \
	  -o $@

clean:
	rm -f $(HTML) $(PDF)
