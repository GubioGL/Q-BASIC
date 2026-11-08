"""
Q-BASIC — Quantum Brazilian Algorithms, SImulations, and Computational tools.

Simulador quântico didático em Python (NumPy/SciPy), com matrizes densas e esparsas.

Uso básico::

    import qbasic as qb

    psi = qb.ket("0")              # |0>
    X = qb.pauliX()
    print(X * psi)                 # |1>

Módulos
-------
objeto
    Classe base :class:`ObjQuantico` (estados e operadores, densos ou esparsos).
estados
    ``bases``, ``ket``, ``bra``, ``fock``, ``coerente``, ``matriz_densidade``.
operadores
    ``identidade``, ``destruicao``, ``criacao``, ``operador_x``, ``operador_p``,
    ``pauliX``, ``pauliY``, ``pauliZ``, ``tensor``.
medidas
    ``valor_esperado``, ``valores_esperados``.
dinamica
    ``resolver_schrodinger`` e ``Resultado``.
visualizacao
    Representação em LaTeX.

Os nomes antigos (``destruiçao``, ``criaçao``, ``Identidade``, ``Fock``,
``matrizdensidade``, ``edo``, ``Valor_esperado``, ``ObjQuantico_esparso`` e os módulos
``class_tijolo``, ``operador`` e ``funçoes``) continuam funcionando, com um aviso de
obsolescência (``DeprecationWarning``).
"""

from . import dinamica, estados, medidas, objeto, operadores, visualizacao
from ._compat import getattr_obsoleto as _getattr_obsoleto
from ._compat import importar_sem_aviso as _importar_sem_aviso
from ._version import __version__
from .dinamica import Resultado, resolver_schrodinger
from .estados import bases, bra, coerente, fock, ket, matriz_densidade
from .medidas import valor_esperado, valores_esperados
from .objeto import ObjQuantico
from .operadores import (
    criacao,
    destruicao,
    identidade,
    operador_p,
    operador_x,
    pauliX,
    pauliY,
    pauliZ,
    tensor,
)

__all__ = [
    "ObjQuantico",
    "Resultado",
    "__version__",
    "bases",
    "bra",
    "coerente",
    "criacao",
    "destruicao",
    "dinamica",
    "estados",
    "fock",
    "identidade",
    "ket",
    "matriz_densidade",
    "medidas",
    "objeto",
    "operador_p",
    "operador_x",
    "operadores",
    "pauliX",
    "pauliY",
    "pauliZ",
    "resolver_schrodinger",
    "tensor",
    "valor_esperado",
    "valores_esperados",
    "visualizacao",
]


def _de_compat(modulo: str, nome: str):
    return lambda: getattr(_importar_sem_aviso(f"qbasic.{modulo}"), nome)


# Nomes antigos (obsoletos desde a versão 0.1.0): continuam funcionando com aviso.
__getattr__ = _getattr_obsoleto(
    "qbasic",
    {
        "destruiçao": ("qbasic.destruicao", lambda: destruicao),
        "criaçao": ("qbasic.criacao", lambda: criacao),
        "Identidade": ("qbasic.identidade", lambda: identidade),
        "Fock": ("qbasic.fock", lambda: fock),
        "matrizdensidade": (
            "qbasic.matriz_densidade",
            _de_compat("operador", "matrizdensidade"),
        ),
        "ObjQuantico_esparso": (
            'qbasic.ObjQuantico(dados, formato="esparso")',
            lambda: objeto.ObjQuantico_esparso,
        ),
        "edo": ("qbasic.resolver_schrodinger", _de_compat("funçoes", "edo")),
        "Valor_esperado": ("qbasic.valores_esperados", _de_compat("funçoes", "Valor_esperado")),
        "class_tijolo": ("qbasic.objeto", lambda: _importar_sem_aviso("qbasic.class_tijolo")),
        "operador": ("qbasic.operadores", lambda: _importar_sem_aviso("qbasic.operador")),
        "funçoes": (
            "qbasic.dinamica e qbasic.medidas",
            lambda: _importar_sem_aviso("qbasic.funçoes"),
        ),
    },
)
