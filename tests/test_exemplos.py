"""Executa os scripts de ``exemplos/`` para garantir que continuam funcionando."""

import runpy
import warnings
from pathlib import Path

import pytest

PASTA_EXEMPLOS = Path(__file__).resolve().parents[1] / "exemplos"
EXEMPLOS = sorted(PASTA_EXEMPLOS.glob("*.py"))


@pytest.mark.parametrize("script", EXEMPLOS, ids=lambda caminho: caminho.name)
def test_exemplo_executa(script, monkeypatch):
    # Versões antigas do matplotlib usam APIs obsoletas do pyparsing ao serem
    # importadas; isso não tem relação com o Q-BASIC.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        matplotlib = pytest.importorskip("matplotlib")
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

    # Os exemplos chamam plt.show(); nos testes não há janela para abrir.
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)
    try:
        runpy.run_path(str(script), run_name="__main__")
    finally:
        plt.close("all")
