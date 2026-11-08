"""Compatibilidade com o código escrito para as versões 0.0.x.

Os nomes antigos (com acento, com maiúsculas ou de módulos renomeados) continuam
funcionando e emitem ``DeprecationWarning`` apontando o nome novo.
"""

import importlib
import importlib.metadata
import sys
import textwrap

import numpy as np
import pytest

import qbasic as qb
from auxiliares import densa

NOMES_NOVOS = [
    "ObjQuantico",
    "Resultado",
    "bases",
    "bra",
    "coerente",
    "criacao",
    "destruicao",
    "fock",
    "identidade",
    "ket",
    "matriz_densidade",
    "operador_p",
    "operador_x",
    "pauliX",
    "pauliY",
    "pauliZ",
    "resolver_schrodinger",
    "tensor",
    "valor_esperado",
    "valores_esperados",
]

# nome antigo no pacote -> nome novo
APELIDOS = {
    "destruiçao": "destruicao",
    "criaçao": "criacao",
    "Identidade": "identidade",
    "Fock": "fock",
}

MODULOS_ANTIGOS = {
    "class_tijolo": ["ObjQuantico", "ObjQuantico_esparso"],
    "operador": [
        "Identidade",
        "destruiçao",
        "criaçao",
        "operador_x",
        "operador_p",
        "pauliX",
        "pauliY",
        "pauliZ",
        "matrizdensidade",
    ],
    "funçoes": ["edo", "valor_esperado", "Valor_esperado"],
}


def test_versao_do_pacote():
    assert qb.__version__ == importlib.metadata.version("Q-BASIC")
    partes = qb.__version__.split(".")
    assert len(partes) >= 3
    assert all(p.isdigit() for p in partes[:3])


@pytest.mark.parametrize("nome", NOMES_NOVOS)
def test_nomes_novos_no_pacote(nome):
    assert hasattr(qb, nome)
    assert nome in qb.__all__


def test_all_contem_apenas_nomes_existentes():
    for nome in qb.__all__:
        assert hasattr(qb, nome), nome


def test_nome_inexistente_gera_attribute_error():
    with pytest.raises(AttributeError, match="não tem o atributo"):
        qb.nao_existe  # noqa: B018


@pytest.mark.parametrize(("antigo", "novo"), APELIDOS.items())
def test_apelidos_avisam_e_funcionam(antigo, novo):
    with pytest.deprecated_call(match=novo):
        funcao = getattr(qb, antigo)
    assert funcao is getattr(qb, novo)


def test_estados_fock_antigo():
    with pytest.deprecated_call(match="qbasic.fock"):
        funcao = qb.estados.Fock
    assert funcao is qb.fock
    with pytest.raises(AttributeError):
        qb.estados.nao_existe  # noqa: B018


@pytest.mark.parametrize("modulo", MODULOS_ANTIGOS)
def test_modulos_antigos_importam_com_aviso(modulo):
    sys.modules.pop(f"qbasic.{modulo}", None)
    with pytest.deprecated_call(match="obsoleto"):
        submodulo = importlib.import_module(f"qbasic.{modulo}")
    for nome in MODULOS_ANTIGOS[modulo]:
        assert hasattr(submodulo, nome), f"qbasic.{modulo}.{nome}"


@pytest.mark.parametrize("modulo", MODULOS_ANTIGOS)
def test_modulos_antigos_como_atributo_do_pacote(modulo):
    sys.modules.pop(f"qbasic.{modulo}", None)
    vars(qb).pop(modulo, None)
    with pytest.deprecated_call():
        assert getattr(qb, modulo).__name__ == f"qbasic.{modulo}"


def test_metodos_antigos():
    H = qb.ObjQuantico([[2, 1], [1, 2]])
    with pytest.deprecated_call(match="traco"):
        assert H.traço() == pytest.approx(4)
    with pytest.deprecated_call(match="autovalores"):
        np.testing.assert_allclose(H.Autovalores(), [1, 3])
    with pytest.deprecated_call(match="autovetores"):
        assert H.Autovetores().shape == (2, 2)
    with pytest.deprecated_call(match="autoestados"):
        valores, _ = H.AutoValor_Vetor()
        np.testing.assert_allclose(valores, [1, 3])
    with pytest.deprecated_call(match="expm"):
        np.testing.assert_allclose(densa(H.expM()), densa(H.expm()))


def test_objquantico_esparso():
    with pytest.deprecated_call(match="formato"):
        classe = qb.ObjQuantico_esparso
    A = classe(np.eye(2), r"\mathbb{1}")
    assert isinstance(A, qb.ObjQuantico)
    assert A.formato == "esparso"
    assert A.latex_representation == r"\mathbb{1}"
    assert isinstance(qb.identidade(2, sparsa=True), classe)
    assert not isinstance(qb.identidade(2), classe)


