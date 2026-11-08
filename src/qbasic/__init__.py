"""
Q-BASIC — Quantum Brazilian Algorithms, SImulations, and Computational tools.

Simulador quântico didático em Python (NumPy/SciPy), com suporte a matrizes
densas e esparsas.

Módulos
-------
class_tijolo
    Classes base ``ObjQuantico`` (densa) e ``ObjQuantico_esparso`` (esparsa).
estados
    Estados quânticos: ``bases``, ``ket``, ``bra``, ``Fock``, ``coerente``.
operador
    Operadores: identidade, criação/destruição, posição/momento, Pauli,
    matriz densidade.
funçoes
    Dinâmica (equação de Schrödinger) e valores esperados.
"""

from ._version import __version__
from .class_tijolo import ObjQuantico, ObjQuantico_esparso
from .estados import Fock, bases, bra, coerente, ket
from .funçoes import Valor_esperado, edo, valor_esperado
from .operador import (
    Identidade,
    criaçao,
    destruiçao,
    matrizdensidade,
    operador_p,
    operador_x,
    pauliX,
    pauliY,
    pauliZ,
)

__all__ = [
    "Fock",
    "Identidade",
    "ObjQuantico",
    "ObjQuantico_esparso",
    "Valor_esperado",
    "__version__",
    "bases",
    "bra",
    "coerente",
    "criaçao",
    "destruiçao",
    "edo",
    "ket",
    "matrizdensidade",
    "operador_p",
    "operador_x",
    "pauliX",
    "pauliY",
    "pauliZ",
    "valor_esperado",
]
