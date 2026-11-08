"""Estados quânticos: base computacional, kets/bras de qubits, Fock, coerente e matriz densidade."""

from __future__ import annotations

import numbers
from collections.abc import Sequence

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spla
from scipy.special import gammaln

from ._compat import getattr_obsoleto
from .objeto import ObjQuantico
from .operadores import _validar_dimensao, destruicao

__all__ = ["bases", "bra", "coerente", "fock", "ket", "matriz_densidade"]

METODOS_COERENTE = ("operador", "analitico")


def _validar_indice(n: object, N: int) -> int:
    if isinstance(n, bool) or not isinstance(n, numbers.Integral):
        raise ValueError(f"o índice n deve ser um inteiro (recebido {n!r})")
    if not 0 <= n < N:
        raise ValueError(f"o índice n deve estar entre 0 e N-1 = {N - 1} (recebido {n})")
    return int(n)


def _vetor_base(N: int, n: int, sparsa: bool, latex: str | None = None, dims=None):
    if sparsa:
        vetor = sps.csr_array(([1.0 + 0j], ([n], [0])), shape=(N, 1))
    else:
        vetor = np.zeros((N, 1), dtype=complex)
        vetor[n, 0] = 1
    return ObjQuantico(vetor, latex, formato="esparso" if sparsa else "denso", dims=dims)


def bases(N: int, n: int, sparsa: bool = False) -> ObjQuantico:
    """Vetor da base :math:`|n\\rangle` num espaço de dimensão ``N``.

    Parameters
    ----------
    N : int
        Dimensão do espaço de Hilbert.
    n : int
        Índice do vetor da base, ``0 <= n < N``.
    sparsa : bool, optional
        Se ``True``, usa o formato esparso.

    Raises
    ------
    ValueError
        Se ``N`` não for um inteiro positivo ou ``n`` estiver fora de ``[0, N)``.

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.bases(3, 1).full().ravel()
    array([0.+0.j, 1.+0.j, 0.+0.j])
    """
    try:
        N = _validar_dimensao(N)
    except ValueError as erro:
        raise ValueError(f"N deve ser um inteiro positivo (recebido {N!r})") from erro
    return _vetor_base(N, _validar_indice(n, N), sparsa)


def fock(N: int, n: int = 0, sparsa: bool = False) -> ObjQuantico:
    """Estado de Fock (número) :math:`|n\\rangle` com ``N`` níveis; por padrão, o vácuo."""
    return bases(N, n, sparsa=sparsa)


def _rotulo_qubits(entrada: object) -> str:
    """Converte a entrada de ``ket``/``bra`` num rótulo binário (ex.: ``"01"``)."""
    if isinstance(entrada, str):
        if entrada and set(entrada) <= {"0", "1"}:
            return entrada
    elif isinstance(entrada, numbers.Integral) and entrada in (0, 1):
        return str(int(entrada))
    raise ValueError(
        f"entrada inválida {entrada!r}: use '0', '1', 0, 1 ou uma sequência de qubits como "
        "'0110' (para outros estados, use bases(N, n))"
    )


def ket(entrada: str | int, sparsa: bool = False) -> ObjQuantico:
    """Ket de um ou mais qubits na base computacional.

    Parameters
    ----------
    entrada : str or int
        ``'0'``, ``'1'``, ``0``, ``1`` ou uma sequência de bits, como ``'0110'``: um ket
        de 4 qubits, :math:`|0\\rangle|1\\rangle|1\\rangle|0\\rangle`.
    sparsa : bool, optional
        Se ``True``, usa o formato esparso.

    Raises
    ------
    ValueError
        Se a entrada não for um rótulo binário válido.

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.ket("1").full().ravel()
    array([0.+0.j, 1.+0.j])
    >>> qb.ket("01").dims
    [[2, 2], [1, 1]]
    """
    rotulo = _rotulo_qubits(entrada)
    n_qubits = len(rotulo)
    return _vetor_base(
        2**n_qubits,
        int(rotulo, 2),
        sparsa,
        latex=rf"$$ \ket{{{rotulo}}} $$",
        dims=[[2] * n_qubits, [1] * n_qubits],
    )


def bra(entrada: str | int, sparsa: bool = False) -> ObjQuantico:
    """Bra de um ou mais qubits, ``ket(entrada).dag()``."""
    return ket(entrada, sparsa=sparsa).dag()


