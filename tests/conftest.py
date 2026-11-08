"""Fixtures compartilhadas pelos testes do Q-BASIC."""

import pytest


@pytest.fixture(params=[False, True], ids=["denso", "esparso"])
def sparsa(request):
    """Roda o teste duas vezes: com matrizes densas e com matrizes esparsas."""
    return request.param
