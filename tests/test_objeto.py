"""Testes da classe base ``ObjQuantico`` (formatos denso e esparso)."""

import numpy as np
import pytest
import scipy.sparse as sps

import qbasic as qb
from auxiliares import ATOL, criar, densa

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2)
# Matriz hermitiana com autovalores 1 e 4.
H = np.array([[2, 1 - 1j], [1 + 1j, 3]])
# Matriz genérica (não hermitiana) com autovalores complexos.
M = np.array([[1, 2], [3, 4]], dtype=complex)
R = np.array([[0, -1], [1, 0]], dtype=complex)  # rotação: autovalores ±i


class TestConstrucao:
    def test_full_retorna_matriz_densa(self, sparsa):
        matriz = criar(X, sparsa).full()
        assert isinstance(matriz, np.ndarray)
        np.testing.assert_allclose(matriz, X)

    def test_formato(self, sparsa):
        A = criar(X, sparsa)
        assert A.formato == ("esparso" if sparsa else "denso")
        assert isinstance(A, qb.ObjQuantico)

    def test_formato_inferido_de_matriz_esparsa(self):
        assert qb.ObjQuantico(sps.csr_array(X)).formato == "esparso"
        assert qb.ObjQuantico(X).formato == "denso"

    def test_dados_no_formato_certo(self, sparsa):
        A = criar(X, sparsa)
        if sparsa:
            assert isinstance(A.dados, sps.csr_array)
        else:
            assert isinstance(A.dados, np.ndarray)

    def test_full_sparsa_e_esparsa(self, sparsa):
        assert sps.issparse(criar(X, sparsa).full_sparsa())

    def test_conversao_de_formato(self, sparsa):
        A = criar(M, sparsa)
        assert A.para_denso().formato == "denso"
        assert A.para_esparso().formato == "esparso"
        np.testing.assert_allclose(densa(A.para_esparso()), M)
        np.testing.assert_allclose(densa(A.para_denso()), M)

    def test_copia_de_outro_objeto(self, sparsa):
        original = qb.ObjQuantico(X, r"\sigma_x", formato="esparso" if sparsa else "denso")
        copia = qb.ObjQuantico(original)
        assert copia.formato == original.formato
        assert copia.latex_representation == r"\sigma_x"
        assert copia.dims == original.dims

    def test_vetor_1d_vira_ket(self):
        psi = qb.ObjQuantico([1, 0, 0])
        assert psi.shape == (3, 1)
        assert psi.tipo == "ket"

    def test_escalar_vira_matriz_1x1(self):
        assert qb.ObjQuantico(2.5).shape == (1, 1)

    def test_definir_dados(self):
        A = qb.ObjQuantico(X)
        A.definir_dados(Z)
        np.testing.assert_allclose(A.full(), Z)
        A.dados = sps.csr_array(M)
        assert A.formato == "esparso"
        np.testing.assert_allclose(A.full(), M)

    @pytest.mark.parametrize(
        ("dados", "erro"),
        [("abc", TypeError), (np.zeros((2, 2, 2)), ValueError), ([None, 1], TypeError)],
        ids=["texto", "3d", "objeto"],
    )
    def test_dados_invalidos(self, dados, erro):
        with pytest.raises(erro):
            qb.ObjQuantico(dados)

    def test_formato_invalido(self):
        with pytest.raises(ValueError, match="formato"):
            qb.ObjQuantico(X, formato="cheio")

    def test_representacao_latex_guardada(self, sparsa):
        A = qb.ObjQuantico(X, r"\sigma_x", formato="esparso" if sparsa else "denso")
        assert A.latex_representation == r"\sigma_x"


class TestFormaETipo:
    def test_dim_de_operador_ket_e_bra(self, sparsa):
        assert criar(np.eye(3), sparsa).dim() == 3
        assert qb.bases(5, 0, sparsa=sparsa).dim() == 5
        assert qb.bases(5, 0, sparsa=sparsa).dag().dim() == 5

    @pytest.mark.parametrize(
        ("matriz", "tipo"),
        [
            (np.eye(2), "operador"),
            (np.ones((3, 1)), "ket"),
            (np.ones((1, 3)), "bra"),
            ([[1]], "escalar"),
        ],
    )
    def test_tipo(self, sparsa, matriz, tipo):
        assert criar(matriz, sparsa).tipo == tipo

    def test_shape(self, sparsa):
        assert criar(np.ones((2, 3)), sparsa).shape == (2, 3)

    def test_dims_padrao(self, sparsa):
        assert criar(np.eye(3), sparsa).dims == [[3], [3]]
        assert qb.bases(4, 0, sparsa=sparsa).dims == [[4], [1]]

    def test_dims_do_produto_tensorial(self, sparsa):
        a = qb.destruicao(3, sparsa=sparsa) @ qb.identidade(2, sparsa=sparsa)
        psi = qb.bases(3, 0, sparsa=sparsa) @ qb.bases(2, 1, sparsa=sparsa)
        assert a.dims == [[3, 2], [3, 2]]
        assert psi.dims == [[3, 2], [1, 1]]
        assert (a * psi).dims == [[3, 2], [1, 1]]
        assert psi.dag().dims == [[1, 1], [3, 2]]

    def test_dims_explicito_e_validado(self):
        assert qb.ObjQuantico(np.eye(4), dims=[[2, 2], [2, 2]]).dims == [[2, 2], [2, 2]]
        with pytest.raises(ValueError, match="dims"):
            qb.ObjQuantico(np.eye(4), dims=[[3], [4]])
        with pytest.raises(ValueError, match="dims"):
            qb.ObjQuantico(np.eye(4), dims=[4])


