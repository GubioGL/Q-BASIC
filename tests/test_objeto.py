"""Testes das classes base ``ObjQuantico`` (densa) e ``ObjQuantico_esparso``."""

import numpy as np
import pytest
import scipy as sp

import qbasic as qb
from auxiliares import ATOL, densa

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2)
# Matriz hermitiana com autovalores 1 e 4.
H = np.array([[2, 1 - 1j], [1 + 1j, 3]])
# Matriz genérica (não hermitiana).
M = np.array([[1, 2], [3, 4]], dtype=complex)


def criar(matriz, sparsa):
    """Cria o objeto no formato pedido."""
    return qb.ObjQuantico_esparso(matriz) if sparsa else qb.ObjQuantico(matriz)


class TestConstrucao:
    def test_full_retorna_os_dados(self, sparsa):
        np.testing.assert_allclose(densa(criar(X, sparsa)), X)

    def test_tipo_do_objeto(self, sparsa):
        esperado = qb.ObjQuantico_esparso if sparsa else qb.ObjQuantico
        assert type(criar(X, sparsa)) is esperado

    def test_full_sparsa_mantem_formato_esparso(self):
        A = qb.ObjQuantico_esparso(X)
        assert sp.sparse.issparse(A.full_sparsa())

    def test_definir_dados(self):
        A = qb.ObjQuantico(X)
        A.definir_dados(Z)
        np.testing.assert_allclose(A.full(), Z)

    def test_dim_de_operador(self, sparsa):
        assert criar(np.eye(3), sparsa).dim() == 3

    def test_dim_de_ket(self, sparsa):
        assert qb.bases(5, 0, sparsa=sparsa).dim() == 5

    def test_representacao_latex_guardada(self, sparsa):
        A = qb.ObjQuantico_esparso(X, r"\sigma_x") if sparsa else qb.ObjQuantico(X, r"\sigma_x")
        assert A.latex_representation == r"\sigma_x"

    def test_transposta(self):
        np.testing.assert_allclose(qb.ObjQuantico(M).T, M.T)


class TestAritmetica:
    def test_soma(self, sparsa):
        np.testing.assert_allclose(densa(criar(X, sparsa) + criar(Z, sparsa)), X + Z)

    def test_subtracao(self, sparsa):
        np.testing.assert_allclose(densa(criar(X, sparsa) - criar(Z, sparsa)), X - Z)

    def test_subtracao_com_array_numpy(self):
        np.testing.assert_allclose(densa(qb.ObjQuantico(X) - I2), X - I2)

    @pytest.mark.parametrize("c", [2, -0.5, 1j, 2 - 3j, np.float64(1.5), np.complex128(1j)])
    def test_produto_por_escalar(self, sparsa, c):
        A = criar(M, sparsa)
        np.testing.assert_allclose(densa(c * A), c * M)
        np.testing.assert_allclose(densa(A * c), c * M)

    @pytest.mark.parametrize("c", [2, 0.5, -4.0])
    def test_divisao_por_escalar_real(self, sparsa, c):
        np.testing.assert_allclose(densa(criar(M, sparsa) / c), M / c)

    def test_produto_matricial(self, sparsa):
        # Álgebra de Pauli: XY = iZ.
        np.testing.assert_allclose(densa(criar(X, sparsa) * criar(Y, sparsa)), 1j * Z)
        np.testing.assert_allclose(densa(criar(M, sparsa) * criar(H, sparsa)), M @ H)

    def test_produto_operador_vetor(self, sparsa):
        ket0 = qb.bases(2, 0, sparsa=sparsa)
        np.testing.assert_allclose(densa(criar(X, sparsa) * ket0), [[0], [1]])

    def test_produto_tensorial_de_operadores(self, sparsa):
        resultado = criar(X, sparsa) @ criar(Z, sparsa)
        assert densa(resultado).shape == (4, 4)
        np.testing.assert_allclose(densa(resultado), np.kron(X, Z))

    def test_produto_tensorial_de_estados(self, sparsa):
        psi = qb.bases(2, 0, sparsa=sparsa) @ qb.bases(3, 1, sparsa=sparsa)
        esperado = np.zeros((6, 1))
        esperado[1, 0] = 1
        np.testing.assert_allclose(densa(psi), esperado)

    @pytest.mark.parametrize("n", [0, 1, 2, 3, 5])
    def test_potencia(self, sparsa, n):
        np.testing.assert_allclose(densa(criar(M, sparsa) ** n), np.linalg.matrix_power(M, n))

    def test_quadrado_de_pauli_e_identidade(self, sparsa):
        np.testing.assert_allclose(densa(criar(X, sparsa) ** 2), I2)

    @pytest.mark.parametrize("n", [-1, 1.5])
    def test_potencia_invalida(self, sparsa, n):
        with pytest.raises(ValueError, match="potência"):
            criar(M, sparsa) ** n


