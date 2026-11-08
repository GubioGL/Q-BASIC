"""Testes da matriz densidade (estados puros e mistos)."""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, densa


def superposicao():
    """(|0> + |1>) / sqrt(2)."""
    return (qb.bases(2, 0) + qb.bases(2, 1)) / np.sqrt(2)


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
        rho = densa(qb.matrizdensidade(estados=psi))
        vetor = densa(psi).ravel()
        np.testing.assert_allclose(rho, np.outer(vetor, vetor.conj()), atol=ATOL)
        verificar_propriedades_fisicas(rho)

    def test_pureza_e_idempotencia(self):
        rho = densa(qb.matrizdensidade(estados=superposicao()))
        assert np.trace(rho @ rho).real == pytest.approx(1.0)
        np.testing.assert_allclose(rho @ rho, rho, atol=ATOL)

    def test_formato_esparso(self):
        rho = qb.matrizdensidade(estados=superposicao(), sparsa=True)
        assert isinstance(rho, qb.ObjQuantico_esparso)
        np.testing.assert_allclose(densa(rho), [[0.5, 0.5], [0.5, 0.5]], atol=ATOL)


class TestEstadoMisto:
    def test_mistura_maxima_de_um_qubit(self, sparsa):
        rho = qb.matrizdensidade([0.5, 0.5], [qb.ket("0"), qb.ket("1")], puro=False, sparsa=sparsa)
        rho = densa(rho)
        np.testing.assert_allclose(rho, np.eye(2) / 2, atol=ATOL)
        assert np.trace(rho @ rho).real == pytest.approx(0.5)

    def test_mistura_geral(self, sparsa):
        probabilidades = [0.2, 0.3, 0.5]
        estados = [
            qb.bases(3, 0),
            (qb.bases(3, 1) + qb.bases(3, 2)) / np.sqrt(2),
            (qb.bases(3, 0) + 1j * qb.bases(3, 2)) / np.sqrt(2),
        ]
        rho = densa(qb.matrizdensidade(probabilidades, estados, puro=False, sparsa=sparsa))
        esperado = sum(
            p * np.outer(densa(s).ravel(), densa(s).ravel().conj())
            for p, s in zip(probabilidades, estados, strict=True)
        )
        np.testing.assert_allclose(rho, esperado, atol=ATOL)
        verificar_propriedades_fisicas(rho)
        assert np.trace(rho @ rho).real < 1

    def test_probabilidades_devem_somar_um(self):
        with pytest.raises(ValueError, match="somar 1"):
            qb.matrizdensidade([0.5, 0.6], [qb.ket("0"), qb.ket("1")], puro=False)

    def test_estados_devem_ser_normalizados(self):
        nao_normalizado = qb.bases(2, 0) + qb.bases(2, 1)
        with pytest.raises(ValueError, match="normalizados"):
            qb.matrizdensidade([0.5, 0.5], [qb.ket("0"), nao_normalizado], puro=False)
