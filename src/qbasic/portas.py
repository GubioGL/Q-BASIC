"""Portas lógicas quânticas para circuitos de qubits.

Convenção de ordem: o qubit 0 é o da **esquerda** (o mais significativo), como em
``ket("01") = |0⟩ ⊗ |1⟩``. Assim, ``cnot(controle=0, alvo=1)`` leva ``|10⟩`` em ``|11⟩``.

Todas as portas têm ``dims = [[2, ..., 2], [2, ..., 2]]`` e aceitam ``sparsa=True``.
"""

from __future__ import annotations

import numbers
from collections.abc import Sequence

import numpy as np
import scipy.sparse as sps

from .objeto import ObjQuantico
from .operadores import pauliX, pauliZ

__all__ = [
    "cnot",
    "cz",
    "fase",
    "hadamard",
    "porta_controlada",
    "porta_em",
    "porta_s",
    "porta_t",
    "rx",
    "ry",
    "rz",
    "swap",
    "toffoli",
]


def _porta(matriz, sparsa: bool, latex: str | None = None) -> ObjQuantico:
    n_qubits = int(np.log2(len(matriz)))
    return ObjQuantico(
        matriz,
        latex,
        formato="esparso" if sparsa else "denso",
        dims=[[2] * n_qubits, [2] * n_qubits],
    )


def hadamard(sparsa: bool = False) -> ObjQuantico:
    """Porta de Hadamard, :math:`H = (X + Z)/\\sqrt{2}`: leva :math:`|0\\rangle` em
    :math:`|+\\rangle = (|0\\rangle + |1\\rangle)/\\sqrt{2}`."""
    return _porta(np.array([[1, 1], [1, -1]]) / np.sqrt(2), sparsa, r"$$ \hat{H} $$")


def fase(phi: float, sparsa: bool = False) -> ObjQuantico:
    """Porta de fase :math:`P(\\phi) = \\mathrm{diag}(1, e^{i\\phi})`."""
    return _porta(np.diag([1, np.exp(1j * phi)]), sparsa)


def porta_s(sparsa: bool = False) -> ObjQuantico:
    """Porta :math:`S = P(\\pi/2) = \\mathrm{diag}(1, i)`."""
    return _porta(np.diag([1, 1j]), sparsa, r"$$ \hat{S} $$")


def porta_t(sparsa: bool = False) -> ObjQuantico:
    """Porta :math:`T = P(\\pi/4) = \\mathrm{diag}(1, e^{i\\pi/4})`."""
    return _porta(np.diag([1, np.exp(1j * np.pi / 4)]), sparsa, r"$$ \hat{T} $$")


def rx(theta: float, sparsa: bool = False) -> ObjQuantico:
    """Rotação em torno do eixo x da esfera de Bloch, :math:`R_x(\\theta) = e^{-i\\theta X/2}`."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return _porta(np.array([[c, -1j * s], [-1j * s, c]]), sparsa)


def ry(theta: float, sparsa: bool = False) -> ObjQuantico:
    """Rotação em torno do eixo y, :math:`R_y(\\theta) = e^{-i\\theta Y/2}`."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return _porta(np.array([[c, -s], [s, c]]), sparsa)


def rz(theta: float, sparsa: bool = False) -> ObjQuantico:
    """Rotação em torno do eixo z, :math:`R_z(\\theta) = e^{-i\\theta Z/2}`."""
    return _porta(np.diag([np.exp(-1j * theta / 2), np.exp(1j * theta / 2)]), sparsa)


def _validar_qubits(qubits: Sequence[int], n_qubits: int) -> list[int]:
    if isinstance(n_qubits, bool) or not isinstance(n_qubits, numbers.Integral) or n_qubits < 1:
        raise ValueError(f"n_qubits deve ser um inteiro positivo (recebido {n_qubits!r})")
    qubits = [int(q) for q in qubits]
    if len(set(qubits)) != len(qubits):
        raise ValueError(f"os qubits devem ser distintos: {qubits}")
    for q in qubits:
        if not 0 <= q < n_qubits:
            raise ValueError(f"qubit {q} fora do intervalo 0..{n_qubits - 1}")
    return qubits


