"""Testes da dinâmica (equação de Schrödinger) e dos valores esperados."""

import numpy as np
import pytest
from scipy.linalg import expm

import qbasic as qb
from auxiliares import densa

METODOS = ["expm", "RK45", "DOP853"]


def rabi(omega=np.pi, tempos=None, sparsa=False, **opcoes):
    """Qubit sob H = (omega/2) X, partindo de |0>; observável Z."""
    tempos = np.linspace(0, 4, 81) if tempos is None else tempos
    H = (omega / 2) * qb.pauliX(sparsa=sparsa)
    return tempos, qb.resolver_schrodinger(H, qb.ket("0"), tempos, [qb.pauliZ()], **opcoes)


class TestRabi:
    @pytest.mark.parametrize("metodo", METODOS)
    def test_oscilacao_de_rabi(self, sparsa, metodo):
        # <Z>(t) = cos(omega t)
        omega = np.pi
        tempos, resultado = rabi(omega, sparsa=sparsa, metodo=metodo)
        np.testing.assert_allclose(
            resultado.valores_esperados[0], np.cos(omega * tempos), atol=1e-7
        )

    @pytest.mark.parametrize("metodo", METODOS)
    def test_conservacao_da_norma_com_opcoes_padrao(self, metodo):
        # Bug B14: com as tolerâncias padrão antigas a norma chegava a variar 1e-4.
        tempos = np.linspace(0, 10, 51)
        resultado = qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), tempos, metodo=metodo)
        np.testing.assert_allclose(np.linalg.norm(resultado.vetores, axis=0), 1.0, atol=1e-7)

    @pytest.mark.parametrize("metodo", METODOS)
    def test_tempos_nao_uniformes(self, metodo):
        tempos = np.array([0.0, 0.1, 0.15, 0.7, 2.0, 3.3])
        _, resultado = rabi(tempos=tempos, metodo=metodo)
        np.testing.assert_allclose(
            resultado.valores_esperados[0], np.cos(np.pi * tempos), atol=1e-7
        )

    def test_tempo_inicial_diferente_de_zero(self):
        tempos = np.linspace(2.0, 3.0, 11)
        _, resultado = rabi(tempos=tempos)
        # Em t = tempos[0] o estado é o inicial: <Z> = 1, e depois cos(omega (t - t0)).
        np.testing.assert_allclose(
            resultado.valores_esperados[0], np.cos(np.pi * (tempos - 2.0)), atol=1e-10
        )

    def test_um_unico_instante(self):
        for metodo in METODOS:
            _, resultado = rabi(tempos=[0.5], metodo=metodo)
            np.testing.assert_allclose(resultado.vetores, [[1], [0]])


class TestResultado:
    def test_atributos(self):
        tempos, resultado = rabi()
        assert resultado.vetores.shape == (2, len(tempos))
        np.testing.assert_allclose(resultado.tempos, tempos)
        assert resultado.metodo == "expm"
        assert resultado.dims == [[2], [1]]
        # Apelidos com os nomes do solve_ivp, usados nos tutoriais.
        assert resultado.t is resultado.tempos
        assert resultado.y is resultado.vetores
        assert "expm" in repr(resultado)

    def test_estados_como_objetos(self):
        _, resultado = rabi(tempos=[0, 0.5, 1.0])
        estados = resultado.estados
        assert len(estados) == 3
        assert all(e.tipo == "ket" for e in estados)
        np.testing.assert_allclose(densa(estados[0]), [[1], [0]])
        # Em t = 1, U = exp(-i (pi/2) X) = -i X, logo |psi> = -i|1>.
        np.testing.assert_allclose(densa(estados[2]), [[0], [-1j]], atol=1e-10)

    def test_sem_observaveis(self):
        resultado = qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), [0, 1])
        assert resultado.valores_esperados == []

    def test_um_observavel_sem_lista(self):
        resultado = qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), [0, 1], qb.pauliZ())
        assert len(resultado.valores_esperados) == 1


