"""Obsoleto: use :mod:`qbasic.operadores` (e :mod:`qbasic.estados` para a matriz densidade).

Mantido para que códigos antigos continuem funcionando. Nomes antigos e novos:

=====================  ==========================
Antigo                 Novo
=====================  ==========================
``Identidade``         ``identidade``
``destruiçao``         ``destruicao``
``criaçao``            ``criacao``
``matrizdensidade``    ``matriz_densidade``
=====================  ==========================
"""

import warnings

from .estados import matriz_densidade
from .operadores import (
    criacao,
    destruicao,
    identidade,
    operador_p,
    operador_x,
    pauliX,
    pauliY,
    pauliZ,
)

__all__ = [
    "Identidade",
    "criaçao",
    "destruiçao",
    "matrizdensidade",
    "operador_p",
    "operador_x",
    "pauliX",
    "pauliY",
    "pauliZ",
]

warnings.warn(
    "'qbasic.operador' está obsoleto e será removido numa versão futura; use 'qbasic.operadores' "
    "(nomes novos: identidade, destruicao, criacao, matriz_densidade).",
    DeprecationWarning,
    stacklevel=2,
)

Identidade = identidade
destruiçao = destruicao
criaçao = criacao


def matrizdensidade(probabilities=None, estados=None, puro=True, sparsa=False):
    """Obsoleto: use :func:`qbasic.matriz_densidade`.

    Nova assinatura: ``matriz_densidade(estados, probabilidades, sparsa)``.
    """
    if puro:
        return matriz_densidade(estados, sparsa=sparsa)
    return matriz_densidade(estados, probabilities, sparsa=sparsa)
