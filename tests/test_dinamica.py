"""Testes da dinâmica (equação de Schrödinger) e dos valores esperados."""

import numpy as np
import pytest
from scipy.linalg import expm

import qbasic as qb
from auxiliares import densa

# Tolerâncias do integrador para comparações com soluções analíticas.
# (Com as tolerâncias padrão o resultado é impreciso: ver bug B14.)
PRECISO = {"rtol": 1e-10, "atol": 1e-12}


def rabi(omega=np.pi, tempos=None, **opcoes):
    """Qubit sob H = (omega/2) X, partindo de |0>."""
    tempos = np.linspace(0, 4, 81) if tempos is None else tempos
    H = (omega / 2) * qb.pauliX()
    return tempos, qb.edo.solve(H, tempos, qb.bases(2, 0), **opcoes)


class TestRabi:
    @pytest.mark.parametrize("metodo", ["RK45", "DOP853"])
    def test_oscilacao_de_rabi(self, metodo):
        # <Z>(t) = cos(omega t)
        omega = np.pi
        tempos, resultado = rabi(omega, method=metodo, **PRECISO)
        z = qb.Valor_esperado(resultado.y, [qb.pauliZ()])[0]
        np.testing.assert_allclose(z, np.cos(omega * tempos), atol=1e-7)

    def test_formato_do_resultado(self):
        tempos, resultado = rabi(**PRECISO)
        assert resultado.success
        assert resultado.y.shape == (2, len(tempos))
        np.testing.assert_allclose(resultado.t, tempos)

    def test_t_span_explicito(self):
        tempos, resultado = rabi(t_span=(0.0, 4.0), **PRECISO)
        assert resultado.success
        np.testing.assert_allclose(resultado.t, tempos)

    def test_conservacao_da_norma(self):
        _, resultado = rabi(**PRECISO)
        np.testing.assert_allclose(np.linalg.norm(resultado.y, axis=0), 1.0, atol=1e-8)

    def test_hamiltoniano_esparso_igual_ao_denso(self):
        tempos = np.linspace(0, 2, 21)
        denso = qb.edo.solve(qb.pauliX(), tempos, qb.bases(2, 0), **PRECISO)
        esparso = qb.edo.solve(
            qb.pauliX(sparsa=True), tempos, qb.bases(2, 0, sparsa=True), **PRECISO
        )
        np.testing.assert_allclose(esparso.y, denso.y, atol=1e-9)


class TestJaynesCummings:
    """Átomo de dois níveis (|1> excitado) acoplado a uma cavidade com N níveis."""

    N = 4
    omega = 2 * np.pi
    g = 0.1 * 2 * np.pi

    def operadores(self, dessintonia=0.0):
        a = qb.destruiçao(self.N) @ qb.Identidade(2)
        sm = qb.Identidade(self.N) @ qb.destruiçao(2)  # sigma-menos
        H = (
            self.omega * a.dag() * a
            + (self.omega + dessintonia) * sm.dag() * sm
            + self.g * (a.dag() * sm + a * sm.dag())
        )
        return a, sm, H

    def test_oscilacao_de_rabi_no_vacuo(self):
        # Em ressonância, partindo de |0 fótons, excitado>:
        # P_excitado = cos^2(g t) e <n> = sen^2(g t).
        a, sm, H = self.operadores()
        tempos = np.linspace(0, 10, 101)
        psi0 = qb.bases(self.N, 0) @ qb.bases(2, 1)
        resultado = qb.edo.solve(H, tempos, psi0, **PRECISO)
        n_fotons, p_excitado = qb.Valor_esperado(resultado.y, [a.dag() * a, sm.dag() * sm])
        np.testing.assert_allclose(p_excitado, np.cos(self.g * tempos) ** 2, atol=1e-7)
        np.testing.assert_allclose(n_fotons, np.sin(self.g * tempos) ** 2, atol=1e-7)

    def test_numero_de_excitacoes_conservado(self):
        a, sm, H = self.operadores(dessintonia=0.3)
        tempos = np.linspace(0, 10, 51)
        psi0 = qb.bases(self.N, 1) @ qb.bases(2, 1)  # 2 excitações
        resultado = qb.edo.solve(H, tempos, psi0, **PRECISO)
        excitacoes = qb.Valor_esperado(resultado.y, [a.dag() * a + sm.dag() * sm])[0]
        np.testing.assert_allclose(excitacoes, 2.0, atol=1e-8)

    def test_igual_a_exponencial_do_hamiltoniano(self):
        # |psi(t)> = exp(-i H t) |psi(0)>
        _, _, H = self.operadores(dessintonia=0.5)
        tempos = np.linspace(0, 3, 16)
        estado_a = qb.bases(self.N, 0) @ qb.bases(2, 1)
        estado_b = qb.bases(self.N, 2) @ qb.bases(2, 0)
        psi0 = (estado_a + estado_b) / np.sqrt(2)
        resultado = qb.edo.solve(H, tempos, psi0, method="DOP853", **PRECISO)
        Hm, v0 = densa(H), densa(psi0).ravel()
        for k, t in enumerate(tempos):
            np.testing.assert_allclose(resultado.y[:, k], expm(-1j * Hm * t) @ v0, atol=1e-8)


class TestValorEsperado:
    @pytest.mark.parametrize(
        ("estado", "observavel", "esperado"),
        [
            ([1, 0], [[1, 0], [0, -1]], 1.0),
            ([0, 1], [[1, 0], [0, -1]], -1.0),
            (np.array([1, 1]) / np.sqrt(2), [[0, 1], [1, 0]], 1.0),
            (np.array([1, 1j]) / np.sqrt(2), [[0, -1j], [1j, 0]], 1.0),
        ],
        ids=["z_em_0", "z_em_1", "x_em_mais", "y_em_mais_i"],
    )
    def test_valor_esperado_de_um_estado(self, estado, observavel, esperado):
        valor = qb.valor_esperado(np.asarray(estado, dtype=complex), np.asarray(observavel))
        assert valor == pytest.approx(esperado)

    def test_valor_esperado_ao_longo_do_tempo(self):
        estados = np.array([[1, 0, 1 / np.sqrt(2)], [0, 1, 1 / np.sqrt(2)]], dtype=complex)
        valores = qb.Valor_esperado(estados, [qb.pauliZ(), qb.pauliX()])
        assert len(valores) == 2
        assert len(valores[0]) == 3
        np.testing.assert_allclose(valores[0], [1, -1, 0], atol=1e-12)
        np.testing.assert_allclose(valores[1], [0, 0, 1], atol=1e-12)
