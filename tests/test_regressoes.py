"""Testes de regressão: um teste por bug corrigido na versão 0.1.0.

Os códigos (B1–B20, P7) são os da seção 1.2 do ``PLANO_DE_TRABALHO.md``. Alguns bugs
têm testes mais completos nos arquivos de cada módulo; aqui fica o caso mínimo, para
que cada bug tenha um teste fácil de achar.
"""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import criar, densa


def test_b2_dimensao_de_um_bra(sparsa):
    assert qb.bases(4, 0, sparsa=sparsa).dag().dim() == 4


def test_b3_autoestados_retorna_valores_e_vetores(sparsa):
    autovalores, autovetores = qb.pauliZ(sparsa=sparsa).autoestados()
    Z = densa(qb.pauliZ())
    for k, autovalor in enumerate(autovalores):
        np.testing.assert_allclose(Z @ autovetores[:, k], autovalor * autovetores[:, k])


def test_b4_repr_nao_imprime_nem_depende_do_ipython(sparsa, capsys):
    texto = repr(qb.destruicao(3, sparsa=sparsa))
    assert capsys.readouterr().out == ""
    assert "1.414" in texto


def test_b5_produto_esparso_nao_imprime_nada(capsys):
    qb.pauliX(sparsa=True) * qb.pauliZ(sparsa=True)
    assert capsys.readouterr().out == ""


def test_b6_aritmetica_com_escalares(sparsa):
    X = qb.pauliX(sparsa=sparsa)
    x = densa(qb.pauliX())
    np.testing.assert_allclose(densa(-X), -x)
    np.testing.assert_allclose(densa(X + 2), x + 2 * np.eye(2))
    np.testing.assert_allclose(densa(2 + X), x + 2 * np.eye(2))
    np.testing.assert_allclose(densa(X - 1), x - np.eye(2))
    np.testing.assert_allclose(densa(X / 1j), -1j * x)


def test_b7_escalar_dividido_por_operador_e_erro(sparsa):
    with pytest.raises(TypeError):
        2 / criar(np.array([[1.0, 2.0], [3.0, 4.0]]), sparsa)


def test_b8_mistura_denso_e_esparso():
    x, z = densa(qb.pauliX()), densa(qb.pauliZ())
    np.testing.assert_allclose(densa(qb.pauliX() * qb.pauliZ(sparsa=True)), x @ z)
    np.testing.assert_allclose(densa(qb.pauliX(sparsa=True) * qb.pauliZ()), x @ z)
    np.testing.assert_allclose(densa(qb.pauliX() + qb.pauliZ(sparsa=True)), x + z)


def test_b9_traco_complexo(sparsa):
    assert criar(np.array([[1j, 0], [0, 1]]), sparsa).traco() == pytest.approx(1 + 1j)


def test_b10_adjunto_mantem_latex(sparsa):
    assert qb.pauliX(sparsa=sparsa).dag().latex_representation is not None


@pytest.mark.parametrize(
    "chamada",
    [lambda: qb.ket("2"), lambda: qb.bra("2"), lambda: qb.ket(1.5)],
    ids=["ket_2", "bra_2", "ket_1.5"],
)
def test_b11_entrada_invalida_gera_erro(chamada):
    with pytest.raises(ValueError, match="entrada inválida"):
        chamada()


@pytest.mark.parametrize(
    "chamada",
    [lambda: qb.bases(2, 5), lambda: qb.bases(2, 5, sparsa=True), lambda: qb.ket(2)],
    ids=["denso", "esparso_vetor_nulo", "ket_2"],
)
def test_b12_indice_fora_da_dimensao(chamada):
    with pytest.raises(ValueError, match="índice n|entrada inválida"):
        chamada()


def test_b13_b14_b15_solver():
    # B13 (t_span), B14 (norma) e B15 (esparso) — detalhes em test_dinamica/test_compat.
    resultado = qb.resolver_schrodinger(qb.pauliX(sparsa=True), qb.ket("0"), np.linspace(0, 10, 51))
    np.testing.assert_allclose(np.linalg.norm(resultado.vetores, axis=0), 1.0, atol=1e-7)


def test_b19_listas_de_tamanhos_diferentes():
    with pytest.raises(ValueError, match="número de probabilidades"):
        qb.matriz_densidade([qb.ket("0")], [0.5, 0.5])


def test_b20_latex_de_ket_e_bra(sparsa):
    assert r"\ket{0}" in qb.ket("0", sparsa=sparsa).latex_representation
    assert r"\bra{1}" in qb.bra("1", sparsa=sparsa).latex_representation


def test_p7_coerente_analitico_estavel_para_n_grande():
    psi = densa(qb.coerente(400, 12.0, metodo="analitico"))
    assert np.all(np.isfinite(psi))
    assert np.linalg.norm(psi) == pytest.approx(1.0, abs=1e-10)
