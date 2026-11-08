"""Testes das portas quânticas e dos estados emaranhados (Bell, GHZ, W)."""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, densa

PORTAS_1Q = {
    "H": qb.hadamard,
    "S": qb.porta_s,
    "T": qb.porta_t,
    "X": qb.pauliX,
}


def indice(rotulo):
    """Índice do vetor da base computacional de um rótulo binário."""
    return int(rotulo, 2)


def saida(porta, rotulo):
    """Estado resultante (denso, 1-D) de aplicar a porta a |rotulo>."""
    return densa(porta * qb.ket(rotulo)).ravel()


class TestPortasDeUmQubit:
    @pytest.mark.parametrize("nome", PORTAS_1Q)
    def test_unitarias(self, sparsa, nome):
        U = densa(PORTAS_1Q[nome](sparsa=sparsa))
        np.testing.assert_allclose(U.conj().T @ U, np.eye(2), atol=ATOL)

    def test_formato_e_dims(self, sparsa):
        H = qb.hadamard(sparsa=sparsa)
        assert H.formato == ("esparso" if sparsa else "denso")
        assert H.dims == [[2], [2]]

    def test_identidades_algebricas(self, sparsa):
        H, S, T = qb.hadamard(sparsa=sparsa), qb.porta_s(sparsa=sparsa), qb.porta_t(sparsa=sparsa)
        X, Z = densa(qb.pauliX()), densa(qb.pauliZ())
        np.testing.assert_allclose(densa(H * H), np.eye(2), atol=ATOL)
        np.testing.assert_allclose(densa(H * qb.pauliX() * H), Z, atol=ATOL)
        np.testing.assert_allclose(densa(H * qb.pauliZ() * H), X, atol=ATOL)
        np.testing.assert_allclose(densa(S * S), Z, atol=ATOL)
        np.testing.assert_allclose(densa(T * T), densa(S), atol=ATOL)

    def test_hadamard_cria_superposicao(self):
        np.testing.assert_allclose(saida(qb.hadamard(), "0"), [1, 1] / np.sqrt(2))
        np.testing.assert_allclose(saida(qb.hadamard(), "1"), [1, -1] / np.sqrt(2))

    def test_fase(self):
        np.testing.assert_allclose(densa(qb.fase(np.pi / 2)), densa(qb.porta_s()), atol=ATOL)
        np.testing.assert_allclose(densa(qb.fase(np.pi)), densa(qb.pauliZ()), atol=ATOL)

    @pytest.mark.parametrize(
        ("rotacao", "pauli"), [(qb.rx, qb.pauliX), (qb.ry, qb.pauliY), (qb.rz, qb.pauliZ)]
    )
    def test_rotacoes(self, sparsa, rotacao, pauli):
        theta = 0.73
        esperado = densa((-0.5j * theta * pauli()).expm())
        np.testing.assert_allclose(densa(rotacao(theta, sparsa=sparsa)), esperado, atol=ATOL)
        # R(pi) = -i sigma
        np.testing.assert_allclose(densa(rotacao(np.pi)), -1j * densa(pauli()), atol=ATOL)

    def test_rotacoes_movem_o_vetor_de_bloch(self):
        np.testing.assert_allclose(
            qb.vetor_bloch(qb.ry(np.pi / 2) * qb.ket("0")), [1, 0, 0], atol=ATOL
        )
        np.testing.assert_allclose(
            qb.vetor_bloch(qb.rx(-np.pi / 2) * qb.ket("0")), [0, 1, 0], atol=ATOL
        )