def porta_em(porta: ObjQuantico, alvos: int | Sequence[int], n_qubits: int) -> ObjQuantico:
    """Aplica uma porta de ``k`` qubits aos qubits ``alvos`` de um registro de ``n_qubits``.

    Os demais qubits recebem a identidade. Os alvos não precisam ser vizinhos nem estar em
    ordem: ``porta_em(cnot(), [2, 0], 3)`` é um CNOT com controle no qubit 2 e alvo no 0.

    Examples
    --------
    >>> import qbasic as qb
    >>> X1 = qb.porta_em(qb.pauliX(), 1, 3)          # X no qubit do meio
    >>> (X1 * qb.ket("000")).full().ravel().real.nonzero()[0]   # |010> = índice 2
    array([2])
    """
    alvos = [alvos] if isinstance(alvos, numbers.Integral) else list(alvos)
    alvos = _validar_qubits(alvos, n_qubits)
    k = len(alvos)
    if porta.shape != (2**k, 2**k):
        raise ValueError(f"a porta deve ser {2**k}×{2**k} para {k} qubit(s) (forma {porta.shape})")
    resto = [q for q in range(n_qubits) if q not in alvos]
    ordem = alvos + resto  # qubits na ordem em que a porta "enxerga"

    # Permutação P: |b_0 ... b_{n-1}> -> |b_ordem[0] ... b_ordem[n-1]>.
    indices = np.arange(2**n_qubits)
    bits = (indices[:, None] >> (n_qubits - 1 - np.arange(n_qubits))) & 1
    permutados = bits[:, ordem] @ (1 << (n_qubits - 1 - np.arange(n_qubits)))
    P = sps.csr_array(
        (np.ones(indices.size), (permutados, indices)), shape=(indices.size, indices.size)
    )
    U = sps.kron(porta.full_sparsa(), sps.identity(2 ** len(resto)), format="csr")
    completa = sps.csr_array(P.T @ U @ P)
    dados = completa if porta.formato == "esparso" else completa.toarray()
    return ObjQuantico(dados, dims=[[2] * n_qubits, [2] * n_qubits])


def porta_controlada(
    porta: ObjQuantico,
    controles: int | Sequence[int] = 0,
    alvo: int = 1,
    n_qubits: int = 2,
    sparsa: bool | None = None,
) -> ObjQuantico:
    """Versão controlada de uma porta de um qubit: aplica ``porta`` ao ``alvo`` quando todos
    os ``controles`` estão em :math:`|1\\rangle`.

    Parameters
    ----------
    porta : ObjQuantico
        Porta 2×2 aplicada ao alvo.
    controles : int or sequence of int
        Qubit(s) de controle.
    alvo : int
        Qubit alvo.
    n_qubits : int
        Número total de qubits do registro.
    sparsa : bool, optional
        Formato do resultado (por padrão, o mesmo da ``porta``).
    """
    controles = [controles] if isinstance(controles, numbers.Integral) else list(controles)
    if porta.shape != (2, 2):
        raise ValueError(f"a porta controlada deve ser de um qubit (forma {porta.shape})")
    k = len(controles) + 1
    bloco = np.eye(2**k, dtype=complex)
    bloco[-2:, -2:] = porta.full()  # atua só quando todos os controles valem 1
    if sparsa is None:
        sparsa = porta.formato == "esparso"
    return porta_em(_porta(bloco, sparsa), controles + [alvo], n_qubits)


def cnot(controle: int = 0, alvo: int = 1, n_qubits: int = 2, sparsa: bool = False) -> ObjQuantico:
    """Porta CNOT (X controlada).

    Examples
    --------
    >>> import qbasic as qb
    >>> qb.cnot().full().real
    array([[1., 0., 0., 0.],
           [0., 1., 0., 0.],
           [0., 0., 0., 1.],
           [0., 0., 1., 0.]])
    """
    return porta_controlada(pauliX(sparsa=sparsa), controle, alvo, n_qubits)


def cz(controle: int = 0, alvo: int = 1, n_qubits: int = 2, sparsa: bool = False) -> ObjQuantico:
    """Porta CZ (Z controlada): troca o sinal de :math:`|11\\rangle`."""
    return porta_controlada(pauliZ(sparsa=sparsa), controle, alvo, n_qubits)


def toffoli(
    controles: Sequence[int] = (0, 1), alvo: int = 2, n_qubits: int = 3, sparsa: bool = False
) -> ObjQuantico:
    """Porta de Toffoli (CCNOT): inverte o alvo quando os dois controles estão em
    :math:`|1\\rangle`."""
    return porta_controlada(pauliX(sparsa=sparsa), list(controles), alvo, n_qubits)


def swap(
    qubit_a: int = 0, qubit_b: int = 1, n_qubits: int = 2, sparsa: bool = False
) -> ObjQuantico:
    """Porta SWAP: troca os estados de dois qubits."""
    matriz = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    return porta_em(_porta(matriz, sparsa), [qubit_a, qubit_b], n_qubits)
