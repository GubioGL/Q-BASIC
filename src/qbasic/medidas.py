"""Medidas e grandezas derivadas de estados: valores esperados, probabilidades e
amostragem de medidas, traço parcial, pureza, entropia, fidelidade e vetor de Bloch."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import scipy.linalg as sla
import scipy.sparse as sps

from .objeto import ObjQuantico

__all__ = [
    "amostrar",
    "entropia_von_neumann",
    "fidelidade",
    "probabilidades",
    "pureza",
    "traco_parcial",
    "valor_esperado",
    "valores_esperados",
    "vetor_bloch",
]


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
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


def _como_densidade(estado: ObjQuantico) -> np.ndarray:
    """Matriz densidade (densa) de um ket, bra ou operador."""
    if not isinstance(estado, ObjQuantico):
        estado = ObjQuantico(estado)
    if estado.tipo == "bra":
        estado = estado.dag()
    if estado.tipo == "ket":
        vetor = estado.full()
        return vetor @ vetor.conj().T
    if estado.shape[0] != estado.shape[1]:
        raise ValueError(f"esperava um ket ou uma matriz densidade (forma {estado.shape})")
    return estado.full()


def _autovalores_densidade(estado: ObjQuantico) -> np.ndarray:
    valores = sla.eigvalsh(_como_densidade(estado))
    return np.clip(valores, 0, None)


# ---------------------------------------------------------------------------
# Valores esperados
# ---------------------------------------------------------------------------
def valor_esperado(estado: Any, observavel: Any) -> Any:
    """Valor esperado :math:`\\langle O \\rangle` de um observável.

    Parameters
    ----------
    estado : ObjQuantico, ndarray ou Resultado
        * ket (ou bra): :math:`\\langle\\psi|O|\\psi\\rangle`;
        * operador (matriz densidade :math:`\\rho`): :math:`\\mathrm{Tr}(\\rho O)`;
        * ``ndarray`` de forma ``(N,)``: um vetor de estado;
        * ``ndarray`` de forma ``(N, T)``, lista de kets ou ``Resultado`` (de
          :func:`~qbasic.resolver_schrodinger` ou :func:`~qbasic.resolver_lindblad`): um
          estado por instante — retorna um array com ``T`` valores.
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

    if getattr(estado, "tipo", None) == "densidade":  # Resultado de resolver_lindblad
        n = estado.dimensao
        rhos = np.asarray(estado.vetores).reshape(n, n, -1, order="F")
        operador = matriz.toarray() if sps.issparse(matriz) else np.asarray(matriz)
        valores = np.einsum("ij,jit->t", operador, rhos)  # Tr(O rho_t)
        return valores.real if hermitiano else valores

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


# ---------------------------------------------------------------------------
# Probabilidades e amostragem
# ---------------------------------------------------------------------------
def probabilidades(estado: ObjQuantico) -> np.ndarray:
    """Probabilidades de cada vetor da base computacional.

    :math:`p_k = |\\langle k|\\psi\\rangle|^2` para um ket, ou :math:`\\rho_{kk}` para uma
    matriz densidade.

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.probabilidades((qb.ket("0") + qb.ket("1")) / 2**0.5).round(3)
    array([0.5, 0.5])
    """
    if estado.tipo in ("ket", "bra"):
        return np.abs(estado.full().ravel()) ** 2
    return np.real(np.diag(_como_densidade(estado))).clip(0, None)


def _rotulos(dims: list[int]) -> list[str]:
    """Rótulos dos vetores da base: ``"01"`` para qubits, ``"0,2"`` em geral."""
    indices = np.indices(dims).reshape(len(dims), -1).T
    separador = "" if all(d == 2 for d in dims) else ","
    return [separador.join(str(i) for i in linha) for linha in indices]


def amostrar(
    estado: ObjQuantico, n_amostras: int = 1000, semente: int | None = None
) -> dict[str, int]:
    """Simula ``n_amostras`` medidas na base computacional e conta os resultados.

    Parameters
    ----------
    estado : ObjQuantico
        Ket ou matriz densidade.
    n_amostras : int, optional
        Número de repetições da medida.
    semente : int, optional
        Semente do gerador de números aleatórios (para resultados reprodutíveis).

    Returns
    -------
    dict
        Contagem de cada resultado, por exemplo ``{"00": 497, "11": 503}`` para um par de
        Bell. Para sistemas que não são de qubits, os rótulos são índices separados por
        vírgula (``"0,2"``). Resultados que não ocorreram não aparecem.

    Examples
    --------
    >>> import qbasic as qb
    >>> contagens = qb.amostrar(qb.bell("phi+"), 1000, semente=1)
    >>> sorted(contagens), sum(contagens.values())
    (['00', '11'], 1000)
    """
    p = probabilidades(estado)
    p = p / p.sum()
    contagens = np.random.default_rng(semente).multinomial(int(n_amostras), p)
    dims = estado.dims[0] if estado.tipo != "bra" else estado.dims[1]
    return {rotulo: int(n) for rotulo, n in zip(_rotulos(dims), contagens, strict=True) if n > 0}


