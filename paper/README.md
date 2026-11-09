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
