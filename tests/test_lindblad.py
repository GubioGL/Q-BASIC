"""Testes da equação mestra de Lindblad (sistemas abertos)."""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, densa

METODOS = ["expm", "RK45", "DOP853"]
TEMPOS = np.linspace(0, 5, 26)


@pytest.mark.parametrize("metodo", METODOS)
def test_emissao_espontanea(sparsa, metodo):
    # Átomo excitado (|1>) decaindo com taxa gamma: P_excitado(t) = exp(-gamma t).
    gamma = 0.7
    sm = qb.destruicao(2, sparsa=sparsa)
    H = 1.3 * qb.numero(2, sparsa=sparsa)
    resultado = qb.resolver_lindblad(
        H, qb.ket("1"), TEMPOS, [np.sqrt(gamma) * sm], [sm.dag() * sm], metodo=metodo
    )
    np.testing.assert_allclose(resultado.valores_esperados[0], np.exp(-gamma * TEMPOS), atol=1e-7)


def test_oscilador_amortecido_mantem_estado_coerente():
    # Cavidade com perda kappa: |alpha> -> |alpha e^{-(i w + kappa/2) t}>.
    N, kappa, w, alpha = 25, 0.4, 1.0, 2.0
    a = qb.destruicao(N, sparsa=True)
    resultado = qb.resolver_lindblad(
        w * qb.numero(N, sparsa=True),
        qb.coerente(N, alpha),
        TEMPOS,
        [np.sqrt(kappa) * a],
        [a.dag() * a, a],
    )
    n_medio, amplitude = resultado.valores_esperados
    np.testing.assert_allclose(n_medio, alpha**2 * np.exp(-kappa * TEMPOS), atol=1e-7)
    esperado = alpha * np.exp(-(1j * w + kappa / 2) * TEMPOS)
    np.testing.assert_allclose(amplitude, esperado, atol=1e-7)


def test_defasagem_destroi_coerencias():
    # L = sqrt(gamma/2) Z: populações fixas, coerência rho_01 decai como exp(-gamma t).
    gamma = 0.5
    mais = (qb.ket("0") + qb.ket("1")) / np.sqrt(2)
    resultado = qb.resolver_lindblad(
        qb.identidade(2) * 0,
        mais,
        TEMPOS,
        [np.sqrt(gamma / 2) * qb.pauliZ()],
        [qb.pauliX(), qb.pauliZ()],
    )
    x, z = resultado.valores_esperados
    np.testing.assert_allclose(x, np.exp(-gamma * TEMPOS), atol=1e-8)
    np.testing.assert_allclose(z, 0, atol=1e-10)
    final = resultado.estados[-1]
    assert qb.pureza(final) < 0.51


@pytest.mark.parametrize("metodo", METODOS)
def test_sem_colapso_e_igual_a_schrodinger(metodo):
    H = qb.pauliX() + 0.3 * qb.pauliZ()
    psi0 = qb.ket("0")
    lindblad = qb.resolver_lindblad(H, psi0, TEMPOS, metodo=metodo)
    schrodinger = qb.resolver_schrodinger(H, psi0, TEMPOS)
    for rho, psi in zip(lindblad.estados, schrodinger.estados, strict=True):
        np.testing.assert_allclose(densa(rho), densa(qb.matriz_densidade(psi)), atol=1e-7)


def test_propriedades_fisicas_preservadas():
    N = 6
    a = qb.destruicao(N)
    H = qb.numero(N) + 0.2 * (a + a.dag())
    rho0 = qb.matriz_densidade([qb.fock(N, 1), qb.fock(N, 3)], [0.4, 0.6])
    resultado = qb.resolver_lindblad(H, rho0, TEMPOS, [0.5 * a, 0.2 * a.dag()])
    for rho in resultado.estados:
        assert rho.traco() == pytest.approx(1.0, abs=1e-9)
        assert rho.eh_hermitiano(tol=1e-9)
        assert np.all(np.linalg.eigvalsh(densa(rho)) > -1e-9)


def test_resultado_de_densidade():
    rho0 = qb.matriz_densidade(qb.ket("01"))
    H = qb.tensor(qb.pauliX(), qb.identidade(2))
    resultado = qb.resolver_lindblad(H, rho0, [0, 0.5, 1.0])
    assert resultado.tipo == "densidade"
    assert resultado.dimensao == 4
    assert resultado.vetores.shape == (16, 3)
    assert all(e.dims == [[2, 2], [2, 2]] for e in resultado.estados)
    assert "densidade" in repr(resultado)
    # valor_esperado aceita o Resultado diretamente
    np.testing.assert_allclose(
        qb.valor_esperado(resultado, qb.tensor(qb.pauliZ(), qb.identidade(2))),
        np.cos(2 * np.array([0, 0.5, 1.0])),
        atol=1e-10,
    )
    estado_unico = qb.resolver_lindblad(H, rho0, [0.3])
    np.testing.assert_allclose(densa(estado_unico.estados[0]), densa(rho0))


def test_liouvilliano():
    # Para H = 0 e L = sqrt(g) sigma-, o Liouvilliano tem autovalores 0, -g/2 (x2) e -g.
    g = 0.8
    L = qb.liouvilliano(qb.identidade(2) * 0, [np.sqrt(g) * qb.destruicao(2)])
    assert L.shape == (4, 4)
    assert L.formato == "esparso"
    autovalores = np.sort(np.linalg.eigvals(densa(L)).real)
    np.testing.assert_allclose(autovalores, [-g, -g / 2, -g / 2, 0], atol=ATOL)


@pytest.mark.parametrize(
    ("estado0", "colapso", "erro", "mensagem"),
    [
        ("bra", [], ValueError, "ket ou uma matriz densidade"),
        ("dim3", [], ValueError, "incompatíveis"),
        ("ket", ["dim3"], ValueError, "operador de colapso"),
        ("array", [], TypeError, "ObjQuantico"),
    ],
)
def test_entradas_invalidas(estado0, colapso, erro, mensagem):
    objetos = {
        "bra": qb.bra("0"),
        "dim3": qb.identidade(3),
        "ket": qb.ket("0"),
        "array": np.eye(2),
    }
    with pytest.raises(erro, match=mensagem):
        qb.resolver_lindblad(qb.pauliZ(), objetos[estado0], [0, 1], [objetos[c] for c in colapso])
