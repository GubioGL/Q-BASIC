"""Dinâmica: evolução temporal pela equação de Schrödinger."""

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

__all__ = ["Resultado", "resolver_schrodinger"]

# Tolerâncias padrão dos integradores numéricos (as do SciPy, rtol=1e-3, não conservam
# a norma do estado de forma aceitável).
RTOL_PADRAO = 1e-8
ATOL_PADRAO = 1e-10


@dataclass
class Resultado:
    """Resultado de :func:`resolver_schrodinger`.

    Attributes
    ----------
    tempos : ndarray
        Instantes de tempo, forma ``(T,)``.
    vetores : ndarray
        Vetores de estado como colunas, forma ``(N, T)``.
    valores_esperados : list of ndarray
        Um array ``(T,)`` para cada observável pedido.
    metodo : str
        Método usado (``"expm"`` ou o nome do integrador do SciPy).
    dims : list
        Dimensões dos subsistemas do estado inicial.
    """

    tempos: np.ndarray
    vetores: np.ndarray
    valores_esperados: list[np.ndarray] = field(default_factory=list)
    metodo: str = "expm"
    dims: list = field(default_factory=list)

    @property
    def estados(self) -> list[ObjQuantico]:
        """Lista de kets, um para cada instante."""
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
            f"Resultado(metodo={self.metodo!r}, {len(self.tempos)} instantes de "
            f"{self.tempos[0]:g} a {self.tempos[-1]:g}, dimensão {self.vetores.shape[0]}, "
            f"{len(self.valores_esperados)} observável(is))"
        )


def _validar_entradas(H: ObjQuantico, psi0: ObjQuantico, tempos: Any) -> np.ndarray:
    if not isinstance(H, ObjQuantico) or not isinstance(psi0, ObjQuantico):
        raise TypeError("H e psi0 devem ser ObjQuantico")
    if H.shape[0] != H.shape[1]:
        raise ValueError(f"o Hamiltoniano deve ser quadrado (forma {H.shape})")
    if psi0.tipo != "ket":
        raise ValueError(f"o estado inicial deve ser um ket (recebido um {psi0.tipo})")
    if psi0.shape[0] != H.shape[0]:
        raise ValueError(
            f"dimensões incompatíveis: H é {H.shape} e o estado tem {psi0.shape[0]} componentes"
        )
    tempos = np.asarray(tempos, dtype=float)
    if tempos.ndim != 1 or tempos.size == 0:
        raise ValueError("tempos deve ser uma sequência 1-D com pelo menos um instante")
    if tempos.size > 1 and np.any(np.diff(tempos) <= 0):
        raise ValueError("tempos deve ser estritamente crescente")
    return tempos


def _evoluir_expm(H: np.ndarray | sps.csr_array, v0: np.ndarray, tempos: np.ndarray) -> np.ndarray:
    """Evolução exata :math:`e^{-iH(t-t_0)}|\\psi_0\\rangle` com ``expm_multiply``."""
    gerador = -1j * (sps.csc_array(H) if sps.issparse(H) else np.asarray(H))
    if tempos.size == 1:
        return v0.reshape(-1, 1)
    passos = np.diff(tempos)
    if np.allclose(passos, passos[0]):
        # Grade uniforme: uma única chamada calcula todos os instantes.
        estados = spla.expm_multiply(
            gerador,
            v0,
            start=0.0,
            stop=tempos[-1] - tempos[0],
            num=tempos.size,
            endpoint=True,
        )
        return np.asarray(estados).T
    vetores = np.empty((v0.size, tempos.size), dtype=complex)
    vetores[:, 0] = v0
    for k, passo in enumerate(passos, start=1):
        vetores[:, k] = spla.expm_multiply(gerador * passo, vetores[:, k - 1])
    return vetores


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
    tempos = _validar_entradas(H, psi0, tempos)
    v0 = psi0.full().ravel().astype(complex)

    if metodo == "expm":
        vetores = _evoluir_expm(H.dados, v0, tempos)
    else:
        matriz = H.dados

        def derivada(_t: float, y: np.ndarray) -> np.ndarray:
            return -1j * (matriz @ y)

        if tempos.size == 1:
            vetores = v0.reshape(-1, 1)
        else:
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
            vetores = solucao.y

    resultado = Resultado(tempos=tempos, vetores=vetores, metodo=metodo, dims=psi0.dims)
    if observaveis is not None:
        resultado.valores_esperados = [
            np.atleast_1d(valor) for valor in valores_esperados(vetores, observaveis)
        ]
    return resultado
