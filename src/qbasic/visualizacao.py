"""Visualização: representação em LaTeX, função de Wigner e gráficos (esfera de Bloch,
distribuição de Fock, função de Wigner e valores esperados)."""

from __future__ import annotations

import numpy as np

__all__ = [
    "esfera_bloch",
    "formatar_numero",
    "latex_matriz",
    "plotar_fock",
    "plotar_valores_esperados",
    "plotar_wigner",
    "wigner",
]

# Tamanho máximo exibido por completo; acima disso a matriz é resumida com reticências.
MAX_EXIBIDO = 10
BORDA = 4


def formatar_numero(z: complex, digitos: int = 4) -> str:
    """Formata um número (real ou complexo) de forma curta para LaTeX.

    Exemplos: ``1``, ``0.7071``, ``-i``, ``0.5 + 0.5i``.
    """
    z = complex(z)
    tolerancia = 10.0 ** (-(digitos + 6))
    re = 0.0 if abs(z.real) < tolerancia else z.real
    im = 0.0 if abs(z.imag) < tolerancia else z.imag

    def curto(x: float) -> str:
        return f"{x:.{digitos}g}"

    def parte_imaginaria(x: float) -> str:
        if x == 1:
            return "i"
        if x == -1:
            return "-i"
        return f"{curto(x)}i"

    if im == 0:
        return curto(re) if re != 0 else "0"
    if re == 0:
        return parte_imaginaria(im)
    sinal = "-" if im < 0 else "+"
    return f"{curto(re)} {sinal} {parte_imaginaria(abs(im))}"


def _indices(n: int) -> list[int | None]:
    """Índices exibidos; ``None`` marca onde entram as reticências."""
    if n <= MAX_EXIBIDO:
        return list(range(n))
    return [*range(BORDA), None, *range(n - BORDA, n)]


def latex_matriz(matriz, digitos: int = 4) -> str:
    """Código LaTeX (``pmatrix``) de uma matriz densa ou esparsa.

    Matrizes com mais de ``MAX_EXIBIDO`` linhas ou colunas são resumidas: só as
    bordas aparecem, com ``\\cdots``, ``\\vdots`` e ``\\ddots`` no meio.
    """
    linhas_idx = _indices(matriz.shape[0])
    colunas_idx = _indices(matriz.shape[1])
    linhas_validas = [i for i in linhas_idx if i is not None]
    colunas_validas = [j for j in colunas_idx if j is not None]
    # Extrai só o bloco exibido (evita converter matrizes esparsas grandes para densas).
    bloco = matriz[np.ix_(linhas_validas, colunas_validas)]
    bloco = bloco.toarray() if hasattr(bloco, "toarray") else np.asarray(bloco)

    linhas_tex = []
    a = 0
    for i in linhas_idx:
        celulas = []
        b = 0
        for j in colunas_idx:
            if i is None and j is None:
                celulas.append(r"\ddots")
            elif i is None:
                celulas.append(r"\vdots")
            elif j is None:
                celulas.append(r"\cdots")
            else:
                celulas.append(formatar_numero(bloco[a, b], digitos))
            if j is not None:
                b += 1
        if i is not None:
            a += 1
        linhas_tex.append(" & ".join(celulas))
    return r"\begin{pmatrix} " + r" \\ ".join(linhas_tex) + r" \end{pmatrix}"


# ---------------------------------------------------------------------------
# Função de Wigner
# ---------------------------------------------------------------------------
def wigner(estado, x, p) -> np.ndarray:
    """Função de Wigner :math:`W(x, p)` de um modo bosônico (ket ou matriz densidade).

    Usa as quadraturas :math:`x = (a + a^\\dagger)/\\sqrt{2}` e
    :math:`p = -i(a - a^\\dagger)/\\sqrt{2}` (as de :func:`~qbasic.operador_x` e
    :func:`~qbasic.operador_p`), com normalização :math:`\\int W\\,dx\\,dp = 1`. O vácuo
    é :math:`W = e^{-x^2 - p^2}/\\pi`.

    O cálculo usa a expansão na base de Fock com polinômios de Laguerre, adequada para
    algumas dezenas de níveis.

    Parameters
    ----------
    estado : ObjQuantico
        Ket ou matriz densidade de um único modo (para sistemas compostos, use antes
        :func:`~qbasic.traco_parcial`).
    x, p : array_like
        Valores das quadraturas (1-D).

    Returns
    -------
    ndarray
        ``W[i, j] = W(x[j], p[i])``, forma ``(len(p), len(x))`` (pronta para ``contourf``).
    """
    from scipy.special import eval_genlaguerre, gammaln

    from .medidas import _como_densidade

    rho = _como_densidade(estado)
    if len(estado.dims[0] if estado.tipo != "bra" else estado.dims[1]) != 1:
        raise ValueError("a função de Wigner é definida para um único modo; use traco_parcial")
    X, P = np.meshgrid(np.asarray(x, dtype=float), np.asarray(p, dtype=float))
    alpha = (X + 1j * P) / np.sqrt(2)
    r2 = np.abs(alpha) ** 2
    gaussiana = np.exp(-2 * r2)
    W = np.zeros_like(r2)
    N = rho.shape[0]
    for m in range(N):
        for n in range(m + 1):
            if rho[m, n] == 0:
                continue
            # Elemento |m><n| (m >= n): (-1)^n sqrt(n!/m!) (2 alpha*)^(m-n) e^{-2|a|^2} L_n^(m-n)
            fator = (-1) ** n * np.exp(0.5 * (gammaln(n + 1) - gammaln(m + 1)))
            termo = fator * (2 * np.conj(alpha)) ** (m - n) * gaussiana
            termo = termo * eval_genlaguerre(n, m - n, 4 * r2)
            if m == n:
                W += np.real(rho[m, m]) * np.real(termo)
            else:
                W += 2 * np.real(rho[m, n] * termo)
    # (2/pi) na variável alpha; dividir por 2 converte para (x, p), pois d²alpha = dx dp / 2.
    return W / np.pi


