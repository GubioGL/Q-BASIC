"""Garantia de compatibilidade da API pública.

Estes nomes são usados nos tutoriais, nos exemplos e por quem já instalou o
Q-BASIC. Se algum for renomeado (Fase 5 do plano), o nome antigo deve continuar
funcionando como apelido.
"""

import importlib
import importlib.metadata

import pytest

import qbasic as qb

NOMES_PUBLICOS = [
    "ObjQuantico",
    "ObjQuantico_esparso",
    "bases",
    "ket",
    "bra",
    "Fock",
    "coerente",
    "Identidade",
    "destruiçao",
    "criaçao",
    "operador_x",
    "operador_p",
    "pauliX",
    "pauliY",
    "pauliZ",
    "matrizdensidade",
    "edo",
    "valor_esperado",
    "Valor_esperado",
]

SUBMODULOS = {
    "class_tijolo": ["ObjQuantico", "ObjQuantico_esparso"],
    "estados": ["bases", "ket", "bra", "Fock", "coerente"],
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


@pytest.mark.parametrize("nome", NOMES_PUBLICOS)
def test_nome_disponivel_no_pacote(nome):
    assert hasattr(qb, nome)
    assert nome in qb.__all__


def test_all_contem_apenas_nomes_existentes():
    for nome in qb.__all__:
        assert hasattr(qb, nome), nome


@pytest.mark.parametrize("modulo", SUBMODULOS)
def test_submodulos(modulo):
    submodulo = importlib.import_module(f"qbasic.{modulo}")
    for nome in SUBMODULOS[modulo]:
        assert hasattr(submodulo, nome), f"qbasic.{modulo}.{nome}"


def test_submodulos_acessiveis_como_atributo():
    # Forma usada nos exemplos: qb.estados.bases, qb.operador.destruiçao, ...
    assert qb.estados.bases is qb.bases
    assert qb.operador.destruiçao is qb.destruiçao
    assert qb.funçoes.edo is qb.edo


def test_versao_do_pacote():
    assert qb.__version__ == importlib.metadata.version("Q-BASIC")
    partes = qb.__version__.split(".")
    assert len(partes) >= 3
    assert all(p.isdigit() for p in partes[:3])
