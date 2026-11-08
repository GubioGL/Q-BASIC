"""Operadores: identidade, criação/destruição, posição/momento, Pauli e produto tensorial."""

from __future__ import annotations

import numbers
from collections.abc import Iterable
from functools import reduce

import numpy as np
import scipy.sparse as sps

from .objeto import ObjQuantico

__all__ = [
    "criacao",
    "destruicao",
    "identidade",
    "operador_p",
    "operador_x",
    "pauliX",
    "pauliY",
    "pauliZ",
    "tensor",
]


def _validar_dimensao(N: object, nome: str = "N") -> int:
    """Garante que ``N`` é um inteiro positivo."""
    if isinstance(N, bool) or not isinstance(N, numbers.Integral) or N < 1:
        raise ValueError(f"{nome} deve ser um inteiro positivo (recebido {N!r})")
    return int(N)


def _criar(matriz, sparsa: bool, latex: str | None = None) -> ObjQuantico:
    return ObjQuantico(matriz, latex, formato="esparso" if sparsa else "denso")


def identidade(N: int, sparsa: bool = False) -> ObjQuantico:
    """Operador identidade :math:`I` de dimensão ``N``.

    Parameters
    ----------
    N : int
        Dimensão do espaço de Hilbert.
    sparsa : bool, optional
        Se ``True``, usa o formato esparso.

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.identidade(2).full()
    array([[1., 0.],
           [0., 1.]])
    """
    N = _validar_dimensao(N)
    matriz = sps.identity(N, format="csr") if sparsa else np.identity(N)
    return _criar(matriz, sparsa)


def destruicao(N: int, sparsa: bool = False) -> ObjQuantico:
    """Operador de destruição (aniquilação) :math:`a`, truncado em ``N`` níveis de Fock.

    Satisfaz :math:`a|n\\rangle = \\sqrt{n}\\,|n-1\\rangle`.

    Parameters
    ----------
    N : int
        Número de níveis de Fock (dimensão do espaço de Hilbert).
    sparsa : bool, optional
        Se ``True``, usa o formato esparso.
    """
    N = _validar_dimensao(N)
    elementos = np.sqrt(np.arange(1, N))
    if sparsa:
        matriz = sps.diags([elementos], offsets=[1], shape=(N, N), format="csr")
    else:
        matriz = np.diag(elementos, k=1) if N > 1 else np.zeros((1, 1))
    return _criar(matriz, sparsa)


def criacao(N: int, sparsa: bool = False) -> ObjQuantico:
    """Operador de criação :math:`a^\\dagger`, truncado em ``N`` níveis de Fock.

    Satisfaz :math:`a^\\dagger|n\\rangle = \\sqrt{n+1}\\,|n+1\\rangle` (para ``n < N-1``).
    """
    return destruicao(N, sparsa=sparsa).dag()


def operador_x(N: int, sparsa: bool = False) -> ObjQuantico:
    """Operador posição (quadratura) :math:`x = (a + a^\\dagger)/\\sqrt{2}`."""
    a = destruicao(N, sparsa=sparsa)
    return (a + a.dag()) / np.sqrt(2)


def operador_p(N: int, sparsa: bool = False) -> ObjQuantico:
    """Operador momento (quadratura) :math:`p = -i(a - a^\\dagger)/\\sqrt{2}`."""
    a = destruicao(N, sparsa=sparsa)
    return -1j * (a - a.dag()) / np.sqrt(2)


def pauliX(sparsa: bool = False) -> ObjQuantico:
    """Matriz de Pauli :math:`\\sigma_x` (porta NOT quântica)."""
    return _criar(np.array([[0, 1], [1, 0]]), sparsa, r"$$ \hat{\sigma}_x $$")


def pauliY(sparsa: bool = False) -> ObjQuantico:
    """Matriz de Pauli :math:`\\sigma_y`."""
    return _criar(np.array([[0, -1j], [1j, 0]]), sparsa, r"$$ \hat{\sigma}_y $$")


def pauliZ(sparsa: bool = False) -> ObjQuantico:
    """Matriz de Pauli :math:`\\sigma_z`."""
    return _criar(np.array([[1, 0], [0, -1]]), sparsa, r"$$ \hat{\sigma}_z $$")


def tensor(*objetos: ObjQuantico | Iterable[ObjQuantico]) -> ObjQuantico:
    """Produto tensorial :math:`A \\otimes B \\otimes \\cdots`.

    Equivale a ``A @ B @ ...``. Aceita os objetos como argumentos ou numa lista.

    Examples
    --------
    >>> import qbasic as qb
    >>> psi = qb.tensor(qb.ket("0"), qb.ket("1"))   # |01>
    >>> psi.dims
    [[2, 2], [1, 1]]
    """
    if len(objetos) == 1 and not isinstance(objetos[0], ObjQuantico):
        objetos = tuple(objetos[0])
    if not objetos:
        raise ValueError("tensor() precisa de pelo menos um objeto")
    for objeto in objetos:
        if not isinstance(objeto, ObjQuantico):
            raise TypeError(f"tensor() aceita apenas ObjQuantico, não {type(objeto).__name__}")
    return reduce(lambda a, b: a @ b, objetos)
