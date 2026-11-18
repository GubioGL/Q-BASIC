"""Gera o artigo do JOSS em LaTeX para o Overleaf (``paper/overleaf/``).

Uso, a partir da raiz do repositório (precisa de ``pip install -e ".[livro]"`` ou do
``pandoc`` no PATH)::

    python paper/gerar_overleaf.py

Saídas, em ``paper/overleaf/``:

- ``paper.tex``          — artigo em LaTeX (classe ``article``, BibTeX com natbib);
- ``paper.bib``          — referências;
- ``figura_qbasic.png``  — figura usada no texto;
- ``q-basic-overleaf.zip`` — os três arquivos acima, prontos para *New Project → Upload*.

A saída é determinística (o zip usa uma data fixa), então o git só registra mudanças
reais no conteúdo. O hook de commit e o CI rodam este script para manter tudo em dia.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ORIGEM = PASTA / "joss"
DESTINO = PASTA / "overleaf"
ARQUIVOS = ["paper.bib", "figura_qbasic.png"]
ZIP = DESTINO / "q-basic-overleaf.zip"
# Data fixa dentro do zip (o mínimo aceito pelo formato): mesmo conteúdo, mesmo arquivo.
DATA_ZIP = (1980, 1, 1, 0, 0, 0)


def pandoc() -> str:
    """Usa o mesmo pandoc do livro (pypandoc_binary) ou o do PATH."""
    try:
        import pypandoc

        return pypandoc.get_pandoc_path()
    except ImportError:
        caminho = shutil.which("pandoc")
        if caminho is None:
            sys.exit("pandoc não encontrado: rode pip install -e '.[livro]'.")
        return caminho


def gerar_tex() -> None:
    subprocess.run(
        [
            pandoc(),
            "paper.md",
            "--from=markdown",
            "--to=latex",
            "--standalone",
            "--natbib",
            "--bibliography=paper.bib",
            "--output=" + str(DESTINO / "paper.tex"),
        ],
        cwd=ORIGEM,
        check=True,
    )


def gerar_zip() -> None:
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for nome in ["paper.tex", *ARQUIVOS]:
            info = zipfile.ZipInfo(nome, date_time=DATA_ZIP)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, (DESTINO / nome).read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--adicionar-ao-git",
        action="store_true",
        help="depois de gerar, adiciona paper/overleaf ao índice (usado pelo hook de commit)",
    )
    args = parser.parse_args()

    DESTINO.mkdir(exist_ok=True)
    gerar_tex()
    for nome in ARQUIVOS:
        shutil.copyfile(ORIGEM / nome, DESTINO / nome)
    gerar_zip()
    print("Artigo para o Overleaf gerado em", DESTINO)
    if args.adicionar_ao_git:
        subprocess.run(["git", "add", str(DESTINO)], cwd=PASTA.parent, check=True)


if __name__ == "__main__":
    main()
