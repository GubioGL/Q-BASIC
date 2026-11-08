"""Dinâmica: equação de Schrödinger (sistemas fechados) e equação mestra de Lindblad
(sistemas abertos)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spla
from scipy.integrate import solve_ivp

from .medidas import valores_esperados
from .objeto import ObjQuantico

__all__ = ["Resultado", "liouvilliano", "resolver_lindblad", "resolver_schrodinger"]

# Tolerâncias padrão dos integradores numéricos (as do SciPy, rtol=1e-3, não conservam
# a norma do estado de forma aceitável).
RTOL_PADRAO = 1e-8
ATOL_PADRAO = 1e-10


@dataclass
class Resultado:
    """Resultado de :func:`resolver_schrodinger` ou :func:`resolver_lindblad`.

    Attributes
    ----------
    tempos : ndarray
        Instantes de tempo, forma ``(T,)``.
    vetores : ndarray
        Um estado por coluna: kets, forma ``(N, T)``, ou matrizes densidade vetorizadas
        (coluna por coluna), forma ``(N², T)``.
    valores_esperados : list of ndarray
        Um array ``(T,)`` para cada observável pedido.
    metodo : str
        Método usado (``"expm"`` ou o nome do integrador do SciPy).
    dims : list
        Dimensões dos subsistemas do estado inicial.
    tipo : {"ket", "densidade"}
        Tipo dos estados guardados.
    """

    tempos: np.ndarray
    vetores: np.ndarray
    valores_esperados: list[np.ndarray] = field(default_factory=list)
    metodo: str = "expm"
    dims: list = field(default_factory=list)
    tipo: str = "ket"

    @property
    def dimensao(self) -> int:
        """Dimensão do espaço de Hilbert."""
        n = self.vetores.shape[0]
        return int(round(np.sqrt(n))) if self.tipo == "densidade" else n

    @property
    def estados(self) -> list[ObjQuantico]:
        """Lista de estados (kets ou matrizes densidade), um para cada instante."""
        if self.tipo == "densidade":
            n = self.dimensao
            dims = [self.dims[0], self.dims[0]] if self.dims else None
            return [
                ObjQuantico(self.vetores[:, k].reshape(n, n, order="F"), dims=dims)
                for k in range(self.vetores.shape[1])
            ]
        dims = self.dims or None
        return [ObjQuantico(self.vetores[:, k], dims=dims) for k in range(self.vetores.shape[1])]

    @property
    def t(self) -> np.ndarray:
        """Apelido de :attr:`tempos` (mesmo nome do ``solve_ivp``)."""
        return self.tempos

    @property
    def y(self) -> np.ndarray:
        """Apelido de :attr:`vetores` (mesmo nome do ``solve_ivp``)."""
        return self.vetores

    def __repr__(self) -> str:
        return (
            f"Resultado(metodo={self.metodo!r}, tipo={self.tipo!r}, {len(self.tempos)} "
            f"instantes de {self.tempos[0]:g} a {self.tempos[-1]:g}, dimensão {self.dimensao}, "
            f"{len(self.valores_esperados)} observável(is))"
        )


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def _validar_tempos(tempos: Any) -> np.ndarray:
    tempos = np.asarray(tempos, dtype=float)
    if tempos.ndim != 1 or tempos.size == 0:
        raise ValueError("tempos deve ser uma sequência 1-D com pelo menos um instante")
    if tempos.size > 1 and np.any(np.diff(tempos) <= 0):
        raise ValueError("tempos deve ser estritamente crescente")
    return tempos


def _validar_hamiltoniano(H: Any) -> None:
    if not isinstance(H, ObjQuantico):
        raise TypeError("H e o estado inicial devem ser ObjQuantico")
    if H.shape[0] != H.shape[1]:
        raise ValueError(f"o Hamiltoniano deve ser quadrado (forma {H.shape})")


def _evoluir(
    gerador: np.ndarray | sps.csr_array,
    v0: np.ndarray,
    tempos: np.ndarray,
    metodo: str,
    rtol: float,
    atol: float,
    opcoes: dict,
) -> np.ndarray:
    """Resolve :math:`dv/dt = G v`, devolvendo ``v(t)`` em colunas, forma ``(n, T)``."""
    if tempos.size == 1:
        return v0.reshape(-1, 1)

    if metodo == "expm":
        # Solução exata v(t) = exp(G (t - t0)) v0, sem formar a exponencial da matriz.
        if sps.issparse(gerador):
            gerador = sps.csc_array(gerador)
        passos = np.diff(tempos)
        if np.allclose(passos, passos[0]):
            # Grade uniforme: uma única chamada calcula todos os instantes.
            vetores = spla.expm_multiply(
                gerador, v0, start=0.0, stop=tempos[-1] - tempos[0], num=tempos.size, endpoint=True
            )
            return np.asarray(vetores).T
        vetores = np.empty((v0.size, tempos.size), dtype=complex)
        vetores[:, 0] = v0
        for k, passo in enumerate(passos, start=1):
            vetores[:, k] = spla.expm_multiply(gerador * passo, vetores[:, k - 1])
        return vetores

    def derivada(_t: float, y: np.ndarray) -> np.ndarray:
        return gerador @ y

    solucao = solve_ivp(
        derivada,
        (tempos[0], tempos[-1]),
        v0,
        method=metodo,
        t_eval=tempos,
        rtol=rtol,
        atol=atol,
        **opcoes,
    )
    if not solucao.success:
        raise RuntimeError(f"o integrador {metodo} falhou: {solucao.message}")
    return solucao.y


def _calcular_observaveis(resultado: Resultado, observaveis: Any) -> None:
    if observaveis is not None:
        resultado.valores_esperados = [
            np.atleast_1d(valor) for valor in valores_esperados(resultado, observaveis)
        ]


# ---------------------------------------------------------------------------
# Schrödinger
# ---------------------------------------------------------------------------
def resolver_schrodinger(
    H: ObjQuantico,
    psi0: ObjQuantico,
    tempos: Sequence[float] | np.ndarray,
    observaveis: ObjQuantico | Sequence[ObjQuantico] | None = None,
    *,
    metodo: str = "expm",
    rtol: float = RTOL_PADRAO,
    atol: float = ATOL_PADRAO,
    **opcoes: Any,
) -> Resultado:
    """Resolve a equação de Schrödinger, :math:`i\\,d|\\psi\\rangle/dt = H|\\psi\\rangle`.

    Unidades com :math:`\\hbar = 1`.

    Parameters
    ----------
    H : ObjQuantico
        Hamiltoniano (independente do tempo), denso ou esparso.
    psi0 : ObjQuantico
        Estado inicial (ket) no instante ``tempos[0]``.
    tempos : array_like
        Instantes (crescentes) em que o estado é calculado.
    observaveis : ObjQuantico ou lista, optional
        Observáveis cujos valores esperados são calculados em cada instante.
    metodo : str, optional
        ``"expm"`` (padrão): evolução exata com :func:`scipy.sparse.linalg.expm_multiply`,
        sem converter matrizes esparsas para densas. Também aceita qualquer método do
        :func:`scipy.integrate.solve_ivp` com suporte a números complexos (``"RK45"``,
        ``"DOP853"``, ``"RK23"``, ``"BDF"``, ``"Radau"``).
    rtol, atol : float, optional
        Tolerâncias relativas e absolutas dos integradores (ignoradas por ``"expm"``).
    **opcoes
        Repassadas ao ``solve_ivp``.

    Returns
    -------
    Resultado
        Com ``tempos``, ``vetores`` (ou a lista ``estados``) e ``valores_esperados``.

    Examples
    --------
    Oscilação de Rabi de um qubit:

    >>> import numpy as np
    >>> import qbasic as qb
    >>> tempos = np.linspace(0, np.pi, 5)
    >>> res = qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), tempos, [qb.pauliZ()])
    >>> bool(np.allclose(res.valores_esperados[0], np.cos(2 * tempos)))  # <Z>(t) = cos(2t)
    True
    """
    _validar_hamiltoniano(H)
    if not isinstance(psi0, ObjQuantico):
        raise TypeError("H e o estado inicial devem ser ObjQuantico")
    if psi0.tipo != "ket":
        raise ValueError(f"o estado inicial deve ser um ket (recebido um {psi0.tipo})")
    if psi0.shape[0] != H.shape[0]:
        raise ValueError(
            f"dimensões incompatíveis: H é {H.shape} e o estado tem {psi0.shape[0]} componentes"
        )
    tempos = _validar_tempos(tempos)
    v0 = psi0.full().ravel().astype(complex)
    vetores = _evoluir(-1j * H.dados, v0, tempos, metodo, rtol, atol, opcoes)
    resultado = Resultado(tempos=tempos, vetores=vetores, metodo=metodo, dims=psi0.dims)
    _calcular_observaveis(resultado, observaveis)
    return resultado


# ---------------------------------------------------------------------------
# Lindblad
# ---------------------------------------------------------------------------
def liouvilliano(H: ObjQuantico, operadores_colapso: Sequence[ObjQuantico] = ()) -> ObjQuantico:
    """Superoperador de Lindblad :math:`\\mathcal{L}`, com :math:`d\\,\\mathrm{vec}(\\rho)/dt
    = \\mathcal{L}\\,\\mathrm{vec}(\\rho)`.

    .. math::

        \\mathcal{L}\\rho = -i[H, \\rho] + \\sum_k \\Big(L_k \\rho L_k^\\dagger
        - \\tfrac{1}{2}\\{L_k^\\dagger L_k, \\rho\\}\\Big)

    A vetorização empilha as colunas de :math:`\\rho` (``order="F"``), de modo que
    :math:`\\mathrm{vec}(A X B) = (B^T \\otimes A)\\,\\mathrm{vec}(X)`.

    Parameters
    ----------
    H : ObjQuantico
        Hamiltoniano, :math:`N \\times N`.
    operadores_colapso : sequence of ObjQuantico
        Operadores de salto :math:`L_k` (com as taxas já incluídas, por exemplo
        :math:`\\sqrt{\\gamma}\\,a`).

    Returns
    -------
    ObjQuantico
        Matriz esparsa :math:`N^2 \\times N^2`.
    """
    _validar_hamiltoniano(H)
    n = H.shape[0]
    identidade = sps.identity(n, format="csr", dtype=complex)
    h = sps.csr_array(H.full_sparsa(), dtype=complex)
    gerador = -1j * (sps.kron(identidade, h) - sps.kron(h.T, identidade))
    for L in operadores_colapso:
        if not isinstance(L, ObjQuantico) or L.shape != H.shape:
            raise ValueError(f"cada operador de colapso deve ser um ObjQuantico {H.shape}")
        ell = sps.csr_array(L.full_sparsa(), dtype=complex)
        ldl = ell.conj().T @ ell
        gerador = gerador + (
            sps.kron(ell.conj(), ell)
            - 0.5 * sps.kron(identidade, ldl)
            - 0.5 * sps.kron(ldl.T, identidade)
        )
    return ObjQuantico(sps.csr_array(gerador), formato="esparso")


def resolver_lindblad(
    H: ObjQuantico,
    estado0: ObjQuantico,
    tempos: Sequence[float] | np.ndarray,
    operadores_colapso: Sequence[ObjQuantico] = (),
    observaveis: ObjQuantico | Sequence[ObjQuantico] | None = None,
    *,
    metodo: str = "expm",
    rtol: float = RTOL_PADRAO,
    atol: float = ATOL_PADRAO,
    **opcoes: Any,
) -> Resultado:
    """Resolve a equação mestra de Lindblad (sistemas abertos), com :math:`\\hbar = 1`.

    .. math::

        \\frac{d\\rho}{dt} = -i[H, \\rho] + \\sum_k \\Big(L_k \\rho L_k^\\dagger
        - \\tfrac{1}{2}\\{L_k^\\dagger L_k, \\rho\\}\\Big)

    Parameters
    ----------
    H : ObjQuantico
        Hamiltoniano (independente do tempo).
    estado0 : ObjQuantico
        Estado inicial: um ket (convertido em :math:`|\\psi\\rangle\\langle\\psi|`) ou uma
        matriz densidade.
    tempos : array_like
        Instantes (crescentes) em que o estado é calculado.
    operadores_colapso : sequence of ObjQuantico, optional
        Operadores de salto :math:`L_k`, com as taxas incluídas: por exemplo,
        :math:`\\sqrt{\\gamma}\\,\\sigma_-` para emissão espontânea com taxa
        :math:`\\gamma`. Sem eles, a evolução é unitária.
    observaveis : ObjQuantico ou lista, optional
        Observáveis cujos valores esperados :math:`\\mathrm{Tr}(\\rho O)` são calculados.
    metodo : str, optional
        ``"expm"`` (padrão, exato) ou um método do ``solve_ivp`` (``"RK45"``, ``"DOP853"``...).
    rtol, atol : float, optional
        Tolerâncias dos integradores (ignoradas por ``"expm"``).
    **opcoes
        Repassadas ao ``solve_ivp``.

    Returns
    -------
    Resultado
        Com ``tipo="densidade"``: ``estados`` é a lista de matrizes densidade.

    Examples
    --------
    Decaimento de um átomo de dois níveis (:math:`|1\\rangle` excitado) com taxa
    :math:`\\gamma = 0{,}5`:

    >>> import numpy as np
    >>> import qbasic as qb
    >>> sm = qb.destruicao(2)                       # |1> -> |0>
    >>> tempos = np.linspace(0, 4, 5)
    >>> res = qb.resolver_lindblad(qb.identidade(2) * 0, qb.ket("1"), tempos,
    ...                            [np.sqrt(0.5) * sm], [sm.dag() * sm])
    >>> bool(np.allclose(res.valores_esperados[0], np.exp(-0.5 * tempos)))
    True
    """
    _validar_hamiltoniano(H)
    if not isinstance(estado0, ObjQuantico):
        raise TypeError("H e o estado inicial devem ser ObjQuantico")
    if estado0.tipo == "ket":
        estado0 = estado0 * estado0.dag()
    elif estado0.tipo != "operador":
        raise ValueError(
            f"o estado inicial deve ser um ket ou uma matriz densidade (recebido um {estado0.tipo})"
        )
    if estado0.shape != H.shape:
        raise ValueError(
            f"dimensões incompatíveis: H é {H.shape} e o estado inicial é {estado0.shape}"
        )
    tempos = _validar_tempos(tempos)
    gerador = liouvilliano(H, operadores_colapso).dados
    v0 = estado0.full().ravel(order="F").astype(complex)
    vetores = _evoluir(gerador, v0, tempos, metodo, rtol, atol, opcoes)
    resultado = Resultado(
        tempos=tempos, vetores=vetores, metodo=metodo, dims=estado0.dims, tipo="densidade"
    )
    _calcular_observaveis(resultado, observaveis)
    return resultado