class TestAritmetica:
    def test_soma_e_subtracao(self, sparsa):
        np.testing.assert_allclose(densa(criar(X, sparsa) + criar(Z, sparsa)), X + Z)
        np.testing.assert_allclose(densa(criar(X, sparsa) - criar(Z, sparsa)), X - Z)

    def test_formato_do_resultado(self):
        d, e = qb.ObjQuantico(X), qb.ObjQuantico(X, formato="esparso")
        assert (e + e).formato == "esparso"
        assert (e * e).formato == "esparso"
        assert (d + e).formato == "denso"
        assert (e * d).formato == "denso"

    def test_mistura_denso_esparso(self, sparsa):
        outro = not sparsa
        np.testing.assert_allclose(densa(criar(X, sparsa) * criar(Y, outro)), X @ Y)
        np.testing.assert_allclose(densa(criar(X, sparsa) + criar(Y, outro)), X + Y)
        np.testing.assert_allclose(densa(criar(X, sparsa) - criar(Y, outro)), X - Y)
        np.testing.assert_allclose(densa(criar(X, sparsa) @ criar(Y, outro)), np.kron(X, Y))

    def test_operacoes_com_array_numpy(self, sparsa):
        A = criar(X, sparsa)
        np.testing.assert_allclose(densa(A - I2), X - I2)
        np.testing.assert_allclose(densa(I2 - A), I2 - X)
        np.testing.assert_allclose(densa(I2 + A), I2 + X)
        np.testing.assert_allclose(densa(A * M), X @ M)
        np.testing.assert_allclose(densa(M * A), M @ X)

    def test_escalar_soma_multiplo_da_identidade(self, sparsa):
        A = criar(X, sparsa)
        np.testing.assert_allclose(densa(A + 2), X + 2 * I2)
        np.testing.assert_allclose(densa(2 + A), X + 2 * I2)
        np.testing.assert_allclose(densa(A - 1j), X - 1j * I2)
        np.testing.assert_allclose(densa(1 - A), I2 - X)

    def test_negacao(self, sparsa):
        np.testing.assert_allclose(densa(-criar(X, sparsa)), -X)
        np.testing.assert_allclose(densa(+criar(X, sparsa)), X)

    @pytest.mark.parametrize("c", [2, -0.5, 1j, 2 - 3j, np.float64(1.5), np.complex128(1j)])
    def test_produto_por_escalar(self, sparsa, c):
        A = criar(M, sparsa)
        np.testing.assert_allclose(densa(c * A), c * M)
        np.testing.assert_allclose(densa(A * c), c * M)

    @pytest.mark.parametrize("c", [2, 0.5, -4.0, 1j, np.complex128(2 - 1j), np.float32(2)])
    def test_divisao_por_escalar(self, sparsa, c):
        np.testing.assert_allclose(densa(criar(M, sparsa) / c), M / c, rtol=1e-6)

    def test_divisao_por_zero(self, sparsa):
        with pytest.raises(ZeroDivisionError):
            criar(M, sparsa) / 0

    def test_escalar_dividido_por_operador_e_erro(self, sparsa):
        with pytest.raises(TypeError, match="inversa"):
            2 / criar(M, sparsa)

    def test_produto_matricial(self, sparsa):
        np.testing.assert_allclose(densa(criar(X, sparsa) * criar(Y, sparsa)), 1j * Z)
        np.testing.assert_allclose(densa(criar(M, sparsa) * criar(H, sparsa)), M @ H)

    def test_produto_operador_vetor(self, sparsa):
        ket0 = qb.bases(2, 0, sparsa=sparsa)
        np.testing.assert_allclose(densa(criar(X, sparsa) * ket0), [[0], [1]])

    def test_produto_tensorial(self, sparsa):
        resultado = criar(X, sparsa) @ criar(Z, sparsa)
        np.testing.assert_allclose(densa(resultado), np.kron(X, Z))
        psi = qb.bases(2, 0, sparsa=sparsa) @ qb.bases(3, 1, sparsa=sparsa)
        esperado = np.zeros((6, 1))
        esperado[1, 0] = 1
        np.testing.assert_allclose(densa(psi), esperado)

    @pytest.mark.parametrize("n", [0, 1, 2, 3, 5, np.int64(4)])
    def test_potencia(self, sparsa, n):
        np.testing.assert_allclose(densa(criar(M, sparsa) ** n), np.linalg.matrix_power(M, int(n)))

    @pytest.mark.parametrize("n", [-1, 1.5, True])
    def test_potencia_invalida(self, sparsa, n):
        with pytest.raises(ValueError, match="potência"):
            criar(M, sparsa) ** n

    @pytest.mark.parametrize(
        "operacao",
        [
            lambda A, B: A + B,
            lambda A, B: A - B,
            lambda A, B: A * B,
        ],
        ids=["soma", "subtracao", "produto"],
    )
    def test_formas_incompativeis(self, sparsa, operacao):
        with pytest.raises(ValueError, match="incompatíveis"):
            operacao(criar(np.eye(2), sparsa), criar(np.eye(3), sparsa))

    def test_escalar_exige_operador_quadrado(self, sparsa):
        with pytest.raises(ValueError, match="quadrado"):
            criar(np.ones((2, 3)), sparsa) + 1