class TestValidacao:
    @pytest.mark.parametrize(
        ("H", "psi0", "tempos", "erro", "mensagem"),
        [
            (np.eye(2), "ket0", [0, 1], TypeError, "ObjQuantico"),
            ("ret", "ket0", [0, 1], ValueError, "quadrado"),
            ("X", "bra0", [0, 1], ValueError, "ket"),
            ("X", "ket3", [0, 1], ValueError, "incompatíveis"),
            ("X", "ket0", [1, 0], ValueError, "crescente"),
            ("X", "ket0", [], ValueError, "pelo menos um"),
        ],
    )
    def test_entradas_invalidas(self, H, psi0, tempos, erro, mensagem):
        objetos = {
            "X": qb.pauliX(),
            "ret": qb.ObjQuantico(np.ones((2, 3))),
            "ket0": qb.ket("0"),
            "bra0": qb.bra("0"),
            "ket3": qb.bases(3, 0),
        }
        H = objetos.get(H, H) if isinstance(H, str) else H
        with pytest.raises(erro, match=mensagem):
            qb.resolver_schrodinger(H, objetos[psi0], tempos)

    def test_falha_do_integrador_gera_erro(self, monkeypatch):
        class Falha:
            success = False
            message = "passo pequeno demais"

        monkeypatch.setattr(qb.dinamica, "solve_ivp", lambda *args, **kwargs: Falha())
        with pytest.raises(RuntimeError, match="RK45 falhou: passo pequeno demais"):
            qb.resolver_schrodinger(qb.pauliX(), qb.ket("0"), [0, 1], metodo="RK45")


class TestEsparsoNaoDensifica:
    def test_hamiltoniano_esparso_nao_e_convertido(self, monkeypatch):
        # Bug B15: o solver antigo chamava H.full() e perdia a vantagem do formato esparso.
        original = qb.ObjQuantico.full

        def full_vigiado(self):
            if self.formato == "esparso" and self.shape[1] > 1:
                raise AssertionError("o Hamiltoniano esparso foi convertido para denso")
            return original(self)

        monkeypatch.setattr(qb.ObjQuantico, "full", full_vigiado)
        H = qb.destruicao(30, sparsa=True) + qb.criacao(30, sparsa=True)
        for metodo in METODOS:
            resultado = qb.resolver_schrodinger(
                H, qb.fock(30, 0), [0, 0.5, 1.0], [qb.destruicao(30, sparsa=True)], metodo=metodo
            )
            assert resultado.vetores.shape == (30, 3)

    def test_denso_e_esparso_dao_o_mesmo_resultado(self):
        tempos = np.linspace(0, 2, 21)
        for metodo in METODOS:
            denso = qb.resolver_schrodinger(qb.operador_x(6), qb.fock(6, 1), tempos, metodo=metodo)
            esparso = qb.resolver_schrodinger(
                qb.operador_x(6, sparsa=True), qb.fock(6, 1, sparsa=True), tempos, metodo=metodo
            )
            np.testing.assert_allclose(esparso.vetores, denso.vetores, atol=1e-8)


