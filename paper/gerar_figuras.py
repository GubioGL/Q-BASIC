"""Gera a figura do artigo do JOSS a partir da própria biblioteca (reprodutível).

Uso, a partir da raiz do repositório (precisa de ``pip install -e ".[plot]"``)::

    python paper/gerar_figuras.py

Saída: ``paper/joss/figura_qbasic.png`` — função de Wigner de um gato de Schrödinger
numa cavidade com perdas (equação de Lindblad), em três instantes. Os rótulos ficam em
inglês, como o artigo.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

import qbasic as qb  # noqa: E402

DESTINO = Path(__file__).resolve().parent / "joss" / "figura_qbasic.png"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.labelsize": 9,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
    }
)


def figura_wigner(destino: Path = DESTINO) -> list[float]:
    """Desenha a decoerência do gato e devolve a pureza em cada instante."""
    N, alpha = 30, 2.0
    a = qb.destruicao(N)
    gato = (qb.coerente(N, alpha) + qb.coerente(N, -alpha)).normalizar()
    instantes = [0.0, 0.1, 0.4]
    res = qb.resolver_lindblad(0 * qb.numero(N), gato, instantes, [a])  # kappa = 1
    x = np.linspace(-4.5, 4.5, 241)

    funcoes = [qb.wigner(rho, x, x) for rho in res.estados]
    purezas = [float(qb.pureza(rho)) for rho in res.estados]
    limite = max(np.abs(W).max() for W in funcoes)
    niveis = np.linspace(-limite, limite, 61)  # mesma escala de cores nos três painéis

    fig, eixos = plt.subplots(1, 3, figsize=(7.0, 2.45), sharey=True)
    for eixo, t, pureza, W in zip(eixos, instantes, purezas, funcoes, strict=True):
        mapa = eixo.contourf(x, x, W, niveis, cmap="RdBu_r")
        eixo.set_aspect("equal")
        eixo.set_xlabel("$x$")
        eixo.set_title(rf"$\kappa t = {t:.1f}$, purity ${pureza:.2f}$", fontsize=9)
    eixos[0].set_ylabel("$p$")
    fig.colorbar(mapa, ax=eixos, shrink=0.85, label="$W(x,p)$", ticks=MaxNLocator(5))
    fig.savefig(destino, dpi=200)
    plt.close(fig)
    return purezas


def main() -> None:
    purezas = figura_wigner()
    print("Figura gerada em", DESTINO)
    print("  purezas:", ", ".join(f"{p:.3f}" for p in purezas))


if __name__ == "__main__":
    main()