class TestAlgebraLinear:
    def test_adjunto(self, sparsa):
        np.testing.assert_allclose(densa(criar(M * 1j, sparsa).dag()), (M * 1j).conj().T)
        A = criar(M + 1j * H, sparsa)
        np.testing.assert_allclose(densa(A.dag().dag()), M + 1j * H)

    def test_adjunto_de_ket_e_bra(self, sparsa):
        ket = qb.bases(3, 1, sparsa=sparsa)
        np.testing.assert_allclose(densa(ket.dag()), [[0, 1, 0]])
        assert ket.dag().tipo == "bra"

    def test_conjugado_e_transposta(self, sparsa):
        A = criar(M * 1j, sparsa)
        np.testing.assert_allclose(densa(A.conj()), (M * 1j).conj())
        np.testing.assert_allclose(densa(A.transposta()), (M * 1j).T)
        np.testing.assert_allclose(qb.ObjQuantico(M).T, M.T)

    def test_traco(self, sparsa):
        assert criar(H, sparsa).traco() == pytest.approx(5.0)
        assert isinstance(criar(H, sparsa).traco(), float)
        assert criar(np.diag([1j, 1]), sparsa).traco() == pytest.approx(1 + 1j)

    def test_hermitiano(self, sparsa):
        assert criar(H, sparsa).eh_hermitiano()
        assert not criar(M, sparsa).eh_hermitiano()
        assert not criar(np.ones((2, 3)), sparsa).eh_hermitiano()

    def test_autovalores_de_hermitiana_sao_reais_e_crescentes(self, sparsa):
        autovalores = criar(H, sparsa).autovalores()
        assert np.isrealobj(autovalores)
        np.testing.assert_allclose(autovalores, [1.0, 4.0], atol=ATOL)

    def test_autovalores_complexos(self, sparsa):
        np.testing.assert_allclose(criar(R, sparsa).autovalores(), [-1j, 1j], atol=ATOL)

    @pytest.mark.parametrize("matriz", [H, M, R], ids=["hermitiana", "generica", "rotacao"])
    def test_autoestados_satisfazem_a_equacao(self, sparsa, matriz):
        valores, vetores = criar(matriz, sparsa).autoestados()
        np.testing.assert_allclose(valores, criar(matriz, sparsa).autovalores(), atol=ATOL)
        for k, valor in enumerate(valores):
            np.testing.assert_allclose(matriz @ vetores[:, k], valor * vetores[:, k], atol=ATOL)
        np.testing.assert_allclose(criar(matriz, sparsa).autovetores(), vetores)

    def test_k_menores_autovalores_no_formato_esparso(self):
        x = qb.operador_x(40, sparsa=True)
        todos = qb.operador_x(40).autovalores()
        np.testing.assert_allclose(x.autovalores(k=3), todos[:3], atol=1e-8)
        valores, vetores = x.autoestados(k=2)
        assert vetores.shape == (40, 2)
        np.testing.assert_allclose(valores, todos[:2], atol=1e-8)

    def test_k_autovalores_de_operador_nao_hermitiano_esparso(self):
        # x + 0,1i·I não é hermitiano: autovalores x_k + 0,1i (os de menor parte real).
        A = qb.operador_x(30, sparsa=True) + 0.1j
        esperado = qb.operador_x(30).autovalores()[:3] + 0.1j
        np.testing.assert_allclose(A.autovalores(k=3), esperado, atol=1e-8)

    def test_exponencial_de_pauli(self, sparsa):
        # exp(-i θ X) = cos(θ) I - i sen(θ) X
        theta = 0.3
        U = criar(-1j * theta * X, sparsa).expm()
        assert U.formato == ("esparso" if sparsa else "denso")
        esperado = np.cos(theta) * I2 - 1j * np.sin(theta) * X
        np.testing.assert_allclose(densa(U), esperado, atol=ATOL)

    def test_exponencial_da_matriz_nula_e_unitaria(self, sparsa):
        np.testing.assert_allclose(densa(criar(np.zeros((3, 3)), sparsa).expm()), np.eye(3))
        U = densa(criar(-1j * 0.7 * H, sparsa).expm())
        np.testing.assert_allclose(U.conj().T @ U, I2, atol=ATOL)

    def test_operacoes_exigem_operador_quadrado(self, sparsa):
        retangular = criar(np.ones((2, 3)), sparsa)
        for operacao in (retangular.expm, retangular.autovalores, lambda: retangular**2):
            with pytest.raises(ValueError, match="quadrado"):
                operacao()

    def test_norma_e_normalizacao(self, sparsa):
        psi = criar(np.array([[3.0], [4.0]]), sparsa)
        assert psi.norma() == pytest.approx(5.0)
        assert psi.normalizar().norma() == pytest.approx(1.0)
        rho = criar(np.diag([2.0, 2.0]), sparsa)
        assert rho.norma() == pytest.approx(4.0)  # norma do traço
        assert rho.normalizar().traco() == pytest.approx(1.0)
        with pytest.raises(ZeroDivisionError):
            criar(np.zeros((2, 1)), sparsa).normalizar()


