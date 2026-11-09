#!/usr/bin/env python3
"""Gera o livro em LaTeX (e, opcionalmente, o PDF) a partir dos tutoriais em notebooks.

A ordem e os títulos dos capítulos vêm de ``tutoriais/indice.yml``. Cada notebook vira
um capítulo: o Markdown é convertido pelo pandoc, os códigos ganham destaque de sintaxe,
as saídas de texto e as matrizes em LaTeX são preservadas, e os gráficos são salvos em
``figuras/``.

Uso (a partir da raiz do repositório)::

    pip install -e ".[livro]"                          # pandoc embutido (pypandoc_binary)
    python scripts/gerar_tutorial_latex.py             # gera tutorial_latex/build/tutorial.tex
    python scripts/gerar_tutorial_latex.py --pdf       # também compila o PDF

O PDF precisa de uma distribuição LaTeX com XeLaTeX e latexmk (por exemplo, TeX Live) e das
fontes DejaVu.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
INDICE_PADRAO = RAIZ / "tutoriais" / "indice.yml"
MODELO = RAIZ / "tutorial_latex" / "modelo"
SAIDA_PADRAO = RAIZ / "tutorial_latex" / "build"
LOGO = RAIZ / "docs" / "source" / "_static" / "logo_qbasic.png"
MAX_LINHAS_SAIDA = 25

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_EQUACAO = re.compile(r"\\begin\{(equation\*?)\}(.*?)\\end\{\1\}", re.S)
_MATEMATICA_EM_LINHA = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)")
_TITULO = re.compile(r"^(#{1,5})(\s)", re.M)
# Saídas de texto que só "poluem" o livro (representações de objetos do matplotlib etc.).
_RUIDO = re.compile(
    r"^\s*(\[?<[\w.]+(?: [\w.]+)*(?: at 0x[0-9a-f]+)?>\]?|<Figure size .*>|Text\(.*\)"
    r"|\[<matplotlib\..*>(?:, <matplotlib\..*>)*\])\s*$",
    re.S,
)


# ---------------------------------------------------------------------------
# Ferramentas externas
# ---------------------------------------------------------------------------
def caminho_pandoc() -> str:
    """Pandoc do pypandoc_binary ou, na falta dele, o instalado no sistema."""
    try:
        import pypandoc

        return pypandoc.get_pandoc_path()
    except (ImportError, OSError):
        pandoc = shutil.which("pandoc")
        if pandoc:
            return pandoc
    raise SystemExit("pandoc não encontrado: instale com  pip install -e '.[livro]'")


def carregar_indice(caminho: Path) -> dict:
    import yaml

    return yaml.safe_load(caminho.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Conversão das células
# ---------------------------------------------------------------------------
def texto_da_celula(valor) -> str:
    return "".join(valor) if isinstance(valor, list) else str(valor)


def cerca(conteudo: str, minimo: int = 3) -> str:
    """Sequência de crases maior que qualquer uma presente no conteúdo."""
    maior = max((len(m) for m in re.findall(r"`+", conteudo)), default=0)
    return "`" * max(minimo, maior + 1)


def bloco_latex(latex: str) -> str:
    marca = cerca(latex)
    return f"{marca}{{=latex}}\n{latex}\n{marca}\n"


def preparar_markdown(fonte: str) -> str:
    """Ajusta o Markdown do Jupyter (MathJax) para o pandoc.

    - ``\\begin{equation}...\\end{equation}`` vira ``$$...$$``;
    - ``$ x $`` (com espaços, aceito pelo MathJax) vira ``$x$``;
    - os títulos descem um nível (``##`` vira ``###``), porque no livro ``#`` é a parte e
      ``##`` é o capítulo.
    """
    fonte = fonte.replace("\r\n", "\n")
    fonte = _EQUACAO.sub(lambda m: f"\n$$\n{m.group(2).strip()}\n$$\n", fonte)
    fonte = _MATEMATICA_EM_LINHA.sub(lambda m: f"${m.group(1).strip()}$", fonte)
    return _TITULO.sub(lambda m: "#" + m.group(1) + m.group(2), fonte)


def bloco_codigo(fonte: str) -> str:
    marca = cerca(fonte)
    return f"{marca}python\n{fonte.rstrip()}\n{marca}\n"


def bloco_saida(texto: str, erro: bool = False, max_linhas: int = MAX_LINHAS_SAIDA) -> str:
    texto = _ANSI.sub("", texto).rstrip()
    linhas = texto.split("\n")
    if len(linhas) > max_linhas:
        omitidas = len(linhas) - max_linhas
        linhas = [*linhas[:max_linhas], f"... ({omitidas} linhas omitidas)"]
    ambiente = "saidaerro" if erro else "saida"
    return bloco_latex(f"\\begin{{{ambiente}}}\n" + "\n".join(linhas) + f"\n\\end{{{ambiente}}}")


def corrigir_arrays(latex: str) -> str:
    """Ajusta ``\\begin{array}{cc}`` ao número real de colunas.

    O MathJax aceita arrays com mais colunas do que as declaradas (o QuTiP gera assim);
    o LaTeX não.
    """

    def ajustar(m: re.Match) -> str:
        linhas = re.split(r"\\\\", m.group(2))
        colunas = max(linha.count("&") + 1 for linha in linhas)
        especificacao = m.group(1) if len(m.group(1)) >= colunas else "c" * colunas
        return f"\\begin{{array}}{{{especificacao}}}{m.group(2)}\\end{{array}}"

    return re.sub(r"\\begin\{array\}\{([^}]*)\}(.*?)\\end\{array\}", ajustar, latex, flags=re.S)


def bloco_matematica(latex: str) -> str:
    conteudo = latex.strip().strip("$").strip()
    conteudo = re.sub(r"^\\displaystyle\s*", "", conteudo)
    conteudo = _EQUACAO.sub(lambda m: m.group(2), conteudo)
    conteudo = corrigir_arrays(conteudo)
    return bloco_latex(
        "\\begin{center}\n\\begin{adjustbox}{max width=\\linewidth}\n"
        f"$\\displaystyle {conteudo}$\n\\end{{adjustbox}}\n\\end{{center}}"
    )


class Figuras:
    """Salva as imagens das saídas em ``figuras/`` com nomes sequenciais."""

    def __init__(self, pasta: Path, prefixo: str) -> None:
        self.pasta = pasta
        self.prefixo = prefixo
        self.contador = 0

    def salvar(self, png_base64: str) -> str:
        self.contador += 1
        nome = f"{self.prefixo}_{self.contador:02d}.png"
        (self.pasta / nome).write_bytes(base64.b64decode(png_base64))
        return bloco_latex(
            "\\begin{center}\n"
            f"\\includegraphics[width=0.8\\linewidth,height=0.42\\textheight,keepaspectratio]"
            f"{{figuras/{nome}}}\n\\end{{center}}"
        )


def converter_saidas(celula: dict, figuras: Figuras) -> list[str]:
    partes = []
    proposital = "raises-exception" in celula.get("metadata", {}).get("tags", [])
    for saida in celula.get("outputs", []):
        tipo = saida.get("output_type")
        if tipo == "stream":
            if saida.get("name") != "stderr":
                partes.append(bloco_saida(texto_da_celula(saida.get("text", ""))))
        elif tipo in ("execute_result", "display_data"):
            dados = saida.get("data", {})
            if "image/png" in dados:
                partes.append(figuras.salvar(texto_da_celula(dados["image/png"])))
            elif "text/latex" in dados:
                partes.append(bloco_matematica(texto_da_celula(dados["text/latex"])))
            elif "text/plain" in dados:
                texto = texto_da_celula(dados["text/plain"])
                if not _RUIDO.match(texto):
                    partes.append(bloco_saida(texto))
        elif tipo == "error":
            aviso = " (erro proposital: veja o texto)" if proposital else ""
            texto = f"{saida.get('ename', 'Erro')}: {saida.get('evalue', '')}{aviso}"
            partes.append(bloco_saida(texto, erro=True))
    return partes


def converter_notebook(caminho: Path, titulo: str, figuras: Figuras) -> str:
    """Markdown (para o pandoc) de um capítulo."""
    notebook = json.loads(caminho.read_text(encoding="utf-8"))
    identificador = re.sub(r"[^a-z0-9]+", "-", caminho.stem.lower()).strip("-")
    partes = [f"## {titulo} {{#cap-{caminho.parent.name}-{identificador}}}\n"]
    celulas = notebook["cells"]
    # A primeira célula é o título do notebook, substituído pelo título do índice.
    if celulas and celulas[0]["cell_type"] == "markdown":
        primeira = texto_da_celula(celulas[0]["source"]).strip()
        if primeira.startswith("# ") and "\n" not in primeira:
            celulas = celulas[1:]
    for celula in celulas:
        fonte = texto_da_celula(celula.get("source", ""))
        if celula["cell_type"] == "markdown":
            if fonte.strip():
                partes.append(preparar_markdown(fonte) + "\n")
        elif celula["cell_type"] == "code":
            if fonte.strip():
                partes.append(bloco_codigo(fonte))
            partes.extend(converter_saidas(celula, figuras))
    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Livro
# ---------------------------------------------------------------------------
def montar_markdown(indice: dict, pasta_tutoriais: Path, pasta_figuras: Path) -> str:
    prefacio = (MODELO / "prefacio.md").read_text(encoding="utf-8")
    partes = [f"## Prefácio {{.unnumbered}}\n\n{prefacio}\n"]
    for parte in indice["partes"]:
        partes.append(f"# {parte['titulo']}\n")
        for capitulo in parte["capitulos"]:
            caminho = pasta_tutoriais / parte["pasta"] / capitulo["arquivo"]
            prefixo = f"{parte['pasta']}_{Path(capitulo['arquivo']).stem}"
            partes.append(
                converter_notebook(caminho, capitulo["titulo"], Figuras(pasta_figuras, prefixo))
            )
    return "\n".join(partes)


def versao_qbasic() -> str:
    try:
        import qbasic

        return qbasic.__version__
    except ImportError:
        texto = (RAIZ / "src" / "qbasic" / "_version.py").read_text(encoding="utf-8")
        return re.search(r'__version__ = "([^"]+)"', texto).group(1)


def gerar(
    indice: Path = INDICE_PADRAO, saida: Path = SAIDA_PADRAO, data: str | None = None
) -> Path:
    """Gera ``tutorial.tex`` (e o Markdown intermediário) em ``saida``. Devolve o .tex."""
    saida = Path(saida)
    if saida.exists():
        shutil.rmtree(saida)
    (saida / "figuras").mkdir(parents=True)
    shutil.copy2(LOGO, saida / LOGO.name)

    data = data or datetime.date.today().strftime("%d/%m/%Y")
    capa = (MODELO / "capa.tex").read_text(encoding="utf-8")
    capa = capa.replace("@VERSAO@", versao_qbasic()).replace("@DATA@", data)
    (saida / "capa.tex").write_text(capa, encoding="utf-8")

    markdown = montar_markdown(carregar_indice(indice), Path(indice).parent, saida / "figuras")
    (saida / "tutorial.md").write_text(markdown, encoding="utf-8")

    tex = saida / "tutorial.tex"
    subprocess.run(
        [
            caminho_pandoc(),
            str(saida / "tutorial.md"),
            "--from=markdown-raw_tex+autolink_bare_uris",
            "--to=latex",
            "--standalone",
            "--top-level-division=part",
            f"--metadata-file={MODELO / 'metadados.yml'}",
            f"--include-in-header={MODELO / 'preambulo.tex'}",
            f"--include-before-body={saida / 'capa.tex'}",
            f"--resource-path={saida}",
            f"--output={tex}",
        ],
        check=True,
    )
    return tex


def compilar_pdf(tex: Path) -> Path:
    """Compila com XeLaTeX (via latexmk, se existir)."""
    if shutil.which("latexmk"):
        comando = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", tex.name]
        execucoes = [comando]
    elif shutil.which("xelatex"):
        execucoes = [["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex.name]] * 2
    else:
        raise SystemExit("XeLaTeX não encontrado: instale uma distribuição LaTeX (ex.: TeX Live)")
    for comando in execucoes:
        resultado = subprocess.run(comando, cwd=tex.parent, capture_output=True, text=True)
        if resultado.returncode != 0:
            log = tex.with_suffix(".log")
            trecho = log.read_text(errors="replace")[-3000:] if log.exists() else resultado.stdout
            raise SystemExit(f"falha ao compilar o PDF. Final do log:\n{trecho}")
    return tex.with_suffix(".pdf")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Gera o livro em LaTeX a partir dos tutoriais.")
    parser.add_argument("--indice", type=Path, default=INDICE_PADRAO, help="arquivo indice.yml")
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="pasta de saída")
    parser.add_argument("--pdf", action="store_true", help="também compila o PDF (XeLaTeX)")
    args = parser.parse_args(argv)

    tex = gerar(args.indice, args.saida)
    print(f"LaTeX gerado: {tex}")
    if args.pdf:
        print(f"PDF gerado:   {compilar_pdf(tex)}")


if __name__ == "__main__":
    sys.exit(main())
