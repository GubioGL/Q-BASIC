"""Testes dos operadores: Pauli, criação/destruição, posição/momento e identidade."""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, comutador, densa

I2 = np.eye(2)
DIMENSOES = [2, 3, 5, 8]


def comutador_truncado(N):
    """Valor de [a, a†] num espaço de Fock truncado em N níveis.

    No espaço infinito, [a, a†] = I. Com N níveis, o último elemento da diagonal
    vale -(N-1): efeito conhecido do truncamento.
    """
    diagonal = np.ones(N)
    diagonal[-1] = -(N - 1)
    return np.diag(diagonal)


class TestPauli:
    def test_matrizes_explicitas(self, sparsa):
        np.testing.assert_allclose(densa(qb.pauliX(sparsa=sparsa)), [[0, 1], [1, 0]])
        np.testing.assert_allclose(densa(qb.pauliY(sparsa=sparsa)), [[0, -1j], [1j, 0]])
        np.testing.assert_allclose(densa(qb.pauliZ(sparsa=sparsa)), [[1, 0], [0, -1]])

    @pytest.mark.parametrize("pauli", [qb.pauliX, qb.pauliY, qb.pauliZ], ids=["X", "Y", "Z"])
    def test_quadrado_e_identidade(self, sparsa, pauli):
        sigma = pauli(sparsa=sparsa)
        np.testing.assert_allclose(densa(sigma * sigma), I2)

    def test_produtos_ciclicos(self, sparsa):
        X, Y, Z = (f(sparsa=sparsa) for f in (qb.pauliX, qb.pauliY, qb.pauliZ))
        np.testing.assert_allclose(densa(X * Y), 1j * densa(Z))
        np.testing.assert_allclose(densa(Y * Z), 1j * densa(X))
        np.testing.assert_allclose(densa(Z * X), 1j * densa(Y))

    def test_anticomutam(self, sparsa):
        X, Y, Z = (f(sparsa=sparsa) for f in (qb.pauliX, qb.pauliY, qb.pauliZ))
        for A, B in [(X, Y), (Y, Z), (Z, X)]:
            np.testing.assert_allclose(densa(A * B) + densa(B * A), np.zeros((2, 2)))

    @pytest.mark.parametrize("pauli", [qb.pauliX, qb.pauliY, qb.pauliZ], ids=["X", "Y", "Z"])
    def test_hermitiana_traco_nulo_e_autovalores(self, sparsa, pauli):
        sigma = pauli(sparsa=sparsa)
        np.testing.assert_allclose(densa(sigma.dag()), densa(sigma))
        assert sigma.traco() == pytest.approx(0.0)
        np.testing.assert_allclose(np.sort(np.real(sigma.autovalores())), [-1, 1], atol=ATOL)

    def test_representacao_latex(self, sparsa):
        assert qb.pauliX(sparsa=sparsa).latex_representation == r"$$ \hat{\sigma}_x $$"
        assert qb.pauliY(sparsa=sparsa).latex_representation == r"$$ \hat{\sigma}_y $$"
        assert qb.pauliZ(sparsa=sparsa).latex_representation == r"$$ \hat{\sigma}_z $$"


@pytest.mark.parametrize("N", DIMENSOES)
class TestCriacaoDestruicao:
    def test_destruicao_em_estados_de_fock(self, sparsa, N):
        a = qb.destruicao(N, sparsa=sparsa)
        np.testing.assert_allclose(densa(a * qb.bases(N, 0, sparsa=sparsa)), np.zeros((N, 1)))
        for n in range(1, N):
            esperado = np.sqrt(n) * densa(qb.bases(N, n - 1))
            np.testing.assert_allclose(densa(a * qb.bases(N, n, sparsa=sparsa)), esperado)

    def test_criacao_em_estados_de_fock(self, sparsa, N):
        a_dag = qb.criacao(N, sparsa=sparsa)
        for n in range(N - 1):
            esperado = np.sqrt(n + 1) * densa(qb.bases(N, n + 1))
            np.testing.assert_allclose(densa(a_dag * qb.bases(N, n, sparsa=sparsa)), esperado)
        # O último nível não pode subir: efeito do truncamento.
        ultimo = a_dag * qb.bases(N, N - 1, sparsa=sparsa)
        np.testing.assert_allclose(densa(ultimo), np.zeros((N, 1)))

    def test_criacao_e_adjunto_da_destruicao(self, sparsa, N):
        np.testing.assert_allclose(
            densa(qb.criacao(N, sparsa=sparsa)), densa(qb.destruicao(N, sparsa=sparsa).dag())
        )

    def test_operador_numero(self, sparsa, N):
        a = qb.destruicao(N, sparsa=sparsa)
        np.testing.assert_allclose(densa(a.dag() * a), np.diag(np.arange(N)), atol=ATOL)

    def test_comutador(self, sparsa, N):
        a = qb.destruicao(N, sparsa=sparsa)
        np.testing.assert_allclose(comutador(a, a.dag()), comutador_truncado(N), atol=ATOL)


