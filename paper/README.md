# paper — artigo sobre a biblioteca Q-BASIC

O projeto tem dois produtos:

- o **livro** (`tutoriais/` → `tutorial_latex/`), um curso que ensina a construir um
  simulador quântico do zero;
- a **biblioteca** (`src/qbasic/`), o produto final dessas aulas.

Esta pasta guarda o **artigo sobre a biblioteca**, em inglês, para o
[*Journal of Open Source Software*](https://joss.theoj.org/) (JOSS).

| Arquivo | Conteúdo |
|---|---|
| [`JOSS.md`](JOSS.md) | **Leia primeiro:** o que o JOSS exige, o que já temos, o que falta e como justificar o artigo. |
| [`joss/paper.md`](joss/paper.md) | Rascunho do artigo (Markdown no formato do JOSS). Os pontos marcados `TODO` precisam ser preenchidos antes da submissão. |
| [`joss/paper.bib`](joss/paper.bib) | Referências (BibTeX). |
| [`joss/figura_qbasic.png`](joss/figura_qbasic.png) | Figura do artigo, gerada pela própria biblioteca. |
| [`gerar_figuras.py`](gerar_figuras.py) | Script que refaz a figura. |
| [`overleaf/`](overleaf/) | Artigo em LaTeX para o Overleaf: `paper.tex`, `paper.bib`, figura e `q-basic-overleaf.zip`. |
| [`gerar_overleaf.py`](gerar_overleaf.py) | Script que gera a pasta `overleaf/` a partir do `paper.md`. |

Autor: Gubio Gomes de Lima.

## Figura reprodutível

```bash
pip install -e ".[plot]"
python paper/gerar_figuras.py   # grava paper/joss/figura_qbasic.png
```

Os números de desempenho citados no artigo vêm de `benchmarks/` (`make bench`).

## Compilar o PDF

- **GitHub Actions:** o workflow **Artigo** refaz a figura e gera o PDF com a ferramenta
  oficial do JOSS (`openjournals-draft-action`) a cada mudança em `paper/`. O PDF fica
  nos *Artifacts* da execução.
- **Localmente, com Docker:** `make artigo`. Ele roda a imagem `openjournals/inara`,
  a mesma usada pela revista, e grava `paper/joss/paper.pdf`.

## Overleaf

A pasta [`overleaf/`](overleaf/) tem o artigo em LaTeX, pronto para compilar no Overleaf:

1. Baixe [`overleaf/q-basic-overleaf.zip`](overleaf/q-basic-overleaf.zip).
2. No Overleaf, clique em **New Project → Upload Project** e envie o zip.
3. Compile com **pdfLaTeX** (padrão). As referências vêm do `paper.bib`.

A pasta é regenerada automaticamente a cada commit que muda `paper/joss/` (hook do
pre-commit, instalado por `make install-dev`). Para gerar na mão: `make overleaf`.
O CI confere se a pasta está atualizada e falha caso não esteja.
