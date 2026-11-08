"""Medidas: valores esperados de observáveis."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import scipy.sparse as sps

from .objeto import ObjQuantico

__all__ = ["valor_esperado", "valores_esperados"]


def _matriz_observavel(observavel: Any) -> tuple[np.ndarray | sps.csr_array, bool]:
    """Dados do observável e se ele é hermitiano."""
    if isinstance(observavel, ObjQuantico):
        return observavel.dados, observavel.eh_hermitiano()
    if sps.issparse(observavel):
        return observavel, ObjQuantico(observavel).eh_hermitiano()
    matriz = np.asarray(observavel)
    return matriz, ObjQuantico(matriz).eh_hermitiano()


def _matriz_de_kets(estados: Any) -> tuple[np.ndarray, bool]:
    """Estados como colunas de uma matriz ``(N, T)`` e se a entrada era um único ket."""
    if hasattr(estados, "vetores"):  # Resultado de resolver_schrodinger
        return np.asarray(estados.vetores), False
    if isinstance(estados, ObjQuantico):
        if estados.tipo == "bra":
            estados = estados.dag()
        return estados.full(), True
    if isinstance(estados, (list, tuple)) and estados and isinstance(estados[0], ObjQuantico):
        return np.hstack([e.full() if e.tipo != "bra" else e.dag().full() for e in estados]), False
    matriz = np.asarray(estados)
    if matriz.ndim == 1:
        return matriz.reshape(-1, 1), True
    if matriz.ndim == 2:
        return matriz, matriz.shape[1] == 1
    raise ValueError("os estados devem ser um vetor (N,) ou uma matriz (N, T)")


def valor_esperado(estado: Any, observavel: Any) -> Any:
    """Valor esperado :math:`\\langle O \\rangle` de um observável.

    Parameters
    ----------
    estado : ObjQuantico, ndarray ou Resultado
        * ket (ou bra): :math:`\\langle\\psi|O|\\psi\\rangle`;
        * operador (matriz densidade :math:`\\rho`): :math:`\\mathrm{Tr}(\\rho O)`;
        * ``ndarray`` de forma ``(N,)``: um vetor de estado;
        * ``ndarray`` de forma ``(N, T)``, lista de kets ou ``Resultado``: um estado por
          coluna (por exemplo, ao longo do tempo) — retorna um array com ``T`` valores.
    observavel : ObjQuantico ou array_like
        Operador :math:`O` (denso ou esparso).

    Returns
    -------
    float, complex ou ndarray
        Real se o observável for hermitiano, complexo caso contrário.

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.valor_esperado(qb.ket("0"), qb.pauliZ())
    1.0
    """
    matriz, hermitiano = _matriz_observavel(observavel)

    if isinstance(estado, ObjQuantico) and estado.tipo == "operador":
        valor = complex((estado * ObjQuantico(matriz)).traco())
        return valor.real if hermitiano else valor

    kets, unico = _matriz_de_kets(estado)
    if kets.shape[0] != matriz.shape[1]:
        raise ValueError(
            f"dimensões incompatíveis: estado com {kets.shape[0]} componentes e observável "
            f"{matriz.shape}"
        )
    # <psi_t|O|psi_t> para todas as colunas t de uma vez.
    valores = np.einsum("it,it->t", kets.conj(), matriz @ kets)
    if hermitiano:
        valores = valores.real
    return valores[0].item() if unico else valores


def valores_esperados(estados: Any, observaveis: Any | Sequence[Any]) -> list[Any]:
    """Valores esperados de vários observáveis: ``[valor_esperado(estados, O) for O in ...]``.

    Parameters
    ----------
    estados : ObjQuantico, ndarray, lista de kets ou Resultado
        Ver :func:`valor_esperado`.
    observaveis : ObjQuantico ou lista
        Um observável ou uma lista deles.

    Returns
    -------
    list
        Um item por observável (``float``/``complex`` ou ``ndarray`` com um valor por estado).
    """
    if isinstance(observaveis, ObjQuantico) or sps.issparse(observaveis):
        observaveis = [observaveis]
    return [valor_esperado(estados, observavel) for observavel in observaveis]
