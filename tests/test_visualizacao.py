"""Testes da visualização: LaTeX, função de Wigner e gráficos."""

import warnings

import numpy as np
import pytest
from scipy.linalg import expm

import qbasic as qb
from qbasic.visualizacao import formatar_numero

X = np.linspace(-5, 5, 201)


def wigner_por_paridade(rho, x, p, n_grande=60):
    """Definição W = (1/pi) Tr[rho D(alpha) Pi D(alpha)^dagger], com alpha = (x + ip)/sqrt(2)."""
    n = rho.shape[0]
    R = np.zeros((n_grande, n_grande), dtype=complex)
    R[:n, :n] = rho
    a = np.diag(np.sqrt(np.arange(1, n_grande)), 1)
    paridade = np.diag((-1.0) ** np.arange(n_grande))
    alpha = (x + 1j * p) / np.sqrt(2)
    D = expm(alpha * a.conj().T - np.conj(alpha) * a)
    return float(np.real(np.trace(R @ D @ paridade @ D.conj().T)) / np.pi)


class TestWigner:
    def test_vacuo(self):
        W = qb.wigner(qb.fock(10, 0), X, X)
        XX, PP = np.meshgrid(X, X)
        np.testing.assert_allclose(W, np.exp(-(XX**2) - PP**2) / np.pi, atol=1e-12)

    @pytest.mark.parametrize(
        "estado",
        [qb.fock(12, 3), qb.coerente(20, 1.5 - 0.5j), (qb.fock(8, 0) + qb.fock(8, 4)) / np.sqrt(2)],
        ids=["fock3", "coerente", "gato"],
    )
    def test_normalizacao(self, estado):
        grade = np.linspace(-7, 7, 281)  # larga o bastante para conter as caudas
        W = qb.wigner(estado, grade, grade)
        assert W.sum() * (grade[1] - grade[0]) ** 2 == pytest.approx(1.0, abs=1e-6)

    def test_fock_um_e_negativo_na_origem(self):
        W = qb.wigner(qb.fock(4, 1), [0.0], [0.0])
        assert W[0, 0] == pytest.approx(-1 / np.pi)

    def test_coerente_e_gaussiana_deslocada(self):
        alpha = 1.2 + 0.7j
        x0, p0 = np.sqrt(2) * alpha.real, np.sqrt(2) * alpha.imag
        W = qb.wigner(qb.coerente(30, alpha), X, X)
        XX, PP = np.meshgrid(X, X)
        np.testing.assert_allclose(W, np.exp(-((XX - x0) ** 2) - (PP - p0) ** 2) / np.pi, atol=1e-9)

    def test_igual_a_definicao_por_paridade(self, sparsa):
        rng = np.random.default_rng(0)
        M = rng.normal(size=(5, 5)) + 1j * rng.normal(size=(5, 5))
        rho = M @ M.conj().T
        rho /= np.trace(rho)
        estado = qb.ObjQuantico(rho, formato="esparso" if sparsa else "denso")
        pontos = [(0.3, -0.2), (-1.1, 0.8), (1.6, 1.0)]
        for x, p in pontos:
            assert qb.wigner(estado, [x], [p])[0, 0] == pytest.approx(
                wigner_por_paridade(rho, x, p), abs=1e-10
            )

    def test_exige_um_unico_modo(self):
        with pytest.raises(ValueError, match="único modo"):
            qb.wigner(qb.bell(), X, X)


def test_formatar_numero():
    assert formatar_numero(1) == "1"
    assert formatar_numero(0) == "0"
    assert formatar_numero(-1j) == "-i"
    assert formatar_numero(1j) == "i"
    assert formatar_numero(0.5 - 2j) == "0.5 - 2i"
    assert formatar_numero(1e-20 + 1e-20j) == "0"


class TestGraficos:
    @pytest.fixture(autouse=True)
    def _matplotlib(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            matplotlib = pytest.importorskip("matplotlib")
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        yield plt
        plt.close("all")

    def test_plotar_wigner(self):
        ax = qb.plotar_wigner(qb.fock(6, 2), x=np.linspace(-3, 3, 41), p=np.linspace(-3, 3, 41))
        assert ax.get_xlabel() == "x"
        assert ax.get_ylabel() == "p"

    def test_plotar_fock(self):
        ax = qb.plotar_fock(qb.coerente(15, 2.0))
        assert len(ax.patches) == 15

    def test_plotar_valores_esperados(self):
        resultado = qb.resolver_schrodinger(
            qb.pauliX(), qb.ket("0"), np.linspace(0, 3, 10), [qb.pauliZ(), qb.pauliY()]
        )
        ax = qb.plotar_valores_esperados(resultado, ["Z", "Y"])
        assert len(ax.lines) == 2
        assert [t.get_text() for t in ax.get_legend().get_texts()] == ["Z", "Y"]
        with pytest.raises(ValueError, match="valores esperados"):
            qb.plotar_valores_esperados(qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), [0, 1]))

    def test_esfera_bloch(self):
        ax = qb.esfera_bloch([qb.ket("0"), (qb.ket("0") + qb.ket("1")) / np.sqrt(2)])
        assert ax.name == "3d"
        resultado = qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), np.linspace(0, 2, 20))
        vetores = [qb.vetor_bloch(e) for e in resultado.estados]
        ax = qb.esfera_bloch(vetores, trajetoria=True)
        assert ax.name == "3d"
        assert qb.esfera_bloch().name == "3d"
