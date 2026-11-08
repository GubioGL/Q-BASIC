"""Bugs conhecidos (seção 1.2 do PLANO_DE_TRABALHO.md).

Cada teste descreve o comportamento CORRETO e está marcado como ``xfail``
(falha esperada) enquanto o bug existir. Como ``xfail_strict = true`` no
``pyproject.toml``, quando um bug for corrigido o teste passa a "passar
inesperadamente" e a suíte acusa erro: é o aviso para remover a marcação
``xfail`` e o teste virar um teste normal de regressão.

Correções previstas na Fase 4 (e P7 na Fase 5).
"""

import numpy as np
import pytest

import qbasic as qb
from auxiliares import ATOL, densa


def bug(codigo, descricao, **kwargs):
    """Marca um teste como falha esperada por causa de um bug conhecido."""
    return pytest.mark.xfail(reason=f"{codigo}: {descricao}", **kwargs)


# --------------------------------------------------------------------------- B2
@bug("B2", "dim() usa len() e retorna 1 para um bra", raises=AssertionError)
def test_b2_dimensao_de_um_bra(sparsa):
    assert qb.bases(4, 0, sparsa=sparsa).dag().dim() == 4


# --------------------------------------------------------------------------- B3
@bug("B3", "AutoValor_Vetor (denso) retorna só os autovetores", raises=AssertionError)
def test_b3_autovalor_vetor_retorna_valores_e_vetores():
    resultado = qb.pauliZ().AutoValor_Vetor()
    assert isinstance(resultado, tuple)
    autovalores, autovetores = resultado
    Z = densa(qb.pauliZ())
    for k, autovalor in enumerate(autovalores):
        np.testing.assert_allclose(Z @ autovetores[:, k], autovalor * autovetores[:, k])


# --------------------------------------------------------------------------- B4
@bug("B4", "__repr__ chama display() e imprime fora do Jupyter", raises=AssertionError)
def test_b4_repr_nao_imprime_nada(sparsa, capsys):
    repr(qb.destruiçao(3, sparsa=sparsa))
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- B5
@bug("B5", 'print("Aqui !") esquecido no produto esparso', raises=AssertionError)
def test_b5_produto_esparso_nao_imprime_nada(capsys):
    qb.pauliX(sparsa=True) * qb.pauliZ(sparsa=True)
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- B6
class TestB6AritmeticaIncompleta:
    marca = bug("B6", "aritmética com escalares/negação não suportada", raises=TypeError)

    @marca
    def test_negacao(self, sparsa):
        np.testing.assert_allclose(densa(-qb.pauliX(sparsa=sparsa)), -densa(qb.pauliX()))

    @marca
    def test_soma_com_escalar_e_multiplo_da_identidade(self, sparsa):
        X = qb.pauliX(sparsa=sparsa)
        np.testing.assert_allclose(densa(X + 2), densa(qb.pauliX()) + 2 * np.eye(2))

    @marca
    def test_soma_reversa_com_escalar(self, sparsa):
        X = qb.pauliX(sparsa=sparsa)
        np.testing.assert_allclose(densa(2 + X), densa(qb.pauliX()) + 2 * np.eye(2))

    @marca
    def test_subtracao_de_escalar(self, sparsa):
        X = qb.pauliX(sparsa=sparsa)
        np.testing.assert_allclose(densa(X - 1), densa(qb.pauliX()) - np.eye(2))

    @marca
    def test_divisao_por_complexo(self, sparsa):
        X = qb.pauliX(sparsa=sparsa)
        np.testing.assert_allclose(densa(X / 1j), -1j * densa(qb.pauliX()))


# --------------------------------------------------------------------------- B7
@bug("B7", "escalar / operador faz divisão elemento a elemento")
def test_b7_escalar_dividido_por_operador_e_erro():
    with pytest.raises(TypeError):
        2 / qb.ObjQuantico(np.array([[1.0, 2.0], [3.0, 4.0]]))


# --------------------------------------------------------------------------- B8
class TestB8MisturaDensoEsparso:
    marca = bug("B8", "não é possível misturar denso e esparso", raises=TypeError)

    @marca
    def test_denso_vezes_esparso(self):
        resultado = qb.pauliX() * qb.pauliZ(sparsa=True)
        np.testing.assert_allclose(densa(resultado), densa(qb.pauliX()) @ densa(qb.pauliZ()))

    @marca
    def test_esparso_vezes_denso(self):
        resultado = qb.pauliX(sparsa=True) * qb.pauliZ()
        np.testing.assert_allclose(densa(resultado), densa(qb.pauliX()) @ densa(qb.pauliZ()))

    @marca
    def test_soma_denso_e_esparso(self):
        resultado = qb.pauliX() + qb.pauliZ(sparsa=True)
        np.testing.assert_allclose(densa(resultado), densa(qb.pauliX()) + densa(qb.pauliZ()))


