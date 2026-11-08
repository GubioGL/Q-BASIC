"""Testes da matriz densidade (estados puros e mistos)."""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, densa


def superposicao():
    """(|0> + |1>) / sqrt(2)."""
    return (qb.ket("0") + qb.ket("1")) / np.sqrt(2)


def verificar_propriedades_fisicas(rho):
    """Traço 1, hermitiana e positiva semidefinida."""
    assert np.trace(rho).real == pytest.approx(1.0)
    np.testing.assert_allclose(rho, rho.conj().T, atol=ATOL)
    assert np.all(np.linalg.eigvalsh(rho) >= -ATOL)


class TestEstadoPuro:
    @pytest.mark.parametrize(
        "estado",
        [lambda: qb.bases(3, 1), superposicao, lambda: qb.coerente(15, 0.8)],
        ids=["fock", "superposicao", "coerente"],
    )
    def test_projetor_no_estado(self, estado):
        psi = estado()
        rho = densa(qb.matriz_densidade(psi))
        vetor = densa(psi).ravel()
        np.testing.assert_allclose(rho, np.outer(vetor, vetor.conj()), atol=ATOL)
        verificar_propriedades_fisicas(rho)

    def test_pureza_e_idempotencia(self):
        rho = densa(qb.matriz_densidade(superposicao()))
        assert np.trace(rho @ rho).real == pytest.approx(1.0)
        np.testing.assert_allclose(rho @ rho, rho, atol=ATOL)

    def test_formato(self, sparsa):
        rho = qb.matriz_densidade(superposicao(), sparsa=sparsa)
        assert rho.formato == ("esparso" if sparsa else "denso")
        np.testing.assert_allclose(densa(rho), [[0.5, 0.5], [0.5, 0.5]], atol=ATOL)

    def test_dims_de_sistema_composto(self):
        rho = qb.matriz_densidade(qb.ket("01"))
        assert rho.dims == [[2, 2], [2, 2]]

    def test_probabilidade_unitaria_e_aceita(self):
        np.testing.assert_allclose(densa(qb.matriz_densidade(qb.ket("1"), [1.0])), [[0, 0], [0, 1]])

    def test_exige_ket(self):
        with pytest.raises(ValueError, match="ket"):
            qb.matriz_densidade(qb.bra("0"))
        with pytest.raises(ValueError, match="omita"):
            qb.matriz_densidade(qb.ket("0"), [0.5])


class TestEstadoMisto:
    def test_mistura_maxima_de_um_qubit(self, sparsa):
        rho = qb.matriz_densidade([qb.ket("0"), qb.ket("1")], [0.5, 0.5], sparsa=sparsa)
        assert rho.formato == ("esparso" if sparsa else "denso")
        rho = densa(rho)
        np.testing.assert_allclose(rho, np.eye(2) / 2, atol=ATOL)
        assert np.trace(rho @ rho).real == pytest.approx(0.5)

    def test_mistura_geral(self, sparsa):
        probabilidades = [0.2, 0.3, 0.5]
        estados = [
            qb.bases(3, 0),
            (qb.bases(3, 1) + qb.bases(3, 2)) / np.sqrt(2),
            (qb.bases(3, 0) + 1j * qb.bases(3, 2, sparsa=True)) / np.sqrt(2),
        ]
        rho = densa(qb.matriz_densidade(estados, probabilidades, sparsa=sparsa))
        esperado = sum(
            p * np.outer(densa(s).ravel(), densa(s).ravel().conj())
            for p, s in zip(probabilidades, estados, strict=True)
        )
        np.testing.assert_allclose(rho, esperado, atol=ATOL)
        verificar_propriedades_fisicas(rho)
        assert np.trace(rho @ rho).real < 1

    @pytest.mark.parametrize(
        ("probabilidades", "estados", "mensagem"),
        [
            ([0.5, 0.6], ["0", "1"], "somar 1"),
            ([1.5, -0.5], ["0", "1"], "não negativas"),
            # Bug B19: antes o zip ignorava o que sobrava e o traço ficava 0,5.
            ([0.5, 0.5], ["0"], "número de probabilidades"),
            ([1.0], ["0", "1"], "número de probabilidades"),
            (None, ["0", "1"], "informe as probabilidades"),
            ([], [], "vazia"),
        ],
    )
    def test_probabilidades_invalidas(self, probabilidades, estados, mensagem):
        with pytest.raises(ValueError, match=mensagem):
            qb.matriz_densidade([qb.ket(e) for e in estados], probabilidades)

    def test_estados_devem_ser_normalizados(self):
        nao_normalizado = qb.ket("0") + qb.ket("1")
        with pytest.raises(ValueError, match="normalizados"):
            qb.matriz_densidade([qb.ket("0"), nao_normalizado], [0.5, 0.5])

    def test_estados_devem_ser_kets_da_mesma_dimensao(self):
        with pytest.raises(ValueError, match="mesma dimensão"):
            qb.matriz_densidade([qb.ket("0"), qb.bases(3, 0)], [0.5, 0.5])
        with pytest.raises(ValueError, match="kets"):
            qb.matriz_densidade([qb.ket("0"), qb.bra("1")], [0.5, 0.5])
