"""Testes dos estados quânticos: bases, ket/bra, Fock e estado coerente."""

import numpy as np
import pytest
from scipy.special import factorial

import qbasic as qb
from auxiliares import densa, escalar

# Dimensão grande o bastante para que o truncamento do estado coerente seja desprezível.
N_COERENTE = 40
ALFAS = [0.5, 1.0, 1 + 1j, -0.7j]


class TestBases:
    @pytest.mark.parametrize(("N", "n"), [(2, 0), (2, 1), (5, 3), (10, 9)])
    def test_vetor_coluna_com_um_na_posicao_n(self, sparsa, N, n):
        psi = densa(qb.bases(N, n, sparsa=sparsa))
        esperado = np.zeros((N, 1))
        esperado[n, 0] = 1
        assert psi.shape == (N, 1)
        np.testing.assert_allclose(psi, esperado)

    def test_tipo_complexo(self):
        assert np.iscomplexobj(qb.bases(3, 0).full())

    def test_base_ortonormal(self, sparsa):
        N = 4
        for m in range(N):
            for n in range(N):
                bra_m = qb.bases(N, m, sparsa=sparsa).dag()
                produto = escalar(bra_m * qb.bases(N, n, sparsa=sparsa))
                assert produto == pytest.approx(1.0 if m == n else 0.0)

    @pytest.mark.parametrize(("N", "n"), [(0, 0), (-1, 0), (3, -1)])
    def test_entradas_invalidas(self, sparsa, N, n):
        with pytest.raises(ValueError, match="N deve ser"):
            qb.bases(N, n, sparsa=sparsa)


class TestKetBra:
    @pytest.mark.parametrize(("entrada", "indice"), [("0", 0), ("1", 1), (0, 0), (1, 1)])
    def test_ket(self, sparsa, entrada, indice):
        np.testing.assert_allclose(
            densa(qb.ket(entrada, sparsa=sparsa)), densa(qb.bases(2, indice))
        )

    @pytest.mark.parametrize(("entrada", "esperado"), [("0", [[1, 0]]), ("1", [[0, 1]])])
    def test_bra_e_vetor_linha(self, sparsa, entrada, esperado):
        np.testing.assert_allclose(densa(qb.bra(entrada, sparsa=sparsa)), esperado)

    @pytest.mark.parametrize("entrada", ["0", "1"])
    def test_bra_e_adjunto_do_ket(self, sparsa, entrada):
        np.testing.assert_allclose(
            densa(qb.bra(entrada, sparsa=sparsa)), densa(qb.ket(entrada, sparsa=sparsa).dag())
        )

    def test_produto_interno(self, sparsa):
        assert escalar(qb.bra("0", sparsa=sparsa) * qb.ket("0", sparsa=sparsa)) == 1
        assert escalar(qb.bra("0", sparsa=sparsa) * qb.ket("1", sparsa=sparsa)) == 0

    def test_representacao_latex(self, sparsa):
        # Hoje sai "\ket0" (sem chaves: bug B20); o teste só exige o essencial.
        latex_ket = qb.ket("0", sparsa=sparsa).latex_representation
        latex_bra = qb.bra("1", sparsa=sparsa).latex_representation
        assert r"\ket" in latex_ket
        assert "0" in latex_ket
        assert r"\bra" in latex_bra
        assert "1" in latex_bra


class TestFock:
    @pytest.mark.parametrize("n", [0, 2, 4])
    def test_igual_a_bases(self, sparsa, n):
        np.testing.assert_allclose(densa(qb.Fock(5, n, sparsa=sparsa)), densa(qb.bases(5, n)))

    def test_padrao_e_o_vacuo(self):
        np.testing.assert_allclose(densa(qb.Fock(4)), densa(qb.bases(4, 0)))


class TestCoerente:
    @pytest.mark.parametrize("metodo", ["operador", "analitico"])
    @pytest.mark.parametrize("alpha", ALFAS)
    def test_normalizado(self, sparsa, metodo, alpha):
        psi = densa(qb.coerente(N_COERENTE, alpha, metodo=metodo, sparsa=sparsa))
        assert np.linalg.norm(psi) == pytest.approx(1.0, abs=1e-10)

    @pytest.mark.parametrize("alpha", ALFAS)
    def test_distribuicao_de_poisson(self, alpha):
        # |<n|alpha>|^2 = exp(-|alpha|^2) |alpha|^(2n) / n!
        n = np.arange(N_COERENTE)
        probabilidades = np.abs(densa(qb.coerente(N_COERENTE, alpha)).ravel()) ** 2
        poisson = np.exp(-(abs(alpha) ** 2)) * abs(alpha) ** (2 * n) / factorial(n)
        np.testing.assert_allclose(probabilidades, poisson, atol=1e-12)

    @pytest.mark.parametrize("alpha", ALFAS)
    def test_numero_medio_de_fotons(self, sparsa, alpha):
        psi = qb.coerente(N_COERENTE, alpha, sparsa=sparsa)
        a = qb.destruiçao(N_COERENTE, sparsa=sparsa)
        numero_medio = escalar(psi.dag() * (a.dag() * a) * psi)
        assert numero_medio == pytest.approx(abs(alpha) ** 2, abs=1e-10)

    @pytest.mark.parametrize("alpha", ALFAS)
    def test_autoestado_do_operador_destruicao(self, alpha):
        # a|alpha> = alpha|alpha> (a menos do truncamento, desprezível aqui).
        psi = qb.coerente(N_COERENTE, alpha)
        a = qb.destruiçao(N_COERENTE)
        np.testing.assert_allclose(densa(a * psi), alpha * densa(psi), atol=1e-10)

    @pytest.mark.parametrize("alpha", ALFAS)
    def test_metodo_operador_igual_ao_analitico(self, sparsa, alpha):
        por_operador = densa(qb.coerente(N_COERENTE, alpha, metodo="operador", sparsa=sparsa))
        analitico = densa(qb.coerente(N_COERENTE, alpha, metodo="analitico", sparsa=sparsa))
        np.testing.assert_allclose(por_operador, analitico, atol=1e-10)

    @pytest.mark.parametrize("metodo", ["operador", "analitico"])
    def test_alpha_zero_e_o_vacuo(self, metodo):
        np.testing.assert_allclose(
            densa(qb.coerente(5, 0, metodo=metodo)), densa(qb.bases(5, 0)), atol=1e-12
        )

    def test_metodo_invalido(self):
        with pytest.raises(TypeError, match="operador"):
            qb.coerente(5, 1.0, metodo="outro")