class TestPortasDeVariosQubits:
    def test_cnot_matriz(self, sparsa):
        esperado = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
        porta = qb.cnot(sparsa=sparsa)
        np.testing.assert_allclose(densa(porta), esperado)
        assert porta.dims == [[2, 2], [2, 2]]
        assert porta.formato == ("esparso" if sparsa else "denso")

    @pytest.mark.parametrize(
        ("entrada", "esperada"), [("00", "00"), ("01", "01"), ("10", "11"), ("11", "10")]
    )
    def test_cnot_tabela_verdade(self, entrada, esperada):
        np.testing.assert_allclose(saida(qb.cnot(), entrada), densa(qb.ket(esperada)).ravel())

    def test_cnot_invertido(self):
        # controle no qubit 1, alvo no 0: |01> -> |11>
        np.testing.assert_allclose(saida(qb.cnot(1, 0), "01"), densa(qb.ket("11")).ravel())
        np.testing.assert_allclose(saida(qb.cnot(1, 0), "10"), densa(qb.ket("10")).ravel())

    @pytest.mark.parametrize(
        ("entrada", "esperada"),
        [("000", "000"), ("100", "101"), ("110", "111"), ("011", "011"), ("101", "100")],
    )
    def test_cnot_entre_qubits_nao_vizinhos(self, entrada, esperada):
        porta = qb.cnot(controle=0, alvo=2, n_qubits=3)
        np.testing.assert_allclose(saida(porta, entrada), densa(qb.ket(esperada)).ravel())

    def test_cz_e_swap(self, sparsa):
        np.testing.assert_allclose(np.diag(densa(qb.cz(sparsa=sparsa))), [1, 1, 1, -1])
        swap = qb.swap(sparsa=sparsa)
        np.testing.assert_allclose(saida(swap, "01"), densa(qb.ket("10")).ravel())
        np.testing.assert_allclose(densa(swap * swap), np.eye(4))
        # SWAP = 3 CNOTs alternados
        tres = qb.cnot(0, 1) * qb.cnot(1, 0) * qb.cnot(0, 1)
        np.testing.assert_allclose(densa(swap), densa(tres), atol=ATOL)

    def test_toffoli(self):
        for entrada in ["000", "001", "010", "011", "100", "101", "110", "111"]:
            esperada = entrada[:2] + str(1 - int(entrada[2])) if entrada[:2] == "11" else entrada
            np.testing.assert_allclose(
                saida(qb.toffoli(), entrada), densa(qb.ket(esperada)).ravel()
            )

    def test_porta_controlada_generica(self):
        U = qb.porta_controlada(qb.hadamard(), controles=1, alvo=0)
        # Só age quando o controle (qubit 1) vale 1: |01> -> |+>|1>
        esperado = densa(qb.tensor(qb.hadamard() * qb.ket("0"), qb.ket("1"))).ravel()
        np.testing.assert_allclose(saida(U, "01"), esperado, atol=ATOL)
        np.testing.assert_allclose(saida(U, "00"), densa(qb.ket("00")).ravel())

    def test_porta_em(self, sparsa):
        X1 = qb.porta_em(qb.pauliX(sparsa=sparsa), 1, 3)
        esperado = qb.tensor(qb.identidade(2), qb.pauliX(), qb.identidade(2))
        np.testing.assert_allclose(densa(X1), densa(esperado))
        assert X1.formato == ("esparso" if sparsa else "denso")
        # alvos fora de ordem: CNOT com controle no qubit 2 e alvo no 0
        porta = qb.porta_em(qb.cnot(), [2, 0], 3)
        np.testing.assert_allclose(saida(porta, "001"), densa(qb.ket("101")).ravel())

    def test_entradas_invalidas(self):
        with pytest.raises(ValueError, match="distintos"):
            qb.cnot(0, 0)
        with pytest.raises(ValueError, match="fora do intervalo"):
            qb.cnot(0, 2)
        with pytest.raises(ValueError, match="inteiro positivo"):
            qb.porta_em(qb.pauliX(), 0, 0)
        with pytest.raises(ValueError, match="4×4"):
            qb.porta_em(qb.pauliX(), [0, 1], 2)
        with pytest.raises(ValueError, match="um qubit"):
            qb.porta_controlada(qb.cnot(), 0, 1, 3)


class TestCircuitosEEstadosEmaranhados:
    def test_circuito_de_bell(self, sparsa):
        circuito = qb.cnot(sparsa=sparsa) * qb.tensor(qb.hadamard(), qb.identidade(2))
        psi = circuito * qb.ket("00", sparsa=sparsa)
        assert qb.fidelidade(psi, qb.bell("phi+")) == pytest.approx(1.0)

    @pytest.mark.parametrize(
        ("tipo", "componentes"),
        [
            ("phi+", {"00": 1, "11": 1}),
            ("phi-", {"00": 1, "11": -1}),
            ("psi+", {"01": 1, "10": 1}),
            ("psi-", {"01": 1, "10": -1}),
        ],
    )
    def test_estados_de_bell(self, sparsa, tipo, componentes):
        psi = densa(qb.bell(tipo, sparsa=sparsa)).ravel()
        esperado = np.zeros(4)
        for rotulo, sinal in componentes.items():
            esperado[indice(rotulo)] = sinal / np.sqrt(2)
        np.testing.assert_allclose(psi, esperado, atol=ATOL)

    def test_bell_sao_ortonormais(self):
        estados = [qb.bell(t) for t in ("phi+", "phi-", "psi+", "psi-")]
        for i, a in enumerate(estados):
            for j, b in enumerate(estados):
                assert qb.fidelidade(a, b) == pytest.approx(1.0 if i == j else 0.0, abs=1e-12)

    def test_tipo_de_bell_invalido(self):
        with pytest.raises(ValueError, match="phi"):
            qb.bell("xyz")

    @pytest.mark.parametrize("n", [2, 3, 5])
    def test_ghz(self, n):
        psi = qb.ghz(n)
        assert psi.dims == [[2] * n, [1] * n]
        assert qb.amostrar(psi, 500, semente=1).keys() <= {"0" * n, "1" * n}
        # Cada qubit sozinho está maximamente misturado.
        assert qb.entropia_von_neumann(qb.traco_parcial(psi, 0)) == pytest.approx(1.0)

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_w(self, n):
        prob = qb.probabilidades(qb.w(n))
        indices_um_bit = [2**k for k in range(n)]
        np.testing.assert_allclose(prob[indices_um_bit], 1 / n)
        assert prob.sum() == pytest.approx(1.0)

    def test_n_qubits_invalido(self):
        with pytest.raises(ValueError, match="n_qubits"):
            qb.ghz(0)