class TestAlgebraLinear:
    def test_adjunto(self, sparsa):
        np.testing.assert_allclose(densa(criar(M * 1j, sparsa).dag()), (M * 1j).conj().T)

    def test_adjunto_duas_vezes_volta_ao_original(self, sparsa):
        A = criar(M + 1j * H, sparsa)
        np.testing.assert_allclose(densa(A.dag().dag()), M + 1j * H)

    def test_adjunto_de_ket_e_bra(self, sparsa):
        ket = qb.bases(3, 1, sparsa=sparsa)
        np.testing.assert_allclose(densa(ket.dag()), [[0, 1, 0]])

    def test_traco(self, sparsa):
        assert criar(H, sparsa).traço() == pytest.approx(5.0)
        assert criar(X, sparsa).traço() == pytest.approx(0.0)

    def test_autovalores_de_hermitiana(self, sparsa):
        autovalores = np.sort(np.real(criar(H, sparsa).Autovalores()))
        np.testing.assert_allclose(autovalores, [1.0, 4.0], atol=ATOL)

    def test_autovetores_satisfazem_a_equacao(self, sparsa):
        vetores = np.asarray(criar(H, sparsa).Autovetores())
        for k in range(vetores.shape[1]):
            v = vetores[:, k]
            autovalor = (v.conj() @ H @ v) / (v.conj() @ v)
            np.testing.assert_allclose(H @ v, autovalor * v, atol=ATOL)

    def test_autovalor_vetor_esparso_retorna_valores_e_vetores(self):
        # A versão densa ainda não faz isso (bug B3).
        autovalores, autovetores = qb.ObjQuantico_esparso(H).AutoValor_Vetor()
        for k, autovalor in enumerate(autovalores):
            np.testing.assert_allclose(H @ autovetores[:, k], autovalor * autovetores[:, k])

    def test_exponencial_de_pauli(self, sparsa):
        # exp(-i θ X) = cos(θ) I - i sen(θ) X
        theta = 0.3
        U = criar(-1j * theta * X, sparsa).expM()
        esperado = np.cos(theta) * I2 - 1j * np.sin(theta) * X
        np.testing.assert_allclose(densa(U), esperado, atol=ATOL)

    def test_exponencial_da_matriz_nula_e_identidade(self, sparsa):
        np.testing.assert_allclose(densa(criar(np.zeros((3, 3)), sparsa).expM()), np.eye(3))

    def test_exponencial_e_unitaria(self, sparsa):
        U = densa(criar(-1j * 0.7 * H, sparsa).expM())
        np.testing.assert_allclose(U.conj().T @ U, I2, atol=ATOL)


class TestErros:
    """Operações com tipos não suportados devem gerar TypeError."""

    @pytest.mark.parametrize(
        "operacao",
        [
            lambda A: A + [1],
            lambda A: A - [1],
            lambda A: A * [1],
            lambda A: [1] * A,
            lambda A: A / [1],
            lambda A: [1] / A,
            lambda A: A @ [1],
        ],
        ids=[
            "soma",
            "subtracao",
            "produto",
            "produto_reverso",
            "divisao",
            "divisao_reversa",
            "tensor",
        ],
    )
    def test_tipo_nao_suportado(self, sparsa, operacao):
        with pytest.raises(TypeError):
            operacao(criar(X, sparsa))


class TestRepresentacao:
    def test_repr_sem_latex(self, sparsa):
        texto = repr(criar(M, sparsa))
        assert "ObjQuantico" in texto
        assert "(2, 2)" in texto

    def test_repr_com_latex(self):
        texto = repr(qb.pauliX())
        assert "ObjQuantico" in texto

    def test_repr_esparso_com_latex(self):
        assert "ObjQuantico" in repr(qb.pauliX(sparsa=True))
