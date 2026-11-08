"""Testes das medidas: probabilidades, amostragem, traço parcial, pureza, entropia,
fidelidade e vetor de Bloch."""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, densa

MAIS = (qb.ket("0") + qb.ket("1")) / np.sqrt(2)
MAIS_I = (qb.ket("0") + 1j * qb.ket("1")) / np.sqrt(2)
MISTURADO = qb.matriz_densidade([qb.ket("0"), qb.ket("1")], [0.5, 0.5])


class TestProbabilidadesEAmostragem:
    def test_probabilidades(self, sparsa):
        psi = (qb.ket("00", sparsa=sparsa) + 1j * np.sqrt(3) * qb.ket("11", sparsa=sparsa)) / 2
        np.testing.assert_allclose(qb.probabilidades(psi), [0.25, 0, 0, 0.75])
        np.testing.assert_allclose(qb.probabilidades(psi.dag()), [0.25, 0, 0, 0.75])
        rho = qb.matriz_densidade(psi, sparsa=sparsa)
        np.testing.assert_allclose(qb.probabilidades(rho), [0.25, 0, 0, 0.75], atol=ATOL)

    def test_amostrar_qubits(self):
        contagens = qb.amostrar(qb.bell("psi+"), 2000, semente=7)
        assert set(contagens) == {"01", "10"}
        assert sum(contagens.values()) == 2000
        assert contagens == qb.amostrar(qb.bell("psi+"), 2000, semente=7)  # reprodutível
        assert abs(contagens["01"] - 1000) < 150

    def test_amostrar_estado_determinado(self):
        assert qb.amostrar(qb.ket("101"), 10) == {"101": 10}

    def test_amostrar_rotulos_fora_de_qubits(self):
        psi = qb.tensor(qb.fock(3, 2), qb.ket("1"))
        assert qb.amostrar(psi, 5) == {"2,1": 5}

    def test_amostrar_matriz_densidade(self):
        contagens = qb.amostrar(MISTURADO, 1000, semente=3)
        assert set(contagens) == {"0", "1"}


class TestTracoParcial:
    def test_estado_produto(self, sparsa):
        a = qb.coerente(4, 0.5)
        b = qb.ket("1")
        psi = qb.tensor(a, b)
        if sparsa:
            psi = psi.para_esparso()
        rho_a = qb.traco_parcial(psi, 0)
        np.testing.assert_allclose(densa(rho_a), densa(qb.matriz_densidade(a)), atol=ATOL)
        np.testing.assert_allclose(densa(qb.traco_parcial(psi, 1)), [[0, 0], [0, 1]], atol=ATOL)
        assert rho_a.dims == [[4], [4]]

    def test_estado_de_bell_e_maximamente_misturado(self):
        for manter in (0, 1):
            np.testing.assert_allclose(
                densa(qb.traco_parcial(qb.bell(), manter)), np.eye(2) / 2, atol=ATOL
            )

    def test_matriz_densidade_de_entrada(self):
        rho = qb.matriz_densidade(qb.ghz(3))
        reduzida = qb.traco_parcial(rho, [0, 2])
        assert reduzida.dims == [[2, 2], [2, 2]]
        np.testing.assert_allclose(np.diag(densa(reduzida)).real, [0.5, 0, 0, 0.5], atol=ATOL)

    def test_ordem_dos_subsistemas(self):
        psi = qb.ket("01")
        np.testing.assert_allclose(
            densa(qb.traco_parcial(psi, [1, 0])), densa(qb.matriz_densidade(qb.ket("10")))
        )

    def test_manter_tudo_devolve_o_proprio_estado(self):
        psi = qb.w(3)
        np.testing.assert_allclose(
            densa(qb.traco_parcial(psi, [0, 1, 2])), densa(qb.matriz_densidade(psi)), atol=ATOL
        )

    @pytest.mark.parametrize("manter", [[], [0, 0], [2], [-1]])
    def test_indices_invalidos(self, manter):
        with pytest.raises(ValueError, match="manter"):
            qb.traco_parcial(qb.bell(), manter)