class TestJaynesCummings:
    """Átomo de dois níveis (|1> excitado) acoplado a uma cavidade com N níveis."""

    N = 4
    omega = 2 * np.pi
    g = 0.1 * 2 * np.pi

    def operadores(self, dessintonia=0.0, sparsa=False):
        a = qb.destruicao(self.N, sparsa=sparsa) @ qb.identidade(2, sparsa=sparsa)
        sm = qb.identidade(self.N, sparsa=sparsa) @ qb.destruicao(2, sparsa=sparsa)  # sigma-
        H = (
            self.omega * a.dag() * a
            + (self.omega + dessintonia) * sm.dag() * sm
            + self.g * (a.dag() * sm + a * sm.dag())
        )
        return a, sm, H

    @pytest.mark.parametrize("metodo", METODOS)
    def test_oscilacao_de_rabi_no_vacuo(self, sparsa, metodo):
        # Em ressonância, partindo de |0 fótons, excitado>:
        # P_excitado = cos^2(g t) e <n> = sen^2(g t).
        a, sm, H = self.operadores(sparsa=sparsa)
        tempos = np.linspace(0, 10, 101)
        psi0 = qb.fock(self.N, 0) @ qb.ket("1")
        resultado = qb.resolver_schrodinger(
            H, psi0, tempos, [a.dag() * a, sm.dag() * sm], metodo=metodo
        )
        n_fotons, p_excitado = resultado.valores_esperados
        np.testing.assert_allclose(p_excitado, np.cos(self.g * tempos) ** 2, atol=1e-6)
        np.testing.assert_allclose(n_fotons, np.sin(self.g * tempos) ** 2, atol=1e-6)

    def test_numero_de_excitacoes_conservado(self):
        a, sm, H = self.operadores(dessintonia=0.3)
        psi0 = qb.fock(self.N, 1) @ qb.ket("1")  # 2 excitações
        resultado = qb.resolver_schrodinger(
            H, psi0, np.linspace(0, 10, 51), [a.dag() * a + sm.dag() * sm]
        )
        np.testing.assert_allclose(resultado.valores_esperados[0], 2.0, atol=1e-8)

    @pytest.mark.parametrize("metodo", METODOS)
    def test_igual_a_exponencial_do_hamiltoniano(self, metodo):
        # |psi(t)> = exp(-i H t) |psi(0)>
        _, _, H = self.operadores(dessintonia=0.5)
        tempos = np.linspace(0, 3, 16)
        psi0 = (qb.fock(self.N, 0) @ qb.ket("1") + qb.fock(self.N, 2) @ qb.ket("0")) / np.sqrt(2)
        resultado = qb.resolver_schrodinger(H, psi0, tempos, metodo=metodo)
        Hm, v0 = densa(H), densa(psi0).ravel()
        for k, t in enumerate(tempos):
            np.testing.assert_allclose(resultado.vetores[:, k], expm(-1j * Hm * t) @ v0, atol=1e-7)


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
    def test_com_arrays(self, estado, observavel, esperado):
        valor = qb.valor_esperado(np.asarray(estado, dtype=complex), np.asarray(observavel))
        assert isinstance(valor, float)
        assert valor == pytest.approx(esperado)

    def test_com_objetos(self, sparsa):
        mais = (qb.ket("0", sparsa=sparsa) + qb.ket("1", sparsa=sparsa)) / np.sqrt(2)
        assert qb.valor_esperado(mais, qb.pauliX(sparsa=sparsa)) == pytest.approx(1.0)
        assert qb.valor_esperado(mais.dag(), qb.pauliZ()) == pytest.approx(0.0, abs=1e-12)

    def test_com_matriz_densidade(self, sparsa):
        rho = qb.matriz_densidade([qb.ket("0"), qb.ket("1")], [0.75, 0.25], sparsa=sparsa)
        assert qb.valor_esperado(rho, qb.pauliZ(sparsa=sparsa)) == pytest.approx(0.5)

    def test_observavel_nao_hermitiano_da_complexo(self):
        estado = qb.coerente(30, 0.5 + 0.5j)
        valor = qb.valor_esperado(estado, qb.destruicao(30))
        assert isinstance(valor, complex)
        assert valor == pytest.approx(0.5 + 0.5j, abs=1e-10)

    def test_varios_estados_de_uma_vez(self):
        estados = np.array([[1, 0, 1 / np.sqrt(2)], [0, 1, 1 / np.sqrt(2)]], dtype=complex)
        z, x = qb.valores_esperados(estados, [qb.pauliZ(), qb.pauliX()])
        np.testing.assert_allclose(z, [1, -1, 0], atol=1e-12)
        np.testing.assert_allclose(x, [0, 0, 1], atol=1e-12)
        lista = [qb.ket("0"), qb.ket("1")]
        np.testing.assert_allclose(qb.valor_esperado(lista, qb.pauliZ()), [1, -1])

    def test_aceita_resultado(self):
        _, resultado = rabi()
        np.testing.assert_allclose(
            qb.valor_esperado(resultado, qb.pauliZ()), resultado.valores_esperados[0]
        )

    def test_dimensoes_incompativeis(self):
        with pytest.raises(ValueError, match="incompatíveis"):
            qb.valor_esperado(qb.bases(3, 0), qb.pauliZ())
        with pytest.raises(ValueError, match="vetor"):
            qb.valor_esperado(np.zeros((2, 2, 2)), qb.pauliZ())