class TestInteroperabilidadeNumpy:
    def test_numpy_asarray(self, sparsa):
        np.testing.assert_allclose(np.asarray(criar(M, sparsa)), M)
        assert np.asarray(criar(M, sparsa), dtype=complex).dtype == complex

    def test_indexacao(self, sparsa):
        A = criar(M, sparsa)
        assert A[1, 0] == 3
        np.testing.assert_allclose(np.ravel(A[0:1, :]), M[0])

    def test_escalares_numpy_a_esquerda(self, sparsa):
        resultado = np.float64(2.0) * criar(X, sparsa)
        assert isinstance(resultado, qb.ObjQuantico)
        np.testing.assert_allclose(densa(resultado), 2 * X)


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
            lambda A: np.eye(2) @ A,
        ],
        ids=[
            "soma",
            "subtracao",
            "produto",
            "produto_reverso",
            "divisao",
            "divisao_reversa",
            "tensor",
            "tensor_reverso",
        ],
    )
    def test_tipo_nao_suportado(self, sparsa, operacao):
        with pytest.raises(TypeError):
            operacao(criar(X, sparsa))


class TestRepresentacao:
    def test_repr_em_texto(self, sparsa):
        texto = repr(criar(M, sparsa))
        assert "ObjQuantico" in texto
        assert "(2, 2)" in texto
        assert ("esparso" if sparsa else "denso") in texto
        assert "4" in texto  # mostra os elementos

    def test_repr_nao_imprime_nada(self, sparsa, capsys):
        repr(criar(M, sparsa))
        str(criar(M, sparsa))
        assert capsys.readouterr().out == ""

    def test_repr_mostra_dims_compostos(self):
        assert "dims=[[2, 2], [1, 1]]" in repr(qb.ket("01"))

    def test_repr_de_esparsa_grande_e_resumido(self):
        texto = repr(qb.identidade(200, sparsa=True))
        assert "nnz=200" in texto
        assert len(texto.splitlines()) == 1

    def test_latex_com_simbolo(self):
        assert qb.pauliX()._repr_latex_() == r"$$ \hat{\sigma}_x $$"
        assert qb.ObjQuantico(X, r"\sigma")._repr_latex_() == r"$$ \sigma $$"

    def test_latex_da_matriz(self, sparsa):
        latex = criar(np.array([[1, 0.5j], [-1j, 0.70710678]]), sparsa)._repr_latex_()
        assert latex.startswith("$$ \\begin{pmatrix}")
        assert r"0.5i \\ -i & 0.7071" in latex

    def test_latex_de_matriz_grande_e_resumido(self, sparsa):
        latex = qb.identidade(50, sparsa=sparsa)._repr_latex_()
        assert r"\cdots" in latex
        assert r"\vdots" in latex
        assert r"\ddots" in latex

    def test_latex_do_adjunto(self):
        assert qb.ket("01").dag().latex_representation == r"$$ \bra{01} $$"
        assert qb.bra("1").dag().latex_representation == r"$$ \ket{1} $$"
        assert (
            qb.pauliY().dag().latex_representation == r"$$ \left(\hat{\sigma}_y\right)^\dagger $$"
        )
        assert qb.ObjQuantico(X).dag().latex_representation is None
