# Atalhos do Sphinx. Uso: make html  (a partir desta pasta)
SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= python -m sphinx
SOURCEDIR     = source
BUILDDIR      = _build

.PHONY: help Makefile clean
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	rm -rf "$(BUILDDIR)" "$(SOURCEDIR)/tutoriais"

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
