"""Representação de objetos quânticos em texto e em LaTeX."""

from __future__ import annotations

import numpy as np

__all__ = ["formatar_numero", "latex_matriz"]

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
