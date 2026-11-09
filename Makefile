# Atalhos de desenvolvimento do Q-BASIC.
# No Windows sem "make", rode os comandos de cada alvo diretamente.

PYTHON ?= python

.PHONY: help install install-dev test doctest bench tutoriais livro artigo docs cov lint format build clean

help:  ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "} {printf "  %-12s %s\n", $$1, $$2}'

install:  ## Instala o pacote
	$(PYTHON) -m pip install .

install-dev:  ## Instala em modo editável com ferramentas de desenvolvimento
	$(PYTHON) -m pip install -e ".[dev]"
	pre-commit install

test:  ## Roda os testes unitários
	$(PYTHON) -m pytest

doctest:  ## Roda os exemplos das docstrings
	$(PYTHON) -m pytest --doctest-modules src/qbasic --ignore=src/qbasic/class_tijolo.py --ignore=src/qbasic/operador.py --ignore=src/qbasic/funçoes.py

bench:  ## Compara o desempenho com a versão anterior à reestruturação
	$(PYTHON) benchmarks/comparar_versoes.py --saida benchmarks/resultados.md --json benchmarks/resultados.json

tutoriais:  ## Executa todos os notebooks dos tutoriais (precisa de ".[tutorial]" e nbmake)
	MPLBACKEND=Agg $(PYTHON) -m pytest --nbmake --nbmake-timeout=600 tutoriais/simulador tutoriais/computacao_quantica

livro:  ## Gera o livro dos tutoriais em LaTeX e PDF (precisa de ".[livro]" e XeLaTeX)
	$(PYTHON) scripts/gerar_tutorial_latex.py --pdf

artigo:  ## Gera as figuras e o PDF do artigo (precisa de ".[plot]" e LaTeX)
	$(PYTHON) paper/gerar_figuras.py
	cd paper/artigo && latexmk -pdf -interaction=nonstopmode main.tex

docs:  ## Gera o site de documentação em docs/_build/html (precisa de ".[docs]")
	MPLBACKEND=Agg $(PYTHON) -m sphinx -W --keep-going -b html docs/source docs/_build/html

cov:  ## Roda os testes com relatório de cobertura (terminal + htmlcov/)
	$(PYTHON) -m pytest --cov=qbasic --cov-report=term-missing --cov-report=html

lint:  ## Verifica estilo e erros comuns (sem alterar arquivos)
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:  ## Corrige estilo e formatação automaticamente
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

build:  ## Gera o pacote (sdist + wheel) em dist/ e verifica os metadados
	$(PYTHON) -m build
	$(PYTHON) -m twine check --strict dist/*

clean:  ## Remove arquivos gerados
	rm -rf build dist src/*.egg-info .pytest_cache .ruff_cache .coverage coverage.xml htmlcov docs/_build docs/source/tutoriais tutorial_latex/build
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
