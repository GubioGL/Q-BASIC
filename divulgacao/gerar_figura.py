from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch

NAVY, NAVY2 = "#0b0a2a", "#1b1464"
BLUE, AMARELO, VERDE, ROXO = "#1a00a8", "#FFD400", "#18b84a", "#7b2ff7"
BRANCO = "#ffffff"

fig = plt.figure(figsize=(12, 12), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1200)
ax.set_ylim(1200, 0)
ax.axis("off")
fig.patch.set_facecolor(NAVY)

# fundo: faixas sutis em verde e amarelo (como no logo), bem suaves
ax.add_patch(Circle((340, 600), 520, color=NAVY2, alpha=0.55, lw=0))
ax.add_patch(Circle((340, 600), 430, color="#241a7a", alpha=0.35, lw=0))

# título
ax.text(60, 95, "Q-BASIC", color=AMARELO, fontsize=60, fontweight="bold", va="center")
ax.text(
    60,
    165,
    "Aprenda física quântica construindo um simulador",
    color=BRANCO,
    fontsize=21,
    va="center",
)

# esfera de Bloch: o símbolo da biblioteca
cx, cy, R = 340, 600, 215
for k, a in [(1.42, 0.05), (1.28, 0.08), (1.16, 0.12)]:  # brilho
    ax.add_patch(Circle((cx, cy), R * k, color="#6a5cff", alpha=a, lw=0))
ax.add_patch(Circle((cx, cy), R, color=BLUE, lw=0))
ax.add_patch(Circle((cx, cy), R, fill=False, ec=BRANCO, lw=2.5))
ax.add_patch(
    Ellipse(
        (cx, cy), 2 * R, 2 * R * 0.32, fill=False, ec=BRANCO, lw=1.6, ls=(0, (5, 4)), alpha=0.85
    )
)
# eixos
for x2, y2 in [(cx, cy - R - 20), (cx + R + 20, cy), (cx - 150, cy + 150)]:
    ax.add_patch(
        FancyArrowPatch(
            (cx, cy), (x2, y2), arrowstyle="-|>", mutation_scale=16, color=BRANCO, lw=1.4
        )
    )
ax.text(cx + 16, cy - R - 26, "z", color=BRANCO, fontsize=15, style="italic")
ax.text(cx + R + 30, cy + 6, "y", color=BRANCO, fontsize=15, style="italic")
ax.text(cx - 175, cy + 170, "x", color=BRANCO, fontsize=15, style="italic")
# polos |0> e |1>
ax.add_patch(Circle((cx, cy - R), 13, color=BRANCO, zorder=5))
ax.add_patch(Circle((cx, cy + R), 13, color=BRANCO, zorder=5))
ax.text(cx - 18, cy - R - 26, "|0⟩", color=BRANCO, fontsize=18, ha="right", va="center")
ax.text(cx, cy + R + 42, "|1⟩", color=BRANCO, fontsize=18, ha="center", va="center")
# vetor |ψ⟩
tip = (cx + 0.52 * R, cy - 0.66 * R)
ax.add_patch(
    FancyArrowPatch(
        (cx, cy), tip, arrowstyle="-|>", mutation_scale=22, color=AMARELO, lw=4, zorder=6
    )
)
ax.add_patch(Circle(tip, 9, color=AMARELO, zorder=7))
ax.text(tip[0] + 16, tip[1] - 18, "|ψ⟩", color=AMARELO, fontsize=24, fontweight="bold", zorder=8)
ax.plot([tip[0], tip[0]], [tip[1], cy], ls=":", color=BRANCO, lw=1.3, alpha=0.8)
ax.plot([cx, tip[0]], [cy, cy], ls=":", color=BRANCO, lw=1.3, alpha=0.8)
ax.text(cx + 10, cy - 52, "θ", color=BRANCO, fontsize=18, style="italic")
ax.text(cx + 55, cy + 40, "φ", color=BRANCO, fontsize=18, style="italic")
ax.text(
    cx,
    cy + R + 105,
    "símbolo do Q-BASIC",
    color=AMARELO,
    fontsize=15,
    ha="center",
    va="center",
    fontweight="bold",
)

# ciclo de aprendizado (direita)
passos = [
    ("1 · AULA", "um conceito de física:\nestado, operador, evolução", AMARELO),
    ("2 · CÓDIGO", "a biblioteca cresce\njunto com a aula", VERDE),
    ("3 · TESTE", "o resultado é conferido\ncontra a solução analítica", ROXO),
    ("4 · LIVRO", "125 páginas geradas\nautomaticamente a cada versão", AMARELO),
]
x0, w, h = 660, 480, 150
ys = [270, 455, 640, 825]
for (titulo, texto, cor), y in zip(passos, ys, strict=True):
    ax.add_patch(
        FancyBboxPatch(
            (x0, y), w, h, boxstyle="round,pad=0,rounding_size=22", fc="#15124a", ec=cor, lw=3
        )
    )
    ax.add_patch(
        FancyBboxPatch((x0, y), 14, h, boxstyle="round,pad=0,rounding_size=7", fc=cor, ec="none")
    )
    ax.text(x0 + 40, y + 42, titulo, color=cor, fontsize=21, fontweight="bold", va="center")
    ax.text(x0 + 40, y + 98, texto, color=BRANCO, fontsize=15, va="center", linespacing=1.35)
for y in ys[:-1]:
    ax.add_patch(
        FancyArrowPatch(
            (x0 + w / 2, y + h + 4),
            (x0 + w / 2, y + h + 58 - 4),
            arrowstyle="-|>",
            mutation_scale=22,
            color=AMARELO,
            lw=2.5,
        )
    )
ax.text(
    x0 + w / 2,
    225,
    "o ciclo de aprender construindo",
    color=BRANCO,
    fontsize=16,
    ha="center",
    va="center",
    style="italic",
)

# rodapé
ax.add_patch(
    FancyBboxPatch((0, 1040), 1200, 160, boxstyle="square,pad=0", fc=VERDE, ec="none", alpha=0.95)
)
ax.add_patch(FancyBboxPatch((0, 1040), 1200, 16, boxstyle="square,pad=0", fc=AMARELO, ec="none"))
ax.text(
    600,
    1100,
    "Física  ·  Computação quântica  ·  Engenharia de software",
    color=NAVY,
    fontsize=24,
    fontweight="bold",
    ha="center",
    va="center",
)
ax.text(
    600,
    1155,
    "Quantum Brazilian Algorithms, SImulations, and Computational tools  ·  em desenvolvimento",
    color=NAVY,
    fontsize=15,
    ha="center",
    va="center",
)

out = str(Path(__file__).resolve().parent / "figura_linkedin.png")
fig.savefig(out, dpi=100, facecolor=NAVY)
print("ok", out)