# ---------------------------------------------------------------------------
# Gráficos (requerem matplotlib: pip install "Q-BASIC[plot]")
# ---------------------------------------------------------------------------
def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as erro:  # pragma: no cover - depende do ambiente
        raise ImportError(
            "os gráficos precisam do matplotlib: pip install 'Q-BASIC[plot]'"
        ) from erro
    return plt


def plotar_wigner(estado, x=None, p=None, ax=None, cmap: str = "RdBu_r", niveis: int = 100):
    """Desenha a função de Wigner (vermelho positivo, azul negativo).

    Parameters
    ----------
    estado : ObjQuantico
        Ket ou matriz densidade de um modo.
    x, p : array_like, optional
        Grade das quadraturas (padrão: ``linspace(-5, 5, 201)``).
    ax : matplotlib.axes.Axes, optional
        Eixos onde desenhar (padrão: uma figura nova).

    Returns
    -------
    matplotlib.axes.Axes
    """
    plt = _pyplot()
    x = np.linspace(-5, 5, 201) if x is None else np.asarray(x)
    p = np.linspace(-5, 5, 201) if p is None else np.asarray(p)
    W = wigner(estado, x, p)
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 4.2))
    limite = float(np.max(np.abs(W))) or 1.0
    mapa = ax.contourf(x, p, W, niveis, cmap=cmap, vmin=-limite, vmax=limite)
    ax.figure.colorbar(mapa, ax=ax, label="W(x, p)")
    ax.set_xlabel("x")
    ax.set_ylabel("p")
    ax.set_aspect("equal")
    return ax


def plotar_fock(estado, ax=None, cor: str = "C0"):
    """Gráfico de barras das probabilidades :math:`P(n)` na base de Fock (ou computacional)."""
    from .medidas import probabilidades

    plt = _pyplot()
    prob = probabilidades(estado)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(np.arange(prob.size), prob, color=cor)
    ax.set_xlabel("n")
    ax.set_ylabel("P(n)")
    return ax


def plotar_valores_esperados(resultado, rotulos=None, ax=None):
    """Valores esperados de um ``Resultado`` em função do tempo (um traço por observável)."""
    plt = _pyplot()
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 3.5))
    valores = resultado.valores_esperados
    if not valores:
        raise ValueError("o Resultado não tem valores esperados (passe observaveis ao resolver)")
    rotulos = rotulos or [f"observável {k}" for k in range(len(valores))]
    for serie, rotulo in zip(valores, rotulos, strict=True):
        ax.plot(resultado.tempos, np.real(serie), label=rotulo)
    ax.set_xlabel("tempo")
    ax.set_ylabel("valor esperado")
    ax.legend()
    return ax


def esfera_bloch(estados=None, ax=None, cor: str = "C3", trajetoria: bool = False):
    """Desenha a esfera de Bloch com os vetores de um ou mais estados de um qubit.

    Parameters
    ----------
    estados : ObjQuantico, lista ou ndarray, optional
        Um estado, uma lista de estados (kets ou matrizes densidade de um qubit) ou um
        array ``(k, 3)`` de vetores de Bloch já calculados.
    ax : Axes3D, optional
        Eixos 3D onde desenhar (padrão: uma figura nova).
    cor : str, optional
        Cor dos vetores.
    trajetoria : bool, optional
        Se ``True``, liga os pontos com uma linha (útil para a evolução no tempo) em vez
        de desenhar uma seta para cada estado.

    Returns
    -------
    mpl_toolkits.mplot3d.axes3d.Axes3D
    """
    from .medidas import vetor_bloch
    from .objeto import ObjQuantico

    plt = _pyplot()
    if ax is None:
        figura = plt.figure(figsize=(4.5, 4.5))
        ax = figura.add_subplot(projection="3d")

    u, v = np.mgrid[0 : 2 * np.pi : 40j, 0 : np.pi : 20j]
    ax.plot_wireframe(
        np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="gray", alpha=0.15
    )
    for eixo in np.eye(3):
        ax.plot(*np.vstack([-eixo, eixo]).T, color="gray", linewidth=0.8)
    for posicao, texto in [
        ((0, 0, 1.2), r"$|0\rangle$"),
        ((0, 0, -1.3), r"$|1\rangle$"),
        ((1.3, 0, 0), "x"),
        ((0, 1.3, 0), "y"),
    ]:
        ax.text(*posicao, texto, ha="center")

    if estados is not None:
        if isinstance(estados, ObjQuantico):
            estados = [estados]
        vetores = np.asarray(
            [vetor_bloch(e) if isinstance(e, ObjQuantico) else np.asarray(e) for e in estados],
            dtype=float,
        ).reshape(-1, 3)
        if trajetoria:
            ax.plot(*vetores.T, color=cor)
            ax.scatter(*vetores[-1], color=cor)
        else:
            for vx, vy, vz in vetores:
                ax.quiver(0, 0, 0, vx, vy, vz, color=cor, arrow_length_ratio=0.1)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    return ax
