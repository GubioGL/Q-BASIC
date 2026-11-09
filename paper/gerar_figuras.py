"""Gera as figuras e os valores numéricos usados no artigo (reprodutível).

Uso, a partir da raiz do repositório (precisa de ``pip install -e ".[plot]"``)::

    python paper/gerar_figuras.py

Saídas em ``paper/figuras/``:

- ``fig_dinamica.pdf``      — oscilação de Rabi e colapso/renascimento (Jaynes-Cummings);
- ``fig_wigner.pdf``        — decoerência de um gato de Schrödinger (Lindblad + Wigner);
- ``fig_precisao.pdf``      — erro dos métodos de evolução em relação à solução exata;
- ``fig_desempenho.pdf``    — ganho de desempenho (lido de ``benchmarks/resultados.json``);
- ``tabela_desempenho.tex`` — tabela com os tempos medidos;
- ``valores.tex``           — números citados no texto (erros e tempos dos métodos).

E ``paper/joss/figura_qbasic.png``, a figura da versão para o JOSS.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import qbasic as qb  # noqa: E402

PASTA = Path(__file__).resolve().parent
FIGURAS = PASTA / "figuras"
RAIZ = PASTA.parent
ROXO = "#5e17eb"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def numero_br(valor: float, casas: int = 2) -> str:
    """Formata ``1.5e-13`` como ``1{,}5\\times10^{-13}`` (LaTeX, vírgula decimal)."""
    if valor == 0:
        return "0"
    expoente = int(np.floor(np.log10(abs(valor))))
    if -2 <= expoente <= 3:
        return f"{valor:.{casas}f}".replace(".", "{,}")
    mantissa = valor / 10**expoente
    return f"{mantissa:.1f}".replace(".", "{,}") + rf"\times10^{{{expoente}}}"


# ---------------------------------------------------------------------------
# Sistemas usados nas figuras
# ---------------------------------------------------------------------------
def jaynes_cummings(N: int, g: float = 1.0, omega: float = 0.0):
    a = qb.tensor(qb.destruicao(N, sparsa=True), qb.identidade(2, sparsa=True))
    sm = qb.tensor(qb.identidade(N, sparsa=True), qb.destruicao(2, sparsa=True))
    H = omega * (a.dag() * a + sm.dag() * sm) + g * (a.dag() * sm + a * sm.dag())
    return a, sm, H


def figura_dinamica() -> None:
    fig, (eixo_a, eixo_b) = plt.subplots(1, 2, figsize=(7.0, 2.6), width_ratios=[1, 1.6])

    # (a) Rabi: H = (Omega/2) sigma_x, <sigma_z>(t) = cos(Omega t)
    tempos = np.linspace(0, 4 * np.pi, 400)
    pontos = np.linspace(0, 4 * np.pi, 25)
    res = qb.resolver_schrodinger(0.5 * qb.pauliX(), qb.ket("0"), pontos, [qb.pauliZ()])
    eixo_a.plot(tempos, np.cos(tempos), color="0.6", label="analítico")
    eixo_a.plot(pontos, res.valores_esperados[0], "o", color=ROXO, ms=3.5, label="Q-BASIC")
    eixo_a.set_xlabel(r"$\Omega t$")
    eixo_a.set_ylabel(r"$\langle\sigma_z\rangle$")
    eixo_a.set_title("(a) Oscilação de Rabi", loc="left", fontsize=9)
    eixo_a.set_ylim(-1.15, 1.7)
    eixo_a.set_yticks([-1, -0.5, 0, 0.5, 1])
    eixo_a.legend(loc="upper center", ncol=2, frameon=False)

    # (b) Jaynes-Cummings com campo coerente: colapso e renascimento
    N, alpha = 40, np.sqrt(10)
    _, sm, H = jaynes_cummings(N)
    psi0 = qb.tensor(qb.coerente(N, alpha), qb.ket("1"))
    tempos = np.linspace(0, 50, 1500)
    res = qb.resolver_schrodinger(H, psi0, tempos, [sm.dag() * sm])
    eixo_b.plot(tempos, res.valores_esperados[0], color=ROXO, lw=0.8)
    eixo_b.axvline(2 * np.pi * alpha, color="0.4", ls="--", lw=0.8)
    eixo_b.text(2 * np.pi * alpha + 0.8, 0.93, r"$t_r = 2\pi|\alpha|/g$", fontsize=8, color="0.3")
    eixo_b.set_xlabel(r"$g t$")
    eixo_b.set_ylabel(r"$P_e(t)$")
    eixo_b.set_ylim(0, 1.02)
    eixo_b.set_title(r"(b) Colapso e renascimento, $|\alpha|^2 = 10$", loc="left", fontsize=9)

    fig.tight_layout()
    fig.savefig(FIGURAS / "fig_dinamica.pdf")
    plt.close(fig)


def figura_wigner(destino_png: Path | None = None) -> None:
    N, alpha = 30, 2.0
    a = qb.destruicao(N)
    gato = (qb.coerente(N, alpha) + qb.coerente(N, -alpha)).normalizar()
    instantes = [0.0, 0.1, 0.4]
    res = qb.resolver_lindblad(0 * qb.numero(N), gato, instantes, [a])  # kappa = 1
    x = np.linspace(-4.5, 4.5, 241)

    funcoes = [qb.wigner(rho, x, x) for rho in res.estados]
    limite = max(np.abs(W).max() for W in funcoes)
    niveis = np.linspace(-limite, limite, 61)  # mesma escala de cores nos três painéis

    fig, eixos = plt.subplots(1, 3, figsize=(7.0, 2.45), sharey=True)
    for eixo, t, rho, W in zip(eixos, instantes, res.estados, funcoes, strict=True):
        mapa = eixo.contourf(x, x, W, niveis, cmap="RdBu_r")
        mapa.set_rasterized(True)  # mapa de cores como imagem: PDF leve
        eixo.set_aspect("equal")
        eixo.set_xlabel("$x$")
        eixo.set_title(
            rf"$\kappa t = {t:.1f}$, pureza ${qb.pureza(rho):.2f}$".replace(".", "{,}"), fontsize=9
        )
    eixos[0].set_ylabel("$p$")
    fig.colorbar(mapa, ax=eixos, shrink=0.85, label="$W(x,p)$")
    fig.savefig(FIGURAS / "fig_wigner.pdf", dpi=300)
    if destino_png is not None:
        fig.savefig(destino_png, dpi=200)
    plt.close(fig)


def figura_precisao() -> dict[str, str]:
    """Erro de cada método em relação à diagonalização exata (Jaynes-Cummings)."""
    N, alpha = 40, np.sqrt(10)
    _, _, H = jaynes_cummings(N, omega=1.0)
    psi0 = qb.tensor(qb.coerente(N, alpha), qb.ket("1"))
    tempos = np.linspace(0, 50, 500)
    autovalores, autovetores = np.linalg.eigh(H.full())
    v0 = psi0.full().ravel()
    exato = autovetores @ (
        np.exp(-1j * np.outer(autovalores, tempos)) * (autovetores.conj().T @ v0)[:, None]
    )

    valores = {}
    fig, eixo = plt.subplots(figsize=(4.2, 2.6))
    for metodo, cor in [("expm", ROXO), ("DOP853", "C1"), ("RK45", "C2")]:
        inicio = time.perf_counter()
        res = qb.resolver_schrodinger(H, psi0, tempos, metodo=metodo)
        duracao = time.perf_counter() - inicio
        erro = np.linalg.norm(res.vetores - exato, axis=0)
        eixo.semilogy(tempos[1:], np.maximum(erro[1:], 1e-17), color=cor, lw=1, label=metodo)
        chave = {"expm": "Expm", "DOP853": "DOP", "RK45": "RK"}[metodo]  # nomes de macros LaTeX
        valores[f"Erro{chave}"] = numero_br(float(erro.max()))
        valores[f"Tempo{chave}"] = numero_br(duracao * 1e3, 0)
    eixo.set_xlabel("$t$")
    eixo.set_ylabel(r"$\| \psi(t) - \psi_{\mathrm{exato}}(t) \|$")
    eixo.legend(frameon=False, ncol=3, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURAS / "fig_precisao.pdf")
    plt.close(fig)
    return valores


def figura_e_tabela_desempenho() -> dict[str, str]:
    dados = json.loads((RAIZ / "benchmarks" / "resultados.json").read_text(encoding="utf-8"))
    ambiente = dados["depois"]
    antes, depois = dados["antes"]["casos"], dados["depois"]["casos"]
    rotulos = {
        "valor_esperado": "Valor esperado\n(2000 instantes)",
        "potencia": "Potência $x^{64}$\n(denso 200×200)",
        "hamiltoniano_esparso": "Montar $H$ esparso\n($N = 2000$)",
        "solver_esparso": "Solver, $H$ esparso\n(dimensão 400)",
        "coerente_analitico": "Estado coerente\n(analítico)",
        "repr": "repr()\n(40×40)",
    }
    casos = [c for c in rotulos if c in antes and c in depois]
    ganhos = [antes[c]["segundos"] / depois[c]["segundos"] for c in casos]

    fig, eixo = plt.subplots(figsize=(4.4, 2.8))
    eixo.barh([rotulos[c] for c in casos][::-1], ganhos[::-1], color=ROXO)
    eixo.set_xscale("log")
    eixo.axvline(1, color="0.4", lw=0.8)
    for y, ganho in enumerate(ganhos[::-1]):
        eixo.text(ganho * 1.1, y, f"{ganho:.1f}×".replace(".", ","), va="center", fontsize=8)
    eixo.set_xlabel("ganho de velocidade (versão anterior / 0.1.0)")
    eixo.tick_params(axis="y", labelsize=7.5)
    fig.tight_layout()
    fig.savefig(FIGURAS / "fig_desempenho.pdf")
    plt.close(fig)

    def ms(segundos: float) -> str:
        return f"{segundos * 1e3:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    linhas = []
    for c in casos:
        nome = rotulos[c].replace("\n", " ")
        ganho = f"{antes[c]['segundos'] / depois[c]['segundos']:.1f}".replace(".", ",")
        linhas.append(
            f"{nome} & {ms(antes[c]['segundos'])} & {ms(depois[c]['segundos'])} & {ganho}\\\\"
        )
    if "resolver_expm" in depois:
        t = depois["resolver_expm"]["segundos"]
        ganho = f"{antes['solver_esparso']['segundos'] / t:.0f}"
        linhas.append(
            r"\texttt{resolver\_schrodinger} (exato), mesmo sistema & --- & "
            f"{ms(t)} & {ganho}$^*$\\\\"
        )
    tabela = "\n".join(
        [
            r"\begin{tabular}{lrrr}",
            r"\toprule",
            r"Operação & Antes (ms) & Depois (ms) & Ganho \\",
            r"\midrule",
            *linhas,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    (FIGURAS / "tabela_desempenho.tex").write_text(tabela + "\n", encoding="utf-8")

    def razao(caso_antes: str, caso_depois: str) -> str:
        return f"{antes[caso_antes]['segundos'] / depois[caso_depois]['segundos']:.0f}"

    return {
        "AmbientePython": ambiente["python"],
        "AmbienteNumpy": ambiente["numpy"],
        "AmbienteScipy": ambiente["scipy"],
        "GanhoSolver": razao("solver_esparso", "solver_esparso"),
        "GanhoResolver": razao("solver_esparso", "resolver_expm"),
        "GanhoValorEsperado": razao("valor_esperado", "valor_esperado"),
        "TempoSolverAntes": numero_br(antes["solver_esparso"]["segundos"], 1),
    }


def main() -> None:
    FIGURAS.mkdir(exist_ok=True)
    figura_dinamica()
    figura_wigner(destino_png=PASTA / "joss" / "figura_qbasic.png")
    valores = {**figura_precisao(), **figura_e_tabela_desempenho()}
    linhas = ["% Gerado por paper/gerar_figuras.py — não edite à mão."]
    linhas += [f"\\newcommand{{\\{nome}}}{{{valor}}}" for nome, valor in sorted(valores.items())]
    (FIGURAS / "valores.tex").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("Figuras e valores gerados em", FIGURAS)
    for nome, valor in sorted(valores.items()):
        print(f"  {nome} = {valor}")


if __name__ == "__main__":
    main()
