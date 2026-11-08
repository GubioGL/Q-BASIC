"""
Benchmarks do núcleo do Q-BASIC.

Usa apenas a API comum às versões 0.0.x e 0.1.x (nomes antigos como ``destruiçao`` e
``edo.solve``), para que a mesma medição rode nas duas versões e possa ser comparada
por ``comparar_versoes.py``. Na versão nova, mede também o solver novo.

Uso::

    python benchmarks/bench_nucleo.py            # imprime uma tabela
    python benchmarks/bench_nucleo.py --json     # imprime JSON (usado pelo comparador)
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import platform
import timeit
import warnings

import numpy as np
import scipy

warnings.simplefilter("ignore")  # na versão 0.1 os nomes antigos geram DeprecationWarning

import qbasic as qb  # noqa: E402
from qbasic import estados, funçoes, operador  # noqa: E402

CASOS: dict[str, tuple[str, object]] = {}


def caso(nome: str, descricao: str):
    """Registra uma função que prepara o caso e devolve o que deve ser cronometrado."""

    def registrar(preparar):
        CASOS[nome] = (descricao, preparar)
        return preparar

    return registrar


def jaynes_cummings(N: int, sparsa: bool):
    a = operador.destruiçao(N, sparsa=sparsa) @ operador.Identidade(2, sparsa=sparsa)
    sm = operador.Identidade(N, sparsa=sparsa) @ operador.destruiçao(2, sparsa=sparsa)
    H = a.dag() * a + sm.dag() * sm + 0.1 * (a.dag() * sm + a * sm.dag())
    return a, sm, H


@caso("valor_esperado", "Valor esperado de a†a em 2000 instantes (N = 200)")
def _valor_esperado():
    rng = np.random.default_rng(0)
    vetores = rng.normal(size=(200, 2000)) + 1j * rng.normal(size=(200, 2000))
    a = operador.destruiçao(200)
    numero = a.dag() * a
    return lambda: funçoes.Valor_esperado(vetores, [numero])


@caso("potencia", "Potência x**64 de um operador denso 200×200")
def _potencia():
    x = operador.operador_x(200)
    return lambda: x**64


@caso("hamiltoniano_esparso", "Montar o Hamiltoniano de Jaynes-Cummings esparso (N = 2000)")
def _hamiltoniano_esparso():
    return lambda: jaynes_cummings(2000, sparsa=True)


def estado_inicial_coerente():
    """Cavidade num estado coerente (alpha = 8, 64 fótons em média) e átomo excitado."""
    cavidade = estados.coerente(200, 8.0, metodo="analitico", sparsa=True)
    return cavidade @ estados.bases(2, 1, sparsa=True)


@caso("solver_esparso", "edo.solve, Jaynes-Cummings esparso (dimensão 400, α = 8, rtol=1e-8)")
def _solver_esparso():
    _, _, H = jaynes_cummings(200, sparsa=True)
    psi0 = estado_inicial_coerente()
    tempos = np.linspace(0, 10, 100)
    return lambda: funçoes.edo.solve(H, tempos, psi0, rtol=1e-8, atol=1e-10)


@caso("coerente_analitico", "Estado coerente pelo método analítico (N = 150)")
def _coerente():
    return lambda: estados.coerente(150, 3.0, metodo="analitico")


@caso("repr", "repr() de um operador 40×40 (exibição)")
def _repr():
    a = operador.destruiçao(40)
    return lambda: repr(a)


if hasattr(qb, "resolver_schrodinger"):

    @caso("resolver_expm", "resolver_schrodinger (expm, exato), mesmo sistema de solver_esparso")
    def _resolver_expm():
        a, _, H = jaynes_cummings(200, sparsa=True)
        tempos = np.linspace(0, 10, 100)
        psi0 = estado_inicial_coerente()
        return lambda: qb.resolver_schrodinger(H, psi0, tempos, [a.dag() * a])


def medir(funcao, repeticoes: int = 3) -> float:
    """Menor tempo (s) entre algumas repetições, com a saída padrão silenciada."""
    with contextlib.redirect_stdout(io.StringIO()):
        funcao()  # aquecimento
        return min(timeit.repeat(funcao, repeat=repeticoes, number=1))


def executar() -> dict:
    resultados = {}
    for nome, (descricao, preparar) in CASOS.items():
        with contextlib.redirect_stdout(io.StringIO()):
            funcao = preparar()
        resultados[nome] = {"descricao": descricao, "segundos": medir(funcao)}
    return {
        "qbasic": getattr(qb, "__version__", "?"),
        "arquivo": qb.__file__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "plataforma": platform.platform(),
        "casos": resultados,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--json", action="store_true", help="imprime o resultado em JSON")
    args = parser.parse_args()
    dados = executar()
    if args.json:
        print(json.dumps(dados))
        return
    print(f"Q-BASIC {dados['qbasic']} | Python {dados['python']} | NumPy {dados['numpy']}")
    for nome, caso_ in dados["casos"].items():
        print(f"{nome:22s} {1e3 * caso_['segundos']:10.2f} ms   {caso_['descricao']}")


if __name__ == "__main__":
    main()
