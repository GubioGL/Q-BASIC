# Atalhos de desenvolvimento do Q-BASIC.
# No Windows sem "make", rode os comandos de cada alvo diretamente.

PYTHON ?= python

.PHONY: help install install-dev test cov lint format build clean

help:  ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "} {printf "  %-12s %s\n", $$1, $$2}'

install:  ## Instala o pacote
	$(PYTHON) -m pip install .

install-dev:  ## Instala em modo editável com ferramentas de desenvolvimento
	$(PYTHON) -m pip install -e ".[dev]"
	pre-commit install

test:  ## Roda os testes unitários
	$(PYTHON) -m pytest

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
	rm -rf build dist src/*.egg-info .pytest_cache .ruff_cache .coverage coverage.xml htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
