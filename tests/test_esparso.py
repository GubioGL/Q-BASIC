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
    "identidade": lambda s: qb.Identidade(N, sparsa=s),
    "destruicao": lambda s: qb.destruiçao(N, sparsa=s),
    "criacao": lambda s: qb.criaçao(N, sparsa=s),
    "posicao": lambda s: qb.operador_x(N, sparsa=s),
    "momento": lambda s: qb.operador_p(N, sparsa=s),
    "pauli_x": lambda s: qb.pauliX(sparsa=s),
    "pauli_y": lambda s: qb.pauliY(sparsa=s),
    "pauli_z": lambda s: qb.pauliZ(sparsa=s),
    "bases": lambda s: qb.bases(N, 2, sparsa=s),
    "fock": lambda s: qb.Fock(N, 1, sparsa=s),
    "ket": lambda s: qb.ket("1", sparsa=s),
    "bra": lambda s: qb.bra("0", sparsa=s),
    "coerente_operador": lambda s: qb.coerente(10, 0.6 + 0.2j, metodo="operador", sparsa=s),
    "coerente_analitico": lambda s: qb.coerente(10, 0.6 + 0.2j, metodo="analitico", sparsa=s),
    "densidade_pura": lambda s: qb.matrizdensidade(estados=qb.bases(3, 1), sparsa=s),
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
    "exponencial": lambda A, B: (-1j * 0.2 * (A + A.dag())).expM(),
}


def par(sparsa):
    """Dois operadores não comutantes do mesmo espaço."""
    return qb.destruiçao(N, sparsa=sparsa), qb.operador_x(N, sparsa=sparsa)


@pytest.mark.parametrize("nome", CONSTRUTORES)
def test_construtores_equivalentes(nome):
    denso, esparso = CONSTRUTORES[nome](False), CONSTRUTORES[nome](True)
    assert isinstance(denso, qb.ObjQuantico)
    assert isinstance(esparso, qb.ObjQuantico_esparso)
    np.testing.assert_allclose(densa(esparso), densa(denso), atol=ATOL)


@pytest.mark.parametrize("nome", OPERACOES)
def test_operacoes_equivalentes(nome):
    operacao = OPERACOES[nome]
    denso = operacao(*par(False))
    esparso = operacao(*par(True))
    assert isinstance(esparso, qb.ObjQuantico_esparso)
    np.testing.assert_allclose(densa(esparso), densa(denso), atol=ATOL)


def test_resultado_esparso_continua_esparso():
    A, B = par(True)
    assert sp.sparse.issparse((A * B).full_sparsa())


def test_traco_e_autovalores_equivalentes():
    (Ad, Bd), (As, Bs) = par(False), par(True)
    Hd, Hs = Ad.dag() * Ad + Bd, As.dag() * As + Bs
    assert Hs.traço() == pytest.approx(Hd.traço())
    np.testing.assert_allclose(
        np.sort(np.real(Hs.Autovalores())), np.sort(np.real(Hd.Autovalores())), atol=1e-9
    )


def test_hamiltoniano_de_jaynes_cummings():
    def hamiltoniano(sparsa):
        a = qb.destruiçao(N, sparsa=sparsa) @ qb.Identidade(2, sparsa=sparsa)
        sm = qb.Identidade(N, sparsa=sparsa) @ qb.destruiçao(2, sparsa=sparsa)
        return 2.0 * a.dag() * a + 1.5 * sm.dag() * sm + 0.1 * (a.dag() * sm + a * sm.dag())

    np.testing.assert_allclose(densa(hamiltoniano(True)), densa(hamiltoniano(False)), atol=ATOL)