# ---------------------------------------------------------------------------
# Traço parcial, pureza, entropia e fidelidade
# ---------------------------------------------------------------------------
def traco_parcial(estado: ObjQuantico, manter: int | Sequence[int]) -> ObjQuantico:
    """Traço parcial: matriz densidade reduzida dos subsistemas em ``manter``.

    Os subsistemas são definidos por ``estado.dims`` (por exemplo, ``[[2, 2], [1, 1]]`` para
    dois qubits, numerados 0 e 1 da esquerda para a direita).

    Parameters
    ----------
    estado : ObjQuantico
        Ket ou matriz densidade de um sistema composto.
    manter : int or sequence of int
        Índices dos subsistemas que permanecem (os demais são traçados). A ordem dada é a
        ordem dos subsistemas no resultado.

    Returns
    -------
    ObjQuantico
        Matriz densidade reduzida, com os ``dims`` dos subsistemas mantidos.

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.traco_parcial(qb.bell("phi+"), 0).full().real
    array([[0.5, 0. ],
           [0. , 0.5]])
    """
    dims = estado.dims[0] if estado.tipo != "bra" else estado.dims[1]
    manter = [manter] if isinstance(manter, (int, np.integer)) else list(manter)
    n = len(dims)
    if not manter or len(set(manter)) != len(manter) or any(not 0 <= k < n for k in manter):
        raise ValueError(f"manter deve conter índices distintos entre 0 e {n - 1}: {manter}")
    rho = _como_densidade(estado).reshape(dims + dims)
    letras = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if 2 * n > len(letras):
        raise ValueError("número de subsistemas grande demais para o traço parcial")
    linhas = list(letras[:n])
    colunas = [linhas[k] if k not in manter else letras[n + k] for k in range(n)]
    saida = "".join(linhas[k] for k in manter) + "".join(colunas[k] for k in manter)
    reduzida = np.einsum(f"{''.join(linhas)}{''.join(colunas)}->{saida}", rho)
    dims_mantidas = [dims[k] for k in manter]
    tamanho = int(np.prod(dims_mantidas))
    return ObjQuantico(reduzida.reshape(tamanho, tamanho), dims=[dims_mantidas, dims_mantidas])


def pureza(estado: ObjQuantico) -> float:
    """Pureza :math:`\\mathrm{Tr}(\\rho^2)`: 1 para estados puros, :math:`1/N` para o estado
    maximamente misturado."""
    if estado.tipo in ("ket", "bra"):
        return float(estado.norma() ** 4)
    rho = _como_densidade(estado)
    return float(np.real(np.vdot(rho.conj().T, rho)))


def entropia_von_neumann(estado: ObjQuantico, base: float = 2) -> float:
    """Entropia de von Neumann :math:`S = -\\mathrm{Tr}(\\rho \\log \\rho)`.

    Parameters
    ----------
    estado : ObjQuantico
        Ket (entropia zero) ou matriz densidade.
    base : float, optional
        Base do logaritmo: 2 (padrão, resultado em bits) ou ``numpy.e`` (em nats).

    Examples
    --------
    >>> import qbasic as qb
    >>> round(qb.entropia_von_neumann(qb.traco_parcial(qb.bell("phi+"), 0)), 6)
    1.0
    """
    valores = _autovalores_densidade(estado)
    valores = valores[valores > 1e-15]
    return float(max(0.0, -np.sum(valores * np.log(valores)) / np.log(base)))


def fidelidade(estado_a: ObjQuantico, estado_b: ObjQuantico) -> float:
    """Fidelidade :math:`F(\\rho, \\sigma) = \\left(\\mathrm{Tr}\\sqrt{\\sqrt{\\rho}\\,\\sigma
    \\sqrt{\\rho}}\\right)^2`, entre 0 e 1.

    Para dois estados puros, :math:`F = |\\langle\\psi|\\phi\\rangle|^2`; para um puro e um
    misto, :math:`F = \\langle\\psi|\\rho|\\psi\\rangle`.

    Examples
    --------
    >>> import qbasic as qb
    >>> round(qb.fidelidade(qb.ket("0"), (qb.ket("0") + qb.ket("1")) / 2**0.5), 6)
    0.5
    """
    puros = [e.tipo in ("ket", "bra") for e in (estado_a, estado_b)]
    if all(puros):
        a = estado_a.full().ravel()
        b = estado_b.full().ravel()
        return float(abs(np.vdot(a, b)) ** 2)
    if any(puros):
        puro, misto = (estado_a, estado_b) if puros[0] else (estado_b, estado_a)
        vetor = puro.full().ravel()
        return float(np.real(np.vdot(vetor, _como_densidade(misto) @ vetor)))
    rho, sigma = _como_densidade(estado_a), _como_densidade(estado_b)
    valores, vetores = sla.eigh(rho)
    raiz_rho = (vetores * np.sqrt(np.clip(valores, 0, None))) @ vetores.conj().T
    meio = sla.eigvalsh(raiz_rho @ sigma @ raiz_rho)
    return float(np.sum(np.sqrt(np.clip(meio, 0, None))) ** 2)


def vetor_bloch(estado: ObjQuantico) -> np.ndarray:
    """Vetor de Bloch :math:`(\\langle X\\rangle, \\langle Y\\rangle, \\langle Z\\rangle)` de um
    qubit (ket ou matriz densidade 2×2).

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.vetor_bloch(qb.ket("0"))
    array([0., 0., 1.])
    """
    rho = _como_densidade(estado)
    if rho.shape != (2, 2):
        raise ValueError(f"o vetor de Bloch é definido para um qubit (forma recebida {rho.shape})")
    x = 2 * rho[0, 1].real
    y = -2 * rho[0, 1].imag
    z = (rho[0, 0] - rho[1, 1]).real
    return np.array([x, y, z]) + 0.0
