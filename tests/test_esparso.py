"""Equivalência entre os formatos denso e esparso.

Toda construção e operação deve dar o mesmo resultado numérico nos dois formatos.
"""

import numpy as np
import pytest
import scipy as sp

import qbasic as qb
from auxiliares import ATOL, densa

N = 4

CONSTRUTORES = {
    "identidade": lambda s: qb.identidade(N, sparsa=s),
    "destruicao": lambda s: qb.destruicao(N, sparsa=s),
    "criacao": lambda s: qb.criacao(N, sparsa=s),
    "posicao": lambda s: qb.operador_x(N, sparsa=s),
    "momento": lambda s: qb.operador_p(N, sparsa=s),
    "pauli_x": lambda s: qb.pauliX(sparsa=s),
    "pauli_y": lambda s: qb.pauliY(sparsa=s),
    "pauli_z": lambda s: qb.pauliZ(sparsa=s),
    "bases": lambda s: qb.bases(N, 2, sparsa=s),
    "fock": lambda s: qb.fock(N, 1, sparsa=s),
    "ket": lambda s: qb.ket("1", sparsa=s),
    "bra": lambda s: qb.bra("0", sparsa=s),
    "coerente_operador": lambda s: qb.coerente(10, 0.6 + 0.2j, metodo="operador", sparsa=s),
    "coerente_analitico": lambda s: qb.coerente(10, 0.6 + 0.2j, metodo="analitico", sparsa=s),
    "densidade_pura": lambda s: qb.matriz_densidade(qb.bases(3, 1), sparsa=s),
}

OPERACOES = {
    "soma": lambda A, B: A + B,
    "subtracao": lambda A, B: A - B,
    "produto": lambda A, B: A * B,
    "escalar_esquerda": lambda A, B: (2 - 1j) * A,
    "escalar_direita": lambda A, B: A * 0.5,
    "divisao": lambda A, B: A / 4,
    "tensorial": lambda A, B: A @ B,
    "adjunto": lambda A, B: A.dag(),
    "potencia": lambda A, B: A**3,
    "exponencial": lambda A, B: (-1j * 0.2 * (A + A.dag())).expm(),
}


def par(sparsa):
    """Dois operadores não comutantes do mesmo espaço."""
    return qb.destruicao(N, sparsa=sparsa), qb.operador_x(N, sparsa=sparsa)


@pytest.mark.parametrize("nome", CONSTRUTORES)
def test_construtores_equivalentes(nome):
    denso, esparso = CONSTRUTORES[nome](False), CONSTRUTORES[nome](True)
    assert denso.formato == "denso"
    assert esparso.formato == "esparso"
    np.testing.assert_allclose(densa(esparso), densa(denso), atol=ATOL)


@pytest.mark.parametrize("nome", OPERACOES)
def test_operacoes_equivalentes(nome):
    operacao = OPERACOES[nome]
    denso = operacao(*par(False))
    esparso = operacao(*par(True))
    assert esparso.formato == "esparso"
    np.testing.assert_allclose(densa(esparso), densa(denso), atol=ATOL)


def test_resultado_esparso_continua_esparso():
    A, B = par(True)
    assert sp.sparse.issparse((A * B).full_sparsa())


def test_traco_e_autovalores_equivalentes():
    (Ad, Bd), (As, Bs) = par(False), par(True)
    Hd, Hs = Ad.dag() * Ad + Bd, As.dag() * As + Bs
    assert Hs.traco() == pytest.approx(Hd.traco())
    np.testing.assert_allclose(
        np.sort(np.real(Hs.autovalores())), np.sort(np.real(Hd.autovalores())), atol=1e-9
    )


def test_hamiltoniano_de_jaynes_cummings():
    def hamiltoniano(sparsa):
        a = qb.destruicao(N, sparsa=sparsa) @ qb.identidade(2, sparsa=sparsa)
        sm = qb.identidade(N, sparsa=sparsa) @ qb.destruicao(2, sparsa=sparsa)
        return 2.0 * a.dag() * a + 1.5 * sm.dag() * sm + 0.1 * (a.dag() * sm + a * sm.dag())

    np.testing.assert_allclose(densa(hamiltoniano(True)), densa(hamiltoniano(False)), atol=ATOL)