def test_matrizdensidade_com_a_assinatura_antiga():
    with pytest.deprecated_call(match="matriz_densidade"):
        matrizdensidade = qb.matrizdensidade
    puro = matrizdensidade(estados=qb.ket("0"))
    misto = matrizdensidade([0.5, 0.5], [qb.ket("0"), qb.ket("1")], puro=False, sparsa=True)
    np.testing.assert_allclose(densa(puro), [[1, 0], [0, 0]])
    assert misto.formato == "esparso"
    np.testing.assert_allclose(densa(misto), np.eye(2) / 2)


class TestEdoAntigo:
    """``qb.edo.solve`` devolve o objeto do ``solve_ivp``, como antes."""

    @pytest.fixture
    def edo(self):
        with pytest.deprecated_call():
            return qb.edo

    def test_solve(self, edo):
        tempos = np.linspace(0, 2, 21)
        resultado = edo.solve(qb.pauliX(), tempos, qb.ket("0"))
        assert resultado.success
        np.testing.assert_allclose(resultado.t, tempos)
        np.testing.assert_allclose(np.abs(resultado.y[0]) ** 2, np.cos(tempos) ** 2, atol=1e-7)

    def test_t_span_como_array(self, edo):
        # Bug B13: "t_span == None" quebrava com arrays NumPy.
        resultado = edo.solve(qb.pauliX(), [0, 0.5, 1], qb.ket("0"), t_span=np.array([0.0, 1.0]))
        assert resultado.success

    def test_tolerancias_padrao_conservam_a_norma(self, edo):
        # Bug B14: com rtol=1e-3 a norma variava ~1e-4 em t = 10.
        resultado = edo.solve(qb.pauliX(), np.linspace(0, 10, 51), qb.ket("0"))
        np.testing.assert_allclose(np.linalg.norm(resultado.y, axis=0), 1.0, atol=1e-7)

    def test_nao_densifica_hamiltoniano_esparso(self, edo, monkeypatch):
        # Bug B15.
        monkeypatch.setattr(qb.ObjQuantico, "full", _proibir_full_de_operador_esparso)
        resultado = edo.solve(qb.pauliX(sparsa=True), [0, 1], qb.ket("0"))
        assert resultado.success

    def test_edo_nao_e_objeto_quantico(self, edo):
        # Bug B16: edo herdava de ObjQuantico sem motivo.
        assert not issubclass(edo, qb.ObjQuantico)


_full_original = qb.ObjQuantico.full


def _proibir_full_de_operador_esparso(self):
    if self.formato == "esparso" and self.shape[1] > 1:
        raise AssertionError("operador esparso convertido para denso")
    return _full_original(self)


def test_valor_esperado_antigo_devolve_listas_de_float():
    estados = np.array([[1, 0], [0, 1]], dtype=complex)
    with pytest.deprecated_call(match="valores_esperados"):
        Valor_esperado = qb.Valor_esperado
    valores = Valor_esperado(estados, [qb.pauliZ(), qb.pauliX()])
    assert valores == [[1.0, -1.0], [0.0, 0.0]]
    assert all(isinstance(v, float) for v in valores[0])


def test_codigo_dos_tutoriais_continua_rodando():
    """Trecho do antigo Testes/teste_jaymescuming.py, usado nos notebooks."""
    codigo = textwrap.dedent(
        """
        import numpy as np
        import qbasic as qb
        from qbasic.funçoes import edo, Valor_esperado
        from qbasic.operador import destruiçao, Identidade
        from qbasic.class_tijolo import ObjQuantico

        g = 0.05 * 2 * np.pi
        psi0 = qb.estados.bases(2, 0) @ qb.estados.bases(2, 0)
        a = qb.operador.destruiçao(2) @ qb.operador.Identidade(2)
        sm = qb.operador.Identidade(2) @ (qb.operador.destruiçao(2).dag())
        H = 2 * np.pi * (a.dag() * a + sm.dag() * sm) + g * (a * sm.dag() + a.dag() * sm)
        tempo = np.linspace(0, 10, 100)
        resultado = qb.funçoes.edo.solve(H, tempo, psi0)
        valores = qb.funçoes.Valor_esperado(resultado.y, [a.dag() * a, sm.dag() * sm])
        assert isinstance(H, ObjQuantico)
        """
    )
    for modulo in ("funçoes", "operador", "class_tijolo"):
        sys.modules.pop(f"qbasic.{modulo}", None)
        vars(qb).pop(modulo, None)
    espaco = {}
    with pytest.deprecated_call():
        exec(codigo, espaco)
    tempos = espaco["tempo"]
    n_fotons, populacao = espaco["valores"]
    # Oscilação de Rabi no vácuo: a excitação vai e volta entre átomo e cavidade.
    g = espaco["g"]
    np.testing.assert_allclose(n_fotons, np.sin(g * tempos) ** 2, atol=1e-6)
    np.testing.assert_allclose(populacao, np.cos(g * tempos) ** 2, atol=1e-6)