class TestPurezaEntropia:
    def test_estados_puros(self, sparsa):
        psi = qb.coerente(10, 1.0, sparsa=sparsa)
        assert qb.pureza(psi) == pytest.approx(1.0)
        assert qb.pureza(qb.matriz_densidade(psi)) == pytest.approx(1.0)
        assert qb.entropia_von_neumann(psi) == pytest.approx(0.0, abs=1e-9)

    def test_estado_maximamente_misturado(self):
        assert qb.pureza(MISTURADO) == pytest.approx(0.5)
        assert qb.entropia_von_neumann(MISTURADO) == pytest.approx(1.0)
        assert qb.entropia_von_neumann(MISTURADO, base=np.e) == pytest.approx(np.log(2))

    def test_n_qubits_misturados(self):
        rho = qb.ObjQuantico(np.eye(8) / 8)
        assert qb.entropia_von_neumann(rho) == pytest.approx(3.0)
        assert qb.pureza(rho) == pytest.approx(1 / 8)


class TestFidelidade:
    def test_estados_puros(self):
        assert qb.fidelidade(qb.ket("0"), qb.ket("0")) == pytest.approx(1.0)
        assert qb.fidelidade(qb.ket("0"), qb.ket("1")) == pytest.approx(0.0)
        assert qb.fidelidade(qb.ket("0"), MAIS) == pytest.approx(0.5)
        assert qb.fidelidade(MAIS.dag(), MAIS) == pytest.approx(1.0)

    def test_puro_e_misto(self):
        assert qb.fidelidade(qb.ket("0"), MISTURADO) == pytest.approx(0.5)
        assert qb.fidelidade(MISTURADO, qb.ket("1")) == pytest.approx(0.5)

    def test_mistos(self):
        assert qb.fidelidade(MISTURADO, MISTURADO) == pytest.approx(1.0)
        rho = qb.matriz_densidade(MAIS)
        assert qb.fidelidade(rho, qb.matriz_densidade(qb.ket("0"))) == pytest.approx(0.5)
        # Fórmula fechada para qubits: F = Tr(rho sigma) + 2 sqrt(det rho det sigma)
        a = qb.matriz_densidade([qb.ket("0"), MAIS], [0.7, 0.3])
        b = qb.matriz_densidade([qb.ket("1"), MAIS_I], [0.4, 0.6])
        ra, rb = densa(a), densa(b)
        fechada = np.trace(ra @ rb).real + 2 * np.sqrt(
            np.linalg.det(ra).real * np.linalg.det(rb).real
        )
        assert qb.fidelidade(a, b) == pytest.approx(fechada)
        assert qb.fidelidade(a, b) == pytest.approx(qb.fidelidade(b, a))


class TestVetorBloch:
    @pytest.mark.parametrize(
        ("estado", "vetor"),
        [
            (qb.ket("0"), [0, 0, 1]),
            (qb.ket("1"), [0, 0, -1]),
            (MAIS, [1, 0, 0]),
            (MAIS_I, [0, 1, 0]),
            (MISTURADO, [0, 0, 0]),
        ],
        ids=["0", "1", "mais", "mais_i", "misturado"],
    )
    def test_estados_conhecidos(self, estado, vetor):
        np.testing.assert_allclose(qb.vetor_bloch(estado), vetor, atol=ATOL)

    def test_estado_puro_esta_na_superficie(self):
        psi = qb.ry(0.4) * qb.rz(1.3) * qb.ket("0")
        assert np.linalg.norm(qb.vetor_bloch(psi)) == pytest.approx(1.0)

    def test_so_para_um_qubit(self):
        with pytest.raises(ValueError, match="um qubit"):
            qb.vetor_bloch(qb.bell())


def test_comutador_e_anticomutador(sparsa):
    X, Y, Z = (f(sparsa=sparsa) for f in (qb.pauliX, qb.pauliY, qb.pauliZ))
    np.testing.assert_allclose(densa(qb.comutador(X, Y)), 2j * densa(Z), atol=ATOL)
    np.testing.assert_allclose(densa(qb.anticomutador(X, Y)), np.zeros((2, 2)), atol=ATOL)
    np.testing.assert_allclose(densa(qb.anticomutador(X, X)), 2 * np.eye(2), atol=ATOL)


def test_operador_numero(sparsa):
    n = qb.numero(6, sparsa=sparsa)
    np.testing.assert_allclose(densa(n), np.diag(np.arange(6)), atol=ATOL)
    assert qb.valor_esperado(qb.fock(6, 4), n) == pytest.approx(4)