@pytest.mark.parametrize("N", DIMENSOES)
class TestPosicaoMomento:
    def test_definicoes(self, sparsa, N):
        a = densa(qb.destruicao(N))
        np.testing.assert_allclose(
            densa(qb.operador_x(N, sparsa=sparsa)), (a + a.conj().T) / np.sqrt(2), atol=ATOL
        )
        np.testing.assert_allclose(
            densa(qb.operador_p(N, sparsa=sparsa)), -1j * (a - a.conj().T) / np.sqrt(2), atol=ATOL
        )

    def test_hermitianos(self, sparsa, N):
        for operador in (qb.operador_x(N, sparsa=sparsa), qb.operador_p(N, sparsa=sparsa)):
            np.testing.assert_allclose(densa(operador.dag()), densa(operador), atol=ATOL)

    def test_comutador_canonico(self, sparsa, N):
        # [x, p] = i (com o mesmo efeito de truncamento de [a, a†]).
        x, p = qb.operador_x(N, sparsa=sparsa), qb.operador_p(N, sparsa=sparsa)
        np.testing.assert_allclose(comutador(x, p), 1j * comutador_truncado(N), atol=ATOL)


@pytest.mark.parametrize("N", DIMENSOES)
class TestIdentidade:
    def test_dimensao_invalida(self, sparsa, N):
        for funcao in (qb.identidade, qb.destruicao, qb.criacao, qb.operador_x, qb.operador_p):
            with pytest.raises(ValueError, match="inteiro positivo"):
                funcao(-N, sparsa=sparsa)
            with pytest.raises(ValueError, match="inteiro positivo"):
                funcao(float(N), sparsa=sparsa)

    def test_matriz(self, sparsa, N):
        identidade = qb.identidade(N, sparsa=sparsa)
        np.testing.assert_allclose(densa(identidade), np.eye(N))
        assert identidade.traco() == pytest.approx(N)

    def test_elemento_neutro_do_produto(self, sparsa, N):
        identidade = qb.identidade(N, sparsa=sparsa)
        a = qb.destruicao(N, sparsa=sparsa)
        np.testing.assert_allclose(densa(identidade * a), densa(a))
        np.testing.assert_allclose(densa(a * identidade), densa(a))


class TestTensor:
    def test_igual_ao_operador_arroba(self, sparsa):
        a, b, c = (
            qb.pauliX(sparsa=sparsa),
            qb.ket("0", sparsa=sparsa),
            qb.destruicao(3, sparsa=sparsa),
        )
        np.testing.assert_allclose(densa(qb.tensor(a, c)), densa(a @ c))
        np.testing.assert_allclose(densa(qb.tensor([a, c, a])), densa(a @ c @ a))
        np.testing.assert_allclose(densa(qb.tensor(b)), densa(b))

    def test_dims(self):
        assert qb.tensor(qb.ket("0"), qb.ket("1"), qb.ket("1")).dims == [[2, 2, 2], [1, 1, 1]]
        assert qb.tensor(qb.destruicao(3), qb.identidade(2)).dims == [[3, 2], [3, 2]]

    def test_entradas_invalidas(self):
        with pytest.raises(ValueError, match="pelo menos um"):
            qb.tensor()
        with pytest.raises(TypeError, match="ObjQuantico"):
            qb.tensor(qb.ket("0"), np.eye(2))


def test_casos_de_um_nivel(sparsa):
    # N = 1: o único estado é o vácuo, e a = a† = 0.
    np.testing.assert_allclose(densa(qb.destruicao(1, sparsa=sparsa)), [[0]])
    np.testing.assert_allclose(densa(qb.identidade(1, sparsa=sparsa)), [[1]])