def coerente(N: int, alpha: complex, metodo: str = "operador", sparsa: bool = False) -> ObjQuantico:
    """Estado coerente :math:`|\\alpha\\rangle` truncado em ``N`` níveis de Fock.

    Parameters
    ----------
    N : int
        Número de níveis de Fock.
    alpha : complex
        Amplitude do estado coerente (:math:`\\langle n \\rangle = |\\alpha|^2`).
    metodo : {"operador", "analitico"}, optional
        ``"operador"`` aplica o operador deslocamento
        :math:`D(\\alpha) = e^{\\alpha a^\\dagger - \\alpha^* a}` ao vácuo (no espaço
        truncado). ``"analitico"`` usa os coeficientes
        :math:`e^{-|\\alpha|^2/2}\\alpha^n/\\sqrt{n!}`, calculados em escala logarítmica
        para não estourar com ``N`` grande.
    sparsa : bool, optional
        Se ``True``, retorna no formato esparso.

    Raises
    ------
    ValueError
        Se ``metodo`` não for ``"operador"`` nem ``"analitico"``.
    """
    N = _validar_dimensao(N)
    if metodo not in METODOS_COERENTE:
        raise ValueError(f"metodo deve ser 'operador' ou 'analitico' (recebido {metodo!r})")
    formato = "esparso" if sparsa else "denso"
    alpha = complex(alpha)

    if metodo == "operador":
        a = destruicao(N, sparsa=True).dados
        gerador = alpha * a.conj().T - np.conj(alpha) * a
        vacuo = np.zeros(N, dtype=complex)
        vacuo[0] = 1
        vetor = spla.expm_multiply(sps.csc_array(gerador), vacuo)
        return ObjQuantico(vetor, formato=formato)

    n = np.arange(N)
    if alpha == 0:
        coeficientes = (n == 0).astype(complex)
    else:
        log_modulo = -(abs(alpha) ** 2) / 2 + n * np.log(abs(alpha)) - 0.5 * gammaln(n + 1)
        coeficientes = np.exp(log_modulo + 1j * n * np.angle(alpha))
    return ObjQuantico(coeficientes, formato=formato)


def matriz_densidade(
    estados: ObjQuantico | Sequence[ObjQuantico],
    probabilidades: Sequence[float] | None = None,
    sparsa: bool = False,
) -> ObjQuantico:
    """Matriz densidade :math:`\\rho = \\sum_k p_k |\\psi_k\\rangle\\langle\\psi_k|`.

    Parameters
    ----------
    estados : ObjQuantico or sequence of ObjQuantico
        Um ket (estado puro, :math:`\\rho = |\\psi\\rangle\\langle\\psi|`) ou uma lista de kets
        normalizados (estado misto).
    probabilidades : sequence of float, optional
        Pesos :math:`p_k` da mistura (obrigatório para uma lista de estados). Devem ser
        não negativos, somar 1 e ter o mesmo tamanho da lista de estados.
    sparsa : bool, optional
        Se ``True``, retorna no formato esparso.

    Raises
    ------
    ValueError
        Se as probabilidades forem inválidas, se os tamanhos não baterem ou se algum
        estado não for um ket normalizado.

    Examples
    --------
    >>> import qbasic as qb
    >>> rho = qb.matriz_densidade([qb.ket("0"), qb.ket("1")], [0.5, 0.5])
    >>> rho.full().real
    array([[0.5, 0. ],
           [0. , 0.5]])
    """
    formato = "esparso" if sparsa else "denso"
    if isinstance(estados, ObjQuantico):
        if probabilidades is not None and not np.allclose(np.asarray(probabilidades), [1]):
            raise ValueError("para um único estado, omita as probabilidades")
        if estados.tipo != "ket":
            raise ValueError(f"o estado deve ser um ket (recebido um {estados.tipo})")
        return ObjQuantico(estados * estados.dag(), formato=formato)

    estados = list(estados)
    if probabilidades is None:
        raise ValueError("informe as probabilidades de cada estado da mistura")
    probabilidades = np.asarray(probabilidades, dtype=float)
    if probabilidades.ndim != 1 or len(probabilidades) != len(estados):
        raise ValueError(
            f"o número de probabilidades ({probabilidades.size}) é diferente do número de "
            f"estados ({len(estados)})"
        )
    if len(estados) == 0:
        raise ValueError("a lista de estados está vazia")
    if np.any(probabilidades < 0):
        raise ValueError("as probabilidades devem ser não negativas")
    if not np.isclose(probabilidades.sum(), 1):
        raise ValueError("As probabilidades devem somar 1.")
    for estado in estados:
        if not isinstance(estado, ObjQuantico) or estado.tipo != "ket":
            raise ValueError("todos os estados devem ser kets (ObjQuantico coluna)")
        if not np.isclose(estado.norma(), 1):
            raise ValueError("Todos os estados devem ser normalizados.")
    if len({estado.shape for estado in estados}) != 1:
        raise ValueError("todos os estados devem ter a mesma dimensão")

    vetores = np.hstack([estado.full() for estado in estados])  # (N, k)
    rho = (vetores * probabilidades) @ vetores.conj().T
    return ObjQuantico(rho, formato=formato, dims=[estados[0].dims[0]] * 2)


# Nomes antigos (obsoletos)
__getattr__ = getattr_obsoleto("qbasic.estados", {"Fock": ("qbasic.fock", lambda: fock)})