# --------------------------------------------------------------------------- B9
@bug("B9", "traço() descarta a parte imaginária", raises=AssertionError)
def test_b9_traco_complexo(sparsa):
    matriz = np.array([[1j, 0], [0, 1]])
    A = qb.ObjQuantico_esparso(matriz) if sparsa else qb.ObjQuantico(matriz)
    assert A.traço() == pytest.approx(1 + 1j)


# -------------------------------------------------------------------------- B10
@bug("B10", "dag() perde a representação LaTeX", raises=AssertionError)
def test_b10_adjunto_mantem_latex(sparsa):
    assert qb.pauliX(sparsa=sparsa).dag().latex_representation is not None


# -------------------------------------------------------------------------- B11
@bug("B11", "ket/bra com entrada inválida só imprimem uma mensagem e retornam None")
@pytest.mark.parametrize(
    "chamada",
    [lambda: qb.ket("2"), lambda: qb.bra("2"), lambda: qb.ket(1.5)],
    ids=["ket_2", "bra_2", "ket_1.5"],
)
def test_b11_entrada_invalida_gera_erro(chamada):
    with pytest.raises(ValueError):
        chamada()


# -------------------------------------------------------------------------- B12
@bug("B12", "bases/ket não validam n < N (IndexError ou vetor nulo silencioso)")
@pytest.mark.parametrize(
    "chamada",
    [lambda: qb.bases(2, 5), lambda: qb.bases(2, 5, sparsa=True), lambda: qb.ket(2)],
    ids=["denso", "esparso_vetor_nulo", "ket_2"],
)
def test_b12_indice_fora_da_dimensao(chamada):
    with pytest.raises(ValueError):
        chamada()


# -------------------------------------------------------------------------- B13
@bug("B13", "t_span == None quebra com arrays NumPy", raises=ValueError)
def test_b13_t_span_como_array():
    tempos = np.linspace(0, 1, 5)
    resultado = qb.edo.solve(qb.pauliX(), tempos, qb.bases(2, 0), t_span=np.array([0.0, 1.0]))
    assert resultado.success


# -------------------------------------------------------------------------- B14
@bug("B14", "tolerâncias padrão do solver não conservam a norma", raises=AssertionError)
def test_b14_norma_conservada_com_opcoes_padrao():
    tempos = np.linspace(0, 10, 51)
    resultado = qb.edo.solve(qb.pauliX(), tempos, qb.bases(2, 0))
    np.testing.assert_allclose(np.linalg.norm(resultado.y, axis=0), 1.0, atol=1e-6)


# -------------------------------------------------------------------------- B15
class ErroDensificou(RuntimeError):
    """O solver converteu o Hamiltoniano esparso para denso."""


@bug("B15", "o solver converte o Hamiltoniano esparso para denso", raises=ErroDensificou)
def test_b15_solver_nao_densifica_hamiltoniano_esparso(monkeypatch):
    def proibido(self):
        raise ErroDensificou

    H = qb.pauliX(sparsa=True)
    monkeypatch.setattr(qb.ObjQuantico_esparso, "full", proibido)
    resultado = qb.edo.solve(H, np.linspace(0, 1, 5), qb.bases(2, 0))
    assert resultado.success


# -------------------------------------------------------------------------- B16
@bug("B16", "edo herda de ObjQuantico sem motivo", raises=AssertionError)
def test_b16_solver_nao_e_objeto_quantico():
    assert not issubclass(qb.edo, qb.ObjQuantico)


# -------------------------------------------------------------------------- B19
@bug("B19", "matrizdensidade ignora estados/probabilidades sobrando (zip)")
def test_b19_listas_de_tamanhos_diferentes():
    with pytest.raises(ValueError):
        qb.matrizdensidade([0.5, 0.5], [qb.ket("0")], puro=False)


# -------------------------------------------------------------------------- B20
@bug("B20", "f-string engole as chaves do LaTeX de ket/bra", raises=AssertionError)
def test_b20_latex_de_ket_e_bra(sparsa):
    assert r"\ket{0}" in qb.ket("0", sparsa=sparsa).latex_representation
    assert r"\bra{1}" in qb.bra("1", sparsa=sparsa).latex_representation


# --------------------------------------------------------------------------- P7
@bug("P7", "estado coerente analítico estoura (factorial/alpha**n) para N grande")
def test_p7_coerente_analitico_estavel_para_n_grande():
    psi = densa(qb.coerente(400, 12.0, metodo="analitico"))
    assert np.all(np.isfinite(psi))
    assert np.linalg.norm(psi) == pytest.approx(1.0, abs=ATOL)
