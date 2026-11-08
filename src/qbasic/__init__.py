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
    ``bases``, ``ket``, ``bra``, ``fock``, ``coerente``, ``matriz_densidade``, ``bell``,
    ``ghz``, ``w``.
operadores
    ``identidade``, ``destruicao``, ``criacao``, ``numero``, ``operador_x``,
    ``operador_p``, ``pauliX``, ``pauliY``, ``pauliZ``, ``tensor``, ``comutador``,
    ``anticomutador``.
portas
    Portas quânticas: ``hadamard``, ``porta_s``, ``porta_t``, ``fase``, ``rx``, ``ry``,
    ``rz``, ``cnot``, ``cz``, ``swap``, ``toffoli``, ``porta_controlada``, ``porta_em``.
medidas
    ``valor_esperado``, ``valores_esperados``, ``probabilidades``, ``amostrar``,
    ``traco_parcial``, ``pureza``, ``entropia_von_neumann``, ``fidelidade``,
    ``vetor_bloch``.
dinamica
    ``resolver_schrodinger``, ``resolver_lindblad``, ``liouvilliano`` e ``Resultado``.
visualizacao
    LaTeX, função de Wigner e gráficos (``esfera_bloch``, ``plotar_wigner``,
    ``plotar_fock``, ``plotar_valores_esperados``; precisam do matplotlib).

Os nomes antigos (``destruiçao``, ``criaçao``, ``Identidade``, ``Fock``,
``matrizdensidade``, ``edo``, ``Valor_esperado``, ``ObjQuantico_esparso`` e os módulos
``class_tijolo``, ``operador`` e ``funçoes``) continuam funcionando, com um aviso de
obsolescência (``DeprecationWarning``).
"""

from . import dinamica, estados, medidas, objeto, operadores, portas, visualizacao
from ._compat import getattr_obsoleto as _getattr_obsoleto
from ._compat import importar_sem_aviso as _importar_sem_aviso
from ._version import __version__
from .dinamica import Resultado, liouvilliano, resolver_lindblad, resolver_schrodinger
from .estados import bases, bell, bra, coerente, fock, ghz, ket, matriz_densidade, w
from .medidas import (
    amostrar,
    entropia_von_neumann,
    fidelidade,
    probabilidades,
    pureza,
    traco_parcial,
    valor_esperado,
    valores_esperados,
    vetor_bloch,
)
from .objeto import ObjQuantico
from .operadores import (
    anticomutador,
    comutador,
    criacao,
    destruicao,
    identidade,
    numero,
    operador_p,
    operador_x,
    pauliX,
    pauliY,
    pauliZ,
    tensor,
)
from .portas import (
    cnot,
    cz,
    fase,
    hadamard,
    porta_controlada,
    porta_em,
    porta_s,
    porta_t,
    rx,
    ry,
    rz,
    swap,
    toffoli,
)
from .visualizacao import (
    esfera_bloch,
    plotar_fock,
    plotar_valores_esperados,
    plotar_wigner,
    wigner,
)

__all__ = [
    "ObjQuantico",
    "Resultado",
    "__version__",
    "amostrar",
    "anticomutador",
    "bases",
    "bell",
    "bra",
    "cnot",
    "coerente",
    "comutador",
    "criacao",
    "cz",
    "destruicao",
    "dinamica",
    "entropia_von_neumann",
    "esfera_bloch",
    "estados",
    "fase",
    "fidelidade",
    "fock",
    "ghz",
    "hadamard",
    "identidade",
    "ket",
    "liouvilliano",
    "matriz_densidade",
    "medidas",
    "numero",
    "objeto",
    "operador_p",
    "operador_x",
    "operadores",
    "pauliX",
    "pauliY",
    "pauliZ",
    "plotar_fock",
    "plotar_valores_esperados",
    "plotar_wigner",
    "porta_controlada",
    "porta_em",
    "porta_s",
    "porta_t",
    "portas",
    "probabilidades",
    "pureza",
    "resolver_lindblad",
    "resolver_schrodinger",
    "rx",
    "ry",
    "rz",
    "swap",
    "tensor",
    "toffoli",
    "traco_parcial",
    "valor_esperado",
    "valores_esperados",
    "vetor_bloch",
    "visualizacao",
    "w",
    "wigner",
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
