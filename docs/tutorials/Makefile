# Makefile for Sphinx documentation
# PyArchInit Tutorials

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets for building specific languages
pdf-it:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/it" -D master_doc=it/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/it" && make all-pdf

pdf-en:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/en" -D master_doc=en/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/en" && make all-pdf

pdf-de:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/de" -D master_doc=de/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/de" && make all-pdf

pdf-fr:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/fr" -D master_doc=fr/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/fr" && make all-pdf

pdf-es:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/es" -D master_doc=es/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/es" && make all-pdf

pdf-ar:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/ar" -D master_doc=ar/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/ar" && make all-pdf

pdf-ca:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex/ca" -D master_doc=ca/index $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex/ca" && make all-pdf

# Build all PDFs
pdf-all: pdf-it pdf-en pdf-de pdf-fr pdf-es pdf-ar pdf-ca
	@echo "All PDF documentation built successfully!"

# Build HTML documentation
html-all:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "HTML documentation built in $(BUILDDIR)/html"

# Clean build directory
clean:
	rm -rf "$(BUILDDIR)"/*
	@echo "Build directory cleaned"

# Install dependencies
install-deps:
	pip install sphinx myst-parser sphinx-rtd-theme linkify-it-py

# Quick PDF build (single combined document)
pdf:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS)
	@cd "$(BUILDDIR)/latex" && make all-pdf
	@echo "PDF built in $(BUILDDIR)/latex/"
